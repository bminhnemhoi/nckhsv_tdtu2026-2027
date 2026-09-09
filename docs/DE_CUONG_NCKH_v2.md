# ĐỀ CƯƠNG NGHIÊN CỨU KHOA HỌC SINH VIÊN

## Dò phức bộ QRS thai nhi từ điện tim ổ bụng đơn kênh có nhận biết độ tin cậy: benchmark biểu diễn tín hiệu không rò rỉ và chỉ số chất lượng dựa trên đồng điều bền vững

**English title.** *Reliability-aware single-channel fetal QRS detection: a leakage-free representation benchmark and a persistent-homology signal-quality index*

| | |
|---|---|
| **Tên hệ thống** | **RelyFetal** |
| **Đơn vị** | Khoa Khoa học Máy tính, Trường Đại học Tôn Đức Thắng |
| **Nhóm thực hiện** | 3 sinh viên |
| **Thời lượng** | 24 tuần |
| **Phiên bản** | 2.0 — 09/09/2026 (thay thế bản v1.0 ngày 07/09/2026) |
| **Mục tiêu công bố** | 01 bài tạp chí Q1 (*Physiological Measurement* / *Biomedical Signal Processing and Control* / *IEEE JBHI*) + 01 bài hội nghị (*Computing in Cardiology*) + báo cáo Euréka |

> **Ghi chú về phiên bản.** Bản v1.0 đề xuất *TopoFetal-Net*: dùng Persistence Image làm biểu diễn chính cho bộ dò fQRS. Trước khi viết bản này, nhóm đã chạy một loạt thí nghiệm tiền khả thi để kiểm chứng giả thuyết đó. Kết quả **bác bỏ** giả thuyết trung tâm nhưng đồng thời **phát hiện một hướng mạnh hơn**. Bản v2.0 phản ánh trung thực toàn bộ bằng chứng đó. Chi tiết ở §3 và Phụ lục A.

---

## 1. TÓM TẮT

Theo dõi tim thai không xâm lấn từ **một** điện cực ổ bụng là cấu hình rẻ và dễ đeo nhất cho giám sát tại nhà, nhưng khó nhất về xử lý tín hiệu. Hai mươi năm nghiên cứu đã tạo ra nhiều phương pháp với F1 công bố trải từ 78% đến 99,7%, nhưng **không so sánh trực tiếp được** vì giao thức đánh giá khác nhau về tách chủ thể, dung sai ghép cặp và cách chọn kênh.

Nhóm đã chạy thí nghiệm tiền khả thi trên PhysioNet ADFECGDB và phát hiện ba điều định hình toàn bộ đề cương này:

1. **Rào cản thật không phải độ chính xác trung bình mà là độ tin cậy.** Một bộ dò do nhóm xây đạt macro F1 **97,43%** trên ADFECGDB (leave-one-record-out) nhưng chỉ **77,52%** khi chuyển sang PhysioNet/CinC 2013 mà không tinh chỉnh. Quan trọng hơn con số trung bình: phân bố **lưỡng cực** — bốn trên mười bản ghi đạt F1 **tuyệt đối 100%**, ba bản khác sụp xuống 24–49%. Hệ thống **không biết khi nào nó sai**.
2. **Tiền xử lý quan trọng hơn kiến trúc rất nhiều.** Chỉ đổi dải thông từ 1–45 Hz sang 10–60 Hz nâng F1 thêm **11,0 điểm**; toàn bộ khác biệt giữa 16 kiến trúc học sâu chỉ đóng góp **0,4 điểm và không có ý nghĩa thống kê** (p = 0,70).
3. **Biểu diễn topo không phù hợp cho dò đỉnh, nhưng có thể phù hợp cho đánh giá chất lượng.** Persistence Image + CNN 2D đứng **cuối cùng trong 16 kiến trúc** (F1 27,4% so với 97,1% của CNN 1D cùng số tham số). Nhưng nhiệm vụ ECG **duy nhất** mà đồng điều bền vững có kết quả xuất sắc đã công bố lại chính là **đánh giá chất lượng tín hiệu** (Ren et al., *Front. Neurosci.* 2023, mAcc 98,55%).

Từ ba quan sát đó, đề tài đề xuất **RelyFetal**: một bộ dò fQRS đơn kênh **kèm chỉ số chất lượng tín hiệu thai (fSQI) dựa trên đồng điều bền vững**, cho phép hệ thống **từ chối trả lời** khi tín hiệu không đủ tin cậy. Kèm theo là **benchmark không rò rỉ đầu tiên** so sánh năm họ biểu diễn tín hiệu dưới cùng một giao thức trên ba bộ dữ liệu.

---

## 2. ĐẶT VẤN ĐỀ

### 2.1 Bối cảnh lâm sàng

Nhịp tim thai và hình thái QRS thai là cửa sổ chính để phát hiện suy thai, thiếu oxy và bất thường tim bẩm sinh. Hai phương pháp lâm sàng hiện hành đều hạn chế:

- **CTG/Doppler**: chỉ cho nhịp, không cho hình thái, cần kỹ thuật viên, không dùng liên tục tại nhà.
- **Điện cực da đầu thai**: chuẩn vàng nhưng xâm lấn, chỉ dùng được khi đã chuyển dạ và vỡ ối.

Điện tim thai không xâm lấn từ điện cực ổ bụng (aECG) cho phép theo dõi liên tục, tại nhà, chi phí thấp. Cấu hình **đơn kênh** là rẻ nhất và dễ đeo nhất, nhưng loại bỏ khả năng dùng tách nguồn mù đa kênh (ICA, PCA, πCA) vốn đạt độ chính xác cao nhất trong benchmark tổng hợp (Andreotti et al. 2016: BSS 99,9% so với template subtraction 96,0%).

### 2.2 Vì sao đơn kênh khó

| Thách thức | Hệ quả định lượng |
|---|---|
| Biên độ fECG nhỏ hơn mECG nhiều lần | Đo được trên ADFECGDB: tỉ số RMS fQRS/nền chỉ **1,24** ở dải 1–45 Hz |
| Trùng phổ tần số 0,5–40 Hz | Lọc tuyến tính không tách được nếu không làm méo sóng thai |
| Trùng pha mẹ–thai | Đo được: **17–19%** nhịp thai nằm trong ±60 ms của một nhịp mẹ |
| Không có đa dạng không gian | Không dùng được BSS đa kênh |
| Chất lượng kênh biến thiên cực lớn | Đo được: F1 theo từng kênh dao động từ **53,4% đến 98,1%** trên cùng bộ dữ liệu |
| Dữ liệu có nhãn rất ít | ADFECGDB chỉ 5 sản phụ; dễ rò rỉ nếu chia ngẫu nhiên |

### 2.3 Ba khoảng trống trong y văn

Nhóm đã tải và đọc **toàn văn 29 công trình** (27 file PDF, xem Phụ lục B). Ba khoảng trống được xác nhận:

**G1 — Không có so sánh công bằng giữa các biểu diễn tín hiệu.**
Mỗi bài dùng một biểu diễn (tín hiệu thô, ma trận trễ, phổ đồ, đặc trưng topo) trên dữ liệu riêng với giao thức riêng. Chưa ai giữ cố định bộ phân loại, dữ liệu, giao thức và ngân sách huấn luyện để so các biểu diễn. Hệ quả: cộng đồng không biết cải tiến đến từ biểu diễn hay từ tiền xử lý.

