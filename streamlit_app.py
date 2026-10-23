"""Antarmuka chat Rakfilm. File ini hanya mengurus tampilan; logika agent ada di app/agent.py."""

import json
import re
import urllib.parse
import urllib.request
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.agent import send_feedback, stream_agent
from app.data import load_movies, movie_facts
from app.movie_cards import movie_cards, movie_hero
from app.story import MAX_FILMS, THEME_BY_NAME, auto_theme, render_story, story_text, watchlist_movies
from app.tools import PAGE_SIZE, PAGERS

# Harga openai/gpt-4.1-mini di OpenRouter (USD per 1 juta token, Okt 2026). Hanya untuk perkiraan biaya.
PRICE_INPUT, PRICE_OUTPUT = 0.40, 1.60
FX_URL = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=IDR"  # kurs referensi ECB, gratis, tanpa API key
LOGO = "static/rakfilm_mark.png"  # dibuat scripts/make_logo.py (K51)
SUGGESTIONS = {  # contoh pertanyaan di tampilan awal: teks tombol → pertanyaan yang dikirim
    "pencuri yang masuk ke mimpi": "Film tentang pencuri yang masuk ke mimpi orang",
    "horor tahun 80-an": "Film horor terbaik tahun 80-an",
    "mirip Spirited Away": "Film yang mirip Spirited Away",
    "semua film Nolan": "Semua film Christopher Nolan",
}

st.set_page_config(page_title="Rakfilm", page_icon=LOGO)
st.logo(LOGO, size="large")

st.session_state.setdefault("chat", [])  # [{"role", "content", "details"}]
st.session_state.setdefault("session_id", uuid4().hex)  # satu percakapan = satu session Langfuse
st.session_state.setdefault("watchlist", [])  # rak tontonan untuk IG story, maksimal 4, hanya selama sesi browser (K46)


def new_chat() -> None:
    """Kosongkan percakapan dan mulai session Langfuse baru."""
    st.session_state.chat = []
    st.session_state.session_id = uuid4().hex


def suggest(question: str) -> None:
    """Callback contoh pertanyaan di tampilan awal: diproses seperti ketikan user."""
    st.session_state.pending = question


@st.cache_data(ttl=86400, show_spinner=False)
def usd_to_idr() -> tuple[float, str] | None:
    """Kurs USD→IDR dan tanggalnya, diambil sekali sehari (K39). None kalau sumber kurs sedang tidak bisa diakses."""
    try:
        request = urllib.request.Request(FX_URL, headers={"User-Agent": "imdb-movie-assistant"})  # tanpa UA: 403
        with urllib.request.urlopen(request, timeout=3) as response:
            data = json.load(response)
        return data["rates"]["IDR"], data["date"]
    except (OSError, ValueError, KeyError):
        return None


def cost_usd(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens * PRICE_INPUT + output_tokens * PRICE_OUTPUT) / 1e6


def rupiah(usd: float) -> str:
    """$0.0023 → "Rp42" (pemisah ribuan titik). Kosong kalau kurs tidak tersedia."""
    fx = usd_to_idr()
    return f"Rp{usd * fx[0]:,.0f}".replace(",", ".") if fx else ""


def tool_movies(content: str) -> list[dict]:
    """Daftar film dari hasil tool. Semua tool mengembalikan JSON berkunci "movies" (K28)."""
    try:
        return json.loads(content).get("movies", [])
    except json.JSONDecodeError:  # pesan error tool berupa teks biasa
        return []


def tool_total(content: str) -> int | None:
    """Jumlah total hasil kalau tool menyebutkannya (rank_movies: matching_count)."""
    try:
        return json.loads(content).get("matching_count")
    except json.JSONDecodeError:
        return None


