# THẨM ĐỊNH ĐỘC LẬP VÒNG 6 — RelyFetal

**Người thẩm định:** phản biện độc lập (không phải tác giả của bất kỳ kết quả nào dưới đây)
**Ngày:** 2026-09-12
**Phạm vi:** năm kết quả M1 (chẩn đoán mô hình), M2 (kiến trúc), M3 (thích nghi miền),
M4 (dữ liệu), M5 (chọn kênh)
**Nguyên tắc:** mọi con số dưới đây được đọc lại từ tệp JSON gốc trên đĩa. Tôi **không** dùng
bản tóm tắt do các agent cung cấp. Chỗ nào tôi tự tính lại, tôi ghi rõ "tôi tính lại".

---

## 0. Kết luận một đoạn

Vòng này **trung thực một cách bất thường**. Ba trong năm agent tự tố cáo lỗi của chính mình
trước khi tôi kịp tìm ra: M5 tự khai rằng quy tắc tiền đăng ký chỉ ra `gate` chứ không phải
`peakprob`, M1 tự khai một vòng lặp định nghĩa, M3 tự khai thất bại hoàn toàn. Đây là điều
hiếm và nên được ghi nhận.

Nhưng vòng này cũng chứa **một phát hiện làm thay đổi mọi con số ngoài miền đã công bố**
(M4: 15/75 bản ghi CinC là bản sao nguyên văn của dữ liệu huấn luyện), và **một kết quả
tiền đăng ký thực chất đã trượt** mà chưa ai nói thẳng ra (M5: quy tắc `gate` được tiền đăng ký
có p_Holm = 0,085 trên 75 bản và 0,051 trên 60 bản sạch — **không** đạt mức 5%).

**89 con số được kiểm; 88 khớp; 1 không khớp; 0 không tìm thấy.**

---

## VIỆC 1 — ĐỐI CHIẾU TỪNG CON SỐ VỚI TỆP GỐC

### 1.1 Bảng tổng

| Nhiệm vụ | Số con số kiểm | Khớp | Không khớp | Không tìm thấy |
|---|---:|---:|---:|---:|
| M5 chọn kênh | 15 | 14 | 1 | 0 |
| M4 dữ liệu | 17 | 17 | 0 | 0 |
| M1 chẩn đoán | 32 | 32 | 0 | 0 |
| M2 kiến trúc | 15 | 15 | 0 | 0 |
| M3 thích nghi | 10 | 10 | 0 | 0 |
| **Tổng** | **89** | **88** | **1** | **0** |

### 1.2 Con số DUY NHẤT không khớp

**M5, giá trị p của `peakprob` − `psd` trên CinC 75.**

* Bản tóm tắt nói: `p = 3,81e-04`
* `analysis/chonkenh_results.json` → `bang.cinc.peakprob.wilcoxon_p` = **7,696e-04**
* `analysis/CHONKENH.md` dòng 81 cũng ghi **7,7e-04**
* Chuỗi `3,81e` / `3.81e-04` **không xuất hiện ở bất kỳ đâu** trong `analysis/*.md` hay
  `chonkenh_results.json` (tôi đã grep).

Nhận xét: 7,696e-04 / 2 = 3,85e-04, gần nhưng không bằng 3,81e-04. Có thể là một biến thể
một phía được tính ở đâu đó rồi truyền miệng. **Con số đúng để đưa vào bài báo là
p = 7,7e-04 (Wilcoxon hai phía), p_Holm = 5,4e-03.** Tệp trên đĩa đúng; bản tóm tắt sai.
Đây là lỗi truyền đạt, không phải lỗi phân tích — nhưng nó cho thấy vì sao phải đọc tệp.

### 1.3 Bốn con số KHỚP nhưng bị ĐẶT SAI KHUNG

Những con số này có thật trong JSON, nhưng nhãn mà bản tóm tắt gắn cho chúng không đúng
phạm vi. Không phải bịa số, nhưng nếu bê nguyên vào bài báo thì sai.

| Con số | Bản tóm tắt nói | Thực tế trong tệp |
|---|---|---|
| B2_03 "13,1 điểm dư địa" | trần hợp nhất − kênh tốt nhất | 98,01 − **84,87** (gộp bỏ phiếu), không phải 98,01 − 83,91 (= **14,1**) |
| Jitter "3,76 ms trung vị" | jitter chung | `peakprob_67` — tức đã **loại 8 bản khó**. Trên đủ 75 bản, quy tắc psd: trung vị **6,01 ms**; peakprob: **4,01 ms** |
| Mức ngẫu nhiên nhóm (a) "15,2 / 11,2" | mức ngẫu nhiên chung | mức ngẫu nhiên **của riêng peakprob** (15,24 / 11,23). Của psd là 14,66 / 10,26 |
| "68/75 bản CinC có đỉnh 60 Hz mà front-end chỉ chặn 50 Hz" | ngụ ý đây là nguyên nhân | Đúng 68/75 có 60 Hz — **nhưng cả 75/75 đều có 50 Hz**, và chính M3 đã thử chặn 60 Hz: **+0,19 điểm, p = 0,60**. Giả thuyết này đã bị chính M3 bác bỏ |

Kết luận VIỆC 1: **dữ liệu trên đĩa đáng tin.** Không có dấu hiệu bịa số. Sai sót nằm ở
khâu tóm tắt và đặt khung, không ở khâu tính toán.

---

## VIỆC 2 — DANH SÁCH KIỂM LỖI PHƯƠNG PHÁP

### (a) RÒ RỈ NHÃN

**M5 — SẠCH, đã kiểm bằng thực nghiệm.**
`analysis/chonkenh_leakcheck.py` thay nhãn thật bằng nhãn ngẫu nhiên rồi chạy lại: **0/776
lựa chọn đổi** (8 quy tắc × 97 bản ghi). Đối chứng dương cho thấy phép thử đủ nhạy (F1 từng
kênh của a01 tụt từ [100,0; 81,0; 40,6; 96,2] xuống [24,8; 24,7; 15,9; 22,2]).
Siêu tham số duy nhất (k của quy tắc hợp nhất) chốt trên 22 chủ thể rồi áp nguyên sang CinC —
tôi xác nhận `k_hop_nhat_chon_tren_22 = 2` trong JSON.
*Giới hạn mà chính M5 đã nêu (mục 4.5) và tôi đồng ý:* phép thử chỉ chứng minh **bước chọn**
mù nhãn; việc **chấm điểm** mù nhãn thì phải tin mã nguồn. Tôi đã đọc: cổng chỉ nhận `seg_feat`
(12 SQI), không đặc trưng nào chạm nhãn. Chấp nhận được.

**M3 — SẠCH, và đây là điểm mạnh nhất của M3.**
`adapt_results.json.sieu_tham_so.quy_tac_chon` ghi rõ: bề mặt quyết định là `hp_m12_to_B1`
(mô hình 12 chủ thể → 10 chủ thể B1), **"KHONG dung bat ky mau nao cua CinC 2013"**.
Cấu hình chốt (`tent`: lr 1e-3, 30 bước; `pl`: lr 1e-4, 40 bước, conf 0,9) được chọn ở đó
rồi áp thẳng. Nhãn CinC chỉ chạm vào ở bước chấm điểm cuối. **Đây là thiết kế đúng sách.**

**M4 — KHÔNG có rò rỉ nhãn, nhưng PHÁT HIỆN rò rỉ DỮ LIỆU.** Xem (a-bis) ngay dưới.

**M1 — có một chỗ dùng nhãn để định nghĩa nhóm.** M1 tự khai. Xem (g).

**M2 — sạch.** Ngưỡng chọn trên chủ thể val riêng của từng fold (`protocol` trong `run_meta`).

### (a-bis) PHẢN BIỆN NGHIÊM KHẮC PHÁT HIỆN NCC = 1,0000 CỦA M4

Đây là phát hiện quan trọng nhất của cả vòng, nên tôi công kích nó bằng mọi cách tôi nghĩ ra.

**Bốn giả thuyết "NCC = 1,0000 là giả tạo" và vì sao cả bốn đều bị bác:**

1. **"Do cùng một bộ nạp / cùng một mảng bị so với chính nó."**
   *Bác.* Có **hai cài đặt độc lập**: `analysis/dulieu_audit.py` và
   `analysis/dulieu_m4b_verify.py`. Tệp thứ hai ghi ở đầu: *"Viet lai TU DAU, KHONG dung lai
   ham nao cua analysis/dulieu_audit.py"*, và nó nạp ADFECGDB bằng **`mne.io.read_raw_edf`
   từ tệp .edf** còn CinC bằng **`wfdb.rdrecord` từ .dat**. Hai thư viện khác nhau, hai định
   dạng tệp khác nhau, hai cây thư mục khác nhau (`model/data/adfecgdb` vs
   `benchmark_dpss/pcdb`). Không có đường nào để cùng một mảng tự so với chính nó.
   Hai cài đặt cho **cùng 15 bản ghi, cùng bản ghi gốc, cùng cửa sổ 60 s**.

2. **"Do chuẩn hoá (z-score) làm mọi thứ trông giống nhau."**
   *Bác bằng đối chứng.* Nếu chuẩn hoá tự sinh ra NCC = 1, thì **đối chứng dương cũng phải
   bằng 1**. Nó không: các cặp trùng đã biết B2↔PhysioNet cho **0,8555 – 0,9842**
   (B2_01~r01 = 0,8603; B2_02~r10 = 0,9842; B2_07~r04 = 0,9556; B2_10~r07 = 0,9593;
   B2_11~r08 = 0,8555). Cùng một phép chuẩn hoá, cùng một hàm, ra số **khác 1**. Vậy giá trị
   1,0000 mang thông tin thật, không phải sản phẩm của chuẩn hoá.

3. **"Do cắt đoạn 60 s ngắn nên dễ trùng ngẫu nhiên."**
   *Bác bằng đối chứng âm.* 60 bản ghi CinC còn lại, cùng phép đo, cùng độ dài 60 s, quét mọi
   độ trễ: |NCC| tối đa **0,4418** (bản kiểm chính) / **0,6155** (bản kiểm độc lập).
   Khoảng cách 0,44 → 1,00 không phải là chuyện may rủi.

