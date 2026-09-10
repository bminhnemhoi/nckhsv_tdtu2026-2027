# RelyFetal — demo dò phức bộ QRS thai nhi từ điện tim ổ bụng đơn kênh

> **Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.**

Demo web một trang (Gradio + Plotly, chạy cục bộ trên CPU) bao bọc đúng pipeline chuẩn của
`model/fqrs_model.py` — *tiền xử lý → khử QRS mẹ → FetalQRS-TCN → chọn đỉnh* — và bổ sung:
chọn kênh mù nhãn theo PSD, chuỗi nhịp tim thai theo cửa sổ 4 s, đối chiếu với nhãn (nếu có)
và một **đèn tin cậy** tạm thời (quy tắc cứng, sẽ thay bằng fSQI tô-pô).

## 1. Cách chạy

```bash
pip install gradio plotly            # đã kiểm với gradio 6.26.0, plotly 7.0.0 (Python 3.12.6, torch 2.13.0+cpu)
python demo/app.py                   # mở http://127.0.0.1:7860
```

| Biến môi trường | Ý nghĩa | Mặc định |
|---|---|---|
| `RELYFETAL_PORT` | cổng HTTP | `7860` |
| `RELYFETAL_AUTORUN` | `1` = mở trang là tự phân tích bản ghi đầu tiên (r01) | `1` |
| `PYTHONIOENCODING` | trên Windows nên đặt `utf-8` để in tiếng Việt ra console | — |

Dữ liệu mẫu được tìm qua `benchmark_dpss/_paths.py` (ADFECGDB r01/r04/r07/r08/r10 dạng EDF 1000 Hz;
CinC 2013 set-a a01..a10 dạng WFDB 1000 Hz). Không có dữ liệu mẫu thì vẫn chạy được với file tải lên.
Checkpoint: `model/checkpoints/fetalqrs_tcn_fold_rXX.pt` (dùng cho ADFECGDB rXX — **fold chưa từng thấy rXX**)
và `fetalqrs_tcn_production.pt` (mọi bản ghi khác, kể cả CinC 2013 = zero-shot).

**Tải lên file:** `.edf` (kèm `.edf.qrs` nếu có nhãn) · `.hea + .dat` (+ `.fqrs`) · `.csv` / `.npy` / `.txt`
(mảng K×N hoặc N×K; cần nhập fs) · nhãn tuỳ chọn dạng `.txt` mỗi dòng một chỉ số mẫu.

## 2. Cấu trúc

| Tệp | Vai trò |
|---|---|
| `core.py` | **Lõi xử lý, không phụ thuộc gradio.** Đọc bản ghi (EDF/WFDB/CSV/NPY/mảng) → 1000 Hz; `select_lead` (PSD Power-MF, mù nhãn); `analyze`/`analyze_record` gọi `M.preprocess`, `M.cancel_maternal`, `M.probability_series`, `M.pick_peaks` của `model/fqrs_model.py`; `fhr_series`; `match_with_lists` (ghép một-đối-một, ±50 ms, giống `M.match_events`); `confidence` (đèn tin cậy); `summary` (JSON). Không sửa gì trong `model/`. |
| `app.py` | Giao diện Gradio: hàng điều khiển (nguồn, bản ghi, kênh, nút *Phân tích*), 4 thẻ số, 4 tab (*Tín hiệu 5 tầng*, *Nhịp tim thai theo thời gian*, *So sánh với nhãn*, *Nhật ký JSON*). Chỉ dựng giao diện và vẽ Plotly; mọi tính toán ở `core.py`. Tự thích nghi Gradio 5/6 (`css`/`theme` chuyển sang `launch()` ở Gradio 6). |
| `test_core.py` | 8 kiểm thử pytest cho lõi (không cần gradio), gồm hai mốc bắt buộc: r01 kênh 4 F1 > 99 & đèn *cao*; a02 đèn *không cao*. |
| `run_check.py` | Chạy lõi trên mọi bản ghi mẫu (chọn kênh tự động) → `results/demo_check.json` + `.log` — nguồn của bảng mục 4. |
| `smoke_app.py` | Khởi động thử app không mở trình duyệt: HTTP 200, gọi thẳng `app.run()` với r01, gọi qua `gradio_client` API `/run` → `results/smoke_app.json`. |
| `screenshot.py` | Chụp màn hình giao diện thật bằng playwright/Chromium → `screenshots/`. |
| `results/` | `demo_check.json`, `demo_check.log`, `smoke_app.json` (mọi con số trong README lấy từ đây). |
| `screenshots/` | 6 ảnh PNG + `screenshots.json`. |
| `_uploads/` | thư mục tạm cho file tải lên (tự tạo, tự xoá khi tải file mới). |

