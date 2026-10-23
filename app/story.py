"""IG Story "Watchlist minggu ini" (K46): teks dari LLM (cadangan: aturan) dan gambar 1080x1920 gaya Pita Film.

Desain dipilih Reiner dari 3 arah visual di artifact R&D: latar oranye, headline Anton raksasa,
poster di dalam pita film hitam yang dimiringkan, dan watermark sebagai promosi gratis.
"""

import io
import json
import re
import urllib.request
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from langfuse import get_client
from langfuse.langchain import CallbackHandler
from PIL import Image, ImageDraw, ImageFont, ImageOps

from app.config import get_llm
from app.data import load_movies

PROMPT_NAME = "story-headline"  # dibuat sekali di Langfuse, label "production"
MAX_FILMS = 4
FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"  # Anton + IBM Plex Mono (lisensi OFL)
W, H, PAD, TOP = 1080, 1920, 80, 110
PAPER = "#FFF6EC"  # lubang sproket dan teks di dalam pil ajakan
FRAME_W, FRAME_H, FRAME_GAP = 213, 320, 22  # poster 2:3 di dalam pita film


@dataclass(frozen=True)
class Theme:
    """Palet story per genre (K48). Kontras dicek WCAG: teks ≥4,5:1, sorotan headline ≥3:1."""
    name: str
    genres: tuple[str, ...]
    ground: str  # latar
    ink: str  # teks
    accent: str  # baris terakhir headline
    strip: str  # pita film
    swatch: str  # warna genre di tema campur (segmen pita + chip)


# Urutan = prioritas: genre yang lebih spesifik menang (Taegukgi: Action, Drama, War → Perang, bukan Aksi).
THEMES = [
    Theme("Horor", ("Horror",), "#140A0B", "#F2E8E4", "#E8343C", "#3A2426", "#E8343C"),
    Theme("Animasi", ("Animation", "Family"), "#0F6E61", "#F4F9F4", "#FFD84D", "#082F2A", "#3CC9B5"),
    Theme("Musikal", ("Musical", "Music"), "#4B2378", "#F5ECFF", "#FFC94D", "#21102F", "#B07CF0"),
    Theme("Perang", ("War", "History"), "#465020", "#F1E9D2", "#EBC05A", "#1E230C", "#A3B04E"),
    Theme("Komedi", ("Comedy",), "#FFD43B", "#161616", "#1D4ED8", "#161616", "#FFD43B"),
    Theme("Romansa", ("Romance",), "#F7B9C9", "#3A0D1E", "#A3123F", "#3A0D1E", "#F7B9C9"),
    Theme("Sci-Fi", ("Sci-Fi",), "#0A1030", "#E4EEFF", "#3DE0F5", "#26306A", "#3DE0F5"),
    Theme("Noir", ("Thriller", "Crime", "Mystery", "Film-Noir"), "#1C2230", "#E9E7E2", "#F5C518", "#0B0E15", "#F5C518"),
    Theme("Aksi", ("Action", "Adventure", "Western", "Biography", "Sport", "Fantasy"),
          "#F2531B", "#111111", "#FFF6EC", "#111111", "#F2531B"),
    Theme("Drama", ("Drama",), "#2B2540", "#EEE8F7", "#F2A65A", "#14111F", "#F2A65A"),
]
MIXED = Theme("Campur", (), "#121212", "#F2F2F2", "#FF6A3D", "#000000", "#FF6A3D")
THEME_BY_NAME = {theme.name: theme for theme in THEMES + [MIXED]}


def film_theme(movie: dict) -> Theme:
    """Tema satu film: tema berprioritas tertinggi yang genrenya dimiliki film. Drama paling akhir (ada di 72% film)."""
    return next((theme for theme in THEMES if set(theme.genres) & set(movie["genres"])), THEME_BY_NAME["Drama"])


def auto_theme(movies: list[dict]) -> Theme:
    """Tema dominan: tema film yang muncul di ≥2 film (1 film: temanya sendiri) dan tidak seri; selain itu Campur."""
    counts = Counter(film_theme(m).name for m in movies).most_common()
    needed = 1 if len(movies) == 1 else 2
    if counts[0][1] >= needed and (len(counts) == 1 or counts[0][1] > counts[1][1]):
        return THEME_BY_NAME[counts[0][0]]
    return MIXED

