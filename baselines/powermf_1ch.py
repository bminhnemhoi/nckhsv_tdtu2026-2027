# -*- coding: utf-8 -*-
"""A2 PHAN 2 -- Power-MF-1ch: cai lai bo do cua Power-MF (Jaeger 2024) o che do DON KENH,
thuan Python/scipy, theo dac ta 21 buoc trong survey/scout_baselines.md muc 3.

Muc dich: so sanh CONG BANG. Power-MF goc dung 4 dao trinh bung + 2 lan ICA; RelyFetal
dung 1 dao trinh. Bien the nay giu DUNG phan dong gop rieng cua Jaeger 2024
(bao hinh dao ham -> mau trung vi -> bo loc phoi hop) nhung chay tren CUNG mot dao trinh,
CUNG front-end va CUNG bo khu me voi RelyFetal.

Anh xa (muc 3.3 cua scout_baselines.md):
  b1-3  tien xu ly Varanini   -> M.preprocess cua nhom (10-60 Hz + notch 50 Hz, ve 250 Hz)
  b4    FecgICAm              -> BO (can da kenh)
  b5    FecgInterp x4         -> GIU (sg.resample, noi suy Fourier nhu interpft)
  b6-7  do + khu QRS me       -> M.cancel_maternal cua nhom (mau trung vi + ti le BPTT tung nhip)
  b8    FecgICAf              -> BO (can da kenh)
  b9    z-score               -> GIU
  b10-11 bao hinh dao ham     -> GIU NGUYEN (nu, nz, Butterworth bac 1 0,7-8 Hz)
  b12-13 chon kenh bang PSD   -> quy tac kenh mu nhan cua nhom (psd_score), CUNG quy tac
                                 dung cho RelyFetal trong benchmark_dpss
  b14-21 bo loc phoi hop      -> GIU NGUYEN

Hai chi tiet de sai da cai dung (muc 3.2):
  - sig (dung cho mau va bo loc phoi hop) duoc chup TRUOC z-score
  - mau bi lan 2 hang 0 do MATLAB gan tu j=3 (loi cua tac gia). Cai ca hai che do:
    faithful=True tai lap nguyen ven, faithful=False bo 2 hang 0. Bao cao ca hai.
  - gausswin(N) cua MATLAB = gaussian(N, std=(N-1)/5)

Cham diem: M.match_events +/-50 ms, ghep tham lam 1-1 -- CUNG bo cham voi moi so khac.

Chay:
  python baselines/powermf_1ch.py --sets s22 cinc
Xuat: baselines/powermf_1ch.json, baselines/powermf_1ch_log.txt
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')

import argparse
import datetime
import importlib.util
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from scipy import signal as sg
from scipy.io import loadmat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'baselines')
WORK = os.path.join(HERE, 'powermf_work')
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
sys.path.insert(0, os.path.join(ROOT, 'model'))
from _paths import cinc2013_dir  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    'fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)
CFG = M.CFG

FS250 = CFG['fs']            # 250 Hz sau front-end
UP = 4                       # noi suy x4 cua Power-MF -> 1000 Hz noi bo
FS_INT = FS250 * UP          # 1000 Hz
TOL_MS = CFG['tolerance_ms']
FHR_BAND = (1.5, 3.5)

LOG = os.path.join(HERE, 'powermf_1ch_log.txt')
OUT = os.path.join(HERE, 'powermf_1ch.json')

S22 = (['r01', 'r04', 'r07', 'r08', 'r10']
       + ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
       + ['B1_%02d' % i for i in range(1, 11)])
BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')

_t0 = time.time()


def log(msg):
    line = '[%6.1fs] %s' % (time.time() - _t0, msg)
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def psd_score(x250, fs=FS250):
    """Quy tac kenh mu nhan cua nhom (benchmark_dpss/blind_lead.py, dung nguyen van)."""
    e = np.abs(sg.hilbert(x250 - np.mean(x250)))
    e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def matched_filter(x, template):
    """Ban Python cua helper/matched_filter.m:
       N=len(x); L=len(t); w=floor(L/2); t=t[::-1]; r=filter(t,1,[x,zeros(w-1)]); r=r[w:N+w-1]"""
    x = np.asarray(x, float)
    t = np.asarray(template, float)[::-1]
    N, L = len(x), len(t)
    w = L // 2
    y = sg.lfilter(t, 1.0, np.concatenate([x, np.zeros(max(0, w - 1))]))
    # MATLAB r(w : N+w-1) la 1-based, gom ca hai dau -> Python y[w-1 : N+w-1]
    lo = max(0, w - 1)
    return y[lo:lo + N]


def powermf_1ch_detect(res250, ms=340.0, faithful=True):
    """res250: phan du DON KENH sau khu me, @250 Hz.
       -> chi so mau @1000 Hz (fs goc cua nhan tham chieu)."""
    n = len(res250)
    # b5: noi suy Fourier x4 (tuong duong interpft)
    sig = sg.resample(np.asarray(res250, float), n * UP)
    fs = float(FS_INT)

    # b9: z-score -- LUU Y sig duoc giu NGUYEN (chua z-score) cho mau + bo loc phoi hop
    z = (sig - sig.mean()) / (sig.std() + 1e-12)

    # b10: bo loc dao ham tho
    nu = int(np.ceil(0.005 * fs))
    nz = int(np.floor(0.0030 * fs / 2)) * 2 + 1
    B = np.concatenate([np.ones(nu), np.zeros(nz), -np.ones(nu)])
    delay = len(B) // 2
    padded = np.concatenate([np.repeat(z[0], delay), z, np.repeat(z[-1], delay)])
    d = sg.lfilter(B, 1.0, padded)
    d = d[2 * delay:]                      # MATLAB 2*delay+1:end (1-based)
    adecg = np.abs(d[:len(z)])

    # b11: Butterworth bac 1, 0,7-8 Hz, filtfilt
    b, a = sg.butter(1, [0.7 / (fs / 2), 8.0 / (fs / 2)], btype='band')
    abs_dev = sg.filtfilt(b, a, adecg)

    # b12-13: chon kenh -> phep rong (1 kenh)

    # b14-15: do so bo
    distance = ms / 1000.0 * fs
    s_ad = abs_dev - abs_dev.min()
    peaks, _ = sg.find_peaks(s_ad, distance=max(1, int(round(distance))))
    if len(peaks) < 8:
        return np.array([]), dict(n_peaks_so_bo=int(len(peaks)), med_size=0)

    # b16-18: mau trung vi
    med_size = int(round(np.median(np.diff(peaks)) / 2.0))
    if med_size < 2:
        return np.array([]), dict(n_peaks_so_bo=int(len(peaks)), med_size=med_size)
    L = 2 * med_size + 1
    rows = []
    for j in range(2, len(peaks) - 2):     # MATLAB j = 3 : length(peaks)-2
        p = peaks[j]
        if p - med_size < 0 or p + med_size + 1 > len(sig):
            continue
        rows.append(sig[p - med_size:p + med_size + 1])
    if not rows:
        return np.array([]), dict(n_peaks_so_bo=int(len(peaks)), med_size=med_size)
    T = np.asarray(rows)
    if faithful:
        # tai lap loi cua tac gia: template(1,:) va template(2,:) = 0 trong MATLAB
        T = np.vstack([np.zeros((2, L)), T])
    template_med = np.median(T, axis=0)

    # b19-20: bo loc phoi hop + do dinh
    r = matched_filter(sig, template_med)
    r_shift = r - r.min()
    fpk, _ = sg.find_peaks(r_shift, distance=max(1, int(round(distance))))
    # b21: fPeaks/4 tra ve 250 Hz -> nhung nhan tham chieu o 1000 Hz = 250*4,
    # nen chi so noi bo (1000 Hz) dung truc tiep lam chi so @1000 Hz.
    return fpk.astype(float), dict(n_peaks_so_bo=int(len(peaks)), med_size=med_size,
                                   n_hang_mau=int(T.shape[0]))


def run_leads(leads250, gt1000, ms, faithful):
    """leads250: list phan du @250 Hz. -> (ket qua kenh PSD, ket qua tung kenh)"""
    per = []
    for i, res in enumerate(leads250):
        det, info = powermf_1ch_detect(res, ms=ms, faithful=faithful)
        if len(det):
            sc = M.match_events(det, gt1000, CFG['fs_in'], TOL_MS)
        else:
            sc = dict(TP=0, FP=0, FN=int(len(gt1000)), Se=0.0, PPV=0.0, F1=0.0,
                      jitter_ms=float('nan'))
        sc = {k: (float(v) if isinstance(v, float) else int(v)) for k, v in sc.items()}
        sc.update(lead=i, n_det=int(len(det)), **info)
        per.append(sc)
    return per


def load_s22(tag):
    """-> (list 4 phan du @250 Hz, psd list, gt @1000 Hz)"""
    S = loadmat(os.path.join(WORK, tag + '.mat'))
    sig = np.asarray(S['signal'], float)
    fs0 = float(np.asarray(S['Fs']).ravel()[0])
    gt = np.asarray(S['fqrs'], float).ravel() - 1.0
    res, psd = [], []
    for c in range(min(4, sig.shape[0])):
        x = M.preprocess(np.nan_to_num(sig[c]), int(fs0), CFG)
        rr, _ = M.cancel_maternal(x, CFG)
        res.append(rr)
        psd.append(psd_score(rr))
    return res, psd, gt


def load_cinc(D, rec):
    import wfdb
    r_ = wfdb.rdrecord(os.path.join(D, rec))
    ann = wfdb.rdann(os.path.join(D, rec), 'fqrs')
    fs0 = r_.fs
    gt = (np.asarray(ann.sample, float) * (1000.0 / fs0)).round()
    res, psd = [], []
    for lead in range(min(4, r_.p_signal.shape[1])):
        s = np.nan_to_num(r_.p_signal[:, lead])
        if fs0 != 1000:
            s = sg.resample_poly(s, 1000, int(fs0))
        x = M.preprocess(s, 1000, CFG)
        rr, _ = M.cancel_maternal(x, CFG)
        res.append(rr)
        psd.append(psd_score(rr))
    del r_
    return res, psd, gt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sets', nargs='+', default=['s22'], choices=['s22', 'cinc'])
    ap.add_argument('--ms', type=float, default=340.0)
    ap.add_argument('--faithful', type=int, default=1)
    ap.add_argument('--suffix', default='', help='hau to file ket qua (de chay bien the)')
    a = ap.parse_args()

    global OUT, LOG
    if a.suffix:
        OUT = OUT.replace('.json', '_%s.json' % a.suffix)
        LOG = LOG.replace('.txt', '_%s.txt' % a.suffix)

    out = {}
    if os.path.isfile(OUT):
        try:
            out = json.load(open(OUT, encoding='utf-8'))
        except Exception:
            out = {}
    out.setdefault('meta', {}).update(
        ngay=datetime.datetime.now().isoformat(timespec='seconds'),
        thuat_toan='Power-MF-1ch: bo do cua Power-MF (Jaeger 2024) o che do DON KENH, Python/scipy',
        dac_ta='survey/scout_baselines.md muc 3 (21 buoc doc truc tiep tu PowerMF.m)',
        front_end='M.preprocess 10-60 Hz + notch 50 Hz -> 250 Hz; M.cancel_maternal (mau trung vi + ti le BPTT)',
        bo_qua='FecgICAm + FecgICAf (can da kenh); chon kenh PSD thay bang quy tac mu nhan cua nhom',
        cham_diem='M.match_events +/-50 ms, ghep tham lam 1-1',
        ms_minpeakdistance=a.ms, faithful_template=bool(a.faithful))

    log('=' * 78)
    log('Power-MF-1ch (Python) ms=%g faithful=%d sets=%s' % (a.ms, a.faithful, ','.join(a.sets)))

    if 's22' in a.sets:
        rows = []
        for tag in S22:
            res, psd, gt = load_s22(tag)
            per = run_leads(res, gt, a.ms, bool(a.faithful))
            k = int(np.argmax(psd))
            row = dict(rec=tag, n_ref=int(len(gt)), kenh_psd=k,
                       F1_psd=per[k]['F1'], Se_psd=per[k]['Se'], PPV_psd=per[k]['PPV'],
                       F1_kenh0=per[0]['F1'],
                       F1_tb_4kenh=float(np.mean([p['F1'] for p in per])),
                       F1_oracle=float(max(p['F1'] for p in per)),
                       per_lead=per)
            rows.append(row)
            out.setdefault('s22', {})[tag] = row
            log('%-7s PSD kenh %d  F1=%6.2f  Se=%6.2f  PPV=%6.2f  | kenh0=%6.2f oracle=%6.2f'
                % (tag, k, row['F1_psd'], row['Se_psd'], row['PPV_psd'],
                   row['F1_kenh0'], row['F1_oracle']))
            json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        f1 = np.array([r['F1_psd'] for r in rows])
        out.setdefault('tom_tat', {})['s22'] = dict(
            n=len(rows), F1_mean=float(f1.mean()), F1_sd=float(f1.std(ddof=1)),
            F1_median=float(np.median(f1)), F1_min=float(f1.min()), F1_max=float(f1.max()))
        log('TAP s22  n=%d  F1 tb=%.2f  sd=%.2f' % (len(rows), f1.mean(), f1.std(ddof=1)))
        json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    if 'cinc' in a.sets:
        import wfdb  # noqa: F401
        D = cinc2013_dir()
        if D is None:
            log('KHONG co CinC 2013 -- bo qua')
        else:
            recs = sorted(set(f[:-4] for f in os.listdir(D) if f.endswith('.dat')))
            recs = [r for r in recs if os.path.isfile(os.path.join(D, r + '.fqrs'))]
            rows = []
            for i, rec in enumerate(recs):
                try:
                    res, psd, gt = load_cinc(D, rec)
                except Exception as e:
                    log('%-5s LOI nap: %s' % (rec, e))
                    continue
                per = run_leads(res, gt, a.ms, bool(a.faithful))
                k = int(np.argmax(psd))
                row = dict(rec=rec, n_ref=int(len(gt)), kenh_psd=k,
                           F1_psd=per[k]['F1'], Se_psd=per[k]['Se'], PPV_psd=per[k]['PPV'],
                           F1_kenh0=per[0]['F1'],
                           F1_tb_4kenh=float(np.mean([p['F1'] for p in per])),
                           F1_oracle=float(max(p['F1'] for p in per)),
                           bad_annotation=rec in BAD_ANN)
                rows.append(row)
                out.setdefault('cinc75', {})[rec] = row
                log('[%2d/%d] %-5s PSD kenh %d F1=%6.2f  kenh0=%6.2f  TB4=%6.2f  oracle=%6.2f%s'
                    % (i + 1, len(recs), rec, k, row['F1_psd'], row['F1_kenh0'],
                       row['F1_tb_4kenh'], row['F1_oracle'],
                       ' *chu thich sai' if row['bad_annotation'] else ''))
                if (i + 1) % 5 == 0:
                    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            f1 = np.array([r['F1_psd'] for r in rows])
            g = np.array([r['F1_psd'] for r in rows if not r['bad_annotation']])
            out.setdefault('tom_tat', {})['cinc75'] = dict(
                n=len(rows), F1_mean=float(f1.mean()), F1_sd=float(f1.std(ddof=1)),
                F1_median=float(np.median(f1)),
                n68=len(g), F1_mean_68=float(g.mean()),
                F1_kenh0=float(np.mean([r['F1_kenh0'] for r in rows])),
                F1_tb_4kenh=float(np.mean([r['F1_tb_4kenh'] for r in rows])),
                F1_oracle=float(np.mean([r['F1_oracle'] for r in rows])))
            log('TAP cinc n=%d  F1 tb(PSD)=%.2f  sd=%.2f  | 68 ban: %.2f  kenh0=%.2f oracle=%.2f'
                % (len(rows), f1.mean(), f1.std(ddof=1), g.mean(),
                   out['tom_tat']['cinc75']['F1_kenh0'], out['tom_tat']['cinc75']['F1_oracle']))
            json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    log('xong -> %s' % OUT)


if __name__ == '__main__':
    main()