**Thời gian xử lý** hiển thị trên thẻ = tiền xử lý + khử mẹ của kênh được chọn + mô hình + chọn đỉnh
(không tính đọc file và vẽ); CPU 4 luồng (`torch.set_num_threads(4)`). Bản ghi 300 s: ≈ 0,57–0,76 s;
bản ghi 60 s: ≈ 0,12–0,16 s (lần chạy sạch cuối, `results/demo_check.json`). Toàn bộ chu trình kể cả đọc EDF và dựng hình r01: ≈ 1,8–2,1 s (`results/smoke_app.json`).

## 3. Quy trình trong demo (những gì người xem thấy trên tab *Tín hiệu*)

1. **Tín hiệu thô** kênh bụng đã chọn (1000 Hz).
2. **Lọc 10–60 Hz + notch 50 Hz, 250 Hz**; vạch đỏ = đỉnh R mẹ do `cancel_maternal` tìm được.
3. **Phần dư sau khử mẹ** (mẫu trung vị) — chính là đầu vào của mô hình; vạch đen = nhãn nhịp thai (nếu có).
4. **Xác suất nhịp thai** của FetalQRS-TCN (113 481 tham số) và ngưỡng cố định từ tập validation.
5. **Kết quả**: ● TP (xanh), ✕ FP (đỏ), ▲ FN (cam) khi có nhãn; hoặc vạch xanh = nhịp mô hình phát hiện khi không có nhãn.

Chọn kênh *Tự động (PSD)*: khử mẹ trên cả 4 kênh, lấy kênh có đỉnh PSD mạnh nhất trong dải 1,8–3,0 Hz
(108–180 bpm) của đường bao phần dư — không dùng nhãn (sao chép từ `benchmark_dpss/blind_lead.py`).

## 4. Đèn tin cậy (tạm thời — sẽ thay bằng fSQI tô-pô)

Ngưỡng **cố định trước**, không tinh chỉnh trên bản ghi đánh giá (`core.CONF_RULE`). Điểm số
`score = 0,20·s_band + 0,30·s_rr + 0,30·s_prob + 0,20·s_fhr` với

| # | Thành phần (không cần nhãn) | Cách cho điểm |
|---|---|---|
| (i) | tỉ lệ năng lượng 10–60 Hz trên phần dư **băng rộng** (0,5–120 Hz) sau khử mẹ | 0 tại ≤ 20 %, 1 tại ≥ 55 %, tuyến tính ở giữa |
| (ii) | CV của khoảng RR thai đầu ra | 1 tại ≤ 0,05, 0 tại ≥ 0,30 |
| (iii) | tỉ lệ đỉnh phát hiện có xác suất > 0,9 | chính tỉ lệ đó |
| (iv) | fHR trung bình trong 100–200 bpm | 1 / 0 |
| (v) | **cổng bám nhịp mẹ**: tỉ lệ nhịp thai nằm trong ±50 ms của một đỉnh R mẹ (ngẫu nhiên ≈ 13–22 %) | > 60 % ⇒ **thấp** bất kể điểm |

Mức: `score ≥ 0,75` và (iv) đúng ⇒ **cao (xanh)**; `≥ 0,45` ⇒ **trung bình (vàng)**; còn lại hoặc < 10 nhịp hoặc (v) ⇒ **thấp (đỏ)**.
Cổng (v) được thêm sau khi thấy a02: mô hình bám phần dư QRS mẹ ở ~125 bpm mà bốn thành phần còn lại vẫn cho 0,87.

### Kết quả trên 15 bản ghi mẫu (`results/demo_check.json`, chọn kênh tự động, nhãn chỉ dùng để chấm sau khi phân tích)

