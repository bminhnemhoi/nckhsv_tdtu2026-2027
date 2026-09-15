# ĐỀ CƯƠNG NGHIÊN CỨU KHOA HỌC SINH VIÊN — BÁO CÁO HIỆN TRẠNG

**RelyFetal — Dò phức bộ QRS thai nhi từ điện tim ổ bụng đơn kênh, có cổng từ chối trả lời**

> Bản gọn để đọc trong buổi gặp giảng viên hướng dẫn ngày 14/09/2026.
> Bản đầy đủ (148 trang, có toàn bộ nhật ký thí nghiệm) ở `de_cuong_latex/de_cuong.pdf`.
>
> **Quy ước của tài liệu này.** Mỗi bảng đều ghi tệp JSON nguồn ở chân bảng. Mọi con số trong
> tài liệu đã được đối chiếu trực tiếp với tệp trên đĩa tại thời điểm viết (13/09/2026).
> Chỗ nào chưa truy được về một tệp JSON thì ghi rõ **"chưa có trong nguồn"**, không suy đoán.
> Tài liệu phân biệt bốn mức phát biểu: **[SỰ KIỆN]** (có số đo), **[SUY LUẬN]** (diễn giải từ số đo),
> **[GIẢ THUYẾT]** (chưa kiểm chứng được), **[KHUYẾN NGHỊ]** (đề xuất hành động).

---

## 1. THÔNG TIN ĐỀ TÀI

| Mục | Nội dung |
|---|---|
| **Tên đề tài (tiếng Việt)** | Dò phức bộ QRS thai nhi từ điện tim ổ bụng đơn kênh có nhận biết độ tin cậy: đối chuẩn không rò rỉ và cổng từ chối trả lời |
| **Tên đề tài (tiếng Anh)** | Reliability-aware single-channel fetal QRS detection: a leakage-free benchmark and an abstention gate |
| **Tên hệ thống** | RelyFetal |
| **Chủ nhiệm đề tài** | Ngô Bình Minh |
| **Đơn vị** | Khoa Công nghệ Thông tin, Trường Đại học Tôn Đức Thắng |
| **Loại hình** | Nghiên cứu khoa học sinh viên, năm học 2026–2027 |
| **Nhóm thực hiện** | 03 sinh viên (phân vai ở mục 12) |
| **Thời lượng dự kiến** | 24 tuần; đã thực thi trước một phần (xem mục 11) |
| **Giảng viên hướng dẫn** | ……………………………………… *(để trống, chờ phân công)* |
| **Ngày báo cáo hiện trạng** | 13/09/2026 |
| **Mã commit của bản này** | `c20417b` (đã đẩy lên kho từ xa) |
| **Mục tiêu công bố** | 01 tạp chí (*Physiological Measurement*, Q2 Scimago 2024 — đích mặc định); 01 hội nghị (*Computing in Cardiology* 2027); 01 hồ sơ Euréka |

---

## 2. TÓM TẮT

*(296 từ)*

**Vấn đề.** Theo dõi tim thai hiện dựa vào Doppler (chỉ cho nhịp, cần kỹ thuật viên) hoặc điện cực xoắn
da đầu thai (chuẩn vàng nhưng xâm lấn, chỉ dùng được sau khi vỡ ối). Điện tim ổ bụng mẹ khắc phục cả
hai, nhưng ở cấu hình **một đạo trình** — rẻ nhất, dễ đưa vào đai đeo nhất — thì không còn dùng được
tách nguồn mù đa kênh, vốn là họ phương pháp chính xác nhất.

**Phương pháp.** Đề tài xây dựng **RelyFetal**: mạng tích chập thời gian giãn nở 113.481 tham số,
chuỗi-sang-chuỗi, nhận một đạo trình và cho ra bản đồ nhiệt xác suất từng mẫu, kèm **cổng từ chối trả
lời** dựng trên 12 chỉ số chất lượng tín hiệu cổ điển. Đánh giá ở mức chủ thể, dung sai ±50 ms,
bootstrap cụm, hiệu chỉnh Holm.

**Kết quả chính.** Trên 22 chủ thể trong miền, RelyFetal một kênh đạt F1 97,56, lấy lại **89,49 %**
phần lợi ích mà Power-MF có nhờ bốn kênh, và hơn Power-MF một kênh 10,85 điểm ở 22/22 chủ thể. Ngoài
miền, trên 60 bản CinC 2013 sạch, quy tắc chọn kênh mù nhãn chỉ định trước `gate4` nâng F1 từ 74,28 lên
81,01 và sống sót Holm (p = 0,015). Cổng từ chối đạt AUROC gộp 0,965.

**Đóng góp.** Kiểm toán chồng lấn dữ liệu định lượng: 15/75 bản set-a là bản sao nguyên văn của 5 bản
ADFECGDB huấn luyện, thổi phồng 3,27–7,18 điểm. Chồng lấn này đã được ban tổ chức ghi nhận từ 2013;
phần của nhóm là định danh từng bản và đo hậu quả.

**Giới hạn.** 22 chủ thể một hệ ghi; một hạt giống; chưa có bộ công khai thứ ba có nhãn fQRS thật.

---

## 3. ĐẶT VẤN ĐỀ

### 3.1 Ý nghĩa lâm sàng

Nhịp tim thai và hình thái phức bộ QRS thai là cửa sổ chính để phát hiện suy thai, thiếu oxy trường
diễn và một số bất thường tim bẩm sinh. Hai chỉ số được dùng nhiều nhất trong thực hành là **nhịp tim
thai cơ bản** và **biến thiên ngắn hạn (short-term variation, STV)** — STV thấp kéo dài là dấu hiệu
kinh điển của thai chậm phát triển trong tử cung.

### 3.2 Khoảng trống công nghệ

| Phương pháp | Ưu điểm | Giới hạn |
|---|---|---|
| Tim thai đồ / Doppler (CTG) | Không xâm lấn, phổ biến, rẻ | Chỉ cho **nhịp**, không cho hình thái sóng; cần kỹ thuật viên đặt đầu dò; không theo dõi liên tục tại nhà được |
| Điện cực xoắn da đầu thai | Chuẩn vàng, tín hiệu sạch | **Xâm lấn**; chỉ dùng được sau chuyển dạ và vỡ ối; không dùng cho theo dõi thai kỳ |
| Điện tim ổ bụng mẹ, không xâm lấn | Liên tục, tại nhà, chi phí thấp, **cho cả hình thái** | Tín hiệu thai bị tín hiệu mẹ lấn át; khó nhất ở cấu hình một kênh |

*Nguồn: mô tả lâm sàng chuẩn, đối chiếu `de_cuong_latex/sec_1_3.tex` mục "Bối cảnh lâm sàng".*

### 3.3 Vì sao chọn điện tim bụng mẹ, và vì sao **một** kênh

Cấu hình một đạo trình là cấu hình rẻ nhất và dễ tích hợp vào một miếng dán hoặc đai đeo nhất. Nhưng
chính nó loại bỏ khả năng tách nguồn mù đa kênh (ICA, PCA, πCA, SVD) — họ phương pháp đạt độ chính xác
cao nhất trong các đối chuẩn hiện có. **Câu hỏi trung tâm của đề tài** là: một mạng nơ-ron nhỏ, chạy
trên một kênh duy nhất, lấy lại được **bao nhiêu phần** lợi ích mà đa kênh mang lại — và nó có **tự biết**
khi nào mình sai hay không.

Bốn khó khăn định lượng của cấu hình một kênh, đo trên chính dữ liệu của đề tài:

| Thách thức | Hệ quả định lượng |
|---|---|
| Biên độ sóng thai nhỏ hơn sóng mẹ nhiều lần | Tỉ số RMS vùng QRS thai trên nền chỉ **1,24** ở dải 1–45 Hz; **1,64** ở dải 15–60 Hz |
| Nhịp mẹ và nhịp thai trùng pha | **17–19 %** nhịp thai nằm trong ±60 ms của một nhịp mẹ |
| Chất lượng từng kênh biến thiên cực lớn | Trên cùng một bản ghi, F1 theo từng kênh dao động **85,03 → 100,00** |
| Dữ liệu có nhãn rất ít | ADFECGDB chỉ có **5 sản phụ**; chia ngẫu nhiên trong cùng sản phụ là rò rỉ dữ liệu |

*Nguồn: `de_cuong_latex/sec_1_3.tex` bảng "khokhan" (số do nhóm tự đo trên ADFECGDB).*

---

## 4. TỔNG QUAN TÀI LIỆU

### 4.1 Cách chọn và đọc

Nhóm tải và đọc **toàn văn 30 công trình** (PDF lưu ở `papers/`, nhật ký tải ở `papers/papers_records.json`),
chọn theo bốn tiêu chí: được trích dẫn nhiều nhất trong dò QRS thai; mới nhất giai đoạn 2024–2026; mô tả
bộ dữ liệu và thử thách chuẩn; và nền tảng lý thuyết của phân tích dữ liệu topo mà bản đề cương đầu tiên
dựa vào. Với mỗi bài, nhóm ghi bảy điểm quyết định khả năng đối chiếu: **giao thức tách dữ liệu**, **dung
sai ghép nhịp**, **số kênh thật sự dùng**, **có tinh chỉnh trên tập đích không**, **dải thông**, **độ dài
cửa sổ ngữ cảnh**, **có báo cáo chi phí tính toán không**.

**[SỰ KIỆN]** Trong 30 công trình, chỉ **bốn** có giao thức đối chiếu trực tiếp được với giao thức của
nhóm. Phần còn lại rơi vào ít nhất một trong các trường hợp: chia ngẫu nhiên trong cùng chủ thể, dung
sai rộng hơn, gộp nhiều kênh ở bước cuối, tinh chỉnh trên tập đích, hoặc đơn vị phân tích là cửa sổ tín
hiệu thay vì nhịp tim.

### 4.2 Bốn hướng và mười công trình quan trọng nhất

