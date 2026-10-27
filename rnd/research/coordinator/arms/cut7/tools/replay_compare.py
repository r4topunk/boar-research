#!/usr/bin/env python3
"""CUT7: compare replay-retrieval output (engine answer() with LLM stubbed, gate+detector from the cut 6 claim trace) of
cut 6 (wt/detmax) vs cut 7 (wt/cut7) per item: raw (title, section, source), query, k, tier, task, pre-answer sources.
Prints ONLY counts, ids and tiers (no query/question text). Usage: python3 -I replay_compare.py <label> <cut6.jsonl> <cut7.jsonl>"""
import json, sys
L = lambda p: {r["id"]: r for r in map(json.loads, open(p))}
key = lambda r: json.dumps([[(x["title"], x["section"], x["source"]) for x in r.get("raw") or []], r.get("query"), r.get("k"), r.get("tier"), r.get("task"), r.get("sources")])
a, b = L(sys.argv[2]), L(sys.argv[3])
assert set(a) == set(b), "item sets differ"
diff = sorted(i for i in a if key(a[i]) != key(b[i]))
inst6 = sum(r.get("tier") == "instant" for r in a.values()); inst7 = sum(r.get("tier") == "instant" for r in b.values())
print(f"{sys.argv[1]}: n={len(a)} identical={len(a) - len(diff)} changed={len(diff)} instant-tier cut6={inst6} cut7={inst7}"
      + (f" changed ids/tiers: {[(i, a[i].get('tier'), b[i].get('tier')) for i in diff]}" if diff else ""))
