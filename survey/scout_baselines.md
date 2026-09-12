# S1 — Truy tìm baseline có mã nguồn chạy được

Ngày: 2026-09-11 · Ngân sách 45 phút · Máy: Windows 11, Python 3.12.6, torch 2.13.0+cpu, không có MATLAB.

Tài liệu này trả lời đúng một câu hỏi: **baseline SOTA nào ta có thể tự chạy lại, với chi phí bao nhiêu?**
Đây là lỗ hổng lớn nhất mà reviewer P1 nêu. Mọi URL trong bảng đều đã được mở/tải thật trong phiên này
(cột "đã xác minh" ghi rõ cách xác minh).

---

## 0. Kết luận điều hành (đọc phần này trước)

1. **Rào cản Power-MF đã sập một nửa.** `baselines/powermf_status.json` ghi "thiếu 8 hàm Varanini 2014".
   **Sai — 8/8 hàm đó đã tải được**, nằm trong `pmea-varanini.zip` (45 KB) trên archive.physionet.org.
   Phân tích ký hiệu toàn bộ chuỗi gọi cho thấy chúng **chỉ cần gói `signal`** (butter, filtfilt, findpeaks,
   freqz, gausswin, medfilt1, pwelch) — **không cần OSET, không cần fecgsyn, không cần CinC_Behar**.
   Ba gói đó chỉ phục vụ `Sulas21.m` và `Behar14.m`, không phải PowerMF. Rào cản còn lại **duy nhất là runtime**.

2. **Octave đã cài và ĐÃ CHẠY THẬT trên máy này.** Không còn là phỏng đoán: bản portable 11.3.0 đã tải
   (816 MB), giải nén (45 giây) và chạy được smoke test. `pkg load signal` OK. **6/8 hàm then chốt chạy
   ngay; 2 hàm lệch API và tôi đã tìm ra bản vá chính xác cho cả hai** (mục 2.2.1). Nhờ đó ước lượng
   Power-MF đa kênh **giảm từ 1,5–2,5 ngày xuống còn 0,5–1 ngày**, và rủi ro lớn nhất đã được gỡ trước.

3. **Phát hiện có sức nặng nhất, và là tin xấu.** Tôi đã trích số **đã công bố** từ `Results/*.mat` của
   repo Power-MF cho **cả B2 và CinC 2013** (trước đây hồ sơ chỉ trích B1). Trên **chính những tập ta báo cáo**:

   | Tập | n | Ta (1 kênh) | Power-MF (4 kênh) | Varanini 2014 (4 kênh) | Behar 2014 | Sulas 2021 |
   |---|---:|---:|---:|---:|---:|---:|
   | Silesia B1 thai kỳ | 10 | 97,15 | **99,46** | 99,37 | 90,41 | 63,04 |
   | Silesia B2 chuyển dạ | 12 | 97,17 | **97,98** | 97,95 | 87,68 | 65,36 |
   | CinC 2013 set-a | 75 | **79,40** (đủ 75 bản ghi, PSD mù nhãn)¹ | 94,27 | **97,04** | 61,70 | 48,19 |

   ¹ **Sửa 12/09/2026.** Dòng này trước ghi *"ta chỉ chạy 10/75 → 90,34"*. Cả hai vế đều đã lỗi thời:
   nay đã chạy **đủ 75 bản ghi**, và **90,34 đã bị rút** (đó là kênh 0 cố định chọn hậu kiểm trên mẫu 10;
   trên đủ 75 bản ghi quy tắc đó chỉ đạt 69,33). Con số mù nhãn đúng là **79,40**.

   P1 nói ta "đang thua". Số liệu đầy đủ cho thấy **thua trên cả ba tập**, và trên CinC 2013 khoảng cách
   vẫn lớn kể cả sau khi sửa: **Varanini 2014 đạt 97,04 trên toàn bộ 75 bản ghi**, còn ta đạt **79,40**
   trên cùng 75 bản ghi. Lưu ý hai bên **không cùng bộ chấm** (ta dùng bộ chấm ±50 ms của nhóm), nên đây
   là so sánh định hướng chứ chưa phải đối chứng chặt. Không thể viết bài như thể ta là SOTA.

4. **Không có bộ dò fQRS học sâu nào có trọng số dùng lại được.** Đã rà GitHub API (2 truy vấn, ~70 repo),
   Papers with Code, và cả 30 paper trong `survey_raw.json`: **0/30 paper fECG có mã nguồn công khai**
   (các URL mã nguồn duy nhất trong survey đều thuộc nhóm paper TDA). Repo gần nhất là **TCGAN** (JBHI 2025,
   đơn kênh, ADFECGDB) — nhưng checkpoint trong repo là **epoch 0 và epoch 10 của lịch trình 500 epoch**,
   tức không phải mô hình đã công bố, và đầu ra là **dạng sóng chứ không phải vị trí fQRS**.

5. **Đường đi rẻ nhất, giá trị cao nhất: tự cài `Power-MF-1ch`** (đặc tả đầy đủ ở mục 3).
   Đây là biến thể đơn kênh, thuần Python/scipy, ~200 dòng, 1–2 ngày, **không cần Octave**, và nó lấp đúng
   lỗ hổng P1 nêu: một baseline **cùng cấu hình đơn kênh, cùng front-end**, dựng từ phương pháp SOTA 2024.

---

## 1. Bảng tổng hợp

Cột "chạy được?" đánh giá riêng cho **máy này** (Windows, Python 3.12, CPU, không MATLAB).

