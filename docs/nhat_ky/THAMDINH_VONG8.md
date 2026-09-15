# THẨM ĐỊNH VÒNG 8 — phản biện độc lập cuối cùng

**Ngày:** 12/09/2026 · **Phạm vi:** ba sản phẩm do P1 (bài báo), P2 (kịch bản + tóm tắt), P3 (demo + repo) nộp
**Nguồn sự thật:** `survey/facts_phase4.json` + các tệp JSON gốc trên đĩa
**Nguyên tắc:** tìm chỗ sai, không xác nhận. Không sửa tệp nào.

---

## 0. Kết luận một dòng

Ba sản phẩm mới **sạch hơn mong đợi**: 0 con số đã rút được phát biểu như sự thật trong bài báo, kịch bản, tóm tắt và demo; 25/25 con số đối chiếu đều khớp JSON gốc (kể cả một phép tính tôi tự chạy lại từ đầu). **Việc còn lại lớn nhất không nằm ở ba sản phẩm này mà ở đề cương LaTeX** — `sec_4_6.tex` và `sec_7_12.tex` vẫn phát biểu 71,21 / 7,00 điểm / 22-16/75 bản như sự thật, và **bản DOCX gửi giảng viên đang chậm một phiên bản rưỡi**.

---

## VIỆC 1 — BÀI BÁO (`docs/CinC2027_RelyFetal.pdf`)

### 1.1 Hình thức

| Kiểm | Kết quả |
|---|---|
| Số trang | **4 trang đúng** (pypdf) |
| PDF có khớp nguồn không | `md5 = 4a28595…` giống hệt `paper/cinc2026/main.pdf` → **PDF là bản hiện hành**, không phải bản cũ |
| Số đã rút trong PDF | **0/16** (94,87 · 2,74 · 98,38 · 97,33 · 59,15 · 69,31 · 77,34 · 90,34 · 22,33 · +11,00 · 79,40 · 85,60 · 86,87 · 71,21 · 62,82 · AUROC 0,980) |
| Từ cấm | **0** — không có `first` / `novel` / `SOTA` / `pre-registered` / `discovered` / `bottleneck` |
| Cỡ chữ Bảng 3 & 4 | **7,97 pt** (đo trực tiếp từ PDF), không phải ~7 pt như P1 tự khai. Tài liệu tham khảo mới là 6,97 pt. **Đọc được.** P1 tự khai bi quan hơn thực tế — an toàn. |

> ⚠️ **Rủi ro hình thức chưa đóng.** Đầu `main.tex` ghi: *"the official CinC class (cinc.cls) is not installed on this machine; the layout below imitates it"*. **"4 trang" là 4 trang trên một bản NHÁI template**, không phải trên `cinc.cls` thật. Phải dựng lại bằng template chính thức trước khi nộp; số trang có thể đổi.

### 1.2 Đối chiếu số với JSON nguồn — **25 con số, 25 khớp, 0 lệch**

Đề bài yêu cầu 15; tôi kiểm 25 để phủ cả phần P1 tự khai là "tính lại, không có JSON riêng".

