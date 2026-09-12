# -*- coding: utf-8 -*-
"""
Bo nap du lieu NInFEA -- Non-Invasive Multimodal Foetal ECG-Doppler Dataset.

  Sulas E, Urru M, Tumbarello R, Raffo L, Sameni R, Pani D.
  "A non-invasive multimodal foetal ECG-Doppler dataset for antenatal cardiology research."
  Scientific Data 2021;8:30. DOI 10.1038/s41597-021-00811-3
  PhysioNet: https://physionet.org/content/ninfea/1.0.0/
  Giay phep: Open Data Commons Attribution License v1.0
  Kich thuoc: 2,0 GB giai nen (792,9 MB zip). wfdb_format: ~7,8-15 MB moi ban ghi.

NOI DUNG (doi chieu tren PhysioNet 2026-09-11 + .hea ban ghi 1/2/3 da tai)
  60 muc ghi tu 39 SAN PHU (=> co san phu dong gop nhieu muc ghi -- xem canh bao chu the ben duoi)
  Tuoi thai: tuan 21..27 (tam ca nguyet 2, som hon Silesia B1 va CinC 2013)
  Moi muc ghi: 27 kenh dien sinh ly = 24 don cuc BUNG (uni_abd1..24) + 3 luong cuc NGUC ME
               (bi_tho1..3); dien cuc tham chieu o hong phai me.
               Cong them: matrsp (ho hap me), saw, sync, dc1..dc4 -> TONG 34 kenh trong .hea
  fs = 2048 Hz, 22 bit (do phan giai 71,5 nV), bang thong 0-550 Hz
  Do dai trung binh 30,6 s +/- 20,6 s (7,50 .. 119,80 s) -- RAT NGAN so voi Silesia (5-20 phut)
  Kem theo: anh Doppler xung (PWD) dong bo trong pwd_images/, va script Matlab/Octave
            code/envelope_extraction.m de trich bao hinh PWD tu anh.

NHAN THAM CHIEU -- DIEM QUAN TRONG NHAT
  * Nhan KHONG lay tu ECG nguc me, va CUNG KHONG duoc phan phoi san.
    Da liet ke wfdb_format_ecg_and_respiration/: CHI co <n>.dat va <n>.hea, khong co .qrs/.fqrs/.atr,
    khong co RECORDS trong thu muc do (404). Thu muc goc chi co 4 thu muc + LICENSE + RECORDS + SHA256SUMS.
  * Su that tham chieu la DINH V (van dong that trai) tren anh PWD thai, do chuyen gia gan nhan
    BANG MAT trong bai Sci Data. Day la moc CO HOC, khong phai moc DIEN HOC.
  * Do do dung sai danh gia cho bo nay KHAC voi cac bo co dFECG:
      - tre dien-co (electromechanical delay) giua R dien va V co hoc: bai dung nguong
        "khoang cach hop ly ve lam sang" < 200 ms;
      - trong pham vi do, sai so gan moc QRS van lay cua so 50 ms.
    => KHONG duoc so F1 tren NInFEA truc tiep voi F1 tren ADFECGDB/Silesia B2 (dung sai 50 ms so
       voi dFECG). Neu bao cao chung mot bang, phai tach cot "nguon nhan" va "dung sai".
  * Ket qua tham chieu cua chinh tac gia (technical validation, do QRS thai): trung vi
    accuracy 0,79 / Se 0,97 / PPV 0,81; trich duoc fECG tren 95,5 % doan tin hieu.

CANH BAO CHU THE
  60 muc ghi != 60 chu the. 39 san phu -> mot so nguoi co 2-3 muc ghi. PhysioNet KHONG cong bo
  bang anh xa muc ghi -> san phu trong thu muc du lieu. Cho toi khi lay duoc bang do (bang bo sung
  cua bai Sci Data), moi phan chia huan luyen/kiem thu phai coi 60 muc ghi la CO PHU THUOC
  (cluster khong biet) -- an toan nhat la chi dung NInFEA nhu tap KIEM THU ZERO-SHOT, khong dua
  vao huan luyen, va bao cao khoang tin cay bang bootstrap theo muc ghi CO ghi ro han che nay.

DINH DANG THAT (.hea ban ghi 1, da tai ve)
  1 34 2048 57490
  1.dat 32 1119216.6963(598581736)/uV 0 0 570611155 -418 0 uni_abd1
  ...
    - WFDB format 32 = int32 LITTLE-ENDIAN, 34 kenh xen ke theo mau, .dat khong header
    - kiem chung kich thuoc: 57490 mau x 34 kenh x 4 byte = 7 818 640 byte = Content-Length. KHOP.
    - physical = (raw - baseline) / gain  [uV];  baseline nam trong ngoac sau gain
    - cac kenh dc1..dc4 va sync co gain = 1 va baseline = -2147483647 -> gia tri vat ly vo nghia,
      KHONG dung; chi 'sync' huu ich nhu moc dong bo ECG<->PWD (dung mau tho).
    - phan duoi .hea la chu thich '#' liet ke offset dien ap thiet bi DA BI TRU khoi tin hieu.

API
  ninfea_dir()                        -> thu muc goc NInFEA
  list_records()                      -> ['1', '2', ...] cac ban ghi co du .hea + .dat tai ve
  read_header(rec)                    -> dict(fs, n_sig, n_samp, names, gains, baselines)
  read_signals(rec)                   -> ([n_sig, N] uV, header)
  load(rec, fs_out=1000)              -> (abd[24, N] mV, fqrs=None, meta)
  load_thoracic(rec, fs_out=1000)     -> [3, N] mV (bi_tho1..3, dung de tru mau me)
  pwd_image_path(rec)                 -> duong dan anh PWD (neu da tai)
  fetal_qrs(rec)                      -> NotImplementedError kem huong dan
"""
from __future__ import annotations
import os
import re
import glob
from math import gcd

