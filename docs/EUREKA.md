# Giải thưởng Euréka và đề tài RelyFetal — thông tin xác minh, bảng đối chiếu, đánh giá cửa

Soạn ngày 12/09/2026 cho chủ nhiệm Ngô Bình Minh (TDTU); cập nhật cùng ngày sau thẩm định vòng 7 (`docs/nhat_ky/THAMDINH_VONG7.md`): bỏ số cổng từ chối đo trên 75 bản nhiễm, bỏ số logit từ phân tích đã rút, sửa kế hoạch "bộ thứ ba" (không có bộ công khai nào có nhãn), thêm mục 4b cho trường hợp lỡ hạn 2026. Tài liệu tách bạch bốn loại phát biểu:
**[XÁC MINH]** = có nguồn chính thức đọc được; **[CHƯA XÁC MINH]** = chưa tìm được nguồn chính thức, phải hỏi Đoàn trường; **[SUY LUẬN]** = suy ra từ dữ kiện; **[KHUYẾN NGHỊ]** = ý kiến.

Mọi con số về đề tài trong tài liệu này truy ngược về tệp trên đĩa (ghi kèm). Không dùng các con số đã rút (xem mục 6).

> **Cập nhật 17/09/2026 (thẩm định cuối):** đã sửa ngay trong tệp — (1) các số STV ngoài miền cũ (lệch +20,50 ms trên CinC;
> 0,13 ms khi F1 ≥ 99,5; 25,78 ms khi F1 < 90) **đã rút** vì tính trên mẫu CinC 10 bản và mẫu 32 bản có a03 a04 a05 a08
> là bản trùng dữ liệu huấn luyện (`docs/DE_CUONG_HIEN_TRANG.md` mục 15.4); số STV dùng được duy nhất là +0,33 ms trong
> miền, n = 5; (2) 0,934 là cổng 22 ca tính trên 11/22 chủ thể, chỉ ở dạng phân tích — đèn trong demo là cổng 5 ca,
> 0,721 [0,517; 0,898] trên 5 bản CinC sạch; (3) 82,01 luôn kèm 74,28 · 80,72 · 81,01; (4) số mã và kiểm thử: ≈31.000
> dòng Python, 109 kiểm thử; tốc độ ≈920× thời gian thực; (5) cổng không "tự biết khi nào không đáng tin" — chỉ báo khi
> thấy dấu hiệu xấu, không phải lần nào cũng thấy (a57 đèn xanh, F1 17,02).

---

## 1. Thông tin về Giải thưởng — chỉ ghi những gì xác minh được

### 1.1. Đơn vị tổ chức, kỳ hiện tại

| Mục | Nội dung | Loại | Nguồn |
|---|---|---|---|
| Tên | Giải thưởng Sinh viên Nghiên cứu Khoa học – Euréka, lần thứ XXVIII (28), năm 2026 | XÁC MINH | khoahoctre.com.vn/eureka-2026/ ; baovanhoa.vn (bài "TP.HCM khởi động Giải thưởng Euréka lần thứ 28") |
| Đơn vị tổ chức | Thành Đoàn TP.HCM, Đại học Quốc gia TP.HCM và Sở Khoa học và Công nghệ TP.HCM; cơ quan thường trực: Trung tâm Phát triển Khoa học và Công nghệ Trẻ (TST) | XÁC MINH | baovanhoa.vn; eureka.khoahoctre.com.vn |
| Ngày phát động 2026 | Hội nghị triển khai ngày 18/8/2026 tại Trung tâm Khởi nghiệp sáng tạo TP.HCM | XÁC MINH | baovanhoa.vn; baotintuc.vn |
| Đối tượng | Sinh viên Việt Nam và quốc tế đang học tại các trường Đại học, Cao đẳng, Học viện tại Việt Nam; cá nhân hoặc nhóm không quá 05 sinh viên | XÁC MINH | khoahoctre.com.vn/eureka-2026/ ; thông báo cepm.ftu.edu.vn (lần 28); Thể lệ 2021 Điều 1 |
| Số lĩnh vực 2026 | 15 lĩnh vực | XÁC MINH | khoahoctre.com.vn/eureka-2026/ ; baovanhoa.vn |
| Danh sách đủ 15 lĩnh vực 2026 | Các nguồn đọc được chỉ nêu một phần: Công nghệ thông tin, Công nghệ thực phẩm, Hành chính – Pháp lý, Hóa/Công nghệ Hóa – Dược, Giáo dục, Nông lâm ngư nghiệp, Xã hội nhân văn, Khoa học Y – Dược, Kinh tế, Kỹ thuật công nghệ, Quy hoạch – Kiến trúc – Xây dựng, Sinh học/Công nghệ Sinh – Y sinh, Tài nguyên và Môi trường. **Chưa đọc được văn bản thể lệ 2026 có bảng đủ 15 lĩnh vực và chuyên ngành con.** | CHƯA XÁC MINH ĐỦ | Tệp thể lệ 2026 nằm trong thư mục Google Drive dẫn từ khoahoctre.com.vn/eureka-2026/ (chưa tải được bằng công cụ). Chủ nhiệm cần tải và đọc trực tiếp. |
| Quy mô kỳ trước (2025, lần 27) | 2.179 đề tài, hơn 7.500 thí sinh, 161 đơn vị | XÁC MINH | baovanhoa.vn; dhannd.bocongan.gov.vn |
| Kết quả kỳ 26 (trao 08/12/2024) | 187 đề tài đoạt giải trên ~2.000 dự thi: 15 Nhất, 14 Nhì, 18 Ba, 140 Khuyến khích; tổng 414 triệu đồng | XÁC MINH | vnexpress.net (bài "187 nghiên cứu sinh viên đoạt Giải thưởng Euréka") |
| Tổng giá trị giải 2026 | Trên 500 triệu đồng | XÁC MINH | khoahoctre.com.vn/eureka-2026/ |

