# -*- coding: utf-8 -*-
"""
luongcuc.py -- E1: kiem chung gia thuyet LUONG CUC cua bai toan fQRS don kenh.

Nguon so (chi doc, khong tinh lai mo hinh):
  analysis/luongcuc_feat.json          dai luong tin hieu 22 chu the (luongcuc_feat.py)
  baselines/powermf_fair_stats.json    rely / pmf1 / pmf4 muc chu the
  pilot_evidence/band_tcn.json         F1 tung dai loc tren chinh TCN
  analysis/gate22_results.json         diem cong tu choi muc ban ghi (khong nhin nhan)
  analysis/gate22_cinc.json            diem cong tren 75 ban ghi CinC (zero-shot)
  benchmark_dpss/eval_cinc75.json      F1 muc ban ghi m22 / m5 tren CinC 75
  benchmark_dpss/eval_12_cinc.json     F1 muc ban ghi m12 tren CinC 75
  benchmark_dpss/eval_22.json          sieu du lieu 22 chu the (nhan co / khong co)

Ket qua: analysis/luongcuc_results.json, analysis/fig_luongcuc.png
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, itertools, math
import numpy as np
from scipy import stats
import diptest
from sklearn.mixture import GaussianMixture
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
J = lambda *p: json.load(open(os.path.join(ROOT, *p), encoding='utf-8'))
RNG = np.random.default_rng(0)
HARD3 = ['B2_03', 'B1_06', 'B1_07']
OUT = {}

# ------------------------------------------------------------------ 0. gom bang 22 chu the
feat = {r['record']: r for r in J('analysis', 'luongcuc_feat.json')['rows']}
pmf = {r['rec']: r for r in J('baselines', 'powermf_fair_stats.json')['per_subject']}
bt = J('pilot_evidence', 'band_tcn.json')
band = {b['band']: b['rows'] for b in bt['results']}
gate22 = {r['record']: r for r in J('analysis', 'gate22_results.json')['muc_ban_ghi']['bang']}
ev22 = J('benchmark_dpss', 'eval_22.json')['subjects']

SUBJ = sorted(feat)
T = []
for s in SUBJ:
    row = dict(feat[s])
    row['rely'] = pmf[s]['rely']; row['pmf4'] = pmf[s]['pmf4']; row['pmf1'] = pmf[s]['pmf1']
    row['d_rely_pmf4'] = pmf[s]['rely'] - pmf[s]['pmf4']
    row['d_rely_pmf1'] = pmf[s]['rely'] - pmf[s]['pmf1']
    row['b1060'] = band['10-60'][s]['F1_psd']; row['b145'] = band['1-45'][s]['F1_psd']
    row['b390'] = band['3-90'][s]['F1_psd']
    row['d_band'] = row['b1060'] - row['b145']
    row['gate_score'] = gate22[s]['score']
    row['rank_least_reliable'] = gate22[s]['rank_least_reliable']
    row['maternal_lock'] = gate22[s]['maternal_lock']
    m = ev22[s]['meta']
    row['n_ref_flag0'] = m.get('n_ref_flag0', 0)
    row['frac_flag0'] = m.get('n_ref_flag0', 0) / max(1, ev22[s]['n_ref'])
    row['F1_verified_only'] = ev22[s]['model_22'].get('F1_psd_verified_only', None)
    row['jitter_ms'] = ev22[s]['model_22']['jitter_psd']
    row['hard3'] = s in HARD3
    T.append(row)
OUT['bang_22'] = T

FEATS = ['fsnr_db', 'mf_ratio_db', 'fsnr_vs_resid_db', 'resid_m_frac', 'overlap100', 'overlap_excess',
         'fhr_bpm', 'rr_sd_ms', 'rr_cv', 'hum50_frac', 'drift_frac', 'duration_s', 'n_ref',
         'maternal_lock', 'gate_score']
DUNG_NHAN = {'fsnr_db': True, 'mf_ratio_db': True, 'fsnr_vs_resid_db': True, 'resid_m_frac': False,
             'overlap100': True, 'overlap_excess': True, 'fhr_bpm': True, 'rr_sd_ms': True,
             'rr_cv': True, 'hum50_frac': False, 'drift_frac': False, 'duration_s': False,
             'n_ref': True, 'maternal_lock': False, 'gate_score': False}

# ------------------------------------------------------------------ 1. cau hoi 1: tuong quan + tach nhom
def spear(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    r, p = stats.spearmanr(a[m], b[m])
    return float(r), float(p), int(m.sum())


targets = {'F1_rely': [r['rely'] for r in T],
           'diff_rely_pmf4': [r['d_rely_pmf4'] for r in T],
           'diff_band_1060_145': [r['d_band'] for r in T]}

q1 = {'tuong_quan': {}, 'tach_nhom': {}, 'n_so_sanh': len(FEATS) * len(targets)}
for f in FEATS:
    v = [r[f] for r in T]
    q1['tuong_quan'][f] = {'dung_nhan': DUNG_NHAN[f]}
    for tn, tv in targets.items():
        r, p, n = spear(v, tv)
        q1['tuong_quan'][f][tn] = {'rho': r, 'p': p, 'n': n,
                                   'p_bonferroni': min(1.0, p * len(FEATS) * len(targets))}

# kha nang tach 3 ban kho khoi 19 ban con lai
C3 = math.comb(22, 3)
for f in FEATS:
    v = np.array([r[f] for r in T], float)
    idx_hard = [i for i, r in enumerate(T) if r['hard3']]
    for sign, name in ((1, 'tang'), (-1, 'giam')):
        pass
    order = np.argsort(v)                      # tang dan
    ranks_asc = {SUBJ[i]: int(np.where(order == i)[0][0]) + 1 for i in range(len(SUBJ))}
    rk = sorted(ranks_asc[s] for s in HARD3)
    rk_desc = sorted(len(SUBJ) + 1 - ranks_asc[s] for s in HARD3)
    # AUC tach nhom (Mann-Whitney), lay huong thuan loi
    hard = v[idx_hard]; easy = np.delete(v, idx_hard)
    u = stats.mannwhitneyu(hard, easy, alternative='two-sided')
    auc = float(u.statistic / (len(hard) * len(easy)))
    # khoang trong: gia tri cuc tri thu 3 vs thu 4 theo huong thuan loi
    vs = np.sort(v) if auc < 0.5 else np.sort(v)[::-1]
    gap = float(abs(vs[2] - vs[3])); spread19 = float(np.std(vs[3:]))
    q1['tach_nhom'][f] = {
        'dung_nhan': DUNG_NHAN[f],
        'hang_3_ban_kho_tang_dan': rk, 'hang_3_ban_kho_giam_dan': rk_desc,
        'la_3_cuc_tri': bool(rk == [1, 2, 3] or rk_desc == [1, 2, 3]),
        'auc_hard_vs_easy': auc, 'p_mannwhitney': float(u.pvalue),
        'p_ngau_nhien_neu_3_cuc_tri': (2.0 / C3) if (rk == [1, 2, 3] or rk_desc == [1, 2, 3]) else None,
        'gia_tri_3_ban_kho': {s: float(v[SUBJ.index(s)]) for s in HARD3},
        'khoang_trong_cuc_tri_3_4': gap, 'sd_19_con_lai': spread19,
        'ti_so_khoang_trong_tren_sd19': float(gap / spread19) if spread19 > 0 else None}

best = max(q1['tach_nhom'], key=lambda f: abs(q1['tach_nhom'][f]['auc_hard_vs_easy'] - 0.5))
q1['dai_luong_tach_tot_nhat'] = best
OUT['cau_hoi_1'] = q1
print('[Q1] dai luong tach tot nhat:', best, q1['tach_nhom'][best])

# ------------------------------------------------------------------ 2. cau hoi 2: luong cuc?
cinc = J('benchmark_dpss', 'eval_cinc75.json')
recs75 = cinc['records']
F75 = np.array([r['m22']['F1_psd'] for r in recs75], float)
N75 = np.array([r['n_ref'] for r in recs75], float)
NAME75 = [r['record'] for r in recs75]
F22 = np.array([r['rely'] for r in T], float)
NREF22 = np.array([r['n_ref'] for r in T], float)


def logit_F1(F, nref):
    """F1 (%) -> logit, xu ly tran 100 va san 0 bang hieu chinh lien tuc theo do phan giai
    cua chinh ban ghi: mot nhip sai lam F1 doi khoang 1/(2*n_ref) don vi ti le -> eps = 1/(4*n_ref)."""
    p = np.clip(F / 100.0, 0, 1)
    eps = 1.0 / (4.0 * np.maximum(nref, 1))
    p = np.clip(p, eps, 1 - eps)
    return np.log(p / (1 - p)), eps


L75, eps75 = logit_F1(F75, N75)
L22, eps22 = logit_F1(F22, NREF22)
LOG1M75 = np.log10(100.0 - np.minimum(F75, 100 - 100 * eps75))
LOG1M22 = np.log10(100.0 - np.minimum(F22, 100 - 100 * eps22))


def dip(x, name):
    d, p = diptest.diptest(np.asarray(x, float))
    return {'ten': name, 'dip': float(d), 'p': float(p), 'n': int(len(x))}


def gmm_bic(x, name, seed=0):
    X = np.asarray(x, float).reshape(-1, 1)
    out = {'ten': name, 'n': int(len(x))}
    for k in (1, 2, 3):
        g = GaussianMixture(k, covariance_type='full', n_init=20, random_state=seed,
                            reg_covar=1e-4).fit(X)
        out['k%d' % k] = {'bic': float(g.bic(X)), 'aic': float(g.aic(X)),
                          'weights': [float(w) for w in g.weights_],
                          'means': [float(m) for m in g.means_.ravel()],
                          'sds': [float(np.sqrt(c)) for c in g.covariances_.ravel()]}
    out['delta_bic_1_tru_2'] = out['k1']['bic'] - out['k2']['bic']
    out['k_tot_nhat_theo_bic'] = int(np.argmin([out['k%d' % k]['bic'] for k in (1, 2, 3)]) + 1)
    return out


q2 = {'canh_bao_tran': ('F1 bi chan tren o 100 nen phan bo bi don ve bien phai. Da lap lai moi kiem dinh '
                        'tren thang logit voi hieu chinh lien tuc eps = 1/(4*n_ref) rieng tung ban ghi '
                        '(mot nhip sai lam F1 doi ~1/(2*n_ref)), va tren thang log10(100-F1). '
                        'Ket luan chi duoc coi la vung neu no giong nhau tren ca ba thang.'),
      'so_ban_ghi_F1_bang_100': int((F75 >= 99.999).sum()),
      'so_chu_the_F1_bang_100': int((F22 >= 99.999).sum()),
      'dip': {}, 'gmm': {}, 'mo_ta': {}}
for nm, x in (('cinc75_F1_tho', F75), ('cinc75_logit', L75), ('cinc75_log10_100_tru_F1', LOG1M75),
              ('s22_F1_tho', F22), ('s22_logit', L22), ('s22_log10_100_tru_F1', LOG1M22)):
    q2['dip'][nm] = dip(x, nm)
    q2['gmm'][nm] = gmm_bic(x, nm)
    q2['mo_ta'][nm] = {'mean': float(np.mean(x)), 'sd': float(np.std(x, ddof=1)),
                       'median': float(np.median(x)), 'min': float(np.min(x)), 'max': float(np.max(x))}
# doi chung bat buoc: luong cuc tren CinC co phai chi la loi CHON KENH (PSD mu nhan) khong?
ORA = np.array([r['m22']['F1_oracle'] for r in recs75], float)
LD0 = np.array([r['m22']['F1_lead0'] for r in recs75], float)
MN4 = np.array([r['m22']['F1_mean4'] for r in recs75], float)
BAD = np.array([bool(r['bad_annotation']) for r in recs75])
q2['doi_chung_chon_kenh'] = {
    'cau_hoi': ('Neu luong cuc chi do quy tac chon kenh PSD mu nhan that bai tren mot so ban ghi thi '
                'phan bo F1 tren kenh TOT NHAT (oracle) phai het luong cuc.'),
    'oracle': {'mo_ta': 'F1 tren kenh tot nhat trong 4 (oracle, khong trien khai duoc)',
               'dip_tho': dip(ORA, 'oracle_tho'), 'dip_logit': dip(logit_F1(ORA, N75)[0], 'oracle_logit'),
               'gmm_logit': gmm_bic(logit_F1(ORA, N75)[0], 'oracle_logit'),
               'mean': float(ORA.mean()), 'n_lt80': int((ORA < 80).sum()), 'n_lt50': int((ORA < 50).sum())},
    'lead0': {'dip_logit': dip(logit_F1(LD0, N75)[0], 'lead0_logit'), 'mean': float(LD0.mean()),
              'n_lt80': int((LD0 < 80).sum())},
    'mean4': {'dip_logit': dip(logit_F1(MN4, N75)[0], 'mean4_logit'), 'mean': float(MN4.mean()),
              'n_lt80': int((MN4 < 80).sum())}}
# doi chung 2: bo 7 ban ghi bi danh dau nhan xau
q2['doi_chung_bo_nhan_xau'] = {
    'n_bo': int(BAD.sum()), 'nguon': cinc['meta']['bad_annotation_source'],
    'dip_tho': dip(F75[~BAD], 'cinc68_tho'), 'dip_logit': dip(logit_F1(F75[~BAD], N75[~BAD])[0], 'cinc68_logit'),
    'gmm_logit': gmm_bic(logit_F1(F75[~BAD], N75[~BAD])[0], 'cinc68_logit')}
q2['nguong_thuc_te'] = {'cinc75_F1_ge_95': int((F75 >= 95).sum()), 'cinc75_F1_lt_80': int((F75 < 80).sum()),
                        'cinc75_F1_lt_50': int((F75 < 50).sum()),
                        's22_F1_ge_95': int((F22 >= 95).sum()), 's22_F1_lt_95': int((F22 < 95).sum())}
OUT['cau_hoi_2'] = q2
print('[Q2] dip CinC75 tho p=%.4g logit p=%.4g | BIC1-BIC2 logit %.2f'
      % (q2['dip']['cinc75_F1_tho']['p'], q2['dip']['cinc75_logit']['p'],
         q2['gmm']['cinc75_logit']['delta_bic_1_tru_2']))

# ------------------------------------------------------------------ 3. cau hoi 3: hieu ung de vs kho
def paired(a, b, lab):
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b
    n = len(d)
    out = {'ten': lab, 'n': n, 'mean_a': float(np.mean(a)), 'mean_b': float(np.mean(b)),
           'hieu_trung_binh': float(np.mean(d)), 'hieu_trung_vi': float(np.median(d)),
           'sd_hieu': float(np.std(d, ddof=1)) if n > 1 else None,
           'thang': int((d > 0).sum()), 'thua': int((d < 0).sum()), 'hoa': int((d == 0).sum())}
    if n >= 3:
        bs = np.array([np.mean(RNG.choice(d, n, replace=True)) for _ in range(10000)])
        out['ci95_bootstrap'] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        try:
            out['p_wilcoxon'] = float(stats.wilcoxon(d).pvalue)
        except Exception:
            out['p_wilcoxon'] = None
    return out


# 3a. hai tieu chi chia nhom, deu KHONG nhin nhan F1
gs = np.array([r['gate_score'] for r in T])
hard_gate = set(np.array(SUBJ)[np.argsort(gs)[:3]])           # 3 diem cong thap nhat
hard_snr = set(np.array(SUBJ)[np.argsort([r['fsnr_db'] for r in T])[:3]])
q3 = {'tieu_chi_chia': {
        'cong_tu_choi': {'mo_ta': 'ba chu the co diem cong thap nhat (analysis/gate22_results.json, '
                                  'khong nhin nhan)', 'nhom_kho': sorted(hard_gate)},
        'fsnr': {'mo_ta': 'ba chu the co fSNR thap nhat (CO dung nhan de dinh vi phuc bo thai -- '
                          'khong phai tieu chi trien khai duoc)', 'nhom_kho': sorted(hard_snr)}},
      'bang_hieu_ung': {}}

for crit, hardset in (('cong_tu_choi', hard_gate), ('fsnr', hard_snr)):
    idx_h = [i for i, s in enumerate(SUBJ) if s in hardset]
    idx_e = [i for i, s in enumerate(SUBJ) if s not in hardset]
    blk = {}
    for lab, ka, kb in (('RelyFetal_vs_PMF4', 'rely', 'pmf4'),
                        ('RelyFetal_vs_PMF1', 'rely', 'pmf1'),
                        ('band_10_60_vs_1_45', 'b1060', 'b145')):
        A = np.array([r[ka] for r in T]); B = np.array([r[kb] for r in T])
        blk[lab] = {'toan_bo': paired(A, B, lab + '|22'),
                    'nhom_de': paired(A[idx_e], B[idx_e], lab + '|de'),
                    'nhom_kho': paired(A[idx_h], B[idx_h], lab + '|kho')}
    q3['bang_hieu_ung'][crit] = blk

# 3b. CinC 75: m22 vs m5, m22 vs m12 -- chia bang diem cong zero-shot (khong nhin nhan)
gc = {r['record']: r for r in J('analysis', 'gate22_cinc.json')['bang']}
m12 = J('benchmark_dpss', 'eval_12_cinc.json')['cinc2013']['records']
F5 = np.array([r['m5']['F1_psd'] for r in recs75], float)
F12 = np.array([m12[n]['F1_psd'] for n in NAME75], float)
SC = np.array([gc[n]['score'] for n in NAME75], float)
k = 25                                     # phan tu 1/3 duoi theo diem cong
ord_sc = np.argsort(SC)
idx_h75 = ord_sc[:k]; idx_e75 = ord_sc[k:]
q3['cinc75'] = {'tieu_chi_chia': 'diem cong tu choi zero-shot (analysis/gate22_cinc.json), '
                                 'khong nhin nhan; nhom kho = 25 ban ghi diem thap nhat',
                'nhom_kho': [NAME75[i] for i in sorted(idx_h75)],
                'spearman_score_vs_F1': list(J('analysis', 'gate22_cinc.json')['spearman_score_vs_F1'])}
for lab, other in (('m22_vs_m5', F5), ('m22_vs_m12', F12)):
    q3['cinc75'][lab] = {'toan_bo': paired(F75, other, lab + '|75'),
                         'nhom_de': paired(F75[idx_e75], other[idx_e75], lab + '|de'),
                         'nhom_kho': paired(F75[idx_h75], other[idx_h75], lab + '|kho')}
# chia theo F1 cua chinh m22 (NHIN NHAN -- chi de doi chieu, co thien lech hoi quy ve trung binh)
ord_f = np.argsort(F75)
q3['cinc75_chia_theo_F1_m22_CO_THIEN_LECH'] = {
    'canh_bao': 'chia theo chinh F1 cua m22 la nhin nhan; ke ra chi de so sanh, khong dung ket luan',
    'm22_vs_m5_kho25': paired(F75[ord_f[:25]], F5[ord_f[:25]], 'm22_vs_m5|kho25'),
    'm22_vs_m5_de50': paired(F75[ord_f[25:]], F5[ord_f[25:]], 'm22_vs_m5|de50')}

# 3b-bis. DOI CHUNG TAM THUONG: hieu ung tap trung o nhom kho co the chi la HIEU UNG TRAN.
# Tren nhom de ca hai phuong phap da ~99-100 nen chenh lech BUOC phai nho.
# Hai cach kiem tra: (1) du dia con lai, (2) lam lai tren thang logit (khong con tran).
def logit_pct(F, nref):
    return logit_F1(np.asarray(F, float), np.asarray(nref, float))[0]


NREF22a = np.array([r['n_ref'] for r in T], float)
q3['doi_chung_hieu_ung_tran'] = {'cau_hoi': ('Neu tren nhom de ca hai phuong phap deu ~100 thi hieu so '
                                             'buoc phai nho -- tap trung hieu ung o nhom kho co the chi la '
                                             'he qua toan hoc cua tran 100, khong phai phat hien.'),
                                 'du_dia': {}, 'thang_logit': {}}
for crit, hardset in (('cong_tu_choi', hard_gate),):
    idx_h = [i for i, s in enumerate(SUBJ) if s in hardset]
    idx_e = [i for i, s in enumerate(SUBJ) if s not in hardset]
    for lab, ka, kb in (('RelyFetal_vs_PMF4', 'rely', 'pmf4'), ('band_10_60_vs_1_45', 'b1060', 'b145')):
        A = np.array([r[ka] for r in T]); B = np.array([r[kb] for r in T])
        head = 100.0 - B
        q3['doi_chung_hieu_ung_tran']['du_dia'][lab] = {
            'du_dia_trung_binh_nhom_de': float(head[idx_e].mean()),
            'du_dia_trung_binh_nhom_kho': float(head[idx_h].mean()),
            'hieu_ung_de_tren_du_dia': float(np.mean((A - B)[idx_e]) / head[idx_e].mean()),
            'hieu_ung_kho_tren_du_dia': float(np.mean((A - B)[idx_h]) / head[idx_h].mean()),
            'ghi_chu': ('du dia = 100 - F1 cua phuong phap doi chieu. Neu ti le hieu ung / du dia cung '
                        'bang nhau o hai nhom thi tap trung hieu ung chi la hieu ung tran.')}
        LA = logit_pct(A, NREF22a); LB = logit_pct(B, NREF22a)
        q3['doi_chung_hieu_ung_tran']['thang_logit'][lab] = {
            'toan_bo': paired(LA, LB, lab + '|logit|22'),
            'nhom_de': paired(LA[idx_e], LB[idx_e], lab + '|logit|de'),
            'nhom_kho': paired(LA[idx_h], LB[idx_h], lab + '|logit|kho')}
L75m22 = logit_pct(F75, N75); L75m5 = logit_pct(F5, N75); L75m12 = logit_pct(F12, N75)
for lab, LO, RAW in (('m22_vs_m5', L75m5, F5), ('m22_vs_m12', L75m12, F12)):
    q3['doi_chung_hieu_ung_tran']['thang_logit'][lab + '_cinc75'] = {
        'toan_bo': paired(L75m22, LO, lab + '|logit|75'),
        'nhom_de': paired(L75m22[idx_e75], LO[idx_e75], lab + '|logit|de'),
        'nhom_kho': paired(L75m22[idx_h75], LO[idx_h75], lab + '|logit|kho')}
    q3['doi_chung_hieu_ung_tran']['du_dia'][lab + '_cinc75'] = {
        'du_dia_trung_binh_nhom_de': float((100 - RAW[idx_e75]).mean()),
        'du_dia_trung_binh_nhom_kho': float((100 - RAW[idx_h75]).mean()),
        'hieu_ung_de_tren_du_dia': float(np.mean((F75 - RAW)[idx_e75]) / (100 - RAW[idx_e75]).mean()),
        'hieu_ung_kho_tren_du_dia': float(np.mean((F75 - RAW)[idx_h75]) / (100 - RAW[idx_h75]).mean())}

# 3c. cong suat thong ke
def power_sim(n, mu_overall=2.0, frac=1.0 / 7.0, sd_easy=0.9, sd_hard_rel=0.5, nsim=4000, alpha=0.05):
    mu_hard = mu_overall / frac
    pt = pw = 0
    for _ in range(nsim):
        carrier = RNG.random(n) < frac
        d = RNG.normal(0, sd_easy, n)
        d[carrier] += RNG.normal(mu_hard, sd_hard_rel * mu_hard, carrier.sum())
        if np.std(d, ddof=1) > 0:
            if stats.ttest_1samp(d, 0).pvalue < alpha:
                pt += 1
            try:
                if stats.wilcoxon(d).pvalue < alpha:
                    pw += 1
            except Exception:
                pass
    return pt / nsim, pw / nsim


d_band_easy = np.array([r['d_band'] for r in T if r['record'] not in hard_gate])
sd_easy = float(np.std(d_band_easy, ddof=1))
grid = [22, 30, 35, 40, 45, 50, 55, 60, 70, 80, 100, 120, 140, 160, 180, 200, 240, 300, 400, 600]
pw_rows = []
for n in grid:
    pt, pwil = power_sim(n, sd_easy=sd_easy)
    pw_rows.append({'n': n, 'power_ttest': pt, 'power_wilcoxon': pwil})
    print('[Q3] n=%3d  power t %.3f  wilcoxon %.3f' % (n, pt, pwil), flush=True)
n80 = next((r['n'] for r in pw_rows if r['power_ttest'] >= 0.8), None)
n80w = next((r['n'] for r in pw_rows if r['power_wilcoxon'] >= 0.8), None)
q3['cong_suat'] = {
    'mo_hinh': ('hieu so tung chu the: voi xac suat 1/7 chu the la "nguoi mang" va co hieu ung '
                'N(mu_hard, (0,5*mu_hard)^2) voi mu_hard = 2/(1/7) = 14 diem; con lai hieu ung 0. '
                'Nhieu nen N(0, sd_easy^2) voi sd_easy lay tu chinh du lieu (SD hieu so dai loc '
                'tren nhom de).'),
    'mu_tong_the': 2.0, 'ti_le_nguoi_mang': 1.0 / 7.0, 'mu_nguoi_mang': 14.0,
    'sd_easy_lay_tu_du_lieu': sd_easy, 'alpha': 0.05, 'nsim': 4000,
    'duong_cong': pw_rows, 'n_de_dat_power_0_8_ttest': n80, 'n_de_dat_power_0_8_wilcoxon': n80w,
    'so_sanh_neu_hieu_ung_deu': None}
# doi chieu: cung mu = 2 diem nhung DEU o moi chu the
pt_e, pw_e = power_sim(22, frac=1.0, sd_easy=sd_easy)
q3['cong_suat']['so_sanh_neu_hieu_ung_deu'] = {'n': 22, 'power_ttest': pt_e, 'power_wilcoxon': pw_e,
                                               'ghi_chu': 'cung hieu ung trung binh 2 diem nhung trai deu'}
OUT['cau_hoi_3'] = q3

# ------------------------------------------------------------------ 4. cau hoi 4: doi chung
q4 = {}
q4['chat_luong_nhan'] = {
    'mo_ta': ('B1 dung nhan GIAN TIEP (khu ECG me roi chuyen gia duyet, co cot co 0/1); '
              'B2 va ADFECGDB dung dien cuc da dau -> nhan truc tiep. Neu ba ban kho chi la ba ban '
              'nhan te nhat thi chung phai cung nhom nhan va phai co ti le nhip chua duyet cao.'),
    'bang': [{'record': r['record'], 'group': r['group'], 'nguon_nhan':
              ('gian tiep (B1)' if r['group'] == 'B1' else 'truc tiep (dien cuc da dau)'),
              'n_ref': r['n_ref'], 'n_ref_flag0': r['n_ref_flag0'], 'frac_flag0': r['frac_flag0'],
              'F1': r['rely'], 'F1_chi_nhip_da_duyet': r['F1_verified_only'], 'hard3': r['hard3']}
             for r in T]}
fl_h = [r['frac_flag0'] for r in T if r['hard3']]; fl_e = [r['frac_flag0'] for r in T if not r['hard3']]
q4['chat_luong_nhan']['frac_flag0_kho_vs_de'] = {
    'kho': fl_h, 'de_trung_binh': float(np.mean(fl_e)),
    'p_mannwhitney': float(stats.mannwhitneyu(fl_h, fl_e).pvalue)}
q4['do_dai'] = {'kho': {r['record']: r['duration_s'] for r in T if r['hard3']},
                'phan_bo_22': sorted(set(r['duration_s'] for r in T)),
                'ket_luan': None}
d_h = [r['duration_s'] for r in T if r['hard3']]; d_e = [r['duration_s'] for r in T if not r['hard3']]
q4['do_dai']['p_mannwhitney'] = float(stats.mannwhitneyu(d_h, d_e).pvalue)
q4['nguon_du_lieu'] = {'B2_03': 'Silesia B2 (chuyen da, 5 phut, nhan tu dien cuc da dau)',
                       'B1_06': 'Silesia B1 (thai ky, 20 phut, nhan gian tiep)',
                       'B1_07': 'Silesia B1 (thai ky, 20 phut, nhan gian tiep)',
                       'ghi_chu': 'khong cung mot tap con, khong cung quy trinh gan nhan, khong cung do dai'}

# bo 3 ban kho -> con 19: co "ba ban kho moi" khong?
F19 = np.array([r['rely'] for r in T if not r['hard3']])
N19 = np.array([r['n_ref'] for r in T if not r['hard3']])
L19, _ = logit_F1(F19, N19)
q4['sau_khi_bo_3'] = {'n': 19, 'F1': {'mean': float(F19.mean()), 'min': float(F19.min()),
                                      'max': float(F19.max()), 'sd': float(F19.std(ddof=1))},
                      'dip_tho': dip(F19, 'F1_19_tho'), 'dip_logit': dip(L19, 'F1_19_logit'),
                      'gmm_logit': gmm_bic(L19, 'F1_19_logit'),
                      'khoang_trong_lon_nhat': None}
sv = np.sort(F19); gaps = np.diff(sv)
q4['sau_khi_bo_3']['khoang_trong_lon_nhat'] = {
    'gia_tri': float(gaps.max()), 'o_giua': [float(sv[int(np.argmax(gaps))]), float(sv[int(np.argmax(gaps)) + 1])],
    'gap_lon_nhat_khi_co_ca_22': float(np.diff(np.sort(F22)).max())}
# khoang trong tren CinC 75 (mau lon hon)
sv75 = np.sort(F75); g75 = np.diff(sv75)
q4['khoang_trong_cinc75'] = {'gap_lon_nhat': float(g75.max()),
                             'o_giua': [float(sv75[int(np.argmax(g75))]), float(sv75[int(np.argmax(g75)) + 1])],
                             'so_ban_ghi_duoi_khoang_trong': int(np.argmax(g75) + 1)}
# bo nhom duoi tren CinC 75 -> 51 ban ghi tren khoang trong lon nhat: co khoang trong moi khong?
cut = int(np.argmax(g75)) + 1
Fup = sv75[cut:]
q4['cinc75_sau_khi_bo_nhom_duoi'] = {
    'n_bo': int(cut), 'n_con_lai': int(len(Fup)),
    'dip_tho': dip(Fup, 'cinc_tren_tho'),
    'gap_lon_nhat_con_lai': float(np.diff(Fup).max()),
    'o_giua': [float(Fup[int(np.argmax(np.diff(Fup)))]), float(Fup[int(np.argmax(np.diff(Fup))) + 1])],
    'ghi_chu': 'neu duoi dai lien tuc thi sau khi cat van con khoang trong lon tuong tu'}
OUT['cau_hoi_4'] = q4

# ------------------------------------------------------------------ hinh
fig = plt.figure(figsize=(13.5, 9.2))
gs_ = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.05], hspace=0.34, wspace=0.24)

# (A) histogram + KDE CinC 75
axA = fig.add_subplot(gs_[0, 0])
axA.hist(F75, bins=np.arange(0, 102.5, 5), color='#9ec5e8', edgecolor='white', label='75 ban ghi CinC')
kx = np.linspace(0, 100, 400)
kde = stats.gaussian_kde(F75, bw_method=0.30)
axA2 = axA.twinx()
axA2.plot(kx, kde(kx), color='#12436d', lw=2, label='KDE kenh PSD mu nhan')
axA2.plot(kx, stats.gaussian_kde(ORA, bw_method=0.30)(kx), color='#8c8c8c', lw=1.6, ls='--',
          label='KDE kenh tot nhat (oracle)')
axA2.set_yticks([]); axA2.legend(fontsize=8, loc='upper left', frameon=False)
axA.set_xlabel('F1 muc ban ghi (%), mo hinh 22 ca'); axA.set_ylabel('so ban ghi')
axA.set_title('(A) Phan bo F1 tren 75 ban ghi CinC 2013 set-a\n'
              'Hartigan dip: thang tho p = %.3f | thang logit p = %.4f | oracle (logit) p = %.2f'
              % (q2['dip']['cinc75_F1_tho']['p'], q2['dip']['cinc75_logit']['p'],
                 q2['doi_chung_chon_kenh']['oracle']['dip_logit']['p']), fontsize=10)
axA.axvline(95, color='#b3472b', ls='--', lw=1)
axA.text(94, axA.get_ylim()[1] * 0.92, 'F1 = 95', color='#b3472b', ha='right', fontsize=8)

# (B) phan tan dai luong tot nhat vs F1 (22 chu the)
axB = fig.add_subplot(gs_[0, 1])
xb = np.array([r[best] for r in T]); yb = F22
cols = ['#b3472b' if r['hard3'] else '#12436d' for r in T]
axB.scatter(xb, yb, c=cols, s=52, zorder=3)
for r, x0, y0 in zip(T, xb, yb):
    if r['hard3'] or r['record'] == 'B1_10' or r['record'] == 'B1_08':
        axB.annotate(r['record'], (x0, y0), textcoords='offset points', xytext=(6, -3), fontsize=8,
                     color='#b3472b' if r['hard3'] else '#555555')
rr, pp, _ = spear(xb, yb)
axB.set_xlabel(best + '  (dai luong tach tot nhat)'); axB.set_ylabel('F1 RelyFetal (%)')
axB.set_title('(B) %s vs F1, 22 chu the\nSpearman rho = %.3f, p = %.4f; do cam = 3 ban kho'
              % (best, rr, pp), fontsize=10)
axB.grid(alpha=0.25)

# (C) bang hieu ung
axC = fig.add_subplot(gs_[1, :]); axC.axis('off')
LG = q3['doi_chung_hieu_ung_tran']['thang_logit']
rows_tab = []
for lab, key_lg in (('RelyFetal 1 kenh vs Power-MF 4 kenh (22)', 'RelyFetal_vs_PMF4'),
                    ('dai 10-60 vs 1-45 Hz tren TCN (22)', 'band_10_60_vs_1_45')):
    b = q3['bang_hieu_ung']['cong_tu_choi'][key_lg]; g = LG[key_lg]
    rows_tab.append([lab,
                     '%+.2f' % b['toan_bo']['hieu_trung_binh'],
                     '%+.2f' % b['nhom_de']['hieu_trung_binh'],
                     '%+.2f' % b['nhom_kho']['hieu_trung_binh'],
                     '%+.2f' % g['nhom_de']['hieu_trung_binh'],
                     '%+.2f' % g['nhom_kho']['hieu_trung_binh'], '19 / 3'])
for lab, key in (('m22 vs m5 -- them du lieu (CinC 75)', 'm22_vs_m5'),
                 ('m22 vs m12 -- them du lieu (CinC 75)', 'm22_vs_m12')):
    b = q3['cinc75'][key]; g = LG[key + '_cinc75']
    rows_tab.append([lab,
                     '%+.2f' % b['toan_bo']['hieu_trung_binh'],
                     '%+.2f' % b['nhom_de']['hieu_trung_binh'],
                     '%+.2f' % b['nhom_kho']['hieu_trung_binh'],
                     '%+.2f' % g['nhom_de']['hieu_trung_binh'],
                     '%+.2f' % g['nhom_kho']['hieu_trung_binh'], '50 / 25'])
tab = axC.table(cellText=rows_tab,
                colLabels=['so sanh', 'toan bo\n(diem F1)', 'nhom DE\n(diem F1)', 'nhom KHO\n(diem F1)',
                           'nhom DE\n(logit)', 'nhom KHO\n(logit)', 'n de / kho'],
                cellLoc='center', loc='upper center',
                colWidths=[0.34, 0.10, 0.10, 0.10, 0.10, 0.10, 0.09])
tab.auto_set_font_size(False); tab.set_fontsize(9); tab.scale(1, 1.9)
for (i, j), c in tab.get_celld().items():
    c.set_edgecolor('#cccccc')
    if i == 0:
        c.set_facecolor('#12436d'); c.set_text_props(color='white', weight='bold')
    else:
        if j == 0:
            c.set_text_props(ha='left')
        if j == 3:
            c.set_facecolor('#f6e0d8')
        if j in (4, 5):
            c.set_facecolor('#eef2f6')
axC.set_title('(C) Hieu ung do duoc: toan bo mau vs nhom DE vs nhom KHO (nhom kho chia bang diem cong tu choi, '
              'KHONG nhin nhan)\nHai cot xam = lam lai tren thang logit de BO TRAN 100: tren thang do, hieu ung '
              '"them du lieu" KHONG con tap trung o nhom kho', fontsize=9.5, y=1.0)
fig.savefig(os.path.join(HERE, 'fig_luongcuc.png'), dpi=150, bbox_inches='tight', facecolor='white')
print('-> analysis/fig_luongcuc.png')

OUT['meta'] = {'ngay': time.strftime('%Y-%m-%d %H:%M:%S'),
               'lenh_chay_lai': 'python analysis/luongcuc_feat.py && python analysis/luongcuc.py',
               'nguon': ['analysis/luongcuc_feat.json', 'baselines/powermf_fair_stats.json',
                         'pilot_evidence/band_tcn.json', 'analysis/gate22_results.json',
                         'analysis/gate22_cinc.json', 'benchmark_dpss/eval_cinc75.json',
                         'benchmark_dpss/eval_12_cinc.json', 'benchmark_dpss/eval_22.json'],
               'seed': 0, 'n_boot': 10000}
json.dump(OUT, open(os.path.join(HERE, 'luongcuc_results.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('-> analysis/luongcuc_results.json')
