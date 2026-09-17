# Kịch bản trình bày toàn bộ hành trình đề tài — RelyFetal

> **⚠ CẢNH BÁO (17/09/2026) — tệp lưu trữ.** Kịch bản này dựng quanh demo **8 tab** (S15, Phần 7) và bìa có số
> kiểm thử cố định; demo hiện mở **chế độ trình bày 5 bước**, 8 tab nằm trong chế độ chuyên gia. Buổi trình bày mới
> dùng `docs/KICH_BAN_THUYET_TRINH_v2.md` và `docs/HUONG_DAN_DEMO_v2.md`. Ngày 17/09/2026 đã sửa tại chỗ các lỗi
> sự thật: cổng từ chối **không** độc lập với mạng; "17,92 điểm" đã rút (thay bằng 23,28 theo PSD); số STV ngoài
> miền đã rút; mức ngẫu nhiên nhóm lỗi (a) lấy đúng hàng PSD; số kiểm thử.

**Bản 13/09/2026.** Dùng cho buổi trình bày **dài** (bản đầy đủ 45 phút, có bản rút 20 phút và 10 phút ở Phụ lục A).

Tệp này **không thay thế** `docs/KICH_BAN_TRINH_BAY.md`. Tệp kia là bản 20 phút cho buổi gặp giảng viên ngày 14/09, vẫn dùng nguyên. Tệp này kể **toàn bộ quá trình**: từ lúc nghĩ ra đề tài, đọc tài liệu, chọn mô hình, đến năm lần rút lại kết luận và chỗ đứng thật hiện nay.

**Nguồn sự thật:** `survey/facts_phase4.json` (mục `Z_DA_RUT` liệt kê mọi con số đã rút). Mọi con số trong tệp này đối chiếu với các tệp JSON ghi ở dòng *Nguồn* cuối từng phần.

---

## Quy ước đọc tệp này

| Khối | Nghĩa |
|---|---|
| **[NÓI GÌ]** | Lời thoại, đọc gần như nguyên văn. Câu ngắn. **Không có đường dẫn tệp trong khối này** — không ai đọc đường dẫn thành tiếng. |
| **[CHIẾU GÌ]** | Slide số mấy / tab demo nào / ảnh nào. |
| **[VÌ SAO LÀM VẬY]** | Lý do kỹ thuật. Học phần này để trả lời khi bị hỏi "tại sao". |
| **[NẾU CÓ HỎI]** | Một đến hai câu hỏi khó nhất của riêng phần đó, kèm câu trả lời. |
| *Nguồn* | Tệp JSON truy về. Chỉ mở khi được hỏi, không đọc thành tiếng. |

### Bản đồ slide (22 slide, dựng từ sổ tay HTML đã có)

| Slide | Nội dung | Lấy từ |
|---|---|---|
| S1 | Bìa: tên đề tài + 3 ô số (113.481 tham số · 22 chủ thể · 60 bản kiểm ngoài) — không ghi số kiểm thử cố định trên bìa | sổ tay mục 01 |
| S2 | Vì sao phải biết **từng nhịp** — thai chậm phát triển, biến thiên ngắn hạn | mới, vẽ tay |
| S3 | Hai cách đo hiện có: Doppler và điện cực da đầu | sổ tay mục 02 |
| S4 | Thành phần tín hiệu điện tim bụng mẹ | sổ tay mục 03 |
| S5 | Hai câu hỏi của đề tài: một kênh mất bao nhiêu, và máy có tự biết không | mới |
| S6 | Cách đọc 30 bài: 7 nhóm, bảng bài học từng bài | `bang_baihoc.tex` |
| S7 | Ghi chú p13 và p20 — chính nhóm đã ghi việc phải kiểm chồng lấn | `bang_baihoc.tex` |
| S8 | Bốn đóng góp, mỗi cái kèm ranh giới | mới |
| S9 | Đường ống 5 bước | sổ tay mục 04 |
| S10 | Mạng TCN: 113.481 tham số, trường tiếp nhận 1.516 ms, đầu ra từng mẫu | sổ tay mục 06 |
| S11 | Bảng 7 họ kiến trúc cùng tham số ±2,7 % | sổ tay mục 12 |
| S12 | Bảng 4 bộ dữ liệu + thẳng thắn về điểm yếu B1 | sổ tay mục 05 |
| S13 | Bảng 22 chủ thể: Power-MF 4 kênh / 1 kênh / RelyFetal | sổ tay mục 08 |
| S14 | Tỉ lệ lấy lại 89,49 % và khoảng tin cậy của nó | mới |
| S15 | **DEMO** — 8 tab (nay nằm trong chế độ chuyên gia; xem cảnh báo đầu tệp) | `demo/app.py` |
| S16 | Bảng 7 quy tắc chọn kênh trên 60 bản sạch, có cột p Holm | sổ tay mục 09 |
| S17 | Nhật ký sự cố 1: mẫu 10 bản ghi | sổ tay mục 11 |
| S18 | Nhật ký sự cố 2: Power-MF chạy qua Octave | sổ tay mục 11 |
| S19 | Bảng chồng lấn 15 bản: r01→a04, a05, a22 … | sổ tay mục 11 |
| S20 | Hai tuyên bố rút ở vòng 7 | mới |
| S21 | Quy trình 8 vòng, mỗi vòng có một lượt phản biện độc lập | mới |
| S22 | Bảng kết quả tổng hợp + bảng tiến độ + định vị nơi công bố | sổ tay mục 13–14 |

---

# PHẦN 1 — LÊN Ý TƯỞNG: vì sao chọn bài toán này (≈3 phút)

### [NÓI GÌ]

> "Em bắt đầu từ một câu hỏi lâm sàng, không phải từ một mô hình.
>
> Thai chậm phát triển trong tử cung là một nguyên nhân hàng đầu của thai lưu. Dấu hiệu sớm không phải nhịp nhanh hay nhịp chậm. Dấu hiệu sớm là nhịp tim thai mất biến thiên tự nhiên. Muốn đo biến thiên đó thì phải biết từng nhịp rơi vào mili-giây nào. Vì vậy em chọn bài toán định vị từng nhịp, không phải đếm nhịp trung bình.
>
> Hiện có hai cách đo. Siêu âm Doppler đo chuyển động của van tim. Nó cho nhịp trung bình tốt, nhưng thời điểm từng nhịp bị nhoè. Điện cực gắn lên da đầu thai thì cho thời điểm rất chính xác. Nhưng nó xâm lấn, và chỉ gắn được khi đã chuyển dạ.
>
> Còn một lối thứ ba. Điện tim đo từ bụng mẹ không xâm lấn, mà vẫn là tín hiệu điện. Khó ở chỗ tín hiệu tim thai nhỏ hơn tim mẹ nhiều lần. Nó lại trùng dải tần với cơ tử cung.
>
> Các nhóm khác giải bằng cách dùng bốn đến ba mươi hai điện cực rồi tách nguồn. Em hỏi ngược lại. Nếu chỉ còn **một** dây thì mất bao nhiêu? Em hỏi vậy vì em nghĩ xa tới một miếng dán mẹ tự đeo ở nhà. Bốn dây thì cần người dán đúng vị trí. Một dây thì mẹ tự dán được.
>
> Câu hỏi thứ hai em cho là quan trọng hơn. Máy có tự biết lúc nào nó không nhìn thấy tín hiệu không? Một máy đưa ra con số sai mà không cảnh báo thì nguy hiểm hơn không có máy. Em đoán bác sĩ thà nhận câu 'tôi không chắc' hơn một con số sai. Nhưng đó là em đoán. Em chưa gặp bác sĩ sản nào để hỏi."

### [CHIẾU GÌ]
S1 → S2 → S3 → S4 → S5. Dừng lâu nhất ở S3 (bảng so Doppler và điện cực da đầu) và S5.

### [VÌ SAO LÀM VẬY]
- **Vì sao định vị từng nhịp chứ không phải nhịp trung bình:** chỉ số lâm sàng mà đề tài nhắm tới là biến thiên ngắn hạn, tính từ hiệu các khoảng RR liên tiếp. Sai số thời điểm vào thẳng chỉ số đó. Nhịp trung bình thì không cần độ chính xác này.
- **Vì sao dung sai ±50 ms:** đây là quy ước chấm của cộng đồng CinC 2013, để so được với người khác. Ghi chú đọc bài p20 có nêu rằng tiêu chí chính thức của cuộc thi là sai số nhịp/phút và sai số RR chứ không phải F1 ±50 ms, nên đây là quy ước nhóm chọn, phải nói rõ trong bài.
- **Vì sao một kênh:** đây là một **câu hỏi đo được**, không phải một tuyên bố sản phẩm. Câu hỏi là "bỏ ba kênh thì mất bao nhiêu điểm", và có thể trả lời bằng một con số kèm khoảng tin cậy.
- **Vì sao cổng từ chối là đóng góp riêng:** nó tách được "máy sai" khỏi "máy biết mình sai". Với thiết bị đeo tại nhà, không có kỹ thuật viên đứng cạnh, nên việc máy tự báo mất tin cậy là điều kiện dùng được.

### [NẾU CÓ HỎI]
**H: "Biến thiên ngắn hạn phải chính xác tới bao nhiêu mili-giây thì mới có nghĩa lâm sàng?"**
> "Em chưa biết con số ngưỡng theo hướng dẫn nào, và em không đoán. Em chỉ đo được sai số của chính hệ mình. Trong miền, trên năm sản phụ, chỉ số đó lệch 0,33 mili-giây. Ngoài miền em chưa có số dùng được, vì mẫu đo cũ lẫn cả bản trùng dữ liệu huấn luyện. Nên em nói thẳng là chưa dùng làm máy đo độc lập được. Câu ngưỡng bao nhiêu là câu em muốn xin cô một đầu mối bác sĩ để hỏi."

**H: "Doppler rẻ và có sẵn, sao phải làm cái khó hơn?"**
> "Doppler đo chuyển động van nên thời điểm bị nhoè, mà đề tài của em cần đúng thời điểm. Ngoài ra Doppler cần người cầm đầu dò. Miếng dán điện cực thì mẹ tự đeo được nhiều giờ. Em không nói Doppler kém, em nói nó không trả lời được câu hỏi biến thiên."

*Nguồn: `analysis/clinical_results.json`; `de_cuong_latex/tables/bang_baihoc.tex` dòng p20.*

---

# PHẦN 2 — THU THẬP TÀI LIỆU: đọc 30 bài, và một bài học đắt (≈3 phút)

### [NÓI GÌ]

