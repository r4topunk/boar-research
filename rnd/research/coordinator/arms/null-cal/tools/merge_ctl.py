#!/usr/bin/env python3
"""Merge the MINI controls of one pack set into the pool control (0 LLM). Usage: python3 -I merge_ctl.py <K0|K1> <out.json>
Sources: arms/lp-screens/control/aggregates/lpctl-<K>-main-s42.json (MAIN 97) + arms/null-cal/control/aggregates/poolctl-<K>-st180-s42.json (180 self-tests);
adds item["live"] = the control trace generated tokens (timing.outputTokens > 0)."""
import json, sys
K, out = sys.argv[1:3]; A = "<workspace>/rnd/research/coordinator/arms"
src = [(f"{A}/lp-screens/control/aggregates/lpctl-{K}-main-s42.json", f"{A}/lp-screens/control/traces/lpctl-{K}-main-s42.traces.jsonl"),
       (f"{A}/null-cal/control/aggregates/poolctl-{K}-st180-s42.json", f"{A}/null-cal/control/traces/poolctl-{K}-st180-s42.traces.jsonl")]
items = {}
for ag, tr in src:
    a = json.load(open(ag))["items"]; live = {}
    for l in open(tr):
        t = json.loads(l); live[t["itemId"]] = (t["timing"].get("outputTokens") or 0) > 0 and not t.get("error")
    for i, x in a.items():
        assert i not in items; x["live"] = live[i]; items[i] = x
json.dump(dict(pack_set=K, sources=[s[0] for s in src], n=len(items), items=items), open(out, "w"), indent=1, ensure_ascii=False)
print(K, len(items), "items,", sum(x["live"] for x in items.values()), "live ->", out)
