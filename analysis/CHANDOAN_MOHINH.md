> **⚠ CẢNH BÁO (12/09/2026, sau vòng 7).** Tài liệu này được viết khi CinC 2013 set-a còn được tính trên **75 bản ghi**. Sau đó xác định 15 bản (a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25) là bản sao nguyên văn của dữ liệu huấn luyện ADFECGDB — điều ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014] và nhóm đã bỏ sót. **Mọi con số CinC dưới đây (79,40 / 85,60 / 86,87 / 71,21 / 62,82, AUROC 0,980…) bị thổi 3–7 điểm và đã bị rút.** Số chính thức trên **60 bản sạch**: PSD 74,28 · peakprob 82,01 · oracle 83,60 (`analysis/dulieu_results.json`, `benchmark_dpss/eval_cinc60_sach.json`). Kết luận định tính trong tài liệu giữ nguyên trừ khi ghi khác trong `docs/nhat_ky/THAMDINH_VONG7.md`. Cụm "tiền đăng ký" trong tài liệu này **không đúng** — tệp khai báo không neo git.

> **RÚT LẠI (vòng 7, 12/09/2026).** Kết luận "Mô hình KHÔNG phải nút thắt" dưới đây **không còn đứng được**:
> phép thử nhìn thấy dùng để định nghĩa nhóm lỗi (b) "không có tín hiệu" có tỉ lệ âm tính giả **18,0 %
> [12,1; 25,0]** trên 60 bản CinC sạch (ngưỡng khai báo 10 %), 55–70 % trên bản có F1 < 90; sau hiệu chỉnh tỉ
> lệ dư địa "thiếu tín hiệu" từ 86,0 % xuống 26,0 % nhưng con số hiệu chỉnh cũng không định danh được.
> Phát biểu đúng: *chưa chứng minh được mô hình là hay không là nút thắt*. Các số "71 % dư địa", "1,85 điểm
> thuộc mô hình", "8 bản giới hạn cứng" đều đã rút. Chi tiết: `analysis/XACNHAN.md` (việc 4),
> `analysis/xacnhan_results.json → viec4_phep_thu_nhin_thay`. Tệp này giữ nguyên để truy vết.

# Chẩn đoán: mô hình có phải nút thắt không?

> ## KẾT LUẬN
>
> **Mô hình KHÔNG phải nút thắt.**
>
> Ba phép thử độc lập đều nói cùng một điều, và không phép nào ủng hộ việc nâng cấp bộ dò:
>
> 1. **Không bỏ sót nhịp đang nhìn thấy.** Nhóm (a) chỉ chiếm **5,4%** (22 chủ thể) và **2,0%**
>    (CinC 75) tổng số lỗi sau khi dùng quy tắc chọn kênh `peakprob` — **thấp hơn mức ngẫu nhiên
>    của chính phép gán** (15,2% / 11,2%) tương ứng 2,8 lần và 5,6 lần.
> 2. **Không thiếu năng lực.** Nhân 4 lần số tham số (113 481 → 450 961) chỉ đổi được **+0,26
>    điểm** F1 trong mẫu. Ở bề rộng sản xuất, 3/4 chủ thể đã đạt 99,8–100 **trong mẫu**.
> 3. **Không hỏng khâu định vị.** Sai số thời điểm trên các nhịp đã bắt đúng là **3,76 ms** (trung
>    vị, 67 bản ghi CinC thường) so với dung sai chấm **±50 ms**.
>
> Dư địa còn lại được quy cho "bộ dò" là **6,36 điểm** trên CinC 75. Mổ xẻ ra thì **71% của nó
> (4,52 điểm) nằm trên 9 bản ghi mà tín hiệu thai không nhìn thấy được trên *bất kỳ* kênh nào
> trong bốn kênh** — đó là giới hạn **thu tín hiệu**, không phải giới hạn mô hình. Phần thực sự
> còn lại cho mô hình là **1,85 điểm**, rải trên 58 bản ghi.
>
> **RÚT LẠI MỘT KHUYẾN NGHỊ CỦA CHÍNH TÀI LIỆU NÀY (bản 10:55 cùng ngày):** khuyến nghị số 2
> "sửa khâu định vị thời điểm vì 58–68% lỗi thuộc nhóm (e)" **không đứng vững**. Xem mục 1.3.

Tài liệu này trả lời ba việc của nhiệm vụ M1. Mọi con số truy về tệp JSON trên đĩa; mỗi bảng ghi
rõ khóa JSON tương ứng.

Lệnh chạy lại toàn bộ (đặt `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1` trước):

```
python analysis/chandoan.py            # suy luận + phân loại lỗi              (~6 phút)
python analysis/chandoan_recls.py      # phân loại lại nhóm (e) chặt           (~1 phút)
python analysis/chandoan_tol.py        # quét dung sai                         (~1 phút)
python analysis/chandoan_capacity.py --epochs 8 --widths 40,80   # trần năng lực (~52 phút)
python analysis/chandoan_hard.py       # ba bản ghi khó + hình
python analysis/chandoan_agg.py        # tổng hợp + hình chính
python analysis/chandoan_m1.py         # BỔ SUNG: phổ lỗi theo quy tắc, ngân sách  (~20 giây)
python analysis/chandoan_m1_jitter.py  # BỔ SUNG: độ chính xác định vị          (~5 giây)
```

Hai script `chandoan_m1*.py` **không chạy suy luận mới**: chúng đọc lại bộ nhớ đệm đếm lỗi từng
bản ghi × từng kênh (`chandoan_raw.json`) và lựa chọn kênh của từng quy tắc
(`chonkenh_results.json`), nên rẻ và tái lập được tức thì.

