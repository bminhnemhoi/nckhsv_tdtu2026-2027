# -*- coding: utf-8 -*-
"""
M3 -- gop cac shard, thong ke muc ban ghi, hinh va bao cao.
Ra: adapt/adapt_results.json, analysis/fig_thichnghi.png
"""
import os, sys, json, glob, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import adapt_common as A

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = A.ROOT
OUT = os.path.join(HERE, 'adapt_results.json')
FIG = os.path.join(ROOT, 'analysis', 'fig_thichnghi.png')
CINC_REF_PSD = 79.40
METHODS = ('adabn', 'tent', 'pl', 'notch')
LABEL = dict(base='khong thich nghi (moc)', adabn='(a) AdaBN thong ke BN',
             tent='(c) TENT entropy luc kiem tra', pl='(b) tu huan luyen nhan gia',
             notch='(d) chan dien luoi thich nghi')


def merge(stage):
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'shard_%s_*.json' % stage))):
        out.update(json.load(open(f, encoding='utf-8')))
    return out


def rule_table(recs, rule='F1_psd'):
    keys = sorted(recs)
    base = np.array([recs[k]['base'][rule] for k in keys], float)
    rows = {}
    for m in METHODS:
        if m not in recs[keys[0]]:
            continue
        v = np.array([recs[k][m][rule] for k in keys], float)
        st = A.paired_stats(v, base)
        st['records_worse'] = sorted(((k, float(recs[k][m][rule] - recs[k]['base'][rule]))
                                      for k in keys if recs[k][m][rule] < recs[k]['base'][rule] - 1e-9),
                                     key=lambda e: e[1])[:10]
        st['diff_vs_published_ref'] = float(v.mean() - CINC_REF_PSD)
        rows[m] = st
    rows['base'] = dict(n=len(keys), mean_new=float(base.mean()), mean_ref=float(base.mean()),
                        mean_diff=0.0, median_diff=0.0, ci95=[0.0, 0.0], p_wilcoxon=1.0,
                        n_win=0, n_loss=0, n_tie=len(keys), n_drop=0, max_drop=0.0,
                        n_drop_gt5=0, n_drop_gt10=0,
                        ge90=int((base >= 90).sum()), lt50=int((base < 50).sum()),
                        diff_vs_published_ref=float(base.mean() - CINC_REF_PSD))
    return rows, keys, base


