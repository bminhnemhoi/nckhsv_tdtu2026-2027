# -*- coding: utf-8 -*-
"""
train_gate.py -- huan luyen BO PHAN LOAI DOAN XAU (cong tin cay hoc duoc) thay cho luat cung cua den tin cay.

Cau hinh GIONG HET eval_fsqi.py nhom "classical" (nhom da cho AUROC 0,929 tren CinC trong results.json):
  * dac trung : 12 chi so co dien = fsqi.CLASSICAL_KEYS (10) + peak_prob_mean + prob_max  (KHONG topo)
  * doan      : 4 s khong chong (1000 mau @250 Hz), chi giu doan co it nhat 1 nhip nhan
  * nhan xau  : F1 doan < 80 (ghep mot-doi-mot +/-50 ms tren TOAN ban ghi roi gan TP/FN/FP vao doan)
  * learner   : HistGradientBoostingClassifier(max_depth=3, max_iter=200, learning_rate=0.05,
                class_weight='balanced', random_state=0); NaN -> trung vi cua tap huan luyen
  * huan luyen: ADFECGDB 5 ban ghi x 4 kenh (checkpoint fold dung -> khong ro ri), 1500 doan
  * kiem tra  : CinC 2013 set-a a01-a10 x 4 kenh (checkpoint production), 600 doan -> AUROC phai ~0,929

Hieu chuan nguong HAI MUC chi tren ADFECGDB, bang xac suat NGOAI FOLD (LORO-CV noi bo, khong nhin CinC):
  q1 = phan vi 85 cua p_bad ngoai fold  -> doan 'xanh' neu p_bad <  q1   (~85 % doan ADFECGDB)
  q2 = phan vi 95 cua p_bad ngoai fold  -> doan 'do'   neu p_bad >  q2   (~ 5 % doan ADFECGDB)
  con lai 'vang'.
Muc ban ghi (gate.record_confidence): score = 1 - trung binh p_bad;
  level = 'thap' neu ti le doan do > 30 %; 'cao' neu ti le doan xanh > 70 %; con lai 'trung_binh';
  cong bam me >= 60 % ghi de -> 'thap'.

Dau ra (fsqi/):
  gate_classical.pkl      -- dict(model, features, medians, q1, q2, record_rule, sklearn_version, ...)
  gate_meta.json          -- danh sach dac trung, phien ban sklearn, nguong, ti le hieu chuan, AUROC kiem tra
  gate_segments.csv       -- 12 dac trung + F1 doan + p_bad (ngoai fold cho ADFECGDB, production cho CinC)
  train_gate_results.json -- moi con so trong log
  train_gate_log.txt

Chay:  set PYTHONIOENCODING=utf-8 & python fsqi\\train_gate.py            (~2 phut, RAM < 1 GB)
       python fsqi\\train_gate.py --from-csv   (che do nhanh: lay dac trung tu fsqi/segments.csv cua eval_fsqi.py)
"""
import os, sys, json, time, datetime, argparse, pickle, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_v] = '1'
import numpy as np
import torch
torch.set_num_threads(2)
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
import fsqi
from _paths import adfecgdb_dir, cinc2013_dir
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG = M.CFG

FS = CFG['fs']; SEG_S = 4.0; SEG = int(SEG_S * FS); Q = 1000 // FS
TOL_MS = CFG['tolerance_ms']; BAD_THR = 80.0; SEED = 0
FEATURES = list(fsqi.CLASSICAL_KEYS) + ['peak_prob_mean', 'prob_max']      # dung thu tu nhom 'classical' cua eval_fsqi
GB_PARAMS = dict(max_depth=3, max_iter=200, learning_rate=0.05, class_weight='balanced', random_state=SEED)
Q_GREEN, Q_RED = 0.85, 0.95                     # phan vi hieu chuan tren ADFECGDB (ngoai fold)
RECORD_RULE = dict(red_frac_thr=0.30, green_frac_thr=0.70, maternal_lock=0.60)
ADFECGDB_RECS = ['r01', 'r04', 'r07', 'r08', 'r10']
_LOG = None


def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True)
    if _LOG: _LOG.write(s + '\n'); _LOG.flush()


