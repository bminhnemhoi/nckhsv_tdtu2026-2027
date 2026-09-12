# R1 — Rò rỉ CinC 2013 set-a ↔ ADFECGDB: y văn đã ghi nhận chưa, và ai bị nhiễm?

Ngày rà: 2026-09-12. Người rà: tác tử R1 (theo yêu cầu chủ nhiệm Ngô Bình Minh).
Mọi trích dẫn nguyên văn dưới đây lấy từ tệp đã đọc trên đĩa hoặc trang web đã truy cập được;
tệp máy `survey/ro_ri_vanlieu.json` ghi từng nguồn (URL, truy cập được hay không, câu nguyên văn, kết luận).

---

## 0. Kết luận một đoạn

**Kết luận: (B) ở mức bộ dữ liệu, (A) ở mức bản ghi.**

* **(B) — SỰ KIỆN đã được ghi nhận từ 2013.** Ban tổ chức Challenge nói rõ trong bài CinC 2013 (Silva và cộng sự, Bảng 1: "Abdominal and Direct FECG [1] — 25" bản ghi, [1] = Matonia 2006) và trong bài tổng kết Physiol Meas 2014 (Clifford và cộng sự, Bảng 2: "ADFECGDB (Matonia et al., 2006) | 25"). Clifford 2014 còn **nêu đích danh một bài dự thi bị thiên lệch vì lý do này**: *"The authors also used the MIT Abdominal and Direct Fetal Electrocardiogram Database in order to train their algorithm, which may have led to a bias in the results as this database was included in set-a, set-b (and possibly a few records in set-c)."* Su & Wu 2017 (Frontiers) và Matonia 2020 (Sci Data) cũng nhắc lại. **Nhóm đã bỏ sót một cảnh báo đã biết** — thậm chí câu của Clifford đã nằm trong chính ghi chú đọc bài của nhóm (`de_cuong_latex/tables/bang_baihoc.tex`, dòng p20: "trích dẫn chính câu của Clifford về trường hợp Rodrigues") trong khi `analysis/DULIEU.md` mục 12 ghi "nhóm **chưa tìm**".
* **(A) — cái CHƯA nguồn nào ghi (trong phạm vi truy cập được):** bản ghi set-a *nào* là ADFECGDB, chúng là *cửa sổ nào* của bản gốc, và mức thổi phồng con số là bao nhiêu. Không nguồn nào liệt kê 15 định danh a03…a25, cửa sổ 0–60/120–180/240–300 s, hay NCC = 1,0000 đúng thứ tự 4 kênh. Phần này là công việc đo lường của nhóm và **được y văn xác nhận gián tiếp** (25 bản ghi = 5 sản phụ × 5 phút; 15 trong set-a + 10 còn lại trong set-b/c khớp câu "included in set-a, set-b (and possibly a few records in set-c)").
* **Hệ quả cho cách viết:** phải viết *"Như ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014], set-a chứa bản ghi ADFECGDB; chúng tôi xác định bằng đo lường đúng 15 bản ghi nào…"* — **không** được viết "chúng tôi phát hiện rò rỉ".

---

## 1. VIỆC 1 — Nguồn gốc chính thức

### 1.1 Trang PhysioNet challenge-2013 (truy cập được)

URL: https://physionet.org/content/challenge-2013/1.0.0/

Nguyên văn: *"The data were obtained from multiple sources using a variety of instrumentation with differing frequency response, resolution, and configuration"*; *"in all cases they are presented as 1000 samples per signal per second"*; *"a collection of one-minute fetal ECG recordings"*; *"initial set of 25 set A records"* rồi *"supplementary set of 50 more set A records"*; *"the training data set (set A) does not include examples of all of the sources included in the test sets"*. Lời cảm ơn: *"Joachim Behar, Gari Clifford, Marcelino Martinez, Dawid Roj, Reza Sameni, Anton Tokarev, and their colleagues for their generous contributions of data and expertise"*.

**Không** nhắc ADFECGDB / Silesia / Jezewski / Matonia. **Không** ghi bản ghi nào từ nguồn nào.

### 1.2 Trang PhysioNet adfecgdb (truy cập được)

