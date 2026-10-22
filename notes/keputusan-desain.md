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

### K12 · Query pencarian ditulis LLM dalam bahasa Inggris
- **Kelas:** pertanyaan user langsung dipakai sebagai query.
- **Kita:** docstring `search_movies` meminta LLM menulis argumen `query` sebagai deskripsi singkat dalam bahasa Inggris.
- **Alasan:** semua overview IMDB berbahasa Inggris, sedangkan user bertanya dalam bahasa Indonesia. Kemiripan vektor paling tinggi kalau query dan dokumen memakai bahasa yang sama. LLM sudah membaca pertanyaannya, jadi menerjemahkan tidak menambah panggilan model.
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

### K18 · Pencarian judul tahan huruf besar-kecil, typo, dan judul asli
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
- **Bukti (diuji pada dataset, 22 Okt):** `INCEPTION`, `Incepton`, `interstelar`, `the godfater`, `shawshank`, `lord of the rings`, `amelie`, `wall-e`, `harry poter`, `the matrx`, dan `dark night` semuanya ketemu. Yang gagal tanpa lapis 4: `parasite` dan `spirited away` (judul asli), serta `godfathr part 2` (angka Romawi; diatasi normalisasi di lapis 1).
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
