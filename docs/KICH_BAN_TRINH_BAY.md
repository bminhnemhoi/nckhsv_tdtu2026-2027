# Kịch bản buổi gặp đầu tiên với giảng viên hướng dẫn (20–30 phút)

Sổ tay: https://claude.ai/code/artifact/7f120fe6-e199-47b9-8aac-1a194c2d8b00

**Lưu ý trước khi dùng:** mục 14 của sổ tay hiện còn câu cũ "trên bộ dữ liệu 75 sản phụ… từ 79,4 lên 85,6" và mục 10 còn "+6,20 điểm". Hai số đó đã rút (bộ CinC nhiễm 15 bản). Trong buổi gặp chỉ nói **60 bản sạch, 74,28 → 82,01, +7,73**. Nên sửa sổ tay trước buổi gặp.

`docs/HUONG_DAN_DEMO.md` của agent R4 chưa có trên đĩa; phần demo dưới đây soạn theo `demo/README.md` (Gradio, `python demo/app.py`, cổng 7860). Khi R4 ra tài liệu, đối chiếu lại thứ tự thao tác.

---

## 1. Mục tiêu buổi gặp — em muốn gì từ cô

Ba thứ, theo thứ tự ưu tiên:

1. **Dữ liệu và lâm sàng:** một đầu mối bác sĩ sản hoặc khoa sản đang ghi điện tim bụng (kể cả chỉ để phỏng vấn 30 phút). Đây là thứ em không tự làm được.
2. **Định hướng nơi công bố:** em đang nhắm Physiological Measurement (theo Scimago 2024 là Q2/Q3, không phải Q1; Q1 thì là IEEE JBHI hoặc BSPC nhưng cần bộ dữ liệu thứ ba có nhãn, hiện chưa có) và hội nghị CinC 2027 đã có bản nháp 4 trang; xin cô nhận xét có hợp không, hay nên nhắm chỗ khác, và thứ tự nộp.
3. **Đồng ý về cách kể:** em định trình bày đề tài kèm những gì đã rút lại. Em muốn cô biết trước điều đó và cho ý kiến có nên kể ở Euréka không.

Thứ **không** phải mục tiêu buổi này: xin cô duyệt kết quả, xin cô sửa mã, xin thêm thời gian.

---

## 2. Dàn ý 20 phút theo phút

### 0–2 phút — Mở đầu

**Nói gì (lời thoại):**
> "Em chào cô. Em xin 20 phút: 2 phút nói em làm gì, 4 phút vấn đề, 6 phút phương pháp và kết quả có demo, 4 phút những chỗ em đã vấp và sửa, rồi 4 phút cuối em xin cô ba việc. Cô ngắt bất cứ lúc nào cũng được ạ.
>
> Em làm hệ thống đọc điện tim thai từ **một** điện cực dán trên bụng mẹ, tìm từng nhịp tim của bé, và — phần em coi là chính — tự biết khi nào nó không đáng tin để nói 'tôi không chắc' thay vì đưa ra một con số sai. Tên hệ thống là RelyFetal."

**Chiếu gì:** trang đầu sổ tay (4 ô số: 113.481 tham số · 22 sản phụ huấn luyện · 60 bản ghi kiểm tra ngoài · ≈27.700 dòng mã, 56 hàm kiểm thử (39 tests/ + 17 demo/)).

**Không nói gì:** "state-of-the-art", "đầu tiên", "chưa ai làm". Không nói "Q1" ở phút này — để dành cho phần xin hỗ trợ.

### 2–6 phút — Vấn đề và ý tưởng

**Nói gì:**
> "Thai chậm phát triển là một trong các nguyên nhân hàng đầu của thai lưu. Dấu hiệu sớm không phải nhịp nhanh hay chậm, mà là nhịp tim thai mất biến thiên tự nhiên. Muốn đo biến thiên phải biết từng nhịp rơi vào mili-giây nào.
>
> Hiện có hai cách: siêu âm Doppler thì phổ biến nhưng đo chuyển động van, sai số thời điểm lớn; điện cực da đầu thì chính xác nhưng xâm lấn, chỉ dùng khi đã chuyển dạ. Điện tim bụng mẹ là cách duy nhất vừa không xâm lấn vừa cho tín hiệu điện. Nhưng tín hiệu thai nhỏ hơn tim mẹ nhiều lần và trùng dải tần với cơ tử cung.
>
> Các nhóm khác dùng 4 đến 32 điện cực và tách nguồn. Em hỏi ngược lại: nếu chỉ có một dây — để sau này thành miếng dán mẹ tự đeo — thì mất bao nhiêu, và hệ thống có tự biết lúc nào nó không nhìn thấy tín hiệu không? Câu hỏi thứ hai em nghĩ là quan trọng hơn với bác sĩ."

