<div align="center">

# RelyFetal

**Dò phức bộ QRS thai nhi từ điện tim ổ bụng đơn kênh, có nhận biết độ tin cậy**

*Đối chuẩn không rò rỉ giữa các họ biểu diễn tín hiệu và chỉ số chất lượng dựa trên đồng điều bền vững*

Nghiên cứu khoa học sinh viên · Khoa Công nghệ Thông tin · Trường Đại học Tôn Đức Thắng · 2026–2027

[English README](README.md) · [Đề cương đầy đủ (PDF)](docs/De_cuong_NCKH_RelyFetal.pdf) · [Báo cáo 30 công trình (PDF)](docs/Bao_cao_30_paper.pdf)

</div>

---

## Đề tài này là gì

Đo nhịp tim thai bằng **một miếng dán điện cực trên bụng mẹ**. Đây là cấu hình rẻ nhất và dễ đeo nhất cho
theo dõi tại nhà, và cũng là cấu hình khó nhất về xử lý tín hiệu: sóng tim mẹ lớn gấp nhiều lần sóng tim
con, hai nguồn trùng dải tần, và khi chỉ có một kênh thì không dùng được các phương pháp tách nguồn mù
đa kênh.

Kho mã này chứa toàn bộ pipeline chạy được, cùng bằng chứng thực nghiệm cho từng quyết định thiết kế.

**Kết quả khoa học chính là một phát hiện phản trực giác, và đó là điểm mấu chốt của đề tài:**

> Đổi dải thông của bộ lọc ăn **+11,00 điểm F1**.
> Đổi cả họ kiến trúc mạng, ở cùng độ dài ngữ cảnh, chỉ ăn **+0,41 điểm** và
> *không phân biệt được với nhiễu* (Wilcoxon ghép cặp, `p = 0,7012`).

Cả một lĩnh vực đã dành mười năm thiết kế mạng ngày càng lớn, trong khi thứ thật sự quyết định lại nằm ở
khâu trước đó.

---

## Kết quả chính

Giao thức: PhysioNet ADFECGDB, **tách theo bản ghi**, chấm ở mức sự kiện, dung sai **±50 ms** (quy ước
CinC 2013, khắt khe gấp ba lần chuẩn 150 ms của ANSI/AAMI EC57).

### Trong miền — ADFECGDB, 5 sản phụ

| Quy tắc chọn kênh | Macro F1 | Se | PPV | Jitter |
|---|---:|---:|---:|---:|
| **Mù nhãn, theo mật độ phổ công suất (con số báo cáo)** | **99,21** | 99,59 | 98,79 | 3,05 ms |
| Bản đồ đạo trình do giao thức ngoài quy định | 99,18 | 99,59 | 98,79 | 3,05 ms |
| Oracle — dùng nhãn thật, *không được báo cáo* | *99,21* | — | — | — |
| Trung bình trên cả bốn kênh bụng | 97,45 | 97,69 | 97,18 | 3,62 ms |

Gộp toàn cục trên 3.191 nhịp có nhãn: **TP 3.178 · FP 40 · FN 13**.

### Xuyên bộ dữ liệu — CinC 2013 set-a, không tinh chỉnh

| Quy tắc chọn kênh | Macro F1 |
|---|---:|
| Kênh cố định | **77,34 ± 28,54** |
| Quy tắc PSD mù nhãn | 59,15 ± 37,17 |
| Oracle | 77,59 ± 28,14 |

Con số trung bình che giấu vấn đề thật. Phân bố là **lưỡng cực**: 4 trên 10 bản ghi đạt F1 tuyệt đối
100,0, ba bản khác sụp dưới 50. **Hệ thống không biết khi nào nó sai** — và đó chính là thứ mà đóng góp
mới của đề tài được thiết kế để giải quyết.

### Phân rã đóng góp ba tầng

