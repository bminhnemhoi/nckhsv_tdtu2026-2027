# Kịch bản thuyết trình v2 — RelyFetal (30 phút + hỏi đáp)

**Ngày lập:** 17/09/2026 · **Sửa theo thẩm định vòng 10:** 17/09/2026 · **Đồng bộ với demo sau lượt sửa thứ hai vòng 10c (D-sync):** 17/09/2026 · **Đồng bộ với demo sau lượt sửa thứ ba, kiểm demo độc lập lần hai (D-sync2):** 17/09/2026 · **Commit tham chiếu:** b158507 + thay đổi chưa commit · **Người trình bày:** Ngô Bình Minh (TDTU) · **Người nghe:** giảng viên hướng dẫn, giỏi y sinh, không chuyên xử lý tín hiệu, nghe đề tài lần đầu.

**Thứ tự 14 khối đi theo đường hiểu của người nghe** (thẩm định vòng 10, mục 3): thấy bài toán → thấy hệ thống chạy → biết dữ liệu → biết khái niệm → mới nghe kết quả → cuối cùng mới nghe đóng góp. Mỗi khối có:

| Phần | Nghĩa |
|---|---|
| **[NÓI GÌ]** | Lời thoại đọc gần nguyên văn. Câu ngắn, mục tiêu tối đa 20 từ. Không đọc đường dẫn tệp thành tiếng. |
| **[CHIẾU GÌ]** | Slide, hình, thẻ demo. Hình H1–H5 mô tả đủ để người vẽ slide vẽ được. Số slide theo tệp `docs/trinh_bay/slide_bao_cao.html` (31 slide; đánh lại số ngày 17/09 cho khớp tệp). |
| **Con số này nghĩa là gì** | Hộp quy đổi số sang thang người nghe hình dung được. Chỉ đọc khi có thời gian hoặc khi bị hỏi. |
| **[NẾU CÓ HỎI]** | Một đến hai câu hỏi sát nhất, kèm câu trả lời. Câu hỏi khó hơn ở Phụ lục A. |
| *Chú thích* | Nguồn từng con số. Chỉ mở khi bị hỏi. |

**Nguồn sự thật:** `survey/facts_phase4.json` (mục `Z_DA_RUT` liệt kê số đã rút). Bảng đối chiếu số → nguồn ở Phụ lục D. Tài liệu nền: `docs/BOI_CANH_1_KENH.md`, `docs/TOM_TAT_30_BAI.md`, `docs/CONG_BANG_DOI_CHUAN.md`, `analysis/GATE22.md`, `analysis/CLINICAL.md`.

**Quy ước phát biểu:** [SỰ KIỆN] có số đo trên đĩa · [SUY LUẬN] nhóm rút ra từ số đo · [GIẢ THUYẾT] chưa có phép đo · [KHUYẾN NGHỊ] đề xuất · [CẦN KIỂM BẢN GỐC] có trong tài liệu nhóm nhưng chưa có bài gốc trong `papers/` hoặc `survey/`.

**Câu cố định (slide bìa, slide cuối, nói khi mở demo):** *"Nguyên mẫu nghiên cứu, không phải thiết bị y tế, không dùng để ra quyết định lâm sàng."*

---

## Đã sửa theo thẩm định vòng 10

| Mã | Câu cũ | Đã thay bằng | Ở đâu |
|---|---|---|---|
| S1 | Cổng dùng chỉ số "không lấy từ mạng", "không sụp cùng mạng" | Cổng dùng 12 chỉ số: 2 là xác suất của mạng, 4 tính trên nhịp mạng tìm ra, 6 thuần tín hiệu. Chỉ số quan trọng nhất là độ đều nhịp mạng tìm ra. Cổng **không độc lập** với mạng | Khối 3, 5, 8b; A16 |
| S2 | Đèn demo được bảo chứng bằng AUROC 0,934 | Đèn demo là **cổng cũ** (mô hình 5 ca), trong bản ghi 0,721 [0,517; 0,898], đo trên 5 bản CinC sạch **khi ghép với mô hình 5 ca**; ghép với mô hình 22 ca đang chạy trong demo thì **chưa đo lại**. 0,934 là cổng 22 ca, **chỉ ở dạng phân tích**, tính trên 11/22 chủ thể | Khối 8b; A17 |
| S3 | a02: "Dây nào cũng vậy, không dây nào cứu được" | Dây 1 đạt 75,88; ba dây còn lại dưới 25; 6/7 cách chọn không nhìn đáp án chọn dây 2 (learned chọn dây 3), không cách nào chọn dây 1 | Khối 8b; A3-bis |
| S4 | Chệch STV ngoài miền trên mẫu CinC 10 bản | Bỏ hẳn (mẫu a01–a10 chứa 4 bản nhiễm). Chỉ giữ +0,33 ms, kèm n = 5 | Khối 1 |
| S5 | Khoảng cách trong/ngoài miền "15 điểm", "15 đến 23", "gần 18" | **Không dùng số khoảng cách cũ** trong `adapt/adapt_results.json → mo_phong_dich_chuyen.khoang_cach_CinC_con_lai`: tự kiểm thấy nó là 97,32 trừ mốc PSD **75 bản đã rút** (`adapt/adapt_analyze.py` dòng 15, 76). Thay bằng số tự tính trên 60 bản sạch: cùng quy tắc cũ chênh **23,28**; gate 16,84; gate4 16,55; quy tắc hậu kiểm 15,55; trần 13,96 | Khối 8c; Phụ lục B2, D |
| S6 | Chỉ nêu 74,28 và 82,01; hoặc nêu gate4 81,01 mà thiếu gate 80,72 | Luôn nêu đủ: 74,28 (cũ) · **80,72 (gate, quy tắc kế hoạch chọn, ghi trước khi chạy, trượt Holm p 0,051)** · 81,01 (gate4, cũng ghi trước khi chạy, qua Holm p 0,015, nhưng không phải quy tắc kế hoạch chọn) · 82,01 (peakprob, có trong danh sách ghi trước nhưng chọn làm mặc định sau khi xem kết quả CinC: hậu kiểm), kèm trần 83,60 | Khối 7, 8a, 8b, 11, 13; A3-bis, A11; Phụ lục C, D |
| S7 | Slide bìa ghi số kiểm thử | Bỏ số kiểm thử khỏi slide bìa. Danh sách kiểm trước buổi ghi **109** (43 trong `tests/` + 66 trong `demo/test_core.py`, đếm sau lượt sửa thứ ba) | Khối 1; mục Kiểm 15 phút |
| D-sync | Lời thoại demo theo giao diện cũ (4 thẻ chỉ có mã bản ghi, "Tải tệp của bạn", "cả sáu quy tắc", a27 "không có tín hiệu thì không đưa số") | Theo giao diện sau lượt sửa thứ hai vòng 10c: thẻ có tên ca (*Ca dễ*, *Chọn dây quyết định*, *Máy bám nhầm tim mẹ*, *Bốn dây đều kém*, *Tệp của bạn*); hộp vàng a02 ghi 6/7 cách chọn; dòng tóm tắt có đủ năm số. Chuỗi giao diện đối chiếu với `docs/HUONG_DAN_DEMO_v2.md` | Khối 3, 8a, 8b; Kiểm 15 phút |
| D-sync2 | r01 bước 1 "Gai lớn, đều là tim mẹ. Tim bé nhỏ hơn nhiều"; bước 3 "vạch xanh lá là nhịp đã tìm" và ghi chú lệch "vạch đỏ"; a09 "máy ghi khác"; "bốn dây cho bốn tín hiệu"; ô "F1 (độ đúng…)"; 103 kiểm thử | Theo giao diện sau lượt sửa thứ ba: r01 dây 4 gai bé **to ngang** gai mẹ (demo đo biên độ trên chính bản ghi); bước 3 *vạch tím đậm là nhịp mạng đã báo, chưa biết đúng hay sai*; thẻ CinC chỉ ghi *không trùng dữ liệu huấn luyện (ngoài miền); nguồn thiết bị từng bản không được công bố*; *mỗi dây cho một tín hiệu khác nhau*; ô *F1 (bắt đủ và báo đúng, 100 là hoàn hảo)*; bước 5 ghi *Xanh không bảo đảm là đúng*; 109 kiểm thử | Khối 3, 4, 8a, 8b, 9; bảng khái niệm; Phụ lục D #52; Kiểm 15 phút |
| S8 | "Set-a chứa 25 bản ADFECGDB" | Cuộc thi 2013 có 447 bản, trong đó 25 bản lấy từ ADFECGDB; ban tổ chức không nói bản nào ở tập nào; nhóm đo và định danh được 15 bản trong set-a | Khối 4 |
| Thêm | — | a02: cổng cũng đánh đỏ 6/15 đoạn (40 %), không chỉ luật bám nhịp mẹ | Khối 8b; A16 |
| Thêm | "Nếu chỉ trích số, em đã thắng oan chín điểm" | Bỏ con số, nói đúng cơ chế: nếu không vá thì em so với một Power-MF hỏng | Khối 7 |
| Thêm | "Bảy họ kiến trúc gần như ngang nhau" | "Ba họ đầu cách nhau 0,02 điểm; họ kém nhất kém vì nhìn quá hẹp" | Khối 13 |
| Thêm | "Số đo trực tiếp thì không cái nào phải rút" | Bỏ. Hai trong năm tuyên bố đã rút là số đo trên sai tập hoặc sai mô hình | Khối 12 |
| Thêm | "Thai chậm phát triển là nguyên nhân hàng đầu của thai lưu" | Hạ thành "gắn với nguy cơ thai lưu", ghi [CẦN KIỂM BẢN GỐC] | Khối 1 |
| Thẩm định tài liệu 17/09 | "gate4 là kết quả, peakprob là giả thuyết"; "gate và gate4 là kết quả khai báo trước"; khoảng cách thiếu gate 16,84; hướng ba "94 đến 99,7 / 77,8 đến 98,1" (tính cả Castillo, bài cổ điển); "chắc chắn < 60"; số slide lệch tệp HTML từ slide 7; "khoảng cách này đo bề rộng ngữ cảnh" | Gate là quy tắc kế hoạch chọn, trượt Holm; gate4 cũng ghi trước, qua Holm; peakprob hậu kiểm · thêm 16,84 · 96,5–99,7 / 77,8–97,97 · "nhiều nhất 60" · đánh lại số slide theo `slide_bao_cao.html`, thêm mục slide 15 · "phần lớn (≈ 74 %)" | Khối 4, 5 (khái niệm), 8b, 8c, 10, 11, 12; Phụ lục D; Kiểm 15 phút |

---

## Phân bổ thời gian (30 phút)

| Khối | Nội dung | Phút | Mốc |
|---|---|---:|---|
| 1 | Bài toán lâm sàng, người dùng giả định, so với CTG | 2,5 | 0:00–2:30 |
| 2 | Vì sao một điện cực | 1,5 | 2:30–4:00 |
| 3 | Hệ thống trong một hình (H1) + demo r01 + F1 và ±50 ms (H2) | 2 | 4:00–6:00 |
| 4 | Dữ liệu: bốn bộ, trong miền, ngoài miền | 2 | 6:00–8:00 |
| 5 | Năm bước kỹ thuật, mỗi bước một vì sao | 1,5 | 8:00–9:30 |
| — | **Những khái niệm cần hiểu trước** | 1 | 9:30–10:30 |
| 6 | Một dây so với bốn dây (H3) | 2,5 | 10:30–13:00 |
| 7 | Đối chuẩn công bằng đến đâu | 2 | 13:00–15:00 |
| 8 | Kết quả: 8a chọn dây + demo a09 · 8b đèn tin cậy + demo a02, a27 · 8c âm tính | 6 | 15:00–21:00 |
| 9 | Khi hệ thống sai (H5) | 1 | 21:00–22:00 |
| 10 | Vì sao mô hình này | 1,5 | 22:00–23:30 |
| 11 | Văn liệu: năm hướng, em đứng ở đâu | 2 | 23:30–25:30 |
| 12 | Những gì đã rút | 1,5 | 25:30–27:00 |
| 13 | Đóng góp, kèm ranh giới | 1,5 | 27:00–28:30 |
| 14 | Định vị, kế hoạch, đạo đức, pháp lý | 1,5 | 28:30–30:00 |

Phút 15 mà chưa xong khối 7 thì cắt theo Phụ lục C.

---

## Khối 1 — Bài toán lâm sàng, người dùng giả định, so với CTG (2,5 phút)

### [NÓI GÌ]

> "Em xin bắt đầu từ câu hỏi lâm sàng.
>
> Theo tài liệu em đọc, thai chậm phát triển gắn với nguy cơ thai lưu. Một dấu hiệu được theo dõi là nhịp tim thai giảm biến thiên. Muốn đo biến thiên, phải biết từng nhịp rơi vào mili-giây nào. Nên em làm bài toán định vị từng nhịp, thay vì đếm nhịp trung bình.
>
> Ở bệnh viện, cô quen với tim thai đồ, tức CTG. CTG dùng đầu dò Doppler, không xâm lấn, phổ biến. Nó cho nhịp tim, không cho hình dạng sóng điện tim. Và cần người đặt đầu dò.
>
> Điện cực da đầu thai cho tín hiệu sạch nhất. Nhưng nó xâm lấn, chỉ gắn được khi chuyển dạ và đã vỡ ối.
>
> Lối thứ ba là điện tim ghi từ bụng mẹ. Không xâm lấn, vẫn là tín hiệu điện. Khó ở chỗ tim thai nhỏ hơn tim mẹ nhiều lần.
>
> Người dùng em hình dung là sản phụ cần theo dõi giữa hai lần khám. Dữ liệu gửi về bác sĩ. Đèn đỏ nghĩa là nên đi khám lại, không phải chẩn đoán. Đây là kịch bản giả định.
>
> Đề tài hỏi hai câu. Một: chỉ dùng một điện cực thì mất bao nhiêu so với bốn? Hai: máy có tự biết lúc nào không nên trả lời không?
>
> Em xin nói trước một ranh giới. Em chưa gặp bác sĩ sản nào. Mọi lập luận lâm sàng ở đây là em đọc, chưa được kiểm. Đây là nguyên mẫu nghiên cứu, không phải thiết bị y tế."

### [CHIẾU GÌ]

**Slide 1 — bìa.** Tên đề tài, người trình bày, bốn ô số: *113.481 tham số* · *22 sản phụ* · *60 bản kiểm ngoài miền* · *4 bộ dữ liệu công khai*. Không ghi số kiểm thử. Chân slide: câu cố định pháp lý.

**Slide 2 — ba cách đo nhịp tim thai** (bảng ba cột, thay ba cột Doppler / da đầu / bụng mẹ cũ):

| | Tim thai đồ (CTG, Doppler) | Điện cực da đầu thai | Điện tim bụng mẹ |
|---|---|---|---|
| Xâm lấn | Không | **Có** | Không |
| Cho gì | Nhịp tim | Tín hiệu điện sạch, từng nhịp | Tín hiệu điện, từng nhịp, lẫn tim mẹ |
| Khi nào dùng được | Cần người đặt đầu dò | Chỉ khi chuyển dạ, đã vỡ ối | Về nguyên tắc: bất cứ lúc nào |
| Giới hạn | Không cho hình dạng sóng | Không dùng cho theo dõi thai kỳ | Tim thai bị tim mẹ lấn át; **chưa có kiểm chứng lâm sàng trong đề tài này** |

Dòng nhỏ dưới bảng: *"CTG trên máy thương mại có tính biến thiên ngắn hạn theo phương pháp Dawes–Redman [CẦN KIỂM BẢN GỐC]."* Không đọc dòng này thành tiếng.

**Slide 3 — hai câu hỏi + người dùng giả định.** Hai câu hỏi in to. Dưới: một hàng ba ô *sản phụ tự dán* → *dữ liệu gửi bác sĩ* → *đèn đỏ = đi khám lại*, nhãn góc "[GIẢ THUYẾT] — chưa kiểm với bác sĩ".

### [NẾU CÓ HỎI]

**H: "Biến thiên phải chính xác bao nhiêu mili-giây mới có nghĩa lâm sàng?"**
> "Em chưa trả lời được bằng nguồn đã kiểm. Người phản biện nội bộ có đưa một ngưỡng, nhưng em chưa đọc bản gốc nên không đọc số. Em chỉ đo được sai số của hệ mình. Trên 5 sản phụ trong miền, chỉ số biến thiên của máy lệch 0,33 mili-giây so với nhãn. Mẫu đó quá nhỏ. Ngoài miền em chưa có số dùng được. Nên em chưa dùng hệ này làm máy đo biến thiên."

**H: "CTG đã có sẵn và đã tính biến thiên. Điện tim bụng thêm được gì?"** → trả lời theo A18 (Phụ lục A).

*Chú thích:*
* [CẦN KIỂM BẢN GỐC] Bối cảnh lâm sàng (thai chậm phát triển, biến thiên nhịp tim, CTG, điện cực da đầu) lấy từ `docs/DE_CUONG_HIEN_TRANG.md` mục 3.1–3.2, nguồn ghi "mô tả lâm sàng chuẩn". Không có bài gốc lâm sàng trong `papers/` hoặc `survey/`. Câu "nguyên nhân hàng đầu của thai lưu" ở bản cũ không có nguồn trên đĩa, đã hạ xuống. Dawes–Redman: `analysis/CLINICAL.md` dòng 259, 262 ghi "tối thiểu 10 phút" và "tính trên tín hiệu CTG Doppler lấy mẫu đều" nhưng đó là ghi chú của nhóm, chưa đối chiếu bài gốc.
* [SỰ KIỆN] Chệch STV +0,33 ms: `analysis/clinical_results.json → summary.ADFECGDB.stv_diff_mean` = 0,3286, `n_records` 5, STV nhãn trung bình 9,62 ms; mô hình 5 ca để-một-ra (`checkpoint fetalqrs_tcn_fold_r0X`). Ngưỡng lâm sàng: `→ meta.threshold_source` ghi "CHƯA kiểm chứng bản gốc".
* [SỰ KIỆN, đã bỏ] Số chệch STV trên CinC trong cùng tệp đo trên a01–a10, chứa 4 bản nhiễm a03 a04 a05 a08; F1 của chính mẫu này nằm trong `facts_phase4.json → Z_DA_RUT.cinc_mau_10`. Không đọc.
* [GIẢ THUYẾT] Người dùng và tình huống dùng: chưa kiểm với bác sĩ.

---

## Khối 2 — Vì sao một điện cực (1,5 phút)

### [NÓI GÌ]

> "Vì sao em chọn một điện cực. Em có một lý do ứng dụng, và nói rõ cái giá.
>
> Lý do ứng dụng: em nghĩ tới miếng dán mẹ tự dùng ở nhà. Bốn điện cực cần người dán đúng vị trí. Một điện cực thì dễ tự dán hơn. Có nhóm ở nước ngoài đã đi hướng này, với điện cực vải khô.
>
> Cái giá thứ nhất nằm ở phần cứng của hướng nhiều dây. Phương pháp mạnh nhất em chạy lại cần bốn điện cực bụng. Có bài dùng tới mười hai kênh.
>
> Cái giá thứ hai nằm ở thuật toán. Nhóm phương pháp tách nguồn cần số điện cực ít nhất bằng số nguồn tín hiệu. Chỉ có một dây thì nhóm đó không dùng được.
>
> Một dây không có dư thừa để tự sửa. Nên hệ phải biết lúc nào nó sai. Đó là lý do có đèn tin cậy.
>
> Bỏ ba điện cực thì mất bao nhiêu, em sẽ cho số sau khi cô thấy hệ thống chạy."

### [CHIẾU GÌ]

**Slide 4:** hai cột *"Cái giá của nhiều dây"* (số điện cực: 4 bụng, có bài 12 kênh) | *"Cái giá của một dây"* (không tách nguồn được, không dư thừa). Một dòng dưới: *"một dây → cần đèn tin cậy"*. **Không có con số F1 nào trên slide này.**

### [NẾU CÓ HỎI]

**H: "Nếu một dây kém hơn, sao không dùng hai dây cho chắc?"**
> "Em chưa đo hai dây, em ghi lại. Em đặt câu hỏi ở cực một dây để có một con số rõ. Hai dây là bước tiếp theo hợp lý, nếu cô thấy đáng."

*Chú thích:* [SỰ KIỆN] điện cực vải khô đơn kênh — Orvas 2025 (p11); 4 điện cực bụng — Power-MF (`survey/scout_baselines.md`), Behar 2014 (p14); 12 kênh — Wahbah 2024 (p12); bão hoà ≥ 8 kênh — Andreotti 2016 (p15); 24 + 3 điện cực — NInFEA (`survey/scout_datasets.md` mục 2); tách nguồn cần cảm biến ≥ nguồn — DPSS nêu lý do (p05); Power-MF bỏ hai bước ICA khi còn một kênh — `survey/scout_baselines.md` mục 3.3. [GIẢ THUYẾT] "mẹ tự dán được" chưa kiểm. Số 12,12 điểm **đã dời** sang Khối 6 (thẩm định vòng 10, T1).

---

## Khối 3 — Hệ thống trong một hình, rồi xem nó chạy (2 phút)

Thứ tự: Slide 5, hình H1 (30 giây) → slide 6 rồi demo thẻ r01 đi đủ 5 bước (70 giây) → Slide 7, hình H2 (20 giây).

### [NÓI GÌ] — trên hình H1 (30 giây)

> "Đây là toàn bộ hệ thống trong một hình.
>
> Đầu vào là bốn dây điện cực trên bụng mẹ. Máy lọc nhiễu, rồi tìm và trừ tim mẹ.
>
> Phần còn lại đưa vào một mạng nơ-ron nhỏ. Mạng chạy trên cả bốn dây, cho xác suất có nhịp tại từng thời điểm.
>
> Máy tự chọn một dây, không nhìn đáp án. Đầu ra là dãy thời điểm từng nhịp và nhịp tim trung bình.
>
> Cuối cùng là đèn xanh, vàng, đỏ. Cô để ý ô viền cam: đèn cũng dùng đầu ra của mạng."

