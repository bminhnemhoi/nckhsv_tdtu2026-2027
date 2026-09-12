# Bộ chỉ số lâm sàng — RelyFetal

*Sinh ngày 2026-09-12 bởi `analysis/clinical.py`. Dữ liệu thô: `analysis/clinical_results.json`, nhật ký: `analysis/clinical_log.txt`, hình: `clinical_stv_fhr.png`, `clinical_coverage_lock.png`. 32 bản ghi, 269,6 phút tín hiệu thật, 2 luồng CPU, 5,1 phút chạy.*

> **Trả lời thẳng hai câu hỏi của P3, trước khi trình bày số:**
>
> **1. Bộ dò này có dùng được để tính STV không? — KHÔNG, không phải như một máy đo STV độc lập.** Trên 10 bản ghi Silesia B1 (20 phút — tập DUY NHẤT đủ dài để một trị số Dawes-Redman là hợp lệ), giới hạn đồng thuận 95 % là **[−4,45; +8,14] ms** quanh một ngưỡng quyết định 2,6–3,0 ms. Ngay cả khi chỉ giữ những bản ghi mà cổng từ chối chấm "cao" (n = 15, F1 ≥ 99,6), LoA vẫn rộng **1,00 ms**, trong khi ranh giới lâm sàng 2,6 với 3,0 chỉ cách nhau **0,4 ms**. Nặng hơn: sai số **gần như chỉ đi một chiều — 25/32 bản ghi mô hình ĐÁNH GIÁ STV CAO HƠN sự thật** (sai số âm lớn nhất chỉ −0,17 ms, sai số dương lớn nhất +67,14 ms). Đó đúng là chiều **trấn an giả**: một thai bị suy sẽ được máy đọc thành bình thường. 3 bản ghi có STV nhãn < 2,6 ms, mô hình gắn cờ **0/3**.
>
> **2. Độ phủ có chấp nhận được trên lâm sàng không? — Được trên ADFECGDB, KHÔNG trên Silesia, và thất bại hoàn toàn trên CinC 2013.** Tính theo THỜI LƯỢNG (không theo bản ghi): ADFECGDB **96,0 %** (mất 4,0 % — tốt hơn CTG Doppler), Silesia B1 **88,8 %** và B2 **88,2 %** (mất ~11 % — xấu hơn chuẩn 5–8 % của CTG giai đoạn I), CinC 2013 **58,7 %** (mất 41,3 % — vượt xa ngưỡng "mất tín hiệu cao" 20 %). Và **tổng % không phải là vấn đề lớn nhất**: khoảng trống liên tục dài nhất là **192 giây**. Một nhịp giảm kéo dài dài 90–180 s có thể lọt trọn vào một khoảng trống như thế mà máy không hề báo.
>
> Con số 43,8 % trong `facts_phase2.json` là **tỉ lệ BẢN GHI được chấm xanh**, không phải độ phủ thời gian. Hai đại lượng khác nhau; từ nay phải gọi tên tách bạch.

---

## 0. Giao thức — khai báo TRƯỚC khi chạy

| Mục | Quy định |
|---|---|
| Epoch STV | 3,75 s (16 epoch/phút), trung bình khoảng RR trong epoch tính bằng ms; STV = trung bình \|hiệu hai epoch liên tiếp\| |
| RR hợp lệ | 0,25–0,75 s (80–240 bpm); epoch cần ≥ 2 khoảng RR hợp lệ, nếu không thì bỏ |
| Cửa sổ FHR | 60 s không chồng lấn (chính) + quét thêm 5 / 10 / 30 s; cần ≥ 10 RR (60 s) hoặc ≥ 34 % số nhịp kỳ vọng (cửa sổ ngắn) |
| Dung sai khớp nhịp / khóa mẹ | ±50 ms |
| Đoạn cổng từ chối | 4,0 s, `fsqi/gate.py` chế độ `hoc` (GBM 12 chỉ số cổ điển) |
| Kênh | quy tắc **mù nhãn** theo PSD (Power-MF, Jaeger 2024) trên cả ba tập; CinC báo cáo **thêm** kênh 0 cố định vì kênh 0 là lựa chọn HẬU KIỂM |
| Ngưỡng STV tham chiếu | TRUFFLE: < 2,6 ms (< 29 tuần) hoặc < 3,0 ms — **do phản biện P3 cung cấp, CHƯA đối chiếu bản gốc trong phiên này** |
| Nguồn CTG so sánh | mất tín hiệu Doppler 5–8 % giai đoạn I, 9–20 % giai đoạn II; fECG bụng thương mại 5,3 %; "mất tín hiệu cao" > 20 % — **cũng do P3 cung cấp, chưa kiểm chứng** |

