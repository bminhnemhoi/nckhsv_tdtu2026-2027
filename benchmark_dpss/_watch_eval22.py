# -*- coding: utf-8 -*-
"""Cho checkpoint production_22 xuat hien roi chay eval_22.py --partial (dung tach phien)."""
import os, sys, time, glob, subprocess, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CK = os.path.join(ROOT, 'model', 'checkpoints')
LOG = os.path.join(ROOT, 'benchmark_dpss', 'eval_22_watch.log')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('FQRS_THREADS', '2')


def log(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'{datetime.datetime.now():%H:%M:%S}  {m}\n')


def prod_exists():
    return bool(glob.glob(os.path.join(CK, 'fetalqrs_tcn_22_production*.pt')))


log('bat dau cho production_22')
t = 0
while not prod_exists() and t < 6 * 3600:
    time.sleep(120); t += 120
    n = len(glob.glob(os.path.join(CK, 'fetalqrs_tcn_22_fold_*.pt')))
    if t % 1200 == 0:
        log(f'da cho {t//60} phut, fold co san: {n}')
if not prod_exists():
    log('HET 6 GIO VAN CHUA CO production_22 -> chay --partial voi cac fold da co');
else:
    log('production_22 da xuat hien, doi 90 s cho ghi xong')
    time.sleep(90)
cmd = [sys.executable, os.path.join(ROOT, 'benchmark_dpss', 'eval_22.py'), '--partial', '--wait-min', '0']
log('chay: ' + ' '.join(cmd))
with open(os.path.join(ROOT, 'benchmark_dpss', 'eval_22_stdout.txt'), 'w', encoding='utf-8') as out:
    rc = subprocess.call(cmd, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)
log(f'eval_22 ket thuc, ma thoat {rc}')