### [CHIẾU GÌ] — Hình H1: hệ thống từ điện cực đến đèn

Khổ ngang 16:9, một hàng **7 ô chữ nhật**, mũi tên liền trái sang phải. Trên mỗi ô là tên; trong ô là một ảnh nhỏ 3 giây tín hiệu cắt từ demo thẻ r01; dưới ô là **đầu ra trung gian** và **thời gian** (chữ xám, cỡ nhỏ).

| Ô | Tên trên ô | Ảnh trong ô (lấy từ demo r01) | Dưới ô: đầu ra · thời gian |
|---|---|---|---|
| 1 | Bụng mẹ, 4 điện cực | Bước 1, 4 đường tín hiệu thô xếp chồng | 4 dây · 1.000 mẫu/giây (ADFECGDB, CinC) |
| 2 | Lọc 10–60 Hz, chặn 50 Hz, hạ về 250 mẫu/giây | Bước 2, hàng trên | Tín hiệu đã lọc · (gộp với ô 3) |
| 3 | Khử tim mẹ: tìm nhịp mẹ, trừ mẫu trung vị | Bước 2, hàng dưới (phần dư) | Phần dư + **vị trí nhịp mẹ** · lọc + khử mẹ ≈ 6 ms cho bản 60 giây |
| 4 | Mạng TCN, 113.481 tham số, nhìn 1,5 giây, chạy trên cả 4 dây | Bước 3, đường xác suất tím + vạch ngưỡng cam | Xác suất từng mẫu + dãy nhịp · ≈ 0,13 s một dây, ≈ 0,5 s cả 4 dây (bản 60 giây) |
| 5 | Chọn dây mù nhãn (peakprob) | Bước 4, 4 dây thu nhỏ, dây được chọn viền đậm | Một dây · **viền cam** |
| 6 | Kết quả | Bước 5, đường nhịp tim theo thời gian | Dãy thời điểm nhịp + nhịp tim trung bình |
| 7 | Đèn tin cậy xanh / vàng / đỏ | Dải màu theo đoạn 4 giây | Mức đèn mỗi đoạn và cả bản · cổng ≈ 1 s cho bản 5 phút (75 đoạn) · **viền cam** |

Chi tiết phải vẽ đúng:
* **Mũi tên nét đứt màu cam** từ ô 4 sang ô 5, nhãn *"xác suất của mạng"*.
* **Mũi tên nét đứt màu cam** từ ô 4 sang ô 7, nhãn *"nhịp mạng tìm + xác suất của mạng"*.
* Dưới ô 7 một khung chú thích ba dòng: *"12 chỉ số mỗi đoạn 4 giây: 2 là xác suất của mạng · 4 tính trên nhịp mạng tìm ra · 6 thuần tín hiệu"*.
* **Ô phụ "Luật bám nhịp mẹ"** đặt dưới hàng chính, giữa ô 3 và ô 7. Mũi tên từ ô 3 (vị trí nhịp mẹ) và từ ô 4 (nhịp thai) vào ô phụ, rồi từ ô phụ lên ô 7. Nhãn ô phụ: *"≥ 60 % nhịp thai trùng nhịp mẹ (±50 ms) → đỏ"*.
* Ô 4 và ô 5 xếp đúng thứ tự demo: mạng chạy trên 4 dây **trước**, rồi mới chọn. Ghi chú nhỏ cạnh ô 5: *"quy tắc cũ PSD chọn trước mạng, không dùng xác suất"*.
* Góc dưới phải: câu cố định pháp lý.

### Demo thẻ r01 (70 giây)

**Chuẩn bị (làm trước buổi):** chạy `python demo/app.py`, mở `http://127.0.0.1:7860/gradio/` (chế độ trình bày; trang `/` là trang nghiên cứu HTML khác), thẻ *Ca dễ* (r01) tự chạy; dòng trạng thái ghi *⏳ Đang mở sẵn bản ghi r01 (Ca dễ) — khoảng 5–10 giây.* Lần đầu phải nạp mô hình nên lâu hơn: lần đo tự động ghi lúc 22:02 ngày 17/09 là 7,2 giây từ lúc mở trang đến khi r01 sẵn; đó là một lần đo, không dùng để kết luận demo nhanh hay chậm (`docs/HUONG_DAN_DEMO_v2.md` mục 2.5, 4.5). Giao diện sau lượt sửa thứ ba: tiêu đề *RelyFetal — tìm nhịp tim thai trong điện tim đo trên bụng mẹ, chỉ cần một kênh*, dòng dưới nói bản ghi thử có 4 kênh (4 "dây") và máy *báo "tôi không chắc" khi thấy dấu hiệu tín hiệu xấu (không phải lần nào cũng thấy)*; 5 thẻ có tên ca chữ to và mã bản ghi chữ nhỏ, *Ca dễ* · *Chọn dây quyết định* · *Máy bám nhầm tim mẹ* · *Bốn dây đều kém* · *Tệp của bạn*, dòng cuối mỗi thẻ *▶ Bấm để chạy (khoảng 5–10 giây)*; thanh 5 bước *Tín hiệu thô từ bụng mẹ* · *Lọc và khử tim mẹ* · *Mô hình tìm nhịp thai* · *Chọn đúng dây nào* · *Kết quả và độ tin cậy*; nút *◀ Quay lại* / *Tiếp ▶*, bấm là trang tự cuộn tới thanh 5 bước (chỉ khi thanh đó chưa nằm ở nửa trên màn hình); thanh tóm tắt dính đáy màn hình (cửa sổ rộng hơn 700 px): *Bản ghi* · *Bộ dữ liệu* · *Dây đã chọn* · *F1 (bắt đủ và báo đúng, 100 là hoàn hảo)* · *Nhịp tim thai trung bình* · *Đèn tin cậy*.

| Bước | Bấm | Nói |
|---|---|---|
| 1 · Tín hiệu thô từ bụng mẹ | — | "Đây là điện tim ghi ở bụng mẹ, dây 4. Ở dây này gai của bé to ngang gai của mẹ. Gai dày, đều, nhanh hơn là tim bé, khoảng 129 nhịp một phút. Gai thưa hơn là tim mẹ." |
| 2 · Lọc và khử tim mẹ | *Tiếp ▶* | "Máy tìm từng nhịp mẹ, vạch đỏ, rồi trừ đi. Hàng dưới là phần còn lại; vạch đen chấm là nhịp thai theo đáp án. Còn gai lớn trùng vạch đỏ thì đó là tim mẹ chưa trừ hết." |
| 3 · Mô hình tìm nhịp thai | *Tiếp ▶* | "Đường tím là mức tin của mạng. Vượt vạch cam thì tính là một nhịp; vạch tím đậm là nhịp mạng đã báo, chưa biết đúng hay sai. Hàng dưới mới so với đáp án: chấm xanh lá là đúng." |
| 4 · Chọn đúng dây nào | *Tiếp ▶* | "Mỗi dây cho một tín hiệu khác nhau. Bản này dễ: cách chọn mới và cách chọn cũ cùng chọn dây 4. Dây nào cũng cho F1 từ 99,84 trở lên." |
| 5 · Kết quả và độ tin cậy | *Tiếp ▶* | "F1 99,92, đèn xanh: cả 75 đoạn 4 giây đều xanh. Đây là bản dễ. Em giải thích F1 ngay đây." |

Không mở mục *Chi tiết kỹ thuật* ở bước 5. Không nói "gai lớn là tim mẹ, tim bé nhỏ hơn nhiều" ở r01: hộp *Cách đọc hình* của demo ghi *Ở dây này gai của bé to ngang gai của mẹ*, vì demo đo biên độ trên chính bản ghi. Câu chú thích bước 3 và hình đã thống nhất màu (vạch tím đậm), không còn chỗ lệch "vạch đỏ" / "xanh lá" như bản trước.

### [NÓI GÌ] — trên hình H2 (20 giây)

> "Hàng trên là nhịp thật, lấy từ đáp án. Quanh mỗi nhịp thật có một ô rộng cộng trừ 50 mili-giây.
>
> Máy báo một nhịp trong ô thì tính đúng. Ô trống là nhịp sót. Nhịp nằm ngoài mọi ô là nhịp thừa.
>
> F1 gộp sót và thừa thành một số từ 0 đến 100. Con số 50 mili-giây là quy ước chung để các bài so được, chưa phải ngưỡng lâm sàng.
>
> Bản r01 vừa rồi có 644 nhịp thật. Máy đúng 644, thừa 1, sót 0. Trên 22 sản phụ, trung bình là 97,56."

### [CHIẾU GÌ] — Hình H2: F1 và ±50 ms trên một hình

* Trục ngang thời gian dài **3 giây**, vạch chia mỗi 0,5 giây.
* **Hàng trên** (nhãn trái *"Nhịp thật (đáp án)"*): 7 vạch đen dọc, cách đều **430 ms** (tương ứng 140 nhịp/phút).
* Quanh mỗi vạch đen: **ô tô xanh nhạt rộng 100 ms** (±50 ms), cao phủ cả hai hàng. Vẽ đúng tỉ lệ: bề rộng ô bằng khoảng một phần tư khoảng cách hai nhịp.
* **Hàng dưới** (nhãn trái *"Nhịp máy báo"*): vạch xanh lá.
  * 6 vạch nằm trong 6 ô → dấu ✓ nhỏ, chữ *"đúng"* dưới vạch thứ nhất.
  * Ô thứ 7 không có vạch nào → chữ đỏ *"sót"* trong ô.
  * 1 vạch nằm giữa hai ô → vạch đỏ, chữ *"thừa"*.
* Khung bên phải, ba dòng chữ: *"Độ nhạy = đúng / (đúng + sót)"* · *"Độ chính xác dương = đúng / (đúng + thừa)"* · *"F1 = trung bình điều hoà hai số trên — cao khi ít sót và ít thừa"*. Dòng thứ tư, số của chính hình này: *"6 đúng, 1 sót, 1 thừa → độ nhạy 6/7, độ chính xác dương 6/7, F1 = 85,7"*.
* Dòng chân hình: *"±50 ms: quy ước của Behar 2014 và Andreotti 2016 để các bài so được với nhau."*

### Con số này nghĩa là gì

| Số | Quy đổi |
|---|---|
| ±50 ms | Ở 140 nhịp/phút, hai nhịp cách khoảng 430 ms. 50 ms bằng khoảng một phần chín quãng đó: đủ chặt để không tính nhầm sang nhịp bên cạnh. |
| F1 99,92 (r01) | 644 nhịp thật: 644 đúng, 1 thừa, 0 sót. |

### [NẾU CÓ HỎI]

**H: "Sao không dùng độ chính xác (accuracy) cho quen?"**
> "Vì phần lớn thời gian là không có nhịp. Một máy không báo nhịp nào vẫn 'đúng' ở phần lớn thời gian. F1 chỉ nhìn vào nhịp: sót bao nhiêu, thừa bao nhiêu."

*Chú thích:*
* [SỰ KIỆN] Front-end lọc và khử mẹ — `model/fqrs_model.py`. 113.481 tham số, trường tiếp nhận 1.516 ms — `survey/facts_verified.json → mo_hinh`.
* [SỰ KIỆN] 12 chỉ số — `fsqi/gate.py` dòng 61–78 (`segment_features` = 10 khoá `fsqi.CLASSICAL_KEYS` + `peak_prob_mean` + `prob_max`). Bốn khoá `n_det`, `rr_cv`, `rr_plaus`, `bsqi` tính trên `det` = nhịp mạng tìm ra — `fsqi/fsqi.py` dòng 307–318. Sáu khoá còn lại (`sampen`, `kurtosis`, `spec_entropy`, `band_ratio`, `psd_fhr`, `tau_acf`) tính trên tín hiệu; cùng cách chia ở `fsqi/eval_fsqi.py` dòng 50–51 (`SIGNAL_ONLY`, `MODEL_OUT`).
* [SỰ KIỆN] Quy tắc peakprob và PSD — `analysis/chonkenh_results.json → khai_bao_truoc.quy_tac_se_thu`. Luật bám mẹ 60 %, ngưỡng đèn bản ghi (đỏ khi > 30 % đoạn đỏ, xanh khi > 70 % đoạn xanh) — `demo/results/demo_check_showcase.json → gate.record_rule`, `fsqi/gate.py` dòng 14–15.
* [SỰ KIỆN] Thời gian bản 60 giây (a09): lọc + khử mẹ 6,2 ms, mạng một dây 129 ms, cả 4 dây 513 ms — `demo/results/demo_check_showcase.json → rows.a09_leadpeakprob.latency_*`. Cổng bản 5 phút (r01): 1.041 ms — `demo/results/demo_check_showcase.json → rows.r01_leadpeakprob.confidence.components.gate_ms`, cùng lần chạy với ba số trên (12/09, 2 luồng). Đây là lần chạy kiểm demo, chưa phải phép đo hiệu năng chuẩn. Lần chạy 13/09 (`demo_check_2modes.json`, 3 luồng, máy bận) ra 2.963 ms cho cùng bản; không trộn hai lần chạy trong một hình.
* [SỰ KIỆN] r01: TP 644, FP 1, FN 0, F1 99,92 — `demo/results/demo_check_showcase.json → rows.r01_leadpeakprob.metrics`. Dây 4 có cả `peakprob` cao nhất (0,9982) và `psd` cao nhất; F1 bốn dây 100,00 / 99,84 / 100,00 / 99,92; 75/75 đoạn xanh — `→ rows.r01_leadpeakprob.leads`, `.confidence.components`. Dung sai ±50 ms — Behar 2014 / Andreotti 2016 (`de_cuong_latex/tables/bang_baihoc.tex` p13, p15). 97,56 — `baselines/powermf_fair_stats.json → so_sanh.tat_ca_22.rely_vs_pmf4.mean_a`.
* [SUY LUẬN] Câu "máy không báo nhịp vẫn đúng phần lớn thời gian": với ô ±50 ms và nhịp cách 430 ms, ô nhịp chiếm khoảng 23 % thời gian (100/430). Nhóm tự tính, không có trong tệp.

---

## Khối 4 — Dữ liệu: bốn bộ, trong miền và ngoài miền (2 phút)

### [NÓI GÌ]

> "Em dùng bốn bộ dữ liệu công khai.
>
> ADFECGDB: năm sản phụ đang chuyển dạ, mỗi bản năm phút. Nhãn nhịp lấy từ điện cực da đầu bé. Em gọi là nhãn trực tiếp.
>
> Silesia B2: bảy sản phụ chuyển dạ, năm phút, cũng nhãn trực tiếp. Bộ gốc có mười hai bản. Năm bản trùng ADFECGDB nên em bỏ.
>
> Silesia B1: mười sản phụ chưa chuyển dạ, thai 32 đến 42 tuần, hai mươi phút mỗi bản. Nhãn do tác giả dò trên chính tín hiệu bụng. Em gọi là nhãn gián tiếp.
>
> Cộng lại 22 sản phụ. Em huấn luyện và kiểm theo kiểu để một người ra, lần lượt từng người.
>
> Điểm này quan trọng: em tính một điểm cho mỗi sản phụ, rồi mới lấy trung bình. Bốn dây của một người không phải bốn mẫu độc lập.
>
> Bộ thứ tư là CinC 2013 set-a: 75 bản, mỗi bản một phút. Bộ này gom từ nhiều nguồn, và ban tổ chức không công bố thiết bị ghi của từng bản. Em gọi là ngoài miền. Em chỉ dùng để kiểm.
>
> Toàn bộ cuộc thi 2013 có 447 bản. Ban tổ chức ghi từ 2013 rằng 25 bản lấy từ ADFECGDB. Họ không nói bản nào nằm ở tập nào. Em đo và định danh được 15 bản trong set-a là bản sao y nguyên. Em loại chúng, còn 60 bản sạch.
>
> Hai giới hạn. B1 chiếm 77 phần trăm thời lượng huấn luyện mà nhãn gián tiếp. Nên em không dùng B1 để nói về sai số thời điểm.
>
> Và dữ liệu chưa đại diện cho theo dõi tại nhà. Hai bộ là chuyển dạ, CinC chỉ một phút mỗi bản."

### [CHIẾU GÌ]

**Slide 8 — bảng bốn bộ:**

| Bộ | Sản phụ / bản | Giai đoạn · độ dài | Loại nhãn | Dùng làm gì | Điểm yếu |
|---|---|---|---|---|---|
| ADFECGDB (PhysioNet) | 5 | Chuyển dạ · 5 phút | Trực tiếp (da đầu) | Huấn luyện + kiểm, trong miền | Chỉ 5 người |
| Silesia B2 | 7 (bỏ 5 trùng ADFECGDB) | Chuyển dạ, 38–42 tuần · 5 phút | Trực tiếp (da đầu) | Huấn luyện + kiểm, trong miền | 5/12 bản trùng |
| Silesia B1 | 10 | Thai kỳ, 32–42 tuần · 20 phút | **Gián tiếp** | Huấn luyện + kiểm, trong miền | 77 % thời lượng, nhãn gián tiếp |
| CinC 2013 set-a | 60 bản sạch (75 − 15) | Không nêu · **1 phút** | Nhãn tham chiếu của ban tổ chức | **Chỉ kiểm**, ngoài miền | 15 bản trùng; số sản phụ thật không biết, nhiều nhất 60 |

Dưới bảng, hai cột: **"Đủ để chứng minh"** (mô hình một dây học được từ 22 người; B1 đóng góp thật ngoài miền) | **"Không đủ để chứng minh"** (tương đương bốn dây; nguyên nhân khoảng cách ngoài miền; quy tắc chọn dây tổng quát; theo dõi dài tại nhà).

### Con số này nghĩa là gì

| Số | Quy đổi |
|---|---|
| 22 sản phụ | Muốn kết luận "một dây tương đương bốn dây", nhóm ước cần khoảng 50: hơn gấp đôi hiện có. |
| 15 bản trùng | Chấm trên bản sao thì máy "đã thấy đề". Điểm cao hơn thật 3,27 đến 7,18 điểm. |

### [NẾU CÓ HỎI]

**H: "25 hay 15 bản trùng?"**
> "Cả hai đúng, ở hai phạm vi. 25 là số bản ADFECGDB trong toàn cuộc thi 447 bản. 15 là số bản em định danh được trong set-a, tập có nhãn công khai. 10 bản còn lại em suy luận nằm ở hai tập không công bố nhãn."

**H: "Sao không tăng số chủ thể bằng bộ khác?"**
> "Em đã kiểm bốn bộ nữa: NIFEADB, NInFEA, nifecgdb, CinC set-b. Không bộ nào có nhãn nhịp thai dùng được. Một bộ có tệp nhãn, nhưng đo ra 86 nhịp mỗi phút, tức nhịp mẹ. Thiếu dữ liệu có nhãn là trở ngại em không tự gỡ được. Em xin cô giúp ở cuối buổi."

*Chú thích:*
* [SỰ KIỆN] 22 = 5 + 7 + 10 — `analysis/DULIEU.md` §1.4, §4.1. B1 199,6 phút = 76,9 % — `analysis/DULIEU.md` dòng 585–588. B1 thai kỳ, B2 và ADFECGDB chuyển dạ — `analysis/DULIEU.md` dòng 307–308. Tuổi thai B1 32–42 tuần, B2 38–42 tuần — `survey/survey_raw.json` dòng 282 (mô tả bộ Matonia 2020). Nhãn B1 "tác giả khử ECG mẹ rồi dò QRS thai trên tín hiệu bụng" — `analysis/DULIEU.md` dòng 302–303. 5 bản B2 trùng ADFECGDB — `demo/results/demo_check_2modes.json → silesia_excluded_duplicates_of_adfecgdb`.
* [SỰ KIỆN] Để-một-chủ-thể-ra 22 fold — `analysis/chonkenh_results.json → meta.checkpoint_s22`, `analysis/gate22_results.json → thiet_ke.cv`.
* [SỰ KIỆN] 447 bản, 25 bản từ ADFECGDB, không nói bản nào ở tập nào — `survey/ro_ri_vanlieu.json` (Silva 2013 Bảng 1; Clifford 2014 Bảng 2; `ket_luan` dòng 45). 15 bản, NCC 1,0, lệch RR 0,0 ms, thổi phồng 3,27–7,18 — `facts_phase4.json → A_cinc2013_60_ban_sach`. [SUY LUẬN] 10 bản còn lại ở set-b/c — `survey/ro_ri_vanlieu.json → kiem_cheo_ky_thuat.so_hoc_25_ban`.
* [SỰ KIỆN] Số sản phụ thật trong 60 bản sạch không biết, nhiều nhất 60 — `survey/ro_ri_vanlieu.json → kiem_cheo_ky_thuat.cung_san_phu_khac_buoi`. [SUY LUẬN] Có thể ít hơn: NIFECGDB góp 14 bản từ một sản phụ vào cuộc thi, nhưng chưa có trường nào định danh 14 bản đó trong set-a, nên không nói "chắc chắn < 60" dù tệp nguồn có ghi câu đó. Bộ thứ ba không có, 86 nhịp/phút — `facts_phase4.json → C_xac_nhan_vong7.bo_thu_ba`. n ≈ 50 — `analysis/LUONGCUC.md` dòng 210.
* [SỰ KIỆN, giới hạn chưa kiểm] Hai lỗ hổng nhóm tự ghi, nói nếu bị hỏi: (1) chưa loại trừ một số sản phụ B1 và B2 là cùng một người ghi hai lần, nên "22 chủ thể độc lập" là giả định; (2) phép quét chồng lấn mới so CinC với ADFECGDB, chưa so CinC với 22 chủ thể Silesia — `analysis/DULIEU.md` dòng 670–676. Nhãn tham chiếu set-a được cung cấp cho người dự thi — `survey/ro_ri_vanlieu.json` dòng 43.

---

## Khối 5 — Năm bước kỹ thuật, mỗi bước một vì sao (1,5 phút)

