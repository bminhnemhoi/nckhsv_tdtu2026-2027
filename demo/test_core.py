# -*- coding: utf-8 -*-
"""
Kiểm thử lõi demo (không cần gradio).  Chạy:  python -m pytest demo/test_core.py -v

Hai kiểm thử "bám mốc" bắt buộc theo đề cương P9, chạy ở CẢ HAI chế độ đèn tin cậy ('luat' và 'hoc'):
  * r01 kênh 4 (fold checkpoint chưa từng thấy r01): F1 > 99 và đèn tin cậy = 'cao'
  * a02 của CinC 2013 (zero-shot, production checkpoint): đèn tin cậy KHÔNG phải 'cao'
"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import core  # noqa: E402

RECS = core.sample_records()
need_r01 = pytest.mark.skipif('r01' not in RECS, reason='chưa có ADFECGDB r01')
need_a02 = pytest.mark.skipif('a02' not in RECS, reason='chưa có CinC 2013 a02')


# ------------------------------------------------------------------ hai mốc bắt buộc -- chế độ 'luat'
@need_r01
def test_r01_lead4_f1_above_99_and_confidence_high():
    rec = core.load_record(RECS['r01']['path'])
    assert rec['signals'].shape == (4, 300000) and rec['labels'] is not None
    out = core.analyze_record(rec, lead=4, confidence_mode='luat')
    assert out['checkpoint'] == 'fetalqrs_tcn_fold_r01.pt'          # chưa từng thấy r01
    assert out['metrics']['F1'] > 99.0
    assert out['confidence']['mode'] == 'luat'
    assert out['confidence']['level'] == 'cao'
    assert 100 <= out['fhr_mean'] <= 200
    assert out['n_beats'] > 500


@need_a02
def test_a02_cinc_confidence_not_high():
    rec = core.load_record(RECS['a02']['path'])
    out = core.analyze_record(rec, lead='auto', confidence_mode='luat')
    assert out['checkpoint'] == 'fetalqrs_tcn_production.pt'
    assert out['confidence']['mode'] == 'luat'
    assert out['confidence']['level'] != 'cao'
    assert out['confidence']['level'] in ('trung_binh', 'thap')
    assert any('BÁM NHỊP MẸ' in r or 'nhịp' in r for r in out['confidence']['reasons'])


# ------------------------------------------------------------------ hai mốc bắt buộc -- chế độ 'hoc' (GBM, fsqi/gate.py)
@need_r01
def test_r01_lead4_learned_gate_confidence_high():
    """Chế độ 'hoc' trên r01 kênh 4: đèn 'cao', có đèn từng đoạn 4 s (75 đoạn / 300 s), ngưỡng đoạn lấy từ gate_classical.pkl."""
    rec = core.load_record(RECS['r01']['path'])
    out = core.analyze_record(rec, lead=4, confidence_mode='hoc')
    assert out['checkpoint'] == 'fetalqrs_tcn_fold_r01.pt'
    assert out['metrics']['F1'] > 99.0
    c = out['confidence']
    assert c['mode'] == 'hoc' and out['confidence_mode'] == 'hoc'
    assert c['level'] == 'cao'
    assert 0.0 <= c['score'] <= 1.0
    seg = c['segments']
    assert len(seg['p_bad']) == 75 and len(seg['level']) == 75
    assert 0.0 < seg['q1'] < seg['q2'] < 1.0
    assert c['components']['frac_green'] > 0.7 and c['components']['frac_red'] <= 0.3
    assert not c['components']['locked']


@need_a02
def test_a02_cinc_learned_gate_confidence_not_high():
    """Chế độ 'hoc' trên a02 (zero-shot, mô hình bám nhịp mẹ): đèn KHÔNG được 'cao'."""
    rec = core.load_record(RECS['a02']['path'])
    out = core.analyze_record(rec, lead='auto', confidence_mode='hoc')
    assert out['checkpoint'] == 'fetalqrs_tcn_production.pt'
    c = out['confidence']
    assert c['mode'] == 'hoc'
    assert c['level'] != 'cao'
    assert c['level'] in ('trung_binh', 'thap')
    assert len(c['segments']['p_bad']) == 15                          # 60 s / 4 s
    assert any('BÁM NHỊP MẸ' in r or 'đoạn' in r for r in c['reasons'])


# ------------------------------------------------------------------ hợp đồng của analyze()
@need_r01
def test_analyze_returns_required_keys():
    rec = core.load_record(RECS['r01']['path'], lead=1)
    out = core.analyze(rec['signals'][0], rec['labels'], model=core.checkpoint_for('r01')[0])
    for k in ('raw', 'filtered_250', 'residual_250', 'maternal_peaks', 'prob', 'fetal_peaks_1000',
              'fhr_series', 'fhr_mean', 'n_beats', 'latency_ms', 'confidence',
              'metrics', 'matched', 'missed', 'false'):
        assert k in out, k
    assert len(out['filtered_250']) == len(out['residual_250']) == len(out['prob']) == 75000
    assert out['confidence']['level'] in ('cao', 'trung_binh', 'thap')
    assert 0.0 <= out['confidence']['score'] <= 1.0
    assert isinstance(out['confidence']['reasons'], list) and out['confidence']['reasons']
    m = out['metrics']
    assert m['TP'] + m['FN'] == len(rec['labels'])
    assert m['TP'] + m['FP'] == out['n_beats']
    assert len(out['matched']) == m['TP'] and len(out['missed']) == m['FN'] and len(out['false']) == m['FP']
    assert len(out['fhr_series']) == 75          # 300 s / 4 s


# ------------------------------------------------------------------ đối chiếu khớp với M.match_events
def test_match_with_lists_equals_reference_matcher():
    rng = np.random.default_rng(0)
    ref = np.sort(rng.choice(np.arange(500, 290000, 470), 400, replace=False))
    det = np.concatenate([ref[::2] + rng.integers(-40, 41, len(ref[::2])), rng.integers(0, 300000, 30)])
    a = core.M.match_events(det, ref, 1000, 50)
    b = core.match_with_lists(det, ref, 1000, 50)
    for k in ('TP', 'FP', 'FN', 'Se', 'PPV', 'F1'):
        assert a[k] == pytest.approx(b[k])


# ------------------------------------------------------------------ đọc bản ghi từ mảng/CSV/NPY
def test_load_record_from_array_and_files(tmp_path):
    fs = 500; n = fs * 8; t = np.arange(n) / fs
    x = np.stack([np.sin(2 * np.pi * 2.2 * t + p) for p in (0, 1, 2)])   # 3 kênh, 500 Hz
    r = core.load_record(x, fs=fs)
    assert r['signals'].shape == (3, 8000) and r['fs'] == 1000
    r = core.load_record(x.T, fs=fs, lead=2)                              # dạng N x K cũng được
    assert r['signals'].shape == (1, 8000)
    p = tmp_path / 'sig.npy'; np.save(p, x)
    assert core.load_record(str(p), fs=fs)['signals'].shape == (3, 8000)
    p = tmp_path / 'sig.csv'; np.savetxt(p, x.T, delimiter=',', header='c1,c2,c3', comments='')
    r = core.load_record(str(p), fs=fs)
    assert r['signals'].shape == (3, 8000)
    lab = tmp_path / 'lab.txt'; np.savetxt(lab, np.array([100, 350, 600]), fmt='%d')
    r = core.load_record(str(p), fs=fs, labels=str(lab))
    assert list(r['labels']) == [200, 700, 1200]                          # đưa về 1000 Hz


def test_short_random_signal_gives_low_confidence():
    """Nhiễu trắng 20 s: analyze() phải chạy được và không được báo 'cao'."""
    rng = np.random.default_rng(1)
    out = core.analyze(rng.standard_normal(20000), model='production')
    assert out['confidence']['level'] != 'cao'


def test_checkpoint_routing():
    p, note = core.checkpoint_for('r04')
    assert p.endswith('fetalqrs_tcn_fold_r04.pt') and 'r04' in note
    p, note = core.checkpoint_for('a02')
    assert p.endswith('fetalqrs_tcn_production.pt')
    p, _ = core.checkpoint_for('benh_nhan_moi')
    assert p.endswith('fetalqrs_tcn_production.pt')


def test_summary_is_json_serialisable():
    import json
    rng = np.random.default_rng(2)
    out = core.analyze(rng.standard_normal(12000), model='production')
    out.update(record='x', lead=1, lead_mode='thủ công', latency_frontend_ms=1.0, latency_model_ms=1.0)
    json.dumps(core.summary(out), ensure_ascii=False, allow_nan=False)
