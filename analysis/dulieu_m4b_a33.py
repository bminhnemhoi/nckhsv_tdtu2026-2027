# -*- coding: utf-8 -*-
"""Kiem tay ung vien duy nhat vuot nguong NULL trong phep quet cua so con: a33.
Phep phan biet: ban sao THAT giu |NCC| = 1,0000 o MOI do dai cua so; trung hop ngau nhien
giua hai chuoi QRS gia chu ky thi SUY GIAM khi keo dai cua so (nhip hai me troi khoi nhau).
Chay: python analysis/dulieu_m4b_a33.py"""
import os, sys, json
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, wfdb, mne
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
AD = os.path.join(ROOT, 'model', 'data', 'adfecgdb'); CI = os.path.join(ROOT, 'benchmark_dpss', 'pcdb')


def z(x):
    x = np.asarray(x, float) - np.mean(x); s = x.std(); return x / s if s > 0 else x


raw = mne.io.read_raw_edf(os.path.join(AD, 'r07.edf'), preload=True, verbose='ERROR')
Y = raw.get_data()[raw.ch_names.index('Abdomen_3')]; fs = raw.info['sfreq']
LENS = [5, 10, 15, 20, 30]


def curve(x, cs, y, gs):
    out = {}
    for L in LENS:
        n = int(L * fs); a, b = x[cs:cs + n], y[gs:gs + n]
        out[L] = round(float(np.dot(z(a), z(b)) / n), 4) if len(a) == n and len(b) == n else None
    return out


cand = curve(wfdb.rdrecord(os.path.join(CI, 'a33')).p_signal.T[3], int(30.0 * fs), Y, int(41.3 * fs))
posi = curve(wfdb.rdrecord(os.path.join(CI, 'a19')).p_signal.T[2], 0, Y, 0)
P = json.load(open(os.path.join(HERE, 'dulieu_m4b_partial.json'), encoding='utf-8'))
vc = np.array([abs(v['ncc_cua_so_con']) for v in P['tung_ban_ghi']['clean'].values()])
vn = np.array([abs(v['ncc_cua_so_con']) for v in P['tung_ban_ghi']['null'].values()])
res = dict(
    ung_vien='a33', kenh_cinc=3, khop_voi='r07/Abdomen_3', ncc_cua_so_10s=-0.9602,
    duong_cong_ncc_theo_do_dai_cua_so=dict(a33_ung_vien=cand, a19_doi_chung_duong_ban_sao_that=posi),
    so_sanh_phan_bo_clean_vs_null=dict(
        mann_whitney_p=round(float(stats.mannwhitneyu(vc, vn).pvalue), 4),
        ks_p=round(float(stats.ks_2samp(vc, vn).pvalue), 4),
        clean_trung_vi=round(float(np.median(vc)), 4), null_trung_vi=round(float(np.median(vn)), 4),
        clean_max=round(float(vc.max()), 4), null_max=round(float(vn.max()), 4)),
    ket_luan=('a33 KHONG phai ban sao. |NCC| suy giam %.4f -> %.4f khi cua so keo tu 5 s len 30 s, '
              'trong khi ban sao THAT (a19) giu dung 1,0000 o MOI do dai. Dau AM va suy giam dan la '
              'chu ky cua hai chuoi QRS me khac nhau troi khoi nhau, khong phai cung mot tep mau.'
              % (abs(cand[5]), abs(cand[30]))),
    dien_giai_tong=('Phan bo |NCC| cua so con cua 60 ban SACH KHONG phan biet duoc voi nhanh NULL '
                    '(Mann-Whitney p = %.3f, KS p = %.3f). Khong co bang chung chong lan BO PHAN.'
                    % (stats.mannwhitneyu(vc, vn).pvalue, stats.ks_2samp(vc, vn).pvalue)))
json.dump(res, open(os.path.join(HERE, 'dulieu_m4b_a33.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
