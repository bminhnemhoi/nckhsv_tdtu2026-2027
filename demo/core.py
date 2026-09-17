# -*- coding: utf-8 -*-
"""
RelyFetal demo -- lõi xử lý (KHÔNG phụ thuộc gradio, kiểm thử được bằng pytest).

Bao bọc pipeline chuẩn của model/fqrs_model.py:
    preprocess -> cancel_maternal -> FetalQRSTCN -> pick_peaks
và bổ sung: đọc bản ghi (EDF / WFDB / CSV / NPY / mảng numpy), chọn kênh mù nhãn
theo PSD (Power-MF), chuỗi nhịp tim thai theo cửa sổ 4 s, đối chiếu với nhãn
(nếu có) và đèn tin cậy HAI CHẾ ĐỘ (`confidence_mode`):
    'hoc'  (mặc định) -- bộ phân loại GBM học được trên 12 chỉ số cổ điển của từng đoạn 4 s (fsqi/gate.py,
                         huấn luyện bởi fsqi/train_gate.py trên ADFECGDB, ngưỡng hiệu chuẩn ngoài fold)
    'luat'            -- quy tắc cứng 4 thành phần + ngưỡng đặt tay (phiên bản đầu của demo)
    'ca_hai'          -- tính cả hai (out['confidence_by_mode']), out['confidence'] = 'hoc'
Cổng "bám nhịp mẹ" ≥ 60 % là luật ghi đè -> 'thap' ở CẢ HAI chế độ.

Không sửa model/fqrs_model.py -- mọi thứ ở đây chỉ gọi nó.
"""
from __future__ import annotations
import os, sys, time, importlib.util, glob, shutil
from fractions import Fraction

import numpy as np
import torch
from scipy import signal as sg

torch.set_num_threads(int(os.environ.get('RELYFETAL_THREADS', '4')))   # máy 12 nhân, chạy song song với các agent khác

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
sys.path.insert(0, os.path.join(ROOT, 'fsqi'))          # gate.py + fsqi.py (đèn tin cậy học được)
from _paths import adfecgdb_dir as _adfecgdb_dir, cinc2013_dir as _cinc2013_dir, checkpoint as _ckpt  # noqa: E402

_spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(M); CFG = M.CFG

FS_IN = 1000            # mọi bản ghi được đưa về 1000 Hz trước khi phân tích
FS = CFG['fs']          # 250 Hz sau tiền xử lý
FHR_BAND = (1.8, 3.0)   # 108-180 bpm -- dải chọn kênh của Power-MF (Jaeger 2024)
ADFECGDB_RECS = ('r01', 'r04', 'r07', 'r08', 'r10')
CINC_RECS = tuple(f'a{i:02d}' for i in range(1, 76))
# 15 bản ghi CinC set-a là BẢN SAO NGUYÊN VĂN của ADFECGDB (analysis/DULIEU.md: NCC = 1,0000, lệch RR = 0,0 ms)
# -> KHÔNG phải ngoài miền; không được dùng làm ví dụ "zero-shot".
CINC_LEAK = {'a04': 'r01', 'a05': 'r01', 'a22': 'r01', 'a13': 'r04', 'a20': 'r04', 'a25': 'r04',
             'a19': 'r07', 'a23': 'r07', 'a24': 'r07', 'a08': 'r08', 'a15': 'r08', 'a17': 'r08',
             'a03': 'r10', 'a12': 'r10', 'a14': 'r10'}
CINC_BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')     # 7 bản chú thích sai đã khai báo trước
CINC_CLEAN = tuple(r for r in CINC_RECS if r not in CINC_LEAK)      # 60 bản sạch -- số chính của đề tài
SILESIA_RECS = tuple(f'B1_{i:02d}' for i in range(1, 11)) + ('B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12')
SILESIA_DUP = {'B2_01': 'r01', 'B2_02': 'r10', 'B2_07': 'r04', 'B2_10': 'r07', 'B2_11': 'r08'}   # trùng PhysioNet, loại
# 22 chủ thể huấn luyện (5 ADFECGDB + 10 Silesia B1 + 7 Silesia B2) -> checkpoint fold KHÔNG chứa chủ thể đó
SUBJECTS_22 = ADFECGDB_RECS + SILESIA_RECS
LEAD_RULES = ('peakprob', 'psd')
LEAD_RULE_DEFAULT = 'peakprob'
LEAD_RULE_LABEL = {'peakprob': 'auto (peakprob)', 'psd': 'auto (PSD)'}
SEG_S = 4.0             # đoạn 4 s dùng cho peakprob và cho đèn tin cậy học (cùng lưới)

# Bản ghi minh hoạ cho buổi demo (docs/HUONG_DAN_DEMO_v2.md; bản cũ docs/HUONG_DAN_DEMO_v1.md). Lý do chọn ở đó; con số kiểm bằng demo/run_check.py.
DEMO_SHOWCASE = ('r01', 'a09', 'B2_03', 'a02', 'a27')

# --------------------------------------------------------------------------- quy tắc đèn tin cậy
# Ngưỡng CỐ ĐỊNH TRƯỚC, không tinh chỉnh trên bản ghi đánh giá (xem README, mục "Đèn tin cậy").
CONF_RULE = dict(
    band_lo=0.20, band_hi=0.55,      # (i) tỉ lệ năng lượng 10-60 Hz trên phần dư băng rộng: 0.20 -> 0, 0.55 -> 1
    cv_good=0.05, cv_bad=0.30,       # (ii) CV khoảng RR: <=0.05 -> 1, >=0.30 -> 0
    p_conf=0.90,                     # (iii) đỉnh được coi là "chắc" khi xác suất > 0.9
    fhr_lo=100.0, fhr_hi=200.0,      # (iv) fHR trung bình phải nằm trong [100, 200] bpm
    min_beats=10,
    # (v) cổng "bám nhịp mẹ": tỉ lệ nhịp thai phát hiện nằm trong +/-50 ms của một đỉnh R mẹ.
    # Hai nhịp độc lập trùng nhau ngẫu nhiên ~ 2*50ms*mHR/60 = 13-22 % (mHR 80-130 bpm);
    # vượt 60 % nghĩa là mô hình đang theo phần dư QRS mẹ -> đèn ĐỎ bất kể điểm số.
    maternal_lock=0.60, maternal_tol_ms=50.0,
    weights=dict(band=0.20, rr=0.30, prob=0.30, fhr=0.20),
    level_cao=0.75, level_tb=0.45,   # score >= 0.75 -> cao; >= 0.45 -> trung bình; còn lại -> thấp
)
LEVEL_COLOR = {'cao': '#0ca30c', 'trung_binh': '#fab219', 'thap': '#d03b3b'}
LEVEL_LABEL = {'cao': 'CAO (xanh)', 'trung_binh': 'TRUNG BÌNH (vàng)', 'thap': 'THẤP (đỏ)'}
CONFIDENCE_MODES = ('hoc', 'luat', 'ca_hai')
CONFIDENCE_MODE_DEFAULT = 'hoc'
CONF_MODE_LABEL = {'hoc': 'học (GBM trên 12 chỉ số / đoạn 4 s, trong đó 2 là xác suất của mạng; fsqi/gate.py)',
                   'luat': 'luật cứng (4 thành phần, ngưỡng đặt tay)'}
# Cổng đang dùng là bản hiệu chuẩn trên MÔ HÌNH 5 CA (fsqi/gate_classical.pkl, train_gate.py trên ADFECGDB).
# Cổng 22 ca (analysis/GATE22.md, LOSO, AUROC trong bản ghi 0,934) hiện CHỈ là kết quả phân tích, chưa có tệp tải được.
GATE_NOTE = ('Cổng tin cậy: GBM hiệu chuẩn trên mô hình 5 ca ADFECGDB (fsqi/gate_classical.pkl). '
             'Khi ghép với mô hình 5 ca, AUROC trong bản ghi 0,721 [0,517; 0,898] trên 5 bản CinC sạch; '
             'ghép với mô hình 22 ca đang chạy: chưa đo lại. Cổng dùng cả xác suất của mạng nên không độc lập với mạng. '
             'Cổng 22 ca trong analysis/GATE22.md chưa được xuất thành tệp -> chưa dùng ở demo.')


# =========================================================================== dữ liệu mẫu
def adfecgdb_dir():
    try:
        return _adfecgdb_dir()
    except SystemExit:
        return None


def cinc2013_dir():
    return _cinc2013_dir()


_SILESIA = None