**Checkpoint — tất cả đều NGOÀI MẪU:**

| Tập | n | Thời lượng/bản | Checkpoint |
|---|---:|---:|---|
| ADFECGDB (PhysioNet) | 5 | 300 s | `fetalqrs_tcn_fold_rXX.pt` (mô hình n = 5, LORO) |
| Silesia B2 (chuyển dạ) | 7 | 300 s | `fetalqrs_tcn_22_fold_XX.pt` — **fold GIỮ LẠI đúng chủ thể đó** |
| Silesia B1 (thai kỳ) | 10 | 1198 s | như trên |
| CinC 2013 set-a | 10 | 60 s | `fetalqrs_tcn_22_production.pt` (zero-shot, ngoài miền) |

> **Sai lệch có chủ ý so với đề bài.** Đề bài giao `production_22` cho 17 bản Silesia. `production_22` được huấn luyện trên **chính 17 chủ thể đó** → đánh giá trong mẫu. Tôi dùng checkpoint fold giữ lại chủ thể thay thế, và chạy thêm `production_22` để **đo mức thổi phồng**: F1 trung bình 22 chủ thể 97,51 (ngoài mẫu) so với 99,31 (trong mẫu); **độ chệch STV +1,51 ms (ngoài mẫu) so với +0,42 ms (trong mẫu) — đánh giá trong mẫu làm sai số STV nhỏ đi 3,6 lần.** Mọi con số dưới đây là ngoài mẫu.

**Kiểm chứng tính đúng của đường ống:** F1 tính lại ở đây trùng khớp với các con số đã công bố — ADFECGDB kênh PSD **99,21**, Silesia B1 **97,15**, B2 **96,82**, CinC PSD **69,31** (đúng bằng `facts_verified.json` và `facts_phase2.json`). Đường ống lâm sàng không làm lệch phép đo gốc.

---

## 1. STV kiểu Dawes-Redman

### 1.1 Kết quả theo tập

| Tập | n | STV nhãn (ms) | STV mô hình (ms) | Độ chệch | LoA 95 % | Bề rộng LoA | r Pearson | ρ Spearman |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| ADFECGDB | 5 | 9,62 | 9,95 | **+0,33** | [−0,89; +1,55] | 2,44 | 0,986 | 0,700 |
| Silesia B2 | 7 | 8,80 | 10,66 | **+1,86** | [−6,90; +10,63] | 17,53 | 0,863 | 0,964 |
| Silesia B1 | 10 | 7,74 | 9,59 | **+1,84** | [−4,45; +8,14] | 12,58 | 0,732 | 0,685 |
| CinC 2013 (PSD) | 10 | 5,54 | 26,04 | **+20,50** | [−24,76; +65,76] | 90,52 | −0,392 | −0,418 |
| **Tất cả** | 32 | 7,58 | 15,02 | **+7,44** | [−23,05; +37,93] | 60,98 | −0,194 | 0,212 |

Bản ghép cặp (chỉ dùng epoch hợp lệ ở cả hai chuỗi) cho kết quả gần như đồng nhất — độ chệch tổng +7,43 so với +7,44 — nên **sự bất đồng không đến từ việc chọn epoch, mà đến từ vị trí nhịp**.

### 1.2 Sai số STV bám sát chất lượng dò nhịp, và chỉ đi một chiều

| Dải F1 | n | Độ chệch (ms) | \|sai số\| TB | \|sai số\| max | Bề rộng LoA 95 % |
|---|---:|---:|---:|---:|---:|
| F1 ≥ 99,5 | 18 | +0,10 | 0,13 | 0,71 | **0,92** |
| 99,0 ≤ F1 < 99,5 | 2 | +0,43 | 0,43 | 0,46 | 0,19 |
| 95 ≤ F1 < 99 | 3 | +1,17 | 1,17 | 1,61 | **2,12** |
| F1 < 90 | 9 | +25,78 | 25,78 | 67,14 | 79,48 |

