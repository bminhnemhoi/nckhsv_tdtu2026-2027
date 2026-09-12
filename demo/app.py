# -*- coding: utf-8 -*-
"""
RelyFetal -- demo web một trang (Gradio + Plotly), chạy cục bộ.

    python demo/app.py            # mở http://127.0.0.1:7860

Mọi tính toán nằm ở demo/core.py (không phụ thuộc gradio); file này chỉ dựng giao diện và vẽ.
Trạng thái đề tài phản ánh trong demo (xem docs/HUONG_DAN_DEMO.md):
  * mô hình 22 chủ thể (fetalqrs_tcn_22_*): fold không chứa chủ thể cho 22 ca, production cho zero-shot
  * chọn kênh mù nhãn: peakprob (mặc định, HẬU KIỂM) và PSD (Power-MF) để so sánh; hiển thị cả 4 kênh
  * cổng tin cậy: bản hiệu chuẩn trên mô hình 5 ca (fsqi/gate_classical.pkl) -- ghi rõ trên giao diện
  * bảng tổng hợp đọc từ analysis/dulieu_results.json (60 bản CinC sạch) -- không ghi cứng con số
Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.
"""
import os, sys, time, inspect, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

import numpy as np
import pandas as pd
import gradio as gr
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import core

DISCLAIMER = 'Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.'
UPLOAD_DIR = os.path.join(HERE, '_uploads')
RECS = core.sample_records()
LEAD_CHOICES = ['Tự động — peakprob (mặc định)', 'Tự động — PSD (Power-MF)', '1', '2', '3', '4']
LEAD_MODE = {LEAD_CHOICES[0]: 'peakprob', LEAD_CHOICES[1]: 'psd'}
CONF_CHOICES = ['Học (GBM, 12 chỉ số / đoạn 4 s)', 'Luật cứng (4 thành phần)']       # -> core.confidence_mode 'hoc' | 'luat'
CONF_MODE = {CONF_CHOICES[0]: 'hoc', CONF_CHOICES[1]: 'luat'}
SEG_COLOR = {'xanh': '#0ca30c', 'vang': '#fab219', 'do': '#d03b3b'}
SEG_FILL = {'xanh': 'rgba(12,163,12,0.10)', 'vang': 'rgba(250,178,25,0.18)', 'do': 'rgba(208,59,59,0.22)'}
VIEW_S = 10.0                       # cửa sổ hiển thị ban đầu (giây); kéo/thả để phóng to, cuộn để dịch

COL = dict(raw='#6b7280', filt='#2563eb', mat='#dc2626', res='#0f766e', lab='#111827',
           prob='#7c3aed', thr='#ea580c', det='#16a34a', tp='#16a34a', fp='#dc2626', fn='#f59e0b', sel='#2563eb')

SHOWCASE_WHY = {
    'r01': 'ADFECGDB, dễ — fold 22 ca chưa thấy r01; mọi quy tắc chọn kênh đều cho F1 ≈ 100',
    'a09': 'CinC sạch, zero-shot — PSD chọn kênh sai (F1 ≈ 19); peakprob chọn kênh khác (F1 ≈ 94)',
    'B2_03': 'Silesia chuyển dạ, khó — mô hình thất bại một phần; cổng tin cậy phải báo ĐỎ/VÀNG',
    'a02': 'CinC sạch — mô hình bám nhịp MẸ; cổng "bám nhịp mẹ" phải báo ĐỎ',
    'a27': 'CinC sạch, gần như không có tín hiệu thai — hệ thống phải nói "tôi không chắc"',
}


def _rec_label(name):
    d = RECS[name]
    ck = f'fold {core.fold22_of(name)}' if core.fold22_of(name) else 'production (zero-shot)'
    flag = ''
    if d.get('leak'):
        flag = f' · ⚠ RÒ RỈ = {core.CINC_LEAK[name]}'
    elif d.get('bad_annotation'):
        flag = ' · ⚠ nhãn sai'
    return f'{name} — {d["dataset"]} · {ck}{flag}'


REC_LABELS = {_rec_label(n): n for n in RECS}
SHOWCASE_LABELS = {f'{n} — {SHOWCASE_WHY[n]}': n for n in core.DEMO_SHOWCASE if n in RECS}


# =========================================================================== bảng tổng hợp (đọc JSON, không ghi cứng)
def _load_json(rel):
    p = os.path.join(ROOT, rel)
    with open(p, encoding='utf-8') as f:
        return json.load(f), rel


