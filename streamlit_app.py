"""Antarmuka chat. File ini hanya mengurus tampilan; logika agent ada di app/agent.py."""

import json
import re
import urllib.parse
import urllib.request
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.agent import send_feedback, stream_agent
from app.data import load_movies, movie_facts
from app.movie_cards import movie_cards

# Harga openai/gpt-4.1-mini di OpenRouter (USD per 1 juta token, Okt 2026). Hanya untuk perkiraan biaya.
PRICE_INPUT, PRICE_OUTPUT = 0.40, 1.60
FX_URL = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=IDR"  # kurs referensi ECB, gratis, tanpa API key

st.set_page_config(page_title="Asisten Film IMDB", page_icon="🎬")
st.title("🎬 Asisten Film IMDB")
st.caption("Ceritakan film yang ingin Anda tonton. Sumber: 1.000 film terbaik IMDB (1920–2020).")

st.session_state.setdefault("chat", [])  # [{"role", "content", "details"}]
st.session_state.setdefault("session_id", uuid4().hex)  # satu percakapan = satu session Langfuse


def new_chat() -> None:
    """Kosongkan percakapan dan mulai session Langfuse baru."""
    st.session_state.chat = []
    st.session_state.session_id = uuid4().hex


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


with st.sidebar:
    st.button("🗑️ Percakapan baru", on_click=new_chat, width="stretch", type="primary")


def tool_movies(content: str) -> list[dict]:
    """Daftar film dari hasil tool. Semua tool mengembalikan JSON berkunci "movies" (K28)."""
    try:
        return json.loads(content).get("movies", [])
    except json.JSONDecodeError:  # pesan error tool berupa teks biasa
        return []


