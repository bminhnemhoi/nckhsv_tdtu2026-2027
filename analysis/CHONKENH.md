> **⚠ CẢNH BÁO (12/09/2026, sau vòng 7).** Tài liệu này được viết khi CinC 2013 set-a còn được tính trên **75 bản ghi**. Sau đó xác định 15 bản (a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25) là bản sao nguyên văn của dữ liệu huấn luyện ADFECGDB — điều ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014] và nhóm đã bỏ sót. **Mọi con số CinC dưới đây (79,40 / 85,60 / 86,87 / 71,21 / 62,82, AUROC 0,980…) bị thổi 3–7 điểm và đã bị rút.** Số chính thức trên **60 bản sạch**: PSD 74,28 · peakprob 82,01 · oracle 83,60 (`analysis/dulieu_results.json`, `benchmark_dpss/eval_cinc60_sach.json`). Kết luận định tính trong tài liệu giữ nguyên trừ khi ghi khác trong `THAMDINH_VONG7.md`. Cụm "tiền đăng ký" trong tài liệu này **không đúng** — tệp khai báo không neo git.

> **Cảnh báo (vòng 7, 12/09/2026).** Tệp này được viết khi CinC 2013 còn tính trên **75 bản ghi**; 15 bản
> trong đó là bản sao ADFECGDB (điều ban tổ chức đã ghi nhận từ 2013 — `survey/RO_RI_VANLIEU.md`). Mọi con
> số CinC-75 ở đây (79,40 / 85,60 / 86,87 / +6,20 / +8,18 / +7,47 …) **đã rút**; số hiện hành trên 60 bản
> sạch: psd 74,28 · gate 80,72 · gate4 81,01 · rrcv 80,00 · peakprob 82,01 · oracle 83,60
> (`analysis/dulieu_results.json → chon_kenh_60_sach`, `benchmark_dpss/eval_cinc60_sach.json`). Số gốc giữ
> nguyên để truy vết; kết luận định tính đọc kèm `analysis/XACNHAN.md`.

# M5 — Chọn kênh mù nhãn: chẩn đoán quy tắc PSD và so sánh 7 quy tắc đã khai báo trước

**Ngày:** 2026-09-12 · **Dung sai:** ±50 ms · **Đơn vị thống kê:** bản ghi (không phải cặp bản-ghi×kênh)

**Khai báo trước:** [`analysis/chonkenh_khaibao_truoc.json`](chonkenh_khaibao_truoc.json) — ghi **trước** khi chạy bất kỳ quy tắc nào.
**Số liệu thô:** [`analysis/chonkenh_results.json`](chonkenh_results.json) · bộ nhớ đệm từng kênh: `analysis/chonkenh_cache/` (97 tệp)
**Hình:** [`analysis/fig_chonkenh.png`](fig_chonkenh.png) · **Kiểm tra rò rỉ:** `chonkenh_results.json → kiem_tra_ro_ri`

**Chạy lại:**

```
python analysis/chonkenh_cache.py --arm cinc     # 1,5 phút
python analysis/chonkenh_cache.py --arm s22      # 5,3 phút
python analysis/chonkenh_rules.py                # 1,0 phút
python analysis/chonkenh_downstream.py           # hệ quả hậu kiểm
python analysis/chonkenh_leakcheck.py            # kiểm tra rò rỉ nhãn
```

---

## 0. Tóm tắt một đoạn

Quy tắc chọn kênh PSD hiện tại **hỏng ở khoảng một phần năm số bản ghi ngoài miền, và khi hỏng thì hỏng rất nặng**: trên 75 bản ghi CinC 2013 set-a nó chọn đúng kênh tốt nhất ở 48/75 bản ghi, nhưng 15 bản ghi còn lại mất hơn 10 điểm F1 và **một mình 15 bản ghi này gánh 7,25 trong tổng 7,47 điểm dư địa** (97%). Bảy quy tắc mù nhãn đã khai báo trước đều được chạy và báo cáo đầy đủ. **Năm quy tắc vượt mốc PSD trên CinC**; quy tắc đơn giản nhất — chọn kênh có **xác suất trung bình của chính mô hình tại các đỉnh đã phát hiện** cao nhất (`peakprob`, không huấn luyện, không siêu tham số) — đạt **85,60 so với 79,40, hiệu +6,20 KTC95 [+3,01; +9,84], p = 7,7e-04, p_Holm = 0,0054**, tức **lấy lại 83,0% dư địa oracle**, đưa số bản ghi F1 < 50 từ **16 xuống 9**, và **không bản ghi nào mất quá 3,90 điểm**. Hai quy tắc còn lại **thất bại và được báo cáo là thất bại**: hợp nhất 4 kênh (+1,75, KTC chứa 0) và bộ chọn kênh học (+2,81, KTC chứa 0). Cảnh báo quan trọng: quy tắc quyết định đã khai báo trước (chọn theo 22 chủ thể trong miền) chỉ ra `gate` chứ không phải `peakprob`, **và nhánh trong miền hầu như không có khả năng phân biệt** (dư địa oracle chỉ 1,08 điểm) — chi tiết ở mục 4.