### 1.2. Mốc thời gian

| Mốc | Nội dung | Loại | Nguồn |
|---|---|---|---|
| Đăng ký trực tuyến cấp thành (2026) | Từ 08g00 ngày 01/9/2026 đến hết ngày 25/9/2026, tại nopdetai.khoahoctre.com.vn; tài khoản đăng nhập cấp cho cán bộ phụ trách của **trường**, không phải sinh viên | XÁC MINH | eureka.khoahoctre.com.vn; khoahoctre.com.vn/eureka-2026/ ; Thể lệ 2021 Điều 6 (cơ chế tài khoản) |
| Hạn nội bộ các trường (2026) | Các trường chốt hồ sơ **trước** hạn cấp thành. Ví dụ đọc được: ĐH Ngoại thương (CEPM) hạn 17g00 thứ Sáu 04/9/2026; ĐH CNTT (UIT) đăng ký 04/8–20/8/2026 | XÁC MINH (cho hai trường đó) | cepm.ftu.edu.vn; forum.uit.edu.vn |
| **Hạn nội bộ TDTU 2026** | **Chưa tìm được thông báo của TDTU.** Theo hai ví dụ trên, hạn nội bộ của các trường thường rơi vào tháng 8 – đầu tháng 9; hôm nay là 12/9/2026 nên khả năng cao đã qua hoặc còn rất ít ngày. | CHƯA XÁC MINH — hỏi Đoàn trường/Phòng QLKH TDTU **ngay trong tuần này** | — |
| Các vòng | Sơ tuyển cấp trường → Bán kết (hội đồng khoa học theo lĩnh vực, thang 100 điểm) → Chung kết (xếp hạng, trình bày kết quả) → Tổng kết, trao giải | XÁC MINH (cấu trúc) | eureka.khoahoctre.com.vn; Thể lệ 2021 Điều 3 |
| Thời điểm bán kết, chung kết 2026 | Chưa công bố trên các trang đọc được. Tham chiếu kỳ 27 (2025): một hội đồng bán kết họp sáng 02/11/2025, thí sinh **thuyết trình trực tiếp/trực tuyến** trước hội đồng; kỳ 26 trao giải ngày 08/12/2024 | CHƯA XÁC MINH cho 2026; SUY LUẬN: bán kết ~tháng 11, chung kết – trao giải ~tháng 12 | dhannd.bocongan.gov.vn; vnexpress.net |

### 1.3. Tiêu chí chấm điểm (thang 100, dùng ở vòng bán kết)

Nguồn: Thể lệ Euréka lần 23 năm 2021, Điều 3 (bản PDF đọc trực tiếp từ eureka.khoahoctre.com.vn) — **xác nhận lại nguyên văn** trên trang "Tiêu chí đánh giá đề tài dự thi Euréka lần 25 năm 2023" (khoahoctre.com.vn). Chưa đọc được bản 2026; **[SUY LUẬN]** thang này ổn định qua nhiều năm nên khả năng giữ nguyên cao, nhưng phải đối chiếu bản 2026 khi tải được.

| Nhóm | Tiêu chí | Điểm |
|---|---|---|
| 1. Mục đích, ý nghĩa và khả năng ứng dụng (30) | 1a. Mục đích và ý nghĩa nghiên cứu rõ ràng, cụ thể | 10 |
| | 1b. Giới thiệu được tính khoa học, tính sáng tạo, tính mới trong chuyên ngành, trong cách đặt vấn đề và giải quyết vấn đề | 20 |
| 2. Nội dung chuyên môn và phương pháp nghiên cứu (50) | 2a. Nội dung nghiên cứu phù hợp, phương pháp và kết quả nghiên cứu được xác định | 30 |
| | 2b. Có những giải pháp, kiến nghị, đề xuất có giá trị | 20 |
| 3. Hình thức trình bày (20) | 3a. Trình bày khoa học, rõ ràng, có biểu mẫu, hình minh hoạ chi tiết | 10 |
| | 3b. Có trích dẫn cụ thể các nguồn tài liệu tham khảo | 10 |

Giải Đặc biệt (2021): chọn trong các giải Nhất, yêu cầu **từ 95 điểm trở lên**.

### 1.4. Hồ sơ và hình thức (xác minh từ Thể lệ 2021 Điều 4–6 và các thông báo 2026)