# ------------------------------------------------------------------ trich dac trung (giong eval_fsqi.process_lead, bo topo)
def greedy_match(det, ref, tol):
    ref = np.asarray(ref, float); det = np.sort(np.asarray(det, float))
    used = np.zeros(len(ref), bool); dm = np.zeros(len(det), bool)
    for i, d in enumerate(det):
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (~used))[0]
        if len(ok):
            used[ok[int(np.argmin(dd[ok]))]] = True; dm[i] = True
    return det, dm, used


def process_lead(ds, rec, lead, sig1000, gt1000, net, thr, rows):
    x250 = M.preprocess(sig1000, 1000, CFG); res, _ = M.cancel_maternal(x250, CFG)
    prob = M.probability_series(net, M.robust_scale(res).astype(np.float32),
                                M.robust_scale(x250).astype(np.float32), CFG)
    det250 = M.pick_peaks(prob, thr, CFG); det1000 = det250.astype(np.int64) * Q
    det_s, dm, rm = greedy_match(det1000, gt1000, TOL_MS / 1000 * 1000)
    ref = M.match_events(det1000, gt1000, 1000, TOL_MS)
    assert int(rm.sum()) == ref['TP'], 'ghep toan ban ghi khong khop M.match_events'
    n_seg = len(res) // SEG; n_skip = 0; t_feat = 0.0
    for k in range(n_seg):
        a, b = k * SEG, (k + 1) * SEG; a4, b4 = a * Q, b * Q
        gsel = (gt1000 >= a4) & (gt1000 < b4)
        if not gsel.any():
            n_skip += 1; continue
        dsel = (det_s >= a4) & (det_s < b4)
        TP = int(rm[gsel].sum()); FN = int(gsel.sum()) - TP; FP = int((~dm[dsel]).sum())
        F1 = 200.0 * TP / (2 * TP + FP + FN)
        det_rel = det250[(det250 >= a) & (det250 < b)] - a
        t0 = time.perf_counter()
        f = fsqi.classical_features(res[a:b], FS, det_rel, sig1000[a4:b4], 1000)
        pseg = prob[a:b]
        f['peak_prob_mean'] = float(np.mean(pseg[det_rel])) if len(det_rel) else 0.0
        f['prob_max'] = float(pseg.max())
        t_feat += time.perf_counter() - t0
        row = dict(dataset=ds, rec=rec, lead=int(lead), seg=k, t0_s=a / FS, n_gt=int(gsel.sum()),
                   TP=TP, FP=FP, FN=FN, F1=F1, lead_F1=ref['F1'])
        row.update({k2: float(f[k2]) for k2 in FEATURES})
        rows.append(row)
    del x250, res, prob
    return ref['F1'], n_seg, n_skip, t_feat * 1000.0 / max(n_seg - n_skip, 1)


