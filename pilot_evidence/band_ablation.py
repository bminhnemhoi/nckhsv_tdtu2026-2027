"""
BAND-PASS ABLATION driven by the full-text literature reading.

Candidate bands and where each comes from:
  1-45 Hz    : the band currently used in the friend's repository (src/preprocessing.py)
  3-90 Hz    : the band used in our own first pilot
  0.5-100 Hz : Zhong 2018 optimional filtering ablation
  3-100 Hz   : Chen 2025 (Attention R2W-Net) and Asadi 2025 (SCTD-Net)
  10-60 Hz   : Xu 2026 (CNN-2xEEMD) final output filter
  8-45 Hz    : Xu 2026 label-generation filter / stated fetal QRS band
  15-60 Hz   : our own measured optimum in the fQRS-to-baseline RMS ratio test
  20-95 Hz   : Behar, Johnson, Clifford & Oster 2014 GRID-SEARCHED optimum at 250 Hz
               (search fb in [1,49] step 3, fh in [30,120] step 5, applied to all methods)

Protocol: identical to pilot 2. 5 records x 2 leads (1 and 3), hop 20 ms, window 300 ms,
gradient boosting on the raw maternal-cancelled window, LORO with the threshold selected on a
held-out validation record, event scoring at +/-50 ms. Only the band changes.
Also reports the physical fQRS/baseline RMS contrast ratio for each band.
"""
import os, sys, json, time, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, mne, wfdb
from scipy import signal as sg
from sklearn.ensemble import HistGradientBoostingClassifier

ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pilot', os.path.join(ROOT, 'pilot.py'))
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
OUT = os.path.join(ROOT, 'results'); os.makedirs(OUT, exist_ok=True)
RECS, FS, W, HALF, HOP = P.RECS, 250, 75, 37, 5
LEADS = [1, 3]
BANDS = [(1, 45, 'repo hien tai'), (3, 90, 'pilot 1 cua chung toi'), (0.5, 100, 'Zhong 2018'),
         (3, 100, 'Chen 2025 / Asadi 2025'), (8, 45, 'Xu 2026 (nhan)'), (10, 60, 'Xu 2026 (dau ra)'),
         (15, 60, 'do duoc o Phan C'), (20, 95, 'Behar 2014 grid-search')]
LOGF = open(os.path.join(OUT, 'band_ablation_log.txt'), 'a', encoding='utf-8')
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOGF.write(s + '\n'); LOGF.flush()

def prep(raw1k, lo, hi):
    b, a = sg.butter(4, [lo / 500., hi / 500.], btype='band')
    x = sg.filtfilt(b, a, raw1k)
    if lo < 50 < hi:
        x = sg.filtfilt(*sg.iirnotch(50, 30, 1000), x)
    return sg.resample_poly(x, 1, 4)

def contrast(x250, fq):
    """RMS of a +/-25 ms window around each fetal R-peak divided by RMS of a baseline window"""
    seg, base = [], []
    for p in fq:
        if p > 7 and p + 70 < len(x250):
            seg.append(x250[p - 6:p + 7]); base.append(x250[p + 50:p + 63])
    if not seg: return float('nan')
    return float(np.sqrt(np.mean(np.array(seg) ** 2)) / (np.sqrt(np.mean(np.array(base) ** 2)) + 1e-12))

def event_metrics(prob, centers, fq, thr, tol_ms=50, refr_ms=250):
    p = np.convolve(prob, np.ones(3) / 3, mode='same')
    pk, _ = sg.find_peaks(p, height=thr, distance=max(int(refr_ms / 1000 * FS / HOP), 1))
    det = centers[pk]; tol = int(tol_ms / 1000 * FS)
    gm = np.zeros(len(fq), bool); tp = 0
    for d in det:
        dd = np.abs(fq - d); ok = np.where((dd <= tol) & (~gm))[0]
        if len(ok): gm[ok[np.argmin(dd[ok])]] = True; tp += 1
    fp = len(det) - tp; fn = len(fq) - int(gm.sum())
    se = tp / (tp + fn) * 100 if tp + fn else 0.; ppv = tp / (tp + fp) * 100 if tp + fp else 0.
    return dict(Se=se, PPV=ppv, F1=2 * se * ppv / (se + ppv) if se + ppv else 0., TP=tp, FP=fp, FN=fn)

