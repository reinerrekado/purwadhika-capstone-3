"""Tampilan VS Code (editor Monaco, tema Dark Modern) untuk potongan kode repo: baris a-b disorot. PNG 1144x952."""
import html
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from segments import CODE  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
REPO = Path(r"C:\Users\reine\OneDrive\Documents\Work Repository\Capstone Project Purwadhika")
OUT = HERE / "code"
OUT.mkdir(exist_ok=True)
TABS = ["streamlit_app.py", "app/agent.py", "app/tools.py", "app/rerank.py", "app/data.py", "scripts/ingest.py"]
W, H = 1144, 952
CHROME = 35 + 35 + 22 + 22  # title, tab, breadcrumb, status


def key(file, a, b):
    return f"{file.replace('/', '_')}-{a}-{b}"


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<style>
html,body{margin:0;width:%(w)dpx;height:%(h)dpx;overflow:hidden;background:#1F1F1F;font-family:'Segoe UI',system-ui,sans-serif;color:#CCCCCC}
.title{height:35px;background:#181818;border-bottom:1px solid #2B2B2B;display:flex;align-items:center;justify-content:center;font-size:12px;color:#9D9D9D;position:relative}
.title .menu{position:absolute;left:12px;display:flex;gap:14px;font-size:12px;color:#CCCCCC}
.title .menu span:first-child{color:#3B9CFF;font-weight:700}
.tabs{height:35px;background:#181818;display:flex;align-items:stretch;border-bottom:1px solid #2B2B2B}
.tab{padding:0 14px;display:flex;align-items:center;gap:8px;font-size:13px;color:#9D9D9D;border-right:1px solid #2B2B2B;white-space:nowrap}
.tab.active{background:#1F1F1F;color:#FFFFFF;border-top:1px solid #0078D4;margin-bottom:-1px}
.tab i{display:inline-block;width:12px;height:12px;border-radius:2px;background:#3572A5}
.crumbs{height:22px;display:flex;align-items:center;gap:6px;padding:0 16px;font-size:12px;color:#A9A9A9}
.crumbs b{font-weight:400;color:#CCCCCC}
#editor{position:absolute;left:0;top:92px;width:%(w)dpx;height:%(eh)dpx}
.status{position:absolute;left:0;bottom:0;width:%(w)dpx;height:22px;background:#181818;border-top:1px solid #2B2B2B;display:flex;align-items:center;justify-content:space-between;padding:0 12px;font-size:12px;color:#CCCCCC}
.status span{display:flex;gap:16px}
.hl-range{background:rgba(242,83,27,.17)}
.hl-gutter{background:#F2531B;width:3px !important;margin-left:6px}
.monaco-editor .cursors-layer{display:none}
</style></head><body>
<div class="title"><div class="menu"><span style="display:inline-block;width:14px;height:14px;background:#2489DA;border-radius:3px"></span><span>File</span><span>Edit</span><span>Selection</span><span>View</span><span>Go</span><span>Run</span><span>Terminal</span><span>Help</span></div>%(file)s - Capstone Project Purwadhika - Visual Studio Code</div>
<div class="tabs">%(tabs)s</div>
<div class="crumbs">%(crumbs)s</div>
<div id="editor"></div>
<div class="status"><span><span>⎇ main</span><span>⊘ 0 ⚠ 0</span></span><span><span>Ln %(a)d, Col 1</span><span>Spaces: 4</span><span>UTF-8</span><span>LF</span><span>{ } Python</span><span>3.12 ('capstone3': conda)</span></span></div>
<script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs/loader.js"></script>
<script>
require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs' } });
window.__ready = false;
require(['vs/editor/editor.main'], function () {
  monaco.editor.defineTheme('dark-modern', { base: 'vs-dark', inherit: true, rules: [],
    colors: { 'editor.background': '#1F1F1F', 'editorLineNumber.foreground': '#6E7681', 'editorLineNumber.activeForeground': '#CCCCCC',
              'editor.lineHighlightBackground': '#1F1F1F', 'editorGutter.background': '#1F1F1F', 'editor.foreground': '#CCCCCC' } });
  const ed = monaco.editor.create(document.getElementById('editor'), {
    value: %(code)s, language: 'python', theme: 'dark-modern', readOnly: true, fontSize: %(fs)d, lineHeight: %(lh)d,
    fontFamily: "'Cascadia Code', 'Cascadia Mono', Consolas, monospace", fontLigatures: true, wordWrap: 'on', minimap: { enabled: false },
    scrollBeyondLastLine: false, renderLineHighlight: 'none', lineNumbersMinChars: 4, glyphMargin: false, folding: false,
    overviewRulerLanes: 0, hideCursorInOverviewRuler: true, scrollbar: { vertical: 'hidden', horizontal: 'hidden' }, renderWhitespace: 'none',
    guides: { indentation: true }, occurrencesHighlight: 'off', selectionHighlight: false, matchBrackets: 'never' });
  ed.createDecorationsCollection([{ range: new monaco.Range(%(a)d, 1, %(b)d, 1), options: { isWholeLine: true, className: 'hl-range', linesDecorationsClassName: 'hl-gutter' } }]);
  ed.setPosition({ lineNumber: %(a)d, column: 1 });
  const span = %(b)d - %(a)d + 1, visible = Math.floor(%(eh)d / %(lh)d);
  if (span + 4 <= visible) { ed.revealLinesInCenter(%(a)d, %(b)d); } else { ed.setScrollTop(Math.max(0, (%(a)d - 3) * %(lh)d)); }
  setTimeout(() => { window.__ready = true; }, 400);
});
</script></body></html>"""


def render(page, file, a, b, sym):
    text = (REPO / file).read_text(encoding="utf-8")
    eh = H - CHROME
    fs = max(14, min(20, int(eh / ((b - a + 1) + 6) / 1.5)))
    lh = int(fs * 1.5)
    tabs = "".join(f'<div class="tab{" active" if t == file else ""}"><i></i>{t.split("/")[-1]}</div>' for t in TABS)
    crumbs = " › ".join(["Capstone Project Purwadhika", *file.split("/")[:-1], f"<b>{file.split('/')[-1]}</b>", f"<b>{html.escape(sym)}</b>"])
    doc = PAGE % {"w": W, "h": H, "eh": eh, "file": file.split("/")[-1], "tabs": tabs, "crumbs": crumbs, "a": a, "b": b,
                  "code": json.dumps(text), "fs": fs, "lh": lh}
    tmp = OUT / f"{key(file, a, b)}.html"
    tmp.write_text(doc, encoding="utf-8")
    page.goto(tmp.resolve().as_uri())
    page.wait_for_function("() => window.__ready === true", timeout=60_000)
    page.wait_for_timeout(200)
    page.screenshot(path=str(OUT / f"{key(file, a, b)}.png"))
    tmp.unlink()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, **({"channel": "msedge"} if sys.platform == "win32" else {}))
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    done = set()
    for file, a, b, sym, _ in CODE:
        if key(file, a, b) in done:
            continue
        render(page, file, a, b, sym)
        done.add(key(file, a, b))
        print("ok", key(file, a, b))
    browser.close()
print("selesai:", len(done), "gambar kode di", OUT)
