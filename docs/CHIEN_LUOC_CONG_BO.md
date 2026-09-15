# CHIẾN LƯỢC CÔNG BỐ — RelyFetal ĐANG Ở ĐÂU VÀ ĐI ĐÂU ĐƯỢC?

*Nhiệm vụ R6. Viết ngày 2026-09-12, sau thẩm định vòng 6 (`docs/nhat_ky/THAMDINH_VONG6.md`, commit fb1c53b).*
*Cập nhật cùng ngày sau thẩm định vòng 7 (`docs/nhat_ky/THAMDINH_VONG7.md`): đích chính đổi thành Physiological Measurement + CinC 2027; JBHI là dự phòng có điều kiện (cần dữ liệu có nhãn mới); abstract sửa ba câu; ước lượng Q1 hạ. Các chỗ sửa đánh dấu **[V7]**.*
*Vai trò: phản biện senior trong xử lý tín hiệu y sinh. Mọi con số trong tài liệu này truy về một tệp trên đĩa (ghi cạnh số). Mọi xếp hạng venue truy về một nguồn web (ghi ở mục 2.4). Những gì tôi không kiểm được, tôi ghi "không xác minh".*

---

## 0. Kết luận một đoạn (đọc trước khi đọc gì khác)

**Bài này, ở trạng thái hiện tại, là một bài Q2 vững. Đường lên Q1 cần dữ liệu có nhãn mới (tự chú thích có chuyên gia kiểm, hoặc trung tâm ghi thứ hai) — không có bộ công khai nào làm được việc đó [V7]. Nó không phải bài A* và không có đường ngắn nào biến nó thành bài A*.** Lý do rất cụ thể: (i) thứ mạnh nhất còn lại là một *định lượng hậu quả rò rỉ dữ liệu* (rò rỉ 15/75 bản CinC) và một *quy tắc hậu kiểm* (peakprob +7,73 điểm) — cả hai là đóng góp đáng giá với tạp chí y sinh, nhưng không phải "tính mới ML" mà NeurIPS/ICML/ICLR chấm; (ii) quy mô: 22 chủ thể trong miền, 60 bản ngoài miền, một hạt giống; (iii) chưa có bộ dữ liệu thứ ba. Điểm mạnh thật sự của bài — hiếm ở mức sinh viên và hiếm cả ở mức Q1 — là **kỷ luật kiểm toán**: tự định danh 15 bản trùng bằng hai cài đặt độc lập (chồng lấn đã được ban tổ chức ghi nhận, nhóm từng bỏ sót), kiểm rò rỉ nhãn có đối chứng dương, mức ngẫu nhiên cho phép gán lỗi, báo cáo trọn bốn kết quả âm tính. Đó chính là câu chuyện nên kể.

**[V7]** Venue tôi chọn nếu chỉ được nộp **một** nơi trong 3 tháng: **Physiological Measurement** (Q2 Scimago 2024; "sân nhà" của cộng đồng fECG và CinC Challenge; xác suất nhận ước 55–65 % nếu viết đúng trục "kiểm toán + cổng từ chối" và mọi số trên 60 bản sạch). Song song, gửi **CinC 2027** (Auckland; hạn abstract dự kiến 4/2027 — kỳ 2026 ở Madrid đã diễn ra 20–23/9/2026 nên không còn là lựa chọn) như bản hội nghị. **IEEE JBHI** (Q1) là dự phòng có điều kiện: chỉ nộp khi có một bộ có nhãn fQRS thật ngoài dữ liệu đã dùng để chạy peakprob đúng một lần, cộng 3 hạt giống — ước 15–20 % trong 6 tháng, ≈ 35 % trong 12 tháng nếu tự tạo được bộ có nhãn.

---

## 1. VIỆC 1 — ĐỊNH VỊ TỪNG ĐÓNG GÓP SAU THẨM ĐỊNH

Quy ước: **[F]** = sự kiện đã đo, có tệp; **[S]** = suy luận của tôi; **[G]** = giả thuyết; **[K]** = khuyến nghị.