def summarize_run(new_messages: list) -> dict:
    """Ambil tool call, film yang ditemukan tool, dan pemakaian token dari satu run agent."""
    ai_messages = [m for m in new_messages if m.type == "ai"]
    movies = {m.tool_call_id: tool_movies(m.content) for m in new_messages if m.type == "tool"}
    found = {movie["id"]: movie for result in movies.values() for movie in result}  # tanpa duplikat
    return {
        "tool_calls": [
            {"name": call["name"], "args": call["args"],
             "titles": [movie["title"] for movie in movies.get(call["id"], [])]}
            for m in ai_messages for call in m.tool_calls
        ],
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
    """Panel detail saat kartu diklik (K41, K43): info lengkap, fakta menarik, chip sutradara/pemain."""
    movie = load_movies().set_index("id").loc[movie_id]
    left, right = st.columns([1, 2])
    if poster_available(movie["poster"]):
        left.image(movie["poster"], width="stretch")
    else:
        left.caption("🎞️ Poster tidak tersedia")
    with right:
        st.subheader(f"{movie['title']} ({movie['year']})")
        certificate, meta_score = ("–" if pd.isna(movie[c]) else movie[c] for c in ("certificate", "meta_score"))
        st.caption(f"{', '.join(movie['genres'])} · {movie['runtime_min']} menit · {certificate}")
        st.markdown(f"⭐ **{movie['rating']}** IMDB · Metascore **{meta_score}**")
        st.write(movie["overview_id"])  # terjemahan offline (K42)

        with st.container(horizontal=True):  # chip: klik → cari film lain orang itu (K43)
            if st.button(movie["director"], icon="🎬", type="tertiary"):
                ask(f"Film lain yang disutradarai {movie['director']}")
            for star in movie["stars"]:
                if st.button(star, icon="🎭", type="tertiary"):
                    ask(f"Film lain yang dibintangi {star}")

        watch, similar = st.columns(2)
        watch.link_button("📺 Tonton di mana?", width="stretch",
                          url="https://www.justwatch.com/id/search?q=" + urllib.parse.quote(movie["title"]))  # K37
        if similar.button("🔁 Cari yang mirip", width="stretch"):
            ask(f"Film yang mirip {movie['title']}")

        st.markdown("**💡 Fakta menarik**\n" + "\n".join(f"- {fact}" for fact in movie_facts(movie_id)))


def show_answer(answer: str, details: dict, index: int) -> None:
    """Jawaban dengan kartu film di tempatnya (K44), lalu grid untuk film yang disebut di dalam paragraf."""
    blocks, leftover = split_answer(answer, details.get("found", []))
    opened = None
    for n, (kind, content) in enumerate(blocks):
        key = f"cards_{st.session_state.session_id}_{index}_{n}"
        if kind == "text":
            st.markdown(content)
        elif (clicked := movie_cards(card_data(content), layout="list", key=key, on_open=lambda: None)) is not None:
            opened = clicked
    if leftover:
        key = f"grid_{st.session_state.session_id}_{index}"
        clicked = movie_cards(card_data([(i, "") for i in leftover[:10]]), layout="grid", key=key, on_open=lambda: None)
        opened = clicked if clicked is not None else opened
    if opened is not None:
        movie_dialog(opened)


def save_feedback(key: str, trace_id: str) -> None:
    """Dipanggil saat 👍/👎 diklik. st.feedback("thumbs") bernilai 1 = 👍, 0 = 👎, None = dibatalkan."""
    if st.session_state[key] is not None:
        send_feedback(trace_id, st.session_state[key] == 1)


def show_details(details: dict, index: int) -> None:
    """Tampilkan tool call (dalam expander), usage, dan tombol feedback di bawah jawaban."""
    calls = details["tool_calls"]
    with st.expander(f"🔧 {len(calls)} tool call"):
        for call in calls:
            args = ", ".join(f"{k}={v!r}" for k, v in call["args"].items() if v is not None)
            st.code(f"{call['name']}({args})", language="python")
            st.caption("Hasil: " + (", ".join(call["titles"]) or "tidak ada film yang cocok"))
    usd = cost_usd(details["input_tokens"], details["output_tokens"])
    st.caption(f"Token: {details['input_tokens']:,} input · {details['output_tokens']:,} output · "
               f"≈ {rupiah(usd)} (${usd:.4f})")
    if trace_id := details.get("trace_id"):
        key = f"feedback_{st.session_state.session_id}_{index}"  # unik per percakapan dan per jawaban
        st.feedback("thumbs", key=key, on_change=save_feedback, args=(key, trace_id))


for index, message in enumerate(st.session_state.chat):  # chat history
    with st.chat_message(message["role"]):
        if message.get("details"):
            show_answer(message["content"], message["details"], index)
            show_details(message["details"], index)
        else:
            st.markdown(message["content"])

question = st.chat_input("Misalnya: thriller tahun 90-an yang bikin tegang") or st.session_state.pop("pending", None)
if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.chat.append({"role": "user", "content": question})

    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat]
    with st.chat_message("assistant"):
        run = {}  # diisi stream_agent setelah selesai: pesan baru + trace_id
        streaming = st.empty()  # teks mengalir dulu, lalu diganti tampilan dengan kartu film
        with streaming.container(), st.spinner("Mencari film..."):
            answer = st.write_stream(stream_agent(history, st.session_state.session_id, run))
        streaming.empty()
        details = summarize_run(run["messages"]) | {"trace_id": run["trace_id"]}
        show_answer(answer, details, len(st.session_state.chat))
        show_details(details, len(st.session_state.chat))
    st.session_state.chat.append({"role": "assistant", "content": answer, "details": details})

with st.sidebar:  # ditulis terakhir supaya angkanya sudah termasuk jawaban yang baru selesai
    runs = [m["details"] for m in st.session_state.chat if m.get("details")]
    tokens_in = sum(d["input_tokens"] for d in runs)
    tokens_out = sum(d["output_tokens"] for d in runs)
    usd = cost_usd(tokens_in, tokens_out)
    st.subheader("Sesi ini")
    st.metric("Pertanyaan", len(runs))
    st.metric("Token", f"{tokens_in + tokens_out:,}", help=f"{tokens_in:,} input · {tokens_out:,} output")
    left, right = st.columns(2)
    left.metric("Biaya (Rp)", rupiah(usd) or "–")
    right.metric("Biaya (USD)", f"${usd:.4f}")
    if fx := usd_to_idr():
        rate = f"{fx[0]:,.0f}".replace(",", ".")
        st.caption(f"Kurs Rp{rate}/USD (ECB, {fx[1]}). Harga gpt-4.1-mini: "
                   f"${PRICE_INPUT:.2f} input / ${PRICE_OUTPUT:.2f} output per 1 juta token.")
