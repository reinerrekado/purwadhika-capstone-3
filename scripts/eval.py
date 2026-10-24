"""Set uji 10 pertanyaan (K60): jalankan agent sungguhan, periksa perilakunya otomatis, simpan laporan.

Dijalankan dari folder root project:  python -m scripts.eval
Hasilnya dicetak di terminal dan disimpan di notes/hasil-uji.md. Kode keluar 1 kalau ada pemeriksaan yang gagal.
Memakai LLM, Qdrant, dan Langfuse sungguhan: sekali jalan sekitar satu menit dan kurang dari satu sen.
"""

import json
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from langfuse import get_client

from app.agent import get_agent, reply_language, stream_agent
from app.tools import INDONESIAN_WORDS

REPORT = Path(__file__).resolve().parent.parent / "notes" / "hasil-uji.md"


@dataclass
class Result:
    """Satu giliran agent: pertanyaan, jawaban akhir, tool yang dipanggil, dan pemakaian token."""
    question: str
    answer: str
    calls: list[dict]  # [{"name", "args", "movies": [judul], "error": bool}]
    input_tokens: int
    output_tokens: int
    seconds: float
    prompt_version: int

    @property
    def tool_titles(self) -> list[str]:
        return [title for call in self.calls for title in call["movies"]]


@dataclass
class Check:
    """Satu pemeriksaan: fungsi (Result) -> bool, plus kalimat yang menjelaskannya."""
    description: str
    test: object  # callable(Result) -> bool


def run_turn(history: list[dict], question: str, session_id: str) -> Result:
    """Jalankan agent seperti streamlit_app.py: kirim seluruh riwayat sesi, pesan terakhir = pertanyaan baru."""
    run, started = {}, time.time()
    answer = "".join(stream_agent(history + [{"role": "user", "content": question}], session_id, run))
    seconds = time.time() - started
    new = run["messages"]
    results = {m.tool_call_id: m for m in new if m.type == "tool"}
    calls = []
    for message in (m for m in new if m.type == "ai"):
        for call in message.tool_calls:
            result = results.get(call["id"])
            try:
                body = json.loads(result.content) if result else {}
            except json.JSONDecodeError:  # pesan error tool berupa teks biasa
                body = {}
            calls.append({"name": call["name"], "args": call["args"], "movies": [m["title"] for m in body.get("movies", [])],
                          "error": bool(result and getattr(result, "status", "") == "error"),
                          "rejected": "error" in body})  # ditolak tool (mis. query tidak berbahasa Inggris), lalu diulang agent
    final = next((m.content for m in reversed(new) if m.type == "ai" and m.content), answer)
    ai = [m for m in new if m.type == "ai"]
    return Result(question, final, calls, sum((m.usage_metadata or {}).get("input_tokens", 0) for m in ai),
                  sum((m.usage_metadata or {}).get("output_tokens", 0) for m in ai), seconds, get_agent()[1].version)


# ---- Pemeriksaan: tiap fungsi membuat satu Check ----

def called(tool: str) -> Check:
    return Check(f"memanggil {tool}", lambda r: any(c["name"] == tool for c in r.calls))


def called_any(*tools: str) -> Check:
    return Check("memanggil salah satu dari " + ", ".join(tools), lambda r: any(c["name"] in tools for c in r.calls))


def not_called(tool: str) -> Check:
    return Check(f"tidak memanggil {tool}", lambda r: all(c["name"] != tool for c in r.calls))


def no_tools() -> Check:
    return Check("tidak memanggil tool apa pun", lambda r: not r.calls)


def arg_contains(tool: str, name: str, text: str) -> Check:
    return Check(f"{tool}({name}) memuat '{text}'", lambda r: any(
        c["name"] == tool and text.lower() in str(c["args"].get(name) or "").lower() for c in r.calls))


def arg_is(tool: str, name: str, value) -> Check:
    return Check(f"{tool}({name}) = {value!r}", lambda r: any(
        c["name"] == tool and c["args"].get(name) == value for c in r.calls))


def english_queries() -> Check:
    def test(r: Result) -> bool:
        queries = [c["args"].get("query", "") for c in r.calls if c["name"] == "search_movies" and not c["rejected"]]
        return all(not (set(re.findall(r"[a-z]+", q.lower())) & INDONESIAN_WORDS) for q in queries)
    return Check("query search_movies yang diterima berbahasa Inggris (K26, K61)", test)


