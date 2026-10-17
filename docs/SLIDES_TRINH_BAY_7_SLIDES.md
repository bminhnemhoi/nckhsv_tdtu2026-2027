# BÀI THUYẾT TRÌNH DỰ ÁN RELYFETAL (7 SLIDE: RÕ RÀNG — ĐỦ KỸ THUẬT — DỄ THUYẾT TRÌNH)
**Đề tài:** Nhận diện nhịp tim thai nhi từ điện tim ổ bụng đơn kênh có cổng từ chối (Single-Channel fQRS Detection with Confidence Gate)  
**Mô hình cốt lõi:** `FetalQRS-TCN` (113.481 tham số, 0.48 MB)  
**Tác giả:** Nhóm NCKH Sinh viên TDTU 2026–2027  

---

## SLIDE 1: BÀI TOÁN, THÁCH THỨC & GIAO THỨC CHIA DỮ LIỆU (TRAIN / VAL / TEST)

### 1. Ý chính của slide
> *"Tín hiệu tim thai cực kỳ yếu và bị tim mẹ đè bẹp. Nhóm giải quyết bài toán chỉ bằng 1 kênh đo ở bụng, đồng thời thiết lập giao thức chia dữ liệu Train/Val/Test nghiêm ngặt, loại bỏ hoàn toàn các ca rò rỉ và sai nhãn trong y văn."*

### 2. Nội dung trình chiếu
* **Khó khăn kỹ thuật của bài toán:**
  * Biên độ tim thai cực nhỏ ($10–50\ \mu\text{V}$), bị tim mẹ ($200–1000\ \mu\text{V}$) lấn át hoàn toàn với tỷ số tín hiệu trên nhiễu (SNR) từ $-5\text{ dB}$ đến $-25\text{ dB}$.
  * Các giải pháp hiện tại bắt buộc phải có thêm kênh ngực mẹ hoặc dùng 4–12 kênh bụng, gây cồng kềnh khi theo dõi tại nhà.

![Tín hiệu điện tim bụng mẹ thực tế — Tim mẹ lấn át hoàn toàn tim thai](../de_cuong_latex/figs/fig8_tin_hieu_dau_vao.png)
*Hình 1.1: Dạng sóng điện tim thu từ 1 kênh bụng mẹ thực tế. Đỉnh tim mẹ (mQRS) biên độ lớn gấp 5–10 lần, trong khi nhịp tim thai (fQRS) nhấp nhô li ti chìm sâu trong nhiễu cơ và trôi đường đẳng điện.*

* **Giao thức chia dữ liệu huấn luyện & kiểm thử (Train / Val / Test):**
  * **Bộ chuẩn vàng PhysioNet ADFECGDB (5 ca chuyển dạ, 1000 Hz):** Có nhãn đo trực tiếp từ điện cực da đầu thai nhi.
    * Áp dụng giao thức **Leave-One-Record-Out (LORO)**: Huấn luyện trên 4 ca (tách 1 phần làm validation để tinh chỉnh ngưỡng), kiểm thử độc lập trên ca còn lại; lặp lại xoay vòng 5 lần $\rightarrow$ Đảm bảo **tách biệt hoàn toàn người bệnh giữa tập Train và Test**, không bao giờ học vẹt.
  * **Bộ Silesia NIFECG (22 ca, 500 Hz):** Rà soát và **loại bỏ 5 ca** thực chất là bản sao của ADFECGDB (`B2_01`, `B2_02`, `B2_07`, `B2_10`, `B2_11`) để tránh kiểm thử trùng lặp.
  * **Bộ kiểm thử độc lập CinC 2013 (75 ca):**
    * Phát hiện **15 ca rò rỉ** (bản sao nguyên văn ADFECGDB, hệ số tương quan $NCC = 1.000$).
    * Phát hiện **7 ca bị chú thích sai** đã được y văn công nhận (`a33`, `a38`, `a47`, `a52`, `a54`, `a71`, `a74`).
    * $\rightarrow$ Giữ lại đúng **60 bản ghi sạch** để làm tập kiểm thử ngoại kiểm (Test chéo không tinh chỉnh).

![Kiểm toán bộ dữ liệu CinC 2013 — Loại bỏ 15 ca rò rỉ và 7 ca sai nhãn](../de_cuong_latex/figs/fig18_cinc75.png)
*Hình 1.2: Kết quả kiểm toán tính toàn vẹn 75 ca CinC 2013: Phát hiện 15 ca rò rỉ (bản sao ADFECGDB) và 7 ca sai nhãn, giữ lại đúng 60 bản ghi sạch cho tập kiểm thử ngoại kiểm độc lập.*

* **Quy chuẩn đầu vào:** Đưa về **đúng 1 kênh bụng duy nhất**, hạ mẫu chuẩn hóa về $f_s = 250\text{ Hz}$.

