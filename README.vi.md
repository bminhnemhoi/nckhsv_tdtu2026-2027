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
> Dưới giao thức không rò rỉ, **sáu kiến trúc mạng nằm trong 1,5 điểm nhau và không kiến trúc nào khác một
> CNN giãn nở 26 nghìn tham số có ý nghĩa thống kê** (mọi `p ≥ 0,105`). Biến kiến trúc duy nhất quan trọng
> là trường tiếp nhận (`p = 0,0001`).

---

## Kết quả chính

Giao thức xuyên suốt: chấm ở mức sự kiện, dung sai **±50 ms**, ghép một-đối-một tham lam đối chiếu với
Hungarian, chọn kênh **mù nhãn**.

### Một mô hình, năm cấu hình dữ liệu

| Bộ dữ liệu | Sản phụ | Phút | Nhãn | F1, kênh PSD mù nhãn | F1, trung bình 4 kênh |
|---|---:|---:|---|---:|---:|
| ADFECGDB (PhysioNet), tách bản ghi | 5 | 25 | điện cực da đầu | **99,21 ± 1,50** | 97,45 ± 2,96 |
| Silesia B2 chuyển dạ, 12 bản ghi | 12 | 60 | điện cực da đầu | 97,17 ± 7,45 | 95,26 ± 9,59 |
| Silesia B2, chỉ 7 bản ghi chưa thấy, zero-shot | 7 | 35 | điện cực da đầu | 95,87 ± 9,75 | 93,73 ± 12,48 |
| **Silesia B1 thai kỳ 32–42 tuần, zero-shot** | 10 | 200 | gián tiếp | **93,30 ± 13,46** | 91,31 ± 9,99 |
| CinC 2013 set-a, zero-shot | 10 | 10 | cộng đồng gán | 59,15 ± 37,17 | 61,96 ± 34,09 |

Mô hình chỉ huấn luyện trên 5 ca chuyển dạ, chưa từng thấy dữ liệu thai kỳ. Chuyển từ chuyển dạ sang
thai kỳ *cùng hệ ghi* mất ~4 điểm; chuyển sang *hệ ghi khác* (CinC 2013) mất ~38 điểm và phân bố
**lưỡng cực** — 4/10 bản ghi hoàn hảo, 5/10 dưới 50. Thứ phá vỡ tổng quát hoá là thiết bị và bố trí điện
cực, không phải tuổi thai.

Kiểm tra rò rỉ bằng tương quan chéo cho thấy **5 trong 12 bản ghi Silesia B2 chính là 5 bản ghi
PhysioNet** (NCC 0,988–0,994). Năm bản đó được chấm bằng fold checkpoint chưa thấy chúng; số sản phụ độc
lập vì vậy là **22**, không phải 27.

### Phân rã đóng góp ba tầng

| Tầng | Δ Macro F1 | p | Kết luận |
|---|---:|---:|---|
| Front-end tín hiệu (chọn dải thông) | **+11,00** | < 0,001 | có ý nghĩa |
| Độ dài ngữ cảnh và đầu ra từng mẫu | +4,53 | 0,0000 | có ý nghĩa |
| Họ kiến trúc, ở ngữ cảnh cố định | +0,41 | **0,7012** | **không có ý nghĩa** |

### Baseline cổ điển tự cài lại (ADFECGDB, cùng giao thức, siêu tham số chỉ chọn trên r01)

| Phương pháp | 4 kênh (n=20) | Kênh PSD (n=5) | Δ so với mô hình | p, thua ở |
|---|---:|---:|---:|---|
| Trừ mẫu + Pan–Tompkins | 78,96 ± 23,52 | 87,68 | −18,49 | 5,7×10⁻⁶, 19/20 |
| TS-PCA + Pan–Tompkins | 91,05 ± 10,17 | 96,74 | −6,40 | 1,9×10⁻⁶, 20/20 |
| Độ nhô đỉnh trên **cùng front-end** | 86,39 ± 11,14 | 92,03 | −11,06 | 1,9×10⁻⁶, 20/20 |
| **FetalQRS-TCN** | **97,45 ± 4,44** | **99,21** | — | — |

Baseline thứ ba tách riêng phần đóng góp của mạng: cùng tín hiệu dư, chỉ thay mạng bằng lấy đỉnh → mạng
đáng **+11,06 điểm**. TS-PCA trên kênh tốt nhất đạt 96,74 — phương pháp cổ điển vẫn mạnh, nhất quán với
phát hiện về front-end.

### Cổng từ chối trả lời và kết quả phủ định về đồng điều bền vững

Bộ phân loại "mô hình sẽ sai ở đoạn này không?" huấn luyện trên ADFECGDB, kiểm thử **xuyên miền** trên
CinC 2013:

| Nhóm đặc trưng | AUROC | F1 ở độ phủ 80 % | F1 ở độ phủ 50 % |
|---|---:|---:|---:|
| Từ chối ngẫu nhiên | 0,500 | 62,03 | 62,14 |
| 16 đặc trưng topo (Takens + ripser, sublevel H0) | **0,566** | 63,40 | 64,44 |
| 12 chỉ số cổ điển | **0,929** | **69,40** | **84,51** |
| Cả 28 | 0,905 | 69,41 | 82,44 |
| Oracle | — | 74,55 | 97,81 |

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
└─ powermf_status.json      Vì sao Power-MF không chạy lại được tại chỗ

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
pytest tests/ demo/test_core.py                          # 24 kiểm thử
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

- **Tập huấn luyện vẫn là 5 sản phụ, đều chuyển dạ.** Đánh giá đã phủ 22 sản phụ độc lập gồm 10 thai kỳ,
  nhưng huấn luyện lại trên cả 22 (Phase P3) chưa làm.
- **Tổng quát sang hệ ghi khác chưa giải quyết.** 59–77 F1 trên CinC 2013 với phân bố lưỡng cực. Cổng từ
  chối giảm nhẹ (+7,4 điểm ở độ phủ 80 %); tiền huấn luyện FECGSYNDB (Phase P7) là hướng xử lý.
- **Bảng kiến trúc chỉ một seed, ba epoch**, và bỏ Transformer cùng hai biến thể 2D vì chi phí. Thứ tự
  không đổi nhưng con số tuyệt đối còn thiếu huấn luyện.
- **Đèn tin cậy trong demo là luật đặt tay.** Ngưỡng bám mẹ 60 % được đặt sau khi nhìn một bản ghi đánh giá.
  Bộ phân loại chỉ số cổ điển đã học trong `fsqi/` nên thay vào.
- **Power-MF chưa chạy lại được** (MATLAB, thiếu phụ thuộc đa kênh); 98,0 % vẫn là số đã công bố.
- **Chỉ số chất lượng topo đề xuất ban đầu không hoạt động** (AUROC 0,566 so với 0,929). Được báo cáo là
  kết quả phủ định, không giấu.

---

## Giấy phép

Mã nguồn **MIT**. Tài liệu, hình vẽ và trọng số **CC BY 4.0**. Dữ liệu sinh lý và công trình bên thứ ba
**không** phân phối lại — xem [`LICENSE`](LICENSE).

> **Không phải thiết bị y tế.** Bản mẫu nghiên cứu, chưa thẩm định lâm sàng, không có chứng nhận quản lý.
