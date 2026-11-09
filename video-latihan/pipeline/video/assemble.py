"""Rakit video latihan Rakfilm: tiap segmen (visual + narasi) jadi MP4 1920x1080 dengan rangka, panel narator, teleprompter,
label bagian, dan pewaktu; lalu digabung. Keluaran di <repo>/video-latihan/.

Pakai: python assemble.py            semua segmen
       python assemble.py 001 015    hanya segmen tertentu (uji)
"""
import json
import subprocess
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
if sys.platform == "win32":
    sys.path.insert(0, str(HERE.parent / "pylib"))  # bundel Windows; di Mac: pip install imageio-ffmpeg edge-tts
import imageio_ffmpeg  # noqa: E402
from segments import PLAN, S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
FF = imageio_ffmpeg.get_ffmpeg_exe()
REPO = Path(r"C:\Users\reine\OneDrive\Documents\Work Repository\Capstone Project Purwadhika")
OUT = REPO / "video-latihan"
SEGDIR = HERE / "seg"
SEGDIR.mkdir(exist_ok=True)
(OUT / "bagian").mkdir(parents=True, exist_ok=True)
FRAME = {"two": OUT / "rangka" / "rakfilm-rangka-1920x1080.png", "wide": OUT / "rangka" / "rakfilm-rangka-lebar-1920x1080.png"}
LOGO = REPO / "static" / "rakfilm_mark.png"
if sys.platform == "win32":
    FONT, FONT_B = r"C\:/Windows/Fonts/segoeui.ttf", r"C\:/Windows/Fonts/seguisb.ttf"
else:  # macOS
    FONT, FONT_B = "/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
DURS = json.loads((HERE / "audio" / "durations.json").read_text())
STEPS_FILE = HERE / "demo" / "steps.json"
STEPS = json.loads(STEPS_FILE.read_text()) if STEPS_FILE.exists() else {}
DEMO = HERE / "demo" / "demo.webm"
ONLY = set(sys.argv[1:])
TAIL = 0.5  # jeda setelah narasi sebelum pindah visual
DEMO_ORDER = [s["visual"][1] for s in S if s["visual"][0] == "demo"] + ["end"]


def esc(path: Path) -> str:
    return str(path).replace("\\", "/").replace(":", "\\:")


def visual_input(seg):
    kind = seg["visual"][0]
    if kind == "slide":
        return ["-loop", "1", "-framerate", "30", "-i", str(HERE / "slides" / f"{seg['visual'][1]}-{seg['visual'][2]}.png")], None
    if kind == "code":
        _, file, a, b, _sym = seg["visual"]
        return ["-loop", "1", "-framerate", "30", "-i", str(HERE / "code" / f"{file.replace('/', '_')}-{a}-{b}.png")], None
    if kind == "shot":
        name = seg["visual"][1]
        real = HERE / "shots-real" / f"{name}.png"
        return ["-loop", "1", "-framerate", "30", "-i", str(real if real.exists() else HERE / "shots" / f"{name}.png")], None
    if kind == "demo":
        name = seg["visual"][1]
        if STEPS and DEMO.exists() and name in STEPS:
            start = STEPS[name]
            end = STEPS[DEMO_ORDER[DEMO_ORDER.index(name) + 1]]
            return ["-ss", f"{start:.3f}", "-i", str(DEMO)], end - start
        return ["-loop", "1", "-framerate", "30", "-i", str(HERE.parent / "jawaban-tool-call.png")], None  # cadangan
    raise ValueError(kind)


def duration(seg, clip_len):
    narr = DURS[seg["id"]] if seg["text"] else seg["hold"]
    if clip_len is not None:
        return max(clip_len, narr + 0.3)
    return narr + (TAIL if seg["text"] else 0)


def wrap(text, width):
    return "\n".join(textwrap.wrap(text, width)) if text else ""


