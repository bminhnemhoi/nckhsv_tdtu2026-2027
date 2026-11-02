# Đối chiếu nội dung — bản 14 slide

Mọi slide bám theo BM02 (`BM02_De_cuong_nghien_cuu_DA_CHINH_SUA.pdf`). Số liệu lấy từ tệp bằng chứng của dự án, không lấy từ bài báo khác hay giao thức khác.

Bản 15 slide gộp các cặp trùng nội dung của bản 18 slide: mục đích vào slide lý do, dữ liệu vào giao thức, phương pháp vào phần huấn luyện, kết quả khả thi vào biểu đồ trong miền, đóng góp vào ý nghĩa, câu hỏi vào tiêu chí. Bản 14 slide bỏ slide phụ lục so sánh kiến trúc (nội dung vẫn nằm trong phụ lục câu hỏi của `loi_thoai.md`).

| Slide | Nội dung | Nguồn |
|---|---|---|
| 1 | Tên đề tài, tác giả, GVHD | BM02 §1. Ba số nhanh (97,56% · 113 nghìn tham số · 8 tháng) đã bỏ khỏi bìa — chúng xuất hiện ở slide 4, 5 và 12 |
| 2 | Lý do chọn đề tài + hình một kênh (mẹ + thai + nhiễu) + câu rào đạo đức | BM02 §2.1; `assets/signal-mix.svg` là hình minh họa, không phải bản ghi. Tiêu chí số **không** lặp ở đây — để slide 13 |
| 3 | Ba nguồn dữ liệu (ADFECGDB + Silesia, CinC set-a, MIT-BIH) + chia 11 lượt, ±50 ms, bootstrap, Holm | BM02 §4, §5 nội dung 1, "Phương pháp phân tích thống kê"; `assets/data-split.png` |
| 4 | Năm khâu xử lý + cách huấn luyện (4 giây, Gauss σ = 12 ms, BCE có trọng số + tăng cường, AdamW, 3 hạt giống, ≥ 250 ms) + đồ thị thật a09 | BM02 §5 nội dung 2–3; `assets/model-probability.png`, `assets/model-beats.png` cắt từ demo |
| 5 | Kết quả bước đầu 9/2026: 97,56%; 89,5%; đối chứng 98,83 / 86,71; +10,85 [6,80; 15,40] 22/22; −1,27 [−3,08; +0,27] | BM02 §2.1; `baselines/powermf_fair_stats.json` → `so_sanh.tat_ca_22` |
| 6 | 15 bản trùng, NCC = 1,0000, lệch RR 0 ms, thổi phồng 3,27–7,18 điểm, còn 60 bản, 74,28% | BM02 §5 nội dung 1; `survey/facts_phase4.json` mục A |
| 7 | Trả lời câu hỏi 1: bảng ngoài miền 55,97 / 74,28 / 80,72 (Holm 0,051) / 82,01 (hậu kiểm) | `survey/facts_phase4.json` mục B; BM02 §6.1 |
| 8 | Ca khó a02; 12 chỉ số = 6 tín hiệu + 6 đầu ra; AUROC ≥ 0,85 | BM02 §5 nội dung 4; `assets/reliability-case.png` từ demo |
| 9 | INT8, TFLite Micro/ESP-DL, INA219, OLED; < 200 KB (ước tính < 150 KB), ≤ 1 điểm, < 4 giây | BM02 §5 nội dung 5, §6.1, §6.3; `assets/embedded.svg` là sơ đồ kế hoạch |
| 10 | Đã có / sẽ hoàn thiện (gồm kịch bản chạy lại toàn bộ bảng kết quả, bản đầy đủ và bản INT8); ví dụ r01 99,92% | BM02 §6.2; `baselines/powermf_fair_stats.json` (`rely` của r01); `assets/monitor-r01.png`, `assets/monitor-b203.png` chụp thật |
| 11 | Bốn đóng góp + ý nghĩa, ứng dụng, hiệu quả KT–XH | BM02 §7; số liệu: slide 5, 6 |
| 12 | Tiến độ **7 mốc** theo §9 (03/2027 90%, 04/2027 100%, 05/2027); kinh phí 1,40 + 1,00 + 0,55 = 2,95 triệu | BM02 §9, §10 |
| 13 | Ba câu hỏi nghiên cứu + bốn tiêu chí hoàn thành | BM02 §2.2, §6.1 |
| 14 | Kết luận: thông điệp + bốn con số đáng nhớ | Tổng hợp từ slide 5, 6, 8, 9 |

## Cách đọc số liệu — những điểm không được nói quá

- 89,5% là phần khoảng cách 4 kênh ↔ 1 kênh mà mô hình lấy lại được (BM02 nêu ở §2.1), **không** phải kết quả vượt 4 kênh.
- Power-MF một kênh là **biến thể do nhóm dựng** từ mã nguồn gốc, không phải cấu hình tác giả công bố.
- Chênh lệch với 4 kênh có KTC [−3,08; +0,27] → **chưa** chứng minh tương đương.
- Ngoài miền: 74,28% (PSD) là quy tắc cơ sở và chưa đạt mục tiêu ≥ 80%; gate trượt Holm (p = 0,051); peakprob (82,01%) chọn sau khi xem kết quả nên chỉ là thăm dò.
- 15 bản trùng đã được ban tổ chức CinC ghi nhận; nhóm **định lượng mức ảnh hưởng**, không tuyên bố phát hiện đầu tiên.
- Không tuyên bố phát minh TCN hay đạt mục tiêu phần cứng; slide 9 và 8 ghi rõ là kế hoạch / cần nghiệm thu.
- 99,92% trên slide 10 là F1 của **một bản ghi (r01)**, không phải trung bình 22 sản phụ (97,56%).
- So sánh kiến trúc (§5.3) không còn slide riêng; trả lời miệng bằng phụ lục trong `loi_thoai.md`.
- Kinh phí là dự toán đề xuất, không phải chi phí đã phát sinh.

## Hình và ảnh

- `signal-mix.svg`, `embedded.svg`, `leakage.svg`, `data-split.png`: sơ đồ minh họa, không phải bằng chứng thực nghiệm.
- `model-probability.png`, `model-beats.png`, `reliability-case.png`: cắt từ demo thật, không tính lại hay sửa giá trị.
- `monitor-r01.png`, `monitor-b203.png`: ảnh chụp màn hình `/monitor` thật (Chrome DevTools Protocol).
- `tdtu-logo.png`: logo gốc, giữ nguyên tỉ lệ và màu.

## Thiết kế

Nền trắng, một màu nhấn xanh (`#00557f`), xanh lá cho kết quả tích cực và đỏ nâu cho cảnh báo. Tiêu đề 43 px, chữ nội dung 18–28 px, số liệu chính 30–98 px trên khung 1280×720. Mỗi slide một thông điệp, số trang ở góc phải, logo ở góc trái như mọi slide TDTU.

Kiểm tra bố cục sau mỗi lần sửa: `python3 qa_layout.py` (phải in `OK: không có phần tử tràn khung`). Xuất PDF: `sh render.sh`.
