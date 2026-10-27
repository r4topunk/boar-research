#!/usr/bin/env python3
"""Agreement between labeler 1 (dev.jsonl, the writers) and labeler 2 (relabel/labeler2.jsonl, blind to labels).
Prints Cohen's kappa on `emergency` and on the 3-way {pos, howto, strict-neg}, plus every disagreement with its text.
Run: python3 agreement.py"""
import json
from collections import Counter
from pathlib import Path
H = Path(__file__).resolve().parent
A = {json.loads(l)["id"]: json.loads(l) for l in open(H / "dev.jsonl")}
B = {json.loads(l)["id"]: json.loads(l) for l in open(H / "relabel/labeler2.jsonl")}
assert set(A) == set(B), set(A) ^ set(B)
def kappa(pairs):
    n = len(pairs); po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return po, (po - pe) / (1 - pe)
three = lambda r: "pos" if r["emergency"] else ("howto" if r["howto"] else "neg")
ids = sorted(A)
po, k = kappa([(A[i]["emergency"], B[i]["emergency"]) for i in ids]); print(f"emergency: agree {po:.3f}  kappa {k:.3f}")
po3, k3 = kappa([(three(A[i]), three(B[i])) for i in ids]); print(f"3-way:     agree {po3:.3f}  kappa {k3:.3f}")
for lang in ("en", "pt", "es"):
    L = [i for i in ids if A[i]["lang"] == lang]; p, kk = kappa([(A[i]["emergency"], B[i]["emergency"]) for i in L]); print(f"  {lang}: agree {p:.3f} kappa {kk:.3f}")
dis = [i for i in ids if three(A[i]) != three(B[i])]
print(f"disagreements {len(dis)} (1→0 {sum(A[i]['emergency'] > B[i]['emergency'] for i in dis)}, 0→1 {sum(A[i]['emergency'] < B[i]['emergency'] for i in dis)}, howto-only {sum(A[i]['emergency'] == B[i]['emergency'] for i in dis)})")
for i in dis:
    a, b = A[i], B[i]; u = " || ".join(("U: " if t["role"] == "user" else "A: ") + t["text"] for t in a["turns"])
    print(f"\n{i}  L1 {three(a)} [{a['cat']}] note: {a['note'][:140]}\n      L2 {three(b)} [{b['rule']}/{b['conf']}] {b.get('why','')}\n      {u[:600]}")
