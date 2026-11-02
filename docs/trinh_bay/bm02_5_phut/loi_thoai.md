# Lời thoại thuyết trình — RelyFetal, BM02, 13 slide

Đọc liền mạch từ trên xuống. Chữ **in đậm** là chỗ nhấn giọng. Phần *in nghiêng trong ngoặc* là ghi chú cho bạn, không đọc lên.



---

## Slide 1 — Tên đề tài

Dạ, em kính chào thầy cô trong hội đồng. Em xin trình bày đề tài **RelyFetal**: phát hiện từng nhịp tim thai từ **một kênh** điện tim ổ bụng, có cơ chế **tự đánh giá độ tin cậy**, hướng tới chạy trên thiết bị nhúng.

Toàn bộ ý tưởng của đề tài gói trong một câu: **một kênh đo, thêm độ tin cậy**.

---

## Slide 2 — Vì sao chọn đề tài

Theo dõi tim thai là việc làm thường quy những tháng cuối thai kỳ. Nhưng cách đo phổ biến nhất hiện nay là monitor sản khoa dùng Doppler lại chỉ cho **nhịp trung bình**, không cho biết chính xác từng nhịp rơi vào lúc nào.

Những phương pháp chính xác nhất thì cần **bốn kênh trở lên** để tách tín hiệu thai ra khỏi tín hiệu mẹ. Bốn kênh nghĩa là nhiều dây, và rất khó thu gọn thành một miếng dán để sản phụ tự đeo.

Nhìn vào hình giữa slide, thầy cô sẽ thấy vấn đề: trong một kênh ghi, sóng điện tim của **mẹ** rất lớn, sóng của **thai** nhỏ hơn nhiều lần và bị che lấp, còn nhiễu cơ, nhiễu cử động và nhiễu điện lưới thì phủ lên tất cả.

Và còn một chuyện ít ai nói tới. Khi tín hiệu kém, mô hình **vẫn trả ra một con số nhịp tim** — con số đó có thể sai mà người dùng không biết.

Từ đó nhóm em đặt ra mục tiêu: một kênh đo vẫn phải đạt độ chính xác của bốn kênh, và quan trọng hơn — **hệ thống phải biết khi nào nên từ chối trả lời**. Bốn tiêu chí đo lường cụ thể em xin trình bày ở phần cuối.

Em xin nhấn mạnh ngay từ đầu: nhóm **không thu thập dữ liệu** và **không thử nghiệm trên sản phụ**. Toàn bộ thí nghiệm dùng dữ liệu công khai đã ẩn danh.

---

## Slide 3 — Dữ liệu và cách chia không rò rỉ

Đây là nguồn dữ liệu của toàn bộ đề tài.

**Trong miền** có **22 sản phụ độc lập**, ghép từ **ADFECGDB** trên PhysioNet, công bố năm 2012, và bộ **Silesia** công bố năm 2020, sau khi đã loại các bản ghi trùng giữa hai nguồn. Đây là tập duy nhất dùng để **huấn luyện** mô hình.

**Ngoài miền** là **60 bản** của CinC Challenge 2013 set-a, sau khi loại 15 bản trùng. Tập này **chỉ để kiểm tra**, hoàn toàn không dùng để tinh chỉnh.

Và bộ nhiễu **MIT-BIH Noise Stress Test** để thử độ bền. Tất cả các bộ đều được hạ về **250 Hz**.

Bên dưới là cách chia dữ liệu. Nhóm chia **theo sản phụ** thành **11 lượt**, mỗi lượt giữ riêng **2 sản phụ** để kiểm tra, 20 người còn lại để huấn luyện. Một sản phụ **không bao giờ** xuất hiện đồng thời ở cả hai tập trong cùng một lượt.

Nói cách khác: mô hình dùng để chấm một sản phụ **chưa từng thấy người đó** khi học. Nhờ vậy điểm số phản ánh đúng khả năng trên người mới, chứ không phải khả năng học thuộc.

---

## Slide 4 — Từ tín hiệu đến từng nhịp thai

Chuỗi xử lý gồm **năm khâu**, đi từ trái sang phải.