### [NÓI GÌ]

> "Hình lúc nãy có năm bước. Em nói thêm vì sao cho từng bước.
>
> Lọc: dải 10 đến 60 héc, chạy hai chiều. Lọc một chiều làm trễ tín hiệu. Em đo thời điểm, nên không được trễ.
>
> Khử tim mẹ: dựng mẫu trung vị của nhịp mẹ, co giãn cho từng nhịp rồi trừ. Vì mẹ thở và cử động thì hình nhịp mẹ đổi.
>
> Mạng: mạng tích chập thời gian, 113.481 tham số, chưa tới nửa mê-ga-bai. Mạng nhìn 1,5 giây quanh mỗi điểm, khoảng ba đến bốn nhịp thai. Đầu ra là xác suất có nhịp tại từng mẫu. Nhờ vậy em đo được sai số thời điểm thật.
>
> Đèn tin cậy: một bộ phân loại chấm từng đoạn 4 giây bằng 12 chỉ số. Hai chỉ số là xác suất của mạng. Bốn chỉ số tính trên nhịp mạng tìm ra. Chỉ số quan trọng nhất là độ đều của nhịp mạng tìm ra.
>
> Nên đèn không độc lập với mạng. Khi mạng sai một cách tự tin, đèn có thể sai theo.
>
> Thêm một luật riêng: từ 60 phần trăm nhịp trở lên trùng nhịp mẹ thì đèn đỏ.
>
> Trên CPU máy tính, mạng chạy nhanh hơn thời gian thực khoảng 920 lần. Em chưa đo trên thiết bị đeo, chưa ước giá."

### [CHIẾU GÌ]

**Slide 9:** dùng lại H1, làm mờ ô 1–2 và ô 6, phóng to ô 3, 4, 5, 7. Cạnh mỗi ô một dòng "vì sao". Ô 7 có biểu đồ thanh ngang nhỏ: độ quan trọng hoán vị của 12 chỉ số, hai thanh dài là `rr_cv` 0,140 và `peak_prob_mean` 0,032, mười thanh còn lại gần bằng 0 (tô xám). Nếu mạng ổn và còn thời gian: chế độ chuyên gia, tab *Tín hiệu (5 tầng)* bản r01.

### Con số này nghĩa là gì

| Số | Quy đổi |
|---|---|
| 113.481 tham số · 0,48 MB | Chưa tới nửa mê-ga-bai. |
| 4,35 ms cho cửa sổ 4 giây | Xử lý 4 giây tín hiệu trong chưa tới 5 phần nghìn giây: nhanh hơn thời gian thực khoảng 920 lần, trên CPU máy tính, chưa trên thiết bị đeo. |
| 1.516 ms trường nhìn | Ở 140 nhịp/phút: khoảng 3,5 nhịp thai. |
| `rr_cv` 0,140 so với sáu chỉ số thuần tín hiệu < 0,002 | Xáo trộn độ đều nhịp làm cổng mất nhiều khả năng phân biệt nhất. Xáo trộn từng chỉ số thuần tín hiệu gần như không đổi gì. |

### [NẾU CÓ HỎI]

**H: "Lọc hai chiều cần toàn bộ tín hiệu. Thiết bị đeo thời gian thực làm sao?"**
> "Đúng, đây là hạn chế thật. Em xử lý theo khối, chưa theo dòng. Thời gian thực phải chấp nhận trễ vài giây. Em chưa đo ở chế độ khối trượt nên không hứa."

**H: "Đèn dùng xác suất của mạng thì khi mạng sai, đèn có sai theo không?"** → trả lời theo A16.

*Chú thích:*
* [SỰ KIỆN] Front-end và khử mẹ — `model/fqrs_model.py`. 113.481 tham số, 0,48 MB, 4,35 ms/cửa sổ, hệ số thời gian thực 920, trường tiếp nhận 1.516 ms — `survey/facts_verified.json → mo_hinh`. Sigma 12 ms — `analysis/kientruc_results.json → table.tcn.sigma_ms`.
* [SỰ KIỆN] Độ quan trọng hoán vị (cổng **22 ca**, phân tích) — `analysis/gate22_results.json → cong.permutation_importance_delta_auroc`: `rr_cv` 0,1404; `peak_prob_mean` 0,0318; mười khoá còn lại trị tuyệt đối đều dưới 0,002 (lớn nhất `prob_max` −0,0017, `psd_fhr` 0,0010). Cổng cũ trong demo dùng cùng 12 chỉ số (`demo/results/demo_check_2modes.json → gate.features`); độ quan trọng của cổng cũ chưa tìm thấy trên đĩa.
* [SỰ KIỆN] Chưa đo trên thiết bị đeo, chưa có phần cứng — `HANDOFF.md` §10 không có việc phần cứng; không có tệp đo nào.

---

## Những khái niệm cần hiểu trước (1 phút)

Đặt ngay trước phần kết quả. **Nói** phần dưới trong 1 phút; **bảng** dưới đây in lên slide 10–11 và tờ phát tay. Khái niệm nào được nói kỹ ở khối sau thì ghi cột cuối.

### [NÓI GÌ]

> "Trước khi vào kết quả, em xin một phút cho vài khái niệm. Chúng có trên tờ phát tay.
>
> Khoảng tin cậy 95 phần trăm là vùng giá trị thật có lẽ nằm trong, khi chỉ có 22 người. Khoảng chứa số 0 thì chưa khẳng định có khác biệt.
>
> Giá trị p trả lời: nếu hai hệ thật ra ngang nhau, chênh lệch cỡ này hay gặp đến đâu. p lớn thì chưa kết luận được.
>
> Thử nhiều quy tắc cùng lúc thì dễ có một cái thắng nhờ may. Em dùng hiệu chỉnh Holm để siết ngưỡng.
>
> Hậu kiểm là chọn sau khi đã nhìn kết quả. Nó là giả thuyết, chưa phải bằng chứng.
>
> Oracle là nhìn đáp án để chọn dây tốt nhất. Không thiết bị nào làm được. Em chỉ dùng nó làm trần."

### [CHIẾU GÌ] — Slide 10–11 và tờ phát tay

| Khái niệm | Lời thường | Ví dụ đời thường | Nói kỹ ở |
|---|---|---|---|
| **F1** | Máy sai hai kiểu: sót nhịp có thật, và báo nhịp không có. F1 gộp hai kiểu sai thành một số từ 0 đến 100. Không dùng độ chính xác vì phần lớn thời gian là "không có nhịp". | Điểm danh lớp 40 người. F1 hỏi: gọi đủ người có mặt chưa, và có gọi nhầm người vắng không. Đếm ghế trống đúng thì không nói lên gì. | Khối 3 (H2) |
| **±50 ms** | Nhịp máy báo được tính đúng nếu nằm trong 50 phần nghìn giây quanh nhịp thật. Đây là quy ước để các bài so được với nhau, chưa phải ngưỡng lâm sàng. Ở 140 nhịp/phút, 50 ms bằng khoảng một phần chín quãng giữa hai nhịp. | Bấm giờ chạy: về đích lệch vài phần trăm giây vẫn tính đúng vạch; lệch nửa giây là đã sang người khác. | Khối 3 (H2) |
| **Mức chủ thể** | Một sản phụ có bốn dây, nhưng bốn dây của cùng một người rất giống nhau. Đếm thành bốn mẫu là tự nhân bản bằng chứng. Nên tính một điểm cho mỗi người rồi mới lấy trung bình. | Hỏi ý kiến 22 gia đình về một món ăn: không đếm mỗi thành viên là một phiếu, vì cả nhà ăn chung một nồi. | Khối 4 |
| **Khoảng tin cậy 95 %** | Vùng mà giá trị thật có lẽ nằm trong, sau khi tính đến chuyện chỉ có 22 người. "−1,27 [−3,08; +0,27]" nghĩa là ước lượng thua 1,27, nhưng thật sự có thể thua hơn 3 hoặc hơn nhẹ 0,27. Khoảng chứa 0 thì chưa khẳng định có khác biệt. | Cân bao gạo trên cân cũ lệch nửa ký. Nói "9,5 đến 10,5 ký" trung thực hơn "10 ký". Nếu khoảng đó chứa con số người bán ghi, chưa thể nói họ cân gian. | Khối 6 |
| **p** | Nếu thật ra hai hệ ngang nhau, chênh lệch cỡ này vẫn xuất hiện bao thường xuyên chỉ do may rủi chọn người. p = 0,156 nghĩa là khoảng 16 lần trong 100: quá thường để kết luận có khác biệt. | Tung xúc xắc ra mặt sáu có khả năng khoảng 0,17. Chuyện đó xảy ra thường, không ai nói xúc xắc gian. | Khối 6 |
| **Holm** | Em thử bảy quy tắc cùng lúc. Thử càng nhiều, càng dễ có một cái "thắng" nhờ may. Holm siết ngưỡng: cái mạnh nhất phải qua ngưỡng chặt nhất, rồi nới dần. p sau hiệu chỉnh dưới 0,05 mới gọi là đạt. | Mua bảy tờ vé số thì dễ trúng một giải nhỏ hơn mua một tờ. Muốn nói mình giỏi chọn số, phải đòi mức trúng cao hơn hẳn. | Khối 8a |
| **Trong miền / ngoài miền** | Trong miền: dữ liệu cùng loại với lúc huấn luyện, nhưng khác người. Ngoài miền: dữ liệu từ bộ khác, có thể khác máy ghi, nơi ghi, cách đặt điện cực. Với CinC 2013, em chỉ kiểm được là không trùng dữ liệu huấn luyện; thiết bị của từng bản không được công bố. Mô hình thường tụt khi ra ngoài miền. | Học lái ở sân tập của trường, rồi lần đầu chạy ngoài phố giờ cao điểm. Cùng kỹ năng, kết quả khác hẳn. | Khối 4, 8c |
| **Hậu kiểm** | Quy tắc được chọn sau khi đã nhìn điểm trên chính tập kiểm. Con số tốt có thể một phần nhờ may của đúng 60 bản đó. Nên nó là giả thuyết, cần kiểm lại trên dữ liệu mới. | Bắn tên vào tường rồi mới vẽ bia quanh mũi tên: trúng hồng tâm, nhưng không ai tin đó là tài thiện xạ. | Khối 8a |
| **Oracle** | Nhìn đáp án rồi chọn dây tốt nhất cho từng bản. Không thiết bị nào làm được. Nó cho biết trần: chọn dây hoàn hảo thì được bao nhiêu. | Chọn đường về nhà sau khi đã biết đường nào tắc. Đó là trần, người lái thật không làm được. | Khối 8a |
| **gate / gate4 / peakprob** | Cả ba chọn một trong bốn dây mà không nhìn đáp án, và đều dùng đầu ra của mạng. **gate:** chọn dây có ít đoạn bị đèn chấm xấu nhất, với đèn học trên đoạn của một dây. **gate4:** cùng câu hỏi, nhưng đèn học trên đoạn của cả bốn dây. **peakprob:** không dùng đèn, chọn dây mà mạng tự tin nhất tại các nhịp nó tìm. gate và gate4 có trong danh sách ghi trước khi chạy (tệp chưa neo git); gate là quy tắc kế hoạch chọn và trượt Holm; việc chọn peakprob làm quy tắc chính diễn ra sau khi thấy kết quả, nên là hậu kiểm. | Chọn một trong bốn ứng viên. gate: hỏi người phỏng vấn chỉ quen một kiểu hồ sơ. gate4: hỏi người đã xem đủ bốn kiểu hồ sơ. peakprob: chọn người tự tin nhất khi trả lời. | Khối 8a |
| **89,49 %** | Thêm ba dây giúp Power-MF thêm 12,12 điểm so với chính nó chạy một dây. Mạng một dây của em cao hơn Power-MF một dây 10,85 điểm. 10,85 chia 12,12 là 89,49 %. Nó không nói một dây bằng bốn dây: em vẫn kém bốn dây 1,27. | Một đội bốn người khiêng hơn một người tay không 12 bao. Một người có dụng cụ tốt khiêng hơn người tay không gần 11 bao. Người đó bù được chín phần mười khoảng chênh, vẫn kém đội bốn người hơn 1 bao. | Khối 6 |

*Chú thích:*
* [SỰ KIỆN] Định nghĩa gate, gate4, peakprob, PSD, oracle — `analysis/chonkenh_results.json → khai_bao_truoc.quy_tac_se_thu` và `→ khai_bao_truoc.bo_sung_truoc_khi_chay_quy_tac.hai_bien_the_cua_quy_tac_b` (gate: huấn luyện chỉ trên đoạn của dây PSD; gate4: huấn luyện trên đoạn cả 4 dây). Hậu kiểm của peakprob — `HANDOFF.md` §8.3; `facts_phase4.json → B_chon_kenh_7_quy_tac_60_sach.trang_thai`, `→ B.khai_bao_truoc` ("không neo git, viết sau khi có F1 từng kênh").
* [SỰ KIỆN] 89,49 = 10,847 / 12,1212 — `analysis/recovery_ratio.json → phan_lay_lai_diem, gia_tri_da_kenh_diem, ti_le_pct`. Nhóm tự tính lại: 10,8470 / 12,1212 = 0,89488. 12,12 − 10,85 = 1,27, khớp hiệu RelyFetal − Power-MF 4 kênh.
* [SUY LUẬN] Ví dụ đời thường là minh hoạ, không có số đo đi kèm. Xúc xắc: 1/6 ≈ 0,167, gần p = 0,156.

---

## Khối 6 — Một dây so với bốn dây, đo được (2,5 phút)

### [NÓI GÌ]

> "Đây là phép đo chính. Cùng 22 sản phụ, cùng bộ chấm, cùng dung sai 50 mili-giây.
>
> Power-MF là phương pháp tách nguồn bốn điện cực, công bố năm 2024. Em chạy lại bằng mã của tác giả: 98,83.
>
> Cùng phương pháp đó, em cắt về một dây: 86,71.
>
> Mạng một dây của em: 97,56.
>
> So với bốn dây, em kém 1,27 điểm. Khoảng tin cậy từ âm 3,08 đến dương 0,27, chứa số 0. p bằng 0,156. Nên chưa khẳng định được là kém.
>
> Em hơn ở 18 trên 22 người. Nhưng có ba người em thua gần 10 đến gần 13 điểm. Họ kéo trung bình xuống.
>
> So với Power-MF một dây, em hơn 10,85 điểm, hơn ở cả 22 người.
>
> Ghép hai số lại. Thêm ba dây giúp Power-MF 12,12 điểm. Mạng một dây của em bù lại 10,85 trong số đó. Tức 89,49 phần trăm, khoảng tin cậy 81,4 đến 103,2.
>
> Cận trên vượt 100 nghĩa là dữ liệu chưa loại được khả năng bù đủ. Nó không có nghĩa một dây bằng bốn dây. Muốn kết luận tương đương, em ước cần khoảng 50 sản phụ."

### [CHIẾU GÌ]

**Slide 12 — bảng ba dòng:**

| Hệ thống | Số dây | F1, 22 sản phụ |
|---|---|---|
| Power-MF (chạy lại qua Octave) | 4 | **98,83** |
| Power-MF, nhóm tự cắt | 1 | **86,71** |
| RelyFetal | 1 | **97,56** |

Dưới bảng: *−1,27 [−3,08; +0,27], p 0,156, hơn 18 / kém 4* · *+10,85 [+6,80; +15,40], hơn 22 / kém 0* · *bù 89,49 % [81,4; 103,2]*.

**Hình H3 — 22 sản phụ, từng người một** (slide 13):
* Trục ngang: 22 sản phụ, xếp theo hiệu RelyFetal − Power-MF 4 dây, từ âm nhất (B1_07, −12,88) đến dương nhất (B1_03 và B2_04, +0,95).
* Trục dọc: F1 từ 40 đến 100.
* Mỗi người ba chấm nối bằng một đường dọc mảnh: tam giác xám = Power-MF 1 dây; vuông đen = Power-MF 4 dây; tròn xanh = RelyFetal.
* Tô đỏ nền cột của **4 người RelyFetal kém bốn dây**: B1_07 (−12,88), B1_06 (−10,51), B2_03 (−9,77), B1_10 (−1,86).
* Bên phải: một thanh ngang dài tương ứng 12,12 điểm, tô xanh đoạn 10,85, đoạn còn lại xám 1,27. Nhãn: *"bù 89,49 % [81,4; 103,2]"*. Vạch mảnh ở 81,4 % và 103,2 %; vạch 100 % nét đứt.

### Con số này nghĩa là gì

Quy đổi dùng: **100 − F1 xấp xỉ số nhịp sai trên 100 nhịp máy báo**, với giả định số nhịp sót và số nhịp thừa ngang nhau. Giả định này gần đúng với RelyFetal trên 22 sản phụ: sót 1.006, thừa 1.035. Với Power-MF, em chưa kiểm giả định này. Ví dụ dùng nhịp 140 lần/phút.

| Số | Quy đổi xấp xỉ | Tự tính |
|---|---|---|
| **97,56** | ≈ 2,4 nhịp sai trên 100; ≈ 3,4 nhịp sai mỗi phút | 100 − 97,56 = 2,44; 2,44 × 1,4 = 3,42 |
| **98,83** | ≈ 1,2 nhịp sai trên 100; ≈ 1,6 mỗi phút | 1,17; 1,64 |
| **−1,27** | Nhỏ trên thang F1, nhưng trên thang lỗi là **khoảng gấp đôi**: 2,44 so với 1,17. Khoảng tin cậy vẫn chứa 0 | 2,44 / 1,17 = 2,09 |
| **12,12** | Power-MF mất ba dây: từ ≈ 1,2 lên ≈ 13,3 nhịp sai trên 100, **gấp khoảng 11 lần** | 100 − 86,71 = 13,29; 13,29 / 1,17 = 11,4 |
| **+10,85** | Cùng một dây, cùng 22 người: từ ≈ 13,3 xuống ≈ 2,4 nhịp sai trên 100, **giảm khoảng 5 lần** | 13,29 / 2,44 = 5,4 |
| **89,49 %** | Xem thanh ngang ở H3 | 10,85 / 12,12 |
| **p 0,156** | Khoảng 16 lần trong 100 lần lặp lại, chỉ do may rủi chọn người | — |
| **18 / 22** | Hơn ở 18 người, nhưng hơn rất ít: trung vị chỉ +0,23. Ba người kém gần 10 đến 13 điểm | Hiệu từng người, `per_subject` |
| **Cần ≈ 50** | Hơn gấp đôi 22 | 50 / 22 = 2,3 |

**Nói thẳng:** em chưa biết mức 2 đến 3 nhịp sai trên 100 có đủ cho chỉ số biến thiên lâm sàng hay không.

### [NẾU CÓ HỎI]

**H: "Hơn 18/22 mà trung bình vẫn kém. Nên tin số nào?"**
> "Cả hai, vì chúng nói hai chuyện. Trung vị dương 0,23 nghĩa là ở bản thường em ngang hoặc hơn chút ít. Trung bình âm 1,27 nghĩa là ở vài bản khó em thua đậm. Bốn người em kém cũng là bốn người cổng 22 ca trong phân tích xếp đáng ngờ nhất. Em báo cả hai số."

**H: "Khoảng tin cậy chạm 103 %. Con số 89,5 còn nghĩa gì?"** → A3.

*Chú thích:*
* [SỰ KIỆN] Mọi số F1 và hiệu — `baselines/powermf_fair_stats.json → so_sanh.tat_ca_22` (rely_vs_pmf4: −1,2743 [−3,0759; +0,2651], p 0,1560, 18/0/4; rely_vs_pmf1: +10,8470 [+6,8008; +15,3994], 22/0/0; pmf1_vs_pmf4: −12,1212 [−18,2721; −6,9018]). Trung vị +0,23 và hiệu từng người — nhóm tự tính từ `→ per_subject` (trung vị đúng +0,23). Tỉ lệ 89,49 [81,4; 103,16] — `analysis/recovery_ratio.json`. n ≈ 50 — `analysis/LUONGCUC.md` dòng 210.
* [SỰ KIỆN] Sót 1.006, thừa 1.035, đúng 35.307 — `analysis/chandoan_results.json → pho_loi.22_chu_the_kenh_PSD.n_FN, n_FP, n_TP`.
* [SỰ KIỆN] Bốn người kém trùng top 4 của cổng 22 ca — `analysis/gate22_results.json → muc_ban_ghi.top4` = B2_03, B1_07, B1_06, B1_10.
* [SUY LUẬN] Mọi phép quy đổi trong hộp là nhóm tự tính, chỉ đúng xấp xỉ dưới giả định sót ≈ thừa.

---

## Khối 7 — Đối chuẩn công bằng đến đâu (2 phút)

### [NÓI GÌ]

> "Ai em chạy lại, ai em chỉ trích số.
>
> Chạy lại: Power-MF bốn dây, bằng mã gốc của tác giả, qua Octave. Power-MF một dây, em tự cắt. Ba phương pháp cổ điển, em cài lại theo mô tả. Chỉ trích số: DPSS, CUNet, Castillo, Behar, Varanini.
>
> Công bằng đến đâu. Công bằng nhất là Power-MF một dây: cùng dây, cùng lọc, cùng 22 người, cùng bộ chấm. Ở đó em hơn 10,85. Nhưng bản cắt đó là của em, tác giả chưa xác nhận.
>
> Power-MF bốn dây khác đúng số dây. Ở đó em kém 1,27.
>
> Trên 60 bản CinC sạch, số tác giả Power-MF bốn dây, em lọc lại, là 93,12. Mạng của em ở 74,28 với quy tắc chọn dây cũ. 80,72 với quy tắc em chọn trong kế hoạch trước khi chạy, và nó trượt hiệu chỉnh. 81,01 với biến thể gate4, cũng ghi trước khi chạy. 82,01 với quy tắc hậu kiểm. Trần là 83,60. Chỗ này không ủng hộ em, em nói luôn.
>
> Power-MF một dây trên cùng 60 bản chỉ 55,97. Nên phần lớn khoảng cách là do nhiều dây.
>
> Câu chuyện Power-MF. Lần chạy lại trước, sáu trên mười bản B1 hỏng. Em đoán do tham số khoảng cách tối thiểu 340 mili-giây. Em đo trên 27 bản: khoảng nhịp ngắn hơn 340 nhiều nhất chỉ 0,15 phần trăm. Đoán sai.
>
> Nguyên nhân thật: hàm tìm đỉnh trong Octave tốn bộ nhớ theo bình phương, tràn ở bản dài. Vá xong, B1 ra 99,40. Tác giả công bố 99,46.
>
> Nếu không vá, em đã so với một Power-MF hỏng và thắng oan trên B1. DPSS em chưa chạy lại, nó đang ở đúng vị trí Power-MF trước bản vá."

