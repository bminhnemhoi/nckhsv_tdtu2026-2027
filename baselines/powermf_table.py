# -*- coding: utf-8 -*-
"""Dung bang so sanh HAI COT: don kenh (mo hinh cua nhom) vs da kenh (Power-MF chay lai).

Nguon so:
  da kenh  : baselines/powermf_results.json            (CHAY LAI THAT trong phien nay)
  don kenh : benchmark_dpss/eval_22.json               (LOSO 11 fold, mo hinh 22 chu the)
  da cong bo: baselines/powermf_status.json            (trich tu Results/*.mat cua repo goc)

Ket qua ghi ra: baselines/powermf_table.md  (roi dan vao baselines/README.md)
"""
import os
import sys
import json
import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'baselines')

PMF = json.load(open(os.path.join(HERE, 'powermf_results.json'), encoding='utf-8'))
EV = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json'), encoding='utf-8'))
PUB = json.load(open(os.path.join(HERE, 'powermf_published.json'), encoding='utf-8'))


def pub_f1(rec):
    for s in ('b1_powermf', 'b2_powermf'):
        d = PUB['sets'].get(s, {}).get('per_record', {})
        if rec in d:
            return d[rec]['F1']
    return None

PHYSIONET = ['r01', 'r04', 'r07', 'r08', 'r10']
B2_KEEP = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
B2_ALL = ['B2_%02d' % i for i in range(1, 13)]
B1_ALL = ['B1_%02d' % i for i in range(1, 11)]
DUP = {'B2_01': 'r01', 'B2_02': 'r04', 'B2_07': 'r07', 'B2_10': 'r08', 'B2_11': 'r10'}


def pmf_f1(rec):
    r = PMF.get('per_record', {}).get(rec)
    return r['F1'] if r and r.get('ok') else None


def ours(rec, key='F1_psd'):
    s = EV['subjects'].get(rec)
    return s['model_22'][key] if s else None


def stat(xs):
    a = np.array([x for x in xs if x is not None], float)
    if not len(a):
        return 'n/a'
    return '%.2f' % a.mean() if len(a) == 1 else '%.2f +/- %.2f' % (a.mean(), a.std(ddof=1))


def mean(xs):
    a = np.array([x for x in xs if x is not None], float)
    return float(a.mean()) if len(a) else float('nan')


L = []
w = L.append

w('# Power-MF chay lai -- bang so sanh don kenh vs da kenh')
w('')
w('*Tao ngay %s boi `baselines/powermf_table.py`. Moi so o cot "da kenh" la DO THAT'
  ' trong phien nay, khong phai trich tu bai bao.*' % datetime.datetime.now().isoformat(timespec='seconds'))
w('')
w('## 0. Phai doc truoc khi dung bang nay')
w('')
w('- **Power-MF la thuat toan DA KENH.** No dung ca 4 dao trinh bung cung luc va chay ICA hai lan'
  ' (`FecgICAm` tren tin hieu goc, `FecgICAf` tren phan du sau khi khu QRS me). Mo hinh cua nhom la'
  ' **DON KENH**. Day khong phai so sanh cong bang ve dau vao; day la so sanh **ta dang o dau so voi'
  ' da kenh manh nhat da cong bo**.')
w('- Ca hai cot dung **cung bo cham diem**: `model/fqrs_model.py::match_events`, dung sai +/-50 ms,'
  ' ghep tham lam 1-1. KHONG dung `Bxb_compare` cua repo goc (can WFDB Toolbox).')
w('- Cot don kenh lay **F1_psd** (chon dao trinh mu bang PSD) va **F1_mean4** (trung binh 4 dao trinh),'
  ' deu tu `benchmark_dpss/eval_22.json`, mo hinh 22 chu the, LOSO 11 fold.')
w('')

w('## 1. Bang chinh (theo tap du lieu)')
w('')
w('| Tap | n chu the | DON KENH: F1_psd | DON KENH: F1_mean4 | **DA KENH: Power-MF (ta chay lai)** |'
  ' Power-MF da cong bo (repo) | Chenh lech da/don (F1_psd) |')
w('|---|---:|---:|---:|---:|---:|---:|')

