# -*- coding: utf-8 -*-
"""
CHOT SIEU THAM SO -- chay TRUOC khi cham mot ban ghi CinC nao.

QUY TAC CHON (khai bao truoc khi doc ket qua):
  * Be mat CHINH = `hpsim`: 22 chu the TRONG MIEN, nhan trong mien, moi ban ghi bi lam
    suy bien theo DUNG ba dich chuyen do duoc o VIEC 1 (cat 60 s, luong tu 10,13 bit,
    bom dien luoi 60 Hz den ti so 1,64). Chon cau hinh co F1 trung binh cao nhat.
  * Be mat PHU = `hp`: mo hinh 12 chu the -> 10 chu the Silesia B1 (dich chuyen he ghi THAT,
    nhung m12 da gan tran tren B1 nen it thong tin). Chi bao cao, khong quyet dinh.
  * Khong mot mau nao cua CinC 2013 tham gia vao buoc nay.
Ra: adapt/hp_selected.json
"""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import adapt_common as A
from adapt_run import GRID, SIM

HERE = os.path.dirname(os.path.abspath(__file__))


def merge(stage):
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'shard_%s_*.json' % stage))):
        out.update(json.load(open(f, encoding='utf-8')))
    return out


def main():
    sim = merge('hpsim')
    b1 = merge('hp')
    rows = [w for v in sim.values() for w in v]
    keys = sorted({k for r in rows for k in r})
    sim_mean = {k: float(np.mean([r[k] for r in rows if k in r])) for k in keys}
    sim_n = len(rows)
    b1_mean = {k: float(np.mean([v[k] for v in b1.values()])) for k in (sorted(list(b1.values())[0]) if b1 else [])}

    # Be mat mo phong (hpsim) DA BI HUY vi vuot ngan sach tinh toan (245 s/chu the, xem
    # adapt/THICHNGHI muc han che). Be mat quyet dinh thuc te la `hp`: m12 -> Silesia B1.
    surf = b1_mean if b1_mean else sim_mean
    surf_name = 'hp_m12_to_B1' if b1_mean else 'hpsim'

    def pick(prefix, grid):
        v = [surf['%s%d' % (prefix, j)] for j in range(len(grid))]
        best = max(v)
        # hoa trong 0,05 diem -> chon cau hinh THAN TRONG hon (toc do hoc nho hon)
        cand = [j for j, x in enumerate(v) if best - x <= 0.05]
        return min(cand, key=lambda j: grid[j].get('lr', 0)), v

    tent_i, tent_v = pick('tent', GRID['tent'])
    pl_i, pl_v = pick('pl', GRID['pl'])
    sel = dict(adabn=dict(), tent=GRID['tent'][tent_i], pl=GRID['pl'][pl_i])

    out = dict(
        quy_tac_chon=('be mat quyet dinh = hp_m12_to_B1: mo hinh 12 chu the (chua tung thay Silesia B1) '
                      'thich nghi sang 10 chu the B1. Chon cau hinh co F1 trung binh cao nhat; '
                      'hoa trong 0,05 diem thi chon toc do hoc nho hon. '
                      'KHONG dung bat ky mau nao cua CinC 2013.'),
        mo_phong=SIM, grid=GRID, selected=sel,
        selected_index=dict(tent=tent_i, pl=pl_i), be_mat_quyet_dinh=surf_name,
        hpsim_bi_huy=('be mat mo phong bi dung giua chung vi 245 s/chu the vuot ngan sach 150 phut; '
                      'anh huong duoc bao cao o muc han che'),
        surface_hpsim=dict(n_cua_so=sim_n, n_chu_the=len(sim), mean_F1=sim_mean, per_subject=sim),
        surface_b1_m12=dict(n_chu_the=len(b1), mean_F1=b1_mean, per_subject=b1,
                            ghi_chu='m12 da dat ~99,7 tren B1 -> gan nhu khong con du dia, chi de tham khao'))
    json.dump(out, open(os.path.join(HERE, 'hp_selected.json'), 'w', encoding='utf-8'), indent=1)

    print('=== be mat QUYET DINH: %s (%d chu the) ===' % (surf_name, len(b1) or len(sim)))
    for k in sorted(surf):
        print('  %-8s %6.2f  %s' % (k, surf[k], '<== CHON' if k in ('tent%d' % tent_i, 'pl%d' % pl_i) else ''))
    if sim_n:
        print('=== be mat mo phong (khong day du, %d cua so) ===' % sim_n)
        for k in sorted(sim_mean):
            print('  %-8s %6.2f' % (k, sim_mean[k]))
    print('\nDA CHOT: tent=%s' % json.dumps(sel['tent']))
    print('DA CHOT: pl  =%s' % json.dumps(sel['pl']))


if __name__ == '__main__':
    main()
