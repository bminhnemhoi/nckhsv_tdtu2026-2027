# -*- coding: utf-8 -*-
"""
Phan loai lai nhom (e) THEO TIEU CHI CHAT, tu analysis/chandoan_events.npz (khong chay lai mang).

Ly do: tieu chi long ban dau ("co mot phat hien chua khop trong 50-150 ms") co MUC NGAU NHIEN rat cao
khi mat do nhip ~2,5/giay: cua so 200 ms chiem ~50% cua mot chu ky RR ~390 ms. Tieu chi chat doi hoi
CAP LANG GIENG GAN NHAT HAI CHIEU (nhan gan phat hien do nhat VA phat hien gan nhan do nhat).
Muc ngau nhien do bang chuoi phat hien bi lam nhieu +-500 ms (giu mat do, pha huy canh chinh tung nhip).

Ghi: analysis/chandoan_strict.json
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EV = np.load(os.path.join(HERE, 'chandoan_events.npz'))
RAW = json.load(open(os.path.join(HERE, 'chandoan_raw.json'), encoding='utf-8'))
TOL = 50.0; LOC = 150.0; MAT = 60.0; DBL = 400.0
KEYS = ('a_bo_nhip_co_tin_hieu', 'b_khong_co_tin_hieu', 'c_me', 'e_lech', 'd1_doi', 'd2_ngau_nhien')
BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')
HARD = ('B1_06', 'B1_07', 'B2_03')


def nn(a, b):
    """voi moi phan tu cua a: (khoang cach toi phan tu gan nhat cua b, chi so do). b phai da sap xep."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    if not len(b): return np.full(len(a), np.inf), np.full(len(a), -1, int)
    j = np.searchsorted(b, a)
    lo = np.clip(j - 1, 0, len(b) - 1); hi = np.clip(j, 0, len(b) - 1)
    dl = np.abs(a - b[lo]); dh = np.abs(a - b[hi])
    take_hi = dh < dl
    idx = np.where(take_hi, hi, lo)
    return np.where(take_hi, dh, dl), idx


def match_assign(det, ref, tol=TOL):
    ref = np.asarray(ref, float); det = np.sort(np.asarray(det, float))
    ref2det = np.full(len(ref), -1, int); det2ref = np.full(len(det), -1, int)
    for i, d in enumerate(det):
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (ref2det < 0))[0]
        if len(ok):
            j = ok[int(np.argmin(dd[ok]))]; ref2det[j] = i; det2ref[i] = j
    return det, ref2det, det2ref


def classify(det, ref, mq, z, tau):
    det, ref2det, det2ref = match_assign(det, ref)
    ref = np.asarray(ref, float); mq = np.sort(np.asarray(mq, float))
    fn = np.where(ref2det < 0)[0]; fp = np.where(det2ref < 0)[0]
    tp_det = np.sort(det[det2ref >= 0])
    d_ref, i_ref = nn(ref, det)          # tu moi nhan -> phat hien gan nhat
    d_det, i_det = nn(det, ref)          # tu moi phat hien -> nhan gan nhat
    dm_ref, _ = nn(ref, mq); dm_det, _ = nn(det, mq)
    dtp_det, _ = nn(det, tp_det)
    cnt = {k: 0 for k in KEYS}
    # --- FN
    for j in fn:
        i = i_ref[j]
        mutual = (i >= 0) and (i_det[i] == j)
        if mutual and TOL < d_ref[j] <= LOC and det2ref[i] < 0:
            cnt['e_lech'] += 1; continue
        if dm_ref[j] <= MAT:
            cnt['c_me'] += 1; continue
        cnt['a_bo_nhip_co_tin_hieu' if z[j] >= tau else 'b_khong_co_tin_hieu'] += 1
    # --- FP
    for i in fp:
        j = i_det[i]
        mutual = (j >= 0) and (i_ref[j] == i)
        if mutual and TOL < d_det[i] <= LOC and ref2det[j] < 0:
            cnt['e_lech'] += 1; continue
        if dm_det[i] <= MAT:
            cnt['c_me'] += 1; continue
        if dtp_det[i] <= DBL:
            cnt['d1_doi'] += 1; continue
        cnt['d2_ngau_nhien'] += 1
    return cnt, int(len(fn) + len(fp)), int(len(fn)), int(len(fp))


