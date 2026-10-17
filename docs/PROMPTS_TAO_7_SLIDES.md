# BỘ 7 PROMPT TẠO SLIDE THUYẾT TRÌNH ĐỒNG BỘ (RATIO 16:9)
**Đề tài:** RelyFetal — Dò phức bộ QRS thai nhi từ điện tim ổ bụng đơn kênh có cổng từ chối  
**Phong cách chủ đạo:** Modern Medical Deep-Tech (Công nghệ Y tế Chuyên sâu, Tối giản, Chữ to rõ, Tương phản cao)  
**Tỉ lệ khung hình:** Widescreen 16:9 (1920x1080 hoặc 3840x2160)  
**Tập tin tương ứng:** [`docs/SLIDES_TRINH_BAY_7_SLIDES.md`](file:///Users/xuannguyen/Desktop/Competitions/NCKH%20-%202026/nckhsv_tdtu2026-2027/docs/SLIDES_TRINH_BAY_7_SLIDES.md)

---

## 🎨 HƯỚNG DẪN THIẾT KẾ ĐỒNG BỘ (DESIGN SYSTEM GUIDE)

Trước khi nhập từng prompt, hãy áp dụng quy chuẩn phong cách chung này cho toàn bộ 7 slide (trong Gamma.app, Beautiful.ai, Canva, Midjourney hoặc ChatGPT Plus):

* **Tông màu chủ đạo (Color Palette):**
  * Nền: Xanh thẫm y tế cao cấp (Deep Navy `#0B132B` hoặc Slate `#0F172A`).
  * Màu nhấn tích cực / Thành công: Ngọc lục bảo sáng (Emerald Green `#10B981`).
  * Màu nhấn công nghệ: Xanh lơ dạ quang (Electric Cyan `#06B6D4`).
  * Màu cảnh báo / Cổng từ chối: Đỏ san hô (Coral Red `#EF4444`) & Vàng hổ phách (Amber `#F59E0B`).
  * Chữ & Thẻ nội dung: Trắng tuyết `#FFFFFF` và Xám khói nhạt `#E2E8F0` trên nền thẻ mờ viền kính (Glassmorphism card `#1E293B` với viền `1px solid rgba(255,255,255,0.1)`).
* **Quy tắc Typography (Chữ to, rõ ràng, dễ đọc từ xa):**
  * Font chữ: Sans-serif hiện đại (Inter, SF Pro Display, Montserrat, hoặc Roboto).
  * Tiêu đề chính: 38pt – 44pt, in đậm (Bold/ExtraBold).
  * Chỉ số / KPI Cards: 48pt – 64pt, màu Emerald Green hoặc Cyan nổi bật.
  * Tiêu đề phụ / Đề mục thẻ: 20pt – 24pt, Semi-Bold.
  * Nội dung chi tiết: 16pt – 18pt, khoảng cách dòng thoáng (Line height 1.5), tối đa 3–4 gạch đầu dòng mỗi thẻ.

---

## PROMPT SLIDE 1: ĐẶT VẤN ĐỀ & TUYỂN CHỌN DỮ LIỆU LÂM SÀNG NGHIÊM NGẶT

### Thông tin Slide
* **Tiêu đề:** ĐẶT VẤN ĐỀ & TUYỂN CHỌN DỮ LIỆU LÂM SÀNG
* **Phụ đề:** Loại bỏ triệt để rò rỉ dữ liệu và nhãn sai lệch trong y văn để xây dựng mô hình tin cậy
* **Bố cục 16:9:** Chia 2 cột (Cột trái: Thách thức tín hiệu & Hình ảnh so sánh; Cột phải: 3 thẻ tuyển chọn dữ liệu ADFECGDB, Silesia, CinC 2013).

### Nội dung Prompt (Copy vào công cụ tạo Slide / AI)
```text
Tạo một slide thuyết trình tỉ lệ 16:9 theo phong cách Modern Medical Deep-Tech, nền xanh thẫm (Deep Navy #0B132B), chữ trắng to rõ, bố cục 2 cột cân đối:

TIÊU ĐỀ SLIDE:
- Tiêu đề chính (42pt, Bold, Màu trắng): ĐẶT VẤN ĐỀ & TUYỂN CHỌN DỮ LIỆU LÂM SÀNG
- Tiêu đề phụ (20pt, Regular, Màu Cyan #06B6D4): Kiểm toán tính toàn vẹn của dữ liệu y sinh — Nền tảng cho mô hình AI y tế đáng tin cậy

CỘT TRÁI (THÁCH THỨC LÂM SÀNG & TÍN HIỆU):
- Một thẻ lớn viền kính nổi bật:
  + Tiêu đề thẻ (24pt): Tín hiệu fECG bị che lấp hoàn toàn
  + Gạch đầu dòng (18pt):
    * Tín hiệu tim thai cực nhỏ (10–50 µV), bị tim mẹ lớn gấp 5–10 lần (200–1000 µV) lấn át (SNR từ -5 dB đến -25 dB).
    * Bị nhiễu cơ bụng (EMG), nhiễu hô hấp và dịch chuyển điện cực do cử động thai.
    * Đa số nghiên cứu đòi hỏi nhiều kênh bụng hoặc kênh ngực mẹ -> Gây cồng kềnh, khó theo dõi tại nhà.
- Hình ảnh minh họa bên dưới thẻ: Đồ thị dạng sóng ECG 1 kênh bụng thực tế hiển thị đỉnh nhịp mẹ (mQRS) cao vượt trội và đỉnh nhịp thai (fQRS) nhấp nhô li ti bị chìm trong nhiễu.

CỘT PHẢI (3 HỘP DỮ LIỆU ĐÃ KIỂM TOÁN):
- Hộp 1 (Viền xanh ngọc #10B981): 
  + Tiêu đề: PhysioNet ADFECGDB (Chuẩn vàng)
  + Nội dung: 5 ca chuyển dạ, 4 kênh bụng, 1000 Hz. Nhãn chuẩn xác 100% từ điện cực da đầu thai nhi (Direct scalp ECG).
- Hộp 2 (Viền xanh dương #3B82F6): 
  + Tiêu đề: Silesia NIFECG (22 ca, 500 Hz)
  + Nội dung: Đối soát và LOẠI BỎ 5 ca trùng bản sao PhysioNet (B2_01, B2_02, B2_07, B2_10, B2_11) để tránh kiểm thử thiên lệch.
- Hộp 3 (Viền đỏ san hô #EF4444 cảnh báo): 
  + Tiêu đề: PhysioNet CinC 2013 (75 ca) — Kiểm toán rò rỉ
  + Nội dung: Phát hiện 15 ca rò rỉ (bản sao nguyên văn ADFECGDB, NCC = 1.000) và 7 ca chú thích sai đã công bố trong y văn -> Giữ lại ĐÚNG 60 BẢN SẠCH để kiểm thử độc lập khách quan.

DƯỚI CÙNG (Dải băng tóm tắt):
- Chuẩn hóa đầu vào hệ thống: 1 kênh bụng duy nhất, tần số lấy mẫu chuẩn fs = 250 Hz (chuẩn Behar 2014).
```

---

## PROMPT SLIDE 2: KIẾN TRÚC MÔ HÌNH FetalQRS-TCN & KỸ THUẬT PHÁT TRIỂN

### Thông tin Slide
* **Tiêu đề:** KIẾN TRÚC MÔ HÌNH FetalQRS-TCN
* **Phụ đề:** Mạng tích chập giãn nở chuỗi-sang-chuỗi — Trường tiếp nhận dài 1.5s với chỉ 113.481 tham số
* **Bố cục 16:9:** Bên trái là sơ đồ khối luồng kiến trúc mạng TCN 5 khối; Bên phải là 3 thẻ phân tích thực nghiệm then chốt (Ablation studies) kèm 3 thẻ KPI lớn.

### Nội dung Prompt (Copy vào công cụ tạo Slide / AI)
```text
Tạo một slide thuyết trình tỉ lệ 16:9 phong cách Modern Medical Tech, nền tối xanh đen, đồ họa vector sắc nét, chữ to rõ:

TIÊU ĐỀ SLIDE:
- Tiêu đề chính (42pt, Bold, Màu trắng): KIẾN TRÚC MÔ HÌNH FetalQRS-TCN
- Tiêu đề phụ (20pt, Regular, Màu Cyan): Thiết kế chuỗi-sang-chuỗi tối ưu hóa trường tiếp nhận sinh lý trên thiết bị tài nguyên giới hạn

PHẦN TRÊN (3 THẺ KPI NỔI BẬT):
- Thẻ 1: 113.481 Tham số (Kích thước mô hình chỉ 0.48 MB — nhỏ hơn SOTA 81 lần)
- Thẻ 2: 1.516 ms (Trường tiếp nhận sinh lý 1.51 giây, bao trọn 3–4 nhịp thai và 2 nhịp mẹ)
- Thẻ 3: 1.0 ms Jitter (Sai số định thời cực thấp nhờ Heatmap xác suất theo từng mẫu)

CỘT TRÁI (SƠ ĐỒ KIẾN TRÚC DẠNG VECTOR NỔI BẬT):
Vẽ sơ đồ khối luồng tín hiệu từ trên xuống dưới dạng sơ đồ công nghệ vi mạch phát sáng:
1. Đầu vào: Tín hiệu 2 kênh x 1000 mẫu @ 250 Hz (Tín hiệu thô + Tín hiệu sau khử mẹ)
2. Khối Stem: Conv1D (k=7, 40 kênh đặc trưng) -> Receptive Field (RF) = 28 ms
3. Chuỗi 5 khối Dilated Residual Blocks (k=7, 40 kênh, GELU, BatchNorm1D):
   - Block 1 (d=1) -> RF = 124 ms
   - Block 2 (d=2) -> RF = 316 ms
   - Block 3 (d=4) -> RF = 700 ms
   - Block 4 (d=8) -> RF = 1468 ms
   - Block 5 (d=16) -> RF = 1516 ms (Đạt trần sinh lý tim học)
4. Đầu ra: Conv1D 1x1 + Sigmoid -> Heatmap xác suất từng mẫu (Gaussian σ = 12 ms).

CỘT PHẢI (3 PHÁT HIỆN THỰC NGHIỆM ĐỊNH HÌNH THIẾT KẾ):
- Thẻ 1 (Khảo sát 16 kiến trúc): Thay đổi họ mô hình (MLP, ResNet, U-Net, Transformer) chỉ chênh 2.55 điểm F1 (p = 0.7012 không ý nghĩa), trong khi Transformer chạy chậm hơn 21.7 lần.
- Thẻ 2 (Quét trường tiếp nhận RF): Kéo dài RF từ 172 ms lên 1.516 ms tăng vọt F1 từ 92.67% lên 97.16% (p < 0.0001). Vượt 1.5s F1 bão hòa. TCN là giải pháp rẻ nhất để đạt RF dài.
- Thẻ 3 (Hồi quy Heatmap từng mẫu): Giảm sai số định thời từ 5.6–6.0 ms (phân loại cửa sổ) xuống 1.0 ms, giải quyết triệt để bài toán định vị đỉnh nhịp tim thai.
```

---

## PROMPT SLIDE 3: KỸ THUẬT XỬ LÝ TÍN HIỆU & CỔNG TỪ CHỐI TIN CẬY (REJECTION GATE)

### Thông tin Slide
* **Tiêu đề:** XỬ LÝ TÍN HIỆU & CỔNG TỪ CHỐI TIN CẬY
* **Phụ đề:** Kết hợp hài hòa xử lý tín hiệu kinh điển, chọn kênh mù nhãn và cơ chế tự động từ chối
* **Bố cục 16:9:** Hàng trên là quy trình xử lý tín hiệu 4 bước (Pipelines); Hàng dưới là giao diện Cổng tin cậy 3 màu (Đèn Xanh / Vàng / Đỏ) kèm biểu đồ dạng sóng.

### Nội dung Prompt (Copy vào công cụ tạo Slide / AI)
```text
Tạo một slide thuyết trình tỉ lệ 16:9 chủ đề Y sinh, nền xanh thẫm, các khối trực quan dạng thẻ kính, chữ to rõ:

TIÊU ĐỀ SLIDE:
- Tiêu đề chính (42pt, Bold): XỬ LÝ TÍN HIỆU & CỔNG TỪ CHỐI TIN CẬY
- Tiêu đề phụ (20pt, Cyan): Khử mẹ thích nghi, chọn kênh mù nhãn và cơ chế an toàn lâm sàng theo đoạn 4 giây

NỬA TRÊN (QUY TRÌNH XỬ LÝ TÍN HIỆU 4 BƯỚC):
Thiết kế 4 bước dạng thẻ ngang liên kết bằng mũi tên công nghệ:
- Bước 1: Tiền xử lý 10–60 Hz (Butterworth bậc 4 pha không + Notch 50Hz). Thực nghiệm chứng minh dải 10–60 Hz tăng +11.0 điểm F1 so với dải 1–45 Hz truyền thống, triệt trôi đẳng điện và sóng T mẹ.
- Bước 2: Khử QRS mẹ bằng Median Template (MTS). Lập khuôn mẫu trung vị từ các nhịp mẹ, co giãn biên độ bình phương tối thiểu kẹp [0.3; 3.0] thích nghi từng nhịp, không cần kênh ngực mẹ.
- Bước 3: Chọn kênh mù nhãn (Blind Lead Selection). Tự động chọn kênh bụng tối ưu qua 'peakprob' (độ nét xác suất mô hình) hoặc 'PSD' (tỷ số phổ dải 1.8–3.0 Hz), hoàn toàn không cần nhãn thật.
- Bước 4: Dò đỉnh & Ước lượng fHR. Lấy đỉnh thích nghi với thời gian trơ 250 ms, ước lượng nhịp tim thai fHR (bpm) theo cửa sổ trượt.

NỬA DƯỚI (HỆ THỐNG CỔNG TIN CẬY & ĐÈN BÁO 3 MÀU):
Bố cục 3 hộp đèn tín hiệu trực quan sinh động:
- Đèn Xanh (Green #10B981): Tín hiệu chất lượng cao, fHR ổn định sinh lý (110–160 bpm) -> Cho phép hiển thị kết quả đo cho bác sĩ.
- Đèn Vàng (Amber #F59E0B): Tín hiệu có nhiễu nhẹ, biến thiên nhịp nhanh -> Cảnh báo bác sĩ cần theo dõi thêm.
- Đèn Đỏ (Red #EF4444 - Cực kỳ quan trọng): Tín hiệu suy biến, mất tiếp xúc, HOẶC phát hiện tỷ lệ bám nhịp mẹ >= 60% -> HỆ THỐNG TỪ CHỐI TRẢ LỜI, khóa hiển thị fHR ảo để bảo đảm an toàn sinh mạng thai nhi.
```

---

## PROMPT SLIDE 4: PHƯƠNG PHÁP ĐÁNH GIÁ CHUẨN MỰC Y VĂN QUỐC TẾ

### Thông tin Slide
* **Tiêu đề:** PHƯƠNG PHÁP ĐÁNH GIÁ CHUẨN MỰC QUỐC TẾ
* **Phụ đề:** Tuân thủ quy ước PhysioNet / CinC 2013 / AAMI — Khắt khe và công bằng học thuật
* **Bố cục 16:9:** Cột trái là sơ đồ trực quan thuật toán ghép cặp tham lam 1-1 với dung sai ±50ms; Cột phải là hệ thống công thức và bảng đối chiếu "Chuẩn mực vs Bẫy số liệu ảo".

### Nội dung Prompt (Copy vào công cụ tạo Slide / AI)
```text
Tạo một slide thuyết trình tỉ lệ 16:9 chủ đề Nghiên cứu khoa học chuẩn quốc tế, nền xanh thẫm, các ô đồ họa tương phản cao:

TIÊU ĐỀ SLIDE:
- Tiêu đề chính (42pt, Bold): PHƯƠNG PHÁP ĐÁNH GIÁ CHUẨN MỰC QUỐC TẾ
- Tiêu đề phụ (20pt, Cyan): Quy chuẩn PhysioNet, CinC 2013 và AAMI — Nói không với các thủ thuật thổi phồng số liệu

CỘT TRÁI (SƠ ĐỒ GHÉP CẶP SỰ KIỆN THAM LAM 1-1):
- Vẽ sơ đồ thời gian (Timeline):
  + Trục thời gian với các vạch đỏ (Đỉnh nhãn thật - Reference) và vạch xanh (Đỉnh mô hình dò - Detection).
  + Khung dung sai vàng ±50 ms (tương đương ±12 mẫu tại 250 Hz hoặc ±50 mẫu tại 1000 Hz).
  + Minh họa trực quan:
    * Đúng (True Positive - TP): Đỉnh xanh rơi vào vùng dung sai ±50 ms quanh đỉnh đỏ.
    * Sai thừa (False Positive - FP): Đỉnh xanh nằm ngoài vùng dung sai hoặc bị ghép trùng.
    * Sai thiếu (False Negative - FN): Đỉnh đỏ không có đỉnh xanh nào ghép cặp.

CỘT PHẢI (CÔNG THỨC ĐỊNH LƯỢNG & BẢO VỆ TÍNH TRUNG THỰC):
- Hộp công thức (Chữ to, rõ ràng, định dạng toán học đẹp):
  * Độ nhạy: Se = TP / (TP + FN) x 100%
  * Độ chuẩn xác: PPV = TP / (TP + FP) x 100%
  * Điểm F1-score: F1 = 2 x (Se x PPV) / (Se + PPV)
  * Độ lệch thời gian (Jitter): Mean(|t_det - t_ref|) tính bằng mili-giây (ms).

- Bảng đối chiếu cảnh báo (2 cột nhỏ tương phản):
  * CỘT ĐỎ (CÁC BẪY SỐ LIỆU PHỔ BIẾN Ở BÀI BÁO KHÁC):
    - Dùng dung sai lỏng lẻo ±500 ms (thổi phồng F1 từ 59% lên 91%).
    - Rò rỉ bệnh nhân: Cắt ngẫu nhiên cửa sổ train/test trên cùng 1 ca.
    - Chọn kênh bằng Oracle (dùng nhãn thật để chọn kênh tốt trước khi test).
  * CỘT XANH (CAM KẾT CỦA RELYFETAL):
    - Dung sai chuẩn mực y văn: ĐÚNG ±50 ms.
    - Kiểm thử ngoại trừ đối tượng (LORO) hoàn toàn độc lập.
    - Chọn kênh mù nhãn hoàn toàn không biết trước nhãn.
```

---

## PROMPT SLIDE 5: BENCHMARK ĐỐI SÁNH TRỰC QUAN VỚI CÁC MÔ HÌNH SOTA

### Thông tin Slide
* **Tiêu đề:** BENCHMARK ĐỐI SÁNH TRỰC QUAN VỚI SOTA
* **Phụ đề:** FetalQRS-TCN vs. SCTD-Net (IEEE JBHI 2025), R2W-Net, DPSS, 1D-CycleGAN
* **Bố cục 16:9:** Bảng đối sánh số liệu trung tâm chiếm 65% diện tích; Cột phải hoặc hàng dưới gồm 3 biểu đồ thanh / huy hiệu so sánh kích thước và độ phức tạp tính toán.

### Nội dung Prompt (Copy vào công cụ tạo Slide / AI)
```text
Tạo một slide thuyết trình tỉ lệ 16:9 phong cách Báo cáo Benchmark Y tế chuyên sâu, nền tối sang trọng, bảng dữ liệu nổi bật, chữ số to rõ:

TIÊU ĐỀ SLIDE:
- Tiêu đề chính (42pt, Bold): BENCHMARK ĐỐI SÁNH TRỰC QUAN VỚI CÁC MÔ HÌNH SOTA
- Tiêu đề phụ (20pt, Cyan): Hiệu năng vượt trội trong ngân sách tài nguyên siêu nhỏ gọn

PHẦN TRUNG TÂM (BẢNG BENCHMARK SOTA TO RÕ):
Bảng kẻ viền hiện đại, làm nổi bật hàng của FetalQRS-TCN bằng khung viền xanh ngọc Emerald sáng:

| Mô hình / Tác giả | Kiến trúc & Số kênh | Số tham số | Dung lượng | GFLOPs | F1 ADFECGDB (±50ms) | F1 CinC 2013 (Zero-shot) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SCTD-Net (Asadi 2025, IEEE JBHI) | 1D U-Net + 2D Ursa-Net (1 kênh) | 9.220.000 | 111.8 MB | 4.63 | 96.52% | 97.97% (80 kênh lọc) |
| Attention R2W-Net (Chen 2025, IEEE) | 2x R2U-Net + Attn (1 kênh) | Không nêu | ~25.0 MB | ~2.10 | 99.17% (nghi rò rỉ) | 98.03% |
| DPSS (Shokouhmand 2023, IEEE JBHI) | GAN + DP-LSTM (1 kênh) | Không nêu | ~40.0 MB | ~1.85 | 97.70% | 95.30% (chọn tay) |
| 1D-CycleGAN (Basak 2024, Elsevier) | ResNet 13 blocks (4 kênh bụng) | 762.000 | 3.1 MB | 0.85 | 96.40% | Chưa công bố |
| FetalQRS-TCN (Nhóm đề xuất) | Dilated Residual TCN (1 kênh) | 113.481 | 0.48 MB | 0.11 | 97.16% (Kênh tốt: 99.18%) | 77.52% (60 bản sạch) |

PHẦN DƯỚI (3 THẺ ĐỐI SÁNH TRỰC QUAN NHANH):
- Thẻ 1 (Màu xanh ngọc #10B981): Nhẹ hơn SCTD-Net 81 LẦN (113k vs 9.22M tham số; 0.48 MB vs 111.8 MB).
- Thẻ 2 (Màu Cyan #06B6D4): Tính toán thấp hơn 42 LẦN (0.11 GFLOPs vs 4.63 GFLOPs), cho phép chạy mượt trên CPU đơn nhân.
- Thẻ 3 (Màu Vàng Amber #F59E0B): Độ chính xác thực chất: F1 97.16% (kênh lâm sàng tốt đạt 99.18%, Jitter 3.05 ms). Con số 77.52% trên CinC 2013 phản ánh đúng độ khó xuyên miền (tương đương Complex U-Net 77.8% của Orvas 2025).
```

---

## PROMPT SLIDE 6: PHƯƠNG HƯỚNG PHÁT TRIỂN & PHƯƠNG PHÁP GIẢ LẬP MẠCH NHÚNG

### Thông tin Slide
* **Tiêu đề:** PHƯƠNG HƯỚNG PHÁT TRIỂN & GIẢ LẬP MẠCH NHÚNG
* **Phụ đề:** Thiết kế thiết bị đeo biên (Edge Wearable) & Phương pháp giả lập ràng buộc phần cứng trên máy tính
* **Bố cục 16:9:** Cột trái là Thiết kế phần cứng mục tiêu (Patch dán bụng, Vi điều khiển MCU); Cột phải là Phương pháp 3 bước giả lập mạch nhúng trên máy tính.

### Nội dung Prompt (Copy vào công cụ tạo Slide / AI)
```text
Tạo một slide thuyết trình tỉ lệ 16:9 chủ đề Phần cứng nhúng y tế (Embedded Medical Hardware), nền xanh thẫm công nghệ, chữ to rõ:

TIÊU ĐỀ SLIDE:
- Tiêu đề chính (42pt, Bold): PHƯƠNG HƯỚNG PHÁT TRIỂN & GIẢ LẬP MẠCH NHÚNG
- Tiêu đề phụ (20pt, Cyan): Lộ trình đưa AI lên vi điều khiển giá rẻ & Phương pháp kiểm chứng giả lập

CỘT TRÁI (PHẦN CỨNG MỤC TIÊU - WEARABLE EMBEDDED PATCH):
- Hình ảnh / Đồ họa minh họa: Bản vẽ thiết bị Patch dán bụng thông minh 1 kênh thu nhỏ gọn gàng gắn trên bụng sản phụ, kết nối không dây Bluetooth với điện thoại.
- 2 Vi điều khiển mục tiêu với chi phí tối ưu:
  + STM32H743VIT6: ARM Cortex-M7 @ 480 MHz, 2 MB Flash, 1 MB SRAM (Giá ~10 USD) — Dành cho thiết bị y tế chuyên dụng.
  + ESP32-S3: Xtensa Dual-Core 32-bit @ 240 MHz, tích hợp Wi-Fi/BLE, 512 KB SRAM (Giá ~3 USD) — Dành cho thiết bị theo dõi tại nhà giá rẻ.

CỘT PHẢI (PHƯƠNG PHÁP GIẢ LẬP RÀNG BUỘC PHẦN CỨNG TRÊN MÁY TÍNH):
Trình bày 3 bước giả lập môi trường nhúng nghiêm ngặt trực tiếp trên máy tính:
- Bước 1: Khóa thực thi đơn luồng (Single-Thread CPU Throttling):
  Ép mô hình chạy trên đúng 1 nhân CPU duy nhất (torch.set_num_threads(1)), vô hiệu hóa hoàn toàn GPU/NPU và đa luồng song song để mô phỏng chính xác vi xử lý nhúng.
- Bước 2: Lượng tử hóa đối xứng INT8 (Symmetric INT8 Quantization):
  Chuyển đổi toàn bộ trọng số float 32-bit (FP32) sang số nguyên 8-bit (INT8) trong dải [-127, 127] theo chuẩn của ARM CMSIS-NN và TensorFlow Lite Micro.
- Bước 3: Mô phỏng bộ đệm trượt & Đo bộ nhớ cực đại (Sliding-window Profiling):
  Nạp tín hiệu theo từng cửa sổ 4 giây (1000 mẫu @ 250 Hz), đo lường chính xác dung lượng Flash (ROM) và RAM đệm hoạt động (Activation RAM).
```

---

## PROMPT SLIDE 7: KẾT QUẢ THỰC NGHIỆM GIẢ LẬP & BÁO CÁO ĐO LƯỜNG PHẦN CỨNG

### Thông tin Slide
* **Tiêu đề:** KẾT QUẢ THỰC NGHIỆM GIẢ LẬP MẠCH NHÚNG
* **Phụ đề:** Báo cáo đo lường độ chính xác, tốc độ và mức tiêu thụ tài nguyên thực tế
* **Bố cục 16:9:** Nửa trên là Bảng số liệu đo đạc thực tế (FP32 vs INT8); Nửa dưới là 3 khối phân tích: Tốc độ thời gian thực (RTF), Bộ nhớ phần cứng, và Tiết kiệm năng lượng (Pin).

### Nội dung Prompt (Copy vào công cụ tạo Slide / AI)
```text
Tạo một slide thuyết trình tỉ lệ 16:9 phong cách Báo cáo thực nghiệm khoa học, nền tối, hiển thị bảng đo lường và các biểu đồ KPI thực tế:

TIÊU ĐỀ SLIDE:
- Tiêu đề chính (42pt, Bold): KẾT QUẢ THỰC NGHIỆM GIẢ LẬP MẠCH NHÚNG
- Tiêu đề phụ (20pt, Cyan): Số liệu đo đạc thực nghiệm từ bài test giả lập vi điều khiển đơn luồng và lượng tử hóa INT8

NỬA TRÊN (BẢNG ĐO LƯỜNG THỰC TẾ TRÊN MÁY):
Bảng so sánh 3 cột viền kính nổi bật:

| Tiêu chí đo đạc | Bản gốc (FP32) | Bản lượng tử hóa (INT8) | Mức cải thiện / Dung sai |
| :--- | :---: | :---: | :---: |
| Bộ nhớ Flash / ROM | 443.3 KB | 110.8 KB | Tiết kiệm 75.0% Flash (vừa vặn mọi MCU) |
| Bộ nhớ RAM đệm (Activations) | 320.0 KB | 80.0 KB | Giảm 4 lần, vừa vặn trong 512KB SRAM |
| Thời gian suy luận TCN (4s ECG) | 5.12 ms | 4.98 ms | Nhanh hơn thời gian thực 781.6 LẦN |
| Thời gian toàn bộ Pipeline (4s ECG) | 37.42 ms | 35.10 ms | Nhanh hơn thời gian thực 106.9 LẦN |
| Độ chính xác F1 (Ca r01) | 100.00% | 100.00% | KHÔNG ĐỔI (Suy hao 0.00%) |
| Sai số định thời Jitter (Ca r01) | 1.59 ms | 1.61 ms | Chênh lệch chỉ 0.02 ms (không đáng kể) |

NỬA DƯỚI (3 ĐÁNH GIÁ ĐỊNH LƯỢNG VỀ TÍNH KHẢ THI PHẦN CỨNG):
- Thẻ 1 (Tốc độ vượt trội - RTF 106.9x): Xử lý 4 giây tín hiệu chỉ mất 37.4 ms trên 1 luồng CPU. Đảm bảo hiển thị nhịp tim thai tức thời không có độ trễ cảm nhận.
- Thẻ 2 (Bộ nhớ siêu tiết kiệm): 110.8 KB Flash chỉ chiếm 5.5% bộ nhớ của chip STM32H7 (2MB) và 80 KB RAM đệm hoàn toàn vừa vặn trong 512KB SRAM của ESP32-S3 mà không cần gắn thêm chip nhớ ngoài.
- Thẻ 3 (Thời lượng pin dài - 99% Deep Sleep): Do thời gian tính toán chỉ chiếm < 1% thời gian thực (37.4 ms trong mỗi chu kỳ 4000 ms), vi điều khiển có thể chuyển sang chế độ ngủ sâu (Low-power Deep Sleep) trong 99% thời gian còn lại -> Giúp thiết bị chạy pin liên tục nhiều tuần.

KẾT LUẬN CUỐI SLIDE:
Mô hình FetalQRS-TCN hoàn toàn sẵn sàng 100% để nạp vào mạch nhúng thực tế mà không cần chip tăng tốc AI đắt tiền.
```

---

## 💡 HƯỚNG DẪN SỬ DỤNG NHANH

1. **Dùng với Gamma.app:** Chọn `New with AI` -> `Paste in text` -> Dán lần lượt nội dung của từng Slide vào, chọn giao diện màu `Dark Navy / Emerald Tech`.
2. **Dùng với ChatGPT (GPT-4o / DALL-E) hoặc Midjourney:** Dán nguyên văn từng prompt trên để tạo ảnh mockup slide 16:9 với câu lệnh `--ar 16:9`.
3. **Dùng với Canva / PowerPoint:** Copy trực tiếp tiêu đề, cấu trúc gạch đầu dòng và số liệu từ bảng vào các slide template chủ đề Medical / Technology.