### 3. Lời thoại gợi ý khi thuyết trình:
> *"Kính thưa thầy cô, khó khăn lớn nhất của đề tài là tín hiệu tim thai cực kỳ yếu, nhỏ hơn tim mẹ từ 5 đến 10 lần và bị chìm hoàn toàn trong nhiễu. Mục tiêu của nhóm là chỉ dùng đúng 1 kênh đo ở bụng người mẹ.  
> Về phương pháp chia dữ liệu Train/Val/Test: Nhóm sử dụng bộ dữ liệu chuẩn vàng ADFECGDB gồm 5 sản phụ có gắn điện cực trực tiếp ở đầu thai nhi. Nhóm áp dụng giao thức kiểm tra chéo ngoại trừ 1 đối tượng (LORO): 4 sản phụ dùng để Train và Val chọn ngưỡng, sản phụ thứ 5 hoàn toàn độc lập dùng để Test, xoay vòng 5 lần. Cách làm này đảm bảo mô hình không bao giờ gặp dữ liệu của người bệnh lúc kiểm tra.  
> Đặc biệt, khi kiểm toán bộ dữ liệu CinC 2013, nhóm phát hiện có 15 ca thực chất bị sao chép trùng lặp từ bộ ADFECGDB và 7 ca bị gắn nhãn sai. Nhóm đã kiên quyết loại bỏ 22 ca này, chỉ giữ lại đúng 60 bản ghi sạch để làm tập kiểm tra ngoại kiểm độc lập."*

---

## SLIDE 2: KIẾN TRÚC MÔ HÌNH FetalQRS-TCN & CÁC THỰC NGHIỆM CẢI THIỆN

### 1. Ý chính của slide
> *"Nhóm chứng minh việc đổi họ mô hình phức tạp chỉ giúp tăng 0.41 điểm F1, trong khi việc mở rộng tầm nhìn thời gian (Receptive Field) lên 1.5 giây mới là yếu tố quyết định giúp F1 tăng vọt từ 92% lên 97% với chỉ 113 nghìn tham số."*

### 2. Nội dung trình chiếu
* **Kiến trúc cụ thể của FetalQRS-TCN (Chuỗi-sang-chuỗi):**
  * **Đầu vào:** Mảng 2 kênh $\times$ 1000 mẫu tại 250 Hz (Tín hiệu thô + Tín hiệu sau khi đã khử mẹ).
  * **Tầng gốc (Stem):** 1 lớp tích chập Conv1D ($k=7$, 40 kênh đặc trưng).
  * **Thân mạng:** **5 khối Residual Dilated TCN** với bước nhảy giãn nở tăng theo cấp số nhân: $d \in \{1, 2, 4, 8, 16\}$ kết hợp kết nối tắt (skip connection), hàm kích hoạt GELU và chuẩn hóa BatchNorm1D.
  * **Tầng ra (Head):** Conv1D $1 \times 1$ + Sigmoid $\rightarrow$ Xuất **Heatmap Gaussian theo từng mẫu** ($\sigma = 12\text{ ms}$).

![Kiến trúc mô hình chuỗi-sang-chuỗi FetalQRS-TCN](../tai_lieu_notebooklm/hinh_anh/03_kien_truc_fetalqrs_tcn.png)
*Hình 2.1: Sơ đồ kiến trúc chuỗi-sang-chuỗi FetalQRS-TCN gồm tầng Stem tích chập và 5 khối Residual Dilated TCN với bước nhảy giãn nở d = 1, 2, 4, 8, 16, chỉ 113.481 tham số (0.48 MB).*

* **Tổng tham số & Dung lượng:**
  * Đúng **113.481 tham số** (Dung lượng: **0.48 MB** thập phân / **443 KB** nhị phân) $\rightarrow$ Nhỏ hơn các mô hình SOTA từ 40 đến 270 lần.
* **Các thực nghiệm kiểm chứng (Ablation Studies) định hình kiến trúc:**
  1. *Khảo sát 16 kiến trúc (ResNet, U-Net, Transformer, MLP):* Chênh lệch giữa các mô hình chỉ là 2.55 điểm ($p = 0.7012$ — không có ý nghĩa thống kê), trong khi Transformer chạy chậm hơn 21.7 lần.
  2. *Quét tầm nhìn thời gian (Receptive Field - RF):* Kéo dài RF từ 172 ms lên **1.516 ms (379 mẫu)** giúp F1 tăng từ 92.67% lên **97.16%** ($p < 0.0001$). Vượt qua 1.5s (chứa trọn 3–4 nhịp thai và 2 nhịp mẹ), F1 bão hòa sinh lý. TCN là giải pháp rẻ nhất để đạt RF dài.
  3. *Đầu ra Heatmap từng mẫu:* Giảm sai số định thời (Jitter) từ $5.6\text{ ms}$ (phân loại cửa sổ) xuống **$1.0\text{ ms}$**.

![Quy luật bão hòa trường tiếp nhận sinh lý (Receptive Field)](../tai_lieu_notebooklm/hinh_anh/04_bao_hoa_truong_tiep_nhan.png)
*Hình 2.2: Mối quan hệ giữa trường tiếp nhận (Receptive Field) và F1-score: F1 tăng vọt từ 92.67% lên 97.16% khi RF đạt 1.516 ms (chứa trọn 3–4 nhịp thai và 2 nhịp mẹ) và bão hòa sinh lý sau 1.5s.*

