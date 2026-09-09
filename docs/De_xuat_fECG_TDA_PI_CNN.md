# ĐỀ XUẤT NGHIÊN CỨU

## Phân loại và phân tách tín hiệu điện tim thai nhi (fECG) đơn kênh bằng Persistence Images và CNN 2D

**Tên phương pháp đề xuất:** **TopoFetal-Net** — *Topological Fetal QRS Network*
**Phiên bản:** 1.0 — 07/09/2026
**Đối tượng đọc:** nhóm 3 sinh viên + GVHD, Bộ môn Khoa học Máy tính, TDTU
**Mục tiêu tài liệu:** biến 5 bước gợi ý của đề tài thành một kế hoạch nghiên cứu hoàn chỉnh (bài toán → cơ sở khoa học → SOTA → phương pháp → dữ liệu → thực nghiệm → triển khai → bài báo), có đóng góp khoa học rõ ràng so với công trình hiện có.

> **Quy ước:** các số liệu SOTA trong tài liệu được tổng hợp từ abstract/bài báo công khai (có URL ở §13). Trước khi đưa vào báo cáo Euréka hoặc bài báo, nhóm phải kiểm chứng lại từng con số bằng bản toàn văn (dùng prompt ở §12). Những chỗ ghi *[kiểm chứng]* là nơi tôi chưa chắc chắn 100%.

---

## 0. Tóm tắt điều hành (Executive summary)

**Bài toán.** Từ **một kênh** ECG ổ bụng mẹ (aECG), xác định vị trí các đỉnh QRS thai nhi (fQRS) và tách thành phần fECG. Tín hiệu thai nhi nhỏ hơn tín hiệu mẹ 5–10 lần, bị nhiễu EMG, trôi nền, nhiễu lưới; đơn kênh nên không dùng được các phương pháp tách nguồn mù đa kênh (ICA/PCA/πCA).

**Ý tưởng cốt lõi.** Coi mỗi cửa sổ tín hiệu ngắn là một quỹ đạo trong không gian pha (nhúng Takens). QRS mẹ và QRS thai tạo ra các cấu trúc hình học ở **hai thang đo khác nhau**; đồng điều bền vững (persistent homology) đo được cấu trúc đó một cách **ổn định với nhiễu, bất biến với co giãn biên độ và biến dạng thời gian nhỏ**. Persistence Image (PI) biến thông tin topo thành ảnh 2D kích thước cố định để CNN 2D học.

**Khoảng trống đã xác nhận (tính đến 09/2026).** Có nhiều công trình dùng TDA cho ECG người trưởng thành (loạn nhịp, HRV, chất lượng tín hiệu), nhưng **chưa tìm thấy công trình nào dùng persistent homology / Persistence Images cho fECG**. Công trình gần nhất là **SCTD-Net (IEEE, 12/2025)**: biến aECG đơn kênh thành ma trận trễ 2D (time-delay) rồi dùng CNN 2D — nhưng **không tính đồng điều**, chỉ xếp các bản trễ thô của tín hiệu. Đây vừa là bằng chứng rằng hướng "1D → 2D qua trễ thời gian" có giá trị, vừa là baseline tự nhiên để chúng ta vượt qua.

**Năm đóng góp dự kiến của TopoFetal-Net:**

1. **Bộ dò fQRS đầu tiên dựa trên TDA** cho aECG đơn kênh (tính mới về hướng tiếp cận).
2. **Topological Image Tensor đa lọc – đa thang**: xếp chồng PI từ Vietoris–Rips (H0, H1) ở hai độ trễ τ (thang mẹ / thang thai) và từ lọc sublevel-set (H0 = độ nổi của đỉnh) thành một tensor nhiều kênh — thay vì một PI đơn lẻ.
3. **Learnable Persistence Weighting với tiên nghiệm "thang thai"**: hàm trọng số của PI được học cùng CNN (theo tinh thần PersLay), khởi tạo dạng băng thông ưu tiên các đặc trưng có độ bền trung bình (thai) thay vì độ bền lớn nhất (mẹ) như PI chuẩn.
4. **Kiến trúc hai luồng** (PI-2D-CNN + 1D-CNN trên tín hiệu dư) với ablation chứng minh TDA đóng góp thông tin bổ trợ, đặc biệt ở SNR thấp.
5. **Giao thức đánh giá nghiêm ngặt và tái lập được**: leave-one-record-out, chia theo bản ghi, đánh giá xuyên bộ dữ liệu, thử nghiệm nhiễu có kiểm soát — khắc phục điểm yếu phổ biến của các bài F1 > 99% dùng chia ngẫu nhiên theo đoạn (rò rỉ dữ liệu). Kèm mã nguồn mở, API FastAPI và dashboard.

**Đầu ra:** (i) báo cáo Euréka, (ii) 1 bài báo hội nghị quốc tế (mục tiêu chính: *Computing in Cardiology*) hoặc tạp chí (Physiol. Meas. / Biomed. Signal Process. Control), (iii) repo + demo.

---

## 1. Bài toán và động lực

### 1.1 Bối cảnh lâm sàng
- Theo dõi tim thai (fHR, biến thiên nhịp, hình thái QRS) là cửa sổ chính để phát hiện suy thai, thiếu oxy, dị tật tim bẩm sinh.
- Phương pháp chuẩn hiện tại: CTG/Doppler (chỉ cho nhịp, không cho hình thái; cần kỹ thuật viên) hoặc điện cực da đầu thai (xâm lấn, chỉ dùng khi chuyển dạ).
- fECG không xâm lấn từ điện cực ổ bụng cho phép **theo dõi liên tục, tại nhà, chi phí thấp**. **Đơn kênh** là cấu hình rẻ nhất, dễ đeo nhất (miếng dán) nhưng cũng khó nhất về xử lý tín hiệu.

### 1.2 Bối cảnh kỹ thuật — vì sao đơn kênh khó
| Thách thức | Hệ quả |
|---|---|
| Biên độ fECG ≈ 1/5–1/10 mECG, có lúc chồng lấn hoàn toàn với mQRS | Bộ dò đỉnh cổ điển bắt nhầm đỉnh mẹ / bỏ sót đỉnh thai |
| Không có đa dạng không gian | ICA/PCA/πCA (đa kênh) không áp dụng được |
| Nhiễu EMG cơ bụng, trôi nền, hô hấp, 50 Hz | SNR dao động mạnh trong cùng một bản ghi |
| fHR 110–160 bpm biến thiên, hình thái QRS thai thay đổi theo tuổi thai và tư thế | Mô hình dễ overfit vào từng sản phụ |
| Dữ liệu thực có nhãn rất ít (5 bản ghi ADFECGDB, 75 bản ghi 1 phút PCDB) | Dễ rò rỉ dữ liệu nếu chia ngẫu nhiên; kết quả khó tái lập |

### 1.3 Phát biểu bài toán (formal)
- **Đầu vào:** một kênh aECG rời rạc $x[n],\ n=1..N$, tần số lấy mẫu $f_s$ (1 kHz trên PhysioNet; hạ xuống 250–500 Hz khi xử lý).
- **Đầu ra chính (phân loại / dò):** tập thời điểm fQRS $\{t_k\}$; suy ra fHR(t) và chuỗi RR thai.
- **Đầu ra phụ (phân tách):** ước lượng dạng sóng fECG $\hat{f}[n]$ (giữ hình thái ở mức mẫu nhịp), phục vụ so sánh hình thái với fECG da đầu trên ADFECGDB.
- **Không được dùng** kênh fECG trực tiếp (da đầu) hay kênh ngực mẹ làm đầu vào — chỉ dùng để tạo nhãn / đánh giá.

