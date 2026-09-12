# -*- coding: utf-8 -*-
"""M4 -- tong hop: anh huong CHONG LAN, duong cong so chu the, can bang nguon, tang cuong.
Chay: python analysis/dulieu.py
Ket qua: analysis/dulieu_results.json, analysis/fig_dulieu.png
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, datetime
import numpy as np
from scipy.stats import wilcoxon, binomtest, t as tdist
from scipy.optimize import curve_fit

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))

LEAK = ['a03', 'a04', 'a05', 'a08', 'a12', 'a13', 'a14', 'a15', 'a17', 'a19', 'a20', 'a22', 'a23', 'a24', 'a25']
BAD = ['a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74']
RNG = np.random.default_rng(0)
NBOOT = 10000


def log(*a):
    print(' '.join(str(x) for x in a), flush=True)


def paired(a, b, nboot=NBOOT, seed=0):
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b; n = len(d)
    rng = np.random.default_rng(seed)
    bs = np.array([d[rng.integers(0, n, n)].mean() for _ in range(nboot)])
    se = d.std(ddof=1) / np.sqrt(n)
    tc = tdist.ppf(.975, n - 1) * se
    try:
        w = float(wilcoxon(a, b).pvalue)
    except Exception:
        w = float('nan')
    wins = int((d > 0).sum()); losses = int((d < 0).sum())
    return dict(n=n, mean_a=float(a.mean()), mean_b=float(b.mean()), mean_diff=float(d.mean()),
                median_diff=float(np.median(d)),
                ci95_bootstrap=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                ci95_t=[float(d.mean() - tc), float(d.mean() + tc)], wilcoxon_p=w,
                sign_test_p=float(binomtest(wins, wins + losses).pvalue) if wins + losses else float('nan'),
                wins=wins, losses=losses, ties=int((d == 0).sum()))


# =================================================================== 1. chong lan
def part_overlap():
    au = J('analysis/dulieu_audit.json')['overlap']
    ev = J('benchmark_dpss/eval_cinc75.json')
    recs = {r['record']: r for r in ev['records']}
    e12 = J('benchmark_dpss/eval_12_cinc.json')['cinc2013']['records']
    allr = sorted(recs)
    sets = {'75_goc': allr,
            '60_sach': [r for r in allr if r not in LEAK],
            '15_ro_ri': LEAK,
            '68_bo_chu_thich_sai': [r for r in allr if r not in BAD],
            '53_sach_va_chu_thich_dung': [r for r in allr if r not in LEAK and r not in BAD]}
    out = {'danh_sach_ro_ri': LEAK, 'n_ro_ri': len(LEAK),
           'bang_chung': {c: dict(ncc=au['signal_top3_per_cinc'][c][0][0],
                                  ban_ghi_goc=au['signal_top3_per_cinc'][c][0][1],
                                  rr_median_abs_diff_ms=au['rr_top3_per_cinc'][c][0][0]) for c in LEAK},
           'doi_chung_duong_tinh_ncc': au['signal_positive_control'],
           'ncc_lon_nhat_cac_ban_con_lai': float(max(v[0][0] for c, v in au['signal_top3_per_cinc'].items()
                                                     if c not in LEAK)),
           'bo': {}}
    for name, sel in sets.items():
        m5 = np.array([recs[r]['m5']['F1_psd'] for r in sel])
        m22 = np.array([recs[r]['m22']['F1_psd'] for r in sel])
        m12 = np.array([e12[r]['F1_psd'] for r in sel])
        orc = np.array([recs[r]['m22']['F1_oracle'] for r in sel])
        mean4 = np.array([recs[r]['m22']['F1_mean4'] for r in sel])
        lead0 = np.array([recs[r]['m22']['F1_lead0'] for r in sel])
        out['bo'][name] = dict(n=len(sel), m5_psd=float(m5.mean()), m12_psd=float(m12.mean()),
                               m22_psd=float(m22.mean()), m22_mean4=float(mean4.mean()),
                               m22_lead0=float(lead0.mean()), m22_oracle=float(orc.mean()),
                               du_dia_chon_kenh=float(orc.mean() - m22.mean()),
                               m22_median=float(np.median(m22)),
                               n_ge90=int((m22 >= 90).sum()), n_lt50=int((m22 < 50).sum()),
                               m22_vs_m5=paired(m22, m5), m22_vs_m12=paired(m22, m12),
                               m12_vs_m5=paired(m12, m5))
    a = out['bo']['75_goc']; b = out['bo']['60_sach']
    out['thoi_phong'] = dict(m5=a['m5_psd'] - b['m5_psd'], m12=a['m12_psd'] - b['m12_psd'],
                             m22=a['m22_psd'] - b['m22_psd'],
                             oracle=a['m22_oracle'] - b['m22_oracle'])
    return out


# =================================================================== 2. duong cong
def _inv(n, a, b):   return a - b / np.asarray(n, float)
def _log(n, a, b):   return a + b * np.log(np.asarray(n, float))
def _logit(p):       return np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
def _expit(z):       return 1.0 / (1.0 + np.exp(-z))


def fit_curve(n, y, name):
    n = np.asarray(n, float); y = np.asarray(y, float)
    out = {'n': list(n), 'F1': list(y), 'ten': name, 'fits': {}}
    # (a) F1 = a - b/n
    p, _ = curve_fit(_inv, n, y, p0=[y.max() + 5, 50.0], maxfev=20000)
    r = y - _inv(n, *p)
    out['fits']['a_minus_b_over_n'] = dict(a=float(p[0]), b=float(p[1]), rmse=float(np.sqrt((r ** 2).mean())),
                                           tiem_can=float(p[0]),
                                           du_bao={str(k): float(_inv(k, *p)) for k in (30, 50, 100, 200)})
    # (b) F1 = a + b log n
    p2 = np.polyfit(np.log(n), y, 1)
    r2 = y - (p2[0] * np.log(n) + p2[1])
    out['fits']['a_plus_b_logn'] = dict(a=float(p2[1]), b=float(p2[0]), rmse=float(np.sqrt((r2 ** 2).mean())),
                                        tiem_can=None,
                                        du_bao={str(k): float(p2[0] * np.log(k) + p2[1]) for k in (30, 50, 100, 200)})
    # (c) logit(F1/100) = a + b log n   -- ton trong tran 100
    z = _logit(y / 100.0)
    p3 = np.polyfit(np.log(n), z, 1)
    r3 = z - (p3[0] * np.log(n) + p3[1])
    out['fits']['logit_a_plus_b_logn'] = dict(a=float(p3[1]), b=float(p3[0]),
                                              rmse_logit=float(np.sqrt((r3 ** 2).mean())),
                                              tiem_can=100.0,
                                              du_bao={str(k): float(100 * _expit(p3[0] * np.log(k) + p3[1]))
                                                      for k in (30, 50, 100, 200)})
    out['ghi_chu'] = ('3 diem du lieu, 2 tham so moi dang -> chi con 1 bac tu do; moi du bao la NGOAI SUY, '
                      'do tin cay THAP, khong co khoang tin cay dung nghia')
    return out


def part_curve():
    ov = J('analysis/dulieu_results.json')['chong_lan'] if False else None
    ev = J('benchmark_dpss/eval_cinc75.json')
    recs = {r['record']: r for r in ev['records']}
    e12 = J('benchmark_dpss/eval_12_cinc.json')['cinc2013']['records']
    clean = [r for r in sorted(recs) if r not in LEAK]
    y_cinc = [float(np.mean([recs[r]['m5']['F1_psd'] for r in clean])),
              float(np.mean([e12[r]['F1_psd'] for r in clean])),
              float(np.mean([recs[r]['m22']['F1_psd'] for r in clean]))]
    ab = J('analysis/ablation_b1_results.json')
    y_b1 = [ab['B1']['mean_m5'], ab['B1']['mean_m12'], ab['B1']['mean_m22']]
    res = {'ngoai_mien_CinC60_sach': fit_curve([5, 12, 22], y_cinc, 'CinC 2013, 60 ban ghi SACH, quy tac PSD'),
           'trong_mien_B1_10': fit_curve([5, 12, 19], y_b1,
                                         '10 chu the B1 (cung tap kiem thu cho ca ba mo hinh); '
                                         'm22 = LOSO nen n huan luyen thuc = 19'),
           'ngoai_mien_CinC75_CU_BI_O_NHIEM': fit_curve([5, 12, 22],
                                                        [71.21375488793569, 74.33957014439426, 79.3986490628945],
                                                        'CHI DE DOI CHIEU -- 75 ban ghi co 15 ban ro ri')}
    return res


# =================================================================== 3. can bang nguon
def part_balance():
    au = J('analysis/dulieu_audit.json')['labels']
    PN = ['r01', 'r04', 'r07', 'r08', 'r10']
    B1 = ['B1_%02d' % i for i in range(1, 11)]
    B2 = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
    STRIDE = {'PhysioNet': 250, 'B1': 500, 'B2': 250}
    SEG = 1000; FS = 250; LEADS = 4
    out = {'nguon': {}}
    tot_s = tot_b = tot_seg = tot_exp = 0.0
    for g, tags in (('PhysioNet', PN), ('B1', B1), ('B2', B2)):
        s = sum(au[t]['duration_s'] for t in tags)
        b = sum(au[t]['n_beats'] for t in tags)
        nseg = sum(LEADS * max(0, int((au[t]['duration_s'] * FS - SEG) // STRIDE[g])) for t in tags)
        # so nhip mo hinh NHIN THAY moi epoch = so doan x nhip trung binh moi doan
        exp_ = sum(LEADS * max(0, int((au[t]['duration_s'] * FS - SEG) // STRIDE[g]))
                   * (au[t]['n_beats'] / au[t]['duration_s'] * SEG / FS) for t in tags)
        out['nguon'][g] = dict(n_chu_the=len(tags), giay=round(s, 1), phut=round(s / 60, 1), nhip=int(b),
                               stride_mau=STRIDE[g], n_doan_moi_epoch=int(nseg),
                               nhip_nhin_thay_moi_epoch=round(exp_, 0),
                               nhan='GIAN TIEP' if g == 'B1' else 'TRUC TIEP (dien cuc da dau)')
        tot_s += s; tot_b += b; tot_seg += nseg; tot_exp += exp_
    for g in out['nguon']:
        d = out['nguon'][g]
        d['ty_le_giay_pct'] = round(100 * d['giay'] / tot_s, 1)
        d['ty_le_nhip_pct'] = round(100 * d['nhip'] / tot_b, 1)
        d['ty_le_doan_pct'] = round(100 * d['n_doan_moi_epoch'] / tot_seg, 1)
        d['ty_le_nhip_nhin_thay_pct'] = round(100 * d['nhip_nhin_thay_moi_epoch'] / tot_exp, 1)
    out['tong'] = dict(giay=round(tot_s, 1), phut=round(tot_s / 60, 1), nhip=int(tot_b),
                       n_doan_moi_epoch=int(tot_seg), nhip_nhin_thay_moi_epoch=round(tot_exp, 0))
    out['he_so_can_bang_de_xuat'] = {g: round(tot_exp / 3.0 / out['nguon'][g]['nhip_nhin_thay_moi_epoch'], 3)
                                     for g in out['nguon']}
    return out


# =================================================================== 4. chat luong nhan
def part_labels():
    au = J('analysis/dulieu_audit.json')['labels']
    PN = ['r01', 'r04', 'r07', 'r08', 'r10']
    B1 = ['B1_%02d' % i for i in range(1, 11)]
    B2 = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
    cinc = au['_cinc']
    out = {'theo_nhom': {}, 'theo_chu_the': {k: v for k, v in au.items() if k != '_cinc'}}
    for g, tags in (('PhysioNet', PN), ('B1', B1), ('B2', B2), ('CinC2013_75', sorted(cinc))):
        src = cinc if g.startswith('CinC') else au
        f = lambda k: np.array([src[t][k] for t in tags], float)
        out['theo_nhom'][g] = dict(
            n=len(tags), nhip=int(f('n_beats').sum()),
            pct_rr_ngoai_dai_TB=round(float(f('pct_rr_out_of_range').mean()), 3),
            pct_rr_ngoai_dai_max=round(float(f('pct_rr_out_of_range').max()), 3),
            pct_rr_nhay25_TB=round(float(f('pct_rr_jump25').mean()), 3),
            n_ban_ghi_hoan_toan_sach=int((f('pct_rr_out_of_range') + f('pct_rr_jump25') == 0).sum()),
            gap_gt2s_tong=int(f('n_gap_gt2s').sum()), tong_giay_gap=round(float(f('total_gap_s').sum()), 2),
            pnn50_TB=round(float(f('pnn50').mean()), 2),
            do_phu_TB_pct=round(float(f('coverage_pct').mean()), 2))
    b1flag = {t: dict(n_flag0=au[t]['n_flag0'], pct=au[t]['pct_flag0'],
                      n_beats=au[t]['n_beats'],
                      n_beats_verified=au[t]['verified_only']['n_beats'] if 'verified_only' in au[t] else au[t]['n_beats'],
                      rr_ngoai_dai_sau_loc=au[t]['verified_only']['pct_rr_out_of_range'] if 'verified_only' in au[t] else 0.0,
                      rr_max_sau_loc_ms=au[t]['verified_only']['rr_max_ms'] if 'verified_only' in au[t] else au[t]['rr_max_ms'])
             for t in B1}
    out['B1_co_0'] = dict(theo_ban_ghi=b1flag,
                          tong_nhip_co0=int(sum(v['n_flag0'] for v in b1flag.values())),
                          pct_tong=round(100.0 * sum(v['n_flag0'] for v in b1flag.values())
                                         / sum(v['n_beats'] for v in b1flag.values()), 3))
    try:
        se = J('benchmark_dpss/silesia_eval.json')['records']
        vo = {}
        for t in B1:
            r = se[t]
            lead = 'A%d' % r['psd_lead'] if 'A%d' % r['psd_lead'] in r['per_lead'] else list(r['per_lead'])[0]
            pl = r['per_lead'][lead]
            if 'verified_only' in pl:
                vo[t] = dict(F1_tat_ca=pl['F1'], F1_chi_co1=pl['verified_only']['F1'],
                             hieu=pl['verified_only']['F1'] - pl['F1'])
        if vo:
            d = np.array([v['hieu'] for v in vo.values()])
            out['B1_co_0']['anh_huong_loc_co0_len_F1_m5'] = dict(
                theo_ban_ghi=vo, hieu_TB=float(d.mean()), hieu_min=float(d.min()), hieu_max=float(d.max()),
                nguon='benchmark_dpss/silesia_eval.json (mo hinh m5, kenh PSD)')
    except Exception as e:
        out['B1_co_0']['anh_huong_loc_co0_len_F1_m5'] = 'khong doc duoc: %s' % e
    return out


# =================================================================== 5. tang cuong / can bang (thuc nghiem)
def part_exp():
    p = os.path.join(HERE, 'dulieu_exp.json')
    if not os.path.isfile(p):
        return {'trang_thai': 'chua co ket qua'}
    d = json.load(open(p, encoding='utf-8'))
    runs = d['runs']
    folds = sorted({r['fold'] for r in runs.values()})
    arms = d['meta']['arms']
    done = [f for f in folds if all('%s_f%02d' % (a, f) in runs for a in arms)]
    out = {'meta': d['meta'], 'fold_du_ca_ba_nhanh': done, 'n_chu_the': 0}
    if not done:
        out['trang_thai'] = 'chua fold nao du ca ba nhanh'
        return out
    subj, vals = [], {a: [] for a in arms}
    v4 = {a: [] for a in arms}
    for f in done:
        for tag in runs['%s_f%02d' % (arms[0], f)]['test_subjects']:
            subj.append(tag)
            for a in arms:
                vals[a].append(runs['%s_f%02d' % (a, f)]['F1_psd'][tag])
                v4[a].append(runs['%s_f%02d' % (a, f)]['F1_mean4'][tag])
    out['n_chu_the'] = len(subj); out['chu_the'] = subj
    out['F1_psd'] = {a: {t: round(v, 3) for t, v in zip(subj, vals[a])} for a in arms}
    out['trung_binh_F1_psd'] = {a: float(np.mean(vals[a])) for a in arms}
    out['trung_binh_F1_mean4'] = {a: float(np.mean(v4[a])) for a in arms}
    if 'base' in arms and 'noaug' in arms:
        out['tang_cuong_base_tru_noaug'] = paired(vals['base'], vals['noaug'])
        out['tang_cuong_base_tru_noaug_mean4'] = paired(v4['base'], v4['noaug'])
    if 'base' in arms and 'bal' in arms:
        out['can_bang_bal_tru_base'] = paired(vals['bal'], vals['base'])
        out['can_bang_bal_tru_base_mean4'] = paired(v4['bal'], v4['base'])
    if 'bal' in runs.get('bal_f%02d' % done[0], {}).get('arm', ''):
        pass
    bs = runs.get('bal_f%02d' % done[0], {}).get('balance_stats')
    if bs:
        out['can_bang_da_ap_dung'] = bs
    return out


def main():
    res = dict(meta=dict(date=str(datetime.datetime.now()), nguon_du_lieu=[
        'analysis/dulieu_audit.json', 'benchmark_dpss/eval_cinc75.json', 'benchmark_dpss/eval_12_cinc.json',
        'analysis/ablation_b1_results.json', 'benchmark_dpss/silesia_eval.json', 'model/train_22.json',
        'analysis/dulieu_exp.json']))
    log('-- chong lan --');  res['chong_lan'] = part_overlap()
    log('-- duong cong --'); res['duong_cong'] = part_curve()
    log('-- can bang --');   res['can_bang'] = part_balance()
    log('-- nhan --');       res['chat_luong_nhan'] = part_labels()
    log('-- thuc nghiem --');res['thuc_nghiem'] = part_exp()
    out = os.path.join(HERE, 'dulieu_results.json')
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    log('-> ' + out)
    b = res['chong_lan']['bo']
    log('CinC 75 goc  m22 %.2f | 60 sach m22 %.2f | thoi phong %.2f'
        % (b['75_goc']['m22_psd'], b['60_sach']['m22_psd'], res['chong_lan']['thoi_phong']['m22']))
    for k, v in res['duong_cong'].items():
        log(k, v['F1'], '-> 50 chu the:',
            {f: round(x['du_bao']['50'], 2) for f, x in v['fits'].items()})


if __name__ == '__main__':
    main()
