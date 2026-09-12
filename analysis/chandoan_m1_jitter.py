# -*- coding: utf-8 -*-
"""Do DO CHINH XAC DINH VI tren chinh cac nhip DA BAT DUNG (TP jitter).

Muc dich: tach hai gia thuyet ve nhom (e) "lech thoi diem":
  (H1) mang dinh vi kem -> jitter cua TP phai LON (tien toi 50 ms)
  (H2) mang dinh vi tot, nhung o cac doan xau no bat NHAM mot thu khac gan do
       -> jitter cua TP van NHO, va (e) khong phai loi dinh vi tinh vi.
"""
import os
for _v in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_v] = '1'
import json
import numpy as np

R = os.path.dirname(os.path.abspath(__file__))
HARD8 = ('a27', 'a43', 'a54', 'a57', 'a59', 'a60', 'a68', 'a71')
BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')

ck = json.load(open(os.path.join(R, 'chonkenh_results.json'), encoding='utf-8'))
SEL = ck['chon_kenh_theo_quy_tac']['cinc']
ev = json.load(open(os.path.join(R, '..', 'benchmark_dpss', 'eval_cinc75.json'), encoding='utf-8'))

lines = []


def log(s=''):
    print(s)
    lines.append(s)


rows = []
for rec in ev['records']:
    name = rec['record']
    pl = rec['m22']['per_lead']
    oracle = max(pl, key=lambda k: pl[k]['F1'])
    for rule in ('psd', 'peakprob', 'gate'):
        k = str(SEL[name][rule])
        rows.append(dict(record=name, rule=rule, lead=k, F1=pl[k]['F1'],
                         jitter_ms=pl[k]['jitter_ms'], bias_ms=pl[k].get('bias_ms'),
                         TP=pl[k]['TP'], hard=name in HARD8, bad_ann=name in BAD_ANN))
    rows.append(dict(record=name, rule='oracle', lead=oracle, F1=pl[oracle]['F1'],
                     jitter_ms=pl[oracle]['jitter_ms'], bias_ms=pl[oracle].get('bias_ms'),
                     TP=pl[oracle]['TP'], hard=name in HARD8, bad_ann=name in BAD_ANN))

log('=== DO CHINH XAC DINH VI TREN CAC NHIP DA BAT DUNG (CinC 75, mo hinh 22 ca) ===')
log('    dung sai cham la +/-50 ms. Neu jitter TP << 50 ms thi khau dinh vi KHONG hong.')
log('')
hdr = '%-9s %6s %10s %10s %10s %10s' % ('quy tac', 'n', 'jitter TV', 'jitter TB', 'ph.vi 90', 'max')
log(hdr)
log('-' * len(hdr))
out = {}
for rule in ('psd', 'gate', 'peakprob', 'oracle'):
    v = np.array([r['jitter_ms'] for r in rows if r['rule'] == rule and r['TP'] > 0])
    out[rule] = dict(n=int(v.size), trung_vi=float(np.median(v)), trung_binh=float(v.mean()),
                     phan_vi_90=float(np.percentile(v, 90)), max=float(v.max()))
    log('%-9s %6d %10.2f %10.2f %10.2f %10.2f'
        % (rule, v.size, np.median(v), v.mean(), np.percentile(v, 90), v.max()))

log('')
log('   Tach theo do kho (quy tac peakprob):')
for lab, sel in (('67 ban thuong', lambda r: not r['hard']), ('8 ban gioi han cung', lambda r: r['hard'])):
    v = np.array([r['jitter_ms'] for r in rows if r['rule'] == 'peakprob' and sel(r) and r['TP'] > 0])
    out['peakprob_%s' % lab.split()[0]] = dict(n=int(v.size), trung_vi=float(np.median(v)),
                                               trung_binh=float(v.mean()), max=float(v.max()))
    log('      %-22s n=%2d  jitter trung vi %6.2f ms  trung binh %6.2f  max %6.2f'
        % (lab, v.size, np.median(v), v.mean(), v.max()))

log('')
log('   Tach theo F1 cua chinh ban ghi (quy tac peakprob):')
bins = [(90, 101, 'F1 >= 90'), (50, 90, 'F1 50-90'), (0, 50, 'F1 < 50')]
for lo, hi, lab in bins:
    v = np.array([r['jitter_ms'] for r in rows
                  if r['rule'] == 'peakprob' and lo <= r['F1'] < hi and r['TP'] > 0])
    if v.size:
        out['peakprob_bin_%s' % lab] = dict(n=int(v.size), trung_vi=float(np.median(v)),
                                            trung_binh=float(v.mean()), max=float(v.max()))
        log('      %-12s n=%2d  jitter trung vi %6.2f ms  trung binh %6.2f  max %6.2f'
            % (lab, v.size, np.median(v), v.mean(), v.max()))

# ban ghi co jitter lon nhat
log('')
log('   10 ban ghi jitter lon nhat (peakprob):')
bad = sorted([r for r in rows if r['rule'] == 'peakprob' and r['TP'] > 0],
             key=lambda r: -r['jitter_ms'])[:10]
for r in bad:
    log('      %-4s jitter %6.2f ms  F1 %6.2f  TP %4d  %s'
        % (r['record'], r['jitter_ms'], r['F1'], r['TP'],
           'GIOI HAN CUNG' if r['hard'] else ''))

res = dict(meta=dict(nguon='benchmark_dpss/eval_cinc75.json (m22) + analysis/chonkenh_results.json',
                     mo_ta='jitter cua cac nhip DA bat dung, theo tung quy tac chon kenh',
                     dung_sai_cham_ms=50),
           tong_hop=out, tung_ban_ghi=rows)
json.dump(res, open(os.path.join(R, 'chandoan_m1_jitter.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, default=float)
open(os.path.join(R, 'chandoan_m1_jitter_log.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n-> analysis/chandoan_m1_jitter.json')