Hai chữ trong tên đề tài được cụ thể hoá như sau: **"phân loại"** = phân loại từng cửa sổ trượt là *có fQRS ở tâm* hay *không* (từ đó dò đỉnh); **"phân tách"** = tách thành phần thai khỏi hỗn hợp nhờ khử mECG + tái tạo nhịp thai dựa trên vị trí fQRS đã dò.

---

## 2. Cơ sở khoa học

### 2.1 Nhúng Takens (tái tạo không gian pha)
Từ chuỗi 1D $x[n]$ tạo điểm $d$ chiều: $\mathbf{y}_n = (x_n, x_{n+\tau}, \dots, x_{n+(d-1)\tau}) \in \mathbb{R}^d$. Định lý Takens bảo đảm (với $d$ đủ lớn) quỹ đạo $\{\mathbf{y}_n\}$ bảo toàn cấu trúc topo của hệ động lực sinh ra $x$. Với ECG (hệ gần tuần hoàn), quỹ đạo là một **vòng khép kín** mỗi nhịp; QRS là đoạn quỹ đạo "phóng ra xa" rồi quay về.
- Chọn $\tau$: cực tiểu đầu tiên của thông tin tương hỗ (AMI); chọn $d$: false nearest neighbours (FNN). giotto-tda có `SingleTakensEmbedding(parameters_type="search")` làm việc này.
- **Nhận xét quan trọng cho fECG:** QRS thai hẹp hơn QRS mẹ (≈ 30–40 ms so với 80–100 ms). Để đoạn Q-R-S của thai "mở" thành một vòng nhìn thấy được trong không gian pha, $\tau$ phải cỡ 1/3–1/4 độ rộng QRS thai (≈ 8–12 ms). Với $\tau$ lớn (≈ 25–40 ms) ta thấy rõ vòng của mẹ. → **Không có một τ tối ưu duy nhất; dùng hai τ là hợp lý** (cơ sở cho đóng góp 2).

### 2.2 Đồng điều bền vững (Persistent Homology)
Ta dùng **hai kiểu lọc** (filtration) bổ trợ nhau:

| Kiểu lọc | Đầu vào | Đặc trưng thu được | Ý nghĩa với aECG |
|---|---|---|---|
| **Vietoris–Rips (VR)** trên đám mây điểm Takens | $\{\mathbf{y}_n\}$ | **H0**: các thành phần liên thông hợp nhất theo bán kính $\epsilon$ → mã hoá *khoảng cách giữa các điểm liên tiếp*, tức **tốc độ quỹ đạo** (QRS = độ dốc lớn = điểm thưa = thanh H0 dài). **H1**: các vòng → mã hoá **chu kỳ / hình dạng nhịp**. | Vòng H1 lớn, bền = nhịp mẹ; vòng nhỏ, bền trung bình = nhịp thai; vòng rất ngắn = nhiễu |
| **Sublevel-set (lọc theo mức)** trực tiếp trên chuỗi 1D | $x[n]$ và $-x[n]$ | **H0** của lọc dưới mức = mỗi cực trị địa phương sinh một thành phần, bị "chết" khi gặp cực trị cao hơn → **độ bền = độ nổi (prominence) của đỉnh** | Đỉnh mẹ: độ nổi rất lớn; đỉnh thai: độ nổi trung bình; nhiễu: độ nổi nhỏ. Đây là "bộ dò đỉnh đa thang" tự nhiên, chi phí O(n log n). Trong giotto-tda dùng `CubicalPersistence` trên mảng 1D. |

Kết quả của mỗi lọc là **Persistence Diagram (PD)**: tập điểm $(b_i, d_i)$ (sinh, chết). **Định lý ổn định** (Cohen-Steiner–Edelsbrunner–Harer): nhiễu nhỏ trên tín hiệu → dịch chuyển nhỏ (khoảng cách bottleneck) trên PD. Đây là lý lẽ toán học cho tính chống nhiễu.

### 2.3 Persistence Image (PI)
Đổi PD sang toạ độ (sinh, độ bền) $(b, p=d-b)$, đặt một Gaussian $\sigma$ tại mỗi điểm với trọng số $w(b,p)$, tích phân trên lưới $R\times R$ (R = 32) → ảnh $R\times R$. PI **ổn định** theo Adams et al. (2017) và có kích thước cố định dù PD có số điểm khác nhau → phù hợp làm đầu vào CNN.
- **Điểm yếu của PI chuẩn cho bài toán này:** trọng số mặc định $w = p$ (tuyến tính theo độ bền) làm **đặc trưng mẹ (độ bền lớn) áp đảo** và **triệt tiêu đặc trưng thai (độ bền trung bình)** — đúng thứ ta muốn tìm. → Cần thiết kế lại trọng số (đóng góp 3).

### 2.4 Vì sao TDA hợp với fECG — và điểm yếu phải xử lý (đánh giá trung thực)
**Ưu điểm kỳ vọng**
- Bất biến với **co giãn biên độ** (sau chuẩn hoá) → giảm khác biệt giữa sản phụ, giữa kênh.
- Ổn định với **biến dạng thời gian nhỏ** và **nhiễu cộng** → hy vọng suy giảm chậm hơn CNN 1D khi SNR giảm.
- Tách được **hai thang đo** (mẹ/thai) trong cùng một biểu diễn.
- PI 32×32 nhỏ → CNN mỏng, chạy được trên CPU/thiết bị biên.

**Điểm yếu và cách xử lý (đây là nơi đề tài dễ thất bại nếu làm ngây thơ)**
| Rủi ro | Giải pháp thiết kế |
|---|---|
| Vòng H1 của thai gần như không thấy được trong VR trên aECG thô vì bị vòng mẹ áp đảo | (a) Khử mECG trước bằng template subtraction (TS-PCA) và tính TDA trên **tín hiệu dư**; (b) thêm lọc sublevel-set H0 (không cần vòng, chỉ cần đỉnh); (c) hai τ |
| PI chuẩn triệt tiêu đặc trưng độ bền trung bình | Trọng số học được, khởi tạo băng thông |
| PI là bản tóm tắt toàn cửa sổ, khó **định vị** đỉnh trong cửa sổ | Cửa sổ **ngắn** (≈ 300 ms), trượt dày (10 ms), CNN trả lời "có fQRS ở tâm hay không" → chuỗi xác suất theo thời gian → dò đỉnh |
| Chi phí tính VR | Cửa sổ ngắn ⇒ 75–150 điểm ⇒ Ripser tính trong ≈ 1 ms/cửa sổ; tiền tính và cache; song song hoá |
| TDA có thể không vượt CNN 1D | Kiến trúc hai luồng + ablation → dù kết quả nào cũng là đóng góp có giá trị (bổ trợ / chống nhiễu) |

---

## 3. Tổng quan SOTA và khoảng trống

### 3.1 Phương pháp truyền thống (không học sâu)
- **Template subtraction (TS, TS-PCA)**: dò mQRS trên aECG (dễ vì mẹ trội), lấy trung bình/PCA các nhịp mẹ làm mẫu, trừ đi → tín hiệu dư chứa thai. Là nền của khung `fecgsyn` (Behar, Oster, Clifford, 2014) và vẫn là **bước tiền xử lý tiêu chuẩn** trong nhiều bài học sâu.
- **Lọc thích nghi / EKF đơn kênh** (Niknazar et al., IEEE TBME 2013): mô hình hoá mECG bằng trạng thái Kalman mở rộng — mạnh về lý thuyết, nhạy với khởi tạo.
- **EMD/EEMD, wavelet, NMF đơn kênh**: hiệu quả trung bình, phụ thuộc chọn thành phần.
- **Đa kênh (ICA, πCA, ESN)**: F1 cao hơn nhưng ngoài phạm vi đơn kênh.

### 3.2 Học sâu cho fECG (kết quả trên dữ liệu thực; **chú ý giao thức chia dữ liệu khác nhau nên không so trực tiếp được**)

