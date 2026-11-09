"""Daftar segmen video latihan Rakfilm: satu segmen = satu visual + satu potongan narasi (dari notes/naskah-video.md).

visual:
  ("slide", id, step)        gambar slide deck, step = jumlah klik yang sudah terjadi
  ("code", file, a, b, sym)  tampilan VS Code untuk file repo, baris a-b disorot
  ("demo", nama_langkah)     potongan rekaman app publik (dibuat drive_demo.py)
  ("shot", nama)             screenshot Langfuse/Qdrant (placeholder sampai screenshot asli ada)
mode: "two" = rangka dua panel, "wide" = rangka lebar
text kosong = jeda tanpa suara selama `hold` detik.
"""

S = []


def seg(section, label, mode, visual, text="", hold=0.0):
    S.append({"id": f"{len(S) + 1:03d}", "section": section, "label": label, "mode": mode, "visual": visual, "text": text, "hold": hold})


# 1 · Intro -----------------------------------------------------------------------------------------------------------
seg("1", "Intro", "two", ("slide", "cover", 0),
    "Halo, saya Reiner, peserta Purwadhika JCAIEH. Ini video Capstone Modul 3 saya: Rakfilm, asisten film berbasis agentic RAG di atas dataset IMDB Top 1000.")
seg("1", "Intro", "two", ("slide", "cover", 0),
    "Dalam kurang lebih 14 menit saya tunjukkan masalah yang diselesaikan, cara saya membangunnya, demo langsung di app, Langfuse, dan Qdrant, lalu kodenya fungsi per fungsi.")

# 2 · Tujuan ----------------------------------------------------------------------------------------------------------
seg("2", "Tujuan", "two", ("slide", "ch02", 0), hold=2.5)
seg("2", "Tujuan", "two", ("slide", "masalah", 0),
    "Bayangkan Anda mengelola katalog film. Masalah pengguna bukan kurang pilihan. Mereka tahu suasana film yang ingin ditonton, tapi tidak tahu judulnya: film tentang pencuri yang masuk ke mimpi orang. Pencarian biasa butuh judul atau genre yang persis, jadi pencarian seperti ini gagal, dan pengguna pergi.")
seg("2", "Tujuan", "two", ("slide", "solusi", 0),
    "Rakfilm menerima cerita bebas seperti itu, mencarikan film yang cocok dari 1.000 film terbaik IMDB, dan menjelaskan alasannya dengan data: rating, sutradara, dan pemain. Rakfilm juga menjawab pertanyaan yang jawabannya pasti, misalnya ada berapa film Miyazaki tahun 2000-an, langsung dari tabel, bukan tebakan. Pengguna bahkan bisa mengubah rak tontonannya jadi IG story berlogo Rakfilm, jadi setiap story yang dibagikan adalah promosi gratis.")
seg("2", "Tujuan", "two", ("slide", "bukti", 0),
    "Ada tiga hal yang penting untuk bisnis. Pertama, jawaban hanya dari data: Rakfilm tidak mengarang film di luar katalog. Kedua, setiap jawaban bisa diaudit: tool yang dipanggil, dokumen yang dipakai, dan biayanya terlihat di layar, dan semuanya tercatat di Langfuse. Ketiga, murah dan terukur: sekitar 20 sampai 60 rupiah per pertanyaan, dan kualitasnya diukur dengan 17 pertanyaan uji otomatis yang saat ini lolos semua.")

# 3 · Langkah membangun -----------------------------------------------------------------------------------------------
seg("3", "Langkah membangun", "two", ("slide", "ch03", 0),
    "Saya membangun bertahap: versi paling sederhana yang jalan dari ujung ke ujung dibuat dan di-deploy dulu, baru dilengkapi. Masalah integrasi jadi ketahuan di hari-hari pertama, bukan di minggu terakhir.")
