---
name: video-latihan-pipeline
description: Rehearsal video + naskah + frame PNGs + re-runnable pipeline live in video-latihan/, committed to the public repo since 2026-11-09 (except arsip/, bagian/, pylib/, seg/); Reiner moves to a MacBook from 2026-11-10
metadata:
  node_type: memory
  type: project
  originSessionId: 890bbd1c-903a-4344-bdf0-b0c49a01e244
  modified: 2026-11-09T03:08:52.980Z
---

On 2026-11-09 I built a rehearsal video for Reiner's Capstone 3 presentation: `video-latihan/rakfilm-latihan.mp4` (v2, 18:17, Edge TTS id-ID-Ardi narration, slide renders, real public-app demo recording, Monaco "VS Code" code frames, 10 real Langfuse/Qdrant screenshots), plus MP3, SRT and `laporan-durasi.md` (per-section durations and start positions). The naskah (`naskah-video.md`) and frame PNGs (`rangka/`) also live there.

**History of where it lives:** early 9 Nov Reiner asked to keep the video notes off GitHub, so `video-latihan/` was gitignored. Later that day his `git clone` on the Mac did not bring it (expected: ignored files never clone, and OneDrive was not set up there), and he decided "push saja": the folder is now committed to the **public** repo (incl. naskah, screenshots, `claude-memory/`), except `arsip/` (v1, 203 MB), `bagian/` (per-section MP4s, 92 MB duplicate), `pipeline/pylib/` (Windows Python packages incl. a 105 MB ffmpeg.exe — over GitHub's 100 MB limit) and `pipeline/video/seg/` (intermediate clips), which stay gitignored and exist only on the Windows laptop/OneDrive.

**Why:** Reiner wanted to practice by watching a narrated version before recording himself, and from 10 Nov works on a MacBook (guide `video-latihan/LANJUT-DI-MAC.md`, memory copy `video-latihan/claude-memory/`, handoff `notes/serah-terima.md`). He wants earlier versions kept as archives when overwriting (v1 is in `arsip/v1-placeholder/`). Screenshots came via Google Drive folders (download with `curl -L "https://drive.google.com/uc?export=download&id=<fileId>"` after listing with the Drive MCP).

**How to apply:** Pipeline is `video-latihan/pipeline/video/` (scripts pick browser/fonts by OS). Rendered inputs (`slides/`, `code/`, `demo/`, `audio/`, `shots-real/`) are committed, so `python assemble.py` runs on a fresh clone after `pip install playwright edge-tts imageio-ffmpeg` and rebuilds `seg/` + `bagian/` + the full MP4. Script text changes: edit `segments.py`, delete affected `audio/<id>.mp3`, run `make_tts.py`, then `assemble.py`. Key finding: the full naskah reads at 18:17 (plan 14:15) — section 6 code +2:10, section 3 +0:49, section 4 +0:39, 5b +0:28 — so it must be cut by ~4 minutes; cuts were proposed, not yet applied. Known gaps: demo's 👍 click not captured; code frames are Monaco renders, not real VS Code. Before any future push of this folder, check sizes (`du -sh`) and grep for keys. See [[capstone-m3-requirements]], [[capstone-docs-workflow]].