| Yêu cầu | Nội dung | Nguồn |
|---|---|---|
| Phiếu đăng ký (mẫu M01) | Có ảnh 3×4; phần "Tóm tắt công trình, những vấn đề mới" **không quá 100 từ**; tên GVHD (học hàm, học vị); cam kết số liệu trung thực có nguồn gốc; xác nhận của trường | Thể lệ 2021; cepm.ftu.edu.vn 2026 |
| Giấy tờ | Bản sao CCCD của mọi thành viên (không cần công chứng) | Thể lệ 2021; cepm.ftu.edu.vn 2026 |
| Công trình toàn văn | 02 quyển nộp ở vòng bán kết (2021). UIT 2026: "bản thuyết minh đề tài (Word + PDF)". Tiếng Việt hoặc tiếng Anh. | Thể lệ 2021 Điều 6; forum.uit.edu.vn |
| Bố cục bắt buộc | 1. Đặt vấn đề · 2. Tổng quan tài liệu · 3. Mục tiêu – Phương pháp · 4. Kết quả – Thảo luận · 5. Kết luận – Đề nghị · 6. Tài liệu tham khảo, phụ lục, danh mục công trình của tác giả | Thể lệ 2021 Điều 4 |
| Hình thức | A4, Times New Roman cỡ 13, đánh số trang giữa đầu trang; mục đánh số 1., 1.1., 1.1.1.; **tóm tắt tối đa 1 mặt A4 đặt ở trang đầu**; bìa giấy xanh nước biển, gáy dán keo; **không ghi tên tác giả, tên trường, tên GVHD, không lời cảm ơn, không ký tên** ở bất kỳ chỗ nào (chấm mù) | Thể lệ 2021 Điều 5 |
| Poster | 0,8 m × 1,3 m khổ dọc; nộp file (JPG/PDF) khi đăng ký | Thể lệ 2021 Điều 6; cepm.ftu.edu.vn; forum.uit.edu.vn |
| Phiếu đánh giá hội đồng cấp trường | Bắt buộc kèm hồ sơ | Thể lệ 2021 Điều 6 |
| Bài báo khoa học (mẫu M04) | Chỉ yêu cầu với đề tài **vào chung kết**; Word, A4, tóm tắt 250–350 từ tiếng Việt, 5–7 từ khoá | Thể lệ 2021 mẫu M04 |
| Giới hạn số lượng | Mỗi đơn vị tối đa 10 đề tài/lĩnh vực (thêm 1–3 nếu trường có giải kỳ trước) | Thể lệ 2021 Điều 1; cepm.ftu.edu.vn 2026 |
| Số trang tối đa toàn văn | **Không thấy quy định** trong Thể lệ 2021 (chỉ giới hạn tóm tắt 1 trang). Bản 2026 chưa đọc. | CHƯA XÁC MINH |

### 1.5. Cơ cấu giải (theo Thể lệ 2021; trang UIT về kỳ 2025 xác nhận mức 10/5/3 triệu)

Mỗi lĩnh vực: 01 giải Nhất 10 triệu + Bằng khen Bộ KH&CN + Huy hiệu Tuổi trẻ sáng tạo (T.Ư Đoàn); 01 giải Nhì 5 triệu; 01 giải Ba 3 triệu; các giải Khuyến khích 2 triệu (kèm bằng khen Thành Đoàn). Giải Đặc biệt 20 triệu. Đề tài giải Nhất/Đặc biệt được xem xét đăng trên Chuyên san Khoa học trẻ (ISSN 2354-1105) hoặc Tạp chí Phát triển KH&CN ĐHQG-HCM sau phản biện. GVHD của đề tài giải Nhất được bằng khen ĐHQG-HCM. **[CHƯA XÁC MINH]** mức tiền 2026.

### 1.6. Lĩnh vực nên đăng ký — [KHUYẾN NGHỊ, có lập luận]

| Lựa chọn | Lý do nên | Rủi ro |
|---|---|---|
| **Công nghệ thông tin** — chuyên ngành *Trí tuệ nhân tạo* (hoặc *Điện tử viễn thông*) — **khuyến nghị chính** | Đóng góp của đề tài là thuật toán, học máy, xử lý tín hiệu, thống kê đánh giá và mã nguồn (≈31.000 dòng .py — `wc -l` 136 tệp, 17/09; 109 kiểm thử = 43 trong `tests/` + 66 trong `demo/test_core.py`, đếm bằng `pytest --collect-only`; demo, API). Hội đồng CNTT hiểu "cổng từ chối", "rò rỉ dữ liệu", "F1 mức chủ thể". | Hội đồng có thể hỏi "sản phẩm đâu" → trả lời bằng demo + API + 0,48 MB chạy trên vi điều khiển (hướng). Lĩnh vực đông đề tài nhất, cạnh tranh cao. |
| Kỹ thuật công nghệ — *Điện, điện tử* | Nếu chỉ tiêu CNTT của TDTU đã đầy (10 đề tài/lĩnh vực) | Hội đồng thiên phần cứng; đề tài chưa có phần cứng. |
| Khoa học Y – Dược | Ứng dụng là sản khoa | **Không khuyến nghị**: hội đồng y sẽ đòi kiểm chứng lâm sàng, mà chỉ số STV của đề tài mới có một số dùng được (+0,33 ms trong miền, n = 5, `analysis/clinical_results.json`; số STV ngoài miền đã rút) và chưa có bác sĩ đồng hành. |

---

## 2. Bảng đối chiếu: từng tiêu chí Euréka ↔ đề tài

Mọi số liệu: `survey/facts_phase4.json` (nguồn tổng hợp), `analysis/dulieu_results.json` (khoá `chon_kenh_60_sach`), `baselines/powermf_fair_stats.json` và `analysis/recovery_ratio.json` (22 chủ thể, tỉ lệ lấy lại), `analysis/gate22_results.json` (cổng, 22 chủ thể LOSO — `gate22_cinc.json` tính trên 75 bản gồm 15 bản nhiễm, **không trích**), `analysis/kientruc_results.json` (kiến trúc), `analysis/clinical_results.json` (STV), `adapt/adapt_results.json` (thích nghi miền), `analysis/xacnhan_results.json` (logit 22 chủ thể, bộ thứ ba, âm tính giả), `survey/ro_ri_vanlieu.json` (y văn về chồng lấn).

