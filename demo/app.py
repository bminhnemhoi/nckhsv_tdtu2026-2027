# -*- coding: utf-8 -*-
"""
RelyFetal -- demo web một trang (Gradio + Plotly), chạy cục bộ.

    python demo/app.py            # mở http://127.0.0.1:7860

Mọi tính toán nằm ở demo/core.py (không phụ thuộc gradio); file này chỉ dựng giao diện và vẽ.
Trạng thái đề tài phản ánh trong demo (xem docs/HUONG_DAN_DEMO_v2.md; bản 8 tab cũ: docs/HUONG_DAN_DEMO_v1.md):
  * mô hình 22 chủ thể (fetalqrs_tcn_22_*): fold không chứa chủ thể cho 22 ca, production cho zero-shot
  * chọn kênh mù nhãn: peakprob (mặc định, HẬU KIỂM) và PSD (Power-MF) để so sánh; hiển thị cả 4 kênh
  * cổng tin cậy: bản hiệu chuẩn trên mô hình 5 ca (fsqi/gate_classical.pkl) -- ghi rõ trên giao diện
  * bảng tổng hợp đọc từ analysis/dulieu_results.json (60 bản CinC sạch) -- không ghi cứng con số
Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.
"""
import os, sys, time, inspect, json, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

import numpy as np
import pandas as pd
import gradio as gr
import fastapi
import uvicorn
import markdown
from fastapi.responses import HTMLResponse, JSONResponse
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import core
from monitor_template import MONITOR_HTML
from research_template import RESEARCH_HTML

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
COL_BAO = '#4c1d95'                 # chế độ trình bày: nhịp mạng đã báo (chưa biết đúng/sai)