> "Em đọc 30 bài và xếp thành bảy nhóm. Nhóm học sâu dò nhịp thai. Nhóm tách nguồn. Nhóm xử lý tín hiệu cổ điển. Nhóm đối chuẩn và dữ liệu. Và ba nhóm về một hướng hình học em đã thử rồi bỏ.
>
> Cách chọn bài của em có ba tiêu chí. Một, bài phải chạy trên bộ dữ liệu công khai mà em cũng có. Hai, bài phải nói rõ giao thức chấm. Ba, ưu tiên bài có mã nguồn để em chạy lại được.
>
> Cách ghi chú thì em không tóm tắt bài. Em ghi ba cột. Cột một, so với mô hình của em thì có so được không, và vì sao. Cột hai, con số của họ đo trên đơn vị nào. Cột ba, bài học áp dụng được gì.
>
> Cột một quan trọng nhất. Phần lớn bài **không** so trực tiếp được với em. Có bài chấm trên ô 100 mili-giây, em chấm trên từng nhịp. Có bài dùng bốn kênh, em dùng một kênh. Có bài lấy đầu ra của một thuật toán khác làm nhãn chuẩn. Đặt số của họ cạnh số của em là sai.
>
> Giờ em nói một bài học đắt. Trong ghi chú của chính em, hai dòng p13 và p20 đều ghi một việc phải làm ngay. Việc đó là kiểm chồng lấn giữa bộ ADFECGDB và bộ CinC 2013. Dòng p20 còn trích nguyên câu cảnh báo của Clifford năm 2014. Em đã đọc. Em đã ghi. Rồi em không làm.
>
> Mãi tới vòng làm việc thứ bảy em mới tự đi đo, và thấy đúng mười lăm bản trùng. Bài học là: ghi chú chỉ có giá trị khi nó biến thành một việc có hạn. Bây giờ mỗi dòng bài học trong bảng của em đều phải có một mục kiểm đi kèm."

### [CHIẾU GÌ]
S6 (bảng 7 nhóm, đếm số bài từng nhóm) → S7. Ở S7 chiếu **đúng hai ô** p13 và p20, phóng to câu "kiểm tra chồng lấn giữa ADFECGDB và CinC 2013". Đây là slide gây ấn tượng nhất của cả buổi — để im ba giây trước khi nói tiếp.

### [VÌ SAO LÀM VẬY]
- **Vì sao bảng ba cột chứ không phải tóm tắt:** tóm tắt bài không dùng được vào lúc viết bài báo. Cột "có so được không" mới là thứ quyết định bài nào được đưa vào bảng đối chuẩn.
- **Vì sao vẫn kể chuyện bỏ sót:** vì nếu người phản biện tự tìm ra thì nặng hơn nhiều. Và vì đó là bằng chứng cho cách làm việc hiện giờ: mỗi bài học phải gắn một mục kiểm.
- **Vì sao ba nhóm về hướng hình học vẫn nằm trong bảng:** đó là một hướng đã thử ở giai đoạn thăm dò và đã bỏ vì kết quả không ủng hộ. Giữ lại để nếu bị hỏi "sao không thử hướng khác" thì có câu trả lời bằng số.

### [NẾU CÓ HỎI]
**H: "Em đọc 30 bài trong bao lâu, và đọc toàn văn hay đọc tóm tắt?"**
> "Em đọc trong khoảng ba tuần. Không phải bài nào em cũng đọc được toàn văn. Có năm bài em không mở được toàn văn vì tạp chí đóng. Em ghi rõ năm bài đó trong phần hạn chế, và em không trích số từ bài em chưa đọc được."

**H: "Vì sao bảng của em toàn viết 'không so sánh trực tiếp được'? Nghe như né tránh."**
> "Em hiểu vì sao cô thấy vậy. Nhưng đó là kết luận có lý do ghi kèm từng dòng. Ví dụ một bài báo cáo 98,36 phần trăm độ chính xác. Họ dùng bốn kênh, cửa sổ chồng lấp chín mươi phần trăm, xáo trộn trước khi chia tập. Đặt con số đó cạnh F1 từng nhịp của em là gây hiểu nhầm. Em chỉ so trực tiếp với những phương pháp em tự chạy lại được trên đúng dữ liệu của em."

*Nguồn: `de_cuong_latex/tables/bang_baihoc.tex` (30 dòng, 7 nhóm); `survey/RO_RI_VANLIEU.md` mục 0 và mục hạn chế.*

---

# PHẦN 3 — ĐÓNG GÓP: bốn đóng góp, mỗi cái kèm ranh giới (≈4 phút)

### [NÓI GÌ]

> "Em có bốn thứ để nộp. Em nói luôn ranh giới của từng cái, vì cái nào cũng có ranh giới.
>
> **Thứ nhất là một phép đo.** Câu hỏi: một kênh lấy lại được bao nhiêu phần lợi ích của bốn kênh? Em đo được 89,49 phần trăm. Khoảng tin cậy từ 81,4 đến 103,2. Kiểm lại bằng jackknife thì nằm trong 88,6 đến 93,4. Ranh giới: đây là phép đo so với **một** phương pháp đối chuẩn, trên 22 chủ thể. Cận trên vượt 100 phần trăm nghĩa là em chưa loại được khả năng một kênh lấy lại toàn bộ. Em gọi đây là phép đo, không phải một máy dò tốt hơn.
>
> **Thứ hai là một quy tắc chọn kênh mù nhãn.** Trên 60 bản ghi ngoài miền, quy tắc cũ cho 74,28, quy tắc mới cho 82,01. Cộng 7,73 điểm. Ranh giới, và đây là ranh giới nặng nhất: quy tắc thắng là quy tắc em chọn **sau khi** nhìn kết quả. Luật ghi trước của em chỉ vào một quy tắc khác. Quy tắc đó cho 80,72, và trượt hiệu chỉnh nhiều phép thử với p bằng 0,051. Trong cùng họ đã khai báo trước, còn một quy tắc nữa cho 81,01 và sống sót với p 0,015, nhưng nó không phải quy tắc kế hoạch chọn. Em báo cáo cả ba số, không giấu số trượt.
>
> **Thứ ba là cách đo phổ lỗi có mức ngẫu nhiên đối chứng.** Em chia lỗi thành sáu nhóm. Nhưng em không dừng ở tỉ lệ. Em tính thêm: nếu gán nhãn nhóm hoàn toàn ngẫu nhiên thì tỉ lệ sẽ là bao nhiêu. Nhóm 'bỏ nhịp dù có tín hiệu' chiếm 3,8 phần trăm trong miền. Mức ngẫu nhiên là 14,7. Ngoài miền là 1,0 so với 10,3. Cặp ngoài miền đó em đo trước khi loại mười lăm bản trùng. Ranh giới: đây là đóng góp phương pháp phụ, không phải kết quả chính. Em nêu vì trong tài liệu điện tim thai em ít thấy ai đặt mức ngẫu nhiên đối chứng.
>
> **Thứ tư là định lượng hậu quả chồng lấn dữ liệu.** Em nói rõ ngay: **ban tổ chức đã ghi việc này từ 2013**, và bài tổng kết 2014 còn cảnh báo nguyên văn. Cái em làm thêm là định danh đúng mười lăm bản nào, và đo mức thổi phồng từ 3,27 đến 7,18 điểm. Ranh giới: đây không phải một phát hiện. Đây là một phép đo trên một sự kiện đã được ghi."

### [CHIẾU GÌ]
S8 — bảng bốn dòng, mỗi dòng hai cột: *đóng góp* và *ranh giới*. Hai cột bằng nhau về bề rộng, cố ý.

### [VÌ SAO LÀM VẬY]
- **Vì sao đặt ranh giới cạnh đóng góp ngay trên cùng một slide:** người phản biện sẽ tìm đúng những chỗ đó. Nêu trước thì mất chủ động ít hơn là bị hỏi.
- **Vì sao vẫn báo cáo quy tắc chọn hậu kiểm:** nó sống sót hiệu chỉnh Holm trên cả họ bảy quy tắc, p 0,0039, và nó không có siêu tham số nào để tinh chỉnh. Giấu đi thì mất thông tin; báo cáo mà không gắn nhãn hậu kiểm thì là gian.
- **Vì sao đóng góp thứ ba lại là "phương pháp":** vì tỉ lệ phần trăm của một phép phân nhóm chỉ có nghĩa khi biết mức ngẫu nhiên của chính phép phân nhóm đó. Không có mức đối chứng thì 3,8 phần trăm nghe như nhỏ mà không chứng minh được gì.
- **Cảnh báo phải nhớ khi bị hỏi sâu:** cặp số ngoài miền (1,0 so với 10,3) được đo trên **toàn bộ 75 bản**, trước khi loại 15 bản trùng. Tỉ lệ này là tỉ số giữa các nhóm lỗi nên hướng kết luận ít nhạy với việc loại bản, nhưng **con số cụ thể chưa tính lại trên 60 bản sạch**. Nếu bị hỏi chính xác thì nói đúng câu đó, đừng đọc con số như số hiện hành. Cặp trong miền (3,8 so với 14,7) đo trên 22 chủ thể nên không bị ảnh hưởng. Mức ngẫu nhiên lấy cùng hàng kênh PSD (`analysis/chandoan_results.json` → `pho_loi.*_kenh_PSD.pct_null`); cặp 15,2 / 11,2 ghi trước 17/09/2026 là hàng `peakprob`, lệch hàng.

### [NẾU CÓ HỎI]
**H: "Bốn đóng góp mà ba cái kèm chữ 'chưa xác nhận'. Vậy đóng góp chắc chắn là cái nào?"**
> "Cái chắc nhất là phép đo 89,49 phần trăm và bản kiểm toán bộ dữ liệu. Hai cái đó là số đo, chạy lại được, không phụ thuộc lựa chọn hậu kiểm nào. Quy tắc chọn kênh thì em ghi là giả thuyết mạnh. Em nghĩ một bài báo có hai phép đo chắc và một giả thuyết ghi rõ ràng thì vẫn đăng được."

**H: "Nếu cận trên khoảng tin cậy vượt 100 phần trăm, em có dám nói một kênh bằng bốn kênh không?"**
> "Không ạ. Vượt 100 chỉ nghĩa là dữ liệu của em chưa loại trừ được khả năng đó. Trung bình em vẫn thua bốn kênh 1,27 điểm. Muốn nói bằng nhau thì phải làm thử nghiệm tương đương với cỡ mẫu đủ. Em tự tính là cần khoảng 50 chủ thể, hiện em có 22."

*Nguồn: `analysis/recovery_ratio.json`; `analysis/dulieu_results.json` mục `chon_kenh_60_sach`; `analysis/gate22_results.json`; `survey/facts_phase4.json` mục A và B.*

---

# PHẦN 4 — PHƯƠNG PHÁP: năm bước, mỗi bước một lý do (≈4 phút)

### [NÓI GÌ]

