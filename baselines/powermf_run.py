# -*- coding: utf-8 -*-
"""Chay lai Power-MF (Jaeger 2024, DA KENH - 4 dao trinh bung) bang GNU Octave,
roi cham diem bang CHINH bo cham cua nhom (model.fqrs_model.match_events, +/-50 ms).

Vi sao lam: den truoc phien nay, KHONG baseline SOTA nao trong bai duoc chay lai;
moi con so Power-MF/Varanini deu la so DA CONG BO trich tu Results/*.mat cua repo goc.

Chuoi thuc thi:
  1. powermf_export.py  ->  .mat (signal[4xN], Fs, fqrs, rec)      [Python]
  2. octave/run_powermf.m  ->  .mat (fPeaks @Fs, 1-based)          [Octave 11.3.0 + pkg signal]
     PowerMF.m dung o buoc nay la BAN DA VA (octave/apply_patches.py, 6 ban va P1..P6)
  3. M.match_events(det, ref, fs, 50)  ->  TP/FP/FN/Se/PPV/F1      [Python, bo cham cua NHOM]

KHONG dung Bxb_compare cua repo (can WFDB Toolbox) de bao dam cung giao thuc cham
voi moi so khac trong bai.

Chay:
  python baselines/powermf_run.py --sets adfecgdb --workers 2
  python baselines/powermf_run.py --sets adfecgdb b2 b1 --workers 2
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')

import argparse
import datetime
import importlib.util
import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from scipy.io import loadmat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'baselines')
WORK = os.path.join(HERE, 'powermf_work')
OCT_DIR = os.path.join(HERE, 'octave')
OCTAVE = os.path.join(ROOT, 'tools', 'octave', 'octave-11.3.0-w64',
                      'mingw64', 'bin', 'octave-cli.exe')
VARANINI = os.path.join(ROOT, 'tools', 'varanini', 'xCinC')
LOG = os.path.join(HERE, 'powermf_log.txt')
OUT = os.path.join(HERE, 'powermf_results.json')

sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
sys.path.insert(0, os.path.join(ROOT, 'model'))

_spec = importlib.util.spec_from_file_location(
    'fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

sys.path.insert(0, HERE)
import powermf_export as EX  # noqa: E402

SETS = {
    'adfecgdb': list(EX.PHYSIONET),           # 5 ban ghi PhysioNet
    'b2': list(EX.B2_ALL),                    # 12 ban ghi B2 (gom ca 5 ban trung PhysioNet)
    'b2_keep': list(EX.B2_KEEP),              # 7 ban ghi B2 khong trung
    'b1': list(EX.B1_ALL),                    # 10 ban ghi B1
}

_lock = threading.Lock()
_t0 = time.time()


def log(msg):
    line = '[%7.1fs] %s' % (time.time() - _t0, msg)
    with _lock:
        print(line, flush=True)
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')


def ensure_mat(tag):
    p = os.path.join(WORK, tag + '.mat')
    if os.path.isfile(p) and os.path.getsize(p) > 1000:
        return p
    info = EX.export(tag, WORK)
    return info['mat']


def run_one(tag, ms):
    """-> dict ket qua mot ban ghi"""
    t0 = time.time()
    in_mat = os.path.join(WORK, tag + '.mat')
    out_mat = os.path.join(WORK, tag + '_powermf.mat')
    stdout_txt = os.path.join(WORK, tag + '_octave.log')

    cmd = [OCTAVE, '--no-gui', '--quiet',
           os.path.join(OCT_DIR, 'run_powermf.m'), in_mat, out_mat, VARANINI, str(ms)]
    log('%-7s bat dau Octave' % tag)
    try:
        pr = subprocess.run(cmd, cwd=OCT_DIR, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', timeout=3600)
        txt = (pr.stdout or '') + '\n----- stderr -----\n' + (pr.stderr or '')
    except subprocess.TimeoutExpired:
        txt = 'TIMEOUT sau 3600 s'
        pr = None
    with open(stdout_txt, 'w', encoding='utf-8') as f:
        f.write(txt)

    rec = dict(rec=tag, ms=ms, octave_rc=(pr.returncode if pr else -9),
               wall_s=round(time.time() - t0, 1), octave_log=stdout_txt)

    if pr is None or not os.path.isfile(out_mat):
        rec.update(ok=False, err='octave khong tao duoc file ket qua')
        log('%-7s THAT BAI (%s)' % (tag, rec['err']))
        return rec

    o = loadmat(out_mat)
    det = np.asarray(o['fPeaks'], float).ravel()
    ok = bool(np.asarray(o['ok']).ravel()[0])
    err = str(np.asarray(o['err']).ravel()[0]) if np.asarray(o['err']).size else ''
    src = loadmat(in_mat)
    ref = np.asarray(src['fqrs'], float).ravel()
    fs = float(np.asarray(src['Fs']).ravel()[0])
    n = int(np.asarray(src['signal']).shape[1])

    rec.update(ok=ok, err=err, fs=fs, n_samples=n,
               dur_min=round(n / fs / 60.0, 2),
               n_det=int(det.size), n_ref=int(ref.size),
               octave_s=float(np.asarray(o['elapsed_s']).ravel()[0]))
    if det.size:
        # ca hai deu la chi so 1-based -> lui ve 0-based (phep doi khong doi ket qua ghep)
        sc = M.match_events(det - 1.0, ref - 1.0, fs, 50)
        rec.update({k: (float(v) if isinstance(v, float) else int(v)) for k, v in sc.items()})
    else:
        rec.update(TP=0, FP=0, FN=int(ref.size), Se=0.0, PPV=0.0, F1=0.0,
                   jitter_ms=float('nan'))
    log('%-7s F1=%6.2f  Se=%6.2f  PPV=%6.2f  TP=%d FP=%d FN=%d  (%.0f s)'
        % (tag, rec['F1'], rec['Se'], rec['PPV'], rec['TP'], rec['FP'], rec['FN'],
           rec['wall_s']))
    return rec


def summarize(recs):
    f1 = np.array([r['F1'] for r in recs], float)
    return dict(n=len(recs),
                F1_mean=float(f1.mean()), F1_sd=float(f1.std(ddof=1)) if len(f1) > 1 else 0.0,
                F1_median=float(np.median(f1)),
                F1_min=float(f1.min()), F1_max=float(f1.max()),
                Se_mean=float(np.mean([r['Se'] for r in recs])),
                PPV_mean=float(np.mean([r['PPV'] for r in recs])),
                n_that_bai=int(sum(1 for r in recs if not r['ok'])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sets', nargs='+', default=['adfecgdb'], choices=list(SETS))
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--ms', type=float, default=340.0)
    ap.add_argument('--only', nargs='*', default=None, help='chi chay may ban ghi nay')
    a = ap.parse_args()

    os.makedirs(WORK, exist_ok=True)
    if not os.path.isfile(OCTAVE):
        raise SystemExit('Khong thay octave-cli: ' + OCTAVE)
    if not os.path.isdir(VARANINI):
        raise SystemExit('Khong thay ma Varanini: ' + VARANINI)

    log('=' * 78)
    log('Power-MF (DA KENH, 4 dao trinh bung) -- chay lai that, khong phai so da cong bo')
    log('ngay=%s  octave=%s  ms=%g  workers=%d  sets=%s'
        % (datetime.datetime.now().isoformat(timespec='seconds'), OCTAVE, a.ms,
           a.workers, ','.join(a.sets)))

    all_res = {}
    if os.path.isfile(OUT):
        try:
            all_res = json.load(open(OUT, encoding='utf-8'))
        except Exception:
            all_res = {}
    all_res.setdefault('meta', {})
    all_res['meta'].update(
        ngay=datetime.datetime.now().isoformat(timespec='seconds'),
        thuat_toan='Power-MF (Jaeger 2024) -- DA KENH: 4 dao trinh bung, ICA 2 lan',
        nguon_ma='github.com/mad-lab-fau/fecg-benchmarking (MIT) + xCinC cua Varanini 2014 '
                 '(archive.physionet.org/challenge/2013/sources/pmea)',
        runtime='GNU Octave 11.3.0 portable (tools/octave), pkg signal',
        ban_va='baselines/octave/apply_patches.py (P1..P6); P6 la ban va chan dung: '
               'interpft cua Octave tra ve so phuc -> findpeaks tra ve 0 dinh -> '
               'PowerMF rong tren MOI ban ghi',
        cham_diem='model/fqrs_model.py::match_events, +/-50 ms, ghep tham lam 1-1 '
                  '(bo cham cua NHOM, khong dung Bxb_compare cua repo)',
        ms_minpeakdistance=a.ms)

    for s in a.sets:
        tags = SETS[s]
        if a.only:
            tags = [t for t in tags if t in a.only]
        log('--- tap %s: %d ban ghi ---' % (s, len(tags)))
        for t in tags:
            ensure_mat(t)
        recs = []
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            for r in ex.map(lambda t: run_one(t, a.ms), tags):
                recs.append(r)
                all_res.setdefault('per_record', {})[r['rec']] = r
                json.dump(all_res, open(OUT, 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=1)
        good = [r for r in recs if r['ok']]
        summ = summarize(recs)
        all_res.setdefault('tom_tat', {})[s] = summ
        log('TAP %-9s n=%d  F1 tb=%.2f  sd=%.2f  trung vi=%.2f  min=%.2f  max=%.2f  that_bai=%d'
            % (s, summ['n'], summ['F1_mean'], summ['F1_sd'], summ['F1_median'],
               summ['F1_min'], summ['F1_max'], summ['n_that_bai']))
        json.dump(all_res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    log('xong. ket qua -> %s' % OUT)


if __name__ == '__main__':
    main()