URL: https://physionet.org/content/adfecgdb/1.0.0/

Nguyên văn: *"five women in labor"*; *"Sampling rate: 1 kHz"*; *"five-minute multichannel fetal ECG recordings"*; *"Medical University of Silesia, Poland"*; *"Published: Aug. 9, 2012"*. **Không** nhắc Challenge 2013.

### 1.3 Silva, Behar, Sameni, Zhu, Oster, Clifford, Moody — CinC 2013 (truy cập được, PDF)

URL: http://www.cinc.org/archives/2013/pdf/0149.pdf — *Computing in Cardiology 2013; 40:149–152*, ISSN 2325-8861. **Không có DOI** (Crossref không có bản ghi; IEEE Xplore doc 6712433).

Nguyên văn: *"Data for the challenge consist of a collection of one-minute, four-channel non-invasive FECGs sampled at 1 kHz. The data were obtained from multiple sources using a variety of instrumentation with differing frequency response, resolution, and configuration. The 447 records used in the challenge were drawn from five data collections (Table 1)."*

Bảng 1 nguyên văn ("FECG database reference", Database Name — N records):

| Database Name | N records |
|---|---|
| Abdominal and Direct FECG [1] | 25 |
| Artificially Generated FECGs [2] | 20 |
| Non-Invasive FECG [3] | 14 |
| Ukraine Non-Invasive FECG | 340 |
| Private Scalp FECG Database | 48 |

Tài liệu [1] nguyên văn: *"Matonia A, Jezewski J, Kupka T, Horoba K, Wrobel J, Gacek A. The influence of coincidence of fetal and maternal QRS complexes on fetal heart rate reliability. Medical Biological Engineering Computing 2006;44(5):393–403."*

*"The 447 records were partitioned into three subsets. Training set A contains 75 records; its reference annotations were provided to the participants. Open test set B contains 100 records; ... Hidden test set C contains the remaining 272 records"*.

→ Ban tổ chức **nói rõ nguồn** (ADFECGDB, 25 bản ghi) nhưng **không** nói bản ghi nào rơi vào set A.

### 1.4 Clifford, Silva, Behar, Moody — Physiol Meas 2014 (truy cập được, toàn văn tại `papers/p20_text.txt`)

DOI **đã xác minh Crossref**: 10.1088/0967-3334/35/8/1521 — *Physiological Measurement* 35(8):1521–1536, 2014 (tiêu đề Crossref: "Non-invasive fetal ECG analysis").

Nguyên văn (dòng 77): *"The data sets used for the Challenge were obtained from five different sources, Tab.2, yielding a total of 447 records. Two out of the five databases have been previously made public ((Matonia et al., 2006) and (Goldberger et al., 2000)), and one database was artificially generated ... The other two databases were donated to PhysioNet for this Challenge"*.

Bảng 2 nguyên văn: *"ADFECGDB (Matonia et al., 2006) | 25 ; Simulated FECGs (Behar et al., 2014b) | 20 ; NIFECGDB (Goldberger et al., 2000) | 14 ; Non-Invasive FECG | 340 ; Scalp FECG Database | 48 ; Total | 447"*.

Dòng 96: *"All records were formatted to have a 1 kHz sampling frequency, one minute duration, and four channels of non-invasive abdominal maternal ECG leads. The databases in Tab.2 were re-arranged into three data sets for the Challenge"*.

**Câu quyết định (dòng 149):** *"Rodrigues (2014) employed a Wiener filter which took as the input, the three abominal channels with a number of coeffiecients (91) in order to filter out the MQRS from the fourth channel. The authors also used the MIT Abdominal and Direct Fetal Electrocardiogram Database in order to train their algorithm, which may have led to a bias in the results as this database was included in set-a, set-b (and possibly a few records in set-c)."*

Ghi chú: dòng 68 của cùng bài mô tả ADFECGDB vừa "fs = 250 Hz" vừa "fs = 1 kHz" trong một câu — lỗi nội tại của bài gốc; trang PhysioNet ghi 1 kHz.

### 1.5 Behar — luận án DPhil Oxford (arXiv 1606.01093, toàn văn `papers/p13_thesis.txt`)

