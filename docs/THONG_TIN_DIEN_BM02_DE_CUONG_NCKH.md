# THÔNG TIN ĐIỀN BIỂU MẪU BM02: ĐỀ CƯƠNG CÔNG TRÌNH NCKH SINH VIÊN

**NĂM HỌC 2026 – 2027 (TRƯỜNG ĐẠI HỌC TÔN ĐỨC THẮNG - TDTU)**

> **Mã biểu mẫu:** TT/P.QLPTKHCN/13/BM02  
> **Tổng kinh phí đề nghị Nhà trường hỗ trợ:** 2.920.000 VNĐ (Hai triệu chín trăm hai mươi nghìn đồng)  
> **Đặc điểm:** Nội dung ngắn gọn, từ ngữ đơn giản, dễ hiểu, kinh phí tập trung vào GPU, phần cứng và in poster.

---

### 1. Tên đề tài:

- **Tiếng Việt:** Nhận diện nhịp tim thai từ điện tim ổ bụng đơn kênh trên thiết bị nhúng
- **Tiếng Anh:** Single-channel abdominal fetal heart rate detection on embedded devices

---

### 2. Lý do/ mục đích nghiên cứu:

- **Lý do nghiên cứu:**
  - Việc theo dõi nhịp tim thai liên tục giúp phát hiện sớm tình trạng suy thai hoặc thiếu oxy để can thiệp kịp thời.
  - Hiện nay, phương pháp siêu âm tim thai (Doppler/CTG) cần nhân viên y tế thao tác và khó theo dõi liên tục tại nhà. Phương pháp gắn điện cực vào da đầu thai nhi thì phải can thiệp xâm lấn, chỉ làm được khi sinh.
  - Đo điện tim ở bụng mẹ là hướng đi an toàn, nhưng đa số nghiên cứu dùng nhiều dây đo (4 đến 32 điện cực) rất vướng víu.
  - Nếu rút gọn xuống chỉ dùng **1 kênh đo duy nhất** (như một miếng dán đơn giản) thì tín hiệu tim thai rất yếu, dễ bị lẫn vào nhịp tim mẹ và tiếng ồn cử động. Ngoài ra, máy đo tự động hiện nay dễ báo động sai khi miếng dán bị hở. Vì vậy, cần một giải pháp AI thông minh, vừa bắt được nhịp thai từ 1 dây đo, vừa biết tự ngắt cảnh báo khi tín hiệu không rõ ràng.

- **Mục đích nghiên cứu:**
  - Xây dựng mô hình trí tuệ nhân tạo (AI) gọn nhẹ để nhận diện chính xác nhịp tim thai từ 1 dây điện cực bụng mẹ.
  - Tích hợp tính năng cảnh báo an toàn: máy tự biết lúc nào tín hiệu bị nhiễu hoặc tuột dây để không đưa ra kết quả sai.
  - Chạy thử nghiệm thuật toán trên mạch vi điều khiển thực tế để chứng minh tính khả thi khi làm thiết bị đeo giá rẻ.

---

### 3. Đối tượng nghiên cứu:

- Tín hiệu điện tim ổ bụng người mẹ đo từ 1 kênh dẫn.
- Nhịp tim thai và vị trí các đỉnh nhịp tim thai.
- Thuật toán lọc nhiễu, tách nhịp tim mẹ để lấy nhịp tim thai.
- Mô hình mạng nơ-ron nhân tạo dạng chuỗi thời gian (TCN) kích thước nhỏ.
- Mạch vi điều khiển nhúng giá rẻ (dòng chip ESP32) để xử lý tín hiệu.

---

### 4. Phạm vi/ giới hạn nghiên cứu:

- **Phạm vi dữ liệu:** Sử dụng các bộ dữ liệu điện tim thai mở chuẩn quốc tế từ PhysioNet (ADFECGDB và CinC 2013).
- **Phạm vi kỹ thuật:** Chỉ tập trung xử lý trên 1 kênh đo duy nhất ở bụng mẹ; đánh giá độ chính xác theo dung sai chuẩn y tế (±50 ms).
- **Giới hạn nghiên cứu:** Nhóm thực hiện mô phỏng và thử nghiệm tín hiệu trên bo mạch điện tử trong phòng thí nghiệm; chưa thử nghiệm trực tiếp trên phụ nữ mang thai để đảm bảo an toàn y đức.

---

### 5. Nội dung/ phương pháp nghiên cứu:

Đề tài được triển khai qua 5 nội dung chính với phương pháp thực hiện cụ thể như sau:

