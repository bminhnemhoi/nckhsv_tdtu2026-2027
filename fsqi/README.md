> **⚠ CẢNH BÁO (12/09/2026, sau vòng 7).** Tài liệu này được viết khi CinC 2013 set-a còn được tính trên **75 bản ghi**. Sau đó xác định 15 bản (a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25) là bản sao nguyên văn của dữ liệu huấn luyện ADFECGDB — điều ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014] và nhóm đã bỏ sót. **Mọi con số CinC dưới đây (79,40 / 85,60 / 86,87 / 71,21 / 62,82, AUROC 0,980…) bị thổi 3–7 điểm và đã bị rút.** Số chính thức trên **60 bản sạch**: PSD 74,28 · peakprob 82,01 · oracle 83,60 (`analysis/dulieu_results.json`, `benchmark_dpss/eval_cinc60_sach.json`). Kết luận định tính trong tài liệu giữ nguyên trừ khi ghi khác trong `THAMDINH_VONG7.md`. Cụm "tiền đăng ký" trong tài liệu này **không đúng** — tệp khai báo không neo git.

> **Cảnh báo (vòng 7, 12/09/2026).** Tệp này được viết khi CinC 2013 còn tính trên **75 bản ghi**; 15 bản
> trong đó là bản sao ADFECGDB (điều ban tổ chức đã ghi nhận từ 2013 — `survey/RO_RI_VANLIEU.md`). Mọi con
> số CinC-75 ở đây (79,40 / 85,60 / 86,87 / +6,20 / +8,18 / +7,47 …) **đã rút**; số hiện hành trên 60 bản
> sạch: psd 74,28 · gate 80,72 · gate4 81,01 · rrcv 80,00 · peakprob 82,01 · oracle 83,60
> (`analysis/dulieu_results.json → chon_kenh_60_sach`, `benchmark_dpss/eval_cinc60_sach.json`). Số gốc giữ
> nguyên để truy vết; kết luận định tính đọc kèm `analysis/XACNHAN.md`.

# fSQI — chỉ số chất lượng tín hiệu thai bằng đồng điều bền vững + cổng từ chối (đóng góp C3)

Câu hỏi thí nghiệm: **đặc trưng tô-pô (persistent homology) tính trên từng đoạn 4 s có dự báo được lỗi của
FetalQRS-TCN không, và có hơn các chỉ số chất lượng cổ điển không?**

Trả lời ngắn (đo thật, xem mục 4): **có dự báo được một chút, nhưng yếu, và KHÔNG hơn chỉ số cổ điển.**
Trên CinC 2013 (ngoài miền), bộ phân loại "đoạn lỗi" chỉ dùng 16 đặc trưng tô-pô đạt AUROC 0,566
(gần ngẫu nhiên), trong khi 12 chỉ số cổ điển đạt 0,929; gộp cả hai (0,905) còn kém hơn cổ điển đơn thuần.
Cổng từ chối 20 % đoạn kém tin cậy nhất: tô-pô nâng F1 trung bình đoạn từ 61,9 lên 63,4 (ngẫu nhiên: 62,0),
cổ điển nâng lên 69,4 (oracle: 74,6). Đây là **kết quả phủ định** và được công bố nguyên trạng.

## 1. Cách chạy

```
cd D:\NCKHSV2026-2027
set PYTHONIOENCODING=utf-8
set OPENBLAS_NUM_THREADS=1
python fsqi\profile_one.py r01 3      # chẩn đoán thời gian từng hàm trên r01 kênh 3 -> fsqi\profile.txt (~10 s)
python fsqi\eval_fsqi.py              # thí nghiệm đầy đủ -> results.json, segments.csv, 2 hình, fsqi_log.txt (~4 phút)
python fsqi\fsqi.py                   # tự kiểm: đối chiếu sublevel-H0 với scipy, SampEn với ma trận đầy, các ca trần cứng
```

