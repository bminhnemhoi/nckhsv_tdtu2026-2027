# -*- coding: utf-8 -*-
"""M1 bo sung: pho loi theo TUNG QUY TAC CHON KENH (psd / gate / peakprob / oracle),
tran nang luc (phep thu B), va chan doan 8 ban ghi CinC gioi han cung.

KHONG chay suy luan moi: tai su dung analysis/chandoan_raw.json (dem loi tung ban ghi x kenh)
va analysis/chonkenh_results.json (lua chon kenh cua tung quy tac).
"""
import os
for _v in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_v] = '1'
import json
import numpy as np

R = os.path.dirname(os.path.abspath(__file__))
KEYS = ['a_bo_nhip_co_tin_hieu', 'b_khong_co_tin_hieu', 'c_me', 'e_lech', 'd1_doi', 'd2_ngau_nhien']
BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')
HARD3 = ('B1_06', 'B1_07', 'B2_03')
HARD8 = ('a27', 'a43', 'a54', 'a57', 'a59', 'a60', 'a68', 'a71')

raw = json.load(open(os.path.join(R, 'chandoan_raw.json'), encoding='utf-8'))
ck = json.load(open(os.path.join(R, 'chonkenh_results.json'), encoding='utf-8'))
cap = json.load(open(os.path.join(R, 'chandoan_capacity.json'), encoding='utf-8'))
gate = json.load(open(os.path.join(R, 'gate22_cinc.json'), encoding='utf-8'))
SEL = ck['chon_kenh_theo_quy_tac']
RULES = ['psd', 'gate', 'peakprob', 'rrcv', 'gate4']

log_lines = []


def log(s=''):
    print(s)
    log_lines.append(s)


def lead_of(name, rec, rule, dom):
    if rule == 'oracle':
        return str(rec['oracle_lead'])
    return str(SEL[dom][name][rule] + 1)


log('=== 0. KIEM TRA NHAT QUAN HAI BO NHO DEM ===')
bad = []
for dom, blk in (('s22', raw['subjects22']), ('cinc', raw['cinc'])):
    for name, rec in blk.items():
        if name not in SEL[dom]:
            bad.append((dom, name, 'thieu trong chonkenh'))
            continue
        if str(SEL[dom][name]['psd'] + 1) != str(rec['psd_lead']):
            bad.append((dom, name, 'psd_lead lech: chonkenh %d vs chandoan %d'
                        % (SEL[dom][name]['psd'] + 1, rec['psd_lead'])))
log('   ban ghi lech: %d' % len(bad))
for b in bad[:10]:
    log('     %s' % (b,))

chk = {}
for rule in RULES:
    for dom, blk, key in (('s22', raw['subjects22'], 's22'), ('cinc', raw['cinc'], 'cinc')):
        mine = float(np.mean([blk[n]['per_lead'][lead_of(n, blk[n], rule, dom)]['F1'] for n in blk]))
        theirs = ck['bang'][key][rule]['mean']
        chk['%s/%s' % (dom, rule)] = dict(tu_chandoan_raw=mine, tu_chonkenh=theirs,
                                          lech=abs(mine - theirs))
        log('   %-5s %-9s F1 tu chandoan_raw %7.3f | tu chonkenh %7.3f | lech %.4f'
            % (dom, rule, mine, theirs, abs(mine - theirs)))


