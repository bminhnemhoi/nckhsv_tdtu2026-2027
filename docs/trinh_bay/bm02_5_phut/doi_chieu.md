# Đối chiếu nội dung — bản 13 slide

Mọi slide bám theo BM02 (`BM02_De_cuong_nghien_cuu_DA_CHINH_SUA.pdf`). Số liệu lấy từ tệp bằng chứng của dự án, không lấy từ bài báo khác hay giao thức khác.

Bản 15 slide gộp các cặp trùng nội dung của bản 18 slide: mục đích vào slide lý do, dữ liệu vào giao thức, phương pháp vào phần huấn luyện, kết quả khả thi vào biểu đồ trong miền, đóng góp vào ý nghĩa, câu hỏi vào tiêu chí. Bản 13 slide gộp hai slide cũ — trùng lặp dữ liệu và kết quả ngoài miền — thành một slide benchmark đặt RelyFetal cạnh phương pháp 4 kênh tốt nhất chạy lại được; phần trùng lặp chuyển xuống dòng chú thích dưới bảng. Bản 14 slide bỏ slide phụ lục so sánh kiến trúc (nội dung vẫn nằm trong phụ lục câu hỏi của `loi_thoai.md`).

| Slide | Nội dung | Nguồn |
|---|---|---|
| 1 | Tên đề tài, tác giả, GVHD | BM02 §1. Ba số nhanh (97,56% · 113 nghìn tham số · 8 tháng) đã bỏ khỏi bìa — chúng xuất hiện ở slide 4, 5 và 11 |
| 2 | Lý do chọn đề tài + hình một kênh (mẹ + thai + nhiễu) + câu rào đạo đức | BM02 §2.1; `assets/signal-mix.svg` là hình minh họa, không phải bản ghi. Tiêu chí số **không** lặp ở đây — để slide 12 |
| 3 | Ba nguồn dữ liệu (ADFECGDB + Silesia, CinC set-a, MIT-BIH) + chia 11 lượt, mỗi lượt 2 sản phụ kiểm tra | BM02 §4, §5 nội dung 1; `assets/data-split.png`. Phần thống kê (±50 ms, bootstrap, Wilcoxon/Holm) đã **bỏ khỏi slide** — chỉ nêu miệng khi được hỏi |
| 4 | Năm khâu xử lý + cách huấn luyện (4 giây, Gauss σ = 12 ms, BCE có trọng số + tăng cường, AdamW, 3 hạt giống, ≥ 250 ms) + đồ thị thật a09 | BM02 §5 nội dung 2–3; `assets/model-probability.png`, `assets/model-beats.png` cắt từ demo |
| 5 | Kết quả bước đầu 9/2026: F1 **97,56%** trên 22 sản phụ, 113 nghìn tham số, 0,48 MB. Phần đối chứng với Power-MF đã **chuyển sang slide 6** để mỗi slide một thông điệp | BM02 §2.1; `baselines/powermf_fair_stats.json` → `so_sanh.tat_ca_22` |
| 6 | Benchmark với phương pháp 4 kênh tốt nhất: RelyFetal **97,56%** (113.481 tham số) · Power-MF 4 kênh **98,83%** (0 tham số học) (chênh −1,27 [−3,08; +0,27]) · Power-MF 1 kênh **86,71%** (+10,85 [6,80; 15,40], 22/22). Hai ô số bên dưới đã **bỏ** (KTC và 22/22 nêu miệng); chú thích dưới bảng: Varanini 2014 công bố 97,04% bằng bộ chấm khác, chưa chạy lại được; 15 bản trùng CinC đã loại, tránh thổi phồng 3,27–7,18 điểm, còn 60 bản sạch | BM02 §2.1; `baselines/powermf_fair_stats.json` → `so_sanh.tat_ca_22`; `survey/facts_phase4.json` mục A (trùng lặp), mục B (74,28% PSD); `survey/scout_baselines.md` dòng ~23 (Varanini 2014); 113.481: `model/train_22_log.txt`; Power-MF không học tham số: `survey/RO_RI_VANLIEU.md` dòng 110, `survey/scout_baselines.md` §3.1 |
| 7 | Ca khó a02; 12 chỉ số = 6 tín hiệu + 6 đầu ra; AUROC ≥ 0,85 | BM02 §5 nội dung 4; `assets/reliability-case.png` từ demo |
| 8 | INT8, TFLite Micro/ESP-DL, INA219, OLED; < 200 KB (ước tính < 150 KB), ≤ 1 điểm, < 4 giây | BM02 §5 nội dung 5, §6.1, §6.3; `assets/embedded.svg` là sơ đồ kế hoạch |
| 9 | Đã có / sẽ hoàn thiện (gồm kịch bản chạy lại toàn bộ bảng kết quả, bản đầy đủ và bản INT8); ví dụ r01 99,92% | BM02 §6.2; `baselines/powermf_fair_stats.json` (`rely` của r01); `assets/monitor-r01.png`, `assets/monitor-b203.png` chụp thật |
| 10 | Hai đóng góp (12 chỉ số của cổng · hệ thống gọn 0,48 MB) + ứng dụng, hiệu quả KT–XH | BM02 §7; số liệu: slide 7 và 5. Hai thẻ đầu (89,5% và 15 bản) đã **bỏ khỏi slide** vì lặp lại slide 5 |
| 11 | Tiến độ **7 mốc**, mỗi mốc một ý chính (chuẩn bị dữ liệu → huấn luyện → cổng → nén/chạy bo → demo → nghiệm thu) theo §9; kinh phí 1,40 + 1,00 + 0,55 = 2,95 triệu | BM02 §9, §10 |
| 12 | Ba câu hỏi nghiên cứu, mỗi câu kèm tiêu chí §6.1 và **trạng thái thật hôm nay**: 97,56% đạt / 74,28% chưa; AUROC 0,90 trên ADFECGDB / 0,75 gộp; INT8 chưa có | BM02 §2.2, §6.1; 97,56%: `baselines/powermf_fair_stats.json`; 74,28%: `facts_phase4.json` mục B; AUROC: `fsqi/gate_meta.json` (`cv_auroc_adfecgdb_mean`, `oof_auroc_pooled`) |
| 13 | Kết luận: thông điệp + bốn con số đáng nhớ | Tổng hợp từ slide 5, 6, 7, 8 |

