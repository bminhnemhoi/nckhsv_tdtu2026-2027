# -*- coding: utf-8 -*-
"""
Chon dao trinh MU NHAN theo mat do pho cong suat (PSD), theo Jaeger et al. Power-MF,
Physiol Meas 45(5):055009, 2024 -- chon kenh co dinh PSD cao nhat trong dai nhip tim thai
1,8-3,0 Hz (108-180 bpm). Quy tac nay KHONG dung nhan that, nen thay the duoc cach
"chon kenh tot nhat" vi pham liem chinh.

Chay tren ca ADFECGDB (5 ban ghi x 4 kenh) va CinC 2013 set-a (10 ban ghi x 4 kenh).
"""
import os, sys, json, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, torch, mne, wfdb
from scipy import signal as sg

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import adfecgdb_dir, cinc2013_dir
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG = M.CFG
FHR_BAND = (1.8, 3.0)          # 108-180 bpm, dung dai cua Power-MF


def psd_score(x250, fs=250):
    """dinh PSD lon nhat trong dai nhip thai, tinh tren duong bao nang luong sau khu me"""
    e = np.abs(sg.hilbert(x250 - np.mean(x250)))
    e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def pick_blind(residuals):
    """residuals: dict lead -> tin hieu du 250 Hz. Tra ve lead co PSD thai manh nhat."""
    return max(residuals, key=lambda l: psd_score(residuals[l]))


def match(det, gt, tol=50):
    gm = np.zeros(len(gt), bool); tp = 0; err = []
    for x in det:
        d = np.abs(gt - x); w = np.where((d <= tol) & (~gm))[0]
        if len(w):
            j = w[np.argmin(d[w])]; gm[j] = True; tp += 1; err.append(d[j])
    return tp, len(det) - tp, len(gt) - tp, (np.mean(err) if err else np.nan)


def f1(tp, fp, fn):
    return 200 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0


# ------------------------------------------------------------------ ADFECGDB
def run_adfecgdb():
    RAW = adfecgdb_dir()
    DPSS = {'r01': 4, 'r04': 4, 'r07': 4, 'r08': 4, 'r10': 1}
    rows = {}
    print('\n' + '=' * 92)
    print('ADFECGDB -- chon dao trinh MU NHAN bang PSD (Power-MF) so voi cac quy tac khac')
    print('=' * 92)
    print(f'{"rec":<5}{"PSD chon":>10}{"DPSS quy dinh":>15}{"F1 PSD":>10}{"F1 DPSS":>10}'
          f'{"F1 oracle":>11}{"F1 TB 4 kenh":>14}')
    for rec in DPSS:
        b = torch.load(os.path.join(ROOT, 'model', 'checkpoints', f'fetalqrs_tcn_fold_{rec}.pt'),
                       map_location='cpu', weights_only=False)
        net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
        thr = float(b['threshold'])
        raw = mne.io.read_raw_edf(os.path.join(RAW, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        gt = np.array(wfdb.rdann(os.path.join(RAW, rec), 'edf.qrs').sample)
        res, per = {}, {}
        for lead in (1, 2, 3, 4):
            x = M.preprocess(sig[lead], 1000, CFG); r, _ = M.cancel_maternal(x, CFG)
            res[lead] = r
            p = M.probability_series(net, M.robust_scale(r).astype(np.float32),
                                     M.robust_scale(x).astype(np.float32), CFG)
            det = M.pick_peaks(p, thr, CFG).astype(np.int64) * 4
            per[lead] = f1(*match(det, gt)[:3])
        bl = pick_blind(res)
        rows[rec] = dict(psd_lead=bl, dpss_lead=DPSS[rec], per_lead=per,
                         F1_psd=per[bl], F1_dpss=per[DPSS[rec]],
                         F1_oracle=max(per.values()), F1_mean=float(np.mean(list(per.values()))))
        print(f'{rec:<5}{"lead"+str(bl):>10}{"lead"+str(DPSS[rec]):>15}{per[bl]:>10.2f}'
              f'{per[DPSS[rec]]:>10.2f}{max(per.values()):>11.2f}{np.mean(list(per.values())):>14.2f}')
    g = lambda k: np.mean([v[k] for v in rows.values()])
    print('-' * 92)
    print(f'{"MACRO":<5}{"":>10}{"":>15}{g("F1_psd"):>10.2f}{g("F1_dpss"):>10.2f}'
          f'{g("F1_oracle"):>11.2f}{g("F1_mean"):>14.2f}')
    return rows


# ------------------------------------------------------------------ CinC 2013
def run_cinc():
    D = cinc2013_dir()
    if D is None:
        print('\n[bo qua CinC 2013: chua tai du lieu -- xem README]')
        return {}
    recs = sorted({f[:-4] for f in os.listdir(D) if f.endswith('.dat')})[:10]
    b = torch.load(os.path.join(ROOT, 'model', 'checkpoints', 'fetalqrs_tcn_production.pt'),
                   map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
    thr = float(b['threshold'])
    rows = {}
    print('\n' + '=' * 92)
    print('CinC 2013 set-a -- xuyen bo du lieu, khong tinh chinh')
    print('=' * 92)
    print(f'{"rec":<5}{"PSD chon":>10}{"F1 PSD":>10}{"F1 kenh 0":>12}{"F1 oracle":>11}{"F1 TB":>10}')
    for rec in recs:
        r_ = wfdb.rdrecord(os.path.join(D, rec)); ann = wfdb.rdann(os.path.join(D, rec), 'fqrs')
        fs0 = r_.fs; gt = (ann.sample * (1000.0 / fs0)).round().astype(int)
        res, per = {}, {}
        for lead in range(min(4, r_.p_signal.shape[1])):
            s = np.nan_to_num(r_.p_signal[:, lead])
            if fs0 != 1000:
                s = sg.resample_poly(s, 1000, int(fs0))
            x = M.preprocess(s, 1000, CFG); rr, _ = M.cancel_maternal(x, CFG)
            res[lead] = rr
            p = M.probability_series(net, M.robust_scale(rr).astype(np.float32),
                                     M.robust_scale(x).astype(np.float32), CFG)
            det = M.pick_peaks(p, thr, CFG).astype(np.int64) * 4
            per[lead] = f1(*match(det, gt)[:3])
        bl = pick_blind(res)
        rows[rec] = dict(psd_lead=bl, per_lead=per, F1_psd=per[bl], F1_lead0=per[0],
                         F1_oracle=max(per.values()), F1_mean=float(np.mean(list(per.values()))))
        print(f'{rec:<5}{"lead"+str(bl):>10}{per[bl]:>10.2f}{per[0]:>12.2f}'
              f'{max(per.values()):>11.2f}{np.mean(list(per.values())):>10.2f}')
    g = lambda k: np.mean([v[k] for v in rows.values()])
    print('-' * 92)
    print(f'{"MACRO":<5}{"":>10}{g("F1_psd"):>10.2f}{g("F1_lead0"):>12.2f}'
          f'{g("F1_oracle"):>11.2f}{g("F1_mean"):>10.2f}')
    return rows


if __name__ == '__main__':
    a = run_adfecgdb()
    c = run_cinc()
    json.dump(dict(adfecgdb=a, cinc=c), open(os.path.join(HERE, 'blind_lead.json'), 'w'), indent=1)
    print('\nda ghi blind_lead.json')
