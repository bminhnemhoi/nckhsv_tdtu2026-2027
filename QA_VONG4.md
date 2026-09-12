> **Báo cáo vòng cũ — giữ để truy vết, KHÔNG phải trạng thái hiện hành.** Nhiều con số trong tệp này đã rút
> (mẫu 10 bản CinC; 75 bản CinC nhiễm 15 bản sao ADFECGDB; Power-MF cổng chuyển hỏng; +11,00 dải lọc; "8 kiến
> trúc"; "mô hình không phải nút thắt"; "Physiological Measurement là Q1"). Số hiện hành: `README.md` mục
> *Retractions* và `survey/facts_phase4.json`.

# QA vòng 4 — kiểm thử toàn diện, dọn repo, chuẩn bị commit

**Ngày:** 12/09/2026 · **Vai trò:** đảm bảo chất lượng (D3) · **Nhiệm vụ:** tìm lỗi, không phải xác nhận mọi thứ ổn.

Tài liệu này ghi lại đầy đủ những gì đã kiểm, những gì đã sửa, và — quan trọng hơn — **những gì vẫn còn
sai hoặc chưa làm được**. Mọi con số trích ở đây đều truy ngược được về một tệp JSON trên đĩa.

---

## 1. Kết quả kiểm thử

| Bộ kiểm thử | Lệnh | Kết quả |
|---|---|---|
| Kiểm thử đơn vị | `pytest tests/ demo/test_core.py` | **53 qua / 0 hỏng** |
| Kiểm tra demo | `python demo/run_check.py` | **thoát mã 0**, 32 bản ghi |

Chạy `pytest` **hai lần**: một lần trước khi sửa và một lần sau toàn bộ thay đổi của vòng này. Cả hai lần
đều **53/53**. Không có kiểm thử nào hỏng, nên **không phải sửa hay cập nhật kiểm thử nào**, và không có
API nào đổi.

Phân bố: `tests/test_api.py` 13 · `tests/test_baselines.py` 4 · `tests/test_fsqi.py` 6 ·
`tests/test_silesia_loader.py` 4 · `tests/test_smoke.py` 16 · `demo/test_core.py` 10.

Cảnh báo duy nhất là `StarletteDeprecationWarning` của FastAPI (`httpx` → `httpx2`), thuộc thư viện ngoài,
không phải lỗi của repo.

### `demo/run_check.py` — 32 bản ghi, hai chế độ cổng

| Chế độ | Đèn cao | Đèn trung bình | Đèn thấp | XANH nhưng F1 < 90 | ĐỎ nhưng F1 ≥ 95 |
|---|---|---|---|---|---|
| `hoc` (học được) | 14 bản, F1 TB 99,92 | 9 bản, 98,66 | 9 bản, 44,99 | **0** | **0** |
| `luat` (luật tay) | 22 bản, F1 TB 99,41 | 7 bản, 58,18 | 3 bản, 32,48 | **0** | **0** |

Không có **lỗi nguy hiểm** nào (đèn xanh trên bản ghi kém). Kết quả ghi ở
`demo/results/demo_check_2modes.json`.

> **Quan sát cần nêu:** `run_check.py` dùng **checkpoint production**, nên F1 của nó thấp hơn số trong
> `eval_22.json` (dùng checkpoint theo fold, không thấy bản ghi kiểm thử). Ví dụ B1_07: 58,72 ở
> `run_check` so với 86,56 trong bảng Power-MF. **Đây không phải mâu thuẫn** — hai thứ đo hai mô hình
> khác nhau. Nhưng cùng ba bản ghi B1_07 / B1_06 / B2_03 lại là bản yếu nhất ở **cả hai** cách đo, nên đó
> là điểm yếu thật của mô hình chứ không phải ngẫu nhiên của một lần chấm.

---

## 2. Số liệu sai đã sửa

### 2.1 Nguyên tắc áp dụng

- **Giữ** mọi số thô trong tệp kết quả thí nghiệm (`*_results.json`, `eval_*.json`, `pilot_evidence/*.json`).
- **Sửa hoặc đóng khung rút lại** mọi chỗ *diễn giải* hoặc *tuyên bố*.
- Nơi con số cũ có giá trị lịch sử (nhật ký, hồ sơ liêm chính), **giữ nguyên nhưng gắn nhãn RÚT LẠI ngay
  tại chỗ** — không xoá lặng lẽ.

### 2.2 Bảng số đúng (nguồn: `baselines/powermf_fair_stats.json`, `powermf_1ch.json`, `benchmark_dpss/eval_cinc75.json`)

Đã **tự kiểm chứng lại từ JSON** bằng script, không chép tay:

| Tập | n | Power-MF 4 kênh | Power-MF 1 kênh | RelyFetal 1 kênh |
|---|---:|---:|---:|---:|
| ADFECGDB | 5 | 99,01 | 92,37 | **99,40** |
| Silesia B2 | 7 | 97,90 | 87,28 | 96,82 |
| Silesia B1 | 10 | **99,40** | 83,48 | 97,15 |
| **Tất cả 22** | 22 | **98,83** | 86,71 | 97,56 |
| CinC 75 | 75 | chưa chạy | 62,82 | **79,40** |

Trung vị hiệu số RelyFetal − PMF4 trên 22 chủ thể = **+0,23**; thắng **18/22**.

### 2.3 Danh sách từng tệp, từng chỗ đã sửa

| # | Tệp | Chỗ | Cũ | Mới |
|---|---|---|---|---|
| 1 | `README.md` | bảng 5 cấu hình, hàng CinC | 10 bản ghi → F1 **59.15**, KTC [38.32; 81.01], TB 4 kênh 61.96 | 75 bản ghi → F1 **71.21**, SD 33.96 / trung vị 94.34, TB 4 kênh 64.78 |
| 2 | `README.md` | dưới bảng | (không có) | chú thích ¹ rút lại 59.15, nêu rõ không bịa KTC cho 75 bản ghi |
| 3 | `README.md` | đoạn lưỡng cực | `~38 điểm; 4/10 hoàn hảo, 5/10 dưới 50` | `~26 điểm; 15/75 hoàn hảo, 22/75 dưới 50` |
| 4 | `README.md` | cả mục CinC | bảng chính `59.15/69.31/77.34/90.34`, `22.33 điểm` | bảng `71.21/79.40/58.72/69.33/86.87`, `7.47 điểm`, hộp rút lại |
| 5 | `README.md` | sau mục baseline | (không có mục Power-MF) | mục Power-MF mới: hộp rút lại, kiểm chứng ngoài 99.40 vs 99.46, bảng 3 cột, thống kê, luận đề 89.5 % |
| 6 | `README.md` | cấu trúc kho mã | `powermf_status.json  Why Power-MF could not be re-run locally` | 4 dòng mới trỏ tới `powermf_fair_run.py`, `powermf_1ch.py`, `findpeaks_mpd.m`, `BASELINES.md` |
| 7 | `README.md` | khối chạy lại | `# 24 tests` | `# 53 tests` |
| 8 | `README.md` | hạn chế | `69.3 … (90.3 only with a post-hoc fixed lead)` | `79.4 … (all 75 records)` |
| 9 | `README.md` | hạn chế | `Only 10 of the 75 CinC records were evaluated` | đã chạy đủ 75 + 68; hạn chế thật là **không dùng bộ chấm chính thức** |
| 10 | `README.md` | hạn chế | `Power-MF was not re-run … its 98.0 % remains a published number` | đã chạy lại, nhưng chưa chạy trên CinC; **thêm** hạn chế dải lọc +11.00 đo trên GBM chứ chưa trên TCN |
| 11 | `README.md` | trích dẫn | `v3.1` | `v3.3` |
| 12 | `README.md` | trước mục Citation | (không có) | bảng **"What is verified, and what is not"** (14 dòng) |
| 13–24 | `README.vi.md` | — | *y hệt 12 mục trên, bản tiếng Việt* | — |
| 25 | `docs/README_KET_QUA.md` | mục 2 | bảng `94,87 / +2,74 / 98,38 / 97,33`, 18 và 16 bản ghi | hộp rút lại + kiểm chứng ngoài + bảng 22 chủ thể 3 cột + bảng ba bản ghi thua + luận đề đúng |
| 26 | `paper/cinc2026/CHANGELOG.md` | Bảng 2 vòng B2 | bảng "bắt buộc giữ" với `98.38 / 94.87` | đóng khung ⛔ RÚT LẠI, gạch ngang toàn bảng, trỏ sang `tab:pmf` của `main.tex` |
| 27 | `analysis/CLINICAL.md` | mục 5 | `dùng quy tắc PSD mù nhãn (F1 69,31)` nêu như sự kiện | thêm hộp RÚT LẠI: 79,40 trên 75 bản ghi, kênh 0 chỉ 69,33; ghi rõ phân tích lâm sàng **chưa chạy lại** |
| 28 | `analysis/STATS.md` | 2 nhãn hàng bảng | `(90,34 da cong bo)`, `(77,34 da cong bo)` | `(90,34 DA RUT …)`, `(77,34 DA RUT …)` |
| 29 | `analysis/STATS.md` | dưới bảng | (không có) | ghi chú rút lại: KTC trong bảng chỉ đúng cho mẫu 10, không mô tả kết quả hiện hành |
| 29b | `analysis/STATS.md` | dòng giải thích cột KTC | `đại lượng mà bài báo đang báo cáo (99,21 / 93,30 / 90,34)` | `… và cho CinC là **79,40 trên đủ 75 bản ghi**; 90,34 đã bị rút` |
| 30 | `fsqi/README.md` | hạn chế | `số 77,34 đã công bố trước đó` | thêm ghi chú 77,34 **đã rút**, số đúng 71,21 / 79,40 |
| 31 | `survey/facts_phase2.json` | `SUA_LIEM_CHINH.1_con_so_chinh_cinc` | `con so CinC phai bao la 69,31` | đã rút; số đúng 79,40; luận điểm liêm chính **mạnh lên** vì kênh 0 chỉ 69,33 |
| 32 | `survey/facts_phase2.json` | `.2_quy_tac_chon_kenh…` | `kem oracle 22,33 diem` | `22,33` đã rút → **7,47** trên 75 bản ghi |
| 33 | `survey/facts_phase2.json` | `.5_cinc_10_tren_75` | "sẽ phải chạy" | **đã hoàn thành**: 75 → 79,40; 68 → 80,70 |
| 34 | `survey/facts_phase2.json` | `F_cinc2013_production22` | `CON_SO_CHINH: PSD 69,31`, `vai_tro: CON SO CHINH`, `ket_luan`, `canh_bao` | thêm `TRANG_THAI` rút lại; mọi trường diễn giải viết lại; **giữ nguyên số thô** |
| 35 | `survey/facts_phase3.json` | `A_powermf_chay_lai` | toàn mục dựa trên bản hỏng | **viết lại hoàn toàn** — xem §3 |
| 36 | `survey/facts_verified.json` | đầu tệp + `xuyen_bo_du_lieu_cinc2013` | `59,15 so voi 77,34` nêu như sự kiện | banner `DA_RUT_CinC_2026_09_12` + gắn nhãn tại chỗ; nêu rõ **PSD HƠN kênh cố định 12,49 điểm** trên đủ mẫu |
| 37 | `survey/scout_baselines.md` | bảng đối chuẩn | `— (ta chỉ chạy 10/75 → 90,34)` | `79,40 (đủ 75 bản ghi, PSD mù nhãn)` |
| 38 | `survey/scout_baselines.md` | đoạn diễn giải | `ta đạt 90,34 trên 10 bản ghi tự chọn` | `79,40 trên cùng 75 bản ghi` + cảnh báo **không cùng bộ chấm** với Varanini |
| 39 | `survey/scout_datasets.md` | cảnh báo rò rỉ | `"CinC 2013 zero-shot 90,34"` | ghi chú rút lại + 79,40; cảnh báo nguồn gốc hỗn hợp **vẫn nguyên giá trị** |
| 40 | `survey/scout_datasets.md` | khuyến nghị 6 | `"zero-shot 90,34" chưa chắc zero-shot` | `79,40` (90,34 đã rút) |
| 41 | `baselines/powermf_status.json` | đầu tệp | `kha_thi_chay_tai_cho: false` + `ly_do: khong co MATLAB/Octave` | banner `TRANG_THAI_2026_09_12`: trường đó **đã sai**, Power-MF đã chạy lại được |
| 42 | `benchmark_dpss/eval_22.py:72` | `CINC_REF_STATED` | hằng số trần trụi `77.34 / 59.15` | thêm chú thích: số **đã rút**, chỉ dùng kiểm tra hồi quy trên đúng 10 bản ghi cũ |
| 43 | `de_cuong_latex/make_figs.py` | `fig_bimodal` | nhãn `trung bình 77,34` | `TB mẫu 10 bản ghi, kênh 0 cố định: 77,34 (hậu kiểm — đã rút)` |
| 44 | `de_cuong_latex/make_figs.py` | `fig_m22` + `__main__` | hàm dùng `77.34/90.34` vẫn **được gọi** | đánh dấu đã rút + **bỏ lời gọi**; chỉ còn `fig_m22_v2` (71,21/79,40) |
| 45 | `de_cuong_latex/fix_stale.py` | đầu tệp | script sẽ ghi `77,34` vào `survey_raw.json` nếu chạy lại | **chặn chạy** bằng `raise SystemExit` + giải thích |

### 2.4 Hai lỗi tiềm ẩn — đáng chú ý nhất của vòng này

Hai mục #44 và #45 **không phải lỗi chữ nghĩa mà là bẫy sẽ tự tái sinh số đã rút**:

1. `make_figs.py` vẫn **đang gọi** `fig_m22()` trong `__main__`. Ai chạy lại bộ sinh hình sẽ tạo lại
   `fig16_m22.pdf` với cột CinC = 90,34. Hình đó hiện **không** được `\includegraphics` (đề cương dùng
   `fig19_m22_v2`), nhưng tệp vẫn nằm trong `de_cuong_latex/figs/` và chỉ cách một dòng `\includegraphics`
   là vào bài. Đã bỏ lời gọi.
2. `fix_stale.py` có luật `77,52 → 77,34`. Chạy lại script này sẽ **ghi con số đã rút vào
   `survey/survey_raw.json`**. Đã chặn bằng `raise SystemExit`.

### 2.5 Những chỗ CỐ Ý giữ nguyên

| Nơi | Vì sao giữ |
|---|---|
| `benchmark_dpss/eval_22.json`, `eval_cinc75.json`, `pilot_evidence/*.json`, `baselines/*_results.json` | **số thô thí nghiệm** — sửa là làm giả dữ liệu |
| `analysis/stats_results.json` (`gia_tri_bao_cao_cu: 90.34 / 77.34`) | tên trường đã tự nói là "giá trị báo cáo **cũ**" |
| `de_cuong_latex/data_v33.json` | đã có khoá `DA_RUT_powermf` do vòng trước gắn — **đã kiểm, đúng** |
| `de_cuong_latex/sec_*.tex`, `paper/cinc2026/main.tex` | **đã được sửa trong lúc vòng này đang chạy** — kiểm lại thấy đã có hộp rút lại và bảng 3 cột đúng |
| `survey/review_round2*.{md,json}` | biên bản phản biện vòng 2, là hồ sơ lịch sử |
| `paper/cinc2026/CHANGELOG.md` mục đầu | đã có bảng "con số đã rút" do vòng B3 thêm; mục #26 bổ sung gạch ngang tại chỗ cho bảng vòng B2 |

### 2.6 Tuyên bố "8 kiến trúc không phân biệt được"

Đã grep toàn repo. **Không còn chỗ nào nêu như sự kiện.** Mọi lần xuất hiện đều nằm trong câu rút lại
(`analysis/STATS.md`, `stats.py`, `docs/README_KET_QUA.md`, `README.vi.md`, `de_cuong_latex/sec_*.tex`,
`survey/facts_phase2.json`). Không cần sửa.

### 2.7 Từ cấm

Grep `SOTA` / `novel` / `first` / `state-of-the-art` trong `*.md` và `*.tex`: các lần xuất hiện đều là
**câu tự cấm** ("không được dùng chữ SOTA", "TUYỆT ĐỐI KHÔNG…") hoặc mô tả công trình của **người khác**.
Không có chỗ nào tự nhận. Mục Power-MF mới trong cả hai README kết bằng câu tự giới hạn rõ ràng.

---

## 3. `survey/facts_phase3.json` đã viết lại

Cấu trúc mới:

| Khoá | Nội dung |
|---|---|
| `A_powermf_DA_RUT_ban_cu` | **mới** — giữ lại 3 bộ số cũ (94,87 / 98,38 / 97,33 …) kèm `TRANG_THAI: DA RUT TOAN BO`, nguyên nhân O(k²), giả thuyết 340 ms bị bác bỏ bằng RR thật, cách vá, ảnh hưởng |
| `A2_powermf_sau_va_P7` | **mới** — kiểm chứng ngoài (99,40 vs 99,46), bảng F1 theo tập, thống kê mức chủ thể, khối `PHAN_BO_KHONG_DOI_XUNG_phai_neu_ro` (trung vị +0,23, 18/22, ba bản ghi thua), khối `LUAN_DE_DUNG` kèm điều cấm |
| `A3_powermf_1ch` | **mới** — định nghĩa Power-MF-1ch, vì sao cần, kết quả 22 chủ thể + CinC 75/68 |
| `B_cinc75` | thêm `SO_CHINH`, viết lại `sua_so_cu`, thêm `khoang_cach_PSD_den_oracle_DA_SUA` (22,33 → 7,47) |
| `dang_chay` | chỉ còn `band_tcn`, ghi rõ đã xong dải 10–60 Hz = 98,07 ± 4,05, còn 3 dải, **cấm động vào** |
| `con_thieu_de_len_Q1` | đổi từ danh sách chuỗi sang danh sách có `trang_thai`: **3 mục XONG** (Power-MF 1 kênh, lỗi cổng chuyển, ablation bỏ B1), 1 **DANG CHAY** (dải lọc), 3 **CHUA XONG** |

Khoá cũ `A_powermf_chay_lai` đã bị xoá; toàn bộ nội dung còn giá trị đã chuyển sang `A_powermf_DA_RUT_ban_cu`
và `A2_powermf_sau_va_P7`.

---

## 4. README.md và README.vi.md

Cả hai đã có: bảng Power-MF **3 cột**, mục CinC dùng **79,40 trên 75 bản ghi**, và bảng
**"điều gì đã kiểm chứng / điều gì chưa"** (mới thêm, trước đây **không** có).

| Hạng mục | Trạng thái |
|---|---|
| `LICENSE` | **có** (2 678 byte, MIT cho mã + CC BY 4.0 cho tài liệu) |
| `CITATION.cff` | **có** |
| Hướng dẫn cài đặt | **có**, cả hai bản |
| Hướng dẫn chạy lại từng con số | **có**, cả hai bản (đã sửa `24 tests` → `53 tests`) |
| Bảng "đã kiểm chứng / chưa" | **đã bổ sung vòng này** |
| Bảng Power-MF 3 cột | **đã bổ sung vòng này** |

Bảng mới phân biệt ba mức: *đo lại được trong repo* · *kiểm chứng NGOÀI* (chỉ Power-MF, đối chiếu 99,40 với
99,46 của tác giả) · *ĐÃ RÚT / KHÔNG dùng được*. Ba dòng nói thẳng là **không**: dùng làm máy đo STV độc lập,
độ chính xác thời điểm trên B1, và điểm so được với bảng xếp hạng CinC.

### Ba tệp `.bak_integrity`

`README.md.bak_integrity` · `README.vi.md.bak_integrity` · `survey/facts_phase2.json.bak_integrity`

Đây là bản sao chụp **trước** lần sửa liêm chính sáng 12/09. Nội dung của chúng đã bị thay thế hoàn toàn bởi
lịch sử git và bởi các hộp rút lại viết ngay trong tài liệu.

> **ĐỀ XUẤT XOÁ — chưa tự xoá.** Đã thêm `*.bak_integrity` vào `.gitignore` nên chúng **không vào commit**.
> Chủ nhiệm đề tài quyết định có xoá khỏi đĩa hay không.

---

## 5. `.gitignore` và chuẩn bị commit

### 5.1 Cảnh báo — một vấn đề bản quyền thật

> **`baselines/octave/` chứa mã nguồn MATLAB của chính tác giả Power-MF và sẽ bị commit nếu không chặn.**
>
> `PowerMF.m`, `PowerMF.m.bak_a2`, `PowerMF_dbg.m`, `matched_filter.m` đều mang tiêu đề
> `Author: Katharina M. Jaeger, katharina.jaeger@fau.de`. Đây **đúng cùng loại tệp** mà `.gitignore` đã cố ý
> loại qua `tools/` với lý do *"KHÔNG tái phân phối mã nguồn bên thứ ba"* — nhưng bản sao trong
> `baselines/octave/` thì **chưa bị chặn**. Nếu commit, repo sẽ tái phân phối đúng thứ đã tuyên bố không
> tái phân phối.
>
> **Đã thêm vào `.gitignore`.** Chỉ giữ lại các tệp **do nhóm viết**: `findpeaks_mpd.m` (bản vá P7),
> `test_fpmpd.m`, `run_powermf.m`, `apply_patches.py`. Người khác dựng lại môi trường bằng
> `python baselines/powermf_setup.py` rồi `python baselines/octave/apply_patches.py`, đúng như với `tools/`.

### 5.2 Các mục khác đã thêm vào `.gitignore`

| Mục | Lý do | Dung lượng |
|---|---|---|
| `baselines/octave/{PowerMF.m, PowerMF.m.bak_a2, PowerMF_dbg.m, matched_filter.m}` | mã nguồn bên thứ ba | ~23 KB |
| `baselines/octave/{_dbg_fp.m, _dbg_fp2.m, _mkdbg.py}` | script chẩn đoán một lần, **nhúng đường dẫn tuyệt đối `D:/…` của máy cá nhân** | ~4 KB |
| `analysis/gate22_cache/` | bộ nhớ đệm đặc trưng, tái tạo được, 27 tệp | **2,4 MB** |
| `docs/de_cuong.pdf` | **trùng byte-for-byte** với `docs/De_cuong_NCKH_RelyFetal.pdf` (cùng MD5 `112d8a63…`) | **3,26 MB** |
| `de_cuong_latex/_check.txt` | sản phẩm phụ khi dựng DOCX | 0,32 MB |
| `*_stdout.txt` | trùng nội dung với `*_log.txt` có cấu trúc; luật cũ chỉ chặn lẻ tẻ vài tệp | ~0,1 MB |
| `*.bak_integrity` | bản sao trước khi sửa, git đã giữ lịch sử | ~39 KB |

### 5.3 Kết quả

| | Trước | Sau |
|---|---:|---:|
| Số mục trong `git status --short` | 133 | **118** |
| Tệp thực sự vào commit | 197 | **148** |
| Dung lượng vào commit | 18,45 MB | **12,44 MB** |

`git count-objects -vH`: `count: 343, size: 26.03 MiB` (chưa đóng gói — đây là repo chưa `gc`, không đáng lo).

**Không có tệp nào > 10 MB.** Tệp lớn nhất còn lại là `docs/De_cuong_NCKH_RelyFetal.pdf` (3,26 MB) và
`docs/De_cuong_NCKH_RelyFetal.docx` (2,33 MB) — là sản phẩm bàn giao, giữ là hợp lý.

Đã xác nhận **không** commit: `tools/` (Octave ~2 GB) · `model/data/` · `*.npz` ·
`baselines/powermf_work/` · `goi-danh-gia-doi-chuan-dpss/` · `papers/`.

### 5.4 Thông điệp commit

Đã soạn sẵn (tiếng Anh, nhiều dòng) tại:

```
C:\Users\Admin\AppData\Local\Temp\claude\d--NCKHSV2026-2027\6d28f72f-143e-44dc-8fc9-44a5055f6415\scratchpad\COMMIT_MESSAGE.txt
```

> **KHÔNG chạy `git commit` và `git push`.** Chủ nhiệm đề tài tự quyết định.

---

## 6. Hạn chế và việc còn tồn của chính vòng QA này

Phần này liệt kê những gì **chưa** làm được, để không ai hiểu nhầm là repo đã sạch hoàn toàn.

1. **Không kiểm chứng lại được hai bảng `.tex` bằng cách dựng PDF.** `de_cuong.pdf` và `main.pdf` trong
   commit là bản dựng **trước** một số sửa của vòng này. Cần chạy lại `pdflatex` và `make_docx.py` trước khi
   nộp. `de_cuong_latex/_flat.tex` là tệp sinh ra và đã bị `.gitignore`, nhưng bản trên đĩa hiện vẫn chứa
   bảng Power-MF cũ — nó sẽ đúng sau khi chạy lại `make_docx.py`.
2. **Các hình trong `de_cuong_latex/figs/` chưa sinh lại.** `fig16_m22.pdf` (chứa 90,34) và
   `fig6_luong_cuc.pdf` (nhãn 77,34 cũ) vẫn là bản cũ trên đĩa. Đã sửa **mã sinh hình**, nhưng phải chạy
   `python de_cuong_latex/make_figs.py` thì tệp mới đổi. **Đề xuất xoá hẳn `figs/fig16_m22.{pdf,png}`** vì
   không còn tài liệu nào dùng.
3. **`analysis/CLINICAL.md` và `fsqi/README.md` mới được gắn nhãn rút lại, chưa chạy lại trên 75 bản ghi.**
   Các cặp F1/STV và toàn bộ thí nghiệm cổng từ chối vẫn đo trên mẫu 10 bản ghi. Đã ghi rõ điều này ngay
   trong hai tài liệu, nhưng **đó là nợ thí nghiệm, không phải nợ chữ nghĩa**.
4. **Power-MF đa kênh chưa chạy trên CinC 2013.** Cột đó trong mọi bảng vẫn là "chưa chạy". Cho tới khi
   chạy, mọi so sánh xuyên hệ ghi với Power-MF đều **chỉ** có ở cấu hình đơn kênh.
5. **Con số +11,00 điểm của dải lọc vẫn đo trên GBM cửa sổ 300 ms, không phải trên TCN.**
   `pilot_evidence/band_tcn.py` đang chạy (đã xong 10–60 Hz = 98,07 ± 4,05, còn 3 dải). Vòng này **không
   động vào** tiến trình đó. Hạn chế này đã được thêm vào mục "Hạn chế" của **cả hai** README.
6. **Chưa kiểm chứng độc lập được `baselines/BASELINES.md`** — tài liệu do agent A2 viết. Đã đối chiếu mọi
   con số trong đó với `powermf_fair_stats.json` bằng script và **khớp**, nhưng chưa chạy lại
   `powermf_fair_run.py` từ đầu (cần Octave, ~48 s/bản ghi × 22, và có tiến trình khác đang chiếm máy).
7. **Không chạy `api/check_server.py` và `baselines/powermf_check.py`** — cái đầu cần server đang chạy, cái
   sau cần Octave. `tests/test_api.py` đã phủ API bằng `fastapi.testclient` nên phần API vẫn có kiểm thử.
8. **Grep dựa trên chuỗi số.** Nếu một con số đã rút bị viết ở dạng khác (làm tròn `94.9`, tách chữ, hoặc
   nằm trong ảnh/PDF) thì grep không bắt được. Đã quét `*.md`, `*.tex`, `*.py`, `*.json`, `*.txt`, `*.cff`,
   `*.yml`. **Không quét được nội dung PDF và DOCX.**
9. **`de_cuong_latex/sec_*.tex` và `paper/cinc2026/main.tex` bị sửa bởi agent khác trong lúc vòng này đang
   chạy.** Đã grep lại lần cuối sau khi họ xong và xác nhận đúng, nhưng nếu họ còn sửa tiếp thì kết luận ở
   §2 có thể lệch. **Nên grep lại ngay trước khi commit.**

---

## 7. Lệnh grep để chủ nhiệm tự kiểm lại

```bash
cd D:/NCKHSV2026-2027
for p in "94[.,]87" "98[.,]38" "97[.,]33" "90[.,]34" "77[.,]34" "69[.,]31" "59[.,]15" "22[.,]33"; do
  echo "=== $p ==="
  grep -rnE "(^|[^0-9])$p([^0-9]|$)" --include=*.md --include=*.tex --include=*.py --include=*.json . \
    | grep -vE "^\./(papers|tools|goi-danh-gia-doi-chuan-dpss|model/data)/"
done
```

Mọi dòng trả về phải rơi vào **một** trong ba loại: (a) nằm trong câu rút lại rõ ràng, (b) là số thô trong
tệp kết quả thí nghiệm, (c) là hồ sơ lịch sử đã gắn nhãn. **Nếu có dòng thứ tư, đó là lỗi còn sót.**