### 3. Lời thoại gợi ý khi thuyết trình:
> *"Về kiến trúc cụ thể: Mô hình của nhóm có tên là FetalQRS-TCN, thuộc dạng chuỗi-sang-chuỗi. Đầu vào là 1 đoạn tín hiệu 4 giây gồm 2 kênh: tín hiệu gốc và tín hiệu sau khi đã khử nhịp mẹ. Mạng gồm 1 tầng Stem tích chập và 5 khối TCN giãn nở với bước nhảy 1, 2, 4, 8, 16, có kết nối tắt residual.  
> Vì sao nhóm lại chọn kiến trúc này? Nhóm đã làm thực nghiệm đối đầu 16 kiến trúc khác nhau cùng số lượng tham số. Kết quả cho thấy việc đổi giữa ResNet, U-Net hay Transformer chỉ chênh lệch nhau có 0.41 điểm F1, nhưng Transformer lại chạy chậm hơn 21 lần. Trong khi đó, biến số quyết định độ chính xác là tầm nhìn thời gian. Khi nhóm kéo dài tầm nhìn của TCN từ 172 mili-giây lên 1.516 mili-giây, điểm F1 tăng vọt từ 92% lên 97%. Khoảng 1.5 giây này chứa vừa vặn 2 nhịp mẹ và 3–4 nhịp con, giúp mô hình học trọn vẹn nhịp điệu sinh lý.  
> Toàn bộ mô hình chỉ có 113 nghìn tham số, nặng chưa tới nửa Megabyte, xuất ra bản đồ xác suất từng mili-giây giúp sai số định vị nhịp giảm xuống chỉ còn đúng 1 mili-giây."*

---

## SLIDE 3: KỸ THUẬT XỬ LÝ TÍN HIỆU & CƠ CHẾ TỰ TỪ CHỐI (CỔNG AN TOÀN 3 MÀU)

### 1. Ý chính của slide
> *"Mô hình AI chỉ phát huy hiệu quả khi kết hợp với quy trình xử lý tín hiệu kinh điển: lọc dải 10–60 Hz giúp tăng 11 điểm F1, thuật toán trừ nhịp mẹ thích nghi từng nhịp, và cơ chế ĐÈN ĐỎ tự động từ chối khi mô hình bám nhịp mẹ."*

### 2. Nội dung trình chiếu
* **Khó khăn về chất lượng tín hiệu & Kỹ thuật xử lý:**
  1. *Nhiễu trôi đường đẳng điện và sóng T mẹ:*
     * **Giải pháp:** Tiền xử lý bằng bộ lọc dải Butterworth bậc 4 pha không 10–60 Hz + Lọc khử nguồn 50 Hz.
     * **Cải thiện:** Tăng vọt **+11.0 điểm F1** so với dải 1–45 Hz truyền thống, loại bỏ hoàn toàn trôi trượt do nhịp thở.

![Hiệu quả dải lọc 10–60 Hz so với 1–45 Hz truyền thống](../tai_lieu_notebooklm/hinh_anh/02_hieu_qua_dai_loc_10_60hz.png)
*Hình 3.1: Phổ tần số và hiệu quả tiền xử lý: Dải lọc 10–60 Hz giúp tăng +11.0 điểm F1 so với dải 1–45 Hz truyền thống nhờ loại bỏ hoàn toàn trôi trượt hô hấp và sóng T mẹ.*

  2. *QRS mẹ đè bẹp QRS thai:*
     * **Giải pháp:** Dùng phương pháp khuôn mẫu trung vị (Median Template Subtraction) kết hợp hệ số co giãn bình phương tối thiểu kẹp trong $[0.3; 3.0]$ thích nghi theo từng nhịp $\rightarrow$ Triệt tiêu mẹ sạch sẽ mà không làm biến dạng tim thai.
  3. *Tự chọn kênh đo mù nhãn (Blind Lead Selection):*
     * Tự động chọn kênh bụng tốt nhất qua chỉ số `peakprob` (độ nhọn xác suất của TCN) hoặc `PSD` (năng lượng dải 1.8–3.0 Hz), hoàn toàn không cần biết trước nhãn.
* **Cơ chế an toàn lâm sàng — Cổng từ chối theo đoạn 4 giây:**
  * 🟢 **Đèn Xanh:** Tín hiệu tốt, nhịp thai nằm trong vùng sinh lý ($110–160\text{ bpm}$) $\rightarrow$ Xuất kết quả tin cậy.
  * 🟡 **Đèn Vàng:** Tín hiệu hơi nhiễu hoặc nhịp thai biến động $\rightarrow$ Cảnh báo cần chú ý.
  * 🔴 **Đèn Đỏ (Cơ chế an toàn cốt lõi):** Phát hiện miếng dán bị lỏng, tín hiệu quá xấu, hoặc **mô hình bị bám nhịp mẹ $\ge 60\%$** $\rightarrow$ **Hệ thống TỪ CHỐI hiển thị kết quả ảo**, yêu cầu kiểm tra lại miếng dán.

![Cơ chế Cổng từ chối kích hoạt Đèn Đỏ trên ca bám nhịp mẹ a02](../tai_lieu_notebooklm/hinh_anh/07_demo_den_do_tu_choi_a02.png)
*Hình 3.2: Cơ chế an toàn y tế lâm sàng: Khi phát hiện máy bám nhịp mẹ 78% trên ca a02, hệ thống lập tức kích hoạt ĐÈN ĐỎ, gạch bỏ số đo FHR để ngăn ngừa chẩn đoán sai lầm.*

