# Thẩm định vòng 10 — Kịch bản thuyết trình v2 nhìn từ ghế giảng viên nghe lần đầu

**Ngày:** 17/09/2026 · **Commit tham chiếu:** b158507 + thay đổi chưa commit · **Tài liệu thẩm định:** `docs/KICH_BAN_THUYET_TRINH_v2.md` (đọc tuần tự mục 1 → 14 → Phụ lục A–D), kèm `docs/BOI_CANH_1_KENH.md`, `docs/CONG_BANG_DOI_CHUAN.md`, `docs/TOM_TAT_30_BAI.md`.
**Vai:** giảng viên hướng dẫn giỏi y sinh, không chuyên xử lý tín hiệu, lần đầu nghe đề tài.
**Nguyên tắc:** không sửa tệp nào; mọi số dưới đây mở từ tệp trên đĩa. Quy ước [SỰ KIỆN] / [SUY LUẬN] / [KHUYẾN NGHỊ] như kịch bản.

---

## 0. Bốn lỗi sự thật phải sửa TRƯỚC khi lo chuyện dễ hiểu

Trong lúc kiểm các chỗ khó hiểu, tôi mở tệp nguồn và thấy bốn câu trong kịch bản không khớp đĩa. Cả bốn đều nằm đúng chỗ giảng viên sẽ hỏi.

| # | Câu trong kịch bản | Đĩa nói gì [SỰ KIỆN] | Mức |
|---|---|---|---|
| S1 | Mục 5: "Mười hai chỉ số chất lượng tín hiệu cổ điển, **không lấy từ mạng**. Vì sao: để cổng không sụp cùng lúc với mạng." | `fsqi/gate.py` dòng 67–76: 12 đặc trưng = 10 khoá `CLASSICAL_KEYS` + `peak_prob_mean` + `prob_max`, **hai khoá là xác suất đầu ra của mạng**. Các khoá `rr_cv`, `rr_plaus`, `n_det`, `bsqi` tính trên **nhịp mạng tìm ra** (`det_rel`). Độ quan trọng hoán vị (`analysis/gate22_results.json → cong.permutation_importance_delta_auroc`): `rr_cv` 0,140 và `peak_prob_mean` 0,032 là hai đặc trưng lớn nhất; tám đặc trưng thuần tín hiệu đều dưới 0,002. | **Nặng.** Câu "không sụp cùng lúc với mạng" không đứng được. |
| S2 | Mục 11 + Mục 13 + `HUONG_DAN_DEMO_v2.md` mục 4: đèn trong demo được bảo chứng bằng "AUROC trong bản ghi 0,934, bỏ-một-chủ-thể trên 22 sản phụ". | `analysis/GATE22.md` dòng 364–366: cổng 22 ca **chỉ tồn tại dưới dạng phân tích**; demo vẫn dùng **cổng cũ** `fsqi/gate_classical.pkl` huấn luyện trên mô hình 5 ca, AUROC trong bản ghi của cổng cũ là **0,721 [0,517; 0,898]** (GATE22.md dòng 70–71). Thêm nữa, 0,934 là trung bình trên **11/22** chủ thể (11 chủ thể còn lại không có đoạn xấu nào) — GATE22.md dòng 66, 72. | **Nặng.** Số đang bảo chứng cho một cổng khác cổng đang chiếu. |
| S3 | Mục 13, thẻ a02 bước 4: "Dây nào cũng vậy, không dây nào cứu được." | `analysis/chonkenh_results.json → F1_tung_ban_ghi.cinc.a02`: dây 1 (`lead0`) F1 **75,88** = oracle; dây được chọn (dây 2) **24,91**; trung bình 4 dây 36,29, dây tệ nhất 19,86. Cả **sáu** quy tắc mù nhãn (psd, gate, gate4, rrcv, peakprob, rrplaus) đều chọn dây 2 (`chon_kenh_theo_quy_tac.cinc.a02`). Bước 4 của demo hiện cột F1 từng dây, nên giảng viên **nhìn thấy** 75,9. | **Nặng.** Lời thoại mâu thuẫn trực tiếp với hình đang chiếu. |
| S4 | Mục 1 [NẾU CÓ HỎI]: "Trong miền lệch 0,33 ms, **ngoài miền lệch 20,50**." | `analysis/clinical_results.json`: CinC2013 `n_records` 10 = **a01…a10**, chứa **a03 a04 a05 a08** (4 bản nhiễm). F1 của chính mẫu này (69,31) nằm trong `Z_DA_RUT.cinc_mau_10`. Số 20,50 ms đi cùng một mẫu đã rút. | Trung bình. Không được đọc như số ngoài miền. |

Lỗi nhỏ đi kèm:

* **S5.** Khoảng cách trong/ngoài miền được nói ba cỡ khác nhau: Mục 8 "mất 15 đến 23 điểm", Mục 11 "gần 18 điểm" (17,92), `HANDOFF.md` mục 11 "15 điểm". Người nghe sẽ hỏi con số nào đúng. Chọn một (17,92, có nguồn) và giải thích 15–23 là khoảng giữa các quy tắc chọn kênh, nếu đúng như thế.
* **S6.** Mục 4 và Mục 10 chỉ nêu 74,28 và 82,01 (hậu kiểm), bỏ **gate4 81,01** — trái `HANDOFF.md` §8.3 "luôn báo cả ba". Thẻ a09 trong demo cũng chỉ nêu 82,01 và 74,28.
* **S7.** Slide 1 và mục "Kiểm 15 phút" ghi **82 kiểm thử**; vòng 10 đã lên **89** (`demo/test_core.py`). Chạy pytest trước buổi sẽ ra số khác slide.
* **S8.** `docs/TOM_TAT_30_BAI.md` hướng 5 viết "set-a chứa **25** bản ADFECGDB" rồi "nhóm định danh **15** bản". Giảng viên đọc tờ phát tay sẽ hỏi "25 hay 15?". Kịch bản không có câu trả lời.

---

## 1. Nghe xong tôi CÒN KHÔNG HIỂU gì

Mỗi mục: khái niệm → cách giải thích bằng lời thường (2–3 câu) → ví dụ đời thường.

