---
name: capstone-build-principles
description: "Reiner's 4 build rules for the capstone (simple, structural, logical, efficient) plus \"make it impressive\" on top"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1e691203-d152-4b0d-9da4-66caa0747fb4
  modified: 2026-10-22T16:07:00.233Z
---

For the capstone, Reiner set four rules (2026-10-22): **keep it simple, keep it structural, keep it logical, keep it efficient & effective** — and above those, **make it impressive**.

**Why:** they must explain every line in a 7–15 min video and grading rewards extras/UI; complexity they can't explain is a liability.
**How to apply:** pick the lightest option that works (e.g. full-history messages instead of a checkpointer, prompts via Langfuse UI, ChatOpenAI+base_url for OpenRouter); clear file/function boundaries; spend "impressive" effort where it shows (poster cards, filtered search, visible tool calls/usage, Langfuse session traces, clean README diagram), not on extra infrastructure. See [[capstone-m3-requirements]].
