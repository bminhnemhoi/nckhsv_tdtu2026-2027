# -*- coding: utf-8 -*-
"""
M2 -- KIEN TRUC: TCN co phai lua chon dung khong?  (dau doi dau o GIAO THUC HIEN HANH)

VAN DE: khao sat kien truc cu (pilot_evidence/arch_loro.py -> arch_loro_merged.json) do o giao thuc
CU (5 chu the, 20 ban ghi, leave-one-record-out, CUA SO 300 ms phan loai) va xep cnn_l (83.137 tham so,
macro F1 92,43) TREN tcn (63.105, 91,07); TOST cu (analysis/STATS.md) ghi cnn_l hon +0,73 KTC95
[+0,18;+1,22]. Nhung mo hinh san xuat la TCN 113k CHUOI-SANG-CHUOI tren 22 chu the. Hai bang do
KHONG so sanh truc tiep duoc. Script nay do lai TAT CA o mot giao thuc duy nhat.

GIAO THUC (chon va ly do):
  * Chia fold: lay logic K-FOLD THEO NHOM cua pilot_evidence/band_tcn.py (make_folds), KHONG lay
    make_folds cua model/train_22.py. Ly do: train_22 co dinh 11 fold (2 chu the test/fold) -> 11 lan
    huan luyen cho MOI kien truc, vuot xa ngan sach 150 phut. band_tcn cho dat so fold tuy y va van
    rai deu PhysioNet/B2/B1 vao cac fold. Dung 3 fold (nhiem vu yeu cau toi thieu 3).
  * Cham diem: lay cua model/train_22.py, KHONG lay cua band_tcn.py. Ly do: train_22 cham o 1000 Hz
    voi NHAN GOC (det*4 vs fq1000) thay vi ha xuong 250 Hz, va pick_threshold cua no tinh chuoi xac
    suat MOT LAN roi quet nguong (band_tcn tinh lai 13 lan -- lang phi thuan tuy).
  * Nhan B1 = meta['fqrs_all'] (ke ca nhip co=0), dung quy uoc train_22.py.
  * Kenh: quy tac PSD mu nhan (khong dung nhan) = so chinh; kem trung binh 4 kenh va oracle.
  * Nguong: quet 0,20..0,75 tren CHU THE VALIDATION rieng (toi da F1 trung binh 4 kenh), ap co dinh
    sang chu the test. Khong bao gio quet nguong tren test.

CONG BANG: moi kien truc nhan CUNG tap doan, CUNG so buoc toi uu, CUNG bo toi uu (AdamW 3e-3,
  weight_decay 1e-4), CUNG lich OneCycle, CUNG batch 32, CUNG seed, CUNG fold, CUNG nhan (tru bien
  the sigma vi do chinh la bien duoc khao sat). So tham so khop trong +/-3% (in ra trong log).

DA THU NHO QUY MO SO VOI SAN XUAT (bat buoc vi ngan sach 150 phut, 3 luong):
  * 3 fold thay vi 11  -> tap train ~14 chu the thay vi 20
  * stride doan train 4 s (gold) / 8 s (B1) thay vi 1 s / 2 s -> ~6k doan/fold thay vi 33k
  * 3 epoch batch 16 (train_22: 4 epoch batch 32) -- cung so mau trinh dien/epoch nhung GAP DOI so
    buoc toi uu voi cung thoi gian may (do: 19,4 vs 18,9 ms/mau). KHONG tang cuong du lieu.
  * ~1.140 buoc toi uu / fold so voi 4.168 buoc cua train_22 -> MOI mo hinh deu duoi-huan-luyen.
    Chieu lech nay LAM YEU DI khac biet giua cac kien truc (thien ve ket luan 'hoa nhau').
  => F1 tuyet doi SE THAP HON 97,56 cua mo hinh san xuat. Day la so sanh TUONG DOI giua cac kien truc
     o cung ngan sach, KHONG phai con so de bao cao ra ngoai.

Chay:
    python pilot_evidence/arch22.py --calibrate      # do toc do, uoc luong thoi gian, khong train
    python pilot_evidence/arch22.py                  # day du theo ngan sach
    python pilot_evidence/arch22.py --archs tcn,cnn_l --folds 3 --epochs 4
Xuat: pilot_evidence/arch22.json, arch22_log.txt
"""
import os, sys
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, time, math, argparse, importlib.util, datetime, platform, gc
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
from scipy import signal as sg
from scipy import stats as st

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
sys.path.insert(0, os.path.join(ROOT, 'model'))
from _paths import adfecgdb_dir                                          # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


