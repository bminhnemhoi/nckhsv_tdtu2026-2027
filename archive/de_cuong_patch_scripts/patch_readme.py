# -*- coding: utf-8 -*-
"""Cập nhật docs/README_KET_QUA.md cho bản 3.4."""
import io, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'docs', 'README_KET_QUA.md')
t = io.open(p, encoding='utf-8').read()
n = 0

cap = [
 ('Cập nhật 12/09/2026, phiên bản **3.3**.',
  'Cập nhật 12/09/2026 (chiều), phiên bản **3.4**.'),

 ('| **`De_cuong_NCKH_RelyFetal.pdf`** | **Đề cương chính thức v3.3** (130 trang) |',
  '| **`De_cuong_NCKH_RelyFetal.pdf`** | **Đề cương chính thức v3.4** (138 trang) |'),

 ('## v3.3 rút lại bốn phát biểu của v3.2',
  """## v3.4 — đề cương đã mang số Power-MF đúng

Bản 3.3 của đề cương (sáng 12/09) dùng số Power-MF từ một bản Octave còn hỏng. **Bản 3.4 (chiều 12/09)
đã viết lại toàn bộ mục 5.7** bằng số sau bản vá P7, thêm cột **Power-MF đơn kênh**, và thêm một mục mới
**§8.3 "Nhóm đã đoán sai nguyên nhân hai lần trong một ngày"**. Chi tiết:

- Mục 5.7 mở đầu bằng một **hộp rút lại** ghi rõ 94,87 / 98,38 / 97,33 đều sai và vì sao.
- Bảng 3 cột đầy đủ 22 chủ thể (PMF 4 kênh / PMF 1 kênh / RelyFetal) + bảng F1 từng chủ thể.
- Bảng thống kê mức chủ thể đầy đủ: 3 phép so sánh × 4 tập con = 12 dòng.
- Hộp **kiểm chứng ngoài**: 99,40 chạy lại so với 99,46 tác giả công bố, lệch 0,06 điểm.
- Mục **ba bản ghi kéo tụt trung bình** (B1_07 / B1_06 / B2_03), kèm trung vị +0,23 và thắng 18/22.
- Mục **luận đề 89,5 %** — cách định vị đúng của cả đề tài.
- Hình 17 đổi từ 2 cột sang **3 cột**.

Toàn bộ 82 con số Power-MF trong PDF đã được đối chiếu tự động với `baselines/powermf_fair_stats.json`
bằng `de_cuong_latex/verify_v34.py` — **82/82 khớp**.

## v3.3 rút lại bốn phát biểu của v3.2"""),
]

for old, new in cap:
    if old not in t:
        print('  !! KHONG THAY:', old[:60]); continue
    t = t.replace(old, new, 1); n += 1

io.open(p, 'w', encoding='utf-8').write(t)
print('README_KET_QUA.md: %d cho' % n)