Đầu tiên là **lọc** Butterworth 10–60 Hz dạng pha không, cộng lọc chặn 50 Hz.

Tiếp theo là **khử điện tim mẹ**: dò đỉnh R của mẹ, dựng mẫu sóng trung vị rồi trừ khỏi tín hiệu, có hiệu chỉnh biên độ từng nhịp bằng phương pháp bình phương tối thiểu.

Sau đó là **chọn kênh** bằng bảy quy tắc dựa trên phổ công suất, độ đều của khoảng RR và độ tự tin của mô hình — **không nhìn nhãn**.

Khâu chính là **mạng tích chập thời gian**: năm khối dư với hệ số giãn 1, 2, 4, 8, 16, trường tiếp nhận khoảng 1,5 giây, **113 nghìn tham số**.

Và cuối cùng là **cổng tin cậy**.

Hàng giữa là phần **cách huấn luyện**, em xin nói rõ vì hội đồng hay hỏi. Đầu vào là đoạn **4 giây, một kênh**. Nhãn được làm mềm thành **hàm Gauss với độ lệch chuẩn 12 mili giây** quanh mỗi nhịp thai, thay vì nhãn cứng. Hàm mất mát là **entropy chéo nhị phân có trọng số cho lớp thiểu số**, kết hợp tăng cường dữ liệu. Thuật toán tối ưu là **AdamW**, và mỗi cấu hình được huấn luyện với **ba hạt giống** ngẫu nhiên để báo cáo mức dao động. Khi lấy nhịp, hệ thống lấy các đỉnh của đường xác suất, với **khoảng cách tối thiểu 250 mili giây** giữa hai nhịp.

Hai hình dưới là **kết quả thật**: bên trái là đường xác suất, bên phải là các nhịp phát hiện được đối chiếu với nhãn tham chiếu.

---

## Slide 5 — Kết quả bước đầu tháng 9/2026

Đây là phần nhóm em **đã chạy thật**, không phải đề xuất.

Trong tháng 9, mô hình chỉ dùng **một kênh** đạt F1 trung bình **97,56%** trên **22 sản phụ**, kiểm tra không trùng người với tập huấn luyện, dung sai **±50 mili giây**.

Mô hình chỉ **113 nghìn tham số**, tệp trọng số **0,48 megabyte** — đây là lý do nhóm em tin có thể đưa xuống một con chip rẻ.

Việc so sánh với phương pháp bốn kênh em xin để sang slide sau, vì đó là câu hỏi riêng.

---

## Slide 6 — So với phương pháp 4 kênh tốt nhất

Đây là slide nhóm em muốn thầy cô xem kỹ nhất, vì nó trả lời thẳng câu hỏi: **bỏ ba kênh thì mất bao nhiêu?**

Chuẩn so sánh là **Power-MF** — phương pháp bốn kênh có mã nguồn công khai, nhóm em chạy lại được và chấm bằng **cùng một bộ chấm ±50 ms** trên **cùng 22 sản phụ**.

Kết quả: Power-MF bốn kênh đạt **98,83%**. RelyFetal một kênh đạt **97,56%**. Chênh **1,27 điểm** nghiêng về phía bốn kênh — nhóm em ghi rõ là còn kém, không nói mạnh hơn thế. Muốn nói tương đương thì phải có cỡ mẫu lớn hơn.

Điều đáng chú ý nằm ở thanh thứ ba: **chính phương pháp Power-MF khi chỉ còn một kênh** chỉ đạt **86,71%**. Vậy giá trị của hướng tiếp cận này không phải đánh bại bốn kênh, mà là **giữ được gần như toàn bộ độ chính xác khi số kênh bị cắt từ bốn xuống một** — điều mà cách làm truyền thống không làm được.

Hai điều phải nói để không ai hiểu quá: một là Varanini 2014 công bố **97,04%** trên tập CinC — cao hơn nhóm em — nhưng bằng bộ chấm riêng, nhóm **chưa chạy lại được** nên không đưa vào bảng. Hai là tập CinC có **15 bản trùng** với dữ liệu huấn luyện; nếu để nguyên thì điểm sẽ **cao giả 3,27 đến 7,18 điểm**. Nhóm loại bỏ và báo cáo trên **60 bản sạch**. Việc trùng lặp này **ban tổ chức CinC đã ghi nhận** từ trước — nhóm chỉ định lượng mức ảnh hưởng, không nhận là người phát hiện đầu tiên.

