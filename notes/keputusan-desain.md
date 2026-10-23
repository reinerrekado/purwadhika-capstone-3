# Keputusan Desain: Di Mana Kita Berbeda dari Kelas, dan Kenapa

> Catatan hidup, diperbarui setiap kali ada keputusan baru. Dipakai sebagai bahan menjawab "kenapa begini?" di video dan saat penilaian.

## Cara membaca

Setiap keputusan dibandingkan dengan dua hal:

- **Arahan**: aturan yang diucapkan atau ditulis Pak Herman (stack wajib, prompt di Langfuse, kode modular, UI wajib, deploy, dan sebagainya). **Melawan arahan hanya boleh dengan alasan kuat dan harus dikonfirmasi dulu.**
- **Contoh kelas**: kode di slide dan notebook (misalnya `main.py` Sesi 14). Contoh bukan aturan. Berbeda dari contoh itu wajar dalam engineering, asal alasannya jelas.

Status yang dipakai:

| Status | Arti |
|---|---|
| ✅ Sesuai arahan | Mengikuti arahan Pak Herman |
| 🔁 Beda dari contoh | Tidak melawan arahan, hanya berbeda dari kode contoh kelas |
| 💬 Dikonfirmasi | Sudah ditanyakan ke Pak Herman (22 Oktober 2026) |

**Ringkasan per 22 Oktober 2026: tidak ada keputusan yang melawan arahan.**

## Klarifikasi Pak Herman (22 Oktober 2026)

Jawaban langsung Pak Herman, yang menjadi dasar status 💬 di bawah.

| Topik | Jawaban Pak Herman | Keputusan |
|---|---|---|
| Qdrant lewat LangChain atau langsung | Bebas | `langchain_qdrant` (pola kelas) |
| Filter metadata di pencarian | Boleh | Dipakai (K04) |
| Akses Qdrant untuk penilaian | Intinya harus bisa dilihat Pak Herman | URL + API key read-only, dan dashboard ditunjukkan di video |
| Langfuse versi berapa | Yang mana saja yang works, dijalankan di VS Code | v5 dengan pola Sesi 17 (K02, K20) |
| Prompt apa saja di Langfuse | Cukup di Langfuse, yang praktis | Hanya system prompt (K03) |
| Prompt dibuat lewat kode atau UI | Cukup UI | UI |
| Trace per pertanyaan atau per session | Keduanya boleh | Per pertanyaan, dikelompokkan per session |
| Chat history | Intinya tiap sesi | Agent ingat percakapan selama satu sesi (K07) |
| Cara agent ingat | Yang ringan, tidak menyulitkan | Kirim seluruh riwayat, tanpa checkpointer |
| Chat history, tool call, usage | **Wajib semua** | Ketiganya tampil di UI |
| Deploy | **Wajib** Streamlit | Streamlit Community Cloud |
| Chunking | Terserah | Tanpa chunking (K08) |
| Dataset di repo publik | Publik saja | CSV ikut di-commit |
| Kelas OpenRouter di LangChain | Terserah | `ChatOpenAI` + `base_url` (K10) |

---

## Daftar keputusan

### K01 · Membuat agent dengan `create_agent`
- **Kelas:** slide 22 Sesi 10 menyebut `create_react_agent` (`langgraph.prebuilt`); slide 37 dan notebook Sesi 10 memakai `create_agent` (`langchain.agents`).
- **Kita:** `create_agent`.
- **Alasan:** `create_react_agent` sudah *deprecated* sejak LangGraph 1.0. Keduanya membangun graf ReAct yang sama. Kita mengikuti notebook, bukan slide yang tertinggal.
- **Status:** ✅ Sesuai arahan (notebook kelas)

### K02 · Langfuse versi 3
- **Kelas:** slide 26–28 Sesi 17 memakai gaya v2 (`Langfuse()`, `CallbackHandler(session_id=...)`); notebook memakai v3.
- **Kita:** v3: `get_client()`, `CallbackHandler()` tanpa argumen, session lewat `config["metadata"]["langfuse_session_id"]`.
- **Alasan:** `pip install langfuse` saat ini memasang v3, dan argumen gaya v2 sudah tidak diterima.
- **Status:** 💬 Dikonfirmasi ("yang mana saja yang works")

### K03 · Hanya system prompt yang disimpan di Langfuse, dibuat lewat UI
- **Arahan:** semua prompt di Langfuse, tidak ada hardcode.
- **Kita:** system prompt agent di Langfuse, dibuat lewat UI. Docstring tool tetap di kode.
- **Alasan:** docstring adalah bagian dari definisi fungsi (dibaca LangChain untuk membuat skema tool), bukan prompt terpisah. Memindahkannya ke Langfuse menambah kerumitan tanpa manfaat.
- **Status:** 💬 Dikonfirmasi ("cukup di Langfuse, yang praktis"; "cukup UI")

