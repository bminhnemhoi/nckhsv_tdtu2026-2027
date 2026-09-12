# -*- coding: utf-8 -*-
"""Bootstrap percentile CI (muc chu the/ban ghi) cho Bang 1 cua main.tex va cho bang CinC day du.

Chi dung numpy; khong torch. Seed 0, 10000 lan lay mau lai -- cung quy uoc voi analysis/stats.py
(kiem chung: cinc_m22_lead0 va cinc_m5_lead0 tai lap dung KTC trong analysis/stats_results.json).
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np

ROOT = r'D:\NCKHSV2026-2027'
ev = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json'), encoding='utf-8'))
sil = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'silesia_eval.json'), encoding='utf-8'))


def boot(vals, n=10000, seed=0):
    v = np.asarray(vals, float)
    rng = np.random.default_rng(seed)
    m = v[rng.integers(0, len(v), size=(n, len(v)))].mean(axis=1)
    return {'mean': float(v.mean()), 'sd': float(v.std(ddof=1)), 'n': int(len(v)),
            'ci95_bootstrap': [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]}


out = {'meta': {'n_boot': 10000, 'seed': 0, 'don_vi': 'ban ghi (CinC) / chu the (Silesia)',
                'nguon': ['benchmark_dpss/eval_22.json', 'benchmark_dpss/silesia_eval.json']}}

recs = ev['cinc2013']['records']
for tag, get in (('psd', lambda r: r['F1_psd']), ('lead0', lambda r: r['F1_lead0']),
                 ('mean4', lambda r: r['F1_mean4']), ('oracle', lambda r: r['F1_oracle'])):
    out['cinc_m22_' + tag] = boot([get(recs[k]) for k in sorted(recs)])
    out['cinc_m5_' + tag] = boot([get(recs[k]['model_5']) for k in sorted(recs)])

out['cinc_psd_chon_dung_lead0'] = {
    'psd_lead_tung_ban_ghi': {k: recs[k]['psd_lead'] for k in sorted(recs)},
    'so_ban_ghi_psd_chon_lead0': sum(1 for k in recs if recs[k]['psd_lead'] == 0),
    'n': len(recs)}

r = sil['records']


def f1psd(rec):
    ks = list(rec['per_lead'])
    return rec['per_lead'][ks[rec['psd_lead']]]['F1']


out['silesia_B2_12_psd_m5'] = boot([f1psd(r[k]) for k in sorted(r) if r[k]['group'] == 'B2'])
out['silesia_B2_7moi_psd_m5'] = boot([f1psd(r[k]) for k in
                                      ('B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12')])
out['silesia_B1_10_psd_m5'] = boot([f1psd(r[k]) for k in sorted(r) if r[k]['group'] == 'B1'])

# do on dinh 2 seed tren 20 chu the chung (mo hinh 22 ca, kenh PSD)
a = json.load(open(os.path.join(ROOT, 'model', 'train_22.json'), encoding='utf-8'))
b = json.load(open(os.path.join(ROOT, 'model', 'train_22_seed1.json'), encoding='utf-8'))
common = sorted(set(a['subjects']) & set(b['subjects']))
diff = {k: b['subjects'][k]['F1_psd'] - a['subjects'][k]['F1_psd'] for k in common}
out['on_dinh_2_seed'] = {
    'n_chu_the_chung': len(common),
    'mean_abs_diff': float(np.mean([abs(v) for v in diff.values()])),
    'max_abs_diff': float(max(abs(v) for v in diff.values())),
    'chu_the_lech_nhat': max(diff, key=lambda k: abs(diff[k])),
    'hieu_tung_chu_the': {k: round(v, 3) for k, v in sorted(diff.items(), key=lambda t: -abs(t[1]))},
    'nguong_fold_seed0': sorted(round(v['threshold'], 2) for v in a['folds'].values()),
    'nguong_fold_seed1': sorted(round(v['threshold'], 2) for v in b['folds'].values())}

p = os.path.join(ROOT, 'analysis', 'boot_ci_table1.json')
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('-> ' + p)
for k, v in out.items():
    if isinstance(v, dict) and 'ci95_bootstrap' in v:
        print('%-24s %7.2f  [%6.2f; %6.2f]  n=%d' % (k, v['mean'], v['ci95_bootstrap'][0],
                                                     v['ci95_bootstrap'][1], v['n']))
print('PSD chon lead0 o %d/%d ban ghi CinC' % (out['cinc_psd_chon_dung_lead0']['so_ban_ghi_psd_chon_lead0'],
                                               out['cinc_psd_chon_dung_lead0']['n']))
s = out['on_dinh_2_seed']
print('2 seed: |hieu| TB %.2f diem, lon nhat %.2f (%s), n=%d' % (
    s['mean_abs_diff'], s['max_abs_diff'], s['chu_the_lech_nhat'], s['n_chu_the_chung']))
