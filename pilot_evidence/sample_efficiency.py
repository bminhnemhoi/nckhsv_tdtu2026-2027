# -*- coding: utf-8 -*-
"""
Hieu qua mau (Phase P8, nhiem vu G, phan 2): F1 tren chu the giu lai theo so chu the huan luyen k.

Recipe HUAN LUYEN lay nguyen tu model/train_final.py (copy ham, KHONG sua file goc):
  segments() stride 250, heatmap Gaussian sigma=3 mau, BCEWithLogits pos_weight (clamp 30),
  AdamW lr 3e-3 wd 1e-4, OneCycleLR, clip_grad 1.0, batch 32, 6 epoch (hoac 4 neu vuot ngan sach 40 phut).

Thiet ke:
  k=1: 5 lan (moi ban ghi PhysioNet lam tap train mot lan), test tren 4 ban ghi con lai x 4 kenh = 16 danh gia/lan.
       KHONG co ban ghi val -> nguong CO DINH 0,45 (nguong production trong train_final.py: trung vi 5 fold
       = 0,45; cung la gia tri mac dinh cua M.detect).
  k=2: 5 cap chon ngau nhien khong lap tu 10 cap (np.random.default_rng(0)), train tren ca hai ban ghi,
       nguong chon tren ban ghi THU NHAT cua cap (nam TRONG tap train -> nguong in-sample, ghi ro),
       test tren 3 ban ghi con lai x 4 kenh = 12 danh gia/lan.
       Phu: cung mo hinh do voi nguong co dinh 0,45 (de tach anh huong cua cach chon nguong).
  k=3: KHONG chay lai. Lay tu LORO da co (pilot_evidence/train_final.json: 3 ban ghi train + 1 ban ghi val
       rieng + 1 ban ghi test; benchmark_dpss/all_leads.json cung mo hinh do, cham lai).

Cham: +/-50 ms, M.match_events tai 250 Hz (nhu train_final.eval_record). Bao cao:
  macro F1 tren TAT CA danh gia giu lai gop lai (pooled) va TB / min / max cua macro F1 tung lan chay.

Chay:  PYTHONIOENCODING=utf-8 python pilot_evidence/sample_efficiency.py [--epochs N] [--budget_min 40]
Ghi:   pilot_evidence/sample_efficiency.json, sample_efficiency.png, sample_log.txt
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, math, argparse, datetime, importlib.util, itertools
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
import mne, wfdb

torch.set_num_threads(3)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
from _paths import adfecgdb_dir
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG = M.CFG

RECS = ['r01', 'r04', 'r07', 'r08', 'r10']
LEADS = (1, 2, 3, 4)
FIXED_THR = 0.45          # train_final.py: thr_prod = median(fold thresholds) = 0.45; M.detect default
GRID = np.arange(.20, .80, .05)   # luoi nguong cua train_final.pick_threshold


class Tee:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.s = sys.stdout
    def write(self, t): self.s.write(t); self.f.write(t)
    def flush(self): self.s.flush(); self.f.flush()


# ------------------------------------------------------------------ copy tu model/train_final.py
def load_records(RAW):
    D = {}
    for ri, rec in enumerate(RECS):
        raw = mne.io.read_raw_edf(os.path.join(RAW, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data(); del raw
        q = CFG['fs_in'] // CFG['fs']
        fq = (wfdb.rdann(os.path.join(RAW, rec + '.edf'), 'qrs').sample / q).round().astype(int)
        for lead in LEADS:
            x250 = M.preprocess(sig[lead], CFG['fs_in'], CFG)
            res, _ = M.cancel_maternal(x250, CFG)
            D[(ri, lead)] = (M.robust_scale(res).astype(np.float32),
                             M.robust_scale(x250).astype(np.float32), fq)
        del sig
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


def train(model, X, Y, epochs=6, bs=32, lr=3e-3, log=print):
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


# ------------------------------------------------------------------ danh gia (xac suat tinh 1 lan, quet nguong)
def probs_record(model, D, ri):
    return {lead: M.probability_series(model, D[(ri, lead)][0], D[(ri, lead)][1], CFG) for lead in LEADS}


def score_probs(P, D, ri, thr):
    out = []
    for lead in LEADS:
        pk = M.pick_peaks(P[lead], thr, CFG)
        m = M.match_events(pk, D[(ri, lead)][2], CFG['fs'], CFG['tolerance_ms'])
        m = {k: (float(v) if isinstance(v, (float, np.floating)) else int(v)) for k, v in m.items()}
        m.update(record=RECS[ri], lead=lead, threshold=float(thr)); out.append(m)
    return out


def pick_threshold_probs(P, D, ri, grid=GRID):
    best, bt = -1, FIXED_THR
    for t in grid:
        f = float(np.mean([m['F1'] for m in score_probs(P, D, ri, float(t))]))
        if f > best: best, bt = f, float(t)
    return bt, best


def summarize(rows):
    f = np.array([r['F1'] for r in rows])
    tp = sum(r['TP'] for r in rows); fp = sum(r['FP'] for r in rows); fn = sum(r['FN'] for r in rows)
    return dict(n=int(len(rows)), macro_F1=float(f.mean()), sd_F1=float(f.std(ddof=1)) if len(f) > 1 else 0.0,
                min_F1=float(f.min()), max_F1=float(f.max()), micro_F1=200 * tp / max(2 * tp + fp + fn, 1),
                Se=float(np.mean([r['Se'] for r in rows])), PPV=float(np.mean([r['PPV'] for r in rows])),
                TP=tp, FP=fp, FN=fn)


# ------------------------------------------------------------------ chinh
def main(epochs_arg, budget_min, seed):
    t0 = time.time()
    sys.stdout = Tee(os.path.join(HERE, 'sample_log.txt'))
    def log(*a):
        print(' '.join(str(x) for x in a), flush=True)
    log('=' * 96)
    log('HIEU QUA MAU -- train tren k chu the PhysioNet (k=1,2), test tren chu the con lai; k=3 = LORO da co')
    log('bat dau:', datetime.datetime.now().isoformat(timespec='seconds'),
        '| torch threads', torch.get_num_threads(), '| seed', seed, '| ngan sach', budget_min, 'phut')
    log('numpy %s torch %s mne %s wfdb %s' % (np.__version__, torch.__version__, mne.__version__, wfdb.__version__))
    log('=' * 96)
    RAW = adfecgdb_dir(); log('ADFECGDB:', RAW)
    D = load_records(RAW); log('nap %d (ban ghi x kenh) trong %.0fs' % (len(D), time.time() - t0))

    # ---- k=3 tu LORO da co
    tf = json.load(open(os.path.join(HERE, 'train_final.json'), encoding='utf-8'))
    al = json.load(open(os.path.join(ROOT, 'benchmark_dpss', 'all_leads.json'), encoding='utf-8'))
    k3_runs = []
    for rec in RECS:
        fold = tf['folds'][rec]
        k3_runs.append(dict(train=fold.get('rows', [{}])[0].get('record') and None or None,
                            test=[rec], threshold=fold['threshold'],
                            macro_F1_train_final=fold['macro_F1'],
                            per_lead_all_leads=al[rec], macro_F1_all_leads=float(np.mean(al[rec]))))
    k3_pooled_all_leads = float(np.mean([v for rec in RECS for v in al[rec]]))
    k3_pooled_train_final = tf['summary']['macro_F1']
    log('k=3 (LORO da co): train_final.json macro 20 = %.2f ; all_leads.json macro 20 = %.2f ; theo fold: %s'
        % (k3_pooled_train_final, k3_pooled_all_leads,
           ['%s %.2f' % (r, float(np.mean(al[r]))) for r in RECS]))

    # ---- do thoi gian 1 epoch (k=1, 1 ban ghi) de chon so epoch trong ngan sach
    X1, Y1 = segments(D, [0])
    torch.manual_seed(seed); probe = M.FetalQRSTCN()
    tt = time.time(); train(probe, X1, Y1, epochs=1, log=lambda *a: None); t_ep = time.time() - tt
    n_seg1 = len(X1); del X1, Y1, probe
    # tong doan-epoch: k=1: 5 lan x n_seg1 ; k=2: 5 lan x 2*n_seg1 (xap xi, cac ban ghi dai bang nhau)
    seg_passes_per_epoch = 5 * n_seg1 + 5 * 2 * n_seg1
    t_train_6 = t_ep / n_seg1 * seg_passes_per_epoch * 6
    t_eval = 10 * 4 * 4 * 0.6 + 5 * 4 * 0.6     # uoc luong probability_series ~0.6 s/kenh (do o snr_curve)
    proj_6 = (t_train_6 + t_eval) / 60
    if epochs_arg:
        epochs = epochs_arg; why = 'chi dinh boi --epochs'
    elif proj_6 <= budget_min:
        epochs = 6; why = 'du kien %.1f phut <= ngan sach %d phut' % (proj_6, budget_min)
    else:
        epochs = 4; why = 'du kien 6 epoch = %.1f phut > ngan sach %d phut -> giam xuong 4 epoch' % (proj_6, budget_min)
    log('do thu: 1 epoch tren %d doan (1 ban ghi) = %.1fs -> du kien 6 epoch toan bo = %.1f phut => epochs = %d (%s)'
        % (n_seg1, t_ep, proj_6, epochs, why))

    runs = []
    # ---- k=1
    log('\n===== k = 1 (5 lan, nguong co dinh %.2f) =====' % FIXED_THR)
    for ti in range(5):
        test_ids = [i for i in range(5) if i != ti]
        log('-- k=1 train=%s test=%s' % (RECS[ti], [RECS[i] for i in test_ids]))
        X, Y = segments(D, [ti]); torch.manual_seed(seed)
        tt = time.time(); model = train(M.FetalQRSTCN(), X, Y, epochs, log=log); t_tr = time.time() - tt
        del X, Y
        rows_fixed, rows_insample = [], []
        P_train = probs_record(model, D, ti)
        thr_in, f_in = pick_threshold_probs(P_train, D, ti); del P_train
        for te in test_ids:
            P = probs_record(model, D, te)
            rows_fixed += score_probs(P, D, te, FIXED_THR)
            rows_insample += score_probs(P, D, te, thr_in)
            del P
        sf, si = summarize(rows_fixed), summarize(rows_insample)
        log('   train %.0fs | nguong co dinh %.2f: macro %.2f (min %.2f, max %.2f) | [phu] nguong in-sample %.2f (F1 train %.2f): macro %.2f'
            % (t_tr, FIXED_THR, sf['macro_F1'], sf['min_F1'], sf['max_F1'], thr_in, f_in, si['macro_F1']))
        log('   theo ban ghi test: ' + ', '.join('%s %.2f' % (RECS[te], np.mean([r['F1'] for r in rows_fixed if r['record'] == RECS[te]])) for te in test_ids))
        runs.append(dict(k=1, train=[RECS[ti]], val=None, test=[RECS[i] for i in test_ids], epochs=epochs,
                         threshold_rule='co dinh 0,45 (production)', threshold=FIXED_THR, train_s=t_tr,
                         primary=sf, rows=rows_fixed,
                         supp_insample_threshold=dict(threshold=thr_in, F1_on_train=f_in, summary=si, rows=rows_insample)))
        del model
        log('   [%.1f phut da troi]' % ((time.time() - t0) / 60))

    # ---- k=2
    pairs_all = list(itertools.combinations(range(5), 2))
    rng = np.random.default_rng(0)
    pairs = [pairs_all[i] for i in sorted(rng.choice(len(pairs_all), 5, replace=False))]
    log('\n===== k = 2 (5 cap ngau nhien seed 0 tu %d cap: %s; nguong tren ban ghi thu nhat cua cap, in-sample) ====='
        % (len(pairs_all), [(RECS[a], RECS[b]) for a, b in pairs]))
    for (va, tb) in pairs:
        test_ids = [i for i in range(5) if i not in (va, tb)]
        log('-- k=2 train=%s (val in-sample=%s) test=%s' % ([RECS[va], RECS[tb]], RECS[va], [RECS[i] for i in test_ids]))
        X, Y = segments(D, [va, tb]); torch.manual_seed(seed)
        tt = time.time(); model = train(M.FetalQRSTCN(), X, Y, epochs, log=log); t_tr = time.time() - tt
        del X, Y
        P_val = probs_record(model, D, va)
        thr, vf1 = pick_threshold_probs(P_val, D, va); del P_val
        rows_val, rows_fixed = [], []
        for te in test_ids:
            P = probs_record(model, D, te)
            rows_val += score_probs(P, D, te, thr)
            rows_fixed += score_probs(P, D, te, FIXED_THR)
            del P
        sv, sf = summarize(rows_val), summarize(rows_fixed)
        log('   train %.0fs | val %s F1 %.2f tai thr %.2f -> TEST macro %.2f (min %.2f, max %.2f) | [phu] nguong co dinh %.2f: macro %.2f'
            % (t_tr, RECS[va], vf1, thr, sv['macro_F1'], sv['min_F1'], sv['max_F1'], FIXED_THR, sf['macro_F1']))
        log('   theo ban ghi test: ' + ', '.join('%s %.2f' % (RECS[te], np.mean([r['F1'] for r in rows_val if r['record'] == RECS[te]])) for te in test_ids))
        runs.append(dict(k=2, train=[RECS[va], RECS[tb]], val=RECS[va], val_in_train=True, test=[RECS[i] for i in test_ids],
                         epochs=epochs, threshold_rule='chon tren ban ghi val nam trong tap train (in-sample)',
                         threshold=thr, val_F1=vf1, train_s=t_tr, primary=sv, rows=rows_val,
                         supp_fixed_threshold=dict(threshold=FIXED_THR, summary=sf, rows=rows_fixed)))
        del model
        log('   [%.1f phut da troi]' % ((time.time() - t0) / 60))

    # ---- tong hop
    def agg(k, key='primary'):
        rs = [r for r in runs if r['k'] == k]
        pooled = summarize([row for r in rs for row in (r['rows'] if key == 'primary' else r[key]['rows'])])
        per_run = [r[key]['macro_F1'] if key == 'primary' else r[key]['summary']['macro_F1'] for r in rs]
        per_test_rec = {}
        for r in rs:
            rows = r['rows'] if key == 'primary' else r[key]['rows']
            for te in r['test']:
                per_test_rec.setdefault(te, []).append(float(np.mean([x['F1'] for x in rows if x['record'] == te])))
        return dict(n_runs=len(rs), pooled=pooled, per_run_macro=per_run,
                    mean_of_runs=float(np.mean(per_run)), min_of_runs=float(np.min(per_run)), max_of_runs=float(np.max(per_run)),
                    per_test_record_mean={k_: float(np.mean(v)) for k_, v in per_test_rec.items()},
                    per_test_record_min={k_: float(np.min(v)) for k_, v in per_test_rec.items()},
                    per_test_record_max={k_: float(np.max(v)) for k_, v in per_test_rec.items()})

    k3_per_fold = [float(np.mean(al[r])) for r in RECS]
    table = {
        '1': agg(1),
        '2': agg(2),
        '3': dict(n_runs=5, source='pilot_evidence/train_final.json + benchmark_dpss/all_leads.json (LORO, khong chay lai)',
                  pooled=dict(n=20, macro_F1=k3_pooled_all_leads, macro_F1_train_final=k3_pooled_train_final,
                              sd_F1=tf['summary']['sd_F1'], micro_F1=tf['summary']['micro_F1'],
                              min_F1=float(min(v for r in RECS for v in al[r])), max_F1=float(max(v for r in RECS for v in al[r]))),
                  per_run_macro=k3_per_fold, mean_of_runs=float(np.mean(k3_per_fold)),
                  min_of_runs=float(np.min(k3_per_fold)), max_of_runs=float(np.max(k3_per_fold)),
                  per_test_record_mean={r: float(np.mean(al[r])) for r in RECS},
                  threshold_rule='chon tren 1 ban ghi val RIENG (khong nam trong train)'),
    }
    table['1_supp_insample_thr'] = agg(1, 'supp_insample_threshold')
    table['2_supp_fixed_thr'] = agg(2, 'supp_fixed_threshold')
    log('\n' + '-' * 96)
    log('%-6s%-10s%-42s%12s%12s%12s%12s' % ('k', 'so lan', 'nguong', 'macro gop', 'TB lan', 'min lan', 'max lan'))
    for kk, lab in (('1', 'co dinh 0,45'), ('2', 'val in-sample'), ('3', 'val rieng (LORO)'),
                    ('1_supp_insample_thr', '[phu] in-sample'), ('2_supp_fixed_thr', '[phu] co dinh 0,45')):
        v = table[kk]
        log('%-6s%-10d%-42s%12.2f%12.2f%12.2f%12.2f' % (kk.split('_')[0], v['n_runs'], lab, v['pooled']['macro_F1'],
                                                        v['mean_of_runs'], v['min_of_runs'], v['max_of_runs']))
    log('-' * 96)

    elapsed = time.time() - t0
    out = dict(meta=dict(ngay=datetime.datetime.now().isoformat(timespec='seconds'), thoi_gian_chay_s=round(elapsed, 1),
                         epochs=epochs, ly_do_epochs=why, t_1_epoch_1_record_s=round(t_ep, 1), n_seg_1_record=n_seg1,
                         du_kien_6_epoch_phut=round(proj_6, 1), ngan_sach_phut=budget_min, seed=seed, batch=32, lr=3e-3,
                         recipe='copy tu model/train_final.py: segments stride 250, BCEWithLogits pos_weight, AdamW 3e-3 OneCycle, clip 1.0',
                         nguong_k1='co dinh 0,45 (train_final.py thr_prod = trung vi nguong 5 fold; mac dinh M.detect)',
                         nguong_k2='chon tren ban ghi thu nhat cua cap, ban ghi nay nam TRONG tap train (in-sample); luoi 0,20..0,75 buoc 0,05',
                         nguong_k3='LORO da co: val rieng, khong nam trong train',
                         cap_k2=[[RECS[a], RECS[b]] for a, b in pairs],
                         cham='+/-50 ms, M.match_events tai 250 Hz, macro F1 = TB F1 tung (ban ghi x kenh) giu lai',
                         phien_ban=dict(python=sys.version.split()[0], numpy=np.__version__, torch=torch.__version__,
                                        mne=mne.__version__, wfdb=wfdb.__version__), torch_threads=torch.get_num_threads()),
               table=table, runs=runs)
    jp = os.path.join(HERE, 'sample_efficiency.json')
    json.dump(out, open(jp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    log('\nda ghi %s (%.1f phut)' % (jp, elapsed / 60))
    plot(out, os.path.join(HERE, 'sample_efficiency.png'))
    log('xong:', datetime.datetime.now().isoformat(timespec='seconds'))


def plot(out, path):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    T = out['table']
    C = dict(blue='#2a78d6', orange='#eb6834', ink='#0b0b0b', ink2='#52514e', grid='#e6e5e1')
    plt.rcParams.update({'font.size': 10, 'axes.edgecolor': C['ink2'], 'axes.labelcolor': C['ink'],
                         'xtick.color': C['ink2'], 'ytick.color': C['ink2'], 'axes.spines.top': False,
                         'axes.spines.right': False, 'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb'})
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))
    ks = [1, 2, 3]
    # (A) macro F1 gop + khoang min-max cua tung lan chay (giao thuc chinh)
    a = ax[0]
    y = [T[str(k)]['pooled']['macro_F1'] for k in ks]
    lo = [T[str(k)]['min_of_runs'] for k in ks]; hi = [T[str(k)]['max_of_runs'] for k in ks]
    a.fill_between(ks, lo, hi, color=C['blue'], alpha=0.15, lw=0, label='min–max của 5 lần chạy')
    a.plot(ks, y, color=C['blue'], lw=2, marker='o', ms=7, label='macro F1 gộp trên chủ thể giữ lại', zorder=3)
    for k, v, l, h in zip(ks, y, lo, hi):
        a.annotate('%.2f' % v, (k, v), xytext=(0, 9), textcoords='offset points', ha='center', fontsize=9, color=C['ink'])
        a.annotate('%.1f–%.1f' % (l, h), (k, l), xytext=(0, -13), textcoords='offset points', ha='center', fontsize=8, color=C['ink2'])
    for k in ks:
        for m in T[str(k)]['per_run_macro']:
            a.plot([k], [m], marker='_', ms=12, color=C['blue'], alpha=0.6, lw=0)
    a.set_xticks(ks); a.set_xticklabels(['k=1\nngưỡng cố định 0,45\n(5 lần)', 'k=2\nngưỡng val trong train\n(5 cặp)', 'k=3\nLORO, val riêng\n(5 fold, đã có)'])
    a.set_ylabel('macro F1 (%) trên (bản ghi × kênh) giữ lại'); a.set_ylim(0, 102)
    a.set_title('(A) F1 giữ lại theo số chủ thể huấn luyện', loc='left', fontsize=11)
    a.grid(axis='y', color=C['grid'], lw=0.8); a.set_axisbelow(True); a.legend(frameon=False, fontsize=8, loc='lower right')
    # (B) tach quy tac nguong: co dinh 0,45 vs chon tren val
    a = ax[1]
    yf = [T['1']['pooled']['macro_F1'], T['2_supp_fixed_thr']['pooled']['macro_F1']]
    yv = [T['1_supp_insample_thr']['pooled']['macro_F1'], T['2']['pooled']['macro_F1']]
    w = 0.34
    b1 = a.bar([1 - w / 2, 2 - w / 2], yf, width=w, color=C['blue'], label='ngưỡng cố định 0,45')
    b2 = a.bar([1 + w / 2, 2 + w / 2], yv, width=w, color=C['orange'], label='ngưỡng chọn trên bản ghi train (in-sample)')
    a.bar([3], [T['3']['pooled']['macro_F1']], width=w, color=C['ink2'], label='LORO: ngưỡng chọn trên val riêng')
    for bars in (b1, b2):
        for b in bars:
            a.annotate('%.1f' % b.get_height(), (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 3),
                       textcoords='offset points', ha='center', fontsize=8, color=C['ink'])
    a.annotate('%.1f' % T['3']['pooled']['macro_F1'], (3, T['3']['pooled']['macro_F1']), xytext=(0, 3),
               textcoords='offset points', ha='center', fontsize=8, color=C['ink'])
    a.set_xticks(ks); a.set_xticklabels(['k=1', 'k=2', 'k=3']); a.set_ylim(0, 102)
    a.set_ylabel('macro F1 (%) gộp'); a.set_title('(B) Ảnh hưởng của quy tắc chọn ngưỡng', loc='left', fontsize=11)
    a.grid(axis='y', color=C['grid'], lw=0.8); a.set_axisbelow(True); a.legend(frameon=False, fontsize=8, loc='lower right')
    fig.suptitle('ADFECGDB, 5 sản phụ; %d epoch, batch 32, recipe train_final.py; ±50 ms; k=3 lấy từ LORO đã có (không chạy lại)'
                 % out['meta']['epochs'], fontsize=9, color=C['ink2'], y=0.995)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)
    print('da ghi', path)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--epochs', type=int, default=0, help='0 = tu chon 6 hoac 4 theo ngan sach')
    ap.add_argument('--budget_min', type=float, default=40)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--plot_only', action='store_true')
    a = ap.parse_args()
    if a.plot_only:
        plot(json.load(open(os.path.join(HERE, 'sample_efficiency.json'), encoding='utf-8')), os.path.join(HERE, 'sample_efficiency.png'))
    else:
        main(a.epochs, a.budget_min, a.seed)
