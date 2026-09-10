# -*- coding: utf-8 -*-
"""
RelyFetal -- demo web một trang (Gradio + Plotly), chạy cục bộ.

    python demo/app.py            # mở http://127.0.0.1:7860

Mọi tính toán nằm ở demo/core.py (không phụ thuộc gradio); file này chỉ dựng giao diện và vẽ.
Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.
"""
import os, sys, time, inspect, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

import numpy as np
import pandas as pd
import gradio as gr
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import core

DISCLAIMER = 'Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.'
UPLOAD_DIR = os.path.join(HERE, '_uploads')
RECS = core.sample_records()
LEAD_CHOICES = ['Tự động (PSD)', '1', '2', '3', '4']
VIEW_S = 10.0                       # cửa sổ hiển thị ban đầu (giây); kéo/thả để phóng to, cuộn để dịch

COL = dict(raw='#6b7280', filt='#2563eb', mat='#dc2626', res='#0f766e', lab='#111827',
           prob='#7c3aed', thr='#ea580c', det='#16a34a', tp='#16a34a', fp='#dc2626', fn='#f59e0b')


def _rec_label(name):
    d = RECS[name]
    ck = 'fold ' + name if name in core.ADFECGDB_RECS else 'production'
    return f'{name} — {d["dataset"]} · checkpoint {ck}'


REC_LABELS = {_rec_label(n): n for n in RECS}


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
    titles = [f'[1] Tín hiệu thô, kênh {out.get("lead", "?")} ({out["fs_raw"]} Hz{", hiển thị 1/4 mẫu" if step > 1 else ""})',
              f'[2] Đã lọc 10–60 Hz + notch 50 Hz, 250 Hz — vạch đỏ: {len(mpk)} nhịp mẹ (QRS mẹ)',
              f'[3] Sau khử mẹ (phần dư đưa vào mô hình)' + (f' — vạch đen: {len(lab)} nhịp thai theo nhãn' if has_lab else ' — không có nhãn'),
              f'[4] Xác suất nhịp thai của FetalQRS-TCN — ngưỡng {thr:.2f} (cố định từ tập validation)',
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


def fhr_figure(out):
    fig = go.Figure()
    fig.add_hrect(y0=110, y1=160, fillcolor='rgba(22,163,74,0.10)', line_width=0,
                  annotation_text='vùng bình thường 110–160 bpm', annotation_position='top left',
                  annotation_font=dict(color='#15803d', size=12))
    lab = out.get('labels_1000')
    if lab is not None:
        rt, rb = core.fhr_series(np.asarray(lab) / (out['fs_raw'] / out['fs']), len(out['residual_250']))
        fig.add_trace(go.Scatter(x=rt, y=rb, mode='lines+markers', name='Theo nhãn', line=dict(color='#111827', width=1.5, dash='dot'),
                                 marker=dict(size=5), hovertemplate='%{x:.0f} s<br>%{y:.1f} bpm<extra>nhãn</extra>'))
    fig.add_trace(go.Scatter(x=out['fhr_time_s'], y=out['fhr_series'], mode='lines+markers', name='Mô hình (cửa sổ 4 s)',
                             line=dict(color=COL['filt'], width=2.5), marker=dict(size=7),
                             hovertemplate='%{x:.0f} s<br>%{y:.1f} bpm<extra>mô hình</extra>'))
    if np.isfinite(out['fhr_mean']):
        fig.add_hline(y=out['fhr_mean'], line=dict(color=COL['filt'], width=1, dash='dash'),
                      annotation_text=f'trung bình {out["fhr_mean"]:.0f} bpm', annotation_position='bottom right')
    fig.update_yaxes(title_text='nhịp tim thai (bpm)', range=[60, 220], showgrid=True, gridcolor='rgba(0,0,0,0.06)')
    fig.update_xaxes(title_text='thời gian (s)', showgrid=True, gridcolor='rgba(0,0,0,0.06)')
    fig.update_layout(height=380, margin=dict(l=60, r=20, t=30, b=50), plot_bgcolor='white', paper_bgcolor='white',
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), hovermode='x unified')
    return fig


