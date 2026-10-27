#!/usr/bin/env python3
"""RETFLOOR: parity of base vs LITEPACKS/LITE5 traces, and the MAIN items a variant empties or keeps covered by appends only (titles)."""
import json, sys
sys.path.insert(0, "/nonexistent")
O = "<workspace>/rnd/research/coordinator/arms/retfloor/out"; A = "<workspace>/rnd/research/coordinator/arms"
rd = lambda f: {r["itemId"]: r for r in map(json.loads, open(f))}
PM = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
t = lambda r: [k["title"] for k in r["retrieval"]["kept"]]
rc = lambda r: [c for c in r["route"]["reasonCodes"] if c.startswith(("context:", "headpass:")) or c == "grounding:no-good-source"]
ref = {**rd(f"{A}/litepacks/traces/lp-K1-v01-s42.traces.jsonl"), **rd(f"{A}/litepacks/traces/lp-K1-cm-s42.traces.jsonl")}
b = rd(f"{O}/base-MAIN.traces.jsonl")
print("parity MAIN vs LITEPACKS K1: kept", sum(t(b[i]) == t(ref[i]) for i in b), "codes", sum(rc(b[i]) == rc(ref[i]) for i in b), "/", len(b))
s = k = 0
for p in PM:
    r5 = rd(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.traces.jsonl"); bb = rd(f"{O}/base-PM-{p}.traces.jsonl")
    s += sum(t(bb[i]) == t(r5[i]) for i in bb); k += len(bb)
print("parity PM vs LITE5-180 X2b 1.7B traces: kept", s, "/", k)
V = sys.argv[1] if len(sys.argv) > 1 else "V1orC"
v = rd(f"{O}/{V}-MAIN.traces.jsonl"); main = [l.strip() for l in open(f"{A}/lp-screens/main-97.ids") if l.strip()]
pre = lambda r: next((int(c.split(":")[2]) for c in r["route"]["reasonCodes"] if c.startswith("retfloor:kept:")), 0)
print(f"\n{V}: MAIN items emptied (base kept titles)")
for i in main:
    if t(b[i]) and not t(v[i]): print(" ", i, "|", b[i]["question"][:70], "|", t(b[i]))
print(f"\n{V}: MAIN items still covered by appends only (kept titles)")
for i in main:
    if t(v[i]) and pre(v[i]) == 0: print(" ", i, "|", v[i]["question"][:70], "|", t(v[i]))
