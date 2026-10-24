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
  - URL: https://imdb-movie-assistant.streamlit.app (private sampai Fase 7)

## Fase 3 · Fitur lengkap (26–29 Okt)
- [x] `get_movie_details`: pencarian judul 4 lapis (K18, K30) (23 Okt)
- [x] `rank_movies`: filter, urutkan, hitung, filter seri film (K29, K30) (23 Okt)
- [x] UI: kartu poster untuk film yang disebut di jawaban (23 Okt)
- [x] Uji draf prompt v2: 12 skenario + 4 pertanyaan × 3 run, semuanya benar; pertanyaan lanjutan sekarang memakai tool (K31) (23 Okt)
- [x] Prompt `movie-agent-system` **v2** di UI Langfuse, label production (23 Okt)
- [x] Fase 3 di-push, Streamlit Cloud update otomatis; poster + 3 tool dicoba di app Cloud, semuanya benar (23 Okt, masih prompt v1)
- [x] Verifikasi v2: teks dari Langfuse = draf teruji; uji e2e session `e2e-prompt-v2-23okt`, 2 pertanyaan lanjutan memakai `get_movie_details` (23 Okt)

- [x] Uji manual Reiner di app Cloud: 15 pertanyaan, 11 benar + 4 temuan (Parasite, Drishyam, Spirited Away, poster rusak) (23 Okt)
- [x] Perbaikan temuan: hint not_found, docstring query, poster 404 → kotak placeholder, urutan poster "Judul (tahun)"; draf prompt v3 diuji 6 kasus × 5 run, semuanya benar (24 Okt, K32–K33)
- [x] Prompt `movie-agent-system` **v3** di UI Langfuse, label production (24 Okt)
- [x] Verifikasi v3: teks dari Langfuse = draf teruji (24 Okt)

- [x] Fitur tambahan (K34–K38): tool `similar_movies`, feedback 👍/👎 → Langfuse score, sidebar (contoh, percakapan baru, token + biaya), link "Tonton di mana?" (JustWatch), jawaban streaming; prompt di-cache per teks, jadi versi baru terpakai tanpa restart (24 Okt)
- [x] Masukan Reiner: biaya Rp + USD dengan kurs harian ECB; contoh di sidebar diganti tombol "Cari yang mirip" di bawah poster (24 Okt, K39–K40)
- [x] Masukan Reiner: grid poster ala Netflix (2:3 di-crop, gelap + ikon saat disorot, klik → panel detail); "Cari yang mirip" pindah ke panel detail (24 Okt, K41)
- [x] Sinopsis 1.000 film diterjemahkan offline + diperiksa (24 Okt, K42)
- [x] Panel detail: Fakta menarik + chip sutradara/pemain (24 Okt, K43)
- [x] Kartu film langsung di dalam jawaban, tanpa batas 5 film (24 Okt, K44)
- [x] "Muat 5 film lagi" langsung dari UI dengan offset Qdrant, tanpa LLM (24 Okt, K45)
- [x] **Anda:** coba kartu + panel detail + Muat lebih banyak di app Cloud
- [x] IG story "Watchlist minggu ini": R&D 3 arah visual di artifact → Reiner pilih C (Pita Film) → Pillow + headline LLM/aturan (24 Okt, K46)
- [x] Daftar lengkap (Nolan 8/8) + "Muat lebih banyak" untuk rank_movies; draf prompt v5 diuji (24 Okt, K47)
- [x] Prompt v4 terpasang dan terverifikasi (24 Okt)
- [x] Tema story per genre (10 tema + Campur pita warna-warni), otomatis + manual, kontras WCAG lolos; R&D 11 story di artifact (24 Okt, K48)
- [x] Review tema per genre: Reiner puas (24 Okt)
- [x] Prompt v5 terpasang dan terverifikasi (24 Okt)
- [x] Genre saja → rank_movies (urut rating), ada deskripsi → search_movies; 24/24 tepat (24 Okt, K49)
- [x] Nama app **Rakfilm** + logo (24 Okt, K50)
- [x] UI baru: mockup 8 layar di artifact, review anti-AI-generic, diterapkan (tema terang/gelap, sidebar Rak kamu, tampilan awal dinding poster, panel detail imersif, panel story) (24 Okt, K51)
- [x] Hover poster ala Netflix, kartu kaca hasil teratas, label "Muat N film lagi" sesuai sisa, mode terang putih tulang (24 Okt, K52)
- [x] Logo Rakfilm di IG story, satu warna mengikuti tema (24 Okt, K53)
- [x] Latar kaca jadi efek hover di semua kartu hasil (ide latar halaman dibatalkan karena butuh CSS internal Streamlit) (24 Okt, K54)
- [x] Audit: 9 jenis pertanyaan lolos, koneksi + prompt + riwayat git aman; `.devcontainer/` dihapus (24 Okt, K55)
- [ ] **Anda:** pasang prompt `movie-agent-system` **v6** di UI Langfuse, label production (K55)
- [ ] **Anda:** coba UI baru di app Cloud (mode gelap dan terang, laptop dan HP)
- [x] **Anda:** coba watchlist + Buat IG story di app Cloud, unduh PNG-nya
- [x] **Anda:** buat prompt `movie-agent-system` **v4** di UI Langfuse, label production
- [x] Verifikasi v4 + coba fitur baru di app Cloud

