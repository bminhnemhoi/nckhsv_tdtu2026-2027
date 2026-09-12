# BUILD VÒNG 5 — sinh lại hình, dựng lại tài liệu, kiểm sạch số liệu trên chính PDF/DOCX

**Ngày:** 12/09/2026 · **Tác nhân:** E2 (sinh lại hình và bản dựng)
**Lỗ hổng cần đóng (do vòng QA D3 nêu):** *"PDF và DOCX trong repo là bản dựng TRƯỚC một số sửa của
vòng này; grep KHÔNG đọc được nội dung PDF/DOCX nên không thể bảo đảm hai định dạng đó đã sạch số
liệu"* và *"fig16_m22.pdf (chứa 90,34) và fig6_luong_cuc.pdf (nhãn 77,34 cũ) vẫn là bản cũ trên đĩa"*.

**Kết luận ngắn:** lỗ hổng đã đóng. Cả ba định dạng (đề cương PDF, đề cương DOCX, bài báo PDF) đã
được trích văn bản và quét từng con số đã rút: **0 lần xuất hiện được phát biểu như sự thật**. Đề
cương 140 trang, bài báo **đúng 4 trang**, cả hai dựng sạch (0 lỗi `^!`, 0 tham chiếu chưa định
nghĩa, 0 chuỗi `??`).

---

## VIỆC 1 — Sinh lại hình

### 1.1 Kiểm lại lời khai của D3 (không tin, đã đọc mã)

| Điều D3 báo | Kiểm chứng | Kết luận |
|---|---|---|
| đã bỏ lời gọi `fig_m22()` | `__main__` của `make_figs.py` không còn gọi `fig_m22()`; hàm còn nhưng có ghi chú "ĐÃ RÚT" | **ĐÚNG** |
| đã sửa `fig_powermf()` thành 3 cột | hàm vẽ đủ ba thanh `pmf4` / `pmf1` / `rely`, đọc thẳng `baselines/powermf_fair_stats.json` | **ĐÚNG** |
| `fig16_m22.pdf` vẫn là bản cũ chứa 90,34 | có trên đĩa (mốc 07:45 hôm nay), **không còn `\includegraphics` ở đâu** | **ĐÚNG** → đã **XOÁ** cả `.pdf` và `.png` |
| `fig6_luong_cuc.pdf` vẫn mang nhãn 77,34 cũ | đúng; nhãn cũ ghi "hậu kiểm — đã rút" nhưng chữ **đè lên** nhãn vùng đỏ | đã **sinh lại**, nhãn chuyển xuống dưới trục và ghi rõ ĐÃ BỊ RÚT |

### 1.2 Hai chỗ D3 **bỏ sót** — chính E2 phát hiện và sửa

1. **`fig1_chuoi_cai_tien` và `fig7_dong_gop` vẫn in trị số $p$ đã bị gỡ.** Đề cương tuyên bố công
   khai *"mọi trị số p trên 5 sản phụ là giả lập và đã bị gỡ"* (tính trên hàng bản ghi × kênh ×
   seed), nhưng hai hình này vẫn hiển thị `p < 0,001` cho tầng 1 và tầng 2 và `p = 0,70` cho tầng 3.
   → đã thay toàn bộ bằng **phạm vi đo** và **KTC mức chủ thể**; không hình nào còn in $p$ giả lập.
2. **`fig2_dai_loc` không nói rõ phạm vi đo.** Tiêu đề cũ "Khảo sát 8 dải thông: chênh lệch 18,9
   điểm F1" khiến 18,89 điểm đọc như một sự thật chung, trong khi nó đo trên **GBM cửa sổ 300 ms**.
   → tiêu đề mới ghi rõ phạm vi, chú thích hình thêm cảnh báo "độ lớn này *không* chuyển sang TCN".

### 1.3 Hình đã sinh lại (12 hình, 09:39 ngày 12/09/2026)