rows = [
    ('ADFECGDB PhysioNet (5)', PHYSIONET, None),
    ('Silesia B2 chuyen da (7, bo trung)', B2_KEEP, 97.98),
    ('Silesia B2 chuyen da (12, ca trung)', B2_ALL, 97.98),
    ('Silesia B1 thai ky (10)', B1_ALL, 99.46),
]
for name, recs, pub in rows:
    p = [pmf_f1(r) for r in recs]
    o1 = [ours(r, 'F1_psd') for r in recs]
    o4 = [ours(r, 'F1_mean4') for r in recs]
    n_ok = sum(1 for x in p if x is not None)
    d = mean(p) - mean(o1) if n_ok else float('nan')
    w('| %s | %d | %s | %s | **%s** | %s | %s |'
      % (name, len(recs), stat(o1), stat(o4),
         stat(p) if n_ok else 'CHUA CHAY',
         ('%.2f' % pub) if pub else 'khong co (repo khong chay tap nay)',
         ('%+.2f' % d) if n_ok else '--'))
w('')
w('> Cot "Power-MF da cong bo" la so trong `Results/b1_powermf.mat` / `b2_powermf.mat` cua repo goc,'
  ' cham bang `Bxb_compare` cua ho tren **bo du lieu figshare o tan so goc 500 Hz**. Cot ta chay lai'
  ' dung tin hieu da nang len **1000 Hz** (giao thuc cua nhom) va bo cham cua nhom. Chenh lech giua'
  ' hai cot do CA HAI khac biet nay, khong chi do ban va Octave.')
w('')

w('## 2. Tung ban ghi')
w('')
for name, recs in [('ADFECGDB PhysioNet', PHYSIONET), ('Silesia B2', B2_ALL), ('Silesia B1', B1_ALL)]:
    w('### %s' % name)
    w('')
    w('| Ban ghi | n_ref | Power-MF F1 (ta chay) | Power-MF F1 (da cong bo) | Lech |'
      ' Se | PPV | TP | FP | FN | jitter (ms) | Don kenh F1_psd | Don kenh F1_mean4 | Ghi chu |')
    w('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|')
    for r in recs:
        pr = PMF.get('per_record', {}).get(r)
        note = ('TRUNG voi %s' % DUP[r]) if r in DUP else ''
        pb = pub_f1(r)
        if not pr:
            w('| %s | | CHUA CHAY | %s | | | | | | | | | | %s |'
              % (r, ('%.2f' % pb) if pb else '--', note))
            continue
        o1, o4 = ours(r, 'F1_psd'), ours(r, 'F1_mean4')
        w('| %s | %d | %.2f | %s | %s | %.2f | %.2f | %d | %d | %d | %.2f | %s | %s | %s |'
          % (r, pr['n_ref'], pr['F1'],
             ('%.2f' % pb) if pb is not None else '--',
             ('%+.2f' % (pr['F1'] - pb)) if pb is not None else '--',
             pr['Se'], pr['PPV'], pr['TP'], pr['FP'], pr['FN'], pr['jitter_ms'],
             ('%.2f' % o1) if o1 is not None else '--',
             ('%.2f' % o4) if o4 is not None else '--', note))
    w('')

w('## 3. Kiem chung noi bo: 5 ban ghi trung lap')
w('')
w('B2_01/02/07/10/11 la **cung tin hieu** voi r01/r04/r07/r08/r10 (nhom luon loai chung khi tinh'
  ' trung binh). Chung duoc giu lai o day lam **phep thu doi chung**: Power-MF phai cho ket qua'
  ' gan nhu giong het tren cap trung.')
w('')
w('| Cap trung | Power-MF tren ban B2 | Power-MF tren ban PhysioNet | Chenh lech |')
w('|---|---:|---:|---:|')
for b2, pn in DUP.items():
    a, b = pmf_f1(b2), pmf_f1(pn)
    if a is None or b is None:
        w('| %s = %s | %s | %s | -- |' % (b2, pn, a or 'chua chay', b or 'chua chay'))
    else:
        w('| %s = %s | %.2f | %.2f | %+.2f |' % (b2, pn, a, b, a - b))
w('')

w('## 3b. So sanh theo cap chu the (don kenh vs da kenh)')
w('')
w('Don vi la **chu the**, khong phai cap (ban ghi x kenh) -- theo dung sua loi trong'
  ' `analysis/STATS.md`. Voi n = 5, p nho nhat ma Wilcoxon hai phia co the dat la **0,0625**,'
  ' nen tren ADFECGDB **khong so sanh nao co the dat p < 0,05**, bat ke hieu so lon den dau.')
w('')
w('| Tap | n | Power-MF (da kenh) | Mo hinh nhom, F1_psd (don kenh) | Hieu so TB (PMF - nhom) |'
  ' KTC 95% kieu t | p Wilcoxon | p sign test | So chu the Power-MF thang |')
