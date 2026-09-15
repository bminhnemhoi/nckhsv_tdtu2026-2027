# THẨM ĐỊNH VÒNG 9 — PHẢN BIỆN ĐỘC LẬP

**Ngày thẩm định:** 13/09/2026 · **Buổi gặp giảng viên:** 14/09/2026
**Phạm vi:** năm sản phẩm vòng 9 (demo/ + 4 tệp docs/)
**Nguyên tắc:** chỉ đọc và chạy, không sửa tệp nào. Mọi con số dưới đây do tôi tự chạy lại hoặc tự truy về tệp JSON gốc.

---

## 0. PHÁN QUYẾT TỔNG THỂ

**Phần mã chạy tốt hơn phần tài liệu.** Demo thật sự chạy: 82/82 kiểm thử qua, smoke ĐẠT, cả hai tab mới hoạt động, thông báo lỗi tiếng Việt tử tế, và tệp ví dụ ra đúng từng con số chủ nhiệm đã đo. Không có từ cấm nào bị dùng như sự thật, không có số đã rút nào bị hồi sinh, không bản nhiễm nào bị dùng sai.

**Nhưng có ba lỗi có thể làm vỡ buổi gặp**, và cả ba đều nằm ngoài phần mã:

1. **Bảng kết quả chính trong đề cương bị đảo cột** — đọc theo tiêu đề thì `peakprob` *thua 35/60 bản*, trong khi sự thật là *thắng 19, hoà 35, thua 6*. Bảng này mâu thuẫn trực tiếp với slide. Đặt hai tệp cạnh nhau là mất uy tín ngay.
2. **Hai tab mới biến mất ở màn hình 1366 px** — và miếng CSS chủ nhiệm vừa thêm **không hề có tác dụng** (sai selector cho Gradio 6). Chủ nhiệm đang tin là đã sửa xong.
3. **`KICH_BAN_HANH_TRINH.md` chưa hề biết đến vòng 9** — không nhắc hai tab mới lần nào, vẫn nói "6 tab", "4 phút", "60 kiểm thử", trong khi sổ tay demo nói 8 tab, 6–8 phút. Hai tài liệu dẫn cùng một buổi demo theo hai kịch bản khác nhau.

Không sản phẩm nào phải bỏ. Tổng thời gian sửa ước tính **2 giờ 25 phút**, trong đó **50 phút là bắt buộc**.

---

## VIỆC 1 — CHẠY THẬT DEMO

Môi trường: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`, Python 3.12.6, Gradio **6.26.0**, Plotly 7.0.0.

### (a) Kiểm thử — con số THẬT: **82 passed**, 0 hỏng

```
python -m pytest tests/ demo/test_core.py -q
82 passed, 2 warnings in 50.53s     (exit 0)
```

Chủ nhiệm đo 82 → **ĐÚNG**. Phân rã thật: `tests/` = **43**, `demo/test_core.py` = **39**.
(Ghi nhớ cho việc 2: đề cương ghi "60/60 qua (43 + 17)" — sai cả tổng lẫn vế sau.)

Hai cảnh báo đều vô hại: một `StarletteDeprecationWarning` của FastAPI, một `UserWarning: genfromtxt: Empty input file` do chính kiểm thử cố tình nạp tệp rỗng.

### (b) `python demo/smoke_app.py` — **ĐẠT**

```
[1] GET http://127.0.0.1:7861/ -> 200  (khởi động 0.91 s) · 69 thành phần, 7 sự kiện
[2] app.run(r01, tự động) -> kênh 4, F1 = 99.92, đèn = cao, 4.06 s
[4a] Dữ liệu của nhóm: ADFECGDB -> 5 bản ghi; xem thô r01 -> 5 trace, 0.28 s
[4b] Tải dữ liệu mới: vidu_tai_len.csv -> kênh 1, F1 = 98.46, 0.49 s; không nhãn -> KHÔNG có F1 (đúng)
KẾT QUẢ: ĐẠT
```

### (c) Khởi động thật `demo/app.py` — **ĐƯỢC**

Tôi không dùng lại smoke mà tự gọi `build_app()` + `launch()` trên cổng riêng, rồi thao tác bằng hai đường: gọi thẳng hàm xử lý, **và** điều khiển trình duyệt thật (Chromium qua Playwright) ở đúng độ phân giải phòng học.

- Khởi động **0,50 s**, `http://127.0.0.1:7873/` trả 200, trang 182 903 ký tự.
- **Tab "Dữ liệu của nhóm"** — cả **5 bộ** đều nạp được, bảng đúng **9 cột**, nút *Xem tín hiệu thô* vẽ được cho mọi bộ:

| Bộ dữ liệu | Số bản ghi | Xem thô | Trace |
|---|---:|---|---:|
| ADFECGDB — 5 bản (PhysioNet, nhãn da đầu) | 5 | r01 | 5 |
| Silesia B2 — chuyển dạ (12 bản trên đĩa) | 12 | B2_01 | 5 |
| Silesia B1 — thai kỳ (10 bản, nhãn gián tiếp) | 10 | B1_01 | 5 |
| CinC 2013 set-a — 60 bản SẠCH (ngoài miền) | 60 | a01 | 5 |
| CinC 2013 set-a — 15 bản NHIỄM (bản sao ADFECGDB) | 15 | a03 | 5 |

  Mọi ô đọc thật từ `.hea`/`.edf`/`.ecg` trên đĩa (đã đối chiếu dòng đầu mỗi bảng). Bộ 15 bản nhiễm **được gắn nhãn "NHIỄM — bản sao r10; NCC = 1,0000"** ngay trong bảng — đúng cách.
  Bấm *Xem tín hiệu thô* khi chưa chọn bản ghi → `Chưa chọn bản ghi nào — hãy chọn một bản ghi trong danh sách bên trái.` Tử tế.

- **Tab "Tải dữ liệu mới"** — chạy được cả hai nhánh có nhãn và không nhãn (chi tiết ở mục (e)).

### (d) Sáu trường hợp lỗi — **5 tử tế, 1 không phải lỗi**