# =========================================================================== thẻ số & bảng
def _fmt(v, f='{:.0f}'):
    return f.format(v) if v is not None and np.isfinite(v) else '—'


def cards_html(out, wall_ms=None):
    c = out['confidence']
    reasons = ''.join(f'<li>{r}</li>' for r in c['reasons'])
    mode = out.get('lead_mode', '')
    ck = out.get('checkpoint_note', out['checkpoint'])
    lat = out['latency_ms']
    return f'''
<div class="rf-cards">
  <div class="rf-card"><div class="rf-k">fHR trung bình</div>
    <div class="rf-v">{_fmt(out['fhr_mean'])}<span class="rf-u"> bpm</span></div>
    <div class="rf-s">median RR trong từng cửa sổ 4 s</div></div>
  <div class="rf-card"><div class="rf-k">Số nhịp thai phát hiện</div>
    <div class="rf-v">{out['n_beats']}</div>
    <div class="rf-s">{out['duration_s']:.0f} s · kênh {out.get('lead', '?')} ({mode})</div></div>
  <div class="rf-card rf-conf" style="border-color:{c['color']};background:{c['color']}14">
    <div class="rf-k">Đèn tin cậy</div>
    <div class="rf-v" style="color:{c['color']}">● {c['label']}</div>
    <div class="rf-s">điểm {c['score']:.2f} / 1 — quy tắc cứng tạm thời, sẽ thay bằng fSQI tô-pô</div>
    <ul class="rf-r">{reasons}</ul></div>
  <div class="rf-card"><div class="rf-k">Thời gian xử lý</div>
    <div class="rf-v">{lat:,.0f}<span class="rf-u"> ms</span></div>
    <div class="rf-s">tiền xử lý + khử mẹ + mô hình, CPU 4 luồng{f" · toàn bộ kể cả đọc file & vẽ: {wall_ms:,.0f} ms" if wall_ms else ""}<br>checkpoint: {ck}</div></div>
</div>'''


