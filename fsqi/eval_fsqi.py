# -*- coding: utf-8 -*-
"""
eval_fsqi.py -- thi nghiem dong gop C3: chi so chat luong tin hieu thai (fSQI) co du bao duoc
                loi cua FetalQRS-TCN khong, va dac trung topo co hon chi so co dien khong?

Quy trinh (moi con so trong results.json deu do that tu script nay):
  1. Pipeline chuan (blind_lead.py): preprocess -> cancel_maternal -> probability_series -> pick_peaks,
     tren TOAN BO ban ghi, ADFECGDB dung checkpoint fold dung (test_record = ban ghi), CinC 2013 set-a
     dung checkpoint production. 4 kenh bung moi ban ghi.
  2. Ghep mot-doi-mot tham lam (+/-50 ms) tren toan ban ghi (M.match_events), roi gan TP/FN theo vi tri
     nhan, FP theo vi tri phat hien vao tung doan 4 s (buoc 4 s, khong chong) -> F1 doan THAT.
     Bo doan khong co nhip nhan nao.
  3. Voi moi doan: 16 dac trung topo (fsqi.topo_features + sublevel_h0_features), 10 chi so co dien
     (fsqi.classical_features) + 2 chi so tin cay cua chinh mo hinh (xac suat tai dinh). Do thoi gian.
  4. Spearman rho(chi so, F1 doan) + bootstrap 95% (1000 lan, theo doan VA theo cum ban ghi x kenh).
  5. Bo phan loai "F1 doan < 80": HUAN LUYEN TREN ADFECGDB, KIEM THU TREN CinC. Learner (logistic /
     gradient boosting) chon bang LORO-CV noi bo ADFECGDB (khong dung CinC). AUROC/AUPRC tren CinC cho
     nhom topo, co dien, ket hop (+ hai nhom phu de dien giai).
  6. Cong tu choi tren CinC: tu choi x% doan tin cay thap nhat (x = 0..50), F1 trung binh doan con lai;
     duong co so NGAU NHIEN (200 hoan vi) va duong oracle (tu choi theo F1 that).
"""
import os, sys, json, time, datetime, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
# gioi han luong BLAS/OpenMP TRUOC khi nap numpy/torch: may 12 loi, OpenBLAS mo 12 luong/tien trinh
# -> tranh chap luong voi tien trinh khac (nghi pham cua lan chay 2236 s o r01 kenh 3) va loi cap phat bo nho
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ.setdefault(_v, '4')
import numpy as np, torch, mne, wfdb
torch.set_num_threads(4)
from scipy import signal as sg, stats
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
import fsqi
from _paths import adfecgdb_dir, cinc2013_dir
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG = M.CFG

FS = CFG['fs']; SEG_S = 4.0; SEG = int(SEG_S * FS); Q = 1000 // FS
TOL_MS = CFG['tolerance_ms']; BAD_THR = 80.0; N_BOOT = 1000; N_RAND = 200; SEED = 0
REJECT_FRACS = list(range(0, 51))

TOPO = list(fsqi.TOPO_KEYS)
CLASSICAL = list(fsqi.CLASSICAL_KEYS) + ['peak_prob_mean', 'prob_max']
SIGNAL_ONLY = ['sampen', 'kurtosis', 'spec_entropy', 'band_ratio', 'psd_fhr', 'tau_acf']
MODEL_OUT = ['rr_cv', 'rr_plaus', 'bsqi', 'n_det', 'peak_prob_mean', 'prob_max']
GROUPS = {'topo': TOPO, 'classical': CLASSICAL, 'combined': TOPO + CLASSICAL,
          'classical_signal_only': SIGNAL_ONLY, 'classical_model_output_only': MODEL_OUT}
MAIN_GROUPS = ['topo', 'classical', 'combined']
ALL_FEATS = TOPO + CLASSICAL
COLOR = {'topo': '#2a78d6', 'classical': '#eb6834', 'combined': '#1baf7a',
         'random': '#8a8a8a', 'oracle': '#222222'}
