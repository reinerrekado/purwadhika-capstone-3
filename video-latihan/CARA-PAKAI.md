# Video latihan Rakfilm: isi folder dan cara memperbaruinya

Folder ini **ikut git sejak 9 Nov siang** (supaya bisa di-pull di Mac), kecuali `arsip/` dan `bagian/` (besar; tersedia di Google Drive › Video Untuk Capstone 3 › video-latihan-tambahan, dipasang dengan `python video-latihan/pipeline/pasang_tambahan.py <path unduhan>`) serta `pipeline/pylib/` dan `pipeline/video/seg/` (khusus Windows / klip antara; dibuat ulang oleh `pip install` + `assemble.py`). Dibuat 9 Nov dini hari oleh Claude Code dari deck "Rakfilm · Video" dan `naskah-video.md` (di folder ini juga). Panduan pindah ke Mac: `LANJUT-DI-MAC.md`.

## File

| File | Isi |
|---|---|
| `rakfilm-latihan.mp4` | Video latihan penuh, 1920×1080, 30 fps. Narator Edge TTS (id-ID-Ardi) membacakan naskah; panel kanan = teks naskah (teleprompter) dan gelombang suara; label bagian dan pewaktu di atas |
| `rakfilm-latihan.mp3` | Audio saja, untuk didengar di jalan |
| `rakfilm-latihan.srt` | Subtitle (teks naskah per segmen), bisa dimuat di VLC |
| `bagian/*.mp4` | Potongan per bagian (1, 2, 3, 4, 5, 5b, 6, 6b, 7) untuk latihan satu bagian |
| `laporan-durasi.md` | Durasi aktual tiap bagian vs rencana naskah; dasar memangkas naskah |
| `prompt-claude-chrome.md` | Dua prompt untuk mengambil screenshot Langfuse dan Qdrant dengan Claude in Chrome |
| `screenshot/` | Taruh hasil screenshot di sini dengan nama sesuai daftar di prompt |
| `pipeline/` | Skrip dan bahan untuk merakit ulang (lihat bawah) |

## Screenshot Langfuse dan Qdrant

Versi pertama (9 Nov dini hari) memakai kartu placeholder; **versi kedua (9 Nov pagi)** sudah memakai screenshot asli dari Reiner (folder `screenshot/`, diambil lewat Google Drive). Versi pertama diarsipkan di `arsip/v1-placeholder/`. Pemetaan ke `pipeline/video/shots-real/`:

| Slot video | File sumber di `screenshot/` | Isi |
|---|---|---|
| langfuse-01-sessions | langfuse-01-sessions.png | Session `eval-edac5c-7` |
| langfuse-02-trace-tree | langfuse-02-trace-tree.png | Trace Tree, `rank_movies` → 8 film, 8,46 |
| langfuse-03-scores | langfuse-03-scores.png | Scores `user_feedback` |
| langfuse-04-prompt-supervisor | langfuse-04-prompt-supervisor.png | `movie-supervisor-system` v1 |
| langfuse-05-prompt-agent | langfuse-05-prompt-agent-v8.png | `movie-agent-system` v1–v9 |
| langfuse-06-trace-v9-miyazaki | langfuse-06-trace-v9-miyazaki.png | Trace v9 Miyazaki "4 film" (segmen cerita perbaikan) |
| qdrant-01-collection | qdrant-extra-041856.png | Daftar Collections: 1000 · 1536 · Cosine |
| qdrant-02-payload-index | qdrant-02-payload-index.png | payload_schema + Payload Indexes |
| qdrant-03-point-inception | qdrant-03-point-inception.png | Console `GET points/8` |
| qdrant-04-points | qdrant-extra-041943.png | Tab Points (segmen akses penilai) |

Tidak terpakai: `qdrant-01-collection.png` (JSON Info) dan `qdrant-extra-042021.png` (Graph). Kalau ingin mengganti gambar lagi: timpa file di `pipeline/video/shots-real/` (nama slot sama), lalu jalankan dari `pipeline/video/`:

```
python assemble.py
```

(`python` = Python base Anaconda yang punya Playwright; ffmpeg dan edge-tts ada di `pipeline/pylib`, tidak perlu instal apa pun.) Hanya segmen yang berubah perlu dirakit ulang, tapi menjalankan semuanya juga cuma ±6 menit.

## Kalau naskah diubah

1. Ubah teks di `pipeline/video/segments.py` (satu entri = satu potongan narasi + visual).
2. Hapus `pipeline/video/audio/<id>.mp3` untuk segmen yang teksnya berubah, lalu `python make_tts.py` (membuat ulang yang hilang saja).
3. `python assemble.py`.

Slide diubah di deck → `python render_slides.py`. Nomor baris kode berubah → ubah `CODE` di `segments.py`, lalu `python render_code.py`. Demo ingin direkam ulang → `python drive_demo.py` (±Rp150 OpenRouter, 3 menit).

## Catatan jujur

- Suara narator = Edge "Read Aloud" lewat paket `edge-tts` (tidak resmi, gratis). Untuk video pengumpulan, Anda sendiri yang bicara.
- Tampilan kode = editor Monaco (mesin editor VS Code) yang dirender dari file repo, bukan tangkapan jendela VS Code Anda.
- Klik 👍 di demo tidak terekam (tombolnya tidak ditemukan skrip), jadi di Langfuse tidak ada score baru dari sesi demo ini; score lama (23 dan 26 Okt) tetap ada.
