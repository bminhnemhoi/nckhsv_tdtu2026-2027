# -*- coding: utf-8 -*-
"""
fSQI -- chi so chat luong tin hieu thai (fetal Signal Quality Index) cho tung doan 4 s
cua tin hieu du (sau khu me, 250 Hz). Thu vien thuan numpy/scipy/ripser, khong phu thuoc mo hinh.

Ba nhom dac trung, moi ham nhan mang 1 chieu va tra ve dict:
  topo_features(x)        -- dong dieu ben vung (persistent homology) tren nhung tre Takens
                             (dim 3, tau = 5 mau co dinh = 20 ms; tau theo ACF ghi thanh dac trung phu)
                             -> ripser H0/H1 (maxdim=1) tren 300 diem lay mau con ngau nhien, hat giong co dinh.
  sublevel_h0_features(x) -- H0 cua loc sublevel-set tren chinh tin hieu 1 chieu (= prominence cua dinh);
                             cai bang union-find tren cac diem toi han, doi chieu voi scipy.signal.peak_prominences.
  classical_features(x, fs, det=None, raw=None, raw_fs=1000)
                          -- SampEn(m=2, r=0,2*std; tu cai, dem cap bang cKDTree Chebyshev), kurtosis,
                             entropy pho (Welch), ti so nang luong 10-60 Hz/tong (tren doan tho 1000 Hz),
                             CV khoang RR cua dau ra mo hinh, ti le RR hop ly 0,3-0,7 s,
                             bSQI-like = F1 trung khop giua mo hinh va bo do prominence don gian,
                             dinh PSD dai nhip thai 1,8-3,0 Hz (quy tac Power-MF) chuan hoa, tau ACF.

Moi ham chuan hoa robust (median/IQR) doan truoc khi tinh nen bat bien voi thang bien do.

TRAN CUNG (them sau chan doan profile_one.py, de moi doan 4 s < 100 ms tong):
  - ripser: toi da MAX_RIPSER_POINTS = 300 diem; loai diem trung (np.unique sau lam tron 9 chu so)
    va them jitter xac dinh 1e-9 de pha cac cap khoang cach bang nhau (dam may thoai hoa / luoi ADC
    lam ripser cham); dam may < dim + 2 diem -> bieu do rong.
  - SampEn: toi da MAX_SAMPEN_N = 1000 mau (giam mau deu neu dai hon); r <= 0 -> tra ve can tren.
  - sublevel H0: toi da MAX_SUBLEVEL_N = 5000 mau (giam mau deu neu dai hon); vong lap
    tim cuc tri da vector hoa.
  - robust_scale: IQR ~ 0 -> dung std; std ~ 0 -> tra ve toan 0 (tranh chia cho 1e-9).
  - all_features ghi 'slow' = danh sach ham vuot SLOW_MS = 200 ms (de eval ghi log canh bao).
"""
from __future__ import annotations
import time
import numpy as np
from scipy import signal as sg
from scipy import stats
from scipy.spatial import cKDTree
from ripser import ripser

EPS = 1e-12
TOPO_KEYS = ['h1_total', 'h1_max', 'h1_n_abs', 'h1_n_rel', 'h1_entropy', 'h1_ratio', 'h1_count',
             'h0_total', 'h0_max', 'h0_entropy', 'h0_ratio',
             'sl_n_prom', 'sl_total', 'sl_max', 'sl_entropy', 'sl_ratio']
CLASSICAL_KEYS = ['sampen', 'kurtosis', 'spec_entropy', 'band_ratio', 'rr_cv', 'rr_plaus',
                  'bsqi', 'n_det', 'psd_fhr', 'tau_acf']
DEFAULT = dict(dim=3, tau=5, n_points=300, seed=0, abs_thr=0.5, rel_thr=0.2, sl_rel_thr=0.25)
MAX_RIPSER_POINTS = 300     # tran cung so diem dua vao ripser
MAX_SAMPEN_N = 1000         # tran cung so mau cho SampEn (cKDTree, O(N^2) xau nhat ~ 1M phep)
MAX_SUBLEVEL_N = 5000       # tran cung so mau cho H0 sublevel (union-find tren cuc tri)
JITTER = 1e-9               # jitter xac dinh pha cap khoang cach bang nhau truoc ripser
SLOW_MS = 200.0             # nguong canh bao mot ham cham


