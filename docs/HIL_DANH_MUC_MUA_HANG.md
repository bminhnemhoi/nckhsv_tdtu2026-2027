# Danh mục mua phần cứng HIL - Rev C, 21/10/2026

Đây là BOM cho **một bộ nguyên mẫu HIL trên bàn**, khớp [hồ sơ Rev C](HIL_RA_SOAT_VA_NGHIEM_THU.md). Mã bo được chọn để có pinout chính hãng rõ ràng; **không dùng giá bo clone cũ để dự toán bộ chính hãng này**. Có thể tận dụng đồ sẵn có nếu đúng thông số. Chưa có báo giá nhà cung cấp Việt Nam xác nhận, nên không ghi tổng tiền giả định.

## 1. Phần cứng phải có

| Ref | Tên/mã cần đặt | Lắp | Số lượng nên mua | Quy cách chốt và lưu ý |
| --- | --- | ---: | ---: | --- |
| A1 | **Espressif ESP32-DevKitC-32E**, DevKitC V4, ESP32-WROOM-32E | 1 | **1 bo** | Header 2,54 mm đã hàn, USB Micro-B, có GPIO25 DAC. Không thay bằng S3/C3/C6 hoặc module trần. [Pinout/mã đặt hàng](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html). |
| A2 | **Espressif ESP32-S3-DevKitC-1-N8R8**, revision **v1.1** | 1 | **1 bo** | ESP32-S3-WROOM-1-N8R8, Flash 8 MB, PSRAM 8 MB, header đã hàn; cổng USB-to-UART Micro-B. Yêu cầu người bán xác nhận mã trên vỏ module và revision; không tự đổi sang TMe/clone USB-C. [Pinout/mã đặt hàng](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html). PSRAM là dự phòng dung lượng, không bảo đảm mọi vùng DMA/arena chạy được trong PSRAM. |
| A3 | **DFRobot DFR0486**, Gravity I²C OLED 0,96 inch SSD1306 **128×64**, bản tương ứng schematic V1.0 | 1 | **1 bộ** | Cấp 3V3 từ A2; gồm **cáp Gravity I²C PH2.0-4P** theo [packing list chính hãng](https://www.dfrobot.com/product-1576.html). Yêu cầu đầu còn lại tách 4 tín hiệu để nối header/breadboard; không mua nhầm cáp hai đầu giắc kín hoặc SH1106/SPI. Nếu shop tách cáp khỏi bộ thì mua bù đúng cáp. |
| R1 | Điện trở **10 kΩ, ±1%, 0,25 W**, metal film, chân xuyên lỗ axial | 1 | **5 con** | Đo xác nhận trước lắp; tính toán vẫn dùng dung sai ±5% bảo thủ. |
| R2 | Điện trở **39 kΩ, ±1%, 0,25 W**, metal film, axial | 1 | **5 con** | Không dùng 56 kΩ từ slide cũ. |
| R3/R4 | Điện trở **4,7 kΩ, ±1%, 0,25 W**, metal film, axial | 2 | **5 con** | Rev C DFR0486: lắp 2 con kéo SDA/SCL về 3V3_A2. Đây là điện trở ngoài module; không nhầm mã R trên schematic OLED. |
| C1/C2 | Tụ gốm **100 nF (0,1 µF, mã 104), X7R, ±10%, 50 V**, radial, bước chân 2,54 hoặc 5,08 mm | 2 | **5 con** | Tụ không phân cực, dạng xuyên lỗ để cắm breadboard; không mua SMD rời hoặc tụ có sai số không rõ. |
| BB1 | Breadboard **830 điểm**, bước 2,54 mm, thanh nguồn hai bên | 1 | **1 cái** | Dùng cho R/C và chia net; hai dev-board đặt trên đế cách điện bên ngoài, nối bằng dây. Không giả định hai bo rộng cắm vừa một breadboard 400 điểm. Kiểm tra thanh nguồn có bị ngắt giữa. |
| W1 | Dây Dupont **cái-đực**, bước 2,54 mm, dài 10-15 cm | ≥10 dây | **1 bó 40 dây** | Từ header đực của bo tới breadboard. Dây analog ngắn, đi cùng GND. |
| W2 | Dây Dupont **đực-đực**, bước 2,54 mm, dài 10-15 cm | Theo bố trí | **1 bó 40 dây** | Nối các net trên breadboard. |
| W3 | Dây Dupont **cái-cái**, bước 2,54 mm, dài 10-15 cm | Theo đầu cáp OLED | **1 bó 20 dây** | Nối đầu đực của cáp Gravity với header đực A2 nếu cần; kiểm nhãn và continuity, không tin màu dây. |
| USB1/USB2 | Cáp **USB data sang Micro-B**, ≤1 m | 2 | **2 sợi** | Chọn đầu phía máy tính USB-A hoặc USB-C đúng máy; phía cả hai bo chính hãng đã chọn là Micro-B. Phải có data, không chỉ sạc. |
| Cơ khí | Đế cách điện không dẫn điện, khoảng **20×15 cm**, kèm dây rút/keo đệm gá bo | 1 bộ | **1 bộ** | Không để mặt dưới bo chạm kim loại; không che/cọ antenna và nút BOOT/EN. |

Đây là thông số đủ để mua R/C/dây, không bắt buộc một hãng cụ thể. Với A1/A2/A3, mã hãng là bắt buộc trong cấu hình đã đối chiếu. Nếu cần giảm giá bằng bo khác, phải lập biến thể BOM và pinmap riêng trước khi lắp.

Nguồn: laptop có hai cổng USB đủ cấp nguồn hoặc hub USB có nguồn riêng. Nếu thiếu cổng/công suất, bổ sung **1 hub USB data có nguồn riêng, upstream đúng cổng máy, nguồn 5 V tổng ≥2 A, hỗ trợ tải ≥500 mA mỗi cổng dùng**; không nối nguồn hub vào chân 5V bo. Laptop/hub là phương tiện cấp nguồn, không nằm trong mạch đo bệnh nhân.

## 2. Thiết bị phải có để nghiệm thu - ưu tiên mượn phòng thí nghiệm

| Thiết bị | Số lượng | Yêu cầu tối thiểu cho các phép kiểm tra trong kế hoạch |
| --- | ---: | --- |
| Đồng hồ số + que đo/kẹp | **1 bộ** | DC và đo R/thông mạch; độ chính xác DC ≤±0,5% để phân biệt biên 2,85 V. Ghi model/dải đo và sai số thực. |
| Oscilloscope + hai probe ×10 có dây mass ngắn | **1 bộ 2 kênh** | Băng thông ≥20 MHz, ≥100 MSa/s; đo TP1/TP2, ripple/overshoot, cạnh I²C. Không cần mua nếu lab cho mượn. |
| Logic analyzer | **1 bộ, tùy chọn** | ≥4 kênh, logic 3,3 V, ≥10 MSa/s và phần mềm decode I²C; hữu ích cho thống kê thời gian dài. Không thay oscilloscope để đo điện áp hoặc rise time analog. |

Không cần mua AD8232, điện cực, dây bệnh nhân, pin/sạc lithium, STM32, DAC/ADC rời, op-amp hay LED đỏ/xanh cho bộ cơ sở. OLED DFR0486 là đơn sắc xanh: trạng thái chấp nhận/từ chối hiển thị bằng chữ/ký hiệu, không phải đèn màu. Nếu cần đèn màu vật lý phải thiết kế bổ sung GPIO và điện trở hạn dòng.

## 3. Mẫu nội dung gửi shop để lấy báo giá

> Xin báo giá 1 ESP32-DevKitC-32E (Espressif, V4), 1 ESP32-S3-DevKitC-1-N8R8 (Espressif v1.1), cả hai đã hàn header; 1 DFRobot DFR0486 kèm cáp Gravity I²C PH2.0-4P tách đầu tín hiệu; 5 điện trở mỗi loại 10k/39k/4k7 ±1% 1/4W axial; 5 tụ 100nF X7R ±10% 50V radial; 1 breadboard 830 điểm; 40 dây cái-đực, 40 dây đực-đực, 20 dây cái-cái 2,54mm dài 10-15cm; 2 cáp data Micro-B đầu máy tính phù hợp. Xin ảnh mã module, revision bo, đầu giắc/cáp trước khi giao; không tự thay mã bằng hàng “tương đương”.

BOM chốt **chủng loại, quy cách và số lượng**; hàng còn tồn, revision lô giao, đơn giá, VAT và phí vận chuyển phải được shop xác nhận. Đơn giá OLED công bố trực tiếp tại hãng khi rà soát là 14,90 USD, chưa phải giá về Việt Nam và không đủ cơ sở tính tổng bộ.