import numpy as np
from scipy import signal as sg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DIR = os.path.join(ROOT, 'model', 'data', 'ninfea')
WFDB_SUBDIR = 'wfdb_format_ecg_and_respiration'
BIN_SUBDIR = 'bin_format_ecg_and_respiration'
PWD_SUBDIR = 'pwd_images'

BASE_URL = 'https://physionet.org/files/ninfea/1.0.0/'
CITE = ('Sulas E, Urru M, Tumbarello R, Raffo L, Sameni R, Pani D. Sci Data. 2021;8:30. '
        'DOI 10.1038/s41597-021-00811-3')
LICENCE = 'Open Data Commons Attribution License v1.0'

N_RECORDS_TOTAL = 60          # muc ghi
N_SUBJECTS = 39               # san phu -> muc ghi KHONG doc lap
GA_WEEKS = (21, 27)
FS_ORIG = 2048.0

#: Bo nay KHONG phan phoi nhan QRS thai (xem phan "NHAN THAM CHIEU" o tren).
HAS_FETAL_ANNOTATIONS = False
#: Dung sai danh gia do tac gia de xuat: tre dien-co toi da, va cua so gan moc QRS.
TOL_ELECTROMECHANICAL_MS = 200.0
TOL_QRS_MS = 50.0

ABD_PREFIX = 'uni_abd'
THO_PREFIX = 'bi_tho'
JUNK_CHANNELS = ('dc1', 'dc2', 'dc3', 'dc4', 'saw')   # gain=1, baseline=-2147483647 -> vo nghia

_FMT_DTYPE = {16: '<i2', 61: '>i2', 32: '<i4', 24: None, 160: '<u2', 80: 'u1'}


def ninfea_dir(path=None):
    """Thu muc goc NInFEA (chua wfdb_format_ecg_and_respiration/...)."""
    for cand in (path, os.environ.get('NINFEA_DIR'), DEFAULT_DIR):
        if cand and os.path.isdir(cand):
            return cand
    raise FileNotFoundError(
        f'Khong thay thu muc NInFEA. Da thu: {path!r}, $NINFEA_DIR, {DEFAULT_DIR!r}.\n'
        f'Tai bang: python model/download_more.py --only ninfea   (2,0 GB tu {BASE_URL})\n'
        f'Chi can thu muc {WFDB_SUBDIR}/ neu khong dung anh PWD (~600 MB).')


