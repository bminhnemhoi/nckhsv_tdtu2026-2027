# -*- coding: utf-8 -*-
"""
Bo nap du lieu NIFEADB -- Non-Invasive Fetal ECG Arrhythmia Database.

  Behar JA, Bonnemains L, Shulgin V, Oster J, Ostras O, Lakhno I.
  "Noninvasive fetal electrocardiography for the detection of fetal arrhythmias."
  Prenatal Diagnosis 2019;39(3):178-187. DOI 10.1002/pd.5412
  PhysioNet: https://physionet.org/content/nifeadb/1.0.0/   DOI 10.13026/C2CT0S
  Giay phep: Open Data Commons Attribution License v1.0

CANH BAO LON NHAT -- BO NAY KHONG CO NHAN fQRS
  Da liet ke toan bo thu muc PhysioNet 1.0.0 (2026-09-11): chi co
      ARR_01..ARR_12 .dat/.hea, NR_01..NR_14 .dat/.hea, RECORDS, HEADER.shtml, SHA256SUMS.txt
  KHONG co bat ky file .qrs / .fqrs / .atr nao, va file ANNOTATORS cung khong ton tai.
  => KHONG the dung NIFEADB de bao cao F1/Se/PPV do QRS thai theo kieu co giam sat.
  Cac cach dung HOP LE:
    (1) danh gia KHONG NHAN: on dinh cua chi so tu choi (fSQI/AUROC theo do phu), do lech mien;
    (2) kiem tra dinh tinh tren loan nhip thai (12 ban ghi ARR_*) -- nguon bien thien RR
        nam ngoai moi bo huan luyen hien co;
    (3) tu chu thich (can chuyen gia) roi cong bo nhan nhu mot dong gop rieng.
  Neu cong bo, PHAI ghi ro nhan lay tu dau. Xem D:/NCKHSV2026-2027/survey/scout_datasets.md.

DINH DANG THAT (doi chieu tren .hea tai ve 2026-09-11)
  ARR_01  6 1000 600052
  ARR_01.dat 16 26599.2897(-14247)/mV 16 0 -15331 6038 0 ECG
  ARR_01.dat 16 61563.1752(-11451)/mV 16 0  12759 6551 0 Abdomen_1
  ... Abdomen_2 .. Abdomen_5
    - WFDB format 16 (int16 little-endian), 6 kenh xen ke theo mau, khong header trong .dat
    - kenh 0 = 'ECG'  -> ECG NGUC ME (1 dao trinh), KHONG phai kenh bung
    - kenh 1..5 = 'Abdomen_1..5' -> 4 hoac 5 dao trinh bung (mot so ban ghi chi co 4)
    - gain rat lon (1e4..1e5 don vi/mV) vi tin hieu da duoc chuan hoa; luon dung
      physical = (raw - baseline) / gain  [mV]
    - fs = 500 hoac 1000 Hz, doc TU HEADER tung ban ghi (khong duoc gia dinh)
    - do dai ~600 000 mau @1000 Hz ~ 10 phut/ban ghi
  Tong bo: 177,7 MB, 26 ban ghi.

SO CHU THE DOC LAP
  26 ban ghi = 12 loan nhip (ARR_01..12) + 14 nhip binh thuong (NR_01..14).
  Trang PhysioNet va HEADER.shtml KHONG khang dinh moi ban ghi la mot san phu khac nhau; bai
  Behar 2019 mo ta cohort theo thai nhi. Cho toi khi doi chieu duoc bang chan doan trong bai,
  loader nay TRA VE subject_id = ten ban ghi va danh dau subject_id_is_assumed=True.
  KHONG duoc dem 26 nhu 26 chu the doc lap trong bat ky phan tich cum/bootstrap nao ma khong
  dan chung tu bai bao.
  (Canh bao 'ecgca* deu tu 1 nguoi' trong download_more.py la NHAM BO: ecgca* thuoc nifecgdb --
   Non-Invasive Fetal ECG Database, 55 ban ghi tu MOT san phu -- khong lien quan toi NIFEADB.)

API
  nifeadb_dir()                       -> thu muc chua .dat/.hea
  list_records()                      -> ['ARR_01', ..., 'NR_14'] (chi nhung ban ghi co du .hea+.dat)
  read_header(rec)                    -> dict(fs, n_sig, n_samp, names, gains, baselines, fmt)
  load(rec, fs_out=1000)              -> (abd[C, N] mV, fqrs=None, meta)
  load_maternal(rec, fs_out=1000)     -> mecg[N] mV  (kenh 'ECG')
  groups()                            -> dict(ARR=[...], NR=[...])
"""
from __future__ import annotations
import os
import re
from math import gcd

import numpy as np
from scipy import signal as sg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DIR = os.path.join(ROOT, 'model', 'data', 'nifeadb')

