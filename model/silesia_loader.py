# -*- coding: utf-8 -*-
"""
Bo nap du lieu Silesia (Matonia A. va cs., "Fetal electrocardiograms, direct and abdominal with
reference heartbeat annotations", Scientific Data 7:200, 2020, DOI 10.1038/s41597-020-0538-z;
figshare collection DOI 10.6084/m9.figshare.c.4740794, file "Data Records.zip", 195,1 MB).

DINH DANG THAT (da doi chieu tren file giai nen, xem benchmark_dpss/silesia_eval.py muc 'format_check'):
  Data Records/B1_Pregnancy_dataset/B1_Pregnancy_XX/   XX = 01..10   THAI KY, 20 phut (598 900 mau @500 Hz)
      B1_abSignals_XX.ecg   nhi phan int16 BIG-ENDIAN, KHONG header, 8 cot xen ke theo mau, gia tri = int/10;
                            cot 0-3 = 4 dao trinh bung A1..A4, cot 4-7 = 4 tin hieu bien doi cua tac gia
                            (bien do nho, ~1/8 cot 0-3; KHONG dung de danh gia)
      B1_abSignals_XX.txt   ban van ban cua file tren: tab, dau phay thap phan, CRLF -- trung KHOP 100 %
      B1_Fetal_R_XX.txt     nhan QRS thai: 'chi_so_mau@500Hz <TAB> co' ; co = 1 hoac 0
      B1_Maternal_R_XX.txt  nhan QRS me: chi_so_mau@500Hz
  Data Records/B2_Labour_dataset/B2_Labour_XX/         XX = 01..12   CHUYEN DA, 5 phut (150 000 mau @500 Hz)
      B2_abSignals_XX.ecg   nhu tren (8 cot @500 Hz)
      B2_dFECG_XX.ecg       FECG TRUC TIEP tu dien cuc da dau, 300 000 mau @1000 Hz, 2 cot (tho, da loc)
      B2_Fetal_R_XX.txt     nhan QRS thai: chi_so_mau @1000 Hz (lay tren FECG truc tiep) -- KHONG co cot co
      B2_Maternal_R_XX.txt  nhan QRS me: chi_so_mau @500 Hz
  Online-only Table 1..4.pdf: chi so chat luong tung kenh va thong so FHR cua tung ban ghi.
  Khong co file readme trong zip.

  Kiem chung tan so: FHR trung vi tu nhan B1 @500 Hz = 127-157 bpm, B2 @1000 Hz = 126-157 bpm, khop voi
  "Basal FHR" trong Online-only Table 2/4 (vi du B1_01 155,4 vs 156,3; B2_01 127,7 vs 128,7).

NGUON NHAN:
  B2 (chuyen da): dien cuc da dau -> FECG truc tiep -> nhan tin cay (nhu ADFECGDB).
  B1 (thai ky): KHONG co dien cuc da dau. Nhan la NHAN GIAN TIEP: tac gia khu ECG me tren tin hieu bung,
  do QRS thai tren FECG gian tiep va chuyen gia duyet; cot 'co' = 1/0 (xem README_silesia.md).
  Vi vay F1 tren B1 do "dong y voi nhan gian tiep", khong phai voi su that sinh ly.

RO RI: 5 ban ghi ADFECGDB PhysioNet (r01,r04,r07,r08,r10) cung tu nhom Silesia -> silesia_eval.py kiem tra
  tuong quan cheo va loai/thay checkpoint (xem silesia_eval.json['leak_check']).

API:
  silesia_dir()                                 -> thu muc "Data Records"
  list_records()                                -> [('B1', 1), ..., ('B2', 12)]
  load(record_id)                               -> (abd[4, N] @1000 Hz, fetal_R @1000 Hz, meta)
                                                   record_id = 'B1_01' | ('B1', 1)
  load_record(group, idx, fs_out=1000, verified_only=False) -> nhu tren, tuy chon
  load_direct_fecg(idx)                         -> B2: [2, 300000] @1000 Hz
"""
from __future__ import annotations
import os, re
from math import gcd
import numpy as np
from scipy import signal as sg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FS_AB = 500                       # tin hieu bung (ca B1 va B2)
FS_DIRECT = 1000                  # FECG truc tiep (chi B2)
FS_FQRS = {'B1': 500, 'B2': 1000}  # nhan QRS thai: B1 tren tin hieu bung, B2 tren FECG truc tiep
FS_MQRS = 500                     # nhan QRS me (ca hai)
N_COLS_AB = 8
N_COLS_DIRECT = 2
N_B1, N_B2 = 10, 12
ECG_DTYPE = '>i2'                 # int16 big-endian
ECG_SCALE = 0.1                   # gia tri = int / 10  (khop 100 % voi file .txt)


