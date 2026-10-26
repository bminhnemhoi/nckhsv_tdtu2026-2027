> **Đã có Rev C ngày 21/10/2026:** Giữ Rev B để truy vết. Lắp/mua theo [hồ sơ Rev C](../HIL_RA_SOAT_VA_NGHIEM_THU.md), có mã bo chính hãng và chân header cụ thể; không trộn biến thể TMe của Rev B với pinmap Rev C.

# Rà soát sơ đồ HIL RF-HIL-001, Rev B

Ngày: 18-10-2026. Đầu vào: PowerPoint v10, firmware và mô phỏng trong dự án. Đầu ra: PowerPoint v12 và các tệp trong thư mục này.

## 1. Kết luận và mức phát hành

Bản v10 phù hợp để trao đổi ý tưởng nhưng **chưa đủ làm hồ sơ kỹ thuật phát hành sản phẩm**. Rev B đã sửa liên kết giữa module, ký hiệu, mã cụm, điểm đo, điều kiện lắp và biên điện áp. Trạng thái vẫn là **NGUYÊN MẪU HIL, CHƯA PHÊ DUYỆT SẢN XUẤT**.

Đây là sơ đồ nguyên lý liên kết cấp module. A1/A2/A3 là mã cụm của dự án, R là điện trở, C là tụ, TP là vị trí đo. Cổng ghi bằng nhãn tín hiệu trên bo, không phải số thứ tự chân vật lý hay bản vẽ layout PCB. Chỉ các cổng sử dụng được thể hiện, phần mạch bên trong module thuộc tài liệu nhà sản xuất.

IEC 61082-1:2014 liên quan quy tắc trình bày tài liệu kỹ thuật điện; IEC 60617 liên quan ký hiệu đồ họa. Lần này chỉ truy cập mô tả phạm vi và tài liệu công khai. **Không đánh giá từng điều khoản toàn văn tiêu chuẩn, không tuyên bố chứng nhận hoặc tuân thủ đầy đủ IEC.** Ký hiệu quen thuộc không tự chứng minh sản phẩm đáp ứng tiêu chuẩn.

## 2. Điểm sửa so với bản trước

| Điểm ở bản cũ | Xử lý Rev B |
| --- | --- |
| J1/J2/J3 dùng cho toàn bo; số 1/2/3/4 cạnh tín hiệu chưa được xác minh | Dùng A1/A2/A3, bỏ số chân tự đặt. Bảng nối ghi A1:GPIO25, A2:GPIO1, A3:SDA... |
| Ký hiệu giống nối đất bảo vệ trong hệ thống chỉ có mass tín hiệu | Dùng tam giác mass tín hiệu và nhãn GND/0 V, không thể hiện PE. |
| BOM ghi DevKitC-1 nhưng giá/link là bo ESP32-S3 Dev của TMe | Đồng bộ A2 thành TMe ESP32-S3 Dev, WROOM-1 N8R8, USB-C. Không dùng số chân của bo Espressif cho bo TMe. |
| Mặc định thứ tự chân OLED giữa các module | Ghi theo VCC/GND/SDA/SCL, đối chiếu silk thực. |
| Thiếu điều kiện pull-up I²C | Thêm R3/R4 4k7 tùy chọn về 3V3_A2. DNP khi module có pull-up phù hợp. |
| Thiếu tụ nguồn OLED, điểm đo, revision | Thêm C2 100 nF gần A3, TP1/TP2/TP3, mã RF-HIL-001, Rev B, ngày, tờ, trạng thái phê duyệt. |
| Chỉ tính R ±5%, nguồn luôn đúng 3,3 V | Tính thêm nguồn +5%, đổi R2 từ 56 kΩ thành 39 kΩ. |
| Tài liệu, slide và mô phỏng dễ lệch | Đồng bộ R2=39 kΩ trong slide, netlist, bảng nối, script RC và Wokwi. |

Nguồn TMe trước đó đã nêu USB-C và N8R8. Lần này công cụ tìm kiếm còn ghi nhận danh mục, nhưng không truy xuất lại được trang sản phẩm/PDF riêng. Vẫn phải chốt revision vật lý, hình silk và tài liệu pin của lô bo trước khi lắp hoặc phát hành. Pinout bo Espressif không phải bằng chứng pinout bo TMe.

## 3. Cấu hình điện

