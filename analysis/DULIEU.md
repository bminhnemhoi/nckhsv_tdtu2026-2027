# M4 — Dữ liệu huấn luyện đã tốt chưa?

Kiểm toán nhãn · chồng lấn dữ liệu · đường cong số chủ thể · tăng cường · cân bằng nguồn.

Mọi con số trong tài liệu này truy ngược về:

| Tệp | Nội dung |
|---|---|
| `analysis/dulieu_audit.json` | kiểm toán nhãn thô + kết quả quét chồng lấn (RR và tín hiệu) |
| `analysis/dulieu_results.json` | mọi số tổng hợp, thống kê, khớp đường cong |
| `analysis/dulieu_exp.json` | thí nghiệm đối chứng tăng cường / cân bằng (M4-mini) |
| `analysis/fig_dulieu.png` | hình 4 bảng (vòng đầu) |
| `analysis/fig_dulieu_m4b.png` | hình 3 bảng: kiểm độc lập · chọn kênh 60 sạch · thí nghiệm |
| `analysis/dulieu_m4b_verify.json` | **kiểm chồng lấn ĐỘC LẬP** (mã viết lại từ đầu, agent M4b) |
| `analysis/dulieu_m4b_partial.json` | quét chồng lấn **bộ phận** (cửa sổ con 10 s) + nhánh NULL |
| `analysis/dulieu_m4b_a33.json` | kiểm tay ứng viên a33 |
| `analysis/dulieu_results.json → chon_kenh_60_sach` | bảng chọn kênh M5 tính lại trên 60 bản sạch |
| `analysis/dulieu_results.json → thuc_nghiem` | tổng hợp thí nghiệm tăng cường / cân bằng |

Lệnh chạy lại (thứ tự):

```
python analysis/dulieu_audit.py --stage labels
python analysis/dulieu_audit.py --stage overlap
python analysis/dulieu.py
python analysis/dulieu_addendum.py
python analysis/dulieu_fig.py
FQRS_THREADS=2 python analysis/dulieu_exp.py --folds 1,2,3,4 --epochs 2 --keep 3 --arms base,noaug,bal
```

Vòng bổ sung **M4b** (kiểm độc lập + bảng 60 sạch + 2 fold thí nghiệm nữa) chạy theo thứ tự:

```
python analysis/dulieu_m4b_verify.py    # kiem chong lan DOC LAP (viet lai tu dau)   ~4 phut
python analysis/dulieu_m4b_partial.py   # quet chong lan BO PHAN, co nhanh NULL      ~4 phut
python analysis/dulieu_m4b_a33.py       # kiem tay ung vien duy nhat vuot nguong     ~10 giay
FQRS_THREADS=3 python analysis/dulieu_exp.py --folds 11,10 --epochs 2 --keep 3 --arms base,noaug,bal
python analysis/dulieu_m4b.py           # nap tat ca vao dulieu_results.json
python analysis/dulieu_m4b_md.py        # cam khoi ket qua M4-mini vao DULIEU.md
python analysis/dulieu_m4b_fig.py       # -> analysis/fig_dulieu_m4b.png
```

---

## 0. RÚT LẠI CÔNG KHAI — con số CinC 2013 của nhóm bị ô nhiễm bởi chồng lấn dữ liệu

**SỰ KIỆN (fact).** 15 trong 75 bản ghi CinC 2013 set-a **là những đoạn 60 giây cắt trực tiếp
ra từ 5 bản ghi ADFECGDB mà mô hình đã được huấn luyện trên đó**. Tương quan chéo chuẩn hoá
(NCC) giữa tín hiệu CinC và tín hiệu gốc = **1,0000** (bốn chữ số), và chuỗi RR tham chiếu
khớp đến **0,00 ms**.

Cấu trúc chồng lấn đều đặn đến mức không thể là trùng hợp: mỗi bản ghi ADFECGDB dài 5 phút
đóng góp **đúng ba** cửa sổ 60 s — phút 1 (0–60 s), phút 3 (120–180 s), phút 5 (240–300 s):

| CinC | bản gốc | cửa sổ trong bản gốc | ánh xạ kênh | NCC cả 4 kênh |
|---|---|---|---|---|
| a05 | r01 | 0–60 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a04 | r01 | 120–180 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a22 | r01 | 240–300 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a25 | r04 | 0–60 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a20 | r04 | 120–180 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a13 | r04 | 240–300 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a19 | r07 | 0–60 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a23 | r07 | 120–180 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a24 | r07 | 240–300 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a17 | r08 | 0–60 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a15 | r08 | 120–180 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a08 | r08 | 240–300 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a03 | r10 | 0–60 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a14 | r10 | 120–180 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |
| a12 | r10 | 240–300 s | c0→A1, c1→A2, c2→A3, c3→A4 | 1,0000 |

> **SỬA LỖI so với bản 11:05 của tài liệu này.** Bảng trước ghi ánh xạ kênh kiểu
> "ch0 → A2", "ch2 → A3" — **sai**. Kiểm lại bằng ma trận NCC đầy đủ 4×5 cho từng bản
> (`analysis/dulieu_m4b_verify.json → ban_do_kenh_dung`) cho thấy **cả bốn** kênh của mỗi bản
> CinC rò rỉ đều là bản sao NCC = 1,0000 của Abdomen_1…4 **đúng thứ tự**: c0→A1, c1→A2,
> c2→A3, c3→A4, không có ngoại lệ trên cả 15 bản. Lỗi cũ đến từ việc chỉ ghi lại cặp
> khớp tốt nhất thay vì cả ma trận. Kết luận không đổi — nó **mạnh hơn**: rò rỉ không phải
> một kênh mà là **toàn bộ cửa sổ 4 kênh**.


**Độ tin cậy của phép phát hiện.** Phép đo được kiểm chứng hai chiều trước khi dùng:
*đối chứng dương* — 5 cặp trùng đã biết B2↔ADFECGDB cho NCC 0,856–0,984 và median|ΔRR| = 0,00 ms;
*đối chứng âm* — 60 bản CinC còn lại có NCC tối đa **0,4418**. Khoảng trống giữa 1,0000 và 0,4418
không để lại chỗ cho nghi ngờ. (Lưu ý: 5 cặp trùng đã biết chỉ đạt NCC 0,86–0,98 chứ không phải
1,0000 vì hai bản phát hành đã qua lọc/đồng bộ khác nhau; 15 cặp CinC↔ADFECGDB đạt đúng 1,0000
nghĩa là **cùng một tệp mẫu**, chỉ cắt ra.)

**HẬU QUẢ (fact).** Trên 15 bản ghi này mọi mô hình đều đạt ~100 % — vì đó là dữ liệu huấn luyện:
m5 99,92 · m12 99,97 · m22 99,87. Chúng kéo trung bình toàn tập lên.

| Chỉ số (quy tắc PSD mù nhãn) | 75 bản (ĐÃ CÔNG BỐ) | 60 bản SẠCH (ĐÚNG) | thổi phồng |
|---|---|---|---|
| m5  (5 chủ thể)  | 71,21 | **64,04** | +7,18 |
| m12 (12 chủ thể) | 74,34 | **67,93** | +6,41 |
| **m22 (22 chủ thể)** | **79,40** | **74,28** | **+5,12** |
| m22 ORACLE chọn kênh | 86,87 | 83,60 | +3,27 |
| m22 trung bình 4 kênh | 74,09 | 67,69 | +6,40 |
| m22 trung vị | 99,27 | 95,07 | — |
| số bản F1 ≥ 90 | 48/75 | 33/60 | — |
| số bản F1 < 50 | 16/75 | 16/60 | — |

**Phải rút lại / sửa những phát biểu sau:**

1. ~~"CinC 2013 đủ 75 bản ghi, zero-shot, m22 = 79,40"~~ → **74,28 trên 60 bản ghi thật sự
   chưa từng thấy**. Cụm từ "zero-shot xuyên hệ ghi" áp cho cả 75 bản là **sai**; 20 % tập
   kiểm thử là dữ liệu huấn luyện.
2. ~~"dư địa chọn kênh = 86,87 − 79,40 = 7,47 điểm"~~ → **83,60 − 74,28 = 9,32 điểm**
   (dư địa còn LỚN HƠN, không nhỏ hơn).
3. ~~"cổng từ chối kéo 79,40 → 97,76 ở độ phủ 66,7 %"~~ → trên 60 bản sạch, cùng cổng đó và
   cùng độ phủ 66,7 % chỉ kéo **74,28 → 90,28**, và còn **4** bản F1 < 50 lọt lưới (không phải 1).
   (`dulieu_results.json → chong_lan.cong_tu_choi_tinh_lai`)
4. Mọi phát biểu "bản ghi a03/a04/a05/a08/a12/a13/a14/a15/a17/a19/a20/a22/a23/a24/a25 đạt ~100 %"
   không phải bằng chứng tổng quát hoá.