| # | Trường hợp | Kết quả | Thông báo |
|---|---|---|---|
| 1 | Tệp không tồn tại | `gr.Error`, **không** stack trace, nhưng **lẫn tiếng Anh** | `Không xử lý được tệp tải lên: FileNotFoundError: [Errno 2] No such file or directory: 'C:/…/khong_ton_tai.csv'` |
| 2 | `.dat` thiếu `.hea` | **Tiếng Việt tử tế**, chỉ rõ cách sửa | `Tệp codat.dat là WFDB nhị phân nhưng THIẾU tệp header .hea đi kèm. Hãy chọn CẢ HAI tệp (.dat và .hea) cùng lúc rồi tải lên lại.` |
| 3 | CSV 1 cột | **KHÔNG báo lỗi — và đúng như vậy** | Coi là bản ghi **1 kênh** (mô hình vốn là đơn kênh, tài liệu ghi "mỗi cột một kênh"). Nhiễu ngẫu nhiên → **đèn THẤP**, 0/7 đoạn xanh. Cổng từ chối làm đúng việc. |
| 4 | `fs = 0` | **Tiếng Việt tử tế**, nêu dải hợp lệ | `Tần số lấy mẫu 0 Hz không hợp lý (chấp nhận 50–20000 Hz). Tệp .csv/.npy/.txt KHÔNG tự khai tần số nên bạn phải nhập đúng.` |
| 5 | Tín hiệu 2 giây | **Tiếng Việt tử tế**, nêu ngưỡng và gợi ý nguyên nhân | `Bản ghi chỉ dài 2.00 s — quá ngắn. Cần ít nhất 8 s (mô hình dùng cửa sổ 4 s, trường tiếp nhận 1,516 s). Nếu tệp thực ra dài hơn, hãy kiểm tra lại ô tần số lấy mẫu.` |
| 6 | Tệp rỗng 0 byte | **Tiếng Việt tử tế** | `Tệp rong.csv không chứa kênh tín hiệu nào.` (numpy có in `UserWarning` ra console, **không** lọt lên giao diện) |

**Không trường hợp nào văng stack trace lên giao diện.** Chỉ #1 lộ tên ngoại lệ tiếng Anh và đường dẫn tuyệt đối — nhưng qua giao diện Gradio thật thì tình huống này gần như không xảy ra được (Gradio tự sao tệp trước khi gọi hàm), nên để nguyên cũng được.

**Kiểm thêm — cổng từ chối có bị lừa không?** Tôi nạp nhiễu ngẫu nhiên 4 kênh 60 s và tín hiệu toàn số 0. Cả hai đều ra **đèn THẤP** (0/15 đoạn xanh, 15/15 đỏ). Không có chuyện rác vào mà đèn xanh. Đây là điểm mạnh, nên chủ động nói ra nếu cô hỏi.

### (e) Tệp ví dụ — **khớp chính xác con số chủ nhiệm đo**

| Chỉ số | Chủ nhiệm đo | Tôi đo lại | |
|---|---|---|---|
| Kênh được chọn | 1 | **1** (auto, peakprob) | ✔ |
| F1 | 98,46 | **98,4615** | ✔ |
| Jitter | 2,375 ms | **2,375 ms** | ✔ |
| Đèn | CAO | **cao** (điểm 0,992; 7/7 đoạn xanh) | ✔ |

Se = PPV = 98,46; 65 nhịp; fHR 130,0 bpm. Không nhãn → `F1/Se/PPV = None` và giao diện ghi rõ **"không có nhãn → KHÔNG tính được F1/Se/PPV"**. Đúng.

**Kết quả có hợp lý không — CÓ, và cái bẫy đã được rào đúng chỗ.** Tôi chạy `a09` **đầy đủ 60 s** để so: **F1 = 94,25**, kênh 1, đèn cao. Vậy đoạn trích 30 s **dễ hơn** bản đầy đủ (98,46 so với 94,25) — đúng như cảnh báo. Ba lớp rào đã có sẵn và đều đúng:
- `vidu_tai_len_META.json` ghi `"canh_bao": "KHÔNG phải dữ liệu mới thật — trích từ a09 để thử luồng tải lên."`
- Giao diện tab in hộp cảnh báo "trích từ bản ghi `a09`… KHÔNG phải *dữ liệu mới* thật".
- Có kiểm thử riêng `test_tep_vi_du_dung_la_trich_tu_a09`.
- **Đã grep toàn bộ 4 tệp docs: chuỗi `98,46` / `98.46` xuất hiện 0 lần.** Không ai trích nhầm nó thay cho 94,25.

### (f) CSS thanh tab — **CÓ THẬT TRONG MÃ, NHƯNG KHÔNG CÓ TÁC DỤNG**

CSS có thật (`demo/app.py:770–781`), được nạp vào trang (đã xác nhận chuỗi `flex-wrap` nằm trong HTML phục vụ), và **không làm hỏng gì** — phần `.rf-*` (thẻ số, hộp cảnh báo) vẫn đẹp.

**Nhưng phần thanh tab là vô hiệu.** Đo bằng Chromium thật:

| Bề rộng màn hình | Số tab hiện trên thanh | Hai tab cuối |
|---:|---:|---|
| 1920 px | **8/8** | hiện bình thường |
| **1366 px (phòng học)** | **6/8** | **bị nuốt vào menu tràn `⋯`** |
| 1100 px | **4/8** | bị nuốt |

Nguyên nhân: CSS nhắm vào `.tab-nav`, còn **Gradio 6.26 không có phần tử nào tên `.tab-nav`** — thanh tab thật mang lớp `.tab-container`. Tôi đếm trực tiếp trong DOM: `document.querySelectorAll('.tab-nav').length` = **0**.

Bằng chứng quyết định: tôi chạy lại **gỡ sạch CSS** rồi đo lại ở 1366 px — kết quả **giống hệt từng pixel** (6 tab, cùng toạ độ x = 75/221/421/630/784/1039, cùng nút tràn ở x = 1257). **Có CSS hay không có CSS là như nhau.** Miếng vá không sửa được gì.

**Mức độ thiệt hại — vừa, không phải thảm hoạ.** Vì selector sai nên dòng `display:none` định giấu menu tràn cũng không chạy theo; menu `⋯` (34 × 26 px, ở x = 1257) vẫn còn và **vẫn bấm được**: tôi bấm vào nó ở 1366 px, thấy đủ *Tải dữ liệu mới* + *Nhật ký (JSON)*, bấm tiếp thì form tải lên hiện ra đúng. Nghĩa là hai tab **vẫn tới được**, chỉ là **không nằm ở chỗ người thuyết trình đã tập**.

> Rủi ro thật: sổ tay bảo "bấm tab **Tải dữ liệu mới**". Trên máy chiếu 1366 px tab đó không có trên thanh. Người nói sẽ khựng lại giữa buổi và đi tìm. Đó là mất bình tĩnh, không phải mất chức năng.

**Cách sửa chắc ăn:** không phải đổi selector. Gradio 6 tính tràn **bằng JavaScript** (đo tổng bề rộng 1 400 px so với khoang 1 174 px rồi tự đẩy phần thừa vào `⋯`), nên CSS `flex-wrap` khó ép được. Cách chắc chắn là **rút ngắn nhãn tab cho tổng dưới ~1 174 px**, ví dụ `Kết quả tổng hợp (60 bản sạch)` (256 px) → `Tổng hợp 60 bản` và `Nhịp tim thai + đèn đoạn` (209 px) → `Nhịp tim thai`; hai chỗ đó đã tiết kiệm ~215 px, vừa đủ. Nếu không kịp sửa: **đặt cửa sổ trình duyệt ở 1920 px hoặc thu phóng trình duyệt xuống 80 % (Ctrl+−)** trước buổi demo — đủ để cả 8 tab hiện ra, và không phải đụng vào mã.

