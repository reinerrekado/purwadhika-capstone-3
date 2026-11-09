"""Rekam demo app publik (naskah 5a) dengan Edge headless. Aksi mengikuti naskah; tiap langkah ditahan selama narasinya.
Keluaran: demo/demo.webm dan demo/steps.json (detik mulai tiap langkah, relatif ke awal rekaman)."""
import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from segments import S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
OUT = HERE / "demo"
OUT.mkdir(exist_ok=True)
URL = "https://imdb-movie-assistant.streamlit.app/~/+/"
W, H = 1144, 952
DUR_FILE = HERE / "audio" / "durations.json"

for _ in range(240):  # tunggu TTS selesai (durations.json ditulis paling akhir)
    if DUR_FILE.exists():
        break
    time.sleep(5)
durs = json.loads(DUR_FILE.read_text())
NARR = {s["visual"][1]: durs[s["id"]] for s in S if s["visual"][0] == "demo"}
print("durasi narasi per langkah:", {k: round(v, 1) for k, v in NARR.items()}, flush=True)


def wait_idle(page, timeout=150_000):
    page.wait_for_timeout(1200)
    page.wait_for_function("() => !document.querySelector('[data-testid=\"stStatusWidget\"]')", timeout=timeout)
    page.wait_for_timeout(800)


def find_card(page, title):
    """Tombol kartu poster bisa berada di dokumen utama atau di frame komponen."""
    for frame in page.frames:
        loc = frame.locator(f'button[aria-label="Buka detail {title}"]')
        if loc.count():
            return loc.first
    for frame in page.frames:
        loc = frame.locator("button.card")
        if loc.count():
            return loc.last
    return None


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, **({"channel": "msedge"} if sys.platform == "win32" else {}))
    ctx = browser.new_context(viewport={"width": W, "height": H}, color_scheme="dark",
                              record_video_dir=str(OUT), record_video_size={"width": W, "height": H})
    t0 = time.perf_counter()
    page = ctx.new_page()
    steps = {}

    def mark(name):
        steps[name] = round(time.perf_counter() - t0, 3)
        print(f"{steps[name]:7.1f}s  {name}", flush=True)

    def hold(name, extra=0.8):
        """Tahan sampai narasi langkah ini (ditambah jeda kecil) selesai, dihitung dari saat langkah dimulai."""
        remaining = NARR[name] + extra - (time.perf_counter() - t0 - steps[name])
        if remaining > 0:
            page.wait_for_timeout(remaining * 1000)

    def scroll(dy, times, gap_ms):
        page.mouse.move(700, 520)
        for _ in range(times):
            page.mouse.wheel(0, dy)
            page.wait_for_timeout(gap_ms)

    def last_msg():
        return page.locator("[data-testid=stChatMessage]").last

    def ask(text):
        box = page.locator("[data-testid=stChatInputTextArea]")
        box.click()
        box.type(text, delay=45)
        page.wait_for_timeout(400)
        box.press("Enter")
        wait_idle(page)

    page.goto(URL, wait_until="domcontentloaded")
    try:
        page.wait_for_selector("[data-testid=stChatInputTextArea]", timeout=40_000)
    except Exception:
        wake = page.get_by_role("button", name=re.compile("get this app back up", re.I))
        if wake.count():
            print("app tidur, membangunkan...", flush=True)
            wake.first.click()
        page.wait_for_selector("[data-testid=stChatInputTextArea]", timeout=180_000)
    wait_idle(page)
    page.wait_for_function("() => Array.from(document.images).every(i => i.complete)", timeout=30_000)
    page.wait_for_timeout(600)

    mark("beranda")
    hold("beranda")

    mark("q1")
    page.get_by_role("button", name="pencuri yang masuk ke mimpi").click()
    wait_idle(page)
    hold("q1")

    mark("q1-expander")
    exp = last_msg().locator("[data-testid=stExpander]").first
    exp.locator("summary").click()
    page.wait_for_timeout(700)
    scroll(180, 6, 2600)
    hold("q1-expander")

    mark("q2")
    ask("film christoper nolan")
    hold("q2")

    mark("q2-expander")
    exp = last_msg().locator("[data-testid=stExpander]").first
    exp.locator("summary").click()
    page.wait_for_timeout(700)
    scroll(160, 3, 1500)
    hold("q2-expander")

    mark("q2-more")
    more = last_msg().get_by_role("button", name=re.compile(r"^Muat"))
    if more.count():
        more.first.click()
        wait_idle(page)
    thumbs = last_msg().locator("[data-testid=stButtonGroup] button")
    if thumbs.count():
        thumbs.first.scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        thumbs.first.click()
        page.wait_for_timeout(900)
    else:
        print("tombol jempol tidak ditemukan", flush=True)
    hold("q2-more")

    mark("q3")
    ask("yang mana paling lama?")
    hold("q3")

    mark("panel-film")
    card = find_card(page, "Interstellar")
    if card is not None:
        card.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        card.click()
        page.wait_for_selector("[data-testid=stDialog]", timeout=30_000)
        wait_idle(page)
    else:
        print("kartu Interstellar tidak ditemukan", flush=True)
    hold("panel-film")

    mark("panel-orang")
    nolan = page.get_by_role("button", name="Christopher Nolan", exact=True)
    if nolan.count():
        nolan.first.click()
        wait_idle(page)
        page.wait_for_timeout(600)
    else:
        print("tombol Christopher Nolan tidak ditemukan", flush=True)
    hold("panel-orang")

    mark("sidebar")
    page.keyboard.press("Escape")
    page.wait_for_timeout(700)
    page.mouse.move(150, 600)
    hold("sidebar")
    mark("end")

    video = page.video
    ctx.close()
    src = Path(video.path())
    dst = OUT / "demo.webm"
    if dst.exists():
        dst.unlink()
    src.rename(dst)
    browser.close()

(OUT / "steps.json").write_text(json.dumps(steps, indent=1))
print("selesai:", dst, "durasi ±", steps["end"], "dtk")
