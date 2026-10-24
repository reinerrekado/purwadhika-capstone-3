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

> **K34–K38: fitur tambahan (24 Okt).** Pak Herman menyebut fitur tambahan sebagai nilai tambah. Dipilih Reiner dari 4 usulan + 1 ide sendiri (link tonton).

### K34 · Tool ke-4 `similar_movies`: film mirip lewat vektor film itu sendiri
- **Kita:** "film yang mirip Inception" → `find_title` mencari id Inception → `client.query_points(query=id)`. Qdrant memakai vektor Inception yang **sudah tersimpan** sebagai query, jadi tidak perlu embedding baru. Film itu sendiri otomatis tidak ikut di hasil. Satu panggilan, ±190 ms.
- **Beda dengan `search_movies`:** `search_movies` meng-embed **teks** user. `similar_movies` memakai **film** sebagai titik awal. Ini pemakaian kedua Qdrant yang berbeda dari RAG biasa.
- **Tanpa parameter genre:** saat diuji, agent menebak genre sendiri (Action untuk Dark Knight, Animation untuk Spirited Away). Kemiripan vektor sudah mencakup genre, jadi parameternya dibuang. Hasilnya lebih sederhana dan tidak ada yang bisa ditebak. Filter tahun tetap ada ("mirip Dark Knight tapi tahun 90-an").
- **Bukti:** Inception → Inside Man, The Matrix, Gattaca. Spirited Away → judul tidak ketemu → agent mencoba lagi dengan judul asli → film Ghibli. Dark Knight 90-an → Batman: Mask of the Phantasm. 10/10 tanpa tebakan genre.
- **Status:** 🔁 Revisi K17 (3 → 4 tool)

### K35 · Prompt baru terpakai tanpa restart (perbaikan K24)
- **Masalah:** K24 memakai `@lru_cache` pada `get_agent()`, sehingga prompt disimpan **selamanya** selama proses hidup. Pernyataan "ganti prompt tanpa deploy ulang" jadi tidak sepenuhnya benar. v3 kebetulan langsung terpakai karena push berikutnya ikut me-restart app.
- **Perbaikan:** `get_prompt()` dipanggil setiap pertanyaan. SDK Langfuse menyimpan prompt di memori 60 detik, jadi hampir selalu tanpa akses jaringan. Agent di-cache per **teks prompt** (`_build_agent(system_prompt)`), jadi agent baru hanya dibuat saat prompt benar-benar berubah.
- **Status:** 🔁 Revisi K24

### K36 · Feedback 👍/👎 disimpan sebagai score Langfuse
- **Kita:** `st.feedback("thumbs")` di bawah setiap jawaban → `create_score(trace_id, name="user_feedback", value=1/0, data_type="BOOLEAN")`.
  - `score_id` tetap (`{trace_id}-feedback`), jadi mengganti 👍 ke 👎 menimpa score lama, bukan menambah. Sudah dibuktikan: 2 kiriman → 1 score.
  - Setiap trace diberi tag `prompt-v{versi}`, jadi rasio 👍 bisa dibandingkan antar versi prompt.
- **Loop perbaikan:** Langfuse → Scores, filter `user_feedback = 0` → buka trace → lihat tool, argumen, dan hasil → reproduksi di laptop → perbaiki (docstring, prompt, atau kode) → kasus masuk set uji → versi prompt baru → bandingkan rasio 👍 per tag. Ini loop yang sama dengan K32, hanya sumber temuannya user, bukan uji manual.
- **Status:** ✅ Tidak ada arahan yang terkait (Sesi 17: observability)

### K37 · Link "Tonton di mana?" ke pencarian JustWatch, bukan API ketersediaan streaming
- **Kita:** setiap kartu poster punya link `justwatch.com/id/search?q=<judul>`.
- **Alternatif yang ditolak:**
  - API TMDB watch providers: datanya dari JustWatch, gratis hanya untuk non-komersial, komersial butuh lisensi, perlu API key baru, dan judul harus dicocokkan ke ID TMDB.
  - JustWatch Partner API: token harus diminta lewat email.
- **Affiliate:** tidak ditemukan program affiliate resmi JustWatch (dicek 24 Okt). Disebut di pitch video sebagai pengembangan berikutnya, bukan klaim.
- **Status:** ✅ Tidak ada arahan yang terkait

### K38 · Jawaban mengalir (streaming) + sidebar
- **Streaming:** `agent.stream(stream_mode=["messages", "updates"])`. Mode `messages` memberi potongan token untuk `st.write_stream`; hanya potongan dari node `model` yang ditampilkan. Mode `updates` memberi pesan utuh (AIMessage + ToolMessage), sehingga tool call dan usage tetap bisa dihitung seperti sebelumnya. `run_agent` diganti `stream_agent`. Hasil uji: token pertama sekitar 3 detik, teks yang di-stream sama persis dengan jawaban akhir.
- **Sidebar:** 4 contoh pertanyaan yang bisa diklik, tombol "Percakapan baru" (kosongkan chat + session Langfuse baru), dan total pertanyaan, token, serta perkiraan biaya sesi (harga gpt-4.1-mini di OpenRouter: $0,40 input / $1,60 output per 1 juta token).
- **Revisi 24 Okt (K40):** contoh pertanyaan di sidebar dihapus atas masukan Reiner ("aneh, saya tidak suka konsep coba tanya"). Sidebar sekarang hanya berisi tombol percakapan baru dan ringkasan biaya.
- **Temuan sampingan:** `usage_metadata` menunjukkan `cache_read` sekitar 1.150 token. OpenAI otomatis meng-cache awalan prompt (system prompt + skema tool) yang sama, sehingga token itu ditagih lebih murah. Perkiraan biaya di sidebar belum memperhitungkan diskon ini, jadi angkanya sedikit di atas biaya sebenarnya.
- **Status:** ✅ Tidak ada arahan yang terkait

### K39 · Biaya ditampilkan dalam Rupiah dan USD, dengan kurs harian ECB
- **Permintaan Reiner:** dua indikator supaya tidak bingung, dengan kurs terbaru.
- **Kita:** Frankfurter API (`api.frankfurter.dev/v1`, kurs referensi resmi Bank Sentral Eropa). Gratis, tanpa API key, dan di-cache sehari dengan `st.cache_data(ttl=86400)`, jadi hanya 1 request per hari per server. Biaya tampil di setiap jawaban ("≈ Rp30 ($0.0016)") dan di sidebar (dua metrik berdampingan, plus sumber dan tanggal kurs).
- **Alternatif:** open.er-api.com juga gratis tanpa key, tapi mewajibkan link atribusi. ECB lebih resmi.
- **Jebakan yang ditemukan:** alamat lama `api.frankfurter.app` dialihkan ke `.dev/v1`, dan servernya menolak (403) request Python yang tidak membawa User-Agent. Alamat baru dipakai langsung, dengan header User-Agent.
- **Kalau sumber kurs mati:** `usd_to_idr()` mengembalikan `None`, dan app tetap jalan dengan biaya USD saja ("–" untuk Rupiah).
- **Status:** ✅ Tidak ada arahan yang terkait

### K40 · "Cari yang mirip" di bawah setiap poster, bukan contoh pertanyaan di sidebar
- **Masukan Reiner:** contoh "film yang mirip X" di sidebar terasa aneh. Lebih alami kalau ditawarkan tepat di bawah film yang baru muncul.
- **Kita:** setiap kartu poster punya tombol "🔁 Cari yang mirip". Klik → `ask("Film yang mirip <judul>")` → diproses seperti ketikan user → `similar_movies`. Contoh pertanyaan di sidebar dihapus seluruhnya.
- **Kenapa judul tanpa tahun:** `find_title("Drishyam (2013)")` tidak akan cocok karena "2013" tidak ada di judul. Judul kembar sangat jarang (1 kasus dari 1.000 film).
- **Bukti:** jawaban Spirited Away → klik di poster Sen to Chihiro → `similar_movies('Sen to Chihiro no kamikakushi')` → Totoro, Howl's Moving Castle.
- **Revisi (K41):** tombol di bawah **setiap** poster ternyata terasa ramai (masukan Reiner). Tombolnya dipindah ke panel detail yang terbuka saat poster diklik.
- **Status:** ✅ Tidak ada arahan yang terkait

### K41 · Grid poster ala Netflix + panel detail saat diklik
- **Masukan Reiner:**
  1. tinggi poster tidak seragam, sehingga teks di bawahnya tidak sejajar;
  2. tombol "Cari yang mirip" di setiap poster terasa ramai;
  3. minta cara Netflix: ukuran tetap dan di-crop; saat disorot poster sedikit menggelap dan muncul ikon expand; detail terbuka hanya **setelah diklik**, bukan saat disorot.
- **Kita:**
  - **Grid** (`app/poster_grid.py`, Streamlit Custom Components v2): rasio 2:3 tetap, `object-fit: cover` (di-crop, tidak gepeng), judul maksimal 2 baris dengan tinggi tetap supaya semua kartu sejajar. Saat disorot atau difokus keyboard, muncul lapisan gelap 35% dan ikon expand. Klik → `setTriggerValue("opened", id)` → Python menerima id film.
  - **Panel detail** (`st.dialog`): poster besar, genre, durasi, sertifikat, rating, Metascore, sutradara, pemain, sinopsis, tombol "📺 Tonton di mana?", dan **satu** tombol "🔁 Cari yang mirip".
- **Kenapa komponen custom:** `st.image` tidak bisa diklik dan tidak bisa diberi efek hover. Komponen v2 cukup ditulis sebagai HTML, CSS, dan JS di dalam satu file Python, tanpa build tool. Warnanya memakai variabel tema Streamlit (`--st-text-color` dan lainnya), jadi tetap cocok di mode gelap maupun terang.
- **Struktur:** file ketujuh di `app/`. Isinya murni tampilan, dipisah dari `streamlit_app.py` supaya file utama tetap terbaca. Sejak K44 namanya `app/movie_cards.py`, karena kini punya dua tata letak.
- **Status:** 🔁 Revisi K40

