> **⚠ CẢNH BÁO (12/09/2026, sau vòng 7).** Tài liệu này được viết khi CinC 2013 set-a còn được tính trên **75 bản ghi**. Sau đó xác định 15 bản (a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25) là bản sao nguyên văn của dữ liệu huấn luyện ADFECGDB — điều ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014] và nhóm đã bỏ sót. **Mọi con số CinC dưới đây (79,40 / 85,60 / 86,87 / 71,21 / 62,82, AUROC 0,980…) bị thổi 3–7 điểm và đã bị rút.** Số chính thức trên **60 bản sạch**: PSD 74,28 · peakprob 82,01 · oracle 83,60 (`analysis/dulieu_results.json`, `benchmark_dpss/eval_cinc60_sach.json`). Kết luận định tính trong tài liệu giữ nguyên trừ khi ghi khác trong `docs/nhat_ky/THAMDINH_VONG7.md`. Cụm "tiền đăng ký" trong tài liệu này **không đúng** — tệp khai báo không neo git.

> **Cảnh báo (vòng 7, 12/09/2026).** Tệp này được viết khi CinC 2013 còn tính trên **75 bản ghi**; 15 bản
> trong đó là bản sao ADFECGDB (điều ban tổ chức đã ghi nhận từ 2013 — `survey/RO_RI_VANLIEU.md`). Mọi con
> số CinC-75 ở đây (79,40 / 85,60 / 86,87 / +6,20 / +8,18 / +7,47 …) **đã rút**; số hiện hành trên 60 bản
> sạch: psd 74,28 · gate 80,72 · gate4 81,01 · rrcv 80,00 · peakprob 82,01 · oracle 83,60
> (`analysis/dulieu_results.json → chon_kenh_60_sach`, `benchmark_dpss/eval_cinc60_sach.json`). Số gốc giữ
> nguyên để truy vết; kết luận định tính đọc kèm `analysis/XACNHAN.md`.

# E1 — Kiểm chứng giả thuyết "bài toán fQRS đơn kênh là lưỡng cực"

**Ngày:** 2026-09-12 · **Chạy lại:** `python analysis/luongcuc_feat.py && python analysis/luongcuc.py`
**Mọi số trong tài liệu này đều nằm trong** `analysis/luongcuc_results.json` **và** `analysis/luongcuc_feat.json`.
**Hình:** `analysis/fig_luongcuc.png`

---

## 0. Kết luận một dòng

Giả thuyết **được ủng hộ một phần, và phần bị bác bỏ là phần quan trọng nhất về mặt cơ chế.**

* Phần **"mọi lựa chọn thiết kế đều không quan trọng trên đa số dễ"** — **đúng trên thang điểm F1**,
  lặp lại trên 4 phép so sánh độc lập và 2 bộ dữ liệu.
* Nhưng khi tự dựng đối chứng bỏ trần 100 (làm lại trên thang logit), **hai trong bốn phép so sánh
  mất hoàn toàn tính tập trung** — hiệu ứng "thêm dữ liệu huấn luyện" hoá ra **lớn hơn** trên nhóm dễ.
  Nghĩa là: phần lớn "sự tập trung" mà ta quan sát là **hiệu ứng trần của chính thước đo F1**, không phải
  một tính chất của bài toán.
* Phân bố F1 **có bằng chứng lưỡng cực trên mẫu lớn (75 bản ghi CinC)** nhưng **không** trên 22 chủ thể,
  và **biến mất khi dùng kênh tốt nhất (oracle)** — tức một phần đáng kể của cực dưới là **lỗi quy tắc
  chọn kênh**, không phải độ khó nội tại của bản ghi.
* **Không tìm được cơ chế vật lý** tách được ba bản ghi khó (xem §1, phản ví dụ B1_08).

