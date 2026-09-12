# -*- coding: utf-8 -*-
"""VIEC 3 + VIEC 4 -- thi nghiem doi chung THU NHO, ba nhanh cung giao thuc:
    base  = tang cuong BAT,  chi so goc (B1 chiem ~63 % so doan)
    noaug = tang cuong TAT,  chi so goc
    bal   = tang cuong BAT,  chi so CAN BANG theo SO NHIP giua ba nguon (PhysioNet / B1 / B2)

Giao thuc M4-mini (khai bao TRUOC khi chay, KHONG doi sau khi thay ket qua):
    - cung 11 fold nhom chu the cua train_22.py, chi chay cac fold duoc chon
    - lay mau chi so train: giu 1/KEEP doan (mac dinh 1/3) -> giam chi phi, GIU NGUYEN ty le nguon
    - epochs giam (mac dinh 2), nguong CO DINH = 0,75 (nguong production train_22) cho CA BA nhanh
      -> khong tim nguong tren val, nen ba nhanh khac nhau DUY NHAT o phep tang cuong / can bang
    - cham o muc CHU THE: F1 quy tac PSD mu nhan (so chinh) + F1 trung binh 4 kenh
CANH BAO: quy mo nho hon san xuat (2 epoch, 1/3 du lieu) nen SO TUYET DOI THAP HON train_22.json
va KHONG so sanh truc tiep duoc; chi so SANH GIUA BA NHANH la co y nghia.

Chay: python analysis/dulieu_exp.py --folds 1,2,3,4 --epochs 2 --keep 3 --arms base,noaug,bal
Ket qua: analysis/dulieu_exp.json (ghi tang dan sau moi fold), analysis/dulieu_exp_log.txt
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('FQRS_THREADS', '2')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, argparse, importlib.util, datetime, platform
import numpy as np, torch

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


T = _load('train22', os.path.join(ROOT, 'model', 'train_22.py'))
M = T.M
OUT = os.path.join(HERE, 'dulieu_exp.json')
LOG = open(os.path.join(HERE, 'dulieu_exp_log.txt'), 'a', encoding='utf-8')


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + '\n'); LOG.flush()


def beats_per_segment(D, HM, idx):
    """so nhip nhan trong tung doan (dem tam heatmap > 0,5 roi chia do rong)."""
    cs = {}
    out = np.empty(len(idx), np.float64)
    for k, (tag, lead, s) in enumerate(idx):
        if (tag, lead) not in cs:
            fq = D[tag][lead][2]
            c = np.zeros(len(D[tag][lead][0]) + 1)
            v = fq[(fq >= 0) & (fq < len(c) - 1)]
            np.add.at(c, v + 1, 1.0)
            cs[(tag, lead)] = np.cumsum(c)
        c = cs[(tag, lead)]
        out[k] = c[min(s + T.SEG, len(c) - 1)] - c[s]
    return out


def balance_index(D, HM, idx, seed=0):
    """Lay mau lai chi so sao cho TONG SO NHIP cua ba nguon bang nhau, giu nguyen tong so doan."""
    rng = np.random.default_rng(seed)
    b = beats_per_segment(D, HM, idx)
    grp = np.array([T.group_of(t) for t, _, _ in idx])
    groups = sorted(set(grp))
    n_total = len(idx)
    target_beats = b.sum() / len(groups)
    out = []
    stats = {}
    for g in groups:
        m = np.where(grp == g)[0]
        mean_b = b[m].mean()
        n_take = int(round(target_beats / mean_b))
        pick = rng.choice(m, size=n_take, replace=n_take > len(m))
        out.append(pick)
        stats[g] = dict(n_goc=int(len(m)), n_moi=int(n_take), nhip_goc=float(b[m].sum()),
                        nhip_moi=float(mean_b * n_take), replace=bool(n_take > len(m)))
    sel = np.concatenate(out)
    rng.shuffle(sel)
    # giu tong so doan ~ nhu goc de so buoc/epoch khong doi
    if len(sel) > n_total:
        sel = sel[:n_total]
    return [idx[i] for i in sel], stats


def run_arm(arm, folds, D, HM, epochs, keep, thr, seed, res):
    for f in folds:
        key = '%s_f%02d' % (arm, f['fold'])
        if key in res['runs']:
            log('   bo qua (da co) ' + key); continue
        idx = T.build_index(D, f['train'])[::keep]
        stats = None
        if arm == 'bal':
            idx, stats = balance_index(D, HM, idx, seed)
        torch.manual_seed(seed)
        model = M.FetalQRSTCN()
        t0 = time.time()
        hist, tstep = T.train(model, D, HM, idx, epochs, seed, augment=(arm != 'noaug'))
        model.eval()
        test = {}
        for tag in f['test']:
            with torch.no_grad():
                test[tag] = T.eval_subject_full(model, D, tag, thr)
        res['runs'][key] = dict(arm=arm, fold=f['fold'], test_subjects=f['test'], n_segments=len(idx),
                                epochs=epochs, keep=keep, threshold=thr, loss=hist, ms_per_step=tstep * 1000,
                                minutes=(time.time() - t0) / 60.0, balance_stats=stats,
                                F1_psd={k: v['F1_psd'] for k, v in test.items()},
                                F1_mean4={k: v['F1_mean4'] for k, v in test.items()},
                                detail=test)
        json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
        log('   %-14s %s  F1_psd %s  (%.1f phut)' % (key, f['test'],
            {k: round(v, 2) for k, v in res['runs'][key]['F1_psd'].items()}, res['runs'][key]['minutes']))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--folds', default='1,2,3,4')
    ap.add_argument('--epochs', type=int, default=2)
    ap.add_argument('--keep', type=int, default=3)
    ap.add_argument('--thr', type=float, default=0.75)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--arms', default='base,noaug,bal')
    ap.add_argument('--calibrate', action='store_true')
    a = ap.parse_args()
    log('\n===== M4-mini | %s | threads %d | epochs %d | keep 1/%d | thr %.2f | arms %s ====='
        % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), torch.get_num_threads(), a.epochs, a.keep,
           a.thr, a.arms))
    allf = T.make_folds(a.seed)
    sel = [int(x) for x in a.folds.split(',') if x]
    folds = [f for f in allf if f['fold'] in sel]
    log('nap 22 chu the ...')
    D = T.load_all(T.ALL)
    HM = T.make_heatmaps(D, T.ALL)
    res = json.load(open(OUT, encoding='utf-8')) if os.path.isfile(OUT) else dict(runs={})
    res['meta'] = dict(date=str(datetime.datetime.now()), epochs=a.epochs, keep=a.keep, threshold=a.thr,
                       seed=a.seed, folds=sel, arms=a.arms.split(','), threads=torch.get_num_threads(),
                       torch=torch.__version__, platform=platform.platform(),
                       protocol='M4-mini: 1/%d doan, %d epoch, nguong CO DINH %.2f cho ca ba nhanh; '
                                'KHONG so sanh truc tiep voi train_22.json' % (a.keep, a.epochs, a.thr))
    if a.calibrate:
        idx = T.build_index(D, folds[0]['train'])[::a.keep]
        torch.manual_seed(a.seed)
        _, ts = T.train(M.FetalQRSTCN(), D, HM, idx, 1, a.seed, True, max_steps=20)
        torch.manual_seed(a.seed)
        _, ts = T.train(M.FetalQRSTCN(), D, HM, idx, 1, a.seed, True, max_steps=30)
        nst = int(np.ceil(len(idx) / 32))
        t0 = time.time()
        with torch.no_grad():
            T.eval_subject_full(M.FetalQRSTCN().eval(), D, 'B1_01', a.thr)
        te = time.time() - t0
        tot = (len(folds) * len(a.arms.split(',')) * (nst * a.epochs * ts + 2 * te)) / 60
        log('   %.0f ms/buoc, %d buoc/epoch, eval B1 %.0fs -> du kien TONG %.1f phut' % (ts * 1000, nst, te, tot))
        return
    # duyet theo FOLD truoc roi den nhanh: neu bi cat ngang van co cac fold DU CA BA NHANH de so sanh
    for f in folds:
        log('-- fold %02d  test %s --' % (f['fold'], f['test']))
        for arm in a.arms.split(','):
            run_arm(arm, [f], D, HM, a.epochs, a.keep, a.thr, a.seed, res)
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    log('-> ' + OUT)


if __name__ == '__main__':
    main()
