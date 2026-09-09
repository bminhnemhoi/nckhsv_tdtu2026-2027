"""
PILOT EXPERIMENT: do fetal-QRS windows carry a usable topological signature?
Data: ADFECGDB (5 records x 4 abdominal leads, 1 kHz, scalp-derived fQRS annotations)
Pipeline: bandpass 3-90 + notch 50 -> resample 250 Hz -> maternal QRS detection -> median-template
          subtraction with per-beat LS scaling -> residual r
Windows: 300 ms (75 samples), label + if fQRS within +/-20 ms of centre, - if none within +/-60 ms.
Feature groups (per window): amplitude stats, sublevel-set H0 persistences (== peak prominences),
  Vietoris-Rips H0/H1 on Takens(d=3) at tau_f=2 samples (8 ms) and tau_m=8 samples (32 ms),
  persistence images (10x10, H0+H1), raw samples.
Classifier: HistGradientBoosting, leave-one-record-out (train 4 records x 4 leads, test 1 record x 4 leads).
Metrics: ROC-AUC and average precision per held-out record.
Noise: NSTDB em/ma added to aECG at SNR {10,5,0} dB relative to residual power; train clean -> test noisy,
  and matched train/test noise.
"""
import os, sys, json, time, math
import numpy as np
import mne, wfdb
from scipy import signal, stats
from ripser import ripser
from persim import PersistenceImager
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(os.path.dirname(ROOT), 'repo')
RAW = os.path.join(REPO, 'data', 'raw')
NSTDB = os.path.join(ROOT, 'nstdb')
OUT = os.path.join(ROOT, 'results')
os.makedirs(OUT, exist_ok=True)
RECS = ['r01', 'r04', 'r07', 'r08', 'r10']
FS0 = 1000; FS = 250
W = 75; HALF = W // 2
TAU_F = 2; TAU_M = 8
N_POS = 600; N_NEG = 900
SNRS = [10, 5, 0]
rng = np.random.default_rng(0)
LOG = None
def log(*a):
    global LOG
    if LOG is None: LOG = open(os.path.join(OUT, 'pilot_log.txt'), 'w', encoding='utf-8')
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n'); LOG.flush()

# ---------------- signal processing ----------------
def bandpass(x, fs, lo=3.0, hi=90.0, order=4):
    b, a = signal.butter(order, [lo / (fs / 2), hi / (fs / 2)], btype='band'); return signal.filtfilt(b, a, x)
def notch(x, fs, f0=50.0, q=30.0):
    b, a = signal.iirnotch(f0, q, fs); return signal.filtfilt(b, a, x)