Kết luận thực hành vẫn đứng vững và thậm chí mạnh hơn ban đầu:
**F1 trung bình theo bản ghi là thước đo sai** — không chỉ vì nó bị ba bản ghi kéo, mà còn vì trần 100
nén mọi hiệu ứng thật trên nhóm dễ xuống gần 0 và khiến ta tưởng "không có gì khác biệt" khi thực ra có.

---

## 1. Câu hỏi 1 — Ba bản ghi đó có gì khác biệt đo được?

Đo trên **đúng kênh PSD mù nhãn** mà `benchmark_dpss/eval_22.json` đã chọn cho từng chủ thể
(script `analysis/luongcuc_feat.py`, kết quả `analysis/luongcuc_feat.json`; mọi định nghĩa nằm
trong khoá `meta.dinh_nghia` của tệp đó, kèm nhãn **DÙNG NHÃN / KHÔNG DÙNG NHÃN**).

### 1.1 Đại lượng nào tách được 3 khó khỏi 19 còn lại?

| Đại lượng | Dùng nhãn? | AUC (3 khó vs 19) | p Mann–Whitney | Hạng của 3 bản khó | Khoảng trống hạng 3→4 |
|---|---|---|---|---|---|
| `fsnr_db` (tỉ số tín/tạp thai) | **có** | 0,000 (tách hoàn hảo) | 0,0013 | 1, 2, 3 | **0,005 dB** |
| `gate_score` (điểm cổng từ chối) | không | 0,000 (tách hoàn hảo) | 0,0013 | 1, 2, 3 | 0,188 (≈ 6 SD của 19) |
| `fsnr_vs_resid_db` | có | 0,035 | 0,0052 | 1, 2, 5 | 0,41 dB |
| `fhr_bpm` (nhịp tim thai) | có | 0,965 | 0,013 | 18, 21, 22 | 9,1 bpm |
| `mf_ratio_db` (mẹ/con) | có | 0,807 | 0,108 | 9, 21, 22 | — |
| `resid_m_frac` (tàn dư mẹ) | không | 0,719 | 0,265 | 12, 16, 19 | — |
| `overlap100` (chồng lấn nhịp) | có | 0,316 | 0,356 | 3, 8, 13 | — |
| `duration_s`, `drift_frac`, `rr_cv`, `rr_sd_ms`, `maternal_lock`, `hum50_frac` | — | 0,44–0,83 | ≥ 0,09 | rải rác | — |

**Đã thực hiện 45 phép so sánh tương quan** (15 đại lượng × 3 mục tiêu). Ngưỡng Bonferroni là
p < 0,0011. **Chỉ một quan hệ vượt ngưỡng:** `gate_score` vs F1, rho = 0,684, p = 0,0004.
`fsnr_db` vs F1 cho rho = 0,525, **p = 0,0121 — KHÔNG vượt Bonferroni.**

### 1.2 Phản ví dụ giết cơ chế: B1_08

`fsnr_db` xếp đúng ba bản ghi khó vào ba hạng thấp nhất (xác suất ngẫu nhiên 2/C(22,3) = 0,0013).
Nhưng:

```
B2_03  fSNR 10,898 dB   F1  79,72   (khó)
B1_06  fSNR 11,145 dB   F1  89,45   (khó)
B1_07  fSNR 13,656 dB   F1  86,56   (khó)
B1_08  fSNR 13,661 dB   F1  99,83   (DỄ)   <-- cách B1_07 đúng 0,005 dB
B1_09  fSNR 14,820 dB   F1  99,07   (dễ)
```

Biên giữa hạng 3 và hạng 4 là **0,005 dB**, bằng **0,17 %** độ lệch chuẩn của 19 bản còn lại.
Hai bản ghi có tỉ số tín/tạp thai giống hệt nhau chênh nhau **13,3 điểm F1**.

> **Phát biểu trung thực:** fSNR thấp có vẻ là điều kiện **cần** (cả ba bản khó đều nằm trong nhóm
> fSNR thấp nhất) nhưng **không đủ**, và ngưỡng tách không tồn tại về mặt vật lý — nó là một khoảng
> trống rộng 0,005 dB. **Chúng tôi KHÔNG tìm được cơ chế.**

