# Kịch bản buổi gặp đầu tiên với giảng viên hướng dẫn (20 phút + hỏi đáp)

> **⚠ CẢNH BÁO (17/09/2026) — tệp lưu trữ** của buổi gặp 14/09, dựng quanh demo 8 tab. Đã cũ so với demo sau lượt
> sửa thứ ba: số kiểm thử (17, 82; hiện 111 = 43 trong `tests/` + 68 trong `demo/test_core.py`); số dòng mã (27.700;
> hiện ≈ 31.000 — 30.957 dòng trong 136 tệp `.py` theo dõi hoặc chưa bị bỏ qua, `wc -l`, 17/09); tên
> `docs/HUONG_DAN_DEMO.md` (nay là `HUONG_DAN_DEMO_v1.md`); câu "hệ thống tự biết khi nào nó không đáng tin" nói quá
> (đèn chỉ báo khi thấy dấu hiệu xấu, không phải lần nào cũng thấy: a57 đèn xanh, F1 17,02 —
> `demo/results/demo_check_2modes.json → summary_by_mode.hoc.green_but_F1_below_90`); "bộ khác, máy khác" chưa kiểm được (ban tổ chức CinC 2013 không công bố
> thiết bị ghi của từng bản). Buổi trình bày mới dùng `docs/KICH_BAN_THUYET_TRINH_v2.md` và `docs/HUONG_DAN_DEMO_v2.md`.
> **Địa chỉ demo trong tệp này cũng đã cũ:** từ commit ghép 17/09, `http://127.0.0.1:7860` mở trang nghiên cứu HTML,
> còn chế độ trình bày nằm ở `http://127.0.0.1:7860/gradio/`.
>
> **Thẩm định cuối 17/09 — các chỗ trong lời thoại dưới đây đã sửa hoặc phải đọc theo ghi chú này:**
> - **Số STV ngoài miền đã rút:** "lệch 20,5 ms trên CinC" và "0,13 ms khi cổng cho phép" (cùng 25,74–25,78 ms) tính trên
>   mẫu CinC 10 bản và mẫu 32 bản có a03 a04 a05 a08 là bản trùng dữ liệu huấn luyện (`README.vi.md` bảng rút lại).
>   Số STV dùng được duy nhất là +0,33 ms trong miền, n = 5 (`analysis/clinical_results.json → summary.ADFECGDB.stv_ba`).
>   Hai chỗ lời thoại cũ (mục 12–16 phút và câu hỏi 9) đã viết lại.
> - **Không dùng "khoảng cách 15 điểm".** Khoảng cách trong/ngoài miền trên 60 bản sạch: 23,28 (PSD) · 16,84 (gate) ·
>   16,55 (gate4) · 15,55 (peakprob, hậu kiểm) · 13,96 (trần) — `survey/facts_phase4.json → Z_DA_RUT.khoang_cach_trong_ngoai_mien_17_92.thay_bang`.
> - **0,934 [0,872; 0,981]** là cổng 22 ca, LOSO, chỉ tính trên 11/22 chủ thể có đoạn xấu, chỉ ở dạng phân tích, chưa có
>   trong demo (`analysis/gate22_results.json`). Đèn trong demo là cổng 5 ca, 0,721 [0,517; 0,898] trên 5 bản CinC sạch.
> - **Cổng không độc lập với mạng:** 12 chỉ số gồm 6 thuần tín hiệu, 4 tính trên nhịp mạng tìm ra, 2 là xác suất của mạng
>   (`fsqi/gate.py`); câu "12 chỉ số chất lượng tín hiệu cổ điển" trong tệp này đã sửa.
> - **82,01 không đứng một mình:** luôn kèm 74,28 (PSD) · 80,72 (gate, quy tắc kế hoạch chọn, trượt Holm 0,051) ·
>   81,01 (gate4, cũng ghi trước, qua Holm 0,015) · trần 83,60 (`analysis/dulieu_results.json → chon_kenh_60_sach.bang`).

Viết lại 12/09/2026 sau thẩm định vòng 7 (`docs/nhat_ky/THAMDINH_VONG7.md`). Mọi con số dưới đây truy về `survey/facts_phase4.json` (nguồn tổng hợp) hoặc tệp JSON ghi trong ngoặc. Không có con số nào tính trên 75 bản CinC. Lúc viết (12/09) tệp này vẫn còn số STV ngoài miền, về sau (17/09) cũng đã rút; các chỗ đó đã sửa theo cảnh báo ở trên.

Sổ tay (HTML): https://claude.ai/code/artifact/7f120fe6-e199-47b9-8aac-1a194c2d8b00
Hướng dẫn demo chi tiết: `docs/HUONG_DAN_DEMO.md`. Tờ tóm tắt in giấy: `docs/TOM_TAT_1_TRANG.md`.

**Kiểm trước buổi gặp (15 phút):** (1) mở sổ tay, rà mục 10 và 14 — nếu còn số CinC tính trên 75 bản hoặc số cổng từ chối zero-shot thì **không chiếu** hai mục đó, chỉ nói theo kịch bản này; (2) chạy `python -m pytest demo/test_core.py -q` (17 pass) và `python demo/run_check.py --only r01,a09,a02 --out demo_check_3ban --threads 2` để chắc máy chạy được; (3) bản nháp hội nghị 4 trang cũ trong `paper/` **không mang theo** — toàn số 75 bản, hội nghị năm nay đã diễn ra.

---

## 1. Mục tiêu buổi gặp — em muốn gì từ cô