4. **"Do làm tròn."**
   *Đã kiểm, và đúng là có làm tròn:* `dulieu_m4b_verify.py` dòng 92 ghi `ncc=round(v,4)`.
   Nên "1,0" thực ra là |NCC| ≥ 0,99995. **Điều này không cứu được gì** — 0,99995 giữa hai
   tệp tải từ hai nguồn khác nhau vẫn có nghĩa là cùng một tín hiệu, chỉ sai khác ở lượng tử
   hoá. Và độ lệch RR **= 0,0 ms** (không phải "xấp xỉ 0") trên cả 15 bản củng cố điều đó.

**Bằng chứng mà bản kiểm độc lập tìm ra còn MẠNH HƠN bản gốc** — và đây là chi tiết khiến tôi
tin hoàn toàn: không phải **một** kênh trùng, mà **cả bốn** kênh của mỗi bản CinC rò rỉ đều là
bản sao NCC = 1,0000 của `Abdomen_1..4` **đúng thứ tự** (`cinc_ch k → Abdomen_(k+1)`). Và
**mỗi bản ADFECGDB đóng góp đúng ba cửa sổ: 0–60 s, 120–180 s, 240–300 s.** Một cấu trúc đều
đặn như vậy không thể là trùng hợp thống kê; nó là dấu vết của một quy trình cắt dữ liệu.

**Một cách giải thích khác mà tôi PHẢI nêu ra, và nó KHÔNG cứu được tình hình:**
Có thể CinC 2013 set-a *về mặt xuất xứ* hợp pháp có chứa bản ghi ADFECGDB (ban tổ chức thách
thức lấy dữ liệu từ nhiều nguồn công khai). Nếu vậy thì đây **không phải lỗi của nhóm** — nhóm
không làm gì sai, chỉ là hai bộ dữ liệu công khai chồng nhau mà không ai ghi chú.
**Nhưng hệ quả kỹ thuật y hệt:** mô hình `fetalqrs_tcn_22_production.pt` được huấn luyện trên
cả 22 chủ thể, trong đó **có r01, r04, r07, r08, r10** (tôi xác nhận trong
`chonkenh_results.json.chan_doan_psd.s22` và trong `kientruc_results.json.meta.folds`).
Vậy 15/75 bản ghi "ngoài miền" nằm trong tập huấn luyện. **Đó vẫn là rò rỉ, bất kể lỗi của ai.**
Cách diễn đạt đúng trong bài báo là mô tả sự chồng lấn như một **đặc tính của dữ liệu công
khai** và báo cáo con số trên 60 bản sạch, chứ không phải tự nhận lỗi.

**Phán xử: phát hiện NCC = 1,0000 ĐỨNG VỮNG. Tôi không tìm được cách bác.**
Đây là kết quả có giá trị nhất của cả vòng — nó vừa là đóng góp cho cộng đồng (chưa thấy ai
ghi chú sự chồng lấn này), vừa buộc nhóm tự hạ con số của chính mình. Cả hai đều đáng khen.

**Mức đo phóng đại** (`chong_lan.thoi_phong`): m5 **+7,18** · m12 **+6,41** · m22 **+5,12** ·
oracle **+3,27** điểm. Tức mọi con số CinC đã công bố bị thổi lên 3–7 điểm.

**Một mâu thuẫn nhỏ giữa hai bản kiểm của chính M4:** |NCC| tối đa trên 60 bản còn lại là
0,4418 (bản gốc, tín hiệu đã lọc) vs 0,6155 (bản độc lập, tín hiệu thô). Không ảnh hưởng kết
luận (cả hai đều cách xa 1,0), nhưng **bài báo phải ghi một con số và nói rõ nó đo trên tín
hiệu thô hay đã lọc.** Tôi đề nghị dùng 0,62 (thô) vì đó là con số bảo thủ hơn.

### (b) CHỌN HẬU KIỂM — M5

**M5 có báo cáo trung thực không? CÓ, và báo cáo rất tốt.**
`analysis/CHONKENH.md` mục 4.1 (dòng 156) viết nguyên văn:
*"Quy tắc quyết định đã khai báo trước chỉ ra `gate`, KHÔNG phải `peakprob`."*
Mục 4.2 (dòng 162) còn tự phê bình gay gắt hơn tôi định viết: *"Chọn `gate` thay vì `rrcv` là
chọn theo nhiễu. Thiết kế khai báo trước của tôi ở điểm này **sai**: tôi đã giao vai trò trọng
tài cho một nhánh đã chạm trần."* Mục 193–194 khuyến nghị báo cáo **cả hai** con số.
**Không có gì bị giấu.** Đây là chuẩn mực tôi mong thấy ở mọi vòng sau.

**NHƯNG — điều M5 chưa nói thẳng, và đây là phát hiện của tôi:**

| quy tắc | CinC 75: hiệu | p Wilcoxon | **p_Holm** | CinC 60 sạch: hiệu | p Wilcoxon | **p_Holm** |
|---|---:|---:|---:|---:|---:|---:|
| `gate` *(tiền đăng ký)* | +5,14 | 0,017 | **0,085** ✗ | +6,44 | 0,010 | **0,0505** ✗ |
| `peakprob` *(hậu kiểm)* | +6,20 | 7,7e-04 | **0,0054** ✓ | +7,73 | 5,6e-04 | **0,0039** ✓ |

**Phép thử xác nhận đã được tiền đăng ký — `gate` — KHÔNG sống sót hiệu chỉnh Holm, trên cả
hai quần thể.** 0,085 và 0,0505. Điều này chưa từng được phát biểu thẳng ở đâu. Nếu đọc khai
báo trước theo nghĩa nghiêm ngặt nhất, **kết quả xác nhận của M5 là THẤT BẠI.**

*Nhưng khai báo trước tự mâu thuẫn ở chính điểm này*, và tôi phải công bằng:
`khai_bao_truoc.quy_tac_quyet_dinh_chinh` nói *"Kết quả CinC 75 của chính quy tắc đó là phép
thử XÁC NHẬN **duy nhất** được coi là có giá trị suy diễn"* — tức **một** phép thử, không cần
Holm, và khi đó `gate` đạt p = 0,017 ✓. Nhưng `khai_bao_truoc.chi_so_bao_cao` lại liệt kê
*"Holm hiệu chỉnh đa so sánh trên 6 quy tắc mới"*. Hai điều khoản này không thể cùng đúng.
**Bản thân sự mâu thuẫn trong khai báo trước là một lỗi phương pháp**, và nó phải được thú
nhận trong bài báo chứ không được dùng để chọn cách đọc có lợi hơn.

**Lập luận bào chữa của M5 (mục 4.3) — tôi kiểm và thấy nó ĐÚNG.**
M5 lập luận: `peakprob` **nằm trong danh sách 7 quy tắc đã khai báo trước**, và hiệu ứng của
nó sống sót Holm trên **toàn bộ 7** (p_Holm = 0,0054). Nghĩa là ngay cả khi coi việc chọn
`peakprob` là hoàn toàn hậu kiểm trong họ đã khai báo, kết luận vẫn đứng ở mức 5%.
**Về mặt thống kê đây chính xác là phép hiệu chỉnh đúng** cho thao tác "chọn cái tốt nhất
trong một họ đã định trước sau khi nhìn dữ liệu" — nó khống chế FWER của toàn bộ thao tác.
Và nó còn đứng vững trên 60 bản sạch (p_Holm = 0,0039). **Tôi chấp nhận lập luận này.**

*Chỗ hở còn lại:* họ Holm được tính trên **7 quy tắc × 1 quần thể**. Trong thực tế M5 báo cáo
**3 quần thể** (75 / 68 / 60). Nếu tính chặt thì họ lớn hơn. Tôi kiểm và thấy điều này **không
lật kết luận**: p_Holm của `peakprob` là 0,0054 (75 bản) và 0,0039 (60 bản) — nhân 3 vẫn dưới
0,05. Ghi vào phần hạn chế là đủ.

**Kiểm mốc thời gian tệp khai báo trước — ĐÂY LÀ CHỖ YẾU THẬT SỰ.**

```
10:33:46  chonkenh_cache.py          (viết script)
10:33:57  chonkenh_cache/cinc_a01.json  ← bắt đầu sinh bộ nhớ đệm F1 TỪNG KÊNH của CinC
10:35:59  chonkenh_khaibao_truoc.json   ← KHAI BÁO TRƯỚC được ghi
10:36:14  chonkenh_cinc_log.txt         ← log F1 4 kênh × 75 bản ghi HOÀN TẤT (15 s SAU)
10:38:38  chonkenh_rules.py          (viết script quy tắc)
10:40:11  chonkenh_rules_log.txt     (bắt đầu chạy quy tắc)
10:47:12  chonkenh_results.json      (kết quả)
```

Ba nhận xét:

1. **Khai báo trước được ghi TRƯỚC khi chạy bất kỳ quy tắc nào** (10:36 vs 10:40). Điều nhóm
   tự nhận (`ghi_chu_thu_tu`) là đúng theo đúng câu chữ.
