# Công bằng đối chuẩn và dữ liệu có đủ chưa

*Nhiệm vụ T2 · 17/09/2026 · commit b158507 · mọi con số truy ngược về tệp JSON hoặc tài liệu ghi ở cột "Nguồn". Số đã rút (`survey/facts_phase4.json → Z_DA_RUT`) không xuất hiện trong tài liệu này trừ khi được ghi rõ là "đã rút".*

Bốn câu hỏi của chủ nhiệm và câu trả lời ngắn:

| Câu hỏi | Trả lời ngắn | Mục |
|---|---|---|
| So sánh trên cùng tập dữ liệu với bài khác thì kết quả thế nào? | Trong miền (22 chủ thể, ±50 ms): RelyFetal 1 kênh 97,56 · Power-MF 4 kênh 98,83 · Power-MF 1 kênh 86,71. Ngoài miền (CinC 2013, 60 bản sạch): RelyFetal 74,28 (PSD) / 80,72 (gate, quy tắc kế hoạch chọn, trượt Holm) / 81,01 (gate4, cũng ghi trước) / 82,01 (peakprob, hậu kiểm), trần oracle 83,60 · Power-MF 1 kênh 55,97 · Power-MF 4 kênh **93,12** (số tác giả tự công bố, ta lọc 15 bản nhiễm) · CUNet 77,8 (75 bản, số trích). | 1, 2 |
| Có công bằng không? | **Chỉ hai so sánh là công bằng đầy đủ**: Power-MF 1 kênh (cùng đạo trình, cùng front-end, cùng 22 chủ thể) và TS/TS-PCA/Prominence (cùng 5 chủ thể ADFECGDB). Power-MF 4 kênh so được nhưng **họ có 4 đạo trình, ta có 1**. Mọi con số khác đều lệch ít nhất một yếu tố (bộ bản ghi, đơn vị, đầu vào). | 2 |
| Phương pháp của họ chạy lại so với ta thì sao? | Chỉ Power-MF được chạy lại thật (Octave, kiểm chứng ngoài 99,40 vs 99,46 tác giả). Chạy lại đã lộ một lỗi cổng chuyển làm Power-MF hỏng 6/10 bản B1 mà nếu chỉ trích số thì không bao giờ biết. DPSS và CUNet **vẫn là số trích**. | 1, 3 |
| Dữ liệu có đủ để train chưa? | **Đủ** để chứng minh mô hình 1 kênh học được và ổn định trong miền (97,56, seed 1 cho 97,59). **Không đủ** để (i) tuyên bố tương đương với Power-MF 4 kênh (cần ~50 chủ thể), (ii) nói vì sao ngoài miền mất 13,96–23,28 điểm (97,56 trong miền trừ F1 trên 60 bản sạch, từ trần oracle 83,60 đến PSD 74,28), (iii) dùng B1 làm thước đo thời điểm. Đường cong 5 → 12 → 22 chỉ có 3 điểm, không ngoại suy. | 4 |

---

## 1. Bảng 1 — Ai chạy lại, ai chỉ trích

Quy ước: **CHẠY LẠI** = nhóm chạy mã của họ (hoặc cài lại theo mô tả) trên dữ liệu ta có và chấm bằng đúng bộ chấm của ta (`model/fqrs_model.py::match_events`, ±50 ms, ghép tham lam 1-1). **TRÍCH** = lấy số trong bài hoặc trong kho kết quả của tác giả, không chạy.