# ------------------------------------------------------------------ tien ich
def robust_scale(x):
    x = np.asarray(x, float)
    med = np.median(x); iqr = np.subtract(*np.percentile(x, [75, 25]))
    if not np.isfinite(iqr) or iqr < 1e-12:            # doan gan phang / bao hoa: IQR = 0
        sd = float(np.std(x))
        if not np.isfinite(sd) or sd < 1e-12: return np.zeros_like(x)
        return (x - med) / sd
    return (x - med) / iqr


def _cap_len(x, n_max):
    """giam mau deu (stride) neu doan dai hon n_max -- tran cung kich thuoc dau vao"""
    x = np.asarray(x, float)
    if len(x) <= n_max: return x
    step = int(np.ceil(len(x) / n_max))
    return x[::step]


def _entropy(lengths):
    """entropy persistence: p_i = l_i / sum l_i, E = -sum p_i log p_i (0 neu rong)"""
    l = np.asarray(lengths, float); l = l[np.isfinite(l) & (l > 0)]
    if l.size == 0: return 0.0
    p = l / l.sum()
    return float(-np.sum(p * np.log(p + EPS)))


def acf_first_zero(x, max_lag=50):
    """tre tau = diem qua 0 dau tien cua ham tu tuong quan (bi chan trong [1, max_lag])"""
    x = np.asarray(x, float) - np.mean(x)
    n = len(x); den = float(np.dot(x, x)) + EPS
    for k in range(1, min(max_lag, n - 1)):
        if np.dot(x[:-k], x[k:]) / den <= 0: return k
    return max_lag


def takens_embed(x, dim=3, tau=5):
    x = np.asarray(x, float)
    n = len(x) - (dim - 1) * tau
    if n < 10: raise ValueError('doan qua ngan de nhung tre')
    return np.stack([x[i * tau:i * tau + n] for i in range(dim)], 1)


# ------------------------------------------------------------------ (a) topo Takens + ripser
def takens_diagrams(x, dim=3, tau=5, n_points=300, seed=0, maxdim=1):
    """
    (dgms, X_sub): ripser tren dam may nhung tre, lay mau con ngau nhien n_points diem (hat giong co dinh).
    Tran cung: n_points <= MAX_RIPSER_POINTS; loai diem trung (np.unique sau lam tron 9 chu so);
    jitter xac dinh JITTER pha cap khoang cach bang nhau; dam may < dim + 2 diem -> bieu do rong.
    """
    n_points = min(int(n_points), MAX_RIPSER_POINTS)
    X = takens_embed(robust_scale(x), dim, tau)
    rng = np.random.default_rng(seed)
    if len(X) > n_points:
        idx = np.sort(rng.choice(len(X), n_points, replace=False))
        X = X[idx]
    X = np.unique(np.round(X, 9), axis=0)                 # loai diem trung / gan trung
    if len(X) < dim + 2:                                   # thoai hoa hoan toan (doan phang)
        return [np.zeros((0, 2)), np.zeros((0, 2))], X
    X = X + JITTER * rng.standard_normal(X.shape)          # pha cac cap khoang cach bang nhau (luoi ADC)
    return ripser(X, maxdim=maxdim)['dgms'], X


def diagram_features(dgms, abs_thr=0.5, rel_thr=0.2):
    h0 = dgms[0]; h1 = dgms[1] if len(dgms) > 1 else np.zeros((0, 2))
    h0 = h0[np.isfinite(h0[:, 1])]
    l0 = h0[:, 1] - h0[:, 0]
    l1 = h1[:, 1] - h1[:, 0] if len(h1) else np.zeros(0)
    f = {}
    f['h1_total'] = float(l1.sum())
    f['h1_max'] = float(l1.max()) if l1.size else 0.0
    f['h1_n_abs'] = int((l1 > abs_thr).sum())
    f['h1_n_rel'] = int((l1 > rel_thr * f['h1_max']).sum()) if l1.size else 0
    f['h1_entropy'] = _entropy(l1)
    f['h1_ratio'] = float(f['h1_max'] / (f['h1_total'] + EPS))
    f['h1_count'] = int(l1.size)
    f['h0_total'] = float(l0.sum())
    f['h0_max'] = float(l0.max()) if l0.size else 0.0
    f['h0_entropy'] = _entropy(l0)
    f['h0_ratio'] = float(f['h0_max'] / (f['h0_total'] + EPS))
    return f


def topo_features(x, dim=3, tau=5, n_points=300, seed=0, abs_thr=0.5, rel_thr=0.2):
    """dac trung topo cua mot doan 1 chieu (tau co dinh)"""
    dgms, _ = takens_diagrams(x, dim, tau, n_points, seed)
    return diagram_features(dgms, abs_thr, rel_thr)