| Tiêu chí (điểm) | Đề tài đáp ứng thế nào | Bằng chứng (tệp) | Điểm yếu hội đồng sẽ thấy | Việc cần làm |
|---|---|---|---|---|
| 1a. Mục đích, ý nghĩa rõ (10) | Rõ: đo biến thiên nhịp tim thai từ **một** điện cực bụng để tiến tới theo dõi tại nhà; điểm khác biệt là hệ thống **báo khi thấy dấu hiệu kết quả chưa đáng tin** (không phải lần nào cũng thấy). | Sổ tay mục 01–02; `docs/TOM_TAT_1_TRANG.md`; phần Introduction của bản hội nghị 4 trang viết lại cho CinC 2027 | Chưa có ý kiến bác sĩ sản nào xác nhận nhu cầu; câu "theo dõi tại nhà" đang là giả thuyết ứng dụng. | Xin GVHD giới thiệu 1 bác sĩ sản/1 kỹ thuật viên CTG để phỏng vấn 30 phút; ghi 3 câu trích dẫn (có xin phép) vào phần Đặt vấn đề. |
| 1b. Tính khoa học, sáng tạo, tính mới (20) | Ba đóng góp có ranh giới rõ: (i) đo được "một kênh lấy lại 89,49 % [81,4; 103,2] lợi ích của bốn kênh" (jackknife bỏ từng chủ thể 88,6–93,4 %); (ii) cổng từ chối không nhãn (12 chỉ số, 6 dựa trên đầu ra mạng — không độc lập với mạng): LOSO trên 22 chủ thể, AUROC trong bản ghi 0,934 [0,872; 0,981] tính trên 11/22 chủ thể có đoạn xấu, chỉ ở dạng phân tích, chưa có trong demo (đèn demo là cổng 5 ca, 0,721 [0,517; 0,898] trên 5 bản CinC sạch), xếp đúng 3 bản khó nhất vào 3 hạng chót (ngẫu nhiên 1/1540); (iii) quy tắc chọn kênh mù nhãn trên 60 bản sạch: PSD 74,28 · gate 80,72 · gate4 81,01 · peakprob 82,01 (hậu kiểm) · trần 83,60; peakprob − PSD +7,73 [+3,82; +12,41], p Holm 0,0039, bản F1 < 50 từ 16 xuống 9. Cộng thêm: kiểm toán bộ kiểm tra — chồng lấn set-a ↔ ADFECGDB đã được ban tổ chức ghi nhận (Silva 2013 Bảng 1; Clifford 2014); nhóm định danh bằng đo lường đúng 15 bản (NCC = 1,0000, cửa sổ 0–60/120–180/240–300 s) và đo mức thổi phồng 3,27–7,18 điểm. | `analysis/recovery_ratio.json`; `analysis/gate22_results.json`; `analysis/dulieu_results.json`; `survey/ro_ri_vanlieu.json` | Trung bình vẫn **thua** Power-MF 4 kênh 1,27 điểm; peakprob là lựa chọn **hậu kiểm** (quy tắc kế hoạch chọn là gate, gate trượt Holm p = 0,051; gate4 cũng ghi trước, qua Holm p = 0,015; trên thang logit 22 chủ thể gate vẫn đứng đầu ở 2/3 cách kẹp, peakprob hạng 3 — `analysis/xacnhan_results.json`); 5/24 quy tắc một đặc trưng cũng xếp đúng 3 bản khó nên chưa chứng minh cổng học là cần thiết; không có bộ công khai thứ ba có nhãn fQRS thật để nhân rộng (NIFEADB, NInFEA, nifecgdb, set-b — đã kiểm 12/09). Hội đồng sinh viên có thể coi "tự rút lại" là yếu nếu kể sai cách. | Kể theo khung "phép đo + ranh giới": mỗi điểm mới đi kèm một câu giới hạn. Không dùng từ tự khen. Nhân rộng peakprob chỉ làm được nếu tự chú thích một bộ có chuyên gia kiểm hoặc xin được dữ liệu ngoài — ghi là "đang xin", không hứa. |
| 2a. Nội dung phù hợp, phương pháp và kết quả xác định (30) | Điểm mạnh nhất. Baseline mạnh nhất (Power-MF) được **chạy lại** qua GNU Octave và kiểm chứng ngoài: B1 99,40 vs 99,46 tác giả công bố; đối chứng 1 kênh của chính Power-MF; thống kê **mức chủ thể** (cluster bootstrap, Wilcoxon, Holm, TOST); 7 họ kiến trúc cùng tham số; 4 phương pháp thích nghi miền đều báo cáo âm tính; phổ lỗi có mức ngẫu nhiên đối chứng; 109 kiểm thử (43 + 66). | `baselines/powermf_results.json`, `baselines/powermf_published.json`; `analysis/kientruc_results.json`; `analysis/THICHNGHI.md`; `analysis/chandoan_results.json`; `tests/` | Chỉ 22 chủ thể (tự tính cần ~50); 77 % thời lượng huấn luyện từ nhãn gián tiếp (Silesia B1); chưa có trung tâm ghi thứ hai; DPSS (đối thủ thứ hai) chưa chạy lại; kết quả chính 1 seed (seed 1 chỉ có tệp huấn luyện: 97,59 so với 97,56, `model/train_22_seed1.json`). | Chạy 3 seed cho kết quả chính (rẻ, làm được trước hạn); viết rõ mục "Giới hạn" ngay trong Kết quả – Thảo luận chứ không giấu ở cuối. |
| 2b. Giải pháp, kiến nghị có giá trị (20) | Có sản phẩm chạy được: demo Gradio 5 tầng tín hiệu + đèn tin cậy, FastAPI, mô hình 113.481 tham số / 0,48 MB / 4,35 ms mỗi cửa sổ 4 s (≈920× nhanh hơn thời gian thực trên CPU). Kiến nghị: dùng cổng từ chối làm bộ lọc chất lượng trước khi tính chỉ số lâm sàng — là hướng cần kiểm, chưa có số ngoài miền dùng được (số STV ngoài miền cũ đã rút). | `demo/results/smoke_app.json`, `demo/results/demo_check_2modes.json`; `analysis/clinical_results.json`; `api/` | Chưa dùng được làm máy đo STV độc lập (số STV dùng được duy nhất là +0,33 ms trong miền, n = 5); đèn xanh vẫn có thể sai (a57 F1 17,02); chưa có phần cứng; "miếng dán tại nhà" là tầm nhìn, chưa có nguyên mẫu. | Nói thẳng ranh giới; đưa lộ trình 3 bước (dữ liệu có nhãn mới ngoài bộ đã dùng → trung tâm ghi thứ hai → nguyên mẫu phần cứng) vào Kết luận – Đề nghị. Không hứa thiết bị y tế. |
| 3a. Hình thức, biểu đồ, hình minh hoạ (10) | Đã có 9 hình phân tích (`analysis/fig_*.png`), 16 ảnh chụp demo, sổ tay HTML, đề cương LaTeX 140 trang (bản nháp hội nghị 4 trang cũ trong `paper/` toàn số 75 bản — phải viết lại trên 60 bản sạch trước khi dùng). | `analysis/fig_chonkenh.png`, `fig_gate22.png`, `fig_dulieu.png`, `fig_kientruc` (bảng), `demo/screenshots/` | Đề cương 140 trang **quá dài** cho hội đồng sinh viên; hình đang là hình phân tích nội bộ, chưa có chú thích dễ đọc; phải **bỏ tên tác giả/trường/GVHD** trong toàn văn theo thể lệ. | Rút xuống toàn văn khoảng 40–60 trang (khuyến nghị, thể lệ không ghi trần); vẽ lại 3 hình chính (mục C của kế hoạch); dò toàn văn để xoá mọi tên. |
| 3b. Trích dẫn cụ thể (10) | `refs.bib` trong `paper/`; khảo sát 30 bài (`docs/Bao_cao_30_paper.pdf`); `survey/facts_phase2.json`. | các tệp trên | Rủi ro duy nhất là DOI/tên bài không chính xác. | Kiểm lại từng DOI trong refs.bib bằng tay trước khi nộp; không thêm tài liệu chưa đọc toàn văn. |
| Trình bày trước hội đồng (bán kết/chung kết, không tính điểm riêng trong thang 100 nhưng quyết định thứ hạng) | Chủ nhiệm có câu chuyện mạnh: tự kiểm và định danh 15 bản trùng trong bộ chuẩn công cộng (chồng lấn mà ban tổ chức đã ghi nhận từ 2013 và nhóm từng bỏ sót — không nói "em phát hiện"), tự rút ba tuyên bố, chạy lại baseline của đối thủ. Demo trực tiếp 1 bản tốt (r01) + 1 bản bị từ chối (a02). | `docs/KICH_BAN_TRINH_BAY.md`; `demo/README.md` | Nếu kể "em sai nhiều" mà không kể "vì thế số còn lại đáng tin" thì hội đồng hiểu nhầm. | Tập theo kịch bản; luôn nói rút lại → đã sửa → kết quả chính **mạnh lên** trên dữ liệu sạch (+7,73 trên 60 bản sạch; hiệu số trên 75 bản nhiễm nhỏ hơn và đã rút, không đọc số cũ trước hội đồng). |