**Hướng sai số:** 25/32 bản ghi mô hình cho STV **cao hơn** nhãn; 7 bản thấp hơn nhưng nhiều nhất chỉ **−0,17 ms**. Nguyên nhân cơ học rõ ràng: mỗi dương tính giả / âm tính giả làm nhiễu một khoảng RR, nhiễu này cộng vào hiệu giữa hai epoch liên tiếp, nên **mọi lỗi dò nhịp đều đẩy STV LÊN**. Sai số đó không ngẫu nhiên — nó luôn đi về phía "biến thiên tốt, thai khoẻ".

### 1.3 Bảng quyết định ở ngưỡng lâm sàng

| Ngưỡng | Bản ghi nhãn dương | Mô hình gắn cờ | TP | FN | FP |
|---|---:|---:|---:|---:|---:|
| STV < 3,0 ms | 3 (a02, a07, a09) | 0 | **0** | **3** | 0 |
| STV < 2,6 ms | 3 (a02, a07, a09) | 0 | **0** | **3** | 0 |

STV mô hình trên ba bản ghi đó: **21,81 / 42,57 / 67,63 ms** so với nhãn **1,18 / 0,93 / 0,49 ms**. Sai một đến hai bậc độ lớn, luôn về phía trấn an.

> **Cảnh báo bắt buộc về ba bản ghi này.** Chúng dài **60 giây**. Dawes-Redman cần tối thiểu 10 phút (thực hành thường 30–60 phút). Vì vậy **1,18 / 0,93 / 0,49 ms không phải là STV lâm sàng hợp lệ** và tôi **không** tuyên bố đó là ba thai bị suy. Đã kiểm tra chuỗi RR nhãn: chúng không phải nhãn suy biến (a09 có 51 giá trị RR khác nhau, SD 16,1 ms) — trị số STV thấp là do RR **so le lên xuống**, nên trung bình từng epoch gần như không đổi. Điều bảng này chứng minh được là: **khi chuỗi tham chiếu nằm trong dải thấp, mô hình không tái tạo được nó**, bất kể dải thấp ấy là sinh lý hay là tạo tác của cửa sổ 60 s.

### 1.4 Tập con đúng nghĩa nhất, và tại sao vẫn chưa đủ

| Tập con | n | Độ chệch | LoA 95 % | Bề rộng |
|---|---:|---:|---|---:|
| Chỉ B1 — **20 phút, tập duy nhất đủ dài cho Dawes-Redman** | 10 | +1,84 | [−4,45; +8,14] | **12,58** |
| 22 chủ thể trong miền | 22 | +1,51 | [−4,88; +7,90] | 12,78 |
| Cổng chấm CAO + TRUNG BÌNH (= tất cả những gì máy thật sự trả lời) | 23 | +0,27 | [−0,62; +1,16] | **1,78** |
| Chỉ cổng chấm CAO | 15 | +0,11 | [−0,39; +0,61] | **1,00** |
| Tất cả 32 | 32 | +7,44 | [−23,05; +37,93] | 60,98 |

Con số **có ý nghĩa vận hành** là hàng thứ ba: sau khi cổng từ chối loại 9 bản ghi, LoA của những gì máy trả lời là **[−0,62; +1,16] ms, bề rộng 1,78 ms**.

**So với yêu cầu lâm sàng:**
- Phân biệt 2,6 với 3,0 ms cần độ phân giải **0,4 ms**. LoA 1,78 ms rộng gấp **4,5 lần**; ngay cả 1,00 ms của nhóm "cao" cũng gấp **2,5 lần**.
- Bề rộng 1,78 ms bằng **59 %** của chính ngưỡng 3,0 ms, trên một thang mà bình thường là 5–9 ms.
- **Không một chủ thể nào trong 22 chủ thể trong miền có STV nhãn gần vùng bệnh lý** (thấp nhất 3,49 ms ở B1_05). Ba trường hợp duy nhất dưới 2,6 ms đều là bản ghi 60 s. Nói cách khác: **chưa có một điểm dữ liệu hợp lệ nào trong vùng ra quyết định** — khẳng định "mô hình phát hiện được STV thấp" hiện **không kiểm chứng được**, chứ không phải "đã bác bỏ".

### 1.5 Kết luận về STV