2. **Nhưng nó được ghi SAU khi F1 từng kênh của CinC đã gần xong** — bộ nhớ đệm bắt đầu từ
   10:33:57, khai báo lúc 10:35:59, log hoàn tất 10:36:14. Tức là **dư địa oracle và danh tính
   kênh tốt nhất trên CinC đã nằm trên đĩa (hoặc sắp nằm) tại thời điểm khai báo.** Không có
   cách nào chứng minh tác giả chưa nhìn. Nhóm có thú nhận một phần (*"Chỉ số chẩn đoán của
   VIỆC 1 được tính từ `benchmark_dpss/eval_cinc75.json` đã có sẵn từ vòng trước"*) — tức họ
   **thừa nhận** đã biết tình hình CinC khi viết khai báo.
3. **Tệp khai báo trước KHÔNG nằm trong git** (`git log --follow` trả về rỗng; `git status`
   cho thấy toàn bộ `analysis/` là `??` chưa theo dõi). **Bằng chứng duy nhất là mtime, mà
   mtime có thể sửa được bằng một lệnh.** Với một bài báo Q1, đây không phải là tiền đăng ký
   theo nghĩa được chấp nhận.

**Phán xử (b):** M5 trung thực về **nội dung**, nhưng từ "tiền đăng ký" đang bị dùng quá mạnh.
**Bài báo không được dùng chữ "pre-registered" / "tiền đăng ký".** Cách nói đúng: *"kế hoạch
phân tích được cố định và ghi ra tệp trước khi đánh giá bất kỳ quy tắc nào, nhưng sau khi F1
cơ sở từng kênh đã biết; tệp không được chốt bằng dấu thời gian bên thứ ba."*
**Từ vòng sau: `git commit` tệp khai báo trước, hoặc đăng lên OSF, trước khi chạy.** Chi phí
30 giây, giá trị rất lớn.

### (c) GIẢ LẬP — nhiều đạo trình / nhiều đoạn của CÙNG một sản phụ

**ĐÂY LÀ LỖI CHƯA AI TÌM RA, và nó nằm ngay trong phát hiện của M4.**

M4 chứng minh **mỗi bản ghi ADFECGDB đóng góp đúng 3 cửa sổ** vào CinC set-a:
r01 → a04, a05, a22 · r04 → a13, a20, a25 · r07 → a19, a23, a24 ·
r08 → a08, a15, a17 · r10 → a03, a12, a14.

**Hệ quả mà M4 chưa rút ra:** 15 bản ghi đó **không phải 15 sản phụ, mà là 5 sản phụ**.
Vậy CinC 75 có **nhiều nhất 65 chủ thể khác biệt**, không phải 75. Nhưng:

* M5 tính KTC bằng **cluster bootstrap lấy mẫu lại BẢN GHI** (`chi_so_bao_cao`: *"KTC 95%
  cluster bootstrap 10000 lần (lấy mẫu lại bản ghi)"*) — **bản ghi, không phải chủ thể**.
* Wilcoxon ghép cặp cũng trên n = 75 bản ghi.

Với 15 bản ghi chỉ đến từ 5 sản phụ, **n hiệu dụng nhỏ hơn 75**, nên **mọi KTC trên 75 bản
ghi đều hẹp hơn sự thật và mọi p đều nhỏ hơn sự thật.** Đây đúng là giả lập (pseudoreplication).

**May mắn: lỗi này tự biến mất khi chuyển sang 60 bản sạch** — vì 15 bản vi phạm chính là 15
bản bị loại. **Đây là một lý do độc lập, thuần thống kê, để báo cáo trên 60 bản sạch**, bên
cạnh lý do rò rỉ. Tôi cho đây là lập luận mạnh nhất để chốt việc dùng 60 bản.

**Rủi ro còn lại chưa ai kiểm:** *60 bản còn lại có thật sự là 60 sản phụ khác nhau không?*
NCC tối đa 0,44–0,62 giữa chúng chỉ loại trừ **trùng nguyên văn**; nó **không** loại trừ
"cùng sản phụ, buổi đo khác" hay "cùng sản phụ, đoạn không chồng nhau". Đây là **giả định chưa
được kiểm** và phải ghi vào phần hạn chế.

**Các nhiệm vụ khác:** M2 (`unit = "chu the (n=22)"`), M3 (`per_subject`, n = 22),
M1 (22 chủ thể) đều thống kê ở mức chủ thể trong miền — **đúng**. Vấn đề chỉ ở nhánh CinC.

### (d) SO SÁNH KHÔNG CÔNG BẰNG — M2

**Kiểm và KHÔNG tìm thấy lỗi.** `kientruc_results.json.meta.run_meta`:
`seed = 0`, `n_folds = 3`, `epochs = 3`, `batch_size = 16`, cùng `stride`, cùng
`tolerance_ms = 50`, cùng giao thức (*"ngưỡng trên chủ thể val riêng; kênh PSD mù nhãn"*).
`meta.folds` liệt kê **đúng cùng 3 fold, cùng danh sách test/val/train** cho mọi kiến trúc.

Tham số: 113 481 / 114 493 / 114 943 / 114 247 / 114 886 / 116 514 / 116 011.
Lệch tối đa **2,673 %** (rf_wide). Khớp với "chênh < 2,7 %". **Công bằng.**

**Nhưng có ba vấn đề khác mà tôi tìm thấy:**

1. **Giao thức bị thu nhỏ mạnh.** `run_meta.scale_down` ghi rõ: *"3 fold (không phải 11),
   stride 4s/8s (không phải 1s/2s), không tăng cường, 3 epoch, batch 16"*. **3 epoch.**
   Kết luận "tcn ≡ rf_wide ≡ tcn_ms" được rút ra từ một chế độ **huấn luyện thiếu**. Ở chế độ
   thiếu huấn luyện, các kiến trúc có xu hướng hội tụ về nhau; khác biệt chỉ lộ ra khi huấn
   luyện đủ. Kết luận tương đương **chưa được chứng minh cho mô hình sản xuất**.
2. **Chỉ một hạt giống (seed 0).** Mọi hiệu số nhỏ hơn 1 điểm ở đây không có ước lượng phương
   sai theo hạt giống. Với `rf_wide` −0,0087 điểm, không thể phân biệt "tương đương" với
   "may mắn ở seed 0".
3. **`cnn_wide` là KHÔNG XÁC ĐỊNH, không phải "tương đương".** Wilcoxon Holm = 0,296 (không
   khác biệt) **và** TOST Holm = 1,0 (không tương đương). Nghĩa là dữ liệu **không đủ để kết
   luận gì** về cnn_wide. Lập luận "khoảng cách là do bề rộng ngữ cảnh chứ không do họ kiến
   trúc" dựa trên việc nới RF của cnn_l từ 60 ms → 1508 ms thu hẹp khoảng cách từ −3,10 xuống
   −0,80, tức **lấp được 74 %**. Đó là bằng chứng tốt, nhưng **26 % còn lại chưa được giải
   thích** và không được nói thành "bằng 0".

**Biên tương đương TOST = 1,0 điểm F1** (`meta.margin_F1`). Trên nền F1 trung bình 97,6 với
dư địa oracle chỉ ~1,0 điểm, **biên 1,0 điểm lớn bằng toàn bộ dư địa còn lại**. Nói "tương
đương trong ±1,0 điểm" ở đây gần như không ràng buộc gì. Biên phải được biện minh trên tiêu
chí lâm sàng, không phải chọn cho tiện.

### (e) TRẦN F1

**Có và nghiêm trọng — nhưng M2 đã xử lý đúng, M1 thì chưa.**

* **M2 — đã làm trên thang logit.** `comparisons.*.all22` có `logit_diff` và `logit_ci95`
  cho **mọi** kiến trúc. Tôi kiểm: cnn_l `logit_diff` = −1,638 [−2,086; −1,157]; unet1d
  −0,804 [−1,169; −0,427]; **cnn_wide −0,447 [−0,745; −0,156] — KTC logit KHÔNG chứa 0**,
  trong khi KTC trên thang F1 thô [−2,40; +0,13] **có** chứa 0. **Thang logit cho kết luận
  MẠNH HƠN và ngược chiều với thang thô.** Tương tự rf_narrow: logit [−0,675; +0,117] chứa 0
  còn thô [−1,73; +0,068] cũng chứa 0.
  **→ Bài báo phải dùng thang logit cho M2, không phải F1 thô.** Kết luận đổi: `cnn_wide`
  thực ra **kém hơn TCN một cách có ý nghĩa** trên thang logit. Lập luận "bề rộng ngữ cảnh
  giải thích tất cả" **yếu đi** khi đo đúng cách.

* **M1 — KHÔNG làm trên logit, và cần làm.** Nhánh 22 chủ thể có trung vị 99,81 và 14/22 chủ
  thể **đạt đúng oracle**, dư địa chỉ 1,08 điểm. Mọi so sánh trong vùng đó bị trần bóp méo.
  M1 tự nhận điều này ở mục 4.2 tương ứng của M5, nhưng **không tính lại trên logit**.

* **M5 — bị trần ở nhánh 22 chủ thể, và ĐÂY LÀ NGUYÊN NHÂN GỐC của toàn bộ vấn đề (b).**
  Bốn quy tắc đứng đầu cách nhau **0,04 điểm** (98,61 / 98,60 / 98,58 / 98,57). Chính vì
  nhánh trọng tài chạm trần mà nó chọn sai quy tắc. **Nếu M5 so trên thang logit ở nhánh 22
  chủ thể, rất có thể thứ hạng đã khác** và toàn bộ tranh cãi gate/peakprob đã không xảy ra.
  **Đây là việc nên làm lại — rẻ và có thể lật kết luận.**

### (f) n NHỎ

Bốn chỗ kết luận được phát biểu mạnh hơn mức n cho phép:

1. **Trần năng lực (M1) — n = 4 bản ghi, TRONG MẪU, một hạt giống.**
   `chandoan_capacity.json.meta`: `subset = ["r01","B2_12","B2_03","B1_07"]`, `epochs = 8`,
   và ghi chú của chính M1: *"ngưỡng chọn TRONG MẪU → F1 trong mẫu là CHẶN TRÊN"*.
   Nhân 4 lần tham số (113 481 → 450 961) chỉ được +0,26 điểm **trong mẫu**, và gần như toàn
   bộ rơi vào B2_03 (96,55 → 97,51).
   **Phê bình của tôi:** một mô hình lớn gấp 4 lần *lẽ ra phải* khớp trong mẫu tốt hơn nhiều.
   Việc nó không khớp được nói lên rằng **phần lỗi còn lại trong mẫu là nhiễu/lỗi nhãn không
   thể giảm** — chứ **không** nói lên rằng năng lực đã bão hoà cho việc **tổng quát hoá ngoài
   miền**. Đây là hai mệnh đề hoàn toàn khác nhau. Với n = 4 bản ghi trong mẫu, kết luận
   "không cần mô hình lớn hơn" **không được chứng minh cho CinC**.

2. **"3 bản khó" (M1) — n = 3.** `gate` 92,95 = oracle 92,95; peakprob 90,05.
   **Và bản tóm tắt bỏ sót: `rrcv` cũng đúng 92,95.** Vậy không phải "gate bằng oracle" mà
   **"gate và rrcv cùng bằng oracle"**. Trên n = 3 chủ thể, đây là **giai thoại, không phải
   bằng chứng**, và tuyệt đối không được dùng để chọn quy tắc chính của bài báo.

3. **"RF bão hoà ở 1,5 s" (M2) — dựa trên 3 điểm lưới** (748 / 1516 / 3052 ms). Ba điểm
   không xác định được vị trí bão hoà; chúng chỉ cho biết bão hoà nằm **đâu đó giữa 748 và
   3052 ms**. Phát biểu đúng: *"nới RF từ 0,75 s lên 3,0 s không cải thiện thêm"*.

4. **Đường cong dữ liệu (M4) — 3 điểm, 2 tham số.** M4 **tự ghi chú đúng**:
   *"3 điểm dữ liệu, 2 tham số mọi dạng → chỉ còn 1 bậc tự do; mọi dự báo là NGOẠI SUY, độ tin
   cậy THẤP, không có khoảng tin cậy"*. **Không được đưa dự báo ngoại suy vào bài báo.**

### (g) VÒNG LẶP ĐỊNH NGHĨA

**M1 tự khai một, và khai đầy đủ.** `CHANDOAN_MOHINH.md` dòng 357–359: nhóm "8 bản giới hạn
cứng" được **định nghĩa** là F1_oracle < 50; số bản ngoài nhóm có F1_oracle < 50 là 0; nên
nhóm 8 ≡ {F1_oracle < 50} theo đúng định nghĩa, và *"mọi đặc trưng dùng nhãn tất nhiên tách
được nhóm này"*. M1 còn đi xa hơn: dòng 313 thừa nhận ranh giới 8/67 là *"ngưỡng cắt tuỳ ý
trên một dải liên tục"*, dòng 454 thừa nhận jitter *"chỉ đo trên các nhịp đã bắt đúng — theo
định nghĩa, đó là những nhịp dễ nhất"*. **Mức tự phê bình này là mẫu mực.**

**Tôi tìm được BA vòng lặp tương tự chưa được khai:**

1. **M1, phổ lỗi — nhóm (b) "không có tín hiệu" được định nghĩa bằng phép thử nhìn thấy, rồi
   dùng để kết luận "mô hình không phải nút thắt".** Nếu phép thử nhìn thấy dùng cùng một bộ
   lọc / cùng dải tần với mô hình, thì bất cứ gì mô hình không thấy sẽ tự động rơi vào (b).
   Có một phanh hãm: `sensitivity_of_visibility_test` = 0,951 (22 chủ thể) / 0,862 (CinC) và
   M1 có hiệu chỉnh (`pct_a_corrected`). Nhưng **độ ĐẶC HIỆU của phép thử nhìn thấy không được
   báo cáo** — tức không biết bao nhiêu nhịp bị gán "không nhìn thấy" trong khi thật ra nhìn
   thấy được. **Đây là chỗ hở thật.**

2. **M1, "6,36 điểm bỏ dò, 71 % nằm trên 9 bản không đo được".** 9 bản đó được chọn bằng
   `nhin_thay_kenh_tot_nhat < 0,5` — **lại là chính phép thử nhìn thấy**. Tôi tính lại và xác
   nhận số học đúng (4,5151 / 6,3613 = 71,0 %; 9 bản; 1,8462 điểm còn lại trên 58 bản), nhưng
   **kết luận "chỉ ~1,85 điểm là thật sự của mô hình" phụ thuộc hoàn toàn vào việc phép thử
   nhìn thấy có đúng hay không**, và độ đặc hiệu của nó chưa đo.

3. **M5, nhánh 22 chủ thể.** Quy tắc `gate` được huấn luyện leave-one-subject-out **trên chính
   22 chủ thể** rồi được **chấm bằng khả năng chọn kênh trên 22 chủ thể đó**. Tuy LOSO ngăn
   rò rỉ trực tiếp, các siêu tham số của cổng (max_depth 3, max_iter 200, lr 0,05) được kế
   thừa từ `gate22_analyze.py` — **một vòng trước đã tối ưu trên cùng 22 chủ thể này**. Vậy
   `gate` được ưu ái trên chính sân nhà đã dùng để chỉnh nó, còn `peakprob` (không huấn luyện,
   không tham số) thì không. **Đây có thể là lý do thật sự khiến `gate` thắng ở nhánh 22 chủ
   thể và thua ở CinC** — và nó củng cố việc **không** nên tin nhánh 22 chủ thể.

---

## VIỆC 3 — MÂU THUẪN GIỮA CÁC AGENT

### Mâu thuẫn 1 — M1 "mô hình không phải nút thắt" vs M2 "chênh 3,10 điểm giữa các kiến trúc"

**Phán xử: KHÔNG mâu thuẫn về số học, NHƯNG M1 phát biểu quá phạm vi.**

* Chênh 3,10 điểm là của `cnn_l`, có **trường tiếp nhận 60 ms** — một mốc bị làm què có chủ ý,
  không phải ứng viên thật. Trong nhóm kiến trúc có RF đủ (≥ 748 ms), toàn bộ dải chỉ là
  **0,71 điểm** (96,93 → 97,64). Vậy "họ kiến trúc" quả thực ít quan trọng.
* **Nhưng M2 chỉ chạy TRONG MIỀN (22 chủ thể), nơi mọi thứ ở trần** (`unit = "chu the (n=22)"`;
  không có nhánh CinC nào trong `kientruc_results.json`). **Chưa ai đo biến thiên kiến trúc
  trên CinC.** Trong khi khoảng cách thật cần giải thích là **97,6 trong miền → 74,3 trên 60
  bản CinC sạch = 23,3 điểm**.
* M1 kết luận "mô hình không phải nút thắt" từ ngân sách sai số **trên CinC** (6,36/20,60 điểm
  thuộc bộ dò), còn M2 đo tương đương **trong miền**. **Hai bên nói về hai quần thể khác nhau
  và không bên nào chứng minh mệnh đề cho quần thể của bên kia.**

**Phát biểu đúng, hẹp hơn:** *"Trong miền, họ kiến trúc không quan trọng khi trường tiếp nhận
≥ 0,75 s (dải 0,71 điểm). Ngoài miền, biến thiên kiến trúc chưa được đo."*

### Mâu thuẫn 2 — M1 nói `gate` tốt hơn, M5 chọn `peakprob`

**Phán xử: SỐ CHÍNH CỦA BÀI BÁO PHẢI LÀ `peakprob`.** Lý do, theo thứ tự sức nặng:

1. **Bằng chứng ủng hộ `gate` đều nằm ở nơi không phân biệt được.** Trên 22 chủ thể, gate
   98,61 vs peakprob 98,22 — khoảng cách **0,39 điểm** trong một dư địa oracle **1,08 điểm**,
   với 14/22 chủ thể đã chạm oracle. Trên "3 bản khó", n = 3, **và `rrcv` cũng đạt 92,95 y
   như gate** — nên đó không phải bằng chứng cho gate mà là bằng chứng rằng 3 bản đó quá ít.
2. **Bằng chứng ủng hộ `peakprob` nằm ở nơi phân biệt được.** Trên 60 bản CinC sạch (dư địa
   oracle **9,32 điểm**): peakprob +7,73 (p_Holm 0,0039) vs gate +6,44 (p_Holm 0,0505).
   **Chỉ peakprob sống sót hiệu chỉnh.**
3. **Hồ sơ rủi ro bất đối xứng mạnh.** `CHONKENH.md` dòng 103–104: peakprob mất tối đa
   **3,90 điểm, 0 bản mất quá 5 điểm**; gate mất tối đa **13,39 điểm, 3 bản mất quá 5 điểm**.
   Với ứng dụng theo dõi thai, **đuôi xấu quan trọng hơn trung bình.**
4. **`peakprob` không huấn luyện, không siêu tham số, không phụ thuộc.** `gate` kéo theo một
   HistGradientBoostingClassifier, 12 SQI, và siêu tham số thừa kế từ vòng trước — tức thêm
   bề mặt để hỏng khi chuyển miền. Chính `learned` (bộ chọn kênh học) đã hỏng đúng kiểu đó
   (+3,52 trên 60 bản, KTC [−0,77; +8,48] chứa 0, p_Holm = 1,0).

**Nhưng bài báo PHẢI báo cáo cả hai**, đúng như M5 tự khuyến nghị ở dòng 194. Xem VIỆC 6.

### Mâu thuẫn 3 — M4 tìm 15 bản rò rỉ: phải tính lại những gì?

Tôi tự tính lại trên 60 bản sạch từ dữ liệu từng bản ghi, không dựa vào báo cáo của ai.

| Kết quả | Trên 75 bản | Trên 60 bản sạch | Kết luận có đổi? |
|---|---|---|---|
| **M5** psd | 79,40 | **74,28** | Mốc tụt 5,12 điểm |
| **M5** peakprob | 85,60 | **82,01** | |
| **M5** peakprob − psd | +6,20 (p_H 0,0054) | **+7,73 (p_H 0,0039)** | **KHÔNG — mạnh lên** |
| **M5** gate − psd | +5,14 (p_H 0,085) | **+6,44 (p_H 0,0505)** | **KHÔNG — vẫn trượt Holm** |
| **M5** dư địa oracle | 7,47 | **9,32** | Dư địa lớn hơn ⇒ chọn kênh quan trọng hơn |
| **M3** notch *(tôi tính)* | +0,19 (p 0,62) | **+0,25 (p 0,70)** | **KHÔNG** |
| **M3** pseudo-label *(tôi tính)* | −0,53 (p 0,005) | **−0,68 (p 0,003)** | **KHÔNG — xấu hơn** |
| **M3** AdaBN *(tôi tính)* | −1,27 | **−1,58** | **KHÔNG — xấu hơn** |
| **M3** TENT *(tôi tính)* | −1,95 | **−2,43** | **KHÔNG — xấu hơn** |
| **M3** trên nền peakprob *(tôi tính)* | −0,45…−2,70 | **−0,55…−3,35** | **KHÔNG — xấu hơn** |
| **M1** phổ lỗi | a 1,0 b 19,3 c 9,1 e 58,6 | *chưa tính* (CinC68: a 0,98 b 20,5 c 9,5 e 59,6) | Xu hướng ổn định; **nên tính lại cho đủ** |
| **M2** | *chỉ trong miền* | không áp dụng | Không ảnh hưởng |

**Kết luận VIỆC 3.3:** Rò rỉ **làm xê dịch mọi mốc tuyệt đối 3–7 điểm nhưng KHÔNG lật bất kỳ
kết luận định tính nào.** Cả hai kết luận lớn của vòng — *"peakprob thắng psd"* và *"thích nghi
miền thất bại hoàn toàn"* — đều **mạnh hơn** trên dữ liệu sạch. Đó là dấu hiệu tốt.
**Tuy nhiên mọi con số tuyệt đối trong README, bài báo và đề cương phải được thay bằng con số
60 bản.** M1 là nhiệm vụ duy nhất chưa tính lại trên 60 bản sạch.

### Mâu thuẫn 4 — M3 tự mâu thuẫn (tôi tìm ra, chưa ai nêu)

M3 xếp **điện lưới 60 Hz** là dịch chuyển miền lớn thứ tư (Cohen d = 1,92) và trình bày nó như
một nguyên nhân khả dĩ. **Nhưng chính M3 đã can thiệp đúng vào 60 Hz** (nhánh `notch`) và thu
được **+0,19 điểm, p = 0,60** (tôi tính lại trên 60 bản sạch: +0,25, p = 0,70).
**Một dịch chuyển đã được can thiệp trực tiếp và không mang lại gì thì không còn là nguyên
nhân khả dĩ — nó là một dịch chuyển vô hại.** Ngoài ra **cả 75/75 bản CinC đều có đỉnh 50 Hz**
(`mains_detected.n_with_50 = 75`), mà front-end đã chặn 50 Hz. Cách trình bày hiện tại của M3
mời người đọc đi vào ngõ cụt. **Phải sửa.**

### Mâu thuẫn 5 — M3 khẳng định quá phạm vi (tôi tìm ra)

M3 kết luận: *"phân bố ĐẦU VÀO CỦA MẠNG gần như KHÔNG dịch chuyển"* (|d| ≤ 0,32, p 0,73–0,76).
Tôi kiểm `THICHNGHI.md` dòng 51–52: bằng chứng là **hai đại lượng** — độ lệch chuẩn phần dư và
phân vị 99,9 — cộng độ nhọn.

**Đây là ba mô men biên độ bậc thấp.** Hai phân bố có thể trùng khít ở độ lệch chuẩn và phân vị
99,9 mà vẫn khác nhau hoàn toàn về **nội dung phổ, tỉ số tín hiệu thai trên nhiễu, hình dạng
phức bộ**. Và bằng chứng nội tại cho thấy **chúng KHÁC nhau thật**: chính M1 đo được nhóm lỗi
(b) "không có tín hiệu thai" chiếm **19,3 % lỗi trên CinC nhưng chỉ 8,4 % trong miền**, và M3
đo `p_10_60` (công suất trong dải 10–60 Hz, chính là dải mà mô hình đọc) lệch **d = −1,06**.

**Phát biểu đúng:** *"Các mô men biên độ bậc thấp của đầu vào mạng không dịch chuyển sau
`robust_scale`; do đó chuẩn hoá biên độ không phải là chỗ cần sửa. Dịch chuyển thật nằm ở nội
dung phổ và ở tỉ số tín hiệu thai — mà chuẩn hoá không thể chạm tới."*
Đây không phải bắt lỗi vặt: **nó đổi hoàn toàn hướng khắc phục.** Nếu đầu vào thật sự không
dịch chuyển thì không có gì để làm; nếu dịch chuyển nằm ở SNR thì hướng đi là **thu thêm dữ
liệu SNR thấp**, chứ không phải thích nghi miền — và điều đó khớp chính xác với việc cả bốn
phương pháp thích nghi đều thất bại.

---

## VIỆC 4 — PHÁN XỬ TỪNG KẾT QUẢ

### M4 — RÒ RỈ DỮ LIỆU ADFECGDB ↔ CinC 2013
### → **DÙNG ĐƯỢC NGAY**

Kết quả mạnh nhất của vòng. Hai cài đặt độc lập (thư viện khác, định dạng khác, viết lại từ
đầu), đối chứng dương (0,86–0,98) và đối chứng âm (0,44–0,62) đều đúng chiều, cấu trúc cửa sổ
đều đặn 0–60 / 120–180 / 240–300 s không thể là ngẫu nhiên. Tôi công kích bốn hướng và không
bác được hướng nào.

*Hai điều kiện kèm theo:*
1. Trình bày như **đặc tính của dữ liệu công khai**, không phải lỗi của nhóm. Nêu rõ mô hình
   sản xuất được huấn luyện trên r01/r04/r07/r08/r10 nên 15 bản này không thể coi là ngoài miền.
2. Chốt **một** con số cho đối chứng âm và nói rõ thô hay đã lọc (đề nghị: 0,62, thô).

### M4 — CÂN BẰNG DỮ LIỆU, CHẤT LƯỢNG NHÃN, ĐƯỜNG CONG n
### → **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN**

Phần kiểm kê (259,6 phút, 36 313 nhịp, hệ số cân bằng) dùng được ngay.
**Đường cong dữ liệu PHẢI BỎ phần ngoại suy** — 3 điểm, 2 tham số, 1 bậc tự do, không KTC.
M4 đã tự ghi chú đúng; chỉ cần đảm bảo bài báo không trích dự báo.
Thực nghiệm tăng cường vs không tăng cường (n = 8 chủ thể, hiệu −0,12, p = 0,875) là **kết quả
vô hiệu trên n nhỏ** — báo cáo là "không phát hiện khác biệt", tuyệt đối không nói "tương đương".

### M5 — CHỌN KÊNH
### → **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN** (bốn điều kiện bắt buộc)

Phát hiện là thật và có giá trị: quy tắc PSD hiện hành hỏng ở ~20 % bản ghi ngoài miền, và một
quy tắc **một dòng, không huấn luyện** lấy lại 82,9 % dư địa oracle. Kiểm rò rỉ nhãn đã chạy và
đã qua. Bảy quy tắc đều được báo cáo kể cả quy tắc hỏng.

**Điều kiện 1 — bỏ chữ "tiền đăng ký" / "pre-registered".** Tệp không nằm trong git, chỉ có
mtime, và được ghi sau khi F1 cơ sở từng kênh của CinC đã biết. Dùng: *"kế hoạch phân tích được
cố định trước khi đánh giá bất kỳ quy tắc nào"*.

**Điều kiện 2 — báo cáo con số trên 60 bản sạch làm con số chính** (+7,73, p_Holm 0,0039), và
nêu con số 75 bản chỉ để đối chiếu với tài liệu cũ.

**Điều kiện 3 — nói thẳng rằng quy tắc được chỉ định trước (`gate`) trượt Holm** (0,085 / 0,0505),
và nói thẳng rằng khai báo trước tự mâu thuẫn ở điều khoản Holm. Không được im lặng về điều này.

**Điều kiện 4 — dùng phát biểu chính thức ở VIỆC 6.**

*Ghi chú:* lập luận bào chữa của M5 (peakprob nằm trong họ 7 đã định trước, sống sót Holm trên
cả 7) **đúng về mặt thống kê** và đủ để giữ kết luận. Nhưng nó chỉ đúng vì có Holm — nên không
được bỏ Holm khi trình bày.

### M5 — HỆ QUẢ HẬU KIỂM (so với Power-MF)
### → **PHẢI BỎ khỏi bài báo** (giữ làm ghi chú nội bộ)

`he_qua_hau_kiem.canh_bao` tự ghi: *"Quy tắc chọn kênh được so ở đây đã được thử trên chính 22
chủ thể này; con số không phải bằng chứng ngoài miền."* Và `CHONKENH.md` dòng 187 cũng nói
*"phải kiểm lại trên dữ liệu mới trước khi đưa vào bài báo"*. Đồng ý hoàn toàn. Con số
"1 kênh chỉ kém 4 kênh 0,22 điểm" **rất hấp dẫn và rất dễ bị phản biện đánh sập**. Để dành.

### M1 — PHỔ LỖI SÁU NHÓM
### → **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN**

Khung phân loại lỗi có mức ngẫu nhiên đi kèm là một đóng góp phương pháp thật; hiếm khi thấy
trong tài liệu fECG. Số liệu khớp hoàn toàn. Nhất quán chéo với M5 đã kiểm
(`kiem_tra_nhat_quan.so_ban_ghi_lech = 0`, lệch F1 ≤ 2,8e-14 trên 10 cặp quần thể×quy tắc).

*Điều kiện:* (1) **tính lại trên 60 bản sạch** — M1 là nhiệm vụ duy nhất chưa làm;
(2) **báo cáo độ ĐẶC HIỆU của phép thử nhìn thấy**, không chỉ độ nhạy — vì nhóm (b) và con số
"1,85 điểm thuộc mô hình" phụ thuộc hoàn toàn vào nó;
(3) ghi rõ mức ngẫu nhiên trong bảng là của quy tắc nào.

### M1 — "MÔ HÌNH KHÔNG PHẢI NÚT THẮT"
### → **CẦN LÀM LẠI** (phát biểu quá phạm vi; bằng chứng chống đỡ quá yếu)

Ba trụ chống đỡ đều không chịu nổi tải:

1. **Trần năng lực:** n = 4 bản ghi, **trong mẫu**, 1 hạt giống, ngưỡng chọn trong mẫu. Không
   thể suy ra điều gì về tổng quát hoá ngoài miền.
2. **Định vị (jitter):** đo **chỉ trên các nhịp đã bắt đúng** — M1 tự thừa nhận đó là "những
   nhịp dễ nhất theo định nghĩa". Nói về độ chính xác định vị, không nói về năng lực.
3. **"Chỉ 1,85 điểm thuộc mô hình":** dựa vào phép thử nhìn thấy mà độ đặc hiệu chưa đo, và
   dùng chính phép thử đó để định nghĩa tập 9 bản bị loại.

*Cách làm lại (rẻ):* huấn luyện một biến thể bề rộng 80 với **cùng giao thức LOSO 22 chủ thể**
như mô hình sản xuất, rồi **chấm trên 60 bản CinC sạch**. Nếu 60 bản sạch không cải thiện thì
kết luận "năng lực không phải nút thắt" mới có chỗ đứng. Chi phí ~1 lần huấn luyện.

*Phát biểu thay thế dùng được ngay:* *"Trong miền, bốn phần năm sai số còn lại là lệch thời
điểm trong dung sai chứ không phải bỏ nhịp; ngoài miền, phần lớn dư địa nằm ở các bản ghi mà
tín hiệu thai không đo được trên bất kỳ kênh nào. Chúng tôi chưa đo được liệu tăng năng lực có
giúp ích ngoài miền hay không."*

### M1 — NHÓM 8 BẢN "GIỚI HẠN CỨNG"
### → **PHẢI BỎ như một phát hiện** (giữ làm mô tả)

M1 tự khai đúng: nhóm được **định nghĩa** bằng F1_oracle < 50, nên mọi đặc trưng dùng nhãn tất
nhiên tách được nó. Thêm vào đó, a54 chỉ có **37 nhãn** trong khi mô hình phát hiện **144 nhịp**
— đó là lỗi nhãn, không phải bản ghi khó; a54 và a71 đều nằm trong danh sách chú thích sai đã
khai từ trước. Nhóm thật còn 6 bản.
**Giữ lại phần dùng được:** bảng AUROC của các đặc trưng **mù nhãn** tách 8 bản khỏi 67 bản —
phần đó **không** bị vòng lặp vì nó không dùng nhãn ở phía đặc trưng. Nhưng phải trình bày là
*"đặc trưng mù nhãn dự đoán được các bản ghi vô vọng"*, không phải *"chúng tôi phát hiện một
nhóm bản ghi giới hạn cứng"*.

### M1 — DƯ ĐỊA HỢP NHẤT MỨC XÁC SUẤT (B2_03)
### → **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN** (n = 1 — chỉ là giả thuyết)

Con số đúng: kênh tốt nhất 83,91 · gộp bỏ phiếu tốt nhất 84,87 · **trần hợp nhất 98,01**.
Dư địa 13,1 điểm là **so với gộp bỏ phiếu**, không phải so với kênh tốt nhất (số đó là 14,1).
**Đây là MỘT chủ thể.** Là gợi ý tốt cho hướng đi, không phải kết quả. Trên cả 22 chủ thể:
gộp bỏ phiếu tốt nhất 98,47 vs oracle 98,63 vs trần hợp nhất 99,80 — dư địa 1,33 điểm.
Phát biểu đúng: *"giả thuyết, dựa trên một chủ thể"*.

### M2 — TƯƠNG ĐƯƠNG KIẾN TRÚC
### → **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN** (ba điều kiện)

Thiết kế công bằng đã được kiểm và **đạt**: cùng seed, cùng fold, cùng epoch, cùng stride,
tham số lệch ≤ 2,67 %. Đây là so sánh kiến trúc sạch nhất tôi thấy trong repo này.

**Điều kiện 1 — báo cáo trên thang logit, không phải F1 thô.** M2 đã tính sẵn `logit_diff` cho
mọi kiến trúc; chỉ việc dùng. Và phải chấp nhận rằng kết luận **đổi**: trên thang logit,
`cnn_wide` kém TCN có ý nghĩa ([−0,745; −0,156] không chứa 0) trong khi trên F1 thô thì không.

**Điều kiện 2 — ghi rõ giao thức thu nhỏ (3 epoch, 3 fold, không tăng cường, 1 seed)** ở ngay
chú thích bảng, và phát biểu tương đương là *"trong chế độ huấn luyện thu nhỏ"*, không phải
tuyệt đối.

**Điều kiện 3 — biện minh biên TOST 1,0 điểm**, hoặc giảm nó. Trên nền 97,6 với dư địa 1,0
điểm, biên 1,0 điểm gần như không ràng buộc.

*Phát biểu dùng được:* *"Với ngân sách tham số cố định (±2,7 %) và giao thức đồng nhất, mở rộng
trường tiếp nhận từ 60 ms lên ~1,5 s thu hẹp 74 % khoảng cách hiệu năng giữa CNN thường và TCN
giãn nở; nới tiếp lên 3,0 s không mang lại thêm. Cơ chế giãn nở không cần thiết — bề rộng ngữ
cảnh mới cần."*

### M3 — THÍCH NGHI MIỀN
### → **DÙNG ĐƯỢC NGAY, như một KẾT QUẢ ÂM TÍNH** (sau khi sửa hai cách diễn đạt)

Đây là kết quả tôi tin tưởng nhất sau M4. Lý do:

* **Không rò rỉ:** siêu tham số chọn trên bề mặt m12→B1, không chạm CinC. Thiết kế đúng sách.
* **Tôi tự tính lại trên 60 bản sạch:** mọi kết luận giữ nguyên và **mạnh lên**
  (AdaBN −1,58 · TENT −2,43 · pseudo-label −0,68 · notch +0,25 p = 0,70).
* **Bền trên hai mốc nền:** trên nền peakprob, cả bốn vẫn âm (−0,55 đến −3,35).
* **Chẩn đoán có ý nghĩa:** áp cả ba dịch chuyển đo được lên 22 chủ thể trong miền chỉ mất
  0,01 điểm (97,3301 → 97,3166) trong khi khoảng cách thật còn 17,92 điểm. Tức **các dịch
  chuyển đo được KHÔNG giải thích được khoảng cách.** Đây là kết luận có giá trị thật.

Một kết quả âm tính sạch, có chẩn đoán đi kèm, **đăng được** — tài liệu thích nghi miền trong
y sinh đầy rẫy báo cáo tích cực chọn lọc.

**Sửa 1:** bỏ 60 Hz khỏi danh sách nguyên nhân khả dĩ (đã can thiệp, p = 0,60/0,70), và nêu rõ
cả 75/75 bản đều có 50 Hz.
**Sửa 2:** hạ *"phân bố đầu vào của mạng không dịch chuyển"* xuống *"các mô men biên độ bậc
thấp của đầu vào mạng không dịch chuyển"*, và nêu rằng dịch chuyển thật nằm ở nội dung phổ và
tỉ số tín hiệu thai (`p_10_60` d = −1,06; nhóm lỗi (b) 8,4 % → 19,3 %).

### M3 — CẢNH BÁO eff_bits
### → **DÙNG ĐƯỢC VỚI ĐIỀU KIỆN**

`dich_chuyen_mien.canh_bao_eff_bits` tự ghi rằng eff_bits của Silesia bị thổi phồng do bộ nạp
resample/scale về float, nên chỉ so sánh hợp lệ giữa CinC và ADFECGDB. **Đúng và phải giữ cảnh
báo này.** Hệ quả: `eff_bits` (d = −2,81) là **dịch chuyển đứng đầu bảng nhưng phần lớn là ảo**.
Bảng dịch chuyển miền nên loại eff_bits khỏi hai dòng đầu, nếu không người đọc sẽ đuổi theo một
hiện vật của bộ nạp.

---

## VIỆC 5 — TRẢ LỜI BỐN CÂU HỎI CỦA CHỦ NHIỆM ĐỀ TÀI

### 1. Mô hình hiện tại đã đủ tốt chưa?

**Trong miền: đủ tốt, và đã chạm trần đo được. Ngoài miền: chưa, còn xa.**

* Trong miền (22 chủ thể, LOSO): **97,56** với quy tắc psd, **98,61** với gate,
  oracle **98,63**. 14/22 chủ thể đã đạt đúng oracle. Dư địa còn lại **1,08 điểm**.
  Ở mức này, **thiết bị đo (dữ liệu và nhãn) đã hết độ phân giải** — không phải mô hình.
* Ngoài miền (60 bản CinC **sạch**): **74,28** với psd, **82,01** với peakprob,
  oracle **83,60**. **16/60 bản có F1 < 50.**
* Khoảng cách trong miền → ngoài miền: **23,3 điểm.** Đó mới là bài toán thật.

**Bằng chứng:** `chonkenh_results.json.bang.s22` + `dulieu_results.json.chon_kenh_60_sach`.
**Độ tin cậy: CAO** cho các con số; **TRUNG BÌNH** cho việc quy 60 bản sạch là đại diện cho
"ngoài miền" nói chung (60 bản, 60 s mỗi bản, một thách thức năm 2013, chưa kiểm trùng chủ thể
trong nội bộ 60 bản).

**Cảnh báo quan trọng:** *mọi con số CinC đã công bố trước vòng này bị thổi 3–7 điểm.*
README, bài báo, đề cương phải được sửa.

### 2. Có thể tinh chỉnh hay bổ sung kiến trúc cho tối ưu hơn không?

**Theo bằng chứng hiện có: KHÔNG — và đây là câu trả lời đáng tin cậy nhất trong bốn câu.**

* Sáu kiến trúc thay thế, cùng ngân sách tham số (±2,67 %), cùng seed/fold/epoch: hai kiến
  trúc (`rf_wide`, `tcn_ms`) **tương đương thống kê** với TCN sản xuất (TOST Holm 7,1e-10 và
  4,6e-06 trong biên ±1,0 điểm). Không kiến trúc nào **thắng**.
* Nhân **4 lần** tham số (113 k → 451 k) được **+0,26 điểm trong mẫu**, gần như toàn bộ rơi
  vào một chủ thể.
* Thứ **duy nhất** thật sự quan trọng là **bề rộng trường tiếp nhận**: 60 ms → 1,5 s lấp được
  74 % khoảng cách. Mô hình sản xuất đã có 1 516 ms. **Đã ở đúng chỗ.**

**Bằng chứng:** `kientruc_results.json` + `chandoan_capacity.json`.
**Độ tin cậy: TRUNG BÌNH-CAO.** Hạ từ CAO xuống vì: chỉ 3 epoch, chỉ 1 seed, **chỉ đo trong
miền nơi mọi thứ ở trần**, và trần năng lực chỉ n = 4 bản ghi trong mẫu.

**Khuyến nghị: ĐỪNG động vào kiến trúc.** Đây là đòn bẩy yếu nhất trong mọi đòn bẩy đã đo.
Thời gian dành cho kiến trúc là thời gian không dành cho dữ liệu — nơi đòn bẩy thật nằm.

### 3. Có thể fine-tune gì không?

**Thích nghi miền không nhãn: KHÔNG. Đã thử bốn cách, cả bốn thất bại, và tôi đã tự kiểm lại.**

| phương pháp | 75 bản | **60 bản sạch (tôi tính)** | trên nền peakprob |
|---|---:|---:|---:|
| chặn điện lưới | +0,19 (p 0,60) | **+0,25 (p 0,70)** | −0,45 |
| tự huấn luyện nhãn giả | −0,53 | **−0,68 (p 0,003)** | −2,08 |
| AdaBN | −1,27 | **−1,58 (p 0,001)** | −2,70 |
| TENT | −1,95 | **−2,43 (p 4e-05)** | −2,18 |

Không phải "không cải thiện" — mà **chủ động làm hỏng**, và hỏng nhiều hơn trên dữ liệu sạch.

**Vì sao:** áp cả ba dịch chuyển đo được lên 22 chủ thể trong miền chỉ mất **0,01 điểm**, trong
khi khoảng cách thật còn **17,92 điểm**. Các dịch chuyển mà thích nghi miền biết cách sửa
**không phải** là thứ đang gây ra khoảng cách. Thứ gây ra khoảng cách là **tín hiệu thai yếu
hơn hoặc vắng mặt** — nhóm lỗi (b) tăng từ 8,4 % lên 19,3 % tổng lỗi. **Không thuật toán thích
nghi nào tạo ra được tín hiệu không tồn tại.**

**Bằng chứng:** `adapt_results.json` + tính lại của tôi trên 60 bản sạch.
**Độ tin cậy: CAO.** Đây là kết luận vững nhất của vòng: thiết kế không rò rỉ, bền qua hai mốc
nền, bền qua hai quần thể, và có chẩn đoán cơ chế đi kèm.

**CÓ một thứ "fine-tune" hiệu quả, và nó rẻ nhất trong tất cả: ĐỔI QUY TẮC CHỌN KÊNH.**
psd → peakprob: **+7,73 điểm** trên 60 bản sạch, **lấy lại 82,9 % dư địa oracle**, đưa số bản
F1 < 50 từ 16 xuống 9, **không huấn luyện, không tham số, không phụ thuộc mới**. Chi phí: chạy
mô hình 4 lần thay vì 1 lần (4 × 4,35 ms mỗi cửa sổ 4 s — vẫn nhanh hơn thời gian thực ~230 lần).
**Đây là đòn bẩy tốt nhất còn lại, và nó đã sẵn sàng.**

### 4. Dữ liệu huấn luyện đã tốt chưa?

**CHƯA — và đây là nút thắt thật sự. Ba vấn đề riêng biệt:**

**(i) Quá ít chủ thể.** 22 chủ thể, 259,6 phút. Bộ chọn kênh học thất bại với lý do rõ ràng:
**88 hàng huấn luyện (22 × 4 kênh) với 36 đặc trưng.** M5 khuyến nghị đừng học bộ chọn kênh
cho tới khi có > 50 chủ thể. Tôi đồng ý.

**(ii) Sai phân bố, không phải sai kích thước.** 60 bản CinC sạch có **16/60 bản F1 < 50**, và
trong 67 bản phân tích được, **9 bản chiếm 71 % toàn bộ dư địa của bộ dò** vì tín hiệu thai
không đo được trên **bất kỳ kênh nào**. Tập huấn luyện hiện tại **gần như không chứa bản ghi
loại đó** — nhóm lỗi (b) chỉ 8,4 % trong miền so với 19,3 % trên CinC. Thêm 22 chủ thể nữa
cùng loại sẽ **không** giúp. **Cần chủ thể SNR THẤP.**

**(iii) Chất lượng nhãn có vấn đề đã biết.** a54 có **37 nhãn** trong khi mô hình phát hiện
**144 nhịp**; 7 bản nằm trong danh sách chú thích sai đã khai từ trước
(a33 a38 a47 a52 a54 a71 a74); 130 nhịp trong B1 có nhãn 0 (0,458 % tổng). Ở mức F1 ~99 trong
miền, **lỗi nhãn đang chiếm một phần đáng kể của sai số còn lại** — đó là lý do vật lý vì sao
nhân 4 lần tham số chỉ được +0,26 điểm.

**Bằng chứng:** `dulieu_results.json` (cân bằng, chất lượng nhãn) + `chandoan_results.json`
(`bo_do_67_chi_tiet`, `gioi_han_cung_8`).
**Độ tin cậy: CAO** cho (i) và (iii); **TRUNG BÌNH-CAO** cho (ii) — vì phép thử nhìn thấy chưa
báo cáo độ đặc hiệu, nên "tín hiệu không đo được" có thể bị đếm thừa.

---

## VIỆC 6 — PHÁT BIỂU CHÍNH THỨC CHO KẾT QUẢ CHỌN KÊNH

> ### Bản dùng cho phần Kết quả của bài báo
>
> Chúng tôi so sánh bảy quy tắc chọn kênh mù nhãn với quy tắc PSD hiện hành (Jaeger 2024).
> Danh sách bảy quy tắc, các chỉ số báo cáo và quy tắc quyết định được cố định và ghi ra tệp
> (`analysis/chonkenh_khaibao_truoc.json`) **trước khi đánh giá bất kỳ quy tắc nào**, tuy sau
> khi F1 cơ sở từng kênh đã được tính ở vòng trước; tệp không được chốt bằng dấu thời gian của
> bên thứ ba, nên chúng tôi **không** mô tả nghiên cứu này là tiền đăng ký.
>
> Đánh giá thực hiện trên 60 bản ghi của CinC 2013 set-a, sau khi loại 15 bản ghi mà chúng tôi
> xác định là bản sao nguyên văn của dữ liệu huấn luyện ADFECGDB (tương quan chéo chuẩn hoá
> = 1,0000; lệch RR = 0,0 ms; xác nhận bằng hai cài đặt độc lập). Việc loại này còn cần thiết
> vì lý do thứ hai: 15 bản ghi đó chỉ đến từ 5 sản phụ, nên giữ chúng lại sẽ vi phạm giả định
> độc lập của thống kê ở mức bản ghi.
>
> Quy tắc quyết định đã ghi trước chỉ định chọn quy tắc tốt nhất theo F1 trung bình trên 22 chủ
> thể trong miền. **Luật đó chỉ ra `gate`**, đạt **+6,44 điểm F1 so với mốc PSD
> (KTC 95 % [+2,49; +11,10], Wilcoxon p = 0,010)**. **Hiệu ứng này KHÔNG sống sót hiệu chỉnh
> Holm trên bảy quy tắc (p_Holm = 0,051).** Chúng tôi báo cáo điều này như một thất bại của
> phép thử xác nhận đã được chỉ định trước.
>
> Chúng tôi cũng ghi nhận rằng nhánh trọng tài trong miền **không có khả năng phân biệt**: bốn
> quy tắc đứng đầu cách nhau 0,04 điểm trong khi toàn bộ dư địa oracle ở đó chỉ 1,08 điểm, và
> 14/22 chủ thể đã đạt đúng hiệu năng của kênh oracle. Việc giao vai trò trọng tài cho một
> nhánh đã chạm trần là một sai lầm thiết kế của chúng tôi.
>
> Quy tắc mạnh nhất trong bảy quy tắc đã ghi trước là `peakprob` — chọn kênh có xác suất trung
> bình của chính mô hình tại các đỉnh đã phát hiện cao nhất; không huấn luyện, không siêu tham
> số. Nó đạt **82,01 so với 74,28, hiệu +7,73 điểm F1 (KTC 95 % [+3,82; +12,41],
> Wilcoxon p = 5,6e-04, p_Holm = 0,0039 trên toàn bộ bảy quy tắc)**, tức **lấy lại 82,9 % dư
> địa của bộ chọn kênh oracle**, đưa số bản ghi có F1 < 50 từ 16 xuống 9, thắng 19 / hoà 35 /
> thua 6, và **không bản ghi nào mất quá 3,90 điểm**.
>
> **`peakprob` được chọn sau khi đã nhìn kết quả CinC.** Chúng tôi không trình bày nó như một
> phép thử xác nhận. Cơ sở để vẫn báo cáo nó là hiệu ứng sống sót hiệu chỉnh Holm trên **toàn
> bộ** họ bảy quy tắc đã ghi trước — tức ngay cả khi coi thao tác "chọn quy tắc tốt nhất trong
> họ sau khi nhìn dữ liệu" là hoàn toàn hậu kiểm, sai số họ vẫn được khống chế ở mức 5 %.
> Chúng tôi báo cáo cả hai con số và không trình bày con số lớn hơn một cách đơn lẻ.
>
> Kết quả này **chưa được nhân rộng trên một bộ dữ liệu thứ ba độc lập.** Chúng tôi coi nó là
> **một giả thuyết mạnh, chưa được xác nhận**, và nêu việc xác nhận trên dữ liệu giữ riêng là
> bước tiếp theo bắt buộc.

**Vì sao phát biểu này thoả cả hai ràng buộc:**
* *Trung thực:* nói thẳng peakprob là hậu kiểm, nói thẳng gate trượt Holm, nói thẳng sai lầm
  thiết kế, nói thẳng chưa được xác nhận, bỏ chữ "tiền đăng ký".
* *Không bán rẻ:* +7,73 điểm, 82,9 % dư địa, p_Holm 0,0039, đuôi xấu tối đa 3,90 điểm, 16→9
  bản hỏng nặng — đều được nêu đủ. Cơ sở thống kê để giữ kết luận (Holm trên cả họ) được trình
  bày rõ chứ không bị giấu sau lời xin lỗi.

---

## VIỆC 7 — BA VIỆC TIẾP THEO CÓ GIÁ TRỊ NHẤT

### Việc 1 (ưu tiên tuyệt đối) — Sửa mọi con số CinC đã công bố, và tính lại M1 trên 60 bản sạch

**Lý do:** M4 chứng minh mọi con số CinC bị thổi **3,27–7,18 điểm** (`chong_lan.thoi_phong`).
README, README.vi, `paper/cinc2026/main.tex`, đề cương, `survey/facts_phase2.json` đang mang số
sai. **Đây là rủi ro liêm chính, không phải việc dọn dẹp.** Nếu một phản biện Q1 tự phát hiện
sự chồng lấn này sau khi bài đã nộp, hậu quả nặng hơn nhiều so với việc tự công bố trước.

M5, M3, M4 đã có bản 60 bản sạch (M3 do tôi tính lại và xác nhận). **M1 là nhiệm vụ duy nhất
chưa có** — phổ lỗi, ngân sách sai số, nhóm bỏ dò đều đang tính trên 75 hoặc 68 bản.

**Chi phí:** vài giờ, không cần huấn luyện lại. **Lợi ích:** toàn bộ bài báo đứng trên số đúng.

**Kèm theo, chi phí gần bằng 0:** `git commit` toàn bộ `analysis/` và `adapt/` (hiện đang là
`??` chưa theo dõi). Mọi bằng chứng của vòng này hiện chỉ tồn tại dưới dạng tệp chưa cam kết
với mtime có thể sửa. **Mọi lập luận "chúng tôi cố định kế hoạch trước" đều vô giá trị nếu
không có cam kết git.**

### Việc 2 — Xác nhận `peakprob` trên một bộ dữ liệu thứ ba, và tính lại nhánh 22 chủ thể trên thang logit

**Lý do:** `peakprob` là **đòn bẩy lớn nhất còn lại đã được đo** (+7,73 điểm, lấy lại 82,9 %
dư địa, chi phí gần bằng 0). Nhưng nó là lựa chọn hậu kiểm trên chính tập đánh giá. **Một lần
nhân rộng trên dữ liệu chưa từng chạm sẽ biến nó từ "giả thuyết mạnh" thành "kết quả"** — và
đó là khác biệt giữa một bài Q2 và một bài Q1.

Ứng viên sẵn có trong repo: **CinC 2013 set-b** (chưa dùng), **NInFEA**, **NIFEADB** (đã có
bộ nạp: `model/ninfea_loader.py`, `model/nifeadb_loader.py`). **Phải chạy set-b hoặc NInFEA
đúng một lần, với `peakprob` chốt cứng từ trước, và báo cáo bất kể kết quả ra sao.**

**Việc phụ, rẻ và có thể lật kết luận:** tính lại nhánh 22 chủ thể **trên thang logit**. Ở đó
bốn quy tắc cách nhau 0,04 điểm F1 thô với 14/22 chủ thể chạm trần — **trên logit thứ hạng rất
có thể khác**. Nếu `peakprob` thắng trên logit ở nhánh trong miền, thì **toàn bộ vấn đề "chọn
hậu kiểm" biến mất**: quy tắc quyết định đã ghi trước sẽ chỉ đúng vào `peakprob`. Đây là việc
một buổi chiều với khả năng cứu được điểm yếu lớn nhất của bài báo. **Nhưng phải khai báo ý
định này TRƯỚC khi chạy và báo cáo kết quả dù nó bất lợi** — nếu không thì đây lại là một lần
chọn hậu kiểm nữa.

### Việc 3 — Thu thập (hoặc mô phỏng có kiểm soát) chủ thể SNR thấp, và đo độ đặc hiệu của phép thử nhìn thấy

**Lý do:** ba nhiệm vụ độc lập cùng chỉ về một chỗ.
* M3: cả bốn phương pháp thích nghi miền thất bại vì các dịch chuyển đo được **không** giải
  thích khoảng cách (áp cả ba chỉ mất 0,01 điểm, còn thiếu 17,92 điểm).
* M1: **71 % dư địa của bộ dò nằm trên 9 bản ghi** mà tín hiệu thai không đo được trên bất kỳ
  kênh nào; nhóm lỗi (b) tăng **8,4 % → 19,3 %**.
* M2: kiến trúc đã hết đòn bẩy (dải 0,71 điểm); năng lực đã hết đòn bẩy (+0,26 khi nhân 4).

Ba đường độc lập cùng chỉ vào **phân bố dữ liệu huấn luyện**, không phải mô hình. Tập huấn
luyện hiện tại **hầu như không chứa** chế độ vận hành đang gây ra lỗi.

**Làm trước, chi phí thấp nhất:** `pilot_evidence/snr_curve.json` đã có sẵn đường cong theo
SNR. **Hạ SNR của dữ liệu trong miền một cách có kiểm soát và huấn luyện lại**, rồi đo trên 60
bản CinC sạch. Nếu đường cong cải thiện → xác nhận rằng dữ liệu SNR thấp là đòn bẩy, và biện
minh cho việc đi thu thập thật. Nếu không → tiết kiệm cho nhóm nhiều tháng đi sai hướng.
Đây là phép thử **rẻ** cho một giả thuyết **đắt**.

**Kèm theo, bắt buộc:** **đo độ ĐẶC HIỆU của phép thử nhìn thấy.** Hiện chỉ có độ nhạy
(0,951 / 0,862). Hai con số quan trọng nhất của M1 — nhóm (b) và "chỉ 1,85 điểm thuộc mô hình"
— **đều treo trên phép thử này**, và nếu nó gán nhầm "không nhìn thấy" cho các nhịp thật ra
nhìn thấy được, thì kết luận "mô hình không phải nút thắt" **đảo chiều**.

---

## PHỤ LỤC A — NHỮNG ĐIỀU TÔI KHÔNG KIỂM ĐƯỢC

1. **Tính đúng đắn của mã nguồn.** Tôi đọc JSON và các tệp .py then chốt, nhưng **không chạy
   lại thí nghiệm nào** (theo ngân sách). Nếu có lỗi trong `arch22.py` hay `chonkenh_rules.py`
   thì nó sẽ nhất quán giữa JSON và MD, và tôi sẽ không thấy.
   *Ngoại lệ:* tôi **tự tính lại** toàn bộ M3 trên 60 bản sạch từ dữ liệu từng bản ghi thô và
   tái tạo được các con số trên 75 bản — nên đường ống của M3 tôi tin.
2. **Nhãn gốc.** Tôi coi nhãn `fqrs` của CinC và `qrs` của ADFECGDB là đúng. Bằng chứng a54
   (37 nhãn / 144 phát hiện) cho thấy giả định này **có chỗ sai**, nhưng tôi không kiểm được
   mức độ.
3. **60 bản CinC còn lại có phải 60 sản phụ khác nhau không.** NCC ≤ 0,62 chỉ loại trừ trùng
   nguyên văn. Trùng ở mức chủ thể (cùng sản phụ, buổi đo khác) **chưa được kiểm** và sẽ tiếp
   tục vi phạm giả định độc lập nếu có.
4. **Mốc thời gian tệp.** mtime hệ thống tệp có thể sửa. Với `analysis/` chưa cam kết git,
   mọi lập luận về trình tự đều dựa trên thiện chí.
5. **Giá trị Power-MF.** Tôi không kiểm `baselines/powermf_fair_stats.json`. Vì tôi khuyến nghị
   bỏ so sánh Power-MF khỏi bài báo (hậu kiểm trên dữ liệu đã dùng), điều này không ảnh hưởng
   phán xử nào ở trên.
6. **Một hạt giống.** Mọi hiệu số dưới 1 điểm trong M2 và mọi kết quả thích nghi trong M3 đều
   ở một hạt giống. Tôi không thể tách "hiệu ứng thật" khỏi "biến thiên hạt giống" cho các hiệu
   số nhỏ.

## PHỤ LỤC B — NHỮNG ĐIỀU LÀM ĐÚNG (để giữ lại, đừng đánh mất)

Liêm chính không tự nhiên mà có; nó là thói quen. Những thói quen sau đã xuất hiện trong vòng
này và **phải được giữ nguyên ở mọi vòng sau**:

1. **Kiểm rò rỉ nhãn bằng thực nghiệm có đối chứng dương** (`chonkenh_leakcheck.py`: xáo nhãn,
   0/776 đổi, đối chứng dương cho thấy phép thử đủ nhạy). Hầu như không ai làm việc này.
2. **Viết lại từ đầu để kiểm chéo một phát hiện quan trọng** (`dulieu_m4b_verify.py`, thư viện
   khác, định dạng khác). Đây là lý do tôi không bác được phát hiện NCC.
3. **Mức ngẫu nhiên cho chính phép gán nhãn lỗi** (`pct_null`). Nếu không có nó, "nhóm (a) chỉ
   3,8 %" là con số vô nghĩa.
4. **Tự tố cáo vòng lặp định nghĩa trước khi bị bắt** (M1, dòng 357).
5. **Tự tố cáo rằng quy tắc được chỉ định trước không phải quy tắc được báo cáo** (M5, mục 4.1)
   và tự phê bình thiết kế của chính mình (mục 4.2).
6. **Báo cáo đầy đủ các quy tắc thất bại** (`learned`, `fuse`) thay vì im lặng bỏ đi.
7. **Báo cáo một kết quả âm tính hoàn chỉnh kèm chẩn đoán cơ chế** (M3).
8. **Cảnh báo hiện vật của bộ nạp** (`canh_bao_eff_bits`) — thừa nhận đặc trưng đứng đầu bảng
   của chính mình phần lớn là ảo.
9. **Rút lại một lựa chọn hậu kiểm cũ và đo lại đúng hậu quả của nó** (kênh 0 cố định:
   90,34 → 69,33, đo lại đúng bằng 69,33).

Điểm 9 đặc biệt đáng nói: nhóm đã **từng** phạm đúng lỗi chọn hậu kiểm ở vòng trước, đã rút
lại, và vòng này xây dựng cả một khung khai báo trước để tránh lặp lại. Khung đó **chưa hoàn
hảo** (mtime, không có git, trọng tài chạm trần) — nhưng hướng đi đúng. Hãy hoàn thiện nó thay
vì bỏ nó.
