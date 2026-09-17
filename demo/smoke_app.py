# -*- coding: utf-8 -*-
"""
Khởi động thử demo Gradio (không mở trình duyệt) -- kiểm tra 4 tầng:
  1. server lên, HTTP GET / trả 200
  2. gọi TRỰC TIẾP hàm xử lý app.run() theo đúng đường đi của nút "Phân tích" với r01 (tự động chọn kênh peakprob)
     -> phải có F1 trong JSON tóm tắt
  3. gọi qua gradio_client (API /run) -- nếu phiên bản gradio hỗ trợ; lỗi ở tầng này chỉ cảnh báo
  4. hai tab mới: 'Dữ liệu của nhóm' (bảng metadata + hình tín hiệu thô) và 'Tải dữ liệu mới'
     (tệp ví dụ demo/assets/vidu_tai_len.csv, CÓ nhãn -> có F1; KHÔNG nhãn -> không có F1; lỗi thân thiện)
Ghi demo/results/smoke_app.json.  Chạy:  python demo/smoke_app.py
"""
import os, sys, time, json, traceback
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
PORT = int(os.environ.get('RELYFETAL_SMOKE_PORT', '7861'))
os.environ.setdefault('RELYFETAL_AUTORUN', '1')          # giữ đúng cấu hình thật (mở trang là chạy r01)

import requests
import gradio as gr
import plotly

t_import = time.perf_counter()
import app                                                 # dựng Blocks ngay khi import
t_import = time.perf_counter() - t_import

res = dict(gradio=gr.__version__, plotly=plotly.__version__, python=sys.version.split()[0],
           port=PORT, build_s=round(t_import, 2), ok=False)
