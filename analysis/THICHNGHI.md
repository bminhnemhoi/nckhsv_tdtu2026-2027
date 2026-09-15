> **⚠ CẢNH BÁO (12/09/2026, sau vòng 7).** Tài liệu này được viết khi CinC 2013 set-a còn được tính trên **75 bản ghi**. Sau đó xác định 15 bản (a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25) là bản sao nguyên văn của dữ liệu huấn luyện ADFECGDB — điều ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014] và nhóm đã bỏ sót. **Mọi con số CinC dưới đây (79,40 / 85,60 / 86,87 / 71,21 / 62,82, AUROC 0,980…) bị thổi 3–7 điểm và đã bị rút.** Số chính thức trên **60 bản sạch**: PSD 74,28 · peakprob 82,01 · oracle 83,60 (`analysis/dulieu_results.json`, `benchmark_dpss/eval_cinc60_sach.json`). Kết luận định tính trong tài liệu giữ nguyên trừ khi ghi khác trong `docs/nhat_ky/THAMDINH_VONG7.md`. Cụm "tiền đăng ký" trong tài liệu này **không đúng** — tệp khai báo không neo git.

> **Cảnh báo (vòng 7, 12/09/2026).** Tệp này được viết khi CinC 2013 còn tính trên **75 bản ghi**; 15 bản
> trong đó là bản sao ADFECGDB (điều ban tổ chức đã ghi nhận từ 2013 — `survey/RO_RI_VANLIEU.md`). Mọi con
> số CinC-75 ở đây (79,40 / 85,60 / 86,87 / +6,20 / +8,18 / +7,47 …) **đã rút**; số hiện hành trên 60 bản
> sạch: psd 74,28 · gate 80,72 · gate4 81,01 · rrcv 80,00 · peakprob 82,01 · oracle 83,60
> (`analysis/dulieu_results.json → chon_kenh_60_sach`, `benchmark_dpss/eval_cinc60_sach.json`). Số gốc giữ
> nguyên để truy vết; kết luận định tính đọc kèm `analysis/XACNHAN.md`.

# M3 - Thich nghi mien khong nhan: 97,56 trong mien so voi 79,40 / 85,60 ngoai mien

**Ket qua mot dong: THAT BAI. Khong phuong phap nao trong bon cai thien duoc, duoi CA HAI moc.**

Ban ghi: `adapt/adapt_results.json`, `adapt/diag_results.json`, `adapt/hp_selected.json`,
`adapt/peakprob_merged.json`, `adapt/adapt_log.txt`. Hinh: `analysis/fig_thichnghi.png`.
Ma nguon: `adapt/adapt_diag.py`, `adapt_common.py`, `adapt_run.py`, `adapt_peakprob.py`,
`adapt_analyze.py`, `adapt_pp_analyze.py`, `adapt_pp_fig.py`, `check_no_leak.py`.

HAI moc so sanh, ca hai deu la mo hinh 22 chu the zero-shot tren 75 ban ghi CinC 2013 set-a:
* **79,40** - quy tac chon kenh PSD mu nhan (`benchmark_dpss/eval_cinc75.json`), de so voi cac
  con so da cong bo truoc day;
* **85,60** - quy tac chon kenh `peakprob` cua M5 (`analysis/chonkenh_results.json`), de biet
  thich nghi con them duoc gi SAU khi da sua chon kenh. Quy tac tien dang ky cua M5 la `gate`
  (84,54); xem han che muc 8.4.

---

## 0. Rang buoc liem chinh va cach kiem tra

| Rang buoc | Cach thuc thi |
|---|---|
| Nhan CinC chi dung o buoc cham diem | Trong `adapt/adapt_common.py` khong ham `m_*` nao nhan doi so nhan; trong `adapt/adapt_run.py` bien `gt` chi duoc truyen vao `A.score(...)`. Kiem tra tu dong: `python adapt/check_no_leak.py` |
| Sieu tham so khong chon tren CinC | Chon tren be mat `hp_m12_to_B1` (mo hinh 12 chu the → 10 chu the Silesia B1), chot vao `adapt/hp_selected.json` **truoc** khi cham ban ghi CinC dau tien. Tep do khong chua ten ban ghi CinC nao (kiem tra tu dong) |
| Khong dung sang som tren CinC | So buoc gradient co dinh truoc (`steps`), khong co tieu chi dung nao doc nhan |
| Moi con so truy nguoc ve JSON | Moi bang duoi day deu tro ve `adapt/adapt_results.json` |

