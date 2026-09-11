# -*- coding: utf-8 -*-
"""
Huan luyen lai FetalQRS-TCN tren 22 SAN PHU DOC LAP (Phase P3):
    5 PhysioNet ADFECGDB (r01,r04,r07,r08,r10)  -- chuyen da, nhan da dau
   10 Silesia B1_01..B1_10                        -- thai ky 20 phut, nhan GIAN TIEP
    7 Silesia B2 KHONG trung PhysioNet (B2_03,04,05,06,08,09,12) -- chuyen da, nhan da dau
   (B2_01,02,07,10,11 trung r01,r10,r04,r07,r08 -- NCC 0,988-0,994 -- bi loai)

Giao thuc: 11 fold theo NHOM chu the, moi fold giu lai 2 chu the (1 B1 + 1 B2/PhysioNet khi co the), val = 1 chu the
nhan da dau trong phan train, nguong chon tren val. Cung recipe train_final.py: doan 4 s @250 Hz, BCEWithLogits
pos_weight, AdamW 3e-3 + OneCycle, clip 1.0, batch 32, 6 epoch (hoac 4 neu vuot ngan sach 100 phut -- ghi ro).
Tang cuong on-the-fly (augment.py) chi khi train. Doan train lay theo CHI SO tu ban ghi day du (khong nhan ban
bo nho): B1 stride 2 s, B2/PhysioNet stride 1 s. Sau 11 fold: production_22 tren ca 22, nguong = trung vi nguong fold.

Chay:  python model/train_22.py                 (day du, seed 0)
       python model/train_22.py --calibrate     (chi do toc do va uoc luong thoi gian)
       python model/train_22.py --no-augment --folds 1,2,3 --tag noaug   (doi chung khong tang cuong)
Ket qua: model/train_22.json, model/train_22_log.txt, model/checkpoints/fetalqrs_tcn_22_fold_XX.pt, _production.pt
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, math, argparse, importlib.util, random, datetime, platform, gc
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
import mne, wfdb
from scipy import signal as sg

torch.set_num_threads(int(os.environ.get('FQRS_THREADS', 5)))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
from _paths import adfecgdb_dir


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


M = _load('fqrs', os.path.join(HERE, 'fqrs_model.py')); CFG = M.CFG
L = _load('silesia_loader', os.path.join(HERE, 'silesia_loader.py'))
A = _load('augment', os.path.join(HERE, 'augment.py'))

CKPT = os.path.join(HERE, 'checkpoints'); os.makedirs(CKPT, exist_ok=True)
PHYSIONET = ['r01', 'r04', 'r07', 'r08', 'r10']
B1 = [f'B1_{i:02d}' for i in range(1, 11)]
B2 = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
B2_DUPLICATES = {'B2_01': 'r01', 'B2_02': 'r10', 'B2_07': 'r04', 'B2_10': 'r07', 'B2_11': 'r08'}
ALL = PHYSIONET + B1 + B2
LEADS = (1, 2, 3, 4)
SEG = CFG['seg']; Q = CFG['fs_in'] // CFG['fs']
STRIDE = {'PhysioNet': 250, 'B2': 250, 'B1': 500}
TOL_MS = 50; FHR_BAND = (1.8, 3.0)
THR_GRID = np.arange(.20, .80, .05)
BUDGET_MIN = 100.0

_LOG = None
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True)
    if _LOG: _LOG.write(s + '\n'); _LOG.flush()


def group_of(tag):
    return 'PhysioNet' if tag.startswith('r') else tag[:2]


# ------------------------------------------------------------------ du lieu
def load_subject(tag):
    """-> dict lead -> (r250 f32, x250 f32, fq250 int, fq1000 int); nhan B1 = fqrs_all (ke ca co=0, nhu silesia_eval)."""
    g = group_of(tag)
    if g == 'PhysioNet':
        D = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        fq1000 = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, int)
        chans = {lead: sig[lead] for lead in LEADS}
        del raw, sig
    else:
        sig, _, meta = L.load(tag)
        fq1000 = np.asarray(meta['fqrs_all'], int)
        chans = {lead: sig[lead - 1] for lead in LEADS}
        del sig
    out = {}
    fq250 = np.round(fq1000 / Q).astype(int)
    for lead in LEADS:
        x250 = M.preprocess(chans[lead], CFG['fs_in'], CFG)
        res, _ = M.cancel_maternal(x250, CFG)
        # psd: diem PSD Power-MF tren phan du CHUA chuan hoa (nhu blind_lead.py) -> quy tac chon kenh mu nhan;
        # chi giu so vo huong, khong giu mang de tiet kiem RAM
        out[lead] = (M.robust_scale(res).astype(np.float32), M.robust_scale(x250).astype(np.float32),
                     fq250, fq1000, psd_score(res))
    del chans
    return out


def load_all(tags):
    D = {}
    t0 = time.time()
    for tag in tags:
        D[tag] = load_subject(tag)
        n = len(D[tag][1][0])
        log(f'   {tag:<6} {group_of(tag):<9} {n / CFG["fs"] / 60:5.1f} phut  {len(D[tag][1][2]):5d} nhan  '
            f'({time.time() - t0:.0f}s)')
    return D


def make_heatmaps(D, tags):
    return {(tag, lead): M.make_heatmap(len(D[tag][lead][0]), D[tag][lead][2]) for tag in tags for lead in LEADS}


def build_index(D, tags):
    """danh sach (tag, lead, start) cua cac doan train; B1 stride 2 s, con lai 1 s."""
    idx = []
    for tag in tags:
        st = STRIDE[group_of(tag)]
        for lead in LEADS:
            n = len(D[tag][lead][0])
            idx += [(tag, lead, s) for s in range(0, n - SEG, st)]
    return idx


def pos_weight_of(HM, idx):
    """dung nhu train_final: (#Y<0,1)/(#Y>0,5) tren dung cac doan train, tinh bang tong tich luy."""
    cs = {}
    neg = pos = 0
    for tag, lead, s in idx:
        if (tag, lead) not in cs:
            hm = HM[(tag, lead)]
            cs[(tag, lead)] = (np.concatenate([[0], np.cumsum(hm < .1)]), np.concatenate([[0], np.cumsum(hm > .5)]))
        cn, cp = cs[(tag, lead)]
        neg += cn[s + SEG] - cn[s]; pos += cp[s + SEG] - cp[s]
    return float(min(neg / max(pos, 1), 30.0))


def gather(D, HM, idx, sel, rng, augment):
    X = np.empty((len(sel), 2, SEG), np.float32); Y = np.empty((len(sel), SEG), np.float32)
    for k, j in enumerate(sel):
        tag, lead, s = idx[j]
        r, x = D[tag][lead][0], D[tag][lead][1]
        if augment:
            s = int(np.clip(s + A.sample_shift(rng), 0, len(r) - SEG))
        X[k, 0] = r[s:s + SEG]; X[k, 1] = x[s:s + SEG]; Y[k] = HM[(tag, lead)][s:s + SEG]
    if augment:
        X = A.augment_batch(X, rng)
    return torch.from_numpy(X), torch.from_numpy(Y)


# ------------------------------------------------------------------ huan luyen
def train(model, D, HM, idx, epochs, seed, augment, bs=32, lr=3e-3, max_steps=None):
    rng = np.random.default_rng(seed)
    pw = torch.tensor([pos_weight_of(HM, idx)])
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    spe = math.ceil(len(idx) / bs)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, lr, epochs * spe)
    g = torch.Generator().manual_seed(seed)
    hist = []; step = 0; t0 = time.time()
    for ep in range(epochs):
        model.train(); perm = torch.randperm(len(idx), generator=g).tolist(); tot = 0.; nb = 0
        for i in range(0, len(idx), bs):
            X, Y = gather(D, HM, idx, perm[i:i + bs], rng, augment)
            loss = F.binary_cross_entropy_with_logits(model(X), Y, pos_weight=pw)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.); opt.step(); sch.step()
            tot += loss.item(); nb += 1; step += 1
            if max_steps and step >= max_steps:
                return hist, (time.time() - t0) / step
        hist.append(tot / max(1, nb))
        log(f'      epoch {ep + 1}/{epochs} loss {hist[-1]:.4f}  ({time.time() - t0:.0f}s, {len(idx)} doan, pos_w {pw.item():.1f})')
    return hist, (time.time() - t0) / max(step, 1)


