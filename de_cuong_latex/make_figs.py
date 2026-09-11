# -*- coding: utf-8 -*-
"""Sinh toan bo hinh vector (PDF) cho de cuong RelyFetal."""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import NullFormatter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
os.makedirs(OUT, exist_ok=True)

rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = 9
rcParams['axes.linewidth'] = 0.7
rcParams['axes.spines.top'] = False
rcParams['axes.spines.right'] = False
rcParams['xtick.major.width'] = 0.7
rcParams['ytick.major.width'] = 0.7
rcParams['pdf.fonttype'] = 42

BLUE, GREEN, RED, GRAY = '#1F3864', '#1E6B33', '#9B1C1C', '#8A8A8A'
vn = lambda v, n=2: f'{v:.{n}f}'.replace('.', ',')


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.pdf'), bbox_inches='tight', pad_inches=0.03)
    fig.savefig(os.path.join(OUT, name + '.png'), dpi=170, bbox_inches='tight', pad_inches=0.03)
    plt.close(fig)
    print('  ->', name)


# ---------------------------------------------------------------- 1. chuoi cai tien
def fig_waterfall():
    labels = ['GBM\n1-60 Hz', 'GBM\n10-60 Hz', 'GBM\n10-60 Hz', 'CNN 1D\ndilated',
              'TCN 4 giây\nđầu ra từng mẫu']
    labels[0] = 'GBM\n1-45 Hz'
    vals = [80.06, 91.06, 92.49, 92.90, 97.43]
    deltas = [None, '+11,00', None, '+0,41', '+4,53']
    notes = ['điểm xuất phát', 'p < 0,001', 'đổi giao thức', 'p = 0,70\nkhông ý nghĩa', 'p < 0,001']
    cols = [GRAY, GREEN, GRAY, RED, GREEN]

    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    x = np.arange(5)
    ax.bar(x, vals, width=0.52, color=cols, edgecolor='white', linewidth=0.8, zorder=3)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.6, vn(v), ha='center', fontsize=9.2, fontweight='bold')
    labels = [f'{l}\n{n}' for l, n in zip(labels, notes)]
    for i in (1, 3, 4):
        ax.annotate('', xy=(i - 0.28, vals[i]), xytext=(i - 0.72, vals[i - 1]),
                    arrowprops=dict(arrowstyle='-|>', lw=1.0, color=cols[i],
                                    shrinkA=1, shrinkB=1))
        ax.text(i - 0.5, max(vals[i], vals[i - 1]) + 1.7, deltas[i], ha='center',
                fontsize=8.4, color=cols[i], fontweight='bold')
    ax.axvline(1.5, color='#999999', ls=':', lw=1.0, zorder=2, ymin=0.12)
    ax.text(1.5, 101.6, '2 đạo trình  |  4 đạo trình', ha='center', fontsize=7.0,
            color='#666666', style='italic')
    ax.set_yticks([75,80,85,90,95,100])
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7.8, linespacing=1.45)
    ax.set_ylim(74, 103); ax.set_ylabel('Macro F1 (%)')
    ax.grid(axis='y', lw=0.4, color='#DDDDDD', zorder=0)
    ax.set_title('Chuỗi cải tiến đo được trên ADFECGDB (tách bản ghi, $\\pm$50 ms)',
                 fontsize=9.5, pad=8)
    save(fig, 'fig1_chuoi_cai_tien')


