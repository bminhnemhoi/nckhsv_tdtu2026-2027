> **HIỆN HÀNH 21/10/2026:** Báo cáo tuần cũ được giữ để truy vết; cấu hình và kết luận đã được rà soát lại trong [hồ sơ Rev C](HIL_RA_SOAT_VA_NGHIEM_THU.md). Dùng [BOM Rev C](HIL_DANH_MUC_MUA_HANG.md) để mua hàng. Các số mô phỏng/ước lượng bên dưới không phải đo trên bo thật.

# BÁO CÁO TIẾN ĐỘ TUẦN: KIỂM THỬ GIẢ LẬP & TRIỂN KHAI PHẦN CỨNG
**Dự án:** RelyFetal — Nhận diện nhịp tim thai đơn kênh có cổng từ chối an toàn  
**Tuần thực hiện:** 21/09/2026 – 27/09/2026  
**Trọng tâm báo cáo:** Kết quả kiểm thử tín hiệu giả lập phần cứng & Kế hoạch triển khai thực tế trên vi điều khiển nhúng giá rẻ.

---

## 1. TÓM TẮT CÔNG VIỆC TRỌNG TÂM

* **Phạm vi nghiên cứu:** Thử HIL trên bàn bằng dữ liệu phát lại; cấu hình này không có đầu vào điện cực hay cách ly để kết nối người.
* **Kết quả mô phỏng số được báo cáo trước đây (chưa xác nhận HIL thật):** Mô phỏng lượng tử hóa DAC 8 bit được báo cáo không đổi F1 trong các ca đã chọn; chưa bao gồm DAC/RC/ADC thật, mất mẫu, nhiễu hoặc firmware nhúng.
* **Chuẩn bị nguyên mẫu:** Đã có header và firmware minh họa 250 Hz. Firmware thu chưa chạy TCN/gate thật; xem các việc bắt buộc trong hồ sơ Rev C. Giá cũ không áp dụng BOM mới.

---

## 2. KẾT QUẢ KIỂM THỬ GIẢ LẬP PHẦN CỨNG

### 2.1. Đánh giá suy hao thuật toán qua chuyển đổi DAC 8-bit (0 – 3.3V)
Nhóm đã cho tín hiệu điện tim bụng thực tế đi qua bộ lượng tử hóa DAC 8-bit (256 mức điện áp) mô phỏng chân analog của ESP32 để đo lường độ suy hao:

| Bản ghi kiểm thử | Tiêu chí kỹ thuật | Tín hiệu gốc Float32 (Chuẩn Lab) | Qua mô phỏng DAC 8-bit | Đánh giá sai lệch |
| :--- | :--- | :---: | :---: | :--- |
| **Ca r01 (ADFECGDB)**<br>*(Chuẩn vàng da đầu thai)* | **Điểm F1-score** | **99.92%** | **99.92%** | **Suy hao: 0.0000%** (Bảo toàn nguyên vẹn) |
| | **Sai số định thời phát hiện QRS**| **1.47 ms** | **1.27 ms** | ±50 ms là dung sai ghép nhịp đánh giá, không phải chuẩn jitter phần cứng |
| | **Số nhịp tim bắt được** | **644 / 645 nhịp** | **644 / 645 nhịp** | 644/645; không phải 100% |
| | **Trạng thái Đèn tin cậy** | **CAO (Xanh)** | **CAO (Xanh)** | Nhận diện chính xác chất lượng cao |
| **Ca a02 (CinC 2013)**<br>*(Ca bẫy bám nhịp mẹ)* | **Tỷ lệ bám nhịp mẹ** | **78.3%** | **78.3%** | Phát hiện bẫy nhịp mẹ vượt ngưỡng 60% |
| | **Trạng thái Đèn tin cậy** | **THẤP (Đỏ)** | **THẤP (Đỏ)** | **Trạng thái mô phỏng; chưa đo HIL** |
| | **Hành vi từ chối dự kiến** | Tự gạch bỏ số đo FHR | Tự gạch bỏ số đo FHR | Không suy ra hiệu quả/an toàn lâm sàng từ mô phỏng |

