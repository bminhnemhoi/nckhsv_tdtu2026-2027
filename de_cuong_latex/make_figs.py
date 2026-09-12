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
    # Moi tri so p cua ban 3.2 da bi go (tinh tren 20-60 hang ban ghi x kenh x seed = gia lap).
    # Nhan duoi moi cot chi ghi PHAM VI DO, khong ghi p.
    notes = ['điểm xuất phát', 'đo trên GBM\ncửa sổ 300 ms', 'đổi giao thức',
             '$n=5$: không đủ lực', 'KTC chủ thể\n[+1,58; +7,43]']
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
    # Ket qua so bo tren chinh TCN: pilot_evidence/band_tcn_stats.json
    fig.text(0.5, -0.10, 'Bước $+11{,}00$ đo trên GBM. Lặp lại đúng thay đổi dải đó trên chính TCN, 22 chủ thể:\n'
             'chỉ $+2{,}44$ điểm, KTC 95% $[-0{,}04;\\ +6{,}29]$ — chạm số không (kết quả sơ bộ)',
             fontsize=6.8, color=RED, ha='center', va='top', linespacing=1.45)
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
    ax.set_title('Khảo sát 8 dải thông trên GBM cửa sổ 300 ms: chênh lệch 18,9 điểm F1',
                 fontsize=8.8, pad=8)
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
    # 77,34 = trung binh KENH 0 CO DINH tren dung MAU 10 ban ghi nay. Con so do DA BI RUT
    # (chon hau kiem; tren du 75 ban ghi quy tac nay chi dat 58,72 voi mo hinh 5 ca).
    # Giu duong ke vi no mo ta dung mau 10 ban ghi trong hinh, nhung NHAN phai noi ro pham vi.
    ax.axhline(77.34, color=GRAY, ls='--', lw=1.0, zorder=2)
    fig.text(0.5, -0.09, 'Đường 77,34 là trung bình của riêng mẫu 10 bản ghi này dưới quy tắc kênh 0 hậu kiểm; '
             'con số đó ĐÃ BỊ RÚT.\nTrên toàn bộ 75 bản ghi set-a, chính quy tắc ấy chỉ đạt 58,72. '
             'Số chính: xem hình CinC 75 bản ghi.',
             fontsize=6.6, color=RED, ha='center', va='top', linespacing=1.45)
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
    fig, ax = plt.subplots(figsize=(5.9, 2.9))
    items = ['Front-end tín hiệu\nđổi dải thông', 'Độ dài ngữ cảnh\nvà độ phân giải đầu ra',
             'Họ kiến trúc\nở ngữ cảnh cố định']
    vals = [11.00, 4.53, 0.41]
    # Khong ghi p: moi tri so p cua ban 3.2 tinh tren ban ghi x kenh x seed nen gia lap, da bi go.
    tags = ['đo trên GBM, cửa sổ 300 ms', 'KTC chủ thể [+1,58; +7,43]', '$n=5$: không đủ lực']
    cols = [GREEN, BLUE, RED]
    y = np.arange(3)[::-1]
    ax.barh(y, vals, 0.38, color=cols, edgecolor='white', linewidth=0.7, zorder=3)
    for i, v in enumerate(vals):
        ax.text(v + 0.3, y[i], f'+{vn(v)} điểm', va='center', fontsize=8.0, fontweight='bold')
        ax.text(v + 3.9, y[i], tags[i], va='center', fontsize=6.8, color=cols[i], style='italic')
    # Tang 1 do lai tren CHINH TCN (so bo): pilot_evidence/band_tcn_stats.json
    yy = y[0] - 0.44
    ax.barh(yy, 2.44, 0.28, color='white', edgecolor=RED, linewidth=0.9, hatch='////', zorder=3)
    ax.plot([-0.04, 6.29], [yy, yy], lw=1.1, color=RED, zorder=4, solid_capstyle='butt')
    ax.plot([-0.04, 6.29], [yy, yy], '|', ms=4, color=RED, zorder=4)
    ax.text(6.7, yy, 'lặp lại trên chính TCN (sơ bộ): $+2{,}44$ điểm,\nKTC $[-0{,}04;\\ +6{,}29]$ chạm số không',
            va='center', fontsize=6.5, color=RED, style='italic', linespacing=1.35)
    ax.set_yticks(y); ax.set_yticklabels(items, fontsize=8.3, linespacing=1.35)
    ax.set_ylim(-0.95, 2.45)
    ax.set_xlim(-1.4, 18); ax.set_xticks([0, 4, 8, 12, 16])
    ax.set_xlabel('Mức tăng Macro F1 (điểm)')
    ax.grid(axis='x', lw=0.4, color='#DDDDDD', zorder=0)
    ax.set_title('Phân rã đóng góp ba tầng (tầng 1 đo trên GBM; bản lặp trên TCN còn sơ bộ)',
                 fontsize=8.6, pad=8)
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
# DA RUT (12/09/2026): cot CinC cua hinh nay dung 77,34 / 90,34 -- do tren MAU 10/75 ban ghi voi
# quy tac kenh 0 co dinh chon HAU KIEM, ca hai con so deu da bi rut. Hinh thay the la fig_m22_v2()
# (fig19_m22_v2), dung 71,21 / 79,40 tren du 75 ban ghi. Ham nay KHONG con duoc goi trong __main__;
# giu lai chi de doi chieu lich su. Tep fig16_m22.pdf/.png sinh ra truoc day nen bi XOA.
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