def summary_tables_md():
    """Bảng tổng hợp từ analysis/dulieu_results.json (60 bản CinC sạch) và analysis/chonkenh_results.json (22 chủ thể)."""
    parts = []
    try:
        d, src = _load_json('analysis/dulieu_results.json')
        c = d['chon_kenh_60_sach']; B = c['bang']
        oracle = B['psd']['mean_60_sach'] + c['du_dia_oracle']
        rows = []
        for k, nm in (('psd', 'PSD (Power-MF, Jaeger 2024)'), ('gate', 'gate — quy tắc KHAI BÁO TRƯỚC'),
                      ('gate4', 'gate4'), ('rrcv', 'rrcv'), ('peakprob', 'peakprob — HẬU KIỂM (mặc định demo)')):
            b = B[k]
            ci = b['ci95']; hp = b.get('holm_p')
            rows.append(f"| {nm} | {b['mean_60_sach']:.2f} | {b['median_60']:.2f} | {b['lt50']} | "
                        f"{b['hieu_vs_psd']:+.2f} [{ci[0]:+.2f}; {ci[1]:+.2f}] | {b['wilcoxon_p']:.2g} | "
                        f"{('%.3g' % hp) if hp is not None else '—'} | {b['thang']}/{b['hoa']}/{b['thua']} |")
        parts.append(f'''
### Chọn kênh mù nhãn trên **60 bản CinC 2013 set-a sạch** (đã loại 15 bản rò rỉ) — nguồn `{src}` → `chon_kenh_60_sach`
Mô hình `fetalqrs_tcn_22_production.pt`, zero-shot. Đơn vị: bản ghi (n = {B['psd']['n']}). Oracle (kênh tốt nhất theo nhãn) = **{oracle:.2f}**.

| Quy tắc | F1 TB | F1 trung vị | bản F1 < 50 | hiệu so với PSD [KTC 95 %] | p Wilcoxon | p Holm (7 quy tắc) | thắng/hoà/thua |
|---|--:|--:|--:|---|--:|--:|--:|
''' + '\n'.join(rows) + f'''

peakprob lấy lại **{B['peakprob']['phan_tram_du_dia_oracle']:.1f} %** dư địa oracle.
**Cảnh báo bắt buộc:** quy tắc quyết định *khai báo trước* là **gate**, và gate **trượt Holm** (p Holm {B['gate']['holm_p']:.3f}).
peakprob là lựa chọn **hậu kiểm** (chọn sau khi đã biết F1 từng kênh) → *"giả thuyết mạnh chưa được xác nhận; cần nhân rộng trên bộ thứ ba"*.
Kiểm rò rỉ nhãn: xáo nhãn rồi chạy lại → 0/776 lựa chọn đổi (`analysis/chonkenh_results.json` → `kiem_tra_ro_ri`).
''')
    except Exception as e:                                       # noqa: BLE001
        parts.append(f'*Không đọc được analysis/dulieu_results.json: {e}*')
    try:
        d, _ = _load_json('analysis/chonkenh_results.json')
        s22 = d['bang']['s22']
        # KTC Power-MF lay tu tep chuan (cung nguon voi bai bao), khong tu he_qua_hau_kiem
        pf, src = _load_json('baselines/powermf_fair_stats.json')
        def _r(k):
            x = pf['so_sanh']['tat_ca_22'][k]
            return {'mean_a': x['mean_a'], 'mean_b': x['mean_b'], 'hieu': x['hieu'],
                    'ci95': [x['ci_lo'], x['ci_hi']], 'p_wilcoxon': x['p_wilcoxon'],
                    'thang': x['thang'], 'thua': x['thua']}
        r4 = _r('rely_vs_pmf4'); r1 = _r('rely_vs_pmf1')
        parts.append(f'''
### 22 chủ thể trong miền (F1 mức chủ thể, checkpoint fold không chứa chủ thể) — nguồn `{src}`

| So sánh | RelyFetal 1 kênh (PSD) | Power-MF | hiệu [KTC 95 %] | p Wilcoxon | thắng/thua |
|---|--:|--:|---|--:|--:|
| so với Power-MF **4 kênh** | {r4['mean_a']:.2f} | {r4['mean_b']:.2f} | {r4['hieu']:+.2f} [{r4['ci95'][0]:+.2f}; {r4['ci95'][1]:+.2f}] | {r4['p_wilcoxon']:.3f} | {r4['thang']}/{r4['thua']} |
| so với Power-MF **1 kênh** | {r1['mean_a']:.2f} | {r1['mean_b']:.2f} | {r1['hieu']:+.2f} [{r1['ci95'][0]:+.2f}; {r1['ci95'][1]:+.2f}] | {r1['p_wilcoxon']:.2g} | {r1['thang']}/{r1['thua']} |

Trên 22 chủ thể, peakprob = {s22['peakprob']['mean']:.2f} so với PSD = {s22['psd']['mean']:.2f}
(hiệu {s22['peakprob']['diff_vs_psd']:+.2f}, p Wilcoxon {s22['peakprob']['wilcoxon_p']:.3f}, p Holm {s22['peakprob'].get('holm_p', float('nan')):.3f}) — trong miền, quy tắc chọn kênh hầu như không đổi kết quả.
Power-MF chạy lại qua GNU Octave (`baselines/`), kiểm chứng ngoài: B1 99,40 so với 99,46 tác giả công bố.
''')
    except Exception as e:                                       # noqa: BLE001
        parts.append(f'*Không đọc được analysis/chonkenh_results.json: {e}*')
    parts.append(f'''
### Cổng tin cậy
{core.GATE_NOTE} Kết quả cổng 22 ca (LOSO, `analysis/gate22_results.json`): AUROC trong bản ghi 0,934; 3 bản khó nhất (B2_03, B1_07, B1_06)
xếp đúng hạng 1-2-3 — nhưng 5/24 quy tắc một đặc trưng cũng xếp đúng 3/3, nên chưa được coi là bằng chứng mạnh.

*Mọi con số CinC trên 75 bản ghi đã công bố trước đây đều bị **rút** (15/75 bản là bản sao huấn luyện). Không có con số nào trong demo lấy từ 75 bản.*
''')
    return '\n'.join(parts)


SUMMARY_MD = summary_tables_md()


# =========================================================================== vẽ
def _vlines(xs, y0, y1):
    """nhiều đoạn thẳng đứng trong MỘT trace (ngăn cách bằng NaN) -- rẻ hơn hàng trăm shape."""
    xs = np.asarray(xs, float)
    if len(xs) == 0:
        return np.zeros(0), np.zeros(0)
    x = np.column_stack([xs, xs, np.full_like(xs, np.nan)]).ravel()
    y = np.tile([y0, y1, np.nan], len(xs))
    return x, y


def _rng(y, pad=0.08):
    lo, hi = float(np.nanmin(y)), float(np.nanmax(y)); d = (hi - lo) or 1.0
    return lo - pad * d, hi + pad * d