def compare_md(out):
    if 'metrics' not in out:
        return ('**Bản ghi không có nhãn** — chế độ so sánh tắt. Với file tải lên, thêm file nhãn `.txt` '
                '(mỗi dòng một chỉ số mẫu) hoặc chú giải WFDB `.fqrs` / `.edf.qrs` cùng tên để bật.')
    m = out['metrics']
    return f'''
**Giao thức chấm:** dung sai ±{core.CFG['tolerance_ms']} ms, ghép một-đối-một tham lam (quy ước CinC 2013 / Behar 2014).
Nhãn: {len(out['labels_1000'])} nhịp thai. Mô hình: {out['n_beats']} nhịp.

| Se | PPV | F1 | Jitter |
|---:|---:|---:|---:|
| **{m['Se']:.2f} %** | **{m['PPV']:.2f} %** | **{m['F1']:.2f}** | {_fmt(m['jitter_ms'], '{:.2f}')} ms |

| TP (đúng) | FP (dư) | FN (sót) |
|---:|---:|---:|
| {m['TP']} | {m['FP']} | {m['FN']} |
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
def run(source, upload_files, sample_label, lead_choice, fs_in):
    t0 = time.perf_counter()
    try:
        if source.startswith('Tải'):
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
            name = REC_LABELS.get(sample_label)
            if name is None:
                raise gr.Error('Chưa có bản ghi mẫu nào trên đĩa — hãy tải dữ liệu (xem README) hoặc tải file lên.')
            rec = core.load_record(RECS[name]['path'])
        lead = 'auto' if lead_choice.startswith('Tự') else int(lead_choice)
        out = core.analyze_record(rec, lead=lead)
    except gr.Error:
        raise
    except Exception as e:                       # noqa: BLE001
        raise gr.Error(f'Lỗi khi phân tích: {e}')
    fig1, fig2 = signal_figure(out), fhr_figure(out)
    wall = (time.perf_counter() - t0) * 1000
    s = core.summary(out)
    lead_txt = ''
    if out.get('lead_scores'):
        lead_txt = ' · PSD dải thai từng kênh: ' + ', '.join(f'k{k}={v:.2e}' for k, v in out['lead_scores'].items())
    status = (f'Đã phân tích **{out["record"]}** ({out["source"]}, {out["duration_s"]:.0f} s, {rec["signals"].shape[0]} kênh) '
              f'— kênh **{out["lead"]}** ({out["lead_mode"]}){lead_txt} — checkpoint *{out["checkpoint_note"]}*.')
    return fig1, fig2, cards_html(out, wall), compare_md(out), compare_df(out), s, status


CSS = '''
.rf-cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:6px 0 2px}
@media (max-width:900px){.rf-cards{grid-template-columns:repeat(2,minmax(0,1fr))}}
.rf-card{border:1.5px solid #e5e7eb;border-radius:12px;padding:12px 14px;background:#fff;min-height:110px}
.rf-k{font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:#6b7280;font-weight:600}
.rf-v{font-size:30px;font-weight:700;line-height:1.25;margin:4px 0 2px;color:#111827}
.rf-u{font-size:15px;font-weight:500;color:#6b7280}
.rf-s{font-size:12px;color:#6b7280}
.rf-r{margin:8px 0 0;padding-left:18px;font-size:12.5px;color:#374151;line-height:1.45}
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
    with gr.Blocks(**bk) as demo:
        gr.HTML('<div class="rf-title"><h1>RelyFetal — dò phức bộ QRS thai nhi từ điện tim ổ bụng <em>đơn kênh</em></h1>'
                '<p>FetalQRS-TCN (113 481 tham số, CPU) · khử QRS mẹ bằng mẫu trung vị · chọn kênh mù nhãn theo PSD · đèn tin cậy. '
                f'<b style="color:#991b1b">{DISCLAIMER}</b></p></div>')
        with gr.Row(equal_height=True):
            source = gr.Radio(['Bản ghi mẫu', 'Tải lên file'], value='Bản ghi mẫu', label='Nguồn dữ liệu', scale=1)
            sample = gr.Dropdown(choices=list(REC_LABELS), value=(list(REC_LABELS)[0] if REC_LABELS else None),
                                 label='Bản ghi mẫu (ADFECGDB rXX dùng fold checkpoint chưa từng thấy rXX)', scale=3)
            upload = gr.File(label='Tải lên: .edf · .hea+.dat(+.fqrs) · .csv · .npy · .txt (kèm nhãn .txt tuỳ chọn)',
                             file_count='multiple', visible=False, scale=3)
            fs_in = gr.Number(value=1000, label='fs của CSV/NPY (Hz)', precision=0, visible=False, scale=1)
            lead = gr.Dropdown(choices=LEAD_CHOICES, value=LEAD_CHOICES[0], label='Kênh bụng', scale=1)
            btn = gr.Button('Phân tích', variant='primary', scale=1)
        status = gr.Markdown('Chọn bản ghi rồi bấm **Phân tích**.')
        cards = gr.HTML()
        with gr.Tabs():
            with gr.Tab('Tín hiệu (5 tầng)'):
                fig_sig = gr.Plot(label='Từ tín hiệu thô đến kết quả')
            with gr.Tab('Nhịp tim thai theo thời gian'):
                fig_fhr = gr.Plot(label='fHR')
            with gr.Tab('So sánh với nhãn'):
                cmp_md = gr.Markdown()
                cmp_df = gr.DataFrame(label='Danh sách sự kiện (FP, FN trước; TP tối đa 200 dòng)', wrap=True)
            with gr.Tab('Nhật ký (JSON)'):
                js = gr.JSON(label='Tóm tắt phân tích — sao chép vào báo cáo')
        gr.HTML(f'<div class="rf-foot">{DISCLAIMER}</div>')

        def _toggle(src):
            up = src.startswith('Tải')
            return gr.update(visible=not up), gr.update(visible=up), gr.update(visible=up)
        source.change(_toggle, source, [sample, upload, fs_in])
        outs = [fig_sig, fig_fhr, cards, cmp_md, cmp_df, js, status]
        btn.click(run, [source, upload, sample, lead, fs_in], outs)
        if REC_LABELS and os.environ.get('RELYFETAL_AUTORUN', '1') == '1':
            demo.load(run, [source, upload, sample, lead, fs_in], outs)     # mở trang là thấy ngay kết quả r01
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