| Năm | Công trình | Kiểu | Đơn kênh? | Kết quả báo cáo (fQRS) | Ghi chú giao thức |
|---|---|---|---|---|---|
| 2018 | Zhong et al., *Physiol. Meas.* — 1D-CNN dò fQRS | 1D-CNN phân loại mẫu | Có | F1 ≈ 77% trên PCDB | Mốc "đầu tiên" nhưng thấp; lọc kênh xấu bằng SampEn |
| 2019 | Zhong et al. — RCED-Net (residual encoder–decoder) | 1D enc–dec, huấn luyện trên FECGSYNDB | Có | F1 94.10% (ADFECGDB), 93.62% (PCDB) | Huấn luyện tổng hợp → thử thực: giao thức sạch |
| 2022 | Mohebbian et al., *IEEE JBHI* — Attention CycleGAN | GAN dịch aECG→fECG, không cần cặp | Không hẳn (dùng nhiều kênh) | F1 99.4% (ADFECGDB), 99.3% (NI-FECG), 97.2% (NI-FECG challenge) | Chia theo đoạn; đánh giá cả hình thái |
| 2024 | Basak et al., *Expert Syst. Appl.* — 1D-CycleGAN giữ hình thái | GAN | Có | F1 ≈ 92% (dò), PCC 88.4% (hình thái) | Gộp ADFECGDB + bộ Matonia |
| 2024 | CBLS-CycleGAN, *Sensors* | CycleGAN CNN–BiLSTM | – | Se 99.34 / PPV 99.31 / F1 99.33 (ADFECGDB) | *[kiểm chứng giao thức]* |
| 2023–25 | Attention R2W-Net; DPSS (DP-LSTM) | U-Net attention / mask | – | R2W-Net F1 99.17% (ADFECGDB), 98.03% (PCDB); DPSS F1 97.7% (ADFECGDB, 22 ca) | *[cần tra toàn văn]* |
| **12/2025** | **SCTD-Net (IEEE)** — *time-delay representation* + Ursa-Net | 1D U-Net khử mECG → **ma trận trễ 2D** → 2D U-Net | **Có** | **PPV 98.8% (PCDB), 97.94% (ADFECGDB)**; Se/F1 thấp hơn CycleGAN một chút | Huấn luyện FECGSYNDB → thử thực (giao thức sạch) |
| 2026 | CNN-2×EEMD (đơn kênh, LOSO) | 1D-CNN chọn IMF + TS + EEMD | Có | F1 0.84–0.96 trên bộ độc lập; AUC 0.93 (LOSO ADFECGDB) | **Dùng LOSO** → con số thấp hơn nhưng đáng tin hơn |

**Bài học rút ra:**
1. Các con số F1 > 99% gần như luôn đi kèm chia dữ liệu theo đoạn trong cùng bản ghi (cùng sản phụ ở train và test). Khi dùng LOSO hoặc huấn luyện-tổng-hợp/thử-thực, F1 rơi về vùng **84–98%**. **Đây là "sân chơi" thực sự của chúng ta.**
2. Xu hướng mới nhất (SCTD-Net) xác nhận: **biểu diễn 2D từ trễ thời gian giúp CNN 2D học tốt hơn 1D**. Chúng ta đi thêm một bước: từ ma trận trễ thô → **bất biến topo** của quỹ đạo trễ.
3. Chưa nhóm nào công bố phân tích **độ bền theo SNR** một cách hệ thống cho phương pháp đơn kênh — TDA có luận cứ lý thuyết ở đây.

### 3.3 TDA cho ECG (người trưởng thành) — chứng minh khả thi của công cụ
| Công trình | Nội dung | Liên hệ với ta |
|---|---|---|
| Ignacio et al. (ICMLA 2019); Dindin, Umeda & Chazal (2020) | Persistent homology (sublevel-set / Takens) + ML/NN cho phân loại loạn nhịp, AF (CinC 2017) | Chứng minh PD/Betti curve mang thông tin nhịp |
| Frontiers Neurosci 2023 | VR + sublevel-set PH → barcode → GoogLeNet để đánh giá chất lượng ECG đeo được (CinC 2011) | Gần nhất về **pipeline PH → ảnh → CNN 2D** cho ECG |
| Dlugas (2024) | Đưa đường đẳng điện vào ECG để sinh đặc trưng H1 không tầm thường cho P/Q/S/T; dùng N đặc trưng bền nhất | Thủ thuật tiền xử lý hay, có thể mượn |
| Graff et al. (PLoS ONE 2021); Frontiers Physiol 2021; PLoS ONE 2025 (HRV trẻ em) | PH trên chuỗi RR / HRV | Bài 2025 nêu rõ "mở rộng sang HRV thai là hướng tương lai" — **xác nhận khoảng trống** |

### 3.4 Công trình gần nhất và cách chúng ta khác biệt
| | **SCTD-Net (2025)** | **TopoFetal-Net (đề xuất)** |
|---|---|---|
| Biến đổi 1D→2D | Ma trận trễ thô (x, x−1, x−2, x−3 mẫu) | Đám mây điểm Takens (τ tối ưu, hai thang) → **PD → PI**; thêm lọc sublevel-set |
| Cái CNN "nhìn thấy" | Giá trị mẫu được sắp lại | **Bất biến hình học**: độ nổi đỉnh, tốc độ quỹ đạo, vòng nhịp, đã tách thang |
| Bất biến/ổn định | Không có bảo đảm | Ổn định bottleneck (PD), ổn định PI (Adams 2017) |
| Trọng số đặc trưng | Học ngầm | **Học tường minh trên trục độ bền** + tiên nghiệm sinh lý |
| Đầu ra | Dạng sóng fECG → Pan–Tompkins dò đỉnh | Chuỗi xác suất fQRS trực tiếp (+ tái tạo nhịp) |
| Đánh giá | Tổng hợp → thực; PPV cao | Thêm LORO, xuyên bộ, **đường cong F1–SNR**, kiểm định thống kê |
| Giải thích được | Thấp | PI/PD có thể trực quan hoá cho bác sĩ ("vòng thai" hiện ra ở đâu) |

### 3.5 Khoảng trống → cơ hội đóng góp
- **G1** Chưa có TDA cho fECG. → Đóng góp 1.
- **G2** PI đơn thang, trọng số chuẩn không phù hợp tín hiệu hai thang. → Đóng góp 2, 3.
- **G3** Chưa có bằng chứng định lượng TDA bổ trợ CNN 1D trong fECG. → Đóng góp 4.
- **G4** Giao thức đánh giá thiếu nhất quán, rò rỉ. → Đóng góp 5.
- **G5** Thiếu sản phẩm mở, chạy được đầu-cuối cho đơn kênh. → API + dashboard.

---

## 4. Phương pháp đề xuất: TopoFetal-Net

