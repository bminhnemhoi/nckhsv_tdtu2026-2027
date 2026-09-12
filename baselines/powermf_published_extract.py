# -*- coding: utf-8 -*-
"""Trich so DA CONG BO tu tools/fecg-benchmarking/Results/*.mat va GHEP voi ten ban ghi.

Phat hien then chot: `Results/*.mat` khong luu ten ban ghi (chi la mang `score` theo thu tu
`dir(*.mat)`), nhung SO NHAN THAM CHIEU cua moi ban ghi (TP+FN) la mot van tay duy nhat va
KHOP CHINH XAC voi so nhan ta doc duoc qua `model/silesia_loader.py`:

  B1: 3120 2804 2565 2774 2770 2889 3114 2911 2866 2592   ->  B1_01..B1_10
  B2:  644  637  716  681  660  684  632  645  674  627  646  657  ->  B2_01..B2_12

Ca 22 ban ghi khop tuyet doi, dung thu tu -> ghep duoc ten. Dieu nay bac bo ghi chu cu trong
powermf_status.json ("khong co ten ban ghi nen KHONG ghep duoc") VA dong thoi xac nhan
silesia_loader doc dung bo du lieu ma repo goc da dung.

Ghi ra: baselines/powermf_published.json  (de tools/ co the bi xoa ma so van con)
"""
import os
import sys
import json
import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
from scipy.io import loadmat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, 'tools', 'fecg-benchmarking', 'Results')
OUT = os.path.join(ROOT, 'baselines', 'powermf_published.json')

NAMES = {'b1': ['B1_%02d' % i for i in range(1, 11)],
         'b2': ['B2_%02d' % i for i in range(1, 13)],
         'challenge': None}   # CinC 2013 set-a: a01..a75 theo thu tu dir


def grab(path):
    d = loadmat(path)['score']
    out = []
    for i in range(d.shape[1]):
        e = d[0, i]

        def g(k):
            v = e[k].ravel()
            return float(v[0]) if v.size else 0.0
        out.append(dict(F1=g('F1') * 100, Se=g('SE') * 100, PPV=g('PPV') * 100,
                        TP=int(g('TP')), FN=int(g('FN')), FP=int(g('FP'))))
    return out


def main():
    if not os.path.isdir(RES):
        raise SystemExit('Khong thay %s -- chay baselines/powermf_setup.py truoc' % RES)
    res = dict(ngay=datetime.datetime.now().isoformat(timespec='seconds'),
               nguon='tools/fecg-benchmarking/Results/*.mat (repo mad-lab-fau, MIT)',
               ghi_chu='SO DA CONG BO cua tac gia, cham bang Bxb_compare cua ho (+/-50 ms). '
                       'KHONG phai so ta chay lai -- xem powermf_results.json cho so ta do.',
               ghep_ten='theo van tay so nhan tham chieu TP+FN, khop tuyet doi 22/22 ban ghi Silesia',
               sets={})
    for ds in ('b1', 'b2', 'challenge'):
        for alg in ('powermf', 'varanini', 'behar', 'sulas'):
            p = os.path.join(RES, '%s_%s.mat' % (ds, alg))
            if not os.path.isfile(p):
                continue
            rows = grab(p)
            names = NAMES[ds] or ['a%02d' % (i + 1) for i in range(len(rows))]
            for n, r in zip(names, rows):
                r['rec'] = n
            f1 = np.array([r['F1'] for r in rows], float)
            res['sets']['%s_%s' % (ds, alg)] = dict(
                n=len(rows), F1_mean=float(f1.mean()),
                F1_sd=float(f1.std(ddof=1)), F1_median=float(np.median(f1)),
                per_record={r['rec']: {k: (round(v, 4) if isinstance(v, float) else v)
                                       for k, v in r.items() if k != 'rec'} for r in rows})
            print('%-22s n=%2d  F1 tb=%.2f' % ('%s_%s' % (ds, alg), len(rows), f1.mean()))
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('viet %s' % OUT)


if __name__ == '__main__':
    main()