### K04 · Filter metadata di pencarian Qdrant
- **Kelas:** `qdrant.similarity_search(query, k=10)` tanpa filter (Sesi 14).
- **Kita:** `similarity_search(query, k=5, filter=...)` dengan filter genre dan rentang tahun.
- **Alasan:** pertanyaan seperti "thriller tahun 90-an" punya syarat pasti. Vektor mencari makna, filter menjamin syaratnya terpenuhi. Tanpa filter, film drama tahun 2010 bisa ikut muncul hanya karena ceritanya mirip.
- **Bukti (23 Okt, Qdrant):** query "great thriller from the 90s" **tanpa filter** menghasilkan 3 dari 5 film yang bukan dari tahun 90-an (Cape Fear 1962, Strangers on a Train 1951, Wait Until Dark 1967), karena vektor tidak memahami tahun. **Dengan filter** Thriller + 1990–1999, kelimanya tepat: Misery, Lost Highway, Funny Games, Heat, The Usual Suspects.
- **Status:** 💬 Dikonfirmasi ("boleh saja")

### K05 · Jumlah hasil pencarian `k=5`
- **Kelas:** `k=10`.
- **Kita:** `k=5`.
- **Alasan:** 5 film sudah cukup untuk satu rekomendasi, dan filter sudah mempersempit kandidat. Hasil tool ikut dikirim ke LLM sebagai input, jadi lebih sedikit hasil berarti lebih sedikit token.
- **Status:** 🔁 Beda dari contoh

### K06 · Output tool berupa JSON metadata
- **Kelas:** tool mengembalikan list `page_content` (teks saja), Sesi 14.
- **Kita:** tool mengembalikan JSON berisi metadata film (judul, tahun, genre, rating, sutradara, poster, overview).
- **Alasan:**
  1. LLM langsung mendapat fakta terstruktur (tahun, rating), tidak perlu menebak dari teks.
  2. UI membuat kartu poster dari data tool, bukan dari teks jawaban LLM. Jadi kartu hanya berisi film yang benar-benar ada di dataset, dan film karangan tidak bisa tampil.
- **Status:** 🔁 Beda dari contoh. Tidak ada arahan tentang format output tool.

### K07 · Agent ingat percakapan dengan mengirim seluruh riwayat
- **Kelas:** `main.py` Sesi 14 hanya mengirim pesan terakhir, sehingga agent tidak ingat percakapan.
- **Kita:** seluruh `st.session_state.messages` (teks user dan jawaban akhir) dikirim setiap kali bertanya. Tanpa checkpointer.
- **Alasan:** pertanyaan lanjutan ("yang kedua tadi siapa sutradaranya?") harus bisa dijawab. Mengirim riwayat adalah cara paling ringan. Output tool tidak ikut disimpan, jadi riwayat tetap kecil.
- **Status:** 💬 Dikonfirmasi ("tiap sesi", "yang ringan")

### K08 · Tanpa chunking
- **Kelas:** Sesi 13 mengajarkan chunking dengan text splitter.
- **Kita:** 1 film = 1 Document = 1 vektor.
- **Alasan:** overview terpanjang 313 karakter (56 kata), jauh di bawah batas input model embedding (8.192 token). Memotongnya justru memisahkan kalimat yang saling melengkapi.
- **Status:** 💬 Dikonfirmasi ("terserah")

### K09 · Tanpa reranker
- **Kelas:** Sesi 13–14 mengajarkan reranker (cross-encoder dan LLM as reranker), sebagai opsi.
- **Kita:** tidak dipakai.
- **Alasan:** filter metadata dan `k=5` sudah menghasilkan kandidat yang tepat. Reranker menambah satu panggilan model per pencarian. Kalau set uji #1–2 gagal, reranker dipertimbangkan lagi.
- **Status:** ✅ Sesuai arahan ("reranker bukan hal wajib")

### K10 · OpenRouter lewat `ChatOpenAI` + `base_url`
- **Kelas:** Sesi 09 menyebut "install integrasi OpenRouter, lalu ganti kelasnya". Sesi 06 mendemokan OpenRouter dengan library `openai` dan mengganti `base_url`.
- **Kita:** `ChatOpenAI(base_url="https://openrouter.ai/api/v1", ...)`.
- **Alasan:** cara yang sama dengan demo Sesi 06, tanpa library tambahan. Satu library (`langchain-openai`) dipakai untuk LLM dan embedding.
- **Status:** 💬 Dikonfirmasi ("terserah")