---

## VIỆC 2 — ĐỐI CHIẾU SỐ LIỆU (33 con số, rải đều 4 tệp)

**Khớp 22 · Không khớp 10 · Giá trị đúng nhưng ghi sai nguồn 1.**

### Không khớp

| # | Giá trị | Tệp:dòng | Sự thật |
|---|---|---|---|
| 1 | Sai số STV khi F1 < 90 = **25,78 ms** | `docs/HUONG_DAN_DEMO.md:53` | **25,74** (`analysis/clinical_results.json`, n = 9) |
| 2 | "**sáu mươi** kiểm thử tự động qua hết" | `docs/KICH_BAN_HANH_TRINH.md:530` | **82** |
| 3 | `pytest demo/test_core.py` → "**17 pass**" | `docs/KICH_BAN_HANH_TRINH.md:685` | **39** |
| 4 | Cột **Thắng/Hoà/Thua** đảo, 6 dòng | `docs/DE_CUONG_HIEN_TRANG.md:313, 316–321` | xem khung dưới |
| 5 | "thắng 49 / **hoà 5 / thua 6**" | `docs/DE_CUONG_HIEN_TRANG.md:342` | hoà **6** / thua **5** |
| 6 | `app.py` **603** dòng · `core.py` **789** dòng | `docs/DE_CUONG_HIEN_TRANG.md:528` | **924** · **1 147** |
| 7 | "**6 tab**" · "**12 ảnh**" | `docs/DE_CUONG_HIEN_TRANG.md:528, 685` | **8 tab** · **16 ảnh** |
| 8 | Kiểm thử **60/60** (43 + **17**) | `docs/DE_CUONG_HIEN_TRANG.md:535` | **82** (43 + **39**) |
| 9 | "**60 kiểm thử tự động**" (ô số bìa) | `docs/NOI_DUNG_SLIDE.md:31, 35, 715, 727` | **82** |
| 10 | "**12 ảnh** trong `demo/screenshots/`" | `docs/NOI_DUNG_SLIDE.md:727, 815` | **16** |

### Lỗi số nghiêm trọng nhất — đảo cột trong bảng kết quả chính

`docs/DE_CUONG_HIEN_TRANG.md:313` đặt tiêu đề **`Thắng/Hoà/Thua`**, nhưng sáu dòng dữ liệu chép nguyên thứ tự khoá JSON là `thang / thua / hoa`. Đọc theo tiêu đề thì bảng nói ngược hẳn kết quả:

| Dòng | Đang in | Đọc theo tiêu đề (SAI) | Sự thật |
|---|---|---|---|
| `:316` learned | 15 / 13 / 32 | thua 32 | 15 / **32** / **13** |
| `:317` rrplaus | 17 / 9 / 34 | thua 34 | 17 / **34** / **9** |
| `:318` rrcv | 15 / 10 / 35 | thua 35 | 15 / **35** / **10** |
| `:319` gate | 16 / 7 / 37 | thua 37 | 16 / **37** / **7** |
| `:320` **gate4** | 17 / 5 / 38 | thua 38 | 17 / **38** / **5** |
| `:321` **peakprob** | 19 / 6 / 35 | **thua 35/60 bản** | 19 / **35** / **6** |

`docs/NOI_DUNG_SLIDE.md:429–437` in **đúng** (`19/35/6`). Nghĩa là **hai sản phẩm đang nói ngược nhau về chính bảng kết quả chủ lực**. Nếu cô mở đề cương trong lúc slide đang chiếu, đây là chỗ vỡ nhanh nhất cả buổi.

### Giá trị đúng nhưng sai nguồn

`docs/HUONG_DAN_DEMO.md:398–399, 688` ghi jitter **3,76 ms** (đúng) nhưng dẫn nguồn `analysis/xacnhan_results.json` — tệp đó **không có trường jitter nào**. Nguồn thật: `analysis/chandoan_m1_jitter.json → tong_hop.peakprob_67.trung_vi` = 3,7589.

### Đã kiểm và KHỚP (trích)

Thổi phồng chồng lấn m5 +7,18 / m12 +6,41 / m22 +5,12 / oracle +3,27 · bảy kiến trúc (7 dòng × 5 cột) · phổ lỗi 6 nhóm (24/24 ô) · cổng 3 890 đoạn / 210 xấu / AUROC gộp 0,965 [0,857; 0,992] · rủi ro–độ phủ +0,27 [−0,02; +0,48] · tỉ lệ lấy lại 89,49 % [81,4; 103,16], jackknife [88,62; 93,43] · bảng baseline công bố (8/8 ô) · 99,40 so với 99,46 của tác giả · header `a09.hea` chép đúng từng ký tự · ngưỡng đoạn xanh 0,052 / đỏ 0,540 · a02 bám nhịp mẹ 78 %.

### Mâu thuẫn nội bộ về xác suất venue

`KICH_BAN_HANH_TRINH.md:534` ghi 58 / 12 / 32 / <5 % (khớp số chính vòng 8).
`NOI_DUNG_SLIDE.md:684–688` ghi 55 / 15–20 / 35 / 80 % (khớp `docs/CHIEN_LUOC_CONG_BO.md` mục 2.1, nhưng **lệch số chính**).
Chưa chốt một bộ số duy nhất. Nếu cô hỏi "khả năng đăng bao nhiêu phần trăm" mà hai tài liệu trả lời khác nhau thì khó đỡ.

---

## VIỆC 3 — TÍNH NHẤT QUÁN GIỮA 5 SẢN PHẨM

### (1) Tên tab — chuẩn (tôi tự đọc `demo/app.py`)

Cấp 1 (8): `Tín hiệu (5 tầng)` · `Chọn kênh — cả 4 kênh` · `Nhịp tim thai + đèn đoạn` · `So sánh với nhãn` · `Kết quả tổng hợp (60 bản sạch)` · `Dữ liệu của nhóm` · `Tải dữ liệu mới` · `Nhật ký (JSON)`
Cấp 2, lồng trong *Tải dữ liệu mới* (5): `Tín hiệu (5 tầng)` · **`Chọn kênh — mọi kênh`** · `Nhịp tim thai + đèn đoạn` · `So sánh với nhãn` · `Nhật ký (JSON)`

**Trả lời câu hỏi "tên tab có khớp không": phần lớn khớp, bốn chỗ lệch.**

