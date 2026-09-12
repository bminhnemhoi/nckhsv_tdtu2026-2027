# -*- coding: utf-8 -*-
"""
M3 -- THICH NGHI MIEN KHONG NHAN cho RelyFetal.
Moc so sanh: mo hinh 22 chu the, zero-shot tren CinC 2013 set-a, quy tac PSD mu nhan = 79,40 F1
(benchmark_dpss/eval_cinc75.json).

BON PHUONG PHAP THICH NGHI, khong phuong phap nao doc nhan cua mien dich:
  adabn  (a) tinh lai thong ke BatchNorm tren chinh ban ghi dich
  tent   (c) thich nghi luc kiem tra, toi thieu entropy tren tham so affine BN
  pl     (b) tu huan luyen bang nhan gia, TRANSDUCTIVE tung ban ghi
  notch  (d) thich nghi dau vao: do tan so dien luoi cua ban ghi dich (50 hay 60 Hz) tu
             pho cua chinh tin hieu do, roi chan dung tan so do. Dong co: chan doan VIEC 1
             cho thay 56/75 ban ghi CinC co dinh 60 Hz trong khi front-end chi chan 50 Hz.

QUY TAC TUYET DOI (kiem tra duoc trong ma nguon):
  nhan CinC chi xuat hien trong bien `gt`, va `gt` chi duoc truyen cho A.score() o buoc cuoi.
  Khong ham thich nghi nao nhan `gt`.
  Sieu tham so duoc chon o --stage hp, chay HOAN TOAN trong mien nguon:
  mo hinh 12 chu the (chua tung thay Silesia B1) thich nghi sang 10 chu the B1.

Chay:
  python adapt/adapt_run.py --stage hp        --shard 0/3
  python adapt/adapt_run.py --stage cinc      --shard 0/3
  python adapt/adapt_run.py --stage indomain  --shard 0/3
  python adapt/adapt_run.py --stage merge
"""
import os, sys, json, time, argparse, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
from scipy import signal as sg
import adapt_common as A

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = A.ROOT
HP_JSON = os.path.join(HERE, 'hp_selected.json')
CINC_REF_PSD = 79.40           # benchmark_dpss/eval_cinc75.json, m22, quy tac PSD, 75 ban ghi
METHODS = ('adabn', 'tent', 'pl', 'notch')


# ------------------------------------------------------------------ (d) front-end thich nghi
def mains_present(raw1000, fc):
    f, P = sg.welch(raw1000 - np.mean(raw1000), fs=1000, nperseg=min(len(raw1000), 8192))
    pk = P[(f >= fc - 1) & (f <= fc + 1)]
    bg = P[((f >= fc - 6) & (f <= fc - 2)) | ((f >= fc + 2) & (f <= fc + 6))]
    if not len(pk) or not len(bg):
        return 0.0
    return float(pk.max() / (np.median(bg) + 1e-30))


def preprocess_adaptive(raw1000, ratio_thr=1.5):
    """bandpass 10-60 Hz + chan MOI tan so dien luoi thuc su co mat trong ban ghi.
    Tan so duoc chon tu PHO CUA CHINH TIN HIEU DICH -- khong dung nhan."""
    lo, hi = A.CFG['band']
    y = A.M.bandpass(np.asarray(raw1000, float), 1000, lo, hi)
    hit = []
    for fc in (50.0, 60.0):
        if lo < fc <= hi and mains_present(raw1000, fc) >= ratio_thr:
            y = sg.filtfilt(*sg.iirnotch(fc, A.CFG['notch_q'], 1000), y)
            hit.append(fc)
    if not hit and lo < A.CFG['notch'] < hi:          # giu nguyen hanh vi goc khi khong do duoc gi
        y = sg.filtfilt(*sg.iirnotch(A.CFG['notch'], A.CFG['notch_q'], 1000), y)
    q = int(round(1000 / A.CFG['fs']))
    return sg.resample_poly(y, 1, q), hit


def leads_notch(raws):
    out, hits = [], []
    for r in raws:
        x, hit = preprocess_adaptive(r)
        rr, _ = A.M.cancel_maternal(x, A.CFG)
        out.append(dict(r_s=A.M.robust_scale(rr).astype(np.float32),
                        x_s=A.M.robust_scale(x).astype(np.float32), psd=A.psd_score(rr)))
        hits.append(hit)
    return out, hits


# ------------------------------------------------------------------ cham diem mot ban ghi
def rules(per_lead_f1, psds):
    f1 = np.asarray(per_lead_f1, float)
    pl = int(np.argmax(psds))
    return dict(psd_lead=pl, F1_psd=float(f1[pl]), F1_lead0=float(f1[0]),
                F1_mean4=float(f1.mean()), F1_oracle=float(f1.max()),
                oracle_lead=int(np.argmax(f1)))


