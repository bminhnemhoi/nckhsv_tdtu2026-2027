# -*- coding: utf-8 -*-
"""
GIAI DOAN 1 muc 9 -- ABLATION BO B1 (kiem tra thien lech do sap nhap du lieu / incorporation bias).

Sao chep NGUYEN VEN cong thuc cua model/train_22.py, chi doi DANH SACH CHU THE:
    12 chu the CHI CO NHAN DIEN CUC DA DAU (nhan truc tiep, chuyen da):
        5 PhysioNet ADFECGDB : r01, r04, r07, r08, r10
        7 Silesia B2 khong trung PhysioNet : B2_03, B2_04, B2_05, B2_06, B2_08, B2_09, B2_12
    KHONG co B1 (10 chu the thai ky, nhan GIAN TIEP suy tu tin hieu bung, khong co dien cuc da dau).

CAU HOI: cai thien 5 -> 22 chu the (B1 93,30 -> 97,15) la do THEM DU LIEU hay do HOC THEO
PHONG CACH NHAN B1? Neu mo hinh 12 chu the (nhan sach, it du lieu hon 22, khong he thay B1)
van tot tren B1 va tren CinC 2013 thi phong cach nhan B1 KHONG phai nguyen nhan.

Giao thuc: 6 fold theo NHOM chu the, moi fold 2 chu the test / 1 val / 9 train; nguong chon tren val.
Doan 4 s @250 Hz, BCEWithLogits pos_weight, AdamW 3e-3 + OneCycle, clip 1.0, batch 32, 4 epoch, seed 0,
tang cuong on-the-fly (augment.py) chi khi train, stride 1 s. Sau 6 fold: production_12 tren ca 12,
nguong = trung vi nguong fold. Moi thu khac giong het train_22.py.

Chay:  python model/train_12.py                      (day du, seed 0, 4 epoch)
       python model/train_12.py --folds 1,2,3        (chay mot phan)
       python model/train_12.py --no-production
Ket qua: model/train_12.json, model/train_12_log.txt, model/checkpoints/fetalqrs_tcn_12_fold_XX.pt,
         model/checkpoints/fetalqrs_tcn_12_production.pt
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, math, argparse, importlib.util, random, datetime, platform, gc
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
import mne, wfdb
from scipy import signal as sg

torch.set_num_threads(int(os.environ.get('FQRS_THREADS', 3)))
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
B2 = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
B1_EXCLUDED = [f'B1_{i:02d}' for i in range(1, 11)]          # CO Y bo ra -- day la bien ablation
B2_DUPLICATES = {'B2_01': 'r01', 'B2_02': 'r10', 'B2_07': 'r04', 'B2_10': 'r07', 'B2_11': 'r08'}
ALL = PHYSIONET + B2                                          # 12 chu the, tat ca nhan da dau
LEADS = (1, 2, 3, 4)
SEG = CFG['seg']; Q = CFG['fs_in'] // CFG['fs']
STRIDE = {'PhysioNet': 250, 'B2': 250, 'B1': 500}
TOL_MS = 50; FHR_BAND = (1.8, 3.0)
THR_GRID = np.arange(.20, .80, .05)
N_FOLDS = 6

_LOG = None
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True)
    if _LOG: _LOG.write(s + '\n'); _LOG.flush()


def group_of(tag):
    return 'PhysioNet' if tag.startswith('r') else tag[:2]


# ------------------------------------------------------------------ du lieu (y het train_22.py)
def load_subject(tag):
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
    idx = []
    for tag in tags:
        st = STRIDE[group_of(tag)]
        for lead in LEADS:
            n = len(D[tag][lead][0])
            idx += [(tag, lead, s) for s in range(0, n - SEG, st)]
    return idx


def pos_weight_of(HM, idx):
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
    bl = max(LEADS, key=lambda l: D[tag][l][4])
    f1s = [per[l]['F1'] for l in LEADS]
    return dict(record=tag, group=group_of(tag), psd_lead=int(bl), threshold=thr,
                per_lead={f'A{l}': per[l] for l in LEADS},
                F1_psd=per[bl]['F1'], Se_psd=per[bl]['Se'], PPV_psd=per[bl]['PPV'], jitter_psd=per[bl]['jitter_ms'],
                bias_psd=per[bl]['bias_ms'], F1_mean4=float(np.mean(f1s)), F1_oracle=float(max(f1s)),
                bias_mean4=float(np.nanmean([per[l]['bias_ms'] for l in LEADS])))


# ------------------------------------------------------------------ fold
def make_folds(seed=0):
    """6 fold, moi fold 2 chu the test (moi chu the duoc test dung 1 lan), 1 val, 9 train."""
    rng = random.Random(seed)
    gold = ALL[:]
    rng.shuffle(gold)
    tests = [[gold[2 * i], gold[2 * i + 1]] for i in range(N_FOLDS)]
    folds = []
    for k, test in enumerate(tests):
        rest = [g for g in gold if g not in test]
        val = rest[k % len(rest)]
        train_ = [t for t in ALL if t not in test and t != val]
        folds.append(dict(fold=k + 1, test=test, val=val, train=train_))
    return folds


def main():
    global _LOG
    ap = argparse.ArgumentParser()
    ap.add_argument('--epochs', type=int, default=4)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--no-augment', action='store_true')
    ap.add_argument('--folds', default='', help='vd 1,2,3 ; rong = tat ca 6 + production')
    ap.add_argument('--tag', default='')
    ap.add_argument('--no-production', action='store_true')
    ap.add_argument('--thr-prod', type=float, default=None,
                    help='nguong cho production_12 khi khong chay lai fold (vd lay trung vi tu train_12.json cu)')
    a = ap.parse_args()
    augment = not a.no_augment
    suffix = f'_{a.tag}' if a.tag else ''
    _LOG = open(os.path.join(HERE, f'train_12{suffix}_log.txt'), 'a', encoding='utf-8')
    t_all = time.time()
    log(f'\n===== TRAIN 12 (ABLATION BO B1) | {datetime.datetime.now():%Y-%m-%d %H:%M:%S} | seed {a.seed} | '
        f'augment {augment} | epochs {a.epochs} | threads {torch.get_num_threads()} | torch {torch.__version__} | '
        f'{platform.platform()} =====')
    log(f'chu the ({len(ALL)}): {ALL}')
    log(f'CO Y LOAI (bien ablation): B1 {B1_EXCLUDED}  -- nhan gian tiep, khong co dien cuc da dau')
    log(f'CUNG LOAI (trung PhysioNet): {list(B2_DUPLICATES)}')
    folds = make_folds(a.seed)
    for f in folds:
        log(f'   fold {f["fold"]:2d}: test {f["test"]}  val {f["val"]}  train n={len(f["train"])} {f["train"]}')
    sel = [int(x) for x in a.folds.split(',') if x] if a.folds else list(range(1, N_FOLDS + 1))
    log('nap 12 chu the ...')
    D = load_all(ALL)
    HM = make_heatmaps(D, ALL)
    rf = M.FetalQRSTCN().receptive_field
    log(f'model: {M.n_params(M.FetalQRSTCN()):,} tham so, truong tiep nhan {rf} mau = {rf * 1000 // CFG["fs"]} ms; '
        f'tang cuong: {A.describe() if augment else "KHONG"}')
    n_steps = {f['fold']: math.ceil(len(build_index(D, f['train'])) / 32) for f in folds}
    n_prod = math.ceil(len(build_index(D, ALL)) / 32)
    log(f'so buoc/epoch: fold {sorted(set(n_steps.values()))}, production {n_prod}')

    results = dict(meta=dict(date=str(datetime.datetime.now()), seed=a.seed, augment=augment, epochs=a.epochs,
                             threads=torch.get_num_threads(), torch=torch.__version__, stride=STRIDE,
                             tolerance_ms=TOL_MS, n_folds=N_FOLDS,
                             subjects=dict(PhysioNet=PHYSIONET, B2=B2),
                             excluded_B1=B1_EXCLUDED, excluded_duplicates=B2_DUPLICATES,
                             augment_cfg=A.describe() if augment else None,
                             cfg={k: (list(v) if isinstance(v, tuple) else v) for k, v in CFG.items()},
                             ablation='bo toan bo 10 chu the B1 (nhan gian tiep) khoi tap huan luyen; '
                                      'moi thu khac giong het train_22.py',
                             label_note='tat ca 12 chu the deu co nhan DIEN CUC DA DAU (truc tiep)'),
                   folds={}, subjects={})
    # gop ket qua fold da chay tu lan truoc (chay lam nhieu dot vi ngan sach thoi gian)
    prev = os.path.join(HERE, f'train_12{suffix}.json')
    if os.path.isfile(prev):
        try:
            old = json.load(open(prev, encoding='utf-8'))
            for kk, vv in old.get('folds', {}).items():
                if int(kk) not in sel: results['folds'][kk] = vv
            for kk, vv in old.get('subjects', {}).items():
                if vv.get('fold') not in sel: results['subjects'][kk] = vv
            if results['folds']:
                log(f'   gop lai {sorted(results["folds"])} tu lan chay truoc')
        except Exception as e:
            log(f'   (khong gop duoc {prev}: {e})')
    for f in folds:
        if f['fold'] not in sel: continue
        k = f['fold']; tf = time.time()
        log(f'\n-- fold {k:02d}  test={f["test"]}  val={f["val"]}  train={f["train"]} --')
        idx = build_index(D, f['train'])
        torch.manual_seed(a.seed)
        model = M.FetalQRSTCN()
        hist, _ = train(model, D, HM, idx, a.epochs, a.seed, augment)
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
                    val_F1=vf1, seed=a.seed, augment=augment, epochs=a.epochs, loss=hist,
                    n_segments=len(idx), minutes=(time.time() - tf) / 60, test=rows)
        results['folds'][f'{k:02d}'] = info
        if not a.tag:
            p = os.path.join(CKPT, f'fetalqrs_tcn_12_fold_{k:02d}.pt')
            torch.save(dict(state_dict=model.state_dict(), config=CFG, threshold=thr, fold=k,
                            test_subjects=f['test'], val_subject=f['val'], train_subjects=f['train'],
                            seed=a.seed, augment=augment, augment_cfg=A.describe() if augment else None,
                            epochs=a.epochs, stride=STRIDE, loss=hist, val_F1=vf1,
                            metrics={t: dict(F1_psd=r['F1_psd'], F1_mean4=r['F1_mean4'], psd_lead=r['psd_lead'])
                                     for t, r in rows.items()},
                            n_params=M.n_params(model), receptive_field_samples=rf,
                            note='ABLATION: train tren 12 chu the nhan da dau (KHONG co B1)'), p)
        log(f'   fold {k:02d} xong {info["minutes"]:.1f} phut; tong {(time.time() - t_all) / 60:.1f} phut')
        del model, idx; gc.collect()
        json.dump(results, open(os.path.join(HERE, f'train_12{suffix}.json'), 'w'), indent=1, default=float)

    # ---- tong hop theo nhom
    summ = {}
    for g in ('PhysioNet', 'B2'):
        rows = [e for e in results['subjects'].values() if e['group'] == g]
        if not rows: continue
        for key in ('F1_psd', 'F1_mean4'):
            v = np.array([e[key] for e in rows])
            summ[f'{g}_{key}'] = dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                                      n=int(len(v)), n_ge90=int((v >= 90).sum()), n_lt50=int((v < 50).sum()))
        summ[f'{g}_bias_psd_median'] = float(np.nanmedian([e['bias_psd'] for e in rows]))
    allrows = list(results['subjects'].values())
    if allrows:
        for key in ('F1_psd', 'F1_mean4'):
            v = np.array([e[key] for e in allrows])
            summ[f'ALL12_{key}'] = dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                                        n=int(len(v)), n_ge90=int((v >= 90).sum()), n_lt50=int((v < 50).sum()))
    results['summary'] = summ
    log('\n===== TONG HOP 12 chu the (giu lai theo fold) =====')
    for g in ('PhysioNet', 'B2', 'ALL12'):
        if f'{g}_F1_psd' in summ:
            s, m = summ[f'{g}_F1_psd'], summ[f'{g}_F1_mean4']
            log(f'   {g:<9} n={s["n"]:2d}  F1 PSD {s["mean"]:6.2f} +/- {s["sd"]:5.2f}  TB4 {m["mean"]:6.2f} +/- {m["sd"]:5.2f}  '
                f'>=90: {s["n_ge90"]}  <50: {s["n_lt50"]}')

    # ---- production
    if not a.no_production and not a.tag:
        log('\n-- production_12: train tren CA 12 chu the (nhan da dau) --')
        idx = build_index(D, ALL)
        torch.manual_seed(a.seed)
        prod = M.FetalQRSTCN()
        hist, _ = train(prod, D, HM, idx, a.epochs, a.seed, augment)
        if results['folds']:
            thr_prod = float(np.median([v['threshold'] for v in results['folds'].values()]))
        elif a.thr_prod is not None:
            thr_prod = float(a.thr_prod)
        else:
            old = os.path.join(HERE, 'train_12.json')
            fj = json.load(open(old, encoding='utf-8'))['folds'] if os.path.isfile(old) else {}
            thr_prod = float(np.median([v['threshold'] for v in fj.values()])) if fj else .45
        log(f'   nguong production = {thr_prod:.2f} (trung vi nguong fold)')
        p = os.path.join(CKPT, 'fetalqrs_tcn_12_production.pt')
        torch.save(dict(state_dict=prod.state_dict(), config=CFG, threshold=thr_prod, trained_on=ALL, seed=a.seed,
                        augment=augment, augment_cfg=A.describe() if augment else None, epochs=a.epochs, stride=STRIDE,
                        loss=hist, expected_performance=summ, n_params=M.n_params(prod), receptive_field_samples=rf,
                        note='ABLATION BO B1: train tren 12 san phu nhan da dau (5 PhysioNet + 7 B2 khong trung). '
                             'KHONG he thay B1 -> dung de do zero-shot tren B1 va CinC 2013.'), p)
        results['production'] = dict(path=os.path.basename(p), threshold=thr_prod, loss=hist, n_segments=len(idx))
        log(f'   da luu {p} (nguong {thr_prod:.2f})')
        del prod, idx
    results['meta']['minutes'] = (time.time() - t_all) / 60
    json.dump(results, open(os.path.join(HERE, f'train_12{suffix}.json'), 'w'), indent=1, default=float)
    log(f'\nDONE {results["meta"]["minutes"]:.1f} phut -> train_12{suffix}.json')


if __name__ == '__main__':
    main()
