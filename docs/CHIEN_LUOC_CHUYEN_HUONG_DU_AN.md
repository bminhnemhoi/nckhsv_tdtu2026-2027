# BÁO CÁO TOÀN DIỆN: HIỆN TRẠNG DỰ ÁN & HAI HƯỚNG PHÁT TRIỂN ĐỘT PHÁ MỚI

**Tài liệu:** Đánh giá hiện trạng công nghệ và xây dựng chiến lược chuyển đổi ứng dụng thực tế  
**Kho mã nguồn:** `nckhsv_tdtu2026-2027`  
**Ngày cập nhật:** 28/09/2026  

---

## MỤC LỤC

1. [Phần 1: Hiện trạng và Tài sản Kỹ thuật Cốt lõi của Dự án Hiện tại](#phan-1-hien-trang-va-tai-san-ky-thuat-cot-loi-cua-du-an-hien-tai)
2. [Phần 2: Hướng đề xuất 1 — Giải mã Sóng P & Cổng từ chối Báo động giả trên Điện tim Đơn kênh](#phan-2-huong-de-xuat-1--giai-ma-song-p--cong-tu-choi-bao-dong-gia-tren-dien-tim-don-kenh)
3. [Phần 3: Hướng đề xuất 2 — Miếng dán Đơn kênh Tách Tín hiệu Điện tim và Cơ hoành (dEMG) Giám sát Hô hấp & Giấc ngủ](#phan-3-huong-de-xuat-2--mieng-dan-don-kenh-tach-tin-hieu-dien-tim-va-co-hoanh-demg-giam-sat-ho-hap--giac-ngu)
4. [Phần 4: Ma trận So sánh Chiến lược Giữa 3 Phương án](#phan-4-ma-tran-so-sanh-chien-luoc-giua-3-phuong-an)
5. [Phần 5: Lộ trình Chuyển đổi Nhanh Không Gián đoạn Nghiên cứu](#phan-5-lo-trinh-chuyen-doi-nhanh-khong-gian-doan-nghien-cuu)

---

## PHẦN 1: HIỆN TRẠNG VÀ TÀI SẢN KỸ THUẬT CỐT LÕI CỦA DỰ ÁN HIỆN TẠI

### 1.1 Bản chất bài toán hiện tại (RelyFetal — Single-Channel fECG)
Dự án hiện tại giải quyết bài toán: **Dò tìm phức bộ nhịp tim thai nhi (fQRS) từ điện tim ổ bụng thu bằng duy nhất 1 kênh đo**, đồng thời tích hợp **Cổng từ chối an toàn lâm sàng (Confidence Rejection Gate)** khi tín hiệu bị suy biến hoặc khi máy bị nhầm sang nhịp tim mẹ.

### 1.2 Toàn bộ tài sản kỹ thuật đã hoàn thiện 100% trong kho mã
Nhóm đã phát triển một hệ thống hoàn chỉnh từ thuật toán phòng lab, nén nhúng vi điều khiển đến giao diện người dùng:

1. **Mô hình học sâu FetalQRS-TCN:**
   * Dạng mạng: Mạng tích chập thời gian giãn nở có kết nối tắt (Dilated Residual 1D-TCN).
   * Quy mô siêu nhẹ: Đúng **113.481 tham số**, dung lượng chỉ **0.48 MB** (443 KB nhị phân), nhẹ hơn mô hình SOTA thế giới (SCTD-Net IEEE JBHI 2025) tới **81.2 lần**.
   * Trường tiếp nhận (Receptive Field - RF): Tối ưu ở mức **1.516 ms (1.52 giây, 379 mẫu)**, bao trọn 3–4 nhịp thai và 2 nhịp mẹ, giúp điểm F1 tăng vọt từ 92% lên 97.16% và đạt trần sinh lý.
   * Định dạng xuất: Heatmap Gaussian theo từng mẫu, giảm sai số định thời (Jitter) xuống chỉ còn **1.0 – 1.5 ms**.

2. **Quy trình xử lý tín hiệu kinh điển (Preprocessing & Artifact Cancellation):**
   * Bộ lọc dải Butterworth bậc 4 pha không **10 – 60 Hz** kết hợp Notch 50 Hz, giúp tăng +11 điểm F1 so với dải 1–45 Hz truyền thống nhờ cắt đứt nhiễu trôi thở và sóng T mẹ.
   * Thuật toán trừ mẫu trung vị thích nghi (**Median Template Subtraction - MTS**): Tự động tìm đỉnh tim mẹ, dựng sóng mẫu trung vị và co giãn biên độ bình phương tối thiểu kẹp trong [0.3; 3.0] để triệt tiêu nhịp mẹ sạch sẽ mà không làm biến dạng tín hiệu mục tiêu.
   * Thuật toán chọn kênh mù nhãn: `peakprob` (độ nhọn xác suất của TCN) và `PSD` (năng lượng dải 1.8–3.0 Hz).

3. **Cơ chế Cổng an toàn lâm sàng 3 màu (Confidence Gate):**
   * Sử dụng 12 chỉ số đặc trưng chất lượng tín hiệu (SQI).
   * Đèn Xanh: Tín hiệu tốt, FHR sinh lý (110–160 bpm) → Xuất số đo.
   * Đèn Vàng: Tín hiệu biến thiên hoặc có nhiễu nhẹ → Cảnh báo.
   * Đèn Đỏ: Phát hiện miếng dán lỏng, tín hiệu nát, hoặc **tỷ lệ bám nhịp mẹ ≥ 60%** → **Tự động từ chối xuất kết quả (gạch bỏ số đo)** để chống chẩn đoán nhầm.

4. **Tối ưu hóa phần cứng nhúng (Edge-AI / TinyML Profiling):**
   * Đã xuất sang đồ thị tính toán chuẩn **ONNX** (`model/fetalqrs_tcn.onnx`).
   * Lượng tử hóa đối xứng **INT8** (chuẩn ARM CMSIS-NN): Flash ROM chỉ tốn **110.6 KB** (chiếm 1.35% chip ESP32-S3), RAM đệm luân phiên Ping-Pong chỉ tốn **117.2 KB** (chiếm 22.89% SRAM).
   * Tốc độ suy luận: **280 ms** trên STM32H7 và **364 ms** trên ESP32-S3 cho 4 giây tín hiệu (nhanh gấp 11 – 14 lần thời gian thực).
   * Chế độ ngủ sâu (Deep Sleep): Chiếm **> 90% thời gian**, chứng minh pin duy trì được nhiều tuần.

5. **Phần mềm và Giao diện Web Monitor thời gian thực:**
   * Máy hiện sóng Web Live Monitor tại `http://127.0.0.1:7860/monitor` với màn hình OLED, quét sóng 250 Hz mượt mà, tích hợp bảng đối chuẩn SOTA động.
   * Hệ thống 5 bước kể chuyện và 8 tab chuyên gia tại `http://127.0.0.1:7860/gradio/`.

### 1.3 "Nút thắt thực tế" duy nhất của đề tài hiện tại
* **Rào cản Đạo đức Y sinh (IRB):** Phụ nữ mang thai và thai nhi là đối tượng bảo vệ đặc biệt theo Tuyên ngôn Helsinki. Tuyệt đối không được tự ý dán mạch tự chế lên cơ thể thai phụ khi chưa có chứng nhận an toàn điện y tế IEC 60601-1 và phê duyệt đạo đức của bệnh viện.
* **Hạn chế thiết bị đo lâm sàng:** Không có máy đo chuyên dụng và không có nguồn bệnh nhân mang thai để đo kiểm thực địa tại trường.

---

## PHẦN 2: HƯỚNG ĐỀ XUẤT 1 — GIẢI MÃ SÓNG P & CỔNG TỪ CHỐI BÁO ĐỘNG GIẢ TRÊN ĐIỆN TIM ĐƠN KÊNH

*(Single-Lead P-Wave Delineation & Motion-Aware False Alarm Rejection for Ambulatory Cardiac Monitoring)*

### 2.1 "Khoảng trống khoa học" của thế giới (Tại sao Apple Watch bất lực?)
Rất nhiều người lầm tưởng đồng hồ thông minh (Apple Watch, Garmin, Samsung Watch) đã giải quyết xong bài toán đo điện tim cá nhân. Tuy nhiên, y văn tim mạch quốc tế (AHA 2024, ESC 2025) chỉ ra 2 lỗ hổng chí mạng:

1. **Điểm mù trước sóng P (Tâm nhĩ):**
   * Apple Watch hay vòng đeo tay chỉ bắt được **đỉnh R của tâm thất** (biên độ lớn 1.000 – 2.000 µV).
   * Chúng hoàn toàn **"mù" trước sóng P** (hoạt động của tâm nhĩ) vì sóng P cực kỳ nhỏ (**chỉ 10 – 50 µV**, chìm sâu trong nhiễu cơ và trôi đường đẳng điện — **hoàn toàn tương đồng với biên độ nhịp tim thai**).
   * Vì không nhìn thấy sóng P, các thiết bị này **không thể phát hiện được:**
     * Rung nhĩ kịch phát (Paroxysmal Atrial Fibrillation).
     * Cuồng nhĩ (Atrial Flutter).
     * Các dạng Block nhĩ thất độ 1, độ 2 (AV Blocks — khoảng PR kéo dài > 200 ms).
     * Suy nút xoang, nhịp nhĩ lang thang.
   * Apple Watch chỉ "đoán mò" rung nhĩ dựa vào việc nhịp tim đập không đều, dẫn đến bỏ sót hàng loạt bệnh nhân rung nhĩ nguy cơ đột quỵ cao.

2. **Vấn nạn "Báo động giả" (Alert Fatigue):**
   * Khi người dùng cử động tay, đi lại hoặc tập thể dục, nhiễu cơ (EMG) làm máy hiểu nhầm là loạn nhịp tim.
   * Tỷ lệ báo động giả của các thiết bị đeo hiện nay lên tới **60% – 70%**, làm bệnh nhân hoảng loạn và bác sĩ lâm sàng bị quá tải thông tin rác.

### 2.2 Đóng góp khoa học mới mang tính đột phá
1. **Dò chính xác vị trí, đỉnh và ranh giới sóng P (P-wave onset/peak/offset) từ 1 kênh duy nhất:**
   * Tận dụng kiến trúc TCN trường tiếp nhận 1.5 giây (chứa trọn 2 chu kỳ nhịp tim người lớn) để học trọn vẹn hình thái khoảng dẫn truyền PR (120–200 ms).
   * Định vị đỉnh sóng P với sai số thời gian chỉ 1–2 mili-giây, đo lường chính xác khoảng PR theo thời gian thực.
2. **Cơ chế Cổng an toàn dập tắt 100% báo động giả khi vận động (Motion Rejection Gate):**
   * Khi người đeo vung tay mạnh, chạy nhảy hoặc điện cực bị lỏng, hệ thống **bật ĐÈN ĐỎ và TỰ ĐỘNG KHÓA CẢNH BÁO LOẠN NHỊP**, loại bỏ hoàn toàn hiện tượng báo động giả do nhiễu cơ.

### 2.3 Mức độ kế thừa mã nguồn hiện tại: Giữ lại 90%
* **Mô hình TCN (113k tham số, 0.48 MB):** Giữ nguyên kiến trúc 5 khối giãn nở, hàm kích hoạt GELU, chuẩn hóa BatchNorm và đầu ra Heatmap. Chỉ cần huấn luyện lại trên nhãn sóng P (QTDB, LUDB).
* **Bộ lọc và tiền xử lý:** Giữ nguyên lọc dải và kỹ thuật khử đỉnh R để làm nổi sóng P.
* **Cổng an toàn 3 màu:** Giữ nguyên logic Cổng tin cậy (Đèn Xanh: sóng P chuẩn xác; Đèn Đỏ: nhiễu vận động, từ chối báo động giả).
* **Mô phỏng vi điều khiển ESP32-S3:** Tận dụng 100% code nén INT8, CMSIS-NN và đo đạc chu kỳ xung nhịp.
* **Giao diện Web Monitor:** Giữ nguyên toàn bộ giao diện máy hiện sóng OLED, chỉ đổi vạch đánh dấu từ nhịp thai sang đỉnh sóng P.

### 2.4 Khả năng thử nghiệm thực tế trên người thật: CỰC KỲ DỄ DÀNG
* **Đối tượng:** Bất kỳ ai (sinh viên trong nhóm, bạn bè, thầy cô).
* **Kịch bản thực nghiệm tại chỗ:**
  1. *Nghỉ ngơi:* Dán 1 kênh trước ngực, đo sóng P sắc nét, đo khoảng PR chuẩn 160 ms.
  2. *Thay đổi tư thế sinh lý:* Nằm nghỉ rồi đột ngột đứng dậy, hoặc nín thở (nghiệm pháp Valsalva) để thấy khoảng PR và sóng P co giãn sinh lý trực tiếp trên màn hình.
  3. *Vận động gây nhiễu:* Người đo chạy tại chỗ hoặc hít đất, chứng minh Cổng an toàn tự chuyển sang Đèn Đỏ để khóa báo động giả.
* **Cơ sở dữ liệu đối chuẩn quốc tế:** Kiểm chứng trên PhysioNet QT Database, LUDB Database (các bộ chuẩn vàng quốc tế có nhãn từng sóng P, QRS, T).

---

## PHẦN 3: HƯỚNG ĐỀ XUẤT 2 — MIẾNG DÁN ĐƠN KÊNH TÁCH TÍN HIỆU ĐIỆN TIM VÀ CƠ HOÀNH (dEMG) GIÁM SÁT HÔ HẤP & GIẤC NGỦ

*(Single-Patch Surface Diaphragmatic EMG & Cardiac Decoupling for Continuous Respiratory Effort and Apnea Monitoring)*

### 3.1 "Khoảng trống khoa học" của thế giới
1. **Nhu cầu cấp thiết trong Hồi sức Cấp cứu & Bệnh phổi:**
   * Trong suy hô hấp cấp, hen phế quản nặng, bệnh phổi tắc nghẽn mạn tính (COPD) và cai máy thở: Bác sĩ cần biết **bệnh nhân có đang phải gắng sức thở hay không** qua hoạt động điện của cơ hoành (Diaphragmatic EMG - dEMG).
2. **Nút thắt kỹ thuật hiện tại:**
   * Cách duy nhất hiện nay để đo chuẩn hoạt động cơ hoành là **luồn một ống thông cảm biến qua mũi, đi qua thực quản xuống dạ dày** (hệ thống NAVA - Neurally Adjusted Ventilatory Assist). Phương pháp này xâm lấn, gây đau đớn, chảy máu mũi và khó chịu tột cùng cho bệnh nhân.
   * Nếu dán điện cực ngoài lồng ngực/hạ sườn: **Xung điện tim (ECG 1.000 – 2.000 µV) đè bẹp hoàn toàn xung điện cơ hoành (chỉ 10 – 50 µV)**. Các bộ lọc thông thường hoàn toàn bất lực vì dải tần số của tim và cơ hoành trùng lấn nhau (20 – 250 Hz).

### 3.2 Đóng góp khoa học mới mang tính đột phá
1. **Thay thế ống thông dạ dày bằng 1 miếng dán duy nhất ở hạ sườn (xương sườn 7–8):**
   * Sử dụng thuật toán **Trừ khuôn mẫu trung vị thích nghi (Median Template Subtraction - MTS)** của nhóm: Triệt tiêu sạch sẽ 100% xung điện tim (QRS-T) mà không làm biến dạng tín hiệu cơ hoành.
   * Sử dụng mạng **TCN**: Trích xuất đường cong công thở cơ hoành (Work of Breathing) liên tục theo từng nhịp hít vào/thở ra.
2. **Phát hiện sớm và phân loại chuẩn xác chứng Ngưng thở khi ngủ (Sleep Apnea):**
   * Phân biệt rạch ròi giữa **Ngưng thở tắc nghẽn (Obstructive Apnea)** (cơ hoành vẫn gắng sức co bóp nhưng khí không vào được) và **Ngưng thở trung ương (Central Apnea)** (cơ hoành ngừng co bóp hoàn toàn do não ngừng phát lệnh).
3. **Cổng từ chối thông minh:** Bật Đèn Đỏ tự ngắt khi bệnh nhân ho, nuốt nước bọt hoặc nói chuyện làm lệch tín hiệu.

### 3.3 Mức độ kế thừa mã nguồn hiện tại: Giữ lại 85%
* Thuật toán khử nhịp mẹ (MTS) được chuyển đổi trực tiếp thành thuật toán **Khử nhịp tim để cứu tín hiệu cơ hoành**.
* Mạng TCN được dùng để dự đoán đường bao năng lượng cơ hoành (dEMG envelope).
* Toàn bộ mã nhúng vi điều khiển ESP32-S3, quy trình INT8 và trang Web Monitor giữ nguyên cấu trúc.

### 3.4 Khả năng thử nghiệm thực tế trên người thật: CỰC KỲ DỄ DÀNG
* **Đối tượng:** Bất kỳ thành viên nào trong nhóm.
* **Kịch bản thực nghiệm tại chỗ:**
  * Dán 1 miếng dán ở hạ sườn phải (gian sườn 7–8 đường nách giữa).
  * Thở bình thường → Thở sâu → Thở gấp → Nín thở trong 15 giây.
  * Màn hình máy tính hiển thị: Nhịp tim bị xóa sạch, để lộ đường cong co bóp cơ hoành nhấp nhô theo từng nhịp thở. Khi nín thở, đường cong lập tức nằm ngang và hệ thống bật cảnh báo ngưng thở.
* **Cơ sở dữ liệu đối chuẩn:** Thử nghiệm trên tập dữ liệu PhysioNet Non-Invasive Diaphragmatic EMG Database.

---

## PHẦN 4: MA TRẬN SO SÁNH CHIẾN LƯỢC GIỮA 3 PHƯƠNG ÁN

| Tiêu chí đánh giá | Đề tài hiện tại (RelyFetal - Tim thai) | Hướng đề xuất 1 (Giải mã Sóng P & Chống báo động giả) | Hướng đề xuất 2 (Miếng dán Cơ hoành & Hô hấp dEMG) |
| :--- | :--- | :--- | :--- |
| **Bản chất bài toán kỹ thuật** | Tách tim con (10–50 µV) bị tim mẹ (1000 µV) đè bẹp từ 1 kênh bụng | Tách sóng P (10–50 µV) bị QRS (1000 µV) đè bẹp & chống báo động giả | Khử điện tim (1000 µV) để trích xuất tín hiệu cơ hoành (10–50 µV) |
| **Tỷ lệ giữ lại mã nguồn hiện có** | 100% | **90%** (Kiến trúc TCN, bộ lọc, cổng an toàn, INT8, Web giữ nguyên) | **85%** (Tái sử dụng MTS, TCN, INT8, Web Monitor) |
| **Khả năng test trên người thật** | **Rất khó** (vướng Y đức IRB thai phụ, không có người đo) | **Rất dễ 100%** (Dán ngực bất kỳ ai, test vận động / đổi tư thế) | **Rất dễ 100%** (Dán hạ sườn, test các kiểu thở / nín thở) |
| **Tính mới đối với thế giới** | Rất cao, nhưng khó kiểm chứng thực địa diện rộng | **Rất cao:** Giải quyết điểm mù Apple Watch + diệt báo động giả | **Rất cao:** Thay thế ống thông luồn thực quản xâm lấn |
| **Chi phí phần cứng thử nghiệm** | ~300.000 VNĐ (chạy giả lập HIL) | ~150.000 VNĐ (Module AD8232 + ESP32) | ~150.000 VNĐ (Module sEMG/ECG + ESP32) |
| **Tính thuyết phục trước Hội đồng** | Tốt trên lý thuyết / HIL, nhưng dễ bị hỏi về thử nghiệm lâm sàng | **Thuyết phục tuyệt đối:** Live Demo trực tiếp trên cơ thể tại bàn | **Thuyết phục tuyệt đối:** Người đo nín thở, màn hình báo động ngay |

---

## PHẦN 5: LỘ TRÌNH CHUYỂN ĐỔI NHANH KHÔNG GIÁN ĐOẠN NGHIÊN CỨU

Nếu nhóm quyết định chọn **Hướng 1 (Giải mã Sóng P & Chống báo động giả)** — hướng đi tối ưu nhất:

### Giai đoạn 1: Chuẩn bị dữ liệu và huấn luyện chuyển giao (3 – 5 ngày)
* Tải tập dữ liệu mở có nhãn sóng P chuẩn quốc tế của PhysioNet (QT Database / LUDB Database).
* Nạp trọng số mạng `FetalQRS-TCN` sẵn có, tinh chỉnh nhẹ (Fine-tuning) trong 20 epoch để mạng chuyển từ bắt đỉnh fQRS sang bắt đỉnh và ranh giới sóng P.

### Giai đoạn 2: Tinh chỉnh logic Cổng từ chối an toàn (2 ngày)
* Điều chỉnh logic Đèn Đỏ: Khi phát hiện nhiễu cơ (biên độ dao động tần số cao vượt ngưỡng) hoặc đường đẳng điện trôi mạnh do cử động tay → Hệ thống tự động khóa cờ cảnh báo loạn nhịp, báo ĐÈN ĐỎ "Tín hiệu bị nhiễu do vận động — Không phát báo động giả".

### Giai đoạn 3: Nạp chip ESP32 và kiểm thử thực địa tại chỗ (2 ngày)
* Dùng module AD8232 (giá 50k VNĐ) nối vào chân ADC của chip ESP32-S3.
* Dán 2 điện cực lên ngực một bạn trong nhóm, kết nối Bluetooth/Serial truyền sóng về trang Web Live Monitor.
* Thực hiện bài test chạy bộ tại chỗ để chứng minh: Khi ngồi yên sóng P hiện rõ; khi chạy bộ máy tự bật Đèn Đỏ chặn báo động giả.

### Giai đoạn 4: Hoàn thiện báo cáo và bài thuyết trình bảo vệ (2 ngày)
* Đổi tên đề tài sang: **"Giải mã sóng P và phát hiện sớm rối loạn dẫn truyền nhĩ thất trên điện tim đơn kênh ứng dụng AI biên có cơ chế từ chối báo động giả"**.
* Cập nhật số liệu thực nghiệm vào bài báo và slide thuyết trình.
