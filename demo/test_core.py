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
import os, sys, json, re
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


# ================================================================== A1: metadata bộ dữ liệu của nhóm
def _ds(key):
    rows, err = core.dataset_rows(key)
    if not rows:
        pytest.skip(f'chưa có bộ {key} trên đĩa: {err}')
    return rows


def test_dataset_rows_khoa_khong_hop_le():
    with pytest.raises(ValueError):
        core.dataset_rows('khong_ton_tai')


@pytest.mark.parametrize('key', core.DATASET_KEYS)
def test_dataset_rows_du_truong_va_doc_that_tu_dia(key):
    rows = _ds(key)
    can = ('ten', 'duong_dan', 'dinh_dang', 'fs_Hz', 'do_dai_s', 'so_kenh_bung',
           'so_nhip_nhan', 'nguon_nhan', 'ghi_chu', 'kenh')
    for r in rows:
        assert set(can) <= set(r), f'{key}/{r.get("ten")} thiếu trường'
        assert os.path.isfile(r['duong_dan']), f'{key}/{r["ten"]}: đường dẫn không có thật'
        assert 50 <= r['fs_Hz'] <= 20000
        assert r['do_dai_s'] > 1.0
        assert r['so_kenh_bung'] >= 1
        assert r['so_nhip_nhan'] is None or r['so_nhip_nhan'] > 0


def test_dataset_cinc_dung_60_sach_va_15_nhiem():
    sach = _ds('cinc_sach'); nhiem = _ds('cinc_nhiem')
    assert len(sach) == 60 and len(nhiem) == 15
    ten_sach = {r['ten'] for r in sach}; ten_nhiem = {r['ten'] for r in nhiem}
    assert ten_nhiem == set(core.CINC_LEAK)
    assert not (ten_sach & ten_nhiem)
    for r in nhiem:
        assert 'NHIỄM' in r['ghi_chu'] and core.CINC_LEAK[r['ten']] in r['ghi_chu']
    for r in sach:
        if r['ten'] in core.CINC_BAD_ANN:
            assert 'SAI' in r['ghi_chu']
    # metadata phải KHỚP header thật, không ghi cứng
    import wfdb
    h = wfdb.rdheader(os.path.splitext(sach[0]['duong_dan'])[0])
    assert sach[0]['fs_Hz'] == float(h.fs)
    assert sach[0]['so_kenh_bung'] == int(h.n_sig)
    assert sach[0]['do_dai_s'] == pytest.approx(h.sig_len / h.fs)


def test_dataset_adfecgdb_bo_kenh_truc_tiep():
    rows = _ds('adfecgdb')
    assert len(rows) == 5
    for r in rows:
        assert r['so_kenh_bung'] == 4                  # 5 kênh trong EDF, bỏ Direct_1
        assert 'Direct' in r['kenh']                   # kênh trực tiếp CÓ trong tệp nhưng không được đếm
        assert 'TRỰC TIẾP' in r['nguon_nhan']


def test_dataset_silesia_gan_co_5_ban_trung():
    rows = _ds('silesia_b2')
    trung = {r['ten'] for r in rows if 'TRÙNG' in r['ghi_chu']}
    assert trung == set(core.SILESIA_DUP)
    b1 = _ds('silesia_b1')
    assert all('GIÁN TIẾP' in r['nguon_nhan'] for r in b1)


def test_header_example_doc_nguyen_van_tu_dia():
    _ds('cinc_sach')
    p, txt = core.header_example('cinc_sach', n_lines=8)
    assert p and os.path.isfile(p) and txt
    with open(p, encoding='utf-8', errors='replace') as f:
        that = f.read()
    assert that.startswith(txt.split('\n')[0])         # đúng nguyên văn dòng đầu
    assert len(txt.split('\n')) <= 8
    assert core.header_example('adfecgdb')[1] is None  # EDF nhị phân -> không in


def test_preview_window_va_load_dataset_record():
    rows = _ds('cinc_sach')
    rec = core.load_dataset_record('cinc_sach', rows[0]['ten'])
    assert rec['signals'].shape[0] == rows[0]['so_kenh_bung']
    w = core.preview_window(rec, 0.0, 10.0)
    assert w['signals'].shape == (rec['signals'].shape[0], 10000)
    assert w['t'][0] == 0.0 and w['t'][-1] == pytest.approx(9.999)
    assert w['labels_s'] is not None and 5 <= w['n_beats_window'] <= 40      # 30-240 nhịp/phút
    with pytest.raises(core.LoiDuLieu):
        core.load_dataset_record('cinc_sach', 'khong_co_ban_nay')


# ================================================================== A2: tải dữ liệu mới
def _vidu(name):
    p = os.path.join(HERE, 'assets', name)
    if not os.path.isfile(p):
        pytest.skip(f'chưa có tệp ví dụ {p}')
    return p


