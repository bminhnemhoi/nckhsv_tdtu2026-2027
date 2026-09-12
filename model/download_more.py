# -*- coding: utf-8 -*-
"""
Tai bo sung du lieu de pha diem yeu "mot he ghi, 10/75 ban ghi CinC".

  cinc75   PhysioNet/CinC 2013 set-a DAY DU 75 ban ghi (a01..a75) -> benchmark_dpss/pcdb/
  nifeadb  Non-Invasive Fetal ECG Arrhythmia Database (Behar 2019) -> model/data/nifeadb/
  ninfea   NInFEA (Sulas 2021, 60 thai phu 21-27 tuan, 2048 Hz)   -> model/data/ninfea/   (LON, tai dan)

Chay:  python model/download_more.py --only cinc75 nifeadb
       python model/download_more.py --only ninfea --max-records 12
Co tiep tuc (bo qua file da du kich thuoc), ghi data_card_more.json voi sha256.
"""
import os, sys, json, time, argparse, hashlib, datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMEOUT = (30, 180)

SOURCES = {
    'cinc75': dict(
        name='PhysioNet/CinC Challenge 2013 set-a (full 75 records)',
        cite='Silva I, Behar J, Sameni R, et al. Computing in Cardiology 2013;40:149-152.',
        licence='Open Data Commons Attribution License v1.0',
        base='https://physionet.org/files/challenge-2013/1.0.0/set-a/',
        out=os.path.join(ROOT, 'benchmark_dpss', 'pcdb'),
        files=[f'a{i:02d}{e}' for i in range(1, 76) for e in ('.dat', '.hea', '.fqrs')],
        note='7 ban ghi bi loai theo Zhong 2018 (chu thich sai): a33 a38 a47 a52 a54 a71 a74 -- '
             'quy tac loai tru phai KHAI BAO TRUOC khi bao cao.',
    ),
    'nifeadb': dict(
        name='Non-Invasive Fetal ECG Arrhythmia Database (NIFEADB)',
        cite='Behar JA, Bonnemains L, Shulgin V, et al. Prenat Diagn. 2019;39(3):178-187. DOI 10.1002/pd.5412',
        licence='Open Data Commons Attribution License v1.0',
        base='https://physionet.org/files/nifeadb/1.0.0/',
        out=os.path.join(ROOT, 'model', 'data', 'nifeadb'),
        files=None,          # lay tu RECORDS
        note='26 ban ghi co chu thich fQRS, co ca loan nhip thai. CANH BAO: cac ban ghi ecgca* '
             'deu tu MOT san phu -- khong duoc dem la nhieu chu the doc lap.',
    ),
    'ninfea': dict(
        name='NInFEA: Non-Invasive Multimodal Foetal ECG-Doppler (Sulas 2021)',
        cite='Sulas E, Urru M, Tumbarello R, et al. Sci Data. 2021;8:30. DOI 10.1038/s41597-021-00811-3',
        licence='Open Data Commons Attribution License v1.0',
        base='https://physionet.org/files/ninfea/1.0.0/',
        out=os.path.join(ROOT, 'model', 'data', 'ninfea'),
        files=None,
        note='60 ban ghi, 21-27 tuan thai, 22 kenh bung + Doppler PWD, 2048 Hz. Nhan tham chieu tu '
             'Doppler -> Power-MF dung dung sai 200 ms cho bo nay, KHONG phai 50 ms.',
    ),
}


def log(m):
    print(f'{datetime.datetime.now():%H:%M:%S}  {m}', flush=True)


def fetch(url, path, retries=6):
    """tai mot file, bo qua neu da co va kich thuoc khop; tra (ok, bytes, tu_cache)"""
    try:
        h = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        want = int(h.headers.get('Content-Length', 0))
    except Exception:
        want = 0
    if os.path.exists(path) and want and os.path.getsize(path) == want:
        return True, want, True
    for k in range(retries):
        try:
            have = os.path.getsize(path) if os.path.exists(path) else 0
            hdr = {'Range': f'bytes={have}-'} if (have and want and have < want) else {}
            with requests.get(url, headers=hdr, stream=True, timeout=TIMEOUT) as r:
                if r.status_code == 404:
                    return False, 0, False
                if r.status_code not in (200, 206):
                    raise RuntimeError(f'HTTP {r.status_code}')
                mode = 'ab' if r.status_code == 206 else 'wb'
                with open(path, mode) as f:
                    for blk in r.iter_content(1 << 18):
                        if blk:
                            f.write(blk)
            return True, os.path.getsize(path), False
        except Exception as e:
            if k == retries - 1:
                log(f'   THAT BAI {os.path.basename(path)}: {type(e).__name__}')
                return False, 0, False
            time.sleep(min(4 * (k + 1), 30))
    return False, 0, False


def record_list(base):
    """doc RECORDS cua mot bo PhysioNet -> danh sach ban ghi"""
    r = requests.get(base + 'RECORDS', timeout=TIMEOUT)
    r.raise_for_status()
    return [x.strip() for x in r.text.splitlines() if x.strip()]


def sha256(path, n=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blk in iter(lambda: f.read(n), b''):
            h.update(blk)
    return h.hexdigest()


def do(key, max_records=None):
    s = SOURCES[key]
    os.makedirs(s['out'], exist_ok=True)
    log(f'=== {key}: {s["name"]} ===')
    log(f'    {s["note"]}')
    files = s['files']
    if files is None:
        recs = record_list(s['base'])
        if max_records:
            recs = recs[:max_records]
        log(f'    RECORDS: {len(recs)} ban ghi')
        files = []
        for rec in recs:
            files += [rec + e for e in ('.dat', '.hea', '.atr', '.qrs', '.fqrs')]
    ok = skipped = miss = 0
    total = 0
    t0 = time.time()
    for i, fn in enumerate(files, 1):
        path = os.path.join(s['out'], fn.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        good, nb, cached = fetch(s['base'] + fn, path)
        if good:
            ok += 1; total += nb; skipped += int(cached)
        else:
            miss += 1
            if os.path.exists(path) and os.path.getsize(path) == 0:
                os.remove(path)
        if i % 25 == 0 or i == len(files):
            log(f'    {i}/{len(files)}  ok {ok} (cache {skipped})  thieu {miss}  {total/1e6:.1f} MB  {time.time()-t0:.0f}s')
    got = [f for f in os.listdir(s['out']) if os.path.isfile(os.path.join(s['out'], f))]
    card = dict(key=key, name=s['name'], cite=s['cite'], licence=s['licence'], base=s['base'],
                note=s['note'], downloaded=datetime.datetime.now().isoformat(),
                n_files=len(got), bytes=sum(os.path.getsize(os.path.join(s['out'], f)) for f in got),
                sha256={f: sha256(os.path.join(s['out'], f))[:16] for f in sorted(got)[:400]})
    with open(os.path.join(s['out'], 'data_card_more.json'), 'w', encoding='utf-8') as f:
        json.dump(card, f, ensure_ascii=False, indent=1)
    log(f'    XONG: {len(got)} file, {card["bytes"]/1e6:.1f} MB -> {s["out"]}')
    return card


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', nargs='+', default=['cinc75'], choices=list(SOURCES))
    ap.add_argument('--max-records', type=int, default=None)
    a = ap.parse_args()
    out = {}
    for k in a.only:
        try:
            out[k] = do(k, a.max_records)
        except Exception as e:
            log(f'{k} LOI: {type(e).__name__}: {e}')
    log('hoan tat: ' + ', '.join(f'{k}={v["n_files"]} file' for k, v in out.items()))
