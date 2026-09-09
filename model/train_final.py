"""
Train and SAVE the FetalQRS-TCN checkpoints.

Produces two kinds of artefact:
  1. Five leave-one-record-out fold models (fold_r01 ... fold_r10) with the honest
     held-out metrics for each. These are the numbers to quote.
  2. One production model trained on all five records, for use on new recordings.
     It has NO honest held-out score by construction; the LORO mean is its expected
     performance on an unseen woman.

Each checkpoint stores weights, config, the decision threshold chosen on the inner
validation record, the metrics, and the git-free provenance needed to reproduce it.
"""
import os, sys, json, time, math, argparse, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
import mne, wfdb

ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
torch.set_num_threads(max(1, (os.cpu_count() or 4) - 1))

RAW = os.environ.get('ADFECGDB_DIR', os.path.join(ROOT, 'data', 'adfecgdb'))
CKPT = os.path.join(ROOT, 'checkpoints'); os.makedirs(CKPT, exist_ok=True)
RES = os.path.join(ROOT, 'results'); os.makedirs(RES, exist_ok=True)
RECS = ['r01', 'r04', 'r07', 'r08', 'r10']
LEADS = (1, 2, 3, 4)
CFG = M.CFG
LOG = open(os.path.join(RES, 'train_final_log.txt'), 'a', encoding='utf-8')
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n'); LOG.flush()

def load_records():
    if not os.path.isdir(RAW):
        raise SystemExit(
            'ADFECGDB not found at %s\n'
            'Run:  python download_data.py --root data --only adfecgdb\n'
            'or set the ADFECGDB_DIR environment variable to the folder holding r01.edf' % RAW)
    D = {}
    for ri, rec in enumerate(RECS):
        raw = mne.io.read_raw_edf(os.path.join(RAW, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        q = CFG['fs_in'] // CFG['fs']
        fq = (wfdb.rdann(os.path.join(RAW, rec + '.edf'), 'qrs').sample / q).round().astype(int)
        for lead in LEADS:
            x250 = M.preprocess(sig[lead], CFG['fs_in'], CFG)
            res, _ = M.cancel_maternal(x250, CFG)
            D[(ri, lead)] = (M.robust_scale(res).astype(np.float32),
                             M.robust_scale(x250).astype(np.float32), fq)
    return D

def segments(D, rec_ids, stride=250):
    X, Y = [], []
    for (ri, lead), (r, x, fq) in D.items():
        if ri not in rec_ids: continue
        hm = M.make_heatmap(len(r), fq)
        for s in range(0, len(r) - CFG['seg'], stride):
            X.append(np.stack([r[s:s + CFG['seg']], x[s:s + CFG['seg']]]))
            Y.append(hm[s:s + CFG['seg']])
    return torch.from_numpy(np.stack(X)), torch.from_numpy(np.stack(Y))

def train(model, X, Y, epochs=6, bs=32, lr=3e-3):
    pw = torch.tensor([float((Y < .1).sum() / max((Y > .5).sum(), 1))]).clamp(max=30.)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, lr, epochs * math.ceil(len(X) / bs))
    for ep in range(epochs):
        model.train(); perm = torch.randperm(len(X)); tot = 0.
        for i in range(0, len(X), bs):
            j = perm[i:i + bs]
            loss = F.binary_cross_entropy_with_logits(model(X[j]), Y[j], pos_weight=pw)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.); opt.step(); sch.step()
            tot += loss.item()
        log(f'      epoch {ep+1}/{epochs} loss {tot/max(1,math.ceil(len(X)/bs)):.4f}')
    return model

def eval_record(model, D, ri, thr):
    out = []
    for lead in LEADS:
        r, x, fq = D[(ri, lead)]
        prob = M.probability_series(model, r, x, CFG)
        pk = M.pick_peaks(prob, thr, CFG)
        m = M.match_events(pk, fq, CFG['fs'], CFG['tolerance_ms'])
        m.update(record=RECS[ri], lead=lead); out.append(m)
    return out

def pick_threshold(model, D, ri, grid=np.arange(.20, .80, .05)):
    best, bt = -1, .45
    for t in grid:
        f = float(np.mean([m['F1'] for m in eval_record(model, D, ri, float(t))]))
        if f > best: best, bt = f, float(t)
    return bt, best