> "Đường ống có năm bước. Em nói mỗi bước một câu, kèm một câu vì sao.
>
> **Bước một, lọc.** Butterworth 10 đến 60 héc, cộng khử nhiễu 50 héc, rồi hạ về 250 mẫu mỗi giây. Điểm cần nói là lọc **pha-không**. Bộ lọc thường làm trễ tín hiệu, và độ trễ đó khác nhau theo tần số. Mà đề tài của em đo đúng cái thời điểm. Nên em chạy bộ lọc hai chiều để độ trễ triệt tiêu.
>
> **Bước hai, khử tim mẹ.** Em dựng một mẫu trung vị của phức bộ mẹ. Rồi em co giãn biên độ mẫu đó cho **từng nhịp**, bằng bình phương tối thiểu. Rồi trừ đi. Vì sao từng nhịp: phức bộ mẹ không giống nhau giữa các nhịp. Mẹ thở thì lồng ngực đổi hình. Mẹ cử động thì điện cực đổi thế tiếp xúc. Trừ bằng một mẫu cố định thì để lại tàn dư đúng ở chỗ có nhịp mẹ. Tàn dư đó rất dễ bị nhận nhầm thành nhịp thai.
>
> **Bước ba, chọn kênh mù nhãn.** Trong bốn kênh, chọn một. Chọn mà không nhìn nhãn. Em sẽ nói kỹ ở phần sai lầm.
>
> **Bước bốn, mạng.** Mạng tích chập thời gian giãn nở, 113.481 tham số, 0,48 mê-ga-bai. Nó chạy 4,35 mili-giây cho mỗi cửa sổ bốn giây trên chíp thường. Điểm cần nói là đầu ra. Mạng không trả về 'cửa sổ này có nhịp'. Nó trả về một bản đồ nhiệt **từng mẫu**, dạng chuông, độ rộng 12 mili-giây. Vì sao: nếu đầu ra là cửa sổ thì sai số thời điểm bị chặn dưới bởi bề rộng cửa sổ. Còn ra từng mẫu thì em đo được sai số thật. Sai số đó là 3,76 mili-giây, trên dung sai chấm 50.
>
> **Bước năm, cổng từ chối.** Mười hai chỉ số cho mỗi đoạn bốn giây. Sáu chỉ số lấy thẳng từ tín hiệu. Bốn chỉ số tính trên các nhịp mà mạng dò ra. Hai chỉ số là xác suất của chính mạng. Nên cổng **không độc lập** với mạng, em nói luôn. Chúng vào một bộ phân loại nhỏ cho ra xác suất 'đoạn này không đáng tin'. Đánh giá bỏ-một-chủ-thể trên 22 sản phụ."

### [CHIẾU GÌ]
S9 (sơ đồ 5 bước) → S10 (mạng, ô số). Nếu còn thời gian: mở demo tab *Tín hiệu (5 tầng)* với bản **r01** và chỉ tay theo đúng 5 tầng, mỗi tầng ứng một bước. Ảnh dự phòng: `01`–`03`.

### [VÌ SAO LÀM VẬY]
- **Pha-không:** bộ lọc nhân quả có độ trễ nhóm phụ thuộc tần số. Với tín hiệu thai vốn có phổ rộng, độ trễ đó dịch đỉnh đi vài mili-giây mà không đều. Chạy hai chiều thì pha triệt tiêu, đổi lại là không chạy được thời gian thực đúng nghĩa — đây là hạn chế phải ghi.
- **Dải 10–60 Hz:** chọn từ khảo sát dải. Nhưng con số ưu thế của dải này **đã được đo lại trên đúng mô hình hiện hành** và chỉ còn +2,44 điểm ở kênh chọn theo phổ, khoảng tin cậy chạm 0, và gần bằng 0 khi lấy trung bình bốn kênh. Nói đúng: dải lọc không quan trọng với bộ dò này.
- **Khử mẹ từng nhịp:** đây là chỗ sinh ra chế độ hỏng nguy hiểm nhất của cả hệ. Khi tàn dư mẹ còn lại, mô hình bám vào tàn dư và trả về một chuỗi nhịp rất đều, trông y như nhịp thai. Bản a02 trong demo là ví dụ đúng cho chuyện này.
- **Đầu ra từng mẫu:** cho phép đo jitter thật, và cho phép ghép nhịp một-một theo quy ước chấm mà không cần hậu xử lý nặng.
- **Cổng KHÔNG độc lập với mạng** [SỰ KIỆN]: 2/12 chỉ số là xác suất mạng (`peak_prob_mean`, `prob_max`), 4/12 tính trên nhịp mạng dò (`n_det`, `rr_cv`, `rr_plaus`, `bsqi`). Độ quan trọng hoán vị: `rr_cv` 0,140, `peak_prob_mean` 0,032, 10 chỉ số còn lại < 0,002 (`analysis/gate22_results.json` → `cong.permutation_importance_delta_auroc`). [SUY LUẬN] Cổng có thể sai cùng chiều với mạng khi mạng sai một cách tự tin. Câu cũ "cố ý không dùng đặc trưng của mạng" là sai và đã rút.

### [NẾU CÓ HỎI]
**H: "Lọc pha-không nghĩa là phải có toàn bộ tín hiệu. Vậy thiết bị đeo thời gian thực làm sao?"**
> "Đúng ạ, đây là hạn chế thật. Hiện em xử lý theo khối, không phải theo dòng. Muốn chạy thời gian thực thì phải chấp nhận một độ trễ khối, khoảng vài giây. Với theo dõi tại nhà thì độ trễ vài giây chấp nhận được. Nhưng em chưa đo lại hiệu năng ở chế độ khối trượt, nên em không hứa."

**H: "Sao không để mạng tự học luôn khâu khử tim mẹ?"**
> "Em chưa thử, và em ghi lại. Lý do em làm tay là để quy trách nhiệm được. Khi hỏng, em muốn biết hỏng ở khâu nào. Nếu gộp hết vào mạng thì mỗi lần kết quả xấu em không tách được nguyên nhân. Nhưng đó là lựa chọn thiết kế, không phải kết quả đo."

*Nguồn: `model/fqrs_model.py`; `pilot_evidence/band_tcn_stats.json`; `analysis/CHANDOAN_MOHINH.md` mục jitter; `analysis/gate22_results.json`.*

---

# PHẦN 5 — CÁCH CHỌN MÔ HÌNH: đo bảy họ rồi kết luận kiến trúc là đòn bẩy yếu (≈3 phút)

### [NÓI GÌ]

> "Em không chọn mạng theo cảm tính. Ở giai đoạn thăm dò em có thử tám họ kiến trúc. Nhưng giao thức lúc đó không cân bằng tham số. Nên kết luận cũ em đã rút.
>
> Em làm lại. Lần này bảy họ, cùng số tham số trong khoảng cộng trừ 2,7 phần trăm. Cùng hạt giống, cùng cách chia fold, cùng số epoch. Giao thức rút gọn ba epoch, ba fold, một hạt giống, cho chạy trong một buổi.
>
> Kết quả. Mạng em đang dùng được 97,64. Hai họ sát ngay sau là 97,63 và 97,62. Hai họ đó theo kiểm định tương đương là **tương đương thật**, không phải hoà tình cờ. Rồi 96,93, rồi 96,84, rồi 96,38. Họ kém nhất được 94,53, kém mạng của em 3,10 điểm.
>
> Chỗ đáng nói là **vì sao** họ kém nhất lại kém. Em đo trường tiếp nhận của từng họ. Họ kém nhất chỉ nhìn được 60 mili-giây tín hiệu quanh mỗi điểm. Mạng của em nhìn 1.516 mili-giây. Em nới trường tiếp nhận của họ đó cho khớp, giữ nguyên số tham số. Nó lên 96,84.
>
> Nên khoảng cách đó không đo cái gọi là 'họ kiến trúc nào tốt hơn'. Nó đo **bề rộng ngữ cảnh**. Và bề rộng đó bão hoà ở khoảng 1,5 giây; rộng hơn nữa không thêm được gì.
>
> Em thử thêm một hướng nữa. Nhân bốn lần số tham số. Chỉ được cộng 0,26 điểm, mà là đo trong mẫu.
>
> Kết luận của em: kiến trúc là **đòn bẩy yếu nhất** trong bài toán này. Em nghĩ đây là một kết quả có giá trị, dù nó là kết quả âm. Nó nói cho người sau biết đừng tốn thời gian ở đó."

### [CHIẾU GÌ]
S11 — bảng 7 họ, bốn cột: *họ* · *số tham số* · *trường tiếp nhận đo bằng gradient* · *F1*. Cột trường tiếp nhận là cột kể chuyện, tô đậm dòng 60 ms.

### [VÌ SAO LÀM VẬY]
- **Vì sao phải cân bằng tham số trước:** nếu không cân bằng thì mọi khác biệt đều có thể quy về dung lượng mô hình, và so sánh mất nghĩa. Đây chính là lỗi của giao thức cũ.
- **Vì sao đo trường tiếp nhận bằng gradient chứ không tính công thức:** công thức cho trường lý thuyết; gradient cho trường thực sự có ảnh hưởng. Với mạng có kết nối tắt thì hai số lệch nhau.
- **Vì sao giao thức rút gọn ba epoch ba fold là chấp nhận được:** vì mục tiêu là **xếp hạng** các họ, không phải lấy số cuối cùng. Số sản xuất vẫn chạy giao thức đầy đủ.
- **Vì sao không đổi sang mạng lớn hơn:** đã đo, nhân bốn tham số chỉ được 0,26 điểm trong mẫu. Và mục tiêu xa là chạy trên thiết bị nhỏ.

### [NẾU CÓ HỎI]
**H: "Ba epoch thì mô hình chưa hội tụ. Xếp hạng như vậy có đáng tin không?"**
> "Em đồng ý là chưa hội tụ. Em chỉ dám dùng nó để xếp hạng, và em ghi rõ điều đó. Có một điểm làm em yên tâm hơn: họ đứng đầu ở giao thức rút gọn cũng chính là họ đang chạy ở giao thức đầy đủ, và số đầy đủ là 97,56. Nếu cô thấy cần, em chạy lại đầy đủ cho ba họ đầu, mất khoảng một ngày máy."

**H: "Vì sao không thử Transformer?"**
> "Em chưa thử, em ghi lại. Nhưng em có một lý do để hoãn. Em đo được là bề rộng ngữ cảnh bão hoà ở 1,5 giây. Transformer mạnh ở ngữ cảnh dài. Bài toán của em không đòi ngữ cảnh dài, nên em đoán lợi ích nhỏ. Đó là phỏng đoán, không phải kết quả. Em từng đoán sai một lần rồi nên em nói rõ nó là phỏng đoán."

*Nguồn: `analysis/kientruc_results.json`; `pilot_evidence/arch22.json`; `analysis/KIENTRUC.md` bảng cân bằng tham số.*

---

# PHẦN 6 — DỮ LIỆU HIỆN TẠI: bốn bộ, và nói thẳng điểm yếu (≈3 phút)

### [NÓI GÌ]

> "Em dùng bốn bộ công khai. Em nói cả cái tốt và cái yếu.
>
> Bộ thứ nhất, năm sản phụ, mỗi bản năm phút, bốn kênh bụng. Nhãn lấy từ một điện cực gắn trực tiếp lên da đầu thai. Đây là nhãn tốt nhất em có.
>
> Bộ thứ hai, dữ liệu Silesia, mười bảy bản. Trong đó mười hai bản chuyển dạ cũng có nhãn trực tiếp từ da đầu. Còn mười bản thai kỳ thì nhãn là gián tiếp.
>
> Cộng lại em có 22 chủ thể để huấn luyện.
>
> Bộ thứ ba là bộ kiểm ngoài, 75 bản một phút. Em loại mười lăm bản trùng, còn 60 bản sạch. Trong 60 bản đó lại có bảy bản em xác định là chú thích sai. Em báo cáo cả hai cách, có và không có bảy bản đó.
>
> Giờ là điểm yếu, và em muốn nói thẳng. Nhóm mười bản nhãn gián tiếp chiếm **77 phần trăm** tổng thời lượng huấn luyện của em. Em còn đo được là nhãn của nhóm đó lệch ở mốc thời gian. Một cách đo cho lệch 3,25 mili-giây. Hai cách kia cho 6,50. Nghĩa là em **không được** dùng nhóm đó để nói bất cứ điều gì về sai số thời điểm hay về chỉ số biến thiên. Em ghi câu cấm này vào tài liệu.
>
> Điểm yếu thứ hai. Em có 22 chủ thể. Em tự tính công suất thống kê thì cần khoảng 50.
>
> Điểm yếu thứ ba, và cái này em mới thấy gần đây. Sáu mươi bản sạch **không phải** 60 sản phụ. Một phần trong đó đến từ một bộ mà toàn bộ bản ghi là của cùng một người. Số sản phụ thật trong 60 bản em **không biết**, chỉ biết chắc là nhỏ hơn 60. Nên phép bootstrap theo bản ghi của em chỉ là gần đúng.
>
> Còn hai bộ nữa em đã tải về nhưng không dùng được. Một bộ không có chú thích nhịp thai. Một bộ chỉ có tham chiếu Doppler. Em kiểm tận nơi chứ không tin mô tả."