BASE_URL = 'https://physionet.org/files/nifeadb/1.0.0/'
CITE = ('Behar JA, Bonnemains L, Shulgin V, Oster J, Ostras O, Lakhno I. Prenat Diagn. '
        '2019;39(3):178-187. DOI 10.1002/pd.5412')
LICENCE = 'Open Data Commons Attribution License v1.0'

#: Bo nay KHONG phan phoi nhan QRS thai. Hang so de code goi kiem tra tuong minh.
HAS_FETAL_ANNOTATIONS = False

RECORDS = [f'ARR_{i:02d}' for i in range(1, 13)] + [f'NR_{i:02d}' for i in range(1, 15)]

_FMT_BYTES = {8: 1, 16: 2, 61: 2, 32: 4, 80: 1, 160: 2}
_FMT_DTYPE = {16: '<i2', 61: '>i2', 32: '<i4', 160: '<u2', 80: 'u1'}


def nifeadb_dir(path=None):
    """Thu muc du lieu. Uu tien tham so, roi NIFEADB_DIR, roi model/data/nifeadb."""
    for cand in (path, os.environ.get('NIFEADB_DIR'), DEFAULT_DIR):
        if cand and os.path.isdir(cand):
            return cand
    raise FileNotFoundError(
        f'Khong thay thu muc NIFEADB. Da thu: {path!r}, $NIFEADB_DIR, {DEFAULT_DIR!r}.\n'
        f'Tai bang: python model/download_more.py --only nifeadb   (177,7 MB tu {BASE_URL})')


def list_records(path=None):
    """Cac ban ghi co DU ca .hea va .dat trong thu muc."""
    d = nifeadb_dir(path)
    out = []
    for r in RECORDS:
        if os.path.isfile(os.path.join(d, r + '.hea')) and os.path.isfile(os.path.join(d, r + '.dat')):
            out.append(r)
    return out


def groups(path=None):
    """{'ARR': [...], 'NR': [...]} -- ARR = loan nhip thai, NR = nhip binh thuong."""
    recs = list_records(path)
    return {'ARR': [r for r in recs if r.startswith('ARR')],
            'NR': [r for r in recs if r.startswith('NR')]}


def read_header(rec, path=None):
    """Doc .hea WFDB (chi cac truong can thiet). Tra dict."""
    d = nifeadb_dir(path)
    hea = os.path.join(d, rec + '.hea')
    with open(hea, 'r', encoding='utf-8', errors='replace') as f:
        lines = [ln.rstrip('\n') for ln in f]
    body = [ln for ln in lines if ln.strip() and not ln.lstrip().startswith('#')]
    head = body[0].split()
    n_sig = int(head[1])
    fs = float(head[2]) if len(head) > 2 else 250.0
    n_samp = int(head[3]) if len(head) > 3 else None

    names, gains, baselines, fmts, dat_files = [], [], [], [], []
    for ln in body[1:1 + n_sig]:
        tok = ln.split()
        dat_files.append(tok[0])
        fmts.append(int(re.match(r'(\d+)', tok[1]).group(1)))
        # gain(baseline)/units  -- baseline co the vang, khi do baseline = adc_zero
        m = re.match(r'([-\d.eE+]+)(?:\((-?\d+)\))?(?:/(\S+))?', tok[2]) if len(tok) > 2 else None
        g = float(m.group(1)) if m and m.group(1) else 200.0
        gains.append(g if g != 0 else 200.0)
        adc_zero = int(tok[4]) if len(tok) > 4 else 0
        baselines.append(int(m.group(2)) if (m and m.group(2) is not None) else adc_zero)
        names.append(tok[8] if len(tok) > 8 else f'ch{len(names)}')
    return dict(record=rec, fs=fs, n_sig=n_sig, n_samp=n_samp, names=names,
                gains=np.asarray(gains, float), baselines=np.asarray(baselines, float),
                fmts=fmts, dat=dat_files[0], header_path=hea)


def read_signals(rec, path=None):
    """Doc toan bo .dat -> mang vat ly [n_sig, n_samp] don vi mV, cung header."""
    d = nifeadb_dir(path)
    h = read_header(rec, path)
    fmt = h['fmts'][0]
    if any(f != fmt for f in h['fmts']):
        raise NotImplementedError(f'{rec}: cac kenh khac dinh dang -- khong ho tro.')
    if fmt not in _FMT_DTYPE:
        raise NotImplementedError(f'{rec}: WFDB format {fmt} chua ho tro (dung wfdb.rdrecord).')
    raw = np.fromfile(os.path.join(d, h['dat']), dtype=_FMT_DTYPE[fmt])
    n_sig = h['n_sig']
    n_full = raw.size // n_sig
    if h['n_samp'] and n_full < h['n_samp']:
        raise IOError(f'{rec}: .dat ngan hon header ({n_full} < {h["n_samp"]}) -- tai chua xong?')
    raw = raw[:n_full * n_sig].reshape(n_full, n_sig).T.astype(np.float64)
    if h['n_samp']:
        raw = raw[:, :h['n_samp']]
    phys = (raw - h['baselines'][:, None]) / h['gains'][:, None]
    return phys, h