Che do tu huan luyen duoc chon: **transductive tung ban ghi**. Voi moi ban ghi dich, mo hinh
duoc sao chep, tu sinh nhan gia tren chinh ban ghi do, hoc tiep tren chinh ban ghi do, roi
cham tren chinh ban ghi do. Day la hop le vi khong dung nhan that, nhung **gioi han** cua che do
nay phai noi ro: mo hinh ket qua chi dung cho MOT ban ghi, khong phai mot mo hinh chung; chi phi
suy luan tang tu 4,35 ms len ~4 s moi ban ghi 60 s; va khong the ket luan gi ve kha nang tong quat
hoa cua trong so sau khi hoc.

---

## 1. VIEC 1 — Chan doan dich chuyen mien (khong dung nhan)

`adapt/adapt_diag.py` do 30 dac trung **hoan toan khong nhan** tren 75 ban ghi CinC va 22 chu the
trong mien. Trung vi [tu phan vi 25; 75]:

| Dac trung | CinC 2013 (n=75) | Trong mien (n=22) | Cohen d |
|---|---|---|---|
| Do dai ban ghi (s) | 60,0 [60; 60] | 300,0 [300; 1198] | −2,00 |
| So nhip me trong ban ghi | 90 [81; 102] | 461 [413; 1868] | −1,86 |
| Dinh 60 Hz / nen | 1,64 [1,49; 1,81] | 1,26 [1,18; 1,35] | +1,92 |
| Ti le cong suat 0–10 Hz | 0,85 [0,60; 0,98] | 0,44 [0,41; 0,51] | +1,01 |
| Ti le cong suat 10–60 Hz | 0,15 [0,02; 0,34] | 0,55 [0,47; 0,58] | −1,06 |
| Bien tan pho 95 % (Hz) | 17,4 [2,8; 33,7] | 36,4 [28,8; 41,6] | — |
| So bit huu hieu | 10,13 [9,29; 11,07] | 20,28 [19,30; 21,79] | −2,81 |
| **Do lech chuan dau vao mang (phan du)** | **1,46 [1,20; 1,90]** | **1,46 [1,32; 1,59]** | **+0,32** |
| **Phan vi 99,9 dau vao mang** | **10,37 [7,72; 14,89]** | **10,19 [8,80; 11,64]** | **+0,32** |
| **Do nhon dau vao mang** | **21,7 [11,2; 35,4]** | **27,0 [11,8; 46,8]** | **−0,22** |
| Nhip tim thai uoc tinh mu (bpm) | 139,2 [131,8; 161,1] | 133,7 [128,2; 141,9] | +0,63 |
| Nhip tim me (bpm) | 90,4 [81,7; 107,1] | 86,2 [82,1; 94,8] | +0,38 |

**Ba phat hien, va mot dinh chinh.**

1. **So bit huu hieu la dich chuyen co |d| lon nhat, nhung mot phan la gia tao va phai bi ha cap.**
   Do rieng tung nhom: CinC 10,13 bit; ADFECGDB 11,49 bit; Silesia B1 21,85 bit; Silesia B2 19,54 bit.
   Silesia di qua bo nap co doi thang do va lay mau lai ve float nen cau truc luong tu bi xoa —
   con so 20 bit la thuoc tinh cua **bo nap**, khong phai cua may ghi. So sanh hop le duy nhat la
   CinC (10,13) voi ADFECGDB (11,49): chenh ~1,4 bit, khong phai 10 bit.
   *Day la mot con so trong ban nhap dau bi loai sau khi kiem tra; ghi lai o day de khong ai trich dan nham.*

2. **Dich chuyen THAT va lon nhat la do dai ban ghi:** 60 s so voi 300–1198 s, keo theo so nhip me
   dung de dung mau khu me giam tu ~461 xuong ~90, va so doan 4 s khong chong lan tren mot ban ghi
   giam tu hang tram xuong **15**. Moi phuong phap thich nghi dua tren thong ke cua ban ghi dich
   deu phai song voi 15 doan nay.

