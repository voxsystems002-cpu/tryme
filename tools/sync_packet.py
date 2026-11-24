"""Single source of truth: data/emergent_bit.json.

Writes that packet into index.html twice:
  - the <script id="postcard-data"> block in <head>
  - the <pre id="back-json"> fallback on the back face (what a no-JS visitor sees)

Run this after editing the data file, then run tools/check_card.py, which fails
loudly if the three copies ever disagree again.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
data_path = ROOT / "data" / "emergent_bit.json"
html_path = ROOT / "index.html"

packet = json.loads(data_path.read_text(encoding="utf-8"))
pretty = json.dumps(packet, indent=2, ensure_ascii=False)
html = html_path.read_text(encoding="utf-8")

# 1. head block
head_open = '<script type="application/json" id="postcard-data">'
i = html.index(head_open) + len(head_open)
j = html.index("</script>", i)
# keep the newline that follows the opening tag
if html[i] == "\n":
    i += 1
    j = html.rindex("\n", i, j + 1)
    replacement = pretty
else:
    replacement = pretty
html = html[:i] + replacement + html[j:]

# 2. static fallback inside the back face
m = re.search(r'(<pre id="back-json">)(.*?)(</pre>)', html, re.S)
if not m:
    sys.exit("could not find <pre id=\"back-json\">")
html = html[:m.start(2)] + pretty + html[m.end(2):]

html_path.write_text(html, encoding="utf-8")
print(f"packet v{packet['packet_version']} written to both copies in index.html")
