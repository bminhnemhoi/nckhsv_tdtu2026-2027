"""
ARCHITECTURE SEARCH for single-channel fetal QRS detection.

Protocol (no test leakage):
  DEV SPLIT   train = r01, r04, r07 (4 leads each)   validate = r08 (4 leads)
  r10 is held out completely and never touched during the search.
  15 architectures are compared on the dev split at event level (Se/PPV/F1, +/-50 ms,
  threshold swept on the validation record itself -> optimistic but IDENTICAL for every
  architecture, so the ranking is fair).
  The top-3 are then re-run under full 5-fold LORO with an inner validation record.

Everything trains on the same cached windows, same optimiser, same epochs, same batch size.
"""
import os, sys, json, time, math, argparse
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from scipy import signal as sg

torch.manual_seed(0); np.random.seed(0)
torch.set_num_threads(max(1, (os.cpu_count() or 4) - 1))
ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, 'cache_arch.npz')
OUT = os.path.join(ROOT, 'results'); os.makedirs(OUT, exist_ok=True)
RECS = ['r01', 'r04', 'r07', 'r08', 'r10']
FS, HOP = 250, 5          # 20 ms hop
W_LONG, W_SHORT = 125, 75
LOGF = open(os.path.join(OUT, 'arch_search_log.txt'), 'a', encoding='utf-8')
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOGF.write(s + '\n'); LOGF.flush()

# ---------------------------------------------------------------- data
D = np.load(CACHE, allow_pickle=True)
R, XR, Y, HM, PI = D['r'], D['x'], D['y'], D['hm'], D['pi']
CEN, REC, LEAD = D['c'], D['rec'], D['lead']
FQ = D['fq'].item()
log(f'cache: r{R.shape} pi{PI.shape} pos-rate {Y.mean():.4f}')

def crop(a, w):
    if w == a.shape[-1]: return a
    o = (a.shape[-1] - w) // 2
    return a[..., o:o + w]

def delay_matrix(r, nd=8, lag=2):
    """(B,L) -> (B,1,nd,L-(nd-1)*lag): stacked delayed copies, SCTD-Net style"""
    L = r.shape[-1]; n = L - (nd - 1) * lag
    return np.stack([r[:, i * lag:i * lag + n] for i in range(nd)], 1)[:, None]

