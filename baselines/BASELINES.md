> **⚠ CẢNH BÁO (12/09/2026, sau vòng 7).** Tài liệu này được viết khi CinC 2013 set-a còn được tính trên **75 bản ghi**. Sau đó xác định 15 bản (a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25) là bản sao nguyên văn của dữ liệu huấn luyện ADFECGDB — điều ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014] và nhóm đã bỏ sót. **Mọi con số CinC dưới đây (79,40 / 85,60 / 86,87 / 71,21 / 62,82, AUROC 0,980…) bị thổi 3–7 điểm và đã bị rút.** Số chính thức trên **60 bản sạch**: PSD 74,28 · peakprob 82,01 · oracle 83,60 (`analysis/dulieu_results.json`, `benchmark_dpss/eval_cinc60_sach.json`). Kết luận định tính trong tài liệu giữ nguyên trừ khi ghi khác trong `THAMDINH_VONG7.md`. Cụm "tiền đăng ký" trong tài liệu này **không đúng** — tệp khai báo không neo git.

> **Cảnh báo (vòng 7, 12/09/2026).** Tệp này được viết khi CinC 2013 còn tính trên **75 bản ghi**; 15 bản
> trong đó là bản sao ADFECGDB (điều ban tổ chức đã ghi nhận từ 2013 — `survey/RO_RI_VANLIEU.md`). Mọi con
> số CinC-75 ở đây (79,40 / 85,60 / 86,87 / +6,20 / +8,18 / +7,47 …) **đã rút**; số hiện hành trên 60 bản
> sạch: psd 74,28 · gate 80,72 · gate4 81,01 · rrcv 80,00 · peakprob 82,01 · oracle 83,60
> (`analysis/dulieu_results.json → chon_kenh_60_sach`, `benchmark_dpss/eval_cinc60_sach.json`). Số gốc giữ
> nguyên để truy vết; kết luận định tính đọc kèm `analysis/XACNHAN.md`.

# Baseline: so sánh đơn kênh và đa kênh (nhiệm vụ A2)

*Tạo tự động bởi `baselines/powermf_fair_table.py` ngày 2026-09-12T07:49:00. Mọi con số trong tài liệu này đều do chạy thật trong repo, có JSON và log kèm theo.*

## 0. Điều quan trọng nhất: sửa một lỗi cổng chuyển, không phải sửa tham số

Lần chạy Power-MF trước (`baselines/powermf_results.json`) có 6/10 bản ghi Silesia B1 hỏng: B1_01 và B1_02 cho Se ≈ 50 % với PPV ≈ 99,7; B1_03–B1_06 trả về rỗng. Giả thuyết ban đầu là tham số `ms_minpeakdistance = 340 ms` quá sát nhịp tim thai. **Giả thuyết đó sai.** Chẩn đoán thật nằm ở mục 1.

## 1. Chẩn đoán lỗi (PHẦN 1a–1c)

### 1.1 Bác bỏ giả thuyết `ms = 340 ms` quá sát

`baselines/powermf_diag.py` đo RR thật của từng bản ghi từ nhãn tham chiếu (`baselines/powermf_rr_diag.json`):

| Bản ghi | HR (bpm) | RR trung vị (ms) | RR bách phân vị 5 (ms) | % khoảng RR < 340 ms |
|---|---:|---:|---:|---:|
| B1_01 | 155.4 | 386.0 | 358.0 | 0.00 |
| B1_02 | 142.2 | 422.0 | 404.0 | 0.00 |
| B1_07 | 157.1 | 382.0 | 366.0 | 0.00 |
| B2_03 | 157.1 | 382.0 | 362.0 | 0.14 |

Trên **cả 27 bản ghi** đã kiểm tra, tỉ lệ khoảng RR ngắn hơn 340 ms lớn nhất là **0.15 %**. Nói cách khác ràng buộc 340 ms **chưa từng chặn một nhịp thật nào**. Thêm nữa B1_07 có đúng nhịp tim thai như B1_01 (157,1 bpm, RR 382 ms) nhưng đạt F1 = 98,93 ở lần chạy cũ. Tham số không phải nguyên nhân.