3. **Dich chuyen thu hai la dien luoi 60 Hz.** Front-end hien tai chan **50 Hz** co dinh, trong khi
   56/75 ban ghi CinC co dinh 60 Hz manh hon 1,5 lan nen xung quanh, va 60 Hz nam ngay **bien tren**
   cua dai loc 10–60 Hz. Day la dich chuyen duy nhat trong bang co the sua bang mot thay doi front-end.

4. **Dieu quan trong nhat: phan bo DAU VAO CUA MANG gan nhu KHONG dich chuyen.** Sau
   `robust_scale`, do lech chuan, phan vi 99,9 va do nhon cua phan du tren CinC va tren mien nguon
   trung nhau (|d| ≤ 0,32; p Mann–Whitney 0,73–0,76). Noi cach khac, buoc chuan hoa hien co **da**
   lam xong viec cua "thich nghi thong ke chuan hoa". Day la co so du doan truoc rang phuong phap
   (a) va (c) — von chi can chinh lai thong ke dac trung — se khong con gi de sua.

---

## 2. Cac dich chuyen do duoc co giai thich duoc khoang cach khong?

Truoc khi thu thich nghi, mot phep kiem chung truc tiep (`adapt/adapt_simshift.py`):
lay 22 chu the **trong mien**, ap len chung dung ba dich chuyen do duoc o muc 1, roi cham lai
bang chinh checkpoint LOSO cua chu the do (3 cua so 60 s moi chu the).

| Dieu kien | F1 TB muc chu the | Trung vi | Mat so voi C0 |
|---|---|---|---|
| C0 — chi cat con 60 s | 97,33 | 99,87 | — |
| C1 — 60 s + luong tu hoa ve 10,13 bit | 97,34 | 99,87 | +0,01 |
| C2 — 60 s + bom dien luoi 60 Hz den ti so 1,64 | 97,33 | 99,87 | −0,00 |
| C3 — 60 s + luong tu + dien luoi | 97,32 | 99,87 | **−0,01** |

Ap **ca ba** dich chuyen do duoc len du lieu trong mien lam mat **0,01 diem** (tut lon nhat tren
mot chu the: 0,25 diem). 20/22 chu the van >= 90, khong chu the nao < 50.

**Ket luan chan doan (suy luan, khong phai fact truc tiep):** cac dich chuyen phan bo ma ta do duoc
**khong giai thich duoc** khoang cach. Sau khi da ap het chung, muc trong mien van la 97,32 trong khi
CinC that la 79,40 — con **17,92 diem** khong giai thich duoc bang do dai ban ghi, phan giai bit hay
dien luoi. Do la co so de du doan **truoc khi chay** rang cac phuong phap thich nghi thong ke se
khong lay lai duoc khoang cach nay, va de dinh huong ket luan cuoi cung ve nguyen nhan that.

---

## 3. VIEC 2 — Bon phuong phap da thu

| Ma | Phuong phap | Thuoc nhom nao trong de bai | Co gradient? | Sieu tham so da chot |
|---|---|---|---|---|
| `notch` | (d) **Front-end thich nghi**: do pho cua chinh ban ghi dich, chan MOI tan so dien luoi thuc su co mat (50 va/hoac 60 Hz) thay vi chan 50 Hz co dinh | de xuat them (khong co trong de bai) — xem muc 3.1 | khong | nguong ti so dinh/nen = 1,5 |
| `adabn` | (a) **Thich nghi thong ke chuan hoa**: tinh lai running mean/var cua moi lop BatchNorm tren chinh ban ghi dich | (a) | khong | khong co |
| `tent` | (c) **Thich nghi luc kiem tra**: toi thieu entropy nhi phan cua dau ra, chi cap nhat tham so affine cua BatchNorm (TENT, Wang et al. ICLR 2021) | (c) | 30 buoc | lr 1e-3, steps 30, batch 16 |
| `pl` | (b) **Tu huan luyen bang nhan gia**, che do **transductive tung ban ghi** | (b) | 40 buoc | lr 1e-4, steps 40, batch 16, nguong tin cay 0,90, sigma 12 ms |

