# Đề tài fECG đơn kênh — RelyFetal

Cập nhật 11/09/2026, phiên bản 3.2.

## Tài liệu gửi giảng viên hướng dẫn

| Tệp | Nội dung |
|---|---|
| **`De_cuong_NCKH_RelyFetal.pdf`** | **Đề cương chính thức v3.2** |
| `De_cuong_NCKH_RelyFetal.docx` | Bản Word để GVHD sửa trực tiếp |
| **`Bao_cao_30_paper.pdf`** | Báo cáo đọc 30 công trình |
| `Bao_cao_30_paper.docx` | Bản Word của báo cáo 30 công trình |
| `../paper/cinc2026/main.pdf` | Bản thảo Computing in Cardiology, 4 trang, đã qua phản biện nội bộ |

## Thay đổi v3.1 → v3.2 (cùng ngày)

| Mục | v3.1 | v3.2 |
|---|---|---|
| Mô hình | học trên 5 ca | **học trên 22 ca**, 11 fold, có tăng cường; 12 checkpoint mới |
| Thai kỳ (Silesia B1) | 93,30 zero-shot | **97,15** (p = 0,037), SD 13,46 → 4,95 |
| Hệ ghi khác (CinC 2013) | 77,34, lưỡng cực, 3/10 dưới 50 | **90,34**, 0/10 dưới 50 (p = 0,016) |
| Hiệu quả mẫu | chưa đo | 1/2/3 ca: 91,2 / 93,4 / 97,5 — chưa bão hoà |
| Độ bền nhiễu | chưa đo | 4 loại nhiễu MIT-BIH × 6 SNR; mạng gãy chậm hơn TS-PCA |
| Đèn tin cậy | luật cứng | thêm chế độ học (GBM 12 chỉ số); 0 lỗi nguy hiểm trên 32 bản ghi |
| API / kiểm thử | chưa có / 24 test | FastAPI 3 điểm cuối / **53 test**, CI |
| Bài báo | chưa có | bản thảo CinC 4 trang, 12 tài liệu |
| Phản biện nội bộ | 1 vòng | 2 vòng (mã nguồn K; kết quả tự kiểm chứng) |

## Kết luận đã sửa

Bản v3.1 viết "thứ phá vỡ tổng quát hoá là thiết bị, không phải tuổi thai". Với 22 ca, mô hình chuyển sang hệ
ghi khác ở mức 90 chứ không phải 77 — phần lớn sụp đổ là do **thiếu dữ liệu**. Khoảng cách còn lại 90 so với
97–99 mới là phần thật sự do thiết bị.

## Ba việc kế tiếp

1. Hiệu chuẩn lại cổng tin cậy cho mô hình 22 ca (hiện vẫn theo mô hình 5 ca, quá thận trọng trên thai kỳ).
2. Đo riêng đóng góp của tăng cường dữ liệu; thêm 2 seed cho mô hình 22 ca và bảng kiến trúc.
3. Dữ liệu đa trung tâm — khoảng trống duy nhất còn lại về tổng quát hoá.
