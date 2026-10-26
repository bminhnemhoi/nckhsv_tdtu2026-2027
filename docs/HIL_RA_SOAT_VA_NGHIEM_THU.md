# Rà soát HIL và kế hoạch nghiệm thu - RF-HIL-001 Rev C

Ngày rà soát: **21/10/2026**. Phạm vi: `docs`, firmware trong `analysis/hardware_simulator`, mô hình `model/fqrs_model.py` và script dự toán MCU. Trạng thái: **thiết kế nguyên mẫu bàn thí nghiệm; chưa lắp và đo nghiệm thu**.

## 1. Kết luận

Hướng dùng một ESP32 phát DAC sang ESP32-S3 thu ADC **hợp lý cho thử nghiệm đường tín hiệu analog và triển khai thuật toán**. Tuy nhiên, tài liệu cũ chưa đủ căn cứ để khẳng định chạy AI, giữ nguyên F1 hay đạt chuẩn thiết bị y tế. Rev B đã sửa phần chia áp hợp lý; Rev C giữ nguyên cấu trúc analog, khóa loại bo và bổ sung hồ sơ lắp, mua hàng, tiêu chí nghiệm thu.

**Không thể bảo đảm “lắp theo sơ đồ chắc chắn chạy”.** Phần điện cần đo trên linh kiện thực; firmware hiện có chưa phải bản triển khai TCN. Hoàn thành đấu dây chỉ là một điều kiện. Chưa có kết quả đo điện áp, jitter, ADC, chạy dài hoặc inference trên bo để xác nhận toàn hệ thống.

Hồ sơ hiện hành:

- [Bản vẽ vector Rev C](hil_revC/RF-HIL-001_RevC_schematic.pdf), [SVG](hil_revC/RF-HIL-001_RevC_schematic.svg).
- [Bảng chân và đấu nối](hil_revC/RF-HIL-001_RevC_connections.csv), [netlist cấp module](hil_revC/RF-HIL-001_RevC_netlist.json).
- [Danh mục mua hàng chính xác](HIL_DANH_MUC_MUA_HANG.md).
- [Biên bản nghiệm thu để điền số đo](hil_revC/BIEN_BAN_NGHIEM_THU.md).

Các slide v1-v14, ảnh cũ và hồ sơ Rev B là tài liệu lịch sử, không dùng để đặt hàng hay đấu dây thay Rev C.

## 2. Các vấn đề thực sự tìm thấy

| Vấn đề | Bằng chứng trong dự án | Xử lý và ý nghĩa |
| --- | --- | --- |
| Hướng dẫn cũ ghi R=1 kΩ, không chia áp | `HUONG_DAN_LAP_RAP_PHAN_CUNG_HIL.md`, mục 1-4 | Bỏ hướng dẫn điện cũ, dùng R1=10 kΩ, R2=39 kΩ của Rev B/C. Không nối DAC trực tiếp ADC. |
| Chưa khóa bo; TMe, DevKit V1, NodeMCU và bo Espressif bị dùng lẫn | Rev B và các bảng mua cũ | Rev C chọn A1 Espressif ESP32-DevKitC-32E; A2 Espressif ESP32-S3-DevKitC-1-N8R8 v1.1; A3 DFRobot DFR0486. Chỉ pinmap này được đối chiếu. |
| Số fHR được gán sẵn | `esp32s3_receiver_oled.ino`: `current_fhr = 142`, không cập nhật bằng bộ phát hiện đỉnh | Số 142 và chữ `[OK]` không chứng minh thuật toán. Firmware này chỉ là minh họa giao diện, không dùng làm kết quả nghiên cứu. |
| “Gate” chỉ so mức DC | Cùng file: `avg_val > 2150`, không gọi TCN hoặc `fsqi/gate.py` | Bỏ suy diễn bám nhịp mẹ từ ADC mean; phải chạy gate thật trên đặc trưng, với ngưỡng đã xác nhận độc lập. Không chỉnh ngưỡng để ép r01 xanh/a02 đỏ. |
| Thiếu cấu hình attenuation ADC | Có `analogReadResolution(12)`, chưa có `analogSetPinAttenuation` | Bản firmware nghiệm thu cần đặt attenuation cao nhất và hiệu chuẩn; raw 4095 không mặc nhiên là 3,3 V. |
| OLED làm gián đoạn lấy mẫu | `display.display()` chạy cùng vòng `loop()`; cập nhật mỗi 40 ms | Khung 128×64 cần tối thiểu 1024×9/100000 = **92,16 ms** chỉ riêng dữ liệu tại 100 kHz; ở 400 kHz cũng là 23,04 ms. Phải tách thu mẫu khỏi truyền OLED, dùng bộ đệm và đếm overflow. |
| Bộ lọc 5 mẫu làm mất dải tín hiệu | `smooth_analog_read`, fs=250 Hz | Trung bình 5 điểm có điểm triệt đầu tiên tại **50 Hz**, ảnh hưởng dải 10-60 Hz của mô hình. Lưu ADC thô, chỉ làm mượt bản sao để vẽ nếu cần. |
| Nút bấm làm dừng phát | Bộ phát dùng `delay(200)` rồi `delay(300)`; giữ BOOT tiếp tục đổi ca | Cần debounce theo cạnh, không chặn, mốc đổi ca, sample index và đánh dấu đoạn chuyển tiếp không hợp lệ. Không giữ BOOT khi reset. |
| Hai clock chưa đồng bộ | Hai vòng `micros()` độc lập, `last_sample_time = now` | Cần timer/bộ đệm, timestamp, số thứ tự mẫu và đo drift; không coi hai lệnh “250 Hz” là đồng bộ. |
| Tài nguyên và độ trễ bị gọi là đo thật | `analysis/profile_mcu_hardware.py` dùng cycles/MAC giả định, arena=3×activation, tốc độ hai nhân chia 1,8 | 110,6 KB, 117,2 KB, 364,78 ms là **ước lượng**, không phải build INT8 hay benchmark. Không suy ra thời lượng pin từ tỷ lệ thời gian còn lại. |
| Mô hình PC chưa phải mô hình nhúng trực tuyến | `fqrs_model.py`: raw đầu vào 1000 Hz, xử lý 250 Hz, 2 kênh gồm residual và original, dùng `filtfilt` | Cần triển khai cả tiền xử lý, khử mẹ, scaling và gate. `filtfilt` dùng mẫu tương lai: phải thiết kế xử lý theo khối/look-ahead và đo độ trễ, hoặc kiểm định lại bộ lọc causal. |
| Tài liệu gọi mô phỏng là chứng minh 100% | Các mục F1, jitter và “SPICE tương đương” cũ | Mô phỏng Python RC lý tưởng không phải SPICE linh kiện, đo bench, ERC hay phép đánh giá F1 của cả chuỗi. |

