---
name: capstone-docs-workflow
description: "After every capstone step, update notes/progress.md (checklist) and notes/penjelasan-kode.md (explanation + Q&A + video lines)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1e691203-d152-4b0d-9da4-66caa0747fb4
  modified: 2026-10-23T04:56:49.443Z
---

Reiner tracks progress with a checklist file and wants explanations saved for later (2026-10-23). In the capstone repo `notes/`:
- `progress.md` — phased checklist matching the artifact schedule; tick items with the date when done.
- `penjelasan-kode.md` — per file: tugas, fungsi & baris penting, likely questions with answers (with real numbers from tests), and a "🎬 Untuk video" sentence.
- `keputusan-desain.md` — K-numbered decisions (see [[deviation-log-rule]]).

**Why:** they must explain every step in the video and easily forget details (e.g. why Int64); a checklist is how they normally track work.
**How to apply:** in the same change that finishes a file/step, tick progress.md and add/extend that file's section in penjelasan-kode.md; when the user asks "kenapa X?", add the Q&A there too. Related: [[user-capstone-learning-style]].
