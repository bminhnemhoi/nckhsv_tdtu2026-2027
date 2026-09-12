# Phan tich thong ke o DON VI CHU THE -- ban sua loi gia lap (pseudo-replication)

*Tao ngay 2026-09-11T22:32:53 boi `analysis/stats.py`. Bootstrap 10000 lan, seed 0, bien tuong duong delta = 1,0 diem F1.*

## 0. Loi da sua

| | Cach cu | Cach moi |
|---|---|---|
| Don vi phan tich | Cap (ban ghi x kenh), 20-88 cap | **Chu the** (TB 4 kenh truoc), n = 5-22 |
| Gia dinh doc lap | 4 kenh bung cua cung 1 phu nu coi la 4 quan sat doc lap | Kenh la do lap lai trong cum; chu the la don vi |
| KTC | t tren thang phan tram | Thang logit + bootstrap percentile |
| Bien thien | SD tren cap | Cluster bootstrap lay mau lai chu the |
| Da so sanh | khong hieu chinh | Holm cho ho 7 kien truc |
| Ket luan 'khong khac' | p > 0,05 | **TOST** bien 1,0 diem |

> **Gioi han cung cua n = 5.** Voi n = 5 chu the, Wilcoxon signed-rank hai phia co p NHO NHAT co the dat = 2/2^5 = 0,0625. Do do KHONG mot so sanh nao tren ADFECGDB (5 phu nu) co the dat p < 0,05 o muc chu the, bat ke hieu so lon den dau. Moi p < 0,05 tung bao cao tren tap nay deu la san pham cua gia lap.

## 1. Bang tong hop: moi so sanh chinh

