> **⚠ CẢNH BÁO (12/09/2026, sau vòng 7).** Tài liệu này được viết khi CinC 2013 set-a còn được tính trên **75 bản ghi**. Sau đó xác định 15 bản (a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25) là bản sao nguyên văn của dữ liệu huấn luyện ADFECGDB — điều ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014] và nhóm đã bỏ sót. **Mọi con số CinC dưới đây (79,40 / 85,60 / 86,87 / 71,21 / 62,82, AUROC 0,980…) bị thổi 3–7 điểm và đã bị rút.** Số chính thức trên **60 bản sạch**: PSD 74,28 · peakprob 82,01 · oracle 83,60 (`analysis/dulieu_results.json`, `benchmark_dpss/eval_cinc60_sach.json`). Kết luận định tính trong tài liệu giữ nguyên trừ khi ghi khác trong `docs/nhat_ky/THAMDINH_VONG7.md`. Cụm "tiền đăng ký" trong tài liệu này **không đúng** — tệp khai báo không neo git.

> **Cảnh báo (vòng 7, 12/09/2026).** Tệp này được viết khi CinC 2013 còn tính trên **75 bản ghi**; 15 bản
> trong đó là bản sao ADFECGDB (điều ban tổ chức đã ghi nhận từ 2013 — `survey/RO_RI_VANLIEU.md`). Mọi con
> số CinC-75 ở đây (79,40 / 85,60 / 86,87 / +6,20 / +8,18 / +7,47 …) **đã rút**; số hiện hành trên 60 bản
> sạch: psd 74,28 · gate 80,72 · gate4 81,01 · rrcv 80,00 · peakprob 82,01 · oracle 83,60
> (`analysis/dulieu_results.json → chon_kenh_60_sach`, `benchmark_dpss/eval_cinc60_sach.json`). Số gốc giữ
> nguyên để truy vết; kết luận định tính đọc kèm `analysis/XACNHAN.md`.

# Cổng từ chối hiệu chuẩn lại cho mô hình 22 ca — nó có bắt được ba bản ghi khó không?

**Ngày:** 12/09/2026 · **Tác vụ:** A3 · **Mã:** `analysis/gate22_features.py`, `analysis/gate22_analyze.py`,
`analysis/gate22_cinc.py`, `analysis/gate22_fig.py`
**Số liệu máy đọc:** `analysis/gate22_results.json`, `analysis/gate22_cinc.json`,
`analysis/gate22_segments.csv` · **Nhật ký:** `analysis/gate22_log.txt`, `analysis/gate22_cinc_log.txt`
**Hình:** `analysis/fig_gate22.png`

---

## 0. Câu hỏi và câu trả lời một dòng

RelyFetal (một kênh, 113.481 tham số) thua Power‑MF (bốn kênh, tách nguồn ICA) trung bình 1,27 điểm F1
trên 22 chủ thể, và toàn bộ khoảng âm đó do **ba bản ghi** gây ra: B1_07, B1_06, B2_03. Câu hỏi: cổng
từ chối có biết trước ba bản ghi đó là không tin cậy hay không?

> **CÓ — và bắt trọn vẹn.** Với cổng hiệu chuẩn lại theo kiểu không rò rỉ (leave‑one‑**subject**‑out),
> ba bản ghi khó xếp hạng **1, 2, 3** trong danh sách 22 chủ thể sắp theo độ tin cậy tăng dần:
> B2_03 hạng 1 (kém tin cậy nhất), B1_07 hạng 2, B1_06 hạng 3. Không có chủ thể nào khác chen vào.
> Bản ghi thua nhẹ thứ tư (B1_10, −1,86 điểm) xếp hạng 4.

Đây là **sự kiện quan sát được**, không phải suy luận: xem bảng mục 3. Diễn giải và các giới hạn
(nhất là: cổng học **không** phải thứ duy nhất làm được việc này) nằm ở mục 9 và mục 10.

---

## 1. Thiết kế — vì sao kết quả này không phải do rò rỉ