Bảng 4.2 nguyên văn: *"ADFECGDB [67] 25 ; NIFECGDB [65] 14 ; AFECGDB [6] 20 ; PNIFECGDB 340 ; PSFECGDB 48 ; Total 447"*. Dòng 2160–2164: *"Joachim formatted and provided the PSFECGDB, NIFECGDB (manual annotation of each individual FQRS was necessary for this database), AFECGDB and the ADFECGDB. In order to objectively compare the approach presented in this thesis (see Chapter 7) ... only the official data provided to the Challenge participants was used for training."* Dòng 5397 lặp lại đúng câu cảnh báo Rodrigues.

### 1.6 Matonia và cộng sự — Sci Data 2020 (toàn văn `papers/p21_...pdf`), DOI xác minh 10.1038/s41597-020-0538-z

Nguyên văn: *"As a result of the work, five selected records from the labour dataset were made available to the scientific community via the PhysioNet portal as The abdominal and direct fetal electrocardiogram database (ADFECGDB). Additionally, in order to unify the sampling frequency, the abdominal signals were resampled to 1kHz. In 2013, those signals were part of the research material in the 'Noninvasive Fetal ECG: the PhysioNet/Computing in Cardiology Challenge' to develop effective methods for analyzing the abdominal fetal electrocardiogram."*

→ Chính tác giả bộ dữ liệu xác nhận ADFECGDB **là** vật liệu của Challenge 2013.

### 1.7 Su & Wu — Frontiers Appl Math Stat 2017 (truy cập được), DOI xác minh 10.3389/fams.2017.00002

Nguyên văn: *"Among 447 records, 25 records are from the adfecgdb [52], so there might be overlapping between the CinC2013 and adfecgdb databases."* Tác giả **không** loại bản ghi nào, chỉ cảnh báo.

### 1.8 Baldazzi & Pani — chương sách Springer (DOI xác minh 10.1007/978-3-031-32625-7_12, trang 221–240)

**Không truy cập được toàn văn** (Springer chuyển hướng cookie; ouci.dntb.gov.ua trả 502). Ghi chú `survey/scout_novelty.md` của nhóm dẫn cụm "shares signals with ADFECGDB" — **chưa xác minh nguyên văn** trong vòng này; chỉ trích dẫn với ghi chú "theo ghi chú đọc nội bộ".

### 1.9 Điều y văn KHÔNG cung cấp

* Danh sách bản ghi set-a theo nguồn (không có tệp SOURCES/README nào; `archive.physionet.org/challenge/2013/set-a/` trả 404).
* Số sản phụ thật trong set-a. Không nguồn chính thức nào nêu. (Một tổng quan MDPI Sensors 2025 xuất hiện trong kết quả tìm kiếm ghi "training set A comprised 25 subjects" — nguồn thứ cấp, **chưa xác minh**, nhiều khả năng nhầm "records" với "subjects".)
* Cửa sổ thời gian nào của mỗi bản ADFECGDB được cắt.

---

## 2. VIỆC 2 — Bảng kiểm toán nhiễm

Tiêu chí "bị nhiễm": mô hình/tham số được **học hoặc tinh chỉnh** trên ADFECGDB (hoặc bộ Silesia chứa 5 bản này) **và** được **đánh giá** trên CinC 2013 set-a mà **không** loại 15 bản trùng (hoặc ngược lại). "Đếm trùng" = hai tập kiểm thử "độc lập" thực ra chia sẻ 15 phút của cùng 5 sản phụ — không phải rò rỉ huấn luyện, nhưng làm phóng đại số bộ dữ liệu độc lập.

