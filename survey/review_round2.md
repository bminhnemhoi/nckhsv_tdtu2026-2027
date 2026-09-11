# Phản biện đối kháng vòng 2 — RelyFetal (bản thảo CinC 2026, mã huấn luyện 22 ca, mã đường cong SNR / hiệu quả mẫu)

Ngày: 11/09/2026. Người phản biện: tác tử K (mặc định hoài nghi; tự đọc mã và JSON, không tin báo cáo).
Nguồn đối chiếu: `survey/facts_verified.json`, `survey/facts_phase1.json`, `benchmark_dpss/*.json`, `baselines/results.json`, `fsqi/results.json`, `pilot_evidence/*.json`, `pilot_evidence/*_log.txt`, `survey/survey_raw.json` (trường `trich_dan`).
Các con số tôi phải **tính lại** (vì không có sẵn trong facts) được lưu tại `survey/review_round2_checks.json`.

Hai tiến trình nền (`train_22.py`, `snr_curve.py`) **không** bị chạy lại; tôi chỉ đọc mã và log.

---

## 0. Bảng tổng hợp vấn đề

| Mức | # | Vấn đề | Vị trí | Trạng thái / cách sửa |
|---|---|---|---|---|
| **NGHIÊM TRỌNG** | — | Không phát hiện con số bịa hoặc kết luận sai so với dữ liệu đo. | — | — |
| TRUNG BÌNH | T1 | PDF "đã biên dịch" nhưng **chưa chạy bibtex**: không có `main.bbl`, toàn bộ 16 trích dẫn hiện `[?]`, không có mục References (main.log cũ dòng 1124 "No file main.bbl"). | `paper/cinc2026/` | **ĐÃ SỬA**: xelatex → bibtex → xelatex ×2. 4 trang, 0 `[?]`, 0 tham chiếu chưa định nghĩa. |
| TRUNG BÌNH | T2 | Hai hình (`fig13_kien_truc_v2.pdf`, `fig9_risk_coverage.png`) toàn nhãn **tiếng Việt** ("Bảng kiến trúc chạy lại…", "mốc", "Cổng từ chối trên CinC 2013", chú giải "Từ chối ngẫu nhiên"…) trong bài tiếng Anh; caption phải chua "(\emph{m\^oc} = reference)" và còn sai dấu (môc). | main.tex:266-270, 305-308 | **ĐÃ SỬA**: vẽ lại bằng tiếng Anh từ đúng JSON nguồn (`figs/make_figs_en.py` → `fig13_arch_en.pdf`, `fig9_risk_coverage_en.pdf`); hình gốc giữ nguyên. Đã kiểm tra bằng mắt: nhãn không bị cắt, giá trị khớp (69,40 / 84,51; 8 kiến trúc đúng thứ tự). |
| TRUNG BÌNH | T3 | Tầng 2 "+4,53 (p<0,001)": Δ = 97,43 − 92,90 lấy từ hai thí nghiệm (train_final vs final_loro), nhưng **không file nào** chứa Wilcoxon cho đúng cặp này; p = 0,0000 trong facts_verified là của cặp khác (seq_loro: short_cnn vs tcn_rf2s). | main.tex:208-209, 226; facts_verified `phan_ra_dong_gop.p_value_ngu_canh` | **Đã kiểm chứng trực tiếp**: Wilcoxon trên 20 (bản ghi × kênh), cnn_dil seed 0 (final_loro_10_60_w75.json) vs TCN (train_final.json): Δ = 4,52, p = 8,8·10⁻⁵, thắng 20/20 (vs trung bình 3 seed: Δ 4,53, p = 1,9·10⁻⁶). Kết luận trong bài đứng vững; **cần** ghi p này vào facts (đã lưu ở review_round2_checks.json). Không sửa bài. |
| TRUNG BÌNH | T4 | "Of the 15.9 points **separating** the naive pipeline from the final model": 15,9 = 11,00 + 4,53 + 0,41 là tổng ba hiệu số đo ở ba thí nghiệm khác nhau (tầng 1 trên 2 đạo trình, tầng 2-3 trên 4 đạo trình); khoảng cách đo thật 80,06 → 97,43 là 17,4. facts_verified đã cảnh báo đúng lỗi trộn này. | main.tex:320 | **ĐÃ SỬA** thành "gained over the three tiers of Table 2". |
| TRUNG BÌNH | T5 | "Three earlier controls" (27,42 / 97,14 / +0,88, p = 0,625) lấy từ bảng 16 kiến trúc cũ: dải 3–90 Hz, **một** bản ghi validation (r08), ngưỡng quét trên chính bản ghi đánh giá (facts_verified `so_sanh_16_kien_truc.canh_bao_nghiem_trong`). Bài không nói giao thức này. | main.tex:311-313 | **ĐÃ SỬA**: thêm "(3–90 Hz pilot, one validation record, threshold swept on it, so optimistic for every entry)". Kết luận không đổi (chênh 70 điểm). |
| TRUNG BÌNH | T6 | Định nghĩa SNR trong `snr_curve.py` lấy P_signal = phương sai **toàn bộ** tín hiệu bụng thô (QRS mẹ áp đảo) → "0 dB" ở đây tương đương khoảng −15…−20 dB so với thành phần thai; và nhiễu được cộng **trước** lọc 10–60 Hz nên nhiễu `bw` (≤1 Hz) bị lọc gần hết: đường bw phẳng (r01 bw −5 dB: F1 99,88) đo **bộ lọc**, không đo mô hình. | snr_curve.py:9-17, 91-94, 185-188 | Chưa vào bài. Khi đưa vào: phải nêu rõ mốc SNR (so với tín hiệu bụng), báo thêm SNR trong dải sau lọc, và không được trình bày "miễn nhiễm bw" như tính chất của mạng. |
| TRUNG BÌNH | T7 | `train_22.py`: B1 stride 2 s vẫn chiếm ≈ 24 k / 33,3 k ≈ 72 % đoạn huấn luyện (log fold 1: 33 332 đoạn), trong khi nhãn B1 **gián tiếp** và 5/10 bản ghi lệch hệ thống 8–12 ms, kèm cả nhịp flag = 0 (line 79). Không phải rò rỉ, nhưng là lựa chọn trọng số dữ liệu có thể dạy mô hình một độ lệch thời gian. | train_22.py:51, 79, 110-118 | Không sửa (đang chạy). Phải khai báo trong bài; kiểm tra `bias_ms` trên test B2/PhysioNet trong `train_22.json` khi xong (script có log). |
| TRUNG BÌNH | T8 | `sample_efficiency.py` k = 1: ngưỡng cố định 0,45 = trung vị 5 ngưỡng fold LORO, mà các ngưỡng đó được chọn trên các bản ghi val **trùng** với bản ghi test của k = 1 → rò rỉ nhẹ một vô hướng. Đường k = 1→2→3 trộn ba quy tắc ngưỡng (cố định / in-sample / val riêng). | sample_efficiency.py:42, 181-203, 211-234 | Script đã khai báo (meta.nguong_k1/k2) và có biến thể phụ. Khuyến nghị: dùng ngưỡng cố định 0,45 làm trục chính cho **cả** k = 3 (hiện thiếu) để đường cong so sánh được. |
| TRUNG BÌNH | T9 | "the lead is often chosen with the test labels" — phát biểu về y văn không có nguồn trong facts/survey. | main.tex:87 | Không sửa; cần trích dẫn cụ thể hoặc bỏ "often". |
| TRUNG BÌNH | T10 | Chưa dùng `cinc.cls` chính thức (ghi ở đầu main.tex). Giới hạn 4 trang chỉ được xác nhận với `article` giả lập; lề/khoảng cách khác có thể tràn trang 5. | main.tex:4-6 | Không sửa được trên máy này; phải kiểm tra lại sau khi thay template. |
| NHẸ | N1 | `\newcommand{\pm}{\ensuremath{\pm}}` → **lỗi LaTeX thật** "Command \pm already defined" (main.log cũ dòng 596), biên dịch chỉ đi tiếp nhờ nonstopmode. | main.tex:34 | **ĐÃ SỬA** (xóa). |
| NHẸ | N2 | Ba bảng tràn cột: Bảng 1 +23,4 pt, Bảng 2 +59,9 pt, Bảng 3 +97,3 pt (≈3,4 cm đè sang cột bên). | main.tex:185-197, 221-230, 245-255 | **ĐÃ SỬA**: rút ngắn chữ (TS + PT, "300 ms window → 4 s per-sample", p chính xác chuyển xuống caption Bảng 3) + macro `\fitwidth` (chỉ co khi rộng hơn cột). Không còn Overfull. |
| NHẸ | N3 | 97,43 ± 4,37 (dòng 177) vs 97,45 ± 2,96 (Bảng 1) vs 97,45 ± 4,44 (Bảng 3) không giải thích. Nguyên nhân đã xác minh: cùng phát hiện, chấm ở 250 Hz (train_final) vs chấm lại ở 1 kHz (all_leads/baselines); chênh trung bình 0,016, tối đa 0,155 điểm. | main.tex:177-178 | **ĐÃ SỬA**: thêm một câu nêu rõ. |
| NHẸ | N4 | "Since the **first** convolutional fQRS detector [Zhong 2018]": survey_raw.json ghi đây là "theo tuyên bố của chính tác giả". | main.tex:79 | **ĐÃ SỬA**: "the convolutional fQRS detector of Zhong et al." |
| NHẸ | N5 | "None holds the protocol fixed" — tuyệt đối hoá. | main.tex:87-88 | **ĐÃ SỬA**: "None of them" (giới hạn trong 4 bài vừa trích). |
| NHẸ | N6 | Tầng 3: Δ = +0,41 là hiệu trung bình 3 seed (92,90 − 92,49) nhưng p = 0,70 là của seed 0 (Δ 0,42; final_loro_log). | main.tex:210-211, 227 | Không sửa (chênh 0,01); ghi chú để nhất quán khi có thời gian. |
| NHẸ | N7 | Tác giả giữ chỗ "[Co-author]", "[Supervisor]". | main.tex:37 | Không sửa (không thuộc thẩm quyền). |
| NHẸ | N8 | `build.bat` dùng pdflatex nhưng bản dựng thực tế (log) là XeTeX; `inputenc` bị bỏ qua dưới XeTeX (cảnh báo vô hại). | build.bat | Không sửa; nên thống nhất một engine. |