def _resample(x, fs_from, fs_to):
    if fs_from == fs_to:
        return np.asarray(x, np.float32)
    g = gcd(int(round(fs_from)), int(round(fs_to)))
    return sg.resample_poly(np.asarray(x, np.float64),
                            int(round(fs_to)) // g, int(round(fs_from)) // g, axis=-1
                            ).astype(np.float32)


def abdominal_index(names):
    """Chi so cac kenh bung (ten 'Abdomen_*'); loai kenh 'ECG' = nguc me."""
    return [i for i, n in enumerate(names) if n.lower().startswith('abdomen')]


def maternal_index(names):
    """Chi so kenh ECG nguc me."""
    for i, n in enumerate(names):
        if n.strip().lower() == 'ecg':
            return i
    return None


def load(rec, fs_out=1000, path=None):
    """
    Tra (abd, fqrs, meta).
      abd  : float32 [C, N] mV, CHI cac kenh bung (4 hoac 5), da lay lai mau ve fs_out
      fqrs : LUON None -- bo nay khong co nhan QRS thai (xem HAS_FETAL_ANNOTATIONS)
      meta : dict co fs_orig, fs, names, group, subject_id, has_fetal_annotations, ...
    """
    phys, h = read_signals(rec, path)
    idx = abdominal_index(h['names'])
    if not idx:
        raise ValueError(f'{rec}: khong tim thay kenh bung trong {h["names"]}')
    abd = _resample(phys[idx], h['fs'], fs_out)
    meta = dict(
        dataset='nifeadb', record=rec, group=rec.split('_')[0],
        fs_orig=h['fs'], fs=float(fs_out), n_samp_orig=h['n_samp'],
        duration_s=(h['n_samp'] / h['fs']) if h['n_samp'] else None,
        names=[h['names'][i] for i in idx], n_abd=len(idx),
        maternal_channel=maternal_index(h['names']),
        has_fetal_annotations=False,
        fqrs_source=None,
        subject_id=rec, subject_id_is_assumed=True,
        licence=LICENCE, cite=CITE, url=BASE_URL,
    )
    return abd, None, meta


def load_maternal(rec, fs_out=1000, path=None):
    """Kenh ECG nguc me [N] mV (dung cho tru mau me / can chinh)."""
    phys, h = read_signals(rec, path)
    i = maternal_index(h['names'])
    if i is None:
        raise ValueError(f'{rec}: khong co kenh ECG nguc me.')
    return _resample(phys[i], h['fs'], fs_out)


def fetal_qrs(rec, path=None):
    """Luon bao loi -- de code goi khong am tham coi la 'khong co dinh'."""
    raise NotImplementedError(
        'NIFEADB khong phan phoi nhan QRS thai (kiem tra 2026-09-11: khong co .qrs/.fqrs/.atr, '
        'khong co file ANNOTATORS). Chi dung bo nay cho danh gia khong nhan hoac sau khi tu chu '
        'thich co chuyen gia duyet. Xem survey/scout_datasets.md.')


def format_check(path=None, n_show=3):
    """Kiem tra nhanh: dem ban ghi, in fs / so kenh / do dai, xac nhan khong co file nhan."""
    d = nifeadb_dir(path)
    recs = list_records(path)
    files = os.listdir(d)
    ann = [f for f in files if os.path.splitext(f)[1].lower() in ('.qrs', '.fqrs', '.atr', '.ann')]
    print(f'thu muc          : {d}')
    print(f'ban ghi day du   : {len(recs)}/26  {recs[:n_show]}{" ..." if len(recs) > n_show else ""}')
    print(f'file nhan tim duoc: {ann if ann else "KHONG CO (dung nhu mong doi)"}')
    fss = {}
    for r in recs:
        h = read_header(r, path)
        fss.setdefault((h['fs'], h['n_sig']), []).append(r)
    for (fs, ns), rr in sorted(fss.items()):
        print(f'  fs={fs:g} Hz, {ns} kenh : {len(rr)} ban ghi  ({rr[0]}..{rr[-1]})')
    for r in recs[:n_show]:
        abd, fq, m = load(r, fs_out=1000, path=path)
        print(f'  {r}: abd{abd.shape} {m["duration_s"]:.0f}s fs_orig={m["fs_orig"]:g} '
              f'kenh={m["names"]} fqrs={fq}')
    return dict(n_records=len(recs), annotation_files=ann, by_fs={str(k): v for k, v in fss.items()})


if __name__ == '__main__':
    format_check()