def signal_figure(out):
    fs = out['fs']; n = len(out['filtered_250']); t = np.arange(n) / fs
    raw = out['raw']; step = 4 if len(raw) > 200_000 else 1
    traw = np.arange(0, len(raw), step) / out['fs_raw']
    x250, res, prob = out['filtered_250'], out['residual_250'], out['prob']
    mpk, det = out['maternal_peaks'], out['fetal_peaks_250']
    lab = out.get('labels_1000'); has_lab = lab is not None
    thr = out['threshold']
    titles = [f'[1] Tín hiệu thô, kênh {out.get("lead", "?")} ({out["fs_raw"]} Hz{", hiển thị 1/4 mẫu" if step > 1 else ""}) — chọn bởi {out.get("lead_mode", "")}',
              f'[2] Đã lọc 10–60 Hz + notch 50 Hz, 250 Hz — vạch đỏ: {len(mpk)} nhịp mẹ (QRS mẹ)',
              f'[3] Sau khử mẹ (phần dư đưa vào mô hình)' + (f' — vạch đen: {len(lab)} nhịp thai theo nhãn' if has_lab else ' — không có nhãn'),
              f'[4] Xác suất nhịp thai của FetalQRS-TCN — ngưỡng {thr:.2f} (cố định, lưu trong checkpoint)',
              '[5] Kết quả: mô hình so với nhãn — ● TP xanh, ✕ FP đỏ, ▲ FN cam' if has_lab
              else f'[5] Kết quả: {len(det)} nhịp thai do mô hình phát hiện (không có nhãn để đối chiếu)']
    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.045, subplot_titles=titles)

    fig.add_trace(go.Scattergl(x=traw, y=raw[::step], name='Thô', line=dict(color=COL['raw'], width=1),
                               hovertemplate='%{x:.3f} s<br>%{y:.4g}<extra>thô</extra>'), row=1, col=1)

    lo, hi = _rng(x250)
    fig.add_trace(go.Scattergl(x=t, y=x250, name='Đã lọc', line=dict(color=COL['filt'], width=1),
                               hovertemplate='%{x:.3f} s<br>%{y:.3g}<extra>lọc</extra>'), row=2, col=1)
    vx, vy = _vlines(mpk / fs, lo, hi)
    fig.add_trace(go.Scattergl(x=vx, y=vy, name='Nhịp mẹ', mode='lines', line=dict(color=COL['mat'], width=1.2),
                               opacity=0.7, hoverinfo='skip'), row=2, col=1)

    lo, hi = _rng(res)
    fig.add_trace(go.Scattergl(x=t, y=res, name='Phần dư', line=dict(color=COL['res'], width=1),
                               hovertemplate='%{x:.3f} s<br>%{y:.3g}<extra>phần dư</extra>'), row=3, col=1)
    if has_lab:
        vx, vy = _vlines(lab / out['fs_raw'], lo, hi)
        fig.add_trace(go.Scattergl(x=vx, y=vy, name='Nhãn nhịp thai', mode='lines',
                                   line=dict(color=COL['lab'], width=1, dash='dot'), opacity=0.8, hoverinfo='skip'), row=3, col=1)

    fig.add_trace(go.Scattergl(x=t, y=prob, name='Xác suất', line=dict(color=COL['prob'], width=1.2),
                               fill='tozeroy', fillcolor='rgba(124,58,237,0.12)',
                               hovertemplate='%{x:.3f} s<br>p = %{y:.2f}<extra></extra>'), row=4, col=1)
    fig.add_hline(y=thr, line=dict(color=COL['thr'], width=1.5, dash='dash'), row=4, col=1)
    fig.add_trace(go.Scattergl(x=det / fs, y=prob[det], name='Đỉnh chọn', mode='markers',
                               marker=dict(color=COL['det'], size=6, symbol='circle'),
                               hovertemplate='%{x:.3f} s<br>p = %{y:.2f}<extra>đỉnh</extra>'), row=4, col=1)

    fig.add_trace(go.Scattergl(x=t, y=res, name='Phần dư', line=dict(color='#9ca3af', width=1),
                               showlegend=False, hoverinfo='skip'), row=5, col=1)
    lo, hi = _rng(res)
    if has_lab:
        d_tp = np.array([d for d, _ in out['matched']], int); d_fp = np.array(out['false'], int); d_fn = np.array(out['missed'], int)
        q = int(out['fs_raw'] // fs)
        for arr, key, nm, sym in ((d_tp, 'tp', 'TP (đúng)', 'circle'), (d_fp, 'fp', 'FP (dư)', 'x'), (d_fn, 'fn', 'FN (sót)', 'triangle-up')):
            if len(arr) == 0:
                continue
            i = np.clip(arr // q, 0, n - 1)
            fig.add_trace(go.Scattergl(x=arr / out['fs_raw'], y=res[i], name=f'{nm}: {len(arr)}', mode='markers',
                                       marker=dict(color=COL[key], size=9 if key != 'tp' else 7, symbol=sym,
                                                   line=dict(width=1, color=COL[key])),
                                       hovertemplate='%{x:.3f} s<extra>' + nm + '</extra>'), row=5, col=1)
        if len(d_fn):
            vx, vy = _vlines(d_fn / out['fs_raw'], lo, hi)
            fig.add_trace(go.Scattergl(x=vx, y=vy, mode='lines', showlegend=False,
                                       line=dict(color=COL['fn'], width=1, dash='dot'), hoverinfo='skip'), row=5, col=1)
    else:
        vx, vy = _vlines(det / fs, lo, hi)
        fig.add_trace(go.Scattergl(x=vx, y=vy, name=f'Mô hình: {len(det)} nhịp', mode='lines',
                                   line=dict(color=COL['det'], width=1.2), hoverinfo='skip'), row=5, col=1)

    dur = len(raw) / out['fs_raw']
    fig.update_xaxes(range=[0, min(VIEW_S, dur)], showgrid=True, gridcolor='rgba(0,0,0,0.06)')
    fig.update_xaxes(title_text='thời gian (s) — kéo để phóng to, nhấp đúp để xem toàn bộ', row=5, col=1)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.06)', zeroline=False)
    fig.update_yaxes(title_text='xác suất', range=[-0.02, 1.05], row=4, col=1)
    fig.update_layout(height=1150, margin=dict(l=60, r=20, t=40, b=50), hovermode='closest',
                      legend=dict(orientation='h', yanchor='bottom', y=1.015, xanchor='right', x=1, font=dict(size=11)),
                      plot_bgcolor='white', paper_bgcolor='white', font=dict(size=12), dragmode='zoom')
    for a in fig.layout.annotations:
        a.font.size = 13; a.x = 0.0; a.xanchor = 'left'
    return fig


def leads_figure(out):
    """Cả K kênh: phần dư + đỉnh mô hình (+ nhãn); kênh được chọn tô nền xanh. Chỉ có ở chế độ tự động."""
    L = out.get('leads')
    fig = go.Figure()
    if not L:
        fig.add_annotation(text='Chọn kênh thủ công — không có so sánh 4 kênh. Đổi ô "Kênh bụng" sang Tự động để xem.',
                           showarrow=False, font=dict(size=14))
        fig.update_layout(height=200, plot_bgcolor='white', paper_bgcolor='white')
        return fig
    fs = out['fs']; ks = sorted(L); K = len(ks)
    lab = out.get('labels_1000'); has_lab = lab is not None
    rule = out.get('lead_rule')
    titles = []
    for k in ks:
        d = L[k]
        sc = (f'peakprob = {d["peakprob"]:.3f}' if d.get('peakprob') is not None else '') + f' · PSD = {d["psd"]:.2e}'
        extra = ''
        if 'n_beats' in d:
            extra = f' · {d["n_beats"]} nhịp · fHR {d["fhr_mean"]:.0f} bpm' if np.isfinite(d['fhr_mean']) else f' · {d["n_beats"]} nhịp'
        if 'F1' in d:
            extra += f' · F1 = {d["F1"]:.2f}'
        titles.append(f'Kênh {k} ({d["name"]}){" — ĐƯỢC CHỌN bởi " + rule if d["selected"] else ""} · {sc}{extra}')
    fig = make_subplots(rows=K, cols=1, shared_xaxes=True, vertical_spacing=0.06, subplot_titles=titles)
    for r, k in enumerate(ks, 1):
        d = L[k]; res = d['residual_250']; t = np.arange(len(res)) / fs
        lo, hi = _rng(res)
        col = COL['sel'] if d['selected'] else '#6b7280'
        fig.add_trace(go.Scattergl(x=t, y=res, mode='lines', line=dict(color=col, width=1), showlegend=False,
                                   hovertemplate='%{x:.3f} s<br>%{y:.3g}<extra>kênh ' + str(k) + '</extra>'), row=r, col=1)
        if 'det250' in d:
            det = np.asarray(d['det250'], int)
            fig.add_trace(go.Scattergl(x=det / fs, y=res[np.clip(det, 0, len(res) - 1)], mode='markers',
                                       marker=dict(color=COL['det'], size=6), name='đỉnh mô hình', showlegend=(r == 1),
                                       hovertemplate='%{x:.3f} s<extra>đỉnh k' + str(k) + '</extra>'), row=r, col=1)
        if has_lab:
            vx, vy = _vlines(lab / out['fs_raw'], lo, hi)
            fig.add_trace(go.Scattergl(x=vx, y=vy, mode='lines', line=dict(color=COL['lab'], width=1, dash='dot'),
                                       opacity=0.6, name='nhãn nhịp thai', showlegend=(r == 1), hoverinfo='skip'), row=r, col=1)
        if d['selected']:
            fig.add_vrect(x0=0, x1=len(res) / fs, fillcolor='rgba(37,99,235,0.07)', line_width=0, row=r, col=1)
    dur = out['duration_s']
    fig.update_xaxes(range=[0, min(VIEW_S, dur)], showgrid=True, gridcolor='rgba(0,0,0,0.06)')
    fig.update_xaxes(title_text='thời gian (s) — kéo để phóng to, nhấp đúp để xem toàn bộ', row=K, col=1)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.06)', zeroline=False)
    fig.update_layout(height=230 * K + 60, margin=dict(l=60, r=20, t=40, b=50), hovermode='closest',
                      plot_bgcolor='white', paper_bgcolor='white', font=dict(size=12), dragmode='zoom',
                      legend=dict(orientation='h', yanchor='bottom', y=1.01, xanchor='right', x=1))
    for a in fig.layout.annotations:
        a.font.size = 13; a.x = 0.0; a.xanchor = 'left'
    return fig


