# -*- coding: utf-8 -*-
"""M4b -- hoan tat nhiem vu M4:
  (1) KIEM DOC LAP chong lan ADFECGDB <-> CinC (viet lai tu dau, khong dung dulieu_audit.py)
  (2) tinh lai bang CHON KENH (M5) tren 60 ban ghi SACH
  (3) tong hop thi nghiem tang cuong / can bang (dulieu_exp.json)
Ghi vao analysis/dulieu_results.json  (cac khoa: kiem_doc_lap, chon_kenh_60_sach, thuc_nghiem)
Chay: python analysis/dulieu_m4b.py
"""
import os, sys, json
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
RES = os.path.join(HERE, 'dulieu_results.json')
LEAK = ['a03','a04','a05','a08','a12','a13','a14','a15','a17','a19','a20','a22','a23','a24','a25']
rng = np.random.default_rng(0); NB = 10000


def boot_ci(d):
    d = np.asarray(d, float)
    if len(d) < 2 or np.allclose(d, d[0]):
        return [float(d.mean()), float(d.mean())]
    bs = d[rng.integers(0, len(d), (NB, len(d)))].mean(1)
    return [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def wilcox(d):
    nz = np.asarray(d, float); nz = nz[nz != 0]
    return float(stats.wilcoxon(nz).pvalue) if len(nz) > 0 else 1.0


# ---------- (2) chon kenh tren 60 ban sach ----------
def chon_kenh_60():
    F = json.load(open(os.path.join(HERE, 'chonkenh_results.json'), encoding='utf-8'))['F1_tung_ban_ghi']['cinc']
    allr = sorted(F); clean = [t for t in allr if t not in LEAK]
    RULES = ['psd','peakprob','gate4','gate','rrcv','rrplaus','learned','fuse_k2','lead0','mean4','oracle']
    base = np.array([F[t]['psd'] for t in clean])
    out = {}
    for r in RULES:
        v60 = np.array([F[t][r] for t in clean]); v75 = np.array([F[t][r] for t in allr])
        d = v60 - base
        out[r] = dict(mean_60_sach=float(v60.mean()), mean_75_o_nhiem=float(v75.mean()),
                      median_60=float(np.median(v60)), ge90=int((v60 >= 90).sum()), lt50=int((v60 < 50).sum()),
                      hieu_vs_psd=float(d.mean()), ci95=boot_ci(d) if r != 'psd' else [0.0, 0.0],
                      wilcoxon_p=wilcox(d) if r != 'psd' else 1.0,
                      thang=int((d > 0).sum()), thua=int((d < 0).sum()), hoa=int((d == 0).sum()), n=len(clean))
    new = ['gate','gate4','rrcv','rrplaus','peakprob','learned','fuse_k2']
    ps = sorted((out[r]['wilcoxon_p'], r) for r in new); prev = 0.0
    for i, (p, r) in enumerate(ps):
        prev = min(1.0, max(prev, (len(ps) - i) * p)); out[r]['holm_p'] = prev
    du_dia = out['oracle']['mean_60_sach'] - out['psd']['mean_60_sach']
    for r in RULES:
        out[r]['phan_tram_du_dia_oracle'] = (100.0 * (out[r]['mean_60_sach'] - out['psd']['mean_60_sach']) / du_dia) if du_dia else None
    return dict(ban_ghi_sach=clean, du_dia_oracle=float(du_dia), bang=out,
                ghi_chu='Tinh lai bang M5 sau khi bo 15 ban ghi ro ri. Holm tren 7 quy tac moi. '
                        'Quy tac tien dang ky la GATE; PEAKPROB la hau kiem.')


# ---------- (3) thi nghiem tang cuong / can bang ----------
def thuc_nghiem():
    p = os.path.join(HERE, 'dulieu_exp.json')
    R = json.load(open(p, encoding='utf-8'))['runs']
    byfold = {}
    for k, v in R.items():
        byfold.setdefault(v['fold'], {})[v['arm']] = v
    def pairs(a, b):
        rows = []
        for f in sorted(byfold):
            if a in byfold[f] and b in byfold[f]:
                for s in byfold[f][a]['test_subjects']:
                    rows.append(dict(fold=f, chu_the=s, A=byfold[f][a]['F1_psd'][s], B=byfold[f][b]['F1_psd'][s],
                                     hieu=byfold[f][a]['F1_psd'][s] - byfold[f][b]['F1_psd'][s]))
        return rows
    out = {}
    for name, (a, b) in dict(tang_cuong_vs_khong=('base', 'noaug'), can_bang_vs_base=('bal', 'base')).items():
        rows = pairs(a, b)
        if not rows:
            out[name] = dict(trang_thai='chua co cap nao'); continue
        d = np.array([r['hieu'] for r in rows])
        nonceil = [r for r in rows if max(r['A'], r['B']) < 99.5]
        out[name] = dict(nhanh_A=a, nhanh_B=b, n_chu_the=len(rows), folds=sorted(set(r['fold'] for r in rows)),
                         tung_chu_the=rows, hieu_trung_binh=float(d.mean()), ci95=boot_ci(d), wilcoxon_p=wilcox(d),
                         thang=int((d > 0).sum()), thua=int((d < 0).sum()), hoa=int((d == 0).sum()),
                         n_chu_the_khong_o_tran=len(nonceil),
                         hieu_trung_binh_khong_o_tran=float(np.mean([r['hieu'] for r in nonceil])) if nonceil else None)
    out['giao_thuc'] = json.load(open(p, encoding='utf-8'))['meta']
    out['canh_bao'] = ('Quy mo nho hon san xuat (2 epoch, 1/3 doan, nguong co dinh 0.75) -- so TUYET DOI '
                       'KHONG so sanh duoc voi train_22.json; chi HIEU SO giua cac nhanh co nghia. '
                       'n rat nho -> cong suat thong ke rat thap.')
    return out


def main():
    res = json.load(open(RES, encoding='utf-8'))
    ver = json.load(open(os.path.join(HERE, 'dulieu_m4b_verify.json'), encoding='utf-8'))
    res['kiem_doc_lap'] = ver
    res['chon_kenh_60_sach'] = chon_kenh_60()
    res['thuc_nghiem'] = thuc_nghiem()
    json.dump(res, open(RES, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    print('-> ' + RES)
    print('chon kenh 60 sach: peakprob %+.2f  gate %+.2f' % (
        res['chon_kenh_60_sach']['bang']['peakprob']['hieu_vs_psd'],
        res['chon_kenh_60_sach']['bang']['gate']['hieu_vs_psd']))
    for k in ('tang_cuong_vs_khong', 'can_bang_vs_base'):
        t = res['thuc_nghiem'][k]
        if 'hieu_trung_binh' in t:
            print('%s: n=%d  hieu %+.2f  KTC [%+.2f;%+.2f]  p=%.3g' % (k, t['n_chu_the'], t['hieu_trung_binh'], t['ci95'][0], t['ci95'][1], t['wilcoxon_p']))


if __name__ == '__main__':
    main()
