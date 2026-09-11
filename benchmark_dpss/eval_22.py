# -*- coding: utf-8 -*-
"""
Danh gia DOC LAP cac checkpoint FetalQRS-TCN huan luyen tren 22 san phu (model/train_22.py):
    fetalqrs_tcn_22_fold_XX.pt  (11 fold, moi fold giu lai 2 chu the; nguong chon tren val rieng)
    fetalqrs_tcn_22_production.pt (train tren ca 22; chi dung cho zero-shot CinC 2013)

Voi moi fold co san: nap checkpoint -> test_subjects -> tung chu the x 4 dao trinh bung, pipeline chuan
(M.preprocess 10-60 Hz @250 Hz -> M.cancel_maternal -> M.probability_series -> M.pick_peaks(nguong cua blob) -> x4
-> M.match_events +/-50 ms @1000 Hz). Bao cao F1/Se/PPV/jitter tung (chu the x kenh), kenh PSD mu nhan (pick_blind,
Power-MF tren phan du chua chuan hoa nhu blind_lead.py) va do lech co dau trung vi (phat hien - nhan) ms tren cac cap
khop (nhu silesia_eval.py) de kiem tra nhan gian tiep B1 co keo mo hinh lech hay khong.

Dat canh mo hinh n=5 (train 5 PhysioNet) tren CUNG chu the / kenh:
    B1, B2 : benchmark_dpss/silesia_eval.json  (checkpoint production_5, chua tung thay Silesia)
    PhysioNet: tinh lai tai cho bang fetalqrs_tcn_fold_rXX.pt (LORO, chua thay rXX) va doi chieu voi
               all_leads.json + blind_lead.json (phai khop).
Wilcoxon ghep cap (scipy.stats.wilcoxon) model_22 vs model_5 theo (chu the x kenh) va theo kenh PSD (n = chu the).

Neu co production_22: zero-shot CinC 2013 set-a (a01-a10, 4 kenh, 1000 Hz, nhan fqrs), dat canh production_5
(blind_lead.json['cinc']).

Chay:  python benchmark_dpss/eval_22.py --partial                 (bat ky so fold nao da co)
       python benchmark_dpss/eval_22.py --partial --wait-min 20   (chua co fold nao -> doi toi da 20 phut, 2 phut/lan)
       python benchmark_dpss/eval_22.py --partial --no-cache      (tinh lai tat ca, bo cache theo mtime checkpoint)
Ket qua (ghi de moi lan): eval_22.json, eval_22_log.txt, eval_22_partial_status.txt, eval_22_cache.json
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, argparse, importlib.util, datetime, platform, gc, glob, re
import numpy as np, torch, mne, wfdb
from scipy import signal as sg
from scipy.stats import wilcoxon

torch.set_num_threads(int(os.environ.get('FQRS_THREADS', 2)))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _paths import adfecgdb_dir, cinc2013_dir


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


M = _load('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py')); CFG = M.CFG
L = _load('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))

CKPT_DIR = os.environ.get('FQRS_CKPT_DIR') or os.path.join(ROOT, 'model', 'checkpoints')   # FQRS_CKPT_DIR: chi de thu nghiem
N5_DIR = os.path.join(ROOT, 'model', 'checkpoints')                                          # checkpoint n=5 (fold_rXX)
OUT_DIR = os.environ.get('FQRS_EVAL_OUT') or HERE                                            # FQRS_EVAL_OUT: chi de thu nghiem
OUT_JSON = os.path.join(OUT_DIR, 'eval_22.json')
OUT_LOG = os.path.join(OUT_DIR, 'eval_22_log.txt')
OUT_STATUS = os.path.join(OUT_DIR, 'eval_22_partial_status.txt')
OUT_CACHE = os.path.join(OUT_DIR, 'eval_22_cache.json')
SILESIA_JSON = os.path.join(HERE, 'silesia_eval.json')
ALL_LEADS_JSON = os.path.join(HERE, 'all_leads.json')
BLIND_JSON = os.path.join(HERE, 'blind_lead.json')

# cung danh sach voi train_22.py (sao chep de eval khong phu thuoc viec import train_22 dang chay)
PHYSIONET = ['r01', 'r04', 'r07', 'r08', 'r10']
B1 = [f'B1_{i:02d}' for i in range(1, 11)]
B2 = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
B2_DUPLICATES = {'B2_01': 'r01', 'B2_02': 'r10', 'B2_07': 'r04', 'B2_10': 'r07', 'B2_11': 'r08'}
ALL = PHYSIONET + B1 + B2
GROUPS = ('PhysioNet', 'B2', 'B1')
LEADS = (1, 2, 3, 4)
Q = CFG['fs_in'] // CFG['fs']
TOL_MS = 50; FHR_BAND = (1.8, 3.0); N_FOLDS = 11
# production_5 tren CinC 2013 (facts_verified.json / blind_lead.json): kenh 0 / PSD / TB4 ; so >=90 / <50 do tu file
CINC_REF_STATED = dict(F1_lead0=77.34, F1_psd=59.15, F1_mean4=61.96, n_ge90=4, n_lt50=5)


class Tee:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.o = sys.stdout
    def write(self, s):
        self.o.write(s); self.f.write(s); self.f.flush()
    def flush(self):
        self.o.flush(); self.f.flush()


def group_of(tag):
    return 'PhysioNet' if tag.startswith('r') else tag[:2]


# ------------------------------------------------------------------ chon kenh mu nhan (nhu blind_lead.py)
def psd_score(x250, fs=250):
    e = np.abs(sg.hilbert(x250 - np.mean(x250))); e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def pick_blind(residuals):
    return max(residuals, key=lambda l: psd_score(residuals[l]))


# ------------------------------------------------------------------ cham diem (nhu silesia_eval.py)
def signed_bias(det, ref, tol_ms=TOL_MS):
    """trung vi (phat hien - nhan) ms tren cac cap trong +/-tol; am = nhan nam SAU dinh phat hien."""
    det = np.sort(np.asarray(det, float)); ref = np.sort(np.asarray(ref, float))
    if not len(det) or not len(ref):
        return float('nan')
    j = np.clip(np.searchsorted(ref, det), 1, len(ref) - 1)
    cand = np.stack([det - ref[j - 1], det - ref[j]])
    s = cand[np.abs(cand).argmin(0), np.arange(len(det))]
    s = s[np.abs(s) <= tol_ms]
    return float(np.median(s)) if len(s) else float('nan')


def match_flagged(det, ref, flags, fs, tol_ms):
    """nhu M.match_events nhung nhip co=0 (B1, chuyen gia khong xac nhan) la 'khong quan tam'."""
    tol = tol_ms / 1000 * fs
    ref = np.asarray(ref, float); det = np.sort(np.asarray(det, float)); flags = np.asarray(flags, int)
    used = np.zeros(len(ref), bool); tp = 0; dc = 0; errs = []
    for d in det:
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (~used))[0]
        if len(ok):
            j = ok[int(np.argmin(dd[ok]))]; used[j] = True
            if flags[j] == 1:
                tp += 1; errs.append(dd[j] / fs * 1000)
            else:
                dc += 1
    fp = len(det) - tp - dc
    fn = int(((~used) & (flags == 1)).sum())
    se = tp / (tp + fn) * 100 if tp + fn else 0.0
    ppv = tp / (tp + fp) * 100 if tp + fp else 0.0
    return dict(TP=tp, FP=fp, FN=fn, ignored=dc, Se=se, PPV=ppv,
                F1=2 * se * ppv / (se + ppv) if se + ppv else 0.0,
                jitter_ms=float(np.mean(errs)) if errs else float('nan'))


def score(det1000, fq1000, flags=None):
    m = M.match_events(det1000, fq1000, CFG['fs_in'], TOL_MS)
    m['n_det'] = int(len(det1000)); m['n_ref'] = int(len(fq1000)); m['bias_ms'] = signed_bias(det1000, fq1000)
    if flags is not None:
        m['verified_only'] = match_flagged(det1000, fq1000, flags, CFG['fs_in'], TOL_MS)
    return m


# ------------------------------------------------------------------ du lieu
def load_subject(tag):
    """-> dict(lead -> dict(r_s, x_s, psd)), fq1000, flags(None neu da dau), meta"""
    g = group_of(tag); flags = None; meta = {}
    if g == 'PhysioNet':
        D = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        fq1000 = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, int)
        chans = {lead: sig[lead] for lead in LEADS}
        meta = dict(duration_s=float(sig.shape[1] / 1000.0), label='DIRECT scalp FECG (ADFECGDB)')
        del raw, sig
    else:
        sig, _, mt = L.load(tag)
        fq1000 = np.asarray(mt['fqrs_all'], int)
        chans = {lead: sig[lead - 1] for lead in LEADS}
        if g == 'B1':
            flags = np.asarray(mt['fqrs_flags'], int)
        meta = dict(duration_s=float(mt['duration_s']), n_ref_flag0=int(mt['n_fqrs_flag0']),
                    fhr_median_bpm=float(mt['fhr_median_bpm']), label=mt['reference_source'])
        del sig
    out = {}
    for lead in LEADS:
        x = M.preprocess(chans[lead], CFG['fs_in'], CFG); r, _ = M.cancel_maternal(x, CFG)
        out[lead] = dict(r_s=M.robust_scale(r).astype(np.float32), x_s=M.robust_scale(x).astype(np.float32),
                         psd=psd_score(r))
    del chans
    return out, fq1000, flags, meta


def run_net(net, thr, prep, fq1000, flags):
    per = {}
    for lead in LEADS:
        p = M.probability_series(net, prep[lead]['r_s'], prep[lead]['x_s'], CFG)
        det = M.pick_peaks(p, thr, CFG).astype(np.int64) * Q
        per[lead] = score(det, fq1000, flags)
    return per


def summarize_leads(per, psd_lead, thr):
    f1s = [per[l]['F1'] for l in LEADS]
    out = dict(psd_lead=int(psd_lead), threshold=float(thr), per_lead={f'A{l}': per[l] for l in LEADS},
               F1_psd=per[psd_lead]['F1'], Se_psd=per[psd_lead]['Se'], PPV_psd=per[psd_lead]['PPV'],
               jitter_psd=per[psd_lead]['jitter_ms'], bias_psd=per[psd_lead]['bias_ms'],
               F1_mean4=float(np.mean(f1s)), F1_oracle=float(max(f1s)), oracle_lead=int(LEADS[int(np.argmax(f1s))]),
               bias_median4=float(np.nanmedian([per[l]['bias_ms'] for l in LEADS])),
               jitter_mean4=float(np.nanmean([per[l]['jitter_ms'] for l in LEADS])))
    if 'verified_only' in per[LEADS[0]]:
        out['F1_psd_verified_only'] = per[psd_lead]['verified_only']['F1']
        out['F1_mean4_verified_only'] = float(np.mean([per[l]['verified_only']['F1'] for l in LEADS]))
    return out


def load_net(path):
    b = torch.load(path, map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
    return net, float(b['threshold']), b


# ------------------------------------------------------------------ mo hinh n=5 tren cung chu the
def ref5_silesia(tag, sil):
    """tu silesia_eval.json: production_5 tren B1 / B2 khong trung (checkpoint 'production')."""
    if not sil or tag not in sil.get('records', {}):
        return None
    e = sil['records'][tag]
    per = {l: dict(e['per_lead'][f'A{l}']) for l in LEADS}
    for l in LEADS:
        per[l].pop('verified_only', None)
    out = summarize_leads(per, int(e['psd_lead']) + 1, sil['meta']['thresholds'].get(e['checkpoint'], float('nan')))
    out['checkpoint'] = e['checkpoint']; out['source'] = 'silesia_eval.json'
    if 'F1_psd_verified_only' in e:
        out['F1_psd_verified_only'] = e['F1_psd_verified_only']; out['F1_mean4_verified_only'] = e['F1_mean4_verified_only']
    return out


def ref5_physionet(tag, prep, fq1000, psd_lead, all_leads, blind):
    """tinh lai fold_rXX (LORO n=5) tren rXX voi cung pipeline, doi chieu all_leads.json + blind_lead.json."""
    p = os.path.join(N5_DIR, f'fetalqrs_tcn_fold_{tag}.pt')
    if not os.path.isfile(p):
        return None
    net, thr, _ = load_net(p)
    per = run_net(net, thr, prep, fq1000, None)
    out = summarize_leads(per, psd_lead, thr); out['checkpoint'] = f'fold_{tag}'; out['source'] = 'recomputed fold_rXX (n=5 LORO)'
    chk = {}
    if all_leads and tag in all_leads:
        chk['all_leads_max_abs_dF1'] = float(max(abs(per[l]['F1'] - all_leads[tag][l - 1]) for l in LEADS))
    if blind and tag in blind.get('adfecgdb', {}):
        b = blind['adfecgdb'][tag]
        chk['blind_lead_max_abs_dF1'] = float(max(abs(per[l]['F1'] - b['per_lead'][str(l)]) for l in LEADS))
        chk['blind_lead_psd_lead_same'] = bool(int(b['psd_lead']) == psd_lead)
    out['crosscheck'] = chk
    del net
    return out


# ------------------------------------------------------------------ tong hop
def summ(vals):
    v = np.array([x for x in vals if x is not None], float)
    if not len(v):
        return dict(n=0)
    return dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0, n=int(len(v)),
                n_ge90=int((v >= 90).sum()), n_lt50=int((v < 50).sum()), min=float(v.min()), max=float(v.max()),
                median=float(np.median(v)))


def paired_wilcoxon(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b
    out = dict(n=int(len(d)), mean_diff=float(d.mean()) if len(d) else float('nan'),
               median_diff=float(np.median(d)) if len(d) else float('nan'),
               n_pos=int((d > 0).sum()), n_neg=int((d < 0).sum()), n_zero=int((d == 0).sum()))
    if len(d) < 2 or np.all(d == 0):
        out.update(stat=float('nan'), p=float('nan'), note='n<2 hoac moi hieu = 0')
        return out
    try:
        w = wilcoxon(a, b)
        out.update(stat=float(w.statistic), p=float(w.pvalue))
    except Exception as ex:
        out.update(stat=float('nan'), p=float('nan'), note=str(ex))
    return out


def compare_groups(subjects):
    """subjects: tag -> dict(model_22=..., model_5=... | None). -> tong hop theo nhom + Wilcoxon."""
    res = {}
    for g in GROUPS + ('ALL',):
        tags = [t for t in subjects if (g == 'ALL' or subjects[t]['group'] == g)]
        if not tags:
            continue
        r = dict(n_subjects=len(tags), subjects=tags)
        for name in ('model_22', 'model_5'):
            rows = [dict(subjects[t][name], record=t) for t in tags if subjects[t].get(name)]
            if not rows:
                continue
            leadF1 = [e['per_lead'][f'A{l}']['F1'] for e in rows for l in LEADS]
            r[name] = dict(n=len(rows), F1_psd=summ([e['F1_psd'] for e in rows]), F1_mean4=summ([e['F1_mean4'] for e in rows]),
                           F1_oracle=summ([e['F1_oracle'] for e in rows]), F1_per_lead=summ(leadF1),
                           Se_psd=summ([e['Se_psd'] for e in rows]), PPV_psd=summ([e['PPV_psd'] for e in rows]),
                           jitter_psd_mean=float(np.nanmean([e['jitter_psd'] for e in rows])),
                           bias_psd_median=float(np.nanmedian([e['bias_psd'] for e in rows])),
                           bias_psd_mean_abs=float(np.nanmean([abs(e['bias_psd']) for e in rows])),
                           bias_lead_median=float(np.nanmedian([e['per_lead'][f'A{l}']['bias_ms'] for e in rows for l in LEADS])),
                           bias_lead_values={t: [subjects[t][name]['per_lead'][f'A{l}']['bias_ms'] for l in LEADS]
                                             for t in tags if subjects[t].get(name)},
                           subjects_ge90=[e['record'] for e in rows if e['F1_psd'] >= 90],
                           subjects_lt50=[e['record'] for e in rows if e['F1_psd'] < 50])
            if all('F1_psd_verified_only' in e for e in rows):
                r[name]['F1_psd_verified_only'] = summ([e['F1_psd_verified_only'] for e in rows])
                r[name]['F1_mean4_verified_only'] = summ([e['F1_mean4_verified_only'] for e in rows])
        both = [t for t in tags if subjects[t].get('model_22') and subjects[t].get('model_5')]
        if both:
            a = [subjects[t]['model_22']['per_lead'][f'A{l}']['F1'] for t in both for l in LEADS]
            b = [subjects[t]['model_5']['per_lead'][f'A{l}']['F1'] for t in both for l in LEADS]
            r['wilcoxon_subject_x_lead'] = paired_wilcoxon(a, b)
            r['wilcoxon_psd'] = paired_wilcoxon([subjects[t]['model_22']['F1_psd'] for t in both],
                                                [subjects[t]['model_5']['F1_psd'] for t in both])
            r['wilcoxon_mean4'] = paired_wilcoxon([subjects[t]['model_22']['F1_mean4'] for t in both],
                                                  [subjects[t]['model_5']['F1_mean4'] for t in both])
            r['wilcoxon_bias_lead'] = paired_wilcoxon(
                [np.nan_to_num(subjects[t]['model_22']['per_lead'][f'A{l}']['bias_ms']) for t in both for l in LEADS],
                [np.nan_to_num(subjects[t]['model_5']['per_lead'][f'A{l}']['bias_ms']) for t in both for l in LEADS])
            r['n_paired_subjects'] = len(both)
        res[g] = r
    return res


# ------------------------------------------------------------------ CinC 2013 zero-shot
def run_cinc(net, thr, blind):
    D = cinc2013_dir()
    if D is None:
        return dict(note='chua co du lieu CinC 2013 (cinc2013_dir() = None)')
    recs = sorted({f[:-4] for f in os.listdir(D) if f.endswith('.dat')})[:10]
    rows = {}
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
            p = M.probability_series(net, M.robust_scale(rr).astype(np.float32), M.robust_scale(x).astype(np.float32), CFG)
            det = M.pick_peaks(p, thr, CFG).astype(np.int64) * 4
            per[lead] = score(det, gt)
        bl = pick_blind(res); f1s = [per[l]['F1'] for l in sorted(per)]
        rows[rec] = dict(record=rec, psd_lead=int(bl), per_lead={str(l): per[l] for l in per},
                         F1_psd=per[bl]['F1'], F1_lead0=per[0]['F1'], F1_oracle=float(max(f1s)), F1_mean4=float(np.mean(f1s)),
                         bias_lead0=per[0]['bias_ms'], bias_psd=per[bl]['bias_ms'], n_ref=int(len(gt)))
        ref = blind.get('cinc', {}).get(rec) if blind else None
        if ref:
            rows[rec]['model_5'] = dict(psd_lead=int(ref['psd_lead']), per_lead=ref['per_lead'], F1_psd=ref['F1_psd'],
                                        F1_lead0=ref['F1_lead0'], F1_oracle=ref['F1_oracle'], F1_mean4=ref['F1_mean'])
    out = dict(n=len(rows), records=rows, threshold=thr, dir=D)
    for k in ('F1_lead0', 'F1_psd', 'F1_mean4', 'F1_oracle'):
        out[f'production_22_{k}'] = summ([e[k] for e in rows.values()])
    ref_rows = [e['model_5'] for e in rows.values() if 'model_5' in e]
    if ref_rows:
        for k in ('F1_lead0', 'F1_psd', 'F1_mean4', 'F1_oracle'):
            out[f'production_5_{k}'] = summ([e[k] for e in ref_rows])
        both = [e for e in rows.values() if 'model_5' in e]
        out['wilcoxon_lead0'] = paired_wilcoxon([e['F1_lead0'] for e in both], [e['model_5']['F1_lead0'] for e in both])
        out['wilcoxon_psd'] = paired_wilcoxon([e['F1_psd'] for e in both], [e['model_5']['F1_psd'] for e in both])
        out['wilcoxon_mean4'] = paired_wilcoxon([e['F1_mean4'] for e in both], [e['model_5']['F1_mean4'] for e in both])
        out['wilcoxon_record_x_lead'] = paired_wilcoxon(
            [e['per_lead'][l]['F1'] for e in both for l in sorted(e['per_lead'])],
            [e['model_5']['per_lead'][l] for e in both for l in sorted(e['per_lead'])])
    out['production_5_stated'] = CINC_REF_STATED
    return out


# ------------------------------------------------------------------ cache
def _sig(path):
    st = os.stat(path); return dict(mtime=st.st_mtime, size=st.st_size)


def cache_load(use):
    if use and os.path.isfile(OUT_CACHE):
        try:
            return json.load(open(OUT_CACHE, encoding='utf-8'))
        except Exception:
            return {}
    return {}


# ------------------------------------------------------------------ in bang
def fmt_row(tag, g, fold, e5, e22):
    def part(e):
        if not e:
            return f'{"--":>7}{"--":>7}' + ''.join(f'{"--":>7}' for _ in LEADS) + f'{"--":>8}'
        return (f'{e["F1_psd"]:>7.2f}{e["F1_mean4"]:>7.2f}' + ''.join(f'{e["per_lead"][f"A{l}"]["F1"]:>7.2f}' for l in LEADS) +
                f'{e["bias_psd"]:>+8.1f}')
    d1 = e22['F1_psd'] - e5['F1_psd'] if (e5 and e22) else float('nan')
    d2 = e22['F1_mean4'] - e5['F1_mean4'] if (e5 and e22) else float('nan')
    return (f'{tag:<8}{g:<10}{fold:>4}{"A" + str(e22["psd_lead"]):>4} |' + part(e22) + ' |' + part(e5) +
            f' |{d1:>+8.2f}{d2:>+8.2f}')


HDR = (f'{"chu the":<8}{"nhom":<10}{"fold":>4}{"PSD":>4} |{"F1 PSD":>7}{"TB4":>7}{"A1":>7}{"A2":>7}{"A3":>7}{"A4":>7}{"lech":>8} |'
       f'{"F1 PSD":>7}{"TB4":>7}{"A1":>7}{"A2":>7}{"A3":>7}{"A4":>7}{"lech":>8} |{"dPSD":>8}{"dTB4":>8}')


def print_group_table(comp):
    print(f'\n{"nhom":<10}{"mo hinh":<9}{"n":>3}{"F1 PSD":>17}{"F1 TB4":>17}{"F1 kenh":>17}{">=90":>5}{"<50":>4}'
          f'{"Se PSD":>8}{"PPV PSD":>8}{"jit":>6}{"lech PSD":>9}{"lech kenh":>10}')
    for g in GROUPS + ('ALL',):
        if g not in comp:
            continue
        for name in ('model_5', 'model_22'):
            r = comp[g].get(name)
            if not r:
                continue
            a, b, c = r['F1_psd'], r['F1_mean4'], r['F1_per_lead']
            print(f'{g:<10}{name:<9}{r["n"]:>3}{a["mean"]:>9.2f} +/-{a["sd"]:>5.2f}{b["mean"]:>9.2f} +/-{b["sd"]:>5.2f}'
                  f'{c["mean"]:>9.2f} +/-{c["sd"]:>5.2f}{a["n_ge90"]:>5}{a["n_lt50"]:>4}{r["Se_psd"]["mean"]:>8.2f}'
                  f'{r["PPV_psd"]["mean"]:>8.2f}{r["jitter_psd_mean"]:>6.1f}{r["bias_psd_median"]:>+9.1f}{r["bias_lead_median"]:>+10.1f}')
        w = comp[g].get('wilcoxon_subject_x_lead')
        if w:
            wp = comp[g]['wilcoxon_psd']; wm = comp[g]['wilcoxon_mean4']; wb = comp[g]['wilcoxon_bias_lead']
            print(f'{"":<10}Wilcoxon 22 vs 5: (chu the x kenh) n={w["n"]} dF1 TB {w["mean_diff"]:+.2f} trung vi {w["median_diff"]:+.2f} '
                  f'(+{w["n_pos"]}/-{w["n_neg"]}/={w["n_zero"]}) p={w["p"]:.4f} | PSD n={wp["n"]} dF1 {wp["mean_diff"]:+.2f} p={wp["p"]:.4f} '
                  f'| TB4 n={wm["n"]} dF1 {wm["mean_diff"]:+.2f} p={wm["p"]:.4f} | lech kenh d={wb["mean_diff"]:+.1f} ms p={wb["p"]:.4f}')


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--partial', action='store_true', help='chap nhan bat ky so fold nao da co (mac dinh cung vay, nhung ghi ro)')
    ap.add_argument('--wait-min', type=float, default=0.0, help='neu chua co fold nao: doi toi da N phut, kiem tra moi --poll-s')
    ap.add_argument('--poll-s', type=float, default=120.0)
    ap.add_argument('--no-cache', action='store_true')
    ap.add_argument('--skip-cinc', action='store_true')
    ap.add_argument('--folds', default='', help='vd 1,2 ; rong = moi fold co san')
    a = ap.parse_args()
    t_all = time.time()
    sys.stdout = Tee(OUT_LOG)
    print(f'eval_22.py  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}  torch {torch.__version__}  threads {torch.get_num_threads()}  '
          f'{platform.platform()}  partial={a.partial}')

    # --- tham chieu mo hinh n=5
    sil = json.load(open(SILESIA_JSON, encoding='utf-8')) if os.path.isfile(SILESIA_JSON) else None
    all_leads = json.load(open(ALL_LEADS_JSON, encoding='utf-8')) if os.path.isfile(ALL_LEADS_JSON) else None
    blind = json.load(open(BLIND_JSON, encoding='utf-8')) if os.path.isfile(BLIND_JSON) else None
    print(f'tham chieu n=5: silesia_eval.json {"co" if sil else "KHONG"} | all_leads.json {"co" if all_leads else "KHONG"} | '
          f'blind_lead.json {"co" if blind else "KHONG"}')
    if sil:
        assert set(sil['duplicates_b2_to_physionet']) == set(B2_DUPLICATES), 'danh sach B2 trung khong khop silesia_eval.json'
        for t in B1 + B2:
            assert sil['records'][t]['checkpoint'] == 'production', f'{t}: silesia_eval.json dung checkpoint {sil["records"][t]["checkpoint"]}'

    # --- doi checkpoint
    def found():
        fs = sorted(glob.glob(os.path.join(CKPT_DIR, 'fetalqrs_tcn_22_fold_*.pt')))
        return [f for f in fs if re.search(r'fold_(\d{2})\.pt$', f)]
    t_wait = time.time()
    while not found() and (time.time() - t_wait) < a.wait_min * 60:
        print(f'   {datetime.datetime.now():%H:%M:%S} chua co fold checkpoint nao trong {CKPT_DIR}; doi {a.poll_s:.0f} s '
              f'(con {a.wait_min - (time.time() - t_wait) / 60:.1f} phut)', flush=True)
        time.sleep(a.poll_s)
    files = found()
    sel = [int(x) for x in a.folds.split(',') if x] if a.folds else None
    if sel:
        files = [f for f in files if int(re.search(r'fold_(\d{2})\.pt$', f).group(1)) in sel]
    prod_path = os.path.join(CKPT_DIR, 'fetalqrs_tcn_22_production.pt')
    have_prod = os.path.isfile(prod_path)
    print(f'checkpoint fold co san: {len(files)}/{N_FOLDS} -> {[os.path.basename(f) for f in files]}; production_22: '
          f'{"co" if have_prod else "chua co"}')

    cache = cache_load(not a.no_cache)
    out = dict(meta=dict(date=str(datetime.datetime.now()), torch=torch.__version__, threads=torch.get_num_threads(),
                         tolerance_ms=TOL_MS, partial=a.partial, n_folds_total=N_FOLDS,
                         cfg={k: (list(v) if isinstance(v, tuple) else v) for k, v in CFG.items()},
                         subjects=dict(PhysioNet=PHYSIONET, B1=B1, B2=B2), excluded_duplicates=B2_DUPLICATES,
                         model5_reference=dict(B1_B2='silesia_eval.json (production_5)',
                                               PhysioNet='fold_rXX.pt tinh lai (LORO n=5), doi chieu all_leads.json/blind_lead.json'),
                         label_note='B1: nhan gian tiep (fqrs_all ke ca co=0 nhu silesia_eval; them bien the verified_only); '
                                    'B2/PhysioNet: nhan da dau'),
               folds={}, subjects={})
    print('\n' + '=' * len(HDR)); print('TUNG CHU THE GIU LAI: model_22 (fold) | model_5 (production_5 / fold_rXX) | hieu (22 - 5)')
    print('  F1 theo kenh PSD mu nhan, trung binh 4 kenh, tung kenh A1..A4; lech = trung vi (phat hien - nhan) ms tren kenh PSD')
    print('=' * len(HDR)); print(HDR)
    n_done = 0
    for path in files:
        k = int(re.search(r'fold_(\d{2})\.pt$', path).group(1)); key = f'{k:02d}'
        sig = _sig(path)
        if key in cache and cache[key].get('sig') == sig and not a.no_cache:
            info = cache[key]['fold']; rows = cache[key]['subjects']
            for tag, e in rows.items():
                out['subjects'][tag] = e
                print(fmt_row(tag, e['group'], key, e.get('model_5'), e['model_22']) + '  [cache]')
            out['folds'][key] = info; n_done += 1
            continue
        try:
            net, thr, b = load_net(path)
        except Exception as ex:      # co the dang ghi do
            time.sleep(5)
            try:
                net, thr, b = load_net(path)
            except Exception as ex2:
                print(f'   fold {key}: khong nap duoc checkpoint ({ex2}) -> bo qua'); continue
        info = dict(path=os.path.basename(path), threshold=thr, test_subjects=list(b['test_subjects']),
                    val_subject=b['val_subject'], n_train=len(b['train_subjects']), val_F1=float(b.get('val_F1', float('nan'))),
                    epochs=b.get('epochs'), augment=b.get('augment'), seed=b.get('seed'), loss=b.get('loss'),
                    train_22_metrics=b.get('metrics'))
        assert not (set(b['test_subjects']) & set(b['train_subjects'])), f'fold {key}: test trung train'
        assert b['val_subject'] not in b['test_subjects'], f'fold {key}: val trung test'
        rows = {}
        for tag in b['test_subjects']:
            t0 = time.time(); g = group_of(tag)
            prep, fq1000, flags, meta = load_subject(tag)
            psd_lead = max(LEADS, key=lambda l: prep[l]['psd'])
            per = run_net(net, thr, prep, fq1000, flags)
            e22 = summarize_leads(per, psd_lead, thr); e22['checkpoint'] = os.path.basename(path)
            if g == 'PhysioNet':
                e5 = ref5_physionet(tag, prep, fq1000, psd_lead, all_leads, blind)
            else:
                e5 = ref5_silesia(tag, sil)
            e = dict(record=tag, group=g, fold=k, val_subject=b['val_subject'], psd_lead=psd_lead,
                     psd_scores={f'A{l}': prep[l]['psd'] for l in LEADS}, n_ref=int(len(fq1000)), meta=meta,
                     model_22=e22, model_5=e5, seconds=time.time() - t0)
            # doi chieu voi so train_22 tu tinh (cung pipeline -> phai khop)
            tm = (b.get('metrics') or {}).get(tag)
            if tm:
                e['crosscheck_train_22'] = dict(dF1_psd=float(e22['F1_psd'] - tm['F1_psd']), dF1_mean4=float(e22['F1_mean4'] - tm['F1_mean4']),
                                                psd_lead_same=bool(int(tm['psd_lead']) == psd_lead))
            if e5 and e5.get('psd_lead') != psd_lead:
                e['warn'] = f'kenh PSD khac mo hinh n=5 (A{e5.get("psd_lead")})'
            rows[tag] = e; out['subjects'][tag] = e
            line = fmt_row(tag, g, key, e5, e22)
            if tm:
                line += f'  [train_22: dPSD {e["crosscheck_train_22"]["dF1_psd"]:+.2f} dTB4 {e["crosscheck_train_22"]["dF1_mean4"]:+.2f}]'
            if e5 and e5.get('crosscheck'):
                line += f'  [n=5 doi chieu: {e5["crosscheck"]}]'
            if 'warn' in e:
                line += '  ! ' + e['warn']
            print(line, flush=True)
            del prep, per; gc.collect()
        out['folds'][key] = info; n_done += 1
        cache[key] = dict(sig=sig, fold=info, subjects=rows)
        json.dump(cache, open(OUT_CACHE, 'w', encoding='utf-8'), indent=0, default=float)
        del net; gc.collect()
    print('-' * len(HDR))
    print(f'da danh gia {n_done}/{N_FOLDS} fold, {len(out["subjects"])}/22 chu the giu lai '
          f'(PhysioNet {sum(1 for e in out["subjects"].values() if e["group"] == "PhysioNet")}/5, '
          f'B2 {sum(1 for e in out["subjects"].values() if e["group"] == "B2")}/7, '
          f'B1 {sum(1 for e in out["subjects"].values() if e["group"] == "B1")}/10)')

    # --- tong hop theo nhom
    comp = compare_groups(out['subjects']) if out['subjects'] else {}
    out['comparison'] = comp
    if comp:
        print('\n' + '=' * 120)
        print(f'TONG HOP THEO NHOM ({n_done}/{N_FOLDS} fold; macro F1 +/- SD giua chu the; >=90 / <50 dem tren kenh PSD; '
              f'lech = trung vi (phat hien - nhan) ms)')
        print('=' * 120)
        print_group_table(comp)
        if 'B1' in comp and comp['B1'].get('model_22', {}).get('F1_psd_verified_only'):
            for name in ('model_5', 'model_22'):
                r = comp['B1'].get(name, {})
                if r.get('F1_psd_verified_only'):
                    print(f'   B1 bo qua nhip co=0 ({name}): F1 PSD {r["F1_psd_verified_only"]["mean"]:.2f} +/- {r["F1_psd_verified_only"]["sd"]:.2f} '
                          f'| TB4 {r["F1_mean4_verified_only"]["mean"]:.2f} +/- {r["F1_mean4_verified_only"]["sd"]:.2f}')
        print('\nLECH NHAN theo chu the (trung vi (phat hien - nhan) ms tren 4 kenh; am = nhan SAU dinh phat hien):')
        for g in GROUPS:
            if g not in comp:
                continue
            for name in ('model_5', 'model_22'):
                r = comp[g].get(name)
                if r:
                    print(f'   {g:<10}{name:<9}' + '  '.join(f'{t}:' + '/'.join(f'{v:+.0f}' for v in vs) for t, vs in r['bias_lead_values'].items()))

    # --- production_22 -> CinC 2013
    if have_prod and not a.skip_cinc:
        net, thr, b = load_net(prod_path)
        print('\n' + '=' * 120)
        print(f'CinC 2013 set-a ZERO-SHOT: production_22 (nguong {thr:.2f}, train tren {len(b.get("trained_on", []))} chu the) '
              f'vs production_5 (blind_lead.json)')
        print('=' * 120)
        c = run_cinc(net, thr, blind); out['cinc2013'] = c
        if 'records' in c:
            print(f'{"rec":<5}{"PSD":>4}{"F1 kenh0":>10}{"F1 PSD":>8}{"TB4":>8}{"oracle":>8}{"lech0":>7} | {"n=5 kenh0":>10}{"PSD":>8}{"TB4":>8}{"oracle":>8}')
            for rec, e in c['records'].items():
                m5 = e.get('model_5')
                s5 = (f'{m5["F1_lead0"]:>10.2f}{m5["F1_psd"]:>8.2f}{m5["F1_mean4"]:>8.2f}{m5["F1_oracle"]:>8.2f}' if m5 else f'{"--":>34}')
                print(f'{rec:<5}{e["psd_lead"]:>4}{e["F1_lead0"]:>10.2f}{e["F1_psd"]:>8.2f}{e["F1_mean4"]:>8.2f}{e["F1_oracle"]:>8.2f}'
                      f'{e["bias_lead0"]:>+7.1f} | ' + s5)
            p22 = {k: c[f'production_22_{k}'] for k in ('F1_lead0', 'F1_psd', 'F1_mean4', 'F1_oracle')}
            print(f'production_22 (n={c["n"]}): kenh 0 {p22["F1_lead0"]["mean"]:.2f} +/- {p22["F1_lead0"]["sd"]:.2f} | '
                  f'PSD {p22["F1_psd"]["mean"]:.2f} +/- {p22["F1_psd"]["sd"]:.2f} | TB4 {p22["F1_mean4"]["mean"]:.2f} +/- {p22["F1_mean4"]["sd"]:.2f} | '
                  f'oracle {p22["F1_oracle"]["mean"]:.2f} | kenh0 >=90: {p22["F1_lead0"]["n_ge90"]} <50: {p22["F1_lead0"]["n_lt50"]} | '
                  f'PSD >=90: {p22["F1_psd"]["n_ge90"]} <50: {p22["F1_psd"]["n_lt50"]}')
            if 'production_5_F1_lead0' in c:
                p5 = {k: c[f'production_5_{k}'] for k in ('F1_lead0', 'F1_psd', 'F1_mean4', 'F1_oracle')}
                print(f'production_5  (blind_lead.json): kenh 0 {p5["F1_lead0"]["mean"]:.2f} +/- {p5["F1_lead0"]["sd"]:.2f} | '
                      f'PSD {p5["F1_psd"]["mean"]:.2f} +/- {p5["F1_psd"]["sd"]:.2f} | TB4 {p5["F1_mean4"]["mean"]:.2f} +/- {p5["F1_mean4"]["sd"]:.2f} | '
                      f'oracle {p5["F1_oracle"]["mean"]:.2f} | kenh0 >=90: {p5["F1_lead0"]["n_ge90"]} <50: {p5["F1_lead0"]["n_lt50"]} | '
                      f'PSD >=90: {p5["F1_psd"]["n_ge90"]} <50: {p5["F1_psd"]["n_lt50"]}   '
                      f'[so da cong bo: {CINC_REF_STATED}]')
                for k in ('lead0', 'psd', 'mean4', 'record_x_lead'):
                    w = c[f'wilcoxon_{k}']
                    print(f'   Wilcoxon {k:<14} n={w["n"]:>2} dF1 TB {w["mean_diff"]:+.2f} trung vi {w["median_diff"]:+.2f} '
                          f'(+{w["n_pos"]}/-{w["n_neg"]}/={w["n_zero"]}) p={w["p"]:.4f}')
        else:
            print('   ' + c.get('note', ''))
        del net
    else:
        out['cinc2013'] = dict(note='chua co production' if not have_prod else 'bo qua (--skip-cinc)')
        print(f'\nCinC 2013 zero-shot: {out["cinc2013"]["note"]}')

    # --- ghi
    out['meta']['minutes'] = (time.time() - t_all) / 60
    out['meta']['n_folds_evaluated'] = n_done
    json.dump(out, open(OUT_JSON, 'w', encoding='utf-8'), indent=1, default=float)
    missing = [f'{k:02d}' for k in range(1, N_FOLDS + 1) if f'{k:02d}' not in out['folds']]
    st = [f'thoi diem: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}',
          f'fold da danh gia: {n_done}/{N_FOLDS} -> {sorted(out["folds"])}',
          f'fold chua co: {missing}',
          f'chu the da danh gia ({len(out["subjects"])}/22): {sorted(out["subjects"])}',
          f'production_22: {"co -> CinC 2013 " + ("da chay" if "records" in out.get("cinc2013", {}) else "khong chay") if have_prod else "chua co"}',
          f'trang thai: {"HOAN TAT" if n_done == N_FOLDS and have_prod else "PARTIAL"}',
          f'ket qua: {OUT_JSON} | {OUT_LOG} | thoi gian {out["meta"]["minutes"]:.1f} phut']
    open(OUT_STATUS, 'w', encoding='utf-8').write('\n'.join(st) + '\n')
    print('\n' + '\n'.join(st))


if __name__ == '__main__':
    main()