seg("3", "Langkah membangun", "two", ("slide", "timeline", 0),
    "Ada 104 commit di repo, dan empat langkah ini urutannya. Langkah pertama, 21 sampai 22 Oktober: saya memilih kasus IMDB, lalu EDA. Datanya punya masalah: tahun Apollo 13 berisi PG, ada dua film berbeda berjudul Drishyam, dan pendapatan tersimpan sebagai teks. Semua pembersihan saya taruh di satu file, data.py. Sebelum menulis kode, saya mengajukan klarifikasi ke Pak Herman dan mencatat setiap keputusan.")
seg("3", "Langkah membangun", "wide", ("slide", "ingest", 0),
    "Langkah kedua, 23 Oktober: versi pertama. Saya cek dulu koneksi ke OpenRouter, Qdrant, dan Langfuse. Lalu ingest: 1.000 film menjadi 1.000 vektor di Qdrant dalam sekitar 39 detik. Saya tidak memakai chunking, karena teks per film rata-rata hanya 185 karakter; dengan potongan 500 karakter, tidak ada satu film pun yang terpecah. Hari itu juga satu tool, agent, Streamlit, dan prompt di Langfuse berjalan dan di-deploy ke Streamlit Cloud; tool kedua dan ketiga menyusul malamnya. Jalur bawah: bio dan foto 3.202 sutradara dan pemain diambil dari Wikipedia, diterjemahkan, dan disimpan di people.csv.")
seg("3", "Langkah membangun", "two", ("slide", "timeline", 0),
    "Langkah ketiga, 24 sampai 25 Oktober, dua hari terpadat dengan 56 commit: tool bertambah jadi lima, ditambah reranker, bio dan foto dari Wikipedia tadi, UI Rakfilm, dan set uji otomatis 17 pertanyaan yang menjalankan agent sungguhan. Setelah itu jeda sampai 6 November karena Modul 4 berjalan.")
seg("3", "Langkah membangun", "two", ("slide", "timeline", 0),
    "Langkah keempat, 7 November: arsitektur supervisor, satu hari. Prototipe pertama hanya lolos 12 dari 17 pertanyaan. Setelah tiga perbaikan, 17 dari 17. Semua keputusan saya catat beserta alasannya: ada 81 keputusan di keputusan-desain.md. Pola yang paling sering muncul: model sering mengabaikan aturan yang hanya ditulis di prompt. Jadi aturan yang penting saya tegakkan di kode, lalu saya uji ulang.")

# 4 · Alur app + tools ------------------------------------------------------------------------------------------------
seg("4", "Alur app dan tools", "two", ("slide", "ch04", 0), hold=2.5)
seg("4", "Alur app dan tools", "wide", ("slide", "agents", 0),
    "Definisinya dulu: agent sama dengan LLM ditambah prompt ditambah tool. Setiap kartu bergaris oranye di sini adalah satu agent, dan isinya selalu tiga hal itu.")
seg("4", "Alur app dan tools", "wide", ("slide", "agents", 1),
    "Pertanyaan dari layar Streamlit masuk ke supervisor. LLM-nya gpt-4.1-mini, prompt-nya movie-supervisor-system, dan tool-nya tiga: dua tombol oper, satu ke tiap sub-agent, dan forward_message untuk meneruskan jawaban sub-agent apa adanya. Tugasnya memilih sub-agent; ia menjawab sendiri hanya untuk pertanyaan di luar topik film.")
seg("4", "Alur app dan tools", "wide", ("slide", "agents", 2),
    "rag_agent untuk cari dari cerita. search_movies dan similar_movies membaca vektor di Qdrant; search_movies juga memakai reranker yang memilih 5 dari 15 kandidat.")
seg("4", "Alur app dan tools", "wide", ("slide", "agents", 3),
    "data_agent untuk fakta, peringkat, dan orang. get_movie_details dan rank_movies membaca tabel 1.000 film dengan pandas, get_person_info membaca bio di people.csv.")
seg("4", "Alur app dan tools", "wide", ("slide", "agents", 4),
    "Prompt ketiga agent disimpan di Langfuse, bukan di kode, dan setiap run dicatat balik ke sana sebagai trace.")
