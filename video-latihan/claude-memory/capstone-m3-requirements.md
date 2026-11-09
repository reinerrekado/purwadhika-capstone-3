---
name: capstone-m3-requirements
description: "Purwadhika JCAIEH Module 3 capstone (Capstone 3) rules, locked stack, deadline, and video/README grading points"
metadata:
  node_type: memory
  type: project
  originSessionId: 1e691203-d152-4b0d-9da4-66caa0747fb4
  modified: 2026-11-06T19:36:00.643Z
---

Capstone 3, Purwadhika JCAIEH (tutor Pak Herman Sugiharto). Individual. Case: **IMDB Top 1000 movies** (chosen 2026-10-21; the HR/Resume option is dropped — do not mention it in deliverables).

- Deadline: **2026-11-10 23:59** (00:01 on 11 Nov counts as late; late = point deduction). Submission via Google Form from operations.
- Locked stack (cannot change): **Qdrant Cloud** (vector DB; may need to hand the tutor an API key + URL), **Streamlit** (single app, direct call to the agent, no FastAPI/Docker for now; deploy to Streamlit Cloud), **Langfuse** (all prompts stored there, none hardcoded; the agent is traced in Langfuse; use the new `get_client` API, not the old one).
- Free choice: LLM/embedding provider (OpenRouter recommended so embeddings + reranker are in one place), agent framework (LangChain `create_agent` — create_react_agent is deprecated; **supervisor architecture MANDATORY** — Reiner confirmed 2026-11-07, overriding the earlier "optional"; built on branch `supervisor` as 1 supervisor + rag_agent + data_agent, see notes K75; LangChain may be swapped e.g. Pydantic AI), extra DBs (SQLite/Postgres ok). Reranker optional.
- Required pieces: ingestion code (chunking if needed, embed, upsert to Qdrant; .py or .ipynb ok), RAG retrieval tool, extra non-RAG tools (stats, ranking, lookup), agent, prompts in Langfuse, Streamlit UI showing chat history, tool calls, and usage details.
- Code must be modular: agent.py separate from the Streamlit file; no `if __name__ == "__main__"` side effects in imported modules.
- README: flow diagram (tldraw/any), install, env vars, how to run (`streamlit run ...`), example queries.
- Video 7–15 min, face visible, code readable: intro, goal (pitch as if to C-level), workflow/build steps, app flow + tools, live demo, code walkthrough per function in order (Streamlit → agent → tools → DB), outro. Host on Google Drive/YouTube, public link.
- GitHub repo public, .env never committed.
- Tutor's reference repo (batch 002, outdated libs, don't copy-paste) has scripts/database upload + agent.py + simulation.py.

Repo: https://github.com/reinerrekado/purwadhika-capstone-3 (created 2026-10-21; **made PUBLIC 2026-10-24** after a full-history audit with the real .env values found 0 leaks, K67). Streamlit app is PUBLIC (confirmed 2026-10-25: following redirects gives HTTP 200; the first 303 hop is just a cookie handshake, not a login wall); note the OpenRouter key has its own $5 limit (~$3.5 left on 2026-10-24) and the app stops answering if exhausted. Qdrant read-only key for the grader exists (only in .env + to be pasted in the Google Form, never in repo). Draft architecture artifact: https://claude.ai/artifact/MaBHfUY4FEzu43LUUX5mzr (repo copy deleted 2026-10-24, K56; README is now the only architecture doc). App name Rakfilm; Docker/devcontainer not required and removed (K55).

Clarified with Pak Herman 2026-10-22 (full table in repo `notes/keputusan-desain.md`, section "Klarifikasi Pak Herman"): langchain_qdrant + metadata filter ok; Qdrant must be viewable by tutor (read-only key); Langfuse v3, only agent system prompt in Langfuse, created via UI; traces per question grouped by session; agent remembers within a session by sending full st.session_state history (no checkpointer); chat history + tool calls + usage ALL mandatory; Streamlit Cloud deploy mandatory; no chunking ok; dataset CSV public in repo; OpenRouter via ChatOpenAI base_url.

**Why:** grading = meet minimums on time (≥80) plus extras for features/UI/presentation.
**How to apply:** check every design choice against the locked stack; keep the user able to explain every function ([[user-capstone-learning-style]]).

**Update 2026-10-25:** the user already sent Pak Herman (WhatsApp, because he said to send once progress is significant) the repo link, the Anatomi Capstone 3 artifact, the Rakfilm design canvas link and the app link. So those are live graded material: keep Anatomi artifact (do not delete) and keep it consistent with the real app; every push to main redeploys the public app. Pak Herman also told another student in the class group that chunking is unnecessary (combine title + a few columns) and reranker is optional but earns extra points.
