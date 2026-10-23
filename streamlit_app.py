"""Antarmuka chat. File ini hanya mengurus tampilan; logika agent ada di app/agent.py."""

import json
import re
import urllib.request
from uuid import uuid4

import streamlit as st

from app.agent import run_agent
from app.data import load_movies

st.set_page_config(page_title="Asisten Film IMDB", page_icon="🎬")
st.title("🎬 Asisten Film IMDB")
st.caption("Ceritakan film yang ingin Anda tonton. Sumber: 1.000 film terbaik IMDB (1920–2020).")

st.session_state.setdefault("chat", [])  # [{"role", "content", "details"}]
st.session_state.setdefault("session_id", uuid4().hex)  # satu percakapan = satu session Langfuse


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


def show_posters(movie_ids: list[int]) -> None:
    """Kartu poster film yang disebut di jawaban. Poster diambil dari data.py lewat id (K25)."""
    if not movie_ids:
        return
    movies = load_movies().set_index("id")
    for column, movie_id in zip(st.columns(5), movie_ids):
        movie = movies.loc[movie_id]
        if poster_available(movie["poster"]):
            column.image(movie["poster"], width="stretch")
        else:
            column.container(border=True).caption("🎞️ Poster tidak tersedia")
        column.caption(f"**{movie['title']}** ({movie['year']}) · ⭐ {movie['rating']}")


def show_details(details: dict) -> None:
    """Tampilkan poster, tool call (dalam expander), dan usage di bawah jawaban."""
    show_posters(details.get("movie_ids", []))
    calls = details["tool_calls"]
    with st.expander(f"🔧 {len(calls)} tool call"):
        for call in calls:
            args = ", ".join(f"{k}={v!r}" for k, v in call["args"].items() if v is not None)
            st.code(f"{call['name']}({args})", language="python")
            st.caption("Hasil: " + (", ".join(call["titles"]) or "tidak ada film yang cocok"))
    st.caption(f"Token: {details['input_tokens']:,} input · {details['output_tokens']:,} output")


for message in st.session_state.chat:  # chat history
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("details"):
            show_details(message["details"])

if question := st.chat_input("Misalnya: thriller tahun 90-an yang bikin tegang"):
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.chat.append({"role": "user", "content": question})

    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat]
    with st.chat_message("assistant"):
        with st.spinner("Mencari film..."):
            new_messages = run_agent(history, st.session_state.session_id)
        answer = new_messages[-1].content
        details = summarize_run(new_messages, answer)
        st.markdown(answer)
        show_details(details)
    st.session_state.chat.append({"role": "assistant", "content": answer, "details": details})