| So sanh | n chu the | p cu (gia lap) | Don vi cu | p moi (muc chu the) | p sign test | Hieu so TB | KTC 95% bootstrap | KTC 95% t (bao thu) | Cliff delta | Doi ket luan? |
|---|---:|---:|---|---:|---:|---:|---|---|---:|---|
| ADFECGDB: FetalQRS-TCN vs TS (TB 4 kenh) | 5 | 5,72e-06 | 20 cap (ban ghi x kenh) | **0,0625** | 0,0625 | 18,49 | [6,38; 30,60] | [-1,81; 38,80] | 1,000 (lon) | **CO -- mat y nghia** |
| ADFECGDB: FetalQRS-TCN vs TS-PCA (TB 4 kenh) | 5 | 1,91e-06 | 20 cap (ban ghi x kenh) | **0,0625** | 0,0625 | 6,40 | [4,70; 8,09] | [3,69; 9,10] | 0,920 (lon) | **CO -- mat y nghia** |
| ADFECGDB: FetalQRS-TCN vs Prominence (TB 4 kenh) | 5 | 1,91e-06 | 20 cap (ban ghi x kenh) | **0,0625** | 0,0625 | 11,06 | [7,80; 14,51] | [5,73; 16,38] | 1,000 (lon) | **CO -- mat y nghia** |
| ADFECGDB: FetalQRS-TCN vs TS (kenh PSD mu nhan) | 5 | 0,1250 | 5 cap (kenh PSD) | **0,1250** | 0,3750 | 11,53 | [4,25; 19,58] | [-0,38; 23,44] | 0,920 (lon) | khong |
| ADFECGDB: FetalQRS-TCN vs TS-PCA (kenh PSD mu nhan) | 5 | 0,0625 | 5 cap (kenh PSD) | **0,0625** | 0,0625 | 2,14 | [1,54; 2,68] | [1,23; 3,05] | 0,680 (lon) | khong |
| ADFECGDB: FetalQRS-TCN vs Prominence (kenh PSD mu nhan) | 5 | 0,0625 | 5 cap (kenh PSD) | **0,0625** | 0,0625 | 7,18 | [3,27; 11,47] | [0,90; 13,46] | 1,000 (lon) | khong |
| PhysioNet: mo hinh 22 chu the vs mo hinh 5 chu the (TB 4 kenh) | 5 | 0,2445 | 20 cap (chu the x kenh) | **0,8125** | 1,0000 | 1,24 | [-0,35; 3,01] | [-1,44; 3,91] | 0,200 (nho) | khong |
| B2: mo hinh 22 chu the vs mo hinh 5 chu the (TB 4 kenh) | 7 | 0,0156 | 28 cap (chu the x kenh) | **0,4688** | 0,4531 | 0,77 | [-0,16; 2,38] | [-1,15; 2,68] | 0,102 (khong dang ke) | **CO -- mat y nghia** |
| B1: mo hinh 22 chu the vs mo hinh 5 chu the (TB 4 kenh) | 10 | 4,32e-09 | 40 cap (chu the x kenh) | **0,0039** | 0,0215 | 5,71 | [2,12; 10,17] | [0,79; 10,62] | 0,500 (lon) | khong |
| ALL: mo hinh 22 chu the vs mo hinh 5 chu the (TB 4 kenh) | 22 | 1,49e-08 | 88 cap (chu the x kenh) | **0,0029** | 0,0525 | 3,12 | [1,27; 5,48] | [0,76; 5,48] | 0,264 (nho) | khong |
| B1: mo hinh 22 vs mo hinh 5 (kenh PSD mu nhan) | 10 | 0,0371 | 10 chu the (kenh PSD) | **0,0371** | 0,0215 | 3,85 | [0,05; 9,62] | [-2,49; 10,19] | 0,360 (trung binh) | khong |
| ALL: mo hinh 22 vs mo hinh 5 (kenh PSD mu nhan) | 22 | 0,0074 | 22 chu the (kenh PSD) | **0,0056** | 0,0075 | 2,09 | [0,23; 4,99] | [-0,63; 4,82] | 0,153 (nho) | khong |
| CinC 2013 zero-shot: mo hinh 22 vs mo hinh 5 (kenh 0 co dinh) | 10 | 3,99e-05 | 40 cap (ban ghi x kenh) | **0,0156** | 0,0156 | 13,01 | [3,58; 24,58] | [0,18; 25,83] | 0,230 (nho) | khong |
| CinC 2013 zero-shot: mo hinh 22 vs mo hinh 5 (TB 4 kenh) | 10 | 3,99e-05 | 40 cap (ban ghi x kenh) | **0,0312** | 0,1250 | 10,68 | [4,66; 16,73] | [3,40; 17,95] | 0,190 (nho) | khong |
| Tang 2 (ngu canh): TCN truong thu nhan 2 s vs CNN cua so ngan | 5 | -- | 60 hang (ban ghi x kenh x seed) | **0,0625** | 0,0625 | 4,49 | [1,58; 7,43] | [-0,29; 9,27] | 0,520 (lon) | -- |

Quy uoc hieu so: **A - B** voi A la cot dau trong ten so sanh (mo hinh, model_22, kien truc moi).

**Doc bang nay cho dung -- ba luu y quan trong:**

1. **Mat y nghia KHONG tu dong co nghia la mat hieu ung -- nhung voi TS thi mat that.** Voi TS-PCA va Prominence, p tang tu ~1e-6 len 0,0625 chi vi n = 5 lam san kiem dinh hang, con KTC 95% cua hieu so van **loai tru 0** ca o bootstrap lan o thang t (TS-PCA: [3,69; 9,10] diem theo t). Voi hai baseline nay, *huong* cua ket qua giu nguyen, chi la **khong duoc tuyen bo y nghia thong ke** tu 5 phu nu. Nhung voi **TS thi khac**: KTC 95% kieu t la **[-1,81; 38,80] -- chua ca 0**. Hieu so 18,49 diem hoan toan do bien thien giua 5 ban ghi, khong phai mot loi the on dinh. Bang baseline trong bai dang trinh bay ca ba nhu nhau; thuc te chung khong cung do chac.
2. **KTC bootstrap voi n = 5 cum la hep hon thuc te.** Cot 'KTC 95% t' bao thu hon; khi hai cot mau thuan thi tin cot t. Voi n = 5-7 nen bao cao ca hai.
3. **Sign test la kiem dinh bao thu nhat** va cho thay do manh that su: vi du 'ALL 22 chu the' co Wilcoxon p = 0,0029 nhung sign test p = 0,0525 -- tuc ket qua phu thuoc vao DO LON cua vai chu the, khong phai vao viec da so chu the deu cai thien.