| Vấn đề | Tệp:dòng | Ghi trong tài liệu | Chuẩn |
|---|---|---|---|
| Đủ 8 tên, đúng thứ tự, đúng gạch ngang dài | `HUONG_DAN_DEMO.md:17–18` | — | **KHỚP** |
| Cắt cụt tên | `HUONG_DAN_DEMO.md:155` | "tab **Chọn kênh**" | `Chọn kênh — cả 4 kênh` |
| Cắt cụt tên | `HUONG_DAN_DEMO.md:593` | "tab *Kết quả tổng hợp*" | `Kết quả tổng hợp (60 bản sạch)` |
| Cắt cụt tên | `KICH_BAN_HANH_TRINH.md:576` | "bỏ tab *Chọn kênh*" | `Chọn kênh — cả 4 kênh` |
| **Thiếu hẳn** | không tệp nào | `Chọn kênh — mọi kênh` (tab con) **không xuất hiện ở bất kỳ tệp docs nào** | `app.py:876` |

Tab con tên **khác** tab cấp 1 ("mọi kênh" chứ không phải "cả 4 kênh") mà không tài liệu nào nói — người nói dễ gọi nhầm tên ngay trên màn hình.

### (2) Số tab — **4 chỗ nói 6, sự thật là 8**

`KICH_BAN_HANH_TRINH.md:39` ("S15 | DEMO — 6 tab") · `KICH_BAN_HANH_TRINH.md:530` ("Demo web sáu tab") · `DE_CUONG_HIEN_TRANG.md:528` · `DE_CUONG_HIEN_TRANG.md:685`.
`HUONG_DAN_DEMO.md:17` ghi "Tám tab" — **đúng**, và là tệp duy nhất đúng.

### (3) Thứ tự demo — **hai tài liệu KHÔNG khớp**

| | `HUONG_DAN_DEMO.md` §3 (:136–161) | `KICH_BAN_HANH_TRINH.md` (:297–308) |
|---|---|---|
| Thời lượng | **6–8 phút** | **4 phút** |
| r01 | Tín hiệu → **So sánh với nhãn** | Tín hiệu (bỏ bước So sánh) |
| a09 | Chọn kênh, đổi PSD rồi đổi lại | giống |
| a02 | Đèn tin cậy → fHR → **quay lại Chọn kênh** | Đèn tin cậy → fHR (không quay lại) |
| **Dữ liệu của nhóm** | **có** (4:35–6:00, đổi 3 bộ, xem thô) | **KHÔNG CÓ** |
| **Tải dữ liệu mới** | **có** (6:00–7:00, nạp `vidu_tai_len.csv`) | **KHÔNG CÓ** |
| Bản rút 3 phút | r01 → a09 → kết, **bỏ a02** | A.2: r01, a09, **giữ a02** |

**Gốc rễ:** `KICH_BAN_HANH_TRINH.md` chưa được cập nhật cho vòng 9 — toàn tệp **không nhắc `Dữ liệu của nhóm` hay `Tải dữ liệu mới` lần nào**, cũng không nhắc tệp ví dụ `vidu_tai_len.csv`. Nó vẫn là kịch bản của bản demo 6 tab.

Thêm: `NOI_DUNG_SLIDE.md:820–821` ghi *"Thứ tự demo **4 phút** theo `docs/HUONG_DAN_DEMO.md` **mục 3**"* — **dẫn sai nguồn**: mục 3 của sổ tay là 6–8 phút và có 5 chặng. Slide đang mô tả kịch bản của tệp kia nhưng trỏ nguồn sang sổ tay.

### (4) Số liệu 5 bản minh hoạ so với `demo/results/demo_check_showcase.json` — **KHỚP TOÀN BỘ**

| Bản | Tài liệu | JSON / tôi chạy lại | |
|---|---|---|---|
| r01 | F1 99,92 · Se 100,00 · PPV 99,84 · jitter 1,47 ms · kênh 4 | 99,9224 / 100,0 / 99,845 / 1,4689 / kênh 4 | ✔ |
| a09 | peakprob k1 0,990; k2–k4 0,905–0,932; F1 94,25; k2 F1 19,35 | 0,98975 / 0,90469–0,93228 / 94,2529 / 19,3548 | ✔ |
| a02 | F1 24,91 · bám mẹ 78 % · đèn THẤP | 24,9135 / 0,78295 / thap | ✔ |
| a27 | 32,94 · đèn đỏ cả hai chế độ | 32,9412 / luat thap + hoc thap | ✔ |
| B2_03 | 83,91 | 83,9065 (peakprob, kênh 4) | ✔ |

**Một chỗ trông như mâu thuẫn nhưng KHÔNG phải lỗi** — cần một chữ làm rõ:
`NOI_DUNG_SLIDE.md:477` ghi `B2_03 (F1 79,72)`, `DE_CUONG_HIEN_TRANG.md:539` ghi `B2_03 (83,91)`. Tôi chạy lại: **cả hai đều đúng, nhưng là hai đại lượng khác nhau** — 79,72 là F1 **kênh 1 (quy tắc PSD)**, dùng trong bảng cổng 22 chủ thể; 83,91 là F1 **kênh 4 (peakprob)**, dùng trong demo. Không tệp nào nói rõ kênh nào, nên đọc cạnh nhau vẫn giống mâu thuẫn. Chỉ cần thêm "(kênh PSD)" / "(peakprob)".

### (5) Các lệch khác

| Sự việc | Nói | Thật | Tệp:dòng |
|---|---|---|---|
| Số slide / vị trí slide DEMO | 22 slide, DEMO = S15 | **26** slide, DEMO = **slide 25** | `KICH_BAN_HANH_TRINH.md:21, 39` |
| Commit | `85cd61a`, 10 commit | **`c20417b`, 11 commit** | `DE_CUONG_HIEN_TRANG.md:30, 536, 735` |
| Tổng dòng `.py` | "~27 700" | ~29 400 (tính theo cách của nhóm) | `KICH_BAN_HANH_TRINH.md:530` |
| Tên tệp ảnh | "`demo/screenshots/01.png`" | thật là `01_r01_tong_quan.png` … | `NOI_DUNG_SLIDE.md:813, 815` |
| Manifest ảnh | — | `screenshots.json` chỉ liệt kê **12**; 4 ảnh 13–16 có trên đĩa nhưng **không có trong manifest** | `demo/screenshots/screenshots.json` |
| Độ trễ tệp ví dụ | "453 ms" | smoke ngày 13/09 đo 0,49 s | `HUONG_DAN_DEMO.md:437` |

**Khớp tốt, không cần sửa:** tên 5 nhãn bộ dữ liệu (`HUONG_DAN_DEMO.md:252–256` so với `demo/core.py:797–803`) khớp nguyên văn · bảng 9 cột khớp `app.py:512–513` · tên 3 tệp ví dụ khớp đĩa (CSV 30 000 dòng + tiêu đề, 4 cột `AECG1..4`, nhãn 65 dòng) · các số dùng chung 82,01 / 74,28 / 81,01 / 80,72 / +7,73 / 97,56 / −1,27 / +10,85 / 113 481 khớp nhau ở cả bốn tệp.