def test_doc_tai_len_csv_kem_nhan(tmp_path):
    rec = core.doc_tai_len([_vidu('vidu_tai_len.csv')], str(tmp_path), fs=1000,
                           label_paths=[_vidu('vidu_tai_len_nhan.csv')])
    assert rec['signals'].shape == (4, 30000) and rec['fs'] == 1000
    assert rec['co_nhan'] and rec['nhan_tu'] == 'vidu_tai_len_nhan.csv'
    assert 40 <= len(rec['labels']) <= 120                                   # 30 s thai nhi
    assert rec['fs_tu_khai'] is False
    out = core.analyze_record(rec, lead='auto')
    assert 'metrics' in out and out['metrics']['F1'] > 0


def test_doc_tai_len_khong_co_nhan_thi_khong_co_F1(tmp_path):
    rec = core.doc_tai_len([_vidu('vidu_tai_len.csv')], str(tmp_path), fs=1000)
    assert rec['co_nhan'] is False and rec['nhan_tu'] is None
    out = core.analyze_record(rec, lead='auto')
    assert 'metrics' not in out                       # KHÔNG được bịa F1 khi không có nhãn


def test_doc_tai_len_npy(tmp_path):
    rng = np.random.default_rng(7)
    p = tmp_path / 'x.npy'; np.save(p, rng.standard_normal((4, 12000)))
    rec = core.doc_tai_len([str(p)], str(tmp_path / 'wd'), fs=1000)
    assert rec['signals'].shape == (4, 12000) and rec['source'] == 'NPY'
    assert rec['co_nhan'] is False


def test_doc_tai_len_wfdb_dat_kem_hea(tmp_path):
    rows = _ds('cinc_sach')
    base = os.path.splitext(rows[0]['duong_dan'])[0]
    rec = core.doc_tai_len([base + '.dat', base + '.hea'], str(tmp_path), fs=1)   # fs bị bỏ qua: tệp tự khai
    assert rec['fs_tu_khai'] is True and rec['signals'].shape[0] == 4
    assert rec['duration_s'] == pytest.approx(rows[0]['do_dai_s'])


@pytest.mark.parametrize('mo_ta, dung', [
    ('khong_tep', lambda tp: ([], {})),
    ('dat_thieu_hea', lambda tp: ([_mk(tp, 'a.dat', b'\x00' * 4000)], {})),
    ('dinh_dang_la', lambda tp: ([_mk(tp, 'a.mat', b'\x00' * 4000)], {})),
    ('npy_hong', lambda tp: ([_mk(tp, 'a.npy', b'day khong phai numpy' * 50)], dict(fs=1000))),
])
def test_doc_tai_len_loi_than_thien(mo_ta, dung, tmp_path):
    paths, kw = dung(tmp_path)
    with pytest.raises(core.LoiDuLieu) as ei:
        core.doc_tai_len(paths, str(tmp_path / 'wd'), **kw)
    msg = str(ei.value)
    assert msg and msg[0].isupper() and 'Traceback' not in msg


def _mk(tmp_path, name, data):
    p = tmp_path / name
    p.write_bytes(data)
    return str(p)


def test_doc_tai_len_fs_vo_ly_va_qua_ngan(tmp_path):
    sig = _vidu('vidu_tai_len.csv')
    for fs in (3, 0, -100, 1e9, 'abc'):
        with pytest.raises(core.LoiDuLieu):
            core.doc_tai_len([sig], str(tmp_path / 'wd'), fs=fs)
    p = tmp_path / 'ngan.csv'
    np.savetxt(p, np.random.default_rng(3).standard_normal((2000, 4)), delimiter=',')
    with pytest.raises(core.LoiDuLieu) as ei:
        core.doc_tai_len([str(p)], str(tmp_path / 'wd'), fs=1000)
    assert 'quá ngắn' in str(ei.value)


def test_doc_nhan_tai_len_lech_thang(tmp_path):
    p = tmp_path / 'nhan.csv'
    np.savetxt(p, np.arange(900000, 900100), fmt='%d')
    with pytest.raises(core.LoiDuLieu) as ei:
        core.doc_tai_len([_vidu('vidu_tai_len.csv')], str(tmp_path / 'wd'), fs=1000, label_paths=[str(p)])
    assert 'NGOÀI' in str(ei.value)
    p2 = tmp_path / 'rong.txt'; p2.write_text('', encoding='utf-8')
    with pytest.raises(core.LoiDuLieu):
        core.doc_tai_len([_vidu('vidu_tai_len.csv')], str(tmp_path / 'wd2'), fs=1000, label_paths=[str(p2)])