---

## A. Bản thảo `paper/cinc2026/main.tex`

### A1. Truy nguồn từng con số

Ký hiệu: FV = facts_verified.json, FP = facts_phase1.json. "Tính lại" = tôi tính từ JSON gốc, lưu ở `review_round2_checks.json`.

| Dòng | Con số trong bài | Nguồn | Kết quả |
|---|---|---|---|
| 54, 123 | 113 481 tham số; RF 379 mẫu = 1 516 ms | FV `mo_hinh`; `fqrs_model.py`:87 (1 + 2·6·31 + 6 = 379) | ĐẠT |
| 55, 175, 189 | 99,21 (kênh PSD) = oracle; 97,45 (TB 4 kênh) | FV `adfecgdb_giao_thuc_kenh_don`; `blind_lead.json` | ĐẠT |
| 57, 192 | B1: 93,30 ± 13,46; 91,31 ± 9,99; ≥90: 8; <50: 0; oracle 97,04 | FP `C_silesia`; `silesia_eval.json` summary.B1 | ĐẠT |
| 57, 193-194 | CinC: 59,15 ± 37,17 / 61,96 ± 34,09 (≥90: 4, <50: 5); kênh 0: 77,34 ± 28,54 (≥90: 5, <50: 3) | FV chỉ có trung bình; SD và số đếm **tính lại** từ `blind_lead.json` | ĐẠT (khớp hoàn toàn) |
| 59-61, 206-214, 225-227 | +11,00 (80,06→91,06); +4,53 (92,90→97,43); +0,41 (92,49→92,90), p 0,70; spread 18,89 (72,17…91,06) | FV `khao_sat_dai_loc`, `phan_ra_dong_gop`; `band_ablation.json`; `final_loro_log.txt` | ĐẠT; riêng p tầng 2 xem T3 |
| 61, 258-262 | 6 kiến trúc trong 1,53 điểm (92,43…90,90); p ≥ 0,105; cnn_m 88,76 p = 0,0001; linear 37,47; cùng 25 953 tham số | FP `A_bang_kien_truc_v2`; `arch_loro_merged.json` | ĐẠT |
| 63, 233-237, 249-252 | −18,49 (19/20; 5,7e−6), −6,40 (20/20; 1,9e−6), −11,06 (20/20; 1,9e−6); 96,74; 2,47; SD 4,44 vs 10,17; held-out 75,55/90,94/84,99/96,81; PSD 87,68/96,74/92,03/99,21 | FP `B_baseline_co_dien`; `baselines/results.json` | ĐẠT |
| 64-65, 275-282, 293-298 | AUROC 0,929 / 0,566 / 0,666 / 0,905; 61,96→69,40 (random 62,03, oracle 74,55); 84,51 (oracle 97,81); đơn đặc trưng 0,970/0,956/0,915/0,904; "1,4 điểm trên random" (63,40 − 62,03 = 1,37) | FP `D_fsqi_C3`; `fsqi/results.json` | ĐẠT |
| 103 | 3 191 nhịp (644+632+627+651+637) | FV `doi_chuan_dpss.dieu_dung_trong_goi` | ĐẠT |
| 104-105 | B1 32–42 tuần, 20 phút, 199,6 phút; B2 12 bản ghi 5 phút, 500 Hz | survey_raw papers[17]; `silesia_eval.json` (duration 1197,8 s / 300 s) | ĐẠT |
| 107 | 5/10 bản ghi lệch 8–12 ms sau đỉnh | `silesia_eval.json` summary.B1.bias_psd_ms: B1_01 −10, B1_02 −10, B1_06 −8, B1_08 −8, B1_10 −12 | ĐẠT |
| 109-111 | 250 Hz, 4×4 cặp kênh, ±5 phút, NCC 0,988–0,994, cặp B2↔r | `silesia_eval.py`:142-143, 161-172; `silesia_eval.json` leak_check | ĐẠT |
| 117-130 | 10–60 Hz bậc 4 zero-phase, notch 50, 250 Hz, mQRS 8–25 Hz, template trung vị + LS, σ = 3, AdamW 3e−3 one-cycle wd 1e−4, 6 epoch, batch 32, stride 1 s, overlap 1 s, refractory 250 ms, 0,48 MB, 4,35 ms, 920× | `fqrs_model.py` CFG/`train_final.py`:53-66; FV `mo_hinh` | ĐẠT |
| 135, 139 | lưới ngưỡng 0,20–0,75; PSD 1,8–3,0 Hz (108–180 bpm) | `train_final.py`:88; `blind_lead.py`:20 | ĐẠT |
| 148-149 | prominence median + 3 MAD, 250 ms; tuning chỉ trên r01 | `baselines/results.json` tuning_r01.chosen (k = 3,0); meta.tuning | ĐẠT |
| 151-159 | tầng 1: 8 dải, GBM, 300 ms, 2 đạo trình; benchmark 8 họ, 1 seed, 3 epoch | `band_ablation.py`:15, 31; `arch_loro_merged.json` meta | ĐẠT |
| 162-170 | 1 500 / 600 đoạn; 16 topo (dim 3), 12 cổ điển (6+6); bootstrap 1 000 | `fsqi/results.json` meta | ĐẠT |
| 176 | 99,18 (Se 99,59, PPV 98,79, 3,05 ms) | FV `adfecgdb_giao_thuc_kenh_don` | ĐẠT |
| 177-178 | 97,43 ± 4,37 (Se 97,69, PPV 97,18, 3,62 ms; 12 468/366/296); 97,16 ± 4,34 (3 seed) | FV `adfecgdb_loro`; `train_final_log.txt`; `seq_loro_log.txt` | ĐẠT (xem N3) |
| 190-191 | B2 12: 97,17 ± 7,45 / 95,26 ± 9,59 (11, 0); 7 mới: 95,87 ± 9,75 / 93,73 ± 12,48 (6, 0) | `silesia_eval.json` summary.B2, non_duplicate_only | ĐẠT (12,48 và "6" không có trong FP, lấy từ JSON) |
| 211-213 | 92,67 ± 10,46 → 97,16 ± 4,34 (3 seed, p<0,001); 98,73/99,25/99,50/99,52 | FV `quet_truong_tiep_nhan`; `seq_loro_log.txt`, `seq_search_log.txt` | ĐẠT |
| 311-317 | 27,42 vs 97,14; +0,88 (p 0,625); 2 011 đỉnh sai lệch 0; 8/16 và 3/12 đổi dấu Spearman | FV `tda_da_bac_bo`; `fsqi_log.txt`:73 (n_compared 2011, max_abs_diff 0,0); **tính lại** từ `fsqi/results.json` spearman: topo 8/16 (h1_total, h0_total, h0_max, h0_entropy, h0_ratio, sl_total, sl_max, sl_ratio), classical 3/12 (sampen, kurtosis, n_det) | ĐẠT (xem T5 về giao thức) |
| 327-328 | +2,95 (cnn_m vs cnn_dil); +4,5 (97,16 − 92,67) | FP; seq_loro | ĐẠT |
| 332-333 | 97→93; 97→77/59; "20–38 điểm" (97,45 − 77,34 = 20,1; 97,45 − 59,15 = 38,3) | FP `C_silesia`, FV | ĐẠT |
| 342 | 65 ms / đoạn | FP `D_fsqi_C3.thoi_gian_ms_doan.tong` 65,2 | ĐẠT |
| 344, 346 | 38–41 tuần (ADFECGDB); B1 timing 8,2 ms | mô tả PhysioNet ADFECGDB; `silesia_eval.json` summary.B1.jitter_psd_mean 8,218 | ĐẠT |
| 81-83 | DPSS 98,08 (labour, zero-shot); Power-MF 99,5 ± 0,5 / 98,0 ± 3,0 | FV `doi_chuan_dpss.so_that_trong_bai`, `doi_thu_bo_sot.ket_qua` | ĐẠT |