| # | Tác giả – năm | Phương pháp | Dữ liệu | Kết quả họ báo cáo | Số kênh | Vị trí so với nhóm |
|---|---|---|---|---|---|---|
| 1 | **Jaeger et al. 2024 — Power-MF**<br>DOI 10.1088/1361-6579/ad4952 | Xử lý tín hiệu cổ điển: lọc đạo hàm, khử mẹ bằng SVD+ICA, chọn kênh theo PSD, bộ lọc phù hợp | Silesia B1 (10 bản), B2 (12 bản), 500 Hz | F1 99,5 ± 0,5 (B1); 98,0 ± 3,0 (B2), dung sai 50 ms | **4** | **Đối thủ mạnh nhất; đã chạy lại thật** qua GNU Octave và chấm bằng cùng bộ chấm. Tái lập số công bố đến 0,06 điểm (B1: 99,40 vs 99,46) |
| 2 | **Zhong et al. 2018**<br>DOI 10.1088/1361-6579/aab297 | CNN 1D nông 3 khối | CinC 2013 | F1 77,85 | 1 | Công trình học sâu nền tảng. **Cảnh báo trích dẫn:** 77,85 là F1 **phân loại nhị phân cửa sổ 100 ms trên tập cân bằng lớp nhân tạo**, không phải F1 dò nhịp CinC. Nhiều bài về sau trích lại như thể là F1 dò nhịp |
| 3 | **Clifford, Silva, Behar, Moody 2014**<br>DOI 10.1088/0967-3334/35/8/1521 | Xã luận tổng quan Challenge 2013 | CinC 2013, 447 bản | — | 4 | **Nguồn gốc của cảnh báo chồng lấn dữ liệu** mà nhóm đã bỏ sót (mục 7.2) |
| 4 | **Silva et al. 2013**, Comput Cardiol 40:149–152<br>*(không có DOI; ISSN 2325-8861)* | Mô tả Challenge | 447 bản từ 5 nguồn | — | 4 | Bảng 1 ghi rõ "Abdominal and Direct FECG — **25**" bản ghi. **Đây là bằng chứng chồng lấn đã công bố từ 2013** |
| 5 | **Andreotti et al. 2016**<br>DOI 10.1088/0967-3334/37/5/627 | Khung stress-test nguồn mở | 145,8 giờ tín hiệu tổng hợp | Chứng minh lựa chọn tiền xử lý **đảo thứ hạng** thuật toán | 4 | **Tiền lệ của luận điểm "front-end quan trọng hơn"** — ở dạng định tính, trên dữ liệu tổng hợp. Nhóm **tiếp nối**, thêm số trên dữ liệu thật |
| 6 | **Andreotti et al. 2017**<br>DOI 10.1109/TBME.2017.2675543 | Chỉ số chất lượng tín hiệu fECG (fSQI) | fECG | — | đa kênh | **Cổng từ chối không phải ý tưởng mới của nhóm.** Phần còn lại của nhóm: đánh giá xuyên hệ ghi, zero-shot, kèm đường cong rủi ro–độ phủ |
| 7 | **Fotiadou et al. 2021**<br>DOI 10.1088/1361-6579/abf7db | CNN-LSTM giãn nở kiểu inception | fECG thật | Ước lượng nhịp tim thai | đa kênh | **Tiền lệ của "trường tiếp nhận là biến kiến trúc quan trọng nhất"**, trong chính lĩnh vực fECG và chính tạp chí nhóm nhắm tới |
| 8 | **Zahid et al. 2022**<br>DOI 10.1109/TBME.2021.3088218 | Phân đoạn 1 chiều theo từng mẫu cho dò đỉnh R | Holter chất lượng thấp | — | 1 | **Tiền lệ của đầu ra theo từng mẫu.** Gaussian σ = 12 ms của nhóm chỉ là làm mượt nhãn, không phải phát biểu bài toán mới |
| 9 | **Huang et al. 2025 — TCGAN**<br>DOI 10.1109/JBHI.2024.3524085 | GAN tích chập thời gian, trích fECG | Dữ liệu thật | PPV 99,02 % | **1** | **Đối thủ trực tiếp nhất ở cấu hình đơn kênh**, đăng đúng tạp chí mục tiêu. Không dùng làm baseline được (đầu ra là dạng sóng, không phải vị trí fQRS) nhưng bắt buộc phải trích |
| 10 | **Matonia et al. 2020**<br>DOI 10.1038/s41597-020-0538-z | Mô tả bộ dữ liệu Silesia | 10 bản thai kỳ + 12 bản chuyển dạ | — | 4–5 | **Bộ dữ liệu chính của đề tài.** Baldazzi & Pani 2023 (DOI 10.1007/978-3-031-32625-7_12) đã in rằng bộ này *"shares signals with ADFECGDB"* |

*Mọi DOI trong bảng đã được xác minh (ghi trong `de_cuong_latex/tables/danhmuc.tex` và `survey/ro_ri_vanlieu.json`).
Silva et al. 2013 **chưa xác minh DOI** — Crossref không có bản ghi; nguồn truy cập: cinc.org/archives/2013/pdf/0149.pdf.
Danh mục đầy đủ 30 công trình ở `de_cuong_latex/tables/danhmuc.tex`.*

### 4.3 Điều tổng quan tài liệu buộc nhóm phải sửa

**[SUY LUẬN]** Sáu trong bảy tài liệu tìm thêm ở vòng rà soát thứ ba **làm yếu đi** một tuyên bố của
nhóm chứ không củng cố nó. Hệ quả: nhóm **định vị lại đề tài là tiếp nối, không phải phản bác**.
Andreotti 2016 đã nói đúng điều nhóm đo được (tiền xử lý đảo thứ hạng), chỉ là nói định tính trên dữ
liệu tổng hợp; Andreotti 2017 đã có fSQI; Fotiadou 2021 đã quét trường tiếp nhận; Zahid 2022 đã có đầu
ra từng mẫu. Điều còn lại nhóm gọi là mới: **chưa công trình nào ghép ba tầng front-end / ngữ cảnh /
kiến trúc vào một thí nghiệm duy nhất trong fECG**, giữ cố định bộ phân loại, dữ liệu, giao thức và
ngân sách huấn luyện.

---

## 5. MỤC TIÊU VÀ CÂU HỎI NGHIÊN CỨU

**Mục tiêu tổng quát.** Xây dựng và đánh giá nghiêm ngặt một bộ dò phức bộ QRS thai nhi hoạt động trên
**một** đạo trình điện tim ổ bụng, kèm cơ chế **tự báo độ tin cậy**, dưới một giao thức đánh giá không
rò rỉ dữ liệu.

| Mã | Mục tiêu cụ thể | Câu hỏi trả lời được bằng số liệu | Trạng thái |
|---|---|---|---|
| **MT1** | Đo xem một mạng đơn kênh lấy lại được bao nhiêu phần lợi ích của tách nguồn đa kênh | Tỉ lệ lấy lại (Power-MF 4 kênh − 1 kênh) là bao nhiêu, KTC 95 % có loại 0 không? | **Đã trả lời** — mục 8(a) |
| **MT2** | Tách bạch đóng góp của ba tầng: front-end tín hiệu, độ dài ngữ cảnh, họ kiến trúc | Giữ cố định tham số ±2,7 %, cùng hạt giống và giao thức, họ kiến trúc nào khác biệt? Trường tiếp nhận bão hoà ở đâu? | **Đã trả lời** — mục 8(c) |
| **MT3** | Xây quy tắc chọn kênh **mù nhãn** và kiểm chứng ngoài miền | Trong bảy quy tắc khai báo trước, quy tắc nào sống sót hiệu chỉnh đa so sánh trên tập ngoài miền? | **Đã trả lời một phần** — mục 8(b); chưa nhân rộng được |
| **MT4** | Xây cổng từ chối trả lời và đo đường cong rủi ro–độ phủ | Cổng có xếp đúng các bản ghi mà hệ thống sẽ sai không? AUROC bao nhiêu? | **Đã trả lời trong miền** — mục 8(e); chưa tính lại trên 60 bản sạch |
| **MT5** | Đo giới hạn: hệ thống sai ở đâu, có thể dùng cho chỉ số lâm sàng nào | Phổ lỗi phân bố thế nào so với mức ngẫu nhiên? Sai số STV bám sát F1 ra sao? | **Đã trả lời** — mục 8(e), 10 |

**[SUY LUẬN]** Bốn trong năm mục tiêu đã có số liệu trả lời. Điều đó đúng vì đề tài **đã được thực thi
trước một phần** trong tháng 9/2026 (mục 11), không phải vì mục tiêu đặt quá dễ.

---

## 6. PHƯƠNG PHÁP

### 6.1 Đường ống năm bước

| Bước | Nội dung | Chi tiết |
|---|---|---|
| 1 | **Lọc front-end** | Butterworth 10–60 Hz pha-không (`filtfilt`) + chặn khấc 50 Hz; hạ mẫu về 250 Hz |
| 2 | **Khử điện tim mẹ** | Mẫu trung vị theo nhịp + co giãn theo tỉ lệ bình phương tối thiểu từng nhịp |
| 3 | **Chọn kênh mù nhãn** | Quy tắc dựa trên mật độ phổ công suất / cổng đa tiêu chí — **không nhìn nhãn** (mục 8b) |
| 4 | **Mạng dò** | FetalQRSTCN — chuỗi-sang-chuỗi, ra bản đồ nhiệt Gauss từng mẫu (σ = 12 ms) |
| 5 | **Cổng từ chối trả lời** | 12 chỉ số chất lượng tín hiệu cổ điển, phân loại từng đoạn 4 s |

### 6.2 Kiến trúc mô hình

| Tham số | Giá trị | Nguồn |
|---|---|---|
| Họ kiến trúc | TCN giãn nở dư, 5 khối, c = 40 | `analysis/kientruc_results.json` → `table.tcn.desc` |
| Số tham số | **113.481** | `analysis/kientruc_results.json` → `table.tcn.params` |
| Trường tiếp nhận | 379 mẫu = **1.516 ms** | `analysis/kientruc_results.json` → `table.tcn.rf_ms` |
| Độ rộng nhãn Gauss | σ = **12 ms** | `analysis/kientruc_results.json` → `table.tcn.sigma_ms` |
| Kích thước tệp | 0,48 MB | **chưa có trong nguồn JSON** — chỉ ghi ở `README.vi.md`, `docs/KICH_BAN_TRINH_BAY.md` |
| Thời gian suy diễn | 4,35 ms / cửa sổ 4 s trên CPU | **chưa có trong nguồn JSON** — chỉ ghi ở `README.vi.md`, `docs/KICH_BAN_TRINH_BAY.md` |
| Tần số làm việc | 250 Hz (sau hạ mẫu từ 1 kHz) | `model/fqrs_model.py` |

### 6.3 Giao thức huấn luyện

- 22 chủ thể, chia nhóm **11 fold theo chủ thể** (grouped): chủ thể dùng để kiểm không bao giờ xuất
  hiện trong tập huấn luyện của fold đó.
- Có tăng cường dữ liệu; 12 checkpoint cho mô hình chính, lưu ở `model/checkpoints/` (**20 tệp** tại
  thời điểm viết).