| # | Mục xuất hiện đầu tiên | Khái niệm | Giải thích đề xuất | Ví dụ đời thường |
|---|---|---|---|---|
| 1 | Mục 2 ("rơi 12,12 điểm") — chưa nói điểm của cái gì; F1 chính thức xuất hiện Mục 3 nhưng không được định nghĩa | **F1, vì sao không dùng accuracy** | Máy làm hai kiểu sai: bỏ sót nhịp có thật, và báo nhịp không có. F1 gộp hai kiểu sai này thành một số từ 0 đến 100. Không dùng accuracy vì phần lớn thời gian là "không có nhịp": một máy im lặng suốt cũng đúng tới hơn 90 % số mili-giây mà không tìm được nhịp nào. | Điểm danh lớp 40 người. Accuracy kiểu "đúng bao nhiêu ghế trống" thì cao vô nghĩa. F1 hỏi: gọi đủ người có mặt chưa, và có gọi nhầm tên người vắng không. |
| 2 | Mục 1 chú thích; Mục 3 lời thoại | **±50 ms, vì sao 50** | Một nhịp máy báo được tính là đúng nếu nằm trong 50 phần nghìn giây quanh nhịp thật. 50 là quy ước của Behar 2014 và Andreotti 2016 để các bài so được với nhau, không phải ngưỡng lâm sàng. Với nhịp thai 140 lần/phút, hai nhịp cách nhau khoảng 430 ms, nên 50 ms là khoảng một phần chín quãng giữa hai nhịp: đủ chặt để không nhầm sang nhịp bên cạnh. | Bấm giờ chạy 100 m: về đích lệch 0,05 giây vẫn tính là "đúng vạch", nhưng lệch nửa giây là đã sang người khác. |
| 3 | Mục 3 ("22 chủ thể"), Mục 10 ("thống kê mức chủ thể") | **Mức chủ thể vs mức bản ghi** | Một sản phụ đeo bốn điện cực cho bốn bản ghi, nhưng bốn bản đó giống nhau vì cùng một người. Đếm thành bốn mẫu là tự nhân bản bằng chứng. Nên em tính một điểm cho mỗi sản phụ, rồi mới lấy trung bình. | Hỏi ý kiến 22 gia đình về một món ăn, không được đếm mỗi thành viên trong nhà là một phiếu độc lập, vì cả nhà ăn cùng nồi. |
| 4 | Mục 2 chú thích, Mục 3 lời thoại | **KTC 95 % đọc thế nào** | Khoảng tin cậy là vùng mà giá trị thật có lẽ nằm trong, sau khi tính đến chuyện chỉ có 22 người. "−1,27 [−3,08; +0,27]" nghĩa là: ước lượng là thua 1,27, nhưng thật sự có thể thua tới 3 hoặc hơn nhẹ 0,27. Khoảng chứa số 0 thì chưa khẳng định được là có khác biệt. | Cân một bao gạo trên cân cũ: đọc ra 10 kg, nhưng cân lệch nửa ký. Nói "9,5 đến 10,5 kg" trung thực hơn "10 kg". Nếu khoảng đó chứa cả con số người bán ghi thì chưa thể tố họ cân gian. |
| 5 | Mục 6 (trước khi Mục 11 nêu bảng) | **Holm là gì, vì sao cần** | Em thử bảy quy tắc cùng lúc. Thử càng nhiều thì càng dễ có một cái "thắng" nhờ may. Holm là cách siết ngưỡng khi thử nhiều thứ: cái đầu phải qua ngưỡng chặt nhất, rồi nới dần. p sau hiệu chỉnh dưới 0,05 mới được gọi là thắng. | Mua bảy tờ vé số, trúng một tờ giải nhỏ thì chưa chứng minh mình giỏi chọn số. Muốn nói giỏi, tờ trúng phải trúng giải lớn hơn hẳn so với khi chỉ mua một tờ. |
| 6 | Mục 6 nêu tên, Mục 11 nêu số, **không mục nào định nghĩa** | **gate / gate4 / peakprob khác nhau chỗ nào** | Cả ba đều chọn một trong bốn dây mà không nhìn đáp án. `gate` hỏi cổng từ chối "dây nào ít đoạn xấu nhất", với cổng học trên một dây. `gate4` hỏi cùng câu đó nhưng cổng học trên cả bốn dây. `peakprob` không dùng cổng: chọn dây mà mạng tự tin nhất tại các nhịp nó tìm thấy. Hai cái đầu ghi trước khi chấm; cái thứ ba nghĩ ra sau khi đã thấy điểm. | Chọn một trong bốn ứng viên. `gate`: hỏi một người phỏng vấn đã quen một kiểu hồ sơ. `gate4`: hỏi người phỏng vấn đã xem đủ bốn kiểu hồ sơ. `peakprob`: chọn người tự tin nhất khi trả lời. |
| 7 | Mục 4 ("82,01 quy tắc hậu kiểm") — trước khi giải thích ở Mục 6 | **Hậu kiểm, vì sao làm yếu kết quả** | Hậu kiểm là quy tắc được chọn sau khi đã nhìn điểm của tất cả quy tắc trên chính tập kiểm. Khi đã nhìn đáp án rồi mới chọn, con số tốt có thể một phần nhờ may của đúng 60 bản này. Nên nó là giả thuyết cần kiểm lại trên dữ liệu mới, chưa phải kết quả. | Bắn tên vào tường rồi mới vẽ bia quanh mũi tên: trúng hồng tâm, nhưng không ai tin đó là tài thiện xạ. |
| 8 | Mục 2 lời thoại, Mục 3 | **89,49 % là tỉ lệ của cái gì** | Bốn dây giúp Power-MF thêm 12,12 điểm so với chính nó chạy một dây. Mạng một dây của em đứng cao hơn Power-MF một dây 10,85 điểm. 10,85 chia 12,12 là 89,49 %: em bù lại được chín phần mười cái lợi của việc có thêm ba dây. Nó không nói gì về chuyện một dây bằng bốn dây. | Xe bốn bánh chở 12 bao, xe ba bánh cùng hãng chở 0 bao thêm. Xe ba bánh cải tiến chở thêm được gần 11 trong số 12 bao chênh lệch đó. |
| 9 | Mục 10 ("chọn kênh oracle thổi phồng số") — số 83,60 xuất hiện Mục 11 | **Oracle** | Oracle là "gian lận có chủ đích để lấy trần": nhìn đáp án rồi chọn dây tốt nhất cho từng bản. Không thiết bị nào làm được vậy. Nó cho biết nếu chọn dây hoàn hảo thì được bao nhiêu, để đo quy tắc thật còn cách trần bao xa. | Chấm điểm bài thi với đáp án trong tay: ra điểm tối đa có thể, không phải điểm thật của học sinh. |
| 10 | Mục 1 [NẾU CÓ HỎI] ("trong miền lệch 0,33") — trước khi Mục 4 và 8 dùng tiếp | **Trong miền vs ngoài miền** | Trong miền: dữ liệu giống lúc huấn luyện (cùng loại máy, cùng bệnh viện, cùng kiểu sản phụ), nhưng khác người. Ngoài miền: máy ghi khác, nơi khác, cách đặt điện cực khác. Mô hình thường tụt khi ra ngoài miền, và ở đây tụt gần 18 điểm. | Học lái xe ở sân tập của trường (trong miền) rồi lần đầu chạy ngoài phố giờ cao điểm (ngoài miền). Cùng kỹ năng, kết quả khác hẳn. |
| 11 | Mục 5 ("mạng tích chập thời gian giãn nở"), Mục 7 ("trường tiếp nhận") | **TCN / trường tiếp nhận** | TCN là kiểu mạng đọc tín hiệu theo thời gian, mỗi lớp nhìn xa hơn lớp trước theo cấp số. Trường tiếp nhận là đoạn tín hiệu mà mạng được nhìn khi quyết định tại một thời điểm: ở đây 1,5 giây, tức khoảng ba đến bốn nhịp thai. Mạng nhìn 60 ms thì chỉ thấy một mẩu của một nhịp, nên dễ nhầm nhiễu thành nhịp. | Đọc một từ trong câu: chỉ nhìn một chữ cái thì khó đoán; nhìn cả câu thì đoán gần đúng. Nhìn thêm cả trang sách thì không giúp gì hơn nữa (bão hoà ở 1,5 giây). |
| 12 | Mục 1 ("máy có tự biết lúc nào không nên trả lời"), Mục 5 bước năm | **Cổng từ chối học từ đâu** | Em cắt tín hiệu thành đoạn 4 giây. Đoạn nào mạng chấm F1 dưới 80 thì dán nhãn "xấu" (5,40 % số đoạn). Rồi em cho một bộ phân loại học từ 12 chỉ số của đoạn để đoán đoạn nào xấu mà **không** cần đáp án. Phải nói thật: vài chỉ số trong đó lấy từ chính mạng (xem S1). | Giáo viên chấm lại 100 bài cũ, đánh dấu bài làm ẩu, rồi rút ra dấu hiệu "chữ nguệch ngoạc, gạch xoá nhiều" để lần sau nhìn qua là biết bài nào cần chấm kỹ. |
| 13 | Mục 3 lời thoại | **p 0,156** | Nếu thật ra hai hệ ngang nhau, thì chênh lệch cỡ này vẫn xuất hiện khoảng 16 lần trong 100 lần lặp lại nghiên cứu, chỉ do may rủi chọn người. 16 % là quá thường để kết luận có khác biệt. | Tung đồng xu 6 lần ra 4 ngửa: chưa đủ để nói đồng xu lệch. |
| 14 | Mục 11 ("diện tích dưới đường cong trong bản ghi 0,934") | **AUROC, "trong bản ghi"** | Lấy ngẫu nhiên một đoạn xấu và một đoạn tốt **trong cùng một bản ghi**. AUROC 0,934 nghĩa là cổng xếp đoạn xấu là đáng ngờ hơn trong khoảng 93 lần trên 100. 0,5 là tung đồng xu, 1,0 là hoàn hảo. "Trong bản ghi" khó hơn "gộp" vì không được lợi dụng chuyện có bản ghi tệ toàn bộ. | Bác sĩ nhìn hai phim X-quang của **cùng** một bệnh nhân, đoán phim nào có tổn thương: khó hơn so sánh phim người khoẻ với phim người bệnh nặng. |
| 15 | Mục 6, Mục 12 ("15 bản", "thổi phồng 3,27–7,18") + tờ phát tay ghi "25 bản" | **Chồng lấn: 25 hay 15, thổi phồng nghĩa là gì** | Ban tổ chức 2013 ghi một số bản của bộ kiểm có nguồn gốc từ bộ huấn luyện của em. Em đo từng cặp và thấy đúng 15 bản là bản sao y nguyên. Chấm trên bản sao thì máy "đã thấy đề", nên điểm cao hơn thật 3,27 đến 7,18. Phần chênh 25 và 15 cần một câu giải thích có nguồn (S8). | Cho học sinh thi lại đúng đề đã luyện: điểm cao hơn năng lực thật. |
| 16 | Mục 8 ("nhãn gián tiếp") | **Nhãn trực tiếp vs gián tiếp** | Nhãn trực tiếp: nhịp lấy từ điện cực gắn trên da đầu bé, đo tận nơi. Nhãn gián tiếp: nhịp do người hoặc thuật toán đánh dấu trên chính tín hiệu bụng, nên có thể lệch vài mili-giây theo quy luật. | Đo nhiệt độ bằng nhiệt kế kẹp nách (trực tiếp) so với sờ trán đoán (gián tiếp). |
| 17 | Mục 5 ("khử tim mẹ bằng mẫu trung vị") | **Khử tim mẹ** | Tim mẹ mạnh hơn tim bé nhiều lần. Em lấy trung bình hình dạng một nhịp mẹ, rồi trừ nó ra khỏi từng nhịp mẹ. Phần còn lại mới là chỗ tìm tim bé. | Ghi âm tiếng thì thầm trong phòng có quạt trần: thu riêng tiếng quạt rồi trừ đi, còn lại tiếng thì thầm. |

