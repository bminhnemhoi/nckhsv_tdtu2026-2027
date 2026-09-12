# -*- coding: utf-8 -*-
"""
xacnhan.py -- R2: (3) tinh lai 22 chu the tren thang LOGIT, (4) ti le am tinh gia cua phep thu
nhin thay, (5) so seed 0 vs seed 1 o muc chu the. (2) bo thu ba: khong co nhan -> khong chay.

Khai bao truoc: analysis/xacnhan_khaibao.md (git ed819e3). CHI DOC tep co san, khong suy luan moi
(tru muc 3b dung phan du da luu san trong chandoan_cache.npz).
Dau ra: analysis/xacnhan_results.json, analysis/XACNHAN.md, analysis/fig_xacnhan.png
"""
import os, sys
for _v in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_v] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, glob, datetime, subprocess
import numpy as np
from scipy.stats import wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SEED = 0; NBOOT = 10000
NEW_RULES = ['gate', 'gate4', 'rrcv', 'peakprob', 'rrplaus', 'fuse', 'learned']
ORDER = ['psd'] + NEW_RULES + ['mean4', 'oracle']
LEAK15 = ['a03', 'a04', 'a05', 'a08', 'a12', 'a13', 'a14', 'a15', 'a17', 'a19', 'a20', 'a22', 'a23', 'a24', 'a25']
TOL_MS = 50; LOC_MS = 150; MAT_MS = 60; Q = 4
rng_global = np.random.default_rng(SEED)

ck = json.load(open(os.path.join(HERE, 'chonkenh_results.json'), encoding='utf-8'))
dul = json.load(open(os.path.join(HERE, 'dulieu_results.json'), encoding='utf-8'))
raw = json.load(open(os.path.join(HERE, 'chandoan_raw.json'), encoding='utf-8'))
CLEAN60 = dul['chon_kenh_60_sach']['ban_ghi_sach']
assert len(CLEAN60) == 60 and not (set(CLEAN60) & set(LEAK15))


def git_hash():
    try:
        return subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', 'analysis/xacnhan_khaibao.md'],
                                       cwd=ROOT).decode().strip()
    except Exception:
        return None


def boot_ci(d, nboot=NBOOT, seed=SEED):
    d = np.asarray(d, float); rng = np.random.default_rng(seed)
    b = d[rng.integers(0, len(d), size=(nboot, len(d)))].mean(1)
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def wilc(a, b):
    d = np.asarray(a) - np.asarray(b)
    if np.sum(np.abs(d) > 1e-12) == 0:
        return 1.0
    try:
        return float(wilcoxon(a, b, zero_method='wilcox').pvalue)
    except ValueError:
        return 1.0


def holm(p, names):
    idx = np.argsort(p); m = len(p); out = {}; prev = 0.0
    for r, i in enumerate(idx):
        v = min(1.0, max(prev, (m - r) * p[i])); prev = v; out[names[i]] = float(v)
    return out


def logit(p):
    return np.log(p / (1 - p))


def inv_logit(y):
    return 1 / (1 + np.exp(-y))


# ============================================================ VIEC 3: LOGIT
def clamp(F1, n, how):
    p = np.asarray(F1, float) / 100.0
    if how == 'A':
        return (p * n + 0.5) / (n + 1.0)
    if how == 'B':
        return np.minimum(p, 0.999)
    if how == 'C':
        return np.minimum(p, 0.995)
    raise ValueError(how)


