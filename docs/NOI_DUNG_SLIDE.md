# NỘI DUNG SLIDE — buổi gặp giảng viên hướng dẫn 14/09/2026

> **⚠ CẢNH BÁO (17/09/2026) — tệp lưu trữ.** Tệp viết cho buổi 14/09 và mô tả demo **8 tab / 16 ảnh** như mặc
> định; demo hiện mở **chế độ trình bày 5 bước**, 8 tab nằm trong chế độ chuyên gia. Dựng slide mới theo
> `docs/KICH_BAN_THUYET_TRINH_v2.md` và `docs/HUONG_DAN_DEMO_v2.md`. Ngày 17/09/2026 đã sửa tại chỗ các lỗi sự
> thật: cổng từ chối không độc lập với mạng; "17,92 điểm" đã rút (thay bằng 23,28 theo PSD); 0,934 ghi rõ phạm
> vi 11/22 chủ thể; bỏ số kiểm thử cố định ở slide bìa. Cùng ngày, đồng bộ với demo sau lượt sửa thứ ba: slide 1–2
> theo tiêu đề demo *chỉ cần một kênh* và câu đèn không nói quá; bỏ "máy khác" ở slide CinC; 109 kiểm thử.

**Đề tài:** RelyFetal — dò phức bộ QRS thai nhi từ một đạo trình bụng, có cổng từ chối
**Chủ nhiệm:** Ngô Bình Minh · NCKH sinh viên TDTU 2026–2027
**Tệp này viết ngày:** 13/09/2026 · **Buổi gặp:** 14/09/2026
**Thời lượng dự kiến:** 20–25 phút (26 slide) · **Người dựng slide:** chủ nhiệm (artifact HTML)

> **Quy tắc của tệp này.** Mỗi con số trên slide đều ghi kèm tệp JSON nguồn trong trường
> HÌNH/BẢNG. Nguồn tổng hợp: `survey/facts_phase4.json`. Không có con số nào tính trên 75 bản
> CinC, không có con số nào nằm trong mục `Z_DA_RUT`. Danh sách từ cấm ở cuối tệp.
>
> **Cách đọc:** phần NỘI DUNG CHÍNH là chữ **in trên slide** (tối đa 5 gạch đầu dòng, mỗi dòng
> tối đa 12 từ). Phần GHI CHÚ NGƯỜI NÓI là chữ **không in trên slide**, chủ nhiệm nói miệng.

---

## SLIDE 1

**TIÊU ĐỀ:** RelyFetal — nhịp tim thai, chỉ cần một kênh

**LOẠI:** tiêu đề

**NỘI DUNG CHÍNH:**
- Dò phức bộ QRS thai từ một đạo trình bụng
- Có cổng từ chối khi không đáng tin
- Ngô Bình Minh · Khoa Khoa học Máy tính, TDTU
- Nghiên cứu khoa học sinh viên 2026–2027
- Báo cáo tiến độ · 14/09/2026

**HÌNH/BẢNG:** Ba ô số lớn xếp ngang dưới tiêu đề, không viền, nền nhạt:
`113.481 tham số` · `22 sản phụ` · `60 bản ghi kiểm ngoài`.
Nguồn: 113.481 từ `analysis/kientruc_results.json → table.tcn.params`; 22 chủ thể từ
`baselines/powermf_fair_stats.json → so_sanh.tat_ca_22.rely_vs_pmf4.n`; 60 bản ghi từ
`analysis/dulieu_results.json → chon_kenh_60_sach.bang.psd.n`. **Không ghi số kiểm thử trên bìa** — số này đổi
theo từng vòng (17/09/2026 sau lượt sửa demo thứ ba: 109 = 43 + 66, đếm bằng `pytest --collect-only tests/ demo/test_core.py`).

**GHI CHÚ NGƯỜI NÓI:** "Em chào cô. Em xin khoảng 20 phút, có demo ở giữa, cô ngắt bất cứ lúc nào
cũng được ạ." Nói rõ đây là báo cáo tiến độ, không phải xin duyệt kết quả. Nêu ngay ba con số
khung: một mô hình rất nhỏ, 22 sản phụ huấn luyện, 60 bản ghi của bộ khác để kiểm ngoài. Không
đọc to bốn ô số — để cô tự đọc trong lúc mình giới thiệu tên.

---

## SLIDE 2

**TIÊU ĐỀ:** Đề tài này là gì

**LOẠI:** số lớn (một câu, chữ to)

**NỘI DUNG CHÍNH:**
- Tìm từng nhịp tim thai trên bụng mẹ, chỉ một kênh —
- và nói "tôi không chắc" khi thấy dấu hiệu tín hiệu xấu.

**HÌNH/BẢNG:** Không có hình. Một câu duy nhất, cỡ chữ 40–48 pt, căn giữa, chiếm cả slide.
Tô đậm hai cụm: **một kênh** và **nói "tôi không chắc"**. Không có số liệu trên slide này.

**GHI CHÚ NGƯỜI NÓI:** Dừng lại 3 giây sau khi chiếu, để cô đọc xong câu rồi mới nói. "Vế đầu là
phần kỹ thuật, ai cũng làm. Vế sau mới là phần em coi là chính: hệ thống báo khi thấy dấu hiệu nó không
đáng tin và từ chối trả lời, thay vì đưa ra một con số sai. Không phải lần nào nó cũng thấy." Nói thêm: tầm nhìn xa là miếng dán
mẹ tự đeo ở nhà, nhưng đó là tầm nhìn, chưa phải sản phẩm. Nếu bị hỏi "có lúc nào đèn không thấy không":
có — trong 82 bản đã chấm, 3 bản đèn xanh mà F1 dưới 90, thấp nhất a57 F1 17,02 (`demo/results/demo_check_2modes.json → summary_by_mode.hoc.green_but_F1_below_90`).

---

## SLIDE 3

**TIÊU ĐỀ:** Vấn đề lâm sàng

**LOẠI:** nội dung

**NỘI DUNG CHÍNH:**
- Theo tài liệu nhóm đọc, thai chậm phát triển gắn với nguy cơ thai lưu [CẦN KIỂM BẢN GỐC]
- Giảm biến thiên nhịp tim thai là một dấu hiệu được theo dõi [CẦN KIỂM BẢN GỐC]
- Đo biến thiên cần biết từng nhịp đến mili-giây
- CTG (Doppler) phổ biến, cho nhịp tim nhưng không cho hình dạng sóng điện tim; CTG thương mại có tính biến thiên ngắn hạn theo Dawes–Redman [CẦN KIỂM BẢN GỐC]
- Điện cực da đầu chính xác nhưng xâm lấn, chỉ khi chuyển dạ

**HÌNH/BẢNG:** Bảng nhỏ 3 dòng × 3 cột: *Cách đo* | *Cho gì* | *Dùng được khi nào*.
Ba dòng: Doppler (CTG) / nhịp tim, không có hình dạng sóng / trước và trong chuyển dạ — Điện cực da đầu / tín hiệu điện sạch, từng nhịp / chỉ khi đã chuyển dạ —
Điện tim bụng mẹ / tín hiệu điện từng nhịp, lẫn tim mẹ / về nguyên tắc mọi lúc, không xâm lấn. Bảng này là **mô tả định tính, không có số đo
của nhóm** — ghi chú chân slide: "đặc tính chung, không phải kết quả đo của đề tài".

**GHI CHÚ NGƯỜI NÓI:** Nhấn vào chỗ này: cái bác sĩ cần không phải nhịp nhanh hay chậm, mà là
biến thiên — và biến thiên chỉ đo được khi biết từng nhịp rơi vào mili-giây nào. Nói thẳng là em
chưa gặp bác sĩ sản nào để hỏi ngưỡng chính xác cần bao nhiêu, và đó là một trong ba thứ em sẽ
xin cô ở cuối buổi. Không hứa hẹn gì về thiết bị.

---

## SLIDE 4

**TIÊU ĐỀ:** Vì sao bài toán này khó

**LOẠI:** nội dung

**NỘI DUNG CHÍNH:**
- Tín hiệu thai nhỏ hơn tim mẹ nhiều lần, trùng dải tần
- Bẫy 1: mô hình bám tàn dư tim mẹ, ra nhịp rất đều
- Bẫy 2: kênh nào đọc được thay đổi theo từng bản ghi
- Bẫy 3: dữ liệu có nhãn thật rất ít, dễ rò rỉ
- Cả ba bẫy đều đã cắn em một lần

**HÌNH/BẢNG:** Ba thẻ ngang, mỗi thẻ một con số đo được:
(1) Bẫy 1 → `a02: F1 24,91 · 78 % nhịp "thai" trùng đỉnh mẹ` — nguồn
`demo/results/demo_check_showcase.json`, đối chiếu `survey/facts_phase4.json → F_demo`.
(2) Bẫy 2 → `chọn kênh đúng đáng 9,32 điểm F1 (74,28 → 83,60)` — nguồn
`benchmark_dpss/eval_cinc60_sach.json → variants.60_sach.psd_vs_oracle_m22.hieu` = 9,32.
(3) Bẫy 3 → `15 / 75 bản của bộ kiểm chuẩn là bản sao của dữ liệu huấn luyện` — nguồn
`analysis/dulieu_results.json → chong_lan.n_ro_ri` = 15.

**GHI CHÚ NGƯỜI NÓI:** Đây là slide đặt bẫy cho cả phần sau: ba con số này quay lại ở slide 14,
18 và 19. Nói câu cuối thật rõ — "cả ba bẫy đều đã cắn em một lần" — vì đó là lời hứa với cô rằng
phần vấp sẽ được kể thật chứ không giấu. Nếu cô hỏi ngay "rò rỉ là sao", trả lời một câu: "bộ
kiểm ngoài có chứa chính bản ghi em huấn luyện, ban tổ chức đã ghi nhận từ 2013, em sẽ nói kỹ ở
slide 18" rồi đi tiếp.

---

## SLIDE 5

