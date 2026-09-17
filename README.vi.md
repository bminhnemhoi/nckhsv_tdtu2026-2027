<div align="center">

# RelyFetal

**Dò phức bộ QRS thai nhi từ điện tim ổ bụng đơn kênh, có nhận biết độ tin cậy**

*Đối chuẩn không rò rỉ, phân rã đóng góp ba tầng, cổng từ chối trả lời — và một kết quả phủ định có kiểm soát về đồng điều bền vững*

Nghiên cứu khoa học sinh viên · Khoa Công nghệ Thông tin · Trường Đại học Tôn Đức Thắng · 2026–2027

[English README](README.md) · [Đề cương (PDF)](docs/De_cuong_NCKH_RelyFetal.pdf) · [Báo cáo 30 công trình (PDF)](docs/Bao_cao_30_paper.pdf) · [Demo](demo/)

</div>

---

> **Bạn tiếp nhận dự án? Đọc [`HANDOFF.md`](HANDOFF.md) trước** — cài đặt, tải dữ liệu, bản đồ kho mã, nguồn
> sự thật cho mọi con số, quy tắc liêm chính, các bẫy kỹ thuật đã biết, và danh sách việc tiếp theo.
> Thay đổi và tuyên bố đã rút theo từng vòng: [`CHANGELOG.md`](CHANGELOG.md).

---

## Đề tài này là gì

Đo nhịp tim thai bằng **một miếng dán điện cực trên bụng mẹ** — cấu hình rẻ nhất, dễ đeo nhất cho theo dõi
tại nhà, và khó nhất về xử lý tín hiệu: sóng tim mẹ lớn gấp nhiều lần sóng tim con, hai nguồn trùng dải
tần, và khi chỉ có một kênh thì không dùng được tách nguồn mù đa kênh.

Kho mã này chứa pipeline chạy được, bằng chứng thực nghiệm cho từng quyết định thiết kế, ba baseline cổ
điển tự cài lại, bản demo với đèn tin cậy, và một kết quả phủ định được kiểm soát chặt. Mọi con số trong
README này truy ngược được về một tệp JSON trên đĩa; tệp tổng hợp là
[`survey/facts_phase4.json`](survey/facts_phase4.json). Mọi phát biểu đã rút được ghi ngay tại chỗ nó
từng đứng (mục *Rút lại — danh sách đầy đủ* ở cuối), không xoá lặng lẽ.

**Kết quả chính, nói thẳng:**

> Trên bộ học cửa sổ 300 ms, đổi dải thông bộ lọc ăn **+11,00 điểm F1**; đo lại trên chính TCN với 22 sản
> phụ, cùng thay đổi đó chỉ đáng **+2,44 [−0,04; +6,29]** (khoảng chứa 0, `pilot_evidence/band_tcn.json`),
> nên **con số +11,00 bị rút** với tư cách một phát biểu về mô hình phát hành ở đây. Dưới giao thức không rò
> rỉ, sáu kiến trúc mạng nằm trong **1,53 điểm** của nhau và với **n = 5 chủ thể nghiên cứu này không đủ lực
> để phân biệt chúng theo bất kỳ chiều nào** (TOST biên 1,0 điểm: 0/7 tương đương, 6/7 không kết luận).
> Hai biến kiến trúc đủ lớn để phân giải là giãn nở (+2,95 ở cùng số tham số) và trường tiếp nhận (+4,49).

Cách viết cũ — *"tám kiến trúc không phân biệt được"* — là kết luận tương đương rút từ `p > 0,05`, tức từ
vắng mặt bằng chứng. Đã rút. Câu suy rộng cho cả ngành cũng đã rút: nghiên cứu này đo 5 sản phụ.

---

## Kết quả chính

Giao thức xuyên suốt: chấm ở mức sự kiện, dung sai **±50 ms** (quy ước CinC 2013 — chặt gấp ba ANSI/AAMI
EC57), ghép một-đối-một tham lam đối chiếu với Hungarian, chọn kênh **mù nhãn**.

### Một mô hình, năm cấu hình dữ liệu

| Bộ dữ liệu | Sản phụ | Phút | Nhãn | F1, kênh PSD mù nhãn | KTC 95 % (bootstrap cụm) | F1, TB 4 kênh |
|---|---:|---:|---|---:|---|---:|
| ADFECGDB (PhysioNet), tách bản ghi | 5 | 25 | điện cực da đầu | **99,21** | [97,87; 99,95] | 97,45 |
| Silesia B2 chuyển dạ, 12 bản ghi | 12 | 60 | điện cực da đầu | 97,17 | [92,68; 99,75] | 95,26 |
| Silesia B2, chỉ 7 bản chưa thấy, zero-shot | 7 | 35 | điện cực da đầu | 95,87 | [88,41; 99,84] | 93,73 |
| **Silesia B1 thai kỳ 32–42 tuần, zero-shot** | 10 | 200 | gián tiếp | **93,30** | [84,93; 99,37] | 91,31 |
| CinC 2013 set-a, zero-shot, **60 bản ghi sạch**¹ | 60 | 60 | cộng đồng gán | 64,04 | [55,4; 72,5] | 56,00 |

Khoảng tin cậy là bootstrap cụm theo chủ thể, phân vị 95 % (10.000 lần, seed 0;
`analysis/boot_ci_table1.py` → `analysis/boot_ci_table1.json`).

¹ **Rút lại (hai lần), và đính chính về việc ai tìm ra điều gì.** Các bản trước ghi **59,15 [38,32; 81,01]**
(mẫu 10 bản) rồi **71,21** (đủ 75 bản) cho CinC 2013. **Cả hai bị rút.** Set-a không độc lập với ADFECGDB,
và **điều này ban tổ chức Challenge đã ghi nhận từ đầu**: Silva và cs. (CinC 2013;40:149–152, Bảng 1:
"Abdominal and Direct FECG — 25 bản ghi") và Clifford và cs. (Physiol Meas 2014;35:1521, Bảng 2), kèm cảnh
báo rằng một thuật toán dự thi huấn luyện trên ADFECGDB "may have led to a bias in the results as this
database was included in set-a, set-b (and possibly a few records in set-c)". Câu đó đã nằm trong ghi chú
đọc bài của chính nhóm (`de_cuong_latex/tables/bang_baihoc.tex`, mục p20) mà nhóm bỏ sót; bản trước của
README này và của `analysis/DULIEU.md` trình bày sự chồng lấn như phát hiện của nhóm — **cách viết đó bị
rút** (`survey/RO_RI_VANLIEU.md`). Điều không nguồn nào ghi là *bản ghi set-a nào* là ADFECGDB, và phần đó
nhóm đo (`analysis/dulieu_audit.py`, cài đặt độc lập thứ hai `analysis/dulieu_m4b_verify.py`): đúng
**15/75 bản là bản sao nguyên văn của 5 bản huấn luyện** (NCC = 1,0000 cả 4 kênh đúng thứ tự, lệch RR
0,0 ms; đối chứng dương — các bản trùng B2↔PhysioNet đã biết — chỉ đạt 0,86–0,98; 60 bản còn lại tối đa
0,44 đã lọc / 0,62 thô). Mỗi bản ADFECGDB xuất hiện ba lần, là các cửa sổ 0–60, 120–180, 240–300 s:
r01→a04,a05,a22 · r04→a13,a20,a25 · r07→a19,a23,a24 · r08→a08,a15,a17 · r10→a03,a12,a14. Mọi số CinC
chính nay tính trên **60 bản sạch** (`benchmark_dpss/eval_cinc60_sach.py` → `eval_cinc60_sach.json`;
bootstrap 10.000 lần theo bản ghi, seed 0). 15 bản rò rỉ đạt 99,87 với mô hình 22 ca — đó là cách chúng
thổi phồng trung bình cũ 3,27–7,18 điểm.

