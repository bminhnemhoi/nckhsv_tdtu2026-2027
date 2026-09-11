# -*- coding: utf-8 -*-
"""
Tang cuong du lieu ON-THE-FLY cho FetalQRS-TCN (chi dung khi HUAN LUYEN, khong dung khi kiem thu).

Moi doan train la mot cap (du sau khu me, tin hieu goc) da robust_scale, dai 1000 mau @250 Hz, cung ban do
nhiet nhan. Bon phep bien doi, moi phep ap voi xac suat p=0,5, doc lap theo tung doan trong batch:
  (a) nhan bien do ngau nhien a ~ U(0,7; 1,4)           -- cung mot he so cho CA HAI hang
  (b) nhieu Gauss trang o SNR ~ U(10; 30) dB so voi cong suat cua tung hang; CUNG mot hien thuc nhieu chuan hoa
      cho ca hai hang (nhieu tren tin hieu goc di nguyen vao phan du), chi khac he so theo cong suat tung hang
  (c) troi duong nen: sin tan so f ~ U(0,1; 0,5) Hz, pha ngau nhien, bien do ~ U(0,1; 0,3) x do lech chuan cua
      tung hang; cung f va pha cho ca hai hang
  (d) dich thoi gian +/-100 ms: KHONG dich bang cach dem mau -- bo lay mau doc doan tu vi tri s + delta trong ban
      ghi day du, nen tin hieu VA nhan dich cung nhau, khong co mau dem 0. Ham sample_shift() chi tra ve delta.

API:
  sample_shift(rng, p=.5, max_ms=100, fs=250) -> int (so mau dich, 0 neu khong ap)
  augment_batch(X, Y, rng, p=.5, ...)         -> X' (B,2,T) float32; Y giu nguyen (dich da xu ly o bo lay mau)
"""
from __future__ import annotations
import numpy as np

AUG_CFG = dict(p=0.5, amp=(0.7, 1.4), snr_db=(10.0, 30.0), bw_hz=(0.1, 0.5), bw_amp=(0.1, 0.3),
               shift_ms=100.0, fs=250)


def sample_shift(rng, p=AUG_CFG['p'], max_ms=AUG_CFG['shift_ms'], fs=AUG_CFG['fs']):
    """so mau dich trong [-max, +max] voi xac suat p, nguoc lai 0."""
    if rng.random() >= p:
        return 0
    m = int(round(max_ms / 1000.0 * fs))
    return int(rng.integers(-m, m + 1))


def augment_batch(X, rng, p=AUG_CFG['p'], amp=AUG_CFG['amp'], snr_db=AUG_CFG['snr_db'],
                  bw_hz=AUG_CFG['bw_hz'], bw_amp=AUG_CFG['bw_amp'], fs=AUG_CFG['fs']):
    """X: ndarray (B, C, T) float32, C = 2 hang (du, goc). Tra ve ban sao da tang cuong (a)(b)(c).
    Nhan khong doi vi ba phep nay khong dich thoi gian."""
    X = np.array(X, dtype=np.float32, copy=True)
    B, C, T = X.shape
    t = np.arange(T, dtype=np.float32) / fs
    # (a) bien do -- mot he so cho ca hai hang
    m = rng.random(B) < p
    if m.any():
        a = rng.uniform(amp[0], amp[1], size=B).astype(np.float32)
        X[m] *= a[m][:, None, None]
    # (b) nhieu trang theo SNR so voi cong suat tung hang; cung hien thuc nhieu chuan hoa cho hai hang
    m = rng.random(B) < p
    if m.any():
        snr = rng.uniform(snr_db[0], snr_db[1], size=B).astype(np.float32)
        P = np.mean(X ** 2, axis=2)                                  # (B, C)
        sig = np.sqrt(P / (10.0 ** (snr[:, None] / 10.0))).astype(np.float32)
        n = rng.standard_normal((B, 1, T)).astype(np.float32)
        X[m] += (n * sig[:, :, None])[m]
    # (c) troi duong nen sin cham, cung f va pha cho hai hang, bien do theo do lech chuan tung hang
    m = rng.random(B) < p
    if m.any():
        f = rng.uniform(bw_hz[0], bw_hz[1], size=B).astype(np.float32)
        ph = rng.uniform(0, 2 * np.pi, size=B).astype(np.float32)
        r = rng.uniform(bw_amp[0], bw_amp[1], size=B).astype(np.float32)
        sd = X.std(axis=2)                                           # (B, C)
        w = np.sin(2 * np.pi * f[:, None] * t[None, :] + ph[:, None]).astype(np.float32)   # (B, T)
        X[m] += ((r[:, None] * sd)[:, :, None] * w[:, None, :])[m]
    return X


def describe():
    return dict(AUG_CFG, ops=['amplitude', 'white_noise_snr', 'baseline_wander_sin', 'time_shift_via_sampler'],
                note='moi phep p=0,5 doc lap; ap nhat quan tren ca hai hang (du + goc); dich thoi gian dich ca nhan')


if __name__ == '__main__':
    rng = np.random.default_rng(0)
    X = rng.standard_normal((4, 2, 1000)).astype(np.float32)
    Y = augment_batch(X, rng)
    print('shape', Y.shape, 'dtype', Y.dtype, 'diff mean abs', float(np.abs(Y - X).mean()))
    print('shifts', [sample_shift(rng) for _ in range(10)])