### K42 · Sinopsis diterjemahkan sekali secara offline, hanya untuk tampilan
- **Masalah:** panel detail menampilkan sinopsis bahasa Inggris (kolom `Overview` di dataset).
- **Kita:** `scripts/translate_overviews.py` menerjemahkan 1.000 sinopsis ke `data/overview_id.csv`. Prosesnya: 40 batch × 25 sinopsis, gpt-4.1-mini, 5 berjalan paralel. Prompt `overview-translator` disimpan di Langfuse (dibuat lewat SDK, label production), jadi tidak ada teks prompt di kode. Skrip aman dijalankan ulang: film yang sudah diterjemahkan dilewati. `data.py` membaca file itu sebagai kolom `overview_id`, dan kembali ke sinopsis Inggris kalau file tidak ada.
- **Yang tidak berubah:** embedding Qdrant dan hasil tool untuk LLM tetap berbahasa Inggris (K12, K26).
- **Kenapa offline, bukan saat panel dibuka:** panel muncul seketika, biaya sekali saja (sekitar $0,15), hasilnya bisa diperiksa sebelum dipakai, dan panel tetap jalan kalau OpenRouter bermasalah.
- **Pemeriksaan:**
  - **Panjang:** rasio terjemahan/asli rata-rata 1,14× (min 0,79, maks 1,66), jadi tidak ada isi yang ditambah.
  - **Nama:** cek otomatis versi pertama menandai 341 film. Hampir semuanya tanda palsu, karena kata seperti *World War*, *German*, *Earth* memang benar diterjemahkan. Setelah dipersempit (kata yang di film lain juga muncul berhuruf kecil atau berakhiran kebangsaan dianggap kata umum), tersisa 157. Semuanya dibaca manual dan isinya nama tempat yang wajar diterjemahkan (Rome → Roma) atau istilah. Nama tokoh tetap utuh (Ekdahl, Horcrux, Tuan Dashwood).
  - **Sampel:** 20 sampel acak dibaca, dan terjemahannya natural.
- **Status:** ✅ Tidak ada arahan yang terkait

### K43 · Panel detail: "Fakta menarik" dari data + chip sutradara/pemain
- **Fakta menarik** (`movie_facts()` di `data.py`), semuanya dihitung dari dataset dan tidak dikarang LLM:
  - peringkat rating (hanya untuk 100 besar, karena rating dataset hanya 7,6–9,3 sehingga peringkat di bawahnya banyak yang seri)
  - jumlah vote + persentil popularitas
  - box office + peringkat terlaris
  - kritikus vs penonton (selisih Metascore/10 dan rating ≥ 1)
  - jumlah film sutradara di dataset

  Fakta yang datanya kosong dilewati. Angka memakai format Indonesia ("$67,4 juta").
- **Chip:** sutradara (🎬) dan 4 pemain (🎭) berupa tombol. Klik → "Film lain yang disutradarai/dibintangi X" → agent memakai `rank_movies(director=/star=)` yang sudah ada. Dipakai tombol, bukan `st.pills`, karena tombol tidak menyimpan pilihan, jadi chip tidak "nyangkut" saat panel dibuka lagi.
- **Ditolak:** sinopsis lebih panjang dari LLM (melanggar aturan anti-halusinasi), API TMDB (lisensi), dan link Wikipedia (Reiner: tidak perlu).
- **Status:** ✅ Tidak ada arahan yang terkait

### K44 · Kartu film langsung di dalam jawaban
- **Masukan Reiner:** poster di akhir jawaban terpisah dari alasannya. Kalimat "Mau info lebih detail tentang film mana?" juga mubazir kalau kartunya bisa diklik.
- **Kita:**
  - `split_answer()` memecah jawaban per baris. Baris yang **diawali** "Judul (tahun)" dan hanya menyebut satu film menjadi kartu: poster kecil di kiri, judul + tahun + rating + alasan di kanan, dan seluruh kartu bisa diklik.
  - Baris lain tetap teks. Film yang disebut di tengah paragraf (misalnya "Inception (2010) dan Interstellar (2014)...") ditampilkan sebagai grid poster di bawah jawaban.
  - Selama streaming, teks tampil biasa; begitu selesai, teks diganti tampilan berkartu.
  - Batas 5 poster dihapus, jadi daftar 10 film tampil semua.
- **Prompt v4 aturan 6:** "Put each movie on its own line as: Title (year) - one reason... Do not end by offering more details; the app shows a movie's details when the user clicks it."
- **Bug yang ditemukan saat uji:** jawaban Parasite berupa paragraf ("Film Gisaengchung (2019) atau Parasite bercerita...") sempat dijadikan kartu, dan judulnya terpotong dari tengah kalimat. Perbaikannya: baris hanya menjadi kartu kalau **diawali** judul.
- **Tata letak panel (masukan Reiner):** Fakta menarik dipindah ke kolom kanan di bawah tombol, karena ruangnya masih kosong.
- **Bukti (7 jawaban asli agent):** daftar 10 film DiCaprio → 10 kartu; thriller, Star Wars, film mirip → 3 kartu; Drishyam → 2 kartu (judul sama, id berbeda); perbandingan → teks + 2 kartu; paragraf → teks + grid.
- **Status:** 🔁 Revisi K41

### K45 · "Muat lebih banyak" langsung dari UI, tanpa LLM
- **Pertanyaan Reiner:** apakah hasil dibatasi, kenapa, dan bisakah dilanjutkan?
- **Batas tetap:** 5 film per pencarian (K05), karena:
  - hasil tool = 55% token, dan setiap film sekitar 110 token
  - relevansi pencarian makna turun setelah 5 besar
  - jawaban chat tetap mudah dibaca
- **Kita (opsi B, dipilih Reiner):**
  - Tombol "⬇️ Muat 5 film lagi" di bawah jawaban `search_movies`/`similar_movies` yang hasilnya penuh. Klik → UI memanggil **fungsi pencarian yang sama** (`search_page`/`similar_page`) dengan argumen tool call terakhir + `offset`. Qdrant mendukung `offset` di `similarity_search` dan `query_points`.
  - Logika pencarian dipisah dari `@tool`, jadi `offset` tidak terlihat oleh LLM.
  - Film tambahan tampil sebagai kartu dengan sinopsis Indonesia (K42).
- **Detail penting:** agent biasanya hanya menampilkan 2–3 dari 5 hasil. Klik pertama menampilkan sisa yang belum tampil **lebih dulu**, baru halaman berikutnya. Film yang sudah tampil tidak diulang.
- **Opsi A (lewat agent) ditolak:**
  - ±4 detik dan ≈ Rp30 per klik
  - agent bisa salah mengulang query/filter, karena riwayat hanya berisi teks
- **Konsekuensi:** klik "Muat lebih banyak" tidak tercatat di Langfuse, karena tidak melewati LLM.
- **Bukti:** "film tentang anak yang tersesat": jawaban 3 film → klik 1: E.T., Stand by Me (sisa hasil pertama) + 3 baru → klik 2: 5 lagi. 13 film, 0 duplikat, 0 panggilan LLM.
- **Status:** 🔁 Pengembangan dari K05

### K46 · IG Story "Watchlist minggu ini" (ide Reiner)
- **Alur:** panel detail → "➕ Tambah ke watchlist" (maks 4, disimpan di `st.session_state` selama sesi browser; tanpa akun, sesuai batas app) → sidebar "Watchlist (n/4)" → "🎨 Buat IG story" → pilih 1 dari 3 headline (atau tulis sendiri) + ubah ajakan → pratinjau → "⬇️ Unduh story (PNG)".
- **Desain:** dipilih Reiner dari 3 arah visual di artifact R&D ("Story Watchlist R&D"): **C · Pita Film**. Latar oranye, headline Anton raksasa dengan baris terakhir berwarna terang, poster dalam pita film hitam miring 3°, daftar judul, statistik, ajakan berbentuk pil, dan watermark "dibuat dengan Asisten Film IMDB" (setiap story yang dibagikan menjadi promosi gratis).
- **Gambar:** `app/story.py` menggambar dengan **Pillow** (sudah ikut terpasang bersama Streamlit, kini ditulis eksplisit di `requirements.txt`). Font Anton + IBM Plex Mono (lisensi OFL, beserta file lisensinya) disimpan di `assets/fonts/` (sejak K51 pindah ke `static/fonts/`). 1080×1920, ±0,7 detik, ±500 KB. Headline otomatis mengecil sampai muat dalam maksimal 3 baris. Pita film dan judul ditaruh di tengah ruang sisa, jadi tidak ada ruang kosong besar. Poster yang hilang (K33) diganti kotak berisi judul.
- **Teks:** gabungan (pilihan Reiner). LLM dengan prompt `story-headline` di Langfuse (dibuat lewat SDK, label production) membuat 3 headline ≤4 kata + 1 ajakan dari genre, tahun, durasi, dan rating watchlist (JSON mode, di-trace dengan tag `story`). Hasil divalidasi; kalau gagal atau tidak valid, dipakai **aturan cadangan** berdasarkan genre dominan. LLM dipanggil sekali per isi watchlist (disimpan di `session_state`), dan gambar di-cache per kombinasi headline + ajakan.
- **Temuan saat uji:**
  - simbol ★ tampil sebagai kotak kosong karena IBM Plex Mono tidak punya glyph-nya, jadi diganti "RATING 8,1"
  - ruang kosong besar saat headline 2 baris, jadi isi tengah diposisikan di tengah ruang sisa
  - LLM sesekali menulis "seru!.", jadi tanda baca ganda dibersihkan otomatis
- **Catatan hak cipta:** poster film milik studionya. Membagikannya untuk keperluan pribadi di media sosial lazim, tapi tidak untuk produk komersial.
- **Status:** ✅ Tidak ada arahan yang terkait

