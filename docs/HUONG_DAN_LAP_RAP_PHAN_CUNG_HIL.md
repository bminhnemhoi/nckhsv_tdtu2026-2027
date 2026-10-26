> **HIỆN HÀNH 21/10/2026 - Rev C:** Dùng [hồ sơ rà soát/nghiệm thu](HIL_RA_SOAT_VA_NGHIEM_THU.md) và [BOM mua hàng](HIL_DANH_MUC_MUA_HANG.md). Chưa có đo kiểm trên bo; firmware thu hiện tại là demo giao diện, chưa chạy TCN/gate. Các ảnh và slide cũ không phải hướng dẫn lắp Rev C.

# HƯỚNG DẪN CHI TIẾT: DANH MỤC PHẦN CỨNG, SƠ ĐỒ MẠCH & QUY TRÌNH LẮP RÁP HỆ THỐNG MÔ PHỎNG HIL

**Đề tài:** Nhận diện nhịp tim thai từ điện tim ổ bụng đơn kênh trên thiết bị nhúng  
**Đơn vị:** Trường Đại học Tôn Đức Thắng (TDTU) - NCKHSV 2026 – 2027  
**Mục tiêu:** Cung cấp cấu hình mua sắm, sơ đồ liên kết và quy trình chuẩn bị firmware và kiểm thử HIL trên bàn thí nghiệm, không phải kiểm thử lâm sàng.

---

## 1. TỔNG QUAN PHƯƠNG PHÁP HARDWARE-IN-THE-LOOP (HIL)

### 1.1 Phạm vi sử dụng HIL

Thử nghiệm trên bàn cho phép phát lại dữ liệu có nhãn, đo đường DAC-RC-ADC và so với baseline số trước khi đánh giá thuật toán nhúng. Đây là lựa chọn của kế hoạch nghiên cứu, không phải tuyên bố HIL là thủ tục bắt buộc cho mọi đề tài. Cấu hình này không có AFE điện cực hoặc cách ly cho người; chỉ dùng dây tín hiệu giữa các bo.

### 1.2 Kiến trúc luồng tín hiệu hiện hành

Dữ liệu số → A1 DAC GPIO25 → R1=10k → nút ADC (R2=39k và C1=100nF xuống GND) → A2 GPIO1. A2 điều khiển A3 DFR0486 qua GPIO8 SDA/GPIO9 SCL. A3 lấy nguồn 3V3_A2; GND ba module chung. Hai nguồn USB riêng, không nối rail 5V/3V3 giữa bo.

## 2. DANH MỤC PHẦN CỨNG CẦN MUA

Dùng duy nhất [danh mục Rev C](HIL_DANH_MUC_MUA_HANG.md). Các báo giá cũ 265.000-540.000đ chưa xác nhận và không khớp bộ bo chính hãng đã chọn. Không mua AD8232/điện cực cho cấu hình HIL này.

## 3. SƠ ĐỒ MẠCH VÀ ĐẤU NỐI

![Sơ đồ nguyên lý Rev C](hil_revC/RF-HIL-001_RevC_schematic.svg)

[Bản PDF để in](hil_revC/RF-HIL-001_RevC_schematic.pdf) · [Bảng dây có số chân header](hil_revC/RF-HIL-001_RevC_connections.csv).

Chân A1/A2 theo đúng bo Espressif trong BOM; không áp dụng vị trí chân cho clone khác. A3 theo schematic DFR0486 V1.0, không lấy thứ tự dòng wiki làm số chân giắc. Tụ gốm không phân cực. C1 sát ADC A2, C2 sát nguồn A3, R3/R4 4k7 lắp kéo lên 3V3_A2. Dùng đế cách điện gá hai bo ở ngoài breadboard, nối dây cái-đực; breadboard dùng cho R/C và chia net. Ảnh cũ trong `images` chỉ là minh họa lịch sử, chưa phải ảnh mạch đã lắp và đo.

## 4. TÍNH TOÁN ĐIỆN VÀ GIỚI HẠN KIỂM CHỨNG