---

## 2. Mục THIẾU HOÀN TOÀN

| # | Tên | Vì sao cần | Nội dung đề xuất | Đặt ở đâu |
|---|---|---|---|---|
| M1 | **Sơ đồ hệ thống tổng thể, từ điện cực đến kết quả** | Mục 5 kể năm bước bằng lời, người không chuyên không giữ được năm ô trong đầu. Không chỗ nào nói **đầu vào là gì** (1 phút / 5 phút, 1 kHz, bao nhiêu dây) và **đầu ra là gì** (dãy thời điểm nhịp, nhịp tim trung bình mỗi 4 s, đèn ba màu, đoạn bị từ chối). | Một hình ngang: điện cực bụng → lọc 10–60 Hz → khử mẹ → chọn dây → TCN → dãy nhịp → nhịp tim theo thời gian + đèn xanh/vàng/đỏ. Dưới mỗi ô ghi **đầu ra trung gian nhìn thấy được** và **thời gian**. Ghi rõ ô nào dùng xác suất của mạng (chọn dây `peakprob`, cổng) để khỏi lặp S1. | Ngay sau Mục 2, trước mọi con số. |
| M2 | **Người dùng cuối và tình huống dùng** | Mục 2 nói "miếng dán mẹ tự dùng ở nhà", nhưng không nói **ai đọc kết quả**, **đọc khi nào**, **làm gì với nó**. Không có câu này thì "97,56" không có nghĩa với ai. | Viết rõ đây là **kịch bản giả định** [GIẢ THUYẾT]: sản phụ thai chậm phát triển, tuần 28–36, theo dõi tại nhà giữa hai lần khám; dữ liệu gửi về bác sĩ; đèn đỏ = đi khám lại hoặc làm CTG, không phải chẩn đoán. Nói thẳng: chưa gặp bác sĩ nào để kiểm kịch bản này (Mục 1 đã có ranh giới, cần kéo sang đây). | Mục 1, sau câu hai câu hỏi. |
| M3 | **Ý nghĩa lâm sàng của từng con số** | Người nghe y sinh nghĩ theo "sai bao nhiêu nhịp mỗi phút" và "bỏ sót ca nguy hiểm bao nhiêu". Kịch bản chỉ có F1. | Quy đổi xấp xỉ (xem mục 4 báo cáo này): F1 97,56 ≈ 2–3 nhịp lỗi trên 100, tức khoảng 3–4 nhịp lỗi mỗi phút ở 140 lần/phút (giả định sót và dư ngang nhau — phải nói là xấp xỉ). Kèm câu **chưa đo**: sai số này ảnh hưởng chỉ số biến thiên bao nhiêu ngoài miền (số 20,50 ms không dùng được, S4). | Một hộp "con số này nghĩa là gì" dưới bảng Mục 3 và bảng Mục 11. |
| M4 | **Khi hệ thống sai thì chuyện gì xảy ra** | Có câu hỏi "đèn xanh có sai không" ở Mục 13, nhưng không có phân tích hai chiều sai và hậu quả. | Bảng 2×2: đèn xanh + đúng / đèn xanh + sai (nguy hiểm nhất: 3 bản chế độ học, thấp nhất a57 F1 17,02 — `facts_phase4.json → F_demo`) / đèn đỏ + sai (0 bản F1 ≥ 95: chỉ tốn một lần khám thừa) / đèn đỏ + đúng. Nêu nguyên tắc thiết kế: sai theo hướng từ chối rẻ hơn sai theo hướng trả số đẹp. Và nêu chế độ lỗi a02: nhịp mẹ bị báo là nhịp thai. | Sau Mục 11, trước demo. |
| M5 | **So với CTG đang dùng ở bệnh viện Việt Nam** | Giảng viên y sinh biết CTG/NST. Mục 1 nói "Doppler" nhưng không gọi tên CTG, không nói CTG đã tính biến thiên ngắn hạn theo Dawes–Redman trên đoạn 3,75 giây. Câu hỏi "vậy điện tim bụng thêm được gì" chắc chắn đến. | Bảng ba cột: CTG Doppler (có sẵn, cần người đặt đầu dò, mất tín hiệu khi mẹ béo/thai cử động, nhịp theo cửa sổ), điện tim da đầu (chuẩn vàng, xâm lấn), điện tim bụng (không xâm lấn, cho từng nhịp, **chưa có kiểm chứng lâm sàng**). Chỉ nêu điều có nguồn; phần "ưu điểm lâm sàng" ghi [GIẢ THUYẾT]. Ghi rõ ngưỡng STV trong `analysis/clinical_results.json → meta.threshold_source` là "CHƯA kiểm chứng bản gốc". | Mục 1, thay cho ba cột Doppler/da đầu/bụng mẹ. |
| M6 | **Chi phí và thời gian thực** | Có 4,35 ms/cửa sổ và 0,48 MB nhưng không đặt vào khung "chạy trên gì, pin bao lâu, trễ bao nhiêu". Lọc hai chiều cần cả khối (đã thừa nhận ở Mục 5). | Hai dòng: (1) mạng nhỏ hơn một ảnh chụp điện thoại, xử lý nhanh hơn thời gian thực khoảng nghìn lần trên CPU máy tính [SỰ KIỆN, 4 s / 4,35 ms]; (2) chưa đo trên vi điều khiển, chưa đo chế độ khối trượt, chưa có phần cứng, chưa ước giá [SỰ KIỆN: chưa làm]. Không đưa số chi phí không có nguồn. | Cuối Mục 5. |
| M7 | **Đạo đức và an toàn dữ liệu** | Mục 14 xin "đầu mối khoa sản để xin dữ liệu có nhãn" mà không nói tới hội đồng đạo đức, đồng thuận, ẩn danh. Giảng viên y sinh sẽ hỏi ngay. | (1) Dữ liệu hiện tại: PhysioNet công khai, đã ẩn danh; giấy phép cấm phân phối lại, repo đã chặn `*.dat *.hea *.edf` (`HANDOFF.md` §9). (2) Dữ liệu mới: cần phê duyệt hội đồng đạo đức của bệnh viện, phiếu đồng thuận, ẩn danh trước khi ra khỏi bệnh viện; chưa bắt đầu thủ tục. | Mục 14, trước "ba việc xin cô". |
| M8 | **Kế hoạch kiểm chứng lâm sàng** | Có "ba việc rẻ" kỹ thuật, không có lộ trình từ "số trên PhysioNet" tới "bác sĩ tin". | Ba nấc [KHUYẾN NGHỊ]: (a) kiểm hồi cứu trên dữ liệu bệnh viện có nhãn da đầu, khai báo trước quy tắc chọn dây và ngưỡng cổng, neo bằng commit; (b) so song song với CTG trên cùng sản phụ; (c) chỉ sau đó mới nói tới dùng tại nhà. Nói rõ năm nay đề tài chỉ tới nấc (a) nếu có dữ liệu. | Mục 14. |
| M9 | **Giới hạn pháp lý** | Người nghe có thể hiểu "đèn đỏ" là chức năng chẩn đoán. | Một câu cố định trên slide cuối và trong demo: *"Nguyên mẫu nghiên cứu, không phải thiết bị y tế, không dùng để ra quyết định lâm sàng."* Không nêu tên văn bản pháp luật cụ thể khi chưa kiểm. | Slide bìa, thanh tóm tắt demo, slide cuối. |
| M10 | **Tuổi thai và độ dài bản ghi của dữ liệu** | Ứng dụng giả định là thai kỳ (tuần 28–36), nhưng ADFECGDB và Silesia B2 là **chuyển dạ**, CinC chỉ **1 phút**. Không chỗ nào đối chiếu dữ liệu với kịch bản dùng. | Thêm một cột "giai đoạn thai kỳ / độ dài" vào bảng Mục 8 và một câu giới hạn: dữ liệu chưa đại diện cho theo dõi dài tại nhà. | Mục 8. |

