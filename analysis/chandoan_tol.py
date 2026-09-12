# -*- coding: utf-8 -*-
"""
Phep thu quyet dinh cho nhom (e): neu loi that su la LECH THOI DIEM thi noi long dung sai
phai lam F1 tang vot. Tinh F1 o dung sai 50 / 75 / 100 / 150 ms tu analysis/chandoan_events.npz.
CHU Y: +-50 ms la quy uoc CinC 2013 -- cac con so o dung sai khac CHI dung de chan doan,
KHONG duoc bao cao nhu hieu nang.
Ghi: analysis/chandoan_tol.json
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EV = np.load(os.path.join(HERE, 'chandoan_events.npz'))
RAW = json.load(open(os.path.join(HERE, 'chandoan_raw.json'), encoding='utf-8'))
TOLS = (50.0, 75.0, 100.0, 150.0)
HARD = ('B1_06', 'B1_07', 'B2_03')
BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')


def f1(det, ref, tol):
    ref = np.asarray(ref, float); det = np.sort(np.asarray(det, float))
    used = np.zeros(len(ref), bool); tp = 0
    for d in det:
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (~used))[0]
        if len(ok):
            used[ok[int(np.argmin(dd[ok]))]] = True; tp += 1
    se = tp / len(ref) * 100 if len(ref) else 0
    pp = tp / len(det) * 100 if len(det) else 0
    return 2 * se * pp / (se + pp) if se + pp else 0.0


def main():
    out = dict(meta=dict(date=str(datetime.datetime.now()), tols=list(TOLS),
                         warning='chi de chan doan; hieu nang cong bo luon o +-50 ms'), per_record={})
    rows = {}
    for scope in ('subjects22', 'cinc'):
        for tag in sorted(RAW[scope]):
            rec = RAW[scope][tag]
            ref = EV[f'{tag}|ref'].astype(float)
            for how in ('psd', 'oracle'):
                l = str(rec['psd_lead'] if how == 'psd' else rec['oracle_lead'])
                det = EV[f'{tag}|L{l}|det'].astype(float)
                rows[(scope, tag, how)] = [f1(det, ref, t) for t in TOLS]
            out['per_record'][tag] = {h: rows[(scope, tag, h)] for h in ('psd', 'oracle')}

    def agg(scope, tags, how):
        v = np.array([rows[(scope, t, how)] for t in tags])
        return v.mean(0).tolist()

    t22 = sorted(RAW['subjects22']); tc = sorted(RAW['cinc'])
    out['tong_hop'] = {
        '22_chu_the_PSD': agg('subjects22', t22, 'psd'),
        '22_chu_the_oracle': agg('subjects22', t22, 'oracle'),
        '22_de19_PSD': agg('subjects22', [t for t in t22 if t not in HARD], 'psd'),
        '22_kho3_PSD': agg('subjects22', list(HARD), 'psd'),
        'CinC75_PSD': agg('cinc', tc, 'psd'),
        'CinC75_oracle': agg('cinc', tc, 'oracle'),
        'CinC68_PSD': agg('cinc', [t for t in tc if t not in BAD_ANN], 'psd'),
    }
    for t in HARD:
        out['tong_hop'][f'{t}_PSD'] = rows[('subjects22', t, 'psd')]
        out['tong_hop'][f'{t}_oracle'] = rows[('subjects22', t, 'oracle')]
    json.dump(out, open(os.path.join(HERE, 'chandoan_tol.json'), 'w', encoding='utf-8'), indent=1, default=float)
    print(f'{"":<24}' + ''.join(f'{"+-" + str(int(t)) + " ms":>11}' for t in TOLS) + f'{"tang 50->150":>14}')
    for k, v in out['tong_hop'].items():
        print(f'{k:<24}' + ''.join(f'{x:>11.2f}' for x in v) + f'{v[-1] - v[0]:>+14.2f}')


if __name__ == '__main__':
    main()