def silesia_loader():
    """model/silesia_loader.py (nạp lười); None nếu chưa có bộ Silesia trên đĩa."""
    global _SILESIA
    if _SILESIA is None:
        try:
            spec = importlib.util.spec_from_file_location('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))
            m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
            m.silesia_dir()
            _SILESIA = m
        except (SystemExit, Exception):        # noqa: BLE001
            _SILESIA = False
    return _SILESIA or None


def sample_records():
    """
    dict tên -> {path|None, kind, dataset, note, group}; chỉ liệt kê bản ghi thực sự có trên đĩa.
      ADFECGDB r01..r10 (5)     EDF, nhãn da đầu, checkpoint fold 22 ca không chứa chủ thể
      CinC 2013 set-a a01..a75  WFDB, 60 s; 15 bản RÒ RỈ (bản sao ADFECGDB) và 7 bản nhãn sai được gắn cờ
      Silesia B1/B2 (17)        qua model/silesia_loader.py; loại 5 bản trùng PhysioNet
    """
    out = {}
    d = adfecgdb_dir()
    if d:
        for r in ADFECGDB_RECS:
            p = os.path.join(d, r + '.edf')
            if os.path.isfile(p):
                out[r] = dict(path=p, kind='edf', dataset='ADFECGDB', group='ADFECGDB', note='nhãn da đầu, 300 s')
    c = cinc2013_dir()
    if c:
        for r in CINC_RECS:
            p = os.path.join(c, r + '.hea')
            if os.path.isfile(p):
                if r in CINC_LEAK:
                    note = f'RÒ RỈ: bản sao {CINC_LEAK[r]} của ADFECGDB — KHÔNG phải ngoài miền'
                elif r in CINC_BAD_ANN:
                    note = 'bản sạch nhưng nhãn tham chiếu SAI (đã khai báo trước)'
                else:
                    note = 'bản sạch, zero-shot'
                out[r] = dict(path=p, kind='wfdb', dataset='CinC 2013 set-a', group='CinC', note=note,
                              leak=r in CINC_LEAK, bad_annotation=r in CINC_BAD_ANN)
    SL = silesia_loader()
    if SL:
        for r in SILESIA_RECS:
            g, i = SL.parse_record_id(r)
            if os.path.isfile(os.path.join(SL.record_dir(g, i), f'{g}_abSignals_{i:02d}.ecg')):
                out[r] = dict(path=None, kind='silesia', group='Silesia ' + g,
                              dataset='Silesia ' + g + (' thai kỳ' if g == 'B1' else ' chuyển dạ'),
                              note='nhãn GIÁN TIẾP, 20 phút' if g == 'B1' else 'nhãn da đầu, 5 phút')
    return out


def load_silesia(rid):
    """Silesia B1_xx / B2_xx -> dict giống load_record (4 kênh bụng A1..A4 @1000 Hz, nhãn @1000 Hz)."""
    SL = silesia_loader()
    if SL is None:
        raise FileNotFoundError('Chưa có bộ Silesia trên đĩa (model/download_silesia.py)')
    abd, fq, meta = SL.load(rid)
    abd = np.asarray(abd, float)
    return dict(name=rid, signals=abd, lead_names=['A1', 'A2', 'A3', 'A4'], fs=FS_IN,
                fs_orig=float(meta['fs_native']), labels=np.asarray(fq, int), source='Silesia',
                duration_s=abd.shape[1] / FS_IN,
                extra=dict(stage=meta['stage'], reference_source=meta['reference_source'],
                           n_fqrs=int(meta['n_fqrs']), fhr_median_label_bpm=float(meta['fhr_median_bpm'])))


def load_sample(name, recs=None):
    """Đọc một bản ghi mẫu theo tên (r01 / a09 / B2_03) -> dict như load_record."""
    recs = recs or sample_records()
    if name not in recs:
        raise KeyError(f'Không có bản ghi mẫu {name!r} trên đĩa')
    info = recs[name]
    if info['kind'] == 'silesia':
        return load_silesia(name)
    rec = load_record(info['path'])
    rec['note'] = info.get('note', '')
    return rec


# =========================================================================== đọc bản ghi
def _to_1000hz(x, fs):
    x = np.asarray(x, float)
    if abs(fs - FS_IN) < 1e-9:
        return x
    fr = Fraction(FS_IN / float(fs)).limit_denominator(1000)
    return sg.resample_poly(x, fr.numerator, fr.denominator, axis=-1)


def _read_label_file(path, fs):
    """Nhãn dạng văn bản: mỗi dòng một chỉ số mẫu (ở fs đầu vào). Trả về mẫu ở 1000 Hz."""
    v = np.loadtxt(path, ndmin=1).ravel()
    return np.round(v * (FS_IN / float(fs))).astype(int)


def load_record(path_or_array, fs=1000, lead=None, labels=None, name=None):
    """
    Đọc một bản ghi ECG bụng về dạng thống nhất ở 1000 Hz.

    path_or_array : đường dẫn .edf / .hea / .dat / .csv / .npy / .txt, hoặc mảng numpy
    fs            : tần số lấy mẫu của CSV/NPY/mảng (EDF/WFDB tự đọc từ file)
    lead          : None = trả về mọi kênh bụng; số 1..K = chỉ trả về kênh đó
    labels        : (tuỳ chọn) đường dẫn file nhãn văn bản; với EDF/WFDB nhãn tự tìm cạnh file
    Trả về dict: name, signals (K x N, 1000 Hz), lead_names, fs (=1000), labels (mẫu 1000 Hz | None), source
    """
    lab = None
    if isinstance(path_or_array, (str, os.PathLike)):
        path = str(path_or_array); base, ext = os.path.splitext(path); ext = ext.lower()
        rec_name = name or os.path.basename(base)
        if ext == '.edf':
            import mne
            raw = mne.io.read_raw_edf(path, preload=True, verbose=False)
            sigs = raw.get_data(); fs0 = float(raw.info['sfreq']); names = list(raw.ch_names)
            keep = [i for i, n in enumerate(names) if 'direct' not in n.lower()] or list(range(len(names)))
            sigs = sigs[keep]; names = [names[i] for i in keep]
            src = 'EDF'
            qrs = base + '.edf.qrs'
            if os.path.isfile(qrs):
                import wfdb
                lab = np.asarray(wfdb.rdann(base, 'edf.qrs').sample)
                lab = np.round(lab * (FS_IN / fs0)).astype(int)
        elif ext in ('.hea', '.dat', '') and os.path.isfile(base + '.hea'):
            import wfdb
            r = wfdb.rdrecord(base)
            sigs = np.nan_to_num(r.p_signal).T; fs0 = float(r.fs)
            names = list(r.sig_name) if r.sig_name else [f'ch{i+1}' for i in range(sigs.shape[0])]
            src = 'WFDB'
            for ann in ('fqrs', 'edf.qrs', 'qrs'):
                if os.path.isfile(base + '.' + ann):
                    lab = np.asarray(wfdb.rdann(base, ann).sample)
                    lab = np.round(lab * (FS_IN / fs0)).astype(int); break
        elif ext == '.csv' or ext == '.txt':
            arr = np.genfromtxt(path, delimiter=',' if ext == '.csv' else None, dtype=float)
            if arr.ndim == 2 and np.isnan(arr[0]).all():      # dòng tiêu đề
                arr = arr[1:]
            arr = np.nan_to_num(np.atleast_2d(arr))
            if arr.shape[0] > arr.shape[1]:
                arr = arr.T
            sigs, fs0 = arr, float(fs); names = [f'ch{i+1}' for i in range(sigs.shape[0])]; src = 'CSV'
        elif ext == '.npy':
            arr = np.atleast_2d(np.asarray(np.load(path), float))
            if arr.shape[0] > arr.shape[1]:
                arr = arr.T
            sigs, fs0 = arr, float(fs); names = [f'ch{i+1}' for i in range(sigs.shape[0])]; src = 'NPY'
        else:
            raise ValueError(f'Không hỗ trợ định dạng: {path}')
        if labels and os.path.isfile(labels):
            lab = _read_label_file(labels, fs0)
    else:
        arr = np.atleast_2d(np.asarray(path_or_array, float))
        if arr.shape[0] > arr.shape[1]:
            arr = arr.T
        sigs, fs0 = arr, float(fs); names = [f'ch{i+1}' for i in range(sigs.shape[0])]
        src = 'array'; rec_name = name or 'array'
        if labels is not None:
            lab = np.round(np.asarray(labels, float) * (FS_IN / fs0)).astype(int)

    sigs = _to_1000hz(sigs, fs0)
    if lead is not None:
        k = int(lead) - 1
        if not 0 <= k < sigs.shape[0]:
            raise ValueError(f'Kênh {lead} không tồn tại (bản ghi có {sigs.shape[0]} kênh)')
        sigs, names = sigs[k:k + 1], names[k:k + 1]
    return dict(name=rec_name, signals=sigs, lead_names=names, fs=FS_IN, fs_orig=fs0,
                labels=lab, source=src, duration_s=sigs.shape[1] / FS_IN)


# =========================================================================== mô hình
_FOLD22 = None


def fold22_of(subject):
    """chủ thể trong 22 ca -> số fold (chuỗi '01'..'11') mà chủ thể đó là TEST (benchmark_dpss/eval_22.json)."""
    global _FOLD22
    if _FOLD22 is None:
        _FOLD22 = {}
        p = os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json')
        if os.path.isfile(p):
            import json
            with open(p, encoding='utf-8') as f:
                for fold, v in json.load(f)['folds'].items():
                    for s in v['test_subjects']:
                        _FOLD22[s] = fold
    return _FOLD22.get(subject)


def checkpoint_for(record_name):
    """
    Mô hình 22 chủ thể (5 ADFECGDB + 17 Silesia, grouped 11-fold):
      * chủ thể thuộc 22 ca -> fetalqrs_tcn_22_fold_XX.pt với XX là fold KHÔNG chứa chủ thể đó
      * mọi bản ghi khác (CinC 2013, file tải lên) -> fetalqrs_tcn_22_production.pt (zero-shot)
    Dự phòng: nếu thiếu checkpoint 22 ca thì rơi về mô hình 5 ca cũ (fold_rXX / production).
    """
    n = (record_name or '').strip()
    if n.lower() in ADFECGDB_RECS:
        n = n.lower()
    fold = fold22_of(n)
    if fold is not None:
        p = _ckpt(f'fetalqrs_tcn_22_fold_{fold}.pt')
        if os.path.isfile(p):
            return p, f'22 ca, fold {fold} (chủ thể {n} KHÔNG nằm trong tập huấn luyện)'
    p = _ckpt('fetalqrs_tcn_22_production.pt')
    if os.path.isfile(p):
        return p, '22 ca, production (zero-shot: bản ghi không thuộc 22 chủ thể huấn luyện)'
    if n in ADFECGDB_RECS and os.path.isfile(_ckpt(f'fetalqrs_tcn_fold_{n}.pt')):
        return _ckpt(f'fetalqrs_tcn_fold_{n}.pt'), f'5 ca, fold {n} (dự phòng: thiếu checkpoint 22 ca)'
    return _ckpt('fetalqrs_tcn_production.pt'), '5 ca, production (dự phòng: thiếu checkpoint 22 ca)'


_MODELS = {}


def load_model(path_or_name='production'):
    """Trả về (net, threshold, meta). Có bộ nhớ đệm."""
    p = path_or_name
    if not os.path.isfile(p):
        p = _ckpt(p if p.endswith('.pt') else f'fetalqrs_tcn_{p}.pt')
    p = os.path.abspath(p)
    if p not in _MODELS:
        blob = torch.load(p, map_location='cpu', weights_only=False)
        net = M.FetalQRSTCN(); net.load_state_dict(blob['state_dict']); net.eval()
        meta = {k: v for k, v in blob.items() if k != 'state_dict'}
        meta['path'] = p; meta['name'] = os.path.basename(p)
        _MODELS[p] = (net, float(blob['threshold']), meta)
    return _MODELS[p]


# =========================================================================== chọn kênh mù nhãn
def psd_score(x250, fs=FS):
    """Sao chép từ benchmark_dpss/blind_lead.py: đỉnh PSD trong dải nhịp thai của đường bao phần dư."""
    e = np.abs(sg.hilbert(x250 - np.mean(x250)))
    e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def pick_blind(residuals):
    """residuals: dict lead -> phần dư 250 Hz. Trả về lead có PSD thai mạnh nhất (không dùng nhãn)."""
    return max(residuals, key=lambda l: psd_score(residuals[l]))


def peakprob_score(prob, det250, fs=FS, seg_s=SEG_S):
    """
    Quy tắc peakprob (analysis/chonkenh_rules.py, rule_select 'peakprob'; đặc trưng peak_prob_mean của fsqi/gate.py):
    chia bản ghi thành các đoạn 4 s không chồng; trong mỗi đoạn lấy XÁC SUẤT TRUNG BÌNH của mô hình tại các
    đỉnh đã phát hiện (0 nếu đoạn không có đỉnh); điểm của kênh = TRUNG VỊ qua các đoạn. Không nhãn, không tham số học.
    Chọn kênh có điểm cao nhất. Cảnh báo bắt buộc: quy tắc này là lựa chọn HẬU KIỂM trên CinC (quy tắc khai báo trước là GATE).
    """
    prob = np.asarray(prob, float); det = np.asarray(det250, int)
    seg = int(round(seg_s * fs)); n_seg = len(prob) // seg
    if n_seg == 0:
        return float(np.mean(prob[det])) if len(det) else 0.0
    v = np.zeros(n_seg)
    for k in range(n_seg):
        a, b = k * seg, (k + 1) * seg
        d = det[(det >= a) & (det < b)]
        v[k] = float(np.mean(prob[d])) if len(d) else 0.0
    return float(np.median(v))


def front_end(sig_1000):
    """tiền xử lý + khử mẹ cho MỘT kênh -> (x250, residual, maternal_peaks_250)"""
    x = M.preprocess(np.asarray(sig_1000, float), FS_IN, CFG)
    r, mpk = M.cancel_maternal(x, CFG)
    return x, r, mpk


def infer(net, thr, front):
    """chạy FetalQRS-TCN trên một kênh đã tiền xử lý -> (prob, det250, ms)"""
    t0 = time.perf_counter()
    x250, res, _ = front
    prob = M.probability_series(net, M.robust_scale(res).astype(np.float32),
                                M.robust_scale(x250).astype(np.float32), CFG)
    det250 = M.pick_peaks(prob, thr, CFG).astype(np.int64)
    return prob, det250, (time.perf_counter() - t0) * 1000.0


def _norm_lead_mode(mode):
    """'auto' | 'peakprob' | 'psd' | 1..K -> ('peakprob'|'psd'|int)"""
    if isinstance(mode, str):
        s = mode.strip().lower()
        if s in ('auto', 'peakprob', 'auto (peakprob)'):
            return 'peakprob'
        if s in ('psd', 'auto (psd)'):
            return 'psd'
        return int(s)
    return int(mode)


def select_lead(signals_1000, mode='auto', model=None):
    """
    mode = 'peakprob' / 'auto' (mặc định): chạy mô hình trên CẢ K kênh, chọn kênh có peakprob_score cao nhất
           'psd'                          : quy tắc PSD của Power-MF (Jaeger 2024) trên đường bao phần dư
           1..K                           : chọn tay
    model: (net, thr) -- bắt buộc với 'peakprob'.
    Trả về (lead_1based, fronts, per_lead, fe_ms) với
       fronts[k]   = (x250, residual, mpk)
       per_lead[k] = dict(psd, peakprob, prob, det250, n_beats, fhr_mean, model_ms)  (prob/det chỉ có ở 'peakprob')
       hoặc per_lead = None khi chọn tay.
    """
    K = signals_1000.shape[0]
    rule = _norm_lead_mode(mode)

    def _timed(k):
        t0 = time.perf_counter(); fr = front_end(signals_1000[k - 1])
        return fr, (time.perf_counter() - t0) * 1000.0

    if rule in LEAD_RULES:
        fronts, fe_ms, per = {}, {}, {}
        for k in range(1, K + 1):
            fronts[k], fe_ms[k] = _timed(k)
            per[k] = dict(psd=psd_score(fronts[k][1]))
        if rule == 'peakprob':
            if model is None:
                raise ValueError("select_lead('peakprob') cần model=(net, thr)")
            net, thr = model
            for k in per:
                prob, det, ms = infer(net, thr, fronts[k])
                _, bpm = fhr_series(det, len(prob))
                per[k].update(peakprob=peakprob_score(prob, det), prob=prob, det250=det, n_beats=int(len(det)),
                              fhr_mean=float(np.nanmean(bpm)) if np.isfinite(bpm).any() else float('nan'), model_ms=ms)
        key = 'peakprob' if rule == 'peakprob' else 'psd'
        lead = max(per, key=lambda k: per[k][key])
        for k in per:
            per[k]['selected'] = (k == lead)
        return lead, fronts, per, fe_ms
    lead = rule
    if not 1 <= lead <= K:
        raise ValueError(f'Kênh {lead} không tồn tại (có {K} kênh)')
    fr, ms = _timed(lead)
    return lead, {lead: fr}, None, {lead: ms}


# =========================================================================== nhịp tim thai
def fhr_series(peaks_250, n_samples_250, fs=FS, win_s=4.0):
    """bpm theo từng cửa sổ 4 s không chồng lấn (median RR trong cửa sổ). NaN nếu < 2 nhịp."""
    t = np.asarray(peaks_250, float) / fs
    end = n_samples_250 / fs
    starts = np.arange(0.0, end, win_s)
    ts, bpm = [], []
    for w0 in starts:
        sel = t[(t >= w0) & (t < w0 + win_s)]
        v = np.nan
        if len(sel) >= 2:
            rr = np.diff(sel); rr = rr[(rr > 0.25) & (rr < 1.0)]      # 60-240 bpm
            if len(rr):
                v = 60.0 / float(np.median(rr))
        ts.append(w0 + win_s / 2); bpm.append(v)
    return np.asarray(ts), np.asarray(bpm)


# =========================================================================== đối chiếu nhãn
def match_with_lists(det, ref, fs, tolerance_ms=50):
    """Ghép một-đối-một tham lam giống hệt M.match_events, nhưng trả thêm các danh sách."""
    tol = tolerance_ms / 1000 * fs
    ref = np.asarray(ref, float); det = np.sort(np.asarray(det, float))
    used = np.zeros(len(ref), bool); matched, false, errs = [], [], []
    for d in det:
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (~used))[0]
        if len(ok):
            j = ok[int(np.argmin(dd[ok]))]; used[j] = True
            matched.append((int(d), int(ref[j]))); errs.append(dd[j] / fs * 1000)
        else:
            false.append(int(d))
    missed = [int(r) for r in ref[~used]]
    tp, fp, fn = len(matched), len(false), len(missed)
    se = tp / (tp + fn) * 100 if tp + fn else 0.0
    ppv = tp / (tp + fp) * 100 if tp + fp else 0.0
    return dict(TP=tp, FP=fp, FN=fn, Se=se, PPV=ppv,
                F1=2 * se * ppv / (se + ppv) if se + ppv else 0.0,
                jitter_ms=float(np.mean(errs)) if errs else float('nan'),
                matched=matched, missed=missed, false=false)


