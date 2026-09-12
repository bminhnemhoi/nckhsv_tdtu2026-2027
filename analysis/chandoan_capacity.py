# -*- coding: utf-8 -*-
"""
NHIEM VU M1 -- VIEC 2: TRAN NANG LUC.  Mo hinh THIEU hay THUA nang luc?

Hai phep thu:
  A. TRONG MAU O QUY MO THAT: checkpoint production_22 duoc huan luyen tren CA 22 chu the.
     Danh gia no tren chinh 22 chu the do = TRONG MAU. So voi LOSO (eval_22.json).
     Neu trong mau ~ ngoai mau  -> mo hinh KHONG hoc thuoc noi du lieu cua chinh no -> thieu nang luc / thieu toi uu.
     Neu trong mau >> ngoai mau -> van de la TONG QUAT HOA, khong phai nang luc.
  B. PHEP THU HOC THUOC: huan luyen lai tu dau tren 4 chu the (2 de + 2 kho), KHONG tang cuong,
     nhieu epoch hon, roi do F1 TRONG MAU tren chinh 4 chu the do. Lam voi 2 be rong kenh
     (40 = kien truc san xuat, 80 = gap ~4 lan tham so) de xem tang nang luc co giup khong.

Chay:  python analysis/chandoan_capacity.py --epochs 12
Ket qua: analysis/chandoan_capacity.json, analysis/chandoan_capacity_log.txt
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, math, argparse, importlib.util, datetime, gc
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
import mne, wfdb
from scipy import signal as sg

torch.set_num_threads(int(os.environ.get('FQRS_THREADS', 2)))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
from _paths import adfecgdb_dir


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


M = _load('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py')); CFG = M.CFG
L = _load('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))

CKPT = os.path.join(ROOT, 'model', 'checkpoints')
OUT_JSON = os.path.join(HERE, 'chandoan_capacity.json')
EVAL22 = os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json')
PHYSIONET = ['r01', 'r04', 'r07', 'r08', 'r10']
B1 = [f'B1_{i:02d}' for i in range(1, 11)]
B2 = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
ALL22 = PHYSIONET + B1 + B2
LEADS = (1, 2, 3, 4); SEG = CFG['seg']; Q = CFG['fs_in'] // CFG['fs']
# buoc truot 2 s cho MOI nhom (train_22 dung 1 s cho B2/PhysioNet). It doan hon -> DE hoc thuoc hon,
# tuc la thien ve phia 'mo hinh du nang luc'; neu van khong hoc thuoc duoc thi ket luan cang manh.
STRIDE = {'PhysioNet': 500, 'B2': 500, 'B1': 500}
TOL_MS = 50; FHR_BAND = (1.8, 3.0)
THR_GRID = np.arange(.20, .80, .05)
SUBSET = ['r01', 'B2_12', 'B2_03', 'B1_07']      # 2 de + 2 kho; KHAI BAO TRUOC KHI CHAY


class Tee:
    def __init__(self, path):
        self.f = open(path, 'w', encoding='utf-8'); self.o = sys.stdout
    def write(self, s): self.o.write(s); self.f.write(s); self.f.flush()
    def flush(self): self.o.flush(); self.f.flush()


def group_of(tag): return 'PhysioNet' if tag.startswith('r') else tag[:2]


def psd_score(x250, fs=250):
    e = np.abs(sg.hilbert(x250 - np.mean(x250))); e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def load_subject(tag):
    g = group_of(tag)
    if g == 'PhysioNet':
        D = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        fq1000 = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, int)
        chans = {l: sig[l] for l in LEADS}; del raw, sig
    else:
        sig, _, mt = L.load(tag)
        fq1000 = np.asarray(mt['fqrs_all'], int)
        chans = {l: sig[l - 1] for l in LEADS}; del sig
    fq250 = np.round(fq1000 / Q).astype(int)
    out = {}
    for l in LEADS:
        x = M.preprocess(chans[l], CFG['fs_in'], CFG)
        r, _ = M.cancel_maternal(x, CFG)
        out[l] = (M.robust_scale(r).astype(np.float32), M.robust_scale(x).astype(np.float32),
                  fq250, fq1000, psd_score(r))
    del chans
    return out


def score_lead(prob, fq1000, thr):
    det = M.pick_peaks(prob, thr, CFG).astype(np.int64) * Q
    m = M.match_events(det, fq1000, CFG['fs_in'], TOL_MS)
    m['n_det'] = int(len(det)); m['n_ref'] = int(len(fq1000))
    return m


def eval_subject(model, D, tag, thr):
    per = {}
    for l in LEADS:
        p = M.probability_series(model, D[tag][l][0], D[tag][l][1], CFG)
        per[l] = score_lead(p, D[tag][l][3], thr)
    bl = max(LEADS, key=lambda l: D[tag][l][4])
    f1s = [per[l]['F1'] for l in LEADS]
    return dict(record=tag, psd_lead=int(bl), per_lead={f'A{l}': per[l] for l in LEADS},
                F1_psd=per[bl]['F1'], F1_mean4=float(np.mean(f1s)), F1_oracle=float(max(f1s)))


def pick_thr_insample(model, D, tags):
    P = {(t, l): M.probability_series(model, D[t][l][0], D[t][l][1], CFG) for t in tags for l in LEADS}
    best, bt = -1, .45
    for thr in THR_GRID:
        f = float(np.mean([score_lead(P[(t, l)], D[t][l][3], float(thr))['F1'] for t in tags for l in LEADS]))
        if f > best: best, bt = f, float(thr)
    return bt, best


def build_index(D, tags):
    idx = []
    for tag in tags:
        st = STRIDE[group_of(tag)]
        for l in LEADS:
            n = len(D[tag][l][0])
            idx += [(tag, l, s) for s in range(0, n - SEG, st)]
    return idx


def pos_weight_of(HM, idx):
    cs = {}; neg = pos = 0
    for tag, lead, s in idx:
        if (tag, lead) not in cs:
            hm = HM[(tag, lead)]
            cs[(tag, lead)] = (np.concatenate([[0], np.cumsum(hm < .1)]), np.concatenate([[0], np.cumsum(hm > .5)]))
        cn, cp = cs[(tag, lead)]
        neg += cn[s + SEG] - cn[s]; pos += cp[s + SEG] - cp[s]
    return float(min(neg / max(pos, 1), 30.0))


def gather(D, HM, idx, sel):
    X = np.empty((len(sel), 2, SEG), np.float32); Y = np.empty((len(sel), SEG), np.float32)
    for k, j in enumerate(sel):
        tag, lead, s = idx[j]
        X[k, 0] = D[tag][lead][0][s:s + SEG]; X[k, 1] = D[tag][lead][1][s:s + SEG]
        Y[k] = HM[(tag, lead)][s:s + SEG]
    return torch.from_numpy(X), torch.from_numpy(Y)


def train_nofaug(model, D, HM, idx, epochs, seed=0, bs=32, lr=3e-3):
    pw = torch.tensor([pos_weight_of(HM, idx)])
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    spe = math.ceil(len(idx) / bs)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, lr, epochs * spe)
    g = torch.Generator().manual_seed(seed)
    hist = []; t0 = time.time()
    for ep in range(epochs):
        model.train(); perm = torch.randperm(len(idx), generator=g).tolist(); tot = 0.; nb = 0
        for i in range(0, len(idx), bs):
            X, Y = gather(D, HM, idx, perm[i:i + bs])
            loss = F.binary_cross_entropy_with_logits(model(X), Y, pos_weight=pw)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.); opt.step(); sch.step()
            tot += loss.item(); nb += 1
        hist.append(tot / max(1, nb))
        print(f'      epoch {ep + 1}/{epochs} loss {hist[-1]:.4f}  ({time.time() - t0:.0f}s, {len(idx)} doan, pos_w {pw.item():.1f})', flush=True)
    return hist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--epochs', type=int, default=12)
    ap.add_argument('--skip-a', action='store_true')
    ap.add_argument('--skip-b', action='store_true')
    ap.add_argument('--widths', default='40,80')
    a = ap.parse_args()
    sys.stdout = Tee(os.path.join(HERE, 'chandoan_capacity_log.txt'))
    t0 = time.time()
    print(f'chandoan_capacity.py {datetime.datetime.now():%Y-%m-%d %H:%M:%S} torch {torch.__version__} threads {torch.get_num_threads()}')
    out = dict(meta=dict(date=str(datetime.datetime.now()), epochs=a.epochs, subset=SUBSET,
                         note='B: khong tang cuong, nguong chon TRONG MAU -> F1 trong mau la CHAN TREN'))

    # ---------------------------------------------------------------- A
    if not a.skip_a:
        print('\n=== A. production_22 TREN CHINH 22 CHU THE DA HUAN LUYEN (trong mau) ===')
        b = torch.load(os.path.join(CKPT, 'fetalqrs_tcn_22_production.pt'), map_location='cpu', weights_only=False)
        net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
        thr = float(b['threshold'])
        ev = json.load(open(EVAL22, encoding='utf-8'))
        rows = {}
        print(f'   nguong {thr:.2f}; n tham so {M.n_params(net)}')
        print(f'   {"chu the":<8}{"trong mau PSD":>15}{"LOSO PSD":>10}{"hieu":>8}{"trong mau TB4":>15}{"LOSO TB4":>10}')
        for tag in ALL22:
            D = {tag: load_subject(tag)}
            e = eval_subject(net, D, tag, thr)
            lo = ev['subjects'][tag]['model_22']
            e['loso_F1_psd'] = lo['F1_psd']; e['loso_F1_mean4'] = lo['F1_mean4']; e['loso_F1_oracle'] = lo['F1_oracle']
            rows[tag] = e
            print(f'   {tag:<8}{e["F1_psd"]:>15.2f}{lo["F1_psd"]:>10.2f}{e["F1_psd"] - lo["F1_psd"]:>+8.2f}'
                  f'{e["F1_mean4"]:>15.2f}{lo["F1_mean4"]:>10.2f}', flush=True)
            del D; gc.collect()
        ins = np.array([rows[t]['F1_psd'] for t in ALL22]); los = np.array([rows[t]['loso_F1_psd'] for t in ALL22])
        ins4 = np.array([rows[t]['F1_mean4'] for t in ALL22]); los4 = np.array([rows[t]['loso_F1_mean4'] for t in ALL22])
        out['A_insample_22'] = dict(threshold=thr, n_params=int(M.n_params(net)), records=rows,
                                    mean_insample_psd=float(ins.mean()), mean_loso_psd=float(los.mean()),
                                    gap_psd=float((ins - los).mean()),
                                    mean_insample_mean4=float(ins4.mean()), mean_loso_mean4=float(los4.mean()),
                                    gap_mean4=float((ins4 - los4).mean()),
                                    n_insample_ge99=int((ins >= 99).sum()), n_loso_ge99=int((los >= 99).sum()))
        print(f'\n   TRONG MAU PSD {ins.mean():.2f}  |  LOSO PSD {los.mean():.2f}  |  khoang cach {(ins - los).mean():+.2f} diem')
        print(f'   TRONG MAU TB4 {ins4.mean():.2f}  |  LOSO TB4 {los4.mean():.2f}  |  khoang cach {(ins4 - los4).mean():+.2f} diem')
        del net; gc.collect()

    # ---------------------------------------------------------------- B
    if not a.skip_b:
        print(f'\n=== B. PHEP THU HOC THUOC tren {SUBSET} ({a.epochs} epoch, KHONG tang cuong) ===')
        D = {t: load_subject(t) for t in SUBSET}
        HM = {(t, l): M.make_heatmap(len(D[t][l][0]), D[t][l][2]) for t in SUBSET for l in LEADS}
        idx = build_index(D, SUBSET)
        print(f'   {len(idx)} doan train, {math.ceil(len(idx) / 32)} buoc/epoch')
        out['B_memorise'] = dict(n_segments=len(idx), subset=SUBSET, epochs=a.epochs, models={})
        for w in [int(x) for x in a.widths.split(',')]:
            torch.manual_seed(0); np.random.seed(0)
            net = M.FetalQRSTCN(c=w)
            npar = M.n_params(net)
            print(f'   -- be rong {w} kenh, {npar} tham so --')
            hist = train_nofaug(net, D, HM, idx, a.epochs, seed=0)
            net.eval()
            thr, f1m = pick_thr_insample(net, D, SUBSET)
            rows = {t: eval_subject(net, D, t, thr) for t in SUBSET}
            per = [rows[t]['per_lead'][f'A{l}']['F1'] for t in SUBSET for l in LEADS]
            print(f'      nguong trong mau {thr:.2f}; F1 TRONG MAU trung binh tren 16 (chu the x kenh) {np.mean(per):.2f}')
            for t in SUBSET:
                print(f'      {t:<8} PSD {rows[t]["F1_psd"]:6.2f}  TB4 {rows[t]["F1_mean4"]:6.2f}  oracle {rows[t]["F1_oracle"]:6.2f}  '
                      + ' '.join(f'A{l}:{rows[t]["per_lead"][f"A{l}"]["F1"]:.1f}' for l in LEADS))
            out['B_memorise']['models'][str(w)] = dict(width=w, n_params=int(npar), loss_hist=hist, threshold=thr,
                                                       F1_insample_lead_mean=float(np.mean(per)),
                                                       F1_insample_mean4=float(np.mean([rows[t]['F1_mean4'] for t in SUBSET])),
                                                       F1_insample_psd=float(np.mean([rows[t]['F1_psd'] for t in SUBSET])),
                                                       records=rows)
            del net; gc.collect()
        del D, HM; gc.collect()

    out['meta']['minutes'] = (time.time() - t0) / 60
    json.dump(out, open(OUT_JSON, 'w', encoding='utf-8'), indent=1, default=float)
    print(f'\nDONE {out["meta"]["minutes"]:.1f} phut -> {OUT_JSON}')


if __name__ == '__main__':
    main()
