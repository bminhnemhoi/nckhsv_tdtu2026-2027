# -*- coding: utf-8 -*-
"""
Duong cong F1 theo SNR (Phase P8, nhiem vu G, phan 1).

Nhieu chuan MIT-BIH NSTDB (Moody 1984): bw = troi duong nen, em = nhieu dien cuc, ma = nhieu co,
360 Hz, kenh 'noise1' (cot 0). Noi suy len 1000 Hz bang scipy.signal.resample_poly(x, 25, 9).
'mix' = tong ba loai sau khi chuan hoa moi loai ve phuong sai don vi.

Dinh nghia SNR (chuan, tinh tren TOAN BO ban ghi):
    SNR_dB = 10*log10(P_signal / P_noise)
    P_signal = mean((s - mean(s))^2)  voi s = tin hieu bung THO 1000 Hz (mot kenh, 5 phut) -- tuc la
               phuong sai cua ca ban ghi, gom ca ECG me (thanh phan ap dao) + ECG thai + nhieu san co.
    P_noise  = mean((n - mean(n))^2)  voi n = doan nhieu duoc cong vao.
    y = s + a*(n - mean(n)),  a = sqrt(P_signal / (P_noise * 10^(SNR/10))).
    LUU Y: SNR o day la so voi TOAN BO tin hieu bung (chu yeu la QRS me), KHONG phai so voi
    rieng thanh phan thai (thanh phan thai nho hon me nhieu). 0 dB nghia la nhieu co cong suat
    bang ca tin hieu bung.

Doan nhieu: offset ngau nhien trong ban ghi nhieu 30 phut, seed co dinh
    rng = np.random.default_rng([SEED, chi_so_ban_ghi, kenh, chi_so_loai_nhieu]);
    cung mot offset cho moi muc SNR (de cac muc SNR so sanh duoc voi nhau).

Mo hinh: checkpoint fold_rXX (khong huan luyen tren rXX), nguong lay tu checkpoint (chon tren ban ghi
val cua fold), M.preprocess -> M.cancel_maternal -> M.robust_scale -> M.probability_series -> M.pick_peaks.
Baseline: TS-PCA (n_pc=2) + Pan-Tompkins thich nghi (thr_frac=0,75) -- tham so chon tren r01 trong
baselines/ts_baseline.py, import nguyen ham. Cham +/-50 ms tai 1000 Hz bang M.match_events.
Kenh PSD mu nhan: pick_blind() cua benchmark_dpss/blind_lead.py ap len phan du cua moi phuong phap.

Chay:  PYTHONIOENCODING=utf-8 python pilot_evidence/snr_curve.py [--quick]
Ghi:   pilot_evidence/snr_curve.json, snr_curve.png, snr_log.txt
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, argparse, datetime, importlib.util
import numpy as np, torch, mne, wfdb
from scipy import signal as sg

torch.set_num_threads(3)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
from _paths import adfecgdb_dir, checkpoint
from blind_lead import pick_blind
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG = M.CFG
spec2 = importlib.util.spec_from_file_location('ts_baseline', os.path.join(ROOT, 'baselines', 'ts_baseline.py'))
TSB = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(TSB)

RECS = ['r01', 'r04', 'r07', 'r08', 'r10']
LEADS = (1, 2, 3, 4)
NOISE_TYPES = ['bw', 'em', 'ma', 'mix']
SNRS = [20, 15, 10, 5, 0, -5]
SEED = 0
FS_IN = CFG['fs_in']; UP = FS_IN // CFG['fs']; TOL = CFG['tolerance_ms']
NSTDB = os.path.join(ROOT, 'model', 'data', 'nstdb')
TSPCA_NPC = 2; TSPCA_THR_FRAC = 0.75     # tu baselines/results.json: tuning_r01.chosen.TS_PCA


class Tee:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.s = sys.stdout
    def write(self, t): self.s.write(t); self.f.write(t)
    def flush(self): self.s.flush(); self.f.flush()


def load_noise():
    out = {}
    for t in ('bw', 'em', 'ma'):
        r = wfdb.rdrecord(os.path.join(NSTDB, t))
        assert r.fs == 360, r.fs
        x = np.asarray(r.p_signal[:, 0], np.float64)            # kenh 'noise1'
        x = sg.resample_poly(x, 25, 9)                           # 360 -> 1000 Hz
        out[t] = (x - x.mean()).astype(np.float32)
        del x
    return out


def make_noise_segment(noise, t, n, rng):
    """tra ve doan nhieu dai n (chua chuan hoa), da tru trung binh."""
    if t == 'mix':
        seg = np.zeros(n, np.float64)
        for tt in ('bw', 'em', 'ma'):
            s = make_noise_segment(noise, tt, n, rng)
            seg += s / (s.std() + 1e-12)
        return seg
    src = noise[t]; off = int(rng.integers(0, len(src) - n))
    seg = src[off:off + n].astype(np.float64)
    return seg - seg.mean()


def add_noise(s, seg, snr_db):
    p_sig = float(np.mean((s - s.mean()) ** 2)); p_n = float(np.mean(seg ** 2))
    a = np.sqrt(p_sig / (p_n * 10 ** (snr_db / 10.0)))
    return s + a * seg, p_sig, p_n, float(a)


def clean_metrics(m):
    return {k: (float(v) if isinstance(v, (float, np.floating)) else int(v)) for k, v in m.items()}


def run_model(net, thr, y):
    x250 = M.preprocess(y, FS_IN, CFG); res, _ = M.cancel_maternal(x250, CFG)
    prob = M.probability_series(net, M.robust_scale(res).astype(np.float32),
                                M.robust_scale(x250).astype(np.float32), CFG)
    det = M.pick_peaks(prob, thr, CFG).astype(np.int64) * UP
    return det, res, x250


def run_tspca(x250):
    res = TSB.cancel_ts_pca(x250, npc=TSPCA_NPC)[0]
    det = TSB.pan_tompkins_fetal(res, thr_frac=TSPCA_THR_FRAC).astype(np.int64) * UP
    return det, res


def main(quick=False):
    t0 = time.time()
    sys.stdout = Tee(os.path.join(HERE, 'snr_log.txt'))
    print('=' * 96)
    print('DUONG CONG F1-SNR -- ADFECGDB x nhieu NSTDB (bw/em/ma/mix), mo hinh fold vs TS-PCA')
    print('bat dau:', datetime.datetime.now().isoformat(timespec='seconds'), '| quick =', quick)
    print('numpy %s scipy %s torch %s mne %s wfdb %s | torch threads %d'
          % (np.__version__, __import__('scipy').__version__, torch.__version__, mne.__version__,
             wfdb.__version__, torch.get_num_threads()))
    print('=' * 96)
    RAW = adfecgdb_dir(); print('ADFECGDB:', RAW, '| NSTDB:', NSTDB)
    snrs = [20, 5, -5] if quick else SNRS
    types = ['mix', 'ma'] if quick else NOISE_TYPES

    noise = load_noise()
    for t in noise:
        print('  nhieu %s: %d mau @1000 Hz (%.1f phut), std %.4f mV' % (t, len(noise[t]), len(noise[t]) / 60000, noise[t].std()))

    SIG, GT, NET, THR = {}, {}, {}, {}
    for rec in RECS:
        raw = mne.io.read_raw_edf(os.path.join(RAW, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data(); del raw
        SIG[rec] = {ld: np.asarray(sig[ld], np.float64) for ld in LEADS}; del sig
        GT[rec] = np.asarray(wfdb.rdann(os.path.join(RAW, rec), 'edf.qrs').sample, int)
        b = torch.load(checkpoint('fetalqrs_tcn_fold_%s.pt' % rec), map_location='cpu', weights_only=False)
        assert b['test_record'] == rec and rec not in b['train_records'], (rec, b['train_records'])
        net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
        NET[rec] = net; THR[rec] = float(b['threshold'])
        print('  %s: %d mau, %d nhan thai, fold ckpt train=%s val=%s thr=%.2f'
              % (rec, len(SIG[rec][1]), len(GT[rec]), b['train_records'], b['val_record'], THR[rec]))
        del b

    # ---------------------------------------------------------------- [1] khong nhieu
    print('\n[1] khong nhieu (kiem tra tai lap all_leads.json / baselines/results.json)')
    clean = dict(model={}, tspca={}, psd={})
    for rec in RECS:
        clean['model'][rec] = {}; clean['tspca'][rec] = {}
        rm, rt = {}, {}
        for ld in LEADS:
            det, res, x250 = run_model(NET[rec], THR[rec], SIG[rec][ld])
            clean['model'][rec][str(ld)] = clean_metrics(M.match_events(det, GT[rec], FS_IN, TOL)); rm[ld] = res
            det2, res2 = run_tspca(x250)
            clean['tspca'][rec][str(ld)] = clean_metrics(M.match_events(det2, GT[rec], FS_IN, TOL)); rt[ld] = res2
        lm, lt = int(pick_blind(rm)), int(pick_blind(rt))
        clean['psd'][rec] = dict(model_lead=lm, model_F1=clean['model'][rec][str(lm)]['F1'],
                                 tspca_lead=lt, tspca_F1=clean['tspca'][rec][str(lt)]['F1'])
        print('  %s  mo hinh: %s  PSD->kenh %d | TS-PCA: %s  PSD->kenh %d' % (
            rec, ['%.2f' % clean['model'][rec][str(l)]['F1'] for l in LEADS], lm,
            ['%.2f' % clean['tspca'][rec][str(l)]['F1'] for l in LEADS], lt))
    c_model = float(np.mean([clean['model'][r][str(l)]['F1'] for r in RECS for l in LEADS]))
    c_tspca = float(np.mean([clean['tspca'][r][str(l)]['F1'] for r in RECS for l in LEADS]))
    c_psd_m = float(np.mean([clean['psd'][r]['model_F1'] for r in RECS]))
    c_psd_t = float(np.mean([clean['psd'][r]['tspca_F1'] for r in RECS]))
    print('  KHONG NHIEU: mo hinh 4 kenh %.2f | kenh PSD %.2f || TS-PCA 4 kenh %.2f | kenh PSD %.2f'
          % (c_model, c_psd_m, c_tspca, c_psd_t))

    # ---------------------------------------------------------------- [2] luoi nhieu
    print('\n[2] luoi: %d ban ghi x 4 kenh x %s x SNR %s dB' % (len(RECS), types, snrs))
    grid = {rec: {str(ld): {t: {} for t in types} for ld in LEADS} for rec in RECS}
    psd = {rec: {t: {} for t in types} for rec in RECS}
    n_done = 0; n_total = len(RECS) * len(LEADS) * len(types) * len(snrs)
    for ri, rec in enumerate(RECS):
        for t in types:
            segs = {}
            for ld in LEADS:
                rng = np.random.default_rng([SEED, ri, ld, NOISE_TYPES.index(t)])
                segs[ld] = make_noise_segment(noise, t, len(SIG[rec][ld]), rng)
            for snr in snrs:
                rm, rt = {}, {}
                for ld in LEADS:
                    y, p_sig, p_n, a = add_noise(SIG[rec][ld], segs[ld], snr)
                    det, res, x250 = run_model(NET[rec], THR[rec], y)
                    mm = clean_metrics(M.match_events(det, GT[rec], FS_IN, TOL)); rm[ld] = res
                    det2, res2 = run_tspca(x250)
                    mt = clean_metrics(M.match_events(det2, GT[rec], FS_IN, TOL)); rt[ld] = res2
                    grid[rec][str(ld)][t][str(snr)] = dict(
                        model=mm, tspca=mt, n_det_model=int(len(det)), n_det_tspca=int(len(det2)),
                        P_signal=p_sig, P_noise_unit=p_n, scale_a=a)
                    del y, det, res, x250, det2, res2
                    n_done += 1
                lm, lt = int(pick_blind(rm)), int(pick_blind(rt))
                psd[rec][t][str(snr)] = dict(
                    model_lead=lm, model_F1=grid[rec][str(lm)][t][str(snr)]['model']['F1'],
                    model_lead_same_as_clean=bool(lm == clean['psd'][rec]['model_lead']),
                    model_oracle_F1=max(grid[rec][str(l)][t][str(snr)]['model']['F1'] for l in LEADS),
                    tspca_lead=lt, tspca_F1=grid[rec][str(lt)][t][str(snr)]['tspca']['F1'],
                    tspca_lead_same_as_clean=bool(lt == clean['psd'][rec]['tspca_lead']))
                fm = [grid[rec][str(l)][t][str(snr)]['model']['F1'] for l in LEADS]
                ft = [grid[rec][str(l)][t][str(snr)]['tspca']['F1'] for l in LEADS]
                print('  %s %-3s %+3d dB | mo hinh %s TB %.2f PSD k%d %.2f | TS-PCA %s TB %.2f PSD k%d %.2f | %d/%d %.0fs'
                      % (rec, t, snr, ['%.1f' % v for v in fm], np.mean(fm), lm, psd[rec][t][str(snr)]['model_F1'],
                         ['%.1f' % v for v in ft], np.mean(ft), lt, psd[rec][t][str(snr)]['tspca_F1'],
                         n_done, n_total, time.time() - t0), flush=True)
            del segs

    # ---------------------------------------------------------------- [3] tong hop
    def mean20(method, t, snr):
        v = [grid[r][str(l)][t][str(snr)][method]['F1'] for r in RECS for l in LEADS]
        return float(np.mean(v)), float(np.std(v, ddof=1))

    def micro(method, t, snr):
        tp = sum(grid[r][str(l)][t][str(snr)][method]['TP'] for r in RECS for l in LEADS)
        fp = sum(grid[r][str(l)][t][str(snr)][method]['FP'] for r in RECS for l in LEADS)
        fn = sum(grid[r][str(l)][t][str(snr)][method]['FN'] for r in RECS for l in LEADS)
        return dict(TP=tp, FP=fp, FN=fn, Se=100 * tp / max(tp + fn, 1), PPV=100 * tp / max(tp + fp, 1),
                    F1=200 * tp / max(2 * tp + fp + fn, 1))

    summary = dict(clean=dict(model_4lead=c_model, model_psd=c_psd_m, tspca_4lead=c_tspca, tspca_psd=c_psd_t),
                   model={}, tspca={}, psd_model={}, psd_tspca={}, psd_model_lead_stable={}, micro_model={}, micro_tspca={})
    for t in types:
        summary['model'][t] = {}; summary['tspca'][t] = {}; summary['psd_model'][t] = {}; summary['psd_tspca'][t] = {}
        summary['psd_model_lead_stable'][t] = {}; summary['micro_model'][t] = {}; summary['micro_tspca'][t] = {}
        for snr in snrs:
            m, sd = mean20('model', t, snr); summary['model'][t][str(snr)] = dict(F1_mean=m, F1_sd=sd)
            m2, sd2 = mean20('tspca', t, snr); summary['tspca'][t][str(snr)] = dict(F1_mean=m2, F1_sd=sd2)
            summary['psd_model'][t][str(snr)] = float(np.mean([psd[r][t][str(snr)]['model_F1'] for r in RECS]))
            summary['psd_tspca'][t][str(snr)] = float(np.mean([psd[r][t][str(snr)]['tspca_F1'] for r in RECS]))
            summary['psd_model_lead_stable'][t][str(snr)] = int(sum(psd[r][t][str(snr)]['model_lead_same_as_clean'] for r in RECS))
            summary['micro_model'][t][str(snr)] = micro('model', t, snr)
            summary['micro_tspca'][t][str(snr)] = micro('tspca', t, snr)
    single = [t for t in ('bw', 'em', 'ma') if t in types]
    summary['model_avg_bw_em_ma'] = {str(s): float(np.mean([summary['model'][t][str(s)]['F1_mean'] for t in single])) for s in snrs} if single else {}
    summary['tspca_avg_bw_em_ma'] = {str(s): float(np.mean([summary['tspca'][t][str(s)]['F1_mean'] for t in single])) for s in snrs} if single else {}
    # SNR tai do F1 (mo hinh, mix) roi duoi 90 / 80: muc SNR cao nhat trong luoi ma F1 < nguong (khong noi suy)
    thresholds = {}
    for t in types:
        thresholds[t] = {}
        for method in ('model', 'tspca'):
            for lim in (90, 80):
                below = [s for s in snrs if summary[method][t][str(s)]['F1_mean'] < lim]
                thresholds[t]['%s_below_%d' % (method, lim)] = (max(below) if below else None)
    summary['snr_first_below'] = thresholds
    worst = {str(s): min(single, key=lambda t: summary['model'][t][str(s)]['F1_mean']) for s in snrs} if single else {}
    summary['model_worst_noise_type_per_snr'] = worst

    print('\n' + '-' * 96)
    print('MACRO F1 (TB 20 = 5 ban ghi x 4 kenh) theo SNR   [khong nhieu: mo hinh %.2f, TS-PCA %.2f]' % (c_model, c_tspca))
    print('-' * 96)
    print('%-16s' % 'SNR (dB)' + ''.join('%9s' % ('%+d' % s) for s in snrs))
    for method in ('model', 'tspca'):
        for t in types:
            print('%-16s' % ('%s/%s' % ('Mo hinh' if method == 'model' else 'TS-PCA', t))
                  + ''.join('%9.2f' % summary[method][t][str(s)]['F1_mean'] for s in snrs))
    print('-' * 96)
    print('Kenh PSD mu nhan (TB 5 ban ghi)  [khong nhieu: mo hinh %.2f, TS-PCA %.2f]' % (c_psd_m, c_psd_t))
    for t in types:
        print('%-16s' % ('PSD mo hinh/%s' % t) + ''.join('%9.2f' % summary['psd_model'][t][str(s)] for s in snrs)
              + '   kenh giu nguyen: ' + '/'.join('%d' % summary['psd_model_lead_stable'][t][str(s)] for s in snrs) + ' (tren 5)')
    for t in types:
        print('%-16s' % ('PSD TS-PCA/%s' % t) + ''.join('%9.2f' % summary['psd_tspca'][t][str(s)] for s in snrs))
    print('SNR dau tien (cao nhat) ma F1 < 90 / < 80:', json.dumps(thresholds))
    print('Loai nhieu hai nhat cho mo hinh theo SNR:', worst)

    elapsed = time.time() - t0
    meta = dict(
        ngay=datetime.datetime.now().isoformat(timespec='seconds'), thoi_gian_chay_s=round(elapsed, 1), quick=quick,
        nhieu='MIT-BIH NSTDB (Moody 1984) bw/em/ma, kenh noise1 (cot 0), 360 Hz -> 1000 Hz resample_poly(25, 9); '
              'mix = tong ba loai sau khi chuan hoa moi loai ve phuong sai don vi',
        dinh_nghia_snr='SNR_dB = 10*log10(P_signal/P_noise); P_signal = phuong sai cua tin hieu bung THO 1000 Hz tren toan ban ghi '
                       '(gom ECG me ap dao + ECG thai + nhieu san co); P_noise = phuong sai doan nhieu cong vao; '
                       'y = s + a*(n-mean(n)), a = sqrt(P_signal/(P_noise*10^(SNR/10))). SNR so voi TOAN BO tin hieu bung, '
                       'khong phai so voi rieng thanh phan thai.',
        doan_nhieu='offset ngau nhien, rng = default_rng([SEED=%d, chi_so_ban_ghi, kenh, chi_so_loai]); cung offset cho moi SNR; '
                   'moi kenh mot doan doc lap' % SEED,
        mo_hinh='checkpoint fold_rXX (rXX ngoai train/val), nguong tu checkpoint (chon tren ban ghi val cua fold); '
                'M.preprocess -> M.cancel_maternal -> robust_scale -> M.probability_series -> M.pick_peaks',
        tspca='baselines/ts_baseline.py cancel_ts_pca(npc=%d) + pan_tompkins_fetal(thr_frac=%.2f) (chon tren r01)' % (TSPCA_NPC, TSPCA_THR_FRAC),
        cham='+/-%d ms tai 1000 Hz, ghep 1-1 tham lam M.match_events; macro F1 = TB 20 (ban ghi x kenh)' % TOL,
        kenh_psd='benchmark_dpss/blind_lead.pick_blind tren phan du cua tung phuong phap trong DIEU KIEN NHIEU do',
        thresholds_fold={r: THR[r] for r in RECS}, snrs=snrs, noise_types=types, seed=SEED,
        phien_ban=dict(python=sys.version.split()[0], numpy=np.__version__, scipy=__import__('scipy').__version__,
                       torch=torch.__version__, mne=mne.__version__, wfdb=wfdb.__version__),
        torch_threads=torch.get_num_threads())
    out = dict(meta=meta, summary=summary, clean=clean, grid=grid, psd=psd)
    jp = os.path.join(HERE, 'snr_curve.json' if not quick else 'snr_curve_quick.json')
    json.dump(out, open(jp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('\nda ghi %s (%.1f s)' % (jp, elapsed))
    if not quick:
        plot(out, os.path.join(HERE, 'snr_curve.png'))
    print('xong:', datetime.datetime.now().isoformat(timespec='seconds'))


# -------------------------------------------------------------------- ve hinh
def plot(out, path):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    S = out['summary']; snrs = out['meta']['snrs']; types = out['meta']['noise_types']
    C = dict(blue='#2a78d6', orange='#eb6834', aqua='#1baf7a', yellow='#eda100', ink='#0b0b0b', ink2='#52514e', grid='#e6e5e1')
    plt.rcParams.update({'font.size': 10, 'axes.edgecolor': C['ink2'], 'axes.labelcolor': C['ink'],
                         'xtick.color': C['ink2'], 'ytick.color': C['ink2'], 'axes.spines.top': False,
                         'axes.spines.right': False, 'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb'})
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
    x = list(range(len(snrs)))

    def line(a, ys, color, ls, label, marker='o'):
        a.plot(x, ys, color=color, ls=ls, lw=2, marker=marker, ms=6, label=label, zorder=3)
        a.annotate('%.1f' % ys[-1], (x[-1], ys[-1]), xytext=(6, 0), textcoords='offset points', va='center',
                   fontsize=8, color=C['ink2'])

    # (A) 4 duong + duong ngang khong nhieu
    a = ax[0]
    line(a, [S['model']['mix'][str(s)]['F1_mean'] for s in snrs], C['blue'], '-', 'Mô hình, nhiễu mix')
    line(a, [S['model_avg_bw_em_ma'][str(s)] for s in snrs], C['blue'], '--', 'Mô hình, TB bw/em/ma', 's')
    line(a, [S['tspca']['mix'][str(s)]['F1_mean'] for s in snrs], C['orange'], '-', 'TS-PCA, nhiễu mix')
    line(a, [S['tspca_avg_bw_em_ma'][str(s)] for s in snrs], C['orange'], '--', 'TS-PCA, TB bw/em/ma', 's')
    a.axhline(S['clean']['model_4lead'], color=C['blue'], ls=':', lw=1.2)
    a.axhline(S['clean']['tspca_4lead'], color=C['orange'], ls=':', lw=1.2)
    a.text(0, S['clean']['model_4lead'] + 0.6, 'không nhiễu, mô hình %.2f' % S['clean']['model_4lead'], fontsize=8, color=C['ink2'])
    a.text(0, S['clean']['tspca_4lead'] - 2.4, 'không nhiễu, TS-PCA %.2f' % S['clean']['tspca_4lead'], fontsize=8, color=C['ink2'])
    a.set_title('(A) Macro F1 (5 bản ghi × 4 kênh) theo SNR', loc='left', fontsize=11)
    a.legend(frameon=False, fontsize=8, loc='lower left')

    # (B) mo hinh theo tung loai nhieu
    a = ax[1]
    for t, col, mk in zip(['bw', 'em', 'ma', 'mix'], [C['blue'], C['orange'], C['aqua'], C['yellow']], 'os^D'):
        if t in types:
            line(a, [S['model'][t][str(s)]['F1_mean'] for s in snrs], col, '-', 'Mô hình, ' + t, mk)
    a.axhline(S['clean']['model_4lead'], color=C['ink2'], ls=':', lw=1.2)
    a.set_title('(B) Mô hình theo từng loại nhiễu', loc='left', fontsize=11)
    a.legend(frameon=False, fontsize=8, loc='lower left')

    # (C) kenh PSD mu nhan
    a = ax[2]
    line(a, [S['psd_model']['mix'][str(s)] for s in snrs], C['blue'], '-', 'Mô hình, kênh PSD (mix)')
    line(a, [S['model']['mix'][str(s)]['F1_mean'] for s in snrs], C['blue'], '--', 'Mô hình, TB 4 kênh (mix)', 's')
    line(a, [S['psd_tspca']['mix'][str(s)] for s in snrs], C['orange'], '-', 'TS-PCA, kênh PSD (mix)')
    a.axhline(S['clean']['model_psd'], color=C['blue'], ls=':', lw=1.2)
    a.text(0, S['clean']['model_psd'] + 0.6, 'không nhiễu, kênh PSD %.2f' % S['clean']['model_psd'], fontsize=8, color=C['ink2'])
    for i, s in enumerate(snrs):
        a.text(i, 2, '%d/5' % S['psd_model_lead_stable']['mix'][str(s)], ha='center', fontsize=8, color=C['ink2'])
    a.text(0, 6, 'số bản ghi giữ nguyên kênh PSD so với không nhiễu:', fontsize=8, color=C['ink2'])
    a.set_title('(C) Quy tắc chọn kênh PSD mù nhãn dưới nhiễu', loc='left', fontsize=11)
    a.legend(frameon=False, fontsize=8, loc='center left')

    for a in ax:
        a.set_xticks(x); a.set_xticklabels(['%+d' % s for s in snrs]); a.set_xlabel('SNR (dB) — nhiễu tăng dần sang phải')
        a.set_ylim(0, 102); a.set_ylabel('F1 (%)'); a.grid(axis='y', color=C['grid'], lw=0.8); a.set_axisbelow(True)
        a.set_xlim(-0.3, len(snrs) - 0.4)
    fig.suptitle('ADFECGDB + nhiễu MIT-BIH NSTDB; SNR so với toàn bộ tín hiệu bụng thô; ±50 ms; mô hình = checkpoint fold (giữ bản ghi ngoài), TS-PCA n_pc=2, thr_frac=0,75',
                 fontsize=9, color=C['ink2'], y=0.995)
    fig.tight_layout()
    fig.savefig(path, dpi=150); plt.close(fig)
    print('da ghi', path)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true', help='chi 3 SNR x 2 loai nhieu, ghi snr_curve_quick.json')
    ap.add_argument('--plot_only', action='store_true')
    a = ap.parse_args()
    if a.plot_only:
        plot(json.load(open(os.path.join(HERE, 'snr_curve.json'), encoding='utf-8')), os.path.join(HERE, 'snr_curve.png'))
    else:
        main(a.quick)
