# -*- coding: utf-8 -*-
"""A2 PHAN 1a -- Chan doan: RR that cua tung ban ghi so voi ms_minpeakdistance=340 ms,
va uoc luong RR MU NHAN (khong dung nhan) de dat tham so thich nghi.

Uoc luong mu nhan: bang thong 10-60 Hz -> bao hinh |dao ham| -> Welch PSD ->
dinh lon nhat trong dai 1,6-3,6 Hz (96-216 bpm) -> HR -> RR.
(Cung tinh than voi buoc 12 cua PowerMF nhung chay trong Python, tren tin hieu bung THO,
khong dung bat ky nhan nao.)

Xuat: baselines/powermf_rr_diag.json
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from scipy.io import loadmat
from scipy import signal as sps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, 'baselines', 'powermf_work')
OUT = os.path.join(ROOT, 'baselines', 'powermf_rr_diag.json')

TAGS = (['r01', 'r04', 'r07', 'r08', 'r10']
        + ['B2_%02d' % i for i in range(1, 13)]
        + ['B1_%02d' % i for i in range(1, 11)])


def blind_rr_ms(sig4, fs):
    """Uoc luong RR trung vi (ms) MU NHAN tu 4 dao trinh bung tho."""
    b, a = sps.butter(3, [10.0, 60.0], btype='band', fs=fs)
    best = None
    for ch in range(sig4.shape[0]):
        x = np.asarray(sig4[ch], float)
        x = x - np.median(x)
        y = sps.filtfilt(b, a, x)
        env = np.abs(np.diff(y, prepend=y[0]))
        # ha mau ve 200 Hz cho PSD nhanh
        q = int(fs // 200)
        if q > 1:
            env = sps.decimate(env, q, ftype='fir', zero_phase=True)
            fse = fs / q
        else:
            fse = fs
        env = env - env.mean()
        nper = int(min(len(env), fse * 20))
        f, P = sps.welch(env, fs=fse, nperseg=nper, noverlap=nper // 2)
        m = (f >= 1.6) & (f <= 3.6)
        if not m.any():
            continue
        pk = P[m].max()
        fr = f[m][int(np.argmax(P[m]))]
        if best is None or pk > best[0]:
            best = (pk, fr, ch)
    if best is None:
        return float('nan'), -1, float('nan')
    _, fr, ch = best
    return 1000.0 / fr, ch, fr * 60.0


def main():
    res = {}
    for tag in TAGS:
        p = os.path.join(WORK, tag + '.mat')
        if not os.path.isfile(p):
            print('thieu %s' % p)
            continue
        S = loadmat(p)
        sig = np.asarray(S['signal'], float)
        fs = float(np.asarray(S['Fs']).ravel()[0])
        ref = np.asarray(S['fqrs'], float).ravel() - 1.0
        rr = np.diff(ref) / fs * 1000.0
        rr = rr[(rr > 200) & (rr < 1200)]
        rr_med = float(np.median(rr))
        rr_p05 = float(np.percentile(rr, 5))
        rr_p01 = float(np.percentile(rr, 1))
        brr, bch, bhr = blind_rr_ms(sig, fs)
        # tham so thich nghi: 0,7 x RR uoc luong mu nhan
        ms_adapt = float(round(0.7 * brr)) if np.isfinite(brr) else 340.0
        d = dict(rec=tag, fs=fs, n_ref=int(ref.size),
                 dur_s=round(sig.shape[1] / fs, 1),
                 hr_ref_bpm=round(60000.0 / rr_med, 1),
                 rr_ref_median_ms=round(rr_med, 1),
                 rr_ref_p05_ms=round(rr_p05, 1),
                 rr_ref_p01_ms=round(rr_p01, 1),
                 frac_rr_duoi_340=round(float(np.mean(rr < 340.0)) * 100, 2),
                 frac_rr_duoi_400=round(float(np.mean(rr < 400.0)) * 100, 2),
                 rr_mu_nhan_ms=round(float(brr), 1),
                 hr_mu_nhan_bpm=round(float(bhr), 1),
                 kenh_mu_nhan=int(bch),
                 ms_thich_nghi=ms_adapt,
                 sai_so_uoc_luong_ms=round(float(brr - rr_med), 1))
        res[tag] = d
        print('%-7s HR=%6.1f bpm  RR trung vi=%6.1f ms  p05=%6.1f  %%RR<340=%5.2f  '
              '| mu nhan RR=%6.1f (lech %+6.1f)  -> ms=%.0f'
              % (tag, d['hr_ref_bpm'], rr_med, rr_p05, d['frac_rr_duoi_340'],
                 brr, brr - rr_med, ms_adapt), flush=True)
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('-> %s' % OUT)


if __name__ == '__main__':
    main()
