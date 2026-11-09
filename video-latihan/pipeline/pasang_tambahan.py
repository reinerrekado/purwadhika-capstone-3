#!/usr/bin/env python3
"""Pasang file tambahan video latihan (bagian/ dan arsip/) dari hasil unduhan Google Drive.

Dua folder itu sengaja tidak masuk git karena besar. Skrip ini mencari isinya di path yang
diberikan, mengenali folder dari nama dan ukuran file, menyalin ke tempat yang benar di repo,
lalu memastikan git tidak menganggapnya file baru.

Pakai:
    python video-latihan/pipeline/pasang_tambahan.py <path> [<path> ...]
    <path> = folder hasil ekstrak, file .zip dari Drive, atau folder induknya (mis. ~/Downloads).
    Tanpa argumen: mencari di ~/Downloads.
    --coba : hanya menunjukkan apa yang akan dilakukan, tanpa menyalin.

Hanya pustaka standar Python 3.9+. Tidak pernah menghapus: file lama yang isinya berbeda
diberi akhiran .lama-<waktu> sebelum ditimpa.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[2]  # .../video-latihan/pipeline/pasang_tambahan.py -> repo
VL = REPO / "video-latihan"

# Ukuran byte file yang dikirim 9 Nov 2026: dipakai untuk membedakan v1/v2 dan memeriksa salinan.
_SAMA = {"01-intro.mp4": 2558082, "02-tujuan.mp4": 7136303, "03-langkah-membangun.mp4": 11832485,
         "04-alur-app-dan-tools.mp4": 12714201, "05-demo-app.mp4": 14299468}
BAGIAN_V2 = {**_SAMA, "05b-langfuse.mp4": 8163908, "06-kode-per-fungsi.mp4": 32642091,
             "06b-qdrant.mp4": 2674842, "07-penutup.mp4": 4303676}
BAGIAN_V1 = {**_SAMA, "05b-langfuse.mp4": 7341950, "06-kode-per-fungsi.mp4": 32644470,
             "06b-qdrant.mp4": 2452320, "07-penutup.mp4": 4304483}
ARSIP_V1 = {"rakfilm-latihan.mp4": 95272586, "rakfilm-latihan.mp3": 21965427,
            "rakfilm-latihan.srt": 17890, "laporan-durasi.md": 814}

DEST_BAGIAN = VL / "bagian"
DEST_ARSIP = VL / "arsip" / "v1-placeholder"

ZIP_PREFIX = ("bagian", "arsip", "video-latihan-tambahan", "video untuk capstone 3")
SKIP_DIRS = {"__MACOSX", "node_modules", ".git", "pylib", "seg"}
MAX_DEPTH = 6


def iter_dirs(root: Path):
    """Semua folder di bawah root (termasuk root), kedalaman terbatas, folder tersembunyi dilewati."""
    root = root.resolve()
    for cur, dirs, _files in os.walk(root):
        depth = len(Path(cur).relative_to(root).parts)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")] if depth < MAX_DEPTH else []
        yield Path(cur)


def extract_zips(root: Path, tmp: Path) -> list[Path]:
    """Ekstrak zip Drive (nama diawali bagian/arsip/...) di root atau satu tingkat di bawahnya."""
    out = []
    cands = [root] if root.suffix.lower() == ".zip" else [*root.glob("*.zip"), *root.glob("*/*.zip")]
    for z in cands:
        if not z.name.lower().startswith(ZIP_PREFIX):
            continue
        target = tmp / z.stem
        print(f"  ekstrak {z.name} ...")
        with zipfile.ZipFile(z) as zf:
            zf.extractall(target)
        out.append(target)
    return out


def size(p: Path) -> int:
    try:
        return p.stat().st_size
    except OSError:
        return -1


def score(d: Path, table: dict[str, int]) -> int:
    return sum(1 for n, s in table.items() if size(d / n) == s)


def classify(d: Path):
    """Kembalikan daftar (label, {nama_file: sumber}, folder_tujuan, tabel_ukuran) untuk folder d."""
    names = {p.name for p in d.iterdir() if p.is_file()}
    found = []
    if names >= BAGIAN_V2.keys():
        v2, v1 = score(d, BAGIAN_V2), score(d, BAGIAN_V1)
        if v2 == 0 and v1 == 0:  # ukuran tidak dikenal: tebak dari induknya
            is_v1 = (d.parent / "rakfilm-latihan.mp4").exists()
            print(f"  peringatan: ukuran file di {d} tidak sama dengan kiriman 9 Nov; dianggap {'v1' if is_v1 else 'v2'}")
        else:
            is_v1 = v1 > v2
        table = BAGIAN_V1 if is_v1 else BAGIAN_V2
        dest = DEST_ARSIP / "bagian" if is_v1 else DEST_BAGIAN
        found.append((f"{'arsip/v1-placeholder/bagian' if is_v1 else 'bagian'} ({'v1' if is_v1 else 'video v2'})",
                      {n: d / n for n in table}, dest, table))
    if {"rakfilm-latihan.mp4", "laporan-durasi.md"} <= names and (d / "bagian").is_dir():
        found.append(("arsip/v1-placeholder (file utuh v1)", {n: d / n for n in ARSIP_V1 if n in names}, DEST_ARSIP, ARSIP_V1))
    return found


def copy_files(files: dict[str, Path], dest: Path, coba: bool) -> tuple[int, int]:
    """Salin file ke dest. Kembalikan (disalin, sama). File lama yang berbeda diarsipkan dulu."""
    copied = same = 0
    if not coba:
        dest.mkdir(parents=True, exist_ok=True)
    for name, src in files.items():
        tgt = dest / name
        if tgt.exists() and size(tgt) == size(src):
            same += 1
            continue
        if tgt.exists() and not coba:
            backup = tgt.with_name(f"{tgt.name}.lama-{time.strftime('%Y%m%d-%H%M%S')}")
            tgt.rename(backup)
            print(f"  file lama berbeda, disimpan sebagai {backup.name}")
        if not coba:
            shutil.copy2(src, tgt)
        copied += 1
    return copied, same


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def main(argv: list[str]) -> int:
    coba = "--coba" in argv
    args = [a for a in argv if a != "--coba"]
    roots = [Path(a).expanduser() for a in args] or [Path.home() / "Downloads"]
    print("Pasang tambahan video latihan" + (" (uji coba, tidak menyalin)" if coba else ""))
    print(f"  repo   : {REPO}")
    for r in roots:
        print(f"  sumber : {r}")
        if not r.exists():
            print("  TIDAK ADA. Periksa path-nya."); return 2

    tmp = Path(tempfile.mkdtemp(prefix="drive-tambahan-"))
    scan: list[Path] = []
    for r in roots:
        if r.is_dir():
            scan.append(r)
        scan += extract_zips(r, tmp)

    jobs, seen, env_src, stray = [], set(), None, []
    for root in scan:
        for d in iter_dirs(root):
            for label, files, dest, table in classify(d):
                key = (label, dest)
                if key not in seen:
                    seen.add(key); jobs.append((label, files, dest, table))
            if (d / ".env").is_file() and env_src is None:
                env_src = d / ".env"
            for p in d.glob("rakfilm-latihan*.mp4"):
                if not (d / "laporan-durasi.md").exists():
                    stray.append(p)
    if not jobs:
        print("\nTidak menemukan folder bagian/ atau arsip/ di path itu.")
        print("Tempel path folder hasil ekstrak (yang berisi 01-intro.mp4 dst.), atau file .zip dari Drive.")
        shutil.rmtree(tmp, ignore_errors=True); return 2

    print()
    ok = total = 0
    for label, files, dest, table in jobs:
        copied, same = copy_files(files, dest, coba)
        rel = dest.relative_to(REPO).as_posix()
        print(f"  {label:38s} {len(files):2d} file -> {rel:40s} disalin {copied}, sudah sama {same}")
        if not coba:
            for n, s in table.items():
                if n in files:
                    total += 1
                    ok += size(dest / n) == s
    if env_src:
        if (REPO / ".env").exists():
            print(f"  {'.env':38s} dilewati: repo sudah punya .env")
        elif not coba:
            shutil.copy2(env_src, REPO / ".env"); print(f"  {'.env':38s} disalin ke akar repo (isinya tidak ditampilkan)")
    for p in stray:
        print(f"  {p.name:38s} dilewati: video utuh v2 sudah ada di repo (video-latihan/rakfilm-latihan.mp4)")

    if not coba:
        print(f"\nPemeriksaan ukuran: {ok}/{total} file cocok dengan kiriman 9 Nov." + ("" if ok == total else " Periksa yang berbeda."))
        ign = [p for p in ("video-latihan/bagian", "video-latihan/arsip") if git("check-ignore", "-q", p).returncode == 0]
        st = git("status", "--short").stdout.strip()
        baru = [l for l in st.splitlines() if "video-latihan/bagian" in l or "video-latihan/arsip" in l]
        print(f"git: {' dan '.join(ign) or 'TIDAK ADA YANG'} ter-ignore; " + ("tidak ada file baru dari skrip ini." if not baru else "PERHATIAN, muncul di status:\n  " + "\n  ".join(baru)))
    shutil.rmtree(tmp, ignore_errors=True)
    print("Selesai.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
