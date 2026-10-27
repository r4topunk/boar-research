#!/usr/bin/env python3
"""STYLE-SEFIX judge plan (0 LLM): D ids whose (id, text) has no cached row -> judge/need.ids. python3 -I tools/plan.py"""
import sys, json; sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/style-sefix/tools")
from common import *
cache = build_cache(); TD = ld(D + "/traces/style-sefix-D-s42.traces.jsonl"); TS = ld(SF + "/ans-traces/sefix124-main-s42.traces.jsonl")
assert sorted(TD) == sorted(ids)
need = [i for i in ids if (i, TD[i]["answer"]["text"]) not in cache]
same = [i for i in ids if TD[i]["answer"]["text"] == TS[i]["answer"]["text"]]
print("need", len(need), "calls", 2 * len(need), "identical-to-S", len(same), same)
assert 2 * len(need) <= 400
open(D + "/judge/need.ids", "w").write("\n".join(need) + "\n")
json.dump(dict(need=need, identical_to_S=same, cached=[i for i in ids if i not in need]), open(D + "/aggregates/plan.json", "w"), indent=1)
