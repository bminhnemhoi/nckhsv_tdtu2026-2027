# -*- coding: utf-8 -*-
"""
ARCH LORO -- bang so sanh kien truc SUA LAI (Phase P1 cua de cuong RelyFetal).

Bang 16 kien truc cu (arch_search.py, stage 1; ket qua trong arch_stage1.json) co 4 loi phuong phap luan.
Script nay sua het 4 loi do va GIU NGUYEN moi thu khac (cua so, nhan, bo toi uu, kien truc):
  (a) dai loc 10-60 Hz  : dung M.preprocess voi CFG mac dinh cua model/fqrs_model.py
                          (Butterworth bac 4, 10-60 Hz + notch 50 Hz, 1000 -> 250 Hz),
                          KHONG phai 3-90 Hz nhu cache_arch.py cu.
  (b) tach theo ban ghi : 5 fold leave-one-record-out. Moi fold: test = 1 ban ghi,
                          val = 1 ban ghi khac (others[0], dung logic cua model/train_final.py),
                          train = 3 ban ghi con lai (4 kenh bung moi ban ghi).
  (c) nguong quyet dinh : quet luoi 0,05..0,90 buoc 0,05 TREN BAN GHI VAL (max trung binh F1 4 kenh),
                          roi ap CO DINH sang ban ghi test. Tuyet doi khong quet nguong tren test.
  (d) bao cao           : macro F1 +/- SD tren 20 (ban ghi x kenh) test, micro F1, Se, PPV, jitter,
                          Wilcoxon ghep cap (2 phia) tung kien truc so voi cnn_dil tren 20 cap F1,
                          kem hieu chinh Holm cho 7 so sanh.

Cua so va nhan (chep dung arch_search.py / cache_arch.py, kind='1d', win=75, use_x=True):
  cua so 75 mau @250 Hz = 300 ms; 2 kenh vao = [du sau khu me, tin hieu loc], deu robust_scale;
  tam cua so buoc 5 mau (20 ms); nhan duong = tam cua so cach QRS thai gan nhat <= 5 mau (20 ms).
  Suy luan: xac suat theo tam cua so -> lam tron 3 diem -> find_peaks (tro 250 ms) -> tam (250 Hz) x4
  -> ghep mot-doi-mot tham lam +/-50 ms bang M.match_events tai 1000 Hz voi nhan goc (edf.qrs).
  Bo toi uu giong bang cu: AdamW lr 2e-3 wd 1e-4, OneCycle, batch 512, pos_weight, clip 1.0.

8 kien truc (dinh nghia chep nguyen van tu arch_search.py): linear, mlp, cnn_m, cnn_dil, cnn_l,
resnet1d, tcn, cnn_gru. Loai bo (ly do trong EXCLUDED): transformer (2109 s/lan train o bang cu,
~22x cnn_dil), cnn2d_pi / twostream (can anh ben vung ripser, nhieu gio; da biet that bai 27,4%),
cnn2d_delay (cham va da thua ro cac mang 1D), cac bien the khong duoc giao (cnn_s, cnn_se, cnn_wide_k, unet1d).

NGAN SACH: toi da 100 phut CPU, 4 luong (may dung chung voi 4 agent khac).
  Do thuc te (bench_threads, may ranh, 4 luong): 1 epoch tren toan bo ~180k cua so train
  cho ca 8 kien truc x 5 fold ~ 22 phut; tcn chiem ~40%. Bang cu dung 10 epoch (~1,8M luot mau, ~3500 buoc
  toi uu) -> khong the giu. Mac dinh: --train_stride 2 (lay 1 trong 2 cua so train -> buoc 40 ms,
  van chong lan 7,5 lan) va --epochs 3 -> ~270k luot mau, ~530 buoc toi uu / mo hinh / fold.
  Moi kien truc nhan cung ngan sach -> so sanh o "ngan sach bang nhau". Danh gia (val + test) van dung
  DU cua so buoc 20 ms. Loss tung epoch duoc ghi de kiem tra hoi tu.
MOT SEED (seed 0). Ket qua la 1 seed -- khong co khoang tin cay giua cac seed.

Chay:  PYTHONIOENCODING=utf-8 python pilot_evidence/arch_loro.py
       (tuy chon: --epochs 3 --train_stride 2 --archs cnn_dil,linear --quick --out_dir <thu muc>)
Xuat:  pilot_evidence/arch_loro.json, pilot_evidence/arch_loro_log.txt
"""
import os, sys, json, time, math, argparse, importlib.util, datetime, platform
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
import mne, wfdb
from scipy import signal as sg
from scipy.stats import wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
from _paths import adfecgdb_dir
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG = M.CFG

