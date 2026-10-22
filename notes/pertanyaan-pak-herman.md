# Pertanyaan Capstone 3 untuk Pak Herman

> **Catatan sementara.** Dibuat 22 Oktober 2026. Hapus atau ringkas file ini setelah semua pertanyaan terjawab.
> Kasus yang saya pilih: **IMDB Top 1000** (asisten rekomendasi film).

Setiap pertanyaan berisi: **latar belakang** (kenapa saya bingung), **pertanyaan** (kalimat yang bisa langsung saya tanyakan), dan **rencana saya** kalau belum sempat dijawab, supaya pengerjaan tidak tertahan.

---

## Sudah diputuskan, tidak perlu ditanyakan

- **Membuat agent dengan `create_agent`** dari `langchain.agents`. `create_react_agent` (dari `langgraph.prebuilt`) sudah *deprecated* sejak LangGraph 1.0, dan notebook Sesi 10 juga memakai `create_agent`. Prinsipnya: pakai yang relevan dengan versi library terbaru.

---

## 1. Qdrant: harus lewat LangChain, dan bolehkah menambah filter?

**Latar belakang**

Di kelas (Sesi 12 dan `main.py` Sesi 14), Qdrant dipakai lewat **`langchain_qdrant.QdrantVectorStore`**:

```python
# upload (Sesi 12)
QdrantVectorStore.from_documents(documents, embeddings, url=..., api_key=..., collection_name=...)

# cari (Sesi 14)
qdrant = QdrantVectorStore.from_existing_collection(embedding=embeddings, collection_name=..., url=..., api_key=...)
docs = qdrant.similarity_search(query, k=10)
```

Dataset IMDB punya kolom terstruktur (genre, tahun, sutradara). Saya ingin menambah **filter** saat mencari, misalnya "film thriller setelah tahun 2000": vektor mencari makna ceritanya, filter memastikan genre dan tahunnya. Di kelas, pencarian dilakukan tanpa filter.

```python
docs = qdrant.similarity_search(
    query, k=5,
    filter=models.Filter(must=[
        models.FieldCondition(key="metadata.genres", match=models.MatchValue(value="Thriller")),
        models.FieldCondition(key="metadata.year", range=models.Range(gte=2000)),
    ]),
)
```

**Pertanyaan**

1. Apakah Qdrant **wajib** dipakai lewat `langchain_qdrant`, atau boleh juga langsung pakai `qdrant_client` (misalnya `client.query_points(...)`)?
2. Bolehkah RAG tool saya memakai **filter metadata** seperti di atas? Apakah ini dihitung sebagai nilai tambah?
3. Untuk penilaian, apakah cukup memberi **URL cluster + API key read-only** supaya Bapak bisa melihat isi collection?

**Rencana saya kalau belum dijawab:** tetap pakai `langchain_qdrant` seperti di kelas, ditambah filter metadata.

---

## 2. Langfuse: ikut slide (v2) atau notebook (v3)?

**Latar belakang**

Di catatan Sesi 17 saya menemukan bahwa **slide 26–28 memakai cara Langfuse versi 2**, sedangkan **notebook memakai versi 3**. Di kelas exercise Bapak juga sempat bilang contoh capstone "masih yang lama, harusnya pakai `get_client`".

| Hal | Slide (v2) | Notebook (v3) |
|---|---|---|
| Membuat klien | `Langfuse()` | `get_client()` |
| Import handler | `from langfuse.callback import CallbackHandler` | `from langfuse.langchain import CallbackHandler` |
| Isi session/user | `CallbackHandler(session_id=..., user_id=...)` | `CallbackHandler()` **tanpa argumen**, session lewat `config` |

Rencana kode saya (v3):

```python
from langfuse import get_client
from langfuse.langchain import CallbackHandler

langfuse = get_client()
system_prompt = langfuse.get_prompt("movie-agent-system").compile()

agent.invoke(
    {"messages": messages},
    config={
        "callbacks": [CallbackHandler()],
        "metadata": {"langfuse_session_id": session_id},
    },
)
```

