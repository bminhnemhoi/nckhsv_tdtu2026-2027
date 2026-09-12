# -*- coding: utf-8 -*-
"""
clinical.py -- BO CHI SO LAM SANG cho RelyFetal (yeu cau cua phan bien P3, bac si san khoa).

Bac si khong nhin QRS. Ho nhin duong nhip tim thai, do dao dong ngan han (STV) va do phu tin hieu.
Bai hien chua do bat ky dai luong nao trong so do. File nay do 4 nhom:

  1. STV kieu Dawes-Redman   epoch 3,75 s (16 epoch/phut), trung binh RR trong epoch (ms),
                             STV = trung binh |chenh lech giua hai epoch lien tiep|.
                             Tinh tu (a) nhan chuan va (b) dau ra mo hinh -> chenh lech, tuong quan,
                             Bland-Altman (bias +- 1,96 SD). Nguong tham chieu TRUFFLE: STV < 2,6 ms
                             (< 29 tuan) hoac < 3,0 ms  [gia tri do phan bien P3 cung cap, CHUA kiem chung
                             trong phien nay -- xem CLINICAL.md muc "Nguon nguong"].
  2. Bland-Altman FHR        cua so 60 s KHONG chong lan; FHR = 60 / trung binh RR hop le trong cua so.
                             bias, gioi han dong thuan, % cua so lech > 5 bpm
                             (chi so "FHR precision" cua DPSS: ho bao 88,61 % tren ADFECGDB).
  3. Do phu THEO THOI GIAN   cong tu choi fsqi/gate.py che do 'hoc' -> p_bad tung doan 4 s -> xanh/vang/do.
                             % THOI LUONG duoc tra loi (khong phai % ban ghi) + phan bo do dai khoang trong
                             lien tuc bi tu choi (trung vi, p90, max, histogram).
  4. Khoa nham nhip me       ti le nhip "thai" mo hinh tra ve trung dinh R me (+/- 50 ms), tren TUNG ban ghi,
                             so voi (a) nguong ngau nhien giai tich 2*tol / RR_me va (b) phan phoi rong
                             mo phong bang dich vong tron 200 lan. Doi chung: cung chi so tinh tren NHAN CHUAN.

Chu the / checkpoint (khai bao TRUOC khi chay):
  PhysioNet r01,r04,r07,r08,r10   -> fetalqrs_tcn_fold_rXX.pt          (mo hinh n=5, LORO, ngoai mau)
  Silesia B1_01..10 + B2 (7 ban)  -> fetalqrs_tcn_22_fold_XX.pt        (fold GIU LAI dung chu the do -> ngoai mau)
                                     va fetalqrs_tcn_22_production.pt  (TRONG mau -- chi de doi chieu)
  CinC 2013 a01..a10              -> fetalqrs_tcn_22_production.pt     (zero-shot, ngoai mien)

Kenh: quy tac MU NHAN theo PSD (Power-MF, Jaeger 2024) tren ca ba tap. Rieng CinC bao cao them kenh 0 co dinh
      vi kenh 0 la lua chon HAU KIEM (xem SU THAT MOI NHAT / facts_phase2.json): so chinh cua CinC la PSD.

Chay:  python analysis/clinical.py            (mac dinh: 22 chu the + 10 ban CinC dau)
       python analysis/clinical.py --smoke    (1 ban ghi moi nhom, de kiem tra nhanh)
Ket qua: analysis/clinical_results.json, analysis/clinical_log.txt,
         analysis/clinical_stv_fhr.png, analysis/clinical_coverage_lock.png
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import json, time, argparse, importlib.util, datetime, platform, gc
import numpy as np
import torch
import mne, wfdb
from scipy import signal as sg
from scipy.stats import pearsonr, spearmanr

torch.set_num_threads(2)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
sys.path.insert(0, os.path.join(ROOT, 'fsqi'))
from _paths import adfecgdb_dir, cinc2013_dir, checkpoint


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


M = _load('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
CFG = M.CFG
L = _load('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))
import gate as FGATE

# ------------------------------------------------------------------ hang so khai bao truoc
FS = CFG['fs']                 # 250 Hz (tin hieu lam viec)
FS_IN = CFG['fs_in']           # 1000 Hz
Q = FS_IN // FS
TOL_S = 0.050                  # dung sai khop nhip / khoa me: 50 ms
EPOCH_S = 3.75                 # Dawes-Redman: 16 epoch / phut
RR_LO, RR_HI = 0.25, 0.75      # RR thai hop le: 80-240 bpm
MIN_RR_EPOCH = 2               # so RR toi thieu de mot epoch co gia tri
FHR_WIN_S = 60.0               # cua so Bland-Altman FHR
MIN_RR_FHR_WIN = 10            # so RR toi thieu trong cua so 60 s
FHR_PREC_TOL = 5.0             # +-5 bpm (dinh nghia "FHR precision" cua DPSS)
STV_THR = (2.6, 3.0)           # nguong TRUFFLE do P3 cung cap
SEG_S = 4.0                    # doan cua cong tu choi
N_PERM = 200                   # so lan dich vong tron cho nguong ngau nhien khoa me
FHR_BAND = (1.8, 3.0)          # dai PSD chon kenh mu nhan (Power-MF)
LEADS = (1, 2, 3, 4)

PHYSIONET = ['r01', 'r04', 'r07', 'r08', 'r10']
B1 = [f'B1_{i:02d}' for i in range(1, 11)]
B2 = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
CINC = [f'a{i:02d}' for i in range(1, 11)]
# fold 22 chu the giu lai chu the nao (benchmark_dpss/eval_22.json['folds'])
FOLD22 = {'B1_08': '01', 'B2_12': '01', 'B1_09': '02', 'r10': '02', 'B1_02': '03', 'B2_09': '03',
          'B1_06': '04', 'B2_04': '04', 'B1_04': '05', 'r01': '05', 'B1_05': '06', 'r04': '06',
          'B1_03': '07', 'B2_05': '07', 'B1_01': '08', 'r07': '08', 'B1_10': '09', 'B2_06': '09',
          'B1_07': '10', 'r08': '10', 'B2_08': '11', 'B2_03': '11'}

OUT_JSON = os.path.join(HERE, 'clinical_results.json')
OUT_LOG = os.path.join(HERE, 'clinical_log.txt')
FIG1 = os.path.join(HERE, 'clinical_stv_fhr.png')
FIG2 = os.path.join(HERE, 'clinical_coverage_lock.png')


class Tee:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.o = sys.stdout
    def write(self, s):
        self.o.write(s); self.f.write(s); self.f.flush()
    def flush(self):
        self.o.flush(); self.f.flush()


# ================================================================== 1. STV
def epoch_mean_rr_ms(peaks_s, dur_s, epoch_s=EPOCH_S):
    """Trung binh khoang RR (ms) trong tung epoch 3,75 s. NaN neu epoch co < MIN_RR_EPOCH khoang hop le."""
    t = np.sort(np.asarray(peaks_s, float))
    n_ep = int(np.floor(dur_s / epoch_s))
    out = np.full(max(n_ep, 0), np.nan)
    if len(t) < 2 or n_ep <= 0:
        return out
    rr = np.diff(t)
    mid = (t[:-1] + t[1:]) / 2.0
    ok = (rr >= RR_LO) & (rr <= RR_HI)
    rr, mid = rr[ok], mid[ok]
    if not len(rr):
        return out
    idx = np.floor(mid / epoch_s).astype(int)
    keep = (idx >= 0) & (idx < n_ep)
    rr, idx = rr[keep], idx[keep]
    cnt = np.bincount(idx, minlength=n_ep)
    ssum = np.bincount(idx, weights=rr, minlength=n_ep)
    good = cnt >= MIN_RR_EPOCH
    out[good] = ssum[good] / cnt[good] * 1000.0
    return out


def stv_from_epochs(m):
    """STV = trung binh |m[k+1] - m[k]| tren cac cap epoch LIEN TIEP deu hop le."""
    m = np.asarray(m, float)
    if len(m) < 2:
        return float('nan'), 0
    d = np.abs(np.diff(m))
    ok = np.isfinite(d)
    return (float(d[ok].mean()) if ok.any() else float('nan')), int(ok.sum())


def stv_pair(ref_s, det_s, dur_s):
    """STV nhan / STV mo hinh, ca hai bien the: DOC LAP (moi ben dung epoch hop le cua no) va GHEP CAP."""
    a = epoch_mean_rr_ms(ref_s, dur_s)
    b = epoch_mean_rr_ms(det_s, dur_s)
    sa, na = stv_from_epochs(a)
    sb, nb = stv_from_epochs(b)
    both = np.isfinite(a) & np.isfinite(b)
    ap = np.where(both, a, np.nan); bp = np.where(both, b, np.nan)
    spa, npa = stv_from_epochs(ap)
    spb, _ = stv_from_epochs(bp)
    return dict(stv_ref_ms=sa, stv_det_ms=sb, n_pairs_ref=na, n_pairs_det=nb,
                stv_ref_paired_ms=spa, stv_det_paired_ms=spb, n_pairs_paired=npa,
                n_epoch_total=int(len(a)), n_epoch_ref_valid=int(np.isfinite(a).sum()),
                n_epoch_det_valid=int(np.isfinite(b).sum()),
                epoch_valid_frac_det=float(np.isfinite(b).mean()) if len(b) else float('nan'))


# ================================================================== 2. FHR theo cua so 1 phut
def fhr_windows(peaks_s, dur_s, win_s=FHR_WIN_S, min_rr=None):
    """FHR trung binh (bpm) tung cua so khong chong lan; NaN neu it hon min_rr khoang RR hop le."""
    if min_rr is None:
        min_rr = MIN_RR_FHR_WIN if win_s >= FHR_WIN_S else max(3, int(round(0.34 * win_s * 2.3)))
    t = np.sort(np.asarray(peaks_s, float))
    n_w = int(np.floor(dur_s / win_s))
    out = np.full(max(n_w, 0), np.nan)
    if len(t) < 2 or n_w <= 0:
        return out
    rr = np.diff(t); mid = (t[:-1] + t[1:]) / 2.0
    ok = (rr >= RR_LO) & (rr <= RR_HI)
    rr, mid = rr[ok], mid[ok]
    if not len(rr):
        return out
    idx = np.floor(mid / win_s).astype(int)
    keep = (idx >= 0) & (idx < n_w)
    rr, idx = rr[keep], idx[keep]
    cnt = np.bincount(idx, minlength=n_w)
    ssum = np.bincount(idx, weights=rr, minlength=n_w)
    good = cnt >= min_rr
    out[good] = 60.0 / (ssum[good] / cnt[good])
    return out


FHR_WIN_SWEEP = (5.0, 10.0, 30.0, 60.0)


def fhr_precision_sweep(ref_s, det_s, dur_s):
    """"FHR precision" (% cua so lech <= 5 bpm) theo NHIEU do dai cua so.

    DPSS bao 88,61 % tren ADFECGDB nhung KHONG neu do dai cua so. Cua so cang dai cang de
    (60 s gop ~140 nhip), nen bao cao ca day de khong so khap khenh."""
    out = {}
    for w in FHR_WIN_SWEEP:
        if dur_s < w:
            continue
        fr = fhr_windows(ref_s, dur_s, w); fd = fhr_windows(det_s, dur_s, w)
        both = np.isfinite(fr) & np.isfinite(fd)
        dif = fd[both] - fr[both]
        nref = int(np.isfinite(fr).sum())
        out[f'{w:.0f}s'] = dict(
            n_win_total=int(len(fr)), n_win_ref_valid=nref, n_win_paired=int(both.sum()),
            bias_bpm=float(dif.mean()) if both.any() else float('nan'),
            mae_bpm=float(np.mean(np.abs(dif))) if both.any() else float('nan'),
            pct_within5_of_paired=float(np.mean(np.abs(dif) <= FHR_PREC_TOL) * 100) if both.any() else float('nan'),
            pct_within5_of_ref_valid=float(np.sum(np.abs(dif) <= FHR_PREC_TOL) / max(nref, 1) * 100),
            diff_bpm=[float(v) for v in dif])
    return out


# ================================================================== 4. khoa nham nhip me
def coincidence_frac(a_s, b_s, tol=TOL_S):
    """ti le phan tu cua a nam trong +-tol cua mot phan tu cua b."""
    a = np.sort(np.asarray(a_s, float)); b = np.sort(np.asarray(b_s, float))
    if not len(a) or not len(b):
        return float('nan')
    j = np.clip(np.searchsorted(b, a), 1, len(b) - 1)
    d = np.minimum(np.abs(a - b[j - 1]), np.abs(a - b[j]))
    return float(np.mean(d <= tol))


def null_coincidence(a_s, b_s, dur_s, n=N_PERM, seed=0, tol=TOL_S):
    """phan phoi rong: dich VONG TRON chuoi a mot luong ngau nhien -> giu nguyen cau truc RR ca hai ben."""
    a = np.asarray(a_s, float); b = np.asarray(b_s, float)
    if not len(a) or not len(b) or not np.isfinite(dur_s) or dur_s <= 0:
        return dict(mean=float('nan'), p95=float('nan'), sd=float('nan'), n=0)
    rng = np.random.default_rng(seed)
    vals = []
    for s in rng.uniform(0, dur_s, n):
        vals.append(coincidence_frac(np.mod(a + s, dur_s), b, tol))
    v = np.asarray(vals, float)
    return dict(mean=float(np.nanmean(v)), sd=float(np.nanstd(v, ddof=1)),
                p95=float(np.nanpercentile(v, 95)), n=int(n))


def analytic_chance(mat_s, tol=TOL_S):
    """neu nhip thai va me doc lap: ti le trung ky vong = 2*tol / RR_me (chan tren 1,0)."""
    m = np.sort(np.asarray(mat_s, float))
    if len(m) < 2:
        return float('nan'), float('nan')
    rr = np.diff(m); rr = rr[(rr > 0.3) & (rr < 1.6)]
    if not len(rr):
        return float('nan'), float('nan')
    rrm = float(np.median(rr))
    return float(min(1.0, 2 * tol / rrm)), rrm


# ================================================================== 3. do phu theo thoi gian
def run_lengths(mask):
    """do dai cac doan True lien tiep (don vi: so doan)."""
    m = np.asarray(mask, bool)
    if not m.any():
        return np.zeros(0, int)
    d = np.diff(np.concatenate([[0], m.view(np.int8), [0]]))
    st = np.where(d == 1)[0]; en = np.where(d == -1)[0]
    return (en - st).astype(int)


def coverage_stats(levels, seg_s=SEG_S):
    lv = np.asarray(levels)
    n = len(lv)
    if n == 0:
        return dict(n_seg=0)
    red = lv == 'do'; green = lv == 'xanh'
    g_red = run_lengths(red) * seg_s
    g_ng = run_lengths(~green) * seg_s
    def q(a, p):
        return float(np.percentile(a, p)) if len(a) else 0.0
    return dict(
        n_seg=int(n), duration_covered_s=float(n * seg_s),
        frac_green=float(green.mean()), frac_yellow=float((lv == 'vang').mean()), frac_red=float(red.mean()),
        # P1: tra loi tru doan DO
        cov_P1_pct=float((1 - red.mean()) * 100),
        gap_P1_n=int(len(g_red)), gap_P1_median_s=float(np.median(g_red)) if len(g_red) else 0.0,
        gap_P1_p90_s=q(g_red, 90), gap_P1_max_s=float(g_red.max()) if len(g_red) else 0.0,
        gap_P1_lengths_s=[float(v) for v in g_red],
        # P2: chi tra loi doan XANH
        cov_P2_pct=float(green.mean() * 100),
        gap_P2_n=int(len(g_ng)), gap_P2_median_s=float(np.median(g_ng)) if len(g_ng) else 0.0,
        gap_P2_p90_s=q(g_ng, 90), gap_P2_max_s=float(g_ng.max()) if len(g_ng) else 0.0,
        gap_P2_lengths_s=[float(v) for v in g_ng])


# ================================================================== nap du lieu
def psd_score(x250, fs=FS):
    e = np.abs(sg.hilbert(x250 - np.mean(x250))); e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def load_subject(tag):
    """-> dict(lead -> dict(raw1000, x250, res250, psd)), ref_s, mat_ref_s|None, meta"""
    meta = {}
    if tag.startswith('a'):                                       # CinC 2013 set-a
        D = cinc2013_dir()
        rec = wfdb.rdrecord(os.path.join(D, tag))
        ann = wfdb.rdann(os.path.join(D, tag), 'fqrs')
        fs0 = rec.fs
        ref_s = np.asarray(ann.sample, float) / fs0
        chans = {}
        for k in range(min(4, rec.p_signal.shape[1])):
            s = np.nan_to_num(rec.p_signal[:, k])
            if fs0 != FS_IN:
                s = sg.resample_poly(s, FS_IN, int(fs0))
            chans[k + 1] = s
        meta = dict(duration_s=float(rec.p_signal.shape[0] / fs0), dataset='CinC2013',
                    label='nhan fQRS chuyen gia (set-a)')
        mat_ref = None
        del rec
    elif tag.startswith('r'):                                      # ADFECGDB PhysioNet
        D = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        ref_s = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, float) / FS_IN
        chans = {l: sig[l] for l in LEADS}
        meta = dict(duration_s=float(sig.shape[1] / FS_IN), dataset='ADFECGDB',
                    label='DIRECT scalp FECG')
        mat_ref = None
        del raw, sig
    else:                                                          # Silesia
        sig, _, mt = L.load(tag)
        ref_s = np.asarray(mt['fqrs_all'], float) / FS_IN
        chans = {l: sig[l - 1] for l in LEADS}
        mat_ref = np.asarray(mt['mqrs'], float) / FS_IN
        meta = dict(duration_s=float(mt['duration_s']), dataset='Silesia-' + tag[:2],
                    label=mt['reference_source'], n_ref_flag0=int(mt['n_fqrs_flag0']))
        del sig
    out = {}
    for l in sorted(chans):
        x = M.preprocess(chans[l], FS_IN, CFG)
        r, _ = M.cancel_maternal(x, CFG)
        out[l] = dict(raw1000=np.asarray(chans[l], float), x250=x, res250=r, psd=psd_score(r))
    del chans
    return out, ref_s, mat_ref, meta


def load_net(path):
    b = torch.load(path, map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
    return net, float(b['threshold'])


def ckpt_for(tag):
    """(duong dan chinh - NGOAI MAU, duong dan phu - trong mau hoac None, nhan)"""
    if tag.startswith('a'):
        return checkpoint('fetalqrs_tcn_22_production.pt'), None, 'production_22 (zero-shot, ngoai mien)'
    if tag.startswith('r'):
        return checkpoint(f'fetalqrs_tcn_fold_{tag}.pt'), checkpoint('fetalqrs_tcn_22_production.pt'), \
               'fold_%s (n=5, LORO)' % tag
    return checkpoint(f'fetalqrs_tcn_22_fold_{FOLD22[tag]}.pt'), checkpoint('fetalqrs_tcn_22_production.pt'), \
           'fold_22_%s (giu lai %s)' % (FOLD22[tag], tag)


# ================================================================== mot ban ghi
def process(tag, do_secondary=True):
    t0 = time.perf_counter()
    prep, ref_s, mat_ref_s, meta = load_subject(tag)
    dur = meta['duration_s']
    leads = sorted(prep)
    psd_lead = max(leads, key=lambda l: prep[l]['psd'])
    main_ck, sec_ck, ck_label = ckpt_for(tag)

    # kenh bao cao: PSD mu nhan o moi tap; CinC bao cao them kenh 1 (= "kenh 0" 0-index) co dinh
    report_leads = {'psd': psd_lead}
    if tag.startswith('a'):
        report_leads['lead0'] = leads[0]

    net, thr = load_net(main_ck)
    res = dict(record=tag, dataset=meta['dataset'], duration_s=dur, label=meta['label'],
               psd_lead=int(psd_lead), checkpoint=os.path.basename(main_ck), checkpoint_note=ck_label,
               threshold=float(thr), n_ref=int(len(ref_s)),
               maternal_ref='Silesia mqrs (nhan)' if mat_ref_s is not None else 'M.detect_maternal_qrs (uoc luong)',
               leads={})

    for name, lead in report_leads.items():
        p = prep[lead]
        prob = M.probability_series(net, M.robust_scale(p['res250']).astype(np.float32),
                                    M.robust_scale(p['x250']).astype(np.float32), CFG)
        det250 = M.pick_peaks(prob, thr, CFG).astype(np.int64)
        det_s = det250 / FS
        d = dict(lead=int(lead), n_det=int(len(det250)))
        # do chinh xac dinh (de doi chieu voi cac bang F1 da co)
        d['match'] = M.match_events(det250 * Q, np.round(ref_s * FS_IN).astype(int), FS_IN, 50)
        # 1. STV
        d['stv'] = stv_pair(ref_s, det_s, dur)
        # 2. FHR cua so 60 s
        fr = fhr_windows(ref_s, dur); fd = fhr_windows(det_s, dur)
        both = np.isfinite(fr) & np.isfinite(fd)
        diff = fd[both] - fr[both]
        d['fhr'] = dict(n_win_total=int(len(fr)), n_win_ref_valid=int(np.isfinite(fr).sum()),
                        n_win_det_valid=int(np.isfinite(fd).sum()), n_win_paired=int(both.sum()),
                        ref_bpm=[float(v) for v in fr], det_bpm=[float(v) for v in fd],
                        diff_bpm=[float(v) for v in diff],
                        mae_bpm=float(np.mean(np.abs(diff))) if both.any() else float('nan'),
                        pct_within5_of_paired=float(np.mean(np.abs(diff) <= FHR_PREC_TOL) * 100) if both.any() else float('nan'),
                        pct_within5_of_ref_valid=float(np.sum(np.abs(diff) <= FHR_PREC_TOL) /
                                                       max(int(np.isfinite(fr).sum()), 1) * 100),
                        sweep=fhr_precision_sweep(ref_s, det_s, dur))
        # 3. do phu theo thoi gian (cong hoc)
        p_bad = FGATE.score_segments(p['res250'], p['x250'], prob, det250, raw1000=p['raw1000'],
                                     fs=FS, raw_fs=FS_IN)
        lv = FGATE.segment_levels(p_bad)
        cov = coverage_stats(lv)
        cov['mean_p_bad'] = float(np.mean(p_bad)) if len(p_bad) else float('nan')
        d['coverage'] = cov
        # 4. khoa me
        mat_det_s = M.detect_maternal_qrs(p['x250'], CFG) / FS
        mm = mat_ref_s if mat_ref_s is not None else mat_det_s
        ch, rrm = analytic_chance(mm)
        d['maternal'] = dict(
            n_mat=int(len(mm)), rr_mat_median_s=rrm, chance_analytic=ch,
            lock_model=coincidence_frac(det_s, mm), lock_reference=coincidence_frac(ref_s, mm),
            null_model=null_coincidence(det_s, mm, dur, seed=0),
            null_reference=null_coincidence(ref_s, mm, dur, seed=1),
            lock_model_vs_detected_mqrs=coincidence_frac(det_s, mat_det_s))
        rc = FGATE.record_confidence(p_bad, d['maternal']['lock_model'])
        d['record_confidence'] = dict(level=rc['level'], score=rc['score'], locked=rc['components']['locked'])
        cov['cov_P3_pct'] = 0.0 if rc['level'] == 'thap' else cov['cov_P1_pct']
        res['leads'][name] = d
        del prob, p_bad

    del net
    # phu: checkpoint trong mau / production, chi tren kenh PSD, chi STV + FHR
    if do_secondary and sec_ck and os.path.isfile(sec_ck):
        net2, thr2 = load_net(sec_ck)
        p = prep[psd_lead]
        prob = M.probability_series(net2, M.robust_scale(p['res250']).astype(np.float32),
                                    M.robust_scale(p['x250']).astype(np.float32), CFG)
        det250 = M.pick_peaks(prob, thr2, CFG).astype(np.int64)
        det_s = det250 / FS
        fr = fhr_windows(ref_s, dur); fd = fhr_windows(det_s, dur)
        both = np.isfinite(fr) & np.isfinite(fd)
        diff = fd[both] - fr[both]
        res['secondary'] = dict(checkpoint=os.path.basename(sec_ck),
                                note='production_22 (chu the nay CO trong tap huan luyen neu la Silesia/PhysioNet)',
                                threshold=float(thr2), n_det=int(len(det250)),
                                match=M.match_events(det250 * Q, np.round(ref_s * FS_IN).astype(int), FS_IN, 50),
                                stv=stv_pair(ref_s, det_s, dur),
                                fhr_mae_bpm=float(np.mean(np.abs(diff))) if both.any() else float('nan'),
                                fhr_pct_within5=float(np.mean(np.abs(diff) <= FHR_PREC_TOL) * 100) if both.any() else float('nan'))
        del net2, prob
    del prep
    gc.collect()
    res['seconds'] = float(time.perf_counter() - t0)
    return res


# ================================================================== tong hop
def ba(diff):
    """Bland-Altman: bias, SD, gioi han dong thuan."""
    d = np.asarray([v for v in diff if np.isfinite(v)], float)
    if len(d) < 2:
        return dict(n=int(len(d)), bias=float(d.mean()) if len(d) else float('nan'),
                    sd=float('nan'), loa_lo=float('nan'), loa_hi=float('nan'))
    b = float(d.mean()); s = float(d.std(ddof=1))
    return dict(n=int(len(d)), bias=b, sd=s, loa_lo=b - 1.96 * s, loa_hi=b + 1.96 * s)


def corr(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3:
        return dict(n=int(m.sum()), pearson_r=float('nan'), pearson_p=float('nan'),
                    spearman_rho=float('nan'), spearman_p=float('nan'))
    pr = pearsonr(a[m], b[m]); sp = spearmanr(a[m], b[m])
    return dict(n=int(m.sum()), pearson_r=float(pr[0]), pearson_p=float(pr[1]),
                spearman_rho=float(sp[0]), spearman_p=float(sp[1]))


def summarize(records):
    groups = {}
    for r in records:
        groups.setdefault(r['dataset'], []).append(r)
    groups['TAT_CA'] = list(records)
    out = {}
    for g, rs in groups.items():
        key = 'psd'
        sr = [r['leads'][key]['stv']['stv_ref_ms'] for r in rs]
        sd_ = [r['leads'][key]['stv']['stv_det_ms'] for r in rs]
        srp = [r['leads'][key]['stv']['stv_ref_paired_ms'] for r in rs]
        sdp = [r['leads'][key]['stv']['stv_det_paired_ms'] for r in rs]
        dstv = [b - a for a, b in zip(sr, sd_)]
        dstvp = [b - a for a, b in zip(srp, sdp)]
        allw = []
        for r in rs:
            allw += r['leads'][key]['fhr']['diff_bpm']
        nref = sum(r['leads'][key]['fhr']['n_win_ref_valid'] for r in rs)
        npair = sum(r['leads'][key]['fhr']['n_win_paired'] for r in rs)
        aw = np.asarray([v for v in allw if np.isfinite(v)], float)
        cov1 = [r['leads'][key]['coverage']['cov_P1_pct'] for r in rs]
        cov2 = [r['leads'][key]['coverage']['cov_P2_pct'] for r in rs]
        cov3 = [r['leads'][key]['coverage'].get('cov_P3_pct', np.nan) for r in rs]
        nseg = sum(r['leads'][key]['coverage']['n_seg'] for r in rs)
        nred = sum(int(round(r['leads'][key]['coverage']['frac_red'] * r['leads'][key]['coverage']['n_seg'])) for r in rs)
        ngreen = sum(int(round(r['leads'][key]['coverage']['frac_green'] * r['leads'][key]['coverage']['n_seg'])) for r in rs)
        gaps1 = sum([r['leads'][key]['coverage']['gap_P1_lengths_s'] for r in rs], [])
        gaps2 = sum([r['leads'][key]['coverage']['gap_P2_lengths_s'] for r in rs], [])
        lock = [r['leads'][key]['maternal']['lock_model'] for r in rs]
        lockref = [r['leads'][key]['maternal']['lock_reference'] for r in rs]
        excess = [a - b for a, b in zip(lock, lockref)]
        sweep = {}
        for w in FHR_WIN_SWEEP:
            k = f'{w:.0f}s'
            dd, nref = [], 0
            for r in rs:
                s = r['leads'][key]['fhr'].get('sweep', {}).get(k)
                if s:
                    dd += s['diff_bpm']; nref += s['n_win_ref_valid']
            dd = np.asarray([v for v in dd if np.isfinite(v)], float)
            if not len(dd):
                continue
            sweep[k] = dict(n_win_ref_valid=int(nref), n_win_paired=int(len(dd)),
                            bias_bpm=float(dd.mean()), mae_bpm=float(np.mean(np.abs(dd))),
                            pct_within5_of_paired=float(np.mean(np.abs(dd) <= FHR_PREC_TOL) * 100),
                            pct_within5_of_ref_valid=float(np.sum(np.abs(dd) <= FHR_PREC_TOL) / max(nref, 1) * 100),
                            ba=ba(dd))
        p95 = [r['leads'][key]['maternal']['null_model']['p95'] for r in rs]
        chance = [r['leads'][key]['maternal']['chance_analytic'] for r in rs]
        f1s = [r['leads'][key]['match']['F1'] for r in rs]
        out[g] = dict(
            n_records=len(rs),
            total_duration_s=float(sum(r['duration_s'] for r in rs)),
            F1_macro=float(np.mean(f1s)), F1_sd=float(np.std(f1s, ddof=1)) if len(f1s) > 1 else 0.0,
            stv_ref_mean=float(np.nanmean(sr)), stv_det_mean=float(np.nanmean(sd_)),
            stv_diff_mean=float(np.nanmean(dstv)), stv_abs_diff_mean=float(np.nanmean(np.abs(dstv))),
            stv_ba=ba(dstv), stv_corr=corr(sr, sd_),
            stv_paired_ba=ba(dstvp), stv_paired_corr=corr(srp, sdp),
            stv_ref_lt3=int(np.sum(np.asarray(sr, float) < 3.0)),
            stv_det_lt3=int(np.sum(np.asarray(sd_, float) < 3.0)),
            stv_ref_lt26=int(np.sum(np.asarray(sr, float) < 2.6)),
            stv_det_lt26=int(np.sum(np.asarray(sd_, float) < 2.6)),
            fhr_ba=ba(aw), fhr_n_win_ref_valid=int(nref), fhr_n_win_paired=int(npair),
            fhr_mae_bpm=float(np.mean(np.abs(aw))) if len(aw) else float('nan'),
            fhr_pct_within5_of_paired=float(np.mean(np.abs(aw) <= FHR_PREC_TOL) * 100) if len(aw) else float('nan'),
            fhr_pct_within5_of_ref_valid=float(np.sum(np.abs(aw) <= FHR_PREC_TOL) / max(nref, 1) * 100),
            cov_P1_time_pct=float(100.0 * (nseg - nred) / max(nseg, 1)),
            cov_P2_time_pct=float(100.0 * ngreen / max(nseg, 1)),
            cov_P1_record_mean_pct=float(np.mean(cov1)), cov_P2_record_mean_pct=float(np.mean(cov2)),
            cov_P3_record_mean_pct=float(np.nanmean(cov3)),
            n_seg_total=int(nseg), n_seg_red=int(nred), n_seg_green=int(ngreen),
            gap_P1=dict(n=len(gaps1), median_s=float(np.median(gaps1)) if gaps1 else 0.0,
                        p90_s=float(np.percentile(gaps1, 90)) if gaps1 else 0.0,
                        max_s=float(max(gaps1)) if gaps1 else 0.0,
                        total_s=float(sum(gaps1))),
            gap_P2=dict(n=len(gaps2), median_s=float(np.median(gaps2)) if gaps2 else 0.0,
                        p90_s=float(np.percentile(gaps2, 90)) if gaps2 else 0.0,
                        max_s=float(max(gaps2)) if gaps2 else 0.0,
                        total_s=float(sum(gaps2))),
            fhr_sweep=sweep,
            lock_model_mean=float(np.nanmean(lock)), lock_model_max=float(np.nanmax(lock)),
            lock_reference_mean=float(np.nanmean(lockref)),
            lock_excess_mean=float(np.nanmean(excess)), lock_excess_median=float(np.nanmedian(excess)),
            lock_excess_max=float(np.nanmax(excess)),
            n_excess_gt10pt=int(np.sum(np.asarray(excess, float) > 0.10)),
            chance_analytic_mean=float(np.nanmean(chance)),
            n_exceed_null_p95=int(np.sum([l > p for l, p in zip(lock, p95) if np.isfinite(l) and np.isfinite(p)])),
            n_exceed_gate60=int(np.sum(np.asarray(lock, float) >= 0.60)),
            records=[r['record'] for r in rs])
    return out


# ================================================================== hinh
def figures(records, summ):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    COL = {'ADFECGDB': '#1f77b4', 'Silesia-B1': '#2ca02c', 'Silesia-B2': '#ff7f0e', 'CinC2013': '#d62728'}
    ds = [r['dataset'] for r in records]
    sr = np.array([r['leads']['psd']['stv']['stv_ref_ms'] for r in records], float)
    sd_ = np.array([r['leads']['psd']['stv']['stv_det_ms'] for r in records], float)

    # ---- hinh 1: STV + FHR
    fig, ax = plt.subplots(1, 3, figsize=(15.5, 5.1))
    TOP = 20.0                                     # phong to vung lam sang; diem ngoai khung ve o mep
    ax[0].plot([0, TOP], [0, TOP], 'k--', lw=1, zorder=1, label='y = x')
    n_out = 0
    for g in dict.fromkeys(ds):
        m = np.array([d == g for d in ds])
        xs = np.clip(sr[m], 0, TOP); ys = np.clip(sd_[m], 0, TOP)
        off = (sd_[m] > TOP) | (sr[m] > TOP)
        n_out += int(off.sum())
        ax[0].scatter(xs[~off], ys[~off], s=42, alpha=.85, c=COL.get(g, 'gray'),
                      edgecolor='k', lw=.4, label=g, zorder=3)
        if off.any():
            ax[0].scatter(xs[off], ys[off], s=58, marker='^', alpha=.9, c=COL.get(g, 'gray'),
                          edgecolor='k', lw=.5, zorder=4)
    for t, c in zip(STV_THR, ('#999', '#555')):
        ax[0].axvline(t, color=c, lw=1, ls=':'); ax[0].axhline(t, color=c, lw=1, ls=':')
    ax[0].axvspan(0, 3.0, color='#c00', alpha=.07)
    ax[0].set_xlim(0, TOP); ax[0].set_ylim(0, TOP)
    ax[0].set_xlabel('STV tu nhan chuan (ms)'); ax[0].set_ylabel('STV tu mo hinh (ms)')
    ax[0].set_title('(a) STV Dawes-Redman, epoch 3,75 s\ncham: nguong TRUFFLE 2,6 / 3,0 ms; do = vung benh ly', fontsize=10)
    ax[0].annotate('%d diem vuot khung %.0f ms\n(STV mo hinh toi da %.1f ms)' % (n_out, TOP, np.nanmax(sd_)),
                   xy=(0.97, 0.03), xycoords='axes fraction', ha='right', va='bottom', fontsize=7, color='#c00')
    ax[0].legend(fontsize=7, loc='upper left')

    d = sd_ - sr; mvals = (sd_ + sr) / 2
    b = summ['TAT_CA']['stv_ba']
    for g in dict.fromkeys(ds):
        m = np.array([x == g for x in ds])
        ax[1].scatter(mvals[m], d[m], s=42, alpha=.85, c=COL.get(g, 'gray'), edgecolor='k', lw=.4, zorder=3)
    ax[1].axhline(b['bias'], color='#c00', lw=1.4, label=f"bias {b['bias']:+.2f} ms")
    ax[1].axhline(b['loa_lo'], color='#c00', lw=1, ls='--', label=f"LoA [{b['loa_lo']:.2f}; {b['loa_hi']:.2f}]")
    ax[1].axhline(b['loa_hi'], color='#c00', lw=1, ls='--')
    ax[1].axhline(0, color='k', lw=.7)
    ax[1].axhspan(-0.4, 0.4, color='#3a3', alpha=.12)
    ax[1].set_xlabel('trung binh STV (nhan, mo hinh) (ms)'); ax[1].set_ylabel('mo hinh - nhan (ms)')
    ax[1].set_title('(b) Bland-Altman STV (n = %d ban ghi)\nvung xanh = +-0,4 ms = do phan giai can de tach 2,6 voi 3,0 ms' % b['n'],
                    fontsize=9.5)
    ax[1].legend(fontsize=7)

    allw, allm = [], []
    for r in records:
        f = r['leads']['psd']['fhr']
        fr = np.asarray(f['ref_bpm'], float); fd = np.asarray(f['det_bpm'], float)
        mk = np.isfinite(fr) & np.isfinite(fd)
        allw += list(fd[mk] - fr[mk]); allm += list((fd[mk] + fr[mk]) / 2)
    allw = np.asarray(allw); allm = np.asarray(allm)
    bf = summ['TAT_CA']['fhr_ba']
    ax[2].scatter(allm, allw, s=16, alpha=.5, c='#444', edgecolor='none')
    ax[2].axhline(bf['bias'], color='#c00', lw=1.4, label=f"bias {bf['bias']:+.2f} bpm")
    ax[2].axhline(bf['loa_lo'], color='#c00', lw=1, ls='--',
                  label=f"LoA [{bf['loa_lo']:.2f}; {bf['loa_hi']:.2f}]")
    ax[2].axhline(bf['loa_hi'], color='#c00', lw=1, ls='--')
    ax[2].axhspan(-5, 5, color='#3a3', alpha=.12, label='+-5 bpm (FHR precision)')
    ax[2].set_xlabel('FHR trung binh cua so (bpm)'); ax[2].set_ylabel('mo hinh - nhan (bpm)')
    ax[2].set_title('(c) Bland-Altman FHR, cua so 60 s (n = %d)\n%.1f%% trong +-5 bpm'
                    % (bf['n'], summ['TAT_CA']['fhr_pct_within5_of_paired']), fontsize=10)
    ax[2].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(FIG1, dpi=150); plt.close(fig)

    # ---- hinh 2: do phu + khoa me
    fig, ax = plt.subplots(1, 3, figsize=(15.5, 5.4))
    names = [r['record'] for r in records]
    c1 = np.array([r['leads']['psd']['coverage']['cov_P1_pct'] for r in records])
    c2 = np.array([r['leads']['psd']['coverage']['cov_P2_pct'] for r in records])
    o = np.arange(len(names))
    ax[0].barh(o, c1, color='#9ecae1', label='P1: tra loi tru doan DO')
    ax[0].barh(o, c2, height=.5, color='#2171b5', label='P2: chi doan XANH')
    ax[0].set_yticks(o); ax[0].set_yticklabels(names, fontsize=6)
    ax[0].invert_yaxis()
    ax[0].axvline(95, color='#3a3', lw=1.2, ls='--', label='CTG Doppler: mat 5 %')
    ax[0].axvline(80, color='#c00', lw=1.2, ls='--', label='nguong "mat tin hieu cao" 20 %')
    ax[0].set_xlabel('% THOI LUONG duoc tra loi'); ax[0].set_xlim(0, 100)
    ax[0].set_title('(a) Do phu theo thoi gian, tung ban ghi', fontsize=10)
    ax[0].legend(fontsize=6.5, loc='upper center', bbox_to_anchor=(0.5, -0.10), ncol=2)

    g1 = sum([r['leads']['psd']['coverage']['gap_P1_lengths_s'] for r in records], [])
    g2 = sum([r['leads']['psd']['coverage']['gap_P2_lengths_s'] for r in records], [])
    XMAX = 120.0
    bins = np.arange(0, XMAX + 8, 4)
    ax[1].hist([np.clip(g1, 0, XMAX), np.clip(g2, 0, XMAX)], bins=bins,
               color=['#9ecae1', '#2171b5'], label=['P1 (doan do)', 'P2 (khong xanh)'])
    ax[1].set_yscale('log'); ax[1].set_xlim(0, XMAX + 8)
    ax[1].axvline(90, color='#c00', lw=1.1, ls='--')
    ax[1].annotate('90 s = do dai mot nhip giam keo dai;\nkhoang trong dai hon co the giau tron mot con giam',
                   xy=(90, ax[1].get_ylim()[1]), xytext=(-4, -6), textcoords='offset points',
                   ha='right', va='top', fontsize=6.5, color='#c00')
    ax[1].annotate('%d khoang P1 va %d khoang P2 > %.0f s\n(gop vao cot cuoi; max P1 %.0f s, P2 %.0f s)'
                   % (sum(1 for v in g1 if v > XMAX), sum(1 for v in g2 if v > XMAX), XMAX,
                      max(g1) if g1 else 0, max(g2) if g2 else 0),
                   xy=(0.97, 0.72), xycoords='axes fraction', ha='right', fontsize=6.5)
    ax[1].set_xlabel('do dai khoang trong lien tuc (s)'); ax[1].set_ylabel('so khoang (thang log)')
    s1 = summ['TAT_CA']['gap_P1']; s2 = summ['TAT_CA']['gap_P2']
    ax[1].set_title('(b) Phan bo khoang trong bi tu choi\nP1: trung vi %.0f s, p90 %.0f s, max %.0f s | P2: %.0f / %.0f / %.0f s'
                    % (s1['median_s'], s1['p90_s'], s1['max_s'], s2['median_s'], s2['p90_s'], s2['max_s']), fontsize=9)
    ax[1].legend(fontsize=7)

    lk = np.array([r['leads']['psd']['maternal']['lock_model'] for r in records]) * 100
    lr = np.array([r['leads']['psd']['maternal']['lock_reference'] for r in records]) * 100
    p95 = np.array([r['leads']['psd']['maternal']['null_model']['p95'] for r in records]) * 100
    ax[2].barh(o, lk, color='#fdae6b', label='mo hinh')
    ax[2].plot(lr, o, 'o', ms=4, color='#31a354', label='nhan chuan (doi chung)')
    ax[2].plot(p95, o, '|', ms=11, color='k', mew=1.4, label='p95 phan phoi rong (dich vong tron)')
    ax[2].set_yticks(o); ax[2].set_yticklabels(names, fontsize=6); ax[2].invert_yaxis()
    ax[2].axvline(60, color='#c00', lw=1.2, ls='--', label='nguong cong 60 %')
    ax[2].set_xlabel('% nhip "thai" trung dinh R me (+-50 ms)')
    ax[2].set_xlim(0, 100)
    ax[2].set_title('(c) Khoa nham nhip me\n(chi doc duoc khi so sanh voi cham xanh = mac nen cua chinh ban ghi)', fontsize=9.5)
    ax[2].legend(fontsize=6.5, loc='upper center', bbox_to_anchor=(0.5, -0.10), ncol=2)
    fig.tight_layout(); fig.savefig(FIG2, dpi=150); plt.close(fig)


# ================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--no-secondary', action='store_true')
    ap.add_argument('--figures-only', action='store_true',
                    help='ve lai 2 hinh tu clinical_results.json da co, khong chay lai mo hinh')
    a = ap.parse_args()
    if a.figures_only:
        o = json.load(open(OUT_JSON, encoding='utf-8'))
        figures(o['records'], o['summary'])
        print(f'da ve lai {FIG1}\nda ve lai {FIG2}')
        return
    tags = (['r01', 'B1_01', 'B2_03', 'a01'] if a.smoke else PHYSIONET + B2 + B1 + CINC)
    sys.stdout = Tee(OUT_LOG)
    t0 = time.perf_counter()
    print('=' * 108)
    print('BO CHI SO LAM SANG -- RelyFetal (yeu cau P3)')
    print('=' * 108)
    print(f'ngay {datetime.datetime.now()}   torch {torch.__version__}  threads 2  may {platform.processor()}')
    print(f'epoch STV {EPOCH_S} s | cua so FHR {FHR_WIN_S} s | dung sai khop {TOL_S*1000:.0f} ms | '
          f'RR hop le {RR_LO}-{RR_HI} s | doan cong {SEG_S} s | {N_PERM} lan dich vong tron')
    print(f'{len(tags)} ban ghi: {", ".join(tags)}')
    print('-' * 108)
    print(f'{"ban ghi":<8}{"tap":<12}{"s":>7}{"kenh":>5}{"F1":>7}{"STVnhan":>9}{"STVmh":>8}{"dSTV":>7}'
          f'{"MAEfhr":>8}{"<5bpm%":>8}{"covP1%":>8}{"covP2%":>8}{"khoaMe%":>9}{"rong%":>7}{"giay":>7}')
    recs = []
    for tg in tags:
        try:
            r = process(tg, do_secondary=not a.no_secondary)
        except Exception as ex:
            print(f'{tg:<8} LOI: {type(ex).__name__}: {ex}')
            continue
        d = r['leads']['psd']
        print(f'{r["record"]:<8}{r["dataset"]:<12}{r["duration_s"]:>7.0f}{d["lead"]:>5}{d["match"]["F1"]:>7.2f}'
              f'{d["stv"]["stv_ref_ms"]:>9.2f}{d["stv"]["stv_det_ms"]:>8.2f}'
              f'{d["stv"]["stv_det_ms"]-d["stv"]["stv_ref_ms"]:>7.2f}'
              f'{d["fhr"]["mae_bpm"]:>8.2f}{d["fhr"]["pct_within5_of_paired"]:>8.1f}'
              f'{d["coverage"]["cov_P1_pct"]:>8.1f}{d["coverage"]["cov_P2_pct"]:>8.1f}'
              f'{d["maternal"]["lock_model"]*100:>9.1f}{d["maternal"]["null_model"]["p95"]*100:>7.1f}'
              f'{r["seconds"]:>7.1f}')
        recs.append(r)
    summ = summarize(recs)
    print('-' * 108)
    for g in ('ADFECGDB', 'Silesia-B2', 'Silesia-B1', 'CinC2013', 'TAT_CA'):
        if g not in summ:
            continue
        s = summ[g]
        print(f'{g:<20} n={s["n_records"]:<3} F1 {s["F1_macro"]:6.2f} | STV nhan {s["stv_ref_mean"]:5.2f} '
              f'mh {s["stv_det_mean"]:5.2f} bias {s["stv_ba"]["bias"]:+5.2f} '
              f'LoA [{s["stv_ba"]["loa_lo"]:+6.2f};{s["stv_ba"]["loa_hi"]:+6.2f}] r={s["stv_corr"]["pearson_r"]:.3f} | '
              f'FHR bias {s["fhr_ba"]["bias"]:+5.2f} LoA [{s["fhr_ba"]["loa_lo"]:+6.2f};{s["fhr_ba"]["loa_hi"]:+6.2f}] '
              f'{s["fhr_pct_within5_of_paired"]:5.1f}% | phu P1 {s["cov_P1_time_pct"]:5.1f}% P2 {s["cov_P2_time_pct"]:5.1f}% | '
              f'khoa me TB {s["lock_model_mean"]*100:4.1f}% (nhan {s["lock_reference_mean"]*100:4.1f}%) vuot rong {s["n_exceed_null_p95"]}')
    out = dict(meta=dict(
        date=str(datetime.datetime.now()), torch=torch.__version__, threads=2,
        epoch_s=EPOCH_S, fhr_win_s=FHR_WIN_S, tol_ms=TOL_S * 1000, rr_lo_s=RR_LO, rr_hi_s=RR_HI,
        min_rr_epoch=MIN_RR_EPOCH, min_rr_fhr_win=MIN_RR_FHR_WIN, seg_s=SEG_S, n_perm=N_PERM,
        stv_thresholds_ms=list(STV_THR),
        threshold_source='TRUFFLE, do phan bien P3 cung cap; CHUA kiem chung ban goc trong phien nay',
        channel_rule='PSD mu nhan (Power-MF, Jaeger 2024); CinC bao cao them kenh 0 co dinh',
        gate='fsqi/gate.py che do hoc (GBM 12 chi so co dien, 4 s/doan)',
        coverage_policies=dict(P1='tra loi tru doan DO', P2='chi tra loi doan XANH',
                               P3='P1 nhung 0 % neu record_confidence = thap'),
        minutes=float((time.perf_counter() - t0) / 60)),
        records=recs, summary=summ)
    json.dump(out, open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1,
              default=lambda o: None if isinstance(o, float) and not np.isfinite(o) else float(o))
    try:
        figures(recs, summ)
        print(f'\nda ghi {FIG1}\nda ghi {FIG2}')
    except Exception as ex:
        print(f'\nLOI ve hinh: {type(ex).__name__}: {ex}')
    print(f'da ghi {OUT_JSON}   tong {(time.perf_counter()-t0)/60:.1f} phut')


if __name__ == '__main__':
    main()