def silesia_dir():
    for c in (os.environ.get('SILESIA_DIR'),
              os.path.join(ROOT, 'model', 'data', 'silesia', 'extracted', 'Data Records'),
              os.path.join(ROOT, 'model', 'data', 'silesia', 'Data Records'),
              os.path.join(ROOT, 'model', 'data', 'silesia')):
        if c and os.path.isfile(os.path.join(c, 'B1_Pregnancy_dataset', 'B1_Pregnancy_01', 'B1_abSignals_01.ecg')):
            return c
    raise SystemExit('Khong tim thay bo Silesia da giai nen. Chay model/download_silesia.py roi giai nen '
                     'Data_Records.zip (bo .tif) vao model/data/silesia/extracted/ (hoac dat SILESIA_DIR).')


def record_dir(group, idx):
    g = 'B1_Pregnancy_dataset' if group == 'B1' else 'B2_Labour_dataset'
    sub = ('B1_Pregnancy_%02d' if group == 'B1' else 'B2_Labour_%02d') % idx
    return os.path.join(silesia_dir(), g, sub)


def list_records():
    out = []
    for g, n in (('B1', N_B1), ('B2', N_B2)):
        for i in range(1, n + 1):
            if os.path.isfile(os.path.join(record_dir(g, i), f'{g}_abSignals_{i:02d}.ecg')):
                out.append((g, i))
    return out


def parse_record_id(record_id):
    if isinstance(record_id, (tuple, list)):
        return record_id[0], int(record_id[1])
    m = re.match(r'^(B[12])[_\- ]?(\d{1,2})$', str(record_id).strip())
    if not m:
        raise ValueError(f'record_id khong hop le: {record_id!r} (vi du "B1_01", "B2_12")')
    return m.group(1), int(m.group(2))


def read_ecg_binary(path, n_cols):
    """file .ecg = int16 big-endian, khong header, xen ke theo mau; gia tri thuc = int/10. -> [n_cols, n]"""
    raw = np.fromfile(path, dtype=ECG_DTYPE)
    assert raw.size % n_cols == 0, f'{path}: {raw.size} gia tri khong chia het cho {n_cols}'
    return raw.reshape(-1, n_cols).T.astype(np.float64) * ECG_SCALE


def read_ecg_text(path, n_cols, n_max=None):
    """ban .txt (tab, dau phay thap phan) -- chi de doi chieu dinh dang, cham."""
    rows = []
    with open(path, 'r', encoding='ascii', errors='replace') as f:
        for k, line in enumerate(f):
            if n_max is not None and k >= n_max:
                break
            t = line.strip().split('\t')
            if len(t) == n_cols:
                rows.append([float(v.replace(',', '.')) for v in t])
    return np.asarray(rows).T


def read_marks(path):
    """file *_R_XX.txt: moi dong 'chi_so_mau [co]'. Tra ve (samples int, flags int; flags=1 neu khong co cot)."""
    rows = []
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            t = [x for x in re.split(r'[\s,;]+', line.strip()) if x]
            if not t:
                continue
            try:
                rows.append([float(x) for x in t])
            except ValueError:
                continue
    if not rows:
        return np.zeros(0, int), np.zeros(0, int)
    w = max(len(r) for r in rows)
    a = np.asarray([r + [1.0] * (w - len(r)) for r in rows])
    s = a[:, 0].round().astype(int)
    fl = a[:, 1].round().astype(int) if a.shape[1] > 1 else np.ones(len(s), int)
    return s, fl


def _rescale_idx(samples, fs_from, fs_to):
    return np.round(np.asarray(samples, float) * (fs_to / fs_from)).astype(int)


def _resample(sig, fs_from, fs_to):
    up, down = int(fs_to), int(fs_from)
    g = gcd(up, down); up //= g; down //= g
    if up == 1 and down == 1:
        return sig
    return np.stack([sg.resample_poly(s, up, down) for s in sig])