---

## VIỆC 4 — CHẤT LƯỢNG VĂN BẢN

### (a) `KICH_BAN_HANH_TRINH.md` — độ dài câu ĐẠT, giọng văn CÓ VẤN ĐỀ

Trên 133 dòng lời thoại (`>` và khối `[NÓI GÌ]`), 570 câu: trung vị **11 từ**, chỉ **11 câu ≥ 25 từ (1,9 %)**, dài nhất 33 từ. Với kịch bản nói, đây là mức an toàn.

**5 câu dài nhất**

| # | Từ | Tệp:dòng | Câu |
|---|---:|---|---|
| 1 | **33** | `:221` | "Có một điểm làm em yên tâm hơn: họ đứng đầu ở giao thức rút gọn cũng chính là họ đang chạy ở giao thức đầy đủ, và số đầy đủ là 97,56." |
| 2 | 31 | `:266` | "Em có thể tự chú thích mười đến hai mươi bản, nhưng phải có chuyên gia kiểm lại, nếu không thì nhãn của em cũng chỉ là đầu ra thuật toán." |
| 3 | 29 | `:355` | "Hiện giờ ngưỡng quyết định của em được quét trên một chủ thể validation riêng rồi áp cố định sang tập kiểm, không bao giờ quét trên tập kiểm." |
| 4 | 28 | `:321` | "Em có ghi số của họ trong phần tổng quan, nhưng em ghi kèm đơn vị đo của họ và ghi rõ là không so trực tiếp được." |
| 5 | 25 (7 câu đồng hạng) | `:129, 244, 280, 341, 355, 469, 627` | vd `:341` "Không bao giờ báo cáo một siêu tham số được chọn sau khi nhìn tập đánh giá, mà không gắn nhãn là chọn hậu kiểm." |

**Có nghe như AI viết không — CÓ, khá rõ.** Đây là vấn đề nặng hơn độ dài câu, vì kịch bản này để sinh viên **nói ra miệng**.

*Châm ngôn tự đúc* (nguy hiểm nhất — không ai nói thế trong lúc trình bày):

| Tệp:dòng | Nguyên văn |
|---|---|
| `:100` | "Bài học là: **ghi chú chỉ có giá trị khi nó biến thành một việc có hạn.**" |
| `:375` | "**Cái giá của việc đoán đúng thì nhỏ, cái giá của việc đoán sai mà tin là rất lớn.**" |
| `:64` | "**Một máy đưa ra con số sai mà không cảnh báo thì nguy hiểm hơn không có máy.**" |
| `:411` | "Bài học: **tìm trong y văn gốc trước khi gọi cái gì là phát hiện.**" |
| `:648` | "…một hội đồng sẽ tin **một đề tài biết rõ ranh giới của mình hơn là một đề tài toàn số đẹp.**" |

*Nhịp ba vế:* `:98` "Em đã đọc. **Em đã ghi. Rồi em không làm.**" · `:278` "**Khác dung sai. Khác đơn vị. Khác cách chia tập.**" · `:284` "**Cùng dữ liệu. Cùng khâu lọc. Cùng khâu khử tim mẹ. Cùng bộ chấm.**"

*"Không phải A mà là B":* **19 lần** trong 133 dòng thoại (`:54, 56, 127, 131, 183, 186, 200, 224, 248, 292, 318, 441×2, 445, 466, 469, 481, 534, 636`). Một hai lần thì tự nhiên; 19 lần thành tật văn phong nghe được bằng tai.

*Lây sang slide:* `NOI_DUNG_SLIDE.md:835` "Em không làm ra bộ dò tốt nhất — em làm ra một phép đo có ranh giới" và `:839` "Cái em cần tiếp theo không phải mô hình tốt hơn — mà là dữ liệu có nhãn". Hai khẩu hiệu đối xứng in liền nhau trên slide kết — chỗ lộ nhất cả buổi.

> Khuyến nghị: **giữ** `:98` (phục vụ đoạn thú nhận, có sức nặng thật), **hạ giọng** `:64, 100, 375, 411, 648` thành lời kể việc, và giảm "không phải A mà là B" xuống dưới 8 lần.

### (b) `DE_CUONG_HIEN_TRANG.md` — đủ 15 mục ✔, mục 13 đủ 4 nhóm ✔, **4 bảng thiếu nguồn**

15 mục đủ và đúng thứ tự (1 Thông tin → 15 Phụ lục). Mục 13 đủ bốn nhóm: **(a) dữ liệu** `:580` (4 câu) · **(b) kiến trúc–mô hình** `:589` (3) · **(c) hệ thống–triển khai** `:597` (3) · **(d) công bố–giải thưởng** `:605` (5). Cả bốn bảng đều có cột "Câu trả lời của cô sẽ đổi cái gì" — tốt.

**Bảng số liệu thiếu dòng *Nguồn*:**

| Bảng | Dòng | Số không truy được về tệp |
|---|---|---|
| **10. GIỚI HẠN (G1–G11)** | `:496–508` | Bảng dày số nhất tệp mà không có nguồn: seed 97,56 vs 97,59 · 76,9 % · +0,33/+20,50 ms · AUROC 0,980 · độ phủ 66,7 % · 15/16 |
| **7.2 Ánh xạ 15 bản chồng lấn** | `:246–252` | Bảng bằng chứng quan trọng nhất của đề tài mà không nêu tệp. Nguồn thật có: `survey/ro_ri_vanlieu.json`, `benchmark_dpss/eval_cinc60_sach.json → meta.leak_records` (được ghi ở `KICH_BAN_HANH_TRINH.md:430` nhưng không ghi ở đây) |
| **7.1 Bốn bộ dữ liệu** | `:226–231` | 15/681/35/5,6 MB · 75 bản · 1 kHz · 60 s. Dòng nguồn ở `:233` chỉ trỏ cho hai bộ **đã loại** |
| **Bảng 5 — AUROC** | `:411–416` | chỉ được phủ bởi dòng nguồn chung ở `:449–450`, cách 34 dòng và sau một bảng khác |

Các bảng kết quả chính (1–4, phổ lỗi) **đều có nguồn đầy đủ**. Điểm sáng đáng giữ: `:426–428` ghi thẳng *"con số 5/24 lấy từ `analysis/GATE22.md` dòng 293–304; **chưa truy được về một trường JSON riêng**"* — đúng chuẩn trung thực, nên áp cùng cách đó cho bảng mục 10.

### (c) `NOI_DUNG_SLIDE.md` — **26 slide** ✔ · không slide nào quá 5 gạch ✔ · **41 dòng quá 12 từ** ✘

26 slide (trong khoảng 22–26, nhưng sát trần). Không slide nào quá 5 gạch đầu dòng — nhưng **23/26 slide dùng đúng 5**, tức nội dung bị ép vừa khuôn.