`fig1_chuoi_cai_tien`, `fig2_dai_loc`, `fig3_kien_truc`, `fig4_truong_tiep_nhan`, `fig5_doi_chuan`,
`fig6_luong_cuc`, `fig7_dong_gop`, `fig13_kien_truc_v2`, `fig17_powermf`, `fig18_cinc75`,
`fig19_m22_v2`, **`fig20_band_tcn` (hình mới)** — mỗi hình đủ cả `.pdf` và `.png`.

Đã xoá: `fig16_m22.pdf`, `fig16_m22.png` (mồ côi, chứa 90,34).

### 1.4 Tệp còn cũ trong `figs/` và xử lý

| Tệp | Mốc sửa | Còn `\includegraphics`? | Xử lý |
|---|---|---|---|
| `fig0_pipeline.pdf` | 09/09 | **Có** (`sec_4_6.tex`) | Giữ. Đã trích văn bản bằng `pdftotext`: **không chứa** con số đã rút. Sinh từ `fig_pipeline.tex`, tệp này không đổi. |
| `fig0_pipeline.png` | 09/09 | dùng ở nhánh DOCX (pandoc đổi `.pdf`→`.png`) | như trên |
| `fig9_risk_coverage.png` | 10/09 | **Có** (`sec_fsqi.tex`) | Giữ. MD5 trùng khít `fsqi/risk_coverage.png`; mã sinh không chứa hằng số đã rút. |
| `fig10_sqi_correlation.png` | 10/09 | **Có** (`sec_fsqi.tex`) | như trên (`fsqi/sqi_correlation.png`) |
| `fig11_demo_r01.png`, `fig12_demo_a02.png` | 10/09 | **Có** (`sec_demo.tex`) | Giữ. Ảnh chụp demo, không chứa số đã rút. |
| `fig14_snr.png` | 11/09 | **Có** (`sec_snr.tex`) | Giữ. MD5 trùng khít `pilot_evidence/snr_curve.png`, JSON nguồn không đổi. |
| `fig15_sample_efficiency.png` | 11/09 | **Có** (`sec_model22.tex`) | Giữ. MD5 trùng khít `pilot_evidence/sample_efficiency.png`. |
| `fig8_tin_hieu_dau_vao.pdf/.png` | 10/09 | **KHÔNG** | Mồ côi, vô hại (đồ thị tín hiệu thô). Giữ nguyên, ghi nhận ở đây. |

> **Hạn chế thành thật:** bảy tệp `.png` ở trên **không có lớp văn bản** nên không thể `grep` trực
> tiếp. Bằng chứng gián tiếp dùng thay: (a) MD5 trùng khít với tệp nguồn do chính thí nghiệm sinh,
> (b) `grep` mã sinh (`fsqi/*.py`, `analysis/clinical.py`, `pilot_evidence/snr_curve.py`,
> `pilot_evidence/sample_efficiency.py`) không có hằng số nào trong danh sách đã rút. Đây là bằng
> chứng **yếu hơn** so với việc trích văn bản, và được ghi nhận là hạn chế.

### 1.5 Quét lại chính các tệp hình `.pdf` (có lớp văn bản)

Chỉ hai hình còn chứa con số đã rút, **cả hai đều trong nhãn rút lại hiển thị ngay trên hình**:

- `fig6_luong_cuc.pdf` → `77,34`: dòng chú dưới trục ghi *"Đường 77,34 là trung bình của riêng mẫu 10
  bản ghi này dưới quy tắc kênh 0 hậu kiểm; con số đó ĐÃ BỊ RÚT. Trên toàn bộ 75 bản ghi set-a,
  chính quy tắc ấy chỉ đạt 58,72."*
- `fig18_cinc75.pdf` → `59,15`, `69,31`: cột được gắn nhãn *"10 bản ghi (mẫu cũ, đã rút)"* và chữ đỏ
  *"mẫu nhỏ, bị lệch — hai con số này đã rút"*.

---

## VIỆC 2 — Biên dịch lại