| # | Đóng góp | Loại | Tệp gốc | Venue coi là đủ mạnh | Điểm yếu phản biện sẽ đánh |
|---|---|---|---|---|---|
| 1 | **Rò rỉ CinC 2013 set-a ↔ ADFECGDB**: 15/75 bản là bản sao nguyên văn (NCC = 1,0000, lệch RR 0,0 ms; hai cài đặt độc lập) [F] | Kiểm toán benchmark — **không phải phát hiện của nhóm**: chồng lấn set-a ↔ ADFECGDB đã được ban tổ chức ghi nhận (Silva 2013 Bảng 1; Clifford 2014 Bảng 2 và cảnh báo về Rodrigues; `survey/RO_RI_VANLIEU.md`); phần của nhóm là định danh đúng 15 bản và đo mức thổi phồng 3,27–7,18 điểm | `analysis/dulieu_results.json` (`chong_lan`, `kiem_doc_lap`), `analysis/dulieu_m4b_verify.json` | Physiol. Meas. (nơi CinC Challenge 2013 được công bố); JBHI, CBM, BSPC — như **một mục** của bài, không phải bài riêng. Đủ cho một *Letter/Short communication* độc lập ở Physiol. Meas. nếu tách ra. | (a) "Cộng đồng đã biết chưa?" — **đã rà [V7]** (`survey/RO_RI_VANLIEU.md`): Silva 2013, Clifford 2014, Su & Wu 2017, Matonia 2020 đều ghi nhận chồng lấn ở mức bộ dữ liệu; đóng góp là "định lượng hậu quả" (định danh đúng 15 bản, 3,27–7,18 điểm), không hơn. (b) Chỉ kiểm được trùng nguyên văn; trùng ở mức *sản phụ* trong 60 bản còn lại chưa kiểm (Phụ lục A.3 vòng 6). (c) Hệ quả là các bài đã công bố dùng ADFECGDB huấn luyện + set-a kiểm tra đều bị thổi — phát biểu này *cần nêu* nhưng phải nêu dè dặt. |
| 2 | **Quy tắc chọn kênh `peakprob`**: +7,73 [+3,82; +12,41] so với PSD trên 60 bản sạch, p_Holm 0,0039, lấy lại 82,9 % dư địa oracle, không tham số [F]; nhưng là lựa chọn **hậu kiểm**, quy tắc ghi trước chỉ `gate` (trượt Holm 0,051) [F] | Phương pháp (nhẹ) + phép đo | `analysis/dulieu_results.json` → `chon_kenh_60_sach.bang.peakprob`; `analysis/chonkenh_khaibao_truoc.json`; `analysis/chonkenh_results.json` (`kiem_tra_ro_ri`: 0/776) | Với **xác nhận trên bộ thứ ba**: JBHI/TBME/BSPC/CBM chấp nhận như đóng góp phương pháp chính. Không có xác nhận: chỉ đủ Physiol. Meas./CinC, và phải gắn nhãn "giả thuyết mạnh". | (a) Hậu kiểm trên chính tập đánh giá — phản biện sẽ hỏi thẳng "bao nhiêu quy tắc đã thử?" (7, Holm đã sửa, nhưng *chọn quy tắc để báo cáo* thì Holm không sửa được). (b) Tệp khai báo không neo git → mọi lập luận trình tự dựa trên thiện chí. (c) Ý tưởng "chọn kênh bằng độ tự tin của chính mô hình" không mới về khái niệm (self-confidence selection) — tính mới nằm ở việc *đo nghiêm* trong fECG, không ở ý tưởng. |
| 3 | **Tỉ lệ 89,5 %**: mạng đơn kênh lấy lại 10,85/12,12 điểm mà tách nguồn đa kênh mang lại cho chính Power-MF; KTC [81,4; 103,2], jackknife 88,6–93,4 % [F] | Phép đo / khung đánh giá ("chi phí của việc bỏ ba kênh") | `baselines/powermf_fair_stats.json`, `baselines/BASELINES.md` (dòng 100, 123–124) | JBHI, TBME (thích các phép đo có khung diễn giải rõ), Physiol. Meas. | (a) So với **một** baseline đa kênh; "đa kênh" ≠ Power-MF; phản biện sẽ đòi thêm ít nhất một baseline đa kênh khác (ví dụ ESN hay TS-based của Behar) hoặc thu hẹp phát biểu. (b) 22 chủ thể, 14 chạm trần F1 → tỉ số bị phóng đại ở mẫu số; jackknife giúp nhưng không thay được n. (c) Vòng 6 đã yêu cầu bỏ "hệ quả hậu kiểm so với Power-MF" (`CHONKENH.md` dòng 182–184) — phải giữ đúng phán xử đó. |
| 4 | **Phê bình trần F1**: F1 chạm 100 ở nhiều chủ thể nên hiệu số thô bị nén; nhóm đã tính lại nhánh 22 chủ thể trên thang logit với ba cách kẹp (`analysis/xacnhan_results.json`) [F]. Con số cũ "logit trên nhóm chủ thể dễ" xuất phát từ phân tích đã rút (`analysis/LUONGCUC.md`; nhóm đó chia SAU khi thấy F1) — **không trích** [V7] | Phê bình thước đo (phụ) | `analysis/xacnhan_results.json` → `viec3_logit_22` | Tạp chí y sinh có truyền thống thống kê (Physiol. Meas., TBME) coi trọng; CBM/BSPC ít quan tâm. | (a) Trên logit, gate đứng đầu ở 2/3 cách kẹp (+0,225 [+0,004; +0,589], Holm 0,475), peakprob hạng 3 (+0,134 [−0,038; +0,407]) → phê bình trần F1 **không** cứu được vấn đề hậu kiểm của peakprob. (b) Logit của F1 = 100 là vô cực — ba cách kẹp cho ba xếp hạng, phải nêu rõ. (c) Chỉ nên là một đoạn phân tích nhạy, không phải kết quả chính. |
| 5 | **Tương đương kiến trúc**: 7 họ cùng tham số, tcn 97,64 ≈ rf_wide 97,63 ≈ tcn_ms 97,62 (TOST Holm); cnn_wide kém có ý nghĩa trên logit; nhân 4 lần tham số +0,26 [F] | Kết quả âm tính có kiểm định tương đương | `analysis/kientruc_results.json` (`table`, `holm_tost`) | Phụ lục/mục nhỏ ở mọi tạp chí; **không** là đóng góp chính ở đâu cả. | (a) 3 epoch, 3 fold, 1 seed — giao thức thu nhỏ; phản biện sẽ nói "chưa hội tụ thì tương đương là tầm thường". (b) Chỉ trong miền. (c) Giá trị thật là *đóng câu hỏi để không ai đòi thêm kiến trúc* — hãy dùng nó đúng như thế (một đoạn + một bảng phụ lục). |
| 6 | **Thích nghi miền thất bại có chẩn đoán**: notch thích nghi +0,25 (p 0,70), tự huấn luyện −0,68, AdaBN −1,58, TENT −2,43; áp ba dịch chuyển đo được lên 22 chủ thể chỉ mất 0,01 điểm, thiếu 17,92 điểm [F] → khoảng cách ngoài miền không phải loại dịch chuyển mà thích nghi không giám sát sửa được; nguyên nhân còn lại **chưa xác định** (phép thử nhìn thấy có âm tính giả 18,0 % [12,1; 25,0], `analysis/xacnhan_results.json`) [V7] | Kết quả âm tính + chẩn đoán cơ chế | `analysis/THICHNGHI.md`; các JSON trong `adapt/` (chưa cam kết git tại thời điểm vòng 6) | JBHI, CBM, BSPC nhận kết quả âm tính **nếu** nó phục vụ lập luận chính (ở đây: có). Physiol. Meas. rất hợp. | (a) Bốn phương pháp, một hạt giống → không tách được "thật sự thất bại" khỏi "biến thiên hạt giống" cho các hiệu số < 1 điểm; TENT −2,43 và AdaBN −1,58 thì đủ lớn. (b) Không được viết "khoảng cách là do không có tín hiệu" như kết luận: phép thử nhìn thấy đã đo và có âm tính giả 18 % trên nhịp bắt đúng; phần dư địa "thiếu tín hiệu" không xác định được [V7]. (c) Phản biện ML sẽ hỏi "đã thử DANN / CORAL / test-time augmentation chưa?" — trả lời thẳng: chưa, và nêu lý do cơ chế. |
| 7 | **Phổ lỗi có mức ngẫu nhiên**: 6 nhóm; "bỏ nhịp dù có tín hiệu" 3,8 %/1,0 % so với ngẫu nhiên 15,2 %/11,2 %; jitter 3,76 ms [F]; kết luận cũ về nút thắt (mô hình hay tín hiệu) **đã rút**, câu hỏi để mở — phép thử nhìn thấy có âm tính giả 18,0 % trên 60 bản sạch, phần dư địa "thiếu tín hiệu" không xác định được (`analysis/XACNHAN.md`) | Khung phân tích lỗi (phương pháp phụ) | `analysis/chandoan_results.json` (`pho_loi`, `tran`), `analysis/chandoan_m1_jitter.json` | Mục "error analysis" ở JBHI/TBME sẽ được đánh giá cao vì hiếm ai làm mức ngẫu nhiên. | (a) Phép thử nhìn thấy có âm tính giả 18 % trên 60 bản sạch → *mọi* con số nhóm (b) phải in kèm khoảng bất định đó [V7]. (b) Trần năng lực n = 4 trong mẫu. (c) Nhóm "bản giới hạn cứng" của vòng cũ đã bị vòng 6 bỏ — không được lén đưa lại. (d) a54 là lỗi nhãn (37/144) — cần ghi rõ trong bảng, không dùng làm bằng chứng mô hình. |
| 8 | **Cổng từ chối**: LOSO 12 SQI, xếp đúng 3 bản khó 1-2-3 (1/1540); AUROC trong bản ghi 0,934 [0,872; 0,981] [F]; số zero-shot trên CinC trong `gate22_cinc.json` tính trên **75 bản gồm 15 bản nhiễm** — đã rút khỏi mọi văn bản, chưa tính lại trên 60 sạch [V7]; nhưng 5/24 quy tắc một đặc trưng cũng xếp đúng 3/3 [F] | Phương pháp (phụ) + đánh giá risk–coverage | `analysis/gate22_results.json` (`gate22_cinc.json` chỉ dùng sau khi tính lại trên 60 sạch) | JBHI (thích "trustworthy"/abstention), Physiol. Meas.; CinC. | (a) 12 SQI huấn luyện trên 22 chủ thể — với 3 bản khó, "1/1540" là sự kiện hiếm nhưng 5/24 đặc trưng đơn cũng đạt → cổng học được có thể chỉ tương đương một ngưỡng SNR. (b) Khi tính lại trên 60 sạch: ~9 bản không nhìn thấy tín hiệu ở kênh nào — phân biệt "không có gì để bắt" thì dễ; cái khó là bản trung gian. (c) Đặc trưng đứng đầu `eff_bits` phần lớn là hiện vật bộ nạp (tự khai). |
| 9 | **Power-MF chạy lại qua GNU Octave, kiểm chứng ngoài** B1 99,40 vs 99,46 tác giả công bố [F] | Tái lập (reproduction) | `baselines/powermf_fair.json`, `baselines/powermf_published.json` | Không tạp chí nào xem là đóng góp; nhưng là **điều kiện cần** để mục 3 đứng vững và là điểm cộng lớn về liêm chính. | (a) Đã từng công bố số Power-MF hỏng (cổng chuyển Octave: hàm tìm đỉnh tràn bộ nhớ) rồi rút — phải nói rõ trong bài (một câu) để không bị lộ qua lịch sử git/README. (b) Lỗi `template(j,:)` từ j = 3 của tác giả gốc: nêu như ghi chú, không quy kết. |
| 10 | **Đo STV lâm sàng**: chệch +0,33 ms ADFECGDB nhưng +20,50 ms CinC; không dùng được làm máy đo STV độc lập [F] | Kết quả âm tính (lâm sàng) | `analysis/clinical_results.json`, `analysis/CLINICAL.md` dòng 49, 52 | Mục "clinical applicability" ngắn ở JBHI/Physiol. Meas.; là *hạn chế* chứ không là đóng góp. | (a) STV trên 10 bản CinC với KTC [−24,76; +65,76] là vô nghĩa về thống kê — chỉ đủ nói "không dùng được", không đủ nói "sai bao nhiêu". (b) Phản biện lâm sàng sẽ hỏi vì sao không đo trên nhịp *đã qua cổng* — nếu STV sau cổng tốt thì đây là lập luận cho cổng; nếu chưa làm, hãy làm (rẻ). |

