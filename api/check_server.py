# -*- coding: utf-8 -*-
"""
Kiểm tra dịch vụ thật ngoài Docker: khởi động đúng lệnh CMD của Dockerfile
(uvicorn api.main:app) trên một cổng tạm, rồi gọi bằng curl:
    GET  /health, GET /model, POST /analyze (NPY 10 s từ r01 kênh 4 nếu có ADFECGDB)
Ghi kết quả vào api/logs/server_check.json. Thoát mã 0 nếu cả ba trả về 200.

Chạy:  python api/check_server.py [--port 8017]
"""
import os, sys, json, time, subprocess, tempfile, argparse, shutil
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, ValueError):
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT, 'api', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)


def curl(args, timeout=60):
    """chạy curl thật, trả về (mã HTTP, thân JSON hoặc None, thời gian s)"""
    t0 = time.perf_counter()
    r = subprocess.run(['curl', '-sS', '-w', '\n%{http_code}'] + args,
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
    dt = time.perf_counter() - t0
    out = r.stdout.rstrip('\n')
    body, _, code = out.rpartition('\n')
    try:
        body = json.loads(body)
    except ValueError:
        body = body
    return int(code) if code.isdigit() else -1, body, dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8017)
    a = ap.parse_args()
    base = f'http://127.0.0.1:{a.port}'
    env = dict(os.environ, RELYFETAL_TORCH_THREADS='2', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               PYTHONIOENCODING='utf-8')
    cmd = [sys.executable, '-m', 'uvicorn', 'api.main:app', '--host', '127.0.0.1', '--port', str(a.port)]
    log_path = os.path.join(LOG_DIR, 'uvicorn_check.log')
    logf = open(log_path, 'w', encoding='utf-8')
    proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=logf, stderr=subprocess.STDOUT)
    result = dict(cmd=' '.join(cmd), port=a.port, started=time.strftime('%Y-%m-%d %H:%M:%S'))
    tmp = tempfile.mkdtemp(prefix='relyfetal_check_')
    try:
        # chờ dịch vụ lên (tối đa 90 s)
        t0 = time.perf_counter(); code = -1
        while time.perf_counter() - t0 < 90:
            code, body, _ = curl([f'{base}/health'], timeout=10)
            if code > 0:
                break
            if proc.poll() is not None:
                break
            time.sleep(1.0)
        result['startup_s'] = round(time.perf_counter() - t0, 2)
        result['health'] = dict(code=code, body=body)
        print(f'GET /health -> {code} sau {result["startup_s"]} s: {json.dumps(body, ensure_ascii=False)}')

        code, body, dt = curl([f'{base}/model'])
        result['model'] = dict(code=code, dt_s=round(dt, 3),
                               body={k: body.get(k) for k in ('n_params', 'receptive_field_samples', 'checkpoint',
                                                              'threshold', 'available_checkpoints')} if isinstance(body, dict) else body)
        print(f'GET /model -> {code} ({dt * 1000:.0f} ms): n_params={body.get("n_params") if isinstance(body, dict) else body}')

        # POST /analyze với NPY 10 s (r01 kênh 4) nếu có ADFECGDB; nếu không, dùng nhiễu trắng 8 s (vẫn phải 200)
        sys.path.insert(0, os.path.join(ROOT, 'demo'))
        import numpy as np
        import core
        recs = core.sample_records()
        npy = os.path.join(tmp, 'r01.npy')
        if 'r01' in recs:
            rec = core.load_record(recs['r01']['path'], lead=4)
            np.save(npy, rec['signals'][0][:10_000].astype(np.float64))
            result['analyze_input'] = 'r01 kênh 4, 10 s đầu @1000 Hz'
        else:
            np.save(npy, np.random.default_rng(0).standard_normal(8000))
            result['analyze_input'] = 'nhiễu trắng 8 s (không có ADFECGDB)'
        code, body, dt = curl(['-F', f'file=@{npy}', '-F', 'lead=1', '-F', 'fs=1000', f'{base}/analyze'])
        keep = ('record', 'n_beats', 'fhr_mean', 'checkpoint', 'latency_ms', 'latency_total_ms', 'duration_s')
        summ = {k: body.get(k) for k in keep} if isinstance(body, dict) else body
        if isinstance(body, dict) and 'confidence' in body:
            summ['confidence'] = {k: body['confidence'].get(k) for k in ('level', 'score')}
        result['analyze'] = dict(code=code, dt_s=round(dt, 3), body=summ)
        print(f'POST /analyze -> {code} ({dt * 1000:.0f} ms): {json.dumps(summ, ensure_ascii=False)}')

        # lỗi đầu vào phải là 4xx JSON, không phải traceback
        code, body, _ = curl(['-F', f'file=@{npy};filename=x.wav', f'{base}/analyze'])
        result['analyze_bad_ext'] = dict(code=code, body=body)
        print(f'POST /analyze (.wav) -> {code}: {json.dumps(body, ensure_ascii=False)}')

        ok = (result['health']['code'] == 200 and result['model']['code'] == 200
              and result['analyze']['code'] == 200 and result['analyze_bad_ext']['code'] == 415)
        result['ok'] = ok
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
        logf.close()
        shutil.rmtree(tmp, ignore_errors=True)
    out = os.path.join(LOG_DIR, 'server_check.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f'-> {out}  ok={result["ok"]}  (log uvicorn: {log_path})')
    sys.exit(0 if result['ok'] else 1)


if __name__ == '__main__':
    main()
