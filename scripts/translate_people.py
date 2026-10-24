"""Fase offline: terjemahkan bio orang film dari people.csv ke bahasa Indonesia, sekali saja (K70).

Menambah kolom extract_id di data/people.csv. Prompt `bio-translator` disimpan di Langfuse (dibuat otomatis kalau
belum ada). Sebelum memanggil LLM, biaya diperkirakan dan skrip berhenti kalau melewati batas (MAX_COST_USD).
Dijalankan dari folder root project:  python -m scripts.translate_people
Aman dijalankan ulang: bio yang sudah punya terjemahan dilewati.
"""

import json
import re
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from langchain_core.runnables import RunnablePassthrough
from langfuse import get_client
from langfuse.langchain import CallbackHandler

from app.config import get_llm
from app.data import PEOPLE_PATH
from scripts.fetch_people import plain

PROMPT_NAME = "bio-translator"  # disimpan sekali di Langfuse, label "production"
PROMPT_TEXT = """Translate each short biography below from English into natural, fluent Indonesian.

Rules:
1. Translate only. Do not add, remove, or explain anything.
2. Keep the names of people, characters, places, organizations, and titles of works exactly as written (e.g. Christopher Nolan, The Dark Knight, Hollywood).
3. Keep dates, numbers, and awards as they are.
4. Return JSON only: an object that maps each id to its Indonesian translation.

Biographies (JSON object, id -> English text):
{{bios}}"""
BATCH_SIZE = 25
MAX_COST_USD = 0.83  # sekitar Rp15.000 (batas dari Reiner)
PRICE_INPUT, PRICE_OUTPUT = 0.40, 1.60  # USD per 1 juta token, openai/gpt-4.1-mini di OpenRouter
CHARS_PER_TOKEN, ID_LENGTH_FACTOR = 4, 1.25  # perkiraan kasar: 1 token = 4 karakter, bahasa Indonesia ±25% lebih panjang
PROMPT_TOKENS = 300  # instruksi per panggilan


def estimate_cost(texts: list[str]) -> float:
    """Perkiraan biaya terjemahan dalam USD, dari panjang karakter."""
    calls = -(-len(texts) // BATCH_SIZE)
    tokens_in = sum(len(t) for t in texts) / CHARS_PER_TOKEN + calls * PROMPT_TOKENS
    tokens_out = sum(len(t) for t in texts) / CHARS_PER_TOKEN * ID_LENGTH_FACTOR
    return (tokens_in * PRICE_INPUT + tokens_out * PRICE_OUTPUT) / 1e6


def subject_named(row, text: str) -> bool:
    """Terjemahan harus menyebut nama belakang orangnya (K70). Menangkap hasil model yang bergeser ke baris tetangga.

    Nama depan saja tidak cukup: "Takeshi Aono" dan "Takeshi Kaneshiro" berbagi nama depan. Nama satu kata
    ("Madhavan", "Topol") dipakai utuh.
    """
    words = set()
    for full in (row["name"], row["title"]):
        tokens = plain(full).split()
        words |= {t for t in tokens[1:] if len(t) >= 3} or set(tokens)
    lead = re.match(r"(?:[A-Z][^\s,.;(]*\s?){1,6}", row["extract"])  # bio dibuka dengan nama lahir: "Knut Gunnar Johanson adalah..."
    if lead:
        words |= {t for t in plain(lead.group(0)).split()[1:] if len(t) >= 3}
    return any(word in plain(text) for word in words)


def get_prompt():
    """Prompt dari Langfuse; dibuat sekali kalau belum ada (aturan: semua prompt di Langfuse, bukan di kode)."""
    langfuse = get_client()
    try:
        return langfuse.get_prompt(PROMPT_NAME)
    except Exception:
        langfuse.create_prompt(name=PROMPT_NAME, prompt=PROMPT_TEXT, labels=["production"], type="text")
        return langfuse.get_prompt(PROMPT_NAME, cache_ttl_seconds=0)


def translate_batch(prompt, llm, batch: dict[str, str]) -> dict[str, str]:
    """Satu panggilan LLM untuk 25 bio. Model diminta mengembalikan JSON {nama: terjemahan}."""
    chain = RunnablePassthrough() | llm.bind(response_format={"type": "json_object"})
    reply = chain.invoke(  # di dalam chain supaya prompt Langfuse tertaut ke generation (K73)
        prompt.compile(bios=json.dumps(batch, ensure_ascii=False)),
        config={"callbacks": [CallbackHandler()], "metadata": {"langfuse_tags": ["offline"], "langfuse_prompt": prompt}},
    )
    return json.loads(reply.content)


def main() -> None:
    people = pd.read_csv(PEOPLE_PATH, keep_default_na=False)
    if "extract_id" not in people:
        people["extract_id"] = ""
    wrong = [i for i, row in people.iterrows() if row["extract_id"] and not subject_named(row, row["extract_id"])]
    for i in wrong:  # terjemahan lama yang tertukar atau rusak dibuang, lalu diterjemahkan ulang di bawah
        print(f"  dibuang (tidak menyebut {people.loc[i, 'name']}): {people.loc[i, 'extract_id'][:60]!r}")
        people.loc[i, "extract_id"] = ""
    todo = people[(people["extract"] != "") & (people["extract_id"] == "")]
    cost = estimate_cost(todo["extract"].tolist())
    print(f"{len(todo)} bio perlu diterjemahkan. Perkiraan biaya ${cost:.2f} (batas ${MAX_COST_USD:.2f}).")
    if cost > MAX_COST_USD:
        raise SystemExit("Perkiraan melewati batas, tidak ada yang dikirim. Naikkan MAX_COST_USD kalau memang disengaja.")

    ids = {str(i): row.extract for i, row in todo.iterrows()}  # kunci = nomor baris, bukan nama (nama bisa mengandung tanda kutip)
    items = list(ids.items())
    batches = [dict(items[i:i + BATCH_SIZE]) for i in range(0, len(items), BATCH_SIZE)]
    prompt, llm = get_prompt(), get_llm()
    results = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        for number, result in enumerate(pool.map(lambda batch: translate_batch(prompt, llm, batch), batches), 1):
            results.append(result)
            print(f"  {number}/{len(batches)} kelompok diterjemahkan", flush=True)  # indikator kemajuan

    rejected = []
    for result in results:
        for key, text in result.items():
            if key not in ids or not text.strip():
                continue
            if subject_named(people.loc[int(key)], text):
                people.loc[int(key), "extract_id"] = text.strip()
            else:
                rejected.append(people.loc[int(key), "name"])  # tidak menyebut orangnya: tidak disimpan
    people.to_csv(PEOPLE_PATH, index=False)
    done = (people["extract_id"] != "").sum()
    print(f"Tersimpan: {done} dari {(people['extract'] != '').sum()} bio punya terjemahan.")
    get_client().flush()  # kirim trace sebelum skrip berhenti
    for name in rejected:
        print(f"  ditolak (tidak menyebut orangnya): {name}")
    for key in (k for k in ids if not people.loc[int(k), "extract_id"]):
        print(f"  belum ada terjemahan, UI memakai bio Inggris: {people.loc[int(key), 'name']}")


if __name__ == "__main__":
    main()
