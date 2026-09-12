# Hướng dẫn demo RelyFetal cho buổi gặp giảng viên hướng dẫn

> **Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.**
> Tài liệu này viết cho người **chưa từng chạy** demo. Mọi con số trong đây đều truy ngược được về một tệp JSON
> trên đĩa (mục 7). Không có con số nào trong demo lấy từ 75 bản CinC (đã rút vì 15/75 bản là bản sao huấn luyện).

Cập nhật: 2026-09-12, sau thẩm định phản biện vòng 6. Demo phản ánh đúng trạng thái đề tài:

| Thành phần | Demo đang dùng | Ghi chú liêm chính |
|---|---|---|
| Mô hình | FetalQRS-TCN, 113 481 tham số, huấn luyện **22 chủ thể** (`model/checkpoints/fetalqrs_tcn_22_*.pt`) | 22 ca (r01…, B1_xx, B2_xx) dùng checkpoint fold **không chứa** chủ thể đó; CinC dùng `22_production` (zero-shot) |
| Chọn kênh mù nhãn | **peakprob** (mặc định) và PSD (Power-MF) để so sánh | peakprob là quy tắc **hậu kiểm**; quy tắc khai báo trước là *gate* và gate trượt Holm — demo nói rõ điều này ở tab *Kết quả tổng hợp* |
| Cổng tin cậy | GBM 12 chỉ số / đoạn 4 s, `fsqi/gate_classical.pkl` | **Hiệu chuẩn trên mô hình 5 ca ADFECGDB.** Cổng 22 ca (`analysis/GATE22.md`) chỉ có kết quả phân tích, chưa có tệp tải được → chưa dùng; giao diện ghi rõ |
| Bảng tổng hợp | đọc lúc khởi động từ `analysis/dulieu_results.json` (60 bản sạch) và `analysis/chonkenh_results.json` (22 chủ thể) | không ghi cứng con số trong mã |

---

## 1. Cài đặt và khởi động

### 1.1. Yêu cầu

* Windows/Linux/macOS, Python 3.12 (đã kiểm trên Windows 11, Python 3.12.6), CPU là đủ (không cần GPU).
* Gói: `torch`, `numpy`, `scipy`, `mne`, `wfdb`, `scikit-learn`, `pandas`, `gradio` (đã kiểm với 6.26.0), `plotly` (7.0.0).
  Cài một lần: `pip install -r requirements.txt` ở gốc repo (nếu thiếu tệp này: `pip install torch numpy scipy mne wfdb scikit-learn pandas gradio plotly`).
* Dữ liệu trên đĩa (demo tự tìm qua `benchmark_dpss/_paths.py` và `model/silesia_loader.py`):
  * ADFECGDB: `model/data/adfecgdb/r01.edf` … (5 bản) — `python model/download_data.py --root model/data --only adfecgdb`
  * CinC 2013 set-a: `benchmark_dpss/pcdb/a01.hea` … (75 bản)
  * Silesia: `model/data/silesia/extracted/Data Records/…` — `python model/download_silesia.py` rồi giải nén
* Checkpoint: `model/checkpoints/fetalqrs_tcn_22_production.pt` và `fetalqrs_tcn_22_fold_01..11.pt` (có sẵn trong repo).

### 1.2. Khởi động (lệnh chính xác)

Mở terminal **tại gốc repo** (`D:\NCKHSV2026-2027`):

```powershell
# Windows PowerShell
$env:PYTHONIOENCODING = "utf-8"     # để in tiếng Việt ra console
python demo/app.py
```

```bash
# Linux / macOS
PYTHONIOENCODING=utf-8 python demo/app.py
```

Biến môi trường tuỳ chọn: `RELYFETAL_PORT=7860` (cổng), `RELYFETAL_THREADS=4` (số luồng CPU cho torch),
`RELYFETAL_AUTORUN=0` (tắt việc tự phân tích r01 khi mở trang).

### 1.3. Thời gian chờ và cách biết đã chạy

1. **Sau 5–15 s** terminal in dòng:
   `RelyFetal demo: http://127.0.0.1:7860   (Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.)`
   và Gradio in `* Running on local URL:  http://127.0.0.1:7860`. Lần đầu có thể lâu hơn vì torch/mne nạp chậm.