5. **Mẫu 10 bản ghi cũ (a01…a10) cũng bị ô nhiễm**: 4 trong 10 bản (a03, a04, a05, a08) là dữ
   liệu huấn luyện. Các con số 90,34 / 69,31 / 22,33 điểm đã bị rút trước đây vì lý do khác
   (mẫu nhỏ, chọn kênh hậu kiểm) — nay có thêm lý do thứ ba, mạnh hơn. Chúng phải **ở nguyên
   trạng thái đã rút**, không được phục hồi dưới bất kỳ hình thức nào.

**Điều KHÔNG bị bác bỏ.** Luận đề "thêm dữ liệu thì tốt hơn" **mạnh lên** khi bỏ phần ô nhiễm,
vì 15 bản rò rỉ là nơi cả ba mô hình đều bão hoà ở 100 nên chúng *nén* hiệu số lại:

| So sánh (mức bản ghi, quy tắc PSD) | 75 bản (cũ) | 60 bản SẠCH (đúng) |
|---|---|---|
| m22 − m5 | +8,18 KTC95 [+5,62; +11,09] | **+10,24 KTC95 [+7,13; +13,60]**, W p = 3,5e−10, thắng 52/55 |
| m22 − m12 | +5,06 [+3,19; +7,23] | **+6,35 [+4,04; +8,95]**, W p = 3,0e−08, thắng 46/51 |
| m12 − m5 | +3,13 [+1,49; +4,98] | **+3,90 [+1,86; +6,15]**, W p = 1,2e−03, thắng 38/52 |

**SUY LUẬN.** Ba bộ dữ liệu "độc lập" mà nhóm đang dùng thực ra chỉ có **hai** nguồn gốc thật
(nhóm Silesia và CinC 2013), và Silesia xuất hiện ba lần: ADFECGDB trên PhysioNet, Silesia B2,
và 15 bản CinC. Trước khi công bố, **mọi** con số xuyên bộ dữ liệu phải được tính lại trên tập
60 bản sạch, và bài báo phải mô tả rõ phép kiểm chồng lấn này.

**KHUYẾN NGHỊ.** Đưa danh sách 15 bản ghi vào hằng số trong mã nguồn (như đã làm với 7 bản
chú thích sai), và báo cáo song song hai tập: 60 bản sạch (số chính) và 53 bản sạch + chú thích
đúng (số phụ: m22 = **75,27**).

---

### 0.1 Kiểm chứng độc lập (agent M4b)

Phát hiện trên quan trọng đến mức nó được **kiểm lại bằng mã viết lại từ đầu**, không dùng
lại một hàm nào của `analysis/dulieu_audit.py`: NCC chuẩn hoá qua FFT trên tín hiệu **thô**
(chưa lọc, chưa khử mẹ), hạ mẫu 1000 → 250 Hz, quét **mọi** độ trễ, so 75 × 4 kênh CinC với
5 × **5** kênh ADFECGDB (4 bụng **và** kênh điện cực da đầu).

| Kiểm | Kết quả |
|---|---|
| số bản ghi rò rỉ | **15** — trùng khớp danh sách cũ, không thừa không thiếu |
| bản ghi gốc của từng bản | trùng khớp 15/15 |
| cửa sổ 60 s của từng bản | trùng khớp 15/15 (0–60, 120–180, 240–300 s) |
| ánh xạ kênh | **khác** — xem hộp sửa lỗi ở trên |
| \|NCC\| lớn nhất trong 60 bản còn lại | **0,6155** |
| kênh điện cực da đầu (Direct_1) có trong CinC không | **không** — 0/15 |

Con số 0,6155 **khác** con số 0,4418 của vòng trước, vì phép kiểm độc lập này chạy trên tín
hiệu **thô** và **có** đưa kênh điện cực da đầu vào tập so sánh, nên nền tương quan cao hơn.
Điều đó **không** làm yếu kết luận: khoảng trống giữa 0,6155 và 1,0000 vẫn không để lại chỗ
cho nghi ngờ, và hai phép đo độc lập chọn ra **đúng cùng một tập 15 bản ghi**.

Kênh điện cực da đầu **không** nằm trong CinC — nên nhãn fQRS của CinC vẫn do người chú thích
CinC tạo ra độc lập. Rò rỉ ở đây là rò rỉ **tín hiệu đầu vào**, không phải rò rỉ nhãn. Điều
đó không làm nhẹ vấn đề: mô hình đã thấy đúng những mẫu đó lúc huấn luyện.

Mọi con số tổng hợp lại ở mục 0 cũng được tính lại độc lập từ `benchmark_dpss/eval_cinc75.json`
và `benchmark_dpss/eval_12_cinc.json`, khớp đến hai chữ số thập phân (m5 71,21→64,04 ·
m12 74,34→67,93 · m22 79,40→74,28 · oracle 86,87→83,60).

---

## 0.3 Còn chồng lấn BỘ PHẬN không? — quét cửa sổ con 10 s, có đối chứng

Phép quét ở mục 0.1 so **trọn** cửa sổ 60 s. Một bản CinC chỉ trùng 10–30 s với ADFECGDB sẽ bị
pha loãng và lọt lưới. Mục này đóng lỗ hổng đó: quét **cửa sổ con 10 s, bước trượt 5 s**, mọi độ
trễ, 60 bản sạch × 4 kênh × 11 cửa sổ × 25 kênh ADFECGDB.

**Bài học phương pháp — con số thô KHÔNG đọc được một mình.** Lần chạy đầu cho max \|NCC\| = 0,9602
và **12/60 bản vượt 0,9**. Nếu dừng ở đó thì đã kết luận sai rằng có 12 bản rò rỉ thêm. Vấn đề:
quét cửa sổ con có **số so sánh khổng lồ**, và hai chuỗi QRS giả chu kỳ bất kỳ luôn tự tương quan
mạnh ở *một* độ trễ nào đó. Phải có **nhánh NULL** mới có ngưỡng. Nhánh NULL dùng ADFECGDB **đảo
ngược thời gian** — giữ nguyên phổ và cấu trúc chuỗi QRS, phá huỷ mọi trùng khớp thật.

| nhánh | n | trung vị \|NCC\| | max \|NCC\| |
|---|---|---|---|
| **clean** — 60 bản sạch vs ADFECGDB thật | 60 | 0,8448 | 0,9602 |
| **null** — 60 bản sạch vs ADFECGDB ĐẢO NGƯỢC | 60 | 0,8276 | 0,9450 |
| **positive** — 15 bản đã biết rò rỉ vs ADFECGDB thật | 15 | 1,0000 | 1,0000 |

**KẾT QUẢ.** Phân bố nhánh clean **không phân biệt được** với nhánh null:
Mann-Whitney p = 0,6255, KS p = 0,8133. Đối chứng dương đạt **đúng 1,0000 cả 15/15**, nên phép đo
thừa độ nhạy. Kết luận: **không có bằng chứng chồng lấn bộ phận** trong 60 bản sạch.

**Ứng viên duy nhất vượt ngưỡng null — a33, đã loại bằng tay.** a33 (kênh 3) cho NCC =
**−0,9602** với r07/Abdomen_3. Phép phân biệt quyết định: **bản sao thật giữ \|NCC\| = 1,0000 ở
MỌI độ dài cửa sổ; trùng hợp ngẫu nhiên thì SUY GIẢM** khi kéo dài cửa sổ, vì nhịp tim hai sản
phụ trôi khỏi nhau.

| độ dài cửa sổ | a33 (ứng viên) | a19 (bản sao THẬT, đối chứng) |
|---|---|---|
| 5 s | −0,9667 | +1,0000 |
| 10 s | −0,9587 | +1,0000 |
| 15 s | −0,9301 | +1,0000 |
| 20 s | −0,9048 | +1,0000 |
| 30 s | −0,8918 | +1,0000 |

a33 suy giảm 0,9667 → 0,8918; a19 đứng yên ở 1,0000. **a33 không phải bản sao** — nó chỉ là hai chuỗi
QRS mẹ tình cờ khớp pha trong ~10 s, dấu âm do cực điện cực ngược. Giữ a33 trong tập 60 bản sạch.
(Riêng a33 vẫn nằm trong 7 bản **chú thích sai** đã khai báo trước — chuyện khác, không liên quan.)

*Nguồn: `analysis/dulieu_m4b_partial.json`, `analysis/dulieu_m4b_a33.json`;
mã: `analysis/dulieu_m4b_partial.py`, `analysis/dulieu_m4b_a33.py`.*

---

## 0.2 Hệ quả cho kết quả CHỌN KÊNH (nhiệm vụ M5) — tính lại trên 60 bản sạch

Đề bài M4 nêu rõ: nếu có chồng lấn thì **mọi** con số xuyên bộ dữ liệu bị đe doạ, "kể cả kết quả
chọn kênh vừa đạt được". Bảng M5 được đo trên **75** bản ghi, trong đó 15 bản là dữ liệu huấn
luyện. Dưới đây là bảng đó tính lại trên **60 bản sạch**, từ
`analysis/chonkenh_results.json → F1_tung_ban_ghi.cinc` (F1 từng bản ghi đã có sẵn, không chạy
lại mô hình), bootstrap cụm 10 000 lần, Wilcoxon ghép cặp, Holm trên **7 quy tắc mới**.
Nguồn: `dulieu_results.json → chon_kenh_60_sach`.

