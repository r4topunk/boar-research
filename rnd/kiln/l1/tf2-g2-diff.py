# G2 diff (tf2-criterion.md): route + pre-generation reason codes + retrieval context, cut 2 vs tf2, same requests/seed.
import json, re, sys
PRE = ("route-gate", "task", "retrieve", "detector", "instant", "places", "near", "diet", "context", "travel", "offer-deep", "answer")
def load(p): return {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
def route(t):
    r = t["route"]; codes = [c for c in r["reasonCodes"] if c.split(":")[0] in PRE]
    return (r.get("task"), r.get("tier"), r.get("outcome"), tuple(codes))
def ctx(t):
    rv = t.get("retrieval") or {}
    f = lambda xs: tuple((x.get("title"), x.get("section"), x.get("source")) for x in (xs or []))
    return (f(rv.get("raw")), f(rv.get("kept")))
def tf_item(i, a, b): return bool(re.search(r"trv|food", i)) or "places" in (a["route"].get("task"), b["route"].get("task"))
A, B = load(sys.argv[1]), load(sys.argv[2]); allowed_extra = {"vit-cry-006"}
assert set(A) == set(B), (set(A) ^ set(B))
rows = []; bad = []
for i in A:
    a, b = A[i], B[i]; dr = route(a) != route(b); dc = ctx(a) != ctx(b); da = (a["answer"] or {}).get("text") != (b["answer"] or {}).get("text")
    if not (dr or dc or da): continue
    ok = i in allowed_extra or tf_item(i, a, b)
    rows.append((i, dr, dc, da, ok))
    if (dr or dc) and not ok: bad.append(i)
    if dr:
        ra, rb = route(a), route(b)
        print(f"{i} ROUTE {ra[:3]} -> {rb[:3]}; codes -{sorted(set(ra[3]) - set(rb[3]))} +{sorted(set(rb[3]) - set(ra[3]))}")
    if dc:
        ca, cb = ctx(a), ctx(b)
        for k, n in ((0, "raw"), (1, "kept")):
            if ca[k] != cb[k]: print(f"{i} CTX {n} -{[x[0] for x in ca[k] if x not in cb[k]]} +{[x[0] for x in cb[k] if x not in ca[k]]}" + (" (order)" if set(ca[k]) == set(cb[k]) else ""))
print(f"n={len(A)} changed(route|ctx|answer)={len(rows)}: route {sum(r[1] for r in rows)}, ctx {sum(r[2] for r in rows)}, answer-only {sum(r[3] and not r[1] and not r[2] for r in rows)}")
print("answer-only ids:", [r[0] for r in rows if r[3] and not r[1] and not r[2]])
print("route/ctx changes outside allowed set:", bad or "none")
print("errors:", sum(bool(t.get("error")) for t in A.values()), sum(bool(t.get("error")) for t in B.values()))
