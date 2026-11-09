"""Render slide deck "Rakfilm · Video" jadi PNG 1920x1080, satu gambar per tahap klik (data-build-in)."""
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
SCRATCH = HERE.parent
SLIDES = SCRATCH / "artifact-files" / "8f72fe8e-c7ca-473b-abf2-26d5f0aea6f5" / "project" / "slides"
ASSETS = SCRATCH / "deck-assets"
OUT = HERE / "slides"
OUT.mkdir(exist_ok=True)
TMP = HERE / "slides-html"
TMP.mkdir(exist_ok=True)

BLOBS = {p.stem: p for p in ASSETS.iterdir()}
BLOBS["76b3c22dc21163142f70f7e0e718a8be"] = SCRATCH / "shot-chat-crop.png"  # screenshot slide Solusi

HEAD = """<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
html,body{margin:0;padding:0;width:1920px;height:1080px;overflow:hidden;background:#0E0D0C}
section{position:relative;width:1920px;height:1080px;overflow:hidden}
section,section *{box-sizing:border-box}
h1,h2,h3,p{margin:0}
ul,ol{margin:0;padding-left:1.1em}
li{margin:0}
img{display:block}
table{border-collapse:collapse}
th,td{text-align:left;padding:12px 16px;border-bottom:1px solid #2E2B28;vertical-align:top}
th{font-weight:600}
x-shape{display:block}
x-shape[kind=arrow-right]{clip-path:polygon(0 32%,58% 32%,58% 0,100% 50%,58% 100%,58% 68%,0 68%)}
[data-hide]{visibility:hidden}
aside{display:none}
</style></head><body>
"""
PLANE = ('<svg width="36" height="36" viewBox="0 0 24 24" fill="#9A948B" style="flex:0 0 auto">'
         '<path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg>')


def prepare(html: str) -> tuple[str, int]:
    html = re.sub(r'<x-icon name="PaperPlane"[^>]*></x-icon>', PLANE, html)
    html = re.sub(r"/_blob/([0-9a-f]{32})", lambda m: BLOBS[m.group(1)].resolve().as_uri(), html)
    steps = [int(n) for n in re.findall(r'data-build-in="fade (\d+)"', html)]
    return html, max(steps, default=0)


def state(html: str, k: int) -> str:
    return re.sub(r'data-build-in="fade (\d+)"',
                  lambda m: m.group(0) + (" data-hide" if int(m.group(1)) > k else ""), html)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, **({"channel": "msedge"} if sys.platform == "win32" else {}))
    page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    for file in sorted(SLIDES.glob("*.html")):
        html, max_step = prepare(file.read_text(encoding="utf-8"))
        for k in range(max_step + 1):
            doc = HEAD + state(html, k) + "</body></html>"
            tmp = TMP / f"{file.stem}-{k}.html"
            tmp.write_text(doc, encoding="utf-8")
            page.goto(tmp.resolve().as_uri())
            page.evaluate("document.fonts.ready")
            page.wait_for_function("() => Array.from(document.images).every(i => i.complete)")
            page.wait_for_timeout(250)
            page.screenshot(path=str(OUT / f"{file.stem}-{k}.png"), clip={"x": 0, "y": 0, "width": 1920, "height": 1080})
        print(f"{file.stem}: {max_step + 1} gambar")
    browser.close()
print("selesai:", len(list(OUT.glob('*.png'))), "PNG di", OUT)