def test_tep_vi_du_dung_la_trich_tu_a09():
    """Tệp ví dụ PHẢI khớp bit-đối-bit với 30 s đầu của a09 — nếu không thì nó là số bịa."""
    rows = _ds('cinc_sach')
    if 'a09' not in {r['ten'] for r in rows}:
        pytest.skip('không có a09')
    import wfdb
    r = wfdb.rdrecord(os.path.join(core.cinc2013_dir(), 'a09'))
    goc = np.nan_to_num(r.p_signal)[:30000]
    doc = np.genfromtxt(_vidu('vidu_tai_len.csv'), delimiter=',', skip_header=1)
    assert doc.shape == goc.shape
    assert np.abs(doc - goc).max() < 1e-4                     # ghi 5 chữ số thập phân
    ann = np.asarray(wfdb.rdann(os.path.join(core.cinc2013_dir(), 'a09'), 'fqrs').sample, int)
    nhan = np.loadtxt(_vidu('vidu_tai_len_nhan.csv'), dtype=int, ndmin=1)
    assert list(nhan) == list(ann[(ann >= 0) & (ann < 30000)])



# ------------------------------------------------------------------ T3: chế độ trình bày (kể chuyện 5 bước) trong demo/app.py
def _app():
    pytest.importorskip('gradio')
    import app                                                   # dựng Blocks khi import (~5 s)
    return app


CHUOI_CAM = ('SOTA', 'novel', 'state-of-the-art', 'đầu tiên', 'tiền đăng ký', 'pre-registered', 'phát hiện rò rỉ',
             'em phát hiện', 'mô hình không phải nút thắt', 'lượng cực', 'thiếu tín hiệu thật', 'Q1', 'CinC 2026',
             # yêu cầu [E]: không JSON, không đường dẫn tệp, không tên hàm, không số đã rút, không bảng 75 bản
             '.json', 'analysis/', 'fsqi/', '.pkl', '.pt ', 'checkpoint', '75 bản', 'demo/', 'core.')


def _story_texts_on_screen(app):
    """Mọi chữ tĩnh của chế độ trình bày: hằng số + giá trị ban đầu của thành phần gắn lớp rf-story."""
    parts = [app.STORY_TITLE_HTML, app.STORY_UPLOAD_CARD, *app.STORY_STEPS, *app.STORY_CAPTION, app.story_summary_html(None)]
    parts += [app.story_card_html(n) for n in app.STORY_RECS]
    for b in app.demo.blocks.values():
        cls = getattr(b, 'elem_classes', None) or []
        if 'rf-story' in cls and isinstance(getattr(b, 'value', None), str):
            parts.append(b.value)
    return parts


def test_trinh_bay_5_buoc_moi_luc_mot_buoc():
    app = _app()
    assert len(app.STORY_STEPS) == 5 == app.STORY_N_STEPS == len(app.STORY_CAPTION)
    for s in range(1, 6):
        v = app.story_view(s)
        assert v[0] == s
        vis = [u['visible'] for u in v[2:7]]
        assert vis.count(True) == 1 and vis[s - 1] is True
        assert f'rf-pg-on"><span class="rf-pg-n">{s}<' in v[1]
    assert app.story_step(1, -1)[0] == 1                          # không lùi quá bước 1
    assert app.story_step(5, +1)[0] == 1                          # hết bước 5 -> xem lại từ đầu
    assert app.story_step(2, +1)[0] == 3


def test_trinh_bay_che_do_chuyen_gia_bat_tat_giu_8_tab():
    app = _app()
    import gradio as gr
    assert app.toggle_expert(True)['visible'] is True and app.toggle_expert(False)['visible'] is False
    tabs = [b.label for b in app.demo.blocks.values() if isinstance(b, gr.Tab)]
    for t in ('Tín hiệu (5 tầng)', 'Chọn kênh — cả 4 kênh', 'Nhịp tim thai + đèn đoạn', 'So sánh với nhãn',
              'Kết quả tổng hợp (60 bản sạch)', 'Dữ liệu của nhóm', 'Tải dữ liệu mới', 'Nhật ký (JSON)'):
        assert t in tabs, f'thiếu tab {t}'
    cb = [b for b in app.demo.blocks.values() if isinstance(b, gr.Checkbox) and str(b.label).startswith('Chế độ chuyên gia')]
    assert len(cb) == 1 and cb[0].value is False                  # mặc định TẮT


def test_trinh_bay_khong_co_chuoi_cam_tren_giao_dien():
    app = _app()
    for txt in _story_texts_on_screen(app):
        for cam in CHUOI_CAM:
            assert cam not in txt, f'chuỗi cấm "{cam}" trong: {txt[:120]}'


def test_trinh_bay_the_so_doc_tu_json_tren_dia():
    app = _app()
    n = app.STORY_NUM
    p = os.path.join(ROOT, 'demo', 'results', 'demo_check_showcase.json')
    if not os.path.isfile(p):
        pytest.skip('chưa có demo/results/demo_check_showcase.json')
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    for r in app.STORY_RECS:
        assert abs(n[r]['F1'] - d['rows'][f'{r}_leadpeakprob']['metrics']['F1']) < 1e-9
    assert n['a02']['bam_me'] > 0.6                              # cổng "bám nhịp mẹ" ghi đè -> đỏ
    spec = app.story_card_spec('a02')
    assert f'{n["a02"]["bam_me"] * 100:.0f} %' in spec['cho_thay'] and 'ĐỎ' in spec['so']
    assert app._vn(n['r01']['F1']) in app.story_card_spec('r01')['so']


