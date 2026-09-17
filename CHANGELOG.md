# Nhật ký thay đổi

Mọi thay đổi đáng kể của RelyFetal, mới nhất ở trên. Mỗi mục ghi **commit**, **đã làm gì**, và **đã rút gì**.
Chi tiết từng vòng thẩm định: [`docs/nhat_ky/`](docs/nhat_ky/). Danh sách đầy đủ số đã rút:
`survey/facts_phase4.json` mục `Z_DA_RUT`.

> **Đính chính lịch sử git.** Tiêu đề commit `fb1c53b` ghi *"find a 15-record leak"*. Cách diễn đạt đó **sai**:
> chồng lấn CinC 2013 set-a ↔ ADFECGDB đã được ban tổ chức ghi nhận từ 2013 (Silva et al., CinC 2013;
> Clifford et al., Physiol Meas 2014). Nhóm chỉ **định danh bằng đo lường** đúng 15 bản nào và mức thổi phồng.
> Lịch sử đã đẩy lên nên không viết lại; đính chính ở đây và ở vòng 7 bên dưới.

---

## Vòng 10 — 16–17/09/2026 — Buổi trình bày với giảng viên: kịch bản, bối cảnh, demo dễ hiểu

**Đã làm**

- Tài liệu mới: `docs/BOI_CANH_1_KENH.md` (vì sao một kênh, 30 bài theo số kênh, các bài đơn kênh đã tới đâu),
  `docs/CONG_BANG_DOI_CHUAN.md` (so sánh nào công bằng, dữ liệu đủ chưa), `docs/TOM_TAT_30_BAI.md`,
  `docs/KICH_BAN_THUYET_TRINH_v2.md` (30 phút), `docs/HUONG_DAN_DEMO_v2.md`. Hướng dẫn cũ giữ ở `HUONG_DAN_DEMO_v1.md`.
- Demo có **chế độ trình bày** mặc định: 4 thẻ bản ghi + thẻ tệp của bạn, 5 bước có nút Tiếp/Quay lại, hai hộp
  "Con số cần nhớ" / "Cách đọc hình", thanh tóm tắt cố định. 8 tab cũ nằm trong "Chế độ chuyên gia", tắt sẵn.
- Phản biện độc lập đóng vai giảng viên y sinh nghe lần đầu: `docs/nhat_ky/THAMDINH_VONG10_KICH_BAN.md`.

**Đã sửa — lỗi sự thật do phản biện tìm ra, trưởng nhóm kiểm lại trên đĩa**

- **Cổng từ chối không độc lập với mạng.** Kịch bản viết "12 chỉ số không lấy từ mạng". Sai: 2/12 chỉ số là xác suất
  đầu ra của mạng, và chỉ số quan trọng nhất (`rr_cv`, 0,140) tính trên nhịp mạng tìm ra (`fsqi/gate.py`,
  `analysis/gate22_results.json`).
- **Đèn trong demo là cổng cũ.** Tài liệu dùng AUROC trong bản ghi 0,934 để bảo chứng cho đèn. Số đó thuộc cổng 22 ca,
  chỉ có dạng phân tích. Demo chạy cổng hiệu chuẩn trên mô hình 5 ca, trong bản ghi 0,721 [0,517; 0,898]
  (5 bản CinC sạch a01 a06 a07 a09 a10, đo khi ghép mô hình 5 ca; ghép mô hình 22 ca đang chạy trong demo: chưa đo lại;
  `analysis/stats_results.json → comparisons.gate_auroc_cinc`, `analysis/GATE22.md`). Demo nay ghi rõ điều này ở bước 5.
- **a02 không phải "dây nào cũng hỏng".** Dây 1 đạt F1 75,88; 6/7 cách chọn dây không nhìn đáp án chọn dây 2 (24,91),
  learned chọn dây 3 (19,86); không cách nào chọn dây 1 (`analysis/chonkenh_results.json → chon_kenh_theo_quy_tac.cinc.a02`).