# ------------------------------------------------------------------ danh gia
def psd_score(x250, fs=250):
    e = np.abs(sg.hilbert(x250 - np.mean(x250))); e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def signed_bias(det, ref, tol_ms=TOL_MS):
    """trung vi (phat hien - nhan) ms tren cac cap trong +/-tol (nhu silesia_eval.py); am = nhan sau dinh."""
    det = np.sort(np.asarray(det, float)); ref = np.sort(np.asarray(ref, float))
    if not len(det) or not len(ref):
        return float('nan')
    j = np.clip(np.searchsorted(ref, det), 1, len(ref) - 1)
    cand = np.stack([det - ref[j - 1], det - ref[j]])
    s = cand[np.abs(cand).argmin(0), np.arange(len(det))]
    s = s[np.abs(s) <= tol_ms]
    return float(np.median(s)) if len(s) else float('nan')


def probs_subject(model, D, tag):
    return {lead: M.probability_series(model, D[tag][lead][0], D[tag][lead][1], CFG) for lead in LEADS}


def score_lead(prob, fq1000, thr):
    det = M.pick_peaks(prob, thr, CFG).astype(np.int64) * Q
    m = M.match_events(det, fq1000, CFG['fs_in'], TOL_MS)
    m['n_det'] = int(len(det)); m['n_ref'] = int(len(fq1000)); m['bias_ms'] = signed_bias(det, fq1000)
    return m