Ngoài ra `fsnr_db` **dùng nhãn** để định vị phức bộ thai, nên kể cả nếu nó tách được thì nó cũng
**không phải tiêu chí triển khai được**. Đại lượng duy nhất vừa tách hoàn hảo vừa không nhìn nhãn
lúc suy luận là `gate_score`, nhưng cổng này **được huấn luyện có giám sát để dự đoán F1 đoạn**
(leave-one-subject-out) — nó là **một bộ dự báo F1**, không phải một lời giải thích vật lý. Dùng nó
làm cơ chế là lập luận vòng.

---

## 2. Câu hỏi 2 — Phân bố F1 có thật sự lưỡng cực không?

### 2.1 Xử lý trần 100 (bắt buộc)

F1 bị chặn trên ở 100; **28/75** bản ghi CinC và **6/22** chủ thể đạt đúng 100,00. Mọi kiểm định
được lặp lại trên **ba thang**:

1. **thô** — F1 (%) như công bố;
2. **logit** — `log(p/(1-p))` với `p = F1/100`, hiệu chỉnh liên tục **riêng từng bản ghi**
   `eps = 1/(4·n_ref)` (sai một nhịp làm F1 đổi ~`1/(2·n_ref)`, nên eps bằng nửa bước phân giải);
3. **log10(100 − F1)** với cùng hiệu chỉnh.

> **Cảnh báo tự đặt ra:** phép biến đổi logit *kéo giãn* vùng gần 100 và *nén* vùng giữa, tức nó
> **thiên về việc tạo ra** vẻ lưỡng cực. Vì vậy dưới đây chỉ những kết luận **giống nhau trên cả ba
> thang** mới được coi là vững, và kết quả thang thô được nêu trước.

### 2.2 Kiểm định Hartigan dip

| Mẫu | thang thô | thang logit | log10(100−F1) |
|---|---|---|---|
| CinC 75 (m22, kênh PSD) | dip 0,0499 · **p = 0,175** | dip 0,0807 · **p = 0,00051** | dip 0,1159 · **p < 1e−5** |
| CinC 68 (bỏ 7 bản nhãn xấu) | p = 0,083 | **p = 0,00064** | — |
| 22 chủ thể | p = 0,954 | **p = 0,854** | p = 0,853 |
| CinC 75 trên **kênh tốt nhất (oracle)** | p = 0,949 | **p = 0,589** | — |

### 2.3 Mô hình hỗn hợp Gauss, so sánh BIC

| Mẫu / thang | BIC k=1 | BIC k=2 | BIC k=3 | k tốt nhất |
|---|---|---|---|---|
| CinC 75, thô | 726,5 | 482,5* | 480,4 | 3 |
| CinC 75, logit | 384,6 | 336,0 | **264,9** | 3 |
| CinC 68, logit | — | — | — | ≥2 (ΔBIC 1−2 = +54,5) |
| 22 chủ thể, logit | **103,2** | 107,4 | 109,2 | **1** |

(*) Thành phần k=2 trên thang thô: trọng số 0,58 quanh trung bình 99,67 (SD 0,54) và trọng số 0,42
quanh 51,4 (SD 25,5). Trên thang logit, k=2: 0,64 quanh logit 5,53 (≈ F1 99,6 %) và 0,36 quanh
logit −0,25 (≈ F1 44 %).

### 2.4 Điều rút ra

* **Trên 75 bản ghi CinC, phân bố F1 không phải một mode.** Dip test bác bỏ đơn cực trên hai trong
  ba thang (và sau khi bỏ 7 bản nhãn xấu), BIC bác bỏ một thành phần trên cả ba thang một cách áp đảo.
  Khoảng trống lớn nhất là **10,37 điểm, giữa F1 = 65,12 và F1 = 75,48**, với 24 bản ghi nằm dưới.
