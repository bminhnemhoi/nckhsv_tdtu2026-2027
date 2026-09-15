> **⚠ CẢNH BÁO (12/09/2026, sau vòng 7).** Tài liệu này được viết khi CinC 2013 set-a còn được tính trên **75 bản ghi**. Sau đó xác định 15 bản (a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25) là bản sao nguyên văn của dữ liệu huấn luyện ADFECGDB — điều ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014] và nhóm đã bỏ sót. **Mọi con số CinC dưới đây (79,40 / 85,60 / 86,87 / 71,21 / 62,82, AUROC 0,980…) bị thổi 3–7 điểm và đã bị rút.** Số chính thức trên **60 bản sạch**: PSD 74,28 · peakprob 82,01 · oracle 83,60 (`analysis/dulieu_results.json`, `benchmark_dpss/eval_cinc60_sach.json`). Kết luận định tính trong tài liệu giữ nguyên trừ khi ghi khác trong `docs/nhat_ky/THAMDINH_VONG7.md`. Cụm "tiền đăng ký" trong tài liệu này **không đúng** — tệp khai báo không neo git.

> **Cảnh báo (vòng 7, 12/09/2026).** Tệp này được viết khi CinC 2013 còn tính trên **75 bản ghi**; 15 bản
> trong đó là bản sao ADFECGDB (điều ban tổ chức đã ghi nhận từ 2013 — `survey/RO_RI_VANLIEU.md`). Mọi con
> số CinC-75 ở đây (79,40 / 85,60 / 86,87 / +6,20 / +8,18 / +7,47 …) **đã rút**; số hiện hành trên 60 bản
> sạch: psd 74,28 · gate 80,72 · gate4 81,01 · rrcv 80,00 · peakprob 82,01 · oracle 83,60
> (`analysis/dulieu_results.json → chon_kenh_60_sach`, `benchmark_dpss/eval_cinc60_sach.json`). Số gốc giữ
> nguyên để truy vết; kết luận định tính đọc kèm `analysis/XACNHAN.md`.

# Ablation bỏ B1 — cải thiện 5 → 22 chủ thể là do THÊM DỮ LIỆU hay do HỌC PHONG CÁCH NHÃN?

*Sinh ngày 2026-09-12 08:20 bởi `analysis/ablation_b1.py`. Nguồn số: `model/train_12.json`, `benchmark_dpss/eval_12.json`, `benchmark_dpss/eval_22.json`, `benchmark_dpss/eval_cinc75.json`. Bootstrap cụm 10000 lần ở mức CHỦ THỂ, seed 0.*

## 0. Thiết kế và ba mô hình được so sánh

| Mô hình | Huấn luyện trên | Loại nhãn | Đã từng thấy B1? | Checkpoint |
|---|---|---|---|---|
| **m5** | 5 sản phụ ADFECGDB | điện cực da đầu (trực tiếp) | Không | `fetalqrs_tcn_production.pt` |
| **m12** | 12 sản phụ (5 PhysioNet + 7 B2) | điện cực da đầu (trực tiếp) | **Không — đây là biến ablation** | `fetalqrs_tcn_12_production.pt` |
| **m22** | 22 sản phụ (5 + 7 + **10 B1**) | 12 trực tiếp + 10 **gián tiếp** | Có (fold giữ lại chính chủ thể đang đo) | `fetalqrs_tcn_22_fold_XX.pt` |

Nhãn B1 là nhãn **gián tiếp**: tác giả Silesia khử ECG mẹ trên tín hiệu bụng rồi dò QRS thai và duyệt lại — không có điện cực da đầu. B1 chiếm 77 % tổng thời lượng huấn luyện (199,6/259,6 phút) của m22, nên nếu m22 hơn m5 chỉ vì nó *bắt chước phong cách chấm nhãn của B1* thì con số 97,15 trên B1 là thiên lệch do sáp nhập dữ liệu (incorporation bias), không phải năng lực thật.

