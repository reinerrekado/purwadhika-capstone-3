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

    Use this when the user describes what they want to watch. Do not use it to find a movie
    or a movie series by title; use get_movie_details for that.

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
    return json.dumps({"movies": movies}, ensure_ascii=False)


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
        result["not_found"] = not_found
        result["hint"] = ("Non-English movies use their original title (e.g. Parasite = Gisaengchung). "
                          "If you know the director or year, try rank_movies with those filters; "
                          "otherwise try search_movies with a short English plot description.")
    return json.dumps(result, ensure_ascii=False)


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

    Use this for "top/best/most/how many" questions, to rank a movie series, or to list a
    director's or actor's movies. Returns the matching count and average rating too.

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

    top = df.sort_values(sort_by, ascending=(order == "lowest")).head(max(1, min(limit, 10)))
    return json.dumps({
        "matching_count": len(df),
        "average_rating": round(float(df["rating"].mean()), 2) if len(df) else None,
        "movies": to_records(top[RANK_FIELDS]),
    }, ensure_ascii=False)


TOOLS = [search_movies, get_movie_details, rank_movies]