* **Trên 22 chủ thể, KHÔNG có bằng chứng lưỡng cực.** Dip p = 0,85–0,95; BIC ưu tiên **một** thành
  phần trên thang logit. Với n = 22 và 3 điểm ở cực dưới, kiểm định lưỡng cực đơn giản là **không đủ
  công suất**. Câu "ba bản ghi khó" ở mức 22 chủ thể vẫn **chỉ là ba điểm**, không phải một mode.
* **Một phần đáng kể của cực dưới trên CinC là lỗi chọn kênh, không phải độ khó bản ghi.** Trên kênh
  tốt nhất (oracle) dip test không còn có ý nghĩa (p = 0,59 logit; p = 0,95 thô), trung bình F1 tăng
  79,40 → 86,87 và số bản ghi F1 < 50 giảm 16 → 8. Ngược lại, trên `lead0` cố định dip cực mạnh
  (p < 1e−5). **Vậy "lưỡng cực" ở đây là tính chất của *đường ống một kênh có quy tắc chọn kênh*,
  chứ không được chứng minh là tính chất của *bài toán*.**

---

## 3. Câu hỏi 3 — Lưỡng cực làm sai lệch kết luận bao nhiêu?

Nhóm khó được chia bằng **điểm cổng từ chối** (`analysis/gate22_results.json`, `analysis/gate22_cinc.json`)
— tiêu chí **không nhìn nhãn lúc suy luận**. Trên 22 chủ thể, ba điểm cổng thấp nhất là **B2_03,
B1_06, B1_07** — trùng khít với ba bản ghi khó, và cũng trùng với ba fSNR thấp nhất (hai tiêu chí
cho **cùng một nhóm**, nên bảng dưới không đổi khi đổi tiêu chí). Trên CinC 75, nhóm khó = 25 bản
ghi điểm cổng thấp nhất (Spearman điểm cổng vs F1 = 0,810, p = 1,3e−18).

### 3.1 Bảng hiệu ứng (điểm F1)

| So sánh | Toàn bộ mẫu | Nhóm DỄ | Nhóm KHÓ | n dễ / khó |
|---|---|---|---|---|
| RelyFetal 1 kênh − Power-MF 4 kênh (22) | −1,27 [−3,07; +0,25] | **+0,27** [−0,02; +0,48], 18 thắng/1 thua, p = 0,0012 | **−11,05** [−12,88; −9,77] | 19 / 3 |
| Dải 10–60 − dải 1–45 Hz trên TCN (22) | +2,44 [−0,04; +6,29] | **−0,07** [−0,21; +0,04], 6 thắng/7 thua/6 hoà | **+18,27** [+8,15; +37,83] | 19 / 3 |
| m22 − m5 (CinC 75) | +8,18 [+5,54; +11,04] | +4,59 [+2,04; +7,69] | +15,38 [+10,58; +20,62] | 50 / 25 |
| m22 − m12 (CinC 75) | +5,06 [+3,11; +7,27] | +1,55 [+0,76; +2,48] | +12,08 [+7,54; +16,99] | 50 / 25 |

Trên thang F1, bức tranh rất rõ: hiệu ứng ở nhóm khó lớn hơn nhóm dễ **41 lần** (RelyFetal vs PMF4),
**280 lần** (dải lọc), 3,3 lần và 7,8 lần (thêm dữ liệu).

### 3.2 ĐỐI CHỨNG BẮT BUỘC — đây có phải chỉ là hiệu ứng trần?

Trên nhóm dễ, cả hai phương pháp đều đã ở 99–100, nên **dư địa** (100 − F1 của phương pháp đối chiếu)
chỉ còn 0,65–0,77 điểm, trong khi ở nhóm khó dư địa là 3,7–27,9 điểm. Hiệu số **buộc phải** nhỏ.
Vì vậy chúng tôi làm lại toàn bộ bảng trên **thang logit**, nơi trần 100 không còn tồn tại:

| So sánh | Nhóm DỄ (điểm F1) | Nhóm KHÓ (điểm F1) | **Nhóm DỄ (logit)** | **Nhóm KHÓ (logit)** |
|---|---|---|---|---|
| RelyFetal − Power-MF 4 kênh | +0,27 | −11,05 | **+1,20** [+0,76; +1,64] | −3,31 |
| Dải 10–60 − dải 1–45 Hz | −0,07 | +18,27 | **−0,04** [−0,24; +0,14] | +1,34 |
| m22 − m5 (CinC 75) | +4,59 | +15,38 | **+1,20** [+0,74; +1,71] | **+0,72** |
| m22 − m12 (CinC 75) | +1,55 | +12,08 | **+0,78** [+0,42; +1,15] | **+0,59** |

**Hai kết luận trái ngược nhau rơi ra từ bảng này:**

1. **Hiệu ứng dải lọc thật sự tập trung.** Trên thang logit, nhóm dễ vẫn bằng 0 (−0,04, KTC ôm 0)
   còn nhóm khó +1,34. Trần không giải thích được điều này. Với **số kênh** cũng vậy về mặt *dấu*:
   trên nhóm dễ mạng một kênh **hơn** Power-MF 4 kênh (+1,20 logit, KTC không ôm 0, 18 thắng/1 thua,
   p = 0,0012), trên nhóm khó thì kém hẳn (−3,31 logit) — tức đây là **đảo dấu**, không phải "không
   quan trọng ở nhóm dễ".
2. **Hiệu ứng "thêm dữ liệu huấn luyện" KHÔNG tập trung.** Trên thang logit, m22 − m5 là +1,20 ở nhóm
   dễ và **+0,72** ở nhóm khó; m22 − m12 là +0,78 và **+0,59**. Nghĩa là thêm dữ liệu giúp **đều đặn
   trên mọi bản ghi**, thậm chí giúp nhiều hơn (theo tỉ lệ lỗi) ở nhóm dễ. Con số "+15,38 vs +4,59 điểm"
   trong bảng §3.1 **hoàn toàn là hệ quả của trần 100**.

> **Vì vậy phát biểu gốc "TOÀN BỘ hiệu ứng của MỌI lựa chọn thiết kế tập trung ở thiểu số khó" là SAI.**
> Phát biểu đúng: *hiệu ứng của lựa chọn tiền xử lý (dải lọc) và của số kênh tập trung ở thiểu số khó
> và còn đảo dấu; hiệu ứng của lượng dữ liệu huấn luyện thì không.* Khi báo cáo bằng F1 trung bình,
> cả hai loại trông giống hệt nhau — và đó chính là vấn đề của thước đo.

### 3.3 Công suất thống kê — cần bao nhiêu chủ thể?

Mô phỏng Monte-Carlo (4 000 lần/điểm, alpha = 0,05, hai phía): mỗi chủ thể là "người mang" với xác
suất 1/7; người mang có hiệu ứng N(14; (0,5·14)²) điểm để hiệu ứng trung bình toàn mẫu đúng bằng
**2 điểm**; người không mang có hiệu ứng 0. Nhiễu nền N(0; σ²) với **σ = 0,290 điểm lấy từ chính dữ
liệu** (độ lệch chuẩn hiệu số dải lọc trên 19 chủ thể nhóm dễ).

| n chủ thể | Công suất t-test ghép cặp | Công suất Wilcoxon |
|---|---|---|
| 22 | 0,22 | 0,14 |
| 40 | 0,66 | 0,27 |
| **50** | **0,84** | 0,35 |
| 80 | 0,99 | 0,50 |
| **160** | 1,00 | **0,80** |
| 300 | 1,00 | 0,98 |