# ------------------------------------------------------------------ (b) sublevel-set H0 cua tin hieu 1D
def _critical_points(y):
    """chi so cac cuc tri chat (va hai bien) -- H0 sublevel cua ham tuyen tinh tung khuc chi phu thuoc vao chung"""
    d = np.diff(y)
    s = np.sign(d)
    # bo cac buoc phang: lay dau khac 0 gan nhat ve phia truoc (vector hoa: forward-fill chi so)
    nz = s != 0
    if nz.any():
        idx = np.where(nz, np.arange(len(s)), -1)
        idx = np.maximum.accumulate(idx)
        s = np.where(idx >= 0, s[np.maximum(idx, 0)], 0.0)
    ext = np.where(s[1:] * s[:-1] < 0)[0] + 1
    return np.concatenate(([0], ext, [len(y) - 1]))


def sublevel_h0_bars(y):
    """
    H0 cua loc sublevel-set f = y (1D, tuyen tinh tung khuc). Tra ve mang (birth, death, birth_index)
    cho moi thanh phan huu han; thanh phan chua cuc tieu toan cuc song mai (khong ghi).
    Quy tac elder: khi hai thanh phan gap nhau tai diem yen ngua, thanh phan sinh tai cuc tieu thap hon song sot.
    Voi y = -x: moi thanh = mot dinh cua x, death - birth = prominence cua dinh (khi ca hai phia bi chan boi dinh cao hon).
    Tran cung: doan dai hon MAX_SUBLEVEL_N mau bi giam mau deu.
    """
    y = _cap_len(y, MAX_SUBLEVEL_N)
    if len(y) < 3: return np.zeros((0, 3))
    cp = _critical_points(y); v = y[cp]; n = len(v)
    order = np.argsort(v, kind='stable')
    parent = np.full(n, -1); root_min = np.zeros(n, int)

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i

    bars = []
    for i in order:
        roots = []
        for j in (i - 1, i + 1):
            if 0 <= j < n and parent[j] >= 0:
                r = find(j)
                if r not in roots: roots.append(r)
        if not roots:
            parent[i] = i; root_min[i] = i
        elif len(roots) == 1:
            parent[i] = roots[0]
        else:
            ra, rb = roots
            elder, young = (ra, rb) if v[root_min[ra]] <= v[root_min[rb]] else (rb, ra)
            bars.append((v[root_min[young]], v[i], cp[root_min[young]]))
            parent[young] = elder; parent[i] = elder
    return np.asarray(bars, float).reshape(-1, 3)


def sublevel_h0_features(x, rel_thr=0.25):
    """dac trung tu H0 sublevel-set cua -x (cac dinh cua x); persistence = prominence"""
    z = robust_scale(x)
    bars = sublevel_h0_bars(-z)
    l = bars[:, 1] - bars[:, 0] if len(bars) else np.zeros(0)
    lmax = float(l.max()) if l.size else 0.0
    return dict(sl_n_prom=int((l > rel_thr * lmax).sum()) if l.size else 0,
                sl_total=float(l.sum()), sl_max=lmax, sl_entropy=_entropy(l),
                sl_ratio=float(lmax / (l.sum() + EPS)))


def check_sublevel_vs_scipy(x):
    """
    doi chieu: persistence H0 sublevel cua -x == scipy.peak_prominences tai cung dinh,
    cho cac dinh ma ca hai phia deu bi chan boi diem cao hon (scipy dung bien tin hieu lam day
    cho dinh khong bi chan, con persistence thi khong -> chi so sanh dinh bi chan hai phia).
    """
    z = robust_scale(x); bars = sublevel_h0_bars(-z)
    pk, _ = sg.find_peaks(z)
    prom = sg.peak_prominences(z, pk)[0]
    scipy_at = {int(p): float(q) for p, q in zip(pk, prom)}
    diffs = []; n_cmp = 0; n_edge = 0
    for b0, d0, bi in bars:
        bi = int(bi)
        if bi in scipy_at:
            # dinh bi chan hai phia <=> ton tai mau cao hon o ca ben trai va ben phai
            if (z[:bi] > z[bi]).any() and (z[bi + 1:] > z[bi]).any():
                n_cmp += 1; diffs.append(abs((d0 - b0) - scipy_at[bi]))
            else:
                n_edge += 1
    mx = float(max(diffs)) if diffs else 0.0
    return dict(n_bars=int(len(bars)), n_scipy_peaks=int(len(pk)), n_compared=n_cmp,
                n_edge_skipped=n_edge, max_abs_diff=mx, match=bool(mx < 1e-9))