# =========================================================================== đèn tin cậy
def band_energy_ratio(sig_1000):
    """
    (i) Tỉ lệ năng lượng 10-60 Hz trên phần dư BĂNG RỘNG (0,5-120 Hz, 250 Hz).
    Phần dư chuẩn của pipeline đã lọc 10-60 Hz nên tỉ lệ đó tầm thường (~1); ở đây khử mẹ
    trên bản băng rộng rồi hỏi: năng lượng còn lại tập trung ở dải QRS thai hay tràn ra
    trôi nền (<10 Hz) / EMG (>60 Hz)?
    """
    x = np.asarray(sig_1000, float)
    b, a = sg.butter(2, [0.5 / 500, 120.0 / 500], btype='band')
    xw = sg.resample_poly(sg.filtfilt(b, a, x), 1, 4)
    rw, _ = M.cancel_maternal(xw, CFG)
    f, P = sg.welch(rw - rw.mean(), fs=FS, nperseg=min(len(rw), 2048))
    tot = float(np.trapezoid(P[(f >= 0.5)], f[(f >= 0.5)])) + 1e-12
    inb = float(np.trapezoid(P[(f >= 10) & (f <= 60)], f[(f >= 10) & (f <= 60)]))
    return inb / tot


def _lin(x, x0, x1):
    """0 tại x0, 1 tại x1, tuyến tính ở giữa (x0 < x1 hoặc ngược lại)."""
    if np.isnan(x):
        return 0.0
    return float(np.clip((x - x0) / (x1 - x0), 0.0, 1.0))