| Tầng | Δ Macro F1 | p | Kết luận |
|---|---:|---:|---|
| Front-end tín hiệu (chọn dải thông) | **+11,00** | < 0,001 | có ý nghĩa |
| Độ dài ngữ cảnh và độ phân giải đầu ra | +4,53 | 0,0000 | có ý nghĩa |
| Họ kiến trúc, ở ngữ cảnh cố định | +0,41 | **0,7012** | **không có ý nghĩa** |

---

## Mô hình

`FetalQRS-TCN` — mạng tích chập giãn nở có kết nối dư, dạng chuỗi sang chuỗi.

| Thuộc tính | Giá trị |
|---|---|
| Tham số huấn luyện được | **113.481** |
| Kích thước checkpoint | 0,48 MB |
| Trường tiếp nhận | 379 mẫu = **1.516 ms** |
| Độ trễ một cửa sổ 4 giây | **4,35 ms** trên CPU (920× thời gian thực) |
| Đầu vào | 2 × 1000 — tín hiệu dư sau khử mẹ + tín hiệu gốc, đoạn 4 s ở 250 Hz |
| Đầu ra | một logit cho **từng mẫu**; nhãn là bản đồ nhiệt Gauss, σ = 12 ms |

```
1 kênh ECG bụng @ 1000 Hz
   ↓  Butterworth 10–60 Hz pha không + chặn dải 50 Hz → hạ về 250 Hz
   ↓  dò QRS mẹ (dải 8–25 Hz, RR ≥ 350 ms)
   ↓  khử mẹ bằng mẫu trung vị + hệ số bình phương tối thiểu từng nhịp
   ↓  cắt đoạn 4 giây, 2 × 1000
   ↓  FetalQRS-TCN — stem Conv1d(k=7) + 5 khối dư, giãn nở 1,2,4,8,16
   ↓  bản đồ nhiệt từng mẫu → lấy đỉnh, ngưỡng τ + thời gian trơ 250 ms
vị trí từng nhịp thai + nhịp tim thai
```

Kiến trúc này **không** được chọn vì họ TCN ưu việt. Trong 16 kiến trúc ở cùng ngân sách tham số, 13 kiến
trúc hợp lý chỉ cách nhau 2,55 điểm F1. Thứ thật sự quan trọng là **trường tiếp nhận** (172 ms → 98,73;
748 ms → 99,25; 1.516 ms → 99,50, bão hoà sau đó, `p = 0,0000` so với nền ngữ cảnh ngắn) và **độ phân
giải đầu ra theo từng mẫu** (sai số định vị giảm từ 5,6–6,0 ms xuống 1,0 ms). TCN giãn nở đơn giản là
cách rẻ nhất để mua cả hai: ở cùng trường tiếp nhận, U-Net 1 chiều tốn 678.257 tham số mà F1 lại *thấp
hơn*, còn Transformer chậm gấp 21,7 lần để đổi lấy 0,25 điểm.

---

## Giao thức đánh giá

Ba luật cứng được áp dụng xuyên suốt, vì mỗi luật chặn một nguồn thổi phồng phổ biến trong lĩnh vực này:

1. **Không huấn luyện trên chủ thể đem đi chấm.** Mỗi bản ghi được chấm bằng checkpoint chỉ huấn luyện
   trên các bản ghi khác. Ngưỡng quyết định chọn trên một bản ghi validation *riêng*, không bao giờ chọn
   trên bản ghi kiểm thử.
2. **Dung sai ghép cặp ±50 ms**, ghép tham lam một-đối-một, đối chiếu chéo với thuật toán Hungarian tối
   ưu (trùng khớp tuyệt đối trên toàn bộ dữ liệu của nhóm).
3. **Chọn kênh mù nhãn.** Chọn kênh tốt nhất trong bốn kênh bằng cách so với nhãn thật là chọn kiểu
   oracle và không được báo cáo. Nhóm dùng quy tắc mật độ phổ công suất (theo Jaeger và cộng sự,
   *Physiol. Meas.* 2024), không đụng tới nhãn.

---

## Cấu trúc kho mã