**Con số KHÔNG truy được / SAI**: không có con số nào sai. Con số **không truy được tới một file có sẵn** duy nhất là p<0,001 của tầng 2 (T3) — đã tính lại và xác nhận đúng.

### A2. refs.bib

| Khóa | DOI trong bib | Đối chiếu | Kết quả |
|---|---|---|---|
| shokouhmand2023 | 10.1109/TBME.2022.3189617 | đề bài; survey papers[3]; FV | ĐẠT |
| jaeger2024 | 10.1088/1361-6579/ad4952 | đề bài; FV `doi_thu_bo_sot.trich_dan` (tác giả, tập/số/trang khớp) | ĐẠT |
| matonia2020 | 10.1038/s41597-020-0538-z | đề bài; survey papers[17] | ĐẠT |
| zhong2018 | 10.1088/1361-6579/aab297 | đề bài; survey papers[0] | ĐẠT |
| clifford2014 | 10.1088/0967-3334/35/8/1521 | survey papers[16] | ĐẠT |
| andreotti2016 | 10.1088/0967-3334/37/5/627 | survey papers[12] | ĐẠT |
| xu2026 | 10.3390/s26072037 | survey papers[6] (Sensors 26(7):2037, tác giả khớp) | ĐẠT |
| behar2014 | 10.1088/0967-3334/35/8/1569 | survey papers[11]: tập/số/trang 35(8):1569-1589 khớp, nhưng ghi "DOI: bài KHÔNG NÊU trong file PDF" | Chưa xác minh được từ nguồn trong repo (theo mẫu IOP thì hợp lý). Không sửa. |
| perea2015 | (không DOI) FoCM 15(3):799-838 | survey papers[18] | ĐẠT |
| adams2017 | (không DOI) JMLR 18(8):1-35 | survey papers[19] ("18 (2017) 1-35") | ĐẠT (số "8" không có trong survey, nhưng đúng với JMLR paper 16-337) |
| goldberger2000, pan1985 | 10.1161/01.CIR.101.23.e215; 10.1109/TBME.1985.325532 | không có trong survey | Trích dẫn kinh điển, DOI đúng theo hiểu biết chung; không kiểm được từ repo. |

