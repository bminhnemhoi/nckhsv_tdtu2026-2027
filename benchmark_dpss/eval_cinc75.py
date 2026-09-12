# -*- coding: utf-8 -*-
"""
GIAI DOAN 1 muc 8 -- danh gia zero-shot TOAN BO 75 ban ghi CinC 2013 set-a (a01..a75).

Truoc day chi danh gia 10 ban ghi (blind_lead.json / eval_22.json). Day la lan dau chay du 75.

Hai mo hinh, cung mot pipeline, cung mot bo du lieu:
    model/checkpoints/fetalqrs_tcn_production.pt     -- train tren 5 san phu PhysioNet  (goi la m5)
    model/checkpoints/fetalqrs_tcn_22_production.pt  -- train tren 22 san phu doc lap   (goi la m22)
Ca hai deu CHUA TUNG THAY CinC 2013 -> zero-shot xuyen he ghi.

Pipeline (sao chep nguyen tu benchmark_dpss/eval_22.py::run_cinc, khong doi tham so):
    wfdb.rdrecord -> 4 kenh (AECG1..4, 1000 Hz) -> M.preprocess (10-60 Hz, resample 250 Hz)
    -> M.cancel_maternal -> robust_scale(residual), robust_scale(x) -> M.probability_series
    -> M.pick_peaks(nguong cua checkpoint) -> x4 ve 1000 Hz -> M.match_events(+/-50 ms)
Nhan chuan: <rec>.fqrs (wfdb.rdann), don vi mau @1000 Hz.

BON QUY TAC CHON KENH duoc bao cao rieng:
    psd    -- mu nhan, diem PSD Power-MF tren phan du chua chuan hoa (SO CHINH, xem ghi chu ben duoi)
    lead0  -- kenh 0 co dinh (AECG1)
    mean4  -- trung binh F1 cua 4 kenh
    oracle -- kenh tot nhat chon HAU KIEM bang nhan that (chan tren, KHONG dung duoc trong thuc te)

GHI CHU TRUNG THUC BAT BUOC: con so 90,34 tung bao cao cho CinC 2013 la quy tac "kenh 0 co dinh",
va kenh 0 duoc chon HAU KIEM sau khi thay quy tac PSD that bai tren mien nay. Quy tac mu nhan that su
(PSD) cho con so thap hon nhieu. SO CHINH phai bao cao la PSD.

HAI BIEN THE TAP BAN GHI, KHAI BAO TRUOC KHI CHAY:
    75 ban ghi -- toan bo set-a
    68 ban ghi -- loai 7 ban ghi bi ghi nhan la CHU THICH SAI trong y van:
                  a33 a38 a47 a52 a54 a71 a74
                  (Behar J, Oster J, Clifford GD. Non-invasive FECG extraction from a set of abdominal
                   sensors. Computing in Cardiology 2013;40:297-300; danh sach nay duoc truyen lai qua
                   Zhong et al. 2018.)
    Danh sach nay CO DINH TRONG MA NGUON TRUOC KHI CHAY, khong chon sau khi thay ket qua.

Thong ke o MUC BAN GHI (don vi = ban ghi, khong phai cap ban-ghi-x-kenh):
    hieu so m22 - m5, KTC 95% bootstrap 10000 lan (lay mau lai BAN GHI), KTC 95% kieu t,
    Wilcoxon ghep cap, sign test, Cliff delta, phan bo >=90 / 50-90 / <50.

Chay:  python benchmark_dpss/eval_cinc75.py
       python benchmark_dpss/eval_cinc75.py --limit 5      (thu nhanh)
Ket qua: benchmark_dpss/eval_cinc75.json, eval_cinc75_log.txt, eval_cinc75_hist.png
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

OUT_JSON = os.path.join(HERE, 'eval_cinc75.json')
OUT_LOG = os.path.join(HERE, 'eval_cinc75_log.txt')
OUT_PNG = os.path.join(HERE, 'eval_cinc75_hist.png')

TOL_MS = 50; FHR_BAND = (1.8, 3.0); Q = CFG['fs_in'] // CFG['fs']
N_BOOT = 10000; SEED = 0
# KHAI BAO TRUOC: 7 ban ghi chu thich sai (Behar/Oster/Clifford CinC 2013;40:297-300 qua Zhong 2018)
BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')
RULES = ('psd', 'lead0', 'mean4', 'oracle')
RULE_LABEL = dict(psd='PSD mu nhan (SO CHINH)', lead0='kenh 0 co dinh', mean4='TB 4 kenh', oracle='oracle (chan tren)')
MODELS = [('m5', 'fetalqrs_tcn_production.pt', 'train 5 san phu PhysioNet'),
          ('m22', 'fetalqrs_tcn_22_production.pt', 'train 22 san phu doc lap')]


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
    m['n_det'] = int(len(det1000)); m['n_ref'] = int(len(fq1000))
    m['bias_ms'] = signed_bias(det1000, fq1000)
    return m


def load_net(path):
    b = torch.load(path, map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
    return net, float(b['threshold'])


def prep_record(D, rec):
    """-> list 4 x (r_s, x_s, psd), gt @1000 Hz"""
    r_ = wfdb.rdrecord(os.path.join(D, rec))
    ann = wfdb.rdann(os.path.join(D, rec), 'fqrs')
    fs0 = r_.fs
    gt = (np.asarray(ann.sample, float) * (1000.0 / fs0)).round().astype(int)
    leads = []
    for lead in range(min(4, r_.p_signal.shape[1])):
        s = np.nan_to_num(r_.p_signal[:, lead])
        if fs0 != 1000:
            s = sg.resample_poly(s, 1000, int(fs0))
        x = M.preprocess(s, 1000, CFG)
        rr, _ = M.cancel_maternal(x, CFG)
        leads.append((M.robust_scale(rr).astype(np.float32), M.robust_scale(x).astype(np.float32), psd_score(rr)))
    del r_
    return leads, gt, float(fs0)


def run_model(net, thr, leads, gt):
    per = []
    for r_s, x_s, _ in leads:
        p = M.probability_series(net, r_s, x_s, CFG)
        det = M.pick_peaks(p, thr, CFG).astype(np.int64) * Q
        per.append(score(det, gt))
    f1s = [e['F1'] for e in per]
    psd_lead = int(np.argmax([l[2] for l in leads]))
    oracle_lead = int(np.argmax(f1s))
    return dict(per_lead={str(i): per[i] for i in range(len(per))},
                psd_lead=psd_lead, oracle_lead=oracle_lead,
                F1_psd=float(f1s[psd_lead]), F1_lead0=float(f1s[0]),
                F1_mean4=float(np.mean(f1s)), F1_oracle=float(max(f1s)),
                Se_psd=float(per[psd_lead]['Se']), PPV_psd=float(per[psd_lead]['PPV']),
                Se_lead0=float(per[0]['Se']), PPV_lead0=float(per[0]['PPV']),
                jitter_psd=float(per[psd_lead]['jitter_ms']), jitter_lead0=float(per[0]['jitter_ms']),
                bias_psd=float(per[psd_lead]['bias_ms']), bias_lead0=float(per[0]['bias_ms']),
                TP_psd=int(per[psd_lead]['TP']), FP_psd=int(per[psd_lead]['FP']), FN_psd=int(per[psd_lead]['FN']),
                TP_lead0=int(per[0]['TP']), FP_lead0=int(per[0]['FP']), FN_lead0=int(per[0]['FN']))


# ------------------------------------------------------------------ thong ke muc ban ghi
def cliffs_delta(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    gt = sum(int(np.sum(xi > y)) for xi in x); lt = sum(int(np.sum(xi < y)) for xi in x)
    d = (gt - lt) / (len(x) * len(y)); ad = abs(d)
    mag = 'khong dang ke' if ad < .147 else ('nho' if ad < .330 else ('trung binh' if ad < .474 else 'lon'))
    return dict(delta=float(d), magnitude=mag)


def boot_ci_paired(a, b, n_boot=N_BOOT, seed=SEED):
    """lay mau lai BAN GHI (cum) -> KTC percentile cho trung binh hieu so a-b."""
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b; n = len(d)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = d[idx].mean(1)
    return dict(mean_diff=float(d.mean()),
                ci95_bootstrap=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                n_boot=int(n_boot))


def ci_t(d, alpha=.05):
    d = np.asarray(d, float); n = len(d)
    if n < 2: return [float('nan'), float('nan')]
    se = d.std(ddof=1) / np.sqrt(n); h = tdist.ppf(1 - alpha / 2, n - 1) * se
    return [float(d.mean() - h), float(d.mean() + h)]


def dist(v):
    v = np.asarray(v, float)
    return dict(n=int(len(v)), ge90=int((v >= 90).sum()),
                mid50_90=int(((v >= 50) & (v < 90)).sum()), lt50=int((v < 50).sum()),
                eq100=int((v >= 99.999).sum()), eq0=int((v <= 1e-9).sum()))


def summ(v):
    v = np.asarray(v, float)
    return dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                median=float(np.median(v)), min=float(v.min()), max=float(v.max()), n=int(len(v)))


def compare(rows, rule):
    a = [r['m22'][f'F1_{rule}'] if rule != 'mean4' else r['m22']['F1_mean4'] for r in rows]
    b = [r['m5'][f'F1_{rule}'] if rule != 'mean4' else r['m5']['F1_mean4'] for r in rows]
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b
    nz = int(np.sum(np.abs(d) > 1e-9))
    try:
        w = float(wilcoxon(a, b, zero_method='wilcox').pvalue) if nz else 1.0
    except ValueError:
        w = 1.0
    wins = int(np.sum(d > 1e-9)); losses = int(np.sum(d < -1e-9))
    sp = float(binomtest(wins, wins + losses, .5).pvalue) if (wins + losses) else 1.0
    out = dict(rule=rule, m22=summ(a), m5=summ(b),
               dist_m22=dist(a), dist_m5=dist(b),
               wilcoxon_p=w, sign_test_p=sp, wins_m22=wins, losses_m22=losses,
               ties=int(len(d) - wins - losses),
               cliffs_delta=cliffs_delta(a, b), ci95_t=ci_t(d))
    out.update(boot_ci_paired(a, b))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0, help='chi chay N ban ghi dau (thu nhanh)')
    a = ap.parse_args()
    sys.stdout = Tee(OUT_LOG)
    t0 = time.time()
    D = cinc2013_dir()
    if D is None:
        raise SystemExit('Khong tim thay CinC 2013.')
    recs = sorted({f[:-4] for f in os.listdir(D) if f.endswith('.dat')})
    have_ann = [r for r in recs if os.path.isfile(os.path.join(D, r + '.fqrs'))]
    if a.limit:
        have_ann = have_ann[:a.limit]
    print(f'===== EVAL CinC 2013 set-a FULL | {datetime.datetime.now():%Y-%m-%d %H:%M:%S} | '
          f'{platform.platform()} | torch {torch.__version__} | {torch.get_num_threads()} luong =====')
    print(f'thu muc {D}: {len(recs)} ban ghi .dat, {len(have_ann)} co nhan .fqrs')
    print(f'KHAI BAO TRUOC: bien the 68 ban ghi loai {list(BAD_ANN)} (chu thich sai, Behar/Oster/Clifford CinC 2013;40:297-300)')
    print(f'SO CHINH = quy tac PSD mu nhan. Kenh 0 co dinh la quy tac chon HAU KIEM -> chi bao cao lam tham chieu.\n')

    nets = {}
    for key, fn, note in MODELS:
        p = checkpoint(fn)
        if not os.path.isfile(p):
            raise SystemExit(f'thieu checkpoint {p}')
        net, thr = load_net(p)
        nets[key] = (net, thr)
        print(f'   {key:<4} {fn:<34} nguong {thr:.2f}  ({note})')
    print()

    rows = []
    for i, rec in enumerate(have_ann, 1):
        tr = time.time()
        leads, gt, fs0 = prep_record(D, rec)
        row = dict(record=rec, n_ref=int(len(gt)), n_leads=len(leads), fs=fs0,
                   bad_annotation=rec in BAD_ANN)
        for key in ('m5', 'm22'):
            net, thr = nets[key]
            row[key] = run_model(net, thr, leads, gt)
            row[key]['threshold'] = thr
        rows.append(row)
        print(f'[{i:2d}/{len(have_ann)}] {rec}{" *" if rec in BAD_ANN else "  "} nhan {len(gt):4d} | '
              f'm5  PSD A{row["m5"]["psd_lead"]+1} {row["m5"]["F1_psd"]:6.2f} k0 {row["m5"]["F1_lead0"]:6.2f} '
              f'TB4 {row["m5"]["F1_mean4"]:6.2f} orc {row["m5"]["F1_oracle"]:6.2f} | '
              f'm22 PSD A{row["m22"]["psd_lead"]+1} {row["m22"]["F1_psd"]:6.2f} k0 {row["m22"]["F1_lead0"]:6.2f} '
              f'TB4 {row["m22"]["F1_mean4"]:6.2f} orc {row["m22"]["F1_oracle"]:6.2f} | {time.time()-tr:.1f}s')
        del leads
        if i % 10 == 0:
            gc.collect()
            json.dump(dict(status='dang chay', n_done=i, records=rows), open(OUT_JSON, 'w'), indent=1, default=float)

    # ---------------------------------------------------------------- tong hop
    variants = {'75': rows, '68': [r for r in rows if not r['bad_annotation']]}
    out = dict(meta=dict(date=str(datetime.datetime.now()), dir=D, n_records=len(rows),
                         tolerance_ms=TOL_MS, n_boot=N_BOOT, seed=SEED,
                         bad_annotation_excluded=list(BAD_ANN),
                         bad_annotation_source='Behar J, Oster J, Clifford GD. CinC 2013;40:297-300 (qua Zhong 2018)',
                         models={k: dict(file=f, note=n, threshold=nets[k][1]) for k, f, n in MODELS},
                         main_rule='psd',
                         note_lead0='Kenh 0 co dinh la quy tac chon HAU KIEM (sau khi thay PSD that bai). '
                                    'Khong phai quy tac mu nhan. SO CHINH la PSD.',
                         cfg={k: (list(v) if isinstance(v, tuple) else v) for k, v in CFG.items()},
                         minutes=None),
               records=rows, variants={})

    for vk, vrows in variants.items():
        v = dict(n=len(vrows), records=[r['record'] for r in vrows], rules={})
        for rule in RULES:
            v['rules'][rule] = compare(vrows, rule)
        # micro (gop TP/FP/FN) cho hai quy tac chinh
        for rule in ('psd', 'lead0'):
            for key in ('m5', 'm22'):
                TP = sum(r[key][f'TP_{rule}'] for r in vrows)
                FP = sum(r[key][f'FP_{rule}'] for r in vrows)
                FN = sum(r[key][f'FN_{rule}'] for r in vrows)
                se = TP / (TP + FN) * 100 if TP + FN else 0.0
                ppv = TP / (TP + FP) * 100 if TP + FP else 0.0
                v.setdefault('micro', {})[f'{key}_{rule}'] = dict(
                    TP=TP, FP=FP, FN=FN, Se=se, PPV=ppv, F1=2 * se * ppv / (se + ppv) if se + ppv else 0.0)
        # quy tac PSD co chon dung kenh oracle khong?
        for key in ('m5', 'm22'):
            hit = sum(1 for r in vrows if r[key]['psd_lead'] == r[key]['oracle_lead'])
            hit0 = sum(1 for r in vrows if r[key]['oracle_lead'] == 0)
            v.setdefault('psd_vs_oracle', {})[key] = dict(
                psd_equals_oracle=hit, n=len(vrows), pct=100.0 * hit / max(len(vrows), 1),
                oracle_is_lead0=hit0, pct_oracle_lead0=100.0 * hit0 / max(len(vrows), 1))
        out['variants'][vk] = v

    # ---------------------------------------------------------------- in bang
    for vk in ('75', '68'):
        v = out['variants'][vk]
        print(f'\n\n===== BIEN THE {vk} BAN GHI (n = {v["n"]}) =====')
        print(f'{"quy tac":<26} {"m5":>7} {"sd":>6} {"m22":>7} {"sd":>6} {"hieu":>7} '
              f'{"KTC95 bootstrap":>20} {"KTC95 t":>20} {"p Wil":>8} {"p sign":>8} {"Cliff":>7}')
        for rule in RULES:
            c = v['rules'][rule]
            print(f'{RULE_LABEL[rule]:<26} {c["m5"]["mean"]:7.2f} {c["m5"]["sd"]:6.2f} '
                  f'{c["m22"]["mean"]:7.2f} {c["m22"]["sd"]:6.2f} {c["mean_diff"]:+7.2f} '
                  f'[{c["ci95_bootstrap"][0]:+7.2f};{c["ci95_bootstrap"][1]:+7.2f}] '
                  f'[{c["ci95_t"][0]:+7.2f};{c["ci95_t"][1]:+7.2f}] '
                  f'{c["wilcoxon_p"]:8.2e} {c["sign_test_p"]:8.2e} {c["cliffs_delta"]["delta"]:+7.3f}')
        print(f'\n{"phan bo ban ghi":<26} {">=90":>6} {"50-90":>6} {"<50":>6} {"=100":>6} {"=0":>6}')
        for rule in RULES:
            c = v['rules'][rule]
            for key in ('m5', 'm22'):
                dd = c[f'dist_{key}']
                print(f'{RULE_LABEL[rule][:20]+" / "+key:<26} {dd["ge90"]:6d} {dd["mid50_90"]:6d} '
                      f'{dd["lt50"]:6d} {dd["eq100"]:6d} {dd["eq0"]:6d}')
        print(f'\nmicro (gop TP/FP/FN toan bo ban ghi):')
        for k, m in v['micro'].items():
            print(f'   {k:<12} TP {m["TP"]:6d} FP {m["FP"]:6d} FN {m["FN"]:6d}  '
                  f'Se {m["Se"]:6.2f} PPV {m["PPV"]:6.2f} F1 {m["F1"]:6.2f}')
        print(f'\nquy tac PSD co trung kenh oracle khong:')
        for k, m in v['psd_vs_oracle'].items():
            print(f'   {k:<4} PSD == oracle {m["psd_equals_oracle"]:3d}/{m["n"]} ({m["pct"]:5.1f}%)  |  '
                  f'oracle la kenh 0: {m["oracle_is_lead0"]:3d}/{m["n"]} ({m["pct_oracle_lead0"]:5.1f}%)')

    out['meta']['minutes'] = (time.time() - t0) / 60
    json.dump(out, open(OUT_JSON, 'w'), indent=1, default=float)
    make_fig(out)
    print(f'\nDONE {out["meta"]["minutes"]:.1f} phut -> {OUT_JSON}, {OUT_LOG}, {OUT_PNG}')


def make_fig(out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = out['records']
    bins = np.arange(0, 105, 5)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    for ax, rule, title in zip(axes, ('psd', 'lead0'),
                               ('Quy tac PSD mu nhan (SO CHINH)', 'Kenh 0 co dinh (chon hau kiem)')):
        a5 = [r['m5'][f'F1_{rule}'] for r in rows]
        a22 = [r['m22'][f'F1_{rule}'] for r in rows]
        ax.hist(a5, bins=bins, alpha=.55, color='#9e9e9e', edgecolor='#555', label=f'm5  (TB {np.mean(a5):.1f})')
        ax.hist(a22, bins=bins, alpha=.55, color='#1f77b4', edgecolor='#0d3d63', label=f'm22 (TB {np.mean(a22):.1f})')
        ax.axvline(50, color='#c62828', ls='--', lw=1)
        ax.axvline(90, color='#2e7d32', ls='--', lw=1)
        ax.set_title(f'{title}\n{len(rows)} ban ghi CinC 2013 set-a, zero-shot')
        ax.set_xlabel('F1 tung ban ghi (%)'); ax.set_ylabel('so ban ghi')
        ax.legend(fontsize=8); ax.grid(alpha=.25, axis='y')
    fig.suptitle('CinC 2013 set-a: phan bo F1 theo ban ghi, mo hinh 5 vs 22 san phu', fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=140)
    plt.close(fig)


if __name__ == '__main__':
    main()