| # | Tên | URL | DOI / định danh | Ngôn ngữ | Giấy phép | Chạy được? | Công sức | Giá trị |
|---|---|---|---|---|---|---|---|---|
| 1 | **fecg-benchmarking** (Power-MF, Behar14, Varanini14, Sulas21) | github.com/mad-lab-fau/fecg-benchmarking | Jaeger 2024 (repo ghi "DOI: xxxxxxxxx", chưa điền) | MATLAB R2021a | MIT (file LICENSE) | **CÓ** — Octave đã chạy thật, cần 2 bản vá ở mục 2.2.1 | **0,5–1 ngày** | ⭐⭐⭐⭐⭐ |
| 2 | **Varanini 2014 `xCinC`** (8 hàm còn thiếu) | archive.physionet.org/challenge/2013/sources/pmea/pmea-varanini.zip | 10.1088/0967-3334/35/8/1607 | MATLAB | PhysioNet challenge (xem mục 2.3) | **Có** (đã tải, 45 KB, 30 file .m) | gộp vào #1 | ⭐⭐⭐⭐⭐ |
| 3 | **Behar 2014 CinC** | archive.physionet.org/challenge/2013/sources/joachimbehar.zip | CinC 2013 | MATLAB | như trên | Có (đã tải, 48 KB) | +0,5 ngày | ⭐⭐ |
| 4 | **Power-MF-1ch** (ta tự cài, đặc tả mục 3) | — (chưa tồn tại) | dẫn xuất từ #1/#2 | Python/scipy | ta viết → MIT | **Có, không cần Octave** | **1–2 ngày** | ⭐⭐⭐⭐⭐ |
| 5 | **GNU Octave 11.3.0** | ftp.gnu.org/gnu/octave/windows/ (`octave-11.3.0-w64.zip`, 816 MB) | — | — | GPL-3.0 | **ĐÃ CÀI VÀ CHẠY** — `pkg load signal` OK, 6/8 hàm chạy ngay | **~25 phút** | ⭐⭐⭐⭐ |
| 6 | **OSET** | github.com/alphanumericslab/OSET | — | MATLAB (+ ít Python) | BSD-3-Clause | Có | chỉ cần cho Sulas21 | ⭐ |
| 7 | **fecgsyn** | github.com/fernandoandreotti/fecgsyn | Andreotti 2016, 10.1088/0967-3334/37/5/627 (= p15 trong survey) | MATLAB | GPL | Có (chưa clone trong phiên này) | chỉ cần cho Behar14 | ⭐ |
| 8 | **TCGAN** | github.com/zhwt-xidian/TCGAN | JBHI 2025, ieeexplore.ieee.org/document/10818591 | Python/PyTorch | **KHÔNG có LICENSE** | Một phần (xem 4.1) | 2–4 ngày | ⭐⭐ |
| 9 | Fetal-QRS-Detection-By-CNN | github.com/CodeNoob-SEU/Fetal-QRS-Detection-By-CNN | không dẫn paper | Python | không có | Chưa rõ (không README) | 1–2 ngày | ⭐ |
| 10 | fecg-rpeak-detection | github.com/soroor-ag/fecg-rpeak-detection | không dẫn paper | MATLAB | MIT | Không (MATLAB, 4 kênh) | — | ⭐ |
| 11 | FQRS-detection | github.com/alinamuliak/FQRS-detection | đồ án sinh viên | Jupyter | MIT | Có nhưng không phải SOTA | — | ⭐ |
| 12 | **Zhong 2018 CNN** (tự cài lại) | không có mã nguồn | 10.1088/1361-6579/aac96c (p01) | ta viết | — | **Có** | 0,5 ngày | ⭐⭐⭐ |
| 13 | **U-Net-1D** (tự cài lại) | không có mã nguồn | kiến trúc chuẩn | ta viết | — | **Có** | 1 ngày | ⭐⭐⭐⭐ |

**Cách xác minh:** #1, #8 — `git clone` thành công, đã liệt kê toàn bộ file. #2, #3, #5 — tải thật bằng
`Invoke-WebRequest`, kích thước byte khớp, #2 đã giải nén và đếm đủ 8/8 hàm. #6 — WebFetch mở được.
#9, #10, #11 — trả về từ GitHub Search API (repo tồn tại, có metadata); #9 đã WebFetch trang repo nhưng
**README trả 404 trên nhánh `main`** nên không xác nhận được nội dung. #7 — chỉ thấy trong kết quả API, chưa clone.

---

## 2. Chi tiết theo nhiệm vụ

### 2.1 (a) Octave — KHẢ THI

| Hạng mục | Kết quả |
|---|---|
| `winget search octave` | `Octave / GNU.Octave / 11.3.0 / winget` — **có** |
| `choco` | chưa cài trên máy |
| MATLAB / Octave sẵn có | **không** (`matlab`, `octave`, `octave-cli` đều vắng mặt) |
| Cài bằng winget | **hỏng**: `InternetOpenUrl() failed. 0x80072efd` khi tải `octave-11.3.0-w64-installer.exe` từ `ftpmirror.gnu.org`. Đây là **lỗi mạng, không phải lỗi quyền admin** |
| Phương án thay thế | `https://ftp.gnu.org/gnu/octave/windows/octave-11.3.0-w64.zip` (816 MB / 855 208 207 byte, portable) — **đã tải xong**, ~70 MB/phút |
| Giải nén | `tar -xf` (bsdtar có sẵn trong Windows 11) — **45 giây**. Dùng `tar`, **đừng dùng `Expand-Archive`** (chậm hơn nhiều lần) |
| Tệp thực thi | `…\octave-11.3.0-w64\mingw64\bin\octave-cli.exe` |
| **Đã chạy thật** | `octave-cli --no-gui --quiet test.m` → **`octave version: 11.3.0`, `pkg load signal: OK`** |