---

## 1. VIỆC 1 — Chẩn đoán quy tắc PSD hiện tại

Quy tắc hiện tại: chọn kênh có đỉnh mật độ phổ công suất lớn nhất trong dải nhịp thai 1,8–3,0 Hz của đường bao Hilbert tín hiệu dư (theo Power-MF / Jaeger 2024).

Nguồn: `chonkenh_results.json → chan_doan_psd`. Số liệu tái lập khớp tuyệt đối (`|Δ| < 1e-6`) với `benchmark_dpss/eval_cinc75.json` và `benchmark_dpss/eval_22.json` — kiểm chứng bằng `assert` trong `chonkenh_cache.py`.

| Chỉ số | CinC 75 (ngoài miền) | 22 chủ thể (trong miền) |
|---|---:|---:|
| F1 trung bình, quy tắc PSD | **79,40** | **97,56** |
| F1 trung bình, oracle (chặn trên) | 86,87 | 98,63 |
| Dư địa chọn kênh | **7,47** | **1,08** |
| Kênh PSD **đạt** F1 của oracle | 48/75 (64,0%) | 14/22 (63,6%) |
| Hạng của kênh PSD (tốt nhất / 2 / 3 / tệ nhất) | 48 / 10 / 10 / 7 | 14 / 4 / 2 / 2 |
| Mất trung bình **khi chọn sai** | **20,75 điểm** | 2,96 điểm |
| Mất trung vị trên toàn bộ | 0,00 | 0,00 |
| Bản ghi F1 < 50 (PSD → oracle) | **16 → 8** | 0 → 0 |
| Bản ghi F1 ≥ 90 (PSD → oracle) | 48 → 53 | 19 → 21 |

**Phân bố mất mát trên CinC 75** (oracle − PSD):

| Mất | < 1 | 1–5 | 5–10 | 10–20 | 20–50 | ≥ 50 |
|---|---:|---:|---:|---:|---:|---:|
| Số bản ghi | 56 | 4 | 0 | 4 | 7 | **4** |

**Ba phát hiện của VIỆC 1 (đều là *fact*, đọc thẳng từ JSON):**

1. **Mất mát cực kỳ lệch, không phải sai số đều.** Trung vị mất mát là 0: ở 56/75 bản ghi quy tắc PSD thực tế không mất gì. Nhưng 15 bản ghi mất > 10 điểm và gánh **7,25/7,47 = 97,0%** toàn bộ dư địa. Mất lớn nhất là 74,90 điểm (một bản ghi). Nói cách khác, đây **không phải** một quy tắc "hơi kém đều đều" mà là một quy tắc **thỉnh thoảng hỏng toàn phần**.
2. **Trần cứng nhỏ hơn nhiều so với lo ngại.** Chỉ 8/75 bản ghi có **mọi** kênh đều kém (oracle < 50): `a27 a43 a54 a57 a59 a60 a68 a71`. Nhóm này chỉ chiếm **0,61** điểm dư địa. **Dư địa thực tế còn cứu được là 6,86 điểm**, không phải 7,47. (Ghi chú: `a54` và `a71` nằm trong danh sách 7 bản chú thích sai đã khai báo từ trước.)
3. **Trong miền hầu như không có vấn đề gì.** Trên 22 chủ thể dư địa chỉ 1,08 điểm, 19/22 chủ thể mất < 1 điểm, không có bản ghi trần cứng. Chỉ một chủ thể mất > 10 điểm (B1_06: 89,45 → 99,64). Đây là lý do vì sao lỗi chọn kênh **không hiện ra** trong các vòng đo trước — và cũng là lý do nhánh trong miền không đủ sức làm trọng tài (mục 4).

---