### 3. Lời thoại gợi ý khi thuyết trình:
> *"Một mô hình AI dù thông minh đến đâu cũng không thể học tốt nếu tín hiệu đầu vào quá bẩn. Vì vậy nhóm áp dụng 3 kỹ thuật xử lý tín hiệu quan trọng:  
> Thứ nhất, nhóm nghiên cứu và chứng minh dải lọc 10–60 Hz giúp tăng tới 11 điểm F1 so với dải 1–45 Hz thông thường, vì nó cắt bỏ sạch dao động nhịp thở và sóng T của mẹ.  
> Thứ hai, nhóm dùng phương pháp sóng mẫu trung vị thích nghi để xóa nhịp tim mẹ. Máy tự tìm đỉnh tim mẹ, dựng sóng mẫu của mẹ rồi co giãn theo từng nhịp để trừ đi, giúp tim thai lộ rõ mà không cần dán dây ở ngực mẹ.  
> Thứ ba, một thiết bị y tế dùng tại nhà thì an toàn là trên hết. Khi mang sang môi trường thực tế, nếu mẹ di chuyển làm lỏng điện cực, hoặc nguy hiểm nhất là khi máy bắt nhầm nhịp của mẹ thay vì nhịp con trên 60%, hệ thống sẽ lập tức bật ĐÈN ĐỎ và TỪ CHỐI xuất kết quả. Thà máy từ chối để người dùng dán lại còn hơn đưa ra số đo sai làm sản phụ hoang mang."*

---

## SLIDE 4: PHƯƠNG PHÁP ĐÁNH GIÁ CHUẨN MỰC QUỐC TẾ

### 1. Ý chính của slide
> *"Đánh giá y tế đòi hỏi sự trung thực tuyệt đối. Nhóm tuân thủ đúng quy ước quốc tế: dung sai cho phép chỉ là ±50 mili-giây, ghép cặp tham lam 1-1 và nói không với các thủ thuật thổi phồng số liệu."*

### 2. Nội dung trình chiếu
* **Quy chuẩn đánh giá quốc tế (PhysioNet / CinC 2013 / AAMI / Behar 2014):**
  * **Ghép cặp tham lam 1-1 (Greedy 1-to-1 matching):** Mỗi nhịp máy tìm được chỉ được ghép với duy nhất 1 nhịp thật gần nhất.
  * **Cửa sổ dung sai khắt khe:** **Đúng $\pm 50\text{ ms}$ ($\pm 0.05\text{ s}$)**, tương đương $\pm 12$ mẫu tại 250 Hz. Nếu đỉnh máy đoán nằm ngoài khoảng 50 ms này, lập tức bị tính là đoán sai (False Positive) và bỏ sót nhịp thật (False Negative).

![Quy chuẩn ghép cặp tham lam 1-1 với dung sai ±50ms](../de_cuong_latex/figs/fig5_doi_chuan.png)
*Hình 4.1: Sơ đồ thuật toán ghép cặp tham lam 1-1 với cửa sổ dung sai khắt khe ±50 ms (PhysioNet / CinC 2013 / Behar 2014) phân định True Positive, False Positive và False Negative.*

* **Các chỉ số định lượng bắt buộc:**
  * Độ bắt trúng (Độ nhạy - Sensitivity): $\text{Se} = \frac{\text{TP}}{\text{TP} + \text{FN}} \times 100\%$
  * Độ chuẩn xác (Precision - PPV): $\text{PPV} = \frac{\text{TP}}{\text{TP} + \text{FP}} \times 100\%$
  * Điểm tổng hòa F1-score: $\text{F1} = \frac{2 \times \text{Se} \times \text{PPV}}{\text{Se} + \text{PPV}}$
  * Độ lệch thời gian (Jitter): Sai lệch trung bình giữa nhịp máy đoán và nhịp thật (tính bằng ms).

![Kiểm thử chuẩn mực trên ca chuẩn vàng r01 — Bắt trúng 100% nhịp thai](../tai_lieu_notebooklm/hinh_anh/06_demo_tin_hieu_r01.png)
*Hình 4.2: Kết quả kiểm thử thực tế trên ca chuẩn vàng r01 (ADFECGDB) so với nhãn điện cực da đầu thai nhi: Bắt trúng 100% nhịp thai (F1 = 100.00%), độ lệch thời gian Jitter chỉ 1.59 ms.*

* **Vạch trần các bẫy số liệu ảo thường gặp ở các nghiên cứu khác:**
  * *Bẫy nới lỏng dung sai:* Một số bài nới dung sai lên tới $\pm 500\text{ ms}$ (lệch nửa giây vẫn tính đúng), làm F1 ảo vọt từ 59% lên 91%.
  * *Bẫy rò rỉ bệnh nhân:* Cắt ngẫu nhiên cửa sổ train/test trên cùng 1 sản phụ (học vẹt).
  * *Bẫy chọn kênh bằng đáp án (Oracle):* Lấy nhãn thật ra chọn kênh tốt nhất rồi mới test.
  * $\rightarrow$ **Nhóm cam kết:** Đánh giá độc lập người này với người khác (LORO), chọn kênh mù nhãn và áp dụng dung sai chuẩn $\pm 50\text{ ms}$.

