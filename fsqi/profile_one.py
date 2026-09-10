# -*- coding: utf-8 -*-
"""
profile_one.py -- chan doan thoi gian: lay r01 kenh 3 (ADFECGDB), chay pipeline chuan roi
all_features tren tung doan 4 s, do thoi gian TUNG HAM (topo / sublevel / classical va cac ham con
cua classical). Ghi ket qua vao fsqi/profile.txt, in 5 doan cham nhat va ham gay cham.

Thu tu: (1) sublevel + classical (cac ham con) cho MOI doan truoc, (2) topo (ripser) sau, moi doan
in chan doan dam may (so diem trung, hang, khoang cach nho nhat) TRUOC khi goi ripser -> neu treo,
dong cuoi cua profile.txt cho biet doan nao va dac diem dam may.

Chay:  python fsqi/profile_one.py [rec=r01] [lead=3]
"""
import os, sys, time, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, torch, mne, wfdb
torch.set_num_threads(4)

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
import fsqi
from _paths import adfecgdb_dir
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG = M.CFG
FS = CFG['fs']; SEG = int(4.0 * FS); Q = 1000 // FS

REC = sys.argv[1] if len(sys.argv) > 1 else 'r01'
LEAD = int(sys.argv[2]) if len(sys.argv) > 2 else 3
OUT = os.path.join(HERE, 'profile.txt')


class Tee:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.o = sys.stdout
    def write(self, s): self.o.write(s); self.f.write(s); self.f.flush()
    def flush(self): self.o.flush(); self.f.flush()


def timed(fn, *a, **k):
    t0 = time.perf_counter(); r = fn(*a, **k); return r, (time.perf_counter() - t0) * 1e3


def cloud_diag(x, p):
    """chan doan dam may Takens truoc khi goi ripser"""
    X = fsqi.takens_embed(fsqi.robust_scale(x), p['dim'], p['tau'])
    if len(X) > p['n_points']:
        idx = np.sort(np.random.default_rng(p['seed']).choice(len(X), p['n_points'], replace=False)); X = X[idx]
    nu = len(np.unique(np.round(X, 9), axis=0))
    rank = int(np.linalg.matrix_rank(X - X.mean(0)))
    from scipy.spatial.distance import pdist
    d = pdist(X); dmin = float(d.min()); n_tie = int((d < 1e-9).sum())
    return dict(n=len(X), n_unique=nu, rank=rank, dmin=dmin, n_zero_dist=n_tie,
                iqr=float(np.subtract(*np.percentile(x, [75, 25]))), std=float(np.std(x)))


