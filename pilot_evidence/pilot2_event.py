"""
PILOT 2 - EVENT-LEVEL detection (Se/PPV/F1 at +/-50 ms), leave-one-record-out.
Answers: (a) what F1 does a *simple* classifier on the raw maternal-cancelled window reach under a
clean LORO protocol? (b) do TDA features add anything at event level? (c) is prominence == sublevel H0?

Protocol (leakage-free):
- 5 ADFECGDB records, leads 1 and 3 (each lead treated as an independent single-channel recording).
- LORO: test = 1 record (both leads); of the 4 training records, 1 is held out as validation to pick
  the decision threshold and the peak-picking height; the model is trained on the remaining 3.
- Dense sliding windows, hop 20 ms, window 300 ms; probability series -> smoothing -> find_peaks
  (min distance 250 ms) -> match to reference within +/-50 ms (greedy nearest, one-to-one).
- Feature sets: raw (75 samples of residual), amp (6 classical), tda (sublevel + VR H0/H1 at 2 delays),
  amp+tda, raw+amp+tda.
"""
import os, sys, json, time
import numpy as np
import mne, wfdb
from scipy import signal, stats
from ripser import ripser
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import importlib.util
spec = importlib.util.spec_from_file_location('pilot', os.path.join(ROOT, 'pilot.py'))
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

RAW = P.RAW
OUT = os.path.join(ROOT, 'results')
os.makedirs(OUT, exist_ok=True)
RECS = P.RECS
FS = 250; W = 75; HALF = W // 2
TAU_F, TAU_M = 2, 8
HOP = 5           # 20 ms at 250 Hz
LEADS = [1, 3]
LOG = open(os.path.join(OUT, 'pilot2_log.txt'), 'w', encoding='utf-8')
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n'); LOG.flush()

def features_for_lead(rec, lead):
    raw = mne.io.read_raw_edf(os.path.join(RAW, rec + '.edf'), preload=True, verbose=False)
    sig = raw.get_data()
    fq = (wfdb.rdann(os.path.join(RAW, rec + '.edf'), 'qrs').sample / 4).round().astype(int)
    x = P.preprocess(sig[lead])
    mpk = P.detect_mqrs(x)
    r = P.template_subtract(x, mpk)
    r_s = P.robust_scale(r)
    centers = np.arange(HALF + 2, len(r) - HALF - 2, HOP)
    d = np.abs(centers[:, None] - fq[None, :]).min(1)
    y = (d <= 5).astype(float)          # +/-20 ms -> positive
    amb = (d > 5) & (d < 15)            # 20-60 ms -> ambiguous, excluded from TRAINING only
    F_raw = np.zeros((len(centers), W), np.float32)
    F_amp = np.zeros((len(centers), 6), np.float32)
    F_tda = np.zeros((len(centers), 14 + 14 + 14), np.float32)
    t0 = time.perf_counter()
    for i, c in enumerate(centers):
        w = r_s[c - HALF:c - HALF + W]
        F_raw[i] = w
        F_amp[i] = P.amp_feats(w)
        F_tda[i] = np.concatenate([P.sub_feats(w), P.vr_feats(P.takens(w, TAU_F)), P.vr_feats(P.takens(w, TAU_M))])
    dt = (time.perf_counter() - t0) / len(centers) * 1000
    log(f'  {rec} lead{lead}: {len(centers)} windows, {int(y.sum())} pos, {dt:.2f} ms/window (feature extraction)')
    return dict(centers=centers, y=y, amb=amb, raw=F_raw, amp=F_amp, tda=F_tda, fq=fq, n=len(r))

def event_metrics(prob, centers, fq, thr, fs=FS, tol_ms=50, refractory_ms=250):
    p = np.convolve(prob, np.ones(3) / 3, mode='same')
    dist = int(refractory_ms / 1000 * fs / HOP)
    pk, _ = signal.find_peaks(p, height=thr, distance=max(dist, 1))
    det = centers[pk]
    tol = int(tol_ms / 1000 * fs)
    gm = np.zeros(len(fq), bool); dm = np.zeros(len(det), bool); errs = []
    for i, dpk in enumerate(det):
        dd = np.abs(fq - dpk); ok = np.where((dd <= tol) & (~gm))[0]
        if len(ok):
            j = ok[np.argmin(dd[ok])]; gm[j] = True; dm[i] = True; errs.append(dd[j] / fs * 1000)
    tp = int(dm.sum()); fp = len(det) - tp; fn = len(fq) - int(gm.sum())
    se = tp / (tp + fn) * 100 if tp + fn else 0.0
    ppv = tp / (tp + fp) * 100 if tp + fp else 0.0
    f1 = 2 * se * ppv / (se + ppv) if se + ppv else 0.0
    return dict(TP=tp, FP=fp, FN=fn, Se=se, PPV=ppv, F1=f1, jitter=float(np.mean(errs)) if errs else float('nan'))