| Hạng mục | Giá trị |
|---|---|
| Mô hình chấm | `fetalqrs_tcn_22_fold_XX.pt` — với mỗi chủ thể dùng **đúng fold không chứa chủ thể đó** (lấy từ `benchmark_dpss/eval_22.json`) |
| Kênh | quy tắc PSD mù nhãn 1,8–3,0 Hz (Power‑MF, Jaeger 2024), tái lập đúng kênh mà `eval_22.py` đã chọn |
| Đoạn | 4 s không chồng lấn (1000 mẫu @250 Hz); 3.890 đoạn có ít nhất một nhịp nhãn (0 đoạn bị loại) |
| Nhãn "đoạn xấu" | F1 đoạn < 80 (giữ nguyên định nghĩa của `fsqi/train_gate.py`); 210/3.890 = 5,40 % |
| Đặc trưng | đúng **12 chỉ số SQI cổ điển**: `sampen, kurtosis, spec_entropy, band_ratio, rr_cv, rr_plaus, bsqi, n_det, psd_fhr, tau_acf, peak_prob_mean, prob_max`. **Không đặc trưng nào nhìn thấy nhãn.** |
| Bộ học | `HistGradientBoostingClassifier(max_depth=3, max_iter=200, learning_rate=0.05, class_weight='balanced', random_state=0)`; NaN → trung vị tập huấn luyện |
| Kiểm định chéo | **leave‑one‑SUBJECT‑out, 22 fold.** Mọi đoạn của một chủ thể đều được chấm bởi một cổng **chưa từng thấy chủ thể đó** |
| Điểm mức bản ghi | `score = 1 − trung bình p_bad` (ngoài fold). Không cần ngưỡng nào |
| KTC | cluster bootstrap **lấy mẫu lại CHỦ THỂ**, 10.000 lần, seed 0 (mức đoạn: 2.000 lần) |

**Kiểm chứng tính đúng đắn đường ống.** F1 mức bản ghi tính lại trong nghiên cứu này khớp
`eval_22.json` với sai lệch tuyệt đối lớn nhất **0,0** trên cả 22 chủ thể. F1 Power‑MF 4 kênh dựng lại
từ đỉnh thô (`baselines/powermf_work/*_powermf.mat`, cùng nhãn, cùng bộ ghép ±50 ms) khớp
`powermf_fair_stats.json` với sai lệch lớn nhất **1,4 × 10⁻¹⁴**. Không có con số nào trong tài liệu này
được gõ tay.

---

## 2. Cổng 22 ca: nó phân biệt được gì, và không phân biệt được gì

Hai câu hỏi khác nhau, hai con số khác nhau. **Phải đọc cả hai.**

| Câu hỏi | Số đo | Giá trị |
|---|---|---|
| **(a)** "Bản ghi nào đáng ngờ?" | AUROC **gộp** cả 3.890 đoạn của 22 chủ thể | **0,965** KTC95 [0,857; 0,992] |
| | AUPRC gộp | 0,801 (tỉ lệ nền 5,40 %) |
| **(b)** "Trong một bản ghi, **giây nào** đáng ngờ?" | AUROC **trong từng bản ghi**, trung bình 11 chủ thể có cả hai lớp | **0,934** KTC95 [0,872; 0,981] |
| | — trung vị / khoảng | 0,983 / [0,676; 1,000] |

Con số (a) lớn hơn vì nó **trộn lẫn** khác biệt giữa bản ghi với khác biệt trong bản ghi. Con số (b)
là con số phải dùng khi nói "cổng biết đoạn nào trong bản ghi là xấu". Vòng trước đã ghi nhận đúng
hiện tượng này với cổng cũ (0,929 giữa bản ghi so với 0,721 [0,517; 0,898] trong bản ghi); cổng
22 ca **cải thiện rõ ở con số trong bản ghi** (0,934 [0,872; 0,981]), nhưng nó chỉ dựa trên **11/22**
chủ thể — 11 chủ thể còn lại không có đoạn xấu nào nên không định nghĩa được AUROC trong bản ghi.

AUROC trong từng bản ghi:

| bản ghi | AUROC | đoạn xấu | | bản ghi | AUROC | đoạn xấu |
|---|---|---|---|---|---|---|
| r10 | 0,676 | 5/75 | | B1_05 | 1,000 | 1/299 |
| B2_04 | 0,836 | 2/75 | | B1_06 | 0,925 | 56/299 |
| B2_03 | 0,921 | 30/75 | | B1_07 | 0,947 | 82/299 |
| B2_09 | 0,986 | 1/75 | | B1_09 | 0,999 | 5/299 |
| B1_02 | 0,997 | 1/299 | | B1_10 | 0,983 | 26/299 |
| B1_03 | 1,000 | 1/299 | | | | |