- **Kết quả chính chạy trên một hạt giống (seed 0).** Seed 1 đã chạy để đo độ ổn định nhưng **không có
  checkpoint lưu lại** (`train_22.py` chỉ lưu khi `--tag` rỗng) — xem mục 10.

### 6.4 Giao thức đánh giá, và vì sao chọn như vậy

| Lựa chọn | Nội dung | Lý do |
|---|---|---|
| **Dung sai ghép nhịp ±50 ms** | Quy ước CinC 2013 | 150 ms là chuẩn AAMI EC57 cho **người lớn**; nới dung sai làm con số đẹp lên mà không cần cải tiến gì |
| **Đơn vị phân tích: mức chủ thể** | Tính F1 từng chủ thể rồi lấy trung bình vĩ mô | Một bản ghi B1 có ~2.800 nhịp, một bản CinC có ~140 nhịp; gộp toàn bộ nhịp lại sẽ để bản ghi dài chi phối kết quả |
| **Bootstrap cụm theo chủ thể** | Lấy lại mẫu ở cấp chủ thể, không ở cấp nhịp | Các nhịp trong cùng một bản ghi không độc lập |
| **Hiệu chỉnh Holm** | Trên **bảy** quy tắc chọn kênh | Bảy quy tắc cùng được thử trên một tập; không hiệu chỉnh thì tỉ lệ dương tính giả tăng |
| **Báo cáo cả thang logit** | Song song với F1 thô | Nhiều chủ thể chạm F1 = 100 nên hiệu số thô bị nén ở trần |

### 6.5 Cổng từ chối trả lời

- **12 đặc trưng cổ điển**, không có đặc trưng học từ mạng: `sampen`, `kurtosis`, `spec_entropy`,
  `band_ratio`, `rr_cv`, `rr_plaus`, `bsqi`, `n_det`, `psd_fhr`, `tau_acf`, `peak_prob_mean`, `prob_max`.
- Đơn vị: đoạn **4 giây**. Nhãn "xấu" = đoạn thuộc bản ghi có F1 < 80.
- Bộ học: `HistGradientBoostingClassifier`, kiểm chéo **leave-one-SUBJECT-out** trên 22 chủ thể.

*Nguồn: `analysis/gate22_results.json` → `thiet_ke`.*

---

## 7. DỮ LIỆU

### 7.1 Bốn bộ dữ liệu

| Bộ | Dung lượng | Nội dung | Loại nhãn | Dùng để |
|---|---|---|---|---|
| **ADFECGDB** (PhysioNet) | 15 MB | 5 bản `.edf` + `.edf.qrs`; 1 kHz, 5 phút, 4 kênh bụng + 1 kênh trực tiếp | **Trực tiếp** từ điện cực da đầu thai | Huấn luyện + kiểm trong miền |
| **Silesia** (`Data Records/`) | 681 MB | B1: 10 bản thai kỳ; B2: 12 bản chuyển dạ | B2 **trực tiếp** (điện cực da đầu); B1 **gián tiếp** | Huấn luyện + kiểm trong miền |
| **CinC 2013 set-a** (`benchmark_dpss/pcdb/`) | 35 MB | 75 bản `.dat`/`.hea`/`.fqrs`; 1 kHz, 60 s, 4 kênh | Nhãn do người chấm **độc lập** | Kiểm **ngoài miền** (60 bản sạch) |
| **NSTDB** | 5,6 MB | Nhiễu chuẩn MIT-BIH | — | Thí nghiệm đường cong F1–SNR |

**Hai bộ đã kiểm và loại** (`analysis/xacnhan_results.json` → `viec2_bo_thu_ba`):
**NIFEADB** (178 MB, 26 bản) — PhysioNet 1.0.0 không có tệp `.qrs`/`.atr`/`ANNOTATORS`, **không có chú
thích thai**. **NInFEA** (16 MB) — không có tệp chú thích nhịp; tham chiếu gốc là Doppler.
Ngoài ra `nifecgdb` (thăm dò 1 bản) có `.qrs` nhưng 375 nhãn/270 s → RR trung vị 0,695 s = **86 nhịp/phút**,
tức là **QRS mẹ**, không phải thai. CinC set-b: nhãn không công bố.

**[SỰ KIỆN]** Vậy **không có bộ công khai thứ ba nào có nhãn fQRS thật**. Đây là rào cản chính của đề tài.

### 7.2 Chồng lấn 15 bản ghi giữa CinC 2013 set-a và ADFECGDB

**[SỰ KIỆN]** Mỗi bản ADFECGDB xuất hiện **đúng 3 lần** trong set-a, theo ba cửa sổ 0–60 s / 120–180 s /
240–300 s:

| Bản ADFECGDB | Ba bản set-a tương ứng |
|---|---|
| r01 | a04, a05, a22 |
| r04 | a13, a20, a25 |
| r07 | a19, a23, a24 |
| r08 | a08, a15, a17 |
| r10 | a03, a12, a14 |

Bằng chứng đo lường: **NCC = 1,0000** trên cả 4 kênh đúng thứ tự; **lệch RR = 0,0 ms**. Đối chứng dương
(trùng lặp đã biết B2 ↔ PhysioNet, cùng sản phụ nhưng khác xử lý) cho NCC 0,856–0,984; **60 bản còn lại
tối đa 0,62**. Mức thổi phồng F1 do 15 bản này gây ra: **3,27–7,18 điểm** (m5 +7,18 | m12 +6,41 |
m22 +5,12 | oracle +3,27).

> ### ⚠️ Tuyên bố quyền ưu tiên — nhóm đã BỎ SÓT một cảnh báo đã có
>
> **Sự chồng lấn này đã được ban tổ chức Challenge ghi nhận công khai:** Silva et al., *Comput Cardiol*
> 2013;40:149–152, Bảng 1 ghi *"Abdominal and Direct FECG — 25"*; Clifford et al., *Physiol Meas*
> 2014;35:1521 (DOI 10.1088/0967-3334/35/8/1521) cảnh báo nguyên văn. **Cảnh báo đó nằm ngay trong ghi
> chú đọc bài của chính nhóm** (`bang_baihoc` p13/p20) mà nhóm bỏ sót khi lập kế hoạch đánh giá.
>
> **Phát biểu đúng:** *"Như ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014], set-a chứa bản ghi
> ADFECGDB; chúng tôi xác định bằng đo lường đúng 15 bản nào và mức thổi phồng."*
> Cái mới của nhóm **chỉ là định danh từng bản ghi và định lượng hậu quả**, không phải phát hiện.

Ngoài 15 bản chồng lấn, 7 bản khác bị xác định là **chú thích sai**: a33, a38, a47, a52, a54, a71, a74.
Kết quả chính báo cáo trên **60 bản sạch**; có thêm nhánh 53 bản (loại tiếp 7 bản nhãn sai) để đối chiếu.

### 7.3 Điểm yếu dữ liệu — nói thẳng

1. **22 chủ thể** là mẫu nhỏ cho một bài toán sinh học có biến thiên lớn giữa các cá thể.
2. **Nhãn B1 là gián tiếp**, mà B1 chiếm **76,9 %** tổng thời lượng của tập trong miền (11.978 s trên
   15.578 s — tính từ `analysis/clinical_results.json` → `records[].duration_s`). Trung vị lệch so với
   nhãn da đầu giữ ở 0,0 ms, nhưng 5/10 bản B1 lệch 8–12 ms.
3. **Một hệ ghi, một trung tâm** (Đại học Y Silesia, Ba Lan) cho toàn bộ tập trong miền.
4. **Không có bộ công khai thứ ba có nhãn thật** để nhân rộng kết luận chọn kênh.
5. CinC set-a chỉ 60 giây mỗi bản → ít nhịp, phương sai ước lượng F1 từng bản lớn.

---

## 8. KẾT QUẢ

### (a) Bảng 1 — 22 chủ thể trong miền: RelyFetal so với Power-MF

| Hệ thống | Số kênh | F1 trung bình vĩ mô | So với RelyFetal | KTC 95 % | p (Wilcoxon) | Thắng/Hoà/Thua |
|---|---|---|---|---|---|---|
| **Power-MF** (Jaeger 2024) | 4 | **98,83** | RelyFetal − PMF4 = **−1,27** | [−3,08; +0,27] | 0,156 | 18 / 0 / 4 |
| **RelyFetal** (quy tắc PSD) | **1** | **97,56** | — | — | — | — |
| **Power-MF một kênh** (nhóm tự cài lại) | 1 | **86,71** | RelyFetal − PMF1 = **+10,85** | [+6,80; +15,40] | 4,8 × 10⁻⁷ | **22 / 0 / 0** |
| Khoảng cách do đa kênh tạo ra | — | — | PMF1 − PMF4 = **−12,12** | [−18,27; −6,90] | 1,4 × 10⁻⁶ | 1 / 0 / 21 |

**Tỉ lệ lấy lại:** RelyFetal một kênh lấy lại **89,49 %** phần lợi ích của đa kênh
(10,847 / 12,1212 điểm), KTC 95 % bootstrap cụm **[81,4 ; 103,2]**, jackknife bỏ từng chủ thể
**88,6 – 93,4 %**, và 99,1 % lần bootstrap cho tỉ lệ trên 80 %.

**Kiểm chứng ngoài:** Power-MF chạy lại qua GNU Octave cho F1 **99,40** trên Silesia B1, so với **99,46**
mà tác giả công bố — lệch 0,06 điểm.

> **[SUY LUẬN]** Dấu của hiệu số chính là **âm**: mạng một kênh của nhóm **không** vượt được Power-MF bốn
> kênh (−1,27, KTC chạm 0, p = 0,156). Kết quả trung thực là *"một kênh lấy lại gần chín phần mười lợi
> ích của bốn kênh"*, không phải *"một kênh tốt hơn bốn kênh"*.

*Nguồn: `baselines/powermf_fair_stats.json` → `so_sanh.tat_ca_22`; `analysis/recovery_ratio.json`.*

---

### (b) Bảng 2 — 60 bản CinC 2013 sạch, bảy quy tắc chọn kênh mù nhãn

