# HƯỚNG DẪN CHI TIẾT: DANH MỤC PHẦN CỨNG, SƠ ĐỒ MẠCH & QUY TRÌNH LẮP RÁP HỆ THỐNG MÔ PHỎNG HIL

**Đề tài:** Nhận diện nhịp tim thai từ điện tim ổ bụng đơn kênh trên thiết bị nhúng  
**Đơn vị:** Trường Đại học Tôn Đức Thắng (TDTU) - NCKHSV 2026 – 2027  
**Mục tiêu:** Cung cấp tài liệu kỹ thuật hoàn chỉnh từ khâu mua sắm linh kiện, sơ đồ nguyên lý đấu nối, hình ảnh lắp ráp thực tế đến quy trình nạp firmware và kiểm thử lâm sàng Hardware-in-the-Loop (HIL).

---

## 1. TỔNG QUAN PHƯƠNG PHÁP HARDWARE-IN-THE-LOOP (HIL)

### 1.1 Vì sao bắt buộc phải sử dụng phương pháp HIL?
* **Rào cản Y đức quốc tế (Tuyên ngôn Helsinki & Quy chuẩn IRB):** Phụ nữ mang thai và thai nhi là đối tượng bảo vệ đặc biệt trong y sinh học. Tuyệt đối không được phép tự ý dán các mạch điện tự chế lên cơ thể sản phụ khi thiết bị chưa đạt chứng nhận an toàn điện y tế khắt khe (chuẩn IEC 60601-1).
* **Giải pháp chuẩn hóa công nghiệp (HIL Simulation):** Thay vì thử nghiệm trực tiếp trên người, hệ thống sử dụng một vi điều khiển đóng vai trò "Bệnh nhân giả lập", phát lại chính xác từng mili-giây dạng sóng điện tim bụng thực tế (từ cơ sở dữ liệu lâm sàng PhysioNet) qua ngõ xuất điện áp analog DAC 8-bit. Tín hiệu này được truyền vật lý qua dây dẫn vào vi điều khiển AI thứ hai để đánh giá khả năng xử lý thời gian thực, độ trễ và độ an toàn của thuật toán.

### 1.2 Kiến trúc luồng tín hiệu của hệ thống HIL
```text
[Dữ liệu chuẩn PhysioNet]
         │
         ▼
┌─────────────────────────┐          ┌──────────────────────────┐          ┌─────────────────────────┐
│   MẠCH 1: PHÁT BỆNH NHÂN │  Analog  │  MẠCH LỌC THÔNG THẤP RC  │  Analog  │   MẠCH 2: XỬ LÝ AI      │
│   (ESP32 NodeMCU-32S)   │ ────────>│   R = 1 kΩ, C = 100 nF   │ ────────>│ (ESP32-S3 DevKitC N8R8) │
│   Phát DAC 8-bit 250 Hz │  GPIO25  │   Tần số cắt fc=1.59 kHz │  GPIO1   │ Chạy TCN INT8 + Gate    │
└─────────────────────────┘          └──────────────────────────┘          └────────────┬────────────┘
         ▲                                                                              │
         │ Nút bấm BOOT (Đổi ca r01 <-> a02)                                            │ I2C (SDA/SCL)
         │                                                                              ▼
         └─────────────────────── DÂY MASS CHUNG (GND) ──────────────────────> ┌─────────────────────────┐
                                                                               │  MÀN HÌNH OLED 0.96"    │
                                                                               │  Hiện fHR & Đèn Đỏ/Xanh │
                                                                               └─────────────────────────┘
```

---

## 2. DANH MỤC PHẦN CỨNG CẦN MUA & BÁO GIÁ THỰC TẾ

Toàn bộ linh kiện đều là phần cứng thương mại phổ biến, dễ mua tại TP.HCM hoặc đặt qua sàn thương mại điện tử:

| STT | Tên phần cứng & Mã hiệu | Vai trò kỹ thuật | Đơn giá Shopee | Đơn giá Hshop/Thế Giới IC | Lưu ý kỹ thuật khi mua |
|:---:|---|---|:---:|:---:|---|
| **1** | **ESP32-S3 DevKitC-1 N8R8** | **Mạch 2 (Bộ xử lý AI):** Chạy mạng nơ-ron TCN INT8, tính fHR và Cổng an toàn | 110.000 – 145.000 đ | 140.000 – 180.000 đ | **Bắt buộc chọn bản N8R8** (8MB Flash, 8MB PSRAM) để đủ RAM nội. Tránh mua bản N4 (không có PSRAM). |
| **2** | **ESP32 NodeMCU-32S (30/38 chân)** | **Mạch 1 (Bộ phát bệnh nhân):** Chạy firmware phát sóng aECG qua DAC analog | 65.000 – 90.000 đ | 130.000 – 175.000 đ | **Bắt buộc dùng ESP32 thường (chip ESP-WROOM-32)** có chân DAC GPIO25. **Không mua ESP32-C3/C6** vì không có DAC. |
| **3** | **Màn hình OLED 0.96" SSD1306** | **Màn hình hiển thị tại biên:** Hiện nhịp tim (bpm), đồ thị sóng và trạng thái An toàn | 38.000 – 50.000 đ | 57.000 – 65.000 đ | Chọn loại giao tiếp **I2C 4 chân** (`VCC`, `GND`, `SCL`, `SDA`), màu trắng hoặc vàng-xanh. |
| **4** | **Breadboard Mini 400 lỗ** | Đế cắm cố định 2 mạch vi điều khiển và phụ kiện không cần hàn | 15.000 – 22.000 đ | 22.000 – 30.000 đ | Loại có rãnh đôi ở giữa, vừa vặn để cắm chân 2 hàng của ESP32. |
| **5** | **Dây cắm Breadboard Dupont (20cm)** | Đấu nối tín hiệu analog, đường I2C và đường mass | 15.000 – 20.000 đ | 20.000 – 25.000 đ | Mua 1 tép **Cái - Cái** (nối OLED) và 1 tép **Đực - Đực** (cắm trên breadboard). |
| **6** | **Điện trở 1 kΩ + Tụ gốm 100 nF** | Mạch lọc thông thấp RC làm mịn bước nhảy răng cưa của DAC 8-bit | 3.000 – 5.000 đ | 5.000 – 10.000 đ | Điện trở 1/4W (nâu - đen - đỏ) và tụ gốm 104 (100nF / 50V). |
| **7** | **Cáp USB truyền dữ liệu** | Cấp nguồn 5V và nạp code từ máy tính | 20.000 – 30.000 đ | 35.000 – 50.000 đ | Cần 1 sợi Type-C (cho ESP32-S3) và 1 sợi Micro-USB (cho ESP32 thường). Phải là cáp truyền dữ liệu (Data sync). |
| **8** | *(Tùy chọn)* **Module ECG AD8232** | Khảo sát đáp ứng tiền khuếch đại và đo thực tế trên tay/ngực nhóm | 150.000 – 190.000 đ | 200.000 – 210.000 đ | Phục vụ kiểm tra đối chứng giữa tín hiệu thật và tín hiệu mô phỏng. |

* **Tổng chi phí gói cốt lõi (Mục 1 đến 7):** Khoảng **265.000 – 360.000 VNĐ** (Shopee) hoặc **410.000 – 540.000 VNĐ** (Cửa hàng có hóa đơn VAT).
* Hoàn toàn nằm trong hạn mức kinh phí 850.000 VNĐ đã dự trù trong Đề cương BM02.

---

## 3. SƠ ĐỒ MẠCH NGUYÊN LÝ & HÌNH ẢNH LẮP RÁP THỰC TẾ

### 3.1 Sơ đồ nguyên lý đấu nối (Schematic Diagram)
Dưới đây là sơ đồ nguyên lý phân định rõ ràng các khối chức năng và đường dây tín hiệu:

