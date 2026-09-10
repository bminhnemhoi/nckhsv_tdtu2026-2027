# -*- coding: utf-8 -*-
"""Ve tin hieu that o tung buoc cua pipeline, de nhin thay du lieu dau vao trong nhu the nao."""
import os, sys, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, torch, mne, wfdb
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'benchmark_dpss'))
from _paths import adfecgdb_dir
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG = M.CFG

rcParams['font.family'] = 'Times New Roman'; rcParams['font.size'] = 9
rcParams['axes.linewidth'] = 0.7
BLUE, GREEN, RED, GRAY = '#1F3864', '#1E6B33', '#9B1C1C', '#8A8A8A'

REC, LEAD, T0, DUR = 'r01', 4, 12.0, 4.0          # 4 giay tu giay thu 12
RAW = adfecgdb_dir()

raw = mne.io.read_raw_edf(os.path.join(RAW, REC + '.edf'), preload=True, verbose=False)
sig = raw.get_data()[LEAD]
gt1000 = np.array(wfdb.rdann(os.path.join(RAW, REC), 'edf.qrs').sample)

blob = torch.load(os.path.join(ROOT, 'model', 'checkpoints', f'fetalqrs_tcn_fold_{REC}.pt'),
                  map_location='cpu', weights_only=False)
net = M.FetalQRSTCN(); net.load_state_dict(blob['state_dict']); net.eval()
thr = float(blob['threshold'])

x250 = M.preprocess(sig, 1000, CFG)
res, _ = M.cancel_maternal(x250, CFG)
mpk = M.detect_maternal_qrs(x250, CFG)
prob = M.probability_series(net, M.robust_scale(res).astype(np.float32),
                            M.robust_scale(x250).astype(np.float32), CFG)
det250 = M.pick_peaks(prob, thr, CFG)

fs = CFG['fs']
a, b = int(T0 * fs), int((T0 + DUR) * fs)
t = np.arange(a, b) / fs
gt = gt1000 / 1000.0
gt = gt[(gt >= T0) & (gt < T0 + DUR)]
mp = mpk / fs; mp = mp[(mp >= T0) & (mp < T0 + DUR)]
dt = det250 / fs; dt = dt[(dt >= T0) & (dt < T0 + DUR)]

raw_seg = sig[int(T0 * 1000):int((T0 + DUR) * 1000)]
t_raw = np.arange(len(raw_seg)) / 1000.0 + T0

fig, ax = plt.subplots(5, 1, figsize=(9.2, 8.4), sharex=True,
                       gridspec_kw=dict(hspace=0.32))

# --- 1. tin hieu tho
ax[0].plot(t_raw, raw_seg * 1e3, color=GRAY, lw=0.6)
ax[0].set_ylabel('mV')
ax[0].set_title('1.  Tín hiệu thô từ điện cực bụng, 1000 Hz — nhịp thai gần như không nhìn thấy',
                fontsize=9.5, loc='left', pad=4)

# --- 2. sau loc 10-60 Hz
ax[1].plot(t, x250[a:b], color=BLUE, lw=0.7)
for p in mp: ax[1].axvline(p, color=RED, lw=0.8, alpha=0.55)
ax[1].set_ylabel('đã lọc')
ax[1].set_title('2.  Sau lọc 10–60 Hz và hạ về 250 Hz — vạch đỏ là nhịp MẸ mà thuật toán dò được',
                fontsize=9.5, loc='left', pad=4)

# --- 3. tin hieu du sau khu me
ax[2].plot(t, res[a:b], color=GREEN, lw=0.7)
for p in gt: ax[2].axvline(p, color='#B8860B', lw=0.9, alpha=0.8)
ax[2].set_ylabel('tín hiệu dư')
ax[2].set_title('3.  Sau khi trừ mẫu ECG mẹ — vạch vàng là nhịp THAI thật (nhãn chuẩn từ điện cực da đầu)',
                fontsize=9.5, loc='left', pad=4)

# --- 4. dau ra mang
ax[3].plot(t, prob[a:b], color=BLUE, lw=1.0)
ax[3].axhline(thr, color=RED, ls='--', lw=0.9)
ax[3].text(T0 + 0.03, thr + 0.04, f'ngưỡng τ = {thr:.2f}'.replace('.', ','), fontsize=7.6, color=RED)
for p in gt: ax[3].axvline(p, color='#B8860B', lw=0.9, alpha=0.55)
ax[3].set_ylim(-0.05, 1.1); ax[3].set_ylabel('xác suất')
ax[3].set_title('4.  Đầu ra mạng — một xác suất cho TỪNG MẪU, không phải phân loại cửa sổ',
                fontsize=9.5, loc='left', pad=4)

# --- 5. ket qua
ax[4].plot(t, res[a:b], color='#CCCCCC', lw=0.6)
for i, p in enumerate(gt):
    ax[4].axvline(p, color='#B8860B', lw=1.6, alpha=0.85,
                  label='nhịp thai thật' if i == 0 else None)
for i, p in enumerate(dt):
    ax[4].axvline(p, color=GREEN, lw=1.0, ls='--',
                  label='mô hình phát hiện' if i == 0 else None)
rr = np.diff(dt)
if len(rr): ax[4].text(T0 + 0.03, ax[4].get_ylim()[1] * 0.78,
                       f'nhịp tim thai ≈ {60/np.mean(rr):.0f} bpm', fontsize=8, color=GREEN)
ax[4].legend(fontsize=7.6, frameon=False, loc='lower right', ncol=2)
ax[4].set_ylabel('kết quả'); ax[4].set_xlabel('thời gian (giây)')
ax[4].set_title('5.  Kết quả — vạch xanh nét đứt trùng khít vạch vàng nghĩa là dò đúng',
                fontsize=9.5, loc='left', pad=4)

for a_ in ax:
    a_.grid(lw=0.35, color='#EEEEEE'); a_.spines['top'].set_visible(False)
    a_.spines['right'].set_visible(False)
ax[0].set_xlim(T0, T0 + DUR)

fig.suptitle(f'Bản ghi {REC}, kênh {raw.ch_names[LEAD]} — 4 giây thật, mô hình chưa từng thấy bản ghi này',
             fontsize=10.5, y=0.985)
out = os.path.join(HERE, 'figs', 'fig8_tin_hieu_dau_vao')
fig.savefig(out + '.pdf', bbox_inches='tight', pad_inches=0.05)
fig.savefig(out + '.png', dpi=155, bbox_inches='tight', pad_inches=0.05)
print('da luu', out + '.png')

print(f'\nTrong 4 giay nay: {len(gt)} nhip thai that, {len(dt)} nhip mo hinh phat hien, '
      f'{len(mp)} nhip me')
print(f'Bien do tin hieu tho: {raw_seg.std()*1e3:.3f} mV | sau khu me (chuan hoa): {res[a:b].std():.3f}')