def summarize_run(new_messages: list) -> dict:
    """Ambil tool call, film yang ditemukan tool, dan pemakaian token dari satu run agent."""
    ai_messages = [m for m in new_messages if m.type == "ai"]
    movies = {m.tool_call_id: tool_movies(m.content) for m in new_messages if m.type == "tool"}
    found = {movie["id"]: movie for result in movies.values() for movie in result}  # tanpa duplikat
    totals = {m.tool_call_id: tool_total(m.content) for m in new_messages if m.type == "tool"}
    tool_calls = [{"name": call["name"], "args": call["args"],
                   "titles": [movie["title"] for movie in movies.get(call["id"], [])],
                   "ids": [movie["id"] for movie in movies.get(call["id"], [])],
                   "total": totals.get(call["id"])}
                  for m in ai_messages for call in m.tool_calls]
    # Pencarian terakhir yang masih punya hasil lanjutan bisa diteruskan dengan "Muat lebih banyak" (K45, K47):
    # rank_movies tahu jumlah totalnya (matching_count); search/similar dianggap berlanjut kalau halamannya penuh.
    pageable = [c for c in tool_calls if c["name"] in PAGERS and c["ids"]
                and (c["total"] > len(c["ids"]) if c["total"] is not None else len(c["ids"]) == PAGE_SIZE)]
    return {
        "tool_calls": tool_calls,
        "more": {"tool": pageable[-1]["name"], "args": pageable[-1]["args"], "offset": len(pageable[-1]["ids"]),
                 "queue": pageable[-1]["ids"], "done": False, "total": pageable[-1]["total"]} if pageable else None,
        "found": [{"id": m["id"], "title": m["title"], "year": m["year"]} for m in found.values()],
        "input_tokens": sum((m.usage_metadata or {}).get("input_tokens", 0) for m in ai_messages),
        "output_tokens": sum((m.usage_metadata or {}).get("output_tokens", 0) for m in ai_messages),
    }


def title_pattern(movie: dict) -> str:
    """Regex "Judul (tahun)" sesuai aturan 3 prompt. \\W{0,3} mengizinkan tanda kutip atau ** di antaranya."""
    return rf"{re.escape(movie['title'])}\W{{0,3}}\({movie['year']}\)"


def split_answer(answer: str, found: list[dict]) -> tuple[list[tuple[str, object]], list[int]]:
    """Pecah jawaban menjadi blok teks dan blok kartu film (K44).

    Baris yang DIAWALI "Judul (tahun)" dan hanya menyebut satu film menjadi kartu: poster di kiri,
    sisa barisnya (alasan) di kanan. Baris lain tetap teks, karena memotong judul dari tengah kalimat
    merusak kalimatnya. Film yang disebut di dalam teks dikembalikan untuk grid poster di bawah jawaban.
    Judul terpanjang dicocokkan dulu, supaya "Star Wars" tidak cocok di dalam "Star Wars: Episode V".
    """
    by_length = sorted(found, key=lambda m: len(m["title"]), reverse=True)
    blocks, carded, in_text = [], set(), []
    for line in answer.split("\n"):
        masked, hits = line, []
        for movie in by_length:
            if match := re.search(title_pattern(movie), masked):
                hits.append((movie, match))
                masked = masked[:match.start()] + "\0" * (match.end() - match.start()) + masked[match.end():]
        prefix = re.sub(r"^\s*(\d+[.)]|[-*•])\s*", "", line[:hits[0][1].start()]) if hits else ""
        if len(hits) == 1 and not prefix.strip(" \"'*") and hits[0][0]["id"] not in carded:
            movie, match = hits[0]
            reason = line[match.end():].replace("**", "").strip(" \"'*-–—:·")
            carded.add(movie["id"])
            if blocks and blocks[-1][0] == "cards":
                blocks[-1][1].append((movie["id"], reason))
            else:
                blocks.append(("cards", [(movie["id"], reason)]))
            continue
        in_text += [movie["id"] for movie, _ in sorted(hits, key=lambda hit: hit[1].start())]
        if not line.strip() and blocks and blocks[-1][0] == "cards":
            continue  # baris kosong di antara kartu tidak perlu ditampilkan
        if blocks and blocks[-1][0] == "text":
            blocks[-1] = ("text", blocks[-1][1] + "\n" + line)
        else:
            blocks.append(("text", line))
    leftover = list(dict.fromkeys(i for i in in_text if i not in carded))
    return blocks, leftover