### K47 · Daftar ditampilkan lengkap + "Muat lebih banyak" untuk rank_movies (prompt v5)
- **Masalah (uji Reiner):** "film film besutan christoper nolan" hanya menampilkan 3 dari 8 film Nolan, ditutup "Apakah Anda ingin rekomendasi film Nolan lainnya?", dan tidak ada cara melihat sisanya.
- **Penyebab:**
  1. Aturan 6 v4 ("2-3 best matches unless the user asks for more"): "film-film X" tidak dianggap permintaan daftar.
  2. "Muat lebih banyak" baru ada untuk `search_movies`/`similar_movies`.
  3. Aturan v4 hanya melarang tawaran *detail*, bukan pertanyaan penutup secara umum.
- **Perbaikan:**
  - **Prompt v5 aturan 6:** rekomendasi terbuka → 2–3 film; permintaan **daftar** (film sutradara/aktor, seri, top list, "film-film ...") → semua film dari tool. "Never end with a question or an offer."
  - **`rank_page`:** logika filter dan urutan dipisah ke `_ranked()`, dipakai `rank_movies` (untuk LLM) dan `rank_page` (untuk UI). `rank_movies` memberi `matching_count`, jadi UI tahu persis masih ada sisa atau tidak.
- **Bukti (draf v5, 6 pertanyaan × 2 run):**
  - Nolan: 8/8 film tampil (sebelumnya 3)
  - Tom Hanks: 10 kartu + tombol untuk 4 sisanya
  - Harry Potter: 6 kartu
  - rekomendasi dan perbandingan tetap ringkas
  - 0 dari 12 jawaban diakhiri pertanyaan
- **Status:** 🔁 Revisi K44, K45

### K48 · Tema story mengikuti genre (otomatis + manual)
- **Ide Reiner:** tema berubah seiring genre. Keputusan:
  - tema otomatis plus pilihan manual
  - palet mengikuti usulan
  - watchlist campuran memakai "Pita warna-warni"
  - review lewat artifact
- **Kita:** tata letak Pita Film tetap sama, yang berubah hanya palet (`Theme`: latar, teks, sorotan headline, pita, swatch). Ada 10 tema + Campur:
  - Horor, Animasi, Musikal, Perang, Komedi, Romansa, Sci-Fi, Noir, Aksi (default oranye), Drama
  - **Campur:** latar hitam, segmen pita di belakang tiap poster berwarna genre filmnya, dan chip genre di bawah judul.
- **Aturan tema otomatis (`auto_theme`):**
  1. Tema tiap film = tema berprioritas tertinggi yang genrenya dimiliki film (urutan Horor → Animasi → Musikal → Perang → Komedi → Romansa → Sci-Fi → Noir → Aksi → Drama). Yang spesifik menang: Taegukgi (Action, Drama, War) → Perang; Inception → Sci-Fi.
  2. Drama paling akhir, karena ada di 72% film dataset; kalau tidak, hampir semua watchlist akan "Drama".
  3. Dominan = tema yang muncul di ≥2 film (1 film: temanya sendiri) dan tidak seri. Selain itu → Campur.
- **Keterbacaan (cek WCAG otomatis):** semua teks ≥5,4:1 dan sorotan headline ≥3,3:1. Oranye default digelapkan (`#FF5A24` → `#F2531B`), karena baris headline krem sebelumnya hanya 2,9:1. Teks pil ajakan memakai warna latar tema (di tema gelap, teks krem di atas pil terang tidak terbaca).
- **Bug sekalian diperbaiki:** koma "SERU," menabrak baris berikutnya, jadi jarak baris headline dinaikkan dari 0,95 ke 1,02 × ukuran huruf.
- **R&D:** halaman "Tema per genre" di artifact *Story Watchlist R&D*, berisi 11 story hasil Pillow asli dengan headline dari LLM. Tema otomatis tepat 11/11.
- **Status:** 🔁 Pengembangan K46

### K49 · Genre saja → rank_movies (urut rating); ada cerita/suasana → search_movies
- **Pertanyaan Reiner:** "film horor terbaik" urut rating, tapi "rekomendasikan saya film horor" tidak. Kenapa?
- **Penyebab:** dua tool sama-sama "boleh" untuk permintaan yang hanya menyebut genre, jadi agent ragu. Dengan kalimat yang sama, run 1 memakai `search_movies`, run 2 memakai `rank_movies`. `search_movies` mengurutkan berdasarkan **kemiripan makna** dengan query, dan karena user tidak mendeskripsikan cerita, agent **mengarang** query ("scary horror movies with intense atmosphere"). Urutannya jadi terlihat acak.
- **Prinsip:** pencarian makna hanya berguna kalau ada makna yang dicari. Tanpa deskripsi, urutan yang paling masuk akal dan bisa dijelaskan adalah rating.
- **Perbaikan (docstring, prompt Langfuse tidak berubah):** `search_movies` hanya untuk deskripsi cerita, tema, atau suasana; "genre/tahun saja → rank_movies sorted by rating". `rank_movies` juga disebut untuk "recommendations that only name a genre, year, or decade".
- **Bukti (8 pertanyaan × 3 run, prompt v5):** 24/24 tool tepat. "Rekomendasikan saya film horor", "film komedi tahun 90-an", "mau nonton film animasi" → `rank_movies`. "Horor tentang rumah berhantu", "komedi yang bikin hati hangat", "pencuri masuk mimpi" → `search_movies`. "Mirip Inception" → `similar_movies`.
- **Status:** 🔁 Revisi K27

### K50 · Nama app "Rakfilm", berdasarkan fitur yang terbukti kuat
- **Cek ketentuan:** nama proyek **tidak wajib** (catatan Sesi 04 bagian E dan Sesi 17 Bab 8 hanya mengatur dataset, komponen, bobot nilai, dan pengumpulan; hasil capstone bebas). Nama lama "Asisten Film IMDB" memakai merek dagang IMDb (milik Amazon) sebagai nama; sebagai keterangan sumber data tetap wajar.
- **Uji sebelum memilih (atas keraguan Reiner, 24 Okt):** apakah app benar bisa mencari film dari "adegan"? 10 pertanyaan lewat agent asli:
  - **inti cerita: 5/5 ketemu, semuanya #1.** Truman Show, Memento, Finding Nemo, WALL·E, The Sixth Sense.
  - **adegan spesifik: 0/5.** Joker (menari di tangga), Titanic (pintu kayu), The Godfather (kepala kuda), The Matrix (menghindari peluru), E.T. (sepeda di depan bulan).
  
  Penyebabnya, sinopsis dataset hanya 1–2 kalimat inti cerita, jadi adegan tidak tercatat. Karena itu calon nama "Adegan" dan sambutan "Ingat adegannya, lupa judulnya?" **ditarik**, karena menjanjikan fitur yang tidak kuat.
- **Keputusan Reiner:** **Rakfilm**, dikembangkan dari usulan "Rak". Nama ini menonjolkan fitur yang kuat dan unik (rak tontonan → IG story), terdengar seperti merek sungguhan, dan tidak menjanjikan kemampuan yang tidak ada. Subjudul "asisten film · IMDB Top 1000" menyebut sumber data, jadi penilai langsung paham.
- **Turunannya:**
  - sambutan "Mau nonton apa?" + "Ceritakan ceritanya, sebut genrenya, atau cari yang mirip film favoritmu. Simpan ke rak, bagikan ke story."
  - logo bingkai film + "?" dibaca "nonton apa?"
  - watermark story "dibuat dengan Rakfilm"
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

### K51 · UI "Bioskop malam" untuk Rakfilm: netral, poster yang memberi warna
- **Proses:** mockup 8 layar di artifact "UI Asisten Film" (tampilan awal, percakapan gelap/terang/HP, panel detail, panel story, detail di HP, logo). Reiner meminta review jujur soal kesan "AI generic". Temuannya:
  - kata berwarna di headline
  - label mono kapital di mana-mana
  - 4 kartu ide ala ChatGPT
  - kartu angka besar
  - semua elemen dikotakkan
  - Anton di semua judul
  - kalimat bertiga dan slogan
  - gimik (pil mood)

  Semua sudah dibuang. Prinsipnya: antarmuka hampir netral, warna datang dari poster (seperti Netflix/Letterboxd/MUBI).
- **Tema (`.streamlit/config.toml`):**
  - Mode terang dan gelap sama-sama tersedia (menu Settings); tampilan awal mengikuti setelan sistem pengguna (batasan Streamlit).
  - Palet: hitam hangat `#0E0D0C` / kertas hangat `#F4F1EC`, satu aksen oranye.
  - Font: IBM Plex Sans (teks) dan IBM Plex Mono (data), lewat Google Fonts. Anton disajikan dari `static/fonts/` (`enableStaticServing`) dan **hanya** dipakai untuk wordmark RAKFILM dan judul film di panel detail.
  - Sudut 6 px.
  - **Tombol utama Streamlit selalu berteks putih**, jadi oranye tombol dipilih yang lolos 4,5:1 untuk teks putih: `#D2430E` (gelap, 4,6:1) dan `#C2410C` (terang, 5,2:1). Logo tetap `#F2531B`, karena tidak ada teks di atasnya.
- **Logo:** `scripts/make_logo.py` menggambar bingkai film oranye miring 3° dengan "?" (nonton apa?) memakai Pillow → `static/rakfilm_mark.png`. Dipakai untuk `st.logo` (sidebar + ikon saat sidebar terlipat di HP), ikon tab browser, dan avatar asisten.
- **Tata letak:**
  - **Sidebar:** wordmark + "Asisten film · IMDB Top 1000", "+ Percakapan baru", **Rak kamu** (poster mini 4 kolom + slot kosong bergaris putus-putus, bisa diklik), "Bikin IG story", ringkasan sesi (tanpa `st.metric`, yang termasuk pola kartu angka besar).
  - **Tampilan awal** (hanya saat chat kosong): "Mau nonton apa?" + **dinding 10 poster acak** yang bisa diklik + "Coba:" 4 contoh pertanyaan sebagai tombol teks. Ini menggantikan 4 kartu ide.
  - **Kotak chat** `st.chat_input(height=92)`: lebih tinggi supaya terlihat (permintaan Reiner).
  - **Panel detail** `st.dialog(width="large")` (maksimal 1280 px, ukuran terbesar Streamlit): komponen `movie_hero` dengan latar poster yang diburamkan (CSS `blur`) + poster, judul Anton, info, skor, sinopsis. Di bawahnya: Sutradara/Pemain (tombol), "+ Tambah ke rak", "Cari yang mirip", "Tonton di mana ↗", lalu Fakta menarik sebagai kalimat biasa dua kolom.
  - **Panel story** "Bikin IG story": ringkasan rak, headline, ajakan + tema berdampingan, "Unduh PNG", pratinjau besar.