| Quy tắc | Loại khai báo | F1 (60 sạch) | Hiệu so với psd | KTC 95 % | p Wilcoxon | **p Holm** (7 quy tắc) | Bản F1 < 50 | Thắng / Thua / Hoà |
|---|---|---|---|---|---|---|---|---|
| `psd` | mốc tham chiếu | 74,28 | 0,00 | — | 1,00 | — | 16 | — |
| `learned` | khai báo trước | 77,80 | +3,52 | [−0,77; +8,48] | 0,69 | 1,00 | 16 | 15 / 13 / 32 |
| `rrplaus` | khai báo trước | 78,87 | +4,59 | [+0,88; +8,93] | 0,13 | 0,41 | 14 | 17 / 9 / 34 |
| `rrcv` | khai báo trước | 80,00 | +5,72 | [+1,61; +10,41] | 0,10 | 0,41 | 12 | 15 / 10 / 35 |
| `gate` | **chỉ định trước (trọng tài)** | 80,72 | +6,44 | [+2,49; +11,10] | 0,010 | **0,051 → TRƯỢT** | 12 | 16 / 7 / 37 |
| **`gate4`** | **chỉ định trước** | **81,01** | **+6,72** | **[+2,85; +11,18]** | 0,0025 | **0,015 → SỐNG SÓT** | 12 | 17 / 5 / 38 |
| `peakprob` | **hậu kiểm** | **82,01** | **+7,73** | [+3,82; +12,41] | 5,6 × 10⁻⁴ | 0,0039 | **9** | 19 / 6 / 35 |
| `oracle` (trần) | nhìn nhãn | 83,60 | +9,32 | [+5,10; +14,15] | — | — | 8 | — |

**Đọc bảng này cho đúng:**

- **[SỰ KIỆN]** `gate4` là quy tắc **chỉ định trước** (nằm trong cùng hồ khai báo trước) và **sống sót**
  hiệu chỉnh Holm với p = 0,015. **Đây là kết quả trung thực mạnh nhất của đề tài.**
- **[SỰ KIỆN]** `gate` — quy tắc được chỉ định làm **trọng tài** theo F1 trong miền — **trượt** Holm
  (p = 0,051). Nhóm báo cáo thất bại này nguyên vẹn.
- **[GIẢ THUYẾT]** `peakprob` cho F1 thô cao nhất (82,01), lấy lại **82,92 %** dư địa oracle, kéo số bản
  F1 < 50 từ 16 xuống **9**, và **không bản nào mất quá 3,90 điểm**. Nhưng đây là **lựa chọn hậu kiểm**:
  trên thang logit 22 chủ thể, `gate` mới đứng đầu còn `peakprob` hạng 3 (+0,134, KTC [−0,038; +0,407],
  Holm 1,00). Không có bộ thứ ba có nhãn thật để xác nhận → **chưa nhân rộng được**.
- Bản khai báo trước (`analysis/chonkenh_khaibao_truoc.json`) **không được bên thứ ba neo** và được viết
  sau khi đã có F1 từng kênh. Vì vậy tài liệu này **không dùng chữ "tiền đăng ký"**.

*Nguồn: `analysis/dulieu_results.json` → `chon_kenh_60_sach.bang.*`; `benchmark_dpss/eval_cinc60_sach.json`;
`analysis/xacnhan_results.json` → `viec3_logit_22`.*

**Nhánh đối chiếu (loại tiếp 7 bản nhãn sai, còn 53 bản):** psd m5 64,19 → m22 75,27, hiệu +11,08
KTC [7,54; 14,82], p = 4,4 × 10⁻⁹. **Power-MF một kênh trên 60 bản sạch:** F1 **55,97** [48,08; 64,03];
RelyFetal hơn **+18,32** [13,35; 23,64], thắng 49 / thua 6 / hoà 5.

---

### (c) Bảng 3 — Bảy họ kiến trúc, cùng tham số ±2,7 %

Giao thức thu nhỏ: **3 epoch, 3 fold, 1 hạt giống** (80,95 phút tổng); mọi họ dùng cùng seed, cùng fold,
cùng ngân sách.

| Họ | Tham số | Lệch so với TCN | Trường tiếp nhận | F1 (kênh PSD) | KTC 95 % | F1 (trung bình 4 kênh) | Jitter (ms) | Kết luận |
|---|---|---|---|---|---|---|---|---|
| **tcn** (sản xuất) | 113.481 | 0,0 % | 1.516 ms | **97,64** | [95,51; 99,28] | 96,41 | 3,80 | mốc |
| `rf_wide` | 116.514 | +2,67 % | 3.052 ms | 97,63 | [95,43; 99,31] | 96,60 | 3,60 | **TƯƠNG ĐƯƠNG** (TOST Holm 7,1 × 10⁻¹⁰) |
| `tcn_ms` | 116.011 | +2,23 % | 2.716 ms | 97,62 | [95,38; 99,39] | 96,38 | 3,76 | **TƯƠNG ĐƯƠNG** (TOST Holm 4,6 × 10⁻⁶) |
| `rf_narrow` | 114.886 | +1,24 % | 748 ms | 96,93 | [94,21; 99,24] | 94,65 | 3,97 | kém hơn, không kết luận được |
| `cnn_wide` | 114.943 | +1,29 % | 1.508 ms | 96,84 | [93,84; 99,22] | 95,63 | 3,95 | kém hơn, không kết luận được |
| `unet1d` | 114.247 | +0,68 % | 636 ms | 96,38 | [93,26; 99,04] | 94,08 | 3,91 | kém (Holm-Wilcoxon 0,021) |
| `cnn_l` | 114.493 | +0,89 % | **60 ms** | **94,53** | [89,99; 98,27] | 89,91 | 4,52 | **kém 3,10 điểm** (Holm-Wilcoxon 7,2 × 10⁻⁴); Δlogit −1,64 [−2,09; −1,16], 2/0/20 |

**[SUY LUẬN] Kết luận quan trọng nhất của bảng này là một kết luận phủ định cho chính mô hình của nhóm.**
Họ kém nhất (`cnn_l`) chỉ kém vì **trường tiếp nhận 60 ms**. Khi nới trường tiếp nhận cho khớp TCN mà
vẫn giữ kiến trúc đó (`cnn_wide`, 1.508 ms), F1 lên **96,84**, tức là khoảng cách **đo bề rộng ngữ cảnh
chứ không đo họ kiến trúc**. Trường tiếp nhận **bão hoà ở khoảng 1,5 giây** (3.052 ms không hơn 1.516 ms).
Nhân bốn lần tham số chỉ thêm **+0,26 điểm** trong mẫu.

**[KHUYẾN NGHỊ]** Đầu tư thêm vào mô hình là hướng có tỉ suất sinh lợi thấp nhất trong đề tài này.

*Nguồn: `analysis/kientruc_results.json` → `table`, `comparisons`, `holm_wilcoxon`, `holm_tost`, `meta.run_meta`.*

**Dải lọc — một tuyên bố cũ đã bị chính nhóm bác bỏ:** lặp lại khảo sát dải lọc **trên chính TCN**,
10–60 Hz so với 1–45 Hz cho **+2,44** [−0,04; +6,29] trên kênh PSD, nhưng **−0,07** [−0,51; +0,39] trên
trung bình 4 kênh. Con số cũ **+11,00** (đo trên GBM cửa sổ 300 ms, không phải TCN) **đã rút**.
*Nguồn: `pilot_evidence/band_tcn_stats.json`.*

---

### (d) Bảng 4 — Bốn phương pháp thích nghi miền không nhãn, trên 60 bản sạch

| Phương pháp | F1 sau thích nghi | Hiệu so với mốc 74,28 | p (Wilcoxon, ghép cặp) | Kết quả |
|---|---|---|---|---|
| Chặn khấc điện lưới thích nghi (`notch`) | 74,53 | **+0,25** | 0,68 | **Không cải thiện có ý nghĩa** |
| Tự huấn luyện bằng nhãn giả (`pl`) | 73,61 | **−0,67** | 0,003 | **Xấu đi** |
| AdaBN | 72,70 | **−1,58** | 0,001 | **Xấu đi** |
| TENT | 71,85 | **−2,43** | < 0,001 | **Xấu đi** |

**[SỰ KIỆN] Cả bốn đều thất bại.** Ba trong bốn làm hệ thống **xấu đi** có ý nghĩa thống kê.

**Thí nghiệm mô phỏng dịch chuyển:** áp cả ba dịch chuyển đo được (cửa sổ 60 s, lượng tử hoá 10,13 bit
hiệu dụng, điện lưới 60 Hz) lên 22 chủ thể trong miền chỉ làm mất **0,013 điểm** (97,330 → 97,317),
trong khi khoảng cách thật giữa hai miền còn **17,92 điểm**.

> **[SUY LUẬN] KHÔNG được kết luận "thiếu tín hiệu thật".** Phép thử "nhìn thấy" dùng để kết luận điều đó
> có **tỉ lệ âm tính giả 18,0 %** [12,1 ; 25,0] trên chính 60 bản sạch. Nguyên nhân của khoảng cách 17,92
> điểm **chưa xác định được**. Kết luận cũ *"mô hình không phải nút thắt"* **đã rút**.

*Nguồn: `adapt/adapt_results.json` → `per_record_cinc` (tự tính lại sau khi loại đúng 15 bản chồng lấn;
phép tính này đã được thẩm định độc lập, `docs/nhat_ky/THAMDINH_VONG8.md` mục 1.2 số 21) và `mo_phong_dich_chuyen`;
`analysis/xacnhan_results.json` → `viec4_phep_thu_nhin_thay`.*

*Ghi chú chênh lệch: `README.vi.md` ghi self-training **−0,68** và p của notch là **0,70**; tính lại từ
JSON gốc cho **−0,67** và **p = 0,68**. Chênh do làm tròn / phiên bản bootstrap; bảng trên dùng số tính
lại từ JSON.*

---

### (e) Bảng 5 — Cổng từ chối trả lời và phổ lỗi

**Cổng từ chối** (22 chủ thể, LOSO, 12 chỉ số cổ điển, đoạn 4 s, 3.890 đoạn / 210 đoạn xấu = 5,4 %):

| Chỉ số | Giá trị | KTC 95 % |
|---|---|---|
| AUROC **gộp** | **0,965** | [0,857; 0,992] |
| AUPRC gộp | 0,801 | — |
| AUROC **trong bản ghi** (trung bình 11 bản có cả hai lớp) | **0,934** | [0,872; 0,981] |
| AUROC trong bản ghi, trung vị | 0,983 | — |

**[SỰ KIỆN]** Cổng xếp đúng ba bản ghi khó nhất (**B2_03**, **B1_07**, **B1_06**) vào ba hạng cuối trong
22 chủ thể. Nếu xếp ngẫu nhiên, xác suất đúng cả ba hạng là **1/1540**.