---

## Slide 7 — Cổng độ tin cậy

Đây là phần trả lời câu hỏi thứ hai, và theo nhóm em là phần **khác biệt nhất** so với các công trình đơn kênh đã công bố.

Với mỗi đoạn 4 giây, hệ thống tính **12 chỉ số**: 6 chỉ số từ chính tín hiệu, như entropy mẫu, độ nhọn, entropy phổ, tỉ lệ năng lượng theo dải tần; và 6 chỉ số từ đầu ra mô hình, như số nhịp phát hiện được, độ biến thiên khoảng RR, mức hợp lý sinh lý của RR.

Bộ phân loại tăng cường gradient học từ 12 chỉ số đó, kiểm tra chéo bỏ ra từng sản phụ. Khi cổng đánh giá một đoạn là **không đáng tin**, hệ thống **không hiển thị nhịp tim** mà báo **"tín hiệu kém"** và nhắc người dùng kiểm tra lại điện cực.

Hình bên trái là ca khó a02: đường dự đoán lệch khỏi nhãn, và những **đoạn đỏ** chính là những đoạn đã bị cổng từ chối.

Em cũng xin nói rõ: đèn xanh của cổng **chưa bảo đảm** kết quả đúng — đó là phần cần nghiệm thu trong năm học.

---

## Slide 8 — Phần nhúng ESP32-S3

Câu hỏi thứ ba là chạy trên phần cứng. Có **ba việc** sẽ làm.

Một là **lượng tử hóa INT8** sau huấn luyện, so sánh F1 trước và sau trên cùng tập kiểm tra. Nếu giảm quá 1 điểm thì chuyển sang huấn luyện có xét lượng tử hóa.

Hai là **viết lại phần lọc và khử điện tim mẹ bằng C**, chạy bằng TensorFlow Lite Micro hoặc ESP-DL.

Ba là **phát lại tín hiệu** từ cơ sở dữ liệu vào bo mạch, đo thời gian xử lý, RAM và dòng tiêu thụ bằng cảm biến INA219, rồi hiển thị lên màn hình OLED.

Ngưỡng cam kết là: mô hình **dưới 200 kilobyte** — ước tính thực tế khoảng **dưới 150 kilobyte** — F1 giảm **không quá 1 điểm**, xử lý đoạn 4 giây trong **dưới 4 giây**.

Sơ đồ trên slide là **kế hoạch thử nghiệm**, **chưa phải thiết bị đã đo**.

---

## Slide 9 — Sản phẩm bàn giao

Đây là **màn hình theo dõi thật** của nhóm, chạy trên bản ghi r01.

Đường màu đỏ là sóng điện tim thai chạy theo thời gian thực, mỗi đỉnh được đánh dấu. Ở góc trái, hệ thống hiển thị **129 nhịp mỗi phút**, đèn báo **xanh**, F1 so với đáp án **99,92%**, thời gian xử lý **291 mili giây**. Con số 99,92% này là của **một ca cụ thể**, không phải trung bình 22 sản phụ.

Ở hình nhỏ bên dưới là ca chuyển dạ khó B2_03: đèn chuyển **đỏ**, hệ thống ghi rõ **"từ chối, không dùng số này"** — đúng nguyên tắc an toàn mà nhóm đặt ra.

Về bàn giao, nhóm **đã có** mã nguồn, mô hình, web demo, API, bộ kiểm thử và màn hình theo dõi. Trong năm học sẽ hoàn thiện **mô hình INT8 dưới 200 kilobyte kèm cổng đã nghiệm thu**, **kịch bản chạy lại toàn bộ bảng kết quả** để người khác tái lập được, **nguyên mẫu ESP32-S3** có màn hình OLED và bảng đo, cùng **bài báo và báo cáo nghiệm thu**.

