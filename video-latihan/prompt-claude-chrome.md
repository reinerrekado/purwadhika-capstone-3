# Prompt Claude in Chrome: screenshot Langfuse dan Qdrant untuk video latihan

Cara pakai: Chrome dimaksimalkan (1920×1080), tema gelap di kedua layanan, zoom Chrome 110%. Claude berhenti di tiap tampilan dan menulis "SIAP: <nama file>". Saat itu tekan **Win+Shift+S** → mode "Jendela" → klik jendela Chrome. Gambar tersimpan otomatis di `Gambar\Screenshots`. Setelah selesai, pindahkan ke folder ini (`video-latihan\screenshot\`) dengan nama file sesuai daftar.

Nama file yang dipakai video: `langfuse-01-sessions.png`, `langfuse-02-trace-tree.png`, `langfuse-03-scores.png`, `langfuse-04-prompt-supervisor.png`, `langfuse-05-prompt-agent.png`, (opsional) `langfuse-06-trace-v9-miyazaki.png`, `qdrant-01-collection.png`, `qdrant-02-payload-index.png`, `qdrant-03-point-inception.png`.

## Prompt 1 · tab Langfuse (cloud.langfuse.com, project "My Project")

```
Bantu saya menyiapkan 5 tampilan Langfuse untuk screenshot. Saya sudah login. Pakai tema gelap (Settings → Theme → Dark) dan jangan mengubah data apa pun (jangan klik tombol hapus, label, atau edit). Di setiap tampilan, berhenti, tulis "SIAP: <nama file>", lalu tunggu saya bilang "lanjut".

1. Tracing → Sessions. Buka session paling atas yang berisi 3 trace: "Film tentang pencuri yang masuk ke mimpi orang", "film christoper nolan", "yang mana paling lama?" (kalau tidak ada, pakai session "eval-edac5c"). Pastikan daftar trace di dalam session terlihat. SIAP: langfuse-01-sessions.png

2. Buka trace yang input-nya "film christoper nolan". Pilih tab Tree (bukan Graph). Perlebar pohon supaya terlihat urutan: supervisor → transfer_to_data_agent → data_agent → rank_movies → supervisor. Klik node rank_movies supaya panel kanan menampilkan Input (director Christopher Nolan) dan Output (matching_count 8, average_rating 8.46). Pastikan tag prompt-v8 dan supervisor-v1, latensi, token, dan biaya di header terlihat. SIAP: langfuse-02-trace-tree.png

3. Di trace yang sama, tampilkan bagian Scores (user_feedback = 1). Kalau tidak ada score di trace ini, buka menu Scores di sidebar kiri dan filter nama score = user_feedback. SIAP: langfuse-03-scores.png

4. Prompts → buka "movie-supervisor-system" versi 1. Scroll supaya aturan memilih sub-agent (routing) terbaca dan label production terlihat. SIAP: langfuse-04-prompt-supervisor.png

5. Prompts → buka "movie-agent-system". Tampilkan daftar versi v1 sampai v9 dengan label production di v8 dan staging di v9 (kalau perlu, buka tab versi). SIAP: langfuse-05-prompt-agent.png

6. (Opsional) Tracing → Traces → filter tag prompt-v9 → buka trace dengan input "ada berapa film Hayao Miyazaki tahun 2000-an?", tab Tree. SIAP: langfuse-06-trace-v9-miyazaki.png. Kalau tidak ketemu dalam 1 menit, lewati dan beri tahu saya.
```

## Prompt 2 · tab Qdrant (cloud.qdrant.io)

```
Bantu saya menyiapkan 3 tampilan dashboard Qdrant untuk screenshot. Saya sudah login ke Qdrant Cloud. Jangan mengubah apa pun: tidak membuat, menghapus, atau mengedit collection, point, atau API key. Di setiap tampilan, berhenti, tulis "SIAP: <nama file>", lalu tunggu saya bilang "lanjut".

1. Clusters → buka cluster yang host-nya diawali "65aa8fb2" (eu-west-2). Masuk ke dashboard/Cluster UI-nya (tombol "Open Dashboard" atau "Cluster UI"). Aktifkan tema gelap kalau ada tombolnya. Buka Collections → imdb_movies → tab Info. Pastikan terlihat: points count 1000, vectors size 1536, distance Cosine. SIAP: qdrant-01-collection.png

2. Masih di imdb_movies, tampilkan payload schema / payload indexes: metadata.genres (keyword) dan metadata.year (integer). Biasanya ada di tab Info bagian payload_schema; kalau tidak, scroll ke bawah. SIAP: qdrant-02-payload-index.png

3. Buka menu Console dan jalankan:
GET collections/imdb_movies/points/8
Pastikan hasilnya terlihat: page_content berisi "Inception" dan metadata (title, year, genres, rating, director, stars, poster). Kalau Console tidak ada, buka tab Points dan cari point dengan id 8. SIAP: qdrant-03-point-inception.png
```
