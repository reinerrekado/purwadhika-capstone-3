"""Uji key Qdrant read-only untuk penilai (K62): baca harus berhasil, tulis harus ditolak.

Dijalankan dari folder root project:  python -m scripts.check_readonly_key
Key dibaca dari QDRANT_READONLY_API_KEY di .env dan tidak pernah dicetak.
Uji tulis memakai collection percobaan baru, bukan imdb_movies, jadi data asli tidak tersentuh.
"""

import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

load_dotenv()

PROBE = "zz_readonly_probe"  # nama collection percobaan; seharusnya tidak pernah berhasil dibuat


def main() -> None:
    url, collection = os.getenv("QDRANT_URL"), os.getenv("QDRANT_COLLECTION", "imdb_movies")
    readonly, admin = os.getenv("QDRANT_READONLY_API_KEY"), os.getenv("QDRANT_API_KEY")
    if not (url and readonly):
        raise SystemExit("Isi QDRANT_URL dan QDRANT_READONLY_API_KEY di .env dulu (key dari konsol Qdrant Cloud).")
    if readonly == admin:
        raise SystemExit("[GAGAL] Ini key yang sama dengan QDRANT_API_KEY (admin). Buat key baru read-only.")
    client = QdrantClient(url=url, api_key=readonly)
    print("[OK] Key berbeda dari key admin.")

    try:  # 1. baca harus berhasil
        info = client.get_collection(collection)
        points, _ = client.scroll(collection, limit=1)
        print(f"[OK] Baca: collection '{collection}' berisi {info.points_count} point, contoh id {points[0].id}.")
    except Exception as error:
        raise SystemExit(f"[GAGAL] Baca ditolak atau error ({type(error).__name__}). Cek key, izin collection, dan tanggal kedaluwarsa.")

    try:  # 2. tulis harus ditolak: percobaan membuat collection baru
        client.create_collection(PROBE, vectors_config=models.VectorParams(size=4, distance=models.Distance.COSINE))
    except UnexpectedResponse as error:
        if error.status_code in (401, 403):
            print(f"[OK] Tulis ditolak (HTTP {error.status_code}). Key benar-benar read-only.")
            return
        raise SystemExit(f"[?] Tulis gagal dengan HTTP {error.status_code}, bukan penolakan izin. Periksa manual.")
    client.delete_collection(PROBE)  # kalau sampai sini, key bisa menulis: bersihkan percobaannya
    raise SystemExit("[GAGAL] Collection percobaan berhasil dibuat. Key ini BUKAN read-only; hapus dan buat ulang.")


if __name__ == "__main__":
    main()