# ---------------------------------------------------------------- 2. dai loc
def fig_band():
    d = json.load(open(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'pilot_evidence', 'band_ablation.json'), encoding='utf-8'))
    d = sorted(d, key=lambda r: -r['macro_F1'])
    names = [r['band'] + ' Hz' for r in d]
    f1 = [r['macro_F1'] for r in d]
    sd = [r['sd'] for r in d]
    note = [r['note'] for r in d]
    cols = [GREEN if r['band'] == '10-60' else (RED if r['band'] in ('1-45', '0.5-100', '20-95')
            else BLUE) for r in d]

    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    y = np.arange(len(d))[::-1]
    ax.barh(y, f1, xerr=sd, height=0.6, color=cols, edgecolor='white', linewidth=0.7,
            error_kw=dict(lw=0.7, capsize=2, ecolor='#555555'), zorder=3)
    for i in range(len(d)):
        ax.text(122, y[i], vn(f1[i]), va='center', ha='right', fontsize=8.6, fontweight='bold')
        ax.text(128, y[i], note[i], va='center', ha='left', fontsize=7.2,
                color='#444444', style='italic')
    ax.text(122, len(d) - 0.3, 'F1', ha='right', fontsize=7.6, fontweight='bold', color='#333333')
    ax.text(128, len(d) - 0.3, 'nguồn', ha='left', fontsize=7.6, fontweight='bold', color='#444444')
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8.6)
    ax.set_xlim(0, 195); ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel('Macro F1 (%)')
    ax.grid(axis='x', lw=0.4, color='#DDDDDD', zorder=0)
    ax.set_title('Khảo sát 8 dải thông: chênh lệch 18,9 điểm F1', fontsize=9.5, pad=8)
    save(fig, 'fig2_dai_loc')


# ---------------------------------------------------------------- 3. 16 kien truc
def fig_arch():
    data = [('resnet1d', 92545, 98.96), ('tcn', 63105, 98.88), ('transformer', 80385, 98.81),
            ('cnn_l', 83137, 98.77), ('cnn_dil', 25953, 98.56), ('cnn_gru', 28257, 98.25),
            ('unet1d', 46345, 98.01), ('cnn_wide_k', 38753, 97.93), ('cnn_se', 29845, 97.65),
            ('twostream', 53601, 97.24), ('cnn_m', 25953, 97.14), ('cnn_s', 13857, 96.60),
            ('mlp', 27649, 96.41), ('cnn2d_delay', 27633, 93.08), ('linear', 151, 48.55),
            ('cnn2d_pi', 27777, 27.42)]
    names = [d[0] for d in data]; f1 = [d[2] for d in data]
    cols = [RED if n == 'cnn2d_pi' else (GREEN if n == 'cnn_dil' else (GRAY if n == 'linear'
            else BLUE)) for n in names]

    fig, ax = plt.subplots(figsize=(6.2, 4.1))
    y = np.arange(len(data))[::-1]
    ax.barh(y, f1, height=0.64, color=cols, edgecolor='white', linewidth=0.7, zorder=3)
    for i, (n, p, v) in enumerate(data):
        ax.text(118, y[i], vn(v), va='center', ha='right', fontsize=8.2, fontweight='bold')
        ax.text(146, y[i], f'{p:,}'.replace(',', '.'), va='center', ha='right',
                fontsize=7.4, color='#555555')
    ax.text(118, len(data) - 0.25, 'F1', ha='right', fontsize=7.8, fontweight='bold', color='#333333')
    ax.text(146, len(data) - 0.25, 'tham số', ha='right', fontsize=7.8, fontweight='bold',
            color='#555555')
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8.3, fontfamily='Consolas')
    ax.set_xlim(0, 148); ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel('F1 trên bản ghi validation (%)')
    ax.grid(axis='x', lw=0.4, color='#DDDDDD', zorder=0)
    ax.set_title('16 kiến trúc, cùng dữ liệu và cùng ngân sách tham số', fontsize=9.5, pad=8)
    ax.annotate('đề xuất ban đầu\nPersistence Image + CNN 2D', xy=(28.5, y[-1]),
                xytext=(52, y[-1] + 1.15), fontsize=7.6, color=RED, va='center',
                linespacing=1.35, arrowprops=dict(arrowstyle='-|>', color=RED, lw=0.8))
    save(fig, 'fig3_kien_truc')