---

## 3. Lỗi THỨ TỰ

Kịch bản đi đúng chuỗi câu hỏi của chủ nhiệm, nhưng chuỗi đó là **thứ tự người làm nghĩ**, không phải **thứ tự người nghe hiểu**. Các chỗ dùng trước khi giải thích:

| # | Dùng ở | Được giải thích ở | Vấn đề |
|---|---|---|---|
| T1 | "12,12 điểm" Mục 2 | F1 chưa bao giờ định nghĩa; "Power-MF" chưa giới thiệu | Con số đầu tiên của buổi rơi vào khoảng trống. |
| T2 | "Trong miền lệch 0,33, ngoài miền 20,50" Mục 1 | "miền" Mục 4, dữ liệu Mục 8 | Khái niệm miền dùng ở phút thứ hai, giải thích ở phút 15. |
| T3 | ADFECGDB, CinC, 22 chủ thể, 60 bản sạch — Mục 3, 4 | Mục 8 | Người nghe không biết 22 người đến từ đâu khi nghe kết quả chính. |
| T4 | "hậu kiểm" Mục 4; "Holm" Mục 6; gate/gate4 Mục 6 | Mục 11 (chỉ nêu, không định nghĩa) | Đóng góp được trình bày trước bằng chứng. |
| T5 | Mục 6 "đóng góp" | Bằng chứng ở Mục 11, rút lại ở Mục 12 | Nói "em có bốn thứ để nộp" khi người nghe chưa thấy kết quả. |
| T6 | "Oracle" Mục 10 | Số oracle Mục 11 | |
| T7 | "Cổng từ chối" Mục 1, 2 | Cổng học từ đâu: không mục nào | |
| T8 | Mục 4 và Mục 10 | — | Trùng nội dung: cùng khoảng 94–99,7 và 77,8–98,1, cùng câu "không bài nào so đầu-đối-đầu". |
| T9 | Demo Mục 13 (phút 25) | — | Người nghe phải nghe 25 phút số liệu trước khi **thấy** tín hiệu. Hình r01 là cách nhanh nhất để giải thích "tim mẹ lấn tim bé" và "F1". |