2. Mở trình duyệt vào **http://127.0.0.1:7860**. Trang tự phân tích **r01** ngay khi mở
   (mô hình chạy trên **cả 4 kênh** để chọn kênh → khoảng **2–4 s** với 2 luồng, xem bảng thời gian ở mục 6).
3. Đã chạy đúng khi thấy: dòng trạng thái *"Đã phân tích **r01** (EDF, 300 s, 4 kênh) — kênh **4** (auto (peakprob)) …"*,
   4 thẻ số (fHR ≈ 129 bpm, kênh 4/4, **đèn CAO (xanh)**, thời gian xử lý), và biểu đồ 5 tầng bên dưới.
4. Tắt demo: `Ctrl + C` trong terminal.

**Kiểm nhanh không cần trình duyệt** (2–3 phút, in kết quả 5 bản minh hoạ ra terminal và ghi
`demo/results/demo_check_showcase.json`):

```powershell
python demo/run_check.py --only r01,a09,B2_03,a02,a27 --out demo_check_showcase --threads 2
```

**Kiểm thử đơn vị** (17 kiểm thử, ≈ 15 s sau khi đã nạp dữ liệu): `python -m pytest demo/test_core.py -v`.

---

## 2. Giao diện — nhìn vào đâu

Hàng điều khiển trên cùng, từ trái sang phải:

| Ô | Ý nghĩa |
|---|---|
| **Nguồn dữ liệu** | *Minh hoạ (5 bản)* — đúng 5 bản cho buổi demo; *Bản ghi mẫu* — 97 bản trên đĩa (5 ADFECGDB + 75 CinC + 17 Silesia; bản CinC rò rỉ có cờ ⚠); *Tải lên file* |
| **Bản ghi minh hoạ** | r01 → a09 → B2_03 → a02 → a27, kèm lý do chọn ngay trên nhãn |
| **Kênh bụng** | *Tự động — peakprob (mặc định)* · *Tự động — PSD (Power-MF)* · 1/2/3/4 (chọn tay) |
| **Đèn tin cậy** | *Học (GBM, 12 chỉ số / đoạn 4 s)* (mặc định) · *Luật cứng (4 thành phần)* |
| **Phân tích** | nút chạy |

Bốn thẻ số: **fHR trung bình** · **Kênh được chọn** (quy tắc + điểm từng kênh, kênh chọn tô xanh, kèm F1 từng kênh nếu có nhãn)
· **Đèn tin cậy** (mức, điểm, lý do, và dòng cảnh báo vàng *"cổng hiệu chuẩn trên mô hình 5 ca"*) · **Thời gian xử lý**
(kênh đã chọn; cả 4 kênh = chi phí thật của quy tắc; checkpoint đang dùng).

Sáu tab:

1. **Tín hiệu (5 tầng)** — thô → lọc 10–60 Hz + nhịp mẹ (vạch đỏ) → phần dư sau khử mẹ (+ nhãn, vạch đen) → xác suất của mô hình + ngưỡng → kết quả (● TP xanh, ✕ FP đỏ, ▲ FN cam). Kéo chuột để phóng to, nhấp đúp để xem toàn bộ.
2. **Chọn kênh — cả 4 kênh** — bảng điểm peakprob / PSD / số nhịp / fHR / F1 từng kênh, và 4 dải phần dư với đỉnh mô hình; kênh được chọn tô nền xanh.
3. **Nhịp tim thai + đèn đoạn** — fHR theo cửa sổ 4 s (mô hình so với nhãn), bên dưới là cột *p(đoạn lỗi)* từng đoạn 4 s (xanh/vàng/đỏ); **đoạn bị từ chối tô nền đỏ** trên cả hai.
4. **So sánh với nhãn** — Se, PPV, F1, jitter, TP/FP/FN, danh sách sự kiện.
5. **Kết quả tổng hợp (60 bản sạch)** — bảng chọn kênh trên 60 bản CinC sạch và 22 chủ thể, kèm cảnh báo hậu kiểm.
6. **Nhật ký (JSON)** — tóm tắt để dán vào báo cáo.

---

## 3. Kịch bản demo 8–10 phút

Trước buổi gặp: khởi động demo **trước 5 phút**, để nguyên tab *Tín hiệu (5 tầng)* của r01 trên màn hình.
Giữ ô *Kênh bụng* = *Tự động — peakprob* và *Đèn tin cậy* = *Học* trừ khi kịch bản bảo đổi.

### Mở đầu (0:00–0:45) — nói gì