def logit_arm(arm, recs_keep=None):
    F = ck['F1_tung_ban_ghi'][arm]
    names = sorted(F) if recs_keep is None else [r for r in sorted(F) if r in recs_keep]
    n_ref = {}
    for r in names:
        c = json.load(open(os.path.join(HERE, 'chonkenh_cache', '%s_%s.json' % (arm, r)), encoding='utf-8'))
        n_ref[r] = c['n_ref']
    n = np.array([n_ref[r] for r in names], float)
    out = {}
    for how in ('A', 'B', 'C'):
        Y = {rule: logit(clamp([F[r][rule] for r in names], n, how)) for rule in ORDER}
        tb = {}
        for rule in ORDER:
            d = Y[rule] - Y['psd']
            tb[rule] = dict(mean_logit=float(Y[rule].mean()), F1_tuong_ung=float(100 * inv_logit(Y[rule].mean())),
                            median_logit=float(np.median(Y[rule])), diff_vs_psd=float(d.mean()),
                            ci95=boot_ci(d), wilcoxon_p=wilc(Y[rule], Y['psd']),
                            wins=int((d > 1e-12).sum()), losses=int((d < -1e-12).sum()),
                            ties=int((np.abs(d) <= 1e-12).sum()), n=len(names))
        hp = holm([tb[r]['wilcoxon_p'] for r in NEW_RULES], NEW_RULES)
        for r in NEW_RULES:
            tb[r]['holm_p'] = hp[r]
        rank = sorted(NEW_RULES, key=lambda r: -tb[r]['mean_logit'])
        rank_raw = sorted(NEW_RULES, key=lambda r: -np.mean([F[x][r] for x in names]))
        out[how] = dict(bang=tb, xep_hang_7_quy_tac_moi=rank, dung_dau=rank[0],
                        xep_hang_tho_F1=rank_raw,
                        vuot_psd_ci=[r for r in NEW_RULES if tb[r]['ci95'][0] > 0],
                        vuot_psd_holm=[r for r in NEW_RULES if tb[r]['holm_p'] < 0.05])
    out['n_ref'] = n_ref
    out['ban_ghi'] = names
    out['logit_tung_ban_ghi_kepA'] = {r: {rule: float(logit(clamp([F[r][rule]], n_ref[r], 'A'))[0]) for rule in ORDER}
                                      for r in names}
    return out


L22 = logit_arm('s22')
L60 = logit_arm('cinc', set(CLEAN60))
tops = [L22[h]['dung_dau'] for h in 'ABC']
pp = L22['A']['bang']['peakprob']
post_hoc_gone = all(t == 'peakprob' for t in tops) and pp['ci95'][0] > 0
viec3 = dict(
    ket_qua_theo_kep={h: L22[h] for h in 'ABC'},
    dung_dau_theo_kep={h: L22[h]['dung_dau'] for h in 'ABC'},
    xep_hang_tho_F1=L22['A']['xep_hang_tho_F1'],
    peakprob_kepA=dict(hang=L22['A']['xep_hang_7_quy_tac_moi'].index('peakprob') + 1,
                       diff_vs_psd=pp['diff_vs_psd'], ci95=pp['ci95'], wilcoxon_p=pp['wilcoxon_p'], holm_p=pp['holm_p']),
    gate_kepA=dict(hang=L22['A']['xep_hang_7_quy_tac_moi'].index('gate') + 1,
                   **{k: L22['A']['bang']['gate'][k] for k in ('diff_vs_psd', 'ci95', 'wilcoxon_p', 'holm_p')}),
    van_de_hau_kiem_bien_mat=bool(post_hoc_gone),
    dieu_kien=('peakprob dung dau theo CA BA cach kep VA KTC95(peakprob-psd) tren logit khong chua 0 -- khai bao truoc'),
    n_ref=L22['n_ref'], logit_tung_chu_the_kepA=L22['logit_tung_ban_ghi_kepA'],
    cinc60_phu={h: dict(dung_dau=L60[h]['dung_dau'], xep_hang=L60[h]['xep_hang_7_quy_tac_moi'],
                        bang={r: {k: L60[h]['bang'][r][k] for k in ('mean_logit', 'F1_tuong_ung', 'diff_vs_psd', 'ci95', 'wilcoxon_p')}
                              for r in ORDER}) for h in 'ABC'})


# ============================================================ VIEC 4: PHEP THU NHIN THAY
ev = np.load(os.path.join(HERE, 'chandoan_events.npz'), allow_pickle=True)


def match_assign(det, ref, tol=TOL_MS):
    ref = np.asarray(ref, float); det = np.sort(np.asarray(det, float))
    ref2det = np.full(len(ref), -1, int); det2ref = np.full(len(det), -1, int)
    for i, d in enumerate(det):
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (ref2det < 0))[0]
        if len(ok):
            j = ok[int(np.argmin(dd[ok]))]; ref2det[j] = i; det2ref[i] = j
    return det, ref2det, det2ref


def near(v, arr):
    return np.inf if not len(arr) else float(np.min(np.abs(np.asarray(arr, float) - v)))


