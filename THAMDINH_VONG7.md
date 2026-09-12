# THẨM ĐỊNH VÒNG 7 — phản biện độc lập các sản phẩm R1 / R2 / R4 / R5 / R6

Ngày: 2026-09-12. Người thẩm định: tác tử V2 (độc lập với R1–R6). Nhiệm vụ: **tìm chỗ sai**.
Quy ước: **[F]** = tôi đã tự kiểm (mở tệp, chạy lệnh, truy cập web); **[S]** = suy luận của tôi; **[X]** = không kiểm được.
Mọi con số dưới đây truy về tệp trên đĩa hoặc URL ghi kèm. Tôi không huấn luyện, không suy luận mô hình mới; chỉ chạy
`pytest demo/test_core.py`, `demo/run_check.py --only ...` (tệp kết quả tạm đã xoá) và hai đoạn Python tính lại số của R2.

---

## 0. Kết luận một đoạn

Bốn đính chính của vòng 7 (rò rỉ đã được y văn ghi nhận; không có bộ thứ ba có nhãn; gate vẫn đứng đầu trên logit; phép thử
nhìn thấy có âm tính giả 18 %) **đều đứng vững** khi tôi kiểm lại nguồn và tính lại số. Sai sót nằm ở **các sản phẩm truyền
thông (R4/R5/R6) chưa được cập nhật theo bốn đính chính đó**, cộng thêm **ba loại số đã rút còn lọt**: (i) cổng từ chối
"AUROC 0,980 / giữ 66,7 % / loại 15/16" là số trên **75 bản CinC nhiễm** (`analysis/gate22_cinc.json`, `n_records = 75`)
nhưng đang được dùng làm một trong ba con số chính của Euréka, tờ tóm tắt, kịch bản và cả abstract R6; (ii) "+1,20 logit trên
19 chủ thể dễ, p = 0,0012" xuất phát từ phân tích "lưỡng cực" đã rút (`analysis/LUONGCUC.md`) và được gán nguồn sai; (iii) bản
nháp CinC 4 trang (`paper/cinc2026/main.tex`, in ra `docs/CinC2026_RelyFetal.pdf` để mang đi gặp GVHD) còn nguyên 79,40 /
71,21 / 59,15 / 69,31 / "all 75 records", và **CinC 2026 đã diễn ra 20–23/9/2026 với hạn abstract 15/4/2026** nên "nộp CinC 2026"
là bất khả thi. R3 (dọn repo) **chưa có sản phẩm** (`DON_REPO_VONG7.md` không tồn tại). Xác suất sau vòng này: Q1 ≈ 15–20 %
trong 6 tháng (≈ 35 % trong 12 tháng nếu tự tạo được bộ có nhãn), A\* < 2 %, Euréka 2026 ≈ 0–5 %, Euréka 2027 vào bán kết ≈ 50 %,
có giải ≈ 20 %.

---

## VIỆC 1 — R1: truy cập lại từng nguồn

