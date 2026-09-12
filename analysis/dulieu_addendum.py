# -*- coding: utf-8 -*-
"""Phu luc M4: (1) vi tri chinh xac cua 15 doan CinC ro ri trong ban ghi ADFECGDB me,
(2) tinh lai duong rui ro-do phu cua CONG TU CHOI tren 60 ban ghi CinC SACH,
(3) tinh lai 'du dia chon kenh' tren tap sach.
Chay: python analysis/dulieu_addendum.py   -> ghi them vao analysis/dulieu_results.json
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
AU = importlib.util.spec_from_file_location('au', os.path.join(HERE, 'dulieu_audit.py'))
A = importlib.util.module_from_spec(AU); AU.loader.exec_module(A)
L = A.L

LEAK = ['a03', 'a04', 'a05', 'a08', 'a12', 'a13', 'a14', 'a15', 'a17', 'a19', 'a20', 'a22', 'a23', 'a24', 'a25']


def offsets():
    res = json.load(open(os.path.join(HERE, 'dulieu_audit.json'), encoding='utf-8'))
    top = res['overlap']['signal_top3_per_cinc']
    cache = {}
    out = {}
    for c in LEAK:
        ncc, ref = top[c][0]
        if ref not in cache:
            cache[ref] = A.sig_100hz(ref)
        Y = cache[ref]
        X = A.cinc_sig(c)
        best = None
        for ci in range(X.shape[0]):
            tpl = X[ci, 1000:4000]
            for cj in range(Y.shape[0]):
                cc = L.sliding_ncc(tpl, Y[cj])
                k = int(np.argmax(np.abs(cc)))
                v = float(abs(cc[k]))
                if best is None or v > best[0]:
                    best = (v, ci, cj, k)
        v, ci, cj, k = best
        t0 = (k - 1000) / 100.0          # giay trong ban ghi goc ung voi mau 0 cua ban CinC
        out[c] = dict(ban_ghi_goc=ref, ncc=round(v, 4), kenh_cinc=int(ci), kenh_goc=int(cj),
                      bat_dau_s=round(t0, 2), ket_thuc_s=round(t0 + 60.0, 2))
        print('   %s <- %s  ch%d->A%d  NCC %.4f  [%.1f s ; %.1f s]' % (c, ref, ci, cj + 1, v, t0, t0 + 60))
    return out


def gate_clean():
    g = json.load(open(os.path.join(HERE, 'gate22_cinc.json'), encoding='utf-8'))
    rows = [r for r in g['bang'] if r['record'] not in LEAK]
    rows_all = g['bang']
    out = {}
    for name, rr in (('75_goc', rows_all), ('60_sach', rows)):
        s = sorted(rr, key=lambda r: -r['score'])
        n = len(s)
        curve = []
        for keep in range(n, 0, -5):
            k = s[:keep]
            f = np.array([r['F1'] for r in k])
            curve.append(dict(n_keep=keep, coverage_pct=round(100.0 * keep / n, 2),
                              F1_mean=round(float(f.mean()), 4), F1_median=round(float(np.median(f)), 4),
                              n_ge90=int((f >= 90).sum()), n_lt50=int((f < 50).sum())))
        out[name] = dict(n=n, F1_mean_100pct=round(float(np.mean([r['F1'] for r in rr])), 4), duong=curve)
    # o do phu ~66,7 %
    for name in out:
        c = min(out[name]['duong'], key=lambda r: abs(r['coverage_pct'] - 66.67))
        out[name]['tai_do_phu_66_7'] = c
    return out


if __name__ == '__main__':
    print('-- vi tri 15 doan ro ri --')
    off = offsets()
    print('-- cong tu choi tren tap sach --')
    gc = gate_clean()
    for k, v in gc.items():
        print('   %s: F1 100%% = %.2f ; tai do phu %.1f%% = %.2f (lt50 %d)'
              % (k, v['F1_mean_100pct'], v['tai_do_phu_66_7']['coverage_pct'],
                 v['tai_do_phu_66_7']['F1_mean'], v['tai_do_phu_66_7']['n_lt50']))
    p = os.path.join(HERE, 'dulieu_results.json')
    res = json.load(open(p, encoding='utf-8'))
    res['chong_lan']['vi_tri_doan_ro_ri'] = off
    res['chong_lan']['cong_tu_choi_tinh_lai'] = gc
    json.dump(res, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    print('-> ' + p)