def preprocess(x):
    x = notch(bandpass(x, FS0), FS0)
    x = signal.resample_poly(x, 1, FS0 // FS)  # anti-aliased 1000 -> 250
    return x
def robust_scale(x):
    med = np.median(x); iqr = np.subtract(*np.percentile(x, [75, 25])); return (x - med) / (iqr + 1e-9)

def detect_mqrs(x, fs=FS):
    b, a = signal.butter(2, [8 / (fs / 2), 25 / (fs / 2)], btype='band'); f = signal.filtfilt(b, a, x)
    e = np.convolve(np.diff(f, prepend=f[0]) ** 2, np.ones(int(0.12 * fs)) / int(0.12 * fs), mode='same')
    thr = 0.3 * np.percentile(e, 98)
    pk, _ = signal.find_peaks(e, distance=int(0.35 * fs), height=thr)
    r = int(0.04 * fs); out = []
    for p in pk:
        s, t = max(0, p - r), min(len(x), p + r); out.append(s + np.argmax(np.abs(x[s:t])))
    return np.unique(np.array(out, dtype=int))

def template_subtract(x, mpk, fs=FS, pre=0.15, post=0.30):
    ps, po = int(pre * fs), int(post * fs)
    beats = [x[p - ps:p + po] for p in mpk if p - ps >= 0 and p + po < len(x)]
    if len(beats) < 3: return x.copy()
    T = np.median(np.array(beats), axis=0); nT = np.sum(T ** 2) + 1e-12
    m = np.zeros_like(x)
    for p in mpk:
        if p - ps >= 0 and p + po < len(x):
            seg = x[p - ps:p + po]; alpha = np.clip(np.dot(seg, T) / nT, 0.3, 3.0); m[p - ps:p + po] += alpha * T
    return x - m

# ---------------- topology ----------------
def sublevel_h0(x):
    """0-dim persistence of sublevel sets of a 1-D function (Elder rule). Returns finite persistences + essential."""
    n = len(x); order = np.argsort(x, kind='stable'); parent = np.full(n, -1); birth = np.full(n, np.inf); pers = []
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for v in order:
        parent[v] = v; birth[v] = x[v]
        for u in (v - 1, v + 1):
            if 0 <= u < n and parent[u] != -1:
                ru, rv = find(u), find(v)
                if ru == rv: continue
                if birth[ru] < birth[rv]: old, keep = rv, ru
                else: old, keep = ru, rv
                pers.append(x[v] - birth[old]); parent[old] = keep
    essential = x.max() - x.min()
    return np.array(pers), essential

def topk(a, k):
    a = np.sort(np.asarray(a))[::-1]; out = np.zeros(k); m = min(k, len(a)); out[:m] = a[:m]; return out
def sub_feats(w):
    """14 features: for s=w (pairs = prominences of local MINIMA of w) and s=-w (prominences of local MAXIMA of w):
    top-5 finite persistences, essential persistence (range), sum of finite persistences."""
    fs = []
    for s in (w, -w):
        p, ess = sublevel_h0(s); p = p[p > 1e-9]
        fs += list(topk(p, 5)) + [ess, p.sum() if len(p) else 0.0]
    return np.array(fs)
def takens(w, tau, d=3):
    n = len(w) - (d - 1) * tau; return np.stack([w[i * tau:i * tau + n] for i in range(d)], axis=1)
def vr_feats(pc, return_dgms=False):
    res = ripser(pc, maxdim=1); h0, h1 = res['dgms'][0], res['dgms'][1]
    d0 = h0[np.isfinite(h0[:, 1]), 1]
    p1 = (h1[:, 1] - h1[:, 0]) if len(h1) else np.zeros(0)
    ent = 0.0
    if len(d0):
        q = d0 / d0.sum(); ent = float(-(q * np.log(q + 1e-12)).sum())
    f = list(topk(d0, 5)) + [d0.sum() if len(d0) else 0.0, ent, float(len(d0))] + list(topk(p1, 3)) + [float(len(p1)), p1.sum() if len(p1) else 0.0, (h1[np.argmax(p1), 0] if len(p1) else 0.0)]
    return (np.array(f), (h0, h1)) if return_dgms else np.array(f)
def amp_feats(w):
    pp = signal.find_peaks(w)[0]; pn = signal.find_peaks(-w)[0]
    prp = signal.peak_prominences(w, pp)[0].max() if len(pp) else 0.0
    prn = signal.peak_prominences(-w, pn)[0].max() if len(pn) else 0.0
    return np.array([np.sqrt(np.mean(w ** 2)), np.abs(w).max(), prp, prn, stats.kurtosis(w), np.abs(w[HALF - 3:HALF + 4]).max()])
def unit_diam(pc):
    c = pc - pc.mean(0); r = np.linalg.norm(c, axis=1).max(); return c / (r + 1e-9)

# ---------------- noise ----------------
def load_noise():
    out = {}
    for nm in ('em', 'ma'):
        r = wfdb.rdrecord(os.path.join(NSTDB, nm)); s = r.p_signal[:, 0]
        s = signal.resample_poly(s, 25, 36)  # 360 -> 250 Hz
        out[nm] = bandpass(s, FS, 3, 90, 2)
    return out
def add_noise(x, ref_power, snr_db, noise, seed):
    g = np.random.default_rng(seed); n = np.zeros_like(x)
    for nm in ('em', 'ma'):
        s = noise[nm]; st = g.integers(0, len(s) - len(x)); n += s[st:st + len(x)]
    n = n / (np.sqrt(np.mean(n ** 2)) + 1e-12) * np.sqrt(ref_power / (10 ** (snr_db / 10)))
    return x + n

# ---------------- per record/lead processing ----------------
def process_lead(x250, fq, noise=None, snr=None, seed=0, centers=None):
    """x250: preprocessed 250 Hz abdominal lead. returns dict of feature blocks for given centers"""
    mpk = detect_mqrs(x250); r_clean = template_subtract(x250, mpk)
    if snr is not None:
        ref_power = float(np.mean(r_clean ** 2))
        x_noisy = add_noise(x250, ref_power, snr, noise, seed)
        mpk = detect_mqrs(x_noisy); r = template_subtract(x_noisy, mpk); x_use = x_noisy
    else:
        r = r_clean; x_use = x250
    r_s = robust_scale(r); x_s = robust_scale(x_use)
    if centers is None:
        cand = np.arange(HALF + 5, len(r) - HALF - 5, 5)
        d = np.abs(cand[:, None] - fq[None, :]).min(1)
        pos = cand[d <= 5]; neg = cand[d >= 15]
        pos = rng.choice(pos, min(N_POS, len(pos)), replace=False); neg = rng.choice(neg, min(N_NEG, len(neg)), replace=False)
        centers = np.concatenate([pos, neg]); labels = np.concatenate([np.ones(len(pos)), np.zeros(len(neg))])
    else:
        labels = None
    F = {k: [] for k in ('amp', 'sub', 'sub_raw', 'vr_f', 'vr_m', 'vr_f_norm', 'vr_x_m', 'pi_f', 'raw', 'rawx')}
    imgr = PersistenceImager(pixel_size=0.1, birth_range=(0, 1), pers_range=(0, 1), kernel_params={'sigma': [[0.01, 0], [0, 0.01]]})
    t_rip = 0.0; h1stats = []
    for c in centers:
        w = r_s[c - HALF:c - HALF + W]; wx = x_s[c - HALF:c - HALF + W]
        wz = (w - w.mean()) / (w.std() + 1e-9)
        F['amp'].append(amp_feats(w)); F['sub'].append(sub_feats(wz)); F['sub_raw'].append(sub_feats(w))
        t0 = time.perf_counter()
        f_f, (h0, h1) = vr_feats(takens(w, TAU_F), True); F['vr_f'].append(f_f)
        F['vr_m'].append(vr_feats(takens(w, TAU_M)))
        F['vr_f_norm'].append(vr_feats(unit_diam(takens(w, TAU_F))))
        F['vr_x_m'].append(vr_feats(takens(wx, TAU_M)))
        t_rip += time.perf_counter() - t0
        # PI on unit-diameter cloud so that the [0,1] grid is meaningful
        pcn = unit_diam(takens(w, TAU_F)); res = ripser(pcn, maxdim=1)
        d0 = res['dgms'][0]; d0 = d0[np.isfinite(d0[:, 1])]; d1 = res['dgms'][1]
        pi0 = imgr.transform(d0) if len(d0) else np.zeros((10, 10)); pi1 = imgr.transform(d1) if len(d1) else np.zeros((10, 10))
        F['pi_f'].append(np.concatenate([np.asarray(pi0).ravel(), np.asarray(pi1).ravel()]))
        F['raw'].append(w.copy()); F['rawx'].append(wx.copy())
        p1 = (h1[:, 1] - h1[:, 0]) if len(h1) else np.zeros(0)
        h1stats.append([len(p1), p1.max() if len(p1) else 0.0])
    F = {k: np.array(v) for k, v in F.items()}
    F['h1stats'] = np.array(h1stats)
    return centers, labels, F, t_rip / max(len(centers), 1), mpk

def main():
    t_start = time.time()
    noise = load_noise()
    data = {}  # (rec, lead, cond) -> (centers, labels, F)
    sanity = {}
    for rec in RECS:
        raw = mne.io.read_raw_edf(os.path.join(RAW, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data(); fq = (wfdb.rdann(os.path.join(RAW, rec + '.edf'), 'qrs').sample / (FS0 // FS)).round().astype(int)
        for lead in range(1, 5):
            x = preprocess(sig[lead])
            centers, labels, F, trip, mpk = process_lead(x, fq)
            mhr = 60.0 / (np.median(np.diff(mpk)) / FS)
            dmf = np.abs(fq[:, None] - mpk[None, :]).min(1); overlap = float((dmf <= 15).mean())
            sanity[(rec, lead)] = {'n_pos': int(labels.sum()), 'n_neg': int(len(labels) - labels.sum()), 'maternal_bpm': round(mhr, 1), 'n_mqrs': int(len(mpk)), 'fhr_bpm': round(60.0 / (np.median(np.diff(fq)) / FS), 1), 'frac_fqrs_overlap_mqrs_60ms': round(overlap, 3), 'ripser_ms_per_window_4calls': round(trip * 1000, 2)}
            data[(rec, lead, 'clean')] = (centers, labels, F)
            for snr in SNRS:
                c2, _, F2, _, _ = process_lead(x, fq, noise=noise, snr=snr, seed=(hash((rec, lead, snr)) % 2 ** 31), centers=centers)
                data[(rec, lead, snr)] = (centers, labels, F2)
            log(f'{rec} lead{lead}: {sanity[(rec, lead)]}  elapsed {time.time() - t_start:.0f}s')
    # ------------- single-feature diagnostics (clean) -------------
    diag = {}
    allF = {k: np.concatenate([data[(r, l, 'clean')][2][k] for r in RECS for l in range(1, 5)]) for k in ('amp', 'sub', 'vr_f', 'vr_m', 'h1stats', 'sub_raw')}
    y = np.concatenate([data[(r, l, 'clean')][1] for r in RECS for l in range(1, 5)])
    names = {'amp': ['rms', 'maxabs', 'prom_pos', 'prom_neg', 'kurtosis', 'centre_maxabs'],
             'sub': ['zmin_p1', 'zmin_p2', 'zmin_p3', 'zmin_p4', 'zmin_p5', 'z_range', 'zmin_sum', 'zmax_p1', 'zmax_p2', 'zmax_p3', 'zmax_p4', 'zmax_p5', 'z_range2', 'zmax_sum'],
             'sub_raw': ['min_p1', 'min_p2', 'min_p3', 'min_p4', 'min_p5', 'range', 'min_sum', 'max_p1', 'max_p2', 'max_p3', 'max_p4', 'max_p5', 'range2', 'max_sum'],
             'vr_f': ['H0d1', 'H0d2', 'H0d3', 'H0d4', 'H0d5', 'H0sum', 'H0entropy', 'H0count', 'H1p1', 'H1p2', 'H1p3', 'H1count', 'H1sum', 'H1birth_max'],
             'vr_m': ['H0d1', 'H0d2', 'H0d3', 'H0d4', 'H0d5', 'H0sum', 'H0entropy', 'H0count', 'H1p1', 'H1p2', 'H1p3', 'H1count', 'H1sum', 'H1birth_max'],
             'h1stats': ['H1_count_tauf', 'H1_maxpers_tauf']}
    for k, nm in names.items():
        for j, n in enumerate(nm):
            v = allF[k][:, j]
            try: auc = roc_auc_score(y, v)
            except Exception: auc = float('nan')
            d = (v[y == 1].mean() - v[y == 0].mean()) / (np.sqrt(0.5 * (v[y == 1].var() + v[y == 0].var())) + 1e-12)
            diag[f'{k}:{n}'] = {'auc': round(float(auc), 4), 'cohen_d': round(float(d), 3), 'mean_pos': round(float(v[y == 1].mean()), 4), 'mean_neg': round(float(v[y == 0].mean()), 4)}
    log('\n=== single-feature AUC (clean, all records) ===')
    for k, v in sorted(diag.items(), key=lambda kv: -abs(kv[1]['auc'] - 0.5))[:30]: log(f'{k:28s} AUC={v["auc"]:.3f} d={v["cohen_d"]:+.2f} pos={v["mean_pos"]:.3f} neg={v["mean_neg"]:.3f}')
    F0 = data[('r01', 1, 'clean')][2]
    eq_max = np.mean(np.isclose(F0['amp'][:, 2], F0['sub_raw'][:, 7], rtol=1e-6, atol=1e-6))
    eq_min = np.mean(np.isclose(F0['amp'][:, 3], F0['sub_raw'][:, 0], rtol=1e-6, atol=1e-6))
    ge = np.mean(F0['sub_raw'][:, 7] >= F0['amp'][:, 2] - 1e-9)
    log(f'\nCheck (r01 lead1, {len(F0["amp"])} windows): scipy max prominence of positive peaks == largest finite sublevel-set H0 persistence of -w: fraction equal = {eq_max:.3f} (>= : {ge:.3f}); negative peaks: {eq_min:.3f}. Differences arise only from boundary extrema (scipy ignores them).')
    # ------------- LORO classification -------------
    GROUPS = {'amp': ['amp'], 'sub': ['sub'], 'sub_raw': ['sub_raw'], 'vr_f': ['vr_f'], 'vr_m': ['vr_m'], 'vr_f_norm': ['vr_f_norm'], 'vr_x_m': ['vr_x_m'], 'pi_f': ['pi_f'],
              'tda_all': ['sub', 'vr_f', 'vr_m'], 'tda_all_raw': ['sub_raw', 'vr_f', 'vr_m'], 'amp+tda': ['amp', 'sub_raw', 'vr_f', 'vr_m'], 'raw': ['raw'], 'raw+rawx': ['raw', 'rawx'], 'raw+amp+tda': ['raw', 'amp', 'sub_raw', 'vr_f', 'vr_m']}
    def X_of(rec_list, cond, keys):
        Xs, ys = [], []
        for r in rec_list:
            for l in range(1, 5):
                c, lab, F = data[(r, l, cond)]; Xs.append(np.concatenate([F[k] for k in keys], axis=1)); ys.append(lab)
        return np.concatenate(Xs), np.concatenate(ys)
    results = {}
    def run(gname, keys, train_cond, test_cond, clf_name='hgb'):
        aucs, aps = [], []
        for test_rec in RECS:
            tr = [r for r in RECS if r != test_rec]
            Xtr, ytr = X_of(tr, train_cond, keys); Xte, yte = X_of([test_rec], test_cond, keys)
            if clf_name == 'hgb': clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, max_leaf_nodes=31, random_state=0)
            else: clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=0.5))
            clf.fit(Xtr, ytr); p = clf.predict_proba(Xte)[:, 1]
            aucs.append(roc_auc_score(yte, p)); aps.append(average_precision_score(yte, p))
        key = f'{gname}|{clf_name}|train={train_cond}|test={test_cond}'
        results[key] = {'auc_per_rec': [round(a, 4) for a in aucs], 'auc_mean': round(float(np.mean(aucs)), 4), 'auc_sd': round(float(np.std(aucs)), 4), 'ap_mean': round(float(np.mean(aps)), 4), 'ap_per_rec': [round(a, 4) for a in aps]}
        log(f'{key:52s} AUC {np.mean(aucs):.3f}+-{np.std(aucs):.3f}  AP {np.mean(aps):.3f}   per-rec AUC {np.round(aucs, 3).tolist()}')
        return np.mean(aucs)
    log('\n=== LORO classification, clean (HistGradientBoosting) ===')
    for g, keys in GROUPS.items(): run(g, keys, 'clean', 'clean')
    log('\n=== LORO, clean, logistic regression (linear) on raw and on tda ===')
    run('raw', ['raw'], 'clean', 'clean', 'logreg'); run('amp+tda', ['amp', 'sub_raw', 'vr_f', 'vr_m'], 'clean', 'clean', 'logreg')
    log('\n=== Robustness: train CLEAN -> test NOISY (NSTDB em+ma, SNR rel. residual power) ===')
    for g in ('amp', 'sub_raw', 'vr_f', 'vr_m', 'pi_f', 'tda_all_raw', 'amp+tda', 'raw', 'raw+amp+tda'):
        for snr in SNRS: run(g, GROUPS[g], 'clean', snr)
    log('\n=== Robustness: MATCHED train NOISY -> test NOISY ===')
    for g in ('sub_raw', 'vr_f', 'pi_f', 'amp+tda', 'raw', 'raw+amp+tda'):
        for snr in SNRS: run(g, GROUPS[g], snr, snr)
    json.dump({'sanity': {f'{k[0]}_lead{k[1]}': v for k, v in sanity.items()}, 'single_feature': diag, 'loro': results, 'config': {'W': W, 'fs': FS, 'tau_f': TAU_F, 'tau_m': TAU_M, 'n_pos_per_lead': N_POS, 'n_neg_per_lead': N_NEG, 'snrs': SNRS, 'pos_tol_ms': 20, 'neg_margin_ms': 60}}, open(os.path.join(OUT, 'pilot_results.json'), 'w'), indent=1)
    log(f'\nDONE in {time.time() - t_start:.0f}s')

if __name__ == '__main__':
    main()
