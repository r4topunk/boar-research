#!/usr/bin/env python3
"""Map an engine-displayed title (+ source string) to the A-union pack(s) holding it. 0 LLM, packs opened read-only."""
import sqlite3, os, re
R = os.environ.get("AUNION", "<workspace>/shared-data/packs/persona-a-union")
PACKS = ["boar-crypto", "boar-wikivoyage-en", "boar-visa-en", "boar-medlineplus-en", "boar-firstaid-en", "boar-factbook"]
EXTRA = {}
_T = {}
def titles(p):
    if p not in _T:
        f = EXTRA.get(p, os.path.join(R, p + ".sqlite"))
        db = sqlite3.connect(f"file:{f}?mode=ro", uri=True)
        _T[p] = {r[0].lower() for r in db.execute("select title from articles")}
    return _T[p]
def packs_of(title, packs=PACKS):
    t = title.lower(); cands = [t]
    m = re.match(r"^[^:]{2,20}: (.+)$", title)
    if m: cands.append(m.group(1).lower())
    return [p for p in packs if any(c in titles(p) for c in cands)]
