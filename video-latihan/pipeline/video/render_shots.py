"""Placeholder untuk screenshot Langfuse dan Qdrant (1792x952) sampai screenshot asli dari Claude in Chrome tersedia.
Gambar asli ditaruh di video/shots-real/<nama>.png dan otomatis dipakai assemble.py."""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
OUT = HERE / "shots"
OUT.mkdir(exist_ok=True)

SHOTS = {
    "langfuse-01-sessions": ("Langfuse · Tracing → Sessions", [
        "Satu percakapan di app = satu session; satu pertanyaan = satu trace",
        "Session paling atas = demo barusan (3 trace)",
        "Kolom: traces, durasi, token, biaya"]),
    "langfuse-02-trace-tree": ("Langfuse · trace “film christoper nolan” · tab Tree", [
        "supervisor → transfer_to_data_agent → data_agent → rank_movies → supervisor",
        "rank_movies · Input: director=\"Christopher Nolan\" · Output: matching_count 8, average_rating 8.46",
        "Tag: prompt-v8, supervisor-v1 · latensi, token, biaya di header"]),
    "langfuse-03-scores": ("Langfuse · Scores", [
        "user_feedback = 1 dari 👍 di demo, menempel di trace yang sama",
        "Filter user_feedback = 0 → jawaban yang perlu diperiksa → buka trace-nya"]),
    "langfuse-04-prompt-supervisor": ("Langfuse · Prompts → movie-supervisor-system v1", [
        "Aturan routing: kapan ke rag_agent, kapan ke data_agent, kapan menjawab sendiri",
        "Label production · tidak ada prompt di kode"]),
    "langfuse-05-prompt-agent": ("Langfuse · Prompts → movie-agent-system v1–v9", [
        "production = v8 · staging = v9",
        "Nama dari masa agent tunggal; riwayat v1–v8 utuh",
        "v9: set uji 15/17 (Miyazaki dihitung 4, benar 3) → production tetap v8, tanpa deploy ulang"]),
    "qdrant-01-collection": ("Qdrant Cloud · Collections → imdb_movies", [
        "points: 1.000 · vector size: 1536 · distance: Cosine",
        "Key read-only untuk penilai dikirim lewat Google Form"]),
    "qdrant-02-payload-index": ("Qdrant Cloud · imdb_movies → payload schema", [
        "metadata.genres · keyword", "metadata.year · integer",
        "dibuat scripts/ingest.py → create_payload_indexes"]),
    "qdrant-03-point-inception": ("Qdrant Cloud · point id 8 (Inception)", [
        "page_content: “Inception. Action, Adventure, Sci-Fi. A thief who steals corporate secrets…”",
        "metadata: title, year, genres, rating, director, stars, poster, …"]),
}

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
html,body{margin:0;width:1792px;height:952px;overflow:hidden;background:#161513;color:#EDEAE4;font-family:'IBM Plex Sans',Segoe UI,sans-serif}
.wrap{padding:72px 96px;display:flex;flex-direction:column;gap:28px;height:952px;box-sizing:border-box}
.tag{font-family:'IBM Plex Mono',monospace;font-size:22px;color:#F2531B;letter-spacing:.04em;text-transform:uppercase}
h1{margin:0;font-size:52px;font-weight:600;line-height:1.15}
ul{margin:12px 0 0;padding-left:28px;font-size:30px;line-height:1.45;color:#CFC9C0;display:flex;flex-direction:column;gap:14px}
.note{margin-top:auto;font-family:'IBM Plex Mono',monospace;font-size:22px;color:#9A948B;border-top:1px solid #2E2B28;padding-top:20px}
</style></head><body><div class="wrap"><div class="tag">Screenshot menyusul · diambil dengan Claude in Chrome</div><h1>%s</h1><ul>%s</ul>
<div class="note">Di video asli: rekaman layar %s, rangka lebar (1792×952), wajah kecil di pojok kanan bawah.</div></div></body></html>"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, **({"channel": "msedge"} if sys.platform == "win32" else {}))
    page = browser.new_page(viewport={"width": 1792, "height": 952})
    for name, (title, items) in SHOTS.items():
        tool = "Langfuse" if name.startswith("langfuse") else "dashboard Qdrant Cloud"
        tmp = OUT / f"{name}.html"
        tmp.write_text(PAGE % (title, "".join(f"<li>{i}</li>" for i in items), tool), encoding="utf-8")
        page.goto(tmp.resolve().as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUT / f"{name}.png"))
        tmp.unlink()
        print("ok", name)
    browser.close()