- **Bukan CSS paksaan:** semua lewat `config.toml`, parameter resmi (`height`, `width="large"`, `st.logo`, `avatar`), dan komponen custom v2 (shadow DOM, gaya terisolasi). Satu-satunya HTML adalah wordmark di sidebar.
- **Uji (AppTest):** tampilan awal (10 poster, 4 contoh), klik "semua film Nolan" → 8 film + tampilan awal hilang, rak 3/4 → tombol story, panel detail Inception, panel story; semuanya tanpa error.
- **Status:** ✅ Arahan kelas: UI rapi menambah nilai (Pak Herman dulu desainer grafis)

### K52 · Masukan setelah UI live: hover, kartu kaca, label "Muat", mode terang lebih redup, menu Streamlit
- **Hover ala Netflix di semua kartu:** poster membesar 6% + bayangan saat disorot atau difokus keyboard. Berlaku untuk kartu jawaban, grid, dinding poster, dan rak. Mati kalau pengguna mengaktifkan "reduce motion".
- **Hasil teratas memakai latar kaca:** kartu pertama di jawaban memakai posternya sendiri sebagai latar, diburamkan secukupnya (`blur 22px`, terang 50%, lapisan gelap 32%), jadi gambar yang diperbesar tidak terlihat pecah dan latar tidak monoton. Teks di kartu itu selalu terang karena latarnya selalu gelap, di mode gelap maupun terang.
- **Label "Muat ... lagi" jujur:**
  - `rank_movies` tahu totalnya, jadi labelnya "Muat 4 film lagi" kalau sisanya 4
  - tombol hilang kalau semua sudah tampil (Nolan 8/8)
  - pencarian makna tidak punya total, jadi labelnya "Muat lebih banyak"
- **Mode terang lebih redup:** latar `#F4F1EC` dikeluhkan terlalu silau, jadi diturunkan ke putih tulang `#E9E4DB` (luminans 0,88 → 0,78). Teks tetap 14,5:1, teks redup ≥4,8:1.
- **Menu ⋮ Streamlit (Print, Record screencast, Settings):** itu "viewer options" bawaan Streamlit. `client.toolbarMode = "minimal"` bisa menyembunyikannya, **tapi pengaturan tema terang/gelap ikut hilang**, dan tidak ada opsi untuk menyembunyikan screencast saja. Jadi dibiarkan `auto`: pengunjung hanya melihat viewer options; tombol developer (Rerun, Deploy) hanya untuk pemilik.
- **Status:** 🔁 Revisi K51

### K53 · Logo Rakfilm di IG story
- **Sebelumnya:** watermark story hanya teks "dibuat dengan Rakfilm".
- **Sekarang:** logo bingkai film "?" (104 px) diletakkan di kiri teks itu.
- **Warna logo:** diwarnai ulang satu warna, sama dengan teks tema, bukan oranye asli.
  - Alasan: oranye tenggelam di latar Komedi (kuning) dan bentrok dengan merah Horor.
  - Logo satu warna terbaca di semua tema dan tetap dikenali dari bentuknya.
  - Cara yang sama dipakai merek besar saat logonya menumpang di konten orang lain.
- **Implementasi:** bentuk logo diambil dari kanal alfa `static/rakfilm_mark.png`. Jadi tetap satu sumber logo, tidak ada file kedua yang harus disinkronkan.
- **Status:** ➕ Tambahan

### K54 · Latar kaca jadi efek hover di semua kartu hasil (revisi K52)
- **Maksud asli pengguna:** latar seluruh halaman hasil ikut berwarna dari poster teratas, supaya halaman punya aksen hidup.
- **Kenapa tidak dikerjakan:**
  - Streamlit tidak punya fitur resmi untuk mengubah latar halaman.
  - Satu-satunya cara adalah CSS yang menyasar elemen internal Streamlit, yang bisa diam-diam hilang saat Streamlit di-update.
  - Setelah risiko ini dijelaskan, pengguna memilih membatalkan ide tersebut.
- **Gantinya:**
  - Latar kaca (poster sendiri, diburamkan) tidak lagi permanen di kartu pertama.
  - Sekarang latar kaca muncul pelan saat **kartu mana pun** di jawaban disorot, dan teksnya berganti terang.
  - Halaman tetap tenang. Warna baru hidup saat pengguna berinteraksi, dan tiap film membawa warnanya sendiri.
- **Kode:** parameter `featured` dihapus dari `movie_cards`. Kartu `list` yang punya poster otomatis mendapat kelas `glassy`.
- **Status:** 🔁 Revisi K52

### K55 · Audit sebelum Fase 4: hapus `.devcontainer/`, prompt agent v6
- **Hasil audit:**
  - 9 jenis pertanyaan nyata lolos tanpa error.
  - Koneksi dan ketiga prompt Langfuse aman.
  - Tidak ada key di riwayat git.
- **`.devcontainer/` dihapus:** isinya konfigurasi container GitHub Codespaces yang mengunci Python 3.11. Tidak dipakai (app jalan di Streamlit Cloud dengan Python 3.14), dan Docker tidak diminta: aturan kelasnya satu app Streamlit tanpa FastAPI atau Docker. Folder kosong `assets/` sisa K51 ikut dihapus.
- **Prompt `movie-agent-system` v6** (dipasang lewat UI Langfuse) menutup dua kelemahan yang ditemukan audit:
  - **"Film horor terbaik" hanya memberi 3 film.** Aturan "2-3 film" untuk rekomendasi terbuka ikut terbawa ke daftar peringkat. Di v6, aturan 2-3 hanya untuk pencarian cerita; daftar peringkat tanpa jumlah memakai 5.
  - **Adegan spesifik dijawab terlalu yakin.** "Pria menari di tangga" dijawab All That Jazz dan Billy Elliot dengan kalimat "film dengan adegan…". Datanya hanya sinopsis singkat (K50), jadi v6 mewajibkan agent menyebutnya "paling mendekati dari sinopsis".
  - **Filter tahun 1920-2020 diisi sendiri oleh agent** di `rank_movies`. Hasilnya tidak salah, tapi tidak perlu. Larangan mengisi filter tanpa diminta sekarang berlaku untuk semua tool.
- **Status:** 🔁 Revisi prompt v5

### K56 · Repo dirapikan sebelum video: README jadi satu-satunya dokumen untuk penilai
- **`docs/anatomi-capstone-3.html` dihapus:** isinya rancangan awal (sebelum Rakfilm, sebelum K28–K55), sehingga sebagian sudah tidak sesuai kode. README wajib berisi diagram alur. Dua dokumen arsitektur pasti tidak sinkron, jadi yang dipertahankan hanya README. Versi artifact-nya masih ada di claude.ai kalau perlu dilihat lagi.
- **`data/Dataset Description.docx` dihapus:** isinya (sumber Kaggle + arti 14 kolom) dipindah ke README sebagai tabel. Penilai tidak perlu membuka Word, dan nama file tanpa spasi lebih aman di terminal.
- **README ditulis ulang:**
  - Isi wajib: diagram alur (Mermaid, tampil langsung di GitHub), instalasi, variabel lingkungan, cara menjalankan, contoh pertanyaan.
  - Tambahan: fitur, struktur repo, tabel dataset, dan daftar prompt Langfuse beserta mana yang wajib.
- **Uji contoh pertanyaan:** ke-10 contoh pertanyaan di README sudah dicoba ke agent sungguhan. Semuanya memanggil tool yang tertulis di tabel dan jawabannya benar.
- **Waktunya sekarang, bukan di akhir:** video (Fase 6) memperlihatkan repo, jadi strukturnya harus final dulu. Yang ditunda ke Fase 7 hanya langkah sekali jalan: cek riwayat git, ubah repo dan app jadi public.
- **Status:** ➕ Tambahan

### K57 · Dokumen yang di-retrieve + skor kemiripan tampil di expander tool call
- **Dasar:** catatan modul (Sesi 17 Bab 8): UI harus menunjukkan *tool call dan dokumen yang dipakai*. Sebelumnya expander hanya menampilkan nama tool, argumen, dan daftar judul. Isi dokumen dan skor retrieval belum terlihat, sehingga komponen Streamlit (25%) punya celah.
- **Sekarang:** untuk `search_movies`, `similar_movies`, dan `get_movie_details`, expander menampilkan tiap dokumen: judul (tahun), skor kemiripan kosinus (hanya dua tool Qdrant yang punya skor), dan sinopsis yang dipakai. `rank_movies` tetap berupa daftar judul karena hasilnya dihitung dari tabel, bukan hasil retrieval.
- **Perubahan kode:**
  - `search_page` memakai `similarity_search_with_score`, dan `similar_page` membaca `p.score`.
  - Tiap film di hasil tool dapat kunci `score` (3 desimal).
  - Biaya tambahan token: sekitar 5 angka per pencarian, tidak berarti.
- **Catatan hasil uji:** skor "pencuri masuk mimpi" Inception 0,488 vs 0,320 untuk film nomor 2, jadi selisihnya jelas. "Mirip Interstellar" menghasilkan skor 0,546 sampai 0,516 (Gravity sampai Arrival), jadi lima film itu memang berdekatan.
- **Status:** ➕ Tambahan (memenuhi syarat wajib)

### K58 · Reranker untuk `search_movies` (bonus eksplisit Pak Herman)
- **Dasar:** catatan modul (Sesi 17 Bab 8): *re-ranking* di RAG tool tidak wajib, tapi menambah poin.
- **Cara kerja:**
  - Qdrant mengambil 15 kandidat (`RERANK_CANDIDATES = 3 × PAGE_SIZE`).
  - Model reranker membaca pertanyaan dan tiap kandidat bersamaan, lalu memilih 5 terbaik dengan skor 0 sampai 1.
  - Tool `similar_movies` tidak di-rerank: film asal itu sendiri sudah menjadi query, jadi tidak ada kalimat pertanyaan untuk dibaca reranker.
