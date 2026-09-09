#!/usr/bin/env python
"""
FetalQRS-TCN — command line inference.

Reads one abdominal ECG lead and writes fetal R-peak times, the fetal heart rate series
and a short summary.

Examples
--------
  # a PhysioNet EDF record (ADFECGDB); lead 1 is the first abdominal channel
  python predict.py --input data/raw/r01.edf --lead 1 --out out/r01

  # a WFDB record (CinC 2013 set-a)
  python predict.py --input data/external_test/a01 --lead 0 --format wfdb --out out/a01

  # a plain CSV or NPY of one channel, telling us its sampling rate
  python predict.py --input signal.csv --fs 500 --out out/signal

  # score against reference annotations when they exist
  python predict.py --input data/raw/r01.edf --lead 1 --annot qrs --out out/r01
"""
from __future__ import annotations
import os, sys, json, argparse, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, torch

ROOT = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'fqrs_model.py'))
M = importlib.util.module_from_spec(_s); _s.loader.exec_module(M)

DEFAULT_CKPT = os.path.join(ROOT, 'checkpoints', 'fetalqrs_tcn_production.pt')

def read_signal(path, fmt, lead, fs_cli):
    """returns (signal 1-D float array, fs, reference peaks or None)"""
    ext = os.path.splitext(path)[1].lower()
    if fmt == 'auto':
        fmt = 'edf' if ext == '.edf' else ('csv' if ext in ('.csv', '.txt') else
              ('npy' if ext == '.npy' else 'wfdb'))
    if fmt == 'edf':
        import mne
        raw = mne.io.read_raw_edf(path, preload=True, verbose=False)
        sig = raw.get_data(); fs = float(raw.info['sfreq'])
        if lead >= sig.shape[0]:
            raise SystemExit(f'lead {lead} out of range: file has {sig.shape[0]} channels '
                             f'({raw.ch_names})')
        return sig[lead], fs, raw.ch_names
    if fmt == 'wfdb':
        import wfdb
        rec = wfdb.rdrecord(os.path.splitext(path)[0])
        fs = float(rec.fs)
        if lead >= rec.p_signal.shape[1]:
            raise SystemExit(f'lead {lead} out of range: record has {rec.p_signal.shape[1]} channels')
        return rec.p_signal[:, lead], fs, rec.sig_name
    if fmt == 'npy':
        a = np.load(path); a = a if a.ndim == 1 else a[lead]
        if not fs_cli: raise SystemExit('--fs is required for .npy input')
        return a, float(fs_cli), None
    a = np.loadtxt(path, delimiter=',')
    a = a if a.ndim == 1 else a[:, lead]
    if not fs_cli: raise SystemExit('--fs is required for .csv input')
    return a, float(fs_cli), None

def read_annotations(path, ann_ext, fs_target, fs_in):
    try:
        import wfdb
        ann = wfdb.rdann(path, ann_ext)
        return (np.asarray(ann.sample) * (fs_target / fs_in)).round().astype(int)
    except Exception as e:
        print(f'[warn] could not read annotations ({e})'); return None

def main():
    ap = argparse.ArgumentParser(description='Fetal QRS detection from a single abdominal ECG lead')
    ap.add_argument('--input', required=True, help='EDF / WFDB record / .csv / .npy')
    ap.add_argument('--format', default='auto', choices=['auto', 'edf', 'wfdb', 'csv', 'npy'])
    ap.add_argument('--lead', type=int, default=1, help='channel index (EDF ADFECGDB: 1..4 are abdominal)')
    ap.add_argument('--fs', type=float, default=None, help='sampling rate, required for csv/npy')
    ap.add_argument('--checkpoint', default=DEFAULT_CKPT)
    ap.add_argument('--threshold', type=float, default=None, help='override the stored threshold')
    ap.add_argument('--annot', default=None, help='WFDB annotation extension to score against, e.g. qrs or fqrs')
    ap.add_argument('--out', default=None, help='output prefix; writes <prefix>.json and <prefix>_fqrs.txt')
    a = ap.parse_args()

    if not os.path.exists(a.checkpoint):
        raise SystemExit(f'checkpoint not found: {a.checkpoint}\nRun train_final.py first.')
    ck = torch.load(a.checkpoint, map_location='cpu', weights_only=False)
    cfg = ck.get('config', M.CFG)
    model = M.FetalQRSTCN(); model.load_state_dict(ck['state_dict']); model.eval()
    thr = a.threshold if a.threshold is not None else float(ck.get('threshold', 0.45))

    sig, fs, ch = read_signal(a.input, a.format, a.lead, a.fs)
    print(f'input        {a.input}  lead {a.lead}' + (f'  ({ch[a.lead]})' if ch else ''))
    print(f'sampling     {fs:g} Hz, {len(sig)} samples = {len(sig)/fs:.1f} s')
    print(f'model        {os.path.basename(a.checkpoint)}, {ck.get("n_params", M.n_params(model)):,} params, '
          f'threshold {thr:.2f}')

    res = M.detect(model, sig, fs_in=fs, threshold=thr, cfg=cfg)
    print(f'\nfetal beats  {res["n_beats"]}')
    print(f'fetal HR     median {res["fhr_median_bpm"]:.1f} bpm' +
          (f', range {res["fhr_bpm"].min():.0f}-{res["fhr_bpm"].max():.0f}' if len(res['fhr_bpm']) else ''))
    print(f'maternal HR  {60.0/np.median(np.diff(res["maternal_qrs_seconds"])):.1f} bpm'
          if len(res['maternal_qrs_seconds']) > 2 else 'maternal HR  n/a')

    scored = None
    if a.annot:
        ref = read_annotations(os.path.splitext(a.input)[0] if a.format == 'wfdb' else a.input,
                               a.annot, cfg['fs'], fs)
        if ref is not None:
            det250 = np.round(res['fqrs_seconds'] * cfg['fs']).astype(int)
            scored = M.match_events(det250, ref, cfg['fs'], cfg['tolerance_ms'])
            print(f'\nscored vs .{a.annot} (+/-{cfg["tolerance_ms"]} ms): '
                  f'Se {scored["Se"]:.2f}  PPV {scored["PPV"]:.2f}  F1 {scored["F1"]:.2f}  '
                  f'jitter {scored["jitter_ms"]:.2f} ms  (TP {scored["TP"]} FP {scored["FP"]} FN {scored["FN"]})')

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)) or '.', exist_ok=True)
        np.savetxt(a.out + '_fqrs.txt', res['fqrs_seconds'], fmt='%.4f',
                   header='fetal R-peak times in seconds')
        payload = dict(input=a.input, lead=a.lead, fs_in=fs, checkpoint=os.path.basename(a.checkpoint),
                       threshold=thr, n_beats=int(res['n_beats']),
                       fhr_median_bpm=res['fhr_median_bpm'],
                       fqrs_seconds=[round(float(v), 4) for v in res['fqrs_seconds']],
                       fhr=[[round(float(t), 2), round(float(b), 1)]
                            for t, b in zip(res['fhr_time_s'], res['fhr_bpm'])],
                       scored=scored)
        json.dump(payload, open(a.out + '.json', 'w'), indent=1)
        print(f'\nwrote        {a.out}.json  and  {a.out}_fqrs.txt')

if __name__ == '__main__':
    main()