### 1.1b Vì sao không dùng tham số thích nghi

Vì giả thuyết bị bác bỏ, **không có thay đổi nào về `ms`**: mọi lần chạy trong tài liệu này vẫn dùng `ms = 340 ms`, đúng giá trị mặc định của `PowerMF.m`, nên cột Power-MF so sánh được với số đã công bố. `powermf_diag.py` vẫn cài một bộ ước lượng RR **mù nhãn** (băng 10–60 Hz → bao hình |đạo hàm| → Welch → đỉnh trong 1,6–3,6 Hz) để kiểm tra phương án `ms = 0,7 × RR ước lượng`. Kết quả: sai số tuyệt đối trung bình **101,2 ms**, trung vị 78,4 ms, lớn nhất 243,0 ms, và 13/27 bản ghi lệch quá 100 ms. Một tham số thích nghi dựng trên ước lượng đó sẽ **tệ hơn** hằng số 340 ms. Ghi lại ở đây như một kết quả âm tính.

### 1.2 Nguyên nhân thật: `findpeaks` của Octave tốn O(k²) bộ nhớ

Đọc log Octave từng bản ghi trong `baselines/powermf_work/*_octave.log` cho **một thông báo lỗi duy nhất** trên cả 6 bản ghi hỏng:

```
There was an error! The message was:
out of memory or dimension too large for Octave's index type
  at findpeaks line 203
  at PowerMF line 150   (hoặc 164)
```

`findpeaks` của gói `signal` trong Octave cài đặt ràng buộc `MinPeakDistance` bằng một **ma trận khoảng cách đôi một giữa các ứng viên đỉnh**, tức O(k²) bộ nhớ. Bản ghi Silesia B1 dài 1 197 800 mẫu, cắt đôi còn 598 900 mẫu, nội suy ×4 thành 2 395 600 mẫu ở 4000 Hz; số ứng viên đỉnh lên tới hàng chục nghìn nên ma trận vượt giới hạn chỉ số 32 bit của Octave. MATLAB — nền tảng của tác giả — giải ràng buộc này bằng thuật toán tham O(k log k) nên **không bao giờ gặp lỗi này**.

Bằng chứng khẳng định: trong bản ghi cắt đôi, **một nửa chạy đúng và một nửa chết**. B1_01 phát hiện 1555 đỉnh, toàn bộ nằm ở nửa đầu, 0 đỉnh ở nửa sau; khoảng cách phát hiện trung vị 385,5 ms so với RR thật 386,0 ms — tức nửa chạy được thì chạy **hoàn hảo**. B1_02 ngược lại: 0 đỉnh nửa đầu, 1424 đỉnh nửa sau. Se ≈ 50 % chính là "mất đúng một nửa bản ghi", không phải "bắt cách nhịp".

### 1.3 Bản vá P7

`baselines/octave/findpeaks_mpd.m` thay `findpeaks(x, 'MinPeakDistance', d)` bằng đúng ngữ nghĩa của MATLAB: tìm mọi cực đại địa phương → sắp theo biên độ giảm dần → tham lam nhận đỉnh cao nhất và loại mọi đỉnh cách nó dưới `d`. Dùng danh sách liên kết đôi nên mỗi ứng viên bị gỡ đúng một lần, tổng chi phí O(k). Đã đo: 2 395 600 mẫu chạy trong 14,3 s và **không tốn ma trận nào**.

Kiểm chứng đối chiếu (`baselines/octave/test_fpmpd.m`, 48 trường hợp): tập đỉnh của `findpeaks` Octave **luôn là tập con** của `findpeaks_mpd` (giao = đúng số đỉnh Octave trả về trong 48/48 trường hợp). Chênh lệch đến từ bộ lọc bề rộng đỉnh mặc định của Octave (`MinPeakWidth`, ước lượng bằng khớp parabol) mà **MATLAB không có** khi chỉ truyền `MinPeakDistance`. Vậy bản vá P7 làm cho bản chạy Octave **gần bản gốc MATLAB hơn**, chứ không phải xa hơn. Vì P7 thay đổi ngữ nghĩa một chút, **toàn bộ 27 bản ghi đã được chạy lại** với cùng một bản mã để cột Power-MF nhất quán nội bộ.