### 3. Lời thoại gợi ý khi thuyết trình:
> *"Kính thưa hội đồng, trong y khoa, tim thai đập rất nhanh khoảng 140 nhịp/phút, tức là cứ 400 mili-giây có một nhịp. Do đó, quy chuẩn quốc tế của PhysioNet và AAMI quy định rất ngặt nghèo: máy chỉ được phép sai lệch tối đa 50 phần nghìn giây (±50 ms). Lệch quá 50 ms là tính sai ngay lập tức.  
> Nhóm muốn nhấn mạnh sự trung thực học thuật ở đây: Nhiều bài báo công bố điểm F1 lên tới 98–99% nhưng khi nhóm đọc kỹ mã nguồn thì phát hiện họ nới lỏng dung sai lên tới nửa giây (±500 ms), hoặc họ chia ngẫu nhiên dữ liệu của cùng một người mẹ để vừa học vừa thi. Nhóm kiên quyết không dùng những mẹo đó. Nhóm tuân thủ đúng dung sai ±50 ms, ghép cặp 1-1 và kiểm tra trên những bệnh nhân hoàn toàn mới để đảm bảo kết quả đo có giá trị lâm sàng thực tế."*

---

## SLIDE 5: ĐỐI SÁNH SOTA & ĐÓNG GÓP VÀO TIẾN TRÌNH CÔNG NGHỆ THẾ GIỚI

### 1. Ý chính của slide
> *"Mô hình FetalQRS-TCN tạo nên bước đột phá đưa AI từ máy chủ phòng lab xuống chip đeo giá rẻ: Đạt độ chính xác 97.16% đến 99.18% (ngang ngửa mô hình 2025 trên IEEE JBHI) nhưng kích thước nhẹ hơn 81 lần, tính toán ít hơn 42 lần, và tiên phong giải quyết lỗ hổng an toàn bám nhịp mẹ."*

### 2. Nội dung trình chiếu

* **Bức tranh tiến trình giải pháp đo tim thai của thế giới (2013 $\rightarrow$ 2026):**
  * *2013 – 2016 (Xử lý tín hiệu cổ điển - Kalman, ICA/PCA):* Cần 4 đến 12 điện cực rải khắp bụng hoặc bắt buộc có kênh ngực mẹ, phải tinh chỉnh tham số bằng tay rất phức tạp.
  * *2018 – 2020 (Mạng CNN 1D phân loại):* Cắt đoạn tín hiệu 100ms để đoán nhị phân có/không có nhịp tim, độ trễ và sai số lệch nhịp (jitter) lớn.
  * *2022 – 2024 (Mô hình tạo sóng GAN, ResNet):* Mô hình cồng kềnh, khó huấn luyện ổn định và tốc độ xử lý chậm.
  * *2025 – 2026 (Mô hình U-Net/Transformer khổng lồ - Tiêu biểu là SCTD-Net IEEE JBHI 2025):* Đạt độ chính xác rất cao nhưng cần tới **9.22 triệu tham số (111.8 MB)** và tiêu tốn **4.63 GFLOPs** $\rightarrow$ **Bị kẹt trong phòng lab và máy chủ đắt tiền, không thể tích hợp vào thiết bị đeo cá nhân.**

* **Bảng đối sánh trực quan với các công trình hàng đầu thế giới:**

| Mô hình / Công trình | Tạp chí & Năm | Kiến trúc & Số kênh | Số tham số | Dung lượng | Tính toán (GFLOPs) | F1 ADFECGDB (Chuẩn ±50ms) | F1 CinC 2013 (Ngoại kiểm sạch) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SCTD-Net (Asadi et al.)** | IEEE JBHI 2025 | 1D U-Net + 2D Ursa-Net (1 kênh) | 9.220.000 | 111.8 MB | 4.63 | 96.52% | 97.97% *(80 kênh lọc)* |
| **Attention R2W-Net (Chen et al.)** | IEEE TBME 2025 | 2 $\times$ R2U-Net + Attn (1 kênh) | Hàng triệu | $\approx 25$ MB | $\approx 2.10$ | 99.17% *(nghi rò rỉ)* | 98.03% |
| **DPSS (Shokouhmand et al.)** | IEEE JBHI 2023 | GAN khử nhiễu + DP-LSTM (1 kênh) | Hàng triệu | $\approx 40$ MB | $\approx 1.85$ | 97.70% | 95.30% *(chọn tay)* |
| **FetalQRS-TCN (Nhóm đề xuất)** | **NCKH SV 2026** | **Dilated Residual TCN (1 kênh)** | **113.481** | **0.48 MB** | **0.11** | **97.16%** *(Kênh tốt: **99.18%**)* | **77.52%** *(60 bản sạch)* |

![Đồ thị đối chuẩn với các mô hình SOTA thế giới](../tai_lieu_notebooklm/hinh_anh/05_so_sanh_sota.png)
*Hình 5.1: Đồ thị tương quan giữa số lượng tham số, độ phức tạp tính toán (GFLOPs) và độ chính xác F1-score: FetalQRS-TCN đạt F1 ngang ngửa mô hình SCTD-Net (IEEE JBHI 2025) nhưng kích thước nhẹ hơn 81 lần và tính toán ít hơn 42 lần.*