| Bản ghi | Bộ dữ liệu | Checkpoint | Kênh | Nhịp | fHR | **F1** | Se | PPV | Đèn | Điểm | Bám mẹ | ms |
|---|---|---|--:|--:|--:|--:|--:|--:|---|--:|--:|--:|
| r01 | ADFECGDB | fold r01 | 4 | 644 | 129,1 | **100,00** | 100,00 | 100,00 | cao | 0,858 | 0,16 | 571 |
| r04 | ADFECGDB | fold r04 | 2 | 631 | 126,4 | **99,76** | 99,68 | 99,84 | trung bình | 0,744 | 0,15 | 618 |
| r07 | ADFECGDB | fold r07 | 2 | 627 | 125,5 | **100,00** | 100,00 | 100,00 | cao | 0,800 | 0,13 | 667 |
| r08 | ADFECGDB | fold r08 | 4 | 652 | 130,5 | **99,77** | 99,85 | 99,69 | cao | 0,896 | 0,20 | 648 |
| r10 | ADFECGDB | fold r10 | 1 | 662 | 132,0 | **96,54** | 98,43 | 94,71 | cao | 0,917 | 0,14 | 759 |
| a01 | CinC 2013 | production | 2 | 122 | 129,8 | **59,18** | 54,48 | 64,75 | trung bình | 0,572 | 0,23 | 127 |
| a02 | CinC 2013 | production | 2 | 125 | 125,8 | **21,75** | 19,38 | 24,80 | **thấp** (bám mẹ) | 0,872 | 0,97 | 131 |
| a03 | CinC 2013 | production | 1 | 128 | 128,0 | **100,00** | 100,00 | 100,00 | cao | 0,994 | 0,16 | 116 |
| a04 | CinC 2013 | production | 4 | 129 | 130,9 | **100,00** | 100,00 | 100,00 | cao | 0,937 | 0,16 | 141 |
| a05 | CinC 2013 | production | 4 | 129 | 129,0 | **100,00** | 100,00 | 100,00 | cao | 0,945 | 0,19 | 130 |
| a06 | CinC 2013 | production | 1 | 116 | 121,6 | **42,75** | 36,88 | 50,86 | trung bình | 0,482 | 0,41 | 120 |
| a07 | CinC 2013 | production | 2 | 98 | 115,4 | **29,82** | 26,15 | 34,69 | trung bình | 0,483 | 0,37 | 164 |
| a08 | CinC 2013 | production | 4 | 128 | 127,6 | **100,00** | 100,00 | 100,00 | cao | 1,000 | 0,25 | 139 |
| a09 | CinC 2013 | production | 2 | 94 | 96,2 | **16,96** | 14,62 | 20,21 | **thấp** (bám mẹ) | 0,266 | 0,89 | 132 |
| a10 | CinC 2013 | production | 2 | 110 | 117,5 | **21,05** | 17,14 | 27,27 | trung bình | 0,629 | 0,57 | 126 |
| r01 (kênh 4 thủ công) | ADFECGDB | fold r01 | 4 | 644 | 129,1 | **100,00** | 100,00 | 100,00 | cao | 0,858 | 0,16 | 658 |

*ms* = thời gian xử lý một lần chạy (tiền xử lý + khử mẹ + mô hình + chọn đỉnh; CPU 4 luồng; dao động ±10 % giữa các lần).
ADFECGDB 300 s/bản ghi, CinC 2013 60 s/bản ghi. Chỉ số theo dung sai ±50 ms, ghép một-đối-một.

**Đèn tách được bản ghi tốt/xấu ở mức nào (15 bản ghi, chọn kênh tự động):**

| Đèn | Số bản ghi | F1 trung bình | F1 min | F1 max |
|---|--:|--:|--:|--:|
| cao (xanh) | 8 | **99,54** | 96,54 | 100,00 |
| trung bình (vàng) | 5 | 50,51 | 21,05 | 99,76 |
| thấp (đỏ) | 2 | 19,36 | 16,96 | 21,75 |

Đọc trung thực: **không có bản ghi nào đèn xanh mà F1 < 96**, và hai bản ghi tệ nhất đều đỏ nhờ cổng bám mẹ.
Nhưng nhóm vàng còn lẫn (r04 F1 99,76 bị hạ xuống vàng vì CV RR hơi cao và năng lượng dải QRS thấp; a10 F1 21,05 chỉ vàng vì bám mẹ 57 % chưa vượt cổng 60 %).
Đây là quy tắc cứng với 4 trọng số đặt tay, chưa được tối ưu hay kiểm chứng chéo — mục tiêu của đề tài là thay nó bằng fSQI tô-pô học từ dữ liệu.

## 5. Kịch bản demo 3 phút