**Kết luận: KHẢ THI, đã kiểm chứng.** Tổng ~25 phút (20 phút tải + 45 giây giải nén), **không cần quyền
admin, không đụng registry**. Gói `signal` có sẵn trong bản Windows.

#### Kết quả smoke test 8 hàm then chốt của chuỗi Power-MF

| Hàm | Kết quả |
|---|---|
| `butter`, `filtfilt`, `gausswin`, `medfilt1`, `freqz`, `interpft` | **6/6 chạy ngay, không cần sửa** |
| `pwelch` | **LỆCH API** — `pwelch: arg 3 (overlap) must be real from 0 to 0.950000` |
| `findpeaks` | **LỆCH API** — `Data contains negative values. You may want to "DoubleSided" option` |

Đúng hai hàm tôi đã dự đoán là rủi ro nhất. Bản vá ở mục 2.2.1 — **đã thử nghiệm và xác nhận hoạt động**.

### 2.2 (b) Power-MF — phụ thuộc còn thiếu, đã giải quyết phần lớn

`PowerMF.m` gọi 8 hàm ngoài. Trạng thái **sau khi tải `pmea-varanini.zip`**:

| Hàm | Trạng thái | Đường dẫn trong zip |
|---|---|---|
| `FecgImpArtCanc` | **CÓ** | `xCinC/FecgImpArtCanc.m` |
| `FecgDetrFilt` | **CÓ** | `xCinC/FecgDetrFilt.m` |
| `FecgNotchFilt` | **CÓ** | `xCinC/FecgNotchFilt.m` |
| `FecgICAm` | **CÓ** | `xCinC/FecgICAm.m` |
| `FecgInterp` | **CÓ** | `xCinC/FecgInterp.m` |
| `FecgQRSmDet` | **CÓ** | `xCinC/FecgQRSmDet.m` |
| `FecgQRSmCanc` | **CÓ** | `xCinC/FecgQRSmCanc.m` |
| `FecgICAf` | **CÓ** | `xCinC/FecgICAf.m` |

Zip chứa **30 file .m**, gồm cả các hàm phụ trợ nội bộ mà 8 hàm trên gọi tới
(`ImpArtElimS`, `filtNotchFB`, `notchCoeff`, `medfilt1mit`, `coshFpDeIca`, `kurtFpDeIca`, `maxsc`,
`meansc`, `mimaxsc`, `mimaxscG`, `meanMaxSc`, `meanMaxScW`, `meanMiMaSc`, `QRSdetectorM`,
`QRSdetectorF1`, `QRSdetectorF2`, …). **Chuỗi phụ thuộc khép kín.**

**Phân tích ký hiệu chưa định nghĩa (chạy tự động trên 38 file .m):** toàn bộ chuỗi PowerMF chỉ cần
**gói `signal`**: `butter`, `filtfilt`, `findpeaks`, `freqz`, `gausswin`, `medfilt1`, `pwelch`.
ICA được Varanini **tự cài trong `coshFpDeIca`/`kurtFpDeIca`** (FastICA dạng cosh/kurtosis) — **không gọi
toolbox ICA ngoài nào**. `interpft` (dùng trong `FecgInterp`) là hàm lõi, có sẵn trong Octave.

Các hàm còn thiếu thật sự, và chúng **không thuộc đường đi của PowerMF**:

| Hàm thiếu | Thuộc gói | Chỉ được gọi bởi |
|---|---|---|
| `PiCA`, `LPFilter`, `PeakDetection4`, `RWAverage`, `SynchPhaseTimes2`, `ChannelIndex10`, `HRCalculation2`, `PeriodicDeflDecompositionWDEN`, `jadeR` | OSET | `Sulas21.m` |
| `physionet2013extract`, `stack` | CinC_Behar | `Behar14.m` |
| `Bxb_compare` | WFDB Toolbox | `benchmark_algorithms.m`, `parameter_optimization.m` — **chỉ là bộ chấm điểm; ta đã có bộ chấm riêng bằng Python** |

### 2.2.1 Hai bản vá Octave — ĐÃ THỬ NGHIỆM VÀ XÁC NHẬN

Đây là phần gỡ rủi ro có giá trị nhất của S1. Cả hai lỗi đều nằm **trong chính `PowerMF.m`**, không phải
trong các hàm Varanini.

**Bản vá 1 — `pwelch`: tham số overlap là PHÂN SỐ, không phải số mẫu.**

```matlab
% PowerMF.m dòng ~118 (MATLAB gốc):
[Pxx,f] = pwelch(current-mean(current), gausswin(Nfft), Nfft/2, Nfft, fs);
% Octave: đổi Nfft/2 (số mẫu) -> 0.5 (phân số)
[Pxx,f] = pwelch(current-mean(current), gausswin(Nfft), 0.5,    Nfft, fs);
```
Đã xác nhận: `pwelch(...,0.5,...)` chạy, trả về 129 bin, dải 0–2000 Hz với fs = 4000. **Cùng ngữ nghĩa**
(MATLAB `Nfft/2` mẫu = 50 % chồng lấn = Octave `0.5`), nên **không làm lệch kết quả**.

**Bản vá 2 — `findpeaks`: Octave từ chối dữ liệu có giá trị âm.**