RECS = ['r01', 'r04', 'r07', 'r08', 'r10']
LEADS = (1, 2, 3, 4)
FS = CFG['fs']            # 250 Hz
HOP = 5                   # 20 ms: buoc tam cua so (danh gia)
WIN = 75                  # 300 ms
POS_D = 5                 # nhan duong: tam cua so cach QRS thai <= 5 mau (20 ms), nhu cache_arch.py
THR_GRID = np.arange(.05, .95, .05)     # 0,05 .. 0,90 nhu arch_search.py
BASELINE = 'cnn_dil'
EXCLUDED = {
    'transformer': 'qua cham: 2109 s/lan train o bang cu (~22x cnn_dil) tren 11 luong; 5 fold tren 4 luong vuot ngan sach 100 phut mot minh',
    'cnn2d_pi': 'can anh ben vung (ripser) mat nhieu gio de tinh cho ~300k cua so; da biet that bai (27,4% o bang cu)',
    'cnn2d_delay': 'bien the 2D cham (432 s/lan) va da thua ro cac mang 1D (93,1% o bang cu)',
    'twostream': 'phu thuoc anh ben vung nhu cnn2d_pi',
    'cnn_s, cnn_se, cnn_wide_k, unet1d': 'khong nam trong 8 kien truc duoc giao; deu thua cnn_dil o bang cu',
}

LOGF = None
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True)
    if LOGF is not None: LOGF.write(s + '\n'); LOGF.flush()