LABEL = {'topo': 'Topo (16 đặc trưng)', 'classical': 'Cổ điển (12 chỉ số)', 'combined': 'Kết hợp (28)',
         'random': 'Từ chối ngẫu nhiên', 'oracle': 'Oracle (theo F1 thật)'}


class Tee:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.o = sys.stdout
    def write(self, s): self.o.write(s); self.f.write(s)
    def flush(self): self.o.flush(); self.f.flush()


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ ghep su kien toan ban ghi
def greedy_match(det, ref, tol):
    """giong M.match_events nhung tra ve co ghep cua tung det va tung ref"""
    ref = np.asarray(ref, float); det = np.sort(np.asarray(det, float))
    used = np.zeros(len(ref), bool); dm = np.zeros(len(det), bool)
    for i, d in enumerate(det):
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (~used))[0]
        if len(ok):
            used[ok[int(np.argmin(dd[ok]))]] = True; dm[i] = True
    return det, dm, used


def process_lead(ds, rec, lead, sig1000, gt1000, net, thr, rows):
    x250 = M.preprocess(sig1000, 1000, CFG); res, _ = M.cancel_maternal(x250, CFG)
    prob = M.probability_series(net, M.robust_scale(res).astype(np.float32),
                                M.robust_scale(x250).astype(np.float32), CFG)
    det250 = M.pick_peaks(prob, thr, CFG); det1000 = det250.astype(np.int64) * Q
    det_s, dm, rm = greedy_match(det1000, gt1000, TOL_MS / 1000 * 1000)
    ref = M.match_events(det1000, gt1000, 1000, TOL_MS)
    assert int(rm.sum()) == ref['TP'], 'ghep toan ban ghi khong khop M.match_events'
    n_seg = len(res) // SEG; n_skip = 0; slowest = (0.0, -1)
    for k in range(n_seg):
        a, b = k * SEG, (k + 1) * SEG; a4, b4 = a * Q, b * Q
        gsel = (gt1000 >= a4) & (gt1000 < b4)
        if not gsel.any():
            n_skip += 1; continue
        dsel = (det_s >= a4) & (det_s < b4)
        TP = int(rm[gsel].sum()); FN = int(gsel.sum()) - TP; FP = int((~dm[dsel]).sum())
        F1 = 200.0 * TP / (2 * TP + FP + FN)
        det_rel = det250[(det250 >= a) & (det250 < b)] - a
        f, tm = fsqi.all_features(res[a:b], FS, det_rel, sig1000[a4:b4], 1000)
        if tm['slow']:
            log(f'    CANH BAO doan cham: {ds} {rec} kenh {lead} doan {k}: {tm["slow"]} '
                f'topo {tm["topo_ms"]:.0f} / sublevel {tm["sublevel_ms"]:.0f} / classical {tm["classical_ms"]:.0f} ms')
        if tm['total_ms'] > slowest[0]: slowest = (tm['total_ms'], k)
        tm = {kk: v for kk, v in tm.items() if kk != 'slow'}
        pseg = prob[a:b]
        f['peak_prob_mean'] = float(np.mean(pseg[det_rel])) if len(det_rel) else 0.0
        f['prob_max'] = float(pseg.max())
        row = dict(dataset=ds, rec=rec, lead=int(lead), seg=k, t0_s=a / FS, n_gt=int(gsel.sum()),
                   n_det_seg=int(dsel.sum()), TP=TP, FP=FP, FN=FN, F1=F1, lead_F1=ref['F1'])
        row.update(f); row.update({'time_' + kk: v for kk, v in tm.items()})
        rows.append(row)
    return ref['F1'], n_seg, n_skip, slowest


