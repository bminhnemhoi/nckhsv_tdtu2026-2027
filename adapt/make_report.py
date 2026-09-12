# -*- coding: utf-8 -*-
"""Sinh cac bang markdown cua analysis/THICHNGHI.md tu adapt/adapt_results.json."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'adapt_results.json'), encoding='utf-8'))
M = ('base', 'adabn', 'tent', 'pl', 'notch')
NAME = dict(base='khong thich nghi (moc)', adabn='(a) AdaBN — thong ke BN tren ban ghi dich',
            tent='(c) TENT — entropy luc kiem tra', pl='(b) tu huan luyen nhan gia (transductive)',
            notch='(d) chan dien luoi thich nghi')


def f(x, n=2):
    return ('%.' + str(n) + 'f') % x


print('### Bang 1 — CinC 2013 set-a, 75 ban ghi (75 san phu doc lap), quy tac PSD mu nhan\n')
print('| Phuong phap | F1 TB | Hieu vs moc | KTC95 bootstrap cum | p Wilcoxon | Thang/Thua/Hoa | >=90 | <50 | So ban TUT | Tut lon nhat |')
print('|---|---|---|---|---|---|---|---|---|---|')
for m in M:
    r = R['cinc']['n75']['F1_psd'][m]
    d = '—' if m == 'base' else '%+.2f' % r['mean_diff']
    ci = '—' if m == 'base' else '[%+.2f; %+.2f]' % tuple(r['ci95'])
    p = '—' if m == 'base' else '%.3g' % r['p_wilcoxon']
    wl = '—' if m == 'base' else '%d / %d / %d' % (r['n_win'], r['n_loss'], r['n_tie'])
    dr = '—' if m == 'base' else str(r['n_drop'])
    md = '—' if m == 'base' else f(r['max_drop'])
    print('| %s | %s | %s | %s | %s | %s | %d | %d | %s | %s |'
          % (NAME[m], f(r['mean_new']), d, ci, p, wl, r['ge90'], r['lt50'], dr, md))

print('\n### Bang 2 — cac quy tac chon kenh khac (75 ban ghi)\n')
print('| Phuong phap | PSD (chinh) | kenh 0 co dinh | TB 4 kenh | oracle (chan tren) |')
print('|---|---|---|---|---|')
for m in M:
    row = [R['cinc']['n75'][k][m]['mean_new'] for k in ('F1_psd', 'F1_lead0', 'F1_mean4', 'F1_oracle')]
    print('| %s | %s | %s | %s | %s |' % (NAME[m], f(row[0]), f(row[1]), f(row[2]), f(row[3])))

print('\n### Bang 3 — bien the 68 ban ghi (loai 7 ban chu thich sai, khai bao truoc)\n')
print('| Phuong phap | F1 TB | Hieu vs moc | KTC95 |')
print('|---|---|---|---|')
for m in M:
    r = R['cinc']['n68']['F1_psd'][m]
    d = '—' if m == 'base' else '%+.2f' % r['mean_diff']
    ci = '—' if m == 'base' else '[%+.2f; %+.2f]' % tuple(r['ci95'])
    print('| %s | %s | %s | %s |' % (NAME[m], f(r['mean_new']), d, ci))

print('\n### Bang 4 — chieu nguoc: thich nghi co lam hong hieu nang TRONG MIEN khong?')
print('(22 chu the, checkpoint LOSO cua chinh chu the do, quy tac PSD)\n')
print('| Phuong phap | F1 TB | Hieu vs moc | KTC95 | Thang/Thua | So ban TUT | Tut lon nhat |')
print('|---|---|---|---|---|---|---|')
for m in M:
    r = R['indomain']['F1_psd'][m]
    d = '—' if m == 'base' else '%+.2f' % r['mean_diff']
    ci = '—' if m == 'base' else '[%+.2f; %+.2f]' % tuple(r['ci95'])
    wl = '—' if m == 'base' else '%d / %d' % (r['n_win'], r['n_loss'])
    dr = '—' if m == 'base' else str(r['n_drop'])
    md = '—' if m == 'base' else f(r['max_drop'])
    print('| %s | %s | %s | %s | %s | %s | %s |' % (NAME[m], f(r['mean_new']), d, ci, wl, dr, md))

if 'mo_phong_dich_chuyen' in R:
    m = R['mo_phong_dich_chuyen']
    print('\n### Bang 5 — ap CAC DICH CHUYEN DO DUOC len 22 chu the trong mien\n')
    print('| Dieu kien | F1 TB muc chu the | Mat so voi C0 |')
    print('|---|---|---|')
    lab = {'C0_60s': 'C0 — chi cat con 60 s', 'C1_quant': 'C1 — 60 s + luong tu 10,13 bit',
           'C2_mains': 'C2 — 60 s + dien luoi 60 Hz', 'C3_ca_hai': 'C3 — 60 s + luong tu + dien luoi'}
    c0 = m['mean_F1']['C0_60s']
    for c in m['dieu_kien']:
        print('| %s | %s | %s |' % (lab[c], f(m['mean_F1'][c]),
                                    '—' if c == 'C0_60s' else '%+.2f' % (m['mean_F1'][c] - c0)))
    print('\nMuc CinC that: **%.2f**. Khoang cach con lai sau khi da ap du ba dich chuyen: **%.2f diem**.'
          % (79.40, m['khoang_cach_CinC_con_lai']))

print('\n### Ban ghi TUT diem nhieu nhat (75 ban ghi, quy tac PSD)\n')
for m in ('adabn', 'tent', 'pl', 'notch'):
    w = R['cinc']['n75']['F1_psd'][m].get('records_worse', [])[:5]
    print('- **%s**: %s' % (NAME[m], ', '.join('%s %.2f' % (a, b) for a, b in w) if w else 'khong ban nao tut'))

md = R['cinc']['mains_detected']
print('\nDien luoi do duoc tren CinC (tu pho cua chinh tin hieu dich): 60 Hz **%d/75** ban ghi, '
      '50 Hz **%d/75**, khong do duoc **%d/75**.' % (md['n_with_60'], md['n_with_50'], md['n_none']))