| Tài liệu | Lệnh | Số trang | `grep '^!'` trong `.log` | Tham chiếu chưa định nghĩa | Chuỗi `??` trong PDF |
|---|---|---|---|---|---|
| Đề cương | `xelatex` × 3 | **140** | **0** | **0** | **0** |
| Bài báo CinC | `pdflatex` → `bibtex` → `pdflatex` × 2 | **4** ✔ | **0** | **0** | **0** |

Bài báo suýt tràn sang trang 5 vì phần dải lọc mới. Đã **nén chữ thừa** ở 18 chỗ (mở đầu, phương
pháp, kết quả, thảo luận, hạn chế) để giữ đúng 4 trang. **Không con số nào bị bỏ** để lấy chỗ — chỉ
cắt chữ. Dòng cuối trang 4 nằm ở toạ độ y = 720 pt (mép dưới vùng chữ ≈ 784 pt), tức còn dư chỗ.

---

## VIỆC 3 — Kiểm sạch số liệu trên **chính** PDF và DOCX

Công cụ: PyMuPDF trích văn bản từng trang cho PDF; giải nén `word/document.xml` cho DOCX. Với mỗi
lần xuất hiện của mười con số đã rút (94,87 · 2,74 · 98,38 · 97,33 · 90,34 · 77,34 · 77,52 · 69,31 ·
59,15 · 22,33), soi cửa sổ ±220 ký tự để phân loại **"nằm trong câu rút lại"** hay **"đang được phát
biểu như sự thật"**.

### 3.1 Kết quả cuối

| Tệp | Số lần xuất hiện | Trong câu rút lại | **Phát biểu như sự thật** |
|---|---|---|---|
| `de_cuong_latex/de_cuong.pdf` | 57 | 57 | **0** |
| `de_cuong_latex/De_cuong_NCKH_RelyFetal.docx` | 49 | 49 | **0** |
| `paper/cinc2026/main.pdf` | 5 | 5 | **0** |

### 3.2 Lần quét ĐẦU (trên bản dựng cũ) đã bắt được **rò rỉ thật** — D3 không thấy

Đây chính là thứ mà `grep` trên `.tex` của D3 bỏ lọt, vì nó nằm trong `tables/bang_baihoc.tex` — một
bảng "bài học từng công trình" mà đề cương tuyên bố *"cố tình không sửa"*.

**Bốn ô của bảng phát biểu `77,34 ± 28,54` như kết quả xuyên bộ dữ liệu hiện hành của nhóm**, trong
đó có câu *"CUNet đạt F-score 77,8 ± 18,6 … còn nhóm đạt 77,34 ± 28,54 …, chênh lệch 0,28 điểm tức
thực tế là ngang nhau"*. Con số 77,34 đo trên **mẫu 10 bản ghi** và **đã bị rút**.

Đã sửa:

- `77,34 ± 28,54` → **`79,40 ± 29,18`** (toàn bộ 75 bản ghi set-a, quy tắc PSD mù nhãn; nguồn
  `de_cuong_latex/data_v33.json` → `cinc75.75.rules.psd.m22` = `{mean 79.3986, sd 29.1769}`, đối
  chiếu `benchmark_dpss/eval_cinc75.json`).
- Câu so sánh với Orvas 2025 sửa từ *"chênh lệch 0,28 điểm tức thực tế là ngang nhau"* thành
  **"chênh lệch 1,60 điểm — nhưng độ lệch chuẩn của nhóm lớn gần gấp đôi nên không kết luận được hơn
  kém"**, kèm ghi chú *"con số 77,34 ± 28,54 của các bản trước … đã bị rút"*.
- Hai chỗ khác trong bảng (`"trước khi công bố con số 77,34"`, `"vì sao 77,34 % của…"`) cũng đổi sang
  79,40 kèm ghi chú đã rút.

**Mâu thuẫn nội tại phải xử lý kèm:** hộp cảnh báo đứng trước bảng ghi *"nhóm **cố tình không sửa**
nó"*. Nếu giữ nguyên câu đó mà lại sửa số thì đề cương tự mâu thuẫn. Đã viết lại hộp cảnh báo:
**"giữ nguyên phần *nhận xét*, nhưng đã thay mọi con số bị rút bằng con số đúng (sửa 12/09/2026, bản
3.4) — một bảng lịch sử không được phép trở thành chỗ trú cho số liệu sai."**

