"""Antarmuka chat. File ini hanya mengurus tampilan; logika agent ada di app/agent.py."""

import json
import re
import urllib.parse
import urllib.request
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.agent import send_feedback, stream_agent
from app.data import load_movies
from app.poster_grid import poster_grid

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


def mentioned_ids(movies: list[dict], answer: str) -> list[int]:
    """Id film yang judulnya disebut di jawaban, urut sesuai daftar di jawaban.

    - Judul terpanjang dicocokkan dulu lalu ditutup, supaya "Star Wars" tidak ikut cocok
      di dalam "Star Wars: Episode V - The Empire Strikes Back".
    - Prompt mewajibkan format "Judul (tahun)" (aturan 3). Kalau format itu ada di jawaban, hanya
      judul berformat itu yang dihitung, jadi "Tiga Star Wars terbaik..." tidak ikut.
      Kalau tidak ada sama sekali, dipakai posisi judul biasa.
    - Dikelompokkan per id, bukan per judul: "Drishyam" (2013) dan "Drishyam" (2015) dua film berbeda.
    """
    with_year, plain = {}, {}
    for title in sorted({m["title"] for m in movies}, key=len, reverse=True):
        if title not in answer:
            continue
        for movie in (m for m in movies if m["title"] == title):
            match = re.search(rf"{re.escape(title)}\W{{0,3}}\({movie['year']}\)", answer)  # "Heat" (1995)
            if match:
                with_year[movie["id"]] = match.start()
            plain[movie["id"]] = answer.find(title)
        answer = answer.replace(title, "\0" * len(title))  # panjang tetap, posisi lain tidak bergeser
    positions = with_year or plain
    return sorted(positions, key=positions.get)


def summarize_run(new_messages: list, answer: str) -> dict:
    """Ambil tool call, film yang disebut di jawaban, dan pemakaian token dari satu run agent."""
    ai_messages = [m for m in new_messages if m.type == "ai"]
    movies = {m.tool_call_id: tool_movies(m.content) for m in new_messages if m.type == "tool"}
    found = {movie["id"]: movie for result in movies.values() for movie in result}  # tanpa duplikat
    return {
        "tool_calls": [
            {"name": call["name"], "args": call["args"],
             "titles": [movie["title"] for movie in movies.get(call["id"], [])]}
            for m in ai_messages for call in m.tool_calls
        ],
        "movie_ids": mentioned_ids(list(found.values()), answer)[:5],
        "input_tokens": sum((m.usage_metadata or {}).get("input_tokens", 0) for m in ai_messages),
        "output_tokens": sum((m.usage_metadata or {}).get("output_tokens", 0) for m in ai_messages),
    }


@st.cache_data(ttl=86400, show_spinner=False)
def poster_available(url: str) -> bool:
    """90 dari 1.000 poster sudah dihapus dari server Amazon (404). Dicek sekali per URL, di-cache sehari."""
    try:
        return urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=3).status == 200
    except OSError:  # HTTPError, URLError, dan timeout semuanya turunan OSError
        return False


@st.dialog("Detail film", width="large")
def movie_dialog(movie_id: int) -> None:
    """Panel detail saat poster diklik (K41): info lengkap, tempat menonton, dan cari film yang mirip (K40)."""
    movie = load_movies().set_index("id").loc[movie_id]
    left, right = st.columns([1, 2])
    if poster_available(movie["poster"]):
        left.image(movie["poster"], width="stretch")
    else:
        left.caption("🎞️ Poster tidak tersedia")
    right.subheader(f"{movie['title']} ({movie['year']})")
    certificate, meta_score = ("–" if pd.isna(movie[c]) else movie[c] for c in ("certificate", "meta_score"))
    right.caption(f"{', '.join(movie['genres'])} · {movie['runtime_min']} menit · {certificate}")
    right.markdown(f"⭐ **{movie['rating']}** IMDB · Metascore **{meta_score}**  \n"
                   f"**Sutradara:** {movie['director']}  \n**Pemain:** {', '.join(movie['stars'])}")
    right.write(movie["overview"])
    watch, similar = right.columns(2)
    watch.link_button("📺 Tonton di mana?", width="stretch",
                      url="https://www.justwatch.com/id/search?q=" + urllib.parse.quote(movie["title"]))  # K37
    if similar.button("🔁 Cari yang mirip", width="stretch"):
        st.session_state.pending = f"Film yang mirip {movie['title']}"  # diproses seperti ketikan user
        st.rerun()


def show_posters(movie_ids: list[int], index: int) -> None:
    """Grid poster film yang disebut di jawaban (K41). Poster diambil dari data.py lewat id (K25)."""
    if not movie_ids:
        return
    rows = load_movies().set_index("id").loc[movie_ids]
    cards = [{"id": int(movie_id), "title": row["title"], "year": int(row["year"]), "rating": float(row["rating"]),
              "poster": row["poster"] if poster_available(row["poster"]) else None}  # int/float: harus bisa jadi JSON
             for movie_id, row in rows.iterrows()]
    opened = poster_grid(cards, key=f"posters_{st.session_state.session_id}_{index}", on_open=lambda: None)
    if opened is not None:
        movie_dialog(opened)


def save_feedback(key: str, trace_id: str) -> None:
    """Dipanggil saat 👍/👎 diklik. st.feedback("thumbs") bernilai 1 = 👍, 0 = 👎, None = dibatalkan."""
    if st.session_state[key] is not None:
        send_feedback(trace_id, st.session_state[key] == 1)


def show_details(details: dict, index: int) -> None:
    """Tampilkan poster, tool call (dalam expander), usage, dan tombol feedback di bawah jawaban."""
    show_posters(details.get("movie_ids", []), index)
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
        st.markdown(message["content"])
        if message.get("details"):
            show_details(message["details"], index)

question = st.chat_input("Misalnya: thriller tahun 90-an yang bikin tegang") or st.session_state.pop("pending", None)
if question:
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.chat.append({"role": "user", "content": question})

    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat]
    with st.chat_message("assistant"):
        run = {}  # diisi stream_agent setelah selesai: pesan baru + trace_id
        with st.spinner("Mencari film..."):
            answer = st.write_stream(stream_agent(history, st.session_state.session_id, run))
        details = summarize_run(run["messages"], answer) | {"trace_id": run["trace_id"]}
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