## 2. Kết quả trước và sau bản vá (PHẦN 1d)

| Bản ghi | Power-MF cũ (P1–P6) | Power-MF sau P7 | Chênh |
|---|---:|---:|---:|
| B1_01 | 66.44 | 99.92 | +33.48 |
| B1_02 | 67.12 | 99.55 | +32.43 |
| B1_03 | THẤT BẠI | 98.97 | — |
| B1_04 | THẤT BẠI | 99.86 | — |
| B1_05 | THẤT BẠI | 99.66 | — |
| B1_06 | THẤT BẠI | 99.97 | — |
| B1_07 | 98.93 | 99.44 | +0.50 |
| B1_08 | 99.16 | 99.31 | +0.16 |
| B1_09 | 97.98 | 98.39 | +0.42 |
| B1_10 | 99.54 | 98.91 | -0.63 |
| **B1 trung bình** | **88.19** (n=6 chạy được) | **99.40** (n=10) | |

B1_01 đi từ 66,44 lên **99.92** và B1_02 từ 67,12 lên **99.55**. Vậy **đó đúng là lỗi cổng chuyển**, không phải tính chất của Power-MF.

**Kiểm chứng ngoài.** Số đã công bố của repo gốc cho Silesia B1 là **99,46** (`baselines/powermf_published.json`, trích từ `Results/*.mat`). Sau bản vá P7 ta chạy lại được **99.40** trên đúng 10 bản ghi đó — lệch 0.06 điểm, nằm trong sai khác biên `filtfilt` giữa Octave và MATLAB. Trước P7 con số này là 88,19 trên 6 bản chạy được. Đây là bằng chứng độc lập rằng bản chạy lại hiện đã đúng.

## 3. Bảng cuối cùng: đơn kênh so với đa kênh (PHẦN 3)

Tất cả chấm bằng cùng một bộ: `model/fqrs_model.py::match_events`, dung sai ±50 ms, ghép tham lam 1-1.

| Chu thể | Nhóm | **ĐƠN KÊNH** RelyFetal | **ĐƠN KÊNH** Power-MF-1ch | **ĐA KÊNH** Power-MF (4 đạo trình) |
|---|---|---:|---:|---:|
| r01 | ADFECGDB | 99.92 | 92.33 | 99.69 |
| r04 | ADFECGDB | 99.68 | 92.41 | 99.53 |
| r07 | ADFECGDB | 100.00 | 90.17 | 99.20 |
| r08 | ADFECGDB | 99.77 | 90.05 | 99.46 |
| r10 | ADFECGDB | 97.61 | 96.91 | 97.15 |
| B2_03 | B2 | 79.72 | 47.97 | 89.49 |
| B2_04 | B2 | 98.90 | 97.88 | 97.95 |
| B2_05 | B2 | 100.00 | 90.77 | 99.70 |
| B2_06 | B2 | 100.00 | 99.56 | 99.85 |
| B2_08 | B2 | 100.00 | 86.13 | 99.77 |
| B2_09 | B2 | 99.11 | 98.44 | 98.74 |
| B2_12 | B2 | 100.00 | 90.23 | 99.77 |
| B1_01 | B1 | 99.97 | 95.25 | 99.92 |
| B1_02 | B1 | 99.79 | 98.73 | 99.55 |
| B1_03 | B1 | 99.92 | 91.30 | 98.97 |
| B1_04 | B1 | 100.00 | 99.98 | 99.86 |
| B1_05 | B1 | 99.87 | 93.83 | 99.66 |
| B1_06 | B1 | 89.45 | 54.36 | 99.97 |
| B1_07 | B1 | 86.56 | 63.36 | 99.44 |
| B1_08 | B1 | 99.83 | 83.50 | 99.31 |
| B1_09 | B1 | 99.07 | 88.27 | 98.39 |
| B1_10 | B1 | 97.05 | 66.18 | 98.91 |
| **ADFECGDB (n=5)** | | **99.40 ± 1.01** | **92.37 ± 2.78** | **99.01 ± 1.05** |
| **B2 (n=7)** | | **96.82 ± 7.55** | **87.28 ± 18.05** | **97.90 ± 3.77** |
| **B1 (n=10)** | | **97.15 ± 4.95** | **83.48 ± 16.28** | **99.40 ± 0.51** |
| **TẤT CẢ 22 (n=22)** | | **97.56 ± 5.30** | **86.71 ± 14.87** | **98.83 ± 2.20** |

