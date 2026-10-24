"""Reranker (K58): mengurutkan ulang kandidat dari Qdrant dengan model rerank lewat OpenRouter."""

import os

import httpx

from app.config import OPENROUTER_BASE_URL, env

# Model rerank lain (Cohere, Voyage) ditolak akun karena setelan Zero Data Retention; Qwen3 lolos (K58).
RERANK_MODEL = os.getenv("RERANK_MODEL", "qwen/qwen3-reranker-8b")


def rerank(query: str, documents: list[str], top_n: int) -> list[tuple[int, float]] | None:
    """Urutan dokumen paling relevan: [(indeks di `documents`, skor 0-1)], terbaik dulu.

    None kalau reranker gagal (jaringan, kuota, dan sebagainya), supaya pemanggil memakai urutan vektor
    dan pencarian tidak pernah mati hanya karena fitur tambahan ini.
    """
    try:
        response = httpx.post(
            f"{OPENROUTER_BASE_URL}/rerank", timeout=20,
            headers={"Authorization": f"Bearer {env('OPENROUTER_API_KEY')}"},
            json={"model": RERANK_MODEL, "query": query, "documents": documents, "top_n": top_n},
        )
        response.raise_for_status()
        return [(item["index"], item["relevance_score"]) for item in response.json()["results"]]
    except (httpx.HTTPError, KeyError, ValueError):
        return None