seg("4", "Alur app dan tools", "wide", ("slide", "alur", 0),
    "Sekarang satu pertanyaan: film tentang pencuri yang masuk ke mimpi orang. Nomor berlatar oranye dikerjakan LLM, nomor bergaris dikerjakan kode.")
seg("4", "Alur app dan tools", "wide", ("slide", "alur", 1), "Satu, Streamlit mengirim pertanyaan beserta seluruh riwayat sesi ke supervisor.")
seg("4", "Alur app dan tools", "wide", ("slide", "alur", 2), "Dua, LLM supervisor memilih rag_agent, lewat tombol oper.")
seg("4", "Alur app dan tools", "wide", ("slide", "alur", 3),
    "Tiga, LLM rag_agent menulis tool call: search_movies, beserta argumennya. LLM tidak menjalankan apa pun; ia hanya menulis permintaan.")
seg("4", "Alur app dan tools", "wide", ("slide", "alur", 4), "Empat, kode yang menjalankannya: Qdrant mengambil 15 kandidat yang maknanya paling dekat.")
seg("4", "Alur app dan tools", "wide", ("slide", "alur", 5), "Lima, reranker memilih 5 terbaik, dan hasilnya kembali ke rag_agent sebagai JSON.")
seg("4", "Alur app dan tools", "wide", ("slide", "alur", 6),
    "Enam, LLM rag_agent menulis jawaban dari JSON itu, dan jawabannya mengalir ke layar bersama tool call dan usage.")
seg("4", "Alur app dan tools", "wide", ("slide", "alur", 7),
    "Tujuh, kendali kembali ke supervisor, dan LLM supervisor menutup giliran. Idealnya ia meneruskan jawaban dengan forward_message, tapi tiga dari empat kali ia menulis ulang. Karena itu layar dikunci di kode pada jawaban sub-agent, apa pun yang ditulis supervisor.")
seg("4", "Alur app dan tools", "wide", ("slide", "alur", 8),
    "Delapan, seluruh run tercatat di Langfuse sebagai satu trace, dan jempol pengguna masuk sebagai skor di trace itu. Jadi LLM hanya memilih dan menulis. Mencari, menyaring, dan menghitung dikerjakan kode. Untuk pertanyaan peringkat atau fakta, jalurnya sama, hanya lewat data_agent dan pandas.")
seg("4", "Alur app dan tools", "two", ("slide", "harga", 0),
    "Kenapa supervisor, bukan swarm? Pertanyaan film hampir selalu jatuh ke satu bidang, jadi cukup satu supervisor yang memilih. Kenapa dua sub-agent, bukan lima? Pembagiannya mengikuti dua jenis sumber: vektor dan tabel. Harganya saya ukur: set uji tetap 17 dari 17, biaya sekitar 10 persen lebih mahal, dan rata-rata 6,9 detik per pertanyaan dibanding 4,3 detik dengan agent tunggal.")

# 5 · Demo app --------------------------------------------------------------------------------------------------------
seg("5", "Demo app", "two", ("slide", "ch05", 0), hold=2.5)
seg("5", "Demo app", "two", ("demo", "beranda"),
    "Ini app publiknya. Dinding poster diacak dari 1.000 film. Di bawah ada contoh pertanyaan, dan di sidebar ada rak tontonan.")
seg("5", "Demo app", "two", ("demo", "q1"),
    "Saya klik contoh pencuri yang masuk ke mimpi. Jawabannya mengalir kata demi kata. Inception muncul sebagai kartu poster.")
seg("5", "Demo app", "two", ("demo", "q1-expander"),
    "Di judul expander terlihat rutenya: supervisor mengoper ke rag_agent. Argumennya search_movies dengan query berbahasa Inggris, karena sinopsis di dataset berbahasa Inggris. Di bawahnya dokumen yang dipakai: 15 kandidat dari Qdrant yang diurutkan ulang reranker, masing-masing dengan skor kemiripan vektor dan skor reranker. Paling bawah: token input dan output serta biayanya dalam rupiah dan dolar.")