> **[SUY LUẬN] Nhưng không được nói "phải có cổng học mới làm được".** Khi thử 24 quy tắc dùng **một**
> đặc trưng duy nhất (12 đặc trưng × 2 chiều dấu), **5/24** quy tắc cũng xếp đúng cả 3/3. Đóng góp của
> cổng học là ở **AUROC và đường cong rủi ro–độ phủ**, không phải ở việc xếp đúng ba bản khó.
> *(Con số 5/24 lấy từ `analysis/GATE22.md` dòng 293–304; chưa truy được về một trường JSON riêng.)*

**Đường cong rủi ro–độ phủ (22 chủ thể):** bỏ B2_03 (còn độ phủ 95,5 % số bản, 98,1 % thời lượng) →
hiệu số RelyFetal − PMF4 thu về −0,87; bỏ thêm B1_07 (90,9 % / 90,4 %) → −0,27; bỏ thêm B1_06
(86,4 % / 82,7 %) → **+0,27** [−0,02; +0,48].

**Phổ lỗi — sáu nhóm, có mức ngẫu nhiên đối chứng:**

| Nhóm lỗi | 22 chủ thể (kênh PSD) | Mức ngẫu nhiên | CinC 75 bản (kênh PSD) | Mức ngẫu nhiên |
|---|---|---|---|---|
| (a) Bỏ nhịp **dù có tín hiệu** | **3,82 %** | 14,66 % | **1,03 %** | 10,26 % |
| (b) Không có tín hiệu để bắt | 8,38 % | 0,93 % | 19,28 % | 6,12 % |
| (c) Bắt nhầm nhịp mẹ | 7,69 % | 7,34 % | 9,08 % | 6,90 % |
| (e) Bắt đúng nhịp nhưng lệch quá dung sai | 68,54 % | 61,28 % | 58,57 % | 61,51 % |
| (d1) Bắt đôi | 3,18 % | 0,11 % | 1,22 % | 0,37 % |
| (d2) Ngẫu nhiên | 8,38 % | 15,69 % | 10,81 % | 14,84 % |
| **Lỗi trên 1.000 nhịp** | **56,2** | — | 397,2 | — |

**Jitter của các nhịp đã bắt đúng:** **3,80 ms** (22 chủ thể, TCN, kênh PSD) và **3,76 ms** (trung vị
67/75 bản CinC, quy tắc `peakprob`) — so với dung sai chấm ±50 ms.

> **[SUY LUẬN]** Nhóm lỗi (a) — "bỏ nhịp dù có tín hiệu", tức lỗi thuộc về mô hình — thấp hơn mức ngẫu
> nhiên khoảng 4 lần ở cả hai tập, và jitter nhỏ hơn dung sai hơn 13 lần. Nhưng **kết luận "mô hình không
> phải nút thắt" ĐÃ RÚT** vì phép thử "nhìn thấy" có âm tính giả 18 %.

*Nguồn: `analysis/gate22_results.json` → `cong`, `rui_ro_do_phu_ban_ghi`; `analysis/chandoan_results.json`
→ `pho_loi`; `analysis/chandoan_m1_jitter.json` → `tong_hop`; `analysis/kientruc_results.json` → `table.tcn.jitter_psd`.*

**Cảnh báo phạm vi:** cột CinC của phổ lỗi và jitter tính trên **75 bản ghi** (bao gồm 15 bản chồng lấn),
**chưa tính lại trên 60 bản sạch**. Tương tự, các số cổng từ chối trên CinC (AUROC 0,980 / độ phủ 66,7 % /
15 trong 16) đo trên 75 bản nhiễm → **không dùng làm số chính**. Việc tính lại nằm ở tuần 2–4 của kế hoạch.

---

## 9. BÀN LUẬN

### 9.1 Bốn đóng góp, kèm ranh giới

| # | Đóng góp | Bằng chứng | **Ranh giới — điều đóng góp này KHÔNG nói** |
|---|---|---|---|
| **C1** | Kiểm toán rò rỉ định lượng cho CinC 2013 set-a: định danh **15 bản**, ánh xạ 5 → 15, đo mức thổi phồng 3,27–7,18 điểm | `benchmark_dpss/eval_cinc60_sach.json`; `analysis/dulieu_results.json` | **Không phải phát hiện rò rỉ.** Ban tổ chức đã ghi nhận từ 2013 (Silva; Clifford 2014). Chỉ kiểm trùng **nguyên văn**; trùng **chủ thể** chưa kiểm |
| **C2** | Tách bạch ba tầng đóng góp trong một thí nghiệm: front-end / ngữ cảnh / kiến trúc, cùng tham số ±2,7 % | `analysis/kientruc_results.json`; `pilot_evidence/band_tcn_stats.json` | Giao thức **thu nhỏ** (3 epoch, 3 fold, **1 hạt giống**). Dải lọc chỉ quan trọng trên kênh PSD, **không** trên trung bình 4 kênh |
| **C3** | Tỉ lệ lấy lại **89,49 %** lợi ích đa kênh bằng một kênh, kèm KTC cụm và jackknife | `analysis/recovery_ratio.json`; `baselines/powermf_fair_stats.json` | Hiệu số so với Power-MF 4 kênh vẫn **âm** (−1,27) và KTC **chạm 0**. Không được đọc là "một kênh tốt hơn bốn kênh" |
| **C4** | Cổng từ chối xuyên hệ ghi, zero-shot, kèm đường cong rủi ro–độ phủ | `analysis/gate22_results.json` | Ý tưởng fSQI đã có từ Andreotti 2017. **5/24 quy tắc một đặc trưng** cũng xếp đúng 3/3 bản khó. Số trên CinC đo trên 75 bản nhiễm |

### 9.2 Năm tuyên bố đã rút, và vì sao

| # | Tuyên bố đã rút | Đo ở đâu | Vì sao sai | Thay bằng gì |
|---|---|---|---|---|
| 1 | Mọi con số CinC trên **75 bản** (71,21 / 79,40 / 86,87 / 85,60 / 62,82 / 22 trên 75…) | `benchmark_dpss/eval_cinc75.json` | 15/75 bản là bản sao nguyên văn của dữ liệu huấn luyện → thổi phồng 3,27–7,18 điểm | **74,28** (psd) trên **60 bản sạch** |
| 2 | *"Nhóm phát hiện rò rỉ dữ liệu"* | — | Sai về quyền ưu tiên: Silva 2013 Bảng 1 và Clifford 2014 đã ghi nhận; cảnh báo nằm ngay trong ghi chú đọc bài của nhóm | *"Như ban tổ chức đã ghi nhận…, chúng tôi xác định bằng đo lường 15 bản nào và mức thổi phồng"* |
| 3 | *"Mô hình không phải nút thắt"* / *"thiếu tín hiệu thật"* | `analysis/chandoan_results.json` | Phép thử "nhìn thấy" có **âm tính giả 18,0 %** [12,1; 25,0] trên chính 60 bản sạch | *"Nguyên nhân của khoảng cách 17,92 điểm chưa xác định được"* |
| 4 | Dải lọc **+11,00 điểm** | Đo trên **GBM cửa sổ 300 ms**, phát biểu như thể về TCN | Lặp lại trên chính TCN cho **+2,44** [−0,04; +6,29] (kênh PSD) và **−0,07** (trung bình 4 kênh) | *"Dải lọc không quan trọng với bộ dò hiện tại"* |
| 5 | *"Tiền đăng ký"* + *"peakprob nâng F1 lên 82,01"* như một kết quả | `analysis/chonkenh_khaibao_truoc.json` | Bản khai báo **không được bên thứ ba neo** và viết **sau** khi đã có F1 từng kênh; `gate` (trọng tài) **trượt** Holm | `gate4` (chỉ định trước, Holm 0,015) là kết quả; `peakprob` là **giả thuyết hậu kiểm** |
| *(bổ sung)* | Power-MF **94,87**; *"loại hai bản bắt cách nhịp còn 98,38 vs 97,33"* | Bản Octave hỏng | Lỗi cổng chuyển của chính nhóm (`findpeaks` tốn O(k²) bộ nhớ), **không phải** vì tham số 340 ms như nhóm đã đoán (0,00 % khoảng RR dưới 340 ms) | Power-MF 4 kênh = **98,83**; tái lập số tác giả đến 0,06 điểm |

### 9.3 Điều học được về phương pháp luận

1. **[SUY LUẬN]** Ba lần nhóm đoán nguyên nhân trước khi đo, cả ba lần đều sai (tham số 340 ms; quy tắc
   kênh 0 cố định; quyền ưu tiên của phát hiện rò rỉ). **Bài học:** đo trước, giải thích sau.
2. **[SUY LUẬN]** Ghi chú đọc bài của chính nhóm đã chứa cảnh báo chồng lấn mà nhóm bỏ sót. **Bài học:**
   phải có một bước rà lại ghi chú đọc bài trước khi thiết kế giao thức đánh giá, không chỉ trước khi viết.
3. **[SUY LUẬN]** Thiết kế trọng tài của nhóm hỏng: bốn quy tắc tốt nhất cách nhau **0,04 điểm** trên
   tập trong miền, nên trọng tài trong miền không phân biệt được gì. **Bài học:** trọng tài phải có
   độ phân giải đủ trước khi khai báo.
4. **[SUY LUẬN]** Một tệp "nguồn sự thật" duy nhất (`survey/facts_phase4.json`) với mục **Z_DA_RUT** liệt
   kê mọi số đã rút là công cụ hiệu quả nhất nhóm có. Thẩm định vòng 8 kiểm 25 con số độc lập, 25/25 khớp.

---

## 10. GIỚI HẠN

