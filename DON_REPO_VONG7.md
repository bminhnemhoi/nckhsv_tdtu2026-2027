# DỌN REPO VÒNG 7 — biên bản (R3, 12/09/2026)

Phạm vi: dọn dư thừa, đồng bộ mọi con số về 60 bản CinC sạch và bốn đính chính của vòng 7, biên dịch lại
bài báo và đề cương, tạo `survey/facts_phase4.json`, chạy kiểm thử, commit và push.
Mọi con số dưới đây truy ngược về JSON ghi trong `survey/facts_phase4.json` (trường `nguon`).

## 1. Bốn đính chính được đưa vào toàn repo

| # | Đính chính | Phát biểu đúng đã dùng | Tệp nguồn |
|---|---|---|---|
| 1 | Chồng lấn CinC set-a ↔ ADFECGDB **không phải phát hiện của nhóm** | "Như ban tổ chức đã ghi nhận [Silva 2013 Bảng 1; Clifford 2014 Bảng 2 + cảnh báo Rodrigues], set-a chứa bản ghi ADFECGDB; chúng tôi xác định bằng đo lường đúng 15 bản nào (a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25; cửa sổ 0–60/120–180/240–300 s; NCC = 1,0000) và mức thổi phồng 3,27–7,18 điểm." Câu cảnh báo đã nằm trong ghi chú p20 của nhóm — nhóm bỏ sót. | `survey/RO_RI_VANLIEU.md`, `survey/ro_ri_vanlieu.json` |
| 2 | **Không có bộ thứ ba có nhãn fQRS thật** | NIFEADB không .qrs/.atr; NInFEA không nhãn nhịp; nifecgdb `.qrs` là QRS mẹ (RR 0,695 s); set-b chưa công bố → peakprob vẫn là giả thuyết mạnh, chưa thể lặp lại | `analysis/xacnhan_results.json → viec2_bo_thu_ba` |
| 3 | Trên thang logit, **gate vẫn dẫn 22 chủ thể** (kẹp A/B; rrcv kẹp C), peakprob hạng 3/4/6; trên 60 bản sạch logit: gate4 dẫn | vấn đề hậu kiểm KHÔNG biến mất (khai báo trước neo git `ed819e3`) | `analysis/xacnhan_results.json → viec3_logit_22` |
| 4 | **Rút "mô hình không phải nút thắt"** | phép thử nhìn thấy âm tính giả 18,0 % [12,1; 25,0] trên 60 bản sạch (ngưỡng 10 %), 55–70 % trên bản khó; hiệu chỉnh 86,0 % → 26,0 % nhưng không định danh được → "chưa chứng minh được là hay không là nút thắt" | `analysis/xacnhan_results.json → viec4_phep_thu_nhin_thay` |
| 5 | Seed | không có checkpoint seed 1; F1 PSD 97,56 vs 97,59, +0,03 [−0,18; +0,34] → ổn định trong miền, không nói gì ngoài miền | `analysis/xacnhan_results.json → viec5_seed` |
| 6 | Venue | *Physiological Measurement* là Q2/Q3 Scimago 2024, **không phải Q1**; Q1: JBHI, TBME, BSPC, CBM, AI in Medicine | `docs/CHIEN_LUOC_CONG_BO.md` |

Số chính (60 bản sạch, `benchmark_dpss/eval_cinc60_sach.json`, `analysis/dulieu_results.json → chon_kenh_60_sach`):
psd 74,28 · gate 80,72 · gate4 81,01 · rrcv 80,00 · peakprob 82,01 · oracle 83,60; peakprob − psd = +7,73
[+3,82; +12,41], p = 5,6e-04, p_Holm = 0,0039; gate p_Holm = 0,0505 (trượt). 22 chủ thể: PMF4 98,83 · PMF1 86,71 ·
Rely 97,56; Rely − PMF4 = −1,27 [−3,08; +0,27]; Rely − PMF1 = +10,85; 89,5 %.

## 2. VIỆC 1 — kiểm kê dư thừa