| quy tắc | F1 trên 75 (ô nhiễm) | **F1 trên 60 sạch** | ≥90 | <50 | hiệu vs psd, KTC95 | Wilcoxon p | Holm p |
|---|---|---|---|---|---|---|---|
| psd *(đang dùng)* | 79,40 | 74,28 | 33 | 16 | — | — | — |
| peakprob | 85,60 | 82,01 | 38 | 9 | **+7,73** [+3,82; +12,41] | 0,0005564 | 0,003895 |
| gate4 | 84,77 | 81,01 | 38 | 12 | **+6,72** [+2,85; +11,18] | 0,002505 | 0,01503 |
| gate | 84,54 | 80,72 | 38 | 12 | **+6,44** [+2,49; +11,10] | 0,01011 | 0,05055 |
| rrcv | 83,98 | 80,00 | 38 | 12 | **+5,72** [+1,61; +10,41] | 0,1014 | 0,4056 |
| rrplaus | 83,08 | 78,87 | 37 | 14 | **+4,59** [+0,88; +8,93] | 0,1291 | 0,4056 |
| learned *(hỏng)* | 82,21 | 77,80 | 37 | 16 | **+3,52** [-0,77; +8,48] | 0,6947 | 1 |
| fuse_k2 *(hỏng)* | 81,15 | 76,46 | 32 | 14 | **+2,18** [-0,40; +4,98] | 0,5232 | 1 |
| trung bình 4 kênh | 74,09 | 67,69 | 15 | 17 | **-6,59** [-10,55; -2,85] | 0,001858 | — |
| kênh 0 cố định | 69,33 | 61,78 | 21 | 27 | **-12,50** [-22,77; -2,27] | 0,01864 | — |
| **ORACLE** | 86,87 | 83,60 | 38 | 8 | **+9,32** [+5,01; +14,09] | 5,96e−8 | — |

**KẾT QUẢ: hiệu ứng chọn kênh KHÔNG bị chồng lấn thổi phồng — nó bị chồng lấn *che bớt*.**

* peakprob − psd đi từ **+6,20** (75 bản) lên **+7,73** (60 bản sạch), KTC95 [+3,82; +12,41].
* gate − psd đi từ +5,14 lên **+6,44**.
* Dư địa oracle đi từ 7,47 lên **9,32** điểm.

**Vì sao.** 15 bản rò rỉ là dữ liệu huấn luyện nên **mọi** quy tắc đều đạt ~100 ở đó; chúng đóng
góp 15 cặp *hoà* vào phép so sánh ghép cặp, làm loãng cả hiệu số lẫn kiểm định. Bỏ chúng ra thì
mẫu hiệu dụng nhỏ hơn nhưng thông tin nhiều hơn.

**MỨC BẰNG CHỨNG SAU KHI LÀM SẠCH.** Mọi giá trị Holm đều **giảm** (mạnh lên), nhưng **không
quy tắc nào đổi kết luận**: hai quy tắc đã sống sót trên 75 bản (`peakprob`, `gate4`) vẫn sống sót,
và `gate` vẫn không. Làm sạch dữ liệu **củng cố** bức tranh cũ chứ không tạo ra kết luận mới:

| quy tắc | Holm p (75 bản) | Holm p (60 bản sạch) | kết luận |
|---|---|---|---|
| peakprob (hậu kiểm) | 0,0054 | **0,0039** | sống sót |
| gate4 (tiền đăng ký) | 0,0260 | **0,0150** | sống sót |
| **gate (tiền đăng ký, quy tắc quyết định)** | 0,0848 | **0,0505** | **vẫn KHÔNG sống sót** |

**PHÁT BIỂU ĐÚNG, không được nới thêm.** Quy tắc quyết định tiền đăng ký là `gate`, và trên tập
sạch nó vẫn **không** vượt ngưỡng Holm — p = 0,0505 nằm *ngay sát* 0,05 nhưng nằm ở phía sai.
Không được đọc "0,0505 coi như 0,05". Điều đã được xác nhận là: `gate4` (cũng thuộc họ 7 quy tắc
tiền đăng ký) sống sót — và nó đã sống sót **cả trước lẫn sau** khi làm sạch, nên đây không
phải kết quả sinh ra từ việc bỏ 15 bản ghi. **Họ quy tắc chọn kênh nói chung** cho hiệu ứng vững:
**cả 7/7** quy tắc đều vượt psd trên tập sạch, 6/7 vượt từ **+3,52 đến +7,73** điểm, và **không
quy tắc nào** có hiệu số âm. Hướng hiệu ứng nhất quán tuyệt đối. Việc `peakprob` là quy tắc **tốt
nhất** vẫn là lựa chọn **hậu kiểm** và vẫn **chưa** được xác nhận ngoài miền. Cảnh báo liêm chính
của M5 giữ nguyên hiệu lực, không được gỡ.

**Một hệ quả thực dụng.** Trên tập sạch, chuyển từ psd sang peakprob đưa số bản F1 < 50 từ
**16 xuống 9** và số bản ≥ 90 từ **33 lên 38**. Đó là 7 bản ghi đi từ "vô dụng" sang "dùng được"
mà **không** cần huấn luyện lại, không cần thêm dữ liệu, chỉ tốn 4 lần suy luận thay vì 1.

---

## 1. VIỆC 1 — kiểm toán chất lượng nhãn

### 1.1 Nhịp bất thường trong nhãn (22 chủ thể)

Tiêu chí khai báo trước khi chạy: RR ngoài dải sinh lý (< 250 ms hoặc > 700 ms, tức ngoài
86–240 bpm), nhảy RR đột ngột (|RR_k/RR_{k−1} − 1| > 25 %), khoảng trống > 2 s.

| Nhóm | n | nhịp | RR ngoài dải (TB %) | nhảy > 25 % (TB %) | khoảng trống > 2 s | pNN50 (%) | độ phủ (%) |
|---|---|---|---|---|---|---|---|
| PhysioNet (trực tiếp) | 5 | 3 191 | 0,312 | 0,561 | 3 (11,0 s) | 0,56 | 99,17 |
| Silesia B2 (trực tiếp) | 7 | 4 717 | 0,206 | 0,413 | 2 (6,7 s) | 0,48 | 99,53 |
| **Silesia B1 (gián tiếp)** | 10 | 28 405 | **0,115** | **0,038** | **0** | **0,24** | **99,95** |
| CinC 2013 set-a (đối chiếu) | 75 | 10 484 | 0,392 | 1,097 | 5 (18,0 s) | 1,93 | 97,87 |

**FACT.** Tỉ lệ nhịp bất thường trong nhãn rất thấp ở mọi nguồn (≤ 0,4 % trung bình). Không
có chủ thể nào có khoảng trống nhãn đáng kể; bản tệ nhất là B1_10 với 1,12 % RR ngoài dải và
r10 với 3 khoảng trống tổng 11,0 s.

**SUY LUẬN — đây mới là phát hiện đáng lo.** Nhãn B1 **quá đều**. B1 có tỉ lệ nhảy RR > 25 %
thấp hơn nhãn điện cực da đầu **10–15 lần** (0,038 % so với 0,41–0,56 %), pNN50 bằng **một nửa**,
độ phủ 99,95 % và **không một khoảng trống nào** trong 200 phút. Với nhãn gián tiếp (tác giả khử
ECG mẹ rồi dò QRS thai trên tín hiệu bụng) thì mức "sạch" đó không phải là chất lượng cao hơn —
nó là dấu hiệu nhãn **đã bị làm trơn**: những nhịp mà máy dò không tìm được đã được nội suy hoặc
bỏ qua, chứ không để lại lỗ hổng.

**GIẢI THÍCH CẠNH TRANH — phải nêu ra và CHƯA loại trừ được.** B1 là **thai kỳ** (nghỉ ngơi,
20 phút), còn PhysioNet và B2 là **chuyển dạ**. Biến thiên nhịp tim thai tăng thật trong chuyển
dạ (cơn co, nhịp giảm muộn/sớm), nên pNN50 thấp hơn ở B1 có thể hoàn toàn là **sinh lý**, không
phải hiện vật của nhãn. Nhóm **chưa tách được** hai cách giải thích này. Điều khó giải thích
bằng sinh lý hơn là: **không một khoảng trống > 2 s nào trong 200 phút** của nhãn gián tiếp,
trong khi nhãn điện cực da đầu — vốn là tiêu chuẩn vàng — vẫn có (r10: 3 khoảng, 11,0 s).
Một bộ dò chạy trên tín hiệu bụng khó mà không bao giờ mất dấu.

