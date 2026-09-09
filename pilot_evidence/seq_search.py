"""
SEQUENCE-MODEL EXPERIMENT — does LONG CONTEXT matter for single-channel fetal QRS detection?

Motivation from the full-text reading of the literature (all measured/reported values):
  Shokouhmand & Tavassolian 2023 (DPSS): swept analysis window 1-10 s, best F1 at 4 s.
  Chen 2025 (Attention R2W-Net) and Asadi 2025 (SCTD-Net): 1024 samples @250 Hz = 4.096 s.
  Xu 2026 (CNN-2xEEMD): effective receptive field ~2.8 s before global pooling.
  Alidash 2025: conv-stack receptive field only 48 ms; discrimination happens in the FC head.
  Behar 2014: grid-searched optimal band-pass 20-95 Hz at 250 Hz (NOT 1-45 Hz).

Our own window-based pilot used 300 ms and plateaued at macro F1 84%.  This script tests whether
sequence-to-sequence models over 4 s segments beat that, under the identical LORO protocol.

Task: input one 4 s segment of a single abdominal lead (residual + raw, 2 x 1000 @250 Hz),
output a per-sample fetal-R-peak heatmap; peak-pick; score at +/-50 ms.
"""
import os, sys, json, time, math, argparse, importlib.util
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from scipy import signal as sg

torch.manual_seed(0); np.random.seed(0)
torch.set_num_threads(max(1, (os.cpu_count() or 4) - 1))
ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pilot', os.path.join(ROOT, 'pilot.py'))
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
OUT = os.path.join(ROOT, 'results'); os.makedirs(OUT, exist_ok=True)
RECS, FS = P.RECS, 250
SEG = 1000            # 4 s
STRIDE_TR = 250       # 1 s hop for training segments
SIGMA = 3.0           # heatmap sigma in samples (12 ms)
LOGF = open(os.path.join(OUT, 'seq_search_log.txt'), 'a', encoding='utf-8')
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOGF.write(s + '\n'); LOGF.flush()