| # | Bài | DOI | Huấn luyện / tinh chỉnh | Đánh giá | Xử lý chồng lấn? | Kết quả CinC báo cáo | Phán xử |
|---|---|---|---|---|---|---|---|
| 1 | Rodrigues 2014, *Physiol Meas* 35:1699–1711 | 10.1088/0967-3334/35/8/1699 ✔ | ADFECGDB (theo Clifford 2014) | 447 bản Challenge (set A/B/C) | Không (Clifford 2014 nêu đích danh) | điểm Challenge (không F1) | **BỊ NHIỄM** — đã được ban tổ chức ghi nhận |
| 2 | Castillo và cộng sự 2018, *PLOS ONE* 13:e0199308 | 10.1371/journal.pone.0199308 ✔ | ADFECGDB, 17 tín hiệu r01–r10 ("used to train the clustering-based stage ... also used to train the complete method") | set A: 64 tín hiệu / 26 bản ghi do chuyên gia chọn | Không nhắc | F1 theo từng tín hiệu (Bảng 2), nhiều tín hiệu = 100 | **BỊ NHIỄM**: **28/64 tín hiệu (43,8 %) và 12/26 bản ghi** nằm trong 15 bản rò rỉ (a03 a04 a05 a08 a12 a13 a14 a20 a22 a23 a24 a25) — đếm từ Bảng 2 toàn văn |
| 3 | Mohebbian và cộng sự 2022, *IEEE JBHI* 26:515–526 | 10.1109/JBHI.2021.3111873 ✔ | "a model is trained on all the A&D FECG dataset. This model is used for testing on NI-FECG, and NI-FECG challenge datasets" | set-A 69 bản (loại a33 a38 a52 a54 a71 a74) | Không nhắc | F1 99,3 % [95,3; 99,9] | **BỊ NHIỄM**: 15/69 bản kiểm thử (21,7 %) là dữ liệu huấn luyện |
| 4 | Chen, Wu, Zhou 2025, *Sensors* 25:601 (Attention R2W-Net) | 10.3390/s25030601 ✔ | "fine-tuned using a subset of ADFECGDB" | ADFECGDB phần còn lại + "set A of the 2013 ... (PCDB)" 75 bản | Không nhắc; không nêu bản ghi PCDB nào | F1 98,03 % trên PCDB | **BỊ NHIỄM** (mức độ không định lượng được vì bài không nêu tập con) |
| 5 | Shokouhmand & Tavassolian 2023, *IEEE TBME* 70:283–295 (DPSS) | 10.1109/TBME.2022.3189617 ✔ | chỉ FECGSYNDB tổng hợp | ADFECGDB(L) 22 tín hiệu và NIFECGC set A 69 bản | Không nhắc | F1 97,7 (ADFECGDB) / 95,3 (NIFECGC) | Không rò rỉ huấn luyện; **đếm trùng** hai tập "thật" |
| 6 | Asadi và cộng sự 2025 (SCTD-Net, IEEE, toàn văn `papers/p07_*.txt`) | chưa xác minh DOI | FECGSYNDB tổng hợp | PCDB tập con 80 bản + ADFECGDB | Không nhắc | (xem toàn văn) | Không rò rỉ huấn luyện; **đếm trùng** |
| 7 | Su & Wu 2017, *Front Appl Math Stat* 3:2 | 10.3389/fams.2017.00002 ✔ | không học máy | adfecgdb + set A 75 | **Có cảnh báo**, không loại | — | Không rò rỉ; đã nêu rủi ro |
| 8 | Jaeger và cộng sự 2024, *Physiol Meas* 45:055009 (Power-MF) | 10.1088/1361-6579/ad4952 ✔ | không học máy (chọn tham số trên Silesia) | Silesia B1/B2 (B2 chứa 5 bản = ADFECGDB), NInFEA; repo có cả CinC 2013 | Không rõ | — | Không rò rỉ huấn luyện theo nghĩa học máy; nếu bổ sung CinC thì **đếm trùng** với B2 |
| 9 | Zhong và cộng sự 2018, *Physiol Meas* 39:045004 | 10.1088/1361-6579/aab297 ✔ | set-a | set-a (chia trong) | không liên quan | — | **Không nhiễm** cơ chế này |
| 10 | Fotiadou và cộng sự 2021, *Physiol Meas* 42:045007 | 10.1088/1361-6579/abf7db ✔ | bộ riêng 16 bản (54 h) | bộ riêng + "set-A of the Physionet database (68 min)" | không liên quan | PPA 99,6 % | **Không nhiễm** |
| 11 | Orvas và cộng sự 2025 (CUNet), arXiv 2506.22457 | 10.48550/arXiv.2506.22457 | in-silico | set-a 75 | không liên quan | F 77,8 ± 18,6 | **Không nhiễm** |
| 12 | Xu và cộng sự 2026, *Sensors* (toàn văn `papers/p09_*.pdf`) | chưa xác minh DOI | LOSO 15 mô phỏng + 5 ADFECGDB | DaISy, NIFEA — **không** CinC | không liên quan | — | **Không nhiễm** |
| 13 | Huang và cộng sự 2025, *IEEE JBHI* (TCGAN) | 10.1109/JBHI.2024.3524085 (Europe PMC / S2) | ADFECGDB | FECGSYNDB + ADFECGDB, **không** CinC (theo tóm tắt) | không liên quan | — | **Không nhiễm** (chỉ theo tóm tắt) |
| 14 | Basak và cộng sự 2024, *ESWA* 235:121196 | 10.1016/j.eswa.2023.121196 ✔ | ADFECGDB + Matonia 2020 (figshare) gộp | — | **chồng lấn KHÁC**: 5 bản B2 = ADFECGDB (Baldazzi/Pani, Matonia 2020) | — | Không liên quan CinC; có nguy cơ trùng B2↔ADFECGDB, chưa kiểm |
| 15 | Andreotti và cộng sự 2016, *Physiol Meas* 37:627–648 | 10.1088/0967-3334/37/5/627 ✔ | FECGSYNDB | — | không liên quan | — | **Không nhiễm** |
| 16 | Behar và cộng sự 2014, *Physiol Meas* 35:1569–1589 | 10.1088/0967-3334/35/8/1569 ✔ | "only the official data provided to the Challenge participants" (luận án) | set-a/b/c | không liên quan | — | **Không nhiễm** |
| 17 | Zahid và cộng sự 2022, *IEEE TBME* 69:119–128 | (theo ghi chú nhóm) | ECG Holter người lớn | — | — | — | **Không áp dụng** (không phải fECG) |
| 18 | Ghonchi & Abolghasemi 2022, *IEEE Sensors J* | 10.1109/JSEN.2022.3213586 ✔ | (bảng tổng quan của Alidash 2025 ghi dùng "NI-FECGDB + [15] + (A&D FECG)") | ? | ? | ? | **NGHI NGỜ — toàn văn không truy cập được** (repository.essex.ac.uk từ chối kết nối) |
| 19 | Zhong và cộng sự 2019 (RCED-Net), *Australas Phys Eng Sci Med* | 10.1007/s13246-019-00805-x ✔ | ? | PCDB 80 tín hiệu + ADFECGDB (theo Asadi 2025) | ? | ? | **CHƯA XÁC ĐỊNH** — tóm tắt không truy cập được (Springer chặn) |
| 20 | Alidash & Hesar 2025, *Sci Rep* 15:39260 | 10.1038/s41598-025-22999-9 ✔ | set-a (20 tín hiệu) | set-a | không liên quan | — | **Không nhiễm** |