**Phụ chú — hai hàng 0 trong mẫu.** `PowerMF.m` gán `template(j,:)` từ `j = 3`, nên trong MATLAB hàng 1 và hàng 2 của ma trận mẫu tự động bằng 0 và vẫn được đưa vào `median(template,1)`. Gần như chắc chắn đây là lỗi của tác giả. Power-MF-1ch cài cả hai chế độ: tái lập nguyên vẹn cho **86.71**, bỏ hai hàng 0 cho **86.70** — chênh 0.01 điểm trên 22 chủ thể. Lỗi này **không có hậu quả đo được** (`baselines/powermf_1ch_nofaith.json`).

### 3.1 Năm phương pháp đơn kênh trên ADFECGDB, cùng quy tắc PSD mù nhãn

TS, TS-PCA và bộ dò prominence (`baselines/results.json`) chỉ được chạy trên 5 bản ghi ADFECGDB, nên chúng nằm ở bảng riêng này.

| Bản ghi | TS | TS-PCA | Prominence | Power-MF-1ch | RelyFetal | **Power-MF 4 kênh** |
|---|---|---|---|---|---|---|
| r01 | 93.01 | 97.27 | 92.47 | 92.33 | 99.92 | 99.69 |
| r04 | 85.46 | 96.19 | 93.75 | 92.41 | 99.68 | 99.53 |
| r07 | 74.47 | 97.55 | 93.02 | 90.17 | 100.00 | 99.20 |
| r08 | 88.48 | 97.27 | 84.99 | 90.05 | 99.77 | 99.46 |
| r10 | 96.98 | 95.43 | 95.93 | 96.91 | 97.61 | 97.15 |
| **Trung bình (n=5)** | **87.68** | **96.74** | **92.03** | **92.37** | **99.40** | **99.01** |

## 4. Thống kê mức chủ thể

Hiệu số F1 ghép cặp theo chủ thể · khoảng tin cậy 95 % bằng cluster bootstrap (10000 lần, lấy mẫu lại chủ thể có hoàn lại) · Wilcoxon ghép cặp · Cliff delta · (thắng/hòa/thua).

| Tập | So sánh | Hiệu (điểm F1) | KTC 95 % | p | Cliff | T/H/T |
|---|---|---:|---|---:|---:|---|
| Tất cả 22 | RelyFetal (1 kênh) − Power-MF (4 kênh) | -1.27 | [-3.08; +0.27] | 0.156 | 0.260 | 18/0/4 |
| Tất cả 22 | RelyFetal (1 kênh) − Power-MF-1ch | +10.85 | [+6.80; +15.40] | 4.77e-07 | 0.698 | 22/0/0 |
| Tất cả 22 | Power-MF-1ch − Power-MF (4 kênh) | -12.12 | [-18.27; -6.90] | 1.43e-06 | -0.773 | 1/0/21 |
| ADFECGDB (5) | RelyFetal (1 kênh) − Power-MF (4 kênh) | +0.39 | [+0.22; +0.60] | 0.0625 | 0.600 | 5/0/0 |
| ADFECGDB (5) | RelyFetal (1 kênh) − Power-MF-1ch | +7.02 | [+3.84; +9.34] | 0.0625 | 1.000 | 5/0/0 |
| ADFECGDB (5) | Power-MF-1ch − Power-MF (4 kênh) | -6.63 | [-8.88; -3.37] | 0.0625 | -1.000 | 0/0/5 |
| Silesia B2 (7) | RelyFetal (1 kênh) − Power-MF (4 kênh) | -1.08 | [-4.04; +0.54] | 0.297 | 0.388 | 6/0/1 |
| Silesia B2 (7) | RelyFetal (1 kênh) − Power-MF-1ch | +9.54 | [+3.09; +17.87] | 0.0156 | 0.673 | 7/0/0 |
| Silesia B2 (7) | Power-MF-1ch − Power-MF (4 kênh) | -10.61 | [-21.84; -2.67] | 0.0156 | -0.673 | 0/0/7 |
| Silesia B1 (10) | RelyFetal (1 kênh) − Power-MF (4 kênh) | -2.25 | [-5.55; +0.32] | 1 | 0.080 | 7/0/3 |
| Silesia B1 (10) | RelyFetal (1 kênh) − Power-MF-1ch | +13.68 | [+6.91; +21.27] | 0.00195 | 0.620 | 10/0/0 |
| Silesia B1 (10) | Power-MF-1ch − Power-MF (4 kênh) | -15.92 | [-25.93; -7.05] | 0.00391 | -0.780 | 1/0/9 |

