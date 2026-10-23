# Penjelasan Kode: Bahan Belajar dan Video

> Untuk memahami dan menjelaskan ulang setiap file. Diperbarui setiap kali file baru selesai.
> Isi per file: **tugasnya**, **fungsi dan baris penting**, **pertanyaan yang mungkin ditanyakan** beserta jawabannya, dan **kalimat siap pakai untuk video**.
> Alasan memilih satu cara dibanding cara lain ada di `keputusan-desain.md` (kode K01, K02, ...).

## Daftar isi
1. [Persiapan: `.env` dan environment](#1-persiapan-env-dan-environment)
2. [`scripts/check_connections.py`](#2-scriptscheck_connectionspy)
3. [`app/data.py`](#3-appdatapy)

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
