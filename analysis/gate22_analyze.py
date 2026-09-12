# -*- coding: utf-8 -*-
"""
gate22_analyze.py -- Buoc 2 cua A3: HIEU CHUAN LAI CONG TU CHOI CHO MO HINH 22 CA
va tra loi cau hoi "cong co bat duoc ba ban ghi kho (B1_07, B1_06, B2_03) khong?".

Dau vao : analysis/gate22_cache/gate22_feat_<tag>.json  (gate22_features.py)
          baselines/powermf_fair_stats.json             (F1 Power-MF 4 kenh / 1 kenh muc ban ghi)
          baselines/powermf_work/<tag>_powermf.mat      (dinh Power-MF 4 kenh, de cham theo doan)
          baselines/powermf_work/<tag>.mat              (nhan fqrs 1-based da dua vao Octave)
Dau ra  : analysis/gate22_results.json, analysis/GATE22.md, analysis/fig_gate22.png,
          analysis/gate22_segments.csv, analysis/gate22_log.txt

Thiet ke (KHONG RO RI):
  * dac trung: dung 12 SQI co dien cua fsqi (CLASSICAL_KEYS + peak_prob_mean + prob_max).
    KHONG dac trung nao nhin thay nhan.
  * nhan doan xau: F1 doan < 80 (giu nguyen dinh nghia cua train_gate.py).
  * CV: leave-one-SUBJECT-out tren 22 chu the -> moi doan duoc cham boi mot cong
    CHUA TUNG THAY chu the do. Khong co doan nao cua chinh chu the trong tap huan luyen.
  * AUROC bao cao hai kieu: (a) gop tat ca doan (tron lan khac biet GIUA ban ghi voi
    khac biet TRONG ban ghi); (b) TRONG tung ban ghi roi tong hop -- day moi la cau tra loi
    cho "trong mot ban ghi, cong co chi dung doan xau khong".
  * KTC: cluster bootstrap lay mau lai CHU THE (seed 0).
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, glob, datetime
import numpy as np
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from scipy.io import loadmat
from scipy.stats import spearmanr, wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, 'gate22_cache')
PMF_WORK = os.path.join(ROOT, 'baselines', 'powermf_work')

BAD_THR = 80.0; SEED = 0; NBOOT = 10000; NBOOT_SEG = 2000
GB_PARAMS = dict(max_depth=3, max_iter=200, learning_rate=0.05, class_weight='balanced', random_state=SEED)
HARD = ['B1_07', 'B1_06', 'B2_03']
EPOCH_S = 3.75; RR_LO, RR_HI = 0.25, 0.75; MIN_RR_EPOCH = 2; TOL_S = 0.050
_LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); _LOG.append(s)


# ============================================================ nap
def load_all():
    recs = {}
    for p in sorted(glob.glob(os.path.join(CACHE, 'gate22_feat_*.json'))):
        d = json.load(open(p, encoding='utf-8'))
        recs[d['record']] = d
    assert len(recs) == 22, 'can du 22 chu the, dang co %d' % len(recs)
    return recs


def greedy_match(det, ref, tol):
    ref = np.asarray(ref, float); det = np.sort(np.asarray(det, float))
    used = np.zeros(len(ref), bool); dm = np.zeros(len(det), bool)
    for i, d in enumerate(det):
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (~used))[0]
        if len(ok):
            used[ok[int(np.argmin(dd[ok]))]] = True; dm[i] = True
    return det, dm, used


def pmf_segments(tag, ref_s, n_seg, seg_s=4.0):
    """TP/FP/FN cua Power-MF 4 kenh tren tung doan 4 s, dung CUNG nhan va cung bo ghep."""
    f = os.path.join(PMF_WORK, tag + '_powermf.mat')
    g = os.path.join(PMF_WORK, tag + '.mat')
    if not (os.path.isfile(f) and os.path.isfile(g)):
        return None
    det = np.asarray(loadmat(f)['fPeaks'], float).ravel()
    ref_oct = np.asarray(loadmat(g)['fqrs'], float).ravel() - 1.0     # 1-based -> 0-based, don vi mau @1000 Hz
    ref_mine = np.round(np.asarray(ref_s, float) * 1000.0)
    chk = dict(n_ref_octave=int(ref_oct.size), n_ref_mine=int(ref_mine.size),
               max_abs_diff=float(np.max(np.abs(np.sort(ref_oct) - np.sort(ref_mine)))) if ref_oct.size == ref_mine.size else None)
    if ref_oct.size != ref_mine.size or chk['max_abs_diff'] > 0.5:
        return dict(error='nhan Octave khac nhan cua ta', check=chk)
    det = det - 1.0
    ds, dm, rm = greedy_match(det, ref_oct, 50.0)                    # 50 ms = 50 mau @1000 Hz
    out = []
    for k in range(n_seg):
        a4, b4 = k * seg_s * 1000.0, (k + 1) * seg_s * 1000.0
        gsel = (ref_oct >= a4) & (ref_oct < b4); dsel = (ds >= a4) & (ds < b4)
        TP = int(rm[gsel].sum()); FN = int(gsel.sum()) - TP; FP = int((~dm[dsel]).sum())
        out.append((TP, FP, FN))
    return dict(seg=out, n_det=int(det.size), check=chk,
                F1_record=float(200.0 * rm.sum() / (2 * rm.sum() + (~dm).sum() + (~rm).sum())))


# ============================================================ cong
def impute(X, med=None):
    if med is None:
        med = np.nanmedian(X, 0); med = np.where(np.isfinite(med), med, 0.0)
    return np.where(np.isfinite(X), X, med), med


def fit_predict(Xtr, ytr, Xte):
    Xtr, med = impute(Xtr)
    clf = HistGradientBoostingClassifier(**GB_PARAMS); clf.fit(Xtr, ytr)
    Xte, _ = impute(Xte, med)
    return clf, med, clf.predict_proba(Xte)[:, 1]


def f1_micro(tp, fp, fn):
    den = 2 * tp + fp + fn
    return 200.0 * tp / den if den else float('nan')


# ============================================================ STV
def epoch_mean_rr_ms(peaks_s, dur_s, epoch_s=EPOCH_S, mask=None):
    """Trung binh RR (ms) tung epoch 3,75 s (nhu analysis/clinical.py).
    mask: mang bool theo epoch -- epoch bi cong tu choi -> NaN."""
    t = np.sort(np.asarray(peaks_s, float))
    n_ep = int(np.floor(dur_s / epoch_s))
    out = np.full(max(n_ep, 0), np.nan)
    if len(t) < 2 or n_ep <= 0:
        return out
    rr = np.diff(t); mid = (t[:-1] + t[1:]) / 2.0
    ok = (rr >= RR_LO) & (rr <= RR_HI); rr, mid = rr[ok], mid[ok]
    if not len(rr):
        return out
    idx = np.floor(mid / epoch_s).astype(int)
    keep = (idx >= 0) & (idx < n_ep); rr, idx = rr[keep], idx[keep]
    cnt = np.bincount(idx, minlength=n_ep); ssum = np.bincount(idx, weights=rr, minlength=n_ep)
    good = cnt >= MIN_RR_EPOCH
    out[good] = ssum[good] / cnt[good] * 1000.0
    if mask is not None:
        out[~np.asarray(mask, bool)[:n_ep]] = np.nan
    return out


def stv_from_epochs(m):
    m = np.asarray(m, float)
    if len(m) < 2:
        return float('nan'), 0
    d = np.abs(np.diff(m)); ok = np.isfinite(d)
    return (float(d[ok].mean()) if ok.any() else float('nan')), int(ok.sum())


def stv_pair(ref_s, det_s, dur_s, mask=None):
    a = epoch_mean_rr_ms(ref_s, dur_s, mask=mask); b = epoch_mean_rr_ms(det_s, dur_s, mask=mask)
    sa, na = stv_from_epochs(a); sb, nb = stv_from_epochs(b)
    both = np.isfinite(a) & np.isfinite(b)
    spa, npa = stv_from_epochs(np.where(both, a, np.nan))
    spb, _ = stv_from_epochs(np.where(both, b, np.nan))
    return dict(stv_ref_ms=sa, stv_det_ms=sb, n_pairs_ref=na, n_pairs_det=nb,
                stv_ref_paired_ms=spa, stv_det_paired_ms=spb, n_pairs_paired=npa,
                n_epoch_total=int(len(a)), n_epoch_det_valid=int(np.isfinite(b).sum()))


def ba(d):
    d = np.asarray([v for v in d if np.isfinite(v)], float)
    if len(d) < 2:
        return dict(n=int(len(d)), bias=float(d.mean()) if len(d) else float('nan'), sd=float('nan'),
                    lo=float('nan'), hi=float('nan'))
    m = float(d.mean()); s = float(d.std(ddof=1))
    return dict(n=int(len(d)), bias=m, sd=s, lo=m - 1.96 * s, hi=m + 1.96 * s,
                mean_abs=float(np.mean(np.abs(d))))


# ============================================================ bootstrap cum
def boot_mean_diff(a, b, n=NBOOT, seed=SEED):
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b
    rng = np.random.default_rng(seed); k = len(d)
    if k == 0:
        return dict(n=0)
    bs = np.array([d[rng.integers(0, k, k)].mean() for _ in range(n)])
    out = dict(n=k, mean_a=float(a.mean()), mean_b=float(b.mean()), diff=float(d.mean()),
               median_diff=float(np.median(d)), ci_lo=float(np.percentile(bs, 2.5)),
               ci_hi=float(np.percentile(bs, 97.5)),
               thang=int((d > 0).sum()), hoa=int((d == 0).sum()), thua=int((d < 0).sum()))
    if k >= 2 and np.any(d != 0):
        try:
            out['p_wilcoxon'] = float(wilcoxon(a, b).pvalue)
        except Exception as ex:
            out['p_wilcoxon'] = float('nan'); out['wilcoxon_note'] = str(ex)
    else:
        out['p_wilcoxon'] = float('nan')
    return out


def boot_stat_by_subject(groups, fn, n=NBOOT, seed=SEED):
    """fn nhan danh sach chi so chu the (co lap lai) -> gia tri; tra ve KTC 95 %."""
    rng = np.random.default_rng(seed); k = len(groups); vals = []
    for _ in range(n):
        idx = rng.integers(0, k, k)
        v = fn(idx)
        if v is not None and np.isfinite(v):
            vals.append(v)
    if not vals:
        return dict(ci_lo=float('nan'), ci_hi=float('nan'), n_valid=0)
    return dict(ci_lo=float(np.percentile(vals, 2.5)), ci_hi=float(np.percentile(vals, 97.5)),
                n_valid=len(vals))


# ============================================================ chinh
def main():
    T0 = time.time()
    recs = load_all()
    tags = sorted(recs, key=lambda t: (0 if t.startswith('r') else (1 if t.startswith('B2') else 2), t))
    fair = json.load(open(os.path.join(ROOT, 'baselines', 'powermf_fair_stats.json'), encoding='utf-8'))
    pmf = {r['rec']: r for r in fair['per_subject']}

    log('gate22_analyze.py  %s  sklearn %s  numpy %s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                                                         sklearn.__version__, np.__version__))
    log('22 chu the, doan 4 s, nhan xau = F1 doan < %.0f, CV = leave-one-SUBJECT-out (22 fold)' % BAD_THR)

    FEATURES = recs[tags[0]]['features']
    # ---------------------------------------------------------------- ma tran doan
    seg_tag, seg_X, seg_y, seg_F1, seg_k, seg_tp, seg_fp, seg_fn = [], [], [], [], [], [], [], []
    for t in tags:
        for r in recs[t]['rows']:
            if not r['has_gt']:
                continue
            seg_tag.append(t); seg_X.append([r[c] for c in FEATURES]); seg_y.append(r['F1'] < BAD_THR)
            seg_F1.append(r['F1']); seg_k.append(r['seg'])
            seg_tp.append(r['TP']); seg_fp.append(r['FP']); seg_fn.append(r['FN'])
    seg_tag = np.array(seg_tag); X = np.array(seg_X, float); y = np.array(seg_y, bool)
    seg_F1 = np.array(seg_F1, float); seg_k = np.array(seg_k, int)
    seg_tp = np.array(seg_tp, int); seg_fp = np.array(seg_fp, int); seg_fn = np.array(seg_fn, int)
    log('  %d doan co nhip (bo %d doan khong co nhip nhan), xau %d = %.2f %%'
        % (len(y), sum(r['n_seg'] for r in recs.values()) - len(y), int(y.sum()), 100 * y.mean()))

    # ---------------------------------------------------------------- Power-MF 4 kenh theo doan
    pmf_seg = {}
    for t in tags:
        d = recs[t]
        s = pmf_segments(t, d['ref_s'], d['n_seg'])
        if s and 'seg' in s:
            dd = abs(s['F1_record'] - pmf[t]['pmf4'])
            s['F1_record_check_absdiff'] = dd
            if dd > 1e-6:
                log('  CANH BAO %s: F1 Power-MF tinh lai %.4f khac powermf_fair_stats %.4f' % (t, s['F1_record'], pmf[t]['pmf4']))
        pmf_seg[t] = s
    n_ok = sum(1 for v in pmf_seg.values() if v and 'seg' in v)
    log('  doc lai dinh Power-MF 4 kenh theo doan: %d/22 chu the (tai lap F1 muc ban ghi khop)' % n_ok)

    # ---------------------------------------------------------------- [1] LOSO gate
    log('\n[1] CONG 22 CA: leave-one-SUBJECT-out, %d dac trung: %s' % (len(FEATURES), ', '.join(FEATURES)))
    oof = np.full(len(y), np.nan); perm_oof = {f: np.full(len(y), np.nan) for f in FEATURES}
    rng = np.random.default_rng(SEED)
    for t in tags:
        te = seg_tag == t
        clf, med, p = fit_predict(X[~te], y[~te], X[te])
        oof[te] = p
        Xte, _ = impute(X[te], med)
        for j, f in enumerate(FEATURES):
            Xp = Xte.copy(); Xp[:, j] = Xp[rng.permutation(len(Xp)), j]
            perm_oof[f][te] = clf.predict_proba(Xp)[:, 1]
    assert np.isfinite(oof).all()

    auc_pool = float(roc_auc_score(y, oof)); ap_pool = float(average_precision_score(y, oof))

    def _pool_auc(idx):
        yy = np.concatenate([y[seg_tag == tags[i]] for i in idx])
        pp = np.concatenate([oof[seg_tag == tags[i]] for i in idx])
        return roc_auc_score(yy, pp) if 0 < yy.sum() < len(yy) else None

    ci_pool = boot_stat_by_subject(tags, _pool_auc)
    log('  (a) AUROC GOP tat ca %d doan cua 22 chu the: %.3f  KTC95 [%.3f; %.3f] (cluster bootstrap theo CHU THE)'
        % (len(y), auc_pool, ci_pool['ci_lo'], ci_pool['ci_hi']))
    log('      AUPRC gop %.3f (ti le doan xau %.2f %%)' % (ap_pool, 100 * y.mean()))
    log('      LUU Y: so nay tron lan phan biet GIUA ban ghi voi phan biet TRONG ban ghi.')

    within = {}
    for t in tags:
        m = seg_tag == t
        within[t] = float(roc_auc_score(y[m], oof[m])) if 0 < y[m].sum() < m.sum() else None
    wv = [v for v in within.values() if v is not None]
    auc_within_mean = float(np.mean(wv)); auc_within_med = float(np.median(wv))
    wt = [t for t in tags if within[t] is not None]

    def _within_mean(idx):
        vv = [within[wt[i]] for i in idx if within[wt[i]] is not None]
        return float(np.mean(vv)) if vv else None

    ci_within = boot_stat_by_subject(wt, _within_mean)
    log('  (b) AUROC TRONG tung ban ghi (chi %d/22 chu the co ca doan tot lan doan xau):' % len(wv))
    log('      trung binh %.3f  KTC95 [%.3f; %.3f]  trung vi %.3f  khoang [%.3f; %.3f]'
        % (auc_within_mean, ci_within['ci_lo'], ci_within['ci_hi'], auc_within_med, min(wv), max(wv)))
    for t in wt:
        log('        %-7s AUROC trong ban ghi %.3f  (doan xau %d/%d)'
            % (t, within[t], int(y[seg_tag == t].sum()), int((seg_tag == t).sum())))
    log('      Cau hoi (a) tra loi: "ban ghi nao dang ngo?"  Cau hoi (b) tra loi: "trong mot ban ghi, giay nao dang ngo?"')

    imp = {f: float(auc_pool - roc_auc_score(y, perm_oof[f])) for f in FEATURES}
    log('  giam AUROC gop khi hoan vi tung dac trung (ngoai fold): '
        + ', '.join('%s %+.3f' % (k, v) for k, v in sorted(imp.items(), key=lambda t_: -t_[1])))

    # ---------------------------------------------------------------- [2] muc ban ghi
    log('\n[2] DIEM TIN CAY MUC BAN GHI = 1 - trung binh p_bad (ngoai fold)')
    rec_rows = []
    for t in tags:
        m = seg_tag == t; p = oof[m]
        rec_rows.append(dict(record=t, group=recs[t]['group'], duration_s=recs[t]['duration_s'],
                             n_seg=int(m.sum()), mean_p_bad=float(p.mean()), median_p_bad=float(np.median(p)),
                             p90_p_bad=float(np.percentile(p, 90)), frac_p_gt_half=float(np.mean(p > 0.5)),
                             score=float(1 - p.mean()), maternal_lock=recs[t]['maternal_lock'],
                             rely=float(recs[t]['F1_record']), pmf4=float(pmf[t]['pmf4']), pmf1=float(pmf[t]['pmf1']),
                             diff=float(recs[t]['F1_record'] - pmf[t]['pmf4']),
                             n_bad_seg=int(y[m].sum()), frac_bad_seg=float(y[m].mean())))
    order = sorted(rec_rows, key=lambda r: r['score'])          # tin cay thap nhat truoc
    for i, r in enumerate(order, 1):
        r['rank_least_reliable'] = i
    rank = {r['record']: r['rank_least_reliable'] for r in order}
    log('  xep hang tu KEM TIN CAY NHAT (1) den tin cay nhat (22):')
    log('  %-4s %-8s %-6s %8s %8s %8s %8s %8s %7s' % ('#', 'ban ghi', 'nhom', 'diem', 'TB p_bad', 'p>0.5', 'F1 rely', 'F1 pmf4', 'hieu'))
    for r in order:
        mark = '  <== KHO' if r['record'] in HARD else ''
        log('  %-4d %-8s %-6s %8.4f %8.4f %8.3f %8.2f %8.2f %+7.2f%s'
            % (r['rank_least_reliable'], r['record'], r['group'], r['score'], r['mean_p_bad'],
               r['frac_p_gt_half'], r['rely'], r['pmf4'], r['diff'], mark))
    hard_ranks = {t: rank[t] for t in HARD}
    log('  => xep hang cua ba ban ghi kho: ' + ', '.join('%s = %d/22' % (t, hard_ranks[t]) for t in HARD))
    top3 = [r['record'] for r in order[:3]]; top4 = [r['record'] for r in order[:4]]; top5 = [r['record'] for r in order[:5]]
    log('  3 chu the bi nghi nhat: %s | 4: %s | 5: %s' % (top3, top4, top5))
    n_hard_in3 = sum(t in top3 for t in HARD); n_hard_in5 = sum(t in top5 for t in HARD)
    log('  => %d/3 ban ghi kho nam trong top-3 dang ngo; %d/3 nam trong top-5.' % (n_hard_in3, n_hard_in5))

    sc = np.array([r['score'] for r in rec_rows]); f1v = np.array([r['rely'] for r in rec_rows])
    dfv = np.array([r['diff'] for r in rec_rows])
    rho_f1 = spearmanr(sc, f1v); rho_d = spearmanr(sc, dfv)
    log('  Spearman(diem tin cay, F1 that) = %.3f (p = %.2g); Spearman(diem, F1 rely - F1 pmf4) = %.3f (p = %.2g)'
        % (rho_f1.statistic, rho_f1.pvalue, rho_d.statistic, rho_d.pvalue))

    # ---------------------------------------------------------------- [2b] doi chung: mot dac trung don le
    log('\n[2b] DOI CHUNG: neu chi dung MOT chi so SQI (khong hoc) thi co xep dung ba ban ghi kho khong?')
    single = {}
    relymap = {r['record']: r['rely'] for r in rec_rows}
    for j, f in enumerate(FEATURES):
        v = {t: float(np.nanmean(X[seg_tag == t, j])) for t in tags}
        for sign in (+1, -1):
            od = sorted(tags, key=lambda t: sign * v[t])          # 'dang ngo nhat' truoc
            r3 = od[:3]; nh = sum(t in r3 for t in HARD)
            key = f + (' (cao = xau)' if sign < 0 else ' (thap = xau)')
            single[key] = dict(top3=r3, n_hard_in_top3=nh,
                               ranks={t: od.index(t) + 1 for t in HARD},
                               spearman_vs_F1=float(spearmanr([-sign * v[t] for t in tags],
                                                              [relymap[t] for t in tags]).statistic))
    best = sorted(single.items(), key=lambda kv: (-kv[1]['n_hard_in_top3'], max(kv[1]['ranks'].values())))
    for k_, v_ in best[:6]:
        log('  %-28s top3 = %-28s bat duoc %d/3 (hang B1_07/B1_06/B2_03 = %d/%d/%d)'
            % (k_, ','.join(v_['top3']), v_['n_hard_in_top3'], v_['ranks']['B1_07'], v_['ranks']['B1_06'], v_['ranks']['B2_03']))
    n_single_perfect = sum(1 for v_ in single.values() if v_['n_hard_in_top3'] == 3)
    log('  => %d/%d quy tac mot-dac-trung cung bat du 3/3. Cong HOC KHONG phai la thu duy nhat lam duoc;'
        % (n_single_perfect, len(single)))
    log('     nhung CV-theo-chu-the cho cong hoc mot nguong DUY NHAT dung cho moi ban ghi, con quy tac mot dac trung')
    log('     duoc chon HAU KIEM tren chinh 22 chu the nay (khong co tap doc lap de chon).')

    # ---------------------------------------------------------------- [3] rui ro - do phu MUC BAN GHI
    log('\n[3] DUONG RUI RO - DO PHU MUC BAN GHI (bo dan chu the kem tin cay nhat)')
    tot_dur = sum(r['duration_s'] for r in rec_rows)
    by_conf = sorted(rec_rows, key=lambda r: -r['score'])       # tin cay cao nhat truoc
    rc_curve = []
    log('  %-5s %-7s %7s %8s %8s %8s %9s %9s %7s %6s' %
        ('giu', 'do phu', '%giay', 'rely', 'pmf4', 'hieu', 'KTC lo', 'KTC hi', 'p', 'bo'))
    for k in range(len(by_conf), 1, -1):
        keep = by_conf[:k]
        a = [r['rely'] for r in keep]; b = [r['pmf4'] for r in keep]
        st = boot_mean_diff(a, b)
        dur_pct = 100.0 * sum(r['duration_s'] for r in keep) / tot_dur
        drop = [r['record'] for r in by_conf[k:]]
        e = dict(n_keep=k, coverage_record_pct=100.0 * k / len(rec_rows), coverage_time_pct=dur_pct,
                 rely_mean=st['mean_a'], pmf4_mean=st['mean_b'], diff=st['diff'], ci_lo=st['ci_lo'],
                 ci_hi=st['ci_hi'], p_wilcoxon=st['p_wilcoxon'], thang=st['thang'], thua=st['thua'],
                 dropped=drop, pmf1_mean=float(np.mean([r['pmf1'] for r in keep])))
        rc_curve.append(e)
        log('  %-5d %6.1f%% %6.1f%% %8.2f %8.2f %+8.2f %+9.2f %+9.2f %7.3f  %s'
            % (k, e['coverage_record_pct'], dur_pct, e['rely_mean'], e['pmf4_mean'], e['diff'],
               e['ci_lo'], e['ci_hi'], e['p_wilcoxon'], (by_conf[k]['record'] + ' bi bo') if drop else '-'))
    first_nonneg = next((e for e in rc_curve if e['diff'] >= 0), None)
    first_ci0 = next((e for e in rc_curve if e['ci_lo'] > 0), None)
    log('  do phu dau tien ma hieu so >= 0        : %s' %
        ('n=%d (%.1f%% ban ghi, %.1f%% giay), hieu %+.2f' % (first_nonneg['n_keep'], first_nonneg['coverage_record_pct'],
                                                             first_nonneg['coverage_time_pct'], first_nonneg['diff'])
         if first_nonneg else 'KHONG CO'))
    log('  do phu dau tien ma KTC95 KHONG chua 0 (ta hon): %s' %
        ('n=%d (%.1f%% ban ghi, %.1f%% giay), hieu %+.2f [%+.2f; %+.2f]'
         % (first_ci0['n_keep'], first_ci0['coverage_record_pct'], first_ci0['coverage_time_pct'],
            first_ci0['diff'], first_ci0['ci_lo'], first_ci0['ci_hi']) if first_ci0 else 'KHONG CO'))

    # ---------------------------------------------------------------- [4] rui ro - do phu MUC DOAN (theo thoi luong)
    log('\n[4] DUONG RUI RO - DO PHU MUC DOAN 4 s (giu lai % GIAY, khong phai % ban ghi)')
    pmf_tp = np.zeros(len(y), int); pmf_fp = np.zeros(len(y), int); pmf_fn = np.zeros(len(y), int)
    have_pmf = np.zeros(len(y), bool)
    for t in tags:
        s = pmf_seg.get(t)
        if not s or 'seg' not in s:
            continue
        m = np.where(seg_tag == t)[0]
        for i in m:
            tp, fp, fn = s['seg'][seg_k[i]]
            pmf_tp[i], pmf_fp[i], pmf_fn[i] = tp, fp, fn
        have_pmf[m] = True
    log('  co dinh Power-MF cho %d/%d doan' % (int(have_pmf.sum()), len(y)))

    seg_curve = []
    qs = np.arange(1.00, 0.04, -0.02)
    for q in qs:
        thr = float(np.quantile(oof, q)) if q < 1.0 else float(oof.max()) + 1
        keep = oof <= thr
        if keep.sum() < 10:
            continue
        kp = keep & have_pmf
        e = dict(quantile=float(q), p_bad_thr=thr, coverage_seg_pct=100.0 * keep.mean(),
                 coverage_time_pct=100.0 * keep.mean(),
                 rely_micro_F1=f1_micro(seg_tp[keep].sum(), seg_fp[keep].sum(), seg_fn[keep].sum()),
                 pmf4_micro_F1=f1_micro(pmf_tp[kp].sum(), pmf_fp[kp].sum(), pmf_fn[kp].sum()),
                 n_seg=int(keep.sum()), n_bad_kept=int(y[keep].sum()),
                 frac_bad_kept=float(y[keep].mean()))
        # macro theo chu the (chi chu the con >= 5 doan)
        ma, mb, nsub = [], [], 0
        for t in tags:
            m = keep & (seg_tag == t)
            if m.sum() >= 5:
                ma.append(f1_micro(seg_tp[m].sum(), seg_fp[m].sum(), seg_fn[m].sum()))
                mm = m & have_pmf
                mb.append(f1_micro(pmf_tp[mm].sum(), pmf_fp[mm].sum(), pmf_fn[mm].sum()) if mm.sum() >= 5 else np.nan)
                nsub += 1
        e['rely_macro_F1'] = float(np.nanmean(ma)); e['pmf4_macro_F1'] = float(np.nanmean(mb)); e['n_subjects'] = nsub
        pair = [(a_, b_) for a_, b_ in zip(ma, mb) if np.isfinite(a_) and np.isfinite(b_)]
        if len(pair) >= 2:
            st = boot_mean_diff([p_[0] for p_ in pair], [p_[1] for p_ in pair], n=NBOOT_SEG)
            e.update(macro_diff=st['diff'], macro_ci_lo=st['ci_lo'], macro_ci_hi=st['ci_hi'],
                     macro_p=st['p_wilcoxon'], macro_thang=st['thang'], macro_thua=st['thua'])
        seg_curve.append(e)
    log('  %8s %9s %10s %10s %10s %10s %10s %10s' %
        ('%giay', 'nguong', 'rely micro', 'pmf4 micro', 'rely macro', 'pmf4 macro', 'hieu macro', 'KTC95'))
    for e in seg_curve:
        if abs(round(e['coverage_seg_pct']) - e['coverage_seg_pct']) < 2.0 or e['quantile'] in (1.0,):
            log('  %7.1f%% %9.4f %10.2f %10.2f %10.2f %10.2f %+10.2f  [%+.2f; %+.2f]'
                % (e['coverage_seg_pct'], e['p_bad_thr'], e['rely_micro_F1'], e['pmf4_micro_F1'],
                   e['rely_macro_F1'], e['pmf4_macro_F1'], e.get('macro_diff', float('nan')),
                   e.get('macro_ci_lo', float('nan')), e.get('macro_ci_hi', float('nan'))))
    seg_nonneg = next((e for e in seg_curve if e.get('macro_diff', -1) >= 0), None)
    seg_ci0 = next((e for e in seg_curve if e.get('macro_ci_lo', -1) > 0), None)
    log('  do phu THOI LUONG dau tien ma hieu macro >= 0: %s' %
        ('%.1f%% giay (hieu %+.2f)' % (seg_nonneg['coverage_time_pct'], seg_nonneg['macro_diff']) if seg_nonneg else 'KHONG CO'))
    log('  do phu THOI LUONG dau tien ma KTC95 > 0     : %s' %
        ('%.1f%% giay' % seg_ci0['coverage_time_pct'] if seg_ci0 else 'KHONG CO'))

    # ---------------------------------------------------------------- [5] lam sang: STV
    log('\n[5] LAM SANG: STV Dawes-Redman (epoch 3,75 s) tren tap con cong giu lai')
    stv_full = {}
    for t in tags:
        d = recs[t]
        stv_full[t] = stv_pair(d['ref_s'], d['det_s'], d['duration_s'])
        stv_full[t]['diff_ms'] = stv_full[t]['stv_det_ms'] - stv_full[t]['stv_ref_ms']
        stv_full[t]['diff_paired_ms'] = stv_full[t]['stv_det_paired_ms'] - stv_full[t]['stv_ref_paired_ms']
    log('  %-8s %8s %8s %8s %8s' % ('ban ghi', 'STVnhan', 'STVmh', 'chech', 'F1'))
    for r in by_conf:
        t = r['record']
        log('  %-8s %8.2f %8.2f %+8.2f %8.2f' % (t, stv_full[t]['stv_ref_ms'], stv_full[t]['stv_det_ms'],
                                                 stv_full[t]['diff_ms'], r['rely']))
    stv_cov = []
    for k in range(len(by_conf), 1, -1):
        keep = [r['record'] for r in by_conf[:k]]
        d1 = [stv_full[t]['diff_ms'] for t in keep]
        b1 = ba(d1)
        stv_cov.append(dict(n_keep=k, coverage_record_pct=100.0 * k / 22,
                            coverage_time_pct=100.0 * sum(recs[t]['duration_s'] for t in keep) / tot_dur,
                            bias_ms=b1['bias'], sd_ms=b1['sd'], loa_lo=b1['lo'], loa_hi=b1['hi'],
                            mean_abs_ms=b1.get('mean_abs', float('nan')),
                            max_abs_ms=float(np.max(np.abs(d1))), dropped=[r['record'] for r in by_conf[k:]]))
    log('  %-5s %8s %8s %10s %10s %10s %9s' % ('giu', '%giay', 'chech TB', '|chech|TB', 'LoA lo', 'LoA hi', 'max|chech|'))
    for e in stv_cov:
        log('  %-5d %7.1f%% %+8.3f %10.3f %10.3f %10.3f %9.3f'
            % (e['n_keep'], e['coverage_time_pct'], e['bias_ms'], e['mean_abs_ms'], e['loa_lo'], e['loa_hi'], e['max_abs_ms']))
    stv_26 = next((e for e in stv_cov if abs(e['bias_ms']) < 2.6), None)
    stv_26_abs = next((e for e in stv_cov if e['mean_abs_ms'] < 2.6), None)
    stv_26_max = next((e for e in stv_cov if e['max_abs_ms'] < 2.6), None)
    log('  |chech TB| < 2,6 ms lan dau tai n = %s; |chech| TB < 2,6 ms tai n = %s; max|chech| < 2,6 ms tai n = %s'
        % (stv_26['n_keep'] if stv_26 else 'khong', stv_26_abs['n_keep'] if stv_26_abs else 'khong',
           stv_26_max['n_keep'] if stv_26_max else 'khong'))

    # STV tren THOI GIAN duoc giu (loai epoch nam trong doan bi tu choi), o vai do phu doan
    log('  STV khi chi giu EPOCH nam trong doan duoc cong chap nhan (muc doan):')
    stv_seg = []
    for q in (1.00, 0.95, 0.90, 0.85, 0.80, 0.70):
        thr = float(np.quantile(oof, q)) if q < 1.0 else float(oof.max()) + 1
        diffs = []; cov_t = []
        for t in tags:
            d = recs[t]; m = seg_tag == t
            keepseg = np.zeros(d['n_seg'], bool)
            keepseg[seg_k[m][oof[m] <= thr]] = True
            # doan 4 s -> epoch 3,75 s: epoch j duoc giu neu doan chua trung diem cua no duoc giu
            n_ep = int(np.floor(d['duration_s'] / EPOCH_S))
            mid = (np.arange(n_ep) + 0.5) * EPOCH_S
            si = np.floor(mid / 4.0).astype(int)
            emask = np.where(si < d['n_seg'], keepseg[np.clip(si, 0, d['n_seg'] - 1)], False)
            s = stv_pair(d['ref_s'], d['det_s'], d['duration_s'], mask=emask)
            diffs.append(s['stv_det_paired_ms'] - s['stv_ref_paired_ms'])
            cov_t.append(float(emask.mean()))
        b1 = ba(diffs)
        stv_seg.append(dict(quantile=float(q), p_bad_thr=thr, coverage_epoch_pct=100.0 * float(np.mean(cov_t)),
                            bias_ms=b1['bias'], mean_abs_ms=b1.get('mean_abs', float('nan')),
                            loa_lo=b1['lo'], loa_hi=b1['hi'], n=b1['n'],
                            max_abs_ms=float(np.nanmax(np.abs(diffs)))))
        log('    giu %5.1f%% epoch: chech TB %+7.3f ms, |chech| TB %6.3f, LoA [%+.2f; %+.2f], max|chech| %6.3f'
            % (stv_seg[-1]['coverage_epoch_pct'], b1['bias'], stv_seg[-1]['mean_abs_ms'], b1['lo'], b1['hi'],
               stv_seg[-1]['max_abs_ms']))

    # ---------------------------------------------------------------- [6] chap nhan nham (false accept)
    log('\n[6] CHAP NHAN NHAM: ban ghi duoc cong GIU LAI nhung F1 thap')
    fa = {}
    for k in (22, 20, 19, 18, 17, 15):
        keep = by_conf[:k]
        bad = [dict(record=r['record'], rank=rank[r['record']], score=r['score'], rely=r['rely'],
                    pmf4=r['pmf4'], diff=r['diff'], stv_diff_ms=stv_full[r['record']]['diff_ms'])
               for r in keep if r['rely'] < 95.0]
        fa['keep_%d' % k] = bad
        log('  giu %d ban ghi (%.0f%%): %d ban ghi chap nhan nham (F1 < 95): %s'
            % (k, 100.0 * k / 22, len(bad), ', '.join('%s F1 %.2f (hang %d, dSTV %+.2f ms)'
                                                      % (b['record'], b['rely'], b['rank'], b['stv_diff_ms']) for b in bad) or '-'))
    for thr_f1 in (90.0, 95.0, 99.0):
        n_bad_rec = sum(1 for r in rec_rows if r['rely'] < thr_f1)
        log('  (tham chieu: %d/22 ban ghi co F1 < %.0f)' % (n_bad_rec, thr_f1))

    # ---------------------------------------------------------------- luu
    out = dict(
        ngay=datetime.datetime.now().isoformat(timespec='seconds'),
        cau_hoi='cong tu choi co danh dau dung B1_07 / B1_06 / B2_03 la khong tin cay khong?',
        thiet_ke=dict(features=FEATURES, n_features=len(FEATURES), bad_threshold_F1=BAD_THR,
                      seg_s=4.0, cv='leave-one-SUBJECT-out tren 22 chu the (khong ro ri)',
                      learner='HistGradientBoostingClassifier', learner_params=GB_PARAMS,
                      score='1 - trung binh p_bad ngoai fold', n_boot=NBOOT, n_boot_seg=NBOOT_SEG, seed=SEED,
                      sklearn=sklearn.__version__, numpy=np.__version__,
                      nguon_du_lieu=dict(model='fetalqrs_tcn_22_fold_XX.pt qua benchmark_dpss/eval_22.json',
                                         powermf='baselines/powermf_fair_stats.json + powermf_work/*_powermf.mat',
                                         dac_trung='analysis/gate22_cache/gate22_feat_*.json')),
        cong=dict(auroc_pooled=auc_pool, auroc_pooled_ci=[ci_pool['ci_lo'], ci_pool['ci_hi']], auprc_pooled=ap_pool,
                  n_segments=int(len(y)), n_bad=int(y.sum()), frac_bad=float(y.mean()),
                  auroc_within_record=within, auroc_within_mean=auc_within_mean,
                  auroc_within_median=auc_within_med,
                  auroc_within_ci=[ci_within['ci_lo'], ci_within['ci_hi']],
                  n_records_with_both_classes=len(wv),
                  permutation_importance_delta_auroc=imp),
        muc_ban_ghi=dict(bang=rec_rows, xep_hang_kem_tin_cay_nhat=[r['record'] for r in order],
                         hang_cua_ba_ban_ghi_kho=hard_ranks, top3=top3, top4=top4, top5=top5,
                         so_ban_kho_trong_top3=n_hard_in3, so_ban_kho_trong_top5=n_hard_in5,
                         spearman_score_vs_F1=[float(rho_f1.statistic), float(rho_f1.pvalue)],
                         spearman_score_vs_diff=[float(rho_d.statistic), float(rho_d.pvalue)],
                         doi_chung_mot_dac_trung=single,
                         so_quy_tac_mot_dac_trung_bat_du_3=n_single_perfect,
                         so_quy_tac_mot_dac_trung=len(single)),
        rui_ro_do_phu_ban_ghi=dict(duong=rc_curve, do_phu_dau_tien_hieu_khong_am=first_nonneg,
                                   do_phu_dau_tien_KTC_duong=first_ci0, tong_thoi_luong_s=tot_dur),
        rui_ro_do_phu_doan=dict(duong=seg_curve, do_phu_dau_tien_hieu_khong_am=seg_nonneg,
                                do_phu_dau_tien_KTC_duong=seg_ci0,
                                n_doan_co_powermf=int(have_pmf.sum())),
        lam_sang=dict(stv_tung_ban_ghi=stv_full, stv_theo_do_phu_ban_ghi=stv_cov,
                      stv_theo_do_phu_doan=stv_seg,
                      nguong_TRUFFLE_ms=2.6, chap_nhan_nham=fa),
        kiem_chung=dict(F1_tai_lap_tu_eval22={t: recs[t]['F1_check_absdiff'] for t in tags},
                        F1_powermf_tai_lap={t: (pmf_seg[t].get('F1_record_check_absdiff') if pmf_seg.get(t) and 'seg' in pmf_seg[t] else None)
                                            for t in tags}),
        runtime_min=(time.time() - T0) / 60)
    json.dump(out, open(os.path.join(HERE, 'gate22_results.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    with open(os.path.join(HERE, 'gate22_segments.csv'), 'w', encoding='utf-8') as f:
        f.write('record,group,seg,t0_s,n_gt,TP,FP,FN,F1,bad,p_bad_oof,' + ','.join(FEATURES) + '\n')
        for i in range(len(y)):
            t = seg_tag[i]
            f.write('%s,%s,%d,%.1f,%d,%d,%d,%d,%.6f,%d,%.6f,%s\n'
                    % (t, recs[t]['group'], seg_k[i], seg_k[i] * 4.0, seg_tp[i] + seg_fn[i], seg_tp[i], seg_fp[i],
                       seg_fn[i], seg_F1[i], int(y[i]), oof[i], ','.join('%.6g' % v for v in X[i])))
    with open(os.path.join(HERE, 'gate22_log.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(_LOG) + '\n')

    np.save(os.path.join(CACHE, 'oof_p_bad.npy'), oof)
    np.save(os.path.join(CACHE, 'seg_tag.npy'), seg_tag)
    log('\nda ghi gate22_results.json, gate22_segments.csv, gate22_log.txt (%.1f phut)' % ((time.time() - T0) / 60))


if __name__ == '__main__':
    main()