@need_a09
@need_22
def test_trinh_bay_bam_the_a09_ra_dung_ban_ghi_va_ca_2_quy_tac():
    app = _app()
    r = app.story_compute('a09')
    out = r['out']
    assert out['record'] == 'a09' and out['lead_rule'] == 'peakprob' and out['confidence_mode'] == 'hoc'
    assert sorted(r['figs']) == [1, 2, 3, 4, 5] and sorted(r['texts']) == [1, 2, 3, 4, 5]
    assert all(len(fig.data) > 0 for fig in r['figs'].values())
    rules = app.story_rules(out)
    assert rules['khac'] and rules['k_pp'] == out['lead']
    with open(os.path.join(ROOT, 'analysis', 'chonkenh_results.json'), encoding='utf-8') as f:
        ref = json.load(f)['F1_tung_ban_ghi']['cinc']['a09']
    assert rules['f1_pp'] == app._vn(ref['peakprob']) and rules['f1_psd'] == app._vn(ref['psd'])
    assert 'peakprob' in r['rules_md'] and 'PSD' in r['rules_md'] and rules['f1_pp'] in r['rules_md'] and rules['f1_psd'] in r['rules_md']
    assert rules['f1_pp'] in r['texts'][4][0] and rules['f1_psd'] in r['texts'][4][0]
    # đầu ra Gradio: 4 thẻ + 18 ô nội dung + thanh tóm tắt + 9 ô trạng thái bước = 32, và quay về bước 1
    o = app.story_run('a09')
    assert len(o) == 33 == app.STORY_N_OUTS and o[-10] == 1 and o[-1] == ''     # phần tử cuối: dòng trạng thái đã xoá
    assert 'rf-sc-on' in o[1] and 'rf-sc-on' not in o[0]          # thẻ a09 sáng, thẻ r01 tắt
    # màn hình sau khi chạy không được có chuỗi cấm
    for txt in (r['cards'], r['compare'], r['summary'], r['rules_md'], *[t for pair in r['texts'].values() for t in pair]):
        for cam in CHUOI_CAM:
            assert cam not in txt, f'chuỗi cấm "{cam}" trong: {txt[:120]}'


@need_a09
@need_22
def test_trinh_bay_thanh_tom_tat_du_6_muc():
    app = _app()
    out = app.story_compute('a09')['out']
    h = app.story_summary_html(out)
    assert h.count('class="rf-sum-i"') == 6
    for k in ('Bản ghi', 'Bộ dữ liệu', 'Dây đã chọn', 'F1 (bắt đủ và báo đúng, 100 là hoàn hảo)', 'Nhịp tim thai trung bình', 'Đèn tin cậy'):
        assert k in h
    assert 'a09' in h and 'CinC 2013' in h and 'quy tắc mới' in h and out['confidence']['label'] in h
    assert '<s>' not in h                                          # đèn xanh: nhịp tim không bị gạch
    s60 = app.STORY_60
    if s60 is None:
        pytest.skip('chưa có analysis/dulieu_results.json')
    # luôn báo đủ bốn số: cũ · khai báo trước (gate4) · mới hậu kiểm · trần
    with open(os.path.join(ROOT, 'analysis', 'dulieu_results.json'), encoding='utf-8') as f:
        B = json.load(f)['chon_kenh_60_sach']['bang']
    assert s60['n'] == 60
    # đủ năm số: cũ · gate (kế hoạch chọn trước, trượt Holm) · gate4 · peakprob (hậu kiểm) · trần
    for k in ('psd', 'gate', 'gate4', 'peakprob', 'oracle'):
        assert abs(s60[k] - B[k]['mean_60_sach']) < 1e-9 and app._vn(s60[k]) in h, k
    assert 'trước khi chạy (gate)' in h and 'chọn sau khi xem kết quả' in h and 'trần' in h
    assert app.story_summary_html(None).count('class="rf-sum-i"') == 6   # trước khi chạy cũng đủ 6 ô


@need_a02
@need_22
def test_trinh_bay_a02_den_do_va_bam_me_hien_o_buoc_5():
    app = _app()
    r = app.story_compute('a02')
    assert r['out']['confidence']['level'] == 'thap'
    assert 'THẤP' in r['texts'][5][0] and 'trùng nhịp mẹ' in r['texts'][5][0]
    assert 'THẤP' in r['summary'] and 'fsqi/' not in r['cards'] and 'checkpoint' not in r['cards']
    # [B] đèn đỏ -> nhịp tim ở thanh tóm tắt bị gạch và có cảnh báo
    assert '<s>' in r['summary'] and 'không dùng số này' in r['summary']
    # nhịp tim máy báo lệch đáp án >= 10 nhịp/phút -> nói rõ ở bước 5
    assert 'theo đáp án ≈' in r['texts'][5][0]