Mô hình chỉ huấn luyện trên 5 ca chuyển dạ. Chuyển sang thai kỳ *cùng hệ ghi* mất ~4 điểm; chuyển sang *hệ
ghi khác* (CinC 2013, 60 bản sạch) mất ~35 điểm và phân bố tách đôi — 27/60 bản ≥ 90, 22/60 dưới 50 (chỉ
mô tả: hai đỉnh là hệ quả của chọn kênh, không phải hai quần thể, `analysis/LUONGCUC.md`). Thứ phá vỡ tổng
quát hoá là thiết bị và bố trí điện cực, không phải tuổi thai.

Kiểm tra rò rỉ bằng tương quan chéo: **5 trong 12 bản Silesia B2 chính là 5 bản PhysioNet** (NCC
0,988–0,994); chúng được chấm bằng fold checkpoint chưa thấy chúng; số sản phụ độc lập là **22**.

### Huấn luyện lại trên 22 sản phụ

Tách theo nhóm 11 fold (19 huấn luyện / 1 validation / 2 kiểm thử mỗi fold, tăng cường dữ liệu, ngưỡng
chọn trên chủ thể validation). Wilcoxon ghép cặp với mô hình 5 ca trên cùng chủ thể và kênh:

| Nhóm | n | Mô hình 5 ca | **Mô hình 22 ca** | p | thắng/thua |
|---|---:|---:|---:|---:|---|
| PhysioNet chuyển dạ | 5 | 99,21 | 99,40 | 1,00 | 2/2 |
| Silesia B2 chuyển dạ, chưa thấy | 7 | 95,87 | 96,82 | 0,125 | 4/0 |
| **Silesia B1 thai kỳ** | 10 | 93,30 | **97,15** | **0,037** | 9/1 |
| Toàn bộ 22 | 22 | 95,46 | **97,56** | **0,007** | 15/3 |

#### Zero-shot sang hệ ghi khác (CinC 2013) — 60 bản ghi sạch

> **Rút lại.** Mọi con số CinC 2013 README này từng ghi trước 12/09/2026 — **59,15**, **69,31**, **77,34**,
> **90,34** (mẫu 10 bản) rồi **71,21 / 79,40 / 86,87 / +8,18 / +7,47** và mọi số khác tính trên **đủ 75
> bản** — đều **bị rút**. Bộ đầu là mẫu lệch; bộ sau nhiễm 15 bản là bản sao dữ liệu huấn luyện (chú thích
> ¹), và còn vi phạm độc lập mức bản ghi vì 15 bản đó đến từ 5 sản phụ. Số 75 bản giữ trong
> `benchmark_dpss/eval_cinc75.json` và các báo cáo phân tích chỉ để truy vết.

Con số chính là **quy tắc PSD mù nhãn** trên 60 bản sạch (`benchmark_dpss/eval_cinc60_sach.json`):

| Quy tắc chọn kênh | Mô hình 5 ca | **Mô hình 22 ca** | Mù nhãn? |
|---|---:|---:|---|
| **PSD (khai báo trước, mù nhãn)** — **con số chính** | 64,04 | **74,28** [66,6; 81,8] | có |
| Trung bình 4 kênh | 56,00 | 67,69 | có |
| Kênh 0 cố định (**hậu kiểm, đã rút**) | 48,43 | 61,78 | **không** |
| Kênh oracle (dùng nhãn kiểm thử) | 72,76 | 83,60 | **không** |

5 → 22 sản phụ huấn luyện đáng **+10,24 điểm** trên quy tắc mù nhãn (Wilcoxon ghép cặp *p* = 3,5e-10; 52
thắng / 3 thua / 5 hoà; KTC bootstrap [+7,13; +13,60]). Bản ≥ 90: 27 → 33/60; bản < 50: 22 → 16. Trung vị
F1 của mô hình 22 ca là 95,07.

Quy tắc chọn kênh mất độ chính xác khi đổi hệ ghi: trong miền PSD kém oracle **0,02–1,90 điểm**; trên 60 bản
CinC sạch kém **9,32 điểm** (74,28 so với 83,60, KTC [+5,10; +14,15]) và chỉ chọn trúng kênh oracle ở
17/60 bản.

**Biến thể loại trừ khai báo trước.** Bảy bản set-a có chú thích không đáng tin (a33, a38, a47, a52, a54,
a71, a74 — Behar/Oster/Clifford, CinC 2013;40:297–300); trên 53 bản sạch còn lại PSD mù nhãn cho
**64,19 → 75,27**. Cả hai biến thể đều báo cáo; không biến thể nào chọn sau khi thấy kết quả.

#### Một quy tắc chọn kênh mù nhãn tốt hơn — báo cáo như giả thuyết, không phải kết quả đã xác nhận

Bảy quy tắc mù nhãn được so với PSD trên cùng 60 bản sạch (`analysis/CHONKENH.md`,
`analysis/dulieu_results.json → chon_kenh_60_sach`). Mạnh nhất là **`peakprob`**: chạy bộ dò trên cả bốn
kênh và giữ kênh có xác suất trung bình tại chính các đỉnh nó dò được cao nhất — không huấn luyện, không
siêu tham số.