---

## 3. Đánh giá thẳng: có cửa không, ở vòng nào, cần gì

**Có cửa — nhưng gần như chắc chắn là kỳ 2027 (lần 29), không phải kỳ 2026.** Lý do:

1. **[XÁC MINH]** Cổng đăng ký cấp thành 2026 đóng 25/9/2026 và chỉ trường nộp được; **[CHƯA XÁC MINH]** hạn nội bộ TDTU, nhưng hai trường tra được đã đóng từ 20/8 và 04/9. **[SUY LUẬN]** Xác suất TDTU còn nhận hồ sơ mới sau 12/9 là thấp. Việc đầu tiên tuần này: hỏi Đoàn trường/Phòng QLKH TDTU.
2. **[XÁC MINH]** Hồ sơ cần *phiếu đánh giá của hội đồng khoa học cấp trường* và xác nhận của trường. Đề tài NCKH sinh viên 2026–2027 của chủ nhiệm mới ở buổi gặp đầu với GVHD, chưa qua hội đồng cấp trường nào → thiếu giấy tờ bắt buộc cho 2026.
3. **[SUY LUẬN]** Nếu bằng cách nào đó nộp kịp 2026: nội dung chuyên môn (nhóm 2, 50 điểm) đã vượt mặt bằng sinh viên thường thấy; hình thức (nhóm 3) chưa đúng thể lệ (140 trang, có tên). Vào bán kết là khả thi; vào chung kết cần trình bày tốt; giải cao khó vì thiếu bác sĩ đồng hành và chưa có bộ thứ ba.

**Kịch bản khuyến nghị — Euréka lần 29 (2027):**

| Vòng | Nhận định | Điều kiện cần |
|---|---|---|
| Sơ tuyển cấp trường (TDTU) | Khả năng cao qua nếu GVHD ủng hộ | Đề tài NCKH cấp trường được nghiệm thu hoặc có biên bản hội đồng khoa; toàn văn đúng bố cục 6 phần |
| Bán kết (thang 100, thuyết trình) | Khả thi vào top của lĩnh vực nếu giữ được nhóm 2 mạnh và sửa nhóm 3 | Toàn văn 40–60 trang chấm mù; 3 hình chính rõ; 3 seed; bảng "số đã rút và vì sao" ở phụ lục |
| Chung kết / giải Ba – Nhì | Có cửa nếu có **một** trong hai: một bộ có nhãn fQRS thật ngoài dữ liệu đã dùng để chạy peakprob đúng một lần (không có bộ công khai nào — NIFEADB, NInFEA, nifecgdb, set-b đã kiểm 12/09; phải tự chú thích có chuyên gia kiểm hoặc xin ngoài), hoặc dữ liệu từ trung tâm ghi thứ hai | Cả hai đều cần bác sĩ đồng hành — việc xin GVHD giới thiệu ngay buổi gặp đầu |
| Giải Nhất / Đặc biệt (≥95) | Chưa có cửa ở hiện trạng | Cần thêm: bác sĩ đồng hành, chủ thể SNR thấp, bài báo đã được chấp nhận (hội đồng thường coi công bố là bằng chứng mạnh) |