def run_band(lo, hi, note):
    t0 = time.time(); D = {}; cons = []
    for ri, rec in enumerate(RECS):
        raw = mne.io.read_raw_edf(os.path.join(P.RAW, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        fq = (wfdb.rdann(os.path.join(P.RAW, rec + '.edf'), 'qrs').sample / 4).round().astype(int)
        for lead in LEADS:
            x = prep(sig[lead], lo, hi)
            cons.append(contrast(x, fq))
            r = P.robust_scale(P.template_subtract(x, P.detect_mqrs(x)))
            cen = np.arange(HALF + 2, len(r) - HALF - 2, HOP)
            Xw = np.stack([r[c - HALF:c - HALF + W] for c in cen]).astype(np.float32)
            d = np.abs(cen[:, None] - fq[None, :]).min(1)
            D[(ri, lead)] = (Xw, (d <= 5).astype(float), ((d > 5) & (d < 15)), cen, fq)
    rows = []
    for ti in range(5):
        others = [i for i in range(5) if i != ti]; vi = others[0]; tri = others[1:]
        Xtr = np.concatenate([D[(r, l)][0][~D[(r, l)][2]] for r in tri for l in LEADS])
        ytr = np.concatenate([D[(r, l)][1][~D[(r, l)][2]] for r in tri for l in LEADS])
        clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=.08, random_state=0).fit(Xtr, ytr)
        best_t, best_f = .5, -1
        for t in np.arange(.05, .9, .05):
            f = np.mean([event_metrics(clf.predict_proba(D[(vi, l)][0])[:, 1], D[(vi, l)][3], D[(vi, l)][4], t)['F1'] for l in LEADS])
            if f > best_f: best_f, best_t = f, t
        for l in LEADS:
            rows.append(event_metrics(clf.predict_proba(D[(ti, l)][0])[:, 1], D[(ti, l)][3], D[(ti, l)][4], best_t))
    f1s = [r['F1'] for r in rows]
    tp = sum(r['TP'] for r in rows); fp = sum(r['FP'] for r in rows); fn = sum(r['FN'] for r in rows)
    mse = tp / (tp + fn) * 100; mpp = tp / (tp + fp) * 100
    res = dict(band=f'{lo}-{hi}', note=note, contrast=round(float(np.mean(cons)), 3),
               macro_F1=round(float(np.mean(f1s)), 2), sd=round(float(np.std(f1s)), 2),
               micro_F1=round(2 * mse * mpp / (mse + mpp), 2),
               Se=round(float(np.mean([r['Se'] for r in rows])), 2),
               PPV=round(float(np.mean([r['PPV'] for r in rows])), 2), sec=round(time.time() - t0))
    log(f"{res['band']:>9s} Hz | {note:24s} | contrast {res['contrast']:5.2f} | "
        f"macro F1 {res['macro_F1']:6.2f} +-{res['sd']:5.2f} | micro {res['micro_F1']:6.2f} | "
        f"Se {res['Se']:5.1f} | PPV {res['PPV']:5.1f} | {res['sec']}s")
    return res

if __name__ == '__main__':
    log('\n=== BAND ABLATION | 5 records x 2 leads | LORO | +/-50 ms | GBM on raw residual window ===')
    out = [run_band(*b) for b in BANDS]
    out.sort(key=lambda r: -r['macro_F1'])
    log('\n-- ranking by macro F1 --')
    for r in out: log(f"  {r['macro_F1']:6.2f}  {r['band']:>9s} Hz  ({r['note']}), contrast {r['contrast']:.2f}")
    json.dump(out, open(os.path.join(OUT, 'band_ablation.json'), 'w'), indent=1)