Dùng được ở mức **theo dõi xu hướng** trên bản ghi cổng chấm "cao": sai số điển hình 0,13 ms, tối đa 0,71 ms. **Không dùng được để ra quyết định Dawes-Redman/TRUFFLE**, vì (a) độ phân giải thiếu 2,5–4,5 lần so với ranh giới 2,6/3,0 ms, (b) sai số một chiều về phía trấn an giả, (c) 3/3 bản ghi tham chiếu thấp nhất bị bỏ sót, (d) 22/32 bản ghi ngắn hơn tối thiểu 10 phút của Dawes-Redman. Nếu bài báo muốn nêu STV, phải nêu kèm cả bốn điểm này.

---

## 2. Bland-Altman nhịp tim thai (cửa sổ 1 phút)

| Tập | n cửa sổ | Độ chệch (bpm) | LoA 95 % | MAE | **% cửa sổ trong ±5 bpm** |
|---|---:|---:|---|---:|---:|
| ADFECGDB | 25 | +0,11 | [−0,62; +0,83] | 0,14 | **100,00** |
| Silesia B2 | 35 | −0,41 | [−3,74; +2,91] | 0,61 | 91,43 |
| Silesia B1 | 190 | +0,15 | [−6,88; +7,18] | 0,70 | 97,37 |
| CinC 2013 (PSD) | 10 | −7,81 | [−34,60; +18,99] | 9,00 | 60,00 |
| **Tất cả** | 260 | −0,24 | [−8,69; +8,22] | 0,95 | **95,38** |

**Mẫu số là thật:** số cửa sổ ghép cặp = số cửa sổ nhãn hợp lệ ở mọi tập (260/260). Không có cửa sổ nào bị loại vì mô hình không tính nổi — nên 95,38 % không phải con số đã được lọc trước.

### 2.1 So với "FHR precision 88,61 %" của DPSS — quét độ dài cửa sổ

Bài DPSS không nêu độ dài cửa sổ dùng cho "FHR precision". Cửa sổ càng dài càng dễ (60 s gộp ~140 nhịp). Nên quét cả dải:

| Tập | 5 s | 10 s | 30 s | 60 s |
|---|---:|---:|---:|---:|
| ADFECGDB | **98,66 %** (n=299) | **98,66 %** (n=149) | 100,00 % (n=50) | 100,00 % (n=25) |
| Silesia B2 | 94,99 % (n=419) | 94,26 % (n=209) | 92,86 % (n=70) | 91,43 % (n=35) |
| Silesia B1 | 95,98 % (n=2389) | 95,63 % (n=1190) | 97,44 % (n=390) | 97,37 % (n=190) |
| CinC 2013 | 55,00 % (n=120) | 51,67 % (n=60) | 60,00 % (n=20) | 60,00 % (n=10) |
| **Tất cả** | 94,58 % (n=3227) | 94,09 % (n=1608) | 95,66 % (n=530) | 95,38 % (n=260) |

Trên ADFECGDB, **ngay ở cửa sổ khắt khe nhất đã thử (5 s) vẫn đạt 98,66 %**, cao hơn 88,61 % của DPSS. Đây là so sánh **bảo vệ được**: không thể nói chúng ta thắng nhờ chọn cửa sổ dài. Vẫn phải kèm ba điều kiện: (i) DPSS chạy zero-shot từ FECGSYNDB tổng hợp còn đây là LORO trong miền — **hai giao thức khác nhau**; (ii) chưa chạy lại DPSS, đây là so với con số đã công bố; (iii) n = 5 sản phụ.

Bland-Altman theo cửa sổ, toàn bộ 32 bản ghi: 5 s [−11,03; +10,57] → 60 s [−8,69; +8,22]. Độ chệch ổn định −0,23 bpm ở mọi độ dài: **không có sai lệch hệ thống về nhịp**, toàn bộ bề rộng là do các bản ghi hỏng.

---

## 3. Độ phủ theo THỜI GIAN (không theo bản ghi)

Ba chính sách, khai báo trước: **P1** = trả lời trừ đoạn ĐỎ; **P2** = chỉ trả lời đoạn XANH; **P3** = như P1 nhưng bỏ cả bản ghi nếu `record_confidence` = thấp.

| Tập | Thời lượng | Số đoạn 4 s | **P1 (%)** | P2 (%) | P3 (TB bản ghi, %) | Khoảng trống P1: trung vị / p90 / max |
|---|---:|---:|---:|---:|---:|---|
| ADFECGDB | 25,0 phút | 375 | **96,0** | 88,8 | 96,0 | 4 s / 12 s / **12 s** |
| Silesia B2 | 35,0 phút | 525 | **88,2** | 61,3 | 81,0 | 4 s / 12 s / **56 s** |
| Silesia B1 | 199,6 phút | 2990 | **88,8** | 58,8 | 75,8 | 4 s / 12 s / **192 s** |
| CinC 2013 | 10,0 phút | 150 | **58,7** | 42,7 | 39,3 | 8 s / 33 s / **48 s** |
| **Tất cả** | **269,6 phút** | 4040 | **88,2** | 61,3 | 68,7 | 4 s / 16 s / **192 s** |