def wfdb_dir(path=None):
    d = ninfea_dir(path)
    sub = os.path.join(d, WFDB_SUBDIR)
    return sub if os.path.isdir(sub) else d


def list_records(path=None):
    """Ban ghi co DU .hea va .dat, sap theo so."""
    d = wfdb_dir(path)
    out = []
    for hea in glob.glob(os.path.join(d, '*.hea')):
        rec = os.path.splitext(os.path.basename(hea))[0]
        if os.path.isfile(os.path.join(d, rec + '.dat')):
            out.append(rec)
    return sorted(out, key=lambda r: (0, int(r)) if r.isdigit() else (1, r))


def read_header(rec, path=None):
    """Doc .hea WFDB. Tra dict(fs, n_sig, n_samp, names, gains, baselines, fmts, dat)."""
    d = wfdb_dir(path)
    hea = os.path.join(d, str(rec) + '.hea')
    if not os.path.isfile(hea):
        raise FileNotFoundError(hea)
    with open(hea, 'r', encoding='utf-8', errors='replace') as f:
        lines = [ln.rstrip('\n') for ln in f]
    body = [ln for ln in lines if ln.strip() and not ln.lstrip().startswith('#')]
    head = body[0].split()
    n_sig = int(head[1])
    fs = float(head[2]) if len(head) > 2 else 250.0
    n_samp = int(head[3]) if len(head) > 3 else None

    names, gains, baselines, fmts, dat_files, units = [], [], [], [], [], []
    for ln in body[1:1 + n_sig]:
        tok = ln.split()
        dat_files.append(tok[0])
        fmts.append(int(re.match(r'(\d+)', tok[1]).group(1)))
        m = re.match(r'([-\d.eE+]+)(?:\((-?\d+)\))?(?:/(\S+))?', tok[2])
        g = float(m.group(1)) if m and m.group(1) else 200.0
        gains.append(g if g != 0 else 200.0)
        adc_zero = int(tok[4]) if len(tok) > 4 else 0
        baselines.append(int(m.group(2)) if (m and m.group(2) is not None) else adc_zero)
        units.append(m.group(3) if m and m.group(3) else 'mV')
        names.append(tok[8] if len(tok) > 8 else f'ch{len(names)}')
    return dict(record=str(rec), fs=fs, n_sig=n_sig, n_samp=n_samp, names=names, units=units,
                gains=np.asarray(gains, float), baselines=np.asarray(baselines, float),
                fmts=fmts, dat=dat_files[0], header_path=hea,
                duration_s=(n_samp / fs) if n_samp else None)


def read_signals(rec, path=None, channels=None):
    """
    Doc .dat -> (phys[n_sel, n_samp] microvolt, header).
    channels: danh sach TEN kenh (vd ['uni_abd1',...]) hoac None = tat ca.
    Doc theo memmap nen khong nap ca file vao RAM khi chi lay vai kenh.
    """
    d = wfdb_dir(path)
    h = read_header(rec, path)
    fmt = h['fmts'][0]
    if any(f != fmt for f in h['fmts']):
        raise NotImplementedError(f'{rec}: cac kenh khac dinh dang.')
    dt = _FMT_DTYPE.get(fmt)
    if dt is None:
        raise NotImplementedError(f'{rec}: WFDB format {fmt} chua ho tro (dung wfdb.rdrecord).')
    p = os.path.join(d, h['dat'])
    n_sig = h['n_sig']
    itemsize = np.dtype(dt).itemsize
    n_full = os.path.getsize(p) // (itemsize * n_sig)
    if h['n_samp'] and n_full < h['n_samp']:
        raise IOError(f'{rec}: .dat ngan hon header ({n_full} < {h["n_samp"]} mau) -- tai chua xong?')
    mm = np.memmap(p, dtype=dt, mode='r', shape=(n_full, n_sig))
    sel = list(range(n_sig)) if channels is None else [h['names'].index(c) for c in channels]
    n = h['n_samp'] or n_full
    phys = np.asarray(mm[:n, sel], dtype=np.float64).T
    phys = (phys - h['baselines'][sel, None]) / h['gains'][sel, None]   # microvolt
    del mm
    return phys, h