**TIÊU ĐỀ:** Hai câu hỏi nghiên cứu

**LOẠI:** nội dung

**NỘI DUNG CHÍNH:**
- **RQ1 — Đến mức nào?** Một kênh lấy lại bao nhiêu phần của bốn kênh?
- Đo bằng cùng bản ghi, cùng bộ chấm, cùng baseline
- **RQ2 — Có biết không?** Hệ thống có tự nhận ra lúc mình sai?
- Đo bằng bỏ-một-chủ-thể, không dùng nhãn khi quyết định
- Hai câu này quyết định mọi thí nghiệm còn lại

**HÌNH/BẢNG:** Hai khối lớn cạnh nhau, mỗi khối một câu hỏi + một dòng "đo thế nào". Không số
liệu. Dưới mỗi khối ghi tên slide kết quả tương ứng: RQ1 → slide 12–13; RQ2 → slide 15.

**GHI CHÚ NGƯỜI NÓI:** Nói rõ đây **không** phải câu hỏi "làm sao cho F1 cao hơn". Câu hỏi là một
phép đo có ranh giới: mất bao nhiêu khi cắt từ bốn dây xuống một dây, và hệ thống có tự biết
không. Giải thích vì sao đóng khung như vậy: nếu đặt mục tiêu là "cao nhất" thì với 22 chủ thể
sẽ không bao giờ chứng minh được gì; còn một phép đo có khoảng tin cậy thì đứng vững.

---

## SLIDE 6

**TIÊU ĐỀ:** Tổng quan: 30 công trình đã đọc

**LOẠI:** bảng

**NỘI DUNG CHÍNH:**
- Đã đọc toàn văn 30 công trình về điện tim thai
- Hướng chính: tách nguồn đa kênh (4–32 điện cực)
- Hướng hai: lọc thích nghi / trừ mẫu trên phần dư
- Hướng ba: học sâu đầu-cuối trên CinC 2013 set-a
- Khoảng trống: ba điểm ở bảng dưới

**HÌNH/BẢNG:** Hai bảng nhỏ xếp dọc.
*Bảng A — số tác giả công bố, khác bộ chấm, chỉ để định hướng* (nguồn `survey/scout_baselines.md`
mục 0.3, trích từ `Results/*.mat` của kho Power-MF; đối chiếu `baselines/powermf_published.json`):

| Phương pháp (số kênh) | Silesia B1 | Silesia B2 |
|---|---:|---:|
| Power-MF (4 kênh) | 99,46 | 97,98 |
| Varanini 2014 (4 kênh) | 99,37 | 97,95 |
| Behar 2014 | 90,41 | 87,68 |
| Sulas 2021 | 63,04 | 65,36 |

*Bảng B — ba khoảng trống:* (1) không bài nào giữ cố định bộ chấm + giao thức để so các phương
pháp; (2) không bài nào trả lời "bản ghi **này** có đáng tin không", chỉ báo F1 trung bình;
(3) chồng lấn set-a ↔ ADFECGDB đã được ban tổ chức ghi nhận từ 2013 nhưng **mức thổi phồng chưa
ai định lượng** — nguồn `survey/ro_ri_vanlieu.json → ket_luan`.

**GHI CHÚ NGƯỜI NÓI:** Nói rõ bảng A là số **tác giả công bố**, không phải số em đo, và hai bên
không cùng bộ chấm — nên chỉ dùng để thấy thứ hạng chung, không dùng để tuyên bố hơn thua. Nhấn
vào khoảng trống số 2: cả 30 bài đều báo một con số trung bình, không bài nào nói được với một
bản ghi cụ thể thì tin được hay không — đó chính là RQ2 của em. Nếu cô hỏi "có bài nào bị rò rỉ
không": có, bốn bài đã xác định (`survey/ro_ri_vanlieu.json → bang_bi_nhiem.chac_chan`), em sẽ
nói ở slide 19.

---

## SLIDE 7

**TIÊU ĐỀ:** Đường ống năm bước

**LOẠI:** biểu đồ (sơ đồ khối)

**NỘI DUNG CHÍNH:**
- 1. Lọc Butterworth 10–60 Hz pha-không, notch 50 Hz
- 2. Khử điện tim mẹ: mẫu trung vị, co giãn từng nhịp
- 3. Chọn kênh **mù nhãn** — không nhìn nhãn khi chọn
- 4. Mạng tích chập thời gian → xác suất từng mẫu
- 5. Cổng từ chối: 12 chỉ số, 6 dựa trên đầu ra mạng

**HÌNH/BẢNG:** **SƠ ĐỒ KHỐI ngang, 5 hộp nối bằng mũi tên.** Dưới mỗi hộp một dòng nhỏ:
hộp 1 "→ 250 Hz"; hộp 2 "tỉ lệ bình phương tối thiểu từng nhịp"; hộp 3 "4 kênh → 1 kênh";
hộp 4 "113.481 tham số · 0,48 MB · 4,35 ms / cửa sổ 4 s";
hộp 5 "12 chỉ số / đoạn 4 s, không dùng nhãn, không độc lập với mạng". Hộp 3 và hộp 5 tô màu nhấn — đó là hai đóng góp. Nguồn thông số
hộp 4: `analysis/kientruc_results.json → table.tcn` (params 113481, rf_ms 1516, sigma_ms 12).

**GHI CHÚ NGƯỜI NÓI:** Đi nhanh, 45 giây. Chỉ dừng ở hai hộp tô màu: hộp 3 là chỗ em có kết quả
ngoài miền (slide 14), hộp 5 là cổng từ chối (slide 15). Nói rõ "mù nhãn" nghĩa là quy tắc chọn
kênh không được nhìn nhãn — em đã kiểm bằng phép xáo nhãn, 0 trên 776 lựa chọn kênh thay đổi.

---

## SLIDE 8

**TIÊU ĐỀ:** Mô hình: nhỏ, chạy được trên CPU

**LOẠI:** bảng

**NỘI DUNG CHÍNH:**
- TCN giãn nở dư, chuỗi-sang-chuỗi, đầu ra từng mẫu
- 113.481 tham số · 0,48 MB — chạy được trên điện thoại
- Trường tiếp nhận 379 mẫu = 1.516 ms ≈ ba nhịp thai
- 4,35 ms cho mỗi cửa sổ 4 giây trên CPU
- Đầu ra: bản đồ nhiệt Gauss, sigma 12 ms

**HÌNH/BẢNG:** Bảng hai cột *Thuộc tính | Giá trị*, 6 dòng: tham số 113.481 · kích thước 0,48 MB ·
trường tiếp nhận 1.516 ms · sigma đầu ra 12 ms · tốc độ 4,35 ms/cửa sổ 4 s · huấn luyện 22 chủ
thể, grouped 11-fold. Nguồn: `analysis/kientruc_results.json → table.tcn` (params, rf_ms,
sigma_ms); các số kích thước/tốc độ từ `survey/facts_phase4.json` và `model/fqrs_model.py`.
Bên phải: một hình nhỏ minh hoạ trường tiếp nhận 1,5 s chồng lên ~3 nhịp thai (RR ≈ 450 ms).

**GHI CHÚ NGƯỜI NÓI:** Vì sao TCN chứ không phải LSTM hay Transformer: cần đầu ra từng mẫu để
định vị đỉnh đến mili-giây, cần chạy trên CPU, và cần trường tiếp nhận đủ rộng để thấy nhịp
trước và nhịp sau. Con số 1.516 ms không phải chọn bừa — slide sau cho thấy chính bề rộng ngữ
cảnh mới là thứ quan trọng, chứ không phải họ kiến trúc. Nói luôn: mô hình nhỏ là **có chủ đích**,
không phải hạn chế.

---

## SLIDE 9

**TIÊU ĐỀ:** Chọn kiến trúc thế nào — và kết quả

**LOẠI:** biểu đồ + bảng

**NỘI DUNG CHÍNH:**
- 7 họ kiến trúc, cùng tham số ±2,7 %, cùng seed/fold/epoch
- Ba họ đầu cách nhau dưới 0,1 điểm (TOST tương đương)
- Họ kém nhất thua 3,10 điểm vì trường tiếp nhận 60 ms
- Nới trường tiếp nhận cho đúng họ đó → 96,84
- Kết luận: khoảng cách đo **bề rộng ngữ cảnh**, không phải họ kiến trúc

**HÌNH/BẢNG:** **BIỂU ĐỒ PHÂN TÁN (scatter).** Trục X: trường tiếp nhận (ms, thang log, 60 → 3052).
Trục Y: macro F1 22 chủ thể (thang 94–98). Mỗi điểm một họ, có nhãn tên. Vẽ đường cong bão hoà
mềm qua các điểm, đánh dấu vùng "bão hoà từ ~1,5 s". Nguồn mọi điểm:
`analysis/kientruc_results.json → table.<ho>.macro_psd` và `.rf_ms`.

| Họ | F1 | Trường tiếp nhận | Tham số so TCN |
|---|---:|---:|---:|
| tcn (sản xuất) | 97,64 | 1.516 ms | 0 % |
| rf_wide | 97,63 | 3.052 ms | +2,67 % |
| tcn_ms | 97,62 | 2.716 ms | +2,23 % |
| rf_narrow | 96,93 | 748 ms | +1,24 % |
| cnn_wide | 96,84 | 1.508 ms | +1,29 % |
| unet1d | 96,38 | 636 ms | +0,68 % |
| cnn_l | 94,53 | 60 ms | +0,89 % |

Chân bảng: *TOST hiệu chỉnh Holm ở biên 1,0 điểm: rf_wide p = 7,1e-10, tcn_ms p = 4,6e-06 →
tương đương TCN* (`analysis/kientruc_results.json → holm_tost`). *Giao thức thu nhỏ: 3 epoch,
3 fold, 1 hạt giống — nên là kết quả sơ bộ; F1 sản xuất đầy đủ 11 fold là 97,56.*