✔ = DOI xác minh qua api.crossref.org ngày 2026-09-12.

**Đọc bảng:** trong 20 bài rà, **4 bài bị nhiễm chắc chắn** (Rodrigues 2014 — do chính ban tổ chức chỉ ra; Castillo 2018; Mohebbian 2022; Chen 2025), **2 bài nghi ngờ chưa xác định** (Ghonchi 2022, RCED-Net 2019), **3 bài đếm trùng** hai tập kiểm thử (DPSS 2023, SCTD-Net 2025, và Power-MF 2024 nếu ghép CinC với B2). Bài "gần nhất" với nhóm về giao thức (Orvas 2025, DPSS 2023) **không** bị nhiễm rò rỉ huấn luyện — nên con số 77,8 của Orvas vẫn so được với 60 bản sạch của nhóm, nhưng phải ghi rõ Orvas tính trên 75.

---

## 3. VIỆC 3 — Kiểm chéo kỹ thuật

| Kiểm | Bằng chứng | Kết luận |
|---|---|---|
| (a) set-a mỗi bản 60 s ở 1 kHz? | `benchmark_dpss/pcdb/a01.hea`: `a01 4 1000 60000` (4 kênh, 1000 Hz, 60 000 mẫu); tất cả 15 bản rò rỉ và a33/a54 cùng đầu đề `4 1000`. Silva 2013 / Clifford 2014: "one minute duration", "1 kHz". | **Khớp.** |
| (b) ADFECGDB 1 kHz, 5 phút? | `model/data/adfecgdb/r01.edf`: 5 kênh (Direct_1, Abdomen_1…4), 1000 Hz, 300,0 s. PhysioNet: "Sampling rate: 1 kHz", "five-minute". Matonia 2020: gốc KOMPOREL 500 Hz, "resampled to 1kHz" cho PhysioNet. | **Khớp.** 5 sản phụ × 5 phút = **25** cửa sổ 1 phút = đúng con số 25 trong Bảng 1 Silva 2013 / Bảng 2 Clifford 2014. |
| Số học cửa sổ | Nhóm tìm 15 bản trong set-a ở phút 1, 3, 5 của mỗi sản phụ (`analysis/dulieu_results.json → chong_lan.vi_tri_doan_ro_ri`). Còn 10 cửa sổ (phút 2, 4) không có trong set-a. | **Suy luận:** 10 cửa sổ đó nằm trong set-b/set-c — khớp Clifford 2014 "included in set-a, set-b (and possibly a few records in set-c)". Cả 15 định danh nằm trong a01–a25 = **đợt phát hành đầu 25 bản** của set A (trang PhysioNet) → 15/25 bản đầu tiên là ADFECGDB (suy luận từ định danh, chưa có nguồn xác nhận). |
| (c) 60 bản còn lại có thể cùng sản phụ nhưng khác buổi đo không? | Theo Silva 2013 / Clifford 2014, 60 bản còn lại của set-a đến từ: NIFECGDB (**một sản phụ duy nhất**, 55 bản ghi tuần 21–40; 14 bản vào Challenge), "Ukraine Non-Invasive FECG" 340 bản (số sản phụ **không công bố**), mô phỏng 20 bản. | **Có.** NCC chỉ loại bản sao nguyên văn; không phát hiện cùng sản phụ khác buổi/khác đoạn. Đặc biệt, mọi bản set-a lấy từ NIFECGDB là **cùng một người**. Số sản phụ thật trong 60 bản sạch **không biết** và chắc chắn < 60. Bootstrap theo bản ghi vì thế vẫn là **gần đúng**, đúng như V6 đã cảnh báo. |
| Số sản phụ set-a trong y văn | Không nguồn chính thức nào nêu. | **Không tìm được.** |