| Tệp | Lý do | Xử lý |
|---|---|---|
| `de_cuong_latex/{make_figs.py,sec_1_3.tex,sec_4_6.tex,sec_7_12.tex,tables/bang_baihoc.tex}.bak_vong5` (5, đang theo dõi git) | bản sao lưu trước v3.4; bản gốc có trong lịch sử git (`8b85310`) | `git rm` |
| `README.md.bak_integrity`, `README.vi.md.bak_integrity`, `paper/cinc2026/main.tex.bak_integrity`, `paper/cinc2026/refs.bib.bak_integrity`, `survey/facts_phase2.json.bak_integrity` (5, gitignore) | bằng đúng blob tại `da17651` / `d4b44f2` (đã đối chiếu hash) | xoá khỏi đĩa |
| `paper/cinc2026/main.tex.bak_{b2,b3,round2,vong5}`, `refs.bib.bak_b2` (5, gitignore) | bản trung gian các vòng, nội dung có trong lịch sử | xoá khỏi đĩa |
| `de_cuong_latex/patch_{bia,doansai,fig,readme,v34}.py`, `show_input.py` (6) | script vá một lần đã chạy, không tệp nào gọi (kiểm bằng grep tên trên toàn repo) | `git mv` → `archive/de_cuong_patch_scripts/` |
| `benchmark_dpss/_watch_eval22.py`, `baselines/powermf_status_update.py` (2) | script theo dõi/cập nhật trạng thái dùng một lần, không ai gọi | `git mv` → `archive/one_off_scripts/` |
| `model/train_22_stdout.txt`, `pilot_evidence/sample_stdout.txt` (2) | trùng byte / trùng nội dung với `*_log.txt` tương ứng; `.gitignore` đã có `*_stdout.txt` | `git rm --cached` (giữ trên đĩa) |
| `baselines/octave/PowerMF.m.bak_a2`, `PowerMF_dbg.m`, `_dbg_fp.m`, `_dbg_fp2.m`, `baselines/powermf_work/_dbgvars.mat` | mã bên thứ ba / chẩn đoán một lần; **đã gitignore từ vòng 4**, không nằm trong repo | giữ nguyên trên đĩa (không phân phối) |
| `tools/octave/.../*.orig`, `_dbg_*.h` | thuộc GNU Octave portable, gitignore | không đụng |
| `paper/cinc2026/figs/*` (8 tệp) | không hình nào được `\includegraphics` trong `main.tex` (bài 4 trang không còn chỗ) | **giữ** — ứng viên chèn khi có template CinC chính thức; ghi nhận ở đây |
| `de_cuong_latex/figs/*` | tất cả được tham chiếu trong `.tex`/`make_figs.py` | giữ |
| `model/checkpoints/*.pt` (20) | 5 fold + production (5 ca), 12 ca, 11 fold + production (22 ca) — đều được `demo/core.checkpoint_for` / `eval_*.py` tham chiếu | giữ |
| 18 script `.py` không được gọi từ đâu (kiểm bằng grep) | ngoài 8 tệp đã chuyển, còn lại là điểm vào hợp lệ (`gen_tables.py`, `gen_baocao_paper.py`, `make_docx_baocao.py`, `powermf_published_extract.py`, `inspect_ckpt.py`, `adapt_hp_select.py`, `make_report.py`, `chandoan_capacity_parse.py`, `dulieu_exp_md.py`, `powermf_table.py`) | giữ |
| `de_cuong_latex/_check.txt`, `_flat.tex`, `_build*.txt` | sản phẩm phụ build, gitignore | không đụng |

`archive/README.md` liệt kê nội dung và lý do.

## 3. VIỆC 2 — đồng bộ số liệu (chỗ đã sửa)