def load_record(group, idx, fs_out=1000, verified_only=False):
    """Tra ve (sig[4, n] @fs_out, fqrs @fs_out, meta).

    sig: 4 dao trinh bung A1..A4 (cot 0-3 cua abSignals), resample_poly 500 -> fs_out.
    fqrs: nhan QRS thai doi ve fs_out (B1: x fs_out/500, B2: x fs_out/1000).
    verified_only=True: B1 chi giu nhip co co = 1. Mac dinh giu tat ca; co tung nhip nam trong meta['fqrs_flags'].
    """
    d = record_dir(group, idx); tag = f'{group}_{idx:02d}'
    ab = read_ecg_binary(os.path.join(d, f'{group}_abSignals_{idx:02d}.ecg'), N_COLS_AB)
    fq, flag = read_marks(os.path.join(d, f'{group}_Fetal_R_{idx:02d}.txt'))
    mq, _ = read_marks(os.path.join(d, f'{group}_Maternal_R_{idx:02d}.txt'))
    sig = _resample(ab[:4], FS_AB, fs_out)
    fq_out = _rescale_idx(fq, FS_FQRS[group], fs_out)
    mq_out = _rescale_idx(mq, FS_MQRS, fs_out)
    keep = (flag == 1) if verified_only else np.ones(len(fq), bool)
    dur = ab.shape[1] / FS_AB
    meta = dict(record=tag, group=group, idx=idx, stage='pregnancy' if group == 'B1' else 'labour',
                fs_native=FS_AB, fs_fqrs_native=FS_FQRS[group], fs_out=fs_out,
                n_samples_native=int(ab.shape[1]), duration_s=float(dur),
                n_fqrs=int(len(fq)), n_fqrs_flag0=int((flag == 0).sum()), n_mqrs=int(len(mq)),
                fhr_median_bpm=float(60.0 / np.median(np.diff(fq_out)) * fs_out) if len(fq) > 1 else float('nan'),
                fqrs_flags=flag, fqrs_all=fq_out, mqrs=mq_out,
                reference_source=('INDIRECT: abdominal signals, maternal ECG cancelled by the authors, fetal QRS '
                                  'detected and reviewed (flag column) -- no scalp electrode'
                                  if group == 'B1' else 'DIRECT fetal scalp electrode FECG @1000 Hz'))
    return sig, fq_out[keep], meta


def load(record_id, fs_out=1000, verified_only=False):
    """load('B1_03') -> (abd[4, N] @1000 Hz, fetal_R @1000 Hz, meta)"""
    g, i = parse_record_id(record_id)
    return load_record(g, i, fs_out=fs_out, verified_only=verified_only)


def load_direct_fecg(idx):
    """B2 only: FECG truc tiep @1000 Hz, [2, 300000] (cot 0 tho, cot 1 da loc boi tac gia)."""
    d = record_dir('B2', idx)
    return read_ecg_binary(os.path.join(d, f'B2_dFECG_{idx:02d}.ecg'), N_COLS_DIRECT)


def format_check(n_max=3000, full=('B1', 1)):
    """Doi chieu .ecg (BE int16/10) voi .txt: n_max mau dau cua moi file, va toan bo mot ban ghi."""
    out = {}
    for g, i in list_records():
        d = record_dir(g, i)
        names = [(f'{g}_abSignals_{i:02d}', N_COLS_AB)] + ([(f'B2_dFECG_{i:02d}', N_COLS_DIRECT)] if g == 'B2' else [])
        for nm, nc in names:
            nfull = None if (g, i) == tuple(full) else n_max
            be = read_ecg_binary(os.path.join(d, nm + '.ecg'), nc)
            tx = read_ecg_text(os.path.join(d, nm + '.txt'), nc, nfull)
            n = tx.shape[1]
            out[nm] = dict(n_compared=int(n), max_abs_diff=float(np.abs(be[:, :n] - tx).max()),
                           n_samples=int(be.shape[1]))
    return out


def sliding_ncc(template, signal_):
    """NCC chuan hoa cua template (dai L) truot tren signal_ (dai N >= L). Tra ve mang N-L+1 gia tri."""
    a = np.asarray(template, float); b = np.asarray(signal_, float)
    L = len(a); a = (a - a.mean()) / (a.std() + 1e-12)
    num = sg.fftconvolve(b, a[::-1], mode='valid')                       # sum a[k] * b[lag + k]
    csum = np.cumsum(np.concatenate([[0.0], b])); csum2 = np.cumsum(np.concatenate([[0.0], b * b]))
    s1 = csum[L:] - csum[:-L]; s2 = csum2[L:] - csum2[:-L]
    var = np.maximum(s2 / L - (s1 / L) ** 2, 1e-18)
    return num / (L * np.sqrt(var))


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print('thu muc:', silesia_dir())
    for g, i in list_records():
        sig, fq, meta = load_record(g, i)
        print(f'{meta["record"]}: {sig.shape} @{meta["fs_out"]} Hz, {meta["duration_s"]:.1f} s, '
              f'{meta["n_fqrs"]} fQRS (co=0: {meta["n_fqrs_flag0"]}), {meta["n_mqrs"]} mQRS, '
              f'FHR trung vi {meta["fhr_median_bpm"]:.1f} bpm')
