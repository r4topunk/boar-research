#!/usr/bin/env python3
"""RETV1ORC extra metrics (0 LLM). Usage: python3 -I report.py <cand traces> <cand agg.json> <ids file> <ctl agg.json> <ctl traces...>
Coverage = items with >= 1 retrieval.kept source; prompt tokens = mean timing.promptTokens over live items (control generated tokens > 0);
CEu / R counts via null-cal/tools/labels.py. With --stage2: U_d (s := 0 if R) and CEu-rate paired deltas, bootstrap B 2000 seed 11."""
import json, sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "null-cal", "tools")); from labels import label
args = [a for a in sys.argv[1:] if not a.startswith("--")]
ct, ca, idsf, ka = args[:4]; kts = args[4:]
ids = open(idsf).read().split()
def L(fs):
    d = {}
    for f in fs:
        for l in open(f):
            x = json.loads(l); d[x["itemId"]] = x
    return d
C, K = L([ct]), L(kts)
CA, KA = json.load(open(ca))["items"], json.load(open(ka))["items"]
live = lambda i: (K[i].get("timing") or {}).get("outputTokens", 0) > 0
cov = lambda T: sum(len(T[i]["retrieval"]["kept"]) > 0 for i in ids)
pt = lambda T: sum(T[i]["timing"]["promptTokens"] or 0 for i in ids if live(i)) / max(1, sum(live(i) for i in ids))
LC = {i: label(CA[i]) for i in ids}; LK = {i: label(KA[i]) for i in ids}
rf = sum(any(c.startswith("retfloor:variant:V1orC") for c in C[i]["route"]["reasonCodes"]) for i in ids)
rm = sum(int(c.split("removed-")[1]) for i in ids for c in C[i]["route"]["reasonCodes"] if c.startswith("retfloor:variant:"))
print(f"n {len(ids)} | coverage ctl {cov(K)} -> arm {cov(C)} | prompt tokens (live mean) ctl {pt(K):.0f} -> arm {pt(C):.0f} | "
      f"CEu ctl {sum(LK[i]['CEu'] for i in ids)} -> arm {sum(LC[i]['CEu'] for i in ids)} | R ctl {sum(LK[i]['R'] for i in ids)} -> arm {sum(LC[i]['R'] for i in ids)} | "
      f"V1orC gate fired on {rf} items, appends removed {rm} | context changed {sum(C[i]['retrieval']['kept'] != K[i]['retrieval']['kept'] for i in ids)}")
if "--stage2" in sys.argv:
    def m(xs, L, A):
        sr = sum(A[i]["sref"] for i in xs)
        return sum(0 if L[i]["R"] else L[i]["s"] for i in xs) / sr, sum(L[i]["CEu"] for i in xs) / len(xs)
    u1, c1 = m(ids, LC, CA); u0, c0 = m(ids, LK, KA)
    rnd = random.Random(11); du, dc = [], []
    for _ in range(2000):
        s = [rnd.choice(ids) for _ in ids]; a, b = m(s, LC, CA), m(s, LK, KA)
        du.append(a[0] - b[0]); dc.append(a[1] - b[1])
    du.sort(); dc.sort()
    ok = (u1 - u0) >= 0.03 and du[50] > 0 and (c1 - c0) <= 0.02
    print(f"U_d ctl {u0:.4f} -> arm {u1:.4f} delta {u1 - u0:+.4f} [{du[50]:+.4f}, {du[1949]:+.4f}] | CEu rate {c0:.3f} -> {c1:.3f} delta {c1 - c0:+.3f} "
          f"[{dc[50]:+.3f}, {dc[1949]:+.3f}] -> {'PASS' if ok else 'NO'}")