Ghi chú đầu refs.bib nói "mọi DOI lấy từ survey hoặc đề bài" — không đúng cho behar2014/goldberger2000/pan1985; nên sửa ghi chú hoặc bổ sung nguồn.

### A3. Từ ngữ khuếch trương
- `novel`: 0 lần. `state-of-the-art`: 0 lần. `outperform`/`unprecedented`: 0 lần.
- `first`: dòng 59 và 134 là thứ tự (hợp lệ); dòng 79 là tuyên bố ưu tiên không có bằng chứng ngoài lời tác giả gốc → đã sửa (N4).
- "None holds the protocol fixed" → đã giới hạn (N5).

### A4. Abstract: **229 từ** (≤ 250). ĐẠT.

### A5. Biên dịch lại
- Lệnh: `cd paper/cinc2026 && xelatex main && bibtex main && xelatex main && xelatex main`.
- Kết quả: **4 trang**, 0 chuỗi `[?]`/`??`, 0 "undefined", 0 lỗi `!`, 0 Overfull; References 12 mục (kiểu vancouver). Bản gốc trước khi sửa: `main.tex.bak_round2`.
- Kiểm tra bằng mắt 4 trang: bảng nằm trong cột, hình tiếng Anh, chú giải đủ.

---

## B. Mã huấn luyện 22 ca — `model/train_22.py`, `model/augment.py` (chỉ đọc)