def spectrum(recs_named, rule, dom):
    tot = {k: 0 for k in KEYS}
    tot_null = {k: 0.0 for k in KEYS}
    fn_cls = {k: 0 for k in KEYS}
    fp_cls = {k: 0 for k in KEYS}
    n_err = 0
    n_err_null = 0.0
    n_tp = n_fp = n_fn = 0
    sens_num = sens_den = 0.0
    f1s = []
    for name, r in recs_named:
        e = r['per_lead'][lead_of(name, r, rule, dom)]
        for k in KEYS:
            tot[k] += e['counts'][k]
            tot_null[k] += e['counts_null'][k]
            fn_cls[k] += e['counts_FN'][k]
            fp_cls[k] += e['counts_FP'][k]
        n_err += e['n_err']
        n_err_null += e['counts_null']['n_err']
        n_tp += e['TP']
        n_fp += e['FP']
        n_fn += e['FN']
        f1s.append(e['F1'])
        if e['TP'] and np.isfinite(e['sens_test_on_TP']):
            sens_num += e['sens_test_on_TP'] * e['TP']
            sens_den += e['TP']
    se = n_tp / (n_tp + n_fn) * 100 if n_tp + n_fn else 0.0
    pp = n_tp / (n_tp + n_fp) * 100 if n_tp + n_fp else 0.0
    out = dict(quy_tac=rule, n_records=len(recs_named), n_TP=n_tp, n_FP=n_fp, n_FN=n_fn,
               n_err=n_err, micro_Se=se, micro_PPV=pp,
               micro_F1=2 * se * pp / (se + pp) if se + pp else 0.0,
               macro_F1=float(np.mean(f1s)), counts=tot, counts_FN=fn_cls, counts_FP=fp_cls,
               pct={k: (100.0 * tot[k] / n_err if n_err else 0.0) for k in KEYS},
               pct_null={k: (100.0 * tot_null[k] / n_err_null if n_err_null else 0.0) for k in KEYS},
               n_err_null=n_err_null,
               err_per_1000_beats=1000.0 * n_err / max(n_tp + n_fn, 1),
               sensitivity_of_visibility_test=sens_num / sens_den if sens_den else float('nan'))
    s = out['sensitivity_of_visibility_test']
    ab = tot['a_bo_nhip_co_tin_hieu'] + tot['b_khong_co_tin_hieu']
    if ab and np.isfinite(s) and s > 0.05:
        obs = tot['a_bo_nhip_co_tin_hieu'] / ab
        out['frac_a_within_ab_raw'] = obs
        out['frac_a_within_ab_corrected'] = float(np.clip((obs - 0.05) / (s - 0.05), 0, 1))
        out['pct_a_corrected'] = 100.0 * out['frac_a_within_ab_corrected'] * ab / n_err
    return out


S22 = [(n, r) for n, r in raw['subjects22'].items()]
S22_EASY = [(n, r) for n, r in S22 if n not in HARD3]
S22_HARD = [(n, r) for n, r in S22 if n in HARD3]
CINC = [(n, r) for n, r in raw['cinc'].items()]
CINC68 = [(n, r) for n, r in CINC if n not in BAD_ANN]
CINC_H8 = [(n, r) for n, r in CINC if n in HARD8]
CINC_R67 = [(n, r) for n, r in CINC if n not in HARD8]

POP = [('22_chu_the', S22, 's22'), ('22_de19', S22_EASY, 's22'), ('22_kho3', S22_HARD, 's22'),
       ('CinC75', CINC, 'cinc'), ('CinC68', CINC68, 'cinc'),
       ('CinC_gioihancung8', CINC_H8, 'cinc'), ('CinC_conlai67', CINC_R67, 'cinc')]

pho = {}
log('')
log('=== 1. PHO LOI THEO QUY TAC CHON KENH ===')
hdr = ('%-20s %-9s %7s %7s %6s %6s %6s %6s %6s %6s %8s %8s'
       % ('quan the', 'quy tac', 'n_loi', 'loi/1k', '(a)%', '(b)%', '(c)%', '(e)%',
          '(d1)%', '(d2)%', 'microF1', 'macroF1'))
log(hdr)
log('-' * len(hdr))
for pname, recs, dom in POP:
    for rule in RULES + ['oracle']:
        s = spectrum(recs, rule, dom)
        pho['%s|%s' % (pname, rule)] = s
        log('%-20s %-9s %7d %7.1f %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f %8.2f %8.2f'
            % (pname, rule, s['n_err'], s['err_per_1000_beats'],
               s['pct']['a_bo_nhip_co_tin_hieu'], s['pct']['b_khong_co_tin_hieu'],
               s['pct']['c_me'], s['pct']['e_lech'], s['pct']['d1_doi'],
               s['pct']['d2_ngau_nhien'], s['micro_F1'], s['macro_F1']))
    log('')

log('=== 1b. CAU HOI THEN CHOT: (a) sau khi doi quy tac chon kenh ===')
for pname in ('22_chu_the', 'CinC75'):
    for rule in RULES + ['oracle']:
        s = pho['%s|%s' % (pname, rule)]
        log('   %-11s %-9s (a) tho %5.2f%%  hieu chinh %5.2f%%  | do nhay %.3f | (a) ngau nhien %5.2f%%'
            % (pname, rule, s['pct']['a_bo_nhip_co_tin_hieu'],
               s.get('pct_a_corrected', float('nan')),
               s['sensitivity_of_visibility_test'], s['pct_null']['a_bo_nhip_co_tin_hieu']))