Đáng chú ý: **đúng ba bản ghi khó lại là ba bản có nhiều đoạn xấu nhất** (82, 56, 30) và cổng vẫn
phân biệt tốt *bên trong* chúng (0,947 / 0,925 / 0,921) — tức cổng không chỉ nói "bản ghi này hỏng",
nó còn chỉ ra được giây nào hỏng.

**Đặc trưng nào làm việc** (giảm AUROC gộp khi hoán vị, ngoài fold):
`rr_cv +0,140` ≫ `peak_prob_mean +0,032` ≫ mọi thứ còn lại ≤ +0,001. Nói thẳng: gần như toàn bộ sức
mạnh của cổng nằm ở **độ biến thiên khoảng RR của chính đầu ra mô hình** cộng thêm một chút từ
xác suất trung bình tại đỉnh. Mười đặc trưng còn lại gần như không đóng góp.

---

## 3. KẾT QUẢ CHÍNH — xếp hạng độ tin cậy 22 chủ thể

Sắp từ **kém tin cậy nhất** (hạng 1) đến tin cậy nhất (hạng 22). `hiệu` = F1 RelyFetal − F1 Power‑MF 4 kênh.

| # | bản ghi | nhóm | điểm tin cậy | TB p_bad | tỉ lệ p>0,5 | F1 RelyFetal | F1 PMF‑4 | hiệu |
|---|---|---|---|---|---|---|---|---|
| **1** | **B2_03** | B2 | **0,4838** | 0,5162 | 0,520 | 79,72 | 89,49 | **−9,77** |
| **2** | **B1_07** | B1 | **0,6092** | 0,3908 | 0,398 | 86,56 | 99,44 | **−12,88** |
| **3** | **B1_06** | B1 | **0,6680** | 0,3320 | 0,351 | 89,45 | 99,97 | **−10,51** |
| 4 | B1_10 | B1 | 0,8556 | 0,1444 | 0,107 | 97,05 | 98,91 | −1,86 |
| 5 | r04 | PhysioNet | 0,9521 | 0,0479 | 0,027 | 99,68 | 99,53 | +0,16 |
| 6 | B2_09 | B2 | 0,9684 | 0,0316 | 0,027 | 99,11 | 98,74 | +0,37 |
| 7 | B1_08 | B1 | 0,9721 | 0,0279 | 0,007 | 99,83 | 99,31 | +0,52 |
| 8 | B1_02 | B1 | 0,9727 | 0,0273 | 0,007 | 99,79 | 99,55 | +0,23 |
| 9 | B1_01 | B1 | 0,9781 | 0,0219 | 0,003 | 99,97 | 99,92 | +0,05 |
| 10 | B1_09 | B1 | 0,9795 | 0,0205 | 0,020 | 99,07 | 98,39 | +0,68 |
| 11 | B2_04 | B2 | 0,9799 | 0,0201 | 0,013 | 98,90 | 97,95 | +0,95 |
| 12 | B2_05 | B2 | 0,9913 | 0,0087 | 0,000 | 100,00 | 99,70 | +0,30 |
| 13 | r07 | PhysioNet | 0,9914 | 0,0086 | 0,000 | 100,00 | 99,20 | +0,80 |
| 14 | r08 | PhysioNet | 0,9920 | 0,0080 | 0,000 | 99,77 | 99,46 | +0,31 |
| 15 | B1_04 | B1 | 0,9933 | 0,0067 | 0,000 | 100,00 | 99,86 | +0,14 |
| 16 | r01 | PhysioNet | 0,9940 | 0,0060 | 0,000 | 99,92 | 99,69 | +0,23 |
| 17 | B1_03 | B1 | 0,9941 | 0,0059 | 0,003 | 99,92 | 98,97 | +0,95 |
| 18 | B2_06 | B2 | 0,9958 | 0,0042 | 0,000 | 100,00 | 99,85 | +0,15 |
| 19 | B1_05 | B1 | 0,9961 | 0,0039 | 0,003 | 99,87 | 99,66 | +0,22 |
| 20 | r10 | PhysioNet | 0,9965 | 0,0035 | 0,000 | 97,61 | 97,15 | +0,46 |
| 21 | B2_12 | B2 | 0,9986 | 0,0014 | 0,000 | 100,00 | 99,77 | +0,23 |
| 22 | B2_08 | B2 | 0,9989 | 0,0011 | 0,000 | 100,00 | 99,77 | +0,23 |

