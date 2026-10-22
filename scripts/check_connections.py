"""Cek koneksi ke OpenRouter (embedding), Qdrant Cloud, dan Langfuse sebelum ingest.

Jalankan: python scripts/check_connections.py
Script ini tidak pernah mencetak isi API key.
"""

import math
import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langfuse import get_client
from qdrant_client import QdrantClient

load_dotenv()

REQUIRED = [
    "OPENROUTER_API_KEY", "EMBEDDING_MODEL",
    "QDRANT_URL", "QDRANT_API_KEY",
    "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST",
]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def check_env():
    missing = [name for name in REQUIRED if not os.getenv(name)]
    if missing:
        raise SystemExit(f"Variabel kosong di .env: {', '.join(missing)}")
    print("[OK] .env lengkap")


def check_embedding():
    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL"),
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        check_embedding_ctx_length=False,  # kirim teks apa adanya, bukan token ID
    )
    query = "a thief who enters people's dreams"
    overviews = {
        # Overview asli dari imdb_top_1000.csv
        "Inception": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "Interstellar": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
        "The Prestige": "After a tragic accident, two stage magicians engage in a battle to create the ultimate illusion while sacrificing everything they have to outwit each other.",
    }
    query_vec = embeddings.embed_query(query)
    doc_vecs = embeddings.embed_documents(list(overviews.values()))
    print(f"[OK] Embedding: {len(query_vec)} dimensi")
    scores = {title: cosine(query_vec, vec) for title, vec in zip(overviews, doc_vecs)}
    for title, score in sorted(scores.items(), key=lambda kv: -kv[1]):
        print(f"     cosine('{query}', {title}) = {score:.3f}")
    best = max(scores, key=scores.get)
    print(f"[{'OK' if best == 'Inception' else 'CEK'}] Paling mirip: {best}")


def check_qdrant():
    client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
    names = [c.name for c in client.get_collections().collections]
    print(f"[OK] Qdrant terhubung, collection yang ada: {names or 'belum ada'}")


def check_langfuse():
    if get_client().auth_check():
        print(f"[OK] Langfuse terhubung ({os.getenv('LANGFUSE_HOST')})")
    else:
        print("[GAGAL] Langfuse: cek public key, secret key, dan host")


if __name__ == "__main__":
    check_env()
    for check in (check_embedding, check_qdrant, check_langfuse):
        try:
            check()
        except Exception as e:
            print(f"[GAGAL] {check.__name__}: {type(e).__name__}: {e}")