> "Đề tài làm một việc hẹp: từ **một** kênh điện tim ổ bụng của mẹ, tìm vị trí từng nhịp tim thai, và **tự biết khi nào không nên tin kết quả**.
> Mô hình nhỏ — 113 nghìn tham số, chạy CPU — huấn luyện trên 22 sản phụ. Demo này chạy đúng mã của bài báo, không có gì được chỉnh riêng cho demo."

### Bản 1 — **r01** (ADFECGDB, dễ) · 0:45–2:30

*Đã hiện sẵn trên màn hình.*

**Nói:** "Đây là bản ghi 5 phút, 4 kênh bụng, có nhãn từ điện cực da đầu thai nhi. Mô hình dùng checkpoint fold **chưa từng thấy** sản phụ này."

**Chỉ vào:**
* Thẻ *Kênh được chọn*: "Hệ thống chạy mô hình trên cả 4 kênh, chọn kênh mà mô hình **tự tin nhất** với các đỉnh nó tìm được — ở đây 4 kênh đều ≈ 0,998 nên kênh nào cũng tốt (F1 99,84–100 từng kênh)."
* Thẻ *Đèn tin cậy*: **CAO (xanh)**, điểm 0,999, 75/75 đoạn xanh. Chỉ vào dòng vàng: "Cổng này hiệu chuẩn trên mô hình 5 ca — tôi nói rõ để không bị hiểu là cổng 22 ca."
* Tab *Tín hiệu*: kéo phóng to 3 giây. Tầng 2: vạch đỏ = QRS mẹ, lớn gấp nhiều lần QRS thai. Tầng 3: sau khử mẹ chỉ còn nhịp thai nhỏ. Tầng 4: xác suất, ngưỡng 0,75 cố định trong checkpoint. Tầng 5: toàn ● xanh.
* Tab *So sánh với nhãn*: **F1 99,92 · Se 100,00 · PPV 99,84 · jitter 1,47 ms** (645 nhịp mô hình / 644 nhãn; 1 FP).

**Câu hỏi có thể gặp:** *"Sao không 100?"* → "1 nhịp dư trong 644; F1 mức chủ thể trên 22 ca là 97,56 (PSD), không phải 100 — bản này là bản dễ."

### Bản 2 — **a09** (CinC 2013 sạch, zero-shot) · 2:30–4:30

Chọn *a09* → **Phân tích** (≈ 0,5 s).

**Nói:** "Bộ dữ liệu khác, máy khác, chưa từng huấn luyện. Đây là bản mà cách chọn kênh cũ (PSD của Power-MF) **chọn sai kênh**."

**Chỉ vào:**
* Tab *Chọn kênh — cả 4 kênh*: bảng cho thấy peakprob **kênh 1 = 0,990**, các kênh còn lại 0,905–0,932 → chọn kênh 1, **F1 94,25**. Cột F1 của kênh 2 chỉ **19,35** — chính là kênh PSD sẽ chọn.
* Đổi *Kênh bụng* sang *Tự động — PSD* → **Phân tích**: kênh 2, F1 19,35, đèn **THẤP (đỏ)** (bám mẹ 53 %). "Đèn bắt được lỗi này — nhưng peakprob tránh được lỗi ngay từ đầu." Đổi lại *peakprob*.

**Nói thẳng phần liêm chính:** "Trên 60 bản CinC sạch, peakprob hơn PSD **+7,73 điểm F1** (KTC 95 % +3,82…+12,41, p Holm 0,0039), bản F1 < 50 từ 16 xuống 9, không bản nào mất quá 3,9 điểm. **Nhưng** đây là quy tắc chọn **sau khi** đã nhìn F1 từng kênh — quy tắc tôi khai báo trước là *gate*, và gate trượt Holm. Nên tôi ghi là *giả thuyết mạnh, chưa xác nhận, cần bộ dữ liệu thứ ba*." (Mở tab *Kết quả tổng hợp* nếu giảng viên muốn xem bảng.)

**Câu hỏi có thể gặp:** *"peakprob có nhìn nhãn không?"* → "Không. Nó chỉ dùng xác suất của chính mô hình. Kiểm chứng: xáo nhãn rồi chạy lại, 0/776 lựa chọn đổi; kiểm thử `test_peakprob_is_label_blind` bỏ nhãn đi vẫn chọn cùng kênh."
*"Chi phí?"* → "Phải chạy mô hình 4 lần thay vì 1: thẻ *Thời gian xử lý* hiện cả hai con số (kênh đã chọn ≈ 90 ms; cả 4 kênh ≈ 350 ms cho 60 s)."

