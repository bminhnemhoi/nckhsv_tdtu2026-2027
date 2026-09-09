# -*- coding: utf-8 -*-
"""Giai quyet duong dan du lieu, de repo tu chua khong phu thuoc thu muc ben ngoai."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def adfecgdb_dir():
    """Tra ve thu muc chua ADFECGDB (r01.edf ...).

    Thu tu uu tien:
      1. bien moi truong ADFECGDB_DIR
      2. model/data/adfecgdb  -- do model/download_data.py tao ra
      3. goi-danh-gia-doi-chuan-dpss/data/raw  -- neu goi doi chuan ben ngoai co san
    """
    for c in (os.environ.get('ADFECGDB_DIR'),
              os.path.join(ROOT, 'model', 'data', 'adfecgdb'),
              os.path.join(ROOT, 'goi-danh-gia-doi-chuan-dpss', 'data', 'raw')):
        if c and os.path.isfile(os.path.join(c, 'r01.edf')):
            return c
    raise SystemExit(
        'Khong tim thay ADFECGDB.\n'
        'Chay:  python model/download_data.py --root model/data --only adfecgdb\n'
        'hoac dat bien moi truong ADFECGDB_DIR tro toi thu muc chua r01.edf')


def cinc2013_dir():
    """Tra ve thu muc chua CinC 2013 set-a, hoac None neu chua tai."""
    for c in (os.environ.get('CINC2013_DIR'),
              os.path.join(ROOT, 'benchmark_dpss', 'pcdb'),
              os.path.join(ROOT, 'model', 'data', 'pcdb')):
        if c and os.path.isdir(c) and any(f.endswith('.dat') for f in os.listdir(c)):
            return c
    return None


def model_dir():
    return os.path.join(ROOT, 'model')


def checkpoint(name):
    return os.path.join(ROOT, 'model', 'checkpoints', name)