| # | Con số trong bài | Tệp nguồn | Khớp |
|---|---|---|---|
| 1 | 12,12 (PMF4 − PMF1) | `analysis/recovery_ratio.json` → 12,1212 | ✅ |
| 2 | phục hồi 10,85 điểm | 〃 → 10,847 | ✅ |
| 3 | 89,5 % [81,4; 103,2] | 〃 → 89,49; [81,4; 103,16] | ✅ |
| 4 | jackknife 88,6–93,4 | 〃 → [88,62; 93,43] | ✅ |
| 5 | 74,28 (PSD, m22, 60 sạch) | `facts_phase4` A.psd.m22 | ✅ |
| 6 | 64,04 [55,4; 72,5] (m5) | 〃 m5 = 64,04; [55,39; 72,53] | ✅ |
| 7 | ≥90: 27→33 · <50: 22→16 | 〃 m5/m22_ge90, _lt50 | ✅ |
| 8 | trung vị 95,07 | 〃 m22_median | ✅ |
| 9 | 56,00 / 67,69 (4 kênh) | 〃 A.mean4 | ✅ |
| 10 | oracle 83,60 · +9,32 [5,10; 14,15] · trúng 17/60 | 〃 A.oracle, psd_vs_oracle_m22 | ✅ |
| 11 | 53 bản: 64,19→75,27, +11,08, p 4,4·10⁻⁹ | 〃 A.53_ban_loai_7_nhan_sai | ✅ |
| 12 | PMF1 CinC 55,97 · +18,32 [13,4; 23,6] | 〃 A.powermf_1ch_60_sach | ✅ |
| 13 | gate 80,72 · +6,44 [2,49; 11,10] · Holm 0,051 | 〃 B.gate_chi_dinh_truoc | ✅ |
| 14 | gate4 81,01 Holm 0,015 · rrcv 80,00 Holm 0,41 | 〃 B | ✅ |
| 15 | peakprob 82,01 · +7,73 [3,82; 12,41] · Holm 0,0039 · 19/35/6 | 〃 B.peakprob_hau_kiem | ✅ |
| 16 | 82,9 % dư địa oracle | 〃 B → 82,92 | ✅ |
| 17 | âm tính giả 18,0 % [12,1; 25,0] | 〃 C cinc60\|psd → 0,17973; [0,1213; 0,2497] | ✅ |
| 18 | Kiến trúc F1 97,64 / 96,93 / 96,84 / 96,38 / 94,53 + tham số + RF | `analysis/kientruc_results.json` → table | ✅ |
| 19 | CNN 60 ms Δlogit −1,64 [−2,09; −1,16] · 2/0/20 | 〃 comparisons.cnn_l → −1,6384; [−2,0863; −1,1573] | ✅ |
| 20 | Dải: +2,44 [−0,04; 6,29] · −0,07 [−0,51; 0,39] | `pilot_evidence/band_tcn_stats.json` → 2,4355 [−0,0409; 6,2944]; −0,0651 [−0,506; 0,3865] | ✅ |
| 21 | Thích nghi miền +0,25 / −0,67 / −1,58 / −2,43 | **Tôi tự tính lại** từ `adapt/per_record_cinc`, loại 15 bản rò rỉ | ✅ **khớp tuyệt đối** |
| 22 | AUROC gộp 0,965 · trong bản ghi 0,934 | `analysis/gate22_results.json` → 0,96465 / 0,93357 | ✅ |
| 23 | 25 / 447 bản Challenge | `survey/ro_ri_vanlieu.json` (Clifford 2014 "total of 447 records"; Silva 2013 Bảng 1) | ✅ |
| 24 | 48/48 ca kiểm findpeaks | `baselines/BASELINES.md` → `octave/test_fpmpd.m` | ✅ |
| 25 | −1,27 [−3,08; +0,27] p 0,16 | `facts_phase4` D | ✅ |

**Điểm đáng khen nhất:** mục 21. P1 tự khai *"thích nghi miền 60-sạch tính lại từ per_record, không có JSON riêng"* — tôi tự viết lại phép tính từ `adapt/per_record_cinc` (loại đúng 15 bản rò rỉ, bootstrap 10.000 lần) và **ra đúng mốc 74,2805 cùng cả bốn hiệu số**. Không bịa.

**Hai ghi chú ngược chiều (lỗi KHÔNG thuộc bài báo):**
- `survey/facts_phase4.json` ghi KTC dải lọc là `[-0,05; +6,30]` và `[-0,49; +0,40]`; JSON gốc là `[-0,0409; 6,2944]` và `[-0,506; 0,3865]`. **Bài báo đúng, tệp "nguồn sự thật" làm tròn sai.** Cần sửa `facts_phase4.json`.
- Bảng trong ảnh demo `12_tong_hop.png` ghi `-1,27 [-3,07; +0,25]` và `+10,85 [+6,85; +15,25]`; bài báo ghi `[-3,08; +0,27]` và `[+6,80; +15,40]`. Hai lần bootstrap khác nhau. **Phải thống nhất một con số** — hội đồng sẽ mở song song hai thứ.

### 1.3 Các kiểm định nội dung bắt buộc