| Nguồn | Tôi kiểm thế nào | Kết quả |
|---|---|---|
| Silva et al. CinC 2013;40:149–152 | Tải PDF `cinc.org/archives/2013/pdf/0149.pdf`, trích văn bản bằng pypdf **[F]** | Bảng 1 nguyên văn: "Abdominal and Direct FECG [1] 25 / Artificially Generated FECGs [2] 20 / Non-Invasive FECG [3] 14 / Ukraine Non-Invasive FECG 340 / Private Scalp FECG Database 48"; [1] = Matonia 2006; "447 records ... five data collections"; "Training set A contains 75 records". **Trích dẫn của R1 đúng nguyên văn.** |
| Clifford et al. Physiol Meas 2014;35:1521 | DOI 10.1088/0967-3334/35/8/1521 qua api.crossref.org **[F]**; toàn văn IOP đóng, dùng bản cục bộ `papers/p20_text.txt` dòng 149 **[F]** | Câu "The authors also used the MIT Abdominal and Direct Fetal Electrocardiogram Database in order to train their algorithm, which may have led to a bias in the results as this database was included in set-a, set-b (and possibly a few records in set-c)" **có thật**, đúng ngữ cảnh Rodrigues 2014. Bảng 2 "ADFECGDB (Matonia et al., 2006) \| 25" có ở dòng 82. |
| PhysioNet challenge-2013 | WebFetch **[F]** | Không nhắc ADFECGDB; 25 + 50 bản set A; set B/C giữ nhãn. Khớp R1. |
| PhysioNet adfecgdb | WebFetch **[F]** | 5 bản, 5 phút, 1 kHz, không nhắc Challenge. Khớp R1. |
| Su & Wu 2017 | WebFetch Frontiers **[F]** | "Among 447 records, 25 records are from the adfecgdb, so there might be overlapping between the CinC2013 and adfecgdb databases." Đúng nguyên văn. |
| Matonia 2020 Sci Data | pypdf `papers/p21_*.pdf` **[F]** | "...resampled to 1 kHz. In 2013, those signals were part of the research material in the 'Noninvasive Fetal ECG: the PhysioNet/Computing in Cardiology Challenge'". Đúng. |
| `de_cuong_latex/tables/bang_baihoc.tex` dòng p20 | grep **[F]** | Có câu "...phải ghi rõ cảnh báo trong bài kèm trích dẫn chính câu của Clifford về trường hợp Rodrigues" và ở p13 "Việc phải làm ngay là kiểm tra chồng lấn giữa ADFECGDB ... và CinC 2013 set-a". **Lưu ý nhỏ:** ghi chú *nhắc đến* câu Clifford, không *trích nguyên văn*; R1 viết "câu của Clifford đã nằm trong chính ghi chú" là hơi quá — phát biểu đúng là "ghi chú đọc bài của nhóm đã biết cảnh báo này và đã tự đề nghị kiểm chồng lấn từ trước". Kết luận "nhóm bỏ sót cảnh báo đã biết" **vẫn đúng và còn nặng hơn**: nhóm đã tự đề nghị kiểm (p13, p20) rồi viết "chưa tìm" ở DULIEU.md mục 12. |
| DOI bảng "bài bị nhiễm" | Crossref 8 DOI **[F]** | Castillo 2018 PLOS ONE 13:e0199308 ✓; Mohebbian 2022 JBHI 26:515–526 ✓; Chen 2025 Sensors 25:601 ✓; Rodrigues 2014 PM 35:1699–1711 ✓; Clifford 2014 ✓; Su & Wu ✓; Matonia 2020 ✓; DPSS TBME 70:283–295 ✓. Tất cả phân giải đúng tên bài, tạp chí, tập, trang. |
| Castillo 2018 "28/64 tín hiệu, 12/26 bản" | pypdf `papers/p17_*.pdf` **[F]** | Câu "The Abdominal and Direct Fetal Electrocardiogram Database, which was used to train the clustering-based stage, was also used to train the complete method" **có thật** → "bị nhiễm" đứng vững. Con số 28/64 và 12/26 tôi **không tái lập** được bằng pypdf (bảng không trích được theo cụm); R1 đã tự khai đếm bằng pdftotext và yêu cầu kiểm bằng mắt. **Giữ cảnh báo đó.** |

**Phán xử VIỆC 1:** Kết luận (B) ở mức bộ dữ liệu / (A) ở mức bản ghi **đúng và có nguồn**. Mọi trích dẫn tôi kiểm đều có thật.
Phát biểu chuẩn "Như ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014]... chúng tôi xác định bằng đo lường đúng 15 bản ghi
nào" là phát biểu duy nhất được phép. Hai điểm R1 tự khai chưa xác minh (Baldazzi & Pani; Ghonchi; RCED-Net) phải giữ nguyên
nhãn "chưa xác minh". **[S]** Với Mohebbian 2022, vì bài có hai phát biểu mâu thuẫn về huấn luyện, nên hạ xuống "khả năng bị
nhiễm" thay vì "bị nhiễm chắc chắn" khi in vào bài.

---

## VIỆC 2 — R2: khai báo trước, bộ thứ ba, logit, âm tính giả

**Thứ tự thời gian [F]:** `git log` — ed819e3 "R2: pre-declare replication" lúc **16:25:47 +07**, chỉ thêm
`analysis/xacnhan_khaibao.md` (77 dòng). mtime: `xacnhan.py` 16:29:19, `xacnhan_results.json` 16:30:25. **Khai báo có trước
kết quả 5 phút.** Tuy nhiên tệp khai báo tự ghi ở mục 0 rằng đã nhìn thấy xếp hạng F1 thô của 22 chủ thể và 60 bản trước khi
khai báo — tức đây là *khai báo trước cho phép tính lại*, không phải khai báo trước cho giả thuyết; R2 đã tự nhận "đây cũng
là phép thử hậu kiểm". Đúng mực. Không được gọi là "tiền đăng ký".

