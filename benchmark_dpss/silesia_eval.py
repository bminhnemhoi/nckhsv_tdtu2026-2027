# -*- coding: utf-8 -*-
"""
Danh gia FetalQRS-TCN tren bo Silesia (Matonia va cs. 2020): 10 ban ghi THAI KY (B1) + 12 ban ghi CHUYEN DA (B2).

Giao thuc (giong ADFECGDB va CinC 2013 trong blind_lead.py):
  - tung ban ghi, tung dao trinh bung A1..A4: preprocess 10-60 Hz @250 Hz -> khu me -> TCN -> dinh -> +/-50 ms
  - kenh PSD = dao trinh chon MU NHAN theo Power-MF (pick_blind), va trung binh 4 kenh
  - checkpoint production (train tren ca 5 ban ghi PhysioNet); rieng ban ghi B2 TRUNG voi PhysioNet (phat hien bang
    tuong quan cheo tin hieu) dung checkpoint fold_rXX chua tung thay rXX -> con so trung thuc.
  - B1: nhan gian tiep (khong dien cuc da dau); bao cao them bien the "bo qua nhip co = 0" (khong tinh TP/FN/FP quanh
    nhip ma chuyen gia khong xac nhan duoc).

Ket qua: silesia_eval.json, silesia_log.txt (cung thu muc).
Chay:   python benchmark_dpss/silesia_eval.py            (toan bo, ~5-10 phut CPU)
        python benchmark_dpss/silesia_eval.py --quick    (chi leak_check + format_check)
"""
import os, sys, json, time, datetime, importlib.util, platform
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, torch, mne, wfdb
from scipy import signal as sg

