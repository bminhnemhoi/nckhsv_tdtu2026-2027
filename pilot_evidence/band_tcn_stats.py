# -*- coding: utf-8 -*-
"""Tong hop thong ke cho khao sat dai loc tren chinh TCN.

Doc pilot_evidence/band_tcn.json (do band_tcn.py sinh) va ghi ra
pilot_evidence/band_tcn_stats.json, de moi con so ve dai loc trong de cuong va
bai bao truy nguoc duoc ve dung mot tep JSON tren dia.

Tinh ca hai thang do:
  - F1_psd   : chon kenh bang quy tac PSD mu nhan (thang do chinh cua de tai)
  - F1_mean4 : trung binh bon kenh, tuc bo hoan toan buoc chon kenh
"""
import json, os, sys, datetime
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'D:\NCKHSV2026-2027'
SRC = os.path.join(ROOT, 'pilot_evidence', 'band_tcn.json')
DST = os.path.join(ROOT, 'pilot_evidence', 'band_tcn_stats.json')
d = json.load(open(SRC, encoding='utf-8'))
meta, res = d['meta'], d['results']
BASE = '1-45'
THUA = ['B2_03', 'B1_06', 'B1_07']
subs = sorted(res[0]['rows'].keys())

out = {
    'nguon': 'pilot_evidence/band_tcn.json',
    'sinh_boi': 'pilot_evidence/band_tcn_stats.py',
    'ngay': str(datetime.datetime.now())[:19],
    'TRANG_THAI': ('DA CHAY XONG ca 4 dai; van la 1 seed / 3 nep gap / 4 epoch nen la KET QUA SO BO'
                   if len(res) >= len(meta['bands'])
                   else 'SO BO -- thi nghiem van dang chay'),
    'dai_da_xong': [r['band'] for r in res],
    'dai_ke_hoach': meta['bands'],
    'giao_thuc': {'n_chu_the': len(subs), 'n_fold': meta['n_folds'], 'epochs': meta['epochs'],
                  'seeds': meta['seeds'], 'dung_sai_ms': 50,
                  'mo_hinh': 'FetalQRS-TCN, doan 4 s, dau ra tung mau'},
    'macro_F1': {}, 'so_sanh_voi_1_45': {}, 'F1_tung_chu_the': {},
}

for metric, tag in (('F1_psd', 'psd'), ('F1_mean4', 'mean4')):
    tab = {r['band']: {k: v[metric] for k, v in r['rows'].items()} for r in res}
    out['F1_tung_chu_the'][tag] = tab
    out['macro_F1'][tag] = {}
    out['so_sanh_voi_1_45'][tag] = {}
    for b, m in tab.items():
        v = np.array([m[s] for s in subs])
        out['macro_F1'][tag][b] = {'mean': round(float(v.mean()), 4),
                                   'sd': round(float(v.std(ddof=1)), 4), 'n': len(v)}
    rng = np.random.default_rng(0)
    for b in tab:
        if b == BASE:
            continue
        dif = np.array([tab[b][s] - tab[BASE][s] for s in subs])
        boots = np.array([dif[rng.integers(0, len(dif), len(dif))].mean() for _ in range(20000)])
        lo, hi = np.percentile(boots, [2.5, 97.5])
        rest = np.array([tab[b][s] - tab[BASE][s] for s in subs if s not in THUA])
        out['so_sanh_voi_1_45'][tag][b] = {
            'hieu_TB': round(float(dif.mean()), 4),
            'KTC95_cluster_bootstrap': [round(float(lo), 4), round(float(hi), 4)],
            'n_boot': 20000, 'seed_bootstrap': 0,
            'KTC_cham_so_khong': bool(lo <= 0 <= hi),
            'trung_vi_hieu': round(float(np.median(dif)), 4),
            'so_chu_the_tang': int((dif > 0).sum()), 'so_chu_the_giam': int((dif < 0).sum()),
            'so_chu_the_bang': int((dif == 0).sum()),
            'hieu_tung_chu_the': {s: round(float(tab[b][s] - tab[BASE][s]), 4) for s in subs},
            'ba_chu_the_kho': {s: round(float(tab[b][s] - tab[BASE][s]), 4) for s in THUA},
            'TB_19_chu_the_con_lai': round(float(rest.mean()), 4), 'n_con_lai': len(rest),
        }

json.dump(out, open(DST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ghi', DST, '|', out['TRANG_THAI'])
for tag in ('psd', 'mean4'):
    print('--', tag)
    for b, v in out['macro_F1'][tag].items():
        print('   %-8s %7.2f +- %5.2f' % (b, v['mean'], v['sd']))
    for b, v in out['so_sanh_voi_1_45'][tag].items():
        print('   %-8s hieu %+.2f KTC [%+.2f; %+.2f] | 19 con lai %+.3f'
              % (b, v['hieu_TB'], v['KTC95_cluster_bootstrap'][0],
                 v['KTC95_cluster_bootstrap'][1], v['TB_19_chu_the_con_lai']))
