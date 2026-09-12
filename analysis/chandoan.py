# -*- coding: utf-8 -*-
"""
NHIEM VU M1 -- PHO LOI VA TRAN NANG LUC.
Phan loai TUNG loi cua mo hinh 22 ca thanh cac nhom (a..e), tinh tran "gop kenh",
va chan doan ba ban ghi kho.  KHONG huan luyen lai gi o day (xem chandoan_capacity.py).

Chay:  python analysis/chandoan.py            (ca 22 chu the + 75 ban ghi CinC)
       python analysis/chandoan.py --only 22
Ket qua: analysis/chandoan_raw.json, analysis/chandoan_cache.npz, analysis/chandoan_log.txt
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, argparse, importlib.util, datetime, gc
import numpy as np, torch, mne, wfdb
from scipy import signal as sg

torch.set_num_threads(int(os.environ.get('FQRS_THREADS', 2)))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
from _paths import adfecgdb_dir, cinc2013_dir


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


M = _load('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py')); CFG = M.CFG
L = _load('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))

CKPT = os.path.join(ROOT, 'model', 'checkpoints')
OUT_JSON = os.path.join(HERE, 'chandoan_raw.json')
OUT_NPZ = os.path.join(HERE, 'chandoan_cache.npz')
EVAL22 = os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json')
TOL_MS = 50; FHR_BAND = (1.8, 3.0); Q = CFG['fs_in'] // CFG['fs']; LEADS = (1, 2, 3, 4)
LOC_MS = 150      # (e) lech thoi diem: co nhip doi tac trong (50,150] ms
MAT_MS = 60       # (c) lien quan nhip me: trong +-60 ms cua dinh me
DBL_MS = 400      # (d1) phat hien doi: FP trong (50,400] ms cua mot TP
HARD = ('B1_06', 'B1_07', 'B2_03')
BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')
KEYS = ('a_bo_nhip_co_tin_hieu', 'b_khong_co_tin_hieu', 'c_me', 'e_lech', 'd1_doi', 'd2_ngau_nhien')


class Tee:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.o = sys.stdout
    def write(self, s): self.o.write(s); self.f.write(s); self.f.flush()
    def flush(self): self.o.flush(); self.f.flush()


def psd_score(x250, fs=250):
    e = np.abs(sg.hilbert(x250 - np.mean(x250))); e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


# ------------------------------------------------------------------ cham diem co luu gan ket
def match_assign(det, ref, fs=1000, tol_ms=TOL_MS):
    """Giong het M.match_events (tham lam 1-1) nhung TRA VE gan ket.
    -> det_sorted, ref2det (chi so det hoac -1), det2ref (chi so ref hoac -1)"""
    tol = tol_ms / 1000 * fs
    ref = np.asarray(ref, float); det = np.sort(np.asarray(det, float))
    ref2det = np.full(len(ref), -1, int); det2ref = np.full(len(det), -1, int)
    for i, d in enumerate(det):
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (ref2det < 0))[0]
        if len(ok):
            j = ok[int(np.argmin(dd[ok]))]; ref2det[j] = i; det2ref[i] = j
    return det, ref2det, det2ref


def prf(n_tp, n_fp, n_fn):
    se = n_tp / (n_tp + n_fn) * 100 if n_tp + n_fn else 0.0
    pp = n_tp / (n_tp + n_fp) * 100 if n_tp + n_fp else 0.0
    return dict(TP=int(n_tp), FP=int(n_fp), FN=int(n_fn), Se=se, PPV=pp,
                F1=2 * se * pp / (se + pp) if se + pp else 0.0)


# ------------------------------------------------------------------ phep thu "co thay tin hieu thai khong"
def visibility(res250, ref250, mqrs250, fs=250, half_ms=30, blk_s=4.0, n_null=3000, seed=0):
    """Voi moi nhan, z = bien do dinh trong +-30 ms chia cho nhieu cuc bo (MAD khoi 4 s).
    Nguong tau = phan vi 95 cua PHAN BO RONG (cung thong ke tai cac vi tri 'an toan': cach moi nhan
    >=120 ms va moi dinh me >=80 ms). 'Nhin thay' = z >= tau -> do DAC HIEU 95% theo dinh nghia.
    Do NHAY cua phep thu duoc bao cao rieng: ti le 'nhin thay' tren cac nhip mo hinh DA BAT (TP).
    """
    n = len(res250); a = np.abs(np.asarray(res250, float)); half = max(1, int(half_ms / 1000 * fs))
    ref250 = np.asarray(ref250, int); mqrs250 = np.asarray(mqrs250, int)
    blk = int(blk_s * fs); nb = max(1, int(np.ceil(n / blk)))
    keep = np.ones(n, bool)
    for p in ref250:
        keep[max(0, p - int(.04 * fs)):p + int(.04 * fs)] = False
    for p in mqrs250:
        keep[max(0, p - int(.06 * fs)):p + int(.06 * fs)] = False
    sig_blk = np.empty(nb)
    for b in range(nb):
        s, t = b * blk, min(n, (b + 1) * blk)
        v = a[s:t][keep[s:t]]
        if len(v) < 50: v = a[s:t]
        sig_blk[b] = 1.4826 * np.median(np.abs(v - np.median(v))) + 1e-12 if len(v) else 1e-12

    def zstat(pos):
        pos = np.asarray(pos, int); out = np.empty(len(pos))
        for i, p in enumerate(pos):
            s, t = max(0, p - half), min(n, p + half + 1)
            out[i] = (a[s:t].max() if t > s else 0.0) / sig_blk[min(nb - 1, max(0, p) // blk)]
        return out

    safe = np.ones(n, bool)
    for p in ref250:
        safe[max(0, p - int(.12 * fs)):p + int(.12 * fs)] = False
    for p in mqrs250:
        safe[max(0, p - int(.08 * fs)):p + int(.08 * fs)] = False
    safe[:half + 1] = False; safe[max(0, n - half - 1):] = False
    idx = np.where(safe)[0]
    rng = np.random.default_rng(seed)
    if len(idx) < 100:
        tau = float('inf'); z_null = np.zeros(0)
    else:
        z_null = zstat(rng.choice(idx, size=min(n_null, len(idx)), replace=False))
        tau = float(np.percentile(z_null, 95))
    z_ref = zstat(ref250) if len(ref250) else np.zeros(0)
    return z_ref, tau, z_null


# ------------------------------------------------------------------ phan loai loi
def _classify(det1000, ref1000, mq1000, z_ref, tau, fs=1000):
    det, ref2det, det2ref = match_assign(det1000, ref1000, fs, TOL_MS)
    ref = np.asarray(ref1000, float)
    fn_idx = np.where(ref2det < 0)[0]; fp_idx = np.where(det2ref < 0)[0]
    tp_ref_idx = np.where(ref2det >= 0)[0]
    tp_det = det[det2ref >= 0]
    d_unmatched = det[det2ref < 0]
    ref_unmatched = ref[ref2det < 0]

    def near(v, arr):
        if not len(arr): return np.inf
        return float(np.min(np.abs(np.asarray(arr, float) - v)))

    cls_fn = []
    for j in fn_idx:
        r = ref[j]
        if TOL_MS < near(r, d_unmatched) <= LOC_MS:
            cls_fn.append('e_lech'); continue
        if near(r, mq1000) <= MAT_MS:
            cls_fn.append('c_me'); continue
        cls_fn.append('a_bo_nhip_co_tin_hieu' if z_ref[j] >= tau else 'b_khong_co_tin_hieu')
    cls_fp = []
    for i in fp_idx:
        d = det[i]
        if TOL_MS < near(d, ref_unmatched) <= LOC_MS:
            cls_fp.append('e_lech'); continue
        if near(d, mq1000) <= MAT_MS:
            cls_fp.append('c_me'); continue
        if near(d, tp_det) <= DBL_MS:
            cls_fp.append('d1_doi'); continue
        cls_fp.append('d2_ngau_nhien')
    return (dict(n_TP=int(len(tp_ref_idx)), n_FN=int(len(fn_idx)), n_FP=int(len(fp_idx)),
                 n_err=int(len(fn_idx) + len(fp_idx)),
                 counts={k: int(cls_fn.count(k) + cls_fp.count(k)) for k in KEYS},
                 counts_FN={k: int(cls_fn.count(k)) for k in KEYS},
                 counts_FP={k: int(cls_fp.count(k)) for k in KEYS}),
            fn_idx, tp_ref_idx)


def taxonomy(det1000, ref1000, mqrs250, res250, fs=1000, n_null=3):
    ref = np.asarray(ref1000, float)
    mq1000 = np.asarray(mqrs250, float) * Q
    z_ref, tau, _ = visibility(res250, np.round(ref / Q).astype(int), mqrs250)
    base, fn_idx, tp_ref_idx = _classify(det1000, ref, mq1000, z_ref, tau, fs)

    def near(v, arr):
        if not len(arr): return np.inf
        return float(np.min(np.abs(np.asarray(arr, float) - v)))

    # MUC NGAU NHIEN: dich vong cac phat hien di mot doan lon -> mat lien he voi nhan,
    # nhung GIU nguyen mat do va cau truc nhip. Cho biet bao nhieu phan cua moi nhom
    # (nhat la c_me va e_lech) chi la trung hop.
    dur = float(max(len(res250) * Q, (ref.max() if len(ref) else 0) + 1))
    nulls = []
    for f in (0.37, 0.53, 0.71)[:n_null]:
        ds = np.sort((np.asarray(det1000, float) + f * dur) % dur)
        nulls.append(_classify(ds, ref, mq1000, z_ref, tau, fs)[0])
    nk = {}
    if nulls:
        for k in KEYS:
            nk[k] = float(np.mean([n['counts'][k] for n in nulls]))
        nk['n_err'] = float(np.mean([n['n_err'] for n in nulls]))
    out = dict(n_ref=int(len(ref)), n_det=int(len(det1000)), tau=float(tau), counts_null=nk)
    out.update(base)
    out.update(dict(
        sens_test_on_TP=float(np.mean(z_ref[tp_ref_idx] >= tau)) if len(tp_ref_idx) else float('nan'),
        z_median_TP=float(np.median(z_ref[tp_ref_idx])) if len(tp_ref_idx) else float('nan'),
        z_median_FN=float(np.median(z_ref[fn_idx])) if len(fn_idx) else float('nan'),
        z_median_all=float(np.median(z_ref)) if len(z_ref) else float('nan'),
        frac_ref_visible=float(np.mean(z_ref >= tau)) if len(z_ref) else float('nan'),
        frac_FN_on_maternal=float(np.mean([near(ref[j], mq1000) <= MAT_MS for j in fn_idx])) if len(fn_idx) else 0.0))
    out.update(prf(base['n_TP'], base['n_FP'], base['n_FN']))
    return out, z_ref, tau


# ------------------------------------------------------------------ gop kenh bang bo phieu
def fuse_vote(dets_by_lead, k, tol_ms=TOL_MS, refr_ms=250):
    pts = sorted([(float(t), l) for l, ts in dets_by_lead.items() for t in np.asarray(ts, float)])
    if not pts: return np.zeros(0)
    clusters = []; cur = [pts[0]]
    for t, l in pts[1:]:
        if t - cur[-1][0] <= tol_ms:
            cur.append((t, l))
        else:
            clusters.append(cur); cur = [(t, l)]
    clusters.append(cur)
    cand = []
    for c in clusters:
        v = len({l for _, l in c})
        if v >= k: cand.append((float(np.median([t for t, _ in c])), v))
    cand.sort()
    out = []
    for t, v in cand:
        if out and t - out[-1][0] < refr_ms:
            if v > out[-1][1]: out[-1] = (t, v)
        else:
            out.append((t, v))
    return np.array([t for t, _ in out])


def fusion_report(dets_by_lead, ref1000, per_lead_F1):
    r = {}
    for k in (1, 2, 3, 4):
        f = fuse_vote(dets_by_lead, k)
        m = M.match_events(f, ref1000, CFG['fs_in'], TOL_MS)
        r[f'vote{k}'] = dict(F1=m['F1'], Se=m['Se'], PPV=m['PPV'], n_det=int(len(f)))
    hit = np.zeros(len(ref1000), bool)
    for l, ts in dets_by_lead.items():
        _, r2d, _ = match_assign(ts, ref1000, CFG['fs_in'], TOL_MS)
        hit |= (r2d >= 0)
    rec = float(hit.mean() * 100) if len(ref1000) else 0.0
    r['union_recall_ceiling'] = rec
    r['union_F1_ceiling'] = 2 * rec * 100 / (rec + 100) if rec else 0.0   # gia dinh PPV=100 -> KHONG dat duoc
    r['best_vote_F1'] = max(r[f'vote{k}']['F1'] for k in (1, 2, 3, 4))
    r['oracle_lead_F1'] = float(max(per_lead_F1))
    r['mean4_F1'] = float(np.mean(per_lead_F1))
    return r


# ------------------------------------------------------------------ nap du lieu
def load_subject(tag):
    g = 'PhysioNet' if tag.startswith('r') else tag[:2]
    if g == 'PhysioNet':
        D = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        fq1000 = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, int)
        chans = {l: sig[l] for l in LEADS}; del raw, sig
    else:
        sig, _, mt = L.load(tag)
        fq1000 = np.asarray(mt['fqrs_all'], int)
        chans = {l: sig[l - 1] for l in LEADS}; del sig
    out = {}
    for l in LEADS:
        x = M.preprocess(chans[l], CFG['fs_in'], CFG)
        r, mpk = M.cancel_maternal(x, CFG)
        out[l] = dict(res=r, x=x, mqrs=mpk, r_s=M.robust_scale(r).astype(np.float32),
                      x_s=M.robust_scale(x).astype(np.float32), psd=psd_score(r))
    del chans
    return out, fq1000, g


def load_cinc(D, rec):
    r_ = wfdb.rdrecord(os.path.join(D, rec)); ann = wfdb.rdann(os.path.join(D, rec), 'fqrs')
    fs0 = r_.fs
    gt = (np.asarray(ann.sample, float) * (1000.0 / fs0)).round().astype(int)
    out = {}
    for lead in range(min(4, r_.p_signal.shape[1])):
        s = np.nan_to_num(r_.p_signal[:, lead])
        if fs0 != 1000: s = sg.resample_poly(s, 1000, int(fs0))
        x = M.preprocess(s, 1000, CFG); r, mpk = M.cancel_maternal(x, CFG)
        out[lead + 1] = dict(res=r, x=x, mqrs=mpk, r_s=M.robust_scale(r).astype(np.float32),
                             x_s=M.robust_scale(x).astype(np.float32), psd=psd_score(r))
    del r_
    return out, gt


def load_net(path):
    b = torch.load(path, map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
    return net, float(b['threshold'])


def analyse_record(prep, ref1000, net, thr, leads, dump=None, tag=''):
    dets = {}; per = {}; probs = {}
    for l in leads:
        p = M.probability_series(net, prep[l]['r_s'], prep[l]['x_s'], CFG)
        d = M.pick_peaks(p, thr, CFG).astype(np.int64) * Q
        dets[l] = d; probs[l] = p
        per[l], z_ref, tau = taxonomy(d, ref1000, prep[l]['mqrs'], prep[l]['res'])
        per[l]['psd'] = prep[l]['psd']
        if dump is not None:
            dump[f'{tag}|L{l}|det'] = d.astype(np.int64)
            dump[f'{tag}|L{l}|mq'] = np.asarray(prep[l]['mqrs'], np.int64)
            dump[f'{tag}|L{l}|z'] = z_ref.astype(np.float32)
            dump[f'{tag}|L{l}|tau'] = np.float32(tau)
    psd_lead = max(leads, key=lambda l: prep[l]['psd'])
    f1s = [per[l]['F1'] for l in leads]
    oracle_lead = leads[int(np.argmax(f1s))]
    fus = fusion_report(dets, ref1000, f1s)
    return dict(per_lead={str(l): per[l] for l in leads}, psd_lead=int(psd_lead), oracle_lead=int(oracle_lead),
                F1_psd=per[psd_lead]['F1'], F1_oracle=float(max(f1s)), F1_mean4=float(np.mean(f1s)),
                fusion=fus, n_ref=int(len(ref1000))), dets, probs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='both', choices=['both', '22', 'cinc'])
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    sys.stdout = Tee(os.path.join(HERE, 'chandoan_log.txt'))
    t0 = time.time()
    print(f'chandoan.py {datetime.datetime.now():%Y-%m-%d %H:%M:%S} torch {torch.__version__} threads {torch.get_num_threads()}')
    snippets = {}; dump = {}
    out = dict(meta=dict(date=str(datetime.datetime.now()), torch=torch.__version__, tol_ms=TOL_MS,
                         loc_ms=LOC_MS, mat_ms=MAT_MS, dbl_ms=DBL_MS,
                         rule='FN: e_lech -> c_me -> (a/b theo phep thu nhin thay). FP: e_lech -> c_me -> d1_doi -> d2_ngau_nhien',
                         cfg={k: (list(v) if isinstance(v, tuple) else v) for k, v in CFG.items()}),
               subjects22={}, cinc={})

    if a.only in ('both', '22'):
        ev = json.load(open(EVAL22, encoding='utf-8'))
        tags = sorted(ev['subjects'], key=lambda t: ev['subjects'][t]['fold'])
        if a.limit: tags = tags[:a.limit]
        print(f'\n=== 22 CHU THE (checkpoint fold giu lai, LOSO) n={len(tags)} ===')
        cur_k = None; net = None; thr = None
        for tag in tags:
            k = ev['subjects'][tag]['fold']
            if k != cur_k:
                del net; gc.collect()
                net, thr = load_net(os.path.join(CKPT, f'fetalqrs_tcn_22_fold_{k:02d}.pt')); cur_k = k
            tt = time.time()
            prep, ref, grp = load_subject(tag)
            r, dets, probs = analyse_record(prep, ref, net, thr, LEADS, dump, tag)
            if tag in HARD:
                for l in LEADS:
                    snippets[f'{tag}_L{l}_res'] = prep[l]['res'].astype(np.float32)
                    snippets[f'{tag}_L{l}_x'] = prep[l]['x'].astype(np.float32)
                    snippets[f'{tag}_L{l}_prob'] = probs[l].astype(np.float32)
                    snippets[f'{tag}_L{l}_det'] = dets[l].astype(np.int64)
                    snippets[f'{tag}_L{l}_mq'] = prep[l]['mqrs'].astype(np.int64)
                snippets[f'{tag}_ref'] = np.asarray(ref, np.int64)
            dump[f'{tag}|ref'] = np.asarray(ref, np.int64)
            r['group'] = grp; r['fold'] = k; r['threshold'] = thr
            r['F1_psd_eval22'] = ev['subjects'][tag]['model_22']['F1_psd']
            out['subjects22'][tag] = r
            c = r['per_lead'][str(r['psd_lead'])]['counts']
            print(f'  {tag:<7} {grp:<9} F1psd {r["F1_psd"]:6.2f} (eval22 {r["F1_psd_eval22"]:6.2f}) orc {r["F1_oracle"]:6.2f} '
                  f'vote2 {r["fusion"]["vote2"]["F1"]:6.2f} | kenh PSD: a{c["a_bo_nhip_co_tin_hieu"]:4d} b{c["b_khong_co_tin_hieu"]:4d} '
                  f'c{c["c_me"]:3d} e{c["e_lech"]:3d} d{c["d1_doi"] + c["d2_ngau_nhien"]:4d}  ({time.time() - tt:.0f}s)', flush=True)
            del prep, dets, probs; gc.collect()

    if a.only in ('both', 'cinc'):
        D = cinc2013_dir()
        net, thr = load_net(os.path.join(CKPT, 'fetalqrs_tcn_22_production.pt'))
        recs = sorted({f[:-4] for f in os.listdir(D) if f.endswith('.dat')})
        if a.limit: recs = recs[:a.limit]
        print(f'\n=== CinC 2013 set-a n={len(recs)} (production_22, zero-shot) thr={thr:.2f} ===')
        for rec in recs:
            tt = time.time()
            prep, ref = load_cinc(D, rec)
            leads = tuple(sorted(prep))
            r, dets, probs = analyse_record(prep, ref, net, thr, leads, dump, rec)
            r['bad_annotation'] = rec in BAD_ANN; r['threshold'] = thr
            dump[f'{rec}|ref'] = np.asarray(ref, np.int64)
            out['cinc'][rec] = r
            c = r['per_lead'][str(r['psd_lead'])]['counts']
            print(f'  {rec} F1psd {r["F1_psd"]:6.2f} orc {r["F1_oracle"]:6.2f} vote2 {r["fusion"]["vote2"]["F1"]:6.2f} '
                  f'| a{c["a_bo_nhip_co_tin_hieu"]:4d} b{c["b_khong_co_tin_hieu"]:4d} c{c["c_me"]:3d} e{c["e_lech"]:3d} '
                  f'd{c["d1_doi"] + c["d2_ngau_nhien"]:4d} ({time.time() - tt:.0f}s)', flush=True)
            del prep, dets, probs; gc.collect()

    out['meta']['minutes'] = (time.time() - t0) / 60
    json.dump(out, open(OUT_JSON, 'w', encoding='utf-8'), indent=1, default=float)
    if snippets: np.savez_compressed(OUT_NPZ, **snippets)
    if dump: np.savez_compressed(os.path.join(HERE, 'chandoan_events.npz'), **dump)
    print(f'\nDONE {out["meta"]["minutes"]:.1f} phut -> {OUT_JSON}')


if __name__ == '__main__':
    main()
