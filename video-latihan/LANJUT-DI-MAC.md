# Lanjut mengerjakan Capstone 3 di MacBook

Ditulis 9 Nov dini hari, untuk pindah dari laptop Windows ke Mac; diperbarui 9 Nov siang setelah `video-latihan/` dimasukkan ke git (clone pertama di Mac tidak membawanya). Deadline tetap **10 Nov 23:59 WIB**.

## Yang ikut ke Mac lewat mana

| Barang | Di mana | Cara ke Mac |
|---|---|---|
| Kode, notes, README | GitHub (publik) | `git clone` |
| `.env` (kunci OpenRouter, Qdrant, Langfuse) | hanya di folder lokal (tidak di git, dan memang jangan) | folder proyek ini ada di **OneDrive**, jadi `.env` ikut tersinkron kalau OneDrive dipasang di Mac. Kalau tidak: AirDrop file-nya dari HP/laptop, atau ketik ulang dari `.env.example` + dashboard tiap layanan. Jangan kirim lewat chat/email |
| `video-latihan/` (video utuh + MP3 + SRT, naskah, rangka, screenshot, prompt, pipeline, memori Claude) | **ikut git sejak 9 Nov** (±150 MB) | langsung ada setelah `git clone`/`git pull`. Yang sengaja tidak ikut: `arsip/` (v1) dan `bagian/` (potongan per bagian) ada di **Google Drive › Video Untuk Capstone 3 › video-latihan-tambahan** (di samping `.env`), unduh lalu taruh di `video-latihan/`; `pipeline/pylib/` (paket Python Windows) dan `pipeline/video/seg/` (klip antara) tidak berguna di Mac, dibuat ulang oleh `pip install` + `assemble.py` (langkah 5). Posisi tiap bagian di video utuh ada di `laporan-durasi.md` |
| Memori Claude Code (aturan kerja, syarat capstone, link artefak) | per komputer di `~/.claude/projects/<slug>/memory/` | salinannya ada di `video-latihan/claude-memory/` (lihat langkah 4) |
| Percakapan Claude Code di Windows | tidak bisa dibuka di Mac | konteksnya sudah ada di `notes/progress.md`, `notes/keputusan-desain.md`, `notes/penjelasan-kode.md`, dan `video-latihan/CARA-PAKAI.md` |

Saran: **jangan menjalankan git di dalam folder OneDrive di dua komputer**; OneDrive bisa merusak folder `.git` kalau dua mesin menyentuhnya. Di Mac, clone ke folder biasa (mis. `~/Code/capstone3`), dan pakai OneDrive hanya untuk mengambil `.env` dan `video-latihan/`. Nanti kalau kembali ke Windows: `git pull`.

## Langkah di Mac

### 1. Repo dan Python
```bash
git clone https://github.com/reinerrekado/purwadhika-capstone-3.git ~/Code/capstone3
cd ~/Code/capstone3
conda create -n capstone3 python=3.12 -y && conda activate capstone3   # atau: python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
Salin `.env` dari OneDrive: `cp "~/Library/CloudStorage/OneDrive-Personal/Documents/Work Repository/Capstone Project Purwadhika/.env" .` (sesuaikan nama folder OneDrive di Mac). Lalu cek koneksi: `python -m scripts.check_connections`. Set uji (opsional, ±Rp700): `python -m scripts.eval`.

### 2. Folder video latihan
Sudah ikut hasil clone. Tonton `video-latihan/rakfilm-latihan.mp4`; kalau mau melompat per bagian, pakai kolom posisi di `laporan-durasi.md`. Potongan `bagian/` dan arsip v1 diunduh dari Google Drive › Video Untuk Capstone 3 › video-latihan-tambahan (ada `BACA.md` di dalamnya). Setelah diekstrak, **tempel path foldernya ke Claude Code** (atau jalankan sendiri):
```bash
python video-latihan/pipeline/pasang_tambahan.py ~/Downloads/video-latihan-tambahan   # path sesuai tempat ekstrak
```
Skrip menaruh keduanya di `video-latihan/` dan memastikan `git status` tetap bersih.

### 3. Claude Code
Instal Claude Code di Mac (aplikasi desktop atau `npm install -g @anthropic-ai/claude-code`), masuk dengan akun yang sama, buka folder `~/Code/capstone3`.

### 4. Memori Claude
Memori tidak ikut akun. Dua cara, pilih yang gampang:
- **Cara cepat:** di pesan pertama tulis: *"Baca semua file di video-latihan/claude-memory/ dan simpan sebagai memorimu untuk proyek ini."*
- **Cara manual:** salin isi `video-latihan/claude-memory/` ke `~/.claude/projects/<slug>/memory/`, dengan `<slug>` = path proyek yang tiap `/` diganti `-` (contoh: `/Users/reine/Code/capstone3` → `-Users-reine-Code-capstone3`). Folder itu dibuat saat sesi pertama dibuka.

Pesan pembuka yang disarankan (catatan serah terima lengkap ada di repo, `notes/serah-terima.md`):
```
Lanjut Capstone 3 Rakfilm di Mac. Baca notes/serah-terima.md dulu dan ikuti bagian 6-nya,
lalu laporkan ringkas pemahamanmu dan tanyakan tugas hari ini. Deadline 10 Nov 23:59.
```

### 5. Pipeline video di Mac
Skrip sudah memilih browser dan font menurut OS (Windows: Edge + Segoe UI; Mac: Chromium + Arial). Yang perlu diinstal sekali:
```bash
pip install playwright edge-tts imageio-ffmpeg
playwright install chromium
cd video-latihan/pipeline/video
python assemble.py          # rakit ulang (±6 menit); juga membuat ulang seg/ dan bagian/
```
Hasil render (`slides/`, `code/`, `demo/`, `audio/`, `shots-real/`) sudah ikut git, jadi `assemble.py` bisa langsung jalan tanpa Playwright atau TTS. Playwright dan edge-tts baru perlu kalau slide, demo, atau naskah berubah.
Screenshot asli Langfuse/Qdrant: taruh di `video-latihan/pipeline/video/shots-real/` dengan nama sesuai `prompt-claude-chrome.md`, lalu `python assemble.py`.

### 6. Merekam di Mac
- Layar: QuickTime Player (Cmd+Shift+5) atau OBS. Wajah: QuickTime → New Movie Recording, atau OBS sekaligus.
- Rangka PNG: `video-latihan/rangka/`. Susun tiga lapis (layar, wajah, rangka) di **CapCut** atau **DaVinci Resolve** (gratis). iMovie hanya dua lapis.
- Ukuran jendela 1144×952 untuk bagian dua panel: pakai DevTools → device toolbar → ukuran kustom, atau aplikasi pengatur jendela (Rectangle, gratis).
- Chrome di Mac untuk Claude in Chrome dan screenshot Langfuse/Qdrant: sama seperti di Windows (Cmd+Shift+4 untuk screenshot area).

## Pengingat deadline
- Google Form (repo, video, app, URL Qdrant + key read-only) sebelum **10 Nov 23:59**.
- Naikkan batas key OpenRouter sebelum merekam (sisa ±$1,6 per 9 Nov).
- Bangunkan app Streamlit sebelum merekam dan sebelum mengumpulkan.
