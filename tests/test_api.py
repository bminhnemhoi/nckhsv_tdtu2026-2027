# -*- coding: utf-8 -*-
"""
Kiểm thử REST API (api/main.py) bằng fastapi.testclient -- không cần mở cổng mạng.

  /health           -> 200, checkpoint có sẵn
  /model            -> 200, 113 481 tham số, trường tiếp nhận 379 mẫu
  /analyze NPY 10 s -> 200, n_beats trong 15-30 (từ r01 kênh 4; bỏ qua nếu chưa có ADFECGDB)
  file rỗng         -> 400 ; đuôi lạ -> 415 ; kênh không tồn tại -> 422 ; checkpoint lạ -> 404
"""
import os, sys, io, importlib.util
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import pytest

pytest.importorskip('fastapi')
pytest.importorskip('httpx')
try:
    import python_multipart  # noqa: F401   python-multipart >= 0.0.13 (Form/File)
except ImportError:
    pytest.importorskip('multipart')      # tên gói cũ của python-multipart
from fastapi.testclient import TestClient  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location('relyfetal_api_main', os.path.join(ROOT, 'api', 'main.py'))
api = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(api)
core = api.core

RECS = core.sample_records()
need_r01 = pytest.mark.skipif('r01' not in RECS, reason='chưa có ADFECGDB r01')