## 2. Khoang tin cay cho cac con so dat tren tieu de

| Con so | n chu the | TB so hoc | KTC 95% kieu t tren % (SAI) | Vuot 100%? | **KTC 95% bootstrap (cho TB so hoc)** | Diem logit | KTC 95% logit |
|---|---:|---:|---|---|---|---:|---|
| ADFECGDB kenh PSD, mo hinh 5 chu the (99,21 da cong bo) | 5 | 99,21 | [97,35; 101,08] | **CO** | **[97,87; 99,95]** | 99,74 | [98,21; 99,96] |
| ADFECGDB TB 4 kenh, mo hinh 5 chu the (97,45 da cong bo) | 5 | 97,45 | [93,77; 101,13] | **CO** | **[94,94; 99,63]** | 99,00 | [90,65; 99,90] |
| Silesia B1 thai ky, mo hinh 5 chu the (kenh PSD) (93,30 da cong bo) | 10 | 93,30 | [83,67; 102,93] | **CO** | **[84,93; 99,37]** | 98,78 | [94,79; 99,72] |
| Silesia B1 thai ky, mo hinh 22 chu the (kenh PSD) (97,15 da cong bo) | 10 | 97,15 | [93,61; 100,69] | **CO** | **[94,00; 99,67]** | 99,60 | [97,85; 99,93] |
| CinC 2013 zero-shot, mo hinh 22 (kenh 0) (90,34 DA RUT -- xem ghi chu duoi bang) | 10 | 90,34 | [81,74; 98,95] | khong | **[83,10; 97,01]** | 97,26 | [88,25; 99,41] |
| CinC 2013 zero-shot, mo hinh 5 (kenh 0) (77,34 DA RUT -- xem ghi chu duoi bang) | 10 | 77,34 | [56,92; 97,75] | khong | **[59,66; 92,77]** | 93,43 | [66,95; 99,01] |

**Hai uoc luong diem khac nhau, dung nham la sai.**

> **GHI CHU RUT LAI (12/09/2026).** Hai hang CinC trong bang tren do tren **mau 10/75 ban ghi** voi quy
> tac **kenh 0 co dinh chon HAU KIEM**. Ca hai con so 90,34 va 77,34 **DA BI RUT**. Tren **du 75 ban ghi**,
> quy tac mu nhan PSD cho **79,40** (mo hinh 22) va **71,21** (mo hinh 5), con chinh quy tac kenh 0 co dinh
> chi cho **69,33** / **58,72** -- tuc no la quy tac TE NHAT trong bon, chu khong phai tot nhat.
> Nguon: `benchmark_dpss/eval_cinc75.json`. Cac KTC bootstrap trong bang nay van dung *cho mau 10 ban ghi*
> nhung khong con mo ta ket qua hien hanh.

- Cot *KTC bootstrap* la khoang cho **trung binh so hoc** cua F1 tren cac chu the -- day la dai luong ma bai bao dang bao cao (99,21 / 93,30 / va cho CinC la **79,40 tren du 75 ban ghi**; con so 90,34 tung ghi o day DA BI RUT -- xem ghi chu tren). Dung cot nay trong bang ket qua chinh. No khong bao gio vuot 100% vi chi lay lai mau tu cac gia tri quan sat.
- Cot *logit* la trung binh tren thang logit roi doi nguoc -- day la **F1 dien hinh cua mot chu the moi**, keo ve phia cac gia tri cao. Vi vay no CO THE cao hon trung binh so hoc (vi du Silesia B1: TB so hoc 93,30 nhung diem logit 98,78, vi phan bo lech trai co ban ghi thap keo trung binh so hoc xuong). Dung cot nay khi noi ve **mot ca lam sang moi**, va phai noi ro la dai luong KHAC voi trung binh so hoc -- neu bao cao nham, con so se bi thoi phong.
- KTC t tren thang phan tram la cot duy nhat **vuot 100%** -- day chinh la loi dang co trong bai.

Chu y do rong that su: ADFECGDB n = 5 cho KTC rong vai diem F1 (khong phai +-1,5 nhu SD goi y); Silesia B1 va CinC 2013 rong hon 10-30 diem.