log('')
log('=== 1c. CHON KENH CHUYEN LOI TU NHOM NAO SANG NHOM NAO (psd -> peakprob) ===')
dich = {}
for pname in ('22_chu_the', 'CinC75'):
    p0 = pho['%s|psd' % pname]
    p1 = pho['%s|peakprob' % pname]
    d = {k: p1['counts'][k] - p0['counts'][k] for k in KEYS}
    d['n_err'] = p1['n_err'] - p0['n_err']
    dich[pname] = dict(psd=p0['counts'], peakprob=p1['counts'], hieu=d,
                       n_err_psd=p0['n_err'], n_err_peakprob=p1['n_err'])
    log('   %s: tong loi %d -> %d (%+d)' % (pname, p0['n_err'], p1['n_err'], d['n_err']))
    for k in KEYS:
        log('      %-24s %6d -> %6d  (%+d)' % (k, p0['counts'][k], p1['counts'][k], d[k]))

# ---------------------------------------------------------------- 8 ban ghi gioi han cung
log('')
log('=== 2. 8 BAN GHI CinC GIOI HAN CUNG: DAC DIEM CHUNG ===')
gb = {b['record']: b for b in gate['bang']}
hard_rows = []
for name, r in CINC:
    pl = r['per_lead']
    best = max(pl.values(), key=lambda e: e['F1'])
    row = dict(
        record=name,
        nhom_cung=name in HARD8,
        chu_thich_sai=name in BAD_ANN,
        n_ref=r['n_ref'],
        F1_psd=r['F1_psd'],
        F1_oracle=r['F1_oracle'],
        F1_peakprob=pl[lead_of(name, r, 'peakprob', 'cinc')]['F1'],
        F1_union_ceiling=r['fusion'].get('union_F1_ceiling', r['fusion'].get('union', {}).get('F1')),
        # --- dac trung MU NHAN (khong dung nhan) ---
        psd_max=max(e['psd'] for e in pl.values()),
        psd_min=min(e['psd'] for e in pl.values()),
        n_det_max=max(e['n_det'] for e in pl.values()),
        n_det_min=min(e['n_det'] for e in pl.values()),
        tau_median=float(np.median([e['tau'] for e in pl.values()])),
        gate_score=gb.get(name, {}).get('score'),
        gate_mean_p_bad=gb.get(name, {}).get('mean_p_bad'),
        gate_frac_bad=gb.get(name, {}).get('frac_p_gt_half'),
        # --- dac trung CO DUNG NHAN (chi de mo ta, khong dung lam tieu chi) ---
        frac_visible_best=max(e['frac_ref_visible'] for e in pl.values()),
        z_median_best=max(e['z_median_all'] for e in pl.values()),
        frac_FN_maternal_best=best['frac_FN_on_maternal'],
    )
    hard_rows.append(row)

H = [r for r in hard_rows if r['nhom_cung']]
O = [r for r in hard_rows if not r['nhom_cung']]
O_bad = [r for r in O if r['F1_oracle'] < 50]
O_good = [r for r in O if r['F1_oracle'] >= 50]

log('   8 ban gioi han cung (F1 oracle):')
for r in sorted(H, key=lambda x: x['F1_oracle']):
    log('     %-4s n_ref %4d  F1 psd %6.2f  peakprob %6.2f  oracle %6.2f  | psd_max %7.2f  '
        'n_det[%4d,%4d]  gate_score %s  nhin thay %.2f  z %.2f  %s'
        % (r['record'], r['n_ref'], r['F1_psd'], r['F1_peakprob'], r['F1_oracle'],
           r['psd_max'], r['n_det_min'], r['n_det_max'],
           ('%.3f' % r['gate_score']) if r['gate_score'] is not None else '  n/a',
           r['frac_visible_best'], r['z_median_best'],
           'CHU THICH SAI' if r['chu_thich_sai'] else ''))


def summ(rows, f):
    v = [r[f] for r in rows if r[f] is not None and np.isfinite(r[f])]
    return (float(np.median(v)), float(np.min(v)), float(np.max(v)), len(v)) if v else (float('nan'),) * 3 + (0,)


