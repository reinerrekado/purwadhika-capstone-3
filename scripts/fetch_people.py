"""Fase offline: ambil bio dan foto semua sutradara dan pemain dari Wikipedia, sekali saja (K69).

Hasilnya data/people.csv, dipakai tampilan panel orang dan tool get_person_info. Tidak ada panggilan jaringan
saat app berjalan. Dijalankan dari folder root project:  python -m scripts.fetch_people
Aman dijalankan ulang: nama yang sudah punya bio dilewati. Nama yang tidak ketemu dicari ulang setiap kali
(jumlahnya kecil), karena aturan pencarian bisa membaik. Teks Wikipedia berlisensi CC BY-SA, jadi setiap
baris menyimpan tautan sumbernya.
"""

import difflib
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from app.data import PEOPLE_PATH, load_movies

SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
SEARCH_API = "https://en.wikipedia.org/w/rest.php/v1/search/title?limit=3&q="
HEADERS = {"User-Agent": "Rakfilm-capstone/0.1 (proyek belajar Purwadhika; https://github.com/reinerrekado/purwadhika-capstone-3)"}
SUFFIXES = ("", " (actor)", " (actress)", " (director)", " (filmmaker)")  # nama ambigu: "Tom Murray" -> "Tom Murray (actor)"
PERSON_WORDS = ("actor", "actress", "director", "filmmaker", "comedian", "singer", "writer", "producer", "screenwriter",
                "cinematographer", "composer", "musician", "model", "presenter", "martial artist", "animator", "voice",
                "entertainer", "dancer", "performer", "stunt", "personality", "choreographer")
ALIASES = {  # nama di dataset -> judul Wikipedia, untuk nama penting yang tidak bisa ditemukan otomatis (urutan atau ejaan berbeda)
    "Tony Chiu-Wai Leung": "Tony Leung Chiu-wai",
    "Kar-Wai Wong": "Wong Kar-wai",
}
COLUMNS = ["name", "title", "description", "extract", "photo", "url"]


def fetch_json(url: str) -> dict | None:
    """JSON dari satu alamat, atau None kalau halamannya memang tidak ada (404).

    Pembatasan kecepatan (429) dan gangguan server (5xx) bukan "tidak ada": ditunggu lalu diulang, dan kalau tetap
    gagal dilempar sebagai error supaya namanya tidak tercatat sebagai "tidak ketemu" (K69).
    """
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=15) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            wait = float(error.headers.get("Retry-After") or 0) if error.code == 429 else 0
            time.sleep(max(wait, 2 ** attempt))
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** attempt)
    raise RuntimeError(f"gagal mengambil {url}")


def plain(text: str) -> str:
    """Huruf kecil tanpa aksen dan tanda kurung: "Ryô Kase" dan "Ryo Kase" menjadi sama."""
    text = re.sub(r"['’ʻ`]", "", re.sub(r"\s*\(.*?\)", "", text))  # "Ken'ichi" = "Kenichi", "(actor)" dibuang
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def same_name(a: str, b: str) -> bool:
    """Dua nama dianggap orang yang sama kalau tiap katanya hampir identik (urutan bebas, y dan j disamakan dengan i).

    Per kata, bukan per huruf seluruh nama: "Michelle La" dan "Michelle Law" mirip 96% sebagai teks, tapi "La" dan
    "Law" berbeda kata, sedangkan "Aleksey Kravchenko" dan "Aleksei Kravchenko" hanya beda transliterasi (K69).
    """
    words_a, words_b = (sorted(re.sub(r"[yj]", "i", word) for word in plain(n).split()) for n in (a, b))
    return len(words_a) == len(words_b) and all(
        difflib.SequenceMatcher(None, x, y).ratio() >= 0.88 for x, y in zip(words_a, words_b))


def is_person(page: dict | None) -> bool:
    """Artikel biasa yang deskripsinya menyebut profesi orang film."""
    return bool(page) and page.get("type") == "standard" and any(
        word in (page.get("description") or "").lower() for word in PERSON_WORDS)


def find_page(name: str) -> dict | None:
    """Halaman Wikipedia untuk satu nama: judul persis (dan variasi profesi), lalu pencarian judul sebagai cadangan."""
    name = ALIASES.get(name, name)
    for suffix in SUFFIXES:
        page = fetch_json(SUMMARY_API + urllib.parse.quote((name + suffix).replace(" ", "_"), safe=""))
        if is_person(page):
            return page
    found = fetch_json(SEARCH_API + urllib.parse.quote(name)) or {}
    for hit in found.get("pages", []):  # hanya judul yang kata-katanya hampir sama persis: mencegah salah orang
        if same_name(name, hit["title"]):
            page = fetch_json(SUMMARY_API + urllib.parse.quote(hit["title"].replace(" ", "_"), safe=""))
            if is_person(page):
                return page
    return None


def lookup(name: str) -> dict | None:
    """Baris untuk satu nama, atau None kalau gagal sementara (dijalankan ulang nanti)."""
    try:
        page = find_page(name)
    except RuntimeError:
        return None
    if not page:
        return {"name": name, "title": "", "description": "", "extract": "", "photo": "", "url": ""}  # benar-benar tidak ketemu
    extract = " ".join(page.get("extract", "").split())  # spasi ganda dan baris kosong bekas simbol pengucapan dibuang
    return {"name": name, "title": page["title"], "description": page.get("description", ""),
            "extract": extract if len(extract) >= 15 else "",  # potongan rusak seperti "dʒ" (Bárbara Lennie) tidak dipakai
            "photo": (page.get("thumbnail") or {}).get("source", ""), "url": page["content_urls"]["desktop"]["page"]}


def main() -> None:
    movies = load_movies()
    names = sorted(set(movies["director"]) | {star for stars in movies["stars"] for star in stars})
    done = pd.read_csv(PEOPLE_PATH, keep_default_na=False) if PEOPLE_PATH.exists() else pd.DataFrame(columns=COLUMNS)
    have_bio = set(done.loc[done["title"] != "", "name"])
    todo = [name for name in names if name not in have_bio]
    print(f"{len(names)} nama unik. Sudah punya bio {len(have_bio)}, perlu diambil atau dicari ulang {len(todo)}.")

    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for number, row in enumerate(pool.map(lookup, todo), 1):
            results.append(row)
            if number % 100 == 0 or number == len(todo):  # indikator kemajuan: pekerjaan panjang tidak boleh diam
                print(f"  {number}/{len(todo)} nama diproses", flush=True)
    rows = [row for row in results if row]
    if len(rows) < len(todo):
        print(f"{len(todo) - len(rows)} nama gagal sementara dan tidak disimpan. Jalankan ulang perintah ini untuk mengulang.")

    kept = done[~done["name"].isin({row["name"] for row in rows})]  # baris lama diganti hasil baru, kecuali yang gagal sementara
    people = pd.concat([kept, pd.DataFrame(rows, columns=COLUMNS)]).drop_duplicates("name").sort_values("name")
    people.to_csv(PEOPLE_PATH, index=False)
    found = people[people["title"] != ""]
    print(f"Tersimpan {len(people)} baris di {PEOPLE_PATH.name}: bio {len(found)} ({len(found) / len(people):.0%}), "
          f"foto {(found['photo'] != '').sum()} ({(found['photo'] != '').sum() / len(people):.0%}).")


if __name__ == "__main__":
    main()