def run_adfecgdb(rows):
    RAW = adfecgdb_dir(); per = {}
    for rec in ['r01', 'r04', 'r07', 'r08', 'r10']:
        b = torch.load(os.path.join(ROOT, 'model', 'checkpoints', f'fetalqrs_tcn_fold_{rec}.pt'),
                       map_location='cpu', weights_only=False)
        assert b['test_record'] == rec
        net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval(); thr = float(b['threshold'])
        sig = mne.io.read_raw_edf(os.path.join(RAW, rec + '.edf'), preload=True, verbose=False).get_data()
        gt = np.asarray(wfdb.rdann(os.path.join(RAW, rec), 'edf.qrs').sample, int)
        per[rec] = {}
        for lead in (1, 2, 3, 4):
            t0 = time.time()
            F1, n_seg, n_skip, sl = process_lead('adfecgdb', rec, lead, sig[lead], gt, net, thr, rows)
            per[rec][lead] = F1
            log(f'  ADFECGDB {rec} kenh {lead}: F1 ban ghi {F1:6.2f}  doan {n_seg - n_skip}/{n_seg}  '
                f'thr {thr:.2f}  {time.time() - t0:5.1f}s  (doan cham nhat #{sl[1]}: {sl[0]:.0f} ms)')
    return per


def run_cinc(rows):
    D = cinc2013_dir(); assert D is not None, 'khong thay CinC 2013'
    recs = sorted({f[:-4] for f in os.listdir(D) if f.endswith('.dat')})[:10]
    b = torch.load(os.path.join(ROOT, 'model', 'checkpoints', 'fetalqrs_tcn_production.pt'),
                   map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval(); thr = float(b['threshold'])
    per = {}
    for rec in recs:
        r_ = wfdb.rdrecord(os.path.join(D, rec)); ann = wfdb.rdann(os.path.join(D, rec), 'fqrs')
        fs0 = r_.fs; gt = (ann.sample * (1000.0 / fs0)).round().astype(int)
        per[rec] = {}
        for lead in range(min(4, r_.p_signal.shape[1])):
            s = np.nan_to_num(r_.p_signal[:, lead])
            if fs0 != 1000: s = sg.resample_poly(s, 1000, int(fs0))
            t0 = time.time()
            F1, n_seg, n_skip, sl = process_lead('cinc', rec, lead, s, gt, net, thr, rows)
            per[rec][lead] = F1
            log(f'  CinC {rec} kenh {lead}: F1 ban ghi {F1:6.2f}  doan {n_seg - n_skip}/{n_seg}  '
                f'thr {thr:.2f}  {time.time() - t0:5.1f}s  (doan cham nhat #{sl[1]}: {sl[0]:.0f} ms)')
    return per


# ------------------------------------------------------------------ Spearman + bootstrap
def spearman_boot(x, y, grp, rng):
    ok = np.isfinite(x) & np.isfinite(y); x, y, grp = x[ok], y[ok], grp[ok]; n = len(x)
    if n < 10 or np.std(x) == 0 or np.std(y) == 0:
        return dict(rho=float('nan'), p=float('nan'), n=int(n), ci95=[float('nan')] * 2, ci95_cluster=[float('nan')] * 2)
    rho, p = stats.spearmanr(x, y)
    bs = np.empty(N_BOOT); cb = np.empty(N_BOOT)
    ug = np.unique(grp); gi = {u: np.where(grp == u)[0] for u in ug}
    for i in range(N_BOOT):
        idx = rng.integers(0, n, n); bs[i] = stats.spearmanr(x[idx], y[idx])[0]
        pick = rng.choice(ug, len(ug), replace=True)
        idx = np.concatenate([gi[u] for u in pick]); cb[i] = stats.spearmanr(x[idx], y[idx])[0]
    return dict(rho=float(rho), p=float(p), n=int(n),
                ci95=[float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
                ci95_cluster=[float(np.nanpercentile(cb, 2.5)), float(np.nanpercentile(cb, 97.5))])


# ------------------------------------------------------------------ bo phan loai
def make_X(rows, keys):
    return np.array([[r[k] for k in keys] for r in rows], float)


def fit_predict(Xtr, ytr, Xte, learner):
    med = np.nanmedian(Xtr, 0); med = np.where(np.isfinite(med), med, 0.0)
    Xtr = np.where(np.isfinite(Xtr), Xtr, med); Xte = np.where(np.isfinite(Xte), Xte, med)
    if learner == 'lr':
        clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, class_weight='balanced', max_iter=5000))
    else:
        clf = HistGradientBoostingClassifier(max_depth=3, max_iter=200, learning_rate=0.05,
                                             class_weight='balanced', random_state=SEED)
    clf.fit(Xtr, ytr)
    return clf.predict_proba(Xte)[:, 1], clf