**3.1 Vi sao them (d).** De bai cho phep de xuat phuong phap khac neu giai thich duoc. Chan doan
VIEC 1 chi ra dinh 60 Hz la mot trong hai dich chuyen that duy nhat sua duoc o dau vao, va no nam
ngay bien tren cua dai loc 10–60 Hz. `notch` la phuong phap re nhat trong bon (khong gradient,
khong sao chep mang) va la phuong phap duy nhat khong the bi hong boi nhan gia sai.
Tan so do duoc tren CinC: 60 Hz o 68/75 ban ghi, 50 Hz o 75/75.

**3.2 Chon sieu tham so — o DAU va vi sao hop le.** Be mat quyet dinh la `hp_m12_to_B1`:
mo hinh 12 chu the (**chua tung thay Silesia B1**) duoc thich nghi sang 10 chu the B1. Day la mot
dich chuyen that trong mien nguon, khong dung mot mau nao cua CinC. Ket qua be mat
(`adapt/hp_selected.json`, 10 chu the):

| Cau hinh | F1 |
|---|---|
| khong thich nghi | 94,37 |
| `pl` lr 1e-4 | **94,70** (chon) |
| `pl` lr 3e-4 | 94,61 |
| `pl` lr 3e-4 conf 0,98 | 91,08 |
| `tent` lr 1e-4 steps 10 | 94,51 |
| `tent` lr 1e-3 steps 10 | 94,62 |
| `tent` lr 1e-3 steps 30 | **94,81** (chon) |

Tren be mat nay thich nghi **co tac dung**: +0,44 diem cho `tent`, +0,33 cho `pl`, va tren chu the
kho nhat cua be mat (B1_07, m12 chi dat 67,21) `tent` keo len **73,68**, tang 6,47 diem.
Dieu nay quan trong cho phan chan doan o muc 6: cac phuong phap duoc cai dat dung va co kha nang
hoat dong; that bai o muc 4 khong phai loi cai dat.

**3.3 Che do da chon cho (b), va gioi han cua no.** `pl` chay **transductive tung ban ghi**:
voi moi ban ghi dich, sao chep mo hinh, tu sinh nhan gia tren chinh ban ghi do, hoc tiep tren chinh
ban ghi do, cham tren chinh ban ghi do. Hop le vi khong dung nhan that. **Gioi han phai noi ro**:
(i) ket qua la mot mo hinh cho MOT ban ghi, khong phai mot mo hinh chung; (ii) khong ket luan duoc
gi ve kha nang tong quat hoa cua trong so sau khi hoc; (iii) chi phi suy luan tang tu 4,35 ms moi
cua so len hang chuc giay moi ban ghi 60 s (do duoc: ca nam phuong phap x 4 kenh tren mot ban
ghi 60 s mat 77–142 s tuy tai may) — tang khoang bon bac do lon.

---

## 4. VIEC 3 — Ket qua tren DU 75 ban ghi CinC 2013 set-a

### 4.1 So voi moc cu 79,40 (quy tac chon kenh PSD mu nhan)

75 ban ghi = 75 san phu doc lap, nen day **la** muc chu the. KTC95 bootstrap 10 000 lan lay mau lai
ban ghi; Wilcoxon ghep cap. Nguon: `adapt/adapt_results.json` → `cinc.n75.F1_psd`.

| Phuong phap | F1 | Hieu so | KTC95 | p Wilcoxon | Thang | Thua | ≥90 | <50 | Tut max |
|---|---|---|---|---|---|---|---|---|---|
| khong thich nghi (moc) | **79,40** | — | — | — | — | — | 48 | 16 | — |
| (d) chan dien luoi thich nghi | 79,59 | +0,19 | [−0,21; +0,86] | 0,601 | 8 | 11 | 48 | 16 | 3,51 |
| (b) tu huan luyen nhan gia | 78,87 | **−0,53** | [−0,88; −0,22] | 5,7e−03 | 14 | 30 | 48 | 16 | 6,16 |
| (a) AdaBN | 78,13 | **−1,27** | [−2,02; −0,58] | 1,5e−03 | 11 | 30 | 48 | 18 | 12,96 |
| (c) TENT | 77,45 | **−1,95** | [−2,95; −1,07] | 1,4e−04 | 8 | 31 | 48 | 20 | 17,21 |

