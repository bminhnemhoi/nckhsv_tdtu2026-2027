# -*- coding: utf-8 -*-
"""
KHAO SAT DAI LOC TREN CHINH FetalQRS-TCN  (Giai doan 1, muc 6)

Vi sao can: con so "+11,00 diem nho dai loc" hien do tren GRADIENT BOOSTING cua so 300 ms,
2 dao trinh, 5 ban ghi -- KHONG phai tren mang TCN 4 giay duoc mo ta trong bai. Tieu de bai
dang hua mot dieu chua duoc do tren mo hinh that. Day la loi chi mang o moi tap chi.

Thiet ke:
  * 22 chu the doc lap (5 PhysioNet + 7 Silesia B2 khong trung + 10 Silesia B1)
  * K-fold theo NHOM (mac dinh 5 fold): moi fold giu lai ~4-5 chu the, 1 chu the validation
    (uu tien nhan dien cuc da dau), con lai huan luyen
  * Nguong quyet dinh chon TREN CHU THE VALIDATION, ap co dinh sang chu the test
  * Cham: +/-50 ms, kenh PSD mu nhan (so chinh) va trung binh 4 kenh
  * Thong ke o MUC CHU THE: hieu so + cluster bootstrap 95% (lay mau lai CHU THE)
    -- KHONG dung p tren (chu the x kenh) vi do la gia lap

Chay:
    python pilot_evidence/band_tcn.py --calibrate          # do thoi gian 1 fold roi uoc luong
    python pilot_evidence/band_tcn.py                      # chay day du theo ngan sach
    python pilot_evidence/band_tcn.py --bands 10-60,1-45 --seeds 0,1,2
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import sys, json, time, math, argparse, importlib.util, datetime, platform
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from scipy import signal as sg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
sys.path.insert(0, os.path.join(ROOT, 'model'))
from _paths import adfecgdb_dir                                            # noqa: E402
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
CFG = dict(M.CFG)
import silesia_loader as L                                                 # noqa: E402
import mne, wfdb                                                           # noqa: E402

torch.set_num_threads(int(os.environ.get('FQRS_THREADS', 6)))

PHYSIO = ['r01', 'r04', 'r07', 'r08', 'r10']
B2 = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
B1 = [f'B1_{i:02d}' for i in range(1, 11)]
SUBJECTS = PHYSIO + B2 + B1                       # 22 chu the doc lap
SCALP = set(PHYSIO + B2)                          # nhan dien cuc da dau (chuan vang)
B2_DUP = {'B2_01': 'r01', 'B2_02': 'r10', 'B2_07': 'r04', 'B2_10': 'r07', 'B2_11': 'r08'}

BANDS = {  # ten -> (lo, hi)  -- dung 8 dai nhu khao sat GBM de doi chieu truc tiep
    '10-60': (10.0, 60.0), '8-45': (8.0, 45.0), '15-60': (15.0, 60.0), '3-90': (3.0, 90.0),
    '3-100': (3.0, 100.0), '1-45': (1.0, 45.0), '20-95': (20.0, 95.0), '0.5-100': (0.5, 100.0),
}
FS = CFG['fs']; SEG = CFG['seg']; TOL = CFG['tolerance_ms']
LOGF = None


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    if LOGF:
        LOGF.write(s + '\n'); LOGF.flush()


def group_of(t):
    return 'PhysioNet' if t.startswith('r') else t[:2]


# ------------------------------------------------------------------ du lieu
def raw_subject(tag):
    """tra ve (sig4 [4,N] @1000 Hz, fq1000) -- tin hieu THO, chua loc (de loc lai theo tung dai)"""
    if group_of(tag) == 'PhysioNet':
        D = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()[1:5]
        fq = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, int)
    else:
        sig, fq, _ = L.load(tag)
        sig = np.asarray(sig)[:4]
        fq = np.asarray(fq, int)
    return sig.astype(np.float64), fq


def prep_band(sig4, fq1000, lo, hi):
    """loc theo dai (lo,hi) + notch + ve 250 Hz; tra (res[4,n], x[4,n], fq250)"""
    cfg = dict(CFG); cfg['band'] = (lo, hi)
    res, x = [], []
    for k in range(4):
        x250 = M.preprocess(sig4[k], 1000, cfg)
        r, _ = M.cancel_maternal(x250, cfg)
        res.append(M.robust_scale(r).astype(np.float32))
        x.append(M.robust_scale(x250).astype(np.float32))
    n = min(min(len(v) for v in res), min(len(v) for v in x))
    fq = np.unique((fq1000 / (1000 // FS)).round().astype(int))
    fq = fq[(fq >= 0) & (fq < n)]
    return np.stack([v[:n] for v in res]), np.stack([v[:n] for v in x]), fq


def segments(store, tags, stride_short=250, stride_long=500):
    """cat doan 4 s tu cac chu the; B1 (20 phut) dung stride dai hon de tiet kiem bo nho"""
    X, Y = [], []
    for t in tags:
        res, x, fq = store[t]
        st = stride_long if t.startswith('B1') else stride_short
        hm = M.make_heatmap(res.shape[1], fq)
        for k in range(4):
            for s in range(0, res.shape[1] - SEG, st):
                X.append(np.stack([res[k, s:s + SEG], x[k, s:s + SEG]]))
                Y.append(hm[s:s + SEG])
    return torch.from_numpy(np.stack(X)), torch.from_numpy(np.stack(Y))


def train(model, X, Y, epochs, seed, bs=32, lr=3e-3):
    torch.manual_seed(seed)
    pw = torch.tensor([float((Y < .1).sum() / max((Y > .5).sum(), 1))]).clamp(max=30.)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, lr, epochs * math.ceil(len(X) / bs))
    losses = []
    for ep in range(epochs):
        model.train(); perm = torch.randperm(len(X)); tot = 0.
        for i in range(0, len(X), bs):
            j = perm[i:i + bs]
            loss = F.binary_cross_entropy_with_logits(model(X[j]), Y[j], pos_weight=pw)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.); opt.step(); sch.step()
            tot += loss.item()
        losses.append(round(tot / max(1, math.ceil(len(X) / bs)), 4))
    return losses


def psd_score(res, fs=FS, band=(1.8, 3.0)):
    e = np.abs(sg.hilbert(res - res.mean())); e = e - e.mean()
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= band[0]) & (f <= band[1])
    return float(P[m].max()) if m.any() else 0.0


@torch.no_grad()
def score_subject(model, store, tag, thr):
    res, x, fq = store[tag]
    per, scores = {}, {}
    for k in range(4):
        prob = M.probability_series(model, res[k], x[k], CFG)
        det = M.pick_peaks(prob, thr, CFG)
        per[k] = M.match_events(det, fq, FS, TOL)
        scores[k] = psd_score(res[k])
    best = max(scores, key=scores.get)
    return dict(psd_lead=best, F1_psd=per[best]['F1'],
                F1_mean4=float(np.mean([per[k]['F1'] for k in per])),
                F1_oracle=max(per[k]['F1'] for k in per),
                per_lead={k: per[k]['F1'] for k in per})


def pick_threshold(model, store, val_tag, grid=np.arange(.20, .85, .05)):
    best, bt = -1., .45
    for t in grid:
        f = score_subject(model, store, val_tag, float(t))['F1_mean4']
        if f > best: best, bt = f, float(t)
    return bt, best


def make_folds(n_folds, seed=0):
    """K-fold theo nhom: rai deu PhysioNet/B2/B1 vao cac fold; val uu tien nhan da dau"""
    rng = np.random.default_rng(seed)
    pools = {g: list(rng.permutation([s for s in SUBJECTS if group_of(s) == g]))
             for g in ('PhysioNet', 'B2', 'B1')}
    folds = [[] for _ in range(n_folds)]
    i = 0
    for g in ('PhysioNet', 'B2', 'B1'):
        for s in pools[g]:
            folds[i % n_folds].append(str(s)); i += 1
    # chu the validation XOAY VONG qua cac fold (khong lap lai r01 o moi fold)
    val_pool = [s for s in list(rng.permutation(sorted(SCALP)))]
    out = []
    for k, test in enumerate(folds):
        test = sorted(str(s) for s in test)
        rest = [s for s in SUBJECTS if s not in test]
        val = next((str(s) for s in val_pool if s in rest and str(s) not in
                    [o['val'] for o in out]), None)
        if val is None:
            val = next((s for s in rest if s in SCALP), rest[0])
        out.append(dict(test=test, val=str(val),
                        train=sorted(str(s) for s in rest if s != val)))
    return out


def cluster_bootstrap(a, b, n=10000, seed=0):
    """KTC 95% cua hieu so trung binh, lay mau lai CHU THE (khong phai cap chu the x kenh)"""
    a, b = np.asarray(a, float), np.asarray(b, float)
    rng = np.random.default_rng(seed); d = a - b
    idx = rng.integers(0, len(d), size=(n, len(d)))
    m = d[idx].mean(1)
    return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


# ------------------------------------------------------------------ chinh
def run_band(name, store_raw, folds, epochs, seed):
    lo, hi = BANDS[name]
    t0 = time.time()
    store = {}
    for t in SUBJECTS:
        store[t] = prep_band(*store_raw[t], lo, hi)
    rows = {}
    for fi, f in enumerate(folds, 1):
        Xtr, Ytr = segments(store, f['train'])
        model = M.FetalQRSTCN()
        losses = train(model, Xtr, Ytr, epochs, seed)
        del Xtr, Ytr
        model.eval()
        thr, vf1 = pick_threshold(model, store, f['val'])
        for t in f['test']:
            rows[t] = score_subject(model, store, t, thr)
            rows[t].update(fold=fi, threshold=thr, group=group_of(t))
        log(f"    fold {fi}/{len(folds)} val={f['val']} thr={thr:.2f} ({vf1:.2f}) "
            f"test={f['test']} F1_psd={[round(rows[t]['F1_psd'], 1) for t in f['test']]} loss={losses[-1]}")
        del model
    del store
    psd = [rows[t]['F1_psd'] for t in SUBJECTS if t in rows]
    m4 = [rows[t]['F1_mean4'] for t in SUBJECTS if t in rows]
    log(f"  >> {name:<8} macro F1 (PSD) {np.mean(psd):6.2f} +- {np.std(psd, ddof=1):5.2f} | "
        f"(TB 4 kenh) {np.mean(m4):6.2f} +- {np.std(m4, ddof=1):5.2f} | {time.time()-t0:.0f}s")
    return dict(band=name, lo=lo, hi=hi, seed=seed, rows=rows,
                macro_psd=float(np.mean(psd)), sd_psd=float(np.std(psd, ddof=1)),
                macro_mean4=float(np.mean(m4)), sd_mean4=float(np.std(m4, ddof=1)),
                seconds=round(time.time() - t0, 1))


def main():
    global LOGF
    ap = argparse.ArgumentParser()
    ap.add_argument('--bands', default=','.join(BANDS))
    ap.add_argument('--seeds', default='0')
    ap.add_argument('--folds', type=int, default=5)
    ap.add_argument('--epochs', type=int, default=4)
    ap.add_argument('--budget', type=float, default=600., help='phut')
    ap.add_argument('--calibrate', action='store_true')
    ap.add_argument('--out', default=HERE)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    LOGF = open(os.path.join(a.out, 'band_tcn_log.txt'), 'a', encoding='utf-8')
    T0 = time.time()
    bands = [b.strip() for b in a.bands.split(',') if b.strip() in BANDS]
    seeds = [int(s) for s in a.seeds.split(',')]
    folds = make_folds(a.folds)

    log(f'\n===== BAND ABLATION TREN CHINH TCN | {datetime.datetime.now():%Y-%m-%d %H:%M} =====')
    log(f'  22 chu the, {a.folds} fold theo nhom, {a.epochs} epoch, seeds {seeds}, '
        f'{torch.get_num_threads()} luong, doan {SEG/FS:.0f} s, +/-{TOL} ms')
    log(f'  dai: {bands}')
    for f in folds:
        log(f"    fold test={f['test']} val={f['val']} n_train={len(f['train'])}")

    log('\n  nap tin hieu tho 22 chu the...')
    store_raw = {}
    for t in SUBJECTS:
        store_raw[t] = raw_subject(t)
    log(f'  xong {time.time()-T0:.0f}s')

    if a.calibrate:
        log('\n  HIEU CHUAN: chay 1 fold cua dai 10-60 Hz')
        t1 = time.time()
        store = {t: prep_band(*store_raw[t], *BANDS['10-60']) for t in SUBJECTS}
        f = folds[0]
        X, Y = segments(store, f['train'])
        log(f'    {len(X)} doan train; cat doan xong {time.time()-t1:.0f}s')
        t2 = time.time(); train(M.FetalQRSTCN(), X, Y, 1, 0)
        per_ep = time.time() - t2
        log(f'    1 epoch = {per_ep:.0f}s -> 1 fold {a.epochs} epoch ~ {per_ep*a.epochs/60:.1f} phut')
        tot = per_ep * a.epochs * a.folds * len(bands) * len(seeds) / 60
        log(f'    DU KIEN TONG: {tot:.0f} phut cho {len(bands)} dai x {len(seeds)} seed x {a.folds} fold')
        log(f'    (chua ke cham diem ~{a.folds*len(bands)*len(seeds)*0.5:.0f} phut)')
        return

    results = []
    for seed in seeds:
        for b in bands:
            if (time.time() - T0) / 60 > a.budget:
                log(f'  HET NGAN SACH ({a.budget:.0f} phut) -- dung, da xong {len(results)} lan chay')
                break
            log(f'\n-- dai {b} Hz, seed {seed} --')
            results.append(run_band(b, store_raw, folds, a.epochs, seed))
            json.dump(dict(meta=dict(date=str(datetime.datetime.now()), subjects=SUBJECTS,
                                     n_folds=a.folds, epochs=a.epochs, seeds=seeds, bands=bands,
                                     folds=folds, tolerance_ms=TOL, seg_s=SEG / FS,
                                     excluded_duplicates=B2_DUP,
                                     note='Dai loc do tren CHINH FetalQRS-TCN (4 s, heat-map tung mau), '
                                          'khac voi khao sat cu do tren GBM cua so 300 ms / 2 dao trinh / 5 ban ghi.',
                                     platform=platform.platform(), threads=torch.get_num_threads()),
                          results=results),
                      open(os.path.join(a.out, 'band_tcn.json'), 'w'), indent=1)

    # ---------------- tong hop
    log('\n===== XEP HANG (macro F1 muc chu the, n = 22) =====')
    by_band = {}
    for r in results:
        by_band.setdefault(r['band'], []).append(r)
    rk = sorted(by_band, key=lambda b: -np.mean([x['macro_psd'] for x in by_band[b]]))
    log(f'{"dai":>9} {"macro PSD":>10} {"SD":>6} {"TB 4 kenh":>10} {"SD":>6} {"n seed":>7}')
    for b in rk:
        v = by_band[b]
        log(f'{b:>9} {np.mean([x["macro_psd"] for x in v]):10.2f} {np.mean([x["sd_psd"] for x in v]):6.2f} '
            f'{np.mean([x["macro_mean4"] for x in v]):10.2f} {np.mean([x["sd_mean4"] for x in v]):6.2f} {len(v):7d}')

    if '10-60' in by_band and '1-45' in by_band:
        log('\n-- TUONG PHAN CHINH: 10-60 Hz so voi 1-45 Hz, muc CHU THE, cluster bootstrap --')
        for key, lab in (('F1_psd', 'kenh PSD mu nhan'), ('F1_mean4', 'trung binh 4 kenh')):
            a_ = [np.mean([r['rows'][t][key] for r in by_band['10-60'] if t in r['rows']]) for t in SUBJECTS]
            b_ = [np.mean([r['rows'][t][key] for r in by_band['1-45'] if t in r['rows']]) for t in SUBJECTS]
            d, lo, hi = cluster_bootstrap(a_, b_)
            log(f'   {lab:<22} hieu so {d:+6.2f} diem, KTC 95% [{lo:+.2f}; {hi:+.2f}] (n = {len(a_)} chu the)')
        log('   (so cu do tren GBM cua so 300 ms / 2 dao trinh / 5 ban ghi: +11,00)')

    log(f'\nDONE {(time.time()-T0)/60:.1f} phut -> {os.path.join(a.out, "band_tcn.json")}')


if __name__ == '__main__':
    main()
