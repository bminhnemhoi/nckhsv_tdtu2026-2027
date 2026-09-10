# Đề tài fECG đơn kênh — RelyFetal

Cập nhật 11/09/2026, phiên bản 3.1.

## Tài liệu gửi giảng viên hướng dẫn

| Tệp | Nội dung |
|---|---|
| **`De_cuong_NCKH_RelyFetal.pdf`** | **Đề cương chính thức v3.1** — đã cập nhật baseline, Silesia, C3 sau prototype, demo |
| `De_cuong_NCKH_RelyFetal.docx` | Bản Word để GVHD sửa trực tiếp |
| **`Bao_cao_30_paper.pdf`** | Báo cáo đọc 30 công trình, mỗi bài một mục |
| `Bao_cao_30_paper.docx` | Bản Word của báo cáo 30 công trình |

## Thay đổi so với v3.0 (09/09)

| Mục | v3.0 | v3.1 |
|---|---|---|
| Số sản phụ đánh giá | 5 | **22** (10 thai kỳ + 12 chuyển dạ, sau khi loại 5 trùng) |
| Dữ liệu thai kỳ | không có | Silesia B1 zero-shot **93,30** |
| Baseline tự chạy | không | 3 baseline, Wilcoxon, mạng đáng +11,06 điểm |
| Bảng kiến trúc | 16, giao thức lỗi | 8, giao thức đúng, không kiến trúc nào khác cnn_dil có ý nghĩa |
| Đóng góp C3 | thiết kế trên giấy | prototype: topo **thất bại** (AUROC 0,566), cổng từ chối **có tác dụng** (+7,4) |
| Demo | chưa có | Gradio chạy được, đèn tin cậy, ảnh chụp thật |

## Ba việc kế tiếp theo kế hoạch

1. Huấn luyện lại trên 22 sản phụ (Phase P3).
2. Tiền huấn luyện FECGSYNDB để chữa sụp đổ trên hệ ghi khác (Phase P7).
3. Thay luật cứng của đèn tin cậy bằng bộ phân loại chỉ số cổ điển đã học trong `fsqi/`.

Chi tiết ở mục 10 của đề cương.