### [CHIẾU GÌ]
S12 — bảng 4 bộ: *tên* · *số bản* · *loại nhãn* · *dùng vào việc gì* · *điểm yếu*. Cột cuối tô màu. Dưới bảng là một dòng đỏ: "77 % thời lượng huấn luyện có nhãn gián tiếp".

### [VÌ SAO LÀM VẬY]
- **Vì sao vẫn giữ nhóm nhãn gián tiếp:** bỏ đi thì còn 12 chủ thể, quá ít để huấn luyện. Giải pháp là giữ để huấn luyện nhưng **cấm** dùng cho các kết luận về thời điểm.
- **Vì sao báo cáo cả 60 và 53 bản:** bảy bản chú thích sai là phán đoán của nhóm, không phải sự thật đã được bên thứ ba xác nhận. Báo cáo cả hai cách để người đọc tự chọn.
- **Vì sao tự kiểm hai bộ kia thay vì tin mô tả:** một bộ có tệp chú thích, nhưng khi đo khoảng nhịp thì ra 86 nhịp mỗi phút — đó là nhịp mẹ, không phải nhịp thai. Nếu tin mô tả thì đã huấn luyện trên nhãn sai.
- **Hệ quả cho bài báo:** phải ghi rằng đơn vị thống kê ngoài miền là *bản ghi*, không phải *chủ thể*, và ghi lý do.

### [NẾU CÓ HỎI]
**H: "Nếu 77 phần trăm dữ liệu huấn luyện có nhãn kém, sao kết quả lại cao như vậy?"**
> "Em nghĩ có hai lý do, và cả hai em chưa chứng minh. Một là nhãn gián tiếp vẫn đúng về vị trí nhịp, chỉ lệch hệ thống ở mốc thời gian. Mạng học chỗ có nhịp thì vẫn học được. Hai là em đánh giá ở dung sai 50 mili-giây, mà lệch chỉ vài mili-giây. Nhưng nếu em đo biến thiên thì vài mili-giây lại thành vấn đề lớn. Nên em cấm mình dùng nhóm đó cho chỉ số biến thiên."

**H: "Em có định tự chú thích thêm dữ liệu không?"**
> "Có, và đây là việc em xin cô giúp. Có bộ công khai chưa có nhãn nhịp thai. Em có thể tự chú thích mười đến hai mươi bản, nhưng phải có chuyên gia kiểm lại, nếu không thì nhãn của em cũng chỉ là đầu ra thuật toán. Em không có bác sĩ sản nào quen."

*Nguồn: `analysis/DULIEU.md`; `analysis/xacnhan_results.json` mục `viec2_bo_thu_ba`; `survey/RO_RI_VANLIEU.md` mục 137 (thành phần 60 bản); `analysis/ABLATION_B1.md`.*

---

# PHẦN 7 — ĐỐI CHUẨN: vì sao phải chạy lại chứ không trích số (≈4 phút, kèm demo)

### [NÓI GÌ]

> "Phần này em nghĩ là phần kỹ thuật quan trọng nhất.
>
> Trong tài liệu điện tim thai, mỗi bài dùng một cách chấm khác nhau. Khác dung sai. Khác đơn vị. Khác cách chia tập. Nếu em lấy con số in trong bài của người ta đặt cạnh con số của em, em sẽ so hai thứ khác loại. Nên em đặt ra một luật cho mình: chỉ so trực tiếp với phương pháp em **tự chạy lại được**.
>
> Phương pháp mạnh nhất em chạy lại được gọi là Power-MF. Em không có bản quyền phần mềm thương mại nên em chạy qua một phần mềm mã nguồn mở tương thích. Rồi em kiểm chứng ngoài: trên một nhóm bản ghi có số tác giả công bố, em chạy ra 99,40, tác giả công bố 99,46. Lệch 0,06. Từ đó em coi bản chạy lại là dùng được.
>
> Bây giờ là chỗ em thấy tâm đắc nhất về thiết kế thí nghiệm. Câu hỏi của em là 'một kênh mất bao nhiêu'. Nếu em so mạng một kênh của em với Power-MF bốn kênh thì em so lẫn hai thứ: số kênh và thuật toán. Nên em tự cắt Power-MF xuống còn một kênh.
>
> Bản một kênh đó là đối chứng công bằng nhất em có. Cùng dữ liệu. Cùng khâu lọc. Cùng khâu khử tim mẹ. Cùng bộ chấm. Chỉ khác đúng thuật toán lõi.
>
> Ba con số. Power-MF bốn kênh: 98,83. Power-MF một kênh: 86,71. Mạng của em một kênh: 97,56.
>
> Đọc đúng ba con số đó. So với bốn kênh em vẫn **thua** 1,27 điểm, khoảng tin cậy từ âm 3,08 đến dương 0,27, p bằng 0,156. Em thắng 18 trên 22 bản, trung vị dương 0,23, nhưng bốn bản thua lệch lớn kéo trung bình xuống. So với một kênh em hơn 10,85 điểm, khoảng tin cậy 6,80 đến 15,40, thắng cả 22 bản.
>
> Bốn kênh đáng giá 12,12 điểm cho Power-MF. Mạng một kênh của em lấy lại 10,85 trong số đó. Đó là 89,49 phần trăm.
>
> Chỗ còn thiếu, em nói luôn: em chưa chạy lại đối thủ thứ hai. Có một bài gần giao thức của em báo cáo 77,8 trên bộ kiểm ngoài. Nhưng họ tính trên cả 75 bản, không phải 60 bản sạch. Nên em không đặt hai con số cạnh nhau được.
>
> Giờ em cho cô xem nó chạy."

### [CHIẾU GÌ]
S13 → S14 → **S15 (DEMO, 4 phút)**.

Trình tự demo (máy đã mở sẵn, bản r01 đã phân tích xong, ô *Kênh bụng* = *Tự động — peakprob*):

| Phút | Thao tác | Nói gì (ngắn) |
|---|---|---|
| 0:00–1:00 | Tab *Tín hiệu (5 tầng)*, bản **r01**. Chỉ tay 5 tầng. | "Tầng trên là tín hiệu thô. Ở kênh 4 của bản này gai của bé to ngang gai của mẹ. Tầng ba là sau khi trừ mẹ, phần còn lại là nơi tìm tim bé. Bản này F1 99,92. Đèn xanh." |
| 1:00–2:15 | Đổi sang **a09**, *Phân tích*. Mở tab *Chọn kênh — cả 4 kênh*. Đổi quy tắc sang *PSD*, rồi đổi lại. | "Bộ khác, không trùng dữ liệu huấn luyện. Quy tắc mới chọn kênh 1, được 94,25. Quy tắc cũ chọn kênh 2, chỉ được 19,35. Trên 60 bản thì quy tắc mới thắng 19, hoà 35, thua 6. Không bản nào mất quá 3,90 điểm." |
| 2:15–3:15 | Chọn **a02**, *Phân tích*. Chỉ *Đèn tin cậy* và tab *Nhịp tim thai + đèn đoạn*. | "Đây là phần em coi là quan trọng nhất. Mô hình bám nhầm vào tàn dư tim mẹ. Nó trả một chuỗi nhịp rất đều, trông y như thai. F1 chỉ 24,91. Nhưng đèn đỏ, theo hai đường: 6 trên 15 đoạn bị đỏ, và luật bám nhịp mẹ bật vì 78 phần trăm nhịp trùng nhịp mẹ. Nên hệ thống từ chối trả lời." |
| 3:15–4:00 | Tab *Kết quả tổng hợp (60 bản sạch)* rồi *Nhật ký (JSON)*. | "Bảng này đọc thẳng từ tệp kết quả, không có số nào ghi cứng trong mã. Dòng cảnh báo hậu kiểm nằm ngay trong bảng. Đây là bản mẫu nghiên cứu, không phải thiết bị y tế." |

Dự phòng nếu demo hỏng: ảnh `01`–`03` (r01) → `04`–`06` (a09 hai quy tắc) → `09`–`10` (a02) → `12` (bảng tổng hợp).

### [VÌ SAO LÀM VẬY]
- **Vì sao chạy lại thay vì trích:** ba nguồn sai lệch cộng dồn — khác dung sai chấm, khác đơn vị phân tích, khác cách chia tập. Chạy lại trên đúng dữ liệu của mình thì ba nguồn đó biến mất.
- **Vì sao phải kiểm chứng ngoài bản chạy lại:** nếu bản chạy lại yếu hơn bản gốc thì mọi so sánh có lợi cho mình một cách giả tạo. Số 99,40 so với 99,46 là bằng chứng bản chạy lại không bị làm yếu.
- **Vì sao tự cắt bản một kênh:** để cô lập đúng một biến. Đây là thiết kế then chốt của toàn bộ phép đo 89,49 phần trăm.
- **Vì sao chọn demo bản a02 chứ không chỉ bản đẹp:** vì phần đóng góp chính là cổng từ chối, mà cổng chỉ chứng minh được trên bản hỏng.

### [NẾU CÓ HỎI]
**H: "Em tự cắt phương pháp của người ta xuống một kênh. Như vậy có làm hỏng phương pháp của họ không?"**
> "Câu hỏi này đúng chỗ, em có nghĩ tới. Em cắt ở mức đầu vào, không sửa lõi thuật toán. Tức là em cho nó một kênh và giữ nguyên mọi bước còn lại. Nếu cô thấy có cách cắt công bằng hơn, em làm lại. Em cũng ghi rõ trong bài là con số một kênh của họ là do em cắt, không phải số tác giả công bố."

**H: "Vì sao không so với các bài học sâu mới hơn?"**
> "Vì em chưa chạy lại được bài nào trong số đó trên dữ liệu của em. Phần lớn không công bố mã, hoặc công bố thiếu khâu tiền xử lý. Em có ghi số của họ trong phần tổng quan, nhưng em ghi kèm đơn vị đo của họ và ghi rõ là không so trực tiếp được."

*Nguồn: `baselines/powermf_fair_stats.json`; `baselines/powermf_1ch.json`; `baselines/powermf_published.json`; `analysis/recovery_ratio.json`; `survey/RO_RI_VANLIEU.md` (Orvas 2025 tính trên 75 bản).*

---

# PHẦN 8 — SAI LẦM 1: mẫu mười bản ghi đánh lừa cả nhóm (≈2,5 phút)