| Yêu cầu | Kết quả |
|---|---|
| Trích Silva 2013 + Clifford 2014 cho chồng lấn | ✅ `refs.bib` có `silva2013` + `clifford2014`; §2.1 viết *"this was documented by the Challenge organisers… (Table 1 of [1], Table 2 of [2])"*. Không hề nhận công phát hiện — dùng đúng chữ *"we identify by measurement"*. |
| Bảng chọn kênh có CẢ gate (trượt Holm) lẫn peakprob (hậu kiểm) | ✅ Bảng 3: `gate — confirmatory, failed — Holm 0.051`; `peakprob — post-hoc choice — Holm 0.0039`. Nhãn rõ ràng. |
| Có câu nào kết luận "missing fetal signal" | ✅ **Không.** Ngược lại: *"we do not conclude from this that the signal is missing, because the test that would show it has an 18 % false-negative rate."* |
| Kiến trúc có báo cáo trên logit | ✅ Bảng 4 có cột `Δlogit` riêng; §3.4 kết: *"every architecture claim here is stated on both."* |
| Limitations có: hậu kiểm / không bộ thứ ba / 1 seed / 22 chủ thể | ✅ **Đủ cả bốn** — (i) n = 22, một bệnh viện một hệ ghi; (iii) *"peakprob is post hoc; no third labelled dataset exists"*; (iv) *"one seed"*; cộng thêm (vii) tự rút số cổng trên 75 bản. |

### 1.4 LỖI THỰC SỰ TÌM ĐƯỢC TRONG BÀI BÁO (2 lỗi)

**L1 — SAI SỰ THẬT trong câu dẫn Bảng 3 (dòng `main.tex:274`).**
> *"Table 3 reports the seven pre-specified alternatives."*

Bảng 3 **chỉ có 4** quy tắc: `gate`, `gate4`, `rrcv`, `peakprob`. **Thiếu `rrplaus` (78,87), `learned` (77,80) và `fuse`.** Đây là lỗi nặng về hình thức vì: (a) câu văn sai; (b) hiệu chỉnh Holm được khai là "trên bảy quy tắc" nhưng người đọc chỉ thấy bốn, không tự kiểm được; (c) **ba quy tắc bị bỏ đúng là ba quy tắc yếu nhất** → trông như báo cáo chọn lọc, dù thực tế không phải. **Phải thêm 3 dòng hoặc sửa câu thành "four of the seven".**

**L2 — Mâu thuẫn nội bộ về dư địa oracle trong miền.**
§3.1 và Thảo luận: *"the PSD rule sits within 1.90 points of the oracle"*. §3.3: *"the whole oracle headroom is 1.08 points"* (trên 22 chủ thể). Hai con số này đúng theo hai nghĩa khác nhau (1,90 = trường hợp xấu nhất ở Silesia B1; 1,08 = dư địa gộp), nhưng bài **không nói ra sự khác nhau đó**. Phản biện sẽ bắt. Thêm 5 chữ là xong.

### 1.5 Điểm yếu dễ bị khai thác nhất (không phải lỗi)

`gate4` là quy tắc **chỉ định trước** và **sống sót Holm (p = 0,015)**, F1 81,01 — cao hơn `gate`. Bài chỉ để nó nằm im trong bảng, phần lời văn nhảy thẳng từ "gate trượt Holm" sang "peakprob hậu kiểm". Phản biện sẽ hỏi ngay: *"vì sao quy tắc trọng tài không chọn gate4?"* Bài có tự khai trọng tài trong miền vô dụng (bốn quy tắc tốt nhất cách nhau 0,04 điểm — *"a design error on our part"*), nên câu trả lời tồn tại, nhưng **chưa được viết ra**. Đây là chỗ nhóm đang **bán rẻ** kết quả trung thực mạnh nhất mình có. Nên thêm một câu.

---

## VIỆC 2 — KỊCH BẢN + TÓM TẮT (P2)

### 2.1 Số đã rút / từ cấm — **0 lỗi**

Quét `KICH_BAN_TRINH_BAY.md`, `TOM_TAT_1_TRANG.md`, `EUREKA.md`, `CHIEN_LUOC_CONG_BO.md` với 14 con số đã rút + 8 cụm từ cấm, loại ngữ cảnh rút lại: **không có lần trúng nào**.

