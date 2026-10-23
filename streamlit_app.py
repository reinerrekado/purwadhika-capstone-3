"""Antarmuka chat. File ini hanya mengurus tampilan; logika agent ada di app/agent.py."""

import json
from uuid import uuid4

import streamlit as st

from app.agent import run_agent

st.set_page_config(page_title="Asisten Film IMDB", page_icon="🎬")
st.title("🎬 Asisten Film IMDB")
st.caption("Ceritakan film yang ingin Anda tonton. Sumber: 1.000 film terbaik IMDB (1920–2020).")

st.session_state.setdefault("chat", [])  # [{"role", "content", "details"}]
st.session_state.setdefault("session_id", uuid4().hex)  # satu percakapan = satu session Langfuse


def summarize_run(new_messages: list) -> dict:
    """Ambil tool call dan pemakaian token dari pesan-pesan baru satu run agent."""
    ai_messages = [m for m in new_messages if m.type == "ai"]
    tool_results = {m.tool_call_id: json.loads(m.content) for m in new_messages if m.type == "tool"}
    return {
        "tool_calls": [
            {"name": call["name"], "args": call["args"],
             "titles": [movie["title"] for movie in tool_results.get(call["id"], [])]}
            for m in ai_messages for call in m.tool_calls
        ],
        "input_tokens": sum((m.usage_metadata or {}).get("input_tokens", 0) for m in ai_messages),
        "output_tokens": sum((m.usage_metadata or {}).get("output_tokens", 0) for m in ai_messages),
    }


def show_details(details: dict) -> None:
    """Tampilkan tool call (dalam expander) dan usage di bawah jawaban."""
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
        details = summarize_run(new_messages)
        st.markdown(answer)
        show_details(details)
    st.session_state.chat.append({"role": "assistant", "content": answer, "details": details})
