# -*- coding: utf-8 -*-
"""
RelyFetal REST API -- dò QRS thai nhi từ điện tim ổ bụng ĐƠN KÊNH (FastAPI).

Bao bọc demo/core.py (không sửa model/fqrs_model.py). Ba điểm cuối:
    GET  /health   -> trạng thái dịch vụ, checkpoint có sẵn hay không
    GET  /model    -> tham số mô hình, checkpoint, ngưỡng, cấu hình, phiên bản
    POST /analyze  -> multipart: file (EDF / CSV / TXT / NPY), lead ('auto' | 1..K), fs (Hz),
                      labels (tuỳ chọn, file văn bản: mỗi dòng một chỉ số mẫu ở fs đầu vào),
                      checkpoint ('auto' | 'production' | 'fold_r01' ...)
                   -> JSON: n_beats, fhr_mean, fhr_series, beats_ms, confidence{level,score,reasons},
                      latency_ms, metrics (nếu có nhãn)

Mọi lỗi đầu vào trả về 4xx kèm thông điệp trong "detail"; lỗi bất ngờ trả về 500 dạng JSON,
không bao giờ trả về ngoại lệ thô.

Chạy:  uvicorn api.main:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations
import os, sys
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, ValueError):
    pass

import re, time, shutil, tempfile
from typing import Optional

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'demo'))
import core  # noqa: E402  -- demo/core.py: load_record, analyze_record, load_model, checkpoint_for

torch.set_num_threads(max(1, int(os.environ.get('RELYFETAL_TORCH_THREADS', '2'))))

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402

M, CFG = core.M, core.CFG
SUPPORTED_EXT = ('.edf', '.csv', '.txt', '.npy')
MAX_UPLOAD_BYTES = 64 * 1024 * 1024        # 64 MB: r01.edf (5 kênh x 300 s x 1000 Hz) là 3 MB
MIN_DURATION_S = float(CFG['seg']) / CFG['fs']   # 4 s = một cửa sổ của mô hình
FS_RANGE = (50.0, 20000.0)
_START = time.time()


def _version():
    """phiên bản lấy từ CITATION.cff (không ghi cứng)"""
    try:
        with open(os.path.join(ROOT, 'CITATION.cff'), encoding='utf-8') as f:
            for line in f:
                if line.startswith('version:'):
                    return line.split(':', 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return 'unknown'


VERSION = _version()

app = FastAPI(
    title='RelyFetal API',
    version=VERSION,
    description='Dò QRS thai nhi từ điện tim ổ bụng đơn kênh (FetalQRS-TCN) kèm đèn tin cậy. '
                'Bản mẫu nghiên cứu -- không phải thiết bị y tế, không dùng cho chẩn đoán.',
)


# --------------------------------------------------------------------------- tiện ích JSON
def _jf(v):
    """float JSON-an toàn: NaN/inf -> None (JSONResponse dùng allow_nan=False)."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v if np.isfinite(v) else None


def _jlist(a):
    return [_jf(v) for v in np.asarray(a, float).ravel()]


def _jint_list(a):
    return [int(v) for v in np.asarray(a).ravel()]


def _cfg_json(cfg):
    return {k: (list(v) if isinstance(v, tuple) else v) for k, v in cfg.items()}


def _safe_name(filename: str) -> str:
    base = os.path.basename((filename or '').replace('\\', '/')).strip()
    base = re.sub(r'[^A-Za-z0-9._\-]+', '_', base)
    return base or 'upload'


# --------------------------------------------------------------------------- xử lý lỗi
@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    return JSONResponse(status_code=500,
                        content={'detail': f'Lỗi nội bộ khi xử lý yêu cầu: {type(exc).__name__}: {exc}'})


# --------------------------------------------------------------------------- GET /
@app.get('/')
def index():
    return {'service': 'RelyFetal API', 'version': VERSION,
            'endpoints': {'GET /health': 'trạng thái', 'GET /model': 'thông tin mô hình',
                          'POST /analyze': 'phân tích một bản ghi (multipart)', 'GET /docs': 'OpenAPI'},
            'disclaimer': 'Bản mẫu nghiên cứu. Không phải thiết bị y tế.'}


# --------------------------------------------------------------------------- GET /health
@app.get('/health')
def health():
    ckpt = core._ckpt('fetalqrs_tcn_production.pt')
    present = os.path.isfile(ckpt)
    body = dict(status='ok' if present else 'degraded', version=VERSION,
                checkpoint='fetalqrs_tcn_production.pt', checkpoint_present=present,
                model_loaded=os.path.abspath(ckpt) in core._MODELS,
                torch=torch.__version__, torch_threads=torch.get_num_threads(),
                uptime_s=round(time.time() - _START, 1))
    return JSONResponse(status_code=200 if present else 503, content=body)


