#!/usr/bin/env python3 -I
"""usage: replay_compare.py <A.replay.jsonl> <B.replay.jsonl> <article_diff.json> <out.json>   (G4 of WIKIVOYAGE-REBUILD-criterion.md)"""
import sys, json
rd = lambda f: {r["id"]: r for r in (json.loads(l) for l in open(f) if l.strip())}
A, B = rd(sys.argv[1]), rd(sys.argv[2]); d = json.load(open(sys.argv[3]))
changed = set(d["changed_titles"]); holeA = set(d["A_titles_with_hole_chunk"])
isv = lambda e: "wikivoyage" in (e.get("source") or "").lower()
key = lambda e: ((e.get("source") or "").split(" — ")[0], e["title"])
assert set(A) == set(B), "different item sets"
n = len(A); ident = 0; ordered = 0; setdiff = 0; unexplained = []; explained = 0; no_voy_ident = 0; no_voy = 0
hole_items = 0; hole_items_changed = 0; rows = []
for i in sorted(A):
    la, lb = [key(e) for e in A[i]["raw"]], [key(e) for e in B[i]["raw"]]
    bare = lambda t: t.split(": ", 1)[1] if t.startswith("Wikivoyage: ") else t  # raw titles carry the library prefix
    va = [bare(e["title"]) for e in A[i]["raw"] if isv(e)]; vb = [bare(e["title"]) for e in B[i]["raw"] if isv(e)]
    touched = any(t in changed for t in va + vb)
    hole = any(t in holeA for t in va)
    same = la == lb
    if hole:
        hole_items += 1; hole_items_changed += (not same)
    if same: ident += 1
    else:
        if set(la) == set(lb): ordered += 1
        else: setdiff += 1
        if touched: explained += 1
        else: unexplained.append(i)
    if not va and not vb:
        no_voy += 1; no_voy_ident += same
    rows.append({"id": i, "same": same, "touched": touched, "hole_in_A": hole, "voy_A": va, "voy_B": vb})
res = {"items": n, "identical": ident, "differs": n - ident, "order_only": ordered, "set_differs": setdiff,
       "differs_explained": explained, "unexplained": unexplained, "items_no_wikivoyage_in_A_or_B": no_voy,
       "no_wikivoyage_identical": no_voy_ident, "items_A_wikivoyage_article_with_hole": hole_items,
       "of_those_changed": hole_items_changed, "G4_pass": (not unexplained)}
json.dump({"summary": res, "rows": rows}, open(sys.argv[4], "w"), ensure_ascii=False, indent=1)
print(json.dumps(res))
