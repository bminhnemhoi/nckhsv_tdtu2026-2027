# Sổ tay vận hành demo RelyFetal — v1 (lưu trữ, bản 8 tab)

> **⚠ TỆP LƯU TRỮ (8 tab, 13/09/2026) — đọc cảnh báo này trước khi dùng bất kỳ số nào bên dưới.**
> Bản đang dùng là `docs/HUONG_DAN_DEMO_v2.md`; v2 chỉ trỏ sang tệp này cho các mục 4(b), 5, 6(c)–(đ). Tệp này
> trước đây tên `HUONG_DAN_DEMO.md` và tự ghi "— v2" ở tiêu đề; thẩm định cuối 17/09 đã sửa các chỗ sau ngay trong tệp:
> - **Số STV ngoài miền đã rút:** +20,50 ms trên CinC, 0,13 ms (F1 ≥ 99,5) và 25,74 ms (F1 < 90) tính trên mẫu CinC
>   10 bản và mẫu 32 bản có a03 a04 a05 a08 là bản trùng dữ liệu huấn luyện. Số STV dùng được duy nhất là +0,33 ms
>   trong miền, n = 5 (`analysis/clinical_results.json → summary.ADFECGDB.stv_ba`).
> - **0,934 [0,872; 0,981]** là AUROC trong bản ghi của cổng 22 ca, LOSO, chỉ tính trên 11/22 chủ thể có đoạn xấu, chỉ ở
>   dạng phân tích, **chưa có trong demo**. Đèn trong demo là cổng 5 ca: 0,721 [0,517; 0,898] trên 5 bản CinC sạch khi
>   ghép với mô hình 5 ca; ghép với mô hình 22 ca chưa đo lại (`docs/HUONG_DAN_DEMO_v2.md` mục 4.1).
> - **Cổng không độc lập với mạng:** 12 chỉ số gồm 6 thuần tín hiệu, 4 tính trên nhịp mạng tìm ra, 2 là xác suất của
>   mạng (`fsqi/gate.py`). Câu "12 chỉ số cổ điển" và "tự biết khi nào không nên tin kết quả" đã sửa.
> - **Tự huấn luyện nhãn giả là −0,67** (−0,6746), không phải −0,68; p Wilcoxon của notch là **0,68** (0,679), không phải
>   0,70 — tính lại từ `adapt/adapt_results.json → per_record_cinc` trên 60 bản sạch.
> - **82,01 không đứng một mình:** luôn kèm 74,28 (PSD) · 80,72 (gate, quy tắc kế hoạch chọn, trượt Holm 0,051) ·
>   81,01 (gate4, cũng ghi trước, qua Holm 0,015) · trần 83,60.
> - Số kiểm thử và tên tab trong tệp này là của bản 8 tab; demo hiện tại xem `docs/HUONG_DAN_DEMO_v2.md`.

**Dành cho buổi gặp giảng viên hướng dẫn, 14/09/2026.**
Viết cho người đang căng thẳng: mỗi phần đọc được rời, lệnh copy dán được, câu nói có sẵn.

> **Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.**
> Mọi con số trong tài liệu này truy ngược được về một tệp JSON trên đĩa (nguồn ghi ngay cạnh số).
> Không có con số nào lấy từ 75 bản CinC — số chính là **60 bản sạch** (15 bản còn lại là bản sao của
> dữ liệu huấn luyện, xem Phần 4đ).

Cập nhật: 2026-09-13. Bản này thay cho bản ngày 12/09.

**Hai tab mới** — *Dữ liệu của nhóm* và *Tải dữ liệu mới* — đã có trong `demo/app.py` (kiểm lúc 13/09).
Tên ô trong tài liệu này chép đúng theo mã. Nếu trên màn hình có khác đôi chút thì nội dung thao tác vẫn đúng,
chỉ cần đọc theo vị trí — không có con số nào phụ thuộc vào tên tab.

Tám tab, từ trái sang phải: *Tín hiệu (5 tầng)* · *Chọn kênh — cả 4 kênh* · *Nhịp tim thai + đèn đoạn* ·
*So sánh với nhãn* · *Kết quả tổng hợp (60 bản sạch)* · **Dữ liệu của nhóm** · **Tải dữ liệu mới** · *Nhật ký (JSON)*.