**Điều Euréka trọng mà Q1 không trọng (và ngược lại):** hội đồng Euréka chấm "khả năng ứng dụng" và "giải pháp, kiến nghị" (tổng 40/100) — demo, mô hình nhẹ, API và lộ trình sản phẩm là điểm ghi; trong khi phần thống kê chủ thể, TOST, Holm chỉ nên xuất hiện ngắn gọn, đúng chỗ, tránh làm hội đồng mệt. Ngược lại, Q1 không quan tâm poster hay demo.

**Sự tự phê bình của đề tài là điểm mạnh nếu kể đúng cách:** kể theo thứ tự *đã kiểm → phát hiện lỗi → sửa → kết quả trên dữ liệu sạch còn mạnh hơn*, và kèm câu "mọi con số trong báo cáo truy ngược được về một tệp trong kho mã". Không kể theo kiểu liệt kê lỗi.

---

## 4. Việc cần làm ngay (theo thứ tự)

1. **Tuần này:** hỏi Đoàn trường / Phòng QLKH TDTU: (a) hạn nội bộ Euréka 2026 còn không; (b) quy trình sơ tuyển cấp trường; (c) chỉ tiêu lĩnh vực CNTT của TDTU; (d) xin bản thể lệ và kế hoạch 2026 (PDF) để đối chiếu mục 1.3–1.5 ở trên.
2. Tải thư mục thể lệ 2026 từ liên kết trên khoahoctre.com.vn/eureka-2026/ và cập nhật tài liệu này (đặc biệt: bảng 15 lĩnh vực, số trang, ngày bán kết/chung kết).
3. Xin GVHD xác nhận hướng nộp Euréka 2027 và lĩnh vực CNTT – AI; nhờ giới thiệu một bác sĩ sản.
4. Chạy 3 seed cho kết quả chính (seed 0 97,56 vs seed 1 97,59 đã có); tính lại số cổng từ chối trên 60 bản sạch; hỏi bác sĩ (qua GVHD) về khả năng tự chú thích 10–20 bản NIFEADB — không có bộ công khai thứ ba có nhãn fQRS thật.
5. Bắt đầu rút toàn văn theo dàn ý mục 5 dưới đây.

---

## 4b. Nếu lỡ hạn 2026: chuẩn bị Euréka 2027 (lần 29) thế nào

**[SUY LUẬN]** từ chu kỳ 2025–2026: phát động ~tháng 8, đăng ký cấp thành tháng 9, bán kết ~tháng 11, chung kết – trao giải ~tháng 12. Lịch 2027 chưa công bố; mọi mốc dưới đây là ước lượng, phải đối chiếu khi Thành Đoàn công bố. Hạn nội bộ TDTU cho cả 2026 lẫn 2027 **[CHƯA XÁC MINH]** — hỏi trong tuần này.

| Khi nào | Việc | Đầu ra | Vì sao |
|---|---|---|---|
| 9/2026 (tuần này) | Hỏi Đoàn trường / Phòng QLKH TDTU: hạn 2026 còn không; quy trình sơ tuyển cấp trường cho kỳ 2027; chỉ tiêu lĩnh vực CNTT; xin thể lệ 2026 (PDF) | Một email trả lời có ngày tháng | Không biết quy trình nội bộ thì không có phiếu hội đồng cấp trường — giấy bắt buộc |
| 9–10/2026 | GVHD đồng ý đứng tên; đăng ký đề tài NCKH sinh viên cấp trường 2026–2027 đúng kỳ | Quyết định giao đề tài | Euréka cần đề tài đã qua hội đồng cấp trường |
| 10–12/2026 | Viết và nộp bản tạp chí (Physiological Measurement, Q2 — sân nhà fECG); 3 hạt giống; tính lại số cổng từ chối trên 60 bản sạch; chuẩn bị bản 4 trang cho CinC 2027 (hạn abstract dự kiến 4/2027) | Số nộp tạp chí; preprint | Hội đồng coi công bố / đang phản biện là bằng chứng mạnh |
| 11/2026–3/2027 | Xin bác sĩ sản (qua GVHD): phỏng vấn 30 phút; hỏi khả năng tự chú thích 10–20 bản NIFEADB có chuyên gia kiểm; nếu được thì làm và chạy peakprob đúng một lần, báo cáo bất kể chiều | 3 câu trích dẫn bác sĩ (có xin phép); hoặc bộ chú thích tay | Nhóm 1a cần nhu cầu thật; nhóm 1b cần nhân rộng peakprob |
| 4–5/2027 | Nộp CinC 2027; nghiệm thu đề tài cấp trường; viết toàn văn Euréka 40–60 trang chấm mù theo dàn ý mục 5 | Toàn văn v1 + poster | Đúng thể lệ hình thức (nhóm 3) |
| 6–7/2027 | Phản biện nội bộ (GVHD); vẽ lại 3 hình chính; sửa toàn văn; tập trình bày 10 phút theo `docs/KICH_BAN_TRINH_BAY.md` (rút gọn cho hội đồng) | Toàn văn v2, poster, kịch bản 10 phút | Trình bày quyết định thứ hạng |
| 8–9/2027 | Sơ tuyển cấp trường; nộp cấp thành đúng hạn TDTU | Hồ sơ M01 + toàn văn + poster + phiếu hội đồng | — |
| ~11–12/2027 | Bán kết, chung kết | — | — |