### [CHIẾU GÌ]

**Slide 14** — bảng hai khối: *"Chạy lại"* (Power-MF 4 dây · Power-MF 1 dây · TS · TS-PCA · Prominence) | *"Chỉ trích số"* (DPSS · CUNet · Castillo · Behar · Varanini), cột *"Công bằng?"* ba mức: công bằng nhất / đủ công bằng / chỉ tham khảo.

**Slide 15 — ngoài miền, một dây so với bốn dây** (đọc đoạn "Trên 60 bản CinC sạch…" ở trên khi chiếu slide này): bảy thanh F1 trên 60 bản CinC sạch, *Power-MF 4 dây · số tác giả, em lọc 93,12* · *Trần: chọn dây nhìn đáp án 83,60* · *peakprob, hậu kiểm 82,01* · *gate4, cũng ghi trước 81,01* · *gate, trượt Holm 80,72* · *PSD, quy tắc cũ 74,28* · *Power-MF 1 dây 55,97*; bảng nhỏ hai cột trong miền 22 / ngoài miền 60: Power-MF 4 dây 98,83 / 93,12; RelyFetal 1 dây 97,56 / 74,28 · 80,72 · 81,01 · 82,01; Power-MF 1 dây 86,71 / 55,97; *4 dây hơn em* 1,27 / ≈ 11 đến 19. Hai hộp: *"Chỗ này không ủng hộ em"* (không tính tỉ lệ bù ngoài miền vì 93,12 chấm bằng bộ chấm của tác giả) và *"Phần lớn khoảng cách là do nhiều dây"*.

**Slide 16** — ba ô nối mũi tên: *giả thuyết 340 ms* → *phép đo trên 27 bản: RR < 340 ms nhiều nhất 0,15 %* → *nguyên nhân thật: hàm tìm đỉnh tràn bộ nhớ ở bản dài*. Ô cuối có dòng *"sau vá: 99,40 · tác giả: 99,46"*.

### [NẾU CÓ HỎI]

**H: "Em tự cắt Power-MF về một dây. Có làm hỏng phương pháp của họ không?"**
> "Em cắt ở đầu vào, giữ nguyên các bước còn lại, bỏ hai bước ICA vì cần nhiều dây. Em ghi rõ trong bài số một dây là do em cắt. Nếu cô thấy cách cắt khác công bằng hơn, em làm lại."

**H: "Nếu Octave có lỗi như vậy, kết quả chạy lại có tin được không?"** → A10.

*Chú thích:*
* [SỰ KIỆN] Bảng chạy lại / trích — `docs/CONG_BANG_DOI_CHUAN.md` Bảng 1. TS 87,68 / TS-PCA 96,74 / Prominence 92,03 (5 chủ thể, kênh PSD) — `baselines/results.json`.
* [SỰ KIỆN, số dẫn xuất] Power-MF 4 dây trên 60 sạch 93,12 — nhóm lọc từ số từng bản của tác giả, `baselines/powermf_published.json → challenge_powermf`; `docs/CONG_BANG_DOI_CHUAN.md` dòng 33. Chưa có trong facts_phase4.
* [SỰ KIỆN] Power-MF 1 dây 60 sạch 55,97 [48,08; 64,03] — `facts_phase4.json → A.powermf_1ch_60_sach`. Bốn quy tắc và trần — `→ B_chon_kenh_7_quy_tac_60_sach` (psd 74,28; gate_chi_dinh_truoc 80,72, Holm 0,051; gate4 81,01, Holm 0,015; peakprob_hau_kiem 82,01; oracle_F1 83,6); cùng số ở `analysis/dulieu_results.json → chon_kenh_60_sach.bang`. gate là quy tắc kế hoạch chọn — `analysis/chonkenh_results.json → khai_bao_truoc.quy_tac_quyet_dinh_chinh`, `→ quyet_dinh.tot_nhat_theo_22`.
* [SỰ KIỆN] 6/10 bản B1 hỏng, tỉ lệ RR < 340 ms lớn nhất 0,15 % trên 27 bản, bản vá P7, 99,40 so với 99,46 — `baselines/BASELINES.md` dòng 16, 31, 60–76; `baselines/powermf_published.json → b1_powermf`.
* Câu cũ "thắng oan chín điểm" đã bỏ: con số đó ghép trung bình B1 của bản hỏng (6 bản) với số của RelyFetal, không có trường nguồn. DPSS chưa chạy lại — `HANDOFF.md` §10 #6.

---

## Khối 8 — Kết quả, kèm demo (6 phút)

### 8a — Ngoài miền: chọn dây (1,5 phút nói + 1,25 phút demo a09)

#### [NÓI GÌ]

> "Giờ ra ngoài miền: 60 bản CinC sạch. Mạng không được tinh chỉnh gì trên bộ này.
>
> Vấn đề lớn nhất là chọn dây. Cùng một sản phụ, bốn dây cho chất lượng rất khác nhau. Thiết bị phải tự chọn, không có đáp án.
>
> Em so bảy quy tắc. Em nói bốn quy tắc và một mốc trần.
>
> Quy tắc cũ, theo Power-MF, chọn dây có phổ nhịp mạnh nhất: 74,28.
>
> Quy tắc em chọn trong kế hoạch, ghi trước khi chạy, là gate: chọn dây có ít đoạn bị đèn chấm xấu nhất, với đèn học trên đoạn của một dây. Được 80,72. p sau hiệu chỉnh Holm là 0,051. Theo luật em tự đặt, nó trượt.
>
> Gate4 là biến thể cũng ghi trước khi chạy, đèn học trên đoạn của cả bốn dây: 81,01. p sau Holm bằng 0,015, đạt. Nhưng nó không phải quy tắc kế hoạch chọn.
>
> Peakprob chọn dây mà mạng tự tin nhất tại các nhịp nó tìm: 82,01. Nó có trong danh sách ghi trước, nhưng em chọn nó làm mặc định sau khi đã thấy kết quả. Nên nó là giả thuyết.
>
> Trần, nếu nhìn đáp án chọn dây tốt nhất: 83,60."

#### Demo thẻ *Chọn dây quyết định* (a09) (1,25 phút)

Bấm thẻ *Chọn dây quyết định* (mã nhỏ *bản ghi a09 · CinC 2013*). Thẻ ghi *Cùng một bản ghi, đổi cách chọn dây thì kết quả đổi hẳn*, số lớn *19,35 → 94,25*. Bước 1–3 lướt, mỗi bước một câu. Dừng lâu ở **bước 4**.

| Bước | Nói |
|---|---|
| 1 · Tín hiệu thô | "Bản CinC 2013, không trùng dữ liệu huấn luyện. Ở dây này gai lớn đều đặn là tim mẹ; gai của bé nhỏ hơn nhiều." |
| 2 · Lọc và khử mẹ | "Vẫn quy trình đó: tìm tim mẹ, trừ đi." |
| 3 · Mô hình tìm nhịp | "Mạng vẫn tìm được nhịp. Giờ xem nó chọn dây nào." |
| **4 · Chọn đúng dây nào** | Màn hình ghi *Cách chọn mới (peakprob: dây mà mạng tự tin nhất)* chọn dây 1, *Cách chọn cũ (PSD: dây có năng lượng mạnh nhất ở dải nhịp tim thai 1,8–3 Hz, như Power-MF)* chọn dây 2, *Hai cách chọn khác dây, và kết quả khác hẳn.* <br>"Cùng một sản phụ, mỗi dây cho một tín hiệu khác nhau." · "Cách chọn cũ chọn dây 2: F1 19,35. Cách chọn mới chọn dây 1: F1 94,25." · "Gate và gate4, hai quy tắc ghi trước khi chạy, cũng chọn dây 1 ở bản này." · "Máy chọn mà không nhìn đáp án. Số F1 chỉ chấm sau khi đã chọn." |
| 5 · Kết quả và độ tin cậy | "F1 94,25, đèn xanh." · Chỉ dòng dưới thanh tóm tắt, dòng này ghi đủ năm số 74,28 · 80,72 · 81,01 · 82,01 · 83,60: "Thanh dưới ghi lại năm số em vừa nói: cách cũ, gate theo kế hoạch, gate4, cách demo đang dùng chọn sau khi xem kết quả, và trần." · "a09 là bản em chọn để minh hoạ, nó không đại diện cho trung bình." |

#### [CHIẾU GÌ] — Hình H4: 60 bản ngoài miền, bốn quy tắc và trần (slide 17, trước demo; slide 18 là trang chuyển sang demo a09)

* **Nửa trái — F1 tuyệt đối.** Năm thanh ngang, từ trên xuống: *PSD (cũ) 74,28* · *gate (quy tắc kế hoạch chọn, ghi trước khi chạy) 80,72* · *gate4 (cũng ghi trước khi chạy) 81,01* · *peakprob (hậu kiểm: chọn làm mặc định sau khi xem kết quả) 82,01* · *oracle (trần) 83,60*. Thanh PSD có râu khoảng tin cậy [66,63; 81,78]; thanh oracle có râu [77,57; 89,17]. Ba thanh giữa không vẽ râu (tệp chỉ có khoảng tin cậy của hiệu). Màu: PSD xám; gate và gate4 xanh dương; peakprob cam, nền sọc chéo; oracle viền nét đứt, không tô.
* **Nửa phải — hiệu so với PSD**, có râu khoảng tin cậy: gate +6,44 [+2,49; +11,10] · gate4 +6,72 [+2,85; +11,18] · peakprob +7,73 [+3,82; +12,41]. Cạnh mỗi thanh: *p Holm 0,051 — trượt* · *0,015 — đạt* · *0,0039 — hậu kiểm, không tính là bằng chứng*.
* Cột nhỏ bên phải: *số bản F1 < 50 trên 60*: 16 · 12 · 12 · 9 · 8.
* Không vẽ 93,12 của Power-MF 4 dây ở hình này.

#### Con số này nghĩa là gì

| Số | Quy đổi xấp xỉ | Tự tính |
|---|---|---|
| 74,28 → 80,72 → 81,01 → 82,01 → 83,60 | ≈ 26 → 19 → 19 → 18 → 16 nhịp sai trên 100 (giả định sót ≈ thừa, **chưa kiểm trên 60 bản**) | 25,72 · 19,28 · 18,99 · 17,99 · 16,40 |
| Bản F1 < 50: 16 → 12 → 12 → 9 → 8 trên 60 | Từ khoảng 1 bản trong 4 xuống khoảng 1 bản trong 7 | 16/60 = 27 %; 9/60 = 15 % |
| peakprob 82,92 % dư địa | Đi được hơn bốn phần năm quãng từ quy tắc cũ tới trần | Tệp nguồn |
| +7,73 [+3,82; +12,41] | Cùng cỡ với mức thổi phồng do 15 bản trùng, 3,27–7,18. Vì vậy phải loại 15 bản **trước** khi so quy tắc | — |
| p Holm 0,051 | Ngưỡng 0,05 là luật tự đặt. 0,051 là trượt, không làm tròn, không gọi là "gần đạt" | — |

#### [NẾU CÓ HỎI]

**H: "Luật em chỉ định trước trượt, rồi em nêu một quy tắc khác đạt. Có phải cái nào đạt thì lấy?"**
> "Câu này đúng chỗ đau nhất. Gate là quy tắc em chỉ định. Gate4 là biến thể em ghi thêm vào tệp khai báo, trước khi chạy quy tắc nào. Holm tính trên cả bảy. Nhưng tệp khai báo chưa neo vào lịch sử mã, và viết sau khi đã có F1 từng dây. Nên em báo cả ba số theo đúng thứ tự. Nếu chỉ giữ một kết luận, em giữ kết quả gate trượt."

**H: "Ba bản demo là bản đẹp để kể chuyện?"** → A19.

*Chú thích:*
* [SỰ KIỆN] Bảng bảy quy tắc — `facts_phase4.json → B_chon_kenh_7_quy_tac_60_sach` (psd 74,28, lt50 16; gate 80,72, +6,44 [2,49; 11,10], Holm 0,051, lt50 12; gate4 81,01, +6,72 [2,85; 11,18], Holm 0,015, lt50 12; rrcv 80,00; peakprob 82,01, +7,73 [3,82; 12,41], Holm 0,0039, 19/6/35, lt50 9; oracle 83,6; dư địa 82,92). Khoảng tin cậy tuyệt đối của PSD và oracle — `→ A_cinc2013_60_ban_sach.psd.m22_ci95`, `→ oracle.m22_ci95`, oracle lt50 8.
* [SỰ KIỆN] Gate4 thêm trước khi chạy quy tắc — `analysis/chonkenh_results.json → khai_bao_truoc.bo_sung_truoc_khi_chay_quy_tac`; tệp không neo git — `facts_phase4.json → B.khai_bao_truoc`. gate là quy tắc kế hoạch chọn: thủ tục chọn quy tắc tốt nhất trên 22 chủ thể rồi kiểm trên CinC — `→ khai_bao_truoc.quy_tac_quyet_dinh_chinh`; gate đứng đầu trên 22 chủ thể — `→ quyet_dinh.tot_nhat_theo_22`. peakprob có trong `→ khai_bao_truoc.quy_tac_se_thu`, được chọn làm mặc định sau khi xem CinC — `→ quyet_dinh.tot_nhat_theo_cinc_hau_kiem`, `facts_phase4.json → B.trang_thai`.
* [SỰ KIỆN] a09: PSD chọn dây 2 (F1 19,35); peakprob, gate4, gate, rrcv, rrplaus, learned chọn dây 1 (F1 94,25) — `analysis/chonkenh_results.json → chon_kenh_theo_quy_tac.cinc.a09` (chỉ số 0 = dây 1), `→ F1_tung_ban_ghi.cinc.a09`; `demo/results/demo_check_showcase.json → rows.a09_leadpeakprob.leads`. Đừng trích F1 98,46 của a09 (30 giây đầu, `HANDOFF.md` §8.4).
* [SUY LUẬN] Quy đổi lỗi trên 100 là nhóm tự tính.

### 8b — Đèn tin cậy học từ đâu (1 phút nói + 1,25 phút demo a02 + 0,5 phút demo a27)

#### [NÓI GÌ]

> "Phần thứ hai: đèn tin cậy học từ đâu.
>
> Em cắt tín hiệu thành đoạn 4 giây. Đoạn nào máy chấm F1 dưới 80 thì dán nhãn xấu. Trên 22 sản phụ, 5,4 phần trăm số đoạn là xấu.
>
> Một bộ phân loại học từ 12 chỉ số để đoán đoạn xấu, không cần đáp án. Như em đã nói, 6 trong 12 chỉ số lấy từ đầu ra của mạng.
>
> Có hai phiên bản cổng. Đèn trong demo là cổng cũ, học trên mô hình năm sản phụ. Ghép với mô hình năm sản phụ đó, nó xếp đoạn xấu trong cùng bản ghi với diện tích dưới đường cong 0,72, đo trên 5 bản CinC. Khoảng tin cậy rất rộng. Demo hiện ghép cổng này với mô hình 22 sản phụ; cấu hình đó em chưa đo lại.
>
> Cổng mới học trên 22 sản phụ đạt 0,93. Nhưng nó mới ở dạng phân tích, chưa đưa vào demo. Và chỉ tính được trên 11 người có đoạn xấu."

#### Demo thẻ *Máy bám nhầm tim mẹ* (a02) (1,25 phút)

Bấm thẻ *Máy bám nhầm tim mẹ* (mã nhỏ *bản ghi a02 · CinC 2013*). Thẻ ghi *78 % nhịp máy báo trùng nhịp mẹ. Máy báo nhịp tim 130: trông bình thường, nhưng đáp án ≈ 160.*, số lớn *F1 24,91 · đèn ĐỎ*. Nhìn thanh tóm tắt trước: đèn *THẤP (đỏ)*; ô *Nhịp tim thai trung bình* bị gạch ngang, kèm chữ *đèn đỏ: không dùng số này*.

| Bước | Hộp *Con số cần nhớ* trên màn hình | Nói |
|---|---|---|
| 1 · Tín hiệu thô | *Tim mẹ ≈ 124 nhịp/phút. Theo đáp án, tim bé ≈ 160 nhịp/phút; máy đếm được ≈ 130, không tin được (xem bước 5).* | "Một bản CinC khác, cũng ngoài miền. Theo đáp án tim bé khoảng 160; máy đếm được 130, và chính máy ghi là không tin được." |
| 2 · Lọc và khử mẹ | *Tìm được 124 nhịp mẹ trong 60 giây (≈ 124 nhịp/phút) và trừ chúng đi.* | "Ở bản này, phần dư sau khi trừ tim mẹ vẫn còn dấu vết nhịp mẹ." |
| 3 · Mô hình tìm nhịp | *Mạng báo 129 nhịp "thai", nhưng 78 % trùng thời điểm nhịp mẹ: mạng đang bám nhầm tim mẹ. Chỉ đỉnh vượt ngưỡng 0,75 mới được tính.* | "Mạng tìm ra nhịp khá đều. Nhưng 78 phần trăm số nhịp đó trùng nhịp mẹ: mạng đang bám nhầm tim mẹ." |
| **4 · Chọn đúng dây nào** (hộp vàng *Lưu ý trung thực — chọn chưa đúng dây* hiện) | *Cả hai cách cùng chọn dây 2 (F1 24,91).* | Chỉ vào hộp vàng: "Ở bản này, dây 1 đạt F1 75,88. Ba dây còn lại đều dưới 25." · "Em so bảy cách chọn không nhìn đáp án. Sáu cách chọn dây 2, kể cả cách cũ, gate và gate4. Cách thứ bảy chọn dây 3. Không cách nào chọn dây 1." · "Mạng tự tin nhất ở dây 2. Em đoán vì nhịp mẹ ở đó rõ và đều." · "Đây là giới hạn thật của cách chọn dựa vào độ tự tin của mạng." |
| **5 · Kết quả và độ tin cậy** | *F1 24,91 · đèn THẤP (đỏ) · 0 đoạn xanh, 9 vàng, 6 đỏ trên 15 đoạn 4 giây · 78 % nhịp "thai" trùng nhịp mẹ · máy báo 130 nhịp/phút nhưng theo đáp án ≈ 160.* | "Máy tính ra nhịp tim trung bình 130, nằm trong vùng bình thường. Đáp án là 160." · "F1 chỉ 24,91." · "Máy không đưa con số này cho người đọc. Sáu trên mười lăm đoạn bị đánh đỏ, tức 40 phần trăm, quá mức 30. Luật bám nhịp mẹ cũng bật." · "Hình ghi *TB 130 nhịp/phút (đèn đỏ: không dùng)*; ô nhịp tim bị gạch." |

Không mở *Chi tiết kỹ thuật*. Nếu bị hỏi "vậy sao không chọn dây 1": trả lời theo **A3-bis** (60 giây).

#### Demo thẻ *Bốn dây đều kém* (a27) (0,5 phút)

Bấm thẻ *Bốn dây đều kém* (mã nhỏ *bản ghi a27 · CinC 2013*). Thẻ ghi *F1 từng dây chỉ 21,26–32,94. Hệ thống từ chối 14/15 đoạn thay vì đoán.*, số lớn *F1 32,94 · đèn ĐỎ*. Bấm *Tiếp ▶* thẳng đến bước 5.

> "Bản này cả bốn dây đều kém, F1 từ 21 đến 33. Máy chọn đúng dây khá nhất trong bốn, F1 32,94. Mười bốn trên mười lăm đoạn bị đánh đỏ. Ô nhịp tim bị gạch: máy không đưa ra con số trông như thật."

Không nói "bản này không có tín hiệu thai": nhóm chưa đo điều đó.

#### [CHIẾU GÌ] — Slide 19 (trước demo a02; slide 20 là trang chuyển sang demo a02 và a27, slide 21 là slide dự phòng cho A3-bis)

Hai cột bằng nhau:

| Cổng cũ — **đang chạy trong demo** | Cổng 22 ca — **chỉ ở dạng phân tích** |
|---|---|
| Học trên mô hình 5 sản phụ ADFECGDB, 4 dây | Học trên 22 sản phụ, để-một-người-ra |
| AUROC trong bản ghi **0,721 [0,517; 0,898]**, đo trên 5 bản CinC khi ghép với mô hình 5 ca; ghép với mô hình 22 ca đang chạy: **chưa đo lại** | AUROC trong bản ghi **0,934 [0,872; 0,981]**, tính trên **11/22** người có đoạn xấu |
| Tệp `fsqi/gate_classical.pkl` | Chưa xuất thành tệp, chưa thay vào demo |

Dòng dưới: *"Cả hai: 12 chỉ số, 6 lấy từ đầu ra của mạng · Luật riêng: ≥ 60 % nhịp trùng nhịp mẹ → đỏ"*. Dòng dưới nữa: *"Xếp đúng 3 người khó nhất (ngẫu nhiên 1/1540) — nhưng 5/24 quy tắc một chỉ số cũng làm được."*

#### Con số này nghĩa là gì