## 3. Ho kien truc: kiem dinh tuong duong (TOST), bien 1,0 diem F1

| Kien truc | Macro F1 | Hieu so vs cnn_dil | p Wilcoxon (n=5) | p sau Holm | KTC 90% (t) | KTC 90% bootstrap | p TOST | Ket luan |
|---|---:|---:|---:|---:|---|---|---:|---|
| cnn_l | 92,43 | 0,73 | 0,1250 | 0,6250 | [-0,02; 1,47] | [0,18; 1,22] | 0,2380 | KHONG KET LUAN DUOC (KTC 90% rong hon bien tuong duong) |
| mlp | 91,64 | -0,07 | 1,0000 | 1,0000 | [-5,23; 5,10] | [-3,47; 3,52] | 0,3596 | KHONG KET LUAN DUOC (KTC 90% rong hon bien tuong duong) |
| cnn_gru | 91,59 | -0,12 | 0,8125 | 1,0000 | [-1,06; 0,82] | [-0,72; 0,54] | 0,0579 | KHONG KET LUAN DUOC (KTC 90% rong hon bien tuong duong) |
| tcn | 91,07 | -0,64 | 0,1875 | 0,7500 | [-1,40; 0,12] | [-1,13; -0,11] | 0,1827 | KHONG KET LUAN DUOC (KTC 90% rong hon bien tuong duong) |
| resnet1d | 90,90 | -0,81 | 0,6250 | 1,0000 | [-2,18; 0,57] | [-1,79; 0,09] | 0,3887 | KHONG KET LUAN DUOC (KTC 90% rong hon bien tuong duong) |
| cnn_m | 88,76 | -2,95 | 0,0625 | 0,4375 | [-5,21; -0,69] | [-4,55; -1,47] | 0,9300 | KHONG KET LUAN DUOC (KTC 90% rong hon bien tuong duong) |
| linear | 37,47 | -54,24 | 0,0625 | 0,4375 | [-58,44; -50,04] | [-56,41; -50,49] | 1,0000 | KHAC BIET vuot bien 1,0 diem |

- Kien truc tot nhat: **cnn_l**, hon cnn_dil **0,73** diem (tuyen bo cu trong README: +0,41).
- Bien do giua 7 kien truc phi tuyen: 3,67 diem F1.
- So kien truc **chung minh duoc tuong duong** trong bien 1,0 diem: **0/7**.
- So kien truc **khong ket luan duoc**: **6/7**.

> Tuyen bo '8 kien truc khong phan biet duoc' dua tren p > 0,05 -- day la VANG MAT BANG CHUNG, khong phai bang chung tuong duong. TOST o bien 1,0 diem moi la kiem dinh dung.

### 3.1 Day la DAO CHIEU lon nhat cua toan bo nhiem vu

Tuyen bo trong README va trong tieu de bai -- *'8 kien truc khong phan biet duoc, khong cai nao khac cnn_dil 26k tham so'* -- **khong song sot qua kiem dinh tuong duong**:

- **0/7** kien truc chung minh duoc tuong duong trong bien +-1,0 diem F1. Sau khi sua don vi phan tich, du lieu 5 ban ghi **khong du** de ket luan bat ky hai kien truc nao la nhu nhau.
- Ket luan cu duoc rut ra tu 'p > 0,05'. Voi n = 5 chu the, p > 0,05 la ket qua **gan nhu duong nhien** (nguong kha thi nho nhat la 0,0625) -- no do do cong suat thap, khong do cac kien truc giong nhau.
- Nguoc lai, **cnn_m KEM HON ro**: hieu so -2,95 diem, KTC 90% bootstrap [-4,55; -1,47] nam **hoan toan ngoai** bien +-1,0. Tuyen bo 'sau kien truc nam trong 1,5 diem cua nhau' khong dung voi cnn_m.
- **cnn_l tot hon** cnn_dil 0,73 diem voi KTC 90% bootstrap [0,18; 1,22] -- khong loai tru duoc kha nang vuot bien 1,0. Neu cham sat, cnn_l co the thuc su tot hon, chi la chua du bang chung.

