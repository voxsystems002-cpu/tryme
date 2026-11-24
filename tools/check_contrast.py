"""Contrast check: every text colour the card uses, measured against the
surface it actually sits on. Plain Python, no packages, no API key."""
import re, sys

def lum(h):
    h = h.lstrip('#')
    ch = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    ch = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126*ch[0] + 0.7152*ch[1] + 0.0722*ch[2]

def ratio(a, b):
    hi, lo = sorted([lum(a), lum(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)

# (label, text colour, background it renders on, minimum allowed by WCAG AA)
PAIRS = [
    ("hint + footer text",  "#8b949e", "#0d1117", 4.5),
    ("back JSON body",      "#c9d1d9", "#11161f", 4.5),
    ("front body text",     "#e6edf3", "#0d1117", 4.5),
    ("SIDE A badge (blue)", "#58a6ff", "#0d1117", 4.5),
    ("SIDE B badge (green)","#3fb950", "#11161f", 4.5),
    # surfaces added with the language section
    ("glyph note (amber)",  "#d29922", "#0d1117", 4.5),
    ("disclaimer bold",     "#d29922", "#11161f", 4.5),
    ("lexicon term/glyph",  "#3fb950", "#11161f", 4.5),
    ("provenance link",     "#58a6ff", "#11161f", 4.5),
    ("code point label",    "#8b949e", "#11161f", 4.5),
    ("lexicon gloss",       "#c9d1d9", "#11161f", 4.5),
]

if __name__ == "__main__":
    bad = 0
    print(f"{'surface':<22}{'ratio':>8}{'need':>7}  verdict")
    print("-" * 50)
    for label, fg, bg, need in PAIRS:
        r = ratio(fg, bg)
        ok = r >= need
        bad += not ok
        print(f"{label:<22}{r:>7.2f}{need:>7.1f}  {'PASS' if ok else 'FAIL'}")
    print("-" * 50)
    print(f"{len(PAIRS)} pairs checked, {bad} failing")
    sys.exit(1 if bad else 0)