Mục lục:
1. [Demo làm được gì](#1-demo-làm-được-gì)
2. [Khởi động và kiểm trước buổi gặp (15 phút)](#2-khởi-động-và-kiểm-trước-buổi-gặp-15-phút)
3. [Thao tác từng bước cho buổi gặp (6–8 phút)](#3-thao-tác-từng-bước-cho-buổi-gặp-68-phút)
4. [Dữ liệu của nhóm: ở đâu, định dạng gì, cho cô xem thế nào](#4-dữ-liệu-của-nhóm-ở-đâu-định-dạng-gì-cho-cô-xem-thế-nào)
5. [Đọc kết quả thế nào](#5-đọc-kết-quả-thế-nào)
6. [Nếu cô muốn test trên dữ liệu chưa có](#6-nếu-cô-muốn-test-trên-dữ-liệu-chưa-có)
7. [Kế hoạch dự phòng](#7-kế-hoạch-dự-phòng)
8. [Những gì KHÔNG được làm trong demo](#8-những-gì-không-được-làm-trong-demo)

---

## 1. Demo làm được gì

Một bảng, đọc từ trái sang phải: **làm được gì** → **để làm gì** → **giới hạn ở đâu**.

| Năng lực | Để làm gì | Giới hạn |
|---|---|---|
| **Đọc tín hiệu thô nhiều định dạng** — `.edf`, `.hea`+`.dat`, `.csv`, `.npy`, `.txt`, mảng numpy (`demo/core.py: load_record`) | Mở được dữ liệu từ PhysioNet, từ Silesia, và từ file cô đưa mà không phải viết mã | Không đọc được ảnh/giấy in CTG, không đọc file có mã hoá riêng của hãng máy |
| **Lọc + khử điện tim mẹ** — Butterworth 10–60 Hz pha-không, notch 50 Hz, hạ mẫu về 250 Hz, khử mẹ bằng mẫu trung vị + tỉ lệ bình phương tối thiểu từng nhịp | Làm nổi nhịp thai (biên độ nhỏ hơn nhịp mẹ nhiều lần) trước khi đưa vào mô hình | Cần ít nhất 3 nhịp mẹ dò được trong bản ghi, nếu không thì bỏ qua bước khử mẹ (`fqrs_model.cancel_maternal`) |
| **Chọn kênh bụng mù nhãn — 2 quy tắc**: `peakprob` (mặc định) và `PSD` (của Power-MF) | Thiết bị thật thường chỉ đọc được 1 kênh tốt; hệ thống phải tự biết chọn kênh nào mà **không nhìn nhãn** | `peakprob` là **lựa chọn hậu kiểm**. Quy tắc khai báo trước là `gate` (trượt Holm, p 0,051) và `gate4` (sống sót Holm, p 0,015). Phải nói rõ điều này khi trình bày |
| **Phát hiện nhịp thai** — FetalQRS-TCN, 113 481 tham số, chuỗi-sang-chuỗi, ngưỡng 0,75 lưu trong checkpoint | Ra danh sách thời điểm từng nhịp tim thai | Một kênh, CPU; F1 mức chủ thể **97,56** trên 22 chủ thể trong miền, nhưng ngoài miền (60 bản CinC sạch) chỉ 74,28 (PSD) · 80,72 (gate) · 81,01 (gate4) · **82,01** (peakprob, hậu kiểm) |
| **Tính nhịp tim thai theo thời gian** — median RR trong từng cửa sổ 4 s | Cho thấy đường fHR giống thứ cô quen nhìn trên máy monitor | Đây là fHR suy ra từ nhịp phát hiện; nếu mô hình bám nhịp mẹ thì đường này **vẫn trông đẹp** mà sai (bản a02) |
| **Chấm điểm tin cậy từng đoạn 4 s và từ chối** — cổng học (GBM, 12 chỉ số: 6 thuần tín hiệu, 4 trên nhịp mạng tìm ra, 2 là xác suất của mạng — không độc lập với mạng) hoặc luật cứng 4 thành phần | Đây là phần quan trọng nhất của đề tài: khi thấy dấu hiệu xấu, hệ thống nói "đoạn này đừng tin tôi" (không phải lần nào cũng thấy) | Cổng đang dùng trong demo **hiệu chuẩn trên mô hình 5 ca ADFECGDB**; cổng 22 ca mới có kết quả phân tích, chưa xuất được tệp |
| **So sánh với nhãn nếu có** — Se, PPV, F1, jitter, TP/FP/FN, ghép ±50 ms | Để cô kiểm chứng ngay trên màn hình, không phải tin lời kể | Chỉ có với bản ghi có nhãn. Nhãn Silesia B1 là **nhãn gián tiếp** (tác giả khử mẹ rồi đo), nên F1 ở đó là "đồng ý với nhãn gián tiếp" |
| **Xem dữ liệu của nhóm** — tab *Dữ liệu của nhóm*: chọn bộ → bảng từng bản ghi → nút *Xem tín hiệu thô* (10 giây đầu, tất cả kênh, kèm vạch nhãn) | Chứng minh dữ liệu là thật, có trên đĩa, tải từ nguồn công khai | Chỉ liệt kê bộ đã có trên đĩa máy này |
| **Chạy trên dữ liệu mới tải lên** — tab *Tải dữ liệu mới* | Cô đưa file gì cũng thử được ngay trong buổi | Kết quả ngoài miền thường kém hơn nhiều; không có nhãn thì không có F1 |

**Demo KHÔNG làm những việc sau** (nói thẳng câu này nếu bị hỏi):

* **Không chẩn đoán.** Không kết luận thai suy, không cảnh báo lâm sàng, không phân loại bệnh.
* **Không phải thiết bị y tế.** Chưa qua bất kỳ kiểm định nào.
* **Không đo được STV tin cậy.** Số STV dùng được duy nhất: chệch +0,33 ms trên ADFECGDB, n = 5
  (`analysis/clinical_results.json → summary.ADFECGDB.stv_ba`). Các số STV ngoài miền cũ (+20,50 ms trên CinC;
  0,13 ms khi F1 ≥ 99,5; 25,74 ms khi F1 < 90) **đã rút** — mẫu CinC 10 bản và mẫu 32 bản có bản trùng dữ liệu huấn luyện.
  → **Không dùng làm máy đo STV độc lập.**
* **Không chạy thời gian thực từ máy đo.** Demo đọc file đã ghi sẵn. Tốc độ đủ nhanh về lý thuyết
  (4,35 ms cho một cửa sổ 4 s trên CPU) nhưng chưa có đường nối tới thiết bị.
* **Không tự động phát hiện cô đưa nhầm dữ liệu người lớn / dữ liệu khác loại.** Cổng tin cậy sẽ báo đỏ, nhưng đó là suy luận gián tiếp.

---

## 2. Khởi động và kiểm trước buổi gặp (15 phút)

Làm đúng theo thứ tự này, bắt đầu **15 phút** trước giờ hẹn.

### 2.1. Mở terminal đúng chỗ

Mở **Windows PowerShell**, gõ:

```powershell
cd D:\NCKHSV2026-2027
$env:PYTHONIOENCODING = "utf-8"
$env:RELYFETAL_THREADS = "4"
```

Dòng `PYTHONIOENCODING` để tiếng Việt in ra terminal không lỗi. Dòng `RELYFETAL_THREADS` đặt số luồng CPU cho torch.

### 2.2. Kiểm nhanh KHÔNG cần trình duyệt (≈ 1 phút, làm trước)

```powershell
python demo/run_check.py --only r01,a09,a02 --out demo_check_3ban --threads 2
```

* In ra terminal bảng 3 bản ghi (kênh chọn, F1, Se, PPV, đèn học/đèn luật, tỉ lệ bám nhịp mẹ, thời gian ms).
* Ghi kết quả vào `demo/results/demo_check_3ban.json` và `.log`.
* Thời gian thật: lần chạy 5 bản (`demo_check_showcase.json`) mất **10,7 s** với 2 luồng; 3 bản nhanh hơn.

> **CẢNH BÁO:** **KHÔNG** dùng `--out demo_check_showcase`. Tên đó là tệp dự phòng 5 bản minh hoạ
> (`demo/results/demo_check_showcase.json`) — chạy lại sẽ **ghi đè** và mất số dự phòng đang dùng cho Phần 3 và Phần 5.
> Muốn chạy lại đúng 5 bản thì đặt tên khác, ví dụ `--out demo_check_truoc_buoi`.

### 2.3. Khởi động giao diện

```powershell
python demo/app.py
```

**Thời gian chờ thật:**

| Mốc | Thời gian thật đo được |
|---|--:|
| Terminal in `RelyFetal demo: http://127.0.0.1:7860` | 5–15 s (lần đầu lâu hơn vì torch/mne nạp chậm) |
| Mở trang → trang tự phân tích **r01** xong, hiện đủ 4 thẻ số | **12,9 s** kể cả nạp trang lần đầu (`demo/screenshots/screenshots.json` → `first_result_s`) |
| Mỗi bản ghi 60 s bấm *Phân tích* sau đó | ≈ 3,0–3,5 s |
| Bản ghi 300 s (r01, B2_03) | ≈ 6 s |

### 2.4. Biết chắc đã chạy đúng

Mở trình duyệt vào **http://127.0.0.1:7860**. Đã chạy đúng khi thấy **cả ba** dấu hiệu:

1. Dòng trạng thái: *"Đã phân tích **r01** (EDF, 300 s, 4 kênh) — kênh **4** (auto (peakprob)) …"*
2. Bốn thẻ số: **fHR 129 bpm** · **kênh 4 / 4** · **đèn CAO (xanh)** · thời gian xử lý.
3. Biểu đồ 5 tầng hiện ở tab *Tín hiệu (5 tầng)*.

Nếu thiếu một trong ba → sang Phần 7.

### 2.5. Chuẩn bị màn hình trước khi cô vào

* Để nguyên tab *Tín hiệu (5 tầng)* của r01.
* Ô *Kênh bụng* = **Tự động — peakprob (mặc định)**; ô *Đèn tin cậy* = **Học (GBM, 12 chỉ số / đoạn 4 s)**.
* Mở sẵn thư mục `demo/screenshots/` ở một cửa sổ khác (dự phòng).
* Mở sẵn `benchmark_dpss\pcdb\a09.hea` bằng Notepad ở một cửa sổ khác (cho Phần 4c cách 2).

### 2.6. Tắt và khởi động lại khi kẹt

| Việc | Lệnh |
|---|---|
| Tắt demo | `Ctrl + C` trong terminal đang chạy `app.py` |
| Cổng 7860 bận | `$env:RELYFETAL_PORT = "7870"; python demo/app.py` → mở http://127.0.0.1:7870 |
| Máy chậm / treo | `Ctrl + C`, rồi `$env:RELYFETAL_THREADS = "2"; python demo/app.py` |
| Tắt việc tự chạy r01 khi mở trang | `$env:RELYFETAL_AUTORUN = "0"` trước khi chạy `app.py` |

Khởi động lại mất đúng như mục 2.3 — **nói với cô "cho em 15 giây"**, đừng im lặng chờ.

---

## 3. Thao tác từng bước cho buổi gặp (6–8 phút)

Thứ tự bắt buộc: **r01 → a09 (hai quy tắc chọn kênh) → a02 → tab *Dữ liệu của nhóm* → tab *Tải dữ liệu mới*.**
Nếu còn thời gian mới thêm B2_03 và a27 (Phần 7 có ảnh sẵn).

Thời gian trong cột đầu là **thời gian thật đã đo**, nguồn: `demo/screenshots/screenshots.json` (đồng hồ trong trình duyệt,
2 luồng CPU, máy đang chạy việc khác nên là **cận trên**) và `demo/results/demo_check_showcase.json` (thời gian riêng phần mô hình).

| THỜI ĐIỂM | BẤM GÌ | NÓI GÌ |
|---|---|---|
| 0:00–0:40 | Không bấm. Màn hình đang là r01, tab *Tín hiệu (5 tầng)*. | "Đề tài làm một việc hẹp: từ **một** kênh điện tim ổ bụng của mẹ, tìm vị trí từng nhịp tim thai." · "Và báo khi thấy dấu hiệu kết quả chưa đáng tin — không phải lần nào cũng thấy." · "Mô hình 113 nghìn tham số, chạy CPU, huấn luyện trên 22 sản phụ." |
| 0:40–1:10 | Chỉ tay vào thẻ **Kênh được chọn** (kênh 4/4) và thẻ **Đèn tin cậy** (CAO, 0,999). | "Đây là r01: 5 phút, 4 kênh bụng, nhãn lấy từ điện cực da đầu thai nhi." · "Checkpoint dùng ở đây là fold **chưa từng thấy** sản phụ này." · "Bốn kênh đều ≈ 0,998 nên kênh nào cũng tốt." |
| 1:10–1:40 | Trong tab *Tín hiệu (5 tầng)*: kéo chuột phóng to khoảng 3 giây bất kỳ. Chỉ lần lượt tầng 2 → 3 → 4 → 5. | "Tầng 2: vạch đỏ là nhịp **mẹ**, lớn gấp nhiều lần nhịp thai." · "Tầng 3: sau khi khử mẹ chỉ còn nhịp thai nhỏ." · "Tầng 4: xác suất của mô hình, ngưỡng 0,75 cố định." · "Tầng 5: chấm xanh là đúng." |
| 1:40–2:00 | Bấm tab **So sánh với nhãn**. | "F1 **99,92**, Se 100,00, PPV 99,84, lệch thời điểm 1,47 ms." · "Đây là bản dễ. Con số thật của đề tài là **97,56** trên 22 chủ thể, không phải 100." |
| 2:00–2:20 | Ô *Bản ghi minh hoạ* → chọn **a09** → bấm **Phân tích**. Chờ ≈ **3,0 s**. | "Bộ dữ liệu khác, máy khác, chưa từng huấn luyện — CinC 2013." · "Bản này là ví dụ cách chọn kênh cũ **chọn sai kênh**." |
| 2:20–2:50 | Bấm tab **Chọn kênh — cả 4 kênh**. Chỉ vào cột điểm và cột F1. | "peakprob cho kênh 1 điểm **0,990**, ba kênh kia 0,905–0,932 → chọn kênh 1, **F1 94,25**." · "Kênh 2 chỉ F1 **19,35** — đúng là kênh mà quy tắc PSD sẽ chọn." |
| 2:50–3:20 | Ô *Kênh bụng* → **Tự động — PSD (Power-MF)** → **Phân tích**. Chờ ≈ **3,1 s**. Sau đó **đổi lại peakprob**. | "PSD chọn kênh 2, F1 rơi xuống 19,35, đèn chuyển **THẤP (đỏ)**." · "Đèn bắt được lỗi này — nhưng peakprob tránh được ngay từ đầu." |
| 3:20–3:40 | Đứng yên, nói phần liêm chính. Mở tab *Kết quả tổng hợp (60 bản sạch)* nếu cô muốn xem bảng. | "Trên 60 bản CinC sạch, peakprob hơn PSD **+7,73 điểm** (KTC 95 % +3,82…+12,41, p Holm 0,0039)." · "**Nhưng** đây là quy tắc em chọn **sau khi** đã nhìn F1. Quy tắc em khai báo trước là *gate*, và gate trượt Holm (p 0,051)." · "Quy tắc *gate4* trong cùng hồ khai báo trước thì sống sót Holm, p 0,015 — đó mới là kết quả trung thực mạnh nhất của em." |
| 3:40–4:10 | Chọn **a02** → **Phân tích**. Chờ ≈ **3,1 s**. Chỉ vào thẻ *Đèn tin cậy*. | "Đây là kiểu lỗi nguy hiểm nhất." · "Mô hình bám vào **phần dư nhịp mẹ** và báo một chuỗi nhịp rất đều ở 130 bpm — trông y như thai." · "Đèn báo **THẤP (đỏ)**, lý do ghi rõ: 78 % nhịp trùng đỉnh R mẹ, trong khi ngẫu nhiên chỉ 13–22 %." |
| 4:10–4:35 | Bấm tab **Nhịp tim thai + đèn đoạn**, rồi tab **Chọn kênh**. | "Đường fHR của mô hình đẹp nhưng lệch khỏi đường nhãn." · "Và peakprob **không cứu được** bản này: kênh 1 có F1 75,88 nhưng điểm thấp hơn kênh 2." · "Em cho cô xem cả trường hợp quy tắc của em thất bại." |
| 4:35–5:30 | Bấm tab **Dữ liệu của nhóm**. Ô *Bộ dữ liệu* → chọn **"ADFECGDB — 5 bản (PhysioNet, nhãn da đầu)"**, rồi **"CinC 2013 set-a — 60 bản SẠCH (ngoài miền)"**. Ở ô *Bản ghi muốn xem tín hiệu thô* chọn **a09** → bấm **Xem tín hiệu thô**. | "Dữ liệu nhóm đang có: 5 bản ADFECGDB nhãn điện cực da đầu, 22 bản Silesia, 75 bản CinC." · "Bảng này đọc thật từ tệp trên đĩa: đường dẫn, định dạng, tần số, độ dài, số kênh, số nhịp trong nhãn, nguồn nhãn." · "Nút này vẽ 10 giây đầu của tất cả kênh bụng, vạch đỏ là nhãn nhịp thai — để cô thấy đây là tín hiệu thật." |
| 5:30–6:00 | Vẫn ở tab *Dữ liệu của nhóm*, ô *Bộ dữ liệu* → **"CinC 2013 set-a — 15 bản NHIỄM (bản sao ADFECGDB)"**. | "15 bản này là bản sao nguyên văn của dữ liệu huấn luyện — em **loại** khỏi mọi con số." · "Như ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014], set-a có chứa bản ghi ADFECGDB." · "Việc của nhóm em là xác định **đúng 15 bản nào** và **đo mức thổi phồng** — tới +7,18 điểm." |
| 6:00–7:00 | Bấm tab **Tải dữ liệu mới**. Ô *Tệp bản ghi* → chọn `demo\assets\vidu_tai_len.csv`. Ô *Tần số lấy mẫu (Hz)* → **1000**. Ô *Nhãn tham chiếu (tuỳ chọn)* → chọn `vidu_tai_len_nhan.csv`. Bấm **Phân tích**. | "Cô đưa file gì em cũng chạy được ngay: EDF, WFDB, CSV, NPY." · "Chỉ cần cho em biết tần số lấy mẫu; hệ thống tự đưa về 1000 Hz." · "Nói rõ: tệp ví dụ này em **cắt từ a09** để thử luồng tải lên, **không phải** dữ liệu mới." · "Nếu file không có nhãn thì vẫn ra nhịp và đèn tin cậy, chỉ không có F1." |
| 7:00–7:40 | Không bấm. | "Tóm lại: một kênh, F1 mức chủ thể 97,56 trên 22 ca — kém Power-MF **4 kênh** 1,27 điểm (chưa có ý nghĩa thống kê), hơn Power-MF **1 kênh** 10,85 điểm." · "Ngoài miền còn kém: 60 bản CinC sạch chỉ 74,28 với quy tắc cũ, 80,72 với quy tắc kế hoạch chọn, 81,01 với gate4, 82,01 với quy tắc hậu kiểm. Bốn cách thích nghi miền em thử đều thất bại, nguyên nhân **chưa xác định**." · "Vì thế cổng từ chối là phần quan trọng nhất." · "Còn thiếu: một bộ dữ liệu có nhãn fQRS thật ngoài những gì đã dùng — hiện không có bộ công khai nào." |

**Nếu cô cắt ngang và chỉ còn 3 phút:** làm r01 (0:40–2:00) → a09 hai quy tắc (2:00–3:20) → kết (7:00–7:40).

---

## 4. Dữ liệu của nhóm: ở đâu, định dạng gì, cho cô xem thế nào

### (a) Bảng dữ liệu — đường dẫn thật trên máy

Gốc repo: `D:\NCKHSV2026-2027`

| Bộ dữ liệu | Đường dẫn tuyệt đối | Số bản ghi | Định dạng tệp | Tần số | Độ dài | Nguồn nhãn | Giấy phép / nguồn tải | Dùng để làm gì |
|---|---|--:|---|--:|---|---|---|---|
| **ADFECGDB** (PhysioNet) | `D:\NCKHSV2026-2027\model\data\adfecgdb` | 5 (r01, r04, r07, r08, r10) | `.edf` + `.edf.qrs` (15 MB) | 1000 Hz | 5 phút | **TRỰC TIẾP** — điện cực da đầu thai nhi | ODC-BY v1.0, `physionet.org/content/adfecgdb/1.0.0/` | Huấn luyện (nằm trong 22 chủ thể) + bản minh hoạ r01 |
| **CinC 2013 set-a** | `D:\NCKHSV2026-2027\benchmark_dpss\pcdb` | 75 (`a01`…`a75`) — **60 sạch**, 15 nhiễm, 7 nhãn sai | `.hea` + `.dat` + `.fqrs` (35 MB) | 1000 Hz | 60 s, 4 kênh | Người chấm độc lập của ban tổ chức | ODC-BY v1.0, `physionet.org/content/challenge-2013/1.0.0/` (set-a) | **Kiểm tra ngoài miền** — số chính của đề tài |
| **Silesia B1 — thai kỳ** | `D:\NCKHSV2026-2027\model\data\silesia\extracted\Data Records\B1_Pregnancy_dataset\B1_Pregnancy_01..10` | 10 | `.ecg` (int16 big-endian, 8 cột) + `.txt` nhãn | 500 Hz (nhãn 500 Hz) | 20 phút | **GIÁN TIẾP** — tác giả khử ECG mẹ rồi đo, chuyên gia duyệt | figshare **CC0 1.0**; bài báo Matonia và cs., *Sci Data* 7:200 (2020), DOI 10.1038/s41597-020-0538-z | Huấn luyện (trong 22 chủ thể) |
| **Silesia B2 — chuyển dạ** | `…\Data Records\B2_Labour_dataset\B2_Labour_01..12` | 12 trên đĩa, **dùng 7** | `.ecg` bụng 500 Hz + `B2_dFECG_XX.ecg` 1000 Hz + `.txt` nhãn | 500 Hz bụng / 1000 Hz nhãn | 5 phút | **TRỰC TIẾP** — điện cực da đầu | như trên (CC0 1.0) | Huấn luyện (7 bản) + bản minh hoạ B2_03 |
| NIFEADB | `D:\NCKHSV2026-2027\model\data\nifeadb` (178 MB) | — | WFDB | — | — | **KHÔNG có chú thích thai** | ODC-BY v1.0, PhysioNet | Không dùng được để đánh giá |
| NInFEA | `D:\NCKHSV2026-2027\model\data\ninfea` (16 MB) | — | — | — | — | **Chỉ có Doppler** | PhysioNet | Không dùng được để đánh giá |
| NSTDB (nhiễu) | `D:\NCKHSV2026-2027\model\data\nstdb` (5,6 MB) | 3 bản nhiễu (`bw`, `em`, `ma`) | WFDB | — | — | (nhiễu chuẩn, không có nhãn thai) | ODC-BY v1.0, PhysioNet | Thí nghiệm SNR |

**22 chủ thể huấn luyện = 5 ADFECGDB + 10 Silesia B1 + 7 Silesia B2.**
5 bản Silesia B2 bị **loại** vì trùng với PhysioNet: `B2_01=r01`, `B2_02=r10`, `B2_07=r04`, `B2_10=r07`, `B2_11=r08`
(`demo/core.py: SILESIA_DUP`).

Tải lại nếu mất dữ liệu:
```powershell
python model/download_data.py --root model/data --only adfecgdb
python model/download_silesia.py
```

### (b) Định dạng tệp — giải thích cho người không chuyên

**EDF** (*European Data Format*) là định dạng chuẩn của máy đo sinh học: **một tệp duy nhất** chứa cả phần mô tả
(tên kênh, tần số, thời gian ghi) lẫn số liệu. Đọc bằng thư viện `mne`. ADFECGDB dùng EDF; kèm tệp nhãn `.edf.qrs`.

Lưu ý quan trọng về ADFECGDB: bên trong mỗi tệp `.edf` có **5 kênh** — `Direct_1` là fECG lấy **trực tiếp từ điện cực
da đầu thai nhi** (đây là nguồn sinh ra nhãn) và `Abdomen_1..4` là 4 đạo trình **bụng** mẹ. Demo **bỏ hẳn kênh `Direct_1`**
khi phân tích (`demo/core.py: load_record`, lọc tên kênh chứa `direct`). Nếu cho mô hình nhìn kênh trực tiếp thì bài toán
không còn ý nghĩa. Nói câu này nếu cô hỏi "sao biết là 4 kênh chứ không phải 5".

**WFDB** là định dạng của PhysioNet, tách làm **nhiều tệp cùng tên gốc**:

* `a09.hea` — **header**, tệp văn bản thuần, mở bằng Notepad đọc được ngay;
* `a09.dat` — số liệu nhị phân (int16);
* `a09.fqrs` — nhãn vị trí từng nhịp tim thai.

**Vì sao có cả hai?** Vì hai nhóm tác giả khác nhau công bố theo hai chuẩn khác nhau: bộ ADFECGDB phát hành dạng EDF,
bộ CinC 2013 phát hành dạng WFDB. Nhóm không đổi định dạng gốc — `demo/core.py: load_record()` đọc được cả hai, giữ nguyên tệp
như lúc tải về, để ai muốn kiểm tra thì so trực tiếp với bản trên PhysioNet.

**In nguyên văn một header thật** — tệp `D:\NCKHSV2026-2027\benchmark_dpss\pcdb\a09.hea` (5 dòng, đã đọc trực tiếp từ đĩa):

```
a09 4 1000 60000
a09.dat 16 10/uV 12 0 57 -11458 0 AECG1
a09.dat 16 10/uV 12 0 3 14104 0 AECG2
a09.dat 16 10/uV 12 0 -31 -732 0 AECG3
a09.dat 16 10/uV 12 0 -18 25735 0 AECG4
```

Giải thích từng dòng:

**Dòng 1 — dòng mô tả bản ghi:** `a09 4 1000 60000`

| Ô | Giá trị | Nghĩa |
|---|---|---|
| 1 | `a09` | tên bản ghi |
| 2 | `4` | bản ghi có **4 tín hiệu** (4 kênh điện cực trên bụng mẹ) |
| 3 | `1000` | **1000 mẫu mỗi giây** trên mỗi kênh |
| 4 | `60000` | tổng **60 000 mẫu** → 60 000 / 1000 = **60 giây** |

**Dòng 2–5 — mỗi dòng mô tả một kênh:** `a09.dat 16 10/uV 12 0 57 -11458 0 AECG1`

| Ô | Giá trị | Nghĩa |
|---|---|---|
| 1 | `a09.dat` | số liệu nằm trong tệp này |
| 2 | `16` | định dạng số: số nguyên 16 bit |
| 3 | `10/uV` | **hệ số quy đổi**: 10 đơn vị số = 1 micro-vôn (tức 1 đơn vị số = 0,1 µV) |
| 4 | `12` | bộ biến đổi A/D có độ phân giải 12 bit |
| 5 | `0` | giá trị số ứng với 0 vôn |
| 6 | `57` | giá trị mẫu **đầu tiên** của kênh này (dùng để kiểm tra đọc đúng) |
| 7 | `-11458` | **checksum** — tổng kiểm tra; đọc sai một byte là lệch ngay |
| 8 | `0` | kích thước khối (0 = không chia khối) |
| 9 | `AECG1` | tên kênh: *Abdominal ECG 1* — kênh bụng số 1 |

Câu nói gợi ý: *"Header là tệp văn bản thường, cô mở Notepad là đọc được. Nó ghi rõ 4 kênh, 1000 Hz, 60 giây,
và có checksum — nếu em sửa số liệu thì checksum lệch ngay."*

### (c) Ba cách cho cô xem dữ liệu, xếp theo độ tiện

**Cách 1 — ngay trong demo (nhanh nhất, dùng trong buổi):**
Tab **Dữ liệu của nhóm** → ô ***Bộ dữ liệu***, 5 lựa chọn đúng như trên màn hình:

* `ADFECGDB — 5 bản (PhysioNet, nhãn da đầu)`
* `Silesia B2 — chuyển dạ (12 bản trên đĩa, nhãn da đầu)`
* `Silesia B1 — thai kỳ (10 bản, nhãn gián tiếp)`
* `CinC 2013 set-a — 60 bản SẠCH (ngoài miền)`
* `CinC 2013 set-a — 15 bản NHIỄM (bản sao ADFECGDB)`

Bảng bên dưới hiện 9 cột, **đọc thật từ tệp trên đĩa**: Bản ghi · Đường dẫn trên đĩa · Định dạng · fs gốc (Hz) ·
Dài (s) · Số kênh bụng · Số nhịp trong nhãn · Nguồn nhãn · Ghi chú.
Thứ tự trên màn hình: ô **Bộ dữ liệu** → **hộp mô tả định dạng** của bộ đang chọn (kèm 8 dòng đầu của một tệp header
`.hea` / tệp nhãn `.txt` **in nguyên văn từ đĩa**) → **bảng 9 cột** → ô ***Bản ghi muốn xem tín hiệu thô*** +
nút ***Xem tín hiệu thô*** → hình **10 giây đầu, tất cả kênh bụng xếp chồng, vạch đỏ = nhãn nhịp thai** → chú thích số
(tần số, số kênh, số nhịp trong 10 s) → hộp ***Cách đọc hình này*** ở dưới cùng.

Thời gian đo thật trên máy của nhóm (13/09/2026, 3 luồng CPU): đổi bộ dữ liệu **1,1–2,4 s** (ADFECGDB chậm nhất vì phải
mở 5 tệp EDF; lần sau có nhớ đệm nên tức thì), vẽ tín hiệu thô **1,1–1,3 s** qua HTTP, **2,6–4,1 s** tính cả trình duyệt.

**Cách 2 — mở tệp header bằng Notepad (chứng minh dữ liệu là thật):**
```
notepad D:\NCKHSV2026-2027\benchmark_dpss\pcdb\a09.hea
```
Nội dung đúng như đã in ở mục (b). Nói: *"Đây là tệp gốc tải từ PhysioNet, em không sửa gì."*
Với ADFECGDB, tệp `.edf` là nhị phân nên Notepad không đọc được — dùng Cách 1 hoặc chỉ vào thư mục
`D:\NCKHSV2026-2027\model\data\adfecgdb` cho thấy 5 cặp `.edf` + `.edf.qrs`.

**Cách 3 — nếu cô muốn cầm file về:**

| Bộ | Trả lời |
|---|---|
| ADFECGDB | Tải công khai: `physionet.org/content/adfecgdb/1.0.0/` — giấy phép ODC-BY v1.0 (bắt buộc ghi nguồn). Cô tự tải được, không cần xin ai. |
| CinC 2013 set-a | Tải công khai: `physionet.org/content/challenge-2013/1.0.0/` — ODC-BY v1.0. |
| NIFEADB, NInFEA, NSTDB | Tải công khai trên PhysioNet, ODC-BY v1.0. |
| Silesia (B1, B2) | Bản ghi trên figshare ghi **CC0 1.0** (miền công cộng), bài báo CC BY 4.0 — theo `model/data/silesia/README_silesia.md`. Cô tải trực tiếp từ figshare (DOI collection 10.6084/m9.figshare.c.4740794). |
| **Bất kỳ bộ nào nếu cô hỏi "em gửi file cho cô được không"** | **Trả lời: "Em phải kiểm giấy phép trước rồi gửi cô đường dẫn tải chính thức."** An toàn nhất là gửi **đường dẫn nguồn**, không phát tán bản sao — kể cả với bộ có vẻ tự do. |

### (d) Cảnh báo bắt buộc: 15 bản CinC nhiễm

**Nếu cô mở trúng một trong 15 bản dưới đây, phải nói ngay:**

> *"Bản này trùng với dữ liệu huấn luyện của em — không được coi là ngoài miền."*

Đủ 15 mã: **a03 · a04 · a05 · a08 · a12 · a13 · a14 · a15 · a17 · a19 · a20 · a22 · a23 · a24 · a25**

Cách chồng lấn (mỗi bản ADFECGDB xuất hiện **đúng 3 lần**, cắt theo cửa sổ 0–60 s / 120–180 s / 240–300 s):

| Bản gốc ADFECGDB | Xuất hiện trong CinC set-a thành |
|---|---|
| r01 | a04, a05, a22 |
| r04 | a13, a20, a25 |
| r07 | a19, a23, a24 |
| r08 | a08, a15, a17 |
| r10 | a03, a12, a14 |

Bằng chứng đo được: NCC = **1,0000** trên cả 4 kênh đúng thứ tự, lệch RR = **0,0 ms**.
Đối chứng dương (trùng đã biết B2 ↔ PhysioNet, cùng sản phụ nhưng xử lý khác) chỉ đạt 0,856–0,984;
60 bản còn lại tối đa 0,62.

**Cách phát biểu đúng** (học thuộc câu này):

> *"Như ban tổ chức đã ghi nhận [Silva và cs., CinC 2013;40:149-152, Bảng 1 'Abdominal and Direct FECG — 25';
> Clifford và cs., Physiol Meas 2014;35:1521, DOI 10.1088/0967-3334/35/8/1521], set-a có chứa bản ghi ADFECGDB.
> Chúng tôi xác định bằng đo lường đúng 15 bản nào và mức thổi phồng là bao nhiêu."*

Mức thổi phồng đo được: m5 **+7,18** · m12 **+6,41** · m22 **+5,12** · oracle **+3,27** điểm F1.
Ghi chú đọc bài của chính nhóm (`bang_baihoc` trang 13 và 20) đã nhắc cảnh báo này mà nhóm **bỏ sót**.

---

## 5. Đọc kết quả thế nào

Đọc theo đúng thứ tự trên màn hình: thẻ số trên cùng → rồi từng tab.

### 5.1. Bốn thẻ số trên cùng

| Thẻ | Nó là gì | Đọc thế nào | Ngưỡng tốt/xấu | Câu nói mẫu |
|---|---|---|---|---|
| **fHR trung bình** | Nhịp tim thai trung bình, tính bằng median RR trong từng cửa sổ 4 s | Số bpm + số nhịp phát hiện / độ dài bản ghi | Bình thường **110–160 bpm**. Nếu ra ≈ 70–90 bpm → mô hình đang bám **nhịp mẹ** | "129 nhịp mỗi phút, 645 nhịp trong 300 giây — đúng dải thai bình thường." |
| **Kênh được chọn** | Kênh nào được chọn, theo quy tắc nào, điểm từng kênh (kênh chọn tô xanh), kèm F1 từng kênh nếu có nhãn | So điểm 4 kênh với nhau, **không** so điểm tuyệt đối giữa các bản ghi | Điểm peakprob chênh rõ (ví dụ 0,990 so với 0,905) → chọn kênh tự tin. Bốn kênh gần bằng nhau → chọn kênh nào cũng tương đương | "Bốn kênh đều 0,998 nên kênh nào cũng tốt." / "Kênh 1 vượt hẳn nên chọn kênh 1." |
| **Đèn tin cậy** | Mức (CAO/TRUNG BÌNH/THẤP), điểm 0–1, lý do bằng chữ, và dòng cảnh báo vàng | Đọc **lý do** chứ đừng chỉ đọc điểm | Cổng học: > 70 % đoạn xanh và ≤ 30 % đoạn đỏ → **CAO**. Cổng luật: điểm ≥ 0,75 → CAO, ≥ 0,45 → TRUNG BÌNH, dưới nữa → THẤP | "Đèn CAO, 75/75 đoạn xanh." / "Đèn THẤP vì 78 % nhịp trùng đỉnh R mẹ." |
| **Thời gian xử lý** | Thời gian cho kênh đã chọn, thời gian cho cả 4 kênh (chi phí thật của quy tắc chọn kênh), và tên checkpoint | Con số "cả 4 kênh" mới là chi phí thật khi dùng peakprob | Bản 60 s: ≈ 0,12 s một kênh, ≈ 0,42–0,51 s cả 4 kênh. Bản 300 s: ≈ 0,42–0,44 s một kênh, ≈ 1,8–2,0 s cả 4 kênh | "peakprob phải chạy mô hình 4 lần thay vì 1 — em hiện cả hai con số để không giấu chi phí." |

Dòng cảnh báo vàng dưới thẻ *Đèn tin cậy* ghi **"cổng hiệu chuẩn trên mô hình 5 ca"** — **đừng bỏ qua**, đó là điểm liêm chính:
cổng trong demo huấn luyện trên 1 500 đoạn ADFECGDB với mô hình 5 ca, không phải cổng 22 ca.

### 5.2. Tab *Tín hiệu (5 tầng)*

| Tầng | Nó là gì | Đọc thế nào | Cái gì là bất thường |
|---|---|---|---|
| 1 — **Thô** | Tín hiệu gốc từ điện cực bụng, chưa xử lý | Nhìn thấy sóng lớn đều đặn = nhịp **mẹ**; nhịp thai hầu như không thấy | Đường phẳng hoặc nhiễu kín → điện cực hỏng |
| 2 — **Sau lọc 10–60 Hz** (vạch đỏ = nhịp mẹ) | Đã lọc băng thông + notch 50 Hz, hạ mẫu về 250 Hz | Vạch đỏ phải khớp với các đỉnh lớn | Vạch đỏ đặt sai chỗ → khử mẹ sẽ hỏng theo |
| 3 — **Sau khử mẹ (phần dư)**, kèm nhãn vạch đen | Đã trừ mẫu nhịp mẹ; còn lại chủ yếu là nhịp thai | Các gợn nhỏ đều đặn, nhanh gấp đôi nhịp mẹ | Vẫn còn sóng mẹ lớn → sẽ dẫn tới lỗi bám nhịp mẹ |
| 4 — **Xác suất của mô hình** + đường ngưỡng | Mô hình cho mỗi mẫu một xác suất "đây là nhịp thai" | Đỉnh nhọn vượt ngưỡng **0,75** được nhận là nhịp | Xác suất lờ đờ quanh ngưỡng → mô hình không chắc |
| 5 — **Kết quả** | ● xanh = TP (đúng) · ✕ đỏ = FP (báo thừa) · ▲ cam = FN (bỏ sót) | Đếm mắt tỉ lệ xanh | Nhiều ▲ cam liên tiếp = bỏ cả một đoạn |

Thao tác: kéo chuột để phóng to, nhấp đúp để xem lại toàn bộ.

Ngưỡng 0,75 **lưu trong checkpoint**, chọn trên tập validation của fold — không chỉnh theo từng bản ghi.

### 5.3. Tab *Chọn kênh — cả 4 kênh*

Bảng có các cột: **Kênh | peakprob | PSD dải thai | Nhịp | fHR TB | F1 | Se | PPV | Chọn**. Kênh được chọn tô nền xanh.

* **peakprob** = với mỗi đoạn 4 s, lấy xác suất trung bình mà mô hình gán cho chính các đỉnh nó vừa tìm; điểm kênh = **trung vị** qua các đoạn.
  Không nhìn nhãn, không có tham số học.
* **PSD dải thai** = đỉnh mật độ phổ công suất trong dải 1,8–3,0 Hz (108–180 bpm) của đường bao phần dư — quy tắc của Power-MF.
* **Cột F1/Se/PPV chỉ tính SAU khi đã chọn**, chỉ để kiểm tra, **không tham gia việc chọn**.

Cách đọc: so **tương đối** giữa 4 kênh trong cùng một bản ghi. Ví dụ a09: peakprob k1 = 0,990 so với 0,905/0,919/0,932
→ chọn kênh 1 (F1 94,25); PSD lại chọn kênh 2 (F1 19,35).

Câu nói mẫu: *"Điểm này là mức tự tin của mô hình tại chính các đỉnh nó tìm được — cao nghĩa là các đỉnh trông giống nhịp thai thật."*

Câu hỏi hay gặp: *"peakprob có nhìn nhãn không?"* → **"Không.** Kiểm chứng: xáo nhãn rồi chạy lại, 0/776 lựa chọn thay đổi
(`analysis/chonkenh_results.json` → `kiem_tra_ro_ri`); kiểm thử `test_peakprob_is_label_blind` bỏ hẳn nhãn đi vẫn chọn cùng kênh."

### 5.4. Tab *Nhịp tim thai + đèn đoạn*

* **Đường trên** — fHR theo cửa sổ 4 s: đường xanh đậm = mô hình, đường chấm đen = theo nhãn.
  Dải xanh nhạt **110–160 bpm** là vùng bình thường.
  Đọc: hai đường bám nhau = tốt. Đường mô hình phẳng và thấp hơn đường nhãn = dấu hiệu **bám nhịp mẹ**.
* **Cột dưới** — `p(đoạn lỗi)` cho từng đoạn 4 s của cổng học.
  Ngưỡng vẽ sẵn: **xanh khi p < 0,052**, **đỏ khi p > 0,540** (hiệu chuẩn trên ADFECGDB ngoài fold: 85 % xanh, 5 % đỏ).
* **Nền đỏ** trên cả hai biểu đồ = đoạn bị **TỪ CHỐI**.

Câu nói mẫu: *"Cột càng cao thì hệ thống càng cho rằng đoạn đó sai. Những đoạn tô nền đỏ là những đoạn nó tự loại — và đúng
những chỗ đó đường nhịp mới lệch khỏi nhãn."*

### 5.5. Tab *So sánh với nhãn*

| Thẻ số | Nghĩa | Ngưỡng |
|---|---|---|
| **Se** (độ nhạy) | Trong 100 nhịp thật, mô hình bắt được bao nhiêu | càng cao càng ít bỏ sót |
| **PPV** (giá trị dự báo dương) | Trong 100 nhịp mô hình báo, bao nhiêu là thật | càng cao càng ít báo thừa |
| **F1** | **Trung bình điều hoà của Se và PPV — một con số duy nhất, cao chỉ khi vừa ít bỏ sót vừa ít báo thừa** | ≥ 99 rất tốt · 90–99 dùng được · 50–90 có vấn đề · < 50 hỏng |
| **Jitter** | Lệch thời điểm trung bình giữa nhịp phát hiện và nhịp nhãn (chỉ tính trên nhịp đã bắt đúng) | 1–4 ms rất tốt; ≥ 17 ms nghĩa là các nhịp "bắt đúng" thật ra ghép nhầm chỗ |
| **TP / FP / FN** | Số nhịp đúng / thừa / sót | dùng để giải thích F1 |

**F1 nói bằng một câu cho người không làm máy học:**
*"F1 là một điểm từ 0 đến 100 gộp cả hai lỗi lại: bỏ sót nhịp và báo thừa nhịp. Chỉ khi cả hai đều ít thì F1 mới cao."*

**Vì sao dùng dung sai ±50 ms?**
*"Một nhịp được tính là đúng nếu lệch không quá 50 mili-giây so với nhãn. Đây là quy ước của CinC 2013 cho điện tim thai.
Chuẩn AAMI cho người lớn dùng 150 ms, nhưng tim thai đập nhanh gần gấp đôi người lớn — khoảng cách giữa hai nhịp chỉ khoảng
400–460 ms — nên 150 ms quá lỏng, dễ ghép nhầm sang nhịp bên cạnh."*

Thực tế đo được: jitter trên nhịp đã bắt đúng chỉ **3,76 ms**, nhỏ hơn dung sai ±50 ms rất nhiều
(`analysis/xacnhan_results.json`) — nghĩa là dung sai này không phải chỗ ăn gian.

### 5.6. Tab *Kết quả tổng hợp (60 bản sạch)*

Bảng đọc trực tiếp lúc khởi động từ `analysis/dulieu_results.json` (60 bản sạch) và `analysis/chonkenh_results.json` (22 chủ thể) —
**không ghi cứng số trong mã**. Các con số chính:

| Quy tắc chọn kênh | F1 trung bình, 60 bản CinC sạch |
|---|--:|
| psd (Power-MF) | 74,28 |
| gate (khai báo trước) | 80,72 |
| **gate4** (khai báo trước, **sống sót Holm** p 0,015) | **81,01** |
| rrcv | 80,00 |
| **peakprob** (hậu kiểm) | **82,01** |
| oracle (giới hạn trên, có nhìn nhãn) | 83,60 |

peakprob − psd = **+7,73** [+3,82; +12,41], p = 5,6e-04, p Holm 0,0039 trên 7 quy tắc; lấy lại 82,9 % dư địa oracle;
số bản F1 < 50 giảm từ 16 xuống 9; thắng 19 / hoà 35 / thua 6; **không bản nào mất quá 3,90 điểm**.

Câu phải nói kèm: *"peakprob là quy tắc hậu kiểm. Quy tắc em khai báo trước là gate (trượt Holm) và gate4 (sống sót Holm) —
gate4 mới là kết quả trung thực mạnh nhất."*

### 5.7. Tab *Nhật ký (JSON)*

Bản tóm tắt máy đọc được của đúng lần chạy vừa rồi: tên bản ghi, checkpoint, kênh, điểm từng kênh, các chỉ số, thành phần của đèn.
Dùng để dán vào báo cáo hoặc khi cô hỏi một con số mà không nhớ.

---

## 6. Nếu cô muốn test trên dữ liệu chưa có

### (a) Quy trình 5 bước (tab *Tải dữ liệu mới*)

1. **Ô *Tệp bản ghi*** — kéo thả hoặc bấm chọn: `.edf` · `.hea` **+** `.dat` (**chọn cả hai cùng lúc**; có `.fqrs` thì chọn luôn) · `.csv` · `.npy` · `.txt`.
2. **Ô *Tần số lấy mẫu (Hz)*** — chỉ cần với `.csv` / `.npy` / `.txt`; EDF và WFDB tự đọc tần số từ tệp.
   Điền sai tần số thì nhịp tim ra sai theo đúng tỉ lệ đó.
3. **(Tuỳ chọn) Ô *Nhãn tham chiếu*** — `.qrs` · `.fqrs` · `.csv` / `.txt` một cột chỉ số mẫu ở đúng tần số đã khai.
   Có nhãn thì mới có F1/Se/PPV. Hai ô *Kênh bụng* và *Đèn tin cậy* để mặc định là được.
4. **Bấm *Phân tích*.** Đo thật ngày 13/09/2026 với `vidu_tai_len.csv` (30 s, 4 kênh): **453 ms** cho phần đọc tệp +
   mô hình + vẽ ở phía máy chủ, **3,7–4,4 s** tính cả tải tệp lên và vẽ trong trình duyệt. Bản 60 s ≈ gấp đôi.
5. **Đọc kết quả theo Phần 5**, ở các tab con ngay bên dưới — nhưng **đọc đèn tin cậy trước F1**.

Cảnh báo giao diện sẽ hiện (và phải nói thành lời):

* **Không có nhãn** → *"Không có nhãn: không tính được F1/Se/PPV. Chỉ xem được nhịp, fHR và đèn tin cậy."*
* **Về miền dữ liệu** → *"Đây là dữ liệu ngoài miền huấn luyện. Trên bộ ngoài miền đã đo (60 bản CinC sạch), F1 trung bình
  chỉ 74,28 đến 82,01 tuỳ quy tắc chọn kênh (74,28 quy tắc cũ · 80,72 kế hoạch chọn · 81,01 gate4 · 82,01 hậu kiểm) so với 97,56 trong miền. Kết quả kém hơn là điều phải dự kiến."*

**Tệp ví dụ có sẵn để thử ngay** (`D:\NCKHSV2026-2027\demo\assets\`):

| Tệp | Nội dung |
|---|---|
| `vidu_tai_len.csv` | 4 cột `AECG1..AECG4`, **1000 Hz**, **30 giây** (30 000 dòng), đơn vị µV |
| `vidu_tai_len_nhan.csv` | nhãn: mỗi dòng một chỉ số mẫu ở 1000 Hz, **65 nhịp trong 30 s** |
| `vidu_tai_len_META.json` | mô tả nguồn và cảnh báo |

**Phải nói khi dùng tệp này:** nó được **cắt từ bản a09** của CinC 2013 set-a (bản sạch) —
**không phải dữ liệu mới thật**, chỉ để thử luồng tải lên.

### (b) Định dạng tối thiểu cần có

**Số kênh:** **tối thiểu 1 kênh** bụng là chạy được — mô hình vốn làm việc trên **một** kênh.
Có từ 2 kênh trở lên thì quy tắc chọn kênh mới có việc để làm; 4 kênh là cấu hình mà mọi con số trong đề tài được đo.

**Tần số lấy mẫu — trả lời chính xác theo mã** (`demo/core.py: _to_1000hz`, dùng `scipy.signal.resample_poly` với tỉ số hữu tỉ
`Fraction(1000/fs).limit_denominator(1000)`):

| fs của cô | Hệ thống làm gì | Kết quả |
|---|---|---|
| **1000 Hz** | không đổi gì | đúng tuyệt đối (đây là tần số gốc của ADFECGDB và CinC) |
| **500 Hz** | nội suy **×2** | đúng tuyệt đối (đây chính là Silesia) |
| **360 Hz** | nội suy hữu tỉ **×25/9** | đúng tuyệt đối về tần số (360 × 25/9 = 1000) |
| **250 Hz** | nội suy **×4** | đúng tuyệt đối |
| **200 Hz** | nội suy **×5** | đúng tuyệt đối |
| **256 Hz / 512 Hz / 128 Hz** | ×125/32, ×125/64, ×125/16 | đúng tuyệt đối |
| **2000 Hz / 4000 Hz** | hạ mẫu ÷2, ÷4 | đúng tuyệt đối |
| **Tần số lẻ, ví dụ 360 Hz** | xấp xỉ bằng phân số mẫu số ≤ 1000 (×3) | ra 999,9 Hz thay vì 1000 Hz — sai số tần số 0,01 %, trên bản 60 s tương đương trôi ≈ 6 ms. Chấp nhận được với dung sai ±50 ms nhưng **phải nói ra** |

**Mô hình làm việc ở 250 Hz**, nhưng **front-end tự hạ mẫu**: mọi bản ghi được đưa về 1000 Hz trước
(`core._to_1000hz`), lọc 10–60 Hz + notch 50 Hz ở 1000 Hz, rồi hạ mẫu ÷4 xuống 250 Hz (`fqrs_model.preprocess`).
Cô **không phải** tự chuyển đổi gì.

**Giới hạn thật về tần số:** dải làm việc là 10–60 Hz, nên tần số gốc phải trên **120 Hz** mới có đủ nội dung trong dải đó
(định lý lấy mẫu). Nội suy **không** tạo lại được nội dung đã mất. → **Khuyến nghị: fs ≥ 250 Hz**; dưới 200 Hz phải coi là
thí nghiệm thăm dò, không phải kết quả.

**Dải demo thực sự chấp nhận:** `50–20 000 Hz` — ngoài dải này demo **từ chối** kèm thông báo tiếng Việt (`demo/core.py`: `FS_MIN, FS_MAX = 50.0, 20000.0`). Tức là 100 Hz vẫn *chạy* nhưng thuộc vùng thăm dò nói trên.

**Độ dài tối thiểu:**

| Mức | Độ dài | Vì sao |
|---|---|---|
| **Demo TỪ CHỐI nếu ngắn hơn** | **8 giây** | `demo/core.MIN_DURATION_S`: mô hình trượt cửa sổ 4 s và có trường tiếp nhận 1,516 s, nên dưới 8 s là gần như toàn phần đệm. Tải lên tệp ngắn hơn sẽ nhận thông báo tiếng Việt *"Bản ghi chỉ dài X s — quá ngắn…"*, không phải lỗi hệ thống |
| **Tuyệt đối tối thiểu về mặt kỹ thuật** | ~4 giây | mô hình trượt cửa sổ 1000 mẫu @250 Hz = 4 s; ngắn hơn sẽ bị **đệm thêm số 0**, kết quả không đáng tin — đây là lý do demo đặt ngưỡng chặn ở 8 s |
| **Để khử mẹ hoạt động** | ~3 giây trở lên, và phải dò được **≥ 3 nhịp mẹ** | `cancel_maternal` cần ít nhất 3 nhịp để dựng mẫu trung vị; thiếu thì bỏ qua khử mẹ hoàn toàn |
| **Để đèn tin cậy có ý nghĩa** | ≥ 60 giây | đèn và peakprob chia đoạn 4 s; 60 s cho 15 đoạn, đủ để lấy trung vị và tỉ lệ đoạn đỏ |
| **Khuyến nghị** | **60 giây trở lên** | đúng độ dài của bộ CinC 2013, là mức mọi con số trong đề tài được đo |

### (c) Nếu cô CHỈ có giấy in CTG

**Trả lời thẳng: không dùng được.** Hai lý do, nói cả hai:

1. **Sai loại tín hiệu.** CTG đo bằng **Doppler siêu âm** — nó bắt **chuyển động cơ học của van tim và thành tim**,
   không phải hoạt động **điện** của tim. Đề tài này làm về điện tim thai (fECG). Hai thứ đo hai hiện tượng khác nhau;
   không có cách chuyển từ cái này sang cái kia.
2. **Sai độ chính xác thời điểm.** Máy CTG in ra đường nhịp tim đã được làm trơn, mỗi giây vài điểm, và bản thân
   phép Doppler có sai số thời điểm cỡ chục mili-giây trở lên. Đề tài cần **vị trí từng nhịp với dung sai ±50 ms**.
   Giấy in không giữ được thông tin đó, và quét ảnh giấy càng không.

Câu nói: *"Giấy CTG cho em đường nhịp trung bình, còn em cần thời điểm từng nhịp riêng lẻ với sai số dưới 50 mili-giây.
Đó là thông tin đã mất trên giấy, không khôi phục được."*

**Cái có thể dùng:** nếu máy CTG hoặc máy monitor **xuất được tệp số** (ví dụ tệp tín hiệu điện ổ bụng thô, không phải ảnh đường in)
thì mang tệp đó sang — đó mới là thứ demo đọc được.

### (d) Nếu cô có dữ liệu nhưng KHÔNG có nhãn nhịp thai

**Vẫn chạy được**, và cho ra:

* đường **nhịp tim thai theo thời gian**;
* **đèn tin cậy** từng đoạn 4 s và mức của cả bản ghi;
* bảng **điểm chọn kênh** của 4 kênh;
* 5 tầng tín hiệu (tầng 5 chỉ có đỉnh phát hiện, không có ● / ✕ / ▲ vì không có gì để đối chiếu).

**Không** cho ra: F1, Se, PPV, jitter, TP/FP/FN. Nói rõ: *"Không có nhãn thì em không chứng minh được đúng hay sai,
chỉ trình bày được kết quả và mức tự tin của hệ thống."*

**Để có nhãn cần một trong hai:**

1. **Điện cực da đầu thai nhi ghi đồng thời** — cho fECG trực tiếp, nhãn tin cậy nhất (cách của ADFECGDB và Silesia B2);
   chỉ làm được trong chuyển dạ, khi màng ối đã vỡ, và cần chỉ định lâm sàng.
2. **Chuyên gia chấm tay** trên tín hiệu đã khử mẹ — cách của CinC 2013 (người chấm độc lập) và Silesia B1 (nhãn gián tiếp).
   Tốn công, và nếu chỉ một người chấm thì phải ghi là nhãn gián tiếp, không phải sự thật sinh lý.

### (đ) Mẫu thư xin dữ liệu từ khoa sản

Sửa phần trong `[...]` rồi gửi. **Gửi qua giảng viên hướng dẫn, đừng gửi thẳng.**

> **Tiêu đề:** Đề nghị hợp tác chia sẻ dữ liệu điện tim ổ bụng phục vụ đề tài NCKH sinh viên — Trường Đại học Tôn Đức Thắng
>
> Kính gửi [BS. / TS. …], [chức vụ], Khoa Sản [tên bệnh viện],
>
> Em là Ngô Bình Minh, sinh viên Trường Đại học Tôn Đức Thắng, chủ nhiệm đề tài nghiên cứu khoa học sinh viên năm học
> 2026–2027 về phát hiện nhịp tim thai từ tín hiệu điện tim ổ bụng của mẹ. Đề tài do [học hàm, học vị, họ tên giảng viên]
> hướng dẫn (đồng kính gửi trong thư này).
>
> Đề tài hiện dùng bốn bộ dữ liệu công khai quốc tế. Hạn chế lớn nhất của chúng em là chưa có dữ liệu ghi tại Việt Nam,
> nên chưa đánh giá được phương pháp trên dân số và thiết bị trong nước. Vì vậy em viết thư này xin phép được trao đổi
> về khả năng hợp tác chia sẻ dữ liệu.
>
> **Dữ liệu chúng em cần:** tín hiệu điện tim ổ bụng dạng số (từ 1 đến 4 kênh), tần số lấy mẫu từ 250 Hz trở lên,
> mỗi bản ghi từ 60 giây trở lên. Nếu có sẵn chú thích vị trí nhịp tim thai thì rất quý; nếu không có, dữ liệu vẫn hữu ích
> cho phần đánh giá độ tin cậy. Dữ liệu **không cần** kèm thông tin định danh bệnh nhân.
>
> **Mục đích sử dụng:** chỉ phục vụ nghiên cứu khoa học sinh viên và công bố học thuật. Không dùng cho bất kỳ mục đích
> thương mại nào. Kết quả nghiên cứu là bản mẫu nghiên cứu, **không phải thiết bị y tế và không dùng cho chẩn đoán**.
>
> **Cam kết của chúng em:**
> * Không phát tán, không chia sẻ lại dữ liệu cho bất kỳ bên thứ ba nào.
> * Lưu trữ trên máy cá nhân có mật khẩu; xoá theo yêu cầu của quý khoa hoặc khi đề tài kết thúc.
> * Ghi nhận đóng góp của quý khoa trong mọi công bố, theo hình thức quý khoa mong muốn (đồng tác giả hoặc lời cảm ơn).
> * Gửi quý khoa bản thảo trước khi nộp công bố.
>
> **Về đạo đức nghiên cứu:** em xin được hỏi quý khoa hướng dẫn về quy trình cần thiết — hồ sơ trình Hội đồng Đạo đức
> trong nghiên cứu y sinh học của bệnh viện, mẫu phiếu chấp thuận tham gia của sản phụ, và cách ẩn danh dữ liệu mà
> quý khoa yêu cầu. Chúng em sẵn sàng chuẩn bị đầy đủ hồ sơ và chỉ bắt đầu sử dụng dữ liệu sau khi có phê duyệt.
>
> Nếu quý khoa thấy thuận tiện, em xin phép được đến trình bày trực tiếp trong 15 phút về đề tài và cách dữ liệu sẽ được dùng,
> vào thời gian quý khoa sắp xếp.
>
> Em xin chân thành cảm ơn và kính chúc quý khoa nhiều sức khoẻ.
>
> Trân trọng,
> Ngô Bình Minh — Sinh viên, Trường Đại học Tôn Đức Thắng
> [email] · [số điện thoại]
> GVHD: [học hàm, học vị, họ tên] · [email giảng viên]

**Bản tin nhắn ngắn** (nếu liên hệ qua Zalo/điện thoại, khi đã có người giới thiệu):

> Dạ em chào [BS. …], em là Ngô Bình Minh, sinh viên Trường ĐH Tôn Đức Thắng, làm đề tài NCKH sinh viên về đo nhịp tim thai
> từ điện tim ổ bụng, do [tên GVHD] hướng dẫn. Em đang thiếu dữ liệu ghi tại Việt Nam. Em xin phép gửi bác một thư trình bày
> ngắn về đề tài, mục đích dùng dữ liệu và cam kết bảo mật, để bác xem giúp em có khả năng hợp tác không ạ. Em cảm ơn bác nhiều.

---

## 7. Kế hoạch dự phòng

### 7.1. Sự cố và cách xử lý

| Sự cố | Làm gì |
|---|---|
| Trang không mở / cổng 7860 bận | `$env:RELYFETAL_PORT = "7870"; python demo/app.py` → mở http://127.0.0.1:7870 |
| Gradio lỗi khi khởi động | `python demo/run_check.py --only r01,a09,a02 --out demo_check_3ban --threads 2` — in bảng ra terminal, giải thích theo bảng đó |
| Biểu đồ trắng (WebGL bị chặn) | Thẻ số và tab *So sánh với nhãn* vẫn chạy; phần biểu đồ thì mở ảnh trong `demo/screenshots/` |
| Chậm bất thường (> 30 s một bản) | Đặt `RELYFETAL_THREADS=2`; tránh bản Silesia B1 (20 phút) |
| Python/torch hỏng hẳn | Chuyển sang chiếu ảnh (mục 7.2) — **không cố sửa mã trước mặt cô** |
| Cô hỏi con số không nhớ | Mở tab *Kết quả tổng hợp*, hoặc mở `demo/results/demo_check_showcase.json` |

### 7.2. Chiếu ảnh thay cho demo — thứ tự 6 ảnh

Thư mục: `D:\NCKHSV2026-2027\demo\screenshots\`

| # | Tệp | Nói gì khi chiếu |
|---|---|---|
| 1 | `01_r01_tong_quan.png` | "Đây là r01, bản dễ: 5 tầng tín hiệu từ thô đến nhịp phát hiện, đèn tin cậy CAO." |
| 2 | `04_a09_chon_kenh.png` | "Đây là điểm chính của đề tài: cùng một bản ghi, chọn kênh 1 được F1 94,3, chọn kênh 2 chỉ còn 19,4. Cách chọn kênh quyết định kết quả." |
| 3 | `07_B2_03_fhr_den_doan.png` | "Bản chuyển dạ khó, F1 chỉ 83,9 — nhưng hệ thống tự tô đỏ đúng những đoạn nó sai." |
| 4 | `09_a02_the_so.png` | "Lỗi nguy hiểm nhất: mô hình bám nhịp mẹ, 78 % nhịp trùng đỉnh R của mẹ. Đèn báo đỏ." |
| 5 | `11_a27_the_so.png` | "Bản gần như không có tín hiệu thai dùng được. Việc đúng duy nhất là nói 'tôi không chắc' — đèn đỏ ở cả hai chế độ." |
| 6 | `12_tong_hop.png` | "Bảng tổng hợp 60 bản CinC sạch: PSD 74,28, gate (kế hoạch chọn) 80,72, gate4 81,01, peakprob (hậu kiểm) 82,01." |

Bốn ảnh dự phòng cho **hai tab mới** (chụp ngày 13/09/2026, cùng thư mục) — chỉ dùng khi cô hỏi thẳng về dữ liệu:

| # | Tệp | Nói gì khi chiếu |
|---|---|---|
| 13 | `13_du_lieu_nhom_bang.png` | "Đây là toàn bộ dữ liệu của nhóm, đường dẫn thật trên máy, số liệu đọc thẳng từ tệp chứ không gõ tay." |
| 14 | `14_du_lieu_nhom_tin_hieu_tho.png` | "Đây là tín hiệu thô 10 giây của một bản CinC sạch: gai to là nhịp mẹ, vạch đỏ là nhịp thai theo nhãn — thai nhỏ hơn hẳn, đó là lý do phải có mô hình." |
| 15 | `15_tai_du_lieu_moi_form.png` | "Nếu cô có dữ liệu mới, đây là chỗ nạp vào: nhận EDF, WFDB, CSV, NPY, TXT — và hai hộp cảnh báo luôn hiện." |
| 16 | `16_tai_du_lieu_moi_ket_qua.png` | "Đây là kết quả khi nạp tệp ví dụ 30 giây kèm nhãn: hệ thống chạy hết đường và tính được F1." (Nhớ nói: tệp ví dụ cắt từ a09, **không phải** dữ liệu mới thật.) |

### 7.3. Nếu chỉ kịp chiếu MỘT ảnh

Chiếu **`04_a09_chon_kenh.png`**.

Nói đúng ba câu:

> "Cùng một bản ghi, cùng một mô hình, chỉ khác ở chỗ chọn kênh bụng nào."
> "Chọn kênh 1 thì F1 94,3; chọn kênh 2 thì còn 19,4 — quy tắc cũ chọn đúng kênh 2 đó."
> "Trên 60 bản sạch, quy tắc mới hơn quy tắc cũ 7,73 điểm — nhưng đó là quy tắc em chọn hậu kiểm, quy tắc khai báo trước
> là gate4 và nó sống sót hiệu chỉnh Holm."

Lý do chọn ảnh này: nó cho thấy **vấn đề**, **giải pháp**, và **con số** trong một khung hình, và nó là chỗ nhóm có đóng góp rõ nhất.

---

## 8. Những gì KHÔNG được làm trong demo

1. **KHÔNG mở bản ghi nhiễm làm ví dụ ngoài miền.** Đủ 15 mã, đọc lại cho thuộc:
   **a03 · a04 · a05 · a08 · a12 · a13 · a14 · a15 · a17 · a19 · a20 · a22 · a23 · a24 · a25**
   Nếu lỡ mở trúng thì nói ngay: *"Bản này trùng với dữ liệu huấn luyện, không được coi là ngoài miền."*
   Tab *Dữ liệu của nhóm* và danh sách *Bản ghi mẫu* đều gắn cờ ⚠ cho 15 bản này.

2. **KHÔNG chiếu số cổng từ chối đo trên CinC.** Các số AUROC 0,980 / độ phủ 66,7 % / 15 trong 16 được đo trên
   **75 bản nhiễm** → không dùng làm số chính, và **chưa tính lại trên 60 bản sạch**.
   Số cổng được phép dùng: **LOSO 22 chủ thể**, AUROC gộp **0,965** [0,857; 0,992], AUROC **trong bản ghi 0,934** [0,872; 0,981]
   tính trên 11/22 chủ thể có đoạn xấu, chỉ ở dạng phân tích, chưa có trong demo (`analysis/gate22_results.json`).
   Đèn trong demo là cổng 5 ca: 0,721 [0,517; 0,898] trên 5 bản CinC sạch khi ghép mô hình 5 ca.

3. **KHÔNG nói "phải có cổng học mới làm được".** Cổng học xếp đúng 3 bản khó nhất (B2_03, B1_07, B1_06) vào hạng 1-2-3 từ dưới
   (xác suất ngẫu nhiên 1/1540) — **nhưng** 5/24 quy tắc chỉ dùng **một** đặc trưng cũng xếp đúng 3/3.

4. **KHÔNG dùng những từ và cụm sau** (không nói, không viết trên slide):
   *SOTA · state-of-the-art · novel · first · tiền đăng ký · pre-registered · "phát hiện rò rỉ" / "discovered the leak" ·
   "mô hình không phải nút thắt" · "lưỡng cực" (như một đặc tính) · "thiếu tín hiệu thật" (như một kết luận) ·
   "Physiological Measurement là Q1" · "CinC 2026" (như đích nộp).*

5. **KHÔNG kết luận "ngoài miền kém vì thiếu tín hiệu thật".** Bốn phương pháp thích nghi miền đều thất bại
   (chuẩn diện lưới +0,25 p 0,68 · tự huấn luyện nhãn giả −0,67 · AdaBN −1,58 · TENT −2,43), nhưng phép thử này
   có **âm tính giả 18,0 %** [12,1; 25,0] → **nguyên nhân chưa xác định**. Nói đúng: *"chưa chứng minh được nguyên nhân."*

6. **KHÔNG trình bày peakprob như quy tắc đã xác nhận.** Luôn kèm: *"đây là lựa chọn hậu kiểm; quy tắc khai báo trước là gate
   (trượt Holm, p 0,051) và gate4 (sống sót Holm, p 0,015)."* Trên thang logit 22 chủ thể, **gate** vẫn đứng đầu, peakprob hạng 3.

7. **KHÔNG hứa nhân rộng.** Không có bộ công khai nào khác có nhãn fQRS thật: NIFEADB không chú thích thai;
   NInFEA chỉ có Doppler; `nifecgdb` tệp `.qrs` là QRS **mẹ** 86 bpm; CinC set-b nhãn không công bố. → **chưa nhân rộng được.**

8. **KHÔNG nói dải lọc 10–60 Hz là yếu tố quan trọng.** Đo trên chính TCN: +2,44 [−0,04; +6,29] trên kênh PSD,
   nhưng **−0,07** [−0,51; +0,39] trên trung bình 4 kênh → không quan trọng với bộ đo này. Con số +11,00 cũ **đã rút**.

9. **KHÔNG nói kiến trúc là đóng góp.** rf_wide (97,63) và tcn_ms (97,62) **tương đương** TCN (97,64) theo TOST-Holm.
   Khoảng cách của cnn_l (94,53) là do **bề rộng ngữ cảnh** chứ không do họ kiến trúc: nới trường tiếp nhận khớp TCN thì lên 96,84.

10. **KHÔNG trình bày kết quả như đã ổn định qua nhiều seed.** Chỉ có seed 0 (97,56) và seed 1 (97,59), lệch 0,03,
    và **không có checkpoint seed 1**. Nếu cô hỏi số seed: *"mới hai seed, còn thiếu; cần 3–5 seed."*

---

## Phụ lục — truy nguồn con số

| Con số | Tệp trên đĩa |
|---|---|
| 60 bản sạch: psd 74,28 · gate 80,72 · gate4 81,01 · rrcv 80,00 · peakprob 82,01 · oracle 83,60; peakprob − psd +7,73 [+3,82; +12,41] p Holm 0,0039; gate p Holm 0,051; gate4 p Holm 0,015 | `analysis/dulieu_results.json` → `chon_kenh_60_sach`; `benchmark_dpss/eval_cinc60_sach.json` |
| 22 chủ thể: Rely 97,56 · PMF4 98,83 (−1,27 [−3,08; +0,27]) · PMF1 86,71 (+10,85, 22/22) | `analysis/chonkenh_results.json` → `he_qua_hau_kiem.bang.psd`; `baselines/powermf_fair_stats.json` |
| Tỉ lệ lấy lại 89,49 % [81,4; 103,2], jackknife 88,6–93,4 | `analysis/recovery_ratio.json` |
| F1 từng bản / từng quy tắc (a09 psd 19,35 so với peakprob 94,25; a02; a27) | `analysis/chonkenh_results.json` → `F1_tung_ban_ghi.cinc` |
| Kiểm rò rỉ nhãn của peakprob: 0/776 lựa chọn đổi | `analysis/chonkenh_results.json` → `kiem_tra_ro_ri` |
| 15 bản CinC nhiễm, ánh xạ r01/r04/r07/r08/r10, NCC 1,0000 | `analysis/dulieu_results.json`; `demo/core.py: CINC_LEAK`; `survey/ro_ri_vanlieu.json` |
| Cổng 22 ca (chỉ phân tích, chưa có trong demo): AUROC gộp 0,965 · trong bản ghi 0,934 trên 11/22 chủ thể · xếp hạng B2_03/B1_07/B1_06 | `analysis/gate22_results.json` |
| Kiến trúc 7 họ, TOST-Holm | `analysis/kientruc_results.json` |
| Thích nghi miền (4 phương pháp thất bại, âm tính giả 18,0 %) | `adapt/adapt_results.json` |
| Dải lọc trên TCN: +2,44 kênh PSD, −0,07 trung bình 4 kênh | `pilot_evidence/band_tcn_stats.json` |
| Chệch STV +0,33 ms trong miền, n = 5 (số dùng được); +1,86 B2 / +1,84 B1; +20,50 ms CinC **đã rút** | `analysis/clinical_results.json` |
| Jitter 3,76 ms trên nhịp đã bắt đúng; phổ lỗi 6 nhóm | `analysis/xacnhan_results.json` |
| Kết quả 5 bản minh hoạ (F1, đèn, thời gian) | `demo/results/demo_check_showcase.json` |
| Thời gian thật trong trình duyệt (12,9 s · 3,0 s · 3,1 s · 6,0 s · 3,5 s) | `demo/screenshots/screenshots.json` |
| Fold của từng chủ thể trong 22 ca | `benchmark_dpss/eval_22.json` → `folds` |
| Danh sách con số **đã rút** — không được trích dẫn lại | `survey/facts_phase4.json` → `Z_DA_RUT`; `README.md` mục Retractions |

---

**Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.**
