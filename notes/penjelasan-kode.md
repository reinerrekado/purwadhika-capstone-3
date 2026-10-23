# Penjelasan Kode: Bahan Belajar dan Video

> Untuk memahami dan menjelaskan ulang setiap file. Diperbarui setiap kali file baru selesai.
> Isi per file: **tugasnya**, **fungsi dan baris penting**, **pertanyaan yang mungkin ditanyakan** beserta jawabannya, dan **kalimat siap pakai untuk video**.
> Alasan memilih satu cara dibanding cara lain ada di `keputusan-desain.md` (kode K01, K02, ...).

## Daftar isi
1. [Persiapan: `.env` dan environment](#1-persiapan-env-dan-environment)
2. [`scripts/check_connections.py`](#2-scriptscheck_connectionspy)
3. [`app/data.py`](#3-appdatapy)
4. [`app/config.py`](#4-appconfigpy)
5. [`scripts/ingest.py`](#5-scriptsingestpy)
6. [`app/tools.py`](#6-apptoolspy)
7. [`app/agent.py`](#7-appagentpy)
8. [`streamlit_app.py`](#8-streamlit_apppy)

---

## 1. Persiapan: `.env` dan environment

### Kenapa ada dua file env?

| | `.env` | `.env.example` |
|---|---|---|
| Isi | **Key asli** | Hanya **nama variabel**, nilainya kosong |
| Masuk GitHub? | **Tidak** (ada di `.gitignore`) | **Ya**, sengaja |
| Dibaca oleh | Kode (`load_dotenv()`) | Manusia yang meng-clone repo |

Analogi: `.env.example` adalah **formulir kosong**, `.env` adalah **formulir yang sudah Anda isi**. Formulir kosong dibagikan, formulir yang terisi disimpan sendiri.

### Kenapa conda env Python 3.12?
Python bawaan laptop adalah 3.14, yang terlalu baru dan berisiko belum didukung library. Env `capstone3` memisahkan library capstone dari project lain. Versi library dikunci di `requirements.txt` supaya laptop dan Streamlit Cloud memasang versi yang sama persis (K19).

> 🎬 **Untuk video:** "Semua key saya simpan di `.env` yang tidak ikut ke GitHub. Repo hanya berisi `.env.example`, yang memberi tahu variabel apa saja yang harus diisi."

---

## 2. `scripts/check_connections.py`

### Tugasnya
Memastikan ketiga layanan (OpenRouter, Qdrant, Langfuse) tersambung **sebelum** data diunggah. Isi key tidak pernah dicetak.

### Fungsi penting

| Fungsi | Yang dicek |
|---|---|
| `check_env()` | Semua variabel wajib di `.env` terisi |
| `check_embedding()` | Vektor berukuran 1536, dan "a thief who enters people's dreams" paling mirip dengan Inception |
| `check_qdrant()` | Bisa terhubung dan melihat daftar collection |
| `check_langfuse()` | `auth_check()` berhasil |

**Baris kunci:**
```python
OpenAIEmbeddings(..., base_url="https://openrouter.ai/api/v1", check_embedding_ctx_length=False)
```
`check_embedding_ctx_length=False` membuat teks dikirim apa adanya, bukan diubah dulu jadi token ID. Dokumentasi OpenRouter hanya menyebut input berupa teks (K11).

### Hasil nyata (23 Okt)
```
cosine('a thief who enters people's dreams', Inception)    = 0.588
cosine('a thief who enters people's dreams', The Prestige) = 0.226
cosine('a thief who enters people's dreams', Interstellar) = 0.211
```

### Pertanyaan yang mungkin ditanyakan
**T: Apa itu cosine similarity?**
J: Ukuran kemiripan arah dua vektor, dengan rentang -1 sampai 1. Makin mendekati 1, makin mirip maknanya. Rumusnya: hasil kali titik (*dot product*) dibagi perkalian panjang kedua vektor (Sesi 01).

**T: Kenapa query pencarian dibuat dalam bahasa Inggris?**
J: Overview IMDB berbahasa Inggris. Uji kami: query Inggris memberi skor 0,588, query Indonesia hanya 0,390, untuk film yang sama (K12).

> 🎬 **Untuk video:** "Sebelum mengunggah data, saya cek dulu koneksi ketiga layanan. Ini juga membuktikan embedding-nya masuk akal: kalimat tentang pencuri mimpi paling mirip dengan Inception."

---

## 3. `app/data.py`

### Tugasnya
Membaca CSV, membersihkannya, dan memberikan data bersih ke `ingest.py` (untuk Qdrant) dan `tools.py` (untuk statistik). Karena pembersihan **hanya ditulis di sini**, angka di Qdrant dan di statistik pasti sama.

### Fungsi-fungsinya

| Fungsi | Tugas |
|---|---|
| `load_movies()` | Baca CSV sekali, bersihkan, kembalikan DataFrame 1.000 × 14 |
| `_poster_300px(url)` | Ganti thumbnail 67 px dengan versi 300 px |
| `all_genres()` | Daftar 21 genre unik, untuk membatasi pilihan LLM |
| `to_records(df)` | DataFrame → list of dict siap JSON (nilai kosong → `None`) |

### Baris penting

**`@lru_cache(maxsize=1)`**: CSV hanya dibaca **sekali**. Panggilan berikutnya mengambil dari memori. Tanpa ini, setiap pertanyaan user akan membaca file ulang.

**Perbaikan Apollo 13**: tahunnya berisi "PG". Diperbaiki ke 1995 **sebelum** `.astype(int)`; kalau tidak, konversinya error.

**Kolom yang dibangun ulang:**

| Kolom | Dari | Kenapa |
|---|---|---|
| `id` | nomor baris | Judul tidak unik (Drishyam 2013 dan 2015) |
| `genres` | `"Action, Crime"` → `["Action", "Crime"]` | Bisa difilter per genre |
| `runtime_min` | `"142 min"` → `142` | Bisa dihitung dan diurutkan |
| `stars` | Star1–4 → satu list | Satu tempat untuk mencari aktor |
| `meta_score`, `gross_usd` | tipe `Int64` | Lihat pertanyaan di bawah |
| `poster` | 67 px → 300 px | Kartu film di UI terlihat tajam |

**`_poster_300px`** memakai regex: bagian `._V1_...jpg` di akhir URL diganti `._V1_SX300.jpg`, sehingga server Amazon mengirim versi 300 piksel. Garis bawah di depan nama menandai "fungsi bantu internal".

**`to_records`**: JSON tidak mengenal `NaN`. Tanpa konversi ke `None`, film seperti *Soorarai Pottru* (tanpa metascore dan gross) membuat upload ke Qdrant error. `isinstance(value, list)` diperlukan karena `pd.isna()` tidak bisa dipakai langsung pada list.

### Pertanyaan yang mungkin ditanyakan

**T: Kenapa `meta_score` memakai `Int64`, bukan `int` atau `float`?**

J: Metascore adalah angka bulat, tapi 157 film tidak punya nilai.

| Pilihan | Hasil (diuji 23 Okt) |
|---|---|
| `int` | ❌ Error: *"Cannot convert non-finite values (NA) to integer"* |
| `float` | Bisa, tapi nilainya jadi `80.0`, `100.0` |
| Kosong diisi 0 | Rata-rata turun dari **77,97** ke **65,73**, jadi datanya bohong |
| **`Int64`** ✅ | `80`, `100`, dan yang kosong tetap kosong |

Cara mengingat: **`int` = bulat, wajib ada isi. `Int64` (I besar) = bulat, boleh kosong.** `gross_usd` sama (169 film kosong).

**T: Kenapa id memakai nomor baris, bukan judul?**
J: Ada dua film berjudul "Drishyam" (2013 dan 2015). Kalau judul dijadikan id, film kedua akan menimpa film pertama di Qdrant.

**T: Kenapa tidak membersihkan data langsung di `ingest.py`?**
J: Karena `tools.py` juga butuh data bersih yang sama. Kalau pembersihan ditulis dua kali, angkanya bisa berbeda tanpa ketahuan (kritik diri, temuan #4).

> 🎬 **Untuk video:** "`data.py` adalah satu-satunya tempat pembersihan data. Contohnya metascore: saya simpan sebagai `Int64` karena nilainya bulat tapi ada 157 film kosong. Kalau kosongnya diisi nol, rata-ratanya turun dari 78 ke 66. Jadi datanya saya biarkan kosong, tidak dipalsukan."

---

## 4. `app/config.py`

### Tugasnya
Satu tempat untuk membaca konfigurasi dan membuat klien yang dipakai bersama. Untuk sekarang: embedding. Klien LLM menyusul.

### Fungsi-fungsinya

| Fungsi | Tugas |
|---|---|
| `env(name)` | Ambil variabel dari `.env`. Kalau kosong, berhenti dengan pesan yang jelas: variabel mana yang harus diisi, dan di mana |
| `get_embeddings()` | Membuat `OpenAIEmbeddings` untuk `text-embedding-3-small` lewat OpenRouter |

**`load_dotenv()`** membaca file `.env` ke variabel lingkungan. Di Streamlit Cloud tidak ada file `.env`, tapi Secrets di sana juga tersedia sebagai variabel lingkungan, jadi `os.getenv` bekerja di kedua tempat tanpa kode tambahan.

### Pertanyaan yang mungkin ditanyakan
**T: Kenapa tidak memakai `try/except` seperti `main.py` kelas?**
J: `except:` kosong menyembunyikan penyebab error. Di `main.py` kelas, kalau satu variabel hilang, cabang `except`-nya justru ikut error. `env()` langsung menyebut nama variabel yang kosong (K15).

> 🎬 **Untuk video:** "Semua konfigurasi dibaca di `config.py`. Kalau ada key yang lupa diisi, aplikasi langsung memberi tahu variabel mana yang kosong."

---

## 5. `scripts/ingest.py`

### Tugasnya
**Fase offline**: mengubah 1.000 film menjadi vektor dan menyimpannya di Qdrant Cloud. Cukup dijalankan sekali, dari folder root project:
```
python -m scripts.ingest
```
`-m` artinya menjalankan file sebagai **modul**. Dengan cara ini Python mengenali folder `app/`, sehingga `from app.data import ...` bisa dipakai.

### Alurnya
```
data.py (1.000 film bersih)
  → build_documents(): 1 film = 1 Document
  → from_documents(): buat collection + embed + upload
  → create_payload_indexes(): index genre dan tahun
  → laporan: jumlah point, dimensi, jarak
```

### Fungsi-fungsinya

| Fungsi | Tugas |
|---|---|
| `build_documents()` | Membuat 1.000 `Document`. `page_content` = teks yang di-embed, `metadata` = semua data film |
| `create_payload_indexes()` | Index untuk `metadata.genres` (keyword) dan `metadata.year` (integer) |
| `main()` | Menjalankan semuanya dan mencetak laporan |

### Baris penting

**Isi `page_content` (yang di-embed):**
```python
text = f"{movie['title']}. {', '.join(movie['genres'])}. {movie['overview']}"
# "Inception. Action, Adventure, Sci-Fi. A thief who steals corporate secrets ..."
```
Hanya judul, genre, dan overview. Sutradara dan aktor tetap disimpan di `metadata`, tapi tidak di-embed (K13). Kata Pak Herman di Sesi 12: **yang diubah ke vektor hanya `page_content`; metadata ikut disimpan sebagai payload.**

**Satu panggilan untuk tiga pekerjaan** (pola Sesi 12 Bab 6B):
```python
QdrantVectorStore.from_documents(documents, get_embeddings(), ids=ids, ...,
                                 batch_size=100, force_recreate=True)
```
- Membuat collection. Ukurannya otomatis 1536, mengikuti model embedding.
- Meng-embed 1.000 teks, dikirim per **100** teks dalam satu request (`batch_size`).
- Meng-upload vektor + payload.

| Parameter | Arti |
|---|---|
| `ids=ids` | Id point = nomor baris film (K21) |
| `force_recreate=True` | Hapus collection lama lalu buat baru, supaya aman dijalankan ulang (K21) |
| `prefer_grpc=True` | Sama dengan kelas: protokol gRPC, pengiriman lebih cepat |

**Laporan akhir:** LangChain menyimpan vektor dengan **nama kosong** (`""`), sehingga konfigurasi vektornya berbentuk dict. Karena itu ada `vectors[""]`. Ini ketahuan saat percobaan pertama error, dan kemudian diperbaiki.

### Hasil nyata (23 Okt)
```
Selesai: collection 'imdb_movies' berisi 1000 point, 1536 dimensi, jarak Cosine.
durasi: 38.6 detik
```

### Uji pencarian setelah ingest

| Uji | Hasil |
|---|---|
| "a thief who enters people's dreams to steal secrets" | **Inception** urutan 1 (0,532), jauh di atas urutan 2 (0,353) |
| "great thriller from the 90s", **tanpa filter** | 3 dari 5 bukan film 90-an (1962, 1951, 1967) |
| Query sama, **filter** Thriller + 1990–1999 | 5 dari 5 tepat: Misery, Lost Highway, Funny Games, Heat, The Usual Suspects |
| Plot Parasite | Gisaengchung urutan 1, tapi selisihnya tipis (0,370 vs 0,368) |
| Plot Spirited Away | Sen to Chihiro urutan 2, kalah dari Porco Rosso karena kata "pigs" |

### Pertanyaan yang mungkin ditanyakan
**T: Kenapa tidak di-chunk seperti di Sesi 13?**
J: Overview terpanjang hanya 313 karakter. Satu film sudah pas jadi satu potongan; memotongnya justru memisahkan kalimat yang saling melengkapi (K08).

**T: Kenapa perlu filter? Bukankah vektor sudah paham "tahun 90-an"?**
J: Tidak. Vektor menangkap **makna cerita**, bukan angka tahun. Buktinya, tanpa filter muncul film tahun 1951 dan 1962. Filter menjamin syarat yang pasti (K04).

**T: Apa jadinya kalau script ini dijalankan dua kali?**
J: Tetap 1.000 point, karena id-nya tetap dan collection dibuat ulang. Dengan id acak (`uuid4`) seperti di notebook kelas, hasilnya 2.000 point duplikat (K21).

**T: Skor 0,532 itu bagus atau jelek?**
J: Yang penting bukan angka mutlaknya, tapi **selisihnya dengan urutan berikutnya**. Inception 0,532 vs urutan 2 0,353 berarti selisihnya jelas. Untuk Parasite, selisihnya hanya 0,002, jadi hasil itu rapuh.

> 🎬 **Untuk video:** "Ingest cukup dijalankan sekali. Setiap film jadi satu vektor dari judul, genre, dan sinopsisnya. Lihat bedanya: tanpa filter, pencarian 'thriller tahun 90-an' memunculkan film tahun 1951. Dengan filter, lima-limanya tepat."

---

## 6. `app/tools.py`

### Tugasnya
Berisi fungsi-fungsi yang **boleh dipanggil agent**: dua tool Qdrant dan dua tool non-RAG.

| Tool | Sumber data | Dipakai untuk |
|---|---|---|
| `search_movies` | Qdrant (RAG) | "film tentang pencuri yang masuk ke mimpi": mencari berdasarkan makna plot |
| `similar_movies` | Qdrant (vektor film) | "film yang mirip Inception": tetangga terdekat dari vektor sebuah film (K34) |
| `get_movie_details` | `data.py` (pandas) | menyebut judul, pertanyaan lanjutan, perbandingan |
| `rank_movies` | `data.py` (pandas) | "paling bagus/terlaris/berapa banyak", seri film, film seorang sutradara atau aktor |

Ketiganya mengembalikan JSON dengan kunci `"movies"` (K28).

### Cara LLM "melihat" sebuah tool
Decorator `@tool` (Sesi 10) mengubah fungsi Python menjadi **skema JSON** yang dikirim ke LLM. Yang dibaca LLM:
- **nama fungsi**: `search_movies`
- **docstring**: kapan tool ini dipakai
- **parameter + tipe + deskripsinya**: dari bagian `Args:` di docstring (`parse_docstring=True`)

Docstring tool ditulis dalam **bahasa Inggris**, karena docstring adalah instruksi untuk LLM, dan bahasanya disamakan dengan data dan query pencarian (K12).

### Baris penting

**Daftar genre yang dikunci:**
```python
Genre = Literal[tuple(all_genres())]
```
`Literal` memberi tahu LLM bahwa nilai `genre` **hanya boleh** salah satu dari 21 genre di dataset. Di skema JSON, ini menjadi `"enum": ["Action", "Adventure", ..., "Western"]`. LLM tidak bisa mengirim "thriller" huruf kecil atau "Sci Fi" (kritik diri #3). Daftarnya diambil dari `data.py`, jadi tidak diketik ulang.

**Koneksi Qdrant dibuat sekali:**
```python
@lru_cache(maxsize=1)
def _vector_store(): return QdrantVectorStore.from_existing_collection(...)
```
`from_existing_collection` (pola Sesi 14) menyambung ke collection yang sudah diisi `ingest.py`, tanpa upload ulang. `@lru_cache` memastikan koneksinya hanya dibuat sekali, saat pertama dipakai.

**Membangun filter:**
```python
models.FieldCondition(key="metadata.genres", match=models.MatchValue(value=genre))
models.FieldCondition(key="metadata.year", range=models.Range(gte=year_from, lte=year_to))
```
`metadata.` karena LangChain menyimpan data film di bawah kunci `metadata` di payload. `gte` = lebih besar atau sama dengan, `lte` = lebih kecil atau sama dengan. Filter hanya ditambahkan kalau LLM mengisinya.

**Output JSON tanpa poster:**
```python
FIELDS_FOR_LLM = ["id", "title", "year", "genres", "rating", ...]
```
LLM mendapat fakta terstruktur (K06). Poster tidak ikut karena tidak berguna untuk menjawab dan hanya memboroskan token. UI mengambil poster sendiri berdasarkan `id` (K25).

**Film mirip (`similar_movies`, K34):**
```python
store.client.query_points(store.collection_name, query=source_id, using=store.vector_name, limit=5, ...)
```
Kalau `query` diisi **id** sebuah point, Qdrant memakai vektor point itu sendiri sebagai query. Tidak perlu memanggil API embedding lagi, dan film asalnya otomatis tidak ikut di hasil. `store.client` adalah `QdrantClient` yang sudah dibuat LangChain, jadi tidak perlu koneksi kedua. `using=store.vector_name` diperlukan karena LangChain memberi nama `""` pada vektornya (ingat bug `vectors[""]` di ingest).

**Filter bersama (`_qdrant_filter`):** filter genre dan tahun dipakai oleh `search_movies` dan `similar_movies`, jadi kodenya ditulis sekali saja.

**Normalisasi judul (`normalize`):**
```python
unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()  # Amélie -> Amelie
re.sub(r"[^a-z0-9]+", " ", text.lower().replace("&", " and "))         # WALL·E -> wall e
ROMAN.get(word, word)                                                    # part ii -> part 2
```
`NFKD` memecah `é` menjadi `e` + tanda aksen, lalu `encode("ascii", "ignore")` membuang tanda aksennya. Regex mengganti semua karakter selain huruf dan angka dengan spasi. Judul di dataset **dan** ketikan user dinormalisasi dengan cara yang sama, jadi keduanya bisa dibandingkan apa adanya.

**Pencarian judul (`find_title`), 4 lapis (K18, K30):**
```python
partial = titles.map(lambda t: set(words) <= set(t.split()))
```
`<=` pada `set` berarti "himpunan bagian": **semua** kata dari query ada di judul. `"dark knight"` ⊆ `"the dark knight rises"`. Judul yang persis sama juga lolos di sini, lalu diberi label `exact` dan ditaruh paling atas. Pencarian tidak berhenti di judul persis, supaya "Star Wars" tetap membawa Episode V–VII (K30).
```python
difflib.get_close_matches(w, t.split(), n=1, cutoff=0.8)
```
Lapis typo, dipakai kalau lapis sebelumnya kosong. Setiap kata query harus punya kata yang **mirip ≥ 80%** di judul (`poter` ↔ `potter` = 91%). `difflib` adalah library bawaan Python, jadi tidak perlu instal apa-apa. Kalau tetap tidak ketemu, tool mengembalikan 3 judul termirip, ditambah `hint` (lapis 4).

**`rank_movies` = filter pandas bertingkat:**
```python
df = load_movies().dropna(subset=[sort_by])
if genre: df = df[df["genres"].map(lambda genres: genre in genres)]
...
top = df.sort_values(sort_by, ascending=(order == "lowest")).head(limit)
```
Setiap filter hanya dipasang kalau LLM mengisinya, sama seperti `search_movies`. `dropna` membuang film yang kolom urutannya kosong (misalnya `gross_usd` kosong untuk 169 film), supaya urutannya tidak kacau. `matching_count` dihitung **sebelum** `head`, jadi "ada berapa film horor?" terjawab 32, bukan 5.

### Hasil uji (23 Okt)
| Ketikan user | Hasil |
|---|---|
| `inception`, `INTERSTELLAR` | exact |
| `shawshank`, `dark knight` | partial (The Dark Knight + Rises) |
| `the matrx`, `harry poter`, `dark night` | fuzzy |
| `godfather part 2` | partial → The Godfather: Part II (angka Romawi) |
| `Parasite` | not_found + hint → agent mencari `Gisaengchung` → ketemu |
| `rank_movies(title="star wars")` | Episode V (8.7) di urutan 1 |

Setiap pemanggilan butuh sekitar 10–50 ms, karena data ada di memori dan tidak perlu jaringan.

### Pertanyaan yang mungkin ditanyakan
**T: Bagaimana LLM tahu tool mana yang dipanggil?**
J: Dari docstring setiap tool, ditambah satu baris per tool di system prompt. Contohnya, `search_movies` berbunyi "Use this when the user describes what they want to watch. Do not use it to find a movie or a movie series by title". LLM membaca deskripsi semua tool, lalu memilih yang cocok dengan pertanyaan (Sesi 10: tool calling).

**T: Siapa yang menentukan genre "Thriller" dan tahun 1990–1999?**
J: LLM, dari kalimat user "thriller tahun 90-an". Tapi yang **menjalankan** filter adalah kode dan Qdrant. LLM hanya mengusulkan argumen, kode yang memutuskan hasilnya.

**T: Kenapa `get_movie_details` dan `rank_movies` tidak lewat Qdrant?**
J: Keduanya mencari judul atau angka secara **persis**, bukan berdasarkan makna. Pandas bisa melakukannya dengan tepat dan cepat. Embedding malah bisa meleset: pertanyaan "harry poter" lewat `search_movies` sempat melewatkan film Harry Potter yang ratingnya paling tinggi (K30).

**T: Kenapa ada label `match`?**
J: Supaya agent tahu seberapa yakin hasilnya. Kalau labelnya `fuzzy` atau hasilnya lebih dari satu, agent bisa memastikan dulu: "Maksud Anda *The Matrix*?"

> 🎬 **Untuk video:** "Saya punya tiga tool. Satu tool RAG ke Qdrant untuk mencari berdasarkan plot, dan dua tool pandas untuk judul dan peringkat. Saya pernah menemukan bug: 'Star Wars terbaik' dijawab salah karena pencarian berhenti di judul yang persis sama. Ini perbaikannya, dan ini buktinya."

---

## 7. `app/agent.py`

### Tugasnya
Merakit **agent ReAct**: LLM + tools + system prompt dari Langfuse, dan mencatat setiap run ke Langfuse.

### Fungsi-fungsinya

| Fungsi | Tugas |
|---|---|
| `get_agent()` | Ambil prompt `production` dari Langfuse (di-cache SDK 60 detik), kembalikan agent + nomor versi prompt |
| `_build_agent(system_prompt)` | `create_agent(model, tools, system_prompt)`, di-cache per teks prompt (`@lru_cache`) |
| `stream_agent(messages, session_id, run)` | Jalankan agent dengan seluruh riwayat, alirkan teks jawaban; setelah selesai mengisi `run` dengan pesan baru + `trace_id` |
| `send_feedback(trace_id, thumbs_up)` | Simpan 👍/👎 sebagai score di trace Langfuse |

### Baris penting

**System prompt dari Langfuse, bukan hardcode, dan selalu versi terbaru (K35):**
```python
prompt = get_client().get_prompt(PROMPT_NAME)          # label production, cache SDK 60 detik
return _build_agent(prompt.compile()), prompt.version  # agent di-cache per teks prompt
```
`get_prompt` mengambil versi berlabel `production` (Sesi 17). Versi awal memakai `@lru_cache` langsung di `get_agent()`, sehingga prompt baru baru terpakai setelah app restart. Sekarang cache-nya **per teks prompt**: selama prompt sama, agent yang sama dipakai ulang; begitu label production dipindah ke versi baru, dalam ≤60 detik agent baru dibuat otomatis.

**Tracing ke Langfuse:**
```python
config = {"callbacks": [handler], "metadata": {
    "langfuse_session_id": session_id,
    "langfuse_tags": [f"prompt-v{prompt_version}"],
}}
```
`CallbackHandler` mencatat semuanya: setiap panggilan LLM, setiap tool call beserta argumen dan hasilnya, token, dan waktu. `langfuse_session_id` mengelompokkan satu percakapan menjadi satu **session**. `langfuse_tags` memberi label versi prompt pada setiap trace, sehingga feedback bisa dibandingkan antar versi. Di Langfuse v3 ke atas, keduanya dikirim lewat `metadata`, bukan lewat argumen `CallbackHandler(...)` seperti di slide 27 (K02).

**Streaming dua jalur (K38):**
```python
for mode, data in agent.stream(..., stream_mode=["messages", "updates"]):
    if mode == "messages":            # potongan token → ditampilkan langsung
        if meta["langgraph_node"] == "model" and chunk.content: yield chunk.content
    else:                             # pesan utuh tiap node selesai → untuk tool call & token
        new_messages += update["messages"]
run.update(messages=new_messages, trace_id=handler.last_trace_id)
```
Fungsi ini **generator** (`yield`): Streamlit (`st.write_stream`) menampilkan setiap potongan begitu datang. Ada dua jenis event. `messages` berisi potongan teks; hanya yang berasal dari node `model` yang ditampilkan, bukan dari node `tools`. `updates` berisi pesan utuh (AIMessage dengan `tool_calls` dan `usage_metadata`, serta ToolMessage), sehingga hanya pesan **baru** yang terkumpul, tanpa perlu memotong `[len(messages):]` lagi. Generator tidak bisa mengembalikan nilai ke `st.write_stream`, jadi hasil tambahannya dititipkan ke dict `run` yang dibawa dari pemanggil.

**Feedback ke Langfuse (K36):**
```python
get_client().create_score(trace_id=trace_id, name="user_feedback", value=int(thumbs_up),
                          data_type="BOOLEAN", score_id=f"{trace_id}-feedback")
```
Score menempel pada trace jawaban itu. `score_id` yang tetap membuat klik ulang menimpa nilai lama, bukan menambah score baru.

### Isi satu run
Contoh hasil nyata untuk "thriller tahun 90-an":
```
['ai', 'tool', 'ai']
 │      │      └─ jawaban akhir untuk user
 │      └─ hasil search_movies (JSON 5 film)
 └─ LLM memutuskan: panggil search_movies(genre="Thriller", year_from=1990, year_to=1999)
```
Ini **loop ReAct** (Sesi 10): berpikir → bertindak (tool) → membaca hasil → menjawab.

### Pertanyaan yang mungkin ditanyakan
**T: Kenapa `create_agent`, bukan `create_react_agent`?**
J: `create_react_agent` sudah *deprecated* sejak LangGraph 1.0 dan dipindahkan ke `langchain.agents.create_agent`. Notebook Sesi 10 juga memakai `create_agent` (K01).

**T: Kenapa agent tidak dibuat saat file di-import?**
J: Itu akan mengakses jaringan (Langfuse, Qdrant) begitu file di-import, padahal arahannya modul tidak boleh punya efek samping saat di-import. Agent dibuat saat pertanyaan pertama masuk, lalu dipakai ulang selama prompt tidak berubah (K24, K35).

**T: Feedback 👍/👎 dipakai untuk apa?**
J: Untuk menemukan jawaban buruk dari pengguna sungguhan. Di Langfuse → Scores, filter `user_feedback = 0`, buka trace-nya, lalu lihat tool apa yang dipanggil, dengan argumen apa, dan apa hasilnya. Masalahnya direproduksi di laptop, diperbaiki (docstring, prompt, atau kode), dimasukkan ke set uji, lalu dirilis sebagai versi prompt baru. Karena setiap trace diberi tag `prompt-vN`, rasio 👍 sebelum dan sesudah perbaikan bisa dibandingkan (K36).

**T: Kenapa memilih `gpt-4.1-mini`?**
J: Dari uji 6 model: nano sempat salah menulis judul ("Seance of the Lambs"), DeepSeek berhalusinasi, Gemini lite kena rate limit, gpt-5-mini 3× lebih lambat. gpt-4.1-mini cepat (±4 dtk), teliti, dan murah (<$1 per 1.000 pertanyaan) (K23).

> 🎬 **Untuk video:** "Agent saya dibuat dengan `create_agent`. System prompt-nya tidak ditulis di kode, tapi diambil dari Langfuse. Setiap run dicatat ke Langfuse, dikelompokkan per sesi, dan diberi tag versi prompt. Feedback 👍/👎 dari pengguna masuk ke trace yang sama, jadi saya tahu jawaban mana yang buruk dan dengan versi prompt yang mana."

---

## 8. `streamlit_app.py`

### Tugasnya
Hanya **tampilan**. Semua logika ada di `app/agent.py` (arahan modular Pak Herman). Menampilkan tiga hal wajib: **chat history**, **tool call**, dan **usage**.

### Fungsi-fungsinya

| Fungsi / bagian | Tugas |
|---|---|
| `st.session_state.chat` | Riwayat percakapan yang bertahan selama sesi browser |
| `st.session_state.session_id` | Id acak per sesi, dikirim ke Langfuse |
| `tool_movies()` | Baca daftar `movies` dari hasil tool (K28). Kalau isinya pesan error, kembalikan list kosong |
| `summarize_run()` | Dari pesan baru, ambil tool call (nama, argumen, judul hasil), id film yang disebut di jawaban, dan jumlah token |
| `show_posters()` | Kartu poster (maksimal 5) untuk film yang disebut di jawaban, dengan link "Tonton di mana?" (K37) |
| `show_details()` | Poster + expander "🔧 tool call" + baris jumlah token + tombol 👍/👎 |
| `save_feedback()` | Callback saat 👍/👎 diklik → `send_feedback` ke Langfuse |
| `new_chat()` | Callback tombol "Percakapan baru": kosongkan chat, buat `session_id` baru |
| `split_answer()` | Pecah jawaban per baris: baris yang diawali "Judul (tahun)" → kartu, lainnya → teks (K44) |
| `show_answer()` → `movie_cards()` | Gambar teks + kartu film (`app/movie_cards.py`), lalu grid untuk film di dalam paragraf; buka panel kalau ada yang diklik |
| `card_data()` | Siapkan data kartu: judul, tahun, rating, alasan, poster (atau None kalau poster hilang) |
| `movie_dialog()` | Panel detail (`@st.dialog`): sinopsis Indonesia, chip sutradara/pemain, "Tonton di mana?", "Cari yang mirip", Fakta menarik (K40–K43) |
| `ask()` | Dipanggil dari panel: titipkan pertanyaan, lalu `st.rerun()` |
| `load_more()` | Callback "⬇️ Muat 5 film lagi": panggil `search_page`/`similar_page` dengan `offset` berikutnya, tanpa LLM (K45) |
| `shown_ids()` | Id film yang sudah tampil di satu jawaban, supaya "Muat lebih banyak" tidak mengulang |
| `usd_to_idr()` | Kurs USD→IDR harian dari ECB (Frankfurter), di-cache sehari; `None` kalau gagal (K39) |
| `cost_usd()`, `rupiah()` | Hitung biaya dari token, lalu ubah ke format "Rp42" |
| sidebar (atas) | Tombol percakapan baru |
| sidebar (bawah) | Total pertanyaan, token, biaya dalam Rp dan USD, serta sumber kurs. Ditulis di akhir skrip supaya sudah termasuk jawaban terbaru |
| loop `for index, message in ...` | Menggambar ulang chat history setiap rerun |
| `st.chat_input(...) or pending` | Pertanyaan dari kotak ketik **atau** dari tombol contoh di sidebar |
| `st.write_stream(stream_agent(...))` | Menampilkan jawaban potong demi potong, lalu mengembalikan teks lengkapnya |

### Baris penting

**Riwayat lengkap dikirim ke agent:**
```python
history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat]
```
Hanya `role` dan `content` yang dikirim. Kolom `details` hanya untuk tampilan. Inilah yang membuat agent ingat percakapan, sesuatu yang tidak dilakukan `main.py` kelas (K07).

**Token dijumlahkan dari semua panggilan LLM:**
```python
"input_tokens": sum((m.usage_metadata or {}).get("input_tokens", 0) for m in ai_messages)
```
Satu pertanyaan bisa memicu 2–3 panggilan LLM (memutuskan tool → menjawab), jadi tokennya dijumlahkan. `usage_metadata` adalah atribut `AIMessage` dari Sesi 09. `or {}` berjaga-jaga kalau ada penyedia model yang tidak mengirim data token.

**Mencocokkan tool call dengan hasilnya:**
```python
tool_results = {m.tool_call_id: json.loads(m.content) for m in new_messages if m.type == "tool"}
```
Setiap tool call punya `id`, dan hasilnya (`ToolMessage`) membawa `tool_call_id` yang sama. Dari situ UI bisa menampilkan "search_movies(...) → Hasil: Misery, Heat, ...".

**Poster hanya untuk film yang benar-benar disebut:**
```python
for title in sorted(found, key=len, reverse=True):                     # judul terpanjang dulu
    match = re.search(rf"{re.escape(title)}\W{{0,3}}\({year}\)", answer)  # "Heat" (1995)
    ...
    answer = answer.replace(title, "\0" * len(title))                    # tutup, panjang tetap
positions = with_year or plain
```
Tool bisa mengembalikan 5–10 film, tapi jawaban mungkin hanya menyebut 3. Hanya film yang disebut di jawaban yang diberi poster, urut sesuai daftar di jawaban. Ada tiga jebakan yang ditemukan saat uji (23 Okt):
1. **Judul di dalam judul.** "Star Wars" ada di dalam "Star Wars: Episode V - ...". Karena itu judul terpanjang dicocokkan dulu, lalu ditutup dengan karakter `\0` sepanjang judulnya. Panjang teks tetap sama, jadi posisi judul lain tidak bergeser.
2. **Frasa umum.** Kalimat "Tiga **Star Wars** dengan rating tertinggi..." bukan penyebutan film Star Wars (1977). Prompt mewajibkan format `Judul (tahun)` (aturan 3), jadi posisi dicari dengan regex judul + tahun. `\W{0,3}` mengizinkan tanda kutip atau `**` di antaranya, misalnya `"Heat" (1995)` atau `**Heat** (1995)`.
3. **Jawaban tanpa tahun.** Kalau tidak ada satu pun judul berformat `Judul (tahun)`, dipakai posisi judul biasa (`plain`). `with_year or plain` berarti: pakai `with_year` kalau tidak kosong, selain itu `plain`.
4. **Judul kembar (uji 24 Okt).** "Drishyam" (2013) dan "Drishyam" (2015) adalah dua film berbeda. Awalnya film dikelompokkan per judul, jadi hanya satu poster yang tampil. Sekarang film dikelompokkan per `id`, dan tahun di regex membedakan keduanya.

**Poster yang sudah dihapus (K33):**
```python
@st.cache_data(ttl=86400, show_spinner=False)
def poster_available(url): ... urlopen(Request(url, method="HEAD"), timeout=3).status == 200
```
90 dari 1.000 poster sudah dihapus dari server Amazon. `HEAD` hanya meminta status tanpa mengunduh gambar. `st.cache_data` menyimpan hasilnya sehari, jadi setiap URL hanya dicek sekali. `except OSError` menangkap semua kegagalan jaringan, karena `HTTPError`, `URLError`, dan timeout adalah turunan `OSError`.

Posternya diambil dari `data.py` lewat `id` (K25), tidak lewat LLM.

**Tombol feedback per jawaban:**
```python
key = f"feedback_{st.session_state.session_id}_{index}"
st.feedback("thumbs", key=key, on_change=save_feedback, args=(key, trace_id))
```
`key` unik per percakapan dan per posisi jawaban. Kalau hanya memakai `index`, pilihan 👍 di percakapan lama akan muncul lagi di jawaban pertama percakapan baru. `on_change` dipanggil Streamlit **sebelum** rerun, dan nilai widget dibaca dari `st.session_state[key]`.

**Kartu di dalam jawaban (K44):**
```python
if len(hits) == 1 and not prefix.strip(" \"'*"):   # baris DIAWALI satu "Judul (tahun)"
    reason = line[match.end():]                      # sisanya = alasan
```
Untuk setiap baris jawaban, `split_answer()` mencari pola "Judul (tahun)" dari film yang ditemukan tool. Kalau baris itu **diawali** judul (setelah nomor daftar, tanda kutip, atau `**` dibuang), baris itu menjadi kartu. Kalau judulnya ada di tengah kalimat, baris tetap teks, karena memotong judul dari tengah kalimat merusak kalimatnya (bug Parasite saat uji). Selama jawaban mengalir, teks tampil biasa di `st.empty()`; setelah selesai, isinya dikosongkan dan diganti tampilan berkartu.

**Kartu yang bisa diklik (K41, `app/movie_cards.py`):**
```python
_MOVIE_CARDS = st.components.v2.component("movie_cards", html=..., css=..., js=...)
card.onclick = () => setTriggerValue("opened", movie.id)                      // JS: kirim id ke Python
opened = movie_cards(cards, layout="list", key=..., on_open=lambda: None)     # Python: id yang diklik, atau None
if opened is not None: movie_dialog(opened)
```
Satu komponen dengan dua tata letak: `"list"` (kartu di dalam jawaban: poster kecil + alasan) dan `"grid"` (deretan poster untuk film yang disebut di paragraf).
`st.image` tidak bisa diklik, jadi grid dibuat sebagai **custom component v2**: HTML, CSS, dan JS kecil di dalam file Python, tanpa build tool. Alurnya:
1. Python mengirim daftar film lewat `data=`.
2. JS menggambar kartu.
3. Saat diklik, JS memanggil `setTriggerValue("opened", id)`, dan Streamlit me-rerun app.
4. `poster_grid()` mengembalikan id itu **hanya pada rerun tersebut**. *Trigger* berbeda dari *state*: trigger otomatis kosong lagi setelah satu rerun, jadi panel tidak terbuka ulang terus-menerus.

CSS-nya meniru Netflix:
- `aspect-ratio: 2/3` + `object-fit: cover` → semua poster sama ukuran, gambar di-crop, bukan gepeng
- `-webkit-line-clamp: 2` + `min-height` → judul maksimal 2 baris, sehingga semua kartu sejajar
- `.card:hover .shade` → lapisan gelap 35% + ikon expand muncul; `:focus-visible` memberi efek yang sama untuk keyboard
- warna dari variabel tema Streamlit (`--st-text-color` dan lainnya), jadi cocok di mode gelap maupun terang

**Panel detail dan "Cari yang mirip" (K40):**
```python
@st.dialog("Detail film", width="large")
def movie_dialog(movie_id): ...
    if similar.button("🔁 Cari yang mirip"):
        st.session_state.pending = f"Film yang mirip {movie['title']}"
        st.rerun()
question = st.chat_input(...) or st.session_state.pop("pending", None)
```
`@st.dialog` mengubah fungsi menjadi jendela modal. Tombol di dalamnya menitipkan pertanyaan lalu memanggil `st.rerun()`, yang menutup panel dan menjalankan ulang app. Di bawahnya, pertanyaan titipan diproses persis seperti ketikan user, lalu agent memilih `similar_movies`. `pop` mengambil sekaligus menghapusnya, jadi tidak terkirim dua kali.

**Biaya dalam Rupiah (K39):**
```python
request = urllib.request.Request(FX_URL, headers={"User-Agent": "imdb-movie-assistant"})
```
Kurs diambil dari ECB lewat Frankfurter, sekali sehari (`st.cache_data(ttl=86400)`). Header User-Agent wajib, karena server menolak (403) request Python tanpa header itu. Formatnya `f"{x:,.0f}".replace(",", ".")`: Python memakai koma sebagai pemisah ribuan, lalu diganti titik sesuai format Indonesia.

### Menjalankan
```
streamlit run streamlit_app.py
```

---

## 9. `app/story.py`: IG Story "Watchlist minggu ini" (K46)

### Tugasnya
Membuat teks dan gambar story 1080×1920 dari 1–4 film di watchlist. Logikanya murni, tanpa Streamlit, jadi bisa diuji sendiri. `streamlit_app.py` hanya memanggil `story_text()` dan `render_story()`.

### Fungsi-fungsinya

| Fungsi | Tugas |
|---|---|
| `story_text(ids, session_id)` | 3 headline + 1 ajakan dari LLM (prompt `story-headline` di Langfuse, JSON mode). Gagal atau tidak valid → `fallback_text()` |
| `fallback_text(movies)` | Aturan cadangan: headline dari genre yang paling sering muncul (`Counter`) |
| `stats_line(movies)` | "4 FILM · 7J 38M · RATING 8,1", dihitung dari data |
| `render_story(ids, headline, cta)` | Gambar PNG dengan Pillow, gaya Pita Film |
| `_fit_headline()` | Cari ukuran huruf terbesar (≤200 px) yang membuat headline muat dalam ≤3 baris |
| `_film_strip()` | Pita film: lubang sproket + poster crop 2:3, lalu dimiringkan 3°. Tema Campur: segmen warna per film |
| `Theme`, `THEMES` | Palet per genre (K48): latar, teks, sorotan, pita, swatch. Urutan list = prioritas |
| `film_theme(movie)` | Tema satu film: tema pertama di `THEMES` yang genrenya dimiliki film (`set & set` = irisan) |
| `auto_theme(movies)` | Tema dominan (`Counter`): muncul di ≥2 film dan tidak seri, selain itu Campur |
| `_logo(color)` | Logo Rakfilm untuk watermark (K53): bentuk dari kanal alfa `rakfilm_mark.png`, diwarnai dengan warna teks tema |

### Baris penting

**Headline otomatis mengecil:**
```python
for size in range(200, 99, -6):            # coba 200 px, 194 px, ... sampai 100 px
    ... bungkus kata per baris selama lebarnya muat ...
    if len(lines) <= 3: return font, lines
```
Headline pendek ("Aksi seru nonstop.") tampil 200 px dalam 2 baris. Headline panjang otomatis mengecil sampai muat dalam 3 baris.

**Pita film miring:**
```python
strip.rotate(3, resample=Image.BICUBIC, expand=True)
canvas.paste(strip, (x, y), strip)
```
Pita digambar lurus di gambar terpisah (RGBA, latarnya transparan), lalu diputar 3° berlawanan arah jarum jam, sama dengan `rotate(-3deg)` di CSS desain R&D. `expand=True` memperbesar kanvas supaya sudutnya tidak terpotong. Argumen ketiga `paste` adalah mask transparansi, jadi sudut kosongnya tidak menutupi latar oranye.

**Teks AI dengan cadangan:**
```python
try:   ... LLM → json.loads → validasi (≥2 headline, ≤6 kata, ada ajakan) ...
except Exception: pass
return fallback_text(movies)
```
Story adalah fitur tambahan, jadi apa pun yang gagal (jaringan, JSON rusak, format salah), pengguna tetap bisa membuat story dari aturan cadangan.

> 🎬 **Untuk video:** "Pengguna menambahkan sampai 4 film ke watchlist, lalu menekan Buat IG story. LLM menulis 3 pilihan headline dari genre filmnya, dengan prompt di Langfuse. Pillow menggambar story 1080×1920 dengan desain yang saya pilih dari 3 prototipe. Watermark di bawah membuat setiap story yang dibagikan menjadi promosi gratis."

> 🎬 **Untuk video:** "Jawaban mengalir kata demi kata. Di bawahnya ada poster film yang disebut, link tempat menonton, tool apa yang dipanggil beserta argumennya, jumlah token, dan tombol 👍/👎 yang masuk ke Langfuse. Di sidebar ada contoh pertanyaan dan total biaya sesi. Riwayat chat dikirim utuh ke agent, jadi saya bisa bertanya lanjutan seperti 'yang kedua siapa sutradaranya?'."

---

## 10. Tampilan Rakfilm: tema, logo, tata letak (K50, K51)

### File yang terlibat
| File | Tugas |
|---|---|
| `.streamlit/config.toml` | Tema: warna mode terang dan gelap, font IBM Plex, sudut 6 px, `enableStaticServing` untuk folder `static/` |
| `static/fonts/` | Anton (wordmark dan judul film) + IBM Plex Mono (story), lisensi OFL. Dipakai app **dan** story |
| `scripts/make_logo.py` | Menggambar logo dengan Pillow → `static/rakfilm_mark.png` |
| `app/movie_cards.py` | Komponen kartu (layout `list`, `grid`, `wall`, `rack`) + `movie_hero` (bagian atas panel detail) |
| `streamlit_app.py` | Sidebar, tampilan awal, chat, panel detail, panel story |

### Baris penting

**Dua mode, satu file:**
```toml
[theme.light]
primaryColor = "#C2410C"
[theme.dark]
primaryColor = "#D2430E"
```
Kalau `[theme.light]` dan `[theme.dark]` sama-sama diisi, Streamlit memunculkan pilihan terang/gelap di menu Settings. Oranye tombol berbeda per mode karena **teks tombol utama Streamlit selalu putih**: oranye logo `#F2531B` hanya 3,5:1 untuk teks putih, sedangkan batas keterbacaan 4,5:1.

**Font sendiri dari `static/`:**
```toml
[[theme.fontFaces]]
family = "Anton"
url = "app/static/fonts/Anton-Regular.ttf"
```
Streamlit menyajikan isi folder `static/` di alamat `app/static/...`. Setelah didaftarkan, font Anton bisa dipakai di seluruh halaman, termasuk di dalam komponen kartu (shadow DOM tetap memakai font yang terdaftar di dokumen).

**Logo sebagai kode:**
```python
draw.rounded_rectangle(box(3, 9, 42, 30), radius=6 * SCALE, fill=ORANGE)   # bingkai
draw.rounded_rectangle(box(x, 12, 4, 3), radius=SCALE, fill=(0, 0, 0, 0))  # lubang transparan
mark = mark.rotate(3, resample=Image.BICUBIC)                              # miring 3°
```
Logo digambar dari koordinat yang sama dengan SVG di mockup (grid 48×48, dikali 10 supaya tajam). Lubangnya transparan, jadi warna latar sidebar (gelap atau terang) yang terlihat melalui lubang itu.

**Tampilan awal hanya saat chat kosong:**
```python
question = st.chat_input("Ceritakan film yang kamu cari…", height=92) or st.session_state.pop("pending", None)
if not st.session_state.chat and not question:
    st.title("Mau nonton apa?") ...
```
`st.chat_input` dipanggil **sebelum** isi halaman, karena kotak chat selalu menempel di bawah layar di mana pun dipanggil. Dengan begitu, saat contoh pertanyaan diklik, tampilan awal langsung hilang di rerun yang sama, tidak berkedip dulu.

**Satu panel per rerun:**
```python
if (opened := rack_click if rack_click is not None else wall_click) is not None:
    movie_dialog(opened)
elif story_click:
    story_dialog()
```
Streamlit hanya bisa membuka satu `st.dialog` dalam satu rerun. Klik dari rak, dinding poster, dan tombol story dikumpulkan dulu, lalu satu panel dibuka di akhir skrip.

**Hover ala Netflix (K52), di `app/movie_cards.py`:**
```css
.card:hover .frame img { transform: scale(1.06); }
.card:hover .frame { box-shadow: 0 10px 24px rgba(0, 0, 0, 0.45); }
```
`.frame` punya `overflow: hidden`. Jadi poster membesar **di dalam** bingkainya, tidak menabrak kartu sebelah, dan bayangannya membuat kartu terlihat terangkat. Kalau pengguna menyalakan "kurangi animasi" di sistem operasinya, `prefers-reduced-motion` mematikan efek ini.

**Latar kaca saat kartu disorot (K54):**
```css
.glass { inset: -30px; filter: blur(22px) brightness(0.5) saturate(1.25); opacity: 0; transition: opacity 0.3s ease; }
.glassy:hover .glass, .glassy:hover::after { opacity: 1; }
```
Setiap kartu hasil yang punya poster diberi lapisan `.glass`: poster yang sama, diperbesar lalu diburamkan. Lapisan ini tidak terlihat (`opacity: 0`) sampai kartunya disorot, lalu muncul pelan dalam 0,3 detik dan teks berganti terang. Jadi tiap film punya warna hover sendiri: *Gravity* biru angkasa, *Avatar* biru-oranye.

Detail tampilannya:
- `inset: -30px` membuat gambar lebih lebar dari kartu, jadi tepi blur yang pudar terpotong dan tidak terlihat
- blur menyembunyikan piksel yang pecah karena poster kecil diperbesar
- lapisan gelap 32% menjaga teks putih tetap terbaca, di poster terang sekalipun

**Label "Muat" yang jujur (K52), di `streamlit_app.py`:**
```python
left = more["total"] - len(shown) if more.get("total") is not None else None
label = "Muat lebih banyak" if left is None else f"Muat {min(PAGE_SIZE, left)} film lagi"
```
- `rank_movies` menyaring data, jadi totalnya diketahui (Tom Hanks 14 film, 10 tampil → "Muat 4 film lagi"). Kalau sisanya 0, tombolnya tidak muncul.
- Pencarian makna (`search_movies`) tidak punya total karena hasilnya selalu "film paling mirip berikutnya". Karena itu labelnya tidak menyebut angka.

**Logo di IG story (K53), di `app/story.py`:**
```python
alpha = Image.open(LOGO).getchannel("A").resize((size, size), Image.LANCZOS)
mark = Image.new("RGBA", (size, size), color)
mark.putalpha(alpha)
```
Kanal alfa menyimpan bentuk logo: piksel logo bernilai 255, latar dan lubang sproket bernilai 0. Bentuk itu dipasang ke kotak satu warna (warna teks tema). Hasilnya logo yang sama, tapi warnanya mengikuti tema, sehingga tetap terbaca di latar kuning Komedi maupun hitam Horor.

> 🎬 **Untuk video:** "Namanya Rakfilm. Tampilannya sengaja netral; warna datang dari poster filmnya, seperti Netflix atau Letterboxd. Tema terang dan gelap diatur di satu file config, logonya digambar dengan kode, dan semuanya memakai fitur resmi Streamlit, bukan CSS tempelan yang bisa rusak saat Streamlit di-update."