**Tệp tự đặt luật ở `:12–13`** ("tối đa 5 gạch, mỗi dòng tối đa 12 từ") rồi **tự vi phạm ở 41/123 dòng = 33 %**. 20 dòng tệ nhất:

| Từ | Slide | Tệp:dòng | Nội dung |
|---:|---|---|---|
| **19** | S24 | `:778` | "1. Dữ liệu và một bác sĩ sản. Đầu mối khoa sản đang ghi CTG hoặc điện tim bụng" |
| 18 | S19 | `:595` | "Ban tổ chức đã ghi nhận từ 2013; ghi chú đọc bài của em có, em bỏ sót" |
| 18 | S24 | `:781` | "3. Euréka. Hạn nội bộ TDTU kỳ 2026 em chưa xác minh — em sẽ hỏi Đoàn trường" |
| 18 | S25 | `:808` | "a02 (F1 24,91 — đèn đỏ, hệ thống từ chối) · a27 (gần như không có tín hiệu)" |
| 18 | S26 | `:835` | "Em không làm ra bộ dò tốt nhất — em làm ra một phép đo có ranh giới" |
| 18 | S26 | `:839` | "Cái em cần tiếp theo không phải mô hình tốt hơn — mà là dữ liệu có nhãn" |
| 16 | S14 | `:416` | "gate4 (quy tắc trong họ khai báo trước): 81,01 · p Holm 0,015 — sống sót" |
| 16 | S22 | `:717` | "Không khối nào bị chặn bởi kỹ thuật — chỉ bởi dữ liệu và thời gian" |
| 16 | S26 | `:838` | "Mọi con số báo trên dữ liệu sạch; mọi số sai đều được rút công khai" |
| 15 | S5 | `:125` | "RQ1 — Đến mức nào? Một kênh lấy lại bao nhiêu phần của bốn kênh?" |
| 15 | S19 | `:597` | "5: từng kết luận khoảng cách ngoài miền không thuộc mô hình → đã rút" |
| 15 | S23 | `:752` | "Tuần 3–4: dữ liệu thứ ba nếu có bác sĩ; STV sau cổng; chốt đích" |
| 14 | S5 | `:127` | "RQ2 — Có biết không? Hệ thống có tự nhận ra lúc mình sai?" |
| 14 | S9 | `:242` | "Kết luận: khoảng cách đo bề rộng ngữ cảnh, không phải họ kiến trúc" |
| 14 | S11 | `:319` | "Kiểm chứng ngoài: Silesia B1 em đo 99,40 — tác giả công bố 99,46" |
| 14 | S15 | `:471` | "Nhưng 5 / 24 quy tắc một đặc trưng cũng làm được như vậy" |
| 14 | S19 | `:598` | "Cái em thật sự làm: định danh 15 bản và đo mức thổi phồng" |
| 14 | S20 | `:642` | "Kết quả: 5 tuyên bố lớn tự rút, kể cả tuyên bố mình thích" |
| 14 | S23 | `:751` | "Tuần 1–2: cam kết git, tính lại cổng + phổ lỗi trên 60 sạch" |
| 14 | S23 | `:754` | "Tuần 7–10: rà văn liệu ảnh hưởng; viết bản thảo; phản biện nội bộ" |

Nặng nhất: **S24, S26, S23, S19** (mỗi slide 3/5 dòng vi phạm). S24 và S26 là hai slide đóng — chính là chỗ không được để chữ dày.

### (d) `HUONG_DAN_DEMO.md` — ví dụ `.hea` **ĐỌC THẬT** ✔ · câu trả lời tần số **SAI** ✘

**Ví dụ `.hea` — khớp 100 %.** Tôi tự đọc `benchmark_dpss/pcdb/a09.hea` và so từng dòng với `:213–219`:

| Dòng | Trên đĩa = trong tài liệu |
|---|---|
| 1 | `a09 4 1000 60000` |
| 2 | `a09.dat 16 10/uV 12 0 57 -11458 0 AECG1` |
| 3 | `a09.dat 16 10/uV 12 0 3 14104 0 AECG2` |
| 4 | `a09.dat 16 10/uV 12 0 -31 -732 0 AECG3` |
| 5 | `a09.dat 16 10/uV 12 0 -18 25735 0 AECG4` |

Không sai một ký tự. Bảng giải nghĩa trường ở `:225–245` cũng đúng chuẩn WFDB (`16` = int16, `10/uV` = 10 adu/µV, `12` = độ phân giải A/D, `57` = mẫu đầu, `-11458` = checksum). Tài liệu ghi "(5 dòng, đã đọc trực tiếp từ đĩa)" — **đúng sự thật**.

**Câu trả lời về tần số — bảng tái lấy mẫu ĐÚNG, nhưng phần giới hạn SAI.**
Tôi đọc `_to_1000hz` (`core.py:183–188`) và `load_record` (`:197–267`) rồi tính lại `Fraction(1000/fs).limit_denominator(1000)` cho từng dòng bảng `:466–475`: **1000 → giữ nguyên · 500 → ×2 · 360 → ×25/9 · 250 → ×4 · 200 → ×5 · 256/512/128 → ×125/32, 125/64, 125/16 · 2000/4000 → ÷2, ÷4 · 333,3 → ×3 = 999,9 Hz, lệch 0,01 %, trôi ~6 ms/60 s.** **Đúng hết**, kể cả con số trôi.

Nhưng ba chỗ phải sửa:

| # | Vấn đề |
|---|---|
| **S1 — nặng nhất** | `:479–481` viết *"Khuyến nghị fs ≥ 250 Hz; **dưới 200 Hz phải coi là thí nghiệm thăm dò**"* — hàm ý "vẫn chạy được". Thực tế `core.py:998` + `:1087` **từ chối thẳng** mọi fs ngoài **50–20 000 Hz** bằng `LoiDuLieu`. Tôi đã chạy: `fs = 0` → báo lỗi ngay. **Trớ trêu:** giao diện `app.py:695–696` **in đúng** dải "50–20000 Hz" — nên sổ tay đang mâu thuẫn với chính màn hình sẽ chiếu cho cô xem. |
| **S2** | `:475` lấy **333,3 Hz** làm ví dụ, nhưng ô nhập là `gr.Number(..., precision=0)` (`app.py:862–863`) → **làm tròn về số nguyên**, không gõ được 333,3. Ví dụ minh hoạ sai số **không tái hiện được qua giao diện**. |
| **S3** | Kiểm tra `FS_MIN/FS_MAX` nằm trong nhánh `if not tu_khai` (`:1081`), tức **chỉ áp cho `.csv/.npy/.txt`**. Với `.edf`/`.hea` tần số đọc từ tệp và **không bị kiểm tra gì** — một EDF khai 10 Hz vẫn lọt. Tài liệu không nói hệ quả này. |