Ba thứ, theo thứ tự ưu tiên:

1. **Dữ liệu có nhãn và một bác sĩ sản.** Đây là nút thắt duy nhất em không tự gỡ được: không có bộ công khai nào ngoài dữ liệu em đã dùng có nhãn nhịp thai thật (đã kiểm NIFEADB, NInFEA, nifecgdb, CinC set-b ngày 12/09 — `analysis/xacnhan_results.json`). Muốn nhân rộng kết quả phải tự chú thích có chuyên gia kiểm, hoặc xin ghi từ một khoa sản.
2. **Định hướng nơi công bố.** Đích thực tế của em là Physiological Measurement (Q2 Scimago 2024, sân nhà của cộng đồng điện tim thai) và hội nghị Computing in Cardiology 2027 (hạn dự kiến tháng 4/2027). Q1 (IEEE JBHI, BSPC) chỉ có cửa khi có dữ liệu mới ở mục 1. Xin cô cho ý kiến đích đó có hợp không.
3. **Đồng ý về cách kể.** Em định trình bày đề tài kèm những gì em đã rút lại, và định hỏi Đoàn trường về Euréka. Em muốn cô biết trước và cho ý kiến.

Thứ **không** phải mục tiêu buổi này: xin cô duyệt kết quả, xin cô sửa mã, xin thêm thời gian, xin cô ký bất cứ gì.

---

## 2. Dàn ý 20 phút theo phút

### 0–2 phút — Mở đầu

**Nói gì:**
> "Em chào cô. Em xin 20 phút, chia mấy phần, có demo ở giữa ạ. Cô ngắt bất cứ lúc nào cũng được ạ.
>
> Em làm hệ thống đọc điện tim thai từ **một** điện cực dán trên bụng mẹ, tìm từng nhịp tim của bé. Phần em coi là chính thì nằm ở chỗ khác: hệ thống tự biết khi nào nó không đáng tin. Lúc đó nó nói 'tôi không chắc', thay vì đưa ra một con số sai. Tên hệ thống là RelyFetal. Em huấn luyện trên 22 sản phụ, kiểm ngoài trên 60 bản ghi của một bộ khác. Mã khoảng 27.700 dòng Python với 82 kiểm thử tự động."

**Chiếu gì:** trang đầu sổ tay (ô số: 113.481 tham số · 22 sản phụ · 60 bản ghi kiểm ngoài · 82 kiểm thử).

**Không nói gì:** không tự khen ("tốt nhất hiện nay", "chưa ai làm", "đầu tiên"). Không nói "Q1" ở phút này.

### 2–6 phút — Vấn đề và ý tưởng

**Nói gì:**
> "Thai chậm phát triển là một nguyên nhân hàng đầu của thai lưu. Dấu hiệu sớm không phải nhịp nhanh hay chậm, mà là nhịp tim thai mất biến thiên tự nhiên. Muốn đo biến thiên phải biết từng nhịp rơi vào mili-giây nào.
>
> Hiện có hai cách. Siêu âm Doppler thì phổ biến, nhưng nó đo chuyển động van nên sai số thời điểm lớn. Điện cực da đầu thì chính xác nhưng xâm lấn, chỉ dùng khi đã chuyển dạ. Điện tim bụng mẹ là cách duy nhất vừa không xâm lấn vừa cho tín hiệu điện. Nhưng tín hiệu thai nhỏ hơn tim mẹ nhiều lần và trùng dải tần với cơ tử cung.
>
> Các nhóm khác dùng 4 đến 32 điện cực và tách nguồn. Em hỏi ngược lại hai câu. Một, nếu chỉ có một dây thì **mất bao nhiêu** so với bốn dây? Em nghĩ xa là miếng dán mẹ tự đeo ở nhà. Hai, hệ thống có **tự biết** lúc nào nó không nhìn thấy tín hiệu không? Câu thứ hai em nghĩ là quan trọng hơn với bác sĩ — nhưng em chưa gặp bác sĩ nào để hỏi, đó là điều em muốn xin cô."

**Chiếu gì:** bảng "Hai cách đo hiện có" và bảng "Thành phần tín hiệu" (sổ tay mục 02–03).

**Không nói gì:** không hứa "miếng dán" là sản phẩm — nói là tầm nhìn. Không nêu chỉ số STV như thứ đã đo được (để dành phần vấp).

### 6–12 phút — Phương pháp và kết quả, kèm demo 4 phút

