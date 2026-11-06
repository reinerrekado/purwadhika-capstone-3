"""Arsitektur supervisor: 1 supervisor + 2 sub-agent (rag_agent, data_agent). Setiap run di-trace ke Langfuse.

Agent = LLM + prompt + tool. Supervisor hanya memilih sub-agent; sub-agent yang memanggil tool film.
"""

import re
from collections.abc import Iterator
from functools import lru_cache

from langchain.agents import create_agent
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langgraph_supervisor import create_supervisor
from langgraph_supervisor.handoff import create_forward_message_tool

from app.config import get_llm
from app.tools import INDONESIAN_WORDS, get_movie_details, get_person_info, rank_movies, search_movies, similar_movies

PROMPT_NAME = "movie-agent-system"  # prompt sub-agent; dibuat lewat UI Langfuse, label "production" (K03)
SUPERVISOR_PROMPT_NAME = "movie-supervisor-system"  # prompt supervisor; dibuat lewat API Langfuse, label "production"

# Kata penanda bahasa (K65). Heuristik sederhana: bahasa dengan kata penanda terbanyak menang, seri = Indonesia.
ENGLISH_MARKERS = {"the", "is", "are", "what", "who", "how", "which", "movie", "movies", "like", "about", "best", "with",
                   "for", "of", "an", "me", "show", "find", "recommend", "directed", "does", "do", "can", "any", "some",
                   "from", "in", "to", "there", "many", "similar", "give", "list", "and", "that", "this", "longest"}
INDONESIAN_MARKERS = INDONESIAN_WORDS | {"film", "apa", "siapa", "berapa", "bagaimana", "mana", "paling", "terbaik",
                                         "mirip", "ada", "tolong", "carikan", "dong", "bisa", "dan", "di", "ke", "sutradara"}


def reply_language(text: str) -> str:
    """"English" kalau pesan lebih banyak memuat kata penanda Inggris, selain itu "Indonesian" (termasuk kalau seri)."""
    words = re.findall(r"[a-z]+", text.lower())
    english, indonesian = sum(w in ENGLISH_MARKERS for w in words), sum(w in INDONESIAN_MARKERS for w in words)
    return "English" if english > indonesian else "Indonesian"


# Kalimat penutup berupa tawaran ("Jika Anda ingin ...", "Let me know ..."). Prompt v5 dan v8 melarangnya, tapi
# gpt-4.1-mini kadang tetap menulisnya, jadi ditegakkan di kode (K74). Hanya kalimat PALING AKHIR yang dipotong.
OFFER = re.compile(
    r"^(jika|kalau|bila)\s+(anda|kamu|kau)\s+(ingin|mau|berminat|butuh|perlu)\b|"
    r"^(apakah|apa)\s+(anda|kamu)\s+(ingin|mau)\b|^(mau|ingin)\s+(saya|aku)\b|^silakan\s+(beri tahu|tanya|kabari)|"
    r"^saya\s+(bisa|dapat|siap)\s+(memberikan|membantu|menjelaskan|mencarikan)|"
    r"^(if you(?:'d| would)? (?:like|want)|let me know|would you like|do you want|feel free)\b",
    re.IGNORECASE)


def trim_offer(answer: str) -> str:
    """Buang kalimat penutup yang hanya menawarkan bantuan lanjutan. Teks lain tidak disentuh."""
    paragraphs = answer.rstrip().split("\n\n")
    sentences = re.split(r"(?<=[.!?])\s+", paragraphs[-1])
    while sentences and OFFER.match(sentences[-1].strip()):
        sentences.pop()
    kept = paragraphs[:-1] + ([" ".join(sentences)] if sentences else [])
    return "\n\n".join(kept) if kept else answer  # jangan pernah mengosongkan jawaban