## 2. VIỆC 2 — Bảy quy tắc mù nhãn đã khai báo trước

Tất cả quy tắc chỉ đọc: điểm PSD, 12 SQI cổ điển theo đoạn 4 s, và chuỗi phát hiện của mô hình. **Không quy tắc nào nhìn thấy nhãn ở bước suy luận.** Trường F1/TP/FP/FN của từng kênh chỉ dùng để **chấm điểm**, và đối với `gate`/`learned` là để huấn luyện trên dữ liệu **không phải** tập kiểm.

| Mã | Quy tắc | Cần huấn luyện? | Siêu tham số |
|---|---|---|---|
| `psd` | **Mốc chuẩn**: đỉnh PSD 1,8–3,0 Hz lớn nhất | không | không |
| `gate` | Cổng từ chối đã hiệu chuẩn (huấn luyện trên đoạn của **kênh PSD**), chọn kênh có 1 − trung bình P(đoạn xấu) cao nhất | có | không (giữ nguyên tham số vòng trước) |
| `gate4` | Như trên, nhưng huấn luyện trên đoạn của **cả 4 kênh** | có | không |
| `rrcv` | `rr_cv` của chuỗi phát hiện thấp nhất | không | không |
| `peakprob` | Xác suất trung bình của mô hình **tại các đỉnh đã phát hiện** cao nhất | không | không |
| `rrplaus` | Tỉ lệ RR trong 0,3–0,7 s cao nhất (hòa thì phá bằng `rr_cv`) | không | không |
| `fuse` | **Hợp nhất** 4 kênh: gom phát hiện cách nhau ≤ 50 ms, giữ cụm có ≥ k kênh đồng ý | không | **k, chọn trên 22 chủ thể** |
| `learned` | Hồi quy gradient boosting dự đoán F1 từng kênh từ đặc trưng mù nhãn mức bản ghi | có | cố định trước, không dò lưới |

### 2.1 Kết quả trên 75 bản ghi CinC 2013 set-a (ngoài miền, người chấm độc lập)

Mô hình `fetalqrs_tcn_22_production.pt`, zero-shot. Đơn vị = bản ghi, n = 75. KTC95 = cluster bootstrap 10 000 lần lấy mẫu lại bản ghi, seed 0. `p_Holm` = hiệu chỉnh Holm trên **7 quy tắc mới**.

| Quy tắc | F1 TB | Trung vị | ≥90 | <50 | Hiệu vs PSD | KTC95 | p Wilcoxon | p Holm | Thắng/Thua |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| PSD (mốc chuẩn) | 79,40 | 99,27 | 48 | 16 | — | — | — | — | — |
| **peakprob** | **85,60** | 99,28 | 53 | **9** | **+6,20** | [+3,01; +9,84] | **7,7e-04** | **0,0054** | 21/6 |
| gate4 | 84,77 | 99,29 | 53 | 12 | +5,38 | [+2,20; +9,04] | 4,3e-03 | 0,026 | 18/7 |
| gate | 84,54 | 99,28 | 53 | 12 | +5,14 | [+1,94; +8,78] | 0,017 | 0,085 | 17/9 |
| rrcv | 83,98 | 99,31 | 53 | 12 | +4,58 | [+1,27; +8,31] | 0,108 | 0,430 | 16/11 |
| rrplaus | 83,08 | 99,31 | 52 | 14 | +3,68 | [+0,58; +7,23] | 0,116 | 0,430 | 18/10 |
| learned | 82,21 | 99,29 | 52 | 16 | +2,81 | [−0,86; +6,63] | 0,724 | 1,00 | 16/15 |
| fuse (k=2) | 81,15 | 98,58 | 47 | 14 | +1,75 | [−0,33; +4,04] | 0,526 | 1,00 | 21/20 |
| *ORACLE (chặn trên)* | *86,87* | *99,31* | *53* | *8* | *+7,47* | *[+3,98; +11,40]* | *5,6e-06* | — | *27/0* |
| *kênh 0 cố định (hậu kiểm, đã rút)* | *69,33* | *86,92* | *36* | *27* | *−10,07* | *[−18,56; −2,09]* | *0,019* | — | *17/35* |
| *TB 4 kênh (không chọn)* | *74,09* | *80,75* | *30* | *17* | *−5,31* | *[−8,50; −2,40]* | *1,2e-03* | — | *18/41* |
| *kênh tệ nhất (sàn)* | *56,95* | *38,83* | *27* | *42* | *−22,45* | *[−29,31; −16,17]* | *3,5e-10* | — | *0/52* |

