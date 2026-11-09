---
name: explain-agent-terms
description: "When explaining agent architecture to Reiner, start from the definition and use one consistent term (\"sub-agent\"), no synonyms"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 890bbd1c-903a-4344-bdf0-b0c49a01e244
  modified: 2026-11-06T19:27:47.829Z
---

Explain multi-agent concepts from the ground up: first "agent = LLM + prompt + tool", then count the agents and give each one role. Use exactly one term per thing: "supervisor" and "sub-agent" (rag_agent, data_agent). Do not switch to synonyms like "spesialis" or "worker".

**Why:** on 2026-11-07, an explanation that called the sub-agents "spesialis", with a hospital analogy, left Reiner more confused ("jadi agen itu siapa"). The definition plus a 3-row table of agents made it click right away.

**How to apply:** in chat, docs (penjelasan-kode.md, README) and code comments, keep "supervisor" and "sub-agent". Lead with the definition, not an analogy. See [[user-capstone-learning-style]].