**Quy tắc quyết định khai báo trước:** nếu m12 (ít dữ liệu hơn, chưa từng thấy B1) vẫn ngang m22 trên B1 thì phong cách nhãn KHÔNG phải nguyên nhân. Nếu m12 ≈ m5 ≪ m22 trên B1 nhưng m12 ≈ m22 trên CinC thì phần lớn lợi ích trên B1 là do học phong cách nhãn.

## 1. (a) 10 chủ thể B1 — tập mà m12 CHƯA TỪNG THẤY

F1 trên kênh chọn theo quy tắc PSD mù nhãn (%), dung sai ±50 ms.

| Chủ thể | m5 | **m12** | m22 | m12 − m5 | m12 − m22 |
|---|---:|---:|---:|---:|---:|
| B1_01 | 97,70 | **99,65** | 99,97 | +1,95 | -0,32 |
| B1_02 | 99,59 | **99,70** | 99,79 | +0,11 | -0,09 |
| B1_03 | 99,86 | **99,88** | 99,92 | +0,02 | -0,04 |
| B1_04 | 99,80 | **99,98** | 100,00 | +0,18 | -0,02 |
| B1_05 | 99,78 | **99,77** | 99,87 | -0,02 | -0,11 |
| B1_06 | 80,90 | **82,09** | 89,45 | +1,20 | -7,36 |
| B1_07 | 58,72 | **67,21** | 86,56 | +8,49 | -19,35 |
| B1_08 | 99,52 | **99,74** | 99,83 | +0,22 | -0,09 |
| B1_09 | 99,04 | **98,86** | 99,07 | -0,17 | -0,21 |
| B1_10 | 98,12 | **96,86** | 97,05 | -1,25 | -0,19 |
| **Trung bình (PSD)** | **93,30** | **94,37** | **97,15** | +1,07 | -2,78 |
| Độ lệch chuẩn | 13,46 | 11,01 | 4,95 | | |
| **Trung bình 4 kênh** | 91,31 | **93,44** | 97,01 | +2,13 | -3,57 |

**Thống kê ghép cặp ở mức chủ thể (n = 10):**

| So sánh | Hiệu số TB | KTC 95 % bootstrap | KTC 95 % t | p Wilcoxon | p sign test | thắng/thua | Cliff δ |
|---|---:|---|---|---:|---:|---:|---|
| B1 kênh PSD: m12 − m5 | +1,07 | [-0,12; +2,90] | [-0,89; +3,03] | 0,1602 | 0,3438 | 7/3 | +0,140 (khong dang ke) |
| B1 kênh PSD: m12 − m22 | -2,78 | [-6,66; -0,11] | [-7,25; +1,69] | 0,0020 | 0,0020 | 0/10 | -0,260 (nho) |
| B1 kênh PSD: m22 − m5 (mốc cũ) | +3,85 | [+0,05; +9,62] | [-2,49; +10,19] | 0,0371 | 0,0215 | 9/1 | +0,360 (trung binh) |
| B1 TB 4 kênh: m12 − m5 | +2,13 | [+0,72; +3,94] | [+0,16; +4,10] | 0,0020 | 0,0020 | 10/0 | +0,200 (nho) |
| B1 TB 4 kênh: m12 − m22 | -3,57 | [-6,31; -1,34] | [-6,59; -0,55] | 0,0059 | 0,0215 | 1/9 | -0,420 (trung binh) |

**Quét ngưỡng (m12 trên B1, trung bình 10 chủ thể)** — kiểm tra kết luận có phụ thuộc ngưỡng không:

| Ngưỡng | 0,45 | 0,55 | 0,65 | 0,75 | 0,80 |
|---|---:|---:|---:|---:|---:|
| F1 kênh PSD | 94,68 | 94,66 | 94,65 | 94,52 | 94,37 |
| F1 TB 4 kênh | 93,81 | 93,81 | 93,77 | 93,61 | 93,44 |

## 2. (b) CinC 2013 set-a — 75 bản ghi, zero-shot ngoài miền

Con số chính là **quy tắc PSD mù nhãn**. Kênh 0 cố định là quy tắc chọn HẬU KIỂM, chỉ để tham chiếu.

### toàn bộ 75 bản ghi (n = 75)