# --------------------------------------------------------------------------- GET /model
@app.get('/model')
def model_info(checkpoint: str = 'production'):
    try:
        net, thr, meta = core.load_model(checkpoint)
    except FileNotFoundError as e:
        raise HTTPException(404, f'Không tìm thấy checkpoint "{checkpoint}": {e}')
    except (KeyError, RuntimeError, ValueError) as e:
        raise HTTPException(422, f'Không nạp được checkpoint "{checkpoint}": {e}')
    rf = int(net.receptive_field)
    out = dict(
        name='FetalQRS-TCN', version=VERSION,
        checkpoint=meta['name'], checkpoint_path=meta['path'], threshold=_jf(thr),
        n_params=int(M.n_params(net)), receptive_field_samples=rf,
        receptive_field_ms=rf * 1000 // CFG['fs'],
        input=dict(channels=2, samples=CFG['seg'], fs=CFG['fs'], seconds=CFG['seg'] / CFG['fs'],
                   description='[phần dư sau khử mẹ, tín hiệu lọc 10-60 Hz] chuẩn hoá robust'),
        output='một logit cho từng mẫu (bản đồ nhiệt Gauss), chọn đỉnh với ngưỡng + trơ 250 ms',
        config=_cfg_json(dict(meta.get('config', CFG))),
        trained_on=meta.get('trained_on') or meta.get('train_records'),
        val_record=meta.get('val_record'), test_record=meta.get('test_record'),
        seed=meta.get('seed'), epochs=meta.get('epochs'), note=meta.get('note'),
        expected_performance=meta.get('expected_performance'),
        macro_F1_heldout=_jf(meta['macro_F1']) if 'macro_F1' in meta else None,
        available_checkpoints=sorted(f for f in os.listdir(os.path.dirname(meta['path'])) if f.endswith('.pt')),
        torch=torch.__version__,
    )
    # expected_performance là dict số thuần (ghi bởi train_final.py) -> đảm bảo JSON-an toàn
    if isinstance(out['expected_performance'], dict):
        out['expected_performance'] = {k: (_jf(v) if isinstance(v, (int, float, np.floating, np.integer)) else v)
                                       for k, v in out['expected_performance'].items()}
    return out


# --------------------------------------------------------------------------- POST /analyze
def _parse_lead(lead: str):
    s = (lead or 'auto').strip().lower()
    if s in ('', 'auto', 'psd'):
        return 'auto'
    if not re.fullmatch(r'\d+', s):
        raise HTTPException(422, f'lead phải là "auto" hoặc số kênh 1..K, nhận được: {lead!r}')
    k = int(s)
    if k < 1:
        raise HTTPException(422, f'lead phải >= 1, nhận được: {k}')
    return k


def _resolve_checkpoint(name: str, record_name: str):
    s = (name or 'auto').strip()
    if s.lower() in ('', 'auto'):
        return None                      # core.analyze_record -> checkpoint_for(record_name)
    if os.sep in s or '/' in s or '..' in s:
        raise HTTPException(422, 'checkpoint chỉ nhận tên ("production", "fold_r01"), không nhận đường dẫn')
    p = core._ckpt(s if s.endswith('.pt') else f'fetalqrs_tcn_{s}.pt')
    if not os.path.isfile(p):
        raise HTTPException(404, f'Không tìm thấy checkpoint "{s}"')
    return p


