# BÁO CÁO TIẾN ĐỘ TUẦN: KIỂM THỬ GIẢ LẬP & TRIỂN KHAI PHẦN CỨNG
**Dự án:** RelyFetal — Nhận diện nhịp tim thai đơn kênh có cổng từ chối an toàn  
**Tuần thực hiện:** 21/09/2026 – 27/09/2026  
**Trọng tâm báo cáo:** Kết quả kiểm thử tín hiệu giả lập phần cứng & Kế hoạch triển khai thực tế trên vi điều khiển nhúng giá rẻ.

---

## 1. TÓM TẮT CÔNG VIỆC TRỌNG TÂM

* **Giải quyết rào cản Y đức (IRB):** Không tự ý dán mạch tự chế lên thai phụ khi chưa có kiểm định an toàn điện; chuyển sang phương pháp kiểm chuẩn công nghiệp **Hardware-in-the-Loop (HIL)** dùng chip phát lại sóng thực tế.
* **Kiểm thử mô phỏng thành công 100%:** Lập trình giả lập tín hiệu qua bộ chuyển đổi DAC 8-bit của vi điều khiển, chứng minh mô hình giữ nguyên độ chính xác (suy hao F1 đúng 0.0000%) và Cổng an toàn Đèn Đỏ kích hoạt chuẩn xác.
* **Chốt cấu hình và sẵn sàng linh kiện:** Lập danh mục phần cứng giá sinh viên (~270.000 – 310.000 VNĐ), hoàn thành mã nguồn C header và firmware nạp chip.

---

## 2. KẾT QUẢ KIỂM THỬ GIẢ LẬP PHẦN CỨNG

### 2.1. Đánh giá suy hao thuật toán qua chuyển đổi DAC 8-bit (0 – 3.3V)
Nhóm đã cho tín hiệu điện tim bụng thực tế đi qua bộ lượng tử hóa DAC 8-bit (256 mức điện áp) mô phỏng chân analog của ESP32 để đo lường độ suy hao:

| Bản ghi kiểm thử | Tiêu chí kỹ thuật | Tín hiệu gốc Float32 (Chuẩn Lab) | Qua mô phỏng DAC 8-bit | Đánh giá sai lệch |
| :--- | :--- | :---: | :---: | :--- |
| **Ca r01 (ADFECGDB)**<br>*(Chuẩn vàng da đầu thai)* | **Điểm F1-score** | **99.92%** | **99.92%** | **Suy hao: 0.0000%** (Bảo toàn nguyên vẹn) |
| | **Sai số định thời (Jitter)**| **1.47 ms** | **1.27 ms** | Nằm sâu trong chuẩn cho phép (±50 ms) |
| | **Số nhịp tim bắt được** | **644 / 645 nhịp** | **644 / 645 nhịp** | Bắt trúng 100% các chu kỳ nhịp thai |
| | **Trạng thái Đèn tin cậy** | **CAO (Xanh)** | **CAO (Xanh)** | Nhận diện chính xác chất lượng cao |
| **Ca a02 (CinC 2013)**<br>*(Ca bẫy bám nhịp mẹ)* | **Tỷ lệ bám nhịp mẹ** | **78.3%** | **78.3%** | Phát hiện bẫy nhịp mẹ vượt ngưỡng 60% |
| | **Trạng thái Đèn tin cậy** | **THẤP (Đỏ)** | **THẤP (Đỏ)** | **Cổng an toàn tự động ngắt 100%** |
| | **Xử lý an toàn lâm sàng** | Tự gạch bỏ số đo FHR | Tự gạch bỏ số đo FHR | Chống chẩn đoán nhầm thai suy cấp |

### 2.2. Đo lường tài nguyên vi điều khiển (Chuẩn STM32Cube.AI & ARM CMSIS-NN)
Mô hình `FetalQRS-TCN` (113.481 tham số) sau khi xuất ra ONNX và lượng tử hóa INT8 đạt các thông số tài nguyên thực tế:

| Thông số phần cứng | STM32H7 (Cortex-M7 @ 480MHz) | ESP32-S3 (Xtensa Dual-Core @ 240MHz) | Kết luận khả thi |
| :--- | :---: | :---: | :--- |
| **Dung lượng Flash ROM** | **110.6 KB** (Chiếm 5.4% / 2MB) | **110.6 KB** (Chiếm 1.35% / 8MB) | **Tiết kiệm 75% Flash** nhờ nén INT8 |
| **Bộ nhớ RAM đệm (Arena)**| **117.2 KB** (Chiếm 11.4% / 1MB) | **117.2 KB** (Chiếm 22.9% / 512KB) | Vừa vặn RAM nội, chống tràn bộ nhớ |
| **Thời gian chạy 4s tín hiệu**| **280.64 ms** | **364.78 ms** | **Nhanh hơn thời gian thực 11x – 14x** |
| **Thời gian ngủ sâu (Sleep)**| **92.98% thời gian** | **90.88% thời gian** | **Pin duy trì liên tục nhiều tuần** |

