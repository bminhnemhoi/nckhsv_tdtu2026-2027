> **⚠ CẢNH BÁO (12/09/2026, sau vòng 7).** Tài liệu này được viết khi CinC 2013 set-a còn được tính trên **75 bản ghi**. Sau đó xác định 15 bản (a03 a04 a05 a08 a12 a13 a14 a15 a17 a19 a20 a22 a23 a24 a25) là bản sao nguyên văn của dữ liệu huấn luyện ADFECGDB — điều ban tổ chức đã ghi nhận [Silva 2013; Clifford 2014] và nhóm đã bỏ sót. **Mọi con số CinC dưới đây (79,40 / 85,60 / 86,87 / 71,21 / 62,82, AUROC 0,980…) bị thổi 3–7 điểm và đã bị rút.** Số chính thức trên **60 bản sạch**: PSD 74,28 · peakprob 82,01 · oracle 83,60 (`analysis/dulieu_results.json`, `benchmark_dpss/eval_cinc60_sach.json`). Kết luận định tính trong tài liệu giữ nguyên trừ khi ghi khác trong `docs/nhat_ky/THAMDINH_VONG7.md`. Cụm "tiền đăng ký" trong tài liệu này **không đúng** — tệp khai báo không neo git.

> **Cảnh báo (vòng 7, 12/09/2026).** Tệp này được viết khi CinC 2013 còn tính trên **75 bản ghi**; 15 bản
> trong đó là bản sao ADFECGDB (điều ban tổ chức đã ghi nhận từ 2013 — `survey/RO_RI_VANLIEU.md`). Mọi con
> số CinC-75 ở đây (79,40 / 85,60 / 86,87 / +6,20 / +8,18 / +7,47 …) **đã rút**; số hiện hành trên 60 bản
> sạch: psd 74,28 · gate 80,72 · gate4 81,01 · rrcv 80,00 · peakprob 82,01 · oracle 83,60
> (`analysis/dulieu_results.json → chon_kenh_60_sach`, `benchmark_dpss/eval_cinc60_sach.json`). Số gốc giữ
> nguyên để truy vết; kết luận định tính đọc kèm `analysis/XACNHAN.md`.

# M2 -- KIEN TRUC: TCN co phai lua chon dung khong?

**Nguon so lieu:** `pilot_evidence/arch22.json` (chay 2026-09-12 10:43 -> 12:04, 81,0 phut),
phan tich `analysis/kientruc.py` -> `analysis/kientruc_results.json`, bang tu dong
`analysis/_kientruc_tables.md`. Nhat ky day du: `pilot_evidence/arch22_log.txt`.
Moi con so trong tai lieu nay truy nguoc ve hai tep JSON do.

---

## 0. Tra loi ngan