Toàn bộ: 4040 đoạn, 475 đỏ, 2478 xanh; 224 khoảng trống P1 tổng cộng 1900 s (31,7 phút) bị từ chối.

### 3.1 Đối chiếu chuẩn lâm sàng

| Chuẩn | Mất tín hiệu | RelyFetal tương ứng |
|---|---|---|
| CTG Doppler giai đoạn I | 5–8 % | ADFECGDB **4,0 %** ✅ · Silesia **11,2–11,8 %** ❌ · CinC **41,3 %** ❌ |
| CTG Doppler giai đoạn II | 9–20 % | Silesia nằm trong dải này |
| fECG bụng thương mại | 5,3 % | chỉ ADFECGDB đạt |
| "Mất tín hiệu cao" | > 20 % | chỉ CinC vượt |

**Đọc đúng:** trên 5 bản ADFECGDB, độ phủ thời gian **tốt hơn CTG Doppler thường quy**. Trên 199,6 phút Silesia B1 — dữ liệu dài nhất, gần thực tế theo dõi liên tục nhất — mất 11,2 %, **xấu hơn giai đoạn I, ngang giai đoạn II**. Chưa đạt.

### 3.2 Điều quan trọng hơn tổng phần trăm: độ dài khoảng trống

Trung vị khoảng trống là 4 s (một đoạn đơn lẻ) — vô hại. Nhưng đuôi phân bố mới là chỗ nguy hiểm:

- **p90 = 16 s**, **max = 192 s** (B1_07), 48–64 s ở B1_06/B1_10/B2_03.
- Nhịp giảm muộn kéo dài 30–90 s; nhịp giảm kéo dài theo định nghĩa là 2–10 phút. **Một khoảng trống 192 s có thể giấu trọn một cơn giảm kéo dài.** Một khoảng trống 60 s giấu được một nhịp giảm muộn.
- Ở chính sách P2 (chỉ tin đoạn xanh) khoảng trống lớn nhất là **528 s (8,8 phút)** — không thể chấp nhận trên lâm sàng.

**Vì vậy: chỉ báo cáo "% thời lượng" là chưa đủ.** Bất kỳ tuyên bố nào về độ phủ phải kèm p90 và max của khoảng trống. Đây là mục phải bổ sung vào bài.

### 3.3 Đánh đổi phải nói rõ

Độ phủ chỉ là 88,2 % **vì** cổng từ chối làm việc của nó. Nếu tắt cổng, máy trả lời 100 % thời lượng nhưng 9/32 bản ghi sẽ trả kết quả sai (F1 từ 19,35 đến 89,45). Đánh đổi này là đúng hướng, nhưng phải trình bày như một đánh đổi, không được trình bày 88,2 % như một khuyết điểm thuần tuý hay 100 % như một ưu điểm.

### 3.4 Cổng từ chối có bắt đúng không

| Mức cổng | n | F1 TB | F1 min | \|ΔSTV\| TB | \|ΔSTV\| max |
|---|---:|---:|---:|---:|---:|
| cao | 15 | 99,92 | 99,61 | 0,15 ms | 0,71 ms |
| trung_binh | 8 | 98,81 | 96,54 | 0,56 ms | 1,61 ms |
| thấp | 9 | 61,03 | 19,35 | 25,78 ms | 67,14 ms |

- **Lỗi nguy hiểm theo F1 (cổng nói cao/trung bình nhưng F1 < 90): 0/32.** Phân tầng sạch.
- **Lỗi nguy hiểm theo STV (cổng không nói "thấp" nhưng \|ΔSTV\| > 1,0 ms): 2 — r10 (+1,34 ms) và B1_10 (+1,61 ms).** Cả hai có F1 ≥ 96,5, tức **cổng hiệu chuẩn cho việc dò nhịp vẫn để lọt sai số STV đủ lớn để lật một quyết định lâm sàng**. Nếu bài muốn xuất STV, cổng phải được hiệu chuẩn lại theo tiêu chí STV, không phải theo F1.

