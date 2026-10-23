# Progress Capstone 3: IMDB Movie Assistant

> Deadline: **Senin, 10 November 2026, 23:59 WIB**. Target submit: **9 November**.
> Diperbarui setiap kali satu langkah selesai. Format tanggal: `(23 Okt)` = selesai tanggal itu.

## Fase 0 · Perencanaan (21–22 Okt)
- [x] Pilih kasus: IMDB Top 1000 (21 Okt)
- [x] EDA dataset: 1.000 baris, 16 kolom, masalah data dicatat (21 Okt)
- [x] Artifact arsitektur [Anatomi Capstone 3](https://claude.ai/artifact/MaBHfUY4FEzu43LUUX5mzr) (21–22 Okt)
- [x] Baca catatan Sesi 09–17, samakan pola kode dengan kelas (22 Okt)
- [x] Klarifikasi ke Pak Herman, jawaban di `keputusan-desain.md` (22 Okt)
- [x] Kritik diri rencana: 10 temuan, semuanya sudah diperbaiki (22 Okt)
- [x] Log keputusan desain `keputusan-desain.md` (22 Okt, terus diperbarui)

## Fase 1 · Setup dan data (22–23 Okt)
- [x] Akun Langfuse (EU), Qdrant Cloud, OpenRouter, dan key di `.env` (23 Okt)
- [x] `.env.example` di-commit, `.env` diabaikan git (23 Okt)
- [x] Conda env `capstone3` (Python 3.12) + `requirements.txt` terkunci (23 Okt)
- [x] `scripts/check_connections.py`: embedding, Qdrant, Langfuse semuanya OK (23 Okt)
- [x] `app/data.py`: `load_movies()`, `all_genres()`, `to_records()` (23 Okt)
- [x] `app/config.py` versi awal: `env()` + `get_embeddings()` (23 Okt)
- [x] `scripts/ingest.py`: 1.000 film masuk ke Qdrant, 1536 dimensi, Cosine, ±39 detik (23 Okt)
- [x] Uji pencarian: Inception urutan 1; filter Thriller 90-an 5/5 tepat (23 Okt)
- [x] Lihat sendiri collection `imdb_movies` di dashboard Qdrant (23 Okt)

## Fase 2 · Kerangka berjalan (24–25 Okt)
- [x] `app/config.py`: tambah `get_llm()` (23 Okt)
- [x] Pilih `LLM_MODEL`: `openai/gpt-4.1-mini` dari uji 6 model (23 Okt, K23)
- [x] `app/tools.py`: `search_movies` dengan enum 21 genre + filter tahun (23 Okt)
- [x] `app/agent.py`: `get_agent()` + `run_agent()`; memori percakapan terbukti jalan (23 Okt)
- [x] `streamlit_app.py`: chat history, tool call, dan usage token (23 Okt)
- [x] System prompt `movie-agent-system` v1 di UI Langfuse, label production (23 Okt)
- [x] Uji e2e dengan prompt asli: 3 pertanyaan dalam 1 session Langfuse (23 Okt)
- [x] Perbaikan: genre tidak lagi ditebak (K27) (23 Okt)
- [x] Jalankan `streamlit run streamlit_app.py` lokal dan coba 3 pertanyaan (23 Okt)
- [x] Cek session `e2e-langfuse-prompt-23okt` di Langfuse → Sessions (23 Okt)
- [x] Deploy pertama ke Streamlit Community Cloud, Python 3.12 (sama dengan lokal), Secrets lewat form; semua uji lolos (23 Okt)

## Fase 3 · Fitur lengkap (26–29 Okt)
- [x] `get_movie_details`: pencarian judul 4 lapis (K18, K30) (23 Okt)
- [x] `rank_movies`: filter, urutkan, hitung, filter seri film (K29, K30) (23 Okt)
- [x] UI: kartu poster untuk film yang disebut di jawaban (23 Okt)
- [x] Uji draf prompt v2: 12 skenario + 4 pertanyaan × 3 run, semuanya benar; pertanyaan lanjutan sekarang memakai tool (K31) (23 Okt)
- [ ] **Anda:** buat prompt `movie-agent-system` **v2** di UI Langfuse, label production
- [ ] Verifikasi v2 dari Langfuse + uji UI (poster) lokal, lalu push → Streamlit Cloud update otomatis

## Fase 4 · Uji dan dokumentasi (30 Okt – 1 Nov)
- [ ] Set uji 10 pertanyaan: semuanya lolos
- [ ] Set uji memeriksa otomatis: setiap query `search_movies` berbahasa Inggris (K26)
- [ ] Rapikan system prompt di Langfuse
- [ ] README: diagram alur, install, env, cara run, contoh query
- [ ] API key Qdrant **read-only** untuk penilai

## Fase 5 · Cadangan (2–5 Nov, Module 4 masih berjalan)
- [ ] Perbaikan dari hasil uji, kalau ada

## Fase 6 · Video (6–8 Nov)
- [ ] Naskah dari `penjelasan-kode.md` + set uji
- [ ] Uji rekam: kode terbaca jelas
- [ ] Rekam video 7–15 menit, wajah terlihat
- [ ] Upload ke Google Drive/YouTube, link publik

## Fase 7 · Pengumpulan (9 Nov)
- [ ] Cek riwayat git: tidak ada key yang pernah ter-commit
- [ ] Repo GitHub diubah jadi **public**
- [ ] App Streamlit diubah jadi **public** (Share → "public and searchable"); sebelumnya pasang credit limit di key OpenRouter
  - Sampai tahap ini app private. Kalau Pak Herman perlu melihat lebih awal: Share → Invite viewers → email beliau
- [ ] Isi Google Form: repo, video, app Streamlit, akses Qdrant
