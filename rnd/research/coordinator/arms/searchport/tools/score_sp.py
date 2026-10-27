#!/usr/bin/env python3
"""SEARCHPORT scorer (0 LLM): retbench/tools/score.py (unchanged rules) pointed at arms/searchport/replays + aggregates.
Only change: an ST item's own docs compare without the 'local-' pack-id prefix (the native kit uses catalog ids). usage: score_sp.py <name> [--base B0]"""
import sys, os
RB0 = "<workspace>/rnd/research/coordinator/arms/retbench"; SP = "<workspace>/rnd/research/coordinator/arms/searchport"
src = open(RB0 + "/tools/score.py").read()
src = src.replace('f"{RB}/replays/', 'f"{SP}/replays/').replace('f"{RB}/aggregates/', 'f"{SP}/aggregates/')
old = 'own = lambda c: (c.get("docId") or "") in x["own_docs"]'
assert old in src
src = src.replace(old, 'own = lambda c: nid(c.get("docId")) in {nid(d) for d in x["own_docs"]}')
os.makedirs(SP + "/aggregates", exist_ok=True)
if "--base" not in sys.argv: sys.argv += ["--base", "B0"]
g = {"__name__": "__main__", "SP": SP}
exec(compile(src, "score.py", "exec"), g)
