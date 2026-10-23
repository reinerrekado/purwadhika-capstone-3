"""Tools yang bisa dipanggil agent.

Docstring setiap tool dikirim ke LLM sebagai deskripsi tool, jadi ditulis dalam bahasa Inggris
(bahasa yang sama dengan data dan query pencarian, K12).
"""

import json
from functools import lru_cache
from typing import Literal

from langchain.tools import tool
from langchain_qdrant import QdrantVectorStore
from qdrant_client import models

from app.config import env, get_embeddings
from app.data import all_genres

# 21 genre persis dari dataset. LLM hanya bisa memilih salah satu nilai ini (kritik diri #3).
Genre = Literal[tuple(all_genres())]

# Kolom yang dikirim ke LLM. Poster tidak ikut: UI mengambilnya sendiri lewat id (hemat token).
FIELDS_FOR_LLM = ["id", "title", "year", "genres", "rating", "meta_score",
                  "runtime_min", "director", "stars", "overview"]


@lru_cache(maxsize=1)
def _vector_store() -> QdrantVectorStore:
    """Sambung ke collection yang sudah diisi ingest.py (pola Sesi 14). Dibuat saat pertama dipakai."""
    return QdrantVectorStore.from_existing_collection(
        embedding=get_embeddings(),
        collection_name=env("QDRANT_COLLECTION"),
        url=env("QDRANT_URL"),
        api_key=env("QDRANT_API_KEY"),
    )


@tool(parse_docstring=True)
def search_movies(
    query: str,
    genre: Genre | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
) -> str:
    """Find movies by plot, theme, or mood among the IMDB top 1,000 movies (semantic search).

    Use this when the user describes what they want to watch instead of naming a title.

    Args:
        query: Short description of the wanted plot or mood, written in English.
        genre: Only return movies that have this genre. Leave empty unless the user names a genre.
        year_from: Earliest release year, inclusive. Leave empty unless the user names a year or decade.
        year_to: Latest release year, inclusive. Leave empty unless the user names a year or decade.
    """
    conditions = []
    if genre:
        conditions.append(models.FieldCondition(key="metadata.genres", match=models.MatchValue(value=genre)))
    if year_from or year_to:
        conditions.append(models.FieldCondition(key="metadata.year",
                                                range=models.Range(gte=year_from, lte=year_to)))

    docs = _vector_store().similarity_search(
        query, k=5, filter=models.Filter(must=conditions) if conditions else None,
    )
    movies = [{field: doc.metadata[field] for field in FIELDS_FOR_LLM} for doc in docs]
    return json.dumps(movies, ensure_ascii=False)


TOOLS = [search_movies]
