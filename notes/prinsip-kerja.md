# Prinsip kerja Reiner

Ditulis dari cara kerja yang terbukti di capstone ini (73+ keputusan, 17 uji otomatis, app publik). Bisa disalin ke repo lain: salin file ini ke `notes/` lalu pasang potongan `CLAUDE.md` di bagian paling bawah.

## 1. Prinsip

> **Simple. Structural. Logical. Efficient & effective.** Di atas keempatnya: **impressive.**

| Prinsip | Artinya dalam praktik | Contoh dari capstone |
|---|---|---|
| **Simple** | Pilih opsi paling ringan yang berhasil. Kalau tidak bisa dijelaskan dalam satu kalimat, terlalu rumit. | Riwayat penuh dikirim ke agent, bukan checkpointer. Satu film = satu vektor, tanpa chunking. |
| **Structural** | Batas file dan fungsi jelas. UI hanya UI, logika di modul sendiri, satu sumber untuk tiap data. | `streamlit_app.py` hanya tampilan; `data.py` satu-satunya tempat membersihkan data. |
| **Logical** | Setiap keputusan punya alasan yang bisa dikatakan keras-keras. Alasan dicatat, bukan diingat. | Setiap penyimpangan masuk `keputusan-desain.md` dengan nomor K. |
| **Efficient & effective** | Hemat uang, token, dan waktu; ukur sebelum memutuskan. | Biaya terjemahan dihitung dulu (batas Rp15 ribu); uji 20 item sebelum menjalankan 1.000. |
| **Impressive** | Usaha ekstra ditaruh di tempat yang **terlihat**, bukan di infrastruktur tambahan. | Kartu poster, skor reranker yang tampak di layar, panel orang, README dengan diagram dan screenshot. |

Aturan tambahan yang selalu berlaku:

- **Harus bisa dijelaskan.** Reiner harus mampu menjelaskan setiap langkah dan kode penting. Kode yang tidak bisa dijelaskan adalah beban, seberapa pun bagusnya.
- **Diskusi dulu kalau diminta.** Saat Reiner bilang "diskusi dulu", jelaskan pilihan dan kekurangannya, beri rekomendasi, lalu tunggu. Jangan bertindak.
- **Ikuti bahasa visual yang sudah ada.** Jangan "memperbaiki" jauh dari desain yang sudah dipilih. Hindari tampilan generik buatan AI.

## 2. Metode kerja (urutannya)

1. **Pahami syarat dulu.** Tulis syarat wajib, batas waktu, dan hal yang tidak boleh diganti. Cek setiap pilihan terhadap daftar itu.
2. **Irisan tipis dari ujung ke ujung.** Versi paling sederhana yang berjalan dan sudah ter-deploy dibuat lebih dulu, baru dilengkapi. Masalah integrasi ketahuan di minggu pertama.
3. **Verifikasi dengan data nyata.** Jangan percaya jawaban yang terdengar meyakinkan. Cek ke sumber, uji beberapa kali, simpan angkanya.
4. **Tegakkan di kode, bukan di prompt.** Kalau model sering mengabaikan sebuah aturan, jangan menambah kalimat di prompt. Pindahkan aturan itu ke kode atau skema, lalu uji. (Contoh: bahasa jawaban, query berbahasa Inggris, memotong tawaran penutup.)
5. **Satu perubahan, satu bukti.** Setiap perbaikan diuji, dan hasilnya (angka, bukan perasaan) ditulis. Uji otomatis dijalankan ulang setelah perubahan yang berisiko.
6. **Audit berkala.** Setelah fitur selesai, periksa celah yang belum terpikir: kegagalan layanan, batas biaya, kebocoran rahasia, klaim di dokumen yang sudah usang.
7. **Akui kesalahan sendiri.** Kalau klaim ternyata salah, koreksi di catatan dengan alasannya. Jangan diam-diam diperbaiki.

## 3. Tiga catatan wajib (diperbarui di perubahan yang sama)

Folder `notes/` berisi:

| File | Isi | Kapan diperbarui |
|---|---|---|
| `progress.md` | Daftar centang bertahap. Centang dengan tanggal. Ada bagian "pengingat" untuk hari penting. | Setiap langkah selesai |
| `keputusan-desain.md` | Entri bernomor **K01, K02, …**: pilihan, alasan, status (✅ baru, 🔁 revisi, 💬 menunggu konfirmasi). | Setiap kali berbeda dari arahan atau contoh |
| `penjelasan-kode.md` | Per file: tugas, fungsi dan baris penting, pertanyaan yang mungkin muncul beserta jawaban dengan angka nyata, dan satu kalimat "🎬 Untuk video". | Setiap file atau langkah selesai |

Bedakan dua jenis penyimpangan di `keputusan-desain.md`: **melawan arahan** (perlu alasan kuat dan konfirmasi) dan **beda dari contoh** (wajar, cukup dijelaskan).

## 4. Keamanan dan uang

- Jangan pernah mencetak atau menempel nilai key. Cek nilai env lewat panjangnya saja.
- Key hanya di `.env` (di-ignore git) dan di rahasia platform deploy. `.env.example` hanya berisi nama variabel.
- Sebelum repo dibuka ke publik: audit seluruh riwayat git dengan nilai key asli.
- Pasang batas pemakaian (per sesi dan per jam) dan batas biaya di key sebelum app dibuka ke publik.
- Hal yang sulit dibalik (menghapus, force-push, mengubah akses, mengirim ke layanan luar) **ditanyakan dulu**. Tidak ada yang dihapus tanpa kata "hapus" dari Reiner.
- Setiap push ke `main` me-redeploy app publik: perubahan berisiko diuji dulu secara lokal.

## 5. Cara memakai di repo lain (contoh: SEO kit)

1. Salin file ini ke `notes/prinsip-kerja.md`.
2. Buat tiga catatan kosong: `notes/progress.md`, `notes/keputusan-desain.md`, `notes/penjelasan-kode.md`.
3. Tempel potongan di bawah ini ke `CLAUDE.md` repo itu.
4. Mulai dari irisan tipis yang berjalan, bukan dari fitur terlengkap.
5. Sesuaikan hanya contoh dan syarat wajibnya. Prinsipnya tetap.

### Potongan untuk `CLAUDE.md`

```markdown
## Cara kerja (baca `notes/prinsip-kerja.md`)
- Prinsip: simple, structural, logical, efficient & effective; di atasnya impressive (usaha ekstra di hal yang terlihat).
- Reiner harus bisa menjelaskan setiap langkah. Jelaskan setiap file dan fungsi yang dibuat, tanpa menggurui.
- Setiap perubahan selesai: centang `notes/progress.md`, tambah entri K di `notes/keputusan-desain.md` kalau berbeda dari arahan atau contoh, dan perluas `notes/penjelasan-kode.md`, semuanya di commit yang sama.
- Aturan yang sering dilanggar model: tegakkan di kode, bukan di prompt.
- Verifikasi dengan data nyata dan simpan angkanya. Koreksi klaim sendiri yang salah di catatan.
- "Diskusi dulu" berarti jelaskan pilihan, beri rekomendasi, dan tunggu. Jangan bertindak.
- Jangan cetak nilai key. Tanyakan dulu sebelum menghapus, force-push, atau mengubah akses.
```
