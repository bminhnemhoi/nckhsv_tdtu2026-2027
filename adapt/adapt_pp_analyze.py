# -*- coding: utf-8 -*-
"""
M3 bo sung -- gop ket qua peakprob, doi chieu voi CA HAI moc:
   79,40  quy tac PSD mu nhan (moc cu, de so voi so da cong bo)
   85,60  quy tac peakprob cua M5 (moc moi ngoai mien, hau kiem)
   84,54  quy tac gate cua M5 (tien dang ky) -- chi trich dan, khong tinh lai o day

Ghi bo sung vao adapt/adapt_results.json khoa 'peakprob'.
"""
import os, sys, json, glob, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import adapt_common as A

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'adapt_results.json')
M5 = os.path.join(A.ROOT, 'analysis', 'chonkenh_results.json')
METHODS = ('base', 'notch', 'adabn', 'tent', 'pl')
REF_PSD, REF_PP, REF_GATE = 79.3986490628945, 85.5957, 84.5366


def main():
    pp = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'shard_pp_*.json'))):
        pp.update(json.load(open(f, encoding='utf-8')))
    keys = sorted(pp)
    print('ban ghi co peakprob: %d' % len(keys))
    if len(keys) < 75:
        print('CHUA DU 75 -- dung lai'); return

    # ---- KIEM CHUNG 1: base duoi quy tac peakprob phai TRUNG voi M5 tung ban ghi
    m5 = json.load(open(M5, encoding='utf-8'))['F1_tung_ban_ghi']['cinc']
    bad = [(k, pp[k]['base']['F1_peakprob'], m5[k]['peakprob']) for k in keys
           if abs(pp[k]['base']['F1_peakprob'] - m5[k]['peakprob']) > 1e-6]
    assert not bad, 'peakprob khong tai lap M5: %s' % bad[:5]
    bad = [(k, pp[k]['base']['F1_psd'], m5[k]['psd']) for k in keys
           if abs(pp[k]['base']['F1_psd'] - m5[k]['psd']) > 1e-6]
    assert not bad, 'psd khong tai lap M5: %s' % bad[:5]
    print('KIEM CHUNG: 75/75 ban ghi, quy tac peakprob VA psd tai lap dung M5 (<1e-6)')

    base_psd = np.array([pp[k]['base']['F1_psd'] for k in keys])
    base_pp = np.array([pp[k]['base']['F1_peakprob'] for k in keys])
    out = dict(n=len(keys),
               moc=dict(psd=float(base_psd.mean()), peakprob=float(base_pp.mean()),
                        gate_trich_dan_M5=REF_GATE),
               kiem_chung='F1 tung kenh tai lap shard M3 <1e-6; F1 quy tac psd/peakprob tai lap M5 <1e-6',
               bang={})
    for rule, ref, refname in (('F1_psd', base_psd, 'moc psd 79,40'),
                               ('F1_peakprob', base_pp, 'moc peakprob 85,60')):
        out['bang'][rule] = {}
        for m in METHODS:
            v = np.array([pp[k][m][rule] for k in keys])
            st = A.paired_stats(v, ref)
            st['records_worse'] = sorted(((k, float(v[i] - ref[i])) for i, k in enumerate(keys)
                                          if v[i] < ref[i] - 1e-9), key=lambda e: e[1])[:8]
            st['records_better'] = sorted(((k, float(v[i] - ref[i])) for i, k in enumerate(keys)
                                           if v[i] > ref[i] + 1e-9), key=lambda e: -e[1])[:8]
            st['so_voi'] = refname
            out['bang'][rule][m] = st
    # doi chieu cheo: moi phuong phap duoi peakprob so voi BASE-PSD (79,40)
    out['bang']['F1_peakprob_vs_moc_psd'] = {}
    for m in METHODS:
        v = np.array([pp[k][m]['F1_peakprob'] for k in keys])
        out['bang']['F1_peakprob_vs_moc_psd'][m] = A.paired_stats(v, base_psd)
    # chan tren: oracle theo tung phuong phap
    out['oracle'] = {m: float(np.mean([pp[k][m]['F1_oracle'] for k in keys])) for m in METHODS}
    out['mean4'] = {m: float(np.mean([pp[k][m]['F1_mean4'] for k in keys])) for m in METHODS}
    # quy tac peakprob co doi kenh sau thich nghi khong?
    out['doi_kenh'] = {m: int(sum(1 for k in keys
                                  if pp[k][m]['peakprob_lead'] != pp[k]['base']['peakprob_lead']))
                       for m in METHODS}
    out['per_record'] = {k: {m: dict(psd=pp[k][m]['F1_psd'], peakprob=pp[k][m]['F1_peakprob'],
                                     oracle=pp[k][m]['F1_oracle'],
                                     pp_lead=pp[k][m]['peakprob_lead']) for m in METHODS}
                         for k in keys}

    res = json.load(open(RES, encoding='utf-8'))
    res['peakprob'] = out
    json.dump(res, open(RES, 'w', encoding='utf-8'), indent=1)

    LAB = dict(base='khong thich nghi (moc)', notch='(d) chan dien luoi thich nghi',
               adabn='(a) AdaBN', tent='(c) TENT', pl='(b) tu huan luyen nhan gia')
    for rule, tag in (('F1_psd', 'QUY TAC PSD (moc 79,40)'), ('F1_peakprob', 'QUY TAC PEAKPROB (moc 85,60)')):
        print('\n===== CinC 75 ban ghi | %s =====' % tag)
        print('%-30s %7s %8s %20s %9s %6s %6s %6s %6s %8s' %
              ('phuong phap', 'F1', 'hieu', 'KTC95 bootstrap', 'p Wilc', 'thang', 'thua', '>=90', '<50', 'tut max'))
        for m in METHODS:
            r = out['bang'][rule][m]
            print('%-30s %7.2f %+8.2f [%+7.2f;%+7.2f] %9.2e %6d %6d %6d %6d %8.2f' %
                  (LAB[m], r['mean_new'], r['mean_diff'], r['ci95'][0], r['ci95'][1], r['p_wilcoxon'],
                   r['n_win'], r['n_loss'], r['ge90'], r['lt50'], r['max_drop']))
    print('\noracle theo phuong phap (chan tren cua MOI quy tac chon kenh):')
    for m in METHODS:
        print('  %-30s oracle %6.2f   TB 4 kenh %6.2f   doi kenh peakprob %d/75'
              % (LAB[m], out['oracle'][m], out['mean4'][m], out['doi_kenh'][m]))
    print('\n-> %s (khoa "peakprob")' % RES)


if __name__ == '__main__':
    main()