| # | Câu hỏi | Kết luận | Bằng chứng |
|---|---|---|---|
| (i) | 5 bản ghi Silesia trùng PhysioNet bị loại đúng? | **ĐẠT** | `train_22.py`:46 `B2 = ['B2_03','B2_04','B2_05','B2_06','B2_08','B2_09','B2_12']`; :47 `B2_DUPLICATES` đúng 5 cặp (B2_01=r01, B2_02=r10, B2_07=r04, B2_10=r07, B2_11=r08) khớp `silesia_eval.json` leak_check; :48 `ALL` = 5 + 10 + 7 = 22; log nạp đúng 22 chủ thể. |
| (ii) | Chủ thể test có nằm trong train/val? | **ĐẠT** | `make_folds` :223-234: `gold_train = gold − test`; `val = gold_train[k % n]`; `train_ = ALL − test − val`. Log: 11 fold, mỗi fold train n = 19 = 22 − 2 − 1; fold 1 train liệt kê không chứa B1_08/B2_12/r10. Hai lần hiệu chuẩn (:269-271) dùng fold 1 train, model bị bỏ. |
| (iii) | Ngưỡng chọn trên val riêng? | **ĐẠT** | :311 `pick_threshold(model, D, f['val'])`, val ∉ train, luôn là chủ thể nhãn da đầu (PhysioNet/B2); lưới 0,20–0,75 (:53); production: trung vị ngưỡng fold (:364). |
| (iv) | Tăng cường có áp lên val/test? | **ĐẠT** | `gather(..., augment)` :134-144 chỉ được gọi trong `train()` :159; đánh giá dùng `probs_subject` :191-192 → `D[tag][lead][0], [1]` chưa tăng cường; `pick_threshold` :202-207 cũng vậy. `augment.py` không đụng nhãn (dịch thời gian thực hiện ở bộ lấy mẫu, nhãn dịch theo). |
| (v) | Nhãn B1 500 Hz đổi sang 250 Hz đúng (hệ số 0,5)? | **ĐẠT** | `silesia_loader.py`:52 `FS_FQRS = {'B1': 500, 'B2': 1000}`; :161 `fq_out = _rescale_idx(fq, 500, 1000)` (×2); tín hiệu :160 `resample_poly` 500→1000; `train_22.py`:83 `fq250 = round(fq1000 / 4)` → tổng ×0,5 cho B1, ×0,25 cho B2 (nhãn gốc 1 kHz trên FECG trực tiếp). Log: B1_01 20,0 phút, 3 120 nhãn = `silesia_eval.json` n_ref. |
| (vi) | Stride B1 2 s làm lệch pos_weight? | **ĐẠT (không lệch)** | `pos_weight_of` :121-131 đếm `hm<0,1` / `hm>0,5` trên **đúng** các đoạn trong chỉ mục train; tỉ lệ dương/âm trong một đoạn phụ thuộc FHR, không phụ thuộc stride; log pos_w 13,6 (cùng công thức train_final, kẹp 30). Lưu ý T7: stride chỉ làm B1 chiếm ≈ 72 % số đoạn chứ không làm lệch pos_weight. |