### Bản 3 — **B2_03** (Silesia chuyển dạ, khó) · 4:30–6:15

Chọn *B2_03* → **Phân tích** (≈ 2,5 s).

**Nói:** "Bản chuyển dạ 5 phút, nhãn da đầu, fold không chứa sản phụ này. Mô hình **chỉ đạt F1 83,91** — đây là bản mô hình thất bại một phần, và điều tôi muốn cho thấy là hệ thống **tự nhận ra**."

**Chỉ vào:**
* Thẻ *Đèn tin cậy*: **THẤP (đỏ)** ở chế độ học, điểm 0,40; lý do liệt kê số đoạn đỏ.
* Tab *Nhịp tim thai + đèn đoạn*: các cột đỏ và **nền đỏ** = đoạn bị từ chối; đường fHR mô hình lệch khỏi đường nhãn đúng ở những đoạn đó.
* Đổi *Đèn tin cậy* sang *Luật cứng* → **Phân tích**: đèn **CAO** (0,83) — **sai**. "Đây là lý do chế độ học là mặc định: luật cứng bị lừa vì RR vẫn đều." Đổi lại *Học*.

**Câu hỏi có thể gặp:** *"Cổng học được huấn luyện trên gì?"* → "1 500 đoạn ADFECGDB, mô hình 5 ca; Silesia chưa từng tham gia huấn luyện cổng. Phân tích cổng trên 22 ca (LOSO) cho AUROC trong bản ghi 0,934 và xếp B2_03 là bản kém tin cậy nhất trong 22 — nhưng 5/24 quy tắc một đặc trưng cũng xếp đúng, nên tôi chưa gọi đó là bằng chứng mạnh."

### Bản 4 — **a02** (CinC sạch, mô hình bám nhịp mẹ) · 6:15–7:30

Chọn *a02* → **Phân tích**.

**Nói:** "Kiểu lỗi nguy hiểm nhất: mô hình theo **phần dư QRS mẹ** và báo một chuỗi nhịp rất đều ở 130 bpm — trông như thai."

**Chỉ vào:**
* Thẻ *Đèn tin cậy*: **THẤP (đỏ)**, lý do *"78 % nhịp thai trùng đỉnh R mẹ (ngẫu nhiên ≈ 13–22 %) → mô hình đang BÁM NHỊP MẸ"*.
* Tab *Nhịp tim thai*: đường mô hình ≈ 130 bpm, đường nhãn cao hơn.
* Tab *Chọn kênh*: peakprob **không** cứu được bản này (kênh 1 có F1 75,88 nhưng điểm 0,963 < kênh 2 0,970). "Tôi cho thấy cả trường hợp quy tắc thất bại."

### Bản 5 — **a27** (CinC sạch, gần như không có tín hiệu thai) · 7:30–8:30

Chọn *a27* → **Phân tích**.

**Nói:** "Bản không có tín hiệu thai dùng được ở kênh nào (F1 tốt nhất trong 4 kênh chỉ 33). Điều đúng duy nhất hệ thống có thể làm là nói **'tôi không chắc'**."

**Chỉ vào:** đèn **THẤP (đỏ)** ở cả hai chế độ (học 0,17; luật 0,43); tab *đèn đoạn* gần như toàn đỏ.

### Kết (8:30–9:30)

> "Tóm lại: một kênh, 113 nghìn tham số, F1 mức chủ thể 97,56 trên 22 ca — kém Power-MF **4 kênh** 1,27 điểm (KTC −3,08…+0,27, chưa có ý nghĩa), hơn Power-MF **1 kênh** 10,85 điểm (22/22 thắng).
> Ngoài miền còn kém: 60 bản CinC sạch F1 trung bình 82,01 với peakprob; 4 cách thích nghi miền đều thất bại, khoảng cách đó không phải dịch chuyển thống kê mà thích nghi miền sửa được — nguyên nhân còn lại chưa chứng minh được (phép thử nhìn thấy có âm tính giả 18 %). Vì thế cổng từ chối là phần quan trọng nhất.
> Còn thiếu để lên tạp chí: một bộ dữ liệu có nhãn fQRS thật ngoài những gì đã dùng (hiện KHÔNG có bộ công khai nào — đã kiểm 12/09), 3–5 seed cho kết quả chính, trung tâm ghi thứ hai."

