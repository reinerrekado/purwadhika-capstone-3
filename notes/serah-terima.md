# Serah terima untuk sesi Claude Code baru

> Untuk Claude Code yang melanjutkan Capstone 3 Rakfilm di komputer lain (MacBook Reiner, mulai 10 Nov 2026) tanpa riwayat percakapan sebelumnya. Ditulis 9 Nov 2026 pagi oleh sesi Claude Code di laptop Windows Reiner. Tidak ada rahasia di file ini. Deadline pengumpulan: **Senin 10 Nov 2026, 23:59 WIB**.

## 0. Pesan pembuka yang dikirim Reiner

```
Lanjut Capstone 3 Rakfilm di Mac. Baca notes/serah-terima.md dulu dan ikuti bagian 6-nya,
lalu laporkan ringkas pemahamanmu dan tanyakan tugas hari ini. Deadline 10 Nov 23:59.
```

## 1. Siapa Reiner dan cara kerja yang sudah disepakati

- Reiner Rekado Bisara, peserta Purwadhika JCAIEH, mengerjakan Capstone Modul 3. Bahasa kerja: **Indonesia**. Ia belajar sambil membangun: **jelaskan setiap langkah** (apa yang dilakukan, kenapa, di file mana), bukan hanya hasil akhirnya.
- Istilah: definisikan dulu **agent = LLM + prompt + tool**; untuk arsitektur pakai hanya kata **supervisor** dan **sub-agent**, jangan sinonim lain.
- Prinsip membangun: sederhana, struktural, logis, efisien; di atas semuanya: **mengesankan**.
- Aturan dokumentasi (wajib setiap langkah): centang `notes/progress.md`; perluas `notes/penjelasan-kode.md` kalau kode berubah; setiap penyimpangan dari arahan tutor (Pak Herman) atau kode kelas dicatat di `notes/keputusan-desain.md` sebagai K-nomor berikutnya (sekarang sampai **K81**) dengan alasannya.
- **Commit dan push hanya kalau Reiner minta**; ia menyetujui per batch. Pesan commit berbahasa Indonesia, diakhiri baris `Co-Authored-By: Claude ... <noreply@anthropic.com>`.
- **Rahasia:** `.env` tidak pernah di-commit (sudah dicek ke seluruh riwayat, 0 temuan). Key Qdrant read-only hanya untuk Google Form, tidak untuk README.
- Semua prompt LLM ada di **Langfuse**, bukan di kode. Stack terkunci: Qdrant, Streamlit, Langfuse (ditambah OpenRouter, LangChain, LangGraph).
- Setelah push yang hanya mengubah kode, Streamlit Cloud sering **tidak ikut memperbarui**: minta Reiner menekan *Reboot app*, lalu verifikasi lewat trace Langfuse.
- Konfirmasi dulu untuk tindakan yang sulit dibatalkan (force push, hapus, tulis ulang riwayat). Saat mengganti hasil kerja (misalnya video), **duplikat versi lama sebagai arsip** dulu.
- Reiner suka laporan berbentuk artefak bertab (gaya "Anatomi") dan sudah terbiasa dengan tabel ringkas + alasan.

## 2. Proyek dalam satu halaman

- **Rakfilm**: asisten film agentic RAG di atas IMDB Top 1000 (1.000 film, 1920–2020). Repo publik: <https://github.com/reinerrekado/purwadhika-capstone-3>. App publik: <https://imdb-movie-assistant.streamlit.app>.
- **Arsitektur:** 1 supervisor (`langgraph-supervisor`, tool: 2 tombol oper + `forward_message`) + `rag_agent` (`search_movies`, `similar_movies`: Qdrant, reranker `qwen3-reranker-8b` memilih 5 dari 15) + `data_agent` (`get_movie_details`, `rank_movies`, `get_person_info`: pandas dan `data/people.csv`). LLM `openai/gpt-4.1-mini`, embedding `text-embedding-3-small` (1.536 dimensi), semuanya lewat OpenRouter. Qdrant Cloud cluster `Capstone-M3` (eu-west-2), collection `imdb_movies`, 1.000 point, Cosine, payload index `metadata.genres` (keyword) dan `metadata.year` (integer).
- **Prompt di Langfuse** (project "My Project", region EU): `movie-agent-system` v8 production (v9 staging, gagal uji 15/17, nama dipertahankan dari masa agent tunggal), `movie-supervisor-system` v1 production, `story-headline`, `overview-translator`, `bio-translator`. Tiap agent tertaut ke prompt-nya sendiri (K78).
- **Uji:** `python -m scripts.eval` menjalankan 17 pertanyaan / 116 pemeriksaan, terakhir **17/17** (7 Nov 17:09), laporan `notes/hasil-uji.md` (selalu ditimpa). Biaya ±Rp700 per putaran. Konvensi: gagal → ulang; perubahan perilaku → 3 putaran.
- **Angka penting:** 104 commit; 81 keputusan desain; 3.202 orang di `people.csv`; jawaban dua bahasa (`reply_language`); feedback jempol → score Langfuse `user_feedback` (baru 2 score, 23 dan 26 Okt); supervisor meneruskan dengan `forward_message` hanya 25%, sisanya menulis ulang, layar dijaga di kode.
- **Artefak di claude.ai:** laporan *Anatomi Capstone 3* (8 tab, versi 30) <https://claude.ai/artifact/MaBHfUY4FEzu43LUUX5mzr>; deck video *Rakfilm · Video* (19 slide, versi 15) <https://claude.ai/artifact/JiPx25xd1TqpwDXGJyHo1W>; kanvas desain *Rakfilm* <https://claude.ai/artifact/FBwNeeQQqrhBXnEywN4Tv6>.
- **Keterbatasan yang sudah diputuskan diterima** (jangan diperbaiki diam-diam; sebut sebagai keterbatasan): pertanyaan agregat per kelompok ("genre rata-rata tertinggi") salah (Drama vs War); "ceritakan film Parasite" ±1 dari 6 dioper ke `rag_agent`; pertanyaan lintas domain hanya memanggil satu sub-agent; supervisor lebih sering menulis ulang daripada meneruskan.