@st.cache_data(ttl=86400, show_spinner=False)
def poster_available(url: str) -> bool:
    """90 dari 1.000 poster sudah dihapus dari server Amazon (404). Dicek sekali per URL, di-cache sehari."""
    try:
        return urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=3).status == 200
    except OSError:  # HTTPError, URLError, dan timeout semuanya turunan OSError
        return False


def card_data(items: list[tuple[int, str]]) -> list[dict]:
    """Data kartu untuk komponen. Poster diambil dari data.py lewat id (K25); int/float supaya bisa jadi JSON."""
    movies = load_movies().set_index("id")
    return [{"id": int(movie_id), "title": movies.loc[movie_id, "title"], "year": int(movies.loc[movie_id, "year"]),
             "rating": f"{movies.loc[movie_id, 'rating']:.1f}", "text": text,  # "8.0", bukan "8"
             "poster": movies.loc[movie_id, "poster"] if poster_available(movies.loc[movie_id, "poster"]) else None}
            for movie_id, text in items]


def ask(question: str) -> None:
    """Titipkan pertanyaan dari panel detail, lalu jalankan ulang app; diproses seperti ketikan user."""
    st.session_state.pending = question
    st.rerun()


@st.dialog("Detail film", width="large")
def movie_dialog(movie_id: int) -> None:
    """Panel detail saat kartu diklik (K41, K43, K51): latar poster buram, info, sutradara/pemain, rak, fakta."""
    movie = load_movies().set_index("id").loc[movie_id]
    certificate, meta_score = ("–" if pd.isna(movie[c]) else movie[c] for c in ("certificate", "meta_score"))
    movie_hero({
        "title": movie["title"], "rating": f"{movie['rating']:.1f}", "metascore": str(meta_score),
        "meta": f"{movie['year']} · {movie['runtime_min']} menit · {certificate} · {', '.join(movie['genres'])}",
        "overview": movie["overview_id"],  # terjemahan offline (K42)
        "poster": movie["poster"] if poster_available(movie["poster"]) else None,
    }, key=f"hero_{movie_id}")

    with st.container(horizontal=True, vertical_alignment="center"):  # klik nama → film lain orang itu (K43)
        st.caption("Sutradara")
        if st.button(movie["director"], key=f"director_{movie_id}"):
            ask(f"Film lain yang disutradarai {movie['director']}")
    with st.container(horizontal=True, vertical_alignment="center"):
        st.caption("Pemain")
        for star in movie["stars"]:
            if st.button(star, key=f"star_{movie_id}_{star}"):
                ask(f"Film lain yang dibintangi {star}")

    watchlist = st.session_state.watchlist
    with st.container(horizontal=True):
        if movie_id in watchlist:
            if st.button("Di rak · hapus"):
                watchlist.remove(movie_id)
                st.rerun()
        elif st.button(f"+ Tambah ke rak ({len(watchlist)}/{MAX_FILMS})", type="primary",
                       disabled=len(watchlist) >= MAX_FILMS):
            watchlist.append(movie_id)
            st.rerun()
        if st.button("Cari yang mirip"):
            ask(f"Film yang mirip {movie['title']}")
        st.link_button("Tonton di mana ↗",
                       url="https://www.justwatch.com/id/search?q=" + urllib.parse.quote(movie["title"]))  # K37

    st.markdown("**Fakta menarik**")
    columns = st.columns(2)
    for n, fact in enumerate(movie_facts(movie_id)):
        columns[n % 2].caption(fact)