# ------------------------------------------------------------------ (c) chi so co dien
def sample_entropy(x, m=2, r=None):
    """
    SampEn(m, r) tu cai (Richman & Moorman 2000): dem cap mau Chebyshev <= r bang cKDTree (chinh xac,
    doi chieu voi ma tran day trong __main__). Tran cung: N <= MAX_SAMPEN_N (giam mau deu neu dai hon),
    xau nhat O(N^2) ~ 1M phep so sanh; r <= 0 hoac tin hieu phang -> can tren 2 ln(N - m).
    """
    x = _cap_len(x, MAX_SAMPEN_N)
    if r is None: r = 0.2 * np.std(x)
    n = len(x); k = n - m                       # cung so mau cho m va m+1
    if k < 2 or not np.isfinite(r) or r <= 0: return float(2 * np.log(max(k, 2)))
    def count(mm):
        E = np.stack([x[i:i + k] for i in range(mm)], 1)
        T = cKDTree(E)
        return int(T.count_neighbors(T, r, p=np.inf)) - k   # bo tu ghep
    B = count(m); A = count(m + 1)
    if A == 0 or B == 0: return float(2 * np.log(k))         # gioi han tren hop ly
    return float(-np.log(A / B))


def spectral_entropy(x, fs, nperseg=256):
    f, P = sg.welch(x, fs=fs, nperseg=min(nperseg, len(x)))
    P = P / (P.sum() + EPS)
    return float(-np.sum(P * np.log(P + EPS)) / np.log(len(P)))


def band_energy_ratio(raw, fs, band=(10.0, 60.0), total=(0.5, 100.0)):
    f, P = sg.welch(raw - np.mean(raw), fs=fs, nperseg=min(1024, len(raw)))
    mb = (f >= band[0]) & (f <= band[1]); mt = (f >= total[0]) & (f <= total[1])
    return float(P[mb].sum() / (P[mt].sum() + EPS))


def psd_fhr_peak(x, fs, band=(1.8, 3.0)):
    """quy tac Power-MF (blind_lead.pick_blind): dinh PSD cua duong bao Hilbert trong dai nhip thai,
    chuan hoa theo tong PSD 0,5-10 Hz de bat bien thang do"""
    e = np.abs(sg.hilbert(x - np.mean(x))); e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 1024))
    m = (f >= band[0]) & (f <= band[1]); t = (f >= 0.5) & (f <= 10.0)
    return float(P[m].max() / (P[t].sum() + EPS)) if m.any() else 0.0


def simple_prominence_detector(x, fs, refractory_s=0.25, rel=0.4):
    """bo do don gian: duong bao |x| lam tron 40 ms, dinh cach nhau >= 250 ms, prominence >= rel*max"""
    z = robust_scale(x); w = max(1, int(.04 * fs))
    e = np.convolve(np.abs(z), np.ones(w) / w, mode='same')
    pk, pr = sg.find_peaks(e, distance=max(1, int(refractory_s * fs)), prominence=0)
    if len(pk) == 0: return pk
    p = pr['prominences']
    return pk[p >= rel * p.max()]


def agreement_f1(a, b, fs, tol_ms=50):
    """F1 trung khop mot-doi-mot tham lam giua hai tap su kien (bSQI-like)"""
    a = np.sort(np.asarray(a, float)); b = np.asarray(b, float)
    if len(a) == 0 and len(b) == 0: return 1.0
    if len(a) == 0 or len(b) == 0: return 0.0
    tol = tol_ms / 1000 * fs; used = np.zeros(len(b), bool); tp = 0
    for d in a:
        dd = np.abs(b - d); ok = np.where((dd <= tol) & (~used))[0]
        if len(ok): used[ok[int(np.argmin(dd[ok]))]] = True; tp += 1
    return float(2 * tp / (len(a) + len(b)))


