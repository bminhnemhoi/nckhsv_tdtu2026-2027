# -*- coding: utf-8 -*-
"""Thay ham fig_powermf trong make_figs.py bang ban 3 cot (PMF4 / PMF1 / Ours)."""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

MOI = '''def fig_powermf():
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
            axA.text(41.5, yy, '*', fontsize=11, va='center', ha='left',
                     color=RED, fontweight='bold', zorder=5)
    from matplotlib.patches import Patch
    axA.set_yticks(y)
    axA.set_yticklabels([r['rec'] for r in ps], fontsize=6.6)
    axA.set_xlim(40, 101)
    axA.set_xticks([40, 60, 80, 100])
    axA.set_xlabel('F1 (%), dung sai $\\\\pm$50 ms')
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
        for kk, kn, col in keys:
            b = S['so_sanh'][tk][kk]
            lo, hi, mu = b['ci_lo'], b['ci_hi'], b['hieu']
            c = GREEN if lo > 0 else (RED if hi < 0 else '#8A8A8A')
            axB.plot([lo, hi], [-i, -i], lw=1.7, color=c, solid_capstyle='butt', zorder=3)
            axB.plot([mu], [-i], 'o', ms=4.2, color=c, zorder=4)
            axB.text(hi + 0.7, -i, vn(mu), va='center', fontsize=6.6, color=c)
            lab.append(kn); pos.append(-i); i += 1
        axB.text(-27.5, -i + 1.0, tn, fontsize=7.4, fontweight='bold',
                 color=BLUE, ha='left', va='center')
        i += 1
    axB.axvline(0, color='#444444', lw=0.8, ls='--', zorder=2)
    axB.set_yticks(pos)
    axB.set_yticklabels(lab, fontsize=6.5)
    axB.yaxis.set_ticks_position('right')
    axB.spines['left'].set_visible(False)
    axB.spines['right'].set_visible(True)
    axB.spines['right'].set_linewidth(0.7)
    axB.set_xlim(-28, 24)
    axB.set_xticks([-20, -10, 0, 10, 20])
    axB.set_xlabel('Hiệu số F1 (điểm) · KTC 95% cluster bootstrap')
    axB.grid(axis='x', lw=0.4, color='#DDDDDD', zorder=0)
    axB.set_title('(B) Hiệu số ghép cặp mức chủ thể', fontsize=9.0, pad=6)

    fig.suptitle('Tách nguồn đa kênh đáng 12,12 điểm F1 — mạng đơn kênh lấy lại 10,85 điểm (89,5%)',
                 fontsize=9.4, y=0.985)
    fig.subplots_adjust(wspace=0.46)
    save(fig, 'fig17_powermf')
'''

p = 'make_figs.py'
t = io.open(p, encoding='utf-8').read()
i = t.index('def fig_powermf():')
j = t.index('# ---------------------------------------------------------------- 18. CinC 2013')
t = t[:i] + MOI + '\n\n' + t[j:]
io.open(p, 'w', encoding='utf-8').write(t)
print('da thay fig_powermf')