### 4.1 Tổng quan pipeline
```
 aECG 1 kênh (1 kHz)
   │
   ▼  Giai đoạn 0 — Tiền xử lý & khử mECG
   ├─ hạ mẫu 250 Hz · lọc thông dải 3–90 Hz · notch 50 Hz · robust scaling
   ├─ dò mQRS (Pan–Tompkins) → TS-PCA → tín hiệu dư r[n]
   │
   ▼  Giai đoạn 1 — Cửa sổ trượt
   ├─ cửa sổ W = 300 ms, bước 10 ms, trên cả x[n] (ngữ cảnh) và r[n] (thai)
   │
   ▼  Giai đoạn 2 — Topological Image Tensor  (mỗi cửa sổ → tensor C×32×32)
   ├─ Takens(τ_f≈10 ms, d=3) trên r → VR → PD_H0, PD_H1
   ├─ Takens(τ_m≈30 ms, d=3) trên x → VR → PD_H1            (ngữ cảnh mẹ)
   ├─ Sublevel-set trên r và −r → PD_H0 (độ nổi đỉnh)
   │
   ▼  Giai đoạn 3 — Learnable Persistence Image layer
   ├─ PI_θ(u,v) = Σ_i w_θ(p_i)·G_σ((u,v) − (b_i,p_i)),  w_θ học được, khởi tạo băng thông "thang thai"
   │
   ▼  Giai đoạn 4 — Mạng hai luồng
   ├─ Luồng A: 2D-CNN mỏng (≈0.3M tham số) trên tensor PI  ─┐
   ├─ Luồng B: 1D-CNN nhỏ trên cửa sổ r và x (75 mẫu)      ─┼─ ghép → MLP → p(fQRS ở tâm)
   │                                                        ─┘
   ▼  Giai đoạn 5 — Hậu xử lý & phân tách
   ├─ chuỗi p(t) → làm mượt → dò đỉnh (khoảng cách ≥ 250 ms) → {t_k}
   ├─ fHR(t), RR thai; lọc hợp lý sinh lý (100–200 bpm)
   └─ tái tạo fECG: trung bình đồng bộ quanh {t_k} → mẫu nhịp thai → f̂[n]
```

### 4.2 Giai đoạn 0 — Tiền xử lý và khử mECG
- **Hạ mẫu** 1 kHz → 250 Hz (đủ cho dò QRS; giảm 4× số điểm cho VR). Giữ tuỳ chọn 500 Hz để kiểm tra độ nhạy.
- **Lọc**: Butterworth thông dải 3–90 Hz (bỏ trôi nền, hô hấp), notch 50 Hz (dữ liệu châu Âu). Chuẩn hoá robust (median/IQR) theo từng đoạn 10 s.
- **Dò mQRS** bằng Pan–Tompkins (hoặc neurokit2) trên aECG — mẹ trội nên dễ, Se/PPV thường > 99%.
- **TS-PCA**: cắt các nhịp mẹ quanh mQRS (−250…+400 ms), PCA giữ 3–5 thành phần chính làm mẫu thích nghi, trừ khỏi aECG → **tín hiệu dư r[n]**. Đây là bước chuẩn trong `fecgsyn`; nhóm cài lại bằng Python (numpy/scipy).
- **Ablation A0:** chạy TDA trực tiếp trên x (không khử mẹ) để định lượng vai trò của bước này.

### 4.3 Giai đoạn 1 — Cửa sổ hoá và gán nhãn
- **Cửa sổ** W = 300 ms (75 mẫu @250 Hz), **bước** 10 ms.
- **Nhãn phân loại**: dương nếu có fQRS tham chiếu trong ±20 ms quanh tâm cửa sổ; âm nếu không có fQRS trong ±60 ms; vùng 20–60 ms **bỏ qua** (tránh nhãn mập mờ).
- **Nhãn hồi quy (biến thể)**: mục tiêu heatmap Gaussian $\exp(-\Delta t^2/2\sigma^2)$, $\sigma$ = 15 ms, với $\Delta t$ là khoảng cách từ tâm đến fQRS gần nhất → chuỗi đầu ra mượt hơn, định vị chính xác hơn.
- **Mất cân bằng**: RR thai ≈ 430 ms, vùng dương 40 ms → ≈ 9% mẫu dương. Dùng focal loss (γ = 2) hoặc lấy mẫu cân bằng theo lô.
- **Khối lượng**: 5 phút × 100 cửa sổ/s = 30k cửa sổ/kênh/bản ghi; ADFECGDB (5 × 4 kênh) ≈ 600k; PCDB set-a (75 × 1 phút × 4 kênh) ≈ 1.8M. Với Ripser ≈ 1 ms/cửa sổ và 8 nhân CPU → tính toàn bộ trong vài giờ; lưu cache float16 (32×32×C ≈ 12 KB/cửa sổ).

### 4.4 Giai đoạn 2 — Topological Image Tensor (đóng góp 2)
Cấu hình cơ sở **C = 6 kênh**, mỗi kênh là một PI 32×32:

| Kênh | Nguồn | Lọc | Chiều | Thông tin |
|---|---|---|---|---|
| 1 | r, Takens(τ_f, d=3) | VR | H0 | tốc độ quỹ đạo thang thai |
| 2 | r, Takens(τ_f, d=3) | VR | H1 | vòng nhịp thai |
| 3 | r, Takens(τ_m, d=3) | VR | H1 | vòng ở thang lớn (mẹ còn sót / artefact) |
| 4 | x, Takens(τ_m, d=3) | VR | H1 | ngữ cảnh nhịp mẹ |
| 5 | r | sublevel-set | H0 | độ nổi đỉnh dương |
| 6 | −r | sublevel-set | H0 | độ nổi đỉnh âm (QRS thai có thể đảo cực) |

- Chuẩn hoá đám mây điểm về đường kính 1 trong mỗi cửa sổ (bất biến biên độ); **RMS của cửa sổ** đưa vào MLP cuối như đặc trưng vô hướng để không mất hẳn thông tin biên độ.
- $\sigma$ của PI = 0.05 (đơn vị đường kính chuẩn hoá); lưới 32×32 trên $(b,p)\in[0,1]^2$. Dò siêu tham số $\sigma \in \{0.03, 0.05, 0.1\}$, R ∈ {16, 32, 48}.
- Thư viện: `giotto-tda` (`SingleTakensEmbedding`, `VietorisRipsPersistence` dùng giotto-ph/Ripser, `CubicalPersistence`, `PersistenceImage`) hoặc `ripser` + `persim`.
- **Ablation A1:** từng kênh riêng lẻ; **A2:** bỏ sublevel-set; **A3:** một τ.

### 4.5 Giai đoạn 3 — Learnable Persistence Weighting (đóng góp 3)
PI chuẩn: $w(p) = p$. Đề xuất:
$$\mathrm{PI}_\theta(u,v) = \sum_i w_\theta(p_i)\, G_\sigma\big((u,v) - (b_i, p_i)\big),\qquad w_\theta(p) = \mathrm{softplus}\big(\mathrm{PL}_\theta(p)\big)$$
với $\mathrm{PL}_\theta$ là hàm tuyến tính từng khúc trên 16 bin của trục độ bền (16 tham số) — hoặc một MLP 2 lớp nhỏ.
- **Khởi tạo tiên nghiệm**: $w_0(p) = \exp\!\big(-(p-p_f)^2/2s^2\big)$ với $p_f$ là độ bền trung vị của các điểm PD trong cửa sổ **dương** trên tập huấn luyện (ước lượng tự động), $s$ = 0.15 → ưu tiên "thang thai", triệt bớt thang mẹ và nhiễu.
- Cài đặt PyTorch: lưu PD dạng tensor đệm (N_max điểm + mask), tính PI trên GPU trong forward → **gradient chảy về $\theta$**, huấn luyện đồng thời với CNN.
- Liên hệ: đây là trường hợp riêng, chuyên biệt hoá của PersLay (Carrière et al., 2020) cho PI; tính mới nằm ở **tiên nghiệm sinh lý hai thang** và ứng dụng fECG. Trình bày trung thực như vậy trong bài báo.
- **Ablation A4:** $w=p$ (chuẩn) vs $w_0$ cố định vs $w_\theta$ học.