def leads_md(out):
    L = out.get('leads')
    if not L:
        return '**Chọn kênh thủ công** — không có bảng so sánh kênh.'
    rule = out.get('lead_rule'); has_lab = 'F1' in L[next(iter(L))]
    head = '| Kênh | peakprob (trung vị xác suất tại đỉnh / đoạn 4 s) | PSD dải thai | Nhịp | fHR TB | ' + ('F1 | Se | PPV | ' if has_lab else '') + 'Chọn |'
    sep = '|---|--:|--:|--:|--:|' + ('--:|--:|--:|' if has_lab else '') + '---|'
    rows = []
    for k in sorted(L):
        d = L[k]
        pp = f'{d["peakprob"]:.3f}' if d.get('peakprob') is not None else '—'
        nb = d.get('n_beats', '—'); fh = f'{d["fhr_mean"]:.0f}' if np.isfinite(d.get('fhr_mean', np.nan)) else '—'
        cells = f'| {k} ({d["name"]}) | {pp} | {d["psd"]:.2e} | {nb} | {fh} | '
        if has_lab:
            cells += f'{d["F1"]:.2f} | {d["Se"]:.2f} | {d["PPV"]:.2f} | '
        cells += ('**◀ ' + rule + '**' if d['selected'] else '') + ' |'
        rows.append(cells)
    note = ('\n\n**Cách chọn (peakprob):** chạy mô hình trên cả 4 kênh; điểm mỗi kênh = trung vị (qua các đoạn 4 s) của xác suất '
            'trung bình mà mô hình gán cho các đỉnh nó vừa phát hiện; chọn kênh điểm cao nhất. Không dùng nhãn, không tham số học. '
            'Cột F1/Se/PPV (nếu có) chỉ tính **sau** khi đã chọn — để kiểm tra, không tham gia chọn. '
            '*peakprob là quy tắc hậu kiểm (khai báo trước là gate) — xem tab Kết quả tổng hợp.*'
            if rule == 'peakprob' else
            '\n\n**Cách chọn (PSD, Power-MF):** khử mẹ trên cả 4 kênh, lấy kênh có đỉnh PSD mạnh nhất trong dải 1,8–3,0 Hz '
            'của đường bao phần dư. Không chạy mô hình khi chọn.')
    return f'**Quy tắc đang dùng: `{rule}`** — kênh **{out["lead"]}** được chọn.\n\n' + '\n'.join([head, sep] + rows) + note


