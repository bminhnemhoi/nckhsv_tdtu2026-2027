# -*- coding: utf-8 -*-
"""Hinh bo sung M4b: (a) kiem chong lan doc lap, (b) chon kenh tren 60 ban sach.
Chay: python analysis/dulieu_m4b_fig.py -> analysis/fig_dulieu_m4b.png"""
import os, sys, json
os.environ['OMP_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({'font.size': 8.5, 'axes.grid': True, 'grid.alpha': .25,
                     'font.family': 'DejaVu Sans', 'axes.axisbelow': True})
R = json.load(open(os.path.join(HERE, 'dulieu_results.json'), encoding='utf-8'))
V = json.load(open(os.path.join(HERE, 'dulieu_m4b_verify.json'), encoding='utf-8'))
F = json.load(open(os.path.join(HERE, 'chonkenh_results.json'), encoding='utf-8'))['F1_tung_ban_ghi']['cinc']
LEAK = V['danh_sach_ro_ri']

fig, AX = plt.subplots(1, 3, figsize=(15.0, 4.4))
fig.subplots_adjust(wspace=.30, left=.055, right=.988, top=.80, bottom=.23)

# ---- (a) phan bo |NCC| lon nhat cua CA 75 ban ghi ----
ax = AX[0]
N = V['ncc_tung_ban_ghi_75']
vals = np.array([abs(N[t]['ncc']) for t in sorted(N)])
isleak = np.array([t in set(LEAK) for t in sorted(N)])
bins = np.linspace(0, 1.02, 35)
ax.hist(vals[~isleak], bins=bins, color='#2e86de', alpha=.85, label='60 bản SẠCH (n = 60)')
ax.hist(vals[isleak], bins=bins, color='#c0392b', alpha=.95, label='15 bản RÒ RỈ (n = 15)')
clean_max = V['ncc_lon_nhat_60_ban_con_lai']
ax.axvspan(clean_max, 1.0, color='#f1c40f', alpha=.18, zorder=0)
ax.annotate('', xy=(clean_max, 13.2), xytext=(1.0, 13.2),
            arrowprops=dict(arrowstyle='<->', color='#8a6d00', lw=1.2))
ax.text((clean_max + 1.0) / 2, 13.9, 'khoảng trống %.3f\nkhông có vùng xám' % (1.0 - clean_max),
        ha='center', va='bottom', fontsize=8, color='#8a6d00', style='italic')
ax.set_xlim(0, 1.06); ax.set_ylim(0, 17.5)
ax.set_xlabel('|NCC| lớn nhất với bất kỳ kênh ADFECGDB nào (tín hiệu thô)')
ax.set_ylabel('số bản ghi CinC 2013 set-a')
ax.legend(loc='upper center', bbox_to_anchor=(.5, -.155), ncol=2, fontsize=7.8, frameon=False)
ax.set_title('(a) Kiểm chồng lấn ĐỘC LẬP — phân bố lưỡng cực tuyệt đối\n'
             'mỗi bản rò rỉ = cả 4 kênh sao chép nguyên vẹn, 3 cửa sổ/bản gốc', fontsize=9)

# ---- (b) chon kenh: 75 o nhiem vs 60 sach ----
ax = AX[1]
B = R['chon_kenh_60_sach']['bang']
order = ['psd', 'fuse_k2', 'learned', 'rrplaus', 'rrcv', 'gate', 'gate4', 'peakprob', 'oracle']
lab = {'psd': 'psd (đang dùng)', 'fuse_k2': 'fuse_k2', 'learned': 'learned', 'rrplaus': 'rrplaus',
       'rrcv': 'rrcv', 'gate': 'gate (tiền ĐK)', 'gate4': 'gate4 (tiền ĐK)',
       'peakprob': 'peakprob (hậu kiểm)', 'oracle': 'ORACLE (trần)'}
y = np.arange(len(order))
v75 = [B[r]['mean_75_o_nhiem'] for r in order]
v60 = [B[r]['mean_60_sach'] for r in order]
ax.barh(y + .19, v75, height=.36, color='#b8c4d0', label='75 bản (Ô NHIỄM — đã rút)')
ax.barh(y - .19, v60, height=.36, color=['#c0392b' if r == 'oracle' else
        ('#7f8c8d' if r == 'psd' else '#2e86de') for r in order], label='60 bản SẠCH')
