"""Gambar logo Rakfilm (K51): bingkai film oranye miring 3° dengan tanda tanya ("nonton apa?").

Dijalankan sekali dari folder root project:  python -m scripts.make_logo
Hasil: static/rakfilm_mark.png (logo sidebar, ikon tab browser, avatar asisten).
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

STATIC = Path(__file__).resolve().parent.parent / "static"
ORANGE = "#F2531B"
SCALE = 10  # desain dibuat di grid 48x48 (sama dengan SVG di mockup), digambar 10x supaya tajam


def box(x: float, y: float, w: float, h: float) -> tuple[int, int, int, int]:
    return (round(x * SCALE), round(y * SCALE), round((x + w) * SCALE), round((y + h) * SCALE))


def main() -> None:
    mark = Image.new("RGBA", (48 * SCALE, 48 * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(mark)
    draw.rounded_rectangle(box(3, 9, 42, 30), radius=6 * SCALE, fill=ORANGE)  # bingkai film
    clear = (0, 0, 0, 0)  # lubang transparan: warna latar sidebar/tab yang terlihat
    for x in (8, 16, 24, 32):  # lubang sproket atas dan bawah
        draw.rounded_rectangle(box(x, 12, 4, 3), radius=SCALE, fill=clear)
        draw.rounded_rectangle(box(x, 33, 4, 3), radius=SCALE, fill=clear)
    draw.rounded_rectangle(box(8, 17, 32, 14), radius=round(2.5 * SCALE), fill=clear)  # jendela film
    font = ImageFont.truetype(str(STATIC / "fonts" / "Anton-Regular.ttf"), 13 * SCALE)
    draw.text((24 * SCALE, 24.4 * SCALE), "?", font=font, fill=ORANGE, anchor="mm")
    mark = mark.rotate(3, resample=Image.BICUBIC)  # miring 3°, sama dengan pita film di IG story
    mark.save(STATIC / "rakfilm_mark.png", optimize=True)
    print("tersimpan:", STATIC / "rakfilm_mark.png")


if __name__ == "__main__":
    main()
