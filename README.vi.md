<div align="center">

# RelyFetal

**Dò phức bộ QRS thai nhi từ điện tim ổ bụng đơn kênh, có nhận biết độ tin cậy**

*Đối chuẩn không rò rỉ, phân rã đóng góp ba tầng, cổng từ chối trả lời — và một kết quả phủ định có kiểm soát về đồng điều bền vững*

Nghiên cứu khoa học sinh viên · Khoa Công nghệ Thông tin · Trường Đại học Tôn Đức Thắng · 2026–2027

[English README](README.md) · [Đề cương (PDF)](docs/De_cuong_NCKH_RelyFetal.pdf) · [Báo cáo 30 công trình (PDF)](docs/Bao_cao_30_paper.pdf) · [Demo](demo/)

</div>

---

## Đề tài này là gì

Đo nhịp tim thai bằng **một miếng dán điện cực trên bụng mẹ** — cấu hình rẻ nhất, dễ đeo nhất cho theo dõi
tại nhà, và khó nhất về xử lý tín hiệu: sóng tim mẹ lớn gấp nhiều lần sóng tim con, hai nguồn trùng dải
tần, và khi chỉ có một kênh thì không dùng được tách nguồn mù đa kênh.

Kho mã này chứa pipeline chạy được, bằng chứng thực nghiệm cho từng quyết định thiết kế, ba baseline cổ
điển tự cài lại, bản demo chạy được với đèn tin cậy, và một kết quả phủ định được kiểm soát chặt.

**Kết quả khoa học chính là phản trực giác:**

> Đổi dải thông của bộ lọc ăn **+11,00 điểm F1**.
> Dưới giao thức không rò rỉ, sáu kiến trúc mạng nằm trong **1,53 điểm** của nhau, và với **n = 5 chủ
> thể nghiên cứu này không đủ lực để phân biệt chúng theo bất kỳ chiều nào**: kiểm định tương đương
> (TOST) ở biên 1,0 điểm đã khai báo trước cho **0/7 kiến trúc là tương đương** với CNN giãn nở 26
> nghìn tham số, và để 6/7 ở trạng thái không kết luận được. Hai biến kiến trúc đủ lớn để phân giải ở
> cỡ mẫu này là giãn nở (+2,95 ở cùng số tham số) và trường tiếp nhận (+4,49).

