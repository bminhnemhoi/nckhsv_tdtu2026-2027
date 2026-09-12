# -*- coding: utf-8 -*-
"""
chonkenh_rules.py -- Buoc 2 cua M5: cai va so sanh cac QUY TAC CHON KENH MU NHAN.

Dau vao : analysis/chonkenh_cache/{cinc,s22}_*.json  (chonkenh_cache.py)
          analysis/chonkenh_khaibao_truoc.json       (danh sach khai bao truoc)
Dau ra  : analysis/chonkenh_results.json, analysis/CHONKENH.md, analysis/fig_chonkenh.png

NGUYEN TAC CHONG RO RI (kiem tra bang assert o cuoi tep):
  * Moi quy tac nhan DUY NHAT: diem PSD, dac trung SQI tung doan, chuoi phat hien.
    KHONG quy tac nao doc F1/TP/FP/FN cua kenh -- nhung truong do chi dung de CHAM DIEM.
  * Cong va bo chon hoc: leave-one-SUBJECT-out tren 22 chu the; tren CinC thi huan luyen
    tren TOAN BO 22 chu the roi ap zero-shot (CinC khong bao gio nam trong tap huan luyen).
  * Sieu tham so duy nhat (k cua quy tac hop nhat) CHON TREN 22 CHU THE, ap nguyen sang CinC.

Chay: python analysis/chonkenh_rules.py
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, glob, time, datetime, platform
import numpy as np
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from scipy.stats import wilcoxon, binomtest

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, 'chonkenh_cache')
OUT_JSON = os.path.join(HERE, 'chonkenh_results.json')
OUT_MD = os.path.join(HERE, 'CHONKENH.md')
OUT_PNG = os.path.join(HERE, 'fig_chonkenh.png')
OUT_LOG = os.path.join(HERE, 'chonkenh_rules_log.txt')

SEED = 0; NBOOT = 10000; BAD_THR = 80.0; TOL_S = 0.050; REFRAC_S = 0.250
GB_C = dict(max_depth=3, max_iter=200, learning_rate=0.05, class_weight='balanced', random_state=SEED)
GB_R = dict(max_depth=3, max_iter=200, learning_rate=0.05, random_state=SEED)
NEW_RULES = ['gate', 'gate4', 'rrcv', 'peakprob', 'rrplaus', 'fuse', 'learned']
_LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); _LOG.append(s)


# ================================================================= nap du lieu
def load_arm(arm):
    recs = []
    for p in sorted(glob.glob(os.path.join(CACHE, '%s_*.json' % arm))):
        d = json.load(open(p, encoding='utf-8'))
        d['lead_keys'] = sorted(d['leads'], key=lambda k: int(k))
        recs.append(d)
    return recs


def greedy_f1(det_s, ref_s, tol=TOL_S):
    ref = np.sort(np.asarray(ref_s, float)); det = np.sort(np.asarray(det_s, float))
    used = np.zeros(len(ref), bool); tp = 0
    for d in det:
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (~used))[0]
        if len(ok):
            used[ok[int(np.argmin(dd[ok]))]] = True; tp += 1
    fp = len(det) - tp; fn = len(ref) - tp
    se = 100.0 * tp / (tp + fn) if tp + fn else 0.0
    ppv = 100.0 * tp / (tp + fp) if tp + fp else 0.0
    return dict(TP=tp, FP=fp, FN=fn, Se=se, PPV=ppv,
                F1=(2 * se * ppv / (se + ppv)) if se + ppv else 0.0)


# ================================================================= dac trung mu nhan
def rr_stats(det_s):
    d = np.sort(np.asarray(det_s, float))
    if len(d) < 3:
        return dict(rr_cv=10.0, rr_plaus=0.0, n=len(d))   # 10.0 = gia tri phat huu han (khong dung inf)
    rr = np.diff(d)
    return dict(rr_cv=float(np.std(rr) / (np.mean(rr) + 1e-12)),
                rr_plaus=float(np.mean((rr >= 0.3) & (rr <= 0.7))), n=len(d))


def lead_blind(rec, k):
    """dac trung MU NHAN muc ban ghi cho mot kenh"""
    L = rec['leads'][k]
    F = np.asarray(L['seg_feat'], float)          # (n_seg, 12)
    names = rec['features']
    med = np.nanmedian(F, 0) if len(F) else np.full(len(names), np.nan)
    out = {('seg_%s' % n): float(v) for n, v in zip(names, med)}
    out['psd'] = float(L['psd'])
    out['log_psd'] = float(np.log10(L['psd'] + 1e-30))
    out.update({('rec_%s' % a): b for a, b in rr_stats(L['det_s']).items()})
    out['det_rate'] = len(L['det_s']) / max(rec['duration_s'], 1e-9)
    return out


BLIND_KEYS = None


def blind_matrix(recs):
    """-> X (n_rec*4, n_feat) voi ca gia tri tho va XEP HANG TRONG BAN GHI, y = F1 that"""
    global BLIND_KEYS
    rows, y, gid, rid, lid = [], [], [], [], []
    for ri, rec in enumerate(recs):
        vals = [lead_blind(rec, k) for k in rec['lead_keys']]
        if BLIND_KEYS is None:
            BLIND_KEYS = sorted(vals[0])
        A = np.array([[v[c] for c in BLIND_KEYS] for v in vals], float)
        # xep hang trong ban ghi (0 = nho nhat) -- khong dung nhan
        R = np.argsort(np.argsort(np.where(np.isfinite(A), A, -np.inf), axis=0), axis=0).astype(float)
        for j, k in enumerate(rec['lead_keys']):
            rows.append(np.concatenate([A[j], R[j]]))
            y.append(rec['leads'][k]['F1']); gid.append(rec['record'])
            rid.append(ri); lid.append(j)
    return np.array(rows, float), np.array(y, float), np.array(gid), np.array(rid), np.array(lid)


def impute(X, med=None):
    if med is None:
        med = np.nanmedian(X, 0); med = np.where(np.isfinite(med), med, 0.0)
    return np.where(np.isfinite(X), X, med), med


# ================================================================= cong tu choi
def gate_train_rows(recs, leads='psd'):
    """doan de huan luyen cong. leads='psd' -> chi kenh PSD; leads='all' -> ca 4 kenh."""
    X, y, g = [], [], []
    for rec in recs:
        keys = rec['lead_keys']
        if leads == 'psd':
            keys = [max(keys, key=lambda k: rec['leads'][k]['psd'])]
        for k in keys:
            L = rec['leads'][k]
            F = np.asarray(L['seg_feat'], float)
            segF1 = seg_f1(rec, k)
            for i in range(len(F)):
                if np.isfinite(segF1[i]):
                    X.append(F[i]); y.append(segF1[i] < BAD_THR); g.append(rec['record'])
    return np.array(X, float), np.array(y, bool), np.array(g)


def seg_f1(rec, k, seg_s=4.0):
    """F1 tung doan 4 s cho mot kenh (CHI de huan luyen cong -- dung nhan, nen chi hop le
    o buoc HUAN LUYEN tren du lieu KHONG phai tap kiem)."""
    ref = np.sort(np.asarray(rec['ref_s'], float)); det = np.sort(np.asarray(rec['leads'][k]['det_s'], float))
    used = np.zeros(len(ref), bool); dm = np.zeros(len(det), bool)
    for i, d in enumerate(det):
        dd = np.abs(ref - d); ok = np.where((dd <= TOL_S) & (~used))[0]
        if len(ok):
            used[ok[int(np.argmin(dd[ok]))]] = True; dm[i] = True
    n_seg = rec['leads'][k]['n_seg']; out = np.full(n_seg, np.nan)
    for s in range(n_seg):
        a, b = s * seg_s, (s + 1) * seg_s
        gs = (ref >= a) & (ref < b); ds = (det >= a) & (det < b)
        if not gs.any():
            continue
        TP = int(used[gs].sum()); FN = int(gs.sum()) - TP; FP = int((~dm[ds]).sum())
        den = 2 * TP + FP + FN
        out[s] = 200.0 * TP / den if den else np.nan
    return out


def gate_scores(clf, med, rec):
    """diem tin cay (cang cao cang tot) cho tung kenh"""
    s = []
    for k in rec['lead_keys']:
        F = np.asarray(rec['leads'][k]['seg_feat'], float)
        if not len(F):
            s.append(0.0); continue
        Fi, _ = impute(F, med)
        s.append(float(1.0 - clf.predict_proba(Fi)[:, 1].mean()))
    return np.array(s)


# ================================================================= quy tac
def rule_select(rec, which, ctx):
    """-> chi so kenh (0..3) theo quy tac MU NHAN"""
    keys = rec['lead_keys']; L = rec['leads']
    if which == 'psd':
        return int(np.argmax([L[k]['psd'] for k in keys]))
    if which == 'lead0':
        return 0
    if which == 'rrcv':
        v = [rr_stats(L[k]['det_s'])['rr_cv'] for k in keys]
        return int(np.argmin(v))
    if which == 'peakprob':
        j = rec['features'].index('peak_prob_mean')
        v = [float(np.nanmedian(np.asarray(L[k]['seg_feat'], float)[:, j])) if L[k]['n_seg'] else 0.0 for k in keys]
        return int(np.nanargmax(v))
    if which == 'rrplaus':
        st = [rr_stats(L[k]['det_s']) for k in keys]
        v = np.array([s['rr_plaus'] for s in st]); cv = np.array([s['rr_cv'] for s in st])
        best = np.where(v >= v.max() - 1e-12)[0]
        return int(best[np.argmin(cv[best])])
    if which in ('gate', 'gate4'):
        return int(np.argmax(ctx[which][rec['record']]))
    if which == 'learned':
        return int(np.argmax(ctx['learned'][rec['record']]))
    raise ValueError(which)


def fuse_detections(rec, k_min):
    """gop phat hien 4 kenh -> giu cum co >= k_min kenh dong y trong +/-50 ms"""
    ev = []
    for j, key in enumerate(rec['lead_keys']):
        for t in rec['leads'][key]['det_s']:
            ev.append((float(t), j))
    if not ev:
        return []
    ev.sort()
    T = np.array([e[0] for e in ev]); Lj = np.array([e[1] for e in ev])
    clusters = []; i = 0
    while i < len(T):
        t0 = T[i]; j = i
        while j < len(T) and T[j] - t0 <= TOL_S:
            j += 1
        clusters.append((float(np.median(T[i:j])), len(set(Lj[i:j].tolist()))))
        i = j
    kept = [c for c in clusters if c[1] >= k_min]
    kept.sort(key=lambda c: c[0])
    out = []
    for t, sup in kept:
        if out and t - out[-1][0] < REFRAC_S:
            if sup > out[-1][1]:
                out[-1] = (t, sup)
        else:
            out.append((t, sup))
    return [t for t, _ in out]


# ================================================================= thong ke
def boot_ci(d, nboot=NBOOT, seed=SEED):
    d = np.asarray(d, float); n = len(d)
    rng = np.random.default_rng(seed)
    b = d[rng.integers(0, n, size=(nboot, n))].mean(1)
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def compare(a, b):
    """a = quy tac, b = moc PSD; don vi = ban ghi"""
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b
    nz = int(np.sum(np.abs(d) > 1e-9))
    try:
        w = float(wilcoxon(a, b, zero_method='wilcox').pvalue) if nz else 1.0
    except ValueError:
        w = 1.0
    wins = int((d > 1e-9).sum()); losses = int((d < -1e-9).sum())
    sp = float(binomtest(wins, wins + losses, .5).pvalue) if wins + losses else 1.0
    return dict(mean=float(a.mean()), median=float(np.median(a)), sd=float(a.std(ddof=1)),
                ge90=int((a >= 90).sum()), mid=int(((a >= 50) & (a < 90)).sum()), lt50=int((a < 50).sum()),
                diff_vs_psd=float(d.mean()), ci95=boot_ci(d), wilcoxon_p=w, sign_p=sp,
                wins=wins, losses=losses, ties=int(len(d) - wins - losses), n=int(len(d)))


def holm(pvals, names):
    idx = np.argsort(pvals); m = len(pvals); out = {}; prev = 0.0
    for r, i in enumerate(idx):
        v = min(1.0, max(prev, (m - r) * pvals[i])); prev = v; out[names[i]] = float(v)
    return out


# ================================================================= chay mot canh
def run_arm(recs, ctx_gate_psd, ctx_gate_all, ctx_learned, k_fuse_list):
    ctx = dict(gate=ctx_gate_psd, gate4=ctx_gate_all, learned=ctx_learned)
    per = {}
    sel = {}
    for name in ['psd', 'lead0', 'rrcv', 'peakprob', 'rrplaus', 'gate', 'gate4', 'learned']:
        f1 = []; choice = []
        for rec in recs:
            j = rule_select(rec, name, ctx)
            f1.append(rec['leads'][rec['lead_keys'][j]]['F1']); choice.append(j)
        per[name] = np.array(f1); sel[name] = choice
    per['mean4'] = np.array([np.mean([rec['leads'][k]['F1'] for k in rec['lead_keys']]) for rec in recs])
    per['oracle'] = np.array([max(rec['leads'][k]['F1'] for k in rec['lead_keys']) for rec in recs])
    per['worst'] = np.array([min(rec['leads'][k]['F1'] for k in rec['lead_keys']) for rec in recs])
    for k in k_fuse_list:
        per['fuse_k%d' % k] = np.array([greedy_f1(fuse_detections(rec, k), rec['ref_s'])['F1'] for rec in recs])
    return per, sel


def main():
    t0 = time.time()
    log('===== CHON KENH MU NHAN (M5) | %s | sklearn %s | %s ====='
        % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sklearn.__version__, platform.platform()))
    pre = json.load(open(os.path.join(HERE, 'chonkenh_khaibao_truoc.json'), encoding='utf-8'))
    log('khai bao truoc: %d quy tac (%d quy tac moi: %s)'
        % (len(pre['quy_tac_se_thu']), pre['so_quy_tac_moi'], ', '.join(pre['ma_quy_tac_moi'])))

    s22 = load_arm('s22'); cinc = load_arm('cinc')
    assert len(s22) == 22, '22 chu the, dang co %d' % len(s22)
    assert len(cinc) == 75, '75 ban ghi CinC, dang co %d' % len(cinc)
    log('nap: 22 chu the (%.1f phut tin hieu), 75 ban ghi CinC (%.1f phut)'
        % (sum(r['duration_s'] for r in s22) / 60, sum(r['duration_s'] for r in cinc) / 60))

    # ---------------------------------------------------------- cong: LOSO tren 22, full cho CinC
    gate_ctx = {}
    for tag, leads in (('gate', 'psd'), ('gate4', 'all')):
        X, y, g = gate_train_rows(s22, leads)
        log('%-6s doan huan luyen %d (xau %d = %.1f%%), kenh = %s' % (tag, len(y), int(y.sum()), 100 * y.mean(), leads))
        ctx22 = {}
        for rec in s22:                                   # leave-one-SUBJECT-out
            m = g != rec['record']
            Xi, med = impute(X[m]); clf = HistGradientBoostingClassifier(**GB_C); clf.fit(Xi, y[m])
            ctx22[rec['record']] = gate_scores(clf, med, rec)
        Xa, meda = impute(X); clfa = HistGradientBoostingClassifier(**GB_C); clfa.fit(Xa, y)
        ctxc = {rec['record']: gate_scores(clfa, meda, rec) for rec in cinc}
        gate_ctx[tag] = (ctx22, ctxc)

    # ---------------------------------------------------------- bo chon hoc
    X22, y22, g22, _, _ = blind_matrix(s22)
    Xc, yc, gc, _, _ = blind_matrix(cinc)
    log('bo chon hoc: %d hang huan luyen (22 chu the x 4 kenh), %d dac trung (13 tho + 13 xep hang)'
        % (len(y22), X22.shape[1]))
    learned22 = {}
    for rec in s22:
        m = g22 != rec['record']
        Xi, med = impute(X22[m]); reg = HistGradientBoostingRegressor(**GB_R); reg.fit(Xi, y22[m])
        Xt, _ = impute(X22[~m], med)
        learned22[rec['record']] = reg.predict(Xt)
    Xa, meda = impute(X22); rega = HistGradientBoostingRegressor(**GB_R); rega.fit(Xa, y22)
    learnedc = {}
    for i, rec in enumerate(cinc):
        Xt, _ = impute(Xc[gc == rec['record']], meda)
        learnedc[rec['record']] = rega.predict(Xt)

    # ---------------------------------------------------------- chay ca hai canh
    per22, sel22 = run_arm(s22, gate_ctx['gate'][0], gate_ctx['gate4'][0], learned22, [1, 2, 3, 4])
    perC, selC = run_arm(cinc, gate_ctx['gate'][1], gate_ctx['gate4'][1], learnedc, [1, 2, 3, 4])

    # ---------------------------------------------------------- CHON k CUA QUY TAC HOP NHAT: CHI TREN 22
    k_best = int(max([1, 2, 3, 4], key=lambda k: per22['fuse_k%d' % k].mean()))
    log('\nsieu tham so k cua quy tac hop nhat, CHON TREN 22 CHU THE:')
    for k in (1, 2, 3, 4):
        log('   k=%d  F1 22 chu the %6.2f   (CinC %6.2f -- KHONG dung de chon)'
            % (k, per22['fuse_k%d' % k].mean(), perC['fuse_k%d' % k].mean()))
    log('   -> k = %d, ap NGUYEN XI sang CinC' % k_best)
    per22['fuse'] = per22['fuse_k%d' % k_best]; perC['fuse'] = perC['fuse_k%d' % k_best]

    # ---------------------------------------------------------- VIEC 1: chan doan quy tac PSD
    diag = {}
    for tag, recs, per in (('s22', s22, per22), ('cinc', cinc, perC)):
        psd = per['psd']; orc = per['oracle']; loss = orc - psd
        hard = orc < 50
        allf1 = np.array([[rec['leads'][k]['F1'] for k in rec['lead_keys']] for rec in recs])
        rank = []
        for i, rec in enumerate(recs):
            j = rule_select(rec, 'psd', {})
            rank.append(int(np.sum(allf1[i] > allf1[i][j] + 1e-9)))
        diag[tag] = dict(
            n=len(recs), psd_mean=float(psd.mean()), oracle_mean=float(orc.mean()),
            headroom=float(loss.mean()),
            psd_achieves_oracle=int((loss < 1e-9).sum()),
            psd_lead_is_oracle_index=int(sum(1 for i, rec in enumerate(recs)
                                             if rule_select(rec, 'psd', {}) == int(np.argmax(allf1[i])))),
            loss_median=float(np.median(loss)), loss_p90=float(np.percentile(loss, 90)),
            loss_max=float(loss.max()),
            loss_buckets={'<1': int((loss < 1).sum()), '1-5': int(((loss >= 1) & (loss < 5)).sum()),
                          '5-10': int(((loss >= 5) & (loss < 10)).sum()),
                          '10-20': int(((loss >= 10) & (loss < 20)).sum()),
                          '20-50': int(((loss >= 20) & (loss < 50)).sum()),
                          '>=50': int((loss >= 50).sum())},
            n_loss_gt10=int((loss > 10).sum()),
            headroom_from_loss_gt10=float(loss[loss > 10].sum() / len(recs)),
            n_hard_ceiling=int(hard.sum()),
            hard_records=[recs[i]['record'] for i in np.where(hard)[0]],
            headroom_hard=float((orc[hard] - psd[hard]).sum() / len(recs)),
            headroom_rescuable=float((orc[~hard] - psd[~hard]).sum() / len(recs)),
            psd_rank_hist=[int(np.sum(np.asarray(rank) == r)) for r in range(4)],
            psd_lt50=int((psd < 50).sum()), oracle_lt50=int((orc < 50).sum()),
            psd_ge90=int((psd >= 90).sum()), oracle_ge90=int((orc >= 90).sum()))

    # ---------------------------------------------------------- bang ket qua
    ORDER = ['psd', 'gate', 'gate4', 'rrcv', 'peakprob', 'rrplaus', 'fuse', 'learned',
             'fuse_k1', 'fuse_k2', 'fuse_k3', 'fuse_k4', 'lead0', 'mean4', 'worst', 'oracle']
    tables = {}
    for tag, recs, per in (('s22', s22, per22), ('cinc', cinc, perC)):
        tb = {}
        for name in ORDER:
            tb[name] = compare(per[name], per['psd'])
        ps = [tb[n]['wilcoxon_p'] for n in NEW_RULES]
        hp = holm(ps, NEW_RULES)
        for n in NEW_RULES:
            tb[n]['holm_p'] = hp[n]
        tables[tag] = tb

    # bien the 68 ban ghi CinC (khai bao tu vong truoc: loai 7 ban chu thich sai)
    keep68 = np.array([not r['bad_annotation'] for r in cinc])
    tb68 = {n: compare(perC[n][keep68], perC['psd'][keep68]) for n in ORDER}

    # quy tac chon kenh co trung oracle khong
    hit = {}
    for tag, recs, per, sel in (('s22', s22, per22, sel22), ('cinc', cinc, perC, selC)):
        hit[tag] = {}
        for name in sel:
            h = sum(1 for i, rec in enumerate(recs)
                    if per[name][i] >= per['oracle'][i] - 1e-9)
            hit[tag][name] = dict(dat_oracle=int(h), n=len(recs), pct=100.0 * h / len(recs))

    # ---------------------------------------------------------- quyet dinh da khai bao truoc
    cand = [n for n in NEW_RULES]
    best_by_s22 = max(cand, key=lambda n: tables['s22'][n]['mean'])
    best_by_cinc = max(cand, key=lambda n: tables['cinc'][n]['mean'])
    beat_psd_s22 = [n for n in cand if tables['s22'][n]['ci95'][0] > 0]
    beat_psd_cinc = [n for n in cand if tables['cinc'][n]['ci95'][0] > 0]

    # ---------------------------------------------------------- in bang
    LBL = dict(psd='PSD (moc chuan, mu nhan)', gate='cong (huan luyen kenh PSD)',
               gate4='cong4 (huan luyen 4 kenh)', rrcv='rr_cv thap nhat', peakprob='xac suat dinh cao nhat',
               rrplaus='RR hop ly nhat', fuse='HOP NHAT k=?', learned='bo chon hoc (LOSO)',
               fuse_k1='  hop nhat k=1', fuse_k2='  hop nhat k=2', fuse_k3='  hop nhat k=3',
               fuse_k4='  hop nhat k=4', lead0='kenh 0 co dinh (HAU KIEM)', mean4='TB 4 kenh (khong chon)',
               worst='kenh te nhat (san)', oracle='ORACLE (chan tren)')
    LBL['fuse'] = 'HOP NHAT k=%d' % k_best
    for tag, name in (('s22', '22 CHU THE (TRONG MIEN -- dung de chon quy tac)'),
                      ('cinc', '75 BAN GHI CinC 2013 (NGOAI MIEN -- xac nhan)')):
        tb = tables[tag]
        log('\n\n===== %s =====' % name)
        log('%-30s %7s %7s %6s %5s %5s %8s %20s %9s %9s %7s'
            % ('quy tac', 'F1 TB', 'trvi', 'sd', '>=90', '<50', 'hieu', 'KTC95 bootstrap', 'p Wilc', 'p Holm', 'T/Th'))
        for n in ORDER:
            c = tb[n]
            hp = ('%9.3g' % c['holm_p']) if 'holm_p' in c else ' ' * 9
            log('%-30s %7.2f %7.2f %6.2f %5d %5d %+8.2f [%+8.2f;%+8.2f] %9.3g %s %3d/%-3d'
                % (LBL[n], c['mean'], c['median'], c['sd'], c['ge90'], c['lt50'], c['diff_vs_psd'],
                   c['ci95'][0], c['ci95'][1], c['wilcoxon_p'], hp, c['wins'], c['losses']))
        log('\n%-30s %s' % ('dat F1 cua kenh oracle:',
                            '  '.join('%s %d/%d' % (k, v['dat_oracle'], v['n']) for k, v in hit[tag].items())))

    log('\n\n===== BIEN THE 68 BAN GHI CinC (loai 7 ban chu thich sai, khai bao tu vong truoc) =====')
    for n in ORDER:
        c = tb68[n]
        log('%-30s %7.2f  >=90 %2d  <50 %2d  hieu %+7.2f [%+7.2f;%+7.2f]'
            % (LBL[n], c['mean'], c['ge90'], c['lt50'], c['diff_vs_psd'], c['ci95'][0], c['ci95'][1]))

    log('\n===== QUYET DINH (theo khai bao truoc: chon tren 22 chu the) =====')
    log('quy tac tot nhat theo 22 chu the : %s (F1 %.2f, hieu %+.2f vs PSD)'
        % (best_by_s22, tables['s22'][best_by_s22]['mean'], tables['s22'][best_by_s22]['diff_vs_psd']))
    log('  -> ket qua XAC NHAN tren CinC 75: F1 %.2f, hieu %+.2f KTC95 [%+.2f;%+.2f], p=%.3g'
        % (tables['cinc'][best_by_s22]['mean'], tables['cinc'][best_by_s22]['diff_vs_psd'],
           tables['cinc'][best_by_s22]['ci95'][0], tables['cinc'][best_by_s22]['ci95'][1],
           tables['cinc'][best_by_s22]['wilcoxon_p']))
    log('quy tac tot nhat theo CinC (HAU KIEM, chi mo ta): %s (F1 %.2f)'
        % (best_by_cinc, tables['cinc'][best_by_cinc]['mean']))
    log('vuot moc PSD (KTC95 bootstrap khong chua 0) tren 22 chu the: %s' % (beat_psd_s22 or 'KHONG CO'))
    log('vuot moc PSD (KTC95 bootstrap khong chua 0) tren CinC 75   : %s' % (beat_psd_cinc or 'KHONG CO'))

    out = dict(
        meta=dict(date=str(datetime.datetime.now()), sklearn=sklearn.__version__,
                  platform=platform.platform(), seed=SEED, n_boot=NBOOT,
                  tolerance_ms=50, bad_thr_segment=BAD_THR,
                  n_s22=len(s22), n_cinc=len(cinc),
                  checkpoint_cinc='fetalqrs_tcn_22_production.pt',
                  checkpoint_s22='fetalqrs_tcn_22_fold_XX.pt (fold khong chua chu the)',
                  prereg='analysis/chonkenh_khaibao_truoc.json',
                  cache='analysis/chonkenh_cache/',
                  minutes=None),
        khai_bao_truoc=pre,
        chan_doan_psd=diag,
        k_hop_nhat_chon_tren_22=k_best,
        bang=dict(s22=tables['s22'], cinc=tables['cinc'], cinc68=tb68),
        dat_oracle=hit,
        chon_kenh_theo_quy_tac=dict(
            s22={rec['record']: {n: int(sel22[n][i]) for n in sel22} for i, rec in enumerate(s22)},
            cinc={rec['record']: {n: int(selC[n][i]) for n in selC} for i, rec in enumerate(cinc)}),
        F1_tung_ban_ghi=dict(
            s22={rec['record']: {n: float(per22[n][i]) for n in ORDER} for i, rec in enumerate(s22)},
            cinc={rec['record']: {n: float(perC[n][i]) for n in ORDER} for i, rec in enumerate(cinc)}),
        quyet_dinh=dict(tot_nhat_theo_22=best_by_s22, tot_nhat_theo_cinc_hau_kiem=best_by_cinc,
                        vuot_psd_22=beat_psd_s22, vuot_psd_cinc=beat_psd_cinc))
    out['meta']['minutes'] = (time.time() - t0) / 60
    json.dump(out, open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    make_fig(s22, cinc, per22, perC, tables, diag, k_best)
    open(OUT_LOG, 'w', encoding='utf-8').write('\n'.join(_LOG))
    log('\nDONE %.1f phut -> %s' % (out['meta']['minutes'], OUT_JSON))
    return out


def make_fig(s22, cinc, per22, perC, tables, diag, k_best):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(13.5, 9))

    # A: mat mat cua quy tac PSD tren CinC
    loss = np.sort(perC['oracle'] - perC['psd'])[::-1]
    a = ax[0, 0]
    a.bar(np.arange(len(loss)), loss, color=['#c62828' if v > 10 else '#90a4ae' for v in loss], width=.85)
    a.axhline(10, color='#333', ls='--', lw=1)
    a.set_title('A. Mat mat cua quy tac PSD tren 75 ban ghi CinC\n(oracle - PSD, sap giam); '
                '%d ban ghi mat > 10 diem chiem %.2f/%.2f diem du dia'
                % (diag['cinc']['n_loss_gt10'], diag['cinc']['headroom_from_loss_gt10'], diag['cinc']['headroom']),
                fontsize=10)
    a.set_xlabel('ban ghi (sap theo mat mat)'); a.set_ylabel('F1 mat di (diem)'); a.grid(alpha=.25, axis='y')

    # B: F1 trung binh tung quy tac, hai canh
    names = ['worst', 'mean4', 'lead0', 'rrcv', 'rrplaus', 'peakprob', 'psd', 'gate', 'gate4',
             'learned', 'fuse', 'oracle']
    lbl = ['te nhat', 'TB 4 kenh', 'kenh 0', 'rr_cv', 'RR hop ly', 'xs dinh', 'PSD', 'cong', 'cong4',
           'hoc', 'hop nhat k=%d' % k_best, 'ORACLE']
    x = np.arange(len(names)); w = .38
    a = ax[0, 1]
    a.bar(x - w / 2, [tables['s22'][n]['mean'] for n in names], w, color='#1f77b4', label='22 chu the (trong mien)')
    a.bar(x + w / 2, [tables['cinc'][n]['mean'] for n in names], w, color='#ef6c00', label='CinC 75 (ngoai mien)')
    a.axhline(tables['cinc']['psd']['mean'], color='#ef6c00', ls=':', lw=1)
    a.axhline(tables['s22']['psd']['mean'], color='#1f77b4', ls=':', lw=1)
    a.set_xticks(x); a.set_xticklabels(lbl, rotation=40, ha='right', fontsize=8)
    a.set_ylabel('F1 trung binh muc ban ghi (%)'); a.set_ylim(50, 100)
    a.set_title('B. F1 trung binh theo quy tac chon kenh', fontsize=10)
    a.legend(fontsize=8); a.grid(alpha=.25, axis='y')

    # C: hieu so vs PSD tren CinC voi KTC
    a = ax[1, 0]
    nn = ['gate', 'gate4', 'rrcv', 'peakprob', 'rrplaus', 'fuse', 'learned', 'oracle']
    ll = ['cong', 'cong4', 'rr_cv', 'xs dinh', 'RR hop ly', 'hop nhat k=%d' % k_best, 'hoc', 'ORACLE']
    y = np.arange(len(nn))
    d = [tables['cinc'][n]['diff_vs_psd'] for n in nn]
    lo = [tables['cinc'][n]['diff_vs_psd'] - tables['cinc'][n]['ci95'][0] for n in nn]
    hi = [tables['cinc'][n]['ci95'][1] - tables['cinc'][n]['diff_vs_psd'] for n in nn]
    a.errorbar(d, y, xerr=[lo, hi], fmt='o', color='#2e7d32', capsize=4)
    a.axvline(0, color='#c62828', lw=1.2)
    a.set_yticks(y); a.set_yticklabels(ll, fontsize=9); a.invert_yaxis()
    a.set_xlabel('hieu F1 so voi moc PSD (diem), CinC 75')
    a.set_title('C. Hieu so vs PSD tren CinC 75, KTC95 cluster bootstrap', fontsize=10)
    a.grid(alpha=.25, axis='x')

    # D: so ban ghi F1 < 50 va >= 90
    a = ax[1, 1]
    nn2 = ['psd', 'gate', 'gate4', 'rrcv', 'peakprob', 'rrplaus', 'fuse', 'learned', 'oracle']
    ll2 = ['PSD', 'cong', 'cong4', 'rr_cv', 'xs dinh', 'RR hop ly', 'hop nhat', 'hoc', 'ORACLE']
    x = np.arange(len(nn2))
    a.bar(x - .2, [tables['cinc'][n]['ge90'] for n in nn2], .4, color='#2e7d32', label='F1 >= 90')
    a.bar(x + .2, [tables['cinc'][n]['lt50'] for n in nn2], .4, color='#c62828', label='F1 < 50')
    a.set_xticks(x); a.set_xticklabels(ll2, rotation=40, ha='right', fontsize=8)
    a.set_ylabel('so ban ghi / 75'); a.set_title('D. Phan bo ban ghi tren CinC 75', fontsize=10)
    a.legend(fontsize=8); a.grid(alpha=.25, axis='y')

    fig.suptitle('Chon kenh mu nhan: quy tac PSD hien tai vs 7 quy tac khai bao truoc', fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=140)
    plt.close(fig)


if __name__ == '__main__':
    main()