**Kiểm tra nhất quán đã chạy** (`m1_bo_sung.kiem_tra_nhat_quan`): 0/97 bản ghi lệch chỉ số kênh
giữa hai bộ nhớ đệm; F1 trung bình mức bản ghi của cả 5 quy tắc tính lại từ `chandoan_raw.json`
khớp `chonkenh_results.json` đến **0,0000 điểm** trên cả hai miền. Hai đường tính độc lập cho
cùng một số.

---

## 0. Cách phân loại lỗi (đọc trước khi tin các con số)

Với mỗi bản ghi × kênh, chấm theo đúng quy ước CinC 2013 (ghép tham lam 1‑1, ±50 ms, 1000 Hz),
rồi **mỗi** FN và **mỗi** FP được gán đúng **một** nhóm, theo thứ tự cố định khai báo trước:

| nhóm | định nghĩa vận hành | thuộc về ai |
|---|---|---|
| **(a)** bỏ nhịp có tín hiệu | FN, và tại vị trí nhãn có đỉnh trong phần dư 10–60 Hz vượt ngưỡng "nhìn thấy" | **mô hình** |
| **(b)** không có tín hiệu đo được | FN, và tại vị trí nhãn không có gì vượt ngưỡng | dữ liệu / thu tín hiệu |
| **(c)** liên quan nhịp mẹ | FN hoặc FP nằm trong ±60 ms của một đỉnh mẹ (`M.detect_maternal_qrs`) | khâu khử mẹ |
| **(e)** lệch thời điểm | FN và FP là **cặp láng giềng gần nhất hai chiều**, lệch nhau (50, 150] ms | **mô hình** |
| **(d1)** phát hiện đôi | FP trong 400 ms của một TP | mô hình / ngưỡng |
| **(d2)** FP ngẫu nhiên | phần còn lại | nhiễu |

**Phép thử "nhìn thấy"** (phân biệt (a) với (b)): tại mỗi nhãn lấy `z` = biên độ đỉnh trong ±30 ms
của phần dư sau khử mẹ, chia cho nhiễu cục bộ (MAD trên khối 4 s). Ngưỡng τ = phân vị 95 của
**phân bố rỗng** đo bằng chính thống kê đó tại các vị trí "an toàn" (cách mọi nhãn ≥120 ms, cách
mọi đỉnh mẹ ≥80 ms). Vậy **độ đặc hiệu cố định 95%**. **Độ nhạy** đo trên các nhịp mô hình đã bắt
đúng (TP — chắc chắn là nhịp thai thật): 0,95–0,99 trên 22 chủ thể, 0,86–0,89 trên CinC 75. Tỉ lệ
(a) trong (a)+(b) được báo cả **thô** lẫn **hiệu chỉnh** theo `quan sát = p·nhạy + (1−p)·0,05`.

**Mức ngẫu nhiên — đây là phần quan trọng nhất của mục này.** Mọi tiêu chí "gần nhau" đều có xác
suất trúng do mật độ nhịp (RR thai ≈ 390–460 ms). Nên mỗi phổ lỗi đi kèm một **phân bố rỗng**:
chạy lại đúng phép gán trên chuỗi phát hiện đã bị làm nhiễu đều ±500 ms (giữ nguyên mật độ, phá
canh chỉnh từng nhịp), 3 lần. Cột `pct_null` là **tỉ lệ phần trăm trong tổng số lỗi rỗng** — cùng
đơn vị với cột quan sát, nên **so sánh trực tiếp được** (đây là điểm bản trước đã dè dặt quá mức
và vì thế đọc sai nhóm (e); xem 1.3).

Nguồn: `analysis/chandoan.py`, `chandoan_m1.py`; kết quả thô `chandoan_raw.json`,
`chandoan_strict.json`; sự kiện từng nhịp `chandoan_events.npz`.

---

## 1. VIỆC 1 — Phổ lỗi trên cả hai quy tắc chọn kênh

Micro (gộp mọi lỗi trên mọi bản ghi). `chandoan_results.json → m1_bo_sung.pho_loi_theo_quy_tac`,
khóa `"<quần thể>|<quy tắc>"`.

### 1.1 Bảng chính

**22 chủ thể** (LOSO, mô hình 22 ca):

| quy tắc | số lỗi | lỗi/1000 nhịp | (a) | (b) | (c) | (e) | (d1) | (d2) | F1 macro |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| psd *(đang dùng)* | 2 041 | 56,2 | **3,8%** | 8,4% | 7,7% | 68,5% | 3,2% | 8,4% | 97,56 |
| gate *(khai báo trước)* | 854 | 23,5 | **6,7%** | 6,0% | 11,9% | 57,3% | 6,4% | 11,7% | 98,61 |
| peakprob *(hậu kiểm)* | 1 400 | 38,6 | **5,4%** | 5,8% | 8,7% | 64,7% | 4,9% | 10,5% | 98,22 |
| oracle | 845 | 23,3 | 6,6% | 6,2% | 12,0% | 56,9% | 6,5% | 11,8% | 98,63 |
| *mức ngẫu nhiên* | — | — | *15,2%* | *0,3%* | *7,3%* | *61,3%* | *0,1%* | *15,7%* | — |

**CinC 75** (mô hình 22 ca, người chấm độc lập):

| quy tắc | số lỗi | lỗi/1000 nhịp | (a) | (b) | (c) | (e) | (d1) | (d2) | F1 macro |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| psd *(đang dùng)* | 4 164 | 397,2 | **1,0%** | 19,3% | 9,1% | 58,6% | 1,2% | 10,8% | 79,40 |
| gate *(khai báo trước)* | 3 137 | 299,2 | **1,5%** | 18,8% | 9,0% | 58,2% | 1,1% | 11,4% | 84,54 |
| peakprob *(hậu kiểm)* | 2 917 | 278,2 | **2,0%** | 18,9% | 8,7% | 57,7% | 1,3% | 11,3% | 85,60 |
| oracle | 2 678 | 255,4 | 2,1% | 17,6% | 8,8% | 58,3% | 1,5% | 11,7% | 86,87 |
| *mức ngẫu nhiên* | — | — | *11,2%* | *4,7%* | *6,8%* | *62,2%* | *0,3%* | *14,9%* | — |

