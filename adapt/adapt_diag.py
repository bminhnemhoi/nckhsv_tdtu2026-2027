# -*- coding: utf-8 -*-
"""
M3 / VIEC 1 -- CHAN DOAN DICH CHUYEN MIEN.
So sanh phan bo cua CinC 2013 set-a (75 ban ghi) voi mien huan luyen (22 chu the
ADFECGDB + Silesia). TAT CA cac phep do o day deu KHONG DUNG NHAN
(khong doc <rec>.fqrs cua CinC va khong doc nhan cua 22 chu the) -- de ket luan
chan doan khong bi nhiem nhan mien dich.

Chay:  python adapt/adapt_diag.py            (toan bo)
       python adapt/adapt_diag.py --limit 5  (thu nhanh)
Ra:    adapt/diag_results.json
"""
import os, sys, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import signal as sg, stats
import adapt_common as A

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'diag_results.json')


def band_frac(x, fs, lo, hi, f, P):
    m = (f >= lo) & (f < hi)
    return float(P[m].sum() / (P.sum() + 1e-30))


def lead_features(raw1000, lead):
    """dac trung KHONG NHAN cho mot dao trinh."""
    x = np.asarray(raw1000, float)
    f, P = sg.welch(x - x.mean(), fs=1000, nperseg=min(len(x), 8192))
    cum = np.cumsum(P) / (P.sum() + 1e-30)
    sef95 = float(f[np.searchsorted(cum, 0.95)]) if len(f) else float('nan')
    # dinh dien luoi: cong suat 49-51 / 59-61 so voi nen xung quanh
    def mains(fc):
        pk = P[(f >= fc - 1) & (f <= fc + 1)]
        bg = P[((f >= fc - 6) & (f <= fc - 2)) | ((f >= fc + 2) & (f <= fc + 6))]
        return float(pk.max() / (np.median(bg) + 1e-30)) if len(pk) and len(bg) else float('nan')
    # luong tu hoa
    d = np.diff(np.unique(np.round(x, 12)))
    qstep = float(np.median(d)) if len(d) else float('nan')
    nuniq = int(len(np.unique(x)))
    rng = float(np.percentile(x, 99.9) - np.percentile(x, 0.1))
    r_s, x_s = lead['r_s'], lead['x_s']
    res_raw = r_s  # da robust_scale
    # ty le nen me: nang luong truoc / sau khu me trong bang 10-60
    return dict(
        raw_sd=float(x.std()),
        raw_iqr=float(np.subtract(*np.percentile(x, [75, 25]))),
        q_step=qstep, n_unique=nuniq, dyn_range=rng,
        eff_bits=float(np.log2(rng / qstep + 1)) if qstep and qstep > 0 else float('nan'),
        clip_frac=float(np.mean(np.abs(x) >= 0.999 * np.max(np.abs(x)))),
        p_0_10=band_frac(x, 1000, 0, 10, f, P), p_10_60=band_frac(x, 1000, 10, 60, f, P),
        p_60_100=band_frac(x, 1000, 60, 100, f, P), p_100p=band_frac(x, 1000, 100, 500, f, P),
        sef95=sef95, mains50=mains(50.0), mains60=mains(60.0),
        rs_kurtosis=float(stats.kurtosis(res_raw)), rs_p999=float(np.percentile(np.abs(res_raw), 99.9)),
        rs_sd=float(res_raw.std()), xs_kurtosis=float(stats.kurtosis(x_s)), xs_sd=float(x_s.std()),
        psd_fhr=float(lead['psd']),
    )


def record_features(leads, raws, meta):
    per = [lead_features(raws[i], leads[i]) for i in range(len(leads))]
    # nhip me + so nhip me dung lam mau (anh huong chat luong khu me)
    x0 = leads[0]
    mpk = A.M.detect_maternal_qrs(x0['x_s'], A.CFG)
    mhr = 60.0 / (np.median(np.diff(mpk)) / A.CFG['fs']) if len(mpk) > 2 else float('nan')
    # nhip thai uoc tinh KHONG NHAN: dinh PSD bao hinh tren dao trinh co psd cao nhat
    best = int(np.argmax([l['psd'] for l in leads]))
    r = leads[best]['r_s']
    e = np.abs(sg.hilbert(r - r.mean())); e = e - e.mean()
    f, P = sg.welch(e, fs=A.CFG['fs'], nperseg=min(len(e), 4096))
    m = (f >= A.FHR_BAND[0]) & (f <= A.FHR_BAND[1])
    fhr = float(f[m][np.argmax(P[m])] * 60.0) if m.any() else float('nan')
    rhythm = float(P[m].max() / (np.median(P[(f > 0.5) & (f < 8)]) + 1e-30)) if m.any() else float('nan')
    out = dict(dur_s=meta['dur_s'], fs0=meta['fs0'], n_ch=meta['n_ch'],
               n_mqrs=int(len(mpk)), mhr_bpm=float(mhr), fhr_bpm_blind=fhr, rhythmicity=rhythm)
    for k in per[0]:
        v = [p[k] for p in per]
        out[k] = float(np.nanmean(v))
        out[k + '_max'] = float(np.nanmax(v))
    return out


