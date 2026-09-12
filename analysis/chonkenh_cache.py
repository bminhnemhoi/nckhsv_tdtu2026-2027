# -*- coding: utf-8 -*-
"""
chonkenh_cache.py -- Buoc 1 cua M5: tinh va luu, voi MOI KENH cua moi ban ghi,
    (i) chuoi phat hien cua mo hinh, (ii) 12 SQI co dien tung doan 4 s (KHONG nhin thay nhan),
    (iii) diem PSD mu nhan, (iv) diem F1 that (CHI de danh gia, khong bao gio dua vao quy tac).

Hai canh:
  --arm cinc : 75 ban ghi CinC 2013 set-a, mo hinh fetalqrs_tcn_22_production.pt (zero-shot)
  --arm s22  : 22 chu the Silesia/ADFECGDB, moi chu the dung checkpoint FOLD khong chua chu the do

Kiem chung bat buoc: F1 tung kenh phai trung voi benchmark_dpss/eval_cinc75.json (canh cinc)
hoac benchmark_dpss/eval_22.json (canh s22) den 1e-6. Neu lech -> dung chuong trinh.

Chay: python analysis/chonkenh_cache.py --arm cinc
      python analysis/chonkenh_cache.py --arm s22
Ket qua: analysis/chonkenh_cache/<arm>_<tag>.json
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, argparse, importlib.util, gc
import numpy as np, torch, wfdb
from scipy import signal as sg
torch.set_num_threads(1)

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss')); sys.path.insert(0, os.path.join(ROOT, 'fsqi'))
from _paths import cinc2013_dir, adfecgdb_dir
import fsqi


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


M = _load('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py')); CFG = M.CFG
FS = CFG['fs']; FS_IN = CFG['fs_in']; Q = FS_IN // FS
SEG = int(4.0 * FS); TOL_MS = 50; FHR_BAND = (1.8, 3.0)
FEATURES = list(fsqi.CLASSICAL_KEYS) + ['peak_prob_mean', 'prob_max']
CACHE = os.path.join(HERE, 'chonkenh_cache')
CKDIR = os.path.join(ROOT, 'model', 'checkpoints')


def psd_score(x250, fs=FS):
    e = np.abs(sg.hilbert(x250 - np.mean(x250))); e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def load_net(path):
    b = torch.load(path, map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
    return net, float(b['threshold']), b


def per_lead(net, thr, raw1000, ref1000):
    """-> dict cho mot kenh"""
    x250 = M.preprocess(raw1000, FS_IN, CFG)
    res250, _ = M.cancel_maternal(x250, CFG)
    prob = M.probability_series(net, M.robust_scale(res250).astype(np.float32),
                                M.robust_scale(x250).astype(np.float32), CFG)
    det250 = M.pick_peaks(prob, thr, CFG); det1000 = det250.astype(np.int64) * Q
    sc = M.match_events(det1000, ref1000, FS_IN, TOL_MS)
    n_seg = len(res250) // SEG
    rows = []
    for k in range(n_seg):
        a, b = k * SEG, (k + 1) * SEG
        det_rel = det250[(det250 >= a) & (det250 < b)] - a
        f = fsqi.classical_features(res250[a:b], FS, det_rel, np.asarray(raw1000, float)[a * Q:b * Q], FS_IN)
        ps = prob[a:b]
        f['peak_prob_mean'] = float(np.mean(ps[det_rel])) if len(det_rel) else 0.0
        f['prob_max'] = float(ps.max())
        rows.append([float(f[c]) for c in FEATURES])
    out = dict(psd=psd_score(res250), n_seg=int(n_seg),
               det_s=[round(float(v), 4) for v in (det1000 / FS_IN)],
               seg_feat=rows,
               F1=float(sc['F1']), Se=float(sc['Se']), PPV=float(sc['PPV']),
               TP=int(sc['TP']), FP=int(sc['FP']), FN=int(sc['FN']),
               jitter_ms=float(sc['jitter_ms']) if np.isfinite(sc['jitter_ms']) else None,
               n_det=int(len(det1000)))
    del prob, x250, res250
    return out


# ------------------------------------------------------------------ canh CinC
def run_cinc(limit=0):
    D = cinc2013_dir(); assert D is not None, 'khong tim thay CinC 2013'
    ref = {r['record']: r for r in json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'eval_cinc75.json'),
                                                 encoding='utf-8'))['records']}
    recs = sorted({f[:-4] for f in os.listdir(D) if f.endswith('.dat')
                   and os.path.isfile(os.path.join(D, f[:-4] + '.fqrs'))})
    if limit:
        recs = recs[:limit]
    net, thr, _ = load_net(os.path.join(CKDIR, 'fetalqrs_tcn_22_production.pt'))
    print('CinC: %d ban ghi, nguong %.2f' % (len(recs), thr), flush=True)
    for i, rec in enumerate(recs, 1):
        p = os.path.join(CACHE, 'cinc_%s.json' % rec)
        if os.path.isfile(p):
            print('[%2d] %s [cache]' % (i, rec), flush=True); continue
        t0 = time.time()
        r_ = wfdb.rdrecord(os.path.join(D, rec)); ann = wfdb.rdann(os.path.join(D, rec), 'fqrs')
        fs0 = r_.fs; gt = (np.asarray(ann.sample, float) * (1000.0 / fs0)).round().astype(int)
        leads = {}
        for lead in range(min(4, r_.p_signal.shape[1])):
            s = np.nan_to_num(r_.p_signal[:, lead])
            if fs0 != 1000:
                s = sg.resample_poly(s, 1000, int(fs0))
            leads[str(lead)] = per_lead(net, thr, s, gt)
            got = leads[str(lead)]['F1']; want = float(ref[rec]['m22']['per_lead'][str(lead)]['F1'])
            assert abs(got - want) < 1e-6, '%s kenh %d: F1 %.6f != eval_cinc75 %.6f' % (rec, lead, got, want)
        dur = float(r_.p_signal.shape[0] / fs0)
        out = dict(arm='cinc', record=rec, group='CinC2013', duration_s=dur, fs=float(fs0),
                   checkpoint='fetalqrs_tcn_22_production.pt', threshold=thr,
                   features=FEATURES, ref_s=[round(float(v), 4) for v in (gt / FS_IN)],
                   n_ref=int(len(gt)), bad_annotation=bool(ref[rec]['bad_annotation']),
                   leads=leads, runtime_s=time.time() - t0)
        json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        print('[%2d/%d] %s F1 %s  %.1fs' % (i, len(recs), rec,
              ' '.join('%6.2f' % leads[str(l)]['F1'] for l in range(4)), time.time() - t0), flush=True)
        del r_, leads
        gc.collect()


# ------------------------------------------------------------------ canh 22 chu the
def run_s22(limit=0):
    import mne
    L = _load('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))
    E = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json'), encoding='utf-8'))['subjects']
    tags = sorted(E)
    if limit:
        tags = tags[:limit]
    for i, tag in enumerate(tags, 1):
        p = os.path.join(CACHE, 's22_%s.json' % tag)
        if os.path.isfile(p):
            print('[%2d] %s [cache]' % (i, tag), flush=True); continue
        t0 = time.time(); e = E[tag]
        fold = '%02d' % int(e['fold'])
        net, thr, blob = load_net(os.path.join(CKDIR, 'fetalqrs_tcn_22_fold_%s.pt' % fold))
        assert tag in blob['test_subjects'], '%s khong o test_subjects fold %s -> RO RI' % (tag, fold)
        if tag.startswith('r'):
            D = adfecgdb_dir()
            raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
            sig = raw.get_data()
            gt = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, int)
            chans = {l: sig[l] for l in (1, 2, 3, 4)}; dur = float(sig.shape[1] / 1000.0)
            group = 'PhysioNet'; del raw, sig
        else:
            sig, _, mt = L.load(tag)
            gt = np.asarray(mt['fqrs_all'], int)
            chans = {l: sig[l - 1] for l in (1, 2, 3, 4)}; dur = float(mt['duration_s'])
            group = tag[:2]; del sig
        leads = {}
        for l in (1, 2, 3, 4):
            leads[str(l)] = per_lead(net, thr, chans[l], gt)
            got = leads[str(l)]['F1']; want = float(e['model_22']['per_lead']['A%d' % l]['F1'])
            assert abs(got - want) < 1e-6, '%s kenh %d: F1 %.6f != eval_22 %.6f' % (tag, l, got, want)
        psd_lead = max((1, 2, 3, 4), key=lambda l: leads[str(l)]['psd'])
        assert psd_lead == int(e['psd_lead']), '%s: kenh PSD %d != eval_22 %d' % (tag, psd_lead, e['psd_lead'])
        out = dict(arm='s22', record=tag, group=group, duration_s=dur, fs=1000.0,
                   checkpoint='fetalqrs_tcn_22_fold_%s.pt' % fold, threshold=thr, fold=int(e['fold']),
                   features=FEATURES, ref_s=[round(float(v), 4) for v in (gt / FS_IN)],
                   n_ref=int(len(gt)), bad_annotation=False,
                   label=e['meta']['label'], leads=leads, runtime_s=time.time() - t0)
        json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        print('[%2d/%d] %-6s fold %s F1 %s  %.1fs' % (i, len(tags), tag, fold,
              ' '.join('%6.2f' % leads[str(l)]['F1'] for l in (1, 2, 3, 4)), time.time() - t0), flush=True)
        del chans, leads
        gc.collect()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True, choices=['cinc', 's22'])
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    t0 = time.time()
    (run_cinc if a.arm == 'cinc' else run_s22)(a.limit)
    print('DONE %s %.1f phut' % (a.arm, (time.time() - t0) / 60), flush=True)