log('')
log('   So sanh 8 ban cung vs 67 ban con lai (trung vi [min, max]):')
FEATS = [('psd_max', 'diem PSD lon nhat (MU NHAN)'), ('n_det_max', 'so phat hien lon nhat (MU NHAN)'),
         ('n_ref', 'so nhan that'), ('gate_score', 'diem cong tu choi (MU NHAN)'),
         ('gate_frac_bad', 'ti le doan bi cong danh xau (MU NHAN)'),
         ('frac_visible_best', '%% nhan nhin thay, kenh tot nhat (DUNG NHAN)'),
         ('z_median_best', 'z trung vi, kenh tot nhat (DUNG NHAN)'),
         ('F1_union_ceiling', 'tran hop nhat 4 kenh (DUNG NHAN)')]
so_sanh = {}
for f, lab in FEATS:
    a = summ(H, f)
    b = summ(O_good, f)
    c = summ(O_bad, f)
    so_sanh[f] = dict(nhan=lab, cung8=a, conlai_oracle_ge50=b, conlai_oracle_lt50=c)
    log('     %-42s cung8 %8.2f [%7.2f,%8.2f] | conlai>=50 %8.2f [%7.2f,%8.2f] | conlai<50 %8.2f'
        % (lab, a[0], a[1], a[2], b[0], b[1], b[2], c[0]))

# tieu chi tu choi mu nhan: 8 ban cung co tach duoc bang dac trung khong nhin nhan khong?
log('')
log('   Kha nang tach 8 ban cung bang dac trung MU NHAN (AUROC 1-vs-phan con lai):')


def auroc(pos, neg):
    pos = [p for p in pos if p is not None and np.isfinite(p)]
    neg = [p for p in neg if p is not None and np.isfinite(p)]
    if not pos or not neg:
        return float('nan')
    n = 0.0
    for p in pos:
        for q in neg:
            n += 1.0 if p > q else (0.5 if p == q else 0.0)
    return n / (len(pos) * len(neg))


auc = {}
for f, lab in FEATS:
    a = auroc([r[f] for r in H], [r[f] for r in O])
    a2 = auroc([r[f] for r in H], [r[f] for r in O_good])
    auc[f] = dict(nhan=lab, vs_67=a, vs_conlai_oracle_ge50=a2)
    log('     %-42s vs ca 67: %.3f | vs 59 ban oracle>=50: %.3f' % (lab, a, a2))

# ---------------------------------------------------------------- tran nang luc B
log('')
log('=== 3. TRAN NANG LUC - PHEP THU B (hoc thuoc 4 chu the) ===')
B = cap['B_memorise']
bang_B = {}
for w in ('40', '80'):
    m = B['models'][w]
    rows = {}
    for rn, rec in m['records'].items():
        rows[rn] = dict(F1_psd=rec['F1_psd'], F1_mean4=rec['F1_mean4'], F1_oracle=rec['F1_oracle'],
                        per_lead={k: v['F1'] for k, v in rec['per_lead'].items()})
    bang_B[w] = dict(n_params=m['n_params'], threshold=m['threshold'],
                     loss_cuoi=m['loss_hist'][-1], loss_dau=m['loss_hist'][0],
                     F1_insample_psd=m['F1_insample_psd'],
                     F1_insample_lead_mean=m['F1_insample_lead_mean'], records=rows)
    log('   be rong %s (%d tham so, loss %.4f -> %.4f): F1 trong mau PSD %.2f | TB moi kenh %.2f'
        % (w, m['n_params'], m['loss_hist'][0], m['loss_hist'][-1],
           m['F1_insample_psd'], m['F1_insample_lead_mean']))
    for rn in B['subset']:
        r = rows[rn]
        log('      %-6s PSD %6.2f  TB4 %6.2f  oracle %6.2f   %s'
            % (rn, r['F1_psd'], r['F1_mean4'], r['F1_oracle'],
               ' '.join('%s:%.1f' % (k, v) for k, v in sorted(r['per_lead'].items()))))

log('')
log('   Chenh 80 kenh vs 40 kenh (4x tham so):')
for rn in B['subset']:
    d = bang_B['80']['records'][rn]['F1_oracle'] - bang_B['40']['records'][rn]['F1_oracle']
    log('      %-6s oracle %+6.2f' % (rn, d))
d_psd = bang_B['80']['F1_insample_psd'] - bang_B['40']['F1_insample_psd']
log('      TONG   F1 trong mau PSD %+6.2f (%.2f -> %.2f)'
    % (d_psd, bang_B['40']['F1_insample_psd'], bang_B['80']['F1_insample_psd']))