@pytest.fixture(scope='module')
def client():
    with TestClient(api.app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(scope='module')
def r01_10s():
    """(tín hiệu kênh bụng 4 của r01, 10 s đầu @1000 Hz ; nhãn QRS thai trong 10 s đó @1000 Hz)"""
    rec = core.load_record(RECS['r01']['path'], lead=4)
    x = rec['signals'][0][:10_000].astype(np.float64)
    lab = rec['labels'][rec['labels'] < 10_000]
    return x, lab


def _npy_bytes(x):
    buf = io.BytesIO(); np.save(buf, x); return buf.getvalue()


# ------------------------------------------------------------------ /health, /model
def test_health_ok(client):
    r = client.get('/health')
    assert r.status_code == 200, r.text
    j = r.json()
    assert j['status'] == 'ok' and j['checkpoint_present'] is True
    assert j['checkpoint'] == 'fetalqrs_tcn_production.pt'


def test_model_info_pins_quoted_numbers(client):
    r = client.get('/model')
    assert r.status_code == 200, r.text
    j = r.json()
    assert j['n_params'] == 113_481
    assert j['receptive_field_samples'] == 379 and j['receptive_field_ms'] == 1516
    assert j['checkpoint'] == 'fetalqrs_tcn_production.pt'
    assert 0.0 < j['threshold'] < 1.0
    assert j['config']['band'] == [10.0, 60.0] and j['config']['fs'] == 250
    assert 'No held-out score exists' in (j['note'] or '')
    assert 'fetalqrs_tcn_fold_r01.pt' in j['available_checkpoints']


def test_model_unknown_checkpoint_is_404(client):
    r = client.get('/model', params={'checkpoint': 'khong_ton_tai'})
    assert r.status_code == 404
    assert 'detail' in r.json()


# ------------------------------------------------------------------ /analyze: đường vui
@need_r01
def test_analyze_npy_10s_from_r01(client, r01_10s):
    x, _ = r01_10s
    r = client.post('/analyze',
                    files={'file': ('r01.npy', _npy_bytes(x), 'application/octet-stream')},
                    data={'lead': '1', 'fs': '1000'})
    assert r.status_code == 200, r.text
    j = r.json()
    # 10 s ở ~128 bpm (r01) -> ~21 nhịp
    assert 15 <= j['n_beats'] <= 30, j['n_beats']
    assert len(j['beats_ms']) == j['n_beats']
    assert all(0 <= b <= 10_000 for b in j['beats_ms'])
    assert j['fhr_mean'] is not None and 100 <= j['fhr_mean'] <= 200
    assert j['confidence']['level'] in ('cao', 'trung_binh', 'thap')
    assert isinstance(j['confidence']['reasons'], list) and j['confidence']['reasons']
    assert 0.0 <= j['confidence']['score'] <= 1.0
    assert j['latency_ms'] is not None and j['latency_ms'] > 0
    assert j['lead'] == 1 and j['n_channels'] == 1 and j['duration_s'] == pytest.approx(10.0)
    # tên r01 -> checkpoint CHƯA THẤY r01: fold 05 của mô hình 22 ca (r01 là bản kiểm thử của fold đó,
    # model/train_22.json) hoặc, nếu thiếu, fold r01 của mô hình 5 ca (demo/core.checkpoint_for)
    assert j['checkpoint'] in ('fetalqrs_tcn_22_fold_05.pt', 'fetalqrs_tcn_fold_r01.pt'), j['checkpoint']
    assert 'metrics' not in j                                  # không gửi nhãn


@need_r01
def test_analyze_with_labels_returns_metrics(client, r01_10s):
    x, lab = r01_10s
    lab_txt = '\n'.join(str(int(v)) for v in lab).encode()
    r = client.post('/analyze',
                    files={'file': ('r01.npy', _npy_bytes(x), 'application/octet-stream'),
                           'labels': ('lab.txt', lab_txt, 'text/plain')},
                    data={'lead': 'auto', 'fs': '1000'})
    assert r.status_code == 200, r.text
    j = r.json()
    m = j['metrics']
    assert m['TP'] + m['FN'] == len(lab) == j['n_labels']
    assert m['TP'] + m['FP'] == j['n_beats']
    assert m['F1'] > 90.0, m
    assert m['tolerance_ms'] == 50
    assert j['lead_mode'].startswith('auto')


@need_r01
def test_analyze_csv_at_500hz_is_resampled(client, r01_10s):
    x, _ = r01_10s
    csv = '\n'.join(f'{v:.6g}' for v in x[::2]).encode()           # 500 Hz, 10 s
    r = client.post('/analyze', files={'file': ('bung.csv', csv, 'text/csv')}, data={'lead': '1', 'fs': '500'})
    assert r.status_code == 200, r.text
    j = r.json()
    assert j['duration_s'] == pytest.approx(10.0) and 15 <= j['n_beats'] <= 30
    # tên lạ -> production (22 ca nếu có, 5 ca nếu thiếu)
    assert j['checkpoint'] in ('fetalqrs_tcn_22_production.pt', 'fetalqrs_tcn_production.pt'), j['checkpoint']


# ------------------------------------------------------------------ /analyze: lỗi đầu vào -> 4xx
def test_analyze_empty_file_is_400(client):
    r = client.post('/analyze', files={'file': ('rong.npy', b'', 'application/octet-stream')})
    assert 400 <= r.status_code < 500, r.text
    assert 'detail' in r.json()


def test_analyze_unsupported_extension_is_415(client):
    r = client.post('/analyze', files={'file': ('x.wav', b'abc', 'audio/wav')})
    assert r.status_code == 415


def test_analyze_bad_lead_is_422(client):
    x = np.random.default_rng(0).standard_normal(8000)
    r = client.post('/analyze', files={'file': ('a.npy', _npy_bytes(x), 'application/octet-stream')},
                    data={'lead': '9', 'fs': '1000'})
    assert r.status_code == 422
    r = client.post('/analyze', files={'file': ('a.npy', _npy_bytes(x), 'application/octet-stream')},
                    data={'lead': 'abc', 'fs': '1000'})
    assert r.status_code == 422


def test_analyze_too_short_signal_is_400(client):
    x = np.random.default_rng(0).standard_normal(1000)             # 1 s @1000 Hz
    r = client.post('/analyze', files={'file': ('ngan.npy', _npy_bytes(x), 'application/octet-stream')})
    assert r.status_code == 400
    assert 'ngắn' in r.json()['detail']


def test_analyze_corrupt_npy_is_400(client):
    r = client.post('/analyze', files={'file': ('hong.npy', b'khong phai npy', 'application/octet-stream')})
    assert r.status_code == 400


def test_analyze_unknown_checkpoint_is_404(client):
    x = np.random.default_rng(0).standard_normal(8000)
    r = client.post('/analyze', files={'file': ('a.npy', _npy_bytes(x), 'application/octet-stream')},
                    data={'checkpoint': 'fold_r99'})
    assert r.status_code == 404


def test_analyze_missing_file_is_422(client):
    r = client.post('/analyze', data={'lead': 'auto'})
    assert r.status_code == 422
