# -*- coding: utf-8 -*-
"""
Sinh lại hai tệp ví dụ cho tab "Tải dữ liệu mới":
    demo/assets/vidu_tai_len.csv        30 s đầu của a09, 4 cột = 4 kênh, 1000 Hz
    demo/assets/vidu_tai_len_nhan.csv   nhãn nhịp thai, một cột chỉ số mẫu ở 1000 Hz

a09 thuộc CinC 2013 set-a (bản SẠCH) -- tệp ví dụ KHÔNG phải "dữ liệu mới" thật, chỉ để thử luồng tải lên.
Hai tệp này KHÔNG được commit: .gitignore loại chúng ra vì kho này cố ý không phát tán lại bản ghi
sinh lý gốc (xem đầu .gitignore). Máy nào thiếu thì chạy:  python demo/make_vidu_tai_len.py
"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
import wfdb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import core                                      # noqa: E402  -- chỉ để lấy đúng thư mục pcdb
SRC = os.path.join(core.cinc2013_dir(), 'a09')
OUT = os.path.join(HERE, 'assets')
os.makedirs(OUT, exist_ok=True)

DUR_S = 30.0
r = wfdb.rdrecord(SRC)
fs = float(r.fs)
n = int(round(DUR_S * fs))
sig = np.nan_to_num(r.p_signal)[:n]          # (n, 4) mV
ann = np.asarray(wfdb.rdann(SRC, 'fqrs').sample, int)
lab = ann[(ann >= 0) & (ann < n)]

p_sig = os.path.join(OUT, 'vidu_tai_len.csv')
with open(p_sig, 'w', encoding='utf-8', newline='\n') as f:
    f.write('AECG1,AECG2,AECG3,AECG4\n')
    for row in sig:
        f.write(','.join(f'{v:.5f}' for v in row) + '\n')

p_lab = os.path.join(OUT, 'vidu_tai_len_nhan.csv')
with open(p_lab, 'w', encoding='utf-8', newline='\n') as f:
    for v in lab:
        f.write(f'{int(v)}\n')

meta = dict(nguon='benchmark_dpss/pcdb/a09 (CinC 2013 set-a, bản SẠCH)',
            fs_Hz=fs, do_dai_s=DUR_S, n_mau=int(n), n_kenh=int(sig.shape[1]),
            n_nhip_trong_30s=int(len(lab)), don_vi_tin_hieu=str(r.units[0]),
            don_vi_nhan='chỉ số mẫu ở %g Hz' % fs,
            canh_bao='KHÔNG phải dữ liệu mới thật — trích từ a09 để thử luồng tải lên.')
with open(os.path.join(OUT, 'vidu_tai_len_META.json'), 'w', encoding='utf-8') as f:
    json.dump(meta, f, indent=1, ensure_ascii=False)
print(json.dumps(meta, ensure_ascii=False, indent=1))
for p in (p_sig, p_lab):
    print(p, os.path.getsize(p) / 1e6, 'MB')
