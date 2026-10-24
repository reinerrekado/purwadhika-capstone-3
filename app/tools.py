"""Tools yang bisa dipanggil agent.

Docstring setiap tool dikirim ke LLM sebagai deskripsi tool, jadi ditulis dalam bahasa Inggris
(bahasa yang sama dengan data dan query pencarian, K12).
"""

import difflib
import json
import re
import unicodedata
from functools import lru_cache
from typing import Literal

from langchain.tools import tool
from langchain_qdrant import QdrantVectorStore
from qdrant_client import models

from app.config import env, get_embeddings
from app.data import all_genres, load_movies, to_records
from app.rerank import rerank

# 21 genre persis dari dataset. LLM hanya bisa memilih salah satu nilai ini (kritik diri #3).
Genre = Literal[tuple(all_genres())]

# Kolom yang dikirim ke LLM. Poster tidak ikut: UI mengambilnya sendiri lewat id (hemat token).
FIELDS_FOR_LLM = ["id", "title", "year", "genres", "rating", "meta_score",
                  "runtime_min", "director", "stars", "overview"]
DETAIL_FIELDS = FIELDS_FOR_LLM + ["votes", "gross_usd", "certificate"]
RANK_FIELDS = ["id", "title", "year", "genres", "rating", "meta_score",
               "votes", "gross_usd", "runtime_min", "director"]  # tanpa overview: daftar peringkat (K29)

ROMAN = {"ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6", "vii": "7", "viii": "8", "ix": "9"}
MAX_MATCHES = 10  # cukup untuk satu seri penuh, misalnya 6 film Harry Potter
PAGE_SIZE = 5  # film per pencarian Qdrant (K05): hemat token dan relevansi turun setelah 5 besar
RERANK_CANDIDATES = PAGE_SIZE * 3  # kandidat yang diambil dari Qdrant sebelum reranker memilih PAGE_SIZE terbaik (K58)
NOT_FOUND_HINT = ("Do not tell the user the movie is missing yet. Non-English movies use their original "
                  "title (e.g. Parasite = Gisaengchung), so call the same tool again with the original "
                  "title if you know it. Otherwise try rank_movies with the director or year, or "
                  "search_movies with a short English plot description.")  # K32


@lru_cache(maxsize=1)
def _vector_store() -> QdrantVectorStore:
    """Sambung ke collection yang sudah diisi ingest.py (pola Sesi 14). Dibuat saat pertama dipakai."""
    return QdrantVectorStore.from_existing_collection(
        embedding=get_embeddings(),
        collection_name=env("QDRANT_COLLECTION"),
        url=env("QDRANT_URL"),
        api_key=env("QDRANT_API_KEY"),
    )


def _qdrant_filter(genre: str | None, year_from: int | None, year_to: int | None) -> models.Filter | None:
    """Filter payload Qdrant (K04). Hanya dipasang kalau LLM mengisinya; LangChain menyimpan data di "metadata"."""
    conditions = []
    if genre:
        conditions.append(models.FieldCondition(key="metadata.genres", match=models.MatchValue(value=genre)))
    if year_from or year_to:
        conditions.append(models.FieldCondition(key="metadata.year",
                                                range=models.Range(gte=year_from, lte=year_to)))
    return models.Filter(must=conditions) if conditions else None


@tool(parse_docstring=True)
def search_movies(
    query: str,
    genre: Genre | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
) -> str:
    """Find movies by plot, theme, or mood among the IMDB top 1,000 movies (semantic search).

    Use this only when the user describes a plot, theme, or mood (e.g. "a horror movie about a haunted
    house"). If the user only names a genre, year, or decade (e.g. "recommend me a horror movie"),
    use rank_movies sorted by rating instead. Do not use it to find a movie or a movie series by
    title; use get_movie_details for that.

    Args:
        query: One sentence in English (translate if the user writes in another language) describing the wanted plot or mood with the user's specific details (who, where, what happens).
        genre: Only return movies that have this genre. Leave empty unless the user names a genre.
        year_from: Earliest release year, inclusive. Leave empty unless the user names a year or decade.
        year_to: Latest release year, inclusive. Leave empty unless the user names a year or decade.
    """
    return json.dumps({"movies": search_page(query, genre, year_from, year_to)}, ensure_ascii=False)