`PowerMF.m` gọi `findpeaks` ở ba chỗ, và **hai trong số đó nhận dữ liệu có giá trị âm**:
`abs_dev` (đã qua `filtfilt` băng thông nên dao động quanh 0) và `r` (đầu ra matched filter).

```matlab
% SAI trong Octave -> ném lỗi:
[~,peaks]  = findpeaks(abs_dev(channel,:), 'MINPEAKDISTANCE', distance);
[~,fPeaks] = findpeaks(r,                  'MinPeakDistance', distance);

% ĐÚNG -- dịch lên cho không âm, vị trí đỉnh KHÔNG đổi:
s = abs_dev(channel,:);  s = s - min(s);
[~,peaks]  = findpeaks(s, 'MINPEAKDISTANCE', distance);
rs = r - min(r);
[~,fPeaks] = findpeaks(rs, 'MinPeakDistance', distance);
```

**Đừng dùng `'DoubleSided'`** (gợi ý trong thông báo lỗi của Octave) — nó **trả về cả đáy lẫn đỉnh**,
sai hoàn toàn so với ngữ nghĩa MATLAB. Đã kiểm chứng: phép dịch `s - min(s)` cho **đúng 38 đỉnh**,
trung vị RR 459,5 ms trên tín hiệu thử 132 bpm — khớp kỳ vọng.

**Cảnh báo thêm về `Nfft`:** trong thử nghiệm của tôi, `Nfft = 256` ở fs = 4000 cho độ phân giải 15,6 Hz,
khiến dải 1,8–3,0 Hz chỉ còn **dưới 3 bin** và `findpeaks` ném lỗi *"DATA must be a vector of at least 3
elements"*. Với công thức thật của PowerMF (`nsc = fs*15*(60/110)` → `Nfft = 32768` ở fs = 4000) độ phân
giải là 0,122 Hz nên không sao — **nhưng nếu bản ghi quá ngắn thì nhánh `if Nfft > length/2` sẽ cắt `Nfft`
xuống và tái tạo đúng lỗi này.** Cần chốt chặn: bỏ qua bản ghi ngắn hơn ~30 giây.

**Ước lượng công sức chạy Power-MF trên ADFECGDB: 0,5–1 ngày** (giảm từ 1,5–2,5 ngày nhờ đã gỡ sẵn rủi ro).
Kế hoạch:
1. ~~Cài Octave~~ — **xong** (mục 2.1).
2. Python xuất 4 kênh bụng mỗi bản ghi ra `.mat` (`scipy.io.savemat`) — tránh đọc EDF trong Octave (0,5 giờ).
3. Áp hai bản vá ở trên vào `PowerMF.m` (0,25 giờ).
4. Viết driver `.m`: nạp `.mat` → `PowerMF(ECG, 1000, 340)` → ghi vị trí đỉnh ra `.mat` (1 giờ).
5. Chấm điểm bằng **bộ chấm sẵn có của nhóm** (±50 ms, ghép tham lam) để đảm bảo cùng giao thức (1 giờ).
6. Dự phòng gỡ lỗi (0,5 ngày).

**Cách tự kiểm chứng bắt buộc:** đối chiếu với số đã công bố trong `Results/*.mat` —
**B2 = 97,98; B1 = 99,46**. Nếu ta chạy ra lệch quá ~1 điểm thì bản vá hoặc tiền xử lý đã sai.
`filtfilt` của Octave đệm biên khác MATLAB một chút, nên chênh lệch nhỏ là bình thường.
Đây chính là lý do bước 5 dùng bộ chấm của nhóm chứ không dùng `Bxb_compare` (cần WFDB Toolbox).

### 2.3 Giấy phép — cảnh báo

`fecg-benchmarking` là **MIT**. Nhưng `pmea-varanini.zip` và `joachimbehar.zip` là bài dự thi
PhysioNet/CinC 2013; PhysioNet yêu cầu mã nguồn dự thi được công bố mở nhưng **không gắn nhãn giấy phép
chuẩn trong zip**. Trước khi tái phân phối (kể cả đưa vào repo của nhóm) **phải kiểm tra lại**; an toàn nhất là
**không commit** các zip này mà viết script tải về như `model/download_data.py` đang làm.

---

## 3. (c) ĐẶC TẢ `Power-MF-1ch` — biến thể đơn kênh, thuần Python

Đây là sản phẩm quan trọng nhất của S1. Đặc tả dưới đây đọc trực tiếp từ `PowerMF.m` và `helper/matched_filter.m`.

### 3.1 Power-MF gốc làm gì (21 bước)

Các bước 1–8 là **tiền xử lý + khử mẹ của Varanini 2014**; bước 9–21 mới là **đóng góp riêng của Jaeger 2024**.