def main():
    t0 = time.time()
    diag = json.load(open(os.path.join(HERE, 'diag_results.json'), encoding='utf-8'))
    hp = json.load(open(os.path.join(HERE, 'hp_selected.json'), encoding='utf-8'))
    sim = merge('simshift')
    cinc = merge('cinc')
    ind = merge('indomain')
    res = dict(meta=dict(created=time.strftime('%Y-%m-%d %H:%M:%S'),
                         checkpoint_cinc=A.PROD22, checkpoint_indomain='fetalqrs_tcn_22_fold_XX.pt (LOSO)',
                         n_cinc=len(cinc), n_indomain=len(ind),
                         cinc_published_ref_psd=CINC_REF_PSD,
                         quy_tac_nhan='nhan CinC chi dung o buoc cham diem cuoi cung; sieu tham so chon tren m12->B1'),
               dich_chuyen_mien=dict(
                   top=[r for r in diag['shift_ranked'] if not r['unit_dependent']][:12],
                   canh_bao_eff_bits=('eff_bits cua Silesia bi thoi phong do bo nap resample/scale ve float; '
                                      'so sanh phan giai chi hop le giua CinC (10,13 bit) va ADFECGDB (11,49 bit)'),
                   ),
               sieu_tham_so=hp)
    COND = ('C0_60s', 'C1_quant', 'C2_mains', 'C3_ca_hai')
    if sim:
        sm = {c: float(np.mean([np.mean(v[c]) for v in sim.values() if v.get(c)])) for c in COND}
        res['mo_phong_dich_chuyen'] = dict(
            n_chu_the=len(sim), dieu_kien=list(COND), mean_F1=sm,
            hieu_C3_tru_C0=float(sm['C3_ca_hai'] - sm['C0_60s']),
            khoang_cach_CinC_con_lai=float(sm['C3_ca_hai'] - CINC_REF_PSD),
            per_subject={k: {c: float(np.mean(v[c])) for c in COND if v.get(c)} for k, v in sim.items()},
            dien_giai=('ap ca ba dich chuyen do duoc len du lieu trong mien chi lam mat %.2f diem; '
                       'khoang cach thuc te toi CinC van con %.2f diem'
                       % (sm['C0_60s'] - sm['C3_ca_hai'], sm['C3_ca_hai'] - CINC_REF_PSD)))

    # ---------------- CinC, 75 va 68 ban ghi, 4 quy tac kenh
    res['cinc'] = {}
    for name, sub in (('n75', sorted(cinc)),
                      ('n68', [k for k in sorted(cinc) if k not in A.BAD_ANN])):
        d = {k: cinc[k] for k in sub}
        res['cinc'][name] = {}
        for rule in ('F1_psd', 'F1_lead0', 'F1_mean4', 'F1_oracle'):
            rows, keys, base = rule_table(d, rule)
            res['cinc'][name][rule] = rows
        res['cinc'][name]['n'] = len(sub)
    # tan so dien luoi da chan
    hits = {}
    for k, v in cinc.items():
        h = v.get('notch', {}).get('mains_hit', [])
        hits[k] = sorted({f for lead in h for f in lead})
    res['cinc']['mains_detected'] = dict(
        per_record=hits,
        n_with_60=int(sum(1 for v in hits.values() if 60.0 in v)),
        n_with_50=int(sum(1 for v in hits.values() if 50.0 in v)),
        n_none=int(sum(1 for v in hits.values() if not v)))

    # ---------------- trong mien 22 chu the (LOSO)
    rows, keys, base = rule_table(ind, 'F1_psd')
    res['indomain'] = dict(F1_psd=rows, n=len(keys),
                           per_subject={k: {m: ind[k][m]['F1_psd'] for m in ('base',) + METHODS if m in ind[k]}
                                        for k in keys})

    # ---------------- per-record de ve hinh / truy nguoc
    res['per_record_cinc'] = {k: {m: dict(F1_psd=v[m]['F1_psd'], F1_mean4=v[m].get('F1_mean4'),
                                          psd_lead=v[m]['psd_lead'])
                                  for m in ('base',) + METHODS if m in v} for k, v in cinc.items()}

    best = max(METHODS, key=lambda m: res['cinc']['n75']['F1_psd'][m]['mean_new'])
    bst = res['cinc']['n75']['F1_psd'][best]
    res['ket_luan'] = dict(
        phuong_phap_tot_nhat=best,
        F1_tot_nhat=bst['mean_new'], F1_moc=res['cinc']['n75']['F1_psd']['base']['mean_new'],
        co_cai_thien=bool(bst['ci95'][0] > 0 and bst['mean_diff'] > 0))
    json.dump(res, open(OUT, 'w', encoding='utf-8'), indent=1)

    # ---------------- in bang
    print('\n===== CinC 2013 set-a, 75 ban ghi, quy tac PSD mu nhan =====')
    print('%-34s %7s %8s %20s %9s %7s %7s %6s %6s %8s' %
          ('phuong phap', 'F1', 'hieu', 'KTC95 bootstrap', 'p Wilc', 'thang', 'thua', '>=90', '<50', 'tut max'))
    for m in ('base',) + METHODS:
        r = res['cinc']['n75']['F1_psd'][m]
        print('%-34s %7.2f %+8.2f [%+7.2f;%+7.2f] %9.2e %7d %7d %6d %6d %8.2f' %
              (LABEL[m], r['mean_new'], r['mean_diff'], r['ci95'][0], r['ci95'][1],
               r['p_wilcoxon'], r['n_win'], r['n_loss'], r['ge90'], r['lt50'], r['max_drop']))
    print('\n===== trong mien, 22 chu the, LOSO, quy tac PSD =====')
    for m in ('base',) + METHODS:
        r = res['indomain']['F1_psd'][m]
        print('%-34s %7.2f %+8.2f [%+7.2f;%+7.2f] thang %d thua %d tut max %.2f' %
              (LABEL[m], r['mean_new'], r['mean_diff'], r['ci95'][0], r['ci95'][1],
               r['n_win'], r['n_loss'], r['max_drop']))
    print('\ndien luoi do duoc tren CinC: 60 Hz %d/75 | 50 Hz %d/75 | khong %d/75'
          % (res['cinc']['mains_detected']['n_with_60'], res['cinc']['mains_detected']['n_with_50'],
             res['cinc']['mains_detected']['n_none']))
    if 'mo_phong_dich_chuyen' in res:
        m = res['mo_phong_dich_chuyen']
        print('\n===== mo phong dich chuyen tren 22 chu the TRONG MIEN (cua so 60 s) =====')
        for c in m['dieu_kien']:
            print('  %-12s F1 %.2f' % (c, m['mean_F1'][c]))
        print('  ap du ba dich chuyen chi mat %.2f diem; con thieu %.2f diem moi toi muc CinC'
              % (m['mean_F1']['C0_60s'] - m['mean_F1']['C3_ca_hai'], m['khoang_cach_CinC_con_lai']))
    make_fig(res, diag)
    print('-> %s\n-> %s (%.1f phut)' % (OUT, FIG, (time.time() - t0) / 60))