**GHI CHÚ NGƯỜI NÓI:** Đây là một thí nghiệm em làm để **tự bác bỏ mình**: nếu đổi kiến trúc là
đòn bẩy thì phải thấy chênh lệch lớn, mà không thấy. Chỉ tay vào cnn_l (94,53) rồi cnn_wide
(96,84): cùng một họ tích chập, chỉ khác bề rộng ngữ cảnh, đi từ 60 ms lên 1,5 s là lấy lại 2,3
điểm. Kết luận thực dụng: em **ngừng đầu tư vào đổi kiến trúc**, và đó là một trong hai việc em
quyết định không làm nữa. Cảnh báo trung thực: giao thức này thu nhỏ (3 epoch, 3 fold, 1 hạt
giống) nên là bằng chứng định hướng, không phải kết luận chắc.

---

## SLIDE 10

**TIÊU ĐỀ:** Dữ liệu — và điểm yếu của nó

**LOẠI:** bảng

**NỘI DUNG CHÍNH:**
- 22 chủ thể trong miền: 5 ADFECGDB + 17 Silesia
- 60 bản ghi CinC 2013 set-a sạch để kiểm ngoài
- Silesia B1 dùng nhãn **gián tiếp** — em nói thẳng
- Không bộ công khai nào khác có nhãn nhịp thai thật
- 22 chủ thể là quá ít; cần khoảng 50

**HÌNH/BẢNG:** Bảng 4 dòng × 6 cột: *Bộ | n | Thời lượng | Loại nhãn | Vai trò | Điểm yếu*.

| Bộ | n | Thời lượng | Nhãn | Vai trò | Điểm yếu |
|---|---:|---|---|---|---|
| ADFECGDB | 5 | 300 s | trực tiếp, điện cực da đầu | huấn luyện + kiểm | chỉ 5 sản phụ |
| Silesia B2 (chuyển dạ) | 7 | 300 s | trực tiếp, điện cực da đầu | huấn luyện + kiểm | 5 bản trùng PhysioNet |
| Silesia B1 (thai kỳ) | 10 | 1.198 s | **gián tiếp** | huấn luyện + kiểm | nhãn gián tiếp |
| CinC 2013 set-a (sạch) | 60 | 60 s | người chấm độc lập | **kiểm ngoài** | 60 s/bản, 7 bản nhãn sai |

Nguồn n và thời lượng: `analysis/CLINICAL.md` bảng mục 0; n = 60 từ
`analysis/dulieu_results.json → chon_kenh_60_sach.ban_ghi_sach`; 7 bản chú thích sai
(a33 a38 a47 a52 a54 a71 a74) từ `benchmark_dpss/eval_cinc60_sach.json →
variants.53_sach_loai_7_nhan_sai`. Dòng "không bộ nào khác có nhãn thật": nguồn
`analysis/xacnhan_results.json → viec2_bo_thu_ba` (NIFEADB, NInFEA, nifecgdb, set-b — đã kiểm
từng bộ). Ô "công suất thống kê" ở góc: *hiệu ứng 2 điểm chỉ do 1/7 chủ thể mang → cần n ≈ 50
(t ghép cặp) hoặc n ≈ 160 (Wilcoxon) để đạt power 0,80.*

**GHI CHÚ NGƯỜI NÓI:** Slide này cố ý đặt điểm yếu vào cùng một bảng với điểm mạnh. Ba điểm yếu
phải nói miệng, không giấu: B1 dùng nhãn gián tiếp; 22 chủ thể là ít; và em đã đi kiểm bốn bộ
công khai khác để tìm bộ thứ ba có nhãn thật, không bộ nào có — NIFEADB không chú thích thai,
NInFEA chỉ có Doppler, tệp `.qrs` của nifecgdb thực ra là QRS mẹ ở 86 nhịp/phút, set-b chưa công
bố nhãn. Đó là lý do slide 24 em xin cô đầu mối khoa sản.

---

## SLIDE 11

**TIÊU ĐỀ:** Vì sao phải tự chạy lại baseline

**LOẠI:** nội dung

**NỘI DUNG CHÍNH:**
- So với số in trên giấy là so hai bộ chấm khác nhau
- Nên em chạy lại Power-MF bằng GNU Octave, không có MATLAB
- Kiểm chứng ngoài: Silesia B1 em đo 99,40 — tác giả công bố 99,46
- Lệch 0,06 điểm → cổng chuyển của em đúng
- Từ đó mọi so sánh dùng **cùng bộ chấm ±50 ms**

**HÌNH/BẢNG:** Hình đối chiếu hai cột lớn: `99,40 (em chạy lại, Octave)` — `99,46 (tác giả công
bố)`, ở giữa là dấu ≈ và dòng `Δ = 0,06 điểm`. Nguồn 99,40: `baselines/powermf_fair_stats.json →
so_sanh.b1_10.rely_vs_pmf4.mean_b` = 99,397; nguồn 99,46: `baselines/powermf_published.json`
(trích từ `Results/*.mat` của kho tác giả). Dưới cùng, một dòng nhỏ: *quy trình chấm: ghép 1–1,
dung sai ±50 ms, F1 tính ở mức chủ thể.*

**GHI CHÚ NGƯỜI NÓI:** Đây là bước không tạp chí nào tính là đóng góp, nhưng thiếu nó thì mọi
con số ở slide 12 vô nghĩa. Giải thích ngắn: mỗi bài dùng một dung sai ghép, một cách tính F1,
một tập con bản ghi — nên đối chiếu số in trên giấy là so hai thước đo khác nhau. Em cài Octave,
chuyển mã Power-MF sang chạy được, rồi kiểm bằng cách tái tạo đúng con số tác giả trên B1. Lệch
0,06 điểm là đủ để tin cổng chuyển. Nói luôn: lần đầu em chuyển **sai** và đã rút số đó — chi
tiết ở slide 18.

---

## SLIDE 12

**TIÊU ĐỀ:** Kết quả 1 — trong miền, 22 chủ thể

**LOẠI:** bảng + biểu đồ

**NỘI DUNG CHÍNH:**
- Power-MF 4 kênh **98,83** — Power-MF 1 kênh **86,71**
- RelyFetal 1 kênh **97,56**
- So 4 kênh: **−1,27** [−3,08; +0,27], p 0,156 — chưa phân biệt được
- So 1 kênh: **+10,85** [+6,80; +15,40], thắng 22/22
- Nói thẳng: **em vẫn thua 4 kênh**, nhưng khoảng tin cậy chạm 0

**HÌNH/BẢNG:** **BIỂU ĐỒ ĐIỂM GHÉP CẶP (paired dot / slopegraph), 22 chủ thể.**
Trục Y: F1 mức chủ thể (80–100, cắt trục có ghi chú). Ba cột X: `Power-MF 1 kênh` →
`RelyFetal 1 kênh` → `Power-MF 4 kênh`. Mỗi chủ thể một đường mảnh nối ba điểm; tô ba màu theo
nhóm (ADFECGDB / B1 / B2). Chồng lên: ba chấm lớn là trung bình 86,71 / 97,56 / 98,83.
Nguồn từng chủ thể: `baselines/powermf_fair_stats.json → per_subject` (khoá `rely`, `pmf1`,
`pmf4`). Nguồn ba trung bình và các hiệu số:
`baselines/powermf_fair_stats.json → so_sanh.tat_ca_22`.

Bảng nhỏ kèm bên dưới:

| So sánh | Δ F1 | KTC 95 % | p Wilcoxon | thắng/hoà/thua |
|---|---:|---|---:|---|
| Rely − Power-MF 4 kênh | −1,27 | [−3,08; +0,27] | 0,156 | 18/0/4 |
| Rely − Power-MF 1 kênh | +10,85 | [+6,80; +15,40] | 4,8e-07 | 22/0/0 |
| Power-MF 1 kênh − 4 kênh | −12,12 | [−18,27; −6,90] | 1,4e-06 | 1/0/21 |

**GHI CHÚ NGƯỜI NÓI:** Đọc bảng theo đúng thứ tự này, đừng đảo: trước hết em **thua** bốn kênh
1,27 điểm; khoảng tin cậy từ −3,08 đến +0,27 nên chưa phân biệt được, nhưng em thắng ở 18 trên 22
bản. Điều đáng nói nằm ở dòng thứ ba: cắt chính Power-MF từ bốn kênh xuống một kênh thì nó mất
12,12 điểm. Đó là cái giá của việc mất đa dạng không gian, và slide sau nói em lấy lại được bao
nhiêu phần cái giá đó. Không được nói "một kênh hơn bốn kênh" — em đã rút câu đó.

---

## SLIDE 13 ⭐ (một trong hai slide quan trọng nhất)

**TIÊU ĐỀ:** Kết quả 1b — một kênh lấy lại bao nhiêu

**LOẠI:** số lớn

**NỘI DUNG CHÍNH:**
- **89,49 %** — KTC 95 % [81,4 ; 103,2]
- Một kênh lấy lại gần chín phần mười lợi ích của bốn kênh
- Bốn kênh đáng 12,12 điểm · mạng một kênh lấy lại 10,85
- Jackknife bỏ từng chủ thể: 88,6 – 93,4 % (không do một ca)
- Đây là một **phép đo**, so với một baseline, trên 22 chủ thể

**HÌNH/BẢNG:** **SỐ 89,49 % cỡ 120–150 pt, chiếm nửa trên slide**, bên dưới là khoảng tin cậy cỡ
nhỏ hơn. Nửa dưới: **BIỂU ĐỒ THANH XẾP CHỒNG NGANG, chỉ một thanh.**
Tổng chiều dài thanh = 12,12 điểm (nhãn: "giá trị của bốn kênh, đo trên chính Power-MF").
Phần tô đậm = 10,85 điểm (nhãn: "một kênh lấy lại"), phần còn lại nhạt = 1,27 điểm (nhãn:
"chưa lấy lại được"). Trên thanh vẽ thanh lỗi cho khoảng [81,4 %; 103,2 %].
Nguồn mọi số: `analysis/recovery_ratio.json` — `gia_tri_da_kenh_diem` 12,1212;
`phan_lay_lai_diem` 10,847; `ti_le_pct` 89,49; `ktc95_cluster_bootstrap_chu_the` [81,4; 103,16];
`jackknife_bo_tung_chu_the_min_max` [88,62; 93,43]; `n_boot` 10 000, `seed` 0.

