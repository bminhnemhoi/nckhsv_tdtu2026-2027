"""
FINAL EXPERIMENT — best front end (10-60 Hz, chosen by the band ablation) x best architectures
(chosen by the stage-1 search on a held-out validation record), under FULL leave-one-record-out
with an inner validation record for threshold selection, 3 seeds.

This is the number the team should quote as its own baseline.
"""
import os, sys, json, time, math, argparse, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
import mne, wfdb
from scipy import signal as sg
from scipy.stats import wilcoxon
from sklearn.ensemble import HistGradientBoostingClassifier

torch.set_num_threads(max(1, (os.cpu_count() or 4) - 1))
ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pilot', os.path.join(ROOT, 'pilot.py'))
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
A = importlib.util.spec_from_file_location('arch', os.path.join(ROOT, 'arch_search.py'))
OUT = os.path.join(ROOT, 'results'); os.makedirs(OUT, exist_ok=True)
RECS, FS, HOP = P.RECS, 250, 5
LOGF = open(os.path.join(OUT, 'final_loro_log.txt'), 'a', encoding='utf-8')
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOGF.write(s + '\n'); LOGF.flush()

# ---- models (copied standalone so this script does not import the cache) ----
def blk(i, o, k, d=1):
    return nn.Sequential(nn.Conv1d(i, o, k, padding=(k // 2) * d, dilation=d, bias=False),
                         nn.BatchNorm1d(o), nn.GELU())

class CNN1D(nn.Module):
    def __init__(s, cin, chans, ks, dil=None):
        super().__init__(); dil = dil or [1] * len(chans); L = []; p = cin
        for c, k, d in zip(chans, ks, dil):
            L += [blk(p, c, k, d), nn.MaxPool1d(2)]; p = c
        s.body = nn.Sequential(*L)
        s.head = nn.Sequential(nn.Linear(p * 2, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x):
        h = s.body(x); return s.head(torch.cat([h.mean(-1), h.amax(-1)], 1))

class Res1D(nn.Module):
    def __init__(s, cin, chans=(32, 64, 96)):
        super().__init__(); s.stem = blk(cin, chans[0], 7); mods = []; p = chans[0]
        for c in chans:
            mods.append(nn.ModuleDict({'a': blk(p, c, 3),
                'b': nn.Sequential(nn.Conv1d(c, c, 3, padding=1, bias=False), nn.BatchNorm1d(c)),
                'sc': nn.Conv1d(p, c, 1, bias=False) if p != c else nn.Identity()})); p = c
        s.blocks = nn.ModuleList(mods); s.act = nn.GELU(); s.pool = nn.MaxPool1d(2)
        s.head = nn.Sequential(nn.Linear(p * 2, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x):
        h = s.stem(x)
        for m in s.blocks: h = s.pool(s.act(m['b'](m['a'](h)) + m['sc'](h)))
        return s.head(torch.cat([h.mean(-1), h.amax(-1)], 1))

class TCN(nn.Module):
    def __init__(s, cin, c=48, dils=(1, 2, 4, 8)):
        super().__init__(); s.stem = blk(cin, c, 7)
        s.blocks = nn.ModuleList([nn.ModuleDict({'a': blk(c, c, 3, d),
            'b': nn.Sequential(nn.Conv1d(c, c, 3, padding=d, dilation=d, bias=False), nn.BatchNorm1d(c))}) for d in dils])
        s.act = nn.GELU()
        s.head = nn.Sequential(nn.Linear(c * 2, 64), nn.GELU(), nn.Dropout(.2), nn.Linear(64, 1))
    def forward(s, x):
        h = s.stem(x)
        for m in s.blocks: h = s.act(m['b'](m['a'](h)) + h)
        return s.head(torch.cat([h.mean(-1), h.amax(-1)], 1))

MODELS = {
    'cnn_dil':  lambda ci: CNN1D(ci, (32, 48, 64), (7, 5, 3), dil=(1, 2, 4)),
    'cnn_l':    lambda ci: CNN1D(ci, (32, 64, 96, 128), (7, 5, 3, 3)),
    'resnet1d': lambda ci: Res1D(ci),
    'tcn':      lambda ci: TCN(ci),
}

# ---- data ----
def build(band, win, leads=(1, 2, 3, 4)):
    lo, hi = band; D = {}
    for ri, rec in enumerate(RECS):
        raw = mne.io.read_raw_edf(os.path.join(P.RAW, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        fq = (wfdb.rdann(os.path.join(P.RAW, rec + '.edf'), 'qrs').sample / 4).round().astype(int)
        b, a = sg.butter(4, [lo / 500., hi / 500.], btype='band')
        for lead in leads:
            x = sg.filtfilt(b, a, sig[lead])
            if lo < 50 < hi: x = sg.filtfilt(*sg.iirnotch(50, 30, 1000), x)
            x = sg.resample_poly(x, 1, 4)
            r = P.robust_scale(P.template_subtract(x, P.detect_mqrs(x))); xs = P.robust_scale(x)
            half = win // 2
            cen = np.arange(half + 2, len(r) - half - 2, HOP)
            Xw = np.stack([np.stack([r[c - half:c - half + win], xs[c - half:c - half + win]]) for c in cen]).astype(np.float32)
            d = np.abs(cen[:, None] - fq[None, :]).min(1)
            D[(ri, lead)] = dict(X=Xw, y=(d <= 5).astype(np.float32), amb=((d > 5) & (d < 15)), cen=cen, fq=fq)
    return D

def event_metrics(prob, cen, fq, thr, tol_ms=50, refr_ms=250):
    p = np.convolve(prob, np.ones(3) / 3, mode='same')
    pk, _ = sg.find_peaks(p, height=thr, distance=max(int(refr_ms / 1000 * FS / HOP), 1))
    det = cen[pk]; tol = int(tol_ms / 1000 * FS)
    gm = np.zeros(len(fq), bool); tp = 0; errs = []
    for dd0 in det:
        dd = np.abs(fq - dd0); ok = np.where((dd <= tol) & (~gm))[0]
        if len(ok):
            j = ok[np.argmin(dd[ok])]; gm[j] = True; tp += 1; errs.append(dd[j] / FS * 1000)
    fp = len(det) - tp; fn = len(fq) - int(gm.sum())
    se = tp / (tp + fn) * 100 if tp + fn else 0.; ppv = tp / (tp + fp) * 100 if tp + fp else 0.
    return dict(Se=se, PPV=ppv, F1=2 * se * ppv / (se + ppv) if se + ppv else 0., TP=tp, FP=fp, FN=fn,
                jitter=float(np.mean(errs)) if errs else float('nan'))

def train_nn(model, X, y, epochs, bs=512, lr=2e-3):
    Xt = torch.from_numpy(X); yt = torch.from_numpy(y)
    pw = torch.tensor([float((y == 0).sum() / max((y == 1).sum(), 1))])
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, lr, epochs * math.ceil(len(X) / bs))
    for _ in range(epochs):
        model.train(); perm = torch.randperm(len(X))
        for i in range(0, len(X), bs):
            j = perm[i:i + bs]
            loss = F.binary_cross_entropy_with_logits(model(Xt[j]).view(-1), yt[j], pos_weight=pw)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.); opt.step(); sch.step()
    return model

def predict_nn(model, X):
    model.eval(); Xt = torch.from_numpy(X)
    with torch.no_grad():
        return np.concatenate([torch.sigmoid(model(Xt[i:i + 4096]).view(-1)).numpy() for i in range(0, len(X), 4096)])

def run(D, name, leads, seeds, epochs):
    rows = []
    for sd in seeds:
        for ti in range(5):
            others = [i for i in range(5) if i != ti]; vi = others[0]; tri = others[1:]
            Xtr = np.concatenate([D[(r, l)]['X'][~D[(r, l)]['amb']] for r in tri for l in leads])
            ytr = np.concatenate([D[(r, l)]['y'][~D[(r, l)]['amb']] for r in tri for l in leads])
            if name == 'gbm':
                clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=.08, random_state=sd)
                clf.fit(Xtr[:, 0, :], ytr)
                pred = lambda d: clf.predict_proba(d['X'][:, 0, :])[:, 1]
            else:
                torch.manual_seed(sd)
                m = train_nn(MODELS[name](2), Xtr, ytr, epochs)
                pred = lambda d: predict_nn(m, d['X'])
            bt, bf = .5, -1
            for t in np.arange(.05, .9, .05):
                f = np.mean([event_metrics(pred(D[(vi, l)]), D[(vi, l)]['cen'], D[(vi, l)]['fq'], t)['F1'] for l in leads])
                if f > bf: bf, bt = f, t
            for l in leads:
                mm = event_metrics(pred(D[(ti, l)]), D[(ti, l)]['cen'], D[(ti, l)]['fq'], bt)
                mm.update(rec=RECS[ti], lead=l, seed=sd, thr=float(bt)); rows.append(mm)
    return rows

def summarise(rows):
    f1 = [r['F1'] for r in rows]
    tp = sum(r['TP'] for r in rows); fp = sum(r['FP'] for r in rows); fn = sum(r['FN'] for r in rows)
    se = tp / (tp + fn) * 100; pp = tp / (tp + fp) * 100
    return dict(macro_F1=float(np.mean(f1)), sd=float(np.std(f1)),
                micro_F1=2 * se * pp / (se + pp), Se=float(np.mean([r['Se'] for r in rows])),
                PPV=float(np.mean([r['PPV'] for r in rows])),
                jitter=float(np.nanmean([r['jitter'] for r in rows])), n=len(rows))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--band', default='10,60'); ap.add_argument('--win', type=int, default=75)
    ap.add_argument('--epochs', type=int, default=10); ap.add_argument('--seeds', default='0,1,2')
    ap.add_argument('--models', default='gbm,cnn_dil,resnet1d,tcn,cnn_l')
    a = ap.parse_args()
    lo, hi = [float(v) for v in a.band.split(',')]
    seeds = [int(v) for v in a.seeds.split(',')]
    log(f'\n=== FINAL LORO | band {lo}-{hi} Hz | window {a.win} samples ({a.win*4} ms) | '
        f'4 leads | seeds {seeds} | epochs {a.epochs} | +/-50 ms ===')
    t0 = time.time(); D = build((lo, hi), a.win); log(f'data built {time.time()-t0:.0f}s')
    res = {}
    for name in a.models.split(','):
        t1 = time.time()
        sds = [0] if name == 'gbm' else seeds
        rows = run(D, name, (1, 2, 3, 4), sds, a.epochs)
        s = summarise(rows); res[name] = dict(summary=s, rows=rows)
        log(f'{name:10s} macro F1 {s["macro_F1"]:6.2f} +-{s["sd"]:5.2f} | micro {s["micro_F1"]:6.2f} | '
            f'Se {s["Se"]:5.2f} | PPV {s["PPV"]:5.2f} | jitter {s["jitter"]:4.1f} ms | n={s["n"]} | {time.time()-t1:.0f}s')
    log('\n-- paired Wilcoxon on per-(record,lead) F1, seed 0 --')
    base = [r['F1'] for r in res['gbm']['rows']]
    for name in res:
        if name == 'gbm': continue
        cur = [r['F1'] for r in res[name]['rows'] if r['seed'] == 0]
        if len(cur) != len(base): continue
        try: _, pv = wilcoxon(base, cur)
        except Exception: pv = float('nan')
        log(f'  gbm vs {name:10s}: {np.mean(base):6.2f} vs {np.mean(cur):6.2f}  '
            f'diff {np.mean(np.array(cur)-np.array(base)):+5.2f}  p={pv:.4f}')
    json.dump({k: v['summary'] | {'rows': v['rows']} for k, v in res.items()},
              open(os.path.join(OUT, f'final_loro_{int(lo)}_{int(hi)}_w{a.win}.json'), 'w'), indent=1)
    log(f'DONE {time.time()-t0:.0f}s')
