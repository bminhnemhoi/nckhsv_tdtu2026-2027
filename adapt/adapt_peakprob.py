# -*- coding: utf-8 -*-
"""
M3 bo sung -- do lai MOI phuong phap thich nghi duoi QUY TAC CHON KENH 'peakprob' cua M5.

Ly do: moc ngoai mien da doi. Truoc day la 79,40 (quy tac PSD mu nhan); sau ket qua M5 no la
85,60 (peakprob, hau kiem) va 84,54 (gate, tien dang ky). Cac shard M3 chi luu F1 tung kenh,
KHONG luu diem peakprob, nen khong the suy ra chi so kenh cua quy tac peakprob tu chung.
Tep nay chay lai suy luan de lay diem peakprob, dong thoi KIEM CHUNG rang F1 tung kenh
tai lap dung y het shard cu (sai so < 1e-6) -- neu lech thi dung.

QUY TAC peakprob (sao nguyen tu analysis/chonkenh_rules.py:183):
    voi moi kenh: cat thanh doan 4 s khong chong lan; moi doan lay TRUNG BINH xac suat cua
    mo hinh tai cac dinh DA PHAT HIEN trong doan do (0.0 neu doan khong co dinh);
    diem cua kenh = TRUNG VI qua cac doan. Chon kenh co diem cao nhat. KHONG dung nhan.

Nhan CinC chi duoc dung trong A.score() o buoc cham diem.

Chay: python adapt/adapt_peakprob.py --shard 0/3
      python adapt/adapt_peakprob.py --stage merge
"""
import os, sys, json, time, argparse, glob, gc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
import adapt_common as A
import adapt_run as R

HERE = os.path.dirname(os.path.abspath(__file__))
SEG = int(4.0 * A.CFG['fs'])
METHODS = ('base', 'notch', 'adabn', 'tent', 'pl')


def peakprob_score(prob, det250):
    """diem peakprob cua mot kenh -- KHONG nhin nhan"""
    n_seg = len(prob) // SEG
    if n_seg == 0:
        return 0.0
    vals = []
    for k in range(n_seg):
        a, b = k * SEG, (k + 1) * SEG
        d = det250[(det250 >= a) & (det250 < b)] - a
        vals.append(float(np.mean(prob[a:b][d])) if len(d) else 0.0)
    return float(np.nanmedian(vals))


def eval_leads(net, thr, leads, gt):
    f1, pp, psd = [], [], []
    for lead in leads:
        prob = A.M.probability_series(net, lead['r_s'], lead['x_s'], A.CFG)
        det250 = A.M.pick_peaks(prob, thr, A.CFG)
        det1000 = det250.astype(np.int64) * A.Q
        f1.append(float(A.score(det1000, gt)['F1']))       # <-- noi duy nhat dung nhan
        pp.append(peakprob_score(prob, det250))
        psd.append(float(lead['psd']))
    return f1, pp, psd


def pack(f1, pp, psd):
    f1 = np.asarray(f1, float)
    return dict(per_lead_F1=[float(v) for v in f1], peakprob_score=pp, psd_score=psd,
                peakprob_lead=int(np.argmax(pp)), F1_peakprob=float(f1[int(np.argmax(pp))]),
                psd_lead=int(np.argmax(psd)), F1_psd=float(f1[int(np.argmax(psd))]),
                F1_mean4=float(f1.mean()), F1_oracle=float(f1.max()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shard', default='0/1')
    ap.add_argument('--stage', default='run')
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    if a.stage == 'merge':
        out = {}
        for f in sorted(glob.glob(os.path.join(HERE, 'shard_pp_*.json'))):
            out.update(json.load(open(f, encoding='utf-8')))
        json.dump(out, open(os.path.join(HERE, 'peakprob_merged.json'), 'w', encoding='utf-8'), indent=1)
        print('merged %d ban ghi' % len(out)); return

    si, sn = (int(x) for x in a.shard.split('/'))
    hp = json.load(open(os.path.join(HERE, 'hp_selected.json'), encoding='utf-8'))['selected']
    # F1 tham chieu tu shard M3 cu -- de KIEM CHUNG tai lap
    ref = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'shard_cinc_*.json'))):
        ref.update(json.load(open(f, encoding='utf-8')))
    D, recs = A.list_cinc()
    recs = [r for r in recs if os.path.isfile(os.path.join(D, r + '.fqrs'))]
    if a.limit:
        recs = recs[:a.limit]
    mine = recs[si::sn]
    outp = os.path.join(HERE, 'shard_pp_%d_%d.json' % (si, sn))
    res = json.load(open(outp, encoding='utf-8')) if os.path.isfile(outp) else {}
    print('=== peakprob | shard %d/%d | %d ban ghi | %s ===' % (si, sn, len(mine), time.strftime('%H:%M:%S')), flush=True)
    net0, thr = A.load_net()
    t00 = time.time()
    for rec in mine:
        if rec in res:
            print('  %s [cache]' % rec, flush=True); continue
        t0 = time.time()
        leads, gt, meta, raws = A.prep_cinc(rec, with_raw=True)
        nl, hits = R.leads_notch(raws)
        row = {}
        for m in METHODS:
            if m == 'base':
                row[m] = pack(*eval_leads(net0, thr, leads, gt))
            elif m == 'notch':
                row[m] = pack(*eval_leads(net0, thr, nl, gt))
            else:
                f1, pp, psd = [], [], []
                for lead in leads:
                    if m == 'adabn':
                        net = A.m_adabn(net0, lead)
                    elif m == 'tent':
                        net = A.m_tent(net0, lead, hp['tent'])
                    else:
                        net = A.m_pl(net0, lead, hp['pl'], thr)[0]
                    g1, g2, g3 = eval_leads(net, thr, [lead], gt)
                    f1 += g1; pp += g2; psd += g3
                row[m] = pack(f1, pp, psd)
            # KIEM CHUNG tai lap so voi shard M3 cu
            if rec in ref and m in ref[rec]:
                for i, v in enumerate(row[m]['per_lead_F1']):
                    w = float(ref[rec][m]['per_lead'][str(i)]['F1'])
                    assert abs(v - w) < 1e-6, 'KHONG TAI LAP %s %s kenh %d: %.6f != %.6f' % (rec, m, i, v, w)
        res[rec] = row
        json.dump(res, open(outp, 'w', encoding='utf-8'), indent=1)
        del leads, nl, raws, gt
        gc.collect()
        print('  %s %4ds  ' % (rec, time.time() - t0)
              + ' '.join('%s psd %.1f pp %.1f' % (m, row[m]['F1_psd'], row[m]['F1_peakprob']) for m in METHODS),
              flush=True)
    print('DONE %.1f phut -> %s' % ((time.time() - t00) / 60, outp), flush=True)


if __name__ == '__main__':
    main()