SHOWCASE_WHY = {
    'r01': 'ADFECGDB, dễ — fold 22 ca chưa thấy r01; mọi quy tắc chọn kênh đều cho F1 ≈ 100',
    'a09': 'CinC sạch, zero-shot — PSD chọn kênh sai (F1 ≈ 19); peakprob chọn kênh khác (F1 ≈ 94)',
    'B2_03': 'Silesia chuyển dạ, khó — mô hình thất bại một phần; cổng tin cậy phải báo ĐỎ/VÀNG',
    'a02': 'CinC sạch — mô hình bám nhịp MẸ; cổng "bám nhịp mẹ" phải báo ĐỎ',
    'a27': 'CinC sạch, cả bốn dây đều kém (F1 ≤ 33) — hệ thống phải nói "tôi không chắc"',
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
        for k, nm in (('psd', 'PSD (Power-MF, Jaeger 2024)'), ('gate', 'gate — quy tắc kế hoạch chọn (KHAI BÁO TRƯỚC)'),
                      ('gate4', 'gate4 — cũng ghi trước khi chạy, qua Holm'), ('rrcv', 'rrcv'),
                      ('peakprob', 'peakprob — HẬU KIỂM, chọn sau khi xem kết quả (mặc định demo)')):
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
{core.GATE_NOTE}

* **Cổng đang chạy trong demo** (hiệu chuẩn trên mô hình 5 ca): AUROC trong bản ghi **0,721** [0,517; 0,898], đo trên 5 bản CinC
  khi ghép với mô hình 5 ca (`analysis/stats_results.json` → `gate_auroc_cinc`). Ghép với mô hình 22 ca đang chạy: **chưa đo lại**.
* **Cổng 22 ca** (LOSO, `analysis/gate22_results.json`, chưa đưa vào demo): AUROC trong bản ghi **0,934** [0,872; 0,981],
  tính trên **11/22** chủ thể có đoạn xấu. 3 bản khó nhất (B2_03, B1_07, B1_06) xếp đúng hạng 1-2-3 — nhưng 5/24 quy tắc một
  đặc trưng cũng xếp đúng 3/3, nên chưa được coi là bằng chứng mạnh.
* **Cổng không độc lập với mạng:** 2/12 chỉ số là xác suất đầu ra của mạng, 4/12 tính trên nhịp mạng tìm ra; chỉ số quan trọng
  nhất là độ đều nhịp `rr_cv` (`fsqi/gate.py`, `analysis/gate22_results.json` → `permutation_importance_delta_auroc`).

*Mọi con số CinC trên 75 bản ghi đã công bố trước đây đều bị **rút** (15/75 bản là bản sao huấn luyện). Không có con số nào trong demo lấy từ 75 bản.*
''')
    # số kiểu Việt: dấu thập phân là dấu phẩy (bảng này không có số hàng nghìn, không có đường dẫn chứa "chữ số.chữ số")
    return re.sub(r'(?<=\d)\.(?=\d)', ',', '\n'.join(parts))


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


def leads_figure(out, vi_fmt=False):
    """Cả K kênh: phần dư + đỉnh mô hình (+ nhãn); kênh được chọn tô nền xanh. Chỉ có ở chế độ tự động.
    vi_fmt=True (chế độ trình bày): tiêu đề rút gọn 'Dây k — ĐƯỢC CHỌN · điểm tin của mạng 0,990 · F1 94,25', số kiểu Việt."""
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
    # điểm trùng nhau khi làm tròn 3 chữ số (ví dụ r01: 0,998 cả bốn dây) -> in 4 chữ số để thấy vì sao chọn dây đó
    pp = [L[k]['peakprob'] for k in ks if L[k].get('peakprob') is not None]
    nd_pp = 4 if len({round(v, 3) for v in pp}) < len(pp) else 3
    for k in ks:
        d = L[k]
        sc = (f'peakprob = {_vn(d["peakprob"], 3)}' if d.get('peakprob') is not None else '') + f' · PSD = {_sci_vi(d["psd"])}'
        extra = ''
        if 'n_beats' in d:
            extra = f' · {d["n_beats"]} nhịp · fHR {d["fhr_mean"]:.0f} nhịp/phút' if np.isfinite(d['fhr_mean']) else f' · {d["n_beats"]} nhịp'
        if 'F1' in d:
            extra += f' · F1 = {_vn(d["F1"])}'
        if vi_fmt:
            t = f'Dây {k}' + (' — ĐƯỢC CHỌN' if d['selected'] else '')
            if d.get('peakprob') is not None:
                t += f' · điểm tin của mạng {_vn(d["peakprob"], nd_pp)}'
            if 'F1' in d:
                t += f' · F1 {_vn(d["F1"])}'
            titles.append(t)
            continue
        titles.append(f'Kênh {k} ({d["name"]}){" — ĐƯỢC CHỌN bởi " + rule if d["selected"] else ""} · {sc.lstrip(" ·")}{extra}')
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
    if vi_fmt:
        fig.update_layout(separators=', ', font=dict(size=13))     # trục số: dấu phẩy thập phân
        for tr in fig.data:
            if tr.name == 'đỉnh mô hình':            # cùng màu tím với bước 3: nhịp máy báo, chưa biết đúng/sai
                tr.marker.color = COL_BAO
            tr.name = {'đỉnh mô hình': 'nhịp máy tìm', 'nhãn nhịp thai': 'nhịp thai theo đáp án'}.get(tr.name, tr.name)
        fig.update_xaxes(title_text='thời gian (giây) — kéo để phóng to, nhấp đúp để xem toàn bộ', row=K, col=1)
        fig.update_yaxes(showticklabels=False)                   # đơn vị biên độ khác nhau giữa các máy ghi
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
        pp = _vn(d['peakprob'], 3) if d.get('peakprob') is not None else '—'
        nb = d.get('n_beats', '—'); fh = f'{d["fhr_mean"]:.0f}' if np.isfinite(d.get('fhr_mean', np.nan)) else '—'
        cells = f'| {k} ({d["name"]}) | {pp} | {_sci_vi(d["psd"])} | {nb} | {fh} | '
        if has_lab:
            cells += f'{_vn(d["F1"])} | {_vn(d["Se"])} | {_vn(d["PPV"])} | '
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


def fhr_figure(out, vi_fmt=False):
    """fHR theo cửa sổ 4 s (trên) + điểm tin cậy từng đoạn 4 s (dưới); đoạn ĐỎ tô nền trên cả hai.
    vi_fmt=True (chế độ trình bày): số kiểu Việt (dấu phẩy) trên chú thích và trục."""
    segs = out['confidence'].get('segments')
    nf = lambda v, nd: _vn(v, nd)     # noqa: E731  -- số kiểu Việt ở cả hai chế độ
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.68, 0.32], vertical_spacing=0.08,
                        subplot_titles=['Nhịp tim thai (median RR trong từng cửa sổ 4 s)',
                                        'Điểm tin cậy từng đoạn 4 s — p(đoạn lỗi) của cổng học; ' +
                                        ('nền đỏ = đoạn bị TỪ CHỐI' if segs else 'chế độ luật: không có điểm theo đoạn')])
    lab = out.get('labels_1000')
    if lab is not None:
        rt, rb = core.fhr_series(np.asarray(lab) / (out['fs_raw'] / out['fs']), len(out['residual_250']))
        fig.add_trace(go.Scatter(x=rt, y=rb, mode='lines+markers', name='Theo nhãn', line=dict(color='#111827', width=1.5, dash='dot'),
                                 marker=dict(size=5), hovertemplate='%{x:.0f} s<br>%{y:.1f} bpm<extra>nhãn</extra>'), row=1, col=1)
    fig.add_trace(go.Scatter(x=out['fhr_time_s'], y=out['fhr_series'], mode='lines+markers', name='Mô hình (cửa sổ 4 s)',
                             line=dict(color=COL['filt'], width=2.5), marker=dict(size=7),
                             hovertemplate='%{x:.0f} s<br>%{y:.1f} bpm<extra>mô hình</extra>'), row=1, col=1)
    # dải bình thường vẽ SAU khi ô đã có đường: plotly 7 bỏ qua add_hrect trên ô còn trống (không báo lỗi)
    fig.add_hrect(y0=110, y1=160, fillcolor='rgba(22,163,74,0.10)', line_width=0, row=1, col=1, layer='below',
                  annotation_text='vùng bình thường 110–160 bpm', annotation_position='top left',
                  annotation_font=dict(color='#15803d', size=12))
    if segs:
        n = len(segs['p_bad']); seg_s = float(segs['seg_s'])
        x0 = np.arange(n) * seg_s; xc = x0 + seg_s / 2
        lv = segs['level']; pb = np.asarray(segs['p_bad'], float)
        fig.add_trace(go.Bar(x=xc, y=pb, width=seg_s * 0.9, marker_color=[SEG_COLOR[l] for l in lv], name='p(đoạn lỗi)',
                             hovertemplate='%{x:.0f} s<br>p(đoạn lỗi) = %{y:.3f}<extra>đèn đoạn</extra>'), row=2, col=1)
        fig.add_hline(y=segs['q1'], line=dict(color=SEG_COLOR['xanh'], width=1, dash='dot'), row=2, col=1,
                      annotation_text=f'xanh < {nf(segs["q1"], 3)}', annotation_position='top right', annotation_font=dict(size=10))
        fig.add_hline(y=segs['q2'], line=dict(color=SEG_COLOR['do'], width=1, dash='dot'), row=2, col=1,
                      annotation_text=f'đỏ > {nf(segs["q2"], 3)}', annotation_position='bottom right', annotation_font=dict(size=10))
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
                      annotation_text=f'trung bình {nf(out["fhr_mean"], 0)} bpm', annotation_position='bottom right')
    fig.update_yaxes(title_text='bpm', range=[60, 220], showgrid=True, gridcolor='rgba(0,0,0,0.06)', row=1, col=1)
    fig.update_yaxes(title_text='p(đoạn lỗi)', range=[0, 1.02], showgrid=True, gridcolor='rgba(0,0,0,0.06)', row=2, col=1)
    fig.update_xaxes(title_text='thời gian (s)', showgrid=True, gridcolor='rgba(0,0,0,0.06)', row=2, col=1)
    fig.update_layout(height=560, margin=dict(l=60, r=20, t=40, b=50), plot_bgcolor='white', paper_bgcolor='white',
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), hovermode='x unified',
                      bargap=0)
    if vi_fmt:
        fig.update_layout(separators=', ')
        # chế độ trình bày: chữ thường thay cho thuật ngữ, 'nhịp/phút' thay cho 'bpm'
        ten = {'Nhịp tim thai (median RR': 'Nhịp tim thai theo thời gian (mỗi điểm là một cửa sổ 4 giây)',
               'Điểm tin cậy từng đoạn': 'Mức đáng ngờ của từng đoạn 4 giây — cột càng cao càng đáng ngờ; '
                                        + ('nền đỏ = đoạn hệ thống từ chối trả lời' if segs else 'chế độ luật: không có điểm theo đoạn')}
        for a in fig.layout.annotations:
            for k, v in ten.items():
                if a.text and a.text.startswith(k):
                    a.text = v
            if a.text:
                a.text = a.text.replace(' bpm', ' nhịp/phút').replace('(từ chối)', '(từ chối trả lời)')
                if a.text.startswith('trung bình') and out['confidence'].get('level') == 'thap':
                    a.text = a.text.replace('trung bình', 'TB') + ' (đèn đỏ: không dùng)'
        for tr in fig.data:
            if getattr(tr, 'hovertemplate', None):
                tr.hovertemplate = tr.hovertemplate.replace(' bpm', ' nhịp/phút').replace('p(đoạn lỗi)', 'mức đáng ngờ')
            nm = getattr(tr, 'name', None)
            tr.name = {'p(đoạn lỗi)': 'mức đáng ngờ của đoạn', 'Theo nhãn': 'Theo đáp án',
                       'Mô hình (cửa sổ 4 s)': 'Hệ thống (mỗi 4 giây)'}.get(nm, nm)
        fig.update_yaxes(title_text='nhịp/phút', row=1, col=1)
        fig.update_yaxes(title_text='mức đáng ngờ', row=2, col=1)
        fig.update_xaxes(title_text='thời gian (giây)', row=2, col=1)
    for a in fig.layout.annotations:
        if a.text and (a.text.startswith('Nhịp tim') or a.text.startswith('Điểm tin cậy') or a.text.startswith('Mức đáng ngờ')):
            a.font.size = 13; a.x = 0.0; a.xanchor = 'left'
    return fig


# =========================================================================== thẻ số & bảng
def _fmt(v, f='{:.0f}'):
    return f.format(v) if v is not None and np.isfinite(v) else '—'


def cards_html(out, wall_ms=None):
    c = out['confidence']
    reasons = ''.join(f'<li>{_ly_do_vi(r)}</li>' for r in c['reasons'])
    mode = out.get('lead_mode', '')
    ck = out.get('checkpoint_note', out['checkpoint'])
    lat = out['latency_ms']; lat_all = out.get('latency_all_leads_ms')
    L = out.get('leads')
    if L:
        key = 'peakprob' if out.get('lead_rule') == 'peakprob' else 'psd'
        fmt = (lambda v: _vn(v, 3)) if key == 'peakprob' else _sci_vi
        chips = ''.join(f'<span class="rf-chip{" rf-chip-sel" if L[k]["selected"] else ""}">k{k}: {fmt(L[k][key])}'
                        + (f' · F1 {_vn(L[k]["F1"], 1)}' if 'F1' in L[k] else '') + '</span>' for k in sorted(L))
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
    <div class="rf-s">điểm {_vn(c['score'])} / 1 — chế độ <b>{core.CONF_MODE_LABEL.get(c.get('mode', 'luat'), c.get('mode'))}</b>{f" · {_vn_int(c['components'].get('gate_ms', 0))} ms" if c.get('mode') == 'hoc' else ''}</div>
    <ul class="rf-r">{reasons}</ul>
    <div class="rf-note">⚠ {core.GATE_NOTE}</div></div>
  <div class="rf-card"><div class="rf-k">Thời gian xử lý</div>
    <div class="rf-v">{_vn_int(lat)}<span class="rf-u"> ms</span></div>
    <div class="rf-s">kênh đã chọn: tiền xử lý + khử mẹ + mô hình, CPU {core.torch.get_num_threads()} luồng
    {f"<br>cả {out.get('n_leads', '?')} kênh (chi phí thật của quy tắc tự động): {_vn_int(lat_all)} ms" if lat_all else ""}
    {f"<br>toàn bộ kể cả đọc file &amp; vẽ: {_vn_int(wall_ms)} ms" if wall_ms else ""}<br>checkpoint: {ck}</div></div>
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
| **{_vn(m['Se'])} %** | **{_vn(m['PPV'])} %** | **{_vn(m['F1'])}** | {_vn(m['jitter_ms'])} ms |

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
        fmt = (lambda v: _vn(v, 3)) if key == 'peakprob' else _sci_vi
        lead_txt = f' · điểm {key} từng kênh: ' + '; '.join(f'k{k} = {fmt(v)}' for k, v in out['lead_scores'].items())
    note = out.get('record_note') or ''
    status = (f'Đã phân tích **{out["record"]}** ({out["source"]}, {out["duration_s"]:.0f} giây, {rec["signals"].shape[0]} kênh'
              f'{"; " + note if note else ""}) — kênh **{out["lead"]}** ({out["lead_mode"]}){lead_txt} — checkpoint *{out["checkpoint_note"]}* '
              f'— đèn tin cậy: *{core.CONF_MODE_LABEL[out["confidence_mode"]]}*.')
    return fig1, fig3, leads_md(out), fig2, cards_html(out, wall), compare_md(out), compare_df(out), s, status



# =========================================================================== A1: tab "Dữ liệu của nhóm"
DS_LABELS = {core.DATASET_LABEL[k]: k for k in core.DATASET_KEYS}
DS_COLS = ['Bản ghi', 'Đường dẫn trên đĩa', 'Định dạng', 'fs gốc (Hz)', 'Dài (s)',
           'Số kênh bụng', 'Số nhịp trong nhãn', 'Nguồn nhãn', 'Ghi chú']

DS_FORMAT_MD = {
    'adfecgdb': '''
**ADFECGDB (Abdominal and Direct Fetal ECG Database, PhysioNet)** — 5 bản ghi `r01 r04 r07 r08 r10`.

* Mỗi bản ghi là **một tệp `.edf`** (European Data Format — nhị phân, header văn bản 256 byte/kênh nằm ngay đầu tệp)
  cộng **một tệp `.edf.qrs`** (chú giải WFDB nhị phân: vị trí từng nhịp QRS **thai**).
* Bên trong `.edf` có 5 kênh: `Direct_1` (FECG lấy **trực tiếp từ điện cực gắn trên da đầu thai** — đây là nguồn
  sinh ra nhãn) và `Abdomen_1..4` (4 đạo trình **bụng** mẹ — đây là thứ mô hình được phép nhìn).
  Demo **bỏ kênh `Direct_1`** khi phân tích: nếu đưa kênh trực tiếp vào thì bài toán không còn ý nghĩa.
* `.edf` là **nhị phân** nên không in nguyên văn được; siêu dữ liệu ở bảng trên đọc bằng `mne.io.read_raw_edf`.
''',
    'silesia_b1': '''
**Silesia B1 — thai kỳ** (Silesian University of Technology, 10 bản ghi ~20 phút).

* `B1_abSignals_XX.ecg` — **nhị phân**, `int16` **big-endian**, 8 cột xen kẽ; giá trị thật = số nguyên / 10.
  Demo chỉ dùng **4 cột đầu** = 4 đạo trình bụng A1..A4, lấy mẫu **500 Hz**.
* `B1_abSignals_XX.txt` — cùng nội dung nhưng dạng văn bản (dùng để đối chiếu định dạng, `silesia_loader.format_check`).
* `B1_Fetal_R_XX.txt` — **nhãn nhịp thai**: mỗi dòng `chỉ_số_mẫu  cờ`, cờ = 1 nghĩa là nhịp đã được soát tay.
* `B1_Maternal_R_XX.txt` — nhãn nhịp **mẹ** (dùng kiểm tra khâu khử mẹ, không dùng để chấm điểm).
* **Nguồn nhãn GIÁN TIẾP:** nhóm tác giả khử QRS mẹ ngay trên tín hiệu bụng rồi dò nhịp thai và soát lại —
  **không có điện cực da đầu**. Đây là điểm yếu phải nói rõ khi báo cáo B1.
''',
    'silesia_b2': '''
**Silesia B2 — chuyển dạ** (12 bản ghi 5 phút). Cấu trúc tệp giống hệt B1, thêm một tệp:

* `B2_abSignals_XX.ecg` — 4 đạo trình bụng A1..A4, `int16` big-endian, 8 cột, **500 Hz**, giá trị = int/10.
* `B2_dFECG_XX.ecg` — **FECG trực tiếp từ điện cực da đầu thai**, 1000 Hz, 2 cột (thô + đã lọc bởi tác giả).
  Đây là nguồn sinh nhãn; **không đưa vào mô hình**.
* `B2_Fetal_R_XX.txt` — nhãn nhịp thai (chỉ số mẫu **ở 1000 Hz**, vì đếm trên dFECG).
* **5 bản B2_01, B2_02, B2_07, B2_10, B2_11 trùng với r01, r10, r04, r07, r08 của ADFECGDB** —
  đã loại khỏi 22 chủ thể để không đếm một sản phụ hai lần (xem cột Ghi chú).
''',
    'cinc_sach': '''
**CinC 2013 set-a — 60 bản SẠCH** (PhysioNet/CinC Challenge 2013, mỗi bản 60 s).

* `aXX.hea` — **header WFDB, văn bản thuần, mở bằng Notepad đọc được** (xem ví dụ in nguyên văn bên dưới).
  Dòng 1: `<tên> <số kênh> <fs> <số mẫu>`. Mỗi dòng sau: tệp dữ liệu, độ phân giải bit, hệ số/đơn vị, ... , tên kênh.
* `aXX.dat` — **nhị phân**, `int16`, 4 kênh xen kẽ, 1000 Hz; giá trị vật lý = (số nguyên − offset) / hệ_số.
* `aXX.fqrs` — **chú giải WFDB nhị phân**: vị trí từng nhịp **thai**, do **người chấm độc lập** của ban tổ chức đánh dấu
  (không phải điện cực da đầu). Đây là lý do 7 bản `a33 a38 a47 a52 a54 a71 a74` có nhãn sai đã khai báo trước.
* Đây là bộ **ngoài miền**: đã kiểm là không trùng dữ liệu huấn luyện (tương quan chéo tối đa 0,62). Nhiều khả năng khác thiết bị và
  dân số, nhưng ban tổ chức không công bố nguồn của từng bản. Số chính trên bộ này (F1 trung bình, `analysis/dulieu_results.json`):
  PSD 74,28 · gate 80,72 (quy tắc kế hoạch chọn trước khi chạy, trượt Holm) · gate4 81,01 (cũng ghi trước khi chạy) ·
  peakprob 82,01 (chọn sau khi xem kết quả) · trần nếu biết trước dây tốt nhất 83,60.
''',
    'cinc_nhiem': '''
**CinC 2013 set-a — 15 bản NHIỄM.** Cấu trúc tệp giống 60 bản sạch (`.hea` + `.dat` + `.fqrs`), nhưng **nội dung tín hiệu
là bản sao nguyên văn của ADFECGDB** — tức là trùng với dữ liệu huấn luyện của nhóm.

* Mỗi bản ADFECGDB xuất hiện **đúng 3 lần** theo cửa sổ 0–60 s / 120–180 s / 240–300 s:
  `r01 → a04, a05, a22` · `r04 → a13, a20, a25` · `r07 → a19, a23, a24` · `r08 → a08, a15, a17` · `r10 → a03, a12, a14`.
* Kiểm chứng: **NCC = 1,0000** trên cả 4 kênh đúng thứ tự, **lệch RR = 0,0 ms**.
  Đối chứng dương (trùng đã biết B2 ↔ PhysioNet, cùng sản phụ nhưng khác xử lý) chỉ 0,856–0,984;
  60 bản còn lại tối đa 0,62.
* **Như ban tổ chức đã ghi nhận** (Silva *et al.*, CinC 2013;40:149-152, Bảng 1 *"Abdominal and Direct FECG — 25"*;
  Clifford *et al.*, Physiol Meas 2014;35:1521, cảnh báo nguyên văn), set-a **có chứa** bản ghi ADFECGDB.
  Đóng góp của nhóm chỉ là **định danh đúng 15 bản nào** và **đo mức thổi phồng**
  (m5 +7,18 · m12 +6,41 · m22 +5,12 · oracle +3,27 điểm F1).
* **Mọi con số CinC tính trên 75 bản đều đã bị RÚT.** Bộ này để trong demo *chỉ nhằm minh hoạ sự trùng lặp*,
  không được dùng làm kết quả.
''',
}

DS_HOWTO_MD = '''
#### Cách đọc hình này

Mỗi đường là **một đạo trình điện cực dán trên bụng mẹ** trong 10 giây đầu bản ghi; các đường được xếp chồng
lên nhau (đã dời lên/xuống cho khỏi đè) nên **chỉ so hình dạng, đừng so độ cao giữa các đường**.
Thường thì gai **to, đều** là nhịp tim của **mẹ** và nhịp **thai** nhỏ hơn, dễ lẫn trong nhiễu — đó là lý do phải có mô hình.
Nhưng không phải bản ghi nào cũng vậy: ở vài kênh (ví dụ `r01` kênh 4) gai thai to ngang gai mẹ, nên hãy dựa vào vạch đỏ. **Vạch đỏ đứng** là vị trí nhịp thai theo **nhãn tham chiếu**:
đếm vạch đỏ sẽ thấy thai thường đập nhanh hơn mẹ (tim thai bình thường khoảng 110–160 lần/phút; tim mẹ thường chậm hơn).
Nếu nhìn vào một vạch đỏ mà **không** thấy gai nào rõ ràng thì đó là đoạn khó — đây là dữ liệu thô, chưa lọc, chưa khử mẹ.
'''


def _rel(p):
    """Đường dẫn tương đối so với gốc dự án cho gọn bảng; giữ nguyên nếu nằm ngoài gốc."""
    try:
        r = os.path.relpath(p, ROOT)
        return p if r.startswith('..') else r
    except ValueError:
        return p


def dataset_table(key):
    rows, err = core.dataset_rows(key)
    if not rows:
        d, cmd = core.DATASET_DIR_HINT[key]
        msg = (f'### Chưa có bộ này trên đĩa\n\n{err}\n\nThư mục mong đợi: `{d}`\n\n'
               f'Lệnh tải lại:\n```\n{cmd}\n```')
        return pd.DataFrame(columns=DS_COLS), msg, gr.update(choices=[], value=None)
    df = pd.DataFrame([[r['ten'], _rel(r['duong_dan']), r['dinh_dang'], f'{r["fs_Hz"]:.0f}',
                        _vn(r['do_dai_s'], 1), r['so_kenh_bung'],
                        ('—' if r['so_nhip_nhan'] is None else r['so_nhip_nhan']),
                        r['nguon_nhan'], r['ghi_chu']] for r in rows], columns=DS_COLS)
    tong_s = sum(r['do_dai_s'] for r in rows)
    tong_nhip = sum(r['so_nhip_nhan'] or 0 for r in rows)
    head = (f"### {core.DATASET_LABEL[key]}\n\n"
            f"**{len(rows)} bản ghi** · tổng **{_vn(tong_s / 60, 1)} phút** · tổng **{_vn_int(tong_nhip)} nhịp thai trong nhãn** "
            f"· thư mục `{core.DATASET_DIR_HINT[key][0]}`.\n\n"
            f"Cột *Đường dẫn* ghi **tương đối so với gốc dự án** `{ROOT}`.\n\n"
            f"*Mọi ô trong bảng đọc trực tiếp từ tệp trên đĩa (header WFDB / header EDF / kích thước tệp .ecg / tệp nhãn) "
            f"— không có con số nào ghi cứng trong mã.*\n"
            + DS_FORMAT_MD[key])
    p, txt = core.header_example(key)
    if txt:
        nm = 'header `.hea`' if key.startswith('cinc') else 'tệp nhãn `.txt`'
        head += (f"\n**Ví dụ nội dung {nm} — in nguyên văn 8 dòng đầu của `{os.path.relpath(p, ROOT)}`:**\n"
                 f"```\n{txt}\n```\n")
    elif key == 'adfecgdb':
        head += "\n*(`.edf` là tệp nhị phân — không in nguyên văn được; xem cột Định dạng và tên kênh ở bảng trên.)*\n"
    names = [r['ten'] for r in rows]
    return df, head, gr.update(choices=names, value=names[0])


def dataset_raw_figure(key, name):
    """10 s đầu của TẤT CẢ kênh bụng, xếp chồng, vạch đỏ = nhãn nhịp thai."""
    t0 = time.perf_counter()
    try:
        rec = core.load_dataset_record(key, name)
    except Exception as e:                                      # noqa: BLE001
        raise gr.Error(f'Không đọc được bản ghi {name}: {e}')
    w = core.preview_window(rec, 0.0, VIEW_S)
    sig = w['signals']; K = w['n_leads']
    # dời từng kênh theo bội số của độ lệch chuẩn gộp -> các đường không đè nhau
    sd = float(np.median([np.std(sig[k]) for k in range(K)])) or 1.0
    step = 6.0 * sd
    fig = go.Figure()
    pal = ['#2563eb', '#0f766e', '#b45309', '#7c3aed', '#be123c', '#0369a1', '#4d7c0f', '#9333ea']
    for k in range(K):
        fig.add_trace(go.Scattergl(x=w['t'], y=sig[k] - np.mean(sig[k]) + (K - 1 - k) * step,
                                   name=f'kênh {k + 1} ({w["names"][k]})',
                                   line=dict(color=pal[k % len(pal)], width=1),
                                   hovertemplate='%{x:.3f} s<extra>' + f'kênh {k + 1}' + '</extra>'))
    if w['labels_s'] is not None and len(w['labels_s']):
        lo = -step; hi = K * step
        vx, vy = _vlines(w['labels_s'], lo, hi)
        fig.add_trace(go.Scattergl(x=vx, y=vy, mode='lines', name=f'nhãn nhịp thai: {len(w["labels_s"])} trong 10 s',
                                   line=dict(color='#dc2626', width=1.1), opacity=0.75, hoverinfo='skip'))
    fig.update_layout(height=160 + 110 * K, margin=dict(l=60, r=20, t=36, b=48),
                      title=dict(text=f'{name} — tín hiệu THÔ, {VIEW_S:.0f} s đầu, {K} kênh bụng (chưa lọc, chưa khử mẹ)',
                                 x=0.0, xanchor='left', font=dict(size=14)),
                      legend=dict(orientation='h', yanchor='bottom', y=1.015, xanchor='right', x=1, font=dict(size=11)),
                      plot_bgcolor='white', paper_bgcolor='white', hovermode='closest', dragmode='zoom')
    fig.update_xaxes(title_text='thời gian (giây) — kéo để phóng to, nhấp đúp để xem lại toàn bộ',
                     showgrid=True, gridcolor='rgba(0,0,0,0.06)', range=[0, VIEW_S])
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False,
                     title_text='các kênh xếp chồng (biên độ đã dời, không so được giữa kênh)')
    wall = (time.perf_counter() - t0) * 1000
    nb = 0 if w['labels_s'] is None else len(w['labels_s'])
    fs0 = float(rec.get('fs_orig', rec['fs']))
    fs_txt = (f"**{fs0:.0f} Hz**" if abs(fs0 - w['fs']) < 1e-9
              else f"**{fs0:.0f} Hz** (hình vẽ sau khi tái lấy mẫu về {w['fs']:.0f} Hz)")
    cap = (f"**{name}** · tần số gốc {fs_txt} · "
           f"**{K} kênh bụng** · bản ghi dài **{_vn(w['duration_s'], 1)} giây** · "
           f"**{nb} nhịp thai theo nhãn trong 10 s** đang hiển thị"
           + (f" (≈ {nb * 6} nhịp/phút)" if nb else " — bản ghi này không có nhãn trong cửa sổ đang xem") + ".\n\n"
           f"Định dạng: `{rec.get('dinh_dang', '?')}` · nguồn nhãn: *{rec.get('nguon_nhan', '?')}* · "
           f"tệp: `{os.path.relpath(rec.get('duong_dan', ''), ROOT) if rec.get('duong_dan') else '—'}`"
           + (f"\n\n> ⚠ {rec['note']}" if rec.get('note') else '')
           + f"\n\n*Đọc tệp + vẽ: {_vn_int(wall)} ms.*")
    return fig, cap


# =========================================================================== A2: tab "Tải dữ liệu mới"
UPLOAD_DIR_NEW = os.path.join(HERE, '_uploads_moi')
ASSET_DIR = os.path.join(HERE, 'assets')
VIDU_SIG = os.path.join(ASSET_DIR, 'vidu_tai_len.csv')
VIDU_LAB = os.path.join(ASSET_DIR, 'vidu_tai_len_nhan.csv')

UP_INTRO_MD = f'''
### Thử mô hình trên dữ liệu **chưa có trong đề tài**

**Định dạng nhận được** (chọn nhiều tệp cùng lúc ở ô bên dưới):

| Định dạng | Cần tải lên những gì | Có tự khai tần số không |
|---|---|---|
| `.edf` (European Data Format) | một tệp `.edf` (kèm `.edf.qrs` nếu có nhãn) | **Có** — ô fs bị bỏ qua |
| WFDB | **cả hai** tệp `.dat` **và** `.hea` | **Có** — ô fs bị bỏ qua |
| `.csv` | một tệp, mỗi cột một kênh (cho phép một dòng tiêu đề) | **Không** — phải nhập fs |
| `.npy` | mảng numpy 2 chiều (kênh × mẫu hoặc mẫu × kênh) | **Không** — phải nhập fs |
| `.txt` | như `.csv` nhưng ngăn cách bằng khoảng trắng | **Không** — phải nhập fs |

Bản ghi phải dài ít nhất **{core.MIN_DURATION_S:g} giây**. Tần số lấy mẫu chấp nhận
**{core.FS_MIN:g}–{core.FS_MAX:g} Hz** (mọi thứ được đưa về 1000 Hz rồi lọc xuống 250 Hz trước khi vào mô hình).

''' + ('''
**Tệp ví dụ có sẵn để thử ngay** (nằm trong `demo/assets/`):
`vidu_tai_len.csv` (30 s, 4 kênh, 1000 Hz) và `vidu_tai_len_nhan.csv` (một cột chỉ số mẫu).
> ⚠ Hai tệp này **trích từ bản ghi `a09` của CinC 2013 set-a** nên **KHÔNG phải "dữ liệu mới" thật** —
> chúng chỉ để thử luồng tải lên và xem giao diện phản ứng thế nào.
''' if os.path.isfile(VIDU_SIG) else '''
> ⚠ Chưa có tệp ví dụ trên máy này. Sinh lại bằng: `python demo/make_vidu_tai_len.py`
> (cắt 30 s từ bản `a09` của CinC 2013 set-a; hai tệp này cố ý không được commit vào kho).
''')

UP_WARN_NOLABEL = '''<div class="rf-warn"><b>Không có nhãn tham chiếu</b> → chỉ xem được <b>vị trí nhịp</b> và
<b>điểm tin cậy</b>. <b>KHÔNG tính được F1 / Se / PPV.</b> Muốn đánh giá định lượng thì phải có nhãn
(tệp <code>.qrs</code>/<code>.fqrs</code> đi kèm, hoặc tệp <code>.csv</code>/<code>.txt</code> một cột chỉ số mẫu).</div>'''

UP_WARN_DOMAIN = '''<div class="rf-warn rf-warn-red"><b>Cảnh báo về miền dữ liệu.</b> Mô hình được huấn luyện trên
<b>22 sản phụ</b> (ADFECGDB + Silesia). Trên <b>thiết bị khác hoặc dân số khác, kết quả có thể kém hơn nhiều</b>:
trên bộ ngoài miền CinC 2013 set-a (60 bản sạch), F1 mức bản ghi là <b>74,28</b> với quy tắc chọn kênh PSD,
<b>80,72</b> với quy tắc kế hoạch chọn trước (gate), <b>81,01</b> với gate4 và <b>82,01</b> với peakprob (chọn sau khi xem
kết quả) — thấp hơn hẳn mức 97,56 đo trong miền. Bốn phương pháp thích nghi miền đã thử đều
<b>thất bại</b> (chặn điện lưới +0,25 · tự huấn luyện nhãn giả −0,67 · AdaBN −1,58 · TENT −2,43), và nguyên nhân của
khoảng cách này <b>chưa xác định được</b>. <b>Đèn tin cậy (cổng từ chối) là thứ cần nhìn trước hết</b>, không phải số nhịp.</div>'''


def _api(name):
    """api_name= cho gradio_client, bỏ qua nếu bản gradio không nhận (giữ tương thích 4.x và 6.x)."""
    try:
        return {'api_name': name} if 'api_name' in inspect.signature(gr.Button.click).parameters else {}
    except (TypeError, ValueError):                             # noqa: BLE001
        return {}


def run_dataset(ds_label):
    """Đổi bộ dữ liệu -> (bảng bản ghi, mô tả định dạng, danh sách bản ghi để xem tín hiệu thô)."""
    return dataset_table(DS_LABELS[ds_label])


def run_dataset_raw(ds_label, rec_name):
    """Nút 'Xem tín hiệu thô' -> (hình 10 s mọi kênh, chú thích số thật đọc từ tệp)."""
    if not rec_name:
        raise gr.Error('Chưa chọn bản ghi nào — hãy chọn một bản ghi trong danh sách bên trái.')
    return dataset_raw_figure(DS_LABELS[ds_label], rec_name)


def _loi(msg):
    """gr.Error có tiêu đề tiếng Việt khi bản Gradio hỗ trợ (thay cho chữ 'Error')."""
    try:
        if 'title' in inspect.signature(gr.Error.__init__).parameters:
            return gr.Error(msg, title='Không đọc được dữ liệu')
    except (TypeError, ValueError):                             # noqa: BLE001
        pass
    return gr.Error(msg)


def _so_cot(path):
    """Số cột số của dòng dữ liệu đầu tiên trong .csv/.txt (bỏ dòng tiêu đề); None nếu không đọc được."""
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                parts = [p for p in re.split(r'[,;\s]+', line.strip()) if p]
                if not parts:
                    continue
                try:
                    [float(p) for p in parts]
                    return len(parts)
                except ValueError:
                    if i > 2:
                        return None
    except OSError:
        return None
    return None


def upload_clear():
    """Xoá kết quả cũ TRƯỚC mỗi lần phân tích tệp: nếu lần này lỗi, màn hình không còn số của tệp trước."""
    return ('', None, None, '', None, '', None, 'Đang đọc tệp và phân tích… kết quả cũ đã được xoá.')


def run_upload(files, fs_in, lead_choice, conf_choice, label_files):
    """Nút Phân tích của tab tải tệp. KHÔNG ném lỗi ra giao diện: lỗi hiện ở dòng trạng thái (ném gr.Error thì
    dòng "đang đọc tệp…" của upload_clear kẹt lại và hai nhãn "Error" tiếng Anh hiện trên ô kết quả)."""
    try:
        return _run_upload(files, fs_in, lead_choice, conf_choice, label_files)
    except gr.Error as e:
        msg = str(getattr(e, "message", None) or e)
        chinh, _, chi_tiet = msg.partition(" (Chi tiết kỹ thuật:")
        if chi_tiet:
            print(f"[tải tệp] chi tiết lỗi: {chi_tiet.rstrip(')')}", flush=True)
        return ('', None, None, '', None, '', None,
                f'**Không phân tích được tệp.** {chinh}\n\nKết quả cũ đã được xoá; sửa tệp rồi bấm **Phân tích** lại.')


def _run_upload(files, fs_in, lead_choice, conf_choice, label_files):
    t0 = time.perf_counter()
    paths = [f if isinstance(f, str) else getattr(f, 'name', str(f)) for f in (files or [])]
    lpaths = [f if isinstance(f, str) else getattr(f, 'name', str(f)) for f in (label_files or [])]
    # lỗi hay gặp: bỏ cả tệp tín hiệu lẫn tệp nhãn (một cột chỉ số mẫu) vào ô "Tệp bản ghi"
    bang = [p for p in paths if os.path.splitext(p)[1].lower() in ('.csv', '.txt')]
    if len(bang) >= 2:
        mot_cot = [p for p in bang if _so_cot(p) == 1]
        if mot_cot and len(mot_cot) < len(bang):
            raise _loi(f'Ô "Tệp bản ghi" đang có {len(bang)} tệp bảng số ({", ".join(os.path.basename(p) for p in bang)}). '
                       f'Tệp {", ".join(os.path.basename(p) for p in mot_cot)} chỉ có một cột, nhiều khả năng là tệp NHÃN: '
                       'hãy chuyển nó sang ô "Nhãn tham chiếu" rồi bấm Phân tích lại.')
    try:
        rec = core.doc_tai_len(paths, UPLOAD_DIR_NEW, fs=fs_in, label_paths=lpaths or None)
    except core.LoiDuLieu as e:
        raise _loi(str(e))
    except ValueError as e:
        ten = ', '.join(os.path.basename(p) for p in paths) or 'tệp tải lên'
        raise _loi(f'Không đọc được {ten} thành bảng số. Tệp .csv/.txt phải gồm các cột SỐ: mỗi cột một kênh, mỗi dòng một mẫu, '
                   f'được phép có một dòng tiêu đề; các dòng phải có cùng số cột. (Chi tiết kỹ thuật: {e})')
    except Exception as e:                                      # noqa: BLE001
        raise _loi(f'Không xử lý được tệp tải lên: {type(e).__name__}: {e}')
    try:
        out = core.analyze_record(rec, lead=_lead_arg(lead_choice),
                                  confidence_mode=CONF_MODE.get(conf_choice, 'hoc'))
    except Exception as e:                                      # noqa: BLE001
        raise _loi(f'Đọc tệp thành công nhưng phân tích thất bại: {type(e).__name__}: {e}')
    wall = (time.perf_counter() - t0) * 1000
    nhan = (f'**có nhãn** ({_vn_int(len(rec["labels"]))} nhịp, từ `{rec["nhan_tu"]}`) → tính được F1/Se/PPV'
            if rec['co_nhan'] else '**không có nhãn** → KHÔNG tính được F1/Se/PPV')
    fs_txt = (f'{rec["fs_orig"]:.0f} Hz (tệp tự khai)' if rec['fs_tu_khai']
              else f'{rec["fs_orig"]:.0f} Hz (bạn nhập — tệp không tự khai)')
    canh_list = list(rec.get('canh_bao', []))
    # nhịp tim suy ra ngoài khoảng tim thai -> gần như chắc nhập sai tần số lấy mẫu
    dur = float(rec['duration_s'])
    if rec['co_nhan'] and dur > 0:
        hr = len(rec['labels']) / dur * 60
        if hr < core.CONF_RULE['fhr_lo'] or hr > core.CONF_RULE['fhr_hi']:
            canh_list.append(f'Tệp nhãn cho {len(rec["labels"])} nhịp trong {_vn(dur, 1)} giây (≈ {hr:.0f} nhịp/phút), ngoài khoảng '
                             'thường gặp của tim thai (bình thường 110–160; demo cảnh báo ngoài 100–200). Kiểm tra lại ô tần số lấy mẫu.')
    elif np.isfinite(out['fhr_mean']) and not (core.CONF_RULE['fhr_lo'] <= out['fhr_mean'] <= core.CONF_RULE['fhr_hi']):
        canh_list.append(f'Nhịp tim máy tìm ≈ {out["fhr_mean"]:.0f} nhịp/phút, ngoài khoảng thường gặp của tim thai. '
                         'Nếu tệp không tự khai tần số, hãy kiểm tra lại ô tần số lấy mẫu.')
    canh = ''.join(f'\n\n> ⚠ {c}' for c in canh_list)
    status = (f'Đã phân tích tệp **{os.path.basename(rec["upload_main"])}** '
              f'({rec["source"]}, {_vn(rec["duration_s"], 1)} giây, {rec["signals"].shape[0]} kênh, {fs_txt}) — {nhan}.\n\n'
              f'Kênh được chọn: **{out["lead"]}** ({out["lead_mode"]}) · checkpoint *{out["checkpoint_note"]}* · '
              f'đèn tin cậy *{core.CONF_MODE_LABEL[out["confidence_mode"]]}* · '
              f'toàn bộ (đọc tệp + mô hình + vẽ): **{_vn_int(wall)} ms**.\n\n'
              f'Tệp đã nhận: `{", ".join(rec["upload_files"])}`.{canh}')
    return (cards_html(out, wall), signal_figure(out), leads_figure(out), leads_md(out),
            fhr_figure(out), compare_md(out), core.summary(out), status)

CSS = '''
/* --- thanh tab: XUONG HANG thay vi thu vao menu tran khi man hinh hep ---
   Gradio 6.x dung .tab-container; cac ban truoc dung .tab-nav. Nham ca hai.
   Phong hoc thuong 1366x768; khong sua thi hai tab cuoi bi nuot vao menu tran. */
.tab-container, .tab-nav, div.tab-nav, .tabs > .tab-nav, [class*="tab-container"] {
  flex-wrap: wrap !important;
  overflow: visible !important;
  row-gap: 2px !important;
  scrollbar-width: none;
}
.tab-container > button, .tab-nav > button, [class*="tab-container"] > button {
  white-space: nowrap; flex: 0 0 auto !important; font-size: 13.5px !important; padding: 6px 10px !important;
}
/* KHONG an nut '...' cua Gradio. Gradio 6.26 tu do do rong bang JS va chuyen tab khong vua vao menu tran,
   bat ke CSS xuong hang. Vong 9 an nut nay -> o 1366 px hai tab 'Tai du lieu moi' va 'Nhat ky (JSON)'
   bien mat, khong bam duoc (tim ra vong 10c bang Playwright). Giu nut de moi tab luon mo duoc. */
.tab-wrapper .overflow-menu button { font-weight: 700; }
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
.rf-warn{border:1.5px solid #fcd34d;background:#fffbeb;color:#78350f;border-radius:10px;padding:10px 12px;margin:8px 0;font-size:13.5px;line-height:1.55}
.rf-warn-red{border-color:#fca5a5;background:#fef2f2;color:#7f1d1d}
.rf-warn code{background:#fff;padding:1px 4px;border-radius:4px}
'''


# =========================================================================== T3: chế độ trình bày (kể chuyện, 5 bước)
# Mặc định khi mở trang. Không đụng vào 8 tab cũ (bọc trong "Chế độ chuyên gia", tắt sẵn).
# Mọi con số trên thẻ đọc từ JSON trên đĩa: demo/results/demo_check_showcase.json (F1, tỉ lệ bám nhịp mẹ)
# và analysis/chonkenh_results.json (F1 từng quy tắc chọn kênh của a09). Không ghi cứng.
import re

STORY_RECS = ('r01', 'a09', 'a02', 'a27')
STORY_N_STEPS = 5
STORY_STEPS = ('Tín hiệu thô từ bụng mẹ', 'Lọc và khử tim mẹ', 'Mô hình tìm nhịp thai',
               'Chọn đúng dây nào', 'Kết quả và độ tin cậy')
def _story_den_xanh():
    """(số bản đã chấm, số bản đèn xanh mà F1 < 90, F1 thấp nhất trong nhóm đèn xanh) ở chế độ 'hoc' — đọc từ đĩa."""
    try:
        d, _ = _load_json('demo/results/demo_check_2modes.json')
        s = d['summary_by_mode']['hoc']
        return int(s['n_records']), len(s['green_but_F1_below_90']), float(s['by_level']['cao']['F1_min'])
    except Exception:                                            # noqa: BLE001
        return None


_DX = _story_den_xanh()
STORY_CAPTION = (
    'Tín hiệu trên bụng mẹ chứa cả tim mẹ lẫn tim bé. Tim mẹ thường nổi trội; tim bé có bản ghi thấy rõ, có bản ghi lẫn hẳn trong nhiễu.',
    'Lọc nhiễu, tìm từng nhịp mẹ rồi trừ đi. Phần còn lại là nơi tìm tim bé; nếu còn gai lớn trùng vạch đỏ (nhịp mẹ) '
    'thì đó là dấu vết tim mẹ chưa trừ hết.',
    'Đường tím là mức tin của mạng; vạch tím đậm là nhịp mạng đã báo, chưa biết đúng hay sai. Hàng dưới mới so với đáp án.',
    'Cùng một sản phụ, mỗi dây cho một tín hiệu khác nhau. Hệ thống tự chọn một dây MÀ KHÔNG NHÌN ĐÁP ÁN — '
    'thường chọn đúng, không phải lúc nào cũng đúng.',
    'Mỗi đoạn 4 giây có một đèn: xanh là cổng không thấy dấu hiệu xấu, vàng là chưa chắc, đỏ là hệ thống từ chối trả lời. '
    + (f'Xanh không bảo đảm là đúng: trong {_DX[0]} bản đã chấm có {_DX[1]} bản đèn xanh mà F1 dưới 90, '
       f'thấp nhất {f"{_DX[2]:.2f}".replace(".", ",")}. '
       if _DX else 'Xanh không bảo đảm là đúng. ')
    + 'Cả bản ghi bị đèn đỏ khi quá 30 % số đoạn đỏ, hoặc khi máy bám nhịp mẹ; lúc đó mọi con số của bản ghi, kể cả nhịp tim, '
      'đều không được dùng.',
)
STORY_GATE_NOTE = ('Đèn trong bản demo này dùng cổng hiệu chuẩn trên mô hình 5 sản phụ. Ghép với mô hình đó, trong cùng một bản ghi '
                   'cổng xếp đoạn xấu trên đoạn tốt ở mức AUROC 0,721 (đo trên 5 bản CinC); ghép với mô hình 22 sản phụ đang chạy '
                   'thì chưa đo lại. Cổng dùng cả xác suất của mạng nên không độc lập với mạng. Cổng hiệu chuẩn trên 22 sản phụ '
                   'mới có ở dạng phân tích, chưa đưa vào demo.')
STORY_TITLE_HTML = ('<div class="rf-title"><h1>RelyFetal — tìm nhịp tim thai trong điện tim đo trên bụng mẹ, chỉ cần <em>một</em> kênh</h1>'
                    '<p>Bản ghi thử có 4 kênh (4 "dây"). Máy chạy trên cả 4, tự chọn một kênh để đọc, tách nhịp bé khỏi nhịp mẹ, '
                    'và báo "tôi không chắc" khi thấy dấu hiệu tín hiệu xấu (không phải lần nào cũng thấy). '
                    f'<b style="color:#991b1b">{DISCLAIMER}</b></p></div>')


def _vn(x, nd=2):
    """Số thập phân kiểu Việt (dấu phẩy); None/NaN -> '—'."""
    try:
        if x is None or not np.isfinite(float(x)):
            return '—'
    except (TypeError, ValueError):
        return '—'
    return f'{float(x):.{nd}f}'.replace('.', ',')


def _story_numbers():
    """Con số chính trên 4 thẻ, đọc từ JSON trên đĩa. Thiếu tệp -> thẻ ghi '—' (không bịa)."""
    n = {k: {} for k in STORY_RECS}
    try:
        d, _ = _load_json('demo/results/demo_check_showcase.json')
        for r in STORY_RECS:
            row = d.get('rows', {}).get(f'{r}_leadpeakprob', {})
            f1 = (row.get('metrics') or {}).get('F1')
            if f1 is not None:
                n[r]['F1'] = float(f1)
            comp = (row.get('confidence') or {}).get('components') or {}
            if comp.get('maternal_lock') is not None:
                n[r]['bam_me'] = float(comp['maternal_lock'])
            if (row.get('confidence') or {}).get('level'):
                n[r]['level'] = str(row['confidence']['level'])
            if comp.get('n_seg'):
                n[r]['n_seg'], n[r]['n_red'] = int(comp['n_seg']), int(comp.get('n_red', 0))
            if row.get('fhr_mean') is not None:
                n[r]['fhr'] = float(row['fhr_mean'])
            if row.get('n_labels') and row.get('duration_s'):            # nhịp tim theo đáp án ≈ số nhãn / thời lượng
                n[r]['fhr_dap_an'] = float(row['n_labels']) / float(row['duration_s']) * 60.0
            f1_leads = [float(v['F1']) for v in (row.get('leads') or {}).values() if v.get('F1') is not None]
            if f1_leads:
                n[r]['f1_min_day'], n[r]['f1_max_day'] = min(f1_leads), max(f1_leads)
    except Exception:                                            # noqa: BLE001
        pass
    try:
        d, _ = _load_json('analysis/chonkenh_results.json')
        f = d['F1_tung_ban_ghi']['cinc']
        for r in ('a09', 'a02', 'a27'):
            if r in f:
                n[r]['psd'] = float(f[r]['psd']); n[r]['peakprob'] = float(f[r]['peakprob'])
    except Exception:                                            # noqa: BLE001
        pass
    return n


def _story_60():
    """Dòng cho thanh tóm tắt: F1 trung bình 60 bản sạch theo quy tắc chọn dây.
    -> dict(psd, gate4, peakprob, oracle, n) hoặc None. Luôn báo đủ bốn số: cũ · khai báo trước · mới (hậu kiểm) · trần."""
    try:
        d, _ = _load_json('analysis/dulieu_results.json')
        B = d['chon_kenh_60_sach']['bang']
        return dict(psd=float(B['psd']['mean_60_sach']), gate=float(B['gate']['mean_60_sach']),
                    gate4=float(B['gate4']['mean_60_sach']),
                    peakprob=float(B['peakprob']['mean_60_sach']), oracle=float(B['oracle']['mean_60_sach']),
                    n=int(B['psd']['n']))
    except Exception:                                            # noqa: BLE001
        return None


def _story_rule_votes():
    """Bản CinC -> {chỉ số dây (1-based): [các quy tắc mù nhãn chọn dây đó]} từ analysis/chonkenh_results.json."""
    try:
        d, _ = _load_json('analysis/chonkenh_results.json')
        out = {}
        for rec, rules in d['chon_kenh_theo_quy_tac']['cinc'].items():
            v = {}
            # 7 quy tắc CHỌN một dây, không nhìn nhãn (fuse gộp dây nên không tính; lead0/oracle là tham chiếu)
            for rule in ('psd', 'gate', 'gate4', 'rrcv', 'peakprob', 'rrplaus', 'learned'):
                if rule in rules:
                    v.setdefault(int(rules[rule]) + 1, []).append(rule)
            out[rec] = v
        return out
    except Exception:                                            # noqa: BLE001
        return {}


STORY_NUM = _story_numbers()
STORY_60 = _story_60()
STORY_VOTES = _story_rule_votes()


def story_card_spec(name):
    """Nội dung 4 thẻ: bộ dữ liệu · dữ liệu này là gì · thẻ này cho thấy gì · một con số chính."""
    n = STORY_NUM.get(name, {})
    f1 = _vn(n.get('F1'))
    # đã kiểm: không trùng dữ liệu huấn luyện. "Máy ghi khác, nơi khác" của TỪNG bản là suy luận -> không viết như sự kiện
    cinc = 'bộ CinC 2013, không trùng dữ liệu huấn luyện (ngoài miền); nguồn thiết bị từng bản không được công bố'
    den = {'thap': 'đèn ĐỎ', 'trung_binh': 'đèn VÀNG', 'cao': 'đèn XANH'}.get(n.get('level'), 'đèn —')
    if name == 'r01':
        return dict(ten='Ca dễ', bo='ADFECGDB',
                    du_lieu='sản phụ chuyển dạ; đáp án từ điện cực trên da đầu bé; mô hình chưa từng thấy sản phụ này',
                    cho_thay='Hệ thống tìm đúng gần như mọi nhịp',
                    so=f'F1 {f1}', so_giai='F1 100 = không sót, không báo nhầm nhịp nào', mau='#16a34a')
    if name == 'a09':
        psd, pp = _vn(n.get('psd')), _vn(n.get('peakprob'))
        return dict(ten='Chọn dây quyết định', bo='CinC 2013', du_lieu=cinc,
                    cho_thay='Cùng một bản ghi, đổi cách chọn dây thì kết quả đổi hẳn',
                    so=f'{psd} → {pp}', so_giai='F1 khi chọn dây theo cách cũ → cách mới', mau='#2563eb')
    if name == 'a02':
        bm = f'{n["bam_me"] * 100:.0f} %' if 'bam_me' in n else '—'
        hr = (f'Máy báo nhịp tim {_fmt(n["fhr"])}: trông bình thường, nhưng đáp án ≈ {_fmt(n["fhr_dap_an"])}.'
              if 'fhr' in n and 'fhr_dap_an' in n else 'Nhịp tim máy báo trông bình thường nhưng sai.')
        return dict(ten='Máy bám nhầm tim mẹ', bo='CinC 2013', du_lieu=cinc,
                    cho_thay=f'{bm} nhịp máy báo trùng nhịp mẹ. {hr}',
                    so=f'F1 {f1} · {den}', so_giai='kết quả sai, và máy tự báo đỏ', mau='#dc2626')
    rng = (f'F1 từng dây chỉ {_vn(n["f1_min_day"])}–{_vn(n["f1_max_day"])}. '
           if 'f1_min_day' in n else '')
    tu_choi = (f'Hệ thống từ chối {n["n_red"]}/{n["n_seg"]} đoạn thay vì đoán.' if 'n_seg' in n
               else 'Hệ thống từ chối trả lời thay vì đoán.')
    return dict(ten='Bốn dây đều kém', bo='CinC 2013', du_lieu=cinc, cho_thay=rng + tu_choi,
                so=f'F1 {f1} · {den}', so_giai='thấp, và máy báo đỏ thay vì đoán bừa', mau='#b45309')


def story_card_html(name, active=False):
    s = story_card_spec(name)
    tren_dia = name in RECS
    go = '▶ Bấm để chạy (khoảng 5–10 giây)' if tren_dia else '⚠ chưa có trên đĩa — xem hướng dẫn tải dữ liệu'
    return (f'<div class="rf-sc{" rf-sc-on" if active else ""}{"" if tren_dia else " rf-sc-off"}" style="--sc:{s["mau"]}">'
            f'<div class="rf-sc-name">{s["ten"]}</div><div class="rf-sc-code">bản ghi {name} · {s["bo"]}</div>'
            f'<div class="rf-sc-ds">{s["du_lieu"]}</div>'
            f'<div class="rf-sc-show">{s["cho_thay"]}</div>'
            f'<div class="rf-sc-num">{s["so"]}</div><div class="rf-sc-numk">{s["so_giai"]}</div>'
            f'<div class="rf-sc-go">{go}</div></div>')


STORY_UPLOAD_CARD = ('<div class="rf-sc" style="--sc:#6b7280"><div class="rf-sc-name">Tệp của bạn</div>'
                     '<div class="rf-sc-code">dữ liệu mới · .edf · .dat + .hea · .csv · .npy · .txt</div>'
                     '<div class="rf-sc-ds">bản ghi điện tim bụng mẹ mà nhóm chưa từng dùng</div>'
                     '<div class="rf-sc-show">Chạy đúng quy trình như bốn thẻ bên cạnh</div>'
                     '<div class="rf-sc-num">Thử dữ liệu mới</div>'
                     '<div class="rf-sc-numk">không cần đáp án; có đáp án thì chấm thêm được F1</div>'
                     '<div class="rf-sc-go">▶ Mở phần tải tệp</div></div>')


def story_progress_html(step):
    parts = []
    for i, t in enumerate(STORY_STEPS, 1):
        cls = 'rf-pg-on' if i == step else ('rf-pg-done' if i < step else '')
        parts.append(f'<div class="rf-pg {cls}"><span class="rf-pg-n">{i}</span><span class="rf-pg-t">{t}</span></div>')
    return '<div class="rf-pgbar">' + ''.join(parts) + '</div>'


def _tiers_figure(full, out, rows, titles):
    """Cắt vài tầng từ hình 5 tầng đã vẽ (signal_figure) thành một hình nhỏ — dùng lại trace, đổi tiêu đề."""
    fs = out['fs']
    fig = make_subplots(rows=len(rows), cols=1, shared_xaxes=True, vertical_spacing=0.14, subplot_titles=titles)
    for i, r in enumerate(rows, 1):
        ya = 'y' if r == 1 else f'y{r}'
        for tr in full.data:
            if (tr.yaxis or 'y') == ya:
                fig.add_trace(tr, row=i, col=1)
        if r == 4:
            lo, hi = -0.02, 1.05
            vx, vy = _vlines(np.asarray(out['fetal_peaks_250']) / fs, lo, hi)
            # tím đậm: nhịp mạng đã BÁO, chưa biết đúng/sai. Xanh lá chỉ dành cho "đúng", đỏ cho "báo dư" ở tầng dưới
            fig.add_trace(go.Scattergl(x=vx, y=vy, mode='lines', name='nhịp mạng đã báo',
                                       line=dict(color=COL_BAO, width=1), opacity=0.5, hoverinfo='skip'), row=i, col=1)
            fig.add_hline(y=out['threshold'], line=dict(color=COL['thr'], width=1.5, dash='dash'), row=i, col=1)
            fig.update_yaxes(title_text='mức tin', range=[lo, hi], row=i, col=1)
        else:
            # đơn vị biên độ khác nhau giữa các máy ghi (V, µV, đơn vị ADC) -> không in số trên trục để khỏi so sai
            fig.update_yaxes(title_text='biên độ', showticklabels=False, row=i, col=1)
    # tên đường bằng lời thường (hình 5 tầng gốc ở chế độ chuyên gia giữ nguyên)
    ten = {'Thô': 'tín hiệu thô', 'Đã lọc': 'đã lọc nhiễu', 'Nhịp mẹ': 'nhịp mẹ', 'Phần dư': 'còn lại sau khi trừ tim mẹ',
           'Nhãn nhịp thai': 'nhịp thai theo đáp án', 'Xác suất': 'mức tin của mạng', 'Đỉnh chọn': 'đỉnh vượt ngưỡng'}
    for tr in fig.data:
        nm = tr.name or ''
        if nm in ten:
            tr.name = ten[nm]
        elif nm.startswith('TP (đúng)'):
            tr.name = nm.replace('TP (đúng)', 'đúng')
        elif nm.startswith('FP (dư)'):
            tr.name = nm.replace('FP (dư)', 'báo dư')
        elif nm.startswith('FN (sót)'):
            tr.name = nm.replace('FN (sót)', 'bỏ sót')
        elif nm.startswith('Mô hình:'):
            tr.name = nm.replace('Mô hình:', 'máy tìm:')
        if nm == 'Đỉnh chọn':                                       # chấm đỉnh cùng màu tím, không lẫn với "đúng"
            tr.marker.color = COL_BAO
    dur = len(out['raw']) / out['fs_raw']
    fig.update_xaxes(range=[0, min(VIEW_S, dur)], showgrid=True, gridcolor='rgba(0,0,0,0.06)')
    fig.update_xaxes(title_text='thời gian (giây) — kéo để phóng to, nhấp đúp để xem toàn bộ', row=len(rows), col=1)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.06)', zeroline=False)
    fig.update_layout(height=270 * len(rows) + 80, margin=dict(l=60, r=20, t=44, b=50), hovermode='closest',
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=12)),
                      plot_bgcolor='white', paper_bgcolor='white', font=dict(size=13), dragmode='zoom', separators=', ')
    for a in fig.layout.annotations:
        a.font.size = 15; a.x = 0.0; a.xanchor = 'left'
    return fig


def story_rules(out):
    """Hai quy tắc chọn dây trên cùng bản ghi: quy tắc mới (peakprob) và quy tắc cũ (PSD) chọn dây nào, F1 bao nhiêu.
    Không chạy lại mô hình: F1 từng dây đã có trong out['leads'] (mô hình chạy trên mọi dây khi chọn tự động)."""
    L = out.get('leads')
    if not L:
        return None
    k_pp = max(L, key=lambda k: (L[k].get('peakprob') if L[k].get('peakprob') is not None else -1.0))
    k_psd = max(L, key=lambda k: L[k]['psd'])
    f = lambda k: (_vn(L[k]['F1']) if 'F1' in L[k] else None)         # noqa: E731
    lech = abs(float(L[k_pp]['F1']) - float(L[k_psd]['F1'])) if ('F1' in L[k_pp] and 'F1' in L[k_psd]) else None
    # dây tốt nhất THEO ĐÁP ÁN (chỉ để báo trung thực sau khi đã chọn; không tham gia chọn)
    k_best = max(L, key=lambda k: L[k]['F1']) if all('F1' in L[k] for k in L) else None
    kem = (float(L[k_best]['F1']) - float(L[out['lead']]['F1'])) if (k_best is not None and out.get('lead') in L) else None
    return dict(k_pp=k_pp, k_psd=k_psd, f1_pp=f(k_pp), f1_psd=f(k_psd), khac=(k_pp != k_psd), lech=lech,
                k_best=k_best, f1_best=(f(k_best) if k_best is not None else None), kem_best=kem)


STORY_KEM_NGUONG = 10.0     # dây được chọn kém dây tốt nhất >= 10 điểm F1 -> hiện hộp "chọn chưa đúng"


def story_wrong_lead_html(out):
    """Hộp vàng trung thực khi dây được chọn kém xa dây tốt nhất theo đáp án (ví dụ a02). '' nếu không cần."""
    r = story_rules(out)
    if r is None or r['kem_best'] is None or r['kem_best'] < STORY_KEM_NGUONG:
        return ''
    k, kb = out['lead'], r['k_best']
    votes = STORY_VOTES.get(out.get('record'), {})
    cung = votes.get(int(k), [])
    tong = sum(len(v) for v in votes.values())
    if tong and len(cung) == tong:
        ai = f'Cả {tong} cách chọn dây không nhìn đáp án mà nhóm đã so đều chọn dây {k}.'
    elif tong:
        ai = f'{len(cung)}/{tong} cách chọn dây không nhìn đáp án mà nhóm đã so cũng chọn dây {k}.'
    else:
        ai = 'Chưa có bảng so sánh các cách chọn khác cho bản ghi này.'
    if tong and not votes.get(int(kb)):
        ai += f' Không cách nào chọn dây {kb}.'
    txt = (f'Dây {kb} đạt F1 {r["f1_best"]}, nhưng hệ thống chọn dây {k} (F1 {_vn(out['leads'][k].get('F1'))}). {ai} '
           'Chọn dây mà không nhìn đáp án thì không phải lúc nào cũng đúng; thiết bị thật chỉ có một dây thì không có dây khác để chọn.')
    return f'<div class="rf-box rf-box-warn"><div class="rf-box-k">Lưu ý trung thực — chọn chưa đúng dây</div><div class="rf-box-t">{txt}</div></div>'



def story_rules_md(out):
    """Bước 4: hai quy tắc chọn dây nào (HTML) + hộp vàng nếu dây được chọn kém xa dây tốt nhất."""
    r = story_rules(out)
    if r is None:
        return '<div class="rf-rules">Dây được chọn tay — không có so sánh bốn dây.</div>'
    f1 = lambda v: (f'F1 <b>{v}</b>' if v is not None else 'không có đáp án để chấm')   # noqa: E731
    s = (f'<b>Cách chọn mới</b> (peakprob: dây mà mạng tự tin nhất) chọn dây <b>{r["k_pp"]}</b> → {f1(r["f1_pp"])}. '
         f'<b>Cách chọn cũ</b> (PSD: dây có năng lượng mạnh nhất ở dải nhịp tim thai 1,8–3 Hz, như Power-MF) '
         f'chọn dây <b>{r["k_psd"]}</b> → {f1(r["f1_psd"])}. ')
    if not r['khac']:
        s += 'Hai cách chọn cùng một dây.'
    elif r['lech'] is None:
        s += 'Hai cách chọn <b>khác dây</b>; bản ghi không có đáp án nên chưa biết cách nào đúng.'
    elif r['lech'] >= 10:
        s += 'Hai cách chọn <b>khác dây</b>, và kết quả khác hẳn.'
    else:
        s += 'Hai cách chọn <b>khác dây</b>, nhưng kết quả gần như nhau.'
    return f'<div class="rf-rules">{s}</div>' + story_wrong_lead_html(out)


def _vn_int(x):
    """Số nguyên kiểu Việt: 1.005 (dấu chấm ngăn nghìn)."""
    try:
        return f'{int(round(float(x))):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return '—'


def _sci_vi(x):
    """Số rất lớn/nhỏ (điểm PSD): 7,14·10^0 thay cho 7.14e+00."""
    try:
        m, e = f'{float(x):.2e}'.split('e')
        return f'{m.replace(".", ",")}·10^{int(e)}'
    except (TypeError, ValueError):
        return '—'


def _ly_do_vi(r):
    """Một dòng lý do của đèn, số kiểu Việt: 0.05 -> 0,05; 30% -> 30 %."""
    r = re.sub(r'(?<=[0-9])[.](?=[0-9])', ',', str(r))
    return re.sub(r'(?<=[0-9])%', ' %', r)


def story_cards_html(out):
    """Bước 5, phần 'Chi tiết kỹ thuật': lý do của đèn, điểm từng dây, thời gian xử lý. Số kiểu Việt, không đường dẫn tệp."""
    c = out['confidence']
    reasons = ''.join(f'<li>{_ly_do_vi(r)}</li>' for r in c.get('reasons', []))
    L = out.get('leads') or {}
    pp = [L[k]['peakprob'] for k in L if L[k].get('peakprob') is not None]
    nd_pp = 4 if len({round(v, 3) for v in pp}) < len(pp) else 3
    rows = ''.join(
        f'<tr{" class=rf-tsel" if L[k]["selected"] else ""}><td>Dây {k}{" (được chọn)" if L[k]["selected"] else ""}</td>'
        f'<td>{_vn(L[k].get("peakprob"), nd_pp)}</td><td>{_vn(L[k].get("F1"))}</td><td>{_fmt(L[k].get("fhr_mean"))}</td></tr>'
        for k in sorted(L))
    bang_day = ('<table class="rf-tt"><tr><th>Dây</th><th>Điểm tin của mạng (quy tắc mới)</th><th>F1 theo đáp án</th>'
                f'<th>Nhịp tim (nhịp/phút)</th></tr>{rows}</table>') if L else ''
    lat_all = out.get('latency_all_leads_ms')
    thoi_gian = (f'Xử lý dây đã chọn: {_vn_int(out["latency_ms"])} ms'
                 + (f' · chạy mô hình trên cả {out.get("n_leads", "?")} dây để chọn: {_vn_int(lat_all)} ms' if lat_all else '')
                 + f' · bản ghi dài {out["duration_s"]:.0f} giây · CPU máy tính, {core.torch.get_num_threads()} luồng')
    return (f'<div class="rf-tech"><div class="rf-tech-h">Vì sao đèn {c["label"]} (điểm {_vn(c.get("score"))} / 1)</div>'
            f'<ul class="rf-r">{reasons}</ul>{bang_day}<div class="rf-tech-s">{thoi_gian}</div></div>')


def story_compare_md(out):
    """Bước 5, 'Chi tiết kỹ thuật': bảng chấm với đáp án, số kiểu Việt."""
    if 'metrics' not in out:
        return 'Bản ghi này không có đáp án nên không chấm được F1.'
    m = out['metrics']
    warn = ''
    rn = out.get('record', '')
    if rn in core.CINC_LEAK:
        warn = f'\n\n> ⚠ {rn} là bản sao nguyên văn của {core.CINC_LEAK[rn]} trong dữ liệu huấn luyện: không phải kết quả ngoài miền.'
    elif rn in core.CINC_BAD_ANN:
        warn = f'\n\n> ⚠ {rn} thuộc 7 bản CinC có đáp án sai đã biết: F1 thấp ở đây phần lớn là lỗi đáp án.'
    return (f'**Cách chấm:** một nhịp máy báo được tính đúng nếu cách nhịp thật không quá ±{core.CFG["tolerance_ms"]} ms.\n\n'
            '| Độ nhạy (tìm được bao nhiêu nhịp thật) | Độ chính xác (bao nhiêu nhịp báo là thật) | F1 | Lệch thời điểm TB |\n'
            '|---:|---:|---:|---:|\n'
            f'| {_vn(m["Se"])} % | {_vn(m["PPV"])} % | **{_vn(m["F1"])}** | {_vn(m.get("jitter_ms"))} ms |\n\n'
            '| Đúng | Báo dư | Bỏ sót | Số nhịp theo đáp án |\n|---:|---:|---:|---:|\n'
            f'| {m["TP"]} | {m["FP"]} | {m["FN"]} | {len(out["labels_1000"])} |{warn}\n')


def story_summary_html(out=None):
    """Thanh tóm tắt cố định: bản ghi | bộ dữ liệu | dây đã chọn (quy tắc) | F1 | nhịp tim thai TB | đèn tin cậy."""
    if out is None:
        items = [('Bản ghi', '—'), ('Bộ dữ liệu', '—'), ('Dây đã chọn', '—'),
                 ('F1 (bắt đủ và báo đúng, 100 là hoàn hảo)', '—'), ('Nhịp tim thai trung bình', '—'), ('Đèn tin cậy', '—')]
        col = '#6b7280'
    else:
        ds = RECS.get(out['record'], {}).get('dataset') or out.get('source', '—')
        rule = {'peakprob': 'quy tắc mới', 'psd': 'quy tắc cũ, PSD'}.get(out.get('lead_rule'), 'chọn tay')
        f1 = _vn(out['metrics']['F1']) if 'metrics' in out else 'không có đáp án'
        c = out['confidence']; col = c['color']
        hr = f'{_fmt(out["fhr_mean"])} nhịp/phút'
        if c.get('level') == 'thap':                    # đèn đỏ: không để con số trông bình thường đứng một mình
            hr = f'<s>{hr}</s><div class="rf-sum-bad">đèn đỏ: không dùng số này</div>'
        items = [('Bản ghi', out['record']), ('Bộ dữ liệu', ds),
                 ('Dây đã chọn', f'{out["lead"]} / {out.get("n_leads", "?")} ({rule})'),
                 ('F1 (bắt đủ và báo đúng, 100 là hoàn hảo)', f1),
                 ('Nhịp tim thai trung bình', hr),
                 ('Đèn tin cậy', f'<span style="color:{col}">● {c["label"]}</span>')]
    cells = ''.join(f'<div class="rf-sum-i"><div class="rf-sum-k">{k}</div><div class="rf-sum-v">{v}</div></div>' for k, v in items)
    s60 = STORY_60
    line = (f'Trên {s60["n"]} bản ghi ngoài miền, F1 trung bình theo cách chọn dây: cách cũ (PSD) {_vn(s60["psd"])} · '
            f'cách kế hoạch đã chọn trước khi chạy (gate) {_vn(s60["gate"])} · gate4, cũng ghi trước khi chạy, {_vn(s60["gate4"])} · '
            f'cách demo đang dùng, chọn sau khi xem kết quả (peakprob) {_vn(s60["peakprob"])} · '
            f'trần nếu biết trước dây tốt nhất {_vn(s60["oracle"])}'
            if s60 else 'Chưa đọc được bảng 60 bản ngoài miền trên máy này.')
    return f'<div class="rf-sum" style="border-color:{col}"><div class="rf-sum-row">{cells}</div><div class="rf-sum-60">{line}</div></div>'


def _box(kind, text):
    k = 'Con số cần nhớ' if kind == 'num' else 'Cách đọc hình'
    return f'<div class="rf-box rf-box-{kind}"><div class="rf-box-k">{k}</div><div class="rf-box-t">{text}</div></div>'


def story_ti_le_bien_do(out, giay=10.0, nua_cua_so=5):
    """Trung vị biên độ gai bé / gai mẹ trên tín hiệu đã lọc (250 Hz) trong `giay` giây đầu.
    Cần đáp án (vị trí nhịp bé thật); không có đáp án -> None. r01 dây 4 ≈ 1 (gai bé to ngang mẹ); a09, a02 ≈ 0,1."""
    lab = out.get('labels_1000')
    x = np.asarray(out.get('filtered_250'), float)
    mpk = np.asarray(out.get('maternal_peaks'), int)
    if lab is None or x.size == 0 or mpk.size == 0:
        return None
    fs = out['fs']; n = min(len(x), int(giay * fs))
    fpk = (np.asarray(lab, float) / (out['fs_raw'] / fs)).astype(int)

    def bien_do(idx):
        idx = idx[(idx >= nua_cua_so) & (idx < n - nua_cua_so)]
        return float(np.median([np.max(np.abs(x[i - nua_cua_so:i + nua_cua_so + 1])) for i in idx])) if idx.size else float('nan')
    a_be, a_me = bien_do(fpk), bien_do(mpk)
    if not (np.isfinite(a_be) and np.isfinite(a_me)) or a_me <= 0:
        return None
    return a_be / a_me


def story_texts(out):
    """Mỗi bước: (con số cần nhớ — 1 dòng, cách đọc hình — 2 câu). Số lấy từ out, không ghi cứng."""
    fs, dur = out['fs'], float(out['duration_s'])
    n_m = len(out['maternal_peaks']); mhr = n_m / dur * 60 if dur > 0 else float('nan')
    fhr = _fmt(out['fhr_mean']); nb = int(out['n_beats']); has_lab = 'metrics' in out
    c = out['confidence']; segs = c.get('segments')
    ml = (c.get('components') or {}).get('maternal_lock')
    # cùng luật với cổng (fsqi/gate.py: trùng nhịp mẹ >= ngưỡng trong pkl -> 'locked'), không tự đặt ngưỡng riêng
    bam_me = bool((c.get('components') or {}).get('locked')) and ml is not None and np.isfinite(ml)
    do = c.get('level') == 'thap'
    hr_ref = len(out['labels_1000']) / dur * 60 if (has_lab and dur > 0) else None
    T = {}
    # Bước 1-3 KHÔNG được đưa nhịp tim máy đếm ra như sự thật khi chính bước 5 sẽ bảo "không dùng số này" (ví dụ a02)
    if do and hr_ref is not None:
        t1 = (f'Tim mẹ ≈ {_fmt(mhr)} nhịp/phút. Theo đáp án, tim bé ≈ {_fmt(hr_ref)} nhịp/phút; '
              f'máy đếm được ≈ {fhr}, không tin được (xem bước 5).')
    elif do:
        t1 = f'Tim mẹ ≈ {_fmt(mhr)} nhịp/phút. Máy đếm tim bé ≈ {fhr} nhịp/phút, nhưng đèn đỏ: chưa tin được số này (xem bước 5).'
    else:
        t1 = f'Tim mẹ ≈ {_fmt(mhr)} nhịp/phút, tim bé ≈ {fhr} nhịp/phút.'
        if np.isfinite(out['fhr_mean']) and np.isfinite(mhr) and out['fhr_mean'] > mhr + 5:
            t1 += ' Tim bé đập nhanh hơn tim mẹ.'
    # gai bé to hay nhỏ so với gai mẹ: đo trên CHÍNH bản ghi (cần đáp án để biết nhịp bé ở đâu), không nói chung chung
    ti_le = story_ti_le_bien_do(out)
    if ti_le is not None and ti_le >= 0.5:
        doc1 = (f'Ở dây này gai của bé to ngang gai của mẹ: gai dày, đều, nhanh hơn (≈ {_fmt(hr_ref)} nhịp/phút) là tim bé; '
                f'gai thưa hơn (≈ {_fmt(mhr)} nhịp/phút) là tim mẹ.')
    elif ti_le is not None:
        doc1 = 'Ở dây này gai lớn đều đặn là tim mẹ; gai của bé nhỏ hơn nhiều, lẫn trong nhiễu.'
    else:
        doc1 = 'Thường thì gai lớn đều đặn là tim mẹ, nhưng có dây gai của bé to ngang gai mẹ; bản ghi này không có đáp án để phân biệt.'
    T[1] = (t1, 'Trục ngang là thời gian (đang xem 10 giây đầu, kéo để phóng to). ' + doc1)
    T[2] = (f'Tìm được {n_m} nhịp mẹ trong {dur:.0f} giây (≈ {_fmt(mhr)} nhịp/phút) và trừ chúng đi.',
            'Hàng trên: tín hiệu đã lọc nhiễu, vạch đỏ đánh dấu từng nhịp mẹ hệ thống tìm được. '
            'Hàng dưới: phần còn lại sau khi trừ tim mẹ' + ('; vạch đen chấm là nhịp thai theo đáp án.' if has_lab else '.'))
    if bam_me:
        t3 = (f'Mạng báo {nb} nhịp "thai", nhưng {ml * 100:.0f} % trùng thời điểm nhịp mẹ: mạng đang bám nhầm tim mẹ. '
              f'Chỉ đỉnh vượt ngưỡng {_vn(out["threshold"])} mới được tính.')
    elif do:
        t3 = f'Mạng báo {nb} nhịp, nhưng đèn đỏ: chưa tin được (xem bước 5). Chỉ đỉnh vượt ngưỡng {_vn(out["threshold"])} mới được tính.'
    else:
        t3 = f'Mạng phát hiện {nb} nhịp thai (≈ {fhr} nhịp/phút); chỉ đỉnh vượt ngưỡng {_vn(out["threshold"])} mới được tính.'
    T[3] = (t3,
            'Hàng trên: đường tím lên gần 1 nghĩa là mạng rất tin có một nhịp thai ở đó; vạch cam là ngưỡng, vạch tím đậm là nhịp mạng đã báo. '
            + ('Hàng dưới: so với đáp án — chấm xanh lá là đúng, dấu ✕ đỏ là báo dư, tam giác cam là bỏ sót.' if has_lab
               else 'Hàng dưới: vị trí các nhịp đã phát hiện (bản ghi này không có đáp án để chấm).'))
    r = story_rules(out)
    if r is None:
        t4 = 'Dây được chọn tay, không có so sánh bốn dây.'
    elif r['khac']:
        t4 = (f'Quy tắc mới chọn dây {r["k_pp"]}, quy tắc cũ chọn dây {r["k_psd"]}'
              + (f': F1 {r["f1_pp"]} so với {r["f1_psd"]}.' if r['f1_pp'] is not None else '.'))
    else:
        t4 = f'Cả hai cách cùng chọn dây {r["k_pp"]}' + (f' (F1 {r["f1_pp"]}).' if r['f1_pp'] is not None else '.')
    L = out.get('leads') or {}
    pps = [L[k]['peakprob'] for k in L if L[k].get('peakprob') is not None]
    if len(pps) > 1 and max(pps) - min(pps) < 1e-3:
        f1s = [L[k]['F1'] for k in L if 'F1' in L[k]]
        t4 += (f' {"Bốn" if len(pps) == 4 else len(pps)} dây gần như ngang điểm (chênh dưới 0,001)'
               + (f'; dây nào cũng cho F1 từ {_vn(min(f1s))} trở lên.' if f1s else '.'))
    T[4] = (t4,
            'Mỗi hàng là một dây điện cực; hàng tô nền xanh dương nhạt là dây hệ thống chọn. "Điểm tin của mạng" là mức mạng tin '
            'vào các nhịp nó tìm thấy trên dây đó; cách chọn mới lấy dây có điểm cao nhất. F1 chỉ chấm sau khi đã chọn xong, không tham gia chọn.')
    f1 = f'F1 {_vn(out["metrics"]["F1"])}' if has_lab else 'không có đáp án để chấm'
    seg_txt = ''
    if segs:
        lv = segs['level']; n = len(lv); ng = sum(1 for l in lv if l == 'xanh'); nd = sum(1 for l in lv if l == 'do')
        seg_txt = f' · {ng} đoạn xanh, {n - ng - nd} vàng, {nd} đỏ trên {n} đoạn 4 giây'
    ml_txt = f' · {ml * 100:.0f} % nhịp "thai" trùng nhịp mẹ' if bam_me else ''
    hr_txt = ''
    if hr_ref is not None and np.isfinite(out['fhr_mean']) and abs(float(out['fhr_mean']) - hr_ref) >= 10:
        hr_txt = f' · máy báo {fhr} nhịp/phút nhưng theo đáp án ≈ {_fmt(hr_ref)}'
    T[5] = (f'{f1} · đèn {c["label"]}{seg_txt}{ml_txt}{hr_txt}.',
            'Hình trên: đường xanh dương là hệ thống' + (', đường chấm đen là đáp án' if has_lab else '')
            + ', dải xanh lá nhạt là mức bình thường 110–160. '
            'Hình dưới: mỗi cột là một đoạn 4 giây, cột càng cao càng đáng ngờ; nền đỏ là đoạn hệ thống từ chối trả lời.')
    return T


def story_compute(name):
    """Bấm thẻ -> phân tích ngay (peakprob, cổng học). Trả về dict thuần để kiểm thử; story_run() xếp thành đầu ra Gradio."""
    if name not in RECS:
        raise ValueError(f'Bản ghi {name} chưa có trên đĩa — xem HANDOFF.md mục 4 để tải dữ liệu.')
    t0 = time.perf_counter()
    rec = core.load_sample(name, RECS)
    out = core.analyze_record(rec, lead='peakprob', confidence_mode='hoc')
    full = signal_figure(out)
    lead = out.get('lead', '?'); n_m = len(out['maternal_peaks']); lab = out.get('labels_1000')
    figs = {
        1: _tiers_figure(full, out, (1,), [f'Tín hiệu thô trên bụng mẹ, dây {lead}']),
        2: _tiers_figure(full, out, (2, 3), [f'Đã lọc nhiễu — vạch đỏ: {n_m} nhịp tim mẹ',
                                            'Sau khi trừ tim mẹ — phần còn lại' + (' (vạch đen chấm: nhịp thai theo đáp án)' if lab is not None else '')]),
        3: _tiers_figure(full, out, (4, 5), ['Mức tin của mạng — vạch tím đậm: nhịp mạng đã báo, vạch cam: ngưỡng',
                                            'So với đáp án: ● đúng, ✕ dư, ▲ sót' if lab is not None else f'{out["n_beats"]} nhịp thai đã phát hiện']),
        4: leads_figure(out, vi_fmt=True),
        5: fhr_figure(out, vi_fmt=True),
    }
    return dict(out=out, figs=figs, texts=story_texts(out), rules_md=story_rules_md(out),
                cards=story_cards_html(out), compare=story_compare_md(out), summary=story_summary_html(out),
                wall_ms=(time.perf_counter() - t0) * 1000)


STORY_N_OUTS = 33          # 4 thẻ + 18 ô nội dung + thanh tóm tắt + 9 ô trạng thái bước + dòng trạng thái
_YEU_CAU = {}              # phiên trình duyệt -> thẻ bấm SAU CÙNG (bấm chồng: lượt cũ không được vẽ đè)


def _phien(request):
    return getattr(request, 'session_hash', None) if request is not None else None


def story_request(name, sid):
    """Ghi thẻ bấm sau cùng của phiên (chạy ngay, không xếp hàng) -> dòng trạng thái 'đang phân tích'."""
    if sid is not None:
        _YEU_CAU[sid] = name
    return story_loading_html(name)


def story_run(name, sid=None):
    """Sự kiện bấm thẻ. Thứ tự đầu ra khớp story_outs trong build_app(); phần tử cuối là dòng trạng thái.
    Không ném lỗi: lỗi hiện ở dòng trạng thái (ném gr.Error thì chuỗi .then() dừng và dòng 'đang phân tích' kẹt lại).
    Nếu người dùng đã bấm thẻ khác sau thẻ này: không vẽ gì, giữ nguyên dòng trạng thái của lượt mới."""
    giu = gr.update()
    if sid is not None and _YEU_CAU.get(sid, name) != name:
        return tuple([giu] * STORY_N_OUTS)
    try:
        r = story_compute(name)
    except Exception as e:                                       # noqa: BLE001
        ly_do = str(e) if isinstance(e, ValueError) else f'{type(e).__name__}: {e}'
        loi = (f'<div class="rf-loading rf-loading-loi">Không phân tích được bản ghi {name}: {ly_do} '
               'Hình bên dưới vẫn là bản ghi trước — bấm lại thẻ hoặc chọn thẻ khác.</div>')
        return tuple([giu] * (STORY_N_OUTS - 1)) + (loi,)
    if sid is not None and _YEU_CAU.get(sid, name) != name:     # đã có thẻ bấm sau trong lúc đang tính
        return tuple([giu] * STORY_N_OUTS)
    T, F = r['texts'], r['figs']
    cards = [story_card_html(n, active=(n == name)) for n in STORY_RECS]
    return (*cards,
            F[1], _box('num', T[1][0]), _box('read', T[1][1]),
            F[2], _box('num', T[2][0]), _box('read', T[2][1]),
            F[3], _box('num', T[3][0]), _box('read', T[3][1]),
            F[4], r['rules_md'], _box('num', T[4][0]), _box('read', T[4][1]),
            F[5], r['cards'], r['compare'], _box('num', T[5][0]), _box('read', T[5][1]),
            r['summary'], *story_view(1), '')


def story_view(step):
    """Trạng thái bước hiện tại -> (bước, thanh tiến trình, 5 cột ẩn/hiện, nút Quay lại, nút Tiếp)."""
    step = int(min(max(int(step), 1), STORY_N_STEPS))
    vis = [gr.update(visible=(i == step)) for i in range(1, STORY_N_STEPS + 1)]
    return (step, story_progress_html(step), *vis, gr.update(interactive=step > 1),
            gr.update(value=('Tiếp ▶' if step < STORY_N_STEPS else 'Xem lại từ đầu ↺')))


def story_step(cur, delta):
    nxt = int(cur or 1) + int(delta)
    if nxt > STORY_N_STEPS:
        nxt = 1
    return story_view(nxt)


def story_loading_html(name, lan_dau=False):
    """Dòng trạng thái lúc đang phân tích (thay chữ 'processing' của Gradio)."""
    s = story_card_spec(name) if name in STORY_RECS else {'ten': name}
    dau = 'Đang mở sẵn' if lan_dau else 'Đang phân tích'
    return (f'<div class="rf-loading">⏳ {dau} bản ghi {name} ({s["ten"]}) — khoảng 5–10 giây. '
            'Xong thì hình bên dưới tự đổi; chờ xong rồi hãy bấm "Tiếp ▶".</div>')


# cuộn tới thanh 5 bước sau khi đổi bước / đổi thẻ (Gradio chạy js ở trình duyệt, không cần máy chủ).
# KHÔNG cuộn khi: thanh 5 bước đã nằm nửa trên màn hình (nút Tiếp khỏi chạy khỏi con trỏ), hoặc người xem đã bật
# chế độ chuyên gia và cuộn đi chỗ khác trong lúc chờ (không kéo họ về).
JS_GHI_VI_TRI = "() => { window.__rfY = window.scrollY; }"
JS_CUON_TOI_BUOC = ("() => { setTimeout(() => { const e = document.querySelector('.rf-pgbar'); if (!e) return; "
                    "const cg = document.querySelector('.rf-expert-head input[type=checkbox]'); "
                    "if (cg && cg.checked && Math.abs(window.scrollY - (window.__rfY || 0)) > 150) return; "
                    "const t = e.getBoundingClientRect().top; if (t >= 0 && t < window.innerHeight * 0.5) return; "
                    "e.scrollIntoView({behavior: 'smooth', block: 'start'}); }, 150); }")
JS_CUON_TOI_TAI_TEP = ("() => { setTimeout(() => { const h = [...document.querySelectorAll('h3')]"
                       ".find(x => x.offsetHeight && x.innerText.includes('Thử mô hình trên dữ liệu')); "
                       "const e = h || document.querySelector('.rf-expert-head'); "
                       "if (e) e.scrollIntoView({behavior: 'smooth', block: 'start'}); }, 400); }")


def toggle_expert(flag):
    """Bật/tắt 'Chế độ chuyên gia' -> ẩn/hiện cột bọc 8 tab cũ."""
    return gr.update(visible=bool(flag))


STORY_CSS = '''
.rf-sec{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:#6b7280;font-weight:700;margin:10px 0 2px}
.rf-sc{border:2px solid #e5e7eb;border-left:8px solid var(--sc);border-radius:14px;padding:12px 14px;background:#fff;
  cursor:pointer;min-height:168px;display:flex;flex-direction:column;gap:3px;transition:box-shadow .15s,transform .15s}
.rf-sc:hover{box-shadow:0 6px 18px rgba(0,0,0,.12);transform:translateY(-2px)}
.rf-sc-on{border-color:var(--sc);background:#f8fafc;box-shadow:0 0 0 3px color-mix(in srgb,var(--sc) 30%,transparent)}
.rf-sc-off{opacity:.55;cursor:not-allowed}
.rf-sc-name{font-size:24px;font-weight:800;color:#111827;line-height:1.1}
.rf-sc-ds{font-size:12.5px;color:#4b5563;line-height:1.4}
.rf-sc-show{font-size:14.5px;font-weight:600;color:#1f2937;line-height:1.35;margin-top:2px}
.rf-sc-num{font-size:26px;font-weight:800;color:var(--sc);margin-top:auto;line-height:1.15}
.rf-sc-numk{font-size:11.5px;color:#6b7280}
.rf-sc-go{font-size:12px;color:var(--sc);font-weight:700;margin-top:4px}
.rf-sc-small{min-height:120px}
.rf-sc-wrap{margin:0 !important;align-self:stretch !important;display:flex !important;flex-direction:column}
.rf-sc-wrap>*:not(.wrap){flex:1 1 auto;display:flex;flex-direction:column}
.rf-sc-wrap>*:not(.wrap)>*{flex:1 1 auto;display:flex;flex-direction:column}
.rf-sc{flex:1 1 auto;box-sizing:border-box}
.rf-pgbar{display:flex;gap:6px;margin:8px 0 4px;flex-wrap:wrap}
.rf-pg{flex:1 1 140px;display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:10px;border:1.5px solid #e5e7eb;background:#fff;color:#6b7280}
.rf-pg-n{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:#e5e7eb;font-weight:800;color:#374151;flex:0 0 28px}
.rf-pg-t{font-size:13px;font-weight:600}
.rf-pg-on{border-color:#059669;background:#ecfdf5;color:#065f46}
.rf-pg-on .rf-pg-n{background:#059669;color:#fff}
.rf-pg-done{color:#065f46}
.rf-pg-done .rf-pg-n{background:#a7f3d0;color:#065f46}
.rf-cap{font-size:17px;font-weight:600;color:#111827;background:#f3f4f6;border-left:5px solid #059669;border-radius:8px;padding:10px 14px;margin:4px 0 6px;line-height:1.45}
.rf-box{border-radius:10px;padding:10px 12px;margin:6px 0;line-height:1.5}
.rf-box-num{background:#eff6ff;border:1.5px solid #bfdbfe}
.rf-box-read{background:#fffbeb;border:1.5px solid #fde68a}
.rf-box-k{font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;font-weight:700;color:#6b7280;margin-bottom:2px}
.rf-box-t{font-size:14.5px;color:#1f2937}
.rf-box-num .rf-box-t{font-size:16px;font-weight:700;color:#1e3a8a}
.rf-sum{position:sticky;bottom:0;z-index:20;background:#fff;border:2px solid #e5e7eb;border-radius:12px;padding:8px 12px;margin:10px 0 4px;box-shadow:0 -4px 14px rgba(0,0,0,.08)}
.rf-sum-row{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px}
@media (max-width:900px){.rf-sum-row{grid-template-columns:repeat(3,minmax(0,1fr))}}
.rf-sum-k{font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:#6b7280;font-weight:600}
.rf-sum-v{font-size:17px;font-weight:700;color:#111827;line-height:1.25}
.rf-sum-60{font-size:12.5px;color:#374151;margin-top:6px;border-top:1px dashed #e5e7eb;padding-top:5px}
.rf-expert-head{border-top:2px dashed #d1d5db;margin-top:14px;padding-top:8px}
.rf-box-warn{background:#fefce8;border:1.5px solid #eab308}
.rf-box-warn .rf-box-k{color:#854d0e}
.rf-box-warn .rf-box-t{font-size:15px;color:#422006}
.rf-rules{font-size:15px;line-height:1.5;margin:4px 0 2px;color:#1f2937}
.rf-sum-bad{font-size:11.5px;color:#b91c1c;font-weight:700;line-height:1.2}
.rf-fine{font-size:12.5px;color:#6b7280;margin:2px 2px 6px}
.rf-tech{font-size:14px;color:#1f2937;line-height:1.5}
.rf-tech-h{font-weight:700;margin-bottom:2px}
.rf-tech-s{font-size:13px;color:#4b5563;margin-top:6px}
.rf-tt{border-collapse:collapse;margin-top:6px;font-variant-numeric:tabular-nums}
.rf-tt th,.rf-tt td{border:1px solid #e5e7eb;padding:4px 10px;text-align:right}
.rf-tt th:first-child,.rf-tt td:first-child{text-align:left}
.rf-tt th{background:#f9fafb;font-size:12.5px;font-weight:600}
.rf-tt tr.rf-tsel td{background:#eff6ff;font-weight:700}
.rf-tt td,.rf-story .prose td{white-space:nowrap}
footer{display:none !important}
.rf-sc-code{font-size:12px;color:#6b7280;font-weight:600;margin-top:1px}
.rf-hint{font-size:13px;color:#4b5563;margin:0 0 2px}
.rf-loading{font-size:14px;font-weight:600;color:#1e3a8a;background:#eff6ff;border:1.5px solid #bfdbfe;border-radius:10px;padding:8px 12px;margin:4px 0}
/* thẻ xuống hàng trên màn hẹp thay vì bóp còn 54 px */
.rf-sc-row{flex-wrap:wrap !important;gap:12px !important}
.rf-sc-row>.rf-sc-wrap{flex:1 1 200px !important;min-width:200px !important}
@media (max-width:520px){.rf-sc-row>.rf-sc-wrap{flex-basis:100% !important}}
/* thanh tóm tắt dính đáy: dính theo cột bọc các bước (khung cha của chính thanh thì chỉ cao bằng nó) */
.rf-story-col .rf-sum-wrap{position:sticky !important;bottom:0;z-index:30}
.rf-story-col .rf-sum{position:static;margin:6px 0 0}
/* Gradio 6.26 đặt overflow:hidden trên .gradio-container -> sticky bám khung đó, không bám màn hình. clip giữ chống tràn ngang */
.gradio-container{overflow:visible !important;overflow-x:clip !important}
/* màn hẹp: thanh tóm tắt cao tới 40 % màn hình nếu dính -> để nó nằm yên cuối các bước */
@media (max-width:700px){.rf-story-col .rf-sum-wrap{position:static !important}}
.rf-loading-loi{color:#7f1d1d;background:#fef2f2;border-color:#fca5a5}
.rf-tech{overflow-x:auto}
@media (max-width:520px){.rf-tt th{white-space:normal;font-size:11.5px}.rf-tt td,.rf-tt th{padding:3px 6px}}
'''
CSS = CSS + STORY_CSS


def build_app():
    """Chế độ trình bày (mặc định) + 'Chế độ chuyên gia' bọc nguyên 8 tab cũ (ẩn sẵn)."""
    theme = gr.themes.Soft(primary_hue='emerald') if hasattr(gr, 'themes') else None
    bk = {}
    sig = inspect.signature(gr.Blocks.__init__).parameters
    if 'css' in sig: bk['css'] = CSS
    if 'theme' in sig and theme is not None: bk['theme'] = theme
    if 'title' in sig: bk['title'] = 'RelyFetal — demo dò nhịp tim thai đơn kênh'
    first_show = list(SHOWCASE_LABELS)[0] if SHOWCASE_LABELS else None
    with gr.Blocks(**bk) as demo:
        gr.HTML(STORY_TITLE_HTML, elem_classes=['rf-story'])
        # ------------------------------------------------------------------ [A] bốn thẻ chọn bản ghi
        gr.HTML('<div class="rf-sec">1 · Chọn một bản ghi (bấm thẻ là chạy ngay)</div>', elem_classes=['rf-story'])
        with gr.Row(equal_height=True, elem_classes=['rf-sc-row']):
            card_comps = [gr.HTML(story_card_html(n), elem_classes=['rf-story', 'rf-sc-wrap'], elem_id=f'the_{n}') for n in STORY_RECS]
            card_up = gr.HTML(STORY_UPLOAD_CARD, elem_classes=['rf-story', 'rf-sc-wrap'], elem_id='the_tai_len')
        # dòng trạng thái: thay cho chữ "processing | 1.2s" của Gradio, người xem biết máy đang làm gì
        story_status = gr.HTML('', elem_classes=['rf-story'])
        # ------------------------------------------------------------------ [B] năm bước, mỗi lúc một bước
        # bọc các bước + thanh tóm tắt trong MỘT cột: thanh tóm tắt dính đáy màn hình suốt khi xem các bước,
        # và thôi dính khi cuộn xuống chế độ chuyên gia
        with gr.Column(elem_classes=['rf-story-col']):
            gr.HTML('<div class="rf-sec">2 · Đi theo 5 bước</div>'
                    '<div class="rf-hint">Bấm "Tiếp ▶" để sang bước sau; khi cần, trang tự cuộn tới thanh 5 bước. Bấm thẻ khác ở trên để đổi bản ghi.</div>',
                    elem_classes=['rf-story'])
            step = gr.State(1)
            progress = gr.HTML(story_progress_html(1), elem_classes=['rf-story'])
            with gr.Row():
                btn_back = gr.Button('◀ Quay lại', variant='secondary', interactive=False, scale=1)
                btn_next = gr.Button('Tiếp ▶', variant='primary', scale=1)
            cols, S = [], {}
            for i in range(1, STORY_N_STEPS + 1):
                with gr.Column(visible=(i == 1), elem_classes=['rf-story']) as col:
                    gr.HTML(f'<div class="rf-cap">Bước {i} · {STORY_STEPS[i - 1]}<br><span style="font-weight:400">{STORY_CAPTION[i - 1]}</span></div>')
                    if i == 4:
                        S['rules4'] = gr.HTML()
                    S[f'fig{i}'] = gr.Plot(label=STORY_STEPS[i - 1], show_label=False)   # nhãn Gradio đè lên tiêu đề hình
                    with gr.Row():
                        S[f'num{i}'] = gr.HTML(_box('num', '—'))
                        S[f'read{i}'] = gr.HTML(_box('read', '—'))
                    if i == 5:
                        gr.HTML(f'<div class="rf-fine">{STORY_GATE_NOTE}</div>', elem_classes=['rf-story'])
                        # chi tiết kỹ thuật đóng sẵn: người xem lần đầu chỉ cần hình + hai hộp
                        with gr.Accordion('Chi tiết kỹ thuật — lý do của đèn, điểm từng dây, bảng chấm, thời gian xử lý', open=False):
                            S['cards5'] = gr.HTML()
                            S['cmp5'] = gr.Markdown()
                cols.append(col)
            # -------------------------------------------------------------- [C] thanh tóm tắt dính đáy màn hình
            summary = gr.HTML(story_summary_html(None), elem_classes=['rf-story', 'rf-sum-wrap'])
        # ------------------------------------------------------------------ [D] chế độ chuyên gia (8 tab cũ, nguyên vẹn)
        with gr.Row(elem_classes=['rf-expert-head']):
            expert = gr.Checkbox(value=False, label='Chế độ chuyên gia — hiện 8 tab đầy đủ (bảng số, dữ liệu của nhóm, tải tệp, nhật ký)')
        with gr.Column(visible=False) as expert_col:
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
                btn_phan_tich = gr.Button('Phân tích', variant='primary', scale=1)
            status = gr.Markdown('Chọn bản ghi rồi bấm **Phân tích**.')
            cards = gr.HTML()
            with gr.Tabs() as tabs:
                with gr.Tab('Tín hiệu (5 tầng)', id='tab_tin_hieu'):
                    fig_sig = gr.Plot(label='Từ tín hiệu thô đến kết quả')
                with gr.Tab('Chọn kênh — cả 4 kênh', id='tab_chon_kenh'):
                    leads_txt = gr.Markdown()
                    fig_leads = gr.Plot(label='Phần dư và đỉnh mô hình trên từng kênh; kênh được chọn tô nền xanh')
                with gr.Tab('Nhịp tim thai + đèn đoạn', id='tab_fhr'):
                    fig_fhr = gr.Plot(label='fHR và điểm tin cậy theo đoạn 4 s')
                with gr.Tab('So sánh với nhãn', id='tab_so_sanh'):
                    cmp_md = gr.Markdown()
                    cmp_df = gr.DataFrame(label='Danh sách sự kiện (FP, FN trước; TP tối đa 200 dòng)', wrap=True)
                with gr.Tab('Kết quả tổng hợp (60 bản sạch)', id='tab_tong_hop'):
                    gr.Markdown(SUMMARY_MD)
                with gr.Tab('Dữ liệu của nhóm', id='tab_du_lieu'):
                    gr.Markdown('## Dữ liệu của nhóm đang nằm ở đâu, định dạng thế nào\n\n'
                                'Chọn một bộ để xem **từng bản ghi có thật trên đĩa**: đường dẫn, định dạng, tần số lấy mẫu, '
                                'độ dài, số kênh bụng, số nhịp trong nhãn và **nhãn đó từ đâu ra**. '
                                'Sau đó chọn một bản ghi và bấm *Xem tín hiệu thô* để nhìn tận mắt dữ liệu chưa qua xử lý.')
                    ds_pick = gr.Dropdown(choices=list(DS_LABELS), value=list(DS_LABELS)[0], label='Bộ dữ liệu')
                    ds_info = gr.Markdown()
                    ds_table = gr.DataFrame(label='Từng bản ghi trong bộ (đọc thật từ tệp trên đĩa)', wrap=True)
                    with gr.Row(equal_height=True):
                        ds_rec = gr.Dropdown(choices=[], label='Bản ghi muốn xem tín hiệu thô', scale=4)
                        ds_btn = gr.Button('Xem tín hiệu thô', variant='secondary', scale=1)
                    ds_fig = gr.Plot(label='10 giây đầu, tất cả kênh bụng xếp chồng; vạch đỏ = nhãn nhịp thai')
                    ds_cap = gr.Markdown()
                    gr.Markdown(DS_HOWTO_MD)
                with gr.Tab('Tải dữ liệu mới', id='tab_tai_moi'):
                    gr.Markdown(UP_INTRO_MD)
                    up_files = gr.File(label='Tệp bản ghi — chọn NHIỀU tệp cùng lúc nếu là cặp .dat + .hea',
                                       file_count='multiple')
                    with gr.Row(equal_height=True):
                        up_fs = gr.Number(value=1000, precision=0, scale=1,
                                          label='Tần số lấy mẫu (Hz) — CHỈ dùng cho .csv / .npy / .txt')
                        up_lead = gr.Dropdown(choices=LEAD_CHOICES, value=LEAD_CHOICES[0], scale=2, label='Kênh bụng')
                        up_conf = gr.Dropdown(choices=CONF_CHOICES, value=CONF_CHOICES[0], scale=2, label='Đèn tin cậy')
                    up_lab = gr.File(label='Nhãn tham chiếu (tuỳ chọn): .qrs · .fqrs · .csv/.txt một cột chỉ số mẫu',
                                     file_count='multiple')
                    up_btn = gr.Button('Phân tích', variant='primary')
                    gr.HTML(UP_WARN_NOLABEL)
                    gr.HTML(UP_WARN_DOMAIN)
                    up_status = gr.Markdown('Chọn tệp rồi bấm **Phân tích**. Chưa chạy gì cả.')
                    up_cards = gr.HTML()
                    # tab con đặt tên "Kết quả: …" để không trùng tên với 8 tab ngoài
                    with gr.Tabs():
                        with gr.Tab('Kết quả: tín hiệu (5 tầng)'):
                            up_fig_sig = gr.Plot(label='Từ tín hiệu thô đến kết quả')
                        with gr.Tab('Kết quả: chọn kênh'):
                            up_leads_md = gr.Markdown()
                            up_fig_leads = gr.Plot(label='Phần dư và đỉnh mô hình trên từng kênh')
                        with gr.Tab('Kết quả: nhịp tim + đèn'):
                            up_fig_fhr = gr.Plot(label='fHR và điểm tin cậy theo đoạn 4 s')
                        with gr.Tab('Kết quả: so với nhãn'):
                            up_cmp = gr.Markdown()
                        with gr.Tab('Kết quả: nhật ký JSON'):
                            up_js = gr.JSON(label='Tóm tắt phân tích tệp tải lên')
                with gr.Tab('Nhật ký (JSON)', id='tab_json'):
                    js = gr.JSON(label='Tóm tắt phân tích — sao chép vào báo cáo')
        gr.HTML(f'<div class="rf-foot">{DISCLAIMER}</div>')

        # ------------------------------------------------------------------ sự kiện: chế độ trình bày
        # concurrency_id chung: bấm thẻ và bấm Tiếp/Quay lại xếp hàng tuần tự -> không có chuyện 'Tiếp' chạy song song
        # với phân tích rồi bị kết quả thẻ (về bước 1) ghi đè.
        view_outs = [step, progress, *cols, btn_back, btn_next]
        story_outs = [*card_comps,
                      S['fig1'], S['num1'], S['read1'],
                      S['fig2'], S['num2'], S['read2'],
                      S['fig3'], S['num3'], S['read3'],
                      S['fig4'], S['rules4'], S['num4'], S['read4'],
                      S['fig5'], S['cards5'], S['cmp5'], S['num5'], S['read5'],
                      summary, *view_outs, story_status]
        assert len(story_outs) == STORY_N_OUTS

        def _bam(n):                    # chạy ngay (queue=False): ghi thẻ bấm sau cùng + hiện "đang phân tích"
            def f(request: gr.Request):
                return story_request(n, _phien(request))
            return f

        def _chay(n):                   # xếp hàng 'trinh_bay': phân tích; bỏ qua nếu đã có thẻ bấm sau
            def f(request: gr.Request):
                return story_run(n, _phien(request))
            return f

        for comp, name in zip(card_comps, STORY_RECS):
            comp.click(None, None, None, js=JS_GHI_VI_TRI)
            (comp.click(_bam(name), None, story_status, queue=False)
                 .then(_chay(name), None, story_outs, concurrency_id='trinh_bay', show_progress='hidden',
                       **_api(f'trinh_bay_{name}'))
                 .then(None, None, None, js=JS_CUON_TOI_BUOC))
        # tên biến riêng: vòng lặp này từng dùng 'btn' và ghi đè nút "Phân tích" của chế độ chuyên gia
        for nut_buoc, delta in ((btn_next, +1), (btn_back, -1)):
            nut_buoc.click(None, None, None, js=JS_GHI_VI_TRI)
            (nut_buoc.click(lambda s, d=delta: story_step(s, d), step, view_outs, concurrency_id='trinh_bay', show_progress='hidden')
                .then(None, None, None, js=JS_CUON_TOI_BUOC))
        expert.change(toggle_expert, expert, expert_col)
        # thẻ 'Tệp của bạn': bật chế độ chuyên gia, hiện cột, RỒI mới chọn tab (chọn tab khi cột còn ẩn không có tác dụng),
        # rồi cuộn tới phần tải tệp (không cuộn thì người bấm không thấy gì thay đổi)
        ev_up = card_up.click(lambda: (True, gr.update(visible=True)), None, [expert, expert_col])
        ev_up.then(lambda: gr.update(selected='tab_tai_moi'), None, tabs).then(None, None, None, js=JS_CUON_TOI_TAI_TEP)

        # ------------------------------------------------------------------ sự kiện: chế độ chuyên gia (giữ nguyên)
        def _toggle(src):
            up = str(src).startswith('Tải'); show = str(src).startswith('Minh')
            return gr.update(visible=show), gr.update(visible=not up and not show), gr.update(visible=up), gr.update(visible=up)
        source.change(_toggle, source, [showcase, sample, upload, fs_in])
        outs = [fig_sig, fig_leads, leads_txt, fig_fhr, cards, cmp_md, cmp_df, js, status]
        ins = [source, upload, sample, lead, fs_in, conf, showcase]
        btn_phan_tich.click(run, ins, outs)
        ds_pick.change(run_dataset, ds_pick, [ds_table, ds_info, ds_rec], **_api('du_lieu_nhom'))
        ds_btn.click(run_dataset_raw, [ds_pick, ds_rec], [ds_fig, ds_cap], **_api('xem_tin_hieu_tho'))
        up_outs = [up_cards, up_fig_sig, up_fig_leads, up_leads_md, up_fig_fhr, up_cmp, up_js, up_status]
        # xoá kết quả cũ trước: nếu lần này lỗi thì màn hình không còn số của tệp trước trông như kết quả mới
        up_btn.click(upload_clear, None, up_outs, queue=False).then(
            run_upload, [up_files, up_fs, up_lead, up_conf, up_lab], up_outs, **_api('tai_du_lieu_moi'))
        demo.load(run_dataset, ds_pick, [ds_table, ds_info, ds_rec])   # mở trang là bảng dữ liệu đã sẵn
        if os.environ.get('RELYFETAL_AUTORUN', '1') == '1':
            first = next((n for n in STORY_RECS if n in RECS), None)
            if first:                                           # mở trang là thấy ngay thẻ đầu (r01)
                def _mo_trang(request: gr.Request):
                    if _phien(request) is not None:
                        _YEU_CAU[_phien(request)] = first
                    return story_loading_html(first, lan_dau=True)
                (demo.load(_mo_trang, None, story_status, queue=False)
                     .then(_chay(first), None, story_outs, concurrency_id='trinh_bay', show_progress='hidden'))
            # 8 tab cũ chỉ tự chạy khi được yêu cầu (mặc định ẩn -> chạy r01 hai lần lúc mở là phí)
            if SHOWCASE_LABELS and os.environ.get('RELYFETAL_AUTORUN_EXPERT', '0') == '1':
                demo.load(run, ins, outs)
    return demo


def launch_kwargs(**extra):
    """theme/css chuyển sang launch() ở Gradio >= 6 -- xử lý cả hai đời."""
    kw = dict(server_name='127.0.0.1', inbrowser=False, show_error=True,
              footer_links=[])          # Gradio 6: ẩn "Use via API · Built with Gradio · Settings" (CSS footer là dự phòng)
    sig = inspect.signature(gr.Blocks.launch).parameters
    if 'css' in sig and 'css' not in inspect.signature(gr.Blocks.__init__).parameters:
        kw['css'] = CSS
    if 'theme' in sig and 'theme' not in inspect.signature(gr.Blocks.__init__).parameters and hasattr(gr, 'themes'):
        kw['theme'] = gr.themes.Soft(primary_hue='emerald')
    kw.update(extra)
    return {k: v for k, v in kw.items() if k in sig}


demo = build_app()
server_app = fastapi.FastAPI(title='RelyFetal Live Clinical ECG Monitor')


@server_app.get('/monitor', response_class=HTMLResponse)
def monitor_page():
    return HTMLResponse(content=MONITOR_HTML)


@server_app.get('/api/monitor_data')
def monitor_data(rec: str = 'r01'):
    recs = core.sample_records()
    rec_name = rec if rec in recs else 'r01'
    rec_obj = core.load_sample(rec_name, recs)
    out = core.analyze_record(rec_obj, lead='peakprob')

    raw_1000 = out.get('raw', np.array([]))
    if len(raw_1000) > 0:
        step = max(1, int(out.get('fs_raw', 1000) // 250))
        raw_250 = raw_1000[::step]
    else:
        raw_250 = np.array([])

    residual = out.get('residual_250', np.array([]))
    peaks_250 = out.get('fetal_peaks_250', np.array([]))
    peaks_sec = [float(p / 250.0) for p in peaks_250]

    fhr_time = out.get('fhr_time_s', np.array([]))
    fhr_series = out.get('fhr_series', np.array([]))
    tachogram = []
    for t, b in zip(fhr_time, fhr_series):
        if np.isfinite(b):
            tachogram.append({'t': round(float(t), 2), 'bpm': round(float(b), 1)})

    dur_limit = min(30.0, float(out.get('duration_s', 30.0)))
    n_samples = int(dur_limit * 250)
    residual = residual[:n_samples]
    raw_250 = raw_250[:n_samples]
    peaks_sec = [round(float(p), 3) for p in peaks_sec if p <= dur_limit]
    tachogram = [t for t in tachogram if t['t'] <= dur_limit]

    def _norm_signal(sig):
        if len(sig) == 0:
            return []
        s = np.asarray(sig, dtype=float)
        s = s - np.median(s)
        p99 = np.percentile(np.abs(s), 99.5) if len(s) > 0 else 1.0
        scale = p99 if p99 > 1e-12 else (np.max(np.abs(s)) if np.max(np.abs(s)) > 1e-12 else 1.0)
        return [round(float(v), 5) for v in (s / scale)]

    norm_res = _norm_signal(residual)
    norm_raw = _norm_signal(raw_250)

    m_peaks = out.get('maternal_peaks', np.array([]))
    m_peaks_sec = [round(float(p / 250.0), 3) for p in m_peaks if (p / 250.0) <= dur_limit]
    m_bpm = 74.0
    if len(m_peaks) > 1:
        dur_m = (m_peaks[-1] - m_peaks[0]) / 250.0
        if dur_m > 0:
            m_bpm = round((len(m_peaks) - 1) / dur_m * 60.0, 1)

    f1 = None
    if 'metrics' in out and 'F1' in out['metrics']:
        f1 = round(float(out['metrics']['F1']), 2)

    return JSONResponse({
        'case_name': rec_name,
        'duration': dur_limit,
        'fs': 250,
        'signals': {
            'residual': norm_res,
            'raw': norm_raw,
        },
        'max_amp': 1.0,
        'peaks': peaks_sec,
        'maternal_peaks': m_peaks_sec,
        'tachogram': tachogram,
        'median_fhr': round(float(out.get('fhr_mean', 140.0)), 1),
        'maternal_bpm': m_bpm,
        'f1_score': f1,
        'latency_ms': round(float(out.get('latency_ms', 12.0)), 1),
    })



@server_app.get('/', response_class=HTMLResponse)
def home_research_page():
    """Trang chủ Nghiên cứu RelyFetal — Giao diện OLED Hiện đại thuần FastAPI + Plotly.js."""
    return HTMLResponse(content=RESEARCH_HTML)


@server_app.post('/api/run_analysis')
async def api_run_analysis(request: fastapi.Request):
    t0 = time.perf_counter()
    try:
        data = await request.json()
    except Exception:
        data = {}
    rec_name = data.get('rec_name', 'r01')
    lead_mode_in = data.get('lead_mode', 'peakprob')
    conf_mode_in = data.get('conf_mode', 'hoc')

    recs = core.sample_records()
    if rec_name not in recs:
        for k in recs:
            if k == rec_name or rec_name in k:
                rec_name = k
                break
        else:
            rec_name = 'r01'
    rec_obj = core.load_sample(rec_name, recs)
    lead_arg = _lead_arg(lead_mode_in) if lead_mode_in in LEAD_MODE or lead_mode_in in ('1', '2', '3', '4') else 'peakprob'
    conf_mode = 'hoc' if conf_mode_in in ('hoc', CONF_CHOICES[0]) else 'luat'

    out = core.analyze_record(rec_obj, lead=lead_arg, confidence_mode=conf_mode)
    wall = (time.perf_counter() - t0) * 1000

    fig_sig = signal_figure(out)
    fig_leads = leads_figure(out)
    fig_fhr = fhr_figure(out)

    lead_chips = []
    if out.get('lead_scores'):
        rule_k = out.get('lead_rule', 'peakprob')
        fmt = (lambda v: f'{v:.3f}') if rule_k == 'peakprob' else (lambda v: f'{v:.2e}')
        # F1 từng kênh nằm ở out['leads'][k]['F1'] (khoá 'candidate_metrics' không tồn tại -> cột F1 từng luôn rỗng)
        leads_out = out.get('leads') or {}
        for k, v in out['lead_scores'].items():
            f1_str = None
            if k in leads_out and leads_out[k].get('F1') is not None:
                f1_str = f"{leads_out[k]['F1']:.1f}"
            lead_chips.append({
                'lead': k,
                'score': fmt(v),
                'f1': f1_str,
                'selected': (k == out.get('lead'))
            })

    conf_obj = None
    if 'confidence' in out:
        # Mức đèn nằm ở out['confidence']['level'] ('cao' / 'trung_binh' / 'thap'). Khoá 'gate' không tồn tại, nên
        # bản 16/09 luôn rơi về 'xanh': a02 (đèn ĐỎ thật) hiện "XANH (tin cậy)". Sửa 17/09 khi ghép vòng 10.
        c_state = {'cao': 'xanh', 'trung_binh': 'vang', 'thap': 'do'}.get(out['confidence'].get('level'), 'vang')
        col_map = {'xanh': '#30d158', 'vang': '#ffd60a', 'do': '#ff453a'}
        label_map = {'xanh': 'XANH (tin cậy)', 'vang': 'VÀNG (nghi ngờ)', 'do': 'ĐỎ (từ chối)'}
        conf_obj = {
            'state': c_state,
            'label': label_map.get(c_state, c_state.upper()),
            'color': col_map.get(c_state, '#30d158'),
            'score': float(out['confidence'].get('score', 1.0)),
            'mode_label': core.CONF_MODE_LABEL.get(out.get('confidence_mode', 'hoc'), '')
        }

    leads_html = markdown.markdown(leads_md(out), extensions=['tables', 'fenced_code'])
    cmp_html = markdown.markdown(compare_md(out), extensions=['tables', 'fenced_code'])
    cmp_df_obj = compare_df(out)
    cmp_table_html = (cmp_df_obj.to_html(classes='table', index=False)
                      if cmp_df_obj is not None and not cmp_df_obj.empty
                      else '<p style="color:var(--text-muted)">Không có sự kiện nhãn đối chiếu.</p>')

    summary_obj = core.summary(out)

    # Định dạng status và cards_html y chang Gradio ban đầu
    lead_txt = ''
    if out.get('lead_scores'):
        key = out.get('lead_rule')
        fmt = (lambda v: f'{v:.3f}') if key == 'peakprob' else (lambda v: f'{v:.2e}')
        lead_txt = f' · điểm {key} từng kênh: ' + ', '.join(f'k{k}={fmt(v)}' for k, v in out['lead_scores'].items())
    note = out.get('record_note') or ''
    status_raw = (f'Đã phân tích **{out["record"]}** ({out["source"]}, {out["duration_s"]:.0f} s, {rec_obj["signals"].shape[0]} kênh'
                  f'{"; " + note if note else ""}) — kênh **{out["lead"]}** ({out["lead_mode"]}){lead_txt} — checkpoint *{out["checkpoint_note"]}* '
                  f'— đèn tin cậy: *{core.CONF_MODE_LABEL[out["confidence_mode"]]}*.')
    status_html = markdown.markdown(status_raw)
    cards_html_code = cards_html(out, wall)

    return JSONResponse({
        'record': out.get('record', rec_name),
        'duration_s': float(out.get('duration_s', 0.0)),
        'fhr_mean': float(out.get('fhr_mean', 0.0)) if out.get('fhr_mean') is not None else None,
        'n_beats': len(out.get('fetal_peaks_250', [])),
        'lead': out.get('lead', 1),
        'n_leads': rec_obj['signals'].shape[0],
        'lead_rule': out.get('lead_rule', 'peakprob'),
        'lead_chips': lead_chips,
        'confidence': conf_obj,
        'latency_ms': round(wall, 1),
        'latency_all_ms': round(float(out.get('latency_ms', wall)), 1),
        'checkpoint_note': out.get('checkpoint_note', ''),
        'status_html': status_html,
        'cards_html': cards_html_code,
        'fig_sig': fig_sig.to_json(),
        'fig_leads': fig_leads.to_json(),
        'fig_fhr': fig_fhr.to_json(),
        'leads_html': leads_html,
        'cmp_html': cmp_html,
        'cmp_table_html': cmp_table_html,
        'summary_json': summary_obj
    })


@server_app.get('/api/list_samples')
def api_list_samples():
    recs = core.sample_records()
    items = [{'name': n, 'label': _rec_label(n)} for n in recs]
    return JSONResponse({'records': items})


@server_app.get('/api/summary_info')
def api_summary_info():
    md = summary_tables_md()
    return JSONResponse({'html': markdown.markdown(md, extensions=['tables', 'fenced_code'])})


@server_app.get('/api/dataset_table')
def api_dataset_table(ds: str = 'adfecgdb'):
    key = ds if ds in core.DATASET_KEYS else DS_LABELS.get(ds, 'adfecgdb')
    df, head, _ = dataset_table(key)
    rows, _ = core.dataset_rows(key)
    records = [r['ten'] for r in rows] if rows else []
    table_html = markdown.markdown(head, extensions=['tables', 'fenced_code']) + df.to_html(classes='table', index=False)
    return JSONResponse({
        'table_html': table_html,
        'records': records
    })


@server_app.post('/api/dataset_raw')
async def api_dataset_raw(request: fastapi.Request):
    data = await request.json()
    ds = data.get('ds', 'adfecgdb')
    rec = data.get('rec', '')
    key = ds if ds in core.DATASET_KEYS else DS_LABELS.get(ds, 'adfecgdb')
    try:
        fig, cap = dataset_raw_figure(key, rec)
        return JSONResponse({
            'fig': fig.to_json(),
            'cap': markdown.markdown(cap, extensions=['tables', 'fenced_code'])
        })
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=400)


def mount_kwargs():
    """CSS/theme/ẩn chân trang cho Gradio khi GẮN vào FastAPI. Gradio 6 chỉ nhận css ở launch() hoặc mount_gradio_app();
    thiếu phần này thì chế độ trình bày ở /gradio mất toàn bộ bố cục thẻ, thanh bước, thanh tóm tắt."""
    sig = inspect.signature(gr.mount_gradio_app).parameters
    kw = dict(css=CSS, footer_links=[])
    if hasattr(gr, 'themes'):
        kw['theme'] = gr.themes.Soft(primary_hue='emerald')
    return {k: v for k, v in kw.items() if k in sig}


# Gắn Gradio Blocks (chế độ trình bày 5 bước + chế độ chuyên gia 8 tab) vào đường dẫn '/gradio'
server_app = gr.mount_gradio_app(server_app, demo, path='/gradio', **mount_kwargs())

if __name__ == '__main__':
    port = int(os.environ.get('RELYFETAL_PORT', '7860'))
    print(f'RelyFetal Web App: http://127.0.0.1:{port}   ({DISCLAIMER})')
    print(f'Live Monitor:      http://127.0.0.1:{port}/monitor')
    print(f'Chế độ trình bày:  http://127.0.0.1:{port}/gradio/   (5 bước; Chế độ chuyên gia = 8 tab)')
    uvicorn.run(server_app, host='127.0.0.1', port=port, log_level='info')

