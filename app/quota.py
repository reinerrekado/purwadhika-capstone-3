"""Pembatas pemakaian (K68): app publik tidak boleh menghabiskan kuota OpenRouter karena satu pengunjung atau bot.

Dua batas, keduanya mudah diubah di sini. Satu pertanyaan sekitar Rp20-60, jadi 150 pertanyaan per jam paling
banyak sekitar Rp9.000. Penghitung global hidup di memori proses server: reset kalau app di-restart.
"""

import time
from collections import deque

MAX_PER_SESSION = 30  # pertanyaan per sesi browser
MAX_PER_HOUR = 150  # pertanyaan per jam untuk semua pengunjung
_recent: deque[float] = deque()  # waktu tiap pertanyaan yang diterima, dibagi semua sesi di proses yang sama


def blocked(asked_in_session: int) -> str | None:
    """Pesan untuk pengguna kalau pertanyaan harus ditolak, None kalau boleh. Tidak mencatat apa pun."""
    now = time.time()
    while _recent and now - _recent[0] > 3600:
        _recent.popleft()
    if asked_in_session >= MAX_PER_SESSION:
        return f"Batas demo tercapai: {MAX_PER_SESSION} pertanyaan per sesi. Terima kasih sudah mencoba Rakfilm."
    if len(_recent) >= MAX_PER_HOUR:
        return "Rakfilm sedang ramai dan batas pertanyaan per jam tercapai. Coba lagi beberapa menit lagi."
    return None


def record() -> None:
    """Catat satu pertanyaan yang diterima."""
    _recent.append(time.time())