**Cach viet lai an toan:** thay 'khong kien truc nao khac biet' bang *'voi n = 5 chu the, nghien cuu nay khong du cong suat de phan biet cac kien truc trong bien 1,0 diem F1; hieu so quan sat duoc nam trong khoang -2,95 den +0,73 diem, nho hon nhieu so voi +11,0 diem cua tang front-end'*. Cau nay VAN giu duoc thong diep chinh (front-end quan trong hon kien truc) ma khong tuyen bo dieu chua chung minh.

## 4. Cong tu choi: AUROC voi cluster bootstrap theo BAN GHI

| Dai luong | Gia tri | KTC 95% (bootstrap theo ban ghi, n = 10 cum) | Bao cao cu |
|---|---:|---|---:|
| AUROC (12 SQI co dien, CinC 2013) | 0,929 | [0,830; 0,982] | 0,929 |
| Loi ich F1 o do phu 80% | 7,49 | [2,94; 11,54] | 7,37 |
| AUROC nhom to-po (TDA) | 0,566 | chua tinh duoc (can huan luyen lai) | 0,566 |
| **AUROC TRONG ban ghi** (TB tren 5 ban ghi co ca doan tot lan xau) | **0,721** | [0,517; 0,898] | chua tung bao cao |

AUROC tung ban ghi: a01 = 0,914, a02 = n/a (khong co doan xau), a03 = n/a (khong co doan xau), a04 = n/a (khong co doan xau), a05 = n/a (khong co doan xau), a06 = 0,390, a07 = 0,889, a08 = n/a (khong co doan xau), a09 = 0,886, a10 = 0,526

> 600 doan 4 s den tu 10 ban ghi: doan trong cung mot ban ghi tuong quan manh. KTC dung phai lay mau lai BAN GHI, khong phai doan.

**Phat hien moi, quan trong:** AUROC gop 0,93 phan lon la hieu ung GIUA ban ghi (tach ban ghi tot khoi ban ghi xau), khong phai kha nang xep hang doan BEN TRONG mot ban ghi. Trong ung dung thuc te (mot thai phu, mot phien do) chi co AUROC TRONG ban ghi moi co y nghia.

5/10 ban ghi CinC khong co doan xau nao (mo hinh chay hoan hao suot ban ghi), nen chung khong dong gop gi vao AUROC gop. Con so 0,929 tren thuc te chu yeu tra loi cau hoi *'ban ghi nay co phai ban ghi xau khong'*, chu khong phai *'doan 4 giay nay trong ban ghi cua benh nhan nay co dang tin khong'* -- trong khi cong tu choi duoc ban nhu la thu hai. Day la mot gioi han phai neu ro, va la ly do ket qua nay chua the tuyen bo la dung duoc tai giuong benh.

## 5. CAC KET LUAN DOI CHIEU

| So sanh | p cu | Don vi cu | p moi (chu the) | n | Ket luan |
|---|---:|---|---:|---:|---|
| ADFECGDB: FetalQRS-TCN vs TS (TB 4 kenh) | 5,72e-06 | 20 cap (ban ghi x kenh) | 0,0625 | 5 | DAO CHIEU: tu 'co y nghia' thanh 'KHONG co y nghia' |
| ADFECGDB: FetalQRS-TCN vs TS-PCA (TB 4 kenh) | 1,91e-06 | 20 cap (ban ghi x kenh) | 0,0625 | 5 | DAO CHIEU: tu 'co y nghia' thanh 'KHONG co y nghia' |
| ADFECGDB: FetalQRS-TCN vs Prominence (TB 4 kenh) | 1,91e-06 | 20 cap (ban ghi x kenh) | 0,0625 | 5 | DAO CHIEU: tu 'co y nghia' thanh 'KHONG co y nghia' |
| B2: mo hinh 22 chu the vs mo hinh 5 chu the (TB 4 kenh) | 0,0156 | 28 cap (chu the x kenh) | 0,4688 | 7 | DAO CHIEU: tu 'co y nghia' thanh 'KHONG co y nghia' |
| TUYEN BO TIEU DE: '8 kien truc khong phan biet duoc / khong cai nao khac cnn_dil' | p > 0,05 (vang mat bang chung) | 20 cap (ban ghi x kenh), khong hieu chinh da so sanh | 1,0000 | 5 | DAO CHIEU: TOST bien 1,0 diem cho 0/7 kien truc tuong duong. 'Khong khac biet' thuc chat la 'khong du cong suat'. Ngoai ra cnn_m KEM HON vuot bien (KTC 90% bootstrap [-4,55; -1,47]). |

