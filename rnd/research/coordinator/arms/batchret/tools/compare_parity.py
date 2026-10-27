#!/usr/bin/env python3
"""BATCHRET: parity + SQL/ms summary of two run dirs (runs/<tag>.p<n>). Usage: compare_parity.py <base dir> <new dir> [--json out]
Identical item = every field of the line equal except timing/SQL (ms, calls[].ms, calls[].sql): task, tier, query, k, raw,
sources, codes, sourcesFull, and each retrieve call's query, k, full chunks (text included) and their sha256."""
import json, sys, os, gzip, statistics as st
from collections import defaultdict

def load(d):
    out = {}
    for f in sorted(os.listdir(d)):
        if not f.endswith((".jsonl", ".jsonl.gz")): continue
        for l in (gzip.open if f.endswith(".gz") else open)(os.path.join(d, f), "rt"):
            if l.strip():
                r = json.loads(l); out[(f.removesuffix(".gz"), r["id"])] = r
    return out

def strip(r):
    r = dict(r); r.pop("ms", None)
    r["calls"] = [{k: v for k, v in c.items() if k not in ("ms", "sql")} for c in r.get("calls", [])]
    return json.dumps(r, sort_keys=True)

def pct(a, q):
    a = sorted(a); return a[min(len(a) - 1, int(q * (len(a) - 1) + 0.5))] if a else None

A, B = load(sys.argv[1]), load(sys.argv[2])
assert A.keys() == B.keys(), "item sets differ"
per = defaultdict(lambda: {"n": 0, "same": 0, "calls": 0, "sqlA": [], "sqlB": [], "packA": [], "packB": [], "msA": [], "msB": [], "diff": []})
kindsA, kindsB = defaultdict(int), defaultdict(int)
for key in sorted(A):
    a, b = A[key], B[key]
    s = per[a.get("set") or key[0].split("-")[0]]
    s["n"] += 1
    if strip(a) == strip(b): s["same"] += 1
    else: s["diff"].append(key[1])
    for ca, cb in zip(a.get("calls", []), b.get("calls", [])):
        s["calls"] += 1
        s["sqlA"].append(ca["sql"]["total"]); s["sqlB"].append(cb["sql"]["total"])
        pk = lambda c: sum(v for k, v in c["sql"]["byDb"].items() if not k.startswith("aoair"))
        s["packA"].append(pk(ca)); s["packB"].append(pk(cb))
        s["msA"].append(ca["ms"]); s["msB"].append(cb["ms"])
        for k, v in ca["sql"]["byKind"].items(): kindsA[k.split(":", 1)[1] if ":" in k else k] += v
        for k, v in cb["sql"]["byKind"].items(): kindsB[k.split(":", 1)[1] if ":" in k else k] += v
res = {}
allc = defaultdict(list)
for name, s in per.items():
    for k in ("sqlA", "sqlB", "packA", "packB", "msA", "msB"): allc[k] += s[k]
    allc["n"] = allc.get("n", []) + [s["n"]]; allc["same"] = allc.get("same", []) + [s["same"]]
def summ(s, n, same):
    m = lambda x: round(st.mean(x), 1) if x else None
    return {"items": n, "identical": same, "retrieveCalls": len(s["sqlA"]),
            "sqlPerCall_mean": [m(s["sqlA"]), m(s["sqlB"])], "sqlPerCall_p50": [pct(s["sqlA"], .5), pct(s["sqlB"], .5)],
            "packSqlPerCall_mean": [m(s["packA"]), m(s["packB"])],
            "sqlDrop_mean": round(1 - st.mean(s["sqlB"]) / st.mean(s["sqlA"]), 4) if s["sqlA"] else None,
            "ms_p50": [pct(s["msA"], .5), pct(s["msB"], .5)], "ms_p90": [pct(s["msA"], .9), pct(s["msB"], .9)]}
for name, s in sorted(per.items()):
    res[name] = summ(s, s["n"], s["same"]); res[name]["diffIds"] = s["diff"][:20]
res["ALL"] = summ(allc, sum(allc["n"]), sum(allc["same"]))
nc = res["ALL"]["retrieveCalls"] or 1
res["kindsPerCall"] = {k: [round(kindsA.get(k, 0) / nc, 2), round(kindsB.get(k, 0) / nc, 2)] for k in sorted(set(kindsA) | set(kindsB), key=lambda k: -kindsA.get(k, 0))}
print(json.dumps(res, indent=1))
if "--json" in sys.argv: json.dump(res, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