| Tệp | Sửa gì |
|---|---|
| `README.md` | chú thích ¹ viết lại theo phát biểu đúng (ban tổ chức đã ghi nhận); "bimodal" → mô tả; ràng buộc (4)(5) peakprob: không bộ thứ ba, logit gate/gate4; seed +0,03, không checkpoint seed 1; mục hạn chế "không phải nút thắt" → rút, âm tính giả 18 %; bảng kiểm chứng (3 hàng mới); bảng *Retractions* thêm 5 hàng ("phát hiện rò rỉ", nút thắt/71 %/1,85, kế hoạch lặp lại bộ thứ ba, seed, PM là Q1); demo: bảng đèn hai chế độ trên 82 bản (17:07); cấu trúc thư mục; lệnh tái lập |
| `README.vi.md` | viết lại toàn bộ theo README.md (bản cũ còn ở trạng thái vòng 5: 75 bản, 79,40, "8 kiến trúc") |
| `paper/cinc2026/main.tex` | tóm tắt, đóng góp, mục Data (trích Silva 2013 + Clifford 2014, 15 bản đo được), Bảng 1 hàng CinC (64,04 [55,4; 72,5]), Bảng 2 hàng CinC (55,97 / 74,28 / +18,32 [13,4; 23,6]), **mục 3.3 viết lại** (60 bản sạch, Bảng 3 mới, peakprob = giả thuyết, không bộ thứ ba), thảo luận (9,32; +10,24; DA thất bại; âm tính giả 18 %), kết luận; cắt gọn để đúng **4 trang** (lề 2,0/1,75 cm) |
| `paper/cinc2026/refs.bib` | thêm `silva2013` |
| `paper/cinc2026/CHANGELOG.md` | mục vòng 7 + header |
| `de_cuong_latex/de_cuong.tex` | phiên bản 3.5; mục tiêu công bố (PM Q2/Q3; JBHI/BSPC nếu có bộ thứ ba); hộp ghi chú bìa: rút toàn bộ số 75 bản, phát biểu đúng về chồng lấn |
| `de_cuong_latex/sec_cinc75.tex` | **hộp RÚT LẠI** đầu mục: nguồn Silva/Clifford, 15 bản, bảng 60 bản sạch đầy đủ, peakprob/gate/logit/bộ thứ ba; các bảng 75 bản giữ và đánh dấu đã rút |
| `sec_1_3.tex`, `sec_4_6.tex`, `sec_7_12.tex`, `sec_powermf.tex`, `sec_model22.tex`, `sec_silesia.tex`, `tables/bang_baihoc.tex` (p20) | thay số chính sang 60 bản sạch hoặc thêm câu rút lại tại chỗ; venue Q1 → sửa; p20 ghi rõ cảnh báo Clifford là điều nhóm bỏ sót |
| `de_cuong_latex/bao_cao_30_paper.tex` | hộp đính chính đầu tài liệu (77,34 / 79,40 đã rút) — lưu ý: tệp này do `gen_baocao_paper.py` sinh; nếu sinh lại phải chép hộp vào script |
| `analysis/DULIEU.md` | mục 6.12 "nhóm chưa tìm" → ghi rõ Clifford 2014 đã cảnh báo, nhóm bỏ sót; header đính chính |
| `analysis/CHANDOAN_MOHINH.md` | header RÚT kết luận (âm tính giả 18 %) |
| `analysis/{THICHNGHI,CHONKENH,ABLATION_B1,LUONGCUC,GATE22,CLINICAL,KIENTRUC}.md`, `baselines/BASELINES.md`, `fsqi/README.md` | header cảnh báo: số CinC-75 đã rút, số hiện hành 60 bản sạch; số gốc giữ để truy vết |
| `docs/CHIEN_LUOC_CONG_BO.md` | "Phát hiện về dữ liệu" → kiểm toán, ban tổ chức đã ghi nhận; "tự tìm ra rò rỉ" → sửa; nút thắt → đã rút; ứng viên bộ thứ ba → không có nhãn (R2) |
| `docs/EUREKA.md`, `docs/KICH_BAN_TRINH_BAY.md` | "em/tự phát hiện rò rỉ" → phát biểu đúng; "PM Q1" → Q2/Q3 |
| `BUILD_VONG5.md`, `QA_VONG4.md`, `THAMDINH_VONG6.md`, `docs/README_KET_QUA.md`, `docs/DE_CUONG_NCKH_v2.md`, `docs/De_xuat_fECG_TDA_PI_CNN.md`, `docs/BAO_CAO_PHAN_BIEN_*.md` | header "báo cáo/tài liệu lịch sử, số đã rút" |
| `demo/README.md` | header: bảng mục 4 có 4 bản rò rỉ; số hiện hành 82 bản |
| `CITATION.cff` | abstract bỏ +11,00 / bimodal / p = 0,7012; v3.5, 12/09/2026 |
| `tests/test_api.py` | 2 assertion ghim tên checkpoint 5 ca → chấp nhận checkpoint 22 ca chưa thấy r01 (fold 05) / production 22 ca (hành vi mới của `demo/core.checkpoint_for`, R4) |
| `docs/CinC2026_RelyFetal.pdf`, `docs/De_cuong_NCKH_RelyFetal.pdf`, `docs/Bao_cao_30_paper.pdf` | biên dịch lại |