- A1: ESP32 DevKit V1 có ESP-WROOM-32, DAC GPIO25. A2: TMe ESP32-S3 Dev có N8R8, ADC1_CH0 tại GPIO1. A3: module SSD1306 I²C, nguồn 3,3 V.
- R1 = 10 kΩ, R2 = **39 kΩ**, ±5%, 1/4 W. Không dùng R2=56 kΩ theo các bản slide cũ.
- C1 = 100 nF/50 V, yêu cầu sai số tối đa ±20%, sát ADC. C2 = 100 nF/50 V sát VCC/GND OLED. Tụ không phân cực. Nhà bán phải xác nhận sai số của tụ.
- R3/R4 = 4,7 kΩ ±5%, 1/4 W dự phòng. DNP nghĩa là không lắp khi module đã có pull-up phù hợp.
- Đo cả hai rail 3V3 của A1 và A2, yêu cầu 3,3 V ±5% (3,135–3,465 V) trước khi dùng các kết quả tính toán.
- GND A1/A2/A3 thông nhau. A3 VCC chỉ lấy từ 3V3_A2. Hai bo cấp USB riêng, không nối 5V hoặc hai đầu ra 3V3 với nhau.
- Chỉ cho DAC phát khi A2 đã có nguồn. Ngừng phát trước khi rút nguồn A2. Chưa kiểm chứng bảo vệ cắm nóng/chèn nguồn ngược.
- Đây là bộ giả lập điện áp vào ADC, không có đầu vào điện cực, AFE hay phần cách ly để kết nối người.

### 3.1 Biên độ và tần số cắt

[Espressif Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html) nêu GPIO1 là ADC1_CH0, nên có tụ 0,1 µF gần ADC, và dải có số liệu sai số hiệu chuẩn ở attenuation cao nhất là 0–2,9 V. [Arduino ADC API](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html) nêu dải đo rộng hơn đến 3,1 V. Rev B dùng dải 2,9 V thận trọng hơn. Khi chạy Arduino cần chốt phiên bản core, đặt analogReadResolution(12) và analogSetPinAttenuation(1, ADC_11db) theo API đã dẫn; không suy điện áp chính xác chỉ từ raw code.

Giả thiết DAC lý tưởng, ADC trở kháng cao, nguồn A1 nằm trong 3,3 V ±5%, R ±5%:

    H(0) = R2 / (R1 + R2) = 0,795918
    VADC danh định cao nhất = 3,3 × H(0) = 2,626531 V
    VADC góc cao = 3,465 × (39k × 1,05) / (10k × 0,95 + 39k × 1,05)
                 = 2,812522 V
    Biên so với 2,9 V = 87,478 mV
    Giới hạn nghiệm thu TP2 = 2,85 V
    Rth = R1 // R2 = 7.959,18 Ω
    tau = Rth × C1 = 0,795918 ms
    fc = 1 / (2πtau) = 199,964 Hz
    Với R ±5%, C1 ±20%: fc khoảng 158,70–263,11 Hz

Với R2 cũ 56 kΩ, cùng góc nguồn/điện trở làm VADC khoảng 2,983 V, cao hơn dải 2,9 V. Đây là lý do đổi trị số.

Mô hình không bao gồm trở kháng DAC thực, dòng nạp ADC, phi tuyến ADC, sai số đo và ký sinh dây. Không dùng các số này để khẳng định độ chính xác fHR. RC bậc một cũng chưa phải thiết kế chống alias hoàn chỉnh.

### 3.2 I²C và tùy chọn pull-up

SDA=GPIO8, SCL=GPIO9, 100 kHz. Wire.begin(8,9) phải khớp schematic. Quét địa chỉ thực, chỉ dùng 0x3C khi xác nhận; một số module dùng 0x3D.

