"""Structural check for index.html. No packages, no browser, no API key.

It answers four questions every time you edit the card:
  1. Is the JSON on the back the SAME data as the JSON in the head?
     (they are two copies by design, so they must be compared, not trusted)
  2. Is every glyph character the front prints present in the embedded font?
  3. Is the accessible state wired up, not just the visual state?
  4. Does the page avoid depending on a network fetch to render?
"""
import json, re, sys, pathlib, base64, io, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
fails, notes = [], []

def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        fails.append(name)

# 1. head JSON vs back-face JSON -------------------------------------------
head = re.search(r'<script type="application/json" id="postcard-data">(.*?)</script>',
                 HTML, re.S)
back = re.search(r'<pre id="back-json">(.*?)</pre>', HTML, re.S)
check("head JSON block exists", bool(head))
check("back JSON block exists", bool(back))
if head and back:
    a = json.loads(head.group(1))
    b = json.loads(back.group(1))
    check("back face matches head data", a == b)
    data_file = ROOT / "data" / "emergent_bit.json"
    check("data/emergent_bit.json matches head data",
          json.loads(data_file.read_text(encoding="utf-8")) == a,
          "three copies of the packet: head, back face, data file")
    check("packet_version present", "packet_version" in a, a.get("packet_version", "?"))

# 2. cuneiform coverage ----------------------------------------------------
font_b64 = re.search(r'url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)', HTML)
check("glyph font embedded inline", bool(font_b64),
      "no data: URI, so a missing system font would show empty boxes")
glyphs = set(re.findall(r'[\U00010380-\U0001039F]', HTML))
if glyphs:
    try:
        from fontTools.ttLib import TTFont
        tt = TTFont(io.BytesIO(base64.b64decode(font_b64.group(1))))
        covered = {chr(cp) for cp in tt.getBestCmap()}   # cmap keys are ints
        missing = sorted(ord(c) for c in glyphs - covered)
        check("every glyph has a shape in the font", not missing,
              f"{len(glyphs)} used, missing {[hex(c) for c in missing]}")
    except ImportError:
        notes.append("fontTools not installed — glyph coverage skipped")

# 3. accessibility state ---------------------------------------------------
check("card exposes aria-expanded", 'aria-expanded="false"' in HTML)
check("hidden face removed from a11y tree", 'aria-hidden="true"' in HTML)
check("Escape returns to front", "Escape" in HTML)
check("reduced motion honoured", "prefers-reduced-motion" in HTML)

# 4. no network dependency -------------------------------------------------
check("no external stylesheet/font/script", not re.search(r'(src|href)="https?://', HTML))
check("no runtime fetch()", "fetch(" not in HTML)

# 5. share preview ---------------------------------------------------------
for tag in ("og:title", "og:description", "og:image", "og:type"):
    check(f"{tag} tag", f'property="{tag}"' in HTML)
check("og:image is absolutised or relative-ok",
      bool(re.search(r'property="og:image" content="[^"]+"', HTML)))

print()
for n in notes:
    print("note:", n)
print(f"{len(fails)} failing")
sys.exit(1 if fails else 0)
