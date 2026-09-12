# -*- coding: utf-8 -*-
"""
GIAI DOAN 1 muc 9 (phan danh gia) -- ABLATION BO B1.

Danh gia mo hinh 12 chu the (model/train_12.py -- CHI nhan dien cuc da dau, KHONG he thay B1) tren:
  (a) 10 chu the B1 Silesia (thai ky, nhan gian tiep) -- CHUA TUNG THAY.
      Dat canh mo hinh 22 chu the (97,15 PSD, fold checkpoint -- B1 duoc giu lai) va
      mo hinh 5 chu the (93,30 PSD, production_5 -- chua tung thay Silesia).
      So lieu m22/m5 lay tu benchmark_dpss/eval_22.json (per-subject), khong tinh lai.
  (b) 75 ban ghi CinC 2013 set-a -- dat canh eval_cinc75.json (m5, m22).

CAU HOI: cai thien 5 -> 22 chu the la do THEM DU LIEU hay do HOC PHONG CACH NHAN B1?
  * Neu m12 ~ m22 tren B1  -> phong cach nhan B1 KHONG phai nguyen nhan (them du lieu da dau la du).
  * Neu m12 ~ m5  << m22   -> phan lon loi ich la do HOC THEO NHAN B1 (thien lech sap nhap du lieu).

Chay:  python benchmark_dpss/eval_12.py                (B1 + CinC 75)
       python benchmark_dpss/eval_12.py --skip-cinc
       python benchmark_dpss/eval_12.py --ckpt fetalqrs_tcn_12_fold_01.pt   (neu chua co production)
Ket qua: benchmark_dpss/eval_12.json, eval_12_log.txt
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, argparse, importlib.util, datetime, platform, gc
import numpy as np, torch, wfdb
from scipy import signal as sg
from scipy.stats import wilcoxon, binomtest, t as tdist

torch.set_num_threads(int(os.environ.get('FQRS_THREADS', 3)))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _paths import cinc2013_dir, checkpoint


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


M = _load('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py')); CFG = M.CFG
L = _load('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))

OUT_JSON = os.path.join(HERE, 'eval_12.json')
OUT_LOG = os.path.join(HERE, 'eval_12_log.txt')
EVAL22_JSON = os.path.join(HERE, 'eval_22.json')
CINC75_JSON = os.path.join(HERE, 'eval_cinc75.json')

B1 = [f'B1_{i:02d}' for i in range(1, 11)]
LEADS = (1, 2, 3, 4)
TOL_MS = 50; FHR_BAND = (1.8, 3.0); Q = CFG['fs_in'] // CFG['fs']
N_BOOT = 10000; SEED = 0
BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')
# quet nguong PHU (mien phi: dung lai chuoi xac suat) -- de kiem tra ket luan co phu thuoc nguong khong.
# 0,45 = nguong production_5 ; 0,75 = nguong production_22 ; nguong chinh = nguong cua checkpoint 12.
THR_SWEEP = (0.45, 0.55, 0.65, 0.75, 0.80)


class Tee:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.o = sys.stdout
    def write(self, s):
        self.o.write(s); self.f.write(s); self.f.flush()
    def flush(self):
        self.o.flush(); self.f.flush()


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


def score(det1000, fq1000):
    m = M.match_events(det1000, fq1000, CFG['fs_in'], TOL_MS)
    m['n_det'] = int(len(det1000)); m['n_ref'] = int(len(fq1000)); m['bias_ms'] = signed_bias(det1000, fq1000)
    return m


def load_net(path):
    b = torch.load(path, map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
    return net, float(b['threshold']), b


def cliffs_delta(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    gt = sum(int(np.sum(xi > y)) for xi in x); lt = sum(int(np.sum(xi < y)) for xi in x)
    d = (gt - lt) / (len(x) * len(y)); ad = abs(d)
    mag = 'khong dang ke' if ad < .147 else ('nho' if ad < .330 else ('trung binh' if ad < .474 else 'lon'))
    return dict(delta=float(d), magnitude=mag)


def ci_t(d, alpha=.05):
    d = np.asarray(d, float); n = len(d)
    if n < 2: return [float('nan'), float('nan')]
    se = d.std(ddof=1) / np.sqrt(n); h = tdist.ppf(1 - alpha / 2, n - 1) * se
    return [float(d.mean() - h), float(d.mean() + h)]


def paired_stats(a, b, name_a, name_b):
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b; n = len(d)
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(N_BOOT, n)); boots = d[idx].mean(1)
    try:
        w = float(wilcoxon(a, b, zero_method='wilcox').pvalue) if np.any(np.abs(d) > 1e-9) else 1.0
    except ValueError:
        w = 1.0
    wins = int(np.sum(d > 1e-9)); losses = int(np.sum(d < -1e-9))
    sp = float(binomtest(wins, wins + losses, .5).pvalue) if (wins + losses) else 1.0
    return dict(a=name_a, b=name_b, n=int(n),
                mean_a=float(a.mean()), sd_a=float(a.std(ddof=1)) if n > 1 else 0.0,
                mean_b=float(b.mean()), sd_b=float(b.std(ddof=1)) if n > 1 else 0.0,
                mean_diff=float(d.mean()),
                ci95_bootstrap=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                ci95_t=ci_t(d), wilcoxon_p=w, sign_test_p=sp,
                wins=wins, losses=losses, ties=int(n - wins - losses),
                cliffs_delta=cliffs_delta(a, b))


def dist(v):
    v = np.asarray(v, float)
    return dict(n=int(len(v)), ge90=int((v >= 90).sum()), mid50_90=int(((v >= 50) & (v < 90)).sum()),
                lt50=int((v < 50).sum()))


def summ(v):
    v = np.asarray(v, float)
    return dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                median=float(np.median(v)), min=float(v.min()), max=float(v.max()), n=int(len(v)))


# ------------------------------------------------------------------ B1
def run_b1(net, thr):
    rows = {}
    for tag in B1:
        t0 = time.time()
        sig, _, mt = L.load(tag)
        fq1000 = np.asarray(mt['fqrs_all'], int)
        per = {}; psds = {}; sweep = {f'{t:.2f}': {} for t in THR_SWEEP}
        for lead in LEADS:
            x = M.preprocess(sig[lead - 1], CFG['fs_in'], CFG)
            rr, _ = M.cancel_maternal(x, CFG)
            psds[lead] = psd_score(rr)
            p = M.probability_series(net, M.robust_scale(rr).astype(np.float32),
                                     M.robust_scale(x).astype(np.float32), CFG)
            det = M.pick_peaks(p, thr, CFG).astype(np.int64) * Q
            per[lead] = score(det, fq1000)
            for t in THR_SWEEP:                                   # mien phi: dung lai chuoi xac suat
                d2 = M.pick_peaks(p, float(t), CFG).astype(np.int64) * Q
                sweep[f'{t:.2f}'][lead] = float(M.match_events(d2, fq1000, CFG['fs_in'], TOL_MS)['F1'])
        del sig
        gc.collect()
        f1s = [per[l]['F1'] for l in LEADS]
        bl = max(LEADS, key=lambda l: psds[l])
        sweep_out = {k: dict(F1_psd=v[bl], F1_mean4=float(np.mean([v[l] for l in LEADS]))) for k, v in sweep.items()}
        rows[tag] = dict(record=tag, psd_lead=int(bl), threshold=float(thr), n_ref=int(len(fq1000)),
                         per_lead={f'A{l}': per[l] for l in LEADS},
                         F1_psd=float(per[bl]['F1']), Se_psd=float(per[bl]['Se']), PPV_psd=float(per[bl]['PPV']),
                         jitter_psd=float(per[bl]['jitter_ms']), bias_psd=float(per[bl]['bias_ms']),
                         F1_mean4=float(np.mean(f1s)), F1_oracle=float(max(f1s)),
                         bias_mean4=float(np.nanmean([per[l]['bias_ms'] for l in LEADS])),
                         sweep=sweep_out)
        print(f'   {tag}  PSD A{bl} F1 {rows[tag]["F1_psd"]:6.2f} | TB4 {rows[tag]["F1_mean4"]:6.2f} | '
              f'orc {rows[tag]["F1_oracle"]:6.2f} | kenh ' +
              ' '.join(f'{per[l]["F1"]:6.2f}' for l in LEADS) +
              f' | lech PSD {rows[tag]["bias_psd"]:+.1f} ms | {time.time()-t0:.0f}s')
    return rows


# ------------------------------------------------------------------ CinC
def run_cinc(net, thr, limit=0):
    D = cinc2013_dir()
    recs = sorted({f[:-4] for f in os.listdir(D) if f.endswith('.dat')
                   and os.path.isfile(os.path.join(D, f[:-4] + '.fqrs'))})
    if limit: recs = recs[:limit]
    rows = {}
    for i, rec in enumerate(recs, 1):
        t0 = time.time()
        r_ = wfdb.rdrecord(os.path.join(D, rec)); ann = wfdb.rdann(os.path.join(D, rec), 'fqrs')
        fs0 = r_.fs; gt = (np.asarray(ann.sample, float) * (1000.0 / fs0)).round().astype(int)
        per = []; psds = []; sweep = {f'{t:.2f}': [] for t in THR_SWEEP}
        for lead in range(min(4, r_.p_signal.shape[1])):
            s = np.nan_to_num(r_.p_signal[:, lead])
            if fs0 != 1000: s = sg.resample_poly(s, 1000, int(fs0))
            x = M.preprocess(s, 1000, CFG); rr, _ = M.cancel_maternal(x, CFG)
            psds.append(psd_score(rr))
            p = M.probability_series(net, M.robust_scale(rr).astype(np.float32),
                                     M.robust_scale(x).astype(np.float32), CFG)
            det = M.pick_peaks(p, thr, CFG).astype(np.int64) * Q
            per.append(score(det, gt))
            for t in THR_SWEEP:                                   # mien phi: dung lai chuoi xac suat
                d2 = M.pick_peaks(p, float(t), CFG).astype(np.int64) * Q
                sweep[f'{t:.2f}'].append(float(M.match_events(d2, gt, CFG['fs_in'], TOL_MS)['F1']))
        del r_
        f1s = [e['F1'] for e in per]; bl = int(np.argmax(psds))
        sweep_out = {k: dict(F1_psd=v[bl], F1_lead0=v[0], F1_mean4=float(np.mean(v))) for k, v in sweep.items()}
        rows[rec] = dict(record=rec, psd_lead=bl, oracle_lead=int(np.argmax(f1s)), n_ref=int(len(gt)),
                         bad_annotation=rec in BAD_ANN,
                         per_lead={str(k): per[k] for k in range(len(per))},
                         F1_psd=float(f1s[bl]), F1_lead0=float(f1s[0]),
                         F1_mean4=float(np.mean(f1s)), F1_oracle=float(max(f1s)),
                         TP_psd=int(per[bl]['TP']), FP_psd=int(per[bl]['FP']), FN_psd=int(per[bl]['FN']),
                         TP_lead0=int(per[0]['TP']), FP_lead0=int(per[0]['FP']), FN_lead0=int(per[0]['FN']),
                         sweep=sweep_out)
        print(f'   [{i:2d}/{len(recs)}] {rec}{" *" if rec in BAD_ANN else "  "} PSD A{bl+1} {f1s[bl]:6.2f} '
              f'k0 {f1s[0]:6.2f} TB4 {np.mean(f1s):6.2f} orc {max(f1s):6.2f} | {time.time()-t0:.1f}s')
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', default='fetalqrs_tcn_12_production.pt')
    ap.add_argument('--skip-cinc', action='store_true')
    ap.add_argument('--skip-b1', action='store_true')
    ap.add_argument('--limit-cinc', type=int, default=0)
    ap.add_argument('--out', default='', help='hau to rieng cho file ra (de chay song song B1 va CinC)')
    a = ap.parse_args()
    global OUT_JSON, OUT_LOG
    if a.out:
        OUT_JSON = os.path.join(HERE, f'eval_12_{a.out}.json')
        OUT_LOG = os.path.join(HERE, f'eval_12_{a.out}_log.txt')
    sys.stdout = Tee(OUT_LOG)
    t0 = time.time()
    p = checkpoint(a.ckpt)
    if not os.path.isfile(p):
        raise SystemExit(f'thieu checkpoint {p} -- chay model/train_12.py truoc')
    net, thr, blob = load_net(p)
    print(f'===== EVAL MO HINH 12 (ABLATION BO B1) | {datetime.datetime.now():%Y-%m-%d %H:%M:%S} | '
          f'{platform.platform()} | {torch.get_num_threads()} luong =====')
    print(f'checkpoint {a.ckpt}  nguong {thr:.2f}  train tren {blob.get("trained_on", blob.get("train_subjects"))}')
    out = dict(meta=dict(date=str(datetime.datetime.now()), checkpoint=a.ckpt, threshold=thr,
                         trained_on=blob.get('trained_on', blob.get('train_subjects')),
                         tolerance_ms=TOL_MS, n_boot=N_BOOT, seed=SEED,
                         question='cai thien 5->22 la THEM DU LIEU hay HOC PHONG CACH NHAN B1?'))

    # ---------------------------------------------------------------- (a) B1
    if not a.skip_b1:
        print(f'\n-- (a) 10 chu the B1 Silesia (thai ky, nhan gian tiep), mo hinh 12 CHUA TUNG THAY --')
        b1 = run_b1(net, thr)
        e22 = json.load(open(EVAL22_JSON, encoding='utf-8'))['subjects']
        ref = {t: dict(m22_psd=e22[t]['model_22']['F1_psd'], m22_mean4=e22[t]['model_22']['F1_mean4'],
                       m5_psd=e22[t]['model_5']['F1_psd'], m5_mean4=e22[t]['model_5']['F1_mean4'])
               for t in B1}
        v12p = [b1[t]['F1_psd'] for t in B1]; v12m = [b1[t]['F1_mean4'] for t in B1]
        v22p = [ref[t]['m22_psd'] for t in B1]; v22m = [ref[t]['m22_mean4'] for t in B1]
        v5p = [ref[t]['m5_psd'] for t in B1]; v5m = [ref[t]['m5_mean4'] for t in B1]
        b1out = dict(records=b1, reference=ref,
                     summary=dict(m12_psd=summ(v12p), m22_psd=summ(v22p), m5_psd=summ(v5p),
                                  m12_mean4=summ(v12m), m22_mean4=summ(v22m), m5_mean4=summ(v5m)),
                     dist=dict(m12_psd=dist(v12p), m22_psd=dist(v22p), m5_psd=dist(v5p)),
                     tests=dict(psd_m12_vs_m5=paired_stats(v12p, v5p, 'm12', 'm5'),
                                psd_m12_vs_m22=paired_stats(v12p, v22p, 'm12', 'm22'),
                                psd_m22_vs_m5=paired_stats(v22p, v5p, 'm22', 'm5'),
                                mean4_m12_vs_m5=paired_stats(v12m, v5m, 'm12', 'm5'),
                                mean4_m12_vs_m22=paired_stats(v12m, v22m, 'm12', 'm22')))
        b1out['threshold_sweep'] = {k: dict(F1_psd=float(np.mean([b1[t]['sweep'][k]['F1_psd'] for t in B1])),
                                            F1_mean4=float(np.mean([b1[t]['sweep'][k]['F1_mean4'] for t in B1])))
                                    for k in b1[B1[0]]['sweep']}
        out['B1'] = b1out
        print(f'\n   {"chu the":<8} {"m5":>7} {"m12":>7} {"m22":>7}   (F1 kenh PSD)')
        for t in B1:
            print(f'   {t:<8} {ref[t]["m5_psd"]:7.2f} {b1[t]["F1_psd"]:7.2f} {ref[t]["m22_psd"]:7.2f}')
        print(f'   {"TB":<8} {np.mean(v5p):7.2f} {np.mean(v12p):7.2f} {np.mean(v22p):7.2f}')
        print(f'   {"TB4 kenh":<8} {np.mean(v5m):7.2f} {np.mean(v12m):7.2f} {np.mean(v22m):7.2f}')
        for k, c in b1out['tests'].items():
            print(f'   {k:<20} hieu {c["mean_diff"]:+6.2f}  KTC95 boot [{c["ci95_bootstrap"][0]:+6.2f};'
                  f'{c["ci95_bootstrap"][1]:+6.2f}]  KTC95 t [{c["ci95_t"][0]:+6.2f};{c["ci95_t"][1]:+6.2f}]  '
                  f'p Wil {c["wilcoxon_p"]:.4f}  thang/thua {c["wins"]}/{c["losses"]}  '
                  f'Cliff {c["cliffs_delta"]["delta"]:+.3f}')
        print('   quet nguong (m12 tren B1, TB 10 chu the): ' +
              '  '.join(f'{k}: PSD {v["F1_psd"]:.2f} / TB4 {v["F1_mean4"]:.2f}'
                        for k, v in sorted(b1out['threshold_sweep'].items())))
        json.dump(out, open(OUT_JSON, 'w'), indent=1, default=float)

    # ---------------------------------------------------------------- (b) CinC 75
    if not a.skip_cinc:
        print(f'\n-- (b) CinC 2013 set-a, mo hinh 12 zero-shot --')
        cinc = run_cinc(net, thr, a.limit_cinc)
        c = dict(records=cinc)
        if os.path.isfile(CINC75_JSON):
            ref75 = json.load(open(CINC75_JSON, encoding='utf-8'))
            rr = {e['record']: e for e in ref75['records']}
            common = [k for k in cinc if k in rr]
            for vk, sel in (('75', common), ('68', [k for k in common if k not in BAD_ANN])):
                v = dict(n=len(sel), rules={})
                for rule in ('psd', 'lead0', 'mean4', 'oracle'):
                    a12 = [cinc[k][f'F1_{rule}'] for k in sel]
                    a22 = [rr[k]['m22'][f'F1_{rule}'] for k in sel]
                    a5 = [rr[k]['m5'][f'F1_{rule}'] for k in sel]
                    v['rules'][rule] = dict(m12=summ(a12), m22=summ(a22), m5=summ(a5),
                                            dist_m12=dist(a12), dist_m22=dist(a22), dist_m5=dist(a5),
                                            m12_vs_m5=paired_stats(a12, a5, 'm12', 'm5'),
                                            m12_vs_m22=paired_stats(a12, a22, 'm12', 'm22'))
                c[f'variant_{vk}'] = v
                print(f'\n   == CinC bien the {vk} ban ghi (n={len(sel)}) ==')
                print(f'   {"quy tac":<10} {"m5":>7} {"m12":>7} {"m22":>7} | {"m12-m5":>8} {"KTC95 boot":>20} '
                      f'{"p":>8} | {"m12-m22":>8} {"KTC95 boot":>20} {"p":>8}')
                for rule in ('psd', 'lead0', 'mean4', 'oracle'):
                    q = v['rules'][rule]
                    d5 = q['m12_vs_m5']; d22 = q['m12_vs_m22']
                    print(f'   {rule:<10} {q["m5"]["mean"]:7.2f} {q["m12"]["mean"]:7.2f} {q["m22"]["mean"]:7.2f} | '
                          f'{d5["mean_diff"]:+8.2f} [{d5["ci95_bootstrap"][0]:+8.2f};{d5["ci95_bootstrap"][1]:+8.2f}] '
                          f'{d5["wilcoxon_p"]:8.2e} | {d22["mean_diff"]:+8.2f} '
                          f'[{d22["ci95_bootstrap"][0]:+8.2f};{d22["ci95_bootstrap"][1]:+8.2f}] {d22["wilcoxon_p"]:8.2e}')
            for vk, sel in (('75', common), ('68', [k for k in common if k not in BAD_ANN])):
                sw = {k: dict(F1_psd=float(np.mean([cinc[t]['sweep'][k]['F1_psd'] for t in sel])),
                              F1_lead0=float(np.mean([cinc[t]['sweep'][k]['F1_lead0'] for t in sel])),
                              F1_mean4=float(np.mean([cinc[t]['sweep'][k]['F1_mean4'] for t in sel])))
                      for k in cinc[sel[0]]['sweep']}
                c[f'variant_{vk}']['threshold_sweep'] = sw
                print(f'   quet nguong (m12 tren CinC {vk}): ' +
                      '  '.join(f'{k}: PSD {v["F1_psd"]:.2f}' for k, v in sorted(sw.items())))
        out['cinc2013'] = c
    out['meta']['minutes'] = (time.time() - t0) / 60
    json.dump(out, open(OUT_JSON, 'w'), indent=1, default=float)
    print(f'\nDONE {out["meta"]["minutes"]:.1f} phut -> {OUT_JSON}')


if __name__ == '__main__':
    main()
