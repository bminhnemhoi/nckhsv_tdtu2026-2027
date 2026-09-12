# -*- coding: utf-8 -*-
"""
Kiểm thử lõi demo (không cần gradio).  Chạy:  python -m pytest demo/test_core.py -v

Mô hình 22 chủ thể: r01 dùng checkpoint fold 22 ca KHÔNG chứa r01; CinC dùng 22_production (zero-shot).
Hai kiểm thử "bám mốc" bắt buộc, chạy ở CẢ HAI chế độ đèn tin cậy ('luat' và 'hoc'):
  * r01 kênh 4: F1 > 99 và đèn tin cậy = 'cao'
  * a02 của CinC 2013 (bản sạch, zero-shot): đèn tin cậy KHÔNG phải 'cao'
Quy tắc chọn kênh peakprob (mặc định): định nghĩa khớp fsqi/gate.py, mù nhãn, và cứu được a09 so với PSD
(con số đối chiếu: analysis/chonkenh_results.json -> F1_tung_ban_ghi.cinc.a09: psd 19,35 / peakprob 94,25).
"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import core  # noqa: E402

RECS = core.sample_records()
need_r01 = pytest.mark.skipif('r01' not in RECS, reason='chưa có ADFECGDB r01')
need_a02 = pytest.mark.skipif('a02' not in RECS, reason='chưa có CinC 2013 a02')
need_a09 = pytest.mark.skipif('a09' not in RECS, reason='chưa có CinC 2013 a09')
need_b203 = pytest.mark.skipif('B2_03' not in RECS, reason='chưa có Silesia B2_03')
need_22 = pytest.mark.skipif(not os.path.isfile(core._ckpt('fetalqrs_tcn_22_production.pt')), reason='thiếu checkpoint 22 ca')


# ------------------------------------------------------------------ hai mốc bắt buộc -- chế độ 'luat'
@need_r01
@need_22
def test_r01_lead4_f1_above_99_and_confidence_high():
    rec = core.load_record(RECS['r01']['path'])
    assert rec['signals'].shape == (4, 300000) and rec['labels'] is not None
    out = core.analyze_record(rec, lead=4, confidence_mode='luat')
    assert out['checkpoint'] == 'fetalqrs_tcn_22_fold_05.pt'            # fold 05: r01 là test subject (eval_22.json)
    assert 'KHÔNG nằm trong tập huấn luyện' in out['checkpoint_note']
    assert out['metrics']['F1'] > 99.0
    assert out['confidence']['mode'] == 'luat'
    assert out['confidence']['level'] == 'cao'
    assert 100 <= out['fhr_mean'] <= 200
    assert out['n_beats'] > 500
    assert out['leads'] is None and out['lead_mode'] == 'thủ công'


@need_a02
@need_22
def test_a02_cinc_confidence_not_high():
    rec = core.load_sample('a02', RECS)
    out = core.analyze_record(rec, lead='auto', confidence_mode='luat')
    assert out['checkpoint'] == 'fetalqrs_tcn_22_production.pt'
    assert out['confidence']['mode'] == 'luat'
    assert out['confidence']['level'] != 'cao'
    assert out['confidence']['level'] in ('trung_binh', 'thap')


# ------------------------------------------------------------------ hai mốc bắt buộc -- chế độ 'hoc' (GBM, fsqi/gate.py)
@need_r01
@need_22
def test_r01_lead4_learned_gate_confidence_high():
    """Chế độ 'hoc' trên r01 kênh 4: đèn 'cao', có đèn từng đoạn 4 s (75 đoạn / 300 s), ngưỡng đoạn lấy từ gate_classical.pkl."""
    rec = core.load_record(RECS['r01']['path'])
    out = core.analyze_record(rec, lead=4, confidence_mode='hoc')
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
@need_22
def test_a02_cinc_learned_gate_confidence_not_high():
    """Chế độ 'hoc' trên a02 (bản sạch, zero-shot): đèn KHÔNG được 'cao'."""
    rec = core.load_sample('a02', RECS)
    out = core.analyze_record(rec, lead='auto', confidence_mode='hoc')
    assert out['checkpoint'] == 'fetalqrs_tcn_22_production.pt'
    c = out['confidence']
    assert c['mode'] == 'hoc'
    assert c['level'] in ('trung_binh', 'thap')
    assert len(c['segments']['p_bad']) == 15                          # 60 s / 4 s


# ------------------------------------------------------------------ quy tắc chọn kênh peakprob
def test_peakprob_score_matches_gate_feature_definition():
    """peakprob_score = trung vị qua các đoạn 4 s của cột peak_prob_mean trong fsqi/gate.segment_features."""
    import gate as fgate
    rng = np.random.default_rng(3)
    n = 250 * 30                                   # 30 s @ 250 Hz -> 7 đoạn đầy
    prob = rng.uniform(0, 1, n); res = rng.standard_normal(n)
    det = np.sort(rng.choice(np.arange(0, n, 3), 60, replace=False))
    X = fgate.segment_features(res, prob, det, None, 250, 1000, 4.0, ['peak_prob_mean'])
    assert X.shape == (7, 1)
    assert core.peakprob_score(prob, det) == pytest.approx(float(np.median(X[:, 0])))
    assert core.peakprob_score(prob, np.zeros(0, int)) == 0.0        # không đỉnh -> 0


@need_a09
@need_22
def test_a09_peakprob_rescues_lead_choice_vs_psd():
    """a09: PSD chọn kênh sai (F1 < 30), peakprob chọn kênh khác với F1 > 90 (analysis/chonkenh_results.json)."""
    rec = core.load_sample('a09', RECS)
    pp = core.analyze_record(rec, lead='peakprob')
    psd = core.analyze_record(rec, lead='psd')
    assert pp['lead_rule'] == 'peakprob' and psd['lead_rule'] == 'psd'
    assert pp['lead'] != psd['lead']
    assert psd['metrics']['F1'] < 30.0
    assert pp['metrics']['F1'] > 90.0
    assert set(pp['leads']) == {1, 2, 3, 4}
    for k, d in pp['leads'].items():
        assert 0.0 <= d['peakprob'] <= 1.0 and 'F1' in d and d['selected'] == (k == pp['lead'])
    assert pp['leads'][pp['lead']]['peakprob'] == max(d['peakprob'] for d in pp['leads'].values())
    assert pp['lead_mode'] == 'auto (peakprob)' and psd['lead_mode'] == 'auto (PSD)'
    # đối chiếu với con số đã ghi trên đĩa (cùng checkpoint 22_production, cùng quy tắc)
    with open(os.path.join(ROOT, 'analysis', 'chonkenh_results.json'), encoding='utf-8') as f:
        ref = json.load(f)['F1_tung_ban_ghi']['cinc']['a09']
    assert pp['metrics']['F1'] == pytest.approx(ref['peakprob'], abs=0.5)
    assert psd['metrics']['F1'] == pytest.approx(ref['psd'], abs=0.5)


@need_a09
@need_22
def test_peakprob_is_label_blind():
    """Bỏ nhãn đi, quy tắc vẫn chọn đúng kênh đó (chọn kênh không đọc nhãn)."""
    rec = core.load_sample('a09', RECS)
    with_lab = core.analyze_record(rec, lead='peakprob')
    rec2 = dict(rec); rec2['labels'] = None
    no_lab = core.analyze_record(rec2, lead='peakprob')
    assert with_lab['lead'] == no_lab['lead']
    assert 'metrics' not in no_lab and 'F1' not in no_lab['leads'][1]
    assert no_lab['lead_scores'] == with_lab['lead_scores']


@need_r01
@need_22
def test_r01_auto_peakprob_uses_precomputed_inference_consistently():
    """Chọn tự động rồi phân tích: prob/đỉnh của kênh được chọn phải trùng với chạy tay kênh đó."""
    rec = core.load_record(RECS['r01']['path'])
    auto = core.analyze_record(rec, lead='auto')
    manual = core.analyze_record(rec, lead=auto['lead'])
    assert auto['n_beats'] == manual['n_beats']
    assert np.array_equal(auto['fetal_peaks_250'], manual['fetal_peaks_250'])
    assert auto['metrics']['F1'] == pytest.approx(manual['metrics']['F1'])
    assert auto['latency_all_leads_ms'] > auto['latency_ms']


# ------------------------------------------------------------------ bản ghi Silesia và cờ rò rỉ
@need_b203
@need_22
def test_b2_03_silesia_loads_and_uses_fold_11():
    rec = core.load_sample('B2_03', RECS)
    assert rec['signals'].shape[0] == 4 and rec['labels'] is not None and rec['source'] == 'Silesia'
    p, note = core.checkpoint_for('B2_03')
    assert p.endswith('fetalqrs_tcn_22_fold_11.pt') and 'B2_03' in note


def test_sample_records_flags_leaks_and_showcase_is_clean():
    assert len(core.CINC_LEAK) == 15 and len(core.CINC_CLEAN) == 60
    assert not (set(core.DEMO_SHOWCASE) & set(core.CINC_LEAK))
    for n, d in RECS.items():
        if n in core.CINC_LEAK:
            assert d['leak'] and 'RÒ RỈ' in d['note']
        elif n.startswith('a'):
            assert not d.get('leak')


def test_checkpoint_routing():
    p, note = core.checkpoint_for('r04')
    assert p.endswith('fetalqrs_tcn_22_fold_06.pt') and 'r04' in note
    p, note = core.checkpoint_for('B1_07')
    assert p.endswith('fetalqrs_tcn_22_fold_10.pt')
    p, note = core.checkpoint_for('a02')
    assert p.endswith('fetalqrs_tcn_22_production.pt') and 'zero-shot' in note
    p, _ = core.checkpoint_for('benh_nhan_moi')
    assert p.endswith('fetalqrs_tcn_22_production.pt')


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
    out = core.analyze(rng.standard_normal(20000))
    assert out['confidence']['level'] != 'cao'


def test_random_multichannel_record_auto_select_runs():
    """Bản ghi 3 kênh nhiễu 12 s tải lên: chọn tự động peakprob chạy được, trả đủ leads, JSON-hoá được."""
    rng = np.random.default_rng(4)
    rec = core.load_record(rng.standard_normal((3, 12000)), fs=1000, name='nhieu')
    out = core.analyze_record(rec, lead='auto')
    assert out['lead'] in (1, 2, 3) and set(out['leads']) == {1, 2, 3}
    assert out['confidence']['level'] != 'cao'
    json.dumps(core.summary(out), ensure_ascii=False, allow_nan=False)


def test_summary_is_json_serialisable():
    rng = np.random.default_rng(2)
    out = core.analyze(rng.standard_normal(12000))
    out.update(record='x', lead=1, lead_mode='thủ công', latency_frontend_ms=1.0, latency_model_ms=1.0)
    s = core.summary(out)
    json.dumps(s, ensure_ascii=False, allow_nan=False)
    assert s['gate_note'] == core.GATE_NOTE