def make_fig(res, diag):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    C = dict(base='#555555', adabn='#4a7fb5', tent='#1b6ca8', pl='#c1442b', notch='#2e8b57')
    NAMES = ['moc', 'AdaBN\n(a)', 'TENT\n(c)', 'nhan gia\n(b)', 'chan dien\nluoi (d)']
    ms = ('base',) + METHODS
    nrow = 3 if res.get('peakprob') else 2
    fig = plt.figure(figsize=(15.2, 4.4 * nrow))
    gs = fig.add_gridspec(nrow, 3, hspace=0.46, wspace=0.30)

    ax = fig.add_subplot(gs[0, 0])
    top = res['dich_chuyen_mien']['top'][:8][::-1]
    y = np.arange(len(top))
    ax.barh(y, [t['cohens_d'] for t in top],
            color=['#c1442b' if t['cohens_d'] > 0 else '#1b6ca8' for t in top])
    ax.set_yticks(y); ax.set_yticklabels([t['feature'] for t in top], fontsize=8)
    ax.axvline(0, color='#333', lw=.8)
    ax.set_xlabel('Cohen d  (CinC - trong mien)', fontsize=9)
    ax.set_title('(A) dich chuyen mien do bang dac trung KHONG NHAN (75 vs 22)\n'
                 'eff_bits DA BI HA CAP: thuoc tinh cua bo nap Silesia, khong phai may ghi',
                 fontsize=9.2, loc='left')
    ax.tick_params(labelsize=8)

    ax = fig.add_subplot(gs[0, 1])
    m = res.get('mo_phong_dich_chuyen')
    if m:
        cond = m['dieu_kien']
        v = [m['mean_F1'][c] for c in cond]
        ax.bar(range(len(cond)), v, color=['#888888', '#6a9fd4', '#4a7fb5', '#1b6ca8'])
        for i, val in enumerate(v):
            ax.text(i, val + .4, '%.1f' % val, ha='center', fontsize=8)
        ax.axhline(CINC_REF_PSD, color='#c1442b', ls='--', lw=1.4)
        ax.text(len(cond) - .45, CINC_REF_PSD + .8, 'CinC that: %.2f' % CINC_REF_PSD,
                color='#c1442b', fontsize=8.5, ha='right')
        ax.set_xticks(range(len(cond)))
        ax.set_xticklabels(['60 s', '+luong tu\n10,1 bit', '+dien luoi\n60 Hz', 'ca ba'], fontsize=8)
        ax.set_ylim(74, 103)
        ax.set_ylabel('F1 trung binh muc chu the', fontsize=9)
        ax.set_title('(B) ap CAC DICH CHUYEN DO DUOC len 22 chu the\ntrong mien: gan nhu khong mat gi',
                     fontsize=10, loc='left')
        ax.tick_params(labelsize=8)

    ax = fig.add_subplot(gs[0, 2])
    v = [res['cinc']['n75']['F1_psd'][k]['mean_new'] for k in ms]
    ax.bar(range(len(ms)), v, color=[C[k] for k in ms])
    for i, k in enumerate(ms):
        r = res['cinc']['n75']['F1_psd'][k]
        ax.text(i, v[i] + .5, '%.2f' % v[i], ha='center', fontsize=8)
        if k != 'base':
            ax.errorbar(i, v[i], yerr=[[max(v[i] - (v[0] + r['ci95'][0]), 0)],
                                       [max((v[0] + r['ci95'][1]) - v[i], 0)]],
                        color='#222222', capsize=3, lw=1.1)
    ax.set_xticks(range(len(ms))); ax.set_xticklabels(NAMES, fontsize=8)
    ax.set_ylim(min(v) - 6, max(v) + 4)
    ax.set_ylabel('F1 trung binh muc ban ghi', fontsize=9)
    ax.set_title('(C) CinC 2013, 75 ban ghi, quy tac PSD mu nhan\n(thanh loi = KTC95 bootstrap cua HIEU SO)',
                 fontsize=10, loc='left')
    ax.tick_params(labelsize=8)

    ax = fig.add_subplot(gs[1, 0])
    vi = [res['indomain']['F1_psd'][k]['mean_new'] for k in ms]
    ax.bar(range(len(ms)), vi, color=[C[k] for k in ms])
    for i in range(len(ms)):
        ax.text(i, vi[i] + .1, '%.2f' % vi[i], ha='center', fontsize=8)
    ax.set_xticks(range(len(ms))); ax.set_xticklabels(NAMES, fontsize=8)
    ax.set_ylim(min(vi) - 3, max(vi) + 1.5)
    ax.set_ylabel('F1 trung binh muc chu the', fontsize=9)
    ax.set_title('(D) trong mien, 22 chu the, LOSO\nthich nghi co lam hong khong?', fontsize=10, loc='left')
    ax.tick_params(labelsize=8)

    per = res['per_record_cinc']; keys = sorted(per)
    for j, k in enumerate(('pl', 'notch')):
        ax = fig.add_subplot(gs[1, 1 + j])
        b = np.array([per[q]['base']['F1_psd'] for q in keys])
        a = np.array([per[q][k]['F1_psd'] for q in keys])
        ax.plot([0, 100], [0, 100], color='#999999', lw=.8, ls='--')
        worse = a < b - 1e-9
        ax.scatter(b[~worse], a[~worse], s=18, color=C[k], alpha=.75,
                   label='khong tut (%d)' % int((~worse).sum()))
        ax.scatter(b[worse], a[worse], s=30, facecolors='none', edgecolors='#c1442b', lw=1.2,
                   label='TUT diem (%d)' % int(worse.sum()))
        r = res['cinc']['n75']['F1_psd'][k]
        ax.set_title('(%s) %s\nhieu %+.2f  KTC95 [%+.2f;%+.2f]  tut max %.1f'
                     % ('EF'[j], LABEL[k], r['mean_diff'], r['ci95'][0], r['ci95'][1], r['max_drop']),
                     fontsize=9.5, loc='left')
        ax.set_xlabel('F1 khong thich nghi', fontsize=9); ax.set_ylabel('F1 sau thich nghi', fontsize=9)
        ax.set_xlim(-3, 103); ax.set_ylim(-3, 103); ax.tick_params(labelsize=8)
        ax.legend(fontsize=7.5, loc='upper left', frameon=False)
    pp = res.get('peakprob')
    if pp:
        ax = fig.add_subplot(gs[2, :])
        ms2 = ('base', 'notch', 'adabn', 'tent', 'pl')
        w = 0.38
        xs = np.arange(len(ms2))
        v1 = [pp['bang']['F1_psd'][k]['mean_new'] for k in ms2]
        v2 = [pp['bang']['F1_peakprob'][k]['mean_new'] for k in ms2]
        ax.bar(xs - w / 2, v1, w, color='#9aa7b4', label='quy tac PSD (moc 79,40)')
        ax.bar(xs + w / 2, v2, w, color='#1b6ca8', label='quy tac peakprob (moc 85,60)')
        for i in range(len(ms2)):
            ax.text(xs[i] - w / 2, v1[i] + .4, '%.2f' % v1[i], ha='center', fontsize=8)
            ax.text(xs[i] + w / 2, v2[i] + .4, '%.2f' % v2[i], ha='center', fontsize=8)
        ax.axhline(pp['moc']['psd'], color='#666666', ls=':', lw=1.1)
        ax.axhline(pp['moc']['peakprob'], color='#c1442b', ls='--', lw=1.3)
        ax.text(len(ms2) - .5, pp['moc']['peakprob'] + .5, 'moc peakprob %.2f' % pp['moc']['peakprob'],
                color='#c1442b', fontsize=8.5, ha='right')
        ax.set_xticks(xs)
        ax.set_xticklabels(['moc', 'chan dien luoi (d)', 'AdaBN (a)', 'TENT (c)', 'nhan gia (b)'], fontsize=8.5)
        ax.set_ylim(min(v1 + v2) - 4, max(v1 + v2) + 4)
        ax.set_ylabel('F1 trung binh muc ban ghi', fontsize=9)
        ax.set_title('(G) sau khi DA SUA CHON KENH (quy tac peakprob cua M5): khong phuong phap thich nghi nao '
                     'vuot duoc moc 85,60 -- muc tang 6,20 diem la cua CHON KENH, khong phai cua thich nghi',
                     fontsize=10, loc='left')
        ax.legend(fontsize=8, frameon=False, loc='lower right')
        ax.tick_params(labelsize=8)
    fig.suptitle('M3 -- thich nghi mien khong nhan tu ADFECGDB+Silesia sang CinC 2013 set-a '
                 '(nhan CinC chi dung o buoc cham diem)', fontsize=11.5, y=0.975)
    fig.savefig(FIG, dpi=160, bbox_inches='tight')


if __name__ == '__main__':
    main()