@need_a02
@need_22
def test_trinh_bay_a02_buoc_4_bao_trung_thuc_chon_sai_day():
    """[F] a02: dây 1 đạt 75,88 nhưng mọi quy tắc chọn mù đều chọn dây 2 -> hộp vàng phải nói thẳng, số khớp đĩa."""
    app = _app()
    r = app.story_compute('a02')
    out = r['out']
    with open(os.path.join(ROOT, 'analysis', 'chonkenh_results.json'), encoding='utf-8') as f:
        d = json.load(f)
    ref = d['F1_tung_ban_ghi']['cinc']['a02']
    chon = d['chon_kenh_theo_quy_tac']['cinc']['a02']
    rules = app.story_rules(out)
    assert rules['k_best'] == 1 and rules['f1_best'] == app._vn(ref['oracle'])
    assert out['lead'] == chon['peakprob'] + 1                    # JSON đánh số từ 0, demo từ 1
    assert 'rf-box-warn' in r['rules_md']
    assert f'Dây 1 đạt F1 {app._vn(ref["lead0"])}' in r['rules_md'] and f'chọn dây {out["lead"]}' in r['rules_md']
    # 7 cách chọn MỘT dây không nhìn nhãn: 6 chọn dây 2, 'learned' chọn dây 3, không cách nào chọn dây 1
    bay = ('psd', 'gate', 'gate4', 'rrcv', 'peakprob', 'rrplaus', 'learned')
    so_quy_tac = sum(1 for k in bay if chon[k] + 1 == out['lead'])
    assert so_quy_tac == 6 and not any(chon[k] == 0 for k in bay)
    assert f'6/7 cách chọn dây không nhìn đáp án' in r['rules_md'] and 'Không cách nào chọn dây 1' in r['rules_md']
    assert 'Cả 6' not in r['rules_md']                            # câu cũ nói quá (bỏ sót bộ chọn học)
    for cam in CHUOI_CAM:
        assert cam not in r['rules_md'], cam
    # bước 1 và 3 không được đưa nhịp tim máy đếm (130) ra như sự thật khi bước 5 bảo không dùng
    t1, t3 = r['texts'][1][0], r['texts'][3][0]
    assert 'Theo đáp án' in t1 and 'không tin được' in t1 and 'bé đập nhanh hơn' not in t1
    assert 'bám nhầm tim mẹ' in t3


@need_a09
@need_22
def test_trinh_bay_a09_khong_hien_hop_chon_sai_day():
    app = _app()
    r = app.story_compute('a09')
    assert 'rf-box-warn' not in r['rules_md']                    # dây được chọn chính là dây tốt nhất


def test_trinh_bay_the_a02_a27_noi_dung_khop_dia():
    """[A][G] thẻ a02 nói rõ 'trông bình thường nhưng sai' kèm nhịp đáp án; thẻ a27 nêu khoảng F1 bốn dây và số đoạn bị từ chối."""
    app = _app()
    n = app.STORY_NUM
    if 'fhr' not in n.get('a02', {}):
        pytest.skip('chưa có demo/results/demo_check_showcase.json')
    a02 = app.story_card_spec('a02')
    assert 'số đẹp' not in a02['so_giai'] and 'sai' in a02['so_giai']
    assert f'Máy báo nhịp tim {n["a02"]["fhr"]:.0f}' in a02['cho_thay'] and f'đáp án ≈ {n["a02"]["fhr_dap_an"]:.0f}' in a02['cho_thay']
    a27 = app.story_card_spec('a27')
    assert f'{n["a27"]["n_red"]}/{n["a27"]["n_seg"]} đoạn' in a27['cho_thay']
    assert app._vn(n['a27']['f1_max_day']) in a27['cho_thay'] and 'ĐỎ' in a27['so']
    # thẻ 'Tệp của bạn' có cùng cấu trúc (cùng chiều cao) với 4 thẻ còn lại
    for cls in ('rf-sc-name', 'rf-sc-code', 'rf-sc-ds', 'rf-sc-show', 'rf-sc-num', 'rf-sc-numk', 'rf-sc-go'):
        assert cls in app.STORY_UPLOAD_CARD and cls in app.story_card_html('r01')
    assert 'rf-sc-small' not in app.STORY_UPLOAD_CARD


