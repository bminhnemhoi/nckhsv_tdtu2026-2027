# Bối cảnh văn liệu: một kênh so với đa kênh — họ làm được đến đâu, ta đứng ở đâu

Ngày lập: 17/09/2026 · Commit tham chiếu: b158507 · Người lập: nhóm RelyFetal (Ngô Bình Minh, TDTU).

**Nguồn của mọi con số.** Số của các bài đọc: `de_cuong_latex/bao_cao_30_paper.tex` (mục p##) và `survey/survey_raw.json`; số của nhóm: `survey/facts_phase4.json` (nguồn sự thật duy nhất), `baselines/powermf_fair_stats.json`, `analysis/recovery_ratio.json`; số Power-MF/Varanini công bố: `baselines/powermf_published.json` và `survey/scout_baselines.md`; bảng bài bị nhiễm: `survey/ro_ri_vanlieu.json`. Khi ghi chú đọc bài không nêu một con số, tài liệu này ghi "không nêu" thay vì đoán. Các số đã rút (mục `Z_DA_RUT`) không xuất hiện ở đây.

Quy ước: **fact** = có trong ghi chú đọc bài hoặc JSON trên đĩa; **suy luận** = nhóm tự rút ra, ghi rõ; **giả thuyết** = chưa có phép đo.

---

## 0. Trả lời ngắn cho ba câu hỏi của chủ nhiệm

1. **Vì sao một kênh.** Vì mục tiêu ứng dụng là miếng dán/đai đeo theo dõi tại nhà, và vì đa kênh có hai cái giá: nhiều điện cực hơn (4 bụng ở Power-MF/Behar, 8 kênh để BSS bão hoà ở Andreotti 2016, 12 kênh ở Wahbah 2024, 24 bụng + 3 ngực ở NInFEA) và tách nguồn mù (ICA/PCA/SVD) chỉ chạy được khi có nhiều kênh độc lập. Chi tiết mục 4.
2. **So với bốn kênh thế nào.** Trên cùng 22 sản phụ, cùng bộ chấm ±50 ms, Power-MF 4 kênh (chạy lại qua Octave) đạt 98,83; RelyFetal một kênh đạt 97,56; hiệu −1,27 [−3,08; +0,27], p = 0,156, thắng 18/22 chủ thể. Khi cắt Power-MF về một kênh nó chỉ còn 86,71: tách nguồn đa kênh đáng giá 12,12 điểm cho chính Power-MF, và mạng một kênh lấy lại 10,85 điểm, tức 89,49 % [81,4; 103,2]. Chi tiết mục 3.
3. **Các bài làm một kênh thì sao.** Trong 30 bài đã đọc có 9 bài thuần đơn kênh bụng và 2 bài "đơn kênh bụng + kênh ngực mẹ". Trong miền, số họ công bố nằm trong khoảng 94–99,7 và ta ở cùng khoảng đó (99,40 trên 5 sản phụ ADFECGDB; 97,56 trên 22). Ngoài miền (CinC 2013 set-a, không tinh chỉnh) họ công bố 77,8–98,1 nhưng **không bài nào chấm trên cùng tập bản ghi với ta**: hoặc chọn tập con (Castillo 26/75 bản, Asadi 80/300 kênh), hoặc chọn kênh bằng tay (DPSS), hoặc tập chấm còn chứa bản sao ADFECGDB (Mohebbian 69 bản, Orvas 75 bản). Trên 60 bản sạch ta đạt 74,28 (quy tắc PSD, mốc cũ), 80,72 (`gate`, quy tắc kế hoạch chọn làm phép thử xác nhận, trượt Holm p 0,051), 81,01 (`gate4`, có trong danh sách ghi trước, sống sót Holm p 0,015), 82,01 (`peakprob`, hậu kiểm), 83,60 (oracle). Kết luận thẳng: **trong miền ngang tầm; ngoài miền thấp hơn số công bố của đa số bài đơn kênh, và không có bài nào so đầu-đối-đầu được.** Chi tiết mục 2.

---

## 1. VIỆC 1 — Bảng 30 bài xếp theo số kênh đầu vào

Cột "Kênh": số kênh ECG bụng đưa vào thuật toán (không tính kênh da đầu thai chỉ dùng làm nhãn). Cột "So trực tiếp với ta?": cần đủ ba điều kiện — cùng bộ dữ liệu, cùng dung sai, cùng đơn vị (nhịp). Thiếu một điều kiện là "một phần"; thiếu hai trở lên hoặc khác bài toán là "không".

### 1a. Nhóm đơn kênh bụng (9 bài)

| Mã | Tác giả–năm | Kênh vào | Phương pháp lõi | Bộ dữ liệu | Chỉ số + dung sai | Kết quả họ báo cáo | So trực tiếp với ta? |
|---|---|---|---|---|---|---|---|
| p01 | Zhong 2018, Physiol Meas | **1** (cửa sổ 100 mẫu đơn kênh; kênh chọn bằng SampEn) | CNN 1D 3 lớp, phân loại cửa sổ 100 ms | CinC 2013 set-a, 68 bản (loại 7), chia cố định 55/6/7 bản | Precision/Recall/F1 **mức cửa sổ 100 ms**, không khớp nhịp | F1 77,85 %, Acc 77,38 % | **Không**: đơn vị là cửa sổ đã cân bằng lớp, không phải nhịp ±50 ms |
| p03 | Mohebbian 2022, IEEE JBHI | **1** ("1 Abdominal" trong Bảng III; kênh nào không nêu) | CycleGAN 1D + attention, tái tạo fECG rồi dò đỉnh | ADFECGDB 5 sản phụ (LOSO); NIFECGDB 14; CinC set-a 69 bản | F1 theo nhịp, dung sai **30 ms** | ADFECGDB 99,7 ± 0,4; CinC ngoại kiểm 94,7 [92,6; 96,5] | **Một phần**: cùng bộ ADFECGDB + LOSO + đơn kênh nhưng dung sai 30 ms ≠ 50 ms; CinC 69 bản còn 15 bản sao ADFECGDB (họ huấn luyện trên ADFECGDB → bị nhiễm) |
| p05 | Shokouhmand & Tavassolian 2023, IEEE TBME (DPSS) | **1** (kênh "có fECG rõ nhất", chọn thủ công) | Dual-Path RNN tách nguồn + GAN khử nhiễu, dò đỉnh Pan-Tompkins trên fECG tái tạo | Huấn luyện FECGSYNDB; kiểm zero-shot Silesia 22 ca (10 thai kỳ + 12 chuyển dạ) và CinC set-a 69 bản | F1 theo nhịp, **50 ms**; FHR precision ±5 bpm | Silesia 22: F1 97,7; CinC 69: 95,3 | **Một phần, gần nhất trong các bài đơn kênh**: cùng 22 sản phụ Silesia, cùng 50 ms, cùng nhịp, cùng đơn kênh; khác: kênh chọn bằng tay (dạng oracle), đơn vị lấy trung bình theo kênh/đoạn, số chưa chạy lại, bảng có mâu thuẫn nội tại (Se 86,23 / PPV 95,75 không ra F1 93,43) |
| p06 | Chen 2025, Sensors | **1** (chạy riêng từng kênh) | Attention R2W-Net tái tạo fECG + Pan-Tompkins | FECGSYNDB (1 fold); ADFECGDB **tinh chỉnh trên chính bộ**; PCDB; NIFECGDB | F1 theo nhịp, dung sai **31,25 ms** | ADFECGDB 99,17; PCDB 98,03; NIFECGDB 97,08 | **Không**: tinh chỉnh trên tập đích, cách chia không nêu, dung sai khác |
| p07 | Asadi 2025, IEEE Access (SCTD-Net) | **1** (MECG do mạng tự ước lượng, không phải kênh thứ hai) | U-Net 1D + CNN 2D trên ma trận trễ, Pan-Tompkins | Huấn luyện FECGSYN 55.000 đoạn; kiểm zero-shot PCDB (80/300 kênh chọn) và ADFECGDB (17/20 kênh) | F1 theo nhịp, **50 ms**; đơn vị = kênh | PCDB 97,97; ADFECGDB 96,52 | **Một phần**: cùng 50 ms, cùng đơn kênh, cùng ADFECGDB; khác đơn vị (kênh ≠ chủ thể), loại 3 kênh; PCDB chỉ 80 kênh chọn |
| p09 | Xu 2026, Sensors | **1** | EEMD hai lần + CNN chọn IMF | 15 ca mô phỏng + 5 ADFECGDB (LOSO cho bộ chọn IMF); DaISy 2 kênh; NIFEA 2 ca | AUC mức IMF; F1 dò đỉnh trên 4 ca lẻ, **dung sai không nêu** | AUC 0,9282 ± 0,0189; F1 0,84–0,96 | **Không**: không có F1 trên ADFECGDB, không dung sai |
| p11 | Orvas 2025, arXiv (CUNet) | **1** (kênh nào của CinC không nêu) | UNet giá trị phức trên STFT, huấn luyện in-silico | 10.000 bản mô phỏng; kiểm zero-shot CinC set-a **đủ 75 bản** | F-score theo nhịp, **50 ms** | CinC 75: 77,8 ± 18,6; EKF cổ điển 80,0 | **Có điều kiện**: cùng 50 ms, nhịp, đơn kênh, zero-shot; nhưng 75 bản ≠ 60 bản sạch — xem mục 2.3 |
| p16 | Niknazar 2013, IEEE TBME | **1** (par-EKF; ca song thai cần Fast-ICA đa kênh để lấy nhãn) | Kalman mở rộng, mô hình 5 Gauss | Tổng hợp; DaISy 1 bản 10 s; NIFECGDB 1 sản phụ | Cải thiện SNR/SIR (dB); **không có Se/PPV/F1** | SNR +20 đến +40 dB (mô phỏng) | **Không**: khác bài toán (tách/tăng cường, cần đỉnh R thai đầu vào) |
| p17 | Castillo 2018, PLoS ONE | **1** (thực sự đơn kênh, không kênh ngực) | Wavelet + k-medoids 3 cụm, sửa RR | ADFECGDB (huấn luyện, 17/20 tín hiệu bác sĩ chọn); CinC set-a **26/75 bản** bác sĩ chọn | Se/PPV/F1 theo nhịp, **50 ms**; trong mẫu | ADFECGDB 94,11 (17 tín hiệu) / 98,04 (11 sạch) / 98,63 (kênh tốt nhất); CinC 98,07 (64 tín hiệu) | **Có, nhưng lệch giao thức**: cùng bộ, cùng 50 ms, cùng nhịp, cùng đơn kênh; khác: trong mẫu, không tách bản ghi, lọc kênh/bản bằng bác sĩ |

### 1b. Nhóm "một kênh bụng + kênh ngực mẹ tham chiếu" (2 bài)

| Mã | Tác giả–năm | Kênh vào | Phương pháp lõi | Bộ dữ liệu | Chỉ số + dung sai | Kết quả họ | So trực tiếp? |
|---|---|---|---|---|---|---|---|
| p13 | Behar 2014, luận án Oxford (Chương 6) | **1 bụng + 1 ngực mẹ** (Chương 7: 4 bụng) | Trừ mẫu / LMS / RLS / ESN, dò Pan-Tompkins | CRDB1 (14 bản NIFECGDB) huấn luyện; CRDB2 (11 bản, 8 sản phụ, riêng tư) kiểm | F1 theo nhịp, **50 ms** (nguồn gốc chuẩn ta dùng) | CRDB2: ESNa 90,2; TSpca 89,3 | **Một phần**: cùng thang đo; khác bộ (riêng tư) và có kênh ngực |
| p19 | Sulas 2020, Math Biosci Eng | SR: **1 bụng + 1 ngực**; MR: 1 bụng + 3 ngực | QRD-RLS thích nghi | NInFEA riêng tư, 20 thai phụ tuần 21–27, nhãn Doppler | Acc = (TP+TN)/…, **dung sai không nêu** | SR ≈ 0,68 trung bình; MR 0,85–0,92 | **Không**: chỉ số, nhãn, dung sai đều khác |

### 1c. Nhóm đa kênh (7 bài)

| Mã | Tác giả–năm | Kênh vào | Phương pháp lõi | Bộ dữ liệu | Chỉ số + dung sai | Kết quả họ | So trực tiếp? |
|---|---|---|---|---|---|---|---|
| p04 | Basak 2024, Expert Syst Appl | **4** | 1D-CycleGAN tái tạo fECG, dò EngZee | ADFECGDB + Silesia gộp, 5-fold không nêu cách chia | F1 theo nhịp, **31,25 ms** | F1 96,4 | **Không**: 4 kênh, dung sai khác, nghi chia theo đoạn |
| p10 | Esmaeili Alidash 2025, Sci Rep | **4** đồng thời | CNN phân loại ô 100 ms, 31,4 M tham số | CinC set-a 25 hoặc 60 bản, chia ngẫu nhiên có xáo trộn | Accuracy/F1 **mức ô 100 ms** | Acc 98,36 (25 bản) / 96,79 (60 bản) | **Không**: 4 kênh, đơn vị ô, trong bộ |
| p12 | Wahbah 2024, Front Physiol | **12** | BiLSTM phân loại đoạn 65 ms | 70 sản phụ, 3 bệnh viện, riêng tư; nhãn từ thuật toán BSSR | Accuracy đoạn 65 ms, **không dung sai** | Tách chủ thể 88,8 ± 6,4 | **Không** |
| p14 | Behar 2014, Physiol Meas (FUSE) | **4** + 5 thuật toán song song | Trừ mẫu, ICA/PCA, FUSE chọn đầu ra mượt nhất | CinC set-a 68 bản, tham số quét trên chính set-a | F1 theo nhịp, **50 ms**, trong mẫu | FUSE-SMOOTH 96,0; TS thuần 81,6; ICA 63,7; PCA 51,6 | **Một phần**: cùng thang đo, cùng bộ; khác 4 kênh, trong mẫu, loại 7 bản |
| p15 | Andreotti 2016, Physiol Meas | BSS **8–32**; AM "đơn kênh" nhưng cần kênh mẹ | Khung stress-test FECGSYNDB, 8 thuật toán | Mô phỏng 145,8 h; chọn kênh **oracle** theo nhãn | F1 theo nhịp, **50 ms**; MAE | BSSica trung vị 99,9; 8 kênh 97,46; bão hoà ≥ 8 kênh | **Không** về số (mô phỏng + oracle); có về dung sai |
| p20 | Clifford 2014, Physiol Meas (xã luận CinC 2013) | **4** (dữ liệu thi) | Tổng kết 53 đội | 447 bản, 5 nguồn (ADFECGDB 25) | Điểm E1–E5 (bpm², ms); **không F1, không dung sai** | E1 179,4; E2 20,8 ms | **Không** về số; cùng bộ set-a |
| p21 | Matonia 2020, Sci Data | **4** (PCA/ICA) | Công bố bộ Silesia B1/B2; PCA, ICA | B2 12 bản chuyển dạ, nhãn da đầu | F1 theo nhịp, **40 ms** | PCA 98,56; ICA 98,55 | **Một phần**: cùng B2, khác dung sai, đa kênh |

Ngoài 30 bài: **Jaeger 2024, Power-MF** (Physiol Meas 45:055009) — **4 kênh**, SVD + ICA khử mẹ, chọn kênh PSD, matched filter; số công bố B1 99,46 / B2 97,98 / CinC 75 94,27; **đã chạy lại** qua Octave và chấm bằng bộ chấm ±50 ms của nhóm → so trực tiếp được (mục 3).

### 1d. Không áp dụng — không phải bài ECG bụng (12 bài)

| Mã | Tác giả–năm | Kênh | Vì sao không xếp |
|---|---|---|---|
| p22 | Perea & Harer 2015 | — | Lý thuyết cửa sổ trượt + đồng điều bền vững, dữ liệu tổng hợp |
| p23 | Adams 2017 | — | Persistence Image, đám mây điểm |
| p24 | Carrière 2020 | — | PersLay, đồ thị/quỹ đạo |
| p25 | Som 2020 | — | PI-Net, gia tốc kế và ảnh |
| p26 | Turkes 2022 | — | Hiệu quả PH trên hình dạng |
| p27 | Trần & Hasegawa 2019 | 1 chuỗi/mẫu (UCR NonInvasiveFetalECGThorax1/2) | Phân loại 42 lớp hình thái, không dò đỉnh |
| p28 | Tan 2023 | — | Chọn độ trễ nhúng |
| p29 | Ren 2023 | 12 chuyển đạo người lớn | Đánh giá chất lượng ECG, không thai |
| p30 | Dindin 2019 | 1 chuyển đạo người lớn | Phân loại loạn nhịp MIT-BIH |
| p31 | Chung 2020 | chuỗi HRV | Phân loại giấc ngủ |
| p32 | Dominguez-Monterroza 2025 | chuỗi RR | HRV nhi khoa |
| p33 | Karan & Kaygun 2021 | ECG/ACC WESAD | Phân loại căng thẳng |

**Tổng kết:** đơn kênh bụng 9 · đơn kênh + ngực mẹ 2 · đa kênh 7 · không áp dụng 12 · không rõ trong ghi chú 0 (riêng p03 và p11 ghi "1 kênh" nhưng không nêu kênh nào).

---

## 2. VIỆC 2 — Các bài đơn kênh làm được đến đâu, và ta đứng ở đâu

### 2.1 Điều kiện họ đạt được con số (fact, theo ghi chú đọc bài)

| Bài | Bộ / số chủ thể | Dung sai | Điện cực ngực mẹ? | Tinh chỉnh trên tập kiểm? | Chọn kênh | Ghi chú giao thức |
|---|---|---|---|---|---|---|
| p17 Castillo 2018 | ADFECGDB 5 sản phụ, 17/20 tín hiệu; CinC 26/75 bản | 50 ms | Không | Siêu tham số dò trên ADFECGDB rồi báo cáo trên ADFECGDB (trong mẫu) | Bác sĩ loại tín hiệu xấu; báo cáo cả "kênh tốt nhất" | Không tách bản ghi; loại 49/75 bản CinC |
| p03 Mohebbian 2022 | ADFECGDB 5 (LOSO); CinC 69 | 30 ms | Không | Không (LOSO); CinC ngoại kiểm sau khi huấn luyện toàn bộ ADFECGDB | Không nêu | 15/69 bản CinC là bản sao ADFECGDB (`ro_ri_vanlieu.json`) |
| p05 DPSS 2023 | Silesia 22 ca (10 + 12); CinC 69 | 50 ms | Không | Không (huấn luyện chỉ trên FECGSYNDB) | **Thủ công**, kênh "rõ nhất" | Trung bình theo kênh/đoạn; không CI, không p |
| p06 Chen 2025 | ADFECGDB 5 | 31,25 ms | Không | **Có** — tinh chỉnh trên tập con ADFECGDB, báo cáo cả 5 bản | Từng kênh | Cách chia không nêu |
| p07 Asadi 2025 | ADFECGDB 17 kênh; PCDB 80 kênh | 50 ms | Không | Không (zero-shot từ FECGSYN) | Loại 3 kênh nhiễu theo tiền lệ RCED-Net | Đơn vị = kênh |
| p11 Orvas 2025 | CinC 75 bản | 50 ms | Không | Không (in-silico) | Không nêu | SD ±18,6 rất lớn |
| p09 Xu 2026 | ADFECGDB 5 (chỉ AUC IMF); 4 ca lẻ | Không nêu | Không | Không | Tự chọn kênh 2, 3 của DaISy | Không có F1 trên ADFECGDB |
| p01 Zhong 2018 | CinC 68 bản, chia cố định | Cửa sổ 100 ms | Không | Không | SampEn | Đơn vị cửa sổ |
| p16 Niknazar 2013 | 1 bản DaISy, 1 sản phụ NIFECGDB | — | Không (nhưng nhãn song thai cần ICA đa kênh) | — | — | Không có F1 |

### 2.2 Trên cùng một bộ, ta đứng ở đâu

**ADFECGDB (5 sản phụ chuyển dạ, ±50 ms, nhịp).**
- Ta: 99,40 trung bình 5 chủ thể (mô hình 22 ca, kênh chọn mù; `baselines/powermf_fair_stats.json` → `per_subject`, nhóm ADFECGDB), từng ca 99,92 / 99,68 / 100,00 / 99,77 / 97,61. Số cũ của mô hình 5 ca: macro F1 97,43 ± 4,37 trên đủ 4 đạo trình, 99,18 kênh chọn theo PSD (`survey/facts_verified.json`).
- Castillo 2018 (đơn kênh, 50 ms, trong mẫu): 94,11 toàn bộ 17 tín hiệu; 98,63 kênh tốt nhất → ta cao hơn ở cả hai mức, với giao thức tách chủ thể chặt hơn. Đây là phép so gần nhất đủ ba điều kiện, nhưng số của họ là trong mẫu và đã loại 3/20 tín hiệu.
- Mohebbian 2022 (đơn kênh, LOSO, **30 ms**): 99,7 ± 0,4 → cao hơn ta 0,3 điểm ở dung sai chặt hơn; **không kết luận được** vì chưa đo lại ở 30 ms (`survey/facts_verified.json` liệt kê việc này trong `gioi_han_phai_khai_bao`).
- Asadi 2025 (đơn kênh, 50 ms, zero-shot, đơn vị kênh): 96,52 trên 17 kênh → ta cao hơn nhưng khác đơn vị và khác nguồn huấn luyện (họ không thấy dữ liệu thật).
- Chen 2025: 99,17 nhưng tinh chỉnh trên tập đích → không đặt cạnh.

**Silesia 22 sản phụ (±50 ms, nhịp).**
- Ta: 97,56 (22 chủ thể, kênh chọn mù; `facts_phase4.json` → `D_22_chu_the`).
- DPSS (đơn kênh, kênh chọn thủ công, huấn luyện FECGSYNDB): 97,7 trên "22 ca" theo mô tả của họ. Hai số gần nhau, nhưng (fact) họ chọn kênh bằng tay, (fact) số chưa chạy lại, (fact) bảng của họ có mâu thuẫn nội tại. **Suy luận:** đây là mốc đơn kênh gần nhất với ta trên cùng quần thể; muốn nói hơn/kém phải chạy lại DPSS (HANDOFF mục 10, việc 6).

**CinC 2013 set-a, không tinh chỉnh (±50 ms, nhịp).**
- Ta trên 60 bản sạch: PSD 74,28 [66,63; 81,78]; `gate` 80,72 (quy tắc kế hoạch chọn, trượt Holm p 0,051); `gate4` 81,01 (p Holm 0,015); `peakprob` 82,01 (hậu kiểm); oracle chọn kênh 83,60 (`facts_phase4.json` → `A_cinc2013_60_ban_sach`, `B_chon_kenh_7_quy_tac_60_sach`).
- Họ: Orvas 77,8 ± 18,6 (75 bản); Mohebbian 94,7 (69 bản, 15 bản nhiễm); DPSS 95,3 (69 bản, kênh thủ công); Asadi 97,97 (80/300 kênh chọn); Castillo 98,07 (26/75 bản bác sĩ chọn).
- **Không so trực tiếp được** với bất kỳ bài nào: không ai chấm trên 60 bản sạch với kênh chọn mù. Ngay cả oracle của ta (83,60) vẫn thấp hơn số công bố của Mohebbian/DPSS/Asadi/Castillo, nên (suy luận) khoảng cách không chỉ do chọn kênh; **nguyên nhân chưa xác định** (`analysis/CHANDOAN_MOHINH.md`: phép thử nhìn thấy có âm tính giả 18 %).

### 2.3 Orvas 2025 (CUNet) đối chiếu với 74,28 / 80,72 / 81,01 / 82,01 của ta — có so được không?

**Fact về Orvas** (`bao_cao_30_paper.tex` mục p11; `ro_ri_vanlieu.json`): chấm **đủ 75 bản set-a**, không loại bản nào; huấn luyện in-silico nên với họ 15 bản ADFECGDB **không phải rò rỉ**; dung sai 50 ms; đơn vị nhịp; F-score = 2TP/(2TP+FN+FP); đơn kênh nhưng không nêu kênh nào; SD ±18,6; EKF cổ điển của chính họ đạt 80,0.

**Fact về ta:** 60 bản sạch; kênh chọn theo quy tắc mù; SD 30,57; 33/60 bản ≥ 90, 16/60 bản < 50, trung vị 95,07.

**Kết luận:** so được **có điều kiện, không đầu-đối-đầu**. Bốn điều kiện khớp (dung sai, đơn vị, đơn kênh, zero-shot); hai điều kiện lệch: (i) 75 ≠ 60 bản — 15 bản ADFECGDB nhìn chung dễ (chúng thổi phồng trung bình của ta 3,27–7,18 điểm), nên nếu Orvas cũng bỏ 15 bản đó số của họ có thể giảm, nhưng không biết bao nhiêu; (ii) họ không nêu kênh. Cách trình bày trung thực: đặt 77,8 ± 18,6 (75 bản) cạnh 74,28 [66,63; 81,78] (60 bản, PSD), 80,72 (60 bản, `gate`, quy tắc kế hoạch chọn, trượt Holm p_Holm 0,051), 81,01 (60 bản, `gate4`, khai báo trước, p_Holm 0,015) và 82,01 (60 bản, `peakprob`, hậu kiểm, p_Holm 0,0039), kèm trần oracle 83,60, trong cùng bảng, chú thích "khác tập bản ghi", và ghi nhận rằng 77,8 nằm **trong** khoảng tin cậy 95 % của quy tắc PSD. Không được viết "ngang Orvas" hay "vượt Orvas".

### 2.4 Kết luận thẳng cho VIỆC 2

- Trên ADFECGDB, ta ở trên Castillo 2018 (đơn kênh, cùng dung sai) và ngang mức các bài tái tạo dạng sóng đơn kênh; chỉ Mohebbian 2022 nhỉnh hơn ở dung sai 30 ms chưa đo lại.
- Trên Silesia 22, DPSS 97,7 (kênh tay) và ta 97,56 (kênh mù) gần nhau; chưa chạy lại DPSS nên chưa kết luận.
- Trên CinC set-a, **không có bài đơn kênh nào cùng tập + cùng cách chọn kênh** với ta; so với quy tắc PSD của ta (74,28), số công bố của họ cao hơn 3,52 (Orvas 77,8) đến 23,79 điểm (Castillo 98,07); so với `peakprob` hậu kiểm (82,01), bốn số Mohebbian 94,7 / DPSS 95,3 / Asadi 97,97 / Castillo 98,07 cao hơn 12,69–16,06 điểm, còn Orvas 77,8 **thấp hơn** 4,21 điểm (và thấp hơn cả `gate` 80,72, `gate4` 81,01). Mọi số công bố đó đều có ít nhất một trong ba yếu tố: tập con chọn tay, kênh chọn tay, hoặc tập chấm có bản sao dữ liệu huấn luyện. Đây là câu trả lời hợp lệ, không ép.

---

## 3. VIỆC 3 — Đa kênh được gì, và cái giá

| Phương pháp | Kênh | Bộ / n | Dung sai | F1 | Nguồn số | Cái giá |
|---|---|---|---|---|---|---|
| **Power-MF (Jaeger 2024), ta chạy lại** | 4 bụng | 22 chủ thể (5 + 7 + 10) | 50 ms, bộ chấm của nhóm | **98,83** | `powermf_fair_stats.json` | SVD + 2 lần ICA đa kênh (bước 4 và 8 trong `scout_baselines.md` mục 3.1); chọn kênh PSD; kiểm chứng ngoài B1 99,40 vs 99,46 công bố |
| Power-MF công bố | 4 | B1 10 / B2 12 / CinC 75 | 50 ms (Bxb) | 99,46 / 97,98 / 94,27 | `powermf_published.json` | như trên |
| Varanini 2014 (số do Jaeger chạy lại trong repo benchmark, không phải số Varanini tự công bố) | 4 | B1 / B2 / CinC 75 | 50 ms (Bxb) | 99,37 / 97,95 / 97,04 | `powermf_published.json → b1_varanini, b2_varanini, challenge_varanini`; `scout_baselines.md` mục 0.3 | ICA đa kênh, MATLAB |
| Behar 2014 FUSE-SMOOTH | 4 + 5 thuật toán song song | CinC set-a 68 | 50 ms, trong mẫu | 96,0 | p14 | Chạy 5 bộ tách rồi chọn; tham số quét trên chính set-a |
| Matonia 2020 PCA / ICA | 4 | Silesia B2 12 | 40 ms | 98,56 / 98,55 | p21 | Tách nguồn mù bắt buộc 4 kênh |
| Andreotti 2016 BSSica | 8 (bão hoà ≥ 8) | FECGSYNDB mô phỏng | 50 ms, chọn kênh oracle | trung vị 99,9; 8 kênh 97,46 | p15 | 8 kênh; oracle theo nhãn; không có dữ liệu thật |
| Wahbah 2024 | 12 | 70 sản phụ riêng tư | đoạn 65 ms | Acc 88,8 ± 6,4 | p12 | 12 điện cực, thiết bị riêng 3 bệnh viện, không công khai |
| Sulas 2020 MR | 1 bụng + 3 ngực (6 điện cực ngực) | NInFEA riêng | không nêu | Acc 0,85–0,92 | p19 | Điện cực ngực; SR (1 ngực) chỉ 0,68 |
| Esmaeili Alidash 2025 | 4 | CinC set-a trong bộ | ô 100 ms | Acc 96,79 | p10 | 31,4 M tham số; chia ngẫu nhiên |

**Luận đề của ta, đo trên cùng 22 chủ thể** (`analysis/recovery_ratio.json`, `powermf_fair_stats.json` → `so_sanh.tat_ca_22`):
- Power-MF 4 kênh − Power-MF 1 kênh = **12,12** điểm [+6,90; +18,27], p = 1,4e-06, 4 kênh thắng 21/22 → **tách nguồn đa kênh đáng giá 12,12 điểm cho chính Power-MF**.
- RelyFetal 1 kênh − Power-MF 1 kênh = +10,85 [+6,80; +15,40], p = 4,8e-07, thắng 22/22 → mạng một kênh **lấy lại 89,49 %** [81,4; 103,2] lợi ích đa kênh (jackknife bỏ từng chủ thể 88,6–93,4 %).
- Phần chưa lấy lại: −1,27 [−3,08; +0,27] so với 4 kênh, p = 0,156 — khoảng tin cậy chạm 0, chưa đủ mẫu để nói bằng hay kém (cần n ≈ 50, `facts_phase4.json`).
- Theo nhóm: ADFECGDB ta 99,40 vs 4 kênh 99,01 (5/5, p = 0,0625 — p nhỏ nhất khả thi với n = 5); B2 96,82 vs 97,90; B1 97,15 vs 99,40.
- Ngoài miền (60 bản CinC sạch): Power-MF 1 kênh chỉ 55,97 [48,08; 64,03]; ta hơn +18,32 [13,35; 23,64] (`A_cinc2013_60_ban_sach.powermf_1ch_60_sach`). Power-MF 4 kênh trên 60 bản sạch: 93,12, là số dẫn xuất do nhóm lọc 15 bản nhiễm khỏi kết quả từng bản của tác giả (`baselines/powermf_published.json → sets.challenge_powermf.per_record`), chấm bằng `Bxb_compare` của tác giả, chưa có trong `facts_phase4.json`.

---

## 4. VIỆC 4 — Vì sao một kênh: mỗi ý một câu, có nguồn

**Lâm sàng / ứng dụng**
1. Điện tim bụng mẹ là cách theo dõi liên tục, tại nhà, cho cả hình thái sóng, trong khi CTG/Doppler chỉ cho nhịp và cần kỹ thuật viên đặt đầu dò (`docs/DE_CUONG_HIEN_TRANG.md` mục 3.2–3.3).
2. Cấu hình một đạo trình là cấu hình rẻ nhất và dễ tích hợp vào miếng dán hoặc đai đeo nhất (`DE_CUONG_HIEN_TRANG.md` mục 3.3); hướng điện cực vải khô đeo tại nhà đã được Orvas 2025 theo đuổi với đúng cấu hình đơn kênh (p11).
3. Thai chậm phát triển cần đo biến thiên nhịp từng nhịp đến mili-giây, nên thứ cần là vị trí đỉnh, không phải chỉ nhịp trung bình (`docs/TOM_TAT_1_TRANG.md`).

**Hai cái giá của đa kênh**
4. Giá thứ nhất là điện cực: Power-MF/Varanini/Behar cần 4 điện cực bụng (p14, `scout_baselines.md`), BSS chỉ bão hoà từ 8 kênh (p15), Wahbah dùng 12 kênh (p12), NInFEA thu 24 bụng + 3 ngực (`scout_datasets.md` mục 2), và lọc thích nghi đơn tham chiếu vẫn cần điện cực ngực mà chỉ đạt 0,68 (p19).
5. Giá thứ hai là thuật toán: ICA/PCA/SVD đòi số cảm biến ≥ số nguồn nên với một kênh là bài toán thiếu xác định (p05 nêu rõ lý do này), và trong Power-MF hai bước ICA (bước 4, 8) cùng bước chọn kênh (12–13) thành phép rỗng khi chỉ có một kênh (`scout_baselines.md` mục 3.3).
6. Bằng chứng số của giá thứ hai: cắt Power-MF về một kênh làm F1 rơi từ 98,83 xuống 86,71 trên 22 chủ thể, tức 12,12 điểm (`powermf_fair_stats.json`).

**Cái mất khi bỏ kênh, và cái lấy lại**
7. Cái mất đo được là 12,12 điểm [6,90; 18,27] — đó là giá trị của tách nguồn đa kênh cho chính thuật toán mạnh nhất đã chạy lại (`analysis/recovery_ratio.json`).
8. Cái lấy lại là 10,85 điểm, tức 89,49 % [81,4; 103,2], bằng một mạng 113.481 tham số, 0,48 MB, 4,35 ms/cửa sổ trên CPU, không cần điện cực ngực (`facts_phase4.json`, `facts_verified.json` → `mo_hinh`).
9. Phần chưa lấy lại là −1,27 [−3,08; +0,27] so với 4 kênh, chưa phân biệt được với 0 ở n = 22 (`powermf_fair_stats.json`).
10. Cái một kênh không lấy lại được ngoài miền: trên 60 bản CinC sạch, ngay cả chọn kênh oracle cũng chỉ 83,60, và không cách nào trong bốn cách thích nghi miền giúp được: notch thích nghi +0,25 (thắng 8 / thua 10 / hoà 42 bản — không làm tệ đi, nhưng cũng không giúp), còn tự huấn luyện nhãn giả −0,67, AdaBN −1,58, TENT −2,43 làm tệ đi (quy tắc PSD, tính lại trên 60 bản sạch từ `adapt/adapt_results.json → per_record_cinc`, lọc theo danh sách 60 bản trong `benchmark_dpss/eval_cinc60_sach.json`; `analysis/THICHNGHI.md`); nguyên nhân chưa xác định — đây là giới hạn phải khai báo, không phải luận điểm.

**Điều kiện đi kèm**
11. Vì một kênh không có dư thừa để tự sửa, hệ thống phải biết lúc nào nó sai: cổng từ chối 22 ca đạt AUROC trong bản ghi 0,934 [0,872; 0,981], tính trên 11/22 chủ thể có đoạn xấu, nhưng 5/24 quy tắc một đặc trưng cũng đạt được, nên đây là điều kiện cần chứ chưa phải đóng góp riêng (`analysis/GATE22.md`). Cổng 22 ca mới là kết quả phân tích, **chưa chạy trong demo**; đèn trong demo là cổng cũ `fsqi/gate_classical.pkl` hiệu chuẩn trên mô hình 5 ca, AUROC trong bản ghi 0,721 [0,517; 0,898], trung bình trên 5 bản CinC sạch có cả đoạn tốt lẫn xấu (a01 a06 a07 a09 a10), đo khi ghép với mô hình 5 ca; ghép với mô hình 22 ca đang chạy trong demo thì chưa đo lại (`analysis/stats_results.json → comparisons.gate_auroc_cinc.auroc_TRONG_ban_ghi`; `analysis/GATE22.md`; `analysis/STATS.md` §4). Cổng **không độc lập với mạng**: 2 trong 12 chỉ số là xác suất đầu ra của mạng (`peak_prob_mean`, `prob_max`), 4 chỉ số tính trên nhịp do mạng tìm ra (`rr_cv`, `rr_plaus`, `n_det`, `bsqi`), và chỉ số quan trọng nhất là `rr_cv` — độ đều của nhịp do mạng tìm ra (ΔAUROC hoán vị 0,140; kế đến `peak_prob_mean` 0,032) (`fsqi/gate.py`; `analysis/gate22_results.json → cong.permutation_importance_delta_auroc`).

---

## 5. Hạn chế của chính tài liệu này

- Số của các bài chỉ lấy từ ghi chú đọc bài của nhóm; không đọc lại PDF trong lần lập này.
- Số DPSS, Mohebbian, Asadi, Castillo, Orvas là **số trích dẫn**, chưa chạy lại; chỉ Power-MF đã chạy lại.
- Chưa đo RelyFetal ở dung sai 30 / 31,25 / 40 ms nên mọi so sánh với p03, p04, p06, p21 còn bỏ ngỏ.
- Con số 97,43 ± 4,37 (mô hình 5 ca, 4 đạo trình) và 99,40 (mô hình 22 ca, kênh mù) là hai giao thức khác nhau; khi trích phải ghi rõ giao thức.
- Số sản phụ thật trong 60 bản CinC sạch không biết (nguồn hỗn hợp, `ro_ri_vanlieu.json`), nên thống kê mức chủ thể trên CinC không khả thi.
