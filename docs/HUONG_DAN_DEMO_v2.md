# Hướng dẫn demo RelyFetal — v2: chế độ trình bày (kể chuyện 5 bước)

**Thay cho `HUONG_DAN_DEMO_v1.md` (bản 8 tab, 13/09/2026).** Bản này viết cho người **xem** hiểu ngay và người
**trình bày** nói được mà không cần nhớ tên tab. Bản v1 giữ làm lưu trữ; khi hai bản khác nhau, theo bản này.

> **Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.**
> Mọi con số ở đây truy ngược được về một tệp trên đĩa (ghi ở Phụ lục). Không có kết quả nào tính trên 75 bản CinC;
> số chính là **60 bản sạch**.

Cập nhật: 17/09/2026, khớp demo **sau lượt sửa thứ ba (kiểm demo độc lập lần hai)** (`demo/app.py` sửa lần cuối 21:55,
`demo/core.py` và `fsqi/gate.py` 21:50, ảnh `demo/screenshots/17..23` chụp 22:01–22:02). Quy ước trong tài liệu này:

* Chữ nghiêng = **chuỗi giao diện**, chép từ `demo/app.py`, `demo/core.py` hoặc `fsqi/gate.py`. Dấu `…` là chỗ demo điền số của bản ghi.
  Mọi chuỗi nghiêng đã được đối chiếu tự động với mã và với chuỗi hiển thị thật của bốn thẻ (Phụ lục B).
* Ngoặc kép thường = **lời thoại** của người trình bày hoặc câu hỏi của người xem, không phải chữ trên màn hình.