Phụ thuộc: numpy, scipy, ripser, torch (CPU, 4 luồng), mne, wfdb, scikit-learn, matplotlib. Dữ liệu và checkpoint
lấy qua `benchmark_dpss/_paths.py` (ADFECGDB r01/r04/r07/r08/r10 tại `model/data/adfecgdb`, CinC 2013 set-a a01–a10
tại `benchmark_dpss/pcdb`; checkpoint `model/checkpoints/fetalqrs_tcn_fold_rXX.pt` cho ADFECGDB (fold đúng, bản ghi
kiểm thử = bản ghi đang đo) và `fetalqrs_tcn_production.pt` cho CinC).

## 2. Đặc trưng (`fsqi.py`)

Mọi hàm nhận một đoạn 1 chiều của tín hiệu **dư sau khử mẹ** (250 Hz, 4 s = 1000 mẫu), chuẩn hóa robust
(median/IQR) trước khi tính nên bất biến với thang biên độ.

| Nhóm | Số | Đặc trưng | Cách tính |
|---|---|---|---|
| **Tô-pô (Takens + ripser)** | 11 | `h1_total, h1_max, h1_n_abs, h1_n_rel, h1_entropy, h1_ratio, h1_count, h0_total, h0_max, h0_entropy, h0_ratio` | Nhúng trễ Takens (dim 3, τ = 5 mẫu = 20 ms), lấy mẫu con 300 điểm (hạt giống cố định), `ripser(maxdim=1)`; tổng/max/entropy/số thanh persistence của H0 và H1 |
| **Tô-pô (sublevel-set H0 1-D)** | 5 | `sl_n_prom, sl_total, sl_max, sl_entropy, sl_ratio` | H0 của lọc sublevel-set trên −x bằng union-find trên các điểm tới hạn (quy tắc elder); persistence của mỗi thanh = prominence của một đỉnh. Đối chiếu với `scipy.signal.peak_prominences`: 2011 đỉnh trên 15 đoạn thật, sai lệch tối đa 0,0 |
| **Cổ điển — chỉ tín hiệu** | 6 | `sampen, kurtosis, spec_entropy, band_ratio, psd_fhr, tau_acf` | SampEn(m=2, r=0,2σ; đếm cặp bằng cKDTree Chebyshev, đã đối chiếu với ma trận đầy), kurtosis, entropy phổ Welch, tỉ số năng lượng 10–60 Hz/0,5–100 Hz trên đoạn thô 1000 Hz, đỉnh PSD bao Hilbert trong dải nhịp thai 1,8–3,0 Hz (quy tắc Power-MF), trễ ACF qua 0 |
| **Cổ điển — đầu ra mô hình** | 6 | `rr_cv, rr_plaus, bsqi, n_det, peak_prob_mean, prob_max` | CV khoảng RR của các đỉnh mô hình, tỉ lệ RR trong 0,3–0,7 s, bSQI-like = F1 trùng khớp (±50 ms) giữa mô hình và bộ dò prominence đơn giản, số đỉnh, xác suất trung bình tại đỉnh, xác suất cực đại trong đoạn |

Nhóm "cổ điển" trong so sánh chính = 12 chỉ số (6 + 6). Hai nhóm phụ (chỉ tín hiệu / chỉ đầu ra mô hình) được
báo cáo riêng để diễn giải.

### Trần cứng thời gian (thêm sau chẩn đoán, mục 5)

`MAX_RIPSER_POINTS = 300` (loại điểm trùng bằng `np.unique`, jitter xác định 1e-9 phá cặp khoảng cách bằng nhau;
đám mây < 5 điểm → biểu đồ rỗng), `MAX_SAMPEN_N = 1000`, `MAX_SUBLEVEL_N = 5000` (giảm mẫu đều nếu dài hơn),
`robust_scale` chuyển sang std khi IQR ≈ 0, vòng tìm cực trị vector hóa. `all_features` trả về danh sách hàm vượt
`SLOW_MS = 200` để script đánh giá ghi cảnh báo. Jitter làm đặc trưng tô-pô lệch tối đa 1,2e-7 (kiểm chứng).