* **n ≈ 50 chủ thể** cho công suất 0,80 nếu dùng t-test ghép cặp.
* **n ≈ 160 chủ thể** nếu dùng Wilcoxon — và Wilcoxon (hoặc kiểm định dấu) chính là thứ lĩnh vực này
  hay dùng vì phân bố F1 lệch. Kiểm định thứ hạng **vứt bỏ đúng thông tin cần thiết** khi hiệu ứng
  tập trung vào thiểu số: với 6/7 chủ thể hiệu số gần 0, thứ hạng của họ là nhiễu thuần tuý.
* Để đối chiếu: **nếu cùng hiệu ứng trung bình 2 điểm nhưng trải đều trên mọi chủ thể, n = 22 đã cho
  công suất 1,00** với cả hai kiểm định.

> Đây là con số có giá trị thực tế: **một ablation 2 điểm trên 20–30 chủ thể, báo cáo bằng Wilcoxon,
> có xác suất phát hiện dưới 20 %** nếu hiệu ứng tập trung. Điều này giải thích được vì sao văn liệu
> đầy những ablation mâu thuẫn nhau mà không cần giả định ai làm sai.

---

## 4. Câu hỏi 4 — Đối chứng trung thực, có cách giải thích tầm thường nào không?

### 4.1 Có phải chỉ là ba bản có nhãn tệ nhất? — **KHÔNG**

| Bản ghi | Nguồn nhãn | n_ref | nhịp chưa duyệt (cờ 0) | F1 | F1 chỉ trên nhịp đã duyệt |
|---|---|---|---|---|---|
| **B1_06** | gián tiếp (B1) | 2 889 | 10 (0,35 %) | 89,45 | **89,53** |
| **B1_07** | gián tiếp (B1) | 3 114 | 18 (0,58 %) | 86,56 | **86,72** |
| **B2_03** | trực tiếp (điện cực da đầu) | 716 | 0 | 79,72 | — |
| B1_09 | gián tiếp (B1) | 2 866 | **50 (1,74 %)** | **99,07** | 99,58 |
| B1_08 | gián tiếp (B1) | 2 911 | 14 (0,48 %) | 99,83 | 99,88 |

Chủ thể có tỉ lệ nhịp chưa duyệt **cao nhất** là B1_09 (1,74 %) và nó đạt **99,07**. Tỉ lệ cờ-0 của
ba bản khó không khác 19 bản còn lại (p Mann–Whitney = 0,28). Loại bỏ mọi nhịp chưa duyệt làm F1 của
B1_06 và B1_07 **tăng đúng 0,08 và 0,16 điểm** — không đi đâu cả. **Chất lượng nhãn không giải thích.**

### 4.2 Có phải ba bản dài nhất / ngắn nhất? — **KHÔNG**

Chỉ có hai độ dài trong mẫu: 300,0 s (ADFECGDB + Silesia B2) và 1 197,8 s (Silesia B1). Ba bản khó
gồm **một bản 300 s và hai bản 1 197,8 s** — nằm ở cả hai phía. p Mann–Whitney = 0,47.

### 4.3 Có phải cùng một nguồn dữ liệu? — **KHÔNG, và đây là điểm mạnh nhất của giả thuyết**

| | Tập con | Bối cảnh | Độ dài | Quy trình gán nhãn |
|---|---|---|---|---|
| **B2_03** | Silesia B2 | chuyển dạ | 5 phút | trực tiếp, điện cực da đầu |
| **B1_06** | Silesia B1 | thai kỳ | 20 phút | gián tiếp, khử ECG mẹ + chuyên gia duyệt |
| **B1_07** | Silesia B1 | thai kỳ | 20 phút | gián tiếp, khử ECG mẹ + chuyên gia duyệt |