def summarize(rows, keys):
    out = {}
    for k in keys:
        v = np.asarray([r[k] for r in rows], float)
        v = v[np.isfinite(v)]
        if not len(v):
            continue
        out[k] = dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                      median=float(np.median(v)), q25=float(np.percentile(v, 25)),
                      q75=float(np.percentile(v, 75)), min=float(v.min()), max=float(v.max()), n=int(len(v)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    t0 = time.time()
    _, recs = A.list_cinc()
    if a.limit:
        recs = recs[:a.limit]
    src = {}
    print('CinC 2013 set-a: %d ban ghi' % len(recs), flush=True)
    for i, rec in enumerate(recs):
        leads, _gt, meta, raws = A.prep_cinc(rec, with_raw=True)   # _gt KHONG dung o day
        src[rec] = record_features(leads, raws, meta)
        print('  [%2d/%d] %s %.1fs' % (i + 1, len(recs), rec, time.time() - t0), flush=True)
    tgt = {}
    tags = A.ALL22[:a.limit] if a.limit else A.ALL22
    print('trong mien: %d chu the' % len(tags), flush=True)
    for i, tag in enumerate(tags):
        leads, _gt, meta, raws = A.prep_subject(tag, with_raw=True)
        tgt[tag] = record_features(leads, raws, meta)
        tgt[tag]['group'] = meta['group']
        print('  [%2d/%d] %s %.1fs' % (i + 1, len(tags), tag, time.time() - t0), flush=True)
    keys = [k for k, v in list(src.values())[0].items() if isinstance(v, float) or isinstance(v, int)]
    S = summarize(list(src.values()), keys)
    T = summarize(list(tgt.values()), keys)
    shift = []
    for k in keys:
        if k not in S or k not in T:
            continue
        sd_pool = np.sqrt((S[k]['sd'] ** 2 + T[k]['sd'] ** 2) / 2) + 1e-30
        d = (S[k]['mean'] - T[k]['mean']) / sd_pool
        try:
            p = float(stats.mannwhitneyu([r[k] for r in src.values() if np.isfinite(r[k])],
                                         [r[k] for r in tgt.values() if np.isfinite(r[k])]).pvalue)
        except Exception:
            p = float('nan')
        shift.append(dict(feature=k, cinc_mean=S[k]['mean'], cinc_median=S[k]['median'],
                          indomain_mean=T[k]['mean'], indomain_median=T[k]['median'],
                          cohens_d=float(d), abs_d=float(abs(d)), p_mannwhitney=p))
    # dac trung PHU THUOC DON VI (V so voi uV, so kenh ghi) -> KHONG dung de xep hang dich chuyen,
    # vi robust_scale da loai bo thang do truoc khi vao mang. Van luu lai de tham khao.
    UNIT_DEP = ('raw_sd', 'raw_iqr', 'q_step', 'dyn_range', 'n_unique', 'n_ch', 'fs0')
    for r in shift:
        r['unit_dependent'] = any(r['feature'] == k or r['feature'] == k + '_max' for k in UNIT_DEP)
    shift.sort(key=lambda r: (r['unit_dependent'], -r['abs_d']))
    res = dict(meta=dict(n_cinc=len(src), n_indomain=len(tgt), minutes=round((time.time() - t0) / 60, 2),
                         note='moi phep do deu KHONG dung nhan'),
               cinc_summary=S, indomain_summary=T, shift_ranked=shift,
               per_record_cinc=src, per_subject_indomain=tgt)
    json.dump(res, open(OUT, 'w', encoding='utf-8'), indent=1)
    print('\n=== 15 dich chuyen lon nhat (|Cohen d|) ===')
    for r in [q for q in shift if not q['unit_dependent']][:15]:
        print('%-16s CinC %10.3f | trong mien %10.3f | d %+7.2f | p %.2e'
              % (r['feature'], r['cinc_mean'], r['indomain_mean'], r['cohens_d'], r['p_mannwhitney']))
    print('-> %s (%.1f phut)' % (OUT, (time.time() - t0) / 60))


if __name__ == '__main__':
    main()
