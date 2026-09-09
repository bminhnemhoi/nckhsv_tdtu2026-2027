# Đề tài fECG đơn kênh — RelyFetal

Cập nhật 09/09/2026.

## Tài liệu gửi giảng viên hướng dẫn

| Tệp | Nội dung | Số trang |
|---|---|---|
| **`De_cuong_NCKH_RelyFetal.pdf`** | **Đề cương chính thức v3.0** | 70 |
| `De_cuong_NCKH_RelyFetal.docx` | Bản Word của đề cương, để GVHD sửa trực tiếp | — |
| **`Bao_cao_30_paper.pdf`** | **Báo cáo đọc 30 công trình**, mỗi bài một mục, dễ đọc | 100 |
| `Bao_cao_30_paper.docx` | Bản Word của báo cáo 30 công trình | — |

## Thư mục làm việc

| Thư mục | Nội dung |
|---|---|
| `de_cuong_latex/` | Mã nguồn LaTeX, 8 hình vector, script sinh bảng và xuất Word |
| `model/` | Thư viện, mã huấn luyện, mã suy luận, 6 checkpoint, dữ liệu ADFECGDB |
| `benchmark_dpss/` | Mã đối chuẩn, kiểm chứng Hungarian, quy tắc chọn kênh mù nhãn |
| `pilot_evidence/` | Mã và nhật ký toàn bộ thí nghiệm tiền khả thi |
| `papers/` | 30 PDF toàn văn + `papers_records.json` |
| `survey/` | `survey_raw.json` (khảo sát 30 bài), `facts_verified.json` (số liệu đã kiểm chứng) |
| `goi-danh-gia-doi-chuan-dpss/` | Gói đối chuẩn nhận từ Lê Xuân Khánh — **chỉ đọc, không phụ thuộc** |
| `BAO_CAO_PHAN_BIEN_va_TAI_THIET_KE_fECG_TDA.md` | Tài liệu phản biện nội bộ, 14 phần |
| `De_xuat_fECG_TDA_PI_CNN.md` | Bản v1.0 cũ, giữ để đối chiếu |

## Mô hình

`FetalQRS-TCN` — **113.481 tham số**, checkpoint 0,48 MB, độ trễ 4,35 ms mỗi cửa sổ 4 giây trên CPU.

```
Tiền xử lý   Butterworth 10-60 Hz pha không + chặn dải 50 Hz + hạ về 250 Hz
Khử ECG mẹ   mẫu trung vị + hệ số bình phương tối thiểu theo từng nhịp
Đầu vào      2 x 1000 (tín hiệu dư + tín hiệu gốc), đoạn 4 giây
Thân mạng    stem Conv1d(k=7) + 5 khối residual dilated 1,2,4,8,16 -> RF 1.516 ms
Đầu ra       một logit cho từng mẫu, nhãn heatmap Gaussian sigma 12 ms
Hậu xử lý    lấy đỉnh, ngưỡng tau + thời gian trơ 250 ms
```

## Kết quả đã đo

PhysioNet ADFECGDB, tách theo bản ghi, dung sai ±50 ms:

| Giao thức chọn kênh | Macro F1 |
|---|---|
| **Mù nhãn theo mật độ phổ công suất** | **99,21** |
| Bản đồ đạo trình do gói đối chuẩn quy định | 99,18 |
| Oracle (dùng nhãn thật — không báo cáo được) | 99,21 |
| Trung bình trên cả 4 kênh | 97,45 |

Xuyên bộ dữ liệu sang CinC 2013, không tinh chỉnh: **77,34** với kênh cố định, **59,15** với quy tắc PSD.
Phân bố lưỡng cực: 4/10 bản ghi đạt F1 100,00, 3/10 sụp dưới 50.

Phân rã đóng góp ba tầng:

| Tầng | Mức tăng F1 | p |
|---|---|---|
| Front-end tín hiệu (đổi dải thông) | **+11,00** | < 0,001 |
| Độ dài ngữ cảnh và độ phân giải đầu ra | +4,53 | 0,0000 |
| Họ kiến trúc, ở ngữ cảnh cố định | +0,41 | **0,7012 (không có ý nghĩa)** |

## Chạy lại

```bash
pip install numpy scipy scikit-learn torch mne wfdb

cd model
python download_data.py --root data --only adfecgdb    # tải trực tiếp từ PhysioNet
python train_final.py --epochs 6 --seed 0              # ~30 phút CPU, sinh 6 checkpoint
python predict.py --input data/adfecgdb/r01.edf --lead 1 --annot qrs \
                  --checkpoint checkpoints/fetalqrs_tcn_fold_r01.pt

cd ../benchmark_dpss
python run_dpss_protocol.py --mode loro    # sinh file dự đoán theo giao thức đối chuẩn
python full_measure.py                     # chỉ số đầy đủ + chi phí tính toán
python blind_lead.py                       # quy tắc chọn kênh mù nhãn
```

Dựng lại tài liệu:

```bash
cd de_cuong_latex
python make_figs.py            # 8 hình vector
python gen_tables.py           # bảng LaTeX từ survey_raw.json
xelatex de_cuong.tex           # chạy 3 lần cho mục lục
python make_docx.py            # xuất Word
python gen_baocao_paper.py     # báo cáo 30 paper
python make_docx_baocao.py
```

## Ba việc phải làm trước khi nộp bài báo

1. Bổ sung bộ Silesia (Matonia 2020) để nâng số sản phụ từ 5 lên khoảng 22.
2. Chạy lại bảng 16 kiến trúc ở dải 10-60 Hz, tách bản ghi đầy đủ, ba seed.
   Bảng hiện tại chạy ở 3-90 Hz, một bản ghi, một seed, ngưỡng quét trên chính bản ghi đánh giá.
3. Cài lại bốn baseline cổ điển. Mọi so sánh hiện tại là so với con số đã công bố, không phải bản tự chạy.

Chi tiết ở mục 8 của đề cương.