**Bộ thứ ba [F]:**
- NIFEADB: `model/data/nifeadb/` có đúng 26 `.dat` + 26 `.hea` + 1 json, **không** `.qrs/.atr`; `nifeadb_loader.py:72
  HAS_FETAL_ANNOTATIONS = False`; trang PhysioNet không nhắc tệp chú thích. Khớp.
- NInFEA: `model/data/ninfea/wfdb_format_ecg_and_respiration/` 2 `.dat` + 3 `.hea`; trang PhysioNet: tham chiếu chỉ là
  Doppler xung (PWD), "no beat-by-beat fetal QRS annotation"; 39 sản phụ / 60 bản. Khớp.
- nifecgdb `ecgca102.edf.qrs`: tôi đọc bằng wfdb → **375 nhãn 'N', RR trung vị 0,695 s = 86,3 nhịp/phút, 269 s** — nhịp mẹ.
  Trang PhysioNet không nói .qrs là gì; Behar (luận án, dòng 2160) ghi phải "manual annotation of each individual FQRS" cho
  bộ này → không có nhãn thai công khai. Suy luận của R2 là hợp lý và được ghi đúng là suy luận.
- CinC set-b: nhãn không công bố (trang PhysioNet: "reference annotations withheld"). Khớp.
→ **Kết luận "không có bộ thứ ba có nhãn fQRS thật trong tầm tay" đứng vững.** Hệ quả trực tiếp: kế hoạch "chạy peakprob một
lần trên set-b hoặc NInFEA" trong TOM_TAT, KICH_BAN, EUREKA, CHIEN_LUOC **không thực hiện được như đã viết**.

**Tính lại độc lập từ `chonkenh_results.json` + `chonkenh_cache/s22_*.json` [F]** (bootstrap 10 000, seed 0, mã riêng của tôi):

| Kẹp A | gate | rrcv | peakprob |
|---|---|---|---|
| R2 | +0,225 [+0,004; +0,589] | +0,140 [−0,188; +0,547] | +0,134 [−0,038; +0,407] |
| Tôi | +0,225 [+0,004; +0,581] | +0,140 [−0,191; +0,535] | +0,134 [−0,037; +0,399] |

Kẹp B, C cũng khớp đến 3 chữ số (kẹp C: rrcv +0,223 đứng đầu, gate +0,208, peakprob +0,148). Xếp hạng A/B gate đầu, C rrcv
đầu, peakprob hạng 3/4/6 — **đúng như R2**. Điều kiện "vấn đề hậu kiểm biến mất" không thoả.

**Âm tính giả [F]:** tính lại từ `chandoan_events.npz` + `chandoan_raw.json` (kênh PSD, 60 bản sạch, ghép ±50 ms tham lam):
n_TP = 6 365, bị gán "không thấy" = 1 144 → **17,97 % [12,1; 25,0]**, trung vị theo bản 20,9 %, 31/60 bản > 10 %. **Khớp R2
hoàn toàn.** Định nghĩa: âm tính giả = nhịp mô hình bắt đúng (TP) mà z < τ. Đây là 1 − độ nhạy đo trên TP, **không phải độ
đặc hiệu** (độ đặc hiệu 95 % tại vị trí an toàn là theo định nghĩa, trong mẫu); R2 gọi đúng tên trong XACNHAN.md, còn đề bài
gọi nhầm là "độ đặc hiệu". R2 tự khai độ nhạy trên TP là ước lượng lạc quan — đúng.

**Hiệu chỉnh 86 % → 26 % [S]:** R2 nói đúng rằng v′ = (v − 0,05)/(s − 0,05) không định danh được khi s gần 0,05. Tôi đồng ý
kết luận "không xác định được" là kết luận trung thực duy nhất; **không được** in "26 %" như con số thay thế.

**Seed [F]:** `model/train_22_seed1.json` tồn tại, không có checkpoint seed 1; hiệu +0,03 [−0,18; +0,34]. Khớp.

**Phán xử VIỆC 2: DÙNG ĐƯỢC NGAY** (XACNHAN.md, xacnhan_results.json). Hai điều kiện khi trích: không gọi "tiền đăng ký"; không in
"26 %" như số thay thế.

---

## VIỆC 3 — R6: quartile, Q1/A\*, kế hoạch 3 tháng