- **3/3 bản ghi khó nằm trong top‑3 đáng ngờ.** Nếu xếp hạng hoàn toàn ngẫu nhiên, xác suất để đúng
  ba bản ghi định trước rơi vào top‑3 là 6/(22·21·20) = **1/1540 ≈ 6,5 × 10⁻⁴**.
- Tương quan Spearman(điểm tin cậy, F1 thật) = **0,684** (p = 4,4 × 10⁻⁴).
- Tương quan Spearman(điểm tin cậy, hiệu số RelyFetal − PMF4) = 0,407 (p = 0,060) — **chưa đạt mức ý
  nghĩa 0,05**; điểm tin cậy dự báo "mô hình ta sai", nó **không** trực tiếp dự báo "ta thua Power‑MF".
- Có một sai lệch cần nói rõ: **r10 xếp hạng 20** (rất tin cậy) nhưng F1 chỉ 97,61 — đây là bản ghi
  mà cổng lạc quan nhất so với thực tế. Ngược lại không có bản ghi nào bị cổng nghi oan nặng.

---

## 4. Đường rủi ro – độ phủ ở mức chủ thể

Bỏ dần các chủ thể kém tin cậy nhất; tính lại F1 trung bình trên **phần còn lại**, và so với Power‑MF
4 kênh **trên đúng tập con đó**. KTC95 = cluster bootstrap theo chủ thể.

| giữ | % bản ghi | % thời lượng | RelyFetal | PMF‑4 | hiệu | KTC95 | p (Wilcoxon) | vừa bỏ |
|---|---|---|---|---|---|---|---|---|
| 22 | 100,0 | 100,0 | 97,56 | 98,83 | **−1,27** | [−3,06; +0,23] | 0,156 | — |
| 21 | 95,5 | 98,1 | 98,41 | 99,28 | −0,87 | [−2,60; +0,37] | 0,055 | B2_03 |
| 20 | 90,9 | 90,4 | 99,00 | 99,27 | −0,27 | [−1,45; +0,44] | 0,012 | B1_07 |
| **19** | **86,4** | **82,7** | **99,50** | **99,23** | **+0,27** | [−0,02; +0,48] | 0,001 | B1_06 |
| **18** | **81,8** | **75,0** | **99,64** | **99,25** | **+0,39** | **[+0,27; +0,52]** | 7,6 × 10⁻⁶ | B1_10 |
| 17 | 77,3 | 73,1 | 99,63 | 99,23 | +0,40 | [+0,28; +0,54] | 1,5 × 10⁻⁵ | r04 |
| 15 | 68,2 | 63,5 | 99,66 | 99,26 | +0,40 | [+0,26; +0,55] | — | … |
| 10 | 45,5 | 36,5 | 99,71 | 99,34 | +0,37 | [+0,22; +0,55] | — | … |

(bảng đầy đủ 21 mức trong `gate22_results.json → rui_ro_do_phu_ban_ghi.duong`)

**Trả lời câu hỏi then chốt "ở độ phủ nào thì RelyFetal đơn kênh hết thua Power‑MF đa kênh":**

- Hiệu số **chuyển sang không âm** tại độ phủ **86,4 % bản ghi = 82,7 % thời lượng** (19/22 chủ thể):
  +0,27 điểm, KTC95 [−0,02; +0,48].
- KTC95 **lần đầu không chứa 0** (tức khẳng định được "ta hơn") tại độ phủ **81,8 % bản ghi = 75,0 %
  thời lượng** (18/22 chủ thể): +0,39 điểm, KTC95 [+0,27; +0,52].

Nói đúng phạm vi: ở 100 % độ phủ, một kênh **không phân biệt được** với bốn kênh (−1,27; KTC
[−3,06; +0,23]; p = 0,156). Khi cổng được phép từ chối **khoảng một phần sáu số giây**, một kênh
**hơn** bốn kênh có ý nghĩa thống kê trên phần còn lại. Đây **không** phải tuyên bố "thắng SOTA":
Power‑MF vẫn xử lý được chính những bản ghi mà ta bỏ, và nó xử lý tốt (99,44 / 99,97 / 89,49 trên ba
bản ghi ta từ chối). Kết luận đúng là: **ta biết lúc nào ta sai, và đúng lúc đó là lúc cần thêm đạo trình.**

---

## 5. Đường rủi ro – độ phủ theo **THỜI LƯỢNG** (từ chối từng đoạn 4 s)