**KHONG nen doi khoi TCN.** Cau hoi mo tu vong truoc ("khao sat cua chinh nhom xep `cnn_l`
tren `tcn`") da duoc giai quyet: o giao thuc hien hanh, **dau hieu dao nguoc**. `cnn_l` KEM HON
`tcn` **-3,10 diem F1** KTC95 bootstrap [-6,19; -0,96], Wilcoxon p = 0,0001 (Holm 0,0007),
thua 20/22 chu the. Tren thang logit hieu so la **-1,638** [-2,086; -1,157].

Sau khi da can bang tham so (+/-2,7%), ngan sach epoch, bo toi uu, lich hoc, seed va fold,
**khong mot ho kien truc nao ngoai chinh ho TCN sanh duoc voi TCN**. Hai kien truc duy nhat
dat ket luan TUONG DUONG (TOST bien 1,0 diem, p < 0,0001) la `rf_wide` va `tcn_ms` -- ca hai
deu LA TCN gian no, chi khac truong tiep nhan / so nhanh.

Day la ket qua **ung ho luan diem trung tam cua nhom**: trong bai toan nay kien truc khong phai
la bien quyet dinh, mien la no dat duoc mot dieu kien cu the -- truong tiep nhan du rong
(muc 4). Du dia 6,36 diem con lai cua "bo do" tren CinC **khong nam o viec doi ho kien truc**.

---

## 1. Giao thuc: chon cai nao va vi sao

Nhiem vu cho phep chon giua `model/train_22.py` va `pilot_evidence/band_tcn.py`.
Da chon **tron hai**, va day la ly do tung manh:

| thanh phan | lay tu | ly do |
|---|---|---|
| chia fold | `band_tcn.make_folds` | `train_22.py` co dinh 11 fold (2 chu the test/fold) -> 11 lan huan luyen cho MOI kien truc. Voi 7 kien truc do la 77 lan huan luyen, vuot xa ngan sach. `band_tcn` cho dat so fold tuy y ma van rai deu PhysioNet/B2/B1 vao moi fold. |
| cham diem | `train_22.py` | `train_22` cham o **1000 Hz voi nhan goc** (`det*4` so voi `fq1000`) thay vi ha nhan xuong 250 Hz nhu `band_tcn`. Ha nhan xuong 250 Hz lam tron nhan truoc khi cham, tu no bom them jitter -- ma jitter la mot trong cac diem cuoi cua nhiem vu nay. |
| nhan B1 | `meta['fqrs_all']` | dung quy uoc `train_22.py` (ke ca nhip co = 0). |
| chon kenh | quy tac PSD mu nhan | de so sanh duoc voi moi con so da cong bo (79,40 CinC, 97,56 san xuat). **KHONG** dung `peakprob` cua M5 -- doi ca kien truc lan quy tac chon kenh cung luc thi khong quy trach nhiem duoc. |
| nguong | quet 0,20-0,80 tren mot chu the validation RIENG | ap co dinh sang chu the test. Khong bao gio quet nguong tren test. |

**Can bang (bat buoc, da kiem va in ra log):**

| kien truc | tham so | lech so voi TCN | truong tiep nhan (do thuc nghiem bang gradient) |
|---|---:|---:|---:|
| `tcn` | 113.481 | +0,0% | 379 mau = 1.516 ms |
| `cnn_l` | 114.493 | +0,9% | 15 mau = 60 ms |
| `cnn_wide` | 114.943 | +1,3% | 377 mau = 1.508 ms |
| `unet1d` | 114.247 | +0,7% | 159 mau = 636 ms |
| `rf_narrow` | 114.886 | +1,2% | 187 mau = 748 ms |
| `rf_wide` | 116.514 | +2,7% | 763 mau = 3.052 ms |
| `tcn_ms` | 116.011 | +2,2% | 679 mau = 2.716 ms |

Cung tap doan, cung so buoc toi uu, cung AdamW 3e-3 / weight_decay 1e-4, cung OneCycle,
cung batch 16, cung seed 0, cung 3 fold, cung nhan, cung `pos_weight` tinh tu chinh fold do.
Truong tiep nhan **do thuc nghiem** (lan truyen nguoc tu dau ra o giua, dem so mau dau vao co
gradient khac 0), khong tinh bang cong thuc.

## 2. Da thu nho quy mo the nao (khai bao day du)

So voi giao thuc san xuat `train_22.py`:

* **3 fold thay vi 11** -> tap huan luyen ~13-14 chu the thay vi 20.
* **stride doan 4 s (vang) / 8 s (B1) thay vi 1 s / 2 s** -> ~5.700-6.300 doan/fold thay vi ~33.000.
* **3 epoch, batch 16** (san xuat: 4 epoch, batch 32). Cung so mau trinh dien moi epoch nhung
  gap doi so buoc toi uu voi cung thoi gian may.
* **Khong tang cuong du lieu.**
* Tong 1.065-1.176 buoc toi uu moi fold so voi 4.168 buoc cua `train_22` -> **moi mo hinh deu duoi-huan-luyen**.
* **Bien the sigma (`sigma6`, `sigma24`) da viet code nhung KHONG chay** -- bi cat khoi lenh chay
  de ngan sach 104 phut du cho 7 kien truc con lai. Nhiem vu yeu cau 2-3 bien the; da chay 3
  (`rf_wide`, `rf_narrow`, `tcn_ms`). Nhanh "dau ra / sigma" van con bo ngo.

**He qua phai mang theo:** F1 tuyet doi o day (97,64 cho TCN) khong the so sanh truc tiep voi
97,56 cua mo hinh san xuat -- day la 3 fold voi tap train nho hon, khong phai 11 fold.
Day la bang so sanh **TUONG DOI** giua cac kien truc o cung ngan sach; **khong duoc trich con so
tuyet doi tu bang nay ra ngoai**.

Chieu lech cua viec duoi-huan-luyen: no **lam yeu di** khac biet giua cac kien truc, tuc thien ve
ket luan "hoa nhau". Vi vay cac ket luan KHAC BIET (`cnn_l`, `unet1d`, `cnn_wide` kem hon) la
**bao thu** -- chung song sot du bi lam yeu. Nguoc lai cac ket luan TUONG DUONG (`rf_wide`,
`tcn_ms`) la **khong bao thu** -- xem muc 9.

## 3. Ket qua chinh (VIEC 1 -- dau doi dau)

Xem bang day du o `analysis/_kientruc_tables.md` muc B1-B2. Tom tat:

| kien truc | macro F1 (PSD) | hieu so voi `tcn` | KTC95 bootstrap | Wilcoxon (Holm) | T/H/B | TOST +/-1,0 | **hieu logit** | **KTC95 logit** |
|---|---:|---:|---|---:|---:|---|---:|---|
| `tcn` | **97,64** | -- | -- | -- | -- | -- | -- | -- |
| `rf_wide` | 97,63 | -0,01 | [-0,18; +0,16] | 0,72 (0,87) | 11/5/6 | **TUONG DUONG** | +0,088 | [-0,176; +0,285] |
| `tcn_ms` | 97,62 | -0,02 | [-0,34; +0,24] | 0,43 (0,87) | 9/8/5 | **TUONG DUONG** | +0,035 | [-0,250; +0,274] |
| `rf_narrow` | 96,93 | -0,71 | [-1,73; +0,07] | 0,028 (0,11) | 4/4/14 | chua ket luan | -0,292 | [-0,675; +0,117] |
| `cnn_wide` | 96,84 | -0,80 | [-2,40; +0,13] | 0,099 (0,30) | 6/1/15 | chua ket luan | **-0,447** | **[-0,745; -0,156]** |
| `unet1d` | 96,38 | -1,25 | [-2,90; -0,19] | 0,0041 (0,021) | 3/1/18 | chua ket luan | -0,804 | [-1,169; -0,427] |
| `cnn_l` | 94,53 | **-3,10** | [-6,19; -0,96] | 0,0001 (0,0007) | 2/0/20 | chua ket luan | **-1,638** | [-2,086; -1,157] |

Don vi phan tich = **chu the** (n = 22), khong phai cap (chu the x kenh). Bootstrap 20.000 lan
lay mau lai chu the. Thang logit dung hieu chinh lien tuc eps = 1/(4 n_ref) voi n_ref = so nhan
that cua chinh chu the do (quy uoc cua `analysis/luongcuc.py`).

## 4. Phat hien co gia tri nhat: **truong tiep nhan, khong phai "gian no"**

Xep cac kien truc theo truong tiep nhan do duoc, doi chieu voi hieu so **logit** so voi `tcn`:

| kien truc | RF (ms) | hieu logit so voi `tcn` |
|---|---:|---:|
| `cnn_l` | 60 | -1,638 |
| `unet1d` | 636 | -0,804 |
| `rf_narrow` | 748 | -0,292 |
| `cnn_wide` | 1.508 | -0,447 |
| `tcn` | 1.516 | 0 (chuan) |
| `tcn_ms` | 2.716 | +0,035 |
| `rf_wide` | 3.052 | +0,088 |

Ba suy luan tach bach nhau:

**(a) Phan lon -- nhung khong phai tat ca -- thiet hai cua `cnn_l` la do truong tiep nhan, khong
phai do thieu gian no.** `cnn_wide` la **cung ho chong chap tron, khong gian no** voi `cnn_l`,
chi khac o cho nhan rong hat nhan (k = 95) de RF khop TCN. Chi rieng viec nay keo hieu so logit
tu -1,638 len -0,447, tuc **lay lai 73% khoang cach**. Do la thiet ke da duoc dua vao **chinh vi
muc dich tach bach hai bien nay**, va no tra loi dut diem: cau chuyen "TCN thang vi no gian no"
la SAI; TCN thang chu yeu vi no **re tien cho truong tiep nhan rong**.

**(b) Phan du -0,447 logit KTC95 [-0,745; -0,156] la co that va KHONG chua 0.** O cung truong
tiep nhan 1.508 so voi 1.516 ms va cung so tham so, chong chap tron van kem TCN gian no. Vay
cau truc gian no + noi tat van dong gop mot phan thuc, chi la phan nho hon nhieu so voi RF.

**(c) Bao hoa tren 1,5 s.** Tu 1.516 ms (`tcn`) len 2.716 ms (`tcn_ms`) va 3.052 ms (`rf_wide`),
hieu ung tat (+0,035 va +0,088 logit, ca hai KTC deu chua 0). Xuong 748 ms (`rf_narrow`) bat dau
mat (-0,292, KTC chua 0 sat bien) va xuong 636 ms (`unet1d`) thi mat ro (-0,804, KTC khong chua 0).
**Khuyen nghi:** RF ~1,5 s la du; 1,5 s la ban le, khong phai 0,8 s va cung khong can 3 s.
Con so nay khop voi lap luan sinh ly cua bai (mot cua so ~1,5 s chua tron mot chu ky RR thai nhi
o 120-160 nhip/phut, du de mang ngu canh nhip truoc va nhip sau).

**Luu y: day la suy luan tu 7 diem quan sat khong duoc ngau nhien hoa theo RF**, va `unet1d`
dat RF lon bang **giam mau** chu khong bang gian no nen no khong nam tren cung mot truc voi
5 kien truc kia. Do la mot **gia thuyet co du lieu ho tro**, khong phai mot quan he da chung minh.

## 5. TRAN F1 DA CHE MAT MOT HIEU UNG THAT -- `cnn_wide`

Day la truong hop kiem chung truc tiep canh bao cua nhiem vu:

* Tren **thang F1**: `cnn_wide` - `tcn` = **-0,80**, KTC95 [-2,40; **+0,13**] -- **KTC CHUA 0**,
  Wilcoxon p = 0,099, Holm 0,30. Mot bao cao thong thuong se viet "khong khac biet co y nghia"
  roi **dung lai o do**.
* Tren **thang logit**: **-0,447**, KTC95 [-0,745; **-0,156**] -- **KTC KHONG CHUA 0**.

Nguyen nhan chinh xac doc duoc tu bang B3: tren 19 chu the DE, `cnn_wide` - `tcn` = **-0,04 diem F1**
[-0,15; +0,09] (ca hai deu dung sat 100, thang F1 khong con cho de khac nhau), trong khi tren
3 chu the KHO la **-5,61** [-16,19; +1,55] -- KTC rong den muc vo dung voi n = 3. Trung binh F1
bi 19 gia tri bao hoa keo ve 0 con phuong sai bi 3 gia tri kho lam no tung, nen kiem dinh mat luc.
Thang logit tra lai do phan giai o vung gan 100 va hieu ung hien ra deu tren ca hai nhom
(de19 -0,452 [-0,78; -0,14], kho3 -0,419 [-1,28; +0,16]) -- tuc **hieu ung KHONG tap trung o
nhom kho**, dung nhu ket luan LUONGCUC da rut ra cho bien "them du lieu".

**Ket luan phuong phap luan cho bai bao:** voi 19/22 chu the o tran, **thang F1 khong con du do
phan giai de xep hang kien truc**. Moi so sanh kien truc trong bai phai bao cao kem thang logit.
Neu chi bao cao F1, bai se ket luan sai rang `cnn_wide` tuong duong TCN.

## 6. Ket qua bien the (VIEC 2 -- 3 bien the da chay)

**Bien the 1-2: truong tiep nhan** (`rf_wide` 3.052 ms, `rf_narrow` 748 ms) -- xem muc 4.
Ket qua: rong hon KHONG giup (TOST tuong duong), hep hon CO HAI nhung chua dat muc y nghia
sau Holm (-0,71 diem, Wilcoxon p = 0,028, Holm p = 0,11; logit -0,292 KTC [-0,675; +0,117]).

**Bien the 3: da thang do** (`tcn_ms`, 3 nhanh gian no song song (1,2,4) / (2,8,16) / (8,16,32),
gop bang 1x1). Ket qua: **TUONG DUONG** (-0,02 diem, TOST p < 0,0001; logit +0,035 [-0,250; +0,274]),
nhung **dat hon 19% thoi gian may** (288 so voi 242 ms/buoc). **Khong co ly do de doi sang.**

**Diem cuoi thu cap -- jitter thoi diem** (do o 1000 Hz voi nhan goc, am = tot hon):

| kien truc | hieu jitter so voi `tcn` | KTC95 | Wilcoxon | T/H/B |
|---|---:|---|---:|---:|
| `rf_wide` | **-0,197 ms** | [-0,327; -0,065] | 0,013 | 6/0/16 |
| `tcn_ms` | -0,037 ms | [-0,230; +0,160] | 0,61 | 10/0/12 |
| `unet1d` | +0,115 ms | [-0,139; +0,352] | 0,26 | 13/0/9 |
| `cnn_wide` | +0,151 ms | [-0,165; +0,520] | 0,26 | 14/0/8 |
| `rf_narrow` | +0,168 ms | [+0,007; +0,327] | 0,068 | 14/0/8 |
| `cnn_l` | +0,725 ms | [+0,372; +1,155] | 0,0004 | 18/0/4 |

`rf_wide` la **ung vien duy nhat co mot diem cuoi tot hon TCN voi KTC khong chua 0**: jitter
giam 0,197 ms (3,60 so voi 3,80 ms), thang 16/22 chu the, va TB 4 kenh cung tot hon +0,20
[+0,01; +0,38]. Doi lai no ton +2,7% tham so va +8% thoi gian moi buoc.

**Khuyen nghi (khong phai ket luan):** giu TCN lam mo hinh san xuat. `rf_wide` la kien truc DUY
NHAT dang mot lan chay xac nhan o giao thuc day du 11 fold, va chi vi jitter -- KHONG vi F1.
**Canh bao:** jitter la mot trong 6 diem cuoi duoc kiem o day va ket qua nay la **hau kiem**;
p = 0,013 khong song sot neu hieu chinh cho 6 diem cuoi x 6 kien truc.

## 7. Hieu ung tap trung o vai ban kho, hay trai deu?

Nhiem vu yeu cau kiem: neu mot bien the hon/kem, do la tren TAT CA chu the hay chi vai ban kho?

* `cnn_l`: kem tren **20/22** chu the. Tren thang logit, de19 -1,728 [-2,22; -1,20] va
  kho3 -1,074 [-1,91; -0,65]. Hieu ung **trai deu**, thuc ra con manh hon o nhom DE tren thang logit.
  Tren thang F1 no trong nhu tap trung o nhom kho (de19 -0,95 so voi kho3 -16,75), nhung do la
  **he qua toan hoc cua tran 100** -- dung mo tuong cu nhu LUONGCUC da canh bao.
* `cnn_wide`, `unet1d`: cung dang -- deu tren thang logit, gia tap trung tren thang F1.
* `rf_wide`: thang 11 / hoa 5 / thua 6, kho3 -0,10 [-0,78; +0,96]. Day la **hoa that**, khong phai
  hoa do trung binh trung hoa hai chieu lech nguoc nhau.
* `tcn_ms`: thang 9 / hoa 8 / thua 5. Cung la hoa that.

## 8. Bang cu (`arch_loro_merged.json`) co bi rut khong?

**Khong rut so, nhung PHAI thoi hieu luc suy luan cua no.** Ba dieu can noi dung:

1. Bang cu do o giao thuc **phan loai cua so 300 ms, 20 ban ghi = 5 chu the x 4 dao trinh,
   leave-one-RECORD-out**. Con so 92,43 / 91,07 va TOST +0,73 [+0,18; +1,22] van la con so dung
   **cua giao thuc do**. Khong co gi bia, khong co gi sai so hoc. Khong rut lai.
2. Nhung `cnn_l` cua bang cu **khong phai cung mot vat** voi `cnn_l` o day. Ban goc co MaxPool
   va xuat MOT nhan cho ca cua so 300 ms; de chuyen sang chuoi-sang-chuoi (1 logit moi mau) phai
   bo MaxPool, va viec do keo RF xuong con **60 ms**. Day la dac tinh cua ho kien truc do khi bi
   buoc sang bai toan chuoi-sang-chuoi, khong phai mot loi cai dat. Nhung no co nghia la
   **bang cu khong tra loi duoc cau hoi "dung kien truc nao cho mo hinh san xuat"**.
3. Do do: **`arch_loro_merged.json` khong duoc dung lam can cu chon kien truc trong bai bao.**
   No van dung cho dung cai no do (so sanh ho kien truc o bai toan phan loai cua so). `arch22.json`
   la bang duy nhat duoc trich dan cho quyet dinh kien truc.

Neu ban thao hien tai co cau nao ham y "khao sat cua chung toi xep cnn_l cao hon nhung chung toi
dung TCN", cau do phai bi xoa -- no khong con dung o giao thuc hien hanh.

## 9. Ket luan

1. **TCN la lua chon dung.** Khong doi.
2. Cau hoi mo tu vong truoc **da dong**: dau hieu dao nguoc o giao thuc hien hanh, `cnn_l` kem
   `tcn` -3,10 diem / -1,638 logit, thua 20/22.
3. **Kien truc khong quan trong, mien la truong tiep nhan >= ~1,5 s.** Trong khoang 1,5-3,0 s,
   ba kien truc khac nhau ve cau truc (`tcn`, `tcn_ms`, `rf_wide`) hoa nhau o muc TOST bien 1,0.
   Duoi 0,8 s thi hong. Day la mot phat bieu **co the kiem chung va co gia tri cho bai bao**,
   manh hon phat bieu "kien truc khong quan trong" chung chung.
4. **Thang F1 khong du do phan giai** cho cau hoi nay: no bao `cnn_wide` hoa, thang logit bao
   `cnn_wide` thua that.
5. Du dia 6,36 diem "bo do" tren CinC **khong lay lai duoc bang cach doi ho kien truc**.
   Bay kien truc o cung ngan sach chi trai tren 3,11 diem F1, va sau Holm chi con 2 kien truc
   khac biet that -- ca hai deu KEM hon TCN. Neu muon 6,36 diem do, phai tim o cho khac
   (huan luyen, du lieu, ham muc tieu, hau xu ly) -- khong phai o so do khoi.

## 10. Han che

1. **Duoi-huan-luyen 3,5-3,9 lan so voi san xuat** (1.065-1.176 so voi 4.168 buoc toi uu moi fold), 3 fold
   thay vi 11, khong tang cuong. Chieu lech nay **thien ve ket luan hoa nhau**, nen hai ket luan
   TUONG DUONG (`rf_wide`, `tcn_ms`) la **khong bao thu**: mot kien truc co the doi hoi nhieu
   du lieu / buoc hon moi bat loi the, va thiet ke nay khong nhin thay dieu do. Cac ket luan
   KHAC BIET thi bao thu va dang tin hon.
2. **Nguong bi kiem duyet o bien luoi.** Luoi quet la 0,20-0,80; **7 trong 21 lua chon fold roi
   dung vao gia tri lon nhat 0,80**, trong do `rf_narrow` 2/3 va `unet1d` 2/3, con `tcn` **0/3**.
   Bien luoi lech **co loi cho chuan doi chung**. Mot phan thiet hai cua `unet1d` va `rf_narrow`
   co the la do luoi nguong chu khong phai do kien truc. Phai noi rong luoi truoc khi coi hai
   con so do la ket luan.
3. **Mot seed duy nhat (seed 0), 3 fold.** Vong truoc do do lech seed trung binh 0,28 diem tren
   20 chu the. Cac hieu so -0,71 va -0,80 cua `rf_narrow` / `cnn_wide` **cung bac do lon voi nhieu
   seed**; chi -3,10 cua `cnn_l` va -1,25 cua `unet1d` la ro rang vuot nhieu seed.
4. **n = 3 o nhom kho.** Moi con so "kho3" trong tai lieu nay co KTC rong den muc khong ket luan
   duoc gi (vi du `cnn_wide` kho3 -5,61 [-16,19; +1,55]). Chung duoc in ra de mo ta, khong de
   suy luan.
5. **Bien the sigma / dau ra hai dau chua chay.** Nhanh "dau ra" cua VIEC 2 con bo ngo; khong the
   noi gi ve viec doi sigma hay them dau hoi quy do lech co giam jitter khong.
6. **Khong co trung tam thu hai.** Toan bo bang nay do tren 22 chu the trong mien. Chua kiem
   xem thu tu xep hang kien truc co giu nguyen tren CinC 2013 (75 chu the doc lap) khong --
   va vong truoc da cho thay thu tu **co the dao** khi doi mien (kenh 0 co dinh: 90,34 tren 10
   ban ghi -> 69,33 tren 75 ban ghi).
7. **So sanh jitter la hau kiem** va khong duoc hieu chinh cho da so sanh (6 diem cuoi x 6 kien truc).
8. `unet1d` dat truong tiep nhan bang **giam mau** chu khong bang gian no, nen no khong nam tren
   cung truc voi 5 kien truc kia -- khong the quy thiet hai cua no thuan tuy cho RF.
9. **Chi khao sat o muc ~113k tham so.** Khong loai tru kha nang thu tu xep hang doi o quy mo khac
   (vi du `unet1d` von duoc thiet ke cho mang lon hon nhieu); o day `unet1d` re nhat (2,2 phut,
   70 ms moi buoc so voi 242 ms cua TCN) nen no la ung vien duy nhat dang thu lai o quy mo lon hon
   neu bao gio ngan sach suy luan tro thanh rang buoc.

---

## 11. Chay lai

```bash
# B1: dau doi dau (81 phut, 3 luong; cache tin hieu da co san o pilot_evidence/arch22_cache/)
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 FQRS_THREADS=3 \
  python pilot_evidence/arch22.py --archs tcn,cnn_l,cnn_wide,unet1d,rf_narrow,rf_wide,tcn_ms \
  --folds 3 --epochs 3 --bs 16 --seed 0 --budget 104

# B2: phan tich thong ke (vai giay, khong huan luyen lai)
python analysis/kientruc.py
```

Xem truoc thoi gian ma khong huan luyen: them `--calibrate`.
Bang tu dong sinh: `analysis/_kientruc_tables.md` (B1 doi dau, B2 hieu so, B3 de/kho,
B4 F1 tung chu the, B5 nguong da chon).
