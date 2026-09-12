# -*- coding: utf-8 -*-
"""
Tong hop ket qua chan doan: pho loi, tran nang luc, tran dat duoc, ba ban ghi kho.
Doc:  analysis/chandoan_raw.json, analysis/chandoan_capacity.json, benchmark_dpss/eval_22.json,
      benchmark_dpss/eval_cinc75.json
Ghi:  analysis/chandoan_results.json, analysis/fig_chandoan.png
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
RAW = json.load(open(os.path.join(HERE, 'chandoan_raw.json'), encoding='utf-8'))
EV22 = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json'), encoding='utf-8'))
CAPF = os.path.join(HERE, 'chandoan_capacity.json')
CAP = json.load(open(CAPF, encoding='utf-8')) if os.path.isfile(CAPF) else None
OUT = os.path.join(HERE, 'chandoan_results.json')
PNG = os.path.join(HERE, 'fig_chandoan.png')

KEYS = ('a_bo_nhip_co_tin_hieu', 'b_khong_co_tin_hieu', 'c_me', 'e_lech', 'd1_doi', 'd2_ngau_nhien')
LABEL = {'a_bo_nhip_co_tin_hieu': '(a) bo nhip CO tin hieu',
         'b_khong_co_tin_hieu': '(b) khong co tin hieu do duoc',
         'c_me': '(c) lien quan nhip me',
         'e_lech': '(e) lech thoi diem',
         'd1_doi': '(d1) phat hien doi',
         'd2_ngau_nhien': '(d2) FP ngau nhien'}
COL = {'a_bo_nhip_co_tin_hieu': '#2a78d6', 'b_khong_co_tin_hieu': '#eb6834', 'c_me': '#1baf7a',
       'e_lech': '#eda100', 'd1_doi': '#e87ba4', 'd2_ngau_nhien': '#008300'}
BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')
HARD = ('B1_06', 'B1_07', 'B2_03')


def pick(rec, how):
    return str(rec['psd_lead'] if how == 'psd' else rec['oracle_lead'])


def spectrum(recs, how):
    """gop TAT CA loi tren tat ca ban ghi (micro) tren kenh chon theo 'how'."""
    tot = {k: 0 for k in KEYS}; tot_null = {k: 0.0 for k in KEYS}
    n_err = 0; n_err_null = 0.0; n_tp = n_fp = n_fn = 0
    sens_num = sens_den = 0.0
    fn_cls = {k: 0 for k in KEYS}; fp_cls = {k: 0 for k in KEYS}
    for r in recs:
        e = r['per_lead'][pick(r, how)]
        for k in KEYS:
            tot[k] += e['counts'][k]; tot_null[k] += e['counts_null'][k]
            fn_cls[k] += e['counts_FN'][k]; fp_cls[k] += e['counts_FP'][k]
        n_err += e['n_err']; n_err_null += e['counts_null']['n_err']
        n_tp += e['TP']; n_fp += e['FP']; n_fn += e['FN']
        if e['TP'] and np.isfinite(e['sens_test_on_TP']):
            sens_num += e['sens_test_on_TP'] * e['TP']; sens_den += e['TP']
    se = n_tp / (n_tp + n_fn) * 100 if n_tp + n_fn else 0
    pp = n_tp / (n_tp + n_fp) * 100 if n_tp + n_fp else 0
    out = dict(n_records=len(recs), n_TP=n_tp, n_FP=n_fp, n_FN=n_fn, n_err=n_err,
               micro_Se=se, micro_PPV=pp, micro_F1=2 * se * pp / (se + pp) if se + pp else 0,
               macro_F1=float(np.mean([r['per_lead'][pick(r, how)]['F1'] for r in recs])),
               counts=tot, counts_FN=fn_cls, counts_FP=fp_cls,
               pct={k: (100.0 * tot[k] / n_err if n_err else 0.0) for k in KEYS},
               pct_null={k: (100.0 * tot_null[k] / n_err_null if n_err_null else 0.0) for k in KEYS},
               n_err_null=n_err_null,
               err_per_1000_beats=1000.0 * n_err / max(n_tp + n_fn, 1),
               sensitivity_of_visibility_test=sens_num / sens_den if sens_den else float('nan'))
    # hieu chinh ti le nhin thay trong nhom (a)/(b): quan sat = p*nhay + (1-p)*0.05
    s = out['sensitivity_of_visibility_test']
    ab = tot['a_bo_nhip_co_tin_hieu'] + tot['b_khong_co_tin_hieu']
    if ab and np.isfinite(s) and s > 0.05:
        obs = tot['a_bo_nhip_co_tin_hieu'] / ab
        out['frac_a_within_ab_raw'] = obs
        out['frac_a_within_ab_corrected'] = float(np.clip((obs - 0.05) / (s - 0.05), 0, 1))
        out['pct_a_corrected'] = 100.0 * out['frac_a_within_ab_corrected'] * ab / n_err if n_err else 0.0
    return out


def ceiling(recs):
    g = lambda f: float(np.mean([f(r) for r in recs]))
    return dict(n=len(recs),
                F1_psd=g(lambda r: r['F1_psd']),
                F1_mean4=g(lambda r: r['F1_mean4']),
                F1_vote1=g(lambda r: r['fusion']['vote1']['F1']),
                F1_vote2=g(lambda r: r['fusion']['vote2']['F1']),
                F1_vote3=g(lambda r: r['fusion']['vote3']['F1']),
                F1_vote4=g(lambda r: r['fusion']['vote4']['F1']),
                Se_vote2=g(lambda r: r['fusion']['vote2']['Se']),
                PPV_vote2=g(lambda r: r['fusion']['vote2']['PPV']),
                F1_oracle_lead=g(lambda r: r['F1_oracle']),
                union_recall_ceiling=g(lambda r: r['fusion']['union_recall_ceiling']),
                union_F1_ceiling=g(lambda r: r['fusion']['union_F1_ceiling']))


def main():
    S22 = RAW['subjects22']; CIN = RAW['cinc']
    r22 = [S22[t] for t in sorted(S22)]
    c75 = [CIN[t] for t in sorted(CIN)]
    c68 = [CIN[t] for t in sorted(CIN) if t not in BAD_ANN]
    res = dict(meta=dict(date=str(datetime.datetime.now()), source='analysis/chandoan_raw.json',
                         n22=len(r22), ncinc=len(c75),
                         rule=RAW['meta']['rule'],
                         null='muc ngau nhien = dich vong toan bo chuoi phat hien 0.37/0.53/0.71 do dai ban ghi'))

    # ---------------- VIEC 1: pho loi
    res['pho_loi'] = {}
    for name, recs, how in (('22_chu_the_kenh_PSD', r22, 'psd'), ('22_chu_the_kenh_oracle', r22, 'oracle'),
                            ('CinC75_kenh_PSD', c75, 'psd'), ('CinC75_kenh_oracle', c75, 'oracle'),
                            ('CinC68_kenh_PSD', c68, 'psd')):
        res['pho_loi'][name] = spectrum(recs, how)
    # 19 chu the de vs 3 kho
    easy = [S22[t] for t in sorted(S22) if t not in HARD]
    hard = [S22[t] for t in HARD]
    res['pho_loi']['22_de19_kenh_PSD'] = spectrum(easy, 'psd')
    res['pho_loi']['22_kho3_kenh_PSD'] = spectrum(hard, 'psd')
    # CinC tach theo muc F1
    lo = [r for r in c75 if r['F1_psd'] < 50]; mid = [r for r in c75 if 50 <= r['F1_psd'] < 90]
    hi = [r for r in c75 if r['F1_psd'] >= 90]
    for nm, rr in (('CinC_F1_duoi50', lo), ('CinC_F1_50_90', mid), ('CinC_F1_tu90', hi)):
        if rr: res['pho_loi'][nm] = spectrum(rr, 'psd')

    # ---------------- VIEC 3: tran dat duoc
    res['tran'] = dict(CinC75=ceiling(c75), CinC68=ceiling(c68), chu_the_22=ceiling(r22),
                       chu_the_19_de=ceiling(easy), chu_the_3_kho=ceiling(hard))
    f1 = np.array([EV22['subjects'][t]['model_22']['F1_psd'] for t in EV22['subjects']])
    tags = list(EV22['subjects'])
    med = float(np.median(f1))
    fixed = f1.copy()
    for t in HARD:
        fixed[tags.index(t)] = max(fixed[tags.index(t)], med)
    orc = np.array([EV22['subjects'][t]['model_22']['F1_oracle'] for t in EV22['subjects']])
    res['tran']['kich_ban_22'] = dict(
        hien_tai=float(f1.mean()), trung_vi=med,
        neu_3_kho_len_trung_vi=float(fixed.mean()),
        neu_dung_kenh_oracle=float(orc.mean()),
        PowerMF_4kenh=98.83, PowerMF_1kenh=86.71,
        con_thieu_so_voi_PMF4_neu_sua_3_kho=98.83 - float(fixed.mean()),
        con_thieu_so_voi_PMF4_neu_oracle=98.83 - float(orc.mean()))

    # ---------------- VIEC 4: ba ban ghi kho
    res['ban_ghi_kho'] = {}
    for t in HARD:
        r = S22[t]
        d = dict(psd_lead=r['psd_lead'], oracle_lead=r['oracle_lead'], F1_psd=r['F1_psd'],
                 F1_oracle=r['F1_oracle'], F1_mean4=r['F1_mean4'], fusion=r['fusion'], per_lead={})
        for l in ('1', '2', '3', '4'):
            e = r['per_lead'][l]
            d['per_lead'][l] = dict(F1=e['F1'], Se=e['Se'], PPV=e['PPV'], psd=e['psd'],
                                    frac_ref_visible=e['frac_ref_visible'], z_median_all=e['z_median_all'],
                                    z_median_TP=e['z_median_TP'], z_median_FN=e['z_median_FN'],
                                    counts=e['counts'], counts_null=e['counts_null'], tau=e['tau'],
                                    n_TP=e['TP'], n_FP=e['FP'], n_FN=e['FN'])
        psds = {l: r['per_lead'][l]['psd'] for l in ('1', '2', '3', '4')}
        rank = sorted(psds, key=lambda l: -psds[l])
        d['psd_rank'] = rank
        d['oracle_rank_theo_psd'] = rank.index(str(r['oracle_lead'])) + 1
        res['ban_ghi_kho'][t] = d

    # ---------------- VIEC 2: nang luc
    if CAP:
        res['nang_luc'] = dict(A=CAP.get('A_insample_22', {}).get('mean_insample_psd'),
                               A_full={k: v for k, v in CAP.get('A_insample_22', {}).items() if k != 'records'},
                               B={w: {k: v for k, v in m.items() if k != 'records'}
                                  for w, m in CAP.get('B_memorise', {}).get('models', {}).items()},
                               B_meta={k: v for k, v in CAP.get('B_memorise', {}).items() if k != 'models'})

    # ---------------- gop them tieu chi (e) chat va quet dung sai
    for f, key in (('chandoan_strict.json', 'pho_loi_e_chat'), ('chandoan_tol.json', 'quet_dung_sai')):
        pth = os.path.join(HERE, f)
        if os.path.isfile(pth):
            j = json.load(open(pth, encoding='utf-8'))
            res[key] = j.get('pho_loi_chat') or j.get('tong_hop')
    # ---------------- phan ra khoang thieu toi 100
    if 'quet_dung_sai' in res:
        q = res['quet_dung_sai']
        res['phan_ra_khoang_thieu'] = {}
        for nm, kp, ko in (('CinC75', 'CinC75_PSD', 'CinC75_oracle'), ('22_chu_the', '22_chu_the_PSD', '22_chu_the_oracle')):
            base = q[kp][0]
            res['phan_ra_khoang_thieu'][nm] = dict(
                F1_hien_tai=base, thieu_toi_100=100 - base,
                do_lech_thoi_diem=q[kp][3] - q[kp][0],
                do_chon_kenh=q[ko][0] - q[kp][0],
                ca_hai=q[ko][3] - q[kp][0],
                con_lai_khong_giai_thich=100 - q[ko][3])
    json.dump(res, open(OUT, 'w', encoding='utf-8'), indent=1, default=float)
    if 'phan_ra_khoang_thieu' in res:
        print('
PHAN RA KHOANG THIEU TOI 100 (diem F1):')
        for nm, d in res['phan_ra_khoang_thieu'].items():
            print(f'   {nm:<12} hien tai {d["F1_hien_tai"]:.2f}, thieu {d["thieu_toi_100"]:.2f} | noi long dung sai ->150 ms: '
                  f'{d["do_lech_thoi_diem"]:+.2f} | oracle kenh: {d["do_chon_kenh"]:+.2f} | ca hai: {d["ca_hai"]:+.2f} | '
                  f'con lai {d["con_lai_khong_giai_thich"]:.2f}')

    # ---------------- in bang
    print('=' * 110)
    print('PHO LOI (micro, gop moi loi tren moi ban ghi; % tren TONG so loi = FN + FP)')
    print('=' * 110)
    hdr = f'{"bo du lieu":<26}{"n loi":>7}' + ''.join(f'{LABEL[k].split(")")[0] + ")":>7}' for k in KEYS) + f'{"loi/1000 nhip":>14}{"F1 micro":>10}'
    print(hdr)
    for name in ('22_chu_the_kenh_PSD', '22_chu_the_kenh_oracle', '22_de19_kenh_PSD', '22_kho3_kenh_PSD',
                 'CinC75_kenh_PSD', 'CinC75_kenh_oracle', 'CinC68_kenh_PSD',
                 'CinC_F1_tu90', 'CinC_F1_50_90', 'CinC_F1_duoi50'):
        if name not in res['pho_loi']: continue
        s = res['pho_loi'][name]
        print(f'{name:<26}{s["n_err"]:>7}' + ''.join(f'{s["pct"][k]:>6.1f}%' for k in KEYS) +
              f'{s["err_per_1000_beats"]:>14.1f}{s["micro_F1"]:>10.2f}')
    print('\nmuc NGAU NHIEN cua cung phep gan nhom (dich vong chuoi phat hien):')
    for name in ('22_chu_the_kenh_PSD', 'CinC75_kenh_PSD'):
        s = res['pho_loi'][name]
        print(f'{name:<26}{s["n_err_null"]:>7.0f}' + ''.join(f'{s["pct_null"][k]:>6.1f}%' for k in KEYS))
    print('\ndo nhay cua phep thu "nhin thay" (do tren cac nhip mo hinh DA bat, dac hieu co dinh 95%):')
    for name in ('22_chu_the_kenh_PSD', 'CinC75_kenh_PSD'):
        s = res['pho_loi'][name]
        print(f'   {name:<26} nhay {s["sensitivity_of_visibility_test"]:.3f}  '
              f'-> ti le (a) trong (a)+(b): tho {s.get("frac_a_within_ab_raw", float("nan")):.3f}, '
              f'hieu chinh {s.get("frac_a_within_ab_corrected", float("nan")):.3f}  '
              f'=> (a) chiem {s.get("pct_a_corrected", float("nan")):.1f}% tong loi sau hieu chinh')

    print('\n' + '=' * 110); print('TRAN DAT DUOC'); print('=' * 110)
    print(f'{"":<16}{"PSD":>8}{"TB4":>8}{"vote1":>8}{"vote2":>8}{"vote3":>8}{"vote4":>8}{"oracle kenh":>13}{"tran hop nhat":>15}')
    for nm in ('CinC75', 'CinC68', 'chu_the_22', 'chu_the_19_de', 'chu_the_3_kho'):
        c = res['tran'][nm]
        print(f'{nm:<16}{c["F1_psd"]:>8.2f}{c["F1_mean4"]:>8.2f}{c["F1_vote1"]:>8.2f}{c["F1_vote2"]:>8.2f}'
              f'{c["F1_vote3"]:>8.2f}{c["F1_vote4"]:>8.2f}{c["F1_oracle_lead"]:>13.2f}{c["union_F1_ceiling"]:>15.2f}')
    k = res['tran']['kich_ban_22']
    print(f'\n22 chu the: hien tai {k["hien_tai"]:.2f} | 3 ban kho len trung vi ({k["trung_vi"]:.2f}) -> {k["neu_3_kho_len_trung_vi"]:.2f} '
          f'| oracle kenh -> {k["neu_dung_kenh_oracle"]:.2f} | Power-MF 4 kenh 98.83')

    print('\n' + '=' * 110); print('BA BAN GHI KHO'); print('=' * 110)
    for t in HARD:
        d = res['ban_ghi_kho'][t]
        print(f'{t}  kenh PSD A{d["psd_lead"]} (F1 {d["F1_psd"]:.2f})  kenh tot nhat A{d["oracle_lead"]} (F1 {d["F1_oracle"]:.2f})  '
              f'vote2 {d["fusion"]["vote2"]["F1"]:.2f}  tran hop nhat {d["fusion"]["union_F1_ceiling"]:.2f}')
        print(f'   {"kenh":<6}{"F1":>8}{"Se":>7}{"PPV":>7}{"diem PSD":>11}{"% nhan nhin thay":>18}{"z trung vi":>11}{"a":>5}{"b":>5}{"c":>5}{"e":>5}{"d":>5}')
        for l in ('1', '2', '3', '4'):
            e = d['per_lead'][l]; c = e['counts']
            mark = ' <- PSD' if int(l) == d['psd_lead'] else (' <- tot nhat' if int(l) == d['oracle_lead'] else '')
            print(f'   A{l:<5}{e["F1"]:>8.2f}{e["Se"]:>7.2f}{e["PPV"]:>7.2f}{e["psd"]:>11.3e}{100 * e["frac_ref_visible"]:>17.1f}%'
                  f'{e["z_median_all"]:>11.2f}{c["a_bo_nhip_co_tin_hieu"]:>5}{c["b_khong_co_tin_hieu"]:>5}{c["c_me"]:>5}'
                  f'{c["e_lech"]:>5}{c["d1_doi"] + c["d2_ngau_nhien"]:>5}{mark}')

    if CAP:
        print('\n' + '=' * 110); print('NANG LUC'); print('=' * 110)
        A = CAP.get('A_insample_22')
        if A:
            print(f'A. production_22 tren chinh 22 chu the da huan luyen: TRONG MAU {A["mean_insample_psd"]:.2f} '
                  f'vs LOSO {A["mean_loso_psd"]:.2f} -> khoang cach {A["gap_psd"]:+.2f} diem (kenh PSD); '
                  f'TB4 {A["mean_insample_mean4"]:.2f} vs {A["mean_loso_mean4"]:.2f} ({A["gap_mean4"]:+.2f})')
        for w, m in CAP.get('B_memorise', {}).get('models', {}).items():
            print(f'B. be rong {w} ({m["n_params"]} tham so): F1 TRONG MAU {m["F1_insample_lead_mean"]:.2f} '
                  f'(16 chu the x kenh), TB4 {m["F1_insample_mean4"]:.2f}; loss {m["loss_hist"][0]:.4f} -> {m["loss_hist"][-1]:.4f}')

    # ---------------- hinh
    fig = plt.figure(figsize=(15, 10.5), dpi=130)
    gs = fig.add_gridspec(2, 2, hspace=.42, wspace=.24, left=.07, right=.985, top=.90, bottom=.07)
    fig.suptitle('RelyFetal — chan doan: mo hinh co phai nut that khong?', fontsize=15, y=.975, fontweight='bold')

    # A: pho loi
    ax = fig.add_subplot(gs[0, 0])
    names = ['22_chu_the_kenh_PSD', '22_chu_the_kenh_oracle', 'CinC75_kenh_PSD', 'CinC75_kenh_oracle']
    short = ['22 ca\nkenh PSD', '22 ca\nkenh tot nhat', 'CinC 75\nkenh PSD', 'CinC 75\nkenh tot nhat']
    y = np.arange(len(names))
    left = np.zeros(len(names))
    for k in KEYS:
        v = np.array([res['pho_loi'][n]['pct'][k] for n in names])
        ax.barh(y, v, left=left, color=COL[k], height=.6, label=LABEL[k], edgecolor='white', linewidth=1.4)
        for i, (l0, vv) in enumerate(zip(left, v)):
            if vv >= 6: ax.text(l0 + vv / 2, y[i], f'{vv:.0f}', ha='center', va='center', fontsize=9, color='#0b0b0b')
        left += v
    ax.set_yticks(y); ax.set_yticklabels(short, fontsize=9); ax.invert_yaxis()
    ax.set_xlim(0, 100); ax.set_xlabel('% tren tong so loi (FN + FP)', fontsize=9)
    ax.set_title('A. Pho loi — loi thuoc ve ai?', fontsize=11, loc='left', fontweight='bold')
    ax.legend(fontsize=7.5, loc='upper center', bbox_to_anchor=(.5, -.17), ncol=2, frameon=False)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for i, n in enumerate(names):
        ax.text(101, y[i], f'n={res["pho_loi"][n]["n_err"]}', va='center', fontsize=8, color='#52514e')

    # B: tran
    ax = fig.add_subplot(gs[0, 1])
    rows = [('CinC 75', res['tran']['CinC75']), ('22 chu the', res['tran']['chu_the_22'])]
    bars = [('kenh PSD\n(so chinh)', 'F1_psd', '#2a78d6'), ('TB 4 kenh', 'F1_mean4', '#eb6834'),
            ('gop 4 kenh\n(vote>=2)', 'F1_vote2', '#1baf7a'), ('oracle kenh\n(hau kiem)', 'F1_oracle_lead', '#eda100'),
            ('tran hop nhat\n(khong dat duoc)', 'union_F1_ceiling', '#e87ba4')]
    w = .38
    x = np.arange(len(bars))
    for j, (nm, c) in enumerate(rows):
        v = [c[k] for _, k, _ in bars]
        ax.bar(x + (j - .5) * w, v, w * .9, color=[col for _, _, col in bars], alpha=1 - .45 * j,
               edgecolor='white', linewidth=1.2, label=nm)
        for xi, vi in zip(x + (j - .5) * w, v):
            ax.text(xi, vi + .6, f'{vi:.1f}', ha='center', fontsize=8, color='#0b0b0b')
    ax.set_xticks(x); ax.set_xticklabels([b[0] for b in bars], fontsize=8)
    ax.set_ylim(60, 103); ax.set_ylabel('F1 trung binh muc ban ghi', fontsize=9)
    ax.axhline(98.83, color='#52514e', ls='--', lw=1.2)
    ax.text(len(bars) - .55, 99.1, 'Power-MF 4 kenh 98,83 (tren 22 chu the)', fontsize=7.5, ha='right', color='#52514e')
    ax.set_title('B. Tran dat duoc: chon kenh vs gop kenh', fontsize=11, loc='left', fontweight='bold')
    ax.legend(fontsize=8, frameon=False, loc='lower left')
    for s in ('top', 'right'): ax.spines[s].set_visible(False)

    # C: ba ban ghi kho
    ax = fig.add_subplot(gs[1, 0])
    x = np.arange(4); w = .2
    for i, t in enumerate(HARD):
        d = res['ban_ghi_kho'][t]
        v = [d['per_lead'][str(l)]['F1'] for l in (1, 2, 3, 4)]
        b = ax.bar(x + (i - 1) * w, v, w * .88, color=['#2a78d6', '#eb6834', '#1baf7a'][i],
                   edgecolor='white', linewidth=1.1, label=t)
        for l in (1, 2, 3, 4):
            if l == d['psd_lead']:
                ax.text(x[l - 1] + (i - 1) * w, v[l - 1] + 1.5, 'PSD', ha='center', fontsize=7, color='#0b0b0b',
                        fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels([f'kenh A{l}' for l in (1, 2, 3, 4)], fontsize=9)
    ax.set_ylabel('F1', fontsize=9); ax.set_ylim(0, 108)
    ax.set_title('C. Ba ban ghi kho: F1 tung kenh (nhan PSD = kenh quy tac mu nhan chon)',
                 fontsize=10.5, loc='left', fontweight='bold')
    ax.legend(fontsize=8, frameon=False, ncol=3, loc='lower center')
    for s in ('top', 'right'): ax.spines[s].set_visible(False)

    # D: nang luc
    ax = fig.add_subplot(gs[1, 1])
    if CAP and CAP.get('A_insample_22'):
        A = CAP['A_insample_22']
        tags = sorted(A['records'])
        ins = np.array([A['records'][t]['F1_psd'] for t in tags])
        los = np.array([A['records'][t]['loso_F1_psd'] for t in tags])
        ax.scatter(los, ins, s=52, color='#2a78d6', edgecolor='white', linewidth=1.2, zorder=3, label='1 chu the')
        ax.plot([50, 101], [50, 101], color='#52514e', lw=1.2, ls='--', zorder=2)
        for t, a_, b_ in zip(tags, los, ins):
            if t in HARD: ax.annotate(t, (a_, b_), fontsize=7.5, xytext=(4, -9), textcoords='offset points')
        ax.set_xlabel('F1 NGOAI mau (LOSO, kenh PSD)', fontsize=9)
        ax.set_ylabel('F1 TRONG mau (production_22 tren\nchinh chu the no da hoc)', fontsize=9)
        lo_ = min(ins.min(), los.min()) - 3
        ax.set_xlim(lo_, 101); ax.set_ylim(lo_, 101)
        ax.set_title(f'D. Nang luc: trong mau {ins.mean():.2f} vs ngoai mau {los.mean():.2f} '
                     f'({ins.mean() - los.mean():+.2f})', fontsize=10.5, loc='left', fontweight='bold')
        ax.text(.03, .06, 'diem tren duong cheo = hoc thuoc duoc;\ndiem tren duong cheo = mo hinh KHONG'
                          ' hoc thuoc noi\nchinh du lieu huan luyen cua no',
                transform=ax.transAxes, fontsize=7.5, color='#52514e', va='bottom')
        ax.legend(fontsize=8, frameon=False, loc='upper left')
    else:
        ax.text(.5, .5, 'chua co chandoan_capacity.json', ha='center', transform=ax.transAxes)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)

    fig.savefig(PNG, bbox_inches='tight', facecolor='#fcfcfb')
    print(f'\n-> {OUT}\n-> {PNG}')


if __name__ == '__main__':
    main()