### 2.2. Ước lượng tài nguyên vi điều khiển (không phải benchmark nhúng)
Các số dưới đây xuất phát từ mô hình tính toán trong `analysis/profile_mcu_hardware.py`: số phép MAC, cycles/MAC giả định và arena ước lượng. Chưa có bằng chứng trong bộ firmware HIL hiện tại về xuất/triển khai INT8, STM32Cube.AI hoặc đo latency trên bo; không dùng bảng này làm kết quả thực nghiệm:

| Thông số phần cứng | STM32H7 (Cortex-M7 @ 480MHz) | ESP32-S3 (Xtensa Dual-Core @ 240MHz) | Kết luận khả thi |
| :--- | :---: | :---: | :--- |
| **Dung lượng Flash ROM** | **110.6 KB** (Chiếm 5.4% / 2MB) | **110.6 KB** (Chiếm 1.35% / 8MB) | **Tiết kiệm 75% Flash** nhờ nén INT8 |
| **Bộ nhớ RAM đệm (Arena)**| **117.2 KB** (Chiếm 11.4% / 1MB) | **117.2 KB** (Chiếm 22.9% / 512KB) | Vừa vặn RAM nội, chống tràn bộ nhớ |
| **Thời gian chạy 4s tín hiệu**| **280.64 ms** | **364.78 ms** | **Nhanh hơn thời gian thực 11x – 14x** |
| **Thời gian ngủ sâu (Sleep)**| **92.98% thời gian** | **90.88% thời gian** | **Chưa đo công suất/thời lượng pin** |

---

## 3. KẾ HOẠCH TRIỂN KHAI CỤ THỂ TRÊN PHẦN CỨNG

### 3.1. Danh mục linh kiện hiện hành

Dùng [BOM Rev C](HIL_DANH_MUC_MUA_HANG.md): A1 ESP32-DevKitC-32E, A2 ESP32-S3-DevKitC-1-N8R8 v1.1, A3 DFR0486, R1=10k, R2=39k, C1/C2=100nF và R3/R4=4k7. Danh mục đã bao gồm dây, cáp, breadboard và yêu cầu dụng cụ đo; chưa có báo giá cả bộ xác nhận.

### 3.2. Sơ đồ kết nối hiện hành

Xem [bản vẽ Rev C](hil_revC/RF-HIL-001_RevC_schematic.pdf) và [bảng đấu nối](hil_revC/RF-HIL-001_RevC_connections.csv). Không dùng cấu hình nối trực tiếp GPIO25 sang GPIO1. Đây là mạch HIL mức điện áp vào ADC, không có đầu vào điện cực/AFE.

### 3.3. Các tệp mã nguồn nhúng đã chuẩn bị sẵn trong thư mục dự án
* **Dữ liệu mẫu C Header:** `analysis/hardware_simulator/patient_sim_data.h` (Lưu sẵn 2.500 điểm mẫu chuẩn hóa của ca `r01` và `a02`).
* **Firmware nạp chip phát:** `analysis/hardware_simulator/esp32_patient_simulator.ino` (Đã viết sẵn bộ đếm thời gian 4 ms/mẫu @ 250 Hz, có nút bấm chuyển đổi giữa ca chuẩn và ca bẫy).

---

## 4. KẾ HOẠCH HÀNH ĐỘNG HIỆN HÀNH

Áp dụng các cổng G0-G5 trong [kế hoạch nghiệm thu Rev C](HIL_RA_SOAT_VA_NGHIEM_THU.md#4-kế-hoạch-hil-sửa-lại-theo-cổng-nghiệm-thu): chốt linh kiện → đo điện tĩnh → thu/phát có log → đối chiếu dạng sóng → pipeline thật → chạy dài. Không cam kết hoàn thành HIL AI trong 5-6 ngày trước khi vượt các cổng này. Các kết quả F1/gate cần đánh giá lại trên ADC thu thật, cùng dữ liệu và nhãn, không dùng chữ trên OLED làm bằng chứng.