### 1.2 Trả lời câu hỏi then chốt

> **Sau khi đã dùng `peakprob`, bao nhiêu phần trăm lỗi còn lại thuộc nhóm (a) — bỏ nhịp trong
> khi tín hiệu thai nhìn thấy được trên chính kênh đang đọc?**

**5,4% trên 22 chủ thể và 2,0% trên CinC 75** (thô); sau hiệu chỉnh độ nhạy của phép thử:
**5,2%** và **1,2%** (`pct_a_corrected`). Mức ngẫu nhiên của chính nhóm (a) là **15,2%** và
**11,2%**, tức (a) quan sát được **thấp hơn mức ngẫu nhiên 2,8 lần** (22 chủ thể) và **5,6 lần**
(CinC 75); tính trên số đã hiệu chỉnh thì 2,9 lần và 9,3 lần.

Điều này đúng với **mọi** quy tắc chọn kênh, kể cả oracle (6,6% / 2,1%) — nên nó **không** phải
là sản phẩm phụ của việc chọn kênh nào.

**Kết luận việc 1: tỉ lệ (a) THẤP.** Theo đúng quy tắc quyết định khai báo trước của nhiệm vụ,
điều này nói rằng **nâng cấp kiến trúc để "bắt được nhiều nhịp hơn" sẽ vô ích**. Bộ dò gần như
không bao giờ bỏ sót một nhịp đang hiện rõ trên kênh nó đang đọc.

### 1.3 RÚT LẠI: nhóm (e) **không** chứng minh được là lỗi định vị

Bản 10:55 của tài liệu này viết *"(e) chiếm 58–68%… Hướng cụ thể: tinh chỉnh vị trí đỉnh…, siết
`heatmap_sigma`, thêm đầu ra hồi quy độ lệch"* và xếp đó là hướng đầu tư số 2. **Rút lại.** Ba
bằng chứng ngược:

1. **(e) không vượt mức ngẫu nhiên trên CinC.** Trên 67 bản ghi CinC thường với kênh oracle, (e)
   quan sát **61,7%** so với mức ngẫu nhiên **63,1%** — quan sát còn *thấp hơn* rỗng. Trên CinC 75
   với `peakprob`: 57,7% so với 62,2%. Trên 22 chủ thể: 64,7% so với 61,3%, chênh +3,4 điểm.
   Nói cách khác, tỉ lệ (e) là thứ **hình học của phép ghép cặp tự sinh ra** khi RR ≈ 400 ms và
   cửa sổ (50, 150] ms chiếm một phần tư chu kỳ; nó gần như không mang thông tin.
2. **Sai số định vị trên các nhịp đã bắt đúng rất nhỏ.** `chandoan_m1_jitter.json`, CinC 75, mô
   hình 22 ca, quy tắc `peakprob`:

   | quần thể | n | jitter trung vị | trung bình | phân vị 90 | max |
   |---|---:|---:|---:|---:|---:|
   | **67 bản ghi thường** | 67 | **3,76 ms** | 5,70 | — | 21,89 |
   | 8 bản giới hạn cứng | 8 | 17,36 ms | 19,32 | — | 27,69 |
   | bản ghi F1 ≥ 90 | 53 | 2,72 ms | 4,24 | — | 13,52 |
   | bản ghi F1 50–90 | 13 | 10,89 ms | 10,42 | — | 16,76 |
   | bản ghi F1 < 50 | 9 | 17,76 ms | 19,61 | — | 27,69 |
   | *toàn bộ 75* | 75 | 4,01 | 7,16 | 16,26 | 27,69 |

   Dung sai chấm là **±50 ms**. Ngay cả bản ghi tệ nhất cũng có jitter 27,7 ms, tức **vẫn nằm
   trong dung sai**. Không có bản ghi nào mà "mạng đặt đỉnh lệch đi" đủ để rơi ra ngoài ±50 ms một
   cách hệ thống.
3. **Jitter lớn là *hệ quả* của bản ghi xấu, không phải nguyên nhân.** Jitter đi từ 2,72 ms
   (F1 ≥ 90) lên 17,76 ms (F1 < 50) **cùng chiều** với chất lượng bản ghi. Ở đoạn tín hiệu yếu,
   mạng bám vào một thứ khác gần đó; đó là vấn đề **tỉ số tín hiệu trên nhiễu**, và một đầu ra
   hồi quy độ lệch không sửa được.

**Phát biểu đúng:** nhóm (e) là một **nhóm còn lại có mức ngẫu nhiên cao**, không phải một chẩn
đoán. Con số "58–68% lỗi là (e)" **không được trích dẫn** như bằng chứng cho bất cứ điều gì.

### 1.4 Chọn kênh đã chuyển lỗi từ nhóm nào sang nhóm nào

`m1_bo_sung.chuyen_dich_loi_psd_sang_peakprob` — số lỗi tuyệt đối, psd → peakprob:

| nhóm | 22 chủ thể | CinC 75 |
|---|---:|---:|
| (a) bỏ nhịp có tín hiệu | 78 → 76 (**−2**) | 43 → 59 (**+16**) |
| (b) không có tín hiệu | 171 → 81 (−90) | 803 → 552 (−251) |
| (c) nhịp mẹ | 157 → 122 (−35) | 378 → 253 (−125) |
| (e) lệch thời điểm | 1 399 → 906 (−493) | 2 439 → 1 684 (−755) |
| (d1) phát hiện đôi | 65 → 68 (+3) | 51 → 39 (−12) |
| (d2) FP ngẫu nhiên | 171 → 147 (−24) | 450 → 330 (−120) |
| **tổng** | **2 041 → 1 400 (−641)** | **4 164 → 2 917 (−1 247)** |

