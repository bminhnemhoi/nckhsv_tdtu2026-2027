# -*- coding: utf-8 -*-
"""
gate.py -- CONG TIN CAY HOC DUOC (thay luat cung cua den tin cay trong demo/core.py).

API (khong phu thuoc mo hinh, chi can fsqi.py + gate_classical.pkl do train_gate.py tao):
  score_segments(res250, x250, prob, det250, raw1000=None)
      -> mang p_bad (xac suat doan xau, F1 doan < 80) cho tung doan 4 s khong chong cua ban ghi
         res250 : phan du sau khu me, 250 Hz          x250 : tin hieu da loc 250 Hz (giu cho API, chua dung)
         prob   : xac suat tung mau cua mo hinh       det250: chi so dinh thai mo hinh chon (250 Hz)
         raw1000: tin hieu tho 1000 Hz cung kenh (de tinh ti so nang luong 10-60 Hz); None -> NaN -> trung vi huan luyen
  segment_levels(p_bad) -> mang 'xanh' / 'vang' / 'do' theo nguong q1/q2 trong pkl (hieu chuan tren ADFECGDB)
  record_confidence(p_bad_list, maternal_lock) -> dict(level, score, reasons, components)
      score = 1 - trung binh p_bad
      level = 'thap' neu ti le doan do > 30 %; 'cao' neu ti le doan xanh > 70 %; con lai 'trung_binh'
      cong bam me: maternal_lock >= 60 % -> 'thap' bat ke p_bad (luat ghi de, giu tu demo/core.py)

Thoi gian: 12 chi so co dien ~12 ms/doan (SampEn cKDTree chiem phan lon) -> ban ghi 5 phut (75 doan) ~1 s. KHONG topo.
"""
from __future__ import annotations
import os, sys, json, time, pickle, warnings
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import fsqi

PKL_DEFAULT = os.path.join(HERE, 'gate_classical.pkl')
META_DEFAULT = os.path.join(HERE, 'gate_meta.json')
LEVELS = ('xanh', 'vang', 'do')
_GATE = {}


def load_gate(path=PKL_DEFAULT):
    """nap pkl (co bo nho dem); canh bao neu phien ban sklearn khac luc huan luyen"""
    path = os.path.abspath(path)
    if path not in _GATE:
        if not os.path.isfile(path):
            raise FileNotFoundError(f'khong thay {path} -- chay: python fsqi/train_gate.py')
        with open(path, 'rb') as f:
            g = pickle.load(f)
        try:
            import sklearn
            if sklearn.__version__ != g.get('sklearn_version'):
                warnings.warn(f'gate_classical.pkl huan luyen voi sklearn {g.get("sklearn_version")}, dang chay {sklearn.__version__}')
        except ImportError:
            pass
        g['medians'] = np.asarray(g['medians'], float)
        g['seg'] = int(round(g['seg_s'] * g['fs']))
        _GATE[path] = g
    return _GATE[path]


def gate_info(path=PKL_DEFAULT):
    """tom tat de hien thi (khong co mo hinh)"""
    g = load_gate(path)
    return dict(features=list(g['features']), q1=float(g['q1']), q2=float(g['q2']), record_rule=dict(g['record_rule']),
                sklearn_version=g.get('sklearn_version'), trained_on=g.get('trained_on'), date=g.get('date'))


# ------------------------------------------------------------------ dac trung tung doan
def segment_features(res250, prob, det250, raw1000=None, fs=250, raw_fs=1000, seg_s=4.0, features=None):
    """ma tran [n_seg, 12] dac trung co dien cua tung doan 4 s (giong eval_fsqi/train_gate, khong topo)"""
    res250 = np.asarray(res250, float); prob = np.asarray(prob, float); det250 = np.asarray(det250, int)
    seg = int(round(seg_s * fs)); n_seg = len(res250) // seg
    q = int(round(raw_fs / fs))
    if features is None:
        features = list(fsqi.CLASSICAL_KEYS) + ['peak_prob_mean', 'prob_max']
    X = np.full((n_seg, len(features)), np.nan)
    for k in range(n_seg):
        a, b = k * seg, (k + 1) * seg
        det_rel = det250[(det250 >= a) & (det250 < b)] - a
        raw = raw1000[a * q:b * q] if raw1000 is not None else None
        f = fsqi.classical_features(res250[a:b], fs, det_rel, raw, raw_fs)
        pseg = prob[a:b]
        f['peak_prob_mean'] = float(np.mean(pseg[det_rel])) if len(det_rel) else 0.0
        f['prob_max'] = float(pseg.max())
        X[k] = [f[c] for c in features]
    return X


def score_segments(res250, x250, prob, det250, raw1000=None, fs=250, raw_fs=1000, path=PKL_DEFAULT):
    """-> p_bad [n_seg] cua tung doan 4 s (x250 giu cho API, hien khong dung)"""
    g = load_gate(path)
    X = segment_features(res250, prob, det250, raw1000, fs, raw_fs, g['seg_s'], g['features'])
    if len(X) == 0:
        return np.zeros(0)
    X = np.where(np.isfinite(X), X, g['medians'])
    return g['model'].predict_proba(X)[:, 1]