### 3.3 Ba chỗ ban đầu bị cờ đỏ nhưng là **báo động giả**, vẫn được siết chặt

Ba chỗ ở bảng "Mẫu 10 bản ghi so với toàn bộ 75 bản ghi" (`tab:cinc_lech`, `tab:doansai_kenh`) và
đoạn tường thuật "Bản 3.2 đưa 90,34 lên làm con số chính". Đọc rộng ra thì cả ba nằm trong mục phân
tích *vì sao mẫu 10 bản ghi bị lệch* — đúng là câu rút lại. Nhưng khi pandoc chuyển sang DOCX thì
**số hiệu bảng bị mất**, làm ngữ cảnh yếu đi. Đã siết:

- đầu cột đổi thành **"Mẫu 10 bản ghi (đã rút)"**, ô 69,31 / 90,34 tô đỏ;
- chú thích bảng thêm câu **"Cả hai con số ở cột *mẫu 10 bản ghi* (69,31 và 90,34) đều ĐÃ BỊ RÚT"**;
- câu tường thuật thêm **"— con số đó nay đã bị rút"**.

Sau khi siết: DOCX từ 3 chỗ nghi vấn xuống **0**.

### 3.4 Bài báo: con số `22,33`

Xuất hiện một lần, trong đoạn rút lại mẫu 10 bản ghi. Đã viết lại cho rõ phạm vi, giữ nguyên độ dài:
*"The blind-to-oracle gap also shrinks, from 22.33 on the ten records to 7.47 on all 75"* (trước:
*"…shrinks with the larger sample, from 22.33 points to 7.47"*).

---

## VIỆC 4 — Cập nhật mục dải lọc bằng kết quả trên **chính TCN**

### 4.1 Tình trạng thí nghiệm đã đổi **trong lúc làm việc này**

Khi nhận nhiệm vụ, `pilot_evidence/band_tcn.py` mới xong 2/4 dải. Trong lúc E2 làm việc, tiến trình
đó **tự chạy xong cả bốn dải lúc 09:33 ngày 12/09/2026** (137,6 phút). E2 **không dừng, không sửa,
không giết** tiến trình — chỉ đọc tệp kết quả sau khi nó tự kết thúc.

### 4.2 Số liệu (nguồn: `pilot_evidence/band_tcn.json` → `pilot_evidence/band_tcn_stats.json`)

Giao thức: chính FetalQRS-TCN (đoạn 4 giây, đầu ra từng mẫu), 22 chủ thể, 3 nếp gấp tách theo chủ
thể, 4 epoch, **seed 0**, dung sai ±50 ms.

**Thang đo chính — chọn kênh PSD mù nhãn:**

| Dải | Macro F1 (%) | Hiệu so với 1–45 | KTC 95 % cluster bootstrap |
|---|---|---|---|
| 10–60 Hz | **98,07** ± 4,05 | **+2,44** | **[−0,04; +6,29] — chạm 0** |
| 3–90 Hz | 97,88 ± 4,76 | +2,25 | [−0,53; +6,62] — chạm 0 |
| 1–45 Hz | 95,63 ± 12,09 | mốc | — |
| 0,5–100 Hz | 95,51 ± 12,11 | −0,12 | [−1,01; +0,72] — chạm 0 |

**Thang đo thứ hai — trung bình cả 4 kênh (bỏ hẳn bước chọn kênh):** hiệu số 10–60 so với 1–45 là
**−0,07 điểm, KTC [−0,51; +0,39]** — bằng không **với khoảng hẹp**.

**Phân bố hiệu ứng:** trung vị hiệu số = **0,00**. Toàn bộ +2,44 do ba chủ thể tạo ra —
**B2_03 +37,8 · B1_06 +8,8 · B1_07 +8,2**; 19 chủ thể còn lại trung bình **−0,065 điểm**.