def maternal_coincidence(peaks_250, maternal_250, tol_ms=50.0, fs=FS):
    """(v) tỉ lệ nhịp thai phát hiện nằm trong +/-tol của một đỉnh R mẹ (không cần nhãn)."""
    a = np.asarray(peaks_250, float); b = np.sort(np.asarray(maternal_250, float))
    if len(a) == 0 or len(b) == 0:
        return float('nan')
    j = np.clip(np.searchsorted(b, a), 1, len(b) - 1)
    d = np.minimum(np.abs(a - b[j - 1]), np.abs(a - b[j]))
    return float(np.mean(d <= tol_ms / 1000 * fs))


def confidence(sig_1000, prob, peaks_250, fhr_mean, maternal_250=None, rule=CONF_RULE):
    """
    Quy tắc cứng tạm thời (sẽ thay bằng fSQI tô-pô). Bốn thành phần cho điểm số:
      (i)   tỉ lệ năng lượng 10-60 Hz trên phần dư băng rộng
      (ii)  CV của khoảng RR đầu ra (đều -> tin)
      (iii) tỉ lệ đỉnh phát hiện có xác suất > 0,9
      (iv)  fHR trung bình nằm trong 100-200 bpm
    và một cổng chặn (v): nếu > 60 % nhịp thai trùng nhịp mẹ -> 'thap' bất kể điểm số
    (phát hiện được nhờ a02 của CinC: mô hình bám phần dư QRS mẹ ở 125 bpm mà 4 thành phần trên vẫn cho 'cao').
    Trả về dict(level, score, reasons, components).
    """
    R = rule; W = R['weights']
    pk = np.asarray(peaks_250, int)
    n = len(pk)
    reasons, comp = [], {}

    ratio = band_energy_ratio(sig_1000)
    s_band = _lin(ratio, R['band_lo'], R['band_hi'])
    comp['band_ratio'] = ratio; comp['s_band'] = s_band
    reasons.append(f'Năng lượng 10–60 Hz trên phần dư: {ratio*100:.0f}% '
                   + ('(tập trung ở dải QRS thai)' if s_band >= 0.99 else '(tràn ra ngoài dải QRS: trôi nền/EMG)' if s_band <= 0.01 else '(trung gian)'))

    if n >= 5:
        rr = np.diff(pk) / FS
        cv = float(np.std(rr) / (np.mean(rr) + 1e-12))
    else:
        cv = float('nan')
    s_rr = _lin(cv, R['cv_bad'], R['cv_good'])
    comp['rr_cv'] = cv; comp['s_rr'] = s_rr
    reasons.append(f'Khoảng RR: CV = {cv:.2f} ' + ('(đều)' if s_rr >= 0.99 else '(rất bất thường)' if s_rr <= 0.01 else '(hơi bất thường)')
                   if not np.isnan(cv) else 'Quá ít nhịp để đánh giá RR')

    frac = float(np.mean(prob[pk] > R['p_conf'])) if n else 0.0
    s_prob = frac
    comp['frac_conf_peaks'] = frac; comp['s_prob'] = s_prob
    reasons.append(f'{frac*100:.0f}% đỉnh có xác suất > {R["p_conf"]:.1f}')

    in_range = (not np.isnan(fhr_mean)) and R['fhr_lo'] <= fhr_mean <= R['fhr_hi']
    s_fhr = 1.0 if in_range else 0.0
    comp['fhr_mean'] = float(fhr_mean); comp['s_fhr'] = s_fhr
    reasons.append(f'fHR trung bình {fhr_mean:.0f} bpm ' + ('nằm trong' if in_range else 'NGOÀI') + f' {R["fhr_lo"]:.0f}–{R["fhr_hi"]:.0f} bpm'
                   if not np.isnan(fhr_mean) else 'Không ước lượng được fHR')

    lock = maternal_coincidence(pk, maternal_250, R['maternal_tol_ms']) if maternal_250 is not None else float('nan')
    comp['maternal_lock'] = lock
    locked = (not np.isnan(lock)) and lock > R['maternal_lock']
    if not np.isnan(lock):
        reasons.append(f'{lock*100:.0f}% nhịp thai trùng đỉnh R mẹ (±{R["maternal_tol_ms"]:.0f} ms; ngẫu nhiên ≈ 13–22%)'
                       + (' → mô hình đang BÁM NHỊP MẸ' if locked else ''))

    score = W['band'] * s_band + W['rr'] * s_rr + W['prob'] * s_prob + W['fhr'] * s_fhr
    if n < R['min_beats']:
        level = 'thap'; reasons.append(f'Chỉ phát hiện {n} nhịp (< {R["min_beats"]})')
    elif locked:
        level = 'thap'
    elif score >= R['level_cao'] and in_range:
        level = 'cao'
    elif score >= R['level_tb']:
        level = 'trung_binh'
    else:
        level = 'thap'
    if score >= R['level_cao'] and not in_range and n >= R['min_beats'] and not locked:
        reasons.append('Hạ xuống trung bình vì fHR ngoài dải sinh lý')
    return dict(level=level, score=float(score), reasons=reasons, components=comp,
                color=LEVEL_COLOR[level], label=LEVEL_LABEL[level], mode='luat')


confidence_rule = confidence      # tên rõ nghĩa cho chế độ 'luat'


