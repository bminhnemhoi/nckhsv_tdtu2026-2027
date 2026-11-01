"""Kiểm tra bố cục: phần tử có vượt khung slide không (dò thật, không dựa vào scrollHeight).

Dùng: python3 qa_layout.py
Cần Google Chrome cục bộ; không cần mạng, không cần package bổ sung.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

MEASURE = """<script>window.addEventListener('load',()=>{document.fonts.ready.then(()=>{
const out=[];document.querySelectorAll('.slide').forEach(sl=>{const sr=sl.getBoundingClientRect();
const limit=sr.top+sl.clientHeight-18;
sl.querySelectorAll('main *, header *, footer *').forEach(e=>{const r=e.getBoundingClientRect();
if(!r.height)return;const txt=(e.textContent||'').trim().slice(0,26);
if(r.bottom>limit+0.5||r.right>sr.right-4||r.left<sr.left+4){
out.push(sl.id+' | '+e.tagName+'.'+e.className+' | bottom='+Math.round(r.bottom)+' limit='+Math.round(limit)+' | '+txt)}})});
const pre=document.createElement('pre');pre.id='meas';pre.textContent=JSON.stringify(out,null,1);document.body.append(pre)})})</script></body>"""


def main() -> int:
    if not Path(CHROME).exists():
        print(f"Không tìm thấy Chrome tại {CHROME}")
        return 2
    page = (HERE / "index.html").read_text(encoding="utf-8")
    page = page.replace('href="slides.css"', f'href="file://{HERE / "slides.css"}"')
    page = page.replace('src="assets/', f'src="file://{HERE / "assets"}/')
    page = page.replace("</body>", MEASURE)
    tmpdir = Path(tempfile.mkdtemp(prefix="relyfetal-layout."))
    target = tmpdir / "index.html"
    target.write_text(page, encoding="utf-8")
    try:
        run = subprocess.run(
            [
                CHROME,
                "--headless",
                "--disable-gpu",
                f"--user-data-dir={tmpdir / 'profile'}",
                "--virtual-time-budget=6000",
                "--dump-dom",
                f"file://{target}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    match = re.search(r'<pre id="meas">(.*?)</pre>', run.stdout, re.DOTALL)
    if not match:
        print("Không đọc được kết quả đo từ Chrome")
        return 2
    issues = json.loads(html.unescape(match.group(1)))
    print(
        json.dumps(issues, ensure_ascii=False, indent=1)
        if issues
        else "OK: không có phần tử tràn khung"
    )
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
