"""Do day du: chi so cua Khanh + chi so THAT cua DPSS + chi phi tinh toan."""
import os, sys, json, time, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, torch, mne, wfdb
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import adfecgdb_dir, cinc2013_dir
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG = M.CFG
RAW = adfecgdb_dir()
LEAD = {'r01': 4, 'r04': 4, 'r07': 4, 'r08': 4, 'r10': 1}
RECS = list(LEAD)

def match(det, gt, tol=50):
    gm = np.zeros(len(gt), bool); dm = np.zeros(len(det), bool); err = []
    for i, x in enumerate(det):
        dist = np.abs(gt - x); w = np.where((dist <= tol) & (~gm))[0]
        if len(w): j = w[np.argmin(dist[w])]; gm[j] = True; dm[i] = True; err.append(dist[j])
    tp = int(dm.sum()); return tp, len(det) - tp, len(gt) - tp, err

def fhr_series(pk, fs=1000., seg_s=4.0, dur=300.):
    """fHR trung binh trong tung doan seg_s giay, tinh tu khoang RR"""
    out = []
    for s in np.arange(0, dur, seg_s):
        w = pk[(pk >= s * fs) & (pk < (s + seg_s) * fs)]
        out.append(60.0 * fs / np.mean(np.diff(w)) if len(w) >= 2 else np.nan)
    return np.array(out)

def run(mode):
    rows = {}
    for rec in RECS:
        ck = os.path.join(ROOT, 'model', 'checkpoints',
                          f'fetalqrs_tcn_fold_{rec}.pt' if mode == 'loro' else 'fetalqrs_tcn_production.pt')
        b = torch.load(ck, map_location='cpu', weights_only=False)
        net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
        raw = mne.io.read_raw_edf(os.path.join(RAW, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()[LEAD[rec]]
        x250 = M.preprocess(sig, 1000, CFG); res, _ = M.cancel_maternal(x250, CFG)
        prob = M.probability_series(net, M.robust_scale(res).astype(np.float32),
                                    M.robust_scale(x250).astype(np.float32), CFG)
        det = M.pick_peaks(prob, float(b['threshold']), CFG).astype(np.int64) * 4
        gt = np.array(wfdb.rdann(os.path.join(RAW, rec), 'edf.qrs').sample)
        tp, fp, fn, err = match(det, gt)
        f_hat, f_ref = fhr_series(det), fhr_series(gt)
        ok = ~np.isnan(f_hat) & ~np.isnan(f_ref)
        rows[rec] = dict(
            GT=len(gt), Det=len(det), TP=tp, FP=fp, FN=fn,
            Se=100 * tp / (tp + fn), PPV=100 * tp / (tp + fp),
            F1=200 * tp / (2 * tp + fp + fn), jitter=float(np.mean(err)),
            MAE_khanh=abs(len(det) - len(gt)) / 5.0,
            MAE_fhr_that=float(np.mean(np.abs(f_hat[ok] - f_ref[ok]))),
            FHRprec_DPSS=100 * float(np.mean(np.abs(f_hat[ok] - f_ref[ok]) <= 5.0)))
    return rows

def show(tag, rows):
    print(f'\n########## {tag} ##########')
    h = f'{"rec":<5}{"GT":>5}{"Det":>5}{"TP":>5}{"FP":>4}{"FN":>4}{"Se":>8}{"PPV":>8}{"F1":>8}{"jit_ms":>8}{"MAE_Khanh":>11}{"MAE_that":>10}{"FHRprec":>9}'
    print(h); print('-' * len(h))
    for r, v in rows.items():
        print(f'{r:<5}{v["GT"]:>5}{v["Det"]:>5}{v["TP"]:>5}{v["FP"]:>4}{v["FN"]:>4}{v["Se"]:>8.2f}{v["PPV"]:>8.2f}'
              f'{v["F1"]:>8.2f}{v["jitter"]:>8.2f}{v["MAE_khanh"]:>11.2f}{v["MAE_fhr_that"]:>10.2f}{v["FHRprec_DPSS"]:>9.2f}')
    g = lambda k: np.mean([v[k] for v in rows.values()])
    tp = sum(v['TP'] for v in rows.values()); fp = sum(v['FP'] for v in rows.values()); fn = sum(v['FN'] for v in rows.values())
    print('-' * len(h))
    print(f'{"MACRO":<5}{"":>5}{"":>5}{"":>5}{"":>4}{"":>4}{g("Se"):>8.2f}{g("PPV"):>8.2f}{g("F1"):>8.2f}'
          f'{g("jitter"):>8.2f}{g("MAE_khanh"):>11.2f}{g("MAE_fhr_that"):>10.2f}{g("FHRprec_DPSS"):>9.2f}')
    print(f'{"MICRO":<5}{"":>5}{"":>5}{tp:>5}{fp:>4}{fn:>4}{100*tp/(tp+fn):>8.2f}{100*tp/(tp+fp):>8.2f}{200*tp/(2*tp+fp+fn):>8.2f}')
    return rows

A = show('CHE DO LORO  (moi ban ghi dung checkpoint CHUA TUNG thay no) -- CON SO TRUNG THUC', run('loro'))
B = show('CHE DO PRODUCTION (da thay ca 5 ban ghi) -- CO RO RI, chi de tham chieu', run('prod'))
json.dump(dict(loro=A, prod=B), open(os.path.join(HERE, 'full_measure.json'), 'w'), indent=1)

print('\n########## CHI PHI TINH TOAN (do that tren may nay) ##########')
net = M.FetalQRSTCN(); net.eval()
ntr = sum(p.numel() for p in net.parameters())
nbuf = sum(b.numel() for b in net.buffers())
sz = os.path.getsize(os.path.join(ROOT, 'model', 'checkpoints', 'fetalqrs_tcn_fold_r01.pt')) / 1e6
x = torch.randn(1, 2, 1000)
with torch.no_grad():
    for _ in range(5): net(x)
    t0 = time.perf_counter()
    for _ in range(50): net(x)
    dt = (time.perf_counter() - t0) / 50
print(f'  tham so huan luyen duoc : {ntr:,}')
print(f'  buffer BatchNorm        : {nbuf:,}')
print(f'  file checkpoint         : {sz:.2f} MB')
print(f'  do tre 1 cua so 4 s CPU : {dt*1000:.2f} ms  (he so thoi gian thuc {4.0/dt:.0f}x)')
import platform; print(f'  may: {platform.processor()[:60]}')