# ---------------------------------------------------------------- 4. truong tiep nhan
def fig_rf():
    rf = [172, 748, 1516, 3052]; f1 = [98.73, 99.25, 99.50, 99.52]
    fig, ax = plt.subplots(figsize=(5.2, 2.8))
    xi = np.arange(4)
    ax.plot(xi, f1, 'o-', color=BLUE, lw=1.7, ms=6.5, zorder=3)
    for i, b in enumerate(f1):
        ax.annotate(vn(b), (xi[i], b), textcoords='offset points', xytext=(0, 9),
                    ha='center', fontsize=8.6, fontweight='bold')
    ax.axvline(2, color=GREEN, ls='--', lw=1.0, zorder=2)
    ax.text(2.08, 98.80, 'chọn 1.516 ms\nlợi ích bão hoà', fontsize=7.8, color=GREEN,
            linespacing=1.35)
    ax.set_xticks(xi)
    ax.set_xticklabels([f'{v}' for v in rf], fontsize=8.6)
    ax.set_xlim(-0.35, 3.35)
    ax.set_xlabel('Trường tiếp nhận (ms)'); ax.set_ylabel('F1 (%)')
    ax.set_ylim(98.5, 99.78)
    ax.grid(lw=0.4, color='#DDDDDD', zorder=0)
    ax.set_title('Trường tiếp nhận là biến kiến trúc chi phối', fontsize=9.5, pad=8)
    save(fig, 'fig4_truong_tiep_nhan')


# ---------------------------------------------------------------- 5. doi chuan 3 ben
def fig_bench():
    recs = ['r01', 'r04', 'r07', 'r08', 'r10']
    ours = [100.00, 99.60, 100.00, 99.77, 96.54]
    khanh = [97.04, 83.13, 91.65, 94.62, 86.42]
    fig, ax = plt.subplots(figsize=(5.8, 3.2))
    x = np.arange(5); w = 0.34
    ax.bar(x - w / 2, khanh, w, label='TDA + Dual-Branch CNN (mô hình đối chiếu)', color=GRAY,
           edgecolor='white', linewidth=0.7, zorder=3)
    ax.bar(x + w / 2, ours, w, label='FetalQRS-TCN, tách bản ghi (mô hình của nhóm)', color=BLUE,
           edgecolor='white', linewidth=0.7, zorder=3)
    for i in range(5):
        ax.text(x[i] - w / 2, khanh[i] + 0.7, vn(khanh[i], 1), ha='center', fontsize=7.4)
        ax.text(x[i] + w / 2, ours[i] + 0.7, vn(ours[i], 1), ha='center', fontsize=7.4,
                fontweight='bold')
    ax.axhline(98.08, color=RED, ls='--', lw=1.0, zorder=2)
    ax.text(4.55, 104.6, 'DPSS 98,08  —  số công bố thật trên ADFECGDB nhóm chuyển dạ',
            fontsize=7.2, color=RED, va='center', ha='right')
    ax.annotate('', xy=(4.55, 98.6), xytext=(4.55, 103.9),
                arrowprops=dict(arrowstyle='-|>', color=RED, lw=0.7))
    ax.set_xticks(x); ax.set_xticklabels(recs, fontsize=9)
    ax.set_ylim(78, 107); ax.set_yticks([80, 85, 90, 95, 100])
    ax.set_ylabel('F1 (%)')
    ax.legend(fontsize=7.6, frameon=False, loc='lower center',
              bbox_to_anchor=(0.5, -0.30), ncol=2)
    ax.grid(axis='y', lw=0.4, color='#DDDDDD', zorder=0)
    ax.set_title('Đối chuẩn trên giao thức kênh lâm sàng tốt nhất ($\\pm$50 ms)',
                 fontsize=9.5, pad=8)
    save(fig, 'fig5_doi_chuan')


