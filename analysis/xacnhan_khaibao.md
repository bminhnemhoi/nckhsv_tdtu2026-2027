# KHAI BÁO TRƯỚC — R2: xác nhận peakprob trên bộ thứ ba + tính lại 22 chủ thể trên logit

Ngày khai báo: 2026-09-12. Tệp này được ghi và cam kết git **trước** khi chạy bất kỳ phép tính mới nào
của R2. Mọi con số dưới đây đã có sẵn trên đĩa từ các vòng trước (chonkenh_results.json,
dulieu_results.json, chandoan_raw.json, train_22_seed1.json); chưa có con số nào của R2 được tính.

## 0. Những gì tôi ĐÃ nhìn thấy trước khi khai báo (để minh bạch)
- Bảng F1 thô 22 chủ thể theo 7 quy tắc (chonkenh_results.json, `bang.s22`): gate 98,61 > rrcv 98,60 >
  gate4 98,58 > rrplaus 98,57 > fuse 98,43 > peakprob 98,22 > learned 97,62 > psd 97,56.
- Bảng 60 bản CinC sạch (dulieu_results.json): peakprob 82,01 > gate4 81,01 > gate 80,72 > psd 74,28.
- Độ nhạy phép thử nhìn thấy trên nhịp TP: 0,951 (22) / 0,862 (CinC 75).
Tôi CHƯA tính logit, CHƯA tính tỉ lệ âm tính giả theo bản ghi, CHƯA so seed.

## 1. Bộ dữ liệu thứ ba có nhãn fQRS thật — kết quả kiểm tra (VIỆC 2, đã kiểm TRƯỚC khi khai báo)
| Bộ | Trên đĩa | Nhãn fQRS thật? | Bằng chứng |
|---|---|---|---|
| NIFEADB (Behar 2019) | 26 bản .dat/.hea | **KHÔNG** | thư mục PhysioNet 1.0.0 không có .qrs/.atr/ANNOTATORS (model/nifeadb_loader.py, `HAS_FETAL_ANNOTATIONS=False`) |
| NInFEA (Sulas 2021) | 2,5 bản ghi tải dở | **KHÔNG** | không có tệp chú thích nhịp; tham chiếu gốc là Doppler, không phải fQRS |
| nifecgdb (ecgca*) | 1 bản thăm dò ecgca102 | **KHÔNG** (nhãn mẹ) | .qrs: 375 nhịp/270 s, RR trung vị 0,695 s = 86 nhịp/phút → QRS mẹ; 55 bản đều từ MỘT sản phụ |
| CinC 2013 set-b | không tải | **KHÔNG** | nhãn không công bố |
| ADFECGDB, Silesia B1/B2 | có | có | đã dùng huấn luyện → không phải bộ thứ ba |
**Kết luận trước khi chạy: KHÔNG có bộ thứ ba có nhãn fQRS thật.** VIỆC 2 sẽ không chạy mô hình
trên bất kỳ bộ nào; báo cáo thẳng. VIỆC 3 và VIỆC 4 là việc chính.

## 2. VIỆC 3 — tính lại 22 chủ thể trên thang logit
- Dữ liệu: `chonkenh_results.json` → `F1_tung_ban_ghi.s22` (22 chủ thể × 16 cột), n nhịp tham chiếu
  mỗi chủ thể lấy từ `analysis/chonkenh_cache/s22_*.json` (`n_ref`). KHÔNG chạy suy luận mới.
- Quy tắc so: psd (mốc), gate (quy tắc đã chỉ định trước), peakprob (lựa chọn hậu kiểm), và 4 quy tắc
  mới còn lại (gate4, rrcv, rrplaus, fuse, learned) để Holm trên đúng 7 quy tắc như vòng trước.
- Biến đổi: y = logit(p), p = F1/100. Kẹp F1 = 100 theo HAI cách, báo cáo cả hai:
  - Kẹp A (chính): p' = (p·n + 0,5)/(n + 1), n = số nhịp tham chiếu của chủ thể (kẹp Laplace theo cỡ mẫu).
  - Kẹp B (độ nhạy): p' = min(p, 0,999) (trần 99,9).
  - Kẹp C (độ nhạy thứ hai): p' = min(p, 0,995) (trần 99,5).
- Chỉ số: logit trung bình theo quy tắc; hiệu vs psd; KTC95 bootstrap theo chủ thể (10 000 lần, seed 0);
  Wilcoxon ghép cặp (zero_method='wilcox'); Holm trên 7 quy tắc mới; thắng/hoà/thua.
- Câu hỏi then chốt và ngưỡng quyết định (ghi TRƯỚC):
  - Q1: quy tắc nào có logit trung bình cao nhất trong 7 quy tắc mới, theo kẹp A? Báo cáo thêm B, C.
  - Q2: "vấn đề hậu kiểm biến mất" CHỈ khi peakprob đứng đầu theo CẢ BA cách kẹp VÀ KTC95 (peakprob − psd)
    trên logit không chứa 0. Nếu thiếu bất kỳ điều kiện nào → vấn đề hậu kiểm KHÔNG biến mất, nói thẳng.
  - Thứ hạng khác nhau giữa các cách kẹp → kết luận là "phụ thuộc cách kẹp", không chọn cách có lợi.
