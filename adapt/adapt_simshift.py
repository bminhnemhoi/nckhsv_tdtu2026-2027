# -*- coding: utf-8 -*-
"""
VIEC 1 (phan thu hai) -- CAC DICH CHUYEN DO DUOC CO GIAI THICH DUOC KHOANG CACH KHONG?

Lay 22 chu the TRONG MIEN (nhan trong mien, hop phap), ap len chung DUNG ba dich chuyen
lon nhat da do o adapt/diag_results.json roi cham lai bang chinh mo hinh LOSO:
    C0  nguyen ban, cat con 60 s                (chi dich chuyen do dai)
    C1  60 s + luong tu hoa ve 10,13 bit huu hieu
    C2  60 s + bom dien luoi 60 Hz den ti so 1,64
    C3  60 s + luong tu + dien luoi (day du)
Neu C3 van gan 97-98 thi cac dich chuyen THONG KE do duoc KHONG giai thich duoc khoang cach
xuong 79,40 tren CinC -- tuc khoang cach la THIEU TIN HIEU THAT, khong phai lech phan bo.

KHONG dung bat ky mau nao cua CinC 2013.
Chay: python adapt/adapt_simshift.py --shard 0/2
Ra:   adapt/shard_simshift_<i>_<n>.json
"""
import os, sys, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import adapt_common as A
from adapt_run import fold_of_subject, _quantize, _inject_mains, SIM

HERE = os.path.dirname(os.path.abspath(__file__))
COND = ('C0_60s', 'C1_quant', 'C2_mains', 'C3_ca_hai')


def build(raw, cond):
    x = np.asarray(raw, float)
    if cond in ('C1_quant', 'C3_ca_hai'):
        x = _quantize(x, SIM['eff_bits'])
    if cond in ('C2_mains', 'C3_ca_hai'):
        x, _ = _inject_mains(x, 1000.0, SIM['mains_hz'], SIM['mains_ratio'])
    y = A.M.preprocess(x, 1000, A.CFG)
    rr, _ = A.M.cancel_maternal(y, A.CFG)
    return dict(r_s=A.M.robust_scale(rr).astype(np.float32),
                x_s=A.M.robust_scale(y).astype(np.float32), psd=A.psd_score(rr))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--shard', default='0/1'); a = ap.parse_args()
    sh, ns = (int(v) for v in a.shard.split('/'))
    fmap = fold_of_subject()
    tags = [t for i, t in enumerate(A.ALL22) if i % ns == sh]
    out = {}
    n = int(SIM['win_s'] * 1000)
    for tag in tags:
        t0 = time.time()
        fold, _ = fmap[tag]
        net, thr = A.load_net('fetalqrs_tcn_22_fold_%s.pt' % fold)
        _lead, gt, meta, raws = A.prep_subject(tag, with_raw=True)
        del _lead
        rows = {c: [] for c in COND}
        for f in (0.10, 0.45, 0.80):
            s0 = int(f * (meta['dur_s'] * 1000 - n))
            if s0 < 0:
                continue
            g = np.asarray(gt, int); g = g[(g >= s0) & (g < s0 + n)] - s0
            if len(g) < 20:
                continue
            for c in COND:
                leads = [build(r[s0:s0 + n], c) for r in raws]
                i = int(np.argmax([l['psd'] for l in leads]))
                rows[c].append(A.score(A.detect(net, thr, leads[i])[0], g)['F1'])
        out[tag] = {c: [float(v) for v in rows[c]] for c in COND}
        print('  simshift %s fold%s %.0fs %s' % (tag, fold, time.time() - t0,
              ' '.join('%s=%.1f' % (c, np.mean(rows[c])) for c in COND if rows[c])), flush=True)
    json.dump(out, open(os.path.join(HERE, 'shard_simshift_%d_%d.json' % (sh, ns)), 'w',
                        encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