---

## 4. Khoá nhầm nhịp mẹ — chế độ hỏng nguy hiểm nhất

### 4.1 Ngưỡng ngẫu nhiên phải tính thế nào

Nếu nhịp thai và nhịp mẹ độc lập, tỉ lệ trùng kỳ vọng = 2 × 50 ms / RR_mẹ. Với RR_mẹ 0,46–0,77 s trên 32 bản ghi, ngưỡng này là **13,0–21,9 %** (trung bình 15,2 %). Ước lượng giải tích khớp rất sát trung bình mô phỏng dịch vòng tròn 200 lần (ví dụ a02: giải tích 21,9 % so với mô phỏng 21,2 %) — hai cách xác nhận lẫn nhau.

**Nhưng ngưỡng ngẫu nhiên KHÔNG phải mốc so đúng.** Nhãn chuẩn cũng trùng đỉnh R mẹ đúng ở mức nền đó. Mốc đúng là **chính nhãn chuẩn của bản ghi đó** — nó hấp thụ mọi ghép cặp tần số thật giữa mẹ và thai. Đây là điểm phương pháp tôi thêm vào, không có trong `demo/core.py`.

### 4.2 Kết quả

| Tập | Khoá mô hình TB | Khoá nhãn chuẩn TB | Vượt nhãn TB | Vượt nhãn max | Số bản vượt > 10 điểm |
|---|---:|---:|---:|---:|---:|
| ADFECGDB | 15,7 % | 15,7 % | −0,02 điểm | +0,57 | 0 |
| Silesia B2 | 15,0 % | 14,2 % | +0,85 | +6,17 | 0 |
| Silesia B1 | 15,9 % | 15,7 % | +0,14 | +1,96 | 0 |
| CinC 2013 | 27,4 % | 16,6 % | +10,79 | +58,29 | **2** |
| **Tất cả** | 19,3 % | 15,7 % | +3,60 | +58,29 | **2** |

Trung vị \|vượt nhãn\| trên 32 bản ghi = **0,32 điểm**. Nghĩa là ở đại đa số bản ghi, mô hình trùng nhịp mẹ **đúng bằng** mức mà nhãn thật cũng trùng — không có hiện tượng bám mẹ.

**Chỉ hai bản ghi thật sự khoá nhầm nhịp mẹ, cả hai đều ở CinC 2013:**

| Bản ghi | Khoá mô hình | Khoá nhãn | p95 phân phối rỗng | Vượt nhãn | F1 | Cổng gắn cờ? |
|---|---:|---:|---:|---:|---:|---|
| **a02** | **78,3 %** | 20,0 % | 44,2 % | +58,3 điểm | 24,91 | thấp ✅ (luật khoá mẹ ≥ 60 % kích hoạt) |
| **a09** | **53,4 %** | 15,4 % | 24,6 % | +38,0 điểm | 19,35 | thấp ✅ (**nhưng qua p_bad, KHÔNG qua luật khoá mẹ**) |

**a09 là bài học quan trọng nhất trong mục này.** Hơn một nửa số "nhịp thai" mà mô hình trả về thực chất là nhịp mẹ, nhưng 53,4 % **nằm dưới ngưỡng cổng 60 %** nên luật ghi đè khoá mẹ **không kích hoạt**. Bản ghi được cứu là nhờ điểm `p_bad` của bộ phân loại SQI. Đó là **may, không phải thiết kế**: ngưỡng 60 % được đặt so với một mốc ngẫu nhiên ~13–22 %, tức nó chỉ bắt được trường hợp gần như khoá hoàn toàn.

**Khuyến nghị cụ thể:** thay luật ngưỡng tuyệt đối 60 % bằng **mức vượt so với phân phối rỗng của chính bản ghi**. Với dữ liệu này, cắt ở "vượt p95 mô phỏng hơn 10 điểm" bắt đúng cả a02 và a09 và không tạo dương tính giả nào trong 30 bản còn lại. Đây là thay đổi rẻ và nên làm.

6 bản ghi khác vượt p95 mô phỏng (r01, r08, a05, a08, B2_03, B1_06) nhưng **nhãn chuẩn của chúng cũng vượt gần y hệt** (r08: mô hình 20,4 % / nhãn 20,1 %; a08: 25,0 % / 25,0 %) — đó là ghép cặp tần số mẹ–thai có thật, không phải mô hình bám mẹ. Nếu chỉ so với ngưỡng ngẫu nhiên sẽ báo động giả 6/32 bản ghi.