def eval_record(net, thr, leads, gt, all_leads=True):
    idx = range(len(leads)) if all_leads else [int(np.argmax([l['psd'] for l in leads]))]
    per = {}
    for i in idx:
        det, _ = A.detect(net, thr, leads[i])
        per[i] = A.score(det, gt)                       # <-- NOI DUY NHAT dung nhan
    f1 = [per[i]['F1'] if i in per else float('nan') for i in range(len(leads))]
    out = rules(f1, [l['psd'] for l in leads]) if all_leads else \
        dict(psd_lead=list(idx)[0], F1_psd=float(f1[list(idx)[0]]))
    out['per_lead'] = {str(i): per[i] for i in per}
    return out


def run_methods(net0, thr, leads, raws, gt, hp, which=METHODS, all_leads=True):
    res = dict(base=eval_record(net0, thr, leads, gt, all_leads))
    if 'adabn' in which:
        res['adabn'] = eval_adapted(lambda l: A.m_adabn(net0, l), net0, thr, leads, gt, all_leads)
    if 'tent' in which:
        res['tent'] = eval_adapted(lambda l: A.m_tent(net0, l, hp['tent']), net0, thr, leads, gt, all_leads)
    if 'pl' in which:
        res['pl'] = eval_adapted(lambda l: A.m_pl(net0, l, hp['pl'], thr)[0], net0, thr, leads, gt, all_leads)
    if 'notch' in which and raws is not None:
        nl, hits = leads_notch(raws)
        res['notch'] = eval_record(net0, thr, nl, gt, all_leads)
        res['notch']['mains_hit'] = [[float(x) for x in h] for h in hits]
    return res


def eval_adapted(fit, net0, thr, leads, gt, all_leads):
    """fit duoc goi RIENG cho tung dao trinh (thich nghi tung dao trinh cua ban ghi dich)."""
    idx = range(len(leads)) if all_leads else [int(np.argmax([l['psd'] for l in leads]))]
    per = {}
    for i in idx:
        net = fit(leads[i])
        det, _ = A.detect(net, thr, leads[i])
        per[i] = A.score(det, gt)
    f1 = [per[i]['F1'] if i in per else float('nan') for i in range(len(leads))]
    out = rules(f1, [l['psd'] for l in leads]) if all_leads else \
        dict(psd_lead=list(idx)[0], F1_psd=float(f1[list(idx)[0]]))
    out['per_lead'] = {str(i): per[i] for i in per}
    return out


# ------------------------------------------------------------------ GIAI DOAN hp (trong mien nguon)
# Mo hinh 12 chu the CHUA TUNG THAY Silesia B1 -> B1 la mot dich chuyen he-ghi THAT
# nam HOAN TOAN trong mien nguon, co nhan hop phap. Chon sieu tham so o day.
GRID = dict(
    tent=[dict(lr=1e-4, steps=10, batch=16), dict(lr=1e-3, steps=10, batch=16),
          dict(lr=1e-3, steps=30, batch=16)],
    pl=[dict(lr=1e-4, steps=40, batch=16, conf=0.90, sigma_ms=12.0),
        dict(lr=3e-4, steps=40, batch=16, conf=0.90, sigma_ms=12.0),
        dict(lr=3e-4, steps=40, batch=16, conf=0.98, sigma_ms=12.0)],
)


def stage_hp(shard, nshard, log):
    net0, thr = A.load_net('fetalqrs_tcn_12_production.pt')
    tags = [t for i, t in enumerate(A.B1) if i % nshard == shard]
    out = {}
    for tag in tags:
        t0 = time.time()
        leads, gt, meta, raws = A.prep_subject(tag, with_raw=True)
        pl_i = int(np.argmax([l['psd'] for l in leads]))
        lead = leads[pl_i]
        row = dict(base=A.score(A.detect(net0, thr, lead)[0], gt)['F1'])
        for j, hp in enumerate(GRID['tent']):
            row['tent%d' % j] = A.score(A.detect(A.m_tent(net0, lead, hp), thr, lead)[0], gt)['F1']
        for j, hp in enumerate(GRID['pl']):
            net, _ = A.m_pl(net0, lead, hp, thr)
            row['pl%d' % j] = A.score(A.detect(net, thr, lead)[0], gt)['F1']
        nl, hits = leads_notch(raws)
        row['notch'] = A.score(A.detect(net0, thr, nl[int(np.argmax([l['psd'] for l in nl]))])[0], gt)['F1']
        out[tag] = row
        log('  hp %s %.0fs %s' % (tag, time.time() - t0,
                                  ' '.join('%s=%.2f' % (k, v) for k, v in row.items())))
    return out


