"""Put assets/glyphs.woff2 into index.html as a data URI, so the page is one file
and the glyph line can never depend on the visitor's fonts."""
import base64, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
font = (ROOT / "assets/glyphs.woff2").read_bytes()
b64 = base64.b64encode(font).decode()
html_path = ROOT / "index.html"
html = html_path.read_text(encoding="utf-8")

new, n = re.subn(r"url\(data:font/woff2;base64,[A-Za-z0-9+/=]+\)",
                 f"url(data:font/woff2;base64,{b64})", html, count=1)
if n != 1:
    sys.exit("could not find the embedded font in index.html")
html_path.write_text(new, encoding="utf-8")
print(f"inlined {len(font)} bytes -> {len(b64)} base64 chars")