### [NÓI GÌ]

> "Giờ em kể bốn lần em sai. Em kể thật, vì nó là phần em học được nhiều nhất.
>
> Lần một. Hồi đầu em thử nghiệm trên một mẫu mười bản ghi của bộ kiểm ngoài, cho nhanh. Trên mẫu đó, một cấu hình cho 90,34, cấu hình kia cho 69,31. Chênh hơn hai mươi điểm. Em tin ngay, vì chênh lệch quá lớn.
>
> Rồi em chạy trên toàn bộ. Cấu hình 90,34 xuống còn 69,33. Cấu hình 69,31 lên thành 79,40. Cả bốn con số này về sau đều đã rút, em chỉ kể để thấy chiều đảo.
>
> Nghĩa là nó không chỉ sai một chút. Nó **đảo chiều**, và đảo cả hai đầu.
>
> Bài học của em có hai vế. Vế một: mẫu mười bản là quá nhỏ để xếp hạng bất cứ thứ gì. Vế hai, và đây mới là vế quan trọng: em đã **chọn** cấu hình sau khi nhìn kết quả trên chính mẫu đó. Đó là chọn siêu tham số trên tập đánh giá.
>
> Từ đó em đặt một luật. Không bao giờ báo cáo một siêu tham số được chọn sau khi nhìn tập đánh giá, mà không gắn nhãn là chọn hậu kiểm.
>
> Luật đó về sau bắt được một lỗi khác của chính em, ở phần quy tắc chọn kênh."

### [CHIẾU GÌ]
S17 — hai cột: *trên mẫu 10 bản* và *trên toàn bộ*, mũi tên đảo chiều vẽ đậm. Không cần slide thứ hai.

### [VÌ SAO LÀM VẬY]
- **Vì sao mẫu nhỏ đảo chiều được:** phương sai giữa các bản ghi của bộ này rất lớn — có bản gần 100 điểm, có bản dưới 10. Với mười bản thì một hai bản cực trị đủ lật thứ hạng.
- **Vì sao vẫn kể dù mọi số đó đã rút:** kể được bài học mà không đọc số như sự thật. Trên slide các số này phải có gạch ngang hoặc nhãn "đã rút".
- **Luật rút ra, đang áp dụng:** mọi con số dùng để **chọn** phải tách khỏi con số dùng để **báo cáo**.

### [NẾU CÓ HỎI]
**H: "Vậy sao em không tách ra tập validation riêng ngay từ đầu?"**
> "Đáng lẽ phải làm. Lý do em không làm là vì em coi bộ đó là tập kiểm ngoài, nên em nghĩ nhìn một mẫu nhỏ thì vô hại. Đó là suy nghĩ sai. Hiện giờ ngưỡng quyết định của em được quét trên một chủ thể validation riêng rồi áp cố định sang tập kiểm, không bao giờ quét trên tập kiểm."

*Nguồn: `survey/facts_phase4.json` mục `Z_DA_RUT.cinc_mau_10` và `Z_DA_RUT.cinc_75_o_nhiem`.*

---

# PHẦN 9 — SAI LẦM 2: đoán nguyên nhân trước khi đo (≈2 phút)

### [NÓI GÌ]

> "Lần hai. Em chạy lại phương pháp đối chuẩn trên máy mình. Lúc đầu nó cho kết quả thấp hơn số tác giả công bố vài điểm.
>
> Em đoán ngay. Em nghĩ là do một tham số trong thuật toán, cái ngưỡng khoảng cách tối thiểu giữa hai nhịp, đặt ở 340 mili-giây. Em lý luận rằng nhịp thai nhanh nên có nhịp rơi dưới ngưỡng đó và bị loại. Nghe rất hợp lý.
>
> May là em đo trước khi sửa. Em đếm thật, trong tất cả các khoảng nhịp tham chiếu, có bao nhiêu khoảng dưới 340 mili-giây. Kết quả là **không phần trăm**. Không có một khoảng nào. Giả thuyết của em sai hoàn toàn.
>
> Nguyên nhân thật nằm ở chỗ khác. Hàm tìm đỉnh của phần mềm em dùng có mức tiêu thụ bộ nhớ tăng theo bình phương số điểm. Với chuỗi dài thì nó tràn, và cái tràn đó làm hỏng kết quả ở khâu chuyển đổi.
>
> Sửa xong thì ra 99,40 so với 99,46 của tác giả.
>
> Bài học: đừng phát biểu nguyên nhân trước khi có số. Cái giá của việc đoán đúng thì nhỏ, cái giá của việc đoán sai mà tin là rất lớn. Nếu hôm đó em sửa theo giả thuyết thì em đã viết vào bài một lý do sai, và số vẫn không lên."

### [CHIẾU GÌ]
S18 — ba ô theo thứ tự: *giả thuyết của em* → *phép đo* (0,00 %) → *nguyên nhân thật*. Ô giữa tô đậm.

### [VÌ SAO LÀM VẬY]
- **Vì sao phép đếm đó rẻ mà hiệu quả:** nó là một phép kiểm trực tiếp giả thuyết, chạy trong vài giây, và cho câu trả lời nhị phân.
- **Quy trình rút ra, đang áp dụng:** trước khi sửa bất kỳ lỗi nào, viết một câu giả thuyết và một phép đo rẻ để bác nó. Nếu không nghĩ ra phép đo rẻ nào thì chưa được sửa.
- **Vì sao chuyện này quan trọng cho bài báo:** phần Thảo luận của bài báo toàn là câu giải thích nguyên nhân. Đây là bằng chứng cho thấy nhóm biết phân biệt giải thích đã đo và giải thích chưa đo.

### [NẾU CÓ HỎI]
**H: "Nếu phần mềm mã nguồn mở có lỗi như vậy, kết quả chạy lại của em có đáng tin không?"**
> "Câu hỏi đúng. Đó chính là lý do em làm bước kiểm chứng ngoài. Em chạy trên nhóm bản ghi mà tác giả có công bố số, và em ra 99,40 so với 99,46 của họ. Nếu bản chạy lại của em còn lỗi hệ thống thì con số đó đã không khớp. Em cũng ghi rõ trong bài là chạy qua phần mềm nào."

*Nguồn: `survey/facts_phase4.json` mục `Z_DA_RUT.powermf_cong_chuyen_hong`; `baselines/powermf_published.json`.*

---

# PHẦN 10 — SAI LẦM 3: tưởng mình tìm ra chồng lấn dữ liệu (≈2,5 phút)

### [NÓI GÌ]

> "Lần ba. Đây là lần em suýt viết một câu sai vào bài báo.
>
> Ở vòng làm việc thứ sáu em đi đo chồng lấn giữa bộ huấn luyện và bộ kiểm ngoài. Em dùng tương quan chéo chuẩn hoá từng cặp bản ghi, và so cả chuỗi khoảng nhịp tham chiếu.
>
> Mười lăm bản cho tương quan đúng bằng 1,0000, trên cả bốn kênh, đúng thứ tự kênh. Lệch khoảng nhịp là 0,0 mili-giây. Mỗi bản gốc năm phút xuất hiện đúng ba lần, theo ba cửa sổ một phút. Em có đối chứng dương là các bản đã biết cùng sản phụ, chúng chỉ cho 0,86 đến 0,98. Sáu mươi bản còn lại cao nhất 0,62.
>
> Lúc đó em đã định viết 'chúng tôi phát hiện rò rỉ dữ liệu'.
>
> May là ở vòng bảy em cho rà lại y văn gốc trước khi viết. Và hoá ra **ban tổ chức đã ghi chuyện này từ 2013**. Bảng 1 của bài kỷ yếu năm đó ghi rõ 25 bản đến từ bộ kia. Bài tổng kết trên tạp chí năm 2014 còn cảnh báo nguyên văn. Bài đó nêu đích danh một nhóm dự thi bị thiên lệch vì lý do này.
>
> Tệ hơn nữa. Câu cảnh báo đó **đã nằm trong ghi chú đọc bài của chính em**, hai dòng khác nhau.
>
> Nên phát biểu đúng phải là thế này. Như ban tổ chức đã ghi nhận, bộ kiểm chứa bản ghi của bộ huấn luyện. Nhóm em xác định bằng đo lường đúng mười lăm bản nào, và mức thổi phồng bao nhiêu. Mức đó là 3,27 đến 7,18 điểm tuỳ quy tắc.
>
> Bài học: tìm trong y văn gốc trước khi gọi cái gì là phát hiện. Em cũng đi rà xem còn ai bị. Trong 20 bài em rà, có bốn bài chắc chắn bị, hai bài nghi ngờ chưa xác định được. Em sẽ nêu chuyện này trong bài, dè dặt, và trích dẫn nguồn 2013 với 2014."

### [CHIẾU GÌ]
S19 — bảng ánh xạ r01→a04, a05, a22; r04→a13, a20, a25; r07→a19, a23, a24; r08→a08, a15, a17; r10→a03, a12, a14. Cột bên phải là cửa sổ 0–60, 120–180, 240–300 giây. Dưới bảng in **nguyên văn** câu cảnh báo 2014, cỡ chữ nhỏ.

### [VÌ SAO LÀM VẬY]
- **Vì sao tương quan chuẩn hoá là bằng chứng đủ mạnh:** giá trị đúng 1,0000 trên cả bốn kênh đúng thứ tự chỉ xảy ra với bản sao nguyên văn. Có đối chứng dương (0,86–0,98 cho cùng sản phụ khác buổi) và đối chứng âm (tối đa 0,62 cho phần còn lại).
- **Vì sao đo hai đường độc lập:** hai cách cài đặt khác nhau cho cùng danh sách mười lăm bản. Nếu chỉ có một đường thì không loại được lỗi cài đặt.
- **Vì sao cách phát biểu quan trọng đến thế:** nếu viết "chúng tôi phát hiện" thì người phản biện chỉ cần một câu trích 2013 là bài mất uy tín toàn phần. Còn nếu viết đúng thì phần đo lường vẫn là đóng góp thật.
- **Điều cần nói ra khi bị hỏi dồn:** cái mới của nhóm là **định danh** và **định lượng**, không phải sự kiện.

### [NẾU CÓ HỎI]
**H: "Nếu chuyện này ai cũng biết từ 2013, thì phần này còn đáng đăng không?"**
> "Em nghĩ là có, nhưng phải khiêm tốn. Cái đã biết là bộ kiểm có chứa bản của bộ kia. Cái chưa nguồn nào ghi là bản nào, cửa sổ nào, và mất bao nhiêu điểm khi loại ra. Em đo được ba thứ đó. Và em thấy nó có ích thật, vì đã có bài đăng gần đây vẫn dùng cả bảy mươi lăm bản."

**H: "Sau khi loại mười lăm bản thì kết quả của em xấu đi. Em có tiếc không?"**
> "Số chính rớt khoảng năm điểm, nên có tiếc. Nhưng có một chuyện làm em thấy đỡ. Cải tiến chọn kênh đo trên dữ liệu sạch lại **mạnh hơn** đo trên dữ liệu cũ. Nghĩa là kết luận định tính không dựa vào phần nhiễm. Em thấy yên tâm hơn với số thấp mà sạch."