**GHI CHÚ NGƯỜI NÓI:** Đây là con số em muốn cô nhớ nhất, và cũng là con số em phải rào kỹ nhất.
Cách đọc: lấy chính Power-MF, chạy nó với bốn kênh rồi với một kênh — chênh lệch 12,12 điểm là
giá trị của đa kênh, đo trên cùng bản ghi cùng bộ chấm. Mạng một kênh của em lấy lại 10,85 trong
số đó, tức 89,5 %. Khoảng tin cậy trên vượt 100 % vì bootstrap theo chủ thể, đó là điều bình
thường và em không cắt nó về 100 để đẹp. Jackknife bỏ từng chủ thể vẫn cho 88,6 đến 93,4 nên kết
quả không do một ca dễ gánh. Ranh giới phải nói: đây là phép đo **so với một baseline**, không
phải tuyên bố chung về mọi phương pháp đa kênh.

---

## SLIDE 14 ⭐ (một trong hai slide quan trọng nhất)

**TIÊU ĐỀ:** Kết quả 2 — ngoài miền, 60 bản sạch

**LOẠI:** bảng + biểu đồ

**NỘI DUNG CHÍNH:**
- CinC 2013 set-a, người chấm độc lập, mô hình chưa từng thấy
- 7 quy tắc chọn kênh, hiệu chỉnh Holm cả họ
- **gate4** (quy tắc trong họ khai báo trước): 81,01 · p Holm **0,015 — sống sót**
- **gate** (quy tắc luật chỉ định): 80,72 · p Holm **0,051 — trượt**
- **peakprob** 82,01 cao nhất, nhưng là lựa chọn **hậu kiểm**

**HÌNH/BẢNG:** **BIỂU ĐỒ RỪNG (forest plot) nằm ngang** — đây là hình chính của buổi.
Trục X: Δ F1 so với quy tắc PSD hiện dùng (−2 → +14). Mỗi dòng một quy tắc, chấm = hiệu số,
thanh = KTC 95 %. Vạch đứng đậm ở 0. Ghi p Holm ở cột phải mỗi dòng. Tô ba màu:
xanh đậm = sống sót Holm (gate4, peakprob), xám = trượt (gate, rrcv, rrplaus, learned),
nét đứt = oracle (giới hạn trên, có dùng nhãn).
Nguồn mọi dòng: `analysis/dulieu_results.json → chon_kenh_60_sach.bang.<quy_tắc>`
(khoá `mean_60_sach`, `hieu_vs_psd`, `ci95`, `wilcoxon_p`, `holm_p`, `thang/thua/hoa`, `lt50`);
đối chiếu `survey/facts_phase4.json → B_chon_kenh_7_quy_tac_60_sach`.

| Quy tắc | F1 | Δ vs PSD | KTC 95 % | p Holm | thắng/hoà/thua | F1 < 50 |
|---|---:|---:|---|---:|---|---:|
| PSD (đang dùng) | 74,28 | — | — | — | — | 16 |
| learned | 77,80 | +3,52 | [−0,77; +8,48] | 1,00 | 15/32/13 | 16 |
| rrplaus | 78,87 | +4,59 | [+0,88; +8,93] | 0,41 | 17/34/9 | 14 |
| rrcv | 80,00 | +5,72 | [+1,61; +10,41] | 0,41 | 15/35/10 | 12 |
| **gate** *(luật chỉ định trước)* | 80,72 | +6,44 | [+2,49; +11,10] | **0,051 — trượt** | 16/37/7 | 12 |
| **gate4** *(cùng họ khai báo trước)* | **81,01** | +6,72 | [+2,85; +11,18] | **0,015 — sống sót** | 17/38/5 | 12 |
| **peakprob** *(hậu kiểm)* | **82,01** | +7,73 | [+3,82; +12,41] | **0,0039** | 19/35/6 | **9** |
| oracle (dùng nhãn) | 83,60 | +9,32 | — | — | — | 8 |

Ba ô nhỏ dưới bảng: `peakprob lấy lại 82,9 % dư địa oracle` · `không bản nào mất quá 3,90 điểm` ·
`phép xáo nhãn đổi 0 / 776 lựa chọn kênh → chọn kênh là mù nhãn`.
Nguồn: `analysis/dulieu_results.json → chon_kenh_60_sach.bang.peakprob.phan_tram_du_dia_oracle`
= 82,92; `analysis/chonkenh_leakcheck.py`; README mục Lead selection.

**GHI CHÚ NGƯỜI NÓI:** Đây là slide em muốn cô chất vấn nhiều nhất. Bốn ý, theo thứ tự:
(1) Bối cảnh — bộ này của nhóm khác, không trùng dữ liệu huấn luyện (ban tổ chức không công bố thiết bị ghi
của từng bản), người chấm độc lập, mô hình chưa từng thấy, và em
đã loại 15 bản trùng nên còn 60 bản sạch.
(2) Trung thực về thủ tục — em viết trước một tài liệu phân tích với luật "lấy quy tắc tốt nhất
trong miền". Luật đó chỉ vào `gate`. Gate trên 60 bản sạch cho 80,72 và **trượt** hiệu chỉnh
Holm với p 0,051. Em không giấu chuyện đó.
(3) `gate4`: cùng họ ghi trước khi chạy, 81,01, p Holm 0,015, sống sót — nhưng nó **không phải**
quy tắc kế hoạch chọn, nên em luôn đọc nó cùng câu "gate 80,72 trượt", không đọc riêng.
(4) `peakprob` 82,01 là cao nhất nhưng em chọn **sau khi nhìn kết quả**, nên em gọi nó là giả
thuyết mạnh chưa xác nhận. Em đã thử hai đường cứu: tính lại trên thang logit ở 22 chủ thể — gate
vẫn đứng đầu, peakprob hạng 3; và tìm bộ thứ ba có nhãn để chạy đúng một lần — không có bộ công
khai nào. Nên vấn đề hậu kiểm vẫn còn.
Nếu cô hỏi "vậy con số nào được dùng": số chính vẫn là PSD 74,28; quy tắc kế hoạch chọn (gate 80,72)
trượt; gate4 81,01 sống sót Holm nhưng không phải quy tắc kế hoạch chọn; peakprob là giả thuyết.

---

## SLIDE 15

**TIÊU ĐỀ:** Kết quả 3 — cổng từ chối

**LOẠI:** biểu đồ + nội dung

**NỘI DUNG CHÍNH:**
- 12 chỉ số (6 dựa trên đầu ra mạng), bỏ-một-chủ-thể, **không dùng nhãn**
- AUROC trong bản ghi **0,934** [0,872; 0,981] — trên 11/22 chủ thể
- Xếp đúng 3 bản khó nhất vào 3 hạng chót (ngẫu nhiên 1/1540)
- Nhưng 5 / 24 quy tắc **một đặc trưng** cũng làm được như vậy
- Nên: cổng học được có thể chỉ tương đương một ngưỡng SNR

**HÌNH/BẢNG:** **BIỂU ĐỒ THANH NGANG XẾP HẠNG, 22 chủ thể.**
Trục Y: 22 chủ thể xếp theo điểm tin cậy của cổng (kém tin cậy nhất ở dưới cùng).
Trục X: điểm tin cậy (`score`, 0–1). Tô màu thanh theo F1 thật của chủ thể đó (thang liên tục).
Khoanh đỏ ba thanh dưới cùng và ghi `B2_03 (F1 79,72 (kênh PSD))`, `B1_07 (F1 86,56)`, `B1_06 (F1 89,45)`.
Nguồn: `analysis/gate22_results.json → muc_ban_ghi.bang` (khoá `score`, `rely`, `record`);
thứ hạng từ `muc_ban_ghi.hang_cua_ba_ban_ghi_kho` = {B2_03: 1, B1_07: 2, B1_06: 3};
AUROC từ `cong.auroc_within_mean` = 0,9336 và `cong.auroc_within_ci` = [0,8717; 0,9810];
AUROC gộp `cong.auroc_pooled` = 0,9646 [0,8568; 0,9922];
đối chứng một đặc trưng: `muc_ban_ghi.doi_chung_mot_dac_trung` — 5 trong 24 quy tắc đạt 3/3.
Phạm vi 0,934: trung bình trên **11/22** chủ thể có cả đoạn tốt lẫn đoạn xấu (`cong.n_records_with_both_classes`).
Độ quan trọng hoán vị: `cong.permutation_importance_delta_auroc` — `rr_cv` 0,140, `peak_prob_mean` 0,032,
10 chỉ số còn lại < 0,002.

**GHI CHÚ NGƯỜI NÓI:** Nói thẳng: cổng này **không độc lập với mạng**. Trong 12 chỉ số, 6 thuần tín
hiệu (entropy mẫu, độ nhọn, entropy phổ…), 4 tính trên các nhịp chính mạng dò ra (biến thiên RR,
bSQI…), 2 là xác suất của mạng. Hai chỉ số gánh gần hết độ quan trọng là biến thiên RR và xác suất
trung bình tại đỉnh — cả hai đều đến từ mạng. Huấn luyện bỏ-một-chủ-thể nên không rò rỉ. Cổng 22 ca
này mới ở dạng phân tích, **chưa đưa vào demo**; đèn trong demo là cổng hiệu chuẩn trên mô hình 5 ca. Kết quả: nó xếp đúng ba bản ghi khó nhất vào ba hạng chót, xác suất ngẫu nhiên
là 1 trên 1540. Nhưng em phải tự khai một điều làm yếu kết quả này: em đã dựng 24 quy tắc chỉ
dùng **một** đặc trưng làm đối chứng, và 5 trong số đó cũng xếp đúng cả 3. Nên em **không** được
nói "phải có cổng học mới làm được". Còn một việc chưa xong: số cổng trên CinC hiện có đo trên 75
bản gồm 15 bản nhiễm, em đã rút và sẽ tính lại trên 60 bản sạch — có trong kế hoạch tuần 2.

