#!/usr/bin/env python3
"""CVO L1 control read-out: cut 3 re-run today (ctl) vs cut3-confirm (Oct 4) vs CVO; added time on routed items vs the same-day control."""
import json, statistics
E = "<workspace>/boar-eval/runs/kiln/"
t = lambda p: {r["itemId"]: r for r in (json.loads(l) for l in open(E + p) if l.strip())}
D, N = [], []
for s in (44, 45):
    O = t(f"cut3-confirm/cut3-v01-s{s}.traces.jsonl"); C = t(f"cvo-l1/ctl/ctl-v01-s{s}.traces.jsonl"); V = t(f"cvo-l1/cvo-v01-s{s}.traces.jsonl")
    x = lambda a, b: sorted(i for i in a if a[i]["answer"]["text"] != b[i]["answer"]["text"])
    print(f"s{s}: cut3-today vs cut3-confirm differ {x(C, O)}; CVO vs cut3-today differ {x(V, C)}; CVO vs cut3-confirm differ {x(V, O)}")
    routed = [i for i in V if "cvo:routed" in V[i]["route"]["reasonCodes"]]
    d = [V[i]["timing"]["totalMs"] - C[i]["timing"]["totalMs"] for i in routed]
    nr = [V[i]["timing"]["totalMs"] - C[i]["timing"]["totalMs"] for i in V if i not in routed]
    print(f"  routed {routed} added vs cut3-today {[round(v/1000, 2) for v in d]}; non-routed median diff {statistics.median(nr)/1000:+.2f}s over {len(nr)}")
    D += d; N += nr
print(f"median added time routed (CVO minus cut3 today, n={len(D)}): {statistics.median(D)/1000:+.2f} s; non-routed median {statistics.median(N)/1000:+.2f} s (n={len(N)})")