M = _load('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py')); CFG = M.CFG
L = _load('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))

torch.set_num_threads(int(os.environ.get('FQRS_THREADS', 3)))

PHYSIO = ['r01', 'r04', 'r07', 'r08', 'r10']
B2 = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
B1 = [f'B1_{i:02d}' for i in range(1, 11)]
SUBJECTS = PHYSIO + B2 + B1
SCALP = set(PHYSIO + B2)
B2_DUP = {'B2_01': 'r01', 'B2_02': 'r10', 'B2_07': 'r04', 'B2_10': 'r07', 'B2_11': 'r08'}
HARD = ['B2_03', 'B1_07', 'B1_06']          # 3 ban kho da chot o vong truoc
LEADS = (1, 2, 3, 4)
FS = CFG['fs']; Q = CFG['fs_in'] // FS; SEG = CFG['seg']; TOL_MS = CFG['tolerance_ms']
STRIDE = {'PhysioNet': 1000, 'B2': 1000, 'B1': 2000}      # DA THU NHO (train_22: 250/250/500)
THR_GRID = np.arange(.20, .80, .05)
FHR_BAND = (1.8, 3.0)
CACHE = os.path.join(HERE, 'arch22_cache')

_LOG = None


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    if _LOG:
        _LOG.write(s + '\n'); _LOG.flush()


def group_of(t):
    return 'PhysioNet' if t.startswith('r') else t[:2]


# =================================================================== kien truc
def cbr(i, o, k, d=1):
    return nn.Sequential(nn.Conv1d(i, o, k, padding=(k // 2) * d, dilation=d, bias=False),
                         nn.BatchNorm1d(o), nn.GELU())


class TCN(nn.Module):
    """ho san xuat: TCN du dan gian no, chuoi-sang-chuoi (nguyen van M.FetalQRSTCN khi c=40,k=7,dils=1..16)"""

    def __init__(self, cin=2, c=40, k=7, dils=(1, 2, 4, 8, 16)):
        super().__init__()
        self.stem = cbr(cin, c, k)
        self.blocks = nn.ModuleList([nn.ModuleDict({
            'a': cbr(c, c, k, d),
            'b': nn.Sequential(nn.Conv1d(c, c, k, padding=(k // 2) * d, dilation=d, bias=False),
                               nn.BatchNorm1d(c))}) for d in dils])
        self.act = nn.GELU()
        self.out = nn.Conv1d(c, 1, 1)

    def forward(self, x):
        h = self.stem(x)
        for m in self.blocks:
            h = self.act(m['b'](m['a'](h)) + h)
        return self.out(h).squeeze(1)


class CNNL(nn.Module):
    """ho cnn_l cua bang cu (chong chap TRON, KHONG gian no, be rong tang dan) chuyen sang chuoi-sang-chuoi.
    Bo MaxPool cua ban goc (ban goc phan loai 1 cua so 300 ms; o day can 1 logit / mau)."""

    def __init__(self, cin=2, chans=(42, 84, 126, 168), ks=(7, 5, 3, 3)):
        super().__init__()
        Ls = []
        p = cin
        for c, k in zip(chans, ks):
            Ls.append(cbr(p, c, k)); p = c
        self.body = nn.Sequential(*Ls)
        self.out = nn.Conv1d(p, 1, 1)

    def forward(self, x):
        return self.out(self.body(x)).squeeze(1)


class UNet1D(nn.Module):
    """ho thu ba: U-Net 1D (ma hoa/giai ma co gop mau + noi tat). Dat truong tiep nhan lon bang GIAM MAU
    thay vi bang gian no -- day la con duong kien truc khac han hai ho tren."""

    def __init__(self, cin=2, w=18, ke=(7, 9, 9), kb=9, kd=5):
        super().__init__()
        c1, c2, c3, c4 = w, 2 * w, 3 * w, 4 * w
        self.e1 = cbr(cin, c1, ke[0]); self.e2 = cbr(c1, c2, ke[1]); self.e3 = cbr(c2, c3, ke[2])
        self.b = cbr(c3, c4, kb)
        self.d3 = cbr(c4 + c3, c3, kd); self.d2 = cbr(c3 + c2, c2, kd); self.d1 = cbr(c2 + c1, c1, kd)
        self.pool = nn.MaxPool1d(2)
        self.out = nn.Conv1d(c1, 1, 1)

    @staticmethod
    def _up(h, ref):
        h = F.interpolate(h, scale_factor=2, mode='linear', align_corners=False)
        return h[..., :ref.shape[-1]]

    def forward(self, x):
        n0 = x.shape[-1]
        pad = (-n0) % 8                       # 3 lan gop mau -> can boi so cua 8
        if pad:
            x = F.pad(x, (0, pad), mode='replicate')
        e1 = self.e1(x); e2 = self.e2(self.pool(e1)); e3 = self.e3(self.pool(e2))
        b = self.b(self.pool(e3))
        h = self.d3(torch.cat([self._up(b, e3), e3], 1))
        h = self.d2(torch.cat([self._up(h, e2), e2], 1))
        h = self.d1(torch.cat([self._up(h, e1), e1], 1))
        return self.out(h).squeeze(1)[..., :n0]


class TCNMS(nn.Module):
    """bien the DA THANG DO: 3 nhanh TCN song song, bo gian no khac nhau, noi kenh roi gop bang 1x1"""

    def __init__(self, cin=2, c=30, k=7, branches=((1, 2, 4), (2, 8, 16), (8, 16, 32))):
        super().__init__()
        self.branches = nn.ModuleList()
        for dils in branches:
            self.branches.append(nn.ModuleDict({
                'stem': cbr(cin, c, k),
                'blocks': nn.ModuleList([nn.ModuleDict({
                    'a': cbr(c, c, k, d),
                    'b': nn.Sequential(nn.Conv1d(c, c, k, padding=(k // 2) * d, dilation=d, bias=False),
                                       nn.BatchNorm1d(c))}) for d in dils])}))
        self.act = nn.GELU()
        self.out = nn.Conv1d(c * len(branches), 1, 1)

    def forward(self, x):
        hs = []
        for br in self.branches:
            h = br['stem'](x)
            for m in br['blocks']:
                h = self.act(m['b'](m['a'](h)) + h)
            hs.append(h)
        return self.out(torch.cat(hs, 1)).squeeze(1)


# ten -> (ham dung mo hinh, sigma nhan tinh bang MAU @250 Hz, mo ta)
ARCH = {
    # --- VIEC 1: ba ho kien truc, tham so khop ~113k
    'tcn':       (lambda: TCN(c=40, k=7, dils=(1, 2, 4, 8, 16)), 3.0,
                  'TCN gian no 5 khoi c=40 (mo hinh san xuat)'),
    'cnn_l':     (lambda: CNNL(), 3.0,
                  'cnn_l cua bang cu: chong chap tron, be rong tang dan, chuoi-sang-chuoi (RF nho)'),
    'cnn_wide':  (lambda: CNNL(chans=(12, 18, 22, 26), ks=(95, 95, 95, 95)), 3.0,
                  'cnn_l NHAN RONG: khong gian no nhung RF khop TCN -> tach bach "gian no" va "RF"'),
    'unet1d':    (lambda: UNet1D(w=18), 3.0,
                  'U-Net 1D 3 tang gop mau + noi tat'),
    # --- VIEC 2: bien the
    'rf_wide':   (lambda: TCN(c=37, k=7, dils=(1, 2, 4, 8, 16, 32)), 3.0,
                  'truong tiep nhan rong (~3,0 s)'),
    'rf_narrow': (lambda: TCN(c=45, k=7, dils=(1, 2, 4, 8)), 3.0,
                  'truong tiep nhan hep (~0,75 s)'),
    'tcn_ms':    (lambda: TCNMS(c=30), 3.0,
                  'da thang do: 3 nhanh gian no song song'),
    'sigma6':    (lambda: TCN(c=40, k=7, dils=(1, 2, 4, 8, 16)), 1.5,
                  'nhu tcn nhung ban do nhiet sigma 6 ms'),
    'sigma24':   (lambda: TCN(c=40, k=7, dils=(1, 2, 4, 8, 16)), 6.0,
                  'nhu tcn nhung ban do nhiet sigma 24 ms'),
}
RUN_ORDER = ['tcn', 'cnn_l', 'cnn_wide', 'unet1d', 'rf_narrow', 'rf_wide', 'tcn_ms', 'sigma6', 'sigma24']


def n_params(m):
    return sum(p.numel() for p in m.parameters())


def receptive_field(model, n=2001):
    """do truong tiep nhan THUC NGHIEM: so mau dau vao co gradient khac 0 tai dau ra o giua"""
    model = model.eval()
    x = torch.zeros(1, 2, n, requires_grad=True)
    y = model(x)
    y[0, n // 2].backward()
    g = x.grad.abs().sum(1)[0].numpy()
    nz = np.nonzero(g > 0)[0]
    return int(nz[-1] - nz[0] + 1) if len(nz) else 1


# =================================================================== du lieu
def psd_score(x250, fs=FS):
    e = np.abs(sg.hilbert(x250 - np.mean(x250))); e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def load_subject(tag):
    """-> dict lead -> (res f32 @250, x f32 @250, fq1000 int, psd float); giong train_22.load_subject"""
    import mne, wfdb
    g = group_of(tag)
    if g == 'PhysioNet':
        D = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        fq1000 = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, int)
        chans = {l: sig[l] for l in LEADS}
        del raw, sig
    else:
        sig, _, meta = L.load(tag)
        fq1000 = np.asarray(meta['fqrs_all'], int)
        chans = {l: sig[l - 1] for l in LEADS}
        del sig
    out = {}
    for l in LEADS:
        x250 = M.preprocess(chans[l], CFG['fs_in'], CFG)
        res, _ = M.cancel_maternal(x250, CFG)
        out[l] = (M.robust_scale(res).astype(np.float32), M.robust_scale(x250).astype(np.float32),
                  fq1000, psd_score(res))
    return out


def load_all(tags):
    os.makedirs(CACHE, exist_ok=True)
    D = {}
    t0 = time.time()
    for tag in tags:
        p = os.path.join(CACHE, tag + '.npz')
        if os.path.isfile(p):
            z = np.load(p)
            D[tag] = {l: (z[f'r{l}'], z[f'x{l}'], z['fq'], float(z[f'p{l}'])) for l in LEADS}
            src = 'cache'
        else:
            D[tag] = load_subject(tag)
            np.savez_compressed(p, fq=D[tag][1][2],
                                **{f'r{l}': D[tag][l][0] for l in LEADS},
                                **{f'x{l}': D[tag][l][1] for l in LEADS},
                                **{f'p{l}': D[tag][l][3] for l in LEADS})
            src = 'moi'
        n = len(D[tag][1][0])
        log(f'   {tag:<6} {group_of(tag):<9} {n / FS / 60:5.1f} phut  {len(D[tag][1][2]):5d} nhan  '
            f'[{src}] ({time.time() - t0:.0f}s)')
    return D


def make_heatmap(n, peaks, sigma):
    half = max(1, int(round(4 * sigma)))
    hm = np.zeros(n, np.float32)
    t = np.arange(n)
    for p in np.asarray(peaks, int):
        lo, hi = max(0, p - half), min(n, p + half + 1)
        if hi > lo:
            hm[lo:hi] = np.maximum(hm[lo:hi], np.exp(-((t[lo:hi] - p) ** 2) / (2 * sigma ** 2)))
    return hm


def make_heatmaps(D, sigma):
    out = {}
    for tag in D:
        fq250 = np.round(D[tag][1][2] / Q).astype(int)
        for l in LEADS:
            n = len(D[tag][l][0])
            f = fq250[(fq250 >= 0) & (fq250 < n)]
            out[(tag, l)] = make_heatmap(n, f, sigma)
    return out


def build_index(D, tags):
    idx = []
    for tag in tags:
        stz = STRIDE[group_of(tag)]
        for l in LEADS:
            n = len(D[tag][l][0])
            idx += [(tag, l, s) for s in range(0, n - SEG, stz)]
    return idx


def pos_weight_of(HM, idx):
    cs = {}
    neg = pos = 0
    for tag, l, s in idx:
        if (tag, l) not in cs:
            hm = HM[(tag, l)]
            cs[(tag, l)] = (np.concatenate([[0], np.cumsum(hm < .1)]),
                            np.concatenate([[0], np.cumsum(hm > .5)]))
        cn, cp = cs[(tag, l)]
        neg += cn[s + SEG] - cn[s]; pos += cp[s + SEG] - cp[s]
    return float(min(neg / max(pos, 1), 30.0))


def gather(D, HM, idx, sel):
    X = np.empty((len(sel), 2, SEG), np.float32)
    Y = np.empty((len(sel), SEG), np.float32)
    for k, j in enumerate(sel):
        tag, l, s = idx[j]
        X[k, 0] = D[tag][l][0][s:s + SEG]
        X[k, 1] = D[tag][l][1][s:s + SEG]
        Y[k] = HM[(tag, l)][s:s + SEG]
    return torch.from_numpy(X), torch.from_numpy(Y)


# =================================================================== huan luyen
def train(model, D, HM, idx, epochs, seed, pw_val, bs=16, lr=3e-3, max_steps=None):
    pw = torch.tensor([pw_val])
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    spe = math.ceil(len(idx) / bs)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, lr, epochs * spe)
    g = torch.Generator().manual_seed(seed)
    hist = []
    step = 0
    t0 = time.time()
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(len(idx), generator=g).tolist()
        tot = 0.
        nb = 0
        for i in range(0, len(idx), bs):
            X, Y = gather(D, HM, idx, perm[i:i + bs])
            loss = F.binary_cross_entropy_with_logits(model(X), Y, pos_weight=pw)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.); opt.step(); sch.step()
            tot += loss.item(); nb += 1; step += 1
            if max_steps and step >= max_steps:
                return hist, (time.time() - t0) / step
        hist.append(round(tot / max(nb, 1), 4))
        log(f'      epoch {ep + 1}/{epochs} loss {hist[-1]:.4f} '
            f'({time.time() - t0:.0f}s, {len(idx)} doan, pos_w {pw_val:.1f})')
    return hist, (time.time() - t0) / max(step, 1)


# =================================================================== suy luan / cham
@torch.no_grad()
def prob_series(model, r, x, bs=48):
    """nhu M.probability_series nhung GOP LO cac cua so (ket qua giong het, chi nhanh hon)"""
    model.eval()
    n = len(r)
    ov = CFG['overlap']
    stp = SEG - ov
    if n < SEG:
        r = np.pad(r, (0, SEG - n)); x = np.pad(x, (0, SEG - n))
    starts = list(range(0, max(len(r) - SEG, 0) + 1, stp))
    if starts and starts[-1] + SEG < len(r):
        starts.append(len(r) - SEG)
    acc = np.zeros(len(r)); cnt = np.zeros(len(r))
    for i in range(0, len(starts), bs):
        ss = starts[i:i + bs]
        W = np.stack([np.stack([r[s:s + SEG], x[s:s + SEG]]) for s in ss]).astype(np.float32)
        P = torch.sigmoid(model(torch.from_numpy(W))).numpy()
        for j, s in enumerate(ss):
            acc[s:s + SEG] += P[j]; cnt[s:s + SEG] += 1
    cnt[cnt == 0] = 1
    return (acc / cnt)[:n]


def score_lead(prob, fq1000, thr):
    det = M.pick_peaks(prob, thr, CFG).astype(np.int64) * Q
    m = M.match_events(det, fq1000, CFG['fs_in'], TOL_MS)
    m['n_det'] = int(len(det))
    return m


def probs_subject(model, D, tag):
    return {l: prob_series(model, D[tag][l][0], D[tag][l][1]) for l in LEADS}


def pick_threshold(model, D, tag):
    P = probs_subject(model, D, tag)
    best, bt = -1., .45
    for t in THR_GRID:
        f = float(np.mean([score_lead(P[l], D[tag][l][2], float(t))['F1'] for l in LEADS]))
        if f > best:
            best, bt = f, float(t)
    return bt, best


def eval_subject(model, D, tag, thr):
    P = probs_subject(model, D, tag)
    per = {l: score_lead(P[l], D[tag][l][2], thr) for l in LEADS}
    bl = max(LEADS, key=lambda l: D[tag][l][3])
    f1 = [per[l]['F1'] for l in LEADS]
    jt = [per[l]['jitter_ms'] for l in LEADS]
    return dict(record=tag, group=group_of(tag), psd_lead=int(bl), threshold=thr,
                F1_psd=per[bl]['F1'], Se_psd=per[bl]['Se'], PPV_psd=per[bl]['PPV'],
                jitter_psd=per[bl]['jitter_ms'], F1_mean4=float(np.mean(f1)),
                F1_oracle=float(max(f1)), jitter_mean4=float(np.nanmean(jt)),
                per_lead={f'A{l}': {k: per[l][k] for k in ('F1', 'Se', 'PPV', 'jitter_ms')}
                          for l in LEADS})


# =================================================================== fold
def make_folds(n_folds, seed=0):
    """K-fold theo NHOM -- logic band_tcn.make_folds (rai deu PhysioNet/B2/B1, val = chu the nhan da dau)"""
    rng = np.random.default_rng(seed)
    pools = {g: list(rng.permutation([s for s in SUBJECTS if group_of(s) == g]))
             for g in ('PhysioNet', 'B2', 'B1')}
    folds = [[] for _ in range(n_folds)]
    i = 0
    for g in ('PhysioNet', 'B2', 'B1'):
        for s in pools[g]:
            folds[i % n_folds].append(str(s)); i += 1
    val_pool = [str(s) for s in rng.permutation(sorted(SCALP))]
    out = []
    for k, test in enumerate(folds):
        test = sorted(str(s) for s in test)
        rest = [s for s in SUBJECTS if s not in test]
        val = next((s for s in val_pool if s in rest and s not in [o['val'] for o in out]), None)
        if val is None:
            val = next((s for s in rest if s in SCALP), rest[0])
        out.append(dict(fold=k + 1, test=test, val=str(val),
                        train=sorted(str(s) for s in rest if s != val)))
    return out


# =================================================================== thong ke
def cluster_bootstrap(d, n=20000, seed=0, lo=2.5, hi=97.5):
    d = np.asarray(d, float)
    rng = np.random.default_rng(seed)
    m = d[rng.integers(0, len(d), size=(n, len(d)))].mean(1)
    return float(d.mean()), float(np.percentile(m, lo)), float(np.percentile(m, hi))


def tost(d, margin=1.0):
    """TOST ghep cap: tuong duong neu CA HAI p mot phia < 0,05 (= KTC 90% nam gon trong +/-margin)"""
    d = np.asarray(d, float)
    n = len(d)
    sd = d.std(ddof=1) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n > 1 else 0.0
    if se == 0:
        return dict(p=0.0 if abs(d.mean()) < margin else 1.0,
                    equivalent=bool(abs(d.mean()) < margin),
                    ci90=[float(d.mean()), float(d.mean())], margin=margin)
    t_lo = (d.mean() + margin) / se
    t_hi = (d.mean() - margin) / se
    p_lo = float(st.t.sf(t_lo, n - 1))
    p_hi = float(st.t.cdf(t_hi, n - 1))
    p = max(p_lo, p_hi)
    h = float(st.t.ppf(.95, n - 1)) * se
    return dict(p=p, equivalent=bool(p < .05),
                ci90=[float(d.mean() - h), float(d.mean() + h)], margin=margin)


def compare(rows_a, rows_b, tags, key='F1_psd', seed=0):
    a = np.array([rows_a[t][key] for t in tags], float)
    b = np.array([rows_b[t][key] for t in tags], float)
    d = a - b
    mean, lo, hi = cluster_bootstrap(d, seed=seed)
    try:
        w = float(st.wilcoxon(a, b, zero_method='wilcox').pvalue) if np.any(d != 0) else 1.0
    except Exception:
        w = float('nan')
    return dict(n=len(tags), mean_diff=mean, ci95=[lo, hi], wilcoxon_p=w,
                n_win=int((d > 0).sum()), n_tie=int((d == 0).sum()), n_loss=int((d < 0).sum()),
                per_subject={t: float(x) for t, x in zip(tags, d)}, tost=tost(d))


# =================================================================== chinh
def main():
    global _LOG
    ap = argparse.ArgumentParser()
    ap.add_argument('--archs', default=','.join(RUN_ORDER))
    ap.add_argument('--folds', type=int, default=3)
    ap.add_argument('--epochs', type=int, default=3)
    ap.add_argument('--bs', type=int, default=16)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--budget', type=float, default=115., help='phut cho toan bo lan chay')
    ap.add_argument('--calibrate', action='store_true')
    ap.add_argument('--out', default=HERE)
    a = ap.parse_args()

    _LOG = open(os.path.join(a.out, 'arch22_log.txt'), 'a', encoding='utf-8')
    T0 = time.time()
    archs = [x.strip() for x in a.archs.split(',') if x.strip() in ARCH]
    folds = make_folds(a.folds, a.seed)

    log(f'\n===== M2 ARCH22 | {datetime.datetime.now():%Y-%m-%d %H:%M:%S} | seed {a.seed} | '
        f'{torch.get_num_threads()} luong | torch {torch.__version__} | {platform.platform()} =====')
    log(f'  22 chu the, {a.folds} fold theo nhom, {a.epochs} epoch, batch {a.bs}, AdamW 3e-3 OneCycle, '
        f'stride {STRIDE}, doan {SEG / FS:.0f}s, +/-{TOL_MS} ms, KHONG tang cuong')
    log(f'  kien truc: {archs}')
    log('\n  -- kiem tra can bang tham so va truong tiep nhan --')
    meta_arch = {}
    for k in archs:
        mdl = ARCH[k][0]()
        p = n_params(mdl)
        rf = receptive_field(mdl)
        meta_arch[k] = dict(params=p, rf_samples=rf, rf_ms=rf * 1000 / FS, sigma_samples=ARCH[k][1],
                            sigma_ms=ARCH[k][1] * 1000 / FS, desc=ARCH[k][2])
        log(f'    {k:<10} {p:>8,} tham so ({100 * (p / 113481 - 1):+5.1f}% so voi TCN 113.481)  '
            f'RF {rf:>4d} mau = {rf * 1000 / FS:6.0f} ms  sigma {ARCH[k][1] * 1000 / FS:.0f} ms | {ARCH[k][2]}')
        del mdl
    for f in folds:
        log(f"    fold {f['fold']}: test={f['test']} val={f['val']} n_train={len(f['train'])}")

    log('\n  nap 22 chu the ...')
    D = load_all(SUBJECTS)
    log(f'  xong {(time.time() - T0) / 60:.1f} phut')

    HM = {3.0: make_heatmaps(D, 3.0)}
    IDX = {f['fold']: build_index(D, f['train']) for f in folds}
    PW = {f['fold']: pos_weight_of(HM[3.0], IDX[f['fold']]) for f in folds}
    for f in folds:
        log(f"    fold {f['fold']}: {len(IDX[f['fold']])} doan train, pos_weight {PW[f['fold']]:.1f}")

    # ---- hieu chuan toc do
    log('\n  -- hieu chuan toc do (30 buoc moi kien truc) --')
    cal = {}
    for k in archs:
        torch.manual_seed(a.seed)
        _, ts = train(ARCH[k][0](), D, HM[3.0], IDX[folds[0]['fold']], 1, a.seed,
                      PW[folds[0]['fold']], bs=a.bs, max_steps=30)
        cal[k] = ts
        log(f'    {k:<10} {ts * 1000:6.0f} ms/buoc')
    t0 = time.time()
    _ = probs_subject(ARCH['tcn'][0]().eval(), D, 'B1_01')
    t_b1 = time.time() - t0
    log(f'    cham 1 chu the B1 (20 phut, 4 kenh) {t_b1:.0f}s')
    tot = 0.
    per_arch_est = {}
    for k in archs:
        s = 0.
        for f in folds:
            steps = a.epochs * math.ceil(len(IDX[f['fold']]) / a.bs)
            n_b1 = sum(1 for t in f['test'] if t.startswith('B1'))
            n_g = len(f['test']) - n_b1
            s += steps * cal[k] + (n_b1 + 0.25 * (n_g + 1)) * t_b1
        per_arch_est[k] = s / 60
        tot += s
    log(f'    DU KIEN: {tot / 60:.1f} phut cho {len(archs)} kien truc x {a.folds} fold '
        f'(ngan sach {a.budget:.0f} phut)')
    for k in archs:
        log(f'      {k:<10} ~{per_arch_est[k]:5.1f} phut')
    if a.calibrate:
        return

    # ---- chay
    RES = dict(meta=dict(date=str(datetime.datetime.now()), seed=a.seed, n_folds=a.folds,
                         epochs=a.epochs, batch_size=a.bs, stride=STRIDE, tolerance_ms=TOL_MS, subjects=SUBJECTS,
                         hard_subjects=HARD, excluded_duplicates=B2_DUP, folds=folds, arch=meta_arch,
                         ms_per_step={k: cal[k] * 1000 for k in cal}, threads=torch.get_num_threads(),
                         torch=torch.__version__, platform=platform.platform(),
                         protocol='fold=band_tcn.make_folds; cham=train_22 (1000 Hz, nhan goc); '
                                  'nguong tren chu the val rieng; kenh PSD mu nhan',
                         scale_down='3 fold (khong phai 11), stride 4s/8s (khong phai 1s/2s), '
                                    f'khong tang cuong, {a.epochs} epoch, batch {a.bs}'),
               runs={})
    outp = os.path.join(a.out, 'arch22.json')

    for k in archs:
        if (time.time() - T0) / 60 > a.budget:
            log(f'\n  HET NGAN SACH -> dung truoc khi chay {k}')
            break
        log(f'\n-- KIEN TRUC {k} ({meta_arch[k]["params"]:,} tham so, RF {meta_arch[k]["rf_ms"]:.0f} ms) --')
        tk = time.time()
        rows = {}
        finfo = {}
        sigma = ARCH[k][1]
        if sigma not in HM:
            HM[sigma] = make_heatmaps(D, sigma)
        for f in folds:
            tf = time.time()
            torch.manual_seed(a.seed)
            model = ARCH[k][0]()
            hist, _ = train(model, D, HM[sigma], IDX[f['fold']], a.epochs, a.seed, PW[f['fold']], bs=a.bs)
            model.eval()
            thr, vf1 = pick_threshold(model, D, f['val'])
            for t in f['test']:
                e = eval_subject(model, D, t, thr)
                e['fold'] = f['fold']; e['val'] = f['val']
                rows[t] = e
            log(f"    fold {f['fold']} val={f['val']} thr={thr:.2f} (valF1 {vf1:.2f}) -> " +
                ' '.join(f"{t}:{rows[t]['F1_psd']:.1f}" for t in f['test']) +
                f"  ({(time.time() - tf) / 60:.1f} phut)")
            finfo[f['fold']] = dict(threshold=thr, val_F1=vf1, loss=hist, val=f['val'],
                                    test=f['test'], minutes=(time.time() - tf) / 60)
            del model
            gc.collect()
        psd = np.array([rows[t]['F1_psd'] for t in SUBJECTS])
        m4 = np.array([rows[t]['F1_mean4'] for t in SUBJECTS])
        orc = np.array([rows[t]['F1_oracle'] for t in SUBJECTS])
        jt = np.array([rows[t]['jitter_psd'] for t in SUBJECTS])
        RES['runs'][k] = dict(arch=k, **meta_arch[k], rows=rows, folds=finfo,
                              macro_psd=float(psd.mean()), sd_psd=float(psd.std(ddof=1)),
                              macro_mean4=float(m4.mean()), sd_mean4=float(m4.std(ddof=1)),
                              macro_oracle=float(orc.mean()), jitter_psd=float(np.nanmean(jt)),
                              n_ge90=int((psd >= 90).sum()), n_lt50=int((psd < 50).sum()),
                              minutes=(time.time() - tk) / 60)
        log(f"  >> {k:<10} macro F1 (PSD) {psd.mean():6.2f} +- {psd.std(ddof=1):5.2f} | "
            f"TB4 {m4.mean():6.2f} | oracle {orc.mean():6.2f} | jitter {np.nanmean(jt):5.2f} ms | "
            f">=90: {int((psd >= 90).sum())}/22 | {(time.time() - tk) / 60:.1f} phut "
            f"| tong {(time.time() - T0) / 60:.1f} phut")
        json.dump(RES, open(outp, 'w'), indent=1, default=float)

    # ---- thong ke so sanh voi tcn
    if 'tcn' in RES['runs']:
        base = RES['runs']['tcn']['rows']
        easy = [t for t in SUBJECTS if t not in HARD]
        RES['comparisons'] = {}
        log('\n===== SO SANH VOI TCN (muc chu the, n=22, kenh PSD mu nhan) =====')
        for k in RES['runs']:
            if k == 'tcn':
                continue
            c = compare(RES['runs'][k]['rows'], base, SUBJECTS, 'F1_psd', a.seed)
            c_easy = compare(RES['runs'][k]['rows'], base, easy, 'F1_psd', a.seed)
            c_hard = compare(RES['runs'][k]['rows'], base, HARD, 'F1_psd', a.seed)
            c_m4 = compare(RES['runs'][k]['rows'], base, SUBJECTS, 'F1_mean4', a.seed)
            RES['comparisons'][k] = dict(all=c, easy19=c_easy, hard3=c_hard, mean4=c_m4)
            tt = c['tost']
            log(f"{k:<11}{c['mean_diff']:+7.2f} KTC95 [{c['ci95'][0]:+6.2f};{c['ci95'][1]:+6.2f}] "
                f"Wilcoxon p={c['wilcoxon_p']:.4f} T/H/B {c['n_win']}/{c['n_tie']}/{c['n_loss']}  "
                f"TOST p={tt['p']:.3f} {'TUONG DUONG' if tt['equivalent'] else 'chua ket luan'} "
                f"KTC90 [{tt['ci90'][0]:+.2f};{tt['ci90'][1]:+.2f}]")
            log(f"{'':11}  de19 {c_easy['mean_diff']:+6.2f} [{c_easy['ci95'][0]:+.2f};{c_easy['ci95'][1]:+.2f}] | "
                f"kho3 {c_hard['mean_diff']:+6.2f} [{c_hard['ci95'][0]:+.2f};{c_hard['ci95'][1]:+.2f}] | "
                f"TB4kenh {c_m4['mean_diff']:+6.2f} [{c_m4['ci95'][0]:+.2f};{c_m4['ci95'][1]:+.2f}]")

    RES['meta']['minutes'] = (time.time() - T0) / 60
    json.dump(RES, open(outp, 'w'), indent=1, default=float)
    log(f'\nDONE {RES["meta"]["minutes"]:.1f} phut -> {outp}')


if __name__ == '__main__':
    main()
