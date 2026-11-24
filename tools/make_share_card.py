"""Render assets/share-card.png (1200x630) — the preview a stranger sees in a
chat app before they ever open the page. Deterministic and dependency-light:
same fonts in, same image out.

    python tools/make_share_card.py /path/to/mono.ttf /path/to/mono-bold.ttf \
                                    /path/to/ugaritic.ttf

Fonts are optional; anything missing falls back to DejaVu, except the glyph
line, which needs a Ugaritic face or it draws as boxes. That fallback is
reported out loud instead of being hidden.
"""
import pathlib, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "share-card.png"

W, H = 1200, 630
BG, PANEL, BORDER = "#090c10", "#0d1117", "#30363d"
TEXT, MUTED, BLUE, GREEN, AMBER = "#e6edf3", "#8b949e", "#58a6ff", "#3fb950", "#d29922"
GLYPHS = "\U0001039a\U00010396\U0001039a\U0001038e\U00010386\U0001039a\U0001038b\U00010390"

FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FALLBACK_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def pick(fonts, keyword, fallback):
    """First supplied font whose filename contains keyword, else a fallback."""
    for path in fonts:
        if keyword in path.name.lower():
            return str(path)
    return fallback


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(FALLBACK, size)


def main(argv):
    supplied = [pathlib.Path(a) for a in argv[1:]]
    mono = pick(supplied, "mono", FALLBACK)
    bold = pick(supplied, "bold", FALLBACK_BOLD)
    ugaritic = pick(supplied, "ugaritic", "")
    if not ugaritic:
        print("warning: no Ugaritic font supplied; the glyph line will render as boxes",
              file=sys.stderr)

    f_badge = font(bold, 20)
    f_h1 = font(bold, 54)
    f_body = font(mono, 24)
    f_small = font(mono, 20)
    f_note = font(mono, 22)
    f_glyph = font(font and (ugaritic or mono), 48)

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([48, 48, W - 48, H - 48], radius=18, fill=PANEL, outline=BORDER, width=2)
    d.rectangle([48, 48, W - 48, 58], fill=BLUE)

    d.text((84, 90), "SIDE A // SHOWTIME", font=f_badge, fill=BLUE)
    right = "a postcard that shows its work"
    d.text((W - 84 - d.textlength(right, font=f_badge), 90), right, font=f_badge, fill=MUTED)

    d.text((84, 136), "SHOWTIME //", font=f_h1, fill=TEXT)
    d.text((84, 200), "BACKSTAGE", font=f_h1, fill=TEXT)

    d.text((84, 288), "Eight languages. One glyph line nobody can verify.", font=f_body, fill=TEXT)
    d.text((84, 324), "No formal computer training. No budget. Free-tier models,", font=f_body, fill=MUTED)
    d.text((84, 356), "steered by hand, then checked.", font=f_body, fill=MUTED)

    d.text((84, 414), GLYPHS, font=f_glyph, fill=GREEN)
    glyph_w = d.textlength(GLYPHS, font=f_glyph)
    d.text((84 + glyph_w + 24, 432), "<- embedded font, draws anywhere", font=f_small, fill=AMBER)

    box = [84, 486, W - 84, H - 84]
    d.rounded_rectangle(box, radius=12, outline=BORDER, width=1)

    line = "click / Enter / Space   -   Esc flips back"
    avail = box[2] - box[0] - 56
    size = 22
    while size > 12 and d.textlength(line, font=font(mono, size)) > avail:
        size -= 1
    f_line = font(mono, size)
    l, t, r, b = d.textbbox((0, 0), line, font=f_line)
    # centre the line inside the box, then refuse to draw if it still overflows
    y = box[1] + ((box[3] - box[1]) - (b - t)) // 2 - t
    if y + b > box[3] - 8 or y < box[1] + 8:
        raise SystemExit(f"footer line does not fit the box: y={y}..{y + b}, box={box}")
    d.text((box[0] + 28, y), line, font=f_line, fill=TEXT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main(sys.argv)
