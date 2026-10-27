#!/usr/bin/env python3
"""X2B-RETEST: changed answers / contexts per arm vs the ON control (0 LLM)."""
import json
A = "<workspace>/rnd/research/coordinator/arms"; X = A + "/x2b-retest"
ids = open("<workspace>/rnd/research/coordinator/ruler/ids/stage1-pool.ids").read().split()
ctl = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
tot = 0
for arm in ("x2boff", "x2bv1orc"):
    T = {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{X}/{arm}/traces/{arm}-K1-stage1-pool-s42.traces.jsonl")}
    ch = [i for i in ids if T[i]["answer"]["text"] != ctl[i]["text"]]
    real = [i for i in ch if not i.startswith("st-")]
    print(f"{arm}: changed {len(ch)} (real {len(real)}, st {len(ch)-len(real)}) -> {2*len(ch)} calls"); tot += 2 * len(ch)
print(f"total {tot} calls (cap 200)")