def loro_cv_auroc(rows, keys, learner):
    """LORO-CV noi bo ADFECGDB (chia theo ban ghi) -> AUROC trung binh cac fold co du hai lop"""
    recs = sorted({r['rec'] for r in rows}); X = make_X(rows, keys)
    y = np.array([r['F1'] < BAD_THR for r in rows]); g = np.array([r['rec'] for r in rows])
    aucs = {}
    for rec in recs:
        te = g == rec
        if y[te].sum() == 0 or (~y[te]).sum() == 0 or y[~te].sum() == 0:
            aucs[rec] = None; continue
        p, _ = fit_predict(X[~te], y[~te], X[te], learner)
        aucs[rec] = float(roc_auc_score(y[te], p))
    vals = [v for v in aucs.values() if v is not None]
    return (float(np.mean(vals)) if vals else float('nan')), aucs


def risk_coverage(F1, score_bad, TP, FP, FN):
    order = np.argsort(-score_bad, kind='stable'); n = len(F1); macro, micro = [], []
    for x in REJECT_FRACS:
        keep = order[int(round(x / 100 * n)):]
        macro.append(float(F1[keep].mean()))
        tp, fp, fn = TP[keep].sum(), FP[keep].sum(), FN[keep].sum()
        micro.append(float(200.0 * tp / (2 * tp + fp + fn)))
    return macro, micro


# ------------------------------------------------------------------ ve
def plot_correlation(sp, out):
    feats = sorted(ALL_FEATS, key=lambda k: abs(sp['cinc'][k]['rho']) if np.isfinite(sp['cinc'][k]['rho']) else -1)
    fig, axes = plt.subplots(1, 2, figsize=(12, 9), sharey=True)
    for ax, ds, title in zip(axes, ['adfecgdb', 'cinc'], ['ADFECGDB (trong miền, 5 bản ghi × 4 kênh)',
                                                          'CinC 2013 set-a (ngoài miền, 10 × 4)']):
        ypos = np.arange(len(feats))
        for i, k in enumerate(feats):
            r = sp[ds][k]; rho = r['rho']; lo, hi = r['ci95']
            if not np.isfinite(rho): continue
            a = abs(rho)
            if lo <= 0 <= hi: elo, ehi = a, max(abs(lo), abs(hi)) - a
            else: elo, ehi = a - min(abs(lo), abs(hi)), max(abs(lo), abs(hi)) - a
            col = COLOR['topo'] if k in TOPO else COLOR['classical']
            ax.barh(i, a, color=col, height=0.72, edgecolor='none')
            ax.errorbar(a, i, xerr=[[max(elo, 0)], [max(ehi, 0)]], fmt='none', ecolor='#444444', elinewidth=1, capsize=2)
            ax.text(a + 0.012 + max(ehi, 0), i, ('+' if rho > 0 else '−') + f'{a:.2f}', va='center', fontsize=7.5, color='#333333')
        ax.set_yticks(ypos); ax.set_yticklabels(feats, fontsize=8.5)
        ax.set_xlim(0, 1.0); ax.set_xlabel('|Spearman ρ| với F1 đoạn 4 s (thanh lỗi: bootstrap 95%)', fontsize=9)
        ax.set_title(title, fontsize=10); ax.grid(axis='x', color='#e6e6e6', linewidth=0.8); ax.set_axisbelow(True)
        for s in ('top', 'right'): ax.spines[s].set_visible(False)
    h = [plt.Rectangle((0, 0), 1, 1, color=COLOR['topo']), plt.Rectangle((0, 0), 1, 1, color=COLOR['classical'])]
    axes[0].legend(h, ['Topo (Takens+ripser, sublevel H0)', 'Cổ điển (+ tin cậy mô hình)'], loc='lower right', fontsize=8.5, frameon=False)
    fig.suptitle('fSQI: tương quan từng chỉ số với F1 thật của FetalQRS-TCN trên đoạn 4 s', fontsize=11)
    fig.tight_layout(); fig.savefig(out, dpi=160); plt.close(fig)