| Quy tắc chọn kênh | m5 | **m12** | m22 | m12 − m5 [KTC 95 %] | p | m12 − m22 [KTC 95 %] | p |
|---|---:|---:|---:|---|---:|---|---:|
| **PSD mù nhãn (SỐ CHÍNH)** | 71,21 | **74,34** | 79,40 | +3,13 [+1,49; +4,98] | 0,0011 | -5,06 [-7,23; -3,19] | 3,76e-08 |
| kênh 0 cố định (hậu kiểm) | 58,72 | **62,56** | 69,33 | +3,84 [+1,94; +5,95] | 0,0001 | -6,77 [-9,40; -4,33] | 8,18e-07 |
| TB 4 kênh | 64,78 | **67,79** | 74,09 | +3,01 [+1,67; +4,57] | 6,20e-07 | -6,30 [-8,25; -4,52] | 9,57e-10 |
| oracle (chặn trên) | 78,21 | **80,43** | 86,87 | +2,22 [+0,78; +3,80] | 0,0014 | -6,44 [-9,25; -3,88] | 1,18e-07 |

Phân bố theo quy tắc PSD (toàn bộ 75 bản ghi): ≥ 90 điểm — m5 42, **m12 45**, m22 48; < 50 điểm — m5 22, **m12 21**, m22 16.

| Ngưỡng | 0,45 | 0,55 | 0,65 | 0,75 | 0,80 |
|---|---:|---:|---:|---:|---:|
| m12 F1 kênh PSD | 75,48 | 75,29 | 75,07 | 74,75 | 74,34 |
| m12 F1 kênh 0 | 64,04 | 63,78 | 63,44 | 62,89 | 62,56 |

### 68 bản ghi (loại 7 bản chú thích sai) (n = 68)

| Quy tắc chọn kênh | m5 | **m12** | m22 | m12 − m5 [KTC 95 %] | p | m12 − m22 [KTC 95 %] | p |
|---|---:|---:|---:|---|---:|---|---:|
| **PSD mù nhãn (SỐ CHÍNH)** | 72,08 | **75,24** | 80,70 | +3,16 [+1,37; +5,16] | 0,0020 | -5,46 [-7,82; -3,32] | 5,47e-08 |
| kênh 0 cố định (hậu kiểm) | 59,44 | **63,34** | 70,50 | +3,91 [+1,78; +6,16] | 0,0003 | -7,15 [-10,04; -4,50] | 2,23e-06 |
| TB 4 kênh | 65,28 | **68,28** | 75,07 | +3,00 [+1,55; +4,68] | 4,67e-06 | -6,79 [-8,85; -4,84] | 2,67e-09 |
| oracle (chặn trên) | 79,22 | **81,35** | 88,42 | +2,13 [+0,60; +3,73] | 0,0037 | -7,07 [-10,11; -4,32] | 8,42e-08 |

Phân bố theo quy tắc PSD (68 bản ghi (loại 7 bản chú thích sai)): ≥ 90 điểm — m5 40, **m12 43**, m22 46; < 50 điểm — m5 20, **m12 19**, m22 14.

| Ngưỡng | 0,45 | 0,55 | 0,65 | 0,75 | 0,80 |
|---|---:|---:|---:|---:|---:|
| m12 F1 kênh PSD | 76,43 | 76,23 | 76,03 | 75,69 | 75,24 |
| m12 F1 kênh 0 | 64,84 | 64,55 | 64,23 | 63,67 | 63,34 |

## 3. Dấu vân nhãn — độ lệch thời điểm và jitter trên B1

Nếu m22 chỉ *bắt chước phong cách chấm* của B1 thì dấu hiệu rõ nhất không phải F1 mà là **vị trí mốc thời gian**: mô hình học theo nhãn B1 sẽ trùng tâm với nhãn B1, còn mô hình học nhãn điện cực da đầu sẽ lệch một khoảng hệ thống.

