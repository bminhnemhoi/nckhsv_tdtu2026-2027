#!/usr/bin/env python
"""
Download every dataset this project needs, straight from the source.
No dependency on any third-party repository.

Usage
-----
  python download_data.py --root data                 # ADFECGDB + CinC2013 set-a + NSTDB
  python download_data.py --root data --all           # also FECGSYNDB (large) and NIFEADB
  python download_data.py --root data --only adfecgdb
"""
from __future__ import annotations
import os, sys, argparse, hashlib, urllib.request, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

UA = {'User-Agent': 'Mozilla/5.0 (research script; PhysioNet ODC-BY compliant)'}

SOURCES = {
    'adfecgdb': dict(
        name='Abdominal and Direct Fetal ECG Database',
        cite='Jezewski J, Matonia A, Kupka T, Roj D, Czabanski R. Biomed Tech 2012. '
             'DOI 10.1515/bmt-2011-0130. PhysioNet DOI 10.13026/C2RP4B.',
        licence='Open Data Commons Attribution License v1.0',
        base='https://physionet.org/files/adfecgdb/1.0.0/',
        files=[f'{r}{e}' for r in ('r01', 'r04', 'r07', 'r08', 'r10') for e in ('.edf', '.edf.qrs')],
    ),
    'cinc2013': dict(
        name='PhysioNet/CinC Challenge 2013, set-a',
        cite='Silva I, Behar J, Sameni R, Zhu T, Oster J, Clifford GD, Moody GB. '
             'Computing in Cardiology 2013.',
        licence='Open Data Commons Attribution License v1.0',
        base='https://physionet.org/files/challenge-2013/1.0.0/set-a/',
        files=[f'a{i:02d}{e}' for i in range(1, 76) for e in ('.dat', '.hea', '.fqrs')],
    ),
    'nstdb': dict(
        name='MIT-BIH Noise Stress Test Database (noise records only)',
        cite='Moody GB, Muldrow WE, Mark RG. Computers in Cardiology 1984;11:381-384.',
        licence='Open Data Commons Attribution License v1.0',
        base='https://physionet.org/files/nstdb/1.0.0/',
        files=[f'{n}{e}' for n in ('bw', 'em', 'ma') for e in ('.dat', '.hea')],
    ),
    'nifeadb': dict(
        name='Non-Invasive Fetal ECG Arrhythmia Database',
        cite='Behar JA, Bonnemains L, Shulgin V, Oster J, Ostras O, Lakhno I. '
             'Prenatal Diagnosis 2019. PhysioNet DOI 10.13026/C2CT0S.',
        licence='Open Data Commons Attribution License v1.0',
        base='https://physionet.org/files/nifeadb/1.0.0/',
        files=[f'{p}_{i:02d}{e}' for p in ('ARR', 'NR') for i in range(1, 15) for e in ('.dat', '.hea')],
        optional=True,
    ),
}

NOTES = """
Datasets that must be fetched by hand (no direct file API):

  Matonia et al. 2020, "Fetal electrocardiograms, direct and abdominal with reference
  heartbeat annotations", Scientific Data 7:200. DOI 10.1038/s41597-020-0538-z
  Data on figshare: DOI 10.6084/m9.figshare.c.4740794
  10 pregnancy signals x 20 min (weeks 32-42) + 12 labour signals x 5 min (weeks 38-42),
  500 Hz abdominal / 1 kHz direct, 4 abdominal leads, expert-corrected annotations with a
  per-beat reliability flag. Place under <root>/matonia2020/.

  FECGSYNDB (synthetic), Andreotti et al. 2016, Physiol Meas 37(5):627.
  https://physionet.org/content/fecgsyndb/  -- about 40 GB; use the PhysioNet wget recipe
  or the `wfdb.dl_database('fecgsyndb', ...)` helper for the subset you need.
"""


def fetch(url, dest, retries=3):
    if os.path.exists(dest) and os.path.getsize(dest) > 512:
        return 'cached', os.path.getsize(dest)
    for k in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            if len(data) < 128:
                raise IOError(f'suspiciously small response ({len(data)} bytes)')
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(data)
            return 'ok', len(data)
        except Exception as e:
            if k == retries - 1:
                return f'FAILED ({type(e).__name__}: {e})', 0
    return 'FAILED', 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='data')
    ap.add_argument('--only', default=None, help='one of: ' + ', '.join(SOURCES))
    ap.add_argument('--all', action='store_true', help='include optional large sets')
    a = ap.parse_args()

    keys = [a.only] if a.only else [k for k, v in SOURCES.items() if a.all or not v.get('optional')]
    card = {}
    for k in keys:
        s = SOURCES[k]
        out = os.path.join(a.root, k)
        print(f'\n=== {s["name"]} -> {out} ===')
        print(f'    {s["licence"]}')
        ok = miss = 0
        digests = {}
        for fn in s['files']:
            status, n = fetch(s['base'] + fn, os.path.join(out, fn))
            if status.startswith('FAILED'):
                miss += 1
                print(f'    [!] {fn}: {status}')
            else:
                ok += 1
                with open(os.path.join(out, fn), 'rb') as f:
                    digests[fn] = hashlib.sha256(f.read()).hexdigest()[:16]
        print(f'    {ok} files present, {miss} failed')
        card[k] = dict(name=s['name'], citation=s['cite'], licence=s['licence'],
                       base_url=s['base'], n_files=ok, n_failed=miss, sha256_16=digests)

    os.makedirs(a.root, exist_ok=True)
    with open(os.path.join(a.root, 'data_card.json'), 'w', encoding='utf-8') as f:
        json.dump(card, f, indent=1, ensure_ascii=False)
    print(f'\nWrote {os.path.join(a.root, "data_card.json")} (file hashes for reproducibility).')
    print(NOTES)
    print('Cite every dataset you use. All PhysioNet sets above are ODC-BY: attribution is required.')


if __name__ == '__main__':
    main()