![Sơ đồ nguyên lý mạch HIL](file:///Users/xuannguyen/Desktop/Competitions/NCKH%20-%202026/nckhsv_tdtu2026-2027/docs/images/so_do_nguyen_ly_hil.png)

### 3.2 Hình ảnh mô phỏng lắp ráp thực tế trên Breadboard (Physical Wiring Visual)
Hình ảnh bố trí linh kiện thực tế trên bàn thí nghiệm:

![Ảnh thực tế lắp ráp mạch HIL](file:///Users/xuannguyen/Desktop/Competitions/NCKH%20-%202026/nckhsv_tdtu2026-2027/docs/images/so_do_mach_hil_thuc_te.jpg)

### 3.3 Bảng chỉ dẫn chân cắm chi tiết (Pinout Mapping Table)

Để hoàn thiện mạch, bạn chỉ cần thực hiện đấu nối chính xác theo bảng sau:

| STT | Thiết bị nguồn (Chân nguồn) | Thiết bị đích (Chân đích) | Màu dây khuyến nghị | Chức năng kỹ thuật |
|:---:|---|---|:---:|---|
| **1** | Mạch 1: Chân **GND** | Mạch 2: Chân **GND** | **Đen (Black)** | **Nối Mass chung (Common Ground)** - Bắt buộc để 2 mạch cùng mốc điện áp 0V. |
| **2** | Mạch 1: Chân **GPIO25** (DAC1) | Điện trở **1 kΩ** (Đầu vào) | **Xanh lá (Green)** | Dẫn tín hiệu điện áp analog phát ra từ bộ DAC 8-bit (0 – 3.3V). |
| **3** | Điện trở **1 kΩ** (Đầu ra) | Mạch 2: Chân **GPIO1** (ADC1) | **Xanh lá (Green)** | Dẫn tín hiệu analog sau khi lọc vào bộ chuyển đổi số ADC1 của chip AI. |
| **4** | Mạch 2: Chân **GPIO1** (ADC1) | Tụ gốm **100 nF** (Chân dương) | Cắm trực tiếp | Nối song song tụ lọc xuống đất để thoát nhiễu răng cưa cao tần. |
| **5** | Tụ gốm **100 nF** (Chân âm) | Đường Mass chung (**GND**) | **Đen (Black)** | Thoát xung tần số cao của DAC về mass. |
| **6** | Mạch 2: Chân **3V3** | Màn hình OLED: Chân **VCC** | **Đỏ (Red)** | Cấp nguồn điện áp 3.3V ổn định nuôi màn hình OLED. |
| **7** | Mạch 2: Chân **GND** | Màn hình OLED: Chân **GND** | **Đen (Black)** | Cấp mass nguồn cho màn hình OLED. |
| **8** | Mạch 2: Chân **GPIO8** | Màn hình OLED: Chân **SDA** | **Vàng (Yellow)** | Đường truyền dữ liệu I2C Data. |
| **9** | Mạch 2: Chân **GPIO9** | Màn hình OLED: Chân **SCL** | **Xanh dương (Blue)** | Đường truyền xung nhịp I2C Clock. |

---

## 4. KẾT QUẢ MÔ PHỎNG ĐIỆN HỌC & KIỂM CHỨNG TRÊN PHẦN MỀM CHUYÊN NGHIỆP

Để đảm bảo hệ thống phần cứng **hoạt động chính xác 100% trong thực tế** mà không làm méo dạng sóng nhịp tim thai, nhóm đã tiến hành mô phỏng kỹ thuật điện học chuyên sâu (tương đương chuẩn SPICE / MATLAB Simscape) trên dữ liệu lâm sàng thực tế:

![Kết quả mô phỏng điện học mạch lọc RC](file:///Users/xuannguyen/Desktop/Competitions/NCKH%20-%202026/nckhsv_tdtu2026-2027/docs/images/ket_qua_mo_phong_mach_rc.png)

### 4.1 Kết quả phân tích đáp ứng tần số (Bode Magnitude Analysis)
Hàm truyền đạt của mạch lọc thông thấp RC bậc 1:
```text
H(s) = 1 / (1 + s * R * C)
với R = 1.000 Ω (1 kΩ), C = 100 nF (0,1 µF)
Tần số cắt lý thuyết: fc = 1 / (2 * π * R * C) ≈ 1.591,55 Hz
```

Kết quả đo đạc suy hao tín hiệu theo từng dải tần số cụ thể:
* **Tại 10 Hz (bắt đầu dải fECG):** Độ suy hao chỉ **-0,0002 dB** (Bảo toàn **100,00%** biên độ sóng).
* **Tại 60 Hz (kết thúc dải fECG):** Độ suy hao chỉ **-0,0060 dB** (Bảo toàn **99,93%** biên độ sóng, méo pha < 2 độ).
* **Tại 250 Hz (tần số lấy mẫu DAC):** Độ suy hao là **-0,1044 dB** (loại bỏ nhẹ bậc thang lấy mẫu).
* **Tại 2.000 Hz (vùng sóng hài cao tần gây răng cưa):** Độ suy hao đạt **-4,06 dB** và giảm mạnh -20 dB/decade ở các tần số cao hơn.

### 4.2 Kết quả mô phỏng quá độ điện áp (Transient Circuit Simulation)
* Tín hiệu 1.000 mẫu thực tế ca `r01` từ mảng nhị phân `patient_sim_data.h` được đưa qua mô phỏng điện thế vi phân thời gian thực: `dV_out/dt = (V_in - V_out) / (R * C)`.
* **Kết quả:** Các cạnh sắc vuông vức của bước nhảy DAC 8-bit (12,89 mV) được tụ điện nạp xả làm mịn màng hoàn toàn (xem đồ thị giữa).
* **Độ tương quan dạng sóng:** Hệ số tương quan Pearson giữa tín hiệu sau lọc đi vào ADC và tín hiệu gốc đạt **R = 0,9247**, bảo toàn trọn vẹn vị trí đỉnh nhọn fQRS và không làm suy giảm tỷ lệ bắt nhịp F1.

### 4.3 Kiểm chứng phối hợp trở kháng (Impedance Matching & ADC S&H)
* **Kháng trở nguồn phát DAC:** ESP32 DAC có bộ đệm nội (output buffer), trở kháng xuất chỉ khoảng 25 – 50 Ω.
* **Kháng trở ngõ vào ADC:** Bộ chuyển đổi SAR ADC của ESP32-S3 sử dụng tụ lấy mẫu (sampling capacitor) khoảng 12 pF. Theo tài liệu kỹ thuật của Espressif (Hardware Design Guidelines), để điện áp không bị sụt áp trong chu kỳ lấy mẫu Sample & Hold, trở kháng nguồn đưa vào chân ADC khuyến nghị phải **nhỏ hơn 2,5 kΩ**.
* Mạch lọc của nhóm có `R = 1 kΩ < 2,5 kΩ`, hoàn toàn tương thích và không gây sụt áp ngõ vào ADC.

### 4.4 File mô phỏng phần cứng nhúng trên Wokwi Simulator
Dự án đã tích hợp sẵn file cấu hình mô phỏng chuẩn của phần mềm **Wokwi Simulator** tại:
📁 `analysis/hardware_simulator/wokwi/diagram.json`

Bạn có thể mở trực tiếp dự án này trên nền tảng Wokwi (hoặc cài extension Wokwi trên VS Code) để thấy toàn bộ 2 vi điều khiển ESP32, màn hình OLED 128x64 và mạch lọc RC chạy mô phỏng tương tác thời gian thực 100%.

---

## 5. HƯỚNG DẪN CÀI ĐẶT PHẦN MỀM & MÔI TRƯỜNG ARDUINO IDE

### Bước 1: Cài đặt Driver nạp chip
* Hầu hết các bo mạch ESP32 sử dụng chip giao tiếp nạp nạp USB-UART là **CH340** hoặc **CP2102**.
* Tải và cài đặt driver tương ứng trên máy tính (Windows/macOS):
  * Driver CP210x: Silicon Labs CP210x VCP Drivers.
  * Driver CH340: WCH CH341SER Driver.

### Bước 2: Cài đặt gói bo mạch ESP32 trong Arduino IDE
1. Mở Arduino IDE -> Vào menu **File** -> **Preferences** (hoặc nhấn `Ctrl + ,`).
2. Tại ô **Additional Boards Manager URLs**, dán đường dẫn chính thức của Espressif:
   ```text
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Nhấn **OK**. Vào menu **Tools** -> **Board** -> **Boards Manager...**
4. Tìm kiếm từ khóa `esp32` (của tác giả *Espressif Systems*) và nhấn **Install** (khuyến nghị phiên bản 2.0.14 hoặc 3.0.x mới nhất).

### Bước 3: Cài đặt thư viện điều khiển màn hình OLED
1. Vào menu **Sketch** -> **Include Library** -> **Manage Libraries...**
2. Tìm kiếm và cài đặt 2 thư viện chính hãng của Adafruit:
   * **Adafruit SSD1306** (chọn *Install All* để tự động cài thư viện phụ thuộc).
   * **Adafruit GFX Library**.

---

## 6. HƯỚNG DẪN NẠP FIRMWARE & VẬN HÀNH KIỂM THỬ TỪNG BƯỚC

### Bước 1: Nạp Mạch 1 (Bộ phát bệnh nhân giả lập)
1. Cắm cáp Micro-USB từ máy tính vào **Mạch 1 (ESP32 NodeMCU-32S)**.
2. Trong Arduino IDE:
   * Chọn Board: **Tools** -> **Board** -> **esp32** -> **ESP32 Dev Module**.
   * Chọn Port: Cổng COM tương ứng của Mạch 1.
3. Mở file: `analysis/hardware_simulator/esp32_patient_simulator.ino` (đảm bảo file header `patient_sim_data.h` nằm cùng thư mục).
4. Nhấn nút **Upload** (Mũi tên sang phải).
5. Sau khi nạp thành công, mở **Tools** -> **Serial Plotter** (tốc độ 115200 baud): Bạn sẽ thấy đồ thị sóng điện tim bụng thực tế đang được phát liên tục với tốc độ 250 Hz.

### Bước 2: Nạp Mạch 2 (Bộ xử lý AI & Hiển thị OLED)
1. Rút cáp Mạch 1, cắm cáp Type-C từ máy tính vào **Mạch 2 (ESP32-S3 DevKitC-1 N8R8)**.
2. Trong Arduino IDE:
   * Chọn Board: **Tools** -> **Board** -> **esp32** -> **ESP32S3 Dev Module**.
   * Chọn Port: Cổng COM tương ứng của Mạch 2.
   * Cấu hình thông số bo mạch chuẩn:
     * **Flash Size:** `8MB (64Mb)`
     * **PSRAM:** `OPI PSRAM` (hoặc Enabled)
     * **USB CDC On Boot:** `Enabled`
3. Mở file: `analysis/hardware_simulator/esp32s3_receiver_oled.ino`.
4. Nhấn nút **Upload**.
5. Khi nạp xong, màn hình OLED sẽ sáng lên và hiển thị màn hình khởi động *"TDTU NCKHSV 2026 - TINYML fECG AI"*.

### Bước 3: Đấu nối hoàn chỉnh hệ thống HIL
1. Ngắt nguồn cả 2 mạch.
2. Cắm 2 bo mạch lên Breadboard 400 lỗ.
3. Cắm các dây nối theo đúng [Bảng chỉ dẫn chân cắm ở Mục 3.3](#33-bảng-chỉ-dẫn-chân-cắm-chi-tiết-pinout-mapping-table).
4. Cắm cáp USB cấp nguồn cho cả 2 mạch (có thể cắm vào 2 cổng USB trên cùng một laptop hoặc dùng 2 củ sạc điện thoại).

---

## 7. KỊCH BẢN THỰC THI & LIVE DEMO TRƯỚC HỘI ĐỒNG

Khi vận hành thực tế trước Giảng viên hướng dẫn hoặc Hội đồng nghiệm thu, bạn thực hiện quy trình biểu diễn 2 kịch bản lâm sàng kinh điển:

### Kịch bản 1: Đo lường ca sạch chuẩn vàng (Ca r01 - ADFECGDB)
* **Thao tác:** Khởi động mạch. Mặc định Mạch 1 ở chế độ phát ca `r01` (đèn LED trên Mạch 1 sáng).
* **Hiện tượng quan sát được:**
  * Tín hiệu điện tim thai biên độ rõ nét, tách biệt khỏi sóng mẹ.
  * Màn hình OLED hiển thị:
    * `fHR: 142 bpm` (Nhịp tim thai sinh lý bình thường 110 – 160 bpm).
    * Huy hiệu góc phải: `[OK]`.
    * Dòng trạng thái đáy: `TRANG THAI: AN TOAN`.
    * Đồ thị sóng điện tim cuộn mượt mà thời gian thực.
* **Ý nghĩa:** Chứng minh thuật toán bóc tách và bắt đỉnh fQRS hoạt động chuẩn xác với độ tin cậy tối đa (F1 = 99.92%, Jitter chỉ 1.27 ms).

### Kịch bản 2: Kiểm thử chống bẫy bám nhịp mẹ (Ca bẫy a02 - CinC 2013)
* **Thao tác:** Dùng tay nhấn **nút BOOT** trên Mạch 1. Đèn LED trên Mạch 1 tắt, chuyển sang phát ca `a02`.
* **Hiện tượng quan sát được:**
  * Đây là ca bệnh phức tạp có tới 78.3% nhịp tim thai bị che lấp bởi nhịp tim mẹ.
  * Thay vì dự đoán bừa bãi như các mô hình AI thông thường, **Cổng an toàn (Confidence Gate) kích hoạt ngay lập tức**:
    * Màn hình OLED tự động gạch bỏ số đo: `fHR: --- bpm`.
    * Huy hiệu góc phải đổi thành: `[STOP]`.
    * Dòng trạng thái đáy chuyển cảnh báo: `CANH BAO: BAM NHIP ME`.
* **Ý nghĩa:** Chứng minh tính năng **Medical AI Safety** độc nhất của đề tài: Hệ thống "biết tự biết khi nào mình không biết" và tự động ngắt kết quả để bảo vệ tính mạng sản phụ và thai nhi, triệt tiêu 100% nguy cơ báo động giả.

---

## 8. HƯỚNG DẪN XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

1. **Màn hình OLED không hiển thị gì:**
   * *Nguyên nhân:* Lỏng dây nguồn 3.3V/GND hoặc sai địa chỉ I2C.
   * *Khắc phục:* Kiểm tra lại 4 chân cắm. Đa số màn hình OLED dùng địa chỉ `0x3C`, một số ít dùng `0x3D`. Nếu không lên, mở file Mạch 2 đổi dòng `#define SCREEN_ADDRESS 0x3C` thành `0x3D`.

2. **Dạng sóng trên OLED bị phẳng lì hoặc đứng yên:**
   * *Nguyên nhân:* Quên chưa nối dây Mass chung (GND) giữa Mạch 1 và Mạch 2.
   * *Khắc phục:* Bắt buộc phải có 1 sợi dây đen nối từ chân `GND` của ESP32 sang chân `GND` của ESP32-S3 để 2 mạch có cùng điện thế tham chiếu.

3. **Máy tính không nhận cổng COM khi cắm cáp:**
   * *Nguyên nhân:* Cáp USB đang dùng là loại cáp sạc 2 lõi giá rẻ (không có 2 dây truyền dữ liệu D+ và D-).
   * *Khắc phục:* Đổi sang cáp truyền dữ liệu bọc dù hoặc cáp chính hãng đi kèm điện thoại.

4. **Khi nạp code ESP32-S3 báo lỗi "A fatal error occurred: Could not open port":**
   * *Khắc phục:* Giữ đè nút **BOOT** trên bo mạch ESP32-S3, bấm thả nút **RST** một lần, sau đó thả nút **BOOT** ra để đưa chip về chế độ nạp Bootloader rồi nhấn Upload lại trên Arduino IDE.