| Quy tắc (22 ca, 60 bản sạch) | F1 TB | Δ so PSD | KTC 95 % | p Wilcoxon | p Holm (7 quy tắc) | < 50 |
|---|---:|---:|---|---:|---:|---:|
| PSD (hiện hành) | 74,28 | — | — | — | — | 16 |
| `gate` — **quy tắc kế hoạch phân tích chỉ định** | 80,72 | +6,44 | [+2,49; +11,10] | 0,010 | **0,0505 — trượt** | 12 |
| `gate4` | 81,01 | +6,72 | [+2,85; +11,18] | 0,0025 | 0,0150 | 12 |
| `rrcv` | 80,00 | +5,72 | [+1,61; +10,41] | 0,101 | 0,406 | 12 |
| **`peakprob`** — tốt nhất trong bảy, **chọn sau khi thấy dữ liệu** | **82,01** | **+7,73** | [+3,82; +12,41] | 5,6e-04 | **0,0039** | **9** |
| Kênh oracle (nhãn) | 83,60 | +9,32 | — | — | — | 8 |

`peakprob` lấy lại **82,9 %** dư địa oracle, thắng 19 / hoà 35 / thua 6 bản, không bản nào mất quá 3,90
điểm. Kiểm tra xáo nhãn (`analysis/chonkenh_leakcheck.py`) đổi 0/776 lựa chọn kênh, nên bước *chọn* là mù
nhãn.

**Các ràng buộc bắt buộc.** (1) Kế hoạch phân tích (`analysis/chonkenh_khaibao_truoc.json`) chỉ định `gate`
là quy tắc xác nhận, và `gate` **không qua được Holm** (0,0505 trên 60 bản sạch) — theo chính luật của kế
hoạch, phép thử xác nhận **đã trượt**. (2) `peakprob` chọn **sau** khi thấy kết quả CinC; cơ sở thống kê duy
nhất để báo cáo nó là hiệu ứng sống sót qua Holm trên cả họ bảy quy tắc đã khai báo. (3) Tệp kế hoạch viết
trước khi chấm quy tắc nào nhưng **sau** khi F1 từng kênh của CinC đã có trên đĩa, và không được neo git
hay đóng dấu thời gian bởi bên thứ ba, nên nghiên cứu này **không "tiền đăng ký"** và không dùng từ đó.
(4) Kết quả **chưa được lặp lại trên bộ dữ liệu thứ ba độc lập, và hiện tại không thể**: NIFEADB không phân
phối chú thích thai; NInFEA không có nhãn nhịp (tham chiếu là Doppler); tệp `.qrs` của nifecgdb đánh dấu
QRS **mẹ** (RR trung vị 0,695 s = 86 nhịp/phút); nhãn set-b của CinC 2013 chưa công bố (`analysis/XACNHAN.md`,
`xacnhan_results.json → viec2_bo_thu_ba`). (5) **Trên thang logit, vấn đề hậu kiểm không biến mất**
(`analysis/XACNHAN.md`, khai báo trước ở `analysis/xacnhan_khaibao.md`, git `ed819e3`): trên 22 chủ thể
trong miền, quy tắc đứng đầu là `gate` ở hai trong ba cách kẹp và `rrcv` ở cách thứ ba, `peakprob` xếp
3/4/6 và khoảng tin cậy chứa 0; trên 60 bản CinC sạch, đứng đầu trên logit là `gate4`. Điều dữ liệu ủng hộ
là *"chọn kênh bằng chính đầu ra mô hình tốt hơn PSD ngoài miền"*; quy tắc cụ thể nào tốt nhất tuỳ thang đo.
Vì vậy `peakprob` là **giả thuyết mạnh, chưa phải kết quả xác nhận**.

Trung vị lệch so với nhãn da đầu giữ ở 0,0 ms, nên nhãn gián tiếp của B1 không kéo mô hình. Đường cong
hiệu quả mẫu (1 → 2 → 3 ca: 91,2 → 93,4 → 97,5) chưa bão hoà.

**Ổn định theo seed.** Huấn luyện lại mô hình 22 ca với seed 1 làm F1 từng chủ thể đổi trung bình **0,28
điểm** trên 20 chủ thể chung, lớn nhất 2,81 (B2_03); ở mức chủ thể F1 kênh PSD là 97,56 (seed 0) so với
97,59 (seed 1), hiệu +0,03 [−0,18; +0,34] (`analysis/xacnhan_results.json → viec5_seed`; phân fold khác
nhau giữa hai seed nên hiệu này gồm cả phương sai phân fold). Ngưỡng từng fold kém ổn định hơn (0,50–0,80
so với 0,20–0,80). Checkpoint seed 1 **không được lưu** (`train_22.py` chỉ lưu khi `--tag` rỗng), nên
không có con số seed 1 nào ngoài miền.

### Phân rã đóng góp ba tầng

| Tầng | Δ Macro F1 (mức chủ thể) | KTC 95 % | Kết luận |
|---|---:|---|---|
| Front-end tín hiệu (chọn dải thông) | **+11,00** | không kiểm chứng lại được¹ | lớn nhất trên bộ học 300 ms; **rút** với TCN |
| Ngữ cảnh thời gian và đầu ra từng mẫu | +4,49 | [1,58; 7,43] bootstrap; [−0,29; 9,27] t ghép cặp | dương, khoảng rộng |
| Họ kiến trúc, ở ngữ cảnh cố định | +0,41 | nằm trong biên 1,0 điểm | **không phân giải được ở n = 5** |

¹ `pilot_evidence/band_ablation.json` chỉ lưu tổng hợp theo dải, nên so sánh tầng 1 không kiểm định lại được
ở mức chủ thể; `p < 0,001` từng công bố **rút vì không kiểm chứng được**.

**Mọi giá trị p trên ADFECGDB đã bị bỏ.** Với n = 5, p hai phía nhỏ nhất của Wilcoxon chính xác là 2/2⁵ =
**0,0625**; các số `1,9 × 10⁻⁶`, `5,7 × 10⁻⁶`, `0,0000` trước đây là giả lập (record × kênh × seed). Xem
[`analysis/STATS.md`](analysis/STATS.md).

### Baseline cổ điển tự cài lại (ADFECGDB, cùng giao thức, siêu tham số chỉ chọn trên r01)

| Phương pháp | 4 kênh (n=20) | Kênh PSD (n=5) | Δ so mô hình | KTC bootstrap | KTC t ghép cặp | Vững? |
|---|---:|---:|---:|---|---|---|
| Trừ mẫu + Pan–Tompkins | 78,96 ± 23,52 | 87,68 | −18,49 | [−30,60; −6,38] | **[−38,80; +1,81]** | **không — chứa 0** |
| TS-PCA + Pan–Tompkins | 91,05 ± 10,17 | 96,74 | −6,40 | [−8,09; −4,70] | [−9,10; −3,69] | có |
| Độ nhô đỉnh trên **cùng front-end** | 86,39 ± 11,14 | 92,03 | −11,06 | [−14,51; −7,80] | [−16,38; −5,73] | có |
| **FetalQRS-TCN** | **97,45 ± 4,44** | **99,21** | — | — | — | — |