def pick_threshold(model, D, tag, grid=THR_GRID):
    P = probs_subject(model, D, tag); best, bt = -1, .45
    for t in grid:
        f = float(np.mean([score_lead(P[lead], D[tag][lead][3], float(t))['F1'] for lead in LEADS]))
        if f > best: best, bt = f, float(t)
    return bt, best


def eval_subject_full(model, D, tag, thr):
    P = probs_subject(model, D, tag)
    per = {lead: score_lead(P[lead], D[tag][lead][3], thr) for lead in LEADS}
    bl = max(LEADS, key=lambda l: D[tag][l][4])          # kenh PSD mu nhan (khong dung nhan)
    f1s = [per[l]['F1'] for l in LEADS]
    return dict(record=tag, group=group_of(tag), psd_lead=int(bl), threshold=thr,
                per_lead={f'A{l}': per[l] for l in LEADS},
                F1_psd=per[bl]['F1'], Se_psd=per[bl]['Se'], PPV_psd=per[bl]['PPV'], jitter_psd=per[bl]['jitter_ms'],
                bias_psd=per[bl]['bias_ms'], F1_mean4=float(np.mean(f1s)), F1_oracle=float(max(f1s)),
                bias_mean4=float(np.nanmean([per[l]['bias_ms'] for l in LEADS])))


# ------------------------------------------------------------------ fold
def make_folds(seed=0):
    rng = random.Random(seed)
    b1 = B1[:]; gold = PHYSIONET + B2
    rng.shuffle(b1); rng.shuffle(gold)
    tests = [[b1[i], gold[i]] for i in range(10)] + [[gold[10], gold[11]]]
    folds = []
    for k, test in enumerate(tests):
        gold_train = [g for g in gold if g not in test]
        val = gold_train[k % len(gold_train)]
        train_ = [t for t in ALL if t not in test and t != val]
        folds.append(dict(fold=k + 1, test=test, val=val, train=train_))
    return folds