# ------------------------------------------------------------------ GIAI DOAN hpsim
# Be mat chon sieu tham so THU HAI, va la be mat CHINH: mo phong lai DUNG cac dich chuyen
# da do duoc o VIEC 1 ngay tren du lieu TRONG MIEN (co nhan hop phap):
#   (1) cat con 60 s   -- CinC 60 s vs trong mien 300-1198 s
#   (2) luong tu hoa ve ~10,1 bit huu hieu  -- CinC 10,13 bit vs ADFECGDB 11,49 bit
#   (3) bom dien luoi 60 Hz den ti so dinh/nen ~1,64  -- trung vi do duoc tren CinC
# KHONG mot mau nao cua CinC duoc dung. Nhan dung o day la nhan TRONG MIEN.
SIM = dict(win_s=60.0, n_win=3, eff_bits=10.13, mains_hz=60.0, mains_ratio=1.64)


def _quantize(x, bits):
    rng = float(np.percentile(x, 99.9) - np.percentile(x, 0.1))
    if rng <= 0:
        return x
    step = rng / (2.0 ** bits - 1)
    return np.round(x / step) * step


def _inject_mains(x, fs, fc, target_ratio, sec_ratio=None):
    """bom sin fc cho den khi ti so dinh/nen tai fc dat target_ratio (tim kiem nhi phan)."""
    t = np.arange(len(x)) / fs
    base = mains_present(x, fc)
    if base >= target_ratio:
        return x, 0.0
    lo, hi = 0.0, float(np.std(x)) * 4 + 1e-9
    for _ in range(18):
        a = 0.5 * (lo + hi)
        r = mains_present(x + a * np.sin(2 * np.pi * fc * t), fc)
        if r < target_ratio:
            lo = a
        else:
            hi = a
    a = 0.5 * (lo + hi)
    return x + a * np.sin(2 * np.pi * fc * t), float(a)


def simulate_windows(raws, gt, dur_s):
    """-> danh sach (leads_da_tien_xu_ly, gt_cua_cua_so, raws_cua_cua_so)"""
    n = int(SIM['win_s'] * 1000)
    starts = [int(f * (dur_s * 1000 - n)) for f in (0.10, 0.45, 0.80)][:SIM['n_win']]
    out = []
    for s0 in starts:
        if s0 < 0:
            continue
        wr, leads = [], []
        for raw in raws:
            seg = np.asarray(raw[s0:s0 + n], float)
            seg = _quantize(seg, SIM['eff_bits'])
            seg, _a = _inject_mains(seg, 1000.0, SIM['mains_hz'], SIM['mains_ratio'])
            wr.append(seg)
            x = A.M.preprocess(seg, 1000, A.CFG)
            rr, _ = A.M.cancel_maternal(x, A.CFG)
            leads.append(dict(r_s=A.M.robust_scale(rr).astype(np.float32),
                              x_s=A.M.robust_scale(x).astype(np.float32), psd=A.psd_score(rr)))
        g = np.asarray(gt, int)
        g = g[(g >= s0) & (g < s0 + n)] - s0
        out.append((leads, g, wr))
    return out


def stage_hpsim(shard, nshard, log):
    fmap = fold_of_subject()
    tags = [t for i, t in enumerate(A.ALL22) if i % nshard == shard]
    out = {}
    for tag in tags:
        t0 = time.time()
        fold, _ = fmap[tag]
        net0, thr = A.load_net('fetalqrs_tcn_22_fold_%s.pt' % fold)
        leads, gt, meta, raws = A.prep_subject(tag, with_raw=True)
        del leads
        rows = []
        for wleads, wgt, wraws in simulate_windows(raws, gt, meta['dur_s']):
            if len(wgt) < 20:
                continue
            i = int(np.argmax([l['psd'] for l in wleads]))
            lead = wleads[i]
            r = dict(base=A.score(A.detect(net0, thr, lead)[0], wgt)['F1'],
                     adabn=A.score(A.detect(A.m_adabn(net0, lead), thr, lead)[0], wgt)['F1'])
            for j, hp in enumerate(GRID['tent']):
                r['tent%d' % j] = A.score(A.detect(A.m_tent(net0, lead, hp), thr, lead)[0], wgt)['F1']
            for j, hp in enumerate(GRID['pl']):
                r['pl%d' % j] = A.score(A.detect(A.m_pl(net0, lead, hp, thr)[0], thr, lead)[0], wgt)['F1']
            nl, _h = leads_notch(wraws)
            r['notch'] = A.score(A.detect(net0, thr, nl[int(np.argmax([l['psd'] for l in nl]))])[0], wgt)['F1']
            rows.append(r)
        out[tag] = rows
        if rows:
            log('  hpsim %s fold%s %.0fs n_win=%d %s' % (
                tag, fold, time.time() - t0, len(rows),
                ' '.join('%s=%.1f' % (k, float(np.mean([q[k] for q in rows]))) for k in rows[0])))
    return out


