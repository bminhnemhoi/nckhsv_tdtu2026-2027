# -*- coding: utf-8 -*-
"""Hinh M4: (a) duong cong so chu the, (b) phan bo nguon du lieu,
(c) bang chung chong lan CinC<->ADFECGDB, (d) anh huong len so CinC.
Chay: python analysis/dulieu_fig.py -> analysis/fig_dulieu.png
"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
R = json.load(open(os.path.join(HERE, 'dulieu_results.json'), encoding='utf-8'))
AUD = json.load(open(os.path.join(HERE, 'dulieu_audit.json'), encoding='utf-8'))

SURF = '#fcfcfb'
BLUE, AMBER, TEAL, PURPLE = '#2563eb', '#d97706', '#0d9488', '#9333ea'
INK, INK2, MUTED, GRID = '#1c1b1a', '#57534e', '#8a8580', '#e5e3e0'
plt.rcParams.update({'font.size': 8.5, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'figure.facecolor': SURF,
                     'axes.facecolor': SURF, 'axes.titlecolor': INK, 'axes.grid': True,
                     'grid.color': GRID, 'grid.linewidth': .7, 'axes.axisbelow': True,
                     'xtick.major.size': 0, 'ytick.major.size': 0})

fig, AX = plt.subplots(2, 2, figsize=(11.5, 8.2))
fig.subplots_adjust(hspace=.52, wspace=.26, left=.075, right=.975, top=.89, bottom=.085)

# ------------------------------------------------------------------ (a) duong cong
ax = AX[0, 0]
for key, col, lab, mk in (('ngoai_mien_CinC60_sach', BLUE, 'CinC 2013 (ngoài miền, 60 bản sạch)', 'o'),
                          ('trong_mien_B1_10', TEAL, '10 chủ thể B1 (trong miền)', 's')):
    d = R['duong_cong'][key]
    n = np.array(d['n'], float); y = np.array(d['F1'], float)
    ax.plot(n, y, mk, color=col, ms=8, mec=SURF, mew=1.5, zorder=5, label=lab)
    g = np.linspace(4, 105, 300)
    fa = d['fits']['a_minus_b_over_n']; fl = d['fits']['logit_a_plus_b_logn']
    ax.plot(g, fa['a'] - fa['b'] / g, '-', color=col, lw=2, alpha=.9)
    z = fl['a'] + fl['b'] * np.log(g)
    ax.plot(g, 100 / (1 + np.exp(-z)), '--', color=col, lw=2, alpha=.75)
    for x, v in zip(n, y):
        ax.annotate('%.1f' % v, (x, v), textcoords='offset points', xytext=(0, -14),
                    ha='center', color=INK2, fontsize=7.5)
    ax.annotate('%.1f…%.1f' % (fa['du_bao']['50'], fl['du_bao']['50']), (50, fl['du_bao']['50']),
                textcoords='offset points', xytext=(4, 6), color=col, fontsize=7.5)
ax.axvspan(22.5, 105, color=AMBER, alpha=.07, lw=0)
ax.annotate('NGOẠI SUY — 3 điểm dữ liệu, độ tin cậy thấp', (23.5, 88.5), color=AMBER, fontsize=7.5)
ax.set_xscale('log'); ax.set_xticks([5, 12, 22, 50, 100])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.set_xlim(4.3, 110); ax.set_ylim(58, 102)
ax.set_xlabel('số chủ thể huấn luyện (thang log)'); ax.set_ylabel('F1 trung bình mức chủ thể (%)')
ax.set_title('(a) F1 theo số chủ thể huấn luyện\nliền: F1 = a − b/n   ·   đứt: logit tuyến tính theo log n',
             loc='left', fontsize=9.5)
ax.legend(loc='lower right', frameon=False, fontsize=7.2)

# ------------------------------------------------------------------ (b) phan bo nguon
ax = AX[0, 1]
src = R['can_bang']['nguon']
order = ['PhysioNet', 'B2', 'B1']
cols = {'PhysioNet': BLUE, 'B2': TEAL, 'B1': AMBER}
rows = [('giây ghi', 'ty_le_giay_pct'), ('nhịp có nhãn', 'ty_le_nhip_pct'),
        ('đoạn 4 s / epoch', 'ty_le_doan_pct'), ('nhịp NHÌN THẤY / epoch', 'ty_le_nhip_nhin_thay_pct')]
ypos = np.arange(len(rows))[::-1]
for k, (lab, key) in enumerate(rows):
    left = 0.0
    for g in order:
        w = src[g][key]
        ax.barh(ypos[k], w - .35, left=left, height=.52, color=cols[g], zorder=3,
                label=g if k == 0 else None)
        if w > 7:
            ax.text(left + w / 2, ypos[k], '%.0f%%' % w, ha='center', va='center',
                    color=SURF, fontsize=8, fontweight='bold', zorder=4)
        left += w
ax.set_yticks(ypos); ax.set_yticklabels([r[0] for r in rows], fontsize=8)
ax.set_xlim(0, 100); ax.set_xlabel('tỉ lệ trong tập huấn luyện 22 chủ thể (%)')
ax.xaxis.grid(True); ax.yaxis.grid(False)
ax.set_title('(b) Phân bố nguồn — B1 (nhãn GIÁN TIẾP) chiếm đa số\n%d chủ thể · %.1f phút · %s nhịp'
             % (22, R['can_bang']['tong']['phut'], format(R['can_bang']['tong']['nhip'], ',').replace(',', ' ')),
             loc='left', fontsize=9.5)
ax.legend(loc='upper center', bbox_to_anchor=(.5, -.16), frameon=False, fontsize=8, ncol=3)

# ------------------------------------------------------------------ (c) bang chung chong lan
ax = AX[1, 0]
top = AUD['overlap']['signal_top3_per_cinc']
LEAK = R['chong_lan']['danh_sach_ro_ri']
recs = sorted(top, key=lambda c: -top[c][0][0])
v = np.array([top[c][0][0] for c in recs])
isleak = np.array([c in LEAK for c in recs])
x = np.arange(len(recs))
ax.scatter(x[isleak], v[isleak], s=34, color=AMBER, zorder=5, ec=SURF, lw=.8,
           label='15 bản ghi TRÙNG (NCC = 1,0000)')
ax.scatter(x[~isleak], v[~isleak], s=22, color=BLUE, zorder=4, ec=SURF, lw=.6,
           label='60 bản ghi còn lại (NCC ≤ %.2f)' % v[~isleak].max())
for nm, val in AUD['overlap']['signal_positive_control'].items():
    pass
pc = list(AUD['overlap']['signal_positive_control'].values())
ax.axhline(min(pc), color=TEAL, ls=':', lw=1.6, zorder=3)
ax.annotate('đối chứng dương (5 cặp B2↔ADFECGDB đã biết): NCC %.2f–%.2f'
            % (min(pc), max(pc)), (len(recs) * .30, min(pc) - .09), color=TEAL, fontsize=7.5)
ax.set_xlim(-1.5, len(recs) + .5); ax.set_ylim(0, 1.08)
ax.set_xlabel('75 bản ghi CinC 2013 set-a, xếp theo NCC giảm dần')
ax.set_ylabel('max |tương quan chéo chuẩn hoá| với 27 bản ghi gốc')
ax.set_title('(c) CHỒNG LẤN: 15/75 bản ghi CinC là đoạn 60 s cắt ra từ ADFECGDB\n'
             'mỗi bản r01/r04/r07/r08/r10 cho đúng 3 đoạn: 0–60 s, 120–180 s, 240–300 s',
             loc='left', fontsize=9.5)
ax.legend(loc='center right', frameon=False, fontsize=7.5)

# ------------------------------------------------------------------ (d) anh huong
ax = AX[1, 1]
b = R['chong_lan']['bo']
models = ['m5', 'm12', 'm22']
labs = ['m5\n(5 chủ thể)', 'm12\n(12 chủ thể)', 'm22\n(22 chủ thể)']
v75 = [b['75_goc']['%s_psd' % m] for m in models]
v60 = [b['60_sach']['%s_psd' % m] for m in models]
v15 = [b['15_ro_ri']['%s_psd' % m] for m in models]
X = np.arange(3); w = .26
ax.bar(X - w, v75, w - .02, color=MUTED, zorder=3, label='75 bản ghi\n(đã công bố)')
ax.bar(X, v60, w - .02, color=BLUE, zorder=3, label='60 bản ghi SẠCH\n(số ĐÚNG)')
ax.bar(X + w, v15, w - .02, color=AMBER, zorder=3, label='15 bản ghi TRÙNG\n(đã thấy khi h.luyện)')
for xx, a_, c_, d_ in zip(X, v75, v60, v15):
    ax.text(xx - w, a_ + 1.2, '%.1f' % a_, ha='center', color=INK2, fontsize=7.5)
    ax.text(xx, c_ + 1.2, '%.1f' % c_, ha='center', color=BLUE, fontsize=7.5, fontweight='bold')
    ax.text(xx + w, d_ + 1.2, '%.1f' % d_, ha='center', color=AMBER, fontsize=7.5)
ax.set_xticks(X); ax.set_xticklabels(labs, fontsize=8)
ax.set_ylim(0, 132); ax.set_ylabel('F1 trung bình mức bản ghi, quy tắc PSD (%)')
ax.xaxis.grid(False)
ax.set_title('(d) Hậu quả trên CinC 2013: F1 của m22 là %.2f,\nkhông phải %.2f — thổi phồng +%.2f điểm'
             % (b['60_sach']['m22_psd'], b['75_goc']['m22_psd'], R['chong_lan']['thoi_phong']['m22']),
             loc='left', fontsize=9.5)
ax.legend(loc='upper center', frameon=False, fontsize=7.2, ncol=3, handlelength=1.2,
          columnspacing=1.0, borderpad=.1)

fig.suptitle('M4 — Kiểm toán dữ liệu huấn luyện RelyFetal   ·   mọi con số truy về analysis/dulieu_results.json'
             ' và analysis/dulieu_audit.json', fontsize=10.5, color=INK, x=.075, ha='left', y=.975)
out = os.path.join(HERE, 'fig_dulieu.png')
fig.savefig(out, dpi=170, facecolor=SURF)
print('->', out)