Ba baseline không vững như nhau. Baseline thứ ba tách riêng phần đóng góp của mạng: cùng tín hiệu dư, thay
mạng bằng lấy đỉnh → mạng đáng **+11,06 điểm** [7,80; 14,51], 5/5 sản phụ. TS-PCA trên kênh tốt nhất đạt
96,74 — phương pháp cổ điển vẫn mạnh.

### Power-MF — chạy lại tại chỗ, và câu hỏi repo này thật sự trả lời

Power-MF (Jaeger và cs. 2024) là phương pháp **đa kênh** (4 đạo trình, hai vòng ICA), đã **chạy lại từ chính
mã MATLAB của tác giả** dưới GNU Octave, chấm bằng bộ chấm của nhóm trên cùng 22 chủ thể
(`baselines/powermf_fair_run.py`, [`baselines/BASELINES.md`](baselines/BASELINES.md)).

> **Rút lại.** So sánh Power-MF sáng 12/09/2026 — *"94,87 so với 97,61, +2,74"* và *"98,38 so với 97,33,
> −1,06"* — **bị rút toàn bộ**: đứng trên một **bản cổng chuyển hỏng** (`findpeaks` của Octave dùng ma trận
> khoảng cách O(k²), tràn bộ nhớ trên 6 bản B1 dài). **Lỗi của nhóm, không phải của phương pháp.** Giả
> thuyết `ms_minpeakdistance = 340 ms` quá sát **cũng rút** (0,00 % RR của B1_01 dưới 340 ms).
> `baselines/octave/findpeaks_mpd.m` tái lập ngữ nghĩa MATLAB, O(k), 48/48 trường hợp.

**Kiểm chứng ngoài.** Sau vá, Power-MF đạt **99,40 ± 0,51** trên B1; tác giả công bố **99,46**
(`baselines/powermf_published.json`). Lệch 0,06.

| Bộ dữ liệu | n | Power-MF, **4 kênh** | Power-MF, **1 kênh** | **RelyFetal, 1 kênh** |
|---|---:|---:|---:|---:|
| ADFECGDB | 5 | 99,01 | 92,37 | **99,40** |
| Silesia B2 (chuyển dạ) | 7 | 97,90 | 87,28 | 96,82 |
| Silesia B1 (thai kỳ) | 10 | **99,40** | 83,48 | 97,15 |
| **Toàn bộ 22 chủ thể** | 22 | **98,83** | 86,71 | 97,56 |
| CinC 2013 set-a, 60 bản sạch | 60 | chưa chạy | 55,97 | **74,28** (PSD) / 80,72 (`gate`, quy tắc kế hoạch chọn, trượt Holm) / 81,01 (`gate4`, cũng ghi trước) / 82,01 (`peakprob`, hậu kiểm) |

| So sánh (22 chủ thể, bootstrap cụm 10.000 lần) | Δ F1 | KTC 95 % | p | Cliff δ | thắng/hoà/thua |
|---|---:|---|---:|---:|---|
| RelyFetal − Power-MF (4 kênh) | −1,27 | [−3,08; +0,27] | 0,156 | 0,260 | 18/0/4 |
| RelyFetal − Power-MF (1 kênh) | **+10,85** | [+6,80; +15,40] | 4,8 × 10⁻⁷ | 0,698 | **22/0/0** |
| Power-MF (1 kênh) − Power-MF (4 kênh) | −12,12 | [−18,27; −6,90] | 1,4 × 10⁻⁶ | — | 1/0/21 |

Theo từng tập, RelyFetal − Power-MF (4 kênh): ADFECGDB **+0,39** [+0,22; +0,60], 5/0/0; Silesia B2 −1,08
[−4,04; +0,54]; Silesia B1 −2,25 [−5,55; +0,32]. **Trung vị** hiệu theo chủ thể là **+0,23**; trung bình bị
kéo âm bởi ba bản B1_07 (−12,88), B1_06 (−10,51), B2_03 (−9,77).

**Đại lượng được đo:** bỏ tách nguồn đa kênh khiến chính Power-MF mất **12,12 điểm** (98,83 → 86,71); mạng
đơn kênh lấy lại **10,85 điểm — 89,5 %** — bằng một đạo trình; **không phân biệt được với Power-MF đa
kênh** và **hơn hẳn Power-MF cùng một đạo trình** (22/22). Đây **không** phải tuyên bố "vượt trội"; Power-MF
4 kênh vẫn hơn về trung bình thô.

### Cổng từ chối trả lời và kết quả phủ định về đồng điều bền vững

Bộ phân loại "mô hình sẽ sai ở đoạn này không?" huấn luyện trên ADFECGDB (mô hình 5 ca), kiểm thử xuyên miền trên
10 bản CinC 2013 a01–a10 (600 đoạn; 4 bản a03 a04 a05 a08 nằm trong 15 bản trùng dữ liệu huấn luyện):

| Nhóm đặc trưng | AUROC | KTC 95 % | F1 ở độ phủ 80 % | F1 ở độ phủ 50 % |
|---|---:|---|---:|---:|
| Từ chối ngẫu nhiên | 0,500 | — | 62,03 | 62,14 |
| 16 đặc trưng topo (Takens + ripser, sublevel H0) | **0,566** | — | 63,40 | 64,44 |
| 12 chỉ số của cổng (6 thuần tín hiệu, 6 dựa trên đầu ra mạng) | **0,929** | [0,830; 0,982] | **69,40** | **84,51** |
| Cả 28 | 0,905 | — | 69,41 | 82,44 |
| Oracle | — | — | 74,55 | 97,81 |

0,929 phần lớn là hiệu ứng **giữa** bản ghi và tính trên mẫu có 4 bản nhiễm; AUROC **trong** bản ghi chỉ **0,721**
[0,517; 0,898], đo trên 5 bản CinC sạch có cả hai lớp đoạn (a01 a06 a07 a09 a10) khi ghép với mô hình 5 ca
(`analysis/stats_results.json → comparisons.gate_auroc_cinc.auroc_TRONG_ban_ghi`); ghép với mô hình 22 ca
đang chạy trong demo thì **chưa đo lại**. Đặc trưng
topo gần như không hơn ngẫu nhiên và không bổ sung gì. **Đóng góp topo đề xuất ban đầu đã kiểm chứng có kiểm
soát và rút lại.**

