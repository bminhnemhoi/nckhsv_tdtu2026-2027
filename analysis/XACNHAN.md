# R2 — XÁC NHẬN: bộ thứ ba, 22 chủ thể trên logit, phép thử nhìn thấy, hạt giống

Khai báo trước: `analysis/xacnhan_khaibao.md`, git **ed819e3** (2026-09-12 16:25 +07), cam kết TRƯỚC khi chạy.
Chạy một lần: `python analysis/xacnhan.py` → `xacnhan_results.json`, `fig_xacnhan.png`, `xacnhan_log.txt`.
Không huấn luyện, không suy luận mới; chỉ đọc kết quả đã lưu (chonkenh_results.json, chonkenh_cache/,
chandoan_raw.json, chandoan_events.npz, chandoan_cache.npz, train_22.json, train_22_seed1.json).
Mọi con số dưới đây nằm trong `xacnhan_results.json` (khoá ghi trong ngoặc).

## Tóm tắt một đoạn
1. **Không có bộ thứ ba có nhãn fQRS thật** (`viec2_bo_thu_ba`). NIFEADB không phân phối chú thích; NInFEA
   không có nhãn nhịp; bản thăm dò nifecgdb `ecgca102.edf.qrs` là nhãn QRS **mẹ** (86 nhịp/phút). Việc xác
   nhận peakprob trên bộ thứ ba **chưa thể thực hiện**.
2. **Trên logit, 22 chủ thể vẫn do `gate` đứng đầu** (kẹp A, B) hoặc `rrcv` (kẹp C); peakprob xếp 3/4/6.
   **Vấn đề hậu kiểm KHÔNG biến mất** (`viec3_logit_22.van_de_hau_kiem_bien_mat = false`).
3. **Phép thử nhìn thấy có tỉ lệ âm tính giả 18,0 % [12,1; 25,0] trên 60 bản CinC sạch** (kênh PSD), vượt
   ngưỡng 10 % đã khai báo; trên bản khó tỉ lệ này là 55–70 %, tức phép thử **gần như vô dụng đúng ở nơi
   cần nó**. Con số "71 % dư địa nằm trên bản không có tín hiệu" **phải rút**; sau hiệu chỉnh còn 26 % (ngưỡng
   0,5) nhưng con số hiệu chỉnh cũng **không định danh được** — kết luận đúng là *không xác định được*.
4. Seed 1 vs seed 0 ở mức chủ thể: F1 PSD 97,59 vs 97,56, hiệu +0,03 [−0,18; +0,34] → ổn định. Checkpoint
   seed 1 **không được lưu**, nên peakprob với seed 1 là bất khả thi trong R2.

---

## VIỆC 2 — Bộ dữ liệu thứ ba (`viec2_bo_thu_ba`)

| Bộ | Trên đĩa | Nhãn fQRS thật? | Bằng chứng (fact) |
|---|---|---|---|
| NIFEADB (Behar 2019) | 26 bản .dat/.hea | **Không** | thư mục PhysioNet 1.0.0 không có .qrs/.atr/ANNOTATORS; `model/nifeadb_loader.py` đặt `HAS_FETAL_ANNOTATIONS=False` (ghi chú trong `download_more.py` nói "có chú thích fQRS" là **sai**, loader đã sửa) |
| NInFEA (Sulas 2021) | 2 .dat + 3 .hea, tải dở | **Không** | không tệp chú thích nhịp; tham chiếu gốc là Doppler PWD |
| nifecgdb (ecgca102) | 1 EDF + .qrs | **Không** (nhãn mẹ) | 375 nhãn / 270 s, RR trung vị 0,695 s = 86 nhịp/phút; trang PhysioNet không mô tả nội dung .qrs, nhưng tần số này là nhịp mẹ; 55 bản từ **một** sản phụ |
| CinC 2013 set-b | không | **Không** | nhãn không công bố |

**Phát biểu:** peakprob (+7,73 điểm trên 60 bản sạch) vẫn là **giả thuyết mạnh, chưa được xác nhận**. Bộ thử
thứ ba có nhãn thật hiện chưa tồn tại trong tầm tay nhóm; muốn có phải tự chú thích (cần chuyên gia) hoặc
xin dữ liệu ngoài.

## VIỆC 3 — 22 chủ thể trên thang logit (`viec3_logit_22`)

Biến đổi y = logit(F1/100); kẹp F1 = 100 theo ba cách: **A** (chính) p′ = (p·n+0,5)/(n+1) với n = số nhịp tham
chiếu của chủ thể (`n_ref`, 145–3 114); **B** trần 0,999; **C** trần 0,995. Bootstrap theo chủ thể 10 000 lần,
Wilcoxon ghép cặp, Holm trên 7 quy tắc mới.