def main():
    t0 = time.time()
    log('=== extracting features (5 records x 2 leads, hop 20 ms) ===')
    D = {}
    for rec in RECS:
        for lead in LEADS:
            D[(rec, lead)] = features_for_lead(rec, lead)
    log(f'feature extraction done in {time.time()-t0:.0f}s\n')

    # ---- verify prominence <-> sublevel-set H0 equivalence properly ----
    d0 = D[(RECS[0], LEADS[0])]
    w_all = d0['raw'][:400]
    eq_min, eq_max, n = 0, 0, len(w_all)
    for w in w_all:
        p, ess = P.sublevel_h0(w); p = np.sort(p[p > 1e-9])[::-1]
        pn, _ = P.sublevel_h0(-w); pn = np.sort(pn[pn > 1e-9])[::-1]
        pk = signal.find_peaks(w)[0]; tr = signal.find_peaks(-w)[0]
        sp_max = signal.peak_prominences(w, pk)[0].max() if len(pk) else 0.0
        sp_min = signal.peak_prominences(-w, tr)[0].max() if len(tr) else 0.0
        if len(pn) and abs(pn[0] - sp_max) < 1e-6: eq_max += 1
        if len(p) and abs(p[0] - sp_min) < 1e-6: eq_min += 1
    log(f'PROMINENCE CHECK on {n} windows: top sublevel-H0 persistence of (-w) == scipy max prominence of maxima in {eq_max/n:.3f}; '
        f'top sublevel-H0 persistence of (w) == scipy max prominence of minima in {eq_min/n:.3f}\n')

    SETS = {'raw': ['raw'], 'amp': ['amp'], 'tda': ['tda'], 'amp+tda': ['amp', 'tda'], 'raw+amp+tda': ['raw', 'amp', 'tda']}
    results = {}
    for sname, keys in SETS.items():
        rows = []
        for test_rec in RECS:
            others = [r for r in RECS if r != test_rec]
            val_rec = others[0]; train_recs = others[1:]
            Xtr = np.concatenate([np.concatenate([D[(r, l)][k] for k in keys], 1)[~D[(r, l)]['amb']] for r in train_recs for l in LEADS])
            ytr = np.concatenate([D[(r, l)]['y'][~D[(r, l)]['amb']] for r in train_recs for l in LEADS])
            clf = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.08, max_leaf_nodes=31, random_state=0)
            clf.fit(Xtr, ytr)
            # threshold from validation record
            best_thr, best_f1 = 0.5, -1
            for thr in np.arange(0.05, 0.9, 0.05):
                f1s = []
                for l in LEADS:
                    d = D[(val_rec, l)]
                    pr = clf.predict_proba(np.concatenate([d[k] for k in keys], 1))[:, 1]
                    f1s.append(event_metrics(pr, d['centers'], d['fq'], thr)['F1'])
                if np.mean(f1s) > best_f1: best_f1, best_thr = np.mean(f1s), thr
            for l in LEADS:
                d = D[(test_rec, l)]
                pr = clf.predict_proba(np.concatenate([d[k] for k in keys], 1))[:, 1]
                m = event_metrics(pr, d['centers'], d['fq'], best_thr)
                m.update(record=test_rec, lead=l, thr=float(best_thr), val_rec=val_rec,
                         auc=float(roc_auc_score(d['y'], pr)))
                rows.append(m)
                log(f"{sname:12s} test={test_rec} lead{l} thr={best_thr:.2f} | Se {m['Se']:5.1f} PPV {m['PPV']:5.1f} F1 {m['F1']:5.1f} | jitter {m['jitter']:.1f} ms | winAUC {m['auc']:.3f}")
        f1s = [r['F1'] for r in rows]; ses = [r['Se'] for r in rows]; ppvs = [r['PPV'] for r in rows]
        tp = sum(r['TP'] for r in rows); fp = sum(r['FP'] for r in rows); fn = sum(r['FN'] for r in rows)
        micro_se = tp / (tp + fn) * 100; micro_ppv = tp / (tp + fp) * 100
        micro_f1 = 2 * micro_se * micro_ppv / (micro_se + micro_ppv)
        results[sname] = dict(rows=rows, macro_F1=float(np.mean(f1s)), sd_F1=float(np.std(f1s)),
                              macro_Se=float(np.mean(ses)), macro_PPV=float(np.mean(ppvs)),
                              micro_F1=float(micro_f1), auc=float(np.mean([r['auc'] for r in rows])))
        log(f'>>> {sname:12s} macro F1 {np.mean(f1s):5.2f} +- {np.std(f1s):4.2f} | Se {np.mean(ses):5.2f} | PPV {np.mean(ppvs):5.2f} | micro F1 {micro_f1:5.2f} | mean window AUC {np.mean([r["auc"] for r in rows]):.3f}\n')

    # paired comparison raw vs amp+tda vs raw+amp+tda per (record,lead)
    from scipy.stats import wilcoxon
    log('=== paired Wilcoxon on per-(record,lead) F1, n=10 ===')
    for a, b in [('raw', 'tda'), ('raw', 'amp+tda'), ('raw', 'raw+amp+tda'), ('amp', 'amp+tda'), ('tda', 'amp+tda')]:
        fa = [r['F1'] for r in results[a]['rows']]; fb = [r['F1'] for r in results[b]['rows']]
        try: stat, pv = wilcoxon(fa, fb)
        except Exception as e: stat, pv = float('nan'), float('nan')
        log(f'{a:12s} vs {b:12s}: mean {np.mean(fa):5.2f} vs {np.mean(fb):5.2f}  diff {np.mean(np.array(fb)-np.array(fa)):+5.2f}  p={pv:.4f}')
    json.dump(results, open(os.path.join(OUT, 'pilot2_results.json'), 'w'), indent=1)
    log(f'\nDONE in {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()