1. Xác định pull-up của A3, rail và trị số từ tài liệu module hoặc phép đo phù hợp khi ngắt nguồn. Đo trong mạch có thể bị ảnh hưởng đường song song; nếu kết quả không rõ, kiểm tra linh kiện riêng.
2. Nếu pull-up sẵn phù hợp và đi về 3V3_A2, để R3/R4 DNP. Nếu thiếu, lắp R3/R4 4k7. Ghi lại biến thể lắp.
3. Mục tiêu **điện trở hiệu dụng thực** 1,1–5,1 kΩ mỗi đường, điện dung bus giả thiết ≤200 pF. Không kéo lên 5 V.
4. Theo [TI SLVA689](https://www.ti.com/lit/an/slva689/slva689.pdf), tr=0,8473×Rp×Cb. Ở 5,1 kΩ, 200 pF: tr≈0,864 µs, dưới giới hạn Standard-mode 1 µs. Với 3,465 V, VOL=0,4 V, Rp=1,1 kΩ: dòng sink≈2,786 mA, dưới mốc tính toán 3 mA.
5. Dùng oscilloscope đo rise time và mức low SDA/SCL. Nếu Cb lớn hơn giả thiết hoặc Rp ngoài khoảng, tính lại. Tính toán không tự chứng minh Cb thực ≤200 pF.

## 4. Kiểm tra đã thực hiện

- **24 kiểm tra tùy biến đều qua**: net và endpoint, GND chung, USB tách biệt, nguồn OLED, pin ADC/DAC/SDA/SCL trong firmware, DNP, biên điện áp và thời gian lên I²C. Xem RF-HIL-001_RevB_checks.json.
- Mô phỏng RC có sẵn đã chạy lại với R2=39 kΩ, 2.500 mẫu/ca r01/a02 ở 250 Hz. Log trong RF-HIL-001_RevB_simulation_250Hz.txt. Lệch pha 0,1 ms cho tương quan khoảng 0,879 và 0,759; cần đồng bộ mẫu và đối chiếu với tham chiếu qua cùng RC.
- Với mã tuyến tính lý tưởng 3,3 V/12 bit, mean a02 khoảng 1.964 < ngưỡng 2.150 trong firmware demo. Đây là minh họa ngưỡng cũ không chuyển trực tiếp sang Rev B, không phải dự đoán ADC thật.
- Script Python qua ruff check và ruff format --check.
- Đây **không phải SPICE linh kiện, ERC KiCad/Altium, đo bench, inference TCN hay chứng nhận tiêu chuẩn**.

## 5. Điều kiện phát hành sản phẩm

| Điều kiện | Trạng thái |
| --- | --- |
| Schematic có mã, revision, refs, net, TP và lựa chọn lắp | Đã bổ sung cho nguyên mẫu |
| Khóa mã mua hàng/revision/header vật lý A1/A2/A3 | Chưa khóa đầy đủ |
| Pull-up, Cb, điện áp/ripple, trình tự nguồn có số đo | Chưa đo |
| Nguồn ECAD có pin map, footprint, netlist, ERC, peer review | Chưa có trong lần chỉnh slide này |
| Nếu làm PCB: layout, DRC, BOM khóa, Gerber, tọa độ lắp và bản vẽ lắp | Chưa thực hiện |
| Firmware 1 kHz, ADC calibration, gate, TCN INT8 chạy thật | Hiện vẫn demo 250 Hz, chưa chứng minh TCN |
| Kiểm thử HIL có dung sai định trước, raw ADC, jitter, log, đối chiếu | Mới có mô phỏng |
| ESD/EMC, an toàn, môi trường theo yêu cầu sản phẩm cụ thể | Chưa đánh giá, không suy từ dev-board |
| Người chịu trách nhiệm phê duyệt release | Chưa phê duyệt |

Đây là danh sách công việc kỹ thuật của dự án, không phải trích nguyên văn hay chứng nhận một hệ thống quản lý chất lượng.

## 6. Tệp dùng khi lắp và kiểm tra

- RF-HIL-001_RevB_schematic.pdf: tờ sơ đồ trích từ slide 1, chữ và đường nét vector.
- RF-HIL-001_RevB_connections.csv: W01–W17, net, endpoint nguồn/đích và tùy chọn lắp.
- RF-HIL-001_RevB_wiring.csv: nhóm endpoint theo net.
- RF-HIL-001_RevB_netlist.json: linh kiện, net, lựa chọn lắp và giới hạn.
- RF-HIL-001_RevB_checks.json: kết quả kiểm tra và mục còn mở.
- RF-HIL-001_RevB_simulation_250Hz.txt: log RC.

Bảng nối không mô tả tọa độ lỗ breadboard. TP là chỗ kẹp đầu đo trên net, không bắt buộc mua module test point. Khi làm PCB cần thiết kế pad TP cụ thể.

## 7. Nguồn sơ cấp

1. IEC 61082-1:2014, phạm vi công khai: https://webstore.iec.ch/en/publication/4469
2. IEC TC3, IEC 60617: https://tc3.iec.ch/tc-activity/graphical-symbols-for-diagrams/
3. Espressif ESP32 DAC: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/dac.html
4. Espressif ESP32-S3 Schematic Checklist: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html
5. Espressif Arduino ADC: https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html
6. Espressif S3 GPIO mapping: https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/gpio.html
7. TI SLVA689: https://www.ti.com/lit/an/slva689/slva689.pdf
8. NXP UM10204: https://www.nxp.com/docs/en/user-guide/UM10204.pdf
9. TMe Thiên Minh, danh mục bo N8R8: https://www.tme.vn/Products.aspx?CateId=457
10. Espressif DevKitC-1 v1.1, chỉ để phân biệt với TMe: https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html

Giá trên slide là ước tính kế thừa. R2=39 kΩ và R3/R4 chưa có báo giá mới xác nhận trong lần rà soát này. Khoảng 622.000₫ là ngân sách bộ cơ bản, không phải giá chốt đơn hay BOM đã duyệt mua sắm.