### Bảng xếp hạng 7 quy tắc mới (`ket_qua_theo_kep.*.xep_hang_7_quy_tac_moi`)

| Kẹp | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| F1 thô (vòng trước) | gate | rrcv | gate4 | rrplaus | fuse | **peakprob** | learned |
| A (Laplace theo n) | **gate** | rrcv | peakprob | gate4 | rrplaus | learned | fuse |
| B (trần 99,9) | **gate** | rrcv | gate4 | peakprob | rrplaus | fuse | learned |
| C (trần 99,5) | **rrcv** | rrplaus | gate | gate4 | fuse | peakprob | learned |

### Kẹp A — hiệu so với psd trên logit (`ket_qua_theo_kep.A.bang`)

| Quy tắc | logit TB | F1 tương ứng | hiệu vs psd | KTC95 | p Wilcoxon | p Holm | thắng/hoà/thua |
|---|---|---|---|---|---|---|---|
| psd | 5,545 | 99,61 | 0 | — | — | — | — |
| gate | 5,770 | 99,69 | +0,225 | [+0,004; +0,589] | 0,068 | 0,475 | 4/18/0 |
| rrcv | 5,685 | 99,66 | +0,140 | [−0,188; +0,547] | 0,401 | 1 | 6/14/2 |
| peakprob | 5,679 | 99,66 | +0,134 | [−0,038; +0,407] | 0,176 | 1 | 6/15/1 |
| gate4 | 5,661 | 99,65 | +0,116 | [−0,176; +0,514] | 0,917 | 1 | 3/16/3 |
| rrplaus | 5,589 | 99,63 | +0,043 | [−0,326; +0,472] | 0,959 | 1 | 6/12/4 |
| learned | 5,559 | 99,62 | +0,014 | [−0,229; +0,326] | 0,575 | 1 | 5/12/5 |
| fuse | 5,532 | 99,61 | −0,013 | [−0,345; +0,394] | 0,463 | 1 | 4/9/9 |
| mean4 | 4,446 | 98,84 | −1,099 | [−1,544; −0,663] | 5,4e-04 | — | 3/1/18 |
| oracle | 5,836 | 99,71 | +0,291 | [+0,060; +0,654] | 0,012 | — | 8/14/0 |

**Trả lời câu hỏi then chốt:** trên logit, quy tắc đứng đầu là **gate** (kẹp A, B) — đúng quy tắc mà luật
quyết định ghi trước đã chỉ. Kẹp C đảo sang rrcv, nên thứ hạng **phụ thuộc cách kẹp** ở nhóm 3 quy tắc đầu.
peakprob **không** đứng đầu theo bất kỳ cách kẹp nào và KTC95 (peakprob − psd) chứa 0 ở kẹp A, B. Theo điều
kiện đã khai báo (đứng đầu cả ba kẹp **và** KTC không chứa 0), **vấn đề hậu kiểm không biến mất**.
Không quy tắc nào sống sót qua Holm trên 22 chủ thể; KTC của gate chạm 0 (+0,004) — mong manh.

### Phụ: 60 bản CinC sạch trên logit (`cinc60_phu`, chỉ mô tả, không quyết định)

| Kẹp | Đứng đầu | gate4 hiệu [KTC] p Holm | peakprob hiệu [KTC] p Holm | gate hiệu [KTC] p Holm |
|---|---|---|---|---|
| A | **gate4** | +0,487 [+0,222; +0,802] 0,010 | +0,461 [+0,195; +0,765] 0,016 | +0,445 [+0,172; +0,765] 0,045 |
| B | **gate4** | +0,542 [+0,244; +0,894] 0,012 | +0,487 [+0,180; +0,831] 0,021 | +0,487 [+0,177; +0,845] 0,063 |
| C | **gate4** | +0,482 [+0,219; +0,797] 0,009 | +0,458 [+0,199; +0,754] 0,009 | +0,449 [+0,180; +0,768] 0,029 |

Trên logit ngoài miền, **gate4 vượt peakprob** và cả ba quy tắc mô-hình-đánh-giá-kênh (gate4, peakprob, gate)
đều vượt psd qua Holm (gate trượt nhẹ ở kẹp B, 0,063). Phát biểu ổn định nhất mà dữ liệu ủng hộ: *"chọn kênh
bằng chính đầu ra mô hình (cổng hoặc xác suất đỉnh) tốt hơn PSD ngoài miền"*, còn **quy tắc cụ thể nào tốt
nhất thì phụ thuộc thang đo** (F1 thô: peakprob; logit: gate4). Đây là lập luận mạnh hơn cho việc cần bộ
thứ ba.