**Nói gì (2 phút, trước demo):**
> "Đường ống có 5 bước. Bước một, lọc 10–60 Hz pha-không. Bước hai, khử điện tim mẹ bằng mẫu trung vị co giãn từng nhịp. Bước ba, chọn kênh mù nhãn. Bước bốn, một mạng tích chập thời gian nhỏ cho ra xác suất từng mẫu. Mạng này có 113 nghìn tham số, 0,48 MB, chạy 4,35 mili-giây cho mỗi cửa sổ 4 giây trên CPU. Bước năm, một cổng từ chối dùng 12 chỉ số: 6 thuần tín hiệu, 4 tính trên nhịp mạng tìm ra, 2 là xác suất của mạng — nên cổng không độc lập với mạng.
>
> Kết quả chính đo trên 22 sản phụ, F1 mức chủ thể, ghép ±50 mili-giây. Phương pháp mạnh nhất hiện có mà em chạy lại được là Power-MF. Nó dùng 4 kênh thì đạt 98,83; cắt xuống 1 kênh còn 86,71. Mạng 1 kênh của em đạt 97,56. Nói đúng thì em vẫn thua 4 kênh 1,27 điểm, khoảng tin cậy từ −3,08 đến +0,27. Mức đó chưa có ý nghĩa, nhưng em thắng 18 trên 22 bản. Bốn kênh đáng giá 12,12 điểm cho Power-MF; một kênh của em lấy lại 10,85. Tức là 89,5 %, khoảng tin cậy 81 đến 103 %. Em chạy lại Power-MF bằng Octave và đối chiếu với số tác giả công bố: 99,40 so với 99,46.
>
> Bộ CinC 2013 thì mô hình chưa từng thấy. Em loại 15 bản trùng với dữ liệu huấn luyện, còn 60 bản sạch. Trên 60 bản đó, quy tắc chọn kênh cũ (PSD) cho 74,28; quy tắc kế hoạch chọn (gate) cho 80,72; gate4, cũng ghi trước, cho 81,01; quy tắc mới chọn sau khi xem kết quả (peakprob) cho 82,01; trần chọn kênh nhìn đáp án là 83,60. Quy tắc mới hơn quy tắc cũ 7,73 điểm, khoảng tin cậy 3,82 đến 12,41. Em sẽ nói ở phần vấp vì sao con số này phải gọi là giả thuyết chứ chưa phải kết quả xác nhận. Giờ em cho cô xem nó chạy."

*(nguồn: `analysis/recovery_ratio.json`, `analysis/dulieu_results.json`)*

