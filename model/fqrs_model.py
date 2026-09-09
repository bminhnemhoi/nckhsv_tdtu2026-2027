"""
FetalQRS-TCN — reference implementation.

Single-channel fetal QRS detector from abdominal ECG.
Every design constant below was chosen by an experiment reported in Part L of the review:
  band 10-60 Hz            band ablation over 8 candidates (+11.0 F1 vs the 1-45 Hz baseline)
  250 Hz                   convention of Behar 2014, Chen 2025, Asadi 2025
  4 s segments             DPSS swept 1-10 s -> 4 s best; R2W-Net and SCTD-Net use 4.096 s
  dilations 1,2,4,8,16     receptive-field sweep; F1 monotone in RF, saturating at ~1.5 s
  per-sample heatmap       jitter 1.0 ms vs 5.6-6.0 ms for a window classifier

Measured on ADFECGDB, leave-one-record-out, 3 seeds, 4 abdominal leads, +/-50 ms tolerance:
  macro F1 97.16 +/- 4.34, micro F1 97.15, Se 97.05, PPV 97.28, jitter 3.64 ms.
"""
from __future__ import annotations
import numpy as np, torch, torch.nn as nn
from scipy import signal as sg

# ------------------------------------------------------------------ config
CFG = dict(
    fs_in=1000, fs=250, band=(10.0, 60.0), notch=50.0, notch_q=30.0,
    seg=1000, overlap=250, dilations=(1, 2, 4, 8, 16), channels=40, kernel=7,
    heatmap_sigma=3.0, refractory_ms=250, tolerance_ms=50,
    mqrs_band=(8.0, 25.0), mqrs_min_rr_s=0.35, tmpl_pre_s=0.15, tmpl_post_s=0.30,
)

# ------------------------------------------------------------------ signal front end
def bandpass(x, fs, lo, hi, order=4):
    b, a = sg.butter(order, [lo / (fs / 2), hi / (fs / 2)], btype='band')
    return sg.filtfilt(b, a, x)

def preprocess(x, fs_in=1000, cfg=CFG):
    """raw single abdominal lead -> filtered signal at cfg['fs']"""
    lo, hi = cfg['band']
    y = bandpass(np.asarray(x, float), fs_in, lo, hi)
    if lo < cfg['notch'] < hi:
        y = sg.filtfilt(*sg.iirnotch(cfg['notch'], cfg['notch_q'], fs_in), y)
    q = int(round(fs_in / cfg['fs']))
    return sg.resample_poly(y, 1, q) if q > 1 else y

def robust_scale(x):
    med = np.median(x); iqr = np.subtract(*np.percentile(x, [75, 25]))
    return (x - med) / (iqr + 1e-9)

def detect_maternal_qrs(x, cfg=CFG):
    fs = cfg['fs']; lo, hi = cfg['mqrs_band']
    f = sg.filtfilt(*sg.butter(2, [lo / (fs / 2), hi / (fs / 2)], btype='band'), x)
    e = np.convolve(np.diff(f, prepend=f[0]) ** 2, np.ones(int(.12 * fs)) / int(.12 * fs), mode='same')
    pk, _ = sg.find_peaks(e, distance=int(cfg['mqrs_min_rr_s'] * fs), height=.3 * np.percentile(e, 98))
    r = int(.04 * fs); out = []
    for p in pk:
        s, t = max(0, p - r), min(len(x), p + r)
        if t > s: out.append(s + int(np.argmax(np.abs(x[s:t]))))
    return np.unique(np.asarray(out, int))

def cancel_maternal(x, cfg=CFG):
    """median-template subtraction with per-beat least-squares scaling"""
    fs = cfg['fs']; mpk = detect_maternal_qrs(x, cfg)
    ps, po = int(cfg['tmpl_pre_s'] * fs), int(cfg['tmpl_post_s'] * fs)
    beats = [x[p - ps:p + po] for p in mpk if p - ps >= 0 and p + po < len(x)]
    if len(beats) < 3:
        return x.copy(), mpk
    T = np.median(np.asarray(beats), 0); nT = float(np.sum(T ** 2)) + 1e-12
    m = np.zeros_like(x)
    for p in mpk:
        if p - ps >= 0 and p + po < len(x):
            a = float(np.clip(np.dot(x[p - ps:p + po], T) / nT, 0.3, 3.0))
            m[p - ps:p + po] += a * T
    return x - m, mpk

