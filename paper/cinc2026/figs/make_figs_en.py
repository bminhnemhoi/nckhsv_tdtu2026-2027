# -*- coding: utf-8 -*-
"""
Re-draw the two manuscript figures with English labels, from the same JSON sources
used by the Vietnamese originals (kept untouched next to these files):
  fig13_arch_en.pdf          <- survey/facts_phase1.json  A_bang_kien_truc_v2  (source: pilot_evidence/arch_loro_merged.json)
  fig9_risk_coverage_en.pdf  <- fsqi/results.json  risk_coverage.curves.*.macro
Run:  python paper/cinc2026/figs/make_figs_en.py
"""
import os, sys, json
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))

INK, INK2, GRID = '#1a1a1a', '#5a5a5a', '#e2e2e2'
BLUE, ORANGE, GREEN, GRAY, RED = '#2a5fa8', '#d9642a', '#2f8f5b', '#9a9a9a', '#b03a2e'
plt.rcParams.update({'font.size': 8, 'font.family': 'serif', 'axes.edgecolor': INK2, 'axes.labelcolor': INK,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.spines.top': False,
                     'axes.spines.right': False, 'pdf.fonttype': 42})

# ------------------------------------------------------------------ Fig: architecture benchmark
fp = json.load(open(os.path.join(ROOT, 'survey', 'facts_phase1.json'), encoding='utf-8'))
rows = fp['A_bang_kien_truc_v2']['xep_hang']
NAME = {'cnn_l': 'large CNN', 'cnn_dil': 'dilated CNN', 'mlp': 'MLP', 'cnn_gru': 'CNN-GRU', 'tcn': 'TCN',
        'resnet1d': 'ResNet-1D', 'cnn_m': 'plain CNN', 'linear': 'linear'}
rows = sorted(rows, key=lambda r: r['macro_F1'])          # lowest at bottom
fig, ax = plt.subplots(figsize=(3.6, 2.5))
y = np.arange(len(rows))
for i, r in enumerate(rows):
    sig = r['p'] is not None and r['p'] < 0.05
    col = GREEN if r['arch'] == 'cnn_dil' else (RED if sig else BLUE)
    ax.barh(i, r['macro_F1'], height=0.62, color=col, xerr=r['sd'], error_kw=dict(ecolor=INK2, lw=0.8, capsize=2))
ax.axvline(97.43, color=GREEN, ls='--', lw=1)
ax.text(97.0, len(rows) - 0.45, '4 s per-sample TCN 97.43', ha='right', va='center', fontsize=6.2, color=GREEN)
ax.set_yticks(y); ax.set_yticklabels([NAME[r['arch']] for r in rows])
ax.set_xlim(0, 170); ax.set_ylim(-0.6, len(rows) - 0.2)
ax.set_xlabel('macro F1 (%), 20 (record x lead), LORO', loc='left')
ax.grid(axis='x', color=GRID, lw=0.6); ax.set_axisbelow(True)
# right-hand columns: F1, p vs dilated CNN, parameters
x0, x1, x2 = 103, 123, 168
ax.text(x0, len(rows) - 0.45, 'F1', fontsize=6.2, fontweight='bold', color=INK, va='center')
ax.text(x1, len(rows) - 0.45, 'p vs dil.', fontsize=6.2, fontweight='bold', color=INK, va='center')
ax.text(x2, len(rows) - 0.45, 'params', fontsize=6.2, fontweight='bold', color=INK, va='center', ha='right')
for i, r in enumerate(rows):
    ax.text(x0, i, '%.2f' % r['macro_F1'], fontsize=6.2, va='center', color=INK)
    p = 'ref.' if r['p'] is None else ('<0.0001' if r['p'] < 1e-4 else ('%.4f' % r['p'] if r['p'] < 0.01 else '%.2f' % r['p']))
    ax.text(x1, i, p, fontsize=6.2, va='center', color=INK2, style='italic')
    ax.text(x2, i, '{:,}'.format(r['tham_so']), fontsize=6.2, va='center', color=INK2, ha='right')
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.spines['bottom'].set_bounds(0, 100)
ax.set_clip_on(False)
# allow the text columns to sit outside the data range without clipping
for t in ax.texts: t.set_clip_on(False)
fig.savefig(os.path.join(HERE, 'fig13_arch_en.pdf'), bbox_inches='tight', pad_inches=0.02)
plt.close(fig)
print('fig13_arch_en.pdf', [(r['arch'], r['macro_F1']) for r in rows])

# ------------------------------------------------------------------ Fig: risk-coverage
fs = json.load(open(os.path.join(ROOT, 'fsqi', 'results.json'), encoding='utf-8'))
rc = fs['risk_coverage']
cov = 100 - np.asarray(rc['reject_fracs'], float)
C = rc['curves']
fig, ax = plt.subplots(figsize=(3.4, 2.3))
ax.plot(cov, C['oracle']['macro'], color=INK, ls='--', lw=1.2, label='oracle (true segment F1)')
ax.plot(cov, C['random']['macro'], color=GRAY, lw=1.6, label='random rejection')
ax.plot(cov, C['topo']['macro'], color=BLUE, lw=1.6, label='topological (16)')
ax.plot(cov, C['classical']['macro'], color=ORANGE, lw=1.6, label='classical (12)')
ax.plot(cov, C['combined']['macro'], color=GREEN, lw=1.6, label='combined (28)')
ax.set_xlim(100, 50); ax.set_ylim(60, 100)
ax.set_xlabel('coverage (% of 4 s segments retained)')
ax.set_ylabel('macro F1 of retained segments (%)')
ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=6.2, loc='upper left')
for cv in (80, 50):
    i = int(np.argmin(np.abs(cov - cv)))
    ax.annotate('%.1f' % C['classical']['macro'][i], (cov[i], C['classical']['macro'][i]),
                xytext=((0, -9) if cv == 80 else (-4, -9)), textcoords='offset points',
                ha=('center' if cv == 80 else 'right'), fontsize=6.2, color=ORANGE)
fig.savefig(os.path.join(HERE, 'fig9_risk_coverage_en.pdf'), bbox_inches='tight', pad_inches=0.02)
plt.close(fig)
print('fig9_risk_coverage_en.pdf  classical@80 %.2f @50 %.2f' % (
    C['classical']['macro'][20], C['classical']['macro'][50]))