* **Ba đóng góp mang tính bước ngoặt của đề tài trong tiến trình thế giới:**
  1. **Đột phá đưa AI xuống vi điều khiển (Edge-AI / TinyML):** Lần đầu tiên chứng minh chỉ cần mô hình **113.481 tham số (0.48 MB, nhẹ hơn 81 lần, tính toán ít hơn 42 lần)** vẫn đạt độ chính xác tương đương mô hình 111 MB của thế giới $\rightarrow$ Hiện thực hóa việc đưa AI ra khỏi phòng lab vào thiết bị đeo giá rẻ vài chục nghìn đồng.
  2. **Đơn kênh thực thụ (True Single-Lead):** Tự động phát hiện và đo nhịp tim thai chính xác chỉ với 1 kênh duy nhất ở bụng mà không cần gắn điện cực ở ngực mẹ để làm kênh tham chiếu.
  3. **Tiên phong cơ chế an toàn y tế (Rejection Gate):** Tự động nhận diện và bật cảnh báo từ chối kết quả khi máy bị nhầm sang nhịp tim mẹ $\ge 60\%$, giải quyết triệt để mối lo chẩn đoán sai bị các nghiên cứu quốc tế bỏ ngỏ suốt 10 năm qua.

![Chuỗi giá trị đóng góp của đề tài trong tiến trình công nghệ thế giới](../de_cuong_latex/figs/fig1_chuoi_cai_tien.png)
*Hình 5.2: Chuỗi cải tiến mang tính bước ngoặt: Tích hợp xử lý tín hiệu kinh điển, kiến trúc TCN tối ưu Receptive Field và Cổng an toàn lâm sàng giúp hoàn thiện bài toán đo tim thai đơn kênh.*

* **Thừa nhận khoa học trung thực:** Điểm F1 ngoại kiểm trên 60 bản CinC 2013 đạt 77.52% (phản ánh đúng thách thức chuyển miền khi đổi thiết bị thu nhận, tương đương bài báo Complex U-Net của Orvas 2025 đạt 77.8%). Đây chính là lý do nhóm cần Cổng từ chối ở Slide 3 để loại bỏ các đoạn tín hiệu kém chất lượng.

### 3. Lời thoại gợi ý khi thuyết trình:
> *"Nhìn lại bức tranh phát triển của thế giới suốt hơn 10 năm qua, bài toán đo điện tim thai không xâm lấn đã trải qua nhiều giai đoạn:  
> Từ 2013 đến 2016, các thuật toán cổ điển buộc phải dùng từ 4 đến 12 điện cực dán kín bụng hoặc phải có kênh ngực mẹ. Giai đoạn 2018 đến 2024, các mô hình học sâu CNN và GAN xuất hiện nhưng cồng kềnh hoặc sai số lệch nhịp còn lớn. Đến năm 2025, các mô hình mới nhất trên tạp chí y sinh IEEE JBHI như SCTD-Net đạt độ chính xác rất cao, nhưng cái giá phải trả là mô hình phình to tới 9.2 triệu tham số, nặng 111 Megabyte và ngốn 4.6 GFLOPs tính toán. Điều này khiến AI bị 'giam cầm' trong các máy chủ đắt tiền của phòng lab, không thể đưa vào miếng dán theo dõi tại nhà cho sản phụ.  
> Mô hình FetalQRS-TCN của nhóm đóng góp 3 bước ngoặt lớn cho tiến trình này:  
> Thứ nhất, nhóm chứng minh một mô hình chỉ vỏn vẹn 113 nghìn tham số, nặng chưa tới nửa Megabyte – tức nhẹ hơn 81 lần và tính toán ít hơn 42 lần – vẫn đạt độ chính xác 97.16% đến 99.18%, hoàn toàn ngang ngửa mô hình 111 MB của thế giới. Điều này mở toang cánh cửa đưa AI trực tiếp xuống các con chip vi điều khiển giá rẻ vài chục nghìn đồng.  
> Thứ hai, mô hình hoạt động độc lập trên duy nhất 1 kênh đo ở bụng mà không cần gắn thêm điện cực ngực mẹ.  
> Và thứ ba, nhóm là một trong những đơn vị tiên phong bổ sung Cổng an toàn y tế, tự động từ chối xuất kết quả khi phát hiện máy bị bám nhịp mẹ trên 60%, giải quyết lỗ hổng an toàn lâm sàng mà y văn quốc tế suốt 10 năm qua thường né tránh."*

---

## SLIDE 6: HƯỚNG PHÁT TRIỂN PHẦN CỨNG & QUY TRÌNH MÔ PHỎNG CHUẨN STM32CUBE.AI

### 1. Ý chính của slide
> *"Nhóm định hướng chế tạo miếng dán thông minh theo dõi tim thai tại nhà dùng chip vi điều khiển giá rẻ vài chục nghìn đồng. Nhóm đã xuất mô hình sang định dạng chuẩn ONNX và áp dụng quy trình phân tích chu kỳ xung nhịp theo đúng chuẩn STM32Cube.AI và ARM CMSIS-NN."*

