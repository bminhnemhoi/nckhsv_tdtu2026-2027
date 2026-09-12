# S2 — Khảo sát dữ liệu đa trung tâm cho fQRS thai đơn kênh

Ngày khảo sát: 2026-09-11. Mọi URL trong tài liệu này đã được `curl` kiểm tra trả HTTP 200 trong
phiên làm việc. Mọi con số về định dạng file đều lấy từ header/thư mục **tải thật về**, không lấy
từ trí nhớ.

Bối cảnh: reviewer P1 kết luận đóng góp thật duy nhất là phân rã có kiểm soát, và điểm yếu lớn
nhất là **toàn bộ 22 sản phụ huấn luyện đến từ một bệnh viện (Silesia, Ba Lan)**. Tài liệu này
trả lời: có thể mua thêm được bao nhiêu sự đa dạng bằng dữ liệu công khai, và với giá nào.

---

## 0. Kết luận đi thẳng vào việc

1. **Không có bộ dữ liệu aECG công khai nào khác trên thế giới có sẵn nhãn fQRS thật.**
   Toàn bộ nhãn fQRS công khai hiện hữu nằm trong ba nguồn, và **cả ba đều truy về cùng một
   nhóm nghiên cứu Silesia (Ba Lan)** hoặc dẫn xuất từ nó.
2. **NInFEA và NIFEADB — hai bộ được kỳ vọng nhất — đều KHÔNG phân phối nhãn fQRS.**
   Đây là phát hiện quan trọng nhất của S2 và nó lật ngược giả định trong
   `model/download_more.py` (file đó ngầm định sẽ tải được `.fqrs`/`.qrs` cho hai bộ này).
3. Cộng tất cả nhãn fQRS công khai lại được **≈ 27 thai kỳ độc lập, ≈ 6 giờ tín hiệu,
   1–2 hệ ghi**. Con số này **không đủ cho một benchmark A\*** (so sánh: PTB-XL 18 869 bệnh nhân,
   MIMIC-IV-ECG 174 000). "FetalBench" chỉ khả thi nếu nhóm **tự tạo nhãn** cho NInFEA/NIFEADB —
   và đó mới chính là đóng góp có thể bán được ở NeurIPS D&B.
4. Cảnh báo `ecgca* đều từ 1 người` trong `download_more.py` **gắn nhầm bộ**: `ecgca*` thuộc
   `nifecgdb`, không thuộc NIFEADB. Cần sửa (mục 2.3).

---

## 1. Tiến độ tải (chỉ kiểm tra, không chạy lại)

Tiến trình nền do phiên khác khởi động vẫn đang chạy, log
`D:/NCKHSV2026-2027/model/data/_dl_more.log`:

| Bộ | Đích | Trạng thái lúc 22:28 | Ghi chú |
|---|---|---|---|
| `cinc75` (CinC 2013 set-a, 75 bản ghi) | `benchmark_dpss/pcdb/` | **175/225 file, 28,3 MB, 0 lỗi** — còn ~3 phút | 63/75 `.dat` đã có; 30 file dùng lại cache từ 10 bản ghi cũ |
| `nifeadb` | `model/data/nifeadb/` | **CHƯA khởi động** | tiến trình chỉ chạy `--only cinc75` |
| `ninfea` | `model/data/ninfea/` | **CHƯA khởi động** | 2,0 GB, nên tải riêng |

Trong khuôn khổ S2 tôi đã tải thủ công **mẫu kiểm tra định dạng**: NInFEA bản ghi `1`, `2`, `3`
(2 × `.dat` + 3 × `.hea`, 15,8 MB) và NIFEADB `ARR_01`, `NR_01` (+ 4 `.hea`), đủ để viết và
**chạy thật** hai loader.

---

## 2. (a) NInFEA — physionet.org/content/ninfea

