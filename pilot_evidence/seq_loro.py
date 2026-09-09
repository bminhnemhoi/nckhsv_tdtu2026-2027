"""
DEFINITIVE EXPERIMENT — winning sequence architecture under FULL leave-one-record-out.

Chosen by evidence, not by guess:
  front end 10-60 Hz    : band ablation, 8 candidates (band_ablation.py)
  4 s segments          : literature (DPSS swept 1-10 s -> 4 s best; R2W-Net / SCTD-Net 4.096 s)
  dilated TCN, RF 1.5 s : receptive-field sweep (seq_search.py), F1 monotone in RF
  per-sample heatmap    : gives 1.0 ms jitter vs 5.6-6.0 ms for window classifiers

Protocol: 5 records x 4 abdominal leads, LORO, inner validation record for the threshold,
3 seeds, event scoring at +/-50 ms, one-to-one greedy matching.
"""
import os, sys, json, time, math, argparse, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from scipy import signal as sg
from scipy.stats import wilcoxon

torch.set_num_threads(max(1, (os.cpu_count() or 4) - 1))
ROOT = os.path.dirname(os.path.abspath(__file__))
S = importlib.util.spec_from_file_location('seq', os.path.join(ROOT, 'seq_search.py'))
SS = importlib.util.module_from_spec(S)
sys.argv = ['seq']            # stop seq_search from parsing our args
S.loader.exec_module(SS)
OUT = os.path.join(ROOT, 'results'); os.makedirs(OUT, exist_ok=True)
RECS, FS, SEG = SS.RECS, SS.FS, SS.SEG
LOGF = open(os.path.join(OUT, 'seq_loro_log.txt'), 'a', encoding='utf-8')
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOGF.write(s + '\n'); LOGF.flush()

CANDS = {
    'tcn_rf2s':  lambda: SS.TCNSeq(dils=(1, 2, 4, 8, 16)),
    'tcn_rf4s':  lambda: SS.TCNSeq(dils=(1, 2, 4, 8, 16, 32)),
    'cnn_bigru': lambda: SS.CNNBiGRUSeq(),
    'short_cnn': lambda: SS.ShortCNNSeq(),
}

def run(D, name, seeds, epochs, stride):
    rows = []
    for sd in seeds:
        for ti in range(5):
            others = [i for i in range(5) if i != ti]; vi = others[0]; tri = others[1:]
            X, Y = SS.segments({k: v for k, v in D.items() if k[0] in tri}, tri, stride)
            torch.manual_seed(sd)
            m = SS.train(CANDS[name](), X, Y, epochs)
            _, thr, _ = SS.evaluate(m, D, vi)                      # threshold on VALIDATION record
            for lead in range(1, 5):
                r, x, fq = D[(ti, lead)]
                pr = SS.infer_full(m, r, x)
                mm = SS.event_metrics(pr, fq, thr)
                mm.update(rec=RECS[ti], lead=lead, seed=sd, thr=float(thr)); rows.append(mm)
            log(f'   {name} seed{sd} test={RECS[ti]} thr={thr:.2f} '
                f'F1={np.mean([r["F1"] for r in rows[-4:]]):.2f}')
    return rows

def summarise(rows):
    f1 = [r['F1'] for r in rows]
    tp = sum(r['TP'] for r in rows); fp = sum(r['FP'] for r in rows); fn = sum(r['FN'] for r in rows)
    se = tp / (tp + fn) * 100; pp = tp / (tp + fp) * 100
    return dict(macro_F1=float(np.mean(f1)), sd=float(np.std(f1)), micro_F1=2 * se * pp / (se + pp),
                Se=float(np.mean([r['Se'] for r in rows])), PPV=float(np.mean([r['PPV'] for r in rows])),
                jitter=float(np.nanmean([r['jitter'] for r in rows])), n=len(rows),
                TP=tp, FP=fp, FN=fn)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--band', default='10,60'); ap.add_argument('--epochs', type=int, default=6)
    ap.add_argument('--seeds', default='0,1,2'); ap.add_argument('--stride', type=int, default=250)
    ap.add_argument('--models', default='tcn_rf2s,short_cnn')
    a = ap.parse_args()
    lo, hi = [float(v) for v in a.band.split(',')]
    seeds = [int(v) for v in a.seeds.split(',')]
    log(f'\n=== SEQ LORO | band {lo}-{hi} Hz | 4 s segments | 4 leads | seeds {seeds} | '
        f'epochs {a.epochs} | +/-50 ms ===')
    t0 = time.time(); D = SS.load_all((lo, hi)); log(f'data loaded {time.time()-t0:.0f}s')
    res = {}
    for name in a.models.split(','):
        t1 = time.time(); rows = run(D, name, seeds, a.epochs, a.stride)
        s = summarise(rows); res[name] = dict(summary=s, rows=rows)
        log(f'>>> {name:12s} macro F1 {s["macro_F1"]:6.2f} +-{s["sd"]:5.2f} | micro {s["micro_F1"]:6.2f} | '
            f'Se {s["Se"]:5.2f} | PPV {s["PPV"]:5.2f} | jitter {s["jitter"]:4.2f} ms | '
            f'TP {s["TP"]} FP {s["FP"]} FN {s["FN"]} | {time.time()-t1:.0f}s')
    names = list(res)
    if len(names) > 1:
        log('\n-- paired Wilcoxon on per-(record,lead) F1, seed 0 --')
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a1 = [r['F1'] for r in res[names[i]]['rows'] if r['seed'] == 0]
                b1 = [r['F1'] for r in res[names[j]]['rows'] if r['seed'] == 0]
                try: _, pv = wilcoxon(a1, b1)
                except Exception: pv = float('nan')
                log(f'  {names[i]:12s} vs {names[j]:12s}: {np.mean(a1):6.2f} vs {np.mean(b1):6.2f} '
                    f' diff {np.mean(np.array(b1)-np.array(a1)):+5.2f}  p={pv:.4f}')
    json.dump({k: v['summary'] | {'rows': v['rows']} for k, v in res.items()},
              open(os.path.join(OUT, 'seq_loro.json'), 'w'), indent=1)
    log(f'DONE {time.time()-t0:.0f}s')