def test_trinh_bay_chi_tiet_ky_thuat_dong_san_va_an_chan_trang():
    """[C] bảng kỹ thuật nằm trong Accordion đóng; [E] chân trang Gradio ẩn; [S2] ghi rõ đèn dùng cổng 5 ca."""
    app = _app()
    import gradio as gr
    acc = [b for b in app.demo.blocks.values() if isinstance(b, gr.Accordion) and str(b.label).startswith('Chi tiết kỹ thuật')]
    assert len(acc) == 1 and acc[0].open is False
    assert 'footer{display:none' in app.CSS.replace(' ', '')
    # vòng 9 ẩn nút '...' của thanh tab -> ở 1366 px hai tab cuối không mở được. Không được ẩn lại.
    assert not re.search(r'aria-haspopup\]\s*\{\s*display\s*:\s*none', app.CSS)
    assert not re.search(r'overflow-menu[^{]*\{[^}]*display\s*:\s*none', app.CSS)
    kw = app.launch_kwargs()
    import inspect
    if 'footer_links' in inspect.signature(gr.Blocks.launch).parameters:
        assert kw['footer_links'] == []
    assert '5 sản phụ' in app.STORY_GATE_NOTE and '22 sản phụ' in app.STORY_GATE_NOTE
    assert any(app.STORY_GATE_NOTE in t for t in _story_texts_on_screen(app))


@need_a09
@need_22
def test_trinh_bay_so_kieu_viet_tren_hinh_va_bang():
    """[D] chế độ trình bày: tiêu đề hình bước 4 và bảng kỹ thuật dùng dấu phẩy thập phân, không 'e+', không 'bpm'."""
    app = _app()
    import re as _re
    r = app.story_compute('a09')
    titles4 = [a.text for a in r['figs'][4].layout.annotations if a.text and a.text.startswith('Dây')]
    assert len(titles4) == r['out']['n_leads']
    for t in titles4:
        assert not _re.search(r'\d\.\d', t) and 'e+' not in t and 'e-' not in t, t
    for t in (a.text for a in r['figs'][5].layout.annotations if a.text):
        assert 'bpm' not in t and not _re.search(r'\d\.\d', t), t
    assert r['figs'][5].layout.separators == ', ' and r['figs'][4].layout.separators == ', '
    for txt in (r['cards'], r['compare']):
        # dấu chấm chỉ được là dấu ngăn nghìn (1.005 ms), không được là dấu thập phân (0.963)
        assert not _re.search(r'\d\.\d{1,2}(?!\d)', _re.sub(r'<[^>]+>', '', txt)), txt[:200]



# ------------------------------------------------------------------ vòng 10c lượt 2: phát hiện của kiểm demo độc lập
@need_r01
@need_22
def test_trinh_bay_buoc_5_co_dai_binh_thuong_110_160():
    """plotly 7 bỏ qua add_hrect gọi trước khi ô có đường -> dải 110–160 từng biến mất mà hộp chữ vẫn nhắc tới."""
    app = _app()
    fig = app.story_compute('r01')['figs'][5]
    assert any(getattr(sh, 'y0', None) == 110 and getattr(sh, 'y1', None) == 160 for sh in fig.layout.shapes)
    assert any(a.text and 'vùng bình thường 110–160' in a.text for a in fig.layout.annotations)


@need_r01
@need_22
def test_trinh_bay_r01_diem_ngang_nhau_in_4_chu_so():
    """r01: bốn dây cùng 0,998 khi làm tròn 3 chữ số -> tiêu đề in 4 chữ số và hộp số nói rõ gần như ngang nhau."""
    app = _app()
    r = app.story_compute('r01')
    titles = [a.text for a in r['figs'][4].layout.annotations if a.text and a.text.startswith('Dây')]
    vals = [t.split('điểm tin của mạng ')[1].split(' ')[0] for t in titles]
    assert len(set(vals)) == len(vals) and all(len(v.split(',')[1]) == 4 for v in vals), vals
    assert 'gần như ngang điểm' in r['texts'][4][0]


def test_trinh_bay_the_co_ten_ca_va_ma_ban_ghi():
    app = _app()
    for n, ten in (('r01', 'Ca dễ'), ('a09', 'Chọn dây quyết định'), ('a02', 'Máy bám nhầm tim mẹ'), ('a27', 'Bốn dây đều kém')):
        h = app.story_card_html(n)
        assert f'<div class="rf-sc-name">{ten}</div>' in h and f'bản ghi {n}' in h
    assert 'chưa từng thấy sản phụ này' in app.story_card_spec('r01')['du_lieu']
    for cam in CHUOI_CAM:
        assert cam not in app.story_loading_html('a02') and cam not in app.story_loading_html('r01', lan_dau=True)


def test_trinh_bay_chu_thich_buoc_khong_noi_qua():
    """Bước 1-2 không được khẳng định tim bé luôn nhỏ/không thấy (r01 thấy rõ); bước 5 phải giải thích xanh/vàng/đỏ."""
    app = _app()
    cap = app.STORY_CAPTION
    assert 'nhỏ hơn nhiều lần' not in cap[0] and 'đó là tim bé' not in cap[1]
    assert 'vàng' in cap[4] and '30 %' in cap[4] and 'bám nhịp mẹ' in cap[4]