## Fase 4 · Uji dan dokumentasi (30 Okt – 1 Nov)
- [ ] Set uji 10 pertanyaan: semuanya lolos
- [ ] Set uji memeriksa otomatis: setiap query `search_movies` berbahasa Inggris (K26)
- [ ] Rapikan system prompt di Langfuse
- [x] README: diagram alur, install, env, cara run, contoh query (24 Okt, K56)
- [x] Expander tool call menampilkan dokumen yang di-retrieve + skor kemiripan (syarat wajib: tool call dan dokumen yang dipakai) (24 Okt, K57)
- [x] Reranker (qwen3-reranker-8b via OpenRouter) untuk `search_movies`: 15 kandidat → 5 terbaik, bonus poin (24 Okt, K58)
- [x] Pertanyaan adegan/kutipan: parameter `describes_scene` + catatan di hasil tool, agent jujur "hanya cocok dari sinopsis" (24 Okt, K59)
- [x] Prompt `movie-agent-system` **v7** terpasang (24 Okt)
- [ ] README: tambahkan 2-3 screenshot Rakfilm (dari pengguna)
- [x] Repo dirapikan: `docs/anatomi-capstone-3.html` dan `Dataset Description.docx` dihapus, isinya pindah ke README (24 Okt, K56)
- [ ] API key Qdrant **read-only** untuk penilai

## Fase 5 · Cadangan (2–5 Nov, Module 4 masih berjalan)
- [ ] Perbaikan dari hasil uji, kalau ada. **Catatan UI untuk dikerjakan nanti** (dari uji PDF 24 Okt, dicatat saja, belum diubah):
  - [ ] Tombol "Muat lebih banyak" / "Muat N film lagi" dibuat lebih jelas bisa diklik (permintaan Reiner): sekarang hanya teks polos tanpa tanda tombol
  - [ ] Kartu tunggal di tata letak grid terlalu sempit: judul terpotong ("Interstell", "Star Wars:…") dan "2014 · ★ 8.6" terpecah dua baris. Kolom grid perlu lebar minimum
  - [ ] Argumen tool call terpotong di kanan expander (`search_movies(query='film tentang…`), padahal argumen informasi terpenting. Pakai `st.code(..., wrap_lines=True)`
  - [ ] Jawaban tanpa tool (di luar topik) menampilkan expander "0 tool call" kosong. Sembunyikan atau beri teks "Tidak ada tool yang dipanggil"
  - [ ] Jawaban tanpa kartu kalau judul tidak ditulis persis "Judul (tahun)": "Parasite (judul asli Gisaengchung, 2019)" tidak cocok dengan pola `Gisaengchung (2019)`, jadi tidak ada poster sama sekali. Perlu cadangan: kalau tidak ada judul yang cocok, tampilkan film hasil tool sebagai grid
  - [ ] Label "Muat 5 film lagi" muncul setelah pertanyaan superlatif tunggal ("yang mana paling lama?"), kurang relevan
  - [ ] Cek sekali di layar (bukan PDF): kartu The Dark Knight Rises tampak menimpa kalimat penutup di PDF. Kemungkinan hanya artefak cetak
  - Bukan UI, ditangani lewat set uji `scripts/eval.py`:
    - Query `search_movies` masih berbahasa Indonesia di uji pertama ("film tentang pencuri…"), melanggar K26
    - Pertanyaan adegan tangga masih dijawab "Film dengan adegan pria menari di tangga yang terkenal adalah All That Jazz". Cek apakah K59 sudah ter-deploy (reboot app), lalu ulang
    - Jawaban penolakan ditutup dengan pertanyaan ("Ada hal lain…?"), melanggar aturan 6 prompt

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