## 3. Thiết kế điện Rev C

### 3.1 Analog

```text
A1 GPIO25 -- TP1 -- R1 10 kΩ --+-- TP2 -- A2 GPIO1 (ADC1_CH0)
                              |
                              +-- R2 39 kΩ -- GND
                              |
                              +-- C1 100 nF -- GND

GND A1 -------------------------- GND A2 -------- GND A3
A2 3V3 -------------------------- A3 VCC
A2 GPIO8 ------------------------ A3 SDA
A2 GPIO9 ------------------------ A3 SCL
C2 100 nF: giữa VCC/GND sát A3.
R3/R4 4,7 kΩ: SDA/SCL lên 3V3_A2; lắp cho cấu hình DFR0486 này.
```

R1/R2 mua loại ±1%, tính biên bảo thủ với ±5%; C1/C2 mua 100 nF X7R, ±10%, ≥50 V, chân xuyên lỗ. Tụ không phân cực. C1 đặt sát GPIO1/GND A2; dây DAC-GND đi sát nhau, ngắn, mục tiêu ≤15 cm. Không cần thêm op-amp/DAC/ADC rời trước khi có phép đo chứng minh nhu cầu.

Theo [Espressif DAC](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/dac.html), ESP32 có DAC 8 bit GPIO25/26. Theo [hướng dẫn ADC S3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html), GPIO1 là ADC1_CH0, nên có tụ 0,1 µF và dải hiệu chuẩn attenuation cao nhất tới 2,9 V, sai số được nêu ±50 mV. Đây là dải đo, không phải chứng nhận bảo vệ quá áp.

Giả sử DAC lý tưởng, tải ADC trở kháng cao, nguồn 3,3 V ±5%:

- Gain DC = 39/(10+39) = **0,795918**.
- Đỉnh danh định = **2,62653 V**; góc cao R ±5% = **2,81252 V**. Với điện trở mua ±1%: **2,76905 V**.
- Rth = R1∥R2 = **7,959 kΩ**; τ = **0,795918 ms**; fc = **199,96 Hz**.
- fc bảo thủ với R ±5%, C ±20%: **158,70-263,11 Hz**.
- Độ suy hao RC tương đối với gain DC tại 60 Hz ≈ **-0,374 dB**; khi phát bậc thang 250 Hz còn đáp ứng giữ mẫu DAC. Không được chỉ dùng fc để khẳng định tín hiệu được bảo toàn.
- RC tại Nyquist 125 Hz chỉ suy hao khoảng **-1,43 dB** so với DC: **chưa đủ làm bộ lọc chống alias**. Bản thu nghiệm thu cần lấy ADC nhanh hơn, lọc số rồi giảm mẫu; nhiễu ngoài dải thực phải đo. Không tăng tốc phát header 250 Hz để giả thành dữ liệu gốc 1 kHz.

