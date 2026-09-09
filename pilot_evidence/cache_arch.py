"""
Cache windows + representations for the ARCHITECTURE SEARCH.
5 ADFECGDB records x 4 abdominal leads, hop 20 ms, window 500 ms (crop to 300 ms when needed).
Stores: residual window, raw window, Gaussian heatmap target, binary label, centre, record, lead,
        persistence image (2 x 24 x 24) computed on the central 300 ms of the residual.
"""
import os, sys, time, importlib.util
import numpy as np, mne, wfdb
from ripser import ripser
from persim import PersistenceImager

ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pilot', os.path.join(ROOT, 'pilot.py'))
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

FS = 250
W_LONG = 125          # 500 ms
W_SHORT = 75          # 300 ms
HOP = 5               # 20 ms
TAU_F = 2
OUT = os.path.join(ROOT, 'cache_arch.npz')
RECS = P.RECS

def build():
    t0 = time.time()
    imgr = PersistenceImager(pixel_size=1/24, birth_range=(0, 1), pers_range=(0, 1),
                             kernel_params={'sigma': [[0.012, 0], [0, 0.012]]})
    R, X, Y, HM, C, REC, LEAD, PI = [], [], [], [], [], [], [], []
    half_l, half_s = W_LONG // 2, W_SHORT // 2
    for rec in RECS:
        raw = mne.io.read_raw_edf(os.path.join(P.RAW, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        fq = (wfdb.rdann(os.path.join(P.RAW, rec + '.edf'), 'qrs').sample / 4).round().astype(int)
        for lead in range(1, 5):
            x = P.preprocess(sig[lead])
            mpk = P.detect_mqrs(x)
            r = P.robust_scale(P.template_subtract(x, mpk))
            xs = P.robust_scale(x)
            centers = np.arange(half_l + 2, len(r) - half_l - 2, HOP)
            d = np.abs(centers[:, None] - fq[None, :]).min(1)
            y = (d <= 5).astype(np.float32)                       # +/-20 ms
            hm = np.exp(-(d.astype(np.float32) ** 2) / (2 * (3.75 ** 2))).astype(np.float32)  # sigma 15 ms
            rw = np.stack([r[c - half_l:c - half_l + W_LONG] for c in centers]).astype(np.float32)
            xw = np.stack([xs[c - half_l:c - half_l + W_LONG] for c in centers]).astype(np.float32)
            pis = np.zeros((len(centers), 2, 24, 24), np.float16)
            for i in range(len(centers)):
                w = rw[i, half_l - half_s:half_l - half_s + W_SHORT]
                pc = P.unit_diam(P.takens(w, TAU_F))
                res = ripser(pc, maxdim=1)
                d0 = res['dgms'][0]; d0 = d0[np.isfinite(d0[:, 1])]; d1 = res['dgms'][1]
                if len(d0): pis[i, 0] = np.asarray(imgr.transform(d0), np.float16)
                if len(d1): pis[i, 1] = np.asarray(imgr.transform(d1), np.float16)
            R.append(rw); X.append(xw); Y.append(y); HM.append(hm); PI.append(pis)
            C.append(centers.astype(np.int32))
            REC.append(np.full(len(centers), RECS.index(rec), np.int8))
            LEAD.append(np.full(len(centers), lead, np.int8))
            print(f'{rec} lead{lead}: {len(centers)} win, {int(y.sum())} pos, {time.time()-t0:.0f}s', flush=True)
    np.savez_compressed(OUT,
        r=np.concatenate(R), x=np.concatenate(X), y=np.concatenate(Y), hm=np.concatenate(HM),
        pi=np.concatenate(PI), c=np.concatenate(C), rec=np.concatenate(REC), lead=np.concatenate(LEAD),
        fq={rec: (wfdb.rdann(os.path.join(P.RAW, rec + '.edf'), 'qrs').sample / 4).round().astype(int)
            for rec in RECS}, allow_pickle=True)
    print('saved', OUT, round(os.path.getsize(OUT) / 1e6, 1), 'MB', f'{time.time()-t0:.0f}s')

if __name__ == '__main__':
    build()