| Phút | Thao tác | Điều cần nói |
|---|---|---|
| 0:00–0:30 | Mở `python demo/app.py`; trang tự phân tích **r01**. Chỉ vào 4 thẻ số. | Một kênh bụng, 300 s, 644 nhịp thai, fHR 129 bpm, xử lý ~0,6–0,7 s trên CPU. Checkpoint fold r01 **chưa từng thấy** bản ghi này. Đèn xanh: 5 lý do được liệt kê ngay dưới. |
| 0:30–1:30 | Tab **Tín hiệu (5 tầng)**: kéo chuột phóng to 2–3 giây; chỉ vạch đỏ (mẹ) ở tầng 2, phần dư tầng 3, xác suất tầng 4, TP ở tầng 5. | QRS mẹ lớn gấp ~3 lần QRS thai; sau khử mẹ mô hình chỉ còn nhìn phần dư; ngưỡng 0,40 cố định từ validation, không chỉnh theo bản ghi. |
| 1:30–2:00 | Tab **So sánh với nhãn**. | Se/PPV/F1 = 100/100/100 với dung sai ±50 ms; jitter 1,25 ms. Tab **Nhịp tim thai**: đường mô hình trùng đường nhãn. |
| 2:00–2:45 | Chọn **a02 — CinC 2013** → *Phân tích*. | Bản ghi zero-shot (bộ dữ liệu khác, máy khác). Đèn **đỏ**: 97 % nhịp "thai" trùng đỉnh R mẹ → mô hình đang bám mẹ; tab fHR cho thấy mô hình ~126 bpm còn nhãn ~160 bpm. Điểm 4 thành phần vẫn 0,87 — đây chính là lý do cần fSQI tốt hơn quy tắc cứng. |
| 2:45–3:00 | Chọn **a03** hoặc **a08** → *Phân tích* (đèn xanh, F1 100 zero-shot). Kết bằng dòng miễn trừ. | Khi tín hiệu tốt, mô hình chuyển bộ dữ liệu không cần huấn luyện lại. *Bản mẫu nghiên cứu, không dùng cho chẩn đoán.* |

Dự phòng: đổi **Kênh bụng** của r01 sang 1/2/3 để thấy PSD chọn kênh 4 là đúng (k4 = 3,9·10⁻¹¹ so với k1 = 8,0·10⁻¹² — hiển thị trên dòng trạng thái).

## 6. Ảnh chụp màn hình (`screenshots/`, playwright 1.62.0 + Chromium, 1500 px × 1,5)

| Tệp | Nội dung |
|---|---|
| `01_r01_tin_hieu.png` | r01, tự động chọn kênh 4: thẻ số (đèn **xanh**) + tab *Tín hiệu (5 tầng)*, 10 s đầu |
| `02_r01_fhr.png` | r01: tab *Nhịp tim thai theo thời gian* (mô hình trùng nhãn) |
| `03_r01_so_sanh.png` | r01: tab *So sánh với nhãn* (bảng Se/PPV/F1 và danh sách sự kiện) |
| `04_r01_the_so.png` | r01: chỉ 4 thẻ số — dùng làm hình nhỏ trong đề cương |
| `05_a02_den_do.png` | a02 (zero-shot): đèn **đỏ** "bám nhịp mẹ" + tab fHR (mô hình ~126 bpm, nhãn ~160 bpm) |
| `06_a02_tin_hieu.png` | a02: tab tín hiệu — phần dư còn sót QRS mẹ |

![r01 — tab tín hiệu](screenshots/01_r01_tin_hieu.png)

![a02 — đèn đỏ, fHR](screenshots/05_a02_den_do.png)

Chụp lại: `pip install playwright && python -m playwright install chromium && python demo/screenshot.py`.

## 7. Kiểm thử

```bash
python -m pytest demo/test_core.py -v     # 8 kiểm thử lõi (~1 phút, cần dữ liệu mẫu cho 3 kiểm thử đầu)
python demo/smoke_app.py                  # server + gọi thẳng + gradio_client -> results/smoke_app.json
python demo/run_check.py                  # 16 lần phân tích -> results/demo_check.json / .log
```

`smoke_app.py` đi qua đúng đường postprocess của Gradio, nhờ đó đã bắt được một lỗi thật khi lên Gradio 6:
`gr.JSON` (orjson) từ chối khóa kiểu `int` trong `lead_scores` — đã sửa trong `core.summary` (khóa chuỗi).

## 8. Hạn chế

* Đèn tin cậy là quy tắc cứng đặt tay (4 trọng số + 1 cổng), chưa được tối ưu/kiểm chứng chéo; thử trên 15 bản ghi thì tách được nhóm xanh, nhưng nhóm vàng còn lẫn (xem mục 4).
* CinC 2013 là zero-shot với checkpoint production huấn luyện trên ADFECGDB: F1 lưỡng cực (4/10 = 100, 5/10 < 45, còn lại a01 = 59) — demo cho thấy đúng thực trạng này, không che.
* Chỉ hỗ trợ bản ghi ≤ vài phút trong trình duyệt (Plotly WebGL, bản ghi 300 s ở 250 Hz vẽ mượt; thô 1000 Hz hiển thị 1/4 mẫu).
* Chưa có xử lý theo thời gian thực/luồng; mỗi lần bấm phân tích cả bản ghi.

> **Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.**
