#!/usr/bin/env python3
"""QWEN35-2B wall time and answer length vs the mini control (0 LLM).
Usage: python3 -I wall.py <K0|K1> <ids file> <candidate traces.jsonl> [--json out]
Control traces = the mini controls the gate compares against: lp-screens lpctl-<K>-main-s42 (MAIN 97) + null-cal poolctl-<K>-st180-s42 (180 self-tests).
Over the LIVE items (control outputTokens > 0) of the ids file:
  wall ratio  = sum(candidate totalMs) / sum(control totalMs)      (the stage-2 condition: <= 1.5)
  also median per-item ratio, output tokens (mean / median / max), decode tok/s median, reasoning tokens, errors, think-tag leaks, mean loadAvg1m.
Caveat: the control ran earlier under a different mini load; the ratio is a wall measurement, not a per-token speed."""
import json, statistics as st, sys
A = "<workspace>/rnd/research/coordinator/arms"
K, idf, ctr = sys.argv[1:4]
def load(p): return {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
C = {**load(f"{A}/lp-screens/control/traces/lpctl-{K}-main-s42.traces.jsonl"), **load(f"{A}/null-cal/control/traces/poolctl-{K}-st180-s42.traces.jsonl")}
X = load(ctr); ids = [i for i in open(idf).read().split() if i]
live = [i for i in ids if (C[i]["timing"].get("outputTokens") or 0) > 0]
tm = lambda D, i: D[i]["timing"]["totalMs"]; ot = lambda D, i: D[i]["timing"].get("outputTokens") or 0
def side(D):
    o = [ot(D, i) for i in live]
    return dict(sum_totalMs=round(sum(tm(D, i) for i in live)), out_mean=round(st.mean(o), 1), out_median=st.median(o), out_max=max(o),
                tps_median=st.median([D[i]["timing"].get("decodeTokPerSec") or 0 for i in live]),
                reasoning_tokens=sum(D[i]["timing"].get("reasoningTokens") or 0 for i in live),
                errors=sum(1 for i in ids if D[i].get("error")), think_leak=sum(1 for i in ids if "<think>" in D[i]["answer"]["text"] or "</think>" in D[i]["answer"]["text"]),
                load_mean=round(st.mean([D[i]["runtime"].get("loadAvg1m") or 0 for i in live]), 2))
out = dict(K=K, n=len(ids), live=len(live), cand=side(X), control=side(C))
out["wall_ratio"] = round(out["cand"]["sum_totalMs"] / out["control"]["sum_totalMs"], 3)
out["median_item_ratio"] = round(st.median([tm(X, i) / tm(C, i) for i in live]), 3)
out["out_tokens_ratio"] = round(out["cand"]["out_mean"] / out["control"]["out_mean"], 3)
print(json.dumps(out))
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