@lru_cache(maxsize=4)
def _build_agent(system_prompt: str, supervisor_prompt: str):
    """Supervisor + 2 sub-agent. Sub-agent memakai prompt agent; supervisor hanya memilih sub-agent."""
    llm = get_llm()
    rag_agent = create_agent(model=llm, tools=[search_movies, similar_movies], system_prompt=system_prompt, name="rag_agent")
    data_agent = create_agent(model=llm, tools=[get_movie_details, rank_movies, get_person_info],
                              system_prompt=system_prompt, name="data_agent")
    return create_supervisor([rag_agent, data_agent], model=llm, prompt=supervisor_prompt, output_mode="full_history",
                             tools=[create_forward_message_tool("supervisor")]).compile()  # teruskan, jangan tulis ulang


def get_agent():
    """Supervisor + objek prompt Langfuse sub-agent dan supervisor. SDK Langfuse menyimpan prompt 60 detik,
    jadi versi baru terpakai tanpa restart (K35)."""
    prompt, supervisor_prompt = get_client().get_prompt(PROMPT_NAME), get_client().get_prompt(SUPERVISOR_PROMPT_NAME)
    return _build_agent(prompt.compile(), supervisor_prompt.compile()), prompt, supervisor_prompt


def stream_agent(messages: list[dict], session_id: str, run: dict) -> Iterator[str]:
    """Jalankan agent dengan seluruh riwayat sesi (K07) dan alirkan teks jawaban potong demi potong.

    messages: [{"role": "user" | "assistant", "content": "..."}], pesan terakhir = pertanyaan baru.
    run: diisi setelah selesai, berisi "messages" (pesan baru dari run ini) dan "trace_id" (untuk feedback).
    """
    agent, prompt, supervisor_prompt = get_agent()
    if reply_language(messages[-1]["content"]) == "English":  # model mengabaikan aturan bahasa di prompt, jadi ditegakkan di sini (K65)
        messages = messages[:-1] + [{**messages[-1], "content": messages[-1]["content"] + "\n\n(Reply in English.)"}]
    handler = CallbackHandler()  # trace ke Langfuse (Sesi 17)
    config = {"callbacks": [handler], "metadata": {
        "langfuse_session_id": session_id,  # satu percakapan = satu session
        # feedback bisa dibandingkan per versi prompt sub-agent dan supervisor
        "langfuse_tags": [f"prompt-v{prompt.version}", f"supervisor-v{supervisor_prompt.version}"],
        "langfuse_prompt": prompt,  # menautkan generation ke prompt: metrik per versi di Langfuse terisi (K73)
    }}
    history, last_source = [], None
    for namespace, mode, data in agent.stream({"messages": messages}, config=config, stream_mode=["messages", "values"],
                                              subgraphs=True):
        if mode == "messages":  # potongan token dari LLM
            chunk, meta = data  # meta["langgraph_node"]: "model" (sub-agent) atau "agent" (supervisor)
            source = namespace[0].split(":")[0] if namespace else None  # "supervisor", "rag_agent", atau "data_agent"
            # Yang tampil: jawaban sub-agent. Teks supervisor hanya kalau belum ada sub-agent yang menjawab (di luar
            # topik); kalau supervisor menulis ulang jawaban sub-agent, tulisan ulang itu tidak ditampilkan dua kali.
            if (meta["langgraph_node"] not in ("model", "agent") or not chunk.content
                    or (source == "supervisor" and last_source not in (None, "supervisor"))):
                continue
            if last_source not in (None, source):
                yield "\n\n"  # dua sub-agent menjawab berurutan (pertanyaan lintas domain)
            last_source = source
            yield chunk.content
        elif not namespace:  # "values" tingkat atas: state penuh (pesan masukan + semua pesan baru)
            history = data["messages"]
    run.update(messages=history[len(messages):], trace_id=handler.last_trace_id)


def send_feedback(trace_id: str, thumbs_up: bool) -> None:
    """Simpan 👍/👎 user sebagai score di trace Langfuse (K36)."""
    get_client().create_score(
        trace_id=trace_id, name="user_feedback", value=int(thumbs_up), data_type="BOOLEAN",
        score_id=f"{trace_id}-feedback",  # id tetap: ganti 👍 ke 👎 menimpa score lama, bukan menambah
    )
