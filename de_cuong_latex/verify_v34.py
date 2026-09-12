# -*- coding: utf-8 -*-
"""Đối chiếu từng con số trong PDF với baselines/powermf_fair_stats.json."""
import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
S = json.load(open(os.path.join(ROOT, 'baselines', 'powermf_fair_stats.json'), encoding='utf-8'))
ONE = json.load(open(os.path.join(ROOT, 'baselines', 'powermf_1ch.json'), encoding='utf-8'))
T = io.open(os.path.join(HERE, '_check.txt'), encoding='utf-8', errors='replace').read()

vn = lambda v, n=2: ('%.*f' % (n, v)).replace('.', ',')
ok = bad = 0


def ktra(nhan, chuoi, nguon):
    global ok, bad
    c = T.count(chuoi)
    if c:
        ok += 1
        print('  OK   %-34s %-14s x%-2d  <- %s' % (nhan, chuoi, c, nguon))
    else:
        bad += 1
        print('  SAI  %-34s %-14s KHONG CO TRONG PDF  <- %s' % (nhan, chuoi, nguon))


print('== 1. Trung binh F1 tung tap (per_subject) ==')
import statistics as st
ps = S['per_subject']
for grp, ten in [('ADFECGDB', 'ADFECGDB'), ('B2', 'Silesia B2'), ('B1', 'Silesia B1')]:
    sub = [r for r in ps if r['grp'] == grp]
    for k, kn in [('pmf4', 'PMF4'), ('pmf1', 'PMF1'), ('rely', 'Ours')]:
        v = [r[k] for r in sub]
        ktra('%s %s' % (ten, kn), vn(st.mean(v)), 'per_subject')
for k, kn in [('pmf4', 'PMF4'), ('pmf1', 'PMF1'), ('rely', 'Ours')]:
    v = [r[k] for r in ps]
    ktra('TAT CA 22 %s' % kn, vn(st.mean(v)), 'per_subject')

print('== 2. Thong ke muc chu the (3 so sanh x 4 tap) ==')
for tk in ['tat_ca_22', 'adfecgdb_5', 'b2_7', 'b1_10']:
    for kk in ['rely_vs_pmf4', 'rely_vs_pmf1', 'pmf1_vs_pmf4']:
        b = S['so_sanh'][tk][kk]
        ktra('%s/%s hieu' % (tk, kk), vn(abs(b['hieu'])), 'so_sanh')
        ktra('%s/%s ci_lo' % (tk, kk), vn(abs(b['ci_lo'])), 'so_sanh')
        ktra('%s/%s ci_hi' % (tk, kk), vn(abs(b['ci_hi'])), 'so_sanh')
        ktra('%s/%s T/H/Th' % (tk, kk),
             '%d/%d/%d' % (b['thang'], b['hoa'], b['thua']), 'so_sanh')

print('== 3. Ba ban ghi thua nang + trung vi ==')
for rec in ['B1_07', 'B1_06', 'B2_03', 'B1_10']:
    r = [x for x in ps if x['rec'] == rec][0]
    for k in ['rely', 'pmf4', 'pmf1']:
        ktra('%s %s' % (rec, k), vn(r[k]), 'per_subject')
    ktra('%s hieu' % rec, vn(abs(r['rely'] - r['pmf4'])), 'per_subject')
tv = st.median([r['rely'] - r['pmf4'] for r in ps])
ktra('trung vi hieu so', vn(tv), 'per_subject (median)')

print('== 4. Power-MF-1ch tren CinC 75 ==')
ktra('PMF1ch CinC75', vn(ONE['tom_tat']['cinc75']['F1_mean']), 'powermf_1ch.json')

print('== 5. Luan de 89,5% ==')
h1 = S['so_sanh']['tat_ca_22']['pmf1_vs_pmf4']['hieu']
h2 = S['so_sanh']['tat_ca_22']['rely_vs_pmf1']['hieu']
ti = 100.0 * h2 / abs(h1)
print('  tinh lai: %.2f / %.2f = %.1f %%' % (h2, abs(h1), ti))
ktra('ti so 89,5', vn(ti, 1), 'tinh tu so_sanh')

print('== 6. Kiem chung ngoai ==')
for s in ['99,46', '99,40', '0,06']:
    ktra('kiem chung ngoai', s, 'BASELINES.md / powermf_published.json')

print()
print('TONG: %d dung, %d sai' % (ok, bad))
print('so chuoi "??" trong pdftotext:', T.count('??'))
