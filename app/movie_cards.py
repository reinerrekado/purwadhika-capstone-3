"""Komponen UI kartu film ala Netflix (K41, K44, K51): poster ukuran tetap 2:3 dan di-crop, gelap + ikon expand
saat disorot, klik untuk membuka detail. Dibuat dengan Streamlit Custom Components v2 karena st.image tidak bisa
diklik dan tidak bisa diberi efek hover.

Tata letak:
- "list": satu kartu per baris, poster kecil di kiri dan alasan dari jawaban di kanan (di dalam jawaban).
- "grid": deretan poster + judul (film yang disebut di dalam paragraf).
- "wall": dinding poster tanpa teks (tampilan awal).
- "rack": rak tontonan di sidebar, 4 kolom + slot kosong bergaris putus-putus.

Plus `movie_hero`: bagian atas panel detail dengan latar poster yang diburamkan (tanpa interaksi).
"""

from collections.abc import Callable
from typing import Literal

import streamlit as st

_CSS = """
.cards { font-family: var(--st-font, inherit); color: var(--st-text-color); }
.wall { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(7rem, 1fr)); gap: 12px; }  /* lebar minimum: satu kartu tidak lagi menyempit (K64) */
.rack { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; }
.list { display: flex; flex-direction: column; gap: 4px; }
@media (max-width: 560px) {
  .wall { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
.card { all: unset; cursor: pointer; display: flex; min-width: 0; box-sizing: border-box; }
.grid .card, .wall .card, .rack .card { flex-direction: column; gap: 6px; }
.list .card {
  position: relative; overflow: hidden; flex-direction: row; align-items: flex-start; gap: 16px;
  padding: 10px; margin: 0 -10px; border-radius: 8px; transition: background 0.15s ease, color 0.3s ease;
}
.list .card:hover, .list .card:focus-visible { background: var(--st-secondary-background-color); }
.frame {
  position: relative; flex: none; aspect-ratio: 2 / 3; border-radius: 4px; overflow: hidden;
  background: var(--st-secondary-background-color);
}
.list .frame { width: 4.5rem; }
.frame img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.25s ease; }
.frame { transition: box-shadow 0.25s ease; }
.card:hover .frame img, .card:focus-visible .frame img { transform: scale(1.06); }
.card:hover .frame, .card:focus-visible .frame { box-shadow: 0 10px 24px rgba(0, 0, 0, 0.45); }
/* Latar kaca saat disorot (K54): poster kartu itu sendiri, diburamkan, muncul pelan. Latarnya selalu gelap,
   jadi teks berganti terang, di mode gelap maupun terang. */
.glass { position: absolute; inset: -30px; width: calc(100% + 60px); height: calc(100% + 60px);
  object-fit: cover; filter: blur(22px) brightness(0.5) saturate(1.25); pointer-events: none;
  opacity: 0; transition: opacity 0.3s ease; }
.glassy::after { content: ""; position: absolute; inset: 0; border-radius: 8px; pointer-events: none;
  background: rgba(14, 13, 12, 0.32); box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
  opacity: 0; transition: opacity 0.3s ease; }
.glassy:hover .glass, .glassy:focus-visible .glass, .glassy:hover::after, .glassy:focus-visible::after { opacity: 1; }
.list .card.glassy:hover, .list .card.glassy:focus-visible { color: #F4F1EC; }
.glassy > .frame, .glassy > .body { position: relative; z-index: 1; }
.missing {
  position: absolute; inset: 0; display: grid; place-items: center;
  padding: 0.3rem; text-align: center; font-size: 0.7rem; opacity: 0.7;
}
.slot { aspect-ratio: 2 / 3; border-radius: 4px; border: 1px dashed var(--st-border-color); }
.shade {
  position: absolute; inset: 0; display: grid; place-items: center;
  background: rgba(0, 0, 0, 0); transition: background 0.15s ease;
}
.shade svg {
  width: 1.1rem; height: 1.1rem; color: #fff; opacity: 0; transition: opacity 0.15s ease;
}
.card:hover .shade, .card:focus-visible .shade { background: rgba(0, 0, 0, 0.38); }
.card:hover .shade svg, .card:focus-visible .shade svg { opacity: 1; }
.card:focus-visible { outline: 2px solid var(--st-primary-color); outline-offset: 2px; }
.body { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.title { font-weight: 600; line-height: 1.25; }
.grid .title {
  font-size: 0.82rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden; min-height: 2.5em;
}
.list .title { font-size: 1rem; padding-top: 2px; }
.meta { font-family: var(--st-code-font, monospace); font-size: 0.75rem; opacity: 0.65; white-space: nowrap; }
.text { margin-top: 2px; font-size: 0.95rem; line-height: 1.55; opacity: 0.85; }
@media (prefers-reduced-motion: reduce) {
  .card, .shade, .shade svg, .frame, .frame img, .glass, .glassy::after { transition: none; }
  .card:hover .frame img, .card:focus-visible .frame img { transform: none; }
}
"""