*Ghi chú nguồn nhịp mẹ:* Silesia dùng nhãn mQRS thật; ADFECGDB và CinC không có nhãn mẹ nên dùng `M.detect_maternal_qrs`. Trên Silesia, dùng nhãn thật và dùng bộ dò cho kết quả gần như trùng nhau, nên phần ADFECGDB/CinC đáng tin ở mức tương tự.

---

## 5. Lựa chọn kênh trên CinC 2013 — nhắc lại lỗi liêm chính, dưới góc nhìn lâm sàng

Số CinC trong bảng trên dùng quy tắc PSD mù nhãn, đo trên **mẫu 10 bản ghi** (F1 69,31).

> **RÚT LẠI 12/09/2026.** Con số **69,31** đã bị rút: nó đo trên mẫu 10/75 bản ghi và bị lệch. Trên
> **đủ 75 bản ghi**, quy tắc PSD mù nhãn cho **79,40** (`benchmark_dpss/eval_cinc75.json`). Quan
> trọng hơn cho mục này: quy tắc **kênh 0 cố định** — trên mẫu 10 bản ghi trông như vượt trội — chỉ
> đạt **69,33** trên đủ 75 bản ghi, tức **kém quy tắc mù nhãn 10,07 điểm** và là quy tắc **tệ nhất**
> trong bốn. Bài học về liêm chính dưới đây **mạnh lên**, không yếu đi.
>
> Phân tích lâm sàng trong tài liệu này **chưa chạy lại** trên 75 bản ghi, nên các cặp F1/STV theo
> từng bản ghi bên dưới vẫn là số của mẫu 10 và chỉ dùng để **minh hoạ cơ chế**, không phải để báo cáo.

Với kênh 0 cố định (lựa chọn HẬU KIỂM, không được dùng làm số chính):

| Bản ghi | PSD: F1 / STV / phủ P1 | Kênh 0: F1 / STV / phủ P1 | STV nhãn |
|---|---|---|---:|
| a01 | 80,99 / 18,52 / 66,7 % | 100,00 / 6,53 / 86,7 % | 6,45 |
| a07 | 45,63 / 42,57 / 6,7 % | 86,92 / 12,47 / 80,0 % | 0,93 |
| a09 | 19,35 / 67,63 / 13,3 % | 94,25 / 6,37 / 93,3 % | 0,49 |
| a10 | 47,13 / 46,16 / 6,7 % | 70,89 / 27,58 / 46,7 % | 4,37 |

Kênh 0 tốt hơn nhiều — nhưng đó chính là lý do nó **không được dùng**: kênh 0 được chọn sau khi biết PSD thất bại. Điều đáng chú ý về lâm sàng: **ngay cả ở kênh 0 với F1 = 94,25, STV của a09 vẫn là 6,37 ms so với nhãn 0,49 ms — sai 13 lần.** Tức vấn đề STV **không** sửa được bằng cách chọn kênh tốt hơn. Chọn kênh sửa được F1 và độ phủ; nó không sửa được độ phân giải STV.

---

## 6. Những gì mục này KHÔNG chứng minh được

1. **Không có dữ liệu trong vùng ra quyết định.** 22 chủ thể trong miền có STV nhãn 3,49–15,97 ms; không ai gần 2,6–3,0 ms. Không thể ước lượng độ nhạy/độ đặc hiệu của cờ "STV thấp".
2. **22/32 bản ghi ngắn hơn tối thiểu 10 phút của Dawes-Redman** (ADFECGDB và B2 là 5 phút, CinC là 1 phút). Chỉ 10 bản B1 cho một trị số STV hợp lệ về thời lượng.
3. **Không có thai dưới 38 tuần trong ADFECGDB**, mà giá trị lâm sàng của STV nằm ở tuần 24–37 (đây chính là giới hạn đã ghi trong `facts_verified.json`, nay áp thẳng vào STV).
4. **Ngưỡng TRUFFLE 2,6/3,0 ms và các con số mất tín hiệu CTG 5–8 % / 9–20 % / 5,3 % / 20 % đều do P3 cung cấp, chưa đối chiếu bản gốc trong phiên này.** Trước khi đưa vào bài phải kiểm chứng và trích dẫn đúng.
5. **STV Dawes-Redman gốc tính trên tín hiệu CTG Doppler lấy mẫu đều**, không phải trên chuỗi RR từng nhịp. Định nghĩa dùng ở đây (trung bình RR trong epoch) là bản thích ứng hợp lý cho fECG nhưng **không đồng nhất** với thuật toán Dawes-Redman gốc; không được ngầm hiểu hai bên cho cùng một trị số.
6. **Một seed, một fold cho mỗi chủ thể.** Theo đo độ ổn định 2 seed đã có (trung bình \|hiệu\| 0,28 điểm F1, lớn nhất 2,81 ở B2_03), B2_03 — bản ghi có sai số STV lớn nhất trong miền (+11,99 ms) — cũng chính là bản ghi kém ổn định nhất theo seed. Sai số STV của nó có thể phần lớn là nhiễu huấn luyện.
7. **n nhỏ.** Theo `analysis/STATS.md`, với n = 5 chủ thể không kiểm định xếp hạng hai phía nào đạt được p < 0,05. Các hệ số tương quan ở Mục 1.1 (r = 0,986 với n = 5) **không được trình bày như bằng chứng thống kê**; chúng là mô tả.

