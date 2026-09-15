# Bàn giao dự án RelyFetal

> **Đọc tệp này trước mọi tệp khác.** Nó cho bạn biết đề tài đang ở đâu, cài đặt thế nào, số liệu nào
> được phép dùng, và những cái bẫy nhóm đã rơi vào để bạn khỏi rơi lại.
>
> Cập nhật: **15/09/2026** · Chủ nhiệm: **Ngô Bình Minh** (TDTU) · Kho mã:
> <https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027>

---

## Mục lục

1. [Đề tài trong ba câu](#1-đề-tài-trong-ba-câu)
2. [Trạng thái hiện tại](#2-trạng-thái-hiện-tại)
3. [Cài đặt từ đầu](#3-cài-đặt-từ-đầu)
4. [Tải dữ liệu](#4-tải-dữ-liệu)
5. [Kiểm tra cài đặt đúng chưa](#5-kiểm-tra-cài-đặt-đúng-chưa)
6. [Bản đồ kho mã](#6-bản-đồ-kho-mã)
7. [Nguồn sự thật và quy tắc số liệu](#7-nguồn-sự-thật-và-quy-tắc-số-liệu)
8. [Quy tắc liêm chính — bắt buộc đọc](#8-quy-tắc-liêm-chính--bắt-buộc-đọc)
9. [Bẫy kỹ thuật đã biết](#9-bẫy-kỹ-thuật-đã-biết)
10. [Việc tiếp theo](#10-việc-tiếp-theo)
11. [Câu hỏi còn mở](#11-câu-hỏi-còn-mở)
12. [Cách nhóm làm việc](#12-cách-nhóm-làm-việc)

---

## 1. Đề tài trong ba câu

**RelyFetal** phát hiện phức bộ QRS thai nhi từ **một** điện cực dán trên bụng mẹ, và **tự từ chối trả lời**
khi tín hiệu không đủ tin cậy.

Mô hình là một mạng tích chập thời gian giãn nở (`FetalQRS-TCN`, 113.481 tham số, 0,48 MB, chạy CPU) đọc
đoạn 4 giây và cho xác suất nhịp ở từng mẫu; một cổng từ chối dùng 12 chỉ số chất lượng tín hiệu cổ điển,
không nhìn nhãn.

Câu hỏi nghiên cứu: một kênh lấy lại được bao nhiêu phần lợi ích của bốn kênh — và hệ thống có biết lúc nào
nó sai không.

---

## 2. Trạng thái hiện tại

### Kết quả chính — mọi số truy ngược được về `survey/facts_phase4.json`

| Phép đo | Giá trị | Tệp nguồn |
|---|---|---|
| **22 chủ thể trong miền** — RelyFetal 1 kênh | F1 **97,56** | `baselines/powermf_fair_stats.json` |
| Power-MF 4 kênh (chạy lại qua Octave) | F1 **98,83** — ta **thua 1,27** [−3,08; +0,27], p 0,156 | như trên |
| Power-MF 1 kênh (nhóm tự cắt) | F1 **86,71** — ta hơn +10,85 [+6,80; +15,40] | như trên |
| **Tỉ lệ lấy lại lợi ích đa kênh** | **89,49 %** [81,4; 103,2] | `analysis/recovery_ratio.json` |
| **60 bản CinC 2013 sạch** — quy tắc chọn kênh cũ `psd` | F1 **74,28** | `analysis/dulieu_results.json` |
| Quy tắc chọn kênh mới `peakprob` (**hậu kiểm**) | F1 **82,01** (+7,73, p Holm 0,0039) | như trên |
| Quy tắc `gate4` (**chỉ định trước**, sống sót Holm) | F1 **81,01** (p Holm 0,015) | như trên |
| Cổng từ chối — AUROC trong bản ghi | **0,934** [0,872; 0,981] | `analysis/gate22_results.json` |

### Tiến độ theo khối

| Khối | % | Còn thiếu |
|---|---:|---|
| Hạ tầng, mã, kiểm thử | 95 | Dockerfile đã sửa thiếu `scikit-learn` và kiểm bằng giả lập phụ thuộc; **image chưa `docker build` thật** |
| Mô hình | 95 | Câu hỏi kiến trúc đã **đóng** — giữ TCN |
| Thống kê | 95 | 3 hạt giống cho kết quả chính (hiện có 2) |
| Văn bản | 90 | Toàn văn **mù** cho Euréka (bỏ tên, trường, GVHD) |
| Đánh giá, đối chuẩn | 80 | Đối thủ thứ hai **DPSS** vẫn là số trích dẫn, chưa chạy lại |
| Chỉ số lâm sàng | 75 | Số cổng từ chối trên CinC chưa tính lại trên 60 bản sạch |
| Dữ liệu | 60 | **Không có bộ công khai nào khác có nhãn fQRS thật** |
| Tính mới khoa học | 50 | Gỡ bằng cùng một thứ: dữ liệu có nhãn mới |

### Sản phẩm đã có

| Sản phẩm | Vị trí |
|---|---|
| Demo web 8 tab (Gradio) | `demo/app.py` · hướng dẫn `docs/HUONG_DAN_DEMO.md` |
| API REST | `api/main.py` · `api/README.md` |
| Đề cương đầy đủ v3.5 — 148 trang PDF + DOCX | `docs/De_cuong_NCKH_RelyFetal.pdf` · nguồn `de_cuong_latex/` |
| Đề cương hiện trạng — 15 mục, in được | `docs/DE_CUONG_HIEN_TRANG.md` |
| Bài hội nghị CinC 2027 — 4 trang | `docs/CinC2027_RelyFetal.pdf` · nguồn `paper/cinc2026/` |
| Slide 26 trang (mở bằng trình duyệt; phím N ghi chú, O tổng quan) | `docs/trinh_bay/slide_bao_cao.html` |
| Sổ tay đề tài 16 mục | `docs/trinh_bay/so_tay_de_tai.html` |
| Kịch bản trình bày | `docs/KICH_BAN_HANH_TRINH.md` (đầy đủ) · `docs/KICH_BAN_TRINH_BAY.md` (20 phút) |
| Tóm tắt một trang | `docs/TOM_TAT_1_TRANG.md` |
| Chiến lược công bố | `docs/CHIEN_LUOC_CONG_BO.md` |
| Euréka — thể lệ đã xác minh | `docs/EUREKA.md` |
| Nhật ký thẩm định 7 vòng | `docs/nhat_ky/` |

---

## 3. Cài đặt từ đầu

Đã kiểm với **Python 3.12.6 trên Windows 11**. Không cần GPU.

```powershell
git clone https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027.git
cd nckhsv_tdtu2026-2027

python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate

pip install -r requirements.txt   # lõi: pipeline, demo, API, kiểm thử
```

Chỉ khi cần chạy lại thí nghiệm phân tích, dựng lại tài liệu, hoặc chụp ảnh demo:

```powershell
pip install -r requirements-research.txt
playwright install chromium       # chỉ cho demo/screenshot.py
```

**Lưu ý phiên bản:** demo **bắt buộc Gradio 6.x**. CSS thanh tab nhắm lớp `.tab-container`, lớp này chỉ có
từ Gradio 6. Nếu cài Gradio 5 thì hai tab cuối sẽ bị thu vào menu tràn ở màn hình hẹp.

**Công cụ ngoài, không cài bằng pip** — chỉ cần khi dựng lại tài liệu hoặc chạy lại baseline:
`xelatex` (MiKTeX/TeX Live), `pdflatex` + `bibtex`, `pandoc ≥ 3.0`, GNU Octave 11.x
(`python baselines/powermf_setup.py` tải bản portable).

**Mô hình đã huấn luyện có sẵn** — 20 checkpoint (9,3 MB) trong `model/checkpoints/`. Không cần huấn luyện lại
để chạy demo hay đánh giá.

---

## 4. Tải dữ liệu

Kho mã **không phân phối lại dữ liệu sinh lý** (xem `.gitignore`). Sau khi clone, `model/data/` và
`benchmark_dpss/pcdb/` trống. **Chạy mọi lệnh dưới đây từ thư mục gốc repo.**

| Bộ | Lệnh | Ghi vào | Dung lượng |
|---|---|---|---|
| **ADFECGDB** — 5 sản phụ, nhãn trực tiếp | `python model/download_data.py --root model/data --only adfecgdb` | `model/data/adfecgdb/` | 15 MB |
| **CinC 2013 set-a** — 75 bản ghi | `python model/download_more.py --only cinc75` | `benchmark_dpss/pcdb/` | 35 MB |
| **Silesia** — 22 bản ghi | `python model/download_silesia.py` | `model/data/silesia/Data_Records.zip` | 195 MB |

> ### ⚠ Silesia phải giải nén tay
>
> Script chỉ tải về tệp `.zip`. Bộ nạp tìm thư mục **`Data Records`** (có dấu cách) ở một trong hai chỗ:
> `model/data/silesia/Data Records/` hoặc `model/data/silesia/extracted/Data Records/`.
>
> ```powershell
> Expand-Archive model\data\silesia\Data_Records.zip -DestinationPath model\data\silesia\
> ```
>
> Không giải nén thì demo vẫn chạy, nhưng tab "Dữ liệu của nhóm" báo thiếu hai bộ Silesia.

> ### ⚠ Đừng dùng `--root data` như docstring cũ ghi
>
> Chạy từ gốc repo với `--root data` sẽ tạo `./data/adfecgdb`, là chỗ **không ai tìm**. Luôn dùng
> `--root model/data`.

**Nếu dữ liệu đã có ở chỗ khác**, trỏ bằng biến môi trường thay vì chép:

```powershell
$env:ADFECGDB_DIR = "D:\du_lieu\adfecgdb"      # thư mục chứa r01.edf
$env:CINC2013_DIR = "D:\du_lieu\set-a"         # thư mục chứa a01.dat
```

Tuỳ chọn, chỉ cho thí nghiệm phụ: `python model/download_more.py --only nifeadb ninfea` (NIFEADB không có
chú thích thai; NInFEA chỉ có tham chiếu Doppler — **không dùng được để đánh giá**).

---

## 5. Kiểm tra cài đặt đúng chưa

```powershell
$env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"; $env:MKL_NUM_THREADS="1"

python -m pytest tests/ demo/test_core.py -q     # kỳ vọng: 82 passed khi đủ dữ liệu
python demo/smoke_app.py                         # kỳ vọng: KẾT QUẢ: ĐẠT
python demo/app.py                               # mở trình duyệt, đếm đủ 8 tab
```

Demo mặc định chạy ở `http://127.0.0.1:7860`. Cổng bị chiếm thì đổi bằng **`RELYFETAL_PORT`** — không phải
`GRADIO_SERVER_PORT`, biến đó demo không đọc:

```powershell
$env:RELYFETAL_PORT="7861"; python demo/app.py
```

Demo **chạy được cả khi chưa tải dữ liệu** — đã kiểm trên bản clone mới (lên trong ~8 giây); các tab cần bản ghi
sẽ báo thiếu dữ liệu kèm lệnh tải, không sập.

**Chưa tải dữ liệu mà test báo `skipped` là bình thường** — các test cần bản ghi cụ thể tự bỏ qua kèm lý do
(`chưa có ADFECGDB r01`). Chỉ `failed` mới là lỗi.

Ba biến môi trường luồng ở trên **không phải tuỳ chọn**: không đặt thì NumPy/PyTorch chiếm hết lõi CPU, và
khi chạy song song nhiều thí nghiệm máy sẽ treo.

---

## 6. Bản đồ kho mã

| Thư mục | Làm gì | Đọc gì trước |
|---|---|---|
| `model/` | Mô hình `fqrs_model.py`, huấn luyện `train_22.py`, tải dữ liệu, 20 checkpoint | `fqrs_model.py` |
| `demo/` | Demo Gradio 8 tab; `core.py` là lõi xử lý dùng chung với API | `demo/README.md` |
| `api/` | API REST bọc `demo/core.py` | `api/README.md` |
| `benchmark_dpss/` | Đánh giá trên CinC 2013; `_paths.py` giải đường dẫn dữ liệu | `eval_cinc60_sach.py` |
| `baselines/` | Power-MF chạy lại qua Octave + bản 1 kênh tự cắt | `BASELINES.md` |
| `analysis/` | Các thí nghiệm phân tích vòng 3–7, mỗi cái một `.md` + `.json` | xem bảng dưới |
| `adapt/` | Bốn phương pháp thích nghi miền — **kết quả âm tính** | `analysis/THICHNGHI.md` |
| `fsqi/` | Chỉ số chất lượng tín hiệu, cổng từ chối bản đầu | `fsqi/README.md` |
| `pilot_evidence/` | Thí nghiệm sớm: dải lọc, kiến trúc, đường cong SNR, pilot TDA | — |
| `survey/` | Ghi chép văn liệu; **`facts_phase4.json` là nguồn sự thật** | `facts_phase4.json` |
| `de_cuong_latex/` | Nguồn LaTeX đề cương 148 trang + báo cáo 30 bài | `de_cuong.tex` |
| `paper/cinc2026/` | Nguồn bài CinC 2027 (thư mục giữ tên cũ) | `CHANGELOG.md` |
| `docs/` | Mọi tài liệu người đọc: đề cương, kịch bản, slide, hướng dẫn | `docs/trinh_bay/` |
| `docs/nhat_ky/` | Biên bản 7 vòng thẩm định phản biện | `README.md` trong đó |
| `archive/` | Script dùng một lần đã chạy xong, giữ để truy vết | `archive/README.md` |
| `tests/` | Kiểm thử lõi (43) — thêm 39 test trong `demo/test_core.py` | — |

**Bảng thí nghiệm phân tích** — mỗi dòng là một câu hỏi đã được trả lời:

| Tệp | Câu hỏi | Kết luận |
|---|---|---|
| `analysis/DULIEU.md` | Dữ liệu có chồng lấn không? | 15/75 bản CinC là bản sao ADFECGDB → dùng 60 bản sạch |
| `analysis/CHONKENH.md` | Chọn kênh mù nhãn thế nào? | 7 quy tắc; `peakprob` tốt nhất nhưng hậu kiểm |
| `analysis/KIENTRUC.md` | TCN có đúng không? | Đúng — 7 họ cùng tham số, ba họ đầu tương đương |
| `analysis/THICHNGHI.md` | Thích nghi miền có giúp không? | Không — cả 4 cách làm tệ đi |
| `analysis/GATE22.md` | Cổng từ chối có bắt đúng bản khó? | Có, 3/3 — nhưng 5/24 quy tắc một đặc trưng cũng làm được |
| `analysis/CHANDOAN_MOHINH.md` | Mô hình có phải nút thắt? | **Chưa kết luận được** — phép thử có âm tính giả 18 % |
| `analysis/XACNHAN.md` | Xác nhận `peakprob` được không? | Không — không có bộ thứ ba có nhãn; trên logit `gate` vẫn đầu |
| `analysis/STATS.md` | Thống kê có bị giả lặp không? | Có — sửa về mức chủ thể đảo 5 kết luận |
| `analysis/CLINICAL.md` | Đo STV lâm sàng được không? | Chưa — chệch +20,50 ms ngoài miền |
| `analysis/ABLATION_B1.md` | Dữ liệu B1 nhãn gián tiếp có hại không? | Có dấu vân nhãn ở mốc thời gian → cấm dùng số B1 cho jitter |

---

## 7. Nguồn sự thật và quy tắc số liệu

**`survey/facts_phase4.json` là nguồn sự thật duy nhất.** Mọi con số trong mọi tài liệu phải truy ngược được
về một trường trong tệp này, hoặc về tệp JSON mà trường `nguon` của nó chỉ tới.

Mục **`Z_DA_RUT`** trong tệp đó liệt kê mọi con số và tuyên bố **đã bị rút**. Trước khi viết một con số vào tài
liệu nào, tra mục này.

**Quy tắc khi thêm kết quả mới:**

1. Kết quả phải nằm trong một tệp `.json` do script sinh ra — không gõ tay số vào tài liệu.
2. Ghi tên script sinh ra tệp đó vào trường `nguon`.
3. Nếu kết quả mới làm một số cũ sai, **thêm số cũ vào `Z_DA_RUT` kèm lý do** — không xoá im lặng.
4. Commit tệp `.json` **cùng lúc** với tài liệu dùng nó.

---

## 8. Quy tắc liêm chính — bắt buộc đọc

Nhóm đã tự rút **năm tuyên bố** của chính mình. Những quy tắc dưới đây sinh ra từ các lần đó. Vi phạm một
quy tắc là đủ để phản biện bác bài.

### 8.1 Không dùng các cụm từ này

| Cụm từ | Vì sao |
|---|---|
| "SOTA", "state-of-the-art", "novel", "first", "đầu tiên", "tốt nhất hiện nay" | Chưa kiểm văn liệu đủ để khẳng định |
| "tiền đăng ký", "pre-registered" | Tệp khai báo không được neo bằng bên thứ ba |
| "chúng tôi phát hiện rò rỉ dữ liệu" | Ban tổ chức đã ghi nhận từ 2013 (Silva 2013; Clifford 2014) |
| "mô hình không phải nút thắt" | Phép thử nhìn thấy tín hiệu có âm tính giả 18 % |
| "thiếu tín hiệu thật" như một kết luận | Nguyên nhân khoảng cách ngoài miền **chưa xác định** |
| "bài toán lưỡng cực" như đặc tính | Bị chính đối chứng logit bác bỏ một phần |
| "Physiological Measurement là Q1" | Là **Q2** Scimago 2024 |
| "CinC 2026" như đích nộp | Đã diễn ra 20–23/9/2026 → đích là **CinC 2027** |

### 8.2 Mười lăm bản ghi CinC bị nhiễm

```
a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25
```

Đây là bản sao nguyên văn của dữ liệu huấn luyện ADFECGDB (tương quan chéo = 1,0000, lệch nhịp = 0,0 ms).
Mỗi bản ADFECGDB xuất hiện đúng 3 lần: `r01→a04,a05,a22` · `r04→a13,a20,a25` · `r07→a19,a23,a24` ·
`r08→a08,a15,a17` · `r10→a03,a12,a14`.

**Không bao giờ dùng 15 bản này làm ví dụ "ngoài miền".** Mọi số CinC chính tính trên **60 bản còn lại**.
Mọi số trên 75 bản đã bị rút.

### 8.3 `peakprob` là lựa chọn hậu kiểm

Quy tắc chỉ định trước là `gate` — nó **trượt** hiệu chỉnh Holm (p = 0,051). `peakprob` được chọn **sau khi**
nhìn kết quả CinC. Cứu cánh trung thực là `gate4` — cũng chỉ định trước, **sống sót** Holm (p = 0,015).

Khi viết về chọn kênh, **luôn báo cáo cả ba**. Không bao giờ trình bày `peakprob` một mình như kết quả xác nhận.

### 8.4 Hai con số rất dễ trích nhầm

| Đừng trích | Vì sao | Trích cái này |
|---|---|---|
| F1 **98,46** của `a09` | Chỉ là **30 giây đầu** trong tệp ví dụ demo | F1 **94,25** của `a09` đầy đủ |
| AUROC cổng **0,980** trên CinC | Đo trên 75 bản **nhiễm** | AUROC **0,934** trong bản ghi, 22 chủ thể |

### 8.5 Thống kê

* Thống kê ở **mức chủ thể**, không mức bản ghi. Một sản phụ có 4 đạo trình không phải 4 mẫu độc lập.
* Khoảng tin cậy dùng **cluster bootstrap** lấy mẫu lại **chủ thể**, 10 000 lần, `seed=0`.
* F1 chạm trần 100 — khi so các phương pháp đều trên 97, **làm lại trên thang logit**.
* Với n = 5, p nhỏ nhất Wilcoxon khả thi là 0,0625. Đừng mong p < 0,05.

---

## 9. Bẫy kỹ thuật đã biết

| Bẫy | Triệu chứng | Cách tránh |
|---|---|---|
| **Heredoc Bash nuốt dấu `\`** | Script Python/LaTeX viết qua `<<'EOF'` bị hỏng escape, lỗi cú pháp khó hiểu | Ghi script ra tệp `.py` rồi chạy, đừng nhúng vào heredoc |
| **`findpeaks` của Octave tốn bộ nhớ O(k²)** | Power-MF trả về nửa số nhịp hoặc rỗng trên bản ghi dài | Đã vá bằng `baselines/octave/findpeaks_mpd.m`; đừng gỡ |
| **Gradio 6 đổi tên lớp CSS** | CSS nhắm `.tab-nav` không tác dụng gì | Nhắm `.tab-container` |
| **Không đặt biến môi trường luồng** | Máy treo khi chạy song song | Luôn đặt `OPENBLAS/OMP/MKL_NUM_THREADS=1` |
| **`demo/run_check.py --out demo_check_showcase`** | Ghi đè tệp dự phòng 5 bản minh hoạ | Dùng tên khác, ví dụ `--out demo_check_3ban` |
| **Silesia chưa giải nén** | Tab dữ liệu báo thiếu hai bộ | Xem mục 4 |
| **`train_22.py --tag ...` không lưu checkpoint** | Chạy xong mà `model/checkpoints/` không có tệp mới | Chỉ ghi JSON kết quả; bỏ `--tag` nếu cần checkpoint |
| **`demo/assets/` bị gitignore** | Tab "Tải dữ liệu mới" báo thiếu tệp ví dụ | `python demo/make_vidu_tai_len.py` (cần CinC `a09`) |
| **Ghi dữ liệu sinh lý vào git** | Vi phạm giấy phép PhysioNet | `.gitignore` đã chặn `*.dat *.hea *.edf model/data/` — đừng `git add -f` |
| **Mã nguồn MATLAB của tác giả Power-MF** | Tái phân phối mã không được phép | `baselines/octave/PowerMF*.m` đã gitignore — chỉ commit bản vá của nhóm |
| **`ripser` trông như tuỳ chọn nhưng bắt buộc** | Demo, API sập `ModuleNotFoundError: ripser` khi bấm Phân tích | `fsqi/fsqi.py` import nó ở đầu tệp; đèn tin cậy mặc định nạp `fsqi.py`. Đã đưa vào `requirements.txt`, CI, Dockerfile. Muốn bỏ hẳn thì chuyển import vào trong hàm đặc trưng tô-pô |
| **Mô hình cổng từ chối pickle với `scikit-learn` 1.9.0** | Khác phiên bản thì cảnh báo, có thể không unpickle được | Dockerfile ghim `scikit-learn==1.9.0`. Nâng sklearn thì chạy lại `python fsqi/train_gate.py` rồi commit `.pkl` mới |
| **Đặt `GRADIO_SERVER_PORT` không đổi được cổng demo** | Demo vẫn chạy 7860, trình duyệt mở cổng khác không thấy gì | Demo đọc `RELYFETAL_PORT` (`demo/app.py`) |
| **Giả lập thiếu gói bằng `ImportError` cho kết quả sai** | `pytest.importorskip` báo lỗi thay vì bỏ qua | pytest ≥ 8.2 chỉ bỏ qua với `ModuleNotFoundError`. Khi giả lập một gói vắng, phải ném đúng loại đó |

---

## 10. Việc tiếp theo

Xếp theo **giá trị chia chi phí**. Việc cần người ngoài đứng đầu vì thời gian chờ dài nhất.

| # | Việc | Vì sao | Chi phí |
|---|---|---|---|
| 1 | **Liên hệ khoa sản xin dữ liệu có nhãn** (qua giảng viên hướng dẫn) | Mọi con đường lên Q1 và xác nhận `peakprob` đều cần nó. Không bộ công khai nào có | Tuần, cần đạo đức nghiên cứu |
| 2 | Hỏi Đoàn trường hạn nội bộ **Euréka** | Kỳ 2026 đăng ký cấp thành 01–25/9; hạn TDTU chưa tìm được | 1 cuộc gọi |
| 3 | Hỏi hội đồng trường chấm theo **Scimago hay WoS-JCR** | Physiological Measurement là Q2 Scimago — câu trả lời đổi cả chiến lược | 1 câu hỏi |
| 4 | **3 hạt giống** cho mọi kết quả chính | Hiện 2 hạt giống; phản biện sẽ đòi | ~1 ngày máy |
| 5 | Tính lại **số cổng từ chối trên 60 bản sạch** | Số hiện tại (AUROC 0,980) đo trên 75 bản nhiễm | Vài giờ |
| 6 | **Chạy lại DPSS** | Đối thủ thứ hai vẫn là số trích dẫn — đúng lỗ hổng đã lấp cho Power-MF | 2–3 ngày |
| 7 | Viết **bản dài cho Physiological Measurement**, quanh một trục duy nhất | Đích công bố thực tế nhất (~58 %) | 4 tuần |
| 8 | Dựng bài CinC bằng **`cinc.cls` chính thức**, đếm lại trang | Hiện dùng template mô phỏng; hạn ~4/2027 | 1 ngày |
| 9 | Toàn văn **mù** cho Euréka | Chấm mù: không tên, trường, GVHD | 1 ngày |

**Đừng làm** — bằng chứng đã nói là đòn bẩy yếu:

* **Đổi kiến trúc.** 7 họ cùng tham số, ba họ đầu cách nhau 0,02 điểm; nhân 4 lần tham số chỉ được +0,26.
* **Thích nghi miền không nhãn.** Bốn cách (chặn điện lưới, tự huấn luyện, AdaBN, TENT) đều làm tệ đi.
* **Đặc trưng tô-pô.** Pilot: 27,4 so với 97,1 của mạng 1D cùng tham số.
* **Đổi dải lọc.** Trên trung bình 4 kênh hiệu ứng là −0,07 [−0,51; +0,39].

---

## 11. Câu hỏi còn mở

| Câu hỏi | Trạng thái | Cần gì để trả lời |
|---|---|---|
| Mô hình đã đủ tốt chưa? | **Mở.** Kết luận "không phải nút thắt" đã rút | Phép thử nhìn thấy tín hiệu có độ đặc hiệu tốt hơn |
| `peakprob` có tổng quát không? | **Giả thuyết mạnh, chưa xác nhận** | Một bộ thứ ba có nhãn fQRS thật |
| Vì sao ngoài miền kém trong miền 15 điểm? | **Chưa xác định.** Không phải dịch chuyển thống kê | Dữ liệu tín hiệu yếu có nhãn |
| Cần bao nhiêu chủ thể? | Ước ~50 (công suất thống kê) | Dữ liệu |
| Có dùng làm máy đo STV lâm sàng được không? | **Chưa.** Chệch +0,33 ms trong miền, +20,50 ms ngoài | Dữ liệu dài có nhãn, đánh giá lâm sàng |

---

## 12. Cách nhóm làm việc

Quy trình này đã tìm ra năm lỗi của chính nhóm trước khi có ai khác tìm ra. Giữ nguyên.

1. **Khai báo trước, neo git.** Trước khi chạy một thí nghiệm có nhiều phương án, ghi ra tệp: sẽ so gì, chỉ số
   nào, quy tắc chọn thắng. **Commit tệp đó trước khi chạy.** Tệp không neo git thì không gọi là khai báo trước.
2. **Chạy, ghi `.json`.** Script sinh kết quả, không gõ tay.
3. **Phản biện độc lập.** Một người (hoặc một agent) khác đọc kết quả với nhiệm vụ duy nhất là **tìm chỗ sai**.
   Biên bản các vòng nằm trong `docs/nhat_ky/`.
4. **Rút công khai.** Sai thì thêm vào `Z_DA_RUT` kèm lý do, sửa mọi tài liệu dùng số đó, commit một lần.
5. **Đo trước khi giải thích.** Hai lần nhóm đoán nguyên nhân trước khi đo, cả hai lần đoán sai.

**Kỹ thuật kiểm tra đáng giữ:** đối chứng ngẫu nhiên cho mọi phép gán nhãn lỗi; kiểm rò rỉ nhãn bằng xáo
nhãn (lựa chọn không được đổi); đối chứng dương cho mọi phép đo trùng lặp; thống kê mức chủ thể.

---

*Bản mẫu nghiên cứu, không phải thiết bị y tế. Mã nguồn MIT (xem `LICENSE`). Dữ liệu thuộc giấy phép của
từng nguồn — ADFECGDB, CinC 2013, NIFEADB, NInFEA theo Open Data Commons Attribution v1.0 của PhysioNet; Silesia
xem giấy phép trên figshare (DOI 10.6084/m9.figshare.c.4740794). Tải từ nguồn gốc, không lấy từ kho này, và
trích dẫn mọi bộ dữ liệu bạn dùng.*