# ------------------------------------------------------------------ GIAI DOAN cinc
def stage_cinc(shard, nshard, hp, log):
    net0, thr = A.load_net(A.PROD22)
    _, recs = A.list_cinc()
    mine = [r for i, r in enumerate(recs) if i % nshard == shard]
    out = {}
    for rec in mine:
        t0 = time.time()
        leads, gt, meta, raws = A.prep_cinc(rec, with_raw=True)
        out[rec] = run_methods(net0, thr, leads, raws, gt, hp)
        out[rec]['meta'] = meta
        log('  cinc %s %.0fs base %.2f adabn %.2f tent %.2f pl %.2f notch %.2f'
            % (rec, time.time() - t0, out[rec]['base']['F1_psd'], out[rec]['adabn']['F1_psd'],
               out[rec]['tent']['F1_psd'], out[rec]['pl']['F1_psd'], out[rec]['notch']['F1_psd']))
    return out


# ------------------------------------------------------------------ GIAI DOAN indomain
def fold_of_subject():
    d = json.load(open(os.path.join(ROOT, 'model', 'train_22.json'), encoding='utf-8'))
    m = {}
    for k, f in d['folds'].items():
        for s in f['test_subjects']:
            m[s] = (k, float(f['threshold']))
    return m


def stage_indomain(shard, nshard, hp, log):
    fmap = fold_of_subject()
    tags = [t for i, t in enumerate(A.ALL22) if i % nshard == shard]
    out = {}
    for tag in tags:
        t0 = time.time()
        fold, thr = fmap[tag]
        net0, thr_ck = A.load_net('fetalqrs_tcn_22_fold_%s.pt' % fold)
        leads, gt, meta, raws = A.prep_subject(tag, with_raw=True)
        out[tag] = run_methods(net0, thr_ck, leads, raws, gt, hp, all_leads=False)
        out[tag]['meta'] = dict(meta, fold=fold, threshold=thr_ck)
        log('  indomain %s fold%s %.0fs base %.2f adabn %.2f tent %.2f pl %.2f notch %.2f'
            % (tag, fold, time.time() - t0, out[tag]['base']['F1_psd'], out[tag]['adabn']['F1_psd'],
               out[tag]['tent']['F1_psd'], out[tag]['pl']['F1_psd'], out[tag]['notch']['F1_psd']))
    return out


# ------------------------------------------------------------------ driver
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', required=True, choices=('hp', 'hpsim', 'cinc', 'indomain'))
    ap.add_argument('--shard', default='0/1')
    a = ap.parse_args()
    shard, nshard = (int(x) for x in a.shard.split('/'))
    tag = '%s_%d_%d' % (a.stage, shard, nshard)
    logp = os.path.join(HERE, 'shard_%s.log' % tag)
    fh = open(logp, 'w', encoding='utf-8')

    def log(s):
        print(s, flush=True); fh.write(s + '\n'); fh.flush()

    hp = A.HP
    if a.stage in ('cinc', 'indomain'):
        if not os.path.isfile(HP_JSON):
            raise SystemExit('Chua co %s -- phai chay --stage hp truoc.' % HP_JSON)
        hp = json.load(open(HP_JSON, encoding='utf-8'))['selected']
    log('=== %s | shard %d/%d | %s ===' % (a.stage, shard, nshard, time.strftime('%Y-%m-%d %H:%M:%S')))
    log('sieu tham so: %s' % json.dumps(hp))
    t0 = time.time()
    fn = dict(hp=stage_hp, hpsim=stage_hpsim, cinc=stage_cinc, indomain=stage_indomain)[a.stage]
    res = fn(*((shard, nshard, log) if a.stage in ('hp', 'hpsim') else (shard, nshard, hp, log)))
    outp = os.path.join(HERE, 'shard_%s.json' % tag)
    json.dump(res, open(outp, 'w', encoding='utf-8'), indent=1)
    log('DONE %.1f phut -> %s' % ((time.time() - t0) / 60, outp))


if __name__ == '__main__':
    main()
