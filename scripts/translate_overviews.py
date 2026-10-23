"""Fase offline: terjemahkan 1.000 sinopsis ke bahasa Indonesia, sekali saja (K42).

Hasilnya data/overview_id.csv, hanya untuk tampilan di panel detail. Qdrant dan LLM tetap memakai
teks Inggris (K12, K26). Dijalankan dari folder root project:  python -m scripts.translate_overviews
Aman dijalankan ulang: film yang sudah ada di file dilewati.
"""

import json
import re
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from langfuse import get_client

from app.config import get_llm
from app.data import OVERVIEW_ID_PATH, load_movies

PROMPT_NAME = "overview-translator"  # dibuat sekali di Langfuse, label "production"
BATCH_SIZE = 25


def translate_batch(prompt, llm, batch: dict[int, str]) -> dict[int, str]:
    """Satu panggilan LLM untuk 25 sinopsis. Model diminta mengembalikan JSON {id: terjemahan}."""
    text = prompt.compile(overviews=json.dumps(batch, ensure_ascii=False))
    reply = llm.invoke(text, response_format={"type": "json_object"})
    return {int(movie_id): translation for movie_id, translation in json.loads(reply.content).items()}


def check(original: str, translation: str, common_words: set[str]) -> list[str]:
    """Cek otomatis: panjang wajar (tidak menambah isi) dan nama di tengah kalimat tidak ikut diterjemahkan.

    Kata yang di sinopsis lain juga muncul berhuruf kecil (war, king, earth) atau berakhiran kebangsaan
    (German, Jewish, Japanese) adalah kata umum yang memang wajar diterjemahkan, jadi tidak dihitung.
    """
    problems = []
    ratio = len(translation) / len(original)
    if not 0.75 <= ratio <= 1.7:
        problems.append(f"panjang {ratio:.2f}x")
    names = re.findall(r"(?<=[a-z,] )[A-Z][a-z]+", original)  # kata berhuruf kapital di tengah kalimat
    missing = [name for name in names if name not in translation and name.lower() not in common_words
               and not re.search(r"(an|ans|ish|ese|ian|ians|i|ic)$", name)]
    if missing:
        problems.append("nama hilang: " + ", ".join(missing))
    return problems


def main() -> None:
    movies = load_movies().set_index("id")["overview"]
    done = pd.read_csv(OVERVIEW_ID_PATH) if OVERVIEW_ID_PATH.exists() else pd.DataFrame(columns=["id", "overview_id"])
    todo = movies.drop(done["id"], errors="ignore")
    print(f"Sudah ada {len(done)}, perlu diterjemahkan {len(todo)}.")

    prompt, llm = get_client().get_prompt(PROMPT_NAME), get_llm()
    items = list(todo.items())
    batches = [dict(items[i:i + BATCH_SIZE]) for i in range(0, len(items), BATCH_SIZE)]
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda batch: translate_batch(prompt, llm, batch), batches))

    new = pd.DataFrame([(movie_id, text) for result in results for movie_id, text in result.items()
                        if movie_id in todo.index], columns=["id", "overview_id"])
    all_rows = pd.concat([done, new]).drop_duplicates("id").sort_values("id")
    all_rows.to_csv(OVERVIEW_ID_PATH, index=False)

    common_words = set(re.findall(r"\b[a-z]+\b", " ".join(movies)))
    flagged = {row.id: check(movies[row.id], row.overview_id, common_words) for row in all_rows.itertuples()}
    flagged = {movie_id: problems for movie_id, problems in flagged.items() if problems}
    print(f"Tersimpan {len(all_rows)} terjemahan di {OVERVIEW_ID_PATH.name}. Ditandai untuk dicek: {len(flagged)}.")
    for movie_id, problems in flagged.items():
        print(f"  #{movie_id}: {'; '.join(problems)}")


if __name__ == "__main__":
    main()
