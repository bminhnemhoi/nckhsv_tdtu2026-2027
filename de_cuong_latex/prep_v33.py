# -*- coding: utf-8 -*-
"""Gom so lieu cho de cuong v3.3: doi chuan Power-MF, CinC 75 ban ghi.

Chi DOC cac JSON da co, khong chay lai mo hinh. Xuat:
  de_cuong_latex/data_v33.json   -- so lieu cho bang + hinh
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

import sys
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'de_cuong_latex')

PMF = json.load(open(os.path.join(ROOT, 'baselines', 'powermf_results.json'), encoding='utf-8'))
EV22 = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json'), encoding='utf-8'))
C75 = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'eval_cinc75.json'), encoding='utf-8'))

PHYSIONET = ['r01', 'r04', 'r07', 'r08', 'r10']
B2_KEEP = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
B1_ALL = ['B1_%02d' % i for i in range(1, 11)]
SUSPECT = ['B1_01', 'B1_02']   # PowerMF Se ~50% + PPV ~99,7 -> nghi loi cong chuyen


def pmf_f1(rec):
    r = PMF['per_record'].get(rec)
    if r and r.get('ok') and r.get('F1') is not None:
        return float(r['F1']), float(r['Se']), float(r['PPV'])
    return None


def ours(rec):
    s = EV22['subjects'].get(rec)
    if not s:
        return None
    m = s['model_22']
    return float(m['F1_psd']), float(m.get('Se_psd', float('nan'))), float(m.get('PPV_psd', float('nan')))


def boot_ci(d, n=10000, seed=0):
    rng = np.random.default_rng(seed)
    d = np.asarray(d, float)
    idx = rng.integers(0, len(d), size=(n, len(d)))
    means = d[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def wilcoxon_exact(d):
    """Wilcoxon signed-rank hai phia, exact, bo cac hieu = 0."""
    from scipy import stats
    d = np.asarray([x for x in d if x != 0.0], float)
    if len(d) == 0:
        return float('nan')
    try:
        return float(stats.wilcoxon(d, alternative='two-sided',
                                    mode='exact' if len(d) <= 25 else 'auto').pvalue)
    except TypeError:
        return float(stats.wilcoxon(d, alternative='two-sided').pvalue)


rows = []
for rec in PHYSIONET + B2_KEEP + B1_ALL:
    p = pmf_f1(rec)
    o = ours(rec)
    grp = 'ADFECGDB' if rec in PHYSIONET else ('Silesia B2' if rec.startswith('B2') else 'Silesia B1')
    rows.append({'rec': rec, 'nhom': grp,
                 'pmf': None if p is None else round(p[0], 2),
                 'pmf_Se': None if p is None else round(p[1], 2),
                 'pmf_PPV': None if p is None else round(p[2], 2),
                 'ours': None if o is None else round(o[0], 2),
                 'nghi_loi': rec in SUSPECT,
                 'pmf_that_bai': p is None})


def block(recs, ten):
    a = [r for r in rows if r['rec'] in recs and r['pmf'] is not None and r['ours'] is not None]
    if not a:
        return None
    p = np.array([r['pmf'] for r in a], float)
    q = np.array([r['ours'] for r in a], float)
    d = q - p                     # duong = RelyFetal hon
    lo, hi = boot_ci(d)
    return {'ten': ten, 'n': len(a),
            'ban_ghi': [r['rec'] for r in a],
            'pmf_mean': round(float(p.mean()), 2), 'pmf_sd': round(float(p.std(ddof=1)), 2) if len(p) > 1 else None,
            'ours_mean': round(float(q.mean()), 2), 'ours_sd': round(float(q.std(ddof=1)), 2) if len(q) > 1 else None,
            'hieu': round(float(d.mean()), 2),
            'ktc95_boot': [round(lo, 2), round(hi, 2)],
            'p_wilcoxon': wilcoxon_exact(d),
            'thang': int((d > 0).sum()), 'thua': int((d < 0).sum()), 'hoa': int((d == 0).sum())}


ALL18 = [r['rec'] for r in rows if r['pmf'] is not None and r['ours'] is not None]
CLEAN16 = [r for r in ALL18 if r not in SUSPECT]
B1_OK = [r for r in ALL18 if r.startswith('B1')]
B1_CLEAN = [r for r in B1_OK if r not in SUSPECT]

blocks = [block(ALL18, 'Tat ca 18 ban ghi chung'),
          block(CLEAN16, 'Loai 2 ban nghi loi cong chuyen (16)'),
          block(PHYSIONET, 'Chi ADFECGDB (5)'),
          block(B2_KEEP, 'Chi Silesia B2 moi (7)'),
          block(B1_CLEAN, 'Chi Silesia B1 sach (4)')]

# --- canh bao bat cach nhip: RR trung binh vs ms_minpeakdistance
ms = float(PMF['meta']['ms_minpeakdistance'])
nhip = {}
for rec in SUSPECT + ['B1_07', 'B1_08', 'B1_09', 'B1_10']:
    r = PMF['per_record'].get(rec)
    if r and r.get('n_ref'):
        dur = r['dur_min'] * 60.0
        bpm = r['n_ref'] / dur * 60.0
        nhip[rec] = {'n_ref': r['n_ref'], 'dur_s': round(dur, 1),
                     'bpm': round(bpm, 1), 'rr_ms': round(60000.0 / bpm, 1),
                     'ms_minpeakdistance': ms,
                     'Se': round(r['Se'], 1), 'PPV': round(r['PPV'], 1)}

out = {
    'ghi_chu': 'Sinh boi de_cuong_latex/prep_v33.py. Nguon: baselines/powermf_results.json (Power-MF chay lai qua Octave), benchmark_dpss/eval_22.json (RelyFetal 22 ca), benchmark_dpss/eval_cinc75.json (CinC 75 ban ghi).',
    'powermf_meta': PMF['meta'],
    'powermf_tomtat': PMF['tom_tat'],
    'powermf_that_bai': [r['rec'] for r in rows if r['pmf_that_bai']],
    'per_record': rows,
    'so_sanh': blocks,
    'nhip_nghi_loi': nhip,
    'cinc75': {'75': C75['variants']['75'], '68': C75['variants']['68'], 'meta': C75['meta'],
               '_per_record_psd': [[round(r['m5']['F1_psd'], 4), round(r['m22']['F1_psd'], 4),
                                    r['record'], bool(r['bad_annotation'])] for r in C75['records']],
               '_per_record_lead0': [[round(r['m5']['F1_lead0'], 4), round(r['m22']['F1_lead0'], 4)]
                                     for r in C75['records']]},
}
# so ban ghi CinC 2013 co dung kenh ma quy tac PSD chon == kenh oracle
out['cinc75']['_psd_eq_oracle_m22'] = sum(
    1 for r in C75['records'] if r['m22']['psd_lead'] == r['m22']['oracle_lead'])
out['cinc75']['_n_leads_dist'] = {}
for r in C75['records']:
    k = str(r['n_leads'])
    out['cinc75']['_n_leads_dist'][k] = out['cinc75']['_n_leads_dist'].get(k, 0) + 1
with open(os.path.join(HERE, 'data_v33.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

for b in blocks:
    if b:
        print('%-42s n=%2d  PMF %6.2f  Rely %6.2f  hieu %+6.2f  KTC[%+.2f;%+.2f]  p=%.4f  %d/%d/%d'
              % (b['ten'], b['n'], b['pmf_mean'], b['ours_mean'], b['hieu'],
                 b['ktc95_boot'][0], b['ktc95_boot'][1], b['p_wilcoxon'], b['thang'], b['thua'], b['hoa']))
print('Power-MF that bai (tra ve rong):', out['powermf_that_bai'])
for k, v in nhip.items():
    print('  %-6s n_ref=%4d  %5.1f bpm  RR=%5.1f ms  (minpeakdistance %.0f ms)  Se=%5.1f PPV=%5.1f'
          % (k, v['n_ref'], v['bpm'], v['rr_ms'], v['ms_minpeakdistance'], v['Se'], v['PPV']))
print('-> de_cuong_latex/data_v33.json')