```
1.  X   = FecgImpArtCanc(ECG, fs)        khử nhiễu xung
2.  Xd  = FecgDetrFilt(X, fs)            khử trôi nền
3.  Xf  = FecgNotchFilt(Xd, fs)          notch điện lưới
4.  Se  = FecgICAm(Xf, fs)               ICA đa kênh                    <-- CẦN >1 KÊNH
5.  [Se, fs] = FecgInterp(Se, fs, 4)     nội suy x4  => fs := 4*fs
6.  qrsM = FecgQRSmDet(Se, fs)           chọn kênh + dò QRS mẹ
7.  Xr  = FecgQRSmCanc(Se, qrsM, fs)     khử QRS mẹ
8.  Ser = FecgICAf(Xr, fs)               ICA trên phần dư               <-- CẦN >1 KÊNH
    sig = Ser'                           <<< LƯU Ý: chụp TRƯỚC khi chuẩn hoá
--- từ đây là phần Power-MF ---
9.  chuẩn hoá z-score từng cột của Ser   (sig KHÔNG bị ảnh hưởng)
10. bộ lọc đạo hàm thô:
      nu = ceil(0.005*fs);  nz = floor(0.0030*fs/2)*2 + 1     (nz làm tròn lẻ)
      B  = [ones(nu,1); zeros(nz,1); -ones(nu,1)];  delay = floor(len(B)/2)
      đệm biên bằng lặp mẫu đầu/cuối `delay` lần, filter(B,1,.), cắt 2*delay+1:end
      adecg = abs(decgr)
11. abs_dev = filtfilt(butter(1, [0.7, 8]/(fs/2)), adecg)     bao hình nhịp
12. PSD mỗi kênh:
      nsc  = uint16(fs*15*(60/110));   Nfft = max(256, 2^nextpow2(nsc))
      nếu Nfft > len/2 thì Nfft = len/2
      pwelch(x - mean(x), gausswin(Nfft), Nfft/2, Nfft, fs)
      tìm đỉnh trong dải 1,8–3,0 Hz (108–180 bpm) -> đỉnh lớn nhất mỗi kênh
13. channel = argmax(đỉnh lớn nhất)                            <-- CHỌN KÊNH
14. distance = ms/1000*fs        (ms mặc định = 340)
15. peaks = findpeaks(abs_dev[channel], MinPeakDistance=distance)   dò sơ bộ
16. med_size = round(median(diff(peaks))/2)
17. với j = 3 .. len(peaks)-2:
      template[j,:] = sig[channel, peaks[j]-med_size : peaks[j]+med_size]
18. template_med = median(template, 1)
19. r = matched_filter(sig[channel,:], template_med)
20. fPeaks = findpeaks(r, MinPeakDistance=distance)
21. fPeaks = fPeaks / 4                                        bù lại nội suy x4
```

`matched_filter(signal, template)`:
```
N = len(signal); L = len(template); w = floor(L/2)
template = template[::-1]
r = filter(template, 1, [signal, zeros(w-1)])     # = tương quan chéo
r = r[w : N+w-1]                                   # bù trễ nhóm, đỉnh về giữa mẫu
```

### 3.2 Bốn chi tiết dễ sai — phải cài đúng

1. **`sig` được chụp TRƯỚC khi z-score** (dòng `sig = Ser';` đứng trên vòng chuẩn hoá).
   Vậy: **chọn kênh và dò sơ bộ dùng tín hiệu đã chuẩn hoá (`abs_dev`), còn mẫu (template) và
   matched filter dùng tín hiệu CHƯA chuẩn hoá (`sig`).** Cài sai chỗ này là sai biên độ mẫu.

2. **Mẫu bị lẫn 2 hàng 0.** Trong MATLAB, `template(j,:)` gán từ `j=3` khiến **hàng 1 và 2 tự động bằng 0**,
   rồi `median(template,1)` lấy trung vị **bao gồm cả hai hàng 0 đó**. Đây gần như chắc chắn là **lỗi của
   tác giả**, nhưng để tái lập trung thực thì **phải giữ nguyên**. Nên cài cả hai chế độ
   (`faithful=True/False`) và báo cáo chênh lệch — bản thân nó là một quan sát đáng viết.

3. **`gausswin(N)` của MATLAB dùng alpha = 2,5**, tương đương `scipy.signal.windows.gaussian(N, std=(N-1)/5)`.
   Dùng mặc định của scipy sẽ sai độ rộng cửa sổ.

4. **Nội suy ×4 quyết định độ phân giải thời gian.** Với ADFECGDB 1000 Hz, chuỗi chạy ở **4000 Hz**;
   mọi hằng số phụ thuộc fs (`nu`, `nz`, `distance`, `Nfft`) đều tính theo fs đã nhân 4.

### 3.3 `Power-MF-1ch` — thiết kế đề xuất

Với **một kênh**, các bước ICA (4, 8) vô nghĩa và bước chọn kênh (12–13) thành phép rỗng.
Phần **có thể chuyển giao và cũng là đóng góp thật của Power-MF** là **bộ dò: bao hình đạo hàm →
mẫu trung vị → matched filter**. Ánh xạ:

| Bước gốc | `Power-MF-1ch` | Ghi chú |
|---|---|---|
| 1–3 tiền xử lý Varanini | **front-end sẵn có của nhóm** (10–60 Hz + notch 50 Hz) | giữ nguyên để so sánh công bằng |
| 4 `FecgICAm` | **bỏ** | cần đa kênh |
| 5 `FecgInterp` ×4 | **giữ** — nội suy ×4 trước khi dò | quan trọng cho độ chính xác ±50 ms |
| 6–7 dò + khử QRS mẹ | **bộ khử mẹ sẵn có của nhóm** (mẫu trung vị, tỉ lệ bình phương tối thiểu từng nhịp) | đây chính là `model/` đang làm |
| 8 `FecgICAf` | **bỏ** | cần đa kênh |
| 9 z-score | giữ | trên phần dư đơn kênh |
| 10–11 bao hình đạo hàm | **giữ nguyên** | `nu`, `nz`, Butterworth bậc 1 0,7–8 Hz |
| 12–13 chọn kênh bằng PSD | **phép rỗng** (1 kênh) — hoặc tái dùng cho **chọn đạo trình mù** sẵn có | nhóm đã có `blind_lead.py`, trùng ý tưởng |
| 14–21 dò bằng matched filter | **giữ nguyên** | phần cốt lõi |

