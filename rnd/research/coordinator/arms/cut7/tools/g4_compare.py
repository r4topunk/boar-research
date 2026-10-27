#!/usr/bin/env python3
"""G4: replay-retrieval output of a FACTS tree vs cut 6 (replay-detmax.jsonl) and vs a previous round.
Non-target items must be identical on raw (title, section, source), query, k, tier, task and pre-answer sources.
Usage: python3 -I g4_compare.py <base.jsonl> <prev.jsonl> <new.jsonl> <label>"""
import json, statistics, sys
T = {"lan-cmp-001", "lan-rsn-002", "lan-ref-001", "lan-ref-004", "lan-exp-006", "lan-rsn-007", "lan-ref-005", "trv-002"}
L = lambda p: {r["id"]: r for r in map(json.loads, open(p))}
key = lambda r: json.dumps([[(x["title"], x["section"], x["source"]) for x in r.get("raw") or []], r.get("query"), r.get("k"), r.get("tier"), r.get("task"), r.get("sources")])
base, prev, new = L(sys.argv[1]), L(sys.argv[2]), L(sys.argv[3]); lab = sys.argv[4]
nt = [i for i in base if i not in T]
same = [i for i in nt if key(base[i]) == key(new[i])]
print(f"G4 {lab} vs cut6 (wt/detmax) non-target identical (raw titles+sections+source, query, k, tier, task, pre-answer sources): {len(same)}/{len(nt)}")
print("changed non-target:", sorted(set(nt) - set(same)))
sp = sum(key(prev[i]) == key(new[i]) for i in base)
print(f"{lab} vs prev all {len(base)} identical: {sp} / {len(base)}")
print("targets:", {i: f"{base[i].get('tier')}->{new[i].get('tier')}" for i in sorted(T)})
med = lambda d: statistics.median([d[i]["ms"] for i in nt if d[i].get("ms") is not None])
print(f"retrieve ms median non-target (items with ms): base {med(base):.2f} prev {med(prev):.2f} {lab} {med(new):.2f}")