def fhr_figure(out):
    """fHR theo cửa sổ 4 s (trên) + điểm tin cậy từng đoạn 4 s (dưới); đoạn ĐỎ tô nền trên cả hai."""
    segs = out['confidence'].get('segments')
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.68, 0.32], vertical_spacing=0.08,
                        subplot_titles=['Nhịp tim thai (median RR trong từng cửa sổ 4 s)',
                                        'Điểm tin cậy từng đoạn 4 s — p(đoạn lỗi) của cổng học; ' +
                                        ('nền đỏ = đoạn bị TỪ CHỐI' if segs else 'chế độ luật: không có điểm theo đoạn')])
    fig.add_hrect(y0=110, y1=160, fillcolor='rgba(22,163,74,0.10)', line_width=0, row=1, col=1,
                  annotation_text='vùng bình thường 110–160 bpm', annotation_position='top left',
                  annotation_font=dict(color='#15803d', size=12))
    lab = out.get('labels_1000')
    if lab is not None:
        rt, rb = core.fhr_series(np.asarray(lab) / (out['fs_raw'] / out['fs']), len(out['residual_250']))
        fig.add_trace(go.Scatter(x=rt, y=rb, mode='lines+markers', name='Theo nhãn', line=dict(color='#111827', width=1.5, dash='dot'),
                                 marker=dict(size=5), hovertemplate='%{x:.0f} s<br>%{y:.1f} bpm<extra>nhãn</extra>'), row=1, col=1)
    fig.add_trace(go.Scatter(x=out['fhr_time_s'], y=out['fhr_series'], mode='lines+markers', name='Mô hình (cửa sổ 4 s)',
                             line=dict(color=COL['filt'], width=2.5), marker=dict(size=7),
                             hovertemplate='%{x:.0f} s<br>%{y:.1f} bpm<extra>mô hình</extra>'), row=1, col=1)
    if segs:
        n = len(segs['p_bad']); seg_s = float(segs['seg_s'])
        x0 = np.arange(n) * seg_s; xc = x0 + seg_s / 2
        lv = segs['level']; pb = np.asarray(segs['p_bad'], float)
        fig.add_trace(go.Bar(x=xc, y=pb, width=seg_s * 0.9, marker_color=[SEG_COLOR[l] for l in lv], name='p(đoạn lỗi)',
                             hovertemplate='%{x:.0f} s<br>p(đoạn lỗi) = %{y:.3f}<extra>đèn đoạn</extra>'), row=2, col=1)
        fig.add_hline(y=segs['q1'], line=dict(color=SEG_COLOR['xanh'], width=1, dash='dot'), row=2, col=1,
                      annotation_text=f'xanh < {segs["q1"]:.3f}', annotation_position='top left', annotation_font=dict(size=10))
        fig.add_hline(y=segs['q2'], line=dict(color=SEG_COLOR['do'], width=1, dash='dot'), row=2, col=1,
                      annotation_text=f'đỏ > {segs["q2"]:.3f}', annotation_position='bottom left', annotation_font=dict(size=10))
        # tô nền các đoạn đỏ (từ chối) -- gộp các đoạn liền nhau thành một hình để nhẹ
        red = [i for i, l in enumerate(lv) if l == 'do']
        runs = []
        for i in red:
            if runs and i == runs[-1][1] + 1:
                runs[-1][1] = i
            else:
                runs.append([i, i])
        for a, b in runs[:400]:
            for r in (1, 2):
                fig.add_vrect(x0=a * seg_s, x1=(b + 1) * seg_s, fillcolor=SEG_FILL['do'], line_width=0, row=r, col=1)
        n_red = len(red); n_green = sum(1 for l in lv if l == 'xanh')
        fig.add_annotation(text=f'{n_green}/{n} đoạn xanh · {n - n_green - n_red} vàng · {n_red} đỏ (từ chối)',
                           xref='paper', yref='paper', x=1, y=0.30, xanchor='right', showarrow=False, font=dict(size=12))
    if np.isfinite(out['fhr_mean']):
        fig.add_hline(y=out['fhr_mean'], line=dict(color=COL['filt'], width=1, dash='dash'), row=1, col=1,
                      annotation_text=f'trung bình {out["fhr_mean"]:.0f} bpm', annotation_position='bottom right')
    fig.update_yaxes(title_text='bpm', range=[60, 220], showgrid=True, gridcolor='rgba(0,0,0,0.06)', row=1, col=1)
    fig.update_yaxes(title_text='p(đoạn lỗi)', range=[0, 1.02], showgrid=True, gridcolor='rgba(0,0,0,0.06)', row=2, col=1)
    fig.update_xaxes(title_text='thời gian (s)', showgrid=True, gridcolor='rgba(0,0,0,0.06)', row=2, col=1)
    fig.update_layout(height=560, margin=dict(l=60, r=20, t=40, b=50), plot_bgcolor='white', paper_bgcolor='white',
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), hovermode='x unified',
                      bargap=0)
    for a in fig.layout.annotations:
        if a.text and (a.text.startswith('Nhịp tim') or a.text.startswith('Điểm tin cậy')):
            a.font.size = 13; a.x = 0.0; a.xanchor = 'left'
    return fig


