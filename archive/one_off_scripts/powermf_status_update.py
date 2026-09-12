# -*- coding: utf-8 -*-
"""Cap nhat baselines/powermf_status.json sau khi DA chay that Power-MF.

Ban cu (2026-09-10) ghi hai dieu nay, ca hai NAY DA SAI:
  - "thieu 8 ham Varanini"      -> 8/8 ham co trong pmea-varanini.zip, da tai va chay
  - "kha_thi_chay_tai_cho": false -> da chay that tren Octave 11.3.0, 27/27 ban ghi

Script giu nguyen khoi `published_results_repo` (so trich tu Results/*.mat cua repo goc)
va them khoi `chay_lai_that`.
"""
import os
import sys
import json
import datetime
import subprocess

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'baselines')
ST = os.path.join(HERE, 'powermf_status.json')
PMF = os.path.join(HERE, 'powermf_results.json')

st = json.load(open(ST, encoding='utf-8'))
pm = json.load(open(PMF, encoding='utf-8'))
per = pm.get('per_record', {})

OCTAVE = os.path.join(ROOT, 'tools', 'octave', 'octave-11.3.0-w64',
                      'mingw64', 'bin', 'octave-cli.exe')
ver = ''
try:
    p = subprocess.run([OCTAVE, '--no-gui', '--quiet', '--eval', 'disp(version)'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    ver = (p.stdout or '').strip()
except Exception as e:
    ver = 'loi: %s' % e

GROUPS = {
    'adfecgdb_physionet_5': ['r01', 'r04', 'r07', 'r08', 'r10'],
    'silesia_b2_7_bo_trung': ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12'],
    'silesia_b2_12_ca_trung': ['B2_%02d' % i for i in range(1, 13)],
    'silesia_b1_10': ['B1_%02d' % i for i in range(1, 11)],
}


def summ(recs):
    got = [per[r] for r in recs if r in per]
    if not got:
        return dict(n=0, ghi_chu='chua chay')
    f1 = np.array([g['F1'] for g in got], float)
    return dict(n=len(got),
                n_that_bai=int(sum(1 for g in got if not g['ok'])),
                F1_mean=float(f1.mean()),
                F1_sd=float(f1.std(ddof=1)) if len(f1) > 1 else 0.0,
                F1_median=float(np.median(f1)), F1_min=float(f1.min()), F1_max=float(f1.max()),
                Se_mean=float(np.mean([g['Se'] for g in got])),
                PPV_mean=float(np.mean([g['PPV'] for g in got])),
                jitter_ms_mean=float(np.nanmean([g.get('jitter_ms', np.nan) for g in got])),
                per_record={g['rec']: dict(F1=round(g['F1'], 4), Se=round(g['Se'], 4),
                                           PPV=round(g['PPV'], 4), TP=g['TP'], FP=g['FP'],
                                           FN=g['FN'], n_ref=g['n_ref'], n_det=g['n_det'])
                            for g in got})


st['ngay_cap_nhat'] = datetime.datetime.now().isoformat(timespec='seconds')
st['runtime'] = {'matlab': None, 'octave': None,
                 'octave-cli': OCTAVE if os.path.isfile(OCTAVE) else None,
                 'octave_version': ver,
                 'ghi_chu': 'ban portable tu ftp.gnu.org, giai nen bang tar -xf vao tools/octave/, '
                            'khong can quyen admin, khong dung registry. tools/ nam trong .gitignore.'}
st['deps_present_files'] = {
    'CinC_Varanini (xCinC, pmea-varanini.zip)': len([f for f in os.listdir(
        os.path.join(ROOT, 'tools', 'varanini', 'xCinC'))
        if f.endswith('.m')]) if os.path.isdir(os.path.join(ROOT, 'tools', 'varanini', 'xCinC')) else 0,
    'CinC_Behar': 0, 'fecgsyn': 0, 'OSET-master': 0,
    'ghi_chu': 'CinC_Behar / fecgsyn / OSET chi can cho Behar14.m va Sulas21.m, '
               'KHONG nam tren duong di cua PowerMF.m',
}
st['kha_thi_chay_tai_cho'] = True
st['ly_do'] = [
    'DA CHAY THAT ngay %s: %d/%d ban ghi thanh cong tren GNU Octave %s.'
    % (st['ngay_cap_nhat'][:10], sum(1 for g in per.values() if g['ok']), len(per), ver),
    'Ban ghi cu "thieu 8 ham Varanini" la SAI: ca 8 ham nam trong pmea-varanini.zip '
    '(archive.physionet.org/challenge/2013/sources/pmea), zip co 30 file .m, chuoi phu thuoc khep kin, '
    'chi can goi signal cua Octave.',
    'Ban ghi cu "kha_thi_chay_tai_cho: false" la SAI: chi can 6 ban va nho (xem ban_va_octave).',
    'VAN DUNG: Power-MF la thuat toan DA KENH (4 dao trinh bung + ICA 2 lan). '
    'So sanh voi mo hinh don kenh cua nhom phai khai bao ro dieu nay.',
]
st['ban_va_octave'] = {
    'file': 'baselines/octave/apply_patches.py (ap vao ban sao baselines/octave/PowerMF.m, '
            'ban goc tools/fecg-benchmarking/Code/PowerMF.m khong bi sua)',
    'P1': 'pwelch: tham so overlap cua Octave la PHAN SO, khong phai so mau. Nfft/2 -> 0.5. '
          'Cung ngu nghia (50% chong lan), khong doi ket qua.',
    'P2a': 'findpeaks tu choi du lieu am: abs_dev -> dich s - min(s) truoc khi goi. '
           'Vi tri dinh khong doi. KHONG dung DoubleSided (no tra ve ca day lan dinh).',
    'P2b': 'nhu P2a nhung cho dau ra matched filter r.',
    'P3': 'disp voi phep "+" tren chuoi (lop string cua MATLAB) -> printf cua Octave.',
    'P4': 'Nfft mang kieu uint16 (do nsc=uint16) -> ep ve double.',
    'P6_BAN_VA_CHAN_DUNG': 'interpft cua Octave tra ve MANG PHUC (phan ao ~1e-16) ngay ca khi '
                           'dau vao thuc; MATLAB interpft ep ve thuc. Hau qua: Se phuc -> sig phuc '
                           '-> template phuc -> r phuc -> findpeaks tra ve 0 dinh -> PowerMF rong '
                           'tren MOI ban ghi. Ban va: Se = real(Se) ngay sau FecgInterp. '
                           'Day la loi lam PowerMF im lang tra ve rong truoc khi tim ra.',
}
st['giao_thuc_cham_diem'] = (
    'model/fqrs_model.py::match_events, dung sai +/-50 ms, ghep tham lam 1-1 -- '
    'BO CHAM CUA NHOM, khong dung Bxb_compare cua repo (can WFDB Toolbox). '
    'Muc dich: cung giao thuc voi moi so khac trong bai.')
st['chay_lai_that'] = {
    'ghi_chu': 'DAY la so ta tu do trong phien nay. Khac voi khoi published_results_repo ben duoi '
               '(so da cong bo, trich tu Results/*.mat).',
    'meta': pm.get('meta', {}),
    'tom_tat': {k: summ(v) for k, v in GROUPS.items()},
}

json.dump(st, open(ST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('cap nhat %s' % ST)
for k, v in st['chay_lai_that']['tom_tat'].items():
    if v.get('n'):
        print('  %-24s n=%2d  F1=%.2f +/- %.2f  (min %.2f, max %.2f)'
              % (k, v['n'], v['F1_mean'], v['F1_sd'], v['F1_min'], v['F1_max']))