Tổng: 33 tệp văn bản sửa trực tiếp, ≈ 75 vị trí; 13 tệp thêm header cảnh báo. Rà lại bằng regex sau khi sửa:
mọi lần xuất hiện của số đã rút trong tệp giao nộp (README, bài báo, đề cương, docs) đều nằm trong câu
rút lại / bảng "đã rút", không còn đứng như số hiện hành.

## 4. VIỆC 3 — `survey/facts_phase4.json`

Sinh bởi `survey/make_facts_phase4.py` (đọc trực tiếp `eval_cinc60_sach.json`, `dulieu_results.json`,
`xacnhan_results.json`, `demo_check_2modes.json`, `ro_ri_vanlieu.json`); mỗi mục có `nguon`. Mục `Z_DA_RUT`
liệt kê số và cụm từ cấm.

## 5. VIỆC 4 — kiểm thử

* `pytest tests/ demo/test_core.py -q` → **60 passed, 0 failed** (15 s) — sau khi sửa 2 assertion tên
  checkpoint trong `tests/test_api.py` (trước sửa: 58 passed, 2 failed vì `demo/core.checkpoint_for` nay
  trả checkpoint 22 ca).
* `python demo/run_check.py --threads 2` → 83/83 bản, 2,8 phút, `demo/results/demo_check_2modes.json`
  (17:07). 82 bản có nhãn: chế độ *học* 46 xanh (F1 TB 95,70) / 17 vàng / 19 đỏ, 3 bản xanh có F1 < 90
  (a52, a54, a57), 0 bản đỏ có F1 ≥ 95; chế độ *luật* 58 / 19 / 5, 5 bản xanh có F1 < 90; gợi ý mặc định: `hoc`.
  Lần chạy 16:41 của R4 tóm tắt 74 bản; lần này 82 — số trong README lấy từ lần 17:07.

## 6. Biên dịch

* Bài báo `paper/cinc2026/main.pdf`: **4 trang** (pdflatex + bibtex, không tham chiếu lỗi).
* Đề cương `de_cuong_latex/de_cuong.pdf`: **141 trang** (xelatex ×2; bản 3.4 là 140).
* Báo cáo 30 công trình: xelatex ×2, chép vào `docs/Bao_cao_30_paper.pdf`.

## 7. Hạn chế của đợt dọn

1. Đề cương: các bảng/hình 75 bản trong §CinC, §Power-MF, §phản biện **giữ nguyên số cũ** kèm hộp/ghi chú
   "đã rút" — chưa vẽ lại `fig18_cinc75.pdf`, `fig19_m22_v2.pdf` với 60 bản sạch.
2. `docs/De_cuong_NCKH_RelyFetal.docx`, `docs/Bao_cao_30_paper.docx` chưa sinh lại (`make_docx.py`).
3. `bao_cao_30_paper.tex` được sinh bởi script; hộp đính chính chèn tay vào .tex, chưa đưa vào
   `gen_baocao_paper.py`.
4. Các báo cáo phân tích vòng 6 (`THICHNGHI.md`, `CHONKENH.md`, …) chỉ thêm header, không viết lại từng số.
5. Tệp `demo/*` do R4 sửa (chưa commit) được commit chung trong commit này; nội dung bảng mục 4 của
   `demo/README.md` chưa viết lại theo lần chạy 17:07 (chỉ header).
6. Chưa kiểm 60 bản sạch có từ 60 sản phụ khác nhau không (NCC ≤ 0,62 chỉ loại bản sao nguyên văn).