Thời gian đo thật trên 2100 đoạn, lần chạy sạch cuối cùng (Windows, CPU, 1 tiến trình, máy còn ~1,2 GB RAM trống):

| Hàm | TB (ms) | Trung vị | p95 | Max |
|---|---|---|---|---|
| topo (Takens + ripser) | 51,6 | 52,4 | 61,8 | 106,6 |
| sublevel H0 | 1,1 | 1,1 | 1,4 | 2,3 |
| classical (10 chỉ số) | 12,5 | 12,0 | 18,1 | 25,9 |
| **tổng / đoạn** | **65,2** | 65,4 | **79,7** | 125,8 |

Mục tiêu "mọi đoạn < 100 ms": p95 = 79,7 ms; 2/2100 đoạn vượt — đoạn đầu tiên của cả lần chạy (125,8 ms, khởi động
ripser) và một đoạn đúng 100,0 ms; 0 hàm vượt ngưỡng cảnh báo 200 ms. Lần chạy đầu (cùng mã) cho TB 58,4 / max 96,0 ms —
chênh lệch là dao động của máy, không phải của mã (kết quả số hoàn toàn trùng, xem mục 5).

## 3. Quy trình đánh giá (`eval_fsqi.py`)

1. Pipeline chuẩn của `blind_lead.py`: `preprocess → cancel_maternal → probability_series → pick_peaks` trên toàn bản
   ghi, 4 kênh bụng mỗi bản ghi. Kiểm tra: macro F1 bản ghi × kênh = **97,45** (ADFECGDB, trùng số đã công bố cho
   4 kênh) và **61,96** (CinC set-a, 40 kênh, không chọn kênh).
2. Ghép một-đối-một tham lam ±50 ms trên toàn bản ghi, gán TP/FN theo vị trí nhãn và FP theo vị trí phát hiện vào
   từng đoạn 4 s không chồng → **F1 đoạn thật**. Bỏ đoạn không có nhịp nhãn. Tổng: ADFECGDB 1500 đoạn, CinC 600 đoạn.
   F1 đoạn trung bình: ADFECGDB 97,2 (4,7 % đoạn < 80), CinC 61,9 (52,2 % đoạn < 80).
3. Spearman ρ(chỉ số, F1 đoạn) với bootstrap 95 % (1000 lần) theo đoạn và theo cụm (bản ghi × kênh).
4. Bộ phân loại "F1 đoạn < 80": **huấn luyện trên ADFECGDB, kiểm thử trên CinC**. Learner (logistic chuẩn hóa /
   HistGradientBoosting) chọn bằng LORO-CV nội bộ ADFECGDB — không nhìn CinC.
5. Cổng từ chối trên CinC: loại x % đoạn có xác suất "xấu" cao nhất (x = 0…50), F1 trung bình các đoạn giữ lại; đối
   chứng ngẫu nhiên (200 hoán vị) và oracle (từ chối theo F1 thật).

Không siêu tham số nào được chọn bằng nhãn CinC; tham số tô-pô (dim 3, τ 5, 300 điểm, ngưỡng 0,5/0,2/0,25) cố
định trước khi chạy.

## 4. Kết quả chính

### 4.1 Spearman ρ với F1 đoạn (bootstrap 95 % theo đoạn; trong ngoặc: CI theo cụm bản ghi × kênh)