# ---------------------------------------------------------------- ngan sach sai so
log('')
log('=== 4. PHAN RA NGAN SACH SAI SO TREN CinC 75 THEO TUNG QUY TAC ===')
log('    (chia doi voi tung ban ghi: (100-F1_oracle) la phan BO DO/GIOI HAN,')
log('     (F1_oracle-F1_quy_tac) la phan CHON KENH; chia cho 75 de ra diem macro)')
ngan_sach = {}
for rule in RULES + ['oracle']:
    ch_67 = ch_8 = det_67 = hard_8 = 0.0
    for name, r in CINC:
        f_rule = r['per_lead'][lead_of(name, r, rule, 'cinc')]['F1']
        f_or = r['F1_oracle']
        if name in HARD8:
            ch_8 += (f_or - f_rule) / 75.0
            hard_8 += (100.0 - f_or) / 75.0
        else:
            ch_67 += (f_or - f_rule) / 75.0
            det_67 += (100.0 - f_or) / 75.0
    tong = ch_67 + ch_8 + det_67 + hard_8
    f1 = float(np.mean([r['per_lead'][lead_of(n, r, rule, 'cinc')]['F1'] for n, r in CINC]))
    ngan_sach[rule] = dict(F1=f1, thieu_toi_100=100.0 - f1, chon_kenh_67=ch_67,
                           chon_kenh_nhom_vo_vong_8=ch_8, bo_do_67=det_67,
                           gioi_han_cung_8=hard_8, tong_kiem=tong)
    log('   %-9s F1 %6.2f | thieu %6.2f = chon kenh(67) %5.2f + chon kenh(8 vo vong) %5.2f '
        '+ BO DO(67) %5.2f + GIOI HAN CUNG(8) %5.2f  [kiem %6.2f]'
        % (rule, f1, 100.0 - f1, ch_67, ch_8, det_67, hard_8, tong))

# ---------------------------------------------------------------- tieu chi tu choi mu nhan
log('')
log('=== 5. TIEU CHI TU CHOI MU NHAN CHO NHOM GIOI HAN CUNG ===')
log('   LUU Y VONG LAP: nhom "8 ban gioi han cung" duoc DINH NGHIA la F1_oracle < 50.')
log('   Kiem chung: so ban ngoai nhom 8 co F1_oracle < 50 = %d'
    % sum(1 for r in O if r['F1_oracle'] < 50))
log('   => moi dac trung DUNG NHAN tat nhien tach duoc; chi dac trung MU NHAN moi co gia tri.')
log('   Trong 8 ban: %d ban nam trong danh sach chu thich sai da khai bao truoc (%s).'
    % (sum(1 for r in H if r['chu_thich_sai']),
       ', '.join(sorted(r['record'] for r in H if r['chu_thich_sai']))))
n_det_vs_ref = [(r['record'], r['n_ref'], r['n_det_max']) for r in H if r['chu_thich_sai']]
for rec, nr, nd in n_det_vs_ref:
    log('      %s: n_ref %d nhung mo hinh phat hien toi %d nhip -> khong phai "khong co tin hieu"'
        % (rec, nr, nd))

# cong da co (huan luyen leave-one-subject-out tren 22, zero-shot sang CinC) lam tieu chi
auc_gate = 1.0 - auc['gate_score']['vs_67']
log('')
log('   Cong tu choi CO SAN (GATE22, hieu chuan tren 22 chu the, ZERO-SHOT sang CinC):')
log('      AUROC nhan dien 8 ban gioi han cung = %.3f (diem cong THAP = ban ghi xau)' % auc_gate)
log('      AUROC cua ti le doan bi danh xau        = %.3f' % auc['gate_frac_bad']['vs_67'])
log('      AUROC cua diem PSD lon nhat             = %.3f (nguoc chieu truc giac: PSD CAO = xau)'
    % auc['psd_max']['vs_67'])
thr_scan = []
for t in (0.05, 0.10, 0.20, 0.30, 0.50):
    tp = sum(1 for r in H if r['gate_score'] is not None and r['gate_score'] < t)
    fp = sum(1 for r in O if r['gate_score'] is not None and r['gate_score'] < t)
    thr_scan.append(dict(nguong=t, bat_duoc_trong_8=tp, bao_dong_nham_trong_67=fp))
    log('      nguong diem cong < %.2f: bat %d/8 ban cung, bao dong nham %d/67' % (t, tp, fp))