---

## 7. Việc phải làm, theo thứ tự ưu tiên

| # | Việc | Lý do |
|---:|---|---|
| 1 | Nếu bài nêu STV: bắt buộc kèm LoA [−0,62; +1,16] ms (trên phần máy trả lời), hướng sai số một chiều, và câu "chưa có dữ liệu trong vùng < 3 ms" | Nếu không, người đọc sẽ hiểu là máy đo được STV lâm sàng |
| 2 | Thay luật khoá mẹ ngưỡng cứng 60 % bằng "vượt p95 phân phối rỗng của chính bản ghi > 10 điểm" | Bắt được a09 (53,4 %) theo thiết kế chứ không nhờ may; không thêm dương tính giả nào trong 32 bản ghi |
| 3 | Mọi tuyên bố độ phủ phải là **% thời lượng**, kèm p90 và max khoảng trống | 88,2 % nghe ổn; "khoảng trống 192 s" mới là con số bác sĩ cần |
| 4 | Sửa cách gọi 43,8 % thành "tỉ lệ bản ghi xanh", tách khỏi độ phủ thời gian | Hai đại lượng khác nhau, đang bị dùng lẫn |
| 5 | So sánh FHR precision với DPSS phải dùng bảng quét cửa sổ (5/10/30/60 s), không chỉ 60 s | 98,66 % ở cửa sổ 5 s là con số bảo vệ được; 100 % ở 60 s thì không |
| 6 | Hiệu chuẩn lại cổng theo tiêu chí STV nếu muốn xuất STV | Cổng theo F1 để lọt r10 và B1_10 với ΔSTV 1,3–1,6 ms |
| 7 | Kiểm chứng ngưỡng TRUFFLE và số liệu mất tín hiệu CTG từ bản gốc | Hiện là lời truyền đạt từ P3, chưa có nguồn |
| 8 | Thu bản ghi ≥ 10 phút cho mọi tập nếu muốn nói về STV | 22/32 bản ghi hiện dưới ngưỡng tối thiểu của Dawes-Redman |

---

## 8. Tệp sinh ra

| Tệp | Nội dung |
|---|---|
| `analysis/clinical.py` | mã nguồn, chạy lại bằng `python analysis/clinical.py` (5,1 phút, 2 luồng); `--figures-only` để vẽ lại hình từ JSON; `--smoke` để thử nhanh 4 bản ghi |
| `analysis/clinical_results.json` | toàn bộ số liệu từng bản ghi: STV, FHR (kèm quét cửa sổ), độ phủ, khoảng trống, khoá mẹ, mức cổng, và checkpoint phụ `production_22` để đối chiếu trong/ngoài mẫu |
| `analysis/clinical_log.txt` | nhật ký chạy, bảng từng bản ghi |
| `analysis/clinical_stv_fhr.png` | (a) STV nhãn vs mô hình, phóng to vùng lâm sàng, vùng đỏ = bệnh lý · (b) Bland-Altman STV · (c) Bland-Altman FHR cửa sổ 60 s |
| `analysis/clinical_coverage_lock.png` | (a) % thời lượng trả lời từng bản ghi so với mốc CTG · (b) phân bố độ dài khoảng trống, thang log, mốc 90 s · (c) khoá nhịp mẹ so với nhãn chuẩn và phân phối rỗng |