| Chỉ số | Nhóm | ADFECGDB (n = 1500) | CinC 2013 (n = 600) |
|---|---|---|---|
| `prob_max` | cổ điển (mô hình) | +0,311 [+0,260, +0,359] | **+0,777** [+0,744, +0,803] (cụm [+0,650, +0,830]) |
| `peak_prob_mean` | cổ điển (mô hình) | +0,492 [+0,455, +0,527] | +0,740 [+0,702, +0,773] |
| `band_ratio` | cổ điển (tín hiệu) | −0,109 [−0,170, −0,049] | −0,727 [−0,761, −0,688] |
| `rr_cv` | cổ điển (mô hình) | −0,501 [−0,538, −0,463] | −0,662 [−0,703, −0,613] |
| `psd_fhr` | cổ điển (tín hiệu) | +0,178 [+0,121, +0,234] | +0,545 [+0,485, +0,600] |
| `rr_plaus` | cổ điển (mô hình) | **+0,585** [+0,524, +0,654] (cụm [+0,424, +0,639]) | +0,450 [+0,386, +0,511] |
| `sampen` | cổ điển (tín hiệu) | −0,294 [−0,336, −0,247] | +0,080 [+0,000, +0,159] |
| `sl_entropy` | **tô-pô** (tốt nhất ADFECGDB) | **−0,320** [−0,362, −0,277] (cụm [−0,444, −0,174]) | −0,153 [−0,234, −0,073] (cụm [−0,350, +0,065]) |
| `h1_entropy` | tô-pô | −0,256 [−0,299, −0,214] | −0,091 [−0,181, −0,008] |
| `h0_total` | tô-pô | +0,250 [+0,204, +0,294] | −0,130 [−0,207, −0,052] |
| `h0_max` | **tô-pô** (tốt nhất CinC) | +0,136 [+0,090, +0,182] | **−0,172** [−0,251, −0,095] (cụm [−0,325, +0,018]) |
| `sl_max` | tô-pô | +0,249 [+0,200, +0,298] | −0,066 [−0,151, +0,019] |

Đầy đủ 28 chỉ số: `sqi_correlation.png` và `results.json["spearman"]`. Trung bình |ρ|: tô-pô 0,20 (ADFECGDB) /
0,11 (CinC); cổ điển 0,27 / 0,46. Đáng chú ý: nhiều đặc trưng tô-pô **đổi dấu** giữa hai bộ dữ liệu (`h0_total`,
`h0_max`, `h0_entropy`, `sl_max`), nghĩa là mối liên hệ tô-pô ↔ lỗi phụ thuộc bộ dữ liệu; các chỉ số cổ điển mạnh
(`rr_cv`, `peak_prob_mean`, `prob_max`, `rr_plaus`) giữ dấu và mạnh lên khi ra ngoài miền.

### 4.2 Bộ phân loại đoạn lỗi (F1 < 80), huấn luyện ADFECGDB → kiểm thử CinC

| Nhóm đặc trưng | Số | Learner (chọn bằng CV ADFECGDB) | CV AUROC ADFECGDB | **AUROC CinC** | AUPRC CinC |
|---|---|---|---|---|---|
| Tô-pô | 16 | LR (0,665 vs GB 0,624) | 0,665 | **0,566** | 0,564 |
| Cổ điển | 12 | GB (0,901 vs LR 0,880) | 0,901 | **0,929** | 0,927 |
| Kết hợp | 28 | GB (0,906 vs LR 0,848) | 0,906 | **0,905** | 0,899 |
| Cổ điển — chỉ tín hiệu | 6 | GB (0,672 vs LR 0,659) | 0,672 | 0,666 | 0,686 |
| Cổ điển — chỉ đầu ra mô hình | 6 | LR (0,901 vs GB 0,900) | 0,901 | 0,901 | 0,892 |

Tỉ lệ dương: ADFECGDB 4,7 % (71/1500), CinC 52,2 % (313/600) — AUROC ngẫu nhiên = 0,5, AUPRC ngẫu nhiên ≈ 0,52
trên CinC. AUROC đơn lẻ trên CinC (hướng dấu lấy từ ADFECGDB): `prob_max` 0,970, `peak_prob_mean` 0,956,
`rr_cv` 0,915, `band_ratio` 0,904, `psd_fhr` 0,832, `rr_plaus` 0,739, `bsqi` 0,727.

### 4.3 Cổng từ chối trên CinC (F1 trung bình các đoạn giữ lại, %)