---

## Mô hình

`FetalQRS-TCN` — mạng tích chập giãn nở có kết nối dư, chuỗi sang chuỗi: **113.481** tham số, checkpoint
0,48 MB, trường tiếp nhận 379 mẫu = **1.516 ms**, độ trễ một cửa sổ 4 s **4,35 ms** trên CPU, đầu vào
2 × 1000 (tín hiệu dư sau khử mẹ + tín hiệu gốc, 250 Hz), đầu ra một logit từng mẫu (bản đồ nhiệt Gauss,
σ = 12 ms).

```
aECG 1 kênh @ 1000 Hz
   ↓  Butterworth 10–60 Hz zero-phase + notch 50 Hz → 250 Hz
   ↓  dò QRS mẹ (8–25 Hz, RR ≥ 350 ms) → khử bằng mẫu trung vị, co giãn LS từng nhịp
   ↓  đoạn 4 s, 2 × 1000
   ↓  FetalQRS-TCN — stem Conv1d(k=7) + 5 khối dư, giãn nở 1,2,4,8,16
   ↓  bản đồ nhiệt từng mẫu → lấy đỉnh, ngưỡng τ + khoảng trơ 250 ms
   ↓  cổng tin cậy (độ tự tin mô hình, hợp lý RR, tỉ số dải, kiểm tra bám nhịp mẹ)
vị trí nhịp thai + nhịp tim thai + mức tin cậy
```

CNN giãn nở được giữ vì **hiệu quả tham số**, không phải vì họ kiến trúc ưu việt.

---

## Demo

```bash
python demo/app.py        # máy chủ FastAPI: /gradio/ chế độ trình bày · / trang nghiên cứu · /monitor
```

Mở **http://127.0.0.1:7860/gradio/**. Từ lần ghép 17/09, `demo/app.py` chạy máy chủ FastAPI: `/` là trang nghiên cứu HTML
của Khánh (bố cục 8 tab), `/monitor` là trang theo dõi tín hiệu, `/gradio/` là giao diện Gradio mô tả dưới đây.

Ở `/gradio/` mặc định mở **chế độ trình bày** (thẻ `r01` `a09` `a02` `a27` và thẻ *Tệp của bạn*, đi theo 5 bước). **Tám tab**
cũ nằm trong *Chế độ chuyên gia* (tắt sẵn): năm tầng tín hiệu, chọn kênh mù nhãn trên cả 4 kênh (`peakprob` hoặc PSD), đồ thị nhịp
tim thai kèm đèn từng đoạn, so sánh với nhãn, tổng hợp 60 bản sạch, **Dữ liệu của nhóm** (bảng mọi bản ghi của
5 bộ đọc thật từ header `.hea`/`.edf`, kèm nút xem tín hiệu thô có vạch nhãn), **Tải dữ liệu mới** (`.edf`,
`.dat`+`.hea`, `.csv`, `.npy`, `.txt`, nhãn tuỳ chọn, sáu lỗi đầu vào trả thông báo tiếng Việt), và nhật ký
JSON. Bắt buộc **Gradio 6.x**. Hướng dẫn vận hành: [`docs/HUONG_DAN_DEMO_v2.md`](docs/HUONG_DAN_DEMO_v2.md)
(bản 8 tab cũ: `docs/HUONG_DAN_DEMO_v1.md`).
**Đèn tin cậy** hai chế độ — *học* (GBM trên 12 chỉ số từng đoạn 4 s, `fsqi/gate.py` + `fsqi/gate_classical.pkl`,
mặc định) và *luật*. 12 chỉ số **không** thuần cổ điển: 6 thuần tín hiệu (`sampen`, `kurtosis`, `spec_entropy`,
`band_ratio`, `psd_fhr`, `tau_acf`), 4 tính trên nhịp mạng dò ra (`n_det`, `rr_cv`, `rr_plaus`, `bsqi`), 2 là
xác suất của mạng (`peak_prob_mean`, `prob_max`). Độ quan trọng hoán vị của cổng 22 ca: `rr_cv` 0,140,
`peak_prob_mean` 0,032, 10 chỉ số còn lại < 0,002 (`analysis/gate22_results.json →
cong.permutation_importance_delta_auroc`) — **cổng không độc lập với mạng**.

Hai chế độ đèn chạy lại 12/09/2026 (17:07; chạy lại lúc 23:11 cho tóm tắt giống hệt) trên 82 bản có nhãn không trùng huấn luyện và không rò rỉ
(5 ADFECGDB với fold checkpoint, 60 CinC sạch, 17 Silesia; `python demo/run_check.py --threads 2` →
`demo/results/demo_check_2modes.json`, `summary_by_mode`):

| Chế độ | Xanh (n · F1 TB · min) | Vàng (n · F1 TB) | Đỏ (n · F1 TB) | Xanh nhưng F1 < 90 | Đỏ nhưng F1 ≥ 95 |
|---|---|---|---|---|---|
| học (mặc định) | 46 · 95,70 · 17,02 | 17 · 96,94 | 19 · 54,26 | 3 (a52, a54, a57) | 0 |
| luật | 58 · 97,79 · 78,79 | 19 · 63,82 | 5 · 39,34 | 5 (a06, a11, a16, B1_07, B2_03) | 0 |

Bảng cũ (8 xanh / 5 vàng / 2 đỏ) tính trên 15 bản mẫu, 4 trong đó là bản CinC rò rỉ — đã thay. Cổng học
hiệu chuẩn theo mô hình 5 ca; cổng 22 ca ở `analysis/GATE22.md` chưa xuất vào demo (AUROC trong bản ghi của nó,
0,934 [0,872; 0,981], tính trên 11/22 chủ thể có đoạn xấu, chỉ ở dạng phân tích).

> Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.

## API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000          # hoặc: docker compose up --build
```

FastAPI bọc `demo/core.py`: `GET /health`, `GET /model`, `POST /analyze` (EDF/CSV/TXT/NPY → `n_beats`,
`fhr_mean`, `beats_ms`, `confidence{level,score,reasons}`, `latency_ms`, thêm `metrics` nếu gửi nhãn).
Lược đồ trong [`api/README.md`](api/README.md); kiểm thử `tests/test_api.py`.

---

## Cấu trúc kho mã (sau đợt bàn giao 15/09/2026)

```
HANDOFF.md                Đọc trước: cài đặt, dữ liệu, bản đồ kho mã, quy tắc liêm chính, bẫy, việc tiếp theo
CHANGELOG.md              Thay đổi theo từng vòng và mọi tuyên bố đã rút
requirements.txt          Gói lõi: pipeline, demo, API, kiểm thử (ghi phiên bản đã kiểm)
requirements-research.txt Gói cho thí nghiệm phân tích, dựng tài liệu, chụp ảnh demo