tu_choi = dict(vong_lap='nhom 8 = dinh nghia F1_oracle<50, nen dac trung dung nhan la vong lap',
               so_ban_ngoai_nhom_co_oracle_duoi_50=sum(1 for r in O if r['F1_oracle'] < 50),
               chu_thich_sai_trong_8=[r['record'] for r in H if r['chu_thich_sai']],
               auroc_gate_zero_shot=auc_gate, quet_nguong=thr_scan)

# ---------------------------------------------------------------- 6.36 diem "BO DO" thuc ra la gi
log('')
log('=== 6. MUC "BO DO (67 ban)" = 6,36 DIEM THUC RA GOM NHUNG GI? ===')
cont = []
for name, r in CINC_R67:
    ol = str(r['oracle_lead'])
    e = r['per_lead'][ol]
    cont.append(dict(record=name, F1_oracle=r['F1_oracle'],
                     dong_gop=(100.0 - r['F1_oracle']) / 75.0,
                     nhin_thay_kenh_tot_nhat=max(x['frac_ref_visible'] for x in r['per_lead'].values()),
                     z_median=e['z_median_all'],
                     tran_hop_nhat=r['fusion'].get('union_F1_ceiling'),
                     pct_a=100.0 * e['counts']['a_bo_nhip_co_tin_hieu'] / e['n_err'] if e['n_err'] else 0.0,
                     chu_thich_sai=name in BAD_ANN))
cont.sort(key=lambda x: -x['dong_gop'])
tot_bo_do = sum(x['dong_gop'] for x in cont)
log('   tong = %.2f diem, phan bo RAT TAP TRUNG:' % tot_bo_do)
cum = 0.0
for i, x in enumerate(cont[:10], 1):
    cum += x['dong_gop']
    log('     %2d. %-4s F1_oracle %6.2f  +%.3f diem (cong don %.2f = %2.0f%%)  nhin thay %.2f  (a) %4.1f%% %s'
        % (i, x['record'], x['F1_oracle'], x['dong_gop'], cum, 100 * cum / tot_bo_do,
           x['nhin_thay_kenh_tot_nhat'], x['pct_a'], 'CHU THICH SAI' if x['chu_thich_sai'] else ''))
for k in (5, 10, 20):
    log('     top %2d ban ghi chiem %2.0f%% cua 6,36 diem'
        % (k, 100 * sum(x['dong_gop'] for x in cont[:k]) / tot_bo_do))
log('     so ban ghi da >= 95 tren kenh oracle: %d/67 (chi con %d ban dang ke)'
    % (sum(1 for x in cont if x['F1_oracle'] >= 95), sum(1 for x in cont if x['F1_oracle'] < 95)))

VIS_THR = 0.5
lo = [x for x in cont if x['nhin_thay_kenh_tot_nhat'] < VIS_THR]
hi = [x for x in cont if x['nhin_thay_kenh_tot_nhat'] >= VIS_THR]
log('')
log('   Chia 6,36 diem theo do NHIN THAY tin hieu thai tren kenh TOT NHAT (nguong %.2f):' % VIS_THR)
log('     tin hieu KHONG nhin thay (<%.2f): %2d ban, %.2f diem (%2.0f%%)  -- gioi han THU TIN HIEU'
    % (VIS_THR, len(lo), sum(x['dong_gop'] for x in lo),
       100 * sum(x['dong_gop'] for x in lo) / tot_bo_do))
log('     tin hieu CO nhin thay (>=%.2f): %2d ban, %.2f diem (%2.0f%%)  -- phan co the do mo hinh'
    % (VIS_THR, len(hi), sum(x['dong_gop'] for x in hi),
       100 * sum(x['dong_gop'] for x in hi) / tot_bo_do))
log('')
log('   Thang do nhin thay (trung vi, kenh tot nhat) theo muc F1 oracle:')
for lab, sel in (('67 ban: F1_oracle >= 95', lambda x: x['F1_oracle'] >= 95),
                 ('67 ban: F1_oracle <  95', lambda x: x['F1_oracle'] < 95)):
    v = [x['nhin_thay_kenh_tot_nhat'] for x in cont if sel(x)]
    log('     %-26s n=%2d  nhin thay %.2f' % (lab, len(v), float(np.median(v))))
log('     %-26s n=%2d  nhin thay %.2f'
    % ('8 ban gioi han cung', len(H), float(np.median([r['frac_visible_best'] for r in H]))))