**GIẢ THUYẾT (chưa kiểm chứng).** Vì B1 chiếm 64 % số nhịp mà mô hình nhìn thấy mỗi epoch
(mục 4), mô hình đang học một **tiên nghiệm nhịp quá đều**. Điều này khớp với phát hiện đã có
trong `analysis/CLINICAL.md` — mô hình không dùng được làm máy đo STV độc lập (chệch +20,50 ms
trên CinC) — và khớp với `analysis/ABLATION_B1.md` — có dấu vân nhãn ở mốc thời gian trên B1.
Cách kiểm: so phổ biến thiên RR của **đầu ra mô hình** với nhãn điện cực da đầu trên B2/PhysioNet;
nếu mô hình nén biến thiên lại thì giả thuyết được ủng hộ. **Chưa chạy.**

### 1.2 Nhịp "cờ = 0" trong Silesia B1 (nhãn gián tiếp chưa được duyệt)

| Bản ghi | nhịp | cờ 0 | % | RR ngoài dải sau khi lọc (%) | RR max sau khi lọc (ms) |
|---|---|---|---|---|---|
| B1_01 | 3 120 | 2 | 0,06 | 0,032 | 1 562 |
| B1_02 | 2 804 | 13 | 0,46 | 0,287 | 2 588 |
| B1_03 | 2 565 | 8 | 0,31 | 0,156 | 2 444 |
| B1_04 | 2 774 | 0 | 0,00 | 0,000 | 486 |
| B1_05 | 2 770 | 6 | 0,22 | 0,036 | 2 956 |
| B1_06 | 2 889 | 10 | 0,35 | 0,174 | 2 884 |
| B1_07 | 3 114 | 18 | 0,58 | 0,291 | 2 708 |
| B1_08 | 2 911 | 14 | 0,48 | 0,207 | 2 180 |
| **B1_09** | 2 866 | **50** | **1,74** | 0,249 | **8 738** |
| B1_10 | 2 592 | 9 | 0,35 | **1,201** | 3 272 |
| **Tổng** | **28 405** | **130** | **0,458** | | |

**FACT.** Chỉ 0,458 % số nhịp B1 mang cờ 0. Lọc chúng khỏi tập tham chiếu khi **đánh giá**
(mô hình m5, kênh PSD, `benchmark_dpss/silesia_eval.json`) cho hiệu số F1 trung bình
**+0,129 điểm** trên cả 10 chủ thể, dải −0,002 … **+0,645** (B1_09):

B1_01 −0,002 · B1_02 +0,141 · B1_03 +0,037 · B1_04 0,000 · B1_05 +0,072 · B1_06 +0,136 ·
B1_07 +0,138 · B1_08 +0,050 · B1_09 +0,645 · B1_10 +0,077.

Điều này **tái lập và mở rộng** kết quả vòng trước (+0,08 cho B1_06 và +0,16 cho B1_07 — cùng
bậc độ lớn, sai khác do vòng trước dùng kênh khác).

**KẾT LUẬN.** Cờ 0 **không** phải nguồn sai số đáng kể: 0,13 điểm F1, nhỏ hơn độ ổn định giữa
hai hạt giống (0,28 điểm). Giữ nguyên quy ước hiện tại (`fqrs_all`, kể cả cờ 0) là hợp lý và
đúng với `silesia_eval`. **Cảnh báo:** phép đo này là ở phía **đánh giá**; ảnh hưởng của việc
loại nhịp cờ 0 khỏi phía **huấn luyện** chưa được đo.

**Một chi tiết cần để ý:** sau khi lọc cờ 0, B1_09 để lại một khoảng trống RR **8 738 ms** —
tức gần 9 giây không có nhãn thai. Nếu sau này dùng B1 để nói về biến thiên nhịp, phải loại
đoạn đó bằng tay.

### 1.3 Chồng lấn dữ liệu — xem mục 0

Đây là món nợ đã ghi trong đề cương và **nay đã trả**. Kết quả: **CÓ chồng lấn**, 15/75 bản
ghi CinC 2013 set-a. Chi tiết ở mục 0.

Ngoài ra phép quét cũng cho hai kết luận phụ:

* **Silesia B1 ↔ CinC 2013: KHÔNG chồng lấn.** Cặp cao nhất a60 ↔ B1_10, NCC 0,4196.
* **Silesia B2 (7 bản dùng để huấn luyện) ↔ CinC 2013: KHÔNG chồng lấn.** Cặp cao nhất
  a33 ↔ B2_03, NCC 0,3986.
* **60 bản CinC còn lại ↔ ADFECGDB: KHÔNG chồng lấn.** Cặp cao nhất a54 ↔ r08, NCC 0,4418 —
  đây cũng là NCC lớn nhất trong toàn bộ 60 bản sạch, so với 1,0000 của 15 bản rò rỉ.

### 1.4 Xác nhận 5 bản trùng B2 ↔ PhysioNet đã được xử lý đúng

**FACT.** `model/train_22.py` khai báo `B2_DUPLICATES = {B2_01: r01, B2_02: r10, B2_07: r04,
B2_10: r07, B2_11: r08}` và danh sách `B2` dùng để huấn luyện là `['B2_03','B2_04','B2_05',
'B2_06','B2_08','B2_09','B2_12']` — 5 bản trùng **không** nằm trong đó. `train_22.json →
meta.excluded_duplicates` ghi lại đúng 5 cặp này. Kiểm tra độc lập từ phía nhãn xác nhận trùng:
số nhịp giống hệt (B2_01 644 = r01 644; B2_02 637 = r10 637; B2_07 632 = r04 632;
B2_10 627 = r07 627), median|ΔRR| = 0,00 ms cho cả 5 cặp. **Cấu hình đúng, không có lỗi.**

(Cặp B2_11 ↔ r08 có 646 so với 651 nhịp — chênh 5 nhịp ở rìa — nhưng NCC 0,856 và ΔRR 0,00 ms
nên vẫn là cùng một sản phụ; loại là đúng.)

---

## 2. VIỆC 2 — đường cong dữ liệu: bao nhiêu chủ thể mới đủ?

### 2.1 Ba điểm dữ liệu, hai trục đo

**Trục ngoài miền (trục chính)** — cùng 60 bản ghi CinC 2013 SẠCH cho cả ba mô hình, cả ba
đều chưa từng thấy chúng:

| n chủ thể huấn luyện | 5 | 12 | 22 |
|---|---|---|---|
| F1 (PSD, 60 bản sạch) | 64,04 | 67,93 | **74,28** |

**Trục trong miền** — cùng 10 chủ thể B1 cho cả ba mô hình; m5 và m12 chưa từng thấy B1 nào,
m22 được chấm bằng LOSO nên chủ thể kiểm thử luôn bị giữ ngoài (n huấn luyện thực = 19):

| n chủ thể huấn luyện | 5 | 12 | 19 |
|---|---|---|---|
| F1 (PSD, 10 chủ thể B1) | 93,30 | 94,37 | **97,15** |

### 2.2 Khớp và ngoại suy — BA DẠNG HÀM CHO BA CÂU TRẢ LỜI KHÁC NHAU

Trục ngoài miền (CinC 60 sạch):

| Dạng khớp | tiệm cận | n = 30 | **n = 50** | n = 100 | n = 200 |
|---|---|---|---|---|---|
| F1 = a − b/n | **75,2** | 73,2 | **74,0** | 74,6 | 74,9 |
| F1 = a + b·log n | — (không bão hoà) | 75,5 | **79,0** | 83,6 | 88,3 |
| logit(F1/100) = a + b·log n | 100 | 75,3 | **78,2** | 81,7 | 84,8 |

Trục trong miền (10 chủ thể B1):

| Dạng khớp | tiệm cận | n = 30 | **n = 50** | n = 100 |
|---|---|---|---|---|
| F1 = a − b/n | 97,3 | 96,6 | **96,9** | 97,1 |
| logit(F1/100) = a + b·log n | 100 | 97,4 | **98,1** | 98,8 |

### 2.3 Đọc kết quả — TRẢ LỜI THẲNG

**Ba điểm dữ liệu KHÔNG đủ để khớp một đường bão hoà một cách đáng tin.** Với 3 điểm và 2
tham số mỗi dạng, mỗi khớp chỉ còn **1 bậc tự do**; không có khoảng tin cậy nào đúng nghĩa.
Hai dạng hàm hợp lý như nhau (RMSE 1,74 so với 1,01 điểm — không đủ để loại dạng nào) lại cho
**hai câu trả lời trái ngược** cho cùng câu hỏi "50 chủ thể thì được bao nhiêu?":

* dạng `a − b/n`: **74,0** — nghĩa là *đã gần hết dư địa*, thêm 28 sản phụ nữa chỉ được ~0 điểm;
* dạng log/logit: **78,2 … 79,0** — nghĩa là *thêm 28 sản phụ được khoảng +4 đến +5 điểm*.

Khoảng ước lượng trung thực cho n = 50 là **74 … 79 điểm F1 ngoài miền** (hiện tại 74,28).
Với n = 100 là **74,6 … 83,6**. Đây là **NGOẠI SUY, độ tin cậy thấp**, và độ rộng của nó lớn
hơn hiệu ứng mà nhóm muốn đo.

**KHUYẾN NGHỊ cho quyết định "có đi xin thêm dữ liệu không".**