## VIỆC 4 — Tỉ lệ âm tính giả của phép thử nhìn thấy (`viec4_phep_thu_nhin_thay`)

Định nghĩa: âm tính giả = nhịp **TP** (mô hình bắt đúng trong ±50 ms) mà phép thử bảo "không nhìn thấy"
(z < τ). Tái lập số gộp vòng trước: độ nhạy 0,951 (22) / 0,862 (CinC 75) khớp đến 3 chữ số
(`kiem_tai_lap_do_nhay_vong_truoc`).

### (a) Tỉ lệ âm tính giả (`ti_le_am_tinh_gia`)

| Tập, kênh | n TP | âm tính giả micro [KTC95 theo bản] | trung vị theo bản | p90 | bản > 10 % | F1 ≥ 90 | 50 ≤ F1 < 90 | F1 < 50 |
|---|---|---|---|---|---|---|---|---|
| 22 chủ thể, PSD | 35 307 | **4,9 %** [0,5; 10,4] | 0,2 % | 23,8 % | 3/22 | 0,5 % (19) | 27,2 % (3) | — (0) |
| 22 chủ thể, oracle | 35 932 | 1,5 % [0,4; 3,1] | 0,4 % | 3,0 % | 1/22 | 1,1 % | 28,0 % | — |
| 60 CinC sạch, PSD | 6 365 | **18,0 %** [12,1; 25,0] | 20,9 % | 75,9 % | 31/60 | 3,1 % (33) | **55,2 %** (11) | **69,6 %** (16) |
| 60 CinC sạch, oracle | 7 161 | 16,4 % [11,2; 22,7] | 3,9 % | 64,9 % | 29/60 | 3,9 % (38) | 50,9 % (14) | 69,3 % (8) |

Ngưỡng khai báo 10 % **bị vượt** trên 60 bản sạch. Điều quan trọng hơn con số gộp: trên các bản có F1 < 90 —
chính những bản mang gần hết dư địa — phép thử gán "không nhìn thấy" cho **55–70 % nhịp mà mô hình đã bắt
đúng**. Ở đó phép thử không còn phân biệt "không có tín hiệu" với "có tín hiệu nhưng yếu".

### (b) Độ đặc hiệu ngoài mẫu (3 bản khó trong miền có phần dư lưu sẵn, `do_dac_hieu_ngoai_mau_3_ban`)
- τ tính lại khớp τ đã lưu ở 12/12 kênh.
- Vị trí an toàn **mới** (không dùng để đặt τ): tỉ lệ z ≥ τ trung vị 5,4 %, cao nhất 6,7 % → τ không quá khớp.
- Điểm giữa hai nhãn thai: 4,8 % (cao nhất 6,3 %) → nhất quán với 5 %.
- Tại đỉnh mẹ (cách nhãn thai ≥ 120 ms): **37,9 %** trung vị, cao nhất 83,5 % → phần dư mẹ kích hoạt phép thử;
  vòng trước đã chặn bằng lớp c_me (±60 ms) trước khi hỏi a/b nên không lọt vào (a)/(b), nhưng cho thấy z không
  đặc hiệu với tín hiệu thai.
Chỉ 3 bản trong miền; không suy rộng sang CinC.

### (c) Chia dư địa trên 60 bản sạch (`du_dia_60_sach`)
Dư địa = (100 − F1 oracle)/60 mỗi bản, tổng **16,40 điểm** (trước đây 6,36 trên 67 bản có rò rỉ và đã bỏ 8 bản
"giới hạn cứng" — nhóm đó đã bị phản biện loại vì vòng lặp định nghĩa nên ở đây không bỏ).

| Ngưỡng nhìn thấy | tỉ lệ THÔ: n bản, điểm, % | HIỆU CHỈNH v′ = (v−0,05)/(s−0,05): n bản, điểm, % |
|---|---|---|
| 0,3 | 13 bản, 12,20, **74,4 %** | 0 bản, 0,00, **0 %** |
| 0,5 | 17 bản, 14,11, **86,0 %** | 4 bản, 4,26, **26,0 %** |
| 0,7 | 20 bản, 14,92, 91,0 % | 12 bản, 11,18, 68,2 % |

13 bản đổi nhóm ở ngưỡng 0,5 khi hiệu chỉnh (a07 a16 a18 a32 a38 a50 a54 a60 a63 a64 a68 a71 a75). Ví dụ a71:
F1 oracle 23,05, nhìn thấy thô 0,12, độ nhạy trên 33 TP của chính bản 0,18 → v′ = 0,56.

**Phán xử theo luật đã khai báo:** âm tính giả > 10 % → "71 %" phải thay bằng số hiệu chỉnh; số hiệu chỉnh
26 % < 50 % → kết luận "mô hình không phải nút thắt" **không còn chỗ đứng, phải rút**.