| # | Giới hạn | Hệ quả |
|---|---|---|
| **G1** | **22 chủ thể**, một trung tâm, một hệ ghi | Không suy rộng được ra dân số. Công suất thống kê thấp: nếu một hiệu ứng 2 điểm chỉ do 1/7 chủ thể mang, cần **n ≈ 50** (t-test ghép cặp) hoặc **n ≈ 160** (Wilcoxon) để đạt power 0,80 |
| **G2** | **Một hạt giống** cho kết quả chính | Seed 0 = 97,56 vs seed 1 = 97,59 (lệch 0,03; max lệch từng chủ thể 2,81 ở B2_03). Nhưng **không có checkpoint seed 1** → không lặp lại được nhánh `peakprob` trên seed 1 |
| **G3** | `peakprob` là **lựa chọn hậu kiểm** và không có bộ thứ ba | NIFEADB, NInFEA, nifecgdb, CinC set-b đều đã kiểm và **không bộ nào có nhãn fQRS thật**. Kết luận chọn kênh **chưa nhân rộng được** |
| **G4** | **Nhãn B1 gián tiếp**, chiếm **76,9 %** thời lượng tập trong miền | Jitter và STV trên B1 **không dùng được**; 5/10 bản B1 lệch 8–12 ms so với nhãn da đầu |
| **G5** | **Chưa dùng được làm máy đo STV độc lập** | Chệch STV: +0,33 ms (ADFECGDB) / +1,86 (B2) / +1,84 (B1) nhưng **+20,50 ms** trên CinC (mẫu 10 bản, đã rút khỏi số chính). Sai số bám sát F1: F1 ≥ 99,5 → **0,13 ms**; F1 < 90 → **25,74 ms** |
| **G6** | Cổng từ chối trên CinC **chưa tính lại trên 60 bản sạch** | Các số AUROC 0,980 / độ phủ 66,7 % / 15 trong 16 đo trên **75 bản nhiễm** → không dùng làm số chính |
| **G7** | Bảng kiến trúc chạy theo **giao thức thu nhỏ** (3 epoch, 3 fold, 1 seed) | Kết luận tương đương giữa TCN / `rf_wide` / `tcn_ms` chỉ đúng trong ngân sách đó |
| **G8** | Bản thảo CinC dựng trên **template mô phỏng**, không phải `cinc.cls` chính thức | Số trang (4) có thể đổi khi dựng bằng lớp chính thức. Phải dựng lại trước khi nộp |
| **G9** | Phổ lỗi và jitter trên CinC tính trên 75 bản | Chưa tính lại trên 60 sạch (tuần 2 kế hoạch) |
| **G10** | Kiểm trùng dữ liệu chỉ ở mức **nguyên văn** (NCC) | Trùng **chủ thể** (cùng sản phụ, khác đoạn ghi, khác xử lý) chưa kiểm được |
| **G11** | Không có hội nghị hạng A* đúng lĩnh vực | CinC **không phải** A*. Không nên đặt A* vào bảng mục tiêu |

---

## 11. TIẾN ĐỘ

**Cách tính phần trăm:** theo **khối công việc đã khai báo trong kế hoạch 12 giai đoạn** (P0–P11), mỗi
giai đoạn tính trên các hạng mục con cụ thể liệt kê ở cột "bằng chứng". **Không có tệp JSON nào lưu con
số phần trăm** — các số dưới đây là ước lượng theo số hạng mục con hoàn thành, ghi rõ căn cứ để giảng
viên tự kiểm.

| Khối | Nội dung | Trạng thái | % | Bằng chứng (đường dẫn tệp) |
|---|---|---|---|---|
| **P0** | Bổ sung dữ liệu + chống rò rỉ | Một phần | ~70 % | ADFECGDB, Silesia, CinC, NSTDB đã tải; kiểm chồng lấn xong (`analysis/dulieu_results.json`, `benchmark_dpss/eval_cinc60_sach.json`). **Còn:** FECGSYNDB, NInFEA đầy đủ |
| **P1** | Bảng kiến trúc đúng giao thức | Phần lớn | ~70 % | `analysis/kientruc_results.json` (7 họ). **Còn:** 3 hạt giống, giao thức đầy đủ |
| **P2** | Baseline cổ điển + Power-MF | **Xong** | 100 % | `baselines/powermf_fair_stats.json`, `baselines/powermf_1ch.json`, `baselines/BASELINES.md` (48/48 ca kiểm `findpeaks`) |
| **P3** | Huấn luyện lại mô hình chính | **Xong** | 100 % | 22 chủ thể, 11 fold nhóm; `model/checkpoints/` (**20 tệp**). **Còn:** đo riêng đóng góp tăng cường |
| **P4–P6** | fSQI + cổng từ chối | Nguyên mẫu xong | ~80 % | `analysis/gate22_results.json`, `fsqi/`. Kết quả **phủ định** cho đặc trưng topo, **khẳng định** cho cổng cổ điển. **Còn:** tính lại trên 60 sạch |
| **P7** | Tiền huấn luyện FECGSYNDB | **Chưa động tới** | 0 % | Cần ~40 GB. Sau khi thấy **16/60** bản CinC sạch vẫn dưới 50, mục này **trở lại thành ưu tiên** |
| **P8** | Thống kê đầy đủ + đường cong | Phần lớn | ~85 % | `analysis/stats_results.json`, `pilot_evidence/snr_curve.json`, `analysis/xacnhan_results.json`, `benchmark_dpss/eval_cinc60_sach.json` |
| **P9** | Đóng gói: demo, API, Docker | Phần lớn | ~85 % | `demo/app.py` (924 dòng), `demo/core.py` (1 147 dòng), 8 tab, **16 ảnh** `demo/screenshots/`, `api/`, `Dockerfile` (viết, **chưa build**) |
| **P10** | Bản thảo | Bản nháp | ~60 % | `paper/cinc2026/main.tex` → `docs/CinC2027_RelyFetal.pdf` (4 trang, 0 số đã rút, 25/25 số khớp nguồn theo `docs/nhat_ky/THAMDINH_VONG8.md`). **Còn:** dựng bằng `cinc.cls` chính thức |
| **P11** | Nộp | Chưa | 0 % | — |
| *Ngoài kế hoạch* | Bộ chỉ số lâm sàng | **Xong** | — | `analysis/clinical_results.json` — 32 bản ghi / 269,6 phút |
| *Ngoài kế hoạch* | Thích nghi miền | **Xong (kết quả phủ định)** | — | `adapt/adapt_results.json` — cả 4 phương pháp thất bại |
| *Ngoài kế hoạch* | Tám vòng thẩm định đối kháng nội bộ | **Xong** | — | `THAMDINH_VONG6/7/8.md`, `docs/nhat_ky/QA_VONG4.md`, `docs/nhat_ky/DON_REPO_VONG7.md` |

**Kiểm thử:** `pytest tests/ demo/test_core.py` → **82/82 qua** (43 ở `tests/` + 17 ở `demo/test_core.py`).
**Kho mã:** 11 commit, commit hiện tại `c20417b` đã đẩy.

**Năm bản ghi minh hoạ cho demo** (không bản nào nằm trong 15 bản chồng lấn):
r01 (F1 99,92) | a09 (peakprob 94,25 / PSD 19,35 — cho thấy chọn kênh quan trọng) | B2_03 (83,91 (kênh peakprob) — bản
khó nhất) | a02 (24,91, bám nhịp mẹ 78 %) | a27 (32,94, gần như không có tín hiệu thai).

### Ba việc cần làm ngay, trước buổi gặp

| # | Việc | Vì sao |
|---|---|---|
| 1 | **Dựng lại hoặc xoá `docs/De_cuong_NCKH_RelyFetal.docx`** | Tệp DOCX hiện tại là bản v3.4, còn khẳng định **79,40** là số đúng và **không có** phần rút v3.5. Nếu cô mở file Word thay vì PDF, cô đọc đúng phiên bản nhóm đã tự rút |
| 2 | **Sửa 15 chỗ trong đề cương LaTeX** còn phát biểu số 75 bản như sự thật | `sec_4_6.tex:583, 588, 621, 627`; `sec_7_12.tex:135, 260, 292, 311, 403, 417`; `sec_1_3.tex:245` |
| 3 | **Cắt `docs/TOM_TAT_1_TRANG.md`** từ 877 từ xuống ≤ 620 từ | Hiện tràn sang trang 2; đây là tờ giấy duy nhất chắc chắn được đọc |

---

## 12. KẾ HOẠCH 12 TUẦN (14/09 → 06/12/2026)

**Nguyên tắc xếp:** theo tỉ số giá trị / chi phí; việc rẻ mà có thể **lật** kết luận thì làm trước; việc
cần người ngoài (giảng viên, khoa sản) khởi động từ tuần 1 vì thời gian chờ dài.

| Tuần | Việc | Đầu ra | Phụ thuộc | Ai làm |
|---|---|---|---|---|
| **1** (14–20/9) | (a) Sửa DOCX + 15 chỗ đề cương + tóm tắt 1 trang. (b) Commit toàn bộ `analysis/`, `adapt/`, `baselines/`; gắn thẻ. (c) **Gửi thư xin giới thiệu khoa sản** (Từ Dũ / Hùng Vương / BV ĐH Y Dược) để xin ghi bụng có tham chiếu | DOCX mới; đề cương sạch; thư đã gửi | — | Chủ nhiệm; **PHỤ THUỘC VÀO CÔ**: thư giới thiệu |
| **2** (21–27/9) | Tính lại **trên 60 bản sạch**: số cổng từ chối, phổ lỗi (M1), jitter. Sửa mọi số CinC còn lại trong README / `main.tex` | `analysis/chandoan_60sach.json`; README sạch | Tuần 1 | Chủ nhiệm |
| **3** (28/9–4/10) | (a) Nếu có bác sĩ đồng ý: bắt đầu tự chú thích 10–20 bản NIFEADB có chuyên gia kiểm. **Nếu không có bác sĩ trước cuối tuần 3 → bỏ nhánh này**, đích là Physiological Measurement. (b) Đo STV **sau cổng** trên ADFECGDB + 60 sạch | Bộ nạp + bảng thống kê bộ thứ ba; `clinical_gated.json` | Tuần 1(c) | Thành viên 2; **PHỤ THUỘC VÀO CÔ**: giới thiệu bác sĩ |
| **4** (5–11/10) | (a) Chỉ nếu có bộ tự chú thích: chạy **đúng một lần** psd / gate4 / peakprob / oracle, bootstrap, Holm; báo cáo bất kể kết quả. (b) **Quyết định đích công bố** | `analysis/bo_thu_ba_results.json`; ghi chú quyết định | Tuần 3 | Chủ nhiệm; **cô xem kết quả** |
| **5** (12–18/10) | (a) Huấn luyện **2 hạt giống** thêm cho cấu hình chính. (b) Bắt đầu thí nghiệm SNR thấp có kiểm soát | Checkpoint seed 2, 3; `snr_aug_results.json` | GPU; tuần 2 | Chủ nhiệm |
| **6** (19–25/10) | (a) Tổng hợp 3 hạt giống: bảng chính có trung bình ± SD hạt giống. (b) Kết thúc SNR thấp | `main_3seed.json` | Tuần 5 | Chủ nhiệm |
| **7** (26/10–1/11) | (a) Rà văn liệu: liệt kê các bài huấn luyện ADFECGDB rồi kiểm trên set-a, ghi từng bài có / không bị ảnh hưởng. (b) Viết mục kiểm toán rò rỉ và mục tỉ lệ 89,5 % | `survey/anh_huong_ro_ri.md`; bản nháp 2 mục | — | Thành viên 2; **cô góp ý mục kiểm toán** |
| **8** (2–8/11) | (a) Viết các mục còn lại. (b) Bốn hình chính. (c) **Xin một buổi góp ý lâm sàng từ bác sĩ sản**: cổng từ chối có chấp nhận được trong theo dõi không, độ phủ 67 % nghĩa là gì trong thực hành | Bản nháp đầy đủ v1; 4 hình | Tuần 4–7 | Chủ nhiệm; **PHỤ THUỘC VÀO CÔ**: 1 buổi với bác sĩ |
| **9** (9–15/11) | (a) Gói tái lập: Zenodo cho checkpoint + JSON; `reproduce_tables.py` chạy từ JSON ra mọi bảng. (b) **Cô đọc phản biện nội bộ** | DOI Zenodo; phiếu phản biện | Tuần 8 | Thành viên 3; **PHỤ THUỘC VÀO CÔ**: phản biện |
| **10** (16–22/11) | Sửa theo phản biện; viết thư gửi toà soạn nêu thẳng: chồng lấn dữ liệu, lựa chọn hậu kiểm, các số đã rút; **đề xuất 3–4 phản biện** | Bản v2; cover letter | Tuần 9 | Chủ nhiệm; **cô gợi ý tên phản biện** |
| **11** (23–29/11) | (a) Kiểm cuối tự động: mọi số trong bài ↔ JSON. (b) Chuẩn bị bản CinC 2027 4 trang bằng `cinc.cls` chính thức. (c) Chuẩn bị tóm tắt tiếng Việt cho Euréka | Báo cáo kiểm số; `paper/cinc2027/` | Tuần 10 | Chủ nhiệm |
| **12** (30/11–6/12) | **Nộp bài**; đăng bản tiền ấn phẩm cùng ngày nếu toà soạn cho phép | Số nộp; preprint | Tuần 11 | Chủ nhiệm |