**Khuyến nghị kỹ thuật phát sinh (chưa làm):** (1) quét NCC 60 bản sạch ↔ `nifecgdb` (PhysioNet, công khai, 1 kHz) để tìm bản sao nguyên văn từ nguồn thứ hai đã biết; (2) gom cụm hình thái QRS mẹ (template mQRS) trên 60 bản để ước lượng số "cụm sản phụ" và báo cáo bootstrap theo cụm; (3) kiểm B2↔CinC đã làm (NCC max 0,3986 — không trùng), B1↔CinC đã làm (0,4196 — không trùng).

---

## 4. VIỆC 4 — Phát biểu đúng mức

### 4.1 Tiếng Việt (cho đề cương / báo cáo)

> Tập huấn luyện set-a của PhysioNet/CinC Challenge 2013 không phải một nguồn độc lập với ADFECGDB. Như ban tổ chức đã ghi nhận, 25 trong 447 bản ghi của Challenge được cắt từ "Abdominal and Direct FECG" (Matonia và cộng sự 2006) [Silva 2013, Bảng 1; Clifford 2014, Bảng 2], và Clifford và cộng sự (2014) đã cảnh báo rằng một thuật toán dự thi huấn luyện trên ADFECGDB "may have led to a bias in the results as this database was included in set-a, set-b (and possibly a few records in set-c)"; Su & Wu (2017) và Matonia và cộng sự (2020) cũng nhắc lại điều này. Tuy vậy, không tài liệu nào chúng tôi truy cập được cho biết *bản ghi set-a nào* là ADFECGDB. Chúng tôi xác định bằng đo lường (tương quan chéo chuẩn hoá trên tín hiệu thô, mọi độ trễ, hai cài đặt độc lập) rằng đúng 15/75 bản ghi set-a — a03, a04, a05, a08, a12, a13, a14, a15, a17, a19, a20, a22, a23, a24, a25 — là bản sao nguyên văn (NCC = 1,0000, |ΔRR| = 0,0 ms, cả 4 kênh đúng thứ tự) của các cửa sổ 0–60, 120–180 và 240–300 s của r01, r04, r07, r08, r10; 60 bản còn lại có NCC tối đa 0,62. Vì mô hình của chúng tôi huấn luyện trên ADFECGDB, mọi con số CinC trước đây của chúng tôi bị thổi phồng 3,27–7,18 điểm F1; số chính được tính lại trên 60 bản sạch. Chúng tôi lưu ý rằng ít nhất ba công trình đã công bố huấn luyện hoặc tinh chỉnh trên ADFECGDB rồi đánh giá trên set-a mà không loại các bản trùng này [Castillo 2018; Mohebbian 2022; Chen 2025], bên cạnh trường hợp Rodrigues (2014) mà ban tổ chức đã nêu.

