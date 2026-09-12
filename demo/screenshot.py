# -*- coding: utf-8 -*-
"""
Chụp màn hình demo bằng playwright (Chromium headless) -> demo/screenshots/*.png
(dùng cho docs/HUONG_DAN_DEMO.md và làm ảnh dự phòng khi demo trực tiếp gặp sự cố).

Theo đúng kịch bản 5 bản minh hoạ (core.DEMO_SHOWCASE):
  01_r01_tong_quan.png       r01: thẻ số + tab "Tín hiệu (5 tầng)"                  (toàn trang)
  02_r01_the_so.png          r01: chỉ 4 thẻ số
  03_r01_so_sanh.png         r01: tab "So sánh với nhãn"
  04_a09_chon_kenh.png       a09: tab "Chọn kênh — cả 4 kênh" (peakprob chọn kênh 1, PSD chọn kênh 2)
  05_a09_the_so.png          a09: thẻ số (đèn xanh, kênh 1)
  06_a09_psd_the_so.png      a09 với quy tắc PSD: thẻ số (đèn đỏ/vàng, F1 thấp) -- để so sánh
  07_B2_03_fhr_den_doan.png  B2_03: tab "Nhịp tim thai + đèn đoạn" (đoạn đỏ tô nền)
  08_B2_03_the_so.png        B2_03: thẻ số (đèn ĐỎ chế độ học)
  09_a02_the_so.png          a02: thẻ số (đèn ĐỎ vì bám nhịp mẹ)
  10_a02_fhr.png             a02: tab fHR (mô hình ~130 bpm bám mẹ)
  11_a27_the_so.png          a27: thẻ số (đèn ĐỎ, không có tín hiệu)
  12_tong_hop.png            tab "Kết quả tổng hợp (60 bản sạch)"

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
log = dict(port=PORT, shots={}, records={}, ok=False)


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


def pick_option(page, combobox_index, typed, option_label):
    box = page.get_by_role('combobox').nth(combobox_index)
    box.click(); box.fill(typed); page.wait_for_timeout(400)
    page.get_by_role('option', name=option_label).first.click()
    page.wait_for_timeout(300)


def run_showcase(page, name, lead_choice=None):
    """chọn bản minh hoạ trong dropdown (combobox 0) [+ kênh (combobox 1)] rồi bấm Phân tích; đợi thẻ số đổi."""
    label = next(l for l, n in app.SHOWCASE_LABELS.items() if n == name)
    before = cards_text(page)
    pick_option(page, 0, name, label)
    if lead_choice is not None:
        pick_option(page, 1, lead_choice.split(' ')[0], lead_choice)
    t0 = time.perf_counter()
    page.get_by_role('button', name='Phân tích').click()
    for _ in range(360):                                # tối đa 180 s
        page.wait_for_timeout(500)
        txt = cards_text(page)
        if txt != before and 'Đèn tin cậy' in txt:
            break
    page.wait_for_timeout(1500)
    txt = cards_text(page)
    log['records'][f'{name}{"" if lead_choice is None else " " + lead_choice}'] = dict(
        wall_s=round(time.perf_counter() - t0, 1), cards=txt.replace('\n', ' | ')[:300])
    return txt


def tab(page, name):
    page.get_by_role('tab', name=name).click(); page.wait_for_timeout(800)


demo = app.demo
try:
    demo.launch(**app.launch_kwargs(server_port=PORT, prevent_thread_lock=True, quiet=True))
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        page = br.new_page(viewport=dict(width=1500, height=1000), device_scale_factor=1.5)
        t0 = time.perf_counter()
        page.goto(url, wait_until='networkidle', timeout=90_000)
        page.wait_for_selector('.rf-cards', timeout=180_000)       # autorun r01 xong
        wait_plot(page)
        log['first_result_s'] = round(time.perf_counter() - t0, 1)
        txt = cards_text(page); log['records']['r01 (autorun)'] = dict(wall_s=log['first_result_s'], cards=txt.replace('\n', ' | ')[:300])
        print(f'r01 xong sau {log["first_result_s"]} s:', txt.replace('\n', ' | ')[:160])
        assert 'CAO' in txt, 'r01 phải là đèn CAO'
        shot(page, '01_r01_tong_quan.png')
        shot(page, '02_r01_the_so.png', clip_sel='.rf-cards')
        tab(page, 'So sánh với nhãn'); page.wait_for_timeout(1000)
        shot(page, '03_r01_so_sanh.png')

        # ---- a09: peakprob cứu được so với PSD
        txt = run_showcase(page, 'a09')
        print('a09:', txt.replace('\n', ' | ')[:160])
        tab(page, 'Chọn kênh — cả 4 kênh'); wait_plot(page)
        shot(page, '04_a09_chon_kenh.png')
        shot(page, '05_a09_the_so.png', clip_sel='.rf-cards')
        txt = run_showcase(page, 'a09', app.LEAD_CHOICES[1])
        print('a09 PSD:', txt.replace('\n', ' | ')[:160])
        shot(page, '06_a09_psd_the_so.png', clip_sel='.rf-cards')
        pick_option(page, 1, 'Tự động — peakprob', app.LEAD_CHOICES[0])

        # ---- B2_03: bản khó, cổng học phải báo đỏ
        txt = run_showcase(page, 'B2_03')
        print('B2_03:', txt.replace('\n', ' | ')[:160])
        tab(page, 'Nhịp tim thai + đèn đoạn'); wait_plot(page)
        shot(page, '07_B2_03_fhr_den_doan.png')
        shot(page, '08_B2_03_the_so.png', clip_sel='.rf-cards')

        # ---- a02: bám nhịp mẹ -> đỏ
        txt = run_showcase(page, 'a02')
        print('a02:', txt.replace('\n', ' | ')[:160])
        assert 'THẤP' in txt, 'a02 phải là đèn THẤP'
        shot(page, '09_a02_the_so.png', clip_sel='.rf-cards')
        tab(page, 'Nhịp tim thai + đèn đoạn'); wait_plot(page)
        shot(page, '10_a02_fhr.png')

        # ---- a27: không có tín hiệu -> đỏ
        txt = run_showcase(page, 'a27')
        print('a27:', txt.replace('\n', ' | ')[:160])
        shot(page, '11_a27_the_so.png', clip_sel='.rf-cards')

        tab(page, 'Kết quả tổng hợp (60 bản sạch)'); page.wait_for_timeout(800)
        shot(page, '12_tong_hop.png')
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