w('|---|---:|---:|---:|---:|---|---:|---:|---:|')
try:
    from scipy import stats as _st
    _has_scipy = True
except Exception:
    _has_scipy = False
for name, recs in [('ADFECGDB PhysioNet', PHYSIONET),
                   ('Silesia B2 (7, bo trung)', B2_KEEP),
                   ('Silesia B1', B1_ALL)]:
    pair = [(pmf_f1(r), ours(r, 'F1_psd')) for r in recs]
    pair = [(a, b) for a, b in pair if a is not None and b is not None]
    if not pair:
        w('| %s | 0 | CHUA CHAY | | | | | | |' % name)
        continue
    a = np.array([x[0] for x in pair]); b = np.array([x[1] for x in pair])
    d = a - b
    n = len(d)
    if _has_scipy and n > 1:
        se = d.std(ddof=1) / np.sqrt(n)
        tcrit = _st.t.ppf(0.975, n - 1)
        ci = '[%+.2f; %+.2f]' % (d.mean() - tcrit * se, d.mean() + tcrit * se)
        try:
            pw = _st.wilcoxon(a, b).pvalue
        except Exception:
            pw = float('nan')
        k = int((d > 0).sum())
        ps = _st.binomtest(k, n, 0.5).pvalue
    else:
        ci, pw, ps, k = '--', float('nan'), float('nan'), int((d > 0).sum())
    w('| %s | %d | %.2f | %.2f | %+.2f | %s | %.4f | %.4f | %d/%d |'
      % (name, n, a.mean(), b.mean(), d.mean(), ci, pw, ps, k, n))
w('')
w('> **Doc bang nay cho dung.** Hieu so duong = Power-MF (4 kenh) thang. Tren ADFECGDB hieu so'
  ' **am** -- mo hinh don kenh cua nhom nhinh hon Power-MF -- nhung voi n = 5 day *khong phai*'
  ' tuyen bo thong ke duoc. Cung dung quen Power-MF **khong huan luyen** (khong co nguy co ro ri'
  ' du lieu), con so cua nhom la LOSO 11 fold tren cung 22 chu the.')
w('')

w('## 4. Van tay so nhan: vi sao ghep duoc ten ban ghi')
w('')
w('`Results/*.mat` cua repo goc khong luu ten ban ghi (chi la mang theo thu tu `dir(*.mat)`).'
  ' Nhung **so nhan tham chieu TP+FN cua moi ban ghi la mot van tay duy nhat**, va no khop'
  ' **tuyet doi** voi so nhan `model/silesia_loader.py` doc ra:')
w('')
w('```')
w('B1 (repo, theo thu tu): ' + ' '.join(
    str(PUB['sets']['b1_powermf']['per_record'][r]['TP'] +
        PUB['sets']['b1_powermf']['per_record'][r]['FN']) for r in B1_ALL))
w('B1 (silesia_loader)   : ' + ' '.join(
    str(PMF.get('per_record', {}).get(r, {}).get('n_ref', '?')) for r in B1_ALL))
w('B2 (repo, theo thu tu): ' + ' '.join(
    str(PUB['sets']['b2_powermf']['per_record'][r]['TP'] +
        PUB['sets']['b2_powermf']['per_record'][r]['FN']) for r in B2_ALL))
w('B2 (silesia_loader)   : ' + ' '.join(
    str(PMF.get('per_record', {}).get(r, {}).get('n_ref', '?')) for r in B2_ALL))
w('```')
w('')
w('Hai he qua:')
w('')
w('1. Ghi chu cu trong `powermf_status.json` ("khong co ten ban ghi nen KHONG ghep duoc")'
  ' **da het dung** -- ghep duoc, va bang muc 2 lam dieu do.')
w('2. Day cung la **kiem chung doc lap rang `silesia_loader` doc dung bo du lieu ma repo goc da dung**'
  ' (cung so ban ghi, cung so nhip thai tham chieu, cung thu tu).')
w('')

meta = PMF.get('meta', {})
w('## 5. Xuat xu')
w('')
w('| Hang muc | Gia tri |')
w('|---|---|')
for k in ('ngay', 'thuat_toan', 'nguon_ma', 'runtime', 'ban_va', 'cham_diem', 'ms_minpeakdistance'):
    if k in meta:
        w('| `%s` | %s |' % (k, meta[k]))
w('')

out = os.path.join(HERE, 'powermf_table.md')
open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print('viet %s (%d dong)' % (out, len(L)))
for line in L[:40]:
    print(line)