_JS = """
const EXPAND = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" ' +
  'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>'

function el(tag, className, text) {
  const node = document.createElement(tag)
  node.className = className
  if (text !== undefined) node.textContent = text
  return node
}

export default function ({ data, parentElement, setTriggerValue }) {
  const layout = data?.layout ?? "grid"
  const root = parentElement.querySelector(".cards")
  root.className = `cards ${layout}`
  root.replaceChildren()
  ;(data?.movies ?? []).forEach((movie) => {
    const glassy = layout === "list" && movie.poster
    const card = el("button", glassy ? "card glassy" : "card")
    card.type = "button"
    if (glassy) {  // latar kaca saat disorot: poster yang sama, diburamkan supaya tidak terlihat pecah
      const glass = el("img", "glass")
      glass.src = movie.poster
      glass.alt = ""
      card.append(glass)
    }
    card.setAttribute("aria-label", `Buka detail ${movie.title}`)

    const frame = el("div", "frame")
    if (movie.poster) {
      const img = el("img", "")
      img.src = movie.poster
      img.alt = ""
      frame.append(img)
    } else {
      frame.append(el("span", "missing", movie.title))
    }
    const shade = el("span", "shade")
    shade.innerHTML = EXPAND
    frame.append(shade)
    card.append(frame)

    if (layout === "list" || layout === "grid") {
      const body = el("div", "body")
      body.append(el("span", "title", movie.title), el("span", "meta", `${movie.year} · ★ ${movie.rating}`))
      if (movie.text) body.append(el("span", "text", movie.text))
      card.append(body)
    }
    card.onclick = () => setTriggerValue("opened", movie.id)
    root.append(card)
  })
  for (let i = 0; i < (data?.empty ?? 0); i++) root.append(el("div", "slot"))
}
"""

_MOVIE_CARDS = st.components.v2.component(
    "movie_cards", html='<div class="cards"></div>', css=_CSS, js=_JS,
)

Layout = Literal["list", "grid", "wall", "rack"]


def movie_cards(movies: list[dict], *, layout: Layout, key: str, on_open: Callable[[], None],
                empty: int = 0) -> int | None:
    """Tampilkan kartu film. Kembalikan id film yang baru diklik (hanya pada rerun itu), selain itu None.

    movies: [{"id", "title", "year", "rating", "poster" (None kalau tidak tersedia), "text" (alasan, opsional)}]
    empty: jumlah slot kosong di akhir (dipakai rak tontonan).
    """
    return _MOVIE_CARDS(data={"layout": layout, "movies": movies, "empty": empty}, key=key,
                        on_opened_change=on_open).opened


_HERO_CSS = """
.hero { position: relative; overflow: hidden; border-radius: 6px; background: #161513; color: #EDEAE4;
  font-family: var(--st-font, inherit); }
.backdrop { position: absolute; inset: -60px; width: calc(100% + 120px); height: calc(100% + 120px);
  object-fit: cover; filter: blur(42px) brightness(0.3) saturate(1.15); }
.content { position: relative; display: flex; gap: 40px; align-items: flex-end; padding: 32px; }
.poster { width: 300px; aspect-ratio: 2 / 3; flex: none; object-fit: cover; border-radius: 4px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.5); }
.info { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
h1 { margin: 0; font-family: "Anton", Impact, sans-serif; font-weight: 400; font-size: 84px; line-height: 0.95;
  letter-spacing: 1px; text-transform: uppercase; overflow-wrap: anywhere; }
.meta { font-size: 16px; color: #CFC9C0; }
.scores { display: flex; gap: 24px; align-items: baseline; font-size: 15px; color: #CFC9C0; }
.scores strong { font-size: 22px; color: #EDEAE4; }
p { margin: 0; max-width: 680px; font-size: 18px; line-height: 1.6; color: #E4DFD7; }
@media (max-width: 640px) {
  .content { flex-direction: column; align-items: flex-start; gap: 18px; padding: 18px; }
  .poster { width: 140px; }
  h1 { font-size: 40px; }
  p { font-size: 15px; }
}
"""

_HERO_JS = """
export default function ({ data, parentElement }) {
  const hero = parentElement.querySelector(".hero")
  const poster = data?.poster
  hero.querySelector(".backdrop").hidden = !poster
  hero.querySelector(".poster").hidden = !poster
  if (poster) {
    hero.querySelector(".backdrop").src = poster
    hero.querySelector(".poster").src = poster
    hero.querySelector(".poster").alt = `Poster ${data.title}`
  }
  hero.querySelector("h1").textContent = data?.title ?? ""
  hero.querySelector(".meta").textContent = data?.meta ?? ""
  hero.querySelector(".imdb").textContent = data?.rating ?? ""
  hero.querySelector(".metascore").textContent = data?.metascore ?? "–"
  hero.querySelector("p").textContent = data?.overview ?? ""
}
"""

_MOVIE_HERO = st.components.v2.component(
    "movie_hero",
    html="""<div class="hero"><img class="backdrop" alt="" aria-hidden="true"><div class="content">
<img class="poster"><div class="info"><h1></h1><div class="meta"></div>
<div class="scores"><span><strong class="imdb"></strong> IMDB</span><span><strong class="metascore"></strong> Metascore</span></div>
<p></p></div></div></div>""",
    css=_HERO_CSS, js=_HERO_JS,
)


def movie_hero(movie: dict, *, key: str) -> None:
    """Bagian atas panel detail. movie: {"title", "meta", "rating", "metascore", "overview", "poster" atau None}."""
    _MOVIE_HERO(data=movie, key=key)
