# -*- coding: utf-8 -*-
"""
gate22_features.py -- Buoc 1 cua A3: trich dac trung doan 4 s + F1 doan cho MO HINH 22 CA.

Voi moi chu the trong 22 chu the, dung DUNG checkpoint fold KHONG chua chu the do
(lay tu benchmark_dpss/eval_22.json['folds']) va DUNG kenh PSD mu nhan ma eval_22 da chon
-> tai lap F1 muc ban ghi (kiem chung so voi eval_22.json), roi:
  * cat thanh doan 4 s khong chong (1000 mau @250 Hz)
  * tinh F1 tung doan (ghep tham lam 1-1 +/-50 ms tren TOAN ban ghi roi gan TP/FN/FP vao doan)
  * tinh 12 chi so SQI co dien (fsqi.CLASSICAL_KEYS + peak_prob_mean + prob_max)
    -- KHONG dac trung nao nhin thay nhan
  * luu dinh phat hien / nhan (giay) de tinh STV o buoc 2

Chay:  python analysis/gate22_features.py --subjects r01,r04   (mac dinh: tat ca 22)
Ket qua: analysis/gate22_cache/gate22_feat_<tag>.json  (mot tep moi chu the, de chay song song)
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, argparse, importlib.util
import numpy as np, torch, mne, wfdb
from scipy import signal as sg
torch.set_num_threads(1)

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss')); sys.path.insert(0, os.path.join(ROOT, 'fsqi'))
from _paths import adfecgdb_dir
import fsqi


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


M = _load('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py')); CFG = M.CFG
L = _load('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))

FS = CFG['fs']; FS_IN = CFG['fs_in']; Q = FS_IN // FS
SEG_S = 4.0; SEG = int(SEG_S * FS); TOL_MS = 50; FHR_BAND = (1.8, 3.0)
FEATURES = list(fsqi.CLASSICAL_KEYS) + ['peak_prob_mean', 'prob_max']
EVAL22 = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json'), encoding='utf-8'))
CKDIR = os.path.join(ROOT, 'model', 'checkpoints')
LEADS = (1, 2, 3, 4)


def group_of(tag):
    return 'PhysioNet' if tag.startswith('r') else tag[:2]


def psd_score(x250, fs=FS):
    e = np.abs(sg.hilbert(x250 - np.mean(x250))); e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def load_subject(tag):
    g = group_of(tag)
    if g == 'PhysioNet':
        D = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        fq1000 = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, int)
        chans = {l: sig[l] for l in LEADS}
        dur = float(sig.shape[1] / 1000.0)
        del raw, sig
    else:
        sig, _, mt = L.load(tag)
        fq1000 = np.asarray(mt['fqrs_all'], int)
        chans = {l: sig[l - 1] for l in LEADS}
        dur = float(mt['duration_s'])
        del sig
    return chans, fq1000, dur


def greedy_match(det, ref, tol):
    """ghep tham lam 1-1 nhu train_gate.py / M.match_events"""
    ref = np.asarray(ref, float); det = np.sort(np.asarray(det, float))
    used = np.zeros(len(ref), bool); dm = np.zeros(len(det), bool)
    for i, d in enumerate(det):
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (~used))[0]
        if len(ok):
            used[ok[int(np.argmin(dd[ok]))]] = True; dm[i] = True
    return det, dm, used


def run(tag, out_dir):
    t0 = time.time()
    e22 = EVAL22['subjects'][tag]
    fold = '%02d' % int(e22['fold']); ck = os.path.join(CKDIR, 'fetalqrs_tcn_22_fold_' + fold + '.pt')
    bl = torch.load(ck, map_location='cpu', weights_only=False)
    assert tag in bl['test_subjects'], tag + ' khong nam trong test_subjects cua fold ' + fold + ' -> RO RI'
    net = M.FetalQRSTCN(); net.load_state_dict(bl['state_dict']); net.eval(); thr = float(bl['threshold'])

    chans, fq1000, dur = load_subject(tag)
    prep = {}
    for l in LEADS:
        x = M.preprocess(chans[l], FS_IN, CFG); r, _ = M.cancel_maternal(x, CFG)
        prep[l] = (x, r, psd_score(r))
    psd_lead = max(LEADS, key=lambda l: prep[l][2])
    assert psd_lead == int(e22['psd_lead']), tag + ': kenh PSD khac eval_22'
    x250, res250, _ = prep[psd_lead]
    raw1000 = np.asarray(chans[psd_lead], float)
    del chans, prep

    prob = M.probability_series(net, M.robust_scale(res250).astype(np.float32),
                                M.robust_scale(x250).astype(np.float32), CFG)
    det250 = M.pick_peaks(prob, thr, CFG); det1000 = det250.astype(np.int64) * Q
    ref = M.match_events(det1000, fq1000, FS_IN, TOL_MS)
    d_ref = abs(ref['F1'] - float(e22['model_22']['F1_psd']))
    assert d_ref < 1e-6, tag + ': F1 khac eval_22'

    det_s, dm, rm = greedy_match(det1000, fq1000, TOL_MS / 1000.0 * FS_IN)
    assert int(rm.sum()) == ref['TP']

    mat_s = M.detect_maternal_qrs(x250, CFG) / FS
    ds = det250 / FS
    if len(mat_s) > 1 and len(ds):
        j = np.clip(np.searchsorted(mat_s, ds), 1, len(mat_s) - 1)
        dd = np.minimum(np.abs(ds - mat_s[j - 1]), np.abs(ds - mat_s[j]))
        lock = float(np.mean(dd <= TOL_MS / 1000.0))
    else:
        lock = float('nan')

    n_seg = len(res250) // SEG; rows = []
    for k in range(n_seg):
        a, bb = k * SEG, (k + 1) * SEG; a4, b4 = a * Q, bb * Q
        gsel = (fq1000 >= a4) & (fq1000 < b4)
        dsel = (det_s >= a4) & (det_s < b4)
        TP = int(rm[gsel].sum()); FN = int(gsel.sum()) - TP; FP = int((~dm[dsel]).sum())
        den = 2 * TP + FP + FN
        F1 = 200.0 * TP / den if den else float('nan')
        det_rel = det250[(det250 >= a) & (det250 < bb)] - a
        f = fsqi.classical_features(res250[a:bb], FS, det_rel, raw1000[a4:b4], FS_IN)
        pseg = prob[a:bb]
        f['peak_prob_mean'] = float(np.mean(pseg[det_rel])) if len(det_rel) else 0.0
        f['prob_max'] = float(pseg.max())
        row = dict(seg=k, t0_s=a / FS, n_gt=int(gsel.sum()), TP=TP, FP=FP, FN=FN, F1=F1,
                   has_gt=bool(gsel.any()))
        row.update({c: float(f[c]) for c in FEATURES})
        rows.append(row)

    out = dict(record=tag, group=group_of(tag), fold=int(e22['fold']), checkpoint=os.path.basename(ck),
               threshold=thr, psd_lead=int(psd_lead), duration_s=dur, seg_s=SEG_S, n_seg=n_seg,
               F1_record=ref['F1'], Se_record=ref['Se'], PPV_record=ref['PPV'],
               F1_eval22=float(e22['model_22']['F1_psd']), F1_check_absdiff=d_ref,
               n_ref=int(len(fq1000)), n_det=int(len(det1000)), maternal_lock=lock,
               features=FEATURES, rows=rows,
               det_s=[float(v) for v in (det1000 / FS_IN)], ref_s=[float(v) for v in (fq1000 / FS_IN)],
               runtime_s=time.time() - t0)
    p = os.path.join(out_dir, 'gate22_feat_' + tag + '.json')
    json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    print('%-7s fold %s kenh %d F1 %6.2f (eval_22 %6.2f) doan %d (%d co nhip) lock %.3f %5.1fs'
          % (tag, fold, psd_lead, ref['F1'], float(e22['model_22']['F1_psd']), n_seg,
             sum(r['has_gt'] for r in rows), lock, time.time() - t0), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--subjects', default='')
    ap.add_argument('--out', default=os.path.join(HERE, 'gate22_cache'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tags = a.subjects.split(',') if a.subjects else sorted(EVAL22['subjects'])
    for t in tags:
        run(t.strip(), a.out)
