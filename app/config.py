"""Konfigurasi dan klien bersama: membaca .env (lokal) atau Secrets (Streamlit Cloud)."""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def env(name: str) -> str:
    """Ambil variabel lingkungan; berhenti dengan pesan jelas kalau kosong."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variabel {name} kosong. Isi di .env (lokal) atau Secrets (Streamlit Cloud).")
    return value


def get_llm(model: str | None = None) -> ChatOpenAI:
    """LLM lewat OpenRouter dengan ChatOpenAI + base_url (K10). Model diambil dari LLM_MODEL."""
    return ChatOpenAI(
        model=model or env("LLM_MODEL"),
        base_url=OPENROUTER_BASE_URL,
        api_key=env("OPENROUTER_API_KEY"),
    )


def get_embeddings() -> OpenAIEmbeddings:
    """text-embedding-3-small lewat OpenRouter (K11)."""
    return OpenAIEmbeddings(
        model=env("EMBEDDING_MODEL"),
        base_url=OPENROUTER_BASE_URL,
        api_key=env("OPENROUTER_API_KEY"),
        check_embedding_ctx_length=False,  # kirim teks apa adanya, bukan token ID
    )
