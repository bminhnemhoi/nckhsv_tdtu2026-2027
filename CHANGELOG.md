# Nhật ký thay đổi

Mọi thay đổi đáng kể của RelyFetal, mới nhất ở trên. Mỗi mục ghi **commit**, **đã làm gì**, và **đã rút gì**.
Chi tiết từng vòng thẩm định: [`docs/nhat_ky/`](docs/nhat_ky/). Danh sách đầy đủ số đã rút:
`survey/facts_phase4.json` mục `Z_DA_RUT`.

> **Đính chính lịch sử git.** Tiêu đề commit `fb1c53b` ghi *"find a 15-record leak"*. Cách diễn đạt đó **sai**:
> chồng lấn CinC 2013 set-a ↔ ADFECGDB đã được ban tổ chức ghi nhận từ 2013 (Silva et al., CinC 2013;
> Clifford et al., Physiol Meas 2014). Nhóm chỉ **định danh bằng đo lường** đúng 15 bản nào và mức thổi phồng.
> Lịch sử đã đẩy lên nên không viết lại; đính chính ở đây và ở vòng 7 bên dưới.

---

## [Chưa phát hành] — 15/09/2026 — Bàn giao

**Đã làm**

- `HANDOFF.md` ở gốc repo: cài đặt, tải dữ liệu, bản đồ kho mã, nguồn sự thật, quy tắc liêm chính, bẫy kỹ thuật,
  việc tiếp theo, câu hỏi còn mở.
- `requirements.txt` bổ sung bốn gói **demo cần mà thiếu** — `gradio`, `pandas`, `plotly`, `requests`. Trước đó cài
  theo tệp này rồi chạy `python demo/app.py` là lỗi `ModuleNotFoundError`. Ghi phiên bản đã kiểm thử cho mọi gói.
- `requirements-research.txt` tách riêng gói cho thí nghiệm phân tích, dựng tài liệu, chụp ảnh demo
  (`diptest`, `persim`, `pymupdf`, `python-docx`, `pypdf`, `playwright`).
- Dọn gốc repo: 7 biên bản thẩm định chuyển vào `docs/nhat_ky/` bằng `git mv` (giữ lịch sử), sửa 33 tham chiếu.
- Slide 26 trang và sổ tay đề tài 16 mục chép vào `docs/trinh_bay/` — mở được bằng trình duyệt, không cần mạng.
- `CHANGELOG.md` này.

**Đã sửa — tìm ra bằng giả lập môi trường CI và Docker**

Giả lập bằng cách chặn import đúng những gói mà runner CI và image Docker **không** cài (có tính phụ thuộc bắc cầu:
`wfdb` tự kéo `pandas`, `matplotlib`, `requests`), rồi chạy toàn bộ kiểm thử.

- **`ripser` là phụ thuộc bắt buộc, không phải tuỳ chọn.** `fsqi/fsqi.py` import nó ở đầu tệp, và đèn tin cậy mặc định
  (`hoc`) nạp `fsqi/gate.py` → `fsqi.py`. Bản đầu của đợt bàn giao này xếp nhầm `ripser` vào
  `requirements-research.txt`; đã chuyển về `requirements.txt`.
- **CI thiếu `ripser`** → giả lập cho 15 thất bại khi có dữ liệu. Đã thêm vào `.github/workflows/ci.yml`. Sau sửa: 82 qua.
- **Dockerfile thiếu `scikit-learn`** → endpoint `/analyze` sập vì không unpickle được mô hình cổng từ chối. Giả lập
  cho 3 thất bại. Đã thêm `scikit-learn==1.9.0` (ghim khớp phiên bản đã pickle). Sau sửa: 13/13 test API qua.

---

## Vòng 9 — 13–14/09/2026 — Chuẩn bị buổi gặp giảng viên

`c20417b` · `d43db96` · `ca0b168`

**Đã làm**

- Demo thêm hai tab. **"Dữ liệu của nhóm"**: bảng 9 cột đọc thật từ `.hea`/`.edf` cho 5 bộ, in nguyên văn header,
  vẽ 10 giây tín hiệu thô kèm nhãn. **"Tải dữ liệu mới"**: nhận `.edf` / `.dat+.hea` / `.csv` / `.npy` / `.txt`,
  sáu trường hợp lỗi trả thông báo tiếng Việt thay vì stack trace.
- Kiểm thử 60 → **82**. Smoke test qua máy chủ Gradio thật.
- Tài liệu mới: `KICH_BAN_HANH_TRINH.md` (13 phần), `DE_CUONG_HIEN_TRANG.md` (15 mục), `NOI_DUNG_SLIDE.md`;
  `HUONG_DAN_DEMO.md` viết lại 8 phần.

**Đã sửa sau thẩm định**

- Bảng chọn kênh trong `DE_CUONG_HIEN_TRANG.md` bị **đảo cột Thắng/Thua** — đọc đúng chữ thì `peakprob` thua
  35/60 bản, trong khi sự thật là thắng 19 / hoà 35 / thua 6.
- CSS thanh tab nhắm `.tab-nav` — lớp này **không tồn tại** trong Gradio 6.26. Không tác dụng gì; ở màn 1366 px
  hai tab mới vẫn bị thu vào menu tràn. Sửa sang `.tab-container`.