**Thứ tự đề xuất (giữ nguyên 30 phút):**

1. **Mục 1** Bài toán lâm sàng + **M2** người dùng + **M5** so với CTG (2,5′).
2. **Mục 2** Vì sao một kênh — **bỏ con số 12,12 khỏi đây**, chỉ nói hai cái giá (1,5′).
3. **Mới: Hệ thống trong một hình** (M1) + **demo thẻ r01 bước 1–5** kéo từ Mục 13 lên (2′). Dùng r01 để định nghĩa: tim mẹ/tim bé, khử mẹ, đường tin của mạng, F1, ±50 ms, đèn.
4. **Mục 8** Dữ liệu — kéo lên, thêm trong miền/ngoài miền, trực tiếp/gián tiếp, mức chủ thể, 15 bản chồng lấn một câu (2′).
5. **Mục 5** Năm bước kỹ thuật — rút, vì hình ở bước 3 đã có; sửa câu S1 (1,5′).
6. **Mục 3** Một so bốn (+ KTC, p, 89,49 giải thích bằng hình cột) (2,5′).
7. **Mục 9** Công bằng đối chuẩn (2′).
8. **Mục 11** Kết quả — tách thành 11a ngoài miền + chọn dây (định nghĩa gate / gate4 / peakprob / oracle / Holm / hậu kiểm tại đây), rồi **demo a09** ngay sau; 11b cổng từ chối (học từ đâu, 0,934 nói đúng phạm vi — S2), rồi **demo a02 + a27** ngay sau; 11c ba kết quả âm tính (6′ gồm demo).
9. **Mới M4** Khi hệ thống sai (1′).
10. **Mục 7** Vì sao mô hình này — rút còn một bảng, đặt sau kết quả vì là kết quả âm tính "kiến trúc là đòn bẩy yếu" (1,5′).
11. **Mục 4 + Mục 10 gộp** thành "Văn liệu: 5 hướng, ta đứng ở đâu" (2,5′).
12. **Mục 12** Đã rút (1,5′).
13. **Mục 6** Đóng góp — **dời xuống sau Mục 12**, lúc người nghe đã thấy bằng chứng và ranh giới (1,5′).
14. **Mục 14** Định vị + **M7** đạo đức + **M8** kiểm chứng lâm sàng + **M9** pháp lý (1,5′).

Tóm tắt di chuyển: Mục 8 lên vị trí 4; demo r01 lên vị trí 3; Mục 13 tách ba mảnh chèn vào Mục 11; Mục 7 xuống sau kết quả; Mục 4 gộp vào Mục 10 và xuống; Mục 6 xuống sau Mục 12.

---

## 4. Con số người nghe KHÔNG hình dung được độ lớn

Quy đổi chung dễ hiểu nhất: **tỉ lệ lỗi ≈ 100 − F1** (xấp xỉ, đúng khi sót và dư ngang nhau). Phải nói "khoảng" khi dùng.