---

## Slide 10 — Đóng góp và ý nghĩa thực tế

Lợi ích lớn nhất của đề tài **không phải** một con số cao hơn, mà là **biết được khi nào con số đó đáng tin**.

Hai đóng góp, cả hai đều **đo được**. Thứ nhất, **đo hiệu quả của cơ chế từ chối trả lời** bằng 12 chỉ số cho mỗi đoạn 4 giây — khía cạnh còn ít được quan tâm so với việc chỉ tối ưu độ chính xác. Thứ hai, về kỹ thuật, là một **hệ thống gọn**: một kênh thay vì bốn nghĩa là mạch thu đơn giản hơn, có thể thu gọn thành đai đeo, và mô hình chỉ 0,48 megabyte nên đủ nhỏ cho vi điều khiển giá rẻ.

Về ứng dụng, web demo, API và mã nguồn đã **dùng được ngay** cho học tập và giảng dạy. Về lâu dài, giúp sản phụ **bớt những lần đến viện** chỉ để đo tim thai, giảm tải khoa sản, và báo "tín hiệu kém" thay vì số sai giúp **giảm cảnh báo sai**.

Ranh giới thì em xin nói rõ: đề tài dừng ở mức **thuật toán và nguyên mẫu**; để thành sản phẩm y tế còn cần thử nghiệm lâm sàng và cấp phép; hệ thống **không dùng để chẩn đoán**.

---

## Slide 11 — Tiến độ và kinh phí

Lộ trình kéo dài **tám tháng**, từ tháng 10/2026 đến tháng 5/2027, chia thành các mốc có sản phẩm kiểm tra được.

Bốn tháng đầu là **phần kỹ thuật**: tháng 10 chuẩn bị dữ liệu, tháng 11 huấn luyện mô hình, tháng 12 xây cổng tin cậy, tháng 1 và 2 nén mô hình và chạy thử trên bo — cộng dồn đến 55%.

Ba tháng cuối là **phần hoàn thiện**: tháng 3 gom demo, báo cáo và poster, đạt 90%; tháng 4 **nghiệm thu cấp khoa**, đạt 100%; tháng 5 là báo cáo cấp Trường.

Kinh phí đề nghị nhà trường hỗ trợ là **2,95 triệu đồng**: **1,4 triệu** thuê GPU đám mây trong 100 giờ, **1 triệu** linh kiện ESP32-S3, OLED, INA219, thẻ nhớ và pin, và **0,55 triệu** in ấn poster cùng báo cáo. Đây là con số **đề xuất** trong đề cương, không phải chi phí đã phát sinh.

---

## Slide 12 — Ba câu hỏi · ba mức độ đã trả lời được

Em xin tổng kết bằng cách đặt ba câu hỏi nghiên cứu của đề cương cạnh **câu trả lời đến hôm nay**, để thầy cô thấy rõ phần nào đã xong và phần nào còn lại.

**Câu một: bỏ ba kênh thì mất bao nhiêu?** Tiêu chí là F1 trong miền từ 97% và ngoài miền từ 80%. Trong miền nhóm đạt **97,56%** — đạt. Ngoài miền đạt **74,28%** — **chưa đạt** mục tiêu.

**Câu hai: hệ thống tự biết khi nào không đáng tin?** Tiêu chí AUROC từ 0,85. Trên ADFECGDB cổng đạt **0,90** — đạt. Nhưng khi gộp cả dữ liệu ngoài miền thì chỉ **0,75** — chưa đạt. Nên câu này nhóm trả lời được một nửa.

**Câu ba: chạy được trên vi điều khiển?** Tiêu chí INT8 dưới 200 kilobyte, F1 giảm không quá 1 điểm, xử lý đoạn 4 giây trong dưới 4 giây. Hiện nhóm **chưa có** kết quả này: mới có mô hình 0,48 megabyte bản đầy đủ, việc lượng tử hóa nằm trong tháng 1 và 2 năm 2027.

Nói ngắn: **câu một xong, câu hai được một nửa, câu ba chưa làm.** Đó chính là phần còn lại của năm học.

---