**G2 — Không có đánh giá độ tin cậy ở mức bản ghi.**
Mọi bài báo cáo một con số F1 trung bình. Không bài nào trả lời câu hỏi lâm sàng thật: *"với bản ghi cụ thể này, đầu ra có đáng tin không?"* Đo đạc của nhóm cho thấy phân bố hiệu năng là **lưỡng cực**, nên trung bình che giấu chính thông tin quan trọng nhất.

**G3 — Chưa có công trình nào áp dụng đồng điều bền vững cho tín hiệu thai.**
Truy vấn có cấu trúc trên Europe PMC REST, Semantic Scholar, OpenAlex và arXiv API với tổ hợp `("persistent homology" OR "topological data analysis" OR "persistence image") AND (fetal OR foetal OR "abdominal ECG" OR cardiotocography)` không trả về bài fECG nào. Tìm bổ sung bằng tiếng Trung, tiếng Việt và tiếng Tây Ban Nha cũng không. Kết quả gần nhất là HRV nhi khoa (Domínguez-Monterroza et al., *PLoS One* 2025), mà chính tác giả nêu *"mở rộng khung này sang fetal HRV"* là hướng tương lai.

### 2.4 Câu hỏi nghiên cứu

| Mã | Câu hỏi | Thí nghiệm trả lời |
|---|---|---|
| **RQ1** | Dưới một giao thức không rò rỉ, biểu diễn tín hiệu nào cho hiệu năng dò fQRS đơn kênh tốt nhất khi giữ cố định bộ phân loại và ngân sách huấn luyện? | E1 (benchmark) |
| **RQ2** | Trong toàn bộ pipeline, yếu tố nào đóng góp nhiều nhất vào hiệu năng: tiền xử lý, biểu diễn, kiến trúc, hay hậu xử lý? | E2 (phân rã đóng góp) |
| **RQ3** | Chỉ số chất lượng dựa trên đồng điều bền vững có dự báo được khi nào bộ dò sẽ sai, và có tốt hơn SQI cổ điển (SampEn, bSQI, kurtosis, entropy phổ) không? | E3 (fSQI) |
| **RQ4** | Cơ chế từ chối trả lời dựa trên fSQI nâng độ tin cậy hệ thống lên bao nhiêu, đánh đổi bằng bao nhiêu phần trăm dữ liệu bị loại? | E4 (selective prediction) |
| **RQ5** | Hiệu năng suy giảm thế nào khi chuyển miền (thiết bị, trung tâm, giai đoạn thai kỳ) và khi SNR giảm? | E5, E6 |
| **RQ6** | Tiền huấn luyện trên dữ liệu tổng hợp rồi tinh chỉnh trên dữ liệu thật có cải thiện tổng quát hoá không? | E7 (fine-tuning) |

### 2.5 Giả thuyết có thể kiểm định

| Mã | Giả thuyết | Tiêu chí chấp nhận |
|---|---|---|
| **H1** | Bộ dò RelyFetal đạt F1 ≥ 95% trên ADFECGDB dưới LORO | Kiểm định so với baseline TS-PCA bằng Wilcoxon, p < 0,05 |
| **H2** | Tiền xử lý đóng góp nhiều hơn kiến trúc ít nhất 5 lần về điểm F1 | So sánh hai hiệu ứng chính, có khoảng tin cậy bootstrap |
| **H3** | fSQI topo có tương quan Spearman \|ρ\| ≥ 0,6 với F1 thực theo bản ghi, và ≥ SampEn | Bootstrap CI cho hiệu số ρ |
| **H4** | Từ chối 20% dữ liệu có fSQI thấp nhất nâng F1 trên phần còn lại thêm ≥ 8 điểm | Đường cong coverage–accuracy, so với từ chối ngẫu nhiên |
| **H5** | Tiền huấn luyện FECGSYNDB nâng F1 xuyên bộ dữ liệu thêm ≥ 5 điểm | Wilcoxon ghép cặp theo bản ghi |
| **H6** | *(Giả thuyết mở, không định hướng)* Các biểu diễn suy giảm khác nhau khi SNR giảm | Kiểm định tương tác trên đường cong F1–SNR |
| **H0** | **Giả thuyết phủ định vẫn có giá trị**: nếu H3–H5 không đạt, benchmark + phân rã đóng góp + kết quả phủ định có kiểm định vẫn là một bài báo hoàn chỉnh | — |

---

## 3. KẾT QUẢ TIỀN KHẢ THI ĐÃ CÓ

Đây là phần làm đề cương này khác với một bản kế hoạch thuần lý thuyết. Mọi con số dưới đây do nhóm tự đo, mã và log kèm theo, chạy lại được.

### 3.1 Thiết lập thí nghiệm tiền khả thi

Dữ liệu: PhysioNet ADFECGDB, 5 sản phụ × 4 kênh bụng, 1 kHz, nhãn fQRS từ điện cực da đầu đã được bác sĩ tim mạch duyệt. Giao thức: leave-one-record-out, ngưỡng quyết định chọn trên **một bản ghi validation riêng**, chấm điểm ở mức sự kiện với dung sai **±50 ms** theo quy ước CinC 2013. Tổng khối lượng: trên 600.000 cửa sổ, khoảng 6 giờ tính toán CPU.

### 3.2 Bốn kết quả chính

**(a) Phân rã đóng góp — tiền xử lý áp đảo kiến trúc**

| Cấu hình | Macro F1 | Đóng góp |
|---|---|---|
| Gradient boosting trên cửa sổ dư, dải 1–45 Hz | 80,06 | điểm xuất phát |
| + đổi dải thông sang **10–60 Hz** | 92,49 | **+12,43** |
| + CNN 1D dilated, 25.953 tham số | 92,90 | +0,41 (**p = 0,70**) |
| + ngữ cảnh 4 giây, TCN dilated, đầu ra theo từng mẫu | **97,43** | **+4,53** (**p < 0,0001**) |

Quét 8 dải thông (mỗi dải một lần chạy LORO đầy đủ): 10–60 Hz **91,06** > 8–45 **89,63** > 15–60 **89,01** > 3–90 **84,17** > 3–100 **83,80** > 1–45 **80,06** > 20–95 **77,39** > 0,5–100 **72,17**. Ba nguồn y văn độc lập đọc từ toàn văn ủng hộ hướng này: Behar et al. 2014 grid-search ra 20–95 Hz; Clifford et al. 2014 ghi nhận cắt thông cao ở 10 Hz cải thiện kết quả do loại bỏ sóng P và T của mẹ; Xu et al. 2026 dùng 10–60 Hz.

**(b) So sánh 16 kiến trúc, cùng dữ liệu và cùng ngân sách**

Xếp hạng (F1 trên bản ghi validation, cửa sổ 300 ms): `resnet1d` 98,96 > `tcn` 98,88 > `transformer` 98,81 > `cnn_l` 98,77 > **`cnn_dil` 98,56 (25.953 tham số — hiệu quả nhất)** > `cnn_gru` 98,25 > `unet1d` 98,01 > … > `cnn2d_delay` (ma trận trễ kiểu SCTD-Net) 93,08 > `linear` 48,55 > **`cnn2d_pi` (Persistence Image + CNN 2D) 27,42**.

Hai thí nghiệm có kiểm soát chặt:
- Dilation 1/2/4 so với 1/1/1 ở **cùng số tham số**: **+1,42 điểm**, jitter giảm từ 13,2 xuống 6,0 ms.
- Kiến trúc hai luồng (1D + PI) so với nhánh 1D đơn thuần: **+0,10 điểm**, gấp đôi tham số.

**(c) Receptive field là biến kiến trúc quan trọng nhất**

Cùng kiến trúc TCN, chỉ khác lịch dilation:

| Receptive field | F1 |
|---|---|
| 172 ms | 98,73 |
| 748 ms | 99,25 |
| **1.516 ms** | **99,50** |
| 3.052 ms | 99,52 (bão hoà) |

Dưới LORO đầy đủ 3 seed: RF 1.516 ms cho **97,16 ± 4,34** so với RF 172 ms cho **92,67 ± 10,46**, chênh **4,66 điểm, p = 0,0000**. Đầu ra theo từng mẫu cũng giảm jitter từ 6 ms xuống **1 ms**.

**(d) Phát hiện quyết định — thất bại lưỡng cực khi chuyển miền**

Mô hình huấn luyện **chỉ trên ADFECGDB**, chạy trên PhysioNet/CinC 2013 set-a (thiết bị khác, trung tâm khác), không tinh chỉnh:

| Bản ghi | F1 | | Bản ghi | F1 |
|---|---|---|---|---|
| a03 | **100,00** | | a07 | 84,82 |
| a04 | **100,00** | | a09 | 79,84 |
| a05 | **100,00** | | a10 | **48,98** |
| a08 | **100,00** | | a06 | **42,75** |
| a01 | 94,29 | | a02 | **24,48** |

Macro F1 **77,52 ± 26,83**. Bốn bản ghi hoàn hảo, ba bản thất bại nặng. **Đây là bằng chứng thực nghiệm cho toàn bộ hướng nghiên cứu của đề cương này**: vấn đề không phải mô hình chưa đủ tốt, mà là hệ thống không biết khi nào nó sai.

### 3.3 Trả lời các câu hỏi thường gặp về phần tiền khả thi

| Câu hỏi | Trả lời |
|---|---|
| **Dùng mô hình nào?** | `FetalQRS-TCN` — dilated temporal convolutional network, chuỗi-sang-chuỗi, **113.481 tham số**, do nhóm tự thiết kế dựa trên hai nguồn bằng chứng: ablation đã công bố (đọc từ toàn văn) và thí nghiệm so sánh 16 kiến trúc do nhóm chạy |
| **Đã huấn luyện chưa?** | Rồi. **6 checkpoint**: 5 mô hình leave-one-record-out kèm ngưỡng và metric trên bản ghi chưa từng thấy, cộng 1 mô hình production |
| **Dữ liệu ở đâu?** | Tải trực tiếp từ PhysioNet bằng `download_data.py` của nhóm. ADFECGDB (DOI 10.13026/C2RP4B) và CinC 2013 (challenge-2013/1.0.0). Có `data_card.json` ghi mã băm SHA-256 từng file. **Không phụ thuộc mã nguồn hay dữ liệu của bất kỳ bên thứ ba nào** |
| **Huấn luyện thế nào?** | Đoạn 4 giây @250 Hz, nhãn heatmap Gaussian σ = 12 ms theo từng mẫu, BCEWithLogits có pos_weight, AdamW lr 3e-3, OneCycle, 6 epoch, batch 32, gradient clipping 1.0. Ngưỡng quyết định chọn trên bản ghi validation nội bộ của từng fold |
| **Có fine-tuning không?** | **Chưa — và đây là một trong bảy thí nghiệm chính của đề cương** (E7). Kế hoạch: tiền huấn luyện trên FECGSYNDB tổng hợp rồi tinh chỉnh trên dữ liệu thật, giả thuyết H5 |
| **Đã so với SOTA chưa?** | Đã so với **số liệu công bố** (bảng §3.4), chưa cài lại các phương pháp đó. **Cài lại 4 baseline là hạng mục E1 của đề cương** |
| **Nó có hiệu quả không?** | Trong miền: **có** (97,43% LORO, vượt template subtraction cổ điển 89,3%). Xuyên miền: **có điều kiện** (77,52%, với phân bố lưỡng cực). Chính khoảng cách này là đối tượng nghiên cứu của đề tài |

### 3.4 Đối chiếu với y văn — trung thực về khả năng so sánh

| Phương pháp | F1 công bố trên ADFECGDB | Giao thức | So trực tiếp được? |
|---|---|---|---|
| Attention CycleGAN (Mohebbian, IEEE JBHI 2022) | 99,7% | Không nêu tách chủ thể | **Không** |
| Attention R2W-Net (Chen, Sensors 2025) | 99,17% | Dung sai **31,25 ms**, có tinh chỉnh trên tập đích | **Không** |
| SCTD-ICA (Asadi & Ghaffari, IEEE JBHI 2026) | 96,14% | Không nêu tách chủ thể | Một phần |
| 1D-CycleGAN (Basak, ESWA 2024) | 96,4% | Không nêu tách chủ thể | **Không** |
| CNN-2×EEMD (Xu, Sensors 2026) | 83,7–95,7% | **LOSO** | **Có** |
| Echo state network (Behar, ABME 2014) | 90,2% | 9 sản phụ, đơn kênh | **Có** |
| Template subtraction (Behar, ABME 2014) | 89,3% | như trên | **Có** |
| Zhong et al. (Physiol Meas 2018) | 77,85% | Chia theo bản ghi | **Có** |
| **Tiền khả thi của nhóm** | **97,43%** | **LORO, 3 seed, 4 kênh riêng, ngưỡng trên validation** | — |

**Phát biểu đúng đắn cho bài báo:** trong nhóm phương pháp có giao thức không rò rỉ đã kiểm chứng được (Zhong 2018, Behar 2014, Xu 2026), kết quả của nhóm nằm ở mức cao nhất. **Không được** tuyên bố vượt các bài F1 > 99% vì giao thức của họ không so được. Đây chính là lý do tồn tại của đóng góp C1 (benchmark).

---

## 4. ĐÓNG GÓP KHOA HỌC

### C1 — Benchmark biểu diễn tín hiệu không rò rỉ đầu tiên cho fQRS đơn kênh

So sánh **năm họ biểu diễn** dưới **một** giao thức, trên **ba** bộ dữ liệu, với cùng bộ phân loại, cùng ngân sách tham số, cùng số epoch, 3 seed, kiểm định ghép cặp có hiệu chỉnh Holm:

1. Tín hiệu dư thô sau khử mẹ
2. Ma trận trễ thời gian 2D (kiểu SCTD-Net)
3. Scalogram wavelet liên tục
4. Persistence Image từ lọc Vietoris–Rips và sublevel-set
5. Đặc trưng persistence diagram thủ công

Kèm **bốn baseline cổ điển được cài lại** (template subtraction, TS-PCA, phân cụm cực trị theo Castillo 2018, EEMD) để bảng so sánh là công bằng chứ không phải trích số từ bài khác.

*Tiền lệ Q1*: Andreotti et al., *Physiol. Meas.* 37(5):627, 2016 là một bài benchmark tương tự và là công trình được trích dẫn nhiều nhất trong lĩnh vực.

### C2 — Phân rã định lượng đóng góp của từng khối trong pipeline

Trả lời câu hỏi mà chưa bài nào trả lời: trong pipeline fECG đơn kênh, **tiền xử lý, biểu diễn, kiến trúc và hậu xử lý mỗi thứ đóng góp bao nhiêu**. Kết quả tiền khả thi cho thấy tiền xử lý đóng góp gấp **30 lần** kiến trúc. Nếu kết quả này đứng vững trên ba bộ dữ liệu, nó thay đổi cách cộng đồng phân bổ nỗ lực nghiên cứu.

### C3 — Chỉ số chất lượng tín hiệu thai dựa trên đồng điều bền vững, và dò fQRS có cơ chế từ chối