# ---------------------------------------------------------------- 6. sup do luong cuc
def fig_bimodal():
    recs = ['a03', 'a05', 'a08', 'a04', 'a01', 'a07', 'a09', 'a10', 'a06', 'a02']
    f1 = [100.00, 100.00, 100.00, 99.61, 94.29, 84.82, 79.84, 48.98, 42.75, 23.08]
    cols = [GREEN if v >= 90 else (BLUE if v >= 70 else RED) for v in f1]
    fig, ax = plt.subplots(figsize=(5.8, 3.0))
    x = np.arange(10)
    ax.bar(x, f1, 0.58, color=cols, edgecolor='white', linewidth=0.7, zorder=3)
    for i, v in enumerate(f1):
        ax.text(i, v + 1.8, vn(v, 1), ha='center', fontsize=7.6, fontweight='bold')
    ax.axhline(77.34, color=GRAY, ls='--', lw=1.0, zorder=2)
    ax.text(9.45, 74.5, 'trung bình 77,34', fontsize=7.4, color='#555555',
            va='top', ha='right')
    ax.axvspan(6.5, 9.5, color=RED, alpha=0.07, zorder=1)
    ax.text(8.0, 62, 'ba bản ghi sụp đổ', ha='center', fontsize=7.8, color=RED, fontweight='bold')
    ax.text(8.0, 56, 'động cơ của đóng góp C3', ha='center', fontsize=7.4, color=RED)
    ax.set_xticks(x); ax.set_xticklabels(recs, fontsize=8.6)
    ax.set_ylim(0, 112); ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel('F1 (%)')
    ax.grid(axis='y', lw=0.4, color='#DDDDDD', zorder=0)
    ax.set_title('Xuyên bộ dữ liệu sang CinC 2013: phân bố lưỡng cực', fontsize=9.5, pad=8)
    save(fig, 'fig6_luong_cuc')


# ---------------------------------------------------------------- 7. tien xu ly vs kien truc
def fig_dongop():
    fig, ax = plt.subplots(figsize=(5.2, 2.4))
    items = ['Front-end tín hiệu\nđổi dải thông', 'Độ dài ngữ cảnh\nvà độ phân giải đầu ra',
             'Họ kiến trúc\nở ngữ cảnh cố định']
    vals = [11.00, 4.53, 0.41]
    tags = ['p < 0,001', 'p < 0,001', 'p = 0,70']
    cols = [GREEN, BLUE, RED]
    y = np.arange(3)[::-1]
    ax.barh(y, vals, 0.52, color=cols, edgecolor='white', linewidth=0.7, zorder=3)
    for i, v in enumerate(vals):
        ax.text(v + 0.3, y[i], f'+{vn(v)} điểm', va='center', fontsize=8.6, fontweight='bold')
        ax.text(v + 4.1, y[i], tags[i], va='center', fontsize=7.4, color=cols[i], style='italic')
    ax.set_yticks(y); ax.set_yticklabels(items, fontsize=8.3, linespacing=1.35)
    ax.set_xlim(0, 18); ax.set_xticks([0, 4, 8, 12, 16])
    ax.set_xlabel('Mức tăng Macro F1 (điểm)')
    ax.grid(axis='x', lw=0.4, color='#DDDDDD', zorder=0)
    ax.set_title('Phân rã đóng góp ba tầng', fontsize=9.5, pad=8)
    save(fig, 'fig7_dong_gop')