# Cadangan kalau LLM gagal: headline per genre dominan.
FALLBACK = {
    "Horror": ["Sabtuku penuh teriakan.", "Lampu mati, nyali diuji."],
    "Thriller": ["Plot twist adalah love language-ku.", "Deg-degan sampai kredit."],
    "Crime": ["Weekend-ku penuh kasus.", "Detektif dadakan malam ini."],
    "Romance": ["Siapin tisu, ini serius.", "Mode galau: ON."],
    "Drama": ["Siapin tisu, ini serius.", "Weekend penuh perasaan."],
    "Animation": ["Inner child-ku butuh ini.", "Kartun dulu, dewasa nanti."],
    "Sci-Fi": ["Otakku siap dibikin muter.", "Weekend di luar angkasa."],
    "Comedy": ["Ketawa dulu, mikir belakangan.", "Receh tapi berkelas."],
    "Action": ["Adrenalin weekend ini penuh.", "Ledakan di setiap jam."],
}


def watchlist_movies(movie_ids: list[int]) -> list[dict]:
    """Data film watchlist sesuai urutan pilihan user."""
    movies = load_movies().set_index("id")
    return [{"id": i, **movies.loc[i, ["title", "year", "genres", "runtime_min", "rating", "poster"]].to_dict()}
            for i in movie_ids]


def stats_line(movies: list[dict]) -> str:
    """"4 FILM · 7J 38M · RATING 8,1", semua dihitung dari data. Tanpa ★: font IBM Plex Mono tidak punya glyph-nya."""
    minutes = sum(m["runtime_min"] for m in movies)
    rating = sum(m["rating"] for m in movies) / len(movies)
    return f"{len(movies)} FILM · {minutes // 60}J {minutes % 60}M · RATING {rating:.1f}".replace(".", ",")


def fallback_text(movies: list[dict]) -> dict:
    """Headline dari aturan: genre yang paling sering muncul di watchlist."""
    genres = Counter(g for m in movies for g in m["genres"])
    dominant = next((g for g, _ in genres.most_common() if g in FALLBACK), None)
    headlines = FALLBACK.get(dominant, []) + ["Mood-ku random, watchlist-ku juga."]
    if sum(m["runtime_min"] for m in movies) >= 420:
        headlines.append("Weekend-ku sudah dipesan.")
    return {"headlines": headlines[:3], "cta": "DM aku buat nobar", "source": "aturan"}


def story_text(movie_ids: list[int], session_id: str) -> dict:
    """3 pilihan headline + 1 ajakan dari LLM (prompt di Langfuse). Gagal atau tidak valid → aturan cadangan."""
    movies = watchlist_movies(movie_ids)
    films = "\n".join(f"- {m['title']} ({m['year']}), {', '.join(m['genres'])}, {m['runtime_min']} min, "
                      f"rating {m['rating']}" for m in movies)
    try:
        prompt = get_client().get_prompt(PROMPT_NAME)
        reply = get_llm().invoke(
            prompt.compile(films=films), response_format={"type": "json_object"},
            config={"callbacks": [CallbackHandler()],
                    "metadata": {"langfuse_session_id": session_id, "langfuse_tags": ["story"]}},
        )
        data = json.loads(reply.content)
        headlines = [re.sub(r"[.!?]+$", lambda end: end.group(0)[0], h.strip())  # "seru!." → "seru!"
                     for h in data["headlines"] if isinstance(h, str) and 0 < len(h.split()) <= 6]
        if len(headlines) >= 2 and isinstance(data.get("cta"), str) and data["cta"].strip():
            return {"headlines": headlines[:3], "cta": data["cta"].strip(), "source": "llm"}
    except Exception:  # noqa: BLE001  (fitur tambahan: apa pun yang gagal, story tetap bisa dibuat)
        pass
    return fallback_text(movies)


@lru_cache(maxsize=8)
def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