def confidence_learned(sig_1000, res_250, prob, peaks_250, maternal_250=None, x250=None):
    """
    Chế độ 'hoc' (mặc định): cổng tin cậy học được -- fsqi/gate.py, huấn luyện bởi fsqi/train_gate.py.
      * mỗi đoạn 4 s: 12 chỉ số cổ điển (SampEn, kurtosis, entropy phổ, tỉ số năng lượng 10–60 Hz, CV RR,
        tỉ lệ RR hợp lý, bSQI, số đỉnh, đỉnh PSD dải thai, τ ACF, xác suất trung bình tại đỉnh, xác suất cực đại)
        -> HistGradientBoosting (huấn luyện trên 1500 đoạn ADFECGDB, checkpoint fold) -> p_bad = P(F1 đoạn < 80)
      * ngưỡng đoạn q1/q2 hiệu chuẩn trên ADFECGDB ngoài fold (85 % đoạn xanh, 5 % đoạn đỏ);
        quy tắc bản ghi: > 30 % đoạn đỏ -> thấp; > 70 % đoạn xanh -> cao; còn lại trung bình; điểm = 1 − TB p_bad
      * cổng bám nhịp mẹ ≥ 60 % ghi đè -> thấp (giữ từ chế độ luật)
    Không dùng đặc trưng tô-pô (kết quả phủ định trong fsqi/results.json). Trả về dict như confidence() + 'segments'.
    """
    import gate as fgate
    t0 = time.perf_counter()
    pk = np.asarray(peaks_250, int)
    p_bad = fgate.score_segments(res_250, x250, prob, pk, raw1000=sig_1000, fs=FS, raw_fs=FS_IN)
    lock = maternal_coincidence(pk, maternal_250, CONF_RULE['maternal_tol_ms']) if maternal_250 is not None else float('nan')
    c = fgate.record_confidence(p_bad, lock)
    c['components']['gate_ms'] = (time.perf_counter() - t0) * 1000.0
    g = fgate.load_gate()
    c.update(color=LEVEL_COLOR[c['level']], label=LEVEL_LABEL[c['level']], mode='hoc',
             segments=dict(p_bad=[float(v) for v in p_bad], level=[str(v) for v in fgate.segment_levels(p_bad)],
                           seg_s=float(g['seg_s']), q1=float(g['q1']), q2=float(g['q2'])))
    return c