def plot_risk_coverage(rc, out):
    cov = 100 - np.array(REJECT_FRACS)
    fig, ax = plt.subplots(figsize=(8, 5.2))
    for key in ['oracle', 'random', 'topo', 'classical', 'combined']:
        ls = '--' if key == 'oracle' else '-'
        ax.plot(cov, rc[key]['macro'], ls, color=COLOR[key], linewidth=2 if key != 'oracle' else 1.4, label=LABEL[key])
    for c in (80, 90): ax.axvline(c, color='#bbbbbb', linewidth=0.9, linestyle=':')
    ax.set_xlim(100, 50); ax.set_xlabel('Độ phủ (% đoạn được giữ lại)', fontsize=10)
    ax.set_ylabel('F1 trung bình các đoạn giữ lại (%)', fontsize=10)
    ax.set_title('Cổng từ chối trên CinC 2013 (bộ phân loại huấn luyện trên ADFECGDB)', fontsize=11)
    ax.grid(color='#e6e6e6', linewidth=0.8); ax.set_axisbelow(True)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.legend(fontsize=9, frameon=False, loc='lower left')
    fig.tight_layout(); fig.savefig(out, dpi=160); plt.close(fig)


# ------------------------------------------------------------------ main
def main():
    T0 = time.time(); sys.stdout = Tee(os.path.join(HERE, 'fsqi_log.txt'))
    log(f'eval_fsqi.py  {datetime.datetime.now():%Y-%m-%d %H:%M}  torch {torch.__version__} threads {torch.get_num_threads()}')
    log(f'doan {SEG_S}s @ {FS}Hz, dung sai +/-{TOL_MS} ms, nhan xau = F1 doan < {BAD_THR}, bootstrap {N_BOOT}, seed {SEED}')

    # doi chieu sublevel H0 vs scipy prominence tren tin hieu that (bao cao trong results)
    log('\n[1] Trich dac trung + F1 doan')
    rows = []
    per_ad = run_adfecgdb(rows); per_ci = run_cinc(rows)
    ad = [r for r in rows if r['dataset'] == 'adfecgdb']; ci = [r for r in rows if r['dataset'] == 'cinc']
    log(f'  so doan: ADFECGDB {len(ad)}, CinC {len(ci)}')
    macro_ad = float(np.mean([v for d in per_ad.values() for v in d.values()]))
    macro_ci = float(np.mean([v for d in per_ci.values() for v in d.values()]))
    log(f'  macro F1 ban ghi x kenh (kiem tra pipeline): ADFECGDB {macro_ad:.2f}  CinC {macro_ci:.2f}')
    for ds, rr in (('adfecgdb', ad), ('cinc', ci)):
        F = np.array([r['F1'] for r in rr])
        log(f'  {ds}: F1 doan trung binh {F.mean():.2f}, trung vi {np.median(F):.1f}, ti le doan < {BAD_THR:.0f}: {np.mean(F < BAD_THR) * 100:.1f}%')

    # thoi gian
    timing = {}
    for comp in ('topo', 'sublevel', 'classical', 'total'):
        t = np.array([r['time_' + comp + '_ms'] for r in rows])
        timing[comp] = dict(mean_ms=float(t.mean()), median_ms=float(np.median(t)), p95_ms=float(np.percentile(t, 95)), max_ms=float(t.max()))
        log(f'  thoi gian {comp:9s}: TB {t.mean():6.1f} ms  trung vi {np.median(t):6.1f}  p95 {np.percentile(t, 95):6.1f}  max {t.max():6.1f}')

    # doi chieu sublevel vs scipy tren 20 doan that
    chk = []
    D = cinc2013_dir(); r_ = wfdb.rdrecord(os.path.join(D, 'a01'))
    x = M.preprocess(np.nan_to_num(r_.p_signal[:, 0]), 1000, CFG); res, _ = M.cancel_maternal(x, CFG)
    for k in range(min(15, len(res) // SEG)):
        chk.append(fsqi.check_sublevel_vs_scipy(res[k * SEG:(k + 1) * SEG]))
    sl_check = dict(n_segments=len(chk), n_compared=int(sum(c['n_compared'] for c in chk)),
                    max_abs_diff=float(max(c['max_abs_diff'] for c in chk)), all_match=bool(all(c['match'] for c in chk)))
    log(f'  doi chieu sublevel-H0 vs scipy prominence (a01 kenh 0, {len(chk)} doan): {sl_check}')

    # ghi bang doan
    keys = ['dataset', 'rec', 'lead', 'seg', 't0_s', 'n_gt', 'n_det_seg', 'TP', 'FP', 'FN', 'F1', 'lead_F1'] + ALL_FEATS + \
           ['time_topo_ms', 'time_sublevel_ms', 'time_classical_ms', 'time_total_ms']
    with open(os.path.join(HERE, 'segments.csv'), 'w', encoding='utf-8') as f:
        f.write(','.join(keys) + '\n')
        for r in rows: f.write(','.join(str(r[k]) for k in keys) + '\n')

    # ---------------------------------------------------------- [2] Spearman
    log('\n[2] Spearman rho(chi so, F1 doan) + bootstrap 95%')
    rng = np.random.default_rng(SEED); sp = {}
    for ds, rr in (('adfecgdb', ad), ('cinc', ci)):
        F = np.array([r['F1'] for r in rr]); g = np.array([f"{r['rec']}_{r['lead']}" for r in rr]); sp[ds] = {}
        for k in ALL_FEATS:
            sp[ds][k] = spearman_boot(np.array([r[k] for r in rr], float), F, g, rng)
        log(f'  {ds}:')
        for k in sorted(ALL_FEATS, key=lambda k: -abs(sp[ds][k]['rho']) if np.isfinite(sp[ds][k]['rho']) else 1):
            r = sp[ds][k]
            log(f'    {k:15s} {"topo" if k in TOPO else "codien":7s} rho {r["rho"]:+.3f}  CI95 [{r["ci95"][0]:+.3f},{r["ci95"][1]:+.3f}]'
                f'  CI cum [{r["ci95_cluster"][0]:+.3f},{r["ci95_cluster"][1]:+.3f}]  p {r["p"]:.1e}')
    best = {}
    for ds in ('adfecgdb', 'cinc'):
        bt = max(TOPO, key=lambda k: abs(sp[ds][k]['rho']) if np.isfinite(sp[ds][k]['rho']) else 0)
        bc = max(CLASSICAL, key=lambda k: abs(sp[ds][k]['rho']) if np.isfinite(sp[ds][k]['rho']) else 0)
        best[ds] = dict(best_topo=[bt, sp[ds][bt]['rho']], best_classical=[bc, sp[ds][bc]['rho']],
                        mean_abs_rho_topo=float(np.nanmean([abs(sp[ds][k]['rho']) for k in TOPO])),
                        mean_abs_rho_classical=float(np.nanmean([abs(sp[ds][k]['rho']) for k in CLASSICAL])))
        log(f'  {ds}: topo tot nhat {bt} ({sp[ds][bt]["rho"]:+.3f}), co dien tot nhat {bc} ({sp[ds][bc]["rho"]:+.3f})')
    plot_correlation(sp, os.path.join(HERE, 'sqi_correlation.png'))

    # ---------------------------------------------------------- [3] bo phan loai xuyen mien
    log(f'\n[3] Bo phan loai "F1 doan < {BAD_THR:.0f}": train ADFECGDB -> test CinC')
    y_ad = np.array([r['F1'] < BAD_THR for r in ad]); y_ci = np.array([r['F1'] < BAD_THR for r in ci])
    log(f'  ti le duong: ADFECGDB {y_ad.mean() * 100:.1f}% ({y_ad.sum()}/{len(y_ad)}), CinC {y_ci.mean() * 100:.1f}% ({y_ci.sum()}/{len(y_ci)})')
    clf_res = {}; p_bad = {}
    for gname, keys_g in GROUPS.items():
        cv = {l: loro_cv_auroc(ad, keys_g, l) for l in ('lr', 'gb')}
        chosen = 'lr' if cv['lr'][0] >= cv['gb'][0] else 'gb'      # quy tac co dinh, chi dung ADFECGDB
        Xtr, Xte = make_X(ad, keys_g), make_X(ci, keys_g); out = {}
        for l in ('lr', 'gb'):
            p, clf = fit_predict(Xtr, y_ad, Xte, l)
            out[l] = dict(auroc_cinc=float(roc_auc_score(y_ci, p)), auprc_cinc=float(average_precision_score(y_ci, p)),
                          cv_auroc_adfecgdb=cv[l][0], cv_folds=cv[l][1])
            if l == chosen:
                p_bad[gname] = p
                if l == 'lr':
                    coef = clf.named_steps['logisticregression'].coef_[0]
                    out['lr_coef_standardized'] = {k: float(c) for k, c in sorted(zip(keys_g, coef), key=lambda t: -abs(t[1]))}
        clf_res[gname] = dict(n_features=len(keys_g), chosen_learner=chosen, **out,
                              auroc_cinc=out[chosen]['auroc_cinc'], auprc_cinc=out[chosen]['auprc_cinc'])
        log(f'  {gname:28s} n={len(keys_g):2d}  chon {chosen} (CV ADFECGDB lr {cv["lr"][0]:.3f} gb {cv["gb"][0]:.3f})'
            f'  -> CinC AUROC {out[chosen]["auroc_cinc"]:.3f}  AUPRC {out[chosen]["auprc_cinc"]:.3f}'
            f'   [lr {out["lr"]["auroc_cinc"]:.3f} / gb {out["gb"]["auroc_cinc"]:.3f}]')
    # AUROC tung dac trung don le tren CinC, huong dau lay tu Spearman tren ADFECGDB (khong nhin CinC)
    single = {}
    for k in ALL_FEATS:
        s = np.sign(sp['adfecgdb'][k]['rho']) if np.isfinite(sp['adfecgdb'][k]['rho']) else 1.0
        v = np.array([r[k] for r in ci], float); v = np.where(np.isfinite(v), v, np.nanmedian(v))
        single[k] = float(roc_auc_score(y_ci, -s * v))
    log('  AUROC don le tren CinC (huong tu ADFECGDB): ' + ', '.join(f'{k} {v:.3f}' for k, v in sorted(single.items(), key=lambda t: -t[1])[:8]))

    # ---------------------------------------------------------- [4] cong tu choi
    log('\n[4] Cong tu choi tren CinC (x% doan tin cay thap nhat)')
    F = np.array([r['F1'] for r in ci]); TP = np.array([r['TP'] for r in ci]); FP = np.array([r['FP'] for r in ci]); FN = np.array([r['FN'] for r in ci])
    rc = {}
    for g in MAIN_GROUPS:
        m, mi = risk_coverage(F, p_bad[g], TP, FP, FN); rc[g] = dict(macro=m, micro=mi)
    m, mi = risk_coverage(F, -F, TP, FP, FN); rc['oracle'] = dict(macro=m, micro=mi)
    rng = np.random.default_rng(SEED); acc_m = np.zeros(len(REJECT_FRACS)); acc_i = np.zeros(len(REJECT_FRACS))
    for _ in range(N_RAND):
        m, mi = risk_coverage(F, rng.random(len(F)), TP, FP, FN); acc_m += m; acc_i += mi
    rc['random'] = dict(macro=list(acc_m / N_RAND), micro=list(acc_i / N_RAND))
    i80, i90 = REJECT_FRACS.index(20), REJECT_FRACS.index(10)
    summary = {}
    log(f'  {"":12s}{"phu 100%":>10}{"phu 90%":>10}{"phu 80%":>10}{"phu 50%":>10}   (F1 TB doan, CinC)')
    for key in ['random', 'topo', 'classical', 'combined', 'oracle']:
        mm = rc[key]['macro']
        summary[key] = dict(F1_cov100=mm[0], F1_cov90=mm[i90], F1_cov80=mm[i80], F1_cov50=mm[-1],
                            micro_cov90=rc[key]['micro'][i90], micro_cov80=rc[key]['micro'][i80],
                            mean_over_curve=float(np.mean(mm)))
        log(f'  {key:12s}{mm[0]:10.2f}{mm[i90]:10.2f}{mm[i80]:10.2f}{mm[-1]:10.2f}')
    plot_risk_coverage(rc, os.path.join(HERE, 'risk_coverage.png'))

    # ---------------------------------------------------------- ket luan tu dong (chi tu so do)
    a_t, a_c, a_k = (clf_res[g]['auroc_cinc'] for g in MAIN_GROUPS)
    verdict = dict(topo_predicts_error=bool(a_t > 0.6),
                   topo_beats_classical_auroc=bool(a_t > a_c),
                   combined_beats_classical_auroc=bool(a_k > a_c),
                   topo_beats_classical_at_cov80=bool(summary['topo']['F1_cov80'] > summary['classical']['F1_cov80']),
                   topo_beats_random_at_cov80=bool(summary['topo']['F1_cov80'] > summary['random']['F1_cov80']))
    log('\nKet luan tu so do: ' + json.dumps(verdict))

    res = dict(meta=dict(date=str(datetime.datetime.now()), seg_s=SEG_S, fs=FS, tolerance_ms=TOL_MS, bad_threshold_F1=BAD_THR,
                         n_boot=N_BOOT, n_random=N_RAND, seed=SEED, n_segments=dict(adfecgdb=len(ad), cinc=len(ci)),
                         topo_params=fsqi.DEFAULT, groups={k: v for k, v in GROUPS.items()},
                         runtime_min=(time.time() - T0) / 60, timing_ms=timing, sublevel_vs_scipy=sl_check),
               pipeline_check=dict(per_lead_F1=dict(adfecgdb=per_ad, cinc=per_ci), macro_F1=dict(adfecgdb=macro_ad, cinc=macro_ci)),
               segment_F1=dict(adfecgdb=dict(mean=float(np.mean([r['F1'] for r in ad])), frac_bad=float(y_ad.mean())),
                               cinc=dict(mean=float(np.mean([r['F1'] for r in ci])), frac_bad=float(y_ci.mean()))),
               spearman=sp, spearman_summary=best, classifier=clf_res, single_feature_auroc_cinc=single,
               risk_coverage=dict(reject_fracs=REJECT_FRACS, curves=rc, summary=summary), verdict=verdict)
    json.dump(res, open(os.path.join(HERE, 'results.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    log(f'\nda ghi results.json, segments.csv, sqi_correlation.png, risk_coverage.png, fsqi_log.txt  ({(time.time() - T0) / 60:.1f} phut)')


if __name__ == '__main__':
    main()