seg("5", "Demo app", "two", ("demo", "q2"),
    "Saya sengaja salah ketik: film christoper nolan. Kali ini supervisor mengoper ke data_agent, yang memanggil rank_movies dengan sutradara Nolan.")
seg("5", "Demo app", "two", ("demo", "q2-expander"),
    "Angka di jawaban bisa dicek langsung di panel: 8 film, rata-rata rating 8,46.")
seg("5", "Demo app", "two", ("demo", "q2-more"),
    "Tombol Muat lebih banyak mengambil sisa hasil langsung dari tool, tanpa memanggil LLM. Lalu saya beri jempol untuk jawaban ini; nanti kita lihat di Langfuse.")
seg("5", "Demo app", "two", ("demo", "q3"),
    "Yang mana paling lama? Saya tidak menyebut Nolan lagi. Agent tahu dari riwayat sesi: jawabannya Interstellar, 2014, 169 menit. Riwayat dikirim utuh dari Streamlit setiap giliran, tanpa database tambahan.")
seg("5", "Demo app", "two", ("demo", "panel-film"),
    "Klik poster Interstellar: panel film dengan sinopsis bahasa Indonesia dan fakta menarik. Panel ini tanpa LLM, jadi tanpa biaya token. Sinopsis sudah diterjemahkan sekali secara offline.")
seg("5", "Demo app", "two", ("demo", "panel-orang"),
    "Klik nama Christopher Nolan: panel orang dengan foto, bio dari Wikipedia, dan semua filmnya di Top 1000.")
seg("5", "Demo app", "two", ("demo", "sidebar"),
    "Di sidebar terlihat total pertanyaan, token, dan biaya sesi ini.")

# 5b · Langfuse -------------------------------------------------------------------------------------------------------
seg("5b", "Langfuse", "two", ("slide", "ch05b", 0), hold=2.5)
seg("5b", "Langfuse", "wide", ("shot", "langfuse-01-sessions"),
    "Satu percakapan di app menjadi satu session di Langfuse, dan setiap pertanyaan menjadi satu trace.")
seg("5b", "Langfuse", "wide", ("shot", "langfuse-02-trace-tree"),
    "Saya buka trace film christoper nolan, tab Tree. Urutan kerjanya terlihat lengkap: supervisor mengoper, data_agent memanggil rank_movies dengan argumen ini, hasilnya 8 film, lalu kembali ke supervisor. Di atas ada tag versi prompt, prompt-v8 dan supervisor-v1, latensi, token, dan biaya.")
seg("5b", "Langfuse", "wide", ("shot", "langfuse-03-scores"),
    "Jempol pengguna menempel di trace sebagai score user_feedback. Di halaman Scores semua jempol terkumpul, lengkap dengan tanggal dan trace-nya; filter user_feedback sama dengan nol adalah cara saya mencari jawaban yang perlu diperiksa, lalu membuka trace-nya persis seperti tadi.")
seg("5b", "Langfuse", "wide", ("shot", "langfuse-04-prompt-supervisor"),
    "Tidak ada prompt di kode. Prompt supervisor, movie-supervisor-system versi 1, berisi aturan memilih sub-agent.")
seg("5b", "Langfuse", "wide", ("shot", "langfuse-05-prompt-agent"),
    "Ini prompt kedua sub-agent, movie-agent-system, versi 1 sampai 9, dengan label production di versi 8 dan staging di versi 9. Namanya dari masa agent tunggal, jadi saya pertahankan supaya riwayat versi 1 sampai 8 tidak hilang. Setiap versi lahir dari satu temuan uji.")