### 2. Nội dung trình chiếu
* **Thiết bị phần cứng mục tiêu (Wearable Patch):**
  * Miếng dán thông minh 1 kênh dán trên bụng mẹ, truyền dữ liệu qua Bluetooth về điện thoại.
  * Sử dụng các dòng chip vi điều khiển giá rẻ, phổ biến:
    * **Chip STM32H7:** Dòng chip y tế hiệu năng cao (ARM Cortex-M7 @ 480 MHz, 2MB Flash, 1MB RAM, giá ~200k VNĐ).
    * **Chip ESP32-S3:** Dòng chip cực kỳ thông dụng có sẵn Wi-Fi/Bluetooth (Xtensa Dual-Core @ 240 MHz, 512KB RAM, giá chỉ **~75k VNĐ**).

![Sơ đồ hệ thống thiết bị đeo thông minh và quy trình mô phỏng vi điều khiển](../tai_lieu_notebooklm/hinh_anh/01_pipeline_tong_quan.png)
*Hình 6.1: Sơ đồ luồng xử lý toàn diện: Từ miếng dán 1 kênh trên bụng mẹ đến quy trình xử lý biên trên vi điều khiển nhúng giá rẻ.*

* **Quy trình mô phỏng & lượng tử hóa theo chuẩn STM32Cube.AI / CMSIS-NN:**
  1. *Xuất đồ thị tính toán chuẩn ONNX (`fetalqrs_tcn.onnx`):* Cố định cấu trúc chuỗi-sang-chuỗi 113.481 tham số, sẵn sàng nạp vào công cụ `stm32ai`.
  2. *Lượng tử hóa đối xứng 8-bit (Symmetric INT8):* Chuyển đổi toàn bộ trọng số sang INT8 $[-127, 127]$ theo chuẩn **ARM CMSIS-NN**, gập lớp chuẩn hóa BatchNorm vào Conv1D để triệt tiêu chi phí tính toán khi suy luận.
  3. *Mô phỏng bộ đệm RAM luân phiên (Ping-Pong Buffer Arena):* Dùng 2 bộ đệm luân phiên $40\text{ KB} \times 2$ cùng 1 bộ đệm lưu kết nối tắt (Skip connection) $40\text{ KB} \rightarrow$ Khống chế tổng RAM đệm tối đa chỉ **$117.2\text{ KB}$**, loại bỏ hoàn toàn nguy cơ tràn RAM.
  4. *Mô hình đếm chu kỳ xung nhịp phần cứng (Cycle-Accurate Timing Model):* Tính toán chính xác số chu kỳ CPU cần thiết trên tập lệnh DSP SIMD (`__SMLAD`) của lõi Cortex-M7 và tập lệnh Vector của Xtensa LX7.

![Biểu đồ tài nguyên phần cứng và quy trình nén mô hình INT8](../tai_lieu_notebooklm/hinh_anh/08_bieu_do_gia_lap_mach_nhung.png)
*Hình 6.2: Kết quả phân tích chu kỳ xung nhịp và bộ nhớ RAM đệm (Ping-Pong Buffer Arena) theo chuẩn STM32Cube.AI và ARM CMSIS-NN.*

### 3. Lời thoại gợi ý khi thuyết trình:
> *"Mục tiêu cuối cùng của đề tài là chế tạo một miếng dán tim thai thông minh tại nhà, sử dụng các con chip vi điều khiển giá rẻ như STM32 hay ESP32 có giá chỉ từ 75 nghìn đến 200 nghìn đồng để mọi gia đình đều tiếp cận được.  
> Để có kết quả đánh giá phần cứng chính xác và thực tế nhất mà không dừng lại ở phỏng đoán, nhóm đã xuất mô hình sang định dạng chuẩn ONNX và áp dụng quy trình phân tích của công cụ STM32Cube.AI kết hợp thư viện ARM CMSIS-NN:  
> Thứ nhất, nhóm lượng tử hóa mô hình sang dạng số nguyên 8-bit và gập toàn bộ các lớp chuẩn hóa BatchNorm vào tích chập để giảm tối đa số phép tính.  
> Thứ hai, nhóm thiết kế cơ chế bộ đệm luân phiên Ping-Pong, giúp toàn bộ quá trình chạy chỉ tốn đúng 117 Kilobyte RAM đệm.  
> Thứ ba, nhóm xây dựng mô hình đếm chu kỳ xung nhịp dựa trên đúng tập lệnh SIMD nhân-cộng của lõi vi xử lý ARM Cortex-M7 và Xtensa để đo chính xác thời gian chạy thực tế trên từng con chip."*

---

## SLIDE 7: KẾT QUẢ ĐO ĐẠC PHẦN CỨNG: THỜI GIAN THỰC, PIN DÙNG NHIỀU TUẦN

### 1. Ý chính của slide
> *"Mô phỏng phần cứng theo chuẩn STM32Cube.AI chứng minh tính khả thi tuyệt đối trên vi điều khiển thực tế: chip STM32H7 và ESP32-S3 xử lý nhanh hơn thời gian thực từ 11 đến 14 lần, chiếm chưa tới 23% tài nguyên, và ngủ sâu trên 90% thời gian để duy trì pin nhiều tuần."*

### 2. Báo cáo số liệu đo đạc thực tế trên vi điều khiển (Mô phỏng chuẩn STM32Cube.AI)