# =========================================================================== thẻ số & bảng
def _fmt(v, f='{:.0f}'):
    return f.format(v) if v is not None and np.isfinite(v) else '—'


def cards_html(out, wall_ms=None):
    c = out['confidence']
    reasons = ''.join(f'<li>{r}</li>' for r in c['reasons'])
    mode = out.get('lead_mode', '')
    ck = out.get('checkpoint_note', out['checkpoint'])
    lat = out['latency_ms']; lat_all = out.get('latency_all_leads_ms')
    L = out.get('leads')
    if L:
        key = 'peakprob' if out.get('lead_rule') == 'peakprob' else 'psd'
        fmt = (lambda v: f'{v:.3f}') if key == 'peakprob' else (lambda v: f'{v:.1e}')
        chips = ''.join(f'<span class="rf-chip{" rf-chip-sel" if L[k]["selected"] else ""}">k{k}: {fmt(L[k][key])}'
                        + (f' · F1 {L[k]["F1"]:.1f}' if 'F1' in L[k] else '') + '</span>' for k in sorted(L))
        lead_body = f'<div class="rf-v">kênh {out["lead"]}<span class="rf-u"> / {out.get("n_leads", "?")}</span></div><div class="rf-chips">{chips}</div>'
        lead_sub = f'quy tắc <b>{out.get("lead_rule")}</b> — ' + ('trung vị xác suất tại đỉnh, chạy mô hình trên mọi kênh' if key == 'peakprob' else 'đỉnh PSD dải thai của phần dư')
    else:
        lead_body = f'<div class="rf-v">kênh {out["lead"]}<span class="rf-u"> / {out.get("n_leads", "?")}</span></div>'
        lead_sub = 'chọn tay'
    return f'''
<div class="rf-cards">
  <div class="rf-card"><div class="rf-k">fHR trung bình</div>
    <div class="rf-v">{_fmt(out['fhr_mean'])}<span class="rf-u"> bpm</span></div>
    <div class="rf-s">median RR trong từng cửa sổ 4 s · {out['n_beats']} nhịp thai / {out['duration_s']:.0f} s</div></div>
  <div class="rf-card"><div class="rf-k">Kênh được chọn ({mode})</div>
    {lead_body}
    <div class="rf-s">{lead_sub}</div></div>
  <div class="rf-card rf-conf" style="border-color:{c['color']};background:{c['color']}14">
    <div class="rf-k">Đèn tin cậy</div>
    <div class="rf-v" style="color:{c['color']}">● {c['label']}</div>
    <div class="rf-s">điểm {c['score']:.2f} / 1 — chế độ <b>{core.CONF_MODE_LABEL.get(c.get('mode', 'luat'), c.get('mode'))}</b>{f" · {c['components'].get('gate_ms', 0):,.0f} ms" if c.get('mode') == 'hoc' else ''}</div>
    <ul class="rf-r">{reasons}</ul>
    <div class="rf-note">⚠ {core.GATE_NOTE}</div></div>
  <div class="rf-card"><div class="rf-k">Thời gian xử lý</div>
    <div class="rf-v">{lat:,.0f}<span class="rf-u"> ms</span></div>
    <div class="rf-s">kênh đã chọn: tiền xử lý + khử mẹ + mô hình, CPU {core.torch.get_num_threads()} luồng
    {f"<br>cả {out.get('n_leads', '?')} kênh (chi phí thật của quy tắc tự động): {lat_all:,.0f} ms" if lat_all else ""}
    {f"<br>toàn bộ kể cả đọc file &amp; vẽ: {wall_ms:,.0f} ms" if wall_ms else ""}<br>checkpoint: {ck}</div></div>
</div>'''


def compare_md(out):
    if 'metrics' not in out:
        return ('**Bản ghi không có nhãn** — chế độ so sánh tắt. Với file tải lên, thêm file nhãn `.txt` '
                '(mỗi dòng một chỉ số mẫu) hoặc chú giải WFDB `.fqrs` / `.edf.qrs` cùng tên để bật.')
    m = out['metrics']
    warn = ''
    rn = out.get('record', '')
    if rn in core.CINC_LEAK:
        warn = (f'\n\n> ⚠ **{rn} là bản sao nguyên văn của {core.CINC_LEAK[rn]} (dữ liệu huấn luyện)** — '
                'kết quả ở đây KHÔNG phải ngoài miền và không được trích dẫn (analysis/DULIEU.md).')
    elif rn in core.CINC_BAD_ANN:
        warn = f'\n\n> ⚠ **{rn} thuộc 7 bản CinC có nhãn tham chiếu sai đã khai báo trước** — F1 thấp ở đây phần lớn là lỗi NHÃN.'
    return f'''
**Giao thức chấm:** dung sai ±{core.CFG['tolerance_ms']} ms, ghép một-đối-một tham lam (quy ước CinC 2013 / Behar 2014).
Nhãn: {len(out['labels_1000'])} nhịp thai. Mô hình: {out['n_beats']} nhịp (kênh {out['lead']}, {out.get('lead_mode', '')}).

| Se | PPV | F1 | Jitter |
|---:|---:|---:|---:|
| **{m['Se']:.2f} %** | **{m['PPV']:.2f} %** | **{m['F1']:.2f}** | {_fmt(m['jitter_ms'], '{:.2f}')} ms |

| TP (đúng) | FP (dư) | FN (sót) |
|---:|---:|---:|
| {m['TP']} | {m['FP']} | {m['FN']} |
{warn}
'''