Bốn giá trị k của quy tắc hợp nhất (đầy đủ, dù k được chốt trên 22 chủ thể): k=1 → 81,30; k=2 → 81,15; k=3 → 74,85 (−4,55, **kém hơn PSD có ý nghĩa**); k=4 → 56,40 (−23,00).

**Phân tỉ lệ dư địa lấy lại được** (hiệu / 7,47): peakprob **83,0%** · gate4 72,0% · gate 68,8% · rrcv 61,3% · rrplaus 49,2% · learned 37,6% · fuse 23,5%.

**Tần suất đạt F1 của kênh oracle:** PSD 48/75 → peakprob **63/75** · gate4 59/75 · gate 57/75 · rrcv 55/75 · rrplaus 54/75 · learned 53/75.

**Hồ sơ rủi ro (rất bất đối xứng, ủng hộ `peakprob`):**

| Quy tắc | Mất nhiều nhất trên một bản ghi | Số bản mất > 5 điểm | Số bản được > 5 điểm |
|---|---:|---:|---:|
| **peakprob** | **3,90** | **0** | 13 |
| gate / gate4 | 13,39 | 3 | 11 / 12 |
| rrcv | 13,45 | 6 | 10 |
| rrplaus | 21,22 | 4 | 9 |
| fuse (k=2) | 14,74 | 11 | 12 |
| learned | 53,96 | 6 | 8 |

`peakprob` đổi kênh trên 47/75 bản ghi nhưng **chỉ làm đổi F1 quá 1 điểm ở 19 bản ghi**; trong đó 16 bản được và 3 bản mất, bản mất nhiều nhất là 3,90 điểm. Bốn ví dụ được nhiều nhất: a09 19,4 → 94,3 · a11 26,8 → 86,5 · a07 45,6 → 86,9 · a16 22,3 → 78,8 (cả bốn đều chạm đúng oracle).

**Biến thể 68 bản ghi** (loại 7 bản chú thích sai `a33 a38 a47 a52 a54 a71 a74`, danh sách khai báo từ vòng trước): PSD 80,70 → peakprob **87,06** (+6,36 [+2,85; +10,51]), gate4 86,12, gate 85,86, oracle 88,42. Kết luận không đổi.

### 2.2 Kết quả trên 22 chủ thể (trong miền)

Mỗi chủ thể dùng checkpoint fold **không chứa** chủ thể đó; cổng và bộ chọn học đánh giá **leave-one-SUBJECT-out**. n = 22.

| Quy tắc | F1 TB | ≥90 | <50 | Hiệu vs PSD | KTC95 | p Wilcoxon | Thắng/Thua |
|---|---:|---:|---:|---:|---|---:|---:|
| PSD (mốc chuẩn) | 97,56 | 19 | 0 | — | — | — | — |
| gate | **98,61** | 21 | 0 | +1,05 | [+0,00; +2,37] | 0,068 | 4/0 |
| rrcv | 98,60 | 21 | 0 | +1,04 | [−0,00; +2,36] | 0,161 | 6/2 |
| gate4 | 98,58 | 21 | 0 | +1,03 | [−0,02; +2,35] | 0,345 | 3/3 |
| rrplaus | 98,57 | 21 | 0 | +1,01 | [−0,03; +2,33] | 0,508 | 6/4 |
| fuse (k=2) | 98,43 | 21 | 0 | +0,87 | [−0,12; +2,13] | 0,650 | 4/9 |
| peakprob | 98,22 | 20 | 0 | +0,66 | [+0,01; +1,73] | 0,063 | 6/1 |
| learned | 97,62 | 20 | 0 | +0,07 | [−1,05; +1,30] | 0,721 | 5/5 |
| *ORACLE* | *98,63* | *21* | *0* | *+1,08* | *[+0,03; +2,39]* | *0,012* | *8/0* |

Siêu tham số k của quy tắc hợp nhất, **chọn chỉ trên nhánh này**: k=1 → 98,29 · **k=2 → 98,43 (chọn)** · k=3 → 97,99 · k=4 → 93,90. Giá trị k=2 được áp **nguyên xi** sang CinC, không tinh chỉnh lại.

**Ba bản ghi khó của vòng trước phần lớn là lỗi chọn kênh, không phải giới hạn của mô hình:**

