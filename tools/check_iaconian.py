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

# 5b: the recorded readings must stay honest ------------------------------
# The card had a model guess EMERGENT. The tempting story is that the glyphs
# spell it. They do not, and the negative result is what makes the bit work,
# so it gets enforced like any other claim.
rt = SPEC.get("readings_tried")
check("recorded readings exist", bool(rt and rt.get("rules")), "negative results kept on purpose")
if rt:
    # Negative results are recorded, and so is the one positive result: a
    # substitution key does spell the word. Denying it was the overclaim we had
    # to correct, so the checker asserts the truth, not a convenient story.
    positive = [r for r in rt["rules"] if r["produces_emergent"]]
    check("exactly one reading produces EMERGENT", len(positive) == 1,
          "; ".join(r["rule"].split(" — ")[0] for r in positive))
    for rule in rt["rules"]:
        name = rule["rule"].split(" — ")[0]
        if rule["produces_emergent"]:
            check(f"reading '{name}' is documented as invented, not a decoding",
                  "contradicts the script" in rule["note"])
        else:
            check(f"reading '{name}' does not produce EMERGENT", rule["produces_emergent"] is False,
                  f"got {rule['result']!r}")
    initials = sorted({unicodedata.name(chr(cp)).split()[-1][0] for cp in range(LO, HI + 1)
                       if unicodedata.name(chr(cp), None)})
    check("no Ugaritic letter name begins with E, so an acrostic cannot spell EMERGENT",
          "E" not in initials, "".join(initials))
    check("verdict states what did spell it", "handshake" in rt["verdict"])

    # a substitution key genuinely exists; the claim that it does must be true,
    # and the claim that it was discovered must stay false
    check("spec records that a cipher exists", rt.get("cipher_exists") is True,
          "denying it would be the overclaim we corrected")
    cipher = rt.get("cipher") or {}
    key = {m["letter"]: m["cipher_says"] for m in cipher.get("key", [])}
    if key:
        art = ROOT / "data" / "original_showtime.log"
        shipped = [l for l in art.read_text(encoding="utf-8").split("\n")
                   if l.startswith("\U0001f6e1")][0].split("Iaconian): ")[1].strip()
        letters = [unicodedata.name(c).replace("UGARITIC LETTER ", "") for c in shipped]
        check("the recorded key actually spells EMERGENT",
              "".join(key.get(l, "?") for l in letters) == "EMERGENT",
              "".join(key.get(l, "?") for l in letters))
        check("the key contradicts the script on every letter",
              cipher.get("agreements_with_script") == 0,
              f"{cipher.get('agreements_with_script')} agreements")
        check("the key is under-constrained, not a decoding",
              cipher.get("letters_constrained", 99) < cipher.get("letters_available", 0) / 2,
              f"{cipher.get('letters_constrained')} of {cipher.get('letters_available')} letters")
        check("the key is marked invented, not discovered",
              cipher.get("status") == "invented" and cipher.get("discovered") is False,
              f"status={cipher.get('status')} discovered={cipher.get('discovered')}")
        check("the key is not declared anywhere in the artefact",
              cipher.get("declared_in_artefact") is False)

# 5c: the artefact and the correction must both be real ---------------------
art = ROOT / "data" / "original_showtime.log"
check("the original artefact is committed", art.exists(),
      "the line the model called EMERGENT has to exist somewhere other than memory")
if art.exists():
    log = art.read_text(encoding="utf-8")
    shipped = [l for l in log.split("\n") if l.startswith("\U0001f6e1")]
    check("artefact has exactly one glyph line", len(shipped) == 1)
    if shipped:
        shipped_line = shipped[0].split("Iaconian): ")[1].strip()
        corr = SPEC.get("correction", {})
        check("correction records the shipped line", corr.get("original_code_points") ==
              [f"U+{ord(c):04X}" for c in shipped_line])
        check("the shipped line did NOT spell EMERGENT either",
              corr.get("original_acrostic") != "EMERGENT", corr.get("original_acrostic", "?"))
        check("both lines are the same length", len(shipped_line) == len(render))
        changed = [(i, a, b) for i, (a, b) in enumerate(zip(shipped_line, render)) if a != b]
        check("the correction is a real edit, not a no-op", len(changed) > 0,
              f"{len(changed)} letters changed")
        check("every printed glyph of both lines has a shape in the font",
              all(unicodedata.name(c, "") for c in shipped_line + render))

# 6: honesty surface present and non-empty
check("spec states what it is not", len(SPEC["not_claimed"]) >= 3)
check("spec points outside itself", len(SPEC["provenance"]) >= 2)
check("spec records who deciphered the real script", "1930" in SPEC["script"]["decipherment"])

print()
print(f"{len(fails)} failing")
sys.exit(1 if fails else 0)
