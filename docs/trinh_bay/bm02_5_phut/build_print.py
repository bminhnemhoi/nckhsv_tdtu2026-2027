from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSS = ROOT / "slides.css"
SRC = ROOT / "index.html"


def build(dest: Path) -> Path:
    html = SRC.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    old = '<link rel="stylesheet" href="slides.css">'
    assert old in html, "stylesheet link not found in index.html"
    html = html.replace(old, f"<style>\n{css}\n</style>")
    dest.write_text(html, encoding="utf-8")
    return dest


if __name__ == "__main__":
    print("wrote", build(ROOT / "_print.html"))