**Đóng góp phương pháp luận chính.** Một chỉ số fSQI ∈ [0,1] tính từ đặc trưng topo của tín hiệu dư, dùng để:

- **Từ chối trả lời** trên đoạn hoặc bản ghi không đáng tin (selective prediction, reject option).
- **Chọn/gán trọng số kênh** khi có nhiều điện cực.
- **Gắn khoảng tin cậy** cho ước lượng fHR.

Ba cơ sở:
1. **Thực nghiệm** — thất bại lưỡng cực đo được ở §3.2(d) cho thấy đây là vấn đề thật.
2. **Y văn** — nhiệm vụ ECG duy nhất mà PH có kết quả xuất sắc công bố là đánh giá chất lượng (Ren et al. 2023, mAcc 98,55% đơn đạo trình, đúng pipeline PH → ảnh → CNN).
3. **Lý thuyết** — Turkeš, Montúfar & Otter (NeurIPS 2022) chỉ ra PH mạnh khi nhãn mang bản chất **hình học toàn cục** (chất lượng tín hiệu là "quỹ đạo còn sạch không") chứ không phải khi nhãn là **vị trí sự kiện cục bộ** (đỉnh QRS ở đâu). Điều này giải thích chính xác vì sao PH thất bại ở nhiệm vụ dò và có thể thành công ở nhiệm vụ chất lượng.

**Đây là ứng dụng đầu tiên của đồng điều bền vững cho tín hiệu tim thai** (khoảng trống G3).

### C4 — Bộ mã nguồn mở, tái lập được, chuẩn hoá cho cộng đồng

Fold cố định, data card có mã băm, `reproduce.sh`, CI, kết quả thô theo từng bản ghi để người khác vẽ lại hình. Giấy phép MIT.

---

## 5. PHƯƠNG PHÁP

### 5.1 Kiến trúc hệ thống

```
                      ┌─────────────────────────────────────────┐
   aECG đơn kênh ────►│ KHỐI 1 — TIỀN XỬ LÝ                     │
   (1 kHz / 500 Hz)   │ Butterworth 10–60 Hz zero-phase         │
                      │ notch 50 Hz · resample_poly → 250 Hz    │
                      │ chuẩn hoá robust theo đoạn 10 s         │
                      └──────────────────┬──────────────────────┘
                                         ▼
                      ┌─────────────────────────────────────────┐
                      │ KHỐI 2 — KHỬ mECG                       │
                      │ dò mQRS → TS-PCA (3–5 thành phần)       │
                      │ → tín hiệu dư r[n]                      │
                      └────────┬───────────────────────┬────────┘
                               ▼                       ▼
     ┌──────────────────────────────────┐  ┌──────────────────────────────────┐
     │ KHỐI 3A — BỘ DÒ                  │  │ KHỐI 3B — fSQI (đóng góp C3)     │
     │ đoạn 4 s, 2 × 1000 @250 Hz       │  │ đoạn 5 s của r                   │
     │ TCN dilated 1,2,4,8,16           │  │ Takens → VR H0/H1 + sublevel-set │
     │ RF 1.516 ms                      │  │ → đặc trưng PD / Persistence Img │
     │ → logit theo từng mẫu            │  │ → MLP nhỏ → fSQI ∈ [0,1]         │
     └──────────────┬───────────────────┘  └──────────────┬───────────────────┘
                    ▼                                     ▼
     ┌──────────────────────────────────────────────────────────────────────┐
     │ KHỐI 4 — HỢP NHẤT VÀ TỪ CHỐI                                         │
     │ find_peaks(≥250 ms, ngưỡng θ trên validation)                        │
     │ nếu fSQI < τ  →  TRẢ VỀ "KHÔNG ĐỦ TIN CẬY" thay vì một con số sai    │
     │ fHR(t) kèm khoảng tin cậy · chuỗi RR · tái tạo nhịp thai             │
     └──────────────────────────────────────────────────────────────────────┘
```

### 5.2 Đặc tả bộ dò `RelyFetal-TCN`

```
Đầu vào   (B, 2, 1000)   kênh 0 = tín hiệu dư r, kênh 1 = tín hiệu gốc x
Stem      Conv1d(2→40, k=7, pad=3) → BatchNorm → GELU
Thân      5 khối residual: h ← GELU( BN(Conv(k=7,d)) ∘ GELU(BN(Conv(k=7,d))) + h )
          d ∈ {1, 2, 4, 8, 16}  →  receptive field 379 mẫu = 1.516 ms
Head      Conv1d(40→1, k=1) → logit cho TỪNG MẪU, đầu ra (B, 1000)
Nhãn      heatmap Gaussian σ = 3 mẫu = 12 ms tại mỗi fQRS tham chiếu
Loss      BCEWithLogits, pos_weight = n_neg/n_pos (giới hạn 30)
Tối ưu    AdamW lr 3e-3, weight decay 1e-4, OneCycle, 6 epoch, batch 32, clip 1.0
Suy luận  trượt đoạn 4 s chồng lấn 1 s, trung bình cộng vùng chồng
Tham số   113.481
```

Mỗi quyết định thiết kế đều có bằng chứng, xem bảng §5.3.

### 5.3 Cơ sở của từng quyết định thiết kế

| Quyết định | Bằng chứng |
|---|---|
| Dải 10–60 Hz | Quét 8 dải: +11,0 điểm so với 1–45 Hz. Đồng thuận với Behar 2014, Clifford 2014, Xu 2026 |
| 250 Hz | Behar 2014, Chen 2025, Asadi 2025 đều dùng |
| Đoạn 4 giây | Shokouhmand 2023 quét 1–10 s và tìm ra 4 s tối ưu; Chen 2025 và Asadi 2025 dùng 4,096 s |
| Receptive field ~1,5 s | F1 đơn điệu theo RF, bão hoà ở 1,5 s; +4,66 điểm so với 172 ms, p < 0,0001 |
| TCN dilated, không Transformer | Của nhóm: transformer chậm 22× cho +0,25 điểm. Xu 2026: CNN 0,9445/0,08 GFLOPs so với Transformer 0,9380/12,5 GFLOPs |
| Kernel giảm dần | Xu 2026 ablation ở cùng dung lượng: coarse-to-fine thắng fine-to-coarse 2,69% tương đối |
| Dung lượng vừa phải | Xu 2026: tăng từ 5,91 M lên 14,44 M tham số **làm giảm** AUC |
| Đầu ra theo từng mẫu | Jitter 1,0 ms so với 5,6–6,0 ms của bộ phân loại cửa sổ |
| Hai kênh vào | Tín hiệu gốc cung cấp ngữ cảnh nhịp mẹ để loại tàn dư |
| Ngưỡng trên validation | Chống rò rỉ siêu tham số |

### 5.4 Thiết kế fSQI (đóng góp C3)

**Đặc trưng đầu vào** — tính trên mỗi đoạn 5 giây của tín hiệu dư:

| Nhóm | Nội dung |
|---|---|
| Sublevel-set H0 | Phổ độ nổi đỉnh đa thang trên r và −r (tương đương topo của peak prominence) |
| Vietoris–Rips H0 | Thống kê tốc độ quỹ đạo trên nhúng Takens ở hai độ trễ |
| Vietoris–Rips H1 | Độ bền vòng, số vòng, bán kính sinh |
| Persistence entropy | Đo tính "trật tự" của giản đồ bền vững |
| Đặc trưng biên độ | RMS, kurtosis, độ nổi đỉnh lớn nhất (làm baseline nội bộ) |