Điều kiện tối thiểu để kỳ 2027 có cửa (theo mục 3): đề tài đã qua hội đồng cấp trường; một bài đang phản biện hoặc đã nhận (PM / CinC 2027); mọi số trên 60 bản sạch; toàn văn chấm mù đúng thể lệ. Điều kiện để có giải: thêm bác sĩ đồng hành và, nếu được, một bộ có nhãn mới để nhân rộng peakprob. Nếu 2026 bất ngờ còn hạn: chỉ nộp khi có đủ phiếu hội đồng cấp trường và toàn văn đã xoá tên — thiếu một trong hai thì không nộp, vì hồ sơ thiếu giấy bị loại ở sơ tuyển và không được gì.

---

## 5. Dàn ý báo cáo toàn văn Euréka (Phần C)

Bố cục bám đúng Điều 4 Thể lệ (6 phần). Độ dài **[KHUYẾN NGHỊ]** 40–60 trang A4 Times New Roman 13 (thể lệ 2021 không đặt trần; hội đồng chấm hàng chục đề tài nên ngắn có lợi). Tóm tắt 1 mặt A4 ở trang đầu. **Chấm mù**: không tên tác giả, trường, GVHD ở bất kỳ đâu, kể cả tên tệp và ảnh chụp màn hình có đường dẫn.

| Phần | Số trang gợi ý | Đưa vào | Bỏ / đẩy xuống phụ lục |
|---|---|---|---|
| Tóm tắt (1 trang) | 1 | Bài toán, một kênh, cổng từ chối, ba con số: 97,56 vs 98,83 (22 chủ thể); 74,28 (PSD) · 80,72 (gate) · 81,01 (gate4) · 82,01 (peakprob, hậu kiểm) trên 60 bản CinC sạch; cổng từ chối AUROC trong bản ghi 0,934 (22 chủ thể, LOSO, tính trên 11/22 chủ thể có đoạn xấu, chỉ ở dạng phân tích, chưa có trong demo). Mỗi số kèm một câu ranh giới. | Mọi số đã rút; mọi từ tự khen về tính mới (danh sách trong `survey/facts_phase4.json` mục Z_DA_RUT). |
| 1. Đặt vấn đề | 4–5 | Thai chậm phát triển và biến thiên nhịp tim; hai cách đo hiện có và giới hạn (bảng sổ tay mục 02); vì sao một điện cực; vì sao "báo khi thấy dấu hiệu mình có thể sai" quan trọng với bác sĩ. Nếu có: 2–3 câu từ bác sĩ được phỏng vấn. | Lịch sử ngành dài dòng. |
| 2. Tổng quan tài liệu | 6–8 | Ba nhóm phương pháp (tách nguồn đa kênh, khử mẫu, học sâu đơn kênh); Power-MF làm mốc; bảng 8–10 bài tiêu biểu từ khảo sát 30 bài với cột "đánh giá ở mức nào" để dẫn tới lỗ hổng: ít bài chạy lại baseline, ít bài thống kê mức chủ thể, chưa thấy bài đo "một kênh lấy lại bao nhiêu phần của đa kênh". | Phần TDA/đồng điều dai dẳng (một đoạn 5 dòng kết quả âm tính ở phụ lục). |
| 3. Mục tiêu – Phương pháp | 10–12 | Mục tiêu 3 gạch đầu dòng; đường ống 5 bước (hình 1); FetalQRS-TCN (bảng thông số, vì sao TCN, bảng 7 họ kiến trúc rút gọn 5 dòng); cổng từ chối 12 SQI; quy tắc chọn kênh mù nhãn (7 quy tắc, nói rõ quy tắc ghi trước và lựa chọn hậu kiểm); dữ liệu 4 bộ + bảng trùng lặp 15 bản; giao thức đánh giá (±50 ms, ghép 1-1, grouped 11-fold, mức chủ thể). | Chi tiết bootstrap, TOST đưa xuống phụ lục; các thí nghiệm thích nghi miền chỉ tóm 1 đoạn. |
| 4. Kết quả – Thảo luận | 10–14 | Hình 2 (22 chủ thể); hình 3 (60 bản sạch); bảng cổng từ chối 22 chủ thể (số cổng trên CinC chỉ đưa vào sau khi tính lại trên 60 bản sạch); phổ lỗi rút gọn kèm âm tính giả 18 % của phép thử nhìn thấy; **mục "Giới hạn" nằm ngay đây**: thua 1,27; 22 chủ thể; hậu kiểm; STV chỉ có số trong miền (+0,33 ms, n = 5), số ngoài miền đã rút; cổng không độc lập với mạng; nhãn gián tiếp 77 %. Mục "Những gì đã rút lại và vì sao" (1 trang, giọng bình thản). | Bảng 7 quy tắc đầy đủ, jackknife, logit chi tiết → phụ lục. Không đưa "trần năng lực" và nhóm "bản giới hạn cứng" của vòng cũ như phát hiện (thẩm định vòng 6 yêu cầu bỏ). |
| 5. Kết luận – Đề nghị | 3–4 | Ba câu kết luận có ranh giới; lộ trình 3 bước; kiến nghị ứng dụng: cổng từ chối làm bộ lọc chất lượng trước khi tính chỉ số lâm sàng; hướng sản phẩm miếng dán (tầm nhìn, nêu rõ chưa có nguyên mẫu). | Hứa hẹn thiết bị y tế. |
| 6. TLTK – Phụ lục | 4–6 + phụ lục | refs.bib đã kiểm DOI; phụ lục: bảng số đã rút, bảng thống kê đầy đủ, ảnh demo, hướng dẫn chạy mã. | — |

**Ba hình quan trọng nhất nên vẽ lại cho Euréka** (dùng dữ liệu đã có, vẽ lại với chú thích tiếng Việt, cỡ chữ lớn):

