# -*- coding: utf-8 -*-
"""
Chế độ trình bày (T3): khởi động demo thật, đi hết 5 bước với 4 thẻ, ghi thời gian, chụp 6 ảnh
-> demo/screenshots/17..23 + demo/screenshots/screenshots_v2.json.

  17_the_r01.png   sau khi bấm thẻ r01: bước 1 + thanh tóm tắt (toàn trang)
  18_the_a09.png   sau khi bấm thẻ a09
  19_the_a02.png   sau khi bấm thẻ a02
  20_the_a27.png   sau khi bấm thẻ a27
  21_a09_buoc4.png a09 ở bước 4 (chọn dây: hai quy tắc)
  22_a02_buoc5.png a02 ở bước 5 (đèn ĐỎ, bám nhịp mẹ; chi tiết kỹ thuật đóng sẵn)
  23_a02_buoc4.png a02 ở bước 4 (hộp vàng: dây 1 tốt hơn nhưng 6/7 cách chọn mù nhãn chọn dây 2, không cách nào chọn dây 1)

Cần: pip install playwright && python -m playwright install chromium
Chạy: python demo/screenshot_v2.py       (server tạm ở cổng 7863, tự tắt khi xong)
"""
import os, sys, time, json, traceback
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
OUT = os.path.join(HERE, 'screenshots'); os.makedirs(OUT, exist_ok=True)
PORT = int(os.environ.get('RELYFETAL_SHOT_PORT', '7863'))
os.environ['RELYFETAL_AUTORUN'] = '1'

from playwright.sync_api import sync_playwright
import app

url = f'http://127.0.0.1:{PORT}/'
log = dict(port=PORT, shots={}, thoi_gian={}, ok=False)
SHOT = {'r01': '17_the_r01.png', 'a09': '18_the_a09.png', 'a02': '19_the_a02.png', 'a27': '20_the_a27.png'}


def summary_record(page):
    loc = page.locator('.rf-sum-v')
    try:
        return loc.first.inner_text(timeout=1_000).strip() if loc.count() else ''
    except Exception:                                        # noqa: BLE001
        return ''


def active_step(page):
    loc = page.locator('.rf-pg-on .rf-pg-n')
    try:
        return int(loc.first.inner_text(timeout=1_000)) if loc.count() else 0
    except Exception:                                        # noqa: BLE001
        return 0


def wait_until(fn, max_s, dt=0.25):
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < max_s:
        if fn():
            return True
        time.sleep(dt)
    return False


def visible_plot_ready(page):
    """cột bước đang hiện có ít nhất một đồ thị plotly đã vẽ."""
    return page.locator('.js-plotly-plot .main-svg:visible').count() > 0


def shot(page, name, full=True):
    p = os.path.join(OUT, name)
    if full:
        # ảnh toàn trang: thanh tóm tắt dính đáy sẽ bị chụp đè lên hộp chữ -> tạm cho nó nằm yên đúng chỗ
        page.evaluate("() => document.querySelectorAll('.rf-sum-wrap').forEach(e => e.style.setProperty('position', 'static', 'important'))")
    page.screenshot(path=p, full_page=full)
    if full:
        page.evaluate("() => document.querySelectorAll('.rf-sum-wrap').forEach(e => e.style.removeProperty('position'))")
    log['shots'][name] = os.path.getsize(p)
    print(f'  đã chụp {name}  ({os.path.getsize(p) / 1024:.0f} KB)')


def click_card(page, name, max_s=120):
    """Bấm thẻ, đợi thanh tóm tắt đổi sang bản ghi đó VÀ thanh tiến trình về bước 1.
    Nếu đang ở bước 1 với cùng bản ghi (r01 vừa tự chạy), sang bước 2 trước để việc 'về bước 1' quan sát được."""
    before = summary_record(page)
    if active_step(page) == 1:
        page.get_by_role('button', name='Tiếp').click(timeout=30_000)
        wait_until(lambda: active_step(page) == 2, 60)
    t0 = time.perf_counter()
    page.locator(f'#the_{name}').click()
    ok = wait_until(lambda: summary_record(page) == name and active_step(page) == 1, max_s)
    wait_until(lambda: visible_plot_ready(page), 30)
    page.wait_for_timeout(800)
    dt = time.perf_counter() - t0
    assert ok, f'thẻ {name}: thanh tóm tắt không đổi sang {name} sau {max_s} s (trước: {before!r})'
    return dt


