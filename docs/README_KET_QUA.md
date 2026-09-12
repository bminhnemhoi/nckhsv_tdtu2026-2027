> **Báo cáo vòng cũ — giữ để truy vết, KHÔNG phải trạng thái hiện hành.** Nhiều con số trong tệp này đã rút
> (mẫu 10 bản CinC; 75 bản CinC nhiễm 15 bản sao ADFECGDB; Power-MF cổng chuyển hỏng; +11,00 dải lọc; "8 kiến
> trúc"; "mô hình không phải nút thắt"; "Physiological Measurement là Q1"). Số hiện hành: `README.md` mục
> *Retractions* và `survey/facts_phase4.json`.

# Đề tài fECG đơn kênh — RelyFetal

Cập nhật 12/09/2026 (chiều), phiên bản **3.4**.

## Tài liệu gửi giảng viên hướng dẫn

| Tệp | Nội dung |
|---|---|
| **`De_cuong_NCKH_RelyFetal.pdf`** | **Đề cương chính thức v3.4** (138 trang) |
| `De_cuong_NCKH_RelyFetal.docx` | Bản Word để GVHD sửa trực tiếp |
| **`Bao_cao_30_paper.pdf`** | Báo cáo đọc 30 công trình |
| `Bao_cao_30_paper.docx` | Bản Word của báo cáo 30 công trình |
| `../paper/cinc2026/main.pdf` | Bản thảo Computing in Cardiology — **CẦN SỬA LẠI**, xem bên dưới |

---

## v3.4 — đề cương đã mang số Power-MF đúng

Bản 3.3 của đề cương (sáng 12/09) dùng số Power-MF từ một bản Octave còn hỏng. **Bản 3.4 (chiều 12/09)
đã viết lại toàn bộ mục 5.7** bằng số sau bản vá P7, thêm cột **Power-MF đơn kênh**, và thêm một mục mới
**§8.3 "Nhóm đã đoán sai nguyên nhân hai lần trong một ngày"**. Chi tiết:

- Mục 5.7 mở đầu bằng một **hộp rút lại** ghi rõ 94,87 / 98,38 / 97,33 đều sai và vì sao.
- Bảng 3 cột đầy đủ 22 chủ thể (PMF 4 kênh / PMF 1 kênh / RelyFetal) + bảng F1 từng chủ thể.
- Bảng thống kê mức chủ thể đầy đủ: 3 phép so sánh × 4 tập con = 12 dòng.
- Hộp **kiểm chứng ngoài**: 99,40 chạy lại so với 99,46 tác giả công bố, lệch 0,06 điểm.
- Mục **ba bản ghi kéo tụt trung bình** (B1_07 / B1_06 / B2_03), kèm trung vị +0,23 và thắng 18/22.
- Mục **luận đề 89,5 %** — cách định vị đúng của cả đề tài.
- Hình 17 đổi từ 2 cột sang **3 cột**.

Toàn bộ 82 con số Power-MF trong PDF đã được đối chiếu tự động với `baselines/powermf_fair_stats.json`
bằng `de_cuong_latex/verify_v34.py` — **82/82 khớp**.

## v3.3 rút lại bốn phát biểu của v3.2

Đây là điểm quan trọng nhất của bản này. Bốn kết luận trong v3.2 **không đúng** và đã được sửa kèm con số
đúng, mã nguồn và nhật ký.

### 1. Con số CinC 2013 đo trên mẫu 10 bản ghi của một tập có 75 bản ghi

Đã chạy **toàn bộ 75 bản ghi** set-a (`benchmark_dpss/eval_cinc75.py` → `eval_cinc75.json`).
Mẫu 10 bản ghi **bị lệch, và lệch theo hai hướng ngược nhau**:

| Quy tắc chọn kênh | Mẫu 10 bản ghi (v3.2, **đã rút**) | Toàn bộ 75 bản ghi (ô nhiễm, **đã rút**) | Lệch | **60 bản sạch — số hiện hành** |
|---|---:|---:|---:|---:|
| PSD mù nhãn (**số chính**) | 69,31 | 79,40 | −10,09 | **74,28** (KTC 95% [66,63; 81,78]) |
| Kênh 0 cố định (hậu kiểm) | 90,34 | 69,33 | **+21,01** | — (quy tắc đã rút) |

**Cập nhật vòng 7 (12/09/2026).** Cả cột 10 bản ghi lẫn cột 75 bản ghi đều **đã bị rút**: 15/75 bản ghi
set-a (a03, a04, a05, a08, a12, a13, a14, a15, a17, a19, a20, a22, a23, a24, a25) là bản sao nguyên văn
(NCC = 1,0000 trên cả 4 kênh, sai lệch RR bằng 0,0 ms) của r01, r04, r07, r08, r10 — chính 5 bản ADFECGDB
dùng để huấn luyện; 60 bản còn lại chỉ đạt NCC tối đa 0,62, và việc giữ 15 bản trùng làm trung bình 75 bản
thổi phồng 3,27–7,18 điểm F1. Số hiện hành đo trên **60 bản sạch**: PSD mù nhãn (quy tắc khai báo trước,
**số chính**) **74,28**; quy tắc hậu kiểm `peakprob` 82,01 (chỉ là giả thuyết); trần dùng nhãn 83,60.
Việc set-a chứa bản ghi ADFECGDB đã được chính ban tổ chức ghi nhận (Silva 2013, CinC 40:149–152, Bảng 1;
Clifford 2014, Physiol Meas 35:1521) — nhóm chỉ định danh được đúng 15 bản nào và đo mức thổi phồng.

Con số **90,34** của v3.2 là siêu tham số đã được **khớp vào chính 10 bản ghi đánh giá** (kênh 0 được chọn
sau khi thấy quy tắc PSD thất bại trên đúng 10 bản ghi đó). Khi đem ra 65 bản ghi chưa thấy nó **rơi 21
điểm**, xuống thấp hơn cả quy tắc mù nhãn mà nó từng thay thế. **90,34 đã bị rút khỏi mọi bảng chính.**

Hệ quả nặng nhất: kết luận v3.2 **"không còn bản ghi nào dưới 50"** là **SAI** trên tập đầy đủ.
Trên 60 bản sạch vẫn còn **16 bản ghi dưới 50** với mô hình 22 ca (22 với mô hình 5 ca), trong khi 33/60
bản đạt F1 từ 90 trở lên và trung vị là 95,07. Sụp đổ xuyên hệ ghi **chưa được chữa** — đây là điểm yếu
số một của đề tài.

Thêm dữ liệu vẫn giúp, và lần này đủ mẫu để nói chắc: đo lại trên **60 bản sạch**, mô hình 22 chủ thể đạt
74,28 so với 64,04 của mô hình 5 ca, hiệu **+10,24 điểm**, KTC 95% [+7,13; +13,60], Wilcoxon p = 3,5e−10.
(Con số **+8,18 điểm** [+5,62; +11,09] trên 75 bản ghi ô nhiễm **đã bị rút**.)

### 2. "Power-MF không chạy lại được" — sai, đã chạy; và bảng so sánh đầu tiên cũng sai

Power-MF chạy được trên **GNU Octave 11.3.0** (không cần MATLAB) sau bảy bản vá.

> **RÚT LẠI (trong cùng ngày 12/09/2026).** Bảng so sánh Power-MF công bố **sáng 12/09** —
> *"Tất cả 18 bản ghi: 94,87 so với 97,61, hiệu +2,74"* và *"loại 2 bản nghi lỗi: 98,38 so với 97,33,
> hiệu −1,06 [−3,04; +0,40]"* — **bị rút toàn bộ**. Cả hai dựa trên một **bản Power-MF còn hỏng**.
>
> Nguyên nhân thật (chẩn đoán và vá trong `baselines/BASELINES.md`): hàm `findpeaks` của gói `signal`
> trong Octave cài `MinPeakDistance` bằng **ma trận khoảng cách đôi một O(k²)** → tràn bộ nhớ trên 6 bản
> ghi B1 dài (2.395.600 mẫu sau nội suy ×4). MATLAB — nền tảng của tác giả — dùng thuật toán **tham
> O(k log k)** nên không bao giờ gặp. **Đây là lỗi cổng chuyển của nhóm, không phải tính chất của
> Power-MF.**
>
> Giả thuyết cũ *"`ms_minpeakdistance` = 340 ms quá sát"* **cũng bị bác bỏ** bằng đo RR thật:
> **0,00 %** khoảng RR của B1_01 nằm dưới 340 ms (`baselines/powermf_rr_diag.json`). Tham số được giữ
> nguyên ở mặc định 340 ms của tác giả trong mọi lần chạy.
>
> Bản vá P7 (`baselines/octave/findpeaks_mpd.m`) tái lập đúng ngữ nghĩa MATLAB bằng danh sách liên kết
> đôi, O(k); kiểm chứng 48/48 trường hợp. Cách "loại 2 bản ghi nghi lỗi" của bản cũ nay **không cần
> thiết nữa**: sau khi vá, cả 10 bản ghi B1 đều chạy đúng.

**Kiểm chứng ngoài — đây là căn cứ quyết định.** Sau khi vá, Power-MF đạt **99,40 ± 0,51** trên Silesia
B1. Số **đã công bố của chính tác giả** trên tập đó là **99,46** (`baselines/powermf_published.json`,
trích từ `Results/*.mat` của repo gốc). Lệch **0,06 điểm** → cổng chuyển giờ đã đúng.

Chấm bằng **chính bộ chấm của nhóm** (`match_events`, ±50 ms, ghép tham lam 1-1) trên **đủ 22 chủ thể**,
và lần này có thêm cột **Power-MF đơn kênh** để so sánh đúng cùng cấu hình đạo trình:

| Tập | n | Power-MF **4 kênh** | Power-MF **1 kênh** | **RelyFetal 1 kênh** |
|---|---:|---:|---:|---:|
| ADFECGDB | 5 | 99,01 | 92,37 | **99,40** |
| Silesia B2 | 7 | 97,90 | 87,28 | 96,82 |
| Silesia B1 | 10 | **99,40** | 83,48 | 97,15 |
| **Tất cả 22** | 22 | **98,83** | 86,71 | 97,56 |
| CinC 2013, 60 bản sạch | 60 | chưa chạy | 55,97 | **74,28** |

Thống kê mức chủ thể (bootstrap cụm 10.000 lần lấy mẫu lại **chủ thể**, seed 0; Wilcoxon ghép cặp;
Cliff δ), tất cả 22 chủ thể:

| So sánh | Hiệu | KTC 95% | p | Cliff δ | thắng/hòa/thua |
|---|---:|---|---:|---:|---|
| RelyFetal − Power-MF 4 kênh | −1,27 | [−3,08; +0,27] | 0,156 | 0,260 | 18/0/4 |
| RelyFetal − Power-MF 1 kênh | **+10,85** | [+6,80; +15,40] | 4,77e−07 | 0,698 | **22/0/0** |
| Power-MF 1 kênh − Power-MF 4 kênh | −12,12 | [−18,27; −6,90] | 1,43e−06 | — | 1/0/21 |

Theo từng tập, RelyFetal − Power-MF 4 kênh: ADFECGDB **+0,39** [+0,22; +0,60] p=0,0625, 5/0/0 (KTC
**không chứa 0** → ta hơn); Silesia B2 −1,08 [−4,04; +0,54] p=0,297, 6/0/1; Silesia B1 −2,25
[−5,55; +0,32] p=1, 7/0/3.

**Trung bình che mất hình dạng kết quả — phải nêu rõ.** **Trung vị** hiệu số trên 22 chủ thể là **+0,23**
và ta thắng **18/22**. Trung bình bị kéo âm **chỉ** bởi ba bản ghi:

| Bản ghi | RelyFetal | Power-MF 4 kênh | Hiệu |
|---|---:|---:|---:|
| B1_07 | 86,56 | 99,44 | −12,88 |
| B1_06 | 89,45 | 99,97 | −10,51 |
| B2_03 | 79,72 | 89,49 | −9,77 |
| *(bản thứ tư, nhẹ)* B1_10 | 97,05 | 98,91 | −1,86 |

**Luận đề đúng của bài — dùng cách phát biểu này thay cho mọi cách cũ.** Câu hỏi không phải "ai thắng",
mà là: *một mạng **đơn kênh** 113.481 tham số lấy lại được bao nhiêu phần lợi ích mà **tách nguồn đa
kênh** mang lại?* Lợi ích đó nay đo được vì Power-MF đã chạy ở cả hai cấu hình: bỏ tách nguồn đa kênh
khiến **chính Power-MF mất 12,12 điểm F1** (86,71 so với 98,83). Mô hình đơn kênh lấy lại **10,85 điểm,
tức 89,5 % số đó, bằng một kênh**. Kết quả: **không phân biệt được** với Power-MF **đa kênh**
(−1,27; KTC [−3,08; +0,27]; p = 0,156), và **hơn hẳn** Power-MF khi Power-MF bị giới hạn về **cùng một
đạo trình** (+10,85; 22/22).

**TUYỆT ĐỐI KHÔNG** viết "ta thắng SOTA". Power-MF 4 kênh vẫn hơn về trung bình thô.

### 3. Mọi trị số p trên 5 sản phụ là giả lập

Đơn vị phân tích cũ là **cặp (bản ghi × kênh)**, tức 4 kênh của cùng một phụ nữ bị coi là 4 quan sát độc
lập. Tính lại ở **mức chủ thể** (`analysis/stats.py` → `STATS.md`):

> Với n = 5 chủ thể, Wilcoxon hai phía có **p nhỏ nhất có thể đạt = 2/2⁵ = 0,0625**.
> Không một so sánh nào trên ADFECGDB có thể đạt p < 0,05, bất kể hiệu số lớn đến đâu.

Mọi p trên ADFECGDB (1,9e−6; 5,7e−6; 0,0000) **đã bị gỡ**. Hai kết luận đảo chiều:

- **Silesia B2** "cải thiện có ý nghĩa, p = 0,016" → ở mức chủ thể p = 0,47, Cliff δ = 0,10. **Rút.**
- **"8 kiến trúc không phân biệt được"** → TOST biên 1,0 điểm cho **0/7 tương đương**, 6/7 không kết luận
  được, và `cnn_m` **KÉM HƠN** vượt biên (KTC 90% [−4,55; −1,47]). Phát biểu mới:
  *"với n = 5 chủ thể, nghiên cứu này không đủ lực để phân biệt các kiến trúc trong biên 1,0 điểm F1;
  hiệu số quan sát nằm trong −2,95 đến +0,73 điểm"*.

Thêm: KTC 95% kiểu t của 99,21 **vượt 100%** — đã thay bằng bootstrap cụm [97,87; 99,95].
Và AUROC cổng từ chối 0,929 phần lớn là hiệu ứng **giữa** bản ghi; AUROC **trong** bản ghi — đại lượng
thật sự cần cho lâm sàng — chỉ là **0,721** [0,517; 0,898].

### 4. Chỉ số lâm sàng: hệ thống CHƯA dùng được làm máy đo STV

32 bản ghi, 269,6 phút tín hiệu thật (`analysis/clinical.py` → `CLINICAL.md`).

**Nhịp tim thai — dùng được.** Độ chệch −0,24 bpm, 95,38% cửa sổ trong ±5 bpm trên 260 cửa sổ; trên
ADFECGDB đạt 98,66% ngay ở cửa sổ 5 giây (so với "FHR precision 88,61%" của DPSS — so sánh bảo vệ được vì
không thắng nhờ chọn cửa sổ dài).

**STV — KHÔNG dùng được.** Bốn lý do:
1. LoA của phần máy thật sự trả lời là [−0,62; +1,16] ms, bề rộng **1,78 ms**, trong khi phân biệt 2,6 với
   3,0 ms cần độ phân giải **0,4 ms** — thiếu **4,5 lần** (nhóm "cao": 1,00 ms, vẫn thiếu 2,5 lần).
2. Sai số **một chiều**: 25/32 bản ghi máy đọc STV **cao hơn** sự thật — chiều **trấn an giả**.
3. 3/3 bản ghi có STV nhãn thấp nhất bị **bỏ sót hoàn toàn** (0 TP, 3 FN).
4. 22/32 bản ghi ngắn hơn tối thiểu 10 phút của Dawes-Redman.

Và chọn kênh **không** sửa được: a09 ở kênh 0 với F1 = 94,25 vẫn cho STV 6,37 ms so với nhãn 0,49 ms.

**Độ phủ theo thời lượng** (không phải theo bản ghi — 43,8% của v3.2 là *tỉ lệ bản ghi xanh*, gọi sai):
ADFECGDB 96,0% (tốt hơn CTG Doppler), Silesia 88,2–88,8% (chưa đạt), CinC 58,7% (hỏng).
**Quan trọng hơn tổng phần trăm: khoảng trống liên tục dài nhất là 192 giây** — đủ để giấu trọn một cơn
nhịp giảm kéo dài.

**Khoá nhầm nhịp mẹ:** chỉ 2/32 bản ghi, cả hai ở CinC. Nhưng a09 khoá mẹ 53,4% mà luật ngưỡng cứng 60%
**không kích hoạt** — được cứu nhờ p_bad, tức nhờ may. Khuyến nghị: thay bằng "vượt p95 phân phối rỗng của
chính bản ghi hơn 10 điểm" (bắt đúng cả a02 lẫn a09, không thêm dương tính giả nào).

---

## Ba đóng góp, phát biểu lại cho đúng phạm vi

Rà soát y văn vòng ba (`survey/scout_novelty.md`) tìm ra **năm công trình** mà v3.2 không trích dẫn, và
bốn trong số đó **chiếm mất** một phần tuyên bố "đầu tiên":

| Công trình | Chiếm mất tuyên bố nào |
|---|---|
| Andreotti 2016, `10.1088/0967-3334/37/5/627` | "front-end quan trọng hơn kiến trúc" (định tính, 2016) |
| Andreotti 2017, `10.1109/TBME.2017.2675543` | cổng từ chối / fSQI cho fECG |
| Fotiadou 2021, `10.1088/1361-6579/abf7db` | quét lịch giãn nở / trường tiếp nhận trong fECG |
| Zahid 2022, `10.1109/TBME.2021.3088218` | đầu ra heat-map theo từng mẫu cho dò đỉnh R |
| TCGAN 2025, `10.1109/JBHI.2024.3524085` | đối thủ trực tiếp, đơn kênh, đúng tạp chí mục tiêu |
| Baldazzi & Pani 2023, `10.1007/978-3-031-32625-7_12` | trùng lặp ADFECGDB ↔ Silesia đã in trong sách |

Dải 10–60 Hz — biến mang +11,00 điểm — là dải nhóm **lấy từ Xu 2026**, ghi rõ trong `facts_verified.json`.
Nhóm không phát hiện dải tối ưu; nhóm **đo** dải mà người khác đã chọn.

**Đề tài định vị lại là TIẾP NỐI Andreotti 2016/2017 và Behar 2014, không phản bác.** Một trục duy nhất:
**phân rã có kiểm soát + đối chuẩn công bằng + kết quả phủ định công bố nguyên trạng**.

- **C1** — đối chuẩn công bằng ở cấu hình đơn kênh, nay có **một baseline hiện đại chạy lại thật**.
  Không phải "đối chuẩn đầu tiên".
- **C2** — phân rã ba tầng (front-end / ngữ cảnh / kiến trúc) trong **một** thí nghiệm duy nhất trên dữ
  liệu thật. **Đóng góp duy nhất nhóm còn dám gọi là mới.**
- **C3** — đánh giá cổng từ chối **xuyên hệ ghi, zero-shot**, kèm kết quả phủ định có kiểm soát về đồng
  điều bền vững (AUROC 0,566). Cơ chế không mới; cách đánh giá mới.

**Đã gỡ:** "phản bác cả một dòng công trình", "front-end quan trọng hơn kiến trúc 27 lần".

---

## Độ ổn định theo seed (mới)

Huấn luyện lại toàn bộ mô hình 22 chủ thể ở seed 1. Trên 20 chủ thể chung: |hiệu số| F1 trung bình
**0,28 điểm**, lớn nhất 2,81 (B2_03) — nhỏ hơn nhiều so với mọi hiệu ứng được báo cáo.

Nhưng: **ngưỡng từng fold không ổn định**. Seed 0 cho dải 0,20–0,80 (fold 10 ở 0,20, cực đoan); seed 1
cho 0,50–0,80 và **không tái lập** giá trị 0,20. Quy trình chọn ngưỡng trên một chủ thể validation duy
nhất là điểm mong manh của pipeline.

---

## Việc phải làm, theo thứ tự

1. ~~**Sửa bản thảo CinC 2026**~~ — **đã xong (vòng 7)**: `paper/cinc2026/main.tex` nay báo cáo **74,28**
   (KTC 95% [66,63; 81,78], PSD mù nhãn, quy tắc khai báo trước) trên **60 bản ghi CinC 2013 set-a sạch**
   sau khi loại 15 bản trùng nguyên văn với ADFECGDB; các con số trên mẫu 10 bản ghi, trên 75 bản ghi ô
   nhiễm và các trị số p giả lập đều đã bị gỡ.
2. **Thay luật khoá nhịp mẹ** ngưỡng cứng 60% bằng mức vượt phân phối rỗng — rẻ, và bắt được a09 theo
   thiết kế chứ không nhờ may.
3. ~~**Chạy lại khảo sát dải thông**~~ — **đã chạy trên chính TCN (vòng 7)**: dải 10–60 Hz chỉ được
   **+2,44 điểm** [−0,05; +6,30] ở kênh PSD và **−0,07 điểm** [−0,49; +0,40] khi trung bình 4 kênh; con số
   **+11,00** là của bộ phân loại GBM cửa sổ 300 ms và **đã bị rút** khi nói về TCN.
4. **Truy nguyên lỗi cổng chuyển Power-MF trên bản ghi dài** (B1_01/02 bắt cách nhịp, B1_03–06 rỗng).
5. **P7 — tiền huấn luyện FECGSYNDB**: sau khi thấy 16/75 bản ghi CinC vẫn dưới 50, mục này **trở lại
   thành ưu tiên** chứ không còn "có thể không cần thiết" như v3.2 viết.
6. **Hiệu chuẩn lại cổng theo tiêu chí STV** nếu muốn xuất STV — cổng theo F1 để lọt r10 (+1,34 ms) và
   B1_10 (+1,61 ms).
7. **Kiểm chứng ngưỡng TRUFFLE 2,6/3,0 ms và các mốc mất tín hiệu CTG từ bản gốc** — hiện là lời truyền
   đạt, chưa có nguồn.
8. **Dữ liệu đa trung tâm** — khoảng trống duy nhất còn lại về tổng quát hoá.

---

## Nguồn số liệu (mọi con số đều chạy lại được)

| Tệp | Nội dung |
|---|---|
| `benchmark_dpss/eval_cinc75.json` | CinC 2013, toàn bộ 75 bản ghi, 4 quy tắc chọn kênh, 2 biến thể (75 / 68) |
| `baselines/powermf_results.json` + `powermf_log.txt` | Power-MF chạy lại qua Octave, từng bản ghi |
| `baselines/octave/apply_patches.py` | Sáu bản vá MATLAB → Octave, kể cả P6 (bản vá chặn đứng) |
| `analysis/stats_results.json` + `STATS.md` | Thống kê mức chủ thể, bootstrap cụm, TOST |
| `analysis/clinical_results.json` + `CLINICAL.md` | STV, FHR, độ phủ, khoá mẹ — 32 bản ghi |
| `model/train_22_seed1.json` | Mô hình 22 ca ở seed 1, để đo độ ổn định |
| `de_cuong_latex/prep_v33.py` → `data_v33.json` | Gom số liệu cho bảng và hình của v3.3 |
| `de_cuong_latex/make_figs.py` | Sinh hình; `fig17_powermf`, `fig18_cinc75`, `fig19_m22_v2` là mới |
| `survey/scout_novelty.md` | Rà soát y văn vòng ba, phân tích từng tuyên bố "đầu tiên" |
