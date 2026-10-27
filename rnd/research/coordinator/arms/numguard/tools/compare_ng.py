"""NUMGUARD per-item comparison (0 LLM calls). Usage: python3 -I compare_ng.py <ref traces> <arm traces> <route-replay.jsonl> <set name>
Per paired item: answer text equal (whitespace-normalised), reason codes equal, kept (title, section) list equal; numeric = numericGuard
from the route replay. Prints changed ids split numeric / non-numeric and one JSON line."""
import json, sys
ref, arm, rp, setname = sys.argv[1:5]
tr = lambda p: {(t := json.loads(l))["itemId"]: t for l in open(p) if l.strip()}
A, B = tr(ref), tr(arm)
num = {r["id"]: r["guard"] for r in map(json.loads, open(rp)) if r["set"] == setname}
norm = lambda s: " ".join((s or "").split())
f = {"answer": lambda t: norm((t.get("answer") or {}).get("text")), "codes": lambda t: (t.get("route") or {}).get("reasonCodes"),
     "kept": lambda t: [(s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or []]}
out = {"set": setname, "n": len(set(A) & set(B))}
for k, g in f.items():
    ch = sorted(i for i in set(A) & set(B) if g(A[i]) != g(B[i]))
    out[k] = {"changed_numeric": [i for i in ch if num.get(i)], "changed_non_numeric": [i for i in ch if not num.get(i)]}
print(json.dumps(out))