| Số | Vì sao khó hình dung | Bối cảnh đề xuất |
|---|---|---|
| **97,56** | "Cao" nhưng không biết cao để làm gì. | ≈ 2–3 nhịp lỗi / 100 nhịp; ở 140 lần/phút ≈ 3–4 nhịp lỗi mỗi phút. Đặt cạnh 98,83 (≈ 1 lỗi / 100). Và nói thẳng: chưa biết mức lỗi này đủ cho chỉ số biến thiên hay chưa. |
| **−1,27** | "Nhỏ" theo thang F1, nhưng theo thang lỗi là **gấp đôi**: 2,44 so với 1,17 lỗi / 100 nhịp. | Nói cả hai cách: "kém 1,27 điểm, tức số nhịp lỗi khoảng gấp đôi bốn kênh; nhưng khoảng tin cậy chạm 0, chưa khẳng định được". Trung thực hơn là chỉ nói "1,27 nhỏ". |
| **12,12 điểm** | Không biết nhiều hay ít. | Power-MF từ ≈ 1,2 lên ≈ 13,3 lỗi / 100 nhịp khi mất ba dây: **gấp khoảng 11 lần**. So với biến thiên giữa hai hạt giống huấn luyện (+0,03) thì gấp hàng trăm lần. |
| **+10,85** | | Từ ≈ 13 lỗi xuống ≈ 2–3 lỗi / 100 nhịp trên cùng một dây, cùng 22 người, thắng cả 22. |
| **89,49 % [81,4; 103,2]** | Phần trăm của cái gì; cận trên >100 khó hiểu. | Hình thanh: thanh dài 12,12 (lợi ích bốn dây), tô 10,85 phần em bù được. Cận trên 103 = "chưa loại trừ được là bù đủ", không phải "vượt". |
| **p 0,156** | | "Khoảng 1 trong 6 lần chỉ do may rủi" (mục 1 báo cáo, dòng 13). |
| **18/22** | Tưởng là thắng áp đảo. | Đặt cạnh 4 người thua đậm; vẽ biểu đồ chấm từng người (hình H3). |
| **74,28 → 81,01 → 82,01 → 83,60** | Bốn số sát nhau, người nghe không phân biệt quan trọng. | Quy ra lỗi: ≈ 26 → 19 → 18 → 16 lỗi / 100 nhịp. Và số bản hỏng (F1 < 50): 16 → 9 trên 60, tức từ 1/4 xuống ≈ 1/7 bản ghi. Oracle là trần; peakprob đi được 82,92 % quãng đường tới trần. |
| **+7,73 [+3,82; +12,41]** | | So với **mức thổi phồng do chồng lấn 3,27–7,18**: cỡ cải tiến ngang cỡ sai lệch do dữ liệu bẩn. Đây là lý do phải loại 15 bản trước. |
| **p_Holm 0,051 vs 0,015** | 0,051 và 0,05 trông như nhau. | Nói ngưỡng là quy ước khai báo trước; 0,051 **trượt** theo đúng luật mình tự đặt, không làm tròn. Không trình bày như "gần đạt". |
| **AUROC 0,934** | Không biết tốt hay xấu. | 0,5 = tung đồng xu; 1,0 = hoàn hảo; cổng cũ đang chạy trong demo = 0,721. Và: tính trên 11/22 người có đoạn xấu; tỉ lệ đoạn xấu nền 5,40 %. Đề xuất thêm một con số vận hành dễ hiểu từ `gate22_results.json → rui_ro_do_phu_ban_ghi` (ví dụ: bỏ 3 bản khó thì F1 +0,27, độ phủ còn 86,4 %). |
| **17,92 điểm** khoảng cách ngoài miền | | ≈ 2–3 lỗi / 100 trong miền so với ≈ 20 lỗi / 100 ngoài miền: **gấp khoảng 7 lần**. |
| **18,0 %** âm tính giả của phép thử | Không biết liên quan gì. | "Phép thử em dùng để đổ lỗi cho dữ liệu sai gần 1 lần trong 5 — nên em không đổ lỗi được." |
| **3,27–7,18** thổi phồng | | So với +7,73 của quy tắc chọn dây (trên) và với 1,27 khoảng cách một/bốn kênh: chồng lấn đủ lớn để đảo mọi kết luận nhỏ. |
| **113.481 tham số, 0,48 MB** | | Nhỏ hơn một ảnh chụp điện thoại; mạng nhận diện ảnh phổ biến lớn hơn hàng trăm lần (chỉ nói khi có nguồn số cụ thể; nếu không, chỉ giữ so sánh ảnh điện thoại). |
| **4,35 ms / cửa sổ 4 s** | | Xử lý 4 giây tín hiệu trong chưa tới 5 phần nghìn giây, nhanh hơn thời gian thực khoảng 900 lần — trên CPU máy tính, chưa trên thiết bị đeo. |
| **1.516 ms** trường tiếp nhận | | ≈ 3–4 nhịp thai ở 140 lần/phút; 60 ms của họ kém nhất ≈ một phần bảy nhịp. |
| **×4 tham số → +0,26** | | Tăng bốn lần kích thước, số lỗi giảm chưa tới 3 trên 1.000 nhịp. |
| **0,33 ms** chệch STV | | Chỉ nêu kèm n = 5 và thang của chỉ số (STV cỡ vài ms, `stv_ref_mean` ≈ 9,6 ms trên 5 bản). Bỏ 20,50 (S4). |
| **1/1540** | | = số cách chọn 3 bản trong 22; "như rút đúng ba lá bài đã định từ một bộ 22 lá". Kèm ngay 5/24 để không bị hiểu là cổng đặc biệt giỏi. |
| **22 chủ thể / cần ≈ 50** | | Nói "cần hơn gấp đôi số sản phụ hiện có". |
| **58 % / 12 % / 60 %** ước cửa | Người nghe dễ hiểu là xác suất đo được. | Nói là ước lượng chủ quan của nhóm; nếu không có cơ sở định lượng thì chỉ xếp hạng cao/trung bình/thấp. |

---

## 5. Bảy câu hỏi KHÓ NHẤT chưa được chuẩn bị

Đã đối chiếu với các câu [NẾU CÓ HỎI] trong Mục 1–14 và 15 câu Phụ lục A; bảy câu dưới đây không trùng.