def compare_df(out):
    if 'metrics' not in out:
        return None
    fs0 = out['fs_raw']; rows = []
    for d in out['false']:
        rows.append(dict(loại='FP (dư)', thời_điểm_s=round(d / fs0, 3), mô_hình_mẫu=int(d), nhãn_mẫu=None, sai_lệch_ms=None))
    for r in out['missed']:
        rows.append(dict(loại='FN (sót)', thời_điểm_s=round(r / fs0, 3), mô_hình_mẫu=None, nhãn_mẫu=int(r), sai_lệch_ms=None))
    for d, r in out['matched'][:200]:
        rows.append(dict(loại='TP', thời_điểm_s=round(d / fs0, 3), mô_hình_mẫu=int(d), nhãn_mẫu=int(r), sai_lệch_ms=round((d - r) / fs0 * 1000, 1)))
    df = pd.DataFrame(rows, columns=['loại', 'thời_điểm_s', 'mô_hình_mẫu', 'nhãn_mẫu', 'sai_lệch_ms'])
    df = df.sort_values(['loại', 'thời_điểm_s'], key=lambda s: s.map({'FP (dư)': 0, 'FN (sót)': 1, 'TP': 2}) if s.name == 'loại' else s)
    df.columns = ['Loại', 'Thời điểm (s)', 'Mô hình (mẫu 1000 Hz)', 'Nhãn (mẫu 1000 Hz)', 'Sai lệch (ms)']
    return df.reset_index(drop=True)


# =========================================================================== xử lý sự kiện
def _lead_arg(lead_choice):
    if lead_choice in LEAD_MODE:
        return LEAD_MODE[lead_choice]
    if isinstance(lead_choice, str) and lead_choice.startswith('Tự'):
        return 'peakprob'
    return int(lead_choice)


def run(source, upload_files, sample_label, lead_choice, fs_in, conf_choice=CONF_CHOICES[0], showcase_label=None):
    t0 = time.perf_counter()
    conf_mode = CONF_MODE.get(conf_choice, 'hoc')
    try:
        if str(source).startswith('Tải'):
            if not upload_files:
                raise gr.Error('Hãy tải lên một file bản ghi (.edf, .hea+.dat, .csv, .npy, .txt).')
            paths = [f if isinstance(f, str) else getattr(f, 'name', str(f)) for f in upload_files]
            main = core.gather_upload(paths, UPLOAD_DIR)
            lab = None
            if not main.lower().endswith('.txt'):
                cand = [p for p in os.listdir(UPLOAD_DIR) if p.lower().endswith('.txt')]
                lab = os.path.join(UPLOAD_DIR, cand[0]) if cand else None
            rec = core.load_record(main, fs=float(fs_in or 1000), labels=lab)
        else:
            if str(source).startswith('Minh'):
                name = SHOWCASE_LABELS.get(showcase_label)
            else:
                name = REC_LABELS.get(sample_label)
            if name is None:
                raise gr.Error('Chưa có bản ghi mẫu nào trên đĩa — hãy tải dữ liệu (xem README) hoặc tải file lên.')
            rec = core.load_sample(name, RECS)
        out = core.analyze_record(rec, lead=_lead_arg(lead_choice), confidence_mode=conf_mode)
    except gr.Error:
        raise
    except Exception as e:                       # noqa: BLE001
        raise gr.Error(f'Lỗi khi phân tích: {type(e).__name__}: {e}')
    fig1, fig2, fig3 = signal_figure(out), fhr_figure(out), leads_figure(out)
    wall = (time.perf_counter() - t0) * 1000
    s = core.summary(out)
    lead_txt = ''
    if out.get('lead_scores'):
        key = out.get('lead_rule')
        fmt = (lambda v: f'{v:.3f}') if key == 'peakprob' else (lambda v: f'{v:.2e}')
        lead_txt = f' · điểm {key} từng kênh: ' + ', '.join(f'k{k}={fmt(v)}' for k, v in out['lead_scores'].items())
    note = out.get('record_note') or ''
    status = (f'Đã phân tích **{out["record"]}** ({out["source"]}, {out["duration_s"]:.0f} s, {rec["signals"].shape[0]} kênh'
              f'{"; " + note if note else ""}) — kênh **{out["lead"]}** ({out["lead_mode"]}){lead_txt} — checkpoint *{out["checkpoint_note"]}* '
              f'— đèn tin cậy: *{core.CONF_MODE_LABEL[out["confidence_mode"]]}*.')
    return fig1, fig3, leads_md(out), fig2, cards_html(out, wall), compare_md(out), compare_df(out), s, status


CSS = '''
.rf-cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:6px 0 2px}
@media (max-width:900px){.rf-cards{grid-template-columns:repeat(2,minmax(0,1fr))}}
.rf-card{border:1.5px solid #e5e7eb;border-radius:12px;padding:12px 14px;background:#fff;min-height:110px}
.rf-k{font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:#6b7280;font-weight:600}
.rf-v{font-size:30px;font-weight:700;line-height:1.25;margin:4px 0 2px;color:#111827}
.rf-u{font-size:15px;font-weight:500;color:#6b7280}
.rf-s{font-size:12px;color:#6b7280}
.rf-r{margin:8px 0 0;padding-left:18px;font-size:12.5px;color:#374151;line-height:1.45}
.rf-note{margin-top:8px;font-size:11.5px;color:#92400e;background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:6px 8px;line-height:1.4}
.rf-chips{display:flex;flex-wrap:wrap;gap:4px;margin:6px 0 4px}
.rf-chip{font-size:11.5px;border:1px solid #d1d5db;border-radius:999px;padding:2px 8px;color:#374151;background:#f9fafb}
.rf-chip-sel{border-color:#2563eb;background:#dbeafe;color:#1e3a8a;font-weight:700}
.rf-conf .rf-v{font-size:22px}
.rf-foot{border-top:1px solid #e5e7eb;margin-top:14px;padding:10px 4px;font-weight:700;color:#991b1b;text-align:center}
.rf-title h1{margin:0 0 2px;font-size:26px}
.rf-title p{margin:0;color:#6b7280}
'''