1. **Hình 1 — Đường ống và cổng từ chối trên một bản ghi thật:** 5 tầng như tab "Tín hiệu" của demo (thô → lọc + đỉnh mẹ → phần dư sau khử mẹ → xác suất TCN → TP/FP/FN), thêm dải màu đèn tin cậy theo từng đoạn 4 s bên dưới. Một hình này trả lời cùng lúc "hệ thống làm gì" và "báo khi thấy dấu hiệu không đáng tin" (chú thích phải nói đèn không phải lần nào cũng thấy). Nguồn: `demo/core.py` + `demo/screenshots/`.
2. **Hình 2 — "Một kênh lấy lại chín phần mười của bốn kênh":** biểu đồ điểm theo từng chủ thể (22 chấm) cho ba cột Power-MF 4 kênh / Power-MF 1 kênh / RelyFetal 1 kênh, nối chấm cùng chủ thể; kèm chú thích 89,5 % [81,4; 103,2] và ba chủ thể khó được ghi tên. Nguồn: `baselines/powermf_fair_stats.json`, `baselines/results.json`.
3. **Hình 3 — Chọn kênh mù nhãn trên 60 bản CinC sạch:** tán xạ F1 PSD (trục hoành) vs peakprob (trục tung) với đường chéo, kèm đường ngang oracle; điểm dưới chéo tô đỏ (6 bản thua, không bản nào mất quá 3,90 điểm). Ghi rõ trong chú thích: quy tắc kế hoạch chọn là gate (80,72, trượt Holm 0,051); gate4 cũng ghi trước (81,01, qua Holm 0,015); peakprob (82,01) là lựa chọn hậu kiểm, sống sót Holm 0,0039; PSD 74,28. Nguồn: `analysis/dulieu_results.json`, `analysis/fig_chonkenh.png`.

(Hình dự phòng nếu hội đồng nghiêng ứng dụng: đường cong "độ phủ – F1" của cổng từ chối trên 22 chủ thể, `analysis/fig_gate22.png` / `analysis/gate22_results.json`. Đường cong trên CinC trong `analysis/gate22_cinc.json` tính trên 75 bản gồm 15 bản nhiễm — không dùng cho tới khi tính lại trên 60 bản sạch.)

---

## 6. Những gì KHÔNG được đưa vào hồ sơ Euréka

Danh sách đầy đủ số đã rút và từ cấm nằm ở `survey/facts_phase4.json` mục `Z_DA_RUT` — **không chép lại vào đây** để tệp này grep sạch. Nhóm chính: số Power-MF từ cổng chuyển hỏng; số mẫu 10 bản; số dải lọc đo trên mô hình phụ; mọi số CinC tính trên 75 bản (kể cả số cổng từ chối zero-shot trong `analysis/gate22_cinc.json`); số logit trên "nhóm chủ thể dễ" (chia sau khi thấy F1) từ phân tích đã rút (`analysis/LUONGCUC.md`); kết luận cũ về nút thắt mô hình/tín hiệu (câu hỏi để mở, âm tính giả 18 %); mọi từ tự khen tiếng Anh về tính mới hoặc "tốt nhất hiện nay"; cụm "phát hiện" đi với rò rỉ (ban tổ chức đã ghi nhận từ 2013). Cũng không nói "nộp CinC kỳ này" — kỳ 2026 (Madrid, 20–23/9) đã diễn ra; đích là CinC 2027.

---

## 7. Nguồn đã đọc

- https://khoahoctre.com.vn/eureka-2026/ (phát động lần 28, đăng ký 01–25/9/2026, 15 lĩnh vực, >500 triệu; liên kết Drive chứa thể lệ 2026)
- https://eureka.khoahoctre.com.vn/ (cổng chính thức; cấu trúc vòng thi; nopdetai.khoahoctre.com.vn)
- https://baovanhoa.vn/doi-song/tphcm-khoi-dong-giai-thuong-eureka-lan-thu-28-257103.html (phát động 18/8/2026; đơn vị tổ chức; số liệu 2025)
- https://eureka.khoahoctre.com.vn/wp-content/uploads/sites/9/2021/08/The-le-Eureka-2021.pdf (thể lệ đầy đủ lần 23: tiêu chí, bố cục, hình thức, hồ sơ, giải)
- https://khoahoctre.com.vn/tieu-chi-danh-gia-de-tai-du-thi-giai-thuong-sinh-vien-nghien-cuu-khoa-hoc-eureka-lan-thu-25-nam-2023/ (tiêu chí 30/50/20 năm 2023)
- https://cepm.ftu.edu.vn/thong-bao-v-v-dang-ky-tham-gia-giai-thuong-sv-nckh-eureka-lan-thu-28-nam-2026/ (hồ sơ, poster, hạn nội bộ FTU 04/9/2026)
- https://forum.uit.edu.vn/t/kttt-eureka-2026-giai-thuong-sinh-vien-nghien-cuu-khoa-hoc-lan-thu-28/161701 (hồ sơ UIT 2026)
- https://dhannd.bocongan.gov.vn/... (bán kết lĩnh vực Hành chính – Pháp lý 02/11/2025, thuyết trình)
- https://vnexpress.net/187-nghien-cuu-sinh-vien-doat-giai-thuong-eureka-4825333.html (kết quả lần 26, trao 08/12/2024)
- https://tuoitre.uit.edu.vn/giai-thuong-sinh-vien-nghien-cuu-khoa-hoc-eureka-lan-thu-27-nam-2025 (mức giải 10/5/3 triệu kỳ 2025)

Không truy cập được: fit.ptithcm.edu.vn (lỗi chứng chỉ), khcn.huce.edu.vn (lỗi chứng chỉ), fit.agu.edu.vn (403), uhsvnu.edu.vn (trang không tồn tại), thư mục Google Drive thể lệ 2026.
