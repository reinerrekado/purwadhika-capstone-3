"""Antarmuka chat. File ini hanya mengurus tampilan; logika agent ada di app/agent.py."""

import json
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


def mentioned_ids(found: dict[str, int], answer: str) -> list[int]:
    """Id film yang judulnya disebut di jawaban, dengan urutan hasil tool (peringkat/relevansi).

    Judul terpanjang dicocokkan dulu lalu dihapus dari teks, supaya "Star Wars" tidak ikut
    cocok di dalam "Star Wars: Episode V - The Empire Strikes Back".
    """
    mentioned = set()
    for title in sorted(found, key=len, reverse=True):
        if title in answer:
            mentioned.add(title)
            answer = answer.replace(title, "")
    return [movie_id for title, movie_id in found.items() if title in mentioned]


def summarize_run(new_messages: list, answer: str) -> dict:
    """Ambil tool call, film yang disebut di jawaban, dan pemakaian token dari satu run agent."""
    ai_messages = [m for m in new_messages if m.type == "ai"]
    movies = {m.tool_call_id: tool_movies(m.content) for m in new_messages if m.type == "tool"}
    found = {movie["title"]: movie["id"] for result in movies.values() for movie in result}
    return {
        "tool_calls": [
            {"name": call["name"], "args": call["args"],
             "titles": [movie["title"] for movie in movies.get(call["id"], [])]}
            for m in ai_messages for call in m.tool_calls
        ],
        "movie_ids": mentioned_ids(found, answer)[:5],
        "input_tokens": sum((m.usage_metadata or {}).get("input_tokens", 0) for m in ai_messages),
        "output_tokens": sum((m.usage_metadata or {}).get("output_tokens", 0) for m in ai_messages),
    }


def show_posters(movie_ids: list[int]) -> None:
    """Kartu poster film yang disebut di jawaban. Poster diambil dari data.py lewat id (K25)."""
    if not movie_ids:
        return
    movies = load_movies().set_index("id")
    for column, movie_id in zip(st.columns(5), movie_ids):
        movie = movies.loc[movie_id]
        column.image(movie["poster"], width="stretch")
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