Các phát biểu khác trong cùng mục đã kiểm và **đúng**: `:477–478` (về 1000 Hz → lọc 10–60 Hz + notch 50 → ÷4 xuống 250) · `:489` ngưỡng 8 giây · `:492` cần ≥ 3 nhịp mẹ · `:38` danh sách định dạng.

---

## VIỆC 5 — TỪ CẤM VÀ SỐ ĐÃ RÚT

### **KHÔNG CÓ VI PHẠM NÀO.** Quét 4 tệp docs + `demo/app.py` + `demo/core.py`.

Mọi lần xuất hiện đều thuộc diện miễn trừ, phân loại rõ:

| Loại (miễn trừ) | Tệp:dòng |
|---|---|
| Danh sách từ cấm | `HUONG_DAN_DEMO.md:647–650` · `NOI_DUNG_SLIDE.md:936–944` |
| Hộp cảnh báo / câu rút lại | `DE_CUONG_HIEN_TRANG.md:335, 393, 395, 464, 474–477, 483` · `NOI_DUNG_SLIDE.md:922–932` · `KICH_BAN_HANH_TRINH.md:654–678` |
| Lời kể sai lầm ("em đã sai") | `KICH_BAN_HANH_TRINH.md:333, 335` (mẫu 10 bản 90,34 / 69,31 / 69,33 / 79,40), `:403` ("Lúc đó em đã **định** viết 'chúng tôi phát hiện rò rỉ'") · `NOI_DUNG_SLIDE.md:333, 577–583, 617–627` |
| Bảng "Tuyên bố đã rút" | `DE_CUONG_HIEN_TRANG.md:473–478, 546` (71,21 / 79,40 / 86,87 / 85,60 / 62,82 / +11,00 / 94,87 / 98,38 / 97,33) |
| Dùng thông thường, không hàm ý tính mới | `HUONG_DAN_DEMO.md:241` ("mẫu **đầu tiên** của kênh") · `DE_CUONG_HIEN_TRANG.md:108` ("bản đề cương **đầu tiên**") · `demo/app.py:717` ("cần nhìn **đầu tiên**") |

Chi tiết đáng ghi:

- `SOTA` / `novel` / `state-of-the-art` / `first`: **0 lần** ngoài danh sách cấm. `demo/app.py` và `demo/core.py` **hoàn toàn sạch**.
- `"lưỡng cực"`: chỉ có trong 2 danh sách cấm, **không lần nào dùng như đặc tính**.
- `"tiền đăng ký"` / `pre-registered`: không dùng. `"chỉ định trước"` dùng cho `gate`/`gate4` là **hợp lệ** (đúng số chính), và `DE_CUONG_HIEN_TRANG.md:335` nói thẳng **"tài liệu này không dùng chữ *tiền đăng ký*"**.
- `"Physiological Measurement là Q1"`: **không nơi nào khẳng định**. Ngược lại `NOI_DUNG_SLIDE.md:674, 695–696` và `DE_CUONG_HIEN_TRANG.md:609` nói rõ là **Q2/Q3**.
- `CinC 2026`: chỉ còn là **tên thư mục** `paper/cinc2026/` (`DE_CUONG_HIEN_TRANG.md:529, 687`), ngay cạnh ghi đích thật `CinC2027`. Không phải đích nộp. *(Nên đổi tên thư mục để khỏi hiểu nhầm bằng mắt.)*
- Số đã rút trong `demo/app.py`: chỉ 2 lần (`:133`, `:570`), cả hai là câu rút lại.
- `peakprob` được gắn nhãn **"hậu kiểm"** nhất quán ở mọi nơi, kể cả tiêu đề giao diện demo.

### 15 bản nhiễm — **0 lần dùng sai. Toàn bộ 12 lần xuất hiện đều HỢP LỆ.**

| Tệp:dòng | Ngữ cảnh | Phân loại |
|---|---|---|
| `HUONG_DAN_DEMO.md:294` | "Đủ 15 mã" trong mục Cảnh báo bắt buộc | HỢP LỆ |
| `HUONG_DAN_DEMO.md:300–304` | Bảng ánh xạ r01 → a04, a05, a22 … | **HỢP LỆ — bảng ánh xạ** |
| `HUONG_DAN_DEMO.md:635` | "KHÔNG mở bản ghi nhiễm làm ví dụ ngoài miền" | HỢP LỆ — lệnh cấm |
| `KICH_BAN_HANH_TRINH.md:43, 414` | Bảng chồng lấn slide S19 | **HỢP LỆ — bảng ánh xạ** |
| `DE_CUONG_HIEN_TRANG.md:248–252` | Mục 7.2, bảng ánh xạ | **HỢP LỆ — bảng ánh xạ** |
| `NOI_DUNG_SLIDE.md:601–602` | Sơ đồ ánh xạ 5 → 15 | **HỢP LỆ — bảng ánh xạ** |
| `demo/app.py:562` | Chuỗi hiển thị bảng ánh xạ trong tab *Dữ liệu của nhóm* | **HỢP LỆ** |
| `demo/core.py:44–46` | Hằng `CINC_LEAK`, khớp 15/15 với `eval_cinc60_sach.json → meta.leak_records` | HỢP LỆ |

**Kiểm chéo chủ động:** 5 bản minh hoạ demo là **r01, a09, a02, a27, B2_03** — không bản nào nằm trong 15 bản nhiễm. `demo_check_showcase.json → include_leak: false` xác nhận ở mức mã. Trong tab *Dữ liệu của nhóm*, bộ 15 bản được dán nhãn **"NHIỄM — bản sao r10 (ADFECGDB); NCC = 1,0000; lệch RR = 0,0 ms"** ngay trên bảng — không thể nhầm là dữ liệu ngoài miền.

---

## VIỆC 6 — PHÁN XỬ TỪNG SẢN PHẨM