Bien the 68 ban ghi (loai 7 ban chu thich sai da khai bao truoc) cho cung ket luan:
moc 80,70; notch +0,22 [−0,21; +0,93]; pl −0,50; adabn −1,12; tent −1,99.

### 4.2 So voi moc moi 85,60 (quy tac chon kenh `peakprob` cua M5)

Moc ngoai mien da doi sau M5. Cac shard M3 khong luu diem `peakprob`, nen phai chay lai suy luan
(`adapt/adapt_peakprob.py`). **Hai kiem chung bat buoc da qua**: (i) F1 tung kenh tai lap dung
shard M3 cu den 1e−6 voi ca nam phuong phap; (ii) `base` duoi quy tac `peakprob` va `psd` tai lap
dung `analysis/chonkenh_results.json` cua M5 den 1e−6 tren ca 75/75 ban ghi
(85,5957 va 79,3986). Nguon: `adapt/adapt_results.json` → `peakprob.bang.F1_peakprob`.

| Phuong phap | F1 | Hieu so vs 85,60 | KTC95 | p Wilcoxon | Thang | Thua | ≥90 | <50 | Tut max |
|---|---|---|---|---|---|---|---|---|---|
| khong thich nghi (moc) | **85,60** | — | — | — | — | — | 53 | 9 | — |
| (d) chan dien luoi thich nghi | 85,15 | −0,45 | [−1,30; +0,20] | 0,476 | 8 | 13 | 54 | 10 | 23,60 |
| (b) tu huan luyen nhan gia | 83,51 | **−2,08** | [−3,81; −0,75] | 5,0e−03 | 13 | 26 | 53 | 12 | 43,00 |
| (c) TENT | 83,41 | −2,18 | [−4,56; +0,27] | 1,6e−02 | 12 | 30 | 53 | 15 | 43,23 |
| (a) AdaBN | 82,90 | **−2,70** | [−4,75; −0,98] | 2,5e−03 | 10 | 30 | 53 | 14 | 42,22 |

**Khong phuong phap nao vuot duoc moc 85,60. Ba trong bon lam hong nang hon** khi do o moc moi so
voi o moc cu. Neu do tat ca ve moc 79,40: thich nghi cong voi `peakprob` cho +3,50 den +4,11 diem,
trong khi **chi rieng `peakprob` khong thich nghi da cho +6,20 [+3,01; +9,84]** (p=7,7e−04).
Toan bo muc tang ngoai mien la cua **chon kenh**, va thich nghi **an bot** mot phan cua no.

### 4.3 Chan tren doc lap voi quy tac chon kenh

Lap luan nay khong phu thuoc vao viec chon quy tac nao, vi voi moi quy tac R ta luon co
F1_R ≤ F1_oracle:

| Phuong phap | oracle (chan tren moi quy tac) | TB 4 kenh (chat luong bo do, doc lap chon kenh) |
|---|---|---|
| khong thich nghi | **86,87** | **74,09** |
| (d) chan dien luoi | 87,01 | 74,08 |
| (b) nhan gia | 86,43 | 73,53 |
| (a) AdaBN | 85,90 | 72,11 |
| (c) TENT | 85,06 | 71,61 |

Ca oracle lan trung binh 4 kenh deu **giam** voi (a), (b), (c) — nghia la bo do sau thich nghi kem
hon **o muc tung kenh**, truoc khi bat ky quy tac chon kenh nao can thiep. Rieng TENT co
oracle 85,06 < 85,60, tuc **khong quy tac chon kenh nao** co the dua TENT len bang moc peakprob.

---

## 5. Kiem chieu nguoc bat buoc

### 5.1 Thich nghi co lam hong cac ban ghi von da tot khong?

Co, va muc hong lon hon o moc moi. Duoi quy tac `psd`: 30/75 ban ghi tut diem voi ca `adabn` va
`pl`, 31/75 voi `tent`; so ban tut hon 5 diem la 11 (adabn), 11 (tent), 2 (pl); tut lon nhat
12,96 / 17,21 / 6,16 diem. Duoi quy tac `peakprob` tut lon nhat len toi **42–43 diem**
(a10, a18, a32, a60, a64, a68). `notch` la phuong phap duy nhat gan nhu vo hai duoi quy tac `psd`
(11 ban tut, khong ban nao qua 5 diem), nhung duoi `peakprob` no cung lam mat 23,60 diem tren a75.