# ---------------------------------------------------------------- models
class SE1d(nn.Module):
    def __init__(s, c, r=4):
        super().__init__(); s.f = nn.Sequential(nn.AdaptiveAvgPool1d(1), nn.Flatten(),
            nn.Linear(c, max(c // r, 4)), nn.ReLU(True), nn.Linear(max(c // r, 4), c), nn.Sigmoid())
    def forward(s, x): return x * s.f(x).unsqueeze(-1)

def blk(i, o, k, d=1, st=1):
    return nn.Sequential(nn.Conv1d(i, o, k, st, padding=(k // 2) * d, dilation=d, bias=False),
                         nn.BatchNorm1d(o), nn.GELU())

class CNN1D(nn.Module):
    def __init__(s, cin, chans, ks, dil=None, se=False, head=64):
        super().__init__()
        dil = dil or [1] * len(chans); L = []
        p = cin
        for c, k, d in zip(chans, ks, dil):
            L.append(blk(p, c, k, d)); L.append(nn.MaxPool1d(2)); p = c
            if se: L.append(SE1d(c))
        s.body = nn.Sequential(*L)
        s.head = nn.Sequential(nn.Linear(p * 2, head), nn.GELU(), nn.Dropout(.2), nn.Linear(head, 1))
    def forward(s, x, *a):
        h = s.body(x); h = torch.cat([h.mean(-1), h.amax(-1)], 1); return s.head(h)

class Res1D(nn.Module):
    def __init__(s, cin, chans=(32, 64, 96)):
        super().__init__(); s.stem = blk(cin, chans[0], 7); mods = []
        p = chans[0]
        for c in chans:
            mods.append(nn.ModuleDict({'a': blk(p, c, 3), 'b': nn.Sequential(nn.Conv1d(c, c, 3, padding=1, bias=False), nn.BatchNorm1d(c)),
                                       'sc': nn.Conv1d(p, c, 1, bias=False) if p != c else nn.Identity()})); p = c
        s.blocks = nn.ModuleList(mods); s.act = nn.GELU(); s.pool = nn.MaxPool1d(2)
        s.head = nn.Sequential(nn.Linear(p * 2, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x, *a):
        h = s.stem(x)
        for m in s.blocks:
            h = s.pool(s.act(m['b'](m['a'](h)) + m['sc'](h)))
        return s.head(torch.cat([h.mean(-1), h.amax(-1)], 1))

class TCN(nn.Module):
    def __init__(s, cin, c=48, dils=(1, 2, 4, 8)):
        super().__init__(); s.stem = blk(cin, c, 7); mods = []
        for d in dils:
            mods.append(nn.ModuleDict({'a': blk(c, c, 3, d), 'b': nn.Sequential(nn.Conv1d(c, c, 3, padding=d, dilation=d, bias=False), nn.BatchNorm1d(c))}))
        s.blocks = nn.ModuleList(mods); s.act = nn.GELU()
        s.head = nn.Sequential(nn.Linear(c * 2, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x, *a):
        h = s.stem(x)
        for m in s.blocks: h = s.act(m['b'](m['a'](h)) + h)
        return s.head(torch.cat([h.mean(-1), h.amax(-1)], 1))

class CNNGRU(nn.Module):
    def __init__(s, cin):
        super().__init__(); s.body = nn.Sequential(blk(cin, 32, 7), nn.MaxPool1d(2), blk(32, 48, 5), nn.MaxPool1d(2))
        s.gru = nn.GRU(48, 32, batch_first=True, bidirectional=True)
        s.head = nn.Sequential(nn.Linear(64, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x, *a):
        h = s.body(x).transpose(1, 2); o, _ = s.gru(h); return s.head(o.mean(1))

class TFM(nn.Module):
    def __init__(s, cin, d=64, nl=2):
        super().__init__(); s.stem = nn.Sequential(blk(cin, d, 7, st=1), nn.MaxPool1d(2))
        s.pos = nn.Parameter(torch.randn(1, 128, d) * .02)
        s.enc = nn.TransformerEncoder(nn.TransformerEncoderLayer(d, 4, 128, .1, batch_first=True, norm_first=True), nl)
        s.head = nn.Sequential(nn.Linear(d, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x, *a):
        h = s.stem(x).transpose(1, 2); h = h + s.pos[:, :h.shape[1]]; return s.head(s.enc(h).mean(1))

class UNet1D(nn.Module):
    def __init__(s, cin, c=24):
        super().__init__()
        s.e1 = blk(cin, c, 7); s.e2 = blk(c, c * 2, 5); s.e3 = blk(c * 2, c * 4, 3)
        s.p = nn.MaxPool1d(2)
        s.d2 = blk(c * 4 + c * 2, c * 2, 3); s.d1 = blk(c * 2 + c, c, 3)
        s.out = nn.Conv1d(c, 1, 1)
    def forward(s, x, *a):
        e1 = s.e1(x); e2 = s.e2(s.p(e1)); e3 = s.e3(s.p(e2))
        u2 = F.interpolate(e3, size=e2.shape[-1], mode='linear', align_corners=False)
        d2 = s.d2(torch.cat([u2, e2], 1))
        u1 = F.interpolate(d2, size=e1.shape[-1], mode='linear', align_corners=False)
        d1 = s.d1(torch.cat([u1, e1], 1))
        y = s.out(d1)                      # (B,1,L) per-sample logits
        return y[:, :, y.shape[-1] // 2]   # centre sample

class CNN2D(nn.Module):
    def __init__(s, cin, chans=(16, 32, 64)):
        super().__init__(); L = []; p = cin
        for c in chans:
            L += [nn.Conv2d(p, c, 3, padding=1, bias=False), nn.BatchNorm2d(c), nn.GELU(), nn.MaxPool2d(2)]; p = c
        s.body = nn.Sequential(*L); s.head = nn.Sequential(nn.Linear(p, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x, *a): return s.head(s.body(x).mean((-1, -2)))

class TwoStream(nn.Module):
    def __init__(s, cin1d, cin2d):
        super().__init__()
        s.a = CNN1D(cin1d, (32, 48, 64), (7, 5, 3)); s.a.head = nn.Identity()
        s.b = CNN2D(cin2d); s.b.head = nn.Identity()
        s.head = nn.Sequential(nn.Linear(64 * 2 + 64, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x1, x2): return s.head(torch.cat([s.a(x1), s.b(x2)], 1))

class MLP(nn.Module):
    def __init__(s, cin, L):
        super().__init__(); s.f = nn.Sequential(nn.Flatten(), nn.Linear(cin * L, 128), nn.GELU(),
                                                nn.Dropout(.2), nn.Linear(128, 64), nn.GELU(), nn.Linear(64, 1))
    def forward(s, x, *a): return s.f(x)

class Lin(nn.Module):
    def __init__(s, cin, L):
        super().__init__(); s.f = nn.Sequential(nn.Flatten(), nn.Linear(cin * L, 1))
    def forward(s, x, *a): return s.f(x)

# name -> (builder, kind)  kind: '1d' | '2d_delay' | '2d_pi' | 'two'
ARCH = {
 'linear':      (lambda ci, L: Lin(ci, L), '1d'),
 'mlp':         (lambda ci, L: MLP(ci, L), '1d'),
 'cnn_s':       (lambda ci, L: CNN1D(ci, (16, 32, 48), (7, 5, 3)), '1d'),
 'cnn_m':       (lambda ci, L: CNN1D(ci, (32, 48, 64), (7, 5, 3)), '1d'),
 'cnn_l':       (lambda ci, L: CNN1D(ci, (32, 64, 96, 128), (7, 5, 3, 3)), '1d'),
 'cnn_dil':     (lambda ci, L: CNN1D(ci, (32, 48, 64), (7, 5, 3), dil=(1, 2, 4)), '1d'),
 'cnn_se':      (lambda ci, L: CNN1D(ci, (32, 48, 64), (7, 5, 3), se=True), '1d'),
 'cnn_wide_k':  (lambda ci, L: CNN1D(ci, (32, 48, 64), (15, 9, 5)), '1d'),
 'resnet1d':    (lambda ci, L: Res1D(ci), '1d'),
 'tcn':         (lambda ci, L: TCN(ci), '1d'),
 'cnn_gru':     (lambda ci, L: CNNGRU(ci), '1d'),
 'transformer': (lambda ci, L: TFM(ci), '1d'),
 'unet1d':      (lambda ci, L: UNet1D(ci), '1d'),
 'cnn2d_delay': (lambda ci, L: CNN2D(1), '2d_delay'),
 'cnn2d_pi':    (lambda ci, L: CNN2D(2), '2d_pi'),
 'twostream':   (lambda ci, L: TwoStream(ci, 2), 'two'),
}

# ---------------------------------------------------------------- tensors
def make_inputs(idx, kind, win, use_x):
    r = crop(R[idx], win)
    if kind == '2d_delay':
        return torch.from_numpy(delay_matrix(r).astype(np.float32)), None
    if kind == '2d_pi':
        return torch.from_numpy(PI[idx].astype(np.float32)), None
    ch = [r, crop(XR[idx], win)] if use_x else [r]
    x1 = torch.from_numpy(np.stack(ch, 1).astype(np.float32))
    x2 = torch.from_numpy(PI[idx].astype(np.float32)) if kind == 'two' else None
    return x1, x2

def event_metrics(prob, centers, fq, thr, tol_ms=50, refr_ms=250):
    p = np.convolve(prob, np.ones(3) / 3, mode='same')
    pk, _ = sg.find_peaks(p, height=thr, distance=max(int(refr_ms / 1000 * FS / HOP), 1))
    det = centers[pk]; tol = int(tol_ms / 1000 * FS)
    gm = np.zeros(len(fq), bool); tp = 0; errs = []
    for d in det:
        dd = np.abs(fq - d); ok = np.where((dd <= tol) & (~gm))[0]
        if len(ok):
            j = ok[np.argmin(dd[ok])]; gm[j] = True; tp += 1; errs.append(dd[j] / FS * 1000)
    fp = len(det) - tp; fn = len(fq) - int(gm.sum())
    se = tp / (tp + fn) * 100 if tp + fn else 0.; ppv = tp / (tp + fp) * 100 if tp + fp else 0.
    return dict(Se=se, PPV=ppv, F1=2 * se * ppv / (se + ppv) if se + ppv else 0.,
                jitter=float(np.mean(errs)) if errs else float('nan'), TP=tp, FP=fp, FN=fn)

def eval_record(model, rec_i, kind, win, use_x, thr_grid=np.arange(.05, .95, .05)):
    """returns (best_f1_over_thresholds, best_thr, per-lead metrics at best thr)"""
    model.eval(); per_thr = {t: [] for t in thr_grid}
    for lead in range(1, 5):
        m = (REC == rec_i) & (LEAD == lead)
        idx = np.where(m)[0]
        if not len(idx): continue
        x1, x2 = make_inputs(idx, kind, win, use_x)
        with torch.no_grad():
            pr = []
            for i in range(0, len(idx), 4096):
                a = x1[i:i + 4096]; b = x2[i:i + 4096] if x2 is not None else None
                pr.append(torch.sigmoid(model(a, b)).view(-1).numpy())
            pr = np.concatenate(pr)
        cen = CEN[idx]; fq = FQ[RECS[rec_i]]
        for t in thr_grid: per_thr[t].append(event_metrics(pr, cen, fq, t))
    best_t = max(thr_grid, key=lambda t: np.mean([d['F1'] for d in per_thr[t]]))
    ms = per_thr[best_t]
    return float(np.mean([d['F1'] for d in ms])), float(best_t), ms

def train(model, tr_idx, kind, win, use_x, target='binary', epochs=12, bs=512, lr=2e-3):
    x1, x2 = make_inputs(tr_idx, kind, win, use_x)
    y = torch.from_numpy((HM[tr_idx] if target == 'heatmap' else Y[tr_idx]).astype(np.float32))
    pw = torch.tensor([float((Y[tr_idx] == 0).sum() / max((Y[tr_idx] == 1).sum(), 1))])
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, lr, epochs * math.ceil(len(tr_idx) / bs))
    n = len(tr_idx)
    for ep in range(epochs):
        model.train(); perm = torch.randperm(n)
        for i in range(0, n, bs):
            j = perm[i:i + bs]
            a = x1[j]; b = x2[j] if x2 is not None else None
            out = model(a, b).view(-1)
            loss = (F.binary_cross_entropy_with_logits(out, y[j]) if target == 'heatmap'
                    else F.binary_cross_entropy_with_logits(out, y[j], pos_weight=pw))
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sch.step()
    return model

def nparams(m): return sum(p.numel() for p in m.parameters())

# ---------------------------------------------------------------- stage 1
def stage1(win=75, use_x=True, target='binary', epochs=12):
    tr = np.where(np.isin(REC, [0, 1, 2]))[0]           # r01 r04 r07
    log(f'\n=== STAGE 1 architecture search | train r01,r04,r07 ({len(tr)} win) | val r08 | '
        f'win={win} samples ({win*4} ms), use_x={use_x}, target={target}, epochs={epochs} ===')
    rows = []
    for name, (build, kind) in ARCH.items():
        t0 = time.time()
        ci = 2 if use_x else 1
        torch.manual_seed(0)
        m = build(ci, win)
        try:
            train(m, tr, kind, win, use_x, target, epochs)
            f1, thr, ms = eval_record(m, 3, kind, win, use_x)     # r08
        except Exception as e:
            log(f'{name:14s} FAILED: {type(e).__name__}: {e}'); continue
        rows.append(dict(arch=name, kind=kind, params=nparams(m), val_F1=round(f1, 2), thr=thr,
                         Se=round(float(np.mean([d["Se"] for d in ms])), 2),
                         PPV=round(float(np.mean([d["PPV"] for d in ms])), 2),
                         jitter=round(float(np.nanmean([d["jitter"] for d in ms])), 1),
                         sec=round(time.time() - t0, 1)))
        log(f'{name:14s} params {nparams(m):>8,} | val F1 {f1:6.2f} | Se {rows[-1]["Se"]:5.1f} '
            f'| PPV {rows[-1]["PPV"]:5.1f} | jitter {rows[-1]["jitter"]:5.1f} ms | thr {thr:.2f} | {rows[-1]["sec"]:.0f}s')
    rows.sort(key=lambda r: -r['val_F1'])
    log('\n-- ranking --')
    for r in rows: log(f'  {r["val_F1"]:6.2f}  {r["arch"]:14s} ({r["params"]:,} params)')
    return rows

# ---------------------------------------------------------------- stage 2: design variants
def stage2(best_arch, epochs=12):
    """Vary ONE design choice at a time around the winning architecture. Same dev split."""
    tr = np.where(np.isin(REC, [0, 1, 2]))[0]
    build, kind = ARCH[best_arch]
    log(f'\n=== STAGE 2 design variants around "{best_arch}" | train r01,r04,r07 | val r08 ===')
    variants = [
        dict(tag='baseline  (r+x, 300 ms, binary)', win=75,  use_x=True,  target='binary'),
        dict(tag='residual only (r, 300 ms)',       win=75,  use_x=False, target='binary'),
        dict(tag='window 500 ms',                   win=125, use_x=True,  target='binary'),
        dict(tag='window 200 ms',                   win=51,  use_x=True,  target='binary'),
        dict(tag='Gaussian heatmap target',         win=75,  use_x=True,  target='heatmap'),
        dict(tag='window 500 ms + heatmap',         win=125, use_x=True,  target='heatmap'),
    ]
    rows = []
    for v in variants:
        t0 = time.time(); torch.manual_seed(0)
        m = build(2 if v['use_x'] else 1, v['win'])
        try:
            train(m, tr, kind, v['win'], v['use_x'], v['target'], epochs)
            f1, thr, ms = eval_record(m, 3, kind, v['win'], v['use_x'])
        except Exception as e:
            log(f'{v["tag"]:34s} FAILED {type(e).__name__}: {e}'); continue
        rows.append(dict(**{k: v[k] for k in ('tag', 'win', 'use_x', 'target')}, params=nparams(m),
                         val_F1=round(f1, 2), thr=thr,
                         Se=round(float(np.mean([d['Se'] for d in ms])), 2),
                         PPV=round(float(np.mean([d['PPV'] for d in ms])), 2),
                         jitter=round(float(np.nanmean([d['jitter'] for d in ms])), 1)))
        log(f'{v["tag"]:34s} val F1 {f1:6.2f} | Se {rows[-1]["Se"]:5.1f} | PPV {rows[-1]["PPV"]:5.1f} '
            f'| jitter {rows[-1]["jitter"]:5.1f} ms | {time.time()-t0:.0f}s')
    rows.sort(key=lambda r: -r['val_F1'])
    return rows

# ---------------------------------------------------------------- stage 3: full LORO
def stage3(cands, epochs=12, seeds=(0, 1, 2)):
    """cands: list of dicts {arch, win, use_x, target}. Full 5-fold LORO with an inner
    validation record for threshold selection. Reports macro/micro F1 per (record x lead)."""
    log(f'\n=== STAGE 3 full LORO, {len(cands)} candidates x 5 folds x {len(seeds)} seeds ===')
    allres = {}
    for cd in cands:
        build, kind = ARCH[cd['arch']]
        tag = f"{cd['arch']}|win{cd['win']}|x{int(cd['use_x'])}|{cd['target']}"
        per_seed = []
        for sd in seeds:
            rows = []
            for ti in range(5):
                others = [i for i in range(5) if i != ti]
                vi = others[0]; tri = others[1:]
                tr = np.where(np.isin(REC, tri))[0]
                torch.manual_seed(sd)
                m = build(2 if cd['use_x'] else 1, cd['win'])
                train(m, tr, kind, cd['win'], cd['use_x'], cd['target'], epochs)
                _, thr, _ = eval_record(m, vi, kind, cd['win'], cd['use_x'])     # threshold on VAL
                # evaluate test record at that fixed threshold, per lead
                for lead in range(1, 5):
                    idx = np.where((REC == ti) & (LEAD == lead))[0]
                    x1, x2 = make_inputs(idx, kind, cd['win'], cd['use_x'])
                    m.eval()
                    with torch.no_grad():
                        pr = np.concatenate([torch.sigmoid(m(x1[i:i+4096], x2[i:i+4096] if x2 is not None else None)).view(-1).numpy()
                                             for i in range(0, len(idx), 4096)])
                    mm = event_metrics(pr, CEN[idx], FQ[RECS[ti]], thr)
                    mm.update(rec=RECS[ti], lead=lead, thr=thr, seed=sd)
                    rows.append(mm)
            f1s = [r['F1'] for r in rows]
            tp = sum(r['TP'] for r in rows); fp = sum(r['FP'] for r in rows); fn = sum(r['FN'] for r in rows)
            mse = tp / (tp + fn) * 100; mpp = tp / (tp + fp) * 100
            per_seed.append(dict(seed=sd, macro_F1=float(np.mean(f1s)), sd_F1=float(np.std(f1s)),
                                 micro_F1=2 * mse * mpp / (mse + mpp),
                                 macro_Se=float(np.mean([r['Se'] for r in rows])),
                                 macro_PPV=float(np.mean([r['PPV'] for r in rows])),
                                 jitter=float(np.nanmean([r['jitter'] for r in rows])), rows=rows))
            log(f'  {tag:38s} seed {sd}: macro F1 {per_seed[-1]["macro_F1"]:6.2f} '
                f'(+-{per_seed[-1]["sd_F1"]:5.2f}) | micro {per_seed[-1]["micro_F1"]:6.2f} '
                f'| Se {per_seed[-1]["macro_Se"]:5.1f} | PPV {per_seed[-1]["macro_PPV"]:5.1f}')
        allres[tag] = per_seed
        mf = [p['macro_F1'] for p in per_seed]
        log(f'>>> {tag:38s} macro F1 over seeds {np.mean(mf):6.2f} +- {np.std(mf):4.2f}')
    return allres

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', default='1'); ap.add_argument('--epochs', type=int, default=12)
    ap.add_argument('--arch', default='cnn_m'); ap.add_argument('--cands', default='')
    a = ap.parse_args()
    if a.stage == '1':
        rows = stage1(epochs=a.epochs)
        json.dump(rows, open(os.path.join(OUT, 'arch_stage1.json'), 'w'), indent=1)
    elif a.stage == '2':
        rows = stage2(a.arch, epochs=a.epochs)
        json.dump(rows, open(os.path.join(OUT, 'arch_stage2.json'), 'w'), indent=1)
    elif a.stage == '3':
        cands = json.loads(a.cands)
        res = stage3(cands, epochs=a.epochs)
        json.dump({k: [{kk: vv for kk, vv in p.items() if kk != 'rows'} | {'rows': p['rows']} for p in v]
                   for k, v in res.items()}, open(os.path.join(OUT, 'arch_stage3.json'), 'w'), indent=1)
