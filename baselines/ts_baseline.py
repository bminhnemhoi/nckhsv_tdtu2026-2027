# -*- coding: utf-8 -*-
"""
Baseline CO DIEN (khong hoc may) cho do QRS thai nhi tu ECG bung DON KENH -- Phase P2.

Ba baseline duoc cai lai va cham tren cung giao thuc voi mo hinh FetalQRS-TCN:
  1. TS          : khu me bang mau TRUNG BINH (Cerutti 1986 / Behar 2014 "TS"), tru truc tiep,
                   roi do QRS thai tren phan du bang bo do kieu Pan-Tompkins thich nghi.
  2. TS-PCA      : nhu TS nhung mau me = trung binh + hinh chieu len n_pc thanh phan chinh
                   dau cua ma tran nhip me (Behar 2014 "TSpca"), cung bo do Pan-Tompkins.
  3. Prominence  : do dinh TRUC TIEP tren phan du cua M.cancel_maternal (front-end cua nhom:
                   mau trung vi + ti le binh phuong toi thieu) bang scipy.signal.find_peaks
                   voi prominence thich nghi (median + k*MAD) va distance 250 ms.
                   Day la "baseline khong hoc" tren CUNG front-end voi mo hinh, do dung
                   phan dong gop rieng cua mang TCN.

Front-end dung chung: M.preprocess (dai 10-60 Hz, notch 50 Hz, 250 Hz) va
M.detect_maternal_qrs -- lay nguyen tu model/fqrs_model.py, KHONG sua.

Quy tac chon tham so (rule 4): moi tham so hoac co dinh tu y van, hoac chon tren
ban ghi r01 (4 kenh) roi ap NGUYEN cho 4 ban ghi con lai. Khong dung nhan cua
ban ghi dang cham de chon nguong / kenh / sieu tham so. Bao cao ca macro 20 danh gia
(gom r01) va macro 16 danh gia held-out (khong gom r01).

Giao thuc cham: +/-50 ms, ghep mot-doi-mot tham lam (M.match_events), macro F1 =
trung binh F1 tung (ban ghi x kenh). Kenh mu nhan: pick_blind() cua benchmark_dpss/blind_lead.py
(PSD dinh trong dai 1,8-3,0 Hz, theo Power-MF), ap len phan du cua CHINH baseline do.

Ket qua mo hinh de so sanh: benchmark_dpss/all_leads.json (F1 tung ban ghi x kenh, LORO)
va benchmark_dpss/blind_lead.json (kenh PSD). Wilcoxon ghep cap tren 20 (va 16) danh gia.

Chay:  PYTHONIOENCODING=utf-8 python baselines/ts_baseline.py
Ghi:   baselines/results.json, baselines/baselines_log.txt
"""
import os, sys, json, time, datetime, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
import torch
torch.set_num_threads(4)
import mne, wfdb
from scipy import signal as sg
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
from _paths import adfecgdb_dir
from blind_lead import pick_blind, psd_score          # quy tac kenh mu nhan, dung NGUYEN VAN
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG = M.CFG

RECS = ['r01', 'r04', 'r07', 'r08', 'r10']
LEADS = (1, 2, 3, 4)                 # kenh EDF 1..4 = Abdomen_1..4 ; kenh 0 = Direct, CHI de lam nhan
TUNE_REC = 'r01'                     # ban ghi duy nhat dung de chon sieu tham so
HELDOUT = [r for r in RECS if r != TUNE_REC]
FS = CFG['fs']                       # 250 Hz
TOL_MS = CFG['tolerance_ms']         # 50 ms
UP = CFG['fs_in'] // CFG['fs']       # 4: 250 Hz -> 1000 Hz

# Luoi sieu tham so (co dinh truoc, chon tren r01)
GRID_THR_FRAC = [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]   # he so nguong PT: THR = NPK + frac*(SPK-NPK)
GRID_NPC = [2, 3]                             # so thanh phan chinh TS-PCA (Behar 2014: 2-3)
GRID_K = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0]       # prominence = median + k*MAD


class Tee:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.s = sys.stdout
    def write(self, t): self.s.write(t); self.f.write(t)
    def flush(self): self.s.flush(); self.f.flush()


