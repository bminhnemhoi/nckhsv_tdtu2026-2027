# -*- coding: utf-8 -*-
"""
Kiểm thử fsqi/fsqi.py (chỉ số chất lượng tín hiệu, không cần dữ liệu thật).

  * all_features trả về đúng tập khoá: 16 topo (TOPO_KEYS) + 10 cổ điển (CLASSICAL_KEYS) = 26, đều hữu hạn
  * thời gian một đoạn 4 s < 200 ms (sau một lần khởi động ripser; lấy tốt nhất trong 3 lần)
  * persistence H0 sublevel-set == scipy.signal.peak_prominences trên tín hiệu tổng hợp (định lý elder)
"""
import os, sys
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import pytest
from scipy import signal as sg

pytest.importorskip('ripser')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'fsqi'))
import fsqi as F  # noqa: E402

FS = 250


def _synthetic(seed=0):
    """xung QRS thai giả ~132 bpm trong 4 s + nhiễu trắng, như fsqi.__main__"""
    rng = np.random.default_rng(seed)
    t = np.arange(4 * FS) / FS
    x = np.zeros(4 * FS)
    peaks = np.arange(0.1, 4.0, 1 / 2.2)
    for p in peaks:
        x += np.exp(-((t - p) ** 2) / (2 * 0.004 ** 2))
    x += 0.1 * rng.standard_normal(len(x))
    det = np.array([int(p * FS) for p in peaks])
    raw = rng.standard_normal(4 * 1000)
    return x, det, raw


def test_all_features_returns_exact_key_set():
    x, det, raw = _synthetic()
    f, tm = F.all_features(x, FS, det, raw, 1000)
    expected = set(F.TOPO_KEYS) | set(F.CLASSICAL_KEYS)
    assert set(f) == expected
    assert len(f) == 26 and len(F.TOPO_KEYS) == 16 and len(F.CLASSICAL_KEYS) == 10
    assert all(np.isfinite(float(v)) for v in f.values())
    assert f['n_det'] == len(det) and 0.0 <= f['rr_plaus'] <= 1.0 and 0.0 <= f['bsqi'] <= 1.0
    assert set(tm) == {'topo_ms', 'sublevel_ms', 'classical_ms', 'total_ms', 'slow'}


def test_all_features_without_model_output_gives_nan_rr():
    x, _, _ = _synthetic(1)
    f, _ = F.all_features(x, FS, None, None)
    assert set(f) == set(F.TOPO_KEYS) | set(F.CLASSICAL_KEYS)
    assert np.isnan(f['rr_cv']) and np.isnan(f['band_ratio']) and f['n_det'] == 0


def test_all_features_under_200ms_per_segment():
    x, det, raw = _synthetic()
    F.all_features(x, FS, det, raw, 1000)                     # khởi động (nạp ripser)
    best = min(F.all_features(x, FS, det, raw, 1000)[1]['total_ms'] for _ in range(3))
    assert best < 200.0, f'{best:.1f} ms'


def test_sublevel_h0_persistence_equals_scipy_prominence():
    for seed in (0, 1, 2):
        x, _, _ = _synthetic(seed)
        r = F.check_sublevel_vs_scipy(x)
        assert r['match'] is True and r['n_compared'] >= 5, r
        assert r['max_abs_diff'] < 1e-9


def test_sublevel_h0_bars_direct_comparison():
    """so trực tiếp: mỗi thanh H0 của -z (đỉnh bị chặn hai phía) có persistence = prominence scipy tại đúng đỉnh đó"""
    x, _, _ = _synthetic(3)
    z = F.robust_scale(x)
    bars = F.sublevel_h0_bars(-z)
    pk, _ = sg.find_peaks(z)
    prom = dict(zip(pk.tolist(), sg.peak_prominences(z, pk)[0].tolist()))
    n = 0
    for b0, d0, bi in bars:
        bi = int(bi)
        if bi in prom and (z[:bi] > z[bi]).any() and (z[bi + 1:] > z[bi]).any():
            assert abs((d0 - b0) - prom[bi]) < 1e-9; n += 1
    assert n >= 5


def test_sublevel_h0_matches_scipy_on_white_noise():
    rng = np.random.default_rng(7)
    r = F.check_sublevel_vs_scipy(rng.standard_normal(1000))
    assert r['match'] is True and r['n_compared'] > 100