| Số | Quy đổi |
|---|---|
| AUROC 0,5 / 1,0 | 0,5 là tung đồng xu, 1,0 là xếp hoàn hảo. |
| 0,721 (cổng trong demo, đo khi ghép mô hình 5 ca; ghép mô hình 22 ca chưa đo lại) | Lấy một đoạn xấu và một đoạn tốt trong cùng một bản: cổng xếp đoạn xấu đáng ngờ hơn khoảng 72 lần trên 100. Khoảng tin cậy chạm gần mức đồng xu. |
| 0,934 (cổng 22 ca) | Khoảng 93 lần trên 100, nhưng chỉ trên 11 người. |
| 5,4 % đoạn xấu | Khoảng 1 đoạn trong 19. |
| 1/1540 | Số cách chọn 3 người trong 22 là 1.540. Như rút đúng ba lá bài định trước từ bộ 22 lá. Nói ngay kèm "5/24". |
| Bỏ 3 người cổng 22 ca xếp đáng ngờ nhất | RelyFetal 99,50 so với Power-MF 4 dây 99,23, hiệu +0,27 [−0,02; +0,48]. Giữ lại 86,4 % số người, 82,7 % thời lượng. |
| a02: máy 130, đáp án 160 | Máy báo thấp hơn thật 30 nhịp/phút, mà con số vẫn nằm trong dải xanh *vùng bình thường 110–160 nhịp/phút* trên hình bước 5, và trong dải 100–200 mà chế độ luật của demo coi là hợp lý. Nhìn con số thì không thấy sai. Đây là kiểu sai nguy hiểm nếu không có đèn. |

#### [NẾU CÓ HỎI]

**H: "Cổng từ chối bao nhiêu phần trăm dữ liệu? Từ chối nhiều thì số nào cũng đẹp."**
> "Đúng. Nên các số chính 97,56 và 74,28, 80,72, 81,01, 82,01 đều tính không qua cổng. Trong demo, trên 82 bản, đèn xanh ở 46 bản, tức 56 phần trăm. Không đỏ ở 63 bản, tức 77 phần trăm."

**H: "Con số 0,934 có phải của chính cái đèn trong demo không?"** → A17.

