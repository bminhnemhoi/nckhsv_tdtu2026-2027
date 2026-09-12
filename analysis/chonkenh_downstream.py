# -*- coding: utf-8 -*-
"""
chonkenh_downstream.py -- HE QUA HAU KIEM (KHONG nam trong khai bao truoc).

Cau hoi: neu thay quy tac chon kenh PSD bang quy tac mu nhan tot hon, khoang cach giua
RelyFetal 1 kenh va Power-MF 4 kenh tren 22 chu the thay doi the nao?

Day la phan tich MO TA, HAU KIEM. Khong duoc coi la bang chung xac nhan.
Nguon so: analysis/chonkenh_results.json (F1 tung chu the theo tung quy tac)
          baselines/powermf_fair_stats.json (F1 Power-MF 4 kenh / 1 kenh tung chu the)

Chay: python analysis/chonkenh_downstream.py  -> ghi them khoa 'he_qua_hau_kiem' vao chonkenh_results.json
"""
import os, sys, json
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
from scipy.stats import wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
RES = os.path.join(HERE, 'chonkenh_results.json')
SEED = 0; NBOOT = 10000


def boot_ci(d, nboot=NBOOT, seed=SEED):
    d = np.asarray(d, float); rng = np.random.default_rng(seed)
    b = d[rng.integers(0, len(d), size=(nboot, len(d)))].mean(1)
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def cmp(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b
    try:
        p = float(wilcoxon(a, b, zero_method='wilcox').pvalue)
    except ValueError:
        p = 1.0
    return dict(mean_a=float(a.mean()), mean_b=float(b.mean()), hieu=float(d.mean()),
                ci95=boot_ci(d), p_wilcoxon=p,
                thang=int((d > 1e-9).sum()), thua=int((d < -1e-9).sum()),
                hoa=int((np.abs(d) <= 1e-9).sum()), n=int(len(d)))


def main():
    res = json.load(open(RES, encoding='utf-8'))
    F = res['F1_tung_ban_ghi']['s22']
    pmf = {r['rec']: r for r in json.load(open(os.path.join(ROOT, 'baselines', 'powermf_fair_stats.json'),
                                               encoding='utf-8'))['per_subject']}
    tags = sorted(set(F) & set(pmf))
    assert len(tags) == 22, 'can 22 chu the, dang co %d' % len(tags)
    # kiem chung: cot 'rely' cua powermf_fair_stats phai TRUNG voi quy tac PSD cua ta
    mx = max(abs(pmf[t]['rely'] - F[t]['psd']) for t in tags)
    assert mx < 1e-6, 'cot rely khong khop quy tac PSD: lech %.3g' % mx
    print('kiem chung: F1 quy tac PSD trung voi cot "rely" cua powermf_fair_stats.json (lech toi da %.1e)' % mx)

    p4 = [pmf[t]['pmf4'] for t in tags]
    p1 = [pmf[t]['pmf1'] for t in tags]
    out = {}
    for rule in ['psd', 'gate', 'gate4', 'rrcv', 'peakprob', 'rrplaus', 'fuse', 'learned', 'oracle']:
        v = [F[t][rule] for t in tags]
        out[rule] = dict(vs_powermf4=cmp(v, p4), vs_powermf1=cmp(v, p1))
        c = out[rule]['vs_powermf4']
        print('%-9s RelyFetal %6.2f vs Power-MF 4 kenh %6.2f : hieu %+6.2f KTC95 [%+6.2f;%+6.2f] '
              'p=%.3f  thang %2d thua %2d'
              % (rule, c['mean_a'], c['mean_b'], c['hieu'], c['ci95'][0], c['ci95'][1],
                 c['p_wilcoxon'], c['thang'], c['thua']))
    res['he_qua_hau_kiem'] = dict(
        mo_ta='HAU KIEM, KHONG nam trong khai bao truoc. So sanh RelyFetal 1 kenh (moi quy tac chon kenh) '
              'voi Power-MF 4 kenh va 1 kenh tren cung 22 chu the, don vi = chu the, '
              'KTC95 cluster bootstrap 10000 lan seed 0, Wilcoxon ghep cap.',
        canh_bao='Quy tac chon kenh duoc so sanh o day da duoc thu tren chinh 22 chu the nay; '
                 'con so khong phai bang chung ngoai mien. Chi de xac dinh huong cho vong sau.',
        nguon=['analysis/chonkenh_results.json', 'baselines/powermf_fair_stats.json'],
        kiem_chung_rely_khop_psd=float(mx),
        bang=out)
    json.dump(res, open(RES, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    print('-> ghi them khoa he_qua_hau_kiem vao', RES)


if __name__ == '__main__':
    main()