def answer_has(*texts: str) -> Check:
    return Check("jawaban memuat " + ", ".join(f"'{t}'" for t in texts),
                 lambda r: all(t.lower() in r.answer.lower() for t in texts))


def answer_has_any(*texts: str) -> Check:
    return Check("jawaban memuat salah satu dari " + ", ".join(f"'{t}'" for t in texts),
                 lambda r: any(t.lower() in r.answer.lower() for t in texts))


def answer_lacks(text: str) -> Check:
    return Check(f"jawaban tidak memuat '{text}'", lambda r: text.lower() not in r.answer.lower())


def answer_lists(count: int) -> Check:
    return Check(f"jawaban menyebut ≥{count} film dari hasil tool",
                 lambda r: sum(t.lower() in r.answer.lower() for t in set(r.tool_titles)) >= count)


def before(first: str, second: str) -> Check:
    def test(r: Result) -> bool:
        text = r.answer.lower()
        return first.lower() in text and second.lower() in text and text.index(first.lower()) < text.index(second.lower())
    return Check(f"'{first}' disebut sebelum '{second}'", test)


GENERAL = [  # berlaku untuk semua pertanyaan
    Check("jawaban tidak kosong", lambda r: bool(r.answer.strip())),
    Check("tidak ada error tool", lambda r: not any(c["error"] for c in r.calls)),
    Check("jawaban tidak ditutup dengan pertanyaan (aturan 6 prompt)", lambda r: not r.answer.strip().endswith("?")),
    Check("bahasa jawaban sama dengan bahasa pertanyaan (K65)",
          lambda r: reply_language(r.answer) == reply_language(r.question)),
]


@dataclass
class Case:
    question: str
    focus: str  # yang diuji
    checks: list[Check]
    follows: int | None = None  # nomor kasus yang menjadi riwayat percakapan (mulai dari 1)
    outcome: list[tuple[str, bool]] = field(default_factory=list)
    result: Result | None = None


CASES = [
    Case("film tentang pencuri yang masuk ke mimpi orang", "cari dari cerita (RAG)",
         [called("search_movies"), english_queries(), answer_has("Inception")]),
    Case("film yang mirip Interstellar", "film mirip",
         [called("similar_movies"), answer_has_any("Gravity", "The Martian", "Arrival")]),
    Case("siapa sutradara Parasite dan berapa ratingnya?", "judul asli ≠ judul populer (K32)",
         # get_person_info boleh dipakai model; tool itu meneruskan judul film ke pencarian film (K71)
         [called_any("get_movie_details", "get_person_info"), answer_has("Bong Joon Ho", "8.6")]),
    Case("5 film horor terbaik", "peringkat per genre",
         [called("rank_movies"), arg_is("rank_movies", "genre", "Horror"), answer_lists(5), before("Psycho", "The Shining")]),
    Case("rekomendasikan film horor", "rekomendasi genre saja (K49)",
         [called("rank_movies"), not_called("search_movies"), answer_lists(5)]),
    Case("film christoper nolan", "typo nama sutradara",
         [called("rank_movies"), arg_contains("rank_movies", "director", "nolan"), answer_has("The Dark Knight", "Inception")]),
    Case("yang mana paling lama?", "ingatan percakapan", [answer_has("Interstellar", "169")], follows=6),
    Case("Star Wars mana yang paling bagus?", "seri film (K30)",
         [called("rank_movies"), arg_contains("rank_movies", "title", "star wars"), answer_has("Empire Strikes Back")]),
    Case("film dengan adegan pria menari di tangga", "kejujuran soal adegan (K59)",
         [called("search_movies"), english_queries(), arg_is("search_movies", "describes_scene", True),
          answer_has("sinopsis"), answer_lacks("Berikut film dengan adegan")]),
    Case("cara masak rendang", "di luar topik", [no_tools(), answer_has_any("film")]),
    Case("film horor tahun 80-an", "filter tahun",
         [called("rank_movies"), arg_is("rank_movies", "year_from", 1980), arg_is("rank_movies", "year_to", 1989),
          answer_has("The Shining", "The Thing")]),
    Case("ada berapa film Hayao Miyazaki tahun 2000-an?", "pertanyaan hitung",
         [called("rank_movies"), arg_contains("rank_movies", "director", "miyazaki"), answer_has_any("3 film", "tiga film")]),
    Case("bandingkan The Godfather dan Goodfellas", "membandingkan dua film",
         [called("get_movie_details"), answer_has("The Godfather", "Goodfellas")]),
    Case("movies like Inception", "pertanyaan berbahasa Inggris (K65)",
         [called("similar_movies"), answer_has_any("Inside Man", "The Matrix", "Gattaca", "The Bourne")]),
    Case("siapa Christopher Nolan?", "profil orang (K71)",
         [called("get_person_info"), answer_has("Nolan"), answer_has_any("pembuat film", "sutradara", "filmmaker")]),
    Case("tell me about Tom Hanks", "profil orang, bahasa Inggris (K71)",
         [called("get_person_info"), answer_has("Hanks"), answer_has_any("actor", "filmmaker")]),
    Case("siapa Gal Gadot?", "orang yang tidak ada di dataset (K71)",
         [called("get_person_info"), answer_lacks("Wonder Woman"), answer_has_any("tidak", "bukan")]),
]