```
model/                    Thư viện lõi, huấn luyện, suy luận, trọng số
├─ fqrs_model.py            Cài đặt tham chiếu — mọi hằng số đều truy được về một thí nghiệm
├─ train_final.py           Huấn luyện tách theo bản ghi, sinh 5 checkpoint fold + 1 production
├─ predict.py               Suy luận dòng lệnh: EDF / WFDB / CSV / NPY
├─ download_data.py         Tải nguồn PhysioNet, ghi thẻ dữ liệu SHA-256
└─ checkpoints/             6 mô hình đã huấn luyện (0,48 MB mỗi cái)

benchmark_dpss/           Bộ đối chuẩn
├─ _paths.py                Giải quyết đường dẫn, giữ kho mã tự chứa
├─ run_dpss_protocol.py     Chạy mô hình theo giao thức đối chuẩn bên ngoài
├─ full_measure.py          Bộ chỉ số đầy đủ + chi phí tính toán đo thật
├─ blind_lead.py            Chọn kênh mù nhãn theo PSD (trong và ngoài miền)
└─ all_leads.py             Phân tích từng kênh

pilot_evidence/           Toàn bộ thí nghiệm tiền khả thi, kèm nhật ký
├─ band_ablation.py         8 dải thông ứng viên
├─ arch_search.py           16 kiến trúc ở cùng ngân sách tham số
├─ seq_search.py            Quét trường tiếp nhận
├─ seq_loro.py              Tách bản ghi 3 seed + Wilcoxon ghép cặp
└─ final_loro.py            Lần chạy tách bản ghi cuối cùng

de_cuong_latex/           Đề cương nghiên cứu — mã nguồn LaTeX
├─ make_figs.py             8 hình vector, sinh từ dữ liệu
├─ gen_tables.py            Bảng LaTeX sinh tự động từ JSON khảo sát
└─ make_docx.py             Xuất PDF sang DOCX bằng pandoc

survey/                   Dữ liệu khảo sát 30 công trình + sổ số liệu đã kiểm chứng
docs/                     Tài liệu đã biên dịch (PDF + DOCX)
tests/                    Kiểm thử nhanh
```

---

## Cài đặt và chạy

```bash
git clone https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027.git
cd nckhsv_tdtu2026-2027
python -m venv .venv && .venv\Scripts\activate     # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Chỉ cần CPU. Huấn luyện lại toàn bộ mất khoảng 30 phút trên CPU laptop, không cần GPU.

```bash
# 1. Tải ADFECGDB từ PhysioNet (~15 MB), ghi thẻ dữ liệu SHA-256
python model/download_data.py --root model/data --only adfecgdb

# 2. Suy luận bằng checkpoint chưa từng thấy bản ghi này
python model/predict.py \
    --input model/data/adfecgdb/r01.edf --lead 1 --annot qrs \
    --checkpoint model/checkpoints/fetalqrs_tcn_fold_r01.pt
