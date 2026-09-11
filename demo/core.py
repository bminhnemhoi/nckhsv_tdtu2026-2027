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
CINC_RECS = tuple(f'a{i:02d}' for i in range(1, 11))

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
CONF_MODE_LABEL = {'hoc': 'học (GBM trên 12 chỉ số cổ điển / đoạn 4 s, fsqi/gate.py)',
                   'luat': 'luật cứng (4 thành phần, ngưỡng đặt tay)'}


# =========================================================================== dữ liệu mẫu
def adfecgdb_dir():
    try:
        return _adfecgdb_dir()
    except SystemExit:
        return None


def cinc2013_dir():
    return _cinc2013_dir()


def sample_records():
    """dict tên -> {path, kind, dataset}; chỉ liệt kê bản ghi thực sự có trên đĩa."""
    out = {}
    d = adfecgdb_dir()
    if d:
        for r in ADFECGDB_RECS:
            p = os.path.join(d, r + '.edf')
            if os.path.isfile(p):
                out[r] = dict(path=p, kind='edf', dataset='ADFECGDB')
    c = cinc2013_dir()
    if c:
        for r in CINC_RECS:
            p = os.path.join(c, r + '.hea')
            if os.path.isfile(p):
                out[r] = dict(path=p, kind='wfdb', dataset='CinC 2013 set-a')
    return out


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
def checkpoint_for(record_name):
    """ADFECGDB rXX -> fold checkpoint chưa từng thấy rXX; mọi trường hợp khác -> production."""
    n = (record_name or '').lower().strip()
    if n in ADFECGDB_RECS:
        p = _ckpt(f'fetalqrs_tcn_fold_{n}.pt')
        if os.path.isfile(p):
            return p, f'fold {n} (bản ghi {n} KHÔNG nằm trong tập huấn luyện)'
    return _ckpt('fetalqrs_tcn_production.pt'), 'production (huấn luyện trên toàn bộ ADFECGDB)'


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


def front_end(sig_1000):
    """tiền xử lý + khử mẹ cho MỘT kênh -> (x250, residual, maternal_peaks_250)"""
    x = M.preprocess(np.asarray(sig_1000, float), FS_IN, CFG)
    r, mpk = M.cancel_maternal(x, CFG)
    return x, r, mpk


def select_lead(signals_1000, mode='auto'):
    """
    mode = 'auto' -> quy tắc PSD (Power-MF), hoặc số kênh 1..K.
    Trả về (lead_1based, fronts) với fronts[lead] = (x250, residual, mpk) đã tính cho từng kênh.
    """
    K = signals_1000.shape[0]

    def _timed(k):
        t0 = time.perf_counter(); fr = front_end(signals_1000[k - 1])
        return fr, (time.perf_counter() - t0) * 1000.0

    if isinstance(mode, str) and mode.lower().startswith('auto'):
        fronts, fe_ms = {}, {}
        for k in range(1, K + 1):
            fronts[k], fe_ms[k] = _timed(k)
        scores = {k: psd_score(fronts[k][1]) for k in fronts}
        lead = max(scores, key=scores.get)
        return lead, fronts, scores, fe_ms
    lead = int(mode)
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
def analyze(signal_1000hz, labels_1000=None, model='production', fs=1000, front=None,
            confidence_mode=CONFIDENCE_MODE_DEFAULT):
    """
    Phân tích MỘT kênh ECG bụng. signal_1000hz: mảng 1-D (nếu fs != 1000 sẽ được tái lấy mẫu).
    model: 'production' | đường dẫn .pt | tên checkpoint.  front: (x250, res, mpk) đã tính sẵn (tuỳ chọn).
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
    prob = M.probability_series(net, M.robust_scale(res).astype(np.float32),
                                M.robust_scale(x250).astype(np.float32), CFG)
    det250 = M.pick_peaks(prob, thr, CFG).astype(np.int64)
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
    rec: dict từ load_record(). lead: 'auto' | 1..K. model: None -> checkpoint_for(rec['name']).
    confidence_mode: 'hoc' | 'luat' | 'ca_hai' (xem analyze).
    Trả về dict của analyze() + lead, lead_name, lead_scores, checkpoint_note.
    """
    if model is None:
        model, note = checkpoint_for(rec['name'])
    else:
        note = str(model)
    lead, fronts, scores, fe_ms = select_lead(rec['signals'], lead)
    out = analyze(rec['signals'][lead - 1], rec.get('labels'), model=model, front=fronts[lead],
                  confidence_mode=confidence_mode)
    # latency_ms = tiền xử lý + khử mẹ của kênh được chọn + mô hình + chọn đỉnh (KHÔNG tính đọc file)
    out['latency_model_ms'] = out['latency_ms']
    out['latency_frontend_ms'] = float(fe_ms[lead])
    out['latency_ms'] = out['latency_model_ms'] + out['latency_frontend_ms']
    out['latency_all_leads_ms'] = out['latency_model_ms'] + float(sum(fe_ms.values()))
    out.update(lead=lead, lead_name=rec['lead_names'][lead - 1],
               lead_scores=scores, lead_mode='auto (PSD)' if scores is not None else 'thủ công',
               checkpoint_note=note, record=rec['name'], source=rec['source'])
    return out


def _jf(v):
    """float JSON-an toàn: NaN/inf -> None."""
    v = float(v)
    return v if np.isfinite(v) else None


def _jv(v):
    """giá trị JSON-an toàn: bool/int giữ nguyên, số thực -> _jf."""
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
             checkpoint=out['checkpoint'], threshold=_jf(out['threshold']),
             duration_s=_jf(out['duration_s']), n_beats=int(out['n_beats']), fhr_mean=_jf(out['fhr_mean']),
             latency_ms=_jf(out['latency_ms']),
             latency_frontend_ms=_jf(out.get('latency_frontend_ms', float('nan'))),
             latency_model_ms=_jf(out.get('latency_model_ms', out['latency_ms'])),
             confidence_mode=out.get('confidence_mode', c.get('mode', 'luat')),
             confidence=_conf_summary(c),
             confidence_by_mode={m: _conf_summary(cc) for m, cc in out.get('confidence_by_mode', {}).items()})
    if out.get('lead_scores'):
        # khóa phải là str: gr.JSON (orjson) của Gradio 6 từ chối khóa int ("Dict key must be str")
        s['lead_scores'] = {str(int(k)): _jf(v) for k, v in out['lead_scores'].items()}
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