## 6. Nhung gi KHONG kiem chung lai duoc tu artefact hien co

| Muc | Ly do | He qua |
|---|---|---|
| Tang 1 -- front-end dai thong (+11,00 diem, README ghi p < 0,001) | pilot_evidence/band_ablation.json chi luu tong hop (macro_F1 +- sd cho moi dai), KHONG luu F1 tung ban ghi x kenh. Khong the ghep cap lai o muc chu the, va khong the kiem chung p da cong bo. | p < 0,001 cho tang 1 hien KHONG KIEM CHUNG DUOC. Phai chay lai co luu per-record. |
| AUROC cua nhom dac trung to-po (0,566) va nhom ket hop | fsqi/gate_segments.csv chi luu p_bad cua bo phan loai SQI co dien; muon bootstrap theo cum phai huan luyen lai. | 0,566 van dung lam ket luan phu dinh, nhung chua co KTC theo cum. |
| Bien thien theo seed | Tat ca ket qua chinh chay 1 seed (tru seq_loro co 3 seed). | Moi KTC o day chi bao phu bien thien GIUA CHU THE, khong bao phu bien thien huan luyen. |

## 7. Viec phai sua trong bai, theo thu tu uu tien

| # | Phai sua | Sua thanh |
|---:|---|---|
| 1 | Tuyen bo tieu de '8 kien truc khong phan biet duoc' | 'Nghien cuu nay khong du cong suat (n = 5 chu the) de phan biet cac kien truc trong bien 1,0 diem F1; hieu so quan sat nam trong -2,95 den +0,73 diem.' **Day la thay doi bat buoc** -- tuyen bo hien tai la ket luan tuong duong rut ra tu p > 0,05. |
| 2 | Moi p tren ADFECGDB (1,9e-6, 5,7e-6, ...) | Bo han. Thay bang hieu so + KTC 95% o muc chu the, kem cau 'n = 5 chu the: p < 0,05 la bat kha thi voi kiem dinh hang hai phia'. |
| 3 | Bang baseline trinh bay ca 3 nhu nhau | Tach ro: TS-PCA va Prominence co KTC loai tru 0; **TS thi khong** (KTC t [-1,81; 38,80]). |
| 4 | '99,21 +- 1,50' va cac '+- SD' khac | Trung binh + KTC 95% cluster bootstrap cho TRUNG BINH SO HOC (cot dam trong Muc 2). Neu muon noi ve 'mot ca moi' thi dung KTC logit va **noi ro do la dai luong khac**. |
| 5 | 'B2: cai thien co y nghia, p = 0,016' | Bo. O muc chu the p = 0,47, Cliff delta 0,10 (khong dang ke). |
| 6 | 'Tang 2 (ngu canh) +4,53, p = 0,0000' | p tinh tren 60 hang gom ca 3 seed -- gia lap 12 lan. O muc ban ghi: +4,49 diem, p = 0,0625, KTC t [-0,29; 9,27]. Bao cao hieu so, bo p. |
| 7 | 'AUROC cong tu choi 0,929' | Them KTC cluster bootstrap [0,830; 0,982] VA con so AUROC trong ban ghi 0,721 -- vi ung dung lam sang chi dung duoc con so thu hai. |
| 8 | 'Tang 1 front-end +11,00, p < 0,001' | Chay lai co luu F1 tung ban ghi x kenh roi kiem dinh o muc chu the. Hien khong kiem chung duoc, va (theo P1) lai do tren GBM chu khong tren TCN. |

**Nguyen tac chung cho ban sua:** bao cao **uoc luong hieu so kem KTC** lam ket qua chinh; p-value la phu va phai luon di kem n chu the. Voi n = 5-10, khong tuyen bo y nghia thong ke o bat ky dau; voi ket luan 'khong khac nhau', bat buoc dung TOST kem bien duoc dinh truoc.