Phê bình của vòng trước — "đếm theo bản ghi là gian lận" — được xử lý ở đây: từ chối **từng đoạn 4 s**
theo p_bad, rồi tính lại F1 trên **phần giây được giữ**, cho cả hai phương pháp trên **cùng những giây đó**
(đỉnh Power‑MF được cắt vào cùng lưới đoạn, cùng nhãn, cùng bộ ghép).

| % thời lượng giữ | ngưỡng p_bad | RelyFetal (macro) | PMF‑4 (macro) | hiệu | KTC95 | thắng/thua |
|---|---|---|---|---|---|---|
| 100 | — | 97,56 | 98,83 | −1,28 | [−3,04; +0,23] | 18/4 |
| 98 | 0,987 | 98,16 | 98,96 | −0,80 | [−2,20; +0,29] | 18/4 |
| 96 | 0,942 | 98,77 | 99,17 | −0,40 | [−1,40; +0,34] | 17/5 |
| 94 | 0,788 | 99,21 | 99,28 | −0,06 | [−0,76; +0,45] | 18/3 |
| **92** | 0,502 | **99,46** | 99,34 | **+0,12** | [−0,27; +0,42] | 19/2 |
| 90 | 0,234 | 99,61 | 99,37 | +0,24 | [−0,01; +0,43] | 19/2 |
| **88** | 0,110 | **99,66** | 99,38 | **+0,28** | **[+0,09; +0,45]** | 19/2 |
| 86 | 0,067 | 99,73 | 99,44 | +0,29 | [+0,13; +0,46] | 18/2 |
| 80 | 0,029 | 99,74 | 99,46 | +0,27 | [+0,11; +0,42] | — |

- Hiệu số chuyển **không âm** ở **92 % thời lượng**; KTC95 **không chứa 0** từ **88 % thời lượng** trở xuống.
- Mức 100 % tái lập đúng bảng đã chốt (97,56 vs 98,83; hiệu −1,28; p = 0,156; 18/4) — kiểm chứng
  rằng cách cắt theo đoạn không làm lệch gì.
- **Quan trọng:** từ chối theo giây rẻ hơn nhiều so với từ chối theo bản ghi. Để đạt hiệu số dương
  chắc chắn, cách theo bản ghi phải vứt **25 % thời lượng**, cách theo đoạn chỉ vứt **12 %**.

---

## 6. Đối chiếu lâm sàng (STV Dawes‑Redman, epoch 3,75 s)

### 6.1 Độ chệch STV theo độ phủ mức bản ghi

| giữ | % thời lượng | chệch TB (ms) | trung bình \|chệch\| | LoA 95 % | max \|chệch\| |
|---|---|---|---|---|---|
| 22 | 100,0 | +1,468 | 1,474 | [−4,93; +7,87] | 11,99 |
| 21 | 98,1 | +0,967 | 0,973 | [−3,59; +5,52] | 7,92 |
| 20 | 90,4 | +0,625 | 0,631 | [−2,82; +4,07] | 7,92 |
| **19** | **82,7** | **+0,241** | **0,248** | **[−0,53; +1,01]** | **1,61** |
| 18 | 75,0 | +0,165 | 0,173 | [−0,27; +0,60] | 0,56 |
| 15 | 63,5 | +0,172 | 0,180 | [−0,27; +0,62] | 0,56 |

### 6.2 Từ chối theo epoch (chỉ giữ epoch nằm trong đoạn được chấp nhận)

| % epoch giữ | chệch TB | \|chệch\| TB | LoA 95 % | max \|chệch\| |
|---|---|---|---|---|
| 100,0 | +1,445 | 1,460 | [−4,86; +7,75] | 11,66 |
| 95,4 | +0,581 | 0,626 | [−1,99; +3,15] | 4,11 |
| **91,6** | **+0,159** | **0,199** | **[−0,45; +0,76]** | **0,94** |
| 88,1 | +0,100 | 0,152 | [−0,38; +0,58] | 0,81 |
| 75,2 | +0,109 | 0,147 | [−0,40; +0,62] | 0,85 |

**Trả lời câu hỏi "cổng có kéo độ chệch STV xuống dưới 2,6 ms không":**