**Pertanyaan**

1. Untuk capstone, apakah yang benar memakai **Langfuse v3** (`get_client`, `CallbackHandler()` tanpa argumen) seperti di notebook?
2. "Semua prompt disimpan di Langfuse" itu maksudnya **system prompt agent saja**, atau juga **deskripsi tool** (docstring `@tool`) dan prompt kecil lain?
3. Apakah prompt harus dibuat **lewat kode** (`langfuse.create_prompt(...)`) supaya terlihat di repo, atau cukup dibuat **lewat UI Langfuse**?
4. Apakah trace perlu dikelompokkan per **session** (satu percakapan = satu session), atau cukup trace per pertanyaan?

**Rencana saya kalau belum dijawab:** pakai v3. System prompt di Langfuse dan dibuat lewat script supaya bisa diulang. Docstring tool tetap di kode. Trace dikelompokkan per session.

---

## 3. Chat history: hanya ditampilkan, atau agent harus ingat percakapan?

**Latar belakang**

Di `main.py` Sesi 14, riwayat chat disimpan di `st.session_state.messages`, tapi **hanya untuk ditampilkan di layar**. Yang dikirim ke agent hanya pesan terakhir:

```python
response = agent.invoke({"messages": [{"role": "user", "content": prompt_U}]})
```

Akibatnya agent **tidak ingat** isi percakapan sebelumnya. Contoh:

> **User:** Rekomendasikan 3 film thriller tahun 90-an.
> **Agent:** 1. The Silence of the Lambs, 2. Se7en, 3. The Usual Suspects.
> **User:** Yang kedua siapa sutradaranya?
> **Agent:** *(tidak tahu "yang kedua" itu film apa)*

Di kelas exercise Bapak menyebut contoh Streamlit capstone punya **chat history, tool call, dan usage detail**.

**Pertanyaan**

1. "Chat history" di ketentuan itu maksudnya **riwayat yang ditampilkan di layar** saja, atau **agent juga harus ingat percakapan**?
2. Kalau agent harus ingat, cara mana yang Bapak harapkan?
   - **(a)** Kirim seluruh `st.session_state.messages` ke agent setiap kali bertanya (paling sederhana).
   - **(b)** Pakai **checkpointer** (`InMemorySaver`, dari slide 22 Sesi 10) dengan `thread_id` per sesi.
3. Dari rekaman saya kurang jelas: **chat history, tool call, dan usage detail** itu **ketiganya wajib**, atau cukup salah satu?

**Rencana saya kalau belum dijawab:** ketiganya saya buat. Agent dibuat ingat percakapan dengan cara (a), karena paling mudah dijelaskan.

---

## Pertanyaan tambahan (kalau ada waktu)

1. **Deploy:** apakah app Streamlit **wajib** di-deploy ke Streamlit Community Cloud, atau cukup bisa dijalankan lokal dan ditunjukkan di video?
2. **Chunking:** overview IMDB paling panjang 313 karakter (56 kata), jadi saya tidak melakukan chunking (1 film = 1 vektor). Apakah cukup dijelaskan alasannya di video, atau tetap harus ada chunking?
3. **Dataset di repo:** bolehkan `imdb_top_1000.csv` (±430 KB) ikut di-commit ke GitHub publik supaya script ingestion bisa langsung dijalankan?
4. **OpenRouter:** untuk LangChain, kelas chat OpenRouter yang Bapak pakai yang mana? Atau cukup `ChatOpenAI` dengan `base_url` OpenRouter?

---

## Jawaban Pak Herman

> Diisi setelah bertanya.

| No | Jawaban | Tanggal |
|---|---|---|
| 1. Qdrant | | |
| 2. Langfuse | | |
| 3. Chat history | | |
| Tambahan | | |