## 3. Peta file

| Lokasi | Isi |
|---|---|
| `streamlit_app.py` | UI: chat, kartu poster, panel film/orang, expander tool call (rute supervisor), feedback, IG story |
| `app/agent.py` | `_build_agent`, `get_agent`, `stream_agent`, `send_feedback`, `trim_offer`, `reply_language` |
| `app/tools.py`, `app/rerank.py` | lima tool + reranker; `OptionalGenre`, `_fix_role` (K80, K81) |
| `app/data.py`, `app/movie_cards.py`, `app/story.py`, `app/quota.py`, `app/config.py` | data, komponen UI, IG story, pembatas pemakaian, konfigurasi |
| `scripts/` | `ingest.py`, `eval.py`, `check_connections.py`, `fetch_people.py`, `translate_*.py`, `check_readonly_key.py`, `make_logo.py` |
| `notes/progress.md` | log kerja + daftar tugas (sumber kebenaran status) |
| `notes/keputusan-desain.md` | K01–K81, alasan tiap keputusan |
| `notes/penjelasan-kode.md` | penjelasan per fungsi + tanya-jawab |
| `notes/hasil-uji.md`, `notes/prinsip-kerja.md` | laporan uji terakhir; prinsip kerja yang bisa dipakai ulang |
| `docs/img/` | 5 screenshot README (yang `jawaban-tool-call.png` diperbarui 9 Nov) |
| `video-latihan/` (**ikut git sejak 9 Nov siang**, supaya bisa di-pull di Mac) | video latihan v2 (`rakfilm-latihan.mp4`, 92 MB) + MP3 + SRT, `naskah-video.md`, `rangka/` (PNG rangka), `screenshot/` (Langfuse, Qdrant), `pipeline/` (skrip rakit video + hasil render), `claude-memory/` (salinan memori Claude), `CARA-PAKAI.md`, `LANJUT-DI-MAC.md`, `prompt-claude-chrome.md`, `laporan-durasi.md` |
| **Tidak di git** | `.env`, `video-latihan/arsip/` (v1), `video-latihan/bagian/` (potongan per bagian): ketiganya ada di Google Drive Reiner › Video Untuk Capstone 3 (`.env` di akar folder itu, dua folder video di `video-latihan-tambahan/`). `video-latihan/pipeline/pylib/` (paket Python Windows) dan `pipeline/video/seg/` (klip antara) tidak disalin, dibuat ulang oleh `pip install` + `assemble.py` |

## 4. Status per 9 Nov 2026 siang

**Selesai:** app publik dengan arsitektur supervisor; set uji 17/17; README; laporan Anatomi; deck video 19 slide; naskah video (±14:15 rencana); video latihan bernarasi TTS dengan screenshot asli Langfuse dan Qdrant; panduan pindah ke Mac; `video-latihan/` masuk git (9 Nov siang) karena clone pertama di Mac tidak membawanya.

**Belum, milik Reiner:** rekam video 7–15 menit (wajah terlihat, kode terbaca); unggah (YouTube/Drive publik); isi Google Form (repo, video, app, URL Qdrant + key read-only) sebelum 10 Nov 23:59; naikkan batas key OpenRouter (sisa ±$1,6 dari $5 per 9 Nov); bangunkan app sebelum merekam dan sebelum mengumpulkan (tidur ±12 jam); kabari Pak Herman bahwa arsitektur sekarang supervisor; pastikan cluster Qdrant aktif (free tier nonaktif setelah 1 minggu tanpa pemakaian).

