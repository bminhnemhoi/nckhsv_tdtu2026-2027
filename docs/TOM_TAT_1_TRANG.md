# RelyFetal — phát hiện nhịp tim thai từ một điện cực bụng mẹ, có cổng từ chối

Ngô Bình Minh · NCKH sinh viên TDTU 2026–2027 · bản 12/09/2026 · mọi số truy ngược về `survey/facts_phase4.json` và tệp ghi trong ngoặc · Sổ tay: https://claude.ai/code/artifact/7f120fe6-e199-47b9-8aac-1a194c2d8b00

**Bài toán.** Thai chậm phát triển là một nguyên nhân hàng đầu của thai lưu; dấu hiệu sớm là nhịp tim thai mất biến thiên. Muốn đo biến thiên phải biết từng nhịp rơi vào mili-giây nào. Doppler không đủ chính xác thời điểm; điện cực da đầu chính xác nhưng xâm lấn. Điện tim bụng mẹ là lối ra, nhưng các hệ hiện có cần 4–32 điện cực trong phòng khám.

**Hai câu hỏi.** Nếu chỉ có **một** dây (để sau này thành miếng dán mẹ tự đeo) thì mất bao nhiêu so với bốn dây — và hệ thống có tự biết lúc nào nó không nhìn thấy tín hiệu để từ chối trả lời không?

**Hệ thống.** Lọc 10–60 Hz pha-không → khử điện tim mẹ (mẫu trung vị, co giãn từng nhịp) → chọn kênh mù nhãn → mạng tích chập thời gian FetalQRS-TCN (113.481 tham số, 0,48 MB, 4,35 ms mỗi 4 s trên CPU) → cổng từ chối từ 12 chỉ số chất lượng tín hiệu cổ điển, không dùng nhãn. Demo web cục bộ và API; ≈27.700 dòng Python, 60 kiểm thử pass.

**Kết quả chính** (F1 mức chủ thể, ghép ±50 ms; 22 sản phụ ADFECGDB + Silesia).

| | Power-MF 4 kênh (chạy lại qua Octave; kiểm chứng ngoài 99,40 vs 99,46 tác giả) | Power-MF 1 kênh | RelyFetal 1 kênh |
|---|---|---|---|
| 22 sản phụ trong miền | 98,83 | 86,71 | **97,56** |

- Bốn kênh đáng giá 12,12 điểm cho chính Power-MF; một kênh lấy lại 10,85 = **89,5 %** [81,4; 103,2] (`analysis/recovery_ratio.json`). Trung bình vẫn **thua 1,27** [−3,08; +0,27], p 0,156; thắng 18/22 (`baselines/powermf_fair_stats.json`).
- **CinC 2013 set-a, 60 bản sạch** chưa từng thấy. Set-a chứa bản ADFECGDB — ban tổ chức đã ghi nhận (Silva 2013; Clifford 2014); nhóm định danh bằng đo lường đúng 15 bản trùng (NCC = 1,0000), đo mức thổi phồng 3,27–7,18 điểm, rồi loại. Chọn kênh cũ 74,28 → chọn kênh mới (peakprob) **82,01**, **+7,73** [+3,82; +12,41], p Holm 0,0039 trên 7 quy tắc; bản F1 < 50 từ 16 xuống 9; không bản nào mất quá 3,90 (`analysis/dulieu_results.json`).
- **Cổng từ chối**, bỏ-một-chủ-thể trên 22 sản phụ: AUROC trong bản ghi 0,934 [0,872; 0,981]; xếp đúng 3 bản khó nhất vào 3 hạng chót (ngẫu nhiên 1/1540) — nhưng 5/24 quy tắc một đặc trưng cũng làm được (`analysis/gate22_results.json`). Số cổng trên CinC chưa tính lại trên 60 bản sạch — không nêu.

**Ranh giới.**
1. 89,5 % là *phép đo* so với một baseline đa kênh; 22 chủ thể (tự tính cần ~50); kết quả chính 1 hạt giống (hạt giống 2: 97,59).
2. peakprob là lựa chọn **hậu kiểm**: quy tắc chỉ định trước là *gate* (80,72; p Holm 0,051 — trượt). Trên thang logit 22 sản phụ, gate vẫn đứng đầu, peakprob hạng 3 (`analysis/xacnhan_results.json`). Không có bộ công khai nào khác có nhãn nhịp thai thật (NIFEADB, NInFEA, nifecgdb, set-b — đã kiểm) → **giả thuyết mạnh, chưa xác nhận**.
3. Ngoài miền còn kém trong miền 15 điểm; 4 phương pháp thích nghi miền không giám sát đều thất bại (`adapt/adapt_results.json`). Nguyên nhân **chưa xác định**: phép thử "không nhìn thấy tín hiệu" có âm tính giả 18,0 % [12,1; 25,0].
4. Kiến trúc là đòn bẩy yếu: 7 họ cùng tham số, ba họ đầu tương đương (97,64 / 97,63 / 97,62; `analysis/kientruc_results.json`). Dải lọc 10–60 vs 1–45 Hz: ≈ 0 trung bình 4 kênh.
5. STV lệch +0,33 ms trong miền nhưng +20,50 ms trên CinC — chưa dùng được làm máy đo độc lập; khi cổng cho phép, sai số điển hình 0,13 ms (`analysis/clinical_results.json`).

**Đã tự rút lại.** Số Power-MF từ cổng chuyển Octave hỏng; dải lọc "hơn mười điểm"; "đơn kênh hơn đa kênh"; mọi số CinC tính trên 75 bản; kết luận "khoảng cách là do không có tín hiệu, không do mô hình". Danh sách đầy đủ: `survey/facts_phase4.json` mục Z_DA_RUT.

**Kế hoạch 3 tháng.** 3 hạt giống; tính lại số cổng trên 60 bản sạch; bản dài cho Physiological Measurement (Q2 Scimago 2024 — sân nhà fECG) nộp đầu 12/2026; bản 4 trang cho CinC 2027 (hạn dự kiến 4/2027). Q1 (IEEE JBHI) chỉ khi có bộ có nhãn mới — ước 15–20 % trong 6 tháng. **Dừng:** đổi kiến trúc; thích nghi miền không giám sát.

**Xin cô.** (1) Một đầu mối bác sĩ sản / khoa sản đang ghi CTG hoặc điện tim bụng — hỏi nhu cầu thật, xin dữ liệu có nhãn, hoặc nhờ kiểm nhãn nếu tự chú thích 10–20 bản NIFEADB. (2) Ý kiến về nơi nộp (Physiological Measurement; CinC 2027). (3) Ý kiến về Euréka: hạn nội bộ TDTU kỳ 2026 chưa xác minh (hỏi Đoàn trường tuần này); thực tế là kỳ 2027, lĩnh vực Công nghệ thông tin.

Kho mã: github.com/bminhnemhoi/nckhsv_tdtu2026-2027 (commit 7dd2dac) · Demo: `python demo/app.py` · Bản mẫu nghiên cứu, không phải thiết bị y tế.