- Độ chệch **trung bình** vốn đã dưới 2,6 ms ngay ở 100 % độ phủ (+1,47 ms) — nên câu hỏi đặt ở mức
  trung bình là **không sắc**. Con số đáng lo là **cá thể**: ở 100 % độ phủ có bản ghi lệch **11,99 ms**
  (B2_03), và **LoA rộng tới [−4,93; +7,87] ms** — nghĩa là với một sản phụ bất kỳ, sai số STV có thể
  lớn hơn cả khoảng cách giữa hai ngưỡng TRUFFLE (2,6 và 3,0 ms).
- Điều cổng làm được: **sai số lớn nhất trên MỌI bản ghi** xuống dưới 2,6 ms lần đầu ở **độ phủ 19/22
  bản ghi (82,7 % thời lượng)** — max \|chệch\| = 1,61 ms — và LoA thu về [−0,53; +1,01] ms.
  Từ chối theo epoch đạt điều tương tự ở **91,6 % thời lượng** (max 0,94 ms, LoA [−0,45; +0,76]).
- Sai số STV bám rất sát F1 (kết quả cũ của `CLINICAL.md` giữ nguyên): ba bản ghi cổng loại ra chính
  là ba bản có chệch STV +7,81 / +7,91 / +11,99 ms. Bốn bản ghi kế tiếp đều ≤ +1,61 ms.
- **Vẫn giữ nguyên kết luận cũ:** ngay cả sau khi cổng lọc, hệ thống **không dùng được như một máy đo
  STV độc lập**. Nó chỉ đủ an toàn theo nghĩa "không đưa ra số STV sai lệch bệnh lý mà không cảnh báo".

---

## 7. Chấp nhận nhầm (false accept) — liệt kê từng bản

Bản ghi được cổng **giữ lại** nhưng F1 thấp. Ngưỡng "thấp" = F1 < 95 (3/22 bản ghi có F1 < 95; cũng là
3 bản có F1 < 90).

| mức giữ | số bản chấp nhận nhầm | cụ thể |
|---|---|---|
| 22 (100 %) | 3 | B2_03 F1 79,72 (hạng 1, ΔSTV +11,99 ms); B1_07 F1 86,56 (hạng 2, ΔSTV +7,81); B1_06 F1 89,45 (hạng 3, ΔSTV +7,91) |
| 21 (95 %) | 2 | B1_07, B1_06 |
| 20 (91 %) | **1** | **B1_06 F1 89,45 (hạng 3, ΔSTV +7,91 ms)** |
| 19 (86 %) | **0** | — |
| 18 (82 %) | 0 | — |
| 15 (68 %) | 0 | — |

Diễn giải: ở mức giữ 20/22, **B1_06 lọt lưới** — nó là bản ghi nguy hiểm nhất còn lại: F1 89,45, STV
lệch +7,91 ms, và cổng vẫn xếp nó ở hạng 3 tức "biết" nó xấu, chỉ là chưa đủ để bị cắt. Chỉ từ mức
giữ 19/22 trở xuống mới **không còn** chấp nhận nhầm nào. Đây là lý do kỹ thuật để chọn điểm làm việc
ở 19/22 (82,7 % thời lượng) thay vì 20/22.

Không có "từ chối nhầm" nghiêm trọng ở chiều ngược lại: ở mức giữ 19, ba bản bị loại có F1 79,7 / 86,6 / 89,5
— tất cả đều thực sự kém.

---

## 8. Kiểm chứng ngoài trên CinC 2013 (75 bản ghi, dữ liệu hoàn toàn độc lập)

Cổng cuối (huấn luyện trên toàn bộ 3.890 đoạn của 22 chủ thể, **không hiệu chuẩn lại gì trên CinC**)
được áp thẳng lên 75 bản ghi CinC 2013 set‑a với mô hình `fetalqrs_tcn_22_production.pt` (zero‑shot,
kênh PSD mù nhãn). F1 mức bản ghi tái lập `eval_cinc75.json` với sai lệch **0,0**.

| số đo | giá trị |
|---|---|
| Spearman(điểm tin cậy, F1 bản ghi) | **0,810** (p = 1,3 × 10⁻¹⁸) |
| AUROC mức **bản ghi** (phân biệt bản ghi F1 < 80) | **0,980** (25/75 bản ghi có F1 < 80) |
| trùng nhau giữa 10 bản "cổng nghi nhất" và 10 bản "thực sự tệ nhất" | 4/10 |

Đường rủi ro – độ phủ trên CinC (`gate22_cinc.json`):