Đọc bảng này: chọn kênh tốt hơn **xóa lỗi ở mọi nhóm trừ (a)**. Nhóm (a) **tăng nhẹ trên CinC**
(+16 lỗi) — hợp lý và đáng chú ý: khi đổi sang kênh có tín hiệu thật, những nhịp trước đây "không
nhìn thấy được" (b) nay trở thành "nhìn thấy được nhưng vẫn trượt" (a). Đó là phần duy nhất mà
mô hình **thật sự** nợ, và nó chỉ có **59 lỗi trên 10 484 nhịp** của CinC 75.

---

## 2. VIỆC 2 — Trần năng lực

### 2.1 Nhật ký huấn luyện

`model/train_22_log.txt` **chỉ ghi loss huấn luyện, không ghi loss kiểm tra từng fold** (dòng
`epoch k/4 loss ...`). Loss huấn luyện giảm đều 0,345 → 0,258 qua 4 epoch ở mọi fold và **vẫn đang
giảm khi dừng**; không quan sát được loss val nên **không thể** đọc khoảng cách train–test từ nhật
ký. Đây là một hạn chế của quy trình hiện tại (mục 5). Câu hỏi năng lực vì vậy được trả lời bằng
hai thí nghiệm chạy mới.

### 2.2 Phép thử A — trong mẫu ở đúng quy mô thật

`fetalqrs_tcn_22_production.pt` được huấn luyện trên **cả 22 chủ thể**; đánh giá nó trên chính 22
chủ thể đó là **trong mẫu**. `chandoan_capacity.json → A_insample_22`:

| | F1 kênh PSD | F1 TB4 |
|---|---:|---:|
| TRONG mẫu (production_22 trên chủ thể nó đã học) | **99,31** | 98,64 |
| NGOÀI mẫu (LOSO, 11 fold) | 97,56 | 96,59 |
| khoảng cách | **+1,75** | +2,05 |

* **19 chủ thể dễ**: hiệu trong‑mẫu − ngoài‑mẫu là **0,00 đến +0,52** (r10 còn −0,15). Mô hình
  chạm trần ở cả hai chế độ; **không hề học thuộc**.
* **3 bản ghi khó**: B1_06 89,45 → **98,01** (+8,56); B1_07 86,56 → **98,05** (+11,49);
  B2_03 79,72 → **93,43** (+13,71).

### 2.3 Phép thử B — học thuộc trên 4 chủ thể, hai bề rộng

