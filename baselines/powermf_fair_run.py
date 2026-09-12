# -*- coding: utf-8 -*-
"""A2 PHAN 1d -- chay lai TOAN BO 22 chu the (+5 ban trung) voi PowerMF.m DA VA P7.

P7 = thay findpeaks(...,'MinPeakDistance',d) cua Octave bang findpeaks_mpd.m.
Ly do: cai dat MinPeakDistance cua Octave dung ma tran khoang cach doi mot giua cac
ung vien dinh -> O(k^2) bo nho -> "out of memory or dimension too large for Octave's
index type" tren ban ghi Silesia B1 dai (2 395 600 mau sau noi suy x4).
Do la GIOI HAN CUA BAN CHUYEN OCTAVE, khong phai tinh chat cua Power-MF:
MATLAB (nen tang cua tac gia) xu ly rang buoc nay bang thuat toan tham O(k log k).

Chay lai CA nhung ban ghi truoc day da thanh cong de toan bo cot Power-MF dung
CUNG mot ban ma -> so sanh noi bo nhat quan.

Xuat: baselines/powermf_fair.json  (log: baselines/powermf_fair_log.txt)
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'baselines'))

import powermf_run as R  # noqa: E402

R.OUT = os.path.join(ROOT, 'baselines', 'powermf_fair.json')
R.LOG = os.path.join(ROOT, 'baselines', 'powermf_fair_log.txt')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv += ['--sets', 'b1', 'adfecgdb', 'b2', '--workers', '2']
    R.main()