### 5.2 Thich nghi co lam giam hieu nang TRONG MIEN khong?

Khong. 22 chu the, LOSO, quy tac `psd` (`adapt_results.json` → `indomain`):

| Phuong phap | F1 | Hieu so | KTC95 | Thang | Thua | Tut max |
|---|---|---|---|---|---|---|
| khong thich nghi | 97,56 | — | — | — | — | — |
| (c) TENT | 97,79 | +0,23 | [−0,13; +0,71] | 8 | 7 | 1,74 |
| (b) nhan gia | 97,75 | **+0,20** | [+0,06; +0,36] | 11 | 3 | 0,08 |
| (a) AdaBN | 97,51 | −0,05 | [−0,29; +0,19] | 5 | 7 | 1,77 |
| (d) chan dien luoi | 97,56 | +0,00 | [0; 0] | 0 | 0 | 0,00 |

**Doi dau ro rang:** trong mien thich nghi giup nhe (`pl` KTC khong chua 0), ngoai mien no hai.
Tren ba chu the kho trong mien (B1_06, B1_07, B2_03) thich nghi con giup nhieu hon: tent +1,05,
pl +0,92 (so voi +0,10 va +0,08 tren 19 chu the de). *Canh bao: n=3, day la quan sat dinh huong,
khong phai bang chung.*

---

## 6. VIEC 4 — Chan doan: vi sao that bai, va that bai nay noi len dieu gi

**Ba manh bang chung hoi tu ve mot co che.**

**(i) Thiet hai tap trung dung o cho tin hieu yeu.** Tren CinC, tuong quan Spearman giua F1 goc
cua ban ghi va do thay doi sau thich nghi la duong va co y nghia: TENT rho +0,483 (p=1,1e−05),
`pl` rho +0,396 (p=4,3e−04), AdaBN rho +0,251 (p=0,030). Phan ra theo nhom:

| Nhom ban ghi | AdaBN | TENT | nhan gia | chan dien luoi |
|---|---|---|---|---|
| F1 goc ≥ 90 (n=48) | −0,14 | −0,03 | −0,02 | −0,01 |
| F1 goc 50–90 (n=11) | −4,18 | −5,71 | −0,48 | −0,71 |
| F1 goc < 50 (n=16) | −2,65 | −5,09 | −2,10 | +1,38 |

Ban ghi da tot thi khong bi dong den; toan bo thiet hai roi vao nhom ban ghi ma mo hinh von da
khong nhin thay tin hieu. Day la dang **cung co sai lam** (confirmation bias) kinh dien: nhan gia
va entropy toi thieu deu lay chinh dau ra cua mo hinh lam muc tieu, nen khi dau ra la nhieu,
thich nghi **hoc thuoc nhieu do**.

**(ii) Thich nghi pha hong chinh tin hieu ma quy tac chon kenh dua vao.** Quy tac `peakprob` dung
**xac suat cua chinh mo hinh** tai cac dinh da phat hien. Sau thich nghi, kenh duoc chon doi o
21/75 (AdaBN), 23/75 (TENT), 21/75 (`pl`) ban ghi. Tach hai nhom:

| Phuong phap | Ban ghi **doi kenh** | Ban ghi **giu kenh** |
|---|---|---|
| AdaBN | n=21, **−8,78** | n=54, −0,33 |
| TENT | n=23, **−5,11** | n=52, −0,89 |
| nhan gia | n=21, **−7,14** | n=54, −0,12 |

Gan nhu toan bo thiet hai o moc moi den tu cac ban ghi bi doi kenh. Suy luan: thich nghi khong
nhan lam lech hieu chuan xac suat cua mo hinh, va vi quy tac chon kenh tot nhat hien nay doc
chinh xac suat do, thich nghi lam hong cong cu da mang lai +6,20 diem. Day la mot **tuong tac bat
loi** giua hai y tuong, khong phai hai loi doc lap.