**Menunggu keputusan Reiner:**
1. **Pangkas naskah ±4 menit.** Video latihan membaca naskah penuh = 18:15, batas 15:00. Usulan: §6 kode satu kalimat per baris dan gabungkan baris (−2:00); §3 buang daftar masalah data di langkah 1 dan kalimat Wikipedia di langkah 2 (−0:45); §4 langkah 7 satu kalimat, ringkasan langkah 8 dihapus (−0:35); §5b cerita perbaikan dipadatkan (−0:25). Kalau disetujui: ubah `video-latihan/naskah-video.md`, catatan pembicara deck, dan `video-latihan/pipeline/video/segments.py`, lalu rakit ulang.
2. ~~Bersihkan riwayat git dari naskah dan PNG rangka~~ — **tidak relevan lagi**: 9 Nov siang Reiner memutuskan memasukkan `video-latihan/` (termasuk naskah) ke git supaya bisa di-pull di Mac. Jangan tawarkan lagi kecuali ia berubah pikiran.
3. Memindahkan catatan tool (`SCENE_NOTE`, `ENGLISH_ONLY`, `NOT_FOUND_HINT`, "(Reply in English.)") ke satu prompt Langfuse: tertunda sejak 25 Okt, Reiner condong ke pilihan B.

## 5. Hal teknis yang menghemat waktu

- **Setup Mac:** ikuti `video-latihan/LANJUT-DI-MAC.md`. Python 3.12, `pip install -r requirements.txt`. `.env` disalin dari OneDrive atau diisi dari `.env.example`: `OPENROUTER_API_KEY`, `LLM_MODEL`, `EMBEDDING_MODEL`, `RERANK_MODEL`, `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION`, `QDRANT_READONLY_API_KEY` (opsional), `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST=https://cloud.langfuse.com`. Cek: `python -m scripts.check_connections`.
- **Langfuse SDK v5:** `client.api.observations.get_many(trace_id=..., cursor=...)`, `client.api.scores.get_many(name=...)`, `client.api.prompts.list()`; output observasi berupa string JSON. Tautan prompt per agent lewat `with_config({"metadata": {"langfuse_prompt": prompt}})`, dan config run tidak boleh membawa `langfuse_prompt`.
- **Tab Graph Langfuse** menggabungkan tiga graf; untuk urutan kerja pakai tab **Tree**.
- **Pipeline video** (`video-latihan/pipeline/video/`): `segments.py` (daftar segmen: visual + narasi), `make_tts.py` (Edge TTS id-ID-Ardi, hanya membuat mp3 yang belum ada), `render_slides.py`, `render_code.py` (tampilan VS Code via Monaco), `render_shots.py`, `drive_demo.py` (rekam app publik, ±Rp150), `assemble.py` (ffmpeg → `video-latihan/rakfilm-latihan.mp4`, MP3, SRT, potongan per bagian, `laporan-durasi.md`). Sudah memilih browser dan font menurut OS; di Mac: `pip install playwright edge-tts imageio-ffmpeg && playwright install chromium`. Screenshot asli ada di `pipeline/video/shots-real/`.
- **DOM app** (untuk Playwright): kartu poster = komponen v2 `button.card[aria-label="Buka detail <judul>"]`; tombol contoh = `st.button` berlabel teks contoh; `st.feedback` jempol belum berhasil diklik otomatis.
- **Deck slide** adalah artefak tipe Slides: ubah file `project/slides/<id>.html`, publish dengan `root`; `alur.html` pernah tersimpan ulang dari editor, jadi baca versi live dulu sebelum menimpa.

## 6. Cara memulai sesi ini (untuk Claude)

1. Baca file ini, lalu `notes/progress.md` (fokus Fase 6–7 dan daftar "Menunggu"), `notes/keputusan-desain.md` K75–K81, dan `video-latihan/CARA-PAKAI.md` + `video-latihan/LANJUT-DI-MAC.md` (ikut clone).
2. Simpan isi `video-latihan/claude-memory/` sebagai memori proyek (file `MEMORY.md` adalah indeksnya).
3. Laporkan ke Reiner dalam ±10 baris: status, tugas hari ini yang kamu pahami, dan dua keputusan yang masih menunggu (pangkas naskah ±4 menit; catatan tool ke Langfuse). Tanyakan mana yang mau dikerjakan dulu. **Jangan** memulai pekerjaan besar, commit, atau force push tanpa persetujuan.
4. Selama bekerja: jelaskan setiap langkah; centang `progress.md` setelah tiap langkah; catat penyimpangan di `keputusan-desain.md`; arsipkan versi lama sebelum menimpa.
