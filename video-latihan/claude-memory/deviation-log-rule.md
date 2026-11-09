---
name: deviation-log-rule
description: "Every capstone choice that differs from Pak Herman's guidance or class example code must be logged with its reason in notes/keputusan-desain.md"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1e691203-d152-4b0d-9da4-66caa0747fb4
  modified: 2026-10-22T16:37:17.426Z
---

Any approach that differs from the tutor's guidance (arahan) or from class example code (slides/notebooks/main.py) is allowed if it serves the build principles, but it **must** be recorded in the repo's `notes/keputusan-desain.md` (K-numbered entry: kelas vs kita, alasan, status ✅/🔁/💬). Distinguish "melawan arahan" (needs strong reason + tutor confirmation) from "beda dari contoh kelas" (normal, just explain). Reiner said this applies to every decision (2026-10-22).

**Why:** they must defend every choice in the video/assessment; undocumented deviations look like mistakes.
**How to apply:** whenever code or design departs from a class pattern, add/update a K-entry in the same change. Related: [[capstone-build-principles]], [[capstone-m3-requirements]].
