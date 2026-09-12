# -*- coding: utf-8 -*-
"""
luongcuc_feat.py -- E1 cau hoi 1: do cac dai luong tin hieu tren 22 chu the,
tren DUNG kenh PSD mu nhan ma eval_22.json da chon.

Moi dai luong deu duoc ghi nhan la "dung nhan" hay "khong dung nhan".
Ket qua: analysis/luongcuc_feat.json
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, importlib.util
import numpy as np, mne, wfdb
from scipy import signal as sg

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
from _paths import adfecgdb_dir


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


M = _load('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py')); CFG = M.CFG
L = _load('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))
FS = CFG['fs']; FS_IN = CFG['fs_in']; Q = FS_IN // FS
EVAL22 = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json'), encoding='utf-8'))
LEADS = (1, 2, 3, 4)


def group_of(tag):
    return 'PhysioNet' if tag.startswith('r') else tag[:2]


def load_lead(tag, lead):
    g = group_of(tag)
    if g == 'PhysioNet':
        D = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
        sig = raw.get_data(); x = np.asarray(sig[lead], float)
        fq = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, int)
        dur = float(sig.shape[1] / 1000.0); del raw, sig
    else:
        sig, _, mt = L.load(tag)
        x = np.asarray(sig[lead - 1], float); fq = np.asarray(mt['fqrs_all'], int)
        dur = float(mt['duration_s']); del sig
    return x, fq, dur


def peak_amp(x, idx, rad):
    """bien do dinh-dinh trong cua so +/- rad mau quanh moi vi tri"""
    out = []
    for p in idx:
        s, t = max(0, p - rad), min(len(x), p + rad)
        if t - s > 2:
            out.append(float(np.ptp(x[s:t])))
    return np.asarray(out)


def bandpow(x, fs, lo, hi):
    f, P = sg.welch(x, fs=fs, nperseg=min(len(x), 8192))
    m = (f >= lo) & (f <= hi)
    return float(np.trapezoid(P[m], f[m])) if m.sum() > 1 else 0.0


def run(tag):
    t0 = time.time()
    e = EVAL22['subjects'][tag]; lead = int(e['psd_lead'])
    raw1000, fq1000, dur = load_lead(tag, lead)
    x250 = M.preprocess(raw1000, FS_IN, CFG)
    res250, mpk250 = M.cancel_maternal(x250, CFG)
    fq250 = np.clip((fq1000 // Q).astype(int), 0, len(res250) - 1)
    rad = int(0.04 * FS)  # +/- 40 ms

    # --- 1. bien do phuc bo (dinh-dinh trong +/-40 ms) ---
    a_f_res = peak_amp(res250, fq250, rad)          # thai, sau khu me            [DUNG NHAN]
    a_m_x = peak_amp(x250, mpk250, rad)             # me, truoc khu me            [khong nhan]
    a_m_res = peak_amp(res250, mpk250, rad)         # me con lai sau khu me       [khong nhan]
    A_f = float(np.median(a_f_res)) if len(a_f_res) else float('nan')
    A_m = float(np.median(a_m_x)) if len(a_m_x) else float('nan')
    A_m_res = float(np.median(a_m_res)) if len(a_m_res) else float('nan')

    # --- 2. nen: mau cach MOI nhip thai va MOI nhip me >= 120 ms ---
    mask = np.ones(len(res250), bool); g = int(0.12 * FS)
    allp = np.concatenate([fq250, mpk250]) if len(mpk250) else fq250
    for p in allp:
        mask[max(0, int(p) - g):min(len(res250), int(p) + g)] = False
    bg = res250[mask]
    N_rms = float(1.4826 * np.median(np.abs(bg - np.median(bg)))) if len(bg) > 100 else float('nan')

    fsnr_db = float(20 * np.log10(A_f / (2 * N_rms))) if N_rms > 0 else float('nan')
    mf_ratio_db = float(20 * np.log10(A_m / A_f)) if A_f > 0 else float('nan')
    resid_m_frac = float(A_m_res / A_m) if A_m > 0 else float('nan')
    fsnr_vs_resid_db = float(20 * np.log10(A_f / A_m_res)) if A_m_res > 0 else float('nan')

    # --- 3. chong lan nhip me-con ---
    ms = np.sort(mpk250.astype(float))
    if len(ms) > 1 and len(fq250):
        j = np.clip(np.searchsorted(ms, fq250), 1, len(ms) - 1)
        dd = np.minimum(np.abs(fq250 - ms[j - 1]), np.abs(fq250 - ms[j])) / FS
        overlap100 = float(np.mean(dd <= 0.100))
    else:
        overlap100 = float('nan')
    rr_m = np.diff(ms) / FS
    mhr = float(60.0 / np.median(rr_m)) if len(rr_m) else float('nan')
    overlap_exp = float(min(1.0, 0.200 / np.median(rr_m))) if len(rr_m) else float('nan')
    overlap_excess = overlap100 - overlap_exp

    # --- 4. FHR va bien thien RR cua NHAN ---
    rr = np.diff(np.sort(fq1000)) / FS_IN
    rr = rr[(rr > 0.25) & (rr < 1.0)]
    fhr = float(60.0 / np.median(rr)) if len(rr) else float('nan')
    rr_sd_ms = float(1000 * np.std(rr)) if len(rr) else float('nan')
    rr_cv = float(np.std(rr) / np.mean(rr)) if len(rr) else float('nan')

    # --- 5. nhieu 50 Hz va troi duong nen tren TIN HIEU THO ---
    p50 = bandpow(raw1000, FS_IN, 49, 51); p4060 = bandpow(raw1000, FS_IN, 40, 60)
    p_tot = bandpow(raw1000, FS_IN, 0.05, 100); p_drift = bandpow(raw1000, FS_IN, 0.05, 1.0)
    hum_frac = float(p50 / p4060) if p4060 > 0 else float('nan')
    drift_frac = float(p_drift / p_tot) if p_tot > 0 else float('nan')

    out = dict(record=tag, group=group_of(tag), psd_lead=lead, duration_s=dur, n_ref=int(len(fq1000)),
               n_mqrs=int(len(mpk250)),
               A_fetal_res=A_f, A_maternal_raw=A_m, A_maternal_res=A_m_res, bg_rms=N_rms,
               fsnr_db=fsnr_db, mf_ratio_db=mf_ratio_db, resid_m_frac=resid_m_frac,
               fsnr_vs_resid_db=fsnr_vs_resid_db,
               overlap100=overlap100, overlap_exp=overlap_exp, overlap_excess=overlap_excess,
               mhr_bpm=mhr, fhr_bpm=fhr, rr_sd_ms=rr_sd_ms, rr_cv=rr_cv,
               hum50_frac=hum_frac, drift_frac=drift_frac, runtime_s=time.time() - t0)
    print('%-6s L%d fSNR %6.2f dB  m/f %6.2f dB  resid_m %.3f  ovl %.3f (exp %.3f)  FHR %5.1f  hum %6.2f drift %.3f  %4.1fs'
          % (tag, lead, fsnr_db, mf_ratio_db, resid_m_frac, overlap100, overlap_exp, fhr, hum_frac, drift_frac,
             time.time() - t0), flush=True)
    return out


DINH_NGHIA = {
    'fsnr_db': 'DUNG NHAN. 20log10( (bien do dinh-dinh trung vi cua phuc bo thai tren tin hieu da khu me, cua so +/-40 ms quanh NHAN) / 2 / (RMS nen) ). Nen = cac mau cach moi nhip thai VA moi nhip me >= 120 ms; RMS uoc luong robust bang 1,4826*MAD.',
    'mf_ratio_db': 'DUNG NHAN cho mau so thai. 20log10( bien do me tren tin hieu TRUOC khu me / bien do thai sau khu me ). Cang lon = me cang lan at con.',
    'resid_m_frac': 'KHONG DUNG NHAN. Bien do me CON LAI sau khu me chia bien do me ban dau (trung vi tren cac nhip me tu dong phat hien). Do truc tiep chat luong khu me.',
    'fsnr_vs_resid_db': 'DUNG NHAN. 20log10(bien do thai / bien do me con lai). Am = tan du me lon hon phuc bo thai.',
    'overlap100': 'DUNG NHAN. Ti le nhip thai (nhan) nam trong +/-100 ms quanh mot nhip me tu dong phat hien.',
    'overlap_exp': 'KHONG DUNG NHAN. Ky vong neu nhip thai roi doc lap deu: 0,200 s / RR_me trung vi.',
    'overlap_excess': 'overlap100 - overlap_exp.',
    'fhr_bpm': 'DUNG NHAN. 60 / trung vi RR cua nhan (chi giu RR trong 0,25-1,0 s).',
    'rr_sd_ms': 'DUNG NHAN. Do lech chuan RR cua nhan, ms.',
    'rr_cv': 'DUNG NHAN. He so bien thien RR cua nhan.',
    'hum50_frac': 'KHONG DUNG NHAN. Cong suat 49-51 Hz chia cong suat 40-60 Hz tren tin hieu THO (truoc loc/notch).',
    'drift_frac': 'KHONG DUNG NHAN. Cong suat 0,05-1 Hz chia cong suat 0,05-100 Hz tren tin hieu THO.',
    'ghi_chu_nhip_me': 'Nhip me duoc phat hien bang model.detect_maternal_qrs (dai 8-25 Hz), khong dung nhan me cua bo du lieu, de dong nhat giua ADFECGDB (khong co nhan me) va Silesia.',
    'tuan_thai': 'KHONG CO trong sieu du lieu may doc duoc cua ca hai bo -> khong do duoc.',
}

if __name__ == '__main__':
    tags = sorted(EVAL22['subjects'])
    rows = [run(t) for t in tags]
    meta = dict(date=time.strftime('%Y-%m-%d %H:%M:%S'), n=len(rows), fs=FS, fs_in=FS_IN,
                band=list(CFG['band']), dinh_nghia=DINH_NGHIA)
    json.dump(dict(meta=meta, rows=rows),
              open(os.path.join(HERE, 'luongcuc_feat.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('-> analysis/luongcuc_feat.json')