---

## SLIDE 16

**TIÊU ĐỀ:** Kết quả âm tính — ba đòn bẩy không hiệu quả

**LOẠI:** biểu đồ + bảng

**NỘI DUNG CHÍNH:**
- Thích nghi miền: **cả bốn phương pháp đều thất bại**
- Dải lọc: +2,44 trên kênh PSD nhưng −0,07 trên trung bình 4 kênh
- Kiến trúc: ba họ đầu cách nhau dưới 0,1 điểm
- Ba dịch chuyển đo được chỉ giải thích 0,01 / 23,28 điểm
- Em **chưa** xác định được nguyên nhân khoảng cách ngoài miền

**HÌNH/BẢNG:** **BIỂU ĐỒ THANH CÓ THANH LỖI, ngang, quanh vạch 0.**
Bốn thanh, trục X là Δ F1 trên 60 bản sạch:
`chặn điện lưới +0,25 [−0,25; +1,08], p 0,68` · `tự huấn luyện nhãn giả −0,67 [−1,11; −0,29]` ·
`AdaBN −1,58 [−2,50; −0,73]` · `TENT −2,43 [−3,64; −1,35]`.
Nguồn bốn dòng: `analysis/THICHNGHI.md` và các JSON trong `adapt/` (`adapt_results.json`), trích
lại trong `docs/CHIEN_LUOC_CONG_BO.md` mục 1 dòng 6 và bản thảo trong `paper/` (thư mục giữ tên
cũ để truy vết lịch sử; nội dung đã đồng bộ về 60 bản sạch).
*Đã chốt 17/09:* tự huấn luyện **−0,67** (−0,6746) và p notch **0,68** (0,679, Wilcoxon ghép cặp, 8 hơn / 10 kém /
42 hoà) — tính lại từ `adapt/adapt_results.json → per_record_cinc` trên 60 bản sạch; mọi tài liệu dùng hai số này.
Ô chú thích bên phải: *Áp cả ba dịch chuyển đo được (60 s · lượng tử hoá · điện lưới 60 Hz) lên
22 chủ thể chỉ mất **0,01** điểm, trong khi khoảng cách trong/ngoài miền là **23,28** điểm theo PSD* — nguồn
`adapt/adapt_results.json → mo_phong_dich_chuyen.hieu_C3_tru_C0` = −0,0135; khoảng cách = 97,56
(`baselines/powermf_fair_stats.json → so_sanh.tat_ca_22.rely_vs_pmf4.mean_a`) − 74,28
(`analysis/dulieu_results.json → chon_kenh_60_sach.bang.psd.mean_60_sach`). **Không dùng**
`.khoang_cach_CinC_con_lai` = 17,92: nó tính từ mốc 79,40 trên 75 bản nhiễm, đã rút
(`survey/facts_phase4.json → Z_DA_RUT.khoang_cach_trong_ngoai_mien_17_92`).
Ô cảnh báo dưới cùng, viền đỏ: *Không kết luận được "vì không có tín hiệu": phép thử nhìn thấy có
âm tính giả **18,0 %** [12,1; 25,0] → nguyên nhân **chưa xác định**.* Nguồn
`analysis/xacnhan_results.json → viec4_phep_thu_nhin_thay` (`cinc60|psd`:
`ti_le_am_tinh_gia_micro` 0,1797, `ci95` [0,1213; 0,2497]).

**GHI CHÚ NGƯỜI NÓI:** Em chiếu slide này chứ không giấu, vì nó quyết định việc em **không** làm
nữa. Bốn phương pháp thích nghi miền không giám sát: chặn điện lưới thích nghi, tự huấn luyện
nhãn giả, AdaBN, TENT — không cái nào giúp, hai cái làm xấu đi rõ rệt. Rồi em thử theo hướng
ngược: đo ba khác biệt giữa hai bộ dữ liệu và **áp chúng lên** dữ liệu trong miền để xem mất bao
nhiêu — chỉ mất 0,01 điểm, trong khi khoảng cách thật là 23,28 theo quy tắc PSD. Nghĩa là ba dịch chuyển đó không
giải thích được gì. Điều em **phải** nói kèm: em từng viết rằng khoảng cách đó là do không có tín
hiệu để bắt — em đã rút, vì phép thử em dùng để nói "không nhìn thấy" có âm tính giả 18 %. Nguyên
nhân khoảng cách — 23,28 điểm theo PSD, còn 15,55 nếu dùng peakprob hậu kiểm — hiện vẫn để mở, và em thấy nói "chưa biết" đúng hơn là đoán.

---

## SLIDE 17

**TIÊU ĐỀ:** Và đây là phần em nghĩ quan trọng nhất

**LOẠI:** chuyển tiếp

**NỘI DUNG CHÍNH:**
- (chỉ một dòng chữ to, không bullet)

**HÌNH/BẢNG:** Slide trống, nền đậm, một câu duy nhất ở giữa cỡ 44–54 pt:
**"Và đây là phần em nghĩ quan trọng nhất: những chỗ em đã làm sai."**
Không hình, không số.

**GHI CHÚ NGƯỜI NÓI:** Dừng hẳn, 3–4 giây, nhìn cô rồi mới nói. "Phần từ đây đến hết em nghĩ là
thứ đáng nói nhất trong buổi hôm nay, vì nó cho thấy cách em làm việc chứ không phải con số em
đạt được." Nếu buổi đang chạy chậm so với giờ, đây là slide có thể nói ngắn nhất nhưng **không
được bỏ** — nó đặt khung cho slide 18–20.

---

## SLIDE 18

**TIÊU ĐỀ:** Sai lầm 1 và 2

**LOẠI:** nội dung

**NỘI DUNG CHÍNH:**
- **Sai lầm 1:** báo số CinC trên mẫu 10 bản chọn thuận tay
- Trong 10 bản đó có 4 bản chính là dữ liệu huấn luyện
- Đã rút toàn bộ; nay báo trên **60 bản sạch**
- **Sai lầm 2:** đoán nguyên nhân trước khi đo
- Power-MF chạy lại thấp hơn tác giả → em đoán sai nguyên nhân

**HÌNH/BẢNG:** Hai khối cạnh nhau, mỗi khối có nhãn "TRƯỚC → SAU".
Khối trái (sai lầm 1): `mẫu 10 bản, kênh cố định chọn hậu kiểm` → `60 bản sạch, kênh mù nhãn`;
dưới ghi: *5 con số của mẫu 10 bản đã rút — xem `survey/facts_phase4.json → Z_DA_RUT.cinc_mau_10`;
13 con số của 75 bản đã rút — `Z_DA_RUT.cinc_75_o_nhiem`.* **Không in các con số đã rút lên slide.**
Khối phải (sai lầm 2): `đoán: khác phiên bản thư viện` → `đo: hàm tìm đỉnh của Octave tràn bộ
nhớ` → `sau khi sửa: 99,40 vs 99,46`; dưới ghi: *4 con số Power-MF từ cổng chuyển hỏng đã rút —
`Z_DA_RUT.powermf_cong_chuyen_hong`.*

**GHI CHÚ NGƯỜI NÓI:** Sai lầm 1: lúc đầu em chỉ chạy 10 trên 75 bản CinC, và em chọn 10 bản đó
theo cách thuận tay, lại còn cố định kênh sau khi đã nhìn kết quả. Trong 10 bản đó có 4 bản chính
là dữ liệu em huấn luyện. Em rút toàn bộ nhánh đó và chạy lại đủ bộ.
Sai lầm 2: em chạy lại Power-MF bằng Octave vì không có MATLAB, kết quả thấp hơn tác giả vài
điểm. Em **đoán** nguyên nhân trước rồi mới đo, và đoán sai — thật ra là hàm tìm đỉnh trong cổng
chuyển của em tràn bộ nhớ. Sửa xong thì 99,40 so với 99,46 của tác giả. Bài học em rút: đo trước,
kết luận sau; và em áp quy tắc đó cho mọi thí nghiệm từ vòng 5 trở đi.

---

## SLIDE 19

**TIÊU ĐỀ:** Sai lầm 3, 4 và 5

**LOẠI:** nội dung

**NỘI DUNG CHÍNH:**
- **3:** tưởng chồng lấn set-a ↔ ADFECGDB là của mình
- Ban tổ chức đã ghi nhận từ 2013; ghi chú đọc bài của em có, em bỏ sót
- **4:** F1 chạm trần 100 che khuất khác biệt thật
- **5:** từng kết luận khoảng cách ngoài miền không thuộc mô hình → đã rút
- Cái em thật sự làm: **định danh 15 bản và đo mức thổi phồng**

**HÌNH/BẢNG:** **SƠ ĐỒ ÁNH XẠ 5 → 15** (hình chính của slide).
Cột trái 5 hộp: r01, r04, r07, r08, r10. Cột phải 15 hộp: a04 a05 a22 | a13 a20 a25 |
a19 a23 a24 | a08 a15 a17 | a03 a12 a14. Mũi tên nhóm 3 từ mỗi hộp trái, nhãn trên mũi tên ghi
cửa sổ `0–60 s / 120–180 s / 240–300 s`. Trên hình ghi: `NCC = 1,0000 · lệch RR = 0,0 ms`.
Nguồn: `analysis/dulieu_results.json → chong_lan.bang_chung` (từng bản: `ncc` 1,0,
`ban_ghi_goc`, `rr_median_abs_diff_ms` 0,0); kiểm độc lập lần hai
`analysis/dulieu_m4b_verify.json` (viết lại từ đầu, cùng 15 bản).
Hộp đối chứng bên phải: *đối chứng dương (trùng đã biết B2 ↔ PhysioNet, khác xử lý): NCC
0,856–0,984; 60 bản còn lại: tối đa 0,62* — nguồn `analysis/dulieu_results.json →
chong_lan.doi_chung_duong_tinh_ncc` và `survey/facts_phase4.json →
A_cinc2013_60_ban_sach.ncc_toi_da_60_ban_con_lai`.
Hộp trích dẫn dưới cùng: *Silva et al. CinC 2013;40:149-152 Bảng 1 "Abdominal and Direct FECG —
25"; Clifford et al. Physiol Meas 2014;35:1521, DOI 10.1088/0967-3334/35/8/1521 — cảnh báo nguyên
văn về một bài dự thi huấn luyện trên ADFECGDB.* Nguồn `survey/ro_ri_vanlieu.json → nguon`.
Hộp mức thổi phồng: *3,27 – 7,18 điểm F1* — nguồn `survey/facts_phase4.json →
A_cinc2013_60_ban_sach.thoi_phong_diem_F1`.