Ghi chú thêm (không phải lỗi): (a) `psd_score` :172-176 giống hệt `blind_lead.py`:23-30 → quy tắc kênh mù nhãn nhất quán; (b) lần chạy hiện tại **4 epoch** cố định (log "epoch co dinh 4"), khác 6 epoch của train_final — phải ghi rõ khi báo cáo; (c) nhịp B1 flag = 0 được dùng làm dương (:79, khai báo trong `meta.label_note`).

**F-code = ĐẠT.**

---

## C. `pilot_evidence/snr_curve.py`, `sample_efficiency.py` (chỉ đọc)

| # | Câu hỏi | Kết luận | Bằng chứng |
|---|---|---|---|
| (i) | SNR tính trên gì? Nhất quán? | **ĐẠT về nhất quán; CÓ CAVEAT về định nghĩa (T6)** | :91-94 `SNR = 10log10(P_signal/P_noise)`, P_signal = phương sai tín hiệu bụng **thô** 1 kHz toàn bản ghi, P_noise = phương sai đoạn nhiễu; `y = s + a·n`. Cùng `y` (:185) đi vào `run_model` (:186) và `run_tspca` trên cùng `x250` (:188) → hai phương pháp thấy đúng một tín hiệu nhiễu. Caveat: SNR so với tín hiệu bụng (mẹ áp đảo), không so với thai; nhiễu cộng trước lọc 10–60 Hz nên bw bị loại gần hết (đường bw phẳng). |
| (ii) | NSTDB 360 → 1000 Hz đúng? | **ĐẠT** | :72 `resample_poly(x, 25, 9)`: 360 × 25/9 = 1000 chính xác; log 1 805 556 mẫu = 650 000 × 25/9. |
| (iii) | Cùng đoạn nhiễu cho hai phương pháp? | **ĐẠT** | :179-181 `rng = default_rng([SEED, ri, ld, type_idx])`, đoạn lấy một lần cho mỗi (bản ghi, loại, kênh), dùng cho **mọi** mức SNR và cả hai phương pháp; `mix` xác định từ cùng rng. |
| (iv) | Checkpoint fold_rXX cho bản ghi rXX? | **ĐẠT** | :139-140 nạp `fetalqrs_tcn_fold_%s.pt` và `assert b['test_record']==rec and rec not in b['train_records']`; log: r01 ← train r07,r08,r10 val r04; r04 ← train r07,r08,r10 val r01… Ngưỡng lấy từ checkpoint (chọn trên val). Lưu ý: TS-PCA (npc 2, thr_frac 0,75) tinh chỉnh trên r01 → điểm TS-PCA trên r01 là in-sample (đã khai báo trong baselines; nên nhắc lại trong hình SNR). |
| (v) | k = 1 không có val → ngưỡng? test trùng train? | **ĐẠT có khai báo (T8)** | k = 1: ngưỡng cố định 0,45 (:42, :181-203) = trung vị ngưỡng 5 fold LORO = mặc định `M.detect`; rò rỉ nhẹ một vô hướng vì các ngưỡng fold được chọn trên val trùng bản ghi test của k = 1 → script tự khai báo (meta.nguong_k1) và có biến thể in-sample. k = 2: ngưỡng trên bản ghi thứ nhất của cặp, **nằm trong train** (in-sample, khai báo, có biến thể 0,45). Test/train tách rời ở mọi k: :183 `test_ids = [i ≠ ti]`, :214 loại cả hai bản ghi train. k = 3 lấy từ LORO (val riêng). |