| Chủ thể | PSD | gate | rrcv | peakprob | oracle |
|---|---:|---:|---:|---:|---:|
| B1_06 | 89,45 | 99,64 | 99,64 | 99,15 | 99,64 |
| B1_07 | 86,56 | 95,31 | 95,31 | 87,09 | 95,31 |
| B2_03 | 79,72 | 83,91 | 83,91 | 83,91 | 83,91 |

Đây là *suy luận*: hai trong ba bản ghi khó (B1_06, B1_07) được cứu gần hết chỉ bằng cách đổi quy tắc chọn kênh, nên câu chuyện "ba bản ghi khó" của vòng trước phải được **sửa lại** — phần lớn là lỗi của quy tắc chọn kênh, không phải giới hạn của bộ dò. B2_03 vẫn là giới hạn thật (oracle 83,91).

---

## 3. Hai quy tắc THẤT BẠI — báo cáo đúng như đã cam kết

**(d) Hợp nhất 4 kênh — THẤT BẠI.** Ý tưởng "bỏ phiếu thay vì chọn" không hiệu quả. Trên CinC: +1,75 KTC95 **[−0,33; +4,04]**, p = 0,53, thắng 21 thua 20 — tức là đổi được rất nhiều bản ghi nhưng được và mất gần như cân bằng. Trên 22 chủ thể: +0,87 [−0,12; +2,13], thắng 4 thua 9. Yêu cầu đồng thuận chặt hơn còn tệ hơn hẳn (k=3: −4,55; k=4: −23,00), vì kênh xấu kéo cụm tốt xuống dưới ngưỡng phiếu. **Kết luận: chọn một kênh tốt tốt hơn hợp nhất bốn kênh, với bộ dò này.**

**(e) Bộ chọn kênh học — THẤT BẠI.** Trên CinC: +2,81 KTC95 **[−0,86; +6,63]**, p = 0,72, thắng 16 thua 15. Trên 22 chủ thể, đánh giá LOSO: +0,07 [−1,05; +1,30] — về cơ bản bằng mốc chuẩn. Nó cũng có **hồ sơ rủi ro tệ nhất** (một bản ghi mất 53,96 điểm). *Suy luận về nguyên nhân:* chỉ có 88 hàng huấn luyện (22 chủ thể × 4 kênh) với 36 đặc trưng, và phân phối đặc trưng lệch mạnh giữa hai bộ dữ liệu (bản ghi 20 phút của Silesia so với 60 giây của CinC). Một quy tắc **một dòng, không huấn luyện** (`peakprob`) đánh bại nó rõ rệt. Đây là *khuyến nghị*: đừng học bộ chọn kênh cho đến khi có nhiều hơn ~50 chủ thể.

**Một quy tắc "được" nhưng không sống sót hiệu chỉnh đa so sánh:** `rrcv` (+4,58, p_Holm = 0,43) và `rrplaus` (+3,68, p_Holm = 0,43). KTC95 bootstrap của chúng không chứa 0 nhưng p Wilcoxon lớn — nghĩa là hiệu ứng do một số ít bản ghi thắng rất đậm, không phải do đa số bản ghi nhích lên. Không nên dựa vào hai quy tắc này.

---

## 4. VIỆC 3 — Trung thực về đánh giá: chỗ yếu của chính báo cáo này

**4.1 Quy tắc quyết định đã khai báo trước chỉ ra `gate`, KHÔNG phải `peakprob`.** Khai báo trước nói: chọn quy tắc theo F1 trung bình trên 22 chủ thể trong miền, rồi con số CinC của **chính** quy tắc đó mới là bằng chứng xác nhận. Áp đúng luật đó:

> **`gate`**: 22 chủ thể 98,61 → **CinC 84,54, hiệu +5,14 KTC95 [+1,94; +8,78], p = 0,017.**

Đó là kết quả xác nhận hợp lệ duy nhất theo giao thức đã ký. Nó **không** sống sót hiệu chỉnh Holm trên 7 quy tắc (p_Holm = 0,085).

**4.2 Nhánh trong miền gần như không có khả năng phân biệt — tự phê bình.** Bốn quy tắc đứng đầu trên 22 chủ thể cách nhau **0,04 điểm** (98,61 / 98,60 / 98,58 / 98,57) trong khi toàn bộ dư địa oracle chỉ 1,08 điểm. Chọn `gate` thay vì `rrcv` là chọn theo nhiễu. Thiết kế khai báo trước của tôi ở điểm này **sai**: tôi đã giao vai trò trọng tài cho một nhánh đã chạm trần. Đúng ra phải khai báo trước tiêu chí "chỉ chấp nhận nhánh trong miền làm trọng tài nếu dư địa oracle ở đó > X điểm", hoặc phải tách một tập giữ riêng từ CinC ngay từ đầu.