# ------------------------------------------------------------------ model
def _cbr(i, o, k, d=1):
    return nn.Sequential(nn.Conv1d(i, o, k, padding=(k // 2) * d, dilation=d, bias=False),
                         nn.BatchNorm1d(o), nn.GELU())

class FetalQRSTCN(nn.Module):
    """dilated residual TCN, sequence-to-sequence, one logit per input sample"""
    def __init__(self, cin=2, c=CFG['channels'], k=CFG['kernel'], dils=CFG['dilations']):
        super().__init__()
        self.stem = _cbr(cin, c, k)
        self.blocks = nn.ModuleList([nn.ModuleDict({
            'a': _cbr(c, c, k, d),
            'b': nn.Sequential(nn.Conv1d(c, c, k, padding=(k // 2) * d, dilation=d, bias=False),
                               nn.BatchNorm1d(c))}) for d in dils])
        self.act = nn.GELU()
        self.out = nn.Conv1d(c, 1, 1)
        self.receptive_field = 1 + 2 * (k - 1) * sum(dils) + (k - 1)

    def forward(self, x):
        h = self.stem(x)
        for m in self.blocks:
            h = self.act(m['b'](m['a'](h)) + h)
        return self.out(h).squeeze(1)

# ------------------------------------------------------------------ inference
@torch.no_grad()
def probability_series(model, r, x, cfg=CFG):
    """slide the model over a full record with overlap-averaging -> per-sample probability"""
    model.eval()
    n = len(r); seg, ov = cfg['seg'], cfg['overlap']
    if n < seg:
        pad = seg - n
        r = np.pad(r, (0, pad)); x = np.pad(x, (0, pad))
    acc = np.zeros(len(r)); cnt = np.zeros(len(r))
    step = seg - ov
    starts = list(range(0, max(len(r) - seg, 0) + 1, step))
    if starts and starts[-1] + seg < len(r):
        starts.append(len(r) - seg)
    for s in starts:
        t = torch.from_numpy(np.stack([r[s:s + seg], x[s:s + seg]])[None].astype(np.float32))
        acc[s:s + seg] += torch.sigmoid(model(t)).numpy()[0]
        cnt[s:s + seg] += 1
    cnt[cnt == 0] = 1
    return (acc / cnt)[:n]

def pick_peaks(prob, threshold, cfg=CFG):
    d = int(cfg['refractory_ms'] / 1000 * cfg['fs'])
    pk, _ = sg.find_peaks(prob, height=threshold, distance=max(d, 1))
    return pk

def fetal_heart_rate(peaks_samples, fs=CFG['fs'], win_s=10.0, hop_s=1.0, n=None):
    """returns (t_seconds, bpm) using the median RR inside each window"""
    if len(peaks_samples) < 2: return np.zeros(0), np.zeros(0)
    t = np.asarray(peaks_samples) / fs
    end = (n / fs) if n else t[-1]
    ts, bpm = [], []
    for w0 in np.arange(0, max(end - win_s, 0) + hop_s, hop_s):
        sel = t[(t >= w0) & (t < w0 + win_s)]
        if len(sel) >= 3:
            rr = np.diff(sel); rr = rr[(rr > .3) & (rr < .7)]
            if len(rr): ts.append(w0 + win_s / 2); bpm.append(60.0 / float(np.median(rr)))
    return np.asarray(ts), np.asarray(bpm)

def detect(model, raw_signal, fs_in=1000, threshold=0.45, cfg=CFG, return_series=False):
    """end-to-end: raw single abdominal lead -> fetal R-peak sample indices at fs_in"""
    x250 = preprocess(raw_signal, fs_in, cfg)
    res, mpk = cancel_maternal(x250, cfg)
    r_s, x_s = robust_scale(res), robust_scale(x250)
    prob = probability_series(model, r_s, x_s, cfg)
    pk250 = pick_peaks(prob, threshold, cfg)
    scale = fs_in / cfg['fs']
    out = dict(fqrs_samples=np.round(pk250 * scale).astype(int),
               fqrs_seconds=pk250 / cfg['fs'],
               maternal_qrs_seconds=mpk / cfg['fs'],
               n_beats=len(pk250))
    ts, bpm = fetal_heart_rate(pk250, cfg['fs'], n=len(r_s))
    out['fhr_time_s'], out['fhr_bpm'] = ts, bpm
    out['fhr_median_bpm'] = float(np.median(bpm)) if len(bpm) else float('nan')
    if return_series:
        out['probability'] = prob; out['residual'] = res
    return out

# ------------------------------------------------------------------ evaluation
def match_events(det_samples, ref_samples, fs, tolerance_ms=50):
    """greedy one-to-one matching, the CinC 2013 / Behar 2014 convention"""
    tol = tolerance_ms / 1000 * fs
    ref = np.asarray(ref_samples, float); det = np.sort(np.asarray(det_samples, float))
    used = np.zeros(len(ref), bool); tp = 0; errs = []
    for d in det:
        dd = np.abs(ref - d); ok = np.where((dd <= tol) & (~used))[0]
        if len(ok):
            j = ok[int(np.argmin(dd[ok]))]; used[j] = True; tp += 1; errs.append(dd[j] / fs * 1000)
    fp = len(det) - tp; fn = len(ref) - int(used.sum())
    se = tp / (tp + fn) * 100 if tp + fn else 0.0
    ppv = tp / (tp + fp) * 100 if tp + fp else 0.0
    return dict(TP=tp, FP=fp, FN=fn, Se=se, PPV=ppv,
                F1=2 * se * ppv / (se + ppv) if se + ppv else 0.0,
                jitter_ms=float(np.mean(errs)) if errs else float('nan'))

def make_heatmap(n, peaks, sigma=CFG['heatmap_sigma']):
    hm = np.zeros(n, np.float32); t = np.arange(n)
    for p in np.asarray(peaks, int):
        lo, hi = max(0, p - 12), min(n, p + 13)
        if hi > lo:
            hm[lo:hi] = np.maximum(hm[lo:hi], np.exp(-((t[lo:hi] - p) ** 2) / (2 * sigma ** 2)))
    return hm

def n_params(m): return sum(p.numel() for p in m.parameters())