# ---------------------------------------------------------------- 13. bang kien truc chay lai dung giao thuc
def fig_arch_v2():
    import json as _j
    d = _j.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 'pilot_evidence', 'arch_loro_merged.json'), encoding='utf-8'))
    rows = [(v['summary']['macro_F1'], k, v['summary']['sd_F1'], v.get('params', 0))
            for k, v in d['results'].items()]
    rows.sort()
    names = [r[1] for r in rows]; f1 = [r[0] for r in rows]; sd = [r[2] for r in rows]; pr = [r[3] for r in rows]
    pv = {'cnn_l': 'p = 0,39', 'cnn_dil': 'mốc', 'mlp': 'p = 0,93', 'cnn_gru': 'p = 0,33',
          'tcn': 'p = 0,26', 'resnet1d': 'p = 0,11', 'cnn_m': 'p = 0,0001', 'linear': 'p < 0,0001'}
    cols = [GREEN if n == 'cnn_dil' else (RED if n in ('linear', 'cnn_m') else BLUE) for n in names]
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    y = np.arange(len(rows))
    ax.barh(y, f1, xerr=sd, height=0.62, color=cols, edgecolor='white', linewidth=0.7,
            error_kw=dict(lw=0.7, capsize=2, ecolor='#555555'), zorder=3)
    for i in range(len(rows)):
        ax.text(112, y[i], vn(f1[i]), va='center', ha='right', fontsize=8.4, fontweight='bold')
        ax.text(117, y[i], pv.get(names[i], ''), va='center', ha='left', fontsize=7.2,
                color='#444444', style='italic')
        ax.text(146, y[i], f'{pr[i]:,}'.replace(',', '.'), va='center', ha='right', fontsize=7.2, color='#555555')
    ax.text(112, len(rows) - 0.35, 'F1', ha='right', fontsize=7.6, fontweight='bold', color='#333333')
    ax.text(117, len(rows) - 0.35, 'p vs cnn_dil', ha='left', fontsize=7.6, fontweight='bold', color='#444444')
    ax.text(146, len(rows) - 0.35, 'tham số', ha='right', fontsize=7.6, fontweight='bold', color='#555555')
    ax.axvline(97.43, color=GREEN, ls='--', lw=1.0, zorder=2)
    ax.text(96.2, len(rows) - 0.35, 'mô hình chính 97,43 →', ha='right', fontsize=7.2, color=GREEN)
    ax.set_ylim(-0.6, len(rows) - 0.05)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8.3, fontfamily='Consolas')
    ax.set_xlim(0, 148); ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel('Macro F1 (%) trên 20 (bản ghi × kênh), tách bản ghi, ngưỡng chọn trên validation')
    ax.grid(axis='x', lw=0.4, color='#DDDDDD', zorder=0)
    ax.set_title('Bảng kiến trúc chạy lại đúng giao thức, dải 10–60 Hz, cửa sổ 300 ms', fontsize=9.5, pad=8)
    save(fig, 'fig13_kien_truc_v2')


# ---------------------------------------------------------------- 16. mo hinh 5 ca vs 22 ca
def fig_m22():
    groups = ['PhysioNet\nchuyển dạ (5)', 'Silesia B2\nchuyển dạ mới (7)', 'Silesia B1\nthai kỳ (10)',
              'CinC 2013\nhệ ghi khác (10)']
    m5 = [99.21, 95.87, 93.30, 77.34]; m22 = [99.40, 96.82, 97.15, 90.34]
    pv = ['p = 1,00', 'p = 0,13', 'p = 0,037', 'p = 0,016']
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    x = np.arange(4); w = 0.36
    ax.bar(x - w / 2, m5, w, label='mô hình 5 ca', color=GRAY, edgecolor='white', linewidth=0.7, zorder=3)
    ax.bar(x + w / 2, m22, w, label='mô hình 22 ca', color=GREEN, edgecolor='white', linewidth=0.7, zorder=3)
    for i in range(4):
        ax.text(x[i] - w / 2, m5[i] + 0.6, vn(m5[i]), ha='center', fontsize=7.6)
        ax.text(x[i] + w / 2, m22[i] + 0.6, vn(m22[i]), ha='center', fontsize=7.6, fontweight='bold')
        ax.text(x[i], 72.5, pv[i], ha='center', fontsize=7.2, style='italic',
                color=GREEN if i >= 2 else '#666666')
    ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=8.0, linespacing=1.35)
    ax.set_ylim(70, 104); ax.set_yticks([70, 80, 90, 100]); ax.set_ylabel('Macro F1 (%), kênh PSD mù nhãn')
    ax.legend(fontsize=7.8, frameon=False, loc='upper right', ncol=2)
    ax.grid(axis='y', lw=0.4, color='#DDDDDD', zorder=0)
    ax.set_title('Huấn luyện trên 22 sản phụ thay vì 5: cùng chủ thể, cùng giao thức', fontsize=9.5, pad=8)
    save(fig, 'fig16_m22')


if __name__ == '__main__':
    print('Sinh hinh vao', OUT)
    fig_waterfall(); fig_band(); fig_arch(); fig_rf(); fig_bench(); fig_bimodal(); fig_dongop(); fig_arch_v2(); fig_m22()
    print('XONG')
