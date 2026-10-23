"""Agent ReAct: LLM + tools + system prompt dari Langfuse, dan setiap run di-trace ke Langfuse."""

from collections.abc import Iterator
from functools import lru_cache

from langchain.agents import create_agent
from langfuse import get_client
from langfuse.langchain import CallbackHandler

from app.config import get_llm
from app.tools import TOOLS

PROMPT_NAME = "movie-agent-system"  # dibuat lewat UI Langfuse, label "production" (K03)


@lru_cache(maxsize=4)
def _build_agent(system_prompt: str):
    """Satu agent per teks prompt. Rerun Streamlit memakai agent yang sama selama prompt tidak berubah."""
    return create_agent(model=get_llm(), tools=TOOLS, system_prompt=system_prompt)


def get_agent():
    """Agent + nomor versi prompt. SDK Langfuse menyimpan prompt 60 detik, jadi versi baru terpakai tanpa restart (K35)."""
    prompt = get_client().get_prompt(PROMPT_NAME)
    return _build_agent(prompt.compile()), prompt.version


def stream_agent(messages: list[dict], session_id: str, run: dict) -> Iterator[str]:
    """Jalankan agent dengan seluruh riwayat sesi (K07) dan alirkan teks jawaban potong demi potong.

    messages: [{"role": "user" | "assistant", "content": "..."}], pesan terakhir = pertanyaan baru.
    run: diisi setelah selesai, berisi "messages" (pesan baru dari run ini) dan "trace_id" (untuk feedback).
    """
    agent, prompt_version = get_agent()
    handler = CallbackHandler()  # trace ke Langfuse (Sesi 17)
    config = {"callbacks": [handler], "metadata": {
        "langfuse_session_id": session_id,  # satu percakapan = satu session
        "langfuse_tags": [f"prompt-v{prompt_version}"],  # feedback bisa dibandingkan per versi prompt
    }}
    new_messages = []
    for mode, data in agent.stream({"messages": messages}, config=config, stream_mode=["messages", "updates"]):
        if mode == "messages":  # potongan token dari LLM
            chunk, meta = data
            if meta["langgraph_node"] == "model" and chunk.content:
                yield chunk.content
        else:  # "updates": pesan utuh setiap kali node model/tools selesai
            for update in data.values():
                new_messages += update["messages"]
    run.update(messages=new_messages, trace_id=handler.last_trace_id)


def send_feedback(trace_id: str, thumbs_up: bool) -> None:
    """Simpan 👍/👎 user sebagai score di trace Langfuse (K36)."""
    get_client().create_score(
        trace_id=trace_id, name="user_feedback", value=int(thumbs_up), data_type="BOOLEAN",
        score_id=f"{trace_id}-feedback",  # id tetap: ganti 👍 ke 👎 menimpa score lama, bukan menambah
    )
