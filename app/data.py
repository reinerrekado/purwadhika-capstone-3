"""Memuat dan membersihkan dataset IMDB Top 1000.

Satu-satunya tempat pembersihan data. Dipakai oleh scripts/ingest.py (isi Qdrant)
dan app/tools.py (statistik dan lookup), supaya angka di keduanya selalu sama.
"""

import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "imdb_top_1000.csv"
OVERVIEW_ID_PATH = DATA_PATH.with_name("overview_id.csv")  # terjemahan sinopsis, dibuat translate_overviews.py
PEOPLE_PATH = DATA_PATH.with_name("people.csv")  # bio dan foto sutradara/pemain dari Wikipedia, dibuat fetch_people.py (K69)


def _poster_300px(url: str) -> str:
    """Ganti thumbnail 67 px dari dataset dengan versi 300 px dari server yang sama."""
    return re.sub(r"\._V1_.*\.jpg$", "._V1_SX300.jpg", url)


@lru_cache(maxsize=1)
def load_movies() -> pd.DataFrame:
    """Baca CSV sekali, bersihkan, lalu simpan di memori untuk pemanggilan berikutnya."""
    raw = pd.read_csv(DATA_PATH)

    # Satu-satunya tahun yang rusak di dataset: Apollo 13 berisi "PG" (rilis 1995).
    raw.loc[raw["Series_Title"] == "Apollo 13", "Released_Year"] = "1995"

    return pd.DataFrame({
        "id": raw.index,  # nomor baris, karena judul tidak unik (Drishyam 2013 dan 2015)
        "title": raw["Series_Title"],
        "year": raw["Released_Year"].astype(int),
        "genres": raw["Genre"].str.split(", "),  # "Action, Crime" -> ["Action", "Crime"]
        "rating": raw["IMDB_Rating"],
        "meta_score": raw["Meta_score"].astype("Int64"),  # Int64 = integer yang boleh kosong
        "runtime_min": raw["Runtime"].str.removesuffix(" min").astype(int),
        "director": raw["Director"],
        "stars": raw[["Star1", "Star2", "Star3", "Star4"]].values.tolist(),
        "votes": raw["No_of_Votes"],
        "gross_usd": raw["Gross"].str.replace(",", "").astype("Int64"),
        "certificate": raw["Certificate"],
        "overview": raw["Overview"],
        "overview_id": _overview_id(raw["Overview"]),
        "poster": raw["Poster_Link"].map(_poster_300px),
    })


def _overview_id(overview: pd.Series) -> pd.Series:
    """Sinopsis bahasa Indonesia untuk tampilan (K42). Kalau file terjemahan tidak ada, pakai sinopsis Inggris."""
    if not OVERVIEW_ID_PATH.exists():
        return overview
    translated = pd.read_csv(OVERVIEW_ID_PATH).set_index("id")["overview_id"]
    return translated.reindex(overview.index).fillna(overview)


def _angka(value: float, decimals: int = 0) -> str:
    """Format angka Indonesia: 1234567.8 → "1.234.567,8"."""
    return f"{value:,.{decimals}f}".translate(str.maketrans(",.", ".,"))


def movie_facts(movie_id: int) -> list[str]:
    """"Fakta menarik" untuk panel detail (K43). Semua dihitung dari dataset; fakta tanpa data dilewati."""
    df = load_movies()
    movie = df.set_index("id").loc[movie_id]
    facts = []

    rating_rank = int(df["rating"].rank(ascending=False, method="min")[movie_id])
    if rating_rank <= 100:  # rating dataset hanya 7,6–9,3, jadi peringkat di bawah 100 besar banyak yang seri
        facts.append(f"Masuk 100 besar rating IMDB di dataset ini (peringkat #{rating_rank})")

    votes_top = df["votes"].rank(ascending=False, pct=True)[movie_id] * 100
    facts.append(f"Dinilai {_angka(movie['votes'])} penonton IMDB"
                 + (f" (top {max(1, round(votes_top))}% terpopuler)" if votes_top <= 20 else ""))

    if not pd.isna(movie["gross_usd"]):
        gross_rank = int(df["gross_usd"].rank(ascending=False, method="min")[movie_id])
        facts.append(f"Pendapatan box office AS ${_angka(movie['gross_usd'] / 1e6, 1)} juta, terlaris ke-{gross_rank} "
                     f"dari {df['gross_usd'].notna().sum()} film yang datanya ada")

    if not pd.isna(movie["meta_score"]):
        gap = movie["meta_score"] / 10 - movie["rating"]  # Metascore 0–100 disetarakan ke skala rating 0–10
        if gap >= 1:
            facts.append(f"Kritikus lebih memuji daripada penonton (Metascore {movie['meta_score']} "
                         f"vs rating {_angka(movie['rating'], 1)})")
        elif gap <= -1:
            facts.append(f"Penonton lebih menyukai daripada kritikus (rating {_angka(movie['rating'], 1)} "
                         f"vs Metascore {movie['meta_score']})")

    director_count = (df["director"] == movie["director"]).sum()
    if director_count > 1:
        facts.append(f"1 dari {director_count} film {movie['director']} di dataset ini")
    return facts


