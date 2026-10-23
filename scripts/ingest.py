"""Fase offline: 1.000 film -> Document -> embedding -> Qdrant Cloud.

Dijalankan sekali dari folder root project:  python -m scripts.ingest
Aman dijalankan ulang: collection dibuat ulang dari nol (force_recreate).
"""

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models

from app.config import env, get_embeddings
from app.data import load_movies, to_records


def build_documents() -> tuple[list[Document], list[int]]:
    """1 film = 1 Document. page_content di-embed; metadata disimpan sebagai payload."""
    documents, ids = [], []
    for movie in to_records(load_movies()):
        text = f"{movie['title']}. {', '.join(movie['genres'])}. {movie['overview']}"  # K13
        documents.append(Document(page_content=text, metadata=movie))
        ids.append(movie["id"])  # id = nomor baris, jadi ingest ulang menimpa, bukan menggandakan
    return documents, ids


def create_payload_indexes(client: QdrantClient, collection: str) -> None:
    """Index untuk kolom yang difilter di search_movies, supaya filter tidak memindai semua point."""
    client.create_payload_index(collection, "metadata.genres", models.PayloadSchemaType.KEYWORD)
    client.create_payload_index(collection, "metadata.year", models.PayloadSchemaType.INTEGER)


def main() -> None:
    collection = env("QDRANT_COLLECTION")
    url, api_key = env("QDRANT_URL"), env("QDRANT_API_KEY")

    documents, ids = build_documents()
    print(f"Menyiapkan {len(documents)} film. Contoh page_content:\n  {documents[8].page_content}")

    # Pola Sesi 12 Bab 6B: satu panggilan = buat collection + embed + upload
    QdrantVectorStore.from_documents(
        documents,
        get_embeddings(),
        ids=ids,
        url=url,
        api_key=api_key,
        prefer_grpc=True,
        collection_name=collection,
        batch_size=100,
        force_recreate=True,
    )

    client = QdrantClient(url=url, api_key=api_key)
    create_payload_indexes(client, collection)

    info = client.get_collection(collection)
    vectors = info.config.params.vectors
    vectors = vectors[""] if isinstance(vectors, dict) else vectors  # LangChain memakai vektor bernama ""
    print(f"Selesai: collection '{collection}' berisi {info.points_count} point, "
          f"{vectors.size} dimensi, jarak {vectors.distance}.")


if __name__ == "__main__":
    main()
