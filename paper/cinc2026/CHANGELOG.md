# CHANGELOG — bản thảo CinC (`paper/cinc2026/main.tex`)

## 2026-09-12 — Viết lại cho CinC 2027 trên 60 bản CinC sạch (sau docs/nhat_ky/THAMDINH_VONG7.md)

**Vì sao viết lại.** Phản biện V2 phán bản trước "phải bỏ": còn số 75 bản CinC (nhiễm 15 bản sao ADFECGDB),
hạn CinC 2026 đã qua (Madrid 20–23/9/2026). Đích mới: **CinC 2027**. Thư mục giữ nguyên tên; tiêu đề đổi thành
*"How Much of Multi-Lead Fetal QRS Detection Does One Lead Recover? A Controlled Audit on 22 Women and
60 Cross-Recorder Records"*. Sao lưu bản cũ: `main.tex.bak_v75`, `refs.bib.bak_v75`.

**Biên dịch:** `pdflatex → bibtex → pdflatex ×2` từ thư mục sạch: **4 trang**, 0 lỗi `^!`, 0 overfull, 0 `??`,
0 số đã rút trong `pdftotext`, 0 từ cấm (novel / first / state-of-the-art / SOTA / pre-registered / discovered /
all 75). PDF xuất ra `docs/CinC2027_RelyFetal.pdf`; `docs/CinC2026_RelyFetal.pdf` đã xoá.

### Nguồn sự thật của từng con số (mọi số trong bài truy về JSON)

| Mục trong bài | Con số | Tệp JSON |
|---|---|---|
| Bảng 1 (m5/m22, PSD, 4 kênh) | 99,21 / 97,45 / 99,40 / 98,69; 95,87 / 93,73 / 96,82 / 94,50; 93,30 / 91,31 / 97,15 / 97,01; 95,46 / 93,47 / 97,56 / 96,59; KTC [88,4; 99,8] [84,9; 99,4] [55,4; 72,5] | `benchmark_dpss/eval_22.json → comparison`, `benchmark_dpss/silesia_eval.json → summary`, `analysis/boot_ci_table1.json` |
| Bảng 2 Power-MF 3 cột | 99,01 / 92,37 / 99,40; 97,90 / 87,28 / 96,82; 99,40 / 83,48 / 97,15; 98,83 / 86,71 / 97,56; Δ₄ −1,27 [−3,08; +0,27] p 0,156; Δ₁ +10,85 [+6,80; +15,40] p 4,8e-07; PMF1−PMF4 −12,12 [−18,27; −6,90], thua 21/22 | `baselines/powermf_fair_stats.json → so_sanh` |
| Tỉ lệ lấy lại | 89,5 % KTC [81,4; 103,2], jackknife 88,6–93,4 | `analysis/recovery_ratio.json` |
| Kiểm chứng cổng chuyển | B1 99,40 ± 0,51 (ta) vs 99,46 (tác giả) | `baselines/powermf_fair_stats.json → per_subject (pmf4, B1)`, `baselines/powermf_published.json → sets.b1_powermf` |
| CinC 60 sạch, hàng Power-MF 1 kênh | 55,97; +18,32 [+13,4; +23,6] | `benchmark_dpss/eval_cinc60_sach.json → powermf_1ch.60_sach` |
| 15 bản sao | a03–a05, a08, a12–a15, a17, a19, a20, a22–a25; NCC 1,0000; ΔRR 0,0 ms; 60 bản còn lại ≤ 0,62; thổi phồng 3,27–7,18; 99,87 | `benchmark_dpss/eval_cinc60_sach.json → meta.leak_records`, `analysis/dulieu_results.json → chong_lan`, `survey/facts_phase4.json → A`; 99,87 tính lại từ `benchmark_dpss/eval_cinc75.json` (15 bản, m22 PSD) |
| Bảng 3 CinC-60 | PSD 64,04 → 74,28 (+10,24 [7,13; 13,60], p 3,5e-10, 52/3), ≥90 27→33, <50 22→16, trung vị 95,07; mean4 56,00 / 67,69; oracle 72,76 / 83,60; PSD−oracle 9,32 [5,10; 14,15], trúng 17/60; 53 bản 64,19 → 75,27 (+11,08, p 4,4e-09) | `benchmark_dpss/eval_cinc60_sach.json → variants.60_sach`, `variants.53_sach_loai_7_nhan_sai`; `survey/facts_phase4.json → A` |
| Bảy quy tắc chọn kênh | gate 80,72 (+6,44 [2,49; 11,10], p 0,010, p_Holm 0,051, 16/37/7); gate4 81,01 (+6,72, p_Holm 0,015); rrcv 80,00 (+5,72, p_Holm 0,41); peakprob 82,01 (+7,73 [3,82; 12,41], p 5,6e-04, p_Holm 0,0039, 19/35/6, <50: 9, 82,9 % dư địa, không bản nào mất quá 3,90) | `analysis/dulieu_results.json → chon_kenh_60_sach.bang`, `survey/facts_phase4.json → B` |
| Logit 22 chủ thể | gate dẫn 2/3 cách kép; peakprob hạng 3, +0,13 [−0,04; +0,41]; 4 quy tắc đầu cách 0,04, dư địa 1,08 | `analysis/xacnhan_results.json → viec3_logit_22`; `docs/nhat_ky/THAMDINH_VONG6.md` VIỆC 6 |
| Không có bộ thứ ba | NIFEADB / NInFEA / nifecgdb / set-b không nhãn fQRS | `analysis/xacnhan_results.json → viec2_bo_thu_ba` |
| Bảng 4 kiến trúc | tham số, RF, F1, ΔF1, Δlogit, T/H/B, TOST/Holm cho 7 mô hình | `analysis/kientruc_results.json → table, comparisons, holm_wilcoxon, holm_tost` |
| Dải lọc trên TCN | +2,44 [−0,04; 6,29] kênh PSD; −0,07 [−0,51; 0,39] TB 4 kênh | `pilot_evidence/band_tcn_stats.json → so_sanh_voi_1_45` |
| Thích nghi miền (60 sạch) | notch +0,25 [−0,25; +1,08] p 0,70; self-training −0,67 [−1,11; −0,29]; AdaBN −1,58 [−2,50; −0,73]; TENT −2,43 [−3,64; −1,35] | tính từ `adapt/adapt_results.json → per_record_cinc` lọc 60 bản sạch (bootstrap 10 000, seed 0). **Lưu ý:** README ghi self-training −0,68; giá trị từ JSON là −0,6746 → bài ghi −0,67 |
| Mô phỏng dịch chuyển | 3 dịch chuyển (60 s, 10,13 bit, điện lưới 60 Hz ×1,64) mất 0,01 điểm | `adapt/adapt_results.json → mo_phong_dich_chuyen` |
| Phép thử nhìn thấy | âm tính giả 18,0 % [12,1; 25,0] | `analysis/xacnhan_results.json → viec4_phep_thu_nhin_thay.ti_le_am_tinh_gia.cinc60|psd` |
| Cổng từ chối LOSO | AUROC gộp 0,965 [0,857; 0,992]; trong bản ghi 0,934 [0,872; 0,981] (11 chủ thể); 3 890 đoạn, 5,40 % xấu; B2_03 / B1_07 / B1_06 hạng 1–3 | `analysis/gate22_results.json` |
| Seed | 97,56 vs 97,59, +0,03 [−0,18; +0,34], lệch lớn nhất 2,81 (B2_03) | `analysis/xacnhan_results.json → viec5_seed` |
| STV | chệch +0,33 ms, LoA [−0,89; +1,55] (ADFECGDB); +20,50 ms (mẫu 10 bản CinC cũ, nêu rõ là mẫu cũ) | `analysis/clinical_results.json → summary`, `analysis/CLINICAL.md` |
| Trong miền PSD vs oracle | ≤ 1,90 điểm | `README.md` (ADFECGDB 0,02 / B2 0,66 / B1 1,90 từ `benchmark_dpss/eval_22.json`) |