url = f'http://127.0.0.1:{PORT}/'
demo = app.demo
try:
    # ---------------------------------------------------------------- 1. server
    t0 = time.perf_counter()
    demo.launch(**app.launch_kwargs(server_port=PORT, prevent_thread_lock=True, quiet=True))
    code = None
    for _ in range(40):                                    # tối đa ~20 s
        time.sleep(0.5)
        try:
            code = requests.get(url, timeout=5).status_code
            if code == 200:
                break
        except requests.RequestException:
            code = None
    res['http_status'] = code; res['launch_s'] = round(time.perf_counter() - t0, 2)
    print(f'[1] GET {url} -> {code}  (khởi động {res["launch_s"]} s)')
    assert code == 200, f'HTTP {code}'
    cfg = requests.get(url + 'config', timeout=10).json()
    res['n_components'] = len(cfg.get('components', [])); res['n_dependencies'] = len(cfg.get('dependencies', []))
    print(f'    config: {res["n_components"]} thành phần, {res["n_dependencies"]} sự kiện')

    # ---------------------------------------------------------------- 2. gọi thẳng hàm xử lý
    label = next(l for l, n in app.REC_LABELS.items() if n == 'r01')
    t0 = time.perf_counter()
    fig1, fig_leads, leads_md, fig2, cards, cmp_md, cmp_df, summ, status = app.run('Bản ghi mẫu', None, label, app.LEAD_CHOICES[0], 1000)
    res['direct_wall_s'] = round(time.perf_counter() - t0, 2)
    assert fig1 is not None and fig2 is not None and fig_leads is not None and 'rf-cards' in cards
    assert summ['lead_rule'] == 'peakprob' and len(summ['leads']) == 4
    assert 'metrics' in summ and summ['metrics']['F1'] is not None
    res['direct'] = dict(record=summ['record'], lead=summ['lead'], checkpoint=summ['checkpoint'],
                         F1=summ['metrics']['F1'], Se=summ['metrics']['Se'], PPV=summ['metrics']['PPV'],
                         n_beats=summ['n_beats'], fhr_mean=summ['fhr_mean'], level=summ['confidence']['level'],
                         latency_ms=summ['latency_ms'], n_traces_fig1=len(fig1.data), n_rows_cmp=int(len(cmp_df)))
    print(f'[2] app.run(r01, tự động) -> kênh {summ["lead"]}, F1 = {summ["metrics"]["F1"]:.2f}, '
          f'đèn = {summ["confidence"]["level"]}, {res["direct_wall_s"]} s')

    # ---------------------------------------------------------------- 3. gradio_client (bắt buộc nếu gói có sẵn)
    # Tầng này đi qua đúng đường postprocess của Gradio (đã bắt được lỗi khóa int trong gr.JSON ở Gradio 6).
    try:
        from gradio_client import Client
    except ImportError as e:
        Client = None; res['client_error'] = f'gradio_client chưa cài: {e}'
        print(f'[3] bỏ qua gradio_client: {e}')
    if Client is not None:
        cl = Client(url, verbose=False)
        names = list(cl.view_api(return_format='dict', print_info=False).get('named_endpoints', {}).keys())
        res['api_endpoints'] = names
        ep = '/run' if '/run' in names else (names[0] if names else None)
        assert ep, 'không có endpoint nào'
        t0 = time.perf_counter()
        out = cl.predict('Bản ghi mẫu', None, label, app.LEAD_CHOICES[0], 1000, app.CONF_CHOICES[0], None, api_name=ep)
        js = out[7]
        if isinstance(js, str):
            js = json.loads(js)
        res['client'] = dict(endpoint=ep, wall_s=round(time.perf_counter() - t0, 2), n_outputs=len(out),
                             F1=js['metrics']['F1'], level=js['confidence']['level'])
        assert abs(js['metrics']['F1'] - res['direct']['F1']) < 1e-6, 'F1 qua API khác F1 gọi trực tiếp'
        print(f'[3] gradio_client {ep} -> {len(out)} đầu ra, F1 = {js["metrics"]["F1"]:.2f}, {res["client"]["wall_s"]} s')
    # ---------------------------------------------------------------- 4. hai tab mới (A1 + A2)
    # gọi thẳng hàm xử lý (như tầng 2) rồi lặp lại qua gradio_client nếu có endpoint tương ứng.
    t0 = time.perf_counter()
    ds_lab = list(app.DS_LABELS)[0]
    df, md, upd = app.run_dataset(ds_lab)
    assert len(df) > 0 and 'Bản ghi' in list(df.columns) and md.strip()
    ten = (upd.get('choices') or [None])[0]
    ten = ten[0] if isinstance(ten, (tuple, list)) else ten
    fig_ds, cap_ds = app.run_dataset_raw(ds_lab, ten)
    res['tab_du_lieu'] = dict(bo=ds_lab, n_ban_ghi=int(len(df)), ban_ghi=str(ten),
                              n_traces=len(fig_ds.data), wall_s=round(time.perf_counter() - t0, 2))
    print(f'[4a] Dữ liệu của nhóm: {ds_lab} -> {len(df)} bản ghi; xem thô {ten} -> '
          f'{len(fig_ds.data)} trace, {res["tab_du_lieu"]["wall_s"]} s')

    import os as _os
    vidu = _os.path.join(app.ASSET_DIR, 'vidu_tai_len.csv')
    vidu_lab = _os.path.join(app.ASSET_DIR, 'vidu_tai_len_nhan.csv')
    if _os.path.isfile(vidu):
        t0 = time.perf_counter()
        o = app.run_upload([vidu], 1000, app.LEAD_CHOICES[0], app.CONF_CHOICES[0], [vidu_lab])
        su = o[6]
        assert 'rf-cards' in o[0] and su['metrics']['F1'] is not None
        t_co = round(time.perf_counter() - t0, 2)
        t0 = time.perf_counter()
        o2 = app.run_upload([vidu], 1000, app.LEAD_CHOICES[0], app.CONF_CHOICES[0], None)
        assert 'metrics' not in o2[6] and 'không có nhãn' in o2[5]
        res['tab_tai_len'] = dict(tep='vidu_tai_len.csv', F1_khi_co_nhan=su['metrics']['F1'],
                                  lead=su['lead'], level=su['confidence']['level'],
                                  wall_co_nhan_s=t_co, wall_khong_nhan_s=round(time.perf_counter() - t0, 2))
        print(f'[4b] Tải dữ liệu mới: vidu_tai_len.csv -> kênh {su["lead"]}, F1 = {su["metrics"]["F1"]:.2f}, '
              f'{t_co} s; không nhãn -> KHÔNG có F1 (đúng)')
        # lỗi không ném ra giao diện nữa: hiện ở dòng trạng thái (phần tử cuối), kết quả cũ bị xoá
        o3 = app.run_upload([], 1000, app.LEAD_CHOICES[0], app.CONF_CHOICES[0], None)
        loi = o3[-1]
        assert len(o3) == 8 and loi.startswith('**Không phân tích được tệp.**') and 'Traceback' not in loi
        assert o3[0] == '' and o3[1] is None
        res['tab_tai_len']['loi_than_thien'] = loi[:120]
        print(f'[4c] lỗi thân thiện khi không có tệp: {loi[:70]}')
    else:
        res['tab_tai_len'] = dict(bo_qua='chưa có demo/assets/vidu_tai_len.csv')
        print('[4b] bỏ qua: chưa có demo/assets/vidu_tai_len.csv')

    if Client is not None:
        names2 = res.get('api_endpoints') or []
        for ep, args in (('/du_lieu_nhom', (ds_lab,)), ('/xem_tin_hieu_tho', (ds_lab, ten))):
            if ep in names2:
                t0 = time.perf_counter()
                cl.predict(*args, api_name=ep)
                print(f'[4d] gradio_client {ep} -> OK, {time.perf_counter() - t0:.2f} s')
                res.setdefault('client_tab_moi', {})[ep] = round(time.perf_counter() - t0, 2)

    # ---------------------------------------------------------------- 5. chế độ trình bày (T3): bấm thẻ -> 33 đầu ra, 5 bước
    the = next((n for n in app.STORY_RECS if n in app.RECS), None)
    if the:
        t0 = time.perf_counter()
        o = app.story_run(the)
        assert len(o) == 33 and o[-10] == 1 and 'rf-sum-i' in o[-11] and o[-1] == ''
        vis = [u['visible'] for u in app.story_view(3)[2:7]]
        assert vis == [False, False, True, False, False]
        res['trinh_bay'] = dict(the=the, n_dau_ra=len(o), wall_s=round(time.perf_counter() - t0, 2))
        print(f'[5] chế độ trình bày: thẻ {the} -> {len(o)} đầu ra, về bước 1, {res["trinh_bay"]["wall_s"]} s')
    else:
        res['trinh_bay'] = dict(bo_qua='không có thẻ nào trên đĩa')

    res['ok'] = True
except Exception as e:                                      # noqa: BLE001
    res['error'] = f'{type(e).__name__}: {e}'
    print('LỖI:', res['error']); traceback.print_exc(limit=3)
finally:
    try:
        demo.close()
    except Exception:                                       # noqa: BLE001
        pass
    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    with open(os.path.join(HERE, 'results', 'smoke_app.json'), 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    print('KẾT QUẢ:', 'ĐẠT' if res['ok'] else 'LỖI', '-> demo/results/smoke_app.json')
    sys.exit(0 if res['ok'] else 1)
