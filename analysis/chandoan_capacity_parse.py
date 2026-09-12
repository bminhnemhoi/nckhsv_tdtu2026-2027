# -*- coding: utf-8 -*-
"""
Dung lai analysis/chandoan_capacity.json tu analysis/chandoan_capacity_log.txt.
Can den khi lan chay bi dung som (het ngan sach thoi gian) truoc khi script goc kip ghi JSON.
Moi con so deu doc nguyen van tu nhat ky tren dia -> van truy nguoc duoc.
"""
import os, sys, re, json, datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'chandoan_capacity_log.txt')
OUT = os.path.join(HERE, 'chandoan_capacity.json')
txt = open(LOG, encoding='utf-8').read().splitlines()

res = dict(meta=dict(date=str(datetime.datetime.now()), rebuilt_from='chandoan_capacity_log.txt',
                     note='lan chay bi dung sau nhanh be rong 40 de giu ngan sach 120 phut'))
recs = {}
for ln in txt:
    m = re.match(r'\s+(r\d\d|B[12]_\d\d)\s+([\d.]+)\s+([\d.]+)\s+([+-][\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$', ln)
    if m:
        recs[m.group(1)] = dict(F1_psd=float(m.group(2)), loso_F1_psd=float(m.group(3)),
                                gap=float(m.group(4)), F1_mean4=float(m.group(5)), loso_F1_mean4=float(m.group(6)))
A = dict(records=recs)
for ln in txt:
    m = re.search(r'TRONG MAU PSD ([\d.]+)\s+\|\s+LOSO PSD ([\d.]+)\s+\|\s+khoang cach ([+-][\d.]+)', ln)
    if m:
        A.update(mean_insample_psd=float(m.group(1)), mean_loso_psd=float(m.group(2)), gap_psd=float(m.group(3)))
    m = re.search(r'TRONG MAU TB4 ([\d.]+)\s+\|\s+LOSO TB4 ([\d.]+)\s+\|\s+khoang cach ([+-][\d.]+)', ln)
    if m:
        A.update(mean_insample_mean4=float(m.group(1)), mean_loso_mean4=float(m.group(2)), gap_mean4=float(m.group(3)))
    m = re.search(r'nguong ([\d.]+); n tham so (\d+)', ln)
    if m:
        A.update(threshold=float(m.group(1)), n_params=int(m.group(2)))
res['A_insample_22'] = A

B = dict(models={}, note='ngưỡng chọn TRONG MẪU -> F1 la chan tren; khong tang cuong')
m = re.search(r'PHEP THU HOC THUOC tren (\[.*?\]) \((\d+) epoch', '\n'.join(txt))
if m:
    B['subset'] = eval(m.group(1)); B['epochs'] = int(m.group(2))
m = re.search(r'(\d+) doan train, (\d+) buoc/epoch', '\n'.join(txt))
if m:
    B['n_segments'] = int(m.group(1)); B['steps_per_epoch'] = int(m.group(2))
cur = None
for ln in txt:
    m = re.search(r'-- be rong (\d+) kenh, (\d+) tham so --', ln)
    if m:
        cur = m.group(1); B['models'][cur] = dict(width=int(cur), n_params=int(m.group(2)), loss_hist=[], records={})
        continue
    if cur is None: continue
    m = re.search(r'epoch (\d+)/(\d+) loss ([\d.]+)', ln)
    if m: B['models'][cur]['loss_hist'].append(float(m.group(3)))
    m = re.search(r'nguong trong mau ([\d.]+); F1 TRONG MAU trung binh tren 16 \(chu the x kenh\) ([\d.]+)', ln)
    if m:
        B['models'][cur]['threshold'] = float(m.group(1)); B['models'][cur]['F1_insample_lead_mean'] = float(m.group(2))
    m = re.match(r'\s+(r\d\d|B[12]_\d\d)\s+PSD\s+([\d.]+)\s+TB4\s+([\d.]+)\s+oracle\s+([\d.]+)\s+(.*)$', ln)
    if m:
        B['models'][cur]['records'][m.group(1)] = dict(
            F1_psd=float(m.group(2)), F1_mean4=float(m.group(3)), F1_oracle=float(m.group(4)),
            per_lead={p.split(':')[0]: float(p.split(':')[1]) for p in m.group(5).split()})
for w, mo in B['models'].items():
    if mo['records']:
        mo['F1_insample_psd'] = sum(r['F1_psd'] for r in mo['records'].values()) / len(mo['records'])
        mo['F1_insample_mean4'] = sum(r['F1_mean4'] for r in mo['records'].values()) / len(mo['records'])
res['B_memorise'] = B
json.dump(res, open(OUT, 'w', encoding='utf-8'), indent=1, default=float)
print(f'A: {len(recs)} chu the, trong mau {A.get("mean_insample_psd")} vs LOSO {A.get("mean_loso_psd")}')
for w, mo in B['models'].items():
    print(f'B width {w}: {mo.get("F1_insample_lead_mean")} (16 chu the x kenh), '
          f'loss {mo["loss_hist"][0] if mo["loss_hist"] else None} -> {mo["loss_hist"][-1] if mo["loss_hist"] else None}, '
          f'{len(mo["records"])} chu the')
print('->', OUT)