**G-code = ĐẠT**, với điều kiện khi đưa vào bài phải nêu (1) mốc SNR so với toàn tín hiệu bụng và tính chất "bw bị lọc", (2) quy tắc ngưỡng khác nhau giữa k = 1/2/3 (ưu tiên trục cố định 0,45 cho cả ba).

---

## D. Đánh giá tổng thể

- **J (bản thảo) = ĐẠT CÓ ĐIỀU KIỆN.** Không có con số bịa; mọi con số truy được hoặc tính lại khớp. Điều kiện: (1) giữ các sửa đã áp (bibtex, hình tiếng Anh, bảng, `\pm`, caveat T4/T5); (2) ghi Wilcoxon tầng 2 trực tiếp (p = 8,8·10⁻⁵) vào facts và trích đúng nguồn; (3) T9 cần trích dẫn hoặc bỏ "often"; (4) kiểm tra lại 4 trang với `cinc.cls` chính thức; (5) điền tác giả.
- **F-code (train_22.py, augment.py) = ĐẠT.** Không rò rỉ ở cả 6 điểm. Cần khai báo: 4 epoch, B1 chiếm ~72 % đoạn với nhãn gián tiếp (T7).
- **G-code (snr_curve.py, sample_efficiency.py) = ĐẠT.** Nhất quán và tách fold đúng. Caveat bắt buộc khi báo cáo: T6, T8.

## E. File đã thay đổi / tạo
- Sửa: `paper/cinc2026/main.tex` (24 thay thế; bản gốc `main.tex.bak_round2`), `paper/cinc2026/main.pdf` (dựng lại, có `main.bbl`).
- Tạo: `paper/cinc2026/figs/make_figs_en.py`, `figs/fig13_arch_en.pdf`, `figs/fig9_risk_coverage_en.pdf`, `survey/review_round2_checks.json`, `survey/review_round2.md`.
- Không đụng: `refs.bib` (không phát hiện DOI sai), mọi mã đang chạy, mọi JSON kết quả.
