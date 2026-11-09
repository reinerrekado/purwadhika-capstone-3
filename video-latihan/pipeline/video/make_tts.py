"""Narasi per segmen dengan Edge neural TTS (id-ID-ArdiNeural). Hasil: audio/<id>.mp3 dan audio/durations.json."""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
if sys.platform == "win32":
    sys.path.insert(0, str(Path(__file__).parent.parent / "pylib"))  # bundel Windows; di Mac: pip install imageio-ffmpeg edge-tts
import edge_tts  # noqa: E402
import imageio_ffmpeg  # noqa: E402
from segments import S, speech_text  # noqa: E402

VOICE = sys.argv[1] if len(sys.argv) > 1 else "id-ID-ArdiNeural"
OUT = Path(__file__).parent / "audio"
OUT.mkdir(exist_ok=True)
FFPROBE = Path(imageio_ffmpeg.get_ffmpeg_exe()).with_name("ffprobe.exe")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def duration(path: Path) -> float:
    # ffprobe tidak ikut di bundel imageio; pakai ffmpeg -i dan baca "Duration".
    out = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True, errors="replace").stderr
    for line in out.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"durasi tidak terbaca: {path}")


async def one(seg, sem):
    path = OUT / f"{seg['id']}.mp3"
    if path.exists() and path.stat().st_size > 1000:
        return
    async with sem:
        for attempt in range(4):
            try:
                await edge_tts.Communicate(speech_text(seg["text"]), VOICE, rate="+0%").save(str(path))
                if path.stat().st_size > 1000:
                    return
            except Exception as e:  # noqa: BLE001
                print(f"{seg['id']} percobaan {attempt + 1} gagal: {e}", flush=True)
                await asyncio.sleep(2 + attempt * 3)
        raise RuntimeError(f"TTS gagal untuk {seg['id']}")


async def main():
    sem = asyncio.Semaphore(3)
    await asyncio.gather(*(one(s, sem) for s in S if s["text"]))
    durs = {s["id"]: (duration(OUT / f"{s['id']}.mp3") if s["text"] else s["hold"]) for s in S}
    (OUT / "durations.json").write_text(json.dumps(durs, indent=1))
    total = sum(durs.values())
    print(f"{sum(1 for s in S if s['text'])} potongan audio, total narasi {total / 60:.1f} menit (belum termasuk jeda dan waktu tunggu demo)")
    per = {}
    for s in S:
        per[s["section"]] = per.get(s["section"], 0) + durs[s["id"]]
    for k, v in per.items():
        print(f"  bagian {k}: {v:.0f} dtk")


asyncio.run(main())