| Cách xếp hạng | Phủ 100 % | Phủ 90 % | **Phủ 80 %** | Phủ 50 % |
|---|---|---|---|---|
| Từ chối ngẫu nhiên (200 hoán vị) | 61,91 | 61,98 | 62,03 | 62,14 |
| Tô-pô (16) | 61,91 | 62,81 | **63,40** | 64,44 |
| Cổ điển (12) | 61,91 | 65,61 | **69,40** | 84,51 |
| Kết hợp (28) | 61,91 | 65,23 | 69,41 | 82,44 |
| Oracle (theo F1 thật) | 61,91 | 68,12 | 74,55 | 97,81 |

Hình: `risk_coverage.png`. Micro-F1 tương ứng trong `results.json["risk_coverage"]["summary"]`.

### 4.4 Câu trả lời trung thực

- **Tô-pô có dự báo được lỗi không?** Chỉ ở mức yếu. Trong miền (ADFECGDB) `sl_entropy` đạt ρ = −0,32 và LORO-CV
  AUROC 0,665; ngoài miền (CinC) AUROC rớt xuống 0,566, |ρ| tốt nhất chỉ 0,17 và khoảng tin cậy theo cụm chứa 0.
  Cổng từ chối tô-pô hơn ngẫu nhiên +1,4 điểm F1 ở độ phủ 80 % — có tín hiệu, nhưng không đủ để dùng.
- **Có hơn chỉ số cổ điển không?** **Không, ở mọi thước đo.** AUROC 0,566 vs 0,929; F1 ở độ phủ 80 % 63,4 vs
  69,4; ở 50 % 64,4 vs 84,5. Ngay cả 6 chỉ số cổ điển *chỉ tín hiệu* (không dùng đầu ra mô hình) cũng hơn tô-pô
  (0,666 vs 0,566). Gộp tô-pô vào cổ điển làm giảm AUROC (0,905 vs 0,929) và không đổi F1 ở 80 % (69,41 vs 69,40).
- **Điều gì dự báo lỗi tốt nhất?** Độ tin cậy của chính mô hình (`prob_max`, `peak_prob_mean`: AUROC đơn lẻ 0,97 /
  0,96) và tính hợp lý của nhịp (`rr_cv`), cùng `band_ratio` (tỉ số năng lượng dải 10–60 Hz) là chỉ số thuần tín hiệu
  mạnh nhất (0,90). Với RelyFetal, cổng từ chối nên dựa trên các chỉ số này; đặc trưng tô-pô không thêm giá trị.

Kết quả này nhất quán với thí nghiệm pilot fECG-TDA trước đó (TDA không đóng góp cho phát hiện QRS): mô tả tô-pô
của đoạn 4 s (số/độ dài vòng trong nhúng Takens, prominence của đỉnh) không phân biệt được "đoạn mà mô hình sai" khỏi
"đoạn mà mô hình đúng" tốt hơn các thống kê nhịp và phổ rẻ hơn nhiều lần.

## 5. Chẩn đoán vụ treo 2236 s (bước 1) — `profile_one.py`

Lần chạy trước, r01 kênh 3 mất 2236 s (kênh 1–2: 13 s). Chạy lại `profile_one.py r01 3` với **cùng mã nguồn**
(fsqi.py bản 14:43, chưa sửa) cho 75 đoạn trong **3,7 s tổng** (topo TB 34 ms, classical 14 ms, sublevel 1 ms; đoạn
chậm nhất 124 ms là đoạn 0 do khởi động ripser) — xem `profile_before_fix.txt`. Đám mây Takens của mọi đoạn đều 300
điểm phân biệt, hạng 3, không có cặp khoảng cách 0: không có đoạn nào thoái hoá. Vì mã hoàn toàn xác định (hạt giống
cố định), **không tái hiện được** hiện tượng; nguyên nhân khả dĩ nhất nằm ngoài tiến trình: máy khi đó chỉ còn ~1,2/15,7
GB RAM và ~1,7/44,5 GB commit trống (nhiều phiên khác chạy song song), OpenBLAS mặc định mở 12 luồng/tiến trình và
đã gặp lỗi "memory allocation failed" khi chạy 2–3 tiến trình cùng lúc trong phiên này. Biện pháp: giới hạn
`OMP/OPENBLAS/MKL_NUM_THREADS` ngay đầu `eval_fsqi.py`, chạy một tiến trình một lúc, thêm trần cứng cho mọi hàm và
cảnh báo đoạn > 200 ms để lần sau log chỉ đích danh. Lần chạy lại: r01 kênh 3 mất 4,7 s (lần 1) / 6,1 s (lần chạy
sạch), toàn bộ eval 3,8 / 4,0 phút.

