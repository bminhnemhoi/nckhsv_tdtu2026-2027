# -*- coding: utf-8 -*-
"""Dong lo hong "chong lan MOT PHAN": quet NCC bang cua so CON 10 s.
Neu mot ban CinC chi trung 10-30 s voi ADFECGDB thi NCC tren ca 60 s se bi pha loang.
BA NHANH (bat buoc, vi quet cua so con co so sanh boi RAT lon nen khong co nguong tien nghiem):
  clean    -- 60 ban CinC SACH  vs ADFECGDB that
  null     -- 60 ban CinC SACH  vs ADFECGDB DAO NGUOC THOI GIAN (chung khong the trung nhau,
              nhung van la chuoi QRS gia chu ky cung pho -> cho NGUONG NULL dung)
  positive -- 15 ban CinC DA BIET ro ri vs ADFECGDB that (phai dat ~1.0)
Chay: python analysis/dulieu_m4b_partial.py"""
import os, sys, json, time
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, wfdb, mne

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
AD = os.path.join(ROOT, 'model', 'data', 'adfecgdb')
CI = os.path.join(ROOT, 'benchmark_dpss', 'pcdb')
PN = ['r01', 'r04', 'r07', 'r08', 'r10']
LEAK = set(json.load(open(os.path.join(HERE, 'dulieu_m4b_verify.json'), encoding='utf-8'))['danh_sach_ro_ri'])
DEC = 8          # 1000 -> 125 Hz
WIN_S = 10.0     # cua so con 10 s
HOP_S = 5.0      # buoc truot 5 s -> 11 cua so / ban ghi 60 s


def z(x):
    x = np.asarray(x, float); x = x - x.mean(); s = x.std()
    return x / s if s > 0 else x


RAWCH = {}
for r in PN:
    raw = mne.io.read_raw_edf(os.path.join(AD, r + '.edf'), preload=True, verbose='ERROR')
    for c, nm in enumerate(raw.ch_names):
        RAWCH[(r, nm)] = z(raw.get_data()[c][::DEC])
FS = 1000.0 / DEC
m = int(WIN_S * FS); hop = int(HOP_S * FS)
nfft = 1
while nfft < max(len(v) for v in RAWCH.values()) + m:
    nfft *= 2


def build(reverse):
    L = {k: (v[::-1].copy() if reverse else v) for k, v in RAWCH.items()}
    LFp = {k: np.fft.rfft(v, nfft) for k, v in L.items()}
    P = {}
    for k, v in L.items():
        cs = np.concatenate([[0.0], np.cumsum(v)]); cs2 = np.concatenate([[0.0], np.cumsum(v ** 2)])
        n = len(v) - m + 1
        s1 = cs[m:m + n] - cs[:n]; s2 = cs2[m:m + n] - cs2[:n]
        P[k] = np.sqrt(np.maximum(s2 - s1 * s1 / m, 1e-12)) * np.sqrt(m)
    return L, LFp, P


def scan(recs, reverse):
    LONG, LF, PRE = build(reverse)
    out = {}
    for t in recs:
        X = wfdb.rdrecord(os.path.join(CI, t)).p_signal.T
        best = (0.0, None, None, None)
        for ch in range(X.shape[0]):
            xd = X[ch][::DEC]
            for s0 in range(0, len(xd) - m + 1, hop):
                sz = z(xd[s0:s0 + m])
                S = np.fft.rfft(sz[::-1], nfft)
                for k in LONG:
                    cc = np.fft.irfft(LF[k] * S, nfft)[m - 1:m - 1 + len(PRE[k])]
                    r = cc / PRE[k]
                    j = int(np.argmax(np.abs(r)))
                    if abs(r[j]) > abs(best[0]):
                        best = (float(r[j]), ch, s0 / FS, '%s/%s @%.1fs' % (k[0], k[1], j / FS))
        out[t] = dict(ncc_cua_so_con=round(best[0], 4), kenh_cinc=best[1],
                      bat_dau_trong_cinc_s=best[2], khop_voi=best[3])
        print('  %s  %.4f  (%s)' % (t, abs(best[0]), best[3]), flush=True)
    return out