1. **Không nên dùng đường cong này làm căn cứ chính.** Nó không phân biệt được "đã bão hoà"
   với "còn tăng tuyến tính theo log". Trình bày nó trong bài báo thì phải kèm đúng câu này.
2. **Căn cứ mạnh hơn nằm ở chỗ khác:** dư địa chọn kênh trên tập sạch là **9,32 điểm**
   (83,60 oracle − 74,28 PSD), lớn hơn *mọi* ước lượng lợi ích của việc tăng từ 22 lên 50 chủ
   thể theo dạng `a − b/n`, và ngang ngửa ước lượng lạc quan nhất theo dạng log. **Tiền và thời
   gian bỏ vào quy tắc chọn kênh có kỳ vọng hoàn vốn cao hơn bỏ vào thu thập 28 sản phụ mới.**
   Điều này khớp với kết quả LUONGCUC ("cực dưới chủ yếu là lỗi chọn kênh") và với việc dip test
   biến mất trên kênh oracle (p = 0,589).
3. **Nếu vẫn xin thêm dữ liệu, hãy xin ĐÚNG LOẠI.** Xem mục 4: cái thiếu không phải số giờ,
   mà là **số sản phụ có nhãn điện cực da đầu** và **một trung tâm ghi thứ hai**. 10 sản phụ
   mới từ một trung tâm khác có nhãn trực tiếp có giá trị hơn 40 sản phụ nữa từ Silesia.
4. **Điểm dữ liệu thứ tư sẽ rẻ.** Huấn luyện một mô hình m17 (bỏ 5 chủ thể B1) và chấm trên
   60 bản CinC sạch tốn ~30 phút CPU và sẽ tách được hai dạng hàm tốt hơn mọi lập luận nào.
   Đây là việc nên làm trước khi viết mục này vào bài báo.

---

## 3. VIỆC 3 — tăng cường dữ liệu có giúp không?

### 3.1 BÁO CÁO THẤT BẠI: lần chạy đối chứng không-tăng-cường ĐÃ HỎNG

**FACT.** `model/train_22_noaug_log.txt` dừng lại sau epoch 2 của fold 01:

```
-- fold 01  test=['B1_08', 'B2_12']  val=r10 ...
      epoch 1/4 loss 0.3406  (394s, 33332 doan, pos_w 13.6)
      epoch 2/4 loss 0.2777  (882s, 33332 doan, pos_w 13.6)
```

`model/train_22_noaug_stdout.txt` kết thúc bằng
`RuntimeError: [enforce fail at alloc_cpu.cpp:117] DefaultCPUAllocator: not enough memory:
you tried to allocate 5120000 bytes` — hết bộ nhớ ở 9 luồng. **Không có tệp
`model/train_22_noaug.json`.** Không có một kết quả kiểm thử nào.

**Vì vậy phát biểu "đã có đối chứng không tăng cường để đối chiếu" là SAI và phải sửa.**
Trước hôm nay nhóm **không có bằng chứng nào** về việc tăng cường có giúp hay không.

### 3.2 Tăng cường hiện đang làm gì (đọc `model/augment.py` và `model/train_22.py`)

Bốn phép, mỗi phép áp độc lập với xác suất p = 0,5 cho từng đoạn trong batch:

| Phép | Tham số | Áp thế nào |
|---|---|---|
| (a) nhân biên độ | a ~ U(0,7 ; 1,4) | **một hệ số chung** cho cả hàng dư và hàng gốc |
| (b) nhiễu Gauss trắng | SNR ~ U(10 ; 30) dB | cùng một hiện thực nhiễu chuẩn hoá, tỉ lệ theo công suất từng hàng |
| (c) trôi đường nền | sin, f ~ U(0,1 ; 0,5) Hz, biên độ 0,1–0,3 × SD | cùng f và pha cho hai hàng |
| (d) dịch thời gian | ±100 ms | **không đệm 0** — bộ lấy mẫu đọc đoạn từ vị trí s+δ trong bản ghi đầy đủ, nên tín hiệu và nhãn dịch cùng nhau |

**Nhận xét kỹ thuật (đọc `train_22.py::gather` — tăng cường áp SAU khâu tiền xử lý).**
Trong `gather()`, `X` đã là tín hiệu **đã lọc 10–60 Hz, đã khử mẹ, đã robust_scale**, rồi mới
gọi `augment_batch(X)`. Hệ quả:

* (d) dịch thời gian được cài đặt đúng cách — bộ lấy mẫu đọc lại từ bản ghi đầy đủ, không có
  mẫu đệm 0 giả.
* (a) nhân biên độ là vô hại và hợp lý.
* (c) trôi đường nền 0,1–0,5 Hz được cộng **sau** bộ lọc thông cao 10 Hz. Mạng **có** nhìn thấy
  nhiễu đó khi huấn luyện, nhưng khi suy luận thì tiền xử lý đã loại sạch dải đó — nên phép này
  dạy mạng chống lại một nhiễu **không thể xuất hiện ở thời điểm kiểm thử**. Đây là **lệch
  huấn luyện/suy luận**, không phải bất biến có ích.
* (b) nhiễu Gauss **toàn dải** cũng được cộng sau bộ lọc, trong khi nhiễu thật mà mạng gặp lúc
  suy luận luôn bị giới hạn trong 10–60 Hz. Cùng loại lệch, mức độ nhẹ hơn.

Nếu muốn (b) và (c) mô phỏng đúng thứ mạng sẽ gặp, phải cộng nhiễu **trước** `M.preprocess`,
hoặc lọc nhiễu bằng đúng bộ lọc đó trước khi cộng. Đây là một lỗi thiết kế cụ thể, sửa được.

### 3.3 Thí nghiệm đối chứng M4-mini (đã chạy lại trong nhiệm vụ này)

Giao thức khai báo **trước** khi chạy (`analysis/dulieu_exp.py`): cùng các fold nhóm chủ thể
của `train_22.py`; chỉ số huấn luyện lấy 1/3 đoạn; 2 epoch; **ngưỡng cố định 0,75 cho cả ba
nhánh** (không dò ngưỡng trên val) — nên ba nhánh khác nhau **duy nhất** ở phép tăng cường /
cân bằng. Ba nhánh: `base` (có tăng cường), `noaug` (không), `bal` (cân bằng theo số nhịp).

**KHAI BÁO SAI LỆCH GIAO THỨC (bắt buộc ghi).** Kế hoạch ban đầu là chạy fold 1, 2, 3, 4.
Sau khi fold 1 chạy xong hai nhánh (`base` B1_08 99,76 / B2_12 100,00 ; `noaug` B1_08 99,73 /
B2_12 100,00) **đã thấy rõ hai chủ thể của fold 1 nằm ở TRẦN** — không phép tăng cường nào có
chỗ để thể hiện. Vì ngân sách chỉ còn ~45 phút CPU, tôi đã **dừng lần chạy và chuyển sang
fold 4** (kiểm thử B1_06 và B2_04), vì B1_06 là **một trong ba bản ghi khó** đã biết của dự án.
Việc chọn lại fold này là **hậu kiểm** và dựa trên *phương sai kỳ vọng*, không dựa trên kết quả
của fold 4 (chưa chạy khi quyết định). Tôi ghi lại đây để người đọc tự trừ hao. Kết quả fold 1
vẫn được giữ và báo cáo đầy đủ.

**BỔ SUNG VÒNG M4b (ghi tiếp cùng tinh thần).** Sau khi có thêm ngân sách, tôi chạy thêm
**fold 10** (kiểm thử B1_07 và r08) và **fold 11** (B2_08 và **B2_03**) với **cả ba nhánh**.
Hai fold này cũng được chọn **có chủ đích**: B1_07 và B2_03 là hai trong ba bản ghi khó đã biết,
và B2_03 là bản ghi duy nhất mà mục 0.2 cho thấy bị **giới hạn thật của bộ dò** chứ không phải
lỗi chọn kênh. Lý do chọn giống lần trước — tối đa hoá phương sai quan sát được — và quyết định
được đưa ra **trước** khi chạy. Hệ quả phải trừ hao: mẫu 8 chủ thể này **thiên về phía khó**,
không đại diện cho 22 chủ thể. Lệnh đã chạy:
`FQRS_THREADS=3 python analysis/dulieu_exp.py --folds 11,10 --epochs 2 --keep 3 --arms base,noaug,bal`.
Sau bổ sung: nhánh `base`/`noaug` có **8** chủ thể (fold 1, 4, 10, 11), nhánh `bal` có **6**
(fold 4, 10, 11 — fold 1 không chạy `bal` vì cả hai chủ thể đã ở trần).

> **CẢNH BÁO BẮT BUỘC:** quy mô nhỏ hơn sản xuất (2 epoch, 1/3 dữ liệu) nên **số tuyệt đối
> thấp hơn `train_22.json` và KHÔNG so sánh trực tiếp được**. Chỉ hiệu số giữa ba nhánh là
> có ý nghĩa. Với 4 fold, n = 8 chủ thể — **công suất thống kê rất thấp**; theo
> `analysis/STATS.md`, n = 8 chỉ phát hiện được hiệu ứng rất lớn.