bo_do_chi_tiet = dict(tong=tot_bo_do, tung_ban_ghi=cont, nguong_nhin_thay=VIS_THR,
                      diem_khong_nhin_thay=sum(x['dong_gop'] for x in lo),
                      diem_co_nhin_thay=sum(x['dong_gop'] for x in hi),
                      n_khong_nhin_thay=len(lo), n_co_nhin_thay=len(hi))

# ---------------------------------------------------------------- hinh
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    LAB = {'a_bo_nhip_co_tin_hieu': '(a) bo nhip CO tin hieu', 'b_khong_co_tin_hieu': '(b) khong co tin hieu',
           'c_me': '(c) nhip me', 'e_lech': '(e) lech thoi diem', 'd1_doi': '(d1) phat hien doi',
           'd2_ngau_nhien': '(d2) FP ngau nhien'}
    COL = {'a_bo_nhip_co_tin_hieu': '#2a78d6', 'b_khong_co_tin_hieu': '#eb6834', 'c_me': '#1baf7a',
           'e_lech': '#eda100', 'd1_doi': '#e87ba4', 'd2_ngau_nhien': '#008300'}
    fig, ax = plt.subplots(2, 2, figsize=(14.5, 9.5))

    # (1) pho loi theo quy tac, CinC75 + 22 chu the -- SO LOI TUYET DOI
    a = ax[0][0]
    rl = ['psd', 'gate', 'peakprob', 'oracle']
    x = np.arange(len(rl))
    for i, pname in enumerate(('22_chu_the', 'CinC75')):
        bot = np.zeros(len(rl))
        for k in KEYS:
            v = np.array([pho['%s|%s' % (pname, r)]['counts'][k] for r in rl], dtype=float)
            a.bar(x + i * 0.42 - 0.21, v, 0.38, bottom=bot, color=COL[k],
                  label=LAB[k] if i == 0 else None, edgecolor='white', linewidth=0.4)
            bot += v
        for j, r in enumerate(rl):
            a.text(x[j] + i * 0.42 - 0.21, bot[j] + 60, '%d' % bot[j], ha='center', fontsize=7.5)
    a.set_xticks(x)
    a.set_xticklabels(rl)
    a.set_ylabel('so loi (trai: 22 chu the, phai: CinC 75)')
    a.set_title('1. Pho loi theo quy tac chon kenh (so tuyet doi)', fontsize=11, loc='left')
    a.legend(fontsize=7, ncol=2, loc='upper right')

    # (2) ti le nhom (a) va (e)
    a = ax[0][1]
    w = 0.35
    for i, pname in enumerate(('22_chu_the', 'CinC75')):
        pa = [pho['%s|%s' % (pname, r)]['pct']['a_bo_nhip_co_tin_hieu'] for r in rl]
        pe = [pho['%s|%s' % (pname, r)]['pct']['e_lech'] for r in rl]
        a.plot(x, pa, marker='o', color=COL['a_bo_nhip_co_tin_hieu'],
               ls='-' if i == 0 else '--', label='(a) %s' % pname)
        a.plot(x, pe, marker='s', color=COL['e_lech'], ls='-' if i == 0 else '--', label='(e) %s' % pname)
    nl_e = pho['CinC75|peakprob']['pct_null']['e_lech']
    nl_a = pho['CinC75|peakprob']['pct_null']['a_bo_nhip_co_tin_hieu']
    a.axhline(nl_e, color=COL['e_lech'], ls=':', lw=1.4)
    a.text(2.55, nl_e + 1.6, 'muc NGAU NHIEN cua (e) = %.0f%%' % nl_e, fontsize=7.5, color='#8a6000')
    a.axhline(nl_a, color=COL['a_bo_nhip_co_tin_hieu'], ls=':', lw=1.4)
    a.text(2.55, nl_a + 1.6, 'muc NGAU NHIEN cua (a) = %.0f%%' % nl_a, fontsize=7.5, color='#1a4e8a')
    a.axhline(0, color='k', lw=0.5)
    a.set_xticks(x)
    a.set_xticklabels(rl)
    a.set_ylabel('% tong so loi')
    a.set_ylim(-3, 80)
    a.set_title('2. (a) LUON duoi muc ngau nhien; (e) lon nhung KHONG vuot\n'
                '   muc ngau nhien tren CinC -> (e) khong chung minh duoc',
                fontsize=11, loc='left')
    a.legend(fontsize=7.5)
    a.grid(alpha=0.3)

    # (3) ngan sach sai so CinC
    a = ax[1][0]
    comp = ['chon_kenh_67', 'chon_kenh_nhom_vo_vong_8', 'bo_do_67', 'gioi_han_cung_8']
    cl = ['#2a78d6', '#9ec7ef', '#eda100', '#b03030']
    cn = ['chon kenh (67 ban)', 'chon kenh (8 ban vo vong)', 'BO DO (67 ban)', 'GIOI HAN CUNG (8 ban)']
    rr = ['psd', 'gate', 'peakprob', 'oracle']
    bot = np.zeros(len(rr))
    for c, col, nm in zip(comp, cl, cn):
        v = np.array([ngan_sach[r][c] for r in rr])
        a.bar(np.arange(len(rr)), v, 0.6, bottom=bot, color=col, label=nm, edgecolor='white')
        bot += v
    for j, r in enumerate(rr):
        a.text(j, bot[j] + 0.3, 'F1 %.2f' % ngan_sach[r]['F1'], ha='center', fontsize=8.5)
    a.set_xticks(np.arange(len(rr)))
    a.set_xticklabels(rr)
    a.set_ylabel('diem F1 con thieu toi 100 (macro, CinC 75)')
    a.set_title('3. Ngan sach sai so: peakprob da dong gan het muc CHON KENH;\n'
                '   phan con lai (BO DO 6,36) thi 71%% la ban ghi KHONG CO TIN HIEU',
                fontsize=11, loc='left')
    a.legend(fontsize=7.5)

    # (4) 8 ban gioi han cung: mu nhan vs dung nhan
    a = ax[1][1]
    a.scatter([r['gate_score'] for r in O], [r['F1_oracle'] for r in O], s=26, c='#9aa4ad',
              label='67 ban con lai', edgecolor='none')
    a.scatter([r['gate_score'] for r in H], [r['F1_oracle'] for r in H], s=64, c='#b03030',
              marker='D', label='8 ban gioi han cung')
    for r in H:
        a.annotate(r['record'], (r['gate_score'], r['F1_oracle']), fontsize=7.5,
                   xytext=(4, 3), textcoords='offset points')
    a.axhline(50, color='k', ls=':', lw=1)
    a.set_xlabel('diem cong tu choi GATE22 (MU NHAN, zero-shot)')
    a.set_ylabel('F1 tren kenh oracle (dung nhan)')
    a.set_title('4. Cong mu nhan tach duoc nhom gioi han cung mot phan (AUROC %.3f)' % auc_gate,
                fontsize=11, loc='left')
    a.legend(fontsize=8)
    a.grid(alpha=0.3)

    fig.suptitle('M1 bo sung: pho loi theo quy tac chon kenh, ngan sach sai so, nhom gioi han cung',
                 fontsize=12.5)
    fig.tight_layout(rect=[0, 0, 1, 0.965])
    fp = os.path.join(R, 'fig_chandoan_m1.png')
    fig.savefig(fp, dpi=135)
    log('')
    log('   hinh -> %s' % fp)
