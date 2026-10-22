"""Memuat dan membersihkan dataset IMDB Top 1000.

Satu-satunya tempat pembersihan data. Dipakai oleh scripts/ingest.py (isi Qdrant)
dan app/tools.py (statistik dan lookup), supaya angka di keduanya selalu sama.
"""

import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "imdb_top_1000.csv"


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
        "poster": raw["Poster_Link"].map(_poster_300px),
    })


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