torch.set_num_threads(4)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _paths import adfecgdb_dir, checkpoint
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG = M.CFG
spec2 = importlib.util.spec_from_file_location('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))
L = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(L)

OUT_JSON = os.path.join(HERE, 'silesia_eval.json')
OUT_LOG = os.path.join(HERE, 'silesia_log.txt')
PHYSIONET = ['r01', 'r04', 'r07', 'r08', 'r10']
TOL_MS = 50
NCC_DUP = 0.90            # nguong ket luan trung
FHR_BAND = (1.8, 3.0)     # Power-MF, 108-180 bpm


class Tee:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.o = sys.stdout
    def write(self, s):
        self.o.write(s); self.f.write(s); self.f.flush()
    def flush(self):
        self.o.flush(); self.f.flush()


# ------------------------------------------------------------------ chon kenh mu nhan (copy tu blind_lead.py)
def psd_score(x250, fs=250):
    e = np.abs(sg.hilbert(x250 - np.mean(x250)))
    e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def pick_blind(residuals):
    return max(residuals, key=lambda l: psd_score(residuals[l]))


# ------------------------------------------------------------------ cham diem
def match_flagged(det, ref, flags, fs, tol_ms):
    """nhu M.match_events nhung nhip co flag=0 la 'khong quan tam': khong tinh TP/FN, va phat hien khop voi no
    khong bi tinh FP."""
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


def signed_bias(det, ref, tol_ms=TOL_MS):
    """trung vi cua (phat hien - nhan) tren cac cap trong +/-tol: am = nhan nam SAU dinh R phat hien.
    Dung de phat hien lech he thong cua nhan gian tiep B1 (khong anh huong F1 vi < 50 ms)."""
    det = np.sort(np.asarray(det, float)); ref = np.sort(np.asarray(ref, float))
    if not len(det) or not len(ref):
        return float('nan')
    j = np.clip(np.searchsorted(ref, det), 1, len(ref) - 1)
    cand = np.stack([det - ref[j - 1], det - ref[j]])
    s = cand[np.abs(cand).argmin(0), np.arange(len(det))]
    s = s[np.abs(s) <= tol_ms]
    return float(np.median(s)) if len(s) else float('nan')


def load_net(name):
    b = torch.load(checkpoint(name), map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
    return net, float(b['threshold'])


def run_lead(net, thr, sig1000):
    x = M.preprocess(sig1000, 1000, CFG); r, _ = M.cancel_maternal(x, CFG)
    p = M.probability_series(net, M.robust_scale(r).astype(np.float32), M.robust_scale(x).astype(np.float32), CFG)
    det = M.pick_peaks(p, thr, CFG).astype(np.int64) * 4
    return r, det


def eval_record(group, idx, net, thr):
    sig, _, meta = L.load_record(group, idx)
    ref = meta['fqrs_all']; flags = meta['fqrs_flags']
    res, per = {}, {}
    t0 = time.time()
    for lead in range(4):
        r, det = run_lead(net, thr, sig[lead])
        res[lead] = r
        m = M.match_events(det, ref, 1000, TOL_MS)
        m['n_det'] = int(len(det)); m['n_ref'] = int(len(ref)); m['bias_ms'] = signed_bias(det, ref)
        if group == 'B1':
            m['verified_only'] = match_flagged(det, ref, flags, 1000, TOL_MS)
        per[lead] = m
    bl = pick_blind(res)
    f1s = [per[l]['F1'] for l in range(4)]
    out = dict(record=meta['record'], group=group, duration_s=meta['duration_s'], n_ref=int(len(ref)),
               n_ref_flag0=int(meta['n_fqrs_flag0']), fhr_median_bpm=meta['fhr_median_bpm'],
               psd_lead=int(bl), per_lead={f'A{l + 1}': per[l] for l in range(4)},
               F1_psd=per[bl]['F1'], Se_psd=per[bl]['Se'], PPV_psd=per[bl]['PPV'], jitter_psd=per[bl]['jitter_ms'],
               bias_psd=per[bl]['bias_ms'],
               F1_mean4=float(np.mean(f1s)), F1_oracle=float(max(f1s)), oracle_lead=int(np.argmax(f1s)),
               seconds=time.time() - t0)
    if group == 'B1':
        v = [per[l]['verified_only']['F1'] for l in range(4)]
        out['F1_psd_verified_only'] = per[bl]['verified_only']['F1']
        out['F1_mean4_verified_only'] = float(np.mean(v))
    return out


# ------------------------------------------------------------------ kiem tra ro ri
def leak_check(win_s=(30.0, 90.0)):
    """Voi tung cap (rXX PhysioNet, B2_YY): dua ca hai ve 250 Hz (preprocess 10-60 Hz), lay cua so 60 s cua rXX lam
    mau, truot tren TOAN BO B2_YY (5 phut => moi do lech +/-5 phut), thu ca 4x4 to hop dao trinh bung. Them: FECG
    truc tiep (rXX kenh 0 vs B2_dFECG cot 0) va do lech nhan QRS thai."""
    D = adfecgdb_dir(); fs = CFG['fs']
    a0, a1 = int(win_s[0] * fs), int(win_s[1] * fs)
    B2 = {}
    for i in range(1, L.N_B2 + 1):
        sig, _, meta = L.load_record('B2', i)
        B2[i] = dict(abd=[M.preprocess(sig[k], 1000, CFG) for k in range(4)],
                     direct=M.preprocess(L.load_direct_fecg(i)[0], 1000, CFG), fq=meta['fqrs_all'])
    table, best = {}, {}
    for r in PHYSIONET:
        raw = mne.io.read_raw_edf(os.path.join(D, r + '.edf'), preload=True, verbose=False)
        s = raw.get_data() * 1e6
        A = [M.preprocess(s[k], 1000, CFG) for k in (1, 2, 3, 4)]
        Ad = M.preprocess(s[0], 1000, CFG)
        ann = np.asarray(wfdb.rdann(os.path.join(D, r), 'edf.qrs').sample)
        table[r] = {}
        for i, X in B2.items():
            mat = np.zeros((4, 4)); lag = np.zeros((4, 4), int)
            for k in range(4):
                for j in range(4):
                    c = L.sliding_ncc(A[k][a0:a1], X['abd'][j])
                    q = int(np.argmax(np.abs(c))); mat[k, j] = abs(c[q]); lag[k, j] = q - a0
            cd = L.sliding_ncc(Ad[a0:a1], X['direct']); qd = int(np.argmax(np.abs(cd)))
            kk, jj = np.unravel_index(int(np.argmax(mat)), mat.shape)
            diag = float(np.mean([mat[k, k] for k in range(4)]))
            table[r][f'B2_{i:02d}'] = dict(
                ncc_max=float(mat.max()), best_pair=f'A{kk + 1}->A{jj + 1}', lag_ms=float(lag[kk, jj] / fs * 1000),
                ncc_diag_mean=diag, ncc_matrix=np.round(mat, 3).tolist(),
                ncc_direct=float(abs(cd[qd])), lag_direct_ms=float((qd - a0) / fs * 1000))
        j = max(table[r], key=lambda x: table[r][x]['ncc_max'])
        e = table[r][j]
        # do lech nhan: dich nhan rXX theo lag tin hieu, dem ti le khop trong +/-10 ms
        # lag < 0 nghia la B2 bat dau SOM hon rXX |lag| ms => nhan rXX + lag = toa do B2 (1 mau = 1 ms @1000 Hz)
        fq = B2[int(j[-2:])]['fq']; shift = ann + e['lag_ms']
        dd = shift[:, None] - fq[None, :]; k = np.abs(dd).argmin(1); dsig = dd[np.arange(len(shift)), k]
        second = sorted((v['ncc_max'], k) for k, v in table[r].items())[-2]
        best[r] = dict(b2=j, ncc_max=e['ncc_max'], best_pair=e['best_pair'], lag_ms=e['lag_ms'],
                       ncc_diag_mean=e['ncc_diag_mean'], ncc_direct=e['ncc_direct'], lag_direct_ms=e['lag_direct_ms'],
                       runner_up=dict(b2=second[1], ncc_max=second[0]),
                       n_ann_physionet=int(len(ann)), n_ann_b2=int(len(fq)),
                       ann_offset_raw_median_ms=float(np.median(ann[:5] - fq[:5])),
                       ann_residual_after_lag_median_ms=float(np.median(dsig)),
                       ann_match_10ms_after_lag=float(np.mean(np.abs(dsig) <= 10) * 100),
                       is_duplicate=bool(e['ncc_max'] >= NCC_DUP or e['ncc_direct'] >= NCC_DUP))
    return best, table


def print_leak(best):
    print('\n' + '=' * 100)
    print(f'KIEM TRA RO RI: 5 ban ghi PhysioNet ADFECGDB vs 12 ban ghi B2 (NCC cuc dai, cua so 60 s, moi do lech, 4x4 kenh)')
    print('=' * 100)
    print(f'{"rXX":<5}{"B2 trung":>9}{"NCC bung":>10}{"cap kenh":>10}{"lech ms":>9}{"NCC truc tiep":>15}'
          f'{"NCC hang nhi":>14}{"nhan khop 10ms":>16}{"n nhan":>10}  ket luan')
    for r, e in best.items():
        print(f'{r:<5}{e["b2"]:>9}{e["ncc_max"]:>10.3f}{e["best_pair"]:>10}{e["lag_ms"]:>9.0f}{e["ncc_direct"]:>15.3f}'
              f'{e["runner_up"]["ncc_max"]:>14.3f}{e["ann_match_10ms_after_lag"]:>15.1f}%'
              f'{e["n_ann_physionet"]:>5}/{e["n_ann_b2"]:<5} {"TRUNG -> dung fold_" + r if e["is_duplicate"] else "khong trung"}')


# ------------------------------------------------------------------ tong hop
def summarize(rows, key):
    v = np.array([r[key] for r in rows], float)
    return dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0, n=int(len(v)),
                n_ge90=int((v >= 90).sum()), n_lt50=int((v < 50).sum()), min=float(v.min()), max=float(v.max()))


def reference_numbers():
    """ADFECGDB va CinC 2013 tu cac file ket qua da co (blind_lead.json, crossdataset_pcdb.json) -- khong go tay."""
    ref = {}
    p = os.path.join(HERE, 'blind_lead.json')
    if os.path.isfile(p):
        d = json.load(open(p))
        for k, name in (('adfecgdb', 'ADFECGDB (5, LORO fold)'), ('cinc', 'CinC 2013 set-a (10, zero-shot)')):
            if d.get(k):
                rows = [dict(F1_psd=v['F1_psd'], F1_mean4=v['F1_mean']) for v in d[k].values()]
                ref[name] = dict(psd=summarize(rows, 'F1_psd'), mean4=summarize(rows, 'F1_mean4'), source='blind_lead.json')
    p = os.path.join(ROOT, 'model', 'crossdataset_pcdb.json')
    if os.path.isfile(p):
        d = json.load(open(p)); by = {}
        for r in d:
            by.setdefault(r['rec'], {})[r['lead']] = r['F1']
        rows = [dict(F1_lead0=v[0], F1_mean4=float(np.mean(list(v.values())))) for v in by.values()]
        ref['CinC 2013 set-a (10, zero-shot, kenh 0)'] = dict(lead0=summarize(rows, 'F1_lead0'),
                                                           mean4=summarize(rows, 'F1_mean4'),
                                                           source='model/crossdataset_pcdb.json')
    return ref


def main(quick=False):
    t_all = time.time()
    sys.stdout = Tee(OUT_LOG)
    print(f'silesia_eval.py  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}  torch {torch.__version__}  '
          f'threads {torch.get_num_threads()}  {platform.platform()}')
    print('du lieu:', L.silesia_dir())
    out = dict(meta=dict(date=str(datetime.datetime.now()), torch=torch.__version__, threads=torch.get_num_threads(),
                         tolerance_ms=TOL_MS, ncc_dup_threshold=NCC_DUP, cfg={k: (list(v) if isinstance(v, tuple) else v)
                                                                             for k, v in CFG.items()}))
    # --- dinh dang
    print('\n[format_check] doi chieu .ecg (int16 big-endian /10) voi .txt ...')
    fc = L.format_check(); out['format_check'] = fc
    bad = {k: v for k, v in fc.items() if v['max_abs_diff'] > 1e-6}
    print(f'  {len(fc)} file, sai khac toi da {max(v["max_abs_diff"] for v in fc.values()):.1e} '
          f'(sai so dau phay dong); {"KHOP 100 %" if not bad else "LECH: " + str(bad)}')
    # --- ro ri
    best, table = leak_check(); out['leak_check'] = dict(best=best, table=table)
    print_leak(best)
    dup = {e['b2']: r for r, e in best.items() if e['is_duplicate']}
    out['duplicates_b2_to_physionet'] = dup
    if quick:
        json.dump(out, open(OUT_JSON, 'w'), indent=1); return out
    # --- checkpoint
    nets = {'production': load_net('fetalqrs_tcn_production.pt')}
    for r in PHYSIONET:
        nets[f'fold_{r}'] = load_net(f'fetalqrs_tcn_fold_{r}.pt')
    out['meta']['thresholds'] = {k: v[1] for k, v in nets.items()}
    print('\nnguong checkpoint:', {k: round(v[1], 3) for k, v in nets.items()})
    # --- danh gia
    recs = {}
    for group, n in (('B1', L.N_B1), ('B2', L.N_B2)):
        print('\n' + '=' * 100)
        print(f'{group} -- {"THAI KY, nhan gian tiep (khong dien cuc da dau)" if group == "B1" else "CHUYEN DA, nhan tu FECG truc tiep"}')
        print('=' * 100)
        hdr = (f'{"ban ghi":<8}{"ckpt":>12}{"phut":>6}{"n nhan":>8}{"FHR":>6}{"PSD":>5}{"F1 PSD":>8}{"Se":>7}{"PPV":>7}'
               f'{"jit ms":>8}{"lech ms":>8}{"F1 A1":>7}{"F1 A2":>7}{"F1 A3":>7}{"F1 A4":>7}{"TB4":>7}{"oracle":>8}')
        if group == 'B1': hdr += f'{"F1PSD co=1":>12}{"TB4 co=1":>10}'
        print(hdr)
        for i in range(1, n + 1):
            tag = f'{group}_{i:02d}'
            ck = f'fold_{dup[tag]}' if tag in dup else 'production'
            net, thr = nets[ck]
            e = eval_record(group, i, net, thr); e['checkpoint'] = ck
            if tag in dup:      # con so ro ri, chi de doi chieu
                e2 = eval_record(group, i, *nets['production'])
                e['leaked_production'] = dict(F1_psd=e2['F1_psd'], F1_mean4=e2['F1_mean4'])
            recs[tag] = e
            pl = e['per_lead']
            line = (f'{tag:<8}{ck:>12}{e["duration_s"] / 60:>6.1f}{e["n_ref"]:>8}{e["fhr_median_bpm"]:>6.0f}'
                    f'{"A" + str(e["psd_lead"] + 1):>5}{e["F1_psd"]:>8.2f}{e["Se_psd"]:>7.2f}{e["PPV_psd"]:>7.2f}'
                    f'{e["jitter_psd"]:>8.2f}{e["bias_psd"]:>8.1f}' + ''.join(f'{pl[f"A{k}"]["F1"]:>7.2f}' for k in (1, 2, 3, 4)) +
                    f'{e["F1_mean4"]:>7.2f}{e["F1_oracle"]:>8.2f}')
            if group == 'B1': line += f'{e["F1_psd_verified_only"]:>12.2f}{e["F1_mean4_verified_only"]:>10.2f}'
            if 'leaked_production' in e:
                line += f'   [production ro ri: PSD {e["leaked_production"]["F1_psd"]:.2f} / TB4 {e["leaked_production"]["F1_mean4"]:.2f}]'
            print(line, flush=True)
    out['records'] = recs
    # --- tong hop
    summ = {}
    for group in ('B1', 'B2'):
        rows = [e for e in recs.values() if e['group'] == group]
        s = dict(psd=summarize(rows, 'F1_psd'), mean4=summarize(rows, 'F1_mean4'), oracle=summarize(rows, 'F1_oracle'),
                 Se_psd=summarize(rows, 'Se_psd'), PPV_psd=summarize(rows, 'PPV_psd'),
                 jitter_psd_mean=float(np.nanmean([e['jitter_psd'] for e in rows])),
                 bias_psd_ms={e['record']: e['bias_psd'] for e in rows},
                 bias_psd_mean_abs=float(np.nanmean([abs(e['bias_psd']) for e in rows])),
                 total_minutes=float(sum(e['duration_s'] for e in rows) / 60), n_records=len(rows),
                 records_ge90=[e['record'] for e in rows if e['F1_psd'] >= 90],
                 records_lt50=[e['record'] for e in rows if e['F1_psd'] < 50])
        if group == 'B1':
            s['psd_verified_only'] = summarize(rows, 'F1_psd_verified_only')
            s['mean4_verified_only'] = summarize(rows, 'F1_mean4_verified_only')
        if group == 'B2':
            nd = [e for e in rows if e['record'] not in dup]
            s['non_duplicate_only'] = dict(n=len(nd), psd=summarize(nd, 'F1_psd'), mean4=summarize(nd, 'F1_mean4'))
            dd = [e for e in rows if e['record'] in dup]
            if dd:
                s['duplicates_fold_ckpt'] = dict(n=len(dd), psd=summarize(dd, 'F1_psd'), mean4=summarize(dd, 'F1_mean4'))
                s['duplicates_production_leaked'] = dict(
                    psd=float(np.mean([e['leaked_production']['F1_psd'] for e in dd])),
                    mean4=float(np.mean([e['leaked_production']['F1_mean4'] for e in dd])))
        summ[group] = s
    # micro (gop tat ca nhip, kenh PSD)
    for group in ('B1', 'B2'):
        rows = [e for e in recs.values() if e['group'] == group]
        tp = sum(e['per_lead'][f'A{e["psd_lead"] + 1}']['TP'] for e in rows)
        fp = sum(e['per_lead'][f'A{e["psd_lead"] + 1}']['FP'] for e in rows)
        fn = sum(e['per_lead'][f'A{e["psd_lead"] + 1}']['FN'] for e in rows)
        summ[group]['micro_psd'] = dict(TP=tp, FP=fp, FN=fn, F1=200 * tp / (2 * tp + fp + fn) if tp else 0.0)
    out['summary'] = summ
    out['reference'] = reference_numbers()
    print('\n' + '=' * 100); print('TONG HOP (macro F1 +/- SD giua cac ban ghi; kenh PSD mu nhan | trung binh 4 kenh)')
    print('=' * 100)
    print(f'{"bo du lieu":<48}{"n":>3}{"phut":>7}{"F1 PSD":>16}{"F1 TB4":>16}{">=90":>6}{"<50":>5}')
    for name, r in out['reference'].items():
        a = r.get('psd') or r.get('lead0'); b = r['mean4']
        print(f'{name:<48}{a["n"]:>3}{"":>7}{a["mean"]:>8.2f} +/-{a["sd"]:>5.2f}{b["mean"]:>8.2f} +/-{b["sd"]:>5.2f}'
              f'{a["n_ge90"]:>6}{a["n_lt50"]:>5}   ({r["source"]})')
    for group, label in (('B2', 'Silesia B2 chuyen da (12, 5 trung -> fold ckpt)'), ('B1', 'Silesia B1 THAI KY (10, nhan gian tiep)')):
        s = summ[group]
        print(f'{label:<48}{s["n_records"]:>3}{s["total_minutes"]:>7.1f}{s["psd"]["mean"]:>8.2f} +/-{s["psd"]["sd"]:>5.2f}'
              f'{s["mean4"]["mean"]:>8.2f} +/-{s["mean4"]["sd"]:>5.2f}{s["psd"]["n_ge90"]:>6}{s["psd"]["n_lt50"]:>5}')
    s = summ['B2']['non_duplicate_only']
    print(f'{"  B2 chi 7 ban ghi KHONG trung (production)":<48}{s["n"]:>3}{"":>7}{s["psd"]["mean"]:>8.2f} +/-{s["psd"]["sd"]:>5.2f}'
          f'{s["mean4"]["mean"]:>8.2f} +/-{s["mean4"]["sd"]:>5.2f}{s["psd"]["n_ge90"]:>6}{s["psd"]["n_lt50"]:>5}')
    if 'duplicates_fold_ckpt' in summ['B2']:
        s = summ['B2']['duplicates_fold_ckpt']; s2 = summ['B2']['duplicates_production_leaked']
        print(f'{"  B2 5 ban ghi trung: fold ckpt (trung thuc)":<48}{s["n"]:>3}{"":>7}{s["psd"]["mean"]:>8.2f} +/-{s["psd"]["sd"]:>5.2f}'
              f'{s["mean4"]["mean"]:>8.2f} +/-{s["mean4"]["sd"]:>5.2f}')
        print(f'{"  B2 5 ban ghi trung: production (RO RI, chi doi chieu)":<48}{s["n"]:>3}{"":>7}{s2["psd"]:>8.2f}{"":>9}{s2["mean4"]:>8.2f}')
    s = summ['B1']
    print(f'{"  B1 bo qua nhip co=0 (khong quan tam)":<48}{s["n_records"]:>3}{"":>7}{s["psd_verified_only"]["mean"]:>8.2f} +/-{s["psd_verified_only"]["sd"]:>5.2f}'
          f'{s["mean4_verified_only"]["mean"]:>8.2f} +/-{s["mean4_verified_only"]["sd"]:>5.2f}')
    for group in ('B1', 'B2'):
        m = summ[group]['micro_psd']
        print(f'  {group} micro (gop nhip, kenh PSD): TP {m["TP"]} FP {m["FP"]} FN {m["FN"]}  F1 {m["F1"]:.2f}; '
              f'F1>=90: {summ[group]["records_ge90"]}; F1<50: {summ[group]["records_lt50"]}')
    out['meta']['minutes'] = (time.time() - t_all) / 60
    json.dump(out, open(OUT_JSON, 'w'), indent=1, default=float)
    print(f'\nda ghi {OUT_JSON} va {OUT_LOG}; tong {out["meta"]["minutes"]:.1f} phut')
    return out


if __name__ == '__main__':
    main(quick='--quick' in sys.argv)