**GHI CHÚ NGƯỜI NÓI:** Đây là chỗ phải nói chính xác từng chữ, không được nói quá.
"Ban tổ chức CinC 2013 đã ghi nhận chuyện này từ 2013: Silva Bảng 1 ghi 25 bản lấy từ ADFECGDB;
Clifford 2014 còn cảnh báo nguyên văn về một nhóm huấn luyện trên ADFECGDB rồi kiểm trên set-a.
Em đã đọc bài đó, ghi chú đọc bài của chính em có nhắc, rồi em vẫn bỏ sót khi làm. Có một giai
đoạn em tưởng đó là của mình — em đã rút cách nói đó."
Cái mới của em chỉ là hai thứ: định danh bằng đo lường **đúng 15 bản nào** và đo **mức thổi
phồng** 3,27–7,18 điểm. Nói về bằng chứng: tương quan chuẩn hoá đúng 1,0000 cả bốn kênh đúng thứ
tự, lệch RR 0,0 ms, mỗi bản huấn luyện xuất hiện đúng 3 lần theo ba cửa sổ một phút. Em còn viết
lại phép kiểm từ đầu lần hai, độc lập, ra cùng 15 bản. Thêm: sai lầm 4 là F1 chạm trần 100 nên
che khuất khác biệt thật, em chuyển sang thang logit để kiểm; sai lầm 5 là em từng kết luận
khoảng cách ngoài miền không thuộc về mô hình — đã rút ở slide 16.

---

## SLIDE 20

**TIÊU ĐỀ:** Quy trình sửa: tám vòng phản biện

**LOẠI:** nội dung

**NỘI DUNG CHÍNH:**
- 8 vòng: mỗi vòng có một lượt phản biện đi tìm chỗ sai
- Mọi con số phải truy về một tệp JSON trên đĩa
- Một tệp nguồn sự thật duy nhất: `survey/facts_phase4.json`
- Mục `Z_DA_RUT` liệt kê **mọi** số đã rút, không xoá dấu vết
- Kết quả: 5 tuyên bố lớn tự rút, kể cả tuyên bố mình thích

**HÌNH/BẢNG:** Danh sách 5 dòng, mỗi dòng `Tuyên bố đã rút → thay bằng`, **không in con số đã rút**:

| Đã rút | Thay bằng |
|---|---|
| Mọi số CinC tính trên 75 bản | 60 bản sạch, `benchmark_dpss/eval_cinc60_sach.json` |
| Số Power-MF từ cổng chuyển hỏng | `baselines/powermf_fair_stats.json` |
| "Dải lọc cộng hơn mười điểm" cho mô hình | +2,44, KTC chạm 0 — `pilot_evidence/band_tcn_stats.json` |
| "Bảy/tám kiến trúc không phân biệt được" | TOST ở biên 1,0 điểm — `analysis/kientruc_results.json` |
| "Khoảng cách ngoài miền không thuộc mô hình" | chưa xác định — `analysis/xacnhan_results.json` |

Chân slide: *Danh sách đầy đủ: `survey/facts_phase4.json → Z_DA_RUT` và `README.md` mục
Retractions (17 dòng).*

**GHI CHÚ NGƯỜI NÓI:** Nói về cách làm việc, không khoe công cụ. "Em chạy tám vòng. Mỗi vòng em
cho một lượt phản biện đi tìm chỗ sai trong chính kết quả của em, rồi em đối chiếu từng con số
với tệp gốc trên đĩa. Mọi số trong mọi tài liệu phải truy về một tệp JSON; nếu không truy được
thì em bỏ số đó." Nếu cô hỏi em dùng công cụ gì: nói thật là em dùng công cụ tự động để đối chiếu
và để phản biện, và em tự chịu trách nhiệm về từng con số. Kết lại bằng một câu: "Em giữ lại cả
danh sách những gì em rút, không xoá, để ai đọc kho mã cũng thấy được."

---

## SLIDE 21

**TIÊU ĐỀ:** Định vị thật: nộp ở đâu

**LOẠI:** bảng

**NỘI DUNG CHÍNH:**
- Đích chính: **Physiological Measurement** — sân nhà của cộng đồng điện tim thai
- Xếp hạng Scimago 2024: **Q2** Physiology / Q3 Biomedical Eng.
- Q1 (JBHI/TBME/BSPC/CBM): rào cản là **dữ liệu có nhãn mới**
- Hội nghị đúng chuyên ngành: **Computing in Cardiology 2027**
- **Không** hội nghị A* nào thuộc lĩnh vực này

**HÌNH/BẢNG:** Bảng 5 dòng × 5 cột: *Nơi nộp | Loại | Xếp hạng (nguồn, năm) | Cửa hiện tại |
Rào cản*.

| Nơi nộp | Loại | Xếp hạng | Cửa | Rào cản |
|---|---|---|---:|---|
| Physiological Measurement | tạp chí | Scimago 2024: Q2 / Q3 | ~55 % | — (đích mặc định) |
| BSPC | tạp chí | Scimago: Q1 | ~35 % | đòi bảng so sánh rộng |
| Computers in Biology and Medicine | tạp chí | Scimago: Q1 | ~30 % | cạnh tranh đông |
| IEEE JBHI | tạp chí | Scimago: Q1 | 15–20 % / 6 tháng · ~35 % / 12 tháng | **cần bộ có nhãn mới** |
| Computing in Cardiology 2027 | hội nghị | không có trong CORE | ~80 % | hạn ~4/2027 |

Chân bảng, chữ nhỏ: *Cột "Cửa" là ước lượng chủ quan, **không phải số đo** — nguồn
`docs/CHIEN_LUOC_CONG_BO.md` mục 2.1, cột `P_nay` bản [V7] (sửa 17/09: trước ghi 58 / 32 / 12 / 32 %, không khớp nguồn). Xếp hạng Scimago lấy qua trang tổng hợp bên thứ ba, chưa
xác minh trực tiếp từ JCR. **Không có hội nghị A\* nào đúng lĩnh vực này**; MICCAI là A và không
nhận tín hiệu 1-D.*

**GHI CHÚ NGƯỜI NÓI:** Nói thẳng ngay câu đầu: "Physiological Measurement theo Scimago 2024 là Q2
Physiology và Q3 Biomedical Engineering, **không phải Q1**. Em nói trước để cô không bị bất ngờ."
Giải thích vì sao vẫn chọn nó: đó là nơi chính CinC Challenge 2013 công bố, ban biên tập quen với
bài kiểm toán và kết quả âm tính — đúng loại bài này. Cửa lên Q1 là JBHI, nhưng rào cản không
phải kỹ thuật mà là **dữ liệu**: cần một bộ có nhãn thật để chạy quy tắc chọn kênh đúng một lần.
Em ước cửa Q1 trong 6 tháng khoảng 15–20 %. Và em nói rõ: cột "Cửa" là em ước, không phải số đo.
Về A*: không có hội nghị A* nào đúng lĩnh vực, muốn A* là phải ra khỏi lĩnh vực và ở đó bài này
không cạnh tranh được — em xin không đặt mục tiêu đó.

---

## SLIDE 22

**TIÊU ĐỀ:** Tiến độ theo khối công việc

**LOẠI:** biểu đồ

**NỘI DUNG CHÍNH:**
- Nền tảng đã xong: dữ liệu, mô hình, đánh giá, demo
- Còn thiếu: hạt giống thứ 2–3, cổng trên 60 sạch, bản thảo
- Kiểm thử tự động chạy qua (17/09/2026: 109)
- Ảnh chụp demo dự phòng nếu máy hỏng
- Không khối nào bị chặn bởi kỹ thuật — chỉ bởi dữ liệu và thời gian

**HÌNH/BẢNG:** **BIỂU ĐỒ THANH TIẾN ĐỘ NGANG (progress bars), 8 thanh, trục X 0–100 %.**

| Khối công việc | % | Căn cứ |
|---|---:|---|
| Dữ liệu + kiểm toán chồng lấn | 100 | `analysis/dulieu_results.json`, `analysis/dulieu_m4b_verify.json` (2 cài đặt độc lập) |
| Mô hình + huấn luyện (1 hạt giống) | 100 | `analysis/kientruc_results.json`, checkpoint 11 fold |
| Đánh giá trong miền + baseline | 100 | `baselines/powermf_fair_stats.json`, `analysis/recovery_ratio.json` |
| Đánh giá ngoài miền, 60 bản sạch | 100 | `benchmark_dpss/eval_cinc60_sach.json` |
| Demo + kiểm thử | 100 | 109 kiểm thử (43 `tests/` + 66 `demo/test_core.py`, đếm 17/09/2026 sau lượt sửa demo thứ ba); ảnh trong `demo/screenshots/` |
| Cổng từ chối | 70 | xong trên 22 chủ thể; **chưa** tính lại trên 60 sạch |
| Lâm sàng (STV) | 60 | đo xong; **chưa** đo trên nhịp đã qua cổng |
| Ba hạt giống cho kết quả chính | 33 | mới có hạt giống 0; hạt giống 1 chỉ có F1, không có checkpoint |
| Bản thảo bài báo | 35 | dàn ý + tóm tắt + bản nháp hội nghị — `docs/CHIEN_LUOC_CONG_BO.md` mục 4 |