<!-- KET_QUA_M4_MINI -->

**Bảng A — tăng cường (`base`) trừ không tăng cường (`noaug`), F1 mức chủ thể, quy tắc PSD.**

| fold | chủ thể | base | noaug | hiệu |
|---|---|---|---|---|
| 1 | B1_08 | 99,76 | 99,73 | **+0,03** |
| 1 | B2_12 | 100,00 | 100,00 | **+0,00** |
| 4 | B1_06 | 88,68 | 90,80 | **−2,12** |
| 4 | B2_04 | 98,98 | 98,98 | **+0,00** |
| 10 | B1_07 | 86,21 | 85,47 | **+0,74** |
| 10 | r08 | 99,85 | 99,85 | **+0,00** |
| 11 | B2_08 | 100,00 | 100,00 | **+0,00** |
| 11 | B2_03 | 78,17 | 77,81 | **+0,36** |
| | **trung bình (n = 8)** | | | **−0,12** |

Hiệu trung bình **−0,12** điểm, KTC95 bootstrap [−0,75; +0,32], Wilcoxon p = 0,875, thắng 3 / hoà 4 / thua 1.
Chỉ tính 4 chủ thể **không ở trần** (F1 < 99,5 ở cả hai nhánh): hiệu **−0,26** điểm.

> **KẾT LUẬN (báo cáo thất bại).** Ở quy mô đã đo, tăng cường dữ liệu hiện tại **không làm gì cả**: hiệu số trung bình −0,12 điểm, KTC95 ôm sát 0 ở cả hai phía, thắng 3 / hoà 4 / thua 1. Bốn trong tám chủ thể cho hiệu số **đúng bằng 0,00** — tăng cường không đổi được một nhịp nào. Phát biểu đúng là *"không có bằng chứng tăng cường giúp"*, **không** phải *"tăng cường có hại"*. Điều này khớp với phân tích ở mục 3.2: hai trong bốn phép (nhiễu Gauss toàn dải, trôi đường nền 0,1–0,5 Hz) được cộng **sau** bộ lọc 10–60 Hz nên dạy mạng chống một nhiễu không thể tồn tại lúc suy luận. Nhóm đang trả ~20 % thời gian huấn luyện cho bốn phép biến đổi không đo được tác dụng.

**Bảng B — cân bằng theo số nhịp (`bal`) trừ `base`.**

| fold | chủ thể | bal | base | hiệu |
|---|---|---|---|---|
| 4 | B1_06 | 89,90 | 88,68 | **+1,22** |
| 4 | B2_04 | 99,20 | 98,98 | **+0,22** |
| 10 | B1_07 | 87,11 | 86,21 | **+0,90** |
| 10 | r08 | 99,85 | 99,85 | **+0,00** |
| 11 | B2_08 | 100,00 | 100,00 | **+0,00** |
| 11 | B2_03 | 80,14 | 78,17 | **+1,97** |
| | **trung bình (n = 6)** | | | **+0,72** |

Hiệu trung bình **+0,72** điểm, KTC95 [+0,19; +1,34], Wilcoxon p = 0,125, thắng 4 / hoà 2 / thua 0.

> **KẾT LUẬN — đây là kết quả đáng theo đuổi nhất của mục này.** Cân bằng nguồn **thắng 4, hoà 2, KHÔNG thua trận nào**, và khoảng tin cậy **không chứa 0**. Hiệu ứng tập trung đúng chỗ cần: ba chủ thể khó nhất của dự án đều được lợi nhiều nhất (B2_03 **+1,97** — bản ghi duy nhất bị giới hạn thật của bộ dò; B1_06 +1,22; B1_07 +0,90), còn ba chủ thể đã ở trần thì đứng yên. Wilcoxon p = 0,125 chỉ vì n quá nhỏ: với 4 cặp khác 0, giá trị p nhỏ nhất có thể đạt được là 0,125 — **kiểm định không thể có ý nghĩa ở cỡ mẫu này dù hiệu ứng có thật đến đâu**.
>
> **CHƯA phải bằng chứng, vì hai lý do phải nói rõ.** (1) Ba fold này được chọn **có chủ đích vì chúng chứa các bản ghi khó** — mẫu không đại diện, và hiệu ứng đo được ở đây là cận trên lạc quan. (2) n = 6 với 2 cặp hoà; KTC95 bootstrap trên 4 giá trị khác 0 rất mỏng. **Khuyến nghị: chạy cân bằng đủ 11 fold ở quy mô sản xuất** (~2,5 giờ/nhánh) — đây là thí nghiệm tiếp theo đáng chi ngân sách nhất trong nhiệm vụ M4. Và dùng **trọng số mất mát** thay vì lấy mẫu lặp (mục 4.2), vì lấy mẫu lặp khiến 5 chủ thể PhysioNet bị lặp ~2,3 lần/epoch.

*Nguồn: `analysis/dulieu_exp.json` (từng lần chạy), `analysis/dulieu_results.json → thuc_nghiem` (tổng hợp), `analysis/dulieu_exp_log.txt` (nhật ký). Tổng hợp bởi `analysis/dulieu_m4b.py`.*

<!-- /KET_QUA_M4_MINI -->

---

## 4. VIỆC 4 — cân bằng dữ liệu

### 4.1 Tập huấn luyện 22 chủ thể thực sự gồm những gì

| Nguồn | n chủ thể | phút | nhịp | stride | đoạn 4 s / epoch | nhịp mô hình NHÌN THẤY / epoch | nhãn |
|---|---|---|---|---|---|---|---|
| PhysioNet (ADFECGDB) | 5 | 25,0 (9,6 %) | 3 191 (8,8 %) | 250 | 5 920 (15,6 %) | 50 375 (14,4 %) | TRỰC TIẾP |
| Silesia B2 | 7 | 35,0 (13,5 %) | 4 717 (13,0 %) | 250 | 8 288 (21,8 %) | 74 466 (21,2 %) | TRỰC TIẾP |
| **Silesia B1** | 10 | **199,6 (76,9 %)** | **28 405 (78,2 %)** | 500 | **23 840 (62,7 %)** | **226 140 (64,4 %)** | **GIÁN TIẾP** |
| Tổng | 22 | 259,6 | 36 313 | — | 38 048 | 350 981 | — |

**FACT.** Giả thiết trong đề bài ("B1 chiếm 200/260 phút") đúng: 76,9 % số giây và 78,2 % số
nhịp đến từ B1. Tuy nhiên **stride 500 mẫu cho B1 (so với 250 cho hai nguồn kia) đã làm một
phần việc cân bằng rồi**: tỉ lệ B1 trong *tập huấn luyện thực* giảm từ 78 % (số nhịp thô)
xuống **64,4 %** (số nhịp mô hình nhìn thấy mỗi epoch). Stride này có ghi trong chuỗi tài liệu
của `model/train_22.py` ("B1 stride 2 s, B2/PhysioNet stride 1 s") nhưng **chưa ở đâu nêu nó như
một biện pháp cân bằng nguồn** — nên viết rõ vào bài báo, kèm con số 78 % → 64 %.

**RỦI RO (suy luận).** 64,4 % tín hiệu giám sát đến từ nhãn **gián tiếp**, và mục 1.1 cho thấy
nhãn đó đã bị làm trơn. Mô hình sản xuất vì vậy chủ yếu học cách **đồng ý với một bộ dò QRS
khác**, không phải với điện cực da đầu. Đây là rủi ro thật, độc lập với kết quả F1.

**Bằng chứng đã có, chống lại cách diễn giải bi quan nhất:** mô hình m12 (bỏ **toàn bộ** B1)
đạt 67,93 trên 60 bản CinC sạch trong khi m22 đạt 74,28 (+6,35 KTC95 [+4,04; +8,95],
W p = 3,0e−08). Nghĩa là **B1 đóng góp thật**, không chỉ là dấu vân nhãn — dù nhãn gián tiếp,
nó vẫn dạy mô hình những thứ tổng quát hoá được sang một hệ ghi khác hẳn. Đồng thời trên 12
chủ thể nhãn trực tiếp, m12 và m22 **hoà nhau** (97,84 so với 97,89, KTC95 [−0,20; +0,09]) —
thêm B1 **không làm hỏng** khả năng khớp nhãn trực tiếp.

### 4.2 Hệ số cân bằng đề xuất

Nếu cân bằng để ba nguồn đóng góp **số nhịp bằng nhau** mỗi epoch, trọng số lấy mẫu cần là:

| Nguồn | hệ số |
|---|---|
| PhysioNet | × 2,322 |
| Silesia B2 | × 1,571 |
| Silesia B1 | × 0,517 |

(`dulieu_results.json → can_bang.he_so_can_bang_de_xuat`.) Đây chính là nhánh `bal` trong
thí nghiệm M4-mini; kết quả ở mục 3.3.

