# tryme
see above

---

## What this is

A single page (`index.html`) that opens as a postcard and flips to the working
notes behind it. Front: eight handshake lines and one glyph line nobody can
verify. Back: the receipts — what was claimed, and the file that enforces it.

Made with free-tier AI models, plain-language steering, and no formal computer
training. Nothing here is a credential. The checks below are the argument.

## The checks (the part that is actually verifiable)

```bash
python3 tools/check_contrast.py      # 5 text/surface pairs, WCAG AA floor 4.5:1
python3 tools/check_card.py          # data drift, glyph coverage, a11y state, share tags
```

`check_card.py` needs `fonttools` for the glyph-coverage test
(`pip install fonttools brotli`); everything else is the standard library.
CI runs both on every push — see `.github/workflows/check.yml`.

Why they exist, in order of embarrassment:

1. **The glyph line was drawing nothing.** The characters are U+10380–1039F,
   which is the *Ugaritic* block. The first embedded font was Noto Sans
   **Cuneiform**, which has zero coverage there, so the "Iaconian" line was
   blank on every machine — including the ones it was supposed to fix.
   `check_card.py` now fails if any printed glyph is missing from the font.
2. **Two copies of the packet drifted.** The head JSON and the back face were
   separate hand-written blocks. The back is now printed from the head at load,
   and the checker compares both.
3. **The flip was decoration only.** `aria-expanded` toggles, the hidden face is
   `aria-hidden`, Enter/Space flip, Escape returns, and with
   `prefers-reduced-motion` the faces simply swap instead of rotating.

## Regenerating the glyph font

```bash
tools/build_glyph_font.sh      # subsets Noto Sans Ugaritic to just this line
python3 tools/inline_glyph_font.py   # re-embeds it into index.html
```

## Regenerating the share image

```bash
python3 tools/make_share_card.py <mono.ttf> <mono-bold.ttf> <ugaritic.ttf>
```

Needs Pillow. Output is `assets/share-card.png`, 1200×630, used by the Open
Graph tags. If no Ugaritic font is passed it warns instead of drawing boxes.

## If you share it

The `og:image` tag points at `assets/share-card.png`, a **relative** path.
Scrapers need an absolute URL. Once the page has a home, change the three
`og:image` / `twitter:image` tags to
`https://your-domain/assets/share-card.png`.
