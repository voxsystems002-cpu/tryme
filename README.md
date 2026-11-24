# tryme
see above

---

## What this is

A single page (`index.html`) that opens as a postcard and flips to the working
notes behind it. Front: eight handshake lines and one glyph line nobody can
verify. Back: the receipts — what was claimed, and the file that enforces it.

Made with free-tier AI models, plain-language steering, and no formal computer
training. Nothing here is a credential. The checks below are the argument.

## The language: fictional, but anchored

The glyph line is **Iaconian**: three invented words, written in **Ugaritic** —
a real script excavated at Ras Shamra, deciphered in 1931, and encoded by
Unicode in 2006 at `U+10380–U+1039F`.

| romanised | letters (Unicode) | means |
|---|---|---|
| `to` | U+1039A `UGARITIC LETTER TO` | the hold — what is kept fixed |
| `qo` | U+10396 QOPA + U+10386 WO | a path walked before |
| `nemtun` | U+10390 NUN · U+1038E MEM · U+1039A TO · U+1039C U · U+10390 NUN | to carry a thing back where it was found |

The sentence reads *"the hold, the walked path, carry it back."*

The point of the design: **the words cannot be verified and the letters can.**
You can open the Unicode chart and confirm every character. You cannot look up
`nemtun` anywhere, because it was invented today, and
`data/iaconian.spec.json` says so in a `not_claimed` block instead of hiding it.
That is the grounding — the fiction is tied to something that exists outside
this repository.

Full spec: `data/iaconian.spec.json` (lexicon, grammar, anchors, provenance).
Named anchor letters: NUN opens and closes `nemtun` because it means returning;
`to` is one letter that is also a whole word, because a hold is a thing that
stays put. Both are checked, not asserted.

## The checks (the part that is actually verifiable)

```bash
python3 tools/check_iaconian.py      # every letter is a real character, in the real block
python3 tools/check_contrast.py      # 11 text/surface pairs, WCAG AA floor 4.5:1
python3 tools/check_card.py          # drift, glyph coverage, a11y state, share tags
node tools/test_flip.js              # every flip path + the aria state it leaves behind
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