### 4.3 Ba điểm bắt buộc — đã viết vào **cả** đề cương lẫn bài báo

- **(a) Con số +11,00 đo trên GBM KHÔNG chuyển sang TCN ở cùng độ lớn.** Trên TCN chỉ còn **+2,44**,
  tức khoảng một phần năm. Viết ở: đề cương §1 (mục phát hiện 1), §5.2.1, §7 (mục C2), chú thích
  Hình 6/7/8, hàng bảng phân rã ba tầng; bài báo: tóm tắt, §3.3, Thảo luận, Hạn chế, Kết luận.
- **(b) KTC chạm số không → hiệu ứng KHÔNG được xác lập ở n = 22.** Không chỗ nào viết như thể nó đã
  được xác lập. Mọi phát biểu kiểu "front-end là tầng quan trọng nhất" nay đều bị **giới hạn phạm vi
  vào bộ học cửa sổ 300 ms**. Tiêu đề mục Thảo luận của bài báo đổi từ *"The front-end dominates"*
  thành *"The front-end dominates the 300 ms learner, not yet the network"*.
- **(c) Đây là KẾT QUẢ SƠ BỘ.** Cả bốn dải đã chạy xong, nhưng mới **một seed**, ba nếp gấp, bốn
  epoch. Ghi rõ trong chú thích bảng, chú thích hình, và điểm (c) của mục §5.2.1, kèm cam kết *"khi
  có thêm seed, con số +2,44 sẽ được cập nhật; nhóm cam kết báo cáo cả khi nó đi xuống"*.

**Con số +2,44 KHÔNG bị bỏ đi** dù nó yếu hơn +11,00. Ngược lại, nó được đặt ngay cạnh +11,00 trong
bảng phân rã ba tầng (thanh gạch chéo trong Hình 7) và trong đoạn phát hiện mở đầu.

### 4.4 Một phát hiện thêm được báo cáo trung thực

Thang đo "trung bình 4 kênh" cho hiệu số **bằng không với khoảng hẹp** (−0,07 [−0,51; +0,39]). Suy
ra (ghi rõ là **suy luận**, chưa phải kết luận đã kiểm chứng riêng): phần +2,44 trên thang PSD
**không đến từ việc dải lọc làm tín hiệu tốt hơn**, mà từ việc dải lọc làm **quy tắc chọn kênh** chọn
đúng hơn — và chỉ ở vài chủ thể. Đây là lý do nữa để không phát biểu "dải 10–60 Hz đáng +11 điểm"
như một sự thật chung.

### 4.5 Ba chủ thể lặp lại lần thứ ba

B2_03 / B1_06 / B1_07 — đúng ba bản ghi thua Power-MF 4 kênh nặng nhất và đúng ba hạng thấp nhất của
cổng từ chối. Giả thuyết **lưỡng cực** được nêu trong đề cương (§5.2.1) **dưới dạng giả thuyết cần
kiểm chứng**, kèm hệ quả nếu đúng: *F1 trung bình theo bản ghi là cách đo sai vì nó trộn hai chế độ*.

---

## VIỆC 5 — Chép sang `docs/` và kiểm MD5

| Tệp trong `docs/` | MD5 | Trùng với |
|---|---|---|
| `De_cuong_NCKH_RelyFetal.pdf` | `b80b63cceca2944f5a324bb25dba37f7` | `de_cuong_latex/de_cuong.pdf` ✔ |
| `De_cuong_NCKH_RelyFetal.docx` | `bc726483768b6cc89767491cdbf15a85` | `de_cuong_latex/De_cuong_NCKH_RelyFetal.docx` ✔ |
| `CinC2026_RelyFetal.pdf` | `c060cbfdb62f202ae44bdad8848afca2` | `paper/cinc2026/main.pdf` ✔ |

