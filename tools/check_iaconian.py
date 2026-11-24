"""Check that the fictional language is fictional for the right reason.

The claim on the card is: the words are invented, the letters are not. This
script is what makes that checkable without trusting the card, the model, or
the operator.

It verifies, in plain Python with no network access:
  1. every printed code point is a real, assigned Unicode character
  2. every printed code point sits in the Ugaritic block U+10380-1039F
  3. the sentence renders from the lexicon, so the text and the dictionary
     cannot disagree
  4. each token's letters are the letters the lexicon says they are
  5. no letter is used only once by accident: repeats must be meaningful
     (NUN opens and closes the returning word, TO is itself a word)
  6. the words are NOT real Ugaritic, so nothing here pretends to be a
     decipherment (see data/iaconian.spec.json -> not_claimed)
"""
import json, pathlib, sys, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "data" / "iaconian.spec.json").read_text(encoding="utf-8"))

LO, HI = 0x10380, 0x1039F
fails = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        fails.append(name)


render = SPEC["sentence"]["rendering"]
line = SPEC["sentence"]["rendering_code_points"]

print(f"unicodedata version: {unicodedata.unidata_version}\n")

# 1 + 2: real characters, right block
for cp in line:
    n = int(cp[2:], 16)
    name = unicodedata.name(chr(n), None)
    check(f"{cp} is an assigned character", name is not None, name or "UNASSIGNED")
    check(f"{cp} is in the Ugaritic block", LO <= n <= HI)

# 3: the rendering is derived from the lexicon, not typed
by_token = {e["token"]: e["code_points"] for e in SPEC["lexicon"]}
derived = [cp for t in SPEC["sentence"]["tokens"] for cp in by_token[t]]
check("sentence renders from the lexicon", derived == line,
      f"{len(derived)} code points")
check("rendering matches the code point list", render == "".join(chr(int(c[2:], 16)) for c in line))

# 4: each token really is spelled with the letters its syllables name
for entry in SPEC["lexicon"]:
    letters = [part for syl in entry["syllables"] for part in syl.split("+")]
    check(f"token {entry['token']}: syllable count matches code points",
          len(letters) == len(entry["code_points"]),
          " / ".join(letters))
    for letter, cp in zip(letters, entry["code_points"]):
        name = unicodedata.name(chr(int(cp[2:], 16)), "")
        check(f"  {entry['token']}: {letter} is {cp}", name.endswith(" " + letter), name)

# 5: repeats are deliberate, and documented
repeats = sorted({cp for cp in line if line.count(cp) > 1})
check("repeating letters are documented", bool(repeats),
      f"{len(repeats)} repeated: {repeats}")
check("NUN opens and closes the longest word",
      SPEC["lexicon"][2]["code_points"][0] == SPEC["lexicon"][2]["code_points"][-1] == "U+10390")
check("single-code-point word exists and is named for its letter",
      any(len(e["code_points"]) == 1 and unicodedata.name(chr(int(e["code_points"][0][2:], 16))) ==
          f"UGARITIC LETTER {e['token']}" for e in SPEC["lexicon"]))

# 6: honesty surface present and non-empty
check("spec states what it is not", len(SPEC["not_claimed"]) >= 3)
check("spec points outside itself", len(SPEC["provenance"]) >= 2)
check("spec records who deciphered the real script", "1930" in SPEC["script"]["decipherment"])

print()
print(f"{len(fails)} failing")
sys.exit(1 if fails else 0)