**Nhưng phải nói thêm, và đây là điểm chính:** khi độ nhạy của phép thử trên một bản chỉ 0,09–0,49 (gần
mức nền 0,05), hiệu chỉnh (v − 0,05)/(s − 0,05) chia cho một số gần 0 và **không định danh được** — giá trị 26 %
không đáng tin hơn 86 %. Ở mức nhịp, hiệu chỉnh gộp lại cho kết quả ngược (frac_a hiệu chỉnh ≈ 0,001, tức
"hầu như mọi FN đều không có tín hiệu"), vì độ nhạy gộp bị các bản dễ kéo lên. Hai cách hiệu chỉnh cho hai
cực trái ngược từ cùng dữ liệu = phép thử **không có năng lực phân biệt trên bản khó**. Phát biểu trung thực:
*phần dư địa do "thiếu tín hiệu thật" so với "mô hình bỏ sót" là KHÔNG XÁC ĐỊNH ĐƯỢC bằng phép thử này; khoảng
26–86 % chỉ là hai biên của một đại lượng không đo được.* Kết luận của THICHNGHI.md ("khoảng cách ngoài miền là
thiếu tín hiệu thật") do đó **chỉ còn dựa vào** bằng chứng thích nghi miền thất bại, không còn dựa vào M1.

## VIỆC 5 — Hạt giống (`viec5_seed`)
- Checkpoint seed 1 **không tồn tại** (`train_22.py` chỉ lưu khi `--tag` rỗng). Cấm huấn luyện lại → peakprob
  seed 1 trên 60 bản sạch **không thực hiện được**; ghi vào việc còn thiếu.
- Phần khả thi, 22 chủ thể, cùng 4 epoch, cùng tăng cường; **phân fold khác nhau** giữa hai seed
  (`make_folds(seed)`), kênh PSD trùng 22/22:

| | seed 0 | seed 1 | hiệu | KTC95 | p | chủ thể lệch > 1 | lệch lớn nhất |
|---|---|---|---|---|---|---|---|
| F1 PSD | 97,56 | 97,59 | +0,03 | [−0,18; +0,34] | 0,30 | 1 | 2,81 (B2_03) |
| F1 TB 4 kênh | 96,59 | 96,59 | −0,01 | [−0,14; +0,11] | 0,78 | 0 | 0,74 (B1_10) |
| F1 oracle | 98,63 | 98,59 | −0,04 | [−0,24; +0,17] | 0,30 | 2 | 1,57 (B1_07) |

Kết quả chính trong miền **ổn định theo seed** (kể cả khi đổi phân fold). Không nói được gì về seed ngoài miền.

## Điều gì thay đổi trong phát biểu chính thức
1. Chọn kênh: giữ nguyên "gate là quy tắc chỉ định trước, trượt Holm trên 22 (thô và logit); peakprob tốt nhất
   hậu kiểm trên 60 bản sạch theo F1 thô, **gate4 tốt nhất trên logit**". Thêm: cả ba quy tắc dùng đầu ra mô
   hình vượt psd qua Holm trên logit ngoài miền. Vẫn chưa được gọi là kết quả xác nhận.
2. Rút: "71 % dư địa nằm trên bản không đo được tín hiệu" và "chỉ 1,85 điểm thuộc mô hình". Thay bằng: phép thử
   nhìn thấy có âm tính giả 18 % (55–70 % trên bản khó), phần dư địa do thiếu tín hiệu không xác định được.
3. CHANDOAN_MOHINH.md: nhóm lỗi (b) "không có tín hiệu" phải gắn cảnh báo cùng nội dung; tỉ lệ (a)/(b) chỉ có
   nghĩa trên bản F1 ≥ 90.

## Hạn chế
- Tính lại trên logit là một phép thử hậu kiểm nữa (đã khai báo trước, báo cáo đủ ba cách kẹp, không chọn cách có lợi).
- Độ nhạy phép thử đo trên TP là ước lượng lạc quan; tỉ lệ âm tính giả trên FN thật sự có tín hiệu không đo được.
- Độ đặc hiệu ngoài mẫu chỉ trên 3 bản trong miền.
- 60 bản sạch: chưa kiểm trùng ở mức chủ thể (NCC ≤ 0,62 chỉ loại sao chép nguyên văn).
- Seed: chỉ 2 seed, trong miền, phân fold khác nhau nên hiệu bao gồm cả phương sai phân fold.
- Không có bộ thứ ba → mọi con số CinC vẫn là kết quả trên một bộ ngoài miền duy nhất, sau hậu kiểm.