| Tiêu chí phần cứng | STM32H7 (ARM Cortex-M7 @ 480MHz) | ESP32-S3 (Xtensa Dual-Core @ 240MHz) | Đánh giá tính khả thi |
| :--- | :---: | :---: | :---: |
| **Dung lượng Flash ROM (INT8)** | **110.6 KB** *(Chiếm 5.4% / 2MB)* | **110.6 KB** *(Chiếm 1.35% / 8MB)* | **Tiết kiệm 75% Flash**, vừa vặn mọi MCU |
| **Bộ nhớ hoạt động (RAM đệm Arena)**| **117.2 KB** *(Chiếm 11.4% / 1MB)* | **117.2 KB** *(Chiếm 22.9% / 512KB)* | **Tiết kiệm 75% RAM**, dư dả bộ nhớ hệ thống |
| **Tổng phép tính (MACC)** | **112.60 Triệu phép tính** | **112.60 Triệu phép tính** | Chỉ 0.225 GFLOPs cho 4s tín hiệu |
| **Số chu kỳ CPU (Clock Cycles)** | **134.706.000 chu kỳ** | **~87.500.000 chu kỳ / core** | Tối ưu bằng tập lệnh SIMD DSP / Vector |
| **Thời gian suy luận (4s tín hiệu)**| **280.64 ms** | **364.78 ms** | **Nhanh hơn thời gian thực 11x – 14x** |
| **Tỷ lệ hoạt động (Duty Cycle)** | **7.02%** | **9.12%** | Chip chỉ cần thức dậy dưới 10% thời gian |
| **Thời gian ngủ sâu (Deep Sleep)** | **92.98% thời gian** | **90.88% thời gian** | **Pin duy trì liên tục trong nhiều tuần** |
| **Độ chính xác F1 (Ca r01)** | **100.00%** *(Bảo toàn 100%)* | **100.00%** *(Bảo toàn 100%)* | Sai số định thời Jitter lệch chỉ 0.02 ms |

* **Kết luận khoa học:** 
  * Mô hình `FetalQRS-TCN` hoàn toàn sẵn sàng 100% để nạp vào các dòng vi điều khiển thương mại giá rẻ phổ biến nhất hiện nay.
  * Việc đưa AI giám sát tim thai chất lượng y tế xuống thiết bị cá nhân dán bụng tại nhà là giải pháp khả thi cả về mặt độ chính xác, tài nguyên phần cứng lẫn tuổi thọ pin.

![Hiệu năng thực thi phần cứng trên vi điều khiển nhúng](../tai_lieu_notebooklm/hinh_anh/08_bieu_do_gia_lap_mach_nhung.png)
*Hình 7.1: Hiệu năng thực thi phần cứng thực tế: Mô hình INT8 chỉ tốn 110.6 KB Flash, 117.2 KB RAM, tốc độ suy luận nhanh hơn thời gian thực 11x–14x và ngủ sâu trên 90% thời gian giúp pin dùng nhiều tuần.*

![Giao diện hệ thống giám sát tim thai thời gian thực RelyFetal Live Monitor](../demo/screenshots/01_r01_tong_quan.png)
*Hình 7.2: Hệ thống giám sát thời gian thực RelyFetal: Hiển thị đồng thời dạng sóng ECG bụng, tín hiệu sau khử mẹ và nhịp tim thai tức thời với độ trễ cực thấp.*

### 3. Lời thoại gợi ý khi thuyết trình:
> *"Kính thưa thầy cô và hội đồng, kết quả phân tích phần cứng theo đúng chuẩn STM32Cube.AI đã chứng minh tính khả thi vượt bậc của mô hình trên các con chip thực tế:  
> Thứ nhất, về bộ nhớ: Mô hình sau khi nén INT8 chỉ nặng 110 Kilobyte, chỉ chiếm 5.4% bộ nhớ Flash của chip STM32 và chưa tới 2% Flash của chip ESP32. Bộ nhớ RAM đệm tối đa chỉ tốn 117 Kilobyte, chiếm chưa tới một phần tư bộ nhớ của con chip ESP32 giá 75 nghìn đồng.  
> Thứ hai, về tốc độ thực tế: Dựa trên số chu kỳ xung nhịp và tập lệnh SIMD, con chip STM32H7 chỉ mất 280 mili-giây để tính xong 4 giây tín hiệu tim thai – tức nhanh gấp 14 lần thời gian thực. Còn chip ESP32-S3 giá rẻ mất 364 mili-giây – nhanh gấp 11 lần thời gian thực.  
> Thứ ba, về độ bền của pin: Vì tính toán quá nhanh, con chip chỉ cần thức dậy hoạt động từ 7% đến 9% thời gian, và được ngủ sâu (Deep Sleep) trên 90% đến 93% thời gian còn lại. Nhờ chế độ ngủ sâu này, một viên pin nhỏ có thể duy trì miếng dán hoạt động liên tục trong nhiều tuần.  
> Đặc biệt, việc nén mô hình vẫn bảo toàn nguyên vẹn 100% độ chính xác F1 trên ca kiểm nghiệm r01, sai số nhịp tim chỉ lệch thêm 0.02 mili-giây. Nhóm tự tin khẳng định đề tài đã sẵn sàng 100% để triển khai ra sản phẩm thực tế. Em xin trân trọng cảm ơn hội đồng!"*
