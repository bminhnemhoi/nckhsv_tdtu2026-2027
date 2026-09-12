# -*- coding: utf-8 -*-
"""Dung lai moi truong chay Power-MF tu dau (thu muc tools/ KHONG duoc commit).

Tai ve va giai nen vao D:/NCKHSV2026-2027/tools/:
  tools/octave/octave-11.3.0-w64/        GNU Octave portable, GPL-3.0   (~855 MB tai ve)
  tools/fecg-benchmarking/               repo Jaeger 2024, MIT
  tools/varanini/xCinC/                  30 ham .m cua Varanini 2014 (PhysioNet/CinC 2013)

Vi sao khong commit: Octave 2 GB va GPL-3.0; ma du thi PhysioNet khong gan nhan
giay phep chuan trong zip (xem survey/scout_baselines.md muc 2.3).

Chay:  python baselines/powermf_setup.py
       python baselines/powermf_setup.py --check      (chi kiem tra, khong tai)
"""
import argparse
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')

OCTAVE_URL = 'https://ftp.gnu.org/gnu/octave/windows/octave-11.3.0-w64.zip'
OCTAVE_EXE = os.path.join(TOOLS, 'octave', 'octave-11.3.0-w64', 'mingw64', 'bin', 'octave-cli.exe')
BENCH_URL = 'https://github.com/mad-lab-fau/fecg-benchmarking'
BENCH_DIR = os.path.join(TOOLS, 'fecg-benchmarking')
VAR_URL = 'https://archive.physionet.org/challenge/2013/sources/pmea/pmea-varanini.zip'
VAR_DIR = os.path.join(TOOLS, 'varanini')
VAR_XCINC = os.path.join(VAR_DIR, 'xCinC')

# 8 ham ngoai ma PowerMF.m goi truc tiep (kiem tra du hay thieu)
NEEDED = ['FecgImpArtCanc', 'FecgDetrFilt', 'FecgNotchFilt', 'FecgICAm',
          'FecgInterp', 'FecgQRSmDet', 'FecgQRSmCanc', 'FecgICAf']


def fetch(url, dest):
    if os.path.isfile(dest) and os.path.getsize(dest) > 1000:
        print('  da co: %s (%.1f MB)' % (dest, os.path.getsize(dest) / 1e6))
        return dest
    print('  tai %s -> %s' % (url, dest))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    print('  xong: %.1f MB' % (os.path.getsize(dest) / 1e6))
    return dest


def check():
    ok = True
    print('octave-cli : %s' % ('CO  ' + OCTAVE_EXE if os.path.isfile(OCTAVE_EXE) else 'THIEU'))
    ok &= os.path.isfile(OCTAVE_EXE)
    pm = os.path.join(BENCH_DIR, 'Code', 'PowerMF.m')
    print('PowerMF.m  : %s' % ('CO  ' + pm if os.path.isfile(pm) else 'THIEU'))
    ok &= os.path.isfile(pm)
    have = set()
    if os.path.isdir(VAR_XCINC):
        have = {os.path.splitext(f)[0] for f in os.listdir(VAR_XCINC) if f.endswith('.m')}
    miss = [n for n in NEEDED if n not in have]
    print('xCinC      : %d file .m, thieu %d/%d ham PowerMF can %s'
          % (len(have), len(miss), len(NEEDED), miss if miss else ''))
    ok &= not miss
    if os.path.isfile(OCTAVE_EXE):
        p = subprocess.run([OCTAVE_EXE, '--no-gui', '--quiet', '--eval',
                            'pkg load signal; disp(version)'],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        print('smoke test : rc=%d  out=%r' % (p.returncode, (p.stdout or '').strip()))
        ok &= p.returncode == 0
    print('=> %s' % ('SAN SANG' if ok else 'CHUA DU'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if a.check:
        return check()

    os.makedirs(TOOLS, exist_ok=True)

    print('[1/3] GNU Octave 11.3.0 portable')
    if not os.path.isfile(OCTAVE_EXE):
        z = fetch(OCTAVE_URL, os.path.join(TOOLS, 'octave.zip'))
        os.makedirs(os.path.join(TOOLS, 'octave'), exist_ok=True)
        # bsdtar co san trong Windows 11; nhanh hon Expand-Archive nhieu lan
        print('  giai nen bang tar -xf ...')
        subprocess.run(['tar', '-xf', z], cwd=os.path.join(TOOLS, 'octave'), check=True)
    else:
        print('  da co octave-cli')

    print('[2/3] repo fecg-benchmarking (MIT)')
    if not os.path.isdir(os.path.join(BENCH_DIR, 'Code')):
        if shutil.which('git'):
            subprocess.run(['git', 'clone', '--depth', '1', BENCH_URL, BENCH_DIR], check=True)
        else:
            z = fetch(BENCH_URL + '/archive/refs/heads/main.zip',
                      os.path.join(TOOLS, 'fecg-benchmarking.zip'))
            with zipfile.ZipFile(z) as f:
                f.extractall(TOOLS)
    else:
        print('  da co')

    print('[3/3] xCinC cua Varanini 2014 (PhysioNet/CinC 2013)')
    if not os.path.isdir(VAR_XCINC):
        z = fetch(VAR_URL, os.path.join(VAR_DIR, 'pmea-varanini.zip'))
        with zipfile.ZipFile(z) as f:
            f.extractall(VAR_DIR)
    else:
        print('  da co')

    print('\n--- ap ban va Octave vao ban sao PowerMF.m ---')
    src = os.path.join(BENCH_DIR, 'Code', 'PowerMF.m')
    mf = os.path.join(BENCH_DIR, 'Code', 'helper', 'matched_filter.m')
    dst_dir = os.path.join(ROOT, 'baselines', 'octave')
    os.makedirs(dst_dir, exist_ok=True)
    for s in (src, mf):
        if os.path.isfile(s):
            shutil.copy2(s, os.path.join(dst_dir, os.path.basename(s)))
    subprocess.run([sys.executable, os.path.join(dst_dir, 'apply_patches.py')], check=False)
    return check()


if __name__ == '__main__':
    raise SystemExit(main())