**Lưu ý quan trọng:** cân bằng theo *nguồn* sẽ khiến 5 chủ thể PhysioNet bị lấy mẫu lặp
~2,3 lần mỗi epoch. Với chỉ 5 sản phụ, đó là rủi ro quá khớp theo cá thể. Nếu số liệu cho thấy
cân bằng có ích, cấu hình an toàn hơn là **cân bằng một phần** (ví dụ √ của hệ số trên) hoặc
**trọng số mất mát** thay vì lấy mẫu lặp.

---

## 5. Đề xuất tăng cường dữ liệu — xếp hạng theo kỳ vọng

Chưa chạy phép nào dưới đây; đây là **phân tích và xếp hạng**, không phải kết quả.
Cột "biến thiên vật lý" nói rõ phép này mô phỏng hiện tượng lâm sàng có thật nào.

| # | Phép | Biến thiên VẬT LÝ có thật mà nó mô phỏng | Kỳ vọng | Rủi ro |
|---|---|---|---|---|
| 1 | **Trộn nhiễu THẬT từ bản ghi khác** (cộng phần dư sau khử mẹ của một sản phụ khác, hoặc nhiễu EMG/chuyển động từ `model/data/nstdb`) vào hàng gốc, tỉ lệ theo SNR mục tiêu | Nhiễu cơ tử cung, cử động mẹ, nhiễu điện cực — **phổ giống thật**, khác hẳn nhiễu trắng | **Cao**. Mục tiêu trực tiếp của 16/60 bản CinC F1 < 50; `snr_curve.json` cho thấy mô hình nhạy với SNR | Nếu lấy phần dư từ bản ghi có fQRS chưa khử sạch thì tiêm nhãn giả |
| 2 | **Đổi biên độ QRS mẹ** trước khi khử mẹ (nhân template mẹ ×0,5…×2 rồi cộng lại) | Tỉ lệ mQRS/fQRS thay đổi theo tuổi thai, vị trí điện cực, bề dày thành bụng — nguồn biến thiên **lớn nhất** giữa các sản phụ | **Cao**. Ép mạng bớt phụ thuộc vào khâu khử mẹ | Cần cài trước bước `cancel_maternal`, không phải sau |
| 3 | **Đảo cực / trộn kênh** (đổi dấu đạo trình, hoán vị 4 đạo trình) | Cực tính fQRS trên bụng phụ thuộc **ngôi thai** (đầu/mông) và vị trí điện cực; đây là biến thiên có thật và rất lớn | **Cao**, và **gần như miễn phí** | Không có; heatmap bất biến với đổi dấu |
| 4 | **Co giãn thời gian nhẹ** (resample ×0,92…×1,08, dịch nhãn theo) | Dải FHR sinh lý 110–160 bpm và nhịp nhanh/chậm bệnh lý; tập hiện tại chỉ có FHR trung vị 125–157 bpm — **thiếu hoàn toàn nhịp chậm < 110 và nhịp nhanh > 170** | **Trung bình–cao**. Bù đúng một lỗ hổng đã đo được | Co giãn cũng làm đổi độ rộng QRS thai, vốn là đặc trưng mô hình dùng |
| 5 | **Trộn hai bản ghi theo thời gian (mixup)**: nối hai nửa đoạn của hai sản phụ khác nhau | Biên độ/hình dạng fQRS đổi đột ngột khi điện cực dịch chuyển hoặc thai cử động | Trung bình | Tạo điểm nối không sinh lý; nên làm mờ chỗ nối |
| 6 | **Dịch tần số nhỏ** (±2–3 Hz) | Không mô phỏng hiện tượng lâm sàng nào rõ ràng; dải QRS thai 10–60 Hz ổn định | **Thấp — không khuyến nghị** | Làm hỏng quan hệ với chặn 50 Hz |
| 7 | **Trôi đường nền (đang dùng, phép c)** | Hô hấp, cử động — nhưng cộng SAU bộ lọc thông cao 10 Hz nên là nhiễu mà mạng **không bao giờ gặp lúc suy luận** | **Âm hoặc bằng 0 — nên bỏ, hoặc chuyển lên trước `M.preprocess`** | Gây lệch huấn luyện/suy luận |

**Khuyến nghị hành động:** chuyển (b) và (c) lên **trước** `M.preprocess` (hoặc bỏ (c)), thêm
#3 (đảo cực / hoán vị đạo trình, gần như miễn phí), rồi thử #1 và #2. Cả ba đều nhắm vào **biến thiên giữa các sản phụ**, là thứ mà 22 chủ thể không
đủ để bao phủ — tức là chúng cạnh tranh trực tiếp với việc "đi xin thêm dữ liệu" nhưng rẻ hơn
nhiều bậc.

---

## 6. Hạn chế

1. **Đường cong chỉ có 3 điểm.** Không thể phân biệt bão hoà với tăng theo log; hai dạng hàm
   hợp lý như nhau cho ngoại suy lệch nhau 4–9 điểm ở n = 50. Mọi con số ngoại suy trong mục 2
   phải đọc là gợi ý bậc độ lớn, không phải dự báo.
2. **Ba điểm trên đường cong không đồng nhất về giao thức.** m5 và m12 là checkpoint
   *production* (huấn luyện trên toàn bộ chủ thể của mình), còn điểm m22 trên trục trong miền
   là trung bình LOSO (19 chủ thể huấn luyện). Trục ngoài miền (CinC) thì đồng nhất — cả ba
   đều là production và cả ba đều chưa thấy 60 bản sạch.
3. **Thí nghiệm M4-mini quy mô nhỏ và công suất rất thấp** (2 epoch, 1/3 dữ liệu, ngưỡng cố
   định, n ≤ 8 chủ thể). Một kết quả "không khác biệt" ở đây **không** chứng minh tăng cường
   vô dụng — nó chỉ nói rằng hiệu ứng không lớn ở quy mô này. Kết luận chắc chắn đòi hỏi chạy
   lại đủ 11 fold ở quy mô sản xuất, tốn ~2,5 giờ mỗi nhánh.
4. **Ảnh hưởng của cờ 0 chỉ đo ở phía đánh giá**, chưa đo ở phía huấn luyện, và chỉ đo trên
   mô hình m5.
5. **Giả thuyết "nhãn B1 làm trơn khiến mô hình học tiên nghiệm nhịp quá đều" chưa được kiểm
   chứng** — mới chỉ có bằng chứng gián tiếp (pNN50 thấp bằng nửa, không khoảng trống nào).
6. **Phép quét chồng lấn có thể bỏ sót chồng lấn BỘ PHẬN hoặc BIẾN ĐỔI.** Vòng M4b đã thu hẹp
   lỗ hổng này (mục 0.1 và 0.3): quét lại ở 250 Hz trên **trọn** cửa sổ 60 s, **mọi** độ trễ,
   có cả kênh điện cực da đầu; và quét thêm bằng **cửa sổ con 10 s** có nhánh NULL để bắt chồng
   lấn bộ phận. Vẫn còn bỏ sót được: (a) bản ghi bị **biến đổi phi tuyến** (đổi tỉ lệ theo thời
   gian, lọc mạnh, đảo cực) — NCC tuyến tính không bắt được; (b) chồng lấn **ngắn hơn 10 s**;
   (c) chồng lấn với **Silesia B1/B2** chứ không phải với ADFECGDB — phép quét này chỉ so CinC
   với ADFECGDB, **chưa** so CinC với 22 chủ thể Silesia. Mục (c) là lỗ hổng thật và **chưa làm**.
7. **Chưa loại trừ khả năng một số sản phụ Silesia B1 (thai kỳ) và B2 (chuyển dạ) là CÙNG
   một người ghi ở hai thời điểm.** Phép quét NCC không phát hiện được điều này vì hai lần ghi
   khác buổi thì tín hiệu khác nhau hoàn toàn. Nếu có trùng người, giao thức "22 chủ thể độc lập"
   và các fold theo nhóm chủ thể sẽ bị rò rỉ theo cá thể. Cách kiểm duy nhất là hỏi tác giả bộ
   dữ liệu hoặc tìm trong bài Scientific Data 7:200 (2020); **nhóm chưa làm**.
8. **Chưa kiểm chồng lấn giữa 22 chủ thể huấn luyện với NInFEA và NIFEADB** (`model/data/ninfea`,
   `model/data/nifeadb`) — hai bộ này chưa dùng nên chưa gấp, nhưng phải làm trước khi dùng.
9. **(M4b) Bảng chọn kênh 60 bản sạch KHÔNG phải một phép đo mới.** Nó tính lại từ F1 từng
    bản ghi đã lưu trong `chonkenh_results.json`; mô hình không chạy lại. Nó thừa hưởng **mọi**
    hạn chế của M5, trong đó có việc `peakprob` là lựa chọn **hậu kiểm**. Việc hiệu ứng mạnh lên
    trên tập sạch **không** biến hậu kiểm thành tiền đăng ký.