def segment_levels(p_bad, path=PKL_DEFAULT):
    g = load_gate(path); p = np.asarray(p_bad, float)
    return np.where(p < g['q1'], 'xanh', np.where(p > g['q2'], 'do', 'vang'))


# ------------------------------------------------------------------ muc ban ghi
def record_confidence(p_bad_list, maternal_lock=float('nan'), path=PKL_DEFAULT):
    """
    p_bad_list   : p_bad tung doan (score_segments)
    maternal_lock: ti le nhip thai trung dinh R me (+/-50 ms); NaN neu khong biet
    -> dict(level in {'cao','trung_binh','thap'}, score in [0,1], reasons [str], components {..})
    """
    g = load_gate(path); R = g['record_rule']
    p = np.asarray(p_bad_list, float); p = p[np.isfinite(p)]
    n = len(p); reasons = []; comp = dict(n_seg=int(n))
    lock = float(maternal_lock) if maternal_lock is not None else float('nan')
    locked = np.isfinite(lock) and lock >= R['maternal_lock']
    comp['maternal_lock'] = lock
    if n == 0:
        comp.update(mean_p_bad=float('nan'), frac_green=0.0, frac_yellow=0.0, frac_red=0.0, n_green=0, n_yellow=0, n_red=0)
        reasons.append('Bản ghi ngắn hơn một đoạn 4 s — không chấm được')
        level, score = 'thap', 0.0
    else:
        lv = segment_levels(p, path)
        fg, fy, fr = (float(np.mean(lv == k)) for k in LEVELS)
        score = float(1.0 - p.mean())
        comp.update(mean_p_bad=float(p.mean()), frac_green=fg, frac_yellow=fy, frac_red=fr,
                    n_green=int((lv == 'xanh').sum()), n_yellow=int((lv == 'vang').sum()), n_red=int((lv == 'do').sum()))
        # 12 chỉ số = 6 thuần tín hiệu + 4 tính trên nhịp mạng tìm ra + 2 xác suất của mạng -> cổng KHÔNG độc lập với mạng
        reasons.append(f'Bộ phân loại GBM (12 chỉ số của đoạn: 6 thuần tín hiệu, 4 tính trên nhịp mạng tìm ra, 2 là xác suất của mạng; '
                       f'huấn luyện trên ADFECGDB): '
                       f'{comp["n_green"]}/{n} đoạn 4 s xanh ({fg * 100:.0f} %), {comp["n_yellow"]} vàng, {comp["n_red"]} đỏ ({fr * 100:.0f} %)')
        reasons.append(f'Xác suất đoạn lỗi trung bình {p.mean():.2f} → điểm {score:.2f} '
                       f'(ngưỡng đoạn: xanh < {g["q1"]:.3f}, đỏ > {g["q2"]:.3f}, hiệu chuẩn trên ADFECGDB ngoài fold: 85 % xanh, 5 % đỏ)')
        if fr > R['red_frac_thr']:
            level = 'thap'; reasons.append(f'> {R["red_frac_thr"] * 100:.0f} % đoạn đỏ → THẤP')
        elif fg > R['green_frac_thr']:
            level = 'cao'; reasons.append(f'> {R["green_frac_thr"] * 100:.0f} % đoạn xanh và ≤ {R["red_frac_thr"] * 100:.0f} % đoạn đỏ → CAO')
        else:
            level = 'trung_binh'; reasons.append(f'≤ {R["green_frac_thr"] * 100:.0f} % đoạn xanh, ≤ {R["red_frac_thr"] * 100:.0f} % đoạn đỏ → TRUNG BÌNH')
    if np.isfinite(lock):
        reasons.append(f'{lock * 100:.0f} % nhịp thai trùng đỉnh R mẹ (±50 ms; ngẫu nhiên ≈ 13–22 %)'
                       + (f' ≥ {R["maternal_lock"] * 100:.0f} % → mô hình đang BÁM NHỊP MẸ → THẤP (luật ghi đè)' if locked else ''))
    if locked:
        level = 'thap'
    comp['locked'] = bool(locked)
    return dict(level=level, score=float(score), reasons=reasons, components=comp)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print(json.dumps(gate_info(), ensure_ascii=False, indent=1))
    rng = np.random.default_rng(0); fs = 250; t = np.arange(75 * 1000) / fs
    x = np.zeros_like(t)
    for p in np.arange(0.1, t[-1], 1 / 2.2):
        x += np.exp(-((t - p) ** 2) / (2 * 0.004 ** 2))
    x += 0.1 * rng.standard_normal(len(t))
    det = (np.arange(0.1, t[-1], 1 / 2.2) * fs).astype(int)
    prob = np.zeros_like(t); prob[det] = 0.97
    t0 = time.perf_counter(); pb = score_segments(x, x, prob, det, rng.standard_normal(len(t) * 4))
    print(f'{len(pb)} doan, p_bad TB {pb.mean():.3f}, {(time.perf_counter() - t0) * 1000:.0f} ms')
    print(json.dumps(record_confidence(pb, 0.15), ensure_ascii=False, indent=1))
    print('bam me 75% ->', record_confidence(pb, 0.75)['level'])