### 4.6 Giai đoạn 4 — 2D-CNN mỏng và kiến trúc hai luồng (đóng góp 4)
- **Luồng A (PI-CNN)**: 3 khối [Conv3×3–BN–ReLU]×2 → MaxPool, số kênh 32–64–128, Global Average Pooling, Dropout 0.3 → vector 128. ≈ 0.3M tham số, phù hợp ảnh 32×32 (ResNet-18 pretrained ImageNet **không** chuyển giao tốt cho PI; vẫn chạy ResNet-18 sửa stem làm điểm so sánh theo yêu cầu đề tài).
- **Luồng B (1D-CNN)**: 3 lớp Conv1d (kernel 7/5/3) trên [r, x] 2×75 → vector 64.
- **Hợp nhất**: concat [128, 64, RMS, tuổi thai nếu có] → MLP → sigmoid.
- **Huấn luyện**: AdamW (lr 1e-3, weight decay 1e-4), cosine schedule, 30 epoch, batch 256, focal loss, early stopping theo **F1 mức sự kiện** (không phải accuracy mức cửa sổ) trên tập validation.
- **Tăng cường dữ liệu ở mức tín hiệu, trước TDA**: nhân biên độ ±30%, cộng nhiễu NSTDB (bw/em/ma) ở SNR 0–20 dB, trôi nền 0.3 Hz, co giãn thời gian ±10%, đảo cực. (Tiền tính K = 3 bản tăng cường/cửa sổ để tránh tính PH trong vòng lặp huấn luyện.)
- **Ablation A5:** chỉ luồng A; chỉ luồng B; hai luồng. **A6 (quan trọng nhất):** thay PI bằng **ma trận trễ thô kiểu SCTD-Net** đưa vào cùng CNN 2D → cô lập đúng giá trị của *persistent homology* so với *biểu diễn trễ*.

### 4.7 Giai đoạn 5 — Hậu xử lý và phân tách fECG
- Chuỗi $p(t)$ trên lưới 10 ms → làm mượt Gaussian ($\sigma$ = 10 ms) → `scipy.signal.find_peaks(distance = 250 ms, height = θ)`; θ chọn trên validation. Ràng buộc sinh lý: fHR ∈ [100, 200] bpm; bổ sung nhịp nếu RR ≈ 2× trung vị cục bộ (tuỳ chọn, phải báo cáo có/không dùng).
- **Phân tách**: cắt r[n] quanh mỗi $t_k$ (−100…+150 ms), trung bình đồng bộ có trọng số theo chất lượng → **mẫu nhịp thai**; đặt mẫu tại các $t_k$ → $\hat f[n]$. Đánh giá bằng PCC với fECG da đầu (ADFECGDB). Mở rộng (nếu còn thời gian): 1D encoder–decoder nhỏ có điều kiện theo heatmap fQRS.

### 4.8 Pseudo-code (một cửa sổ)
```python
def topo_tensor(x_win, r_win, tau_f, tau_m, d=3, R=32, sigma=0.05):
    pcs = {
      "r_f": takens(r_win, tau_f, d), "r_m": takens(r_win, tau_m, d),
      "x_m": takens(x_win, tau_m, d),
    }
    pds = {}
    pds["vr_r_f_H0"], pds["vr_r_f_H1"] = ripser_H0H1(normalize(pcs["r_f"]))
    _,               pds["vr_r_m_H1"] = ripser_H0H1(normalize(pcs["r_m"]))
    _,               pds["vr_x_m_H1"] = ripser_H0H1(normalize(pcs["x_m"]))
    pds["sls_r_H0"]  = sublevel_H0(normalize(r_win))
    pds["sls_nr_H0"] = sublevel_H0(normalize(-r_win))
    return pds                         # 6 persistence diagrams (list of (b, p))

class LearnablePI(nn.Module):         # differentiable PI with weight w_theta(p)
    def forward(self, pd_batch, mask):  # pd_batch: [B, C, Nmax, 2]
        b, p = pd_batch[..., 0], pd_batch[..., 1]
        w = F.softplus(self.piecewise_linear(p)) * mask
        G = gaussian_grid(b, p, self.grid, self.sigma)   # [B, C, Nmax, R, R]
        return (w[..., None, None] * G).sum(dim=2)       # [B, C, R, R]

logit = fusion_mlp(cat[pi_cnn(LearnablePI(pds)), cnn1d(stack[r_win, x_win]), rms])
```

---

## 5. Dữ liệu

### 5.1 Bảng dữ liệu (tất cả trên PhysioNet, miễn phí)
| Bộ | Nội dung | Nhãn | Vai trò trong đề tài |
|---|---|---|---|
| **ADFECGDB** (Abdominal and Direct Fetal ECG) | 5 sản phụ (r01, r04, r07, r08, r10), tuần 38–41, mỗi bản 5 phút, 1 kHz, 4 kênh bụng + 1 kênh fECG da đầu | fQRS từ điện cực da đầu (chuẩn vàng) | **Đánh giá chính** (LORO); đánh giá hình thái |
| **PCDB** = PhysioNet/CinC Challenge 2013, set-a | 75 bản ghi × 1 phút, 4 kênh bụng, 1 kHz | fQRS tham chiếu; một số bản ghi có chú giải kém tin cậy thường bị loại *[kiểm chứng danh sách chính xác trong bài Behar 2014 / Andreotti 2016]* | **Huấn luyện chính + 5-fold theo bản ghi** |
| **Matonia et al. 2020** (Fetal ECGs, direct and abdominal with reference heartbeat annotations) | ≈ 22 bản ghi (B1 Pregnancy ≈ 10, B2 Labour ≈ 12), cùng nhóm Silesia với ADFECGDB *[kiểm chứng thời lượng]* | Có chú giải tham chiếu | **Kiểm tra xuyên bộ dữ liệu**; mở rộng số sản phụ |
| **FECGSYNDB** | Dữ liệu tổng hợp từ mô hình FECGSYN: nhiều thai kỳ × mức SNR × tình huống (chuyển động, co bóp, ngoại tâm thu…) | Chuẩn vàng tuyệt đối | **Tiền huấn luyện**; **stress test theo SNR/tình huống** |
| **NI-FECGDB** | 55 bản ghi đa kênh, một sản phụ, tuần 21–40 | Không có chú giải fQRS chuẩn | Chỉ dùng định tính / tự giám sát (tuỳ chọn) |
| **MIT-BIH NSTDB** | Nhiễu thực: baseline wander (bw), electrode motion (em), muscle artefact (ma) | – | Nguồn nhiễu cho tăng cường dữ liệu và đường cong F1–SNR |

### 5.2 Quy ước xử lý
- Mỗi kênh bụng được xem là **một bản ghi đơn kênh độc lập**; báo cáo *trung bình theo kênh* **và** *kênh tốt nhất* (nói rõ cách chọn kênh; không chọn kênh theo tập test).
- Đọc bằng `wfdb` (Python). Ghi lại phiên bản dữ liệu, mã băm tệp, để tái lập.
- Mọi thống kê siêu tham số, ngưỡng θ, $p_f$ chỉ ước lượng trên **tập huấn luyện của fold đó**.

---

## 6. Thiết kế thực nghiệm

### 6.1 Độ đo
- **Mức sự kiện** (chuẩn PhysioNet/CinC 2013): một fQRS dò được tính đúng nếu cách chú giải ≤ **50 ms**; báo cáo **Se, PPV, F1** (yêu cầu của đề tài) theo từng bản ghi và tổng hợp.
- **Nhịp**: MAE fHR (bpm) trên cửa sổ 5–10 s; RMSE RR thai (ms).
- **Hình thái** (phân tách): PCC giữa $\hat f$ và fECG da đầu (chỉ ADFECGDB).
- **Hiệu năng**: thời gian xử lý mỗi phút tín hiệu trên CPU; số tham số; RAM.