| Nhóm bản ghi | n | độ lệch tuyệt đối TB (ms) m5 | **m12** | m22 | jitter TB (ms) m5 | **m12** | m22 |
|---|---:|---:|---:|---:|---:|---:|---:|
| cả 10 chủ thể B1 | 10 | 6,20 | **6,40** | 3,40 | 8,22 | **7,95** | 4,79 |
| 8 chủ thể mà cả ba mô hình đều đạt F1 ≥ 95 (loại B1_06, B1_07) | 8 | 6,50 | **6,50** | 3,25 | 6,80 | **6,62** | 3,79 |

## 4. Bao nhiêu phần của lợi ích 5 → 22 được 7 chủ thể nhãn vàng tái tạo?

| Tập kiểm tra | m5 | m12 | m22 | lợi ích 5→22 | phần m12 lấy lại | phần còn cần B1 | giảm sai số tương đối m12→m22 |
|---|---:|---:|---:|---:|---:|---:|---:|
| B1 (10 chủ thể, kênh PSD) | 93,30 | **94,37** | 97,15 | +3,85 | +1,07 (28 %) | +2,78 (72 %) | 49,4 % |
| B1 (10 chủ thể, TB 4 kênh) | 91,31 | **93,44** | 97,01 | +5,71 | +2,13 (37 %) | +3,57 (63 %) | 54,5 % |
| CinC 2013 (75 bản ghi, kênh PSD) | 71,21 | **74,34** | 79,40 | +8,18 | +3,13 (38 %) | +5,06 (62 %) | 19,7 % |
| CinC 2013 (68 bản ghi, kênh PSD) | 72,08 | **75,24** | 80,70 | +8,62 | +3,16 (37 %) | +5,46 (63 %) | 22,0 % |

## 5. (c) Chính 12 chủ thể nhãn vàng — kiểm định chéo giữ lại nhóm

6/6 fold đã chạy → 12/12 chủ thể có kết quả ngoài mẫu. Ở mục này mỗi mô hình m12 chỉ học từ **9** chủ thể (2 test + 1 val bị giữ lại), còn mỗi mô hình m22 học từ **19** chủ thể — nghĩa là m22 được lợi hơn gấp đôi dữ liệu. Cột m22 lấy từ `eval_22.json` (cũng là fold giữ lại chính chủ thể đó), nên hai cột so sánh được.

| Chủ thể | Nhóm | fold | m12 (PSD) | m22 (PSD) | m12 − m22 | m12 (TB4) | m22 (TB4) |
|---|---|---:|---:|---:|---:|---:|---:|
| r01 | PhysioNet | 5 | 100,00 | 99,92 | +0,08 | 99,96 | 99,94 |
| r04 | PhysioNet | 1 | 99,44 | 99,68 | -0,24 | 98,47 | 98,24 |
| r07 | PhysioNet | 3 | 100,00 | 100,00 | +0,00 | 99,56 | 99,40 |
| r08 | PhysioNet | 4 | 99,85 | 99,77 | +0,08 | 99,71 | 99,69 |
| r10 | PhysioNet | 5 | 97,46 | 97,61 | -0,15 | 96,51 | 96,14 |
| B2_03 | B2 | 2 | 79,11 | 79,72 | -0,61 | 69,16 | 71,04 |
| B2_04 | B2 | 6 | 98,83 | 98,90 | -0,07 | 95,81 | 96,21 |
| B2_05 | B2 | 4 | 99,92 | 100,00 | -0,08 | 99,72 | 99,83 |
| B2_06 | B2 | 2 | 99,78 | 100,00 | -0,22 | 99,47 | 99,58 |
| B2_08 | B2 | 1 | 100,00 | 100,00 | +0,00 | 99,92 | 100,00 |
| B2_09 | B2 | 3 | 99,63 | 99,11 | +0,52 | 96,85 | 96,80 |
| B2_12 | B2 | 6 | 100,00 | 100,00 | +0,00 | 98,05 | 98,04 |
| **Trung bình** | | | **97,84** | **97,89** | -0,06 | 96,10 | 96,24 |