def run_case(case: Case, number: int, session: str) -> None:
    history = []
    if case.follows:  # riwayat = pertanyaan dan jawaban kasus sebelumnya, seperti st.session_state.chat di app
        previous = CASES[case.follows - 1]
        history = [{"role": "user", "content": previous.question}, {"role": "assistant", "content": previous.result.answer}]
    case.result = run_turn(history, case.question, f"eval-{session}-{number}")
    case.outcome = [(check.description, bool(check.test(case.result))) for check in GENERAL + case.checks]


def write_report(started: datetime, passed: int, total: int) -> None:
    first = CASES[0].result
    lines = [f"# Hasil uji agent ({started:%Y-%m-%d %H:%M})", "",
             f"Prompt `movie-agent-system` v{first.prompt_version}. Pemeriksaan lolos: **{passed}/{total}**. "
             "Dibuat otomatis oleh `python -m scripts.eval`.", "",
             "| # | Pertanyaan | Yang diuji | Hasil | Detik | Token (in/out) |", "|---|---|---|---|---|---|"]
    for n, case in enumerate(CASES, 1):
        ok = all(passed_ for _, passed_ in case.outcome)
        r = case.result
        lines.append(f"| {n} | {case.question} | {case.focus} | {'lolos' if ok else '**GAGAL**'} | {r.seconds:.1f} | "
                     f"{r.input_tokens:,} / {r.output_tokens:,} |")
    for n, case in enumerate(CASES, 1):
        r = case.result
        calls = "; ".join(f"`{c['name']}({', '.join(f'{k}={v!r}' for k, v in c['args'].items() if v is not None)})`"
                          for c in r.calls) or "tidak ada tool"
        lines += ["", f"## {n}. {case.question}", f"- Tool: {calls}"]
        lines += [f"- {'lolos' if ok else '**GAGAL**'}: {description}" for description, ok in case.outcome]
        lines.append("- Jawaban: " + r.answer.strip().replace("\n", " ")[:300])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    started, session = datetime.now(), uuid.uuid4().hex[:6]
    print(f"Menjalankan {len(CASES)} pertanyaan (sesi eval-{session}) ...\n")
    for number, case in enumerate(CASES, 1):
        run_case(case, number, session)
        failed = [description for description, ok in case.outcome if not ok]
        print(f"[{'OK' if not failed else 'GAGAL'}] {number:>2}. {case.question}  ({case.result.seconds:.1f} dtk)")
        for description in failed:
            print(f"        x {description}")
    passed = sum(ok for case in CASES for _, ok in case.outcome)
    total = sum(len(case.outcome) for case in CASES)
    cases_ok = sum(all(ok for _, ok in case.outcome) for case in CASES)
    write_report(started, passed, total)
    get_client().flush()
    print(f"\nPertanyaan lolos {cases_ok}/{len(CASES)}, pemeriksaan lolos {passed}/{total}. Laporan: {REPORT}")
    raise SystemExit(0 if cases_ok == len(CASES) else 1)


if __name__ == "__main__":
    main()