10. **(M4b) Nhánh NULL dùng phép đảo ngược thời gian, không phải một mẫu ngẫu nhiên thật.**
    Đảo ngược giữ phổ và cấu trúc chuỗi QRS nhưng vẫn là **cùng những sản phụ đó**. Một nhánh
    null chặt hơn sẽ dùng bản ghi của nhóm nghiên cứu khác hẳn. Kết luận "không có chồng lấn bộ
    phận" vì vậy vững ở mức phù hợp với đối chứng này, không hơn.
11. **(M4b) Thí nghiệm tăng cường chỉ có 8 chủ thể** (cân bằng: 6) dù đã thêm fold 10 và 11 — xem mục 3.3.
    Không fold nào được chọn ngẫu nhiên: fold 4, 10, 11 được chọn **vì** chúng chứa các bản ghi
    khó đã biết. Đó là lựa chọn có chủ đích nhằm tăng phương sai quan sát được, và nó làm mẫu
    **không đại diện** cho 22 chủ thể. Hiệu số đo ở đây không suy rộng ra toàn tập được.
12. **Danh sách 15 bản ghi rò rỉ là kết quả của nhóm, chưa đối chiếu với y văn.** Nếu đã có công
   bố nào ghi nhận sự chồng lấn này thì phải trích dẫn; nhóm **chưa tìm**. Không được viết
   trong bài báo rằng đây là phát hiện của mình khi chưa kiểm.

---

## 7. Việc cần làm tiếp, xếp theo ưu tiên

1. **Sửa mọi con số CinC 2013** từ 75 bản ghi sang 60 bản sạch, và đưa `CINC_LEAKED_15` thành
   hằng số trong `benchmark_dpss/eval_cinc75.py`. Các vị trí đã xác định (tìm bằng
   `grep -rn "79,40\|79\.40\|86,87\|86\.87\|97,76\|7,47\|7\.47"`):

   | Tệp | Dòng |
   |---|---|
   | `README.md` | 111, 114, 129, 213, 483, 486 |
   | `README.vi.md` | 99, 102, 116, 197, 410, 446, 449 |
   | `paper/cinc2026/main.tex` | 70, 255, 265, 271, 289, 292, 399 |
   | `survey/facts_phase2.json` | 4, 5, 8, 11, 130, 147, 186, 200, 247, 248 |
   | `analysis/GATE22.md`, `analysis/LUONGCUC.md`, `analysis/ABLATION_B1.md` | mọi chỗ nhắc 79,40 / 86,87 / 97,76 |
2. **Huấn luyện m17** (bỏ 5 chủ thể B1) để có điểm thứ tư trên đường cong — ~30 phút CPU.
3. **Chạy lại đối chứng tăng cường ở quy mô sản xuất** (11 fold, 4 epoch, 2 luồng để tránh lỗi
   hết bộ nhớ đã gặp) nếu M4-mini cho thấy hiệu ứng đáng theo đuổi.
4. **Kiểm giả thuyết "tiên nghiệm nhịp quá đều"**: so phân bố ΔRR của đầu ra mô hình với nhãn
   điện cực da đầu trên B2/PhysioNet.
5. **Sửa vị trí áp tăng cường**: cộng nhiễu (b) và trôi đường nền (c) TRƯỚC `M.preprocess`,
   hoặc bỏ (c); thêm đảo cực / hoán vị đạo trình.
6. **(MỚI, vòng M4b — ưu tiên cao)** Mọi con số của nhiệm vụ **M5 chọn kênh** phải thay bằng
   bản tính trên 60 bản sạch (mục 0.2): peakprob **+7,73** chứ không phải +6,20; gate **+6,44**
   chứ không phải +5,14; dư địa oracle **9,32** chứ không phải 7,47. Kết luận định tính
   **không đổi**: `peakprob` và `gate4` sống sót Holm cả trước lẫn sau khi làm sạch; `gate` —
   quy tắc quyết định tiền đăng ký — có Holm p = **0,0505** và **vẫn không sống sót**. Không
   được làm tròn xuống 0,05, và không được dùng việc làm sạch để nâng cấp mức bằng chứng.
7. **(MỚI) Quét chồng lấn CinC ↔ Silesia B1/B2.** Mục 0.1 và 0.3 chỉ so CinC với **ADFECGDB**.
   Chưa ai so CinC với 22 chủ thể Silesia. Vì Silesia và ADFECGDB là **cùng một nhóm nghiên cứu**,
   khả năng CinC cũng chứa đoạn Silesia là có thật. Chi phí ~10 phút CPU với chính
   `analysis/dulieu_m4b_partial.py` (đổi tập tham chiếu). **Phải làm trước khi nộp bài.**
8. **(MỚI) Mọi phép quét chồng lấn về sau phải kèm nhánh NULL.** Mục 0.3 cho thấy quét cửa sổ
   con không có ngưỡng tiên nghiệm: nhánh clean và nhánh null đều có trung vị \|NCC\| ≈ 0,83 và
   max ≈ 0,95. Một phép quét không đối chứng sẽ báo động giả 12/60 bản.

---

## Phụ lục A — kiểm toán nhãn từng chủ thể (22 chủ thể huấn luyện)

Nguồn: `analysis/dulieu_audit.json → labels`.

| Chủ thể | nhãn | giây | nhịp | FHR trung vị (bpm) | RR min–max (ms) | RR ngoài dải (%) | nhảy >25 % (%) | khoảng trống >2 s | pNN50 (%) | cờ 0 |
|---|---|---|---|---|---|---|---|---|---|---|
| r01 | trực tiếp | 300 | 644 | 127.7 | 400–769 | 0.311 | 0.623 | 0 (0.0 s) | 0.62 | 0 |
| r04 | trực tiếp | 300 | 632 | 125.5 | 408–588 | 0.000 | 0.000 | 0 (0.0 s) | 0.00 | 0 |
| r07 | trực tiếp | 300 | 627 | 126.1 | 462–524 | 0.000 | 0.000 | 0 (0.0 s) | 0.00 | 0 |
| r08 | trực tiếp | 300 | 651 | 129.3 | 397–805 | 0.462 | 0.924 | 0 (0.0 s) | 0.92 | 0 |
| r10 | trực tiếp | 300 | 637 | 131.6 | 41–4905 | 0.786 | 1.260 | 3 (11.0 s) | 1.26 | 0 |
| B1_01 | trực tiếp | 1198 | 3120 | 155.4 | 348–778 | 0.032 | 0.064 | 0 (0.0 s) | 0.06 | 2 |
| B1_02 | trực tiếp | 1198 | 2804 | 142.2 | 372–552 | 0.000 | 0.000 | 0 (0.0 s) | 0.04 | 13 |
| B1_03 | trực tiếp | 1198 | 2565 | 126.6 | 370–546 | 0.000 | 0.000 | 0 (0.0 s) | 0.00 | 8 |
| B1_04 | trực tiếp | 1198 | 2774 | 138.9 | 360–486 | 0.000 | 0.000 | 0 (0.0 s) | 0.00 | 0 |
| B1_05 | trực tiếp | 1198 | 2770 | 138.9 | 384–496 | 0.000 | 0.000 | 0 (0.0 s) | 0.00 | 6 |
| B1_06 | trực tiếp | 1198 | 2889 | 144.9 | 382–470 | 0.000 | 0.000 | 0 (0.0 s) | 0.00 | 10 |
| B1_07 | trực tiếp | 1198 | 3114 | 157.1 | 340–648 | 0.000 | 0.064 | 0 (0.0 s) | 0.22 | 18 |
| B1_08 | trực tiếp | 1198 | 2911 | 146.3 | 350–558 | 0.000 | 0.000 | 0 (0.0 s) | 0.17 | 14 |
| B1_09 | trực tiếp | 1198 | 2866 | 143.5 | 276–550 | 0.000 | 0.140 | 0 (0.0 s) | 0.21 | 50 |
| B1_10 | trực tiếp | 1198 | 2592 | 135.1 | 376–778 | 1.119 | 0.116 | 0 (0.0 s) | 1.70 | 9 |
| B2_03 | trực tiếp | 300 | 716 | 157.1 | 281–4276 | 0.699 | 1.541 | 2 (6.7 s) | 1.68 | 0 |
| B2_04 | trực tiếp | 300 | 681 | 136.1 | 393–1484 | 0.441 | 0.589 | 0 (0.0 s) | 0.74 | 0 |
| B2_05 | trực tiếp | 300 | 660 | 128.5 | 303–740 | 0.303 | 0.760 | 0 (0.0 s) | 0.91 | 0 |
| B2_06 | trực tiếp | 300 | 684 | 137.0 | 389–510 | 0.000 | 0.000 | 0 (0.0 s) | 0.00 | 0 |
| B2_08 | trực tiếp | 300 | 645 | 129.0 | 420–502 | 0.000 | 0.000 | 0 (0.0 s) | 0.00 | 0 |
| B2_09 | trực tiếp | 300 | 674 | 135.7 | 417–507 | 0.000 | 0.000 | 0 (0.0 s) | 0.00 | 0 |
| B2_12 | trực tiếp | 300 | 657 | 131.9 | 425–484 | 0.000 | 0.000 | 0 (0.0 s) | 0.00 | 0 |