**Chiếu gì:** bảng "Hai cách đo hiện có" và bảng "Thành phần tín hiệu" (sổ tay mục 02–03).

**Không nói gì:** không hứa "miếng dán" là sản phẩm sắp có — nói là tầm nhìn. Không nêu chỉ số STV như thứ đã đo được (phải nói thật ở phần vấp).

### 6–12 phút — Phương pháp và kết quả, kèm demo 4 phút

**Nói gì (2 phút, trước demo):**
> "Đường ống có 5 bước: lọc 10–60 Hz pha-không, khử điện tim mẹ bằng mẫu trung vị co giãn từng nhịp, chọn kênh mù nhãn, một mạng tích chập thời gian nhỏ — 113 nghìn tham số, 0,48 MB, 4,35 mili-giây cho mỗi cửa sổ 4 giây — cho ra đường xác suất từng mẫu, và một cổng từ chối dùng 12 chỉ số chất lượng tín hiệu cổ điển.
>
> Kết quả chính trên 22 sản phụ: phương pháp mạnh nhất hiện có, Power-MF, dùng 4 kênh đạt 98,83; chính nó cắt xuống 1 kênh còn 86,71; mạng 1 kênh của em đạt 97,56. Nói đúng: em vẫn thua 4 kênh 1,27 điểm, nhưng 4 kênh đáng giá 12,12 điểm và một kênh lấy lại được 10,85 — khoảng chín phần mười, khoảng tin cậy từ 81 đến 103 phần trăm (`baselines/powermf_fair_stats.json`).
>
> Trên bộ CinC 2013 mà mô hình chưa từng thấy, sau khi lọc rò rỉ còn 60 bản sạch: quy tắc chọn kênh cũ cho 74,28, quy tắc mới cho 82,01, cộng 7,73 với khoảng tin cậy từ 3,8 đến 12,4 (`analysis/dulieu_results.json`). Cổng từ chối, không dùng nhãn, xếp loại bản ghi với AUROC mức bản ghi 0,980 (đo trên 75 bản gồm 15 bản nhiễm — chưa tính lại trên 60 sạch) và nếu giữ hai phần ba bản ghi thì loại được 15 trong 16 bản tệ nhất (`analysis/gate22_cinc.json`). Giờ em cho cô xem nó chạy."

