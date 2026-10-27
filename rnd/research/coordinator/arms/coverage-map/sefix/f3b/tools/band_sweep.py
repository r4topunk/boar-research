#!/usr/bin/env python3
"""F3B band sweep (0 run): which probes / MAIN cooking items an A-gate at BAND b would let through, from the F3-ON traces (probes: F3 fires with p < b; A's other conditions hold for all 21 F3 fires) and the SEFIX-ALL MAIN traces (5 cooking F3 fires). python3 -I band_sweep.py"""
import json, re, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p): return {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
def pval(t):
    p = None
    for c in t["route"]["reasonCodes"]:
        m = re.match(r"detector:p=([\d.]+)", c)
        if m: p = float(m.group(1))
    return p
ON = load(D + "/../f3-safety/runs/f3safety-on-s42.traces.jsonl"); MAIN = load(D + "/../ans-traces/sefixall-main-s42.traces.jsonl")
fire = lambda t: "grounding:health-fallback-subject" in t["route"]["reasonCodes"]
P = sorted((pval(t), i) for i, t in ON.items() if fire(t)); M = sorted((pval(t), i) for i, t in MAIN.items() if fire(t))
out = {"probe_fires_by_p": P, "main_fires_by_p": M, "bands": {}}
for b in (0.20, 0.28, 0.30, 0.32, 0.33, 0.45, 0.50, 0.60, 0.80, 1.01):
    out["bands"][str(b)] = {"probes": [i for p, i in P if p < b], "main_cooking": [i for p, i in M if p < b]}
json.dump(out, open(D + "/aggregates/band-sweep.json", "w"), indent=1)
for b, v in out["bands"].items(): print(b, "probes", v["probes"], "| main", v["main_cooking"])