seg("5b", "Langfuse", "wide", ("shot", "langfuse-06-trace-v9-miyazaki"),
    "Satu contoh. Saya mencoba versi 9 untuk merapikan prompt, dengan label staging, sehingga app publik tetap memakai versi 8. Set uji turun ke 15 dari 17. Di trace terlihat penyebabnya: untuk ada berapa film Hayao Miyazaki tahun 2000-an, data_agent memakai tool yang salah lalu menghitung sendiri, dan hasilnya 4 film, padahal yang benar 3. Jadi production tetap di versi 8. Mengganti versi di Langfuse cukup memindah label, tanpa deploy ulang. Pertanyaan Miyazaki yang sama pernah gagal dengan cara lain: Miyazaki dicari sebagai aktor, bukan sutradara. Itu saya perbaiki di kode, nanti saya tunjukkan di tools.py.")

# 6 · Kode per fungsi -------------------------------------------------------------------------------------------------
seg("6", "Kode per fungsi", "two", ("slide", "ch06", 0), hold=2.5)
CODE = [
    ("streamlit_app.py", 1, 3, "docstring", "File ini hanya tampilan. Logika agent ada di app/agent.py, sesuai arahan modular."),
    ("streamlit_app.py", 36, 37, "session_state", "chat menyimpan riwayat percakapan, session_id jadi id session di Langfuse."),
    ("streamlit_app.py", 484, 485, "question", "Pertanyaan datang dari kotak ketik, atau dari tombol contoh dan panel."),
    ("streamlit_app.py", 500, 506, "riwayat", "Setiap rerun, seluruh riwayat chat digambar ulang."),
    ("streamlit_app.py", 517, 517, "history", "Yang dikirim ke agent hanya role dan content, seluruh riwayat. Inilah yang membuat agent ingat percakapan."),
    ("streamlit_app.py", 523, 523, "write_stream", "Jawaban dialirkan potong demi potong."),
    ("streamlit_app.py", 525, 525, "trim_offer", "Kalimat penutup berupa tawaran dipotong di kode, karena prompt saja tidak cukup."),
    ("streamlit_app.py", 117, 152, "summarize_run", "Dari pesan baru, fungsi summarize_run mengambil rute supervisor dari tombol transfer_to, setiap tool call beserta argumen dan hasilnya, dan menjumlahkan usage_metadata dari semua panggilan LLM."),
    ("streamlit_app.py", 414, 449, "show_details", "show_details: expander berjudul rute, argumen tool di st.code, dokumen dengan skor vektor dan reranker, usage dalam rupiah dan dolar, lalu tombol jempol yang dikirim ke Langfuse lewat save_feedback."),
    ("streamlit_app.py", 529, 534, "except", "Kalau layanan gagal, pengunjung melihat pesan yang jelas, dan galat lengkapnya masuk log."),
    ("app/agent.py", 1, 3, "docstring", "Agent sama dengan LLM ditambah prompt ditambah tool. Supervisor memilih sub-agent, sub-agent memanggil tool film."),
    ("app/agent.py", 75, 90, "_build_agent", "Di sini tiga agent dibuat. Kedua prompt diambil dari Langfuse dengan nomor versinya. rag_agent dibuat dengan create_agent dan dua tool Qdrant, data_agent dengan tiga tool data. create_supervisor menggabungkan keduanya, dengan forward_message untuk meneruskan jawaban sub-agent. with_config linked prompt menautkan setiap agent ke prompt Langfuse-nya sendiri. lru_cache membuat agent sekali per versi prompt, bukan setiap pertanyaan dan bukan saat file di-import."),
    ("app/agent.py", 93, 97, "get_agent", "Prompt berlabel production diambil setiap pertanyaan, tapi SDK menyimpannya 60 detik. Jadi versi baru di Langfuse terpakai tanpa deploy ulang."),
    ("app/agent.py", 107, 108, "reply_language", "Kalau pertanyaannya berbahasa Inggris, satu baris Reply in English ditambahkan di kode, karena aturan bahasa di prompt sering diabaikan."),
    ("app/agent.py", 109, 116, "CallbackHandler", "Setiap run di-trace ke Langfuse, dikelompokkan per session, dan diberi tag versi prompt."),
    ("app/agent.py", 118, 131, "stream", "subgraphs True memberi tahu asal setiap potongan teks. Yang tampil di layar adalah jawaban sub-agent. Saya ukur di 145 trace: supervisor hanya meneruskan dengan forward_message di 25 persen, sisanya menulis ulang. Jadi layar dijaga di sini: tulisan ulang supervisor tidak ditampilkan dua kali."),
    ("app/agent.py", 134, 134, "run.update", "Setelah selesai, pesan baru dan trace_id dititipkan untuk panel tool call dan feedback."),
    ("app/agent.py", 137, 142, "send_feedback", "Jempol disimpan sebagai score di trace yang sama. score_id-nya tetap, jadi mengganti jempol menimpa, bukan menambah."),
    ("app/tools.py", 24, 27, "Genre", "Genre dikunci ke 21 nilai persis dari dataset, jadi LLM tidak bisa mengarang genre. String kosong diubah jadi tanpa genre, karena sejak supervisor sekitar 8 persen pencarian mengirim genre kosong dan sempat galat."),
    ("app/tools.py", 79, 100, "search_movies", "Decorator tool mengubah fungsi jadi skema yang dibaca LLM: nama, docstring, dan deskripsi tiap argumen. Docstring ini instruksi untuk LLM, jadi ditulis dalam bahasa Inggris."),
    ("app/tools.py", 101, 102, "penjaga bahasa", "Kalau query masih berbahasa Indonesia, tool menolak dan agent mengulang dalam bahasa Inggris."),
    ("app/tools.py", 111, 127, "search_page", "Qdrant mengambil 15 kandidat dengan filter genre dan tahun, reranker memilih 5 terbaik. Kalau reranker gagal, urutan vektor dipakai, jadi pencarian tidak pernah mati."),
    ("app/rerank.py", 13, 28, "rerank", "Satu panggilan ke endpoint rerank OpenRouter, model qwen3-reranker-8b. Kalau gagal, hasilnya None."),
    ("app/tools.py", 283, 286, "query_points", "similar_movies: query-nya id film, jadi Qdrant memakai vektor film itu sendiri. Tidak ada panggilan embedding tambahan."),
    ("app/tools.py", 294, 334, "rank_movies", "Tool data dengan pandas: filter, urutkan, dan kembalikan matching_count serta average_rating. Angka 8 film dan 8,46 di demo tadi datang dari sini."),
    ("app/tools.py", 354, 363, "_fix_role", "Ini perbaikan Miyazaki tadi. Panel tool call memperlihatkan rank_movies dengan star Hayao Miyazaki, 0 film, lalu dijawab tidak ada. Sekarang kalau nama itu di seluruh dataset hanya pernah jadi sutradara, kode mencarinya sebagai sutradara. Diuji 9 kasus dan set uji 17 pertanyaan."),
    ("app/tools.py", 137, 160, "find_title", "Dua tool lain: detail judul dengan pencarian 4 lapis yang tahan typo, dan profil orang dari bio Wikipedia yang diambil offline."),
    ("app/data.py", 23, 47, "load_movies", "Satu-satunya tempat pembersihan data, dibaca sekali lalu disimpan di memori. Tahun Apollo 13 dibetulkan. Id memakai nomor baris karena judul Drishyam ada dua. Metascore memakai Int64, bulat tapi boleh kosong: kalau 157 nilai kosong diisi nol, rata-ratanya turun dari 78 ke 66."),
    ("scripts/ingest.py", 15, 22, "build_documents", "Satu film menjadi satu Document. Yang di-embed hanya judul, genre, dan sinopsis. Semua kolom lain ikut sebagai metadata atau payload."),
    ("scripts/ingest.py", 39, 49, "from_documents", "Satu panggilan untuk membuat collection, meng-embed per 100 teks, dan mengunggah. force_recreate dan id tetap membuat skrip ini aman diulang."),
    ("scripts/ingest.py", 25, 28, "create_payload_indexes", "Index untuk genre dan tahun, supaya filter tidak memindai semua point. Hasilnya saya tunjukkan langsung di Qdrant."),
]
for file, a, b, sym, text in CODE:
    seg("6", "Kode per fungsi", "two", ("code", file, a, b, sym), text)