for i, r in enumerate(order):
    ax.text(v60[i] + .7, i - .19, '%.2f' % B[r]['mean_60_sach'], va='center', fontsize=7.4)
    ax.text(v75[i] + .7, i + .19, '%.2f' % B[r]['mean_75_o_nhiem'], va='center', fontsize=7.0, color='#777')
ax.set_xticks([0,20,40,60,80,100])
ax.set_yticks(y); ax.set_yticklabels([lab[r] for r in order], fontsize=8)
ax.set_xlim(0, 100); ax.set_ylim(-.7, len(order)-.3); ax.set_xlabel('F1 trung bình mức bản ghi (%)')
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color='#b8c4d0', label='75 bản (Ô NHIỄM — đã rút)'),
                   Patch(color='#2e86de', label='60 bản SẠCH'),
                   Patch(color='#7f8c8d', label='psd — mốc so sánh'),
                   Patch(color='#c0392b', label='ORACLE — trần')],
          loc='upper center', bbox_to_anchor=(.5, -.155), ncol=2, fontsize=7.5, frameon=False)
ax.set_title('(b) Chọn kênh (M5) tính lại trên 60 bản sạch\n'
             'hiệu ứng MẠNH LÊN: peakprob +6,20 → +7,73 điểm', fontsize=9)


# ---- (c) thi nghiem tang cuong / can bang ----
ax = AX[2]
T = R['thuc_nghiem']
A = T['tang_cuong_vs_khong']; C = T['can_bang_vs_base']
items = []
for r in A['tung_chu_the']:
    items.append(('aug', r['chu_the'], r['hieu'], max(r['A'], r['B'])))
cm = {r['chu_the']: r['hieu'] for r in C['tung_chu_the']}
subs = [r['chu_the'] for r in A['tung_chu_the']]
subs = sorted(subs, key=lambda t: -max(r['A'] for r in A['tung_chu_the'] if r['chu_the'] == t))
y = np.arange(len(subs))
aug = [next(r['hieu'] for r in A['tung_chu_the'] if r['chu_the'] == t) for t in subs]
bal = [cm.get(t, np.nan) for t in subs]
ax.barh(y + .20, aug, height=.38, color='#95a5a6', label='tăng cường − KHÔNG tăng cường')
ax.barh(y - .20, bal, height=.38, color='#16a085', label='cân bằng nguồn − cơ sở')
ax.axvline(0, color='#333', lw=1.0)
for i, t in enumerate(subs):
    if not np.isnan(bal[i]) and abs(bal[i]) > .05:
        ax.text(bal[i] + .07, i - .20, '%+.2f' % bal[i], va='center', fontsize=7.2, color='#0e6655')
    if abs(aug[i]) > .05:
        ax.text(aug[i] + (.07 if aug[i] > 0 else -.07), i + .20, '%+.2f' % aug[i], va='center',
                ha='left' if aug[i] > 0 else 'right', fontsize=7.2, color='#555')
hard = {'B1_06', 'B1_07', 'B2_03'}
ax.set_yticks(y)
ax.set_yticklabels([t + ('  ◄ khó' if t in hard else '') for t in subs], fontsize=8)
ax.set_xlim(-2.6, 2.6); ax.set_ylim(-.7, len(subs) - .3)
ax.set_xlabel('thay đổi F1 mức chủ thể (điểm)')
ax.legend(loc='upper center', bbox_to_anchor=(.5, -.155), ncol=1, fontsize=7.5, frameon=False)
ax.set_title('(c) M4-mini: tăng cường KHÔNG làm gì, cân bằng nguồn thì có\n'
             + ('aug %+.2f KTC [%+.2f; %+.2f]  ·  bal %+.2f KTC [%+.2f; %+.2f]'
                % (A['hieu_trung_binh'], A['ci95'][0], A['ci95'][1],
                   C['hieu_trung_binh'], C['ci95'][0], C['ci95'][1])
                ).replace('.', ',').replace('-', '−'), fontsize=9)

fig.suptitle('M4b — kiểm chứng độc lập chồng lấn dữ liệu · hệ quả cho chọn kênh · thí nghiệm tăng cường và cân bằng',
             fontsize=10.5, y=.975)
out = os.path.join(HERE, 'fig_dulieu_m4b.png')
fig.savefig(out, dpi=150)
print('-> ' + out)
