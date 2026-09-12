# -*- coding: utf-8 -*-
"""
gate22_cinc.py -- KIEM CHUNG NGOAI cho cong 22 ca: ap thang cong (huan luyen tren TOAN BO 22 chu the
Silesia/ADFECGDB) len 75 ban ghi CinC 2013 set-a, la du lieu HOAN TOAN doc lap (khac may do, khac
nguoi chu thich, 60 s/ban ghi, mo hinh production_22 zero-shot).

Cong KHONG duoc hieu chuan lai gi tren CinC. Cau hoi: diem tin cay co xep hang dung cac ban ghi
ma mo hinh that su lam kem khong?

Chay:  python analysis/gate22_cinc.py
Ket qua: analysis/gate22_cinc.json, analysis/gate22_cinc_log.txt
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, glob, datetime, importlib.util
import numpy as np, torch, wfdb
from scipy import signal as sg
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
torch.set_num_threads(2)

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss')); sys.path.insert(0, os.path.join(ROOT, 'fsqi'))
from _paths import cinc2013_dir
import fsqi


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


M = _load('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py')); CFG = M.CFG
FS = CFG['fs']; SEG = int(4.0 * FS); Q = 4; TOL_MS = 50; BAD_THR = 80.0; SEED = 0
FHR_BAND = (1.8, 3.0)
GB = dict(max_depth=3, max_iter=200, learning_rate=0.05, class_weight='balanced', random_state=SEED)
_LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); _LOG.append(s)


def psd_score(x250):
    e = np.abs(sg.hilbert(x250 - np.mean(x250))); e = e - np.mean(e)
    f, P = sg.welch(e, fs=FS, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def main():
    T0 = time.time()
    # ------------------------------------------------- cong cuoi (toan bo 22 chu the)
    X, y = [], []
    feats = None
    for p in sorted(glob.glob(os.path.join(HERE, 'gate22_cache', 'gate22_feat_*.json'))):
        d = json.load(open(p, encoding='utf-8')); feats = d['features']
        for r in d['rows']:
            if r['has_gt']:
                X.append([r[c] for c in feats]); y.append(r['F1'] < BAD_THR)
    X = np.array(X, float); y = np.array(y, bool)
    med = np.nanmedian(X, 0); med = np.where(np.isfinite(med), med, 0.0)
    clf = HistGradientBoostingClassifier(**GB); clf.fit(np.where(np.isfinite(X), X, med), y)
    log('cong cuoi: huan luyen tren %d doan cua 22 chu the (xau %d), %d dac trung' % (len(y), int(y.sum()), len(feats)))

    # ------------------------------------------------- CinC 75
    D = cinc2013_dir(); assert D is not None
    recs = sorted({f[:-4] for f in os.listdir(D) if f.endswith('.dat')})
    e75 = {r['record']: r for r in json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'eval_cinc75.json'),
                                                  encoding='utf-8'))['records']}
    b = torch.load(os.path.join(ROOT, 'model', 'checkpoints', 'fetalqrs_tcn_22_production.pt'),
                   map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval(); thr = float(b['threshold'])
    log('mo hinh: fetalqrs_tcn_22_production.pt (zero-shot), nguong %.2f; %d ban ghi CinC' % (thr, len(recs)))

    rows = []; segs = []
    for rec in recs:
        r_ = wfdb.rdrecord(os.path.join(D, rec)); ann = wfdb.rdann(os.path.join(D, rec), 'fqrs')
        fs0 = r_.fs; gt = (ann.sample * (1000.0 / fs0)).round().astype(int)
        sigs = {}
        for lead in range(min(4, r_.p_signal.shape[1])):
            s = np.nan_to_num(r_.p_signal[:, lead])
            if fs0 != 1000:
                s = sg.resample_poly(s, 1000, int(fs0))
            x = M.preprocess(s, 1000, CFG); res, _ = M.cancel_maternal(x, CFG)
            sigs[lead] = (s, x, res, psd_score(res))
        lead = max(sigs, key=lambda l: sigs[l][3])
        raw1000, x250, res250, _ = sigs[lead]
        prob = M.probability_series(net, M.robust_scale(res250).astype(np.float32),
                                    M.robust_scale(x250).astype(np.float32), CFG)
        det250 = M.pick_peaks(prob, thr, CFG); det1000 = det250.astype(np.int64) * Q
        sc = M.match_events(det1000, gt, 1000, TOL_MS)
        chk = abs(sc['F1'] - float(e75[rec]['m22']['F1_psd'])) if rec in e75 else None
        n_seg = len(res250) // SEG; P = []
        for k in range(n_seg):
            a, bb = k * SEG, (k + 1) * SEG
            det_rel = det250[(det250 >= a) & (det250 < bb)] - a
            f = fsqi.classical_features(res250[a:bb], FS, det_rel, raw1000[a * Q:bb * Q], 1000)
            ps = prob[a:bb]
            f['peak_prob_mean'] = float(np.mean(ps[det_rel])) if len(det_rel) else 0.0
            f['prob_max'] = float(ps.max())
            v = np.array([[f[c] for c in feats]], float)
            P.append(float(clf.predict_proba(np.where(np.isfinite(v), v, med))[0, 1]))
        P = np.array(P)
        rows.append(dict(record=rec, psd_lead=int(lead), F1=float(sc['F1']),
                         F1_eval_cinc75=float(e75[rec]['m22']['F1_psd']) if rec in e75 else None,
                         F1_check_absdiff=chk, n_seg=int(n_seg), mean_p_bad=float(P.mean()),
                         score=float(1 - P.mean()), frac_p_gt_half=float(np.mean(P > 0.5)),
                         bad_annotation=bool(e75[rec]['bad_annotation']) if rec in e75 else None))
        segs.append(P)
        del r_, sigs, prob
    mx = max(r['F1_check_absdiff'] for r in rows if r['F1_check_absdiff'] is not None)
    log('tai lap F1 muc ban ghi so voi eval_cinc75.json: sai lech tuyet doi lon nhat %.2e' % mx)

    sc = np.array([r['score'] for r in rows]); f1 = np.array([r['F1'] for r in rows])
    rho = spearmanr(sc, f1)
    auc = float(roc_auc_score(f1 < 80.0, -sc))
    log('Spearman(diem tin cay, F1 ban ghi) tren 75 ban ghi CinC = %.3f (p = %.2g)' % (rho.statistic, rho.pvalue))
    log('AUROC muc BAN GHI (phan biet ban ghi F1 < 80): %.3f  (%d/%d ban ghi F1 < 80)'
        % (auc, int((f1 < 80).sum()), len(f1)))

    order = sorted(rows, key=lambda r: -r['score'])
    tot = len(order); curve = []
    log('  %-8s %8s %10s %8s %8s' % ('giu', 'do phu', 'F1 TB giu', '>=90', '<50'))
    for k in range(tot, 4, -5):
        keep = order[:k]
        v = np.array([r['F1'] for r in keep])
        e = dict(n_keep=k, coverage_pct=100.0 * k / tot, F1_mean=float(v.mean()),
                 F1_median=float(np.median(v)), n_ge90=int((v >= 90).sum()), n_lt50=int((v < 50).sum()))
        curve.append(e)
        log('  %-8d %7.1f%% %10.2f %8d %8d' % (k, e['coverage_pct'], e['F1_mean'], e['n_ge90'], e['n_lt50']))

    worst10 = [r['record'] for r in sorted(rows, key=lambda r: r['score'])[:10]]
    trueworst10 = [r['record'] for r in sorted(rows, key=lambda r: r['F1'])[:10]]
    ov = len(set(worst10) & set(trueworst10))
    log('10 ban ghi cong nghi nhat : %s' % ','.join(worst10))
    log('10 ban ghi thuc su te nhat: %s' % ','.join(trueworst10))
    log('trung nhau %d/10' % ov)

    out = dict(ngay=datetime.datetime.now().isoformat(timespec='seconds'),
               mo_ta='kiem chung ngoai: cong huan luyen tren 22 chu the, ap len 75 ban ghi CinC 2013 set-a '
                     '(mo hinh fetalqrs_tcn_22_production.pt, zero-shot, kenh PSD mu nhan)',
               n_records=len(rows), features=feats, gate_trained_on_segments=int(len(y)),
               spearman_score_vs_F1=[float(rho.statistic), float(rho.pvalue)],
               auroc_record_level_F1_lt80=auc, n_F1_lt80=int((f1 < 80).sum()),
               F1_check_max_absdiff=mx, bang=rows, duong_rui_ro_do_phu=curve,
               worst10_theo_cong=worst10, worst10_thuc_te=trueworst10, trung_nhau=ov,
               runtime_min=(time.time() - T0) / 60)
    json.dump(out, open(os.path.join(HERE, 'gate22_cinc.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    open(os.path.join(HERE, 'gate22_cinc_log.txt'), 'w', encoding='utf-8').write('\n'.join(_LOG) + '\n')
    log('da ghi gate22_cinc.json (%.1f phut)' % ((time.time() - T0) / 60))


if __name__ == '__main__':
    main()