def classical_features(x, fs=250, det=None, raw=None, raw_fs=1000):
    """
    x   : doan tin hieu du 250 Hz (sau khu me)
    det : chi so mau (trong doan, cung fs) cua cac dinh mo hinh phat hien; None -> RR/bSQI = NaN
    raw : doan tho tuong ung (raw_fs Hz) de tinh ti so nang luong dai 10-60 Hz; None -> NaN
    """
    z = robust_scale(x)
    f = {}
    f['sampen'] = sample_entropy(z, 2, 0.2 * np.std(z))
    f['kurtosis'] = float(stats.kurtosis(z, fisher=True))
    f['spec_entropy'] = spectral_entropy(z, fs)
    f['band_ratio'] = band_energy_ratio(np.asarray(raw, float), raw_fs) if raw is not None else np.nan
    f['psd_fhr'] = psd_fhr_peak(z, fs)
    f['tau_acf'] = float(acf_first_zero(z))
    if det is not None:
        det = np.sort(np.asarray(det, float))
        f['n_det'] = int(len(det))
        if len(det) >= 3:
            rr = np.diff(det) / fs
            f['rr_cv'] = float(np.std(rr) / (np.mean(rr) + EPS))
            f['rr_plaus'] = float(np.mean((rr >= 0.3) & (rr <= 0.7)))
        else:
            f['rr_cv'] = 1.0; f['rr_plaus'] = 0.0
        f['bsqi'] = agreement_f1(det, simple_prominence_detector(z, fs), fs)
    else:
        f['n_det'] = 0; f['rr_cv'] = np.nan; f['rr_plaus'] = np.nan; f['bsqi'] = np.nan
    return f


# ------------------------------------------------------------------ tong hop + do thoi gian
def all_features(x, fs=250, det=None, raw=None, raw_fs=1000, **kw):
    """tra ve (dict dac trung, dict thoi gian ms)"""
    p = dict(DEFAULT); p.update(kw)
    t = {}
    t0 = time.perf_counter()
    ft = topo_features(x, p['dim'], p['tau'], p['n_points'], p['seed'], p['abs_thr'], p['rel_thr'])
    t['topo_ms'] = (time.perf_counter() - t0) * 1e3
    t0 = time.perf_counter(); fsl = sublevel_h0_features(x, p['sl_rel_thr']); t['sublevel_ms'] = (time.perf_counter() - t0) * 1e3
    t0 = time.perf_counter(); fc = classical_features(x, fs, det, raw, raw_fs); t['classical_ms'] = (time.perf_counter() - t0) * 1e3
    t['total_ms'] = t['topo_ms'] + t['sublevel_ms'] + t['classical_ms']
    t['slow'] = [k[:-3] for k in ('topo_ms', 'sublevel_ms', 'classical_ms') if t[k] > SLOW_MS]
    f = {}; f.update(ft); f.update(fsl); f.update(fc)
    return f, t


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    rng = np.random.default_rng(0)
    fs = 250; t = np.arange(1000) / fs
    x = np.zeros(1000)
    for p in np.arange(0.1, 4.0, 1 / 2.2):
        x += np.exp(-((t - p) ** 2) / (2 * 0.004 ** 2))
    x += 0.1 * rng.standard_normal(1000)
    det = np.array([int(p * fs) for p in np.arange(0.1, 4.0, 1 / 2.2)])
    all_features(x, fs, det, rng.standard_normal(4000), 1000)      # khoi dong
    f, tm = all_features(x, fs, det, rng.standard_normal(4000), 1000)
    for k, v in f.items(): print(f'{k:>14}: {v:.4f}')
    print('thoi gian (ms):', {k: (round(v, 2) if not isinstance(v, list) else v) for k, v in tm.items()})
    print('doi chieu sublevel vs scipy:', check_sublevel_vs_scipy(x))
    # doi chieu SampEn voi cai dat ma tran day
    z = robust_scale(x); r = 0.2 * np.std(z); n = len(z); k = n - 2
    def dense(mm):
        E = np.stack([z[i:i + k] for i in range(mm)], 1); D = np.zeros((k, k))
        for j in range(mm): D = np.maximum(D, np.abs(E[:, j][:, None] - E[:, j][None, :]))
        return (D <= r).sum() - k
    print('SampEn cKDTree', sample_entropy(z, 2, r), 'vs ma tran day', -np.log(dense(3) / dense(2)))
    # tran cung: doan phang, doan luoi ADC (nhieu diem trung), doan rat dai
    for name, xx in (('phang', np.zeros(1000)), ('luoi ADC 3 muc', rng.integers(0, 3, 1000).astype(float)),
                     ('dai 20000 mau', rng.standard_normal(20000))):
        f2, tm2 = all_features(xx, fs, None, None)
        print(f'  tran cung [{name:>14}]: total {tm2["total_ms"]:7.1f} ms  slow={tm2["slow"]}  h1_count={f2["h1_count"]} sampen={f2["sampen"]:.3f}')