### 2.2 `CHIEN_LUOC_CONG_BO.md` — đã sửa đúng

- Physiological Measurement ghi **"Q2 Physiology (25/73), Q3 Biomedical Eng. (51/89) — không phải Q1"** ✅
- **CinC 2026 đã bị loại đúng lý do**: *"kỳ 2026 ở Madrid đã diễn ra 20–23/9/2026 nên không còn là lựa chọn"* → chuyển CinC 2027 (Auckland, abstract ~4/2027) ✅
- Còn cảnh báo đúng chỗ: *"nếu tiêu chí Eureka/trường dùng Scimago thì PM không đạt mốc Q1"* ✅

### 2.3 `TOM_TAT_1_TRANG.md` — **LỖI: KHÔNG VỪA 1 TRANG**

Đếm thật: **877 từ / 35 dòng**. P2 tự khai "~877 từ, vừa 1 trang ở cỡ 10–10,5". Con số từ thì đúng, **kết luận thì sai**: A4 lề 2 cm, chữ 10 pt, giãn dòng đơn chứa khoảng **600–650 từ**; 10,5 pt còn ít hơn. 877 từ ≈ **1,35–1,45 trang**, chưa kể tiêu đề và bảng markdown ăn thêm chiều dọc. **Phải cắt ~230–280 từ hoặc đổi tên tệp.** Một tờ "tóm tắt 1 trang" tràn sang trang 2 là lỗi gây mất điểm ngay ở bàn giấy.

