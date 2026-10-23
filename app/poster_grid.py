"""Komponen UI grid poster ala Netflix (K41): ukuran tetap 2:3 dan di-crop, gelap + ikon expand saat disorot,
klik untuk membuka detail. Dibuat dengan Streamlit Custom Components v2 karena st.image tidak bisa diklik.
"""

from collections.abc import Callable

import streamlit as st

_CSS = """
.grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0.75rem;
  font-family: var(--st-font, inherit);
}
@media (max-width: 560px) {
  .grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
.card {
  all: unset;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}
.frame {
  position: relative;
  aspect-ratio: 2 / 3;
  border-radius: 0.5rem;
  overflow: hidden;
  background: var(--st-secondary-background-color);
}
.frame img { width: 100%; height: 100%; object-fit: cover; display: block; }
.missing {
  position: absolute; inset: 0; display: grid; place-items: center;
  padding: 0.5rem; text-align: center; font-size: 0.75rem;
  color: var(--st-text-color); opacity: 0.7;
}
.shade {
  position: absolute; inset: 0; display: grid; place-items: center;
  background: rgba(0, 0, 0, 0);
  transition: background 0.15s ease;
}
.shade svg {
  width: 2.2rem; height: 2.2rem; padding: 0.5rem; box-sizing: border-box;
  border-radius: 999px; background: rgba(0, 0, 0, 0.6); color: #fff;
  opacity: 0; transform: scale(0.85);
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.card:hover .shade, .card:focus-visible .shade { background: rgba(0, 0, 0, 0.35); }
.card:hover .shade svg, .card:focus-visible .shade svg { opacity: 1; transform: scale(1); }
.card:focus-visible .frame { outline: 2px solid var(--st-primary-color); outline-offset: 2px; }
.title {
  font-size: 0.82rem; font-weight: 600; line-height: 1.25; color: var(--st-text-color);
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  min-height: 2.5em;
}
.meta { font-size: 0.75rem; color: var(--st-text-color); opacity: 0.65; }
@media (prefers-reduced-motion: reduce) {
  .shade, .shade svg { transition: none; }
}
"""

_JS = """
const EXPAND = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
  'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>'

export default function ({ data, parentElement, setTriggerValue }) {
  const grid = parentElement.querySelector(".grid")
  grid.replaceChildren()
  for (const movie of data?.movies ?? []) {
    const card = document.createElement("button")
    card.type = "button"
    card.className = "card"
    card.setAttribute("aria-label", `Buka detail ${movie.title}`)

    const frame = document.createElement("div")
    frame.className = "frame"
    if (movie.poster) {
      const img = document.createElement("img")
      img.src = movie.poster
      img.alt = ""
      frame.append(img)
    } else {
      const missing = document.createElement("span")
      missing.className = "missing"
      missing.textContent = "🎞️ Poster tidak tersedia"
      frame.append(missing)
    }
    const shade = document.createElement("span")
    shade.className = "shade"
    shade.innerHTML = EXPAND
    frame.append(shade)

    const title = document.createElement("span")
    title.className = "title"
    title.textContent = movie.title
    const meta = document.createElement("span")
    meta.className = "meta"
    meta.textContent = `${movie.year} · ★ ${movie.rating}`

    card.append(frame, title, meta)
    card.onclick = () => setTriggerValue("opened", movie.id)
    grid.append(card)
  }
}
"""

_POSTER_GRID = st.components.v2.component(
    "poster_grid", html='<div class="grid"></div>', css=_CSS, js=_JS,
)


def poster_grid(movies: list[dict], *, key: str, on_open: Callable[[], None]) -> int | None:
    """Tampilkan grid poster. Kembalikan id film yang baru diklik (hanya pada rerun itu), selain itu None.

    movies: [{"id", "title", "year", "rating", "poster" (None kalau poster tidak tersedia)}]
    """
    return _POSTER_GRID(data={"movies": movies}, key=key, on_opened_change=on_open).opened