def main():
    sys.stdout = Tee(OUT)
    print(f'profile_one.py  {REC} kenh {LEAD}  fsqi.DEFAULT={fsqi.DEFAULT}')
    RAW = adfecgdb_dir()
    b = torch.load(os.path.join(ROOT, 'model', 'checkpoints', f'fetalqrs_tcn_fold_{REC}.pt'), map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval(); thr = float(b['threshold'])
    sig = mne.io.read_raw_edf(os.path.join(RAW, REC + '.edf'), preload=True, verbose=False).get_data()[LEAD]
    t0 = time.time()
    x250 = M.preprocess(sig, 1000, CFG); res, _ = M.cancel_maternal(x250, CFG)
    prob = M.probability_series(net, M.robust_scale(res).astype(np.float32), M.robust_scale(x250).astype(np.float32), CFG)
    det250 = M.pick_peaks(prob, thr, CFG)
    print(f'pipeline (preprocess+cancel+TCN+peaks) toan ban ghi: {time.time() - t0:.1f} s, {len(det250)} dinh')
    n_seg = len(res) // SEG
    p = dict(fsqi.DEFAULT)
    rows = []
    # (1) sublevel + classical, tung ham con
    print(f'\n[A] sublevel + classical (ham con) tren {n_seg} doan')
    print(f'{"seg":>4} {"sublev":>8} {"sampen":>8} {"kurt":>7} {"spent":>7} {"band":>7} {"psdfhr":>7} {"tauacf":>7} {"bsqi":>7} {"classic":>8}')
    for k in range(n_seg):
        a, b_ = k * SEG, (k + 1) * SEG; xs = res[a:b_]; raw = sig[a * Q:b_ * Q]
        det_rel = det250[(det250 >= a) & (det250 < b_)] - a
        z = fsqi.robust_scale(xs)
        _, t_sl = timed(fsqi.sublevel_h0_features, xs, p['sl_rel_thr'])
        _, t_se = timed(fsqi.sample_entropy, z, 2, 0.2 * np.std(z))
        _, t_ku = timed(fsqi.stats.kurtosis, z)
        _, t_sp = timed(fsqi.spectral_entropy, z, FS)
        _, t_bd = timed(fsqi.band_energy_ratio, np.asarray(raw, float), 1000)
        _, t_ps = timed(fsqi.psd_fhr_peak, z, FS)
        _, t_ac = timed(fsqi.acf_first_zero, z)
        _, t_bq = timed(lambda: fsqi.agreement_f1(det_rel, fsqi.simple_prominence_detector(z, FS), FS))
        _, t_cl = timed(fsqi.classical_features, xs, FS, det_rel, raw, 1000)
        rows.append(dict(seg=k, sublevel=t_sl, sampen=t_se, kurtosis=t_ku, spec_entropy=t_sp, band_ratio=t_bd,
                         psd_fhr=t_ps, tau_acf=t_ac, bsqi=t_bq, classical=t_cl))
        print(f'{k:4d} {t_sl:8.1f} {t_se:8.1f} {t_ku:7.1f} {t_sp:7.1f} {t_bd:7.1f} {t_ps:7.1f} {t_ac:7.1f} {t_bq:7.1f} {t_cl:8.1f}')
    # (2) topo, chan doan dam may truoc
    print(f'\n[B] topo (Takens + ripser) tren {n_seg} doan -- chan doan dam may TRUOC khi goi ripser')
    for k in range(n_seg):
        a, b_ = k * SEG, (k + 1) * SEG; xs = res[a:b_]
        d = cloud_diag(xs, p)
        print(f'  seg {k:3d}: cloud n={d["n"]} unique={d["n_unique"]} rank={d["rank"]} dmin={d["dmin"]:.2e} '
              f'zero_dist_pairs={d["n_zero_dist"]} iqr={d["iqr"]:.3e} std={d["std"]:.3e} -> ripser ...', end='', flush=True)
        ft, t_tp = timed(fsqi.topo_features, xs, p['dim'], p['tau'], p['n_points'], p['seed'], p['abs_thr'], p['rel_thr'])
        rows[k]['topo'] = t_tp; rows[k]['cloud'] = d
        rows[k]['total'] = t_tp + rows[k]['sublevel'] + rows[k]['classical']
        print(f' {t_tp:8.1f} ms  (h1_count={ft["h1_count"]}, h0_total={ft["h0_total"]:.2f})')
    # (3) tong ket
    print('\n[C] TONG KET (ms/doan)')
    for key in ('topo', 'sublevel', 'classical', 'sampen', 'bsqi', 'psd_fhr', 'spec_entropy', 'band_ratio', 'tau_acf', 'total'):
        t = np.array([r[key] for r in rows])
        print(f'  {key:13s} TB {t.mean():8.1f}  trung vi {np.median(t):8.1f}  p95 {np.percentile(t, 95):8.1f}  max {t.max():9.1f}  tong {t.sum() / 1e3:7.1f} s')
    print('\n5 doan cham nhat (tong = topo + sublevel + classical):')
    for r in sorted(rows, key=lambda r: -r['total'])[:5]:
        sub = {kk: r[kk] for kk in ('topo', 'sublevel', 'classical')}
        worst = max(sub, key=sub.get)
        cl = {kk: r[kk] for kk in ('sampen', 'bsqi', 'psd_fhr', 'spec_entropy', 'band_ratio', 'tau_acf')}
        print(f'  seg {r["seg"]:3d}: tong {r["total"]:9.1f} ms  ham cham nhat = {worst} ({sub[worst]:.1f} ms)  '
              f'[topo {r["topo"]:.1f} / sublevel {r["sublevel"]:.1f} / classical {r["classical"]:.1f}; '
              f'classical con: {max(cl, key=cl.get)} {max(cl.values()):.1f}]  cloud unique={r["cloud"]["n_unique"]} rank={r["cloud"]["rank"]} dmin={r["cloud"]["dmin"]:.1e}')
    over = [r['seg'] for r in rows if r['total'] > 100]
    print(f'\nso doan vuot 100 ms tong: {len(over)}/{n_seg}  {over[:30]}')


if __name__ == '__main__':
    main()