def build_app():
    theme = gr.themes.Soft(primary_hue='emerald') if hasattr(gr, 'themes') else None
    bk = {}
    sig = inspect.signature(gr.Blocks.__init__).parameters
    if 'css' in sig: bk['css'] = CSS
    if 'theme' in sig and theme is not None: bk['theme'] = theme
    if 'title' in sig: bk['title'] = 'RelyFetal — demo dò nhịp tim thai đơn kênh'
    first_show = list(SHOWCASE_LABELS)[0] if SHOWCASE_LABELS else None
    with gr.Blocks(**bk) as demo:
        gr.HTML('<div class="rf-title"><h1>RelyFetal — dò phức bộ QRS thai nhi từ điện tim ổ bụng <em>đơn kênh</em>, có cổng từ chối</h1>'
                '<p>FetalQRS-TCN (113 481 tham số, CPU, huấn luyện 22 chủ thể) · khử QRS mẹ bằng mẫu trung vị · '
                'chọn kênh mù nhãn <b>peakprob</b> (mặc định, hậu kiểm) hoặc PSD · đèn tin cậy theo đoạn 4 s. '
                f'<b style="color:#991b1b">{DISCLAIMER}</b></p></div>')
        with gr.Row(equal_height=True):
            source = gr.Radio(['Minh hoạ (5 bản)', 'Bản ghi mẫu', 'Tải lên file'], value='Minh hoạ (5 bản)', label='Nguồn dữ liệu', scale=1)
            showcase = gr.Dropdown(choices=list(SHOWCASE_LABELS), value=first_show,
                                   label='Bản ghi minh hoạ cho buổi demo (thứ tự gợi ý: từ trên xuống)', scale=4)
            sample = gr.Dropdown(choices=list(REC_LABELS), value=(list(REC_LABELS)[0] if REC_LABELS else None),
                                 label=f'Mọi bản ghi mẫu trên đĩa ({len(REC_LABELS)}): ADFECGDB · CinC 2013 (cờ rò rỉ/nhãn sai) · Silesia',
                                 visible=False, scale=4)
            upload = gr.File(label='Tải lên: .edf · .hea+.dat(+.fqrs) · .csv · .npy · .txt (kèm nhãn .txt tuỳ chọn)',
                             file_count='multiple', visible=False, scale=3)
            fs_in = gr.Number(value=1000, label='fs của CSV/NPY (Hz)', precision=0, visible=False, scale=1)
            lead = gr.Dropdown(choices=LEAD_CHOICES, value=LEAD_CHOICES[0], label='Kênh bụng', scale=2)
            conf = gr.Dropdown(choices=CONF_CHOICES, value=CONF_CHOICES[0], label='Đèn tin cậy', scale=2)
            btn = gr.Button('Phân tích', variant='primary', scale=1)
        status = gr.Markdown('Chọn bản ghi rồi bấm **Phân tích**.')
        cards = gr.HTML()
        with gr.Tabs():
            with gr.Tab('Tín hiệu (5 tầng)'):
                fig_sig = gr.Plot(label='Từ tín hiệu thô đến kết quả')
            with gr.Tab('Chọn kênh — cả 4 kênh'):
                leads_txt = gr.Markdown()
                fig_leads = gr.Plot(label='Phần dư và đỉnh mô hình trên từng kênh; kênh được chọn tô nền xanh')
            with gr.Tab('Nhịp tim thai + đèn đoạn'):
                fig_fhr = gr.Plot(label='fHR và điểm tin cậy theo đoạn 4 s')
            with gr.Tab('So sánh với nhãn'):
                cmp_md = gr.Markdown()
                cmp_df = gr.DataFrame(label='Danh sách sự kiện (FP, FN trước; TP tối đa 200 dòng)', wrap=True)
            with gr.Tab('Kết quả tổng hợp (60 bản sạch)'):
                gr.Markdown(SUMMARY_MD)
            with gr.Tab('Nhật ký (JSON)'):
                js = gr.JSON(label='Tóm tắt phân tích — sao chép vào báo cáo')
        gr.HTML(f'<div class="rf-foot">{DISCLAIMER}</div>')

        def _toggle(src):
            up = str(src).startswith('Tải'); show = str(src).startswith('Minh')
            return gr.update(visible=show), gr.update(visible=not up and not show), gr.update(visible=up), gr.update(visible=up)
        source.change(_toggle, source, [showcase, sample, upload, fs_in])
        outs = [fig_sig, fig_leads, leads_txt, fig_fhr, cards, cmp_md, cmp_df, js, status]
        ins = [source, upload, sample, lead, fs_in, conf, showcase]
        btn.click(run, ins, outs)
        if SHOWCASE_LABELS and os.environ.get('RELYFETAL_AUTORUN', '1') == '1':
            demo.load(run, ins, outs)     # mở trang là thấy ngay kết quả r01
    return demo


def launch_kwargs(**extra):
    """theme/css chuyển sang launch() ở Gradio >= 6 -- xử lý cả hai đời."""
    kw = dict(server_name='127.0.0.1', inbrowser=False, show_error=True)
    sig = inspect.signature(gr.Blocks.launch).parameters
    if 'css' in sig and 'css' not in inspect.signature(gr.Blocks.__init__).parameters:
        kw['css'] = CSS
    if 'theme' in sig and 'theme' not in inspect.signature(gr.Blocks.__init__).parameters and hasattr(gr, 'themes'):
        kw['theme'] = gr.themes.Soft(primary_hue='emerald')
    kw.update(extra)
    return {k: v for k, v in kw.items() if k in sig}


demo = build_app()

if __name__ == '__main__':
    port = int(os.environ.get('RELYFETAL_PORT', '7860'))
    print(f'RelyFetal demo: http://127.0.0.1:{port}   ({DISCLAIMER})')
    demo.launch(**launch_kwargs(server_port=port))