**Quartile [F, qua trang tổng hợp; scimagojr.com trả 403 cả với tôi]:**

| Tạp chí | R6 ghi | Tôi kiểm (WebSearch, 2024) |
|---|---|---|
| Physiological Measurement | Q2 (Physiology) / Q3 (BME), SJR 0,595 | "best quartile Q2 (2024), SJR 0,595, IF 3,04" ✓ |
| IEEE JBHI | Q1, SJR 1,62 | Q1 (CS Applications, EE, Health Info), SJR 1,624 ✓ |
| IEEE TBME | Q1, SJR 1,11 | Q1 (2024), SJR 1,113 ✓ |
| BSPC | Q1, SJR 1,23 | Q1 (2024), SJR 1,229 ✓ |
| CBM | Q1, SJR 1,38 | Q1, SJR 1,375 ✓ |

Đánh giá "PM không phải Q1" **có căn cứ**. Thứ hạng cụ thể (25/73, 51/89) tôi không kiểm được **[X]**.

**Q1/A\* có căn cứ không? [S]** Lập luận A\* < 2 % là hợp lý (không tính mới ML, quy mô nhỏ, CinC/EMBC không CORE A\*). Ước
lượng Q1 ≈ 50 % "sau ba việc" **không còn đứng** vì R2 đã cho thấy: việc 1 (bộ thứ ba có nhãn) **không có trong tầm tay**;
việc 2 (đo độ đặc hiệu/nhạy phép thử) **đã làm và cho kết quả xấu** (18 %), kéo sập trụ "thiếu tín hiệu thật"; việc 3 (3 seed)
cần huấn luyện lại 11 fold × 2 seed — khả thi với một sinh viên trên CPU chỉ nếu mỗi lần huấn luyện tính bằng giờ (chưa có số
thời gian huấn luyện trong repo để tôi kiểm **[X]**). R6 tự ghi hạn chế 4 và 5 (chưa kiểm nhãn bộ thứ ba, chưa rà văn liệu) —
cả hai đã được R1/R2 trả lời theo hướng bất lợi. **R6 viết trước R1/R2 nên cần cập nhật**, không phải sai.

**Abstract R6 (CHIEN_LUOC dòng 170) [F]:** không có từ cấm ("novel/SOTA/first/pre-registered"). Nhưng chứa ba câu **phải
sửa**: (a) "We first show that 15 of the 75 challenge records are verbatim copies" → theo R1 phải là "As documented by the
organisers..., we identify by measurement which 15 records..."; (b) "error analysis with chance-level controls attributes the
remaining gap to missing fetal signal rather than distribution shift" → đã rút theo R2 (chỉ còn bằng chứng thích nghi miền
thất bại); (c) "record-level AUROC 0.98 at 67% coverage" → số trên 75 bản nhiễm (xem VIỆC 6).

**Kế hoạch 3 tháng với một sinh viên [S]:** Không khả thi như viết: trục JBHI phụ thuộc bộ thứ ba không tồn tại. Đường khả thi
duy nhất là (i) tự tạo bộ có nhãn (chú thích tay 10–20 bản NIFEADB/nifecgdb có chuyên gia kiểm — cần bác sĩ, chưa có), hoặc
(ii) hạ mục tiêu xuống PM/CinC 2027 với peakprob ghi rõ là giả thuyết. R6 đã có nhánh dự phòng PM — nhánh này là nhánh chính.

