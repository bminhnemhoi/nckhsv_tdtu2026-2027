# RelyFetal REST API

FastAPI wrapper around `demo/core.py` (which itself only calls `model/fqrs_model.py`).
One abdominal ECG record in, fetal beat positions + fetal heart rate + a confidence light out.

> Research prototype. Not a medical device. Not for diagnostic use.

## Run

```bash
pip install -r requirements.txt            # adds fastapi, uvicorn, httpx, python-multipart
uvicorn api.main:app --host 0.0.0.0 --port 8000
# interactive docs: http://127.0.0.1:8000/docs
```

Docker (CPU only, `python:3.12-slim`, torch from the CPU wheel index):

```bash
docker build -t relyfetal-api .
docker run --rm -p 8000:8000 relyfetal-api
# or
docker compose up --build
```

Environment: `RELYFETAL_TORCH_THREADS` (default 2) sets `torch.set_num_threads`;
`OPENBLAS_NUM_THREADS` / `OMP_NUM_THREADS` are pinned to 1 in the image.

**Build status on the development machine (2026-09-11):** the image has NOT been built here yet
("chua build duoc tren may nay"). `docker --version` reports 29.5.3 but the Docker Desktop engine was not
running (`docker info`: `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`),
and it was deliberately not started because two training jobs were sharing the ~4 GB of free RAM. What WAS
verified, by `python api/check_server.py` (starts the exact `CMD` of the Dockerfile outside Docker and calls it
with `curl`; results in `api/logs/server_check.json`, server log in `api/logs/uvicorn_check.log`):

| Call | Result |
|---|---|
| `GET /health` | `200` after 6.51 s start-up, `status: ok`, torch 2.13.0+cpu |
| `GET /model` | `200` in 43 ms, `n_params` = 113481 |
| `POST /analyze` (r01 lead 4, 10 s, NPY) | `200` in 1682 ms wall-clock; `n_beats` = 22, `fhr_mean` = 128.6, `confidence.level` = `cao`, `latency_ms` = 68.2 |
| `POST /analyze` with `.wav` | `415` JSON `detail` |

Every `COPY` source in the Dockerfile exists (checked 2026-09-11). To build once the engine is up:
`docker build -t relyfetal .` then `curl http://127.0.0.1:8000/health`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | `200 {"status":"ok", ...}` when the production checkpoint is present; `503 "degraded"` otherwise |
| `GET` | `/model` | parameter count, receptive field, checkpoint, decision threshold, config, LORO expected performance; `?checkpoint=fold_r01` for a fold model |
| `POST` | `/analyze` | analyse one record (multipart form) |
| `GET` | `/docs` | OpenAPI UI |

### `POST /analyze` — request (multipart/form-data)

| Field | Type | Default | Meaning |
|---|---|---|---|
| `file` | file | required | `.edf`, `.csv`, `.txt` (one column per channel, header row allowed) or `.npy` (`K×N` or `N×K`, or 1-D) |
| `lead` | text | `auto` | `auto` = label-blind PSD rule (Power-MF band 1.8–3.0 Hz) over all channels; or a channel number `1..K` |
| `fs` | number | `1000` | sampling rate of CSV/TXT/NPY in Hz (EDF carries its own); resampled to 1000 Hz internally |
| `labels` | file | — | optional fetal-QRS reference: one sample index per line, at the input `fs`; enables `metrics` |
| `checkpoint` | text | `auto` | `auto` (a file named `r01`…`r10` gets the fold checkpoint that never saw it, anything else gets `production`), `production`, `fold_r01` … |

WFDB pairs (`.hea` + `.dat`) are not accepted through the single-file upload — export to CSV/NPY, or use `model/predict.py`.

```bash
curl -F "file=@signal.npy" -F "lead=auto" -F "fs=1000" http://127.0.0.1:8000/analyze
curl -F "file=@r01.edf"    -F "lead=4"                  http://127.0.0.1:8000/analyze
```

```python
import numpy as np, io, requests
x = np.load('abdomen_lead.npy')                       # 1-D, 1000 Hz
buf = io.BytesIO(); np.save(buf, x)
r = requests.post('http://127.0.0.1:8000/analyze',
                  files={'file': ('lead.npy', buf.getvalue())}, data={'lead': '1', 'fs': '1000'})
print(r.status_code, r.json()['n_beats'], r.json()['fhr_mean'], r.json()['confidence']['level'])
```

### `POST /analyze` — response (`200`)

```jsonc
{
  "record": "r01", "source": "NPY", "duration_s": 10.0, "fs_in": 1000.0, "n_channels": 1,
  "lead": 1, "lead_name": "ch1", "lead_mode": "thủ công", "lead_scores": null,
  "checkpoint": "fetalqrs_tcn_fold_r01.pt", "checkpoint_note": "fold r01 (...)", "threshold": 0.45,
  "n_beats": 21, "fhr_mean": 127.9,
  "fhr_series": {"t_s": [2.0, 6.0, ...], "bpm": [128.2, 127.7, ...], "window_s": 4.0},   // null where < 2 beats
  "beats_ms": [312, 780, ...],                     // fetal R-peak positions, ms from record start (1000 Hz samples)
  "n_maternal_beats": 14,
  "confidence": {
    "level": "cao" | "trung_binh" | "thap", "label": "CAO (xanh)", "score": 0.93,
    "reasons": ["Năng lượng 10–60 Hz trên phần dư: 62% ...", "Khoảng RR: CV = 0.03 (đều)", ...],
    "components": {"band_ratio": ..., "rr_cv": ..., "frac_conf_peaks": ..., "fhr_mean": ..., "maternal_lock": ...}
  },
  "latency_ms": 41.2,               // front-end of the chosen lead + model + peak picking (no file I/O)
  "latency_frontend_ms": 9.8, "latency_model_ms": 31.4, "latency_all_leads_ms": 41.2, "latency_total_ms": 55.0,
  "metrics": {"TP": 21, "FP": 0, "FN": 0, "Se": 100.0, "PPV": 100.0, "F1": 100.0, "jitter_ms": 2.1, "tolerance_ms": 50},  // only with labels
  "n_labels": 21,
  "disclaimer": "..."
}
```

The confidence rule is the hand-set gate documented in `demo/README.md` (band-energy ratio, RR regularity,
fraction of peaks with probability > 0.9, fHR in 100–200 bpm, and a maternal-lock veto at 60 %). It is a
placeholder for the learned classical-SQI classifier from `fsqi/`.

### Errors

Never a raw traceback. Input problems return `4xx` with a `detail` message:

| Code | When |
|---|---|
| `400` | empty file, unreadable/corrupt file, signal shorter than 4 s, NaN/inf in the signal, filter failure |
| `404` | unknown `checkpoint` |
| `413` | upload larger than 64 MB |
| `415` | unsupported extension |
| `422` | bad `lead` / `fs`, channel out of range, labels beyond record length, missing `file` field |
| `500` | anything unexpected, as `{"detail": "..."}` |

## Tests

```bash
pytest tests/test_api.py -v        # TestClient, no network; data-dependent cases skip without ADFECGDB
```