- **Độ lệch STV 20,50 ms** đo trên mẫu 10 bản có 4 bản chồng lấn; không dùng nữa.
- **"set-a chứa 25 bản ADFECGDB"** sai phạm vi: 25 bản nằm rải trong cả 447 bản Challenge; nhóm định danh 15 bản trong set-a.

**Đã sửa — demo**

- Thẻ a02 bỏ câu "số đẹp nhưng sai": nói rõ máy báo nhịp tim 130 trông bình thường nhưng đáp án ≈ 160.
- Bước 4 hiện **hộp vàng trung thực** khi dây được chọn kém dây tốt nhất theo đáp án từ 10 điểm F1 trở lên.
- Thanh tóm tắt gạch ngang nhịp tim khi đèn đỏ; dòng 60 bản lượt 1 báo bốn số 74,28 · 81,01 · 82,01 · trần 83,60
  (thiếu gate 80,72; lượt 2 bên dưới đã bổ sung thành năm số).
- Bước 5: bảng Se/PPV/đếm nhịp/thời gian vào mục "Chi tiết kỹ thuật" đóng sẵn; số kiểu Việt trên hình và bảng.
- Ẩn chân trang Gradio; 5 thẻ cao bằng nhau.
- **Lỗi có từ vòng 9:** CSS ẩn nút "…" của thanh tab. Gradio 6.26 đo độ rộng bằng JS và dồn tab thừa vào menu tràn,
  nên ở 1366 px hai tab "Tải dữ liệu mới" và "Nhật ký (JSON)" không mở được. Đã bỏ quy tắc ẩn, thêm kiểm thử chống tái phát.

**Đã sửa — demo, lượt 2 (theo kiểm demo độc lập bằng Playwright, 19 phát hiện)**

- **a02 tự mâu thuẫn:** bước 1 và 3 từng đưa "tim bé ≈ 130" như sự thật trong khi bước 5 bảo không dùng số đó. Khi đèn đỏ,
  bước 1 nay nêu nhịp theo đáp án và nói số máy đếm không tin được; bước 3 nói mạng đang bám nhầm tim mẹ.
- **Dải "vùng bình thường 110–160" không được vẽ:** plotly 7 bỏ qua `add_hrect` gọi trước khi ô có đường. Đã chuyển lệnh xuống sau.
- **Hộp vàng a02 nói quá:** "Cả 6 quy tắc" bỏ sót bộ chọn học (chọn dây 3). Nay ghi "6/7 cách chọn … Không cách nào chọn dây 1".
- **"Khai báo trước" gắn cho gate4:** quy tắc kế hoạch chọn là **gate 80,72** (trượt Holm). Dòng 60 bản nay nêu đủ năm số.
- Chú thích bước 1–2 không còn khẳng định tim bé luôn nhỏ và không thấy (r01 thấy rõ); bước 5 giải thích đèn xanh/vàng/đỏ
  và luật cả bản ghi đỏ. Ghi chú cổng nêu 0,721 đo ở đâu, và rằng cổng không độc lập với mạng.
- Thẻ có tên ca ("Ca dễ", "Chọn dây quyết định", "Máy bám nhầm tim mẹ", "Bốn dây đều kém"); dòng trạng thái khi đang
  phân tích; tự cuộn tới hình sau mỗi bước; thanh tóm tắt dính đáy thật; thẻ xuống hàng ở màn hẹp; thẻ "Tệp của bạn" cuộn tới phần tải tệp.
- Tải tệp: xoá kết quả cũ trước mỗi lần chạy; lỗi `.csv`/`.txt` sai cột báo bằng lời thường; phát hiện tệp nhãn bỏ nhầm vào ô
  tín hiệu; cảnh báo khi nhịp tim suy ra ngoài 80–220 (thường do nhập sai tần số lấy mẫu). Tab con đổi tên để không trùng tab ngoài.
- Chế độ chuyên gia dùng dấu phẩy thập phân; tên đường trên hình bằng lời thường; điểm tin in 4 chữ số khi trùng nhau (r01).
- Gợi ý tải CinC trong demo trỏ sai lệnh (`download_data.py` ghi vào thư mục demo không đọc); sửa thành `download_more.py --only cinc75`.
- Kiểm thử 89 → **103**.

**Đã rút thêm**

