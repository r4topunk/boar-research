#!/usr/bin/env python3
"""MINISTRAL3-3B screen extras (0 LLM): sanity + answer tokens + wall time vs the mini control traces on the same items.
Usage: python3 -I screen_extras.py <candidate traces.jsonl> <K0|K1> <expected temperature for non-health items>"""
import json, sys, glob, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"
tr, K, temp = sys.argv[1], sys.argv[2], float(sys.argv[3])
C = {r["itemId"]: r for r in map(json.loads, open(tr))}
ctl = {}
for p in [f"{A}/lp-screens/control/traces/lpctl-{K}-main-s42.traces.jsonl", f"{A}/null-cal/control/traces/poolctl-{K}-st180-s42.traces.jsonl"]:
    for r in map(json.loads, open(p)): ctl[r["itemId"]] = r
ids = sorted(C); assert all(i in ctl for i in ids)
err = [i for i in ids if C[i]["error"]]
sha = {C[i]["runtime"]["versions"].get("model.sha256") for i in ids}
temps = {}
for i in ids: temps.setdefault(C[i]["runtime"]["sampler"].get("temperature"), []).append(i)
live = [i for i in ids if ctl[i]["timing"].get("outputTokens", 0) > 0]
tc = [C[i]["timing"]["outputTokens"] for i in live]; tk = [ctl[i]["timing"]["outputTokens"] for i in live]
wc = [C[i]["timing"]["totalMs"] for i in ids]; wk = [ctl[i]["timing"]["totalMs"] for i in ids]
dc = [C[i]["timing"]["decodeTokPerSec"] for i in live if C[i]["timing"].get("decodeTokPerSec")]
print(f"{tr.split('/')[-1]}: n {len(ids)} errors {len(err)} model.sha256 {[s[:8] for s in sha]} temps {{{', '.join(f'{t}: {len(v)}' for t, v in temps.items())}}} (expected {temp} + health 0)")
print(f"  answer tokens (live {len(live)}): cand median {st.median(tc)} mean {st.mean(tc):.0f} | control median {st.median(tk)} mean {st.mean(tk):.0f} | ratio of means {st.mean(tc)/st.mean(tk):.2f}")
print(f"  wall: mean totalMs cand {st.mean(wc)/1000:.1f} s vs control {st.mean(wk)/1000:.1f} s -> ratio {st.mean(wc)/st.mean(wk):.2f} | cand decode median {st.median(dc):.1f} tok/s")
