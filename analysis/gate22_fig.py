# -*- coding: utf-8 -*-
"""gate22_fig.py -- hinh analysis/fig_gate22.png tu analysis/gate22_results.json.

(A) duong rui ro - do phu MUC CHU THE: RelyFetal 1 kenh vs Power-MF 4 kenh tren cung tap con con lai
(B) xep hang tin cay 22 chu the (ba ban ghi kho to mau khac)
(C) duong rui ro - do phu MUC DOAN theo % THOI LUONG giu lai
"""
import os, sys, json
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'gate22_results.json'), encoding='utf-8'))
HARD = ['B1_07', 'B1_06', 'B2_03']
C_RELY = '#1b6ca8'; C_PMF = '#c1442b'; C_HARD = '#c1442b'; C_OK = '#4a7fb5'

fig = plt.figure(figsize=(15.0, 5.0))
gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 1.0], wspace=0.30)

# ------------------------------------------------------------------ (A)
ax = fig.add_subplot(gs[0, 0])
cur = sorted(R['rui_ro_do_phu_ban_ghi']['duong'], key=lambda e: e['n_keep'])
x = [e['coverage_time_pct'] for e in cur]
ax.plot(x, [e['rely_mean'] for e in cur], 'o-', color=C_RELY, lw=2, ms=4, label='RelyFetal, 1 kenh (113.481 tham so)')
ax.plot(x, [e['pmf4_mean'] for e in cur], 's--', color=C_PMF, lw=2, ms=4, label='Power-MF, 4 kenh (tach nguon ICA)')
ax.fill_between(x, [e['rely_mean'] for e in cur], [e['pmf4_mean'] for e in cur],
                where=[e['diff'] >= 0 for e in cur], color=C_RELY, alpha=0.12, interpolate=True)
ax.fill_between(x, [e['rely_mean'] for e in cur], [e['pmf4_mean'] for e in cur],
                where=[e['diff'] < 0 for e in cur], color=C_PMF, alpha=0.12, interpolate=True)
e0 = R['rui_ro_do_phu_ban_ghi']['do_phu_dau_tien_KTC_duong']
if e0:
    ax.axvline(e0['coverage_time_pct'], color='#555', ls=':', lw=1.2)
    ax.annotate('KTC95 cua hieu so\nlan dau khong chua 0\n(%.0f %% thoi luong, %d/22 ban ghi)'
                % (e0['coverage_time_pct'], e0['n_keep']),
                xy=(e0['coverage_time_pct'], 97.9), xytext=(e0['coverage_time_pct'] - 2, 97.75),
                fontsize=8, ha='right', color='#333')
for e in cur:
    if e['n_keep'] in (22, 21, 20, 19):
        ax.annotate('n=%d' % e['n_keep'], (e['coverage_time_pct'], e['rely_mean']),
                    textcoords='offset points', xytext=(4, 6), fontsize=7, ha='left', color=C_RELY)
ax.set_xlabel('do phu = % THOI LUONG duoc giu lai (bo dan chu the kem tin cay nhat)')
ax.set_ylabel('F1 trung binh theo chu the (%)')
ax.set_title('(A) Rui ro - do phu o MUC CHU THE\ncung tap con con lai cho ca hai phuong phap', fontsize=10)
ax.set_ylim(97.3, 99.95); ax.grid(alpha=0.25); ax.legend(fontsize=8, loc='lower left')

# ------------------------------------------------------------------ (B)
ax = fig.add_subplot(gs[0, 1])
rows = sorted(R['muc_ban_ghi']['bang'], key=lambda r: r['score'])
names = [r['record'] for r in rows]; sc = [r['score'] for r in rows]
cols = [C_HARD if n in HARD else C_OK for n in names]
yy = np.arange(len(names))
ax.barh(yy, sc, color=cols, height=0.72)
for i, r in enumerate(rows):
    ax.text(min(r['score'] + 0.012, 0.995), i, 'F1 %.1f' % r['rely'], va='center', fontsize=7,
            color='#222' if r['record'] not in HARD else C_HARD)
ax.set_yticks(yy); ax.set_yticklabels(names, fontsize=8)
ax.invert_yaxis()
ax.set_xlim(0, 1.50); ax.set_xlabel('diem tin cay = 1 - trung binh p_bad (ngoai fold)')
ax.set_title('(B) Xep hang tin cay 22 chu the\ndo = ba ban ghi RelyFetal thua Power-MF nang', fontsize=10)
ax.grid(axis='x', alpha=0.25)
ax.axhline(2.5, color='#555', ls=':', lw=1.2)
ax.text(1.14, 0.55, 'ba chu the\nbi nghi nhat\n= dung ba\nban ghi kho', fontsize=7.5, color=C_HARD,
        va='center', ha='left', linespacing=1.4)

# ------------------------------------------------------------------ (C)
ax = fig.add_subplot(gs[0, 2])
sc2 = sorted(R['rui_ro_do_phu_doan']['duong'], key=lambda e: e['coverage_time_pct'])
xs = [e['coverage_time_pct'] for e in sc2]
ax.plot(xs, [e['rely_macro_F1'] for e in sc2], '-', color=C_RELY, lw=2, label='RelyFetal 1 kenh')
ax.plot(xs, [e['pmf4_macro_F1'] for e in sc2], '--', color=C_PMF, lw=2, label='Power-MF 4 kenh')
e1 = R['rui_ro_do_phu_doan']['do_phu_dau_tien_KTC_duong']
if e1:
    ax.axvline(e1['coverage_time_pct'], color='#555', ls=':', lw=1.2)
    ax.annotate('KTC95 > 0 tu %.0f %% thoi luong' % e1['coverage_time_pct'],
                xy=(e1['coverage_time_pct'], 97.9), xytext=(e1['coverage_time_pct'] - 3, 97.8),
                fontsize=8, ha='right', color='#333')
ax.set_xlabel('% THOI LUONG giu lai (tu choi tung doan 4 s)')
ax.set_ylabel('F1 trung binh theo chu the tren phan giu lai (%)')
ax.set_title('(C) Rui ro - do phu o MUC DOAN 4 s\ntu choi theo giay, khong theo ban ghi', fontsize=10)
ax.set_ylim(97.3, 99.95); ax.grid(alpha=0.25); ax.legend(fontsize=8, loc='lower right')

fig.suptitle('Cong tu choi hieu chuan lai cho mo hinh 22 ca: no co bat duoc ba ban ghi kho khong?  '
             'CO -- ba ban ghi do xep hang 1, 2, 3 tu duoi len (LOSO, khong ro ri)', fontsize=11, y=1.005)
fig.tight_layout()
p = os.path.join(HERE, 'fig_gate22.png')
fig.savefig(p, dpi=160, bbox_inches='tight')
print('da ghi', p)