def search_page(query: str, genre: str | None = None, year_from: int | None = None, year_to: int | None = None,
                offset: int = 0) -> list[dict]:
    """Satu halaman (5 film) hasil search_movies. offset dipakai tombol "Muat lebih banyak" di UI (K45)."""
    hits = _vector_store().similarity_search_with_score(query, k=RERANK_CANDIDATES, offset=offset,
                                                        filter=_qdrant_filter(genre, year_from, year_to))
    if not hits:
        return []
    # Qdrant mengambil 15 kandidat (cepat, berdasarkan makna), reranker memilih 5 terbaik (K58).
    # Kalau reranker gagal, 5 pertama menurut vektor dipakai. score = kemiripan kosinus, rerank_score = skor reranker (K57).
    ranked = rerank(query, [doc.page_content for doc, _ in hits], PAGE_SIZE) or [(i, None) for i in range(PAGE_SIZE)]
    return [{**{field: hits[i][0].metadata[field] for field in FIELDS_FOR_LLM}, "score": round(hits[i][1], 3),
             "rerank_score": None if relevance is None else round(relevance, 2)}
            for i, relevance in ranked if i < len(hits)]


def normalize(text: str) -> str:
    """Lapis 1 (K18): huruf kecil, tanpa aksen, tanda baca jadi spasi, angka Romawi jadi angka."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()  # Amélie -> Amelie
    text = re.sub(r"[^a-z0-9]+", " ", text.lower().replace("&", " and "))
    return " ".join(ROMAN.get(word, word) for word in text.split())


def find_title(query: str) -> dict[int, str]:
    """Cari judul dalam 4 lapis (K18). Kembalikan {id film: label match}, judul persis di urutan pertama.

    Judul persis tidak menghentikan pencarian: "Star Wars" harus ikut membawa Episode V dan seterusnya.
    """
    df = load_movies().sort_values("votes", ascending=False)  # yang terpopuler lebih dulu
    titles = df["title"].map(normalize)
    q = normalize(query)
    words = q.split()
    if not words:
        return {}

    partial = titles.map(lambda t: set(words) <= set(t.split()))  # judul persis pasti lolos di sini juga
    if partial.any():
        labels = (titles[partial] == q).map({True: "exact", False: "partial"})
        hits = df[partial].assign(label=labels).sort_values("label", kind="stable")  # "exact" < "partial"
    else:
        fuzzy = titles.map(lambda t: all(difflib.get_close_matches(w, t.split(), n=1, cutoff=0.8) for w in words))
        hits = df[fuzzy].assign(label="fuzzy")
    return dict(zip(hits["id"].head(MAX_MATCHES), hits["label"].head(MAX_MATCHES)))


@tool(parse_docstring=True)
def get_movie_details(titles: list[str]) -> str:
    """Look up full details of one or more movies by title. Tolerates typos and letter case.

    Use this when the user names a movie or a movie series (e.g. Harry Potter returns every
    Harry Potter movie), asks a follow-up question about a movie mentioned earlier in the
    conversation, or wants to compare movies (pass all titles at once).

    Args:
        titles: Movie titles or series names, one per item. Use the exact titles from earlier tool results when available.
    """
    movies, not_found = [], []
    df = load_movies().set_index("id", drop=False)
    for query in titles:
        matches = find_title(query)
        if matches:
            movies += [{"match": matches[movie["id"]], "query": query, **movie}
                       for movie in to_records(df.loc[list(matches), DETAIL_FIELDS])]
        else:
            by_normalized = {normalize(title): title for title in df["title"]}
            closest = difflib.get_close_matches(normalize(query), by_normalized, n=3, cutoff=0)  # lapis 4
            not_found.append({"query": query, "closest_titles": [by_normalized[t] for t in closest]})

    result = {"movies": movies}
    if not_found:
        result.update(not_found=not_found, hint=NOT_FOUND_HINT)
    return json.dumps(result, ensure_ascii=False)


@tool(parse_docstring=True)
def similar_movies(title: str, year_from: int | None = None, year_to: int | None = None) -> str:
    """Find movies similar to a given movie ("movies like Inception"), by comparing plot embeddings.

    Args:
        title: Title of the movie the user liked. Tolerates typos.
        year_from: Earliest release year, inclusive. Leave empty unless the user names a year or decade.
        year_to: Latest release year, inclusive. Leave empty unless the user names a year or decade.
    """
    matches = find_title(title)
    if not matches:
        return json.dumps({"movies": [], "not_found": [{"query": title}], "hint": NOT_FOUND_HINT})
    source = load_movies().set_index("id").loc[next(iter(matches))]
    return json.dumps({"similar_to": f"{source['title']} ({source['year']})",
                       "movies": similar_page(title, year_from, year_to)}, ensure_ascii=False)


def similar_page(title: str, year_from: int | None = None, year_to: int | None = None,
                 offset: int = 0) -> list[dict]:
    """Satu halaman (5 film) hasil similar_movies. offset dipakai tombol "Muat lebih banyak" di UI (K45)."""
    matches = find_title(title)
    if not matches:
        return []
    store = _vector_store()
    # Query = id film: Qdrant memakai vektor film itu sendiri sebagai query, dan film itu tidak ikut di hasil.
    points = store.client.query_points(
        store.collection_name, query=next(iter(matches)), using=store.vector_name, limit=PAGE_SIZE, offset=offset,
        with_payload=True, query_filter=_qdrant_filter(None, year_from, year_to),  # tanpa genre (K34)
    ).points
    return [{**{field: p.payload["metadata"][field] for field in FIELDS_FOR_LLM}, "score": round(p.score, 3)}
            for p in points]


SortField = Literal["rating", "meta_score", "votes", "gross_usd", "runtime_min", "year"]


@tool(parse_docstring=True)
def rank_movies(
    sort_by: SortField = "rating",
    order: Literal["highest", "lowest"] = "highest",
    title: str | None = None,
    genre: Genre | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    director: str | None = None,
    star: str | None = None,
    limit: int = 5,
) -> str:
    """Rank, filter, and count movies by numbers: best rated, most voted, highest grossing, longest, newest.

    Use this for "top/best/most/how many" questions, to rank a movie series, to list a director's
    or actor's movies, and for recommendations that only name a genre, year, or decade without
    describing a plot or mood. Returns the matching count and average rating too.

    Args:
        sort_by: rating = IMDB rating, meta_score = critics score (0-100), votes = popularity, gross_usd = box office.
        order: highest or lowest first.
        title: Movie series or part of a title, e.g. Star Wars. Tolerates typos.
        genre: Only movies with this genre. Leave empty unless the user names a genre.
        year_from: Earliest release year, inclusive. Leave empty unless the user names a year or decade.
        year_to: Latest release year, inclusive. Leave empty unless the user names a year or decade.
        director: Part of the director's name, e.g. Nolan.
        star: Part of an actor's name, e.g. DiCaprio.
        limit: Number of movies to return, 1 to 10.
    """
    df = _ranked(sort_by, order, title, genre, year_from, year_to, director, star)
    return json.dumps({
        "matching_count": len(df),
        "average_rating": round(float(df["rating"].mean()), 2) if len(df) else None,
        "movies": to_records(df.head(max(1, min(limit, 10)))[RANK_FIELDS]),
    }, ensure_ascii=False)


def rank_page(sort_by: str = "rating", order: str = "highest", title: str | None = None, genre: str | None = None,
              year_from: int | None = None, year_to: int | None = None, director: str | None = None,
              star: str | None = None, limit: int = PAGE_SIZE, offset: int = 0) -> list[dict]:
    """Satu halaman hasil rank_movies untuk tombol "Muat lebih banyak" di UI (K45, K47)."""
    df = _ranked(sort_by, order, title, genre, year_from, year_to, director, star)
    return to_records(df.iloc[offset:offset + limit][RANK_FIELDS])


def _ranked(sort_by, order, title, genre, year_from, year_to, director, star):
    """Filter lalu urutkan. Dipakai rank_movies (untuk LLM) dan rank_page (untuk UI)."""
    df = load_movies().dropna(subset=[sort_by])  # gross_usd/meta_score kosong untuk sebagian film
    if title:
        df = df[df["id"].isin(find_title(title))]
    if genre:
        df = df[df["genres"].map(lambda genres: genre in genres)]
    if year_from:
        df = df[df["year"] >= year_from]
    if year_to:
        df = df[df["year"] <= year_to]
    if director:
        df = df[df["director"].map(normalize).str.contains(normalize(director), regex=False)]
    if star:
        df = df[df["stars"].map(lambda stars: any(normalize(star) in normalize(s) for s in stars))]

    return df.sort_values(sort_by, ascending=(order == "lowest"))


TOOLS = [search_movies, similar_movies, get_movie_details, rank_movies]
# Tool yang punya "Muat lebih banyak" (K45, K47): nama tool → fungsi satu halaman dengan offset.
PAGERS = {"search_movies": search_page, "similar_movies": similar_page, "rank_movies": rank_page}