## 5. Kết luận

1. **RelyFetal đơn kênh so với Power-MF đa kênh, trên cùng 22 chủ thể, sau khi đã sửa lỗi cổng chuyển: hiệu -1.27 điểm F1, KTC 95 % [-3.08; +0.27], p = 0.156.** RelyFetal không phân biệt được với Power-MF đa kênh.
2. **So sánh công bằng thực sự: Power-MF-1ch (cùng một đạo trình, cùng front-end, cùng bộ khử mẹ) đạt 86.71 ± 14.87, tức kém RelyFetal 10.85 điểm F1 (KTC 95 % [+6.80; +15.40], Wilcoxon p = 4.77e-07, thắng 22/22 chủ thể).**
3. **Bỏ ICA đa kênh khiến chính Power-MF mất -12.12 điểm F1 (KTC 95 % [-18.27; -6.90]).** Phần thắng của Power-MF nằm chủ yếu ở **tách nguồn đa kênh**, không nằm ở bộ lọc phối hợp. Đây là lập luận phòng thủ mạnh nhất cho việc một mô hình đơn kênh 113k tham số không cần thắng một thuật toán bốn đạo trình.

### Phát biểu đúng để đưa vào bài

> Trên 22 chủ thể độc lập chấm bằng cùng một giao thức (±50 ms), mô hình đơn kênh 113k tham số đạt hiệu -1.27 điểm F1 so với Power-MF đa kênh (KTC 95 % cluster bootstrap [-3.08; +0.27]; Wilcoxon p = 0.156). Khi Power-MF bị giới hạn về cùng một đạo trình (Power-MF-1ch), khoảng cách đảo chiều thành +10.85 điểm nghiêng về mô hình học sâu.

## 6. Tệp sinh ra

- `baselines/powermf_diag.py` — chẩn đoán RR thật và RR mù nhãn
- `baselines/powermf_rr_diag.json` — kết quả chẩn đoán RR (27 bản ghi)
- `baselines/octave/findpeaks_mpd.m` — bản vá P7 — findpeaks O(k) theo ngữ nghĩa MATLAB
- `baselines/octave/test_fpmpd.m` — kiểm chứng P7 (48 trường hợp)
- `baselines/powermf_fair_run.py` — chạy lại toàn bộ Power-MF đa kênh với P7
- `baselines/powermf_fair.json` — kết quả Power-MF đa kênh sau P7
- `baselines/powermf_fair_log.txt` — log chạy lại
- `baselines/powermf_1ch.py` — Power-MF-1ch (Python, đơn kênh)
- `baselines/powermf_1ch.json` — kết quả Power-MF-1ch (22 chủ thể + CinC 2013)
- `baselines/powermf_fair_stats.json` — thống kê mức chủ thể
- `baselines/BASELINES.md` — tài liệu này

## 7. Power-MF-1ch trên CinC 2013 (75 bản ghi)

| Quy tắc chọn đạo trình | Power-MF-1ch | RelyFetal 22 chủ thể (mốc 12/09) |
|---|---:|---:|
| PSD mù nhãn (số chính) | 62.82 | 79,40 |
| kênh 0 cố định | 55.04 | 69,33 |
| trung bình 4 kênh | 59.99 | 74,09 |
| oracle (kênh tốt nhất) | 75.12 | 86,87 |

68 bản ghi (loại 7 bản chú thích sai): Power-MF-1ch 64.12.