Chân slide, chữ nhỏ, **bắt buộc**: *Phần trăm là ước lượng của chủ nhiệm theo khối lượng còn lại,
**không phải số đo**. Cột "Căn cứ" ghi bằng chứng có thật trên đĩa.*

**GHI CHÚ NGƯỜI NÓI:** Nói ngay là cột phần trăm em tự ước, không phải số đo — chỉ cột "căn cứ"
là sự thật kiểm được. Ba thanh chưa đầy là ba việc em biết chính xác phải làm gì: tính lại số
cổng trên 60 bản sạch (rẻ, tuần 2), đo STV trên nhịp đã qua cổng (rẻ, tuần 3), và chạy thêm hai
hạt giống (tốn thời gian máy). Nhấn: không khối nào bị chặn vì em không biết làm — chỉ bị chặn vì
thiếu dữ liệu có nhãn và thiếu thời gian máy.

---

## SLIDE 23

**TIÊU ĐỀ:** Kế hoạch 12 tuần — năm mốc

**LOẠI:** bảng

**NỘI DUNG CHÍNH:**
- **Tuần 1–2:** cam kết git, tính lại cổng + phổ lỗi trên 60 sạch
- **Tuần 3–4:** dữ liệu thứ ba nếu có bác sĩ; STV sau cổng; **chốt đích**
- **Tuần 5–6:** hai hạt giống nữa; thí nghiệm SNR thấp có kiểm soát
- **Tuần 7–10:** rà văn liệu ảnh hưởng; viết bản thảo; phản biện nội bộ
- **Tuần 11–12:** kiểm số tự động; **nộp** đầu tháng 12/2026

**HÌNH/BẢNG:** Dải thời gian ngang (timeline) 12 tuần, 14/9 → 6/12/2026, gắn 5 mốc. Mỗi mốc một
hộp: tên mốc + đầu ra cụ thể. Đánh dấu điểm quyết định ở tuần 4 bằng hình thoi:
`có bộ có nhãn mới + kết quả thuận → JBHI; mọi trường hợp khác → Physiological Measurement`.
Nguồn: `docs/CHIEN_LUOC_CONG_BO.md` mục 5 (bảng 12 tuần đầy đủ). Ghi rõ ngày nộp mục tiêu:
**30/11 – 6/12/2026**; và `Computing in Cardiology 2027, hạn abstract dự kiến ~15/4/2027`.

**GHI CHÚ NGƯỜI NÓI:** Chỉ vào hình thoi tuần 4 và nói đó là điểm duy nhất kế hoạch rẽ nhánh, và
nó phụ thuộc vào việc cô có giúp được đầu mối khoa sản hay không. Nêu hai việc em **quyết định
dừng**: đổi kiến trúc (slide 9) và thích nghi miền không giám sát (slide 16) — vì đã đo thấy đòn
bẩy yếu, tiếp tục là phí thời gian. Nếu cô hỏi có kịp không: bản nháp hội nghị 4 trang đã có
khung, bản dài đã có dàn ý 9 mục và tóm tắt — phần nặng là hai hạt giống và rà văn liệu.

---

## SLIDE 24

**TIÊU ĐỀ:** Ba điều em xin cô

**LOẠI:** nội dung

**NỘI DUNG CHÍNH:**
- **1. Dữ liệu và một bác sĩ sản.** Đầu mối khoa sản đang ghi CTG hoặc điện tim bụng
- Đây là nút duy nhất em không tự gỡ được
- **2. Ý kiến về nơi nộp.** Physiological Measurement + CinC 2027 có hợp không
- **3. Euréka.** Hạn nội bộ TDTU kỳ 2026 em chưa xác minh — em sẽ hỏi Đoàn trường
- Em **không** xin cô duyệt kết quả hay sửa mã

**HÌNH/BẢNG:** Ba khối đánh số lớn, mỗi khối một dòng "cụ thể là gì" và một dòng "để làm gì".
Khối 1: *cụ thể — xin gặp một bác sĩ sản 30 phút, và hỏi xem có xin được dữ liệu có nhãn không;
để làm gì — không có việc này thì không lên Q1 được* (đối chiếu slide 10 và 21).
Khối 3: *thực tế là kỳ Euréka 2027; vòng bán kết ~60 %, chung cuộc ~5–8 % — ước lượng, chưa xác
minh với Đoàn trường.* Không số liệu JSON trên slide này.

**GHI CHÚ NGƯỜI NÓI:** Nói thứ tự ưu tiên rõ ràng, việc 1 quan trọng hơn hẳn hai việc kia. Với
việc 1: nếu khó xin dữ liệu thì phương án nhỏ hơn là em tự chú thích 10–20 bản của một bộ công
khai chưa có nhãn, rồi nhờ chuyên gia kiểm giúp — cái đó cũng đủ mở đường. Với việc 3: nói thật
là em chưa xác minh được hạn nội bộ kỳ 2026 và sẽ hỏi Đoàn trường trong tuần này, và em muốn hồ
sơ Euréka kể câu chuyện kiểm toán chứ không kể một con số F1. Kết: "Em không xin cô duyệt kết
quả, không xin cô sửa mã, không xin thêm thời gian."

---

## SLIDE 25

**TIÊU ĐỀ:** Demo — hệ thống chạy thật

**LOẠI:** chuyển tiếp

**NỘI DUNG CHÍNH:**
- Năm bản minh hoạ, trong đó có hai bản hệ thống **thất bại**
- r01 (F1 99,92) · a09 (hai quy tắc chọn kênh, 94,25 so 19,35)
- a02 (F1 24,91 — đèn đỏ, hệ thống từ chối) · a27 (32,94; cả bốn dây kém, F1 21,26–32,94; đèn đỏ 14/15 đoạn)
- Mọi bảng trong demo đọc trực tiếp từ tệp kết quả
- Bản mẫu nghiên cứu — **không phải thiết bị y tế**

**HÌNH/BẢNG:** Một ảnh chụp demo lớn (`demo/screenshots/01.png` — tab *Tín hiệu (5 tầng)* của
r01) làm nền mờ, chồng lên là 5 dòng nội dung. Ở góc: đường dẫn chạy `python demo/app.py` và
`http://127.0.0.1:7860`. Số F1 của 5 bản minh hoạ lấy từ `demo/results/demo_check_showcase.json`.
**Dự phòng:** nếu demo trực tiếp hỏng, chuyển sang 16 ảnh `demo/screenshots/01…12` theo thứ tự
01–03 (r01) → 04–06 (a09, hai quy tắc) → 07–08 (B2_03) → 09–10 (a02) → 11 (a27) → 12 (bảng tổng
hợp 60 bản sạch).

**GHI CHÚ NGƯỜI NÓI:** Trước khi chuyển màn hình, nói câu định khung: "Em cho cô xem cả chỗ nó
chạy tốt lẫn chỗ nó hỏng, và chỗ nó hỏng thì em muốn cô xem kỹ hơn." Thứ tự demo 4 phút theo
`docs/HUONG_DAN_DEMO_v1.md` mục 3 (bản 8 tab, lưu trữ; bản hiện hành `docs/HUONG_DAN_DEMO_v2.md`): r01 → a09 (đổi qua lại hai quy tắc chọn kênh) → a02 (đèn đỏ, từ
chối). Điểm cần nói ở a02: mô hình bám tàn dư tim mẹ, ra một chuỗi nhịp rất đều trông như thai,
F1 chỉ 24,91 — nhưng cổng bật đỏ và hệ thống từ chối trả lời. Câu cuối bắt buộc: "Đây là bản mẫu
nghiên cứu, không phải thiết bị y tế — em ghi câu đó ngay đầu trang demo."

---

## SLIDE 26

**TIÊU ĐỀ:** Đóng lại

**LOẠI:** số lớn / kết

**NỘI DUNG CHÍNH:**
- Em không làm ra bộ dò tốt nhất — em làm ra một phép đo có ranh giới
- Một kênh lấy lại **89,5 %** lợi ích của bốn kênh
- Có **cổng báo** lúc không đáng tin — cổng dựa một phần vào mạng
- Mọi con số báo trên dữ liệu sạch; mọi số sai đều được rút công khai
- Cái em cần tiếp theo là **dữ liệu có nhãn** để xác nhận quy tắc chọn kênh và tìm nguyên nhân khoảng cách ngoài miền (chưa xác định là do mô hình hay dữ liệu)

**HÌNH/BẢNG:** Nền sạch. Dòng 2 và 3 làm đậm. Không bảng, không biểu đồ. Góc dưới:
`github.com/bminhnemhoi/nckhsv_tdtu2026-2027` · `survey/facts_phase4.json` ·
"Bản mẫu nghiên cứu, không phải thiết bị y tế".

**GHI CHÚ NGƯỜI NÓI:** Nói chậm, đây là câu cô sẽ nhớ. "Em không làm ra bộ dò tốt nhất, và em
không định nói vậy. Em làm ra một phép đo có ranh giới rõ: một kênh lấy lại 89,5 % lợi ích của
bốn kênh, và hệ thống có một cổng báo khi nó không đáng tin — cổng đó dựa một phần vào chính mạng, nên
em chưa nói nó độc lập." Rồi câu cuối, nhìn thẳng:
"Thứ em cần tiếp theo không phải là mô hình tốt hơn, mà là dữ liệu có nhãn — và đó là chỗ em cần
cô." Dừng, mời cô hỏi.

---
---

# BA LỰA CHỌN MÀU SẮC VÀ PHÔNG CHỮ

Cả ba đều tránh gradient, tránh bóng đổ, tránh biểu tượng trang trí. Tiếng Việt có dấu nên phông
**bắt buộc** phải đủ bộ dấu (Inter, Source Sans 3, IBM Plex Sans, Lora, Be Vietnam Pro đều đủ;
tránh các phông thiếu dấu như Futura hay Gill Sans).