**Phán xử VIỆC 3: DÙNG ĐƯỢC VỚI ĐIỀU KIỆN** — cập nhật mục 1 (#1 hạ từ "phát hiện" xuống "định lượng hậu quả"; #4 "+1,20 logit
19 chủ thể" xuất xứ từ phân tích lưỡng cực đã rút), sửa abstract ba chỗ, đổi ước lượng Q1.

---

## VIỆC 4 — R4: demo

- `python -m pytest demo/test_core.py -q` → **17 passed in 17,09 s** **[F]** (HUONG_DAN ghi "17 kiểm thử ≈ 15 s" — đúng).
- `python demo/run_check.py --only r01,a09,B2_03,a02,a27 --out thamdinh7_check --threads 2` → chạy 0,6 phút, bảng in ra khớp
  mục 6 HUONG_DAN đến từng chữ số: r01 99,92/100,00/99,84 CAO 0,999; a09 94,25 CAO 0,914; B2_03 83,91 THẤP 0,401 (luật CAO
  0,834 — sai, đúng như tài liệu nói); a02 24,91 THẤP 0,544 bám mẹ 0,78; a27 32,94 THẤP 0,173 **[F]**. Tệp kết quả tạm đã xoá.
- **Bản minh hoạ có bản rò rỉ không?** r01 (ADFECGDB, fold không chứa r01), a09, a02, a27 (đều không thuộc 15 bản rò rỉ), B2_03
  (Silesia). **Không.** `demo/run_check.py` loại 15 bản mặc định (`CINC_LEAK`, `--include-leak` để chạy đối chiếu); `app.py`
  gắn cờ "⚠ RÒ RỈ = r0x" và cảnh báo trong kết quả. Tab tổng hợp đọc `chon_kenh_60_sach` từ JSON, không ghi cứng **[F]**.
- **Số đã rút trong demo?** `demo/app.py`, `demo/core.py`: không. **`demo/README.md` dòng 228** (đã commit 11/9): "F1 lưỡng cực
  (4/10 = 100, 5/10 < 45, còn lại a01 = 59)" — số mẫu 10 bản đã rút + chữ "lưỡng cực" → **sót**.
- **Lệnh trong HUONG_DAN chạy được?** pytest ✓, run_check ✓, `python demo/app.py` **[X]** không chạy (không mở server trong phiên
  này); `smoke_app.py` kết quả cũ có trên đĩa.
- **Ảnh chụp [F]:** HUONG_DAN mục 5 liệt kê 12 ảnh `01…12`; trên đĩa chỉ có **5 ảnh mới** (01_r01_tong_quan, 02_r01_the_so,
  03_r01_so_sanh, 04_a09_chon_kenh, 05_a09_the_so) + 5 ảnh cũ ngày 10/9 tên khác. `screenshots.json`: `"ok": false`, lỗi
  `TimeoutError: Locator.click`, a09 `wall_s 187,8 s`. → Kế hoạch dự phòng "mở ảnh 06–12" cho bản B2_03/a02/a27 **không dùng
  được**. Phải chạy lại `screenshot.py` hoặc chụp tay.
- **HUONG_DAN dòng 172** (lời kết): "khoảng cách đó là **thiếu tín hiệu thật**, không phải dịch chuyển thống kê" — theo R2, phép
  thử nhìn thấy không còn chống đỡ được; chỉ còn "4 phương pháp thích nghi miền thất bại". Phải hạ giọng: *"chúng tôi chưa
  xác định được phần nào của khoảng cách là do thiếu tín hiệu; phép thử nhìn thấy có âm tính giả 18 %"*.
- Dòng 148 "Cổng 22 ca AUROC 0,934" truy về `gate22_results.json` (22 chủ thể) — hợp lệ.

**Phán xử VIỆC 4: DÙNG ĐƯỢC VỚI ĐIỀU KIỆN** — sửa dòng 172, bỏ/chụp lại ảnh 06–12, sửa `demo/README.md:228`, commit.

---

## VIỆC 5 — R5: Euréka, kịch bản, tóm tắt

**Nguồn Euréka [F]:** khoahoctre.com.vn/eureka-2026: "Từ ngày 01/9/2026 đến hết ngày 25/9/2026", 15 lĩnh vực, > 500 triệu ✓.
Tiêu chí 30/50/20 (10+20 / 30+20 / 10+10) khớp trang tiêu chí 2023 ✓. FTU hạn nội bộ 17g00 04/9/2026 ✓. **Hạn nội bộ TDTU:**
tôi tìm `science.tdtu.edu.vn/nghien-cuu/nghien-cuu-khoa-hoc-sinh-vien` (chỉ có kỳ 27/2025), WebSearch "TDTU Euréka lần thứ
28" → **không có thông báo công khai**. R5 ghi "chưa xác minh, khả năng đã qua" là đúng mực; tôi không tìm thêm được gì. CinC
2026: cinc2026.org "20th–23rd September 2026, Madrid", "Deadline April 15, 2026" **[F]**.

**Số đã rút / từ cấm / giọng trong 3 tài liệu [F]:**

| Tệp:dòng | Vấn đề | Loại |
|---|---|---|
| EUREKA.md:87, :135; TOM_TAT:19; KICH_BAN:56, :113 (câu 1) | "AUROC 0,980; giữ 66,7 % loại 15/16 bản F1 < 50" — `gate22_cinc.json` ghi `n_records: 75`, "ap len 75 ban ghi CinC 2013 set-a" | **số CinC 75 bản đã rút**; chưa có bản 60 sạch |
| EUREKA.md:87; TOM_TAT:23; KICH_BAN:93; CHIEN_LUOC:25 | "+1,20 logit trên 19 chủ thể dễ, p = 0,0012" — nguồn thật là `analysis/LUONGCUC.md:163–173` (phân tích "lưỡng cực" đã rút; nhóm 19 định nghĩa sau khi thấy F1). EUREKA/CHIEN_LUOC gán nguồn `powermf_fair_stats.json` — tệp này **không chứa** số đó | số từ phân tích đã rút + gán nguồn sai; TOM_TAT còn chữ "hai cực" |
| KICH_BAN:16 | "Physiological Measurement (Q1 theo hiểu biết của em)" | sai (Q2); mâu thuẫn CHIEN_LUOC |
| KICH_BAN:16, :149; TOM_TAT:30, :32; EUREKA:104 (gián tiếp) | "Nộp CinC 2026 (bản 4 trang đã có)" | bất khả thi — hạn 15/4/2026 đã qua, hội nghị 20–23/9/2026 |
| KICH_BAN:78 "em phát hiện bộ kiểm tra bị nhiễm"; :125 "em phát hiện 15 bản"; EUREKA:87 "phát hiện 15/75 bản", :92 "tự phát hiện rò rỉ"; CHIEN_LUOC:10, :22 "phát hiện về dữ liệu" | cụm "phát hiện rò rỉ" | cấm theo đính chính 1 |
| KICH_BAN:132 (câu 7) "em chưa kiểm từng bài" | R1 đã rà 20 bài → cập nhật: "4 bài chắc chắn, 2 nghi ngờ" và nói "ban tổ chức đã ghi nhận từ 2014" | lỗi thời |
| KICH_BAN:95, TOM_TAT:30 "chạy peakprob trên CinC set-b hoặc NInFEA"; :95 "tính lại 22 chủ thể trên logit" | set-b không nhãn, NInFEA không nhãn (R2); logit đã tính và **gate thắng** — kịch bản chưa biết kết quả | lỗi thời; nếu nói trước GVHD sẽ bị hỏi "kết quả thế nào?" |
| KICH_BAN:32 "20.361 dòng mã, 53/53 kiểm thử"; EUREKA:74 "20.400 dòng, 53 kiểm thử"; TOM_TAT:9 | Tôi đếm: 131 tệp .py theo dõi = 27 689 dòng; hàm test = 39 (`tests/`) + 17 (`demo/`) = 56 | không truy nguồn được; sai số nhỏ nhưng vi phạm "mọi số truy về tệp" |
| TOM_TAT:16, EUREKA:87 "89,5 % [81,4; 103,2]" | 10,85/12,12 = 0,895 tính được từ `powermf_fair_stats.json` (`rely_vs_pmf1.hieu = 10,847`, `rely_vs_pmf4.hieu = −1,274`); **KTC [81,4; 103,2] không có trong tệp nào** tôi tìm (`powermf_fair_stats.json`, `stats_results.json`) | KTC chưa truy nguồn được |
| EUREKA:92, :113 "(+6,20 → +7,73)" | dùng số đã rút để kể chuyện | chấp nhận nếu ghi "đã rút", **không** nói trước hội đồng |
| KICH_BAN:181 "in `docs/CinC2026_RelyFetal.pdf`" | PDF từ `paper/cinc2026/main.tex` (commit 09:49 12/9) còn 79,40 / 71,21 / 59,15 / 69,31 / 62,82 / "all 75 records" (dòng 70, 255, 262, 265, 271, 289, 399) | **mang số đã rút đến buổi gặp** |
| KICH_BAN:5, :178 | sổ tay `bao_cao_de_tai.html` "trong scratchpad" — không có trên đĩa repo | tệp tham chiếu không tồn tại |

**Giọng AI?** Kịch bản viết giọng sinh viên, không lộ; nhưng câu "công cụ tự động đối chiếu 89 con số" (KICH_BAN:88) thành thật.
Hai điểm rút lui và quy tắc "em nghĩ... nhưng chưa đo" tốt. **12 câu trả lời:** câu 1, 3, 7, 11, 12 cần sửa theo bảng trên; câu
4, 5, 6, 8, 9, 10 đúng mực và truy nguồn được.

**Phán xử VIỆC 5:** EUREKA.md — **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN** (phần thể lệ/mốc thời gian tốt; bảng đối chiếu mục 2 phải bỏ AUROC 0,980,
+1,20 logit, "phát hiện"). KICH_BAN_TRINH_BAY.md và TOM_TAT_1_TRANG.md — **CẦN LÀM LẠI** (5 và 4 chỗ lỗi thời/sai như bảng;
chưa phản ánh bốn đính chính vòng 7).

---

## VIỆC 6 — grep toàn repo, git, tệp nhạy cảm

- **R3 chưa xong [F]:** `DON_REPO_VONG7.md` không tồn tại ở gốc hay `docs/`. Không có commit nào sau ed819e3 (16:25). `git diff
  --stat`: 10 tệp sửa chưa commit (+21 745 / −10 139 dòng, chủ yếu JSON demo); > 20 tệp mới chưa theo dõi (toàn bộ sản phẩm
  R1/R2/R4/R5/R6). **Mọi sản phẩm vòng 7 hiện chưa được neo git.**
- **Số đã rút còn sót ngoài bảng "đã rút" [F]** (loại trừ các dòng tự ghi "đã rút"): `paper/cinc2026/main.tex` (7 chỗ, nêu trên);
  `demo/README.md:228`; `analysis/CHONKENH.md` (79,40 / 85,60 / +6,20 / 86,87 — tài liệu vòng cũ, chưa có dòng đầu cảnh báo);
  `analysis/CHANDOAN_MOHINH.md:106–109, 260–265` (79,40 / 85,60 / 86,87 / "71 %"); `analysis/ABLATION_B1.md:62–105` (71,21 / 79,40
  / 86,87); `analysis/CLINICAL.md:223–226` (69,31; 79,40); `adapt/*.py`, `adapt_log.txt` (mốc 79,40 / 85,60 trong mã và log);
  README.md chỉ có trong bảng rút — ổn. Từ cấm: `baselines/powermf_run.py:5`, `powermf_table.py:76` ("SOTA" trong mã/bảng);
  `analysis/CHANDOAN_MOHINH.md`, `DULIEU.md`, `THICHNGHI.md`, `adapt/*.py` còn "tiền đăng ký" nhiều chỗ; `analysis/LUONGCUC.md`
  còn nguyên khung "lưỡng cực"; `analysis/XACNHAN.md:129` nhắc "mô hình không phải nút thắt" đúng ngữ cảnh rút. **Đề nghị tối
  thiểu:** thêm một dòng đầu "TÀI LIỆU VÒNG CŨ — số CinC 75 bản đã rút, xem DULIEU.md/XACNHAN.md" vào CHONKENH.md,
  CHANDOAN_MOHINH.md, ABLATION_B1.md, CLINICAL.md, LUONGCUC.md; thay "tiền đăng ký" bằng "khai báo trước (không neo git)".
- **Tệp nhạy cảm [F]:** `.gitignore` loại `model/data/`, `papers/`, `tools/` (Octave portable, fecg-benchmarking, varanini),
  `goi-danh-gia-doi-chuan-dpss/`, `*.edf/*.dat/*.hea` → `git status --ignored` xác nhận cả bốn bị bỏ qua. `baselines/octave/
  run_powermf.m` là driver do nhóm viết (đầu tệp tự khai), `PowerMF.m` của tác giả **không** được theo dõi. Git theo dõi 21 tệp
  `.pt/.pkl` (checkpoint, cổng GBM) — không nhạy cảm, chỉ nặng. Không thấy tệp khoá/secret.

---

## VIỆC 7 — PHÁN XỬ TỪNG SẢN PHẨM

| Sản phẩm | Phán xử | Điều kiện / lý do |
|---|---|---|
| `survey/RO_RI_VANLIEU.md` + `.json` (R1) | **DÙNG ĐƯỢC NGAY** | Sửa một câu: ghi chú p20 *nhắc đến* chứ không *trích* Clifford. Giữ nhãn "chưa xác minh" cho Baldazzi/Ghonchi/RCED-Net; kiểm bằng mắt 28/64 Castillo trước khi in. |
| `analysis/XACNHAN.md` + `xacnhan_results.json` (R2) | **DÙNG ĐƯỢC NGAY** | Số tái lập độc lập 100 %. Không gọi "tiền đăng ký"; không in "26 %" như số thay thế. |
| `docs/CHIEN_LUOC_CONG_BO.md` (R6) | **VỚI ĐIỀU KIỆN** | Cập nhật theo R1/R2: #1 → "định lượng hậu quả"; #4 gắn xuất xứ LUONGCUC; abstract sửa 3 câu; Q1 ước lượng lại; trục JBHI chuyển thành dự phòng, PM/CinC 2027 thành chính. |
| `docs/HUONG_DAN_DEMO.md` + `demo/` (R4) | **VỚI ĐIỀU KIỆN** | Dòng 172 hạ giọng; ảnh 06–12 chưa có (screenshot.py ok=false); `demo/README.md:228`; commit 10 tệp đang sửa. |
| `docs/EUREKA.md` (R5) | **VỚI ĐIỀU KIỆN** | Bỏ AUROC 0,980 (75 bản), +1,20 logit (lưỡng cực), "phát hiện"; số dòng mã/kiểm thử truy nguồn hoặc bỏ. |
| `docs/KICH_BAN_TRINH_BAY.md` (R5) | **CẦN LÀM LẠI** | "PM là Q1", "nộp CinC 2026", "em phát hiện", set-b/NInFEA có nhãn, logit chưa tính, AUROC 0,980, sổ tay không tồn tại, PDF CinC mang số đã rút. |
| `docs/TOM_TAT_1_TRANG.md` (R5) | **CẦN LÀM LẠI** | AUROC 0,980; +1,20/"hai cực"; CinC 2026; kế hoạch set-b/NInFEA; KTC 89,5 % chưa truy nguồn. |
| `paper/cinc2026/main.tex` / `docs/CinC2026_RelyFetal.pdf` | **PHẢI BỎ** (ở trạng thái hiện tại) | Toàn số 75 bản; hội nghị đã qua. Viết lại cho CinC 2027 trên 60 bản sạch. |
| R3 (dọn repo) | **CHƯA CÓ SẢN PHẨM** | `DON_REPO_VONG7.md` không tồn tại; chưa commit. |

**Xác suất — căn cứ [S]:**
- **Q1 (Scimago) ≈ 15–20 % trong 6 tháng; ≈ 35 % trong 12 tháng.** Điều kiện Q1 mà R6 đặt (bộ thứ ba có nhãn) không tồn tại
  trong tầm tay (R2); peakprob vẫn hậu kiểm và gate thắng trên logit trong miền; 1 seed; trụ "thiếu tín hiệu thật" mất phép
  thử. Con đường 12 tháng chỉ mở nếu tự chú thích được một bộ có chuyên gia hoặc có trung tâm ghi thứ hai.
- **Q2 (Physiological Measurement) ≈ 55–65 %** nếu viết đúng trục "kiểm toán + cổng từ chối" và mọi số trên 60 bản sạch.
- **A\* < 2 %.** Không có venue A\* trong lĩnh vực; nội dung không có tính mới ML.
- **Euréka 2026 (lần 28) ≈ 0–5 %:** cổng cấp thành đóng 25/9/2026, chỉ trường nộp; hạn nội bộ TDTU không tìm thấy công khai;
  chưa có phiếu hội đồng cấp trường; toàn văn 140 trang có tên tác giả.
- **Euréka 2027 (lần 29): vào bán kết ≈ 50 %, có giải (Khuyến khích trở lên) ≈ 20 %, giải Nhất ≈ 5 %.** Nội dung nhóm 2 (50 điểm)
  mạnh hơn mặt bằng; nhóm 1b "tính mới" yếu sau khi rò rỉ không còn là phát hiện; chưa có bác sĩ đồng hành.

---

## Hạn chế của thẩm định này

1. Không mở được toàn văn IOP của Clifford 2014 và Rodrigues 2014; dựa vào bản cục bộ `papers/p20_text.txt` và Crossref.
2. Không kiểm bằng mắt bảng Castillo 2018 (28/64); không kiểm thứ hạng Scimago cụ thể (25/73, 51/89); scimagojr.com trả 403.
3. Không chạy `demo/app.py` (server Gradio) và không tái tạo ảnh chụp.
4. Không huấn luyện lại; chưa biết thời gian một lần huấn luyện để đánh giá tính khả thi "3 seed".
5. Xác suất là ước lượng chủ quan, không có số liệu tỉ lệ nhận của tạp chí.
6. Grep số đã rút dùng biểu thức số; có thể sót dạng viết khác (ví dụ "79.4" không có số 0).
