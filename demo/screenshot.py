# -*- coding: utf-8 -*-
"""
Chụp màn hình demo bằng playwright (Chromium headless) -> demo/screenshots/*.png  (cho đề cương / báo cáo).

  01_r01_tin_hieu.png   r01, tự động chọn kênh: thẻ số + tab "Tín hiệu (5 tầng)"   (toàn trang)
  02_r01_fhr.png        r01: tab "Nhịp tim thai theo thời gian"
  03_r01_so_sanh.png    r01: tab "So sánh với nhãn"
  04_r01_the_so.png     r01: chỉ 4 thẻ số (fHR, số nhịp, đèn tin cậy, thời gian) -- cắt gọn
  05_a02_den_do.png     a02 (CinC 2013, zero-shot): đèn ĐỎ vì bám nhịp mẹ -- thẻ số + tab fHR
  06_a02_tin_hieu.png   a02: tab tín hiệu (toàn trang)

Cần:  pip install playwright && python -m playwright install chromium
Chạy: python demo/screenshot.py          (server tạm ở cổng 7862, tự tắt khi xong)
"""
import os, sys, time, json, traceback
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
OUT = os.path.join(HERE, 'screenshots'); os.makedirs(OUT, exist_ok=True)
PORT = int(os.environ.get('RELYFETAL_SHOT_PORT', '7862'))
os.environ['RELYFETAL_AUTORUN'] = '1'

from playwright.sync_api import sync_playwright
import app

url = f'http://127.0.0.1:{PORT}/'
log = dict(port=PORT, shots={}, ok=False)


def wait_plot(page, timeout=60_000):
    """đợi plotly vẽ xong (ít nhất một .js-plotly-plot có .main-svg) + 1,5 s cho WebGL."""
    page.wait_for_selector('.js-plotly-plot .main-svg', state='attached', timeout=timeout)
    page.wait_for_timeout(1500)


def cards_text(page):
    return page.locator('.rf-cards').inner_text()


def shot(page, name, full=True, clip_sel=None):
    p = os.path.join(OUT, name)
    if clip_sel:
        page.locator(clip_sel).first.screenshot(path=p)
    else:
        page.screenshot(path=p, full_page=full)
    log['shots'][name] = os.path.getsize(p)
    print(f'  đã chụp {name}  ({os.path.getsize(p)/1024:.0f} KB)')


def run_record(page, name):
    """chọn bản ghi trong dropdown rồi bấm Phân tích; đợi thẻ số đổi."""
    label = next(l for l, n in app.REC_LABELS.items() if n == name)
    before = cards_text(page)
    box = page.get_by_role('combobox').nth(0)          # dropdown "Bản ghi mẫu" là combobox đầu tiên (Radio không phải combobox)
    box.click(); box.fill(name); page.wait_for_timeout(400)
    page.get_by_role('option', name=label).first.click()
    page.get_by_role('button', name='Phân tích').click()
    for _ in range(240):                                # tối đa 120 s
        page.wait_for_timeout(500)
        txt = cards_text(page)
        if txt != before and 'Đèn tin cậy' in txt:
            break
    page.wait_for_timeout(1500)
    return cards_text(page)


demo = app.demo
try:
    demo.launch(**app.launch_kwargs(server_port=PORT, prevent_thread_lock=True, quiet=True))
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        page = br.new_page(viewport=dict(width=1500, height=1000), device_scale_factor=1.5)
        t0 = time.perf_counter()
        page.goto(url, wait_until='networkidle', timeout=90_000)
        page.wait_for_selector('.rf-cards', timeout=120_000)       # autorun r01 xong
        wait_plot(page)
        log['first_result_s'] = round(time.perf_counter() - t0, 1)
        txt = cards_text(page); log['r01_cards'] = txt
        print(f'r01 xong sau {log["first_result_s"]} s:', txt.replace('\n', ' | ')[:160])
        assert 'CAO' in txt, 'r01 phải là đèn CAO'
        shot(page, '01_r01_tin_hieu.png')
        shot(page, '04_r01_the_so.png', clip_sel='.rf-cards')
        page.get_by_role('tab', name='Nhịp tim thai theo thời gian').click(); wait_plot(page)
        shot(page, '02_r01_fhr.png')
        page.get_by_role('tab', name='So sánh với nhãn').click(); page.wait_for_timeout(1500)
        shot(page, '03_r01_so_sanh.png')

        # ---- a02: bản ghi zero-shot, mô hình bám nhịp mẹ -> đèn đỏ
        txt = run_record(page, 'a02'); log['a02_cards'] = txt
        print('a02:', txt.replace('\n', ' | ')[:160])
        assert 'THẤP' in txt, 'a02 phải là đèn THẤP'
        page.get_by_role('tab', name='Nhịp tim thai theo thời gian').click(); wait_plot(page)
        shot(page, '05_a02_den_do.png')
        page.get_by_role('tab', name='Tín hiệu (5 tầng)').click(); wait_plot(page)
        shot(page, '06_a02_tin_hieu.png')
        br.close()
    log['ok'] = True
except Exception as e:                                       # noqa: BLE001
    log['error'] = f'{type(e).__name__}: {e}'; print('LỖI:', log['error']); traceback.print_exc(limit=3)
finally:
    try:
        demo.close()
    except Exception:                                        # noqa: BLE001
        pass
    with open(os.path.join(OUT, 'screenshots.json'), 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=1, ensure_ascii=False)
    print('KẾT QUẢ:', 'ĐẠT' if log['ok'] else 'LỖI', '->', OUT)
    sys.exit(0 if log['ok'] else 1)
