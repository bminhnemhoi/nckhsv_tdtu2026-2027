# -*- coding: utf-8 -*-
"""
Tai bo Silesia (Matonia va cs. 2020, Scientific Data) tu figshare, co TIEP TUC va TU THU LAI.

DOI collection: 10.6084/m9.figshare.c.4740794   -> article 10311029 -> file 18736784 "Data Records.zip" (~195 MB)

Vi sao can script rieng:
  - figshare chuyen huong sang mot URL S3 ky truoc CHI CO HIEU LUC 10 GIAY, nen moi lan noi lai
    phai xin URL moi roi gui Range ngay lap tuc.
  - Duong truyen tu day toi S3 eu-west-1 chi ~14 KB/s, tai lien tuc mat nhieu gio, de rot.
Chay tach phien (Windows):
  powershell -Command "Start-Process -WindowStyle Hidden python -ArgumentList 'model/download_silesia.py'"
Theo doi:  model/data/silesia/silesia_download.log
"""
import os, sys, time, zipfile, hashlib, datetime
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'model', 'data', 'silesia')
OUT = os.path.join(OUT_DIR, 'Data_Records.zip')
LOG = os.path.join(OUT_DIR, 'silesia_download.log')
FIGSHARE = 'https://ndownloader.figshare.com/files/18736784'
CHUNK = 256 * 1024
os.makedirs(OUT_DIR, exist_ok=True)


def log(msg):
    line = f'{datetime.datetime.now():%H:%M:%S}  {msg}'
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    try:
        print(line, flush=True)
    except Exception:
        pass


def fresh_s3_url():
    r = requests.get(FIGSHARE, allow_redirects=False, timeout=30)
    if r.status_code in (301, 302, 303, 307, 308) and 'Location' in r.headers:
        return r.headers['Location']
    raise RuntimeError(f'khong lay duoc redirect: HTTP {r.status_code}')


def total_size():
    url = fresh_s3_url()
    r = requests.head(url, timeout=30)
    n = int(r.headers.get('Content-Length', 0))
    if n <= 0:
        r = requests.get(url, headers={'Range': 'bytes=0-0'}, stream=True, timeout=30)
        cr = r.headers.get('Content-Range', '')
        n = int(cr.split('/')[-1]) if '/' in cr else 0
        r.close()
    return n


def main():
    log('=== bat dau / tiep tuc tai Silesia ===')
    total = 0
    for _ in range(10):
        try:
            total = total_size(); break
        except Exception as e:
            log(f'chua lay duoc kich thuoc: {e}'); time.sleep(10)
    if total <= 0:
        log('KHONG LAY DUOC KICH THUOC, dung.'); return 2
    log(f'kich thuoc tong: {total/1e6:.1f} MB')

    fails = 0; last_report = 0
    while True:
        have = os.path.getsize(OUT) if os.path.exists(OUT) else 0
        if have >= total:
            break
        try:
            url = fresh_s3_url()                     # URL chi song 10 s -> dung ngay
            with requests.get(url, headers={'Range': f'bytes={have}-'}, stream=True, timeout=(30, 120)) as r:
                if r.status_code not in (200, 206):
                    raise RuntimeError(f'HTTP {r.status_code}')
                if r.status_code == 200 and have > 0:
                    raise RuntimeError('server khong ho tro Range, tu choi ghi de')
                with open(OUT, 'ab') as f:
                    for blk in r.iter_content(CHUNK):
                        if not blk:
                            continue
                        f.write(blk); have += len(blk)
                        if have - last_report >= 5 * 1024 * 1024:
                            log(f'{have/1e6:7.1f} / {total/1e6:.1f} MB  ({100*have/total:5.1f}%)')
                            last_report = have
            fails = 0
        except Exception as e:
            fails += 1
            log(f'rot ket noi ({fails}): {type(e).__name__}: {str(e)[:80]} -- tiep tuc tu {have/1e6:.1f} MB sau {min(5*fails,60)} s')
            time.sleep(min(5 * fails, 60))
            if fails > 500:
                log('QUA NHIEU LOI, dung.'); return 3

    log(f'tai xong: {os.path.getsize(OUT)/1e6:.1f} MB')
    try:
        with zipfile.ZipFile(OUT) as z:
            bad = z.testzip()
            names = z.namelist()
        log(f'zip hop le: {len(names)} file' + (f', LOI o {bad}' if bad else ''))
        h = hashlib.sha256()
        with open(OUT, 'rb') as f:
            for blk in iter(lambda: f.read(1 << 20), b''):
                h.update(blk)
        log(f'sha256: {h.hexdigest()}')
        log('=== HOAN TAT ===')
        return 0
    except zipfile.BadZipFile as e:
        log(f'ZIP HONG: {e}'); return 4


if __name__ == '__main__':
    sys.exit(main())
