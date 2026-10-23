"""Komponen UI kartu film ala Netflix (K41, K44): poster ukuran tetap 2:3 dan di-crop, gelap + ikon expand saat
disorot, klik untuk membuka detail. Dibuat dengan Streamlit Custom Components v2 karena st.image tidak bisa diklik.

Dua tata letak:
- "list": satu kartu per baris, poster kecil di kiri dan alasan dari jawaban di kanan (di dalam jawaban).
- "grid": deretan poster (untuk film yang disebut di dalam paragraf, misalnya perbandingan).
"""

from collections.abc import Callable
from typing import Literal

import streamlit as st

_CSS = """
.cards { font-family: var(--st-font, inherit); color: var(--st-text-color); }
.grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.75rem; }
.list { display: flex; flex-direction: column; gap: 0.5rem; }
@media (max-width: 560px) {
  .grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
.card { all: unset; cursor: pointer; display: flex; min-width: 0; box-sizing: border-box; }
.grid .card { flex-direction: column; gap: 0.3rem; }
.list .card {
  flex-direction: row; align-items: flex-start; gap: 0.9rem;
  padding: 0.5rem; border-radius: 0.6rem; transition: background 0.15s ease;
}
.list .card:hover, .list .card:focus-visible { background: var(--st-secondary-background-color); }
.frame {
  position: relative; flex: none; aspect-ratio: 2 / 3; border-radius: 0.5rem; overflow: hidden;
  background: var(--st-secondary-background-color);
}
.list .frame { width: 4.5rem; }
.frame img { width: 100%; height: 100%; object-fit: cover; display: block; }
.missing {
  position: absolute; inset: 0; display: grid; place-items: center;
  padding: 0.3rem; text-align: center; font-size: 0.7rem; opacity: 0.7;
}
.shade {
  position: absolute; inset: 0; display: grid; place-items: center;
  background: rgba(0, 0, 0, 0); transition: background 0.15s ease;
}
.shade svg {
  width: 2.2rem; height: 2.2rem; padding: 0.5rem; box-sizing: border-box;
  border-radius: 999px; background: rgba(0, 0, 0, 0.6); color: #fff;
  opacity: 0; transform: scale(0.85); transition: opacity 0.15s ease, transform 0.15s ease;
}
.list .shade svg { width: 1.8rem; height: 1.8rem; padding: 0.4rem; }
.card:hover .shade, .card:focus-visible .shade { background: rgba(0, 0, 0, 0.35); }
.card:hover .shade svg, .card:focus-visible .shade svg { opacity: 1; transform: scale(1); }
.card:focus-visible { outline: 2px solid var(--st-primary-color); outline-offset: 2px; }
.body { display: flex; flex-direction: column; gap: 0.2rem; min-width: 0; }
.title { font-weight: 600; line-height: 1.25; }
.grid .title {
  font-size: 0.82rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden; min-height: 2.5em;
}
.list .title { font-size: 1rem; }
.meta { font-size: 0.78rem; opacity: 0.65; }
.text { font-size: 0.95rem; line-height: 1.5; }
@media (prefers-reduced-motion: reduce) {
  .card, .shade, .shade svg { transition: none; }
}
"""

_JS = """
const EXPAND = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
  'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>'

function el(tag, className, text) {
  const node = document.createElement(tag)
  node.className = className
  if (text !== undefined) node.textContent = text
  return node
}

export default function ({ data, parentElement, setTriggerValue }) {
  const root = parentElement.querySelector(".cards")
  root.className = `cards ${data?.layout === "list" ? "list" : "grid"}`
  root.replaceChildren()
  for (const movie of data?.movies ?? []) {
    const card = el("button", "card")
    card.type = "button"
    card.setAttribute("aria-label", `Buka detail ${movie.title}`)

    const frame = el("div", "frame")
    if (movie.poster) {
      const img = el("img", "")
      img.src = movie.poster
      img.alt = ""
      frame.append(img)
    } else {
      frame.append(el("span", "missing", "🎞️ Poster tidak tersedia"))
    }
    const shade = el("span", "shade")
    shade.innerHTML = EXPAND
    frame.append(shade)

    const body = el("div", "body")
    body.append(el("span", "title", movie.title), el("span", "meta", `${movie.year} · ★ ${movie.rating}`))
    if (movie.text) body.append(el("span", "text", movie.text))

    card.append(frame, body)
    card.onclick = () => setTriggerValue("opened", movie.id)
    root.append(card)
  }
}
"""

_MOVIE_CARDS = st.components.v2.component(
    "movie_cards", html='<div class="cards"></div>', css=_CSS, js=_JS,
)


def movie_cards(movies: list[dict], *, layout: Literal["list", "grid"], key: str,
                on_open: Callable[[], None]) -> int | None:
    """Tampilkan kartu film. Kembalikan id film yang baru diklik (hanya pada rerun itu), selain itu None.

    movies: [{"id", "title", "year", "rating", "poster" (None kalau tidak tersedia), "text" (alasan, opsional)}]
    """
    return _MOVIE_CARDS(data={"layout": layout, "movies": movies}, key=key, on_opened_change=on_open).opened