@lru_cache(maxsize=1)
def load_people() -> pd.DataFrame:
    """Bio dan foto sutradara/pemain dari people.csv (K69, K70), diindeks nama seperti di dataset.

    Kolom: title (judul Wikipedia), description, extract (Inggris), extract_id (Indonesia), photo, url.
    Teks kosong berarti tidak ada. File tidak ada: tabel kosong, app tetap jalan tanpa bio.
    """
    columns = ["title", "description", "extract", "extract_id", "photo", "url"]
    if not PEOPLE_PATH.exists():
        return pd.DataFrame(columns=columns).rename_axis("name")
    people = pd.read_csv(PEOPLE_PATH, keep_default_na=False).set_index("name")
    return people.reindex(columns=columns, fill_value="")


@lru_cache(maxsize=1)
def _filmography() -> dict[str, list[tuple[int, str]]]:
    """{nama: [(id film, "Sutradara" atau "Pemain")]} untuk semua orang, dihitung sekali dari 1.000 film."""
    films: dict[str, list[tuple[int, str]]] = {}
    for movie in load_movies().itertuples():
        films.setdefault(movie.director, []).append((movie.id, "Sutradara"))
        for star in movie.stars:
            films.setdefault(star, []).append((movie.id, "Pemain"))
    return films


def person_profile(name: str) -> dict:
    """Profil satu orang: bio, foto, dan angka yang dihitung dari dataset (K71). Dipakai tool dan panel orang.

    films diurutkan dari rating tertinggi; satu film yang orangnya sutradara dan pemain sekaligus dihitung sekali.
    """
    movies = load_movies().set_index("id")
    seen, films = set(), []
    for movie_id, role in sorted(_filmography().get(name, []), key=lambda f: -movies.loc[f[0], "rating"]):
        if movie_id not in seen:
            seen.add(movie_id)
            films.append((int(movie_id), role))
    people = load_people()
    row = people.loc[name] if name in people.index else None
    ratings = [movies.loc[movie_id, "rating"] for movie_id, _ in films]
    years = [int(movies.loc[movie_id, "year"]) for movie_id, _ in films]
    return {
        "name": name,
        "wikipedia_title": row["title"] if row is not None else "",
        "bio_en": row["extract"] if row is not None else "",
        "bio_id": (row["extract_id"] or row["extract"]) if row is not None else "",  # tanpa terjemahan: teks Inggris
        "photo": row["photo"] if row is not None else "",
        "url": row["url"] if row is not None else "",
        "roles": sorted({role for _, role in films}),
        "films": films,
        "average_rating": round(float(sum(ratings) / len(ratings)), 1) if ratings else None,
        "years": [min(years), max(years)] if years else [],
    }


def all_genres() -> list[str]:
    """21 genre unik, diurutkan. Dipakai untuk membatasi pilihan genre di tool."""
    return sorted(load_movies()["genres"].explode().unique())


def to_records(df: pd.DataFrame) -> list[dict]:
    """Ubah DataFrame jadi list of dict siap JSON: nilai kosong (NaN/NA) menjadi None."""
    return [
        {key: (None if not isinstance(value, list) and pd.isna(value) else value)
         for key, value in row.items()}
        for row in df.to_dict(orient="records")
    ]