**Nhận định tổng hợp [S]:** trong 10 mục, chỉ có **#1, #2, #3** đủ sức đứng làm trục; **#6, #7, #8** là "xương sườn" chống đỡ; **#4, #5, #9, #10** là phụ lục hoặc một đoạn. Bài hiện có 10 kết quả rời rạc là vì ba trục chưa được nối. Mục 4 nối chúng.

---

## 2. VIỆC 2 — BẢNG VENUE

### 2.1 Bảng chính

Ký hiệu xác suất: **P_nay** = xác suất chấp nhận (qua ≥ 1 vòng sửa) nếu nộp bài ở trạng thái hiện tại, viết lại quanh trục ở mục 4; **P_sau** = sau khi làm xong ba việc của vòng 6 (sửa số CinC + cam kết git; nhân rộng peakprob trên bộ thứ ba + logit 22; độ đặc hiệu phép thử nhìn thấy + thí nghiệm SNR thấp). Đây là ước lượng chủ quan của một người từng phản biện các nơi này — không phải số đo.

| Venue | Loại | Xếp hạng (nguồn, năm) | IF / SJR | Hạn gần nhất | Phù hợp | Vì sao | P_nay | P_sau |
|---|---|---|---|---|---|---|---|---|
| **Physiological Measurement** (IOP) | Tạp chí | Scimago 2024: **Q2** Physiology (25/73), **Q3** Biomedical Eng. (51/89) — không phải Q1 | IF ≈ 3,0 (2024, không xác minh chính xác); SJR 0,595 | Liên tục | **Cao** | Sân nhà của CinC Challenge 2013 (set-a xuất phát từ đây) và của cộng đồng fECG (Behar, Clifford, Andreotti, Jezewski). Kiểm toán rò rỉ #1 *thuộc về* tạp chí này. Ban biên tập quen với kết quả âm tính và phê bình thước đo. **Đích chính [V7].** | 0,55 [V7] | 0,65 |
| **IEEE JBHI** | Tạp chí | Scimago: **Q1** (Health Informatics; Biomedical Eng.) — theo trang Scimago/Researcher.Life, năm 2024–2025 | IF 6,8 (2025, không xác minh); SJR 1,62 | Liên tục | **Cao** | Thích "trustworthy ML for health": cổng từ chối, risk–coverage, kiểm toán benchmark, kết quả âm tính có chẩn đoán. Chấp nhận bài phương pháp nhẹ nếu đánh giá nghiêm. Cần bộ dữ liệu thứ ba để không bị "single-benchmark" — không có bộ công khai nào; dự phòng có điều kiện [V7]. | 0,15–0,20 [V7] | 0,35 (12 tháng, chỉ nếu có bộ có nhãn mới) |
| **IEEE TBME** | Tạp chí | Scimago: **Q1** Biomedical Eng. | IF ≈ 5,2 (2024, không xác minh); SJR 1,11 | Liên tục | **Trung bình** | Chuộng đóng góp *kỹ thuật* rõ (thuật toán, mô hình sinh lý, phần cứng). Bài này nặng về đánh giá; phê bình thước đo và tỉ lệ 89,5 % hợp khẩu vị thống kê của TBME, nhưng "quy tắc chọn kênh không tham số" sẽ bị coi là mỏng. | 0,10 | 0,25 |
| **Biomedical Signal Processing and Control** (Elsevier) | Tạp chí | Scimago: **Q1** (Signal Processing; Health Informatics) | IF ≈ 7,3 (2024, không xác minh); SJR 1,23 | Liên tục | **Cao** | Đúng chuyên ngành (fECG là đề tài thường trực ở BSPC). Phản biện thường yêu cầu bảng so sánh rộng và ít khắt khe về thống kê hơn PM/TBME. Rủi ro: bị đòi so với 5–10 phương pháp học sâu khác trên ADFECGDB (những bài đó nhiều bài dính đúng rò rỉ #1 — đây là lợi thế nếu trình bày khéo). | 0,35 | 0,55 |
| **Computers in Biology and Medicine** (Elsevier) | Tạp chí | Scimago: **Q1** (Computer Science Applications; Health Informatics) | IF ≈ 8,35 (2025, không xác minh); SJR 1,38 | Liên tục | **Trung bình–cao** | Nhận nhiều bài ML y sinh; thời gian phản biện nhanh; có APC/OA tuỳ chọn. Khẩu vị thiên về "hệ thống + kết quả" hơn "kiểm toán"; phần demo/API là điểm cộng ở đây. Rủi ro: bị xếp cùng làn với hàng trăm bài "deep learning cho fECG" và bị đòi số cao hơn. | 0,30 | 0,50 |
| **Artificial Intelligence in Medicine** (Elsevier) | Tạp chí | Scimago: **Q1** (Medicine misc.; AI) | CiteScore 10,4; IF không xác minh | Liên tục | **Trung bình** | Hợp nếu trục là "abstention + audit"; kém hợp nếu trục là xử lý tín hiệu. Dự phòng cho JBHI. | 0,20 | 0,40 |
| **Journal of Electrocardiology** | Tạp chí | Scimago 2024: **Q3** | IF ≈ 1,2 (không xác minh) | Liên tục | Thấp | Đọc giả lâm sàng; sẽ hỏi STV/FHR, đúng chỗ bài yếu nhất. Chỉ là phương án cuối. | 0,50 | 0,65 |
| **Computing in Cardiology (CinC)** | Hội nghị (4 trang, Scopus/IEEE Xplore) | **Không có trong CORE**; không có A/B/C | — | Abstract dự kiến **15/4/2027** (CinC 2027 Auckland; ngày chưa xác nhận trên cinc2027.org, suy từ hạn chuẩn hàng năm) | **Cao** | Cộng đồng đúng, chấp nhận theo abstract, tỉ lệ nhận cao, bản nháp 4 trang cũ trong `paper/` toàn số 75 bản — phải viết lại trên 60 bản sạch [V7]. Không tính là "rank" theo bất kỳ thang nào chủ nhiệm nêu. | 0,80 | 0,90 |
| **IEEE EMBC** | Hội nghị (4 trang) | CORE 2018: **C**; bị loại khỏi danh sách CORE từ 2020 | — | EMBC 2027: chưa công bố (thường đầu tháng 2) | Trung bình | Dễ nhận, ít giá trị xếp hạng; chỉ hữu ích nếu cần một dòng hội nghị IEEE cho hồ sơ Eureka. | 0,65 | 0,80 |
| **MICCAI** | Hội nghị | CORE 2026 (ICORE): **A** — không phải A* | — | 26/2/2027 (theo mldeadlines.com, chưa chính thức) | **Thấp** | Hội nghị *ảnh* y khoa; fECG 1-D không thuộc phạm vi; không có track nào phù hợp. Nộp là lãng phí một tháng. | < 0,05 | < 0,05 |
| **NeurIPS (main track)** | Hội nghị | CORE: **A\*** | — | NeurIPS 2027: dự kiến tháng 5/2027 (ngoài 3 tháng) | **Rất thấp** | Không có tính mới ML: kiến trúc TCN chuẩn, quy tắc chọn kênh không tham số, kết quả âm tính về DA trên một bài toán hẹp. Reviewer NeurIPS sẽ viết "application paper, little methodological newness, small scale". | < 0,02 | < 0,03 |
| **NeurIPS Evaluations & Datasets track** (tên mới của Datasets & Benchmarks, 2026) | Hội nghị | CORE A\* (tính chung NeurIPS) | — | NeurIPS 2026 E&D đã hết hạn (6/5/2026); kỳ tới ~5/2027 | **Thấp → trung bình có điều kiện** | Xem mục 3.2. Rò rỉ + kiểm toán + phê bình thước đo *đúng loại* track này nhận, **nhưng** quy mô hiện tại (một cặp dataset, một bài toán, không phát hành tài nguyên) là quá nhỏ. Có đường lên nhưng là dự án 8–10 tháng, không phải 3 tháng. | 0,05 | 0,15 (chỉ nếu biến thành benchmark đa-dataset có phát hành, xem 3.2) |
| **ICLR 2027** | Hội nghị | CORE A\* | — | **25/9/2026** (abstract 18/9) — 13 ngày nữa | Rất thấp | Không kịp và không hợp. | < 0,02 | — |
| **ICML 2027** | Hội nghị | CORE A\* | — | ~22/1/2027 (dự kiến từ chu kỳ trước, chưa chính thức) | Rất thấp | Như NeurIPS main. | < 0,02 | < 0,03 |
| **KDD 2027** (Research; có Datasets & Benchmarks track) | Hội nghị | CORE A\* | — | Chu kỳ 2: tháng 2/2027 | Thấp | Track D&B của KDD nhận kiểm toán benchmark, nhưng cộng đồng KDD gần như không có fECG; một bài rò rỉ trong dữ liệu 75 bản ghi sẽ bị coi là quá hẹp. | 0,03 | 0,08 |
| **ML4H / CHIL** (symposium ML for Health; PMLR) | Hội nghị | Không có trong CORE | — | ML4H thường tháng 8–9 (2026 đã qua); CHIL ~tháng 2/2027 | Trung bình | Cộng đồng ML-health đọc được bài kiểm toán; không mang lại "rank" nhưng mang lại người đọc đúng và phản hồi tốt trước khi nộp JBHI. | 0,35 | 0,50 |

### 2.2 Đọc bảng như thế nào

* **Chỉ 5 tạp chí trong bảng là Q1 Scimago**: JBHI, TBME, BSPC, CBM, AI in Medicine. **Physiological Measurement (Q2 Scimago 2024) theo Scimago 2024** (Q2/Q3) — nếu tiêu chí Eureka/trường dùng Scimago thì PM không đạt mốc "Q1", dù về mặt cộng đồng nó là nơi *đúng nhất*. Chủ nhiệm cần kiểm tra thang xếp hạng mà hội đồng dùng (Scimago hay WoS-JCR; JCR thường xếp PM ở Q2–Q3 Engineering, Biomedical) trước khi quyết.
* **Không hội nghị nào trong lĩnh vực này có CORE A\***. CinC không nằm trong CORE; EMBC là C (2018) và đã bị bỏ; MICCAI là A. Muốn A\* là phải ra khỏi lĩnh vực (NeurIPS/ICML/ICLR/KDD), và ở đó bài này không cạnh tranh được.
* Mọi số IF ở trên đến từ trang tổng hợp bên thứ ba (Researcher.Life, Resurchify, Editage, wos-journal.info) — **không xác minh trực tiếp từ JCR**. Quartile Scimago lấy từ scimagojr.com qua trang tổng hợp (trang Scimago trả 403 khi tải trực tiếp trong phiên này).

### 2.3 Hạn nộp còn liên quan trong 3–7 tháng tới

| Mốc | Ngày | Nguồn | Độ tin cậy |
|---|---|---|---|
| ICLR 2027 | 25/9/2026 | iclr.cc/Conferences/2027/Dates | Chính thức |
| ICML 2027 | ~22/1/2027 | mlciv.com (dự phóng) | Chưa chính thức |
| KDD 2027 chu kỳ 2 | 2/2027 | kdd2027.kdd.org | Chính thức (tháng), ngày chưa rõ |
| MICCAI 2027 | 26/2/2027 | mldeadlines.com | Chưa chính thức |
| CinC 2027 (Auckland) | ~15/4/2027 | cinc.org authors kit (hạn chuẩn) | Suy từ thông lệ |
| NeurIPS 2027 E&D | ~5/2027 | Suy từ 2026 (4–6/5/2026) | Suy từ thông lệ |
| Tạp chí (PM, JBHI, TBME, BSPC, CBM) | Liên tục | — | — |

### 2.4 Nguồn tra cứu xếp hạng (WebSearch, 12/9/2026)

* Physiological Measurement: [Scimago](https://www.scimagojr.com/journalsearch.php?q=17049&tip=sid&clean=0), [Resurchify](https://www.resurchify.com/impact/details/17049), [Researcher.Life](https://researcher.life/journal/physiological-measurement/7146)
* IEEE JBHI: [Scimago](https://www.scimagojr.com/journalsearch.php?q=21100256982&tip=sid), [Researcher.Life](https://researcher.life/journal/ieee-journal-of-biomedical-and-health-informatics/1412)
* IEEE TBME: [Scimago](https://www.scimagojr.com/journalsearch.php?q=16318&tip=sid), [Researcher.Life](https://researcher.life/journal/ieee-transactions-on-biomedical-engineering/3381)
* BSPC: [Resurchify](https://www.resurchify.com/impact/details/4700152237), [wos-journal.info](https://wos-journal.info/journalid/13218)
* CBM: [Scimago](https://www.scimagojr.com/journalsearch.php?q=17957&tip=sid), [wos-journal.info](https://wos-journal.info/journalid/2793)
* AI in Medicine: [Scimago](https://www.scimagojr.com/journalsearch.php?q=24140&tip=sid)
* J. Electrocardiology: [Scimago](https://www.scimagojr.com/journalsearch.php?q=23855&tip=sid)
* MICCAI CORE A: [portal.core.edu.au/conf-ranks/1607](https://portal.core.edu.au/conf-ranks/1607/); EMBC CORE C 2018, bỏ 2020: [portal.core.edu.au/conf-ranks/2019](https://portal.core.edu.au/conf-ranks/2019/)
* NeurIPS 2026 E&D track: [CFP](https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets), [blog đổi tên](https://blog.neurips.cc/2026/03/23/introducing-the-evaluations-datasets-track-at-neurips-2026/)
* ICLR 2027: [Dates](https://iclr.cc/Conferences/2027/Dates); ICML 2027: [mlciv](https://mlciv.com/ai-deadlines/); KDD 2027: [Research track CFP](https://kdd2027.kdd.org/research-track-call-for-papers/), [D&B track](https://kdd2027.kdd.org/datasets-and-benchmarks-track-call-for-papers/); MICCAI 2027: [mldeadlines](https://mldeadlines.com/conference/miccai-2027/); CinC 2027: [cinc2027.org](https://www.cinc2027.org/), [authors kit](https://cinc.org/authors_kit/)

---

## 3. VIỆC 3 — TRẢ LỜI THẲNG BA CÂU

### 3.1 Q1 đạt được không?

**[V7] Khó trong 6 tháng: ≈ 15–20 %; ≈ 35 % trong 12 tháng nếu tự tạo được một bộ có nhãn fQRS thật (tự chú thích có chuyên gia kiểm, hoặc trung tâm ghi thứ hai).** Lý do: ba việc vòng 6 đặt ra đã được làm hoặc kiểm, và kết quả bất lợi — (1) không có bộ công khai thứ ba có nhãn; (2) logit 22 chủ thể đã tính, gate vẫn đứng đầu; (3) phép thử nhìn thấy có âm tính giả 18 %, trụ "khoảng cách là do không có tín hiệu" mất. Venue Q1 nếu có dữ liệu mới: **JBHI** (đích), BSPC hoặc CBM (dự phòng, xác suất cao hơn nhưng uy tín cộng đồng fECG thấp hơn). Không phải TBME.

Cần gì thêm, theo thứ tự quan trọng:
1. **Bộ dữ liệu thứ ba với nhãn thật, chạy đúng một lần với peakprob chốt cứng bằng git.** Đây là ranh giới Q2/Q1. Không có nó, phản biện Q1 sẽ viết: "channel-selection rule chosen post hoc on the only held-out set". Ứng viên trong repo: NIFEADB (Behar 2019; bộ nạp `model/nifeadb_loader.py`), NInFEA (Sulas 2021; `model/ninfea_loader.py`). **Cảnh báo:** vòng 6 gợi ý CinC 2013 set-b — theo hiểu biết của tôi, nhãn set-b/set-c *không được PhysioNet công bố* (giữ kín từ Challenge); phải kiểm tra trước khi tính vào kế hoạch. Với NInFEA, cần kiểm xem nhãn fQRS có sẵn cho bao nhiêu bản (bộ này có tham chiếu Doppler xung, không chắc có nhãn từng nhịp) — *tôi không xác minh được trong phiên này*. **[Cập nhật R2, `analysis/XACNHAN.md`: không ứng viên nào trong tầm tay có nhãn fQRS thật — NIFEADB và NInFEA không phân phối nhãn nhịp thai, `.qrs` của nifecgdb là QRS mẹ (RR 0,695 s), set-b chưa công bố nhãn. Việc này hiện KHÔNG thực hiện được với dữ liệu công khai; cần tự chú thích hoặc xin dữ liệu ngoài.]**
2. ~~Tính lại nhánh 22 chủ thể trên logit~~ **Đã làm 12/09 [V7]** (`analysis/xacnhan_results.json`; khai báo tính toán ở commit ed819e3, không phải khai báo giả thuyết): gate đứng đầu ở 2/3 cách kẹp (+0,225 [+0,004; +0,589]), peakprob hạng 3 (+0,134 [−0,038; +0,407]) — vấn đề hậu kiểm không biến mất.
3. **3 hạt giống cho kết quả chính** (22 chủ thể và 60 sạch). Một hạt giống ở Q1 là lý do từ chối phổ biến thứ hai sau "single benchmark".
4. ~~Độ đặc hiệu phép thử nhìn thấy~~ **Đã đo 12/09 [V7]**: âm tính giả 18,0 % [12,1; 25,0] trên nhịp bắt đúng — mọi phát biểu "khoảng cách là do không có tín hiệu" đã hạ xuống "chưa xác định nguyên nhân". Bài mất phần "vì sao"; phần còn lại là bốn phương pháp thích nghi miền thất bại và ba dịch chuyển đo được chỉ giải thích 0,01 điểm.
5. **Cam kết git toàn bộ `analysis/`, `adapt/`, `baselines/`** — hiện tại ~50 tệp `??`. Không có commit thì mọi lập luận "khai báo trước" là vô giá trị và phản biện *sẽ* mở repo.

### 3.2 A\* đạt được không?

**Không, ở bất kỳ trạng thái nào trong 3 tháng; và tôi không tin có đường ngắn.** Ba lý do, không phải một:

* **Loại đóng góp.** A\* trong ML chấm *tính mới về phương pháp hoặc hiểu biết chung*. Bài này có: một TCN chuẩn (tương đương kiến trúc tự chứng minh là không có gì để nói), một quy tắc chọn kênh tương đương "argmax độ tự tin" (đã có trong văn liệu selective prediction), một cổng từ chối 12 đặc trưng thủ công, bốn phương pháp DA thất bại trên một bài toán. Không mục nào là điều một reviewer NeurIPS chưa thấy.
* **Quy mô.** 22 chủ thể + 60 bản ghi + 1 hạt giống. Ở NeurIPS/ICML điều đó là "preliminary".
* **Không có tài nguyên phát hành.** A\* track dữ liệu/đánh giá nhận bài vì cộng đồng *dùng được* thứ họ phát hành.

**Về NeurIPS Evaluations & Datasets track — xét nghiêm túc như yêu cầu.** Track này (đổi tên từ Datasets & Benchmarks năm 2026) *đúng là* nhận bài kiểm toán benchmark, chỉ ra rò rỉ, phê bình thước đo. Ví dụ trong quá khứ của track có nhiều bài kiểu "X benchmark is contaminated" và "metric Y is misleading". Vậy tại sao tôi chỉ cho 15 % ngay cả sau ba việc?

Điều kiện để một bài như vậy được nhận, theo hướng dẫn phản biện của chính track:
1. **Tầm ảnh hưởng**: phát hiện phải chạm nhiều công trình. Rò rỉ ADFECGDB↔CinC ảnh hưởng đến các bài huấn luyện trên ADFECGDB và kiểm trên set-a — cần *liệt kê được* (ước lượng của tôi: vài chục bài, hầu hết ở BSPC/CBM/Sensors; **chưa rà**). Nếu chỉ ~10 bài thì quá hẹp cho NeurIPS; nếu ~50 thì bắt đầu đáng.
2. **Tài nguyên phát hành**: ít nhất (a) danh sách bản trùng kèm mã kiểm NCC dùng được cho bất kỳ cặp dataset nào, (b) giao thức đánh giá "sạch" cho fECG đơn kênh (split cố định, chấm điểm, mức ngẫu nhiên cho phép gán lỗi, risk–coverage), (c) leaderboard chạy được với ≥ 3–4 phương pháp công khai (Power-MF, ESN của Behar, TS/PCA, và mạng của nhóm) trên ≥ 3 dataset (ADFECGDB, Silesia, NIFEADB/NInFEA, FECGSYNDB tổng hợp).
3. **Tổng quát hoá phê bình**: "F1 trần 100 che giấu khác biệt có ý nghĩa trên logit" phải được chứng minh trên nhiều hơn một bài toán, hoặc ít nhất nhiều hơn một cặp phương pháp.

Đó là một dự án **8–10 tháng, hai người, và cần dữ liệu thứ ba đã có** — tức là cần *xong* bài Q1 trước. Khung thời gian: nộp NeurIPS 2027 E&D (~5/2027) là khả thi về lịch nếu bài JBHI đã nộp vào 12/2026 và tháng 1–4/2027 dành cho mở rộng benchmark. Xác suất tôi ước 15 % ở trạng thái đó; 25 % nếu rà văn liệu cho thấy > 40 bài bị ảnh hưởng và nhóm phát hành được leaderboard 4 dataset. **Tôi không khuyên đặt cược Eureka vào đường này.**

Cách nói với chủ nhiệm: *"A\* không phải mục tiêu của bài này; mục tiêu là Q1 với một câu chuyện kiểm toán sạch. Nếu Q1 xong sớm, mở rộng thành benchmark cho NeurIPS E&D 2027 là bước tiếp theo hợp lý — nhưng là dự án khác."*

### 3.3 Nếu chỉ chọn MỘT venue trong 3 tháng

**[V7] Physiological Measurement**, nộp cuối tuần 12 (khoảng 5–12/12/2026). JBHI chỉ khi có dữ liệu có nhãn mới trước tuần 8. Lý do chọn PM:
* Sân nhà của fECG và CinC Challenge; ban biên tập quen kết quả âm tính, phê bình thước đo và bài kiểm toán — đúng loại bài này. Q2 Scimago 2024, không phải Q1: chủ nhiệm cần biết trước và kiểm thang xếp hạng mà trường/Euréka dùng.
* Trục "kiểm toán + cổng từ chối" (mục 4) đứng được ở PM mà không cần bộ thứ ba; ở JBHI thì không.
* Thời gian phản biện PM thường 2–4 tháng vòng đầu → có phản hồi trước Euréka 2027.
* Nếu bị từ chối: BSPC (Q1, ít khắt khe thống kê hơn, sẽ đòi bảng so sánh rộng), rồi Journal of Electrocardiology.

Kèm theo, **không thay thế**: nộp CinC 2027 (abstract 4/2027) — chi phí thấp, bản nháp có sẵn, cho hồ sơ Eureka một dòng hội nghị quốc tế đúng chuyên ngành.

Nếu trước tuần 8 có được bộ có nhãn mới và peakprob thắng trên đó với 3 hạt giống: **nâng đích lên JBHI**. Nếu không: giữ PM và viết peakprob như giả thuyết mạnh chưa xác nhận (PM nhận loại này; JBHI sẽ không) [V7].

---

## 4. VIỆC 4 — KHUNG BÀI BÁO MẠNH NHẤT

### 4.1 Câu chuyện là gì

Bài hiện có 10 kết quả vì mỗi vòng thẩm định thêm một câu hỏi. Một bài Q1 cần **một câu hỏi** mà mọi kết quả đều là bằng chứng cho hoặc chống. Câu hỏi đó, theo tôi, không phải "mô hình tốt bao nhiêu" mà là:

> **Một đạo trình bụng có thể thay bốn đạo trình đến mức nào — và khi không thể, hệ thống có biết không?**

Câu hỏi này nối được mọi thứ:
* *Đến mức nào*: 89,5 % khoảng cách đa kênh được lấy lại trong miền (#3); trần F1 che khuất phần còn lại (#4); kiến trúc không phải đòn bẩy (#5).
* *Đạo trình nào*: peakprob — để mô hình tự chọn kênh nó tin (#2), với cảnh báo hậu kiểm và bộ thứ ba.
* *Khi không thể*: ngoài miền, bốn phương pháp thích nghi miền không thu hẹp khoảng cách và ba dịch chuyển đo được chỉ giải thích 0,01 điểm; nguyên nhân còn lại chưa xác định (#6, #7) [V7].
* *Có biết không*: cổng từ chối và đường risk–coverage (#8); STV không dùng được nếu không có cổng (#10).
* *Trên nền số liệu nào*: benchmark ngoài miền bị rò rỉ 15/75 — mọi con số trước đây bị thổi 3,27–7,18 điểm (#1); ta báo cáo trên 60 bản sạch.

Gợi ý của chủ nhiệm "Khi nào một kênh là đủ? Một kiểm toán có kiểm soát của phát hiện fQRS đơn kênh" **là đúng hướng**; tôi chỉ đề xuất thêm vế "và khi không đủ, có biết không" — vì đó là thứ làm bài này khác với một bài đánh giá thuần, và là phần JBHI muốn đọc.

### 4.2 Ba phương án tiêu đề

1. *When is one abdominal lead enough? A leakage-corrected audit of single-lead fetal QRS detection with model-driven lead selection and abstention*
2. *How much of multi-lead fetal QRS detection does a single lead recover? A controlled audit across two public benchmarks*
3. *Single-lead fetal QRS detection under audit: benchmark leakage, lead selection, abstention, and the limits of domain adaptation*

Tôi nghiêng về **phương án 1** cho JBHI (câu hỏi + hai từ khoá "audit", "abstention"); **phương án 2** cho Physiological Measurement (định lượng, không hứa quá); phương án 3 mô tả đúng nhất nhưng đọc như mục lục.

Không dùng từ tự khen về tính mới, từ "tốt nhất hiện nay", hay từ khai báo trước quá mức — danh sách từ cấm trong `survey/facts_phase4.json` mục Z_DA_RUT.

### 4.3 Abstract (hiện 232 từ — phải cắt về ≤ 200 cho Physiological Measurement; tiếng Anh)

> Fetal QRS detection from a single abdominal lead would simplify home and low-resource monitoring, but it is unclear how much of multi-lead performance a single lead can recover, and whether a detector can recognise when it cannot. We audit a 113k-parameter temporal convolutional detector on 22 subjects (ADFECGDB, Silesia) and on the CinC 2013 challenge set-a. As documented by the challenge organisers, set-a contains ADFECGDB recordings; we identify by measurement exactly which 15 of the 75 records are verbatim copies of training records (normalised cross-correlation 1.0000, two independent implementations) and quantify the resulting inflation at 3.3–7.2 F1 points; all results are reported on the 60 clean records. In-domain, the single-lead detector recovers 89.5% (95% CI 81–103%) of the gap that multi-lead source separation provides to a matched-filter baseline. Out of domain, selecting the lead on which the model is most confident improves F1 by 7.7 points (Holm-adjusted p = 0.004); this rule was chosen after inspecting the results, the pre-specified rule did not survive correction (p = 0.051), and no public dataset with true fetal QRS annotations is available to replicate it, so we report it as a strong but unconfirmed hypothesis. Four unsupervised domain-adaptation methods fail to close the remaining gap, whose cause we could not establish. A signal-quality gate trained leave-one-subject-out ranks the three hardest subjects last (within-record AUROC 0.934, 95% CI 0.872–0.981). Code and audit tools are released.

(≈215 từ — PM cho phép tới 250. Nếu sau này có bộ có nhãn mới, thay câu "no public dataset ... unconfirmed hypothesis" bằng kết quả thật, dù chiều nào [V7].)

### 4.4 Cấu trúc mục

1. **Introduction** — vì sao một đạo trình; hai câu hỏi (đến mức nào / có biết không); tóm tắt bốn đóng góp: kiểm toán rò rỉ (định lượng hậu quả — chồng lấn đã được ban tổ chức ghi nhận), tỉ lệ 89,5 %, chọn kênh (hậu kiểm, chưa nhân rộng được), cổng + chẩn đoán lỗi [V7]. Một câu nêu rõ những gì đã rút lại từ bản CinC sơ bộ (nếu bản CinC 2027 đã đăng) — tự khai trước.
2. **Data and the leakage audit** — ADFECGDB, Silesia B1/B2 (nhãn gián tiếp, 77 % thời lượng — nêu thẳng), CinC set-a; phương pháp NCC + đối chứng dương (trùng B2↔PhysioNet đã biết, NCC 0,86–0,98) + 60 bản còn lại (≤ 0,62); bảng ánh xạ 5→15; hệ quả 3,27–7,18 điểm; giới hạn (chỉ trùng nguyên văn; trùng chủ thể chưa kiểm).
3. **Detector and evaluation protocol** — front-end, khử mẹ, TCN, chấm ±50 ms ghép 1-1, grouped 11-fold; **thang logit bên cạnh F1 thô** và lý do (trần). Tương đương kiến trúc đưa vào một đoạn + bảng phụ lục.
4. **How much does one lead recover? (in-domain)** — Power-MF 4 kênh/1 kênh (tái lập Octave, kiểm chứng 99,40 vs 99,46); hiệu −1,27 và +10,85; tỉ lệ 89,5 % với KTC và jackknife; logit trên cả 22 chủ thể với ba cách kẹp (phân tích nhạy; nhóm "chủ thể dễ" chia hậu kiểm thuộc phân tích đã rút, không dùng) [V7].
5. **Which lead? Model-driven lead selection (out-of-domain)** — bảy quy tắc, Holm; peakprob +7,73; **khai báo trước chỉ gate, gate trượt Holm** — nói trong thân bài, không giấu ở phụ lục; kiểm rò rỉ nhãn 0/776; **nêu thẳng: không có bộ công khai thứ ba có nhãn fQRS thật (NIFEADB, NInFEA, nifecgdb, set-b đã kiểm) — quy tắc là giả thuyết mạnh chưa xác nhận; trên logit 22 chủ thể gate đứng đầu** [V7].
6. **Why does the remaining gap persist?** — bốn DA thất bại; ba dịch chuyển đo được chỉ giải thích 0,01/17,92 điểm; phổ lỗi với mức ngẫu nhiên; phép thử nhìn thấy kèm âm tính giả 18,0 % [12,1; 25,0] — nguyên nhân khoảng cách còn lại để mở; jitter 3,76 ms [V7].
7. **Does the system know? Abstention** — 12 SQI, LOSO, risk–coverage (AUROC trong bản ghi 0,934 [0,872; 0,981] trên 22 ca); số zero-shot CinC **chỉ in sau khi tính lại trên 60 bản sạch** (số hiện có đo trên 75 bản gồm 15 bản nhiễm — không trích) [V7]; so với quy tắc một đặc trưng (5/24 đạt 3/3 — tự khai); STV sau cổng (nếu làm) hoặc STV thất bại (nếu không).
8. **Discussion** — trả lời hai câu hỏi; hàm ý cho các bài đã dùng set-a; hạn chế: 22 chủ thể, 1 (hoặc 3) hạt giống, nhãn gián tiếp B1, không có SNR thấp trong huấn luyện, peakprob hậu kiểm; những gì không làm (DANN/CORAL).
9. **Reproducibility statement** — commit hash cho mỗi bảng, tệp JSON tương ứng, Octave, checkpoint.

---

## 5. VIỆC 5 — KẾ HOẠCH 12 TUẦN (14/9 → 6/12/2026)

Nguyên tắc xếp: giá trị/chi phí; việc rẻ có thể lật kết luận đi trước; việc cần người ngoài (giảng viên, khoa sản) khởi động từ tuần 1 vì thời gian chờ dài.

| Tuần | Việc | Đầu ra | Phụ thuộc | Ai / cần hỗ trợ |
|---|---|---|---|---|
| **1** (14–20/9) | (a) `git add` + commit toàn bộ `analysis/`, `adapt/`, `baselines/`, `benchmark_dpss/`, `model/train_12*`; tag `r6-baseline`. (b) Viết và commit **tệp khai báo trước** cho: logit-22, bộ thứ ba với peakprob chốt cứng, độ đặc hiệu phép thử nhìn thấy, 3 hạt giống. (c) ~~Kiểm tra nhãn~~ đã kiểm 12/09: không bộ công khai nào có nhãn fQRS thật [V7]. (d) Chủ nhiệm gửi giảng viên hướng dẫn: đề nghị giới thiệu khoa sản (BV Từ Dũ / Hùng Vương / BV ĐH Y Dược) để xin **ghi bụng có tham chiếu** (scalp hoặc Doppler), và hỏi lịch Eureka. | Commit hash; `docs/KHAIBAO_TRUOC_R7.md`; bảng khả dụng nhãn của 3 bộ; email đã gửi | — | Chủ nhiệm; **giảng viên** (thư giới thiệu) |
| **2** (21–27/9) | (a) ~~Logit 22 chủ thể~~ đã làm 12/09 (gate đứng đầu) [V7]; thay bằng: tính lại số cổng từ chối trên 60 bản sạch. (b) Sửa mọi số CinC còn lại trong README/README.vi/`main.tex`/đề cương/`facts_phase2.json` sang 60 sạch; xoá `.bak_integrity`. (c) Tính lại M1 (phổ lỗi) trên 60 sạch. | `analysis/logit22_results.json`; README sạch; `chandoan_60sach.json` | Tuần 1(b) | Chủ nhiệm |
| **3** (28/9–4/10) | (a) [V7] Nếu có bác sĩ đồng ý: bắt đầu tự chú thích 10–20 bản NIFEADB có chuyên gia kiểm; nếu không có bác sĩ trước tuần 3 → bỏ nhánh này, đích là PM. (b) ~~Độ đặc hiệu phép thử nhìn thấy~~ đã đo 12/09 (âm tính giả 18 %); thay bằng: STV **sau cổng** trên ADFECGDB + 60 sạch. | Bộ nạp + bảng thống kê bộ thứ ba; giao thức đặc hiệu | Tuần 1(c) | Chủ nhiệm |
| **4** (5–11/10) | (a) [V7] Chỉ nếu có bộ tự chú thích: **chạy đúng một lần** psd / gate / peakprob / oracle, bootstrap, Holm; báo cáo bất kể kết quả. (b) Tính lại nhóm (b) phổ lỗi kèm khoảng bất định từ âm tính giả 18 %. (c) **Quyết định đích**: có bộ có nhãn mới và peakprob thắng (KTC không chứa 0) → JBHI; mọi trường hợp khác → PM (mặc định). | `analysis/bo_thu_ba_results.json`; `chandoan_dachieu.json`; ghi chú quyết định | Tuần 3 | Chủ nhiệm; giảng viên xem kết quả |
| **5** (12–18/10) | (a) Huấn luyện 2 hạt giống thêm cho cấu hình chính (22 chủ thể, 11 fold) — ~2 × thời gian `train_22_seed1`. (b) Bắt đầu thí nghiệm **SNR thấp có kiểm soát**: hạ SNR dữ liệu trong miền (theo `pilot_evidence/snr_curve.json`), huấn luyện lại 1 hạt giống, đo trên 60 sạch. | Checkpoint seed 2, 3; `snr_aug_results.json` (sơ bộ) | GPU; tuần 2 | Chủ nhiệm |
| **6** (19–25/10) | (a) Tổng hợp 3 hạt giống: bảng chính với trung bình ± SD hạt giống. (b) Kết thúc SNR thấp: nếu cải thiện → một mục; nếu không → một đoạn kết quả âm tính. (c) STV **sau cổng** trên ADFECGDB + 60 sạch (rẻ, có thể cứu mục lâm sàng). | `main_3seed.json`; `snr_aug_results.json`; `clinical_gated.json` | Tuần 5 | Chủ nhiệm |
| **7** (26/10–1/11) | (a) Rà văn liệu: liệt kê các bài huấn luyện ADFECGDB + kiểm set-a (Scopus/Google Scholar), ghi từng bài có/không bị ảnh hưởng. (b) Viết mục 2 (kiểm toán rò rỉ) và mục 4 (89,5 %) hoàn chỉnh. | `survey/anh_huong_ro_ri.md`; bản nháp mục 2, 4 | — | Chủ nhiệm; giảng viên góp ý mục 2 |
| **8** (2–8/11) | (a) Viết mục 5, 6, 7. (b) Hình chính: (i) sơ đồ rò rỉ 5→15, (ii) F1 và logit theo quy tắc trên hai/ba bộ, (iii) risk–coverage, (iv) phổ lỗi có mức ngẫu nhiên. (c) Xin **góp ý lâm sàng** từ bác sĩ sản (qua giảng viên) về mục Discussion: cổng từ chối có chấp nhận được trong theo dõi không, độ phủ 67 % nghĩa là gì trong thực hành. | Bản nháp đầy đủ v1; 4 hình | Tuần 4–7 | Chủ nhiệm; **bác sĩ sản** (1 buổi) |
| **9** (9–15/11) | (a) Gói tái lập: Zenodo cho checkpoint + JSON, script `reproduce_tables.py` chạy từ JSON ra mọi bảng, commit hash trong chú thích bảng. (b) Giảng viên đọc phản biện nội bộ theo checklist vòng 6 (a)–(g). | DOI Zenodo; phản biện nội bộ | Tuần 8 | Giảng viên (phản biện) |
| **10** (16–22/11) | Sửa theo phản biện nội bộ; viết cover letter nêu thẳng: rò rỉ, hậu kiểm, các số đã rút; đề xuất phản biện (3–4 tên trong cộng đồng fECG — giảng viên gợi ý). | Bản v2; cover letter | Tuần 9 | Chủ nhiệm, giảng viên |
| **11** (23–29/11) | (a) Kiểm cuối: mọi số trong bài ↔ JSON (script tự động). (b) Chuẩn bị bản CinC 2027 4 trang (rút từ v2) để nộp abstract tháng 4. (c) Nếu Eureka cần hồ sơ trước 12/2026: chuẩn bị tóm tắt tiếng Việt từ v2. | Báo cáo kiểm số; `paper/cinc2027/`; tóm tắt Eureka | Tuần 10 | Chủ nhiệm |
| **12** (30/11–6/12) | **Nộp PM** (hoặc JBHI nếu tuần 4 có dữ liệu có nhãn mới) [V7]. Đăng preprint (arXiv q-bio/eess.SP hoặc medRxiv) cùng ngày nếu tạp chí cho phép (JBHI và PM đều cho). | Số nộp; preprint | Tuần 11 | Chủ nhiệm |

**Việc chủ nhiệm PHẢI xin giảng viên, và xin từ tuần 1:**
1. Thư giới thiệu đến khoa sản để xin ghi bụng có tham chiếu (trung tâm thứ hai có nhãn thật) — đây là việc duy nhất có thể đưa bài lên mức "hai trung tâm", nhưng thời gian xin phép đạo đức thường 3–6 tháng: **không tính vào bài này**, tính vào bài sau và vào hồ sơ Eureka như "đang tiến hành".
2. Một buổi với bác sĩ sản (tuần 8) để mục Discussion không viết sai về thực hành CTG/STV.
3. Phản biện nội bộ tuần 9 và gợi ý tên phản biện.
4. Xác nhận thang xếp hạng mà Eureka/trường dùng (Scimago hay JCR) — quyết định PM có "đếm" hay không.

**Đường mặc định [V7]:** PM; peakprob viết là "giả thuyết mạnh, chưa xác nhận" đúng phán xử vòng 6 và 7. Nâng lên JBHI chỉ khi tuần 4 có bộ có nhãn mới và kết quả thuận.

---

## 6. ĐÁNH GIÁ THẲNG THẮN

* **Điều tốt nhất về bài này không phải con số nào.** Đó là việc nhóm tự kiểm lại chồng lấn mà ban tổ chức đã ghi nhận (và nhóm từng bỏ sót), định danh đúng 15 bản trùng, tự rút số, tự khai chọn hậu kiểm, và báo cáo bốn thất bại. Ở mức sinh viên đây là hiếm; ở mức tạp chí Q1 đây là thứ phản biện *muốn* thấy và ít khi thấy. Hãy đặt nó ở giữa bài, không phải ở phụ lục.
* **Điểm yếu lớn nhất vẫn là peakprob hậu kiểm** và nó chỉ được cứu bằng dữ liệu có nhãn mới — không có bộ công khai nào, phải tự chú thích hoặc xin ngoài [V7]. Không có, bài vẫn công bố được (PM), nhưng không phải Q1 ở JBHI.
* **Điểm yếu thứ hai: phép thử nhìn thấy có âm tính giả 18 %** — đã đo [V7]; nền của "khoảng cách là do không có tín hiệu" mất, mục 6 phải hạ giọng thành "chưa xác định nguyên nhân".
* **Điều mà chủ nhiệm cần nghe:** mục tiêu "Q1 + A\* + Eureka trong một năm" với bài này là hai trong ba. Q1 chỉ thực tế khi có dữ liệu có nhãn mới (≈ 15–20 % trong 6 tháng, ≈ 35 % trong 12 tháng) [V7]. Eureka là thực tế nếu hội đồng coi trọng tính nghiêm và ứng dụng (demo, API, cổng từ chối) — hồ sơ Eureka nên kể câu chuyện kiểm toán, không kể câu chuyện "97,56 %". A\* thì không, và cố nộp A\* trong 3 tháng sẽ lấy đi chính thời gian làm ba việc để có Q1.
* **Quy mô lớn nhất chưa được nói:** 22 chủ thể huấn luyện, 5 trong số đó cũng là nguồn của 15 bản CinC bị rò rỉ. Sau khi bỏ, dữ liệu ngoài miền là 60 bản ghi 1 phút. Bài Q1 sẽ được nhận với quy mô đó nếu kiểm toán chặt; bài A\* thì không bao giờ.

## 7. HẠN CHẾ CỦA CHÍNH TÀI LIỆU NÀY

1. Mọi xác suất chấp nhận là ước lượng chủ quan; không có dữ liệu tỉ lệ nhận theo loại bài của từng tạp chí.
2. IF và quartile lấy qua trang tổng hợp bên thứ ba; Scimago trả 403 khi tải trực tiếp. Quartile Scimago có thể khác giữa các danh mục và giữa năm 2024/2025; JCR có thể xếp khác.
3. Hạn nộp CinC 2027, ICML 2027, MICCAI 2027, NeurIPS 2027 E&D là suy từ thông lệ hoặc trang không chính thức.
4. [Đã giải quyết 12/09, `analysis/XACNHAN.md`: không có nhãn fQRS công khai ở NIFEADB / NInFEA / nifecgdb / set-b.]
5. [Đã giải quyết 12/09, `survey/RO_RI_VANLIEU.md`: chồng lấn đã được ban tổ chức ghi nhận từ 2013; đóng góp #1 là "định lượng hậu quả".]
6. Tôi không chạy lại thí nghiệm nào; các con số trích từ JSON/MD như vòng 6 đã đối chiếu, cộng thêm `baselines/powermf_fair_stats.json` mà vòng 6 chưa kiểm.
7. Xác suất NeurIPS E&D dựa trên hiểu biết về track qua các năm trước và hướng dẫn phản biện 2026; tôi không có số liệu tỉ lệ nhận theo loại bài "audit".