def abdominal_names(names):
    """24 ten kenh bung don cuc, dung thu tu uni_abd1..uni_abd24."""
    got = [n for n in names if n.startswith(ABD_PREFIX)]
    return sorted(got, key=lambda n: int(n[len(ABD_PREFIX):]))


def thoracic_names(names):
    got = [n for n in names if n.startswith(THO_PREFIX)]
    return sorted(got, key=lambda n: int(n[len(THO_PREFIX):]))


def _resample(x, fs_from, fs_to):
    if float(fs_from) == float(fs_to):
        return np.asarray(x, np.float32)
    g = gcd(int(round(fs_from)), int(round(fs_to)))
    return sg.resample_poly(np.asarray(x, np.float64),
                            int(round(fs_to)) // g, int(round(fs_from)) // g, axis=-1
                            ).astype(np.float32)


def load(rec, fs_out=1000, path=None, unit='mV'):
    """
    Tra (abd, fqrs, meta).
      abd  : float32 [24, N] don vi mV (mac dinh) hoac uV, da ha mau 2048 -> fs_out
      fqrs : LUON None -- NInFEA khong phan phoi nhan QRS thai
      meta : dict, co tol_ms_qrs / tol_ms_electromechanical va co canh bao chu the
    Luu y ha mau: 2048 -> 1000 Hz la ti le 125/256, resample_poly xu ly duoc nhung
    neu pipeline chi dung 10-60 Hz thi ha thang ve 500 Hz cung du va re hon.
    """
    h = read_header(rec, path)
    abd_names = abdominal_names(h['names'])
    if not abd_names:
        raise ValueError(f'{rec}: khong thay kenh {ABD_PREFIX}* trong {h["names"]}')
    phys, _ = read_signals(rec, path, channels=abd_names)      # uV
    if unit.lower() == 'mv':
        phys = phys / 1000.0
    abd = _resample(phys, h['fs'], fs_out)
    meta = dict(
        dataset='ninfea', record=str(rec),
        fs_orig=h['fs'], fs=float(fs_out), n_samp_orig=h['n_samp'], duration_s=h['duration_s'],
        names=abd_names, n_abd=len(abd_names), unit=unit,
        thoracic=thoracic_names(h['names']),
        ga_weeks=GA_WEEKS,
        has_fetal_annotations=False, fqrs_source='pulsed-wave Doppler V-peak, gan nhan bang mat',
        tol_ms_qrs=TOL_QRS_MS, tol_ms_electromechanical=TOL_ELECTROMECHANICAL_MS,
        subject_id=None, subject_id_available=False,
        subject_warning=(f'{N_RECORDS_TOTAL} muc ghi tu {N_SUBJECTS} san phu; anh xa muc ghi->san phu '
                         'KHONG co trong ban phat hanh. Coi cac muc ghi la phu thuoc.'),
        licence=LICENCE, cite=CITE, url=BASE_URL,
    )
    return abd, None, meta


def load_thoracic(rec, fs_out=1000, path=None, unit='mV'):
    """3 dao trinh nguc me bi_tho1..3 [3, N] -- dung lam tham chieu tru ECG me."""
    h = read_header(rec, path)
    names = thoracic_names(h['names'])
    if not names:
        raise ValueError(f'{rec}: khong co kenh {THO_PREFIX}*')
    phys, _ = read_signals(rec, path, channels=names)
    if unit.lower() == 'mv':
        phys = phys / 1000.0
    return _resample(phys, h['fs'], fs_out)


