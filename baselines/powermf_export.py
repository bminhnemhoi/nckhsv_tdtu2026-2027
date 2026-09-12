# -*- coding: utf-8 -*-
"""Xuat 4 kenh bung + nhan fQRS tham chieu ra .mat de Octave doc (tranh doc EDF trong Octave).

Dung chung cho ADFECGDB (5 ban ghi PhysioNet) va Silesia (B1 10 ban ghi, B2 12 ban ghi).
Moi .mat chua:
    signal  [4 x N]  double, 4 dao trinh bung, @fs Hz
    Fs      scalar   tan so lay mau
    fqrs    [1 x K]  chi so mau (1-based cho MATLAB/Octave) cua QRS thai tham chieu
    rec     char     ten ban ghi
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from scipy.io import savemat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
sys.path.insert(0, os.path.join(ROOT, 'model'))
from _paths import adfecgdb_dir  # noqa: E402

PHYSIONET = ('r01', 'r04', 'r07', 'r08', 'r10')
# B2_01/02/07/10/11 trung voi PhysioNet -> luon loai (xem MEMORY / eval_22.py)
B2_KEEP = ('B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12')
B2_ALL = tuple('B2_%02d' % i for i in range(1, 13))
B1_ALL = tuple('B1_%02d' % i for i in range(1, 11))


def load_record(tag):
    """-> (abd[4, N] float64 @1000 Hz, fqrs samples @1000 Hz, meta dict)"""
    if tag in PHYSIONET:
        import mne, wfdb
        d = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(d, tag + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        # kenh 0 = FECG truc tiep tu dien cuc da dau; kenh 1..4 = 4 dao trinh bung
        abd = np.ascontiguousarray(sig[1:5], dtype=np.float64)
        fq = np.asarray(wfdb.rdann(os.path.join(d, tag + '.edf'), 'qrs').sample, int)
        meta = dict(source='ADFECGDB PhysioNet (EDF), nhan = FECG truc tiep da dau', fs=1000)
        del raw, sig
    else:
        import silesia_loader as L
        abd, fq, mt = L.load(tag)
        abd = np.ascontiguousarray(np.asarray(abd, dtype=np.float64))
        fq = np.asarray(fq, int)
        meta = dict(source='Silesia %s' % mt.get('reference_source', ''), fs=1000)
    return abd, fq, meta


def export(tag, out_dir):
    abd, fq, meta = load_record(tag)
    # PowerMF khong chiu duoc NaN -> noi suy tuyen tinh nhu benchmark_algorithms.m lam
    n_nan = int(np.isnan(abd).sum())
    if n_nan:
        for c in range(abd.shape[0]):
            row = abd[c]
            bad = np.isnan(row)
            if bad.any():
                row[bad] = np.interp(np.flatnonzero(bad), np.flatnonzero(~bad), row[~bad])
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, tag + '.mat')
    savemat(path, dict(signal=abd, Fs=float(meta['fs']),
                       fqrs=(fq + 1).astype(np.float64).reshape(1, -1), rec=tag),
            do_compression=False)
    print('[export] %-7s  kenh=%d  N=%d  fs=%d  n_fqrs=%d  NaN=%d  -> %s'
          % (tag, abd.shape[0], abd.shape[1], meta['fs'], len(fq), n_nan, path), flush=True)
    return dict(rec=tag, n_samples=int(abd.shape[1]), fs=int(meta['fs']),
                n_fqrs=int(len(fq)), n_nan=n_nan, source=meta['source'], mat=path)


if __name__ == '__main__':
    work = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'baselines', 'powermf_work')
    which = sys.argv[2] if len(sys.argv) > 2 else 'adfecgdb'
    tags = {'adfecgdb': PHYSIONET, 'b2': B2_ALL, 'b1': B1_ALL}[which]
    for t in tags:
        export(t, work)