*Nguồn: `survey/RO_RI_VANLIEU.md`; `survey/ro_ri_vanlieu.json`; `benchmark_dpss/eval_cinc60_sach.json` mục `meta.leak_records`; `analysis/dulieu_m4b_verify.json`.*

---

# PHẦN 11 — SAI LẦM 4 VÀ 5: hai ảo giác thống kê (≈3 phút)

### [NÓI GÌ]

> "Còn hai lần nữa, và hai lần này tinh vi hơn.
>
> **Lần bốn, trần đo lường tạo ra ảo giác.** Em từng kết luận rằng cải tiến của em tập trung ở nhóm bản ghi khó. Nghe rất hợp lý: bản dễ đã gần 100 điểm rồi thì cải thiện được bao nhiêu.
>
> Nhưng đó chính là vấn đề. F1 bị chặn trên ở 100. Bản dễ **không thể** cải thiện nhiều, không phải vì phương pháp mà vì cái trần. Nên nhìn thấy 'hiệu ứng ở nhóm khó' là hệ quả của thang đo, không phải của phương pháp.
>
> Em làm lại trên thang logit, là thang không có trần. Làm lại xong thì hiệu ứng tan. Em rút kết luận đó.
>
> **Lần năm, và lần này em tiếc nhất.** Em từng kết luận rằng khoảng cách giữa trong miền và ngoài miền là do dữ liệu, không phải do mô hình. Em có ba phép thử ủng hộ, nghe rất chắc.
>
> Nhưng một trong ba phép thử dựa trên một định nghĩa: 'chỗ này có nhìn thấy tín hiệu thai không'. Em đi đo độ đặc hiệu của chính phép thử đó. Nó có tỉ lệ âm tính giả **18 phần trăm**, khoảng tin cậy 12 đến 25. Trên những bản khó thì lên tới 55 đến 70 phần trăm.
>
> Nghĩa là phép thử nói 'không có tín hiệu' trong khi thực ra có, cứ năm lần thì gần một lần. Vậy em không được dùng nó để quy trách nhiệm cho dữ liệu. Em rút kết luận đó và mọi con số phái sinh.
>
> Phát biểu đúng bây giờ là: khoảng cách trong miền và ngoài miền là 23,28 điểm theo quy tắc chọn kênh cũ, đó là sự thật đo được. Bốn phương pháp thích nghi miền em thử đều thất bại, đó cũng là sự thật đo được. Còn **nguyên nhân thì em chưa xác định được**. Em để ngỏ.
>
> Em nói thêm một chi tiết làm em tin là còn thứ gì đó em chưa hiểu. Em đo được ba loại dịch chuyển giữa hai miền, rồi em áp cả ba lên dữ liệu trong miền. Kết quả chỉ mất 0,01 điểm. Trong khi khoảng cách thật là hơn hai mươi ba điểm. Nên ba thứ em đo được không giải thích nổi khoảng cách."

### [CHIẾU GÌ]
S20 — hai khối. Khối trái: đường cong hiệu ứng theo F1 gốc và theo logit, đặt cạnh nhau. Khối phải: một ô lớn ghi "âm tính giả 18,0 % [12,1; 25,0]" và dưới đó là dòng "→ rút kết luận về nguyên nhân". Không đọc các số đã rút thành tiếng.

### [VÌ SAO LÀM VẬY]
- **Vì sao logit là thang đúng:** F1 bị chặn hai đầu, nên hiệu số F1 không có cùng ý nghĩa ở giữa thang và ở gần trần. Logit giãn hai đầu ra, nên so được.
- **Vì sao phải đo độ đặc hiệu của chính phép thử:** khi một kết luận dựa vào một phép phân loại phụ, sai số của phép phân loại đó vào thẳng kết luận. Đây là bước đã cứu nhóm.
- **Vì sao dừng thích nghi miền:** bốn phương pháp đều thất bại, hai trong bốn còn làm xấu đi rõ rệt. Không có lý do cơ chế nào để tin phương pháp thứ năm sẽ khác.
- **Chỗ để ngỏ đúng cách:** ghi vào bài là "chưa xác định nguyên nhân", kèm bằng chứng ba dịch chuyển đo được chỉ giải thích 0,01 điểm.

### [NẾU CÓ HỎI]
**H: "Em rút nhiều kết luận như vậy, thì còn lại gì để đăng?"**
> "Còn những thứ em đo trực tiếp chứ không suy ra. Ba con số F1 trên 22 chủ thể. Tỉ lệ lấy lại 89,49 phần trăm. Bảng bảy quy tắc chọn kênh trên 60 bản sạch. Bản kiểm toán mười lăm bản trùng. Kết quả cổng từ chối bỏ-một-chủ-thể. Cái em rút toàn là câu **giải thích nguyên nhân**, không phải số đo."

**H: "Làm sao em biết mình không còn ảo giác thống kê nào nữa?"**
> "Em không biết chắc, và em nói thẳng. Cái em làm được là mỗi vòng có một lượt phản biện độc lập với nhiệm vụ tìm chỗ sai, chứ không phải xác nhận. Năm kết luận em rút thì em tự rút trước khi có ai chỉ ra. Nhưng em không dám nói là hết. Nếu cô thấy chỗ nào nghi thì em đi đo lại chỗ đó."

*Nguồn: `analysis/xacnhan_results.json` mục `viec4_phep_thu_nhin_thay`; `analysis/XACNHAN.md`; `adapt/adapt_results.json` (chỉ phần 0,01 điểm); khoảng cách 23,28 = 97,56 (`baselines/powermf_fair_stats.json` → `so_sanh.tat_ca_22.rely_vs_pmf4.mean_a`) − 74,28 (`analysis/dulieu_results.json` → `chon_kenh_60_sach.bang.psd.mean_60_sach`); số cũ 17,92 đã rút (`survey/facts_phase4.json` → `Z_DA_RUT.khoang_cach_trong_ngoai_mien_17_92`); `analysis/CHANDOAN_MOHINH.md` (khối rút lại ở đầu tệp).*

---

# PHẦN 12 — TRIỂN KHAI LẠI THẾ NÀO: quy trình tám vòng (≈4 phút)

### [NÓI GÌ]

> "Cô có thể hỏi: sao em tự tìm ra được năm lỗi của chính mình. Em kể cách làm.
>
> Em chia công việc thành tám vòng. Mỗi vòng em làm hai việc tách rời. Việc thứ nhất là chạy thí nghiệm và viết kết quả. Việc thứ hai là một lượt phản biện, với nhiệm vụ ghi rõ là **tìm chỗ sai**, không phải xác nhận. Lượt phản biện không được sửa tệp nào, chỉ được nêu lỗi.
>
> Kết quả là năm tuyên bố bị rút, và cả năm em rút trước khi có người ngoài chỉ ra.
>
> Bốn cách làm cụ thể, em nghĩ là dùng lại được cho đề tài khác.
>
> **Một, khai báo trước rồi neo vào lịch sử mã.** Trước khi chạy một thí nghiệm quyết định, em viết ra luật đọc kết quả, rồi ghi lại mốc mã nguồn. Em nói thẳng một chỗ chưa đạt. Tệp khai báo cho quy tắc chọn kênh **chưa được neo**. Nó còn được viết sau khi em đã thấy điểm từng kênh. Nên em không được dùng chữ nào mạnh hơn 'khai báo trước phép tính'. Lần sau em neo trước.
>
> **Hai, luôn có mức ngẫu nhiên đối chứng.** Với mọi phép chia nhóm, em tính thêm: nếu gán nhãn ngẫu nhiên thì con số sẽ là bao nhiêu. Không có mức đó thì tỉ lệ phần trăm không đọc được.
>
> **Ba, thống kê ở mức chủ thể, không ở mức bản ghi.** Em dùng bootstrap theo cụm chủ thể. Năm kết luận cũ của em bị đảo khi làm đúng ở mức này.
>
> **Bốn, kiểm rò rỉ bằng cách xáo nhãn.** Quy tắc chọn kênh của em phải mù nhãn. Để chứng minh, em xáo trộn nhãn rồi cho quy tắc chạy lại. Trong 776 lựa chọn, **không có lựa chọn nào đổi**. Nếu quy tắc lén dùng nhãn thì con số đó đã khác không.
>
> Em cũng dùng công cụ tự động để đối chiếu từng con số trong văn bản với tệp gốc trên đĩa. Vòng cuối đối chiếu 25 con số, khớp cả 25. Nhưng em tự chịu trách nhiệm về từng con số, không đổ cho công cụ."

### [CHIẾU GÌ]
S21 — cột trái là tám vòng theo thời gian, mỗi vòng một dòng một câu. Cột phải là năm tuyên bố đã rút, nối mũi tên sang vòng phát hiện ra chúng. Dưới cùng là bốn cách làm.

### [VÌ SAO LÀM VẬY]
- **Vì sao phản biện phải tách khỏi người làm:** người viết kết quả có động cơ giữ kết quả. Lượt phản biện có nhiệm vụ ngược lại, và không có quyền sửa tệp, nên không tự dọn dấu vết.
- **Vì sao neo mốc mã nguồn:** một tệp khai báo không neo thì không chứng minh được viết lúc nào. Đây đúng là chỗ nhóm còn thiếu, và phải nói ra chứ không lấp.
- **Vì sao bootstrap theo cụm:** các bản ghi của cùng một sản phụ không độc lập. Bootstrap theo bản ghi cho khoảng tin cậy hẹp giả tạo.
- **Vì sao vẫn phải nói phần dùng công cụ tự động:** nếu giấu mà bị hỏi thì mất tin cậy. Nói ra kèm câu "em chịu trách nhiệm từng số" thì lành.
- **Hạn chế còn lại, phải thừa nhận:** ngay cả bootstrap theo cụm ở ngoài miền cũng chỉ là gần đúng, vì số sản phụ thật trong 60 bản không biết.

### [NẾU CÓ HỎI]
**H: "Em dùng công cụ trí tuệ nhân tạo trong quá trình làm. Vậy phần nào là của em?"**
> "Em dùng công cụ để chạy đối chiếu số và để có một lượt đọc phản biện. Phần thiết kế thí nghiệm, phần quyết định rút tuyên bố nào, và phần chịu trách nhiệm về số là của em. Em mở được tệp gốc cho từng con số trong bài. Nếu cô muốn kiểm bất kỳ số nào, em mở tệp ngay tại đây."

**H: "Tám vòng trong mấy ngày? Nghe không giống tiến độ nghiên cứu bình thường."**
> "Em làm tập trung trong một đợt ngắn, và em nói thẳng là các vòng không đều nhau. Có vòng chỉ là rà soát lại, không chạy thí nghiệm mới. Em nghĩ cái đáng nói không phải là số vòng, mà là mỗi vòng đều có một lượt đọc với nhiệm vụ tìm lỗi. Nếu cô thấy nên giãn ra và làm kỹ hơn từng vòng, em nghe cô."

*Nguồn: `docs/nhat_ky/THAMDINH_VONG6.md`, `docs/nhat_ky/THAMDINH_VONG7.md`, `docs/nhat_ky/THAMDINH_VONG8.md`; `analysis/xacnhan_khaibao.md`; `analysis/STATS.md`; `analysis/CHONKENH.md` (phép xáo nhãn 0/776).*

---