- **17,92 điểm** (khoảng cách trong/ngoài miền): tính từ mốc CinC 79,40 trên 75 bản nhiễm (`adapt/adapt_analyze.py`).
  Thay bằng 97,56 trừ số 60 bản sạch: 23,28 (PSD) · 16,84 (gate, kế hoạch chọn) · 16,55 (gate4) · 15,55 (peakprob) · 13,96 (trần).

**Đã sửa — tài liệu, lượt 3 (thẩm định tài liệu độc lập, 17/09)**

- S6 trên slide 15, 25–28, sổ tay, `TOM_TAT_30_BAI.md`, `CONG_BANG_DOI_CHUAN.md`: nêu đủ gate 80,72 (kế hoạch chọn, trượt Holm)
  bên cạnh 74,28 · 81,01 · 82,01; bỏ "gate4 là kết quả" và nhãn "khai báo trước" gắn riêng cho gate4.
- Bỏ các câu nói lại kết luận đã rút ("fetal signal absent", "rào cản không phải mô hình", a27 "gần như không có tín hiệu thai",
  "một kênh thực sự thắng bốn kênh" trên 19 chủ thể dễ chia hậu kiểm).
- DPSS 97,7 là 22 bản Silesia, không phải ADFECGDB 5 chủ thể; learned dùng số 60 bản sạch (+3,52), không dùng +2,81 (75 bản).
- KTC dải lọc thống nhất theo `pilot_evidence/band_tcn_stats.json` ([−0,04; +6,29]; [−0,51; +0,39]); self-training −0,67;
  "chắc chắn < 60" → "nhiều nhất 60"; hướng ba 96,5–99,7 / 77,8–97,97 (Castillo thuộc nhóm cổ điển); số slide trong
  kịch bản đánh lại theo HTML (31 slide).

**Đã sửa — demo, lượt 3 (kiểm demo độc lập lần hai, 17/09)**

- **Nút *Phân tích* của chế độ chuyên gia bị gắn nhầm:** vòng lặp gắn nút Tiếp/Quay lại dùng lại tên biến `btn` và ghi đè
  nút *Phân tích*, nên việc phân tích bị gắn vào nút *◀ Quay lại*; bấm *Phân tích* không ra kết quả. Đổi tên biến; nút chạy đúng.
- **Trạng thái kẹt khi lỗi:** lỗi phân tích ở chế độ trình bày không còn ném `gr.Error` (làm dòng "đang phân tích" kẹt lại);
  dòng trạng thái chuyển nền đỏ, ghi lý do và nói rõ hình bên dưới vẫn là bản ghi trước.
- **Bấm thẻ chồng nhau:** chỉ thẻ bấm sau cùng được vẽ. Lượt cũ bị bỏ qua cả khi chưa bắt đầu lẫn khi **đang tính dở**
  (`story_run` kiểm lại thẻ bấm sau cùng trước và sau khi tính). Thẩm định cuối 17/09 bắt được bản đầu chỉ kiểm trước khi
  tính, nên lượt đã bắt đầu vẫn vẽ đè; đã sửa, thêm kiểm thử.
- **Tự cuộn có điều kiện:** chỉ cuộn khi thanh 5 bước chưa nằm ở nửa trên màn hình, và không kéo người xem đã bật chế độ
  chuyên gia rồi cuộn đi chỗ khác.
- **Thanh tóm tắt dính đáy thật:** Gradio 6.26 đặt `overflow: hidden` trên `.gradio-container` nên `position: sticky` bám
  khung đó, không bám màn hình. Đã ghi đè; thanh dính khi màn hình rộng hơn 700 px, hẹp hơn thì nằm yên.
- **Màu vạch bước 3:** nhịp mạng đã báo vẽ tím đậm (trước là xanh lá, trùng màu "đúng" ở hàng dưới, trong khi chú thích
  ghi "vạch đỏ"). Chú thích và tiêu đề hình: *vạch tím đậm là nhịp mạng đã báo, chưa biết đúng hay sai*.