**4.3 Vì sao vẫn có thể nói `peakprob` là lựa chọn tốt nhất, mà không phạm lỗi chọn hậu kiểm.** `peakprob` nằm **trong danh sách 7 quy tắc đã khai báo trước**, và hiệu ứng của nó trên CinC **sống sót hiệu chỉnh Holm trên toàn bộ 7 quy tắc** (p_Holm = 0,0054 < 0,05). Nghĩa là: ngay cả khi coi việc chọn quy tắc là hoàn toàn hậu kiểm trong tập đã khai báo, kết luận vẫn đứng ở mức 5%. Đây là điểm khác biệt cốt lõi so với sai lầm "kênh 0 cố định" của vòng trước, vốn được chọn sau khi nhìn 10 bản ghi và **không** hề khai báo trước (và trên 75 bản ghi tụt từ 90,34 xuống 69,33 — nay đo lại đúng bằng 69,33, xác nhận việc rút lại là đúng).

**4.4 CinC 75 từ nay KHÔNG còn "trinh nguyên" cho câu hỏi chọn kênh.** Bảy quy tắc đã được đo trên nó. Mọi tuyên bố tiếp theo về chọn kênh phải dùng dữ liệu mới (CinC set-b/set-c nếu lấy được nhãn, hoặc một trung tâm ghi thứ hai). Con số +6,20 nên được coi là **ước lượng có thể lạc quan** cho hiệu năng trên dữ liệu tương lai.

**4.5 Kiểm tra rò rỉ nhãn đã chạy và đã qua.** `analysis/chonkenh_leakcheck.py` thay nhãn thật của từng bản ghi bằng nhãn ngẫu nhiên rồi chạy lại quy tắc: **776/776 lựa chọn (8 quy tắc × 97 bản ghi) không đổi**. Đối chứng dương cho thấy phép thử đủ nhạy (F1 từng kênh của a01 tụt từ [100,0; 81,0; 40,6; 96,2] xuống [24,8; 24,7; 15,9; 22,2] khi xáo nhãn). *Giới hạn của phép thử:* với `gate`/`gate4`/`learned` nó chỉ chứng minh **bước chọn** không đọc nhãn; việc **điểm số** được tính mù nhãn thì dựa vào mã nguồn — cổng chỉ nhận `seg_feat` (12 SQI, không đặc trưng nào nhìn thấy nhãn) và bộ phân loại được huấn luyện leave-one-SUBJECT-out (nhánh 22 chủ thể) hoặc chỉ trên 22 chủ thể (nhánh CinC).

**4.6 Không tinh chỉnh gì trên CinC.** Siêu tham số duy nhất (k của quy tắc hợp nhất) được chốt trên 22 chủ thể rồi áp nguyên. Cổng và bộ chọn học không bao giờ thấy dữ liệu CinC trong tập huấn luyện. `peakprob`, `rrcv`, `rrplaus` hoàn toàn không có tham số nào để tinh chỉnh.

---

## 5. Hệ quả HẬU KIỂM (không nằm trong khai báo trước)

`analysis/chonkenh_downstream.py`, khóa `he_qua_hau_kiem` trong `chonkenh_results.json`. **Đây là mô tả, không phải bằng chứng** — quy tắc chọn kênh đã được thử trên chính 22 chủ thể này.

Khoảng cách giữa RelyFetal một kênh và Power-MF bốn kênh trên 22 chủ thể:

| Quy tắc chọn kênh của RelyFetal | RelyFetal | Power-MF 4 kênh | Hiệu | KTC95 | p Wilcoxon |
|---|---:|---:|---:|---|---:|
| PSD (hiện tại) | 97,56 | 98,83 | −1,27 | [−3,07; +0,25] | 0,156 |
| gate | 98,61 | 98,83 | **−0,22** | **[−0,96; +0,34]** | 0,098 |
| rrcv | 98,60 | 98,83 | −0,23 | [−0,97; +0,33] | 0,129 |
| oracle | 98,63 | 98,83 | −0,20 | [−0,94; +0,37] | 0,098 |

