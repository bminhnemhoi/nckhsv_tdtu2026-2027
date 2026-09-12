# -*- coding: utf-8 -*-
"""
Lop dung chung cho M3 -- thich nghi mien khong nhan (unsupervised domain adaptation).

QUY TAC LIEM CHINH DUOC MA HOA TRONG TEP NAY:
  * Nhan cua CinC 2013 (<rec>.fqrs) CHI duoc doc trong ham score() o buoc cham diem cuoi cung.
    Khong mot ham thich nghi nao trong tep nay nhan tham so nhan that.
  * Moi sieu tham so thich nghi duoc chot trong HP (ben duoi) TRUOC khi chay tren CinC,
    va duoc chon tren 22 chu the TRONG MIEN (xem adapt_run.py --stage hp).
"""
import os, sys
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
import json, copy, importlib.util
import numpy as np, torch, torch.nn as nn
from scipy import signal as sg

torch.set_num_threads(int(os.environ.get('FQRS_THREADS', 1)))

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
from _paths import cinc2013_dir, adfecgdb_dir, checkpoint          # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


M = _load('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py')); CFG = M.CFG
L = _load('silesia_loader', os.path.join(ROOT, 'model', 'silesia_loader.py'))

TOL_MS = 50
FHR_BAND = (1.8, 3.0)
Q = CFG['fs_in'] // CFG['fs']
LEADS = (1, 2, 3, 4)
BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')   # khai bao truoc, Behar/Oster/Clifford 2013
PROD22 = 'fetalqrs_tcn_22_production.pt'

# 22 chu the trong mien (cung danh sach train_22.py / eval_22.py)
PHYSIONET = ['r01', 'r04', 'r07', 'r08', 'r10']
B1 = ['B1_%02d' % i for i in range(1, 11)]
B2 = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
ALL22 = PHYSIONET + B1 + B2

# ------------------------------------------------------------------ SIEU THAM SO
# Gia tri mac dinh; giai doan --stage hp chay tren 22 chu the TRONG MIEN se ghi de
# va ket qua duoc chot vao adapt/hp_selected.json TRUOC khi chay CinC.
HP = dict(
    adabn=dict(),                                  # khong co sieu tham so
    tent=dict(lr=1e-3, steps=10, batch=16),
    pl=dict(lr=3e-4, steps=40, batch=16, conf=0.90, sigma_ms=12.0),
)


# ------------------------------------------------------------------ nap du lieu
def psd_score(x250, fs=250):
    e = np.abs(sg.hilbert(x250 - np.mean(x250))); e = e - np.mean(e)
    f, P = sg.welch(e, fs=fs, nperseg=min(len(e), 4096))
    m = (f >= FHR_BAND[0]) & (f <= FHR_BAND[1])
    return float(P[m].max()) if m.any() else 0.0


def list_cinc():
    D = cinc2013_dir()
    if D is None:
        raise SystemExit('Khong tim thay CinC 2013 set-a')
    recs = sorted(f[:-4] for f in os.listdir(D) if f.endswith('.dat'))
    return D, recs


def prep_cinc(rec, with_raw=False):
    """CinC 2013 set-a -> 4 kenh da tien xu ly. gt CHI dung de cham diem cuoi cung."""
    import wfdb
    D = cinc2013_dir()
    r_ = wfdb.rdrecord(os.path.join(D, rec))
    ann = wfdb.rdann(os.path.join(D, rec), 'fqrs')
    fs0 = float(r_.fs)
    gt = (np.asarray(ann.sample, float) * (1000.0 / fs0)).round().astype(int)
    leads, raws = [], []
    for lead in range(min(4, r_.p_signal.shape[1])):
        s = np.nan_to_num(r_.p_signal[:, lead])
        if fs0 != 1000:
            s = sg.resample_poly(s, 1000, int(fs0))
        if with_raw:
            raws.append(s.astype(np.float32))
        x = M.preprocess(s, 1000, CFG)
        rr, _ = M.cancel_maternal(x, CFG)
        leads.append(dict(r_s=M.robust_scale(rr).astype(np.float32),
                          x_s=M.robust_scale(x).astype(np.float32), psd=psd_score(rr)))
    meta = dict(fs0=fs0, n_ch=int(r_.p_signal.shape[1]), dur_s=r_.p_signal.shape[0] / fs0,
                gain=[float(g) for g in r_.adc_gain])
    del r_
    return leads, gt, meta, raws