| So sánh | Hiệu số TB | KTC 95 % bootstrap | KTC 95 % t | p Wilcoxon | p sign test | thắng/thua | Cliff δ |
|---|---:|---|---|---:|---:|---:|---|
| 12 chủ thể vàng, kênh PSD: m12 − m22 | -0,06 | [-0,20; +0,09] | [-0,22; +0,11] | 0,4258 | 0,5078 | 3/6 | -0,056 (khong dang ke) |
| 12 chủ thể vàng, TB 4 kênh: m12 − m22 | -0,14 | [-0,50; +0,09] | [-0,51; +0,22] | 0,9097 | 0,7744 | 7/5 | +0,000 (khong dang ke) |

*Ghi chú thực thi: fold 01 chạy riêng, các fold 02–06 chạy song song 3 tiến trình (mỗi tiến trình 1 nhân CPU, cờ `--tag`) nên chỉ lưu số đo chứ không lưu checkpoint từng fold; checkpoint được lưu là `fetalqrs_tcn_12_fold_01.pt` và `fetalqrs_tcn_12_production.pt`. Kết quả từng fold nằm trong `model/train_12.json` (đã gộp) và `model/train_12_f23.json`, `_f45.json`, `_f6.json`.*

Ngưỡng chọn trên tập val của từng fold: 0,20, 0,30, 0,30, 0,75, 0,80, 0,80 (trung vị 0,52).

## 6. Kết luận

**Trả lời thẳng: cải thiện 5 → 22 chủ thể chủ yếu là do THÊM DỮ LIỆU, không phải do mô hình học phong cách chấm nhãn của B1. Kết luận cũ được giữ — nhưng phải phát biểu lại chặt hơn ở ba điểm.**

**Bằng chứng quyết định là CinC 2013.** CinC là tập hoàn toàn độc lập: thiết bị khác, dân số khác, người chú thích khác, không liên quan gì tới nhóm Silesia. Trên tập đó, phong cách nhãn B1 *không thể* mang lại lợi thế nào. Vậy mà m22 vẫn hơn m12 5,06 điểm (KTC 95 % [+3,19; +7,23], p = 3,76e-08, n = 75 bản ghi) và hơn m5 8,18 điểm. Ưu thế của m22 tồn tại ở nơi không có gì để bắt chước → nó là năng lực khái quát thật do nhiều dữ liệu và đa dạng hơn, không phải thiên lệch sáp nhập dữ liệu.

**Thêm 7 ca nhãn vàng KHÔNG thay thế được 10 ca B1.** m12 chỉ lấy lại khoảng một phần ba lợi ích: trên B1 +1,07 trên tổng +3,85 điểm; trên CinC +3,13 trên tổng +8,18 điểm. Tỉ lệ lấy lại gần như bằng nhau ở hai tập (28–38 %) — đúng như kỳ vọng nếu nguyên nhân là SỐ LƯỢNG chủ thể, và không phù hợp với giả thuyết "lợi ích trên B1 là ảo".

**Trên chính 12 chủ thể nhãn vàng thì 10 ca B1 KHÔNG giúp gì.** Kiểm định chéo giữ lại nhóm (12/12 chủ thể đã chạy) cho m12 97,84 so với m22 97,89 (hiệu -0,06, p Wilcoxon 0,4258) — hai mô hình không phân biệt được. Nói cách khác: dữ liệu B1 không làm mô hình tốt hơn trên bản ghi chuyển dạ 5 phút; nó chỉ giúp trên bản ghi thai kỳ 20 phút (miền của chính nó) và trên CinC 2013 (miền lạ). Đó là dáng điệu của **đa dạng dữ liệu**, không phải của việc học thuộc một quy ước chấm.

**Ba điều phải sửa trong cách phát biểu:**