| giữ | độ phủ | F1 TB phần giữ | số bản ≥ 90 | số bản < 50 |
|---|---|---|---|---|
| 75 | 100 % | 79,40 | 48 | 16 |
| 65 | 86,7 % | 85,76 | 48 | 9 |
| 60 | 80,0 % | 88,83 | 48 | 7 |
| 55 | 73,3 % | 92,90 | 48 | 4 |
| 50 | 66,7 % | **97,76** | 48 | **1** |

Đây là kết quả **mạnh nhất về khả năng tổng quát của cổng**: trên một tập dữ liệu khác máy đo, khác
người chú thích, khác chiều dài bản ghi, cổng vẫn xếp hạng đúng. Ở độ phủ 66,7 % nó loại được 15/16
bản ghi thảm hoạ (F1 < 50) và kéo F1 trung bình từ 79,40 lên 97,76.

Lưu ý ngược lại: 4/10 trùng nhau ở danh sách "10 tệ nhất" cho thấy cổng **xếp hạng thô tốt nhưng xếp
hạng tinh thì không** — nó phân biệt "tốt vs thảm hoạ" rất tốt (AUROC 0,980) chứ không sắp thứ tự
chính xác trong nhóm kém.

---

## 9. Đối chứng trung thực: cổng HỌC có cần thiết không?

Nếu chỉ dùng **một** chỉ số SQI (trung bình theo bản ghi), không học gì, thì có xếp đúng ba bản ghi khó
vào top‑3 không? Kiểm tra cả 12 đặc trưng × 2 chiều dấu = 24 quy tắc:

| quy tắc một đặc trưng | top‑3 | bắt được |
|---|---|---|
| `rr_cv` cao = xấu | B2_03, B1_07, B1_06 | **3/3** |
| `rr_plaus` thấp = xấu | B2_03, B1_07, B1_06 | **3/3** |
| `psd_fhr` thấp = xấu | B1_06, B1_07, B2_03 | **3/3** |
| `peak_prob_mean` thấp = xấu | B2_03, B1_07, B1_06 | **3/3** |
| `prob_max` thấp = xấu | B1_06, B1_07, B2_03 | **3/3** |
| `bsqi` thấp = xấu | B1_06, B2_03, B1_09 | 2/3 |

**5/24 quy tắc một‑đặc‑trưng cũng bắt đủ 3/3.** Phải nói thẳng: **cổng học không phải thứ duy nhất làm
được việc này**, và điều đó nhất quán với việc `rr_cv` một mình chiếm +0,140 trong +0,17 tổng độ quan
trọng hoán vị. Điểm cộng thật sự của cổng học so với quy tắc một đặc trưng là:
(i) nó cho **một ngưỡng duy nhất** dùng chung cho mọi bản ghi và mọi tập dữ liệu, được hiệu chuẩn
ngoài fold; (ii) nó cho điểm **liên tục ở mức đoạn** dùng được cho đường rủi ro theo giây; (iii) nó
tổng quát sang CinC (AUROC 0,980) mà không phải chọn lại đặc trưng. Quy tắc một đặc trưng ở bảng trên
được chọn **hậu kiểm ngay trên 22 chủ thể này**, không có tập độc lập để chọn — nên bảng này là
**đối chứng**, không phải phương án thay thế đã được kiểm chứng.

---

## 10. Hạn chế (bắt buộc đọc cùng kết quả)

1. **n = 22 chủ thể, 2 nguồn dữ liệu.** "3/3 trong top‑3" là một sự kiện trên một mẫu 22. Xác suất
   ngẫu nhiên 1/1540 chỉ đúng dưới giả thuyết xếp hạng hoàn toàn ngẫu nhiên; nó **không** là một
   kiểm định khai báo trước (không phải "tiền đăng ký" — kế hoạch không neo git), vì ba bản ghi "khó" được xác định *trước* khi chạy cổng nhưng *sau* khi đã
   biết bảng F1. Không có tập kiểm chứng thứ hai ở mức bản ghi Silesia.
2. **Điểm làm việc chọn hậu kiểm; không hiệu chỉnh đa phép so sánh.** 21 mức độ phủ ở mục 4 và 48 mức
   ở mục 5 đều được kiểm định, không hiệu chỉnh. Phát biểu "KTC95 không chứa 0 từ 81,8 % độ phủ" là
   phát biểu **có điều kiện trên tập con đã giữ**; bootstrap lấy mẫu lại chủ thể *trong tập con đó*,
   nó **không** tính đến bước lựa chọn tập con. Một KTC đúng nghĩa cho toàn quy trình (chọn + đánh giá)
   sẽ rộng hơn con số báo cáo. **Không được viết "p < 0,05" cho kết luận này mà không kèm câu này.**
