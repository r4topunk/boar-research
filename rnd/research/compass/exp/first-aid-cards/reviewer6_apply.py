"""Apply the round-6 Opus reviewer (REVIEWER-DECISIONS-6, opus-reviewer-2, 2026-10-03) inside build_cards.py:
round-6 cards (CPR adult/child/infant, poisoning) from round6.build + reviewer6.CARDS edits; licence edits (reviewer6.LIC) on the
already-reviewed scorpion / scorpionadult / marinepuncture cards; 13 new source rows (reviewer6.NEW_ROWS, verified against
snapshots-rev6/ and snapshots-6/); the 6 MedlinePlus rows removed (reviewer6.REMOVED: its terms forbid automated/AI use).
Unlike reviewer6.apply(), this applies the reviewer's CITES too ('(ES + X)' adds X in ES, '(ES: Y)' uses Y in ES)."""
import copy, importlib.util, re, sys
from pathlib import Path
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H))
_s = importlib.util.spec_from_file_location("reviewer6", H / "reviewer6.py"); R6 = importlib.util.module_from_spec(_s); _s.loader.exec_module(R6)
ID = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Za-z0-9]+)+")

def cites_for(spec, lang):
    main = ID.findall(re.sub(r"\([^)]*\)", "", spec))
    for note in re.findall(r"\(([^)]*)\)", spec):
        m = re.match(r"\s*ES\s*\+\s*(.*)", note)
        if m and lang == "es": main = main + ID.findall(m.group(1))
        m = re.match(r"\s*ES:\s*(.*)", note)
        if m and lang == "es": main = ID.findall(m.group(1))
    return main

def apply_edits(card, edits):
    c = copy.deepcopy(card)
    for e in edits:
        w = e["where"]
        if w.startswith("alt_steps"):
            c["alt_steps"] = {lg: [{"text": e[lg], "cites": cites_for(e["cites"], lg)}] for lg in ("en", "pt", "es")}
            continue
        langs = ["es"] if "ES only" in w else ["en", "pt", "es"]
        m = re.match(r"step (\d+)", w)
        for lg in langs:
            tgt = c["langs"][lg]["steps"][int(m.group(1)) - 1] if m else c["langs"][lg]["call"] if w.startswith("call") else None
            if tgt is None: raise SystemExit(f"unknown edit: {c['id']} {w}")
            if "cites only" not in w and not e[lg].startswith("(unchanged"): tgt["text"] = e[lg]
            tgt["cites"] = cites_for(e["cites"], lg)
    c["review"] = {"by": R6.REV, "date": R6.DATE}
    return c

def apply_round6(cards, S):
    """cards: the already-reviewed rounds 1–5 list; S: the source dict (id -> (org, url, quote, flag)). Mutates S."""
    assert not R6.verify_rows(), "reviewer-6 source row not found in its snapshot"
    S.update(R6.round6.S6)
    S.update({k: (v[0], v[1], v[2], v[4]) for k, v in R6.NEW_ROWS.items()})
    for k in R6.REMOVED: S.pop(k, None)
    by = {c["id"]: c for c in cards}
    for k, edits in R6.LIC.items(): by[k] = apply_edits(by[k], edits)
    st = lambda t, *c: {"text": t, "cites": list(c)}; L = lambda t, s, c: {"title": t, "steps": s, "call": c}
    new = [apply_edits(dict(c, round=6), R6.CARDS[c["id"]][2]) for c in R6.round6.build(st, L)]
    return [by[c["id"]] for c in cards] + new