def main(epochs, seed):
    t0 = time.time()
    log(f'\n===== TRAIN FINAL | seed {seed} | epochs {epochs} | band {CFG["band"]} Hz | '
        f'{CFG["seg"]/CFG["fs"]:.1f} s segments =====')
    D = load_records(); log(f'records loaded {time.time()-t0:.0f}s')
    rf = M.FetalQRSTCN().receptive_field
    log(f'model: {M.n_params(M.FetalQRSTCN()):,} params, receptive field {rf} samples = {rf*1000//CFG["fs"]} ms')

    all_rows, fold_info = [], {}
    for ti in range(5):
        others = [i for i in range(5) if i != ti]
        vi, tri = others[0], others[1:]
        log(f'\n-- fold test={RECS[ti]}  val={RECS[vi]}  train={[RECS[i] for i in tri]} --')
        X, Y = segments(D, tri)
        torch.manual_seed(seed)
        model = train(M.FetalQRSTCN(), X, Y, epochs)
        thr, vf1 = pick_threshold(model, D, vi)
        rows = eval_record(model, D, ti, thr)
        f1 = float(np.mean([m['F1'] for m in rows]))
        log(f'   val {RECS[vi]} F1 {vf1:.2f} at thr {thr:.2f}  ->  TEST {RECS[ti]} macro F1 {f1:.2f} '
            f'(Se {np.mean([m["Se"] for m in rows]):.2f}, PPV {np.mean([m["PPV"] for m in rows]):.2f}, '
            f'jitter {np.nanmean([m["jitter_ms"] for m in rows]):.2f} ms)')
        p = os.path.join(CKPT, f'fetalqrs_tcn_fold_{RECS[ti]}.pt')
        torch.save(dict(state_dict=model.state_dict(), config=CFG, threshold=thr,
                        test_record=RECS[ti], val_record=RECS[vi],
                        train_records=[RECS[i] for i in tri], seed=seed, epochs=epochs,
                        metrics_per_lead=rows, macro_F1=f1,
                        n_params=M.n_params(model), receptive_field_samples=rf), p)
        fold_info[RECS[ti]] = dict(path=os.path.basename(p), threshold=thr, macro_F1=f1, rows=rows)
        all_rows += rows

    f1 = [m['F1'] for m in all_rows]
    tp = sum(m['TP'] for m in all_rows); fp = sum(m['FP'] for m in all_rows); fn = sum(m['FN'] for m in all_rows)
    se = tp / (tp + fn) * 100; pp = tp / (tp + fp) * 100
    summary = dict(macro_F1=float(np.mean(f1)), sd_F1=float(np.std(f1)),
                   micro_F1=2 * se * pp / (se + pp), Se=float(np.mean([m['Se'] for m in all_rows])),
                   PPV=float(np.mean([m['PPV'] for m in all_rows])),
                   jitter_ms=float(np.nanmean([m['jitter_ms'] for m in all_rows])),
                   TP=tp, FP=fp, FN=fn, n_evaluations=len(all_rows), seed=seed, epochs=epochs)
    log(f'\n===== LORO SUMMARY (seed {seed}) =====')
    log(f'  macro F1 {summary["macro_F1"]:.2f} +- {summary["sd_F1"]:.2f} | micro {summary["micro_F1"]:.2f} | '
        f'Se {summary["Se"]:.2f} | PPV {summary["PPV"]:.2f} | jitter {summary["jitter_ms"]:.2f} ms')
    log(f'  TP {tp}  FP {fp}  FN {fn}  over {len(all_rows)} (record x lead) evaluations')

    # production model: all five records, threshold = median of the fold thresholds
    log('\n-- production model: training on ALL five records --')
    X, Y = segments(D, list(range(5)))
    torch.manual_seed(seed)
    prod = train(M.FetalQRSTCN(), X, Y, epochs)
    thr_prod = float(np.median([v['threshold'] for v in fold_info.values()]))
    pp_path = os.path.join(CKPT, 'fetalqrs_tcn_production.pt')
    torch.save(dict(state_dict=prod.state_dict(), config=CFG, threshold=thr_prod,
                    trained_on=RECS, seed=seed, epochs=epochs,
                    expected_performance=summary, n_params=M.n_params(prod),
                    receptive_field_samples=rf,
                    note='Trained on all 5 ADFECGDB records. No held-out score exists for this '
                         'model by construction; expected_performance is the LORO mean of the '
                         'fold models trained identically.'), pp_path)
    log(f'  saved {pp_path} (threshold {thr_prod:.2f})')

    json.dump(dict(summary=summary, folds=fold_info, config={k: str(v) for k, v in CFG.items()}),
              open(os.path.join(RES, 'train_final.json'), 'w'), indent=1)
    log(f'\nDONE in {time.time()-t0:.0f}s. Checkpoints in {CKPT}')
    return summary

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--epochs', type=int, default=6); ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    main(a.epochs, a.seed)