**(iii) Cac dich chuyen phan bo do duoc khong phai la nguyen nhan.** Muc 1 cho thay dau vao cua
mang gan nhu khong dich chuyen (|d| ≤ 0,32), va muc 2 cho thay ap ca ba dich chuyen do duoc len du
lieu trong mien chi lam mat 0,01 diem. Vi vay khong con gi de cac phuong phap thong ke sua.
Phu hop voi dieu do, phuong phap thong ke thuan tuy nhat (AdaBN) lai la mot trong hai phuong phap
hai nhat.

**Ket luan chan doan (suy luan, muc do tin cay trung binh–cao):** khoang cach xuyen he ghi **khong**
la dich chuyen thong ke don gian ma phan lon la **thieu tin hieu that** tren mot bo phan ban ghi.
Dieu nay khop voi phan ra ngan sach sai so da chot: 6,77 diem thuoc **gioi han cung** (8 ban ghi
a27 a43 a54 a57 a59 a60 a68 a71 khong cuu duoc voi mot kenh) va tran thuc te cua CinC 2013 set-a
voi mot kenh la khoang **93**, khong phai 100. Bon ban ghi bi thich nghi lam hong nang nhat duoi
quy tac `peakprob` (a60, a68, a32, a64) nam trong hoac ke ngay nhom gioi han cung do.

**Bang chung phan bien da kiem tra:** neu that bai la do cai dat sai thi cac phuong phap phai that
bai o moi noi. Chung **khong**: tren be mat `hp_m12_to_B1` (muc 3.2) TENT +0,44 va +6,47 tren chu
the kho nhat; tren 22 chu the trong mien (muc 5.2) `pl` +0,20 voi KTC khong chua 0. Cac phuong phap
chay dung — chung that bai **vi mien dich, khong vi ma nguon**.

---

## 7. Ket luan

**BAO CAO THAT BAI.** Khong phuong phap thich nghi mien khong nhan nao trong bon phuong phap da thu
cai thien duoc hieu nang tren CinC 2013 set-a, duoi ca hai moc:

* so voi moc cu 79,40 (quy tac PSD): tot nhat la `notch` +0,19 [−0,21; +0,86], p=0,601 — **khong
  phan biet duoc voi khong lam gi**; ba phuong phap con lai deu co KTC nam tron ben am;
* so voi moc moi 85,60 (quy tac `peakprob` cua M5): **khong phuong phap nao vuot**; tot nhat la
  `notch` −0,45 [−1,30; +0,20]; ba phuong phap con lai mat 2,08–2,70 diem.

**Du dia 6,36 diem thuoc ve bo do van con nguyen ven sau cong viec nay.** Thich nghi mien khong nhan
o muc tham so/thong ke **khong phai** duong di den do. Ba huong con lai, xep theo suc thuyet phuc
cua bang chung hien co:

1. **Sua bo do o muc kien truc/huan luyen** (khao sat kien truc dang bo ngo xep `cnn_l` tren `tcn`;
   do la cau hoi mo da ghi nhan, va no tan cong dung 6,36 diem nay).
2. **Bao ve quy tac chon kenh** thay vi thay doi mo hinh: hieu chuan xac suat ma `peakprob` doc vao
   la tai san dang co gia 6,20 diem va de bi pha vo — bat ky thay doi nao voi mo hinh deu phai
   duoc kiem lai duoi quy tac `peakprob`, khong chi duoi `psd`.
3. **Thich nghi co giam sat yeu**, neu va chi neu co duoc mot trung tam ghi thu hai co nhan fQRS
   that — dieu hien **khong co** (NInFEA khong phan phoi nhan).

**Mot ket qua phu co gia tri:** muc 4.3 cho thay bat ky thay doi nao lam giam trung binh 4 kenh
deu se lam giam moi quy tac chon kenh. Do la mot phep sang loc re (khong can nhan CinC de xep hang
so bo, chi can 4 lan suy luan) cho cac thay doi kien truc trong tuong lai.

---

## 8. Han che

