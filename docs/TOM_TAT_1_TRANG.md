# RelyFetal — phát hiện nhịp tim thai từ một điện cực bụng mẹ, có cổng từ chối

Ngô Bình Minh · NCKH sinh viên TDTU 2026–2027 · bản 12/09/2026 · mọi số truy ngược được về tệp trong kho mã (ghi trong ngoặc)

**Bài toán.** Thai chậm phát triển là nguyên nhân hàng đầu của thai lưu; dấu hiệu sớm là nhịp tim thai mất biến thiên. Muốn đo biến thiên phải biết từng nhịp rơi vào mili-giây nào. Siêu âm Doppler không đủ chính xác thời điểm; điện cực da đầu chính xác nhưng xâm lấn. Điện tim bụng mẹ là lối ra, nhưng các hệ hiện có cần 4–32 điện cực trong phòng khám.

**Câu hỏi.** Nếu chỉ có **một** dây (để sau này thành miếng dán mẹ tự đeo) thì mất bao nhiêu so với bốn kênh — và hệ thống có tự biết lúc nào nó không nhìn thấy tín hiệu để từ chối trả lời không?

**Hệ thống.** Lọc 10–60 Hz pha-không → khử điện tim mẹ (mẫu trung vị, co giãn từng nhịp) → chọn kênh mù nhãn → mạng tích chập thời gian FetalQRS-TCN (113.481 tham số, 0,48 MB, 4,35 ms cho mỗi 4 s trên CPU) cho đường xác suất từng mẫu → cổng từ chối từ 12 chỉ số chất lượng tín hiệu cổ điển, không dùng nhãn. Demo web chạy cục bộ và API đã có; ≈27.700 dòng mã, 56 hàm kiểm thử (39 tests/ + 17 demo/).

**Kết quả chính (F1 mức chủ thể, ghép ±50 ms).**

| | Power-MF 4 kênh (chạy lại, kiểm chứng ngoài 99,40 vs 99,46 tác giả công bố) | Power-MF 1 kênh | RelyFetal 1 kênh |
|---|---|---|---|
| 22 sản phụ trong miền | 98,83 | 86,71 | **97,56** |

- Bốn kênh đáng giá 12,12 điểm cho chính Power-MF; một kênh lấy lại 10,85 = **89,5 %** [81,4; 103,2]. Trung bình vẫn **thua 1,27** điểm; thắng 18/22 bản, trung vị +0,23 (`baselines/powermf_fair_stats.json`).
- CinC 2013, **60 bản ghi sạch** chưa từng thấy (đã loại 15 bản là bản sao dữ liệu huấn luyện): chọn kênh cũ 74,28 → chọn kênh mới 82,01, **+7,73** [+3,82; +12,41], không bản nào mất quá 3,90 điểm (`analysis/dulieu_results.json`).
- Cổng từ chối, zero-shot trên CinC: AUROC mức bản ghi 0,980 (đo trên 75 bản gồm 15 bản nhiễm — chưa tính lại trên 60 sạch); giữ 66,7 % bản ghi thì loại 15/16 bản (75 bản, gồm bản nhiễm) có F1 < 50 (`analysis/gate22_cinc.json`).

**Ba đóng góp, mỗi cái kèm ranh giới.**
1. Phép đo "một kênh lấy lại bao nhiêu phần của bốn kênh" trên cùng bản ghi, cùng bộ chấm — *là phép đo, không phải phát minh.*
2. F1 trần 100 che hiệu ứng thật: trên 19 sản phụ dễ, một kênh hơn bốn kênh trên thang logit (+1,20, p = 0,0012) mà F1 thô báo "hoà" — *giả thuyết mạnh hơn về "hai nhóm (chia hậu kiểm)" đã bị chính đối chứng bác một phần.*
3. Cổng từ chối xếp đúng 3 bản khó nhất vào 3 hạng chót trong 22 (1/1540) — *5/24 quy tắc một đặc trưng cũng làm được, nên không nói "phải học mới được".*

**Những gì đã tự rút lại.** Dải lọc "+11 điểm" (đo lại trên đúng mô hình: gần 0); "đơn kênh hơn đa kênh" (sai); mọi số CinC trên 75 bản (nhiễm 15 bản); phép thử xác nhận ghi trước cho quy tắc chọn kênh **đã trượt** (gate, p Holm 0,051) — quy tắc thắng là chọn sau khi nhìn kết quả, nên được gọi là *giả thuyết mạnh chưa xác nhận*. Chỉ số lâm sàng STV lệch +0,33 ms trong miền nhưng +20,50 ms trên CinC: chưa dùng được làm máy đo độc lập (`analysis/clinical_results.json`).

**Giới hạn.** 22 chủ thể (tự tính cần ~50); 77 % thời lượng huấn luyện có nhãn gián tiếp; chưa có trung tâm ghi thứ hai; chưa có bác sĩ đồng hành; kết quả chính 1 hạt giống.

**Kế hoạch 3 tháng.** (1) Chạy quy tắc chọn kênh đúng một lần trên CinC set-b hoặc NInFEA, quy tắc chốt trước, báo cáo bất kể kết quả. (2) 3 hạt giống. (3) Tính lại nhánh 22 chủ thể trên logit. (4) Nộp CinC 2027 (bản 4 trang đã có), rồi bản dài. **Dừng:** đổi kiến trúc (7 họ cùng tham số cách nhau < 1 điểm) và thích nghi miền (4 phương pháp đều hỏng).

**Xin cô.** (1) Một đầu mối bác sĩ sản / khoa sản đang ghi CTG hoặc điện tim bụng. (2) Ý kiến về nơi nộp (CinC 2027; Physiological Measurement). (3) Ý kiến về Euréka 2027, lĩnh vực Công nghệ thông tin.

Kho mã: github.com/bminhnemhoi/nckhsv_tdtu2026-2027 · Demo: `python demo/app.py` · Bản mẫu nghiên cứu, không phải thiết bị y tế.
