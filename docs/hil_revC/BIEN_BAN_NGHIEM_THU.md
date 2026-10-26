# Biên bản nghiệm thu RF-HIL-001 Rev C

Trạng thái ban đầu: **CHƯA ĐO - không có mục nào mặc nhiên đạt**.

- Người lắp / người kiểm tra / ngày: …
- Ảnh A1/A2/A3, mã hàng/revision, đầu giắc: …
- Git commit + trạng thái thay đổi / hash firmware / core / thư viện / cấu hình: …
- Model thiết bị đo, dải đo, sai số, tình trạng hiệu chuẩn: …
- Biến thể R/C thực lắp; pull-up và địa chỉ I²C đã kiểm: …

| Hạng mục | Kết quả đo/log | Tiêu chí | Kết luận/người kiểm |
| --- | --- | --- | --- |
| GND A1/A2/A3; kiểm chập khi mất nguồn | Chưa đo | GND thông, không nối hai rail nguồn | Chưa đạt nghiệm thu |
| Rail 3V3 A1/A2 và ripple | Chưa đo | 3,135-3,465 V | Chưa đạt nghiệm thu |
| DAC 0/64/128/192/255: TP1, TP2, ADC, dải attenuation | Chưa đo | TP2 0-2,85 V kể cả sai số/overshoot; ADC đơn điệu, không bão hòa | Chưa đạt nghiệm thu |
| I²C SDA/SCL high/low/rise-time/address | Chưa đo | 100 kHz, tr ≤1 µs, VOL ≤0,4 V, không NACK bất thường | Chưa đạt nghiệm thu |
| Fs phát/thu, jitter, drift, overflow | Chưa đo | Theo G2, không mất/đảo mẫu | Chưa đạt nghiệm thu |
| r01/a02 ≥60s, corr/NRMSE trước/sau căn chỉnh | Chưa đo | Theo G3; ghi quy tắc xử lý biên | Chưa đạt nghiệm thu |
| Nguồn/lead/scale/fs/hash/nhãn dữ liệu | Chưa xác minh đầy đủ | Truy vết được đoạn và nhãn | Chưa đạt nghiệm thu |
| Baseline và qua HIL: F1/FHR/gate coverage/lỗi | Chưa đo | Theo G4, hold-out cố định | Chưa đạt nghiệm thu |
| Build INT8, RAM/arena, latency gồm preprocessing/gate/UI | Chưa build/đo | max < hop; không dùng số cycles/MAC giả định | Chưa đạt nghiệm thu |
| Chạy ≥30 phút, đổi ca/reset/ngắt tín hiệu | Chưa đo | Không crash/overflow; invalid không xuất FHR hợp lệ | Chưa đạt nghiệm thu |

Lưu CSV ADC thô, timestamp, index, log đo, ảnh mạch và kết quả phân tích cùng biên bản. Khi không đạt: ghi nguyên nhân, thay đổi revision nếu sửa thiết kế và đo lại các mục bị ảnh hưởng. Đạt biên bản bàn thí nghiệm không phải chứng nhận thiết bị y tế.