# PHẦN 13 — HIỆN TẠI ĐẠT ĐƯỢC GÌ (≈5 phút)

### [NÓI GÌ]

> "Cuối cùng em tổng kết chỗ đứng thật.
>
> **Trong miền, 22 sản phụ.** Phương pháp bốn kênh 98,83. Phương pháp đó cắt còn một kênh 86,71. Mạng một kênh của em 97,56. Em thua bốn kênh 1,27 điểm, chưa có ý nghĩa thống kê, thắng 18 trên 22 bản. Em hơn một kênh 10,85 điểm, thắng cả 22 bản. Tỉ lệ lấy lại 89,49 phần trăm.
>
> **Ngoài miền, 60 bản sạch, người chấm độc lập.** Quy tắc cũ 74,28. Quy tắc ghi trước 80,72. Quy tắc trong cùng họ 81,01. Quy tắc tốt nhất theo điểm thô 82,01. Trần lý thuyết nếu chọn kênh hoàn hảo là 83,60. Cải tiến lấy lại 82,9 phần trăm dư địa tới trần đó. Số bản dưới 50 điểm giảm từ 16 xuống 9, và không bản nào mất quá 3,90 điểm.
>
> **Cổng từ chối,** đánh giá bỏ-một-chủ-thể trên 22 sản phụ. Diện tích dưới đường cong trong bản ghi 0,934, khoảng tin cậy 0,872 đến 0,981, tính trên mười một trong hai mươi hai sản phụ có đoạn xấu. Nó xếp đúng ba bản khó nhất vào ba hạng chót; ngẫu nhiên là một phần một nghìn năm trăm bốn mươi. Nhưng em nói rõ ba điều. Năm trong hai mươi bốn quy tắc một đặc trưng đơn giản cũng làm được vậy, nên em không nói phải học mới làm được. Cổng dựa một phần vào đầu ra của mạng, nên không độc lập với mạng. Và cổng này mới ở dạng phân tích, chưa đưa vào demo.
>
> **Hệ thống chạy được.** Mã khoảng ba mươi mốt nghìn dòng Python, một trăm linh chín kiểm thử tự động. Demo web, mặc định là chế độ trình bày năm bước; tám tab cũ nằm trong chế độ chuyên gia. Mô hình 0,48 mê-ga-bai, 4,35 mili-giây mỗi cửa sổ bốn giây trên chíp thường.
>
> **Còn thiếu gì.** Một, chỉ có hai hạt giống; hạt giống thứ hai cho 97,59. Hai, số cổng từ chối ngoài miền chưa tính lại trên 60 bản sạch. Ba, chưa chạy lại đối thủ thứ hai. Bốn, chỉ 22 chủ thể trong khi cần khoảng 50. Năm, quy tắc chọn kênh vẫn là chọn hậu kiểm và chưa có bộ thứ ba để xác nhận.
>
> **Định vị thật.** Đích gần là tạp chí chuyên ngành đo lường sinh lý, nơi cộng đồng điện tim thai công bố. Tạp chí đó xếp hạng Q2 theo bảng 2024. Em ước cửa khoảng năm mươi lăm phần trăm. Đích thứ hai là hội nghị điện tim, kỳ 2027, hạn khoảng tháng tư. Nhóm tạp chí Q1 thì em ước mười lăm đến hai mươi phần trăm trong sáu tháng. Trong mười hai tháng khoảng ba mươi lăm phần trăm, và chỉ khi có dữ liệu có nhãn mới. Các con số này là em ước, không phải số đo. Rào cản là dữ liệu có nhãn mới, không phải phương pháp. Còn nhóm hội nghị hạng A sao thì dưới năm phần trăm. Thực ra **không có hội nghị hạng đó đúng lĩnh vực này**. Nên em bỏ nó khỏi bảng mục tiêu.
>
> Về Euréka, hạn nội bộ của trường em chưa xác minh được nên em sẽ hỏi Đoàn trường trong tuần. Em nghĩ thực tế là kỳ sau.
>
> Ba tháng tới em làm ba việc rẻ. Chạy đủ ba hạt giống. Tính lại số cổng trên 60 bản sạch. Viết hai bản thảo trên 60 bản sạch. Hai việc em quyết định **dừng**, vì đã đo thấy đòn bẩy yếu: đổi kiến trúc và thích nghi miền không giám sát.
>
> Thứ em cần nhất ở cô là dữ liệu có nhãn và một đầu mối bác sĩ sản. Đó là nút thắt duy nhất em không tự gỡ được."

### [CHIẾU GÌ]
S22 — ba bảng trên một slide, hoặc ba slide liền:
1. **Bảng kết quả** (trong miền / ngoài miền / cổng từ chối), mỗi dòng có cột *ranh giới*.
2. **Bảng tiến độ**: xong / đang làm / còn thiếu — năm dòng "còn thiếu" ở trên.
3. **Bảng định vị nơi công bố**: tên nhóm venue · ước cửa · rào cản thật. Dòng hội nghị hạng A sao gạch ngang, ghi "bỏ khỏi mục tiêu".

Kết thúc: tờ tóm tắt in giấy, hai bản.

### [VÌ SAO LÀM VẬY]
- **Vì sao bảng "còn thiếu" đứng trước bảng "đã xong" khi trả lời hỏi đáp:** vì phần đó là phần người nghe sẽ hỏi. Chủ động nêu thì đỡ phải phòng thủ.
- **Vì sao bỏ hội nghị hạng A sao khỏi bảng mục tiêu:** không phải vì khó, mà vì **không có hội nghị hạng đó đúng lĩnh vực**. Để nó trong bảng là tự đặt một mục tiêu không tồn tại.
- **Vì sao nêu số cổng từ chối ngoài miền là "chưa tính lại":** số cũ đo trên tập có mười lăm bản nhiễm. Đọc số cũ là đọc một số đã rút.
- **Vì sao vẫn xin dữ liệu chứ không xin duyệt kết quả:** đây là nút thắt duy nhất không tự gỡ được bằng thêm thời gian máy.

### [NẾU CÓ HỎI]
**H: "Nếu không xin được dữ liệu mới thì đề tài dừng ở đâu?"**
> "Vẫn nộp được một bài ở tạp chí chuyên ngành. Nội dung sẽ là hai phép đo chắc và một giả thuyết ghi rõ. Cái không làm được nếu thiếu dữ liệu là xác nhận quy tắc chọn kênh, và cửa Q1. Em nghĩ đó là kết cục chấp nhận được cho năm nay, nhưng em muốn thử xin trước."

**H: "Em có nghĩ kết quả này đủ mạnh để làm khoá luận hay đề tài cấp trường không?"**
> "Em nghĩ đủ về khối lượng và về tính chặt. Chỗ em không chắc là hội đồng có quen với kiểu trình bày nêu cả phần rút lại không. Đó là một trong ba việc em muốn xin ý kiến cô."

*Nguồn: `analysis/dulieu_results.json`; `benchmark_dpss/eval_cinc60_sach.json`; `baselines/powermf_fair_stats.json`; `analysis/recovery_ratio.json`; `analysis/gate22_results.json`; `analysis/kientruc_results.json`; `adapt/adapt_results.json`; `docs/CHIEN_LUOC_CONG_BO.md`; `survey/facts_phase4.json` mục G.*

---
---

# PHỤ LỤC A — BA BIẾN THỂ THỜI LƯỢNG

## A.1 — Bản 10 phút (chỉ phần 1, 3, 7, 13)

| Phần | Thời lượng | Cắt gì |
|---|---|---|
| 1 — Lên ý tưởng | 2 phút | Bỏ đoạn về bộ lọc và dải tần. Giữ ba câu: vì sao từng nhịp, vì sao một kênh, vì sao cổng từ chối. |
| 3 — Đóng góp | 2,5 phút | Giữ cả bốn đóng góp nhưng mỗi cái **một câu đóng góp + một câu ranh giới**, không hơn. |
| 7 — Đối chuẩn + demo | 4 phút | Demo rút còn **90 giây**: chỉ r01 (30 s) và a02 (60 s). Bỏ a09 và bỏ tab *Chọn kênh*. |
| 13 — Hiện tại đạt gì | 1,5 phút | Chỉ đọc bảng kết quả và ba việc xin hỗ trợ. Bỏ bảng định vị venue. |

**Slide dùng:** S1, S3, S5, S8, S13, S14, S15 (rút), S22.
**Bỏ hẳn:** S2, S4, S6, S7, S9–S12, S16–S21.
**Rủi ro của bản này:** không kể được lần rút lại nào, nên nghe như đề tài "chỉ có kết quả đẹp". Bù bằng một câu chèn ở cuối phần 3: *"Em đã tự rút năm kết luận trong quá trình làm; nếu cô muốn nghe em kể riêng."*

## A.2 — Bản 20 phút (thêm phần 4, 5, 6, 8)

| Phần | Thời lượng |
|---|---|
| 1 — Lên ý tưởng | 2 phút |
| 3 — Đóng góp | 2,5 phút |
| 4 — Phương pháp | 3 phút |
| 5 — Chọn mô hình | 2 phút |
| 6 — Dữ liệu và điểm yếu | 2 phút |
| 7 — Đối chuẩn + demo | 4,5 phút (demo 3 phút: r01, a09, a02) |
| 8 — Sai lầm 1 | 2 phút |
| 13 — Hiện tại đạt gì | 3 phút |

**Slide dùng:** S1, S3, S5, S8, S9, S10, S11, S12, S13, S14, S15, S17, S22.
**Bỏ:** S2, S4, S6, S7, S16, S18, S19, S20, S21.
**Cắt trong phần 5:** bỏ bảng bảy họ, chỉ nói ba con số (97,64 · 94,53 · 96,84 sau khi nới trường tiếp nhận) và một câu kết luận.
**Lưu ý:** bản 20 phút này **khác** bản trong `docs/KICH_BAN_TRINH_BAY.md`. Bản kia hướng tới buổi gặp giảng viên (có mục "em xin gì ở cô"). Bản này hướng tới người nghe muốn hiểu quá trình. Chọn một, không trộn.

## A.3 — Bản 45 phút (đầy đủ)

| Nhóm phần | Thời lượng |
|---|---|
| Phần 1–3 (ý tưởng, tài liệu, đóng góp) | 10 phút |
| Phần 4–7 (phương pháp, mô hình, dữ liệu, đối chuẩn + demo 4 phút) | 14 phút |
| Phần 8–11 (bốn nhóm sai lầm) | 10 phút |
| Phần 12–13 (quy trình, kết quả) | 9 phút |
| Đệm | 2 phút |

**Slide dùng:** tất cả S1–S22.
**Điểm nhịp bắt buộc:** nếu tới phút 24 mà chưa xong phần 7 thì bỏ phần 9 (sai lầm 2) và rút phần 12 còn hai câu. Không bao giờ cắt phần 13.

---

# PHỤ LỤC B — MƯỜI CÂU HỎI KHÓ NHẤT CỦA BUỔI DÀI

> Mười câu này **khác** mười hai câu trong `docs/KICH_BAN_TRINH_BAY.md`. Chúng là những câu chỉ nảy ra khi người nghe đã theo hết hành trình. Trả lời 2–4 câu, không hơn.