def extract_all(rows):
    import mne, wfdb
    from scipy import signal as sg
    RAW = adfecgdb_dir(); per = dict(adfecgdb={}, cinc={})
    for rec in ADFECGDB_RECS:
        b = torch.load(os.path.join(ROOT, 'model', 'checkpoints', f'fetalqrs_tcn_fold_{rec}.pt'),
                       map_location='cpu', weights_only=False)
        assert b['test_record'] == rec, 'checkpoint fold sai ban ghi'
        net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval(); thr = float(b['threshold'])
        sig = mne.io.read_raw_edf(os.path.join(RAW, rec + '.edf'), preload=True, verbose=False).get_data()
        gt = np.asarray(wfdb.rdann(os.path.join(RAW, rec), 'edf.qrs').sample, int)
        per['adfecgdb'][rec] = {}
        for lead in (1, 2, 3, 4):
            t0 = time.time()
            F1, n_seg, n_skip, ms = process_lead('adfecgdb', rec, lead, sig[lead], gt, net, thr, rows)
            per['adfecgdb'][rec][lead] = F1
            log(f'  ADFECGDB {rec} kenh {lead}: F1 ban ghi {F1:6.2f}  doan {n_seg - n_skip}/{n_seg}  thr {thr:.2f}  '
                f'{time.time() - t0:5.1f}s  (dac trung {ms:.1f} ms/doan)')
        del sig, net
    D = cinc2013_dir(); assert D is not None, 'khong thay CinC 2013'
    recs = sorted({f[:-4] for f in os.listdir(D) if f.endswith('.dat')})[:10]
    b = torch.load(os.path.join(ROOT, 'model', 'checkpoints', 'fetalqrs_tcn_production.pt'),
                   map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval(); thr = float(b['threshold'])
    for rec in recs:
        r_ = wfdb.rdrecord(os.path.join(D, rec)); ann = wfdb.rdann(os.path.join(D, rec), 'fqrs')
        fs0 = r_.fs; gt = (ann.sample * (1000.0 / fs0)).round().astype(int)
        per['cinc'][rec] = {}
        for lead in range(min(4, r_.p_signal.shape[1])):
            s = np.nan_to_num(r_.p_signal[:, lead])
            if fs0 != 1000: s = sg.resample_poly(s, 1000, int(fs0))
            t0 = time.time()
            F1, n_seg, n_skip, ms = process_lead('cinc', rec, lead, s, gt, net, thr, rows)
            per['cinc'][rec][lead] = F1
            log(f'  CinC {rec} kenh {lead}: F1 ban ghi {F1:6.2f}  doan {n_seg - n_skip}/{n_seg}  thr {thr:.2f}  '
                f'{time.time() - t0:5.1f}s  (dac trung {ms:.1f} ms/doan)')
        del r_
    return per


def rows_from_csv(path):
    """che do nhanh: doc lai dac trung tu segments.csv cua eval_fsqi.py (cung pipeline, cung fold)"""
    rows = []
    with open(path, encoding='utf-8') as f:
        keys = f.readline().strip().split(',')
        for line in f:
            v = line.strip().split(',')
            d = dict(zip(keys, v))
            row = dict(dataset=d['dataset'], rec=d['rec'], lead=int(d['lead']), seg=int(d['seg']), t0_s=float(d['t0_s']),
                       n_gt=int(d['n_gt']), TP=int(d['TP']), FP=int(d['FP']), FN=int(d['FN']), F1=float(d['F1']), lead_F1=float(d['lead_F1']))
            row.update({k: float(d[k]) for k in FEATURES})
            rows.append(row)
    return rows


def compare_with_csv(rows, path):
    """doi chieu dac trung vua tinh voi segments.csv (tai lap): tra ve (so doan doi chieu, sai lech tuyet doi lon nhat)"""
    if not os.path.isfile(path): return None
    ref = {(r['dataset'], r['rec'], r['lead'], r['seg']): r for r in rows_from_csv(path)}
    n = 0; mx = 0.0; worst = None
    for r in rows:
        k = (r['dataset'], r['rec'], r['lead'], r['seg'])
        if k not in ref: continue
        n += 1
        for f in FEATURES + ['F1']:
            a, b = r[f], ref[k][f]
            if np.isnan(a) and np.isnan(b): continue
            d = abs(a - b)
            if not (d <= mx): mx = float(d); worst = (k, f, a, b)
    return dict(n_compared=n, max_abs_diff=mx, worst=worst)


# ------------------------------------------------------------------ bo phan loai
def make_X(rows):
    return np.array([[r[k] for k in FEATURES] for r in rows], float)


def impute(X, med=None):
    if med is None:
        med = np.nanmedian(X, 0); med = np.where(np.isfinite(med), med, 0.0)
    return np.where(np.isfinite(X), X, med), med


def fit(Xtr, ytr):
    Xtr, med = impute(Xtr)
    clf = HistGradientBoostingClassifier(**GB_PARAMS); clf.fit(Xtr, ytr)
    return clf, med


def predict(clf, med, X):
    X, _ = impute(X, med)
    return clf.predict_proba(X)[:, 1]


def main():
    global _LOG
    ap = argparse.ArgumentParser()
    ap.add_argument('--from-csv', action='store_true', help='lay dac trung tu fsqi/segments.csv thay vi tinh lai')
    ap.add_argument('--out', default=HERE)
    a = ap.parse_args()
    T0 = time.time(); os.makedirs(a.out, exist_ok=True)
    _LOG = open(os.path.join(a.out, 'train_gate_log.txt'), 'w', encoding='utf-8')
    log(f'train_gate.py  {datetime.datetime.now():%Y-%m-%d %H:%M}  torch {torch.__version__} ({torch.get_num_threads()} luong)  '
        f'sklearn {sklearn.__version__}  numpy {np.__version__}')
    log(f'dac trung ({len(FEATURES)}): {FEATURES}')
    log(f'GB: {GB_PARAMS}; nhan xau = F1 doan < {BAD_THR:.0f}; doan {SEG_S:.0f} s @ {FS} Hz; dung sai +/-{TOL_MS} ms')

    # ---------------------------------------------------------- [1] dac trung
    csv_path = os.path.join(HERE, 'segments.csv'); per = None; repro = None
    if a.from_csv:
        log(f'\n[1] Che do nhanh: doc dac trung tu {csv_path}')
        rows = rows_from_csv(csv_path)
    else:
        log('\n[1] Trich 12 chi so co dien + F1 doan (tinh lai tu dau, KHONG topo)')
        rows = []; per = extract_all(rows)
        repro = compare_with_csv(rows, csv_path)
        if repro:
            log(f'  doi chieu voi segments.csv cua eval_fsqi.py: {repro["n_compared"]} doan, sai lech tuyet doi lon nhat '
                f'{repro["max_abs_diff"]:.3e}' + (f'  (tai {repro["worst"]})' if repro['worst'] else ''))
    ad = [r for r in rows if r['dataset'] == 'adfecgdb']; ci = [r for r in rows if r['dataset'] == 'cinc']
    y_ad = np.array([r['F1'] < BAD_THR for r in ad]); y_ci = np.array([r['F1'] < BAD_THR for r in ci])
    X_ad, X_ci = make_X(ad), make_X(ci)
    log(f'  so doan: ADFECGDB {len(ad)} (xau {int(y_ad.sum())} = {y_ad.mean() * 100:.1f}%), '
        f'CinC {len(ci)} (xau {int(y_ci.sum())} = {y_ci.mean() * 100:.1f}%)')
    if per:
        log(f'  macro F1 ban ghi x kenh (kiem tra pipeline): ADFECGDB {np.mean([v for d in per["adfecgdb"].values() for v in d.values()]):.2f}'
            f'  CinC {np.mean([v for d in per["cinc"].values() for v in d.values()]):.2f}')

    # ---------------------------------------------------------- [2] LORO ngoai fold tren ADFECGDB -> hieu chuan nguong
    log('\n[2] LORO-CV noi bo ADFECGDB (chia theo ban ghi) -> xac suat NGOAI FOLD de hieu chuan q1/q2')
    g = np.array([r['rec'] for r in ad]); oof = np.full(len(ad), np.nan); cv_auc = {}
    for rec in ADFECGDB_RECS:
        te = g == rec
        clf, med = fit(X_ad[~te], y_ad[~te]); oof[te] = predict(clf, med, X_ad[te])
        cv_auc[rec] = float(roc_auc_score(y_ad[te], oof[te])) if 0 < y_ad[te].sum() < te.sum() else None
        log(f'  fold {rec}: {int(te.sum())} doan, xau {int(y_ad[te].sum())}, AUROC ngoai fold '
            f'{cv_auc[rec] if cv_auc[rec] is None else round(cv_auc[rec], 3)}')
    assert np.isfinite(oof).all()
    vals = [v for v in cv_auc.values() if v is not None]
    cv_mean = float(np.mean(vals)); oof_auc_pooled = float(roc_auc_score(y_ad, oof))
    log(f'  AUROC ngoai fold: trung binh cac fold {cv_mean:.3f} (results.json classical gb: 0.901), gop 1500 doan {oof_auc_pooled:.3f}')
    q1 = float(np.quantile(oof, Q_GREEN)); q2 = float(np.quantile(oof, Q_RED))
    fr_oof = dict(green=float(np.mean(oof < q1)), red=float(np.mean(oof > q2)))
    fr_oof['yellow'] = 1.0 - fr_oof['green'] - fr_oof['red']
    log(f'  nguong: q1 (phan vi {Q_GREEN * 100:.0f}) = {q1:.4f}, q2 (phan vi {Q_RED * 100:.0f}) = {q2:.4f}')
    log(f'  ti le doan ADFECGDB ngoai fold: xanh {fr_oof["green"] * 100:.1f}%  vang {fr_oof["yellow"] * 100:.1f}%  do {fr_oof["red"] * 100:.1f}%')
    # doan xau roi vao mau nao (ngoai fold)?
    lv_oof = np.where(oof < q1, 'xanh', np.where(oof > q2, 'do', 'vang'))
    conf_oof = {lv: dict(n=int((lv_oof == lv).sum()), n_bad=int(y_ad[lv_oof == lv].sum()),
                         F1_mean=float(np.mean([r['F1'] for r, m in zip(ad, lv_oof == lv) if m])) if (lv_oof == lv).any() else None)
                for lv in ('xanh', 'vang', 'do')}
    for lv, d in conf_oof.items():
        log(f'    doan {lv:5s}: n {d["n"]:4d}, trong do xau {d["n_bad"]:3d}, F1 doan TB {d["F1_mean"]}')

    # ---------------------------------------------------------- [3] mo hinh cuoi (toan bo ADFECGDB) -> kiem tra CinC
    log('\n[3] Mo hinh cuoi: huan luyen tren toan bo 1500 doan ADFECGDB -> kiem tra tren 600 doan CinC (production)')
    clf, med = fit(X_ad, y_ad)
    p_ci = predict(clf, med, X_ci); p_ad_in = predict(clf, med, X_ad)
    auc_ci = float(roc_auc_score(y_ci, p_ci)); ap_ci = float(average_precision_score(y_ci, p_ci))
    log(f'  CinC AUROC {auc_ci:.4f}  AUPRC {ap_ci:.4f}   (results.json classical gb: AUROC 0.9289, AUPRC 0.9265)')
    fr_in = dict(green=float(np.mean(p_ad_in < q1)), red=float(np.mean(p_ad_in > q2)))
    fr_in['yellow'] = 1.0 - fr_in['green'] - fr_in['red']
    log(f'  ti le doan ADFECGDB TRONG MAU (mo hinh cuoi, chi de tham khao): xanh {fr_in["green"] * 100:.1f}%  '
        f'vang {fr_in["yellow"] * 100:.1f}%  do {fr_in["red"] * 100:.1f}%')
    lv_ci = np.where(p_ci < q1, 'xanh', np.where(p_ci > q2, 'do', 'vang'))
    conf_ci = {lv: dict(n=int((lv_ci == lv).sum()), n_bad=int(y_ci[lv_ci == lv].sum()),
                        F1_mean=float(np.mean([r['F1'] for r, m in zip(ci, lv_ci == lv) if m])) if (lv_ci == lv).any() else None)
               for lv in ('xanh', 'vang', 'do')}
    log('  CinC theo mau doan (nguong tu ADFECGDB, khong chinh):')
    for lv, d in conf_ci.items():
        log(f'    doan {lv:5s}: n {d["n"]:4d}, trong do xau {d["n_bad"]:3d}, F1 doan TB {None if d["F1_mean"] is None else round(d["F1_mean"], 2)}')
    # do quan trong dac trung (permutation, tren CinC -- chi de dien giai, khong dung de chon gi)
    rng = np.random.default_rng(SEED); imp = {}
    Xc, _ = impute(X_ci, med)
    for j, k in enumerate(FEATURES):
        Xp = Xc.copy(); Xp[:, j] = Xp[rng.permutation(len(Xp)), j]
        imp[k] = float(auc_ci - roc_auc_score(y_ci, clf.predict_proba(Xp)[:, 1]))
    log('  giam AUROC CinC khi hoan vi tung dac trung: ' + ', '.join(f'{k} {v:+.3f}' for k, v in sorted(imp.items(), key=lambda t: -t[1])))

    # ---------------------------------------------------------- [4] luu
    gate = dict(model=clf, features=FEATURES, medians=[float(v) for v in med], q1=q1, q2=q2,
                record_rule=RECORD_RULE, bad_threshold_F1=BAD_THR, seg_s=SEG_S, fs=FS,
                sklearn_version=sklearn.__version__, trained_on='ADFECGDB r01,r04,r07,r08,r10 x 4 kenh (checkpoint fold)',
                date=str(datetime.datetime.now()))
    pkl = os.path.join(a.out, 'gate_classical.pkl')
    with open(pkl, 'wb') as f: pickle.dump(gate, f, protocol=4)
    meta = dict(date=gate['date'], features=FEATURES, n_features=len(FEATURES), sklearn_version=sklearn.__version__,
                numpy_version=np.__version__, python_version=sys.version.split()[0],
                learner='HistGradientBoostingClassifier', learner_params=GB_PARAMS, nan_imputation='trung vi tap huan luyen',
                medians=dict(zip(FEATURES, gate['medians'])),
                training=dict(dataset='ADFECGDB', records=ADFECGDB_RECS, checkpoints='fold (test_record = ban ghi)', n_segments=len(ad),
                              n_bad=int(y_ad.sum()), frac_bad=float(y_ad.mean()), bad_threshold_F1=BAD_THR, seg_s=SEG_S, fs=FS,
                              features_from='segments.csv (eval_fsqi.py)' if a.from_csv else 'tinh lai tu dau'),
                thresholds=dict(q1=q1, q2=q2, quantiles=dict(q1=Q_GREEN, q2=Q_RED), calibrated_on='ADFECGDB, xac suat ngoai fold (LORO)',
                                rule='xanh neu p_bad < q1; do neu p_bad > q2; con lai vang'),
                calibration_fractions=dict(adfecgdb_out_of_fold=fr_oof, adfecgdb_in_sample_final_model=fr_in),
                segment_levels=dict(adfecgdb_out_of_fold=conf_oof, cinc_production=conf_ci),
                record_rule=dict(**RECORD_RULE, score='1 - trung binh p_bad',
                                 rule='thap neu ti le doan do > red_frac_thr; cao neu ti le doan xanh > green_frac_thr; con lai trung_binh; '
                                      'bam me >= maternal_lock -> thap (ghi de)'),
                checks=dict(cv_auroc_adfecgdb_folds=cv_auc, cv_auroc_adfecgdb_mean=cv_mean, oof_auroc_pooled=oof_auc_pooled,
                            cinc_auroc=auc_ci, cinc_auprc=ap_ci, cinc_n_segments=len(ci), cinc_n_bad=int(y_ci.sum()),
                            reference_results_json=dict(classical_gb_auroc_cinc=0.9288775589718472, cv_auroc_adfecgdb=0.9012866017279672),
                            reproduced=bool(abs(auc_ci - 0.9288775589718472) < 0.01),
                            feature_reproducibility_vs_segments_csv=repro),
                permutation_importance_cinc_delta_auroc=imp, runtime_min=(time.time() - T0) / 60)
    json.dump(meta, open(os.path.join(a.out, 'gate_meta.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    with open(os.path.join(a.out, 'gate_segments.csv'), 'w', encoding='utf-8') as f:
        keys = ['dataset', 'rec', 'lead', 'seg', 't0_s', 'n_gt', 'TP', 'FP', 'FN', 'F1', 'lead_F1'] + FEATURES + ['p_bad', 'p_bad_kind', 'level']
        f.write(','.join(keys) + '\n')
        for r, p, lv in zip(ad, oof, lv_oof):
            f.write(','.join(str(r[k]) for k in keys[:-3]) + f',{p},oof,{lv}\n')
        for r, p, lv in zip(ci, p_ci, lv_ci):
            f.write(','.join(str(r[k]) for k in keys[:-3]) + f',{p},production,{lv}\n')
    res = dict(meta=meta, pipeline_check=per)
    json.dump(res, open(os.path.join(a.out, 'train_gate_results.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    log(f'\nda ghi gate_classical.pkl, gate_meta.json, gate_segments.csv, train_gate_results.json, train_gate_log.txt '
        f'({(time.time() - T0) / 60:.1f} phut)')
    log(f'TAI LAP AUROC CinC: {"DAT" if meta["checks"]["reproduced"] else "KHONG DAT"} ({auc_ci:.4f} so voi 0.9289)')


if __name__ == '__main__':
    main()