# ---------------------------------------------------------------- 17. Power-MF chay lai vs RelyFetal
def _load_v33():
    return json.load(open(os.path.join(os.path.dirname(OUT), 'data_v33.json'), encoding='utf-8'))


def fig_powermf():
    """Ba cau hinh: Power-MF 4 kenh, Power-MF 1 kenh, RelyFetal 1 kenh.

    Doc thang tu baselines/powermf_fair_stats.json (khong qua data_v33.json)
    de moi con so tren hinh truy nguoc duoc ve dung mot tep JSON.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    S = json.load(open(os.path.join(root, 'baselines', 'powermf_fair_stats.json'),
                       encoding='utf-8'))
    ps = S['per_subject']
    order = {'ADFECGDB': 0, 'B2': 1, 'B1': 2}
    ps = sorted(ps, key=lambda r: (order[r['grp']], r['rec']))
    THUA = {'B1_07', 'B1_06', 'B2_03'}          # ba ban ghi RelyFetal thua nang

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(7.2, 5.0),
                                   gridspec_kw={'width_ratios': [1.30, 1.0]})

    # ---------- (A) ba cot moi chu the
    y = np.arange(len(ps))[::-1]
    h = 0.26
    for i, r in enumerate(ps):
        yy = y[i]
        axA.barh(yy + h, r['pmf4'], h, color=BLUE, edgecolor='white',
                 linewidth=0.4, zorder=3)
        axA.barh(yy, r['pmf1'], h, color=GRAY, edgecolor='white',
                 linewidth=0.4, zorder=3)
        axA.barh(yy - h, r['rely'], h,
                 color=(RED if r['rec'] in THUA else GREEN),
                 edgecolor='white', linewidth=0.4, zorder=3)
        if r['rec'] in THUA:
            axA.text(103.0, yy, '*', fontsize=12, va='center', ha='center',
                     color=RED, fontweight='bold', zorder=5)
    from matplotlib.patches import Patch
    axA.set_yticks(y)
    axA.set_yticklabels([r['rec'] for r in ps], fontsize=6.6)
    axA.set_xlim(40, 105)
    axA.set_xticks([40, 60, 80, 100])
    axA.set_xlabel('F1 (%), dung sai $\\pm$50 ms')
    axA.legend(handles=[Patch(facecolor=BLUE, label='Power-MF — 4 đạo trình'),
                        Patch(facecolor=GRAY, label='Power-MF-1ch — 1 đạo trình'),
                        Patch(facecolor=GREEN, label='RelyFetal — 1 đạo trình'),
                        Patch(facecolor=RED, label='* RelyFetal thua trên 9 điểm')],
               fontsize=6.3, frameon=False, loc='upper center',
               bbox_to_anchor=(0.5, -0.10), ncol=2, handlelength=1.3,
               handleheight=0.9, columnspacing=1.0)
    axA.grid(axis='x', lw=0.4, color='#DDDDDD', zorder=0)
    axA.set_title('(A) Từng chủ thể, cùng bộ chấm', fontsize=9.0, pad=6)

    # ---------- (B) hieu so + KTC95 cluster bootstrap, ba phep so sanh x bon tap
    taps = [('tat_ca_22', 'Tất cả 22'), ('adfecgdb_5', 'ADFECGDB (5)'),
            ('b2_7', 'Silesia B2 (7)'), ('b1_10', 'Silesia B1 (10)')]
    keys = [('rely_vs_pmf4', 'Ours $-$ PMF 4 kênh', GREEN),
            ('rely_vs_pmf1', 'Ours $-$ PMF 1 kênh', BLUE),
            ('pmf1_vs_pmf4', 'PMF 1 kênh $-$ PMF 4 kênh', GRAY)]
    lab, pos, i = [], [], 0
    for tk, tn in taps:
        axB.text(-29.0, -i, tn, fontsize=7.6, fontweight='bold',
                 color=BLUE, ha='left', va='center')
        axB.axhline(-i, color='#DDDDDD', lw=0.5, zorder=1)
        i += 1
        for kk, kn, col in keys:
            b = S['so_sanh'][tk][kk]
            lo, hi, mu = b['ci_lo'], b['ci_hi'], b['hieu']
            c = GREEN if lo > 0 else (RED if hi < 0 else '#8A8A8A')
            axB.plot([lo, hi], [-i, -i], lw=1.7, color=c, solid_capstyle='butt', zorder=3)
            axB.plot([mu], [-i], 'o', ms=4.2, color=c, zorder=4)
            axB.text(hi + 0.9, -i, vn(mu), va='center', fontsize=6.6, color=c)
            lab.append(kn); pos.append(-i); i += 1
        i += 0.6
    axB.axvline(0, color='#444444', lw=0.8, ls='--', zorder=2)
    axB.set_yticks(pos)
    axB.set_yticklabels(lab, fontsize=6.5)
    axB.yaxis.set_ticks_position('right')
    axB.spines['left'].set_visible(False)
    axB.spines['right'].set_visible(True)
    axB.spines['right'].set_linewidth(0.7)
    axB.set_xlim(-30.5, 31)
    axB.set_xticks([-20, -10, 0, 10, 20])
    axB.set_xlabel('Hiệu số F1 (điểm) · KTC 95% cluster bootstrap')
    axB.grid(axis='x', lw=0.4, color='#DDDDDD', zorder=0)
    axB.set_title('(B) Hiệu số ghép cặp mức chủ thể', fontsize=9.0, pad=6)

    fig.suptitle('Tách nguồn đa kênh đáng 12,12 điểm F1 — mạng đơn kênh lấy lại 10,85 điểm (89,5%)',
                 fontsize=9.4, y=0.985)
    fig.subplots_adjust(wspace=0.46)
    save(fig, 'fig17_powermf')


# ---------------------------------------------------------------- 18. CinC 2013, 75 ban ghi
def fig_cinc75():
    """Toan bo 75 ban ghi set-a: phan bo F1 va so sanh voi mau 10 ban ghi cu."""
    D = _load_v33()
    V = D['cinc75']['75']
    recs = V['records']
    psd = V['rules']['psd']
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(7.0, 3.2),
                                   gridspec_kw={'width_ratios': [1.15, 1.0]})

    # --- (A) histogram F1 tung ban ghi, m5 vs m22
    f5 = np.array(psd['m5'].get('per_record', []), float) if psd['m5'].get('per_record') else None
    f22 = np.array(psd['m22'].get('per_record', []), float) if psd['m22'].get('per_record') else None
    if f5 is None or f22 is None:
        recs_d = D['cinc75'].get('_per_record_psd')
        f5 = np.array([r[0] for r in recs_d], float)
        f22 = np.array([r[1] for r in recs_d], float)
    bins = np.arange(0, 105, 10)
    axA.hist(f5, bins=bins, color=GRAY, alpha=0.85, label='mô hình 5 ca', zorder=3)
    axA.hist(f22, bins=bins, color=GREEN, alpha=0.62, label='mô hình 22 ca', zorder=4)
    axA.axvline(50, color=RED, ls=':', lw=1.0, zorder=5)
    axA.text(50, axA.get_ylim()[1] * 0.96, ' ngưỡng 50', fontsize=6.8, color=RED, va='top')
    axA.set_xlabel('F1 (%) từng bản ghi, kênh PSD mù nhãn')
    axA.set_ylabel('Số bản ghi')
    axA.legend(fontsize=7.2, frameon=False, loc='upper left')
    axA.grid(axis='y', lw=0.4, color='#DDDDDD', zorder=0)
    axA.set_title('(A) Phân bố trên toàn bộ 75 bản ghi set-a', fontsize=9.0, pad=6)

    # --- (B) mau 10 ban ghi cu vs 75 ban ghi
    lab = ['10 bản ghi\n(mẫu cũ, đã rút)', '75 bản ghi\n(số chính mới)',
           '68 bản ghi\n(loại c.thích sai)']
    m5v = [59.15, 71.21, 72.08]
    m22v = [69.31, 79.40, 80.70]
    x = np.arange(3); w = 0.36
    axB.bar(x - w / 2, m5v, w, color=GRAY, edgecolor='white', linewidth=0.7, zorder=3, label='mô hình 5 ca')
    axB.bar(x + w / 2, m22v, w, color=GREEN, edgecolor='white', linewidth=0.7, zorder=3, label='mô hình 22 ca')
    for i in range(3):
        axB.text(x[i] - w / 2, m5v[i] + 1.0, vn(m5v[i]), ha='center', fontsize=7.0)
        axB.text(x[i] + w / 2, m22v[i] + 1.0, vn(m22v[i]), ha='center', fontsize=7.0, fontweight='bold')
    axB.axvspan(-0.5, 0.5, color='#F3D9D9', alpha=0.55, zorder=0)
    axB.text(0, 14, 'mẫu nhỏ, bị lệch\nhai con số này đã rút', ha='center', fontsize=6.4,
             color=RED, style='italic', linespacing=1.35)
    axB.set_xticks(x); axB.set_xticklabels(lab, fontsize=6.4, linespacing=1.3)
    axB.set_ylim(0, 95); axB.set_yticks([0, 20, 40, 60, 80])
    axB.set_ylabel('Macro F1 (%), kênh PSD mù nhãn')
    axB.legend(fontsize=7.0, frameon=False, loc='upper left')
    axB.grid(axis='y', lw=0.4, color='#DDDDDD', zorder=0)
    axB.set_title('(B) Mẫu 10 bản ghi cũ so với toàn bộ', fontsize=9.0, pad=6)
    fig.suptitle('PhysioNet/CinC 2013 set-a: từ mẫu 10 bản ghi sang toàn bộ 75 bản ghi',
                 fontsize=9.6, y=1.02)
    fig.subplots_adjust(wspace=0.34)
    save(fig, 'fig18_cinc75')


# ------------------------------------------------- 19. mo hinh 5 vs 22, ban sua (CinC 75 ban ghi)
def fig_m22_v2():
    """Nhu fig_m22 nhung cot CinC dung 75 ban ghi (PSD mu nhan), khong dung 90,34 hau kiem."""
    groups = ['PhysioNet\nchuyển dạ (5)', 'Silesia B2\nchuyển dạ mới (7)', 'Silesia B1\nthai kỳ (10)',
              'CinC 2013, 75 bản ghi\nhệ ghi khác']
    m5 = [99.21, 95.87, 93.30, 71.21]
    m22 = [99.40, 96.82, 97.15, 79.40]
    note = ['$n=5$: không đủ lực', '$n=7$: không đủ lực',
            'KTC [+2,1; +10,2]', 'KTC [+5,6; +11,1]']
    solid = [False, False, True, True]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    x = np.arange(4); w = 0.36
    ax.bar(x - w / 2, m5, w, label='mô hình 5 ca', color=GRAY, edgecolor='white', linewidth=0.7, zorder=3)
    ax.bar(x + w / 2, m22, w, label='mô hình 22 ca', color=GREEN, edgecolor='white', linewidth=0.7, zorder=3)
    for i in range(4):
        ax.text(x[i] - w / 2, m5[i] + 0.8, vn(m5[i]), ha='center', fontsize=7.6)
        ax.text(x[i] + w / 2, m22[i] + 0.8, vn(m22[i]), ha='center', fontsize=7.6, fontweight='bold')
        ax.text(x[i], 63.0, note[i], ha='center', fontsize=6.8, style='italic',
                color=GREEN if solid[i] else '#8A8A8A')
    ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=7.8, linespacing=1.35)
    ax.set_ylim(60, 106); ax.set_yticks([60, 70, 80, 90, 100])
    ax.set_ylabel('Macro F1 (%), kênh PSD mù nhãn')
    ax.legend(fontsize=7.8, frameon=False, loc='lower right', ncol=2)
    ax.grid(axis='y', lw=0.4, color='#DDDDDD', zorder=0)
    ax.set_title('Huấn luyện trên 22 sản phụ thay vì 5 — cột CinC dùng toàn bộ 75 bản ghi',
                 fontsize=9.5, pad=8)
    save(fig, 'fig19_m22_v2')


# ------------------------------------------- 20. khao sat dai loc tren CHINH TCN (SO BO)
def fig_band_tcn():
    """Dai loc do lai tren chinh TCN, 22 chu the, tach theo nhom chu the.

    Doc thang pilot_evidence/band_tcn_stats.json (dan xuat tu band_tcn.json).
    THI NGHIEM VAN DANG CHAY: chi ve cac dai da xong. Khong to hong:
    KTC cham so khong, va toan bo hieu ung nam o ba chu the.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    S = json.load(open(os.path.join(root, 'pilot_evidence', 'band_tcn_stats.json'),
                       encoding='utf-8'))
    done = S['dai_da_xong']
    con_lai = [b for b in S['dai_ke_hoach'] if b not in done]
    M, C4 = S['macro_F1']['psd'], S['so_sanh_voi_1_45']['mean4']['10-60']

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(7.2, 3.3),
                                   gridspec_kw={'width_ratios': [1.0, 1.30]})

    # ---- (A) macro F1 tung dai da xong
    bands = sorted(done, key=lambda b: -M[b]['mean'])
    f1 = [M[b]['mean'] for b in bands]
    sd = [M[b]['sd'] for b in bands]
    cols = [GREEN if b == '10-60' else (RED if b == '1-45' else BLUE) for b in bands]
    y = np.arange(len(bands))[::-1]
    axA.barh(y, f1, xerr=sd, height=0.50, color=cols, edgecolor='white', linewidth=0.7,
             error_kw=dict(lw=0.7, capsize=2, ecolor='#555555'), zorder=3)
    for i in range(len(bands)):
        axA.text(f1[i] + sd[i] + 0.8, y[i], vn(f1[i]), va='center', fontsize=8.0,
                 fontweight='bold')
    axA.set_yticks(y); axA.set_yticklabels([b + ' Hz' for b in bands], fontsize=8.4)
    if con_lai:
        axA.text(81, min(y) - 0.85, 'còn %d dải chưa chạy xong: %s'
                 % (len(con_lai), ', '.join(con_lai)), va='center', fontsize=6.8,
                 color='#777777', style='italic')
        axA.set_ylim(min(y) - 1.25, max(y) + 0.55)
    axA.set_xlim(80, 118); axA.set_xticks([80, 90, 100])
    axA.set_xlabel('Macro F1 (%), 22 chủ thể, chọn kênh PSD mù nhãn')
    axA.set_ylim(min(y) - (1.25 if con_lai else 0.55), max(y) + 0.55)
    axA.grid(axis='x', lw=0.4, color='#DDDDDD', zorder=0)
    axA.set_title('(A) Dải lọc đo trên chính TCN', fontsize=9.0, pad=6)

    # ---- (B) hieu so tung chu the, 10-60 tru 1-45
    C = S['so_sanh_voi_1_45']['psd']['10-60']
    dif = C['hieu_tung_chu_the']
    subs = sorted(dif, key=lambda s: dif[s])
    vals = [dif[s] for s in subs]
    THUA = set(C['ba_chu_the_kho'])
    cols = [RED if s in THUA else GRAY for s in subs]
    x = np.arange(len(subs))
    axB.bar(x, vals, 0.66, color=cols, edgecolor='white', linewidth=0.5, zorder=3)
    axB.axhline(0, color='#444444', lw=0.8, zorder=2)
    for i, sname in enumerate(subs):
        if sname in THUA:
            axB.text(i, vals[i] + 0.8, vn(vals[i], 1), ha='center', fontsize=6.2,
                     color=RED, fontweight='bold', rotation=90)
    axB.set_xticks(x); axB.set_xticklabels(subs, fontsize=5.2, rotation=90)
    axB.set_ylabel('Hiệu F1 (điểm): 10–60 Hz $-$ 1–45 Hz', fontsize=8.0)
    axB.set_ylim(-6, 42)
    axB.grid(axis='y', lw=0.4, color='#DDDDDD', zorder=0)
    fig.text(0.5, -0.13, 'Hiệu trung bình +%s điểm, KTC 95%% cluster bootstrap mức chủ thể '
             '[%s; +%s] — khoảng tin cậy chứa số 0, nên hiệu ứng dải lọc\ntrên TCN KHÔNG được xác lập ở '
             'n = 22. Ngoài ba chủ thể tô đỏ, 19 chủ thể còn lại có hiệu trung bình %s điểm, tức bằng không.\n'
             'Nếu BỎ bước chọn kênh và lấy trung bình cả 4 kênh, hiệu số là %s điểm, KTC [%s; +%s] — bằng '
             'không với khoảng hẹp.\n%d chủ thể, %d nếp gấp, 4 epoch, seed 0: kết quả SƠ BỘ.'
             % (vn(C['hieu_TB']), vn(C['KTC95_cluster_bootstrap'][0]).replace('-', '\u2212'),
                vn(C['KTC95_cluster_bootstrap'][1]), vn(C['TB_19_chu_the_con_lai'], 3),
                vn(C4['hieu_TB']).replace('-', '\u2212'),
                vn(C4['KTC95_cluster_bootstrap'][0]).replace('-', '\u2212'),
                vn(C4['KTC95_cluster_bootstrap'][1]),
                S['giao_thuc']['n_chu_the'], S['giao_thuc']['n_fold']),
             fontsize=6.6, color='#333333', ha='center', va='top', linespacing=1.5)
    axB.set_title('(B) Toàn bộ hiệu ứng nằm ở ba chủ thể', fontsize=9.0, pad=6)

    fig.suptitle('KẾT QUẢ SƠ BỘ — dải lọc đo trên chính TCN: hiệu ứng KHÔNG được xác lập ở $n=22$',
                 fontsize=9.3, y=1.03)
    fig.subplots_adjust(wspace=0.30)
    save(fig, 'fig20_band_tcn')


if __name__ == '__main__':
    print('Sinh hinh vao', OUT)
    fig_m22_v2()
    fig_waterfall(); fig_band(); fig_arch(); fig_rf(); fig_bench(); fig_bimodal(); fig_dongop(); fig_arch_v2()
    # fig_m22() -- DA RUT, xem ghi chu tai dinh nghia ham; dung fig_m22_v2() o tren
    fig_powermf(); fig_cinc75(); fig_band_tcn()
    print('XONG')

