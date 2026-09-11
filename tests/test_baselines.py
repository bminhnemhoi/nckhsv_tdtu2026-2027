# -*- coding: utf-8 -*-
"""
Kiểm thử baseline cổ điển (baselines/ts_baseline.py).

  * TS-PCA + Pan-Tompkins trên r01 kênh 4, 30 s đầu, với siêu tham số ĐÃ chọn trên r01
    (n_pc = 2, thr_frac = 0,75 -- baselines/results.json) -> F1 > 80 (bỏ qua nếu chưa có ADFECGDB)
  * results.json ghi đúng bộ siêu tham số đó
  * Pan-Tompkins trên xung tổng hợp: tìm đúng số nhịp
"""
import os, sys, json
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import pytest

pytest.importorskip('mne'); pytest.importorskip('wfdb'); pytest.importorskip('torch')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'baselines'))
import ts_baseline as B  # noqa: E402

try:
    RAW = B.adfecgdb_dir()
except SystemExit:
    RAW = None
need_data = pytest.mark.skipif(RAW is None, reason='chưa có ADFECGDB')

# siêu tham số chọn CHỈ trên r01 (baselines/results.json, tuning_r01.chosen)
TSPCA_NPC, TSPCA_THR_FRAC = 2, 0.75


def test_results_json_records_the_chosen_hyperparameters():
    p = os.path.join(ROOT, 'baselines', 'results.json')
    if not os.path.isfile(p):
        pytest.skip('chưa có baselines/results.json')
    d = json.load(open(p, encoding='utf-8'))
    ch = d['tuning_r01']['chosen']
    assert ch['TS_PCA'] == {'n_pc': TSPCA_NPC, 'thr_frac': TSPCA_THR_FRAC}
    assert d['baselines']['TS-PCA']['macro_20']['F1_mean'] == pytest.approx(91.05, abs=0.01)
    assert d['baselines']['TS-PCA']['psd_macro_5']['F1_mean'] == pytest.approx(96.74, abs=0.01)


@need_data
def test_tspca_pantompkins_r01_lead4_first_30s_f1_above_80():
    sig, gt = B.load_record(RAW, 'r01')
    n = 30 * B.CFG['fs_in']                                   # 30 s @1000 Hz
    x1000 = sig[4][:n]                                        # kênh EDF 4 = Abdomen_4
    gt30 = gt[gt < n]
    assert 50 <= len(gt30) <= 80                              # ~128 bpm -> ~64 nhịp
    x250 = B.M.preprocess(x1000, B.CFG['fs_in'], B.CFG)
    res, mpk = B.cancel_ts_pca(x250, npc=TSPCA_NPC)
    assert len(res) == len(x250) and len(mpk) >= 20           # ~82 bpm mẹ -> ~41 nhịp mẹ
    det = B.pan_tompkins_fetal(res, thr_frac=TSPCA_THR_FRAC)
    s = B.score(det, gt30)
    assert s['TP'] + s['FN'] == len(gt30)
    assert s['F1'] > 80.0, s


@need_data
def test_prominence_on_group_frontend_r01_lead4_first_30s():
    """baseline thứ ba: cùng front-end với mô hình (M.cancel_maternal), chỉ thay mạng bằng lấy đỉnh (k=3 chọn trên r01)"""
    sig, gt = B.load_record(RAW, 'r01')
    n = 30 * B.CFG['fs_in']
    x250 = B.M.preprocess(sig[4][:n], B.CFG['fs_in'], B.CFG)
    res, _ = B.cancel_median_ls(x250)
    det = B.prominence_detector(res, k=3.0)
    s = B.score(det, gt[gt < n])
    assert s['F1'] > 70.0, s


def test_pan_tompkins_counts_synthetic_fetal_beats():
    fs = B.FS; n = fs * 20; t = np.arange(n) / fs
    rng = np.random.default_rng(0)
    beats = np.arange(0.5, 19.5, 0.45)                        # ~133 bpm
    x = sum(np.exp(-((t - b) ** 2) / (2 * 0.004 ** 2)) for b in beats) + 0.02 * rng.standard_normal(n)
    det = B.pan_tompkins_fetal(x)
    s = B.M.match_events(det, np.round(beats * fs).astype(int), fs, B.TOL_MS)
    assert s['F1'] > 95.0, s