3. **AUROC trong bản ghi dựa trên 11/22 chủ thể.** 11 chủ thể còn lại không có đoạn xấu nào, nên con
   số 0,934 [0,872; 0,981] mô tả riêng nhóm chủ thể *có* vấn đề. Với chủ thể sạch, cổng chưa được
   kiểm tra khả năng "không báo động giả" ở mức đoạn ngoài việc tỉ lệ p > 0,5 của chúng là 0,000–0,027.
4. **Nhãn B1 là nhãn gián tiếp.** Toàn bộ 10 chủ thể B1 (10/22 = 200/260 phút dữ liệu) dùng `fqrs_all`
   kể cả nhịp cờ 0 mà chuyên gia không xác nhận. Kết quả A2 vòng trước đã cho thấy B1 có **nhiễu nhãn
   thật ở mốc thời gian** (lệch tuyệt đối TB 3,25–6,50 ms giữa các mô hình). Vì vậy các số **STV** ở
   mục 6 trên B1 phải đọc dè dặt, và không được dùng bộ 22 chủ thể để phát biểu về độ chính xác thời điểm.
5. **Ngưỡng lâm sàng 2,6 ms chưa được kiểm chứng trong phiên này** — nó do phản biện P3 cung cấp
   (xem `analysis/CLINICAL.md`, mục "Nguồn ngưỡng"). Mọi câu có số 2,6 ms là **so với một ngưỡng
   được cung cấp**, không phải một chuẩn đã tự xác minh.
6. **Power‑MF ở mức đoạn là lát cắt hậu kiểm.** Power‑MF được chạy trên **toàn bản ghi** rồi đỉnh của
   nó mới bị cắt vào lưới 4 s. Nó **không** được chạy lại từng đoạn 4 s. Nếu chạy lại theo đoạn,
   Power‑MF có thể tốt hơn hoặc kém hơn (bộ lọc thích nghi và ICA của nó cần ngữ cảnh dài). Bảng mục 5
   vì thế là so sánh "RelyFetal có cổng theo giây" với "Power‑MF toàn bản ghi, đánh giá trên cùng những
   giây đó", không phải hai hệ thống cùng chế độ.
7. **Cổng không giải quyết vấn đề gốc.** Ba bản ghi bị từ chối vẫn cần được đo. Power‑MF 4 kênh làm
   được 99,44 / 99,97 / 89,49 trên chính ba bản ghi đó. Kết quả này nói "hệ đơn kênh biết lúc nào
   phải chuyển sang đa kênh", **không** nói "đơn kênh thay thế được đa kênh".
8. **Thực nghiệm dải lọc trên TCN chưa xong** (`pilot_evidence/band_tcn.py`, 3 dải còn lại). Mọi con
   số +11,00 điểm cho dải 10–60 Hz vẫn đang đo trên GBM cửa sổ 300 ms, chưa phải TCN. Hạn chế này
   giữ nguyên trong bài báo và đề cương.

---

## 11. Cách chạy lại

```bash
set OPENBLAS_NUM_THREADS=1 & set OMP_NUM_THREADS=1 & set MKL_NUM_THREADS=1
python analysis/gate22_features.py            # ~1,5 phút với 3 tiến trình song song; ghi analysis/gate22_cache/
python analysis/gate22_analyze.py             # ~1,3 phút
python analysis/gate22_cinc.py                # ~0,6 phút (kiểm chứng ngoài)
python analysis/gate22_fig.py                 # hình
```

Phụ thuộc dữ liệu: `benchmark_dpss/eval_22.json`, `benchmark_dpss/eval_cinc75.json`,
`baselines/powermf_fair_stats.json`, `baselines/powermf_work/*_powermf.mat`,
`model/checkpoints/fetalqrs_tcn_22_fold_*.pt`, `fetalqrs_tcn_22_production.pt`.

**Cổng cũ (`fsqi/gate_classical.pkl`, huấn luyện trên mô hình 5 ca) KHÔNG bị ghi đè** — nó vẫn là
cổng mà `demo/` và `analysis/clinical.py` đang dùng. Cổng 22 ca ở tài liệu này hiện chỉ tồn tại dưới
dạng kết quả phân tích; việc thay thế cổng sản xuất là một quyết định riêng, chưa thực hiện.