def prep_subject(tag, with_raw=False):
    """22 chu the trong mien -> 4 kenh da tien xu ly + nhan that."""
    import wfdb
    if tag in PHYSIONET:
        import mne
        D = adfecgdb_dir()
        raw = mne.io.read_raw_edf(os.path.join(D, tag + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()
        gt = np.asarray(wfdb.rdann(os.path.join(D, tag + '.edf'), 'qrs').sample, int)
        chans = {l: sig[l] for l in LEADS}
        meta = dict(fs0=1000.0, n_ch=int(sig.shape[0]), dur_s=sig.shape[1] / 1000.0, group='PhysioNet')
        del raw, sig
    else:
        sig, _, mt = L.load(tag)
        gt = np.asarray(mt['fqrs_all'], int)
        chans = {l: sig[l - 1] for l in LEADS}
        meta = dict(fs0=1000.0, n_ch=int(sig.shape[0]), dur_s=float(mt['duration_s']),
                    group=('B1' if tag.startswith('B1') else 'B2'))
        del sig
    leads, raws = [], []
    for l in LEADS:
        if with_raw:
            raws.append(np.asarray(chans[l], np.float32))
        x = M.preprocess(chans[l], CFG['fs_in'], CFG)
        rr, _ = M.cancel_maternal(x, CFG)
        leads.append(dict(r_s=M.robust_scale(rr).astype(np.float32),
                          x_s=M.robust_scale(x).astype(np.float32), psd=psd_score(rr)))
    del chans
    return leads, gt, meta, raws


# ------------------------------------------------------------------ mo hinh
def load_net(name=PROD22):
    b = torch.load(checkpoint(name), map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval()
    return net, float(b['threshold'])


def segments(r_s, x_s, seg=None):
    """cat ban ghi thanh cac doan khong chong lan -> tensor (N, 2, seg)"""
    seg = seg or CFG['seg']
    n = (len(r_s) // seg) * seg
    if n == 0:
        pad = seg - len(r_s)
        r_s = np.pad(r_s, (0, pad)); x_s = np.pad(x_s, (0, pad)); n = seg
    a = r_s[:n].reshape(-1, seg); b = x_s[:n].reshape(-1, seg)
    return torch.from_numpy(np.stack([a, b], 1).astype(np.float32))


def detect(net, thr, lead):
    p = M.probability_series(net, lead['r_s'], lead['x_s'], CFG)
    return M.pick_peaks(p, thr, CFG).astype(np.int64) * Q, p


def score(det1000, gt1000):
    m = M.match_events(det1000, gt1000, CFG['fs_in'], TOL_MS)
    m['n_det'] = int(len(det1000)); m['n_ref'] = int(len(gt1000))
    return m


# ------------------------------------------------------------------ PHUONG PHAP THICH NGHI
# KHONG ham nao duoi day nhan nhan that.
def m_adabn(net0, lead, hp=None):
    """(a) AdaBN -- tinh lai thong ke BatchNorm tren chinh ban ghi dich. Khong gradient."""
    net = copy.deepcopy(net0)
    for mod in net.modules():
        if isinstance(mod, nn.BatchNorm1d):
            mod.reset_running_stats(); mod.momentum = None   # trung binh tich luy
    net.train()
    with torch.no_grad():
        net(segments(lead['r_s'], lead['x_s']))
    net.eval()
    return net


def _entropy(logit):
    p = torch.sigmoid(logit).clamp(1e-6, 1 - 1e-6)
    return -(p * torch.log(p) + (1 - p) * torch.log(1 - p)).mean()


def m_tent(net0, lead, hp):
    """(c) Thich nghi luc kiem tra: toi thieu entropy nhi phan tren dau ra, chi cap nhat
    tham so affine cua BatchNorm (TENT, Wang et al. ICLR 2021). Khong dung nhan."""
    net = copy.deepcopy(net0)
    for mod in net.modules():
        if isinstance(mod, nn.BatchNorm1d):
            mod.train(); mod.track_running_stats = False
            mod.running_mean = None; mod.running_var = None
    params = []
    for mo in net.modules():
        if isinstance(mo, nn.BatchNorm1d):
            params += [mo.weight, mo.bias]
    for p in net.parameters():
        p.requires_grad_(False)
    for p in params:
        p.requires_grad_(True)
    opt = torch.optim.Adam(params, lr=hp['lr'])
    X = segments(lead['r_s'], lead['x_s'])
    bs = min(hp['batch'], len(X))
    if bs < 2:
        net.eval(); return net
    g = torch.Generator().manual_seed(0)
    for _ in range(hp['steps']):            # so BUOC gradient co dinh, khong phu thuoc do dai ban ghi
        idx = torch.randperm(len(X), generator=g)[:bs]
        opt.zero_grad(); _entropy(net(X[idx])).backward(); opt.step()
    net.eval()
    return net


def _gauss_targets(n, peaks, sigma_samp):
    y = np.zeros(n, np.float32)
    if len(peaks) == 0:
        return y
    half = int(4 * sigma_samp)
    t = np.arange(n)
    for p in peaks:
        s, e = max(0, p - half), min(n, p + half + 1)
        y[s:e] = np.maximum(y[s:e], np.exp(-0.5 * ((t[s:e] - p) / sigma_samp) ** 2))
    return y


def m_pl(net0, lead, hp, thr):
    """(b) Tu huan luyen bang nhan gia, che do TRANSDUCTIVE tung ban ghi.
    Phat hien co xac suat >= conf duoc coi la nhan gia; huan luyen tiep toan mang.
    KHONG dung nhan that. conf duoc chot tren 22 chu the trong mien."""
    net = copy.deepcopy(net0)
    net.eval()
    with torch.no_grad():
        p = M.probability_series(net, lead['r_s'], lead['x_s'], CFG)
    pk = M.pick_peaks(p, thr, CFG)
    conf = hp['conf'] if hp.get('conf') is not None else thr
    keep = pk[p[pk] >= conf] if len(pk) else pk
    if len(keep) < 5:
        return net, 0
    sigma = hp['sigma_ms'] / 1000.0 * CFG['fs']
    seg = CFG['seg']; n = (len(lead['r_s']) // seg) * seg
    if n == 0:
        return net, int(len(keep))
    y = _gauss_targets(len(lead['r_s']), keep, sigma)
    X = segments(lead['r_s'], lead['x_s'])
    Y = torch.from_numpy(y[:n].reshape(-1, seg).copy())
    npos = max(float((Y >= .5).sum()), 1.0)
    pw = torch.tensor(min(max(float((Y < .5).sum()) / npos, 1.0), 200.0))
    lossf = nn.BCEWithLogitsLoss(pos_weight=pw)
    net.train()
    for mod in net.modules():                      # giu thong ke BN goc, chi hoc trong so
        if isinstance(mod, nn.BatchNorm1d):
            mod.eval()
    opt = torch.optim.AdamW(net.parameters(), lr=hp['lr'], weight_decay=1e-4)
    bs = min(hp['batch'], len(X))
    g = torch.Generator().manual_seed(0)
    for _ in range(hp['steps']):            # so BUOC gradient co dinh, khong phu thuoc do dai ban ghi
        idx = torch.randperm(len(X), generator=g)[:bs]
        opt.zero_grad()
        lossf(net(X[idx]), Y[idx]).backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
        opt.step()
    net.eval()
    return net, int(len(keep))


# ------------------------------------------------------------------ thong ke muc ban ghi
def boot_ci(d, n_boot=10000, seed=0):
    d = np.asarray(d, float); n = len(d)
    rng = np.random.default_rng(seed)
    b = d[rng.integers(0, n, size=(n_boot, n))].mean(1)
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def paired_stats(new, ref):
    from scipy.stats import wilcoxon
    new = np.asarray(new, float); ref = np.asarray(ref, float); d = new - ref
    try:
        p = float(wilcoxon(new, ref).pvalue) if np.any(d != 0) else 1.0
    except Exception:
        p = float('nan')
    return dict(n=int(len(d)), mean_new=float(new.mean()), mean_ref=float(ref.mean()),
                mean_diff=float(d.mean()), median_diff=float(np.median(d)),
                ci95=boot_ci(d), p_wilcoxon=p,
                n_win=int((d > 1e-9).sum()), n_loss=int((d < -1e-9).sum()),
                n_tie=int((np.abs(d) <= 1e-9).sum()),
                n_drop=int((d < -1e-9).sum()), max_drop=float(-d.min()) if len(d) else 0.0,
                n_drop_gt5=int((d < -5).sum()), n_drop_gt10=int((d < -10).sum()),
                ge90=int((new >= 90).sum()), lt50=int((new < 50).sum()))