def shown_ids(index: int) -> set[int]:
    """Id film yang sudah tampil di jawaban ke-index: kartu, grid, dan hasil "Muat lebih banyak"."""
    message = st.session_state.chat[index]
    blocks, leftover = split_answer(message["content"], message["details"].get("found", []))
    carded = {movie_id for kind, items in blocks if kind == "cards" for movie_id, _ in items}
    return carded | set(leftover) | set(message["details"].get("extra", []))


def load_more(index: int) -> None:
    """Callback "Muat lebih banyak" (K45): tanpa LLM, panggil fungsi pencarian yang sama dengan offset berikutnya.

    Film dari hasil pertama yang belum ditampilkan agent (agent biasanya memilih 2-3 dari 5) keluar lebih dulu.
    """
    details = st.session_state.chat[index]["details"]
    more, shown = details["more"], shown_ids(index)
    queue = [movie_id for movie_id in more["queue"] if movie_id not in shown]
    while len(queue) < PAGE_SIZE and not more["done"]:
        args = more["args"] | ({"limit": PAGE_SIZE} if "limit" in more["args"] else {})  # rank: halaman 5 film
        page = PAGERS[more["tool"]](**args, offset=more["offset"])
        more["offset"] += PAGE_SIZE
        more["done"] = len(page) < PAGE_SIZE  # halaman tidak penuh = hasil sudah habis
        queue += [m["id"] for m in page if m["id"] not in shown and m["id"] not in queue]
    details["extra"] = details.get("extra", []) + queue[:PAGE_SIZE]
    more["queue"] = queue[PAGE_SIZE:]


def show_answer(answer: str, details: dict, index: int) -> None:
    """Jawaban dengan kartu film di tempatnya (K44), grid untuk film di dalam paragraf, lalu "Muat lebih banyak"."""
    blocks, leftover = split_answer(answer, details.get("found", []))
    clicks = []
    for n, (kind, content) in enumerate(blocks):
        if kind == "text":
            st.markdown(content)
        else:
            key = f"cards_{st.session_state.session_id}_{index}_{n}"
            clicks.append(movie_cards(card_data(content), layout="list", key=key, on_open=lambda: None))
    if leftover:
        key = f"grid_{st.session_state.session_id}_{index}"
        clicks.append(movie_cards(card_data([(i, "") for i in leftover[:10]]), layout="grid", key=key,
                                  on_open=lambda: None))
    if extra := details.get("extra"):  # kartu tambahan: sinopsis Indonesia sebagai teks (K42)
        overview = load_movies().set_index("id")["overview_id"]
        key = f"extra_{st.session_state.session_id}_{index}"
        clicks.append(movie_cards(card_data([(i, overview[i]) for i in extra]), layout="list", key=key,
                                  on_open=lambda: None))
    if (more := details.get("more")) and (more["queue"] or not more["done"]):
        # rank_movies tahu jumlah totalnya, jadi labelnya bisa jujur ("Muat 3 film lagi"); pencarian makna tidak.
        shown = {i for kind, items in blocks if kind == "cards" for i, _ in items} | set(leftover) | set(extra or [])
        left = more["total"] - len(shown) if more.get("total") is not None else None
        if left is None or left > 0:
            label = "Muat lebih banyak" if left is None else f"Muat {min(PAGE_SIZE, left)} film lagi"
            st.button(label, key=f"more_{st.session_state.session_id}_{index}",
                      on_click=load_more, args=(index,), type="tertiary")
    if (opened := next((c for c in clicks if c is not None), None)) is not None:
        movie_dialog(opened)


@st.cache_data(show_spinner=False)
def story_png(movie_ids: tuple[int, ...], headline: str, cta: str, theme: str) -> bytes:
    """Gambar story di-cache: ganti headline atau tema lalu kembali lagi tidak menggambar ulang."""
    return render_story(list(movie_ids), headline, cta, theme)