**Nhãn huấn luyện fSQI** — F1 dò thực tế của đoạn đó, tính **chỉ trên tập train**, không bao giờ dùng nhãn của tập test. Hồi quy hoặc phân loại nhị phân "đoạn đạt Se ≥ 0,9".

**Bộ so sánh bắt buộc**: SampEn (Zhong 2018 dùng), bSQI (Behar 2014), kurtosis, entropy phổ, và một MLP trên đặc trưng biên độ. Nếu fSQI topo không thắng các baseline này thì phải báo cáo trung thực là không thắng.

**Đánh giá**: tương quan Spearman với F1 thực; AUC phân loại đoạn tốt/xấu; và quan trọng nhất là **đường cong coverage–accuracy** — F1 trên phần dữ liệu được giữ lại, vẽ theo tỉ lệ dữ liệu bị từ chối, so với đường cơ sở từ chối ngẫu nhiên.

### 5.5 Dữ liệu

Tất cả tải trực tiếp từ nguồn gốc bằng `download_data.py` của nhóm, kèm `data_card.json` ghi mã băm.

| Bộ | Quy mô | Tần số | Nhãn | Giấy phép | Vai trò |
|---|---|---|---|---|---|
| **ADFECGDB** | 5 sản phụ chuyển dạ, 5 phút, 4 kênh bụng + 1 da đầu, tuần 38–41 | 1 kHz | Sóng R trên kênh da đầu, **bác sĩ tim mạch duyệt** | ODC-BY | Đánh giá chính (LORO) |
| **CinC 2013 set-a** | 75 bản ghi × 1 phút, 4 kênh | 1 kHz | Crowd-sourcing chuyên gia + thuật toán | ODC-BY | Huấn luyện + 5-fold theo bản ghi |
| **Matonia 2020** | **10 tín hiệu thai kỳ × 20 phút (tuần 32–42)** + 12 chuyển dạ × 5 phút | 500 Hz bụng | Tự động + chuyên gia sửa, **có cờ độ tin cậy từng nhịp** | figshare | **Mở rộng n lên ~22, bổ sung dữ liệu THAI KỲ** |
| **FECGSYNDB** | 1.750 tín hiệu, 145,8 giờ, 5 mức SNR, 6 tình huống | 250 Hz | Chuẩn vàng tuyệt đối | ODC-BY | Tiền huấn luyện (E7), stress test |
| **NSTDB** | Nhiễu thật: bw, em, ma | 360 Hz | — | ODC-BY | Đường cong F1–SNR |
| **NIFEADB** | 12 loạn nhịp + 14 bình thường | 500 Hz / 1 kHz | Không có chú giải fQRS | ODC-BY | Kiểm tra định tính trên nhịp bất thường |

**Bốn loại rò rỉ phải chặn:**

| Loại | Mô tả | Cách chặn |
|---|---|---|
| L1 — chủ thể | Cùng sản phụ ở train và test | LORO / chia theo bản ghi, không bao giờ chia ngẫu nhiên theo đoạn |
| L2 — kênh | Các kênh của cùng bản ghi rơi vào cả hai phía | Chia theo **bản ghi**, mọi kênh của một bản ghi đi cùng nhau |
| L3 — bộ dữ liệu | **CinC 2013 set-a chứa 25 bản ghi có nguồn gốc từ ADFECGDB** | Cross-dataset chỉ dùng FECGSYNDB → thực; nếu dùng CinC làm train thì phải loại 25 bản ghi đó |
| L4 — siêu tham số | Ngưỡng, chọn kênh, epoch chọn theo tập test | Bản ghi validation riêng trong mỗi fold |

### 5.6 Giao thức đánh giá

| Mã | Giao thức | Trả lời |
|---|---|---|
| **P1** | LORO trên ADFECGDB, 5 fold, validation nội bộ, 3 seed | Tổng quát sang sản phụ chưa thấy |
| **P2** | 5-fold theo bản ghi trên CinC 2013 set-a | Quy mô lớn hơn, đa dạng thiết bị |
| **P3** | LORO trên Matonia B1 (thai kỳ) | Giai đoạn thai kỳ, không chuyển dạ |
| **P4** | Cross-dataset: FECGSYNDB → ADFECGDB / Matonia | Dịch chuyển miền, không vi phạm L3 |
| **P5** | Đường cong F1–SNR: nhiễu NSTDB ở {20, 15, 10, 5, 0} dB, hai kịch bản (train sạch→test nhiễu và matched) | Độ bền |
| **P6** | Hiệu quả mẫu: F1 theo số bản ghi huấn luyện | Cần bao nhiêu dữ liệu |
| **P7** | Coverage–accuracy với fSQI | Giá trị của cơ chế từ chối |

### 5.7 Độ đo

- **Dò fQRS** (chính): Se, PPV, **F1** ở mức sự kiện, dung sai **±50 ms**, ghép cặp một-một tham lam. Báo cáo theo từng (bản ghi × kênh), macro và micro, kèm TP/FP/FN thô. **Jitter** (sai số định vị trên các TP).
- **fHR**: MAE (bpm) trên cửa sổ 5 s và 10 s, RMSE khoảng RR (ms), tỉ lệ cửa sổ sai > 5 bpm.
- **fSQI**: Spearman ρ với F1 thực, AUC phân loại đoạn tốt/xấu, **diện tích dưới đường cong coverage–accuracy**.
- **Tái tạo**: PCC với fECG da đầu, PRD (chỉ ADFECGDB, nêu rõ giới hạn).
- **Hiệu năng**: ms/phút tín hiệu trên CPU, số tham số, RAM đỉnh — đo thật.

### 5.8 Phân tích thống kê

- Đơn vị thống kê là **(bản ghi × kênh)**, không phải cửa sổ. Dùng cửa sổ tạo ra n giả hàng chục nghìn.
- Mọi số: mean ± SD **và** khoảng tin cậy bootstrap 95% ở mức bản ghi, 10.000 lần lấy mẫu lại.
- So sánh cặp: **Wilcoxon signed-rank**, hiệu chỉnh **Holm** khi so nhiều cặp.
- Báo cáo **effect size**: Cliff's delta.
- **3 seed** cho mọi mô hình; tách bạch độ lệch giữa seed và độ lệch giữa fold.
- Với n nhỏ: không dùng t-test, không coi p < 0,001 là bằng chứng mạnh.

### 5.9 Bảy thí nghiệm

| Mã | Thí nghiệm | Trả lời | Đầu ra |
|---|---|---|---|
| **E1** | Benchmark 5 biểu diễn × 4 baseline cổ điển trên P1, P2, P3 | RQ1 | Bảng chính của bài báo |
| **E2** | Phân rã đóng góp: tiền xử lý (8 dải) × biểu diễn × kiến trúc × hậu xử lý | RQ2 | Hình phân rã |
| **E3** | fSQI topo so với 5 SQI cổ điển | RQ3 | Bảng SQI + biểu đồ tán xạ |
| **E4** | Coverage–accuracy, ngưỡng từ chối quét toàn dải | RQ4 | **Hình chính của đóng góp C3** |
| **E5** | Cross-dataset P4 | RQ5 | Bảng chuyển miền |
| **E6** | Đường cong F1–SNR P5 + hiệu quả mẫu P6 | RQ5 | Hai hình |
| **E7** | Tiền huấn luyện FECGSYNDB rồi tinh chỉnh, so với huấn luyện từ đầu | RQ6 | Bảng fine-tuning |

