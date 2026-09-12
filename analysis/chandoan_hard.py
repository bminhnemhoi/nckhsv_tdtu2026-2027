# -*- coding: utf-8 -*-
"""
VIEC 4 -- chan doan tung ban ghi kho (B1_06, B1_07, B2_03).
Doc analysis/chandoan_events.npz + analysis/chandoan_cache.npz (do chandoan.py tao ra).
Ghi analysis/chandoan_hard.json, analysis/fig_chandoan_kho.png
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal as sg

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EV = np.load(os.path.join(HERE, 'chandoan_events.npz'))
CA = np.load(os.path.join(HERE, 'chandoan_cache.npz'))
RAW = json.load(open(os.path.join(HERE, 'chandoan_raw.json'), encoding='utf-8'))
HARD = ('B1_06', 'B1_07', 'B2_03')
COL = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']
TOL = 50.0


def nearest_offset(det, ref):
    """voi moi phat hien: (phat hien - nhan gan nhat) ms"""
    ref = np.sort(np.asarray(ref, float)); det = np.sort(np.asarray(det, float))
    if not len(ref) or not len(det): return np.zeros(0)
    j = np.clip(np.searchsorted(ref, det), 1, len(ref) - 1)
    cand = np.stack([det - ref[j - 1], det - ref[j]])
    return cand[np.abs(cand).argmin(0), np.arange(len(det))]


def block_f1(det, ref, dur_ms, blk_s=30.0):
    from importlib.util import spec_from_file_location, module_from_spec
    out = []
    b = blk_s * 1000
    for s in np.arange(0, dur_ms, b):
        d = det[(det >= s) & (det < s + b)]; r = ref[(ref >= s) & (ref < s + b)]
        if len(r) < 5: continue
        used = np.zeros(len(r), bool); tp = 0
        for x in np.sort(d):
            dd = np.abs(r - x); ok = np.where((dd <= TOL) & (~used))[0]
            if len(ok):
                j = ok[int(np.argmin(dd[ok]))]; used[j] = True; tp += 1
        se = tp / len(r) * 100; pp = tp / max(len(d), 1) * 100
        out.append((s / 1000, 2 * se * pp / (se + pp) if se + pp else 0.0))
    return np.array(out)


def main():
    res = dict(meta=dict(date=str(datetime.datetime.now()), tol_ms=TOL))
    fig = plt.figure(figsize=(15, 11), dpi=130)
    gs = fig.add_gridspec(3, 3, hspace=.45, wspace=.22, left=.06, right=.985, top=.92, bottom=.05)
    fig.suptitle('Ba ban ghi kho — tin hieu thai co ton tai khong, va loi nam o dau?',
                 fontsize=14, y=.965, fontweight='bold')

    for i, tag in enumerate(HARD):
        ref = EV[f'{tag}|ref'].astype(float)
        rec = RAW['subjects22'][tag]
        psd_lead = rec['psd_lead']; orc_lead = rec['oracle_lead']
        d = dict(psd_lead=psd_lead, oracle_lead=orc_lead, leads={})

        # --- cot 1: phan bo lech thoi diem tren kenh PSD va kenh tot nhat
        ax = fig.add_subplot(gs[i, 0])
        for l, c in ((psd_lead, COL[0]), (orc_lead, COL[1])):
            off = nearest_offset(EV[f'{tag}|L{l}|det'].astype(float), ref)
            ax.hist(np.clip(off, -200, 200), bins=np.arange(-200, 202, 8), color=c, alpha=.72,
                    label=f'A{l} ({"PSD" if l == psd_lead else "tot nhat"})')
            d['leads'][f'A{l}_offset_iqr'] = [float(np.percentile(off, 25)), float(np.percentile(off, 75))]
            d['leads'][f'A{l}_frac_off_gt_tol'] = float(np.mean(np.abs(off) > TOL))
            d['leads'][f'A{l}_frac_off_50_150'] = float(np.mean((np.abs(off) > TOL) & (np.abs(off) <= 150)))
        for v in (-TOL, TOL):
            ax.axvline(v, color='#52514e', ls='--', lw=1.1)
        ax.set_yscale('log'); ax.set_xlabel('phat hien − nhan gan nhat (ms)', fontsize=8)
        ax.set_ylabel('so phat hien (log)', fontsize=8)
        ax.set_title(f'{tag} — lech thoi diem (vach = ±50 ms)', fontsize=10, loc='left', fontweight='bold')
        ax.legend(fontsize=7.5, frameon=False)
        for s in ('top', 'right'): ax.spines[s].set_visible(False)

        # --- cot 2: F1 theo thoi gian (khoi 30 s) cho ca 4 kenh
        ax = fig.add_subplot(gs[i, 1])
        dur = float(len(CA[f'{tag}_L1_res']) * 4)
        for l in (1, 2, 3, 4):
            bf = block_f1(EV[f'{tag}|L{l}|det'].astype(float), ref, dur)
            if len(bf):
                ax.plot(bf[:, 0] / 60, bf[:, 1], lw=1.8, color=COL[l - 1], label=f'A{l}')
                d['leads'][f'A{l}_blockF1_min'] = float(bf[:, 1].min())
                d['leads'][f'A{l}_blockF1_frac_below80'] = float(np.mean(bf[:, 1] < 80))
        ax.set_ylim(-3, 103); ax.set_xlabel('thoi gian (phut)', fontsize=8); ax.set_ylabel('F1 khoi 30 s', fontsize=8)
        ax.set_title(f'{tag} — loi tap trung o doan nao?', fontsize=10, loc='left', fontweight='bold')
        ax.legend(fontsize=7.5, frameon=False, ncol=4, loc='lower left')
        for s in ('top', 'right'): ax.spines[s].set_visible(False)

        # --- cot 3: phan du 4 kenh trong mot cua so 4 s xau nhat cua kenh PSD
        ax = fig.add_subplot(gs[i, 2])
        bf = block_f1(EV[f'{tag}|L{psd_lead}|det'].astype(float), ref, dur)
        t0 = float(bf[int(np.argmin(bf[:, 1])), 0]) if len(bf) else 0.0
        s0 = int(t0 * 250); s1 = s0 + 1000
        for l in (1, 2, 3, 4):
            r = CA[f'{tag}_L{l}_res'][s0:s1]
            r = r / (np.percentile(np.abs(r), 99) + 1e-9)
            ax.plot(np.arange(len(r)) / 250, r + 3 * (4 - l), lw=.9, color=COL[l - 1])
            ax.text(-.12, 3 * (4 - l), f'A{l}', fontsize=8, color=COL[l - 1], va='center', ha='right',
                    fontweight='bold')
        rr = ref[(ref >= t0 * 1000) & (ref < (t0 + 4) * 1000)] / 1000 - t0
        for x in rr:
            ax.axvline(x, color='#52514e', lw=.7, alpha=.45)
        ax.set_xlim(-.2, 4); ax.set_yticks([])
        ax.set_xlabel('giay (trong cua so 30 s xau nhat cua kenh PSD)', fontsize=8)
        ax.set_title(f'{tag} — phan du sau khu me, 4 kenh (vach doc = nhan)', fontsize=9.5, loc='left',
                     fontweight='bold')
        for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
        d['worst_window_start_s'] = t0
        res[tag] = d
        print(f'{tag}: kenh PSD A{psd_lead}, kenh tot nhat A{orc_lead}, cua so xau nhat bat dau {t0:.0f} s')
        for k, v in d['leads'].items():
            print(f'    {k}: {v}')

    png = os.path.join(HERE, 'fig_chandoan_kho.png')
    fig.savefig(png, bbox_inches='tight', facecolor='#fcfcfb')
    json.dump(res, open(os.path.join(HERE, 'chandoan_hard.json'), 'w', encoding='utf-8'), indent=1, default=float)
    print(f'-> {png}')


if __name__ == '__main__':
    main()