*Chú thích:*
* [SỰ KIỆN] Nhãn đoạn xấu F1 < 80, tỉ lệ 5,40 %, 3.890 đoạn — `analysis/gate22_results.json → thiet_ke.bad_threshold_F1`, `→ cong.frac_bad, n_segments`.
* [SỰ KIỆN] Cổng cũ: `fsqi/gate_classical.pkl`, "ADFECGDB r01,r04,r07,r08,r10 x 4 kênh" — `demo/results/demo_check_2modes.json → gate.trained_on`, `→ gate_note`. AUROC trong bản ghi 0,721 [0,517; 0,898], trung bình trên 5 bản có cả hai loại đoạn (a01 a06 a07 a09 a10, đều thuộc 60 bản sạch, lấy từ mẫu a01–a10), đo khi cổng ghép với mô hình 5 ca — `analysis/stats_results.json → comparisons.gate_auroc_cinc.auroc_TRONG_ban_ghi` (`trung_binh`, `ci95_bootstrap`, `n_ban_ghi_co_ca_2_lop` 5), `→ .auroc_tung_ban_ghi`; `analysis/GATE22.md` dòng 69–71. Ghép với mô hình 22 ca đang chạy: chưa đo lại (`demo/app.py → STORY_GATE_NOTE`). Không dùng số gộp 0,929 của cùng phép đo: tính trên a01–a10, có 4 bản nhiễm.
* [SỰ KIỆN] Cổng 22 ca: 0,9336 [0,8717; 0,9810], 11 bản có cả hai lớp — `analysis/gate22_results.json → cong.auroc_within_mean, auroc_within_ci, n_records_with_both_classes`. "Chỉ tồn tại dưới dạng kết quả phân tích" — `analysis/GATE22.md` dòng 364–366. 1/1540 và 5/24 — `analysis/GATE22.md` dòng 127, 304; `→ muc_ban_ghi.so_quy_tac_mot_dac_trung_bat_du_3` = 5. Bỏ 3 người: `→ rui_ro_do_phu_ban_ghi.do_phu_dau_tien_hieu_khong_am` (99,50 / 99,23 / +0,2697 [−0,0229; +0,4850] / 86,36 % / 82,70 %).
* [SỰ KIỆN] a02 — `demo/results/demo_check_showcase.json → rows.a02_leadpeakprob`: dây chọn 2; F1 24,91; nhịp tim TB máy 129,9; `n_labels` 160 trong 60 s; dây 1 F1 75,88 (nhịp TB 156,1), dây 3 19,86, dây 4 24,49; `maternal_lock` 0,783; 0 xanh, 9 vàng, 6 đỏ trên 15 đoạn; lý do "> 30 % đoạn đỏ → THẤP" **và** "≥ 60 % → luật ghi đè". Sáu quy tắc mù chọn dây 2, learned chọn dây 3, không quy tắc nào chọn dây 1 — `analysis/chonkenh_results.json → chon_kenh_theo_quy_tac.cinc.a02`; hộp vàng của demo ghi "6/7 cách chọn dây" (`demo/app.py → story_wrong_lead_html`). Nhịp tim đáp án 160 (trung vị RR nhãn) — trưởng nhóm đo lại trên demo ngày 17/09; khớp `n_labels` 160 trong 60 giây. Dải 100–200 nhịp/phút là luật của chế độ luật trong demo — `demo/results/demo_check_showcase.json → rule.fhr_lo, fhr_hi`, không phải ngưỡng lâm sàng.
* [SUY LUẬN] "Phần dư còn dấu vết nhịp mẹ" và "mạng tự tin vì nhịp mẹ rõ" suy ra từ 78 % trùng nhịp mẹ và điểm peakprob dây 2 cao nhất (0,970 so với dây 1 0,963); chưa đo trực tiếp.
* [SỰ KIỆN] a27 — `→ rows.a27_leadpeakprob`: bốn dây 23,26 / 21,26 / 32,94 / 30,23; chọn dây 3 = oracle; 14 đỏ, 1 vàng trên 15 đoạn.
* [SỰ KIỆN] Độ phủ demo: xanh 46/82 = 56,10 %, không đỏ 63/82 = 76,83 % — `demo/results/demo_check_2modes.json → summary_by_mode.hoc.green_coverage_pct, non_red_coverage_pct` (theo bản ghi, chưa theo thời lượng).
* Không dùng: AUROC cổng đo trên CinC 75 bản (đã rút, `HANDOFF.md` §8.4, §10 #5).

### 8c — Hai kết quả âm tính và khoảng cách ngoài miền (0,5 phút)

Kết quả âm tính thứ ba (kiến trúc) nói ở Khối 10.

#### [NÓI GÌ]

> "Hai kết quả âm tính, em báo đủ.
>
> Thích nghi miền không dùng nhãn: bốn cách. Cộng 0,25, trừ 0,67, trừ 1,58, trừ 2,43. Không cách nào giúp.
>
> Dải lọc: trên chính mạng này chỉ cộng 2,44, khoảng tin cậy chạm 0.
>
> Khoảng cách: cùng quy tắc chọn dây cũ, trong miền 97,56, ngoài miền 74,28. Chênh 23,28 điểm. Với gate theo kế hoạch còn 16,84, gate4 còn 16,55, quy tắc hậu kiểm còn 15,55, với trần vẫn còn 13,96. Nguyên nhân em chưa xác định được."

#### [CHIẾU GÌ]

**Slide 22** — ba dòng: *thích nghi miền: +0,25 · −0,67 · −1,58 · −2,43* · *dải lọc trên mạng này: +2,44 [−0,04; +6,29]* · *khoảng cách trong/ngoài miền: 23,28 (cùng quy tắc cũ) → 16,84 (gate, kế hoạch chọn) → 16,55 (gate4) → 15,55 (hậu kiểm) → 13,96 (trần)*.

#### Con số này nghĩa là gì

| Số | Quy đổi xấp xỉ | Tự tính |
|---|---|---|
| Chênh 23,28 (cùng quy tắc cũ) | ≈ 2,4 nhịp sai trên 100 trong miền, ≈ 26 ngoài miền: **gấp khoảng 10 lần** | 25,72 / 2,44 = 10,5 |
| Chênh 15,55 (peakprob) | ≈ 18 so với ≈ 2,4: gấp khoảng 7 lần | 17,99 / 2,44 = 7,4 |
| Chênh 13,96 (trần) | ≈ 16 so với ≈ 2,4: gấp gần 7 lần | 16,40 / 2,44 = 6,7 |
| Âm tính giả 17,97 % của phép thử "không thấy tín hiệu" | Cứ khoảng 6 nhịp máy tìm đúng, phép thử báo "không thấy tín hiệu" ở 1 nhịp. Phép thử sai thường như vậy thì không dùng để đổ lỗi cho dữ liệu được | 1 / 0,1797 = 5,6 |

#### [NẾU CÓ HỎI]

**H: "Bốn cách thích nghi miền có cách nào dùng nhãn CinC không?"** → A21.

*Chú thích:*
* [SỰ KIỆN] Thích nghi miền trên 60 sạch: gốc 74,28; chặn điện lưới thích nghi 74,53 (+0,25); tự huấn luyện nhãn giả 73,61 (−0,67); AdaBN 72,70 (−1,58); TENT 71,85 (−2,43). Nhóm tự tính lại từ `adapt/adapt_results.json → per_record_cinc.*.F1_psd`, loại 15 bản nhiễm: khớp đủ bốn số. Cùng số ở `docs/DE_CUONG_HIEN_TRANG.md` dòng 382–385.
* [SỰ KIỆN] Dải lọc +2,44 [−0,04; +6,29] — `facts_phase4.json → E_dai_loc_tren_TCN`.
* [SỰ KIỆN, tự tính] Khoảng cách: 97,5564 − 74,28 = 23,28; − 80,72 (gate) = 16,84; − 81,01 = 16,55; − 82,01 = 15,55; − 83,60 = 13,96. Nguồn hai vế: `baselines/powermf_fair_stats.json → rely_vs_pmf4.mean_a` (trong miền, dây PSD) và `facts_phase4.json → B_chon_kenh_7_quy_tac_60_sach`. Hai vế khác nhau về độ dài bản ghi (trong miền 5–20 phút, CinC 1 phút) và checkpoint (fold so với production).
* **Không dùng số khoảng cách cũ trong `adapt/`.** Giá trị `adapt/adapt_results.json → mo_phong_dich_chuyen.khoang_cach_CinC_con_lai` được tính bằng `mean_F1.C3_ca_hai` (97,3166) trừ hằng số `CINC_REF_PSD` là mốc PSD **75 bản đã rút** (`adapt/adapt_analyze.py` dòng 15 và 76). Số này đi cùng số đã rút nên không đọc.
* [SỰ KIỆN] Âm tính giả 17,97 % [12,13; 24,97] trên 60 sạch — `facts_phase4.json → C_xac_nhan_vong7.phep_thu_nhin_thay.chi_tiet.ti_le_am_tinh_gia.cinc60|psd`.

---

## Khối 9 — Khi hệ thống sai (1 phút)

### [NÓI GÌ]

> "Đèn cũng sai. Em đếm hai chiều trên 82 bản demo đã chạy: 22 trong miền, 60 CinC sạch. Đèn là cổng cũ trong demo.
>
> Đèn xanh có 46 bản. 43 bản F1 từ 90 trở lên. 3 bản F1 dưới 90, thấp nhất 17,02. Đây là ô nguy hiểm nhất: đèn không thấy dấu hiệu xấu mà kết quả vẫn sai. Demo ghi thẳng điều này ở chú thích bước 5: *Xanh không bảo đảm là đúng*.
>
> Hai trong ba bản đó thuộc nhóm 7 bản CinC mà em đánh dấu nhãn đáp án có vấn đề. Bản còn lại, a57, không có lý do đó.
>
> Đèn đỏ có 19 bản. Không bản nào có F1 từ 90 trở lên.
>
> Trong kịch bản giả định, đèn đỏ sai chỉ tốn một lần khám thêm. Đèn xanh sai thì đưa một con số sai cho bác sĩ. Nên em ưu tiên sai về phía từ chối."

### [CHIẾU GÌ] — Hình H5: bản đồ sai của đèn (slide 23)

Bảng lưới, ô *"xanh mà F1 < 90"* tô viền đỏ đậm, chú thích góc: *"ô nguy hiểm: xanh mà sai"*.

| Đèn (cổng cũ, chế độ học) | F1 ≥ 90 | F1 < 90 | Tổng |
|---|---:|---:|---:|
| **Xanh** | 43 | **3** (a52 85,39 · a54 38,79 · a57 17,02) | 46 |
| Vàng | 15 | 2 (a06 88,46 · a07 86,92) | 17 |
| **Đỏ** | **0** | 19 | 19 |
| Tổng | 58 | 24 | 82 |

Dòng dưới bảng: *"Trong miền (22): xanh 12 bản đều F1 ≥ 90 · đỏ 2 bản đều F1 < 90 (B1_07 87,09 · B2_03 83,91). Ba bản xanh-sai đều là CinC; a52 và a54 thuộc 7 bản nhãn đáng ngờ."* Chân hình: *"Cổng cũ đang chạy trong demo. Chưa phải cổng 22 ca. Chọn dây: peakprob."*

### Con số này nghĩa là gì

| Số | Quy đổi |
|---|---|
| 3 / 46 xanh sai | Khoảng 1 bản trong 15 bản đèn xanh có F1 dưới 90. |
| 0 / 19 đỏ mà F1 ≥ 90 | Bản đỏ có F1 cao nhất là 87,09. |
| Chế độ luật (không dùng mặc định) | 5 bản xanh mà F1 < 90. Chế độ học mặc định ít hơn. |

### [NẾU CÓ HỎI]

**H: "Chín bản F1 dưới 50 ngoài miền, đèn có bắt được không?"** → A20.

*Chú thích:*
* [SỰ KIỆN] Tổng quan — `facts_phase4.json → F_demo.summary_by_mode.hoc` (xanh 46, F1 TB 95,70, thấp nhất 17,02; vàng 17; đỏ 19, F1 TB 54,26; `green_but_F1_below_90` a52 85,39 · a54 38,79 · a57 17,02; `n_red_but_F1_at_least_95` 0). Chế độ luật: 5 bản xanh mà F1 < 90 — `→ summary_by_mode.luat`.
* [SỰ KIỆN, tự đếm] Cột F1 ≥ 90 / < 90 và tách trong miền / CinC: nhóm đếm từ danh sách từng bản trong `demo/results/demo_check_2modes.json → summary_by_mode.hoc.by_level.*.records` (cùng nguồn mà `F_demo` trích). Đỏ cao nhất 87,09 (B1_07).
* [SỰ KIỆN] 7 bản nhãn đáng ngờ a33 a38 a47 a52 a54 a71 a74 — `benchmark_dpss/eval_cinc60_sach.json → meta.bad_annotation`; facts dùng tập này ở `A_cinc2013_60_ban_sach.53_ban_loai_7_nhan_sai`.
* [GIẢ THUYẾT] Hậu quả lâm sàng của đèn đỏ sai và đèn xanh sai: trong kịch bản dùng giả định, chưa kiểm với bác sĩ. [KHUYẾN NGHỊ] Ưu tiên sai về phía từ chối.

---

## Khối 10 — Vì sao chọn mô hình này (1,5 phút)

### [NÓI GÌ]

> "Em không chọn mạng theo cảm tính. Em so bảy họ kiến trúc, cùng số tham số trong cộng trừ 2,7 phần trăm. Cùng hạt giống, cùng cách chia, cùng ngân sách. Giao thức rút gọn: ba epoch, ba fold, một hạt giống.
>
> Mạng em dùng: 97,64. Hai họ sát sau: 97,63 và 97,62, tương đương theo kiểm định. Rồi 96,93, 96,84, 96,38. Họ kém nhất: 94,53, kém 3,10 điểm.
>
> Vì sao họ đó kém. Nó chỉ nhìn 60 mili-giây quanh mỗi điểm. Mạng của em nhìn 1.516 mili-giây. Em nới trường nhìn của họ đó cho khớp, giữ số tham số. Nó lên 96,84. Nên phần lớn khoảng cách này, khoảng 74 phần trăm, đo bề rộng ngữ cảnh; trên thang logit cnn_wide vẫn kém TCN.
>
> Em thử nhân bốn lần số tham số. Chỉ được cộng 0,26 điểm, đo trong mẫu.
>
> Kết luận: trong bài toán này, đổi kiến trúc là đòn bẩy yếu. Đa số bài khác tái tạo dạng sóng tim thai rồi mới dò đỉnh. Em dò thẳng từng mẫu, bỏ bước tái tạo."

### [CHIẾU GÌ]

**Slide 24** — bảng 7 họ, bốn cột: *họ* · *tham số* · *trường nhìn (ms)* · *F1*. Tô đậm dòng 60 ms. Góc dưới: *"×4 tham số → +0,26"*.

### Con số này nghĩa là gì

| Số | Quy đổi xấp xỉ |
|---|---|
| 60 ms | Khoảng một phần bảy quãng giữa hai nhịp thai: chỉ thấy một mẩu của một nhịp. |
| 1.516 ms | Khoảng 3,5 nhịp thai ở 140 nhịp/phút. |
| ×4 tham số → +0,26 | Bốn lần kích thước, bớt khoảng 2 đến 3 nhịp sai trên 1.000 nhịp. |
| 97,64 − 97,62 = 0,02 | Ba họ đầu cách nhau chưa tới một nhịp sai trên 1.000. |

### [NẾU CÓ HỎI]

**H: "Vì sao không thử Transformer?"**
> "Chưa thử ở giao thức cân tham số, em ghi lại. Lý do hoãn: lợi ích của bề rộng ngữ cảnh bão hoà quanh 1,5 giây. Transformer mạnh ở ngữ cảnh dài. Em đoán lợi ích nhỏ, nhưng đó là phỏng đoán."

**H: "Ba epoch chưa hội tụ, xếp hạng có tin được không?"**
> "Em chỉ dùng để xếp hạng, không lấy số cuối. Họ đứng đầu ở giao thức rút gọn cũng là họ chạy ở giao thức đầy đủ. Nếu cô cần, em chạy đầy đủ ba họ đầu, khoảng một ngày máy."

*Chú thích:* [SỰ KIỆN] bảng 7 họ — `analysis/kientruc_results.json → table.*.macro_psd, rf_ms, params_pct_vs_tcn` (tcn 97,64 / 1.516; rf_wide 97,63 / 3.052 / +2,67 %; tcn_ms 97,62 / 2.716; rf_narrow 96,93 / 748; cnn_wide 96,84 / 1.508; unet1d 96,38 / 636; cnn_l 94,53 / 60). −3,10 [−6,19; −0,96], 2 hơn / 20 kém — `→ comparisons.cnn_l.all22`; TOST — `→ holm_tost`. [SỰ KIỆN, tự tính] Nới trường nhìn lấy lại khoảng 74 % khoảng cách: (96,84 − 94,53) / (97,64 − 94,53) = 0,74, từ `→ table.*.macro_psd`; trên thang logit `cnn_wide` kém TCN có ý nghĩa — `analysis/KIENTRUC.md` (README.md mục Limitations). ×4 tham số +0,26 — `analysis/CHANDOAN_MOHINH.md` dòng 22, 242; `analysis/chandoan_capacity.json`. Mô hình các bài — `docs/BOI_CANH_1_KENH.md` mục 1. [SUY LUẬN] quy đổi nhịp.

---

## Khối 11 — Văn liệu: năm hướng, em đứng ở đâu (2 phút)

### [NÓI GÌ]

> "Em đọc 30 bài, xếp thành năm hướng và một nhóm ngoài lề.
>
> Hướng một, khử tim mẹ bằng mẫu và lọc thích nghi. Em dùng chính bước trừ mẫu làm tiền xử lý.
>
> Hướng hai, tách nguồn nhiều dây. Mạnh nhất, như Power-MF, nhưng cần nhiều điện cực.
>
> Hướng ba, học sâu một dây, cùng cấu hình với em. Trong miền trên ADFECGDB, họ công bố 96,5 đến 99,7. Em đạt 99,40 trên 5 sản phụ đó.
>
> Ngoài miền trên CinC, họ công bố 77,8 đến 97,97. Em ở 74,28 với quy tắc cũ, 80,72 với quy tắc kế hoạch chọn trước khi chạy, 81,01 với gate4 cũng ghi trước, 82,01 hậu kiểm. Thấp hơn đa số.
>
> Nhưng mỗi số cao hơn đều có ít nhất một trong ba điều. Chọn tập con bằng tay. Chọn dây bằng tay. Hoặc tập chấm còn bản sao dữ liệu huấn luyện.
>
> Bài gần em nhất là Orvas 2025: một dây, không tinh chỉnh, cùng dung sai. Họ đạt 77,8 trên đủ 75 bản. Số đó nằm trong khoảng tin cậy quy tắc cũ của em. Em không nói ngang hay vượt họ.
>
> Hướng bốn, học sâu nhiều dây. Số cao, nhưng cả ba bài có vấn đề giao thức. Em không so.
>
> Hướng năm, đánh giá và bộ chuẩn. Em học ba việc. Chọn dây oracle làm đẹp số. Phải kiểm chồng lấn dữ liệu. Phải thống kê theo sản phụ.
>
> Nhóm ngoài lề là 12 bài tô-pô. Em thử hướng đó, được 27,4 so với 97,1 của mạng một chiều cùng tham số. Em bỏ.
>
> Một bài học. Ghi chú đọc bài của em đã ghi phải kiểm chồng lấn. Em ghi rồi không làm. Đến vòng bảy mới đo."

### [CHIẾU GÌ]

**Slide 25–26** (slide 25: năm hướng; slide 26: các bài một dây trên cùng bộ dữ liệu) — năm hướng, mỗi hướng ba ô: *họ làm gì* · *số tốt nhất* · *em khác gì*. Nửa dưới: bảng tám bài quan trọng nhất lấy nguyên từ `docs/TOM_TAT_30_BAI.md`, cột cuối *"So được?"* tô ba mức: có / một phần / có điều kiện. Góc: ghi chú đọc bài p13 và p20 phóng to câu "kiểm chồng lấn ADFECGDB–CinC".

### [NẾU CÓ HỎI]

**H: "DPSS một dây đạt 97,7, em 97,56. Vậy em kém họ?"**
> "Chưa kết luận được. Họ chọn dây bằng tay, em chọn mù. Họ tính theo tín hiệu, em theo sản phụ. Số của họ em chưa chạy lại. Muốn nói hơn kém phải chạy lại DPSS, em ước hai đến ba ngày."

**H: "Bảng của em toàn 'không so trực tiếp được'. Có phải né không?"**
> "Mỗi dòng có lý do ghi kèm. Ví dụ một bài báo độ chính xác 98,36 phần trăm. Bài đó dùng bốn dây, cửa sổ chồng 90 phần trăm, xáo trộn trước khi chia. Đặt cạnh F1 từng nhịp của em là gây hiểu nhầm. Em chỉ so trực tiếp với cái em chạy lại được."

*Chú thích:*
* [SỰ KIỆN] Đếm 30 bài, năm hướng, tám bài — `docs/TOM_TAT_30_BAI.md`; `docs/BOI_CANH_1_KENH.md` mục 1–2. Khoảng 96,5–99,7 (Asadi 96,52 trên 17 kênh ADFECGDB; Mohebbian 99,7 ở 30 ms; Chen 99,17) — `docs/BOI_CANH_1_KENH.md`; `de_cuong_latex/bao_cao_30_paper.tex` p03, p06, p07. 99,40 trên 5 ADFECGDB (mô hình 22 ca, dây mù) — `baselines/powermf_fair_stats.json → per_subject`, nhóm tự tính trung bình 5 bản = 99,397. Ngoài miền 77,8 (Orvas, 75 bản) → 97,97 (Asadi, 80 kênh chọn) — `bao_cao_30_paper.tex` p11, p07. Castillo 2018 (94,11; 98,07 trên 26 bản chọn tay) **không** tính vào hướng ba: báo cáo 30 bài xếp bài này ở mục "Xử lý tín hiệu cổ điển" (p17); số của nó vẫn nêu ở slide 26 vì là bài một dây.
* [SỰ KIỆN] 74,28 [66,63; 81,78] — `facts_phase4.json → A.psd`; 80,72 (gate), 81,01 (gate4) và 82,01 (peakprob) — `→ B`. Orvas không nhiễm — `survey/ro_ri_vanlieu.json → bang_bi_nhiem.khong_nhiem`.
* [SỰ KIỆN] DPSS 97,7 trên 22 bản Silesia (bài gọi là ADFECGDB, gồm nhóm chuyển dạ 98,08), huấn luyện chỉ trên FECGSYNDB tổng hợp, zero-shot — `survey/facts_verified.json → doi_chuan_dpss.so_that_trong_bai`; kênh chọn tay — `docs/BOI_CANH_1_KENH.md` dòng 29, 87.
* [SỰ KIỆN] Esmaeili 98,36 (p10) — `docs/BOI_CANH_1_KENH.md` dòng 49. TDA 27,42 so với 97,14 — `survey/facts_verified.json → tda_da_bac_bo`. Ghi chú p13, p20 — `de_cuong_latex/tables/bang_baihoc.tex`.

---

## Khối 12 — Những gì đã rút và vì sao (1,5 phút)

### [NÓI GÌ]

> "Em đã tự rút nhiều tuyên bố của chính mình. Danh sách đầy đủ có 10 cụm tuyên bố và 5 nhóm con số. Em kể năm tuyên bố chính, để cô thấy em biết hệ mình làm được gì.
>
> Một. Mọi số CinC trên 75 bản. Vì 15 bản là bản sao dữ liệu huấn luyện, thổi phồng 3,27 đến 7,18 điểm. Thay bằng số trên 60 bản sạch.
>
> Hai. Câu nhận quyền ưu tiên về chồng lấn. Vì ban tổ chức đã ghi từ 2013, và cảnh báo nằm ngay trong ghi chú đọc bài của em. Thay bằng: em định danh và định lượng.
>
> Ba. Kết luận mô hình đã đủ tốt, khoảng cách là do dữ liệu. Vì phép thử nền có âm tính giả gần 18 phần trăm. Thay bằng: nguyên nhân chưa xác định.
>
> Bốn. Hiệu ứng lớn của dải lọc. Vì nó đo trên mô hình khác mà phát biểu như về mạng này. Đo lại trên mạng này còn 2,44, chạm 0.
>
> Năm. Chữ mạnh về khai báo trước, và peakprob như kết quả xác nhận. Vì tệp khai báo viết sau khi thấy điểm từng dây, chưa neo. Thay bằng: quy tắc kế hoạch chọn là gate, 80,72, trượt Holm. Gate4, cũng ghi trước khi chạy, 81,01, qua Holm nhưng không phải quy tắc kế hoạch chọn. Peakprob 82,01 là giả thuyết hậu kiểm.
>
> Ba trong năm là câu giải thích hoặc câu nhận công. Hai là số đo trên sai tập hoặc sai mô hình."

### [CHIẾU GÌ]

**Slide 27** — bảng 5 dòng: *tuyên bố đã rút* · *vì sao* · *thay bằng*. **Không in lại các số đã rút**, chỉ ghi tên tuyên bố.

### [NẾU CÓ HỎI]

**H: "Rút nhiều thế thì còn gì để đăng?"**
> "Còn những thứ em đo trực tiếp trên đúng tập. Ba số F1 trên 22 sản phụ. Tỉ lệ bù 89,49. Bảng bảy quy tắc trên 60 bản sạch. Danh sách 15 bản trùng. Kết quả cổng để-một-người-ra."

**H: "Kịch bản của em có câu nào từng sai mà chưa rút không?"**
> "Có. Bản nháp kịch bản này từng ghi đèn không lấy từ mạng, và dùng số 0,934 cho đèn demo. Cả hai sai. Em đã sửa trong kịch bản trước buổi này, còn phải rà lại các tài liệu khác."

*Chú thích:* [SỰ KIỆN] năm tuyên bố chính — `docs/DE_CUONG_HIEN_TRANG.md` mục 9.2; danh sách đầy đủ `facts_phase4.json → Z_DA_RUT`: 10 cụm tuyên bố (`cum_tu`) và 5 nhóm con số (cinc_mau_10, cinc_75_o_nhiem, powermf_cong_chuyen_hong, dai_loc_gbm_nhu_phat_bieu_ve_tcn, khoang_cach_trong_ngoai_mien_17_92). Tuyên bố năm: gate là quy tắc kế hoạch chọn, trượt Holm 0,051; gate4 Holm 0,015 — `→ B_chon_kenh_7_quy_tac_60_sach`; `analysis/chonkenh_results.json → quyet_dinh.tot_nhat_theo_22`. Silva 2013 / Clifford 2014 — `→ A.co_so`. Âm tính giả — `→ C.phep_thu_nhin_thay`. Dải lọc — `→ E_dai_loc_tren_TCN`. Tệp khai báo chưa neo — `→ B.khai_bao_truoc`. Câu cũ "trước khi có ai chỉ ra" đã bỏ vì không kiểm được. Câu cũ "số đo trực tiếp không cái nào phải rút" đã bỏ vì tuyên bố một và bốn là số đo.

---

## Khối 13 — Đóng góp, kèm ranh giới (1,5 phút)

### [NÓI GÌ]

> "Giờ cô đã thấy bằng chứng và phần đã rút. Em có bốn thứ để nộp, cái nào cũng có ranh giới.
>
> Một, phép đo tỉ lệ bù: 89,49 phần trăm. Ranh giới: một phương pháp đối chuẩn, 22 sản phụ, khoảng tin cậy vượt 100.
>
> Hai, so sánh quy tắc chọn dây mù trên 60 bản sạch. Cũ 74,28, gate theo kế hoạch 80,72 và trượt Holm, gate4 cũng ghi trước 81,01, peakprob hậu kiểm 82,01, trần 83,60. Ranh giới: quy tắc kế hoạch chọn trượt, quy tắc cao nhất là hậu kiểm, và chưa có bộ thứ ba để kiểm lại.
>
> Ba, phổ lỗi có mức ngẫu nhiên đối chứng. Lỗi bỏ nhịp dù có tín hiệu chiếm 3,8 phần trăm trong miền, mức ngẫu nhiên là 14,7. Ranh giới: phần ngoài miền còn đo trên 75 bản, chưa tính lại.
>
> Bốn, định lượng chồng lấn dữ liệu: định danh đúng 15 bản và đo mức thổi phồng. Ranh giới: sự kiện chồng lấn ban tổ chức đã ghi từ 2013.
>
> Ba thứ em không nhận là đóng góp. Đèn tin cậy: 5 trong 24 quy tắc một chỉ số cũng xếp đúng ba người khó. Kiến trúc mạng: ba họ đầu cách nhau 0,02 điểm. Và bản thân sự kiện chồng lấn."

### [CHIẾU GÌ]

**Slide 28** — bảng bốn dòng, hai cột bằng nhau: *đóng góp* | *ranh giới*. Dưới bảng, ba gạch đầu dòng *"không nhận là đóng góp"*.

### [NẾU CÓ HỎI]

**H: "Đóng góp nào chắc nhất?"**
> "Phép đo 89,49 và bản định lượng 15 bản trùng. Hai cái là số đo, chạy lại được, không phụ thuộc lựa chọn hậu kiểm. Quy tắc chọn dây em ghi là giả thuyết mạnh."

**H: "Ba trong bốn đóng góp kèm chữ chưa xác nhận. Trước hội đồng em bảo vệ kiểu gì?"** → A6.

*Chú thích:* [SỰ KIỆN] 89,49 — `analysis/recovery_ratio.json`. Bảng quy tắc — `facts_phase4.json → B_chon_kenh_7_quy_tac_60_sach`. Phổ lỗi 3,82 % so với 14,66 % — `analysis/chandoan_results.json → pho_loi.22_chu_the_kenh_PSD` (đọc 14,7, không đọc 15,2 của bản cũ); ngoài miền chỉ có `pho_loi.CinC75_kenh_PSD`. 15 bản và 3,27–7,18 — `facts_phase4.json → A_cinc2013_60_ban_sach`. 5/24 — `analysis/GATE22.md` dòng 304. 0,02 = 97,6357 − 97,6177 — `analysis/kientruc_results.json → table`.

---

## Khối 14 — Định vị, kế hoạch, đạo đức, pháp lý (1,5 phút)

### [NÓI GÌ]

> "Đích gần nhất là tạp chí Physiological Measurement, nơi cộng đồng điện tim thai công bố. Tạp chí xếp Q2 theo Scimago 2024. Đích thứ hai là hội nghị CinC 2027, hạn khoảng tháng tư, ngày chưa xác nhận.
>
> Ba tháng tới em làm ba việc rẻ. Chạy đủ ba hạt giống. Tính lại đèn trên 60 bản sạch. Chạy lại DPSS.
>
> Muốn đi xa hơn phải có dữ liệu bệnh viện. Em hình dung ba nấc. Một, kiểm hồi cứu trên dữ liệu có nhãn da đầu, khai báo trước quy tắc và ngưỡng. Hai, đo song song với CTG trên cùng sản phụ. Ba, sau đó mới nói tới dùng tại nhà. Năm nay em chỉ tới nấc một, nếu có dữ liệu.
>
> Dữ liệu mới cần hội đồng đạo đức bệnh viện duyệt và phiếu đồng thuận. Dữ liệu phải ẩn danh trước khi ra khỏi bệnh viện. Em chưa bắt đầu thủ tục nào.
>
> Ba việc em xin cô. Một, đầu mối khoa sản để xin dữ liệu có nhãn. Hai, hỏi hội đồng trường chấm theo Scimago hay WoS. Ba, một buổi cô đọc phản biện trước khi nộp.
>
> Em xin nhắc lại: đây là nguyên mẫu nghiên cứu, không phải thiết bị y tế, không dùng để ra quyết định lâm sàng."

### [CHIẾU GÌ]

**Slide 29–30** — bốn khối: *định vị* (đích · xếp hạng · rào cản; không ghi phần trăm ước cửa) · *ba việc rẻ, hai việc dừng* (đổi kiến trúc; thích nghi miền không nhãn) · *ba nấc kiểm chứng lâm sàng* (bậc thang ba bậc, bậc một tô đậm "năm nay") · *ba việc xin cô*. Góc dưới: hai dòng về dữ liệu (dữ liệu hiện tại theo giấy phép từng nguồn, kho mã không chứa tệp dữ liệu; dữ liệu mới cần đạo đức + đồng thuận + ẩn danh).

**Slide 31 — cuối:** câu cố định pháp lý, chữ to, không có gì khác.

### [NẾU CÓ HỎI]

**H: "Không xin được dữ liệu mới thì đề tài dừng ở đâu?"**
> "Vẫn nộp được một bài ở tạp chí chuyên ngành: hai phép đo chắc và một giả thuyết ghi rõ. Thiếu dữ liệu thì không xác nhận được quy tắc chọn dây. Em thấy đó là kết cục chấp nhận được cho năm nay."

**H: "Khả năng được nhận bao nhiêu?"**
> "Tài liệu chiến lược của nhóm có ghi vài con số phần trăm. Đó là ước lượng chủ quan, không có mô hình tính. Em chỉ dám nói: tạp chí chuyên ngành khả năng khá. Nhóm tạp chí Q1 thì khó nếu không có dữ liệu mới."

*Chú thích:*
* [SỰ KIỆN] PM Q2 Scimago 2024 (Physiology 25/73) — `facts_phase4.json → G_venue`. CinC 2027 hạn khoảng 4/2027 chưa xác nhận — `docs/DE_CUONG_HIEN_TRANG.md` mục 13; không dùng kỳ hội nghị năm nay làm đích (`HANDOFF.md` §8.1). Ước cửa phần trăm — `docs/CHIEN_LUOC_CONG_BO.md`, [SUY LUẬN chủ quan], không đọc thành tiếng.
* [SỰ KIỆN] Ba việc rẻ, hai việc dừng — `HANDOFF.md` §10 (#4 hạt giống, #5 cổng trên 60 sạch, #6 DPSS; "Đừng làm"). Giấy phép dữ liệu, `.gitignore` chặn `*.dat *.hea *.edf` — `HANDOFF.md` dòng 310, 373–375.
* [KHUYẾN NGHỊ] Ba nấc kiểm chứng; thủ tục đạo đức, đồng thuận, ẩn danh. [SỰ KIỆN] chưa bắt đầu thủ tục — `HANDOFF.md` §10 #1 ghi "cần đạo đức nghiên cứu", chưa có tệp thủ tục.

---

# Phụ lục A — Câu hỏi giảng viên có thể hỏi

Trả lời 2–6 câu. Nguồn ghi cuối mỗi câu. A1–A15 là bộ cũ đã sửa số khối. A16–A22 là bảy câu khó nhất từ thẩm định vòng 10 (Q1–Q7). A3-bis là câu trả lời a02 dài 60 giây.

**A1 (Khối 3). "Vì sao chọn F1 ±50 ms mà không dùng tiêu chí chính thức của CinC 2013?"**
> "Tiêu chí chính thức của cuộc thi là sai số nhịp và sai số khoảng RR. F1 dung sai 50 mili-giây là quy ước của Behar 2014 và Andreotti 2016. Nó giúp so được với các bài sau này. Em ghi rõ đây là chấm lại, không phải bảng xếp hạng cuộc thi."
> *Nguồn: `bang_baihoc.tex` p20, p13, p15; `docs/CONG_BANG_DOI_CHUAN.md` mục 6.5.*

**A2 (Khối 2). "Một dây thì chọn dây nào? Thiết bị thật đâu có bốn dây để chọn."**
> "Đúng, đây là chỗ em phải nói rõ. Hiện em chọn một trong bốn dây bằng quy tắc mù nhãn. Thiết bị một điện cực thì phải dán đúng vị trí ngay từ đầu. Vị trí nào tốt nhất, em chưa trả lời được từ dữ liệu này."
> *Nguồn: `analysis/CHONKENH.md`; `docs/BOI_CANH_1_KENH.md` mục 4.*

**A3 (Khối 6). "Khoảng tin cậy chạm 103 phần trăm. Con số 89,5 còn nghĩa gì?"**
> "Ước lượng điểm là 89,5. Dữ liệu chưa loại được khả năng bù toàn bộ. Bỏ lần lượt từng người thì tỉ lệ dao động 88,6 đến 93,4, hẹp hơn. Muốn hẹp nữa phải thêm người."
> *Nguồn: `analysis/recovery_ratio.json → jackknife_bo_tung_chu_the_min_max`.*

**A4 (Khối 11). "Mohebbian 2022 một dây đạt 99,7 ở dung sai 30 ms. Em có đo lại ở 30 ms không?"**
> "Chưa. Em chỉ có số ở 50 mili-giây, em ghi trong giới hạn. Cũng cần nói bộ CinC họ chấm có 15 bản là bản sao dữ liệu huấn luyện của họ."
> *Nguồn: `survey/facts_verified.json → gioi_han_phai_khai_bao`; `survey/ro_ri_vanlieu.json → bang_bi_nhiem.chac_chan` (Mohebbian 15/69 bản).*

**A5 (Khối 5). "Sao không để mạng học luôn khâu khử tim mẹ?"**
> "Em chưa thử, em ghi lại. Em làm tay để quy trách nhiệm được: hỏng thì biết hỏng ở khâu nào. Đây là lựa chọn thiết kế, chưa phải kết quả đo."
> *Nguồn: `model/fqrs_model.py`; `docs/KICH_BAN_HANH_TRINH.md` phần 4.*

**A6 (Khối 13). "Ba trong bốn đóng góp kèm chữ chưa xác nhận. Trước hội đồng em bảo vệ kiểu gì?"**
> "Em đưa hai thứ chắc lên trước: phép đo 89,49 và bản định lượng 15 bản. Rồi nêu quy tắc chọn dây là giả thuyết, kèm kế hoạch xác nhận. Em nghĩ một đề tài biết ranh giới của mình thì dễ tin hơn."
> *Nguồn: `docs/DE_CUONG_HIEN_TRANG.md` mục 9.1.*

**A7 (Khối 10). "Mạng nhìn 1,5 giây, tức thấy nhiều nhịp. Nó có đoán theo chu kỳ thay vì thấy nhịp không?"**
> "Em có đo gián tiếp. Nếu đoán theo chu kỳ thì sẽ bỏ sót nhịp rõ mà lệch chu kỳ. Loại lỗi đó trong miền là 3,8 phần trăm, mức ngẫu nhiên 14,7. Bằng chứng không ủng hộ giả thuyết đoán chu kỳ. Nhưng em chưa làm thí nghiệm cắt chu kỳ chủ động."
> *Nguồn: `analysis/chandoan_results.json → pho_loi.22_chu_the_kenh_PSD`.*

**A8 (Khối 4). "77 phần trăm dữ liệu huấn luyện nhãn gián tiếp mà kết quả vẫn cao. Vì sao?"**
> "Hai lý do, đều chưa chứng minh. Nhãn gián tiếp vẫn đúng vị trí nhịp, chỉ lệch có hệ thống vài mili-giây. Và em chấm ở dung sai 50 mili-giây nên lệch đó ít đổi F1. Nhưng nó cấm em dùng B1 cho chỉ số thời điểm."
> *Nguồn: `analysis/ABLATION_B1.md` §3, §6.*

**A9 (Khối 4). "Sáu mươi bản sạch có bao nhiêu sản phụ?"**
> "Em không biết, và ghi rõ là không biết. Nhiều nhất 60, có thể ít hơn: một nguồn góp 14 bản vào cuộc thi, cả 14 từ một sản phụ, nhưng em chưa định danh được 14 bản đó có nằm trong set-a không. Nên thống kê theo bản ghi ngoài miền chỉ là gần đúng."
> *Nguồn: `survey/ro_ri_vanlieu.json → kiem_cheo_ky_thuat.cung_san_phu_khac_buoi`; `docs/CONG_BANG_DOI_CHUAN.md` mục 4.4.*

**A10 (Khối 7). "Nếu Octave có lỗi như vậy, kết quả chạy lại của em có tin được không?"**
> "Đó là lý do em kiểm chứng ngoài. Trên nhóm bản tác giả có công bố số, em ra 99,40 so với 99,46. Nếu bản chạy lại còn lỗi hệ thống thì số đã không khớp. Em ghi rõ trong bài chạy qua phần mềm nào và bản vá nào."
> *Nguồn: `baselines/BASELINES.md` dòng 76; `baselines/powermf_published.json → b1_powermf`.*

**A11 (Khối 7). "Power-MF bốn dây trên 60 bản sạch đạt 93,12, em chỉ 74 đến 82. Đề tài còn giá trị gì?"**
> "Số đó không ủng hộ em, em nói thẳng. Em ở 74,28 với quy tắc cũ, 80,72 với quy tắc kế hoạch chọn, 81,01 với gate4, 82,01 hậu kiểm. Nhưng Power-MF một dây trên cùng 60 bản chỉ 55,97. Phần lớn khoảng cách là do nhiều dây. Câu hỏi của em là một dây mất bao nhiêu. Câu trả lời ngoài miền là mất nhiều, và đó là một kết quả."
> *Nguồn: `docs/CONG_BANG_DOI_CHUAN.md` dòng 33 (93,12 là số dẫn xuất); `facts_phase4.json → A.powermf_1ch_60_sach`, `→ B`.*

**A12 (Khối 11). "Em đọc toàn văn hay đọc tóm tắt?"**
> "Không phải bài nào em cũng mở được toàn văn. Có năm bài tạp chí đóng. Em ghi rõ năm bài đó và không trích số từ bài chưa đọc được. Tài liệu bối cảnh lần này em lấy từ ghi chú đọc bài, chưa đọc lại PDF."
> *Nguồn: `survey/ro_ri_vanlieu.json → han_che`; `docs/BOI_CANH_1_KENH.md` mục 5.*

**A13 (Khối 8c). "Ngoài miền kém trong miền hơn 20 điểm mà không giải thích được. Hệ có dùng được không?"**
> "Hiện chỉ dùng được trong điều kiện giống dữ liệu huấn luyện. Cùng quy tắc cũ, chênh 23,28 điểm; với quy tắc tốt nhất còn khoảng 15. Đèn tin cậy không cần biết nguyên nhân, chỉ cần nhận ra đoạn không đáng tin. Nên tính lại đèn trên 60 bản sạch là ưu tiên."
> *Nguồn: tự tính từ `baselines/powermf_fair_stats.json` và `facts_phase4.json → B` (Phụ lục D); `HANDOFF.md` §10 #5.*

**A14 (Khối 12). "Em dùng công cụ trí tuệ nhân tạo. Phần nào là của em?"**
> "Em dùng công cụ để đối chiếu số và để có một lượt đọc phản biện. Thiết kế thí nghiệm, quyết định rút tuyên bố nào, và trách nhiệm về số là của em. Cô chọn bất kỳ con số nào, em mở tệp gốc ngay."
> *Nguồn: `docs/nhat_ky/THAMDINH_VONG8.md`; `docs/nhat_ky/THAMDINH_VONG10_KICH_BAN.md`.*

**A15 (Khối 14). "Hội đồng trường có quen với kiểu trình bày nêu cả phần rút lại không?"**
> "Em không chắc, và đó là một trong ba việc em xin ý kiến cô. Em nghĩ phần rút lại cho thấy em biết hệ mình làm được gì. Nếu cô thấy nên gọn lại, em để phần đó vào phụ lục."
> *Nguồn: `docs/DE_CUONG_HIEN_TRANG.md` mục 13.*

**A16 (Khối 5, 8b — Q1). "Đặc trưng quan trọng nhất của đèn là độ đều nhịp do mạng tìm ra, có cả xác suất của mạng. Khi mạng tự tin sai thì đèn có sụp theo không?"**
> "Có thể, cô nói đúng. 6 trong 12 chỉ số lấy từ đầu ra của mạng. Quan trọng nhất là độ đều nhịp mạng tìm ra, rồi đến xác suất của mạng. Xáo trộn từng chỉ số thuần tín hiệu gần như không làm cổng kém đi. Nên đèn không độc lập với mạng. Bản nháp kịch bản của em từng ghi ngược lại, câu đó sai và em đã sửa.
> Ở a02, mạng tự tin trên nhịp mẹ. Đèn vẫn đỏ vì hai đường. Một, 6 trên 15 đoạn bị chấm đỏ. Hai, luật bám nhịp mẹ so trực tiếp với nhịp mẹ. Em chưa đo đèn hỏng theo mạng thường xuyên đến đâu."
> *Nguồn: `fsqi/gate.py` dòng 61–78; `fsqi/fsqi.py` dòng 307–318; `analysis/gate22_results.json → cong.permutation_importance_delta_auroc`; `demo/results/demo_check_showcase.json → rows.a02_leadpeakprob.confidence.reasons`.*

**A17 (Khối 8b — Q2). "Đèn trong demo là cổng nào? Con số 0,934 em đọc có phải của chính cái đèn đó không?"**
> "Không phải. Demo đang dùng cổng cũ, học trên mô hình 5 sản phụ. Trong bản ghi, cổng đó được 0,721, khoảng tin cậy 0,517 đến 0,898, đo trên 5 bản CinC khi ghép với mô hình 5 ca. Ghép với mô hình 22 ca đang chạy trong demo thì em chưa đo lại. Số 0,934 là cổng 22 ca, mới ở dạng phân tích. Nó chỉ tính được trên 11 trong 22 người có đoạn xấu. Thay cổng trong demo là việc chưa làm."
> *Nguồn: `analysis/stats_results.json → comparisons.gate_auroc_cinc.auroc_TRONG_ban_ghi`; `analysis/GATE22.md` dòng 64–71, 364–366; `demo/results/demo_check_2modes.json → gate_note`; `demo/app.py → STORY_GATE_NOTE` ("ghép với mô hình 22 sản phụ đang chạy thì chưa đo lại").*

**A18 (Khối 1 — Q3). "Bệnh viện đã có CTG, và CTG đã tính biến thiên ngắn hạn. Điện tim bụng một dây cho bác sĩ thêm được gì cụ thể?"**
> "Em chưa trả lời được bằng số. Em cũng chưa đọc bản gốc về cách CTG tính biến thiên ngắn hạn, nên không so chi tiết. Điều em đo được chỉ là máy tìm từng nhịp trên tín hiệu điện. Trong miền, trên 5 sản phụ, chỉ số biến thiên lệch 0,33 mili-giây. Lợi ích so với CTG là giả thuyết, cần đo song song trên cùng sản phụ. Đó là câu em muốn hỏi bác sĩ sản trước khi nói tiếp."
> *Nguồn: `analysis/clinical_results.json → summary.ADFECGDB`; Dawes–Redman [CẦN KIỂM BẢN GỐC] — không có bài gốc trong `papers/` hoặc `survey/`.*

**A19 (Khối 8a — Q4). "Các bản em đem demo là bản đẹp để kể chuyện. Trên 60 bản thì quy tắc mới thua ở bao nhiêu bản, có bản nào dây em chọn kém xa dây tốt nhất không?"**
> "Đúng là em chọn để minh hoạ. Trên 60 bản, quy tắc mới hơn quy tắc cũ ở 19 bản, bằng ở 35, kém ở 6. Kém nặng nhất 3,90 điểm. So với dây tốt nhất: quy tắc mới đạt đúng F1 của dây tốt nhất ở 48 bản. Có 2 bản kém dây tốt nhất hơn 10 điểm: a02 kém 51 điểm, a57 kém 21 điểm. Thẻ a02 trong demo chính là trường hợp chọn sai đó."
> *Nguồn: `facts_phase4.json → B.peakprob_hau_kiem.thang_thua_hoa` [19, 6, 35]; nhóm tự tính từ `analysis/chonkenh_results.json → F1_tung_ban_ghi.cinc` trên 60 sạch: kém nặng nhất so với PSD 3,90 (a57); peakprob bằng oracle ở 48 bản; oracle − peakprob: a02 50,97, a57 21,26.*

**A20 (Khối 9 — Q5). "Chín trên sáu mươi bản ngoài miền F1 dưới 50, tức khoảng một lần trong bảy máy gần như hỏng. Đèn có bắt được đúng chín bản đó không?"**
> "Với cổng cũ đang chạy trong demo, em có số đếm. Trong 9 bản đó, 7 bản đèn đỏ, 2 bản đèn xanh là a54 và a57. a54 thuộc nhóm 7 bản nhãn đáng ngờ. Cổng 22 ca thì em chưa tính trên 60 bản sạch. Đó là việc rẻ thứ hai em sắp làm. Nếu cổng mới không bắt được những bản này, lập luận an toàn ngoài miền không đứng."
> *Nguồn: nhóm tự đếm từ `demo/results/demo_check_2modes.json → summary_by_mode.hoc.by_level.*.records` (F1 < 50: a54, a57 xanh; a02, a27, a43, a59, a60, a68, a71 đỏ); khớp `facts_phase4.json → B.peakprob_hau_kiem.lt50` = 9; `benchmark_dpss/eval_cinc60_sach.json → meta.bad_annotation`.*

**A21 (Khối 8c — Q6). "60 bản CinC có nhãn. Sao không lấy một phần để tinh chỉnh, phần còn lại để kiểm? Bốn cách thích nghi miền có cách nào dùng nhãn không?"**
> "Em không tách vì không biết bản nào cùng một sản phụ. Một nguồn góp 14 bản vào cuộc thi, cả 14 từ một người. Tách ngẫu nhiên theo bản thì có thể rò rỉ đúng kiểu em vừa rút.
> Bốn cách thích nghi miền đều không dùng nhãn CinC. Đó là chặn điện lưới thích nghi, tự huấn luyện bằng nhãn giả, AdaBN và TENT. Nhãn CinC chỉ dùng ở bước chấm cuối. Siêu tham số chọn hoàn toàn trên dữ liệu nguồn. Nên tinh chỉnh có dùng nhãn thì em chưa thử."
> *Nguồn: `adapt/adapt_run.py` dòng 7–19 ("không phương pháp nào đọc nhãn của miền đích"); `adapt/adapt_results.json → meta.quy_tac_nhan`; `survey/ro_ri_vanlieu.json → kiem_cheo_ky_thuat.cung_san_phu_khac_buoi`.*

**A22 (Khối 4 — Q7). "Dữ liệu huấn luyện chủ yếu là chuyển dạ và bản ghi ngắn. Ứng dụng em nói là theo dõi tại nhà, lâu hàng chục phút, mẹ cử động. Dữ liệu có đại diện không?"**
> "Không đại diện, em ghi vào giới hạn. ADFECGDB và Silesia B2 là chuyển dạ, năm phút. B1 là thai kỳ, hai mươi phút, nhưng nhãn gián tiếp. CinC mỗi bản một phút. Em chưa kiểm hiệu năng theo tuổi thai hay theo cử động của mẹ. Kịch bản tại nhà là động cơ, chưa phải điều em đã chứng minh."
> *Nguồn: `analysis/DULIEU.md` dòng 307–308, 585–588; `survey/survey_raw.json` dòng 282.*

### A3-bis — Trường hợp a02: trả lời trung thực trong 60 giây

Dùng khi giảng viên chỉ vào hộp vàng bước 4 và hỏi "sao không chọn dây 1?".

> "Cô nhìn đúng. Ở a02, dây 1 được 75,9. Dây hệ thống chọn chỉ 24,9.
>
> Em nói ba điều. Một, em so bảy cách chọn không nhìn đáp án. Sáu cách chọn dây 2, kể cả quy tắc cũ, gate theo kế hoạch và gate4. Cách thứ bảy chọn dây 3. Không cách nào chọn dây 1. Nên lỗi này không riêng quy tắc mới.
>
> Hai, lý do em đoán: quy tắc mới chọn dây mà mạng tự tin nhất. Ở a02, mạng tự tin trên nhịp mẹ, vì nhịp mẹ đều và rõ. Đó là giới hạn gắn với mọi quy tắc dựa trên độ tự tin của mạng.
>
> Ba, giá trung bình của chọn mù em đã báo đủ. Cũ 74,28, gate theo kế hoạch 80,72, gate4 81,01, peakprob 82,01, trần 83,60.
>
> Điều hệ thống làm đúng ở a02: nó không đưa con số sai cho người đọc. Máy tính ra 130 nhịp mỗi phút, đáp án là 160. Đèn đỏ bật, ô nhịp tim bị gạch. Nên bản này là thất bại của khâu chọn dây, và là thành công của khâu từ chối. Dây 1 cho nhịp tim 156, gần đáp án.
>
> Hướng sửa em nghĩ tới là loại dây bám nhịp mẹ trước khi chọn. Nhưng em chưa đo. Nếu làm, đó lại là một quy tắc hậu kiểm, phải kiểm trên dữ liệu mới. Và thiết bị thật chỉ có một dây thì không có dây 1 để chọn."

*Nguồn:* `analysis/chonkenh_results.json → F1_tung_ban_ghi.cinc.a02` (lead0 75,88; psd = gate = gate4 = rrcv = peakprob = rrplaus 24,91; learned 19,86; oracle 75,88), `→ chon_kenh_theo_quy_tac.cinc.a02`; `demo/results/demo_check_showcase.json → rows.a02_leadpeakprob` (nhịp tim TB 129,9 dây 2, 156,1 dây 1; `n_labels` 160 / 60 s; `lead_scores` dây 2 0,970 cao nhất); 80,72 / 81,01 / 82,01 / 83,60 — `analysis/dulieu_results.json → chon_kenh_60_sach.bang`, cùng số ở `facts_phase4.json → B`. [SUY LUẬN] "vì nhịp mẹ đều và rõ". [SỰ KIỆN] chưa đo dây 1 có bám mẹ hay không.

---

# Phụ lục B — Điều tuyệt đối không nói

### B1. Không nhận quyền ưu tiên về chồng lấn dữ liệu

Không dùng câu nào hàm ý nhóm là người tìm ra việc bộ thi chứa bản ADFECGDB.

**Thay bằng:** *"Cuộc thi 2013 có 447 bản, ban tổ chức ghi trong kỷ yếu 2013 và bài tổng kết 2014 rằng 25 bản lấy từ ADFECGDB. Nhóm em đo và định danh được 15 bản trong set-a, và đo mức thổi phồng."*

**Vì sao:** Silva 2013 (CinC 40:149, Bảng 1) và Clifford 2014 (Physiol Meas 35:1521) đã ghi. Cảnh báo còn nằm trong ghi chú đọc bài của chính nhóm ở p13, p20. *Nguồn: `facts_phase4.json → A.co_so`; `survey/ro_ri_vanlieu.json`.*

### B2. Không kết luận mô hình đã đủ tốt, không quy khoảng cách ngoài miền cho dữ liệu

**Thay bằng:** *"Cùng quy tắc chọn dây cũ, trong miền 97,56, ngoài miền 74,28: chênh 23,28 điểm. Bốn cách thích nghi miền đều thất bại. Nguyên nhân em chưa xác định được."*

**Vì sao:** kết luận cũ dựa trên phép thử "nhìn thấy tín hiệu", mà phép thử đó có âm tính giả 17,97 % [12,13; 24,97] trên 60 bản sạch, lên 55–70 % ở bản khó. **Không dùng số khoảng cách cũ** trong `adapt/adapt_results.json → mo_phong_dich_chuyen.khoang_cach_CinC_con_lai`, vì nó được tính từ mốc 75 bản đã rút (Khối 8c, chú thích). *Nguồn: `facts_phase4.json → C.phep_thu_nhin_thay`, `Z_DA_RUT.cum_tu`.*

### B3. Không dùng chữ nào hàm ý nghiên cứu đã đăng ký với bên thứ ba

**Thay bằng:** *"Em khai báo trước phép tính trong một tệp trên máy, rồi mới chạy."* Nếu bị hỏi tiếp: *"Tệp khai báo cho quy tắc chọn dây chưa được neo vào lịch sử mã, và viết sau khi đã thấy điểm từng dây. Chỉ tệp khai báo ở vòng bảy là được neo."*

**Vì sao:** đăng ký với bên thứ ba có dấu thời gian không sửa được. Nhóm không làm điều đó. *Nguồn: `facts_phase4.json → B.khai_bao_truoc`, `C.git_khai_bao`.*

### Câu ngắn cũng nằm trong danh sách cấm

| Câu cấm | Thay bằng |
|---|---|
| "Một dây tốt hơn bốn dây" | "Một dây bù được 89,49 % lợi ích của bốn dây; trung bình vẫn kém 1,27." |
| Nâng hạng tạp chí đo lường sinh lý lên trên hạng thật | "Tạp chí xếp Q2 theo Scimago 2024, nhưng là nơi cộng đồng điện tim thai công bố." |
| Mọi chữ kiểu "tốt nhất hiện nay", "chưa ai làm" | "Đây là phép đo của em trên dữ liệu của em, so với phương pháp em chạy lại được." |
| Kỳ hội nghị điện tim tháng 9 năm nay như đích nộp | "CinC 2027, hạn khoảng tháng tư, ngày chưa xác nhận." |
| "Đèn không lấy từ mạng", "đèn không sụp cùng mạng" | "Đèn dùng 12 chỉ số, 6 lấy từ đầu ra của mạng; đèn không độc lập với mạng." |
| Đọc 0,934 khi nói về đèn trong demo | "Đèn demo là cổng cũ, trong bản ghi 0,721 khi ghép mô hình 5 ca; ghép mô hình 22 ca đang chạy thì chưa đo lại. Cổng 22 ca 0,934 mới ở dạng phân tích." |
| "Không dây nào cứu được" (a02) | "Dây 1 đạt 75,88, nhưng 6 trên 7 cách chọn không nhìn đáp án chọn dây 2, không cách nào chọn dây 1." |
| Số chệch STV ngoài miền | "Ngoài miền em chưa có số STV dùng được." |
| "Khoảng cách 15 điểm", "15 đến 23", "gần 18" | "Cùng quy tắc cũ chênh 23,28; gate theo kế hoạch 16,84; gate4 16,55; quy tắc hậu kiểm 15,55; trần 13,96." |
| "Set-a chứa 25 bản ADFECGDB" | "Cuộc thi 447 bản có 25 bản từ ADFECGDB; em định danh 15 bản trong set-a." |
| "Peakprob là quy tắc đã xác nhận" | "Peakprob là giả thuyết hậu kiểm. Quy tắc kế hoạch chọn là gate, 80,72, trượt Holm; gate4, cũng ghi trước khi chạy, 81,01, qua Holm." |
| "gate thắng", "gate gần đạt", "gate4 là quy tắc em chỉ định" | "Gate là quy tắc kế hoạch chọn, p Holm 0,051: không đạt. Gate4 qua Holm nhưng không phải quy tắc kế hoạch chọn." |

---

# Phụ lục C — Biến thể 15 phút

| Khối | Giữ / bỏ | Phút | Ghi chú |
|---|---|---:|---|
| 1 Bài toán | **Giữ, rút** | 1,5 | Bỏ slide CTG chi tiết, giữ hai câu hỏi, người dùng giả định, ranh giới "chưa gặp bác sĩ" |
| 2 Vì sao một điện cực | **Rút** | 0,5 | Chỉ câu "một dây không dư thừa nên cần đèn" |
| 3 Hình H1 + r01 + H2 | **Giữ** | 2 | Demo r01 chỉ bước 1, 3, 5 |
| 4 Dữ liệu | **Rút** | 1 | Bảng bốn bộ; câu 447 / 25 / 15 |
| 5 Năm bước | **Rút** | 0,5 | Chỉ câu "đèn dùng 6/12 chỉ số từ mạng, không độc lập với mạng" |
| Khái niệm | **Rút** | 0,5 | Chỉ khoảng tin cậy và hậu kiểm; phát tờ bảng khái niệm |
| 6 Một so bốn | **Giữ nguyên** | 2 | Bảng ba dòng là trục của cả buổi |
| 7 Đối chuẩn | **Rút** | 1 | Ba mức công bằng; Power-MF hai câu; DPSS chưa chạy lại |
| 8 Kết quả + demo | **Rút** | 3,5 | 8a: năm số 74,28 / 80,72 / 81,01 / 82,01 / 83,60 + a09 bước 4 (1,5′). 8b: hai cổng + a02 bước 4 và 5 (1,5′). 8c: một câu âm tính (0,5′). Bỏ a27 |
| 9 Khi hệ sai | **Rút** | 0,5 | Chỉ H5 và câu "3 xanh sai, 0 đỏ mà F1 ≥ 90" |
| 10 Mô hình | **Rút** | 0,5 | "Ba họ đầu cách nhau 0,02; ×4 tham số +0,26" |
| 11 Văn liệu | **Bỏ** | — | Phát tờ `docs/TOM_TAT_30_BAI.md` |
| 12 Đã rút | **Rút** | 0,5 | "Em tự rút năm tuyên bố; nếu cô muốn nghe, em kể riêng." |
| 13 Đóng góp | **Giữ, rút** | 0,5 | Bốn đóng góp, mỗi cái một câu kèm ranh giới |
| 14 Định vị | **Giữ, rút** | 0,5 | Ba việc xin cô + câu pháp lý |

**Tổng:** 15 phút. **Không bao giờ cắt:** khối 6, câu "đèn không độc lập với mạng", hộp vàng a02, câu pháp lý.

---

# Phụ lục D — Bảng đối chiếu con số với tệp nguồn (cập nhật 17/09/2026, vòng 10)

Cột "Khớp": ✓ đã mở tệp và khớp · ✓ tự tính · ⚠ có lưu ý · ✗ không dùng.

### D1. Trong miền, 22 sản phụ

| # | Con số trong kịch bản | Giá trị trong tệp | Tệp → trường | Khớp |
|---|---|---|---|---|
| 1 | RelyFetal 97,56 | 97,5564 | `baselines/powermf_fair_stats.json → so_sanh.tat_ca_22.rely_vs_pmf4.mean_a` | ✓ |
| 2 | Power-MF 4 dây 98,83 | 98,8307 | `→ rely_vs_pmf4.mean_b` | ✓ |
| 3 | Power-MF 1 dây 86,71 | 86,7094 | `→ rely_vs_pmf1.mean_b` | ✓ |
| 4 | −1,27 [−3,08; +0,27], p 0,156, 18/0/4 | −1,2743 [−3,0759; +0,2651], 0,1560, 18/0/4 | `→ rely_vs_pmf4` | ✓ |
| 5 | +10,85 [+6,80; +15,40], 22/0/0 | +10,8470 [6,8008; 15,3994] | `→ rely_vs_pmf1` | ✓ |
| 6 | 12,12 [6,90; 18,27] | −12,1212 [−18,2721; −6,9018] | `→ pmf1_vs_pmf4` | ✓ |
| 7 | 89,49 % [81,4; 103,2]; jackknife 88,6–93,4 | 89,49 [81,4; 103,16]; [88,62; 93,43] | `analysis/recovery_ratio.json` | ✓ |
| 8 | Trung vị +0,23; bốn người kém: B1_07 −12,88, B1_06 −10,51, B2_03 −9,77, B1_10 −1,86 | tự tính từ `per_subject` | `→ per_subject` | ✓ tự tính |
| 9 | 99,40 trên 5 ADFECGDB | 99,397 | `→ per_subject` (trung bình 5 bản) | ✓ tự tính |
| 10 | B1 Power-MF sau vá 99,40 vs tác giả 99,46 | đúng | `baselines/BASELINES.md` dòng 76; `baselines/powermf_published.json → b1_powermf` | ✓ |
| 11 | Sót 1.006, thừa 1.035, đúng 35.307 | đúng | `analysis/chandoan_results.json → pho_loi.22_chu_the_kenh_PSD` | ✓ |
| 12 | Phổ lỗi 3,82 % vs ngẫu nhiên 14,66 % (đọc 14,7) | 3,8217 / 14,6568 | `→ pho_loi.22_chu_the_kenh_PSD` | ✓ |
| 13 | Seed 97,56 vs 97,59 | 97,5564 / 97,5881 | `facts_phase4.json → C_xac_nhan_vong7.seed.chi_tiet.bang.F1_psd` | ✓ |
| 14 | STV +0,33 ms, n = 5, STV nhãn TB 9,62 ms | 0,3286; 9,6248 | `analysis/clinical_results.json → summary.ADFECGDB` (mô hình 5 ca để-một-ra) | ✓ |
| 15 | n ≈ 50 | "n ≈ 50 chủ thể" | `analysis/LUONGCUC.md` dòng 210 | ✓ |

### D2. Ngoài miền, 60 bản CinC sạch

| # | Con số | Giá trị | Tệp → trường | Khớp |
|---|---|---|---|---|
| 16 | PSD 74,28 [66,63; 81,78], lt50 16 | đúng | `facts_phase4.json → A_cinc2013_60_ban_sach.psd` | ✓ |
| 17 | gate 80,72, +6,44 [2,49; 11,10], Holm 0,051, lt50 12 | đúng | `→ B_chon_kenh_7_quy_tac_60_sach.gate_chi_dinh_truoc` | ✓ |
| 18 | gate4 81,01, +6,72 [2,85; 11,18], Holm 0,015, lt50 12 | đúng | `→ B.gate4` | ✓ |
| 19 | peakprob 82,01, +7,73 [3,82; 12,41], Holm 0,0039, 19/6/35, lt50 9 | đúng | `→ B.peakprob_hau_kiem` | ✓ |
| 20 | Oracle 83,60 [77,57; 89,17], lt50 8; dư địa 82,92 % | đúng | `→ B.oracle_F1`, `→ A.oracle`, `→ B.peakprob_phan_tram_du_dia_oracle` | ✓ |
| 21 | peakprob kém PSD nặng nhất 3,90 (a57); bằng oracle 48/60; kém oracle > 10: a02 50,97, a57 21,26 | tự tính | `analysis/chonkenh_results.json → F1_tung_ban_ghi.cinc` (loại 15 bản) | ✓ tự tính |
| 22 | 15 bản trùng, NCC 1,0, lệch RR 0,0 ms, thổi phồng 3,27–7,18 | đúng | `facts_phase4.json → A_cinc2013_60_ban_sach` | ✓ |
| 23 | 447 bản; 25 bản từ ADFECGDB; không nói bản nào ở tập nào | đúng | `survey/ro_ri_vanlieu.json` (Silva 2013 Bảng 1; Clifford 2014 Bảng 2) | ✓ |
| 24 | 7 bản nhãn đáng ngờ a33 a38 a47 a52 a54 a71 a74 | đúng | `benchmark_dpss/eval_cinc60_sach.json → meta.bad_annotation` | ✓ |
| 25 | Power-MF 1 dây 55,97 [48,08; 64,03] | đúng | `facts_phase4.json → A.powermf_1ch_60_sach` | ✓ |
| 26 | Power-MF 4 dây 93,12 | số dẫn xuất | `baselines/powermf_published.json → challenge_powermf`; `docs/CONG_BANG_DOI_CHUAN.md` dòng 33 | ⚠ dẫn xuất |
| 27 | m5 64,04 → m12 67,93 → m22 74,28; bỏ B1 −6,35 [4,04; 8,95] | đúng | `→ A.psd`; `analysis/DULIEU.md` dòng 134, 393, 600 | ✓ |
| 28 | Thích nghi miền +0,25 / −0,67 / −1,58 / −2,43 (notch 74,53 · pl 73,61 · AdaBN 72,70 · TENT 71,85) | tự tính lại, khớp | `adapt/adapt_results.json → per_record_cinc.*.F1_psd` (loại 15 bản) | ✓ tự tính |
| 29 | Bốn cách thích nghi không đọc nhãn đích | đúng | `adapt/adapt_run.py` dòng 7–19; `adapt/adapt_results.json → meta.quy_tac_nhan` | ✓ |
| 30 | Dải lọc +2,44 [−0,04; +6,29]; −0,07 [−0,51; +0,39] | đúng | `facts_phase4.json → E_dai_loc_tren_TCN` | ✓ |
| 31 | Âm tính giả 17,97 % [12,13; 24,97]; 55 % (50 ≤ F1 < 90), 70 % (F1 < 50) | 0,1797; 0,5521; 0,6955 | `→ C.phep_thu_nhin_thay.chi_tiet.ti_le_am_tinh_gia` khoá `cinc60` + `psd` | ✓ |
| 32 | Khoảng cách trong/ngoài: 23,28 (PSD) · 16,84 (gate) · 16,55 (gate4) · 15,55 (peakprob) · 13,96 (oracle) | tự tính: 97,5564 trừ từng số (gate: 97,5564 − 80,7158 = 16,8406) | D1 #1 và D2 #16–20; `analysis/dulieu_results.json → chon_kenh_60_sach.bang.*.mean_60_sach` | ✓ tự tính |
| 33 | **Khoảng cách cũ trong `adapt/`** (không in lại số) | 97,3166 − mốc PSD 75 bản đã rút | `adapt/adapt_results.json → mo_phong_dich_chuyen.khoang_cach_CinC_con_lai`; `adapt/adapt_analyze.py` dòng 15, 76 | ✗ **không dùng** |

### D3. Đèn tin cậy và demo

| # | Con số | Giá trị | Tệp → trường | Khớp |
|---|---|---|---|---|
| 34 | 12 chỉ số: 2 xác suất mạng, 4 trên nhịp mạng tìm, 6 thuần tín hiệu | đúng | `fsqi/gate.py` dòng 61–78; `fsqi/fsqi.py` dòng 293–319; `fsqi/eval_fsqi.py` dòng 50–51 | ✓ |
| 35 | Độ quan trọng: `rr_cv` 0,140; `peak_prob_mean` 0,032; mười khoá còn lại trị tuyệt đối < 0,002 | 0,1404; 0,0318; lớn nhất −0,0017 (`prob_max`) | `analysis/gate22_results.json → cong.permutation_importance_delta_auroc` (cổng 22 ca) | ✓ |
| 36 | Cổng 22 ca: AUROC trong bản ghi 0,934 [0,872; 0,981], 11/22; gộp 0,965; đoạn xấu 5,40 % | 0,9336 [0,8717; 0,9810]; 11; 0,9646; 0,0540 | `→ cong` | ✓ (chỉ phân tích) |
| 37 | Cổng cũ trong demo: AUROC trong bản ghi 0,721 [0,517; 0,898], 5 bản CinC a01 a06 a07 a09 a10, ghép mô hình 5 ca; ghép mô hình 22 ca chưa đo lại | 0,72097 [0,51685; 0,89847]; `n_ban_ghi_co_ca_2_lop` 5 | `analysis/stats_results.json → comparisons.gate_auroc_cinc.auroc_TRONG_ban_ghi`, `.auroc_tung_ban_ghi`; `analysis/GATE22.md` dòng 69–71 | ✓ (chưa đo với mô hình 22 ca) |
| 38 | Demo dùng cổng cũ `fsqi/gate_classical.pkl`, học trên 5 ca | đúng | `analysis/GATE22.md` dòng 364–366; `demo/results/demo_check_2modes.json → gate_note, gate.trained_on` | ✓ |
| 39 | 1/1540; 5/24 | đúng; C(22,3) = 1540 | `analysis/GATE22.md` dòng 127, 304; `→ muc_ban_ghi.so_quy_tac_mot_dac_trung_bat_du_3` | ✓ |
| 40 | Bỏ 3 người: 99,50 vs 99,23, +0,27 [−0,02; +0,48], 86,4 % / 82,7 % | 99,5002 / 99,2305 / 0,2697 [−0,0229; 0,4850] / 86,36 / 82,70 | `→ rui_ro_do_phu_ban_ghi.do_phu_dau_tien_hieu_khong_am` | ✓ |
| 41 | Top 4 cổng 22 ca = B2_03, B1_07, B1_06, B1_10 | đúng | `→ muc_ban_ghi.top4` | ✓ |
| 42 | Demo 82 bản: xanh 46 (43 ≥ 90, 3 < 90) · vàng 17 (15 / 2) · đỏ 19 (0 / 19) | tự đếm | `demo/results/demo_check_2modes.json → summary_by_mode.hoc.by_level.*.records`; khớp `facts_phase4.json → F_demo.summary_by_mode.hoc` | ✓ tự đếm |
| 43 | Xanh mà F1 < 90: a52 85,39 · a54 38,79 · a57 17,02; đỏ mà F1 ≥ 95: 0; đỏ cao nhất 87,09 | đúng | `facts_phase4.json → F_demo`; đỏ cao nhất tự đếm | ✓ |
| 44 | Chế độ luật: 5 bản xanh mà F1 < 90 | đúng | `→ F_demo.summary_by_mode.luat` | ✓ |
| 45 | Độ phủ demo: xanh 56,10 %, không đỏ 76,83 % | đúng | `demo/results/demo_check_2modes.json → summary_by_mode.hoc` | ✓ |
| 46 | F1 < 50 ngoài miền: 9 bản; 7 đỏ, 2 xanh (a54, a57) | tự đếm | như #42 | ✓ tự đếm |
| 47 | r01: F1 99,92; TP 644, FP 1, FN 0 | đúng | `demo/results/demo_check_showcase.json → rows.r01_leadpeakprob.metrics` | ✓ |
| 48 | a09: PSD dây 2 F1 19,35 → peakprob dây 1 F1 94,25; gate và gate4 cũng dây 1; 13 xanh / 1 vàng / 1 đỏ | đúng | `→ rows.a09_leadpeakprob`; `analysis/chonkenh_results.json → chon_kenh_theo_quy_tac.cinc.a09` | ✓ |
| 49 | a02: dây 2 F1 24,91; dây 1 75,88; dây 3 19,86; dây 4 24,49; nhịp TB máy 130 (dây 1: 156); đáp án 160; bám mẹ 78 %; 6 đỏ / 9 vàng / 15 đoạn; 6/7 cách chọn dây 2, learned chọn dây 3, không cách nào chọn dây 1 | 129,9; 156,1; `n_labels` 160 / 60 s; 0,783 | `→ rows.a02_leadpeakprob`; `analysis/chonkenh_results.json → *.cinc.a02`; trưởng nhóm đo lại 17/09 | ✓ |
| 50 | a27: bốn dây 23,26 / 21,26 / 32,94 / 30,23; chọn dây 3; 14 đỏ / 1 vàng | đúng | `→ rows.a27_leadpeakprob` | ✓ |
| 51 | Thời gian bản 60 giây: lọc + khử mẹ 6,2 ms; mạng 1 dây 129 ms; 4 dây 513 ms; cổng bản 5 phút 1.041 ms (sửa 17/09: trước ghi 2.963 ms lấy từ lần chạy khác) | đúng | `demo/results/demo_check_showcase.json → rows.a09_leadpeakprob.latency_*` và `→ rows.r01_leadpeakprob.confidence.components.gate_ms` | ✓ |
| 52 | Số kiểm thử: 109 (43 trong `tests/` + 66 trong `demo/test_core.py`); 22 kiểm thử chế độ trình bày | 109 collected; 22/66 với `-k trinh_bay` | `python -m pytest --collect-only -q tests/ demo/test_core.py` (17/09/2026, sau lượt sửa thứ ba; D-sync2 chỉ đếm, không chạy toàn bộ) | ✓ đếm; ⚠ chưa chạy lại toàn bộ |

### D4. Mô hình, dữ liệu, văn liệu, định vị

| # | Con số | Giá trị | Tệp → trường | Khớp |
|---|---|---|---|---|
| 53 | 113.481 tham số; 1.516 ms; 0,48 MB; 4,35 ms/cửa sổ; nhanh hơn thời gian thực 920 lần | đúng | `survey/facts_verified.json → mo_hinh` | ✓ |
| 54 | 7 họ: 97,64 / 97,63 / 97,62 / 96,93 / 96,84 / 96,38 / 94,53; trường nhìn 1.516 / 3.052 / 2.716 / 748 / 1.508 / 636 / 60 | đúng | `analysis/kientruc_results.json → table` | ✓ |
| 55 | cnn_l kém 3,10; 2 hơn / 20 kém; tham số ±2,7 % | −3,1029; 2/20; 2,67 % | `→ comparisons.cnn_l.all22`; `→ table.rf_wide.params_pct_vs_tcn` | ✓ |
| 56 | ×4 tham số +0,26 | +0,26 | `analysis/CHANDOAN_MOHINH.md` dòng 22, 242 | ✓ |
| 57 | 22 = 5 + 7 + 10; B1 76,9 % thời lượng; 36.313 nhịp | đúng | `analysis/DULIEU.md` §1.4, dòng 585–588 | ✓ |
| 58 | Tuổi thai B1 32–42 tuần, 20 phút; B2 38–42 tuần, chuyển dạ, 5 phút | đúng | `survey/survey_raw.json` dòng 282 | ✓ |
| 59 | TDA 27,4 vs 97,1 | 27,42 / 97,14 | `survey/facts_verified.json → tda_da_bac_bo` | ✓ |
| 60 | DPSS 97,7 (22 bản Silesia, bài gọi ADFECGDB); hướng ba: trong miền 96,5–99,7 (Asadi 96,52 · Chen 99,17 · Mohebbian 99,7 ở 30 ms), ngoài miền Orvas 77,8 (75 bản) đến Asadi 97,97 (80 kênh chọn); Castillo 94,11 / 98,07 (26 bản) thuộc nhóm cổ điển | số trích | `survey/facts_verified.json → doi_chuan_dpss`; `bao_cao_30_paper.tex` p03, p06, p07, p11, p17 | ⚠ số trích |
| 61 | Bộ thứ ba không có; 86 nhịp/phút | đúng | `facts_phase4.json → C.bo_thu_ba` | ✓ |
| 62 | PM Q2 Scimago 2024 | đúng | `→ G_venue` | ✓ |

### D5. Quy đổi nhóm tự tính (hộp "Con số này nghĩa là gì")

Giả định chung: 100 − F1 ≈ số nhịp sai trên 100 nhịp máy báo, khi sót ≈ thừa. Nhịp ví dụ 140 lần/phút.

| Phép tính | Kết quả |
|---|---|
| 100 − 97,56 · × 1,4 | 2,44 · 3,42 nhịp sai/phút |
| 100 − 98,83 · × 1,4 | 1,17 · 1,64 |
| 2,44 / 1,17 | 2,09 (gấp khoảng hai) |
| 100 − 86,71 · 13,29 / 1,17 · 13,29 / 2,44 | 13,29 · 11,4 · 5,4 |
| 10,8470 / 12,1212 | 0,8949 |
| 100 − 74,28 / 80,72 / 81,01 / 82,01 / 83,60 | 25,72 / 19,28 / 18,99 / 17,99 / 16,40 |
| 25,72 / 2,44 · 17,99 / 2,44 · 16,40 / 2,44 | 10,5 · 7,4 · 6,7 |
| 16 / 60 · 9 / 60 | 27 % · 15 % |
| 60.000 / 140 · 50 / 428,6 · 100 / 428,6 | 428,6 ms · 0,117 (≈ 1/9) · 0,233 |
| 1.516 / 428,6 · 60 / 428,6 | 3,54 nhịp · 0,14 (≈ 1/7) |
| 4.000 / 4,35 | 919,5 (tệp ghi 920) |
| 46 / 82 · 63 / 82 | 56,1 % · 76,8 % |
| C(22,3) | 1.540 |
| 1 / 0,1797 | 5,6 |
| 50 / 22 | 2,3 |

### D6. Số không dùng trong kịch bản này

| Số / câu | Vì sao |
|---|---|
| Khoảng cách cũ `adapt/adapt_results.json → mo_phong_dich_chuyen.khoang_cach_CinC_con_lai` | Tính từ mốc PSD 75 bản đã rút (D2 #33) |
| Chệch STV trên CinC mẫu 10 bản | Mẫu a01–a10 chứa 4 bản nhiễm; F1 mẫu này trong `Z_DA_RUT.cinc_mau_10` |
| AUROC cổng đo trên CinC 75 bản | 75 bản nhiễm (`HANDOFF.md` §8.4) |
| F1 98,46 của a09 | Chỉ 30 giây đầu (`HANDOFF.md` §8.4) |
| Mọi số trong `Z_DA_RUT` | Đã rút |
| "Thắng oan chín điểm" | Không có trường nguồn |

---

## Kiểm 15 phút trước buổi

1. `python -m pytest tests/ demo/test_core.py -q` — kỳ vọng **109 kiểm thử được thu thập, 0 failed** (43 trong `tests/` + 66 trong `demo/test_core.py`); đủ dữ liệu thì 109 passed, bản thiếu dữ liệu thì skipped là bình thường. Bộ đầy đủ chưa chạy lại sau lượt sửa thứ ba (xem D3 #52). Riêng chế độ trình bày: `-k trinh_bay`, 22 kiểm thử. Không ghi số kiểm thử lên slide.
2. `python demo/smoke_app.py` — dòng cuối bắt đầu bằng `KẾT QUẢ: ĐẠT`. Rồi `python demo/run_check.py --only r01,a09,a02,a27 --mode hoc --out demo_check_4the --threads 2` (ghi vào `demo/results/`) — xác nhận 99,92 · 94,25 · 24,91 · 32,94.
3. Mở demo ở chế độ trình bày, kiểm các chỗ sau (đã có trong demo sau lượt sửa thứ ba, xem ảnh `demo/screenshots/17..23`):
   * tiêu đề ghi *chỉ cần một kênh*; ô F1 của thanh tóm tắt ghi *F1 (bắt đủ và báo đúng, 100 là hoàn hảo)*;
   * năm thẻ có tên ca: *Ca dễ* · *Chọn dây quyết định* · *Máy bám nhầm tim mẹ* · *Bốn dây đều kém* · *Tệp của bạn*; thẻ CinC ghi *nguồn thiết bị từng bản không được công bố*;
   * r01 bước 1, hộp *Cách đọc hình*: *Ở dây này gai của bé to ngang gai của mẹ* …; bước 3: *vạch tím đậm là nhịp mạng đã báo, chưa biết đúng hay sai*;
   * bước 5, chú thích: *Xanh không bảo đảm là đúng: trong 82 bản đã chấm có 3 bản đèn xanh mà F1 dưới 90, thấp nhất 17,02.*;
   * a02 bước 4 có **hộp vàng** *Dây 1 đạt F1 75,88, nhưng hệ thống chọn dây 2 (F1 24,91). 6/7 cách chọn dây không nhìn đáp án mà nhóm đã so cũng chọn dây 2. Không cách nào chọn dây 1.* …;
   * a02 thanh tóm tắt: ô nhịp tim **gạch ngang**, chữ *đèn đỏ: không dùng số này*;
   * dòng dưới thanh tóm tắt ghi đủ **74,28 · 80,72 · 81,01 · 82,01 · 83,60**;
   * bước 5 có ghi chú *Đèn trong bản demo này dùng cổng hiệu chuẩn trên mô hình 5 sản phụ.* … *ghép với mô hình 22 sản phụ đang chạy thì chưa đo lại.*
   Nếu một chỗ khác màn hình, sửa lời thoại tương ứng ở Khối 3 và Khối 8 cho khớp màn hình.
4. Ảnh dự phòng `demo/screenshots/` đã chụp lại sau lượt sửa thứ ba (17/09 22:01–22:02). Thứ tự chiếu khi demo hỏng: `17_the_r01` → `18_the_a09` → `21_a09_buoc4` → `19_the_a02` → `23_a02_buoc4` → `22_a02_buoc5` → `20_the_a27`. Chỉ kịp một ảnh thì `21_a09_buoc4`. Không sửa mã trước mặt cô. Thời gian trong `screenshots_v2.json` là một lần đo: không dùng để kết luận demo nhanh hay chậm. Nếu dòng trạng thái chuyển nền đỏ (*Không phân tích được bản ghi …*), hình bên dưới vẫn là bản ghi trước: bấm lại thẻ.
5. **Không mở làm ví dụ ngoài miền:** a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25.
6. Kiểm tờ phát tay trước khi in:
   * `docs/TOM_TAT_1_TRANG.md`: dòng 21, 26, 27 đã sửa (0,934 kèm phạm vi 11/22; 23,28 / 16,84 / 15,55; STV chỉ +0,33 ms trong miền, n = 5). Kiểm lại dòng 5 (câu "thai chậm phát triển … thai lưu" đã hạ và gắn [CẦN KIỂM BẢN GỐC]) và dòng 9 (số dòng mã ≈ 31.000) trước khi in.
   * `docs/TOM_TAT_30_BAI.md` hướng 5 đã ghi đúng "447 bản có 25 bản từ ADFECGDB; định danh 15 bản trong set-a".
   * In hai bản bảng *"Những khái niệm cần hiểu trước"*.
7. `docs/HUONG_DAN_DEMO_v2.md` đã đồng bộ với demo sau lượt sửa thứ ba (mọi chuỗi giao diện đối chiếu tự động với `demo/app.py`, `demo/core.py`, `fsqi/gate.py`: 329/329 khớp); lời thoại a02 ở đó khớp Khối 8b. Hai câu hỏi hay gặp mới: đèn xanh mà vẫn sai (a57) ở mục 4.4, vì sao lúc nhanh lúc chậm ở mục 4.5. Không in `HUONG_DAN_DEMO_v1.md` làm tài liệu phát.
8. Mở sẵn `survey/facts_phase4.json` và Phụ lục D để tra khi bị hỏi số.
9. Đặt `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1` trước khi chạy demo.
10. **Không mang** bản nháp hội nghị cũ trong `paper/`, còn số 75 bản.