@st.dialog("Bikin IG story", width="large")
def story_dialog() -> None:
    """Pilih headline, lihat pratinjau, unduh PNG 1080x1920 (K46, K48)."""
    ids = tuple(st.session_state.watchlist)
    movies = watchlist_movies(list(ids))
    texts = st.session_state.setdefault("story_texts", {})
    if ids not in texts:  # LLM dipanggil sekali per isi rak
        with st.spinner("Menulis headline..."):
            texts[ids] = story_text(list(ids), st.session_state.session_id)
    text = texts[ids]
    controls, preview = st.columns([1.15, 1], gap="large")
    with controls:
        minutes = sum(m["runtime_min"] for m in movies)
        st.write(f"Dari rak kamu: {', '.join(m['title'] for m in movies)}.")
        st.caption(f"{len(movies)} film · {minutes // 60}j {minutes % 60}m")
        headline = st.radio("Headline", text["headlines"] + ["Tulis sendiri"], key=f"headline_{ids}")
        if headline == "Tulis sendiri":
            headline = st.text_input("Headline kamu", max_chars=40, key=f"own_{ids}") or text["headlines"][0]
        left, right = st.columns(2)
        cta = left.text_input("Ajakan", value=text["cta"], max_chars=30, key=f"cta_{ids}")
        auto = auto_theme(movies).name  # tema otomatis dari genre (K48)
        choices = [f"Otomatis ({auto})"] + list(THEME_BY_NAME)
        theme = right.selectbox("Tema", choices, key=f"theme_{ids}")
        st.caption("Headline ditulis AI dari genre dan durasi film di rak. Tema mengikuti genre yang paling sering "
                   "muncul." if text["source"] == "llm" else "Headline dari aturan cadangan (AI sedang tidak tersedia).")
        png = story_png(ids, headline, cta, auto if theme == choices[0] else theme)
        st.download_button("Unduh PNG", png, file_name="rakfilm-minggu-ini.png", mime="image/png", type="primary")
    preview.image(png, width="stretch")


def save_feedback(key: str, trace_id: str) -> None:
    """Dipanggil saat 👍/👎 diklik. st.feedback("thumbs") bernilai 1 = 👍, 0 = 👎, None = dibatalkan."""
    if st.session_state[key] is not None:
        send_feedback(trace_id, st.session_state[key] == 1)


def show_details(details: dict, index: int) -> None:
    """Tampilkan tool call (dalam expander), usage, dan tombol feedback di bawah jawaban."""
    calls = details["tool_calls"]
    with st.expander(f"{len(calls)} tool call", icon=":material/build:"):
        for call in calls:
            args = ", ".join(f"{k}={v!r}" for k, v in call["args"].items() if v is not None)
            st.code(f"{call['name']}({args})", language="python")
            st.caption("Hasil: " + (", ".join(call["titles"]) or "tidak ada film yang cocok"))
    usd = cost_usd(details["input_tokens"], details["output_tokens"])
    st.caption(f"{details['input_tokens']:,} input · {details['output_tokens']:,} output token · "
               f"≈ {rupiah(usd)} (${usd:.4f})")
    if trace_id := details.get("trace_id"):
        key = f"feedback_{st.session_state.session_id}_{index}"  # unik per percakapan dan per jawaban
        st.feedback("thumbs", key=key, on_change=save_feedback, args=(key, trace_id))


def random_wall(count: int = 10) -> list[int]:
    """Dinding poster tampilan awal: film acak yang posternya masih tersedia, dipilih sekali per sesi."""
    picked = []
    for movie_id, poster in load_movies().sample(frac=1)[["id", "poster"]].itertuples(index=False):
        if poster_available(poster):
            picked.append(int(movie_id))
        if len(picked) == count:
            return picked
    return picked