# ---------------------------------------------------------------- models (chep nguyen van tu arch_search.py)
def blk(i, o, k, d=1, st=1):
    return nn.Sequential(nn.Conv1d(i, o, k, st, padding=(k // 2) * d, dilation=d, bias=False),
                         nn.BatchNorm1d(o), nn.GELU())

class CNN1D(nn.Module):
    def __init__(s, cin, chans, ks, dil=None, head=64):
        super().__init__()
        dil = dil or [1] * len(chans); L = []; p = cin
        for c, k, d in zip(chans, ks, dil):
            L.append(blk(p, c, k, d)); L.append(nn.MaxPool1d(2)); p = c
        s.body = nn.Sequential(*L)
        s.head = nn.Sequential(nn.Linear(p * 2, head), nn.GELU(), nn.Dropout(.2), nn.Linear(head, 1))
    def forward(s, x):
        h = s.body(x); h = torch.cat([h.mean(-1), h.amax(-1)], 1); return s.head(h)

class Res1D(nn.Module):
    def __init__(s, cin, chans=(32, 64, 96)):
        super().__init__(); s.stem = blk(cin, chans[0], 7); mods = []; p = chans[0]
        for c in chans:
            mods.append(nn.ModuleDict({'a': blk(p, c, 3),
                'b': nn.Sequential(nn.Conv1d(c, c, 3, padding=1, bias=False), nn.BatchNorm1d(c)),
                'sc': nn.Conv1d(p, c, 1, bias=False) if p != c else nn.Identity()})); p = c
        s.blocks = nn.ModuleList(mods); s.act = nn.GELU(); s.pool = nn.MaxPool1d(2)
        s.head = nn.Sequential(nn.Linear(p * 2, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x):
        h = s.stem(x)
        for m in s.blocks: h = s.pool(s.act(m['b'](m['a'](h)) + m['sc'](h)))
        return s.head(torch.cat([h.mean(-1), h.amax(-1)], 1))

class TCN(nn.Module):
    def __init__(s, cin, c=48, dils=(1, 2, 4, 8)):
        super().__init__(); s.stem = blk(cin, c, 7); mods = []
        for d in dils:
            mods.append(nn.ModuleDict({'a': blk(c, c, 3, d),
                'b': nn.Sequential(nn.Conv1d(c, c, 3, padding=d, dilation=d, bias=False), nn.BatchNorm1d(c))}))
        s.blocks = nn.ModuleList(mods); s.act = nn.GELU()
        s.head = nn.Sequential(nn.Linear(c * 2, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x):
        h = s.stem(x)
        for m in s.blocks: h = s.act(m['b'](m['a'](h)) + h)
        return s.head(torch.cat([h.mean(-1), h.amax(-1)], 1))

class CNNGRU(nn.Module):
    def __init__(s, cin):
        super().__init__(); s.body = nn.Sequential(blk(cin, 32, 7), nn.MaxPool1d(2), blk(32, 48, 5), nn.MaxPool1d(2))
        s.gru = nn.GRU(48, 32, batch_first=True, bidirectional=True)
        s.head = nn.Sequential(nn.Linear(64, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x):
        h = s.body(x).transpose(1, 2); o, _ = s.gru(h); return s.head(o.mean(1))

class MLP(nn.Module):
    def __init__(s, cin, L):
        super().__init__(); s.f = nn.Sequential(nn.Flatten(), nn.Linear(cin * L, 128), nn.GELU(),
                                                nn.Dropout(.2), nn.Linear(128, 64), nn.GELU(), nn.Linear(64, 1))
    def forward(s, x): return s.f(x)

class Lin(nn.Module):
    def __init__(s, cin, L):
        super().__init__(); s.f = nn.Sequential(nn.Flatten(), nn.Linear(cin * L, 1))
    def forward(s, x): return s.f(x)

ARCH = {
    'linear':   lambda ci, L: Lin(ci, L),
    'mlp':      lambda ci, L: MLP(ci, L),
    'cnn_m':    lambda ci, L: CNN1D(ci, (32, 48, 64), (7, 5, 3)),
    'cnn_dil':  lambda ci, L: CNN1D(ci, (32, 48, 64), (7, 5, 3), dil=(1, 2, 4)),
    'cnn_l':    lambda ci, L: CNN1D(ci, (32, 64, 96, 128), (7, 5, 3, 3)),
    'resnet1d': lambda ci, L: Res1D(ci),
    'tcn':      lambda ci, L: TCN(ci),
    'cnn_gru':  lambda ci, L: CNNGRU(ci),
}
# thu tu chay: baseline truoc, roi tu re den dat, de ket qua quan trong nhat co som nhat
RUN_ORDER = ['cnn_dil', 'linear', 'mlp', 'cnn_m', 'cnn_gru', 'cnn_l', 'resnet1d', 'tcn']

# ---------------------------------------------------------------- data
def load_data(quick=False):
    """dict (rec_idx, lead) -> X (n,2,WIN) float32, y (n,), cen (250 Hz), ann (1000 Hz, nhan goc)"""
    RAW = adfecgdb_dir(); D = {}; half = WIN // 2
    off = np.arange(-half, WIN - half)[None, :]
    for ri, rec in enumerate(RECS):
        raw = mne.io.read_raw_edf(os.path.join(RAW, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        ann = np.asarray(wfdb.rdann(os.path.join(RAW, rec), 'edf.qrs').sample, int)   # 1000 Hz
        fq250 = np.round(ann / (CFG['fs_in'] / FS)).astype(int)
        for lead in LEADS:
            x250 = M.preprocess(sig[lead], CFG['fs_in'], CFG)          # 10-60 Hz + notch, 250 Hz
            res, _ = M.cancel_maternal(x250, CFG)
            r = M.robust_scale(res).astype(np.float32); xs = M.robust_scale(x250).astype(np.float32)
            cen = np.arange(half + 2, len(r) - half - 2, HOP)
            if quick: cen = cen[:1500]
            idx = cen[:, None] + off
            X = np.stack([r[idx], xs[idx]], 1).astype(np.float32)
            d = np.abs(cen[:, None] - fq250[None, :]).min(1)
            D[(ri, lead)] = dict(X=X, y=(d <= POS_D).astype(np.float32), cen=cen, ann=ann)
    return D

def train_set(D, rec_ids, stride):
    Xs, ys = [], []
    for r in rec_ids:
        for l in LEADS:
            d = D[(r, l)]; sel = np.arange(0, len(d['y']), stride)
            Xs.append(d['X'][sel]); ys.append(d['y'][sel])
    return np.concatenate(Xs), np.concatenate(ys)

# ---------------------------------------------------------------- train / predict / score
def train_nn(model, X, y, epochs, seed, bs=512, lr=2e-3):
    """giong train() cua arch_search.py (target='binary')"""
    Xt = torch.from_numpy(X); yt = torch.from_numpy(y)
    pw = torch.tensor([float((y == 0).sum() / max((y == 1).sum(), 1))])
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    steps = epochs * math.ceil(len(X) / bs)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, lr, steps)
    g = torch.Generator().manual_seed(seed); losses = []
    for ep in range(epochs):
        model.train(); perm = torch.randperm(len(X), generator=g); tot = 0.; nb = 0
        for i in range(0, len(X), bs):
            j = perm[i:i + bs]
            loss = F.binary_cross_entropy_with_logits(model(Xt[j]).view(-1), yt[j], pos_weight=pw)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.); opt.step(); sch.step()
            tot += loss.item(); nb += 1
        losses.append(tot / max(nb, 1))
    return losses, steps

def predict(model, X):
    model.eval(); Xt = torch.from_numpy(X)
    with torch.no_grad():
        return np.concatenate([torch.sigmoid(model(Xt[i:i + 4096]).view(-1)).numpy() for i in range(0, len(X), 4096)])

def detect_events(prob, cen, thr):
    """xac suat theo tam cua so -> dinh (chi so mau 250 Hz); giong event_metrics() cua arch_search.py"""
    p = np.convolve(prob, np.ones(3) / 3, mode='same')
    pk, _ = sg.find_peaks(p, height=thr, distance=max(int(CFG['refractory_ms'] / 1000 * FS / HOP), 1))
    return cen[pk]

def score(det250, ann1000):
    """ghep mot-doi-mot tham lam +/-50 ms tai 1000 Hz voi nhan goc (giao thuc chuan cua repo)"""
    scale = CFG['fs_in'] // FS
    return M.match_events(np.asarray(det250, int) * scale, ann1000, CFG['fs_in'], CFG['tolerance_ms'])

def val_threshold(probs, D, vi):
    """chon nguong TREN BAN GHI VAL: max trung binh F1 4 kenh tren luoi; tra ve (thr, F1 val, duong cong)"""
    curve = []
    for t in THR_GRID:
        f = float(np.mean([score(detect_events(probs[l], D[(vi, l)]['cen'], t), D[(vi, l)]['ann'])['F1'] for l in LEADS]))
        curve.append((float(t), f))
    best_t, best_f = max(curve, key=lambda c: c[1])      # max() lay nguong DAU TIEN dat max (on dinh)
    return best_t, best_f, curve

# ---------------------------------------------------------------- one architecture, 5 folds
def run_arch(name, D, epochs, stride, seed):
    rows, folds = [], []
    for ti in range(5):
        t0 = time.time()
        others = [i for i in range(5) if i != ti]; vi, tri = others[0], others[1:]
        Xtr, ytr = train_set(D, tri, stride)
        torch.manual_seed(seed)
        m = ARCH[name](2, WIN)
        losses, steps = train_nn(m, Xtr, ytr, epochs, seed)
        t_train = time.time() - t0
        pv = {l: predict(m, D[(vi, l)]['X']) for l in LEADS}
        thr, vf1, curve = val_threshold(pv, D, vi)
        fr = []
        for l in LEADS:
            pt = predict(m, D[(ti, l)]['X'])
            mm = score(detect_events(pt, D[(ti, l)]['cen'], thr), D[(ti, l)]['ann'])
            mm.update(rec=RECS[ti], lead=l, thr=thr, val_rec=RECS[vi], seed=seed); rows.append(mm); fr.append(mm)
        tf1 = float(np.mean([r['F1'] for r in fr])); per_lead = ' '.join(f'{r["F1"]:5.1f}' for r in fr)
        folds.append(dict(test=RECS[ti], val=RECS[vi], train=[RECS[i] for i in tri], n_train=int(len(ytr)),
                          pos_rate=float(ytr.mean()), opt_steps=int(steps), thr=thr, val_F1=vf1,
                          val_curve=curve, test_F1=tf1, test_F1_per_lead=[r['F1'] for r in fr],
                          loss_per_epoch=losses, sec_train=t_train, sec_total=time.time() - t0))
        log(f'  {name:9s} fold test={RECS[ti]} val={RECS[vi]} n_train={len(ytr):6d} | val F1 {vf1:6.2f} @thr {thr:.2f} '
            f'-> TEST macro F1 {tf1:6.2f} [{per_lead}] | loss {" ".join(f"{x:.3f}" for x in losses)} | {time.time()-t0:.0f}s')
    return rows, folds

def summarise(rows):
    f1 = np.array([r['F1'] for r in rows])
    tp = sum(r['TP'] for r in rows); fp = sum(r['FP'] for r in rows); fn = sum(r['FN'] for r in rows)
    se = tp / (tp + fn) * 100 if tp + fn else 0.; pp = tp / (tp + fp) * 100 if tp + fp else 0.
    return dict(macro_F1=float(f1.mean()), sd_F1=float(f1.std()),
                sd_F1_ddof1=float(f1.std(ddof=1)) if len(f1) > 1 else float('nan'),
                min_F1=float(f1.min()), median_F1=float(np.median(f1)),
                micro_F1=2 * se * pp / (se + pp) if se + pp else 0.,
                Se=float(np.mean([r['Se'] for r in rows])), PPV=float(np.mean([r['PPV'] for r in rows])),
                jitter_ms=float(np.nanmean([r['jitter_ms'] for r in rows])), TP=tp, FP=fp, FN=fn, n=len(rows),
                per_record_F1={rec: float(np.mean([r['F1'] for r in rows if r['rec'] == rec])) for rec in RECS})

def holm(pvals):
    """hieu chinh Holm-Bonferroni; pvals: dict name -> p"""
    items = sorted(((p if np.isfinite(p) else 1.0), k) for k, p in pvals.items()); m = len(items); out = {}; run = 0.
    for i, (p, k) in enumerate(items):
        run = max(run, min(1., (m - i) * p)); out[k] = run
    return out

def stats_vs_baseline(results):
    if BASELINE not in results: return {}
    base = np.array([r['F1'] for r in results[BASELINE]['rows']]); out = {}
    for name, res in results.items():
        if name == BASELINE: continue
        cur = np.array([r['F1'] for r in res['rows']])
        if len(cur) != len(base): continue
        # kiem tra ghep cap dung thu tu (rec, lead)
        assert [(r['rec'], r['lead']) for r in res['rows']] == [(r['rec'], r['lead']) for r in results[BASELINE]['rows']]
        d = cur - base
        try:
            stat, p = wilcoxon(cur, base, zero_method='wilcox', alternative='two-sided'); stat, p = float(stat), float(p)
        except ValueError:
            stat, p = float('nan'), float('nan')     # tat ca hieu = 0
        out[name] = dict(mean_diff=float(d.mean()), median_diff=float(np.median(d)),
                         wins=int((d > 0).sum()), losses=int((d < 0).sum()), ties=int((d == 0).sum()),
                         wilcoxon_stat=stat, p=p, n_pairs=int(len(d)))
    hp = holm({k: v['p'] for k, v in out.items()})
    for k in out: out[k]['p_holm'] = float(hp[k])
    return out

def ranking(results):
    rk = sorted(results, key=lambda k: -results[k]['summary']['macro_F1'])
    return [dict(rank=i + 1, arch=k, macro_F1=results[k]['summary']['macro_F1'], sd_F1=results[k]['summary']['sd_F1'],
                 params=results[k]['params']) for i, k in enumerate(rk)]

def load_old_table():
    p = os.path.join(HERE, 'arch_stage1.json')
    if not os.path.isfile(p): return {}
    old = json.load(open(p, encoding='utf-8'))
    return {r['arch']: dict(old_rank=i + 1, old_val_F1=r['val_F1'], old_thr=r['thr']) for i, r in enumerate(old)}

def load_reference():
    """FetalQRS-TCN (mo hinh chuoi, 4 s, 6 epoch) cung giao thuc LORO -- chi de doi chieu, khong nam trong bang"""
    p = os.path.join(HERE, 'train_final.json')
    if not os.path.isfile(p): return {}
    s = json.load(open(p, encoding='utf-8'))['summary']
    return dict(model='FetalQRSTCN (chuoi 4 s, heatmap, model/train_final.py)', macro_F1=s['macro_F1'], sd_F1=s['sd_F1'],
                micro_F1=s['micro_F1'], seed=s['seed'], epochs=s['epochs'],
                note='cung 5 fold LORO / nguong tren val / +-50 ms / 20 (ban ghi x kenh); KHAC ngu canh (4 s vs 300 ms) va nhan (heatmap)')

def answer_text(results, stats, rk):
    if BASELINE not in results: return 'chua co cnn_dil'
    pos = [r['rank'] for r in rk if r['arch'] == BASELINE][0]
    better = [(k, v) for k, v in stats.items() if v['mean_diff'] > 0]
    sig = [(k, v) for k, v in better if v['p'] < .05]
    sig_holm = [(k, v) for k, v in better if v['p_holm'] < .05]
    worse_sig = [(k, v) for k, v in stats.items() if v['mean_diff'] < 0 and v['p'] < .05]
    s = (f'cnn_dil xep hang {pos}/{len(rk)} (macro F1 {results[BASELINE]["summary"]["macro_F1"]:.2f} +/- '
         f'{results[BASELINE]["summary"]["sd_F1"]:.2f}, n=20, 1 seed). ')
    if better:
        s += 'Kien truc co macro F1 cao hon cnn_dil: ' + ', '.join(f'{k} (+{v["mean_diff"]:.2f}, p={v["p"]:.4f})' for k, v in better) + '. '
    else:
        s += 'Khong kien truc nao co macro F1 cao hon cnn_dil. '
    if sig:
        s += 'Hon cnn_dil co y nghia (Wilcoxon 2 phia p<0,05, chua hieu chinh): ' + ', '.join(k for k, _ in sig) + '. '
        s += ('Sau hieu chinh Holm (7 so sanh): ' + (', '.join(k for k, _ in sig_holm) if sig_holm else 'KHONG con kien truc nao') + '. ')
    else:
        s += 'KHONG co kien truc nao hon cnn_dil co y nghia thong ke (moi p Wilcoxon >= 0,05). '
    if worse_sig:
        s += 'Kem cnn_dil co y nghia (p<0,05): ' + ', '.join(f'{k} ({v["mean_diff"]:+.2f}, p={v["p"]:.4f})' for k, v in worse_sig) + '.'
    return s

# ---------------------------------------------------------------- main
def main():
    global LOGF
    ap = argparse.ArgumentParser()
    ap.add_argument('--epochs', type=int, default=3)
    ap.add_argument('--train_stride', type=int, default=2, help='lay 1 trong N cua so train (N=1: buoc 20 ms, N=2: 40 ms)')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--archs', default=','.join(RUN_ORDER))
    ap.add_argument('--quick', action='store_true', help='chay thu: 1500 cua so/kenh')
    ap.add_argument('--out_dir', default=HERE)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    os.makedirs(a.out_dir, exist_ok=True)
    tag = '_quick' if a.quick else ''
    LOGF = open(os.path.join(a.out_dir, f'arch_loro{tag}_log.txt'), 'w', encoding='utf-8')
    jpath = os.path.join(a.out_dir, f'arch_loro{tag}.json')
    archs = [x for x in a.archs.split(',') if x]
    for x in archs: assert x in ARCH, x
    T0 = time.time()
    log(f'===== ARCH LORO | {datetime.datetime.now():%Y-%m-%d %H:%M:%S} | band {CFG["band"]} Hz notch {CFG["notch"]} | '
        f'win {WIN} mau ({WIN*1000//FS} ms) hop {HOP} ({HOP*1000//FS} ms) | train_stride {a.train_stride} | epochs {a.epochs} | '
        f'seed {a.seed} (1 seed) | threads {torch.get_num_threads()} | quick={a.quick} =====')
    log(f'  giao thuc: 5 fold LORO, val = others[0], nguong chon TREN VAL (luoi {THR_GRID[0]:.2f}..{THR_GRID[-1]:.2f}) roi ap co dinh sang test; '
        f'+/-{CFG["tolerance_ms"]} ms tai 1000 Hz; 20 (ban ghi x kenh); Wilcoxon ghep cap 2 phia vs {BASELINE} + Holm')
    log(f'  archs: {archs}')
    D = load_data(a.quick)
    n_all = sum(len(v['y']) for v in D.values()); pos = sum(v['y'].sum() for v in D.values())
    log(f'  data: {len(D)} (ban ghi x kenh), {n_all} cua so, ti le duong {pos/n_all:.4f}, {time.time()-T0:.0f}s')

    meta = dict(date=str(datetime.datetime.now()), band_hz=list(CFG['band']), notch_hz=CFG['notch'], fs=FS, win_samples=WIN,
                win_ms=WIN * 1000 // FS, hop_samples=HOP, pos_label_max_dist_samples=POS_D, train_stride=a.train_stride,
                train_hop_ms=HOP * a.train_stride * 1000 // FS, epochs=a.epochs, seed=a.seed, n_seeds=1, batch=512, lr=2e-3,
                optimiser='AdamW wd 1e-4 + OneCycle, pos_weight, clip 1.0', threads=torch.get_num_threads(),
                tolerance_ms=CFG['tolerance_ms'], refractory_ms=CFG['refractory_ms'], threshold_grid=[float(t) for t in THR_GRID],
                threshold_selected_on='ban ghi VAL (others[0]); ap co dinh sang test', folds='5 x LORO: test=1, val=1, train=3',
                records=RECS, leads=list(LEADS), n_windows_total=int(n_all), pos_rate=float(pos / n_all), quick=a.quick,
                excluded_architectures=EXCLUDED, python=platform.python_version(), torch=torch.__version__, run_order=archs,
                fixes_vs_old_table=['(a) dai 10-60 Hz thay vi 3-90 Hz', '(b) 5 fold LORO test=1/val=1/train=3 thay vi 1 ban ghi val',
                                    '(c) nguong chon tren val, ap co dinh sang test', '(d) macro F1 +/- SD tren 20 (ban ghi x kenh) + Wilcoxon'],
                note_budget='Ngan sach 100 phut CPU / 4 luong. Bang cu: 10 epoch tren ~180k cua so buoc 20 ms (~1,8M luot mau). '
                            f'Lan nay: {a.epochs} epoch tren cua so buoc {HOP * a.train_stride * 1000 // FS} ms. Moi kien truc nhan cung ngan sach.')
    results = {}; old = load_old_table(); ref = load_reference()
    def dump(final=False):
        st = stats_vs_baseline(results); rk = ranking(results)
        for r in rk:
            if r['arch'] in old: r.update(old[r['arch']])
        json.dump(dict(meta=meta | dict(complete=final, elapsed_min=(time.time() - T0) / 60),
                       results=results, ranking=rk, wilcoxon_vs_cnn_dil=st, old_table_stage1=old, reference_seq_model=ref,
                       answer=answer_text(results, st, rk) if BASELINE in results else ''),
                  open(jpath, 'w', encoding='utf-8'), indent=1)
        return st, rk

    for name in archs:
        t1 = time.time(); torch.manual_seed(a.seed); np.random.seed(a.seed)
        npar = M.n_params(ARCH[name](2, WIN))
        log(f'\n-- {name} ({npar:,} tham so) --')
        rows, folds = run_arch(name, D, a.epochs, a.train_stride, a.seed)
        s = summarise(rows)
        results[name] = dict(params=int(npar), summary=s, folds=folds, rows=rows, sec=time.time() - t1)
        log(f'>> {name:9s} macro F1 {s["macro_F1"]:6.2f} +- {s["sd_F1"]:5.2f} | micro {s["micro_F1"]:6.2f} | Se {s["Se"]:6.2f} | '
            f'PPV {s["PPV"]:6.2f} | jitter {s["jitter_ms"]:4.1f} ms | min {s["min_F1"]:5.1f} | n={s["n"]} | {time.time()-t1:.0f}s | '
            f'tong {(time.time()-T0)/60:.1f} phut')
        dump(False)

    st, rk = dump(True)
    log('\n===== XEP HANG (macro F1 +/- SD tren 20 (ban ghi x kenh) test, nguong chon tren val, 1 seed) =====')
    log(f'{"hang":>4} {"kien truc":10s} {"tham so":>9} {"macro F1":>9} {"SD":>6} {"micro":>7} {"Se":>7} {"PPV":>7} {"jit ms":>7} '
        f'{"vs cnn_dil":>11} {"p Wilcoxon":>11} {"p Holm":>8} {"hang cu":>8} {"F1 cu":>7}')
    for r in rk:
        s = results[r['arch']]['summary']; w = st.get(r['arch'])
        log(f'{r["rank"]:>4} {r["arch"]:10s} {r["params"]:>9,} {s["macro_F1"]:>9.2f} {s["sd_F1"]:>6.2f} {s["micro_F1"]:>7.2f} {s["Se"]:>7.2f} '
            f'{s["PPV"]:>7.2f} {s["jitter_ms"]:>7.1f} '
            + (f'{w["mean_diff"]:>+11.2f} {w["p"]:>11.4f} {w["p_holm"]:>8.4f}' if w else f'{"(baseline)":>11} {"":>11} {"":>8}')
            + f' {r.get("old_rank", "-"):>8} {r.get("old_val_F1", float("nan")):>7.2f}')
    log('\n-- F1 trung binh 4 kenh theo ban ghi test --')
    log(f'{"kien truc":10s} ' + ' '.join(f'{rec:>7s}' for rec in RECS))
    for r in rk:
        pr = results[r['arch']]['summary']['per_record_F1']
        log(f'{r["arch"]:10s} ' + ' '.join(f'{pr[rec]:7.2f}' for rec in RECS))
    log('\n-- Wilcoxon ghep cap (2 phia) tren 20 cap F1 (ban ghi x kenh), kien truc - cnn_dil --')
    for k, v in st.items():
        log(f'  {k:10s} hieu TB {v["mean_diff"]:+6.2f} | trung vi {v["median_diff"]:+6.2f} | thang/thua/hoa {v["wins"]}/{v["losses"]}/{v["ties"]} '
            f'| W={v["wilcoxon_stat"]:.1f} p={v["p"]:.4f} (Holm {v["p_holm"]:.4f})')
    if ref:
        log(f'\n-- Doi chieu (khong nam trong bang): {ref["model"]}: macro F1 {ref["macro_F1"]:.2f} +- {ref["sd_F1"]:.2f} ({ref["note"]})')
    log('\nTRA LOI: ' + answer_text(results, st, rk))
    log(f'DONE {(time.time()-T0)/60:.1f} phut. JSON: {jpath}')

if __name__ == '__main__':
    main()
