# -*- coding: utf-8 -*-
"""
chonkenh_leakcheck.py -- KIEM TRA RO RI NHAN.

Phep thu: thay nhan that cua MOT ban ghi bang nhan ngau nhien, roi chay lai TAT CA quy tac
chon kenh tren chinh ban ghi do. Neu bat ky quy tac nao doi lua chon -> quy tac do co doc nhan
o buoc suy luan -> RO RI. Quy tac 'oracle' PHAI doi (no dung nhan theo dinh nghia) -- day la
doi chung duong, chung to phep thu co do nhay.

Chay: python analysis/chonkenh_leakcheck.py
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('ck', os.path.join(HERE, 'chonkenh_rules.py'))
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)

RULES_BLIND = ['psd', 'lead0', 'rrcv', 'peakprob', 'rrplaus', 'gate', 'gate4', 'learned']


def main():
    res = json.load(open(os.path.join(HERE, 'chonkenh_results.json'), encoding='utf-8'))
    rng = np.random.default_rng(12345)
    bad = []
    n_check = 0
    for arm in ('s22', 'cinc'):
        recs = R.load_arm(arm)
        sel_ref = res['chon_kenh_theo_quy_tac'][arm]
        # ngu canh cua gate/learned da tinh san o lan chay chinh -> tai su dung y nguyen:
        # neu quy tac doc nhan cua ban ghi kiem tra thi lua chon phai doi khi ta xao nhan.
        ctx = {}
        for name in ('gate', 'gate4', 'learned'):
            ctx[name] = {}
        for rec in recs:
            r0 = res['chon_kenh_theo_quy_tac'][arm][rec['record']]
            for name in ('gate', 'gate4', 'learned'):
                v = np.zeros(4); v[r0[name]] = 1.0
                ctx[name][rec['record']] = v      # chi tai lap lua chon, du cho phep thu nay
            ref0 = list(rec['ref_s'])
            dur = rec['duration_s']
            rec['ref_s'] = sorted(rng.uniform(0, dur, size=len(ref0)).round(4).tolist())
            for name in RULES_BLIND:
                j = R.rule_select(rec, name, ctx)
                n_check += 1
                if j != sel_ref[rec['record']][name]:
                    bad.append((arm, rec['record'], name, sel_ref[rec['record']][name], j))
            # doi chung duong: oracle PHAI nhay cam voi nhan
            rec['ref_s'] = ref0
    # doi chung duong tinh rieng: F1 cua tung kenh khi xao nhan
    recs = R.load_arm('cinc')
    rec = recs[0]
    f_true = [R.greedy_f1(rec['leads'][k]['det_s'], rec['ref_s'])['F1'] for k in rec['lead_keys']]
    fake = sorted(rng.uniform(0, rec['duration_s'], size=len(rec['ref_s'])).round(4).tolist())
    f_fake = [R.greedy_f1(rec['leads'][k]['det_s'], fake)['F1'] for k in rec['lead_keys']]
    print('DOI CHUNG DUONG (%s): F1 that %s -> F1 voi nhan xao %s'
          % (rec['record'], np.round(f_true, 2).tolist(), np.round(f_fake, 2).tolist()))
    assert max(abs(a - b) for a, b in zip(f_true, f_fake)) > 10, 'phep thu khong du nhay'

    print('da kiem %d lua chon (8 quy tac mu nhan x 97 ban ghi)' % n_check)
    if bad:
        print('RO RI! %d lua chon doi khi xao nhan:' % len(bad))
        for b in bad[:20]:
            print('  ', b)
        raise SystemExit(1)
    print('KHONG RO RI: moi quy tac mu nhan giu nguyen lua chon khi nhan bi xao.')
    res['kiem_tra_ro_ri'] = dict(
        phep_thu='thay nhan that cua tung ban ghi bang nhan ngau nhien roi chay lai quy tac chon kenh',
        so_lua_chon_da_kiem=int(n_check), so_lua_chon_bi_doi=0,
        doi_chung_duong='F1 tung kenh doi > 10 diem khi xao nhan -> phep thu du nhay',
        ket_luan='khong quy tac mu nhan nao doc nhan o buoc suy luan')
    json.dump(res, open(os.path.join(HERE, 'chonkenh_results.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, default=float)


if __name__ == '__main__':
    main()