## Cách đọc số liệu — những điểm không được nói quá

- 89,5% là phần khoảng cách 4 kênh ↔ 1 kênh mà mô hình lấy lại được (BM02 nêu ở §2.1), **không** phải kết quả vượt 4 kênh.
- Power-MF một kênh là **biến thể do nhóm dựng** từ mã nguồn gốc, không phải cấu hình tác giả công bố.
- Chênh lệch với 4 kênh có KTC [−3,08; +0,27] → **chưa** chứng minh tương đương.
- AUROC cổng: 0,90 là **kiểm tra chéo trên ADFECGDB** (5 bản ghi, 1.500 đoạn); gộp ngoài miền chỉ 0,75 — **dưới mục tiêu 0,85**. Không được nói "cổng đạt mục tiêu" mà không kèm điều kiện này.
- Phần cứng: **chưa có** bản INT8 và chưa có suy luận mạng trên ESP32-S3. Firmware trong `analysis/hardware_simulator/` là mô phỏng HIL (nhịp tim thai gán hằng số 142 bpm), **không phải** chạy mô hình.
- 0,48 MB là mô hình PyTorch float32 (482.133 byte), không phải bản nén.
- Ngoài miền: 74,28% (PSD) là quy tắc cơ sở và chưa đạt mục tiêu ≥ 80%; gate trượt Holm (p = 0,051); peakprob (82,01%) chọn sau khi xem kết quả nên chỉ là thăm dò.
- 15 bản trùng đã được ban tổ chức CinC ghi nhận; nhóm **định lượng mức ảnh hưởng**, không tuyên bố phát hiện đầu tiên.
- Không tuyên bố phát minh TCN hay đạt mục tiêu phần cứng; slide 8 và 7 ghi rõ là kế hoạch / cần nghiệm thu.
- 99,92% trên slide 9 là F1 của **một bản ghi (r01)**, không phải trung bình 22 sản phụ (97,56%).
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