**Bốn việc PHỤ THUỘC VÀO CÔ, và cần bắt đầu từ tuần 1:** thư giới thiệu khoa sản (tuần 1); giới thiệu
bác sĩ sản để chú thích và góp ý lâm sàng (tuần 3 và tuần 8); phản biện nội bộ (tuần 9); gợi ý tên phản
biện (tuần 10).

---

## 13. NHỮNG GÌ CẦN HỎI GIẢNG VIÊN

### (a) DỮ LIỆU — nhóm câu hỏi quan trọng nhất

| # | Câu hỏi | Vì sao hỏi | Câu trả lời của cô sẽ đổi cái gì |
|---|---|---|---|
| a1 | Cô có đầu mối nào ở khoa sản (Từ Dũ / Hùng Vương / BV ĐH Y Dược) để xin **ghi điện tim bụng có tham chiếu** không? | Rào cản số một của đề tài **không phải mô hình mà là dữ liệu**: bảng kiến trúc cho thấy nhân bốn lần tham số chỉ được +0,26 điểm | Nếu **có**: mở đường lên tạp chí Q1 (cần bộ thứ ba có nhãn) và lên mức "hai trung tâm". Nếu **không**: đích cố định là *Physiological Measurement*, và nhánh tuần 3–4 bị bỏ |
| a2 | Có bộ dữ liệu nào **có nhãn fQRS thật** mà cô biết, ngoài bốn bộ nhóm đã kiểm? | Nhóm đã kiểm và loại NIFEADB, NInFEA, nifecgdb, CinC set-b — **không bộ nào có nhãn thai thật** | Quyết định `peakprob` có nhân rộng được không. Đây là điều kiện duy nhất để nâng đích lên JBHI |
| a3 | Quy trình **đạo đức nghiên cứu** và chấp thuận sản phụ ở trường như thế nào, mất bao lâu? | Nhóm ước lượng 3–6 tháng nhưng **chưa xác minh**; nếu đúng thì không kịp cho bài này | Nếu < 3 tháng: đưa vào bài này. Nếu ≥ 3 tháng: ghi vào hồ sơ Euréka là "đang tiến hành", không tính vào bài |
| a4 | Sinh viên **có được tự chú thích nhãn fQRS** không, và ai kiểm chứng? | Tự chú thích NIFEADB là con đường rẻ nhất để có bộ thứ ba, nhưng nhãn không có chuyên gia kiểm thì phản biện sẽ bác | Nếu có bác sĩ kiểm: chạy nhánh tuần 3–4. Nếu không: **bỏ hẳn nhánh bộ thứ ba**, viết `peakprob` là giả thuyết và dừng ở đó |

### (b) KIẾN TRÚC / MÔ HÌNH

| # | Câu hỏi | Vì sao hỏi | Câu trả lời của cô sẽ đổi cái gì |
|---|---|---|---|
| b1 | **Có nên đầu tư thêm vào mô hình không?** Bằng chứng của nhóm nói là **không** | Bảy họ kiến trúc cùng tham số ±2,7 %: ba họ đầu **tương đương** theo TOST; họ kém nhất chỉ kém vì trường tiếp nhận 60 ms; trường tiếp nhận **bão hoà ở 1,5 s**; nhân bốn tham số chỉ +0,26 điểm | Nếu cô **đồng ý**: đóng câu hỏi kiến trúc, dồn 12 tuần vào dữ liệu + đánh giá. Nếu cô **muốn thử thêm**: nhóm cần biết tiêu chí dừng, vì hiện chưa có bằng chứng nào nói mô hình là nút thắt |
| b2 | Khi có thêm dữ liệu, có nên thử **mô hình lớn hơn** (Transformer, mô hình nền) không? | Hiện 22 chủ thể; mô hình lớn gần như chắc chắn quá khớp. Nhưng nếu tuần 3 có dữ liệu mới thì tình hình đổi | Quyết định có viết một mục "hướng mở rộng mô hình" trong đề cương hay không, và có xin GPU hay không |
| b3 | Kết quả **âm tính** của cả bốn phương pháp thích nghi miền có đủ để thành một mục trong bài không, hay nên bỏ? | Cả bốn thất bại, ba làm xấu đi có ý nghĩa. Toà soạn *Physiological Measurement* quen với kết quả âm tính; toà soạn khác có thể không | Quyết định độ dài mục 4 của bài và có giữ `adapt/` trong đề cương hay không |

### (c) HỆ THỐNG / TRIỂN KHAI

| # | Câu hỏi | Vì sao hỏi | Câu trả lời của cô sẽ đổi cái gì |
|---|---|---|---|
| c1 | **Hướng thiết bị đeo có thực tế không**, hay nên giữ là tầm nhìn? | Mô hình 113.481 tham số, 0,48 MB, 4,35 ms / cửa sổ 4 s trên CPU — về lý thuyết nhét vừa vi điều khiển. Nhưng nhóm **chưa có nguyên mẫu phần cứng** và chưa đo trên vi điều khiển thật | Quyết định mục "sản phẩm" trong hồ sơ Euréka: hứa thiết bị (rủi ro) hay hứa phần mềm + lộ trình (an toàn) |
| c2 | Cần gì để chuyển từ demo sang **thử nghiệm lâm sàng thăm dò**? | Nhóm không biết quy trình. Hiện có demo Gradio + API REST + Docker (chưa build) | Quyết định có đưa "thử nghiệm lâm sàng" vào kế hoạch 24 tuần hay chuyển sang đề tài tiếp theo |
| c3 | Cổng từ chối bỏ **~18 %** thời lượng để đổi lấy độ tin cậy — trong theo dõi thai, **mức bỏ bao nhiêu là chấp nhận được**? | Đường cong rủi ro–độ phủ cho thấy bỏ 3 bản khó (17,3 % thời lượng) thì hiệu số so với Power-MF đảo dấu. Nhưng đây là câu hỏi **lâm sàng**, nhóm không tự trả lời được | Quyết định điểm vận hành mặc định của cổng trong demo và trong bài. Nếu cô giới thiệu được bác sĩ sản thì câu này để hỏi ở tuần 8 |

### (d) CÔNG BỐ VÀ GIẢI THƯỞNG

| # | Câu hỏi | Vì sao hỏi | Câu trả lời của cô sẽ đổi cái gì |
|---|---|---|---|
| d1 | **Hội đồng trường chấm xếp hạng tạp chí theo Scimago hay WoS-JCR?** | *Physiological Measurement* là **Q2 Scimago 2024** (Physiology 25/73) / **Q3** (Biomedical Eng. 51/89). Đây là toà soạn **đúng nhất** về cộng đồng nhưng **không đạt mốc Q1** theo Scimago | **Câu này đổi cả chiến lược công bố.** Nếu hội đồng dùng Scimago và đòi Q1: phải chuyển đích sang BSPC hoặc CBM (Q1 Scimago) và chấp nhận phản biện đòi so với 5–10 phương pháp học sâu khác. Nếu không đòi Q1: giữ PM |
| d2 | **Hạn nộp nội bộ Euréka của TDTU là khi nào?** | Nhóm **chưa xác minh được** — không tìm thấy trong tài liệu nào; phải hỏi Đoàn trường. Euréka 2026 theo ước lượng của nhóm gần như đã đóng | Nếu hạn nội bộ còn: dồn tuần 11 vào hồ sơ Euréka. Nếu đã đóng: đích là **Euréka 2027**, và tuần 11–12 dồn vào bài tạp chí |
| d3 | Cô có đồng ý hướng **Physiological Measurement + CinC 2027** không? | Đây là đích mặc định nhóm đề xuất. CinC 2027 (Auckland), hạn abstract ước ~4/2027 — **ngày chưa xác nhận trên cinc2027.org**, suy từ thông lệ hằng năm | Nếu cô đồng ý: khoá kế hoạch 12 tuần như mục 12. Nếu cô muốn Q1 trước: phải có dữ liệu mới, tức là quay lại câu a1 |
| d4 | Nhóm **có nên nói thẳng trong hồ sơ rằng không có hội nghị A\* đúng lĩnh vực** không? | Không tồn tại hội nghị hạng A* đúng chủ đề; CinC **không phải** A*. Để một ô A* trong bảng mục tiêu là hứa điều không làm được | Quyết định bảng mục tiêu công bố trong hồ sơ Euréka. **[KHUYẾN NGHỊ]** của nhóm: nói thẳng, bỏ ô A* |
| d5 | Bài báo nên nêu **kiểm toán chồng lấn dữ liệu** ở mức nào — một mục chính, hay một đoạn trong phần dữ liệu? | Đây là phần có giá trị học thuật rõ nhất nhưng cũng là phần dễ bị đọc thành "tố cáo các bài trước". Nhóm đã viết theo hướng trung lập, trích Silva 2013 và Clifford 2014 | Quyết định trục của bài: "kiểm toán + cổng từ chối" (hợp PM) hay "hệ thống một kênh" (hợp BSPC/CBM) |

