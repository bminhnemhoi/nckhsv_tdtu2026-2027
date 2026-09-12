# -*- coding: utf-8 -*-
"""
Tính lại CinC 2013 set-a trên 60 BẢN GHI SẠCH (loại 15 bản là bản sao nguyên văn của ADFECGDB,
xem analysis/DULIEU.md) từ benchmark_dpss/eval_cinc75.json. Không chạy lại mô hình: chỉ lọc bản ghi
và tính lại thống kê theo cùng công thức (bootstrap 10.000 lần, seed 0; Wilcoxon ghép cặp hai phía).

Chạy:  python benchmark_dpss/eval_cinc60_sach.py  ->  benchmark_dpss/eval_cinc60_sach.json
Đây là NGUỒN cho mọi con số CinC "60 bản sạch" của mô hình m5 / m22 với 4 quy tắc psd / lead0 / mean4 / oracle.
Số peakprob và 6 quy tắc M5 khác nằm ở analysis/dulieu_results.json (chon_kenh_60_sach).
"""
import json, os, datetime
import numpy as np
from scipy.stats import wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'eval_cinc75.json')
OUT = os.path.join(HERE, 'eval_cinc60_sach.json')
LEAK = {'a04': 'r01', 'a05': 'r01', 'a22': 'r01', 'a13': 'r04', 'a20': 'r04', 'a25': 'r04',
        'a19': 'r07', 'a23': 'r07', 'a24': 'r07', 'a08': 'r08', 'a15': 'r08', 'a17': 'r08',
        'a03': 'r10', 'a12': 'r10', 'a14': 'r10'}
BAD_ANN = ['a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74']
RULES = {'psd': 'F1_psd', 'lead0': 'F1_lead0', 'mean4': 'F1_mean4', 'oracle': 'F1_oracle'}
N_BOOT, SEED = 10000, 0


def boot_ci(d, n_boot=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    d = np.asarray(d, float)
    idx = rng.integers(0, len(d), size=(n_boot, len(d)))
    m = d[idx].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def summarise(vals):
    v = np.asarray(vals, float)
    return dict(n=int(len(v)), mean=float(v.mean()), sd=float(v.std(ddof=1)), median=float(np.median(v)),
                ge90=int((v >= 90).sum()), lt50=int((v < 50).sum()), eq100=int((v >= 100 - 1e-9).sum()),
                ci95_bootstrap=boot_ci(v))


def paired(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a - b
    nz = d[d != 0]
    p = float(wilcoxon(a, b).pvalue) if len(nz) else 1.0
    return dict(n=int(len(d)), mean_diff=float(d.mean()), median_diff=float(np.median(d)),
                ci95_bootstrap=boot_ci(d), wilcoxon_p=p,
                wins=int((d > 0).sum()), losses=int((d < 0).sum()), ties=int((d == 0).sum()))


def main():
    with open(SRC, encoding='utf-8') as f:
        src = json.load(f)
    recs = {r['record']: r for r in src['records']}
    out = dict(meta=dict(date=str(datetime.datetime.now()), source='benchmark_dpss/eval_cinc75.json',
                         leak_source='analysis/DULIEU.md, analysis/dulieu_results.json (chong_lan)',
                         leak_records=LEAK, bad_annotation=BAD_ANN, n_boot=N_BOOT, seed=SEED,
                         note='Cùng từng bản ghi F1 như eval_cinc75.json; chỉ lọc và tính lại thống kê. '
                              'Quy tắc lead0 là chọn HẬU KIỂM (đã rút), giữ để đối chiếu.'),
               variants={})
    for name, keep in [('60_sach', [r for r in recs if r not in LEAK]),
                       ('53_sach_loai_7_nhan_sai', [r for r in recs if r not in LEAK and r not in BAD_ANN]),
                       ('75_o_nhiem', list(recs)),
                       ('15_ro_ri', [r for r in recs if r in LEAK])]:
        v = dict(n=len(keep), records=sorted(keep), rules={})
        for rule, key in RULES.items():
            m5 = [recs[r]['m5'][key] for r in keep]
            m22 = [recs[r]['m22'][key] for r in keep]
            v['rules'][rule] = dict(m5=summarise(m5), m22=summarise(m22), m22_minus_m5=paired(m22, m5))
        v['psd_vs_oracle_m22'] = paired([recs[r]['m22']['F1_oracle'] for r in keep],
                                        [recs[r]['m22']['F1_psd'] for r in keep])
        v['psd_picks_oracle_lead_m22'] = int(sum(recs[r]['m22']['psd_lead'] == recs[r]['m22']['oracle_lead'] for r in keep))
        out['variants'][name] = v
    # Power-MF đơn kênh (baselines/powermf_1ch.json, mục cinc75) trên cùng các tập con
    p1 = os.path.join(HERE, '..', 'baselines', 'powermf_1ch.json')
    if os.path.isfile(p1):
        with open(p1, encoding='utf-8') as f:
            pmf = json.load(f)['cinc75']
        out['powermf_1ch'] = {}
        for name, v in out['variants'].items():
            keep = [r for r in v['records'] if r in pmf]
            f1 = [pmf[r]['F1_psd'] for r in keep]
            rely = [recs[r]['m22']['F1_psd'] for r in keep]
            out['powermf_1ch'][name] = dict(n=len(keep), F1_psd=summarise(f1),
                                            rely_m22_psd_minus_pmf1=paired(rely, f1))
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    for name, v in out['variants'].items():
        print(f"== {name} (n={v['n']})")
        for rule, s in v['rules'].items():
            d = s['m22_minus_m5']
            print(f"  {rule:7s} m5 {s['m5']['mean']:6.2f}  m22 {s['m22']['mean']:6.2f}  "
                  f"d {d['mean_diff']:+6.2f} [{d['ci95_bootstrap'][0]:+.2f};{d['ci95_bootstrap'][1]:+.2f}] "
                  f"p {d['wilcoxon_p']:.1e} W/L/T {d['wins']}/{d['losses']}/{d['ties']}  "
                  f"m22 ge90 {s['m22']['ge90']} lt50 {s['m22']['lt50']} med {s['m22']['median']:.2f} ci [{s['m22']['ci95_bootstrap'][0]:.1f};{s['m22']['ci95_bootstrap'][1]:.1f}]")
        po = v['psd_vs_oracle_m22']
        print(f"  oracle-psd m22 {po['mean_diff']:+.2f} [{po['ci95_bootstrap'][0]:+.2f};{po['ci95_bootstrap'][1]:+.2f}]  psd==oracle lead: {v['psd_picks_oracle_lead_m22']}/{v['n']}")
    for name, v in out.get('powermf_1ch', {}).items():
        d = v['rely_m22_psd_minus_pmf1']
        print(f"  Power-MF 1ch {name}: F1 {v['F1_psd']['mean']:.2f} (n={v['n']}); RelyFetal(psd) - PMF1 {d['mean_diff']:+.2f} [{d['ci95_bootstrap'][0]:+.2f};{d['ci95_bootstrap'][1]:+.2f}] p {d['wilcoxon_p']:.1e}")
    print('->', OUT)


if __name__ == '__main__':
    main()