**Ablation** (mỗi cái trả lời đúng một câu hỏi): A1 dải thông · A2 có/không khử mẹ · A3 độ dài đoạn · A4 receptive field · A5 nhãn nhị phân so với heatmap · A6 H0 so với H1 so với cả hai · A7 một lọc so với nhiều lọc · A8 Persistence Image so với đặc trưng PD thủ công · A9 có/không augmentation · A10 có/không ràng buộc RR ở hậu xử lý.

---

## 6. KẾT QUẢ KỲ VỌNG

Mọi mức dưới đây tính từ mức tiền khả thi **đã đạt được** (97,43% trong miền, 77,52% xuyên miền), không phải từ con số tuỳ tiện.

| Mức | Tiêu chí | Ý nghĩa |
|---|---|---|
| **Thất bại** | F1 trong miền < 95% hoặc benchmark không hoàn thành | Phải xem lại pipeline |
| **Tối thiểu** | Benchmark đầy đủ 9 phương pháp × 3 bộ dữ liệu + phân rã đóng góp + mã mở. F1 trong miền ≥ 95% | Đủ cho Euréka và CinC |
| **Tốt** | Thêm: fSQI có ρ ≥ 0,6, coverage–accuracy vượt đường cơ sở ngẫu nhiên rõ rệt, F1 xuyên miền ≥ 85% | **Đủ cho Q1** |
| **Mạnh** | Thêm: từ chối 20% nâng F1 phần còn lại ≥ 8 điểm; fine-tuning FECGSYNDB nâng xuyên miền ≥ 5 điểm; xác nhận trên Matonia | **Q1 vững, có thể nhắm tạp chí top của lĩnh vực** |
| **Rất mạnh** | Thêm: F1 xuyên miền ≥ 92% với cơ chế từ chối, và fSQI tổng quát hoá sang NIFEADB | Vượt mọi kết quả đơn kênh đã công bố có giao thức sạch |

**Điều kiện chuyển hướng.** Nếu đến tuần 14 mà fSQI không vượt SampEn, dừng phát triển fSQI và dồn toàn bộ nguồn lực vào C1 + C2 + kết quả phủ định có kiểm định. Benchmark và phân rã đóng góp **tự chúng đã đủ** cho một bài Q1, vì chúng trả lời câu hỏi mà cả lĩnh vực chưa trả lời.

---

## 7. CHIẾN LƯỢC CÔNG BỐ

### 7.1 Vì sao đề tài này có khả năng Q1

| Tiêu chí của reviewer Q1 | Đề tài đáp ứng thế nào |
|---|---|
| **Vấn đề quan trọng và chưa giải quyết** | Độ tin cậy của fECG đơn kênh; thất bại lưỡng cực đã được nhóm đo đạc, chưa bài nào xử lý |
| **Đóng góp mới, không tăng dần** | C3 là ứng dụng đầu tiên của đồng điều bền vững cho tín hiệu tim thai; C1 là benchmark đầu tiên |
| **Đánh giá nghiêm ngặt** | 7 giao thức, 3 bộ dữ liệu, 3 seed, kiểm định ghép cặp có hiệu chỉnh, bootstrap CI |
| **So sánh công bằng** | 4 baseline **cài lại**, không trích số từ bài khác |
| **Kết quả bất ngờ và có ích** | Tiền xử lý đóng góp gấp 30 lần kiến trúc; kết quả này thay đổi cách phân bổ nỗ lực nghiên cứu |
| **Tái lập được** | Mã mở MIT, fold cố định, data card có mã băm, CI, kết quả thô |
| **Trung thực** | Báo cáo cả kết quả phủ định (PI không hoạt động cho dò đỉnh) kèm giải thích cơ chế |

**Rủi ro Q1 lớn nhất** là reviewer hỏi *"chỉ 5 sản phụ ADFECGDB thì kết luận gì?"*. Đối sách: bắt buộc chạy trên **ba** bộ dữ liệu (ADFECGDB + CinC 2013 + Matonia), nâng n lên **~22 sản phụ** và bổ sung giai đoạn thai kỳ chứ không chỉ chuyển dạ. Đây là lý do E1 chạy trên P1, P2 **và** P3.

### 7.2 Lộ trình công bố

| Bước | Nơi | Thời điểm | Nội dung |
|---|---|---|---|
| 1 | **Computing in Cardiology** (4 trang) | Nộp ~tháng 4–5 | C1 + C2, lấy phản biện sớm và tạo dấu ấn ưu tiên |
| 2 | **Euréka** | Tuần 22–24 | Toàn bộ, kèm demo |
| 3 | **Q1**: *Physiological Measurement* (IOP, Q1 Biomedical Engineering) | Sau CinC | C1 + C2 + C3 + C4 đầy đủ |
| | Dự phòng: *Biomedical Signal Processing and Control*, *Computers in Biology and Medicine*, *IEEE JBHI* | | |
| 4 | Trong nước: RIVF / NICS / KSE / SoICT | Song song | Tập dượt trình bày |

*Physiological Measurement* là lựa chọn số một: nó là nơi công bố của Behar 2014, Andreotti 2016, Clifford 2014 và Le 2025 — tức là chính những bài mà đề tài này đối thoại trực tiếp.

### 7.3 Cách phát biểu đóng góp trong bài báo

**Không viết**: *"Chúng tôi đề xuất một phương pháp mới vượt SOTA."*

**Viết**: *"Chúng tôi cung cấp benchmark không rò rỉ đầu tiên cho dò fQRS đơn kênh, phân rã định lượng đóng góp của từng khối trong pipeline, và giới thiệu một chỉ số chất lượng dựa trên đồng điều bền vững cho phép hệ thống từ chối trả lời khi không đủ tin cậy. Chúng tôi cũng báo cáo kết quả phủ định: biểu diễn topo không cải thiện việc dò đỉnh, kèm giải thích cơ chế."*

Cách phát biểu thứ hai khó bác hơn nhiều, và đúng với bằng chứng.

---

## 8. KẾ HOẠCH TRIỂN KHAI 24 TUẦN