Sau khi thêm trần cứng: `profile.txt` (75 đoạn r01 kênh 3, 0 đoạn vượt 100 ms). Lần chạy sạch cuối cùng (xóa mọi đầu
ra rồi chạy `profile_one.py` + `eval_fsqi.py`) cho `results.json` **trùng 100 % (0/1327 trường khác)** với lần chạy đầu,
chỉ khác thời gian — quy trình xác định hoàn toàn (hạt giống cố định cho lấy mẫu con, jitter, bootstrap, GB).

## 6. Hạn chế

- CinC set-a chỉ 10 bản ghi × 1 phút; lỗi tập trung theo bản ghi (4/10 bản ghi F1 = 100, 3/10 < 50), nên CI theo cụm
  rộng hơn nhiều CI theo đoạn — số theo đoạn (n = 600) phóng đại độ chắc chắn.
- Nhãn "đoạn xấu" = F1 < 80 trên đoạn 4 s (thường 8–12 nhịp): độ phân giải thô; đổi ngưỡng có thể đổi AUROC tuyệt đối
  nhưng thứ tự tô-pô < cổ điển cách nhau quá xa để bị đảo.
- Bộ phân loại huấn luyện trên ADFECGDB gần như không có đoạn xấu (4,7 %); AUROC kết hợp (0,905) thấp hơn AUROC đơn
  lẻ của `prob_max` (0,970) cho thấy khả năng chuyển miền của learner hạn chế — một ngưỡng đơn trên `prob_max` có thể
  đã là cổng tốt hơn, nhưng chưa đo trong script này.
- Chỉ một cấu hình tô-pô (dim 3, τ 5, 300 điểm, maxdim 1) — không quét tham số để tránh chọn theo nhãn kiểm thử.
- Không chạy được nhiều tiến trình song song trên máy hiện tại (thiếu bộ nhớ), nên thời gian đo là của 1 tiến trình
  và dao động ±10–15 % giữa hai lần chạy cùng mã.
- Trên CinC, F1 ở độ phủ 100 % là 61,9 (trung bình 40 kênh, không chọn kênh); số **77,34** từng công bố là
  theo bản ghi với quy tắc chọn kênh, nên hai con số không so sánh trực tiếp. *(Sửa 12/09/2026: **77,34 đã
  bị rút** — nó là kênh 0 cố định chọn hậu kiểm, đo trên mẫu 10/75 bản ghi. Trên đủ 75 bản ghi, mô hình 5 ca
  với quy tắc mù nhãn đạt 71,21 và mô hình 22 ca đạt 79,40. Thí nghiệm cổng từ chối trong tài liệu này
  **chưa chạy lại** trên 75 bản ghi.)*

## 7. Tệp

| Tệp | Nội dung |
|---|---|
| `fsqi.py` | thư viện đặc trưng + trần cứng + tự kiểm (`python fsqi/fsqi.py`) |
| `eval_fsqi.py` | thí nghiệm đầy đủ; mọi con số trên đều do script này ghi |
| `profile_one.py` | chẩn đoán thời gian từng hàm trên một kênh |
| `profile.txt` / `profile_before_fix.txt` | profile r01 kênh 3 sau / trước khi thêm trần cứng |
| `results.json` | meta, thời gian, Spearman + CI, bộ phân loại, AUROC đơn lẻ, đường risk-coverage, kết luận tự động |
| `segments.csv` | 2100 dòng: một đoạn = một dòng (TP/FP/FN/F1 + 28 đặc trưng + thời gian) |
| `sqi_correlation.png`, `risk_coverage.png` | hình |
| `fsqi_log.txt` | log lần chạy sạch cuối cùng |