# ------------------------------------------------------------------ du lieu
def load_record(raw_dir, rec):
    raw = mne.io.read_raw_edf(os.path.join(raw_dir, rec + '.edf'), preload=True, verbose=False)
    sig = raw.get_data()
    gt = np.asarray(wfdb.rdann(os.path.join(raw_dir, rec), 'edf.qrs').sample, int)
    return sig, gt


# ------------------------------------------------------------------ khu me (3 cach)
def _beats(x, mpk, ps, po):
    idx = [int(p) for p in mpk if p - ps >= 0 and p + po < len(x)]
    B = np.asarray([x[p - ps:p + po] for p in idx]) if idx else np.zeros((0, ps + po))
    return idx, B


def cancel_ts_mean(x, cfg=CFG):
    """TS: mau TRUNG BINH cac nhip me, tru truc tiep (he so 1, khong ti le)."""
    fs = cfg['fs']; mpk = M.detect_maternal_qrs(x, cfg)
    ps, po = int(cfg['tmpl_pre_s'] * fs), int(cfg['tmpl_post_s'] * fs)
    idx, B = _beats(x, mpk, ps, po)
    if len(idx) < 3:
        return x.copy(), mpk
    T = B.mean(0); m = np.zeros_like(x)
    for p in idx:
        m[p - ps:p + po] += T
    return x - m, mpk


def cancel_ts_pca(x, npc=2, cfg=CFG):
    """TS-PCA (Behar 2014 TSpca): PCA (SVD) tren ma tran nhip me da tru trung binh;
    moi nhip me duoc uoc luong = trung binh + hinh chieu len npc thanh phan chinh dau."""
    fs = cfg['fs']; mpk = M.detect_maternal_qrs(x, cfg)
    ps, po = int(cfg['tmpl_pre_s'] * fs), int(cfg['tmpl_post_s'] * fs)
    idx, B = _beats(x, mpk, ps, po)
    if len(idx) < max(3, npc + 1):
        return x.copy(), mpk
    mu = B.mean(0); C = B - mu
    _, _, Vt = np.linalg.svd(C, full_matrices=False)
    V = Vt[:npc].T                                    # (L, npc), truc chuan
    m = np.zeros_like(x)
    for p, b in zip(idx, B):
        m[p - ps:p + po] += mu + V @ (V.T @ (b - mu))
    return x - m, mpk


def cancel_median_ls(x, cfg=CFG):
    """Front-end cua nhom: mau TRUNG VI + ti le binh phuong toi thieu tung nhip (M.cancel_maternal)."""
    return M.cancel_maternal(x, cfg)


# ------------------------------------------------------------------ bo do QRS thai (2 cach)
FETAL_RR_S = (0.30, 0.70)      # dai RR thai hop ly (nhu M.fetal_heart_rate), dung cho search-back
FETAL_RR_DEFAULT_S = 0.45      # ~133 bpm, khi chua co lich su RR


FETAL_MAX_GAP_S = 1.5          # khong nhip thai nao thua > 1,5 s (40 bpm): search-back BAT BUOC de nguong tu phuc hoi