Ba bản ghi khó **không cùng tập con, không cùng bối cảnh lâm sàng, không cùng độ dài, không cùng quy
trình gán nhãn**. Cả ba đường bằng chứng độc lập (đối chuẩn Power-MF, khảo sát dải lọc, cổng từ chối)
cùng trả về đúng ba bản này dù ba đường dùng ba mô hình / ba cách chia fold khác nhau. Đây là lập
luận mạnh nhất chống lại "trùng hợp một tập con".

### 4.4 Bỏ ba bản đó ra, có "ba bản khó mới" không? — **KHÔNG**

19 bản còn lại: F1 từ 97,05 đến 100,00, trung bình 99,50, SD 0,84. Dip test p = 0,90 (thô) / 0,74
(logit); BIC ưu tiên **một** thành phần (103,2 vs 107,4). Khoảng trống lớn nhất còn lại chỉ **1,29
điểm** (giữa 97,61 và 98,90), so với **7,60 điểm** khi còn cả 22 (giữa 89,45 và 97,05).

> Ở mức 22 chủ thể, **đuôi dưới không liên tục — có một khoảng trống thật.** Đây là bằng chứng ủng hộ
> giả thuyết, nhưng nó là bằng chứng về **hình dạng của 22 điểm**, không phải một kiểm định có ý nghĩa
> thống kê (xem §2.4).

Trên CinC 75, phép kiểm này **cho kết quả ngược lại một phần**: cắt 24 bản ghi dưới khoảng trống lớn
nhất, 51 bản còn lại vẫn có một khoảng trống 7,86 điểm (giữa 85,82 và 93,68) và dip test p = 0,52.
Tức trên mẫu lớn, đuôi dưới **có cấu trúc phân tầng liên tục hơn** là hai cục rời.

---

## 5. NHỮNG GÌ KHÔNG CHỨNG MINH ĐƯỢC

1. **Không tìm được cơ chế.** Không có đại lượng vật lý nào tách ba bản khó khỏi 19 bản còn lại với
   một biên có ý nghĩa. `fsnr_db` xếp đúng thứ hạng 1-2-3 nhưng biên hạng 3→4 là **0,005 dB** và có
   phản ví dụ trực tiếp (B1_08: cùng fSNR, F1 99,83). Sau hiệu chỉnh Bonferroni cho 45 phép so sánh,
   `fsnr_db` **không** còn liên hệ có ý nghĩa với F1 (p = 0,0121 > 0,0011).
2. **Không chứng minh được bài toán lưỡng cực.** Bằng chứng lưỡng cực chỉ có trên CinC 75, phụ thuộc
   thang đo (p = 0,175 trên thang thô), và **biến mất trên kênh oracle** — nên nó có thể chỉ là tính
   chất của quy tắc chọn kênh PSD mù nhãn, không phải của bài toán. Trên 22 chủ thể không có bằng
   chứng nào.
3. **"Toàn bộ hiệu ứng tập trung ở nhóm khó" bị bác bỏ cho trục dữ liệu huấn luyện.** Sau khi bỏ trần
   (thang logit), m22−m5 và m22−m12 cho hiệu ứng **lớn hơn ở nhóm dễ**. Phát biểu chỉ còn đúng cho
   dải lọc, và với số kênh thì nó là đảo dấu chứ không phải tập trung.
4. **Ba bản ghi vẫn là ba bản ghi.** Mọi con số về "nhóm khó" ở mức 22 chủ thể (−11,05; +18,27) đều
   là trung bình của **n = 3**; KTC bootstrap của chúng rất rộng (+8,15 đến +37,83 cho dải lọc) và
   Wilcoxon với n = 3 không thể cho p < 0,25 dù dữ liệu có hoàn hảo đến đâu.
5. **Tiêu chí chia nhóm không độc lập về mặt thông tin.** `gate_score` không nhìn nhãn lúc suy luận
   nhưng **được huấn luyện để dự đoán F1 đoạn**. Dùng nó chia nhóm rồi kết luận "hiệu ứng tập trung ở
   nhóm điểm thấp" có nguy cơ lập luận vòng; ta giảm nhẹ bằng cách kiểm tra rằng tiêu chí fSNR (độc
   lập với cổng) cho **đúng cùng ba chủ thể**, nhưng fSNR lại dùng nhãn.