- **Pilihan model:**
  - Endpoint `/api/v1/rerank` OpenRouter ada, tapi akun Reiner mewajibkan Zero Data Retention, sehingga Cohere dan Voyage ditolak (HTTP 404, alasan ZDR).
  - `qwen/qwen3-reranker-8b` lolos: sekitar 0,6 sampai 1,1 detik per pencarian dan ±$0,00005 per panggilan.
  - Setelan ZDR tidak diubah. Itu pilihan privasi akun, dan satu model yang lolos sudah cukup.
  - Model bisa diganti lewat variabel `RERANK_MODEL` (opsional, ada nilai bawaan), jadi **tidak ada secret baru** di Streamlit Cloud.
- **Bukti manfaat (20 pertanyaan):** lebih baik di "scary movie", "heist", "revenge", "pencuri masuk mimpi", dan "persahabatan di penjara". Satu kasus sedikit lebih buruk (WALL·E #2 → #4). Skor rendah merata di pertanyaan suasana samar, jadi tidak dipakai sebagai batas keras di kode.
- **Ketahanan:** `rerank()` mengembalikan `None` kalau gagal, lalu 5 hasil vektor pertama dipakai. Pencarian tidak mati karena fitur tambahan.
- **Batasan yang diketahui:**
  - Tombol "Muat lebih banyak" menggeser jendela kandidat 5 film per halaman (offset), sedangkan jendelanya 15. Film yang sudah tampil dibuang di UI. Kandidat peringkat vektor 1 sampai 5 yang tidak dipilih reranker di halaman pertama tidak diperiksa lagi di halaman berikutnya.
  - Tambahan 0,6 sampai 1,1 detik per pencarian.
- **Perubahan lain:**
  - Modul baru `app/rerank.py`.
  - `httpx==0.28.1` dipin di `requirements.txt` (sebelumnya hanya ikut terpasang lewat `openai`).
  - Hasil tool mendapat kunci `rerank_score`, dan UI menampilkannya di expander tool call.
- **Status:** ➕ Tambahan (bonus penilaian)

### K59 · Pertanyaan adegan/kutipan: penegakan dipindah dari prompt ke tool
- **Masalah:** `gpt-4.1-mini` menjawab "adegan pria menari di tangga" dengan "Berikut film dengan adegan…", walau prompt v6 dan v7 sudah menyuruh jujur. Model tidak patuh pada aturan panjang di system prompt. Filter `genre='Sci-Fi'` untuk "pencuri masuk mimpi" juga muncul lagi walau aturan 5 melarangnya.
- **Percobaan 1, ambang skor reranker (gagal):** catatan peringatan diberikan kalau semua skor reranker ≤ 0,01. Skornya ternyata bergantung kata-kata query: "a man dancing on stairs" bernilai 0,00, tapi "a scene with a man dancing on stairs" bernilai 0,08 untuk hasil yang sama-sama salah. Sementara query sah seperti "emotional" hanya 0,05. Tidak ada ambang yang memisahkan keduanya, jadi skor reranker **tidak dipakai sebagai detektor** (hanya sebagai informasi di UI).
- **Percobaan 2, parameter tool (berhasil):** `search_movies` mendapat parameter `describes_scene` ("true kalau pengguna menanyakan satu adegan, momen, atau kutipan"). Kalau `true`, hasil tool membawa `note` yang menyuruh agent membuka jawaban dengan "dicocokkan hanya dari sinopsis, tidak bisa memastikan ada adegannya". Model lebih patuh mengisi parameter dan membaca catatan di hasil tool daripada menaati aturan di prompt.
- **Hasil uji (7 pertanyaan):**
  - 3 pertanyaan adegan/kutipan (tangga, "I will be back", kapal tenggelam): semuanya terbuka dengan peringatan, tanpa mengklaim adegannya ada.
  - 4 pertanyaan kontrol (pencuri mimpi, menangis, astronot, robot): `describes_scene=False`, jawaban normal. Filter genre kosong.
- **Kompatibilitas:** `search_page` menerima `describes_scene` dan mengabaikannya, karena tombol "Muat lebih banyak" memakai ulang argumen tool yang sama.
- **Prompt v7:** aturan 7 tetap dipakai apa adanya. Sebagian isinya kini diulang oleh catatan di hasil tool, tidak berbahaya, jadi tidak perlu v8.
- **Pelajaran untuk video:** aturan yang kritis sebaiknya ditegakkan di kode atau di skema tool, bukan hanya di prompt.
- **Status:** 🔁 Revisi K55 (prompt v6/v7)

### K60 · Set uji 10 pertanyaan otomatis (`scripts/eval.py`)
- **Dasar:** ketentuan modul: demo model 2-3 kali, dan target Fase 4 "set uji: semuanya lolos". Uji manual di app (PDF Reiner, 24 Okt) menemukan masalah yang tidak terlihat di tes terminal, jadi pemeriksaannya diotomatiskan.
- **Cakupan:** 10 pertanyaan, masing-masing satu jenis kasus (cerita, film mirip, judul asli, peringkat genre, rekomendasi genre saja, typo sutradara, pertanyaan lanjutan, seri film, adegan, di luar topik). Ditambah 3 pemeriksaan umum: jawaban tidak kosong, tidak ada error tool, tidak ditutup pertanyaan.
- **Yang diperiksa:** perilaku (tool yang dipanggil, argumennya, film kunci muncul, query Inggris), bukan kecocokan kata. Jawaban LLM tidak persis sama tiap kali.
- **Keterbatasan:** pemeriksaan bahasa query berupa daftar kata Indonesia (heuristik). Query yang tidak memuat satu pun kata di daftar lolos.
- **Bukti uji bisa gagal:** lima hasil palsu yang meniru kegagalan nyata semuanya terdeteksi.
- **Hasil tiga putaran (24 Okt, prompt v7):** 10/10, 9/10, 9/10. Satu-satunya yang gagal: pertanyaan 10 (rendang), karena penolakan ditutup dengan pertanyaan, melanggar aturan 6. Laporan putaran terakhir (9/10) disimpan apa adanya di `notes/hasil-uji.md`.
- **Tindak lanjut:** perbaikan aturan penolakan di prompt (v8), diuji ulang dengan skrip ini.
- **Status:** ➕ Tambahan

### K61 · Prompt v8 dan penolakan query non-Inggris di tool (hasil set uji)
- **Temuan set uji (K60):**
  - Pertanyaan 10 (di luar topik) gagal di 2 dari 3 putaran: jawaban ditutup dengan pertanyaan. Uji lokal: 15 dari 20 jawaban di luar topik berakhir dengan pertanyaan.
  - Pertanyaan 1 sesekali mengirim query berbahasa Indonesia ke `search_movies` (pelanggaran K26), terlihat juga di uji manual Reiner (PDF).
- **Perbaikan 1, prompt v8 (aturan 8):**
  - Pertanyaan di luar topik dijawab satu kalimat tanpa pertanyaan atau tawaran. Pertanyaan tentang asisten itu sendiri dijawab satu kalimat perkenalan "Saya Rakfilm...".
  - Uji lokal sebelum dipasang: 0 dari 24 jawaban berakhir dengan pertanyaan, dan tidak ada tool yang dipanggil.
- **Perbaikan 2, di kode, bukan prompt (pola yang sama dengan K59):**
  - `search_movies` menolak query yang memuat kata Indonesia dan mengembalikan `{"error": "...translate..."}`. Agent lalu menerjemahkan dan mengulang.
  - Daftar `INDONESIAN_WORDS` dipindah dari `scripts/eval.py` ke `app/tools.py` supaya hanya ada satu sumber.
  - Set uji hanya memeriksa query yang **diterima** tool (`rejected=False`), jadi pengulangan yang berhasil tidak dihitung gagal.
  - Pemeriksaan ini heuristik: query Indonesia tanpa satu pun kata di daftar tetap lolos.
  - Biaya: satu pemanggilan tool tambahan hanya pada kasus langka itu.
- **Hasil:** 3 putaran set uji setelah kedua perbaikan, semuanya 10/10 (58/58 pemeriksaan). Sebelumnya: 10/10, 9/10, 9/10 (v7) lalu 10/10, 9/10, 10/10 (v8 tanpa penjagaan query).
- **Keterbatasan jujur:** 3 putaran adalah sampel kecil. Karena model tidak deterministik, kegagalan langka bisa muncul lagi. Set uji bisa dijalankan ulang kapan saja.
- **Status:** 🔁 Revisi prompt v7

### K62 · Key Qdrant read-only untuk penilai
- **Dasar:** klarifikasi Pak Herman (22 Okt): Qdrant harus bisa dilihat penilai. Keputusan kita: URL + API key read-only, dan dashboard ditunjukkan di video.
- **Pembuatan:** key baru di konsol Qdrant Cloud (cluster Capstone-M3), nama `penilai-pak-herman`, permission read-only, dengan tanggal kedaluwarsa. Terpisah dari key admin yang dipakai app.
- **Verifikasi (`scripts/check_readonly_key.py`):**
  - key berbeda dari key admin
  - baca berhasil: 1000 point terbaca di `imdb_movies`
  - tulis ditolak: percobaan membuat collection baru dijawab HTTP 403
  - hanya `imdb_movies` yang ada di cluster, tidak ada collection percobaan tertinggal
- **Keamanan:** key hanya ada di `.env` lokal (gitignored) dan dikirim ke Pak Herman lewat Google Form. Tidak ada di README, kode, notes, atau GitHub, karena repo akan dibuat public. `.env.example` hanya berisi nama variabelnya.
- **Cara penilai melihat data:** buka `<URL cluster>/dashboard`, masukkan key, lalu pilih collection `imdb_movies`.
- **Keterbatasan:** tanggal kedaluwarsa hanya bisa dilihat di konsol Cloud, bukan lewat skrip. Kalau key hilang, buat ulang, karena Qdrant hanya menampilkannya sekali.
- **Status:** ➕ Tambahan

### K63 · README: diagram dipecah dua, struktur dan pengujian dilengkapi
- **Temuan:** tangkapan README di GitHub (Reiner, 24 Okt) menunjukkan diagram satu-blok terlalu tinggi. Qdrant berada di kotak "Offline", sehingga tiga panah dari tool pencarian turun menyeberangi seluruh diagram dan teksnya baru terbaca kalau di-zoom.
- **Perbaikan:**
  - Diagram dipecah dua: (1) persiapan data sekali jalan, kiri ke kanan (`flowchart LR`); (2) saat pengguna bertanya, atas ke bawah. Qdrant muncul di kedua diagram sebagai node sendiri, jadi tidak ada panah panjang.
  - Reranker digambar sebagai cabang dari `search_movies`, bukan putaran Qdrant → Reranker → tool.
  - Struktur repo melengkapi `scripts/eval.py` dan `scripts/check_readonly_key.py`.
  - Bagian baru "Pengujian" menjelaskan set uji dan menautkan `notes/hasil-uji.md`.
  - Tabel variabel lingkungan mencatat `QDRANT_READONLY_API_KEY` (opsional).
- **Belum:** screenshot app (menunggu perbaikan UI supaya tampilannya final).
- **Status:** 🔁 Revisi K56

### K64 · Perbaikan UI dari uji PDF
- **Sumber:** uji manual Reiner di app Cloud (PDF, 24 Okt).
- **Yang diperbaiki:**
  - **Kartu hilang untuk judul "Parasite (judul asli Gisaengchung, 2019)":**
    - `split_answer` hanya mengenali pola "Judul (tahun)". Sekarang ada cadangan: film hasil tool yang judulnya disebut di jawaban tanpa pola itu ditampilkan sebagai kartu grid di bawah jawaban.
    - Hanya film yang benar-benar disebut yang muncul, bukan semua hasil tool.
  - **Grid satu kartu terlalu sempit:**
    - Kolom grid memakai `repeat(auto-fill, minmax(7rem, 1fr))`, bukan lima kolom tetap. Judul tidak lagi terpotong ("Interstell").
    - Teks "2014 · ★ 8.6" diberi `nowrap`.
    - Dinding poster di tampilan awal tetap lima kolom.
  - **Argumen tool call terpotong:** `st.code(..., wrap_lines=True)`.
  - **Expander "0 tool call" kosong:** tidak ditampilkan lagi kalau tidak ada tool yang dipanggil.
  - **Tombol "Muat ...":** dari teks polos (`tertiary`) menjadi tombol bergaris dengan ikon panah bawah (`secondary` + `:material/expand_more:`). Permintaan Reiner agar lebih jelas bisa diklik.
- **Tidak diubah:** label "Muat 5 film lagi" setelah pertanyaan superlatif tunggal ("yang mana paling lama?"). Secara teknis benar dan prioritasnya rendah.
- **Keterbatasan verifikasi:** kode dan alur diuji (AppTest: tanpa error, tidak ada expander untuk pertanyaan rendang, label tombol benar, `split_answer` untuk kasus Parasite). **CSS belum dilihat di browser**, jadi tampilan grid dan tombol perlu dicek langsung di app.
- **Status:** 🔁 Revisi K44, K51

### K65 · Dua bahasa: jawaban mengikuti bahasa pertanyaan (Indonesia atau Inggris)
- **Temuan:** uji manual Reiner: "movies like Inception" dijawab dalam bahasa Indonesia. Aturan 6 prompt berbunyi "Reply in the user's language (Indonesian by default)".
- **Uji lokal (15 percobaan pertanyaan Inggris):** prompt v8 menjawab Inggris 0 kali. Rumusan "ikuti bahasa pesan terakhir" hanya 8 sampai 11 dari 15, tidak stabil. Pola yang sama dengan K59 dan K61: model tidak patuh pada aturan bahasa di prompt.
- **Keputusan Reiner:** dua bahasa saja (Indonesia dan Inggris).
- **Cara kerja (di kode, `app/agent.py`):**
  - `reply_language()` menghitung kata penanda Inggris dan Indonesia di pesan pengguna. Yang terbanyak menang, seri = Indonesia (perilaku sebelumnya). Tanpa panggilan API, tanpa biaya atau latensi tambahan.
  - Kalau Inggris, satu baris "(Reply in English.)" ditambahkan di pesan terakhir hanya untuk panggilan agent. Riwayat di UI tidak berubah, tapi jejak Langfuse memuat baris itu.
  - Pendeteksi diuji pada 19 pertanyaan (7 Inggris, 12 Indonesia), semuanya benar. Pertanyaan satu kata ("Inception", "Star Wars") dianggap Indonesia.
- **Yang tetap Indonesia:** seluruh UI (tombol, label, sidebar, panel detail) dan sinopsis di kartu tambahan "Muat lebih banyak". Hanya teks jawaban agent yang ikut bahasa pertanyaan.
- **Set uji:** pemeriksaan umum baru "bahasa jawaban sama dengan bahasa pertanyaan", ditambah pertanyaan 11 sampai 14 (filter tahun, pertanyaan hitung, perbandingan dua film, pertanyaan Inggris).
- **Status:** ➕ Tambahan

### K66 · `rank_movies`: nama orang di kolom judul diabaikan
- **Temuan (set uji pertanyaan 12):** "ada berapa film Hayao Miyazaki tahun 2000-an?" sesekali dipanggil dengan `title='Hayao Miyazaki'` selain `director='Miyazaki'`. Filter judul tidak cocok dengan film mana pun, sehingga jawabannya "Tidak ada film..." padahal ada 3. Terjadi 2 dari 10 percobaan.
- **Perbaikan:** kalau `title` tidak cocok dengan judul apa pun dan ada `director` atau `star`, kolom judul diabaikan (nama orang tidak mungkin judul film). Docstring tool juga menyuruh jangan menaruh nama orang di `title`.
- **Hasil:** 10 dari 10 percobaan benar. Seri Star Wars, judul yang memang tidak ada, dan judul + aktor tidak berubah.
- **Pelajaran:** pertanyaan hitung dan filter berlapis membuka kombinasi argumen yang tidak terduga. Set uji yang lebih lebar menemukannya.
- **Status:** ➕ Tambahan

### K67 · Repo GitHub diubah menjadi public (24 Okt 2026)
- **Dasar:** syarat penilaian: repo GitHub public, `.env` tidak ter-commit. Dikerjakan lebih awal dari rencana Fase 7 atas permintaan Reiner, dengan syarat semua key aman.
- **Audit sebelum public (seluruh riwayat, semua branch dan tag):**
  - Nilai asli enam rahasia dari `.env` dicari satu per satu di setiap commit: OpenRouter, Qdrant admin, Qdrant read-only, Qdrant URL, Langfuse public dan secret. Hasil: 0 commit memuat satu pun.
  - Pola key umum (`sk-or-v1-`, `sk-lf-`/`pk-lf-`, JWT, baris `KEY=nilai panjang`) di seluruh isi diff: 0 temuan.
  - `.env` dan `secrets.toml` tidak pernah dilacak atau ada di riwayat. `.env.example` hanya berisi nama variabel.
  - Tidak ada alamat email di file yang dilacak.
- **Setelah public:** halaman repo dapat dibuka tanpa login, `.env.example` terbaca, dan `.env` mengembalikan 404.
- **Perlindungan uang (OpenRouter):** key OpenRouter punya batas $5 sendiri (terpakai ±$1,48, sisa ±$3,52, tanpa reset). Kerugian maksimal lewat key ini tinggal sisa itu, bukan saldo akun. Perlu dicatat bahwa kalau batasnya habis, app berhenti menjawab, sehingga penilaian bisa terganggu.
- **Yang perlu diketahui:**
  - Alamat email gmail pribadi terlihat sebagai penulis di riwayat commit publik. Itu data pribadi, bukan rahasia finansial. Commit berikutnya bisa memakai alamat noreply GitHub (`git config user.email`).
  - App Streamlit tetap private (README menautkannya). Pengunjung repo melihat halaman login Streamlit sampai app dibuat public di Fase 7.
  - Prompt Langfuse tidak ada di repo (sesuai aturan semua prompt di Langfuse), jadi penilai melihatnya lewat video.
- **Status:** ➕ Tambahan (mempercepat Fase 7)

### K68 · Pembatas pemakaian dan catatan privasi sebelum app dibuat public
- **Dasar:** app publik bisa dipakai siapa saja dengan key OpenRouter milik Reiner. Key sudah punya batas $5 (sisa ±$3,52), tapi kalau batas itu habis app berhenti menjawab dan penilaian terganggu. Pembatas pemakaian menjaga agar itu tidak terjadi karena satu pengunjung atau bot.
- **Batas (`app/quota.py`, konstanta mudah diubah):**
  - 30 pertanyaan per sesi browser. Tidak direset oleh "+ Percakapan baru".
  - 150 pertanyaan per jam untuk semua pengunjung, dihitung di memori proses server (reset kalau app restart).
  - Satu pertanyaan sekitar Rp20-60, jadi 150 per jam paling banyak sekitar Rp9.000.
  - Pertanyaan yang ditolak menampilkan pesan ramah dan tidak memanggil agent, jadi tidak menambah biaya.
- **Keterbatasan jujur:**
  - Batas sesi bisa dilewati dengan memuat ulang halaman. Batas per jam tetap berlaku untuk semua.
  - Pembuatan IG story (headline dari LLM) tidak dihitung, biayanya kecil per panggilan.
  - Batas per jam bisa dipenuhi satu bot dan menghalangi penilai sesaat. Itu pertukaran yang disengaja: lebih baik tertunda beberapa menit daripada kuota habis.
- **Privasi:** sidebar mencantumkan "Pertanyaanmu dicatat (Langfuse) untuk menilai kualitas jawaban." Trace Langfuse memuat teks pertanyaan pengunjung dan hanya terlihat oleh pemilik akun.
- **Diuji:** logika kuota (batas sesi, batas per jam, catatan lama kedaluwarsa), dan di dalam app: sesi yang sudah mencapai batas ditolak tanpa memanggil agent, pertanyaan normal menambah penghitung.
- **Status:** ➕ Tambahan

### K69 · Bio dan foto sutradara/pemain dari Wikipedia (sumber luar, disetujui Pak Herman)
- **Dasar:** Pak Herman menyetujui pemakaian sumber luar untuk informasi sutradara dan pemain. Dataset hanya memuat nama, tanpa bio dan foto.
- **Sumber:** Wikipedia Inggris (REST API `page/summary`, tanpa kunci), diambil **sekali secara offline** ke `data/people.csv` oleh `scripts/fetch_people.py`. Tidak ada panggilan jaringan saat app berjalan dan tidak ada secret baru.
- **Sumber lain dipertimbangkan:**
  - Wikipedia Indonesia: 0 dari 9 nama sulit, tidak berguna sebagai cadangan.
  - Wikidata: deskripsi satu baris tanpa bio dan ada risiko salah orang (Ivan Bobrov cocok dengan atlet Soviet).
  - TMDB: cakupan terbaik tapi perlu akun dan kunci API. Ditunda lalu **tidak dipakai** setelah cakupan terukur memadai.
- **Hasil akhir (3.202 nama):** bio 92,6%, foto 84,6%.

  | Kelompok | Bio | Foto |
  |---|---|---|
  | Sutradara | 97,4% | 90,3% |
  | Pemain urutan 1 dan 2 | 96,5% / 96,7% | 90,9% / 92,0% |
  | Tampil di 2 film atau lebih | 99,5% | 98,0% |
  | Tampil di 3 film atau lebih | 100% | 99,7% |
  | Hanya 1 film | 90,1% | 79,7% |

  Yang tidak punya bio terutama pemain kecil di satu film. Tampilannya nanti lingkaran inisial plus daftar filmnya dari dataset.
- **Tiga bug ditemukan dan diperbaiki saat mengambil data (pelajaran untuk video):**
  1. **Pembatasan kecepatan dicatat sebagai "tidak ketemu".** Percobaan pertama hanya menemukan 28% bio (padahal sampel 90%). HTTP 429 dianggap halaman tidak ada. Perbaikan: 404 saja yang berarti "tidak ada"; 429 dan 5xx ditunggu lalu diulang, dan kalau tetap gagal namanya tidak disimpan sehingga bisa diulang.
  2. **Pencarian nama mengambil orang yang salah.** Kemiripan huruf 85% menukar Michelle La dengan Michelle Law (penulis), Frantz Turner dengan Frank Turner (penyanyi), Jerry Nelson dengan Jerry Belson, dan lain-lain. Persentase huruf tidak bisa membedakan "La/Law" dari "Aleksey/Aleksei". Perbaikan: bandingkan **kata per kata**, tiap kata ≥88% mirip (y dan j disamakan dengan i). Sembilan kasus salah orang hilang, dan 87 pasangan nama-judul yang tersisa diaudit satu per satu.
  3. **Saringan profesi terlalu sempit.** Gene Kelly ("American entertainer") ditolak. Kata "entertainer", "dancer", "performer", dan sejenisnya ditambahkan.
- **Alias manual:** dua nama penting yang ejaannya berbeda dari Wikipedia: Tony Chiu-Wai Leung → Tony Leung Chiu-wai, Kar-Wai Wong → Wong Kar-wai.
- **Pembersihan:** spasi ganda dan baris kosong dibuang. Satu bio rusak dari sumbernya (Bárbara Lennie, isinya hanya "dʒ") dikosongkan.
- **Lisensi:** teks Wikipedia berlisensi CC BY-SA. Tiap baris menyimpan tautan sumber, dan README mencantumkan atribusinya. Foto dipakai langsung dari Wikimedia (hotlink).
- **Status:** ➕ Tambahan

### K70 · Terjemahan bio ke bahasa Indonesia (penuh, sekali jalan)
- **Keputusan Reiner:** semua bio diterjemahkan penuh, toleransi biaya Rp15.000.
- **Cara:** `scripts/translate_people.py`, gpt-4.1-mini, 25 bio per panggilan, prompt `bio-translator` di Langfuse (dibuat otomatis, aturan semua prompt di Langfuse). Hasil di kolom `extract_id`.
- **Pengaman biaya:** skrip menghitung perkiraan sebelum memanggil LLM dan berhenti sendiri kalau melewati $0,83 (±Rp15.000).
- **Biaya:** perkiraan $0,63. **Sebenarnya ±$0,55 (±Rp10.000)**, dihitung dari selisih pemakaian key OpenRouter.
- **Masalah ditemukan lewat pemeriksaan mutu:** model melewatkan dua bio dalam satu kelompok, dan jawabannya bergeser ke baris tetangga (Susanne Lothar berisi bio Sō Yamamura, Takeshi Aono berisi bio Takeshi Kaneshiro). Satu terjemahan juga rusak ("dʒ", berasal dari bio sumber yang rusak).
- **Pengaman yang dipasang:** terjemahan harus menyebut **nama belakang** orangnya, atau nama dari kalimat pembuka bio aslinya (supaya nama lahir seperti "Knut Gunnar Johanson" untuk Gunnar Björnstrand tidak ditolak). Yang gagal dibuang dan diulang. Skrip memeriksa seluruh terjemahan lama setiap dijalankan.
- **Hasil:** 2.964 bio, semuanya punya terjemahan. Pemeriksaan kata-kata yang hilang yang saya coba lebih dulu terlalu naif (menandai "Amerika" sebagai nama hilang), jadi diganti pemeriksaan nama belakang.
- **Keterbatasan jujur:** terjemahan tidak diperiksa satu per satu oleh manusia. Sampel acak (10 bio) terbaca natural, tapi tidak ada jaminan sempurna. Teks Inggris asli tetap ada di kolom `extract` sebagai cadangan.
- **Status:** ➕ Tambahan

### K71 · Profil orang: tool `get_person_info`, panel orang, dan data dari Wikipedia
- **Dasar:** Pak Herman menyetujui sumber luar untuk informasi sutradara dan pemain. Catatan Sesi 17 menyebut "bikin tools baru" sebagai nilai tambah, dan menurut Pak Herman UI yang bagus juga dinilai.
- **Yang dibangun (semua membaca `data/people.csv`, tanpa jaringan saat app berjalan):**
  - `app/data.py`: `load_people()`, `_filmography()` (nama → film dan perannya, dihitung sekali), dan `person_profile(name)` (bio, foto, peran, rata-rata rating, rentang tahun, daftar film terurut rating). Satu fungsi dipakai bersama oleh tool dan panel.
  - `app/tools.py`: `find_person(query)` dan tool kelima `get_person_info`. Pencarian nama 3 lapis (persis, semua kata ada urutan bebas, typo), memakai nama dataset **dan judul Wikipedia** sebagai alias, jadi "Wong Kar-wai" menemukan "Kar-Wai Wong".
  - `app/movie_cards.py`: komponen `person_hero` (latar foto buram, foto rata di **atas**, inisial kalau tanpa foto atau foto gagal dimuat).
  - `streamlit_app.py`: `person_dialog` (hero, terjemahan otomatis dengan tombol "Teks asli", tautan sumber Wikipedia CC BY-SA, tombol "Tanya Rakfilm tentang …", grid film dengan "Muat N film lagi"); nama sutradara dan pemain di panel film sekarang membuka panel orang. Bio yang dipakai agent tampil sebagai dokumen di expander tool call.
- **Merevisi K43:** klik nama dulu mengirim pertanyaan "Film lain yang disutradarai X" ke agent (satu panggilan LLM). Sekarang membuka panel orang yang langsung menampilkan filmnya dari data, tanpa LLM. Tombol "Tanya Rakfilm tentang X" tetap ada untuk yang ingin bertanya.
- **Hasil pengujian agent:**
  - Pertanyaan tentang orang: 15 dari 15 memilih `get_person_info`. Pertanyaan lama ("film christoper nolan", "5 film Tom Hanks terbaik") tidak direbut.
  - **Regresi ditemukan:** "siapa sutradara Parasite?" 2 dari 3 kali dikirim ke tool orang seolah "Parasite" nama orang, sekali dijawab salah ("tidak ada dalam dataset"). Petunjuk di hasil tool tidak dipatuhi, dan pencocokan judul tidak cukup karena judul asli berbeda (Parasite = Gisaengchung, K32).
  - **Perbaikan (pola K59, K61):** kalau nama tidak ketemu sebagai orang, tool **sendiri** mencari film itu dan mengembalikan detailnya (sutradara dan pemain), apa pun tool yang dipilih model. Hasil: 5 dari 5 jawaban benar, tanpa menjawab dari ingatan.
  - Orang yang tidak ada ("siapa Gal Gadot?"): ditolak jujur 4 dari 5, satu menjawab "tidak ada dalam data". Tidak ada yang mengarang bio.
- **Prompt sistem tidak diubah.** Daftar tool di prompt v8 masih empat, tool kelima dikenali lewat skema dan docstring-nya. Perutean 100% di uji, tapi kalau suatu saat bergeser, langkahnya satu baris di prompt (v9).
- **Biaya token:** hasil tool sekitar 1.500 karakter (±370 token, ±$0,0001) per pertanyaan orang. Panel orang tidak memakai token sama sekali.
- **Set uji:** 14 → 17 pertanyaan (siapa Nolan, tell me about Tom Hanks, siapa Gal Gadot). Pertanyaan #3 menerima jalur baru lewat `called_any`.
- **Mockup:** panel orang digabung ke kanvas utama (bukan artefak lepas), judul kanvas diganti "Rakfilm", dibagi 4 halaman, dan Story R&D ikut dipindah. Foto dipasang di atas (masukan Reiner).
- **Keterbatasan jujur:** (1) klik di dalam panel (nama → panel orang, poster → panel film, "Tanya Rakfilm") tidak bisa diuji `AppTest`, karena `AppTest` menjalankan ulang seluruh skrip sedangkan panel hanya menjalankan ulang fragmennya; yang terbukti hanya penyalur membuka empat keadaan panel dan alur chat penuh. (2) Bio berbahasa Inggris dari Wikipedia dijawab ulang oleh LLM dalam bahasa pengguna; isinya tetap dari hasil tool. (3) Panel hanya untuk orang yang ada di dataset.
- **Status:** ➕ Tambahan (tool baru)
- **Hasil set uji 17 pertanyaan (prompt v8, tiga putaran):** 16/17, 17/17, 17/17. Satu-satunya kegagalan (putaran 1, pertanyaan 8 "Star Wars mana yang paling bagus?") adalah pemeriksaan bahasa jawaban. Empat jawaban pembanding semuanya Indonesia (kata penanda Indonesia 8 sampai 13 lawan 4 sampai 5 kata Inggris). Penyebabnya kelemahan pemeriksaan: judul film berbahasa Inggris menambah kata penanda Inggris, dan pada jawaban pendek bisa menang tipis. Pemeriksaan tidak diubah; kegagalan ini dicatat sebagai keterbatasan heuristik.
- **Bug yang ketemu di Cloud (tangkapan layar Reiner, 25 Okt):** foto dan kotak inisial tampil berdampingan di hero panel orang. Penyebab: atribut `hidden` dikalahkan oleh `display: grid` (`.initials`) dan `display: block` (`.photo`) di CSS komponen. Perbaikan: `[hidden] { display: none !important; }` di CSS `person_hero`. Mockup kanvas tidak memperlihatkan ini karena memakai cabang `sc-if`, bukan atribut `hidden`. `movie_hero` tidak terkena karena elemennya tidak memaksakan `display`. Pelajaran: mockup tidak bisa menangkap bug CSS komponen asli; hanya uji di app yang hidup yang bisa.
- **Galat `ImportError` setelah deploy (25 Okt):** `person_profile` tidak ditemukan padahal ada di GitHub dan impor dari salinan bersih berhasil. Penyebabnya modul `app.data` versi lama masih di memori proses Cloud; Reboot app memperbaikinya.
- **`.devcontainer/` ditambahkan lagi lalu dihapus lagi (25 Okt):** Codespaces (kemungkinan dari ikon pensil di toolbar app Streamlit) menambahkannya otomatis dengan commit "Added Dev Container Folder". Dihapus kembali atas permintaan Reiner dengan alasan yang sama seperti K55: tidak dipakai, mengunci Python 3.11 padahal app berjalan di 3.14, dan Docker tidak diminta.

### K72 · Audit kriteria dan penanganan galat
- **Panel orang menampilkan semua film, tanpa tombol "Muat" (merevisi K71).** Batas 6 film adalah angka yang saya pilih sendiri dari mockup, bukan batas grid (grid memuat ±11 poster per baris di layar lebar). Data: hanya 47 dari 3.202 orang punya lebih dari 6 film, 17 di antaranya hanya kurang 1 film (Bruce Willis), dan paling banyak 17 film (Robert De Niro). Kode penghitung dan callback tombol ikut dihapus.
- **Penanganan galat di sekitar pemanggilan agent.** Sebelumnya kalau OpenRouter, Qdrant, atau Langfuse gagal, pengunjung melihat galat Streamlit mentah. Sekarang: pesan yang jelas, galat lengkap masuk log (`logger.exception`, terlihat di Manage app), pertanyaan yang gagal dibuang dari riwayat supaya percakapan tidak timpang. Diuji dengan mensimulasikan kuota habis di tengah jawaban. Penting karena key OpenRouter punya batas $5 (sisa ±$2,84).
- **Audit terhadap kriteria Pak Herman (bukti, bukan ingatan):**
  - Agen memakai LangGraph: `CompiledStateGraph` (dari `create_agent`).
  - Sintaks 17 file `.py` lolos Python 3.11 (README menjanjikan 3.11+). `pip install --dry-run -r requirements.txt` berhasil.
  - Tidak ada jejak HR/Resume di file dilacak.
  - Chat history (`session_state`), tool call, dokumen yang dipakai, dan usage tampil di UI.
  - README: diagram, instalasi, variabel, cara menjalankan, contoh. Ketinggalan: baris prompt `bio-translator` (sudah ditambahkan) dan screenshot (menunggu).
- **Yang diputuskan Reiner (belum):** (1) teks instruksi LLM di kode (`SCENE_NOTE`, `ENGLISH_ONLY`, `NOT_FOUND_HINT`, petunjuk tool orang, "(Reply in English.)") apakah dipindah ke Langfuse atau dibiarkan; (2) `LICENSE`; (3) menaikkan batas key OpenRouter menjelang rekaman video dan penilaian.
- **Status:** ➕ Tambahan

### K73 · Prompt tertaut ke generation di Langfuse
- **Temuan (tangkapan layar Reiner, 25 Okt):** di daftar Prompts Langfuse, kolom "Number of Observations (7d)" bernilai 0 untuk keempat prompt, termasuk `movie-agent-system` yang dipakai tiap pertanyaan.
- **Penyebab (dibuktikan):** agent memang memakai prompt dari Langfuse (`get_prompt(...).compile()`), tapi `CallbackHandler` tidak diberi tahu bahwa teks itu berasal dari prompt tertentu. Generation di Langfuse punya `prompt_name` kosong, sehingga tidak ada observasi dan tidak ada metrik per versi.
- **Perbaikan:** `"langfuse_prompt": prompt` ditambahkan ke `metadata` config di `stream_agent` dan `story_text`. `get_agent()` sekarang mengembalikan objek prompt (bukan hanya nomor versi). Uji sebelum-sesudah: tanpa metadata `prompt_name` kosong; dengan metadata kedua generation tertaut ke `movie-agent-system` versi 8. Diverifikasi lewat jalur app yang sebenarnya (`stream_agent`).
- **Manfaat:** tab Metrics tiap versi prompt (latensi, token, biaya, skor feedback per versi v1 sampai v8) terisi dari pertanyaan baru, sesuai slide 37-38 Sesi 17. Pertanyaan lama (sebelum perbaikan) tetap tidak tertaut.
- **Belum:** prompt penerjemah (`overview-translator`, `bio-translator`) dipakai skrip offline tanpa pelacakan, jadi tetap 0 observasi. Wajar untuk skrip sekali jalan.
- **Chunking:** keputusan "tanpa chunking" (K08) kini didukung angka: teks per film rata-rata 185 karakter, terpanjang 353; dengan potongan 500 karakter 0 dari 1.000 film terpecah. Ditulis di README.
- **Koreksi atas klaim saya sendiri:** audit sebelumnya menyebut app belum publik. Itu salah: pengecekan berhenti di pengalihan pertama (HTTP 303), yang ternyata jabat tangan cookie biasa. Dengan mengikuti pengalihan seperti browser hasilnya HTTP 200 di alamat app, tanpa halaman login.
- **Status:** 🔁 Revisi K35
- **Susulan (25 Okt): `story-headline` tetap 0 observasi.** Reiner membuat IG story di app, tapi generation-nya tidak tertaut (`prompt_name` kosong). Penyebab: handler Langfuse hanya menautkan prompt ke LLM yang berada di dalam sebuah chain; panggilan `llm.invoke(...)` langsung tidak punya induk yang membawa metadata `langfuse_prompt`. Agent tidak terkena karena `create_agent` sudah berupa graf. **Perbaikan:** `RunnablePassthrough() | llm.bind(response_format=...)` di `app/story.py`. Diuji lewat `story_text`: generation terbaru kini `story-headline` v1. Story yang dibuat sebelum perbaikan tetap tidak tertaut.
- **Susulan 2 (25 Okt): skrip terjemahan kini ikut terpantau.** Reiner bertanya apakah uji kecil (±2%) cukup memicu observasi. Skrip tidak punya pelacakan sama sekali, jadi menjalankannya apa adanya tidak memicu apa pun. `translate_batch` di `translate_overviews.py` dan `translate_people.py` kini memakai pola yang sama dengan story (chain + `CallbackHandler` + `langfuse_prompt`, tag `offline`). Diuji dengan 20 sinopsis dan 20 bio lewat skrip sementara yang **tidak menulis CSV** (biaya di bawah Rp500): `overview-translator` v1 dan `bio-translator` v1 tertaut. Data tidak diubah; menjalankan ulang skrip nanti sudah terpantau. Catatan "Belum" di atas tidak berlaku lagi.

### K74 · Tawaran penutup dipotong di kode
- **Masalah:** prompt v5 dan v8 melarang menutup jawaban dengan tawaran ("Jika Anda ingin, saya bisa memberikan detail lebih lanjut..."), tapi `gpt-4.1-mini` kadang tetap menulisnya. Tertangkap di screenshot README (25 Okt).
- **Keputusan:** pola yang sama dengan K59, K61, K65: ditegakkan di kode, bukan diharapkan dari prompt. `trim_offer()` di `app/agent.py` membuang kalimat **paling akhir** yang berupa tawaran (Indonesia dan Inggris: "Jika Anda ingin...", "Mau saya...", "Let me know...", dst.). Dipanggil di `streamlit_app.py` setelah streaming selesai, sebelum jawaban ditampilkan dan disimpan, jadi riwayat yang dikirim ke agent juga bersih.
- **Batas yang disengaja:** hanya kalimat di akhir; kalimat di tengah ("Jika Anda ingin film horor, pilih Psycho") tidak disentuh; pertanyaan klarifikasi sungguhan ("Film mana yang kamu maksud?") tidak dipotong; jawaban yang seluruhnya tawaran tidak pernah dikosongkan.
- **Diuji:** 7 kasus (tawaran di paragraf sendiri, di akhir paragraf, bahasa Inggris, klarifikasi, kalimat tengah, seluruhnya tawaran, tawaran di baris akhir). Teks yang sedang mengalir saat streaming masih sempat menampilkan tawaran sepersekian detik sebelum diganti tampilan akhir; jawaban yang tersimpan dan ditampilkan sudah bersih. Trace Langfuse tetap menyimpan keluaran asli model (berguna untuk menilai kepatuhan prompt).
- **Status:** ✅ Baru