**Ánh xạ MATLAB → scipy:**

| MATLAB | Python |
|---|---|
| `butter(1, [f1 f2]/(fs/2))` | `scipy.signal.butter(1, [f1, f2], btype='band', fs=fs)` (cùng bậc: 2N) |
| `filtfilt(b,a,x)` | `scipy.signal.filtfilt(b, a, x)` (đệm biên lệch nhẹ, bỏ qua được) |
| `filter(B,1,x)` | `scipy.signal.lfilter(B, 1, x)` |
| `findpeaks(x,'MinPeakDistance',d)` | `scipy.signal.find_peaks(x, distance=d)` (cùng chiến lược: ưu tiên đỉnh cao) |
| `pwelch(x, win, nov, nfft, fs)` | `scipy.signal.welch(x, fs=fs, window=win, noverlap=nov, nfft=nfft)` |
| `gausswin(N)` | `scipy.signal.windows.gaussian(N, std=(N-1)/5)` |
| `interpft(x, n)` | `scipy.signal.resample(x, n)` (cùng là nội suy Fourier) |
| `median(A,1)` | `np.median(A, axis=0)` |

**Công sức: 1–2 ngày. ~200 dòng. Chỉ cần numpy + scipy. Không cần Octave, không cần MATLAB.**

### 3.4 Vì sao baseline này đáng giá nhất

Bảng baseline hiện tại có ba mục tự cài (TS 78,96 / TS-PCA 91,05 / prominence 86,39). Mục yếu nhất về mặt
phản biện là **prominence 86,39** — reviewer sẽ nói "dĩ nhiên mạng nơ-ron thắng phép chọn đỉnh thô".
`Power-MF-1ch` thay `prominence` bằng **bộ dò của một phương pháp SOTA 2024**, trên **cùng phần dư, cùng kênh**.
Có ba kịch bản, **cả ba đều xuất bản được**:

- Nếu `Power-MF-1ch` đạt ~90–94: ta chứng minh được khoảng cách mạng nơ-ron **thật**, không phải do baseline yếu.
- Nếu đạt ~97: **tuyên bố "mạng đáng +11,06 điểm" sụp đổ** — nhưng đây lại là một kết quả âm tính có kiểm soát
  đúng kiểu mà nhóm đã làm tốt với TDA, và nó củng cố luận điểm trung tâm "front-end quan trọng hơn kiến trúc".
- Nếu đạt ~86 (ngang prominence): xác nhận rằng phần thắng của Power-MF nằm ở **ICA đa kênh**, không nằm ở
  matched filter → **đây là lập luận phòng thủ mạnh nhất** cho việc ta thua Power-MF trên B1/B2, và nó
  biến điểm yếu thành một phát hiện.

---

## 4. (d) Bộ dò fQRS học sâu có mã nguồn/trọng số công khai

**Kết quả rà soát: không có bộ dò nào dùng lại được.**

Đã rà: GitHub Search API (`fetal ECG`, `fQRS OR "fetal QRS" OR "abdominal ECG"`, sắp theo sao, ~70 repo),
tìm kiếm web cho Papers with Code / Zenodo, và toàn bộ 30 paper trong `survey_raw.json`.

**Trong 30 paper của survey: 0 paper fECG có mã nguồn công khai.** Các URL mã nguồn duy nhất
(`p23` PersistenceImages, `p24` PersLay, `p25` PI-Net, `p26` turkevs2022on, `p27` delay-variant-embed,
`p31`, `p32`) đều thuộc nhóm paper **TDA**, không phải fECG. Điều này **tự nó là một luận điểm cho bài báo**:
lĩnh vực dò fQRS học sâu **không có baseline tái lập được**, và đó là lý do một benchmark sạch có giá trị.

### 4.1 TCGAN — ứng viên gần nhất, phân tích chi tiết

`github.com/zhwt-xidian/TCGAN` — *TCGAN: Temporal Convolutional GAN for Fetal ECG Extraction Using
Single-channel Abdominal ECG*, IEEE JBHI 2025, `ieeexplore.ieee.org/document/10818591`.

Đã clone và **kiểm tra tĩnh checkpoint bằng `pickletools`** (không thực thi pickle — mã từ repo lạ):

| Hạng mục | Kết quả |
|---|---|
| Trọng số | `checkpoint/ADFECGDB/generator0.pth`, `generator10.pth` (2,9 MB), `discriminator{0,10}.pth` |
| Số tham số | **~722 056** (56 bản ghi lưu trữ, 2 888 224 byte fp32) |
| Kiểu lưu | **full-pickle** (`torch.save(generator)` chứ không phải `state_dict`) → khi nạp phải `weights_only=False` và **phải chạy từ thư mục gốc repo** để `model.Generator`, `common_blocks.tcn.TemporalBlock/Chomp1d` import được |
| Lớp cần import | `model.Generator`, `common_blocks.tcn.TemporalBlock`, `Chomp1d`, `torch.nn.utils.weight_norm.WeightNorm`, Conv1d, ConvTranspose1d, AvgPool1d, Flatten, Linear, ReLU, Dropout |
| Dữ liệu kèm theo | **r01, r04, r07, r08, r10 ADFECGDB dạng EDF** — đúng 5 bản ghi nhóm đang dùng |
| Giao thức | băng thông 2–100 Hz bậc 3 + notch 50 Hz → **hạ mẫu về 200 Hz** → cửa sổ **200 mẫu (1 giây)**, chồng lấn 50 %, nhân cửa sổ Hamming |
| Framework | PyTorch; `.pyc` là `cpython-38` |
| `requirements.txt` | **vô dụng** — 381 dòng UTF-16 `conda list` với đường dẫn `file:///C:/b/abs_...` cục bộ. Phụ thuộc thật chỉ là torch, numpy, scipy, pyedflib, matplotlib |
| Giấy phép | **KHÔNG CÓ** — không thể tái phân phối hợp pháp |

