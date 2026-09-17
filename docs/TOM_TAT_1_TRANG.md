# RelyFetal — phát hiện nhịp tim thai trong điện tim bụng mẹ, chỉ cần một kênh, có cổng từ chối

Ngô Bình Minh · NCKH sinh viên TDTU 2026–2027 · bản 12/09/2026, sửa 17/09 · mọi số truy ngược về `survey/facts_phase4.json`

**Bài toán.** Theo tài liệu nhóm đọc, thai chậm phát triển gắn với nguy cơ thai lưu và giảm biến thiên nhịp tim thai là một dấu hiệu được theo dõi [CẦN KIỂM BẢN GỐC]. Muốn đo biến thiên phải biết từng nhịp đến mili-giây. CTG (Doppler) cho nhịp tim, không cho hình dạng sóng điện tim; điện cực da đầu chính xác nhưng xâm lấn. Điện tim bụng mẹ là lối ra, nhưng phần lớn phương pháp đã công bố dùng từ 4 điện cực bụng trở lên.

**Hai câu hỏi.** Chỉ một dây (để thành miếng dán mẹ tự đeo) thì mất bao nhiêu so với bốn dây? Và hệ thống có tự biết lúc nào không nhìn thấy tín hiệu để từ chối trả lời không?

**Hệ thống.** Lọc 10–60 Hz → khử điện tim mẹ → chọn kênh mù nhãn → mạng tích chập thời gian 113.481 tham số (0,48 MB, 4,35 ms mỗi 4 s) → cổng từ chối từ 12 chỉ số mỗi đoạn 4 s (6 dựa trên đầu ra mạng), không dùng nhãn. Demo web, ≈31.000 dòng Python (đếm 17/09, kể cả dòng trống và chú thích), 109 kiểm thử.

**Kết quả chính** (F1 mức chủ thể, ±50 ms; 22 sản phụ ADFECGDB + Silesia).

| Phương pháp | F1 |
|---|---|
| Power-MF 4 kênh — chạy lại qua Octave, kiểm chứng ngoài 99,40 vs 99,46 tác giả | 98,83 |
| Power-MF 1 kênh | 86,71 |
| **RelyFetal 1 kênh** | **97,56** |

- Bốn kênh đáng giá 12,12 điểm cho chính Power-MF; một kênh lấy lại 10,85 = **89,5 %** [81,4; 103,2]. Trung bình vẫn **thua 1,27** [−3,08; +0,27], p 0,156; thắng 18/22.
- **CinC 2013 set-a, 60 bản sạch.** Set-a chứa bản ADFECGDB — ban tổ chức đã ghi nhận (Silva 2013; Clifford 2014); nhóm định danh bằng đo lường đúng 15 bản trùng (NCC = 1,0000), đo thổi phồng 3,27–7,18 điểm, rồi loại. Chọn kênh cũ 74,28 → *peakprob* (hậu kiểm) **82,01**, **+7,73** [+3,82; +12,41], p Holm 0,0039 trên 7 quy tắc; bản F1 < 50 từ 16 xuống 9; không bản nào mất quá 3,90.
- **Cổng từ chối**, bỏ-một-chủ-thể: AUROC trong bản ghi 0,934 [0,872; 0,981] trên 11/22 sản phụ có đoạn xấu (chưa vào demo); xếp đúng 3 bản khó nhất vào 3 hạng chót (ngẫu nhiên 1/1540) — nhưng 5/24 quy tắc một đặc trưng cũng làm được.

**Ranh giới.**
1. 89,5 % là *phép đo* so với một baseline; 22 chủ thể (cần ~50); hạt giống 2 cho 97,59.
2. *peakprob* là lựa chọn **hậu kiểm**: quy tắc chỉ định trước là *gate* (80,72; p Holm 0,051 — trượt); cùng họ ghi trước, *gate4* (81,01; p Holm 0,015) sống sót nhưng không phải quy tắc kế hoạch chọn. Trên logit 22 sản phụ, gate vẫn đứng đầu. Không bộ công khai nào khác có nhãn nhịp thai thật → **giả thuyết mạnh, chưa xác nhận**.
3. Ngoài miền kém trong miền 23,28 điểm (PSD; 16,84 với *gate*; 15,55 với *peakprob*); 4 phương pháp thích nghi miền đều thất bại. Nguyên nhân **chưa xác định**: phép thử "không nhìn thấy tín hiệu" có âm tính giả 18 %. Cổng không độc lập với mạng.
4. Kiến trúc là đòn bẩy yếu (7 họ cùng tham số, ba họ đầu tương đương); dải lọc ≈ 0. STV lệch +0,33 ms trong miền (n = 5), chưa có số ngoài miền dùng được — chưa làm máy đo độc lập được.

**Đã tự rút lại.** Số Power-MF từ cổng chuyển hỏng; dải lọc "+11 điểm"; "đơn kênh hơn đa kênh"; mọi số CinC trên 75 bản; "17,92 điểm"; "cổng không lấy từ mạng"; "mô hình không phải nút thắt"; "chúng tôi phát hiện rò rỉ". Danh sách đầy đủ: `facts_phase4.json` mục Z_DA_RUT.

**Kế hoạch.** 3 hạt giống; số cổng trên 60 bản sạch; Physiological Measurement (Q2 Scimago — sân nhà fECG) đầu 12/2026; CinC 2027 (hạn ~4/2027). Q1 (JBHI) chỉ khi có bộ có nhãn mới. **Dừng:** đổi kiến trúc; thích nghi miền.

**Xin cô.** (1) Đầu mối khoa sản đang ghi CTG hoặc điện tim bụng — nhu cầu thật, dữ liệu có nhãn. (2) Ý kiến nơi nộp. (3) Euréka: hạn nội bộ TDTU kỳ 2026 chưa xác minh — hỏi Đoàn trường tuần này; thực tế là kỳ 2027.

Kho mã: github.com/bminhnemhoi/nckhsv_tdtu2026-2027 · Demo: `python demo/app.py` · Bản mẫu nghiên cứu, không phải thiết bị y tế.