Huấn luyện lại từ đầu trên `['r01','B2_12','B2_03','B1_07']` (2 dễ + 2 khó), **không tăng cường**,
bước trượt 2 s (ít đoạn hơn `train_22` ⇒ *dễ* học thuộc hơn ⇒ thiên về phía "mô hình đủ năng
lực"), 8 epoch, ngưỡng chọn **trong mẫu** (nên mọi F1 dưới đây là **chặn trên**).
`chandoan_capacity.json → B_memorise`:

| | bề rộng 40 *(đúng kiến trúc sản xuất)* | bề rộng 80 *(≈4× tham số)* |
|---|---:|---:|
| số tham số | 113 481 | 450 961 |
| loss đầu → cuối (8 epoch) | 0,5652 → 0,2617 | 0,5209 → 0,2502 |
| **F1 trong mẫu, kênh PSD** | **99,08** | **99,33** |
| F1 trong mẫu, trung bình 16 (chủ thể × kênh) | 97,59 | 98,44 |

Từng chủ thể, F1 **trong mẫu** (PSD / TB4 / oracle):

| chủ thể | bề rộng 40 | bề rộng 80 | chênh (oracle) |
|---|---|---|---:|
| r01 | 99,92 / 99,92 / 99,92 | 99,92 / 99,96 / 100,00 | +0,08 |
| B2_12 | 100,00 / 99,56 / 100,00 | 100,00 / 99,85 / 100,00 | +0,00 |
| B1_07 | 99,84 / 99,93 / 99,98 | 99,90 / 99,94 / 99,97 | −0,02 |
| **B2_03** | **96,55** / 90,94 / 96,76 | **97,51** / 94,01 / 97,72 | **+0,97** |
| | | **tổng F1 trong mẫu PSD** | **+0,26** |

### 2.4 Đọc kết quả năng lực

* **Ở bề rộng sản xuất, 3/4 chủ thể đã đạt 99,84–100 trong mẫu.** Mạng 113 481 tham số **thừa sức**
  biểu diễn ánh xạ trên các chủ thể nó được nhìn thấy. Không thiếu năng lực.
* **Nhân 4 lần tham số đổi được +0,26 điểm.** Gần như toàn bộ phần tăng đó (+0,97) rơi vào **một**
  chủ thể — B2_03, chủ thể SNR thấp — và **ngay cả ở 4× tham số, trong mẫu, B2_03 vẫn chỉ 97,51,
  không tới 100**. Nếu vấn đề là năng lực thì 4× tham số phải kéo B2_03 lên ~100; nó không.
* **Ghép A với B:** khoảng cách trong‑mẫu/ngoài‑mẫu lớn (+8,56 … +13,71 trên ba bản ghi khó) trong
  khi trần trong‑mẫu đã ≈100 ⇒ theo đúng quy tắc quyết định của nhiệm vụ, **vấn đề là TỔNG QUÁT
  HÓA, không phải năng lực**; và lời giải là **dữ liệu / chính quy / thích nghi chủ thể**, không
  phải kiến trúc.
* Hệ quả trực tiếp cho câu hỏi mở "TCN hay `cnn_l`" (`pilot_evidence/arch_loro_merged.json`):
  **không nằm trên đường tới đích**. Chênh ~1,4 điểm ở giao thức cũ 5 chủ thể không nói gì về một
  nút thắt mà chính nó không phải là nút thắt.

---

## 3. VIỆC 3 — Các bản ghi khó

### 3.1 Ngân sách sai số CinC 75 theo từng quy tắc chọn kênh

`m1_bo_sung.ngan_sach_sai_so_cinc`. Mỗi bản ghi được tách: `(100 − F1_oracle)` là phần **bộ dò /
giới hạn**, `(F1_oracle − F1_quy_tắc)` là phần **chọn kênh**; chia cho 75 để ra điểm macro.

| quy tắc | F1 | thiếu tới 100 | chọn kênh (67 bản) | chọn kênh (8 bản vô vọng) | **BỘ DÒ (67 bản)** | **GIỚI HẠN CỨNG (8 bản)** |
|---|---:|---:|---:|---:|---:|---:|
| psd *(đang dùng)* | 79,40 | 20,60 | 6,86 | 0,61 | **6,36** | **6,77** |
| gate *(khai báo trước)* | 84,54 | 15,46 | 1,44 | 0,89 | **6,36** | **6,77** |
| **peakprob** *(hậu kiểm)* | **85,60** | **14,40** | **0,84** | 0,43 | **6,36** | **6,77** |
| rrcv | 83,98 | 16,02 | 1,85 | 1,04 | 6,36 | 6,77 |
| gate4 | 84,77 | 15,23 | 1,38 | 0,72 | 6,36 | 6,77 |
| oracle | 86,87 | 13,13 | 0,00 | 0,00 | **6,36** | **6,77** |

Cột psd tái lập **chính xác** phân rã 6,86 / 0,61 / 6,36 / 6,77 mà chủ nhiệm đã tự tính từ
`eval_cinc75.json` — một kiểm chứng chéo độc lập của cả hai đường tính.

Đọc bảng: **M5 đã gần như đóng xong mục chọn kênh.** Từ 6,86 + 0,61 = 7,47 điểm xuống còn
0,84 + 0,43 = **1,27 điểm**. Sau `peakprob`, mục lớn nhất **còn lấy được** trên lý thuyết là
**BỘ DÒ 6,36 điểm** (giới hạn cứng 6,77 điểm theo định nghĩa là không lấy được).

### 3.2 Vậy 6,36 điểm "bộ dò" thực ra là gì? — câu trả lời chính của nhiệm vụ

`m1_bo_sung.bo_do_67_chi_tiet`. Phần này **rất tập trung**, không rải đều:

* **48/67 bản ghi đã ≥ 95** trên kênh oracle. Chỉ 19 bản còn đáng kể.
* **10 bản ghi chiếm 79%** của 6,36 điểm; 5 bản chiếm 48%; 20 bản chiếm 97%.

| # | bản ghi | F1 oracle | đóng góp | cộng dồn | % nhãn **nhìn thấy** (kênh tốt nhất) | (a)% |
|---:|---|---:|---:|---:|---:|---:|
| 1 | a32 | 52,11 | 0,638 | 10% | **0,28** | 0,7% |
| 2 | a75 | 52,51 | 0,633 | 20% | **0,25** | 1,6% |
| 3 | a50 | 52,71 | 0,631 | 30% | **0,30** | 0,8% |
| 4 | a18 | 54,98 | 0,600 | 39% | **0,31** | 5,3% |
| 5 | a64 | 57,04 | 0,573 | 48% | **0,24** | 1,7% |
| 6 | a63 | 61,19 | 0,517 | 56% | **0,25** | 0,0% |
| 7 | a38 *(chú thích sai)* | 65,12 | 0,465 | 64% | 0,35 | 3,8% |
| 8 | a10 | 70,89 | 0,388 | 70% | 0,72 | 19,6% |
| 9 | a02 | 75,88 | 0,322 | 75% | 0,67 | 6,7% |
| 10 | a16 | 78,79 | 0,283 | 79% | 0,36 | 0,0% |

Chia 6,36 điểm theo việc tín hiệu thai **có nhìn thấy được trên kênh tốt nhất hay không**
(ngưỡng 0,50):

| | số bản ghi | điểm | tỉ lệ | quy cho ai |
|---|---:|---:|---:|---|
| tín hiệu **KHÔNG** nhìn thấy (< 0,50) | 9 | **4,52** | **71%** | **giới hạn THU TÍN HIỆU** |
| tín hiệu **CÓ** nhìn thấy (≥ 0,50) | 58 | **1,85** | 29% | phần có thể do mô hình |

Và thang độ nhìn thấy xếp thành một **bậc thang đơn điệu** theo chất lượng bản ghi:

| nhóm | n | % nhãn nhìn thấy (trung vị, kênh tốt nhất) |
|---|---:|---:|
| 67 bản: F1 oracle ≥ 95 | 48 | **1,00** |
| 67 bản: F1 oracle < 95 | 19 | **0,51** |
| 8 bản giới hạn cứng | 8 | **0,19** |

> **Trả lời thẳng câu hỏi của nhiệm vụ — "6,36 điểm đó có lấy được không, và bằng cách nào":**
> **Phần lớn là KHÔNG, và không bằng kiến trúc.** 4,52 trong 6,36 điểm nằm trên 9 bản ghi mà tín
> hiệu thai không đo được trên bất kỳ kênh nào trong bốn kênh — cùng một hiện tượng với nhóm
> "giới hạn cứng", chỉ nhẹ hơn. Ranh giới 8 bản / 67 bản là một **ngưỡng cắt tùy ý trên một dải
> liên tục**, không phải hai loại khác nhau. Phần thực sự còn lại cho mô hình là **1,85 điểm**
> trên CinC 75, rải trên 58 bản ghi.

### 3.3 Ba bản ghi khó của 22 chủ thể, sau M5

`m1_bo_sung.pho_loi_theo_quy_tac['22_kho3|*']`, F1 macro trên đúng ba bản ghi:

| quy tắc | F1 macro 3 bản khó | số lỗi | lỗi/1000 nhịp |
|---|---:|---:|---:|
| psd | 85,25 | 1 733 | 257,9 |
| **gate** *(khai báo trước)* | **92,95** | 547 | 81,4 |
| peakprob *(hậu kiểm)* | 90,05 | 1 088 | 161,9 |
| oracle | 92,95 | 547 | 81,4 |

**Đáng chú ý và phải báo cáo:** trên ba bản ghi khó, quy tắc **khai báo trước `gate` đạt đúng bằng
oracle** (92,95; chọn trúng kênh tốt nhất cả 3/3 bản), còn `peakprob` chỉ đạt 90,05. Trên cả 22
chủ thể cũng vậy: gate 98,61 so với peakprob 98,22, oracle 98,63. Đây là **bằng chứng ngược** với
việc chọn `peakprob`, và nó nằm đúng trên miền mà quy tắc quyết định khai báo trước đã chỉ định.
Củng cố cảnh báo liêm chính đã mang theo: **ưu thế của `peakprob` chỉ tồn tại trên CinC (tập
hậu kiểm) và chưa được xác nhận ngoài miền.** Phải báo cáo cả hai.

Kết luận từng bản (chi tiết kênh ở `chandoan_results.json → ban_ghi_kho`, hình
`fig_chandoan_kho.png`):

| bản ghi | tín hiệu thai có trên một kênh nào đó? | bản chất | ai sửa được |
|---|---|---|---|
| B1_06 | **Có, rất rõ** (A3 = 99,64; 99,6% nhãn nhìn thấy) | chọn nhầm kênh thuần túy | quy tắc chọn kênh — **gate đã sửa** |
| B1_07 | **Có** (A3 = 95,31); A4 cũng đủ (98,05 trong mẫu) | chọn kênh + không tổng quát hóa | chọn kênh + thích nghi chủ thể |
| B2_03 | **Không trên một kênh đơn** (tốt nhất 83,91; chỉ 54,7–63,5% nhãn nhìn thấy) | SNR thấp, thông tin rải trên các kênh | **hợp nhất đa kênh** |

B2_03 là bản ghi **duy nhất** trong ba bản là giới hạn thật. Nhưng **thông tin có nằm rải trong
bốn kênh**: trần hợp nhất 98,01 so với kênh tốt nhất 83,91. Đúng như dự đoán từ việc Power‑MF
4 kênh đạt 89,49 ở đây trong khi ta chỉ đạt 79,72: **phải nhiều kênh mới thấy**. Power‑MF dùng ICA
hai lần để **tách nguồn**, ta chỉ **chọn** một kênh — và đó chính là khác biệt quyết định trên
bản ghi này. Phép gộp bỏ phiếu ngây thơ (hợp nhất **đỉnh**) chỉ nhặt được 84,87; khoảng
98,01 − 84,87 = **13,1 điểm** là dư địa cho một phép hợp nhất ở mức **xác suất** thay vì mức đỉnh.
Đây là đề xuất tiền xử lý duy nhất trong tài liệu này có số đo hậu thuẫn — **chỉ phân tích, chưa
cài đặt**.

### 3.4 Tám bản ghi CinC giới hạn cứng: có tiêu chí từ chối mù nhãn không?

`m1_bo_sung.gioi_han_cung_8`.

**Cảnh báo vòng lặp, phải đọc trước.** Nhóm "8 bản giới hạn cứng" được **định nghĩa** là
F1_oracle < 50. Đã kiểm: số bản ghi ngoài nhóm 8 có F1_oracle < 50 là **0**. Vậy nhóm 8 ≡ tập
{F1_oracle < 50} **theo đúng định nghĩa**. Mọi đặc trưng **dùng nhãn** tất nhiên tách được nhóm này
(ví dụ % nhãn nhìn thấy cho AUROC 0,998) — con số đó **không phải phát hiện**. Chỉ đặc trưng
**mù nhãn** mới có giá trị.

**Hai trong tám bản không phải giới hạn thật:**

| bản ghi | n_ref | số nhịp mô hình phát hiện | ghi chú |
|---|---:|---:|---|
| a54 | **37** | tới 144 | nằm trong danh sách **chú thích sai đã khai báo trước** |
| a71 | 153 | tới 142 | nằm trong danh sách **chú thích sai đã khai báo trước** |

a54 chỉ có 37 nhịp được chú thích trong khi mô hình phát hiện 144 nhịp — đây là **lỗi nhãn**, không
phải "không có tín hiệu". Vậy nhóm giới hạn cứng thực chất còn **6 bản**: a27, a43, a57, a59, a60,
a68.

**Đặc điểm chung, đặc trưng MÙ NHÃN** (AUROC tách 8 bản khỏi 67 bản còn lại):

| đặc trưng (mù nhãn) | AUROC | hướng |
|---|---:|---|
| điểm cổng từ chối **GATE22**, hiệu chuẩn trên 22 chủ thể, **zero‑shot** sang CinC | **0,854** | điểm thấp = bản ghi xấu |
| tỉ lệ đoạn bị cổng đánh xấu | 0,818 | cao = xấu |
| **điểm PSD lớn nhất trong 4 kênh** | 0,799 | **PSD CAO = xấu** (ngược trực giác) |
| số phát hiện lớn nhất | 0,359 | — |

Quét ngưỡng trên điểm cổng GATE22:

| ngưỡng | bắt được trong 8 bản cứng | báo động nhầm trong 67 bản |
|---|---:|---:|
| < 0,05 | 4/8 | 5/67 |
| < 0,10 | **6/8** | 10/67 |
| < 0,20 | 6/8 | 12/67 |
| < 0,30 | 6/8 | 14/67 |

**Đọc kết quả này:**

* **Có** một tiêu chí từ chối mù nhãn dùng được, và nó là **cổng GATE22 đã có sẵn** — không cần
  xây thêm gì. Nó chưa bao giờ thấy CinC, nên 0,854 là một con số **zero‑shot thật**.
* Nó **không hoàn hảo**: hai bản (a54, a57) có điểm cổng **cao** (0,97 và 0,79) mà vẫn hỏng — và
  a54 chính là bản chú thích sai, nên cổng có lẽ **đúng** còn nhãn mới sai.
* **Phát hiện phụ đáng chú ý:** điểm PSD lớn nhất **cao** lại đi với bản ghi **xấu** (AUROC 0,799
  theo chiều "PSD cao = xấu"; trung vị 37,4 ở nhóm cứng so với 11,6 ở nhóm còn lại). Đây là bằng
  chứng thêm cho thất bại đã biết của quy tắc PSD trên B1_06 (chọn đúng kênh tệ nhất vì kênh đó
  có điểm PSD cao gấp ba): **công suất trong dải 1,8–3,0 Hz của đường bao không phải bằng chứng
  có nhịp thai dò được**, và ở bản ghi xấu nó bắt phải thứ khác. Quy tắc PSD nên bị loại bỏ.
* Giá trị lâm sàng: một cổng như vậy dùng được ở **mức thu nhận tín hiệu** — báo cho kỹ thuật viên
  đặt lại điện cực trước khi ghi tiếp, thay vì trả ra một chuỗi FHR sai. Nhưng với 8 điểm dữ liệu
  dương, **mọi con số trong mục này đều là ước lượng rất thô** (xem hạn chế 4).

---

## 4. Vậy nên đầu tư vào đâu?

Xếp theo điểm F1 đổi được trên mỗi đơn vị công sức, dựa trên các số đo ở trên:

1. **Hợp nhất đa kênh ở mức XÁC SUẤT (không phải mức đỉnh).** Đây là hướng duy nhất còn dư địa đo
   được và chưa thử: trần hợp nhất **93,11** trên CinC 75 và **98,01** riêng trên B2_03, trong khi
   hợp nhất bỏ phiếu vị trí chỉ đạt 81,56 và 84,87. Trên 22 chủ thể, vote≥2 đã lấy lại 85% dư địa
   chọn kênh **mà không cần nhãn**. Đây cũng là cách duy nhất chạm được vào 4,52 điểm "không nhìn
   thấy trên một kênh đơn", vì Power‑MF chứng minh rằng **tách nguồn đa kênh** thấy được thứ mà
   chọn một kênh không thấy.
2. **Chốt quy tắc chọn kênh, và loại bỏ PSD.** Còn 1,27 điểm trên CinC. Nhưng phải giải quyết mâu
   thuẫn `gate` (khai báo trước, thắng trên 22 chủ thể và trên 3 bản khó) với `peakprob` (hậu kiểm,
   thắng trên CinC) **trên một tập thứ ba**, không phải bằng cách chọn cái có số đẹp hơn.
3. **Cổng từ chối ở mức thu nhận tín hiệu** (GATE22 đã có, AUROC zero‑shot 0,854). Không tăng F1
   nhưng tăng **độ tin cậy lâm sàng**, và đây là phần có giá trị lâm sàng cao nhất của vòng này.
4. **Thích nghi chủ thể / thêm dữ liệu chủ thể mới.** Khoảng cách trong‑mẫu vs ngoài‑mẫu trên ba
   bản ghi khó là +8,56 / +11,49 / +13,71 điểm — số đo trực tiếp của cái mà "biết trước chủ thể"
   đáng giá. Ablation bỏ B1 đã cho thấy "thêm dữ liệu" đúng (+5,06 trên CinC).
5. **KHÔNG đầu tư vào kiến trúc.** Không có bằng chứng nào ở trên ủng hộ. Câu hỏi mở "TCN hay
   `cnn_l`" nên được **đóng lại là không liên quan**, không phải được trả lời.
6. **KHÔNG đầu tư vào hồi quy độ lệch / siết `heatmap_sigma`** — mục 1.3, đã rút lại.

**Trần thực tế cần nói trong bài báo:** với **một** kênh, trần của CinC 2013 set‑a là
100 − 6,77 (giới hạn cứng) − ~4,52 (không nhìn thấy trên kênh đơn) ≈ **89**, không phải 93 và
không phải 100. Với hợp nhất bốn kênh, trần hợp nhất đo được là **93,11**.

---

## 5. Hạn chế (bắt buộc đọc)

1. **Phép thử "nhìn thấy" là một thay thế thô cho "có tín hiệu thai".** Nó đo biên độ đỉnh của
   phần dư 10–60 Hz so với nhiễu cục bộ; nó **không** phân biệt được đỉnh thai với một gai nhiễu
   trùng vị trí nhãn. Độ nhạy đo được chỉ 0,86–0,89 trên CinC ⇒ ~12% nhịp thai thật bị chính phép
   thử gọi là "không nhìn thấy" ⇒ **nhóm (b) bị thổi lên, nhóm (a) bị nén xuống**. Toàn bộ kết
   luận "mô hình không phải nút thắt" dựa một phần vào phép thử này; nếu nó thiên lệch mạnh hơn
   ước tính thì kết luận yếu đi. Công thức hiệu chỉnh `quan sát = p·nhạy + (1−p)·0,05` giả định
   độ nhạy như nhau trên mọi nhịp — **giả định này gần như chắc chắn sai**, vì nhịp yếu vừa khó
   nhìn thấy vừa khó dò (hai sai số cùng chiều, nên (a) thật có thể cao hơn báo cáo).
2. **Ngưỡng nhìn thấy 0,50 ở mục 3.2 là do tôi chọn, không tiền đăng ký.** Con số "71% / 4,52
   điểm" phụ thuộc vào ngưỡng đó. Bậc thang 1,00 / 0,51 / 0,19 thì không phụ thuộc ngưỡng và là
   bằng chứng chắc hơn; nhưng việc chia đôi 6,36 điểm thành 4,52 + 1,85 **là một lựa chọn hậu
   kiểm** và phải được đọc như ước lượng định hướng.
3. **Nhóm (e) đã bị rút với tư cách chẩn đoán, nhưng điều đó không chứng minh điều ngược lại.**
   Việc (e) không vượt mức ngẫu nhiên nghĩa là **không có bằng chứng** cho lỗi định vị, chứ không
   phải bằng chứng rằng định vị hoàn hảo. Bằng chứng tích cực duy nhất là jitter TP nhỏ (3,76 ms),
   và nó chỉ đo trên **các nhịp đã bắt đúng** — theo định nghĩa, đó là những nhịp dễ nhất.
4. **Mục 3.4 có n = 8 (thực chất n = 6 sau khi loại hai bản chú thích sai).** Mọi AUROC ở đó dựa
   trên 8 điểm dữ liệu dương; khoảng tin cậy sẽ rất rộng và **tôi chưa tính**. Bảng quét ngưỡng
   cũng chưa qua kiểm định chéo. Không được trích dẫn 0,854 như một hiệu năng cổng.
5. **Phép thử năng lực B chỉ có 4 chủ thể, 8 epoch, một hạt giống, và chỉ hai bề rộng.** Nó là
   chặn trên (ngưỡng chọn trong mẫu) và không thay thế được quét năng lực đầy đủ; đặc biệt nó
   **không** thử thay đổi trường tiếp nhận, chiều sâu, hay họ kiến trúc — chỉ thử bề rộng. Phát
   biểu "không thiếu năng lực" vì vậy đúng cho **bề rộng**, và chỉ suy rộng ra các chiều khác một
   cách gián tiếp qua phép thử A.
6. **Phép thử A dùng MỘT checkpoint production duy nhất**, không lặp hạt giống. Độ ổn định seed đã
   chốt của nhóm (lệch tuyệt đối trung bình 0,28 điểm trên 20 chủ thể) là ở chế độ LOSO, không
   phải chế độ trong mẫu.
7. **Nhãn B1 là nhãn gián tiếp**, và hai trong ba bản ghi khó (B1_06, B1_07) thuộc nhóm B1. Theo
   ghi chú đã chốt (`analysis/ABLATION_B1.md`), **không được dùng số của B1 để nói về jitter/STV**.
   Bảng jitter ở mục 1.3 vì vậy **chỉ lấy trên CinC**, không lấy trên B1 — đây là thay đổi có chủ
   ý so với bản trước, vốn đã chạm ranh giới đó ở mục quét dung sai.
8. **Không có kiểm định thống kê nào trong tài liệu này.** Mọi con số là mô tả trên các quần thể
   lỗi hữu hạn; không khoảng tin cậy, không kiểm định giả thuyết. Riêng khoảng cách trong‑mẫu /
   ngoài‑mẫu trên ba bản ghi khó là **n = 3**.
9. **Toàn bộ phần bổ sung M1 dùng lại bộ nhớ đệm của vòng trước**, không chạy suy luận độc lập.
   Nếu `chandoan_raw.json` có lỗi hệ thống thì mọi số ở đây kế thừa lỗi đó. Giảm nhẹ: F1 tính lại
   từ bộ nhớ đệm này khớp `chonkenh_results.json` tới 0,0000 điểm trên cả 5 quy tắc × 2 miền, và
   phân rã ngân sách tái lập đúng con số 6,86 / 0,61 / 6,36 / 6,77 mà chủ nhiệm tính độc lập.

---

## 6. Tệp đã tạo

| tệp | nội dung |
|---|---|
| `analysis/CHANDOAN_MOHINH.md` | tài liệu này |
| `analysis/chandoan_results.json` | tổng hợp (khóa `m1_bo_sung` là phần của vòng này) |
| `analysis/fig_chandoan.png` | hình chính vòng trước (4 khung) |
| `analysis/fig_chandoan_kho.png` | hình ba bản ghi khó |
| **`analysis/fig_chandoan_m1.png`** | **hình vòng này: phổ lỗi theo quy tắc, ngân sách, nhóm giới hạn cứng** |
| **`analysis/chandoan_m1.py`** | **phổ lỗi theo quy tắc + ngân sách + nhóm cứng (không suy luận mới)** |
| **`analysis/chandoan_m1_results.json`** | **kết quả vòng này** |
| **`analysis/chandoan_m1_jitter.py` / `.json`** | **độ chính xác định vị trên nhịp đã bắt đúng** |
| `analysis/chandoan.py`, `chandoan_raw.json` | suy luận + phân loại lỗi từng bản ghi × kênh |
| `analysis/chandoan_events.npz`, `chandoan_cache.npz` | sự kiện từng nhịp; tín hiệu ba bản khó |
| `analysis/chandoan_recls.py`, `chandoan_strict.json` | nhóm (e) chặt + mức ngẫu nhiên |
| `analysis/chandoan_tol.py`, `chandoan_tol.json` | quét dung sai 50/75/100/150 ms |
| `analysis/chandoan_capacity.py`, `chandoan_capacity.json` | trần năng lực (A và B) |
| `analysis/chandoan_hard.py`, `chandoan_hard.json` | chẩn đoán ba bản ghi khó |
| `analysis/chandoan_m1_log.txt`, `chandoan_m1_jitter_log.txt` | nhật ký vòng này |