*(Phần đánh giá văn phong lời thoại và rà 12 câu hỏi–trả lời được giao cho một luồng phụ; luồng đó chưa trả kết quả trước khi hết ngân sách 60 phút. Xem mục "Việc còn lại" #7.)*

---

## VIỆC 3 — DEMO (P3) — **TỰ CHẠY, ĐẠT**

| Kiểm | Lệnh / kết quả |
|---|---|
| Test lõi | `pytest demo/test_core.py -q` → **17 passed** |
| Toàn bộ | `pytest tests/ demo/test_core.py -q` → **60 passed** ✅ **Khai "60/60" là ĐÚNG** (17 demo + 43 tests/) |
| `run_check.py` | Chạy 5 bản minh hoạ, **0,7 phút**, exit 0. Tái lập đúng: a09 = 94,25 · a02 = 24,91 · a27 = 32,94 · B2_03 = 83,91 · r01 = 99,92 — khớp ảnh chụp. |
| Số ảnh | **12 ảnh** `.png` ✅ |
| Ảnh có số đã rút? | Mở `02_r01_the_so.png` và `12_tong_hop.png`: **không có**. |
| 5 bản minh hoạ có bản rò rỉ? | **Không.** r01, a09, B2_03, a02, a27 — **không bản nào** nằm trong 15 bản rò rỉ (a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25) ✅ |

**Ảnh `12_tong_hop.png` là sản phẩm mạnh nhất của cả vòng này.** Nó hiển thị đúng bảng 60 bản sạch, nhãn `gate — quy tắc KHAI BÁO TRƯỚC` + `trượt Holm`, `peakprob — HẬU KIỂM`, và dòng chốt: *"Mọi con số CinC trên 75 bản ghi đã công bố trước đây đều bị rút. Không có con số nào trong demo lấy từ 75 bản."* Ảnh `02` còn tự khai *"checkpoint 22 ca, fold 05 (chủ thể r01 KHÔNG nằm trong tập huấn luyện)"* và giới hạn của cổng tin cậy.

**Hai điểm nhỏ:**
- **P3 tự khai sai:** *"demo/README.md a03/a08 (rò rỉ) → thay"*. Thực tế **không thay** — bảng mục 4 vẫn còn a03/a04/a05/a08 với **F1 = 100,00 in đậm** (`demo/README.md:119–124`). Nhưng có hộp cảnh báo ở đầu tệp nêu đích danh 4 bản đó và ghi *"Bảng mục 4 giữ để truy vết"* → **không tính là lỗi nội dung**, chỉ là tự báo cáo không chính xác.
- `run_check.py` in **r01 hai lần** trong bảng kết quả (dòng đầu và dòng cuối). Lỗi hiển thị nhỏ, nên sửa trước khi chiếu.

---

## VIỆC 4 — RÀ TOÀN REPO · **ĐỀ CƯƠNG LÀ VIỆC CÒN LẠI LỚN NHẤT**

### 4.1 Đề cương đã đồng bộ 60 bản sạch chưa? — **CHƯA, mới một nửa**

Đã làm đúng:
- Trang bìa `de_cuong.tex:41–48`: khai báo rút v3.5 đầy đủ, ghi rõ *"ban tổ chức đã ghi nhận từ 2013 (Silva 2013, Bảng 1; Clifford 2014, Bảng 2)… nhóm bỏ sót"*, nêu số đúng 74,28 / 60 bản, PM Q2/Q3 ✅
- `sec_cinc75.tex:5`: có hộp `canhbao` cấp mục phủ toàn bộ bảng 75 bản trong mục đó ✅

**Còn sót — số đã rút phát biểu NHƯ SỰ THẬT, không có hộp cảnh báo tại chỗ:**

| Tệp:dòng | Nội dung | Số đúng hiện hành |
|---|---|---|
| `de_cuong_latex/sec_4_6.tex:583` | *"vẫn là quy tắc mù nhãn tốt nhất khi ra ngoài miền (**71,21** so với 58,72 của kênh cố định)"* | 74,28 |
| `de_cuong_latex/sec_4_6.tex:588` | *"ngoài miền nó kém oracle **7,00 điểm** (**71,21** so với **78,21**), và với mô hình 22 ca là **7,47 điểm**. Quy tắc chỉ chọn trúng kênh oracle ở **22/75** bản ghi."* | **9,32 điểm · 74,28 vs 83,60 · 17/60** |
| `de_cuong_latex/sec_4_6.tex:556–557` | hộp `canhbao` (về bản 3.3) khẳng định *"Trên toàn bộ 75 bản ghi… quy tắc mù nhãn đạt **71,21**"* — hộp nói về một lần rút khác, nên câu này vẫn đứng như sự thật | 74,28 |
| `de_cuong_latex/sec_4_6.tex:621` | chú thích hình: *"22/**75** bản ghi dưới 50 với mô hình 5 ca"* | 22/**60** |
| `de_cuong_latex/sec_4_6.tex:627–628` | *"trên **75** bản ghi, 22 bản dưới 50 (m5) và 16 bản (m22)"* | mẫu số phải là **60** |
| `de_cuong_latex/sec_7_12.tex:135–136` | *"sai trên toàn bộ 75: vẫn còn **16/75** bản ghi dưới 50 với mô hình 22 ca. Đây là điểm yếu số một của đề tài"* | **16/60** |
| `de_cuong_latex/sec_7_12.tex:260` | *"**69,31**, trong khi lấy cố định kênh 0 cho **90,34**"* (mẫu 10 bản, đã rút) | đã rút |
| `de_cuong_latex/sec_7_12.tex:292–293` | *"Đem ra **65 bản ghi** chưa thấy… Trên 75 bản ghi, vẫn còn 16 bản dưới 50"* | 65 = 75−10, không còn hợp lệ |
| `de_cuong_latex/sec_7_12.tex:311–312` | bài học rút ra: *"Nếu có **75 bản ghi thì chạy 75**"* | **bài học nay đã sai ngược** — phải chạy 60 |
| `de_cuong_latex/sec_7_12.tex:403` | *"**đánh giá CinC 2013 trên toàn bộ 75 bản ghi** … xong"* (báo cáo tiến độ) | phải là 60 sạch |
| `de_cuong_latex/sec_7_12.tex:417` | *"sau khi thấy **16/75** bản ghi CinC vẫn dưới 50"* | 16/60 |
| `de_cuong_latex/sec_1_3.tex:245` | kế hoạch kiểm định H5: *"Hiệu số ghép cặp trên **75 bản ghi** CinC 2013… tập duy nhất đủ lực để dùng p"* | 60 bản |
| `de_cuong_latex/sec_7_12.tex:393` | *"P1 phần lớn: **8 kiến trúc** chạy lại đúng giao thức"* | cụm đã rút; bài báo dùng 6 + TCN = 7 |
| `de_cuong_latex/sec_7_12.tex:407` | *"demo Gradio…, **53 test**, CI"* | nay là **60 test** |
| `sec_1_3.tex:191` · `sec_4_6.tex:620` · `sec_silesia.tex:92` | dùng **"lưỡng cực"** như đặc tính cơ chế | bài báo đã đổi sang *"split, not shifted"* |

**Tổng: 15 chỗ.** Đây là **việc còn lại lớn nhất của cả đề tài**, và P1/P2/P3 đều không được giao.

### 4.2 **PHÁT HIỆN NẶNG: bản DOCX gửi giảng viên đang chậm một phiên bản rưỡi**

```
de_cuong_latex/_flat.tex            09:42   ← sinh bởi make_docx.py, nội dung v3.4
docs/De_cuong_NCKH_RelyFetal.docx   09:42   ← dựng TỪ _flat.tex  ⇒ CHƯA CÓ v3.5
docs/De_cuong_NCKH_RelyFetal.pdf    17:09   ← dựng từ de_cuong.tex (17:01) ⇒ CÓ v3.5
```

`_flat.tex:58` vẫn viết **"số đúng là 79,40 trên toàn bộ 75"** — tức **bản DOCX hiện nằm trong `docs/` khẳng định 79,40 là số đúng, hoàn toàn không có phần rút v3.5**. Nếu giảng viên mở file Word thay vì PDF, họ đọc đúng phiên bản mà nhóm đã tự rút. **Phải chạy lại `make_docx.py` hoặc xoá tệp DOCX trước buổi gặp.**

### 4.3 Các tệp KHÔNG tính là lỗi (đã có hộp cảnh báo đúng chuẩn)

- `README.md:626–640` — bảng *Retractions*, đúng chức năng.
- `docs/README_KET_QUA.md` — có banner đầu tệp liệt kê đích danh mọi mục đã rút (75 bản, +11,00, "8 kiến trúc", "mô hình không phải nút thắt", "PM là Q1") và ghi *"KHÔNG phải trạng thái hiện hành"*. Các số 79,40 / 62,82 / +11,00 bên trong được phủ.
- `docs/DE_CUONG_NCKH_v2.md` — có banner *"Tài liệu lịch sử"*.
- `demo/README.md` — có banner nêu đích danh a03/a04/a05/a08.
- `paper/cinc2026/CHANGELOG.md`, `main.tex.bak_v75`, `refs.bib.bak_v75` — tệp lịch sử/nhật ký.
- Mọi lần xuất hiện của "tiền đăng ký" / "pre-registered" đều nằm trong câu tự bác bỏ (`README.md:181`, `README.vi.md:153`). ✅

---

## VIỆC 5 — PHÁN XỬ VÀ XÁC SUẤT

### 5.1 Phán xử từng sản phẩm

| Sản phẩm | Phán xử | Căn cứ |
|---|---|---|
| **P1 — bài báo CinC 2027** | **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN** | 4 trang, 0 số đã rút, 25/25 số khớp nguồn, trích Silva/Clifford đúng, limitations đủ bốn mục, không kết luận "missing signal". **Ba điều kiện:** (1) sửa câu "seven pre-specified" ở dòng 274; (2) làm rõ 1,90 vs 1,08; (3) **dựng lại bằng `cinc.cls` chính thức** rồi kiểm lại số trang. |
| **P2 — kịch bản + tóm tắt** | **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN** | 0 số đã rút trên cả 4 tệp; `CHIEN_LUOC_CONG_BO.md` đã sửa đúng PM = Q2 và CinC 2027. **Một điều kiện cứng:** `TOM_TAT_1_TRANG.md` 877 từ **không vừa 1 trang** — cắt ~250 từ. Phần văn phong lời thoại và 12 câu Q&A **chưa được rà xong** trong ngân sách. |
| **P3 — demo + repo** | **DÙNG ĐƯỢC NGAY** | Tôi tự chạy: 60/60 test thật, `run_check.py` tái lập đúng số, 12 ảnh, 0 số đã rút trong ảnh, 5 bản minh hoạ không dính bản rò rỉ nào. Hai điểm nhỏ (tự báo cáo sai về `demo/README.md`; r01 in hai lần) không chặn dùng. |
| **Đề cương LaTeX** *(không ai được giao)* | **CẦN LÀM LẠI (một phần)** | 15 chỗ số 75 bản / số đã rút đứng như sự thật ở `sec_4_6.tex`, `sec_7_12.tex`, `sec_1_3.tex`. |
| **`docs/De_cuong_NCKH_RelyFetal.docx`** | **PHẢI BỎ hoặc dựng lại ngay** | Là bản v3.4, khẳng định 79,40 là số đúng, không có phần rút v3.5. |
| **`survey/facts_phase4.json`** | **VỚI ĐIỀU KIỆN** | Làm tròn sai hai KTC dải lọc so với JSON gốc. "Nguồn sự thật" mà sai thì nguy hiểm hơn tài liệu sai. |

### 5.2 Xác suất cuối cùng

| Đích | Xác suất | Căn cứ |
|---|---|---|
| **Tạp chí Q1** (JBHI / TBME / BSPC) | **12 %** trong 6 tháng · **32 %** trong 12 tháng | Rào cản không phải chất lượng viết mà là **không có bộ thứ ba có nhãn fQRS thật** — đã kiểm và loại NIFEADB, NInFEA, nifecgdb, set-b. Kết quả chính là *"không tách biệt được với Power-MF"* (dấu âm −1,27) cộng một giả thuyết hậu kiểm. Q1 đòi kết quả dương. |
| **Physiological Measurement (Q2)** | **58 %** | Đúng sân nhà (Behar/Clifford/Andreotti/Jezewski, set-a xuất phát từ đây), toà soạn quen kết quả âm tính và phê bình thước đo. **Bài kiểm toán rò rỉ thuộc về đúng tạp chí này.** Trừ điểm vì n = 22, một bệnh viện, một hạt giống. Trùng ước lượng 0,55–0,65 của `CHIEN_LUOC_CONG_BO.md`. |
| **Hội nghị A\*** | **4 %** | Không có hội nghị A\* nào đúng chủ đề. CinC **không phải A\***. Đây gần như là một ô trống, cần nói thẳng với giảng viên chứ đừng để trong bảng mục tiêu. |
| **Euréka 2026** | **8 %** | Hết thời gian. Còn 15 chỗ phải sửa trong đề cương + DOCX hỏng + tóm tắt tràn trang. Kỳ 2026 thực tế đã đóng. |
| **Euréka 2027** | **62 %** | Đây mới là đích thật. Bộ bằng chứng cực mạnh cho một giải sinh viên: **tự phát hiện và tự rút bốn kết luận của chính mình**, có demo chạy được, 60 test, bảng Retractions công khai. Điểm trừ duy nhất: PM là Q2 — nếu hội đồng chấm theo Scimago thì không có bài Q1. **Chủ nhiệm phải xác minh hội đồng dùng thang Scimago hay WoS-JCR.** |

---

## DANH SÁCH VIỆC CÒN LẠI — theo thứ tự làm

| # | Việc | Vì sao xếp ở đây | Ước lượng |
|---|---|---|---|
| **1** | **Dựng lại hoặc xoá `docs/De_cuong_NCKH_RelyFetal.docx`** | Rủi ro cao nhất, chi phí thấp nhất. Giảng viên mở Word là thấy ngay 79,40 — con số nhóm đã tự rút. Một lệnh `python make_docx.py`. | 5 phút |
| **2** | **Cắt `TOM_TAT_1_TRANG.md` từ 877 xuống ≤ 620 từ** | Đây là tờ giấy duy nhất chắc chắn được đọc. Tràn trang là mất điểm ngay. | 20 phút |
| **3** | **Sửa 3 chỗ nặng nhất trong đề cương**: `sec_4_6.tex:583, 588` và `sec_7_12.tex:135` | Ba câu này khẳng định 71,21 / 7,00 điểm / 16-22 trên 75 bản như sự thật, ở đúng đoạn lập luận cho đóng góp C3 và ở đúng dòng "điểm yếu số một của đề tài". | 30 phút |
| **4** | **Sửa 2 lỗi trong bài báo**: câu "seven pre-specified" (`main.tex:274`) + làm rõ 1,90 vs 1,08 | Lỗi thật, sửa nhanh, và lỗi #1 làm bài trông như báo cáo chọn lọc. | 20 phút |
| **5** | **Thêm một câu về `gate4`** vào §3.3 bài báo | Nhóm đang giấu kết quả trung thực mạnh nhất mình có (quy tắc chỉ định trước, sống sót Holm). Phản biện sẽ hỏi. | 10 phút |
| **6** | **Sửa 2 KTC dải lọc trong `survey/facts_phase4.json`** | Nguồn sự thật sai thì mọi vòng sau kế thừa cái sai. | 5 phút |
| **7** | **Rà nốt 12 câu hỏi–trả lời và văn phong lời thoại trong `KICH_BAN_TRINH_BAY.md`** | Chưa xong trong ngân sách vòng này. Phần số liệu đã sạch; còn lại là nói quá và giọng văn. | 40 phút |
| **8** | **Thống nhất KTC giữa demo và bài báo** (`-1,27 [-3,07;+0,25]` vs `[-3,08;+0,27]`) | Hai artefact công khai nói hai số. | 15 phút |
| **9** | **Sửa 12 chỗ còn lại trong đề cương** (mẫu số 75, "65 bản", "chạy 75", "8 kiến trúc", "53 test", "lưỡng cực") | Ít rủi ro hơn #3 nhưng phải xong trước khi nộp Euréka. | 1,5 giờ |
| **10** | **Dựng bài báo bằng `cinc.cls` chính thức** và kiểm lại số trang | Chỉ cần thiết khi thực sự nộp CinC 2027 (~4/2027). | 1 giờ |
| **11** | Sửa lỗi in r01 hai lần trong `run_check.py` | Thẩm mỹ. | 10 phút |

---

## ĐÁNH GIÁ TỔNG THỂ

Đây là vòng đầu tiên tôi **không tìm được một con số bịa nào** trong các sản phẩm được giao. Tôi cố tình kiểm 25 con số thay vì 15, và tự viết lại từ đầu phép tính mà P1 tự khai là "không có JSON riêng" — nó khớp tuyệt đối. Bài báo tự nêu dấu âm của chính mình trong tóm tắt (−1,27), tự gọi quy tắc chỉ định trước của mình là *"a failed confirmatory test"*, tự gọi thiết kế trọng tài của mình là *"a design error on our part"*, và từ chối kết luận "thiếu tín hiệu" vì phép thử có âm tính giả 18 %. Giao diện demo tự in dòng "mọi con số trên 75 bản đã bị rút". Đó là hành vi của một nhóm đã học được bài học, không phải của một nhóm đang che.

Hai lỗi thật trong bài báo đều nhỏ và sửa trong 20 phút. Nhưng **trọng tâm rủi ro đã dịch chỗ**: nó không còn nằm ở ba sản phẩm mới, mà ở **những tệp không ai được giao** — đề cương LaTeX còn 15 chỗ nói 75 bản như sự thật, và bản DOCX trong `docs/` đang khẳng định đúng con số mà nhóm đã công khai rút. Nếu buổi gặp giảng viên diễn ra hôm nay và giảng viên mở file Word, toàn bộ công sức của vòng 7 và vòng 8 sẽ vô hiệu trong ba mươi giây. **Việc #1 và #3 quan trọng hơn mọi việc còn lại cộng lại.**

Về đích đến, tôi khuyên nhóm nói thẳng một điều với giảng viên: **A\* không có cửa và không nên nằm trong bảng mục tiêu** — không tồn tại hội nghị A\* đúng chủ đề, CinC không phải A\*. Đích thật là Physiological Measurement (Q2, ~58 %) và Euréka 2027 (~62 %). Và chủ nhiệm cần **xác minh hội đồng Euréka chấm theo Scimago hay WoS-JCR trước khi quyết**, vì PM là Q2 theo Scimago — đó là câu hỏi có thể đổi cả chiến lược công bố, và hiện chưa ai trả lời.