def pan_tompkins_fetal(res, fs=FS, thr_frac=0.25, refr_s=0.25, int_win_s=0.06, learn_s=2.0,
                       search_back=True, sb_factor=1.66, refine_s=0.04, est='median',
                       max_gap_s=FETAL_MAX_GAP_S):
    """Pan-Tompkins thich nghi cho QRS thai tren phan du (da o dai 10-60 Hz):
    dao ham 5 diem doi xung -> binh phuong -> tich phan cua so 60 ms (can giua, khong tre)
    -> nguong thich nghi THR = NPK + frac*(SPK-NPK), thoi gian tro 250 ms,
    search-back voi 0,5*THR khi mat nhip qua 1,66*RR (RR = trung vi 8 RR hop ly gan nhat,
    gioi han 0,30-0,70 s; mac dinh 0,45 s); search-back BAT BUOC (khong xet nguong) khi khoang
    trong > max_gap_s = 1,5 s (40 bpm) -- chong khoa nguong vinh vien sau xung nhieu lon.
    est='median': SPK/NPK = trung vi 8 dinh gan nhat (Hamilton & Tompkins 1986; Hamilton 2002),
                  ben voi xung nhieu / phan du me lon -- bien the CHINH.
    est='exp'   : SPK/NPK = trung binh mu 1/8 nhu Pan & Tompkins 1985 -- bien the goc, giu de doi chieu
                  (bi khoa nguong khi gap xung lon, xem README).
    Vi tri cuoi = cuc dai |res| trong +/-40 ms quanh dinh tich phan (nhu M.detect_maternal_qrs)."""
    x = np.asarray(res, float); n = len(x)
    d = np.zeros_like(x)
    d[2:-2] = (2 * x[4:] + x[3:-1] - x[1:-3] - 2 * x[:-4]) / 8.0
    sq = d ** 2
    w = max(1, int(round(int_win_s * fs)))
    integ = np.convolve(sq, np.ones(w) / w, mode='same')
    cand, _ = sg.find_peaks(integ)
    if len(cand) == 0:
        return np.zeros(0, int)
    n0 = min(n, int(learn_s * fs))
    spki = float(integ[:n0].max()) / 3.0; npki = float(integ[:n0].mean()) / 2.0
    spk_hist, npk_hist = [spki], [npki]
    thr = npki + thr_frac * (spki - npki)
    refr = int(refr_s * fs)
    rr_lo, rr_hi = int(FETAL_RR_S[0] * fs), int(FETAL_RR_S[1] * fs)
    qrs, rr_hist = [], []

    def upd_spk(v, w_exp):
        nonlocal spki
        if est == 'median':
            spk_hist.append(v); spki = float(np.median(spk_hist[-8:]))
        else:
            spki = w_exp * v + (1 - w_exp) * spki

    def upd_npk(v):
        nonlocal npki
        if est == 'median':
            npk_hist.append(v); npki = float(np.median(npk_hist[-8:]))
        else:
            npki = 0.125 * v + 0.875 * npki

    for c in cand:
        c = int(c); v = float(integ[c])
        if qrs and c - qrs[-1] < refr:
            continue
        if v >= thr:
            qrs.append(c); upd_spk(v, 0.125)
            if len(qrs) >= 2:
                rr_hist.append(qrs[-1] - qrs[-2])
        else:
            upd_npk(v)
            if search_back and qrs:
                ok = [r for r in rr_hist[-8:] if rr_lo <= r <= rr_hi]
                rr_avg = float(np.median(ok)) if ok else FETAL_RR_DEFAULT_S * fs
                gap = c - qrs[-1]
                if gap > sb_factor * rr_avg:
                    lo = qrs[-1] + refr
                    sel = cand[(cand > lo) & (cand <= c)]
                    if len(sel):
                        j = int(sel[np.argmax(integ[sel])])
                        if integ[j] >= 0.5 * thr or gap > max_gap_s * fs:
                            qrs.append(j); rr_hist.append(qrs[-1] - qrs[-2]); upd_spk(float(integ[j]), 0.25)
        thr = npki + thr_frac * (spki - npki)
    qrs = np.array(sorted(set(qrs)), int)
    r = int(refine_s * fs); out = []
    for p in qrs:
        s, t = max(0, p - r), min(n, p + r + 1)
        if t > s:
            out.append(s + int(np.argmax(np.abs(x[s:t]))))
    return np.unique(np.asarray(out, int))


def prominence_detector(res, fs=FS, k=4.0, dist_s=0.25):
    """find_peaks tren |res| voi prominence = median + k*MAD (MAD x1,4826), distance 250 ms."""
    a = np.abs(np.asarray(res, float))
    med = float(np.median(a)); mad = 1.4826 * float(np.median(np.abs(a - med)))
    pk, _ = sg.find_peaks(a, prominence=med + k * mad, distance=max(1, int(dist_s * fs)))
    return pk.astype(int)


# ------------------------------------------------------------------ cham
def score(det250, gt1000):
    r = M.match_events(np.asarray(det250, int) * UP, gt1000, CFG['fs_in'], TOL_MS)
    return {k: (float(v) if isinstance(v, (float, np.floating)) else int(v)) for k, v in r.items()}


def macro(rows):
    """rows: list dict co F1/Se/PPV -> mean, sd (ddof=1)"""
    f = np.array([r['F1'] for r in rows]); s = np.array([r['Se'] for r in rows]); p = np.array([r['PPV'] for r in rows])
    return dict(n=int(len(rows)), F1_mean=float(f.mean()), F1_sd=float(f.std(ddof=1)) if len(f) > 1 else 0.0,
                Se_mean=float(s.mean()), Se_sd=float(s.std(ddof=1)) if len(s) > 1 else 0.0,
                PPV_mean=float(p.mean()), PPV_sd=float(p.std(ddof=1)) if len(p) > 1 else 0.0,
                F1_min=float(f.min()), F1_median=float(np.median(f)))


