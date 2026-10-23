"""Agent ReAct: LLM + tools + system prompt dari Langfuse, dan setiap run di-trace ke Langfuse."""

from functools import lru_cache

from langchain.agents import create_agent
from langfuse import get_client
from langfuse.langchain import CallbackHandler

from app.config import get_llm
from app.tools import TOOLS

PROMPT_NAME = "movie-agent-system"  # dibuat lewat UI Langfuse, label "production" (K03)


@lru_cache(maxsize=1)
def get_agent():
    """Dibuat sekali per proses saat pertama dipakai, bukan setiap kali Streamlit rerun."""
    system_prompt = get_client().get_prompt(PROMPT_NAME).compile()
    return create_agent(model=get_llm(), tools=TOOLS, system_prompt=system_prompt)


def run_agent(messages: list[dict], session_id: str) -> list:
    """Jalankan agent dengan seluruh riwayat sesi (K07). Kembalikan hanya pesan baru dari run ini.

    messages: [{"role": "user" | "assistant", "content": "..."}], pesan terakhir = pertanyaan baru.
    """
    result = get_agent().invoke(
        {"messages": messages},
        config={
            "callbacks": [CallbackHandler()],  # trace ke Langfuse (Sesi 17)
            "metadata": {"langfuse_session_id": session_id},  # satu percakapan = satu session
        },
    )
    return result["messages"][len(messages):]