| Đối thủ | Chạy lại / Trích | Nếu chạy lại: dữ liệu, số chủ thể, kiểm chứng ngoài | Nếu trích: số họ, trên bộ nào, dung sai, vì sao chưa chạy lại | Nguồn |
|---|---|---|---|---|
| **Power-MF 4 kênh** (Jaeger 2024, Physiol Meas 45:055009) | **CHẠY LẠI** | Mã MATLAB gốc (repo mad-lab-fau, MIT) chạy qua GNU Octave, vá `findpeaks` (P7). 22 chủ thể: ADFECGDB 5 + Silesia B2 7 + B1 10. Kiểm chứng ngoài: **B1 ta chạy 99,40 vs tác giả công bố 99,46** (lệch 0,06, trong sai khác `filtfilt` Octave/MATLAB). Kết quả 22 chủ thể: **98,83 ± 2,20**. | — | `baselines/BASELINES.md` §2; `baselines/powermf_fair.json`; `baselines/powermf_published.json → b1_powermf` |
| **Power-MF 1 kênh** (ta tự cắt) | **CHẠY LẠI** (biến thể do ta cắt) | Cài lại 21 bước của `PowerMF.m` bằng Python, bỏ FecgICAm/FecgICAf (cần đa kênh), giữ `ms = 340 ms` mặc định, dùng front-end và bộ khử mẹ của ta. 22 chủ thể: **86,71 ± 14,87**. CinC 60 sạch: **55,97 [48,08; 64,03]**. Không có số tác giả để kiểm chứng ngoài — tác giả không công bố chế độ đơn kênh. | — | `baselines/powermf_1ch.json → meta, tom_tat`; `benchmark_dpss/eval_cinc60_sach.json → powermf_1ch.60_sach` |
| **TS** (mẫu trung bình + Pan-Tompkins) | **CHẠY LẠI** (cài lại) | ADFECGDB 5 chủ thể × 4 kênh; siêu tham số chọn **chỉ trên r01**, áp cho 4 bản còn lại. Kênh PSD mù nhãn: **87,68**; TB 20 (bản ghi × kênh): 78,96; 16 giữ ngoài: 75,55. Không có số tác giả trên chính bộ này để đối chiếu. | — | `baselines/results.json → baselines.TS` |
| **TS-PCA** (mẫu PCA 2 thành phần + Pan-Tompkins) | **CHẠY LẠI** (cài lại) | Như TS. Kênh PSD: **96,74**; TB 20: 91,05; 16 giữ ngoài: 90,94. | — | `baselines/results.json → baselines.TS-PCA` |
| **Prominence** (front-end của ta + `find_peaks`) | **CHẠY LẠI** (cài lại) | Như TS. Kênh PSD: **92,03**; TB 20: 86,39. Đây là "mốc không học": cùng phần dư mà mô hình nhìn thấy, chỉ thay mạng bằng ngưỡng nổi bật. | — | `baselines/results.json → baselines.Prominence` |
| **DPSS** (Shokouhmand & Tavassolian 2023, IEEE TBME 70:283, DOI 10.1109/TBME.2022.3189617) | **TRÍCH — CHƯA CHẠY LẠI** | — | Silesia 22 bản ghi (10 thai kỳ + 12 chuyển dạ; bài gọi là "ADFECGDB", **không phải** ADFECGDB cổ điển 5 bản) F1 **97,7**; nhóm chuyển dạ 98,08; NIFECGC (= CinC 2013 set-a, tập con không nêu) **95,3**; FECGSYNDB 99,03. Huấn luyện **chỉ** trên FECGSYNDB tổng hợp, zero-shot sang ADFECGDB. Dung sai 50 ms (trích Behar 2016, **không phải** AAMI EC57). Vì sao chưa chạy lại: chưa bố trí thời gian (ước 2–3 ngày, `HANDOFF.md` §10 #6); tình trạng mã nguồn công khai chưa được xác minh trong tệp survey. **Đây là lỗ hổng cùng loại với Power-MF trước khi chạy lại.** | `survey/facts_verified.json → doi_chuan_dpss`; `survey/ro_ri_vanlieu.json → bang_bi_nhiem.dem_trung_hai_tap_kiem_thu` |
| **CUNet** (Orvas và cs. 2025, arXiv 2506.22457, preprint) | **TRÍCH — KHÔNG CHẠY LẠI ĐƯỢC** | — | CinC 2013 set-a **75 bản**, zero-shot, đơn kênh, ±50 ms: F-score **77,8 ± 18,6**. Huấn luyện trên dữ liệu mô phỏng điện cực vải khô (in-silico), không dùng ADFECGDB → **không nhiễm**. Vì sao không chạy lại: bài không nêu số tham số, tham số STFT, tần số lấy mẫu, số tầng; không thấy mã công khai. Không cài lại được từ mô tả. | `survey/RO_RI_VANLIEU.md` bảng dòng 11; `de_cuong_latex/bao_cao_30_paper.tex` p11 |
| **Castillo 2018** (PLoS ONE, DOI 10.1371/journal.pone.0199308) | **TRÍCH** | — | ADFECGDB đơn kênh, 50 ms: **94,11** (17/20 tín hiệu, trong mẫu); **98,04** trên 11 tín hiệu do bác sĩ chọn. Trên CinC: **bị nhiễm** (28/64 tín hiệu là bản sao ADFECGDB) → không dùng số CinC. Chưa chạy lại: chưa bố trí; số ADFECGDB của họ là trong mẫu nên chạy lại cũng không so được với LOSO. | `bang_baihoc.tex` p17; `survey/ro_ri_vanlieu.json → chac_chan` |
| **Behar 2014** (luận án; qua benchmark Jaeger) | **TRÍCH số do Jaeger chạy lại** (không phải ta) | — | Cùng ±50 ms, cùng công thức F1. B1 **90,41**; B2 **87,68**; CinC 75 bản 61,70 → 60 sạch (ta lọc) **55,01**. Dùng 4 kênh bụng, chương 6 thêm 1 kênh ngực mẹ. F1 96,0 gốc trong bài là trong mẫu. Chưa chạy lại: mã trong repo Jaeger, chưa bố trí. | `baselines/powermf_published.json → b1_behar, b2_behar, challenge_behar`; `bang_baihoc.tex` p13, p14 |
| **Varanini** (qua benchmark Jaeger) | **TRÍCH số do Jaeger chạy lại** | — | B1 **99,37**; B2 **97,95**; CinC 75 bản 97,04 → 60 sạch (ta lọc) **96,32**. Đa kênh (ICA). *Suy luận:* Varanini là đội dự thi CinC 2013, set-a là tập huấn luyện công khai của cuộc thi nên tham số có thể đã hợp với set-a — chưa kiểm. | `baselines/powermf_published.json → b1_varanini, b2_varanini, challenge_varanini` |
| **Sulas** (qua benchmark Jaeger) | **TRÍCH số do Jaeger chạy lại** | — | B1 63,04; B2 65,36; CinC 75 bản 48,19 → 60 sạch 47,70. Đưa vào chỉ để hoàn chỉnh bảng của Jaeger. | `baselines/powermf_published.json → b1_sulas, b2_sulas, challenge_sulas` |
| **Power-MF 4 kênh trên CinC** (số tác giả) | **TRÍCH** (tác giả tự chạy MATLAB, chấm `Bxb_compare` ±50 ms) | — | 75 bản: 94,27. **60 bản sạch (ta lọc từ per-record): 93,12**, trung vị 98,54, 3 bản < 50. 15 bản nhiễm: 98,88. Không chạy lại trên CinC vì mã Octave của ta mới chỉ chạy trên 22 chủ thể; CinC 60 s/bản không gặp lỗi `findpeaks` O(k²) nên số tác giả không bị lỗi cổng chuyển như B1. | `baselines/powermf_published.json → challenge_powermf` (lọc 15 bản theo `facts_phase4.json → A.15_ban_ro_ri`) |
| Rodrigues 2014, Mohebbian 2022, Chen 2025 | **KHÔNG DÙNG** | — | Bị nhiễm rò rỉ huấn luyện (huấn luyện trên ADFECGDB, kiểm trên set-a chứa 15 bản sao). Không đưa vào bảng so sánh. | `survey/ro_ri_vanlieu.json → bang_bi_nhiem.chac_chan` |

**Đọc bảng 1:** trong 12 dòng, **5 là chạy lại** (Power-MF 4 kênh, Power-MF 1 kênh, TS, TS-PCA, Prominence) và chỉ **1 có kiểm chứng ngoài** (Power-MF 4 kênh, vì chỉ Power-MF có số tác giả trên chính bộ ta có). TS/TS-PCA/Prominence là cài lại theo mô tả, không có số gốc để đối chiếu — chúng là mốc chuẩn cổ điển, không phải "đối thủ" theo nghĩa có bài công bố trên cùng bộ.

---

## 2. Bảng 2 — Yếu tố gây nhiễu khi so sánh

Cấu hình của **RelyFetal** làm chuẩn so: dung sai **±50 ms** · đơn vị **chủ thể** (22, cluster bootstrap) hoặc **bản ghi** (CinC 60) · bộ **22 chủ thể** trong miền (LOSO) + **CinC 60 sạch** ngoài miền (zero-shot) · **không** điện cực ngực, **1** đạo trình bụng · quy tắc chọn kênh PSD là **mốc cũ** (theo Power-MF); `gate` là quy tắc **kế hoạch chọn** (80,72, trượt Holm); `peakprob` là **hậu kiểm** · seed 0 (seed 1 kiểm: 97,59 vs 97,56, hiệu +0,03 [−0,18; +0,34]).

Ký hiệu: ✓ = giống ta · ✗ = khác ta (ghi khác thế nào) · ? = không xác định được từ nguồn.

| Đối thủ | Dung sai | Đơn vị | Bộ + số bản ghi | Điện cực ngực / số kênh | Tinh chỉnh trên tập kiểm | Hạt giống | **Kết luận** |
|---|---|---|---|---|---|---|---|
| **Power-MF 4 kênh** (ta chạy lại, 22 chủ thể) | ✓ 50 ms | ✓ chủ thể, cùng bộ chấm | ✓ cùng 22 chủ thể | ✗ **4 kênh bụng** (SVD + ICA) vs 1 kênh của ta; không ngực | ? Thuật toán không học, tham số mặc định của tác giả; tác giả công bố trên chính B1/B2 nên không loại trừ tham số đã hợp với bộ này | Tất định, không seed | **SO ĐƯỢC CÓ ĐIỀU KIỆN** — phải ghi "4 kênh vs 1 kênh". Hiệu −1,27 [−3,08; +0,27], p 0,156, 18/0/4 |
| **Power-MF 1 kênh** (ta cắt) | ✓ | ✓ | ✓ | ✓ 1 kênh, cùng đạo trình PSD | ✓ không tinh chỉnh | Tất định | **SO TRỰC TIẾP ĐƯỢC** — nhưng là bản do ta cắt, tác giả chưa xác nhận. +10,85 [+6,80; +15,40], 22/22 |
| **TS / TS-PCA / Prominence** | ✓ | ✓ chủ thể (n = 5) | ✗ chỉ ADFECGDB 5 chủ thể, chưa chạy 17 chủ thể Silesia | ✓ 1 kênh | ✗ siêu tham số chọn trên r01 rồi áp cho 4 bản còn lại (r01 trong mẫu) | Tất định | **SO TRỰC TIẾP ĐƯỢC NHƯNG THIẾU CÔNG SUẤT** — n = 5, p Wilcoxon nhỏ nhất 0,0625; KTC t của TS chứa 0 ([−1,81; 38,80]); TS-PCA và Prominence loại trừ 0 |
| **DPSS 2023** | ✓ 50 ms | ✗ **tín hiệu**, không phải chủ thể | ✗ 22 bản Silesia (bài gọi là "ADFECGDB"; *suy luận*: cùng 22 sản phụ với ta, vì 5 bản ADFECGDB của ta trùng 5 bản B2), nhưng họ chọn kênh bằng tay; số 95,3 trên NIFECGC không nêu tập con; đếm trùng ADFECGDB + CinC (15 bản chung) | ✓ đơn kênh, không ngực | ✗ theo chiều **có lợi cho ta**: họ zero-shot từ tổng hợp sang Silesia, ta LOSO trong miền | ? | **KHÔNG SO TRỰC TIẾP ĐƯỢC** — 97,7 (zero-shot, tín hiệu, kênh chọn tay) vs 97,56 (LOSO, chủ thể, kênh chọn mù) là hai giao thức khác nhau. Muốn so phải chạy lại DPSS trên 22 chủ thể |
| **CUNet 2025** | ✓ 50 ms | ✓ nhịp/bản ghi | ✗ **75 bản** (gồm 15 bản dễ, Power-MF tác giả đạt 98,88 trên 15 bản đó vs 93,12 trên 60) vs 60 sạch của ta | ✓ đơn kênh | ✓ zero-shot, không tinh chỉnh | ? không nêu | **SO CÓ ĐIỀU KIỆN** — 77,8 (75 bản) nằm giữa 74,28 (PSD) và 80,72 (gate, quy tắc kế hoạch chọn, trượt Holm) / 81,01 (gate4, cũng ghi trước) / 82,01 (peakprob, hậu kiểm) của ta trên 60 bản; vì 15 bản thêm là bản dễ, *suy luận* 77,8 được lợi vài điểm so với nếu chấm 60 bản. Không kết luận thắng thua |
| **Castillo 2018** | ✓ 50 ms | ✗ tín hiệu (17/20; 11/20 chọn bởi bác sĩ) | ✗ ADFECGDB trong mẫu; CinC nhiễm | ✓ đơn kênh | ✗ trong mẫu, chọn tín hiệu hậu kiểm | ? | **KHÔNG SO ĐƯỢC** trên CinC; trên ADFECGDB chỉ nêu tham khảo (94,11 trong mẫu vs 99,40 LOSO) |
| **Behar 2014** (số Jaeger) | ✓ | ✓ bản ghi | ✓ B1/B2/CinC (cùng bản) | ✗ 4 kênh bụng (+ ngực ở chương 6) | ? | ? | **SO CÓ ĐIỀU KIỆN** — đa kênh; ta 97,15 (B1) vs 90,41; 96,82 (B2) vs 87,68; CinC 60 sạch 74,28 vs 55,01 |
| **Varanini** (số Jaeger) | ✓ | ✓ bản ghi | ✓ B1/B2/CinC | ✗ đa kênh (ICA) | ✗? *suy luận:* đội dự thi CinC 2013, có thể đã chỉnh trên set-a | ? | **KHÔNG SO TRỰC TIẾP ĐƯỢC** trên CinC; trên B1/B2 chỉ nêu tham khảo (99,37 / 97,95 vs ta 97,15 / 96,82) |
| **Power-MF 4 kênh trên CinC** (số tác giả) | ✓ 50 ms (`Bxb_compare` của họ, không phải `match_events` của ta) | ✓ bản ghi | ✓ **cùng 60 bản sạch** sau khi ta lọc | ✗ 4 kênh | ✓ không học | Tất định | **SO CÓ ĐIỀU KIỆN** — và **kết quả không ủng hộ ta**: 93,12 (4 kênh) vs 74,28 PSD / 80,72 gate (trượt Holm) / 81,01 gate4 / 82,01 peakprob hậu kiểm (1 kênh). Khoảng cách 11–19 điểm; Power-MF 1 kênh của ta chỉ đạt 55,97 → phần lớn khoảng cách là **đa kênh**, không phải thuật toán |

**Ba câu trả lời cho giảng viên hỏi "có công bằng không":**

1. *Công bằng nhất* là Power-MF 1 kênh: cùng đạo trình, cùng front-end, cùng 22 chủ thể, cùng bộ chấm. Ở đó RelyFetal hơn 10,85 điểm, thắng 22/22. Nhưng đây là phiên bản **ta cắt**, tác giả chưa công bố chế độ này.
2. *Đủ công bằng* là Power-MF 4 kênh chạy lại trên 22 chủ thể: cùng mọi thứ trừ **số đạo trình**. RelyFetal kém 1,27 điểm, KTC chạm 0. Câu đúng: "không phân biệt được với n = 22", **không** phải "tương đương".
3. *Không công bằng theo chiều bất lợi cho ta* là CinC 60 sạch: mọi phương pháp đa kênh (Power-MF 93,12, Varanini 96,32) bỏ xa mô hình 1 kênh (74,28 PSD · 80,72 gate, trượt Holm · 81,01 gate4 · 82,01 peakprob hậu kiểm). Số CUNet 77,8 là mốc 1 kênh gần nhất, nhưng trên 75 bản.

**Một điểm phải khai báo về chính ta:** `peakprob` 82,01 là quy tắc chọn **sau khi** đã nhìn 60 bản sạch (p_Holm 0,0039 nhưng hậu kiểm). Quy tắc kế hoạch chọn `gate` (ghi trước khi chạy) cho 80,72 và **trượt** Holm (0,051); `gate4`, cũng ghi trước khi chạy nhưng không phải quy tắc kế hoạch chọn, cho 81,01 và sống sót (0,015). Tệp ghi trước chưa neo git. Khi đặt cạnh CUNet 77,8 phải ghi cả ba số, không chỉ 82,01.

---

## 3. Vì sao phải chạy lại — bài học Power-MF

Chuỗi sự kiện ghi trong `baselines/BASELINES.md` §0–2:

1. **Lần chạy đầu** (`baselines/powermf_results.json`): 6/10 bản Silesia B1 hỏng — B1_01 và B1_02 cho Se ≈ 50 % với PPV ≈ 99,7; B1_03–B1_06 trả về rỗng. B1 trung bình **88,19** trên 6 bản chạy được (số của bản cổng chuyển hỏng, không dùng; `baselines/BASELINES.md` dòng 72. Số này không nằm trong danh sách đã rút `Z_DA_RUT → powermf_cong_chuyen_hong`; danh sách đó chỉ ghi bốn số khác của cùng bản cổng chuyển hỏng).
2. **Đoán sai nguyên nhân:** giả thuyết ban đầu là `ms_minpeakdistance = 340 ms` quá sát nhịp thai. Đo RR thật từ nhãn trên 27 bản ghi: tỉ lệ RR < 340 ms lớn nhất **0,15 %**, B1_01 và B1_02 là **0,00 %**. Ràng buộc 340 ms chưa từng chặn một nhịp thật nào. Giả thuyết bị bác bỏ; thử tham số thích nghi `0,7 × RR ước lượng` cũng cho sai số 101,2 ms trung bình — tệ hơn hằng số.
3. **Nguyên nhân thật:** log Octave của cả 6 bản ghi cùng một dòng `out of memory or dimension too large for Octave's index type at findpeaks line 203`. `findpeaks` của gói `signal` Octave cài `MinPeakDistance` bằng ma trận khoảng cách đôi một, **O(k²)** bộ nhớ; bản ghi B1 nội suy ×4 lên 2.395.600 mẫu có hàng chục nghìn ứng viên đỉnh → vượt chỉ số 32 bit. MATLAB của tác giả dùng thuật toán tham O(k log k), không bao giờ gặp lỗi này. Bằng chứng: B1_01 phát hiện 1555 đỉnh **toàn bộ ở nửa đầu**, 0 ở nửa sau; khoảng cách phát hiện trung vị 385,5 ms so với RR thật 386,0 ms — nửa chạy được thì chạy đúng.
4. **Bản vá P7** (`baselines/octave/findpeaks_mpd.m`): cài đúng ngữ nghĩa MATLAB bằng danh sách liên kết, O(k). Kiểm chứng 48 trường hợp: tập đỉnh Octave luôn là tập con của P7. Chạy lại **toàn bộ 27 bản** với cùng mã.
5. **Sau vá:** B1_01 66,44 → 99,92; B1_02 67,12 → 99,55; 4 bản thất bại → 98,97–99,97. B1 trung bình **99,40** trên 10 bản. **Kiểm chứng ngoài:** tác giả công bố **99,46** (`Results/*.mat` trong repo gốc, ghép theo vân tay TP+FN khớp 22/22 bản Silesia). Lệch **0,06 điểm**.

**Điều gì xảy ra nếu chỉ trích số?** Ta đã có thể viết "Power-MF 88,19 trên B1, RelyFetal 97,15" và thắng 9 điểm — hoàn toàn sai, vì lỗi nằm ở cổng chuyển của ta chứ không ở thuật toán của họ. Chạy lại + kiểm chứng ngoài là thứ duy nhất phát hiện được điều đó. Nó cũng lộ thêm một chi tiết chỉ thấy khi đọc mã: `PowerMF.m` gán `template(j,:)` từ `j = 3`, để hai hàng 0 lọt vào `median` — gần như chắc chắn là lỗi tác giả, nhưng đo ra **không có hậu quả** (86,71 vs 86,70 trên 22 chủ thể).

**Kết:** DPSS hiện ở đúng vị trí Power-MF trước bản vá — một con số trích (97,7 / 95,3) mà ta chưa tái tạo, chưa biết giao thức chi tiết (tập con NIFECGC nào, tín hiệu nào), chưa kiểm được bộ chấm của họ. `facts_verified.json → doi_chuan_dpss` còn ghi 8 tuyên bố không có nguồn về DPSS từng lọt vào gói đối chuẩn nội bộ (91,03 macro F1, 6,8 triệu tham số, độ trễ 35–50 ms…) — tất cả đều **không có trong bài gốc**. Việc tiếp theo về đối chuẩn là **chạy lại DPSS** (`HANDOFF.md` §10 #6, ước 2–3 ngày), không phải thêm đối thủ trích.

---

## 4. Bảng 3 — Dữ liệu có đủ để train chưa

### 4.1 Đường cong số chủ thể: ba điểm, không ngoại suy

| Trục đo | n = 5 (m5) | n = 12 (m12) | n = 22 (m22) | Ghi chú | Nguồn |
|---|---|---|---|---|---|
| **CinC 2013, 60 bản sạch, kênh PSD** (ngoài miền, cả ba mô hình chưa thấy) | 64,04 [55,39; 72,53] | 67,93 | **74,28** [66,63; 81,78] | m22 − m5 = +10,24 [+7,13; +13,60], W p 3,5e−10, thắng 52/3/5. m22 − m12 = +6,35 [+4,04; +8,95] | `facts_phase4.json → A.psd`; `analysis/DULIEU.md` §2.1, §4.1 |
| **Silesia B1, 10 chủ thể, kênh PSD** (trong miền; m22 chấm LOSO nên n huấn luyện thực = 19) | 93,30 | 94,37 | **97,15** [94,00; 99,67] | m5, m12 chưa thấy B1 nào | `analysis/DULIEU.md` §2.1; `analysis/ABLATION_B1.md` §4; `model/train_22.json → summary.B1_F1_psd` |
| **12 chủ thể nhãn trực tiếp** (m12 vs m22, giữ nhóm) | — | 97,84 | 97,89 | hiệu −0,06, KTC [−0,20; +0,09] — **thêm B1 không giúp trên nhãn trực tiếp** | `analysis/ABLATION_B1.md` §5–6 |
| **Trong ADFECGDB, số bản ghi huấn luyện 1 → 2 → 4** (macro F1 bản ghi × kênh, 5 lần chạy mỗi mức) | 91,18 (1 bản) | 93,39 (2 bản) | 97,45 (4 bản, LORO) | Đường cong con, đơn vị bản ghi không phải chủ thể; SD giữa lần chạy 17,2 / 13,6 / 4,4 | `pilot_evidence/sample_efficiency.json → table` |

**Đọc:** cả ba trục đều **tăng đơn điệu** theo số chủ thể và chưa thấy bão hoà ở 22. Đó là toàn bộ điều 3 điểm nói được. `analysis/DULIEU.md` §2.2 có khớp ba dạng hàm (`a − b/n`, `a + b·log n`, logit) và chúng cho **hai câu trả lời trái ngược** tại n = 50 (74,0 vs 79,0) với cùng độ khớp — vì 3 điểm và 2 tham số chỉ còn 1 bậc tự do. Tài liệu này **không dùng** bất kỳ số ngoại suy nào làm căn cứ.

### 4.2 Công suất thống kê: cần bao nhiêu chủ thể

| Câu hỏi | Số | Ý nghĩa | Nguồn |
|---|---|---|---|
| n nhỏ nhất để p Wilcoxon < 0,05 | > 5 | Với n = 5 (ADFECGDB), p nhỏ nhất khả thi là **0,0625** — mọi so sánh trên 5 chủ thể không thể có ý nghĩa thống kê dù hiệu ứng lớn | `analysis/STATS.md` §1, §3.1; `HANDOFF.md` §8.5 |
| TOST biên 1,0 điểm, 7 họ kiến trúc, n = 5 | 0/7 tương đương | "Không khác biệt" trước đây thực chất là "không đủ công suất" | `analysis/STATS.md` §3 |
| n cần cho ablation 2 điểm khi hiệu ứng tập trung ở 1/7 chủ thể | **~50** (t-test ghép cặp) hoặc **~160** (Wilcoxon) | Dưới 30 chủ thể, một kết quả "không có ý nghĩa" không nói lên điều gì | `analysis/LUONGCUC.md` §6.3 |
| Rely − Power-MF 4 kênh, n = 22 | −1,27 [−3,08; +0,27], p 0,156 | KTC chứa 0 và rộng 3,35 điểm → **không kết luận tương đương được**; cần n ~50 để KTC hẹp đủ | `baselines/powermf_fair_stats.json → so_sanh.tat_ca_22` |
| Bộ chọn kênh học (learned) | thất bại: +3,52 [−0,77; +8,48] trên 60 bản CinC sạch, p Holm 1,00 | 88 hàng huấn luyện (22 × 4) cho 36 đặc trưng — khuyến nghị không học bộ chọn kênh dưới ~50 chủ thể | `analysis/dulieu_results.json → chon_kenh_60_sach.bang.learned`; `analysis/CHONKENH.md` (e) cho thiết kế (số +2,81 trong tệp đó tính trên 75 bản nhiễm, không dùng) |

### 4.3 B1 chiếm 77 % thời lượng nhưng nhãn gián tiếp

| Đại lượng | Số | Nguồn |
|---|---|---|
| Phần B1 trong tập huấn luyện 22 | **76,9 %** phút (199,6/259,6) · **78,2 %** nhịp (28.405/36.313) · sau stride 500 (B1) vs 250 (B2/PhysioNet): **64,4 %** nhịp mô hình nhìn thấy mỗi epoch | `analysis/DULIEU.md` §4.1 |
| Nhịp B1 mang cờ 0 (chưa duyệt) | 130/28.405 = **0,458 %**; lọc chúng khi chấm chỉ đổi +0,129 điểm | `analysis/DULIEU.md` §1.2 |
| **Dấu vân nhãn** — độ lệch thời điểm tuyệt đối trên 8 chủ thể B1 mà cả ba mô hình đạt F1 ≥ 95 | m5 **6,50** ms · m12 **6,50** ms · m22 **3,25** ms; jitter 6,80 / 6,62 / 3,79 ms | `analysis/ABLATION_B1.md` §3, §6 |
| B1 có đóng góp thật không | m12 (bỏ toàn bộ B1) 67,93 vs m22 74,28 trên CinC 60 sạch: **+6,35 [+4,04; +8,95]** — CinC không chia người chấm với Silesia nên phần này là khái quát thật | `analysis/DULIEU.md` §4.1 |

**Đọc:** hai mô hình chưa từng thấy B1 lệch mốc **giống hệt nhau** (6,50 / 6,50) còn mô hình đã thấy B1 lệch đúng một nửa (3,25) — đó là chữ ký của **quy ước chấm mốc** của B1, không phải chất lượng dò. Với ±50 ms nó gần như không đổi F1, nhưng nó **cấm** dùng số B1 để nói về độ chính xác thời điểm (jitter 3,76 ms, STV). Đồng thời B1 **không phải chỉ là dấu vân**: bỏ B1 mất 6,35 điểm ở nơi không có gì để bắt chước.

### 4.4 Không còn bộ công khai nào có nhãn

| Bộ | Có nhãn fQRS | Tình trạng với ta | Nguồn |
|---|---|---|---|
| ADFECGDB (PhysioNet) | Có, trực tiếp (da đầu), 1 kHz, 5 × 5 phút | Đã dùng huấn luyện (5 chủ thể) | `analysis/DULIEU.md` §4.1 |
| Silesia B2 (12) / B1 (10) | B2 trực tiếp; B1 gián tiếp | Đã dùng (7 + 10; 5 bản B2 trùng PhysioNet đã loại) | `analysis/DULIEU.md` §1.4 |
| CinC 2013 set-a (75) | Có (ban tổ chức) | 15 bản là bản sao ADFECGDB → chỉ 60 dùng kiểm tra; số sản phụ thật trong 60 bản **không biết, nhiều nhất 60**, có thể ít hơn (NIFECGDB góp 14 bản từ **một** sản phụ vào cuộc thi, chưa biết có nằm trong 60 bản không) | `facts_phase4.json → A`; `ro_ri_vanlieu.json → kiem_cheo_ky_thuat` |
| CinC set-b/c | Không công khai nhãn | Không dùng được | — |
| NInFEA (Power-MF dùng, 200 ms) / FECGSYNDB (DPSS dùng, tổng hợp) | NInFEA: chưa xác minh loại nhãn; FECGSYNDB: nhãn tổng hợp | Chưa tải, chưa chạy | `facts_verified.json → doi_thu_bo_sot` |
| Bộ thứ ba có nhãn fQRS thật để xác nhận `peakprob` | **Không có** | Việc #1 của `HANDOFF.md` §10: xin dữ liệu khoa sản | `HANDOFF.md` §10, §11 |

### 4.5 Kết luận thẳng

**Đủ để chứng minh:**
- Mô hình 1 kênh 113.481 tham số học được bài toán từ 22 chủ thể: LOSO **97,56**, ổn định theo seed (97,59 với seed 1 và phân fold khác), 22/22 chủ thể hơn Power-MF 1 kênh.
- Thêm chủ thể còn giúp: 5 → 12 → 22 tăng đơn điệu trên cả ba trục, chưa bão hoà.
- B1 nhãn gián tiếp đóng góp thật (+6,35 ngoài miền), không làm hỏng khớp nhãn trực tiếp (97,84 vs 97,89).

**Không đủ để chứng minh:**
- **Tương đương** với Power-MF 4 kênh: KTC [−3,08; +0,27] rộng 3,35 điểm; cần ~50 chủ thể.
- **Vì sao** ngoài miền mất 13,96–23,28 điểm (97,56 trong miền so với 60 bản CinC sạch: PSD 74,28 → 23,28; gate 80,72 (kế hoạch chọn, trượt Holm) → 16,84; gate4 81,01 → 16,55; peakprob hậu kiểm 82,01 → 15,55; ngay cả oracle 83,60 vẫn còn 13,96): bốn cách thích nghi miền đều thất bại, phép thử nhìn thấy có âm tính giả 18,0 % → nguyên nhân chưa xác định; cần dữ liệu tín hiệu yếu có nhãn.
- `peakprob` tổng quát: hậu kiểm trên 60 bản, không có bộ thứ ba.
- Độ chính xác **thời điểm** trên B1 (dấu vân 3,25 vs 6,50 ms).
- Số lượng sản phụ độc lập thật sự trong 60 bản CinC sạch.
- Bất kỳ con số nào ở n = 50 hoặc n = 100 (3 điểm không ngoại suy được).

---

## 5. "Nếu họ chạy trên dữ liệu của ta" và "nếu ta chạy trên dữ liệu của họ"

| Đối thủ | **Họ trên dữ liệu ta** (22 chủ thể / CinC 60 sạch) | **Ta trên dữ liệu họ** | Vì sao chưa |
|---|---|---|---|
| Power-MF 4 kênh | **ĐÃ LÀM** — chạy lại 22 chủ thể (98,83), kiểm chứng B1 99,40 vs 99,46 | **ĐÃ LÀM** với B1/B2 (cùng bộ). NInFEA: **chưa** | NInFEA chưa tải; dung sai của họ trên NInFEA là 200 ms, khác ta |
| Power-MF 1 kênh | **ĐÃ LÀM** — 22 chủ thể (86,71) và CinC 60 sạch (55,97) | — (biến thể của ta) | — |
| TS / TS-PCA / Prominence | **MỘT PHẦN** — chỉ 5 chủ thể ADFECGDB; **chưa** chạy trên 17 chủ thể Silesia và CinC | — (mốc chuẩn tự cài, không có "dữ liệu của họ") | Không có lý do kỹ thuật; chưa bố trí. Chi phí thấp (mã đã có trong `baselines/`) |
| DPSS | **CHƯA** — họ tự công bố 97,7 trên 22 bản Silesia (bài gọi là "ADFECGDB"; không phải ADFECGDB cổ điển 5 bản), nhưng theo đơn vị tín hiệu, kênh chọn tay và zero-shot; ta chưa chạy DPSS trên 22 chủ thể | **MỘT PHẦN** — NIFECGC = CinC set-a: ta có 60 sạch, họ 95,3 trên tập con không nêu. FECGSYNDB (tổng hợp): **chưa** | Chưa chạy lại DPSS (2–3 ngày); FECGSYNDB là dữ liệu tổng hợp, ta chưa tải; không rõ họ chấm bản nào của set-a |
| CUNet | **KHÔNG THỂ** — không mã, không đủ tham số để cài lại | **KHÔNG THỂ** — dữ liệu mô phỏng điện cực khô của họ tự tạo, không công khai (theo bài: "không có bộ công khai nào dùng điện cực khô") | Không mã, không dữ liệu. Chỉ so trên CinC: họ 75 bản, ta 60 |
| Castillo 2018 | **CHƯA** — họ tự công bố ADFECGDB (5 chủ thể chung), trong mẫu | **ĐÃ** — cùng ADFECGDB (ta 99,40 LOSO). CinC của họ nhiễm → không so | Số ADFECGDB của họ trong mẫu, chạy lại cũng không cùng giao thức |
| Behar / Varanini / Sulas | **ĐÃ CÓ SỐ** trên B1/B2/CinC — do **Jaeger** chạy lại trong repo benchmark, không phải ta | **ĐÃ** — cùng B1/B2/CinC | Ta chưa tự chạy mã của họ trong repo Jaeger; số là trích |

**Tóm tắt mục 5:** đối thủ duy nhất mà cả hai chiều đều hoàn tất là **Power-MF**. Với DPSS, chiều "họ trên dữ liệu ta" tồn tại dưới dạng số tự công bố (97,7 trên 22 bản Silesia, bài gọi là "ADFECGDB") nhưng theo giao thức khác; chiều "ta trên dữ liệu họ" tồn tại một phần qua CinC. Với CUNet cả hai chiều đều bị chặn bởi thiếu mã và thiếu dữ liệu.

---

## 6. Hạn chế của chính tài liệu này

1. Ba số "60 bản sạch" cho Power-MF 4 kênh (93,12), Varanini (96,32), Behar (55,01), Sulas (47,70) là **ta lọc** từ số per-record của tác giả trong `baselines/powermf_published.json`, không phải ta chạy lại; bộ chấm là `Bxb_compare` của họ, chưa đối chiếu với `match_events` của ta trên CinC. Đây là số **dẫn xuất**, chưa có trong `facts_phase4.json`.
2. Nhận định "Varanini có thể đã chỉnh tham số trên set-a" là **suy luận** từ việc họ là đội dự thi, chưa đọc bài gốc.
3. Nhận định "15 bản nhiễm là bản dễ nên CUNet 77,8 được lợi" là **suy luận** từ Power-MF (98,88 trên 15 vs 93,12 trên 60); chưa có số CUNet theo từng bản.
4. Tình trạng mã công khai của DPSS **chưa xác minh** trong tệp survey; câu "chưa chạy lại vì chưa bố trí" là lý do thật, không phải "không thể".
5. Tiêu chí chính thức của CinC 2013 là sai số FHR (bpm²) và RR (ms), **không phải** F1 ±50 ms (`bang_baihoc.tex` p20). Mọi F1 "trên CinC 2013" trong tài liệu này — của ta lẫn của họ — đều là chấm lại, không phải bảng xếp hạng cuộc thi.
6. TS/TS-PCA/Prominence là cài lại theo mô tả, không có số gốc để kiểm chứng ngoài; kết luận "RelyFetal hơn TS 11,53 điểm" có KTC t chứa 0.

---

## 7. Nguồn

`baselines/BASELINES.md` · `baselines/powermf_fair_stats.json` · `baselines/powermf_1ch.json` · `baselines/powermf_published.json` · `baselines/results.json` · `benchmark_dpss/eval_cinc60_sach.json` · `analysis/STATS.md` · `analysis/KIENTRUC.md` · `analysis/DULIEU.md` · `analysis/ABLATION_B1.md` · `analysis/XACNHAN.md` · `analysis/LUONGCUC.md` · `analysis/CHONKENH.md` · `pilot_evidence/sample_efficiency.json` · `model/train_12.json` · `model/train_22.json` · `survey/facts_phase4.json` · `survey/facts_verified.json` · `survey/ro_ri_vanlieu.json` · `survey/RO_RI_VANLIEU.md` · `de_cuong_latex/tables/bang_baihoc.tex` (p11, p13, p14, p17, p20) · `HANDOFF.md` §8, §10, §11.