**Demo 4 phút — thao tác** (máy đã mở sẵn `python demo/app.py` với `PYTHONIOENCODING=utf-8`, trình duyệt ở http://127.0.0.1:7860, bản r01 đã tự phân tích xong, ô *Kênh bụng* = *Tự động — peakprob*, *Đèn tin cậy* = *Học*). Thứ tự theo `docs/HUONG_DAN_DEMO.md` mục 3, rút từ 5 bản xuống 3:

| Phút | Thao tác | Nói gì |
|---|---|---|
| 0:00–1:00 | Tab *Tín hiệu (5 tầng)*, bản **r01** (ADFECGDB, checkpoint fold chưa thấy r01). Chỉ tay theo 5 tầng từ trên xuống. Chỉ 4 thẻ số. | "Tầng trên là tín hiệu thô — các gai lớn là tim mẹ. Tầng hai đã lọc, vạch đỏ là đỉnh mẹ. Tầng ba là sau khi trừ mẹ — cái còn lại rất nhỏ, đó là tim bé. Tầng bốn là xác suất mô hình. Tầng năm là kết quả so với nhãn: chấm xanh đúng, đỏ báo thừa, cam bỏ sót. Bản này F1 99,92, xử lý cả 5 phút dưới 2 giây phần mô hình, khoảng 3 giây kể cả vẽ biểu đồ trên CPU. Đèn tin cậy xanh. Em nói rõ: đèn này hiệu chuẩn trên mô hình 5 ca cũ, cổng 22 ca em mới có kết quả phân tích, chưa đóng gói vào demo." |
| 1:00–2:15 | Đổi *Bản ghi minh hoạ* sang **a09** (CinC sạch) → *Phân tích* (~3 s kể cả vẽ biểu đồ). Mở tab *Chọn kênh — cả 4 kênh*. Đổi *Kênh bụng* sang *Tự động — PSD* → *Phân tích*. Đổi lại *peakprob*. | "Bộ khác, máy khác, chưa từng huấn luyện. Quy tắc mới chọn kênh 1 vì mô hình tự tin nhất ở đó — F1 94,25. Quy tắc cũ của Power-MF chọn kênh 2 theo phổ năng lượng — F1 chỉ 19,35, và đèn đỏ vì hơn nửa số nhịp trùng đỉnh mẹ. Đây là kiểu lỗi mà chọn kênh mới sửa được trên 19 trong 60 bản, hoà 35, thua 6, không bản nào mất quá 3,90 điểm." |
| 2:15–3:15 | Chọn **a02** → *Phân tích*. Chỉ thẻ *Đèn tin cậy* và tab *Nhịp tim thai + đèn đoạn*. | "Đây là phần em coi là quan trọng nhất. Bản này mô hình bám nhầm vào tàn dư tim mẹ, báo một chuỗi nhịp rất đều khoảng 130 nhịp/phút — trông như thai, F1 chỉ 24,91. Nhưng đèn đỏ: cổng thấy 78 % nhịp 'thai' trùng đỉnh mẹ trong khi ngẫu nhiên chỉ 13–22 %, nên hệ thống từ chối trả lời. Chọn kênh mới cũng **không** cứu được bản này — em cho cô xem cả chỗ nó thất bại." |
| 3:15–4:00 | Mở tab *Kết quả tổng hợp (60 bản sạch)* rồi tab *Nhật ký (JSON)*. Quay về sổ tay. | "Bảng này đọc trực tiếp từ tệp kết quả, không ghi cứng số nào trong mã, và có dòng cảnh báo hậu kiểm ngay trong bảng. Mọi thứ xuất ra JSON, gọi được qua API. Demo là bản mẫu nghiên cứu, không phải thiết bị y tế — em ghi câu đó ngay đầu trang." |

**Dự phòng nếu demo hỏng:** đủ 16 ảnh mới trong `demo/screenshots/` (01…12, `screenshots.json` ok: true, chụp 12/09 23:12). Mở ảnh theo đúng thứ tự demo: 01–03 (r01) → 04–06 (a09, hai quy tắc) → 07–08 (B2_03) → 09–10 (a02) → 11 (a27) → 12 (bảng tổng hợp 60 bản sạch). Nếu cần số: `demo/results/demo_check_showcase.json` (5 bản, đừng ghi đè).

**Chiếu gì:** demo; bảng 22 chủ thể (sổ tay mục 08); bảng 7 quy tắc chọn kênh trên 60 bản sạch (mục 09).

**Không nói gì:** bất kỳ số CinC nào tính trên 75 bản (kể cả số cổng từ chối zero-shot — đo trên 75 bản gồm 15 bản nhiễm, chưa tính lại); số Power-MF từ cổng chuyển hỏng; số dải lọc cũ; "một kênh thắng bốn kênh"; "em phát hiện" về rò rỉ; bất kỳ chữ khai báo trước nào mạnh hơn "khai báo trước phép tính" (từ tiếng Anh về đăng ký trước nghiên cứu cũng không).

### 12–16 phút — Những gì đã vấp và đã sửa

Kể **bốn** lần rút lại như điểm mạnh: em biết chính xác hệ thống làm được gì và không làm được gì.

**Nói gì:**
> "Phần này em nghĩ là thứ đáng nói nhất, vì nó cho thấy cách em làm việc.
>
> **Một, bộ kiểm tra có bản trùng với bộ huấn luyện.** Ban tổ chức CinC 2013 đã ghi điều này từ 2013. Silva 2013 Bảng 1 ghi 25 bản từ ADFECGDB. Clifford 2014 còn cảnh báo nguyên văn về một nhóm huấn luyện trên ADFECGDB rồi kiểm trên set-a. Em đã đọc, đã ghi vào ghi chú đọc bài, rồi vẫn bỏ sót khi làm. Khi đo lại, 15 trong 75 bản là bản sao nguyên văn. Tương quan chuẩn hoá đúng 1,0000, lệch nhịp 0,0 mili-giây. Mỗi bản huấn luyện xuất hiện đúng 3 lần, theo cửa sổ 0–60, 120–180, 240–300 giây. Phần em làm thêm là chỉ đúng 15 bản nào và đo mức thổi phồng: 3,27 đến 7,18 điểm F1. Em loại 15 bản, số chính rớt khoảng 5 điểm. Nhưng cải tiến chọn kênh trên dữ liệu sạch lại mạnh hơn số cũ. Em thấy yên tâm hơn vì số sạch lại cao hơn.
>
> **Hai, em chạy lại Power-MF bằng Octave** vì không có MATLAB. Lúc đầu nó cho kết quả thấp hơn tác giả vài điểm. Em đoán nguyên nhân trước khi đo, và đoán sai. Đo lại thì ra lỗi cổng chuyển của em — hàm tìm đỉnh của Octave tràn bộ nhớ. Sửa xong: 99,40 so với 99,46 tác giả công bố. Em rút kinh nghiệm là phải đo trước rồi mới nói.
>
> **Ba, quy tắc chọn kênh là chọn sau khi nhìn kết quả.** Em thử 7 quy tắc và ghi trước luật 'lấy quy tắc tốt nhất trong miền'. Luật đó chỉ vào quy tắc *gate*. Gate trên 60 bản sạch cho 80,72, trượt hiệu chỉnh Holm với p 0,051. *gate4* cũng ghi trước, cho 81,01 và qua Holm với p 0,015, nhưng không phải quy tắc kế hoạch chọn. Quy tắc thắng, *peakprob* 82,01 (PSD cũ 74,28, trần 83,60), là em chọn sau. Nó sống sót Holm trên cả họ 7 quy tắc với p 0,0039 và không có siêu tham số. Nên em vẫn báo cáo, nhưng gọi là giả thuyết mạnh chưa xác nhận. Em đã thử hai đường cứu. Một là tính lại trên thang logit ở 22 sản phụ — gate vẫn đứng đầu, peakprob hạng 3. Hai là tìm bộ thứ ba có nhãn để chạy đúng một lần, nhưng không có bộ công khai nào. Nên vấn đề hậu kiểm không biến mất. Cái này phải có dữ liệu mới mới giải được.
>
> **Bốn, em rút ba tuyên bố khác.** Dải lọc từng được ghi là cộng hơn mười điểm. Đo lại trên đúng mô hình thì chỉ +2,44 ở kênh PSD, khoảng tin cậy chạm 0. Lấy trung bình 4 kênh thì gần bằng 0. 'Đơn kênh hơn đa kênh' — sai, thua 1,27. Còn kết luận 'khoảng cách ngoài miền là do không có tín hiệu, không phải do mô hình' thì em rút. Lý do là phép thử em dùng để nói 'không nhìn thấy tín hiệu' có âm tính giả 18 %. Khoảng tin cậy từ 12 đến 25 %. Bốn phương pháp thích nghi miền đều thất bại — cái đó là sự thật đo được. Còn nguyên nhân khoảng cách giữa trong miền và ngoài miền — 23,28 điểm với quy tắc cũ, 15,55 với quy tắc hậu kiểm, 13,96 với trần — thì em chưa trả lời được.
>
> Chỉ số lâm sàng STV cũng vậy. Nó lệch 0,33 mili-giây trên dữ liệu trong miền, nhưng chỉ có 5 sản phụ. Số ngoài miền em từng nêu thì em đã rút, vì mẫu đo có bản trùng với dữ liệu huấn luyện. Nên em chưa có bằng chứng nó dùng được làm máy đo độc lập."

*(Ghi chú 17/09, không đọc: hai số STV ngoài miền cũ — lệch 20,5 ms trên CinC và 0,13 ms khi cổng cho phép — **đã rút**; xem cảnh báo đầu tệp.)*

*(nguồn: `analysis/DULIEU.md`, `baselines/powermf_published.json`, `analysis/xacnhan_results.json`, `analysis/clinical_results.json`)*

**Chiếu gì:** sổ tay mục 11 (Nhật ký sự cố) — bảng trùng lặp r01→a04,a05,a22…; bảng 7 quy tắc trên 60 bản sạch với cột p Holm.

**Không nói gì:** không đọc các con số đã rút thành tiếng (chỉ nói "số cũ"). Không nói "agent" hay "AI thẩm định" trừ khi cô hỏi cách làm việc — nếu hỏi thì nói thật: em dùng công cụ tự động đối chiếu từng con số với tệp gốc, và tự chịu trách nhiệm về từng số.

### 16–18 phút — Định vị thật và kế hoạch

**Nói gì:**
> "Đóng góp em định nộp không phải 'một máy dò tốt hơn', mà là ba thứ có ranh giới rõ. Thứ nhất là một phép đo: một kênh lấy lại 89,5 % lợi ích của bốn kênh, trên cùng bản ghi cùng bộ chấm. Thứ hai là một cổng từ chối không dùng nhãn. Nó được đánh giá bỏ-một-chủ-thể trên 22 sản phụ, AUROC trong bản ghi 0,934 tính trên 11/22 chủ thể có đoạn xấu — mới ở dạng phân tích, chưa có trong demo — xếp đúng ba bản khó nhất vào ba hạng chót. Thứ ba là một bản kiểm toán bộ chuẩn: 15 bản trùng, mức thổi phồng, và mọi số báo cáo trên 60 bản sạch. Quy tắc chọn kênh đi kèm như giả thuyết mạnh.
>
> Nơi nộp thực tế là **Physiological Measurement**. Tạp chí đó Q2 theo Scimago 2024, không phải Q1. Nhưng đó là nơi cộng đồng điện tim thai công bố, và chính CinC Challenge 2013 cũng ở đó. Chỗ thứ hai là **Computing in Cardiology 2027**, hạn dự kiến tháng 4/2027; kỳ 2026 đã diễn ra rồi, em không kịp. Q1 như IEEE JBHI chỉ có cửa nếu em có một bộ có nhãn mới để chạy quy tắc chọn kênh đúng một lần. Em ước cửa Q1 trong 6 tháng khoảng 15–20 %, không hơn.
>
> Ba tháng tới em làm ba việc. Một, chạy 3 hạt giống cho kết quả chính; hạt giống thứ hai đã có, 97,59 so với 97,56. Hai, tính lại số cổng từ chối trên 60 bản sạch. Ba, viết bản dài cho Physiological Measurement và bản 4 trang cho CinC 2027, đều trên 60 bản sạch. Có hai việc em quyết định **không** làm nữa, vì đã đo thấy đòn bẩy yếu. Một là đổi kiến trúc. Em thử 7 họ cùng tham số: ba họ đầu cách nhau dưới 0,1 điểm, họ kém nhất cách 3,1 điểm. Hai là thích nghi miền không giám sát: 4 phương pháp đều hỏng."

*(nguồn: `analysis/gate22_results.json`, `analysis/kientruc_results.json`, `adapt/adapt_results.json`)*

**Chiếu gì:** bảng "Còn thiếu gì" (sổ tay mục 13).

**Không nói gì:** không nói "chắc chắn Q1"; không nói Physiological Measurement là Q1; không nói "kiến trúc không quan trọng" tuyệt đối — nói "đòn bẩy yếu nhất đã đo".

### 18–20 phút — Xin hỗ trợ

**Nói gì:**
> "Em xin cô ba việc. **Một**, nếu cô quen khoa sản nào đang ghi CTG hoặc điện tim bụng, em xin gặp một bác sĩ 30 phút. Em cần biết bác sĩ cần chính xác bao nhiêu thì mới dùng được. Em cũng muốn hỏi xem có xin được dữ liệu có nhãn không. Hoặc nếu em tự chú thích 10–20 bản của một bộ công khai chưa có nhãn thì nhờ chuyên gia kiểm giúp. Không có việc này thì em không lên được Q1, và cũng không có gì để nói với hội đồng về nhu cầu thật.
>
> **Hai**, cô xem giúp Physiological Measurement và CinC 2027 có hợp không, hay cô thấy chỗ khác hợp hơn, và thứ tự nộp.
>
> **Ba**, về Euréka: kỳ 2026 đăng ký cấp thành từ 01 đến 25/9, nhưng hạn nội bộ TDTU em chưa tìm được thông báo nào — em sẽ hỏi Đoàn trường tuần này. Em nghĩ thực tế là kỳ 2027. Em xin cô ý kiến có nên đi, và có nên kể phần rút lại trước hội đồng sinh viên không.
>
> Em muốn số liệu chắc chứ không cần đẹp. Mọi con số trong tờ tóm tắt truy ngược được về một tệp trên máy. Em gửi cô kho mã ngay hôm nay."

**Chiếu gì:** tờ tóm tắt in giấy (`docs/TOM_TAT_1_TRANG.md`).

**Không nói gì:** không xin cô ký bất cứ thứ gì trong buổi đầu. Không hứa hạn Euréka khi chưa hỏi Đoàn trường.

---

## 3. Mười hai câu cô có thể hỏi, và câu trả lời mẫu

Từ dễ đến khó. Mỗi câu trả lời 2–4 câu, không hơn.

1. **"Em tóm tắt lại đề tài trong một phút được không?"**
   "Em đọc điện tim thai từ một điện cực trên bụng mẹ, tìm từng nhịp, và hệ thống tự chấm mức tin cậy để từ chối khi tín hiệu không đủ. Trên 22 sản phụ em đạt 97,56, còn phương pháp bốn kênh mạnh nhất em chạy lại được đạt 98,83. Chính phương pháp đó khi chỉ dùng một kênh thì em hơn 10,85 điểm. Trên 60 bản ghi chưa từng thấy em đạt 74,28 với quy tắc chọn kênh cũ, 80,72 với quy tắc kế hoạch chọn, 81,01 với gate4, 82,01 với quy tắc hậu kiểm. Cổng từ chối, đánh giá bỏ-một-chủ-thể, xếp đúng ba bản khó nhất vào ba hạng chót."

2. **"Vì sao chỉ một kênh, trong khi bệnh viện dùng nhiều kênh?"**
   "Vì mục tiêu xa là thiết bị mẹ tự đeo ở nhà, một dây mới đeo được. Câu hỏi khoa học em đặt là 'mất bao nhiêu khi bỏ ba kênh' — em đo được mất 1,27 điểm so với bốn kênh, tức lấy lại 89,5 %. Em không nói một kênh tốt hơn."

3. **"Dữ liệu lấy ở đâu, có nhãn không, bao nhiêu người?"**
   "Ba bộ công khai. ADFECGDB 5 sản phụ và Silesia 17 bản ghi, cộng lại 22 chủ thể dùng huấn luyện. Trong 17 bản Silesia có 7 bản B2 nhãn từ điện cực da đầu và 10 bản B1 nhãn gián tiếp. CinC 2013 set-a 75 bản ghi thì chỉ để kiểm tra. Nhưng 15 bản CinC là bản sao ADFECGDB — ban tổ chức đã ghi nhận từ 2013, em đo lại để biết đúng bản nào — nên em chỉ dùng 60 bản sạch. Điểm yếu em ghi rõ: 77 % thời lượng huấn luyện có nhãn gián tiếp từ Silesia B1."

4. **"So với phương pháp hiện có thì thắng hay thua?"**
   "Thua trung bình 1,27 điểm so với Power-MF bốn kênh, khoảng tin cậy từ −3,08 đến +0,27, p 0,156; thắng 18 trên 22 bản, trung vị +0,23. Bốn bản thua, trong đó ba bản lệch lớn, kéo trung bình xuống. So với Power-MF một kênh thì hơn 10,85, khoảng tin cậy 6,80 đến 15,40. Em chạy lại Power-MF trên máy mình và số khớp tác giả công bố trong 0,06 điểm nên so sánh là công bằng. Em chưa chạy lại DPSS — đối thủ thứ hai — đó là thiếu."

5. **"Mô hình nhỏ vậy có phải vì thiếu máy không?"**
   "Không ạ, là chủ đích. Nhân bốn lần tham số chỉ được cộng 0,26 điểm trong mẫu. 113 nghìn tham số, 0,48 MB, 4,35 mili-giây cho 4 giây tín hiệu trên CPU — đủ nhét vào vi điều khiển sau này. Em so 7 họ kiến trúc cùng tham số ±2,7 %, cùng hạt giống, giao thức rút gọn 3 epoch 3 fold. Ba họ đầu tương đương theo kiểm định tương đương, họ kém nhất cách 3 điểm (`analysis/kientruc_results.json`)."

6. **"Cổng từ chối hoạt động thế nào, nó sai thì sao?"**
   "Mỗi đoạn 4 giây em tính 12 chỉ số: 6 thuần tín hiệu, ví dụ entropy, độ nhọn, năng lượng dải thai; 4 tính trên nhịp mạng tìm ra, ví dụ tỉ lệ RR hợp lý; 2 là xác suất của mạng. Nên cổng không độc lập với mạng. Rồi em đưa chúng vào một bộ phân loại nhỏ, ra xác suất 'đoạn này xấu'. Không dùng nhãn lúc chạy. Trên 22 sản phụ, đánh giá bỏ-một-chủ-thể, AUROC trong bản ghi 0,934, khoảng tin cậy 0,872 đến 0,981, tính trên 11/22 chủ thể có đoạn xấu; cổng 22 ca này mới ở dạng phân tích, đèn trong demo là cổng 5 ca. Nó xếp đúng ba bản khó nhất vào ba hạng chót; ngẫu nhiên là 1 trên 1540. Nhưng 5 trong 24 quy tắc một đặc trưng đơn giản cũng xếp đúng ba bản đó, nên em không dám nói phải học mới làm được. Số cổng trên CinC em chưa tính lại trên 60 bản sạch nên em không đọc ra."

7. **"Rò rỉ dữ liệu là sao — em có chắc không? Người khác có bị không?"**
   "Ban tổ chức đã ghi từ 2013 rằng set-a có 25 bản từ ADFECGDB; cái em làm là đo để biết đúng bản nào. Em kiểm bằng tương quan chéo chuẩn hoá từng cặp, và so cả chuỗi khoảng nhịp tham chiếu. 15 bản cho tương quan đúng 1,0000, lệch 0,0 mili-giây, cả 4 kênh đúng thứ tự. Đối chứng dương là các bản cùng sản phụ đã biết, chỉ cho 0,86–0,98. 60 bản còn lại cao nhất 0,62. Hai cách cài đặt độc lập cho cùng kết quả. Về người khác: em đã rà 20 bài, 4 bài chắc chắn huấn luyện trên ADFECGDB và kiểm trên set-a, 2 bài nghi ngờ (`survey/RO_RI_VANLIEU.md`). Em sẽ nêu dè dặt trong bài, kèm trích dẫn Clifford 2014."

8. **"Quy tắc chọn kênh mới có phải em chọn sau khi nhìn kết quả không?"**
   "Dạ đúng, và em nói rõ trong bài. Luật ghi trước chỉ vào gate; gate 80,72 trượt Holm với p 0,051. gate4 cũng ghi trước, 81,01, qua Holm với p 0,015. peakprob 82,01 là chọn sau; quy tắc cũ PSD là 74,28. Em vẫn báo cáo vì nó sống sót Holm trên cả họ 7 quy tắc với p 0,0039 và không có siêu tham số. Em đã thử cứu bằng thang logit trên 22 sản phụ — gate vẫn đứng đầu, peakprob hạng 3 — nên không cứu được. Bước tiếp theo duy nhất là chạy đúng một lần trên một bộ có nhãn mới, mà không có bộ công khai nào; đó là lý do em xin cô mục dữ liệu."

9. **"Có ý nghĩa lâm sàng chưa? Bác sĩ dùng được gì?"**
   "Chưa, và em phải nói thẳng. Chỉ số STV em đo lệch 0,33 mili-giây trên dữ liệu trong miền, nhưng chỉ 5 sản phụ; số ngoài miền em từng nêu đã rút vì mẫu có bản trùng dữ liệu huấn luyện — nên chưa dùng được làm máy đo độc lập. *(Không đọc: 20,5 ms và 0,13 ms là số STV ngoài miền đã rút.)* Còn 'bác sĩ cần chính xác bao nhiêu' là câu em muốn hỏi cô, vì em chưa gặp bác sĩ nào."

10. **"22 chủ thể có đủ để kết luận không?"**
    "Không đủ cho kết luận mạnh. Em tự tính công suất thống kê thì cần khoảng 50. Với 5 sản phụ ADFECGDB, p nhỏ nhất Wilcoxon có thể cho là 0,0625 nên không bao giờ có p dưới 0,05. Em làm mọi thống kê ở mức chủ thể với cluster bootstrap, và 5 kết luận cũ bị đảo khi làm đúng. Vì vậy dữ liệu trung tâm thứ hai là việc em cần cô giúp nhất."

11. **"Em định nộp ở đâu, khi nào? Q1 có thực tế không?"**
    "Đích thực tế là Physiological Measurement — Q2 Scimago 2024, nhưng là nơi cộng đồng điện tim thai công bố — nộp khoảng đầu tháng 12, và CinC 2027 hạn dự kiến tháng 4. Q1 như IEEE JBHI thì em ước 15–20 % trong 6 tháng. Phản biện sẽ hỏi đúng chỗ em không trả lời được: quy tắc chọn kênh chọn hậu kiểm trên bộ kiểm duy nhất. Có dữ liệu có nhãn mới thì cửa Q1 mở ra khoảng một phần ba trong 12 tháng. Nếu cô thấy nên nhắm chỗ khác, em nghe cô."

12. **"Ba tháng tới em làm gì tiếp, và em cần gì ở cô?"**
    "Ba việc rẻ: 3 hạt giống cho kết quả chính; tính lại số cổng từ chối trên 60 bản sạch; viết bản Physiological Measurement và bản 4 trang CinC 2027. Hai việc em dừng vì đã đo thấy vô ích: đổi kiến trúc và thích nghi miền không giám sát. Ở cô em xin: một đầu mối bác sĩ sản để xin dữ liệu hoặc nhờ kiểm nhãn, ý kiến về nơi nộp, và ý kiến có nên đi Euréka 2027."

---

## 4. Ba điểm rút lui khi bị hỏi dồn

1. **Cô hỏi một sự thật lâm sàng em không biết** (ngưỡng STV bất thường theo hướng dẫn nào, tuần thai nào đo được, CTG hiện dùng thang gì):
   > "Em chưa biết, và em chưa hỏi bác sĩ nào — đó chính là điều em muốn xin cô giới thiệu. Em ghi lại câu hỏi và trả lời cô bằng nguồn cụ thể sau."
   Không đoán, không trích số nhớ mang máng.

2. **Cô hỏi một con số em không nhớ chính xác** (khoảng tin cậy của một quy tắc phụ, số đoạn xấu trong tập huấn luyện cổng, số bản F1 dưới 50 của từng quy tắc):
   > "Em không nhớ chính xác để nói ra. Mọi số nằm trong tệp kết quả trên máy — em mở ngay được nếu cô muốn, hoặc gửi cô sau, chứ em không đoán."
   Rồi mở đúng tệp (`survey/facts_phase4.json` là nơi tra nhanh nhất; sau đó `analysis/dulieu_results.json`, `analysis/gate22_results.json`, `analysis/xacnhan_results.json`).

3. **Cô hỏi về một phương pháp em chưa thử** ("sao không dùng Transformer / học tự giám sát / dữ liệu tổng hợp / DANN, CORAL?"):
   > "Em chưa thử cái đó. Em ghi lại làm việc tiếp. Nếu cô hỏi em đoán, thì em đoán là … Nhưng đó là phỏng đoán, không phải kết quả. Em đã đoán sai một lần với Power-MF nên em không tin phỏng đoán của mình lắm."
   Nếu là kiến trúc: nói thêm "em đã đo 7 họ cùng tham số và thấy đòn bẩy kiến trúc yếu, nên em sẽ chỉ thử nếu cô thấy có lý do đặc biệt". Nếu là thích nghi miền: "em đã thử 4 phương pháp không giám sát và cả 4 đều hỏng; DANN hay CORAL em chưa thử, và em không có lý do cơ chế để tin chúng khác đi."

Quy tắc chung: câu nào bắt đầu bằng "em nghĩ" thì phải kết thúc bằng "nhưng chưa đo". Câu nào về rò rỉ thì mở đầu bằng "ban tổ chức đã ghi nhận", không mở đầu bằng "em phát hiện".

---

## 5. Danh sách mang theo

| Thứ | Trạng thái cần | Ghi chú |
|---|---|---|
| Sổ tay HTML | Mở sẵn trên trình duyệt: https://claude.ai/code/artifact/7f120fe6-e199-47b9-8aac-1a194c2d8b00 | Đã rà mục 10 và 14 trước buổi gặp; mục nào còn số 75 bản thì không chiếu |
| Demo | `python demo/app.py` chạy trước 10 phút với `PYTHONIOENCODING=utf-8`; r01 đã tự phân tích xong; tab thứ hai mở sẵn `demo/screenshots/` | Kiểm `pip install gradio plotly`; checkpoint `model/checkpoints/fetalqrs_tcn_22_production.pt` và `fetalqrs_tcn_22_fold_01..11.pt` có mặt; chạy `run_check.py --only r01,a09,a02` trước để chắc số khớp mục 6 hướng dẫn demo. Không cần mạng. |
| Ảnh dự phòng | đủ 16 ảnh `01…16` trong `demo/screenshots/` (`screenshots.json` ok: true) | Không cần chụp tay. Mở theo thứ tự 01 → 04 → 07 → 09 → 11 → 12 nếu demo hỏng |
| 1 trang tóm tắt in giấy | 2 bản (1 cho cô, 1 cho mình) | `docs/TOM_TAT_1_TRANG.md` |
| Kho mã | Link GitHub sẵn trong tin nhắn nháp | https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027 — commit mới nhất: xem `git log -1` |
| Tệp tra số | `survey/facts_phase4.json` mở sẵn trong trình soạn thảo | Khi cô hỏi số em không nhớ |
| Sổ ghi câu hỏi | Giấy hoặc tệp trống | Ghi từng câu cô hỏi mà mình chưa trả lời được — đầu vào cho email cảm ơn |
| **Không mang** | Bản nháp hội nghị 4 trang cũ trong `paper/` và PDF in từ nó | Toàn số 75 bản; hội nghị 2026 đã diễn ra. Nếu cô hỏi về bản hội nghị: "em sẽ viết lại trên 60 bản sạch cho CinC 2027, hạn tháng 4" |

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
> - [Ý 2 — ý kiến của cô về nơi nộp: Physiological Measurement / CinC 2027 / nơi khác, và thứ tự]
> - [Ý 3 — cô nói gì về việc kể phần rút lại, và về Euréka 2027]
> - [Ý 4 — câu hỏi cô đặt mà em chưa trả lời được; em sẽ trả lời bằng nguồn trước ngày …]
> - [Ý 5 — mốc hẹn lần sau]
>
> Ba việc em xin cô, khi nào cô tiện:
>
> 1. Giới thiệu giúp em một bác sĩ sản hoặc khoa sản đang ghi CTG / điện tim bụng, để em xin phỏng vấn 30 phút. Em cũng muốn hỏi khả năng xin dữ liệu có nhãn. Hoặc nhờ chuyên gia kiểm nhãn nếu em tự chú thích một bộ công khai.
> 2. Cô xem giúp tờ tóm tắt 1 trang (đính kèm) — em chỉ cần nhận xét về cách đặt đóng góp và mức độ thận trọng của phát biểu. Bản dài cho Physiological Measurement em sẽ gửi cô đọc trước khi nộp (dự kiến đầu tháng 12).
> 3. Cho em biết cô có đồng ý đứng tên hướng dẫn hồ sơ Euréka 2027 lĩnh vực Công nghệ thông tin không, để em hỏi Đoàn trường quy trình sơ tuyển. Em cũng sẽ hỏi Đoàn trường xem hạn nội bộ kỳ 2026 còn không và báo cô.
>
> Kho mã và sổ tay: https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027 · https://claude.ai/code/artifact/7f120fe6-e199-47b9-8aac-1a194c2d8b00. Mọi con số trong đó truy ngược được về tệp kết quả trên đĩa (`survey/facts_phase4.json`).
>
> Em cảm ơn cô.
> Ngô Bình Minh — [lớp, khoa, số điện thoại]

### Việc làm ngay sau buổi

- Ghi vào `docs/` một tệp `NHAT_KY_GAP_GVHD.md`: ngày, người dự, 5 ý trên, việc được giao, hạn.
- Trả lời từng câu "em chưa biết" bằng nguồn trong vòng 3 ngày.
- Hỏi Đoàn trường / Phòng QLKH TDTU về Euréka (hạn 2026 còn không; quy trình sơ tuyển 2027) — xem `docs/EUREKA.md` mục 4 và 4b.
- Nếu cô đồng ý giới thiệu bác sĩ: soạn sẵn 5 câu hỏi phỏng vấn (ngưỡng chính xác cần, thang STV đang dùng, tuần thai, số kênh chấp nhận được, có sẵn ghi bụng có tham chiếu không).