def test_trinh_bay_thanh_tom_tat_dinh_day_va_the_xuong_hang():
    app = _app()
    import gradio as gr
    css = app.CSS.replace(' ', '')
    assert '.rf-story-col.rf-sum-wrap{position:sticky!important;bottom:0' in css
    assert '.rf-sc-row{flex-wrap:wrap!important' in css
    wraps = [b for b in app.demo.blocks.values() if 'rf-sum-wrap' in (getattr(b, 'elem_classes', None) or [])]
    assert len(wraps) == 1
    # sau Tiếp / Quay lại / bấm thẻ: trang tự cuộn tới thanh 5 bước
    assert '.rf-pgbar' in app.JS_CUON_TOI_BUOC and 'scrollIntoView' in app.JS_CUON_TOI_TAI_TEP


def test_che_do_chuyen_gia_tab_con_khong_trung_ten_tab_ngoai():
    app = _app()
    import gradio as gr
    labels = [str(b.label) for b in app.demo.blocks.values() if isinstance(b, gr.Tab)]
    assert len(labels) == len(set(labels)), [l for l in labels if labels.count(l) > 1]


def test_che_do_chuyen_gia_so_kieu_viet_trong_bang_tong_hop():
    app = _app()
    assert not re.search(r'\d\.\d', app.SUMMARY_MD)
    assert '0,721' in app.SUMMARY_MD and '11/22' in app.SUMMARY_MD and 'không độc lập với mạng' in app.SUMMARY_MD


def test_tai_len_phat_hien_tep_nhan_bo_nham_o_tin_hieu(tmp_path):
    app = _app()
    import gradio as gr
    sig = tmp_path / 'tin_hieu.csv'; lab = tmp_path / 'nhan.csv'
    sig.write_text('k1,k2,k3,k4\n' + '\n'.join('0.1,0.2,0.3,0.4' for _ in range(20)), encoding='utf-8')
    lab.write_text('\n'.join(str(i * 400) for i in range(1, 20)), encoding='utf-8')
    # lỗi không ném ra giao diện: hiện ở dòng trạng thái (phần tử cuối), 7 ô kết quả rỗng
    o = app.run_upload([str(sig), str(lab)], 1000, app.LEAD_CHOICES[0], app.CONF_CHOICES[0], None)
    assert len(o) == 8 and o[0] == '' and o[1] is None
    assert o[-1].startswith('**Không phân tích được tệp.**') and 'NHÃN' in o[-1] and 'nhan.csv' in o[-1]
    rac = tmp_path / 'rac.txt'
    rac.write_text('1 2 3 4 5 6 7 8\n1 2 3\nabc def\n', encoding='utf-8')
    o = app.run_upload([str(rac)], 1000, app.LEAD_CHOICES[0], app.CONF_CHOICES[0], None)
    assert 'thành bảng số' in o[-1] and 'Some errors were detected' not in o[-1] and 'Chi tiết kỹ thuật' not in o[-1]
    o = app.upload_clear()
    assert len(o) == 8 and 'kết quả cũ đã được xoá' in o[-1]


def test_core_goi_y_tai_cinc_dung_lenh_ghi_vao_pcdb():
    """download_data.py --only cinc2013 ghi vào model/data/cinc2013, demo không đọc thư mục đó."""
    for k in ('cinc_sach', 'cinc_nhiem'):
        thu_muc, lenh = core.DATASET_DIR_HINT[k]
        assert thu_muc == 'benchmark_dpss/pcdb' and 'download_more.py --only cinc75' in lenh



# ------------------------------------------------------------------ vòng 10d: phát hiện của kiểm demo độc lập lần hai
def _fns(app):
    f = app.demo.fns
    return list(f.values()) if isinstance(f, dict) else list(f)


def test_che_do_chuyen_gia_nut_phan_tich_gan_dung_ham_run():
    """Vòng lặp nút Tiếp/Quay lại từng đặt tên biến 'btn', ghi đè nút "Phân tích": run() bị gắn vào "◀ Quay lại"."""
    app = _app()
    import gradio as gr
    run_fns = [f for f in _fns(app) if getattr(f.fn, '__name__', '') == 'run']
    assert len(run_fns) == 1
    dich = [app.demo.blocks[t[0]] for t in run_fns[0].targets]
    assert dich and all(isinstance(b, gr.Button) and b.value == 'Phân tích' for b in dich), [getattr(b, 'value', b) for b in dich]
    back = [b for b in app.demo.blocks.values() if isinstance(b, gr.Button) and b.value == '◀ Quay lại']
    assert len(back) == 1
    co_ham = [f for f in _fns(app) if f.fn is not None and any(t[0] == back[0]._id for t in f.targets)]
    assert len(co_ham) == 1                                        # chỉ story_step