## Slide 13 — Kết luận

Em xin chốt lại bằng một câu: **một kênh đo, thêm độ tin cậy**.

Bốn con số đáng nhớ: **một kênh** thay vì bốn mà vẫn lấy lại **89,5%** khoảng cách; **60 bản sạch** sau khi loại 15 bản trùng, tránh được chỗ điểm cao giả tới hơn 7 điểm; **12 chỉ số** để hệ thống nói "tín hiệu kém" thay vì đưa ra số sai; và mục tiêu **dưới 200 kilobyte** cho ESP32-S3.

Em xin cảm ơn thầy cô và các bạn đã lắng nghe, và sẵn sàng nhận câu hỏi ạ.


---

# Phụ lục — trả lời câu hỏi

**Nếu hội đồng hỏi: 97,56% đã gần 98,83%, sao không nói là tương đương?**

> Vì khoảng tin cậy của chênh lệch là [−3,08; +0,27] điểm, và chỉ có 22 sản phụ. Muốn khẳng định tương đương thì phải đặt trước một biên tương đương và có cỡ mẫu lớn hơn. Nhóm em báo cáo khoảng tin cậy để người đọc tự đánh giá.

**Nếu hội đồng hỏi: ngoài miền chỉ 74–82%, vậy có dùng được thật không?**

> Chưa ạ, và nhóm em không nói là đã dùng được. Đây chính là lý do có cơ chế từ chối trả lời: khi đổi hệ thống ghi, hệ thống phải nhận ra mình đang ở vùng kém tin cậy. Mục tiêu tháng 12 là đưa F1 ngoài miền lên từ 80% với ý nghĩa sau Holm — hiện quy tắc gate đạt 80,72% nhưng p = 0,051 nên chưa đạt.

**Nếu hội đồng hỏi: có phải nhóm phát hiện ra việc trùng lặp dữ liệu CinC không?**

> Không ạ. Ban tổ chức CinC đã ghi nhận việc set-a chứa bản ghi của ADFECGDB. Đóng góp của nhóm là định lượng cụ thể mức ảnh hưởng — 15 bản, tương quan 1,0000, làm F1 tăng ảo 3,27–7,18 điểm — và loại bỏ trước khi báo cáo kết quả ngoài miền.

**Nếu hội đồng hỏi: con số 99,92% có phải kết quả trung bình?**

> Không ạ. Đó là F1 của một bản ghi duy nhất là r01, dùng để minh họa giao diện. Kết quả trung bình trên 22 sản phụ là 97,56%.

**Nếu hội đồng hỏi: dữ liệu chỉ có 22 sản phụ, sao tin được?**

> Đúng là ít, và đều cùng một hệ thống ghi. Nhóm em xử lý bằng ba cách: chia theo sản phụ để không rò rỉ, báo cáo khoảng tin cậy bootstrap theo cụm, và kiểm tra thêm ngoài miền trên 60 bản CinC. Kết luận nào cũng đi kèm giới hạn của mẫu.

**Nếu hội đồng hỏi: huấn luyện như thế nào, có chống overfit không?**

> Nhãn làm mềm bằng hàm Gauss 12 ms, có tăng cường dữ liệu, và mỗi cấu hình chạy 3 hạt giống để báo cáo độ dao động. Quan trọng hơn là chia theo sản phụ — mô hình không bao giờ thấy người đó khi huấn luyện, nên khó học thuộc.

**Nếu hội đồng hỏi: phần nhúng đã làm được gì rồi?**

> Chưa có số đo phần cứng ạ. Hiện đã có mô hình 0,48 megabyte và toàn bộ chuỗi xử lý chạy trên máy tính; lượng tử hóa INT8 và đo trên ESP32-S3 nằm trong kế hoạch tháng 1–2/2027.

**Nếu hội đồng hỏi: kết quả có tái lập được không?**

> Có mã nguồn, có danh sách bản ghi trùng và bộ chấm điểm công khai. Bộ kiểm thử tự động đã có; kịch bản chạy lại toàn bộ bảng kết quả là một trong các sản phẩm bàn giao sẽ hoàn thiện.