1. **Có dấu vân nhãn thật, đo được — nhưng nó nằm ở mốc thời gian, không ở F1.** Trên 8 chủ thể B1 mà cả ba mô hình đều đạt F1 ≥ 95 (loại hai ca khó để không lẫn với độ khó), độ lệch thời điểm tuyệt đối trung bình là m5 6,50 ms, m12 6,50 ms, m22 3,25 ms; jitter 6,80 / 6,62 / 3,79 ms. Mô hình từng thấy B1 trùng tâm với mốc của B1 chính xác gấp đôi hai mô hình chưa từng thấy, và hai mô hình chưa từng thấy lệch **giống hệt nhau** — đó là chữ ký của quy ước chấm mốc, không phải của chất lượng dò. Với dung sai ±50 ms nó gần như không đổi F1, nhưng nó cấm ta dùng số B1 để nói về **độ chính xác thời điểm** (jitter, STV).
2. **Khoảng cách F1 trên B1 dồn vào hai ca khó, không trải đều.** 8/10 chủ thể có |m22 − m12| ≤ 0,5 điểm; toàn bộ khoảng cách nằm ở B1_07 (-19,35) và B1_06 (-7,36). Bắt chước phong cách nhãn sẽ tạo sai lệch **hệ thống trên mọi bản ghi**; cái ta thấy là ngược lại — một mô hình chưa từng thấy B1 bám sát m22 trên 8/10 ca, và chỉ thua ở đúng những ca mà dữ liệu thêm giúp được.
3. **Lợi ích trong miền lớn hơn ngoài miền, và thiết kế này không tách được "cùng miền" khỏi "cùng người chấm".** Giảm sai số tương đối khi đi từ m12 lên m22 là 49 % trên B1 nhưng chỉ 20 % trên CinC. Phần chênh này có thể là do 10 ca thêm vào đúng miền B1 (cùng máy, cùng loại bản ghi 20 phút thai kỳ, cùng dân số) — một lợi ích hợp lệ — hoặc do cùng quy ước nhãn. Ablation này **không phân tách được hai khả năng đó**; muốn tách phải có một tập thai kỳ 20 phút được chấm bằng điện cực da đầu, hiện chưa có công khai.

**Kiểm tra ngưỡng.** m12 chạy ở ngưỡng 0,80 (trung vị ngưỡng fold sẵn có lúc huấn luyện production). Nếu ưu ái m12 bằng ngưỡng tốt nhất của chính nó (0,45 trên B1 → 94,68; 0,45 trên CinC → 75,48) thì khoảng cách với m22 vẫn còn 2,47 điểm trên B1 và 3,92 điểm trên CinC. Trung vị ngưỡng của các fold m12 đã chạy xong là 0,52 — ở ngưỡng 0,75 m12 đạt 94,52 trên B1 và 74,75 trên CinC, vẫn thấp hơn m22. Kết luận không phụ thuộc ngưỡng.

**Câu đúng để viết vào bài:** *"Bỏ toàn bộ 10 chủ thể nhãn gián tiếp khỏi tập huấn luyện làm giảm 2,78 điểm F1 trên chính 10 chủ thể đó và 5,06 điểm trên 75 bản ghi CinC 2013 độc lập. Vì tập CinC không chia sẻ người chú thích với Silesia, phần lớn lợi ích của việc mở rộng dữ liệu là năng lực khái quát thật chứ không phải thiên lệch sáp nhập; phần còn lại, đo được ở độ lệch mốc thời gian chứ không ở F1, là do mô hình trùng quy ước chấm của tập B1."*

**Giới hạn của chính ablation này (khai báo thẳng):**

- m12 học từ 12 chủ thể / m22 học từ 19 chủ thể ở mỗi fold — so sánh này gộp cả **số lượng** lẫn **nguồn gốc** dữ liệu, không tách được hai yếu tố.
- m22 trên B1 là checkpoint fold **giữ lại đúng chủ thể đang đo**, nhưng vẫn thấy 9 chủ thể B1 khác; m12 chưa thấy chủ thể B1 nào. Đó chính là biến ablation, nhưng nó cũng có nghĩa m22 được lợi cả về độ dài dữ liệu (B1 dài 20 phút, gấp 4 lần bản ghi 5 phút).
- Chỉ chạy một seed (0). Độ biến thiên theo seed đã đo trước đây là 0,28 điểm trung bình trên 20 chủ thể — nhỏ so với các hiệu số báo cáo ở đây, nhưng không phải bằng không.
- Đủ 6/6 fold, 12/12 chủ thể ở mục 5. Mọi con số ở mục 1–4 dùng `production_12` (huấn luyện trên cả 12) nên không phụ thuộc số fold.