@lru_cache(maxsize=64)
def _poster(url: str) -> Image.Image | None:
    """Unduh poster sekali per URL. None kalau poster sudah dihapus dari server (K33)."""
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "imdb-movie-assistant"})
        with urllib.request.urlopen(request, timeout=5) as response:
            return Image.open(io.BytesIO(response.read())).convert("RGB")
    except OSError:
        return None


def _spaced(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font, fill, spacing: int) -> None:
    """Teks dengan jarak antarhuruf (Pillow tidak punya letter-spacing)."""
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += font.getlength(char) + spacing


def _fit_headline(text: str, max_width: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Ukuran huruf terbesar (≤200 px) yang membuat headline muat dalam maksimal 3 baris."""
    words = text.upper().split()
    for size in range(200, 99, -6):
        font, lines = _font("Anton-Regular.ttf", size), [""]
        for word in words:
            candidate = f"{lines[-1]} {word}".strip()
            if font.getlength(candidate) <= max_width:
                lines[-1] = candidate
            else:
                lines.append(word)
        if len(lines) <= 3 and all(font.getlength(line) <= max_width for line in lines):
            return font, lines
    return font, lines


def _clip(text: str, font, max_width: int) -> str:
    """Potong teks dengan "…" kalau terlalu lebar."""
    if font.getlength(text) <= max_width:
        return text
    while text and font.getlength(text + "…") > max_width:
        text = text[:-1]
    return text.rstrip() + "…"


def _film_strip(movies: list[dict], theme: Theme) -> Image.Image:
    """Pita film: dua baris lubang sproket dan poster di tengahnya, lalu dimiringkan 3 derajat.

    Tema Campur: bagian pita di belakang tiap poster berwarna genre film itu ("pita warna-warni").
    """
    strip_w, inner = 1200, 920
    strip_h = 26 + 22 + 22 + FRAME_H + 22 + 22 + 26
    strip = Image.new("RGBA", (strip_w, strip_h), theme.strip)
    draw = ImageDraw.Draw(strip)
    left = (strip_w - inner) // 2
    width = len(movies) * FRAME_W + (len(movies) - 1) * FRAME_GAP
    first_x = left + (inner - width) // 2
    if theme is MIXED:  # segmen warna digambar dulu, supaya lubang sproket tetap di atasnya
        for n, movie in enumerate(movies):
            x = first_x + n * (FRAME_W + FRAME_GAP)
            draw.rectangle((x - 11, 0, x + FRAME_W + 11, strip_h), fill=film_theme(movie).swatch)
    for row_y in (26, strip_h - 26 - 22):  # lubang sproket
        for n in range(16):
            x = left + round(n * (inner - 34) / 15)
            draw.rounded_rectangle((x, row_y, x + 34, row_y + 22), radius=6, fill=PAPER)
    x, y = first_x, 26 + 22 + 22
    mask = Image.new("L", (FRAME_W, FRAME_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, FRAME_W - 1, FRAME_H - 1), radius=6, fill=255)
    for movie in movies:
        image = _poster(movie["poster"])
        if image is None:  # poster hilang: kotak berisi judul
            image = Image.new("RGB", (FRAME_W, FRAME_H), (52, 52, 56))
            ImageDraw.Draw(image).multiline_text((16, 16), "\n".join(movie["title"][i:i + 12]
                                                 for i in range(0, min(len(movie["title"]), 48), 12)),
                                                 font=_font("IBMPlexMono-Bold.ttf", 20), fill=PAPER)
        strip.paste(ImageOps.fit(image, (FRAME_W, FRAME_H)), (x, y), mask)  # crop 2:3, seperti kartu di app
        x += FRAME_W + FRAME_GAP
    return strip.rotate(3, resample=Image.BICUBIC, expand=True)  # CSS rotate(-3deg) = 3 derajat berlawanan jarum jam


def render_story(movie_ids: list[int], headline: str, cta: str, theme_name: str | None = None) -> bytes:
    """Gambar PNG 1080x1920 gaya Pita Film untuk 1–4 film. theme_name None = tema otomatis dari genre (K48)."""
    movies = watchlist_movies(movie_ids)[:MAX_FILMS]
    theme = THEME_BY_NAME.get(theme_name) or auto_theme(movies)
    ink = theme.ink
    canvas = Image.new("RGB", (W, H), theme.ground)
    draw = ImageDraw.Draw(canvas)
    content_w = W - 2 * PAD

    _spaced(draw, (PAD, TOP), "WATCHLIST MINGGU INI", _font("IBMPlexMono-Bold.ttf", 28), ink, 6)

    font, lines = _fit_headline(headline, content_w)
    y = TOP + 28 + 22
    for n, line in enumerate(lines):  # baris terakhir memakai warna sorotan tema, seperti "TERIAKAN." di desain
        draw.text((PAD, y + font.size * 0.85), line, font=font, anchor="ls",
                  fill=theme.accent if n == len(lines) - 1 else ink)
        y += round(font.size * 1.02)  # 0,95 terlalu rapat: koma "SERU," menabrak baris berikutnya

    # Pita film + daftar judul (+ chip genre di tema Campur) ditaruh di tengah ruang antara headline
    # dan baris statistik, supaya tidak ada ruang kosong besar kalau headline hanya 1-2 baris.
    strip = _film_strip(movies, theme)
    chips = list(dict.fromkeys(film_theme(m) for m in movies)) if theme is MIXED else []
    titles_h = ((len(movies) + 1) // 2) * 48 + (64 if chips else 0)
    region_top, region_bottom = y + 70, H - PAD - 110 - 26 - 36 - 70
    strip_top = region_top + max(0, (region_bottom - region_top - (strip.height + 40 + titles_h)) // 2)
    canvas.paste(strip, ((W - strip.width) // 2, strip_top), strip)

    bold, medium = _font("IBMPlexMono-Bold.ttf", 28), _font("IBMPlexMono-Medium.ttf", 28)
    col_w = (content_w - 32) // 2
    y = strip_top + strip.height + 40
    for n, movie in enumerate(movies):
        x = PAD + (n % 2) * (col_w + 32)
        row_y = y + (n // 2) * 48
        year = f" ({movie['year']})"
        title = _clip(f"{n + 1:02d} {movie['title']}", bold, col_w - medium.getlength(year))
        draw.text((x, row_y), title, font=bold, fill=ink)
        draw.text((x + bold.getlength(title), row_y), year, font=medium, fill=ink)

    chip_font, chip_x = _font("IBMPlexMono-Bold.ttf", 22), PAD  # tema Campur: legenda warna genre
    chip_y = y + ((len(movies) + 1) // 2) * 48 + 20
    for chip in chips:
        chip_w = round(chip_font.getlength(chip.name.upper())) + 36
        draw.rounded_rectangle((chip_x, chip_y, chip_x + chip_w, chip_y + 44), radius=22, fill=chip.swatch)
        draw.text((chip_x + 18, chip_y + 22), chip.name.upper(), font=chip_font, fill="#111111", anchor="lm")
        chip_x += chip_w + 12

    pill_font = _font("Anton-Regular.ttf", 58)
    cta_text = _clip(cta.upper(), pill_font, 640)
    pill_w, pill_h = round(pill_font.getlength(cta_text)) + 96, 110
    pill_top = H - PAD - pill_h
    draw.rounded_rectangle((PAD, pill_top, PAD + pill_w, pill_top + pill_h), radius=pill_h // 2, fill=ink)
    draw.text((PAD + 48, pill_top + pill_h // 2), cta_text, font=pill_font, fill=theme.ground, anchor="lm")
    small = _font("IBMPlexMono-Bold.ttf", 20)
    draw.multiline_text((W - PAD, pill_top + pill_h // 2), "dibuat dengan\nAsisten Film IMDB", font=small,
                        fill=ink, anchor="rm", align="right", spacing=8)
    _spaced(draw, (PAD, pill_top - 26 - 36), stats_line(movies), _font("IBMPlexMono-Bold.ttf", 30), ink, 2)

    output = io.BytesIO()
    canvas.save(output, format="PNG", optimize=True)
    return output.getvalue()