# 6b · Qdrant ---------------------------------------------------------------------------------------------------------
seg("6b", "Qdrant", "two", ("slide", "ch06b", 0), hold=2.5)
seg("6b", "Qdrant", "wide", ("shot", "qdrant-01-collection"),
    "Ini hasil ingest tadi di Qdrant Cloud: koleksi imdb_movies, 1.000 point, satu per film, vektor 1.536 dimensi, jarak Cosine.")
seg("6b", "Qdrant", "wide", ("shot", "qdrant-02-payload-index"),
    "Dua index payload dari create_payload_indexes: metadata genres dan metadata year, jadi filter genre dan tahun tidak memindai semua point.")
seg("6b", "Qdrant", "wide", ("shot", "qdrant-03-point-inception"),
    "Satu point, Inception, id 8: berisi page_content, yaitu teks yang di-embed: judul, genre, sinopsis, dan metadata lengkap yang dipakai tool dan kartu poster.")
seg("6b", "Qdrant", "wide", ("shot", "qdrant-04-points"),
    "Untuk penilaian, saya menyertakan API key read-only di Google Form, jadi koleksi ini bisa dilihat tanpa bisa diubah.")

# 7 · Outro -----------------------------------------------------------------------------------------------------------
seg("7", "Penutup", "two", ("slide", "ch07", 0), hold=2.5)
seg("7", "Penutup", "two", ("slide", "outro", 0),
    "Ringkasnya: 3 agent, 5 tool, 1.000 film di Qdrant, prompt dan trace di Langfuse, app publik, dan 17 dari 17 pertanyaan uji lolos.")
