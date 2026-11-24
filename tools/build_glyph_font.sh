#!/usr/bin/env bash
# Regenerate assets/glyphs.woff2 — the bytes the card prints the glyph line with.
#
# Two rules, both learned the hard way:
#   1. The codepoints in assets/glyph-line.txt are U+10380-1039F, which is the
#      UGARITIC block. Noto Sans Cuneiform does not cover them and renders blank.
#   2. Subset, don't ship the whole font. The line is 8 characters; the subset
#      is ~1 KB, the full font is ~460 KB.
#
# Needs: npm (to fetch the font), fonttools + brotli (pip install fonttools brotli)
set -euo pipefail
cd "$(dirname "$0")/.."

FONT_PKG="@fontsource/noto-sans-ugaritic"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

( cd "$TMP" && npm pack --silent "$FONT_PKG" >/dev/null && tar xzf ./*.tgz )
SRC="$TMP/package/files/noto-sans-ugaritic-ugaritic-400-normal.woff2"

pyftsubset "$SRC" \
  --text-file=assets/glyph-line.txt \
  --flavor=woff2 \
  --layout-features='' \
  --no-hinting \
  --output-file=assets/glyphs.woff2

echo "wrote assets/glyphs.woff2 ($(wc -c < assets/glyphs.woff2) bytes)"
echo "next: tools/inline_glyph_font.py  (re-embeds it into index.html)"