### 6.2 Năm giao thức
| Mã | Giao thức | Trả lời câu hỏi |
|---|---|---|
| **P1** | **LORO trên ADFECGDB** (5 fold, giữ 20% thời gian của các bản ghi train làm validation) | Tổng quát sang sản phụ chưa thấy? |
| **P2** | **5-fold theo bản ghi trên PCDB set-a** | Quy mô lớn hơn, đa dạng hơn |
| **P3** | **Xuyên bộ dữ liệu**: train PCDB (+FECGSYNDB) → test ADFECGDB & Matonia | Dịch chuyển miền giữa thiết bị/địa điểm |
| **P4** | **Độ bền theo SNR**: cộng nhiễu NSTDB vào ADFECGDB ở SNR {20, 15, 10, 5, 0} dB; vẽ F1–SNR cho từng phương pháp | Giả thuyết trung tâm: TDA suy giảm chậm hơn |
| **P5** | **Hiệu năng & triển khai**: độ trễ, tài nguyên | Khả năng dùng thực tế |

### 6.3 Baseline (tự cài lại bằng Python, cùng tiền xử lý, cùng độ đo)
- **B1** TS-PCA + bộ dò đỉnh ngưỡng thích nghi (dòng `fecgsyn`, không học).
- **B2** EKF đơn kênh (Niknazar 2013) — tuỳ chọn nếu đủ thời gian.
- **B3** 1D-CNN phân loại cửa sổ (theo tinh thần Zhong 2018) — cùng cửa sổ 300 ms.
- **B4** 1D U-Net/encoder–decoder huấn luyện trên FECGSYNDB (RCED/SCTD giai đoạn 1) + Pan–Tompkins.
- **B5** **Ma trận trễ thô + cùng CNN 2D** (biến thể SCTD-Net không có PH) — *ablation then chốt*.
- **B6** Đặc trưng TDA thủ công (persistence entropy, Betti curves, thống kê PD) + Random Forest/XGBoost (kiểu Ignacio 2019).

### 6.4 Ablation (tóm tắt A0–A6 ở §4)
A0 khử mẹ hay không · A1 từng kênh PI · A2 bỏ sublevel-set · A3 một τ · A4 trọng số chuẩn/cố định/học · A5 một luồng/hai luồng · A6 PI vs ma trận trễ thô.

### 6.5 Thống kê
- Mọi số liệu: mean ± SD qua fold/bản ghi; khoảng tin cậy bootstrap 95% ở mức nhịp.
- So sánh cặp giữa phương pháp trên cùng bản ghi: **Wilcoxon signed-rank**; hiệu chỉnh Holm khi so nhiều cặp.
- Lặp 3 seed cho mọi mô hình học sâu.

### 6.6 Bẫy phải tránh (đã thấy trong nhiều bài đã công bố)
1. Chia ngẫu nhiên theo đoạn → cùng sản phụ ở train/test → F1 ảo.
2. Chọn kênh tốt nhất **sau khi** xem kết quả test.
3. Dùng dung sai khác 50 ms rồi so với bài dùng 50 ms.
4. Dùng kênh da đầu/ngực mẹ lọt vào đầu vào.
5. Điều chỉnh ngưỡng θ trên tập test.
6. Báo cáo accuracy mức cửa sổ (≈ 91% ngay cả khi đoán toàn "âm").

---

## 7. Kỳ vọng kết quả và tiêu chí thành công

Đặt dưới dạng giả thuyết kiểm định được (không phải lời hứa):
- **H1 (hiệu năng):** P1 LORO ADFECGDB đơn kênh: F1 kênh tốt nhất ≥ 95%, trung bình các kênh ≥ 90%; P2 PCDB: F1 ≥ 90%. (Vùng này **ngang hoặc hơn** các phương pháp đơn kênh có giao thức sạch: RCED-Net 94.1%, CNN-2×EEMD 84–96%.)
- **H2 (bổ trợ):** hai luồng > từng luồng riêng với p < 0.05 (Wilcoxon) trên ít nhất P1 và P4.
- **H3 (độ bền — luận điểm khoa học chính):** ở SNR ≤ 5 dB, mức sụt F1 của PI-CNN ≤ 50% mức sụt của 1D-CNN (B3) và của ma trận trễ thô (B5).
- **H4 (xuyên bộ):** P3 F1 ≥ 88% mà không cần tinh chỉnh trên bộ đích.
- **H5 (hiệu năng):** < 5 s xử lý mỗi phút tín hiệu trên CPU 4 nhân; mô hình < 2 MB.

Nếu H1 không đạt nhưng H2/H3 đạt → bài báo vẫn có đóng góp rõ ("TDA là đặc trưng bổ trợ chống nhiễu cho fECG đơn kênh"). Nếu cả H2/H3 không đạt → công bố kết quả phủ định có kiểm định (vẫn hợp lệ cho Euréka và CinC) kèm phân tích lý do.

---

## 8. Rủi ro và phương án dự phòng
| Rủi ro | Dấu hiệu sớm | Dự phòng |
|---|---|---|
| Vòng H1 thai quá yếu, PI gần như trống | Kiểm tra trực quan tuần 6–7: PD cửa sổ dương/âm không phân biệt được | Dựa vào sublevel-set H0 + VR-H0; giảm τ; tăng d lên 4–5; tính TDA trên dư sau lọc thông dải 15–60 Hz |
| TDA không hơn CNN 1D | Kết quả A5/A6 tuần 12 | Chuyển trọng tâm sang H3 (độ bền) và tính giải thích; vẫn đủ bài báo |
| Chi phí tính PH | > 5 ms/cửa sổ | Hạ mẫu 200 Hz; cửa sổ 250 ms; farthest-point subsampling 64 điểm; chỉ H0 + sublevel |
| Dữ liệu thực nhỏ, overfit | Chênh lớn train/val | Tiền huấn luyện FECGSYNDB; tăng cường mạnh; mô hình nhỏ; dừng sớm theo F1 sự kiện |
| Chú giải PCDB kém ở một số bản ghi | F1 bất thường thấp ở vài bản | Loại theo danh sách chuẩn trong tài liệu, công khai danh sách |
| Thiếu nền tảng topo đại số trong nhóm | Tuần 1–2 | Bootcamp: tutorial giotto-tda, chương "TDA for time series" (Perea & Harer), làm lại ví dụ SW1PerS trên tín hiệu tổng hợp |
| Trễ tiến độ do baseline nặng (B2, B4) | Tuần 15 | B2 tuỳ chọn; B4 dùng kiến trúc U-Net nhỏ, huấn luyện ≤ 2 giờ |

---

## 9. Kế hoạch triển khai (24 tuần), vai trò, cột mốc, kinh phí

### 9.1 Phân vai (3 sinh viên — mỗi người "sở hữu" một trục, nhưng review chéo)
- **SV1 — Trưởng nhóm Tín hiệu & Topo:** tiền xử lý, TS-PCA, Takens/PH/PI, cache dữ liệu, trực quan hoá PD/PI, A0–A4.
- **SV2 — Trưởng nhóm Học sâu & Đánh giá:** PI-CNN, learnable PI layer, hai luồng, baseline B3–B6, năm giao thức, thống kê.
- **SV3 — Trưởng nhóm Hệ thống & Viết:** repo/CI, FastAPI, dashboard, Docker, tài liệu, bản nháp bài báo, hồ sơ Euréka, quản lý tiến độ.
- **GVHD:** duyệt thiết kế thực nghiệm (tuần 4), duyệt go/no-go (tuần 7), review bản nháp (tuần 20).