```

```
fetal beats  645     fetal HR 127,7 bpm     maternal HR 82,0 bpm
Se 100,00   PPV 99,84   F1 99,92   jitter 1,58 ms   (TP 644, FP 1, FN 0)
```

Chạy lại toàn bộ kết quả:

```bash
python model/train_final.py --epochs 6 --seed 0   # huấn luyện lại 6 checkpoint (~30 phút CPU)
python benchmark_dpss/full_measure.py             # bộ chỉ số đầy đủ + chi phí tính toán
python benchmark_dpss/blind_lead.py               # chọn kênh mù nhãn
python pilot_evidence/band_ablation.py            # khảo sát 8 dải thông
python pilot_evidence/seq_loro.py                 # 3 seed + Wilcoxon
```

---

## Dữ liệu

Kho mã này **không phân phối lại** bất kỳ bản ghi sinh lý nào. `model/download_data.py` tải từ nguồn gốc
và ghi mã băm SHA-256 cho từng tệp.

| Bộ dữ liệu | Nguồn | Giấy phép |
|---|---|---|
| ADFECGDB | physionet.org/content/adfecgdb · DOI 10.13026/C2RP4B | ODC-BY 1.0 |
| CinC 2013 set-a | physionet.org/content/challenge-2013 | ODC-BY 1.0 |
| NSTDB | physionet.org/content/nstdb | ODC-BY 1.0 |
| NIFEADB | physionet.org/content/nifeadb · DOI 10.13026/C2CT0S | ODC-BY 1.0 |
| Silesia (Matonia 2020) | figshare DOI 10.6084/m9.figshare.c.4740794 | tải thủ công |
| FECGSYNDB | physionet.org/content/fecgsyndb | ODC-BY 1.0 |

ADFECGDB là bộ chính: 5 sản phụ chuyển dạ tuần 38–41, bốn kênh bụng ở 1 kHz, nhãn chuẩn lấy từ **điện cực
xoắn da đầu thai** và đã được bác sĩ tim mạch duyệt.

---

## Hạn chế còn tồn tại

Nêu thẳng, vì phản biện sẽ tìm ra dù có nêu hay không.

- **Chỉ 5 sản phụ, tất cả đều đang chuyển dạ tuần 38–41.** Không có dữ liệu dưới 38 tuần, trong khi giá
  trị lâm sàng của theo dõi tại nhà nằm ở tuần 24–37. Bổ sung bộ Silesia là việc đầu tiên phải làm.
- **Khoảng tin cậy 95 % của 99,21 với n = 5 vượt quá 100 %**, tức giả định phân phối chuẩn bị vi phạm.
  Phải dùng bootstrap hoặc thang logit.
- **Bảng 16 kiến trúc lạc quan về giá trị tuyệt đối.** Nó chạy ở dải 3–90 Hz chứ không phải 10–60 Hz tối
  ưu, trên một bản ghi validation, một seed, và F1 lấy là giá trị lớn nhất quét trên 18 ngưỡng *ngay trên
  chính bản ghi đánh giá*. Bảng chỉ dùng để so sánh *tương đối*, vì mọi kiến trúc đều chịu cùng thiên
  lệch. Theo bảng đó `cnn_dil` xếp hạng 5 chứ không phải hạng 1 — lập luận bảo vệ được là **hiệu quả tham
  số**, không phải ưu thế kiến trúc.
- **Chưa cài lại baseline nào.** Mọi so sánh với y văn đều là so với con số *đã công bố*, không phải bản
  tự chạy lại.
- **Chỉ số chất lượng dựa trên đồng điều bền vững mới ở mức thiết kế, chưa triển khai.**

---

## Ghi chú về công trình liên quan

[Power-MF](https://doi.org/10.1088/1361-6579/ad4952) (Jaeger và cộng sự, *Physiol. Meas.* 45(5):055009,
2024) đạt 98,0 ± 3,0 % F1 trên ADFECG B2 ở cùng dung sai 50 ms bằng **xử lý tín hiệu cổ điển**. Không đối
chiếu trực tiếp được — họ dùng bốn kênh trên bộ Silesia 500 Hz, còn công trình này là đơn kênh trên các
bản ghi công khai 1 kHz — nhưng đây là kết quả cạnh tranh mạnh nhất, và quy tắc chọn kênh theo PSD của họ
chính là quy tắc được áp dụng ở đây.

---

## Giấy phép

Mã nguồn theo **MIT**. Tài liệu, hình vẽ và trọng số mô hình theo **CC BY 4.0**. Dữ liệu sinh lý và các
công trình của bên thứ ba **không** được phân phối lại — xem [`LICENSE`](LICENSE) để biết phạm vi đầy đủ.

> **Không phải thiết bị y tế.** Đây là bản mẫu nghiên cứu, chưa được thẩm định lâm sàng và không có bất kỳ
> chứng nhận quản lý nào. Không được dùng để hỗ trợ bất kỳ quyết định chẩn đoán hay điều trị nào.