- **Chú thích đèn xanh không nói quá:** bước 5 ghi *xanh là cổng không thấy dấu hiệu xấu* và *Xanh không bảo đảm là đúng*,
  kèm 82 bản đã chấm / 3 bản xanh F1 dưới 90 / thấp nhất 17,02 đọc từ `demo/results/demo_check_2modes.json`. Đèn đỏ thì
  đường trung bình trên hình ghi *TB … nhịp/phút (đèn đỏ: không dùng)*.
- **Tiêu đề "một kênh":** *RelyFetal — tìm nhịp tim thai trong điện tim đo trên bụng mẹ, chỉ cần một kênh* (bỏ "nghe tim thai
  từ một điện cực"); phụ đề nói bản ghi thử có 4 kênh, máy tự chọn một, và báo "tôi không chắc" khi thấy dấu hiệu tín hiệu
  xấu (không phải lần nào cũng thấy).
- **Nhãn F1** ở thanh tóm tắt: *F1 (bắt đủ và báo đúng, 100 là hoàn hảo)*, thay "độ đúng".
- **Câu bước 1 theo biên độ thật:** hộp *Cách đọc hình* đo tỉ số gai bé / gai mẹ trên chính bản ghi (ngưỡng 0,5): r01 dây 4
  gai bé to ngang gai mẹ; a09, a02, a27 gai bé nhỏ hơn nhiều. Chú thích bước 2 và 4 sửa theo; dòng mô tả thẻ CinC bỏ
  "máy ghi khác, nơi khác", chỉ ghi không trùng dữ liệu huấn luyện và nguồn thiết bị từng bản không được công bố.
- **Tải tệp báo lỗi ở dòng trạng thái:** không còn hộp "Error"; ghi *Không phân tích được tệp. … Kết quả cũ đã được xoá;
  sửa tệp rồi bấm Phân tích lại.* Chi tiết kỹ thuật chỉ in ra cửa sổ dòng lệnh.
- **Số kiểu Việt ở chế độ chuyên gia:** thẻ đèn, bảng kênh (điểm PSD dạng `7,14·10^0`), dòng trạng thái, tab *Dữ liệu của
  nhóm*; câu CinC 60 bản nêu đủ năm số và "tương quan chéo tối đa 0,62"; hướng dẫn đọc hình thô không còn khẳng định gai
  thai luôn nhỏ. Thẩm định cuối 17/09 tìm thêm năm chỗ còn kiểu máy (chú thích "Xem tín hiệu thô" `60.0 s` / `1,234 ms`, lỗi tệp
  quá ngắn `5.00 s`, vạch ngưỡng `0.052`, điểm PSD `1,7e+01`, dấu phân cách đôi ở tiêu đề hình kênh); đã sửa cả năm.
  Còn lại có chủ ý: hình 5 tầng và đơn vị *bpm* trên các hình của chế độ chuyên gia.
- **Lý do của đèn mô tả đúng 6/4/2 chỉ số** (`fsqi/gate.py`): 6 thuần tín hiệu, 4 tính trên nhịp mạng tìm ra, 2 là xác suất
  của mạng; ngưỡng in ba chữ số (0,052 / 0,540), dấu % cách số.
- **Ngưỡng cảnh báo nhịp tim khi tải tệp: 100–200** theo luật cứng của đèn (`demo/core.py: CONF_RULE`), thay 80–220.
- Kiểm thử 103 → **109** (43 trong `tests/` + 66 trong `demo/test_core.py`, trong đó 22 của chế độ trình bày; đếm bằng
  `python -m pytest --collect-only -q tests/ demo/test_core.py`).
- Tài liệu đồng bộ theo giao diện mới: `docs/HUONG_DAN_DEMO_v2.md` (329/329 chuỗi nghiêng khớp mã hoặc chuỗi hiển thị thật;
  thêm hỏi đáp "đèn xanh mà vẫn sai" với a57 F1 17,02, và "vì sao lúc nhanh lúc chậm"), `docs/KICH_BAN_THUYET_TRINH_v2.md`,
  slide, sổ tay, `docs/NOI_DUNG_SLIDE.md`, `docs/TOM_TAT_1_TRANG.md`, `HANDOFF.md`, README.

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
