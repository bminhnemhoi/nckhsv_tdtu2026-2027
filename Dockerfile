# RelyFetal REST API -- CPU only.
#   docker build -t relyfetal-api .
#   docker run --rm -p 8000:8000 relyfetal-api
#   curl http://127.0.0.1:8000/health
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    RELYFETAL_TORCH_THREADS=2 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# torch CPU wheel first (largest layer, changes least), then the rest.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir \
        "numpy>=1.24" "scipy>=1.10" "mne>=1.5" "wfdb>=4.1" ripser \
        fastapi uvicorn python-multipart

# Only what the API needs (see .dockerignore for what is excluded from the context).
COPY model/fqrs_model.py           model/fqrs_model.py
COPY model/checkpoints/            model/checkpoints/
COPY demo/core.py                  demo/core.py
COPY fsqi/fsqi.py                  fsqi/fsqi.py
COPY fsqi/README.md                fsqi/README.md
COPY benchmark_dpss/_paths.py      benchmark_dpss/_paths.py
COPY api/                          api/
COPY CITATION.cff LICENSE          ./

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