Kết bằng dòng miễn trừ ở cuối trang.

### Câu hỏi chung có thể gặp

| Câu hỏi | Trả lời ngắn |
|---|---|
| Tại sao chỉ dùng một kênh? | Thiết bị đeo/rẻ tiền thường chỉ có 1–2 kênh; tách nguồn đa kênh đáng giá 12,12 điểm cho chính Power-MF, mạng đơn kênh lấy lại 89,5 % số đó. |
| Ngưỡng 0,75 lấy ở đâu? | Lưu trong checkpoint, chọn trên tập validation của fold; không chỉnh theo bản ghi. |
| Có so với DPSS/các phương pháp khác chưa? | Power-MF (Jaeger 2024) đã chạy lại bằng Octave và kiểm chứng ngoài (B1 99,40 so với 99,46 công bố). DPSS chưa chạy lại — nói rõ là còn thiếu. |
| Kiến trúc có quan trọng không? | 7 họ cùng tham số: TCN 97,64 ~ rf_wide 97,63 ~ tcn_ms 97,62 (tương đương TOST); đã dừng đào vào kiến trúc. |
| Dải lọc 10–60 Hz có quan trọng không? | Với TCN: +2,44 [−0,05; +6,30] kênh PSD, ≈ 0 trung bình 4 kênh → không quan trọng. Con số +11 trước đây đã rút. |
| Dùng lâm sàng được chưa? | Chưa. Lệch STV +20,5 ms trên CinC → không dùng làm máy đo STV. Đây là bản mẫu nghiên cứu. |

---

## 4. Kế hoạch dự phòng

| Sự cố | Làm gì |
|---|---|
| Trang không mở / cổng 7860 bận | `$env:RELYFETAL_PORT = "7870"; python demo/app.py` rồi mở http://127.0.0.1:7870 |
| Gradio lỗi khi khởi động | Chạy `python demo/run_check.py --only r01,a09,B2_03,a02,a27 --out demo_check_showcase --threads 2` — in bảng 5 bản (kênh, F1, Se, PPV, đèn học/luật, bám mẹ, ms) ra terminal; giải thích theo bảng đó |
| Biểu đồ trắng (WebGL bị chặn) | Vẫn có thẻ số và tab *So sánh với nhãn*; mở ảnh trong `demo/screenshots/` cho phần biểu đồ |
| Chậm bất thường (> 30 s một bản) | Máy đang bận: đặt `RELYFETAL_THREADS=2`, tránh bản Silesia B1 (20 phút) |
| Không có mạng / thiếu dữ liệu | Ảnh chụp sẵn `demo/screenshots/01…12_*.png` theo đúng thứ tự kịch bản (mục 5) |
| Giảng viên hỏi con số không nhớ | Tab *Kết quả tổng hợp* đọc trực tiếp từ JSON; hoặc `demo/results/demo_check_showcase.json` |

---

## 5. Ảnh chụp màn hình (`demo/screenshots/`)

Tạo lại bằng `python demo/screenshot.py` (cần `pip install playwright && python -m playwright install chromium`; ≈ 1–2 phút, server tạm ở cổng 7862).

| Tệp | Nội dung | Dùng ở bước |
|---|---|---|
| `01_r01_tong_quan.png` | r01: thẻ số + 5 tầng tín hiệu | Bản 1 |
| `02_r01_the_so.png` | r01: 4 thẻ số (đèn xanh, kênh 4/4) | Bản 1 |
| `03_r01_so_sanh.png` | r01: Se/PPV/F1/jitter | Bản 1 |
| `04_a09_chon_kenh.png` | a09: bảng + 4 kênh, kênh 1 tô xanh | Bản 2 |
| `05_a09_the_so.png` | a09 peakprob: đèn xanh, F1 94 | Bản 2 |
| `06_a09_psd_the_so.png` | a09 PSD: kênh 2, đèn đỏ, F1 19 | Bản 2 |
| `07_B2_03_fhr_den_doan.png` | B2_03: fHR + đoạn đỏ tô nền | Bản 3 |
| `08_B2_03_the_so.png` | B2_03: đèn ĐỎ (học) | Bản 3 |
| `09_a02_the_so.png` | a02: đèn ĐỎ, bám nhịp mẹ 78 % | Bản 4 |
| `10_a02_fhr.png` | a02: fHR mô hình bám mẹ | Bản 4 |
| `11_a27_the_so.png` | a27: đèn ĐỎ, không tín hiệu | Bản 5 |
| `12_tong_hop.png` | tab Kết quả tổng hợp (60 bản sạch) | Kết |

