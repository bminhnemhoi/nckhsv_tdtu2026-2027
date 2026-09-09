# -*- coding: utf-8 -*-
"""
Cap nhat cac con so cu cua chinh nhom nam rai rac trong ban khao sat 30 paper.

Ly do: khi cac agent doc paper, ho duoc cung cap con so 77,52 +/- 26,83 va 12,43 diem.
Sau do nhom phat hien:
  - 77,52 la ket qua CHON KENH BANG NHAN THAT (oracle), khong bao cao duoc.
    Con so trung thuc, mu nhan, dung kenh co dinh la 77,34 +/- 28,54.
  - 12,43 tron hai thi nghiem khac giao thuc. Con so co kiem soat noi bo la 11,00.
Script nay sua lai cho nhat quan voi facts_verified.json.
"""
import os, sys, json, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'survey', 'survey_raw.json')
S = json.load(open(P, encoding='utf-8'))

FIELDS = ['ho_lam_gi', 'phuong_phap', 'mo_hinh', 'du_lieu', 'giao_thuc_danh_gia',
          'ket_qua_chinh', 'diem_yeu', 'so_voi_chung_ta', 'bai_hoc_ap_dung']

RULES = [
    (r'77,52\s*±\s*26,83\s*%', '77,34 ± 28,54 %'),
    (r'77,52\s*±\s*26,83', '77,34 ± 28,54'),
    (r'77,52\s*%', '77,34 %'),
    (r'\b77,52\b', '77,34'),
    (r'\(26,83\)', '(28,54)'),
    (r'\b26,83\b', '28,54'),
    (r'12,43\s*điểm', '11,00 điểm'),
    (r'\b12,43\b', '11,00'),
    (r'gấp (khoảng )?30 lần', 'lớn hơn nhiều lần'),
]

n = 0
for p in S['papers']:
    for f in FIELDS:
        t0 = p[f]
        t = t0
        for a, b in RULES:
            t = re.sub(a, b, t)
        if t != t0:
            n += t0 != t
            p[f] = t

json.dump(S, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'da sua {n} truong trong survey_raw.json')

# kiem tra lai
left = 0
for p in S['papers']:
    for f in FIELDS:
        left += len(re.findall(r'77,52|12,43|26,83|gấp 30 lần', p[f]))
print('con sot:', left)