# ---- Sidebar: wordmark, rak tontonan, ringkasan sesi (K51) ----
with st.sidebar:
    st.markdown('<div style="font-family: Anton, Impact, sans-serif; font-size: 1.6rem; letter-spacing: 1px; '
                'line-height: 1">RAKFILM</div>', unsafe_allow_html=True)
    st.caption("Asisten film · IMDB Top 1000")
    st.button("+ Percakapan baru", on_click=new_chat, type="tertiary")

    watchlist = st.session_state.watchlist
    name, count = st.columns([3, 1], vertical_alignment="bottom")
    name.markdown("**Rak kamu**")
    count.caption(f"{len(watchlist)}/{MAX_FILMS}")
    rack_click = movie_cards(card_data([(i, "") for i in watchlist]), layout="rack", key="rack",
                             on_open=lambda: None, empty=MAX_FILMS - len(watchlist))
    if watchlist:
        story_click = st.button("Bikin IG story", type="primary", width="stretch")
    else:
        story_click = False
        st.caption("Buka detail film lalu tambahkan ke rak. Isi sampai 4 film untuk dijadikan IG story.")
    session_box = st.container()  # diisi di akhir, supaya angkanya sudah termasuk jawaban terbaru

# Kotak chat dipanggil sebelum isi halaman supaya tampilan awal tahu ada pertanyaan baru atau tidak.
question = (st.chat_input("Ceritakan film yang kamu cari…", height=92)
            or st.session_state.pop("pending", None))

# ---- Tampilan awal: hanya saat chat masih kosong (K51) ----
wall_click = None
if not st.session_state.chat and not question:
    st.title("Mau nonton apa?")
    st.write("Ceritakan inti ceritanya atau sebut film yang kamu suka.")
    wall = st.session_state.setdefault("wall", random_wall())
    wall_click = movie_cards(card_data([(i, "") for i in wall]), layout="wall", key="wall", on_open=lambda: None)
    st.caption("Acak dari 1.000 film terbaik IMDB. Klik poster untuk lihat detail.")
    with st.container(horizontal=True, vertical_alignment="center", gap="small"):
        st.caption("Coba:")
        for label, text in SUGGESTIONS.items():
            st.button(label, key=f"try_{label}", type="tertiary", on_click=suggest, args=(text,))

for index, message in enumerate(st.session_state.chat):  # chat history
    with st.chat_message(message["role"], avatar=LOGO if message["role"] == "assistant" else None):
        if message.get("details"):
            show_answer(message["content"], message["details"], index)
            show_details(message["details"], index)
        else:
            st.markdown(message["content"])

if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.chat.append({"role": "user", "content": question})

    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat]
    with st.chat_message("assistant", avatar=LOGO):
        run = {}  # diisi stream_agent setelah selesai: pesan baru + trace_id
        streaming = st.empty()  # teks mengalir dulu, lalu diganti tampilan dengan kartu film
        with streaming.container(), st.spinner("Mencari film..."):
            answer = st.write_stream(stream_agent(history, st.session_state.session_id, run))
        streaming.empty()
        details = summarize_run(run["messages"]) | {"trace_id": run["trace_id"]}
        show_answer(answer, details, len(st.session_state.chat))
        show_details(details, len(st.session_state.chat))
    st.session_state.chat.append({"role": "assistant", "content": answer, "details": details})

# Satu panel per rerun: dari rak di sidebar, dinding poster, atau tombol IG story.
if (opened := rack_click if rack_click is not None else wall_click) is not None:
    movie_dialog(opened)
elif story_click:
    story_dialog()

with session_box:
    runs = [m["details"] for m in st.session_state.chat if m.get("details")]
    tokens = sum(d["input_tokens"] + d["output_tokens"] for d in runs)
    usd = cost_usd(sum(d["input_tokens"] for d in runs), sum(d["output_tokens"] for d in runs))
    st.divider()
    st.caption("Sesi ini")
    st.markdown(f"{len(runs)} pertanyaan · {tokens:,} token  \n{rupiah(usd) or '–'} · ${usd:.4f}".replace(",", "."))
    if fx := usd_to_idr():
        rate = f"{fx[0]:,.0f}".replace(",", ".")
        st.caption(f"Kurs Rp{rate}/USD, ECB {fx[1]}. Harga gpt-4.1-mini: ${PRICE_INPUT:.2f} input / "
                   f"${PRICE_OUTPUT:.2f} output per 1 juta token.")
