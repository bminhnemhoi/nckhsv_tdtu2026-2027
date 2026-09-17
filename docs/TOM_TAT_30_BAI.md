# Tóm tắt 30 bài đã đọc trong hai trang — cho giảng viên không chuyên tín hiệu

Ngày lập: 17/09/2026. Mọi con số truy ngược về `de_cuong_latex/bao_cao_30_paper.tex` (bài đọc) và `survey/facts_phase4.json` (số của nhóm). Chi tiết từng bài: `docs/BOI_CANH_1_KENH.md`.

**Bài toán trong một câu.** Từ điện tim dán trên bụng mẹ, tìm đúng thời điểm mỗi nhịp tim thai (sai lệch cho phép ±50 ms), trong khi tim mẹ mạnh gấp nhiều lần lấn át tín hiệu. Nhóm làm với **một** điện cực bụng; phần lớn y văn dùng **bốn** trở lên.

---

## Năm hướng trong y văn

**1. Khử tim mẹ bằng mẫu, lọc thích nghi, Kalman (p13, p16, p19; phần trừ mẫu của p14).** Họ ước lượng dạng sóng tim mẹ rồi trừ đi, hoặc dùng bộ lọc Kalman mô hình hoá cả hai tim cùng lúc. Kết quả tốt nhất có số: Behar 2014 đạt F1 90,2 trên bộ riêng khi có thêm điện cực ngực mẹ; lọc thích nghi một tham chiếu của Sulas 2020 chỉ đạt độ chính xác 0,68; Niknazar 2013 không báo cáo F1. Nhóm dùng chính bước trừ mẫu này làm tiền xử lý, rồi để mạng nơ-ron dò đỉnh trên phần dư, đạt 97,56 trên 22 sản phụ mà không cần điện cực ngực. So sánh không hoàn toàn công bằng vì khác bộ dữ liệu, nhưng cùng dung sai 50 ms.

**2. Tách nguồn mù đa kênh: ICA, PCA, SVD (p14, p15, p21; Power-MF ngoài danh sách).** Với 4–8 điện cực, thuật toán tách hỗn hợp thành các "nguồn" độc lập rồi chọn nguồn giống tim thai nhất. Đây là nhóm mạnh nhất: Power-MF 4 kênh 98,83 trên cùng 22 sản phụ của nhóm (nhóm tự chạy lại), Matonia 2020 PCA/ICA 98,56 trên 12 bản chuyển dạ (dung sai 40 ms), Behar FUSE 96,0 trên CinC set-a (trong mẫu). Cái giá là số điện cực và việc ICA không chạy được với một kênh: cắt Power-MF về một kênh thì còn 86,71. Nhóm thua 4 kênh 1,27 điểm (khoảng tin cậy chạm 0), nhưng lấy lại 89,49 % lợi ích đa kênh bằng một kênh. Công bằng: cùng bộ, cùng bộ chấm, cùng 22 người.

**3. Học sâu đơn kênh (p01, p03, p05, p06, p07, p09, p11).** Cùng cấu hình một kênh với nhóm. Hai kiểu: dò đỉnh trực tiếp (Zhong 2018, F1 77,85 nhưng tính trên cửa sổ 100 ms, không phải nhịp) và tái tạo dạng sóng tim thai rồi dò đỉnh (CycleGAN, DPSS, R2W-Net, SCTD-Net, CUNet). Trong miền họ công bố 96,5–99,7 trên ADFECGDB; nhóm đạt 99,40 trên 5 sản phụ đó. Ngoài miền (CinC set-a, không tinh chỉnh) họ công bố 77,8 (Orvas, 75 bản) đến 97,97 (Asadi, 80 kênh chọn); Castillo 2018 (98,07 trên 26 bản chọn tay) là phương pháp cổ điển (p17) nên không tính vào khoảng này. Nhóm đạt 74,28 (PSD, cũ), 80,72 (`gate`, quy tắc kế hoạch chọn, trượt Holm), 81,01 (`gate4`, cũng ghi trước khi chạy) và 82,01 (`peakprob`, hậu kiểm) trên 60 bản sạch, trần oracle 83,60. Công bằng chỉ một phần: Mohebbian dùng dung sai 30 ms, Chen tinh chỉnh trên tập kiểm, DPSS chọn kênh bằng tay, Asadi tính theo kênh, Orvas chấm cả 15 bản trùng dữ liệu huấn luyện của nhóm. Không bài nào chấm trên đúng 60 bản sạch với kênh chọn mù.