def test_trinh_bay_story_run_bo_qua_luot_cu_va_bao_loi_o_trang_thai():
    app = _app()
    app._YEU_CAU['phien_kiem_thu'] = 'a02'                       # người dùng đã bấm a02 sau r01
    o = app.story_run('r01', 'phien_kiem_thu')
    assert len(o) == app.STORY_N_OUTS and all(isinstance(x, dict) and x.get('__type__') == 'update' for x in o)
    o = app.story_run('khong_co_ban_nay')                          # lỗi: không ném, báo ở dòng trạng thái
    assert len(o) == app.STORY_N_OUTS and 'Không phân tích được bản ghi khong_co_ban_nay' in o[-1]
    assert all(isinstance(x, dict) for x in o[:-1])               # giữ nguyên hình của bản ghi trước
    for cam in CHUOI_CAM:
        assert cam not in o[-1]


def test_trinh_bay_chu_de_va_chu_thich_khong_noi_qua():
    app = _app()
    assert 'một</em> điện cực' not in app.STORY_TITLE_HTML and 'kênh' in app.STORY_TITLE_HTML
    assert 'không phải lần nào cũng thấy' in app.STORY_TITLE_HTML
    assert 'Vạch đỏ' not in app.STORY_CAPTION[2] and 'tím đậm' in app.STORY_CAPTION[2]
    assert 'xanh là tin được' not in app.STORY_CAPTION[4] and 'Xanh không bảo đảm là đúng' in app.STORY_CAPTION[4]
    if app._DX:
        n, xanh_sai, f1_min = app._DX
        p = os.path.join(ROOT, 'demo', 'results', 'demo_check_2modes.json')
        with open(p, encoding='utf-8') as f:
            s = json.load(f)['summary_by_mode']['hoc']
        assert n == s['n_records'] and xanh_sai == len(s['green_but_F1_below_90'])
        assert f'{f1_min:.2f}'.replace('.', ',') in app.STORY_CAPTION[4]
    assert 'độ đúng' not in app.story_summary_html(None)
    assert '−0,68' not in app.UP_WARN_DOMAIN and '−0,67' in app.UP_WARN_DOMAIN and 'đầu tiên' not in app.UP_WARN_DOMAIN
    assert 'khác thiết bị, khác dân số' not in app.DS_FORMAT_MD['cinc_sach'] and '80,72' in app.DS_FORMAT_MD['cinc_sach']


@need_r01
@need_a09
@need_22
def test_trinh_bay_buoc_1_noi_theo_bien_do_that_cua_ban_ghi():
    """r01 dây 4: gai bé to ngang gai mẹ -> không được nói 'gai bé nhỏ hơn nhiều'; a09 thì ngược lại."""
    app = _app()
    r01 = app.story_compute('r01')
    a09 = app.story_compute('a09')
    assert app.story_ti_le_bien_do(r01['out']) >= 0.5 and 'to ngang gai của mẹ' in r01['texts'][1][1]
    assert app.story_ti_le_bien_do(a09['out']) < 0.5 and 'nhỏ hơn nhiều' in a09['texts'][1][1]


@need_a09
@need_22
def test_trinh_bay_ban_ghi_khong_co_dap_an_khong_noi_sai():
    app = _app()
    rec = dict(core.load_sample('a09', RECS)); rec['labels'] = None
    out = core.analyze_record(rec, lead='peakprob', confidence_mode='hoc')
    rules = app.story_rules_md(out)
    assert 'chưa biết cách nào đúng' in rules and 'kết quả gần như nhau' not in rules and 'rf-box-warn' not in rules
    T = app.story_texts(out)
    assert 'đáp án' not in T[5][1] and 'không có đáp án' in T[1][1] and app.story_ti_le_bien_do(out) is None


def test_trinh_bay_thanh_tom_tat_dinh_that_va_cuon_co_dieu_kien():
    app = _app()
    css = app.CSS.replace(' ', '')
    assert '.gradio-container{overflow:visible!important;overflow-x:clip!important}' in css
    js = app.JS_CUON_TOI_BUOC
    assert 'innerHeight*0.5' in js.replace(' ', '') and 'checked' in js and '__rfY' in js and '__rfY' in app.JS_GHI_VI_TRI


def test_trinh_bay_luot_dang_tinh_bi_bam_the_khac_thi_khong_ve_de(monkeypatch):
    """Người dùng bấm thẻ khác TRONG LÚC lượt trước đang tính: lượt trước tính xong cũng không được vẽ đè."""
    app = _app()

    def tinh_gia(name):
        app._YEU_CAU['phien_dang_tinh'] = 'a09'
        return {}
    monkeypatch.setattr(app, 'story_compute', tinh_gia)
    app._YEU_CAU['phien_dang_tinh'] = 'r01'
    o = app.story_run('r01', 'phien_dang_tinh')
    assert len(o) == app.STORY_N_OUTS and all(isinstance(x, dict) and x.get('__type__') == 'update' for x in o)
    assert '5–10 giây' in app.story_card_html('r01') and 'khi cần, trang tự cuộn' in ''.join(_story_texts_on_screen(app))