def build(seg, offset):
    sid = seg["id"]
    vin, clip_len = visual_input(seg)
    dur = duration(seg, clip_len)
    audio = HERE / "audio" / f"{sid}.mp3"
    ain = ["-i", str(audio)] if seg["text"] and audio.exists() else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    wide = seg["mode"] == "wide"
    is_slide = seg["visual"][0] == "slide"  # slide deck sudah memuat rangka sendiri: pakai penuh, tanpa overlay rangka
    cx, cy, cw, ch = (0, 0, 1920, 1080) if is_slide else ((64, 64, 1792, 952) if wide else (64, 64, 1144, 952))
    label = f"Bagian {seg['section']} · {seg['label']}"
    (SEGDIR / f"{sid}.lbl").write_text(label, encoding="utf-8", newline="\n")
    if wide:
        text = wrap(seg["text"], 84)
        fs = 28
        narr_draw = (f"drawtext=fontfile='{FONT}':textfile='{esc(SEGDIR / f'{sid}.txt')}':expansion=none:fontcolor=0xEDEAE4:fontsize={fs}"
                     f":line_spacing=8:box=1:boxcolor=0x0E0D0C@0.82:boxborderw=22:x=104:y=978-text_h")
        logo_sz, logo_xy, wave_sz, wave_xy, cap_xy = 104, (1604, 592), "300x84", (1506, 728), (1506, 836)
    else:
        text = wrap(seg["text"], 40)
        fs = 26
        if text.count("\n") >= 12:
            text, fs = wrap(seg["text"], 46), 23
        narr_draw = (f"drawtext=fontfile='{FONT}':textfile='{esc(SEGDIR / f'{sid}.txt')}':expansion=none:fontcolor=0xEDEAE4:fontsize={fs}"
                     f":line_spacing=10:x=1296:y=486")
        logo_sz, logo_xy, wave_sz, wave_xy, cap_xy = 150, (1481, 118), "520x110", (1296, 300), (1296, 436)
    (SEGDIR / f"{sid}.txt").write_text(text, encoding="utf-8", newline="\n")
    timer = ("drawtext=fontfile='%s':text='%%{eif\\:trunc((t+%.3f)/60)\\:d\\:2}\\:%%{eif\\:mod(t+%.3f\\,60)\\:d\\:2}'"
             ":fontcolor=0x9A948B:fontsize=22:x=1856-text_w:y=20" % (FONT, offset, offset))
    frame_step = ["[v3]null[v4]"] if is_slide else ["[v3][3:v]overlay=0:0[v4]"]
    graph = ";\n".join([
        f"[0:v]scale={cw}:{ch}:force_original_aspect_ratio=decrease,pad={cw}:{ch}:(ow-iw)/2:(oh-ih)/2:color=0x161513,setsar=1,fps=30[content]",
        "color=c=0x0E0D0C:s=1920x1080:r=30[bg]",
        f"[bg][content]overlay={cx}:{cy}[v1]",
        "[1:a]aformat=channel_layouts=stereo:sample_rates=48000,apad,asplit=2[a1][a2]",
        f"[a1]showwaves=s={wave_sz}:mode=cline:colors=0xF2531B|0xFF9E7A:rate=30:scale=sqrt:draw=full[wave]",
        f"[v1][wave]overlay={wave_xy[0]}:{wave_xy[1]}[v2]",
        f"[2:v]scale={logo_sz}:{logo_sz}[logo]",
        f"[v2][logo]overlay={logo_xy[0]}:{logo_xy[1]}[v3]",
        *frame_step,
        f"[v4]drawtext=fontfile='{FONT}':text='Narator latihan · Ardi (Edge TTS) · teks = naskah':expansion=none:fontcolor=0x9A948B:fontsize=18:x={cap_xy[0]}:y={cap_xy[1]}[v5]",
        f"[v5]{narr_draw}[v6]",
        f"[v6]drawtext=fontfile='{FONT_B}':textfile='{esc(SEGDIR / f'{sid}.lbl')}':expansion=none:fontcolor=0x9A948B:fontsize=22:x=64:y=20[v7]",
        f"[v7]{timer}[vout]",
    ])
    (SEGDIR / f"{sid}.filter").write_text(graph, encoding="utf-8")
    out = SEGDIR / f"{sid}.mp4"
    cmd = [FF, "-y", "-hide_banner", "-loglevel", "error", *vin, *ain, "-i", str(LOGO), "-i", str(FRAME[seg["mode"]]),
           "-/filter_complex", str(SEGDIR / f"{sid}.filter"), "-map", "[vout]", "-map", "[a2]",
           "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"segmen {sid} gagal:\n{r.stderr[-1500:]}")
    return dur


def main():
    segs = [s for s in S if not ONLY or s["id"] in ONLY]
    # offset (waktu mulai) tiap segmen dihitung dulu secara berurutan
    offsets, t = {}, 0.0
    for s in S:
        offsets[s["id"]] = t
        _, clip_len = visual_input(s)
        t += duration(s, clip_len)
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda s: (s["id"], build(s, offsets[s["id"]])), segs))
    for sid, d in results:
        print(f"ok {sid} {d:5.1f}s", flush=True)
    if ONLY:
        return
    # gabungan penuh
    lst = SEGDIR / "all.txt"
    lst.write_text("".join(f"file '{(SEGDIR / f'{s['id']}.mp4').as_posix()}'\n" for s in S), encoding="utf-8")
    final = OUT / "rakfilm-latihan.mp4"
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(final)], check=True)
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", str(final), "-vn", "-c:a", "libmp3lame", "-b:a", "160k",
                    str(OUT / "rakfilm-latihan.mp3")], check=True)
    # per bagian
    sections = []
    for s in S:
        if s["section"] not in sections:
            sections.append(s["section"])
    for sec in sections:
        part = [s for s in S if s["section"] == sec]
        lst = SEGDIR / f"sec-{sec}.txt"
        lst.write_text("".join(f"file '{(SEGDIR / f'{s['id']}.mp4').as_posix()}'\n" for s in part), encoding="utf-8")
        name = f"{sec.zfill(3 if sec[-1].isalpha() else 2)}-{part[0]['label'].lower().replace(' ', '-')}.mp4"
        subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                        str(OUT / "bagian" / name)], check=True)
    # SRT dan laporan durasi
    def ts(x):
        h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
    srt, n = [], 0
    actual = {}
    for s in S:
        _, clip_len = visual_input(s)
        d = duration(s, clip_len)
        actual[s["section"]] = actual.get(s["section"], 0) + d
        if s["text"]:
            n += 1
            srt.append(f"{n}\n{ts(offsets[s['id']])} --> {ts(offsets[s['id']] + d)}\n{s['text']}\n")
    (OUT / "rakfilm-latihan.srt").write_text("\n".join(srt), encoding="utf-8")
    total_plan, total_act = sum(PLAN.values()), sum(actual.values())
    rows = ["| Bagian | Rencana naskah | Aktual video latihan | Selisih | Mulai di video utuh |", "|---|---|---|---|---|"]
    labels = {s["section"]: s["label"] for s in S}
    starts = {}  # detik mulai tiap bagian = offset segmen pertamanya (pengganti potongan bagian/ yang tidak ikut git)
    for s in S:
        starts.setdefault(s["section"], offsets[s["id"]])
    for sec in sections:
        p, a, st = PLAN[sec], actual[sec], starts[sec]
        rows.append(f"| {sec} · {labels[sec]} | {p // 60:.0f}:{p % 60:02.0f} | {a // 60:.0f}:{a % 60:02.0f} | {'+' if a >= p else '−'}{abs(a - p) // 60:.0f}:{abs(a - p) % 60:02.0f} | {st // 60:.0f}:{st % 60:02.0f} |")
    rows.append(f"| **Total** | **{total_plan // 60:.0f}:{total_plan % 60:02.0f}** | **{total_act // 60:.0f}:{total_act % 60:02.0f}** | "
                f"**{'+' if total_act >= total_plan else '−'}{abs(total_act - total_plan) // 60:.0f}:{abs(total_act - total_plan) % 60:02.0f}** | |")
    report = ["# Laporan durasi video latihan", "",
              "Narasi dibacakan Edge TTS (id-ID-Ardi) pada kecepatan normal; waktu demo app = waktu tunggu app sungguhan. "
              "Selisih positif = naskah lebih panjang dari rencana.", "", *rows, "",
              "Batas video 15:00. Kalau total di atas itu, pangkas dulu bagian dengan selisih terbesar.", ""]
    (OUT / "laporan-durasi.md").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(rows))
    print("selesai:", final)


main()