def load_sync(rec, path=None):
    """
    Kenh 'sync' o MAU THO (khong chia gain: gain=1, baseline=-2147483647 -> vat ly vo nghia).
    Dung de can chinh thoi gian giua ECG va anh PWD khi tu chu thich.
    """
    d = wfdb_dir(path)
    h = read_header(rec, path)
    if 'sync' not in h['names']:
        raise ValueError(f'{rec}: khong co kenh sync')
    i = h['names'].index('sync')
    dt = _FMT_DTYPE[h['fmts'][0]]
    n_sig = h['n_sig']
    p = os.path.join(d, h['dat'])
    n_full = os.path.getsize(p) // (np.dtype(dt).itemsize * n_sig)
    mm = np.memmap(p, dtype=dt, mode='r', shape=(n_full, n_sig))
    out = np.array(mm[:(h['n_samp'] or n_full), i])
    del mm
    return out


def pwd_image_path(rec, path=None):
    """Duong dan anh PWD dong bo cua ban ghi (None neu chua tai pwd_images/)."""
    d = os.path.join(ninfea_dir(path), PWD_SUBDIR)
    if not os.path.isdir(d):
        return None
    for ext in ('.bmp', '.png', '.jpg', '.tif'):
        p = os.path.join(d, f'{rec}{ext}')          # dat ten dung bang so ban ghi: 1.bmp, 10.bmp...
        if os.path.isfile(p):
            return p
    return None


def fetal_qrs(rec, path=None):
    """Luon bao loi -- ep code goi xu ly tuong minh thay vi coi la 'khong co dinh'."""
    raise NotImplementedError(
        'NInFEA khong phan phoi nhan QRS thai. Su that tham chieu la dinh V tren anh Doppler xung '
        '(pwd_images/*.bmp), do chuyen gia gan nhan bang mat trong bai Sci Data 8:30 -- moc CO HOC, '
        'khong phai moc dien hoc.\n'
        'De co nhan: (1) chuyen code/envelope_extraction.m sang Python de trich bao hinh PWD tu anh; '
        '(2) dung kenh "sync" can chinh thoi gian anh<->ECG (load_sync); (3) gan nhan dinh V co chuyen '
        'gia duyet; (4) danh gia voi tre dien-co <= 200 ms va cua so QRS 50 ms.\n'
        'TRUOC KHI DO, chi dung NInFEA cho danh gia KHONG NHAN. Xem survey/scout_datasets.md.')


def format_check(path=None, n_show=2):
    """Kiem tra nhanh tren cac ban ghi da tai (khong doc toan bo bo)."""
    d = wfdb_dir(path)
    recs = list_records(path)
    root = ninfea_dir(path)
    ann = [f for f in os.listdir(d)
           if os.path.splitext(f)[1].lower() in ('.qrs', '.fqrs', '.atr', '.ann')]
    print(f'thu muc wfdb      : {d}')
    print(f'ban ghi da tai    : {len(recs)}/{N_RECORDS_TOTAL}  {recs[:6]}')
    print(f'file nhan tim duoc: {ann if ann else "KHONG CO (dung nhu mong doi)"}')
    print(f'pwd_images/       : {"co" if os.path.isdir(os.path.join(root, PWD_SUBDIR)) else "chua tai"}')
    for r in recs[:n_show]:
        h = read_header(r, path)
        abd, fq, m = load(r, fs_out=1000, path=path)
        exp = (h['n_samp'] * h['n_sig'] * 4) if h['n_samp'] else None
        got = os.path.getsize(os.path.join(d, h['dat']))
        print(f'  {r}: {h["n_sig"]} kenh @ {h["fs"]:g} Hz, {h["duration_s"]:.2f} s | '
              f'.dat {got} byte, du tinh {exp} -> {"KHOP" if exp == got else "LECH"}')
        print(f'      abd{abd.shape} {m["unit"]} bien do p2p trung vi = '
              f'{np.median(np.ptp(abd, axis=1)):.4g}, fqrs={fq}')
        print(f'      bien: {h["names"][:3]} ... {h["names"][-4:]}')
    return dict(n_records_local=len(recs), annotation_files=ann)


if __name__ == '__main__':
    format_check()