Cách viết cũ của README — *"tám kiến trúc không phân biệt được"* — là một kết luận tương đương rút ra
từ `p > 0,05`, tức từ **vắng mặt bằng chứng**. Tuyên bố đó được rút lại. Câu suy rộng kèm theo ("cả
ngành đã tối ưu sai tầng") cũng được rút lại: nghiên cứu này đo 5 sản phụ, không đo một thập kỷ công
trình.

---

## Kết quả chính

Giao thức xuyên suốt: chấm ở mức sự kiện, dung sai **±50 ms**, ghép một-đối-một tham lam đối chiếu với
Hungarian, chọn kênh **mù nhãn**.

### Một mô hình, năm cấu hình dữ liệu

| Bộ dữ liệu | Sản phụ | Phút | Nhãn | F1, kênh PSD mù nhãn | KTC 95 % (bootstrap cụm) | F1, trung bình 4 kênh |
|---|---:|---:|---|---:|---|---:|
| ADFECGDB (PhysioNet), tách bản ghi | 5 | 25 | điện cực da đầu | **99,21** | [97,87; 99,95] | 97,45 |
| Silesia B2 chuyển dạ, 12 bản ghi | 12 | 60 | điện cực da đầu | 97,17 | [92,68; 99,75] | 95,26 |
| Silesia B2, chỉ 7 bản ghi chưa thấy, zero-shot | 7 | 35 | điện cực da đầu | 95,87 | [88,41; 99,84] | 93,73 |
| **Silesia B1 thai kỳ 32–42 tuần, zero-shot** | 10 | 200 | gián tiếp | **93,30** | [84,93; 99,37] | 91,31 |
| CinC 2013 set-a, zero-shot, **đủ 75 bản ghi** | 75 | 75 | cộng đồng gán | 71,21 | SD 33,96, trung vị 94,34¹ | 64,78 |

Khoảng tin cậy là bootstrap cụm theo chủ thể, phân vị 95 % (10.000 lần lấy mẫu lại, seed 0;
`analysis/boot_ci_table1.py` → `analysis/boot_ci_table1.json`). Chúng thay cho `± SD` của bản trước,
vì khoảng t theo SD chạy vượt quá 100 % F1.

¹ **Rút lại.** Các bản trước của bảng này ghi **59,15 [38,32; 81,01]** cho CinC 2013, đo trên **mẫu 10
bản ghi** của set-a. Con số đó **bị rút**: mẫu 10 bị lệch, và trên đủ 75 bản ghi cùng mô hình, cùng quy
tắc mù nhãn cho **71,21**. Chưa tính bootstrap cụm cho trung bình trên 75 bản ghi, nên ở đây ghi SD và
trung vị thay vì bịa ra một khoảng tin cậy (`benchmark_dpss/eval_cinc75.json`).

Mô hình chỉ huấn luyện trên 5 ca chuyển dạ, chưa từng thấy dữ liệu thai kỳ. Chuyển từ chuyển dạ sang
thai kỳ *cùng hệ ghi* mất ~4 điểm; chuyển sang *hệ ghi khác* (CinC 2013) mất ~26 điểm và phân bố
**lưỡng cực** — 15/75 bản ghi hoàn hảo, 22/75 dưới 50. Thứ phá vỡ tổng quát hoá là thiết bị và bố trí
điện cực, không phải tuổi thai.

Kiểm tra rò rỉ bằng tương quan chéo cho thấy **5 trong 12 bản ghi Silesia B2 chính là 5 bản ghi
PhysioNet** (NCC 0,988–0,994). Năm bản đó được chấm bằng fold checkpoint chưa thấy chúng; số sản phụ độc
lập vì vậy là **22**, không phải 27.

### Huấn luyện lại trên 22 sản phụ

Tách theo nhóm 11 fold trên 22 sản phụ độc lập (19 huấn luyện / 1 validation / 2 kiểm thử mỗi fold, tăng
cường dữ liệu khi huấn luyện, ngưỡng chọn trên chủ thể validation). Wilcoxon ghép cặp với mô hình 5 ca trên
cùng chủ thể và kênh:

| Nhóm | n | Mô hình 5 ca | **Mô hình 22 ca** | p | thắng/thua |
|---|---:|---:|---:|---:|---|
| PhysioNet chuyển dạ | 5 | 99,21 | 99,40 | 1,00 | 2/2 |
| Silesia B2 chuyển dạ, chưa thấy | 7 | 95,87 | 96,82 | 0,125 | 4/0 |
| **Silesia B1 thai kỳ** | 10 | 93,30 | **97,15** | **0,037** | 9/1 |
| Toàn bộ 22 | 22 | 95,46 | **97,56** | **0,007** | 15/3 |

#### Zero-shot sang hệ ghi khác (CinC 2013) — nay đã chạy đủ 75 bản ghi

> **Rút lại.** Mọi con số CinC 2013 mà README này từng ghi trước ngày 12/09/2026 — **59,15**, **69,31**,
> **77,34**, **90,34** — đều đo trên **mẫu 10 bản ghi** của set-a. Cả bốn đều **bị rút**. Mẫu 10 bị lệch
> **cả hai chiều**, nên đây không phải chuyện làm tròn: nó đổi cả kết luận xem quy tắc chọn kênh nào
> thắng. Toàn bộ 75 bản ghi nay đã chạy (`benchmark_dpss/eval_cinc75.py` → `eval_cinc75.json`).

Con số chính là **quy tắc PSD mù nhãn, khai báo trước**, trên đủ 75 bản ghi:

| Quy tắc chọn kênh | Mô hình 5 ca | **Mô hình 22 ca** | Mù nhãn? |
|---|---:|---:|---|
| **PSD (khai báo trước, mù nhãn)** — **con số chính** | 71,21 | **79,40** | có |
| Trung bình 4 kênh | 64,78 | 74,09 | có |
| Kênh 0 cố định (**chọn hậu kiểm**) | 58,72 | 69,33 | **không** |
| Kênh oracle (dùng nhãn kiểm thử) | 78,21 | 86,87 | **không** |

Đi từ 5 lên 22 sản phụ huấn luyện đáng **+8,18 điểm** trên quy tắc mù nhãn (Wilcoxon ghép cặp
*p* = 3,2 × 10⁻¹⁰; 53 thắng / 5 thua / 17 hoà; Cliff δ = 0,23; KTC bootstrap [5,62; 11,09]). Số bản ghi
đạt F1 ≥ 90 tăng từ 42 lên 48; số bản dưới 50 giảm từ 22 xuống 16.

**Quy tắc hậu kiểm không chỉ sai về liêm chính — nó còn sai về sự kiện.** Trên mẫu 10 bản ghi, kênh 0 cố
định có vẻ hơn quy tắc PSD mù nhãn tới 21 điểm (90,34 so với 69,31), và chính khoảng cách biểu kiến đó là
lý do kênh cố định từng được đưa lên. Trên đủ 75 bản ghi, kênh 0 cố định chỉ đạt **69,33**, tức **kém quy
tắc PSD mù nhãn 10,07 điểm** và là **quy tắc tệ nhất trong bốn**. Chọn siêu tham số sau khi nhìn tập đánh
giá đã sinh ra một con số lạc quan khoảng 21 điểm và một kết luận đảo ngược khi xét đủ mẫu.

Quy tắc chọn kênh, chứ không chỉ bộ dò, có mất độ chính xác khi đổi hệ ghi — nhưng ít hơn nhiều so với
bản công bố cũ: trong miền quy tắc PSD kém oracle **0,02–1,90 điểm** (ADFECGDB 0,02, Silesia B2 0,66,
Silesia B1 1,90); ngoài miền kém **7,47 điểm** (79,40 so với 86,87). Con số **22,33 điểm** trước đây
**bị rút** — nó cũng đến từ mẫu 10 bản ghi.

**Biến thể loại trừ khai báo trước.** Bảy bản ghi set-a có chú thích tham chiếu không đáng tin (a33, a38,
a47, a52, a54, a71, a74 — Behar/Oster/Clifford, CinC 2013;40:297–300); quy tắc loại được khai báo trước
khi chạy. Trên 68 bản còn lại, quy tắc PSD mù nhãn cho **72,08 → 80,70** (mô hình 5 ca → 22 ca). Cả hai
biến thể đều được báo cáo; không biến thể nào được chọn sau khi đã thấy kết quả.

Trung vị lệch so với nhãn da đầu giữ ở 0,0 ms, nên nhãn gián tiếp của B1 không kéo mô hình. Đường cong
hiệu quả mẫu (1 → 2 → 3 ca huấn luyện: 91,2 → 93,4 → 97,5) chưa bão hoà — vì thế 22 ca vẫn còn giúp.

**Độ ổn định theo seed (kết quả mới).** Huấn luyện lại mô hình 22 ca với seed 1 làm F1 từng chủ thể
đổi trung bình **0,28 điểm** trên 20 chủ thể chung, lớn nhất **2,81** (B2_03). Ngưỡng quyết định từng
fold kém ổn định hơn: seed 1 trải 0,50–0,80 so với 0,20–0,80 của seed 0 (seed 0 có fold 10 dùng ngưỡng
cực đoan 0,20).

### Phân rã đóng góp ba tầng

| Tầng | Δ Macro F1 (mức chủ thể) | KTC 95 % | Kết luận |
|---|---:|---|---|
| Front-end tín hiệu (chọn dải thông) | **+11,00** | không kiểm chứng lại được¹ | hiệu ứng lớn nhất |
| Độ dài ngữ cảnh và đầu ra từng mẫu | +4,49 | [1,58; 7,43] bootstrap; [−0,29; 9,27] t ghép cặp | dương, khoảng rộng |
| Họ kiến trúc, ở ngữ cảnh cố định | +0,41 | nằm trong biên 1,0 điểm | **không phân giải được ở n = 5** |

¹ `pilot_evidence/band_ablation.json` chỉ lưu tổng hợp theo dải, không lưu F1 từng bản ghi × kênh, nên
so sánh tầng 1 không kiểm định lại được ở mức chủ thể. Giá trị `p < 0,001` từng công bố cho tầng này
được **rút lại vì không kiểm chứng được**, chứ không phải được xác nhận.

**Mọi giá trị p trên ADFECGDB đã bị bỏ.** Với n = 5 chủ thể, giá trị p hai phía nhỏ nhất mà kiểm định
Wilcoxon hạng có dấu chính xác có thể cho là 2/2⁵ = **0,0625**, nên *không* so sánh nào trên bộ này đạt
được p < 0,05 ở mức chủ thể, bất kể hiệu ứng lớn đến đâu. Các con số `1,9 × 10⁻⁶`, `5,7 × 10⁻⁶` và
`0,0000` trước đây được tính trên 20–60 hàng (bản ghi × kênh × seed) coi như độc lập — đó là giả lập
(pseudo-replication). Bảng đối chiếu đầy đủ ở [`analysis/STATS.md`](analysis/STATS.md).

### Baseline cổ điển tự cài lại (ADFECGDB, cùng giao thức, siêu tham số chỉ chọn trên r01)

| Phương pháp | 4 kênh (n=20) | Kênh PSD (n=5) | Δ so với mô hình (mức chủ thể) | KTC 95 % bootstrap | KTC 95 % t ghép cặp | Vững? |
|---|---:|---:|---:|---|---|---|
| Trừ mẫu + Pan–Tompkins | 78,96 ± 23,52 | 87,68 | −18,49 | [−30,60; −6,38] | **[−38,80; +1,81]** | **không — chứa 0** |
| TS-PCA + Pan–Tompkins | 91,05 ± 10,17 | 96,74 | −6,40 | [−8,09; −4,70] | [−9,10; −3,69] | có |
| Độ nhô đỉnh trên **cùng front-end** | 86,39 ± 11,14 | 92,03 | −11,06 | [−14,51; −7,80] | [−16,38; −5,73] | có |
| **FetalQRS-TCN** | **97,45 ± 4,44** | **99,21** | — | — | — | — |

**Ba baseline này không vững như nhau và không được đọc chung một khối.** Với TS-PCA và độ nhô đỉnh,
khoảng tin cậy loại trừ 0 trên cả hai thang. Với TS thuần thì không: khoảng t bảo thủ là
[−38,80; +1,81], **chứa 0**, nên khoảng cách 18,49 điểm là do biến thiên giữa các sản phụ (một bản ghi
TS sụp hẳn), không phải một lợi thế ổn định.

Baseline thứ ba tách riêng phần đóng góp của mạng: cùng tín hiệu dư, chỉ thay mạng bằng lấy đỉnh → mạng
đáng **+11,06 điểm**, KTC 95 % [7,80; 14,51], tốt hơn ở 5/5 sản phụ. TS-PCA trên kênh tốt nhất đạt
96,74 — phương pháp cổ điển vẫn mạnh, nhất quán với phát hiện về front-end.

### Power-MF — đã chạy lại tại chỗ, và câu hỏi mà repo này thật sự trả lời

Power-MF (Jaeger và cs. 2024) là phương pháp **đa kênh**: dùng 4 đạo trình bụng và hai vòng ICA. Nay nó
đã được **chạy lại từ chính mã nguồn MATLAB của tác giả** dưới GNU Octave, chấm bằng *bộ chấm của nhóm*
(±50 ms, ghép tham lam 1-1) trên cùng 22 chủ thể (`baselines/powermf_fair_run.py`,
[`baselines/BASELINES.md`](baselines/BASELINES.md)).

> **Rút lại.** Phần so sánh Power-MF công bố sáng 12/09/2026 — *"94,87 so với 97,61, hiệu +2,74"* và
> *"98,38 so với 97,33, hiệu −1,06"* — **bị rút toàn bộ**. Cả hai dựa trên một **bản cổng chuyển hỏng**,
> không phải trên Power-MF. Hàm `findpeaks` của gói `signal` trong Octave cài `MinPeakDistance` bằng ma
> trận khoảng cách đôi một O(k²), gây tràn bộ nhớ trên 6 bản ghi Silesia B1 dài (2.395.600 mẫu sau nội
> suy ×4); MATLAB — nền tảng của tác giả — dùng thuật toán tham O(k log k) nên không bao giờ gặp lỗi này.
> **Đây là lỗi của nhóm, không phải tính chất của phương pháp.** Giả thuyết cũ rằng
> `ms_minpeakdistance = 340 ms` quá sát **cũng bị rút**: đo trên chính nhãn tham chiếu, **0,00 %** khoảng
> RR của B1_01 nằm dưới 340 ms (`baselines/powermf_rr_diag.json`), và tham số này được giữ nguyên ở giá
> trị mặc định của tác giả suốt quá trình. `baselines/octave/findpeaks_mpd.m` tái lập đúng ngữ nghĩa của
> MATLAB bằng danh sách liên kết đôi, O(k), kiểm chứng 48/48 trường hợp.

**Kiểm chứng ngoài cho bản vá.** Sau khi vá, Power-MF đạt **99,40 ± 0,51** trên Silesia B1. Số **đã công
bố của chính tác giả** trên tập đó là **99,46** (`baselines/powermf_published.json`, trích từ
`Results/*.mat` của repo gốc). Lệch 0,06 điểm — cổng chuyển giờ đã đúng, và đó chính là lý do mọi con số
trước khi vá phải bị rút.

| Bộ dữ liệu | n | Power-MF, **4 kênh** | Power-MF, **1 kênh** | **RelyFetal, 1 kênh** |
|---|---:|---:|---:|---:|
| ADFECGDB | 5 | 99,01 | 92,37 | **99,40** |
| Silesia B2 (chuyển dạ) | 7 | 97,90 | 87,28 | 96,82 |
| Silesia B1 (thai kỳ) | 10 | **99,40** | 83,48 | 97,15 |
| **Toàn bộ 22 chủ thể** | 22 | **98,83** | 86,71 | 97,56 |
| CinC 2013 set-a | 75 | chưa chạy | 62,82 | **79,40** |

Thống kê mức chủ thể (bootstrap cụm, 10.000 lần lấy mẫu lại **chủ thể**, seed 0; Wilcoxon ghép cặp;
Cliff δ), toàn bộ 22 chủ thể:

| So sánh | Δ F1 | KTC 95 % | p | Cliff δ | thắng/hoà/thua |
|---|---:|---|---:|---:|---|
| RelyFetal − Power-MF (4 kênh) | −1,27 | [−3,08; +0,27] | 0,156 | 0,260 | 18/0/4 |
| RelyFetal − Power-MF (1 kênh) | **+10,85** | [+6,80; +15,40] | 4,8 × 10⁻⁷ | 0,698 | **22/0/0** |
| Power-MF (1 kênh) − Power-MF (4 kênh) | −12,12 | [−18,27; −6,90] | 1,4 × 10⁻⁶ | — | 1/0/21 |

Theo từng tập, RelyFetal − Power-MF (4 kênh): ADFECGDB **+0,39** [+0,22; +0,60], 5/0/0 — khoảng tin cậy
**không chứa 0**, tức **ta hơn** ở tập này; Silesia B2 −1,08 [−4,04; +0,54], 6/0/1; Silesia B1 −2,25
[−5,55; +0,32], 7/0/3.

**Trung bình che mất hình dạng của kết quả.** **Trung vị** hiệu số theo chủ thể là **+0,23** và RelyFetal
thắng **18 trong 22** chủ thể. Trung bình bị kéo âm bởi đúng ba bản ghi — B1_07 (86,56 so với 99,44;
−12,88), B1_06 (89,45 so với 99,97; −10,51) và B2_03 (79,72 so với 89,49; −9,77), cộng một bản thứ tư
nhẹ hơn là B1_10 (−1,86). Bất cứ bản tóm tắt nào chỉ nêu trung bình đều mô tả sai phân bố này.

**Đại lượng thật sự được đo.** Câu hỏi không phải "ai thắng", mà là: *một mạng đơn kênh 113.481 tham số
lấy lại được bao nhiêu phần lợi ích mà tách nguồn đa kênh mang lại?* Lợi ích đó nay đo được, vì Power-MF
đã chạy ở cả hai cấu hình: bỏ tách nguồn đa kênh khiến **chính Power-MF mất 12,12 điểm F1**
(98,83 → 86,71). Mạng đơn kênh lấy lại **10,85 điểm trong số đó — tức 89,5 % — chỉ bằng một đạo trình**.
Kết quả: **không phân biệt được với Power-MF đa kênh** (−1,27; KTC [−3,08; +0,27]; p = 0,156), và **hơn
hẳn Power-MF khi Power-MF bị giới hạn về cùng một đạo trình** (+10,85; 22/22 chủ thể).

Đây **không** phải tuyên bố vượt SOTA, và từ đó không được dùng ở đây. Power-MF với 4 kênh vẫn hơn về
trung bình thô.

### Cổng từ chối trả lời và kết quả phủ định về đồng điều bền vững

Bộ phân loại "mô hình sẽ sai ở đoạn này không?" huấn luyện trên ADFECGDB, kiểm thử **xuyên miền** trên
CinC 2013:

| Nhóm đặc trưng | AUROC | KTC 95 % (bootstrap theo 10 bản ghi) | F1 ở độ phủ 80 % | F1 ở độ phủ 50 % |
|---|---:|---|---:|---:|
| Từ chối ngẫu nhiên | 0,500 | — | 62,03 | 62,14 |
| 16 đặc trưng topo (Takens + ripser, sublevel H0) | **0,566** | — | 63,40 | 64,44 |
| 12 chỉ số cổ điển | **0,929** | [0,830; 0,982] | **69,40** | **84,51** |
| Cả 28 | 0,905 | — | 69,41 | 82,44 |
| Oracle | — | — | 74,55 | 97,81 |

**Con số 0,929 phần lớn là hiệu ứng GIỮA bản ghi.** Năm trong mười bản ghi CinC không có đoạn xấu nào,
nên AUROC gộp chủ yếu trả lời câu *"đây có phải bản ghi xấu không?"*. Trung bình trên năm bản ghi có
cả hai lớp, **AUROC TRONG bản ghi chỉ 0,721** [0,517; 0,898] — và chỉ con số này mới mô tả điều cổng
từ chối làm được bên trong một phiên theo dõi, tức đúng tình huống lâm sàng.

Đặc trưng đồng điều bền vững gần như không hơn ngẫu nhiên, không bổ sung gì cho chỉ số cổ điển, và đổi
dấu tương quan giữa hai bộ dữ liệu. Chỉ số dự báo lỗi mạnh nhất là độ tự tin của chính mô hình
(`prob_max`, AUROC 0,970), độ đều khoảng RR (0,915) và tỉ lệ năng lượng 10–60 Hz (0,904). Bản thân cổng
từ chối có tác dụng: +7,4 điểm F1 ở độ phủ 80 %. **Phần đóng góp topo đề xuất ban đầu đã được kiểm chứng
có kiểm soát và rút lại.**

---

## Mô hình

`FetalQRS-TCN` — mạng tích chập giãn nở có kết nối dư, chuỗi sang chuỗi.

| Thuộc tính | Giá trị |
|---|---|
| Tham số huấn luyện được | **113.481** |
| Kích thước checkpoint | 0,48 MB |
| Trường tiếp nhận | 379 mẫu = **1.516 ms** |
| Độ trễ một cửa sổ 4 giây | **4,35 ms** trên CPU (920× thời gian thực) |
| Đầu vào | 2 × 1000 — tín hiệu dư sau khử mẹ + tín hiệu gốc, đoạn 4 s ở 250 Hz |
| Đầu ra | một logit cho **từng mẫu**; nhãn bản đồ nhiệt Gauss, σ = 12 ms |

Dưới giao thức đã sửa (10–60 Hz, 5 fold tách bản ghi, ngưỡng chọn trên bản ghi validation riêng), tám kiến
trúc cửa sổ 300 ms đạt 37,5–92,4; mô hình chuỗi 4 giây đầy đủ đạt 97,43. CNN giãn nở được giữ vì **hiệu
quả tham số**, không phải vì họ kiến trúc ưu việt.

---

## Demo

```bash
python demo/app.py        # → http://127.0.0.1:7860
```

Gradio, một trang: tải EDF/WFDB/CSV hoặc chọn bản ghi mẫu, tự động chọn kênh mù nhãn, năm tầng tín hiệu
(thô → lọc → dư → xác suất → kết quả), đồ thị nhịp tim thai, và **đèn tin cậy**. Chọn bản ghi ADFECGDB
thì tự động dùng fold checkpoint chưa thấy bản ghi đó.

| Đèn | Bản ghi | F1 trung bình | F1 thấp nhất |
|---|---:|---:|---:|
| Xanh | 8 | 99,54 | 96,54 |
| Vàng | 5 | 50,51 | 21,05 |
| Đỏ | 2 | 19,36 | 16,96 |

Không bản ghi nào F1 < 96,5 bị đèn xanh. Hai bản ghi tệ nhất của CinC bị bắt bởi luật "bám nhịp mẹ"
(≥ 60 % nhịp "thai" trùng đỉnh R mẹ). Kiểm thử ba tầng: unit test lõi, HTTP, và gọi API `gradio_client`.
Ảnh chụp thật trong [`demo/screenshots/`](demo/screenshots/).

> Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.

## API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000          # hoặc: docker compose up --build
curl http://127.0.0.1:8000/health
curl -F "file=@signal.npy" -F "lead=auto" -F "fs=1000" http://127.0.0.1:8000/analyze
```

Lớp FastAPI bọc `demo/core.py`, ba điểm cuối: `GET /health` (checkpoint production có sẵn không),
`GET /model` (số tham số, trường tiếp nhận, ngưỡng, cấu hình) và `POST /analyze` (nhận EDF/CSV/TXT/NPY;
trả `n_beats`, `fhr_mean`, `beats_ms`, `confidence{level,score,reasons}`, `latency_ms`, thêm `metrics` nếu
gửi kèm file nhãn). Lỗi đầu vào trả về JSON `4xx`, không bao giờ là traceback. Lược đồ yêu cầu/phản hồi trong
[`api/README.md`](api/README.md); kiểm thử ở `tests/test_api.py` (không cần mạng, `fastapi.testclient`).

---

## Cấu trúc kho mã

```
model/                    Thư viện lõi, huấn luyện, suy luận, trọng số
├─ fqrs_model.py            Cài đặt tham chiếu — mọi hằng số truy được về một thí nghiệm
├─ train_final.py           Huấn luyện tách bản ghi → 5 checkpoint fold + 1 production
├─ predict.py               Suy luận dòng lệnh: EDF / WFDB / CSV / NPY
├─ download_data.py         Nguồn PhysioNet với thẻ dữ liệu SHA-256
├─ download_silesia.py      Tải figshare có tiếp tục (URL hết hạn sau 10 s, cần Range + thử lại)
├─ silesia_loader.py        Đọc .ecg Silesia (int16 big-endian, 500 Hz) → 1 kHz
└─ checkpoints/             6 mô hình đã huấn luyện, 0,48 MB mỗi cái

benchmark_dpss/           Bộ đối chuẩn
├─ _paths.py                Giải quyết đường dẫn (kho mã tự chứa)
├─ full_measure.py          Bộ chỉ số đầy đủ + chi phí tính toán đo thật
├─ blind_lead.py            Chọn kênh mù nhãn theo PSD, trong và ngoài miền
├─ silesia_eval.py          Đánh giá Silesia B1/B2 + kiểm tra rò rỉ bằng tương quan chéo
└─ all_leads.py             Phân tích từng kênh

baselines/                Phương pháp cổ điển tự cài lại
├─ ts_baseline.py           TS, TS-PCA, độ nhô; bộ dò Pan–Tompkins; Wilcoxon so với mô hình
├─ powermf_fair_run.py      Power-MF (4 kênh) chạy lại dưới Octave, kèm bản vá findpeaks P7
├─ powermf_1ch.py           Power-MF giới hạn về một đạo trình (bản cài lại Python)
├─ octave/findpeaks_mpd.m   MinPeakDistance O(k) đúng ngữ nghĩa MATLAB (kiểm chứng 48/48)
└─ BASELINES.md             Báo cáo baseline đầy đủ, chẩn đoán lỗi cổng chuyển và phần rút lại

fsqi/                     Thí nghiệm chỉ số chất lượng tín hiệu (đóng góp C3)
├─ fsqi.py                  28 đặc trưng: Takens+ripser H0/H1, sublevel H0, chỉ số cổ điển
├─ eval_fsqi.py             Dự báo lỗi xuyên miền, đường cong rủi ro–độ phủ
└─ README.md                Báo cáo kết quả phủ định đầy đủ

demo/                     Ứng dụng Gradio
├─ core.py                  Logic pipeline, không phụ thuộc giao diện, có unit test
├─ app.py                   Giao diện một trang với đèn tin cậy
└─ screenshots/             Ảnh chụp thật từ ứng dụng đang chạy

pilot_evidence/           Toàn bộ thí nghiệm tiền khả thi, kèm nhật ký
├─ arch_loro.py             Bảng 8 kiến trúc đã sửa (tách bản ghi, 10–60 Hz)
├─ band_ablation.py         8 dải thông ứng viên
├─ seq_search.py            Quét trường tiếp nhận
└─ seq_loro.py              3 seed + Wilcoxon ghép cặp

de_cuong_latex/           Đề cương — mã nguồn LaTeX, hình và bảng sinh từ dữ liệu
survey/                   Khảo sát 30 công trình + sổ số liệu đã kiểm chứng
docs/                     Tài liệu đã biên dịch (PDF + DOCX)
tests/                    Kiểm thử nhanh ghim mọi con số được trích dẫn
```

---

## Cài đặt và chạy

```bash
git clone https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027.git
cd nckhsv_tdtu2026-2027
python -m venv .venv && .venv\Scripts\activate     # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

python model/download_data.py --root model/data --only adfecgdb    # ~15 MB từ PhysioNet
python model/predict.py --input model/data/adfecgdb/r01.edf --lead 1 --annot qrs \
                        --checkpoint model/checkpoints/fetalqrs_tcn_fold_r01.pt
```

Chỉ cần CPU. Huấn luyện lại sáu checkpoint mất ~30 phút trên laptop.

Chạy lại toàn bộ:

```bash
python model/train_final.py --epochs 6 --seed 0
python benchmark_dpss/full_measure.py
python benchmark_dpss/blind_lead.py
python baselines/ts_baseline.py                          # ~2 phút
python pilot_evidence/arch_loro.py                       # ~20 phút
python model/download_silesia.py && python benchmark_dpss/silesia_eval.py
python fsqi/eval_fsqi.py                                 # ~4 phút
python demo/run_check.py && python demo/smoke_app.py
pytest tests/ demo/test_core.py                          # 53 kiểm thử
```

---

## Dữ liệu

Không phân phối lại bản ghi sinh lý nào. Script tải ghi SHA-256 cho từng tệp.

| Bộ dữ liệu | Nguồn | Giấy phép | Dùng cho |
|---|---|---|---|
| ADFECGDB | physionet.org/content/adfecgdb · DOI 10.13026/C2RP4B | ODC-BY 1.0 | huấn luyện, đánh giá tách bản ghi |
| Silesia B1/B2 (Matonia 2020) | figshare DOI 10.6084/m9.figshare.c.4740794 · *Sci Data* 7:200 | CC0 | tổng quát hoá zero-shot |
| CinC 2013 set-a | physionet.org/content/challenge-2013 | ODC-BY 1.0 | tổng quát hoá sang hệ ghi khác |

Silesia B1 (thai kỳ) **không có điện cực da đầu**; nhãn là gián tiếp (tác giả khử mẹ + dò tự động + chuyên
gia sửa) và lệch 8–12 ms sau đỉnh R bụng ở 5/10 bản ghi. F1 trên B1 đo mức đồng thuận với pipeline đó, không
phải sự thật sinh lý.

---

## Hạn chế còn tồn tại

- **Cả 22 sản phụ đều từ một bệnh viện, một hệ ghi.** Trên hệ ghi khác (CinC 2013, đủ 75 bản ghi) mô
  hình 22 ca đạt **79,4 theo quy tắc chọn kênh mù nhãn**, so với 97–99 trong miền; dữ liệu đa trung tâm
  là khoảng trống còn lại. Lần chạy 22 ca là bốn epoch và chưa tách riêng đóng góp của tăng cường dữ
  liệu; seed thứ hai làm F1 từng chủ thể đổi trung bình 0,28 điểm.
- **Cỡ mẫu là hạn chế ràng buộc nhất.** ADFECGDB có 5 sản phụ, nên không so sánh nào trên ADFECGDB đạt
  được ý nghĩa thống kê ở mức chủ thể và mọi khoảng tin cậy ở đây đều rộng. Bảng kiến trúc thiếu lực về
  mặt thiết kế, không phải "không kết luận được" do ngẫu nhiên. (CinC 2013 nay có đủ 75 bản ghi nên
  không còn là ràng buộc cỡ mẫu.)
- **CinC 2013 set-a nay đã đánh giá đủ (75 bản ghi, và 68 bản theo quy tắc loại khai báo trước).** Việc
  chấm vẫn dùng bộ chấm ±50 ms của nhóm chứ không phải bộ chấm chính thức của cuộc thi, nên đây *không*
  phải bài dự thi chính thức dù tập bản ghi đã khớp.
- **Cổng tin cậy học được hiệu chuẩn theo mô hình 5 ca**, quá thận trọng trên thai kỳ (35 % xanh trên Silesia
  so với 82 % của luật). Chưa hiệu chuẩn lại cho mô hình 22 ca.
- **Bảng kiến trúc chỉ một seed, ba epoch**, và bỏ Transformer cùng hai biến thể 2D vì chi phí. Thứ tự
  không đổi nhưng con số tuyệt đối còn thiếu huấn luyện.
- **Đèn tin cậy trong demo là luật đặt tay.** Ngưỡng bám mẹ 60 % được đặt sau khi nhìn một bản ghi đánh giá.
  Bộ phân loại chỉ số cổ điển đã học trong `fsqi/` nên thay vào.
- **Power-MF nay đã chạy lại tại chỗ, nhưng mới trên 22 chủ thể của nhóm** — chưa chạy trên CinC 2013,
  nơi mới chỉ đo được bản đơn kênh. Bản đơn kênh là phần cài lại của nhóm theo mô tả đã công bố, không
  phải mã của tác giả, nên nó mang theo cách hiểu của nhóm về phương pháp.
- **Con số +11,00 điểm của dải thông đo trên GBM cửa sổ 300 ms, không phải trên TCN.** Khảo sát dải lọc
  trên chính TCN vẫn đang chạy (`pilot_evidence/band_tcn.py`; đến giờ dải 10–60 Hz = 98,07 ± 4,05, còn 3
  dải). Đến khi chạy xong, con số tầng 1 mô tả một mô hình khác với mô hình mà repo này phát hành.
- **Chỉ số chất lượng topo đề xuất ban đầu không hoạt động** (AUROC 0,566 so với 0,929). Được báo cáo là
  kết quả phủ định, không giấu.

---

## Điều gì đã được kiểm chứng, điều gì chưa

Bảng này để người đọc không phải đoán mức độ tin cậy của từng con số. *Kiểm chứng ngoài* nghĩa là đối
chiếu được với một nguồn nằm ngoài repo này.

| Tuyên bố | Trạng thái | Bằng chứng |
|---|---|---|
| F1 trong miền (ADFECGDB 99,40; B2 96,82; B1 97,15) | **Đo lại được trong repo** | `benchmark_dpss/eval_22.json`, giao thức tách theo nhóm |
| Không rò rỉ giữa 5 bản PhysioNet và Silesia B2 | **Đã kiểm** | tương quan chéo NCC 0,988–0,994; chấm bằng fold checkpoint chưa thấy bản ghi |
| CinC 2013 = 79,40 trên đủ 75 bản ghi | **Đo lại được trong repo** | `benchmark_dpss/eval_cinc75.json` |
| Bản cổng chuyển Power-MF của nhóm là đúng | **Kiểm chứng NGOÀI** | ta đo 99,40 trên B1; tác giả công bố 99,46 (`baselines/powermf_published.json`) — lệch 0,06 |
| Power-MF 4 kênh / 1 kênh / RelyFetal (bảng 3 cột) | **Đo lại được trong repo** | `baselines/powermf_fair_stats.json`, `powermf_1ch.json` |
| Thêm dữ liệu giúp thật, không phải học phong cách nhãn | **Có bằng chứng độc lập** | m12 (chưa từng thấy B1) 74,34 so với m22 79,40 trên CinC — bộ nhãn do người khác chấm (`analysis/ABLATION_B1.md`) |
| +11,00 điểm cho dải thông | **CHƯA kiểm chứng trên TCN** | đo trên GBM cửa sổ 300 ms; khảo sát trên TCN đang chạy (`pilot_evidence/band_tcn.py`) |
| Độ chính xác thời điểm (jitter, STV) trên Silesia B1 | **KHÔNG dùng được** | nhãn B1 là gián tiếp; lệch hệ thống theo mô hình (m5 6,50 / m12 6,50 / m22 3,25 ms) |
| Dùng làm máy đo STV độc lập | **KHÔNG** | độ chệch STV +0,33 ms trên ADFECGDB nhưng +20,50 ms trên CinC (`analysis/CLINICAL.md`) |
| "8 kiến trúc không phân biệt được" | **ĐÃ RÚT** | TOST biên 1,0 điểm bác bỏ: cnn_m kém hơn, cnn_l hơn (`analysis/STATS.md`) |
| Đóng góp của đặc trưng tô-pô (C3) | **ĐÃ RÚT — kết quả phủ định** | AUROC 0,566 so với 0,929 của chỉ số cổ điển (`fsqi/README.md`) |
| Điểm so được với bảng xếp hạng CinC 2013 | **KHÔNG** | dùng bộ chấm ±50 ms của nhóm, không phải bộ chấm chính thức |
| Ổn định theo seed | **Mới 2 seed** | độ lệch tuyệt đối trung bình 0,28 điểm trên 20 chủ thể |
| Trung tâm thứ hai có nhãn fQRS thật | **CHƯA có** | NInFEA không phân phối nhãn |

Mọi con số trong README này truy ngược được về một tệp JSON trên đĩa. Phần rút lại được ghi ngay tại chỗ
con số cũ từng đứng, không xoá lặng lẽ.

---

## Giấy phép

Mã nguồn **MIT**. Tài liệu, hình vẽ và trọng số **CC BY 4.0**. Dữ liệu sinh lý và công trình bên thứ ba
**không** phân phối lại — xem [`LICENSE`](LICENSE).

> **Không phải thiết bị y tế.** Bản mẫu nghiên cứu, chưa thẩm định lâm sàng, không có chứng nhận quản lý.