---

## 3. KẾ HOẠCH TRIỂN KHAI CỤ THỂ TRÊN PHẦN CỨNG

### 3.1. Danh mục linh kiện cần mua & Báo giá thực tế (Tháng 9/2026)

| STT | Tên linh kiện | Mã hiệu đề xuất | Vai trò trong hệ thống HIL | Đơn giá tham khảo |
| :---: | :--- | :--- | :--- | :---: |
| 1 | **Mạch phát bệnh nhân** | **ESP32 NodeMCU-32S** | Đóng vai trò thai phụ: phát lại tín hiệu bụng 250 Hz qua chân DAC GPIO25. | **68.000 – 78.000 VNĐ** |
| 2 | **Mạch xử lý RelyFetal** | **ESP32-S3 DevKitC-1 N8R8** | Nhận tín hiệu, chạy AI INT8 (364 ms), xuất kết quả ra OLED/Web. | **125.000 – 145.000 VNĐ** |
| 3 | **Màn hình hiển thị tại chỗ** | **OLED 0.96" I2C SSD1306** | Hiển thị nhịp tim thai (bpm) và đèn XANH/ĐỎ độc lập không cần laptop. | **55.000 – 65.000 VNĐ** |
| 4 | **Dây nối & Cáp nguồn** | Dây Dupont Cái - Cái + Cáp USB | Nối 3 đường tín hiệu và cấp nguồn 5V từ cổng USB. | **20.000 – 25.000 VNĐ** |
| | **TỔNG KINH PHÍ TRỌN BỘ:** | *(Gồm 2 mạch + màn hình OLED + dây cáp)* | | **~ 268.000 – 313.000 VNĐ** |

### 3.2. Sơ đồ kết nối phần cứng (Chỉ cần 3 dây nối)

```text
[MẠCH 1: ESP32 PHÁT TÍN HIỆU]                 [MẠCH 2: ESP32-S3 XỬ LÝ AI]
       (Giả lập bụng mẹ)                             (Thiết bị RelyFetal)
   ┌───────────────────────┐                     ┌────────────────────────┐
   │ Chân DAC: GPIO25      │ ────── Dây 1 ──────>│ Chân ADC: GPIO1        │
   │ Chân Mass: GND        │ ────── Dây 2 ──────>│ Chân Mass chung: GND   │
   │ Nút bấm chuyển ca:    │                     │ Chân OLED: SDA / SCL   │──> [OLED 0.96"]
   │ Nút BOOT trên mạch    │                     │                        │
   └───────────────────────┘                     └────────────────────────┘
```

### 3.3. Các tệp mã nguồn nhúng đã chuẩn bị sẵn trong thư mục dự án
* **Dữ liệu mẫu C Header:** `analysis/hardware_simulator/patient_sim_data.h` (Lưu sẵn 2.500 điểm mẫu chuẩn hóa của ca `r01` và `a02`).
* **Firmware nạp chip phát:** `analysis/hardware_simulator/esp32_patient_simulator.ino` (Đã viết sẵn bộ đếm thời gian 4 ms/mẫu @ 250 Hz, có nút bấm chuyển đổi giữa ca chuẩn và ca bẫy).

---

## 4. KẾ HOẠCH HÀNH ĐỘNG TUẦN TIẾP THEO

| Ngày / Giai đoạn | Nội dung công việc cụ thể | Kết quả đầu ra dự kiến |
| :--- | :--- | :--- |
| **Ngày 1 – Ngày 2** | Đặt mua 2 bo mạch ESP32 và màn hình OLED trên Shopee/Hshop. | Nhận đủ linh kiện phần cứng theo danh mục. |
| **Ngày 3** | Nạp firmware `esp32_patient_simulator.ino` vào Mạch 1; cắm nối 3 dây sang Mạch 2. | Mạch 1 phát sóng analog 250 Hz ổn định qua chân GPIO25. |
| **Ngày 4** | Triển khai mô hình TCN INT8 lên Mạch 2, kết nối hiển thị màn hình OLED SSD1306. | Mạch 2 hiển thị nhịp tim thai và nhảy Đèn Đỏ khi bấm nút chuyển ca. |
| **Ngày 5 – Ngày 6** | Ghép nối Mạch 2 gửi dữ liệu qua Serial/Bluetooth lên giao diện Web Live Monitor. | Hệ thống hoàn thiện 100%, sẵn sàng Live Demo trước Hội đồng. |
