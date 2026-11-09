---
name: streamlit-cloud-reboot
description: "After a code-only push, the Streamlit Cloud app kept running old app/agent.py until Reiner pressed Reboot app; verify on Cloud via Langfuse"
metadata:
  node_type: memory
  type: project
  originSessionId: 890bbd1c-903a-4344-bdf0-b0c49a01e244
  modified: 2026-11-07T08:31:22.970Z
---

Observed 2026-11-07: after pushing code-only changes (no requirements.txt change), the public app imdb-movie-assistant.streamlit.app still ran the old `app/agent.py` 5 and 10 minutes later (checked via Langfuse prompt links on a fresh trace). After Reiner pressed **Reboot app** in share.streamlit.io, the new code was live. Pushes that changed requirements.txt (e.g. the supervisor deploy) went live on their own.

**Why:** "pushed" does not mean "live" on Cloud; imported modules seem to stay in memory until a rebuild/reboot.
**How to apply:** after any push that changes app code, verify on the Cloud app (ask one question, check the Langfuse trace for the new behavior). If it is still old, ask Reiner to Reboot app; Claude cannot do it (no access to his Streamlit account). See [[capstone-m3-requirements]].