# ---------------------------------------------------------------- data
import mne, wfdb
def load_all(band=(15., 60.)):
    """returns per (rec,lead): residual, raw, fetal peak indices at 250 Hz"""
    D = {}
    for ri, rec in enumerate(RECS):
        raw = mne.io.read_raw_edf(os.path.join(P.RAW, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        fq = (wfdb.rdann(os.path.join(P.RAW, rec + '.edf'), 'qrs').sample / 4).round().astype(int)
        for lead in range(1, 5):
            x = sg.filtfilt(*sg.butter(4, [band[0] / 500, band[1] / 500], btype='band'), sig[lead])
            x = sg.filtfilt(*sg.iirnotch(50, 30, 1000), x)
            x = sg.resample_poly(x, 1, 4)
            mpk = P.detect_mqrs(x)
            r = P.robust_scale(P.template_subtract(x, mpk))
            D[(ri, lead)] = (r.astype(np.float32), P.robust_scale(x).astype(np.float32), fq)
    return D

def segments(D, recs, stride):
    X, Y = [], []
    for (ri, lead), (r, x, fq) in D.items():
        if ri not in recs: continue
        hm = np.zeros(len(r), np.float32)
        t = np.arange(len(r))
        for p in fq:
            lo, hi = max(0, p - 12), min(len(r), p + 13)
            hm[lo:hi] = np.maximum(hm[lo:hi], np.exp(-((t[lo:hi] - p) ** 2) / (2 * SIGMA ** 2)))
        for s in range(0, len(r) - SEG, stride):
            X.append(np.stack([r[s:s + SEG], x[s:s + SEG]])); Y.append(hm[s:s + SEG])
    return torch.from_numpy(np.stack(X)), torch.from_numpy(np.stack(Y))

# ---------------------------------------------------------------- models (seq2seq, output length = SEG)
def cbr(i, o, k, d=1):
    return nn.Sequential(nn.Conv1d(i, o, k, padding=(k // 2) * d, dilation=d, bias=False), nn.BatchNorm1d(o), nn.GELU())

class TCNSeq(nn.Module):
    """dilated residual TCN; RF = 2*(k-1)*sum(dilations)+1"""
    def __init__(s, cin=2, c=40, k=7, dils=(1, 2, 4, 8, 16, 32)):
        super().__init__(); s.stem = cbr(cin, c, k)
        s.blocks = nn.ModuleList([nn.ModuleDict({'a': cbr(c, c, k, d), 'b': nn.Sequential(
            nn.Conv1d(c, c, k, padding=(k // 2) * d, dilation=d, bias=False), nn.BatchNorm1d(c))}) for d in dils])
        s.act = nn.GELU(); s.out = nn.Conv1d(c, 1, 1)
        s.rf = 1 + 2 * (k - 1) * sum(dils) + (k - 1)
    def forward(s, x):
        h = s.stem(x)
        for m in s.blocks: h = s.act(m['b'](m['a'](h)) + h)
        return s.out(h).squeeze(1)

class UNetSeq(nn.Module):
    """1D U-Net, 4 down / 4 up, like SCTD-Net / R2W-Net but small"""
    def __init__(s, cin=2, c=16):
        super().__init__()
        ch = [c, c * 2, c * 4, c * 8]
        s.enc = nn.ModuleList([nn.Sequential(cbr(cin if i == 0 else ch[i - 1], ch[i], 7 if i == 0 else 5),
                                             cbr(ch[i], ch[i], 3)) for i in range(4)])
        s.bott = nn.Sequential(cbr(ch[3], ch[3] * 2, 3), cbr(ch[3] * 2, ch[3] * 2, 3))
        s.dec = nn.ModuleList([nn.Sequential(cbr(ch[3] * 2 + ch[3], ch[3], 3), cbr(ch[3], ch[3], 3)),
                               nn.Sequential(cbr(ch[3] + ch[2], ch[2], 3), cbr(ch[2], ch[2], 3)),
                               nn.Sequential(cbr(ch[2] + ch[1], ch[1], 3), cbr(ch[1], ch[1], 3)),
                               nn.Sequential(cbr(ch[1] + ch[0], ch[0], 3), cbr(ch[0], ch[0], 3))])
        s.pool = nn.MaxPool1d(2); s.out = nn.Conv1d(ch[0], 1, 1)
        s.rf = 'approx 1.5 s (4 poolings)'
    def forward(s, x):
        skips = []
        h = x
        for e in s.enc:
            h = e(h); skips.append(h); h = s.pool(h)
        h = s.bott(h)
        for d, sk in zip(s.dec, reversed(skips)):
            h = F.interpolate(h, size=sk.shape[-1], mode='linear', align_corners=False)
            h = d(torch.cat([h, sk], 1))
        return s.out(h).squeeze(1)

class CNNBiGRUSeq(nn.Module):
    """conv front end + BiGRU over the whole segment, like the DP-LSTM / BiLSTM family"""
    def __init__(s, cin=2, c=32, h=48):
        super().__init__()
        s.f = nn.Sequential(cbr(cin, c, 7), nn.MaxPool1d(2), cbr(c, c * 2, 5), nn.MaxPool1d(2))
        s.g = nn.GRU(c * 2, h, batch_first=True, bidirectional=True, num_layers=1)
        s.out = nn.Conv1d(h * 2, 1, 1); s.rf = 'full 4 s (recurrent)'
    def forward(s, x):
        h = s.f(x); o, _ = s.g(h.transpose(1, 2)); o = o.transpose(1, 2)
        return s.out(F.interpolate(o, size=x.shape[-1], mode='linear', align_corners=False)).squeeze(1)

class ShortCNNSeq(nn.Module):
    """CONTROL: receptive field deliberately limited to ~300 ms, matching our window pilot"""
    def __init__(s, cin=2, c=48, k=7):
        super().__init__()
        s.f = nn.Sequential(cbr(cin, c, k), cbr(c, c, k, 2), cbr(c, c, k, 4))
        s.out = nn.Conv1d(c, 1, 1); s.rf = 1 + 2 * (k - 1) * 0 + (k - 1) * (1 + 2 + 4)
    def forward(s, x): return s.out(s.f(x)).squeeze(1)

MODELS = {
    'short_cnn_rf300ms': lambda: ShortCNNSeq(),
    'tcn_rf1s':          lambda: TCNSeq(dils=(1, 2, 4, 8)),
    'tcn_rf2s':          lambda: TCNSeq(dils=(1, 2, 4, 8, 16)),
    'tcn_rf4s':          lambda: TCNSeq(dils=(1, 2, 4, 8, 16, 32)),
    'unet1d':            lambda: UNetSeq(),
    'cnn_bigru':         lambda: CNNBiGRUSeq(),
}

# ---------------------------------------------------------------- train / eval
def event_metrics(prob, fq, thr, tol_ms=50, refr_ms=250):
    pk, _ = sg.find_peaks(prob, height=thr, distance=int(refr_ms / 1000 * FS))
    tol = int(tol_ms / 1000 * FS)
    gm = np.zeros(len(fq), bool); tp = 0; errs = []
    for d in pk:
        dd = np.abs(fq - d); ok = np.where((dd <= tol) & (~gm))[0]
        if len(ok):
            j = ok[np.argmin(dd[ok])]; gm[j] = True; tp += 1; errs.append(dd[j] / FS * 1000)
    fp = len(pk) - tp; fn = len(fq) - int(gm.sum())
    se = tp / (tp + fn) * 100 if tp + fn else 0.; ppv = tp / (tp + fp) * 100 if tp + fp else 0.
    return dict(Se=se, PPV=ppv, F1=2 * se * ppv / (se + ppv) if se + ppv else 0., TP=tp, FP=fp, FN=fn,
                jitter=float(np.mean(errs)) if errs else float('nan'))

def infer_full(model, r, x, chunk=1000, ov=250):
    """slide the model over a whole record with overlap-average"""
    model.eval(); n = len(r); acc = np.zeros(n); cnt = np.zeros(n)
    with torch.no_grad():
        for s in range(0, max(n - chunk, 0) + 1, chunk - ov):
            seg = torch.from_numpy(np.stack([r[s:s + chunk], x[s:s + chunk]]))[None]
            if seg.shape[-1] < chunk: break
            p = torch.sigmoid(model(seg)).numpy()[0]
            acc[s:s + chunk] += p; cnt[s:s + chunk] += 1
    cnt[cnt == 0] = 1
    return acc / cnt

def evaluate(model, D, ri, thr_grid=np.arange(.05, .95, .05)):
    per = {t: [] for t in thr_grid}
    for lead in range(1, 5):
        r, x, fq = D[(ri, lead)]
        pr = infer_full(model, r, x)
        for t in thr_grid: per[t].append(event_metrics(pr, fq, t))
    bt = max(thr_grid, key=lambda t: np.mean([d['F1'] for d in per[t]]))
    return float(np.mean([d['F1'] for d in per[bt]])), float(bt), per[bt]

def train(model, X, Y, epochs=8, bs=32, lr=3e-3):
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, lr, epochs * math.ceil(len(X) / bs))
    pw = torch.tensor([float((Y < .1).sum() / max((Y > .5).sum(), 1))]).clamp(max=30.)
    for ep in range(epochs):
        model.train(); perm = torch.randperm(len(X))
        tot = 0.
        for i in range(0, len(X), bs):
            j = perm[i:i + bs]
            out = model(X[j])
            loss = F.binary_cross_entropy_with_logits(out, Y[j], pos_weight=pw)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sch.step(); tot += loss.item()
    return model

def nparams(m): return sum(p.numel() for p in m.parameters())

def main(epochs=8, band=(15., 60.)):
    t0 = time.time()
    log(f'\n=== SEQUENCE MODELS | 4 s segments @250 Hz | band {band[0]}-{band[1]} Hz | '
        f'train r01,r04,r07 | val r08 | epochs {epochs} ===')
    D = load_all(band); log(f'data loaded {time.time()-t0:.0f}s')
    Xtr, Ytr = segments(D, [0, 1, 2], STRIDE_TR)
    log(f'train segments {tuple(Xtr.shape)}  positive-sample rate {(Ytr>0.5).float().mean():.4f}')
    rows = []
    for name, build in MODELS.items():
        t1 = time.time(); torch.manual_seed(0)
        m = build()
        try:
            train(m, Xtr, Ytr, epochs)
            f1, thr, ms = evaluate(m, D, 3)
        except Exception as e:
            log(f'{name:20s} FAILED {type(e).__name__}: {e}'); continue
        rf = m.rf if isinstance(m.rf, str) else f'{m.rf} samples = {m.rf*4} ms'
        rows.append(dict(model=name, params=nparams(m), rf=str(rf), val_F1=round(f1, 2), thr=thr,
                         Se=round(float(np.mean([d['Se'] for d in ms])), 2),
                         PPV=round(float(np.mean([d['PPV'] for d in ms])), 2),
                         jitter=round(float(np.nanmean([d['jitter'] for d in ms])), 1),
                         sec=round(time.time() - t1, 1)))
        log(f'{name:20s} params {nparams(m):>7,} | RF {str(rf):24s} | val F1 {f1:6.2f} | '
            f'Se {rows[-1]["Se"]:5.1f} | PPV {rows[-1]["PPV"]:5.1f} | jitter {rows[-1]["jitter"]:4.1f} ms | {rows[-1]["sec"]:.0f}s')
    rows.sort(key=lambda r: -r['val_F1'])
    log('\n-- ranking --')
    for r in rows: log(f'  {r["val_F1"]:6.2f}  {r["model"]:20s} RF {r["rf"]}')
    json.dump(rows, open(os.path.join(OUT, 'seq_search.json'), 'w'), indent=1)
    return rows

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--epochs', type=int, default=8)
    ap.add_argument('--band', default='15,60')
    a = ap.parse_args()
    lo, hi = [float(v) for v in a.band.split(',')]
    main(a.epochs, (lo, hi))