@app.post('/analyze')
async def analyze(file: UploadFile = File(..., description='EDF / CSV / TXT / NPY, một hoặc nhiều kênh'),
                  lead: str = Form('auto', description='"auto" (quy tắc PSD mù nhãn) hoặc số kênh 1..K'),
                  fs: float = Form(1000.0, description='tần số lấy mẫu (Hz) của CSV/TXT/NPY; EDF tự đọc'),
                  labels: Optional[UploadFile] = File(None, description='tuỳ chọn: nhãn QRS thai, mỗi dòng một chỉ số mẫu ở fs đầu vào'),
                  checkpoint: str = Form('auto', description='"auto" | "production" | "fold_r01" ...')):
    t_all = time.perf_counter()
    name = _safe_name(file.filename)
    base, ext = os.path.splitext(name); ext = ext.lower()
    if ext not in SUPPORTED_EXT:
        raise HTTPException(415, f'Định dạng không hỗ trợ: "{ext or "(không có phần mở rộng)"}". '
                                 f'Hỗ trợ: {", ".join(SUPPORTED_EXT)}. Với WFDB (.hea/.dat) hãy xuất sang CSV/NPY.')
    if not (FS_RANGE[0] <= float(fs) <= FS_RANGE[1]):
        raise HTTPException(422, f'fs phải nằm trong [{FS_RANGE[0]:.0f}, {FS_RANGE[1]:.0f}] Hz, nhận được {fs}')
    lead_req = _parse_lead(lead)

    data = await file.read()
    if not data:
        raise HTTPException(400, 'File rỗng (0 byte)')
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f'File quá lớn ({len(data) / 1e6:.1f} MB > {MAX_UPLOAD_BYTES / 1e6:.0f} MB)')
    lab_data = await labels.read() if labels is not None else None
    if labels is not None and not lab_data:
        raise HTTPException(400, 'File nhãn rỗng')

    tmp = tempfile.mkdtemp(prefix='relyfetal_api_')
    try:
        path = os.path.join(tmp, name)
        with open(path, 'wb') as f:
            f.write(data)
        lab_path = None
        if lab_data is not None:
            lab_path = os.path.join(tmp, 'labels.txt')
            with open(lab_path, 'wb') as f:
                f.write(lab_data)
        del data, lab_data

        try:
            rec = core.load_record(path, fs=float(fs), labels=lab_path, name=base)
        except HTTPException:
            raise
        except Exception as e:                       # mne/numpy/wfdb: file hỏng, không đọc được
            raise HTTPException(400, f'Không đọc được bản ghi "{name}": {type(e).__name__}: {e}')

        K, N = rec['signals'].shape
        if K < 1 or N < 2:
            raise HTTPException(400, 'Bản ghi không có mẫu nào')
        if rec['duration_s'] < MIN_DURATION_S:
            raise HTTPException(400, f'Tín hiệu quá ngắn: {rec["duration_s"]:.2f} s < {MIN_DURATION_S:.0f} s '
                                     f'(một cửa sổ của mô hình)')
        if not np.isfinite(rec['signals']).all():
            raise HTTPException(400, 'Tín hiệu chứa NaN/inf')
        if lead_req != 'auto' and lead_req > K:
            raise HTTPException(422, f'Kênh {lead_req} không tồn tại (bản ghi có {K} kênh)')
        if rec['labels'] is not None and len(rec['labels']) and int(np.max(rec['labels'])) >= N:
            raise HTTPException(422, f'Nhãn vượt quá độ dài bản ghi (max {int(np.max(rec["labels"]))} >= {N} mẫu @1000 Hz)')

        ckpt = _resolve_checkpoint(checkpoint, base)
        try:
            out = core.analyze_record(rec, lead=lead_req, model=ckpt)
        except HTTPException:
            raise
        except ValueError as e:                      # tín hiệu bệnh lý cho bộ lọc / chọn kênh
            raise HTTPException(400, f'Không phân tích được "{name}": {e}')
        finally:
            del rec
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    c = out['confidence']
    resp = dict(
        record=out['record'], source=out['source'], version=VERSION,
        duration_s=_jf(out['duration_s']), fs_in=_jf(out.get('fs_raw', core.FS_IN)),
        n_channels=int(K), lead=int(out['lead']), lead_name=out['lead_name'], lead_mode=out['lead_mode'],
        lead_scores=({str(int(k)): _jf(v) for k, v in out['lead_scores'].items()} if out.get('lead_scores') else None),
        checkpoint=out['checkpoint'], checkpoint_note=out['checkpoint_note'], threshold=_jf(out['threshold']),
        n_beats=int(out['n_beats']), fhr_mean=_jf(out['fhr_mean']),
        fhr_series=dict(t_s=_jlist(out['fhr_time_s']), bpm=_jlist(out['fhr_series']), window_s=4.0),
        beats_ms=_jint_list(out['fetal_peaks_1000']),
        n_maternal_beats=int(len(out['maternal_peaks'])),
        confidence=dict(level=c['level'], label=c['label'], score=_jf(c['score']), reasons=list(c['reasons']),
                        components={k: _jf(v) for k, v in c['components'].items()}),
        latency_ms=_jf(out['latency_ms']),
        latency_frontend_ms=_jf(out['latency_frontend_ms']), latency_model_ms=_jf(out['latency_model_ms']),
        latency_all_leads_ms=_jf(out['latency_all_leads_ms']),
        latency_total_ms=_jf((time.perf_counter() - t_all) * 1000.0),
        disclaimer='Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.',
    )
    if 'metrics' in out:
        resp['metrics'] = {k: _jf(v) for k, v in out['metrics'].items()}
        resp['metrics']['tolerance_ms'] = CFG['tolerance_ms']
        resp['n_labels'] = int(len(out['labels_1000']))
    return resp