**Q1. "Em nói cổng không lấy từ mạng để không sụp cùng mạng. Nhưng đặc trưng quan trọng nhất của cổng là độ đều nhịp do mạng tìm ra, và có cả xác suất của mạng. Vậy khi mạng tự tin sai thì cổng có sụp theo không?"**
> "Cô nói đúng, câu trong slide của em sai và em rút. Hai trong mười hai chỉ số là xác suất của mạng, và chỉ số quan trọng nhất là độ đều của nhịp mạng tìm ra. Nên cổng không độc lập với mạng. Bản a02 là ví dụ: mạng tự tin trên nhịp mẹ, nhịp rất đều; cái bắt được lỗi là luật 'bám nhịp mẹ', so trực tiếp với nhịp mẹ, không phải mười hai chỉ số."

**Q2. "Đèn trong demo là cổng nào? Con số 0,934 em đọc có phải của chính cái đèn đó không?"**
> "Không phải, em phải sửa. Demo đang dùng cổng cũ học trên mô hình 5 ca; trong bản ghi cổng đó được 0,721, khoảng rộng. Số 0,934 là cổng 22 ca, mới có ở dạng phân tích, và chỉ tính được trên 11 trong 22 người có đoạn xấu. Thay cổng trong demo là việc chưa làm."

**Q3. "Bệnh viện đã có CTG, và CTG theo Dawes–Redman đã tính biến thiên ngắn hạn. Điện tim bụng một dây cho bác sĩ thêm được gì cụ thể?"**
> "Em chưa trả lời được bằng số. Điều em đo được chỉ là máy tìm từng nhịp trên tín hiệu điện, trong miền sai số thời điểm nhỏ. Lợi ích lâm sàng so với CTG là giả thuyết, cần so song song trên cùng sản phụ, và đó là câu em muốn hỏi bác sĩ sản trước khi nói tiếp."

**Q4. "Ba bản em đem demo là bản đẹp nhất để kể chuyện. Trên 60 bản thì quy tắc mới thua ở bao nhiêu bản, và có bản nào dây em chọn kém xa dây tốt nhất không?"**
> "Đúng là em chọn để minh hoạ. Trên 60 bản quy tắc mới thắng 19, hoà 35, thua 6, bản thua nặng nhất mất 3,90 điểm. Nhưng so với dây tốt nhất thì có bản kém xa, ví dụ chính a02: dây 1 được 75,9, dây em chọn 24,9. Em nên thêm một thẻ 'chọn sai' vào demo thay vì chỉ thẻ thắng."

**Q5. "Chín trên sáu mươi bản ngoài miền F1 dưới 50. Tức khoảng một lần trong bảy máy gần như hỏng. Cổng có bắt được đúng chín bản đó không?"**
> "Em chưa tính trên 60 bản sạch nên không trả lời bằng số. Số cổng trên CinC cũ đo trên 75 bản có bản trùng, em đã bỏ. Đây là việc thứ hai trong ba việc rẻ của em; nếu cổng không bắt được mấy bản này thì cả lập luận an toàn ngoài miền không đứng."

**Q6. "60 bản CinC có nhãn. Sao không lấy một phần để tinh chỉnh, phần còn lại để kiểm? Bốn cách thích nghi miền thất bại có gồm cách dùng nhãn không?"**
> "Em không tách vì không biết bản nào cùng một sản phụ; có nguồn góp 14 bản từ một người. Tách ngẫu nhiên theo bản thì lại rò rỉ đúng kiểu em vừa rút. Còn bốn cách thích nghi miền, em phải mở lại tệp để nói chính xác cách nào có dùng nhãn, em không muốn trả lời theo trí nhớ."

**Q7. "Dữ liệu huấn luyện chủ yếu là chuyển dạ và bản ghi ngắn. Ứng dụng em nói là theo dõi tại nhà khi thai còn nhỏ, lâu hàng chục phút, mẹ cử động. Dữ liệu có đại diện không?"**
> "Không đại diện, em phải ghi vào giới hạn. ADFECGDB và Silesia B2 là chuyển dạ, CinC mỗi bản một phút. Em chưa kiểm hiệu năng theo tuổi thai hay theo cử động của mẹ. Kịch bản tại nhà là động cơ, chưa phải điều em đã chứng minh."

---

## 6. Trường hợp a02 — trả lời trung thực mà không sụp đề tài

**Sự kiện trên đĩa** (`analysis/chonkenh_results.json`, `demo/results/demo_check_showcase.json → a02_leadpeakprob`):
* Dây 1: F1 **75,88** (= oracle). Dây 2 (được chọn): **24,91**. Trung bình bốn dây 36,29; dây tệ nhất 19,86.
* **Cả sáu** quy tắc mù nhãn chọn dây 2: psd, gate, gate4, rrcv, peakprob, rrplaus. Riêng `learned` chọn dây 3 (19,86).
* Trên dây 2: 78 % nhịp mạng tìm trùng đỉnh R mẹ → luật bám mẹ ghi đè → đèn đỏ.
* Chưa đo dây 1 có bám mẹ hay không.

**Trước hết sửa lời thoại** bước 4 thẻ a02: thay "Dây nào cũng vậy, không dây nào cứu được" bằng *"Ba dây đều kém, một dây khá hơn nhiều, nhưng mọi quy tắc chọn mù đều không chọn được nó."*

**Câu trả lời mẫu** (khoảng 60 giây):

> "Cô nhìn đúng, và câu em nói lúc nãy là sai. Ở a02, dây 1 được 75,9, dây hệ thống chọn chỉ 24,9.
>
> Có ba điều em muốn nói thật. Một, đây không phải lỗi riêng của quy tắc mới. Cả sáu quy tắc chọn mù, kể cả quy tắc cũ PSD và gate4 khai báo trước, đều chọn dây 2. Hai, lý do em đoán được: quy tắc mới chọn dây mà mạng tự tin nhất. Ở a02 mạng tự tin trên nhịp **mẹ**, nhịp đều và rõ, nên tự tin sai. Đó là giới hạn gắn liền với mọi quy tắc dựa trên độ tin của chính mạng. Ba, cái giá trung bình của chọn mù em đã báo: 82,01 so với trần 83,60.
>
> Điều hệ thống làm đúng ở a02: nó không đưa con số sai cho bác sĩ. Luật bám mẹ thấy 78 % nhịp trùng nhịp mẹ và bật đèn đỏ. Nên bản này là thất bại của khâu chọn dây, và là thành công của khâu từ chối. Em không nói nó cứu được.
>
> Hướng sửa em nghĩ tới là loại dây bám mẹ trước khi chọn. Nhưng em chưa đo, và nếu làm thì đó là một quy tắc hậu kiểm nữa, phải kiểm trên dữ liệu mới. Và với thiết bị thật chỉ có một dây, sẽ không có dây 1 để chọn."