**B1. "Khoảng tin cậy của tỉ lệ lấy lại chạm 103 phần trăm. Vậy con số 89,5 có nghĩa gì?"**
> "Nó nghĩa là ước lượng điểm là 89,5, còn dữ liệu của em chưa loại trừ được khả năng lấy lại toàn bộ. Em kiểm lại bằng jackknife thì nằm trong 88,6 đến 93,4, hẹp hơn. Em báo cáo cả hai. Muốn khoảng hẹp hơn nữa thì phải tăng số chủ thể, không có cách nào khác."

**B2. "Luật ghi trước chỉ vào một quy tắc, quy tắc đó trượt. Rồi em lại nêu một quy tắc khác cũng trong họ đó và nó sống. Có phải em chọn cái nào sống thì lấy không?"**
> "Câu này đúng chỗ đau nhất của em. Em trả lời thế này. Em báo cáo **cả ba** con số theo đúng thứ tự. Luật ghi trước chỉ vào quy tắc cho 80,72, trượt với p 0,051. Một quy tắc cùng họ cho 81,01, sống với p 0,015, nhưng không phải quy tắc kế hoạch chọn. Còn quy tắc tốt nhất theo điểm thô là chọn hậu kiểm. Em không bỏ con số trượt đi. Nếu chỉ được giữ một kết luận, em giữ cái trượt, vì nó là luật em ghi trước. Nhưng em cho rằng người đọc có quyền thấy cả ba."

**B3. "Sáu mươi bản sạch có bao nhiêu sản phụ?"**
> "Em không biết, và em ghi rõ là không biết. Em chỉ biết chắc là nhỏ hơn 60. Một phần các bản đó đến từ một bộ mà toàn bộ bản ghi là của cùng một người. Hệ quả là bootstrap theo bản ghi của em chỉ là gần đúng, và khoảng tin cậy ngoài miền có thể hẹp hơn thực tế. Em ghi câu này vào phần hạn chế."

**B4. "Trường tiếp nhận 1,5 giây nghĩa là mạng nhìn được nhiều nhịp cùng lúc. Vậy nó có đang đoán nhịp theo chu kỳ thay vì thật sự thấy nhịp không?"**
> "Câu này em có đi đo. Nếu mạng đoán theo chu kỳ thì nó sẽ bỏ sót những nhịp có tín hiệu rõ mà lệch chu kỳ. Em đếm loại lỗi đó. Trong miền là 3,8 phần trăm, trong khi mức ngẫu nhiên là 14,7. Ngoài miền là 1,0 so với 10,3, nhưng cặp ngoài miền này em đo trước khi loại 15 bản trùng. Nên bằng chứng không ủng hộ giả thuyết đoán theo chu kỳ. Nhưng em chưa làm thí nghiệm cắt chu kỳ chủ động, đó là việc nên làm."

**B5. "Cổng từ chối từ chối bao nhiêu phần trăm dữ liệu? Nếu từ chối nhiều thì con số nào cũng đẹp."**
> "Đúng, và đó là lý do em không bao giờ báo cáo F1 sau khi cổng lọc như số chính. Số 97,56 trong miền, 74,28 ngoài miền, và cả 82,01 của quy tắc hậu kiểm đều là số **không** có cổng, tính trên toàn bộ. Cổng em đánh giá riêng bằng diện tích dưới đường cong và bằng thứ hạng, không bằng cách cải thiện F1. Số độ phủ ngoài miền em chưa tính lại trên 60 bản sạch nên em không đọc ra."

**B6. "Sao không dùng dữ liệu tổng hợp để tăng số chủ thể?"**
> "Em chưa thử, em ghi lại. Em có một e ngại. Nếu tổng hợp bằng mô hình sinh tín hiệu thì mạng học đúng mô hình sinh đó. Nó không học sinh lý thật. Và bộ kiểm ngoài của em vốn có sẵn một phần bản mô phỏng. Nhưng đó là e ngại, không phải kết quả đo. Nếu cô thấy đáng thử, em thử và báo cáo cả khi nó hỏng."

**B7. "Em bảo nhóm nhãn gián tiếp chiếm 77 phần trăm thời lượng huấn luyện mà nhãn lại kém. Sao không bỏ hẳn nhóm đó?"**
> "Bỏ thì còn 12 chủ thể, quá ít. Em chọn cách khác. Giữ để huấn luyện, nhưng cấm dùng nhóm đó cho kết luận về sai số thời điểm. Cấm cả cho chỉ số biến thiên. Em có chạy thí nghiệm bỏ nhóm đó ra để xem ảnh hưởng, và em báo cáo kèm. Nếu sau này có thêm chủ thể nhãn trực tiếp thì em sẽ bỏ."

**B8. "Khoảng cách trong miền và ngoài miền hơn hai mươi ba điểm mà em không giải thích được. Vậy hệ thống có dùng được không?"**
> "Nói thẳng thì hiện chỉ dùng được trong điều kiện giống dữ liệu huấn luyện. Nhưng có một điều làm em nghĩ hệ vẫn có thể có ích. Cổng từ chối không cần biết nguyên nhân; nó chỉ cần nhận ra đoạn nào không đáng tin. Nếu cổng làm đúng việc đó thì hệ an toàn hơn khi ra ngoài miền. Nhưng em chưa chứng minh được: cổng dựa một phần vào chính mạng, và trên năm bản ngoài miền sạch, ghép với mô hình năm ca, diện tích dưới đường cong trong bản ghi chỉ 0,721, khoảng tin cậy 0,517 đến 0,898. Đó là lý do việc tính lại số cổng trên 60 bản sạch là ưu tiên số một của em."

**B9. "Em dùng công cụ trí tuệ nhân tạo. Phần nào là của em, và em chứng minh thế nào?"**
> "Em dùng công cụ để chạy đối chiếu số và để có một lượt đọc phản biện độc lập. Phần thiết kế thí nghiệm và phần quyết định rút tuyên bố nào là của em. Cách chứng minh là: mỗi con số trong bài đều mở được tệp gốc tại chỗ, và lịch sử mã ghi từng vòng. Cô chọn bất kỳ con số nào, em mở tệp ngay."

**B10. "Em trình bày ba đóng góp mà cái nào cũng kèm chữ 'chưa xác nhận'. Trước hội đồng, em bảo vệ kiểu gì?"**
> "Em sẽ đổi thứ tự kể. Em đưa hai thứ chắc lên trước: phép đo tỉ lệ lấy lại, và bản kiểm toán bộ dữ liệu. Hai thứ đó không phụ thuộc lựa chọn hậu kiểm nào. Rồi em nêu quy tắc chọn kênh là giả thuyết có kèm kế hoạch xác nhận. Em nghĩ một hội đồng sẽ tin một đề tài biết rõ ranh giới của mình hơn là một đề tài toàn số đẹp."

---

# PHỤ LỤC C — BA ĐIỀU TUYỆT ĐỐI KHÔNG NÓI

### C1. Không nói "em phát hiện ra rò rỉ dữ liệu"

**Thay bằng:** *"Như ban tổ chức đã ghi nhận trong bài kỷ yếu 2013 và bài tổng kết 2014, bộ kiểm chứa bản ghi của bộ huấn luyện. Nhóm em xác định bằng đo lường đúng mười lăm bản nào và mức thổi phồng bao nhiêu."*

**Vì sao:** sự kiện này đã được ghi trong hai nguồn chính thức, và bài 2014 còn cảnh báo nguyên văn. Tệ hơn, câu cảnh báo đó đã nằm trong ghi chú đọc bài của chính nhóm ở hai dòng khác nhau. Nếu nói "em phát hiện", chỉ cần một người nghe biết nguồn 2013 là toàn bộ phần đó mất uy tín — và kéo theo cả những phần đúng. Cái mới của nhóm là **định danh** và **định lượng**, và hai cái đó vẫn đủ để đăng.

### C2. Không nói "mô hình không phải nút thắt", cũng không nói "phần còn lại là do thiếu tín hiệu thật"

**Thay bằng:** *"Khoảng cách trong miền và ngoài miền là 23,28 điểm theo quy tắc chọn kênh cũ, đó là số đo. Bốn phương pháp thích nghi miền em thử đều thất bại, đó cũng là số đo. Nguyên nhân thì em chưa xác định được."*

**Vì sao:** kết luận cũ dựa trên một phép thử phụ dùng để định nghĩa "chỗ này không có tín hiệu". Khi đo độ đặc hiệu của chính phép thử đó thì tỉ lệ âm tính giả là 18,0 phần trăm, khoảng tin cậy 12,1 đến 25,0, và lên 55 đến 70 phần trăm trên những bản khó. Phép thử sai gần một phần năm số lần thì không dùng để quy trách nhiệm được. Mọi con số phái sinh của kết luận đó đã bị rút và **không được đọc thành tiếng**.

### C3. Không dùng bất kỳ chữ nào hàm ý nghiên cứu đã được đăng ký trước

**Thay bằng:** *"Em khai báo trước phép tính trong một tệp trên máy, rồi mới chạy."* — và nếu bị hỏi tiếp thì nói thẳng: *"Tệp khai báo cho quy tắc chọn kênh chưa được neo vào lịch sử mã, và em viết nó sau khi đã thấy điểm từng kênh. Nên nó không phải bằng chứng mạnh. Chỉ có tệp khai báo ở vòng bảy là được neo."*

**Vì sao:** đăng ký trước là một quy trình có bên thứ ba và có dấu thời gian không sửa được. Nhóm không làm điều đó. Dùng chữ mạnh hơn thực tế ở một buổi trình bày là chuyện nhỏ; lặp lại nó trong bài báo là chuyện lớn. Giữ một cách nói duy nhất ở cả hai nơi thì không bao giờ trượt.

### Ba câu ngắn cũng nằm trong danh sách cấm

| Câu cấm | Thay bằng |
|---|---|
| "Một kênh tốt hơn đa kênh" | "Một kênh lấy lại 89,5 phần trăm lợi ích của bốn kênh; trung bình vẫn thua 1,27 điểm." |
| "Tạp chí đó là Q1" (về tạp chí đo lường sinh lý) | "Tạp chí đó xếp Q2 theo bảng 2024, nhưng là nơi cộng đồng điện tim thai công bố." |
| Bất kỳ chữ nào kiểu "tốt nhất hiện nay", "chưa ai làm", "lần đầu" | "Đây là phép đo của em trên dữ liệu của em, so với phương pháp em chạy lại được." |

---

## Kiểm 15 phút trước buổi trình bày

1. Mở sổ tay HTML, rà lại: **không mục nào còn số tính trên 75 bản**, và không mục nào còn số cổng từ chối ngoài miền chưa tính lại.
2. `python -m pytest demo/test_core.py -q` (68 kiểm thử) và `python -m pytest tests/ -q` (43) — tổng 111 tại 17/09/2026.
3. `python demo/run_check.py --only r01,a09,a02 --out demo_check_3ban --threads 2` — xác nhận ba con số 99,92 · 94,25 · 24,91 khớp kịch bản.
4. Mở sẵn `survey/facts_phase4.json` trong trình soạn thảo, để tra khi bị hỏi số không nhớ.
5. In hai bản `docs/TOM_TAT_1_TRANG.md`.
6. **Không mang** bản nháp hội nghị bốn trang cũ trong `paper/` — toàn số 75 bản.
