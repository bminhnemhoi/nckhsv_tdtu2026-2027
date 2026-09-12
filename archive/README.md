# archive/ — tệp rút khỏi cây làm việc trong đợt dọn repo vòng 7 (12/09/2026)

Không tệp nào ở đây được mã hiện hành import hay gọi. Giữ lại thay vì xoá để chủ nhiệm
đối chiếu; xoá cả thư mục này không ảnh hưởng tới bất kỳ lệnh nào trong README.

| Thư mục | Nội dung | Lý do rút |
|---|---|---|
| `de_cuong_patch_scripts/` | `patch_bia.py`, `patch_doansai.py`, `patch_fig.py`, `patch_readme.py`, `patch_v34.py`, `show_input.py` | script vá một lần cho đề cương v3.3/v3.4, đã chạy xong; kết quả đã nằm trong `de_cuong_latex/*.tex`; không tệp nào khác gọi tới |
| `demo_screenshots_v1/` | `01_r01_tin_hieu.png`, `02_r01_fhr.png`, `04_r01_the_so.png`, `05_a02_den_do.png`, `06_a02_tin_hieu.png` | bộ ảnh demo đời đầu (mô hình 5 ca, chọn kênh PSD, giao diện 4 tab) — bị thay bởi 12 ảnh theo kịch bản 5 bản minh hoạ trong `demo/screenshots/` (P3, 12/09/2026) |
| `one_off_scripts/` | `benchmark_dpss/_watch_eval22.py`, `baselines/powermf_status_update.py` | script theo dõi tiến trình / cập nhật trạng thái dùng một lần trong vòng 2–3; không được gọi từ đâu |

Đã **xoá hẳn** (có sẵn trong lịch sử git, xem `DON_REPO_VONG7.md` để biết commit chứa bản gốc):
`*.bak_vong5` (5 tệp trong `de_cuong_latex/`), `*.bak_integrity` (5 tệp, bản trước sửa liêm chính,
bằng đúng blob tại `da17651` / `d4b44f2`), `paper/cinc2026/*.bak_b2|b3|round2|vong5`.
Hai tệp `*_stdout.txt` trùng byte với `*_log.txt` tương ứng đã bỏ theo dõi (vẫn nằm trên đĩa, `.gitignore` đã có quy tắc).