Mục lục: [1. Mở thế nào](#1-mở-thế-nào) · [2. Kịch bản 5 phút](#2-kịch-bản-5-phút) ·
[3. Bốn thẻ là dữ liệu gì](#3-bốn-thẻ-là-dữ-liệu-gì) · [4. Cách đọc hình và đèn tin cậy](#4-cách-đọc-hình-và-đèn-tin-cậy)
(4.2 đèn xanh/vàng/đỏ nghĩa là gì · 4.3 vì sao gate 80,72 không được gọi là thắng · 4.4 vì sao đèn xanh mà vẫn sai, a57 ·
4.5 vì sao lúc chạy nhanh, lúc chậm) ·
[5. Chế độ chuyên gia](#5-chế-độ-chuyên-gia) · [6. Dữ liệu của nhóm và dữ liệu mới](#6-dữ-liệu-của-nhóm-và-dữ-liệu-mới) ·
[7. Dự phòng](#7-dự-phòng) · [Phụ lục A](#phụ-lục-a--truy-nguồn-con-số) · [Phụ lục B](#phụ-lục-b--đối-chiếu-chuỗi-giao-diện)

---

## 1. Mở thế nào

Mở **Windows PowerShell** tại gốc dự án, gõ đúng bốn dòng:

```powershell
cd D:\NCKHSV2026-2027
$env:PYTHONIOENCODING = "utf-8"
$env:OPENBLAS_NUM_THREADS = "1"; $env:OMP_NUM_THREADS = "1"; $env:MKL_NUM_THREADS = "1"
python demo/app.py
```

Mở trình duyệt tại **http://127.0.0.1:7860**. Cổng bận thì đặt `$env:RELYFETAL_PORT = "7870"` rồi chạy lại, mở cổng 7870.
Demo đọc biến `RELYFETAL_PORT`, **không** đọc `GRADIO_SERVER_PORT`.

Màn hình gồm các phần sau, từ trên xuống. Tiêu đề mục hiện bằng chữ in hoa.

| Phần | Thấy gì | Làm gì |
|---|---|---|
| Tiêu đề | *RelyFetal — tìm nhịp tim thai trong điện tim đo trên bụng mẹ, chỉ cần một kênh*. Dòng dưới: *Bản ghi thử có 4 kênh (4 "dây"). Máy chạy trên cả 4, tự chọn một kênh để đọc, tách nhịp bé khỏi nhịp mẹ, và báo "tôi không chắc" khi thấy dấu hiệu tín hiệu xấu (không phải lần nào cũng thấy).* kèm dòng đỏ *Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.* | Đọc to dòng dưới nếu người xem hỏi "một kênh mà sao có bốn dây" |
| *1 · Chọn một bản ghi (bấm thẻ là chạy ngay)* | Năm thẻ cao bằng nhau. Mỗi thẻ có **tên ca chữ to** và **mã bản ghi chữ nhỏ**: *Ca dễ* (*bản ghi r01 · ADFECGDB*) · *Chọn dây quyết định* (*bản ghi a09 · CinC 2013*) · *Máy bám nhầm tim mẹ* (*bản ghi a02 · CinC 2013*) · *Bốn dây đều kém* (*bản ghi a27 · CinC 2013*) · *Tệp của bạn* | Bấm thẻ bản ghi là chạy ngay, không có nút Phân tích riêng. Dòng cuối mỗi thẻ: *▶ Bấm để chạy (khoảng 5–10 giây)*. Thẻ *Tệp của bạn* ghi *▶ Mở phần tải tệp* (mục 6.3) |
| Dòng trạng thái ngay dưới hàng thẻ | Trong lúc chạy: *⏳ Đang phân tích bản ghi a02 (Máy bám nhầm tim mẹ) — khoảng 5–10 giây. Xong thì hình bên dưới tự đổi; chờ xong rồi hãy bấm "Tiếp ▶".* Nếu lỗi, dòng này chuyển nền đỏ: *Không phân tích được bản ghi …: … Hình bên dưới vẫn là bản ghi trước — bấm lại thẻ hoặc chọn thẻ khác.* | Chờ dòng này biến mất **và** ô *Bản ghi* ở thanh tóm tắt đổi sang đúng bản vừa bấm. Xong thì trang **tự cuộn** tới thanh 5 bước, trừ khi thanh đó đã nằm ở nửa trên màn hình. Lỡ bấm hai thẻ liền nhau: chỉ **thẻ bấm sau cùng** được vẽ; lượt cũ tính xong nhưng không vẽ, nên có thể phải chờ lâu hơn (mục 4.5) |
| *2 · Đi theo 5 bước* | Dòng gợi ý *Bấm "Tiếp ▶" để sang bước sau; khi cần, trang tự cuộn tới thanh 5 bước. Bấm thẻ khác ở trên để đổi bản ghi.* Thanh 5 bước, nút *◀ Quay lại* và *Tiếp ▶*. Mỗi lúc chỉ hiện một bước | Bấm *Tiếp ▶*: trang tự cuộn tới thanh 5 bước nếu thanh đó chưa nằm ở nửa trên màn hình. Nếu người xem đã bật chế độ chuyên gia và cuộn đi chỗ khác trong lúc chờ, trang **không** kéo họ về. Ở bước 5 nút đổi thành *Xem lại từ đầu ↺* |
| **Thanh tóm tắt** | **Dính đáy màn hình** suốt khi xem 5 bước, trên màn hình rộng hơn 700 px; hẹp từ 700 px trở xuống thì nằm yên cuối các bước. Cuộn xuống chế độ chuyên gia thì thôi dính. 6 ô: *Bản ghi* · *Bộ dữ liệu* · *Dây đã chọn* · *F1 (bắt đủ và báo đúng, 100 là hoàn hảo)* · *Nhịp tim thai trung bình* · *Đèn tin cậy*. Dòng dưới: F1 trung bình trên 60 bản ngoài miền theo năm cách chọn dây (mục 4) | Nhìn khi bị hỏi "kết quả là gì" |
| Ô tick cuối trang, mặc định TẮT | *Chế độ chuyên gia — hiện 8 tab đầy đủ (bảng số, dữ liệu của nhóm, tải tệp, nhật ký)* | Chỉ bật khi bị hỏi sâu (mục 5) |

Mở trang xong, thẻ **r01 tự chạy**, dòng trạng thái ghi *⏳ Đang mở sẵn bản ghi r01 (Ca dễ) — khoảng 5–10 giây.*
Lần đầu phải nạp mô hình nên lâu hơn các lần sau (bảng thời gian ở mục 2.5). Chân trang Gradio (`Use via API`,
`Built with Gradio`, `Settings`) đã ẩn.

**Kiểm trước buổi** (số kiểm thử đếm bằng `pytest --collect-only` ngày 17/09/2026 sau lượt sửa thứ ba; thời gian chạy chưa đo lại):

```powershell
python demo/smoke_app.py                              # dòng cuối bắt đầu bằng: KẾT QUẢ: ĐẠT
python -m pytest demo/test_core.py -k trinh_bay -q    # 22 kiểm thử của chế độ trình bày
python -m pytest tests/ demo/test_core.py -q          # toàn bộ: 109 kiểm thử (43 trong tests/ + 66 trong demo/test_core.py)
```

Tầng `[5]` của smoke là chế độ trình bày: bấm thẻ ra 33 đầu ra (phần tử cuối là dòng trạng thái, rỗng khi chạy xong) và về bước 1.

---

## 2. Kịch bản 5 phút

Nguyên tắc: **một thẻ, một câu chuyện, một ý.** Mỗi bước nói 1–2 câu rồi bấm *Tiếp ▶*. Câu ngắn.
Không đọc số trên hình. Số cần nói đã nằm trong hộp *Con số cần nhớ* ở mỗi bước.

### 2.1. Thẻ *Ca dễ* (r01) — 1 phút

Thẻ này tự chạy khi mở trang. Nếu không, bấm thẻ *Ca dễ*.
Thẻ ghi: *sản phụ chuyển dạ; đáp án từ điện cực trên da đầu bé; mô hình chưa từng thấy sản phụ này* ·
*Hệ thống tìm đúng gần như mọi nhịp* · số lớn *F1 99,92* · dòng nhỏ *F1 100 = không sót, không báo nhầm nhịp nào*.

| Bước | Bấm | Nói |
|---|---|---|
| 1 | — | "Đây là điện tim ghi ở bụng mẹ, dây 4. Ở dây này gai của bé to ngang gai của mẹ. Gai dày, đều, nhanh hơn là tim bé, khoảng 129 nhịp một phút. Gai thưa hơn là tim mẹ." |
| 2 | *Tiếp ▶* | "Máy tìm từng nhịp mẹ, vạch đỏ, rồi trừ đi. Hàng dưới là phần còn lại; vạch đen chấm là nhịp thai theo đáp án. Còn gai lớn trùng vạch đỏ thì đó là tim mẹ chưa trừ hết." |
| 3 | *Tiếp ▶* | "Đường tím là mức tin của mạng. Vượt vạch cam thì tính là một nhịp; vạch tím đậm là nhịp mạng đã báo, chưa biết đúng hay sai. Hàng dưới mới so với đáp án: chấm xanh lá là đúng." |
| 4 | *Tiếp ▶* | "Mỗi dây cho một tín hiệu khác nhau. Bản này dễ: cách chọn mới và cách chọn cũ cùng chọn dây 4. Dây nào cũng cho F1 từ 99,84 trở lên." |
| 5 | *Tiếp ▶* | "F1 99,92, đèn xanh: cả 75 đoạn 4 giây đều xanh. Ở bản này đáp án xác nhận máy đúng." |

Ở bước 1, hộp *Cách đọc hình* của r01 ghi *Ở dây này gai của bé to ngang gai của mẹ: gai dày, đều, nhanh hơn (≈ 129 nhịp/phút) là tim bé; gai thưa hơn (≈ 83 nhịp/phút) là tim mẹ.*
Không nói "gai lớn là tim mẹ, tim bé nhỏ hơn nhiều" ở thẻ này: trên dây 4 của r01 điều đó sai (mục 4, bước 1).

Ở bước 4, điểm tin của bốn dây trùng nhau khi làm tròn ba chữ số, nên demo in bốn chữ số, ví dụ
*Dây 4 — ĐƯỢC CHỌN · điểm tin của mạng 0,9982 · F1 99,92*. Hộp số ghi
*Bốn dây gần như ngang điểm (chênh dưới 0,001); dây nào cũng cho F1 từ 99,84 trở lên.*

### 2.2. Thẻ *Chọn dây quyết định* (a09) — 1 phút 30, điểm chính của đề tài

Bấm thẻ *Chọn dây quyết định*. Thẻ ghi *Cùng một bản ghi, đổi cách chọn dây thì kết quả đổi hẳn*, số lớn
*19,35 → 94,25*, dòng nhỏ *F1 khi chọn dây theo cách cũ → cách mới*. Bước 1–3 lướt nhanh, dừng lâu ở **bước 4**.

| Bước | Nói |
|---|---|
| 1 | "Bản này thuộc bộ CinC 2013, không trùng dữ liệu huấn luyện. Ban tổ chức không công bố thiết bị ghi của từng bản. Ở dây này gai lớn đều đặn là tim mẹ; gai của bé nhỏ hơn nhiều." |
| 2 | "Vẫn quy trình đó: tìm tim mẹ, trừ đi." |
| 3 | "Mạng vẫn tìm được nhịp. Giờ xem nó chọn dây nào." |
| **4** | "Cùng một sản phụ, mỗi dây cho một tín hiệu khác nhau." <br>"Cách chọn cũ, lấy dây có năng lượng mạnh nhất ở dải nhịp tim thai như Power-MF, chọn dây 2: F1 19,35. Cách chọn mới, lấy dây mà mạng tự tin nhất, chọn dây 1: F1 94,25." <br>"Máy chọn mà **không nhìn đáp án**. Số F1 trên mỗi hàng chỉ chấm sau khi đã chọn." |
| 5 | "F1 94,25, đèn xanh." <br>Chỉ dòng dưới thanh tóm tắt: "Trên 60 bản ngoài miền: cách cũ 74,28. Cách em chọn trong kế hoạch trước khi chạy là gate, 80,72, và nó không qua hiệu chỉnh thống kê. gate4, cũng ghi trước khi chạy, 81,01. Cách demo đang dùng 82,01, nhưng em chọn nó sau khi xem kết quả. Trần, nếu biết trước dây tốt nhất, 83,60." <br>"a09 là bản em chọn để minh hoạ, không đại diện cho trung bình." |

Nếu bị hỏi "cách chọn mới có phải ghi trước khi chạy không":
> "Có trong danh sách ghi trước khi chạy, nhưng em chọn nó làm mặc định **sau khi** xem kết quả CinC, nên là hậu kiểm.
> Quy tắc kế hoạch chọn là gate: 80,72, p Holm 0,051, không đạt. gate4, cũng ghi trước khi chạy, đạt: p Holm 0,015.
> Nhưng gate4 không phải quy tắc kế hoạch chọn." Chi tiết: mục 4.3.

Bảng đầy đủ nằm ở tab *Kết quả tổng hợp (60 bản sạch)* trong chế độ chuyên gia.

### 2.3. Thẻ *Máy bám nhầm tim mẹ* (a02) — 1 phút 30

Bấm thẻ *Máy bám nhầm tim mẹ*. Thẻ ghi: *78 % nhịp máy báo trùng nhịp mẹ. Máy báo nhịp tim 130: trông bình thường, nhưng đáp án ≈ 160.*
Số lớn *F1 24,91 · đèn ĐỎ*, dòng nhỏ *kết quả sai, và máy tự báo đỏ*.
Nhìn thanh tóm tắt trước: đèn *THẤP (đỏ)*; ô nhịp tim bị gạch ngang, kèm chữ *đèn đỏ: không dùng số này*.

| Bước | Hộp *Con số cần nhớ* trên màn hình | Nói |
|---|---|---|
| 1 | *Tim mẹ ≈ 124 nhịp/phút. Theo đáp án, tim bé ≈ 160 nhịp/phút; máy đếm được ≈ 130, không tin được (xem bước 5).* | "Tim mẹ khoảng 124. Theo đáp án, tim bé khoảng 160. Máy đếm được 130, và chính máy ghi là không tin được." |
| 2 | *Tìm được 124 nhịp mẹ trong 60 giây (≈ 124 nhịp/phút) và trừ chúng đi.* | "Máy tìm được 124 nhịp mẹ và trừ đi. Vạch đen chấm là nhịp thai theo đáp án." |
| 3 | *Mạng báo 129 nhịp "thai", nhưng 78 % trùng thời điểm nhịp mẹ: mạng đang bám nhầm tim mẹ. Chỉ đỉnh vượt ngưỡng 0,75 mới được tính.* | "Mạng báo 129 nhịp. Nhưng 78 phần trăm trùng thời điểm nhịp mẹ: mạng đang bám nhầm tim mẹ. Hàng dưới có nhiều dấu ✕ đỏ là báo dư, tam giác cam là bỏ sót." |
| **4** | *Cả hai cách cùng chọn dây 2 (F1 24,91).* Phía trên hình có hộp vàng *Lưu ý trung thực — chọn chưa đúng dây* | Chỉ vào hộp vàng. <br>"Dây 1 đạt F1 75,88. Nhưng hệ thống chọn dây 2, F1 chỉ 24,91." <br>"Nhóm so bảy cách chọn dây không nhìn đáp án. Sáu cách chọn dây 2, kể cả cách cũ, gate và gate4. Cách thứ bảy chọn dây 3. Không cách nào chọn dây 1." <br>"Đây là giới hạn thật. Lúc chọn, máy không có đáp án. Và mạng tin ở dây 2 hơn dây 1 một chút: 0,970 so với 0,963." |
| **5** | *F1 24,91 · đèn THẤP (đỏ) · 0 đoạn xanh, 9 vàng, 6 đỏ trên 15 đoạn 4 giây · 78 % nhịp "thai" trùng nhịp mẹ · máy báo 130 nhịp/phút nhưng theo đáp án ≈ 160.* | "Máy báo nhịp tim 130, nằm trong vùng bình thường. Nhưng đáp án khoảng 160." <br>"Đèn đỏ bật theo hai đường. Một: 6 trên 15 đoạn bị chấm đỏ, tức 40 phần trăm, quá mức 30. Hai: 78 phần trăm nhịp máy tìm trùng nhịp mẹ, quá mức 60." <br>"Hình ghi *TB 130 nhịp/phút (đèn đỏ: không dùng)*. Thanh tóm tắt gạch số 130. Máy không đưa con số sai cho người đọc." |

Không mở *Chi tiết kỹ thuật*. Không nói "dây nào cũng vậy" hay "không dây nào cứu được": sai, dây 1 đạt 75,88.

**Nếu bị hỏi "sao không chọn dây 1?" — trả lời trong 30 giây:**
> "Vì lúc chọn, máy không có đáp án, chỉ có tín hiệu. Ở dây 2 mạng tin hơn một chút, 0,970 so với 0,963. Cách cũ theo
> năng lượng dải nhịp thai cũng chọn dây 2. Sáu trên bảy cách chọn không nhìn đáp án chọn dây 2, không cách nào chọn
> dây 1. Luôn lấy dây 1 thì đúng ở bản này, nhưng trên 60 bản chỉ được 61,78, thấp hơn cả cách cũ 74,28. Trong 60 bản,
> a02 là bản dây được chọn kém dây tốt nhất nhiều nhất, gần 51 điểm F1. Chọn dây thất bại ở đây. Nhưng đèn đỏ đã chặn con số sai."

Nếu còn thời gian, thêm một câu: "Thiết bị thật chỉ có một dây thì không có dây 1 để chọn."
Bản dài 60 giây: `docs/KICH_BAN_THUYET_TRINH_v2.md` mục A3-bis.

### 2.4. Thẻ *Bốn dây đều kém* (a27) — 45 giây

Bấm thẻ *Bốn dây đều kém*. Thẻ ghi: *F1 từng dây chỉ 21,26–32,94. Hệ thống từ chối 14/15 đoạn thay vì đoán.*
Số lớn *F1 32,94 · đèn ĐỎ*, dòng nhỏ *thấp, và máy báo đỏ thay vì đoán bừa*. Bấm *Tiếp ▶* đến bước 4.

| Bước | Trên màn hình | Nói |
|---|---|---|
| 4 | *Hai cách chọn khác dây, nhưng kết quả gần như nhau.* | "Bốn dây đều kém: F1 từ 21,26 đến 32,94. Cách mới chọn dây 3, cách cũ chọn dây 4: 32,94 so với 30,23, gần như nhau." |
| 5 | *0/15 đoạn xanh · 1 vàng · 14 đỏ (từ chối trả lời)* | "F1 32,94, đèn đỏ. 14 trên 15 đoạn bị từ chối. Ô nhịp tim bị gạch: máy không đưa ra một con số trông như thật." |

**Không nói** "bản này không có tín hiệu thai". Nhóm chưa đo điều đó. Nếu bị hỏi vì sao a27 kém, nói:
"Em chưa có kết luận về nguyên nhân. Bản này chỉ cho thấy máy phản ứng thế nào khi cả bốn dây đều kém."

### 2.5. Kết (15 giây) và thời gian máy chạy

Chỉ vào thanh tóm tắt:
> "Tách nhịp bé khỏi nhịp mẹ, tự chọn dây, tự báo đỏ khi đáng ngờ. Chọn dây chưa phải lúc nào cũng đúng, như a02.
> Đèn cũng còn phải kiểm thêm."

**Thời gian đo bằng trình duyệt tự động** (`python demo/screenshot_v2.py`, 17/09/2026, lần chạy ghi tệp lúc 22:02; Chromium
không giao diện, 1366×768, vẽ đồ thị bằng phần mềm, không dùng GPU). Mở trang đến khi r01 sẵn: **7,2 s**.

> ⚠ Đây là **một lần đo**, không phải phép đo hiệu năng chuẩn; nhóm không ghi lại lúc đó máy có chạy việc khác hay không,
> và tệp `screenshots_v2.json` bị ghi đè mỗi lần chụp lại. **Không dùng các số này để kết luận demo nhanh hay chậm.**
> Chữ *khoảng 5–10 giây* trên thẻ và ở dòng trạng thái là ước lượng ghi trong mã, không phải số đo của
> lần này. Vì sao lúc nhanh lúc chậm: mục 4.5.

| Thẻ | Bấm thẻ → bước 1 hiện | Sang bước 2 · 3 · 4 · 5 | Đi hết 5 bước |
|---|---:|---|---:|
| r01 (300 s) | 6,95 s | 2,55 · 2,91 · 4,55 · 0,90 s | 18,22 s |
| a09 (60 s) | 2,77 s | 1,63 · 1,73 · 2,23 · 1,09 s | 10,03 s |
| a02 (60 s) | 3,48 s | 1,72 · 1,82 · 2,05 · 1,08 s | 10,93 s |
| a27 (60 s) | 3,40 s | 1,62 · 1,78 · 2,10 · 1,41 s | 10,52 s |

Chuyển bước không tính toán lại, chỉ hiện hình đã vẽ. Trình duyệt thật có GPU thường vẽ nhanh hơn, nhưng nhóm chưa đo.

---

## 3. Bốn thẻ là dữ liệu gì

| Thẻ (tên ca · mã) | Bộ dữ liệu | Dòng mô tả trên thẻ | Đáp án (nhãn) từ đâu | Thẻ cho thấy gì (chữ đậm trên thẻ) | Số trên thẻ |
|---|---|---|---|---|---|
| *Ca dễ* · r01 | ADFECGDB (PhysioNet), 1000 Hz, 300 s, 4 dây bụng | *sản phụ chuyển dạ; đáp án từ điện cực trên da đầu bé; mô hình chưa từng thấy sản phụ này* | Điện cực gắn trên da đầu bé: nhãn **trực tiếp** | *Hệ thống tìm đúng gần như mọi nhịp* | *F1 99,92* |
| *Chọn dây quyết định* · a09 | CinC 2013 set-a, 1000 Hz, 60 s, 4 dây | *bộ CinC 2013, không trùng dữ liệu huấn luyện (ngoài miền); nguồn thiết bị từng bản không được công bố* | Người chấm độc lập của ban tổ chức | *Cùng một bản ghi, đổi cách chọn dây thì kết quả đổi hẳn* | *19,35 → 94,25* |
| *Máy bám nhầm tim mẹ* · a02 | CinC 2013 set-a | như a09 | Người chấm độc lập | *78 % nhịp máy báo trùng nhịp mẹ. Máy báo nhịp tim 130: trông bình thường, nhưng đáp án ≈ 160.* | *F1 24,91 · đèn ĐỎ* |
| *Bốn dây đều kém* · a27 | CinC 2013 set-a | như a09 | Người chấm độc lập | *F1 từng dây chỉ 21,26–32,94. Hệ thống từ chối 14/15 đoạn thay vì đoán.* | *F1 32,94 · đèn ĐỎ* |
| *Tệp của bạn* | *dữ liệu mới · .edf · .dat + .hea · .csv · .npy · .txt* | *bản ghi điện tim bụng mẹ mà nhóm chưa từng dùng* | Tệp nhãn tuỳ chọn (mục 6.3) | *Chạy đúng quy trình như bốn thẻ bên cạnh* | *Thử dữ liệu mới* · *không cần đáp án; có đáp án thì chấm thêm được F1* |

"Mô hình chưa từng thấy sản phụ này" ở thẻ r01 nghĩa là demo dùng checkpoint fold **không chứa** r01 (22 chủ thể,
để-một-người-ra). Ba bản CinC đều thuộc **60 bản sạch**, không nằm trong 15 bản trùng dữ liệu huấn luyện. Đó là điều
kiện để gọi chúng là "ngoài miền". B2_03 (Silesia chuyển dạ, F1 83,91, đèn đỏ) không lên thẻ nhưng vẫn có trong chế độ chuyên gia.

Dòng mô tả của ba thẻ CinC không còn ghi "máy ghi khác, nơi khác": nhóm chỉ kiểm được là không trùng dữ liệu huấn luyện;
thiết bị ghi của từng bản ban tổ chức không công bố, nên không nói như sự kiện.
Số trên thẻ và chữ đèn trên thẻ a02, a27 (*đèn ĐỎ*) đọc từ tệp JSON lúc mở demo, không ghi cứng. Thẻ nào chưa có dữ liệu sẽ mờ đi và ghi
*⚠ chưa có trên đĩa — xem hướng dẫn tải dữ liệu*. Cách tải: `HANDOFF.md` mục 4.

---

## 4. Cách đọc hình và đèn tin cậy

Mỗi bước có một khung chú thích đầu bước (chữ *Bước* kèm số và tên bước, rồi một câu giải thích), một hình, và **hai hộp** dưới hình:
*Con số cần nhớ* (xanh dương, tính từ chính bản ghi đang xem) và *Cách đọc hình* (vàng). Người trình bày chỉ cần đọc hai
hộp. Phần dưới đây để trả lời câu hỏi. Mọi hình: kéo chuột để phóng to, nhấp đúp để xem toàn bộ.

**Bước 1 — *Tín hiệu thô từ bụng mẹ*.** Chú thích: *Tín hiệu trên bụng mẹ chứa cả tim mẹ lẫn tim bé. Tim mẹ thường nổi trội; tim bé có bản ghi thấy rõ, có bản ghi lẫn hẳn trong nhiễu.*
Tiêu đề hình *Tín hiệu thô trên bụng mẹ, dây …*: 10 giây đầu của dây đã chọn. Trục dọc ghi *biên độ*, không in số vì
đơn vị khác nhau giữa các máy ghi. Hộp số ghi nhịp mẹ và nhịp bé đo trên chính bản ghi. Khi đèn đỏ và có đáp án, hộp
số **không** đưa nhịp máy đếm ra như sự thật mà ghi *Theo đáp án, tim bé ≈ … nhịp/phút; máy đếm được ≈ …, không tin được (xem bước 5).*

Hộp *Cách đọc hình* của bước 1 **không** nói chung chung "gai lớn là tim mẹ". Demo đo trên chính bản ghi (10 giây đầu,
tín hiệu đã lọc) tỉ số biên độ gai bé / gai mẹ, dùng vị trí nhịp bé theo đáp án:
* Tỉ số từ 0,5 trở lên (r01, dây 4): *Ở dây này gai của bé to ngang gai của mẹ: gai dày, đều, nhanh hơn (≈ … nhịp/phút) là tim bé; gai thưa hơn (≈ … nhịp/phút) là tim mẹ.*
* Tỉ số dưới 0,5 (a09, a02, a27): *Ở dây này gai lớn đều đặn là tim mẹ; gai của bé nhỏ hơn nhiều, lẫn trong nhiễu.*
* Bản không có đáp án (ví dụ tệp tải lên không kèm nhãn): *Thường thì gai lớn đều đặn là tim mẹ, nhưng có dây gai của bé to ngang gai mẹ; bản ghi này không có đáp án để phân biệt.*

Nếu bị hỏi "sao không thấy tim bé" ở a09, a02, a27: "Đúng, ở những dây này tim bé nhỏ và lẫn trong nhiễu, đó là lý do phải có mô hình."

**Bước 2 — *Lọc và khử tim mẹ*.** Chú thích: *Lọc nhiễu, tìm từng nhịp mẹ rồi trừ đi. Phần còn lại là nơi tìm tim bé; nếu còn gai lớn trùng vạch đỏ (nhịp mẹ) thì đó là dấu vết tim mẹ chưa trừ hết.*
Hàng trên *Đã lọc nhiễu — vạch đỏ: … nhịp tim mẹ*: tín hiệu đã lọc dải 10–60 Hz và chặn điện lưới 50 Hz. Hàng dưới
*Sau khi trừ tim mẹ — phần còn lại* *(vạch đen chấm: nhịp thai theo đáp án)*: đã trừ nhịp mẹ bằng mẫu trung vị của chính
bản ghi. Đọc: hai hàng chung trục thời gian; ở hàng dưới còn gai lớn nằm đúng vị trí vạch đỏ của hàng trên thì tim mẹ
chưa trừ hết; vạch đen chấm là chỗ nhịp bé thật nằm.

**Bước 3 — *Mô hình tìm nhịp thai*.** Chú thích: *Đường tím là mức tin của mạng; vạch tím đậm là nhịp mạng đã báo, chưa biết đúng hay sai. Hàng dưới mới so với đáp án.*
Hàng trên *Mức tin của mạng — vạch tím đậm: nhịp mạng đã báo, vạch cam: ngưỡng*: đường tím là mức tin từ 0 đến 1
(chú giải *mức tin của mạng*); vạch cam ngang là ngưỡng 0,75, cố định, lưu trong checkpoint, không chỉnh theo bản ghi;
vạch tím đậm (chú giải *nhịp mạng đã báo*) và chấm cùng màu (chú giải *đỉnh vượt ngưỡng*) là chỗ mạng báo có nhịp.
Màu xanh lá **chỉ** dùng cho "đúng" ở hàng dưới, nên hàng trên không còn vạch xanh lá. Hàng dưới
*So với đáp án: ● đúng, ✕ dư, ▲ sót*, chú giải *đúng: …* · *báo dư: …* · *bỏ sót: …*. Bản không có đáp án thì hàng dưới
chỉ ghi *… nhịp thai đã phát hiện*.

**Bước 4 — *Chọn đúng dây nào*.** Chú thích: *Cùng một sản phụ, mỗi dây cho một tín hiệu khác nhau. Hệ thống tự chọn một dây MÀ KHÔNG NHÌN ĐÁP ÁN — thường chọn đúng, không phải lúc nào cũng đúng.*

Phía trên hình có một đoạn chữ nói hai cách chọn dây nào:
*Cách chọn mới (peakprob: dây mà mạng tự tin nhất) chọn dây … → F1 …. Cách chọn cũ (PSD: dây có năng lượng mạnh nhất ở dải nhịp tim thai 1,8–3 Hz, như Power-MF) chọn dây … → F1 ….*
rồi một trong ba câu: *Hai cách chọn cùng một dây.* · *Hai cách chọn khác dây, và kết quả khác hẳn.* (chênh từ 10 điểm F1) ·
*Hai cách chọn khác dây, nhưng kết quả gần như nhau.*

Mỗi hàng của hình là một dây, tiêu đề hàng dạng *Dây 2 — ĐƯỢC CHỌN · điểm tin của mạng 0,970 · F1 24,91*. Hàng được chọn
vẽ màu xanh dương trên nền xanh nhạt. Chú giải: *nhịp máy tìm*, *nhịp thai theo đáp án*. *Điểm tin của mạng* là mức mạng
tin vào các nhịp nó tìm thấy trên dây đó; cách chọn mới lấy dây có điểm cao nhất. F1 chỉ chấm **sau** khi đã chọn,
không tham gia chọn. Khi điểm các dây trùng nhau ở ba chữ số (r01), demo in bốn chữ số (mục 2.1).

Nếu dây được chọn kém dây tốt nhất theo đáp án từ **10 điểm F1** trở lên, hiện hộp vàng *Lưu ý trung thực — chọn chưa đúng dây*.
Trong bốn thẻ, chỉ a02 hiện hộp này, nguyên văn:
*Dây 1 đạt F1 75,88, nhưng hệ thống chọn dây 2 (F1 24,91). 6/7 cách chọn dây không nhìn đáp án mà nhóm đã so cũng chọn dây 2. Không cách nào chọn dây 1. Chọn dây mà không nhìn đáp án thì không phải lúc nào cũng đúng; thiết bị thật chỉ có một dây thì không có dây khác để chọn.*
Bảy cách được đếm: psd, gate, gate4, rrcv, peakprob, rrplaus, learned. Sáu cách đầu chọn dây 2; learned chọn dây 3
(F1 19,86). fuse không tính vì gộp nhiều dây; lead0 và oracle là mốc tham chiếu.

**Bước 5 — *Kết quả và độ tin cậy*.** Chú thích: *Mỗi đoạn 4 giây có một đèn: xanh là cổng không thấy dấu hiệu xấu, vàng là chưa chắc, đỏ là hệ thống từ chối trả lời. Xanh không bảo đảm là đúng: trong 82 bản đã chấm có 3 bản đèn xanh mà F1 dưới 90, thấp nhất 17,02. Cả bản ghi bị đèn đỏ khi quá 30 % số đoạn đỏ, hoặc khi máy bám nhịp mẹ; lúc đó mọi con số của bản ghi, kể cả nhịp tim, đều không được dùng.*

Ba số 82 · 3 · 17,02 trong câu chú thích demo đọc từ `demo/results/demo_check_2modes.json` lúc mở trang, không ghi cứng
(thiếu tệp thì câu chỉ còn *Xanh không bảo đảm là đúng.*). Bản F1 17,02 là a57: mục 4.4.

* Hình trên *Nhịp tim thai theo thời gian (mỗi điểm là một cửa sổ 4 giây)*: chú giải *Theo đáp án* (đường chấm đen) và
  *Hệ thống (mỗi 4 giây)* (đường xanh dương), trục *nhịp/phút*, dải xanh lá nhạt *vùng bình thường 110–160 nhịp/phút*
  (đã hiện trên hình, xem ảnh `22_a02_buoc5.png`), đường gạch *trung bình … nhịp/phút*. Khi đèn đỏ, chữ đó rút thành
  *TB* và thêm *(đèn đỏ: không dùng)*, ví dụ a02: *TB 130 nhịp/phút (đèn đỏ: không dùng)*; a27: *TB 126 nhịp/phút (đèn đỏ: không dùng)*.
* Hình dưới *Mức đáng ngờ của từng đoạn 4 giây — cột càng cao càng đáng ngờ; nền đỏ = đoạn hệ thống từ chối trả lời*.
  Cột xanh, vàng, đỏ theo hai vạch *xanh < 0,052* và *đỏ > 0,540*. Góc phải ghi số đoạn, ví dụ a02:
  *0/15 đoạn xanh · 9 vàng · 6 đỏ (từ chối trả lời)*. Đoạn đỏ tô nền đỏ trên cả hai hình.
* Dòng chữ nhỏ dưới hai hộp, nguyên văn:
  *Đèn trong bản demo này dùng cổng hiệu chuẩn trên mô hình 5 sản phụ. Ghép với mô hình đó, trong cùng một bản ghi cổng xếp đoạn xấu trên đoạn tốt ở mức AUROC 0,721 (đo trên 5 bản CinC); ghép với mô hình 22 sản phụ đang chạy thì chưa đo lại. Cổng dùng cả xác suất của mạng nên không độc lập với mạng. Cổng hiệu chuẩn trên 22 sản phụ mới có ở dạng phân tích, chưa đưa vào demo.*
* Mục thu gọn, **đóng sẵn**: *Chi tiết kỹ thuật — lý do của đèn, điểm từng dây, bảng chấm, thời gian xử lý*.
  Bên trong: *Vì sao đèn … (điểm … / 1)* và các lý do, dòng đầu là *Bộ phân loại GBM (12 chỉ số của đoạn: 6 thuần tín hiệu, 4 tính trên nhịp mạng tìm ra, 2 là xác suất của mạng; huấn luyện trên ADFECGDB): …*,
  dòng hai ghi ngưỡng *xanh < …, đỏ > …* bằng ba chữ số (0,052 và 0,540), dấu % cách số (*… % đoạn đỏ*); bảng *Dây* · *Điểm tin của mạng (quy tắc mới)* · *F1 theo đáp án* ·
  *Nhịp tim (nhịp/phút)*; dòng thời gian *Xử lý dây đã chọn: …*; bảng chấm với đáp án (dung sai ±50 ms): *Độ nhạy (tìm được bao nhiêu nhịp thật)*,
  *Độ chính xác (bao nhiêu nhịp báo là thật)*, F1, *Lệch thời điểm TB*, *Đúng* / *Báo dư* / *Bỏ sót*. Chỉ mở khi bị hỏi.

**Thanh tóm tắt.** Sáu ô, viền đổi màu theo đèn. Ô *Dây đã chọn* ghi dạng *2 / 4 (quy tắc mới)*. Khi đèn đỏ, ô
*Nhịp tim thai trung bình* bị gạch ngang, kèm chữ *đèn đỏ: không dùng số này*. Dòng dưới cùng, nguyên văn:
*Trên 60 bản ghi ngoài miền, F1 trung bình theo cách chọn dây: cách cũ (PSD) 74,28 · cách kế hoạch đã chọn trước khi chạy (gate) 80,72 · gate4, cũng ghi trước khi chạy, 81,01 · cách demo đang dùng, chọn sau khi xem kết quả (peakprob) 82,01 · trần nếu biết trước dây tốt nhất 83,60*.
Dòng này đọc từ `analysis/dulieu_results.json`. Khi đọc to, luôn đọc **đủ năm số**, không bỏ 80,72.

### 4.1. Đèn tin cậy: đèn trong demo là cổng nào, bảo chứng bằng số nào

**Ba mức của cả bản ghi:** *CAO (xanh)*, *TRUNG BÌNH (vàng)*, *THẤP (đỏ)*. Cách tính: mục 4.2.

**Đèn trong demo là cổng nào.** Là **cổng cũ** `fsqi/gate_classical.pkl`, hiệu chuẩn trên mô hình 5 sản phụ ADFECGDB.
Cổng 22 ca **chưa** đưa vào demo.

**Số bảo chứng đúng cho đèn trong demo:** AUROC trong bản ghi **0,721** [0,517; 0,898].
* Đo trên **5 bản CinC sạch** có cả đoạn tốt lẫn đoạn xấu: a01, a06, a07, a09, a10. Năm bản này lấy từ mẫu a01–a10;
  5 bản còn lại của mẫu không có đoạn xấu nên không tính được AUROC trong bản ghi.
* Số này đo khi cổng **ghép với mô hình 5 ca**. Demo hiện ghép cổng này với **mô hình 22 ca**; nhóm **chưa đo lại** AUROC
  trong cấu hình đó.
* Nghĩa dễ hiểu: lấy một đoạn xấu và một đoạn tốt trong cùng bản ghi, cổng xếp đoạn xấu đáng ngờ hơn khoảng 72 lần
  trên 100. 0,5 là tung đồng xu. Khoảng tin cậy rất rộng, cận dưới gần mức đồng xu.
* **Không dùng** số AUROC gộp của cùng phép đo (0,929): tính trên cả a01–a10, trong đó 4 bản nhiễm (a03 a04 a05 a08),
  và phần lớn là hiệu ứng giữa các bản ghi, không phải khả năng xếp đoạn trong một bản ghi.

**Cổng không độc lập với mạng.** Trong 12 chỉ số, 6 thuần tín hiệu (`sampen`, `kurtosis`, `spec_entropy`, `band_ratio`,
`psd_fhr`, `tau_acf`), 4 tính trên nhịp do mạng tìm ra (`n_det`, `rr_cv`, `rr_plaus`, `bsqi`), 2 là xác suất đầu ra của
mạng (`peak_prob_mean`, `prob_max`). Trong phân tích cổng 22 ca, chỉ số quan trọng nhất là `rr_cv`, độ đều của nhịp do
mạng tìm ra (ΔAUROC hoán vị 0,140; kế đến `peak_prob_mean` 0,032; mười chỉ số còn lại dưới 0,002).
Ở a02 đèn vẫn đỏ vì hai đường: 6/15 đoạn bị chấm đỏ (40 %, quá 30 %), và luật bám nhịp mẹ (78 %, từ 60 % trở lên) so
trực tiếp với nhịp mẹ.

**Nếu bị hỏi "cổng 22 ca thì sao":**
> "Cổng 22 ca đạt AUROC trong bản ghi 0,934, khoảng tin cậy 0,872 đến 0,981. Nhưng cổng đó chưa đưa vào demo.
> Và số đó chỉ tính trên 11 trong 22 chủ thể có đoạn xấu."

**Không được nói:**
* "Đèn trong demo đạt AUROC 0,934." Sai cổng.
* "Đèn trong demo, với mô hình đang chạy, đạt 0,721." Chưa đo cấu hình đó.
* Bất kỳ số cổng nào đo trên 75 bản CinC. Đã rút.

Tab *Kết quả tổng hợp (60 bản sạch)* trong chế độ chuyên gia, mục *Cổng tin cậy*, ghi đủ cả hai cổng: *Cổng đang chạy trong demo*
(0,721, *chưa đo lại* với mô hình 22 ca) và *Cổng 22 ca* (0,934, tính trên 11/22 chủ thể, chưa đưa vào demo), kèm dòng
*Cổng không độc lập với mạng:*. Nếu người xem chỉ vào 0,934, nói ngay:
> "Số này của cổng 22 ca, chưa chạy trong demo, tính trên 11 trong 22 chủ thể. Đèn đang chạy là cổng 5 ca, 0,721, đo với mô hình 5 ca."

### 4.2. Nếu bị hỏi "đèn xanh, vàng, đỏ nghĩa là gì"

**Trả lời trong 30 giây:**
> "Đèn nói về độ tin của phép đo, không nói về sức khoẻ của bé. Máy chia bản ghi thành đoạn 4 giây. Mỗi đoạn được một
> bộ phân loại chấm mức đáng ngờ. Xanh là cổng không thấy dấu hiệu xấu ở đoạn đó, vàng là chưa chắc, đỏ là máy từ chối trả lời.
> Cả bản ghi bị đỏ khi hơn 30 phần trăm số đoạn đỏ, hoặc khi từ 60 phần trăm nhịp máy tìm trở lên trùng nhịp mẹ.
> Đèn đỏ thì mọi con số của bản ghi, kể cả nhịp tim, đều không dùng. Đèn xanh cũng chưa phải bằng chứng là đúng."

**Quy tắc đúng như mã** (`fsqi/gate.py`, `demo/core.py`):

| Mức | Điều kiện | Trên màn hình |
|---|---|---|
| Đoạn 4 giây xanh | mức đáng ngờ dưới 0,052 | cột xanh dưới vạch *xanh < 0,052* |
| Đoạn đỏ | mức đáng ngờ trên 0,540 | cột đỏ trên vạch *đỏ > 0,540*, nền đỏ |
| Đoạn vàng | ở giữa hai ngưỡng | cột vàng |
| Cả bản ghi *THẤP (đỏ)* | hơn 30 % số đoạn đỏ | lý do *> 30 % đoạn đỏ → THẤP* trong *Chi tiết kỹ thuật* |
| Cả bản ghi *CAO (xanh)* | không quá 30 % đoạn đỏ **và** hơn 70 % đoạn xanh | lý do *> 70 % đoạn xanh và ≤ 30 % đoạn đỏ → CAO* |
| Cả bản ghi *TRUNG BÌNH (vàng)* | còn lại | |
| Luật ghi đè → *THẤP (đỏ)* | từ 60 % nhịp máy tìm trở lên trùng đỉnh R mẹ (±50 ms) | lý do *… % nhịp thai trùng đỉnh R mẹ* kèm *mô hình đang BÁM NHỊP MẸ* |

Ngưỡng đoạn hiệu chuẩn trên ADFECGDB ngoài fold sao cho khoảng 85 % đoạn xanh và 5 % đoạn đỏ. Mức ngẫu nhiên của tỉ lệ
trùng nhịp mẹ là khoảng 13–22 %, nên 60 % là trùng có hệ thống.

**Bốn thẻ:**

| Thẻ | Đoạn xanh · vàng · đỏ (trên 15 hoặc 75) | Trùng nhịp mẹ | Đèn cả bản | Vì sao |
|---|---|---:|---|---|
| r01 | 75 · 0 · 0 (trên 75) | 16 % | CAO (xanh) | 100 % đoạn xanh |
| a09 | 13 · 1 · 1 (trên 15) | 18 % | CAO (xanh) | 87 % đoạn xanh, 7 % đoạn đỏ |
| a02 | 0 · 9 · 6 (trên 15) | 78 % | THẤP (đỏ) | **hai đường**: 40 % đoạn đỏ, và luật bám nhịp mẹ |
| a27 | 0 · 1 · 14 (trên 15) | 43 % | THẤP (đỏ) | 93 % đoạn đỏ |

**Đèn không có nghĩa là:**
* Không phải chẩn đoán, không phải mức nguy cơ của bé. Đoạn "xấu" được định nghĩa là đoạn máy tìm nhịp kém (F1 đoạn dưới 80).
* Xanh không chứng minh kết quả đúng. Cổng trong demo chỉ có AUROC trong bản ghi 0,721 (đo với mô hình 5 ca) và không độc
  lập với mạng. Trong lần chạy kiểm tra của nhóm trên 82 bản, 3 bản đèn xanh mà F1 dưới 90; thấp nhất là a57 (bản sạch),
  F1 17,02. Chú thích bước 5 của demo nay nói thẳng điều này (mục 4.4).
* Nhịp tim nằm trong 110–160 không có nghĩa là đúng: a02 báo 130 trong khi đáp án khoảng 160.

### 4.3. Nếu bị hỏi "vì sao gate 80,72 không được gọi là thắng"

**Trả lời trong 30 giây:**
> "Vì theo thủ tục em ghi trước khi chạy, quy tắc được đem đi kiểm là gate, và gate không qua hiệu chỉnh cho nhiều phép
> so. Hiệu so với cách cũ là cộng 6,44 điểm, nhưng p sau hiệu chỉnh Holm là 0,051. Em không làm tròn, không gọi là gần đạt.
> gate4 và peakprob cao hơn và qua được Holm, nhưng gate4 không phải quy tắc kế hoạch chọn, còn peakprob em chọn làm mặc
> định sau khi xem kết quả. Nên kết luận của em là: cách chọn dây mới là giả thuyết mạnh, chưa xác nhận."

**Sự kiện đằng sau câu trả lời:**

| Cách chọn dây | Vai trò | F1 60 bản sạch | Hiệu so với PSD [KTC 95 %] | p Wilcoxon | p Holm (7 quy tắc) | Thắng/hoà/thua so với PSD |
|---|---|---:|---|---:|---:|---|
| PSD | mốc cũ (Power-MF) | 74,28 | — | — | — | — |
| **gate** | **quy tắc kế hoạch chọn**, ghi trước khi chạy | **80,72** | +6,44 [+2,49; +11,10] | 0,010 | **0,051: không đạt** | 16 / 37 / 7 |
| gate4 | cũng ghi trước khi chạy, **không** phải quy tắc kế hoạch chọn | 81,01 | +6,72 [+2,85; +11,18] | 0,0025 | 0,015 | 17 / 38 / 5 |
| peakprob | có trong danh sách ghi trước, nhưng **chọn làm mặc định sau khi xem kết quả CinC**: hậu kiểm | 82,01 | +7,73 [+3,82; +12,41] | 0,00056 | 0,0039 | 19 / 35 / 6 |
| oracle | trần, nhìn đáp án | 83,60 | +9,32 [+5,01; +14,09] | — | — | — |

* Thủ tục ghi trước khi chạy: quy tắc "tốt nhất" được chọn theo F1 trung bình trên **22 chủ thể trong miền**; kết quả
  CinC của chính quy tắc đó là phép thử xác nhận duy nhất. Trên 22 chủ thể, gate đứng đầu, nên gate là quy tắc được kiểm.
* Hiệu chỉnh Holm tính trên 7 quy tắc mới (gate4 được thêm vào danh sách trước khi chạy quy tắc nào, nên số quy tắc tăng từ 6 lên 7).
* Khoảng tin cậy của gate không chứa 0 và p Wilcoxon chưa hiệu chỉnh là 0,010. Nhưng đó là **trước** khi tính đến việc so
  7 quy tắc cùng lúc. Sau hiệu chỉnh, 0,051 lớn hơn ngưỡng 0,05 nhóm dùng.
* Giới hạn phải nói nếu bị hỏi tiếp: tệp ghi trước **chưa neo vào lịch sử git** và được viết **sau khi** đã có F1 từng kênh.
  Không dùng chữ nào hàm ý đã đăng ký với bên thứ ba (`HANDOFF.md` mục 8.1).

**Không được nói:** "gate thắng", "gate gần đạt", "gate4 là quy tắc kế hoạch chọn", "peakprob đã được xác nhận",
hoặc nêu 81,01 mà không nêu 80,72.

### 4.4. Nếu bị hỏi "đèn xanh mà vẫn sai được à?" (a57, F1 17,02)

**Trả lời trong 30 giây:**
> "Được. Đèn xanh chỉ nói cổng không thấy dấu hiệu xấu, không nói kết quả đúng; demo ghi thẳng điều đó ở bước 5.
> Trong 82 bản em chấm, 3 bản đèn xanh mà F1 dưới 90. Hai bản trong đó, a52 và a54, thuộc 7 bản CinC có đáp án sai đã biết.
> Bản còn lại là a57: 14 trên 15 đoạn xanh mà F1 chỉ 17,02. Máy tìm ra một nhịp rất đều, khoảng 86 một phút, trong khi
> đáp án có 148 nhịp trong một phút. Cổng dùng cả độ đều của nhịp mạng tìm ra và độ tự tin của mạng, nên em cho là một nhịp
> sai mà đều vẫn lọt qua. Em chưa xác định máy bám vào nhịp gì. Vì vậy em không coi đèn xanh là bằng chứng."

**Sự kiện đằng sau** (lần chạy kiểm `demo/results/demo_check_2modes.json`, mô hình 22 ca, chọn dây peakprob; đã chạy lại
a57 bằng mã hiện tại ngày 17/09, ra cùng kết quả):

| a57 (CinC 2013 set-a, bản sạch, 60 s) | Giá trị |
|---|---|
| Dây được chọn · điểm tin của mạng | dây 4 · 0,985 (dây 1–3: 0,951 · 0,976 · 0,984) |
| F1 dây được chọn · bốn dây | 17,02 · 38,28 / 20,92 / 17,87 / 17,02 |
| Đúng · báo dư · bỏ sót | 20 · 67 · 128 (máy báo 87 nhịp, đáp án 148 nhịp) |
| Nhịp tim máy báo | ≈ 86 nhịp/phút, dưới dải 110–160 |
| Đèn cổng học (demo mặc định) | *CAO (xanh)*: 14 xanh · 1 vàng · 0 đỏ trên 15 đoạn; trùng nhịp mẹ 0 % nên luật bám mẹ không bật |
| Đèn luật cứng (tuỳ chọn trong chế độ chuyên gia) | *TRUNG BÌNH (vàng)*: nhịp tim 86 ngoài khoảng 100–200 luật cứng coi là hợp lý; hệ số biến thiên RR 0,04 (đều); 100 % đỉnh có xác suất trên 0,9 |
| Ba bản đèn xanh mà F1 dưới 90 | a52 85,39 · a54 38,79 · a57 17,02; a52 và a54 thuộc 7 bản nhãn sai đã khai báo |

* [SỰ KIỆN] 12 chỉ số của cổng gồm 4 chỉ số tính trên nhịp mạng tìm ra (có `rr_cv`, độ đều) và 2 xác suất của mạng (mục 4.1).
* [SUY LUẬN] "Nhịp sai mà đều vẫn lọt qua cổng" là cách nhóm giải thích, chưa có phân tích riêng cho a57 (chưa tách đóng góp
  từng chỉ số trên bản này). Không nói máy bám tim mẹ: tỉ lệ trùng nhịp mẹ đo được là 0 %.
* Muốn cho xem tận mắt: bật chế độ chuyên gia → *Nguồn dữ liệu* *Bản ghi mẫu* → chọn a57 → *Phân tích*. Không có thẻ riêng.

**Không được nói:** "đèn xanh là kết quả đúng", "đèn xanh thì tin được", "cổng bắt được mọi bản sai".

### 4.5. Nếu bị hỏi "sao lúc bấm chạy nhanh, lúc chậm?"

**Trả lời trong 30 giây:**
> "Có mấy lý do. Một, lần đầu mở trang máy phải nạp mô hình. Hai, r01 dài 5 phút, ba bản CinC chỉ 1 phút, nên r01 lâu hơn;
> và để chọn dây, máy chạy mạng trên cả bốn dây rồi mới chọn. Ba, trình duyệt còn phải vẽ năm hình, chậm hơn khi máy không
> có card đồ hoạ hoặc đang bận việc khác. Bấm *Tiếp* trong lúc thẻ chưa chạy xong thì nút phải chờ lượt phân tích xong."

**Sự kiện đằng sau:**
* Phần tính toán, đo trong lần chạy kiểm `demo/results/demo_check_showcase.json` (12/09, 2 luồng CPU):

  | Bản | Dài | Xử lý dây đã chọn | Chạy mạng trên cả 4 dây để chọn | Cổng chấm đoạn |
  |---|---:|---:|---:|---:|
  | r01 | 300 s | 424 ms | 1.997 ms | 1.041 ms |
  | a09 | 60 s | 135 ms | 513 ms | 177 ms |
  | a02 | 60 s | 128 ms | 497 ms | 161 ms |
  | a27 | 60 s | 116 ms | 423 ms | 173 ms |

* Thời gian bấm thẻ trong trình duyệt (mục 2.5) lớn hơn tổng các số trên vì còn dựng 5 hình, gửi về trình duyệt và vẽ.
  Hai phép đo khác lần chạy, không trừ cho nhau được.
* Chuyển bước **không** tính lại; nhưng hình của bước mới được trình duyệt vẽ lúc hiện ra. Trong lần đo ở mục 2.5, sang
  bước 4 lâu nhất ở cả bốn thẻ. [SUY LUẬN] Hình bước 4 có một hàng cho mỗi dây nên nặng nhất; nhóm chưa đo riêng.
* Bấm thẻ và bấm *Tiếp* / *Quay lại* xếp chung một hàng đợi (`demo/app.py`, `concurrency_id='trinh_bay'`), để *Tiếp* không
  chạy song song với lượt phân tích rồi bị kết quả thẻ ghi đè. Hệ quả: bấm *Tiếp* khi dòng *⏳ Đang phân tích…* còn hiện
  thì nút chờ tới khi phân tích xong.
* Bấm hai thẻ liền nhau: lượt sau chờ lượt trước, và chỉ thẻ bấm sau cùng được vẽ. Lượt cũ bị bỏ qua cả khi chưa bắt đầu lẫn khi đang tính dở (ví dụ r01 đang tự chạy lúc mở trang): nó tính xong nhưng không vẽ, dòng *⏳ Đang phân tích…* của thẻ mới vẫn giữ. Vì lượt cũ vẫn phải tính xong, thẻ mới có thể chờ lâu gấp đôi. Chắc nhất vẫn là nhìn ô *Bản ghi* ở thanh tóm tắt trước khi nói tiếp.
* Máy chậm bất thường: đóng việc nặng khác, đặt ba biến luồng như mục 1, tải lại trang.

---

## 5. Chế độ chuyên gia

Tick ô *Chế độ chuyên gia — hiện 8 tab đầy đủ (bảng số, dữ liệu của nhóm, tải tệp, nhật ký)* ở cuối trang.
Phần mở ra gồm: hàng điều khiển (*Nguồn dữ liệu*, *Bản ghi minh hoạ cho buổi demo (thứ tự gợi ý: từ trên xuống)*,
*Kênh bụng*, *Đèn tin cậy*, nút *Phân tích*) và 8 tab:
*Tín hiệu (5 tầng)* · *Chọn kênh — cả 4 kênh* · *Nhịp tim thai + đèn đoạn* · *So sánh với nhãn* ·
*Kết quả tổng hợp (60 bản sạch)* · *Dữ liệu của nhóm* · *Tải dữ liệu mới* · *Nhật ký (JSON)*.

**Ở màn hình 1366 px, thanh tab chỉ hiện 6 tab đầu.** Hai tab *Tải dữ liệu mới* và *Nhật ký (JSON)* nằm trong nút
**⋯** ở cuối thanh tab, bên phải. Bấm nút **⋯**, rồi bấm tên tab. Gradio tự dồn tab không vừa chiều ngang vào nút này.
Đã kiểm bằng trình duyệt tự động ngày 17/09/2026 (`demo/screenshots/screenshots_v2.json` → `tab_trong_menu_tran`).

**Thẻ** *Tệp của bạn* ở hàng thẻ trên cùng: bấm vào là ô chế độ chuyên gia tự được tick, tab *Tải dữ liệu mới* mở thẳng,
và trang **tự cuộn** tới phần tải tệp (tiêu đề *Thử mô hình trên dữ liệu chưa có trong đề tài*). Không cần nút **⋯**.

Bật khi:

| Tình huống | Làm gì |
|---|---|
| Bị hỏi "82,01 và 74,28 lấy ở đâu, có ý nghĩa thống kê không" | Tab *Kết quả tổng hợp (60 bản sạch)*: bảng có KTC 95 %, p Wilcoxon, p Holm, dấu phẩy thập phân. Tên hàng: *gate — quy tắc kế hoạch chọn (KHAI BÁO TRƯỚC)* · *gate4 — cũng ghi trước khi chạy, qua Holm* · *peakprob — HẬU KIỂM, chọn sau khi xem kết quả (mặc định demo)*. Nói theo mục 4.3. Lưu ý mục *Cổng tin cậy* (mục 4.1) |
| Bị hỏi "dữ liệu thật ở đâu, bao nhiêu bản, nhãn từ đâu" | Tab *Dữ liệu của nhóm* (mục 6.2) |
| Người xem đưa tệp của họ | Bấm thẻ *Tệp của bạn* (mục 6.3) |
| Muốn chọn dây bằng tay, đổi cách chọn dây, hoặc đổi đèn học / luật | Ô *Kênh bụng* (*Tự động — peakprob (mặc định)*, *Tự động — PSD (Power-MF)*, *1*–*4*) và ô *Đèn tin cậy* (*Học (GBM, 12 chỉ số / đoạn 4 s)*, *Luật cứng (4 thành phần)*), rồi bấm *Phân tích* |
| Muốn xem B2_03 hoặc bản mẫu khác | *Nguồn dữ liệu* → *Minh hoạ (5 bản)* hoặc *Bản ghi mẫu* → chọn bản → *Phân tích* |
| Cần số để chép vào báo cáo | Nút **⋯** → *Nhật ký (JSON)* |

Chế độ chuyên gia có hàng điều khiển và nút *Phân tích* riêng. Nó **không** dùng chung kết quả với 5 bước phía trên.
Tắt ô tick thì 8 tab ẩn đi, 5 bước vẫn giữ nguyên. Nút *Phân tích* của hàng điều khiển này đã chạy đúng từ lượt sửa thứ
ba (trước đó nút bị gắn nhầm vào nút *◀ Quay lại* của 5 bước nên bấm không ra kết quả).

**Số kiểu Việt.** Thẻ đèn, bảng kênh (điểm PSD ghi dạng `7,14·10^0` thay cho `7.14e+00`), dòng trạng thái và tab
*Dữ liệu của nhóm* ghi dấu phẩy thập phân. Lý do của đèn ghi đúng câu của cổng: *Bộ phân loại GBM (12 chỉ số của đoạn: 6 thuần tín hiệu, 4 tính trên nhịp mạng tìm ra, 2 là xác suất của mạng; huấn luyện trên ADFECGDB): …*,
ngưỡng đoạn in ba chữ số (0,052 và 0,540), dấu % cách số. Vẫn còn chỗ ghi kiểu máy: tiêu đề hình *Tín hiệu (5 tầng)*
(ví dụ ngưỡng `0.75`) và đơn vị *bpm* trên các hình của chế độ chuyên gia. Năm chỗ thẩm định cuối 17/09 tìm thêm đã sửa:
chú thích *Xem tín hiệu thô* (thời lượng và mili-giây), dòng lỗi tệp quá ngắn (*Bản ghi chỉ dài 5,00 giây*), vạch ngưỡng
hình đèn đoạn (*xanh < 0,052* / *đỏ > 0,540*), điểm PSD trên thẻ kênh (dạng `1,69·10^1`), và dấu phân cách đôi ở tiêu đề hình kênh.

**Tab *Dữ liệu của nhóm*, bộ CinC 60 bản sạch** ghi: *Đây là bộ ngoài miền: đã kiểm là không trùng dữ liệu huấn luyện (tương quan chéo tối đa 0,62). Nhiều khả năng khác thiết bị và dân số, nhưng ban tổ chức không công bố nguồn của từng bản.*
kèm đủ năm số 74,28 · 80,72 · 81,01 · 82,01 · 83,60. Hộp *Cách đọc hình này* của tab không còn khẳng định gai thai luôn nhỏ:
nó ghi *ở vài kênh (ví dụ r01 kênh 4) gai thai to ngang gai mẹ, nên hãy dựa vào vạch đỏ*.

Mặc định 8 tab **không tự chạy** khi mở trang. Muốn chúng chạy sẵn r01 thì đặt `$env:RELYFETAL_AUTORUN_EXPERT = "1"`
trước khi mở. Hướng dẫn chi tiết từng tab: `HUONG_DAN_DEMO_v1.md` mục 5.

---

## 6. Dữ liệu của nhóm và dữ liệu mới

### 6.1. Dữ liệu của nhóm nằm ở đâu

Gốc dự án: `D:\NCKHSV2026-2027`. Kho mã **không** chứa dữ liệu sinh lý; tải lại theo `HANDOFF.md` mục 4.
Bảng dưới kiểm ngày 17/09/2026 bằng chính hàm đọc của tab *Dữ liệu của nhóm* (`demo/core.py: dataset_rows`).

| Bộ | Thư mục (tính từ gốc) | Tệp của mỗi bản ghi | Tần số | Độ dài | Dây bụng | Nhãn từ đâu | Dùng làm gì |
|---|---|---|---|---|---|---|---|
| **ADFECGDB** (PhysioNet), 5 bản `r01 r04 r07 r08 r10` | `model/data/adfecgdb` | `rXX.edf` + `rXX.edf.qrs` | 1000 Hz | 300 s | 4 | Trực tiếp: điện cực da đầu thai | Huấn luyện (trong 22 chủ thể); thẻ r01 |
| **Silesia B1** — thai kỳ, 10 bản | `model/data/silesia/extracted/Data Records/B1_Pregnancy_dataset` | `B1_abSignals_XX.ecg` (nhị phân) + tệp nhãn `.txt` | 500 Hz | 1197,8 s (khoảng 20 phút) | 4 | Gián tiếp: tác giả khử QRS mẹ trên tín hiệu bụng rồi soát tay | Huấn luyện (trong 22 chủ thể) |
| **Silesia B2** — chuyển dạ, 12 bản trên đĩa | `model/data/silesia/extracted/Data Records/B2_Labour_dataset` | `B2_abSignals_XX.ecg` + `B2_dFECG_XX.ecg` + nhãn `.txt` | 500 Hz (dây bụng) | 300 s | 4 | Trực tiếp: điện cực da đầu thai | 7 bản trong 22 chủ thể; 5 bản trùng ADFECGDB đã loại |
| **CinC 2013 set-a**, 75 bản | `benchmark_dpss/pcdb` | `aXX.hea` + `aXX.dat` + `aXX.fqrs` | 1000 Hz | 60 s | 4 | Người chấm độc lập của ban tổ chức | **60 bản sạch**: kiểm tra ngoài miền (7 bản trong đó có nhãn sai đã khai báo). **15 bản nhiễm**: không dùng làm kết quả |

22 chủ thể huấn luyện = 5 ADFECGDB + 10 Silesia B1 + 7 Silesia B2. Mọi con số của đề tài đo trên bản ghi 4 dây bụng.

**15 bản CinC nhiễm** là bản sao nguyên văn ADFECGDB: `a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25`.
Mở trúng một bản trong số này thì nói ngay: "Bản này trùng dữ liệu huấn luyện, không được coi là ngoài miền."

### 6.2. Xem dữ liệu thô thế nào

**Cách 1 — trong demo.** Bật chế độ chuyên gia → tab *Dữ liệu của nhóm*.
1. Ô *Bộ dữ liệu*, 5 lựa chọn: *ADFECGDB — 5 bản (PhysioNet, nhãn da đầu)* · *Silesia B2 — chuyển dạ (12 bản trên đĩa, nhãn da đầu)* ·
   *Silesia B1 — thai kỳ (10 bản, nhãn gián tiếp)* · *CinC 2013 set-a — 60 bản SẠCH (ngoài miền)* ·
   *CinC 2013 set-a — 15 bản NHIỄM (bản sao ADFECGDB)*.
2. Phần mô tả định dạng của bộ đang chọn, kèm 8 dòng đầu của một tệp header `.hea` hoặc tệp nhãn `.txt`, in nguyên văn.
3. Bảng *Từng bản ghi trong bộ (đọc thật từ tệp trên đĩa)*, 9 cột: *Bản ghi* · *Đường dẫn trên đĩa* · *Định dạng* ·
   *fs gốc (Hz)* · *Dài (s)* · *Số kênh bụng* · *Số nhịp trong nhãn* · *Nguồn nhãn* · *Ghi chú*.
4. Ô *Bản ghi muốn xem tín hiệu thô* → nút *Xem tín hiệu thô*.
5. Hình: 10 giây đầu, mọi dây bụng xếp chồng, vạch đỏ là nhãn nhịp thai. Chưa lọc, chưa khử mẹ.
   Các đường đã được dời lên xuống cho khỏi đè: chỉ so hình dạng, không so độ cao. Hộp *Cách đọc hình này* ở dưới cùng.

**Cách 2 — mở header bằng Notepad.** `notepad D:\NCKHSV2026-2027\benchmark_dpss\pcdb\a09.hea`. Nội dung thật:

```
a09 4 1000 60000
a09.dat 16 10/uV 12 0 57 -11458 0 AECG1
a09.dat 16 10/uV 12 0 3 14104 0 AECG2
a09.dat 16 10/uV 12 0 -31 -732 0 AECG3
a09.dat 16 10/uV 12 0 -18 25735 0 AECG4
```

Dòng 1: tên bản ghi, 4 tín hiệu, 1000 mẫu mỗi giây, 60 000 mẫu, tức 60 giây. Mỗi dòng sau mô tả một dây bụng
(`AECG1`…`AECG4`). Tệp `.dat`, `.edf`, `.ecg` là nhị phân, Notepad không đọc được. Giải thích từng ô:
`HUONG_DAN_DEMO_v1.md` mục 4(b).

### 6.3. Giảng viên muốn thử dữ liệu mới: chuẩn bị tệp gì

**Định dạng demo nhận** (bảng trong tab *Tải dữ liệu mới*):

| Định dạng | Cần tải lên | Tệp có tự khai tần số không |
|---|---|---|
| `.edf` | một tệp `.edf` (kèm `.edf.qrs` nếu có nhãn) | Có |
| WFDB | **cả hai** tệp `.dat` và `.hea` | Có |
| `.csv` | một tệp, mỗi cột một dây; cho phép một dòng tiêu đề | Không, phải nhập tần số |
| `.npy` | mảng 2 chiều (dây × mẫu hoặc mẫu × dây) | Không, phải nhập tần số |
| `.txt` | như `.csv` nhưng ngăn cách bằng khoảng trắng | Không, phải nhập tần số |

**Điều kiện** (theo `demo/core.py`):
* Dài ít nhất **8 giây**; ngắn hơn thì demo từ chối kèm thông báo tiếng Việt.
* Tần số lấy mẫu **50–20 000 Hz**. Demo tự đưa về 1000 Hz rồi xuống 250 Hz trước khi vào mô hình.
* Nên dài **từ 60 giây**: đèn chia đoạn 4 giây, 60 giây cho 15 đoạn, như các bản CinC trên thẻ.
* Hơn 12 cột tín hiệu thì demo cảnh báo; mô hình vẫn chạy trên mọi cột, nên cột không phải điện tim bụng cần bỏ trước.

**Nhãn (tuỳ chọn).** Có nhãn mới tính được F1. Hai dạng:
* `.qrs` hoặc `.fqrs` (chú giải WFDB), cần tệp `.hea` cùng tên.
* `.csv` hoặc `.txt` **một cột**, mỗi dòng một **chỉ số mẫu**, tính theo tần số của tệp tín hiệu.

**Tệp ví dụ có sẵn**, thư mục `demo/assets/` (đã kiểm nội dung ngày 17/09):

| Tệp | Nội dung |
|---|---|
| `vidu_tai_len.csv` | dòng tiêu đề `AECG1,AECG2,AECG3,AECG4` + 30 000 dòng số; 4 cột = 4 dây; 1000 Hz; 30 giây; đơn vị µV |
| `vidu_tai_len_nhan.csv` | 65 dòng, một cột, không tiêu đề; mỗi dòng một chỉ số mẫu ở 1000 Hz |
| `vidu_tai_len_META.json` | nguồn, tần số, số mẫu, số dây, cảnh báo |

> ⚠ Hai tệp này **trích từ bản a09** của CinC 2013 set-a. **Không phải dữ liệu mới thật**, chỉ để thử luồng tải lên.
> Không trích F1 chạy trên tệp này: nó chỉ là 30 giây, khác F1 94,25 của a09 đầy đủ (`HANDOFF.md` mục 8.4).

**Các bước:**
1. Bấm thẻ *Tệp của bạn* (hoặc nút **⋯** → *Tải dữ liệu mới*).
2. Ô *Tệp bản ghi — chọn NHIỀU tệp cùng lúc nếu là cặp .dat + .hea*.
3. Ô *Tần số lấy mẫu (Hz) — CHỈ dùng cho .csv / .npy / .txt*. Mặc định 1000.
4. (Tuỳ chọn) Ô *Nhãn tham chiếu (tuỳ chọn): .qrs · .fqrs · .csv/.txt một cột chỉ số mẫu*. **Tệp nhãn bỏ vào ô này**, không bỏ vào ô tệp bản ghi.
5. Bấm *Phân tích*. Demo **xoá kết quả cũ trước**, dòng trạng thái ghi *Đang đọc tệp và phân tích… kết quả cũ đã được xoá.*
   Nếu lần này lỗi, màn hình không còn số của tệp trước.
6. Kết quả hiện ở 5 tab con: *Kết quả: tín hiệu (5 tầng)* · *Kết quả: chọn kênh* · *Kết quả: nhịp tim + đèn* ·
   *Kết quả: so với nhãn* · *Kết quả: nhật ký JSON*. Tệp tải lên **không** đi theo 5 bước kể chuyện.

**Lỗi hay gặp và demo báo gì.** Lỗi của phần tải tệp **không** bật hộp báo nào (không còn hộp hay nhãn "Error" tiếng Anh).
Lỗi hiện ở dòng trạng thái ngay dưới nút *Phân tích*, bằng lời thường, không có vết lỗi Python, theo khuôn:
*Không phân tích được tệp. … Kết quả cũ đã được xoá; sửa tệp rồi bấm Phân tích lại.* Chỗ `…` là một trong các lý do ở bảng dưới.
Thẻ số, hình và bảng của lần trước đã bị xoá trước khi chạy, nên không còn số cũ trông như kết quả mới.

| Tình huống | Lý do demo ghi |
|---|---|
| Bấm *Phân tích* khi chưa chọn tệp | *Chưa chọn tệp nào. Hãy tải lên .edf, hoặc CẶP .dat + .hea, hoặc .csv / .npy / .txt.* |
| Bỏ cả tệp tín hiệu lẫn tệp nhãn một cột vào ô tệp bản ghi | *Ô "Tệp bản ghi" đang có … tệp bảng số (…). Tệp … chỉ có một cột, nhiều khả năng là tệp NHÃN: hãy chuyển nó sang ô "Nhãn tham chiếu" rồi bấm Phân tích lại.* |
| `.csv`/`.txt` sai cột, lẫn chữ | *Không đọc được tệp … thành bảng số. Tệp .csv/.txt phải gồm các cột SỐ: mỗi cột một kênh, mỗi dòng một mẫu, được phép có một dòng tiêu đề; mọi dòng phải có cùng số cột và không lẫn chữ.* Phần chi tiết kỹ thuật **không** hiện trên giao diện; demo chỉ in nó ra cửa sổ dòng lệnh đang chạy `python demo/app.py` |
| Chỉ có `.dat`, thiếu `.hea` | *Tệp … là WFDB nhị phân nhưng THIẾU tệp header .hea đi kèm. Hãy chọn CẢ HAI tệp (.dat và .hea) cùng lúc rồi tải lên lại.* |
| Bản ghi quá ngắn | *Bản ghi chỉ dài … s — quá ngắn.* |
| Tần số nhập ngoài 50–20 000 Hz | *Tần số lấy mẫu … Hz không hợp lý (chấp nhận …–… Hz). Tệp .csv/.npy/.txt KHÔNG tự khai tần số nên bạn phải nhập đúng.* |
| Mọi chỉ số nhãn nằm ngoài bản ghi (thường do nhãn ghi bằng giây) | *Mọi chỉ số trong tệp nhãn đều nằm NGOÀI bản ghi* … gợi ý đơn vị giây hoặc tần số khác |
| Nhịp tim suy ra ngoài 100–200 nhịp/phút (thường do nhập sai tần số) — **cảnh báo**, vẫn chạy, hiện trong dòng trạng thái dưới dấu ⚠. Khoảng 100–200 lấy từ luật cứng của đèn (`demo/core.py: CONF_RULE`), trước đây là 80–220 | Có nhãn: *Tệp nhãn cho … nhịp trong … giây (≈ … nhịp/phút), ngoài khoảng thường gặp của tim thai (bình thường 110–160; demo cảnh báo ngoài 100–200). Kiểm tra lại ô tần số lấy mẫu.* Không có nhãn: *Nhịp tim máy tìm ≈ … nhịp/phút, ngoài khoảng thường gặp của tim thai. Nếu tệp không tự khai tần số, hãy kiểm tra lại ô tần số lấy mẫu.* |

### 6.4. Đọc kết quả khi không có đáp án

Demo nói rõ trên màn hình:
* Dòng trạng thái có câu *không có nhãn → KHÔNG tính được F1/Se/PPV*.
* Hộp vàng *Không có nhãn tham chiếu → chỉ xem được vị trí nhịp và điểm tin cậy. KHÔNG tính được F1 / Se / PPV.*
* Tab con *Kết quả: so với nhãn* ghi *Bản ghi không có nhãn — chế độ so sánh tắt.*

Đọc theo thứ tự:
1. **Đèn tin cậy và lý do.** Hộp đỏ *Cảnh báo về miền dữ liệu.* trên giao diện ghi *Đèn tin cậy (cổng từ chối) là thứ cần nhìn trước hết*, không phải số nhịp.
   Hộp này cũng nêu đủ bốn số ngoài miền 74,28 · 80,72 · 81,01 · 82,01 và bốn cách thích nghi miền đã thất bại
   (*chặn điện lưới +0,25 · tự huấn luyện nhãn giả −0,67 · AdaBN −1,58 · TENT −2,43*).
2. **Dòng *… % nhịp thai trùng đỉnh R mẹ*** trong lý do. Lý do ghi mức ngẫu nhiên khoảng 13–22 %. Từ 60 % trở lên thì
   máy đang bám nhịp mẹ và đèn bị ép đỏ.
3. **Đường nhịp tim** và số đoạn đỏ.
4. **Điểm chọn dây** của từng dây.

Nói rõ giới hạn:
> "Không có đáp án thì em không chứng minh được đúng hay sai. Em chỉ trình bày kết quả và mức tự tin của hệ thống."

* Nhịp nằm trong 110–160 **không** có nghĩa là đúng. a02 báo 130 trong khi đáp án khoảng 160.
* Đèn xanh **không** phải bằng chứng (mục 4.2, 4.4).

### 6.5. Nên hỏi gì về dữ liệu

Hỏi trước khi nhận tệp. Mỗi câu gắn với một điều demo cần.

| Câu hỏi | Vì sao cần |
|---|---|
| Đây là điện tim đo trên bụng mẹ, hay đường nhịp CTG (Doppler)? | Demo chỉ đọc tín hiệu điện tim dạng tệp số. Giấy in hoặc ảnh đường CTG không dùng được (`HUONG_DAN_DEMO_v1.md` mục 6(c)) |
| Tệp định dạng gì? | Demo nhận `.edf`, WFDB, `.csv`, `.npy`, `.txt`. Định dạng khác phải đổi trước |
| Tần số lấy mẫu bao nhiêu Hz? | `.csv`, `.npy`, `.txt` không tự khai. Nhập sai thì thời gian bị co giãn, nhịp tim ra sai |
| Có mấy dây bụng? Cột nào là dây bụng, có cột nào là kênh khác không? | Mô hình chạy trên mọi cột. Số của đề tài đo trên 4 dây bụng |
| Mỗi bản ghi dài bao lâu? | Dưới 8 giây demo từ chối; nên từ 60 giây |
| Có nhãn nhịp thai không? Lấy từ điện cực da đầu hay người chấm? Ghi bằng chỉ số mẫu hay giây? | Có nhãn mới có F1. Nhãn phải là chỉ số mẫu. Nguồn nhãn quyết định độ tin của F1 |
| Ghi lúc mang thai hay lúc chuyển dạ? | Dữ liệu huấn luyện có cả hai: Silesia B1 thai kỳ; ADFECGDB và Silesia B2 chuyển dạ |
| Nhóm có được phép dùng dữ liệu này không? | Giấy phép và đạo đức phải rõ trước khi chạy |

Trường hợp chỉ có giấy in CTG, không có nhãn, mẫu thư xin dữ liệu: `HUONG_DAN_DEMO_v1.md` mục 6(c)–6(đ).

---

## 7. Dự phòng

| Sự cố | Làm gì |
|---|---|
| Trang không mở / cổng bận | `$env:RELYFETAL_PORT = "7870"; python demo/app.py` → http://127.0.0.1:7870 |
| Bấm thẻ không thấy gì đổi | Nhìn dòng trạng thái dưới hàng thẻ (*⏳ Đang phân tích bản ghi …*) và ô *Bản ghi* ở thanh tóm tắt. Xong là khi ô *Bản ghi* đổi sang **đúng bản vừa bấm**; dòng trạng thái biến mất thôi chưa đủ (lượt trước đã chạy dở có thể xoá dòng đó sớm, mục 4.5). Trang chỉ tự cuộn khi thanh 5 bước chưa nằm ở nửa trên màn hình, nên không thấy cuộn chưa chắc là lỗi. Máy đang bận việc khác thì có thể lâu hơn *khoảng 5–10 giây* (mục 2.5, 4.5). Vẫn không được thì tải lại trang (F5) |
| Dòng trạng thái chuyển nền đỏ: *Không phân tích được bản ghi …: …* | Hình bên dưới **vẫn là bản ghi trước**, không phải kết quả của thẻ vừa bấm. Làm đúng như dòng đó ghi: *bấm lại thẻ hoặc chọn thẻ khác*. Lỗi lặp lại thì chiếu ảnh dự phòng |
| Lỡ bấm hai thẻ liền nhau | Không bấm thêm. Chờ; chỉ thẻ bấm sau cùng được vẽ, nhưng máy phải tính xong lượt cũ trước nên có thể chờ lâu gấp đôi (mục 4.5). Chỉ nói tiếp khi ô *Bản ghi* ở thanh tóm tắt ghi đúng bản vừa bấm |
| Thanh tóm tắt không dính đáy | Cửa sổ trình duyệt hẹp từ 700 px trở xuống thì thanh nằm yên cuối các bước (cố ý, để thanh không che hình). Phóng to cửa sổ |
| Thẻ mờ, ghi *⚠ chưa có trên đĩa — xem hướng dẫn tải dữ liệu* | Chưa tải dữ liệu: `HANDOFF.md` mục 4 (`python model/download_data.py --root model/data --only adfecgdb`, `python model/download_more.py --only cinc75`) |
| Không thấy tab *Tải dữ liệu mới* hoặc *Nhật ký (JSON)* | Bấm nút **⋯** ở cuối thanh tab (mục 5), hoặc bấm thẻ *Tệp của bạn* |
| Biểu đồ trắng (WebGL bị chặn) | Hộp *Con số cần nhớ*, thanh tóm tắt và thẻ vẫn đúng; chiếu ảnh `demo/screenshots/17..23` thay hình |
| Gradio lỗi khi khởi động | `python demo/run_check.py --only r01,a09,a02,a27 --mode hoc --out demo_check_4the --threads 2`, kể theo bảng in ra terminal |
| Python hoặc torch hỏng hẳn | Chiếu 7 ảnh theo thứ tự dưới. **Không sửa mã trước mặt người xem** |
| Bị hỏi con số không nhớ | Nút **⋯** → *Nhật ký (JSON)*; hoặc mở `demo/results/demo_check_showcase.json` |

**Chiếu ảnh thay demo — 7 ảnh, thư mục `demo/screenshots/`** (chụp bằng `python demo/screenshot_v2.py`, 17/09/2026 22:01–22:02, sau lượt sửa thứ ba):

| # | Tệp | Nói gì |
|---|---|---|
| 17 | `17_the_r01.png` | "Năm thẻ, mỗi thẻ một ca. Đây là Ca dễ, bản r01: F1 99,92, đèn xanh." |
| 18 | `18_the_a09.png` | "Chọn dây quyết định, bản a09 của bộ CinC 2013, không trùng dữ liệu huấn luyện. Thẻ ghi 19,35 thành 94,25." |
| 21 | `21_a09_buoc4.png` | "Bước 4 của a09: cách cũ chọn dây 2, F1 19,35; cách mới chọn dây 1, F1 94,25. Chọn mà không nhìn đáp án." |
| 19 | `19_the_a02.png` | "Máy bám nhầm tim mẹ, bản a02: 78 phần trăm nhịp trùng nhịp mẹ. Đèn đỏ, ô nhịp tim bị gạch." |
| 23 | `23_a02_buoc4.png` | "Hộp vàng: dây 1 đạt 75,88, nhưng 6 trên 7 cách chọn không nhìn đáp án chọn dây 2, không cách nào chọn dây 1." |
| 22 | `22_a02_buoc5.png` | "Máy báo 130, nằm trong vùng bình thường, nhưng đáp án khoảng 160. Đèn đỏ, 6 trên 15 đoạn bị từ chối." |
| 20 | `20_the_a27.png` | "Bốn dây đều kém, bản a27: F1 từng dây 21,26 đến 32,94. Máy từ chối 14 trên 15 đoạn thay vì đoán." |

Nếu chỉ kịp chiếu **một** ảnh: `21_a09_buoc4.png`, nói ba câu:
"Cùng bản ghi, cùng mô hình, chỉ khác dây." — "Dây 1 F1 94,25, dây 2 F1 19,35; cách cũ chọn dây 2." —
"Trên 60 bản sạch: cũ 74,28; gate, quy tắc kế hoạch chọn, 80,72 và không qua Holm; gate4 81,01; cách mới 82,01 nhưng chọn sau khi xem kết quả; trần 83,60."

**Không được làm:**
* Không mở 15 bản nhiễm làm ví dụ ngoài miền.
* Không dùng 0,934 để bảo chứng cho đèn trong demo; không nói 0,721 là số của đèn ghép với mô hình 22 ca; không nêu số cổng đo trên 75 bản CinC.
* Không nói peakprob là quy tắc đã xác nhận. Không trình bày 82,01 hoặc 81,01 mà thiếu 74,28 và 80,72. Không gọi gate là thắng.
* Không nói a27 "không có tín hiệu thai". Không nói ở a02 "không dây nào cứu được".
* Không trích F1 của tệp ví dụ `vidu_tai_len.csv`.
* Không dùng thời gian ở mục 2.5 để kết luận demo nhanh hay chậm.
* Không nói đèn xanh là bằng chứng kết quả đúng (a57: đèn xanh, F1 17,02). Không nói "máy ghi khác, nơi khác" về từng bản CinC.
* Không hứa nhân rộng; không dùng các cụm từ cấm trong `HANDOFF.md` mục 8.1.

---

## Phụ lục A — truy nguồn con số

| Con số | Tệp trên đĩa |
|---|---|
| Thẻ: r01 F1 99,92 · a09 94,25 · a02 24,91 · a27 32,94; mức đèn từng bản | `demo/results/demo_check_showcase.json` → `rows.<bản>_leadpeakprob.metrics.F1`, `.confidence.level` (demo đọc tệp này lúc dựng thẻ) |
| Tên ca, chữ trên thẻ, chú thích 5 bước, ghi chú cổng, dòng tóm tắt, hộp vàng | `demo/app.py`: `story_card_spec`, `STORY_UPLOAD_CARD`, `STORY_CAPTION`, `STORY_GATE_NOTE`, `story_summary_html`, `story_wrong_lead_html`, `story_texts` |
| a02: bám mẹ 78 %; nhịp máy báo 130; đáp án ≈ 160; tim mẹ 124 | `demo/results/demo_check_showcase.json` → `rows.a02_leadpeakprob.confidence.components.maternal_lock` (0,783); `.fhr_mean` (129,9); `.n_labels` 160 / `.duration_s` 60; mạng báo 129 nhịp: `.n_beats`; ngưỡng 0,75: `.threshold`. **124 nhịp mẹ chưa lưu trong tệp JSON nào**: đó là số demo tính khi chạy (hộp *Con số cần nhớ* bước 1–2), nhóm đọc lại bằng cách chạy `story_compute('a02')` ngày 17/09 |
| a02: dây 1 F1 75,88, điểm tin 0,963; dây 2 F1 24,91, điểm tin 0,970; dây 3 19,86; dây 4 24,49; 0 xanh · 9 vàng · 6 đỏ | cùng tệp → `rows.a02_leadpeakprob.leads.<1–4>.F1`, `.peakprob`; `.confidence.components.n_green/n_yellow/n_red` |
| a02: 6/7 cách chọn (psd, gate, gate4, rrcv, peakprob, rrplaus) chọn dây 2; learned chọn dây 3; không cách nào chọn dây 1 | `analysis/chonkenh_results.json` → `chon_kenh_theo_quy_tac.cinc.a02` (chỉ số 1 = dây 2; `learned` 2 = dây 3) |
| a02 lệch dây tốt nhất 50,97 điểm, lớn nhất trong 60 bản sạch (kế đến a57 21,26) | `analysis/chonkenh_results.json` → `F1_tung_ban_ghi.cinc` (`oracle` − `peakprob`, lọc theo `analysis/dulieu_results.json → chon_kenh_60_sach.ban_ghi_sach`) |
| a27: bốn dây 23,26 / 21,26 / 32,94 / 30,23; cách cũ chọn dây 4; 14 đỏ, 1 vàng trên 15 đoạn; trùng nhịp mẹ 43 % | `demo/results/demo_check_showcase.json` → `rows.a27_leadpeakprob.leads.<1–4>.F1`, `.confidence.components`; `analysis/chonkenh_results.json → chon_kenh_theo_quy_tac.cinc.a27.psd` (3 = dây 4) |
| a09 cách cũ 19,35 so với mới 94,25; gate và gate4 cũng chọn dây 1; 13 xanh · 1 vàng · 1 đỏ | `analysis/chonkenh_results.json` → `F1_tung_ban_ghi.cinc.a09`, `chon_kenh_theo_quy_tac.cinc.a09`; `demo/results/demo_check_showcase.json → rows.a09_leadpeakprob` |
| r01: điểm tin bốn dây 0,9976 / 0,9979 / 0,9978 / 0,9982; F1 100,00 / 99,84 / 100,00 / 99,92; 75 đoạn xanh; trùng nhịp mẹ 16 % | `demo/results/demo_check_showcase.json` → `rows.r01_leadpeakprob.leads`, `.confidence` |
| r01: tim bé ≈ 129 nhịp/phút | cùng tệp → `rows.r01_leadpeakprob.fhr_mean` (129,03); đáp án `.n_labels` 644 / `.duration_s` 300 ≈ 128,8. **Tim mẹ ≈ 83 (413 nhịp mẹ) và tỉ số biên độ gai bé / gai mẹ chưa lưu trong tệp JSON nào**: demo tính khi chạy (`demo/app.py: story_texts`, `story_ti_le_bien_do`, ngưỡng 0,5), nhóm đọc lại bằng `story_compute('r01')` ngày 17/09 |
| B2_03 F1 83,91, đèn đỏ | `demo/results/demo_check_showcase.json` → `rows.B2_03_leadpeakprob` |
| 60 bản sạch: PSD 74,28 · gate 80,72 (+6,44 [+2,49; +11,10], Wilcoxon 0,010, Holm 0,051, 16/37/7) · gate4 81,01 (+6,72 [+2,85; +11,18], Holm 0,015, 17/38/5) · peakprob 82,01 (+7,73 [+3,82; +12,41], Holm 0,0039, 19/35/6) · trần 83,60 (+9,32 [+5,01; +14,09]) · luôn lấy dây 1 61,78 | `analysis/dulieu_results.json` → `chon_kenh_60_sach.bang.<psd, gate, gate4, peakprob, oracle, lead0>` (dòng dưới thanh tóm tắt đọc từ đây) |
| gate là quy tắc kế hoạch chọn; thủ tục chọn theo 22 chủ thể; Holm trên 7; peakprob có trong danh sách ghi trước | `analysis/chonkenh_results.json` → `khai_bao_truoc.quy_tac_quyet_dinh_chinh`, `quyet_dinh.tot_nhat_theo_22` (= gate), `khai_bao_truoc.bo_sung_truoc_khi_chay_quy_tac.he_qua`, `khai_bao_truoc.quy_tac_se_thu` |
| peakprob chọn làm mặc định sau khi xem CinC; tệp ghi trước chưa neo git, viết sau khi có F1 từng kênh | `survey/facts_phase4.json` → `B_chon_kenh_7_quy_tac_60_sach.trang_thai`, `.khai_bao_truoc`; `analysis/chonkenh_results.json → quyet_dinh.tot_nhat_theo_cinc_hau_kiem` |
| Cổng trong demo: AUROC trong bản ghi **0,721** [0,517; 0,898], 5 bản CinC a01 a06 a07 a09 a10, đo với mô hình 5 ca; gộp 0,929 không dùng | `analysis/stats_results.json` → `comparisons.gate_auroc_cinc.auroc_TRONG_ban_ghi`, `.auroc_tung_ban_ghi`, `.auroc_diem_tinh_lai`; `analysis/STATS.md` mục 4 |
| Cổng trong demo hiệu chuẩn với mô hình 5 ca; ghép mô hình 22 ca chưa đo lại | `fsqi/train_gate.py` dòng 11–12; `demo/core.py: GATE_NOTE`; `demo/app.py: STORY_GATE_NOTE` |
| Cổng 22 ca (chỉ ở dạng phân tích): **0,934** [0,872; 0,981] trên 11/22 chủ thể | `analysis/gate22_results.json` → `cong.auroc_within_mean`, `.auroc_within_ci`, `.n_records_with_both_classes`; `analysis/GATE22.md` dòng 66, 72 |
| 12 chỉ số: 6 thuần tín hiệu, 4 trên nhịp mạng tìm ra, 2 là xác suất của mạng | `fsqi/gate.py` dòng 61–78, câu lý do của đèn dòng 119–122; `fsqi/fsqi.py` dòng 307–318 |
| `rr_cv` ΔAUROC hoán vị 0,140; `peak_prob_mean` 0,032; mười chỉ số còn lại dưới 0,002 (cổng 22 ca) | `analysis/gate22_results.json` → `cong.permutation_importance_delta_auroc` |
| Đoạn xanh < 0,052, đỏ > 0,540; bản ghi: > 30 % đỏ → THẤP, > 70 % xanh → CAO; bám mẹ từ 60 % → THẤP | `fsqi/gate.py` dòng 93 (`segment_levels`), 107 (`lock >= maternal_lock`), 125–130; ngưỡng đoạn là số demo in trên hình bước 5 (`q1`, `q2` trong `fsqi/gate_classical.pkl`; `demo/results/demo_check_2modes.json → gate.q1` 0,05203, `.q2` 0,53976) |
| Chú thích bước 5: 82 bản đã chấm, 3 bản đèn xanh mà F1 dưới 90, thấp nhất 17,02 | `demo/results/demo_check_2modes.json` → `summary_by_mode.hoc.n_records` (82), `.green_but_F1_below_90` (a52 85,39 · a54 38,79 · a57 17,02), `.by_level.cao.F1_min`; demo đọc lúc mở trang (`demo/app.py: _story_den_xanh`) |
| a57: dây 4, điểm tin 0,951 / 0,976 / 0,984 / 0,985; F1 bốn dây 38,28 / 20,92 / 17,87 / 17,02; TP 20 · FP 67 · FN 128; máy 87 nhịp, đáp án 148; nhịp tim ≈ 86; 14 xanh · 1 vàng · 0 đỏ; trùng mẹ 0 %; luật cứng TRUNG BÌNH, RR CV 0,04 | cùng tệp → `rows.a57_leadpeakprob` (`.lead`, `.lead_scores`, `.leads.<1–4>.F1`, `.metrics`, `.n_beats`, `.n_labels`, `.fhr_mean`, `.confidence.components`, `.confidence_by_mode.luat`); chạy lại bằng mã hiện tại 17/09 ra cùng số |
| a52, a54 thuộc 7 bản nhãn sai đã khai báo | cùng tệp → `cinc_bad_annotation`; `demo/core.py: CINC_BAD_ANN` |
| Thời gian tính toán từng thẻ (dây đã chọn 424 / 135 / 128 / 116 ms; cả 4 dây 1.997 / 513 / 497 / 423 ms; cổng 1.041 / 177 / 161 / 173 ms) | `demo/results/demo_check_showcase.json` → `rows.<bản>_leadpeakprob.latency_ms`, `.latency_all_leads_ms`, `.confidence.components.gate_ms`; `torch_threads` 2, `generated` 12/09/2026 |
| Thời gian trong trình duyệt (mở trang 7,2 s; bấm thẻ 6,95 / 2,77 / 3,48 / 3,40 s; 5 bước 18,22 / 10,03 / 10,93 / 10,52 s) | `demo/screenshots/screenshots_v2.json` (ghi 17/09 22:02) → `mo_trang_toi_r01_s`, `thoi_gian` |
| 6 tab hiện ở 1366 px; hai tab trong nút **⋯** | `demo/screenshots/screenshots_v2.json` → `tab_khi_bat_chuyen_gia`, `tab_trong_menu_tran` |
| 22 kiểm thử chế độ trình bày; 109 kiểm thử toàn bộ (43 + 66); smoke 33 đầu ra | `python -m pytest --collect-only -q demo/test_core.py -k trinh_bay` (22/66) và `python -m pytest --collect-only -q tests/ demo/test_core.py` (109), đếm 17/09/2026 sau lượt sửa thứ ba; `demo/results/smoke_app.json → trinh_bay.n_dau_ra` (33) |
| Bảng dữ liệu mục 6.1 (tần số, độ dài, số dây, nguồn nhãn) | đọc từ đĩa bằng `demo/core.py: dataset_rows` |
| Tệp ví dụ: 4 cột, 30 000 dòng, 1000 Hz, 30 s, µV; nhãn 65 dòng | `demo/assets/vidu_tai_len_META.json`; đếm trực tiếp hai tệp `.csv` |
| Điều kiện tải lên: ≥ 8 s; 50–20 000 Hz; cảnh báo khi hơn 12 cột; cảnh báo nhịp tim ngoài 100–200; lỗi hiện ở dòng trạng thái | `demo/core.py`: `MIN_DURATION_S`, `FS_MIN`, `FS_MAX`, `CONF_RULE` (`fhr_lo` 100, `fhr_hi` 200), `doc_tai_len`; `demo/app.py: run_upload`, `upload_clear` |
| Hộp cảnh báo miền: +0,25 · −0,67 · −1,58 · −2,43 | chữ trên giao diện: `demo/app.py: UP_WARN_DOMAIN`; số: tự tính lại từ `adapt/adapt_results.json → per_record_cinc.*.F1_psd` trên 60 bản sạch (cách tính ở `docs/KICH_BAN_THUYET_TRINH_v2.md` Khối 8c, chú thích nguồn; bảng ở `docs/DE_CUONG_HIEN_TRANG.md` mục (d)) |
| 15 bản CinC nhiễm | `demo/core.py: CINC_LEAK`; `survey/ro_ri_vanlieu.json` |
| Số đã rút — không trích lại | `survey/facts_phase4.json` → `Z_DA_RUT` |

**22 kiểm thử của chế độ trình bày** (`python -m pytest demo/test_core.py -k trinh_bay`): 5 bước mỗi lúc một bước; chế độ
chuyên gia bật/tắt và đủ 8 tab; không có chuỗi cấm trên giao diện; thẻ đọc số từ JSON; a09 hiện cả hai cách chọn; thanh
tóm tắt đủ 6 mục; a02 đèn đỏ và bám mẹ ở bước 5; a02 bước 4 hiện hộp "chọn chưa đúng dây"; a09 không hiện hộp đó; nội
dung thẻ a02, a27 khớp đĩa; chi tiết kỹ thuật đóng sẵn và chân trang ẩn; số kiểu Việt trên hình và bảng; bước 5 có dải
110–160; r01 điểm ngang nhau in 4 chữ số; thẻ có tên ca và mã bản ghi; chú thích bước không nói quá; thanh tóm tắt dính
đáy và thẻ xuống hàng. Năm kiểm thử thêm ở lượt sửa thứ ba: bấm thẻ chồng thì bỏ lượt cũ, lỗi báo ở dòng trạng thái;
tiêu đề và chú thích không nói quá ("một kênh", "không phải lần nào cũng thấy", vạch tím đậm, câu đèn xanh đọc số từ đĩa);
bước 1 nói theo biên độ thật của bản ghi (r01 gai bé to ngang gai mẹ, a09 nhỏ hơn nhiều); bản ghi không có đáp án không
nói sai; thanh tóm tắt dính thật (CSS `overflow` của `.gradio-container`) và tự cuộn có điều kiện.

## Phụ lục B — đối chiếu chuỗi giao diện

Ngày 17/09/2026, mọi chuỗi nghiêng trong tài liệu này được đối chiếu tự động bằng script `dsync_doi_chieu.py`
(chạy ngoài kho mã, trong thư mục tạm của phiên làm việc). Script làm ba việc:

1. Đọc mọi chuỗi trong `demo/app.py`, `demo/core.py` và (từ lượt D-sync2) `fsqi/gate.py`, nơi có câu lý do của đèn, bằng
   `ast` (hằng chuỗi, f-string, chuỗi nối bằng `+`), bỏ thẻ HTML và dấu `**`.
2. Chạy đúng các hàm của chế độ trình bày (`story_compute`, `story_card_html`, `story_loading_html`, `story_summary_html`)
   cho r01, a09, a02, a27 để lấy chuỗi **hiển thị thật**, kể cả số (script `dsync_render.py`, `RELYFETAL_AUTORUN=0`,
   không mở cổng mạng).
3. Với từng chuỗi nghiêng: khớp **nguyên văn** trong mã, hoặc khớp **chuỗi hiển thị thật**, hoặc khớp **khuôn** (bỏ số,
   phần chữ nằm đúng thứ tự trong một chuỗi của mã). Dấu `…` được coi là chỗ điền số.

Lần chạy trước lượt sửa thứ ba của demo (17/09, trên bản tài liệu cũ, với chuỗi hiển thị vừa sinh lại): 280 chuỗi nghiêng,
khớp 272, **không khớp 8** (nhãn ô F1 cũ "độ đúng", dòng mô tả thẻ CinC, chú thích bước 2, 3, 4, 5, tiêu đề hình bước 3,
chữ đường trung bình khi đèn đỏ) và 1 chỉ khớp khuôn (cảnh báo nhịp tim ngoài khoảng). Các chỗ đó đã sửa ở trên.

Kết quả lần chạy cuối (17/09/2026, sau D-sync2): **329 chuỗi nghiêng, khớp 329** (279 nguyên văn trong mã, 50 khớp chuỗi
hiển thị thật, 0 chỉ khớp khuôn), **không khớp 0**. Chuỗi trong ngoặc kép thường là lời thoại, không bắt buộc khớp.
Khi `demo/app.py`, `demo/core.py` hoặc `fsqi/gate.py` đổi chữ, chạy lại hai script trước khi in tài liệu này.

---

**Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.**
