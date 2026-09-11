# -*- coding: utf-8 -*-
"""
Kiểm thử model/silesia_loader.py. Phần cần dữ liệu bị bỏ qua nếu chưa giải nén bộ Silesia.

  * load('B2_03') -> abd (4, N) với N ~ 300 000 (5 phút @1000 Hz), nhãn tăng dần, nằm trong bản ghi,
    nhịp tim thai trung vị trong 100-200 bpm
  * parse_record_id / _rescale_idx không cần dữ liệu
"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'model'))
import silesia_loader as S  # noqa: E402

try:
    SIL = S.silesia_dir()
except SystemExit:
    SIL = None
need_data = pytest.mark.skipif(SIL is None, reason='chưa có bộ Silesia (model/download_silesia.py)')


def test_parse_record_id():
    assert S.parse_record_id('B1_03') == ('B1', 3)
    assert S.parse_record_id('b2-12'.upper()) == ('B2', 12)
    assert S.parse_record_id(('B2', 7)) == ('B2', 7)
    with pytest.raises(ValueError):
        S.parse_record_id('B3_01')


def test_rescale_idx_and_constants():
    assert list(S._rescale_idx(np.array([0, 500, 1000]), 500, 1000)) == [0, 1000, 2000]
    assert S.FS_AB == 500 and S.FS_FQRS == {'B1': 500, 'B2': 1000} and S.N_COLS_AB == 8


@need_data
def test_load_B2_03_shape_and_labels():
    sig, fq, meta = S.load('B2_03')
    assert sig.ndim == 2 and sig.shape[0] == 4
    N = sig.shape[1]
    assert 290_000 <= N <= 310_000, N                   # 5 phút @1000 Hz
    assert meta['fs_out'] == 1000 and meta['group'] == 'B2' and meta['stage'] == 'labour'
    assert np.isfinite(sig).all() and sig.dtype == np.float64
    assert len(fq) > 300                                 # >= 60 bpm trong 5 phút
    assert np.all(np.diff(fq) > 0) and fq[0] >= 0 and fq[-1] < N
    bpm = 60.0 / np.median(np.diff(fq)) * 1000.0
    assert 100.0 <= bpm <= 200.0, bpm
    assert 100.0 <= meta['fhr_median_bpm'] <= 200.0
    assert 'DIRECT' in meta['reference_source']         # B2: điện cực da đầu


@need_data
def test_B2_03_is_listed_and_direct_fecg_has_two_columns():
    assert ('B2', 3) in S.list_records()
    d = S.load_direct_fecg(3)
    assert d.shape[0] == 2 and 290_000 <= d.shape[1] <= 310_000
