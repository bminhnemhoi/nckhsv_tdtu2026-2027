# -*- coding: utf-8 -*-
"""VIEC 1 -- kiem toan chat luong nhan + kiem CHONG LAN du lieu (M4).
Chay: python analysis/dulieu_audit.py --stage labels|overlap|all [--no-signal]
Ket qua: analysis/dulieu_audit.json
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, argparse, importlib.util
import numpy as np
from scipy import signal as sg

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
from _paths import adfecgdb_dir, cinc2013_dir


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


L = _load('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))
import wfdb, mne

PHYSIONET = ['r01', 'r04', 'r07', 'r08', 'r10']
B1 = ['B1_%02d' % i for i in range(1, 11)]
B2_ALL = ['B2_%02d' % i for i in range(1, 13)]
B2_TRAIN = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
B2_DUP = {'B2_01': 'r01', 'B2_02': 'r10', 'B2_07': 'r04', 'B2_10': 'r07', 'B2_11': 'r08'}
TRAIN22 = PHYSIONET + B1 + B2_TRAIN

RR_LO, RR_HI = 250.0, 700.0
JUMP = 0.25
GAP = 2.0


def log(*a):
    print(' '.join(str(x) for x in a), flush=True)


def labels_ms(tag):
    """-> (vi tri nhip ms, co 1/0, thoi luong s, nguon nhan)"""
    if tag.startswith('r'):
        D = adfecgdb_dir()
        s = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, int)
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=False, verbose=False)
        dur = raw.n_times / raw.info['sfreq']
        return s.astype(float), np.ones(len(s), int), float(dur), 'DIRECT scalp (ADFECGDB)'
    g, i = L.parse_record_id(tag)
    d = L.record_dir(g, i)
    fq, flag = L.read_marks(os.path.join(d, '%s_Fetal_R_%02d.txt' % (g, i)))
    fq_ms = fq.astype(float) * (1000.0 / L.FS_FQRS[g])
    nsamp = os.path.getsize(os.path.join(d, '%s_abSignals_%02d.ecg' % (g, i))) // 2 // L.N_COLS_AB
    dur = nsamp / L.FS_AB
    src = 'INDIRECT (abdominal, author-reviewed)' if g == 'B1' else 'DIRECT scalp (Silesia B2)'
    return fq_ms, flag, float(dur), src


def rr_audit(t_ms, dur_s):
    t = np.sort(np.asarray(t_ms, float))
    rr = np.diff(t)
    n = len(rr)
    if n < 3:
        return {}
    lo = rr < RR_LO
    hi = rr > RR_HI
    ratio = rr[1:] / rr[:-1]
    jump = np.abs(ratio - 1.0) > JUMP
    gaps = rr > GAP * 1000.0
    med = float(np.median(rr))
    return dict(
        n_beats=int(len(t)), duration_s=round(dur_s, 1), n_rr=int(n),
        rr_median_ms=round(med, 1), fhr_median_bpm=round(60000.0 / med, 1),
        rr_p01_ms=round(float(np.percentile(rr, 1)), 1), rr_p99_ms=round(float(np.percentile(rr, 99)), 1),
        rr_min_ms=round(float(rr.min()), 1), rr_max_ms=round(float(rr.max()), 1),
        pct_rr_lt250=round(100.0 * float(lo.mean()), 3), pct_rr_gt700=round(100.0 * float(hi.mean()), 3),
        pct_rr_out_of_range=round(100.0 * float((lo | hi).mean()), 3),
        n_rr_lt250=int(lo.sum()), n_rr_gt700=int(hi.sum()),
        pct_rr_jump25=round(100.0 * float(jump.mean()), 3), n_rr_jump25=int(jump.sum()),
        n_gap_gt2s=int(gaps.sum()), total_gap_s=round(float(rr[gaps].sum() / 1000.0), 2),
        pct_time_in_gap=round(100.0 * float(rr[gaps].sum() / 1000.0) / dur_s, 2),
        coverage_pct=round(100.0 * float(rr[~gaps].sum() / 1000.0) / dur_s, 2),
        pnn50=round(100.0 * float((np.abs(np.diff(rr)) > 50).mean()), 2),
    )


def stage_labels():
    out = {}
    for tag in TRAIN22 + [t for t in B2_ALL if t not in B2_TRAIN]:
        t_ms, flag, dur, src = labels_ms(tag)
        a = rr_audit(t_ms, dur)
        a['source'] = src
        a['in_train22'] = tag in TRAIN22
        a['n_flag0'] = int((flag == 0).sum())
        a['pct_flag0'] = round(100.0 * float((flag == 0).mean()), 2) if len(flag) else 0.0
        if a['n_flag0'] > 0:
            b = rr_audit(t_ms[flag == 1], dur)
            a['verified_only'] = {k: b[k] for k in ('n_beats', 'pct_rr_out_of_range', 'pct_rr_jump25',
                                                    'n_gap_gt2s', 'total_gap_s', 'coverage_pct',
                                                    'rr_max_ms', 'fhr_median_bpm')}
        out[tag] = a
        log('   %-6s %5d nhip %7.1fs  FHR %6.1f  ngoai dai %6.3f%%  nhay %6.3f%%  gap %3d (%6.2fs)  co0 %4d'
            % (tag, a['n_beats'], a['duration_s'], a['fhr_median_bpm'], a['pct_rr_out_of_range'],
               a['pct_rr_jump25'], a['n_gap_gt2s'], a['total_gap_s'], a['n_flag0']))
    cd = cinc2013_dir()
    cinc = {}
    if cd:
        for i in range(1, 76):
            rec = 'a%02d' % i
            if not os.path.isfile(os.path.join(cd, rec + '.fqrs')):
                continue
            ann = wfdb.rdann(os.path.join(cd, rec), 'fqrs')
            t_ms = np.asarray(ann.sample, float) * (1000.0 / (ann.fs or 1000.0))
            cinc[rec] = rr_audit(t_ms, 60.0)
    out['_cinc'] = cinc
    return out


def rr_series(tag):
    t, flag, dur, _ = labels_ms(tag)
    return np.diff(np.sort(t))


def cinc_rr(rec):
    cd = cinc2013_dir()
    ann = wfdb.rdann(os.path.join(cd, rec), 'fqrs')
    t = np.asarray(ann.sample, float) * (1000.0 / (ann.fs or 1000.0))
    return np.diff(np.sort(t))


def best_rr_match(rr_q, rr_r, w=40, stride=10):
    nq, nr = len(rr_q), len(rr_r)
    if nq < w or nr < w:
        return (float('inf'), -1, -1)
    V = np.lib.stride_tricks.sliding_window_view(rr_r, w)
    best = (float('inf'), -1, -1)
    for i in range(0, nq - w + 1, stride):
        q = rr_q[i:i + w]
        d = np.median(np.abs(V - q[None, :]), axis=1)
        j = int(np.argmin(d))
        if d[j] < best[0]:
            best = (float(d[j]), i, j)
    return best


def _prep(x, fs):
    b, a = sg.butter(3, [1.0 / (fs / 2), 40.0 / (fs / 2)], 'band')
    y = sg.filtfilt(b, a, np.asarray(x, float), axis=1)
    q = int(round(fs / 100.0))
    if q > 1:
        y = sg.decimate(y, q, ftype='fir', axis=1)
    y = y - y.mean(axis=1, keepdims=True)
    return (y / (y.std(axis=1, keepdims=True) + 1e-12)).astype(np.float32)


def sig_100hz(tag):
    if tag.startswith('r'):
        D = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
        x = raw.get_data()[1:5]
        fs = float(raw.info['sfreq'])
    else:
        g, i = L.parse_record_id(tag)
        d = L.record_dir(g, i)
        x = L.read_ecg_binary(os.path.join(d, '%s_abSignals_%02d.ecg' % (g, i)), L.N_COLS_AB)[:4]
        fs = 500.0
    return _prep(x, fs)


def cinc_sig(rec):
    cd = cinc2013_dir()
    r = wfdb.rdrecord(os.path.join(cd, rec))
    return _prep(r.p_signal.T, float(r.fs))


def max_ncc(tpl, ref):
    if len(tpl) > len(ref):
        tpl, ref = ref, tpl
    c = L.sliding_ncc(tpl, ref)
    return float(np.max(np.abs(c)))


def stage_overlap(full_signal=True):
    refs = PHYSIONET + B1 + B2_ALL
    log('nap chuoi RR tham chieu ...')
    RR = {t: rr_series(t) for t in refs}
    cd = cinc2013_dir()
    cincs = ['a%02d' % i for i in range(1, 76) if os.path.isfile(os.path.join(cd, 'a%02d.fqrs' % i))]
    CRR = {c: cinc_rr(c) for c in cincs}

    log('-- doi chung DUONG TINH (cap trung da biet) --')
    pos = {}
    for b2, r in B2_DUP.items():
        s, i, j = best_rr_match(RR[b2], RR[r])
        pos['%s~%s' % (b2, r)] = round(s, 3)
        log('   %s ~ %s: median|dRR| = %.2f ms' % (b2, r, s))
    log('-- doi chung AM TINH --')
    neg = {}
    for a_, b_ in [('r01', 'B1_01'), ('r04', 'B1_05'), ('B2_03', 'B1_09'), ('B2_04', 'r07'),
                   ('B1_02', 'B1_07'), ('B2_05', 'B2_06'), ('r08', 'B2_12'), ('B1_03', 'B2_09')]:
        s, _, _ = best_rr_match(RR[a_], RR[b_])
        neg['%s~%s' % (a_, b_)] = round(s, 3)
    log('   ' + json.dumps(neg))

    log('-- quet RR: %d CinC x %d ban ghi tham chieu --' % (len(cincs), len(refs)))
    table = {}
    for c in cincs:
        row = sorted((round(best_rr_match(CRR[c], RR[t])[0], 3), t) for t in refs)
        table[c] = row[:3]
    best_overall = sorted((v[0][0], c, v[0][1]) for c, v in table.items())
    log('   10 cap RR giong nhat:')
    for s, c, t in best_overall[:10]:
        log('      %s ~ %s: %.2f ms' % (c, t, s))

    res = dict(rr_positive_control=pos, rr_negative_control=neg,
               rr_top3_per_cinc={c: [list(x) for x in v] for c, v in table.items()},
               rr_best_pairs=[[round(s, 3), c, t] for s, c, t in best_overall[:20]])

    if full_signal:
        log('-- quet TIN HIEU day du (100 Hz, NCC truot) --')
        t0 = time.time()
        REFS = {t: sig_100hz(t) for t in refs}
        log('   nap tin hieu tham chieu: %.0fs' % (time.time() - t0))
        sig_pos = {}
        for b2, r in B2_DUP.items():
            m = max(max_ncc(REFS[b2][ci, 3000:9000], REFS[r][cj]) for ci in range(4) for cj in range(4))
            sig_pos['%s~%s' % (b2, r)] = round(m, 4)
            log('   [doi chung] %s ~ %s: max NCC = %.4f' % (b2, r, m))
        allmax = {}
        for k, c in enumerate(cincs):
            X = cinc_sig(c)
            tpl = [X[ci, 1000:4000] for ci in range(X.shape[0])]
            best = sorted(((round(max(max_ncc(a, REFS[t][cj]) for a in tpl for cj in range(REFS[t].shape[0])), 4), t)
                           for t in refs), reverse=True)
            allmax[c] = best[:3]
            if k % 10 == 0:
                log('   %s: max NCC %.4f voi %s  (%.0fs)' % (c, best[0][0], best[0][1], time.time() - t0))
        flat = sorted(((v[0][0], c, v[0][1]) for c, v in allmax.items()), reverse=True)
        log('   10 cap TIN HIEU giong nhat:')
        for m, c, t in flat[:10]:
            log('      %s ~ %s: NCC %.4f' % (c, t, m))
        res['signal_positive_control'] = sig_pos
        res['signal_top3_per_cinc'] = {c: [list(x) for x in v] for c, v in allmax.items()}
        res['signal_best_pairs'] = [[m, c, t] for m, c, t in flat[:20]]
        res['signal_ncc_max_overall'] = round(float(max(m for m, _, _ in flat)), 4)
        res['minutes_signal'] = round((time.time() - t0) / 60.0, 2)
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', default='all')
    ap.add_argument('--no-signal', action='store_true')
    a = ap.parse_args()
    OUT = os.path.join(HERE, 'dulieu_audit.json')
    res = json.load(open(OUT, encoding='utf-8')) if os.path.isfile(OUT) else {}
    t0 = time.time()
    if a.stage in ('all', 'labels'):
        log('===== VIEC 1a: kiem toan nhan =====')
        res['labels'] = stage_labels()
    if a.stage in ('all', 'overlap'):
        log('===== VIEC 1b: kiem chong lan =====')
        res['overlap'] = stage_overlap(full_signal=not a.no_signal)
    res['minutes_%s' % a.stage] = round((time.time() - t0) / 60.0, 2)
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    log('-> ' + OUT, '%.1f phut' % ((time.time() - t0) / 60.0))