1. **Rui ro ro ri nhan.** Nhan CinC chi duoc doc trong `A.score()` o buoc cham diem;
   `adapt/check_no_leak.py` quet tu dong va bao "khong phat hien duong ro ri". Nhung phep quet nay
   la **tinh** (doc ma nguon), khong chung minh duoc vang mat ro ri **gian tiep**: (i) bo mat na
   7 ban ghi chu thich sai duoc chot trong ma nguon tu truoc nhung van la thong tin ve mien dich;
   (ii) sieu tham so chon tren `m12→B1` duoc quyet dinh boi **nguoi da biet** hinh dang ket qua
   CinC tu cac vong truoc, la ro ri qua nguoi thuc nghiem ma khong cong cu tu dong nao bat duoc;
   (iii) viec chon dung bon phuong phap nay de thu cung chiu anh huong do. Cach duy nhat loai bo
   la mot bo giu kin hoan toan chua tung mo.
2. **Che do transductive khong tao ra mot mo hinh trien khai duoc.** Moi con so cua `pl` va `tent`
   thuoc ve mot mo hinh rieng cho tung ban ghi; khong duoc trich dan nhu hieu nang cua mot mo hinh
   chung, va chi phi suy luan cao hon khoang bon bac do lon.
3. **Khong gian sieu tham so rat hep.** Ba cau hinh cho `tent`, ba cho `pl`. Be mat mo phong
   (`hpsim`) bi dung giua chung vi vuot ngan sach. Khong loai tru duoc kha nang mot cau hinh khac
   (hoc lau hon, nguong tin cay khac, chi hoc lop cuoi) cho ket qua khac — ket luan dung la
   "**cac cau hinh da thu that bai**", khong phai "ho phuong phap nay khong the thanh cong".
4. **So sanh voi moc 85,60 mang theo canh bao hau kiem cua M5.** `peakprob` duoc chon **sau khi**
   nhin ket qua tren chinh tap danh gia; quy tac tien dang ky la `gate` (84,54). Toi khong tinh lai
   `gate` cho cac phuong phap thich nghi trong vong nay (can dac trung SQI va bo phan loai da hieu
   chuan cho tung mo hinh da thich nghi, vuot ngan sach), nen ket luan "khong vuot duoc moc moi"
   duoc chung minh truc tiep voi `peakprob` va chi suy rong sang `gate` qua lap luan oracle o
   muc 4.3.
5. **Hai huong chua thu.** Khong thu thich nghi mien doi khang (DANN/CORAL — can huan luyen lai
   toan bo, vuot ngan sach) va khong thu tang cuong du lieu mo phong dich chuyen luc huan luyen.
   Muc 2 lam giam dong co cho huong thu hai, nhung khong loai tru huong thu nhat.
6. **Lan chay bi gian doan.** Buoc do `peakprob` het RAM o ban ghi thu 63/75 va phai chay lai;
   cac ban ghi da xong duoc doc tu cache. Vi moi buoc deu tat dinh (seed co dinh) va F1 tung kenh
   duoc doi chieu 1e−6 voi lan chay truoc, gian doan nay khong anh huong ket qua — nhung no co
   nghia la cac con so den tu hai lan chay ghep lai.
7. **n=22 cho phan trong mien.** Kiem chieu nguoc "thich nghi co lam hong trong mien khong" chi co
   22 chu the va 19 trong so do da o tran (F1 ≥ 97), nen phep kiem nay co do nhay thap voi cac
   tac hai nho.

---

## 9. Tai lap

```
python adapt/adapt_diag.py                                  # VIEC 1, chan doan dich chuyen
python adapt/adapt_run.py --stage hp       --shard i/3      # chot sieu tham so (m12 -> B1)
python adapt/adapt_run.py --stage simshift --shard i/2      # mo phong dich chuyen
python adapt/adapt_run.py --stage cinc     --shard i/6      # 75 ban ghi CinC, 4 phuong phap
python adapt/adapt_run.py --stage indomain --shard i/6      # 22 chu the LOSO
python adapt/adapt_peakprob.py             --shard i/3      # do lai duoi quy tac peakprob cua M5
python adapt/check_no_leak.py                               # kiem tra ro ri nhan
python adapt/adapt_analyze.py                               # -> adapt_results.json
python adapt/adapt_pp_analyze.py                            # -> them khoa "peakprob"
python adapt/adapt_pp_fig.py                                # -> analysis/fig_thichnghi.png
```