Xem [phân tích Rev C](HIL_RA_SOAT_VA_NGHIEM_THU.md#3-thiết-kế-điện-rev-c): gain=0,795918, fc≈199,96Hz, đỉnh góc cao≈2,81252V dưới giả thiết rail +5%, R ±5%. Mục tiêu TP2≤2,85V phải kiểm tra bằng dụng cụ đo. RC một bậc chưa đủ chống alias; ADC cần chiến lược lấy mẫu/lọc số đã kiểm chứng.

`simulate_hil_rc.py` là mô hình RC/DAC lý tưởng. Không phải SPICE linh kiện, ERC, đo ADC thực hoặc bằng chứng F1 giữ nguyên. Không có căn cứ xác nhận trở kháng DAC 25-50Ω, tụ S&H 12pF hay điều kiện “nguồn dưới 2,5kΩ” trong nguồn đã đối chiếu; các con số đó đã được gỡ khỏi hướng dẫn. `wokwi/diagram.json` chỉ hỗ trợ minh họa, chưa xác nhận mô phỏng analog của toàn hệ thống.

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
4. Tìm kiếm từ khóa `esp32` (của tác giả *Espressif Systems*) và nhấn **Install** ; chọn một phiên bản cụ thể, compile thử và lưu version vào biên bản, không trộn API giữa các core.

### Bước 3: Cài đặt thư viện điều khiển màn hình OLED
1. Vào menu **Sketch** -> **Include Library** -> **Manage Libraries...**
2. Tìm kiếm và cài đặt 2 thư viện chính hãng của Adafruit:
   * **Adafruit SSD1306** (chọn *Install All* để tự động cài thư viện phụ thuộc).
   * **Adafruit GFX Library**.

---

## 6. CHUẨN BỊ FIRMWARE VÀ CẤP NGUỒN

Hai file `.ino` phải được đặt trong **hai thư mục sketch riêng** cùng tên file `.ino`; chỉ thư mục bộ phát chứa thêm `patient_sim_data.h`. Không mở cả hai sketch chung một thư mục vì trùng `setup()`/`loop()`.

- A1: `esp32_patient_simulator.ino`, board ESP32 Dev Module. Đây là bộ phát 250Hz; còn delay nút bấm và lịch phát cần sửa trước nghiệm thu G2.
- A2: `esp32s3_receiver_oled.ino`, board ESP32S3 Dev Module, Flash 8MB, OPI PSRAM. Dùng cổng USB-to-UART của bo đã chọn; cấu hình Serial tương ứng cổng UART, không mặc định chuyển sang native USB CDC. Firmware chưa thực hiện inference và đang hiển thị fHR cố định 142; không dùng để nghiệm thu AI.
- Bản thu nghiệm thu cần `analogReadResolution(12)`, attenuation cao nhất (API Arduino hiện hành: `analogSetPinAttenuation(1, ADC_11db)`), hiệu chuẩn ADC, `Wire.begin(8, 9)`, I²C 100kHz; giữ cùng clock I²C cả trong và sau truyền OLED vì thư viện có thể đổi clock. Quét và xác nhận địa chỉ màn hình thật.
- Tách thu mẫu khỏi OLED, lưu raw ADC cùng timestamp/index/overflow. Gỡ logic ngưỡng DC giả gate và fHR cố định trước khi trình bày kết quả thuật toán. Xem đầy đủ việc cần sửa trong hồ sơ Rev C; lần rà soát này chưa thay firmware.

Khi đấu dây: rút nguồn cả hai bo, kiểm thông mạch theo CSV, chỉ cấp OLED từ A2. Cấp A2 trước, sau đó A1; khi tắt rút A1 trước, A2 sau. Không đổi dây hoặc để A1 tiếp tục phát vào A2 mất nguồn. Không nối người hay điện cực.

## 7. KIỂM THỬ VÀ TRÌNH DIỄN

Thực hiện G0-G5 và điền [biên bản nghiệm thu](hil_revC/BIEN_BAN_NGHIEM_THU.md). Với firmware hiện tại chỉ được mô tả là trình diễn thu analog/OLED, chưa chứng minh nhịp thai hay phát hiện bám nhịp mẹ. Không dùng số 142bpm, chữ `[OK]`/`[STOP]`, các ca được gán sẵn hoặc một mô phỏng DAC 8 bit để khẳng định an toàn lâm sàng.

Sau khi port pipeline thật, mới so F1/FHR/coverage gate trên raw ADC với baseline số cùng dữ liệu/nhãn và tiêu chí đặt trước. Không tự động gán r01 là “an toàn” hay a02 là “nguy hiểm” dựa trên tên ca. Lưu log và cả các trường hợp không đạt.

---

## 8. HƯỚNG DẪN XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

1. **Màn hình OLED không hiển thị gì:**
   * *Nguyên nhân:* Lỏng dây nguồn 3.3V/GND hoặc sai địa chỉ I2C.
   * *Khắc phục:* Kiểm tra lại 4 chân cắm. Quét I²C để xác định địa chỉ thật rồi cấu hình `SCREEN_ADDRESS`; kiểm tra cấp nguồn và ACK. Không đổi địa chỉ bằng phỏng đoán.

2. **Dạng sóng trên OLED bị phẳng lì hoặc đứng yên:**
   * *Nguyên nhân:* Quên chưa nối dây Mass chung (GND) giữa Mạch 1 và Mạch 2.
   * *Khắc phục:* Bắt buộc phải có 1 sợi dây đen nối từ chân `GND` của ESP32 sang chân `GND` của ESP32-S3 để 2 mạch có cùng điện thế tham chiếu.

3. **Máy tính không nhận cổng COM khi cắm cáp:**
   * *Nguyên nhân:* Cáp USB đang dùng là loại cáp sạc 2 lõi giá rẻ (không có 2 dây truyền dữ liệu D+ và D-).
   * *Khắc phục:* Đổi sang cáp Micro-B có đường data đã kiểm tra; vỏ bọc dù không chứng minh có data.

4. **Khi nạp code ESP32-S3 báo lỗi "A fatal error occurred: Could not open port":**
   * *Khắc phục:* Giữ đè nút **BOOT** trên bo mạch ESP32-S3, bấm thả nút **RST** một lần, sau đó thả nút **BOOT** ra để đưa chip về chế độ nạp Bootloader rồi nhấn Upload lại trên Arduino IDE.