**Tệp trùng lặp trong `docs/`: 0.** Đã xoá `docs/de_cuong.pdf` (bản sao MD5 y hệt của
`docs/De_cuong_NCKH_RelyFetal.pdf`). Đã thêm mới `docs/CinC2026_RelyFetal.pdf` (trước đây bài báo
không có mặt trong `docs/`).

*Ghi nhận, không tự ý xoá:* `Bao_cao_30_paper.pdf` vẫn tồn tại ba bản MD5 y hệt
(`./`, `de_cuong_latex/`, `docs/`). Đây là mẫu hình có từ trước (thư mục nguồn + `docs/`) và có thể
đang được README trỏ tới, nên E2 **không** xoá mà chỉ báo cáo.

---

## Danh sách tệp đã sửa

**Mã sinh hình**
- `de_cuong_latex/make_figs.py` (bản lưu: `make_figs.py.bak_vong5`)
- `pilot_evidence/band_tcn_stats.py` — **mới**, dẫn xuất thống kê từ `band_tcn.json`
- `pilot_evidence/band_tcn_stats.json` — **mới**, mọi con số dải lọc trong tài liệu truy về tệp này

**Nguồn LaTeX đề cương** (mỗi tệp có bản lưu `.bak_vong5` nếu được sửa nhiều)
- `de_cuong_latex/sec_1_3.tex` — mục phát hiện 1 viết lại
- `de_cuong_latex/sec_4_6.tex` — §5.2.1 mới, bảng phân rã ba tầng, ba chú thích hình, hộp cảnh báo bảng bài học
- `de_cuong_latex/sec_7_12.tex` — giới hạn C2, bảng `tab:doansai_kenh`
- `de_cuong_latex/sec_cinc75.tex` — bảng `tab:cinc_lech`
- `de_cuong_latex/tables/bang_baihoc.tex` — sáu ô chứa con số đã rút

**Nguồn LaTeX bài báo**
- `paper/cinc2026/main.tex` (bản lưu: `main.tex.bak_vong5`)

**Bản dựng**
- `de_cuong_latex/de_cuong.pdf`, `de_cuong_latex/De_cuong_NCKH_RelyFetal.docx`
- `paper/cinc2026/main.pdf`
- `de_cuong_latex/figs/` — 12 hình sinh lại (24 tệp), 2 tệp xoá
- `docs/` — ba bản mới, một bản sao trùng lặp bị xoá

---

## Hạn chế còn lại (không tô hồng)

1. **Bảy hình `.png` mang từ nơi khác vào không kiểm được bằng cách trích văn bản** (fig9–fig12,
   fig14, fig15, và `.png` của fig0). Bằng chứng dùng thay là MD5 trùng khít tệp nguồn + `grep` mã
   sinh. Yếu hơn hẳn so với hai hình PDF.
2. **Kết quả dải lọc trên TCN mới một seed, 4 epoch.** Chưa đủ để gọi là kết quả cuối. KTC hiện chạm
   số không; thêm seed có thể đẩy nó về hai phía.
3. **Con số +11,00 vẫn chưa có KTC.** Artefact GBM cũ không lưu F1 từng bản ghi, nên ô "KTC 95 % mức
   chủ thể" của tầng 1 vẫn là *"chưa tính lại được"*.
4. **Suy luận ở §4.4 (hiệu ứng đi qua quy tắc chọn kênh chứ không qua dải lọc) chưa được kiểm chứng
   bằng một thí nghiệm riêng** — nó rút ra từ việc đối chiếu hai thang đo của cùng một lần chạy.
5. **`fig8_tin_hieu_dau_vao.*` là tệp mồ côi** còn nằm trong `figs/`. Vô hại nhưng chưa dọn.
6. **Ba bản sao `Bao_cao_30_paper.pdf`** vẫn còn, cố ý không xoá (xem Việc 5).
7. **Bộ phân loại ngữ cảnh dựa trên từ khoá**, không phải đọc hiểu. Ba báo động giả đã được E2 đọc
   tay và xác nhận; nhưng phương pháp này về nguyên tắc có thể bỏ lọt một câu rút lại viết bằng từ
   ngữ lạ.