**4. Học sâu đa kênh (p04, p10, p12).** Đưa 4 hoặc 12 kênh vào mạng cùng lúc. Số công bố 88,8–98,4, khác đơn vị: Basak F1 96,4 ở dung sai 31,25 ms; Esmaeili Alidash độ chính xác (accuracy) 98,36 theo ô 100 ms; Wahbah độ chính xác 88,8 theo đoạn 65 ms khi tách chủ thể. Cả ba bài đều có vấn đề giao thức: Basak chia 5-fold không nêu cách, Esmaeili Alidash xáo trộn rồi chia với cửa sổ chồng 90 %, Wahbah dùng nhãn từ thuật toán chứ không từ điện cực da đầu. Không so được với nhóm: khác số kênh, khác đơn vị (ô 100 ms, đoạn 65 ms), khác cách chia.

**5. Đánh giá, bộ chuẩn, thử thách (p13, p14, p15, p20, p21).** Đây là nơi định nghĩa cách chấm: dung sai ±50 ms và công thức F1 đến từ Behar 2014 và Andreotti 2016, không phải từ xã luận CinC 2013 (Clifford 2014 chấm bằng lỗi nhịp, không dùng F1). Nhóm học được ba việc: chọn kênh oracle (Andreotti) thổi phồng số; toàn bộ Challenge 2013 (447 bản) có 25 bản lấy từ ADFECGDB, ban tổ chức đã ghi nhận từ 2013 nhưng không nói bản nào rơi vào set nào (`survey/ro_ri_vanlieu.json`) — nhóm đo và định danh được 15 bản trong 75 bản set-a là bản sao nguyên văn, và đo mức thổi phồng 3,27–7,18 điểm; và cần báo cáo mức chủ thể, không phải mức bản ghi.

**Nhóm còn lại (p22–p33): 12 bài về tô-pô (TDA) và chuỗi thời gian.** Đọc để kiểm tra hướng dùng đồng điều bền vững; kết quả thử nghiệm của nhóm âm tính (27,4 so với 97,1 của mạng 1D cùng tham số) và nhóm đã bỏ hướng này.

---

## Tám bài quan trọng nhất

| Tác giả–năm | Kênh | Bộ | Kết quả họ | Kết quả ta, cùng điều kiện (nếu có) | So được? |
|---|---|---|---|---|---|
| Jaeger 2024, Power-MF (chạy lại) | 4 | Silesia 22 sản phụ, ±50 ms | 98,83 | 97,56 (1 kênh); hiệu −1,27 [−3,08; +0,27] | **Có** — cùng bộ, cùng bộ chấm |
| Jaeger 2024, Power-MF cắt về 1 kênh | 1 | như trên | 86,71 | 97,56; hiệu +10,85 [+6,80; +15,40] | **Có** |
| Castillo 2018 | 1 | ADFECGDB, ±50 ms | 94,11 (17 tín hiệu) / 98,63 (kênh tốt nhất) | 99,40 (5 sản phụ, tách chủ thể) | Có, nhưng số của họ trong mẫu và lọc kênh bằng bác sĩ |
| Shokouhmand 2023, DPSS | 1 | Silesia 22, ±50 ms | 97,7 (kênh chọn tay) | 97,56 (kênh chọn mù) | Một phần — chưa chạy lại, kênh chọn khác nhau |
| Orvas 2025, CUNet | 1 | CinC set-a, ±50 ms, zero-shot | 77,8 ± 18,6 (75 bản) | 74,28 [66,63; 81,78] PSD / 80,72 gate (kế hoạch chọn, trượt Holm) / 81,01 gate4 (cũng ghi trước) / 82,01 peakprob hậu kiểm (60 bản sạch; trần oracle 83,60) | Có điều kiện — khác tập bản ghi |
| Mohebbian 2022 | 1 | ADFECGDB, **30 ms**, tách chủ thể | 99,7 ± 0,4 | chưa đo ở 30 ms | Một phần — khác dung sai |
| Behar 2014, FUSE | 4 | CinC set-a 68 bản, ±50 ms, trong mẫu | 96,0 | 74,28 PSD / 80,72 gate (trượt Holm) / 81,01 gate4 / 82,01 peakprob hậu kiểm (60 bản sạch, zero-shot) | Một phần — 4 kênh, trong mẫu, khác tập |
| Matonia 2020 | 4 | Silesia B2 12, **40 ms** | 98,56 | 96,82 trên 7 bản B2 không trùng, ±50 ms | Một phần — đa kênh, khác dung sai |

**Ba câu chốt.** (1) Trong miền, một kênh của nhóm ngang tầm các bài đơn kênh và kém bốn kênh 1,27 điểm chưa phân biệt được với 0. (2) Đa kênh đáng giá 12,12 điểm cho Power-MF; nhóm lấy lại 89,49 % bằng một kênh. (3) Ngoài miền nhóm thấp hơn số công bố của đa số bài đơn kênh, nhưng không bài nào so đầu-đối-đầu được; nguyên nhân khoảng cách chưa xác định và là việc phải làm tiếp.