**Demo 4 phút — thao tác (máy đã mở sẵn `python demo/app.py` với `RELYFETAL_AUTORUN=1`, trình duyệt ở http://127.0.0.1:7860, bản r01 đã phân tích xong):**

| Phút | Thao tác | Nói gì |
|---|---|---|
| 0:00–1:00 | Tab *Tín hiệu 5 tầng*, bản r01 (ADFECGDB, checkpoint fold chưa thấy r01). Chỉ tay theo 5 tầng từ trên xuống. | "Tầng trên là tín hiệu thô — cô thấy các gai lớn là tim mẹ. Tầng hai đã lọc, vạch đỏ là đỉnh mẹ tìm được. Tầng ba là sau khi trừ mẹ — cái còn lại rất nhỏ, đó là tim bé. Tầng bốn là xác suất mô hình. Tầng năm là kết quả so với nhãn: chấm xanh đúng, đỏ là báo thừa, cam là bỏ sót." |
| 1:00–1:45 | Chỉ 4 thẻ số (F1, số nhịp, thời gian xử lý, đèn tin cậy). Chuyển tab *Nhịp tim thai theo thời gian*. | "Bản này F1 trên 99, xử lý cả bản 5 phút mất dưới một giây trên CPU. Đèn tin cậy xanh — nghĩa là hệ thống nói 'tin được'. Đường này là nhịp tim thai theo từng 4 giây — thứ bác sĩ cần để tính biến thiên." |
| 1:45–3:15 | Đổi nguồn sang CinC, chọn **a02**, bấm *Phân tích*. Đợi ~2 giây. Chỉ đèn **thấp**. | "Đây là phần em coi là quan trọng nhất. Bản a02 mô hình bám nhầm vào tàn dư tim mẹ ở khoảng 125 nhịp/phút — nhìn tầng bốn xác suất vẫn cao, nhìn F1 thì tệ. Nhưng đèn đỏ: cổng phát hiện hơn 60 % nhịp 'thai' trùng đỉnh mẹ, nên hệ thống từ chối trả lời. Với bác sĩ, 'tôi không chắc' ở đây đáng giá hơn một con số đẹp sai." |
| 3:15–4:00 | Mở tab *Nhật ký JSON*, cuộn qua. Tắt trình duyệt, quay về sổ tay. | "Mọi thứ cô vừa xem đều xuất ra JSON, có thể gọi qua API. Demo là bản mẫu nghiên cứu, không phải thiết bị y tế — em ghi câu đó ngay đầu trang." |

**Dự phòng nếu demo hỏng:** mở `demo/screenshots/` (6 ảnh) và nói theo cùng thứ tự; không mất quá 30 giây để chuyển.

**Chiếu gì:** demo; bảng 22 chủ thể (sổ tay mục 08); bảng 7 quy tắc chọn kênh trên 60 bản sạch (mục 09).

**Không nói gì:** 79,40 / 85,60 / +6,20 (75 bản nhiễm); 94,87 / +2,74 / 98,38 / 97,33 (Power-MF cổng chuyển hỏng); +11,00 dải lọc; "trần 93,1" và "8 bản giới hạn cứng" như phát hiện; "tiền đăng ký"; "một kênh thắng bốn kênh".

### 12–16 phút — Những gì đã vấp và đã sửa

**Nói gì:**
> "Phần này em nghĩ là thứ đáng nói nhất, vì nó cho thấy cách em làm việc.
>
> Một, bộ kiểm tra bị nhiễm — điều ban tổ chức CinC 2013 đã ghi từ 2013 (Silva 2013; Clifford 2014) mà em bỏ sót dù câu cảnh báo nằm trong ghi chú đọc bài của chính em. Khi kiểm lại thì 15 trong 75 bản CinC là bản sao nguyên văn của dữ liệu huấn luyện — tương quan đúng 1,0000, lệch nhịp đúng 0,0 mili-giây, mỗi bản huấn luyện xuất hiện đúng 3 lần (`analysis/DULIEU.md`). Em loại 15 bản, số chính rớt 5 điểm, nhưng cải tiến chọn kênh trên dữ liệu sạch lại mạnh hơn: cộng 7,73 thay vì 6,20. Cải tiến thật không sợ dữ liệu sạch.
>
> Hai, em chạy lại Power-MF bằng Octave vì không có MATLAB, và lúc đầu nó cho kết quả sai. Em đoán nguyên nhân trước khi đo, và đoán sai. Đo lại thì ra lỗi cổng chuyển của em — hàm tìm đỉnh của Octave tràn bộ nhớ. Sửa xong, số của em là 99,40 còn tác giả công bố 99,46 (`baselines/powermf_published.json`). Từ đó em có luật: không phát biểu nguyên nhân trước khi có số.
>
> Ba, em tự rút ba tuyên bố: dải lọc cho +11 điểm — đo lại trên đúng mô hình thì gần bằng 0; 'đơn kênh hơn đa kênh' — sai, thua 1,27; và một phát hiện về 'hai nhóm (chia hậu kiểm)' — bị chính đối chứng của em bác. Và phép thử xác nhận em ghi trước cho quy tắc chọn kênh đã trượt: luật ghi trước chỉ vào quy tắc 'gate', gate trượt hiệu chỉnh Holm với p 0,051; quy tắc thắng là chọn sau khi nhìn kết quả. Em vẫn báo cáo nó nhưng gọi là giả thuyết mạnh chưa xác nhận, và bước tiếp theo bắt buộc là chạy một lần trên bộ thứ ba.
>
> Bốn, chỉ số lâm sàng: em đo biến thiên ngắn hạn STV, trên dữ liệu trong miền lệch 0,33 mili-giây nhưng trên CinC lệch 20,5 (`analysis/clinical_results.json`). Chưa dùng được làm máy đo độc lập. Nhưng chính điều đó là lý do cần cổng từ chối: khi F1 trên 99,5 thì sai số chỉ 0,13 mili-giây."

**Chiếu gì:** sổ tay mục 11 (Nhật ký sự cố) — bảng trùng lặp r01→a04,a05,a22…; mục 10 phần "Ba thứ đã rút lại".

**Không nói gì:** không liệt kê quá 4 sự cố (còn lại để cô hỏi). Không nói "agent" hay "AI thẩm định" trừ khi cô hỏi cách làm việc — nếu hỏi thì nói thật: em dùng công cụ tự động đối chiếu 89 con số với tệp gốc, và tự chịu trách nhiệm về từng số.

### 16–18 phút — Định vị và kế hoạch

**Nói gì:**
> "Đóng góp em định nộp không phải 'một máy dò tốt hơn'. Là ba thứ: một phép đo — một kênh lấy lại bao nhiêu phần của bốn kênh; một phê bình thước đo — F1 có trần 100 nên trên 19 sản phụ dễ, một kênh thực sự hơn bốn kênh trên thang logit mà F1 thô báo là hoà (`analysis/stats_results.json`); và một cổng từ chối biết lúc nào nó sai.
>
> Kế hoạch 3 tháng: (1) chạy quy tắc chọn kênh đúng một lần trên CinC set-b hoặc NInFEA với quy tắc chốt trước, báo cáo bất kể kết quả; (2) 3 hạt giống cho kết quả chính; (3) tính lại nhánh 22 sản phụ trên thang logit; (4) nộp CinC 2027 bản 4 trang đã có, rồi bản dài cho tạp chí. Hai việc em quyết định **không** làm nữa vì đã đo thấy vô ích: đổi kiến trúc — 7 họ cùng tham số chỉ cách nhau dưới 1 điểm (`analysis/kientruc_results.json`); và thích nghi miền — 4 phương pháp đều hỏng (`analysis/THICHNGHI.md`)."

**Chiếu gì:** bảng "Còn thiếu gì" (sổ tay mục 13).

**Không nói gì:** không nói "chắc chắn Q1". Không nói "kiến trúc không quan trọng" tuyệt đối — nói "đòn bẩy yếu nhất đã đo".

### 18–20 phút — Xin hỗ trợ

**Nói gì:**
> "Em xin cô ba việc. Một, nếu cô có liên hệ với khoa sản nào đang ghi điện tim bụng hoặc CTG, em xin được gặp một bác sĩ 30 phút — em cần biết bác sĩ cần chính xác bao nhiêu thì mới dùng được, và có thể xin dữ liệu có nhãn từ trung tâm thứ hai. Hai, cô xem giúp Physiological Measurement và CinC có hợp không, hay cô thấy chỗ khác hợp hơn. Ba, em định nộp Euréka 2027 lĩnh vực Công nghệ thông tin; em xin cô ý kiến có nên kể phần rút lại trước hội đồng sinh viên không.
>
> Em muốn bài này có thực lực chứ không phải đẹp số. Mọi con số trong đề cương truy ngược được về một tệp trên máy, và em sẵn sàng gửi cô kho mã ngay hôm nay."

**Chiếu gì:** trang 1 tờ tóm tắt (`docs/TOM_TAT_1_TRANG.md` in giấy).

**Không nói gì:** không xin "cô ký" bất cứ thứ gì trong buổi đầu.

---

## 3. Mười hai câu cô có thể hỏi, và câu trả lời mẫu

**Từ dễ đến khó. Mỗi câu 2–4 câu trả lời.**

1. **"Em tóm tắt lại đề tài trong một phút được không?"**
   "Em đọc điện tim thai từ một điện cực trên bụng mẹ, tìm từng nhịp, và hệ thống tự chấm mức tin cậy để từ chối khi tín hiệu không đủ. Trên 22 sản phụ em đạt 97,56 so với 98,83 của phương pháp bốn kênh mạnh nhất. Trên 60 bản ghi chưa từng thấy em đạt 82,01 và cổng từ chối lọc được 15 trong 16 bản tệ nhất."

2. **"Vì sao chỉ một kênh, trong khi bệnh viện dùng nhiều kênh?"**
   "Vì mục tiêu xa là thiết bị mẹ tự đeo ở nhà, một dây mới đeo được. Câu hỏi khoa học em đặt là 'mất bao nhiêu khi bỏ ba kênh' — em đo được mất 1,27 điểm so với bốn kênh, tức lấy lại chín phần mười. Em không nói một kênh tốt hơn."

3. **"Dữ liệu lấy ở đâu, có nhãn không, bao nhiêu người?"**
   "Bốn bộ công khai: ADFECGDB 5 sản phụ và Silesia 22 bản ghi có nhãn từ điện cực da đầu — dùng huấn luyện; CinC 2013 75 bản ghi chỉ để kiểm tra. Nhưng 15 bản CinC là bản sao của ADFECGDB (ban tổ chức đã ghi nhận; em đo lại để biết đúng bản nào) nên chỉ dùng 60 bản sạch. Tổng cộng 22 chủ thể huấn luyện, và 77 % thời lượng có nhãn gián tiếp — đó là điểm yếu em ghi rõ."

4. **"So với phương pháp hiện có thì thắng hay thua?"**
   "Thua trung bình 1,27 điểm so với Power-MF bốn kênh, thắng 18 trên 22 bản, trung vị cộng 0,23. Ba bản khó kéo trung bình xuống. So với Power-MF một kênh thì hơn 10,85, thắng 22 trên 22. Em chạy lại Power-MF trên máy mình và số khớp với tác giả công bố trong 0,06 điểm nên so sánh là công bằng."

5. **"Mô hình nhỏ vậy có phải vì thiếu máy không?"**
   "Không ạ, là chủ đích. Nhân bốn lần tham số chỉ được cộng 0,26 điểm trong mẫu, không đáng. 113 nghìn tham số, 0,48 MB, chạy 4,35 mili-giây cho 4 giây tín hiệu trên CPU — đủ nhét vào vi điều khiển sau này. Em đã so 7 họ kiến trúc cùng tham số, cùng hạt giống; ba họ đầu tương đương nhau theo kiểm định tương đương."

6. **"Cổng từ chối hoạt động thế nào, nó sai thì sao?"**
   "Mỗi đoạn 4 giây em tính 12 chỉ số chất lượng cổ điển — entropy, độ nhọn, tỉ lệ RR hợp lý, năng lượng dải thai… — đưa vào một bộ phân loại nhỏ ra xác suất 'đoạn này xấu'. Không dùng nhãn lúc chạy. Trên 22 sản phụ, đánh giá bỏ-một-chủ-thể, nó xếp đúng ba bản khó nhất vào ba hạng chót, xác suất ngẫu nhiên là 1 trên 1540. Nó có sai: 5 trong 24 quy tắc một đặc trưng đơn giản cũng xếp đúng ba bản đó, nên em không dám nói phải học mới làm được."

7. **"Rò rỉ dữ liệu là sao — em có chắc không? Người khác có bị không?"**
   "Em kiểm bằng tương quan chéo chuẩn hoá từng cặp tín hiệu và so chuỗi khoảng nhịp tham chiếu. 15 bản cho tương quan đúng 1,0000 và lệch nhịp 0,0 mili-giây, cả 4 kênh sao đúng thứ tự, mỗi bản ADFECGDB xuất hiện đúng 3 lần theo cửa sổ 0–60, 120–180, 240–300 giây. Đối chứng dương là các bản cùng sản phụ đã biết chỉ cho 0,86–0,98; 60 bản còn lại cao nhất 0,62. Hai cách cài đặt độc lập cùng kết quả. Về người khác: em chỉ dám nói bài nào huấn luyện trên ADFECGDB và kiểm trên CinC set-a thì có cùng rủi ro; em chưa kiểm từng bài."

8. **"Quy tắc chọn kênh mới có phải em chọn sau khi nhìn kết quả không?"**
   "Dạ đúng, và em nói rõ trong bài. Em ghi trước 7 quy tắc và một luật quyết định là 'chọn quy tắc tốt nhất trong miền'. Luật đó chỉ vào gate, và gate trượt hiệu chỉnh Holm với p 0,051. peakprob là chọn sau. Lý do em vẫn báo cáo: hiệu ứng sống sót Holm trên cả họ 7 quy tắc với p 0,0039, và không có siêu tham số nào để tinh chỉnh. Nhưng em gọi nó là giả thuyết mạnh chưa xác nhận, và bước tiếp theo là chạy đúng một lần trên bộ thứ ba."

9. **"Có ý nghĩa lâm sàng chưa? Bác sĩ dùng được gì?"**
   "Chưa, và em phải nói thẳng. Chỉ số STV em đo lệch 0,33 mili-giây trên dữ liệu trong miền nhưng lệch 20,5 trên CinC — chưa dùng được làm máy đo độc lập. Điều bác sĩ dùng được ngay là cổng từ chối: khi cổng cho phép thì sai số STV chỉ 0,13 mili-giây. Còn 'bác sĩ cần chính xác bao nhiêu' là câu em muốn hỏi cô, vì em chưa gặp bác sĩ nào."

10. **"22 chủ thể có đủ để kết luận không?"**
    "Không đủ cho kết luận mạnh. Em tự tính công suất thống kê thì cần khoảng 50. Với 5 sản phụ ADFECGDB, p nhỏ nhất Wilcoxon có thể cho là 0,0625 nên không bao giờ có p < 0,05. Em làm mọi thống kê ở mức chủ thể với cluster bootstrap và 5 kết luận cũ bị đảo khi làm đúng. Vì vậy xin dữ liệu trung tâm thứ hai là việc em cần cô giúp nhất."

11. **"Em định nộp ở đâu, khi nào? Q1 có thực tế không?"**
    "Bản 4 trang cho CinC 2027 em đã có. Bản dài em nhắm Physiological Measurement. Thực tế thì em nghĩ Q1 cần ít nhất một trong hai: xác nhận trên bộ thứ ba hoặc dữ liệu trung tâm thứ hai — cả hai đều chưa có. Nếu cô thấy nên nhắm tạp chí khác trước để có công bố sớm hơn, em nghe cô."

12. **"Ba tháng tới em làm gì tiếp, và em cần gì ở cô?"**
    "Ba việc rẻ mà quyết định: chạy peakprob một lần trên set-b hoặc NInFEA, 3 hạt giống cho kết quả chính, tính lại 22 chủ thể trên logit (ĐÃ LÀM 12/09: gate vẫn đứng đầu, peakprob hạng 3 — vấn đề hậu kiểm không biến mất). Hai việc em dừng vì đã đo thấy vô ích: đổi kiến trúc và thích nghi miền. Ở cô em xin: một đầu mối bác sĩ sản, ý kiến về nơi nộp, và ý kiến có nên đi Euréka 2027."

---

## 4. Ba điểm rút lui khi bị hỏi dồn

1. **Cô hỏi một sự thật lâm sàng em không biết** (ví dụ: ngưỡng STV bất thường theo hướng dẫn nào, tuần thai nào đo được):
   > "Em chưa biết, và em chưa hỏi bác sĩ nào — đó chính là điều em muốn xin cô giới thiệu. Em ghi lại câu hỏi và trả lời cô bằng nguồn cụ thể sau."
   Không đoán, không trích số nhớ mang máng.

2. **Cô hỏi một con số em không nhớ chính xác** (ví dụ: khoảng tin cậy của một quy tắc phụ, số đoạn xấu trong tập huấn luyện cổng):
   > "Em không nhớ chính xác để nói ra. Mọi số nằm trong tệp kết quả trên máy — em mở ngay được nếu cô muốn, hoặc gửi cô sau chứ em không đoán."
   Rồi mở đúng tệp (`analysis/dulieu_results.json`, `analysis/gate22_results.json`) nếu cô muốn xem.

3. **Cô hỏi về một phương pháp em chưa thử** (ví dụ: "sao không dùng Transformer / học tự giám sát / dữ liệu tổng hợp?"):
   > "Em chưa thử cái đó. Em ghi lại làm việc tiếp. Nếu cô hỏi em đoán, thì em đoán là … — nhưng đó là phỏng đoán, không phải kết quả, và em đã từng đoán sai một lần với Power-MF nên em không tin phỏng đoán của mình lắm."
   Nếu là kiến trúc: nói thêm "em đã đo 7 họ cùng tham số và thấy đòn bẩy kiến trúc yếu, nên em sẽ chỉ thử nếu cô thấy có lý do đặc biệt".

Quy tắc chung: câu nào bắt đầu bằng "em nghĩ" thì phải kết thúc bằng "nhưng chưa đo".

---

## 5. Danh sách mang theo

| Thứ | Trạng thái cần | Ghi chú |
|---|---|---|
Sổ tay: https://claude.ai/code/artifact/7f120fe6-e199-47b9-8aac-1a194c2d8b00
| Demo | `python demo/app.py` chạy trước 10 phút, `RELYFETAL_AUTORUN=1`, r01 đã phân tích xong, tab trình duyệt thứ hai mở sẵn `demo/screenshots/` | Kiểm `pip install gradio plotly` và checkpoint `model/checkpoints/fetalqrs_tcn_fold_r01.pt`, `fetalqrs_tcn_production.pt` có mặt. Đặt `PYTHONIOENCODING=utf-8`. Tắt Wi-Fi không cần thiết; demo chạy cục bộ. |
| 1 trang tóm tắt in giấy | 2 bản (1 cho cô, 1 cho mình) | Nội dung: `docs/TOM_TAT_1_TRANG.md` |
| Bài CinC 4 trang | 1 bản in `docs/CinC2026_RelyFetal.pdf` | Chỉ đưa nếu cô hỏi về nơi nộp |
| Kho mã | Link GitHub sẵn trong tin nhắn nháp | https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027 |
| Sổ ghi câu hỏi | Giấy hoặc tệp trống | Ghi từng câu cô hỏi mà mình chưa trả lời được — đây là đầu vào cho email cảm ơn |

---

## 6. Sau buổi gặp

### Email cảm ơn (gửi trong 24 giờ)

> **Tiêu đề:** Cảm ơn cô — tóm tắt buổi gặp đề tài RelyFetal ngày [dd/mm]
>
> Em chào cô,
>
> Em cảm ơn cô đã dành thời gian cho em hôm [thứ, ngày]. Em ghi lại 5 ý chính để cô kiểm giúp em có hiểu đúng không:
>
> - [Ý 1 — nhận xét chính của cô về hướng đề tài]
> - [Ý 2 — ý kiến của cô về nơi nộp: CinC / Physiological Measurement / nơi khác]
> - [Ý 3 — cô nói gì về việc kể phần rút lại, và về Euréka]
> - [Ý 4 — câu hỏi cô đặt mà em chưa trả lời được; em sẽ trả lời bằng nguồn trước ngày …]
> - [Ý 5 — mốc hẹn lần sau]
>
> Ba việc em xin cô, khi nào cô tiện:
>
> 1. Giới thiệu giúp em một bác sĩ sản hoặc khoa sản đang ghi CTG/điện tim bụng để em xin phỏng vấn 30 phút (và, nếu có thể, xin dữ liệu có nhãn từ trung tâm thứ hai).
> 2. Cô xem giúp bản nháp CinC 4 trang (đính kèm) — em chỉ cần nhận xét về cách đặt đóng góp và mức độ thận trọng của phát biểu.
> 3. Cho em biết cô có đồng ý đứng tên hướng dẫn hồ sơ Euréka 2027 lĩnh vực Công nghệ thông tin không, để em hỏi Đoàn trường quy trình sơ tuyển.
>
> Kho mã và sổ tay: [link GitHub], [link sổ tay]. Mọi con số trong đó truy ngược được về tệp kết quả trên đĩa.
>
> Em cảm ơn cô.
> Ngô Bình Minh — [lớp, khoa, số điện thoại]

### Việc làm ngay sau buổi

- Ghi vào `docs/` một tệp `NHAT_KY_GAP_GVHD.md`: ngày, người dự, 5 ý trên, việc được giao, hạn.
- Trả lời từng câu "em chưa biết" bằng nguồn trong vòng 3 ngày.
- Nếu cô đồng ý Euréka: hỏi Đoàn trường TDTU quy trình sơ tuyển và hạn (xem `docs/EUREKA.md` mục 4).