### Lựa chọn A — "Lâm sàng" (khuyên dùng cho buổi này)

| | |
|---|---|
| Nền | trắng ngà `#FCFCFA` |
| Chữ chính | than `#1A1A1A` |
| Chữ phụ / chú thích | xám `#6B6B6B` |
| Màu nhấn (kết quả dương) | xanh mực `#1B4D7E` |
| Màu cảnh báo (số đã rút, hạn chế) | đỏ gạch `#A03323` |
| Màu trung tính trong biểu đồ | xám nhạt `#C9C9C4` |
| Phông tiêu đề | **Source Sans 3** SemiBold, 32–40 pt |
| Phông nội dung | **Source Sans 3** Regular, 20–24 pt |
| Phông số lớn | **Source Sans 3** Bold, 100–150 pt, dùng chữ số dạng bảng (tabular) |

*Vì sao:* trung tính, đọc được từ cuối phòng, và màu đỏ chỉ xuất hiện đúng ở chỗ cảnh báo nên nó
có sức nặng. Đây là bảng màu an toàn nhất cho một buổi báo cáo có nhiều hạn chế phải nêu.

### Lựa chọn B — "Giấy nghiên cứu"

| | |
|---|---|
| Nền | kem `#F7F4ED` |
| Chữ chính | nâu đen `#2B2622` |
| Màu nhấn | xanh rêu `#3F6B5A` |
| Màu cảnh báo | cam đất `#B5651D` |
| Phông tiêu đề | **Lora** SemiBold (có chân), 30–38 pt |
| Phông nội dung | **IBM Plex Sans** Regular, 20–24 pt |
| Phông số/bảng | **IBM Plex Mono** Medium |

*Vì sao:* tiêu đề có chân tạo cảm giác học thuật; phông mono cho bảng làm các cột số thẳng hàng,
rất hợp với slide 9, 14 và 22. Rủi ro: nền kem có thể ám vàng trên máy chiếu cũ.

### Lựa chọn C — "Tối tương phản cao"

| | |
|---|---|
| Nền | xanh đen `#10161C` |
| Chữ chính | trắng ngà `#F2F2EF` |
| Chữ phụ | xám xanh `#93A1AD` |
| Màu nhấn | xanh sáng `#5AA9E6` |
| Màu cảnh báo | hổ phách `#E8A33D` |
| Phông | **Inter** (Bold cho tiêu đề, Regular cho nội dung) |

*Vì sao:* tốt nếu phòng tối và máy chiếu yếu; slide 17 (chuyển tiếp) và slide 13 (số lớn) rất
mạnh trên nền tối. Rủi ro: các bảng nhiều dòng (slide 14, 21, 22) khó đọc hơn, và nếu in ra giấy
thì tốn mực — mà buổi này có phát tờ tóm tắt in giấy.

### Quy tắc chung cho cả ba

1. Một slide một ý. Nếu phải thu nhỏ chữ xuống dưới 18 pt thì cắt nội dung, không thu chữ.
2. Trong mọi biểu đồ: kết quả dương dùng màu nhấn, mọi thứ khác dùng xám. Không quá **hai** màu
   có nghĩa trên một hình.
3. Mọi biểu đồ có khoảng tin cậy **phải** vẽ thanh lỗi; không vẽ cột trơn cho số có khoảng.
4. Trục Y bị cắt (không bắt đầu từ 0) thì phải ghi rõ trên trục — slide 9 và 12 đều bị cắt.
5. Số trên slide dùng dấu phẩy thập phân theo tiếng Việt (97,56) và dấu chấm phân nhóm nghìn
   (113.481) — thống nhất toàn bộ.
6. Mỗi slide có kết quả đo: một dòng chân slide 11–12 pt ghi tên tệp JSON nguồn.

---

# NHỮNG GÌ KHÔNG NÊN ĐƯA LÊN SLIDE

### 1. Mọi con số đã rút — tuyệt đối không in

- Năm con số CinC của mẫu 10 bản (`Z_DA_RUT.cinc_mau_10`).
- Mười ba con số CinC tính trên 75 bản, gồm cả số chọn kênh và số Power-MF một kênh
  (`Z_DA_RUT.cinc_75_o_nhiem`).
- Bốn con số Power-MF từ cổng chuyển Octave hỏng (`Z_DA_RUT.powermf_cong_chuyen_hong`).
- Con số dải lọc "+11,00" phát biểu như thuộc tính của mô hình (`Z_DA_RUT.dai_loc_gbm_...`).
- Số cổng từ chối zero-shot trên CinC (AUROC 0,980 / độ phủ 66,7 % / 15 trong 16) — đo trên 75
  bản gồm 15 bản nhiễm, **chưa** tính lại trên 60 sạch.
- Ở slide 18 và 20 chỉ ghi *"đã rút"* và tên tệp; nếu cô hỏi con số cũ là bao nhiêu thì đọc
  miệng kèm câu "con số này đã rút, em nói để cô đối chiếu lịch sử".

### 2. Mọi cụm từ trong danh sách cấm

`SOTA` · `novel` · `first` / `đầu tiên` · `state-of-the-art` / `tốt nhất hiện nay` ·
`tiền đăng ký` / `pre-registered` · `phát hiện rò rỉ` / `chúng tôi phát hiện` (về chồng lấn) ·
`mô hình không phải nút thắt` · `lưỡng cực` (dùng như đặc tính của bài toán) ·
`thiếu tín hiệu thật` (dùng như kết luận) · `Physiological Measurement là Q1` ·
`CinC 2026` (như đích nộp — kỳ đó đã diễn ra). Nguồn danh sách:
`survey/facts_phase4.json → Z_DA_RUT.cum_tu`.
Thay thế đúng: "khai báo trước **phép tính**" thay cho "tiền đăng ký"; "như ban tổ chức đã ghi
nhận [Silva 2013; Clifford 2014], chúng tôi định danh bằng đo lường 15 bản và mức thổi phồng"
thay cho "chúng tôi phát hiện"; "chưa xác định nguyên nhân" thay cho "thiếu tín hiệu thật".

### 3. Chi tiết kỹ thuật quá sâu — để dành cho phần hỏi đáp

- Siêu tham số huấn luyện (learning rate, batch size, số bước, ngưỡng từng fold).
- Cấu hình từng khối giãn nở, số kênh mỗi tầng, kích thước nhân.
- Công thức khử mẹ (tỉ lệ bình phương tối thiểu từng nhịp) — chỉ nói tên bước ở slide 7.
- Bảng phổ lỗi 6 nhóm đầy đủ. Nếu cần nói, chỉ nói **một** con số của 22 chủ thể: *"lỗi loại bỏ
  nhịp dù tín hiệu nhìn thấy được chỉ chiếm 3,8 %, trong khi mức ngẫu nhiên là 14,7 %"*
  (`analysis/chandoan_results.json → pho_loi.22_chu_the_kenh_PSD.pct_null`; số 15,2 % từng ghi ở đây là mức ngẫu nhiên của hàng `peakprob`, không cùng hàng với 3,8 % của PSD —
  `m1_bo_sung.pho_loi_theo_quy_tac`) — và **không** trích con số tương ứng trên CinC vì nó
  đo trên 75 bản, chưa tính lại trên 60 sạch.
- Jitter 3,76 ms và bảng jitter theo phân tầng F1 — chỉ nói nếu cô hỏi về độ chính xác thời điểm.
- Chi tiết lưới siêu tham số của bốn phương pháp thích nghi miền.

### 4. Đường dẫn tệp và lệnh chạy

Không in đường dẫn tuyệt đối (`D:/NCKHSV2026-2027/...`) lên slide. Tên tệp JSON chỉ xuất hiện ở
**chân slide, cỡ 11–12 pt**, dạng tương đối (`analysis/dulieu_results.json`). Lệnh chạy chỉ xuất
hiện ở slide 25.

### 5. Thông tin không kiểm được

- Impact factor của bất kỳ tạp chí nào (mọi IF trong hồ sơ đều lấy qua trang tổng hợp bên thứ ba,
  chưa xác minh từ JCR) — slide 21 chỉ in quartile Scimago kèm năm.
- Hạn nội bộ Euréka kỳ 2026 của TDTU (chưa xác minh) — chỉ nói miệng là "em sẽ hỏi Đoàn trường".
- Tỉ lệ nhận của Euréka — nếu in thì phải ghi "ước lượng, chưa xác minh".
- Số sản phụ thật trong 60 bản CinC sạch: **không biết**, nhiều nhất 60, có thể ít hơn
  (`survey/ro_ri_vanlieu.json → kiem_cheo_ky_thuat.cung_san_phu_khac_buoi`; NIFECGDB góp 14 bản từ một sản phụ vào cuộc thi nhưng chưa định danh được trong set-a). Không in "60 sản phụ".

### 6. Hai cách nói sai thường gặp — không được dùng dù chỉ một lần

- **"Một kênh hơn bốn kênh."** Sai: −1,27 điểm. Nói đúng: "một kênh lấy lại 89,5 % lợi ích của
  bốn kênh, và chênh lệch còn lại chưa phân biệt được về thống kê".
- **"peakprob là kết quả."** Sai: đó là lựa chọn hậu kiểm. Nói đúng: "quy tắc kế hoạch chọn là gate,
  80,72, trượt Holm; gate4 81,01 cùng họ ghi trước sống sót Holm nhưng không phải quy tắc kế hoạch chọn;
  peakprob là giả thuyết mạnh chưa xác nhận".
- **"Cổng dùng chỉ số cổ điển, không lấy từ mạng."** Sai: 2/12 chỉ số là xác suất mạng, 4/12 tính trên
  nhịp mạng dò. Nói đúng: "cổng không độc lập với mạng".

---

*Tệp này do chủ nhiệm dùng để dựng bộ slide. Mọi con số đã đối chiếu với tệp JSON trên đĩa ngày
13/09/2026. Nếu bất kỳ tệp nguồn nào thay đổi, kiểm lại trước khi dựng slide.*
