# -*- coding: utf-8 -*-
"""
Kiem tra kha nang chay Power-MF (Jaeger et al. 2024, https://github.com/mad-lab-fau/fecg-benchmarking)
tren may nay va, neu KHONG chay duoc, trich cac con so DA CONG BO trong repo (Results/*.mat)
de lam tham chieu -- ghi ro day KHONG phai ket qua tu chay.

Power-MF la thuat toan DA KENH (4 kenh bung, ICA cua Varanini 2014 + chon kenh PSD + matched filter),
khong cung cau hinh voi bai toan don kenh cua nhom.

Chay:  PYTHONIOENCODING=utf-8 python baselines/powermf_check.py
Ghi:   baselines/powermf_status.json
"""
import os, sys, json, shutil, subprocess, tempfile, datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = 'https://github.com/mad-lab-fau/fecg-benchmarking'
OUT = os.path.join(HERE, 'powermf_status.json')


def which_any(names):
    return {n: shutil.which(n) for n in names}


def main():
    status = dict(ngay=datetime.datetime.now().isoformat(timespec='seconds'), repo=REPO)
    # 1. runtime MATLAB / Octave?
    rt = which_any(['matlab', 'octave', 'octave-cli'])
    status['runtime'] = rt
    print('runtime MATLAB/Octave tren PATH:', rt)
    # 2. clone repo vao thu muc tam
    tmp = tempfile.mkdtemp(prefix='fecgbench_')
    try:
        subprocess.run(['git', 'clone', '--depth', '1', REPO, os.path.join(tmp, 'fb')],
                       check=True, capture_output=True, timeout=600)
        status['clone'] = 'ok'
    except Exception as e:
        status['clone'] = 'that bai: %s' % e
        print(status['clone']); json.dump(status, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False); return
    fb = os.path.join(tmp, 'fb')
    code = os.listdir(os.path.join(fb, 'Code'))
    status['code_files'] = sorted(code)
    # 3. phu thuoc ngoai bat buoc (theo README va benchmark_algorithms.m)
    deps = {}
    for d in ['CinC_Behar', 'CinC_Varanini', 'fecgsyn', 'OSET-master']:
        p = os.path.join(fb, 'Code', 'subfunctions', d)
        deps[d] = len([f for f in os.listdir(p) if f != 'README.md']) if os.path.isdir(p) else -1
    status['deps_present_files'] = deps
    # PowerMF.m goi cac ham cua Varanini (khong co trong repo)
    src = open(os.path.join(fb, 'Code', 'PowerMF.m'), encoding='utf-8', errors='replace').read()
    ext_calls = [f for f in ['FecgImpArtCanc', 'FecgDetrFilt', 'FecgNotchFilt', 'FecgICAm', 'FecgInterp',
                             'FecgQRSmDet', 'FecgQRSmCanc', 'FecgICAf', 'pwelch', 'findpeaks', 'gausswin', 'filtfilt']
                 if f in src]
    status['powermf_external_calls'] = ext_calls
    kha_thi = all(v is not None for v in rt.values()) and all(v > 0 for v in deps.values())
    status['kha_thi_chay_tai_cho'] = bool(kha_thi)
    status['ly_do'] = [] if kha_thi else [
        'khong co MATLAB/Octave tren may (ma nguon la MATLAB R2021a)',
        'PowerMF.m goi 8 ham tien xu ly/ICA/khu me cua Varanini 2014 (archive.physionet.org/challenge/2013/sources) khong nam trong repo',
        'thieu cac goi OSET, fecgsyn, CinC_Behar, CinC_Varanini (thu muc subfunctions chi co README)',
        'Power-MF la thuat toan DA KENH (ICA 4 kenh) -- khong cung cau hinh don kenh',
    ]
    # 4. trich con so DA CONG BO (Results/b1_powermf.mat: ADFECG B1 Pregnancy, 10 ban ghi figshare)
    try:
        import scipy.io as sio
        pub = {}
        for tag in ['b1_powermf', 'b1_behar', 'b1_varanini', 'b1_sulas']:
            m = sio.loadmat(os.path.join(fb, 'Results', tag + '.mat'), squeeze_me=True, struct_as_record=False)['score']
            rows = [dict(F1=float(s.F1), Se=float(s.SE), PPV=float(s.PPV), TP=int(s.TP), FN=int(s.FN), FP=int(s.FP))
                    for s in np.atleast_1d(m)]
            f1 = np.array([r['F1'] for r in rows])
            pub[tag] = dict(n_records=len(rows), F1_mean=float(f1.mean()), F1_sd=float(f1.std(ddof=1)),
                            F1_median=float(np.median(f1)), per_record=rows)
        status['published_results_repo'] = dict(
            ghi_chu=('Con so DA CONG BO lay tu Results/*.mat cua repo, KHONG phai tu chay. '
                     'Bo du lieu: ADFECG B1 Pregnancy (figshare, 10 ban ghi, DA KENH 4 kenh bung, dung sai 50 ms), '
                     'khac voi ADFECGDB PhysioNet 5 ban ghi ma nhom dung; thu tu ban ghi trong .mat = thu tu dir(*.mat), '
                     'khong co ten ban ghi nen KHONG ghep duoc voi r01..r10. Chi dung de tham chieu quy mo.'),
            **pub)
        for tag, v in pub.items():
            print('%-12s n=%d  F1 = %.4f +/- %.4f (median %.4f)' % (tag, v['n_records'], v['F1_mean'], v['F1_sd'], v['F1_median']))
    except Exception as e:
        status['published_results_repo'] = 'khong doc duoc: %s' % e
    shutil.rmtree(tmp, ignore_errors=True)
    json.dump(status, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('kha thi chay tai cho:', status['kha_thi_chay_tai_cho'])
    for r in status['ly_do']:
        print('  -', r)
    print('da ghi', OUT)


if __name__ == '__main__':
    main()