def beat_level(rec, lead):
    ref = ev['%s|ref' % rec].astype(float)
    det = ev['%s|L%d|det' % (rec, lead)].astype(float)
    z = ev['%s|L%d|z' % (rec, lead)].astype(float); tau = float(ev['%s|L%d|tau' % (rec, lead)])
    mq = ev['%s|L%d|mq' % (rec, lead)].astype(float) * Q
    det, r2d, d2r = match_assign(det, ref)
    tp = np.where(r2d >= 0)[0]; fn = np.where(r2d < 0)[0]
    d_un = det[d2r < 0]
    # FN phan loai nhu chandoan.py: e_lech -> c_me -> a/b
    ab = []
    for j in fn:
        r = ref[j]
        if TOL_MS < near(r, d_un) <= LOC_MS or near(r, mq) <= MAT_MS:
            continue
        ab.append(j)
    ab = np.array(ab, int)
    vis_tp = z[tp] >= tau if len(tp) else np.zeros(0, bool)
    return dict(n_ref=len(ref), n_TP=len(tp), n_FN=len(fn), n_ab=len(ab),
                miss_TP=int((~vis_tp).sum()),                 # am tinh gia: TP ma phep thu bao "khong thay"
                a_raw=int((z[ab] >= tau).sum()) if len(ab) else 0,
                b_raw=int((z[ab] < tau).sum()) if len(ab) else 0,
                z_tp_median=float(np.median(z[tp])) if len(tp) else np.nan,
                z_fn_median=float(np.median(z[fn])) if len(fn) else np.nan,
                frac_ref_visible=float(np.mean(z >= tau)), tau=tau)


def f1_of(dom, rec, lead):
    return raw[dom][rec]['per_lead'][str(lead)]['F1']


def domain_fnrate(dom, recs, which):
    rows = []
    for rec in recs:
        lead = raw[dom][rec]['psd_lead'] if which == 'psd' else raw[dom][rec]['oracle_lead']
        b = beat_level(rec, int(lead)); b['record'] = rec; b['lead'] = int(lead); b['F1'] = f1_of(dom, rec, int(lead))
        rows.append(b)
    tp = np.array([r['n_TP'] for r in rows], float); miss = np.array([r['miss_TP'] for r in rows], float)
    micro = miss.sum() / tp.sum()
    rng = np.random.default_rng(SEED); idx = rng.integers(0, len(rows), size=(NBOOT, len(rows)))
    bs = miss[idx].sum(1) / np.maximum(tp[idx].sum(1), 1)
    per_rec = miss / np.maximum(tp, 1)
    strata = {}
    for lab, lo, hi in (('F1>=90', 90, 1e9), ('50<=F1<90', 50, 90), ('F1<50', -1, 50)):
        m = np.array([(lo <= r['F1'] < hi) for r in rows])
        strata[lab] = dict(n_ban=int(m.sum()), n_TP=int(tp[m].sum()),
                           micro=float(miss[m].sum() / tp[m].sum()) if tp[m].sum() else None)
    a = sum(r['a_raw'] for r in rows); b = sum(r['b_raw'] for r in rows)
    s = 1 - micro
    a_corr_frac = float(np.clip(((a / (a + b)) - 0.05) / (s - 0.05), 0, 1)) if a + b else None
    return dict(n_ban=len(rows), n_TP=int(tp.sum()), n_am_tinh_gia=int(miss.sum()),
                ti_le_am_tinh_gia_micro=float(micro), ci95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                do_nhay_micro=float(1 - micro),
                ti_le_am_tinh_gia_theo_ban=dict(median=float(np.median(per_rec[tp > 0])), p90=float(np.percentile(per_rec[tp > 0], 90)),
                                                max=float(per_rec[tp > 0].max()), n_ban_tren_10pct=int((per_rec[tp > 0] > 0.10).sum()),
                                                n_ban_tren_25pct=int((per_rec[tp > 0] > 0.25).sum())),
                phan_tang_theo_F1=strata,
                nhom_ab_FN=dict(a_co_tin_hieu_raw=a, b_khong_tin_hieu_raw=b,
                                frac_a_raw=(a / (a + b)) if a + b else None, frac_a_hieu_chinh=a_corr_frac),
                tung_ban=[{k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in r.items()} for r in rows])


S22 = sorted(raw['subjects22'])
FN = {}
for which in ('psd', 'oracle'):
    FN['s22|' + which] = domain_fnrate('subjects22', S22, which)
    FN['cinc60|' + which] = domain_fnrate('cinc', CLEAN60, which)
    FN['cinc75|' + which] = domain_fnrate('cinc', sorted(raw['cinc']), which)