seg("7", "Penutup", "two", ("slide", "outro", 0),
    "Ada keterbatasan yang saya ketahui. Pertanyaan agregat per kelompok, misalnya genre apa yang rata-rata ratingnya paling tinggi, belum benar, karena rank_movies menghitung satu kelompok per panggilan. Langkah berikutnya adalah text-to-SQL dengan koneksi read-only. Supervisor juga lebih sering menulis ulang daripada meneruskan, seperti di langkah 7 tadi; layar tetap benar karena dijaga di kode. Dan pertanyaan lintas domain baru memanggil satu sub-agent.")
seg("7", "Penutup", "two", ("slide", "end", 0),
    "Link app, repo, README, dan laporan lengkapnya ada di deskripsi. Terima kasih.")

PLAN = {"1": 30, "2": 75, "3": 90, "4": 150, "5": 135, "5b": 90, "6": 200, "6b": 40, "7": 45}  # detik, dari tabel naskah


def speech_text(text: str) -> str:
    """Teks untuk TTS: nama teknis dibuat terucap wajar, tampilan di layar tetap memakai `text` asli."""
    import re
    t = text
    t = re.sub(r"\b(\w+)\.py\b", r"\1 py", t)           # data.py -> data py
    t = t.replace("_", " ")                                # rank_movies -> rank movies
    t = t.replace("gpt-4.1-mini", "gpt 4 point 1 mini")
    t = re.sub(r"\b(\d+)/(\d+)\b", r"\1 dari \2", t)       # 17/17
    t = t.replace("JCAIEH", "jey si ei ai i eits").replace("IMDB", "ai em di bi").replace("LLM", "el el em")
    t = t.replace("RAG", "reg").replace("UI", "yu ai").replace("API", "ei pi ai").replace("JSON", "jeison").replace("SDK", "es di kei")
    t = t.replace("README", "ridmi").replace("EDA", "i di ei").replace("CSV", "si es vi").replace("SQL", "es kyu el")
    t = t.replace("st.code", "s t code").replace("Int64", "int 64")
    return t