except Exception as exc:
    log('   LOI VE HINH: %r' % (exc,))

# ---------------------------------------------------------------- ghi ket qua
out = dict(
    meta=dict(ngay='2026-09-12', mo_ta='M1 bo sung: pho loi theo quy tac chon kenh, '
                                       'tran nang luc B, 8 ban ghi CinC gioi han cung',
              nguon=['analysis/chandoan_raw.json', 'analysis/chonkenh_results.json',
                     'analysis/chandoan_capacity.json', 'analysis/gate22_cinc.json'],
              suy_luan_moi=False, quy_tac_1based='chonkenh 0-based + 1 = chandoan_raw 1-based'),
    kiem_tra_nhat_quan=dict(so_ban_ghi_lech=len(bad), chi_tiet=bad, doi_chieu_F1=chk),
    pho_loi_theo_quy_tac=pho,
    chuyen_dich_loi_psd_sang_peakprob=dich,
    gioi_han_cung_8=dict(rows=hard_rows, so_sanh=so_sanh, auroc_mu_nhan=auc,
                         tieu_chi_tu_choi=tu_choi),
    ngan_sach_sai_so_cinc=ngan_sach,
    bo_do_67_chi_tiet=bo_do_chi_tiet,
    tran_nang_luc_B=bang_B,
)
p = os.path.join(R, 'chandoan_m1_results.json')
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
open(os.path.join(R, 'chandoan_m1_log.txt'), 'w', encoding='utf-8').write('\n'.join(log_lines))
print('\n-> %s' % p)