- Cảnh báo tự khai: đây CŨNG là một phép thử hậu kiểm (thang đo được đổi sau khi biết kết quả thô).
  Kết quả sẽ được báo cáo bất kể chiều. Phụ: chạy cùng phép trên 60 bản CinC sạch để mô tả, không quyết định.

## 3. VIỆC 4 — tỉ lệ âm tính giả của phép thử nhìn thấy
- Phép thử (analysis/chandoan.py::visibility): z = biên độ đỉnh dư ±30 ms / MAD khối 4 s; τ = phân vị 95
  của z tại vị trí "an toàn" (cách nhãn ≥120 ms, đỉnh mẹ ≥80 ms). Độ đặc hiệu 95% tại vị trí an toàn là
  THEO ĐỊNH NGHĨA (trong mẫu). Chỗ hở phản biện nêu: bao nhiêu nhịp thật ra nhìn thấy được lại bị gán
  "không nhìn thấy" = tỉ lệ âm tính giả (1 − độ nhạy), hiện chỉ có số gộp.
- Dữ liệu: `analysis/chandoan_events.npz` (z từng nhãn, τ, phát hiện, đỉnh mẹ, cho 97 bản × 4 kênh) và
  `analysis/chandoan_raw.json`. KHÔNG chạy suy luận mới.
- Sẽ tính:
  (a) Tỉ lệ âm tính giả trên nhịp TP (ghép ±50 ms, tham lam 1-1), theo kênh psd và kênh oracle, micro và
      macro (trung vị theo bản ghi), riêng 22 chủ thể và 60 bản CinC sạch (loại 15 bản sao chép), KTC95
      bootstrap theo bản ghi. Phân tầng theo F1 bản ghi (≥90 / 50–90 / <50).
  (b) Kiểm tra trần độ đặc hiệu ngoài mẫu trên 3 bản có phần dư lưu sẵn (chandoan_cache.npz): lấy mẫu MỚI
      vị trí an toàn, đo tỉ lệ z ≥ τ (kỳ vọng 5%).
  (c) Tính lại phép chia dư địa "không nhìn thấy / có nhìn thấy" trên 60 bản sạch (không dùng nhóm 8 bản
      giới hạn cứng): dư địa = (100 − F1_oracle)/60 mỗi bản; phân nhóm theo tỉ lệ nhãn nhìn thấy trên kênh
      tốt nhất, ngưỡng 0,5, dùng cả tỉ lệ THÔ và tỉ lệ HIỆU CHỈNH v' = (v − 0,05)/(s − 0,05) với s = độ nhạy
      đo trên TP của chính bản ghi (kẹp [0,1]); quét thêm ngưỡng 0,3 và 0,7.
- Ngưỡng quyết định (ghi TRƯỚC): nếu tỉ lệ âm tính giả micro trên 60 bản sạch > 10% thì con số "71% dư địa
  nằm trên bản không có tín hiệu" PHẢI được thay bằng con số hiệu chỉnh. Nếu sau hiệu chỉnh phần dư địa
  trên bản "không nhìn thấy" < 50% thì kết luận "mô hình không phải nút thắt" không còn chỗ đứng và phải rút.
- Giới hạn tự khai: độ nhạy đo trên TP là ước lượng LẠC QUAN (TP là nhịp dễ); tỉ lệ âm tính giả trên nhịp
  FN thật sự có tín hiệu không đo được vì không có nhãn "có tín hiệu" độc lập.

## 4. VIỆC 5 — hạt giống
- Checkpoint seed 1 KHÔNG được lưu (train_22.py chỉ lưu khi `--tag` rỗng; model/checkpoints/ không có tệp
  seed 1). Vì cấm huấn luyện lại, peakprob với seed 1 trên 60 bản sạch là BẤT KHẢ THI trong R2.
- Sẽ làm phần khả thi: từ `model/train_22_seed1.json` (per_lead F1 22 chủ thể, seed 1) và `model/train_22.json`
  (seed 0): F1 psd, mean4, oracle theo chủ thể; hiệu seed1 − seed0, KTC95 bootstrap; số chủ thể lệch > 1 điểm.
- Ngưỡng: |hiệu trung bình psd| ≤ 1 điểm và KTC chứa 0 → "ổn định theo seed ở mức chủ thể"; ngược lại nói rõ.

## 5. Tài nguyên và đầu ra
- OPENBLAS/OMP/MKL_NUM_THREADS = 1; chỉ đọc tệp có sẵn, không huấn luyện, không suy luận mới (trừ mục 3b
  dùng phần dư đã lưu sẵn). Đầu ra: analysis/xacnhan.py, analysis/xacnhan_results.json, analysis/XACNHAN.md,
  analysis/fig_xacnhan.png. Mỗi con số trong XACNHAN.md truy về xacnhan_results.json.