def spectrum(items):
    tot = {k: 0 for k in KEYS}; tn = {k: 0.0 for k in KEYS}
    ne = 0; ne_n = 0.0
    for c, n, cn, nn_ in items:
        for k in KEYS:
            tot[k] += c[k]; tn[k] += cn[k]
        ne += n; ne_n += nn_
    return dict(n_err=ne, counts=tot, pct={k: 100.0 * tot[k] / ne if ne else 0 for k in KEYS},
                n_err_null=ne_n, pct_null={k: 100.0 * tn[k] / ne_n if ne_n else 0 for k in KEYS})


def main():
    rng = np.random.default_rng(0)
    res = dict(meta=dict(date=str(datetime.datetime.now()), tol_ms=TOL, loc_ms=LOC,
                         rule='e_lech CHAT: cap lang gieng gan nhat HAI CHIEU, ca hai deu chua khop, lech (50,150] ms',
                         null='chuoi phat hien duoc lam nhieu deu +-500 ms (3 lan), giu nguyen mat do'))
    per = {}
    for scope, tags in (('subjects22', sorted(RAW['subjects22'])), ('cinc', sorted(RAW['cinc']))):
        for tag in tags:
            rec = RAW[scope][tag]
            ref = EV[f'{tag}|ref'].astype(float)
            for l in rec['per_lead']:
                det = EV[f'{tag}|L{l}|det'].astype(float)
                mq = EV[f'{tag}|L{l}|mq'].astype(float) * 4
                z = EV[f'{tag}|L{l}|z'].astype(float); tau = float(EV[f'{tag}|L{l}|tau'])
                c, ne, nfn, nfp = classify(det, ref, mq, z, tau)
                nulls = []
                for _ in range(3):
                    dj = np.sort(det + rng.uniform(-500, 500, size=len(det)))
                    nulls.append(classify(dj, ref, mq, z, tau)[0])
                cn = {k: float(np.mean([x[k] for x in nulls])) for k in KEYS}
                nen = float(np.mean([sum(x.values()) for x in nulls]))
                per[f'{tag}|{l}'] = dict(counts=c, n_err=ne, n_FN=nfn, n_FP=nfp, counts_null=cn, n_err_null=nen)
    res['per_lead'] = per

    def grab(scope, tags, how):
        out = []
        for t in tags:
            rec = RAW[scope][t]
            l = str(rec['psd_lead'] if how == 'psd' else rec['oracle_lead'])
            p = per[f'{t}|{l}']
            out.append((p['counts'], p['n_err'], p['counts_null'], p['n_err_null']))
        return out

    t22 = sorted(RAW['subjects22']); tc = sorted(RAW['cinc'])
    res['pho_loi_chat'] = {
        '22_chu_the_kenh_PSD': spectrum(grab('subjects22', t22, 'psd')),
        '22_chu_the_kenh_oracle': spectrum(grab('subjects22', t22, 'oracle')),
        '22_de19_kenh_PSD': spectrum(grab('subjects22', [t for t in t22 if t not in HARD], 'psd')),
        '22_kho3_kenh_PSD': spectrum(grab('subjects22', list(HARD), 'psd')),
        'CinC75_kenh_PSD': spectrum(grab('cinc', tc, 'psd')),
        'CinC75_kenh_oracle': spectrum(grab('cinc', tc, 'oracle')),
        'CinC68_kenh_PSD': spectrum(grab('cinc', [t for t in tc if t not in BAD_ANN], 'psd')),
    }
    json.dump(res, open(os.path.join(HERE, 'chandoan_strict.json'), 'w', encoding='utf-8'), indent=1, default=float)
    print('PHO LOI voi tieu chi (e) CHAT (cap lang gieng gan nhat hai chieu); dong "ng.nhien" = muc ngau nhien')
    print(f'{"bo du lieu":<26}{"n loi":>7}' + ''.join(f'{k.split("_")[0]:>8}' for k in KEYS))
    for n, s in res['pho_loi_chat'].items():
        print(f'{n:<26}{s["n_err"]:>7}' + ''.join(f'{s["pct"][k]:>7.1f}%' for k in KEYS))
        print(f'{"   ng.nhien":<26}{s["n_err_null"]:>7.0f}' + ''.join(f'{s["pct_null"][k]:>7.1f}%' for k in KEYS))


if __name__ == '__main__':
    main()