### 9.2 Lộ trình
| Tuần | Công việc | Sản phẩm bàn giao |
|---|---|---|
| 1–2 | Bootcamp TDA + fECG; tải dữ liệu; loader `wfdb`; EDA; chạy prompt deep-search (§12) | **D1** Ma trận tổng quan tài liệu (≥ 30 bài), data card |
| 3–4 | Tiền xử lý; dò mQRS; TS-PCA; baseline B1; bộ đánh giá ±50 ms | **D2** Bảng baseline theo P1/P2 — chốt "điểm xuất phát" |
| 5–7 | Pipeline TDA: tìm τ, d; PH; PI; cache; trực quan hoá "có thấy thai không?"; B6 (RF trên đặc trưng TDA) | **Go/No-go** tuần 7 |
| 8–11 | PI-CNN; P1 LORO; A1–A3 | **D3** Bảng kết quả đầu tiên |
| 12–14 | Learnable weighting (A4); hai luồng (A5); B5 (A6); P2 trên PCDB; P3 xuyên bộ | Bảng ablation |
| 15–16 | P4 đường cong F1–SNR; B3, B4; thống kê; lặp seed | Hình ảnh chính của bài báo |
| 17–19 | FastAPI, dashboard, Docker, kiểm thử; P5 | **D4** Demo chạy được |
| 20–22 | Viết bài (CinC/BSPC); báo cáo Euréka; poster | **D5** Bản nháp hoàn chỉnh |
| 23–24 | Dự phòng; phản biện nội bộ; nộp | Nộp Euréka / hội nghị |

### 9.3 Kinh phí đề xuất (≥ 3.000.000 VNĐ)
| Khoản | Ước tính |
|---|---|
| GPU đám mây (Colab Pro / Kaggle / Lightning, ~4 tháng) | 1.200.000 |
| Lưu trữ & hosting demo (VPS nhỏ / domain 6 tháng) | 500.000 |
| In ấn poster, báo cáo, tài liệu Euréka | 500.000 |
| Dự phòng công bố (phí hội nghị/proofreading một phần) | 800.000 |
| **Tổng** | **3.000.000** |

---

## 10. Sản phẩm phần mềm (Bước 5 của đề tài)

### 10.1 Cấu trúc repo
```
topofetal/
├── data/            # wfdb loaders, danh sách bản ghi, chia fold (json cố định)
├── preprocessing/   # filters.py, mqrs.py, ts_pca.py
├── topology/        # takens.py, ph.py (giotto-tda/ripser), pi.py, learnable_pi.py
├── models/          # pi_cnn.py, resnet18_small.py, cnn1d.py, fusion.py
├── train/           # train.py, losses.py, augment.py, configs/*.yaml
├── eval/            # metrics_50ms.py, protocols.py (P1–P5), stats.py, plots.py
├── baselines/       # b1_tspca.py, b3_cnn1d.py, b4_unet1d.py, b5_delay_matrix.py, b6_tda_rf.py
├── api/             # FastAPI: main.py, schemas.py
├── dashboard/       # Streamlit app (hoặc React + Plotly)
├── docker/          # Dockerfile, docker-compose.yml
└── notebooks/       # EDA, trực quan hoá PD/PI, hình cho bài báo
```

### 10.2 API (FastAPI)
- `POST /v1/detect` — nhận tệp WFDB/CSV/NPY + `fs` → JSON `{fqrs_ms: [...], fhr_bpm: [[t, bpm]...], rr_ms: [...], quality_score, latency_ms, model_version}`.
- `POST /v1/separate` — trả về $\hat f[n]$ (fECG tái tạo) và mẫu nhịp thai.
- `POST /v1/explain` — với khoảng thời gian cho trước, trả PD và PI (PNG base64) từng kênh + bản đồ Grad-CAM của PI-CNN → phục vụ tính giải thích.
- `GET /v1/health`, `GET /v1/model` — trạng thái, siêu tham số.
- Xử lý theo lô, giới hạn kích thước tệp, log ẩn danh; không lưu dữ liệu người dùng mặc định.

### 10.3 Dashboard
Tải bản ghi → hiển thị aECG, tín hiệu dư, fQRS dò được (so với tham chiếu nếu có), fHR theo thời gian, thư viện PI theo cửa sổ, bảng Se/PPV/F1 theo bản ghi, thanh chọn SNR để mô phỏng nhiễu và xem mô hình phản ứng thế nào (minh hoạ trực tiếp H3).

---

## 11. Khung bài báo và nơi công bố

### 11.1 Cấu trúc (theo chuẩn IEEE/Elsevier, 6–8 trang)
1. **Introduction** — bài toán đơn kênh, hạn chế SOTA (giao thức, độ bền), ý tưởng topo, 5 đóng góp.
2. **Related work** — truyền thống; học sâu (1D, GAN, SCTD-Net); TDA cho ECG; vectorisation học được (PI, PersLay).
3. **Methods** — 3.1 tiền xử lý & khử mECG; 3.2 nhúng Takens hai thang; 3.3 hai kiểu lọc; 3.4 Learnable PI; 3.5 mạng hai luồng; 3.6 hậu xử lý & tái tạo.
4. **Experimental setup** — dữ liệu; giao thức P1–P5; độ đo; baseline; chi tiết huấn luyện.
5. **Results** — bảng chính (P1, P2, P3); hình F1–SNR (P4); ablation; hiệu năng (P5); trực quan hoá PD/PI và Grad-CAM.
6. **Discussion** — vì sao TDA giúp/không giúp; giới hạn (5 sản phụ, tuần 38–41, không có loạn nhịp thai); ý nghĩa lâm sàng.
7. **Conclusion** — và mã nguồn mở.

### 11.2 Bản nháp abstract (tiếng Anh)
> *Non-invasive fetal ECG (fECG) monitoring from a single abdominal lead is attractive for low-cost, wearable surveillance but remains difficult: the fetal QRS is 5–10× weaker than the maternal QRS and no spatial diversity is available for blind source separation. We propose TopoFetal-Net, the first fetal QRS detector built on topological data analysis. Each 300-ms window of the maternal-cancelled residual is embedded via Takens' delay coordinates at two physiologically motivated delays, and persistent homology is computed with Vietoris–Rips (H0, H1) and sublevel-set (H0) filtrations. The resulting diagrams are vectorised into a multi-channel Persistence Image tensor through a learnable, fetal-scale-initialised weighting, and classified by a lightweight 2D CNN fused with a 1D CNN stream. On PhysioNet ADFECGDB under strict leave-one-record-out validation and on the CinC 2013 set-a under record-level cross-validation, TopoFetal-Net achieves an F1 of [xx.x]% and [xx.x]% (±50 ms tolerance), on par with or exceeding single-channel deep-learning methods evaluated under leakage-free protocols, while degrading [x]× more slowly than 1D-CNN and raw delay-matrix baselines as SNR falls to 0 dB. Ablations isolate the contribution of persistent homology over raw time-delay representations. Code, a FastAPI service and a web dashboard are released.*

### 11.3 Nơi công bố (theo thứ tự ưu tiên)
1. **Euréka** (bắt buộc theo đề tài).
2. **Computing in Cardiology (CinC)** — hội nghị chuyên ECG, chấp nhận bài sinh viên, chính là nơi ra đời PCDB → **phù hợp nhất**.
3. Tạp chí: *Physiological Measurement* (IOP), *Biomedical Signal Processing and Control* (Elsevier), *Computers in Biology and Medicine*; trong nước: RIVF / NICS / SoICT / KSE (IEEE-indexed).

---

## 12. Prompt deep-search cải tiến (dùng cho NotebookLM / công cụ tìm kiếm học thuật)
Bản gốc của đề tài tốt nhưng chưa nhắm đúng hai điểm quan trọng: (i) công trình gần nhất SCTD-Net, (ii) vấn đề giao thức đánh giá. Gợi ý bản mở rộng:

```
Act as a research assistant in biomedical signal processing and topological data analysis (TDA).
Scope: single-channel non-invasive fetal ECG (fECG/aECG), fetal QRS detection and fECG extraction.
Deliver a structured literature matrix (one row per paper) with columns: year, venue, input channels,
1D→2D transform (if any), model, datasets (ADFECGDB / PCDB CinC-2013 / NI-FECGDB / Matonia-2020 / FECGSYNDB),
evaluation protocol (random segment split vs leave-one-subject-out vs synthetic-to-real vs cross-dataset),
tolerance window (ms), Se / PPV / F1, code availability.

Cover four threads:
1. Deep-learning single-channel fECG methods 2018–2026, including RCED-Net, attention-based CycleGAN,
   1D-CycleGAN, CBLS-CycleGAN, Attention R2W-Net, DPSS, SCTD-Net (time-delay 2D representation, IEEE 2025),
   and EEMD+CNN (2026). Flag every paper whose protocol allows subject leakage.
2. TDA for cardiac signals 2019–2026: persistent homology on Takens-embedded ECG, sublevel-set filtration
   on ECG, Persistence Images / landscapes / Betti curves fed to CNNs, HRV persistence. Note explicitly
   whether any work targets fetal ECG.
3. Learnable vectorisations of persistence diagrams (PersLay, PLLay, ATOL, Persformer, learnable
   persistence images) and their use with 2D CNNs on time series.
4. Practical TDA tooling and cost: giotto-tda, giotto-ph/Ripser, GUDHI, persim; subsampling strategies
   for point clouds from short windows; reported runtime per window.

Prefer peer-reviewed IEEE / Springer / Elsevier / IOP / Nature-portfolio / MDPI sources; include arXiv only
if no peer-reviewed version exists. Close with a gap analysis: what has NOT been done for single-channel
fECG with TDA, and which evaluation protocol the community would consider leakage-free.
```

---

## 13. Tài liệu tham khảo (khởi điểm — nhóm hoàn thiện trong D1)

**Nền tảng TDA và chuỗi thời gian**
1. Takens F. *Detecting strange attractors in turbulence.* Lecture Notes in Mathematics 898, 1981.
2. Perea JA, Harer J. *Sliding windows and persistence: an application of topological methods to signal analysis.* Found. Comput. Math., 2015.
3. Cohen-Steiner D, Edelsbrunner H, Harer J. *Stability of persistence diagrams.* Discrete Comput. Geom., 2007.
4. Adams H, et al. *Persistence Images: A stable vector representation of persistent homology.* JMLR 18, 2017.
5. Carrière M, Chazal F, Ike Y, Lacombe T, Royer M, Umeda Y. *PersLay: A neural network layer for persistence diagrams.* AISTATS 2020.
6. Umeda Y. *Time series classification via topological data analysis.* Trans. JSAI, 2017.
7. Tauzin G, et al. *giotto-tda: A topological data analysis toolkit for machine learning and data exploration.* JMLR 22, 2021.
8. Bauer U. *Ripser: efficient computation of Vietoris–Rips persistence barcodes.* J. Appl. Comput. Topol., 2021.

**Dữ liệu và khung chuẩn fECG**
9. Jezewski J, et al. *Determination of fetal heart rate from abdominal signals: evaluation of beat-to-beat accuracy in relation to the direct fetal ECG.* Biomed. Tech., 2012 — (ADFECGDB, PhysioNet).
10. Silva I, Behar J, Sameni R, et al. *Noninvasive fetal ECG: the PhysioNet/Computing in Cardiology Challenge 2013.* CinC 2013 — (PCDB).
11. Matonia A, et al. *Fetal electrocardiograms, direct and abdominal with reference heartbeat annotations.* Sci. Data, 2020.
12. Andreotti F, Behar J, Zaunseder S, Oster J, Clifford GD. *An open-source framework for stress-testing non-invasive foetal ECG extraction algorithms.* Physiol. Meas., 2016 — (FECGSYNDB).
13. Behar J, Oster J, Clifford GD. *Combining and benchmarking methods of foetal ECG extraction without maternal or scalp electrode data.* Physiol. Meas., 2014.
14. Niknazar M, Rivet B, Jutten C. *Fetal ECG extraction by extended state Kalman filtering based on single-channel recordings.* IEEE TBME, 2013.
15. Pan J, Tompkins WJ. *A real-time QRS detection algorithm.* IEEE TBME, 1985.
16. Moody GB, Muldrow WE, Mark RG. *A noise stress test for arrhythmia detectors.* CinC 1984 — (NSTDB).

**Học sâu cho fECG (đã kiểm tra abstract 09/2026)**
17. Zhong W, Liao L, Guo X, Wang G. *A deep learning approach for fetal QRS complex detection.* Physiol. Meas., 2018. https://iopscience.iop.org/article/10.1088/1361-6579/aab297
18. Zhong W, et al. *Fetal electrocardiography extraction with residual convolutional encoder–decoder networks.* Australas. Phys. Eng. Sci. Med., 2019 (số liệu F1 94.10/93.62 trích qua Sci. Rep. 2022: https://www.nature.com/articles/s41598-022-24733-1).
19. Mohebbian MR, et al. *Fetal ECG extraction from maternal ECG using attention-based CycleGAN.* IEEE JBHI 26(2):515–526, 2022.
20. Basak P, et al. *A novel deep learning technique for morphology preserved fetal ECG extraction from mother ECG using 1D-CycleGAN.* Expert Syst. Appl. 235:121196, 2024. https://www.sciencedirect.com/science/article/abs/pii/S0957417423016986
21. *Enhancing fetal ECG signal extraction accuracy through a CycleGAN utilizing combined CNN–BiLSTM architecture (CBLS-CycleGAN).* Sensors 24(9):2948, 2024. https://doi.org/10.3390/s24092948
22. *U-Net-Based Deep Learning Framework for Single-Channel Fetal ECG Extraction Using Time-Delay Representation (SCTD-Net).* IEEE, 12/2025. https://ieeexplore.ieee.org/document/11275623/
23. *A Deep Learning-Guided Ensemble Empirical Mode Decomposition Method for Single-Channel Fetal ECG Extraction (CNN-2×EEMD).* 2026. https://pubmed.ncbi.nlm.nih.gov/41977822/
24. *Deep learning-based approach for accurate detection of fetal QRS complexes in abdominal ECG signals.* Sci. Rep., 2025. https://www.nature.com/articles/s41598-025-22999-9
25. Attention R2W-Net; DPSS (dual-path source separation) — *[cần tra toàn văn và trích dẫn đầy đủ]*.

**TDA cho ECG / HRV**
26. Ignacio PSP, Dunstan C, Escobar E, Trujillo L, Uminsky D. *Classification of single-lead electrocardiograms: TDA informed machine learning.* IEEE ICMLA 2019.
27. Dindin M, Umeda Y, Chazal F. *Topological data analysis for arrhythmia detection through modular neural networks.* Canadian AI 2020.
28. *Dynamic ECG signal quality evaluation based on persistent homology and GoogLeNet method.* Front. Neurosci., 2023. https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2023.1153386/full
29. Dlugas H. *Electrocardiogram arrhythmia detection with novel signal processing and persistent homology-derived predictors.* Data Science, 2024. https://journals.sagepub.com/doi/full/10.3233/DS-240061
30. Graff G, et al. *Persistent homology as a new method of the assessment of heart rate variability.* PLoS ONE, 2021. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0253851
31. *A persistent homology approach to heart rate variability analysis with an application to sleep-wake classification.* Front. Physiol., 2021. https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.637684/full
32. *Age-dependent patterns of cardiac complexity unveiled by topological data analysis of pediatric heart rate variability.* PLoS ONE, 2025. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0337620

---

*Tài liệu này là điểm khởi đầu. Hai quyết định lớn nhất cần GVHD chốt sớm: (1) có làm learnable PI layer (đóng góp 3) hay chỉ dùng trọng số cố định để tiết kiệm thời gian; (2) mức ưu tiên giữa hiệu năng tuyệt đối (H1) và luận điểm độ bền (H3) — vì cách viết bài báo sẽ khác nhau.*
