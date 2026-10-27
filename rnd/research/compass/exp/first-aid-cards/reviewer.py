"""Apply the independent Opus reviewer's card edits (REVIEWER-DECISIONS.json, 2026-10-03) on top of rounds 1-5.
Edit kinds: 'step N (replace)', 'step N (ES only)', 'call (replace|PT only|ES only)', 'title (replace|ES only)',
'new step after N', 'new step N (insert at top)', 'old step N (replace; now step N)', 'old step N (remove)'.
Positions always refer to the ORIGINAL (pre-review) numbering. Cites: the leading ids of each comma-separated piece;
'(+ … row)' notes are source additions, listed in NOTES and covered by reviewer_sources.py.
Status after this step: reviewed-by-opus-reviewer."""
import copy, json, re
from pathlib import Path
H = Path(__file__).resolve().parent
R = json.load(open(H / "REVIEWER-DECISIONS.json"))
NOTES = []
ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Za-z0-9†]+)*")

def parse_cites(s, card, where):
    if not s: return None
    out = []
    for piece in re.split(r",\s*", re.sub(r"\([^)]*\)", lambda m: (NOTES.append((card, where, m.group(0))) or ""), s)):
        m = ID.match(piece.strip())
        if m: out.append(m.group(0))
    return out or None

def apply_reviewer(cards, extra=None):
    extra = extra or {}
    by_id = {c["id"]: c for c in cards}
    applied = []
    for cid, dec in R["cards"].items():
        c = by_id[cid]
        langs = c["langs"]
        orig = {L: list(langs[L]["steps"]) for L in langs}
        new = {L: [copy.deepcopy(s) for s in orig[L]] for L in langs}  # index = original position
        removed = set(); inserts = []  # (after_index or -1, edit)
        for e in dec.get("edits", []):
            w = e["where"]; only = "pt" if "PT only" in w else "es" if "ES only" in w else None
            targets = [only] if only else [L for L in ("en", "pt", "es") if L in e]
            cites = parse_cites(e.get("cites"), cid, w)
            if (cid, w) in extra: cites = (cites or []) + [x for x in extra[(cid, w)] if x not in (cites or [])]
            m = re.match(r"(?:old )?step (\d+)", w)
            if w.startswith("call"):
                for L in targets:
                    langs[L]["call"] = {"text": e[L], "cites": cites or langs[L]["call"]["cites"]}
            elif w.startswith("title"):
                for L in targets: langs[L]["title"] = e[L]
            elif "remove" in w and m:
                removed.add(int(m.group(1)) - 1)
            elif w.startswith("new step") and "insert at top" in w:
                inserts.append((-1, e, cites))
            elif w.startswith("new step after"):
                inserts.append((int(re.search(r"after (\d+)", w).group(1)) - 1, e, cites))
            elif m:
                i = int(m.group(1)) - 1
                for L in targets:
                    new[L][i] = {"text": e[L], "cites": cites or new[L][i]["cites"]}
            else:
                raise SystemExit(f"unknown edit kind: {cid}: {w}")
            applied.append((cid, w))
        for L in langs:
            seq = []
            for pos, e, cites in [x for x in inserts if x[0] == -1]:
                if L in e: seq.append({"text": e[L], "cites": cites})
            for i, s in enumerate(new[L]):
                if i not in removed: seq.append(s)
                for pos, e, cites in [x for x in inserts if x[0] == i]:
                    if L in e: seq.append({"text": e[L], "cites": cites})
            langs[L]["steps"] = seq
        c["review"] = {"by": "opus-reviewer", "date": R["date"], "choice": dec["choice"], "note": dec["note"]}
    return cards, applied