### 4.2 English (for the paper)

> Set-a of the PhysioNet/CinC Challenge 2013 is not independent of ADFECGDB. As documented by the organisers, 25 of the 447 Challenge records were derived from the "Abdominal and Direct FECG" database of Matonia et al. (2006) [Silva et al. 2013, Table 1; Clifford et al. 2014, Table 2], and Clifford et al. (2014) explicitly cautioned that an entry trained on ADFECGDB "may have led to a bias in the results as this database was included in set-a, set-b (and possibly a few records in set-c)"; the same caveat is echoed by Su and Wu (2017) and by Matonia et al. (2020). None of the sources we could access, however, states *which* set-a records originate from ADFECGDB. We therefore identified them by measurement (normalised cross-correlation on raw signals over all lags, replicated with two independent implementations): exactly 15 of the 75 set-a records — a03, a04, a05, a08, a12, a13, a14, a15, a17, a19, a20, a22, a23, a24, a25 — are verbatim copies (NCC = 1.0000, |ΔRR| = 0.0 ms, all four channels in order) of the 0–60, 120–180 and 240–300 s windows of r01, r04, r07, r08 and r10; the remaining 60 records reach at most NCC = 0.62. Because our model is trained on ADFECGDB, all our previously reported CinC figures were inflated by 3.27–7.18 F1 points; the headline numbers are recomputed on the 60 clean records. We note that, in addition to the case of Rodrigues (2014) raised by the organisers, at least three published studies trained or fine-tuned on ADFECGDB and evaluated on set-a without excluding these records [Castillo et al. 2018; Mohebbian et al. 2022; Chen et al. 2025].

### 4.3 Tài liệu cần trích (trạng thái DOI)