### Đã bỏ khỏi bài (so với bản `main.tex.bak_v75`)

* Toàn bộ **phân rã ba tầng** (+11,00 dải lọc trên GBM 300 ms; +4,49; +0,41; 80,06 → 91,06; 92,67 → 97,16;
  92,49 → 92,90; 18,89; 72,17) — +11,00 đã rút với TCN; các số khác đo trên 5 chủ thể, không còn chỗ.
* **Bảng kiến trúc cũ "8 họ"** (92,43–90,90; −2,95; +0,73; "0/7 tương đương") — thay bằng Bảng 4 (22 chủ thể, logit).
* Các baseline cổ điển TS / TS-PCA / Prominence (78,96 / 91,05 / 86,39; 11,06; 18,49; 96,74; 2,47) — bỏ vì hết chỗ,
  Power-MF là so sánh cùng bộ chấm duy nhất còn lại.
* Cổng cũ (AUROC 0,929 / 0,721; 61,96 / 69,40; tô-pô 0,566 / 0,905) — thay bằng cổng LOSO 22 chủ thể.
* Câu rút lại các bản nháp nội bộ (59,15 / 69,31 / 77,34 / 90,34 / 71,21 / 79,40 / 86,87) — không thuộc bài nộp.
* "Fixed lead 0 (post hoc, withdrawn)" 48,43 / 61,78 — bỏ hàng.
* Mọi chữ "first / novel / SOTA / pre-registered / discovered the leak".

### Đã thêm

* `refs.bib`: `li2018` (AdaBN, DOI 10.1016/j.patcog.2018.03.005 — xác minh Crossref) và `wang2021` (TENT, ICLR 2021,
  arXiv:2006.10726 — xác minh trang arXiv; không có DOI). `silva2013` và `clifford2014` đã có từ vòng 7.