| # | Sản phẩm | Phán quyết | Điều kiện |
|---|---|---|---|
| 1 | **`demo/`** | **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN** | Mã tốt: 82/82 test, smoke ĐẠT, hai tab mới chạy, lỗi tiếng Việt tử tế, cổng từ chối không bị lừa. **Điều kiện:** xử lý chuyện 2 tab biến mất ở 1366 px — hoặc rút ngắn nhãn tab, hoặc chốt chạy ở 1920 px / thu phóng 80 % và tập lại đúng thao tác đó. |
| 2 | **`docs/HUONG_DAN_DEMO.md`** | **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN** | Tệp tốt nhất trong bốn tệp (duy nhất cập nhật đúng 8 tab + ảnh 13–16, `.hea` đọc thật). **Điều kiện:** sửa mục tần số `:479–481` (dải 50–20 000 Hz, demo **từ chối** ngoài dải) và STV `:53` → 25,74. |
| 3 | **`docs/KICH_BAN_HANH_TRINH.md`** | **CẦN LÀM LẠI (phần demo)** | 13 phần hành trình + giọng văn thì dùng được, nhưng **toàn bộ khối demo là của bản 6 tab**. Làm lại: thêm hai chặng *Dữ liệu của nhóm* + *Tải dữ liệu mới*, sửa "6 tab" → 8, "60 kiểm thử" → 82, "17 pass" → 39, thống nhất thời lượng với sổ tay, gỡ mâu thuẫn bản rút 3 phút. |
| 4 | **`docs/DE_CUONG_HIEN_TRANG.md`** | **CẦN LÀM LẠI (phần bảng)** | Cấu trúc đủ 15 mục, mục 13 đủ 4 nhóm, bảng kết quả chính có nguồn. **Nhưng bảng Thắng/Hoà/Thua đảo cột làm đảo ngược kết quả chủ lực** — phải sửa trước khi đưa cho cô. Kèm: 4 bảng thiếu nguồn, số đếm vòng 8 còn sót. |
| 5 | **`docs/NOI_DUNG_SLIDE.md`** | **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN** | 26 slide, không slide nào quá 5 gạch, số liệu khớp JSON, bảng 7 quy tắc in **đúng**. **Điều kiện:** cắt 41 dòng quá 12 từ (ưu tiên S24/S26/S23/S19), sửa "60 kiểm thử" → 82 và "12 ảnh" → 16, sửa dẫn nguồn sai ở `:820–821`. |

**Không sản phẩm nào phải bỏ.**

### DANH SÁCH VIỆC PHẢI SỬA TRƯỚC BUỔI GẶP

**BẮT BUỘC — không sửa thì đừng mang ra (tổng ~50 phút)**

| # | Việc | Vị trí | Ước |
|---|---|---|---|
| 1 | **Sửa đảo cột Thắng/Hoà/Thua** (6 dòng + 1 câu). Cách nhanh nhất: đổi tiêu đề thành `Thắng/Thua/Hoà`, khớp ngay với dữ liệu đang in | `DE_CUONG_HIEN_TRANG.md:313, 316–321, 342` | **10 ph** |
| 2 | **Quyết chuyện thanh tab 1366 px.** Nhanh nhất và không đụng mã: chốt chạy demo ở 1920 px hoặc Ctrl+− về 80 %, rồi **tập lại đúng đường bấm**. Nếu muốn sửa gốc thì rút ngắn 2 nhãn tab dài nhất | `demo/app.py:841, 836` hoặc quy ước trình chiếu | **15 ph** |
| 3 | **Cập nhật số đếm vòng 9**: 82 test (43+39) · 8 tab · 16 ảnh · app.py 924 / core.py 1 147 dòng · commit `c20417b`/11 | `DE_CUONG_HIEN_TRANG.md:528, 535, 536, 685, 690, 735` · `NOI_DUNG_SLIDE.md:31, 35, 715, 727, 815` · `KICH_BAN_HANH_TRINH.md:39, 530, 685` | **15 ph** |
| 4 | **Sửa mục tần số**: nói rõ dải **50–20 000 Hz** và demo **từ chối** ngoài dải (đang mâu thuẫn với chính màn hình sẽ chiếu) | `HUONG_DAN_DEMO.md:479–481` | **10 ph** |

**NÊN SỬA — cô rất dễ hỏi trúng (tổng ~45 phút)**

| # | Việc | Vị trí | Ước |
|---|---|---|---|
| 5 | Bổ sung hai chặng demo mới vào kịch bản, thống nhất thời lượng (6–8 ph) với sổ tay, gỡ mâu thuẫn bản rút 3 phút | `KICH_BAN_HANH_TRINH.md:297–308, 576, 592` | **20 ph** |
| 6 | Thêm dòng *Nguồn* cho bảng mục **10 GIỚI HẠN** và bảng **7.2 ánh xạ 15 bản** | `DE_CUONG_HIEN_TRANG.md:496–508, 246–252` | **15 ph** |
| 7 | Chốt **một** bộ số venue (58/12/32 hay 55/15–20/35) và dùng thống nhất | `KICH_BAN_HANH_TRINH.md:534` vs `NOI_DUNG_SLIDE.md:684–688` | **10 ph** |

**NÊN SỬA NẾU CÒN THỜI GIAN (tổng ~50 phút)**

| # | Việc | Vị trí | Ước |
|---|---|---|---|
| 8 | Cắt 41 dòng slide quá 12 từ, ưu tiên S24/S26/S23/S19 | `NOI_DUNG_SLIDE.md` | **20 ph** |
| 9 | Hạ giọng 5 châm ngôn tự đúc; giảm "không phải A mà là B" từ 19 xuống dưới 8 | `KICH_BAN_HANH_TRINH.md:64, 100, 375, 411, 648` | **15 ph** |
| 10 | STV 25,78 → **25,74**; sửa nguồn jitter thành `analysis/chandoan_m1_jitter.json` | `HUONG_DAN_DEMO.md:53, 398, 688` | **5 ph** |
| 11 | Ghi rõ kênh cho B2_03 ("79,72 kênh PSD" / "83,91 peakprob") để hai tệp thôi trông như mâu thuẫn | `NOI_DUNG_SLIDE.md:477` · `DE_CUONG_HIEN_TRANG.md:539` | **5 ph** |
| 12 | Đổi ví dụ 333,3 Hz sang fs nguyên (ô nhập `precision=0`); bổ sung tên tab con `Chọn kênh — mọi kênh`; cập nhật `screenshots.json` cho 4 ảnh mới | `HUONG_DAN_DEMO.md:475` · `demo/screenshots/screenshots.json` | **5 ph** |

---

## KẾT

Vòng 9 làm tốt phần khó: **mã chạy thật, số khớp nguồn, kỷ luật ngôn từ giữ được nguyên vẹn** — không một từ cấm nào bị dùng như sự thật, không một số đã rút nào quay lại, không một bản nhiễm nào bị dùng sai chỗ, và cái bẫy nguy hiểm nhất (trích 98,46 của đoạn 30 s thay cho 94,25 của `a09` đầy đủ) đã được rào bằng ba lớp và **không ai sa vào**.

Cái hỏng nằm ở chỗ dễ hỏng nhất khi làm nhanh: **các tài liệu không được cập nhật đồng bộ sau khi mã đổi**. Ba trong bốn tệp docs vẫn đang mô tả bản demo 6 tab của vòng 8. Cộng thêm một lỗi sao chép bảng làm đảo ngược kết quả chủ lực, và một miếng vá CSS mà chủ nhiệm tin là đã sửa xong nhưng thật ra chưa chạm được vào vấn đề.

Ba việc bắt buộc đầu tiên mất khoảng **40 phút**. Làm xong ba việc đó thì buổi gặp ngày mai an toàn.