**Vì sao câu này không làm sụp đề tài:** nó dựa đúng vào hai câu hỏi của đề tài (một dây mất bao nhiêu; máy có biết lúc không nên trả lời không). a02 trả lời "có" cho câu thứ hai và cho thấy giới hạn thật của câu thứ nhất. Điều làm sụp là bị bắt gặp nói "không dây nào cứu được" khi cột F1 đang hiện 75,9.

---

## 7. Hình / sơ đồ nên thêm vào slide

| # | Hình | Vẽ chính xác cái gì | Đặt ở |
|---|---|---|---|
| H1 | **Hệ thống từ điện cực đến đèn** | Hàng ngang 7 ô: bụng mẹ (4 điện cực, chọn 1) → lọc 10–60 Hz, 250 Hz → khử tim mẹ (mẫu trung vị) → chọn dây mù nhãn → TCN 113 481 tham số, nhìn 1,5 s → dãy nhịp + nhịp tim mỗi 4 s → đèn xanh/vàng/đỏ. Dưới mỗi ô một ảnh nhỏ 3 giây tín hiệu lấy từ r01 (bước 1, 2, 3 của demo). Mũi tên nét đứt từ ô TCN sang ô "chọn dây" và ô "đèn" ghi "dùng xác suất của mạng" (sửa S1). Một ô phụ "luật bám mẹ" nối từ ô khử mẹ (nhịp mẹ) sang đèn. | Sau Mục 2 (vị trí 3 thứ tự mới). |
| H2 | **F1 và ±50 ms trên một hình** | Trục thời gian 3 giây; hàng trên vạch đen nhịp thật; hàng dưới vạch nhịp máy báo; quanh mỗi nhịp thật một ô tô nhạt rộng ±50 ms; đánh dấu một nhịp đúng (trong ô), một nhịp sót (ô trống), một nhịp dư (ngoài ô). Bên phải công thức bằng chữ: "F1 cao khi ít sót và ít dư". | Ngay sau H1, trước Mục 3. |
| H3 | **22 sản phụ, từng người một** | Biểu đồ chấm nối cặp: trục ngang 22 chủ thể xếp theo hiệu; mỗi người ba chấm (Power-MF 4 dây, Power-MF 1 dây, RelyFetal). Tô đỏ 4 người RelyFetal thua 4 dây. Bên phải một thanh ngang dài 12,12 với phần tô 10,85 ghi "89,49 % [81,4; 103,2]". Nguồn `baselines/powermf_fair_stats.json → per_subject`. | Mục 3. |
| H4 | **60 bản ngoài miền: bốn quy tắc và trần** | Thanh ngang có khoảng tin cậy cho psd 74,28 · gate 80,72 · gate4 81,01 · peakprob 82,01 · oracle 83,60; cạnh mỗi thanh nhãn "khai báo trước / hậu kiểm / trần", và p_Holm (0,051 trượt · 0,015 sống · 0,0039 hậu kiểm). Dưới: đường kẻ ngang ở 97,56 ghi "trong miền" để thấy khoảng cách 17,92. Không vẽ 93,12 như đối thủ cùng điều kiện; nếu có thì ghi "số dẫn xuất, 4 dây". | Mục 11a. |
| H5 | **Bản đồ sai của đèn (2×2)** | Ô vuông 2×2: hàng = đèn xanh / đèn đỏ; cột = F1 ≥ 90 / F1 < 90; điền số bản trên 82 bản ở chế độ học từ `facts_phase4.json → F_demo.summary_by_mode.hoc` (xanh 46 bản, trong đó 3 bản F1 < 90, thấp nhất 17,02; đỏ 19 bản, 0 bản F1 ≥ 95). Ghi rõ đây là **cổng cũ đang chạy trong demo** và nhóm 82 bản gồm 22 bản trong miền. Chú thích góc: "ô nguy hiểm = xanh mà sai". | Mục mới M4, trước demo a02. |

---

## 8. Phán xử

Kịch bản v2 **trung thực và có nguồn**, nhưng được viết cho người đã sống trong dự án. Một giảng viên y sinh nghe lần đầu sẽ mất hướng ngay từ Mục 2: con số đầu tiên (12,12) đến trước khi biết F1, Power-MF và 22 người là gì. Thứ tự đi theo **chuỗi câu hỏi của người làm**, không theo **đường hiểu của người nghe**. Phần lâm sàng (người dùng, CTG, khi hệ sai, đạo đức, pháp lý) gần như vắng, trong khi đó lại là phần giảng viên y sinh có sẵn trong đầu để bám vào.

Nặng hơn chuyện dễ hiểu: có **bốn câu sai sự thật** nằm đúng chỗ sẽ bị hỏi — cổng "không lấy từ mạng" (S1), 0,934 bảo chứng cho cổng không có trong demo (S2), "không dây nào cứu được" ở a02 trong khi hình hiện 75,9 (S3), và 20,50 ms từ mẫu có 4 bản nhiễm (S4). Cả bốn đều **sửa được trong một buổi** và không đổi con số chính nào. Nếu không sửa, chỉ một câu bị bắt là đủ làm người nghe nghi phần còn lại, đúng loại rủi ro mà Phụ lục B đã cảnh báo.

**Thứ tự ưu tiên:** (1) sửa S1–S4 và S6 trong kịch bản, hướng dẫn demo và lời thoại thẻ a02; (2) thêm H1 + H2 và kéo demo r01 cùng Mục 8 lên trước Mục 3; (3) thêm hộp "con số này nghĩa là gì" theo mục 4 báo cáo này; (4) thêm M4, M5, M7, M9; (5) gộp Mục 4 với Mục 10 và dời Mục 6 xuống sau Mục 12.