*Suy luận:* phần lớn khoảng cách 1,27 điểm giữa một kênh và bốn kênh **không phải** do thiếu thông tin đa kênh mà do **chọn sai kênh**; khi chọn kênh tốt hơn, khoảng cách còn 0,22 điểm và **độ rộng KTC co từ 3,3 xuống 1,3 điểm**. Nhưng đây là con số hậu kiểm trên dữ liệu đã dùng để so quy tắc; phải kiểm lại trên dữ liệu mới trước khi đưa vào bài báo.

---

## 6. Khuyến nghị

1. **Thay quy tắc PSD bằng `peakprob` trong pipeline suy luận** (chạy mô hình trên các kênh sẵn có, chọn kênh có xác suất trung bình tại đỉnh cao nhất). Chi phí: chạy mô hình 4 lần thay vì 1 — 4 × 4,35 ms mỗi cửa sổ 4 giây, vẫn nhanh hơn thời gian thực khoảng 230 lần. Không thêm tham số, không thêm huấn luyện, không thêm phụ thuộc.
2. **Báo cáo cả hai con số trong bài báo**: quy tắc đã khai báo trước (`gate`, +5,14) và quy tắc tốt nhất trong tập khai báo trước (`peakprob`, +6,20, sống sót Holm), kèm đúng mục 4 này. Không được báo cáo chỉ con số lớn nhất.
3. **Rút lại cách diễn đạt "ba bản ghi khó"** trong các tài liệu hiện có: B1_06 và B1_07 phần lớn là lỗi chọn kênh, không phải giới hạn của bộ dò (mục 2.2).
4. **Không theo đuổi bộ chọn kênh học** cho đến khi n ≥ 50 chủ thể.
5. **Không dùng hợp nhất đa kênh** với kiến trúc hiện tại.
6. **Vòng sau cần một tập xác nhận mới** cho chọn kênh (CinC set-b/set-c nếu có nhãn). Không có nó thì con số +6,20 vẫn là ước lượng trong nhà.

---

## 7. Hạn chế

1. **CinC 75 đã bị dùng để so 7 quy tắc**, nên không còn là phép thử độc lập cho câu hỏi chọn kênh. Ước lượng +6,20 có thể lạc quan.
2. **Nhánh trong miền chạm trần** (dư địa oracle 1,08 điểm; 4 quy tắc đầu cách nhau 0,04 điểm) nên quy tắc quyết định khai báo trước thực chất chọn theo nhiễu — lỗi thiết kế của chính báo cáo này, xem mục 4.2.
3. **Chỉ một mô hình, một hạt giống.** Toàn bộ so sánh chạy trên `fetalqrs_tcn_22_production.pt` (CinC) và 11 checkpoint fold (22 chủ thể), seed 0. Chưa biết quy tắc chọn kênh có ổn định qua các hạt giống hay không. Vòng trước đo |hiệu| trung bình 0,28 điểm giữa 2 hạt giống ở mức bản ghi, nhưng **chưa đo cho quy tắc chọn kênh**.
4. **`peakprob` phụ thuộc vào chính ngưỡng của mô hình.** Nó lấy xác suất trung bình tại các đỉnh đã vượt ngưỡng, nên đổi ngưỡng sẽ đổi cả tập đỉnh lẫn điểm số. Chưa đo độ nhạy theo ngưỡng.
5. **Cả bốn kênh đều là kênh bụng của cùng một thiết bị, cùng một lần đặt điện cực.** Kết quả không nói gì về việc chọn kênh khi các kênh đến từ vị trí điện cực hoặc thiết bị khác nhau.
6. **8/75 bản ghi CinC có trần cứng** (oracle < 50): không quy tắc chọn kênh nào cứu được, và 2 trong số đó nằm trong danh sách chú thích sai. Với nhóm này cần cải tiến bộ dò hoặc từ chối bản ghi, không phải chọn kênh.
7. **Dữ liệu trong miền chỉ có 22 chủ thể từ 2 trung tâm**, và 5 chủ thể Silesia B2 trùng với PhysioNet ADFECGDB đã được loại; công suất thống kê ở nhánh này thấp (mục 4.2).
8. **Nhãn B1 là gián tiếp** (`fqrs_all`, kể cả nhịp có 0). Mọi con số của 10 chủ thể B1 kế thừa hạn chế đó; theo ghi chú vòng trước, **cấm dùng số B1 để nói về jitter/STV**.