model/                    Thư viện lõi, huấn luyện, suy luận, 20 checkpoint (5 / 12 / 22 ca + production)
benchmark_dpss/           Bộ đối chuẩn: full_measure, blind_lead, silesia_eval, eval_22, eval_cinc75, eval_cinc60_sach
baselines/                TS / TS-PCA / độ nhô; Power-MF 4 kênh (Octave) và 1 kênh; BASELINES.md
fsqi/                     Chỉ số chất lượng tín hiệu (C3): kết quả phủ định về topo, cổng 12 chỉ số (6 dựa trên đầu ra mạng)
demo/                     Gradio: chế độ trình bày 5 bước + 8 tab chuyên gia (core.py không phụ thuộc UI, 66 kiểm thử trong test_core.py; run_check.py chấm 82 bản; ảnh chụp thật trong screenshots/)
api/                      FastAPI (main.py), lược đồ trong api/README.md
pilot_evidence/           Thí nghiệm tiền khả thi kèm nhật ký (dải lọc, kiến trúc, trường tiếp nhận, band_tcn)
adapt/                    Thích nghi miền không nhãn — bốn phương pháp, đều thất bại (adapt_results.json)
analysis/                 DULIEU.md (15 bản trùng), CHONKENH.md (7 quy tắc), XACNHAN.md (vòng 7), KIENTRUC.md,
                          STATS.md, CLINICAL.md, THICHNGHI.md, CHANDOAN_MOHINH.md (đã rút kết luận), dulieu_results.json
survey/                   Khảo sát 30 công trình; RO_RI_VANLIEU.md (ai đã ghi nhận chồng lấn); facts_phase4.json (nguồn số duy nhất)
de_cuong_latex/           Đề cương v3.5 — LaTeX (xelatex), 148 trang
paper/cinc2026/           Bản thảo Computing in Cardiology 4 trang (pdflatex + bibtex), CHANGELOG.md
docs/                     PDF/DOCX đã biên dịch; DE_CUONG_HIEN_TRANG.md, KICH_BAN_HANH_TRINH.md, HUONG_DAN_DEMO_v2.md (v1 lưu trữ),
                          CHIEN_LUOC_CONG_BO.md, EUREKA.md, KICH_BAN_TRINH_BAY.md, TOM_TAT_1_TRANG.md
docs/trinh_bay/           Slide 31 trang (phím N ghi chú, O tổng quan) và sổ tay đề tài — HTML mở bằng trình duyệt
docs/nhat_ky/             Biên bản 7 vòng thẩm định phản biện
archive/                  Script vá một lần đã rút khỏi cây làm việc (kèm README)
tests/                    Kiểm thử ghim số tham số, trường tiếp nhận, API (43; cộng 66 trong demo/test_core.py = 109, đếm 17/09/2026)
```

---

## Cài đặt và chạy

```bash
git clone https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027.git
cd nckhsv_tdtu2026-2027
python -m venv .venv && .venv\Scripts\activate     # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt                       # thêm requirements-research.txt nếu chạy phân tích, dựng tài liệu
python model/download_data.py --root model/data --only adfecgdb    # ~15 MB từ PhysioNet
python model/download_more.py --only cinc75                        # ~35 MB, CinC 2013 set-a -> benchmark_dpss/pcdb/
python model/download_silesia.py                                   # ~195 MB .zip -- PHẢI giải nén tay, xem HANDOFF.md mục 4
python model/predict.py --input model/data/adfecgdb/r01.edf --lead 1 --annot qrs \
                        --checkpoint model/checkpoints/fetalqrs_tcn_fold_r01.pt