| Phase | Tuần | Mục tiêu | Nhiệm vụ | Người chịu trách nhiệm | Phụ thuộc | Bàn giao | Tiêu chí nghiệm thu | Rủi ro |
|---|---|---|---|---|---|---|---|---|
| **P0** | 1 | Hạ tầng | Repo mới MIT; `download_data.py`; data card; CI; chuẩn mã | SV3 | — | D0: repo sạch chạy được | `pytest` xanh; tải đủ 3 bộ dữ liệu | Thấp |
| **P1** | 2–3 | Nền đánh giá | Module `metrics_50ms.py` **duy nhất**; `folds.json` cố định; kiểm thử đơn vị đối chiếu `wfdb.compare_annotations` | SV2 | P0 | D1: bộ đánh giá + test | Trùng khớp với wfdb trên dữ liệu giả lập | Thấp |
| **P2** | 4–5 | Tiền xử lý và khử mẹ | Quét 8 dải (A1); TS-PCA + 2 biến thể; đo Se/PPV của bộ dò **mQRS** riêng | SV1 | P1 | D2: bảng A1 | Tái lập được kết quả tiền khả thi ±1 điểm | Trung bình |
| **P3** | 6–7 | Baseline cổ điển | Cài lại TS, TS-PCA, Castillo 2018, EEMD | SV1 | P2 | D3: bảng baseline | TS đạt ≥ 88% trên P1 | Trung bình |
| **🚦** | **7** | **Go/No-go 1** | Nếu baseline < 85% thì dừng, sửa pipeline | GVHD | | | | |
| **P4** | 8–10 | Bộ dò | `RelyFetal-TCN`; A2–A5, A9, A10; 3 seed trên P1, P2 | SV2 | P2 | D4: bảng dò chính | F1 ≥ 95% trên P1, vượt TS có ý nghĩa | Trung bình |
| **P5** | 11–13 | **Benchmark E1** | 5 biểu diễn × 3 bộ dữ liệu, cùng ngân sách; A6–A8 | SV2 + SV1 | P3, P4 | **D5: bảng benchmark** | Mọi ô có 3 seed và kiểm định | Cao |
| **P6** | 14 | **Phân rã E2** | Tiền xử lý × biểu diễn × kiến trúc × hậu xử lý | SV2 | P5 | D6: hình phân rã | Có khoảng tin cậy | Trung bình |
| **🚦** | **14** | **Go/No-go 2** | Nếu fSQI (thử nhanh) không hứa hẹn, dồn về C1+C2 | GVHD | | | | |
| **P7** | 15–17 | **fSQI E3, E4** | Đặc trưng topo; nhãn từ train; so 5 SQI cổ điển; coverage–accuracy | SV1 + SV3 | P5 | **D7: bảng SQI + hình C3** | ρ ≥ 0,5 hoặc kết luận phủ định rõ ràng | Cao |
| **P8** | 18–19 | Chuyển miền và độ bền | E5 cross-dataset; E6 F1–SNR và hiệu quả mẫu | SV2 | P4 | D8: 3 hình | Bootstrap CI trên mọi điểm | Trung bình |
| **P9** | 20 | **Fine-tuning E7** | Tiền huấn luyện FECGSYNDB → tinh chỉnh thực | SV1 | P4 | D9: bảng fine-tuning | Có so với huấn luyện từ đầu | Trung bình |
| **P10** | 21 | Sản phẩm | CLI; FastAPI tối giản; dashboard hiển thị fSQI và cảnh báo từ chối; Docker | SV3 | P4, P7 | D10: demo | Chạy được từ clone sạch | Trung bình |
| **P11** | 22–23 | Viết | Bản thảo Q1; bản CinC 4 trang; báo cáo Euréka; poster | Cả nhóm | Tất cả | **D11: bản thảo** | GVHD duyệt; mọi số có nguồn | Cao |
| **P12** | 24 | Tái lập | `reproduce.sh`; ghim phiên bản; Zenodo DOI; kết quả thô | SV3 | Tất cả | D12: gói tái lập | Người ngoài chạy ra cùng số | Trung bình |

### Phân vai

| | **SV1 — Tín hiệu và Topo** | **SV2 — Học máy và Đánh giá** | **SV3 — Hệ thống và Tái lập** |
|---|---|---|---|
| Sở hữu | P2, P3, P7 (đặc trưng), P9 | P1, P4, P5, P6, P8 | P0, P7 (mô hình), P10, P12 |
| Module | `preprocess/`, `mecg/`, `topology/` | `models/`, `train/`, `eval/` | `sqi/`, `api/`, `ci/`, `repro/` |
| Kỹ năng | scipy.signal, wfdb, mne, ripser | PyTorch, sklearn, thống kê | FastAPI, Docker, GitHub Actions |
| Review chéo | SV3 review SV1 | SV1 review SV2 | SV2 review SV3 |

**GVHD**: duyệt thiết kế thực nghiệm (tuần 3), go/no-go 1 (tuần 7), go/no-go 2 (tuần 14), duyệt bản thảo (tuần 21).

**Quy tắc làm việc**: mọi thí nghiệm ghi vào `experiments.csv` (id, ngày, hash cấu hình, fold, seed, metric); mọi PR có ít nhất một reviewer; không ai sửa `metrics_50ms.py` một mình.

---

## 9. RỦI RO VÀ PHƯƠNG ÁN DỰ PHÒNG

| # | Rủi ro | Xác suất | Tác động | Dấu hiệu sớm | Dự phòng |
|---|---|---|---|---|---|
| R1 | fSQI topo không vượt SampEn | Trung bình | Cao | Tuần 15: ρ < 0,4 | Vẫn báo cáo so sánh SQI đầy đủ (có giá trị); dồn về C1+C2 vốn đã đủ cho Q1 |
| R2 | Không tải được Matonia từ figshare | Thấp | Cao | Tuần 2 | Dùng ADFECGDB + CinC; giảm phạm vi P3; nêu rõ hạn chế |
| R3 | Khử mẹ kém trên CinC (nhiều thiết bị) | Trung bình | Cao | F1 CinC thấp bất thường ở nhiều bản | Nhiều biến thể TS (trung vị, PCA, miền tần số theo Wang 2024); báo cáo Se/PPV của bộ dò mQRS riêng để chẩn đoán |
| R4 | Chú giải CinC kém ở một số bản ghi | Cao (đã biết) | Trung bình | F1 thấp bất thường ở vài bản | Loại theo danh sách của Zhong 2018 / Behar 2014, **công bố danh sách đã loại** |
| R5 | Overfit vào ít chủ thể | Cao | Cao | Chênh lớn train/val | Mô hình < 120k tham số; augmentation; tiền huấn luyện FECGSYNDB; báo cáo cả 3 bộ dữ liệu |
| R6 | Nhóm thiếu nền tảng topo đại số | Trung bình | Thấp | Tuần 1–2 | Chỉ cần học đúng ba điều: sublevel-set H0 = độ nổi đỉnh, VR H0 = single-linkage, PI = KDE có trọng số. Không cần lý thuyết đồng điều đầy đủ |
| R7 | Chi phí tính toán | Thấp | Thấp | — | Đã đo: 3,1 ms/cửa sổ cho toàn bộ đặc trưng topo; toàn bộ pipeline chạy trên CPU |
| R8 | Trễ tiến độ viết bài | Trung bình | Cao | Tuần 20 | Bắt đầu viết Methods từ tuần 10, song song với thực nghiệm |

---

## 10. SẢN PHẨM BÀN GIAO

1. **Bản thảo bài báo Q1** (tiếng Anh, 8–12 trang) + bản CinC 4 trang.
2. **Báo cáo Euréka** (tiếng Việt) + poster.
3. **Repo mã nguồn mở** giấy phép MIT: `folds.json`, `data_card.json`, `reproduce.sh`, CI, không chứa dữ liệu PhysioNet hay PDF có bản quyền — chỉ script tải.
4. **Bộ kết quả thô** `results/*.json` cho mọi ô trong mọi bảng, đủ để người khác vẽ lại hình.
5. **Demo**: CLI + FastAPI + dashboard hiển thị fQRS, fHR, **và cảnh báo khi fSQI thấp**.
6. **Checkpoint** đã huấn luyện kèm metric và ngưỡng.

---

## 11. KINH PHÍ ĐỀ XUẤT

| Khoản | Ước tính (VNĐ) |
|---|---|
| GPU đám mây (Colab Pro / Kaggle, 4 tháng) — chỉ cần cho E1 và E7 quy mô lớn | 1.200.000 |
| Lưu trữ và hosting demo (VPS nhỏ, 6 tháng) | 500.000 |
| In ấn poster, báo cáo, hồ sơ Euréka | 500.000 |
| Phí xử lý bài báo / hiệu đính tiếng Anh (một phần) | 800.000 |
| **Tổng** | **3.000.000** |

Ghi chú: toàn bộ thí nghiệm tiền khả thi đã chạy được trên **CPU máy cá nhân**. GPU chỉ cần khi mở rộng sang FECGSYNDB (145,8 giờ dữ liệu).

---

## PHỤ LỤC A — VÌ SAO ĐỀ CƯƠNG ĐỔI TỪ v1.0 SANG v2.0