### K11 · Embedding `text-embedding-3-small` lewat OpenRouter
- **Kelas:** `OpenAIEmbeddings(model="text-embedding-3-small")` langsung ke OpenAI (Sesi 12).
- **Kita:** model yang sama, lewat OpenRouter:
  ```python
  OpenAIEmbeddings(
      model="openai/text-embedding-3-small",
      base_url="https://openrouter.ai/api/v1",
      api_key=OPENROUTER_API_KEY,
      check_embedding_ctx_length=False,
  )
  ```
- **Alasan:** lihat bagian [Pemilihan embedding](#pemilihan-embedding) di bawah.
- **Status:** 🔁 Beda dari contoh (modelnya sama, jalurnya berbeda)
- **Terbukti (23 Okt, `scripts/check_connections.py`):** vektor 1536 dimensi; query "a thief who enters people's dreams" paling mirip dengan overview Inception (0,588), jauh di atas The Prestige (0,226) dan Interstellar (0,211).

### K12 · Query pencarian ditulis LLM dalam bahasa Inggris
- **Kelas:** pertanyaan user langsung dipakai sebagai query.
- **Kita:** docstring `search_movies` meminta LLM menulis argumen `query` sebagai deskripsi singkat dalam bahasa Inggris.
- **Alasan:** semua overview IMDB berbahasa Inggris, sedangkan user bertanya dalam bahasa Indonesia. Kemiripan vektor paling tinggi kalau query dan dokumen memakai bahasa yang sama. LLM sudah membaca pertanyaannya, jadi menerjemahkan tidak menambah panggilan model.
- **Bukti (23 Okt, `text-embedding-3-small`):**

  | Query | Cosine ke film yang benar |
  |---|---|
  | "pencuri yang masuk ke mimpi orang" | Inception 0,390 |
  | "a thief who enters people's dreams" | Inception **0,588** |
  | "film luar angkasa tentang menyelamatkan umat manusia" | Interstellar 0,363 |
  | "space movie about saving humanity" | Interstellar **0,526** |

  Query bahasa Inggris memberi skor ±45–50% lebih tinggi. Query bahasa Indonesia tetap menemukan film yang benar, tapi selisihnya dengan film lain lebih tipis, jadi lebih rawan salah urut.
- **Status:** 🔁 Beda dari contoh

### K13 · Yang di-embed: `judul. genre. overview`
- **Kelas:** `page_content` berisi teks deskripsi produk (Sesi 12).
- **Kita:** judul, genre, dan overview. Sutradara dan aktor disimpan di metadata, tidak di-embed.
- **Alasan:** pertanyaan "film Nolan" butuh kecocokan nama yang persis, dan itu dijawab filter di `rank_movies`. Kemiripan makna tidak cocok untuk nama orang.
- **Status:** 🔁 Beda dari contoh

### K14 · Kode modular dalam 6 file
- **Kelas:** `main.py` Sesi 14 menaruh semuanya dalam satu file.
- **Kita:** `config.py`, `data.py`, `tools.py`, `agent.py`, `streamlit_app.py`, `scripts/ingest.py`.
- **Alasan:** arahan Pak Herman di kelas exercise: file Streamlit hanya untuk front end, dan agent ada di file terpisah. Bonusnya, agent dibuat sekali saat modul di-import, tidak dibangun ulang setiap kali Streamlit rerun.
- **Status:** ✅ Sesuai arahan

### K15 · Membaca `.env` tanpa `except:` kosong
- **Kelas:** `main.py` memakai `try/except:` kosong. Kalau ada variabel yang hilang, cabang `except` ikut error (`StreamlitDuplicateElementId`).
- **Kita:** satu `config.py` yang membaca `os.getenv`, dan langsung menampilkan pesan jelas kalau ada variabel yang kosong.
- **Alasan:** kesalahan konfigurasi langsung terlihat penyebabnya. `os.getenv` juga bekerja di Streamlit Cloud, karena secret tingkat atas tersedia sebagai variabel lingkungan.
- **Status:** 🔁 Beda dari contoh

### K16 · Role pesan `user`/`assistant`
- **Kelas:** `main.py` menyimpan role "Human"/"AI".
- **Kita:** `user`/`assistant`.
- **Alasan:** riwayat dikirim ulang ke agent (K07), dan format pesan LangChain mengenali `user`/`assistant`.
- **Status:** 🔁 Beda dari contoh

### K17 · Tiga tool, bukan lima
- **Kelas:** tidak ada contoh untuk kasus ini.
- **Kita:** `search_movies`, `get_movie_details`, `rank_movies`. Perbandingan film memakai `get_movie_details` dengan beberapa judul sekaligus.
- **Alasan:** tool yang tumpang-tindih membuat LLM ragu memilih dan menambah bahan penjelasan di video.
- **Status:** ✅ Tidak ada arahan yang terkait

### K18 · Pencarian judul tahan huruf besar-kecil, typo, dan judul asli (lapis 1–2 direvisi di K30)
- **Kelas:** tidak ada contoh pencarian judul.
- **Kita:** `get_movie_details` mencocokkan judul dalam 4 lapis, dari yang paling ketat:
  1. **Normalisasi**: huruf kecil, aksen dihapus (`Amélie` → `amelie`), tanda baca jadi spasi (`WALL·E` → `wall e`), angka Romawi diseragamkan (`Part II` → `part 2`). Lalu dicari yang **persis sama**.
  2. **Sebagian judul**: kata-kata query ada di judul (`shawshank` → *The Shawshank Redemption*; `dark knight` → 2 film).
  3. **Typo per kata**: setiap kata query dicocokkan ke kata judul dengan `difflib.get_close_matches` (cutoff 0,8), yaitu library bawaan Python (`harry poter`, `the matrx`, `dark night`).
  4. **Tidak ketemu**: mengembalikan 3 judul termirip, ditambah petunjuk agar agent mencoba `search_movies` dengan deskripsi plot.
  Setiap hasil membawa label `match` (`exact`, `partial`, `fuzzy`, `not_found`), sehingga agent bisa bertanya "Maksud Anda *Interstellar*?" atau meminta user memilih kalau hasilnya lebih dari satu.
- **Alasan:**
  - Lapis 1–3 menangani typo tanpa library tambahan.
  - Lapis 4 menangani karakter dataset: film non-Inggris memakai **judul asli** (*Parasite* = `Gisaengchung`, *Spirited Away* = `Sen to Chihiro no kamikakushi`). Pencocokan teks tidak bisa menebaknya. Agent cukup mencari dari plotnya lewat RAG, sehingga dua tool saling melengkapi.
  - LLM biasanya sudah memperbaiki typo sebelum memanggil tool. Kode tetap menjaga kalau LLM melewatkannya.
- **Uji lapis 4 (23 Okt, Qdrant):** pencarian lewat plot berhasil memasukkan film yang benar ke 5 besar, tapi **belum tentu di urutan pertama**. *Parasite* → Gisaengchung di urutan 1 dengan selisih tipis (0,370 vs 0,368). *Spirited Away* → Sen to Chihiro di urutan 2, kalah dari Kurenai no buta (Porco Rosso) karena kata "pigs". Karena itu, petunjuk `not_found` meminta agent **lebih dulu memakai fakta yang ia tahu** (sutradara atau tahun, lewat `rank_movies`; misalnya Bong Joon Ho, 2019), lalu memakai plot sebagai jalan terakhir. Agent juga melihat 5 hasil lengkap dengan tahun dan sutradaranya (K06), sehingga bisa memilih yang cocok.
- **Bukti (diuji pada dataset, 22 Okt):** `INCEPTION`, `Incepton`, `interstelar`, `the godfater`, `shawshank`, `lord of the rings`, `amelie`, `wall-e`, `harry poter`, `the matrx`, dan `dark night` semuanya ketemu. Yang gagal tanpa lapis 4: `parasite` dan `spirited away` (judul asli), serta `godfathr part 2` (angka Romawi; diatasi normalisasi di lapis 1).
- **Status:** ✅ Tidak ada arahan yang terkait

### K19 · Conda env Python 3.12 + `requirements.txt`, bukan Poetry
- **Kelas:** demo live Sesi 14 memakai Poetry (`poetry run streamlit run ...`); `main.py` Sesi 14 memakai `requirements.txt` + `pip install -r`.
- **Kita:** conda env `capstone3` (Python 3.12.13) + `requirements.txt` dengan versi dikunci.
- **Alasan:** Anaconda sudah terpasang dan Poetry belum. Python bawaan laptop adalah 3.14, yang terlalu baru dan berisiko belum didukung library. Streamlit Community Cloud langsung membaca `requirements.txt`. Versi dikunci supaya laptop dan cloud memasang library yang sama persis (Pak Herman di Sesi 09: masalah terbesar LangChain adalah "bentrok versi antar library").
- **Status:** 🔁 Beda dari contoh (sama dengan `main.py` Sesi 14, beda dari demo live)

### K20 · Langfuse 5.0.4, dengan pola kode Sesi 17
- **Kelas:** notebook Sesi 17 memakai Langfuse v3.
- **Kita:** `pip install langfuse` saat ini memasang **5.0.4**. Pola kelas tetap dipakai apa adanya.
- **Alasan:** diperiksa 23 Okt: `get_client()`, `CallbackHandler()` (semua argumen opsional), `get_prompt`, `auth_check`, dan `flush` masih ada, dan `auth_check()` berhasil ke `https://cloud.langfuse.com`. Cara mengirim `langfuse_session_id` lewat metadata akan dibuktikan saat trace pertama muncul.
- **Status:** 💬 Sesuai jawaban Pak Herman ("yang mana saja yang works")

### K21 · ID point = nomor baris, dan collection dibuat ulang setiap ingest
- **Kelas:** notebook Sesi 12 membuat id acak dengan `uuid4()`.
- **Kita:** `ids=[id film]` (nomor baris 0–999) dan `force_recreate=True`.
- **Alasan:** dengan id acak, menjalankan ingest dua kali akan **menggandakan** data (2.000 point). Dengan id tetap dan pembuatan ulang, hasilnya selalu 1.000 point. Sudah terbukti: ingest dijalankan dua kali pada 23 Okt, dan collection tetap berisi 1.000 point. Id yang sama juga menghubungkan point di Qdrant dengan baris di `data.py`.
- **Status:** 🔁 Beda dari contoh

### K22 · Payload index untuk `metadata.genres` dan `metadata.year`
- **Kelas:** tidak membuat payload index (Qdrant dibuat otomatis lewat `from_documents`).
- **Kita:** `create_payload_index` untuk dua kolom yang dipakai filter di `search_movies`.
- **Alasan:** index membuat Qdrant langsung tahu point mana yang cocok dengan genre/tahun tertentu, tanpa memeriksa semua point satu per satu. Dengan 1.000 film bedanya kecil, tapi ini praktik yang benar dan murah (2 baris kode).
- **Status:** 🔁 Beda dari contoh

### K23 · LLM: `openai/gpt-4.1-mini` lewat OpenRouter
- **Kelas:** `gpt-4o-mini` (Sesi 12, 14).
- **Kita:** `gpt-4.1-mini`, dipilih lewat dua uji pada 23 Okt. Model cukup diganti di `LLM_MODEL` tanpa mengubah kode.
- **Uji 1: 6 model × 4 pertanyaan** (tool calling, filter, menolak film 2023, anti-halusinasi):

  | Model | Hasil |
  |---|---|
  | qwen3.7-flash | Tidak bisa dipakai (diblokir *data policy* akun OpenRouter) |
  | deepseek-v4-flash | Tool benar, tapi **berhalusinasi** ("orang tuanya berubah jadi babi" tidak ada di data) |
  | gemini-2.5-flash-lite | Bagus, tapi 1 kali kena **rate limit (429)** |
  | gpt-5-nano | Benar, tapi lambat (±18 dtk per jawaban karena *reasoning*) |
  | gpt-4.1-nano | 4/4 benar, tercepat (±3 dtk) |
  | gpt-5-mini | Paling rapi, tapi 2× lebih lambat dan 8× lebih mahal |

- **Uji 2: ketepatan menulis judul** (3 pertanyaan × 2 kali). gpt-4.1-nano sempat menulis "**Seance** of the Lambs" (seharusnya *Silence*). gpt-4.1-mini, gemini-2.5-flash, dan gpt-5-mini tidak salah tulis.

  | Model | Rata-rata waktu | Biaya per jawaban |
  |---|---|---|
  | gpt-4.1-nano | 3,7 dtk | $0,00024 |
  | **gpt-4.1-mini** | **4,0 dtk** | **$0,00092** |
  | gemini-2.5-flash | 4,6 dtk | $0,00120 |
  | gpt-5-mini | 13,9 dtk | $0,00281 |

- **Alasan:** hampir secepat nano tapi lebih teliti. Penyedianya (OpenAI) stabil, tanpa rate limit seperti Gemini. Biayanya tetap kecil (1.000 pertanyaan < $1). Cadangan: `google/gemini-2.5-flash`.
- **Status:** 🔁 Beda dari contoh (model dari keluarga yang sama, versi lebih baru)

### K24 · Agent dibuat saat pertama dipakai (`@lru_cache`), bukan saat import
- **Kelas:** `main.py` membuat model, Qdrant, dan agent di level atas file Streamlit, sehingga semuanya dibangun ulang setiap kali halaman di-rerun.
- **Kita:** `get_agent()` dengan `@lru_cache(maxsize=1)`. Agent dibuat sekali, saat pertanyaan pertama masuk, lalu dipakai ulang. Sama untuk koneksi Qdrant (`_vector_store()`).
- **Alasan:** rencana awal "dibuat saat modul di-import" berarti mengakses jaringan (Langfuse, Qdrant) begitu file di-import. Itu efek samping yang dilarang arahan modular. Dengan cache, import tidak melakukan apa-apa, tapi hasilnya tetap dibuat sekali saja. Terbukti: `CacheInfo(hits=1, misses=1)` setelah dua pertanyaan.
- **Konsekuensi:** kalau system prompt diubah di Langfuse, app perlu di-restart (atau di Streamlit Cloud: *Reboot app*) supaya prompt baru terbaca.
- **Status:** ✅ Sesuai arahan (modular, tanpa efek samping saat import)

### K25 · Poster tidak dikirim ke LLM
- **Kita:** tool hanya mengirim fakta film ke LLM. UI mengambil poster sendiri dari `data.py` berdasarkan `id`.
- **Alasan:** URL poster panjang (±100 karakter × 5 film) tapi tidak berguna untuk LLM menjawab. Membuangnya menghemat token input di setiap pencarian.
- **Status:** 🔁 Pengembangan dari K06

### K26 · System prompt berbahasa Inggris, jawaban berbahasa Indonesia
- **Kelas:** system prompt di `main.py` Sesi 14 berbahasa Inggris ("You are a clothing store assistant...").
- **Kita:** system prompt `movie-agent-system` berbahasa Inggris, dengan aturan "Reply in the user's language (Indonesian by default)".
- **Alasan:**
  1. **Konsisten**: docstring tool, data, dan query pencarian semuanya berbahasa Inggris, jadi semua instruksi untuk model memakai satu bahasa.
  2. **Kepatuhan instruksi**: sebagian besar data latih LLM berbahasa Inggris, jadi aturan yang presisi paling aman ditulis dalam bahasa itu. Ini pengetahuan umum; **belum diuji A/B** dengan prompt bahasa Indonesia.
  3. **Token** (diukur 23 Okt dengan `tiktoken` o200k_base): Inggris 196 token, Indonesia 223 token (+14%). Selisih ini kecil dan tidak menentukan.
- **Bahasa jawaban tidak terpengaruh**: semua uji (benchmark 6 model, uji ketepatan judul) menjawab dalam bahasa Indonesia.
- **Kalau ingin diganti:** cukup buat version baru di Langfuse, lalu jalankan ulang set uji.
- **User bertanya dalam bahasa Indonesia: konflik atau boros?** Diukur 23 Okt, satu pertanyaan "thriller tahun 90-an":

  | Bagian input | Token | Porsi |
  |---|---|---|
  | Hasil tool (5 film JSON) | 619 | 55% |
  | Skema tool | 292 | 26% |
  | System prompt | 196 | 18% |
  | Pertanyaan user | 11 | 1% |

  Pertanyaan berbahasa Indonesia 11 token vs Inggris 9; jawaban Indonesia 75 vs Inggris 66 (±$0,000015 per jawaban). Tidak ada konflik: di semua uji, model menulis query bahasa Inggris, memetakan genre dengan benar ("animasi" → `Animation`), dan menjawab dalam bahasa Indonesia. Risiko satu-satunya adalah query yang lupa diterjemahkan, dan ini diperiksa otomatis di set uji. Penghematan, kalau suatu saat diperlukan, ada di hasil tool (55%) dan panjang riwayat, bukan di bahasa.
- **Status:** ✅ Sama dengan contoh kelas

### K27 · Filter hanya dipakai kalau user menyebutnya
- **Masalah (uji e2e 23 Okt, prompt v1 dari Langfuse):** untuk "film tentang pencuri yang masuk ke mimpi orang", model menambahkan sendiri `genre='Sci-Fi'`. Kebetulan benar, tapi kalau tebakan genrenya salah, film yang dicari justru tersaring keluar.
- **Perbaikan:** deskripsi parameter di docstring `search_movies` ditambah "Leave empty unless the user names a genre / a year or decade".
- **Bukti (4 pertanyaan × 3 run):** genre tidak lagi ditebak (6/6 `None` untuk pertanyaan tanpa genre). Pertanyaan dengan genre tetap benar (Thriller + 1990–1999, Animation). Model kadang masih mengisi tahun 1920–2020. Ini dibiarkan karena tidak berbahaya: rentangnya mencakup seluruh dataset.
- **Kenapa diperbaiki di docstring, bukan di system prompt:** aturan ini melekat pada parameter tool, dan docstring dibaca LLM tepat saat memilih argumen.
- **Status:** ✅ Tidak ada arahan yang terkait

### K28 · Semua tool mengembalikan JSON dengan kunci `"movies"`
- **Kita:** `search_movies` → `{"movies": [...]}`. `get_movie_details` → `{"movies": [...], "not_found": [...], "hint": "..."}`. `rank_movies` → `{"matching_count", "average_rating", "movies": [...]}`.
- **Alasan:** satu bentuk hasil membuat UI cukup punya satu fungsi pembaca (`tool_movies()`) untuk menampilkan judul hasil dan kartu poster, apa pun tool yang dipanggil. Tambahan per tool (`not_found`, `matching_count`) tetap bisa dibaca LLM.
- **Status:** 🔁 Pengembangan dari K06

### K29 · `rank_movies` tidak mengirim overview dan pemain
- **Kita:** hasil `rank_movies` hanya berisi angka dan fakta singkat (judul, tahun, genre, rating, Metascore, votes, gross, durasi, sutradara).
- **Alasan:** pertanyaan peringkat dijawab dengan angka. Overview adalah bagian terpanjang dari setiap film, dan hasil tool sudah menyumbang 55% token (K26). Kalau user ingin tahu ceritanya, agent memanggil `get_movie_details`.
- **Status:** 🔁 Pengembangan dari K25

### K30 · Seri film: judul persis tidak menghentikan pencarian, dan `rank_movies` punya filter judul
- **Masalah (uji 23 Okt, 3 run per pertanyaan):**
  1. "Star Wars mana yang ratingnya paling tinggi?" dijawab **salah** (Star Wars 1977, 8.6; yang benar Episode V, 8.7). Penyebabnya, lapis 1 menemukan judul persis "Star Wars", lalu langsung berhenti. Hal yang sama terjadi pada Toy Story.
  2. "harry poter yang paling bagus" dijawab **salah** (Prisoner of Azkaban, 7.9; yang benar Deathly Hallows: Part 2, 8.1). Agent memakai `search_movies` (pencarian makna), sehingga tidak semua film Harry Potter terambil. Selain itu, batas hasil 5 lebih kecil dari jumlah film Harry Potter di dataset (6).
- **Perbaikan:**
  - Lapis 1 dan 2 dari K18 digabung. Semua judul yang memuat kata-kata query diambil, judul yang persis sama ditaruh paling atas dengan label `exact`, dan sisanya berlabel `partial`.
  - `MAX_MATCHES` dinaikkan dari 5 menjadi 10.
  - `rank_movies` mendapat parameter `title` yang memakai fungsi `find_title` yang sama, jadi juga tahan typo.
  - Docstring `search_movies` sekarang menyebut: "Do not use it to find a movie or a movie series by title".
- **Bukti:** Star Wars, Harry Potter (dengan typo), dan Toy Story masing-masing 3/3 benar lewat `rank_movies(title=...)`. Pertanyaan plot tetap memakai `search_movies` (3/3). Set uji 12 skenario: semuanya benar.
- **Status:** 🔁 Revisi K18

### K31 · System prompt v2: setiap fakta harus berasal dari tool call di giliran yang sama
- **Masalah (uji e2e 23 Okt, prompt v1):** "Yang kedua siapa sutradaranya?" dijawab "Bryan Singer" **tanpa tool**. Jawabannya benar, tapi berasal dari pengetahuan model. Riwayat yang dikirim ke agent hanya berisi teks (K07), sehingga hasil tool dari giliran sebelumnya tidak ikut terkirim.
- **Perbaikan (prompt v2):** aturan 2 menjadi "Every fact in your answer must come from a tool result in the current turn... for follow-up questions, call get_movie_details again". Prompt v2 juga berisi satu baris per tool yang menjelaskan kapan tool itu dipakai.
- **Kenapa tidak mengirim hasil tool lama di riwayat:** hasil tool menyumbang 55% token per pertanyaan (K26). Kalau ikut dikirim, token bertambah di setiap giliran. Memanggil `get_movie_details` lagi hanya butuh sekitar 20 ms karena datanya lokal, tanpa Qdrant.
- **Bukti:** "Yang kedua siapa sutradaranya?" → `get_movie_details(['The Usual Suspects'])` → Bryan Singer, dari data tool.
- **Status:** ✅ Tidak ada arahan yang terkait

### K32 · Prompt v3 + hint lebih tegas: jangan menyerah sebelum mencoba lagi
- **Masalah (uji manual Reiner di app Cloud, 23 Okt, 15 pertanyaan):**
  1. "ceritakan film Parasite": `get_movie_details` not_found, lalu agent langsung bilang "Dataset ini tidak memuat Parasite". Reproduksi lokal dengan v2: **gagal 3/4**.
  2. "film drishyam tentang apa?" dijawab "tidak ada" dengan **0 tool call**. Setelah jawaban "tidak memuat" sebelumnya, model meniru polanya tanpa memeriksa.
  3. "film animasi tentang anak perempuan di dunia roh": query model terlalu umum ("a girl in the spirit world"), sehingga Sen to Chihiro tidak masuk 5 besar. Dengan query rinci ("a young girl trapped in a world of gods and spirits") filmnya langsung #1.
  4. Beberapa rekomendasi hanya menawarkan 1 film, padahal tool mengembalikan 5.
- **Perbaikan:**
  - **Hint `not_found`** (kode): "Do not tell the user the movie is missing yet... call get_movie_details again with the original title".
  - **Docstring `query`** (kode): "One English sentence ... with the user's specific details (who, where, what happens)".
  - **Prompt v3** (Langfuse): aturan 2 "Call at least one tool for every question about movies, even when an earlier answer seems to cover it". Aturan 3 menambahkan tahun dalam kurung di belakang setiap judul. Aturan 4 "make at least one more tool call before giving up". Aturan 6 "offer the 2-3 best matches".
- **Bukti (6 kasus × 5 run):** Parasite 5/5, Drishyam dengan riwayat panjang persis seperti sesi app 5/5, Spirited Away 5/5, robot 5/5 (3 film), Star Wars 5/5, film 2023 5/5 (menolak dengan sopan setelah mengecek `rank_movies`).
- **Status:** ✅ Tidak ada arahan yang terkait

### K33 · Poster yang sudah dihapus dari server diganti kotak "Poster tidak tersedia"
- **Masalah:** poster Lost Highway tampil sebagai gambar rusak. Pengecekan semua 1.000 URL: **90 poster (9%) mengembalikan 404**, termasuk link 67 px asli di dataset. Gambarnya sudah dihapus dari server Amazon, jadi kerusakannya ada di sumber data, bukan di kode.
- **Perbaikan:** `poster_available(url)` mengirim request `HEAD` (hanya cek status, tanpa mengunduh gambar) dengan timeout 3 detik. Hasilnya di-cache sehari dengan `st.cache_data`. Kalau gagal, UI menampilkan kotak "🎞️ Poster tidak tersedia".
- **Kenapa tidak membuat daftar poster rusak sekali saja:** status server bisa berubah. Cek langsung dengan cache selalu akurat dan hanya butuh beberapa baris kode.
- **Status:** ✅ Tidak ada arahan yang terkait

---

## Pemilihan embedding

Embedding dipakai dua kali: sekali saat ingest (1.000 overview), lalu setiap kali `search_movies` dipanggil (1 query).

| Opsi | Kelebihan | Kekurangan | Keputusan |
|---|---|---|---|
| **A. `text-embedding-3-small` lewat OpenRouter** | Satu API key dan satu saldo untuk LLM dan embedding (saran Pak Herman). Modelnya sama dengan kelas (1536 dimensi). Biaya ingest di bawah 1 sen dolar. Tidak membebani server Streamlit Cloud. | Dokumentasi OpenRouter hanya menyebut input teks, bukan token ID, sehingga perlu `check_embedding_ctx_length=False`. Belum pernah dicoba di kelas. | **Dipilih** |
| B. `text-embedding-3-small` langsung ke OpenAI | Sudah terbukti di Sesi 12. | Butuh akun dan saldo OpenAI terpisah, jadi dua key dan dua tagihan. | Cadangan kalau A gagal |
| C. Model lokal `sentence-transformers` (Sesi 01) | Gratis. | Model harus diunduh dan dijalankan di Streamlit Cloud setiap kali app dinyalakan, sehingga lambat dan boros memori. Model kecil seperti `all-MiniLM` hanya untuk bahasa Inggris. | Tidak dipilih |
| D. Qdrant Cloud Inference / FastEmbed | Embedding dikerjakan Qdrant. | Konsep baru di luar materi kelas, jadi menambah bahan penjelasan. | Tidak dipilih |

**Kenapa `check_embedding_ctx_length=False`:** secara default `OpenAIEmbeddings` memotong teks dengan `tiktoken` lalu mengirim **token ID** (angka), bukan teks. API OpenAI menerima keduanya, tapi dokumentasi embeddings OpenRouter hanya menyebut teks dan list teks. Dengan opsi ini teks dikirim apa adanya. Karena overview terpanjang hanya 313 karakter, pemotongan memang tidak diperlukan.

**Uji di hari pertama (sebelum ingest):**
1. Embed dua kalimat, lalu pastikan panjang vektornya **1536**.
2. Cosine similarity "a thief who enters dreams" vs overview Inception harus lebih tinggi daripada vs overview film lain.
3. Kalau langkah 1 gagal: coba opsi B.

Sumber: [OpenRouter Embeddings API](https://openrouter.ai/docs/api-reference/embeddings) (endpoint `/embeddings`, input teks atau list teks, contoh model `openai/text-embedding-3-small`).