def wilcoxon_pair(base, model):
    """Wilcoxon ghep cap (baseline vs mo hinh). Tra ve ca hai phia va mot phia (baseline < mo hinh)."""
    b = np.asarray(base, float); m = np.asarray(model, float); d = b - m
    nz = int(np.sum(d != 0))
    out = dict(n=int(len(d)), n_nonzero=nz, mean_diff=float(d.mean()), median_diff=float(np.median(d)),
               n_base_lower=int(np.sum(d < 0)), n_base_higher=int(np.sum(d > 0)), n_tie=int(np.sum(d == 0)))
    if nz == 0:
        out.update(stat=float('nan'), p_two_sided=1.0, p_less=1.0, note='moi hieu deu bang 0')
        return out
    w2 = stats.wilcoxon(b, m, alternative='two-sided')
    w1 = stats.wilcoxon(b, m, alternative='less')
    out.update(stat=float(w2.statistic), p_two_sided=float(w2.pvalue), p_less=float(w1.pvalue))
    return out


# ------------------------------------------------------------------ chay
def main():
    t0 = time.time()
    sys.stdout = Tee(os.path.join(HERE, 'baselines_log.txt'))
    print('=' * 96)
    print('BASELINE CO DIEN -- ADFECGDB, don kenh, +/-%d ms, ghep 1-1 tham lam (M.match_events)' % TOL_MS)
    print('bat dau:', datetime.datetime.now().isoformat(timespec='seconds'))
    print('numpy %s scipy %s torch %s mne %s wfdb %s' % (np.__version__, __import__('scipy').__version__,
                                                          torch.__version__, mne.__version__, wfdb.__version__))
    print('=' * 96)
    RAW = adfecgdb_dir(); print('ADFECGDB:', RAW)

    # ---- mo hinh: F1 tung (ban ghi x kenh) tu all_leads.json, kenh PSD tu blind_lead.json
    all_leads = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'all_leads.json')))
    blind = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'blind_lead.json')))['adfecgdb']
    model_f1 = {rec: {ld: float(all_leads[rec][ld - 1]) for ld in LEADS} for rec in RECS}
    model_psd_lead = {rec: int(blind[rec]['psd_lead']) for rec in RECS}
    model_psd_f1 = {rec: float(blind[rec]['F1_psd']) for rec in RECS}
    for rec in RECS:   # kiem tra nhat quan giua hai file
        assert abs(model_psd_f1[rec] - model_f1[rec][model_psd_lead[rec]]) < 1e-9, rec
    model_macro4 = float(np.mean([model_f1[r][l] for r in RECS for l in LEADS]))
    model_macro4_sd = float(np.std([model_f1[r][l] for r in RECS for l in LEADS], ddof=1))
    model_macro_psd = float(np.mean([model_psd_f1[r] for r in RECS]))
    model_macro4_heldout = float(np.mean([model_f1[r][l] for r in HELDOUT for l in LEADS]))
    print('Mo hinh (all_leads.json): macro 4 kenh = %.2f +/- %.2f ; kenh PSD = %.2f ; held-out 16 = %.2f'
          % (model_macro4, model_macro4_sd, model_macro_psd, model_macro4_heldout))

    # ---- nap du lieu + tien xu ly chung (1 lan)
    print('\n[1] nap du lieu va tien xu ly (M.preprocess 10-60 Hz -> 250 Hz) ...')
    X, GT, NMQ = {}, {}, {}
    for rec in RECS:
        sig, gt = load_record(RAW, rec); GT[rec] = gt; X[rec] = {}
        for ld in LEADS:
            X[rec][ld] = M.preprocess(sig[ld], CFG['fs_in'], CFG)
        print('  %s: %d mau @1000 Hz, %d nhan QRS thai, %d s' % (rec, sig.shape[1], len(gt), sig.shape[1] // 1000))

    # ---- phan du cua 3 cach khu me (TS-PCA cho tung n_pc)
    print('\n[2] khu me: TS (trung binh), TS-PCA (n_pc = %s), median+LS (M.cancel_maternal) ...' % GRID_NPC)
    RES = {rec: {ld: {} for ld in LEADS} for rec in RECS}
    for rec in RECS:
        for ld in LEADS:
            x = X[rec][ld]
            r, mpk = cancel_ts_mean(x); RES[rec][ld]['TS'] = r; NMQ[(rec, ld)] = int(len(mpk))
            for npc in GRID_NPC:
                RES[rec][ld]['TS-PCA%d' % npc] = cancel_ts_pca(x, npc)[0]
            RES[rec][ld]['MedLS'] = cancel_median_ls(x)[0]
        print('  %s: so QRS me do duoc (kenh 1..4) = %s' % (rec, [NMQ[(rec, l)] for l in LEADS]))

    # ---- [3] chon sieu tham so tren r01 (4 kenh), macro F1
    print('\n[3] chon sieu tham so CHI tren %s (4 kenh) -- ap nguyen cho 4 ban ghi con lai' % TUNE_REC)
    tuning = {}

    def tune_f1(canc, det_fn, **kw):
        return float(np.mean([score(det_fn(RES[TUNE_REC][ld][canc], **kw), GT[TUNE_REC])['F1'] for ld in LEADS]))

    # TS + PT
    tuning['TS'] = {str(f): tune_f1('TS', pan_tompkins_fetal, thr_frac=f) for f in GRID_THR_FRAC}
    ts_frac = max(GRID_THR_FRAC, key=lambda f: tuning['TS'][str(f)])
    print('  TS      + PT  : thr_frac -> ' + ', '.join('%.3f: %.2f' % (f, tuning['TS'][str(f)]) for f in GRID_THR_FRAC)
          + '  => chon %.3f' % ts_frac)
    # TS-PCA + PT
    tuning['TS-PCA'] = {}
    for npc in GRID_NPC:
        for f in GRID_THR_FRAC:
            tuning['TS-PCA']['npc=%d,thr_frac=%s' % (npc, f)] = tune_f1('TS-PCA%d' % npc, pan_tompkins_fetal, thr_frac=f)
    best = max(tuning['TS-PCA'], key=lambda k: tuning['TS-PCA'][k])
    pca_npc = int(best.split(',')[0].split('=')[1]); pca_frac = float(best.split('=')[-1])
    for npc in GRID_NPC:
        print('  TS-PCA%d + PT  : thr_frac -> ' % npc + ', '.join(
            '%.3f: %.2f' % (f, tuning['TS-PCA']['npc=%d,thr_frac=%s' % (npc, f)]) for f in GRID_THR_FRAC))
    print('  => chon n_pc=%d, thr_frac=%.3f' % (pca_npc, pca_frac))
    # Prominence tren MedLS
    tuning['Prominence'] = {str(k): tune_f1('MedLS', prominence_detector, k=k) for k in GRID_K}
    prom_k = max(GRID_K, key=lambda k: tuning['Prominence'][str(k)])
    print('  Prominence    : k -> ' + ', '.join('%.0f: %.2f' % (k, tuning['Prominence'][str(k)]) for k in GRID_K)
          + '  => chon k=%.0f' % prom_k)
    # phu: prominence tren TS/TS-PCA va PT tren MedLS (ma tran bo sung, cung quy tac chon tren r01)
    tuning['supp_Prom_on_TS'] = {str(k): tune_f1('TS', prominence_detector, k=k) for k in GRID_K}
    tuning['supp_Prom_on_TS-PCA'] = {str(k): tune_f1('TS-PCA%d' % pca_npc, prominence_detector, k=k) for k in GRID_K}
    tuning['supp_PT_on_MedLS'] = {str(f): tune_f1('MedLS', pan_tompkins_fetal, thr_frac=f) for f in GRID_THR_FRAC}
    k_ts = max(GRID_K, key=lambda k: tuning['supp_Prom_on_TS'][str(k)])
    k_pca = max(GRID_K, key=lambda k: tuning['supp_Prom_on_TS-PCA'][str(k)])
    f_med = max(GRID_THR_FRAC, key=lambda f: tuning['supp_PT_on_MedLS'][str(f)])
    # phu: PT bien the GOC (trung binh mu 1/8, Pan & Tompkins 1985) -- giu de doi chieu voi bien the trung vi
    tuning['supp_TS+PTexp'] = {str(f): tune_f1('TS', pan_tompkins_fetal, thr_frac=f, est='exp') for f in GRID_THR_FRAC}
    tuning['supp_TS-PCA+PTexp'] = {str(f): tune_f1('TS-PCA%d' % pca_npc, pan_tompkins_fetal, thr_frac=f, est='exp') for f in GRID_THR_FRAC}
    f_ts_exp = max(GRID_THR_FRAC, key=lambda f: tuning['supp_TS+PTexp'][str(f)])
    f_pca_exp = max(GRID_THR_FRAC, key=lambda f: tuning['supp_TS-PCA+PTexp'][str(f)])
    print('  [phu] TS + PT-exp     : thr_frac -> ' + ', '.join('%.3f: %.2f' % (f, tuning['supp_TS+PTexp'][str(f)]) for f in GRID_THR_FRAC) + '  => %.3f' % f_ts_exp)
    print('  [phu] TS-PCA + PT-exp : thr_frac -> ' + ', '.join('%.3f: %.2f' % (f, tuning['supp_TS-PCA+PTexp'][str(f)]) for f in GRID_THR_FRAC) + '  => %.3f' % f_pca_exp)

    # ---- cau hinh cuoi cua 3 baseline chinh + 3 to hop bo sung
    configs = {
        'TS':          dict(canc='TS', det='PT', kw=dict(thr_frac=ts_frac),
                            mota='mau trung binh, tru truc tiep; Pan-Tompkins thich nghi'),
        'TS-PCA':      dict(canc='TS-PCA%d' % pca_npc, det='PT', kw=dict(thr_frac=pca_frac),
                            mota='mau PCA (n_pc=%d) tren nhip me; Pan-Tompkins thich nghi' % pca_npc),
        'Prominence':  dict(canc='MedLS', det='Prom', kw=dict(k=prom_k),
                            mota='phan du M.cancel_maternal (front-end cua nhom); find_peaks prominence=median+%.0f*MAD, distance 250 ms' % prom_k),
        'supp_TS+Prom':     dict(canc='TS', det='Prom', kw=dict(k=k_ts), mota='bo sung: TS + prominence (k=%.0f)' % k_ts),
        'supp_TS-PCA+Prom': dict(canc='TS-PCA%d' % pca_npc, det='Prom', kw=dict(k=k_pca), mota='bo sung: TS-PCA + prominence (k=%.0f)' % k_pca),
        'supp_MedLS+PT':    dict(canc='MedLS', det='PT', kw=dict(thr_frac=f_med), mota='bo sung: front-end cua nhom + Pan-Tompkins (thr_frac=%.3f)' % f_med),
        'supp_TS+PTexp':    dict(canc='TS', det='PTexp', kw=dict(thr_frac=f_ts_exp), mota='bo sung: TS + PT bien the goc trung binh mu (thr_frac=%.3f)' % f_ts_exp),
        'supp_TS-PCA+PTexp': dict(canc='TS-PCA%d' % pca_npc, det='PTexp', kw=dict(thr_frac=f_pca_exp), mota='bo sung: TS-PCA + PT bien the goc trung binh mu (thr_frac=%.3f)' % f_pca_exp),
    }
    DET = dict(PT=pan_tompkins_fetal, Prom=prominence_detector,
               PTexp=lambda r, **kw: pan_tompkins_fetal(r, est='exp', **kw))

    # ---- [4] cham 20 danh gia + kenh PSD mu nhan
    print('\n[4] cham 5 ban ghi x 4 kenh (20 danh gia) va kenh PSD mu nhan (5 danh gia)')
    results = {}
    for name, cf in configs.items():
        per = {}; psd = {}
        for rec in RECS:
            per[rec] = {}
            for ld in LEADS:
                det = DET[cf['det']](RES[rec][ld][cf['canc']], **cf['kw'])
                s = score(det, GT[rec]); s['n_det'] = int(len(det)); s['n_ref'] = int(len(GT[rec]))
                per[rec][ld] = s
            bl = int(pick_blind({ld: RES[rec][ld][cf['canc']] for ld in LEADS}))   # PSD tren phan du CUA baseline
            psd[rec] = dict(lead=bl, model_lead=model_psd_lead[rec], **per[rec][bl])
        rows20 = [per[r][l] for r in RECS for l in LEADS]
        rows16 = [per[r][l] for r in HELDOUT for l in LEADS]
        base20 = [per[r][l]['F1'] for r in RECS for l in LEADS]
        mod20 = [model_f1[r][l] for r in RECS for l in LEADS]
        base16 = [per[r][l]['F1'] for r in HELDOUT for l in LEADS]
        mod16 = [model_f1[r][l] for r in HELDOUT for l in LEADS]
        psd_rows = [psd[r] for r in RECS]
        # kenh PSD: (a) PSD tren phan du cua baseline; (b) cung kenh voi lua chon PSD cua mo hinh
        same_lead_rows = [per[r][model_psd_lead[r]] for r in RECS]
        results[name] = dict(
            mota=cf['mota'], canceller=cf['canc'], detector=cf['det'], params=cf['kw'],
            per_eval={r: {str(l): per[r][l] for l in LEADS} for r in RECS},
            macro_20=macro(rows20), macro_16_heldout=macro(rows16),
            psd_blind={r: psd[r] for r in RECS}, psd_macro_5=macro(psd_rows),
            psd_same_lead_as_model_macro_5=macro(same_lead_rows),
            wilcoxon_vs_model_20=wilcoxon_pair(base20, mod20),
            wilcoxon_vs_model_16_heldout=wilcoxon_pair(base16, mod16),
            wilcoxon_psd_vs_model_5=wilcoxon_pair([psd[r]['F1'] for r in RECS], [model_psd_f1[r] for r in RECS]),
        )

    # ---- in bang
    print('\n' + '-' * 96)
    print('F1 tung (ban ghi x kenh), %%  [mo hinh = all_leads.json]')
    print('-' * 96)
    hdr = '%-6s%-5s' % ('rec', 'kenh') + ''.join('%14s' % n for n in ['Mo hinh', 'TS', 'TS-PCA', 'Prominence'])
    print(hdr)
    for rec in RECS:
        for ld in LEADS:
            print('%-6s%-5d' % (rec, ld) + '%14.2f' % model_f1[rec][ld] + ''.join(
                '%14.2f' % results[n]['per_eval'][rec][str(ld)]['F1'] for n in ['TS', 'TS-PCA', 'Prominence']))
    print('-' * 96)
    print('%-11s%14.2f' % ('MACRO 20', model_macro4) + ''.join('%14.2f' % results[n]['macro_20']['F1_mean'] for n in ['TS', 'TS-PCA', 'Prominence']))
    print('%-11s%14.2f' % ('  +/- SD', model_macro4_sd) + ''.join('%14.2f' % results[n]['macro_20']['F1_sd'] for n in ['TS', 'TS-PCA', 'Prominence']))
    print('%-11s%14.2f' % ('HELD-OUT16', model_macro4_heldout) + ''.join('%14.2f' % results[n]['macro_16_heldout']['F1_mean'] for n in ['TS', 'TS-PCA', 'Prominence']))
    print('%-11s%14.2f' % ('PSD 5', model_macro_psd) + ''.join('%14.2f' % results[n]['psd_macro_5']['F1_mean'] for n in ['TS', 'TS-PCA', 'Prominence']))

    print('\n' + '-' * 96)
    print('TOM TAT (macro tren 20 danh gia; mo hinh 99,21 kenh PSD / 97,45 TB 4 kenh)')
    print('-' * 96)
    print('%-18s%16s%10s%10s%14s%12s%14s%12s' % ('baseline', 'F1 +/- SD', 'Se', 'PPV', 'F1 held-out16', 'F1 PSD(5)', 'Wilcoxon p2', 'p(base<mo)'))
    for n in ['TS', 'TS-PCA', 'Prominence', 'supp_TS+Prom', 'supp_TS-PCA+Prom', 'supp_MedLS+PT',
              'supp_TS+PTexp', 'supp_TS-PCA+PTexp']:
        r = results[n]; m = r['macro_20']; w = r['wilcoxon_vs_model_20']
        print('%-18s%8.2f +/- %5.2f%10.2f%10.2f%14.2f%12.2f%14.4g%12.4g' % (
            n, m['F1_mean'], m['F1_sd'], m['Se_mean'], m['PPV_mean'], r['macro_16_heldout']['F1_mean'],
            r['psd_macro_5']['F1_mean'], w['p_two_sided'], w['p_less']))
    print('%-18s%8.2f +/- %5.2f%10s%10s%14.2f%12.2f' % ('FetalQRS-TCN', model_macro4, model_macro4_sd, '-', '-',
                                                       model_macro4_heldout, model_macro_psd))
    for n in ['TS', 'TS-PCA', 'Prominence']:
        w = results[n]['wilcoxon_vs_model_20']; w16 = results[n]['wilcoxon_vs_model_16_heldout']
        print('  %-11s Wilcoxon n=20: W=%.1f p=%.4g (hieu TB %.2f, baseline thap hon o %d/20) | held-out n=16: W=%.1f p=%.4g'
              % (n, w['stat'], w['p_two_sided'], w['mean_diff'], w['n_base_lower'], w16['stat'], w16['p_two_sided']))
    print('\n  Kenh PSD mu nhan cua baseline (PSD tren phan du cua chinh no) so voi kenh PSD cua mo hinh:')
    for n in ['TS', 'TS-PCA', 'Prominence']:
        print('  %-11s ' % n + ' '.join('%s:L%d(mo hinh L%d)=%.2f' % (r, results[n]['psd_blind'][r]['lead'],
                                                                     model_psd_lead[r], results[n]['psd_blind'][r]['F1']) for r in RECS))

    elapsed = time.time() - t0
    out = dict(
        meta=dict(
            ngay=datetime.datetime.now().isoformat(timespec='seconds'), thoi_gian_chay_s=round(elapsed, 1),
            du_lieu='ADFECGDB (PhysioNet) 5 ban ghi x 4 kenh bung, 1000 Hz, nhan edf.qrs tu kenh Direct',
            giao_thuc='+/-%d ms, ghep 1-1 tham lam M.match_events, macro F1 = TB F1 tung (ban ghi x kenh)' % TOL_MS,
            front_end='M.preprocess: Butterworth bac 4 dai 10-60 Hz + notch 50 Hz, resample 250 Hz; M.detect_maternal_qrs',
            tuning='sieu tham so chon CHI tren %s (macro F1 4 kenh), ap nguyen cho %s; luoi co dinh truoc' % (TUNE_REC, HELDOUT),
            grid=dict(thr_frac=GRID_THR_FRAC, n_pc=GRID_NPC, k=GRID_K),
            pan_tompkins=('dao ham 5 diem, binh phuong, tich phan 60 ms, THR=NPK+frac*(SPK-NPK); SPK/NPK = trung vi 8 dinh gan nhat '
                          '(Hamilton-Tompkins 1986) [bien the CHINH] hoac trung binh mu 1/8 (Pan-Tompkins 1985) [bien the goc, phu]; '
                          'tro 250 ms; search-back 1.66*RR (RR = trung vi 8 RR hop ly 0.30-0.70 s, mac dinh 0.45 s) voi 0.5*THR; '
                          'vi tri = max|res| +/-40 ms'),
            kenh_mu_nhan='pick_blind() cua benchmark_dpss/blind_lead.py (PSD dinh 1,8-3,0 Hz) ap len phan du cua chinh baseline',
            mo_hinh='benchmark_dpss/all_leads.json (LORO, 4 kenh) va blind_lead.json (kenh PSD)',
            phien_ban=dict(python=sys.version.split()[0], numpy=np.__version__, scipy=__import__('scipy').__version__,
                           torch=torch.__version__, mne=mne.__version__, wfdb=wfdb.__version__),
            so_qrs_me={'%s_L%d' % (r, l): NMQ[(r, l)] for r in RECS for l in LEADS},
        ),
        model=dict(per_eval={r: {str(l): model_f1[r][l] for l in LEADS} for r in RECS},
                   macro_20_F1=model_macro4, macro_20_F1_sd=model_macro4_sd, macro_16_heldout_F1=model_macro4_heldout,
                   psd_lead=model_psd_lead, psd_F1=model_psd_f1, macro_psd_5_F1=model_macro_psd),
        tuning_r01=dict(chosen=dict(TS=dict(thr_frac=ts_frac), TS_PCA=dict(n_pc=pca_npc, thr_frac=pca_frac),
                                    Prominence=dict(k=prom_k)), grid_macroF1_r01=tuning),
        baselines={k: v for k, v in results.items() if not k.startswith('supp_')},
        supplementary_matrix={k: v for k, v in results.items() if k.startswith('supp_')},
    )
    json.dump(out, open(os.path.join(HERE, 'results.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('\nda ghi results.json va baselines_log.txt  (%.1f s)' % elapsed)


if __name__ == '__main__':
    main()