* Mục 2.4 "Lead rules": phát biểu chính thức theo `docs/nhat_ky/THAMDINH_VONG6.md` VIỆC 6 — kế hoạch viết trước khi chạy CinC
  nhưng sau khi có F1 từng kênh, không neo bên thứ ba → "written plan and nothing stronger".
* Mục 3.4: kiến trúc báo cáo trên **cả F1 lẫn logit**; cnn_wide hoà trên F1, kém trên logit.
* Mục 3.5 + Thảo luận: 4 phương pháp thích nghi miền thất bại; **không** kết luận "thiếu tín hiệu" (âm tính giả 18 %).
* Limitations (vii): cổng từ chối chưa chấm lại trên 60 bản sạch; số cổng trên 75 bản đã rút.

---

> **Báo cáo vòng cũ — giữ để truy vết, KHÔNG phải trạng thái hiện hành.** Nhiều con số trong tệp này đã rút
> (mẫu 10 bản CinC; 75 bản CinC nhiễm 15 bản sao ADFECGDB; Power-MF cổng chuyển hỏng; +11,00 dải lọc; "8 kiến
> trúc"; "mô hình không phải nút thắt"; "Physiological Measurement là Q1"). Số hiện hành: `README.md` mục
> *Retractions* và `survey/facts_phase4.json`.


## 2026-09-12 — Vòng 7 (R3): CinC 2013 chuyển sang 60 bản sạch; chồng lấn set-a ↔ ADFECGDB ghi đúng nguồn

* Mục 3.3, Bảng 3, hàng CinC trong Bảng 1 và 2, tóm tắt, thảo luận, kết luận: mọi số 75 bản (71,21 / 79,40 /
  86,87 / 74,09 / 69,33 / 80,70 / +8,18 / +7,47 / 62,82 / +16,58) **rút**; thay bằng 60 bản sạch: m5 64,04 →
  m22 74,28 (+10,24 [7,13; 13,60], p = 3,5e-10), oracle 83,60, PSD kém oracle 9,32, Power-MF 1 kênh 55,97
  (hiệu +18,32 [13,4; 23,6]), peakprob 82,01 (hậu kiểm, giả thuyết), 53 bản 75,27
  (`benchmark_dpss/eval_cinc60_sach.json`, `analysis/dulieu_results.json`).
* Mục 2.1 Data: chồng lấn set-a ↔ ADFECGDB ghi là **ban tổ chức đã ghi nhận** (thêm `silva2013` vào
  `refs.bib`; trích cảnh báo của Clifford 2014); nhóm chỉ định danh 15 bản bằng đo lường.
* Thêm: bốn phương pháp thích nghi miền thất bại; phép thử nhìn thấy âm tính giả 18 % nên không kết luận
  được mô hình có phải nút thắt.
* Cắt gọn để giữ **4 trang** (lề 2,0/1,75 cm; rút ngắn đoạn Power-MF port, hạn chế, kết luận).


## 2026-09-12 — Vòng B3: RÚT LẠI mốc Power-MF cũ, thay bằng bảng 3 cột

**RÚT LẠI CÔNG KHAI.** Bảng 2 và mục 3.2 của vòng B2 (ở dưới) dựa trên một bản chạy
Power-MF **hỏng**. Mọi con số sau đây bị rút và không được trích dẫn lại:

| Con số đã rút | Xuất hiện ở |
|---|---|
| 94,87 / 97,61 / +2,74 [−1,75; +8,64] (18 bản ghi) | Bảng 2 vòng B2 |
| 98,38 / 97,33 / −1,06 [−3,04; +0,40] (16 bản ghi) | Bảng 2 + tóm tắt + Kết luận vòng B2 |
| 99,05 (ADFECGDB) / 98,90 (B1) / +0,35 / −3,27 | Bảng 2 vòng B2 |
| "6 bản ghi B1 là giới hạn của phương pháp"; "2 bản ghi nửa nhịp" | mục 3.2 vòng B2 |
| Giả thuyết "`ms_minpeakdistance` = 340 ms quá sát nhịp thai" | mục 3.2 vòng B2 |

**Nguyên nhân thật** (chẩn đoán của A2, `baselines/BASELINES.md` mục 1.2): `findpeaks`
của gói `signal` trong Octave cài `MinPeakDistance` bằng ma trận khoảng cách đôi một,
O(k²) bộ nhớ, nên tràn chỉ số trên 6 bản ghi B1 dài (2 395 600 mẫu sau nội suy ×4).
MATLAB — nền tảng của tác giả — giải bằng thuật toán tham O(k log k). **Đây là lỗi cổng
chuyển của nhóm ta, không phải tính chất của Power-MF.** Bản vá P7
(`baselines/octave/findpeaks_mpd.m`) tái lập ngữ nghĩa MATLAB bằng danh sách liên kết đôi,
O(k), đúng 48/48 trường hợp kiểm chứng. Giả thuyết 340 ms bị bác bỏ bằng đo RR thật:
0,00 % khoảng RR của B1_01 ngắn hơn 340 ms (`baselines/powermf_rr_diag.json`).

**Kiểm chứng ngoài:** sau vá, Power-MF đạt 99,40 ± 0,51 trên 10 bản ghi B1, so với
**99,46 do chính tác giả công bố** — lệch 0,06 điểm.

### Bảng 2 mới (nguồn: `baselines/powermf_fair_stats.json`, `baselines/powermf_1ch.json`)

Đủ 22 chủ thể, không loại bản ghi nào. Ba cột phương pháp, vì đóng góp đo được là
"một kênh lấy lại bao nhiêu phần lợi ích của tách nguồn đa kênh".

| Tập chủ thể | n | PMF-4 | PMF-1 | Ta | Δ₄ [KTC95] | Δ₁ [KTC95] |
|---|---:|---:|---:|---:|---|---|
| ADFECGDB | 5 | 99,01 | 92,37 | 99,40 | +0,39 [+0,22; +0,60] | +7,02 [+3,84; +9,34] |
| Silesia B2, chủ thể mới | 7 | 97,90 | 87,28 | 96,82 | −1,08 [−4,04; +0,54] | +9,54 [+3,09; +17,9] |
| Silesia B1 | 10 | 99,40 | 83,48 | 97,15 | −2,25 [−5,55; +0,32] | +13,68 [+6,91; +21,3] |
| **Tất cả 22** | **22** | **98,83** | **86,71** | **97,56** | **−1,27 [−3,08; +0,27]** | **+10,85 [+6,80; +15,4]** |
| CinC 2013 set-a | 75 | — | 62,82 | 79,40 | — | +16,58 |

Luận đề trong bài: tách nguồn đa kênh đáng 12,12 điểm F1 cho chính Power-MF
(86,71 → 98,83); mạng đơn kênh lấy lại 10,85 điểm, tức **89,5 %** số đó, bằng **một** kênh.
Kết quả: **không phân biệt được** với Power-MF 4 kênh (−1,27; p = 0,156) và **hơn hẳn**
Power-MF khi bị giới hạn cùng một đạo trình (+10,85; 22/22). Trung vị hiệu số là **+0,23**
và ta thắng **18/22**; trung bình bị kéo âm **chỉ** bởi B1_07 (−12,88), B1_06 (−10,51),
B2_03 (−9,77). Không dùng chữ "SOTA" / "novel" / "first" / "state-of-the-art".

### Các mục khác đã sửa

* **Tóm tắt** và **Kết luận**: viết lại theo luận đề 12,12 / 10,85 / 89,5 %.
* **Limitations**: thêm thẳng 6 mục — (a) trung bình thấp hơn PMF-4 1,27 điểm, KTC chứa 0
  nên không kết luận được ai hơn nhưng **dấu là âm**, (b) ba bản ghi thua nặng nêu đích
  danh B1_07 / B1_06 / B2_03, (c) tầng 1 (+11,00 cho 10–60 Hz) đo trên GBM cửa sổ 300 ms,
  **chưa** trên TCN, thí nghiệm đang chạy, (d) dải 10–60 Hz là của Xu 2026 chứ không phải
  phát hiện của nhóm, (e) dấu vấn nhãn ở mốc thời gian trên B1 (3,25 ms so với 6,50 ms),
  (f) DPSS vẫn là số trích dẫn, chưa chạy lại.
* Không thêm tài liệu tham khảo nào; `refs.bib` **không đổi**.

### Đã cắt để giữ đúng 4 trang

Bảng 2 mới rộng thêm 2 cột và phần 3.2 dài thêm, nên phải cắt:

1. **Bỏ hẳn Bảng 3 cũ (`tab:tiers`, phân rã ba tầng)** — toàn bộ số liệu 80,06→91,06,
   92,67→97,16, 92,49→92,90 và các KTC được giữ nguyên trong **văn xuôi** mục 3.4,
   không mất con số nào.
2. Gọn lại mục 3.5 (cổng từ chối / tô-pô). Các số bị bỏ: ba đối chứng tô-pô trong repo
   (27,42 vs 97,14; H₀ sublevel = prominence; 8/16 đặc trưng đổi dấu), xếp hạng đặc trưng
   (0,970 / 0,915 / 0,904), so sánh 6 đặc trưng tín hiệu (0,666), điểm tại 50 % phủ (84,51)
   và "5/10 bản ghi không có đoạn xấu".
3. Gọn lại mục đọc lâm sàng. Các số bị bỏ: chệch 1,84/1,86 ms (B1/B2), sai số âm lớn nhất
   −0,17 ms, phân bố khoảng trống 88,2 % / 192 s.
4. Gọn văn phần Thảo luận, Phương pháp (Bộ phát hiện, Thí nghiệm, Cổng từ chối),
   phần đóng góp ở Mở đầu, và tóm tắt — chủ yếu cắt chữ.
5. Bỏ Se 97,69 / PPV 97,18 và jitter 3,62 ms của ADFECGDB 4 đạo trình (F1 97,45 vẫn còn);
   bỏ dải ngưỡng theo nếp (0,50–0,80 vs 0,20–0,80), câu chữ "ngưỡng dịch nhiều hơn" vẫn còn.

Danh sách đầy đủ số bị bỏ khỏi `main.tex` (so với `main.tex.bak_b3`, sinh bằng regex
`\d+\.\d+`): 0.09, 0.17, 0.25, 0.35, 0.40, 0.50, 0.64, 0.666, 0.79, 0.80, 0.88, 0.904,
0.915, 0.970, 1.06, 1.14, 1.75, 1.84, 2.74, 3.04, 3.17, 3.27, 3.47, 3.62, 8.64, 9.11,
27.42, 49.8, 50.6, 84.51, 88.2, 94.87, 95.63, 97.14, 97.18, 97.33, 97.61, 97.69, 98.13,
98.38, 98.90, 99.05, 99.48, 99.7, 99.9, 99.92.

Sao lưu bản B2: `main.tex.bak_b3`.

---

## 2026-09-12 — Vòng B2: tích hợp kết quả mới + cắt từ 5 trang xuống 4 trang

Bản trước: 5 trang (vượt giới hạn CinC là 4). Bản này: **đúng 4 trang**, biên dịch
`xelatex → bibtex → xelatex ×2`, **0 lỗi, 0 cảnh báo tham chiếu chưa xác định, 0 hộp
tràn (overfull), 0 dấu `??` trong PDF**.

Sao lưu bản cũ: `main.tex.bak_b2`, `refs.bib.bak_b2`.

---

## 1. THÊM MỚI — Power-MF chạy lại (mục 3.2 + Bảng 2)

Đây là lỗ hổng lớn nhất của bản trước: mọi con số đối thủ đều là **trích dẫn**, không
phải đo. Nay Power-MF (Jaeger 2024, đa kênh) đã được **chạy lại thật** dưới GNU Octave
trên chính các bản ghi của ta và chấm bằng **bộ chấm của ta** (`M.match_events`, ±50 ms).

> ## ⛔ RÚT LẠI TOÀN BỘ MỤC NÀY — 12/09/2026, chiều
>
> Bảng và phát biểu bên dưới (**bắt buộc giữ nguyên để làm hồ sơ**, nhưng **cấm trích dẫn như
> kết quả**) đứng trên một **bản Power-MF còn hỏng**. Nguyên nhân: `findpeaks` của gói `signal`
> trong Octave cài `MinPeakDistance` bằng ma trận khoảng cách đôi một **O(k²)** → tràn bộ nhớ trên
> 6 bản ghi Silesia B1 dài (2.395.600 mẫu sau nội suy ×4). MATLAB — nền tảng của tác giả — dùng
> thuật toán tham **O(k log k)** nên không bao giờ gặp. **Lỗi cổng chuyển của nhóm, không phải
> tính chất của Power-MF.**
>
> Vì bản gốc hỏng, việc "loại 2 bản ghi nghi lỗi" là vá lỗi của nhóm chứ không phải quy tắc khoa
> học, nên **cả hai dòng 16 và 18 bản ghi đều vô nghĩa**. Giả thuyết `ms_minpeakdistance = 340 ms`
> quá sát **cũng đã bị bác bỏ**: 0,00 % khoảng RR của B1_01 dưới 340 ms
> (`baselines/powermf_rr_diag.json`).
>
> **Số đúng nằm ở `baselines/BASELINES.md` và Bảng `tab:pmf` của `main.tex`** (22 chủ thể, ba cột:
> Power-MF 4 kênh 98.83 / Power-MF 1 kênh 86.71 / ta 97.56; Δ₄ = −1.27 [−3.08; +0.27] p = 0.156;
> Δ₁ = +10.85 [+6.80; +15.40]). Kiểm chứng ngoài cho bản vá: ta đo 99.40 trên B1, tác giả công bố
> 99.46 — lệch 0.06.

Thêm mục con `3.2 Against a re-run multi-channel pipeline` và **Bảng 2** — *bảng dưới đây ĐÃ RÚT*:

| ~~Tập chủ thể~~ | ~~n~~ | ~~Power-MF~~ | ~~Ta~~ | ~~Δ (ta − PMF) [KTC95]~~ | ~~thắng~~ |
|---|---:|---:|---:|---|---:|
| ~~ADFECGDB~~ | ~~5~~ | ~~99.05~~ | ~~99.40~~ | ~~+0.35 [+0.09; +0.64]~~ | ~~5/0~~ |
| ~~Silesia B2, chủ thể mới~~ | ~~7~~ | ~~97.61~~ | ~~96.82~~ | ~~−0.79 [−3.17; +0.51]~~ | ~~6/1~~ |
| ~~Silesia B1, cổng chạy được~~ | ~~4~~ | ~~98.90~~ | ~~95.63~~ | ~~−3.27 [−9.11; +0.88]~~ | ~~2/2~~ |
| ~~**Tập khai báo trước**~~ | ~~**16**~~ | ~~**98.38**~~ | ~~**97.33**~~ | ~~**−1.06 [−3.04; +0.40]**~~ | ~~13/3~~ |
| ~~+2 bản ghi nửa nhịp~~ | ~~18~~ | ~~94.87~~ | ~~97.61~~ | ~~+2.74 [−1.75; +8.64]~~ | ~~15/3~~ |

Phát biểu trong bài **đã thay** bằng bản dựa trên 22 chủ thể sau khi vá; phát biểu cũ dưới đây
**đã rút** (con số −1.06 / +0.35 không còn đúng), tuy cách diễn đạt "không phân biệt được, **không**
dùng chữ 'thắng'/'SOTA'" vẫn là chuẩn phải theo:

> ~~*"the single-channel network is **indistinguishable** from the four-channel pipeline
> (−1.06 F1, CI [−3.04; +0.40], p = 0.25), and on ADFECGDB it is ahead by 0.35 points
> with an interval excluding zero … not separable from a published multi-channel one
> on this material, using one electrode pair instead of four — **not that it beats it**."*~~

**Ghi rõ việc loại 2 bản ghi** (yêu cầu 1): B1_01/B1_02 cho Se = 49.8/50.6 với PPV =
99.9/99.7 — **đúng một nửa nhịp**; tham số `ms_minpeakdistance` = 340 ms nằm ngay dưới
RR trung bình 384 ms của B1_01 (1197.8 s / 3120 nhịp). Số đã công bố của chính tác giả
cho hai bản ghi này là 99.92 / 99.48. Bài **nói thẳng** rằng đây là lỗi cổng chuyển của
ta, không phải của phương pháp, và **đang được điều tra**. Tương tự, 3 bản B1 trả về 0
phát hiện và 1 bản chết — cũng khai báo là lỗi cổng chuyển của ta.

Mục Limitations nói thêm: tập so sánh 16/22 chủ thể **không ngẫu nhiên theo độ dài bản
ghi** (hỏng toàn ở bản ghi dài), nên phép so sánh **lệch về phía bản ghi ngắn**; và
Power-MF chạy ở tần số lấy mẫu lại của ta với bộ chấm của ta, **không đồng nhất** với
đánh giá gốc của tác giả.

Nguồn: `baselines/powermf_results.json`, `baselines/powermf_published.json`,
`baselines/powermf_log.txt`, `benchmark_dpss/eval_22.json`.

---

## 2. THAY — CinC 2013: 10 bản ghi → **75 bản ghi** (mục 3.3 + Bảng 3)

Đổi mục `3.3 All 75 CinC 2013 records, and what ten records hid` và thêm **Bảng 3**
(bắt buộc giữ):

| Quy tắc chọn kênh | n | m5 | m22 | Δ [KTC95] | p | ≥90 | <50 |
|---|---:|---:|---:|---|---|---:|---:|
| PSD, **mù nhãn (số chính)** | 75 | 71.21 | **79.40** | +8.18 [5.6; 11.1] | 3·10⁻¹⁰ | 48 | 16 |
| TB 4 kênh | 75 | 64.78 | 74.09 | +9.31 [7.0; 11.8] | 4·10⁻¹¹ | 30 | 17 |
| Kênh 0 cố định (hậu kiểm) | 75 | 58.72 | 69.33 | +10.61 [7.5; 14.0] | 1·10⁻⁸ | 36 | 27 |
| Oracle (dùng nhãn) | 75 | 78.21 | 86.87 | +8.66 [5.9; 11.7] | 1·10⁻⁹ | 53 | 8 |
| PSD, **68 bản ghi** | 68 | 72.08 | **80.70** | +8.62 [5.7; 11.8] | 4·10⁻⁹ | 46 | 14 |

- Bảng 1 (`tab:data`) — hàng CinC đổi từ `10 bản ghi, PSD 59.15 [38.3; 81.0]` thành
  **`75 bản ghi, PSD 71.21 [63.6; 78.4]`**, TB 4 kênh 64.78, ≥90: 42, <50: 22.
  (KTC bootstrap cụm 10 000 lần, seed 0 — tái lập được: `[63.57; 78.44]`.)
- **Bỏ hàng phụ `oracle / fixed lead 0` khỏi Bảng 1** (chuyển vào Bảng 3).
- Báo cáo **cả biến thể 68 bản ghi** (loại a33, a38, a47, a52, a54, a71, a74 — danh
  sách khai báo TRƯỚC khi chạy, nguồn Behar/Oster/Clifford qua `\cite{behar2014}`).
- **Rút lại cả hai con số mẫu 10 bản ghi**, kèm lý do định lượng (yêu cầu 2):
  - dưới quy tắc mù, mẫu 10 bản ghi **bi quan ~12 điểm** (m5 59.15 vs 71.21; m22 69.31 vs 79.40);
  - dưới kênh 0 hậu kiểm, **lạc quan 19–21 điểm** (m5 77.34 vs 58.72; m22 90.34 vs 69.33);
  - trên toàn bộ 75 bản ghi, **kênh 0 hậu kiểm là quy tắc TỆ NHẤT trong bốn quy tắc**,
    kém quy tắc PSD mù 10 điểm — tức chính lựa chọn hậu kiểm sinh ra để "cứu" quy tắc
    PSD lại là lựa chọn tồi nhất khi đo đủ mẫu. Đây là bằng chứng trực tiếp cho luận
    điểm liêm chính của bài.
- **Sửa một tuyên bố cũ đã bị mẫu nhỏ thổi phồng:** khoảng cách "quy tắc mù → oracle"
  ngoài miền **không phải 22.33 điểm mà là 7.47 điểm** trên 75 bản ghi (86.87 − 79.40).
  Bài nay ghi cả hai và nói rõ nó co lại khi mẫu lớn hơn, nhưng vẫn gấp ~4 lần khoảng
  cách trong miền (0.02 / 0.66 / 1.90).
- Mục Discussion đổi theo: mất "khoảng 38 điểm" → **"khoảng 26 điểm"** (97.45 → 71.21).

Nguồn: `benchmark_dpss/eval_cinc75.json` (+ `eval_cinc75_log.txt`).

---

## 3. THÊM — đoạn chỉ số lâm sàng (cuối mục 3.5)

Đoạn `Clinical read-out` mới, đúng tinh thần "trung thực reviewer sẽ đánh giá cao":

- Độ chệch STV: **+0.33 ms** trên ADFECGDB, +1.84 / +1.86 ms trên Silesia B1/B2,
  **+20.50 ms** trên CinC 2013.
- Phân tầng theo F1: |sai số| TB **0.13 ms** khi F1 ≥ 99.5, **25.78 ms** khi F1 < 90.
- **Sai số một chiều**: 25/32 bản ghi đánh giá STV CAO hơn nhãn, sai số âm lớn nhất chỉ
  −0.17 ms — cơ chế: mỗi nhịp sót/thừa làm nhiễu một khoảng RR và nhiễu chỉ cộng thêm.
- Trên các bản ghi cổng chấm "cao": LoA **[−0.39; +0.61] ms**.
- Nêu rõ **chưa có chủ thể trong miền nào có STV nhãn gần vùng ra quyết định**, nên đây
  là *thất bại về độ phân giải*, **không phải** độ nhạy đã đo được (nhắc lại ở Limitations).
- Kết luận in trong bài: dùng được để **theo dõi xu hướng** trên bản ghi đã qua cổng,
  **KHÔNG dùng được làm máy đo STV độc lập**.
- Thêm yêu cầu báo cáo **độ phủ theo THỜI LƯỢNG kèm phân bố khoảng trống**
  (88.2 % thời lượng được trả lời; khoảng trống bị từ chối dài nhất **192 s**).

**Cố ý KHÔNG đưa vào:** ngưỡng TRUFFLE 2.6/3.0 ms và các con số mất tín hiệu CTG
(5–8 % / 9–20 % / 5.3 % / 20 %). `analysis/CLINICAL.md` mục 6.4 ghi rõ chúng do P3
cung cấp và **chưa đối chiếu bản gốc**; đưa vào sẽ là trích dẫn không kiểm chứng được.
Nhờ vậy **không cần thêm tài liệu tham khảo mới nào**.

Nguồn: `analysis/CLINICAL.md`, `analysis/clinical_results.json`.

---

## 4. THÊM — độ ổn định 2 seed (mục 3.1)

Một câu trong 3.1: seed thứ hai của mô hình 22 chủ thể làm F1 từng chủ thể dịch
**trung bình 0.28 điểm** trên 20 chủ thể chung (lớn nhất 2.81), trong khi **ngưỡng từng
fold kém ổn định hơn** (0.50–0.80 so với 0.20–0.80). Cũng nhắc lại trong abstract.

Nguồn: `survey/facts_phase2.json` → `F_on_dinh_2_seed`.

---

## 5. CẮT XUỐNG 4 TRANG — cắt cái gì

**GIỮ NGUYÊN 100 % (theo yêu cầu):** Bảng Power-MF (Bảng 2), Bảng CinC 75 (Bảng 3),
phần phân rã ba tầng (mục 3.4 + Bảng 4), mục Limitations.

Đã cắt / gộp:

| Chỗ | Trước | Sau |
|---|---|---|
| **TDA / tô-pô** | một mục con riêng + đoạn "Why topology failed" trong Discussion + 3 đối chứng kể dài | **2 câu** trong 3.5 ("Topology contributed nothing: … 0.566 … làm AUROC giảm còn 0.905") + 1 câu gộp ba đối chứng, **trỏ về repo** ("Three controls in the repository agree"); trong Discussion còn 1 câu lý do cấu trúc |
| **Bảng baselines cổ điển** (bảng riêng 4 hàng × 5 cột) | bảng | **gộp thành văn xuôi** 6 dòng trong 3.4 (TS 78.96 / TS-PCA 91.05 / Prominence 86.39 / ta 97.45; vẫn giữ cảnh báo KTC paired-t của TS chứa 0) |
| **Mục "Architecture family"** (mục con riêng) | ~13 dòng | **gộp vào 3.4**, 6 dòng, giữ nguyên TOST 0/7 + cnn_m −2.95 + cnn_l +0.73 |
| **Discussion** | 4 đoạn dài (gồm "Why topology failed" riêng) | 4 đoạn ngắn; đoạn tô-pô gộp vào đoạn tổng quát hoá; **thêm** đoạn mới "One channel is not obviously the limitation" |
| Abstract | ~19 dòng | ~17 dòng, viết lại quanh Power-MF + CinC 75 + STV |
| Introduction | liệt kê 4 phương pháp học sâu + câu SQI | liệt kê 3, bỏ câu SQI (andreotti2017 vẫn được trích ở Methods); bỏ trích `huang2025` |
| Methods (Data / Detector / Protocol / Experiments) | — | siết câu, không bỏ thông tin giao thức nào |
| Bibliography | `\footnotesize` | `\scriptsize` |
| Danh mục đóng góp | 3 mục dài | 3 mục, mục 2 đổi thành "so sánh chạy lại", mục 3 thêm "all 75 CinC records" + STV |
| Preamble | `titlespacing` 8/6 pt, `tabcolsep` 3.5 pt, `arraystretch` 1.08, caption skip 4 pt | 6/4 pt, 3.0 pt, 1.05, 3 pt |

Số tài liệu tham khảo in ra: **18 → 15** (`huang2025`, `kiranyaz2023`, `perea2015`
không còn được trích; **vẫn giữ trong `refs.bib`** kèm chú thích nêu lý do).

---

## 6. Kiểm tra liêm chính số liệu

- Script kiểm tra tự động đối chiếu **56 con số mới** trong `main.tex` với JSON gốc:
  **54/56 khớp chuỗi ký tự tuyệt đối**; 2 trường hợp còn lại là KTC bootstrap của hàng
  CinC trong Bảng 1, chạy lại với `default_rng(0)` sạch cho đúng **[63.57; 78.44] →
  [63.6; 78.4]** như in trong bài (lệch nhỏ trong lần chạy đầu chỉ do RNG đã bị tiêu thụ
  trước đó trong cùng script).
- KTC của Bảng 2 lấy đúng theo mốc đã kiểm chứng ngày 12/09. Chạy lại độc lập cho
  [−3.05; +0.40] thay vì [−3.04; +0.40] và [−1.72; +8.68] thay vì [−1.75; +8.64] —
  **chênh lệch ≤ 0.04 điểm, thuần nhiễu Monte-Carlo của bootstrap**, không đổi kết luận.
- Đếm thắng/thua từng nhóm (5/0, 6/1, 2/2, 13/3, 15/3) tính lại từ JSON, **khớp tuyệt đối**.
- Grep toàn văn: **không có** "SOTA", "novel", "first", "state-of-the-art".
- Grep toàn văn: **không còn** con số 59.15 / 69.31 / 90.34 / 77.34 ở vai trò kết quả —
  chúng chỉ còn xuất hiện trong câu **rút lại chúng**.

Cảnh báo còn lại (không sửa, vì sẽ phải bịa dữ liệu): mục `baldazzi2023` in ra
"Springer; 2023. ." — dấu chấm thừa do `vancouver.bst` gặp trường `pages` rỗng; nguồn
khảo sát không ghi số trang nên **không điền**.

---

## 7. Tệp xuất

| Tệp | Trạng thái |
|---|---|
| `paper/cinc2026/main.tex` | đã sửa (4 trang) |
| `paper/cinc2026/refs.bib` | đã sửa (chỉ thêm chú thích về 3 mục nay chưa trích) |
| `paper/cinc2026/main.pdf` | **4 trang**, 0 lỗi, 0 `??` |
| `paper/cinc2026/CHANGELOG.md` | tệp này |
| `paper/cinc2026/main.tex.bak_b2`, `refs.bib.bak_b2` | bản sao lưu trước vòng B2 |

Lệnh biên dịch lại:

```
cd paper/cinc2026
xelatex -interaction=nonstopmode main.tex
bibtex main
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

(`build.bat` vẫn gọi `pdflatex`; phần bình luận đầu `main.tex` đã đổi sang xelatex —
cả hai trình biên dịch đều cho 4 trang.)