Đặt tiêu chí đo TP2 từ 0 đến **2,85 V**, gồm overshoot và sai số thiết bị đo; nếu vượt phải dừng tìm nguyên nhân. Các phép tính chưa bao gồm trở kháng/phi tuyến DAC, động học ADC, nhiễu nguồn hay dây nối. Đo DC nhiều mức và sóng trước khi quyết định có cần buffer hay ADC ngoài.

### 3.2 I²C và nguồn

Chốt bus **100 kHz**, SDA GPIO8, SCL GPIO9. DFR0486 có level shifter và pull-up trên module theo [schematic V1.0](https://dfimg.dfrobot.com/wiki/18672/DFR0486_ssd1306-oled-display-module_schematics_V1.0.pdf). Lắp R3/R4 4,7 kΩ phía host lên 3V3_A2; không áp dụng mặc định DNP của OLED không rõ loại trong Rev B. Khi thay module phải xét lại pull-up, không lắp chồng một cách tùy ý.

Theo [TI SLVA689](https://www.ti.com/lit/an/slva689/slva689.pdf), tr=0,8473×Rp×Cb. Riêng 4,7 kΩ +5% và 200 pF cho tr≈0,836 µs. Vì module có MOSFET và các rail hai phía, đây chỉ là ước lượng; đo tr SDA/SCL ≤1 µs và VOL ≤0,4 V khi giao tiếp. Không suy ra điện dung hay điện trở hiệu dụng chỉ từ một phép đo trong mạch. Quét 0x3C/0x3D và ghi địa chỉ thật.

Mỗi bo cấp qua **một cổng USB-to-UART Micro-B**, ưu tiên cùng laptop/hub chất lượng. Hai rail 5V và hai đầu ra 3V3 **không nối với nhau**; GND nối chung, A3 chỉ lấy 3V3 từ A2. Đo cả hai rail 3V3 trong 3,135-3,465 V. Bo S3 chính hãng theo pinout được chọn dùng Micro-USB, không phải mặc định USB-C.

Ngắt cả hai nguồn khi đấu dây. Khi cấp: A2 trước, A1 sau; khi tắt: A1 trước, A2 sau. Chỉ nối lại tín hiệu sau khi ngắt nguồn cả hai. Mạch chưa có bảo vệ hot-plug hoặc power-off isolation, không cố tình thử A1 đang phát khi A2 mất nguồn. Không nối người/điện cực vào cấu hình này.

Lưu ý chân A3: schematic V1.0 ghi P1.1=SDA, P1.2=SCL, P1.3=GND, P1.4=VCC; cột “Num” trên wiki liệt kê theo thứ tự ngược, không được dùng làm số chân P1. Bản vẽ Rev C theo schematic; nhận diện nhãn silk và kiểm thông cáp trước khi cấp nguồn.

### 3.3 Mức độ “đúng chuẩn kỹ sư điện”

Bản vẽ có mã, revision, ngày, tờ, mã linh kiện, tên net, chân header có nguồn đối chiếu, điểm đo, trị số/dung sai và điều kiện lắp. Đây là **sơ đồ liên kết cấp module phục vụ phòng thí nghiệm**. Nguồn tái tạo bản vẽ và netlist đi kèm, nhưng chưa có ECAD native với ERC/DRC, footprint/PCB hoặc người phê duyệt độc lập.

[IEC 61082-1](https://webstore.iec.ch/en/publication/4469) quy định trình bày tài liệu điện; [IEC 60617](https://tc3.iec.ch/tc-activity/graphical-symbols-for-diagrams/) là cơ sở ký hiệu. Chưa đối chiếu toàn văn từng điều khoản nên **không tuyên bố tuân thủ đầy đủ hoặc được chứng nhận**. IEC 60601-1 không được chứng minh bằng việc dùng dev-board hoặc mô phỏng; HIL này chỉ thử ngõ điện áp mức volt vào ADC, không kiểm định AFE điện cực/EMC/an toàn y tế.

## 4. Kế hoạch HIL sửa lại theo cổng nghiệm thu

Không ấn định “5 ngày xong 100%”. Chỉ chuyển giai đoạn khi có log đạt, lưu mã firmware, phiên bản core/thư viện, cấu hình bo và ảnh lắp thực.

| Giai đoạn | Việc cần làm | Điều kiện qua - tiêu chí nội bộ dự kiến, không phải chuẩn IEC |
| --- | --- | --- |
| G0 - Hồ sơ/mua | Đối chiếu BOM Rev C, silk/header, cáp; lưu ảnh từng module | Đúng mã, chân, có nguồn pinout; không thay bằng clone chưa đối chiếu |
| G1 - Điện tĩnh | Kiểm thông mạch khi mất nguồn; nguồn từng bo; phát DAC hằng 0/64/128/192/255 bằng firmware kiểm tra riêng | GND thông; không chập rail; TP2 0-2,85 V; ADC đơn điệu, không bão hòa; lưu VTP1/VTP2/ADC cho từng mức |
| G2 - Thu/phát 250 Hz | Timer, không delay nút bấm; lấy ADC ≥1 kHz bằng cơ chế có giới hạn tốc độ được hỗ trợ, lọc số trước decimate; raw ADC có timestamp/index | Đo phát 250 Hz ±0,1%, jitter p99 ≤0,2 ms và max ≤0,5 ms; không mất/đảo mẫu; đếm rõ mọi overflow. Không giả định API ADC continuous hỗ trợ trực tiếp 1 kHz: kiểm tra giới hạn driver, có thể lấy nhanh hơn rồi decimate |
| G3 - Dạng sóng | Thu r01/a02, ít nhất 60 s/ca; đồng bộ pha và drift với nguồn, tham chiếu đi qua cùng ZOH/RC | Sau căn chỉnh dùng chung một phép fit offset/gain cho mỗi lần hiệu chuẩn: corr ≥0,98 và NRMSE/σ(ref) ≤0,10 là mục tiêu; lưu cả kết quả trước/sau căn chỉnh. Không fit riêng từng đoạn để che méo; nếu trượt phải sửa rồi đo lại |
| G4 - Pipeline thật | Chuẩn bị dữ liệu gốc 1 kHz có metadata/nhãn/hash; đưa qua DAC/ADC, PC trước rồi port nhúng; khớp tiền xử lý, 2 kênh, TCN, peak-picking và gate | So với baseline số cùng dữ liệu, cùng pipeline: ΔF1 giảm ≤1 điểm phần trăm, FHR MAE tăng ≤2 bpm là mục tiêu đặt trước. Đánh giá gate cả coverage và lỗi trong tập được nhận, không chỉ 2 ca trình diễn; ghi chính xác nhãn/tập hold-out |
| G5 - Chạy dài | ≥30 phút, OLED bật và tắt, đổi ca/reset/mất tín hiệu; đo RAM, latency p50/p95/max | Không crash/overflow/mất mẫu; output stale/thiếu dữ liệu phải không có FHR hợp lệ. Thời gian xử lý max < hop cập nhật đã chọn, latency gồm buffer/look-ahead/display; không chỉ <4 s vì cửa sổ dài 4 s |

Tắt màn hình hoặc giảm fps chỉ giảm tải; không thay thế việc tách acquisition khỏi I²C. Đo tần số, jitter và drift thật bằng oscilloscope/logic analyzer và timestamp, không lấy khoảng cách thời gian gói USB trên PC làm jitter phần cứng.

Lặp đoạn 10 giây tạo bước nhảy tại biên vòng lặp; đổi ca cũng vậy. Mọi cửa sổ 4 giây giao biên phải đánh dấu invalid hoặc loại khỏi scoring theo quy tắc cố định; nếu không, F1 và gate sẽ bị nhiễu bởi cách phát lại. Để đánh giá chính thức cần đoạn dài và metadata: nguồn, kênh, đơn vị, tần số gốc/đích, scale/offset, lọc/resample, nhãn fQRS và hash. Header hiện tại chưa chứa đủ các thông tin này.

## 5. Kiểm tra có thể thực hiện ngay và giới hạn

Chạy lại mô phỏng RC hiện có; kiểm tra số liệu biên/dung sai, netlist, CSV, pinout, BOM, và smoke tests của mô hình. Kết quả terminal lưu tại `hil_revC/verification.txt`. Đây là kiểm tra tính nhất quán và mô hình toán, không phải xác nhận bo thật. Không sửa firmware trong lần rà soát tài liệu này; các lỗi firmware ở mục 2 vẫn là công việc bắt buộc trước G2/G4.

Chưa có phần cứng kết nối để kiểm tra, chưa có ERC của ECAD và chưa compile firmware bằng Arduino toolchain trong lần này. Vì vậy mức kết luận hiện tại là **có thể mua bộ nguyên mẫu theo BOM và tiến hành G0/G1; chưa đủ điều kiện tuyên bố HIL AI đã chạy**.