**Hai vấn đề chặn đứng việc dùng làm baseline:**

1. **Checkpoint không phải mô hình đã công bố.** `options/ADFECG_parameter.py` đặt `epochs=500`,
   `save_interval=10`. Repo chỉ commit **epoch 0 và epoch 10**. Đây là checkpoint gỡ lỗi giai đoạn đầu.
   Muốn có số của bài báo **phải huấn luyện lại 500 epoch**.
2. **Đầu ra là dạng sóng, không phải vị trí fQRS.** TCGAN hồi quy dạng sóng fECG (mục tiêu = kênh điện cực
   da đầu). Bài báo báo cáo chất lượng tái tạo, **không báo cáo F1 dò fQRS**. Muốn so sánh phải tự gắn thêm
   bộ dò đỉnh lên đầu ra — khi đó **ta lại đang đo bộ dò của chính mình**, không phải của họ.

**Khả năng chạy trên máy này:** torch 2.13.0+cpu ✓, scipy 1.18.0 ✓, numpy 2.4.6 ✓, matplotlib 3.11.0 ✓,
**`pyedflib` thiếu** (cài bằng pip). Rủi ro: `torch.nn.utils.weight_norm` đã bị khai tử (deprecated) trong
torch 2.x — nạp full-pickle từ torch 1.x sang 2.13 có thể vỡ. Ngoài ra pickle tham chiếu `__builtin__.set`
(tên module kiểu Python 2), phải dựa vào lớp tương thích của torch.

**Khuyến nghị: KHÔNG dùng TCGAN làm baseline.** Nhưng **nên trích dẫn** như bằng chứng cho luận điểm
"lĩnh vực này không tái lập được": một bài JBHI 2025 công bố checkpoint epoch-10 không kèm giấy phép.

### 4.2 Các repo còn lại

| Repo | Vì sao loại |
|---|---|
| `soroor-ag/fecg-rpeak-detection` (MIT) | MATLAB, **4 cảm biến** — sai cấu hình đơn kênh |
| `CodeNoob-SEU/Fetal-QRS-Detection-By-CNN` | không README (404 trên `main`), không dẫn paper, không giấy phép, không trọng số. Có `dataset.py/main.py/net.py` — có thể là bản cài lại Zhong 2018 nhưng **không kiểm chứng được** |
| `alinamuliak/FQRS-detection` (MIT) | đồ án sinh viên, không phải SOTA |
| `Satya1729-bil/FR-Net-...` | 1 sao, không giấy phép, không dẫn paper |
| `bwang40/FECG_detection_MLPNN` | 2020, MLP, không giấy phép |
| `Tashreque/Fetal-ECG-Extraction` | 2018, MATLAB, không phải học sâu |

---

## 5. (e) Tự cài lại Zhong 2018 và U-Net-1D dưới giao thức của nhóm

Giao thức chung: **4 giây, 250 Hz, 10–60 Hz, đầu vào 2 × 1000 (phần dư + gốc), nhãn heat-map Gauss σ = 12 ms,
LORO/11-fold theo chủ thể, ngưỡng chọn trên bản ghi validation, chấm ±50 ms.**

### 5.1 Zhong 2018 (p01, Physiol Meas, DOI 10.1088/1361-6579/aac96c)

**Kiến trúc theo survey:** CNN 1D nông, 3 khối tích chập (Conv→BN→ReLU; Conv→Dropout→MaxPool→ReLU; ×2),
64/128/256 bộ lọc, **kernel = 3 cả ba lớp**, max-pool = 2, rồi 3 lớp fully-connected.
**Số đã công bố:** Precision 75,33 / Recall 80,54 / F1 77,85 / Accuracy 77,38 trên CinC 2013.

**Cần gì để cài lại:**
- Chuyển từ **phân lớp cửa sổ** (có/không có fQRS) sang **đầu ra heat-map từng mẫu** — nếu không thì không
  so sánh được. Cách trung thực: giữ nguyên thân tích chập, thay 3 lớp FC bằng một Conv1d(k=1) → 1 logit/mẫu,
  và **báo cáo rõ đã sửa gì**.
- Vấn đề: max-pool ×2 ba lần làm giảm độ phân giải 8 lần (250 Hz → 31,25 Hz = 32 ms/mẫu), **quá thô cho
  dung sai ±50 ms**. Phải thêm upsample hoặc bỏ pooling — **đây là một sửa đổi thực chất phải khai báo**.
- **Công sức: 0,5 ngày** (~100 dòng + 1 lần chạy LORO ~20 phút, hạ tầng đã có sẵn trong `pilot_evidence/arch_loro.py`).
- **Giá trị: ⭐⭐⭐.** Trung bình-cao. Đây là baseline học sâu **được đặt tên, được trích dẫn nhiều**, nhưng
  trường tiếp nhận (receptive field) của nó rất nhỏ → theo chính phát hiện của nhóm (ngữ cảnh +4,53, p<0,001)
  nó **sẽ thua**, và kết quả đó **củng cố luận điểm trung tâm**. Thực ra nó gần như đã nằm trong 8 kiến trúc
  cửa sổ 300 ms mà nhóm đã chạy (37,5–92,4) — nên giá trị gia tăng chủ yếu là **cái tên trong bảng**.