| Tài liệu | DOI / định danh | Trạng thái |
|---|---|---|
| Silva I, Behar J, Sameni R, Zhu T, Oster J, Clifford GD, Moody GB. Noninvasive Fetal ECG: the PhysioNet/Computing in Cardiology Challenge 2013. *Comput Cardiol* 2013;40:149–152. | không có DOI (Crossref không có); ISSN 2325-8861; PDF cinc.org/archives/2013/pdf/0149.pdf | toàn văn đã đọc |
| Clifford GD, Silva I, Behar J, Moody GB. Non-invasive fetal ECG analysis. *Physiol Meas* 2014;35(8):1521–1536. | 10.1088/0967-3334/35/8/1521 | DOI xác minh; toàn văn đã đọc |
| Matonia A, Jezewski J, Kupka T, Horoba K, Wrobel J, Gacek A. The influence of coincidence of fetal and maternal QRS complexes on fetal heart rate reliability. *Med Biol Eng Comput* 2006;44(5):393–403. | chưa xác minh DOI (trích qua Silva 2013 [1]) | chưa đọc |
| Jezewski J, Matonia A, Kupka T, Roj D, Czabanski R. Determination of fetal heart rate from abdominal signals… *Biomed Tech* 2012;57(5). | 10.1515/bmt-2011-0130 | DOI xác minh |
| Matonia A và cộng sự. Fetal electrocardiograms, direct and abdominal with reference heartbeat annotations. *Sci Data* 2020;7:200. | 10.1038/s41597-020-0538-z | DOI xác minh; toàn văn đã đọc |
| Su L, Wu H-T. Extract Fetal ECG from Single-Lead Abdominal ECG… *Front Appl Math Stat* 2017;3:2. | 10.3389/fams.2017.00002 | DOI xác minh; toàn văn đã đọc |
| Rodrigues R. Fetal beat detection in abdominal ECG recordings: global and time adaptive approaches. *Physiol Meas* 2014;35(8):1699–1711. | 10.1088/0967-3334/35/8/1699 | DOI xác minh; chỉ đọc tóm tắt |
| Castillo E và cộng sự. A clustering-based method for single-channel fetal heart rate monitoring. *PLOS ONE* 2018;13(6):e0199308. | 10.1371/journal.pone.0199308 | DOI xác minh; toàn văn đã đọc |
| Mohebbian MR và cộng sự. Fetal ECG Extraction From Maternal ECG Using Attention-Based CycleGAN. *IEEE JBHI* 2022;26(2):515–526. | 10.1109/JBHI.2021.3111873 | DOI xác minh; đọc bản arXiv |
| Chen L, Wu S, Zhou Z. Fetal ECG Signal Extraction … Attention R2W-Net. *Sensors* 2025;25(3):601. | 10.3390/s25030601 | DOI xác minh; toàn văn đã đọc |
| Behar J. Extraction of clinical information from the non-invasive fetal electrocardiogram. DPhil thesis, Oxford 2014. | arXiv:1606.01093 | toàn văn đã đọc |
| Baldazzi G, Pani D. Open Data: Valuable Resources… In: *Innovative Technologies and Signal Processing in Perinatal Medicine*, Springer, tr. 221–240. | 10.1007/978-3-031-32625-7_12 | DOI xác minh; **toàn văn không truy cập được** |
| PhysioNet challenge-2013 v1.0.0 | https://physionet.org/content/challenge-2013/1.0.0/ | đã truy cập |
| PhysioNet adfecgdb v1.0.0 | https://physionet.org/content/adfecgdb/1.0.0/ (DOI 10.13026/C2RP4B — Crossref không phân giải) | đã truy cập |

---

## 5. Hạn chế của vòng rà này

1. Không đọc được toàn văn Rodrigues 2014 (Physiol Meas, đóng), Baldazzi & Pani (Springer, đóng), Ghonchi 2022 (Essex repo từ chối kết nối), Zhong 2019 RCED-Net (Springer chặn), Lee & Lee 2022 W-Net (không tìm được). Hai bài nghi ngờ (Ghonchi, RCED-Net) **chưa xếp loại**.
2. Bảng nhiễm chỉ rà 20 bài nhóm đã đọc hoặc được yêu cầu; **không** phải tổng quan hệ thống. Số bài bị nhiễm thật trong y văn có thể lớn hơn nhiều (hầu hết bài deep learning fECG 2019–2025 dùng cả "PCDB" và "ADFECGDB").
3. Với Mohebbian 2022, bài có hai phát biểu về huấn luyện (mô phỏng từ RR + "trained on all the A&D FECG dataset ... used for testing on ... challenge datasets"); xếp "bị nhiễm" dựa vào câu thứ hai.
4. Con số 28/64 tín hiệu của Castillo đếm từ pdftotext -layout Bảng 2; nên kiểm lại bằng mắt trên PDF trước khi in vào bài.
5. Cụm "shares signals with ADFECGDB" gán cho Baldazzi & Pani chỉ có trong ghi chú nội bộ của nhóm — **không** dùng làm trích dẫn nguyên văn khi chưa có toàn văn.
6. Không có nguồn nào cho số sản phụ trong set-a; mọi phát biểu về "60 bản sạch = 60 sản phụ" là **sai** cho đến khi có bằng chứng ngược lại.