6. **Tuần thai không đo được.** Siêu dữ liệu máy đọc được của cả ADFECGDB lẫn Silesia (file .hea /
   .ecg / .txt trong repo) **không chứa tuần thai**; các bảng "Online-only Table 1–4" của Silesia là
   PDF và chưa được trích. Yếu tố này trong đề bài **bỏ trống, không suy đoán**.
7. **Chỉ một hạt giống, một cấu hình fold.** Khảo sát dải lọc (`pilot_evidence/band_tcn.json`) chạy
   seed 0, 3 fold, 4 epoch. Toàn bộ §3 phụ thuộc vào một lần chạy đó cho trục dải lọc.
8. **Thí nghiệm dải lọc chưa xong** khi viết tài liệu này (dải 0.5–100 chưa có). Mọi kết luận về dải
   lọc chỉ dựa trên 10–60 vs 1–45 (và 3–90 để tham khảo).

---

## 6. Khuyến nghị (suy luận, không phải fact)

1. **Ngừng báo cáo F1 trung bình theo bản ghi làm số chính.** Thay bằng: (a) trung vị + phân vị 10/25,
   (b) số bản ghi dưới ngưỡng lâm sàng (F1 < 95 / < 80), (c) hiệu ứng trên **thang logit** để trần 100
   không nuốt mất hiệu ứng thật trên nhóm dễ.
2. **Báo cáo mọi ablation tách theo nhóm dễ/khó**, với tiêu chí chia công bố trước và không nhìn nhãn.
3. **Cỡ mẫu:** với ablation 2 điểm và nghi ngờ hiệu ứng tập trung, cần ~50 chủ thể (t-test ghép cặp)
   hoặc ~160 (Wilcoxon). Dưới 30 chủ thể thì một kết quả "không có ý nghĩa thống kê" **không nói lên
   điều gì**.
4. **Điều tra quy tắc chọn kênh trước khi điều tra độ khó bản ghi.** Trên CinC, chuyển từ kênh PSD
   sang kênh oracle nâng F1 trung bình 79,40 → 86,87 và làm tan phần lớn cực dưới. Đây có vẻ là hướng
   có đòn bẩy lớn nhất — và là một giả thuyết cần kiểm chứng riêng, chưa được chứng minh ở đây.

---

## 7. Nguồn số (mọi con số truy ngược được)

| Tệp | Dùng cho |
|---|---|
| `analysis/luongcuc_feat.json` | 22 đại lượng tín hiệu, §1 (sinh bởi `analysis/luongcuc_feat.py`) |
| `analysis/luongcuc_results.json` | toàn bộ §1–§4 (sinh bởi `analysis/luongcuc.py`) |
| `baselines/powermf_fair_stats.json` | F1 RelyFetal / Power-MF 1 kênh / 4 kênh, 22 chủ thể |
| `pilot_evidence/band_tcn.json` | F1 từng dải lọc trên chính TCN, 22 chủ thể |
| `analysis/gate22_results.json` | điểm cổng từ chối mức bản ghi, `maternal_lock` |
| `analysis/gate22_cinc.json` | điểm cổng zero-shot trên 75 bản ghi CinC |
| `benchmark_dpss/eval_cinc75.json` | F1 mức bản ghi m22 / m5 / oracle / lead0 / mean4 trên CinC 75 |
| `benchmark_dpss/eval_12_cinc.json` | F1 mức bản ghi m12 trên CinC 75 |
| `benchmark_dpss/eval_22.json` | kênh PSD, fold, siêu dữ liệu, F1 chỉ trên nhịp đã duyệt |

Hạt giống 0, bootstrap 10 000 lần, mô phỏng công suất 4 000 lần mỗi điểm.