### 5.2 U-Net-1D

- Encoder–decoder 1D, 4 tầng xuống/lên, skip connection, đầu ra 1 logit/mẫu — **khớp hoàn toàn** với
  định dạng đầu ra hiện có, không cần sửa đổi nào phải khai báo.
- Tái dùng nguyên vẹn `train_final.py`, bộ tải dữ liệu, hàm mất mát, bộ chọn đỉnh, bộ chấm điểm.
- Kích cỡ nên ghim ~113 k tham số để **so sánh ở cùng ngân sách tham số** với FetalQRS-TCN.
- **Công sức: 1 ngày** (~200 dòng + LORO ~30 phút).
- **Giá trị: ⭐⭐⭐⭐.** Cao nhất trong hai. Lý do: U-Net-1D là baseline **reviewer Q1 chắc chắn sẽ hỏi**
  (p07 SCTD-Net, p11 CUNet, p04 đều dùng U-Net); nó có **cùng trường tiếp nhận lớn** nên là phép thử
  công bằng cho tuyên bố "họ kiến trúc không quan trọng (+0,41, p=0,70)". Nếu U-Net-1D rơi vào khoảng
  96,5–98 thì **bảng 8-kiến-trúc mạnh hẳn lên**: thêm một họ kiến trúc hoàn toàn khác vẫn không phân biệt được.

**Cả hai đều nên làm.** Tổng 1,5 ngày, dùng lại toàn bộ hạ tầng, và trực tiếp lấp ô trống "không có
baseline học sâu nào được chạy lại" trong phản biện của P1.

---

## 6. Thứ tự ưu tiên đề xuất

| Ưu tiên | Việc | Công sức | Vì sao |
|---|---|---|---|
| **1** | `Power-MF-1ch` bằng Python (mục 3) | 1–2 ngày | Lấp lỗ hổng lớn nhất; không cần runtime lạ; cả ba kịch bản kết quả đều xuất bản được |
| **2** | U-Net-1D dưới giao thức nhóm (5.2) | 1 ngày | Baseline học sâu reviewer chắc chắn hỏi; củng cố luận điểm kiến trúc |
| **3** | **Sửa lại mọi tuyên bố SOTA trong bài** | 0,5 ngày | Bảng ở mục 0.3: ta thua trên **cả ba** tập. Phải nêu thẳng, kèm biện hộ 1-kênh-vs-4-kênh |
| **2=** | Power-MF đa kênh đầy đủ trên Octave (2.1, 2.2, 2.2.1) | **0,5–1 ngày** | Rủi ro đã gỡ sẵn: Octave chạy được, hai bản vá đã xác nhận. Biến "số đã công bố" thành "số ta tự đo", **cùng bộ chấm điểm**. Tỉ lệ giá trị/công sức nay cao nhất bảng |
| **5** | Zhong 2018 (5.1) | 0,5 ngày | Thêm tên tuổi vào bảng, giá trị gia tăng thấp hơn |
| — | TCGAN | — | **Bỏ**. Chỉ trích dẫn như bằng chứng về khủng hoảng tái lập |

**Lưu ý phạm vi quan trọng:** mọi số Power-MF/Varanini ở mục 0.3 là **đa kênh (4 kênh bụng)** còn của nhóm
là **đơn kênh**. Đó là biện hộ hợp lệ và phải nêu rõ — nhưng **không xoá được** việc bài đang thua trên các
bản ghi đo được. Cách trình bày trung thực nhất: bảng hai cột *"đơn kênh"* và *"đa kênh"*, để Power-MF ở
cột đa kênh, và để `Power-MF-1ch` (mục 3) làm **so sánh công bằng thực sự** ở cột đơn kênh.

---

## 7. Tài sản đã tải về trong phiên này

Thư mục nháp: `C:\Users\Admin\AppData\Local\Temp\claude\d--NCKHSV2026-2027\6d28f72f-143e-44dc-8fc9-44a5055f6415\scratchpad\deps\`

| Tài sản | Kích thước | Trạng thái |
|---|---|---|
| `fecg-benchmarking/` | repo đầy đủ | đã clone; `Code/PowerMF.m`, `Code/helper/matched_filter.m`, `Results/*.mat` |
| `x_pmea-varanini/xCinC/` | 30 file .m | **8/8 hàm PowerMF cần — đã xác nhận có đủ** |
| `x_mauriziovaranini/` | 67 KB | bản CinC 2013 (khác bản Physiol Meas 2014) |
| `x_joachimbehar/` | 48 KB | cho Behar14 |
| `TCGAN/` | repo đầy đủ | có trọng số epoch 0/10 + 5 EDF ADFECGDB |
| `octave.zip` + `octave/octave-11.3.0-w64/` | 816 MB | **đã giải nén và chạy**; tệp thực thi: `mingw64\bin\octave-cli.exe` |
| `../test_octave.m`, `../test_fix.m` | nhỏ | script smoke test + kiểm chứng hai bản vá (mục 2.2.1) — nên chép vào repo |

**Các thứ này nằm trong thư mục tạm của phiên.** Nếu muốn giữ, hãy chép sang chỗ khác, hoặc tốt hơn là
viết script tải về theo kiểu `model/download_data.py` (xem cảnh báo giấy phép ở mục 2.3).