- **Nội dung 1: Thu thập và tiền xử lý tín hiệu điện tim**
  - _Nội dung thực hiện:_ Chuẩn bị dữ liệu điện tim ổ bụng chuẩn và lọc bỏ các nguồn nhiễu môi trường.
  - _Phương pháp:_ Tải các bộ dữ liệu điện tim thai mở chuẩn quốc tế từ PhysioNet (ADFECGDB, CinC 2013). Sử dụng bộ lọc số kỹ thuật số để loại bỏ nhiễu trôi do nhịp thở của mẹ và nhiễu điện lưới 50 Hz, chỉ giữ lại dải tín hiệu hữu ích (10 – 60 Hz) chứa nhịp tim thai.

- **Nội dung 2: Bóc tách và loại bỏ nhịp tim mẹ khỏi tín hiệu**
  - _Nội dung thực hiện:_ Tách bỏ sóng điện tim của mẹ (vốn có biên độ rất lớn) để làm lộ rõ tín hiệu tim thai (vốn rất yếu).
  - _Phương pháp:_ Tự động dò tìm các đỉnh nhịp tim mẹ, sau đó dựng dạng sóng trung bình của mẹ và thực hiện trừ khử (thuật toán trừ mẫu sóng trung bình). Tín hiệu thu được sau khi trừ sẽ chỉ còn nhịp tim thai và nhiễu nền.

- **Nội dung 3: Thiết kế và huấn luyện mô hình AI nhận diện nhịp tim thai**
  - _Nội dung thực hiện:_ Xây dựng thuật toán AI thông minh có khả năng tự động tìm chính xác từng nhịp tim thai trên một kênh đo duy nhất.
  - _Phương pháp:_ Thiết kế mạng nơ-ron học sâu dạng tích chập thời gian (TCN) với kích thước siêu nhẹ (dưới 120.000 tham số). Huấn luyện mô hình trên máy chủ GPU để quét qua tín hiệu và xuất ra biểu đồ xác suất đỉnh nhịp thai theo thời gian thực.

- **Nội dung 4: Xây dựng cơ chế tự động cảnh báo an toàn**
  - _Nội dung thực hiện:_ Giúp hệ thống tự nhận biết khi nào tín hiệu bị hỏng, lỏng dây đo hoặc bắt nhầm nhịp mẹ để tránh đưa ra kết quả sai lệch.
  - _Phương pháp:_ Tính toán các chỉ số đo độ rõ của tín hiệu. Khi phát hiện dây đo bị hở, cơ bụng co thắt mạnh hoặc tín hiệu quá mờ nhạt, hệ thống sẽ tự động bật cảnh báo và tạm ngừng hiển thị kết quả để đảm bảo an toàn y tế.

- **Nội dung 5: Tối ưu và thử nghiệm trên thiết bị nhúng thực tế**
  - _Nội dung thực hiện:_ Đưa thuật toán AI lên chip vi điều khiển nhỏ gọn và kiểm tra khả năng hoạt động trong điều kiện thực tế.
  - _Phương pháp:_ Nén mô hình AI (lượng tử hóa INT8) để vừa vặn với bộ nhớ nhỏ của chip vi điều khiển ESP32. Kết nối mạch phát tín hiệu thử nghiệm vào chip ESP32 để đo tốc độ nhận diện, kiểm tra độ ổn định và hiển thị nhịp tim thai trực tiếp lên màn hình nhỏ (OLED).

---

### 6. Mục tiêu/ kết quả/ đề xuất giải pháp nghiên cứu:

- **Mục tiêu:**
  - Mô hình đạt độ chính xác nhận diện nhịp tim thai F1 trên 95% trên tập dữ liệu chuẩn.
  - Thuật toán chạy mượt mà trên vi điều khiển nhỏ gọn, thời gian xử lý nhanh gấp nhiều lần thời gian thực.
- **Kết quả dự kiến:**
  - 01 phần mềm và mô hình AI hoàn chỉnh.
  - 01 mô hình mạch vi điều khiển thử nghiệm có màn hình hiển thị nhịp tim thai.
  - 01 bài báo khoa học báo cáo kết quả nghiên cứu.
  - 01 báo cáo tổng kết đề tài NCKH sinh viên cấp Trường.
- **Đề xuất giải pháp:**
  - Ứng dụng mô hình AI siêu nhẹ kết hợp bộ lọc đơn kênh giúp giảm tối đa giá thành thiết bị, mở ra khả năng làm miếng dán theo dõi tim thai tại nhà cho sản phụ.

---

### 7. Vai trò/ tính ứng dụng/ hiệu quả kinh tế - xã hội:

- **Tính ứng dụng:** Là bước đệm quan trọng để phát triển thành thiết bị đo tim thai dạng miếng dán không dây, gọn nhẹ, dễ dùng tại nhà.
- **Hiệu quả kinh tế - xã hội:**
  - Giúp các bà mẹ ở vùng sâu, vùng xa có thể tự theo dõi sức khỏe thai nhi, giảm bớt chi phí và công sức đi lại bệnh viện.
  - Giảm tải cho các bệnh viện phụ sản; chi phí linh kiện của hệ thống rất thấp (chỉ vài trăm nghìn đồng), dễ tiếp cận cho người dân.

---

### 8. Tài liệu tham khảo:

1. Clifford, G. D., et al. (2014). An open-access database for the evaluation of fetal heart rate monitoring algorithms. _Physiological Measurement_, 35(8), 1521.
2. Zhong, W., et al. (2018). A novel framework for fetal ECG extraction from single-channel abdominal ECG. _Physiological Measurement_, 39(4), 045004.
3. Asadi, S., & Ghaffari, A. (2026). A lightweight temporal deep architecture for fetal QRS detection. _IEEE Journal of Biomedical and Health Informatics_, 30(4), 3568-3577.
4. Silva, I., et al. (2013). Noninvasive fetal ECG: the PhysioNet/Computing in Cardiology Challenge 2013. _Computing in Cardiology_, 40, 149-152.

---

### 9. Kế hoạch thực hiện tiến độ dự kiến:

|    Tháng    | Công việc thực hiện                                        | Kết quả dự kiến                                                                           | Tiến độ |
| :---------: | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------- | :-----: |
| **10/2026** | Thu thập, xử lý và làm sạch bộ dữ liệu điện tim thai       | Bộ dữ liệu sạch sẵn sàng huấn luyện                                                       |   15%   |
| **11/2026** | Lập trình thuật toán lọc nhiễu và loại bỏ nhịp tim mẹ      | Module lọc tín hiệu hoạt động tốt                                                         |   30%   |
| **12/2026** | Thiết kế và huấn luyện mô hình AI nhận diện nhịp thai      | Mô hình đạt độ chính xác cao trên tập test                                                |   45%   |
| **01/2027** | Lập trình tính năng tự động cảnh báo tín hiệu nhiễu/lỗi    | Module tự ngắt khi tín hiệu xấu                                                           |   60%   |
| **02/2027** | Nạp mô hình lên bo mạch vi điều khiển và đo đạc thử nghiệm | Mạch phần cứng chạy thử nghiệm ổn định                                                    |   75%   |
| **03/2027** | Hoàn thiện toàn bộ hệ thống và viết tài liệu kỹ thuật      | Hoàn tất công trình theo kế hoạch nghiệm thu cấp khoa                                     |   90%   |
| **04/2027** | Báo cáo nghiệm thu cấp Khoa, chỉnh sửa theo góp ý          | Báo cáo nghiệm thu, chỉnh sửa và nộp công trình theo yêu cầu Hội đồng nghiệm thu cấp khoa |  100%   |
| **05/2027** | Báo cáo nghiệm thu cấp Trường, nộp hồ sơ giải thưởng       | Báo cáo cấp Trường; Chuẩn bị hồ sơ dự giải các cấp (nếu có)                               |    X    |

---

### 10. Dự trù kinh phí thực hiện:

| Diễn giải                                                                                                                                                                                                | Số tiền (đồng) |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------: |
| **1. Thuê máy chủ GPU đám mây phục vụ huấn luyện mô hình AI**<br>_(Chi phí thuê tài nguyên tính toán đám mây tốc độ cao trong quá trình thử nghiệm và tinh chỉnh mô hình)_                               |   1.400.000    |
| **2. Mua linh kiện, vi điều khiển và phụ kiện phục vụ thử nghiệm phần cứng**<br>_(Bao gồm: các bo mạch vi điều khiển ESP32, module màn hình hiển thị, mạch đo thử nghiệm, dây nối và linh kiện phụ trợ)_ |    850.000     |
| **3. In ấn poster khoa học khổ lớn và tài liệu, đóng cuốn báo cáo nghiệm thu**<br>_(In poster màu khổ A0 phục vụ báo cáo nghiệm thu, in ấn tài liệu và đóng cuốn báo cáo chính thức nộp Nhà trường)_     |    670.000     |
| **Tổng cộng**                                                                                                                                                                                            | **2.920.000**  |

- **Bằng chữ:** Hai triệu chín trăm hai mươi nghìn đồng.
- **Trong đó, đề nghị phía nhà trường hỗ trợ:** **2.920.000** đồng.