# =========================================================================== phân tích
def analyze(signal_1000hz, labels_1000=None, model='22_production', fs=1000, front=None,
            confidence_mode=CONFIDENCE_MODE_DEFAULT, inference=None):
    """
    Phân tích MỘT kênh ECG bụng. signal_1000hz: mảng 1-D (nếu fs != 1000 sẽ được tái lấy mẫu).
    model: '22_production' (mặc định) | đường dẫn .pt | tên checkpoint.  front: (x250, res, mpk) đã tính sẵn (tuỳ chọn).
    inference: (prob, det250) đã tính sẵn cho kênh này (tuỳ chọn -- select_lead('peakprob') đã chạy mô hình rồi).
    confidence_mode: 'hoc' (mặc định) | 'luat' | 'ca_hai' (tính cả hai, out['confidence'] = 'hoc').
    """
    if confidence_mode not in CONFIDENCE_MODES:
        raise ValueError(f'confidence_mode phải là một trong {CONFIDENCE_MODES}, nhận {confidence_mode!r}')
    sig = np.asarray(signal_1000hz, float).ravel()
    if fs != FS_IN:
        sig = _to_1000hz(sig, fs)
    net, thr, meta = load_model(model)

    t0 = time.perf_counter()
    x250, res, mpk = front if front is not None else front_end(sig)
    if inference is not None:
        prob, det250 = inference; det250 = np.asarray(det250, np.int64)
    else:
        prob, det250, _ = infer(net, thr, (x250, res, mpk))
    latency_ms = (time.perf_counter() - t0) * 1000.0
    det1000 = det250 * int(FS_IN // FS)

    fhr_t, fhr_bpm = fhr_series(det250, len(res))
    fhr_mean = float(np.nanmean(fhr_bpm)) if np.isfinite(fhr_bpm).any() else float('nan')
    by_mode = {}
    if confidence_mode in ('luat', 'ca_hai'):
        by_mode['luat'] = confidence(sig, prob, det250, fhr_mean, maternal_250=mpk)
    if confidence_mode in ('hoc', 'ca_hai'):
        by_mode['hoc'] = confidence_learned(sig, res, prob, det250, maternal_250=mpk, x250=x250)
    main_mode = 'hoc' if 'hoc' in by_mode else 'luat'
    conf = by_mode[main_mode]

    out = dict(
        raw=sig, fs_raw=FS_IN, filtered_250=x250, residual_250=res, fs=FS,
        maternal_peaks=mpk, prob=prob, threshold=thr,
        fetal_peaks_250=det250, fetal_peaks_1000=det1000,
        fhr_time_s=fhr_t, fhr_series=fhr_bpm, fhr_mean=fhr_mean,
        n_beats=int(len(det250)), latency_ms=float(latency_ms),
        duration_s=len(sig) / FS_IN, confidence=conf,
        confidence_mode=main_mode, confidence_by_mode=by_mode,
        checkpoint=meta['name'], checkpoint_path=meta['path'],
    )
    if labels_1000 is not None:
        lab = np.asarray(labels_1000, int)
        m = match_with_lists(det1000, lab, FS_IN, CFG['tolerance_ms'])
        out['labels_1000'] = lab
        out['metrics'] = {k: m[k] for k in ('TP', 'FP', 'FN', 'Se', 'PPV', 'F1', 'jitter_ms')}
        out['matched'] = m['matched']; out['missed'] = m['missed']; out['false'] = m['false']
    return out


def analyze_record(rec, lead='auto', model=None, confidence_mode=CONFIDENCE_MODE_DEFAULT):
    """
    rec: dict từ load_record()/load_sample(). lead: 'auto' (= 'peakprob') | 'psd' | 1..K.
    model: None -> checkpoint_for(rec['name']).  confidence_mode: 'hoc' | 'luat' | 'ca_hai' (xem analyze).
    Trả về dict của analyze() + lead, lead_name, lead_rule, lead_mode, lead_scores, leads (kết quả từng kênh), checkpoint_note.
      leads[k] = dict(psd, peakprob, n_beats, fhr_mean, residual_250, prob, det250, F1/Se/PPV nếu có nhãn, selected)
                 -- có ở chế độ tự động; None khi chọn tay.
    """
    if model is None:
        model, note = checkpoint_for(rec['name'])
    else:
        note = str(model)
    net, thr, _meta = load_model(model)
    rule = _norm_lead_mode(lead)
    lead, fronts, per, fe_ms = select_lead(rec['signals'], rule, model=(net, thr))
    inf = (per[lead]['prob'], per[lead]['det250']) if per is not None and 'prob' in per[lead] else None
    out = analyze(rec['signals'][lead - 1], rec.get('labels'), model=model, front=fronts[lead],
                  confidence_mode=confidence_mode, inference=inf)
    # latency_ms = tiền xử lý + khử mẹ của kênh được chọn + mô hình + chọn đỉnh (KHÔNG tính đọc file)
    model_ms = per[lead]['model_ms'] if inf is not None else out['latency_ms']
    out['latency_model_ms'] = float(model_ms)
    out['latency_frontend_ms'] = float(fe_ms[lead])
    out['latency_ms'] = out['latency_model_ms'] + out['latency_frontend_ms']
    # chi phí THẬT của quy tắc tự động: tiền xử lý mọi kênh (+ mô hình trên mọi kênh với peakprob)
    all_model = sum(p.get('model_ms', 0.0) for p in per.values()) if per else out['latency_model_ms']
    if per and rule == 'psd':
        all_model = out['latency_model_ms']
    out['latency_all_leads_ms'] = float(all_model + sum(fe_ms.values()))

    leads = None; lead_scores = None
    if per is not None:
        leads, lead_scores = {}, {}
        lab = rec.get('labels')
        for k, p in per.items():
            d = dict(psd=p['psd'], peakprob=p.get('peakprob'), selected=bool(p['selected']),
                     residual_250=fronts[k][1], name=rec['lead_names'][k - 1])
            if 'prob' in p:
                d.update(prob=p['prob'], det250=p['det250'], n_beats=p['n_beats'], fhr_mean=p['fhr_mean'],
                         model_ms=p['model_ms'])
                if lab is not None:
                    m = match_with_lists(p['det250'] * int(FS_IN // FS), np.asarray(lab, int), FS_IN, CFG['tolerance_ms'])
                    d.update(F1=m['F1'], Se=m['Se'], PPV=m['PPV'], jitter_ms=m['jitter_ms'])
            leads[k] = d
            lead_scores[k] = p['peakprob'] if rule == 'peakprob' else p['psd']
    out.update(lead=lead, lead_name=rec['lead_names'][lead - 1], lead_rule=rule if per is not None else 'manual',
               lead_scores=lead_scores, leads=leads,
               lead_mode=LEAD_RULE_LABEL[rule] if per is not None else 'thủ công',
               n_leads=int(rec['signals'].shape[0]),
               checkpoint_note=note, record=rec['name'], source=rec['source'], record_note=rec.get('note', ''))
    return out


def _jf(v):
    """float JSON-an toàn: NaN/inf -> None."""
    v = float(v)
    return v if np.isfinite(v) else None


def _jv(v):
    """giá trị JSON-an toàn: None/bool/int giữ nguyên, số thực -> _jf."""
    if v is None:
        return None
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if isinstance(v, (int, np.integer)):
        return int(v)
    return _jf(v)


def _conf_summary(c, with_reasons=True):
    d = dict(mode=c.get('mode'), level=c['level'], score=_jf(c['score']),
             components={k: _jv(v) for k, v in c['components'].items()})
    if with_reasons:
        d['reasons'] = c['reasons']
    if c.get('segments'):
        sg_ = c['segments']
        d['segments'] = dict(n=len(sg_['p_bad']), seg_s=sg_['seg_s'], q1=_jf(sg_['q1']), q2=_jf(sg_['q2']),
                             p_bad=[round(float(v), 4) for v in sg_['p_bad']],
                             level=''.join({'xanh': 'X', 'vang': 'V', 'do': 'D'}[l] for l in sg_['level']))
    return d


def summary(out):
    """dict JSON-hoá được (không có mảng lớn) -- để ghi log / kiểm thử."""
    c = out['confidence']
    s = dict(record=out.get('record'), lead=out.get('lead'), lead_mode=out.get('lead_mode'),
             lead_rule=out.get('lead_rule'),
             checkpoint=out['checkpoint'], checkpoint_note=out.get('checkpoint_note'), threshold=_jf(out['threshold']),
             duration_s=_jf(out['duration_s']), n_beats=int(out['n_beats']), fhr_mean=_jf(out['fhr_mean']),
             latency_ms=_jf(out['latency_ms']),
             latency_frontend_ms=_jf(out.get('latency_frontend_ms', float('nan'))),
             latency_model_ms=_jf(out.get('latency_model_ms', out['latency_ms'])),
             latency_all_leads_ms=_jf(out.get('latency_all_leads_ms', float('nan'))),
             confidence_mode=out.get('confidence_mode', c.get('mode', 'luat')),
             confidence=_conf_summary(c),
             confidence_by_mode={m: _conf_summary(cc) for m, cc in out.get('confidence_by_mode', {}).items()},
             gate_note=GATE_NOTE)
    if out.get('lead_scores'):
        # khóa phải là str: gr.JSON (orjson) của Gradio 6 từ chối khóa int ("Dict key must be str")
        s['lead_scores'] = {str(int(k)): _jf(v) for k, v in out['lead_scores'].items()}
    if out.get('leads'):
        s['leads'] = {str(int(k)): {kk: _jv(v) for kk, v in d.items()
                                    if kk in ('psd', 'peakprob', 'selected', 'n_beats', 'fhr_mean', 'F1', 'Se', 'PPV', 'jitter_ms', 'model_ms')}
                      for k, d in out['leads'].items()}
    if 'metrics' in out:
        s['metrics'] = {k: _jf(v) for k, v in out['metrics'].items()}
    return s


# =========================================================================== tiện ích tải lên
def gather_upload(paths, workdir):
    """
    Gom các file tải lên (gradio đặt mỗi file một thư mục riêng) vào workdir với tên gốc,
    rồi trả về đường dẫn file chính (.edf / .hea / .csv / .npy / .txt) để đưa vào load_record.
    """
    os.makedirs(workdir, exist_ok=True)
    for f in glob.glob(os.path.join(workdir, '*')):
        os.remove(f)
    local = []
    for p in paths or []:
        q = os.path.join(workdir, os.path.basename(p)); shutil.copyfile(p, q); local.append(q)
    for ext in ('.edf', '.hea', '.csv', '.npy', '.txt'):
        for q in local:
            if q.lower().endswith(ext) and not q.lower().endswith('.edf.qrs'):
                return q
    for q in local:
        if q.lower().endswith('.dat') and os.path.isfile(os.path.splitext(q)[0] + '.hea'):
            return q
    raise ValueError('Không tìm thấy file bản ghi hợp lệ (.edf, .hea+.dat, .csv, .npy, .txt)')


# =========================================================================== A1: mô tả bộ dữ liệu của nhóm
# Mọi số liệu ở phần này đọc THẬT từ tệp trên đĩa (header WFDB, header EDF, kích thước tệp .ecg,
# tệp nhãn văn bản). Không ghi cứng con số nào ngoài các hằng số định dạng do chính tác giả bộ dữ liệu công bố.

DATASET_KEYS = ('adfecgdb', 'silesia_b2', 'silesia_b1', 'cinc_sach', 'cinc_nhiem')
DATASET_LABEL = {
    'adfecgdb': 'ADFECGDB — 5 bản (PhysioNet, nhãn da đầu)',
    'silesia_b2': 'Silesia B2 — chuyển dạ (12 bản trên đĩa, nhãn da đầu)',
    'silesia_b1': 'Silesia B1 — thai kỳ (10 bản, nhãn gián tiếp)',
    'cinc_sach': 'CinC 2013 set-a — 60 bản SẠCH (ngoài miền)',
    'cinc_nhiem': 'CinC 2013 set-a — 15 bản NHIỄM (bản sao ADFECGDB)',
}
DATASET_DIR_HINT = {
    'adfecgdb': ('model/data/adfecgdb',
                 'python model/download_data.py --root model/data --only adfecgdb'),
    'silesia_b2': ('model/data/silesia/extracted/Data Records/B2_Labour_dataset',
                   'python model/download_silesia.py  (rồi giải nén Data_Records.zip vào model/data/silesia/extracted/)'),
    'silesia_b1': ('model/data/silesia/extracted/Data Records/B1_Pregnancy_dataset',
                   'python model/download_silesia.py  (rồi giải nén Data_Records.zip vào model/data/silesia/extracted/)'),
    # download_data.py --only cinc2013 ghi vào model/data/cinc2013 -- demo KHÔNG đọc thư mục đó (xem benchmark_dpss/_paths.py)
    'cinc_sach': ('benchmark_dpss/pcdb',
                  'python model/download_more.py --only cinc75'),
    'cinc_nhiem': ('benchmark_dpss/pcdb',
                   'python model/download_more.py --only cinc75'),
}
DATASET_CACHE = {}


def _rows_adfecgdb():
    d = adfecgdb_dir()
    if not d:
        return None, 'Chưa có bộ ADFECGDB trên đĩa.'
    import wfdb
    import mne
    rows = []
    for r in ADFECGDB_RECS:
        p = os.path.join(d, r + '.edf')
        if not os.path.isfile(p):
            continue
        raw = mne.io.read_raw_edf(p, preload=False, verbose='ERROR')
        fs0 = float(raw.info['sfreq']); n = int(raw.n_times); names = list(raw.ch_names)
        abd = [nm for nm in names if 'direct' not in nm.lower()]
        n_lab = None
        if os.path.isfile(p + '.qrs'):
            try:
                n_lab = int(len(wfdb.rdann(os.path.join(d, r), 'edf.qrs').sample))
            except Exception:                                   # noqa: BLE001
                n_lab = None
        dup = [k for k, v in SILESIA_DUP.items() if v == r]
        cinc = sorted(k for k, v in CINC_LEAK.items() if v == r)
        note = (f'trùng Silesia {dup[0]}' if dup else '')
        if cinc:
            note += ('; ' if note else '') + 'xuất hiện lại trong CinC set-a: ' + ', '.join(cinc)
        rows.append(dict(ten=r, duong_dan=p, dinh_dang='EDF (+ .edf.qrs)', fs_Hz=fs0,
                         do_dai_s=n / fs0, so_kenh_bung=len(abd), so_nhip_nhan=n_lab,
                         nguon_nhan='TRỰC TIẾP — điện cực da đầu thai',
                         ghi_chu=note, kenh=', '.join(names)))
    if not rows:
        return None, 'Thư mục ADFECGDB có nhưng không tìm thấy tệp .edf nào.'
    return rows, None


def _rows_cinc(nhiem):
    c = cinc2013_dir()
    if not c or not os.path.isdir(c):
        return None, 'Chưa có bộ CinC 2013 set-a trên đĩa.'
    import wfdb
    names = sorted(CINC_LEAK) if nhiem else list(CINC_CLEAN)
    rows = []
    for r in names:
        base = os.path.join(c, r)
        if not os.path.isfile(base + '.hea'):
            continue
        h = wfdb.rdheader(base)
        n_lab = None
        if os.path.isfile(base + '.fqrs'):
            try:
                n_lab = int(len(wfdb.rdann(base, 'fqrs').sample))
            except Exception:                                   # noqa: BLE001
                n_lab = None
        if nhiem:
            note = f'NHIỄM — bản sao {CINC_LEAK[r]} (ADFECGDB); NCC = 1,0000; lệch RR = 0,0 ms'
        elif r in CINC_BAD_ANN:
            note = 'bản sạch nhưng NHÃN THAM CHIẾU SAI (1 trong 7 bản đã khai báo trước)'
        else:
            note = 'bản sạch, zero-shot'
        rows.append(dict(ten=r, duong_dan=base + '.dat', dinh_dang='WFDB (.dat + .hea + .fqrs)',
                         fs_Hz=float(h.fs), do_dai_s=float(h.sig_len) / float(h.fs),
                         so_kenh_bung=int(h.n_sig), so_nhip_nhan=n_lab,
                         nguon_nhan='người chấm độc lập (ban tổ chức CinC 2013)',
                         ghi_chu=note, kenh=', '.join(h.sig_name or [])))
    if not rows:
        return None, 'Thư mục CinC có nhưng không tìm thấy tệp .hea nào.'
    return rows, None


def _rows_silesia(group):
    SL = silesia_loader()
    if SL is None:
        return None, 'Chưa có bộ Silesia đã giải nén trên đĩa.'
    rows = []
    n_max = SL.N_B1 if group == 'B1' else SL.N_B2
    for i in range(1, n_max + 1):
        d = SL.record_dir(group, i)
        sig_p = os.path.join(d, f'{group}_abSignals_{i:02d}.ecg')
        if not os.path.isfile(sig_p):
            continue
        tag = f'{group}_{i:02d}'
        n_native = os.path.getsize(sig_p) // (2 * SL.N_COLS_AB)     # int16 big-endian, 8 cột
        n_lab = None
        fq_p = os.path.join(d, f'{group}_Fetal_R_{i:02d}.txt')
        if os.path.isfile(fq_p):
            try:
                n_lab = int(len(SL.read_marks(fq_p)[0]))
            except Exception:                                   # noqa: BLE001
                n_lab = None
        if tag in SILESIA_DUP:
            note = f'TRÙNG PhysioNet {SILESIA_DUP[tag]} — đã LOẠI khỏi 22 chủ thể'
        else:
            note = 'trong 22 chủ thể huấn luyện/đánh giá (grouped 11-fold)'
        rows.append(dict(ten=tag, duong_dan=sig_p,
                         dinh_dang='nhị phân .ecg (int16 big-endian, 8 cột) + .txt nhãn',
                         fs_Hz=float(SL.FS_AB), do_dai_s=n_native / float(SL.FS_AB),
                         so_kenh_bung=4, so_nhip_nhan=n_lab,
                         nguon_nhan=('TRỰC TIẾP — điện cực da đầu thai' if group == 'B2'
                                     else 'GIÁN TIẾP — tác giả khử QRS mẹ trên chính tín hiệu bụng rồi soát tay'),
                         ghi_chu=note, kenh='A1, A2, A3, A4 (4 cột đầu trong 8 cột)'))
    if not rows:
        return None, f'Không tìm thấy bản ghi Silesia {group} nào.'
    return rows, None


def dataset_rows(key):
    """Metadata THẬT của từng bản ghi trong một bộ. Trả về (rows | None, thông_báo_lỗi | None). Có nhớ đệm."""
    if key not in DATASET_KEYS:
        raise ValueError(f'Bộ dữ liệu không hợp lệ: {key!r} (phải thuộc {DATASET_KEYS})')
    if key in DATASET_CACHE:
        return DATASET_CACHE[key]
    try:
        if key == 'adfecgdb':
            res = _rows_adfecgdb()
        elif key == 'cinc_sach':
            res = _rows_cinc(False)
        elif key == 'cinc_nhiem':
            res = _rows_cinc(True)
        elif key == 'silesia_b1':
            res = _rows_silesia('B1')
        else:
            res = _rows_silesia('B2')
    except Exception as e:                                      # noqa: BLE001
        res = (None, f'Không đọc được bộ {key}: {type(e).__name__}: {e}')
    DATASET_CACHE[key] = res
    return res


def header_example(key, n_lines=8):
    """Trả về (đường_dẫn, nội_dung) vài dòng ĐẦU của một tệp văn bản THẬT trên đĩa. (None, None) nếu không có."""
    rows, _err = dataset_rows(key)
    if not rows:
        return None, None
    r = rows[0]
    if key.startswith('cinc'):
        p = os.path.splitext(r['duong_dan'])[0] + '.hea'
    elif key.startswith('silesia'):
        g = 'B1' if key.endswith('b1') else 'B2'
        i = int(r['ten'].split('_')[1])
        p = os.path.join(os.path.dirname(r['duong_dan']), f'{g}_Fetal_R_{i:02d}.txt')
    else:
        return None, None                                       # EDF là nhị phân — không in nguyên văn được
    if not os.path.isfile(p):
        return p, None
    try:
        with open(p, encoding='utf-8', errors='replace') as f:
            lines = []
            for _ in range(n_lines):
                ln = f.readline()
                if not ln:
                    break
                lines.append(ln)
        return p, ''.join(lines).rstrip('\n')
    except OSError as e:
        return p, f'(không đọc được: {type(e).__name__}: {e})'


def preview_window(rec, t0_s=0.0, dur_s=10.0):
    """Cửa sổ tín hiệu THÔ (đã đưa về 1000 Hz) để vẽ: dict(t, signals[K,n], labels_s, names, ...)."""
    fs = rec['fs']; sig = np.atleast_2d(rec['signals'])
    i0 = max(0, int(round(t0_s * fs))); i1 = min(sig.shape[1], i0 + int(round(dur_s * fs)))
    seg = sig[:, i0:i1]
    t = np.arange(i0, i1) / float(fs)
    lab = rec.get('labels')
    lab_s = None
    if lab is not None and len(lab):
        lab = np.asarray(lab, int)
        lab_s = lab[(lab >= i0) & (lab < i1)] / float(fs)
    return dict(t=t, signals=seg, labels_s=lab_s, names=list(rec['lead_names']),
                fs=float(fs), name=rec['name'], n_leads=int(seg.shape[0]),
                duration_s=float(rec['duration_s']),
                n_beats_window=int(0 if lab_s is None else len(lab_s)))


# =========================================================================== A2: tải dữ liệu mới
class LoiDuLieu(ValueError):
    """Lỗi dữ liệu của người dùng — thông báo đã ở dạng tiếng Việt, hiện thẳng lên giao diện."""


MIN_DURATION_S = 8.0            # ngắn hơn thì không đủ cho cửa sổ 4 s + trường tiếp nhận 1,516 s
FS_MIN, FS_MAX = 50.0, 20000.0
UPLOAD_SIG_EXT = ('.edf', '.hea', '.dat', '.csv', '.npy', '.txt')
UPLOAD_LAB_EXT = ('.qrs', '.fqrs', '.csv', '.txt')


def _copy_uploads(paths, workdir):
    os.makedirs(workdir, exist_ok=True)
    for f in glob.glob(os.path.join(workdir, '*')):
        if os.path.isfile(f):
            try:
                os.remove(f)
            except OSError:
                pass
    local = []
    for p in paths or []:
        p = p if isinstance(p, str) else getattr(p, 'name', str(p))
        q = os.path.join(workdir, os.path.basename(str(p)))
        shutil.copyfile(str(p), q); local.append(q)
    return local


def _pick_main(local):
    """Chọn tệp tín hiệu chính trong nhóm tệp đã tải lên. Ném LoiDuLieu với thông báo tiếng Việt."""
    if not local:
        raise LoiDuLieu('Chưa chọn tệp nào. Hãy tải lên .edf, hoặc CẶP .dat + .hea, hoặc .csv / .npy / .txt.')
    low = [q.lower() for q in local]
    for ext in ('.edf', '.hea', '.npy', '.csv', '.txt'):
        for q, l in zip(local, low):
            if l.endswith(ext) and not l.endswith('.edf.qrs'):
                return q
    for q, l in zip(local, low):
        if l.endswith('.dat'):
            raise LoiDuLieu(f'Tệp {os.path.basename(q)} là WFDB nhị phân nhưng THIẾU tệp header .hea đi kèm. '
                            'Hãy chọn CẢ HAI tệp (.dat và .hea) cùng lúc rồi tải lên lại.')
    ds = ', '.join(sorted({os.path.splitext(q)[1].lower() or '(không đuôi)' for q in local}))
    raise LoiDuLieu(f'Không nhận ra định dạng nào dùng được (đã nhận: {ds}). '
                    'Chấp nhận: .edf · .dat kèm .hea · .csv · .npy · .txt.')


def doc_nhan_tai_len(path, fs_signal, n_samples_1000):
    """Tệp nhãn tuỳ chọn -> mảng chỉ số mẫu ở 1000 Hz. Ném LoiDuLieu nếu không đọc được / lệch thang."""
    ext = os.path.splitext(path)[1].lower()
    base = os.path.splitext(path)[0]
    if ext in ('.qrs', '.fqrs'):
        try:
            import wfdb
            lab = np.asarray(wfdb.rdann(base, ext[1:]).sample, float)
        except Exception as e:                                  # noqa: BLE001
            raise LoiDuLieu(f'Không đọc được chú giải WFDB {os.path.basename(path)} '
                            f'({type(e).__name__}: {e}). Chú giải .qrs/.fqrs cần tệp header .hea CÙNG TÊN đi kèm; '
                            'nếu không có, hãy dùng tệp .csv/.txt một cột chỉ số mẫu.') from None
    else:
        try:
            arr = np.genfromtxt(path, delimiter=',' if ext == '.csv' else None, dtype=float)
            arr = np.atleast_2d(np.asarray(arr, float))
            if arr.shape[0] == 1 and arr.shape[1] > 1:
                arr = arr.T
            col = arr[:, 0]
            lab = col[np.isfinite(col)]
        except Exception as e:                                  # noqa: BLE001
            raise LoiDuLieu(f'Không đọc được tệp nhãn {os.path.basename(path)} ({type(e).__name__}: {e}). '
                            'Định dạng mong đợi: MỘT cột, mỗi dòng một chỉ số mẫu.') from None
    if lab is None or len(lab) == 0:
        raise LoiDuLieu(f'Tệp nhãn {os.path.basename(path)} rỗng hoặc không có số nào đọc được.')
    lab = np.round(np.asarray(lab, float) * (FS_IN / float(fs_signal))).astype(int)
    lab = lab[(lab >= 0) & (lab < n_samples_1000)]
    if len(lab) == 0:
        raise LoiDuLieu('Mọi chỉ số trong tệp nhãn đều nằm NGOÀI bản ghi '
                        f'(bản ghi dài {n_samples_1000} mẫu ở 1000 Hz). Nhiều khả năng tệp nhãn ghi theo '
                        f'đơn vị khác (giây?) hoặc theo tần số khác {float(fs_signal):g} Hz.')
    return lab


def doc_tai_len(paths, workdir, fs=1000, label_paths=None, lead=None):
    """
    Đường đi của tab "Tải dữ liệu mới": gom tệp -> chọn tệp chính -> kiểm tra -> load_record().
    Trả về dict của load_record() + upload_main, upload_files, nhan_tu, co_nhan, canh_bao[], fs_tu_khai.
    Mọi lỗi đều là LoiDuLieu với thông báo tiếng Việt (KHÔNG trả stack trace ra giao diện).
    """
    local = _copy_uploads(paths, workdir)
    main = _pick_main(local)
    ext = os.path.splitext(main)[1].lower()
    tu_khai = ext in ('.edf', '.hea')
    canh_bao = []
    if not tu_khai:
        try:
            fs = float(fs)
        except (TypeError, ValueError):
            raise LoiDuLieu(f'Tần số lấy mẫu không phải một số: {fs!r}.') from None
        if not np.isfinite(fs) or not (FS_MIN <= fs <= FS_MAX):
            raise LoiDuLieu(f'Tần số lấy mẫu {fs:g} Hz không hợp lý (chấp nhận {FS_MIN:g}–{FS_MAX:g} Hz). '
                            'Tệp .csv/.npy/.txt KHÔNG tự khai tần số nên bạn phải nhập đúng.')
    if ext == '.hea' and not os.path.isfile(os.path.splitext(main)[0] + '.dat'):
        raise LoiDuLieu(f'Có header {os.path.basename(main)} nhưng THIẾU tệp dữ liệu .dat cùng tên. '
                        'Hãy tải lên cả hai tệp cùng lúc.')
    try:
        rec = load_record(main, fs=fs, lead=lead)
    except LoiDuLieu:
        raise
    except Exception as e:                                      # noqa: BLE001
        if ext in ('.csv', '.txt') and isinstance(e, ValueError):
            # lỗi numpy nguyên văn ("Some errors were detected ! Line #2 (got 3 columns instead of 8)") khó hiểu
            # -> nói điều người dùng cần sửa trước, chi tiết kỹ thuật để cuối
            chi_tiet = ' '.join(str(e).split())
            raise LoiDuLieu(f'Không đọc được tệp {os.path.basename(main)} thành bảng số. Tệp .csv/.txt phải gồm các cột SỐ: '
                            'mỗi cột một kênh, mỗi dòng một mẫu, được phép có một dòng tiêu đề; mọi dòng phải có cùng số cột '
                            f'và không lẫn chữ. (Chi tiết kỹ thuật: {chi_tiet})') from None
        raise LoiDuLieu(f'Không đọc được tệp {os.path.basename(main)}: {type(e).__name__}: {e}') from None
    if rec['signals'].size == 0 or rec['signals'].shape[0] == 0:
        raise LoiDuLieu(f'Tệp {os.path.basename(main)} không chứa kênh tín hiệu nào.')
    if not np.isfinite(rec['signals']).any():
        raise LoiDuLieu(f'Tệp {os.path.basename(main)} không có giá trị số hợp lệ nào (toàn NaN/rỗng).')
    if rec['duration_s'] < MIN_DURATION_S:
        raise LoiDuLieu(f'Bản ghi chỉ dài {rec["duration_s"]:.2f} giây — quá ngắn. '.replace('.', ',', 1)
                        + f'Cần ít nhất {MIN_DURATION_S:g} giây (mô hình dùng cửa sổ 4 giây, trường tiếp nhận 1,516 giây). '
                        'Nếu tệp thực ra dài hơn, hãy kiểm tra lại ô tần số lấy mẫu.')
    if rec['signals'].shape[0] > 12:
        canh_bao.append(f'Bản ghi có {rec["signals"].shape[0]} kênh — nhiều hơn 4 kênh bụng thường gặp. '
                        'Hãy kiểm tra xem có kênh nào KHÔNG phải ECG bụng (mô hình vẫn chạy trên mọi kênh).')
    nhan_tu = 'chú giải đi kèm tệp bản ghi' if rec.get('labels') is not None else None
    lab_local = _copy_uploads(label_paths, os.path.join(workdir, '_nhan')) if label_paths else []
    if lab_local:
        lp = None
        for e_ in UPLOAD_LAB_EXT:
            lp = next((q for q in lab_local if q.lower().endswith(e_)), None)
            if lp:
                break
        if lp is None:
            raise LoiDuLieu('Tệp nhãn phải có đuôi .qrs, .fqrs, .csv hoặc .txt (một cột chỉ số mẫu).')
        rec['labels'] = doc_nhan_tai_len(lp, rec.get('fs_orig', fs) or fs, rec['signals'].shape[1])
        nhan_tu = os.path.basename(lp)
    rec['upload_main'] = main
    rec['upload_files'] = [os.path.basename(q) for q in local]
    rec['nhan_tu'] = nhan_tu
    rec['co_nhan'] = rec.get('labels') is not None
    rec['canh_bao'] = canh_bao
    rec['fs_tu_khai'] = bool(tu_khai)
    return rec


def load_dataset_record(key, name):
    """Đọc một bản ghi theo (bộ, tên) — kể cả bản TRÙNG/NHIỄM không có trong sample_records()."""
    rows, err = dataset_rows(key)
    if not rows:
        raise LoiDuLieu(err or f'Chưa có bộ {key} trên đĩa.')
    r = next((x for x in rows if x['ten'] == name), None)
    if r is None:
        raise LoiDuLieu(f'Không có bản ghi {name!r} trong bộ {DATASET_LABEL.get(key, key)}.')
    if key.startswith('silesia'):
        rec = load_silesia(name)
    else:
        rec = load_record(r['duong_dan'])
    rec['note'] = r['ghi_chu']
    rec['nguon_nhan'] = r['nguon_nhan']
    rec['dinh_dang'] = r['dinh_dang']
    rec['duong_dan'] = r['duong_dan']
    return rec