```

Chạy lại toàn bộ (thứ tự trong `README.md`, mục *Reproducing every number*); riêng số CinC:
`python benchmark_dpss/eval_cinc75.py && python benchmark_dpss/eval_cinc60_sach.py`, kiểm toán trùng:
`python analysis/dulieu_audit.py && python analysis/dulieu_m4b_verify.py`, kiểm thử:
`pytest tests/ demo/test_core.py` (109 kiểm thử tại 17/09/2026; bản ghi chưa tải sẽ *skipped* chứ không *failed*).

---

## Dữ liệu

Không phân phối lại bản ghi sinh lý nào. ADFECGDB (PhysioNet, ODC-BY 1.0) — huấn luyện, đánh giá tách bản
ghi; Silesia B1/B2 (Matonia 2020, figshare, CC0) — zero-shot; CinC 2013 set-a (PhysioNet, ODC-BY 1.0) —
hệ ghi khác, **60 bản sạch**. Silesia B1 không có điện cực da đầu; nhãn gián tiếp, lệch 8–12 ms ở 5/10 bản.

---

## Hạn chế còn tồn tại

- **22 sản phụ từ một bệnh viện, một hệ ghi.** Trên hệ ghi khác (CinC 2013, 60 bản sạch) mô hình 22 ca đạt
  **74,28 theo PSD mù nhãn** (80,72 theo `gate` — quy tắc kế hoạch chọn, trượt Holm; 82,01 theo `peakprob`
  hậu kiểm) so với 97–99 trong miền; khoảng cách so với 97,56 trong miền là 23,28 điểm theo PSD. Bốn phương pháp thích
  nghi miền không nhãn **đều thất bại** (notch thích nghi +0,25, p = 0,68; self-training −0,67; AdaBN −1,58;
  TENT −2,43; `analysis/THICHNGHI.md`).
- **Cỡ mẫu là ràng buộc chặt nhất.** Không so sánh nào trên ADFECGDB có ý nghĩa thống kê ở mức chủ thể.
- **CinC 2013 chấm trên 60 bản sạch (53 theo loại trừ khai báo), không phải 75**; chưa kiểm 60 bản có từ 60
  sản phụ khác nhau không (NCC ≤ 0,62 chỉ loại bản sao nguyên văn). Bộ chấm ±50 ms của nhóm, không phải bộ
  chấm chính thức.
- **Kết luận "mô hình không phải nút thắt" (`analysis/CHANDOAN_MOHINH.md`) đã rút**, cùng với "71 % dư địa
  nằm trên bản không có tín hiệu": phép thử nhìn thấy có **âm tính giả 18,0 % [12,1; 25,0]** trên 60 bản sạch
  (ngưỡng khai báo 10 %), 55–70 % trên bản F1 < 90; sau hiệu chỉnh tỉ lệ dư địa "thiếu tín hiệu" từ 86,0 %
  xuống 26,0 % nhưng con số hiệu chỉnh không định danh được. Phát biểu đúng: *chưa chứng minh được mô hình là
  hay không là nút thắt* (`analysis/XACNHAN.md`).
- **Chưa có bộ dữ liệu thứ ba có nhãn fQRS thật** để xác nhận `peakprob` (xem ràng buộc (4) ở trên).
- **Cổng tin cậy học hiệu chuẩn theo mô hình 5 ca**, quá thận trọng trên thai kỳ; chưa hiệu chuẩn lại cho 22 ca.
- **Bảng kiến trúc một seed, ba epoch.** **Đèn luật trong demo là luật đặt tay.**
- **Power-MF 4 kênh chưa chạy trên CinC 2013**; bản 1 kênh là cài lại của nhóm theo mô tả đã công bố.
- **+11,00 điểm dải thông đo trên GBM 300 ms, rút với TCN** (+2,44 [−0,04; +6,29] trên kênh PSD; −0,07
  [−0,51; +0,39] trung bình 4 kênh; `pilot_evidence/band_tcn_stats.json`).
- **Nhánh 22 ca trong miền ở trần F1** (14/22 chủ thể ở kênh oracle), nên so sánh ở đó phải đọc trên thang
  logit (`analysis/KIENTRUC.md`).
- **Chỉ số chất lượng topo không hoạt động** (AUROC 0,566 so với 0,929, cùng mẫu a01–a10 có 4 bản nhiễm) — kết quả phủ định.
- **Cổng tin cậy không độc lập với mạng**: 6/12 chỉ số dựa trên đầu ra mạng; `rr_cv` và `peak_prob_mean` gánh gần
  hết độ quan trọng hoán vị.
- **Nơi công bố:** *Physiological Measurement* là **Q2/Q3 Scimago 2024, không phải Q1** như đề cương v3.4 ghi;
  Q1 (JBHI, TBME, BSPC, CBM, AI in Medicine) cần bộ dữ liệu thứ ba (`docs/CHIEN_LUOC_CONG_BO.md`).

---

## Điều gì đã được kiểm chứng, điều gì chưa

| Tuyên bố | Trạng thái | Bằng chứng |
|---|---|---|
| F1 trong miền (ADFECGDB 99,40; B2 96,82; B1 97,15) | **Đo lại được trong repo** | `benchmark_dpss/eval_22.json` |
| Không rò rỉ giữa 5 bản PhysioNet và Silesia B2 | **Đã kiểm** | NCC 0,988–0,994; chấm bằng fold chưa thấy |
| CinC 2013 = 74,28 (PSD) trên 60 bản sạch | **Đo lại được trong repo** | `benchmark_dpss/eval_cinc60_sach.json` |
| Set-a chứa bản ghi ADFECGDB | **Ban tổ chức đã ghi nhận, không phải nhóm** | Silva 2013 Bảng 1; Clifford 2014 Bảng 2 + cảnh báo Rodrigues; Su & Wu 2017; Matonia 2020 (`survey/RO_RI_VANLIEU.md`) |
| *Đúng 15/75 bản nào* là bản sao và mức thổi phồng | **Nhóm đo, kiểm hai lần** | NCC = 1,0000 4/4 kênh, lệch RR 0,0 ms; hai cài đặt độc lập; thổi phồng 3,27–7,18 điểm |
| `peakprob` +7,73 so PSD | **Giả thuyết — hậu kiểm, chưa lặp lại** | sống sót Holm (0,0039); `gate` chỉ định trượt (0,0505); trên logit `gate` dẫn 22 ca, `gate4` dẫn 60 bản (`analysis/XACNHAN.md`) |
| "Mô hình không phải nút thắt" | **KHÔNG xác định được** | phép thử nhìn thấy âm tính giả 18,0 %; 26 % so 86 % không định danh |
| Thích nghi miền không nhãn giúp trên CinC | **KHÔNG — bốn phương pháp đều âm** | `analysis/THICHNGHI.md`, `adapt/adapt_results.json` |
| Họ kiến trúc quan trọng ở cùng tham số | **KHÔNG (trong miền, giao thức rút gọn)** | `analysis/KIENTRUC.md` |
| Bản cổng chuyển Power-MF đúng | **Kiểm chứng NGOÀI** | 99,40 so với 99,46 tác giả công bố |
| Thêm dữ liệu giúp thật | **Bằng chứng độc lập** | m12 (chưa thấy B1) 67,93 so m22 74,28 trên 60 bản sạch (`analysis/ABLATION_B1.md`) |
| +11,00 điểm dải thông | **RÚT với TCN** | +2,44 [−0,04; +6,29] (`pilot_evidence/band_tcn_stats.json`) |
| Jitter/STV trên Silesia B1 | **KHÔNG dùng được** | nhãn gián tiếp, lệch phụ thuộc mô hình |
| Máy đo STV độc lập | **KHÔNG** | chỉ có số dùng được trong miền: chệch +0,33 ms trên ADFECGDB, n = 5 (`analysis/CLINICAL.md`); số STV ngoài miền đo trên mẫu có a03 a04 a05 a08 (bản trùng) — không dùng |
| "8 kiến trúc không phân biệt được" | **ĐÃ RÚT** | TOST biên 1,0 (`analysis/STATS.md`) |
| Đóng góp topo (C3) | **ĐÃ RÚT — phủ định** | AUROC 0,566 so 0,929 (`fsqi/README.md`) |
| Điểm so được với bảng CinC 2013 | **KHÔNG** | bộ chấm riêng |
| Ổn định seed | **Chỉ 2 seed, trong miền** | +0,03 [−0,18; +0,34]; checkpoint seed 1 không lưu |
| Lặp lại `peakprob` trên bộ thứ ba | **KHÔNG THỂ với dữ liệu hiện có** | không bộ công khai nào có nhãn fQRS thật (`analysis/XACNHAN.md`) |
| Trung tâm thứ hai có nhãn fQRS thật | **CHƯA có** | — |

---

## Rút lại — danh sách đầy đủ

| Đã rút | Từng đứng ở | Vì sao | Thay bằng |
|---|---|---|---|
| 59,15 / 69,31 / 77,34 / 90,34 / 22,33 | CinC 2013, mẫu 10 bản | mẫu lệch, kênh hậu kiểm; 4/10 bản là dữ liệu huấn luyện | 60 bản sạch |
| 71,21 / 79,40 / 86,87 / 74,09 / 69,33 / +8,18 / +7,47 / 80,70 | CinC 2013, đủ 75 bản | 15 bản là bản sao ADFECGDB; vi phạm độc lập mức bản ghi | 64,04 / **74,28** / 83,60 / 67,69 / +10,24 / +9,32 / 75,27 — `eval_cinc60_sach.json` |
| 85,60 / +6,20 / +5,14 (`peakprob`, `gate` trên 75 bản) | `analysis/CHONKENH.md` | cùng ô nhiễm | 82,01 / +7,73 / +6,44 trên 60 bản sạch |
| 62,82 (Power-MF 1 kênh trên CinC) | bảng Power-MF | cùng ô nhiễm | 55,97 |
| 94,87 / +2,74 / 98,38 / 97,33 | Power-MF, sáng 12/09/2026 | cổng chuyển Octave hỏng | 98,83 / −1,27 [−3,08; +0,27] |
| "+11,00 F1 từ dải lọc" như phát biểu về mô hình | README cũ | đo trên GBM 300 ms; trên TCN +2,44, khoảng chứa 0 | chỉ báo cáo cho bộ học 300 ms |
| "tám kiến trúc không phân biệt được" | README cũ | tương đương suy từ p > 0,05 | TOST; `cnn_wide` kém trên logit |
| "bài toán lưỡng cực" như cơ chế | README cũ | hai đỉnh là hệ quả chọn kênh (`analysis/LUONGCUC.md`) | mô tả, không kết luận |
| "tiền đăng ký" cho nghiên cứu quy tắc chọn kênh | `analysis/CHONKENH.md` | kế hoạch không neo git, viết sau khi có F1 từng kênh | "kế hoạch viết trước khi chấm quy tắc" |
| "mô hình không phải nút thắt"; "71 % dư địa không có tín hiệu"; "chỉ 1,85 điểm thuộc mô hình" | `analysis/CHANDOAN_MOHINH.md`, `THICHNGHI.md` | phép thử nhìn thấy âm tính giả 18,0 % (ngưỡng 10 %), 55–70 % trên bản khó | "chưa chứng minh được là hay không là"; phần dư địa không xác định (26–86 % là hai biên) — `analysis/XACNHAN.md` |
| "AUROC 0,980 / độ phủ 66,7 % / loại 15/16 bản" như số chính của cổng | `analysis/GATE22.md`, `docs/*` | tính trên đủ 75 bản CinC, 15 bản là bản sao ADFECGDB; chưa tính lại trên 60 bản sạch | AUROC trong bản ghi 0,934 [0,872; 0,981] trên 11/22 chủ thể có đoạn xấu (LOSO 22 ca; chỉ ở dạng phân tích, chưa đưa vào demo), 3 bản khó xếp đúng 1-2-3 — `analysis/gate22_results.json`; số 75 bản chỉ được nhắc kèm cảnh báo |
| "khoảng cách trong/ngoài miền 17,92 điểm" | `analysis/THICHNGHI.md`, `docs/*` | tính từ mốc 79,40 trên 75 bản nhiễm (`adapt/adapt_analyze.py` dòng 15 và 76) | 97,56 trừ số 60 bản sạch: 23,28 (PSD) · 16,84 (`gate`) · 16,55 (`gate4`) · 15,55 (`peakprob`) · 13,96 (trần) |
| STV ngoài miền: +20,50 ms; 0,13 ms; 25,74–25,78 ms | `analysis/CLINICAL.md`, `docs/*` | mẫu CinC 10 bản / mẫu 32 bản có a03 a04 a05 a08 (bản trùng) | chỉ +0,33 ms trong miền, n = 5 |
| "cổng dùng 12 chỉ số cổ điển, không lấy từ mạng" | README cũ, `docs/*` | 2/12 là xác suất mạng, 4/12 tính trên nhịp mạng dò | "12 chỉ số, 6 dựa trên đầu ra mạng; cổng không độc lập với mạng" — `fsqi/gate.py`, `analysis/gate22_results.json` |
| CinC 2026 là nơi nộp | `paper/cinc2026/`, `docs/` cũ | CinC 2026 (Madrid, 20–23/9/2026) đã qua; giữ tên thư mục để truy vết | CinC 2027 (abstract dự kiến 4/2027) — `docs/CHIEN_LUOC_CONG_BO.md` |
| "8 bản giới hạn cứng" | `analysis/CHANDOAN_MOHINH.md` | định nghĩa vòng tròn; a54 là lỗi nhãn | chỉ mô tả |
| **"nhóm phát hiện rò rỉ" — chồng lấn set-a ↔ ADFECGDB như phát hiện của nhóm** | README cũ, `analysis/DULIEU.md` §12, `docs/*` | ban tổ chức ghi nhận 2013/2014; cảnh báo nằm trong ghi chú đọc bài của nhóm (p20) | "như ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014] … chúng tôi xác định bằng đo lường đúng 15 bản và mức thổi phồng" — `survey/RO_RI_VANLIEU.md` |
| "lặp lại `peakprob` trên set-b / NInFEA / NIFEADB" như kế hoạch | README cũ, `docs/CHIEN_LUOC_CONG_BO.md` | không bộ nào có nhãn fQRS thật | không có bộ thứ ba; quy tắc vẫn là giả thuyết |
| "hai seed cho thấy ổn định" ngoài phạm vi trong miền | README cũ | checkpoint seed 1 không được lưu | chỉ trong miền: +0,03 [−0,18; +0,34] |
| p < 0,001 cho tầng dải lọc; mọi p trên ADFECGDB | README cũ | giả lập record × kênh × seed | chỉ khoảng tin cậy (`analysis/STATS.md`) |
| đóng góp chỉ số topo | đề cương v1 | AUROC 0,566 so 0,929 | kết quả phủ định |
| *Physiological Measurement* là tạp chí Q1 | đề cương v3.4, `docs/` | Scimago 2024: Q2 (Physiology) / Q3 (Biomedical Eng.) | Q1: JBHI, TBME, BSPC, CBM, AI in Medicine — `docs/CHIEN_LUOC_CONG_BO.md` |

Nguồn số hiện hành duy nhất: [`survey/facts_phase4.json`](survey/facts_phase4.json); mỗi mục ghi tệp JSON
nó được đọc từ.

---

## Trích dẫn và giấy phép

Xem [`CITATION.cff`](CITATION.cff) (v3.5, 12/09/2026). Mã nguồn **MIT**; tài liệu, hình vẽ và trọng số
**CC BY 4.0**; dữ liệu sinh lý và công trình bên thứ ba **không** phân phối lại — [`LICENSE`](LICENSE).

> **Không phải thiết bị y tế.** Bản mẫu nghiên cứu, chưa thẩm định lâm sàng, không có chứng nhận quản lý.
