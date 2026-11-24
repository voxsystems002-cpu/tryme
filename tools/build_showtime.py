"""Regenerate the front face's showtime block from data/original_showtime.log.

The committed log is the artifact: the version where the mistake was made. The
page must not paraphrase it, or the thing on trial stops being the real thing.
So the front is generated from that file, with exactly one substitution: the
Iaconian line, which is marked as corrected.

Run after editing the log, then tools/check_card.py proves they still agree.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "data" / "original_showtime.log"
HTML = ROOT / "index.html"

log = LOG.read_text(encoding="utf-8")
lines = log.split("\n")

# --- pull the pieces out of the artifact
title = next(l for l in lines if l.startswith("SHOWTIME"))
command = next(l for l in lines if l.startswith("COMMAND:"))
target = next(l for l in lines if l.startswith("TARGET:"))
# a flag is a PAIR of regional indicators (two code points), and the shield line
# carries a variation selector, so identify handshake lines by structure
RI = range(0x1F1E6, 0x1F1FF + 1)
handshake = [
    l for l in lines
    if " * " in l and (ord(l[0]) in RI and ord(l[1]) in RI or l.startswith("\U0001f6e1"))
]
if len(handshake) != 9:
    sys.exit(f"expected 8 language lines + 1 glyph line, found {len(handshake)}")

langs, glyph_orig = handshake[:-1], handshake[-1]
orig_line = glyph_orig.split("Iaconian): ")[1].strip()
# --- the corrected line comes from the spec, never typed
import json
spec = json.loads((ROOT / "data" / "iaconian.spec.json").read_text(encoding="utf-8"))
corrected = spec["sentence"]["rendering"]
assert corrected != orig_line, "correction is a no-op; nothing to show"

LANG_TAG = {
    "\U0001F1EA\U0001F1F8": "es", "\U0001F1E8\U0001F1F3": "zh-Hans",
    "\U0001F1EE\U0001F1F3": "hi", "\U0001F1F8\U0001F1E6": "ar",
    "\U0001F1EB\U0001F1F7": "fr", "\U0001F1E9\U0001F1EA": "de",
    "\U0001F1EF\U0001F1F5": "ja", "\U0001F1F9\U0001F1FF": "sw",
}
ISO = {
    "\U0001F1EA\U0001F1F8": "ES", "\U0001F1E8\U0001F1F3": "CN",
    "\U0001F1EE\U0001F1F3": "IN", "\U0001F1F8\U0001F1E6": "SA",
    "\U0001F1EB\U0001F1F7": "FR", "\U0001F1E9\U0001F1EA": "DE",
    "\U0001F1EF\U0001F1F5": "JP", "\U0001F1F9\U0001F1FF": "TZ",
}

flags = [l.split(" * ", 1)[0] for l in langs]
unmapped = [f for f in flags if f not in ISO or f not in LANG_TAG]
if unmapped:
    raise SystemExit(f"unmapped flags in the log: {unmapped}")

rows = []
for l in langs:
    flag, text = l.split(" * ", 1)
    rows.append(
        f'            <li class="row"><span class="lang">{ISO[flag]}</span>'
        f'<span class="flag" aria-hidden="true">{flag}</span>'
        f'<span class="line" lang="{LANG_TAG[flag]}">{text}</span></li>'
    )

block = f'''        <div class="log">
          <div class="meta">================================================================</div>
          <div><span class="meta">[LOG: NANO RUNTIME PATCH]</span></div>
          <div><span class="meta">COMMAND:</span> {command.replace("COMMAND: ", "")}</div>
          <div><span class="meta">TARGET:</span> {target.replace("TARGET: ", "")}</div>
          <div class="meta">================================================================</div>
          <ul class="langs">
{chr(10).join(rows)}
          </ul>
          <div class="row row-glyph">
            <span class="lang">CY</span>
            <div>
              <div class="glyphs" lang="mul" aria-label="Iaconian: TO QO NEMTUN, written in Ugaritic letters">{corrected}</div>
              <div class="glyph-translit">to &nbsp;·&nbsp; qo &nbsp;·&nbsp; nemtun</div>
              <div class="glyph-note"><span class="tag-corrected">CORRECTED</span> the original line was
                {orig_line} — kept verbatim in <code>data/original_showtime.log</code> and put on trial on the
                back. The letters are Ugaritic (U+10380–U+1039F, Unicode since 2006); the words are invented.</div>
            </div>
          </div>
          <div class="meta">================================================================</div>
        </div>
'''

html = HTML.read_text(encoding="utf-8")
start = html.index('        <div class="log">')
end = html.index('        <h3>What the line actually says</h3>')
HTML.write_text(html[:start] + block + "\n" + html[end:], encoding="utf-8")
print(f"front rebuilt from the artifact: 8 lines, original glyph line {orig_line!r}")