---

## Vòng 8 — 12/09/2026 — Bài CinC 2027 và đề cương trên 60 bản sạch

`6fbcc35` · `85cd61a`

**Đã làm**

- Bài hội nghị viết lại toàn bộ trên **60 bản CinC sạch**, 4 trang, đích **CinC 2027**.
- Đề cương v3.5 (148 trang): 65 chỗ sửa, mục mới §5.10.4 về chồng lấn dữ liệu.
- Bài báo nêu `gate4` — quy tắc chỉ định trước **sống sót** hiệu chỉnh Holm (p = 0,015) — trước đó chỉ nằm trong bảng.

**Đã rút**

- "CinC 2026" như đích nộp — kỳ đó đã diễn ra 20–23/9/2026.

---

## Vòng 7 — 12/09/2026 — Kiểm văn liệu, thử nhân rộng

`ed819e3` · `7dd2dac`

**Đã làm**

- Rà văn liệu về chồng lấn CinC ↔ ADFECGDB; bảng các bài đã công bố huấn luyện trên ADFECGDB rồi thử trên set-a.
- Thử nhân rộng `peakprob` — **khai báo trước, neo git** (`ed819e3`) trước khi chạy.
- Chiến lược công bố, tài liệu Euréka có nguồn, kịch bản trình bày.

**Đã rút**

- **"Chúng tôi phát hiện rò rỉ dữ liệu."** Ban tổ chức đã ghi từ 2013; ghi chú đọc bài của chính nhóm đã nhắc.
- **"Mô hình không phải nút thắt."** Phép thử nhìn thấy tín hiệu có âm tính giả 18,0 % [12,1; 25,0].
- **"Physiological Measurement là Q1."** Là Q2 Scimago 2024.

**Kết quả âm tính ghi nhận**

- Không có bộ công khai nào khác có nhãn fQRS thật (NIFEADB, NInFEA, nifecgdb, set-b) → `peakprob` chưa nhân rộng được.
- Trên thang logit, `gate` vẫn đứng đầu nhánh 22 chủ thể — vấn đề hậu kiểm không biến mất.

---

## Vòng 6 — 12/09/2026 — Chồng lấn dữ liệu, kiến trúc, thích nghi miền

`fb1c53b`

**Đã làm**

- Định danh **15/75 bản CinC 2013 set-a** là bản sao nguyên văn dữ liệu huấn luyện ADFECGDB (tương quan chéo
  1,0000, lệch nhịp 0,0 ms). Mọi số CinC chuyển sang **60 bản sạch**.
- Chọn kênh mù nhãn: 7 quy tắc; `peakprob` +7,73 điểm trên 60 bản sạch.
- Đấu 7 họ kiến trúc cùng tham số — **đóng câu hỏi kiến trúc**, giữ TCN.
- Bốn phương pháp thích nghi miền — **cả bốn thất bại**.
- Phổ lỗi 6 nhóm có mức ngẫu nhiên đối chứng.

**Đã rút**

- Mọi số CinC tính trên 75 bản: 79,40 / 85,60 / 86,87 / 71,21 / 62,82 — thổi phồng 3,27–7,18 điểm.
- "Tiền đăng ký" — tệp khai báo không neo git và được ghi sau khi F1 từng kênh đã biết.

---

## Vòng 3–5 — 12/09/2026 — Rút số Power-MF hỏng, đo dải lọc trên TCN

`8b85310`

**Đã làm**

- Chạy lại Power-MF qua GNU Octave; vá `findpeaks` tốn bộ nhớ O(k²). Kiểm chứng ngoài: **99,40** chạy lại so với
  **99,46** tác giả công bố.
- Power-MF 1 kênh tự cắt — đối chứng công bằng nhất.
- Đo dải lọc trên chính TCN thay vì trên GBM.
- Hiệu chuẩn lại cổng từ chối cho mô hình 22 ca.

**Đã rút**

- Số Power-MF từ cổng chuyển hỏng: 94,87 / +2,74 / 98,38 / 97,33.
- "Dải lọc 10–60 Hz cho +11,00 điểm" — đo trên GBM cửa sổ 300 ms; trên TCN chỉ +2,44 [−0,04; +6,29].
- "Tám kiến trúc không phân biệt được" — TOST bác bỏ.
- Số CinC trên mẫu 10 bản: 59,15 / 69,31 / 77,34 / 90,34 / 22,33.
- Thống kê mức bản ghi — sửa về mức chủ thể đảo 5 kết luận.

---

## Giai đoạn 2 — 11/09/2026

`d4b44f2` · `da17651`

- Cổng từ chối học được, API REST, đường cong độ bền theo SNR, bản thảo CinC đầu tiên, 53 kiểm thử.
- Mô hình 22 chủ thể, đường cong hiệu quả mẫu, đề cương v3.2.

## Giai đoạn 1 — 11/09/2026

`500e0a5`

- Baseline cổ điển, nạp bộ Silesia, bảng kiến trúc sửa lại, nguyên mẫu cổng từ chối, demo đầu tiên.

## Phát hành đầu — 09/09/2026

`9cbff62`

- Mô hình `FetalQRS-TCN` phát hiện QRS thai đơn kênh.