ALL = ['a%02d' % i for i in range(1, 76)]
CLEAN = [t for t in ALL if t not in LEAK]
t0 = time.time()
print('-- nhanh CLEAN (60 ban sach vs ADFECGDB that) --', flush=True)
res = scan(CLEAN, False)
print('-- nhanh NULL (60 ban sach vs ADFECGDB DAO NGUOC) --', flush=True)
null = scan(CLEAN, True)
print('-- nhanh POSITIVE (15 ban da biet ro ri vs ADFECGDB that) --', flush=True)
pos = scan(sorted(LEAK), False)

def vals(d):
    return np.array([abs(v['ncc_cua_so_con']) for v in d.values()])


vc, vn, vp = vals(res), vals(null), vals(pos)
thr = float(np.max(vn))
n_vuot = int((vc > thr).sum())
out = dict(
    tieu_de='Quet chong lan MOT PHAN bang cua so con 10 s, CO DOI CHUNG (agent M4b)',
    muc_dich=('Loai kha nang mot ban CinC chi trung 10-30 s voi ADFECGDB roi bi NCC tren ca cua so 60 s '
              'pha loang. Quet cua so con co so sanh boi rat lon (60 ban x 4 kenh x 11 cua so x 25 kenh '
              'x moi do tre) nen KHONG co nguong tien nghiem -- phai lay nguong tu nhanh NULL.'),
    tham_so=dict(cua_so_s=WIN_S, buoc_truot_s=HOP_S, fs_ha_mau=FS,
                 kenh_adfecgdb='4 kenh bung + kenh dien cuc da dau (5 kenh x 5 ban ghi)',
                 nhanh_null='ADFECGDB dao nguoc thoi gian -- giu pho va cau truc chuoi QRS, pha huy moi trung khop that'),
    nhanh=dict(
        clean=dict(n=len(vc), max=round(float(vc.max()), 4), trung_vi=round(float(np.median(vc)), 4),
                   phan_vi_95=round(float(np.percentile(vc, 95)), 4)),
        null=dict(n=len(vn), max=round(float(vn.max()), 4), trung_vi=round(float(np.median(vn)), 4),
                  phan_vi_95=round(float(np.percentile(vn, 95)), 4)),
        positive=dict(n=len(vp), max=round(float(vp.max()), 4), min=round(float(vp.min()), 4),
                      trung_vi=round(float(np.median(vp)), 4))),
    nguong_tu_null=round(thr, 4),
    so_ban_sach_vuot_nguong_null=n_vuot,
    doi_chung_duong_dat=bool(vp.min() > 0.99),
    ket_luan=(('KHONG phat hien chong lan mot phan: %d/%d ban sach vuot nguong NULL %.4f; '
               'doi chung duong (15 ban da biet) deu >= %.4f'
               % (n_vuot, len(vc), thr, float(vp.min()))) if n_vuot == 0 else
              ('CO %d ban sach vuot nguong NULL %.4f -- phai kiem tay' % (n_vuot, thr))),
    canh_bao_dien_giai=('NCC cua so con o CA HAI nhanh clean va null deu cao (trung vi ~0,84) vi '
                        'hai chuoi QRS gia chu ky bat ky cung tu tuong quan manh o mot do tre nao do. '
                        'Con so tuyet doi cua nhanh clean KHONG doc duoc mot minh; chi so sanh voi NULL moi co nghia.'),
    tung_ban_ghi=dict(clean=res, null=null, positive=pos),
    phut=round((time.time() - t0) / 60, 1))
json.dump(out, open(os.path.join(HERE, 'dulieu_m4b_partial.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('=' * 40)
print('CLEAN    n=%d  max %.4f  trung vi %.4f' % (len(vc), vc.max(), np.median(vc)))
print('NULL     n=%d  max %.4f  trung vi %.4f   <- nguong' % (len(vn), vn.max(), np.median(vn)))
print('POSITIVE n=%d  min %.4f  max %.4f' % (len(vp), vp.min(), vp.max()))
print('so ban sach vuot nguong null:', n_vuot)
print(out['ket_luan'])
