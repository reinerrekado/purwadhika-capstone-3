# Naskah Video Capstone 3: Rakfilm

> Target **±14 menit** (batas 7–15 menit, cadangan ±1 menit). Wajah terlihat di box sepanjang video, kode terbaca.
> Urutan wajib: intro → tujuan (pitch ke C-level) → langkah membangun → alur app + tools → demo langsung → kode per fungsi (Streamlit → agent → tools → DB) → outro.
> Konsep: demo biasa ditambah satu cerita **"dari trace ke perbaikan"** di Langfuse (referensi: *LLM Observability with Langfuse: Debugging a Broken RAG Agent*).
> Semua angka di naskah ini dicek ulang dengan dataset, `notes/hasil-uji.md` (7 Nov 17:09), dan kode per 7 Nov.
> **Slide** untuk bagian 1–4 dan 7, plus kartu bab 5 dan 6: deck [Rakfilm · Video](https://claude.ai/artifact/JiPx25xd1TqpwDXGJyHo1W), 17 slide, gaya "Bioskop malam". Slide diagram (fase offline, bagan tiga agent, alur satu pertanyaan) memakai **mode diagram**: panel lebar dan wajah kecil di pojok kanan bawah. Isinya dari artefak Anatomi, dicocokkan ulang dengan kode pada 7 Nov. Catatan pembicara tiap slide berisi kalimat naskah ini. Komposisi mengikuti video contoh: rangka dua panel bersudut 28 px. **Panel kiri 1144×952** (x 64, y 64) untuk slide atau rekaman layar, **panel kanan 600×952** (x 1256, y 64) untuk wajah. Untuk bagian rekaman layar dipakai gambar rangka transparan `rakfilm-rangka-1920x1080.png` dengan geometri yang sama.

Cara membaca: **Layar** = yang terlihat, **Aksi** = yang diklik atau diketik, kutipan (`>`) = yang diucapkan. Kalimat boleh diubah ke gaya bicaramu sendiri; angkanya jangan.

## Ringkasan durasi

| # | Bagian | Waktu | Durasi | Layar utama |
|---|---|---|---|---|
| 1 | Intro | 0:00–0:30 | 0:30 | Slide judul |
| 2 | Tujuan (pitch ke C-level) | 0:30–1:45 | 1:15 | Slide masalah → solusi → bukti |
| 3 | Langkah membangun | 1:45–3:15 | 1:30 | Slide garis waktu, lalu diagram fase offline (mode diagram) |
| 4 | Alur app + tools | 3:15–5:45 | 2:30 | Mode diagram: bagan tiga agent, lalu bagan yang sama untuk alur 7 langkah; lalu slide harga |
| 5 | Demo langsung (app, lalu Langfuse) | 5:45–9:25 | 3:40 | App publik, Langfuse |
| 6 | Kode per fungsi (Streamlit → agent → tools → DB, lalu Qdrant) | 9:25–13:10 | 3:45 | VS Code, dashboard Qdrant |
| 7 | Outro | 13:10–13:55 | 0:45 | Slide ringkasan |

---

## Persiapan sebelum merekam

- [ ] **Kuota OpenRouter:** cek sisa batas key (±$1,8 per 7 Nov) dan naikkan sebelum rekaman. Kalau kuota habis di tengah demo, app menampilkan "Maaf, Rakfilm sedang tidak bisa menjawab".
- [ ] **Bangunkan app** https://imdb-movie-assistant.streamlit.app/ (tidur setelah ±12 jam), lalu coba sekali di jendela incognito.
- [ ] **Qdrant:** cluster aktif di dashboard dan collection `imdb_movies` terbuka.
- [ ] **Langfuse:** login (cloud.langfuse.com, EU). Buka di tab terpisah: *Sessions* dan *Prompts*.
- [ ] **Gladi bersih sekali** untuk ketiga pertanyaan demo di jendela lain (±Rp150). Sesi gladi ini juga jadi cadangan untuk ditunjukkan di Langfuse.
- [ ] **Urutan tab browser:** slide → app → Langfuse → Qdrant → README di GitHub.
- [ ] **VS Code:** buka tab berurutan `streamlit_app.py`, `app/agent.py`, `app/tools.py`, `app/rerank.py`, `app/data.py`, `scripts/ingest.py`. Tutup sidebar (`Ctrl+B`), matikan minimap, zoom 2× (`Ctrl+=`), nyalakan word wrap (`Alt+Z`) supaya baris panjang tetap di dalam panel kiri. Lompat ke baris dengan `Ctrl+G`.
- [ ] **Ukuran jendela yang direkam:** browser dan VS Code dibuat kira-kira **1144×952** (rasio panel kiri), lalu direkam per jendela. Dengan begitu skalanya hampir 1:1 dan teks tidak mengecil. Display scaling Windows 100%.
- [ ] **Notifikasi:** nyalakan *Do not disturb* Windows, tutup WhatsApp dan email.
- [ ] **Uji rekam 20 detik:** suara jelas, dan kode masih terbaca di 1080p.

**Rangka dan wajah.** Ada dua mode rangka:
- **Mode dua panel** (hampir seluruh video): panel kiri berisi slide atau layar, panel kanan 600×952 berisi wajah.
- **Mode diagram** (slide fase offline, bagan tiga agent, alur satu pertanyaan): panel lebar 1792×952, wajah mengecil ke kotak 352×440 di pojok kanan bawah (x 1480, y 552). Rangka transparannya `rakfilm-rangka-diagram-1920x1080.png`. Perpindahan mode cukup dipotong (cut), tidak perlu animasi.

Di mode Present, slide bagan dan alur memunculkan isinya bertahap: bagan 4 klik (supervisor, rag_agent, data_agent, Langfuse), alur 7 klik (**satu klik = satu langkah**). Bicara dulu, baru klik berikutnya.
- **Bagian slide (1–4, 7, dan kartu bab 5–6):** rekam deck dalam mode Present layar penuh. Rangkanya sudah ada di slide, jadi cukup isi panel kanan dengan video wajah.
- **Bagian rekaman layar (demo, Langfuse, kode, Qdrant):** di editor, susun tiga lapis dari bawah ke atas:
  1. rekaman layar, diperbesar sampai menutup lubang kiri
  2. video wajah, di-crop potret, menutup lubang kanan
  3. `rakfilm-rangka-1920x1080.png` di paling atas, sepanjang video

  Sudut membulat otomatis ikut dari gambar rangka.
- **Alat:** Clipchamp bawaan Windows 11 (bisa banyak track dan menerima PNG transparan) atau OBS (Image source untuk rangka di urutan teratas, Display/Window Capture dan Video Capture Device di bawahnya).
- **Kamera:** rekam wajah dengan latar rapi dan cahaya dari depan. Yang terlihat hanya potongan potret 600×952, jadi posisikan wajah di tengah frame kamera.

---

## 1 · Intro · 0:00–0:30

**Layar:** slide judul: "Rakfilm: asisten film agentic RAG · IMDB Top 1000", link app dan repo (deck slide 1).

> Halo, saya Reiner [nama lengkap], peserta Purwadhika JCAIEH. Ini video Capstone Modul 3 saya: **Rakfilm**, asisten film berbasis agentic RAG di atas dataset IMDB Top 1000.
> Dalam ±13 menit saya tunjukkan masalah yang diselesaikan, cara saya membangunnya, demo langsung, lalu kodenya fungsi per fungsi.

---

## 2 · Tujuan: pitch ke C-level · 0:30–1:45

**Layar:** 3 slide berurutan: **Masalah** → **Solusi** → **Kenapa bisa dipercaya**. Teks besar, tanpa istilah teknis.

**Slide Masalah** (±20 dtk)
> Bayangkan Anda mengelola katalog film. Masalah pengguna bukan kurang pilihan. Mereka tahu **suasana** film yang ingin ditonton, tapi tidak tahu **judulnya**: "film tentang pencuri yang masuk ke mimpi orang". Pencarian biasa butuh judul atau genre yang persis, jadi pencarian seperti ini gagal, dan pengguna pergi.

**Slide Solusi** (±25 dtk)
> Rakfilm menerima cerita bebas seperti itu, mencarikan film yang cocok dari 1.000 film terbaik IMDB, dan menjelaskan alasannya dengan data: rating, sutradara, dan pemain. Rakfilm juga menjawab pertanyaan yang jawabannya pasti, misalnya "ada berapa film Miyazaki tahun 2000-an", langsung dari tabel, bukan tebakan. Pengguna bahkan bisa mengubah rak tontonannya jadi IG story berlogo Rakfilm, jadi setiap story yang dibagikan adalah promosi gratis.

**Slide Kenapa bisa dipercaya** (±30 dtk)
> Ada tiga hal yang penting untuk bisnis.
> Pertama, **jawaban hanya dari data**: Rakfilm tidak mengarang film di luar katalog.
> Kedua, **setiap jawaban bisa diaudit**: tool yang dipanggil, dokumen yang dipakai, dan biayanya terlihat di layar, dan semuanya tercatat di Langfuse.
> Ketiga, **murah dan terukur**: sekitar Rp20 sampai Rp60 per pertanyaan, dan kualitasnya diukur dengan 17 pertanyaan uji otomatis yang saat ini lolos semua.

---

## 3 · Langkah membangun · 1:45–3:15

**Layar:** slide garis waktu 4 langkah, lalu slide "Fase offline" (mode diagram) untuk detail langkah 2.

> Saya membangun dengan prinsip **irisan tipis**: versi paling sederhana yang berjalan dari ujung ke ujung dibuat dulu dan langsung di-deploy, baru kemudian dilengkapi. Masalah integrasi jadi ketahuan di hari pertama, bukan di minggu terakhir.

**Langkah 1 · 21–22 Okt: rencana dan data** (±20 dtk)
> Saya memilih kasus IMDB, lalu EDA. Datanya punya masalah: tahun Apollo 13 berisi "PG", ada dua film berbeda berjudul Drishyam, dan pendapatan tersimpan sebagai teks. Semua pembersihan saya taruh di satu file, `data.py`. Sebelum menulis kode, saya mengajukan klarifikasi ke Pak Herman dan mencatat setiap keputusan.

**Langkah 2 · 23 Okt: ingest dan irisan pertama** (±30 dtk)
> Saya cek dulu koneksi ke OpenRouter, Qdrant, dan Langfuse. Lalu ingest: 1.000 film menjadi 1.000 vektor di Qdrant dalam ±39 detik. Saya tidak memakai chunking, karena teks per film rata-rata hanya 185 karakter; dengan potongan 500 karakter, tidak ada satu film pun yang terpecah. Di hari yang sama, satu tool, agent, Streamlit, dan prompt di Langfuse sudah berjalan dan ter-deploy.

**Langkah 3 · 23–25 Okt: fitur dan uji** (±20 dtk)
> Setelah itu tool bertambah jadi lima, ditambah reranker, bio dan foto 3.202 sutradara dan pemain dari Wikipedia, UI Rakfilm, dan set uji otomatis 17 pertanyaan yang menjalankan agent sungguhan.

**Langkah 4 · 7 Nov: arsitektur supervisor** (±20 dtk)
> Terakhir arsitektur supervisor. Prototipe pertama hanya lolos 12 dari 17 pertanyaan. Setelah tiga perbaikan, 17 dari 17.
> Semua keputusan saya catat beserta alasannya: ada 81 keputusan di `keputusan-desain.md`. Pola yang paling sering muncul: model sering mengabaikan aturan yang hanya ditulis di prompt. Jadi aturan yang penting saya tegakkan di kode, lalu saya uji ulang.

---

## 4 · Alur app + tools · 3:15–5:45

**Layar:** mode diagram (wajah kecil di pojok kanan bawah): **bagan** tiga agent, lalu **bagan yang sama** untuk alur satu pertanyaan. Lalu kembali ke mode dua panel untuk slide "Supervisor: alasan dan harganya". Isinya dari artefak Anatomi (Dimensi 2 dan tabel agent), dicocokkan ulang dengan kode pada 7 Nov. Dua koreksi dari versi sebelumnya: prompt diambil `agent.py` sebelum run, bukan oleh supervisor di tengah jalan ([agent.py:106](../app/agent.py#L106)); trace dan jempol dikirim dari app, bukan dari supervisor. Slide "siapa menyalakan siapa" dibuang; intinya (LLM hanya memilih dan menulis) diucapkan di alur.

**Bagan: tiga agent, lima tool** (±60 dtk, klik 4 kali)
> Definisinya dulu: **agent = LLM + prompt + tool**. Setiap kartu bergaris oranye di sini adalah satu agent, dan isinya selalu tiga baris itu.
> *[klik]* Pertanyaan dari layar Streamlit masuk ke **supervisor**. LLM-nya `gpt-4.1-mini`, prompt-nya `movie-supervisor-system`, dan tool-nya hanya tombol oper. Tugasnya memilih sub-agent; ia menjawab sendiri hanya untuk pertanyaan di luar topik film.
> *[klik]* **rag_agent** untuk cari dari cerita. `search_movies` dan `similar_movies` membaca vektor di Qdrant; `search_movies` juga memakai reranker yang memilih 5 dari 15 kandidat.
> *[klik]* **data_agent** untuk fakta, peringkat, dan orang. `get_movie_details` dan `rank_movies` membaca tabel 1.000 film dengan pandas, `get_person_info` membaca bio di `people.csv`.
> *[klik]* Prompt ketiga agent disimpan di **Langfuse**, bukan di kode, dan setiap run dicatat balik ke sana sebagai trace.

**Alur: satu pertanyaan, tujuh langkah** (±70 dtk, bagan yang sama, klik 7 kali)
> Sekarang satu pertanyaan: "film tentang pencuri yang masuk ke mimpi orang". Nomor berlatar oranye dikerjakan LLM, nomor bergaris dikerjakan kode.
> *[klik]* **1**, Streamlit mengirim pertanyaan beserta seluruh riwayat sesi ke supervisor.
> *[klik]* **2**, LLM supervisor memilih rag_agent, lewat tombol oper.
> *[klik]* **3**, LLM rag_agent menulis tool call: `search_movies`, beserta argumennya. LLM tidak menjalankan apa pun; ia hanya menulis permintaan.
> *[klik]* **4**, kode yang menjalankannya: Qdrant mengambil 15 kandidat yang maknanya paling dekat.
> *[klik]* **5**, reranker memilih 5 terbaik, dan hasilnya kembali ke rag_agent sebagai JSON.
> *[klik]* **6**, LLM rag_agent menulis jawaban dari JSON itu, dan jawabannya mengalir ke layar bersama tool call dan usage.
> *[klik]* **7**, kendali kembali ke supervisor, dan seluruh run tercatat di Langfuse; jempol pengguna masuk sebagai skor.
> Jadi LLM hanya memilih dan menulis. **Mencari, menyaring, dan menghitung dikerjakan kode.** Untuk pertanyaan peringkat atau fakta, jalurnya sama, hanya lewat data_agent dan pandas.

**Kenapa bentuknya begini** (±20 dtk, kembali ke dua panel)
> Kenapa supervisor, bukan swarm? Pertanyaan film hampir selalu jatuh ke satu bidang, jadi cukup satu supervisor yang memilih. Kenapa dua sub-agent, bukan lima? Pembagiannya mengikuti dua jenis sumber: vektor dan tabel. Harganya saya ukur: set uji tetap 17 dari 17, biaya sekitar 10% lebih mahal, dan rata-rata 6,9 detik per pertanyaan dibanding 4,3 detik dengan agent tunggal.

---

## 5 · Demo langsung · 5:45–9:25

### 5a · App · 5:45–8:00

**Layar:** app publik di browser biasa (bukan localhost), mode gelap, direkam di panel kiri.

**Beranda** (±10 dtk)
> Ini app publiknya. Dinding poster diacak dari 1.000 film. Di bawah ada contoh pertanyaan, dan di sidebar ada rak tontonan.

**Pertanyaan 1 · RAG** (±45 dtk)
- **Aksi:** klik contoh **"pencuri yang masuk ke mimpi"** (mengirim "Film tentang pencuri yang masuk ke mimpi orang").
> Jawabannya mengalir kata demi kata. Inception muncul sebagai kartu poster.
- **Aksi:** buka expander **"supervisor → rag_agent · 1 tool call"**.
> Di judulnya terlihat rutenya: supervisor mengoper ke rag_agent. Argumennya `search_movies` dengan query **berbahasa Inggris**, karena sinopsis di dataset berbahasa Inggris. Di bawahnya dokumen yang dipakai: 15 kandidat dari Qdrant yang diurutkan ulang reranker, masing-masing dengan skor kemiripan vektor dan skor reranker. Paling bawah: token input dan output serta biayanya dalam Rupiah dan dolar.

**Pertanyaan 2 · data + typo** (±40 dtk)
- **Aksi:** ketik **`film christoper nolan`** (typo disengaja).
> Saya sengaja salah ketik. Kali ini supervisor mengoper ke data_agent, yang memanggil `rank_movies` dengan sutradara Nolan.
- **Aksi:** buka expander. Tunjuk baris **"Hasil: 8 film cocok · rata-rata rating 8,46"**.
> Angka di jawaban bisa dicek langsung di panel: 8 film, rata-rata rating 8,46.
- **Aksi (kalau tombolnya muncul):** klik **"Muat 3 film lagi"**.
> Tombol ini mengambil sisa hasil langsung dari tool, tanpa memanggil LLM.
- **Aksi:** klik 👍 di bawah jawaban ini (nanti ditunjukkan di Langfuse).

**Pertanyaan 3 · ingatan percakapan** (±30 dtk)
- **Aksi:** ketik **`yang mana paling lama?`**
> Saya tidak menyebut Nolan lagi. Agent tahu dari riwayat sesi: jawabannya **Interstellar (2014), 169 menit**. Riwayat dikirim utuh dari Streamlit setiap giliran, tanpa database tambahan.

**Panel film dan orang** (±25 dtk)
- **Aksi:** klik poster **Interstellar** → panel film (sinopsis bahasa Indonesia, fakta menarik) → klik **Christopher Nolan** → panel orang (foto, bio, filmnya).
> Panel ini tanpa LLM, jadi tanpa biaya token. Sinopsis dan bio sudah diterjemahkan sekali secara offline.

**(Opsional, lewati kalau waktu mepet) di luar topik** (±10 dtk)
- **Aksi:** ketik **`cara masak rendang`**.
> Supervisor menjawab sendiri tanpa sub-agent, dan panelnya menulis itu.

**Sidebar** (±5 dtk)
> Di sidebar terlihat total pertanyaan, token, dan biaya sesi ini.

### 5b · Langfuse: dari trace ke perbaikan · 8:00–9:25

**Layar:** Langfuse (mode gelap), direkam di panel kiri.

**Session dan trace** (±45 dtk)
- **Aksi:** *Tracing → Sessions* → session paling atas (yang baru dibuat) → terlihat trace per pertanyaan dalam satu session.
> Satu percakapan di app menjadi satu session di Langfuse, dan setiap pertanyaan menjadi satu trace.
- **Aksi:** buka trace kedua (kolom Input berisi **"film christoper nolan"**) → tab **Tree** (jangan Graph). Klik berurutan: `supervisor` → `transfer_to_data_agent` → `data_agent` → `rank_movies` (Input: argumen, Output: `matching_count: 8`) → kembali ke `supervisor`.
> Urutan kerjanya terlihat lengkap: supervisor mengoper, data_agent memanggil rank_movies dengan argumen ini, hasilnya 8 film, lalu kembali ke supervisor. Di atas ada tag versi prompt, `prompt-v8` dan `supervisor-v1`, latensi, token, dan biaya. Skor 👍 yang saya klik tadi menempel di trace yang sama sebagai `user_feedback`.

**Prompt di Langfuse** (±30 dtk)
- **Aksi:** *Prompts* → daftar 5 prompt → buka `movie-supervisor-system` v1, scroll aturan routing-nya.
> Tidak ada prompt di kode. Prompt supervisor berisi aturan memilih sub-agent.
- **Aksi:** buka `movie-agent-system` → daftar versi v1 sampai v9. Tunjuk label **production di v8** dan **staging di v9**.
> Ini prompt kedua sub-agent. Namanya dari masa agent tunggal, jadi saya pertahankan supaya riwayat v1 sampai v8 tidak hilang. Setiap versi lahir dari satu temuan uji.

**Cerita perbaikan** (±30 dtk)
> Satu contoh. Saya mencoba v9 untuk merapikan prompt, dengan label staging, sehingga app publik tetap memakai v8. Set uji turun ke 15 dari 17. Di trace terlihat penyebabnya: untuk "ada berapa film Hayao Miyazaki tahun 2000-an", data_agent memakai tool yang salah lalu menghitung sendiri, dan hasilnya 4 film, padahal yang benar 3. Jadi production tetap di v8. Mengganti versi di Langfuse cukup memindah label, tanpa deploy ulang.
> Pertanyaan Miyazaki yang sama pernah gagal dengan cara lain: Miyazaki dicari sebagai aktor, bukan sutradara. Itu saya perbaiki di kode, nanti saya tunjukkan di `tools.py`.

*(Opsional, kalau ditemukan cepat: Traces → filter tag `prompt-v9` → buka trace pertanyaan Miyazaki. Kalau mencari lebih dari 10 detik, lewati.)*

---

## 6 · Kode per fungsi · 9:25–13:10

**Layar:** VS Code (persiapan di atas). Lompat baris dengan `Ctrl+G`. Jelaskan per fungsi, jangan per baris.

### 6a · `streamlit_app.py`: tampilan · 9:25–10:20

| Baris | Tunjuk | Ucapan |
|---|---|---|
| 1 | docstring | "File ini hanya tampilan. Logika agent ada di `app/agent.py`, sesuai arahan modular." |
| 36–37 | `session_state` | "`chat` menyimpan riwayat percakapan, `session_id` jadi id session di Langfuse." |
| 484–485 | `chat_input ... or pending` | "Pertanyaan datang dari kotak ketik, atau dari tombol contoh dan panel." |
| 500–506 | loop riwayat | "Setiap rerun, seluruh riwayat chat digambar ulang." |
| 517 | `history` | "Yang dikirim ke agent hanya `role` dan `content`, seluruh riwayat. Inilah yang membuat agent ingat percakapan." |
| 523 | `st.write_stream(stream_agent(...))` | "Jawaban dialirkan potong demi potong." |
| 525 | `trim_offer` | "Kalimat penutup berupa tawaran dipotong di kode, karena prompt saja tidak cukup." |
| 117–152 | `summarize_run` | "Dari pesan baru, fungsi ini mengambil rute supervisor dari tombol `transfer_to_`, setiap tool call beserta argumen dan hasilnya, dan menjumlahkan `usage_metadata` dari semua panggilan LLM." |
| 414–449 | `show_details` | "Expander berjudul rute, argumen tool di `st.code`, dokumen dengan skor vektor dan reranker, usage dalam Rupiah dan dolar, lalu tombol 👍/👎 yang dikirim ke Langfuse lewat `save_feedback`." |
| 529–534 | `except` | "Kalau layanan gagal, pengunjung melihat pesan yang jelas, dan galat lengkapnya masuk log." |

### 6b · `app/agent.py`: supervisor dan sub-agent · 10:20–11:25

| Baris | Tunjuk | Ucapan |
|---|---|---|
| 1–3 | docstring | "Agent = LLM + prompt + tool. Supervisor memilih sub-agent, sub-agent memanggil tool film." |
| 75–90 | `_build_agent` | "Di sini tiga agent dibuat. Kedua prompt diambil dari Langfuse dengan nomor versinya. `rag_agent` dibuat dengan `create_agent` dan dua tool Qdrant, `data_agent` dengan tiga tool data. `create_supervisor` menggabungkan keduanya, dengan `forward_message` untuk meneruskan jawaban sub-agent. `.with_config(_linked(prompt))` menautkan setiap agent ke prompt Langfuse-nya sendiri. `@lru_cache` membuat agent sekali per versi prompt, bukan setiap pertanyaan dan bukan saat file di-import." |
| 93–97 | `get_agent` | "Prompt berlabel production diambil setiap pertanyaan, tapi SDK menyimpannya 60 detik. Jadi versi baru di Langfuse terpakai tanpa deploy ulang." |
| 107–108 | `reply_language` | "Kalau pertanyaannya berbahasa Inggris, satu baris '(Reply in English.)' ditambahkan di kode, karena aturan bahasa di prompt sering diabaikan." |
| 109–116 | `CallbackHandler`, metadata | "Setiap run di-trace ke Langfuse, dikelompokkan per session, dan diberi tag versi prompt." |
| 118–131 | `agent.stream(..., subgraphs=True)` | "`subgraphs=True` memberi tahu asal setiap potongan teks. Yang tampil di layar adalah jawaban sub-agent. Saya ukur di 145 trace: supervisor hanya meneruskan dengan `forward_message` di 25%, sisanya menulis ulang. Jadi layar dijaga di sini: tulisan ulang supervisor tidak ditampilkan dua kali." |
| 134 | `run.update` | "Setelah selesai, pesan baru dan `trace_id` dititipkan untuk panel tool call dan feedback." |
| 137–142 | `send_feedback` | "👍/👎 disimpan sebagai score di trace yang sama." |

### 6c · `app/tools.py` dan `app/rerank.py`: lima tool · 11:25–12:25

| Baris | Tunjuk | Ucapan |
|---|---|---|
| 24, 27 | `Genre`, `OptionalGenre` | "Genre dikunci ke 21 nilai persis dari dataset, jadi LLM tidak bisa mengarang genre. String kosong diubah jadi tanpa genre, karena sejak supervisor ±8% pencarian mengirim `genre=''` dan sempat galat." |
| 79–100 | `@tool` + docstring `search_movies` | "Decorator `@tool` mengubah fungsi jadi skema yang dibaca LLM: nama, docstring, dan deskripsi tiap argumen. Docstring ini instruksi untuk LLM, jadi ditulis dalam bahasa Inggris." |
| 101–102 | penjaga bahasa | "Kalau query masih berbahasa Indonesia, tool menolak dan agent mengulang dalam bahasa Inggris." |
| 111–127 | `search_page` | "Qdrant mengambil 15 kandidat dengan filter genre dan tahun, reranker memilih 5 terbaik. Kalau reranker gagal, urutan vektor dipakai, jadi pencarian tidak pernah mati." |
| `rerank.py` 13–28 | `rerank` | "Satu panggilan ke endpoint rerank OpenRouter, model `qwen3-reranker-8b`. Kalau gagal, hasilnya `None`." |
| 283–286 | `query_points(query=id)` | "`similar_movies`: query-nya id film, jadi Qdrant memakai vektor film itu sendiri. Tidak ada panggilan embedding tambahan." |
| 294–334 | `rank_movies` | "Tool data dengan pandas: filter, urutkan, dan kembalikan `matching_count` serta `average_rating`. Angka 8 film dan 8,46 di demo tadi datang dari sini." |
| 354–363 | `_fix_role` | "Ini perbaikan Miyazaki tadi. Panel tool call memperlihatkan `rank_movies(star='Hayao Miyazaki')`, 0 film, lalu dijawab 'tidak ada'. Sekarang kalau nama itu di seluruh dataset hanya pernah jadi sutradara, kode mencarinya sebagai sutradara. Diuji 9 kasus dan set uji 17 pertanyaan." |
| 137, 160, 219 | `find_title`, `get_movie_details`, `get_person_info` | "Dua tool lain: detail judul dengan pencarian 4 lapis yang tahan typo, dan profil orang dari bio Wikipedia yang diambil offline." |

### 6d · DB: `app/data.py`, `scripts/ingest.py`, dashboard Qdrant · 12:25–13:10

| Baris | Tunjuk | Ucapan |
|---|---|---|
| `data.py` 23–47 | `load_movies` | "Satu-satunya tempat pembersihan data, dibaca sekali lalu disimpan di memori. Tahun Apollo 13 dibetulkan. Id memakai nomor baris karena judul Drishyam ada dua. Metascore memakai `Int64`, bulat tapi boleh kosong: kalau 157 nilai kosong diisi nol, rata-ratanya turun dari 78 ke 66." |
| `ingest.py` 15–22 | `build_documents` | "Satu film menjadi satu Document. Yang di-embed hanya judul, genre, dan sinopsis. Semua kolom lain ikut sebagai metadata atau payload." |
| `ingest.py` 39–49 | `from_documents` | "Satu panggilan untuk membuat collection, meng-embed per 100 teks, dan mengunggah. `force_recreate` dan id tetap membuat skrip ini aman diulang." |
| `ingest.py` 25–28 | `create_payload_indexes` | "Index untuk genre dan tahun, supaya filter tidak memindai semua point." |

**Dashboard Qdrant** (±20 dtk)
- **Aksi:** Qdrant Cloud → cluster → *Collections* → `imdb_movies`: tunjuk **1.000 points**, **1536 dimensi**, **Cosine**, dan payload index `metadata.genres` (keyword) dan `metadata.year` (integer). Buka satu point (misalnya Inception), tunjuk `page_content` dan `metadata`.
> Ini hasilnya di Qdrant Cloud: 1.000 point, vektor 1.536 dimensi, jarak Cosine. Untuk penilaian, saya menyertakan API key read-only di Google Form, jadi koleksi ini bisa dilihat tanpa bisa diubah.

---

## 7 · Outro · 13:10–13:55

**Layar:** slide ringkasan (angka utama + 3 keterbatasan), lalu slide penutup dengan link.

> Ringkasnya: 3 agent, 5 tool, 1.000 film di Qdrant, prompt dan trace di Langfuse, app publik, dan 17 dari 17 pertanyaan uji lolos.
> Ada keterbatasan yang saya ketahui. Pertanyaan agregat per kelompok, misalnya "genre apa yang rata-rata ratingnya paling tinggi", belum benar, karena `rank_movies` menghitung satu kelompok per panggilan. Langkah berikutnya adalah text-to-SQL dengan koneksi read-only. Supervisor juga lebih sering menulis ulang daripada meneruskan; layar tetap benar karena dijaga di kode. Dan pertanyaan lintas domain baru memanggil satu sub-agent.
> Link app, repo, README, dan laporan lengkapnya ada di deskripsi. Terima kasih.

---

## Pertanyaan demo yang aman

Dipilih dari set uji yang lolos berulang (`notes/hasil-uji.md`). Jawaban LLM tidak persis sama setiap kali, jadi yang dijamin adalah rute, tool, dan film kuncinya.

| # | Ketik | Rute → tool | Yang harus muncul |
|---|---|---|---|
| 1 | klik contoh "pencuri yang masuk ke mimpi" | supervisor → rag_agent → `search_movies` | Inception (2010), dokumen dengan skor vektor dan reranker |
| 2 | `film christoper nolan` | supervisor → data_agent → `rank_movies` | 8 film cocok, rata-rata 8,46; The Dark Knight (9.0) teratas |
| 3 | `yang mana paling lama?` | supervisor → data_agent → `rank_movies` | Interstellar (2014), 169 menit |
| opsional | `cara masak rendang` | supervisor sendiri, tanpa tool | satu kalimat penolakan, "supervisor menjawab sendiri" |

**Cadangan** (juga lolos berulang): `5 film horor terbaik` (Psycho 8.5, The Shining, Alien, Tumbbad, The Thing) · `film yang mirip Interstellar` (Gravity) · `ada berapa film Hayao Miyazaki tahun 2000-an?` (3 film: Sen to Chihiro, Hauru no ugoku shiro, Gake no ue no Ponyo; rata-rata 8,17) · `movies like Inception` (jawaban Inggris).

**Hindari saat rekaman:**
- "ceritakan film Parasite": ±1 dari 6 dioper ke rag_agent yang menemukan film lain
- "genre apa yang rata-rata ratingnya paling tinggi?": dijawab Drama, padahal yang benar War (keterbatasan, cukup disebut di outro)
- pertanyaan lintas domain ("film mirip Interstellar dan siapa sutradaranya"): hanya satu sub-agent yang dipanggil
- judul Inggris film non-Inggris ("Spirited Away"): berhasil di percobaan kedua, tapi panel menulis "Judul tidak cocok" dulu, jadi perlu dijelaskan

## Kalau demo meleset

- **Jawaban aneh tapi panel menulis statusnya** ("Judul tidak cocok", "Peran dibetulkan tool"): lanjutkan dan jelaskan. Panel itu memang dibuat untuk memperlihatkan hal seperti ini.
- **Jawaban salah tanpa penjelasan:** potong, ulang bagian itu dengan "Percakapan baru". Video boleh diedit.
- **"Maaf, Rakfilm sedang tidak bisa menjawab":** hampir pasti kuota OpenRouter. Naikkan batas key, lalu ulang.
- **Trace belum muncul di Langfuse:** tunggu beberapa detik, lalu refresh. Kalau tetap kosong, tunjukkan session gladi bersih.
- **Batas pemakaian:** 30 pertanyaan per sesi browser. "Percakapan baru" tidak mengulang hitungannya, tapi tab incognito baru mengulangnya.

## Setelah merekam

- [ ] Durasi akhir 7–15 menit, wajah terlihat di seluruh video, kode terbaca saat diputar 1080p.
- [ ] Upload ke YouTube (Public atau Unlisted) atau Google Drive ("Anyone with the link"), lalu buka link-nya di jendela incognito.
- [ ] Deskripsi video: link app, repo, README, dan Anatomi.
- [ ] Isi Google Form: repo, video, app, URL Qdrant + key read-only. Sebelum 10 Nov 23:59.
