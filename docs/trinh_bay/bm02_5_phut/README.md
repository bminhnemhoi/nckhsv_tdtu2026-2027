# RelyFetal — BM02, bài nói 5 phút

Mở `index.html` trong trình duyệt. Bấm **Trình chiếu**, dùng phím trái/phải hoặc Space, Home/End; Esc thoát. Nút **Toàn màn hình** dùng API trình duyệt, chưa xác minh bằng thao tác GUI.

Xuất lại PDF trên Mac đã có Google Chrome:

```sh
sh render.sh
```

Chạy từ thư mục bất kỳ bằng đường dẫn đến script; PDF được ghi cạnh HTML. Script dùng profile Chrome tạm riêng, không dùng profile cá nhân.

Script gọi `build_print.py` để nhúng thẳng `slides.css` vào `_print.html` rồi mới in (file tạm xóa sau khi xong). Lý do: Chrome headless hay dùng lại bản CSS đã cache theo `file://`, nên sửa CSS mà PDF vẫn ra bản cũ. Đừng in trực tiếp `index.html` và đừng thêm `?v=` vào thẻ link CSS.

Kiểm tra bố cục (phần tử tràn khung, ảnh thiếu):

```sh
python3 qa_layout.py
```

## Nội dung

- `RelyFetal_BM02_5_phut.pdf`: 14 trang 16:9 (960×540 pt).
- `loi_thoai.md`: 994 từ, khoảng 270 giây theo nhịp 2,6 từ/giây — còn khoảng 30 giây đệm trong 5 phút. Cần tập với đồng hồ.
- `doi_chieu.md`: nguồn từng slide và danh sách những điểm không được nói quá.
- `assets/`: logo TDTU gốc; sơ đồ minh họa (`signal-mix.svg`, `embedded.svg`, `leakage.svg`, `data-split.png`); ảnh cắt từ demo thật (`model-probability`, `model-beats`, `reliability-case`, `monitor-r01`, `monitor-b203`).

### Ảnh chụp màn hình theo dõi (slide 10)

Hai ảnh `assets/monitor-r01.png` và `assets/monitor-b203.png` là ảnh chụp thật của route `/monitor`
(`demo/monitor_template.py` — màn hình theo dõi nền đen, sóng thai màu đỏ), không phải hình dựng lại.

Cách chụp lại trên máy có dữ liệu:

```sh
# Dataset ADFECGDB nằm ngoài repo ở máy này; trỏ biến môi trường vào thư mục chứa r01.edf
ADFECGDB_DIR="/duong/dan/toi/raw" python3 demo/app.py

# Chụp: headless thường chỉ chạy được vài frame nên sóng không chạy đủ;
# phải chờ theo thời gian thực rồi mới capture (xem /tmp/cdp_shot.py trong lịch sử làm việc)
```

Cắt khung `(40, 48) → (1560, 486)` của cửa sổ 1600×1000: đủ hàng thẻ số đo (FHR, nhịp mẹ, F1, thời gian xử lý)
và toàn bộ canvas điện tâm đồ. Ca khó dùng `B2_03` (Silesia, chuyển dạ) — đèn đỏ, hệ thống từ chối đưa số ra.

Số liệu trên ảnh là đầu ra thật của mô hình cho đúng bản ghi đó (r01: 129 bpm, F1 99,92%, 291 ms;
B2_03: 160 bpm, F1 83,91%, 272 ms, đèn đỏ). Nếu chụp lại, phải cập nhật chú thích cho khớp từng con số.

## Mạch trình bày

Vấn đề → 3 câu hỏi → kết quả bước đầu 97,56% → mục tiêu → dữ liệu → phương pháp → giao thức → kết quả trong miền → liêm chính dữ liệu → ngoài miền → độ tin cậy → phần nhúng → đóng góp → ứng dụng → sản phẩm → kế hoạch → tiêu chí.

## Đã kiểm tra

- PDF 14 trang, mỗi trang 960×540 pt, chữ chọn được, dấu tiếng Việt đúng.
- `qa_layout.py` chạy sạch: không phần tử nào vượt khung slide, không ảnh thiếu.
- Đã xem ảnh render từng trang ở kích thước trình chiếu và sửa các chỗ chữ nhỏ, chồng cắt.
- Số liệu đối chiếu `baselines/powermf_fair_stats.json` và `survey/facts_phase4.json`; không huấn luyện lại.
- Bản ghi r01 (slide 10) và ca a02 (slide 8) là ví dụ minh họa, không phải kết quả trung bình.
- Slide 9 là sơ đồ kế hoạch; không có đo bench phần cứng nào được trình bày như kết quả.

Số liệu và cách đọc được ghi rõ trong `doi_chieu.md`, đặc biệt: chưa chứng minh tương đương 4 kênh, gate trượt Holm, peakprob là chọn hậu kiểm.