---

## 14. TÀI LIỆU THAM KHẢO

*Chỉ liệt kê tài liệu **đã xác minh**. Toàn bộ 30 công trình đọc toàn văn ở
`de_cuong_latex/tables/danhmuc.tex`; PDF ở `papers/`; nhật ký tải ở `papers/papers_records.json`.*

1. Jaeger KM, Nissen M, Rahm S, Titzmann A, Fasching PA, Beilner J, Eskofier BM, Leutheuser H.
   Power-MF: robust fetal QRS detection from non-invasive fetal electrocardiogram recordings.
   *Physiological Measurement* 2024;45(5):055009. DOI 10.1088/1361-6579/ad4952.
   Mã nguồn: github.com/mad-lab-fau/fecg-benchmarking.
2. Zhong W, Liao L, Guo X, Wang G. A deep learning approach for fetal QRS complex detection.
   *Physiological Measurement* 2018;39(4):045004. DOI 10.1088/1361-6579/aab297.
3. Clifford GD, Silva I, Behar J, Moody GB. Non-invasive fetal ECG analysis.
   *Physiological Measurement* 2014;35(8):1521–1536. DOI 10.1088/0967-3334/35/8/1521.
4. Silva I, Behar J, Sameni R, Zhu T, Oster J, Clifford GD, Moody GB. Noninvasive fetal ECG:
   the PhysioNet/Computing in Cardiology Challenge 2013. *Computing in Cardiology* 2013;40:149–152.
   ISSN 2325-8861. **Chưa xác minh DOI** (Crossref không có bản ghi).
5. Andreotti F, Behar J, Zaunseder S, Oster J, Clifford GD. An open-source framework for
   stress-testing non-invasive foetal ECG extraction algorithms.
   *Physiological Measurement* 2016;37(5):627–648. DOI 10.1088/0967-3334/37/5/627.
6. Andreotti F, Zaunseder S, Malberg H, et al. Robust fetal ECG quality assessment.
   *IEEE Transactions on Biomedical Engineering* 2017. DOI 10.1109/TBME.2017.2675543.
7. Fotiadou E, van Sloun RJG, van Laar JOEH, Vullings R. A dilated inception CNN-LSTM network for
   fetal heart rate estimation. *Physiological Measurement* 2021;42(4):045007. DOI 10.1088/1361-6579/abf7db.
8. Zahid MU, Kiranyaz S, Ince T, et al. Robust R-peak detection in low-quality Holter ECGs using
   1D convolutional neural network. *IEEE Transactions on Biomedical Engineering* 2022;69(1):119–128.
   DOI 10.1109/TBME.2021.3088218 (arXiv:2101.01666).
9. Huang et al. TCGAN: Temporal Convolutional GAN for fetal ECG extraction using single-channel
   abdominal ECG. *IEEE Journal of Biomedical and Health Informatics* 2025. DOI 10.1109/JBHI.2024.3524085.
10. Matonia A, Jezewski J, Kupka T, Jezewski M, Horoba K, Wrobel J, Czabanski R, Kahankova R.
    Fetal electrocardiograms, direct and abdominal with reference heartbeat annotations.
    *Scientific Data* 2020;7:200. DOI 10.1038/s41597-020-0538-z.
11. Baldazzi G, Pani D. Open data: valuable resources and opportunities for the researchers in fetal
    cardiac monitoring. In: *Innovative Technologies and Signal Processing in Perinatal Medicine*,
    Springer, 2023. DOI 10.1007/978-3-031-32625-7_12.
12. Shokouhmand A, Tavassolian N. Fetal electrocardiogram extraction using dual-path source separation
    of single-channel non-invasive abdominal recordings. *IEEE Transactions on Biomedical Engineering*
    2023;70(1):283–295. DOI 10.1109/TBME.2022.3189617.
13. Niknazar M, Rivet B, Jutten C. Fetal ECG extraction by extended state Kalman filtering based on
    single-channel recordings. *IEEE Transactions on Biomedical Engineering* 2013;60(5):1345–1352.
    DOI 10.1109/TBME.2012.2234456.
14. Castillo E, Morales DP, García A, Parrilla L, Ruiz VU, Álvarez-Bermejo JA. A clustering-based
    method for single-channel fetal heart rate monitoring. *PLoS ONE* 2018;13(6):e0199308.
    DOI 10.1371/journal.pone.0199308.
15. Sulas E, Urru M, Tumbarello R, Raffo L, Pani D. Systematic analysis of single- and multi-reference
    adaptive filters for non-invasive fetal electrocardiography.
    *Mathematical Biosciences and Engineering* 2020;17(1):286–308. DOI 10.3934/mbe.2020016.

---

## 15. PHỤ LỤC

### 15.1 Cấu trúc kho mã

```
D:/NCKHSV2026-2027/
├── model/           FetalQRSTCN, huấn luyện, tải dữ liệu
│   ├── fqrs_model.py           mô hình 113.481 tham số
│   ├── checkpoints/            20 tệp .pt
│   └── data/                   adfecgdb, silesia, nifeadb, ninfea, nstdb
├── benchmark_dpss/  Đánh giá CinC 2013
│   ├── pcdb/                   75 bản .dat/.hea/.fqrs
│   └── eval_cinc60_sach.json   KẾT QUẢ CHÍNH ngoài miền
├── baselines/       Power-MF (Octave 4 kênh + Python 1 kênh) và baseline cổ điển
├── analysis/        Toàn bộ phân tích: dữ liệu, chọn kênh, kiến trúc, chẩn đoán, lâm sàng, cổng
├── adapt/           Bốn phương pháp thích nghi miền (kết quả phủ định)
├── pilot_evidence/  Khảo sát dải lọc, đường cong SNR
├── fsqi/            12 chỉ số chất lượng + cổng từ chối
├── survey/          facts_phase4.json (NGUỒN SỰ THẬT), rà văn liệu chồng lấn
├── demo/            Gradio 8 tab + 16 ảnh chụp + test
├── api/             FastAPI
├── paper/cinc2026/  Bản thảo hội nghị 4 trang
├── de_cuong_latex/  Đề cương đầy đủ 148 trang
├── docs/            Tài liệu cho người đọc (gồm tệp này)
└── tests/           43 kiểm thử
```

### 15.2 Cách chạy lại từng thí nghiệm

| Kết quả | Lệnh |
|---|---|
| Toàn bộ kiểm thử | `pytest tests/ demo/test_core.py` |
| Demo | `python demo/app.py` → mở trình duyệt |
| Kiểm nhanh 5 bản minh hoạ | `python demo/run_check.py` (~0,7 phút) |
| Tải lại dữ liệu ADFECGDB | `python model/download_data.py --root model/data --only adfecgdb` |
| Đánh giá CinC 60 bản sạch | Xem `benchmark_dpss/` (kết quả đã lưu ở `eval_cinc60_sach.json`) |
| Bảng kiến trúc | Xem `analysis/` (kết quả đã lưu, ~81 phút chạy lại) |

### 15.3 Danh sách tệp JSON nguồn sự thật

| Tệp | Nội dung |
|---|---|
| **`survey/facts_phase4.json`** | **NGUỒN SỰ THẬT DUY NHẤT.** Mục `Z_DA_RUT` liệt kê mọi số đã rút — không được trích như sự kiện |
| `benchmark_dpss/eval_cinc60_sach.json` | Kết quả chính ngoài miền: 60 bản CinC sạch |
| `analysis/dulieu_results.json` | Bảy quy tắc chọn kênh trên 60 bản sạch; bảng chồng lấn |
| `baselines/powermf_fair_stats.json` | So sánh 22 chủ thể: RelyFetal vs Power-MF 4 kênh / 1 kênh |
| `analysis/recovery_ratio.json` | Tỉ lệ lấy lại 89,49 % + KTC + jackknife |
| `analysis/kientruc_results.json` | Bảy họ kiến trúc, TOST, Holm |
| `adapt/adapt_results.json` | Bốn phương pháp thích nghi miền + mô phỏng dịch chuyển |
| `analysis/gate22_results.json` | Cổng từ chối: AUROC, rủi ro–độ phủ, chỉ số lâm sàng |
| `analysis/chandoan_results.json` | Phổ lỗi 6 nhóm có mức ngẫu nhiên |
| `analysis/chandoan_m1_jitter.json` | Jitter theo quy tắc chọn kênh |
| `analysis/clinical_results.json` | STV, nhịp tim thai, độ phủ trên 32 bản ghi |
| `analysis/xacnhan_results.json` | Xác nhận vòng 7: bộ thứ ba, logit, phép thử nhìn thấy, hạt giống |
| `pilot_evidence/band_tcn_stats.json` | Dải lọc đo trên chính TCN |
| `survey/ro_ri_vanlieu.json` | Rà văn liệu về chồng lấn: trích dẫn nguyên văn Silva 2013, Clifford 2014 |
| `analysis/chonkenh_khaibao_truoc.json` | Bản khai báo trước cho bảy quy tắc (không được bên thứ ba neo) |

### 15.4 Hai chênh lệch nhỏ giữa tài liệu và JSON gốc, đã ghi nhận

1. `docs/CHIEN_LUOC_CONG_BO.md` ghi mức ngẫu nhiên của nhóm lỗi (a) là **15,2 % / 11,2 %**.
   JSON gốc (`analysis/chandoan_results.json`, hàng **kênh PSD**) cho **14,66 % / 10,26 %**;
   hàng **kênh oracle** cho 15,42 % / 11,12 %. Bảng 5 của tài liệu này dùng hàng kênh PSD
   để khớp với cặp 3,82 % / 1,03 %.
2. `docs/EUREKA.md` ghi sai số STV khi F1 < 90 là **25,78 ms**; tính lại trực tiếp từ
   `analysis/clinical_results.json` (n = 9, hiệu tuyệt đối trên cặp epoch) cho **25,74 ms**.

---

*Tài liệu này do chủ nhiệm đề tài Ngô Bình Minh soạn ngày 13/09/2026 trên commit `c20417b`.
Mọi con số truy nguyên về một tệp JSON trên đĩa. Những chỗ chưa truy được nguồn đã ghi rõ
"chưa có trong nguồn".*