def go_next(page, expect_step, max_s=120):
    """Bấm 'Tiếp ▶' rồi đợi thanh tiến trình sang bước mới. Đồ thị WebGL 300 s (r01) qua swiftshader có thể vẽ lâu
    và chặn luồng chính của trang, nên thời hạn đặt rộng; thời gian ghi lại là thời gian THẬT người xem phải chờ."""
    t0 = time.perf_counter()
    page.get_by_role('button', name='Tiếp').click(timeout=max_s * 1000)
    ok = wait_until(lambda: active_step(page) == expect_step, max_s)
    wait_until(lambda: visible_plot_ready(page), 60)
    page.wait_for_timeout(500)
    assert ok, f'không sang được bước {expect_step}'
    return time.perf_counter() - t0


demo = app.demo
try:
    demo.launch(**app.launch_kwargs(server_port=PORT, prevent_thread_lock=True, quiet=True))
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        page = br.new_page(viewport=dict(width=1366, height=768), device_scale_factor=1.5)
        t0 = time.perf_counter()
        # không đợi 'networkidle': Gradio giữ kết nối SSE khi hàng đợi chạy autorun r01 -> không bao giờ "idle"
        page.goto(url, wait_until='load', timeout=90_000)
        wait_until(lambda: summary_record(page) == 'r01', 180)      # autorun r01
        wait_until(lambda: visible_plot_ready(page), 30)
        log['mo_trang_toi_r01_s'] = round(time.perf_counter() - t0, 1)
        print(f'mở trang -> r01 sẵn sau {log["mo_trang_toi_r01_s"]} s')
        # kiểm chế độ chuyên gia mặc định TẮT: không thấy tab nào
        log['tab_hien_luc_mo'] = page.get_by_role('tab').filter(visible=True).count() if hasattr(page.get_by_role('tab'), 'filter') else -1
        for name in ('r01', 'a09', 'a02', 'a27'):
            t_all = time.perf_counter()
            t_card = click_card(page, name)
            shot(page, SHOT[name])
            steps = {}
            for s in range(2, 6):
                steps[s] = round(go_next(page, s), 2)
                if name == 'a09' and s == 4:
                    shot(page, '21_a09_buoc4.png')
                if name == 'a02' and s == 4:
                    shot(page, '23_a02_buoc4.png')
                if name == 'a02' and s == 5:
                    shot(page, '22_a02_buoc5.png')
            log['thoi_gian'][name] = dict(bam_the_s=round(t_card, 2), buoc=steps,
                                          tong_5_buoc_s=round(time.perf_counter() - t_all, 2),
                                          tom_tat=page.locator('.rf-sum').first.inner_text()[:300].replace('\n', ' | '))
            print(f'{name}: bấm thẻ {t_card:.1f} s, 5 bước tổng {log["thoi_gian"][name]["tong_5_buoc_s"]:.1f} s')
        # chế độ chuyên gia: bật lên phải thấy 8 tab
        page.get_by_text('Chế độ chuyên gia', exact=False).first.click()
        page.wait_for_timeout(1500)
        tabs = page.get_by_role('tab')
        names = [tabs.nth(i).inner_text().strip() for i in range(tabs.count()) if tabs.nth(i).is_visible()]
        log['tab_khi_bat_chuyen_gia'] = names
        print('tab hiện trên thanh khi bật chế độ chuyên gia:', names)
        # Gradio 6 dồn tab không vừa vào nút "…" cuối thanh tab -> mở nút đó để ghi đủ 8 tab
        tran = page.locator('.overflow-menu button')
        if tran.count():
            tran.first.click(); page.wait_for_timeout(800)
            them = [tran.nth(i).inner_text().strip() for i in range(tran.count()) if tran.nth(i).is_visible()]
            log['tab_trong_menu_tran'] = [t for t in them if t]
            print('tab trong nút "…":', log['tab_trong_menu_tran'])
        br.close()
    log['ok'] = True
except Exception as e:                                       # noqa: BLE001
    log['error'] = f'{type(e).__name__}: {e}'; print('LỖI:', log['error']); traceback.print_exc(limit=3)
finally:
    try:
        demo.close()
    except Exception:                                        # noqa: BLE001
        pass
    with open(os.path.join(OUT, 'screenshots_v2.json'), 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=1, ensure_ascii=False)
    print('KẾT QUẢ:', 'ĐẠT' if log['ok'] else 'LỖI', '->', OUT)
    sys.exit(0 if log['ok'] else 1)