Bản v1.0 đặt Persistence Image + CNN 2D làm phương pháp chính, với hai giả thuyết: (i) QRS mẹ và thai tạo hai "vòng lặp" tách biệt trong không gian pha; (ii) biểu diễn topo bền với nhiễu hơn tín hiệu thô. Nhóm đã kiểm chứng cả hai trước khi viết bản này.

| Giả thuyết v1.0 | Kết quả kiểm chứng | Kết luận |
|---|---|---|
| Có "vòng nhịp thai" trong nhúng trễ cửa sổ 300 ms | Cửa sổ 300 ms **ngắn hơn một chu kỳ tim thai** (≈430 ms), nên theo chính lý thuyết sliding-window persistence của Perea & Harer (2015) không thể có vòng nhịp. Đặc trưng H1 có AUC 0,641, yếu nhất trong nhóm | **Bác bỏ** |
| Sublevel-set H0 là đặc trưng topo mới | Trùng khớp **chính xác 100%** với `scipy.signal.peak_prominences` trên 2.000 cửa sổ thật (tương quan 1,0000) | **Là kỹ thuật cổ điển**, phải trích dẫn đúng |
| PI + CNN 2D là biểu diễn tốt | Đứng **cuối cùng trong 16 kiến trúc**: F1 27,42 so với 97,14 của CNN 1D cùng số tham số | **Bác bỏ** |
| Hai luồng (1D + PI) bổ trợ nhau | +0,10 điểm, gấp đôi tham số. Ở mức sự kiện: +0,88 điểm, **p = 0,625** | **Bác bỏ có kiểm định** |
| PI bền nhiễu hơn tín hiệu thô | Với nhiễu NSTDB ở SNR 10/5/0 dB, biểu diễn thô cao hơn ở **mọi** mức | **Không ủng hộ** |
| Đóng góp "đa thang độ trễ" là mới | Tran & Hasegawa, *Phys. Rev. E* 99:032209 (2019) đã công bố delay-variant embedding kèm chứng minh bền nhiễu | **Đã có tiền lệ** |
| Đóng góp "learnable persistence weighting" là mới | PersLay (Carrière et al., AISTATS 2020) và PI-Net (Som et al., CVPRW 2020) đã có | **Đã có tiền lệ** |

**Điều được giữ lại từ v1.0**: khoảng trống G3 (chưa có TDA cho tín hiệu thai) là **thật** và đã được xác nhận qua bốn cơ sở dữ liệu và ba ngôn ngữ. Điều thay đổi là **nhiệm vụ** mà TDA được giao: từ dò đỉnh sang đánh giá chất lượng — nhiệm vụ mà cả thực nghiệm của nhóm lẫn y văn đều ủng hộ.

**Đây là điểm mạnh của đề cương, không phải điểm yếu.** Một đề tài đã tự bác bỏ giả thuyết ban đầu bằng thực nghiệm và tái định hướng dựa trên bằng chứng là đề tài đã vượt qua rủi ro lớn nhất trước khi bắt đầu.

---

## PHỤ LỤC B — CƠ SỞ Y VĂN

**Đã tải toàn văn 27 bài, đọc đầy đủ Methods và Results 29 bài.** Danh sách đầy đủ kèm ma trận 17 cột và phân tích A–I từng bài nằm trong tài liệu phản biện kèm theo.

### Nhóm 1 — fECG đơn kênh, học sâu

Zhong et al., *Physiol. Meas.* 39:045004 (2018) · Zhong et al., *Australas. Phys. Eng. Sci. Med.* 42:1081 (2019) · Mohebbian et al., *IEEE JBHI* 26(2) (2022) · Basak et al., *Expert Syst. Appl.* 235:121196 (2024) · Shokouhmand & Tavassolian, *IEEE TBME* 70(1):283 (2023) · Chen, Wu & Zhou, *Sensors* 25(3):601 (2025) · Asadi, Ghaffari & Hatami, *IEEE Access* 13:206367 (2025) · Asadi & Ghaffari, *IEEE JBHI* 30(4):3568 (2026) · Xu et al., *Sensors* 26(7):2037 (2026) · Alidash & Hesar, *Sci. Rep.* (2025) · Orvas et al., arXiv:2506.22457 (2025) · Wahbah et al., *Front. Physiol.* 15:1329313 (2024)

### Nhóm 2 — fECG cổ điển, benchmark, dữ liệu

Behar, Johnson, Clifford & Oster, *Ann. Biomed. Eng.* 42(6):1340 (2014) · Behar, Oster & Clifford, *Physiol. Meas.* 35(8):1569 (2014) · Andreotti et al., *Physiol. Meas.* 37(5):627 (2016) · Niknazar, Rivet & Jutten, *IEEE TBME* 60(5):1345 (2013) · Castillo et al., *PLOS ONE* 13(6):e0199308 (2018) · Le, Vo & Tran, *Physiol. Meas.* 46(7):075005 (2025) · Sulas et al., *Math. Biosci. Eng.* 17(1):286 (2020) · Clifford et al., *Physiol. Meas.* 35(8):1521 (2014) · Matonia et al., *Sci. Data* 7:200 (2020) · Jezewski et al., *Biomed. Tech.* (2012)

### Nhóm 3 — Nền tảng TDA

Takens (1981) · Perea & Harer, *Found. Comput. Math.* (2015) · Cohen-Steiner, Edelsbrunner & Harer, *Discrete Comput. Geom.* 37:103 (2007) · Adams et al., *JMLR* 18(8) (2017) · Carrière et al., AISTATS PMLR 108 (2020) · Som et al., CVPRW (2020) · Turkeš, Montúfar & Otter, *NeurIPS 35* (2022) · Tran & Hasegawa, *Phys. Rev. E* 99:032209 (2019) · Tan et al., *Chaos* 33:032101 (2023)

### Nhóm 4 — TDA cho ECG và tín hiệu sinh học

Ren et al., *Front. Neurosci.* 17:1153386 (2023) · Ignacio et al., IEEE ICMLA (2019) · Dindin, Umeda & Chazal (2019) · Chung et al., *Front. Physiol.* 12:637684 (2021) · Graff et al., *PLoS ONE* 16:e0253851 (2021) · Domínguez-Monterroza et al., *PLoS One* (2025) · Karan & Kaygun, *Expert Syst. Appl.* 183:115326 (2021) · Lee et al., *Ann. Biomed. Eng.* 30(9):1140 (2002)

---

## PHỤ LỤC C — TÌNH TRẠNG MÃ NGUỒN HIỆN TẠI

Mã tiền khả thi đã có, **hoàn toàn độc lập**, tải dữ liệu trực tiếp từ PhysioNet:

| Tệp | Vai trò |
|---|---|
| `download_data.py` | Tải ADFECGDB, CinC 2013, NSTDB, NIFEADB từ PhysioNet; sinh `data_card.json` có mã băm |
| `fqrs_model.py` | Thư viện tham chiếu: tiền xử lý, khử mẹ, mô hình, suy luận, chấm điểm ±50 ms |
| `train_final.py` | Huấn luyện 5 fold LORO + mô hình production, lưu checkpoint kèm metric |
| `predict.py` | CLI: đọc EDF/WFDB/CSV/NPY → vị trí fQRS, fHR, chấm điểm nếu có nhãn |
| `band_ablation.py`, `arch_search.py`, `seq_search.py`, `seq_loro.py` | Bốn thí nghiệm tiền khả thi |

Toàn bộ sẽ được viết lại thành một package sạch trong Phase P0 với cấu trúc chuẩn, kiểm thử đơn vị và CI. **Không tái sử dụng mã của bất kỳ bên thứ ba nào.**