Tự chụp tay nếu cần: Windows `Win + Shift + S`, lưu vào cùng thư mục với tên như trên.

---

## 6. Kết quả 5 bản minh hoạ (đã chạy thật, `demo/results/demo_check_showcase.json`)

Quy tắc chọn kênh peakprob, 2 luồng CPU, máy đang chạy việc khác (thời gian là cận trên).

| Bản ghi | Bộ dữ liệu | Checkpoint | Kênh | F1 | Se | PPV | Jitter | Đèn học | Đèn luật | Bám mẹ | Xử lý kênh chọn | Cả 4 kênh |
|---|---|---|--:|--:|--:|--:|--:|---|---|--:|--:|--:|
| r01 | ADFECGDB | 22 ca fold 05 | 4 | 99,92 | 100,00 | 99,84 | 1,47 ms | CAO 0,999 | CAO 0,861 | 0,16 | ≈ 0,47 s | ≈ 1,9 s |
| a09 | CinC sạch | 22 ca production | 1 | 94,25 | 94,62 | 93,89 | 3,83 ms | CAO 0,914 | CAO 0,944 | 0,18 | ≈ 0,09 s | ≈ 0,35 s |
| a09 (PSD) | CinC sạch | 22 ca production | 2 | 19,35 | 18,46 | 20,34 | 21,6 ms | THẤP 0,194 | TB 0,601 | 0,53 | ≈ 0,08 s | ≈ 0,10 s |
| B2_03 | Silesia B2 | 22 ca fold 11 | 4 | 83,91 | 85,20 | 82,66 | 6,64 ms | **THẤP 0,401** | CAO 0,834 (sai) | 0,18 | ≈ 0,40 s | ≈ 1,6 s |
| a02 | CinC sạch | 22 ca production | 2 | 24,91 | 22,50 | 27,91 | 21,9 ms | THẤP 0,544 (bám mẹ) | THẤP 0,859 (bám mẹ) | 0,78 | ≈ 0,08 s | ≈ 0,32 s |
| a27 | CinC sạch | 22 ca production | 3 | 32,94 | 31,11 | 35,00 | 17,8 ms | THẤP 0,173 | THẤP 0,428 | 0,43 | ≈ 0,08 s | ≈ 0,35 s |

Nguồn: lần chạy `demo/core.py` ngày 2026-09-12 (tệp scratch `check5.json`, cùng số liệu với `demo_check_showcase.json`).
Toàn bộ chu trình kể cả đọc file và vẽ trong trình duyệt: r01 ≈ 3,5 s, a09/a02/a27 ≈ 0,5 s, B2_03 ≈ 2,3 s.

---

## 7. Truy nguồn con số dùng khi nói

| Con số | Tệp |
|---|---|
| peakprob so với PSD trên 60 bản sạch: 82,01 / 74,28, +7,73 [+3,82; +12,41], p Holm 0,0039; gate p Holm 0,051 | `analysis/dulieu_results.json` → `chon_kenh_60_sach.bang` |
| Kiểm rò rỉ nhãn 0/776 | `analysis/chonkenh_results.json` → `kiem_tra_ro_ri` |
| 22 chủ thể: Rely 97,56, PMF4 98,83 (−1,27 [−3,08; +0,27]), PMF1 86,71 (+10,85, 22/22) | `analysis/chonkenh_results.json` → `he_qua_hau_kiem.bang.psd` |
| F1 từng bản/từng kênh a09, a02, a27, B2_03 | `analysis/chonkenh_results.json` → `F1_tung_ban_ghi` |
| 15 bản CinC rò rỉ | `analysis/dulieu_results.json`, `analysis/DULIEU.md` |
| Cổng 22 ca AUROC 0,934, xếp hạng B2_03/B1_07/B1_06 | `analysis/gate22_results.json` |
| Kiến trúc, dải lọc, thích nghi miền | `analysis/kientruc_results.json`, `analysis/thichnghi_results.json` / `analysis/THICHNGHI.md` |
| Fold của từng chủ thể | `benchmark_dpss/eval_22.json` → `folds` |