# kiem tra tai lap do nhay gop vong truoc (0,951 / 0,862 tinh tren kenh psd, 22 / 75)
kiem_tai_lap = dict(s22_psd_do_nhay=FN['s22|psd']['do_nhay_micro'], cinc75_psd_do_nhay=FN['cinc75|psd']['do_nhay_micro'],
                    ghi_chu='vong truoc: 0,951 (22) / 0,862 (CinC 75), tinh bang trong so TP tren per_lead sens_test_on_TP')

# ---- (3b) do dac hieu ngoai mau tren 3 ban co phan du luu san
cache = np.load(os.path.join(HERE, 'chandoan_cache.npz'), allow_pickle=True)


def visibility_parts(res250, ref250, mq250, fs=250, half_ms=30, blk_s=4.0):
    n = len(res250); a = np.abs(np.asarray(res250, float)); half = max(1, int(half_ms / 1000 * fs))
    blk = int(blk_s * fs); nb = max(1, int(np.ceil(n / blk)))
    keep = np.ones(n, bool)
    for p in ref250: keep[max(0, p - int(.04 * fs)):p + int(.04 * fs)] = False
    for p in mq250: keep[max(0, p - int(.06 * fs)):p + int(.06 * fs)] = False
    sig = np.empty(nb)
    for b in range(nb):
        s, t = b * blk, min(n, (b + 1) * blk); v = a[s:t][keep[s:t]]
        if len(v) < 50: v = a[s:t]
        sig[b] = 1.4826 * np.median(np.abs(v - np.median(v))) + 1e-12

    def zstat(pos):
        pos = np.asarray(pos, int); out = np.empty(len(pos))
        for i, p in enumerate(pos):
            s, t = max(0, p - half), min(n, p + half + 1)
            out[i] = (a[s:t].max() if t > s else 0.0) / sig[min(nb - 1, max(0, p) // blk)]
        return out
    safe = np.ones(n, bool)
    for p in ref250: safe[max(0, p - int(.12 * fs)):p + int(.12 * fs)] = False
    for p in mq250: safe[max(0, p - int(.08 * fs)):p + int(.08 * fs)] = False
    safe[:half + 1] = False; safe[max(0, n - half - 1):] = False
    return zstat, np.where(safe)[0]


spec = {}
for rec in ('B1_06', 'B1_07', 'B2_03'):
    ref250 = np.round(cache['%s_ref' % rec] / Q).astype(int)
    for lead in (1, 2, 3, 4):
        res = cache['%s_L%d_res' % (rec, lead)]; mq = cache['%s_L%d_mq' % (rec, lead)].astype(int)
        zstat, idx = visibility_parts(res, ref250, mq)
        rng0 = np.random.default_rng(0); used = rng0.choice(idx, size=min(3000, len(idx)), replace=False)
        tau = float(np.percentile(zstat(used), 95))
        tau_saved = float(ev['%s|L%d|tau' % (rec, lead)])
        rest = np.setdiff1d(idx, used); rng1 = np.random.default_rng(1)
        hold = rng1.choice(rest, size=min(3000, len(rest)), replace=False)
        fp_hold = float(np.mean(zstat(hold) >= tau))
        # vi tri "dinh me" (residual me) cach nhan thai >= 120 ms: null khac, kho hon
        far = np.ones(len(res), bool)
        for p in ref250: far[max(0, p - 30):p + 30] = False
        mqf = mq[(mq > 8) & (mq < len(res) - 8)]; mqf = mqf[far[mqf]]
        fp_mat = float(np.mean(zstat(mqf) >= tau)) if len(mqf) else None
        # diem giua hai nhan thai lien tiep (cach ca hai >= 120 ms), cach dinh me >= 80 ms
        mid = ((ref250[:-1] + ref250[1:]) // 2); mid = mid[(np.diff(ref250) >= 60)]
        okm = np.ones(len(res), bool)
        for p in mq: okm[max(0, p - 20):p + 20] = False
        mid = mid[(mid > 8) & (mid < len(res) - 8)]; mid = mid[okm[mid]]
        fp_mid = float(np.mean(zstat(mid) >= tau)) if len(mid) else None
        spec['%s|L%d' % (rec, lead)] = dict(tau_tinh_lai=tau, tau_da_luu=tau_saved, khop_tau=abs(tau - tau_saved) < 1e-3,
                                            fp_vi_tri_an_toan_ngoai_mau=fp_hold, n_ngoai_mau=int(len(hold)),
                                            fp_tai_dinh_me=fp_mat, n_dinh_me=int(len(mqf)),
                                            fp_diem_giua_nhan=fp_mid, n_diem_giua=int(len(mid)))
spec_summary = dict(
    khop_tau_tat_ca=bool(all(v['khop_tau'] for v in spec.values())),
    fp_an_toan_ngoai_mau_median=float(np.median([v['fp_vi_tri_an_toan_ngoai_mau'] for v in spec.values()])),
    fp_an_toan_ngoai_mau_max=float(max(v['fp_vi_tri_an_toan_ngoai_mau'] for v in spec.values())),
    fp_dinh_me_median=float(np.median([v['fp_tai_dinh_me'] for v in spec.values() if v['fp_tai_dinh_me'] is not None])),
    fp_dinh_me_max=float(max(v['fp_tai_dinh_me'] for v in spec.values() if v['fp_tai_dinh_me'] is not None)),
    fp_diem_giua_median=float(np.median([v['fp_diem_giua_nhan'] for v in spec.values() if v['fp_diem_giua_nhan'] is not None])),
    fp_diem_giua_max=float(max(v['fp_diem_giua_nhan'] for v in spec.values() if v['fp_diem_giua_nhan'] is not None)),
    ghi_chu='chi 3 ban kho trong mien (B1_06, B1_07, B2_03) co phan du luu san; khong dai dien cho CinC')

# ---- (3c) chia du dia tren 60 ban sach theo nhin thay, tho vs hieu chinh
s_pool = FN['cinc60|oracle']['do_nhay_micro']
rows60 = []
for rec in CLEAN60:
    r = raw['cinc'][rec]
    best_lead = max(r['per_lead'], key=lambda l: r['per_lead'][l]['frac_ref_visible'])
    e = r['per_lead'][best_lead]
    v = e['frac_ref_visible']
    s_rec = e['sens_test_on_TP'] if (e['TP'] >= 20 and np.isfinite(e['sens_test_on_TP']) and e['sens_test_on_TP'] > 0.05) else s_pool
    v_corr = float(np.clip((v - 0.05) / (s_rec - 0.05), 0, 1))
    rows60.append(dict(record=rec, F1_oracle=r['F1_oracle'], du_dia=(100 - r['F1_oracle']) / 60.0,
                       nhin_thay_tho=v, nhin_thay_hieu_chinh=v_corr, do_nhay_dung=s_rec, dung_pooled=s_rec == s_pool,
                       kenh_tot_nhat=int(best_lead), TP_kenh=e['TP']))
tot = sum(x['du_dia'] for x in rows60)
split = {}
for thr in (0.3, 0.5, 0.7):
    for key in ('nhin_thay_tho', 'nhin_thay_hieu_chinh'):
        lo = [x for x in rows60 if x[key] < thr]
        split['%s|%.1f' % (key, thr)] = dict(n_khong_thay=len(lo), diem_khong_thay=sum(x['du_dia'] for x in lo),
                                              pct_khong_thay=100 * sum(x['du_dia'] for x in lo) / tot,
                                              ban=[x['record'] for x in lo])
flip = [x['record'] for x in rows60 if x['nhin_thay_tho'] < 0.5 <= x['nhin_thay_hieu_chinh']]
# so sanh voi con so cu: 71% tren 67 ban (75 tru 8 gioi han cung), tho
viec4 = dict(
    dinh_nghia='am tinh gia = nhip TP (ghep +-50 ms) ma phep thu bao "khong nhin thay" (z < tau). Do dac hieu tai vi tri an toan = 95% theo dinh nghia (trong mau).',
    ti_le_am_tinh_gia=FN, kiem_tai_lap_do_nhay_vong_truoc=kiem_tai_lap,
    do_dac_hieu_ngoai_mau_3_ban=dict(tung_kenh=spec, tom_tat=spec_summary),
    du_dia_60_sach=dict(tong_du_dia=tot, do_nhay_pooled_dung_khi_thieu=s_pool, chia=split,
                        ban_doi_nhom_khi_hieu_chinh_nguong_0_5=flip, tung_ban=rows60,
                        con_so_cu='71,0% cua 6,36 diem tren 67 ban (75 tru 8 gioi han cung), tho, chua loai 15 ban sao chep'))
fn60 = FN['cinc60|psd']['ti_le_am_tinh_gia_micro']
viec4['quyet_dinh'] = dict(
    am_tinh_gia_micro_60_sach_psd=fn60, vuot_nguong_10pct=bool(fn60 > 0.10),
    pct_khong_thay_tho_0_5=split['nhin_thay_tho|0.5']['pct_khong_thay'],
    pct_khong_thay_hieu_chinh_0_5=split['nhin_thay_hieu_chinh|0.5']['pct_khong_thay'],
    ket_luan_mo_hinh_khong_nut_that_con_dung=bool(split['nhin_thay_hieu_chinh|0.5']['pct_khong_thay'] >= 50))

# ============================================================ VIEC 5: SEED
t0 = json.load(open(os.path.join(ROOT, 'model', 'train_22.json'), encoding='utf-8'))
t1 = json.load(open(os.path.join(ROOT, 'model', 'train_22_seed1.json'), encoding='utf-8'))
subj = sorted(t0['subjects']); assert sorted(t1['subjects']) == subj and len(subj) == 22
fold_same = all(sorted(t0['folds'][k]['test_subjects']) == sorted(t1['folds'][k]['test_subjects']) for k in t0['folds'])
seed_tb = {}
for key in ('F1_psd', 'F1_mean4', 'F1_oracle'):
    a0 = np.array([t0['subjects'][s][key] for s in subj]); a1 = np.array([t1['subjects'][s][key] for s in subj])
    d = a1 - a0
    seed_tb[key] = dict(seed0_mean=float(a0.mean()), seed1_mean=float(a1.mean()), diff_mean=float(d.mean()),
                        ci95=boot_ci(d), wilcoxon_p=wilc(a1, a0), n_lech_tren_1=int((np.abs(d) > 1).sum()),
                        n_lech_tren_5=int((np.abs(d) > 5).sum()), max_abs=float(np.abs(d).max()),
                        chu_the_lech_nhat=subj[int(np.argmax(np.abs(d)))],
                        tung_chu_the={s: [float(x), float(y)] for s, x, y in zip(subj, a0, a1)})
# ti le psd_lead trung nhau (chon kenh psd doc lap mo hinh -> phai trung)
psd_same = sum(1 for s in subj if t0['subjects'][s]['psd_lead'] == t1['subjects'][s]['psd_lead'])
d_psd = seed_tb['F1_psd']
viec5 = dict(checkpoint_seed1_ton_tai=False,
             ly_do='train_22.py chi luu checkpoint khi --tag rong; model/checkpoints/ khong co tep seed 1',
             peakprob_seed1_kha_thi=False, fold_giong_seed0=bool(fold_same), psd_lead_trung=psd_same,
             epochs=dict(seed0=t0['meta'].get('epochs'), seed1=t1['meta'].get('epochs')),
             bang=seed_tb,
             on_dinh_theo_seed=bool(abs(d_psd['diff_mean']) <= 1 and d_psd['ci95'][0] <= 0 <= d_psd['ci95'][1]))

# ============================================================ VIEC 2: bo thu ba
viec2 = dict(co_bo_thu_ba_co_nhan_that=False,
             da_kiem=[dict(bo='NIFEADB', tren_dia='26 ban .dat/.hea', nhan_fqrs=False,
                           bang_chung='PhysioNet 1.0.0 khong co .qrs/.atr/ANNOTATORS; nifeadb_loader.HAS_FETAL_ANNOTATIONS=False'),
                      dict(bo='NInFEA', tren_dia='2 .dat + 3 .hea (tai do)', nhan_fqrs=False,
                           bang_chung='khong co tep chu thich nhip; tham chieu goc la Doppler'),
                      dict(bo='nifecgdb (ecgca102 tham do)', tren_dia='1 ban EDF + .qrs', nhan_fqrs=False,
                           bang_chung='375 nhan/270 s, RR trung vi 0,695 s = 86 nhip/phut -> QRS ME; 55 ban tu MOT san phu'),
                      dict(bo='CinC 2013 set-b', tren_dia='khong', nhan_fqrs=False, bang_chung='nhan khong cong bo')],
             hanh_dong='KHONG chay mo hinh; xac nhan peakprob tren bo thu ba chua the thuc hien')

out = dict(meta=dict(ngay=str(datetime.datetime.now()), khai_bao_truoc='analysis/xacnhan_khaibao.md',
                     git_khai_bao=git_hash(), seed=SEED, n_boot=NBOOT, n_60_sach=len(CLEAN60),
                     nguon=['analysis/chonkenh_results.json', 'analysis/chonkenh_cache/', 'analysis/dulieu_results.json',
                            'analysis/chandoan_raw.json', 'analysis/chandoan_events.npz', 'analysis/chandoan_cache.npz',
                            'model/train_22.json', 'model/train_22_seed1.json'],
                     suy_luan_moi=False),
           viec2_bo_thu_ba=viec2, viec3_logit_22=viec3, viec4_phep_thu_nhin_thay=viec4, viec5_seed=viec5)
json.dump(out, open(os.path.join(HERE, 'xacnhan_results.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)

# ============================================================ HINH
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(2, 2, figsize=(13.5, 9.5))
LBL = dict(psd='PSD', gate='cổng', gate4='cổng4', rrcv='rr_cv', peakprob='peakprob', rrplaus='RR hợp lý', fuse='hợp nhất', learned='học', mean4='TB 4 kênh', oracle='oracle')
a = ax[0, 0]; rules = ['psd'] + NEW_RULES
x = np.arange(len(rules)); w = 0.27
for i, (how, col) in enumerate((('A', '#1f77b4'), ('B', '#ef6c00'), ('C', '#2e7d32'))):
    tb = L22[how]['bang']
    m = [tb[r]['mean_logit'] for r in rules]
    lo = [tb[r]['mean_logit'] - (tb['psd']['mean_logit'] + tb[r]['ci95'][0]) for r in rules]
    hi = [(tb['psd']['mean_logit'] + tb[r]['ci95'][1]) - tb[r]['mean_logit'] for r in rules]
    a.bar(x + (i - 1) * w, m, w, color=col, label='kẹp %s' % how, yerr=[lo, hi], capsize=2, error_kw=dict(lw=0.8))
a.set_xticks(x); a.set_xticklabels([LBL[r] for r in rules], rotation=30, ha='right', fontsize=8)
a.set_ylabel('logit(F1) trung bình, 22 chủ thể'); a.legend(fontsize=8); a.grid(alpha=.25, axis='y')
a.set_title('A. Xếp hạng trên logit — đứng đầu: A=%s, B=%s, C=%s' % tuple(tops), fontsize=10)

a = ax[0, 1]
for tag, col, mk in (('s22|psd', '#1f77b4', 'o'), ('cinc60|psd', '#ef6c00', 's')):
    rows = FN[tag]['tung_ban']
    a.scatter([r['F1'] for r in rows], [100 * r['miss_TP'] / max(r['n_TP'], 1) for r in rows], s=22, c=col, marker=mk, alpha=.8,
              label='%s (micro %.1f%%)' % ('22 chủ thể' if tag.startswith('s22') else '60 CinC sạch', 100 * FN[tag]['ti_le_am_tinh_gia_micro']))
a.axhline(10, color='#c62828', ls='--', lw=1); a.set_xlabel('F1 kênh PSD của bản ghi'); a.set_ylabel('% nhịp TP bị gán "không nhìn thấy"')
a.set_title('B. Tỉ lệ âm tính giả của phép thử nhìn thấy trên nhịp TP', fontsize=10); a.legend(fontsize=8); a.grid(alpha=.25)

a = ax[1, 0]
thr = [0.3, 0.5, 0.7]
a.bar(np.arange(3) - 0.2, [split['nhin_thay_tho|%.1f' % t]['pct_khong_thay'] for t in thr], 0.4, color='#90a4ae', label='tỉ lệ nhìn thấy THÔ')
a.bar(np.arange(3) + 0.2, [split['nhin_thay_hieu_chinh|%.1f' % t]['pct_khong_thay'] for t in thr], 0.4, color='#c62828', label='HIỆU CHỈNH theo độ nhạy')
a.axhline(50, color='k', ls=':', lw=1); a.axhline(71, color='#555', ls='--', lw=1); a.text(2.35, 71.5, 'cũ: 71% (67 bản, có rò rỉ)', fontsize=7, ha='right')
a.set_xticks(range(3)); a.set_xticklabels(['ngưỡng %.1f' % t for t in thr]); a.set_ylabel('% dư địa (100−F1 oracle) trên bản "không nhìn thấy"')
a.set_title('C. 60 bản CinC sạch: dư địa nằm trên bản không đo được tín hiệu', fontsize=10); a.legend(fontsize=8); a.grid(alpha=.25, axis='y')

a = ax[1, 1]
p0 = [seed_tb['F1_psd']['tung_chu_the'][s][0] for s in subj]; p1 = [seed_tb['F1_psd']['tung_chu_the'][s][1] for s in subj]
a.scatter(p0, p1, s=28, c='#1f77b4'); a.plot([50, 100], [50, 100], 'k--', lw=0.8)
for s, x0, y0 in zip(subj, p0, p1):
    if abs(x0 - y0) > 1: a.annotate(s, (x0, y0), fontsize=7, xytext=(3, 3), textcoords='offset points')
a.set_xlabel('F1 PSD seed 0'); a.set_ylabel('F1 PSD seed 1')
a.set_title('D. Seed 0 vs seed 1, 22 chủ thể: hiệu %+.2f [%+.2f;%+.2f]' % (d_psd['diff_mean'], *d_psd['ci95']), fontsize=10); a.grid(alpha=.25)
fig.suptitle('R2 — xác nhận: logit 22 chủ thể, âm tính giả phép thử nhìn thấy, seed (khai báo trước ed819e3)', fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(HERE, 'fig_xacnhan.png'), dpi=140); plt.close(fig)

# ============================================================ IN TOM TAT
print('git khai bao:', out['meta']['git_khai_bao'])
for how in 'ABC':
    tb = L22[how]['bang']
    print('\n== LOGIT 22, kep %s: dung dau %s | xep hang %s' % (how, L22[how]['dung_dau'], L22[how]['xep_hang_7_quy_tac_moi']))
    for r in ORDER:
        c = tb[r]
        print('  %-9s logitTB %6.3f (F1~%6.2f)  hieu %+6.3f [%+6.3f;%+6.3f] p=%.3g holm=%s  T/H/Th %d/%d/%d' % (
            r, c['mean_logit'], c['F1_tuong_ung'], c['diff_vs_psd'], *c['ci95'], c['wilcoxon_p'],
            ('%.3g' % c['holm_p']) if 'holm_p' in c else '-', c['wins'], c['ties'], c['losses']))
print('xep hang tho F1:', L22['A']['xep_hang_tho_F1'])
print('van de hau kiem bien mat:', post_hoc_gone)
print('\n== CinC60 logit dung dau:', {h: L60[h]['dung_dau'] for h in 'ABC'})
print('\n== AM TINH GIA phep thu nhin thay')
for k, v in FN.items():
    print('  %-14s n_TP %6d  am tinh gia %.3f [%.3f;%.3f]  trung vi ban %.3f  p90 %.3f  >10%%: %d ban  | tang: %s | a/b tho %d/%d, frac_a hc %s' % (
        k, v['n_TP'], v['ti_le_am_tinh_gia_micro'], *v['ci95'], v['ti_le_am_tinh_gia_theo_ban']['median'], v['ti_le_am_tinh_gia_theo_ban']['p90'],
        v['ti_le_am_tinh_gia_theo_ban']['n_ban_tren_10pct'], {a_: b_['micro'] for a_, b_ in v['phan_tang_theo_F1'].items()},
        v['nhom_ab_FN']['a_co_tin_hieu_raw'], v['nhom_ab_FN']['b_khong_tin_hieu_raw'], v['nhom_ab_FN']['frac_a_hieu_chinh']))
print('kiem tai lap:', kiem_tai_lap)
print('dac hieu ngoai mau 3 ban:', json.dumps(spec_summary, ensure_ascii=False))
print('\n== DU DIA 60 sach: tong %.2f' % tot)
for k, v in split.items():
    print('  %-28s n=%2d  %.2f diem  %.1f%%' % (k, v['n_khong_thay'], v['diem_khong_thay'], v['pct_khong_thay']))
print('doi nhom khi hieu chinh (0,5):', flip)
print('\n== SEED: fold giong:', fold_same, '| psd_lead trung', psd_same, '/22')
for k, v in seed_tb.items():
    print('  %-9s seed0 %.2f seed1 %.2f hieu %+.2f [%+.2f;%+.2f] p=%.3g  |d|>1: %d  |d|>5: %d  max %.2f (%s)' % (
        k, v['seed0_mean'], v['seed1_mean'], v['diff_mean'], *v['ci95'], v['wilcoxon_p'], v['n_lech_tren_1'], v['n_lech_tren_5'], v['max_abs'], v['chu_the_lech_nhat']))
print('\nDONE ->', os.path.join(HERE, 'xacnhan_results.json'))