def main():
    global _LOG
    ap = argparse.ArgumentParser()
    ap.add_argument('--epochs', default='auto', help='6 | 4 | auto (chon theo ngan sach 100 phut sau hieu chuan)')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--no-augment', action='store_true')
    ap.add_argument('--folds', default='', help='vd 1,2,3 ; rong = tat ca 11 + production')
    ap.add_argument('--tag', default='', help='hau to ten file ket qua (doi chung); rong = ket qua chinh')
    ap.add_argument('--calibrate', action='store_true')
    ap.add_argument('--no-production', action='store_true')
    ap.add_argument('--budget', type=float, default=BUDGET_MIN)
    a = ap.parse_args()
    augment = not a.no_augment
    suffix = f'_{a.tag}' if a.tag else ''
    _LOG = open(os.path.join(HERE, f'train_22{suffix}_log.txt'), 'a', encoding='utf-8')
    t_all = time.time()
    log(f'\n===== TRAIN 22 | {datetime.datetime.now():%Y-%m-%d %H:%M:%S} | seed {a.seed} | augment {augment} | '
        f'threads {torch.get_num_threads()} | torch {torch.__version__} | {platform.platform()} =====')
    folds = make_folds(a.seed)
    for f in folds:
        log(f'   fold {f["fold"]:2d}: test {f["test"]}  val {f["val"]}  train n={len(f["train"])}')
    sel = [int(x) for x in a.folds.split(',') if x] if a.folds else list(range(1, 12))
    log('nap 22 chu the ...')
    D = load_all(ALL)
    HM = make_heatmaps(D, ALL)
    rf = M.FetalQRSTCN().receptive_field
    log(f'model: {M.n_params(M.FetalQRSTCN()):,} tham so, truong tiep nhan {rf} mau = {rf * 1000 // CFG["fs"]} ms; '
        f'tang cuong: {A.describe() if augment else "KHONG"}')

    # ---- hieu chuan toc do -> chon epoch
    idx1 = build_index(D, folds[0]['train'])
    torch.manual_seed(a.seed)
    _, t_step = train(M.FetalQRSTCN(), D, HM, idx1, 1, a.seed, augment, max_steps=25)
    torch.manual_seed(a.seed)
    _, t_step = train(M.FetalQRSTCN(), D, HM, idx1, 1, a.seed, augment, max_steps=40)   # lan 2 sau khoi dong
    t0 = time.time(); _ = probs_subject(M.FetalQRSTCN().eval(), D, 'B1_01'); t_eval_b1 = time.time() - t0
    n_steps = {f['fold']: math.ceil(len(build_index(D, f['train'])) / 32) for f in folds}
    n_prod = math.ceil(len(build_index(D, ALL)) / 32)
    # danh gia moi fold: val 1 chu the + test 2 chu the (B1 ~4x dai hon B2) ~ uoc 4 x t_eval_b1 x he so
    t_eval_fold = 4 * t_eval_b1
    proj = {}
    for ep in (6, 4):
        tr = sum(n_steps[k] for k in sel) * ep * t_step + (0 if a.no_production else n_prod * ep * t_step)
        proj[ep] = (tr + t_eval_fold * len(sel)) / 60
    log(f'hieu chuan: {t_step * 1000:.0f} ms/buoc (batch 32), {len(idx1)} doan fold 1 = {n_steps[1]} buoc/epoch; '
        f'production {n_prod} buoc/epoch; eval B1 4 kenh {t_eval_b1:.1f}s')
    log(f'   du kien tong: 6 epoch = {proj[6]:.1f} phut | 4 epoch = {proj[4]:.1f} phut | ngan sach {a.budget:.0f} phut')
    if a.calibrate:
        return
    if a.epochs == 'auto':
        epochs = 6 if proj[6] <= a.budget else 4
        log(f'   -> chon {epochs} epoch' + ('' if epochs == 6 else ' (6 epoch vuot ngan sach -> giam xuong 4, KHONG giam so fold)'))
    else:
        epochs = int(a.epochs); log(f'   -> epoch co dinh {epochs}')
    del idx1

    # ---- 11 fold
    results = dict(meta=dict(date=str(datetime.datetime.now()), seed=a.seed, augment=augment, epochs=epochs,
                             projected_minutes={str(k): v for k, v in proj.items()}, ms_per_step=t_step * 1000,
                             threads=torch.get_num_threads(), torch=torch.__version__, stride=STRIDE,
                             tolerance_ms=TOL_MS, subjects=dict(PhysioNet=PHYSIONET, B1=B1, B2=B2),
                             excluded_duplicates=B2_DUPLICATES, augment_cfg=A.describe() if augment else None,
                             cfg={k: (list(v) if isinstance(v, tuple) else v) for k, v in CFG.items()},
                             label_note='B1: nhan gian tiep (fqrs_all ke ca co=0, nhu silesia_eval); B2/PhysioNet: da dau'),
                   folds={}, subjects={})
    for f in folds:
        if f['fold'] not in sel: continue
        k = f['fold']; tf = time.time()
        log(f'\n-- fold {k:02d}  test={f["test"]}  val={f["val"]}  train={f["train"]} --')
        idx = build_index(D, f['train'])
        torch.manual_seed(a.seed)
        model = M.FetalQRSTCN()
        hist, _ = train(model, D, HM, idx, epochs, a.seed, augment)
        model.eval()
        thr, vf1 = pick_threshold(model, D, f['val'])
        rows = {}
        for tag in f['test']:
            e = eval_subject_full(model, D, tag, thr); e['fold'] = k; e['val'] = f['val']
            rows[tag] = e; results['subjects'][tag] = e
            log(f'   val {f["val"]} F1 {vf1:.2f} @thr {thr:.2f} -> TEST {tag} ({e["group"]}): PSD A{e["psd_lead"]} '
                f'F1 {e["F1_psd"]:.2f} | TB4 {e["F1_mean4"]:.2f} | kenh ' +
                ' '.join(f'{e["per_lead"][f"A{l}"]["F1"]:.2f}' for l in LEADS) +
                f' | lech PSD {e["bias_psd"]:+.1f} ms, TB4 {e["bias_mean4"]:+.1f} ms')
        info = dict(test_subjects=f['test'], val_subject=f['val'], train_subjects=f['train'], threshold=thr,
                    val_F1=vf1, seed=a.seed, augment=augment, epochs=epochs, loss=hist,
                    n_segments=len(idx), minutes=(time.time() - tf) / 60,
                    test=rows)
        results['folds'][f'{k:02d}'] = info
        if not a.tag:
            p = os.path.join(CKPT, f'fetalqrs_tcn_22_fold_{k:02d}.pt')
            torch.save(dict(state_dict=model.state_dict(), config=CFG, threshold=thr, fold=k,
                            test_subjects=f['test'], val_subject=f['val'], train_subjects=f['train'],
                            seed=a.seed, augment=augment, augment_cfg=A.describe() if augment else None,
                            epochs=epochs, stride=STRIDE, loss=hist, val_F1=vf1,
                            metrics={t: dict(F1_psd=r['F1_psd'], F1_mean4=r['F1_mean4'], psd_lead=r['psd_lead'])
                                     for t, r in rows.items()},
                            n_params=M.n_params(model), receptive_field_samples=rf), p)
        log(f'   fold {k:02d} xong {info["minutes"]:.1f} phut; tong {(time.time() - t_all) / 60:.1f} phut')
        del model, idx; gc.collect()
        json.dump(results, open(os.path.join(HERE, f'train_22{suffix}.json'), 'w'), indent=1, default=float)

    # ---- tong hop theo nhom
    summ = {}
    for g in ('PhysioNet', 'B2', 'B1'):
        rows = [e for e in results['subjects'].values() if e['group'] == g]
        if not rows: continue
        for key in ('F1_psd', 'F1_mean4'):
            v = np.array([e[key] for e in rows])
            summ[f'{g}_{key}'] = dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                                      n=int(len(v)), n_ge90=int((v >= 90).sum()), n_lt50=int((v < 50).sum()))
        summ[f'{g}_bias_psd_median'] = float(np.nanmedian([e['bias_psd'] for e in rows]))
        summ[f'{g}_bias_lead_median'] = float(np.nanmedian([e['per_lead'][f'A{l}']['bias_ms'] for e in rows for l in LEADS]))
    results['summary'] = summ
    log('\n===== TONG HOP 22 chu the (giu lai theo fold) =====')
    for g in ('PhysioNet', 'B2', 'B1'):
        if f'{g}_F1_psd' in summ:
            s, m = summ[f'{g}_F1_psd'], summ[f'{g}_F1_mean4']
            log(f'   {g:<9} n={s["n"]:2d}  F1 PSD {s["mean"]:6.2f} +/- {s["sd"]:5.2f}  TB4 {m["mean"]:6.2f} +/- {m["sd"]:5.2f}  '
                f'>=90: {s["n_ge90"]}  <50: {s["n_lt50"]}  lech PSD trung vi {summ[f"{g}_bias_psd_median"]:+.1f} ms')

    # ---- production
    if not a.no_production and not a.tag:
        log('\n-- production_22: train tren CA 22 chu the --')
        idx = build_index(D, ALL)
        torch.manual_seed(a.seed)
        prod = M.FetalQRSTCN()
        hist, _ = train(prod, D, HM, idx, epochs, a.seed, augment)
        thr_prod = float(np.median([v['threshold'] for v in results['folds'].values()]))
        p = os.path.join(CKPT, 'fetalqrs_tcn_22_production.pt')
        torch.save(dict(state_dict=prod.state_dict(), config=CFG, threshold=thr_prod, trained_on=ALL, seed=a.seed,
                        augment=augment, augment_cfg=A.describe() if augment else None, epochs=epochs, stride=STRIDE,
                        loss=hist, expected_performance=summ, n_params=M.n_params(prod), receptive_field_samples=rf,
                        note='Train tren 22 san phu doc lap (5 PhysioNet + 10 B1 + 7 B2 khong trung). Khong co diem '
                             'giu lai; expected_performance la tong hop 11 fold train cung cong thuc.'), p)
        results['production'] = dict(path=os.path.basename(p), threshold=thr_prod, loss=hist, n_segments=len(idx))
        log(f'   da luu {p} (nguong {thr_prod:.2f})')
        del prod, idx
    results['meta']['minutes'] = (time.time() - t_all) / 60
    json.dump(results, open(os.path.join(HERE, f'train_22{suffix}.json'), 'w'), indent=1, default=float)
    log(f'\nDONE {results["meta"]["minutes"]:.1f} phut -> train_22{suffix}.json')


if __name__ == '__main__':
    main()
