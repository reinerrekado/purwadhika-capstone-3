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
Berisi fungsi-fungsi yang **boleh dipanggil agent**. Untuk sekarang baru satu: `search_movies` (RAG + filter). Dua tool lain menyusul di Fase 3.

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

### Pertanyaan yang mungkin ditanyakan
**T: Bagaimana LLM tahu kapan harus memanggil `search_movies`?**
J: Dari docstring-nya: "Use this when the user describes what they want to watch instead of naming a title." LLM membaca deskripsi semua tool, lalu memilih yang cocok dengan pertanyaan (Sesi 10: tool calling).

**T: Siapa yang menentukan genre "Thriller" dan tahun 1990–1999?**
J: LLM, dari kalimat user "thriller tahun 90-an". Tapi yang **menjalankan** filter adalah kode dan Qdrant. LLM hanya mengusulkan argumen, kode yang memutuskan hasilnya.

> 🎬 **Untuk video:** "Ini tool RAG saya. LLM hanya mengisi argumen: query dalam bahasa Inggris, genre, dan tahun. Genre dikunci ke 21 pilihan dari dataset, jadi LLM tidak bisa salah ketik."

---

## 7. `app/agent.py`

### Tugasnya
Merakit **agent ReAct**: LLM + tools + system prompt dari Langfuse, dan mencatat setiap run ke Langfuse.

### Fungsi-fungsinya

| Fungsi | Tugas |
|---|---|
| `get_agent()` | Ambil system prompt dari Langfuse, lalu `create_agent(model, tools, system_prompt)`. Dibuat sekali (`@lru_cache`) |
| `run_agent(messages, session_id)` | Jalankan agent dengan seluruh riwayat, lalu kembalikan **hanya pesan baru** dari run ini |

### Baris penting

**System prompt dari Langfuse, bukan hardcode:**
```python
system_prompt = get_client().get_prompt("movie-agent-system").compile()
```
`get_prompt` mengambil versi berlabel `production` (Sesi 17). Prompt bisa diubah di UI Langfuse tanpa mengubah kode, dan setiap versinya tercatat.

**Tracing ke Langfuse:**
```python
config={"callbacks": [CallbackHandler()],
        "metadata": {"langfuse_session_id": session_id}}
```
`CallbackHandler` mencatat semuanya: setiap panggilan LLM, setiap tool call beserta argumen dan hasilnya, token, dan waktu. `langfuse_session_id` mengelompokkan semua pertanyaan dalam satu percakapan menjadi satu **session** di Langfuse. Di Langfuse v3 ke atas, session dikirim lewat `metadata`, bukan lewat argumen `CallbackHandler(...)` seperti di slide 27 (K02).

**Hanya pesan baru:**
```python
return result["messages"][len(messages):]
```
`agent.invoke` mengembalikan **seluruh** percakapan: riwayat lama + pesan baru. Kalau riwayatnya berisi 3 pesan, pesan baru dimulai dari indeks 3. Tanpa pemotongan ini, tool call dan token dari pertanyaan sebelumnya ikut terhitung lagi (kritik diri #5).

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
J: Itu akan mengakses jaringan (Langfuse, Qdrant) begitu file di-import, padahal arahannya modul tidak boleh punya efek samping saat di-import. Dengan `@lru_cache`, agent dibuat sekali, saat pertanyaan pertama masuk (K24).

**T: Kenapa memilih `gpt-4.1-mini`?**
J: Dari uji 6 model: nano sempat salah menulis judul ("Seance of the Lambs"), DeepSeek berhalusinasi, Gemini lite kena rate limit, gpt-5-mini 3× lebih lambat. gpt-4.1-mini cepat (±4 dtk), teliti, dan murah (<$1 per 1.000 pertanyaan) (K23).

> 🎬 **Untuk video:** "Agent saya dibuat dengan `create_agent`. System prompt-nya tidak ditulis di kode, tapi diambil dari Langfuse. Setiap run dicatat ke Langfuse dan dikelompokkan per sesi percakapan."

---

## 8. `streamlit_app.py`

### Tugasnya
Hanya **tampilan**. Semua logika ada di `app/agent.py` (arahan modular Pak Herman). Menampilkan tiga hal wajib: **chat history**, **tool call**, dan **usage**.

### Fungsi-fungsinya

| Fungsi / bagian | Tugas |
|---|---|
| `st.session_state.chat` | Riwayat percakapan yang bertahan selama sesi browser |
| `st.session_state.session_id` | Id acak per sesi, dikirim ke Langfuse |
| `summarize_run()` | Dari pesan baru, ambil tool call (nama, argumen, judul hasil) dan jumlahkan token |
| `show_details()` | Expander "🔧 tool call" + baris jumlah token |
| loop `for message in ...` | Menggambar ulang chat history setiap rerun |
| `st.chat_input` | Kotak ketik; `:=` (*walrus*) menyimpan isi ketikan sekaligus mengecek apakah ada isinya |

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

### Menjalankan
```
streamlit run streamlit_app.py
```

> 🎬 **Untuk video:** "Di bawah setiap jawaban ada dua hal: tool apa yang dipanggil beserta argumennya, dan berapa token yang dipakai. Riwayat chat dikirim utuh ke agent, jadi saya bisa bertanya lanjutan seperti 'yang kedua siapa sutradaranya?'."