**Nguồn:** Sulas E, Urru M, Tumbarello R, Raffo L, Sameni R, Pani D. *A non-invasive multimodal
foetal ECG–Doppler dataset for antenatal cardiology research.* Scientific Data 2021;**8**:30.
DOI [10.1038/s41597-021-00811-3](https://doi.org/10.1038/s41597-021-00811-3) ·
[PMC7838287](https://pmc.ncbi.nlm.nih.gov/articles/PMC7838287/) ·
[PhysioNet](https://physionet.org/content/ninfea/1.0.0/)

| Hạng mục | Giá trị (đã kiểm chứng) |
|---|---|
| Số mục ghi | **60** |
| Số sản phụ | **39** (⇒ 60 mục ghi **không** độc lập; ánh xạ mục ghi→người **không được công bố**) |
| Tuổi thai | **tuần 21–27** (tam cá nguyệt 2 — sớm hơn hẳn Silesia B1 và CinC 2013) |
| Kênh bụng | **24 đơn cực** `uni_abd1..24` |
| Kênh khác | 3 lưỡng cực ngực mẹ `bi_tho1..3`, `matrsp` (hô hấp mẹ), `saw`, `sync`, `dc1..dc4` → **34 kênh** trong `.hea` |
| Tần số | **2048 Hz**, 22 bit (71,5 nV), băng thông 0–550 Hz |
| Độ dài | trung bình **30,6 s ± 20,6 s**, dải 7,50–119,80 s |
| Kích thước | **2,0 GB** giải nén (792,9 MB zip); riêng `wfdb_format/` ≈ 600 MB |
| Giấy phép | Open Data Commons Attribution License v1.0 |

### Định dạng nhãn tham chiếu — câu trả lời cho câu hỏi trọng tâm

**Nhãn đến từ Doppler xung (PWD), KHÔNG từ ECG ngực mẹ — và KHÔNG được phân phối.**

Đã liệt kê toàn bộ `wfdb_format_ecg_and_respiration/`: **chỉ có `<n>.dat` và `<n>.hea`**, không có
một file `.qrs`/`.fqrs`/`.atr` nào; thư mục đó thậm chí không có `RECORDS` (404). Thư mục gốc chỉ
gồm `bin_format_ecg_and_respiration/`, `code/`, `pwd_images/`, `wfdb_format_ecg_and_respiration/`,
`LICENSE.txt`, `RECORDS`, `SHA256SUMS.txt`.

Sự thật tham chiếu trong bài là **đỉnh V (vận động thất trái) trên ảnh PWD, do chuyên gia gán nhãn
bằng mắt**. Đây là mốc **cơ học**, không phải mốc **điện học**. Muốn có nhãn phải: chuyển
`code/envelope_extraction.m` sang Python để trích bao hình từ `pwd_images/<n>.bmp`, dùng kênh
`sync` căn chỉnh ảnh↔ECG, rồi gán nhãn đỉnh V có chuyên gia duyệt.

### Dung sai cộng đồng dùng cho bộ này

Hai con số, **không được lẫn**:

* **200 ms** — trễ điện-cơ (electromechanical delay) giữa R điện và V cơ học; bài dùng ngưỡng
  "khoảng cách hợp lý về lâm sàng < 200 ms" để ghép cặp R↔V.
* **50 ms** — cửa sổ gán mốc QRS trong phạm vi đó.

⇒ **F1 trên NInFEA không so trực tiếp được với F1 trên ADFECGDB / Silesia B2** (dung sai 50 ms so
với dFECG trực tiếp). Nếu báo cáo chung một bảng phải tách cột "nguồn nhãn" và "dung sai".

Kết quả tham chiếu của chính tác giả (technical validation, dò QRS thai): trung vị
**accuracy 0,79 / Se 0,97 / PPV 0,81**; trích được fECG trên **95,5 %** đoạn tín hiệu.
Đây là mốc hợp lý để so — và nó thấp hơn nhiều con số 97 % của nhóm trên Silesia, đúng như kỳ vọng
khi đổi hệ ghi.

### Định dạng file — đã kiểm chứng byte-chính-xác

```
1 34 2048 57490
1.dat 32 1119216.6963(598581736)/uV 0 0 570611155 -418 0 uni_abd1
```
WFDB format 32 = **int32 little-endian**, 34 kênh xen kẽ theo mẫu, `.dat` không header.
Kiểm chứng: 57 490 × 34 × 4 = **7 818 640 byte = Content-Length. KHỚP.**
`physical = (raw − baseline)/gain` [µV]. Các kênh `dc1..dc4`, `sync` có `gain=1`,
`baseline=−2147483647` → giá trị vật lý vô nghĩa, chỉ dùng `sync` ở dạng mẫu thô.

**Loader:** `D:/NCKHSV2026-2027/model/ninfea_loader.py` — đã chạy thật trên bản ghi 1 và 2:

```
1: 34 kênh @ 2048 Hz, 28.07 s | .dat 7818640 byte, dự tính 7818640 -> KHỚP
   abd(24, 28072) mV biên độ p2p trung vị = 3.069, fqrs=None
```

`fetal_qrs()` cố tình **ném `NotImplementedError`** kèm hướng dẫn 4 bước, để không bao giờ có
code gọi im lặng coi "không có đỉnh".

---

## 3. (b) NIFEADB — Non-Invasive Fetal ECG Arrhythmia Database

**Nguồn:** Behar JA, Bonnemains L, Shulgin V, Oster J, Ostras O, Lakhno I. *Noninvasive fetal
electrocardiography for the detection of fetal arrhythmias.* Prenat Diagn 2019;**39**(3):178–187.
DOI [10.1002/pd.5412](https://doi.org/10.1002/pd.5412) ·
[PhysioNet](https://physionet.org/content/nifeadb/1.0.0/) · DOI 10.13026/C2CT0S

| Hạng mục | Giá trị (đã kiểm chứng trên `.hea` tải về) |
|---|---|
| Số bản ghi | **26** = 12 loạn nhịp (`ARR_01..12`) + 14 nhịp thường (`NR_01..14`) |
| Kênh | **6**: `ECG` (1 đạo trình **ngực mẹ**) + `Abdomen_1..5` (4–5 đạo trình bụng) |
| Tần số | **500 hoặc 1000 Hz**, khai trong header **từng** bản ghi — không được giả định |
| Độ dài | ~**600 000 mẫu @1000 Hz ≈ 10 phút**/bản ghi |
| Định dạng | WFDB format 16 (int16 LE), 6 kênh xen kẽ; gain 10⁴–10⁵ đơn vị/mV |
| Kích thước | 177,7 MB |
| Giấy phép | Open Data Commons Attribution License v1.0 |

### Bản ghi nào có chú thích fQRS thật? — **KHÔNG BẢN GHI NÀO**

Liệt kê toàn bộ thư mục PhysioNet 1.0.0: chỉ có 26 × (`.dat` + `.hea`), `RECORDS`,
`HEADER.shtml`, `SHA256SUMS.txt`. **Không có `.qrs`/`.fqrs`/`.atr`, và không tồn tại file
`ANNOTATORS`** (so sánh: `adfecgdb` và `nifecgdb` đều có `ANNOTATORS`). Trang mô tả cũng không hề
nhắc tới chú thích.

⇒ **Không thể báo cáo F1/Se/PPV có giám sát trên NIFEADB.** Ba cách dùng hợp lệ:
(1) đánh giá **không nhãn** — độ ổn định của cổng từ chối, độ lệch miền;
(2) **kiểm tra định tính trên loạn nhịp** — 12 bản ghi `ARR_*` là nguồn biến thiên RR nằm ngoài
mọi bộ huấn luyện hiện có (Silesia và CinC 2013 đều gần như chỉ có nhịp xoang);
(3) **tự chú thích** (cần chuyên gia) rồi công bố nhãn như một đóng góp riêng.

### Bản ghi nào cùng một sản phụ?

Trang PhysioNet và `HEADER.shtml` **không khẳng định** mỗi bản ghi là một sản phụ khác nhau; bài
Behar 2019 mô tả cohort theo thai nhi. **Chưa đối chiếu được bảng chẩn đoán trong bài** (cần lấy
bảng đó trước khi đếm chủ thể). Loader trả `subject_id = tên bản ghi` kèm
`subject_id_is_assumed=True`. **Không được đếm 26 như 26 chủ thể độc lập** trong bất kỳ phân tích
cụm/bootstrap nào mà không có dẫn chứng từ bài.

### Sửa lỗi trong `download_more.py`

Cảnh báo hiện tại:

> `CANH BAO: cac ban ghi ecgca* deu tu MOT san phu`

**gắn nhầm bộ.** `ecgca*` là quy ước đặt tên của `nifecgdb` (mục 4.3), không phải NIFEADB
(dùng `ARR_*`/`NR_*`). Cảnh báo đúng cho `nifecgdb` — và cần thay cảnh báo NIFEADB bằng
"bộ này không có nhãn fQRS".

**Loader:** `D:/NCKHSV2026-2027/model/nifeadb_loader.py` — đã chạy thật:

```
ban ghi day du   : 2/26  ['ARR_01', 'NR_01']
file nhan tim duoc: KHONG CO (dung nhu mong doi)
  fs=1000 Hz, 6 kenh : 2 ban ghi
  ARR_01: abd(5, 600052) 600s ... fqrs=None
```

---

## 4. (c) CinC 2013 set-a — 75 bản ghi

[PhysioNet challenge-2013](https://physionet.org/content/challenge-2013/1.0.0/) ·
[archive](https://archive.physionet.org/physiobank/database/challenge/2013/)

* **set-a**: 75 bản ghi (25 + 50 bổ sung), 4 kênh bụng, 1000 Hz, **1 phút**/bản ghi,
  **có** nhãn `.fqrs` công khai. Đây là tập duy nhất có nhãn.
* **set-b**: 100 bản ghi, tín hiệu công khai, **nhãn bị giữ lại** (dùng chấm sự kiện 4/5/6).
* **set-c**: tập ẩn, **không phát hành**.
  ⇒ **Không có cách nào mở rộng nhãn CinC 2013 ra ngoài 75 bản ghi set-a.**

### Nguồn gốc quy tắc loại 7 bản ghi — ĐÃ TRUY ĐƯỢC

Danh sách `a33 a38 a47 a52 a54 a71 a74` **không nằm trong bất kỳ tài liệu chính thức nào của
PhysioNet** (đã grep cả 3 trang chính thức: không khớp). Chuỗi trích dẫn thật:

> Zhong W. và cs., *A deep learning approach for fetal QRS complex detection*,
> Physiol Meas 2018;**39**:045004, DOI [10.1088/1361-6579/aab297](https://doi.org/10.1088/1361-6579/aab297):
> "As suggested in **Behar et al. (2013)**, seven AECG recordings (a33, a38, a47, a52, a54, a71 and
> a74) are discarded because of **inaccurate reference annotations**."

Nguồn gốc là **Behar J, Oster J, Clifford GD, "Non-invasive FECG extraction from a set of abdominal
sensors", Computing in Cardiology 2013;40:297–300** — tức là chính nhóm đã thiết kế thử thách.
Zhong 2018 chỉ là bên truyền lại.

**Hệ quả cho bài báo:** biến thể 6 bản ghi (bỏ `a47`) cũng lưu hành rộng trong tài liệu. Vì vậy
quy tắc loại **phải khai báo trước**, ghi rõ "7 bản ghi theo Behar 2013 (CinC 40:297), truyền qua
Zhong 2018", và **nên báo cáo cả hai biến thể 69 và 68 bản ghi** để reviewer không thể nói nhóm
chọn ngưỡng có lợi.

**Cảnh báo rò rỉ chưa ai nêu:** set-a là tập **hỗn hợp nguồn gốc** — một phần dẫn xuất từ các bộ
sẵn có (bao gồm dữ liệu nhóm Silesia) và một phần mô phỏng. PhysioNet **không công bố bản đồ bản
ghi→nguồn→sản phụ**. Do đó con số CinC 2013 zero-shot **chưa chắc là zero-shot thật**. *(Sửa
12/09/2026: chỗ này trước viết "zero-shot 90,34" trên 10 bản ghi; **90,34 đã bị rút** và nay đã chạy
đủ 75 bản ghi, con số mù nhãn là **79,40**. Cảnh báo về nguồn gốc hỗn hợp vẫn nguyên giá trị và nay
áp cho cả 75 bản ghi.)* Đây là rủi ro nghiêm trọng ngang với vòng lặp tự đồng ý
mà P1 đã chỉ ra, và cần một mục hạn chế riêng.

---

## 5. (d) Toàn bộ bộ dữ liệu aECG công khai trên thế giới

Tất cả URL dưới đây đã kiểm tra trả HTTP 200 ngày 2026-09-11.

| # | Bộ | Nguồn/nhóm | Chủ thể | Bản ghi × độ dài | Tuổi thai | Nhãn fQRS? | Giấy phép | Tải được? | URL |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **ADFECGDB** Abdominal & Direct Fetal ECG DB | Silesia Univ. of Technology, Ba Lan | **5** sản phụ | 5 × 5 phút, 1000 Hz, 4 bụng + 1 **dFECG da đầu** | 38–41 tuần | **CÓ** (`.edf.qrs`, từ dFECG) | ODC-By v1.0 | có, ~10 MB | https://physionet.org/content/adfecgdb/1.0.0/ |
| 2 | **Silesia / FEPL** (Matonia 2020) | cùng nhóm Silesia | **22** (B1 10 + B2 12) | B1 10×20 ph; B2 12×5 ph, 500 Hz | B1 thai kỳ, B2 chuyển dạ | **CÓ** — B2 từ dFECG (tin cậy), **B1 nhãn gián tiếp** | CC-BY 4.0 | có, 195 MB figshare | https://doi.org/10.6084/m9.figshare.c.4740794 |
| 3 | **CinC Challenge 2013 set-a** | hỗn hợp, một phần dẫn xuất Silesia + mô phỏng | **không công bố** | 75 × 1 phút, 1000 Hz, 4 bụng | không công bố | **CÓ** (`.fqrs`) — 7 bản ghi bị loại | ODC-By v1.0 | có, ~36 MB | https://physionet.org/content/challenge-2013/1.0.0/ |
| 4 | **NInFEA** | Univ. Cagliari, **Ý** | **39** sản phụ / 60 mục ghi | 60 × 30,6 s tb, **2048 Hz, 24 bụng** | **21–27 tuần** | **KHÔNG** (chỉ ảnh PWD + script bao hình) | ODC-By v1.0 | có, 2,0 GB | https://physionet.org/content/ninfea/1.0.0/ |
| 5 | **NIFEADB** | Technion + Kharkiv, **Israel/Ukraine/Pháp** | ≤26, chưa xác minh | 26 × ~10 ph, 500/1000 Hz, 4–5 bụng | xem bài | **KHÔNG** | ODC-By v1.0 | có, 178 MB | https://physionet.org/content/nifeadb/1.0.0/ |
| 6 | **NIFECGDB** Non-Invasive Fetal ECG DB | PhysioNet (bộ cổ) | **1 sản phụ** | 55 bản ghi × ~5 ph, 1000 Hz, 2 ngực + 3 bụng | tuần ~21–40, ghi hàng tuần | **KHÔNG** — `.edf.qrs` là **QRS MẸ** | ODC-By v1.0 | có, ~150 MB | https://physionet.org/content/nifecgdb/1.0.0/ |
| 7 | **OB-1 Fetal ECG DB** | Oriol/Bennet/Aggarwal, Mỹ | **1** (bản mẫu) | 1 bản ghi × 5,7 giờ, 500 Hz | chuyển dạ | có `.qrs` nhưng **"unaudited"** | ODC-By v1.0 | có, ~40 MB | https://physionet.org/content/ob1db/1.0.0/ |
| 8 | **FECGSYNDB** | Andreotti/Behar, mô phỏng | **0 người thật** | 1 750 bản ghi mô phỏng, 32 kênh bụng | — | có (máy sinh) | ODC-By v1.0 | có, rất lớn | https://physionet.org/content/fecgsyndb/1.0.0/ |
| 9 | **ST annotations of ADFECGDB** | IEEE DataPort | (nhãn thêm cho #1) | — | — | nhãn **ST**, không phải fQRS mới | xem trang | có | https://ieee-dataport.org/documents/st-annotations-adfecgdb-database |
| 10 | **DaISy foetal ECG** | KU Leuven, Bỉ | **1** | 1 bản ghi × **10 s**, 250 Hz, 5 bụng + 3 ngực | — | **KHÔNG** | dùng cho nghiên cứu | có, vài KB | https://homes.esat.kuleuven.be/~smc/daisy/daisydata.html |
| 11 | **OSET** (Sameni) | Bộ công cụ + dữ liệu mẫu | vài | rời rạc, không chuẩn hoá | — | **KHÔNG** hệ thống | xem repo | có | https://github.com/alphanumericslab/OSET |

**Về "bộ của Xu 2026":** đã tìm — Xu và cs. 2026 (WTA-Net, IEEE JBHI) là **bài phương pháp**, tra
cứu không thấy bất kỳ thông báo phát hành dữ liệu công khai nào kèm theo. **Không nên viện dẫn**
cho tới khi xác minh được mục Data Availability của bài.

**Đã loại khỏi bảng vì không phải aECG:** `fpcgdb`, `simfpcgdb`, `sufhsdb`, `fetalheartsounddata`
(đều là tim thai âm thanh — phonocardiogram, không dùng được cho nhiệm vụ này).

---

## 6. (e) Bảng tổng hợp — gộp tất cả nhãn fQRS công khai được bao nhiêu?

### Chỉ tính nhãn fQRS THẬT (con người, không mô phỏng)

| Bộ | Chủ thể độc lập | Giờ tín hiệu | Hệ ghi | Nguồn nhãn |
|---|---|---|---|---|
| ADFECGDB | 5 | 0,42 h | KOMPOREL (Silesia) | dFECG da đầu |
| Silesia B2 (chuyển dạ) | 12 | 1,00 h | KOMPOREL (Silesia) | dFECG da đầu |
| Silesia B1 (thai kỳ) | 10 | 3,33 h | KOMPOREL (Silesia) | **gián tiếp** (khử ECG mẹ + chuyên gia duyệt) |
| CinC 2013 set-a (69 sau loại) | **không xác định**, một phần trùng nguồn trên | 1,15 h | hỗn hợp / không công bố | hỗn hợp, 7 bản ghi sai |
| **Tổng (thận trọng)** | **≈ 27 thai kỳ độc lập** | **≈ 5,9 giờ** | **1 hệ chính + phần hỗn hợp không rõ** | 3 loại nhãn khác nhau |

Số 27 đã là **lạc quan**: nó giả định ADFECGDB 5 và Silesia B1/B2 22 là 27 người khác nhau, điều
chưa được kiểm chứng — cả ba đến từ **cùng một bệnh viện, cùng một nhóm, cùng một hệ ghi**, và
repo đã tự ghi nhận khả năng rò rỉ giữa ADFECGDB và Silesia (`silesia_eval.json['leak_check']`).
Nếu có trùng, con số thật có thể xuống **22**.

### Nếu tính cả dữ liệu KHÔNG nhãn (tiềm năng sau khi tự chú thích)

| | Chủ thể | Giờ | Hệ ghi / quốc gia |
|---|---|---|---|
| Đã có nhãn | ≈27 | 5,9 h | 1 (Ba Lan) |
| NInFEA | +39 | +0,5 h | +1 (Ý, 24 kênh, 2048 Hz, tuần 21–27) |
| NIFEADB | +≤26 | +4,3 h | +1 (Ukraine/Israel, có **loạn nhịp**) |
| NIFECGDB | +1 | +4,6 h | +1 (dọc theo thời gian, tuần 21–40) |
| **Trần lý thuyết** | **≈ 93 thai kỳ** | **≈ 15 giờ** | **4 hệ ghi, 4 quốc gia** |

### Đủ cho một benchmark A\* không? — **KHÔNG, ở dạng hiện tại**

**Không đủ, vì bốn lý do định lượng:**

1. **Quy mô.** ≈93 chủ thể / 15 giờ là hai bậc độ lớn dưới các benchmark ECG được chấp nhận ở
   NeurIPS D&B (PTB-XL 18 869 bệnh nhân; MIMIC-IV-ECG ~174 000). Với n=93, sai số chuẩn của F1
   ở mức chủ thể vẫn ~±2–3 điểm — tức là **vẫn không phân biệt được 8 kiến trúc** (đúng kết quả
   +0,41, p=0,70 mà nhóm đã thấy).
2. **Nhãn không đồng nhất.** Bốn loại sự thật tham chiếu (dFECG da đầu / gián tiếp / PWD cơ học /
   mô phỏng) với **ba dung sai khác nhau** (50 ms, 50 ms, 200 ms điện-cơ). Một benchmark trộn
   chúng mà không hiệu chỉnh sẽ bị reviewer bác ngay.
3. **Không có tập kiểm thử giữ kín.** set-b/set-c của CinC không phát hành; mọi bộ còn lại đều
   công khai hoàn toàn ⇒ không thể chống overfitting theo kiểu leaderboard.
4. **Mất cân bằng tuổi thai.** Nhãn thật chỉ tập trung ở tuần 38–41 (ADFECGDB, Silesia B2) và
   thai kỳ muộn (B1); tuần 21–27 **hoàn toàn không có nhãn** (đúng chỗ NInFEA nằm). Ứng dụng lâm
   sàng giá trị nhất lại là sàng lọc sớm.

**Nhưng có một con đường thật.** Khoảng trống ở mục (2) và (4) chính là **sản phẩm**:

> Đóng góp bán được không phải "thêm một mô hình", mà là **bộ nhãn fQRS đầu tiên cho NInFEA
> (39 sản phụ, tuần 21–27, 2048 Hz, 24 kênh) và cho NIFEADB (26 bản ghi, có loạn nhịp)**, kèm
> nghi thức hiệu chỉnh dung sai điện-cơ 200 ms ↔ 50 ms giữa nhãn PWD và nhãn dFECG.

Việc đó biến "1 bệnh viện" thành "4 hệ ghi, 4 quốc gia", đưa số thai kỳ có nhãn từ 27 lên ~93,
và lần đầu phủ tam cá nguyệt 2. Đó là đóng góp dạng Datasets & Benchmarks thật sự, và nó cũng
là thứ duy nhất trong hồ sơ hiện tại có thể gọi là mới.

---

## 7. Việc cần làm tiếp (xếp theo tỉ lệ giá trị/công sức)

1. **Sửa `model/download_more.py`**: (a) cảnh báo `ecgca*` chuyển sang `nifecgdb`; (b) bỏ dòng
   ngầm định NIFEADB/NInFEA có `.qrs`/`.fqrs` — vòng lặp `files += [rec + e for e in (...)]`
   hiện sẽ sinh 404 cho `.atr/.qrs/.fqrs` ở cả hai bộ (vô hại nhưng gây hiểu nhầm trong log).
2. **Chạy `--only nifeadb`** (178 MB, rẻ) để có ngay 12 bản ghi loạn nhịp làm stress-test
   không nhãn cho cổng từ chối — đây là thí nghiệm rẻ nhất cho phản biện "chỉ nhịp xoang".
3. **Lấy bảng bổ sung của Sci Data 8:30** để có ánh xạ mục ghi→sản phụ của NInFEA; không có bảng
   đó thì mọi bootstrap theo chủ thể trên NInFEA đều không hợp lệ.
4. **Chuyển `envelope_extraction.m` sang Python** — đây là chặng chặn của toàn bộ hướng
   "FetalBench".
5. **Khai báo trước** quy tắc loại CinC (Behar 2013 qua Zhong 2018) và báo cáo cả 69 lẫn 68 bản ghi.
6. **Thêm mục hạn chế** về nguồn gốc hỗn hợp của CinC set-a: điểm zero-shot (nay là **79,40** trên đủ
   75 bản ghi; số cũ 90,34 đã rút) chưa chắc là zero-shot thật.

---

## 8. File đã tạo trong nhiệm vụ này

* `D:/NCKHSV2026-2027/model/ninfea_loader.py` — đã chạy thật, xác minh kích thước `.dat` khớp
  byte-chính-xác; `fetal_qrs()` ném lỗi có hướng dẫn.
* `D:/NCKHSV2026-2027/model/nifeadb_loader.py` — đã chạy thật; `format_check()` tự xác nhận
  "không có file nhãn".
* `D:/NCKHSV2026-2027/survey/scout_datasets.md` — tài liệu này.
* Mẫu kiểm tra định dạng: `model/data/ninfea/wfdb_format_ecg_and_respiration/{1,2}.{dat,hea}`,
  `3.hea`; `model/data/nifeadb/{ARR_01,ARR_05,NR_01,NR_10}.hea` + `{ARR_01,NR_01}.dat`;
  `model/data/_scout/ecgca102.edf{,.qrs}` (dùng để chứng minh nhãn `nifecgdb` là **QRS mẹ**:
  375 nhịp, RR trung vị 0,695 s → **86,3 bpm**).
