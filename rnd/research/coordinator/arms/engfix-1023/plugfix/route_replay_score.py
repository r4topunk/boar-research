#!/usr/bin/env python3
"""Score a route_replay.test.ts output with the frozen PLUGBATCH-SELF route rules (score.py's route_hit, parsed by exec of its head).
python3 -I route_replay_score.py replay.json -> per-class route hits and the failing rows."""
import json, sys, collections
D = "<workspace>/rnd/research/coordinator/arms/plugbatch-self"
src = open(D + "/tools/score.py").read().split("def load(arm):")[0]
exec(src)
rep = json.load(open(sys.argv[1]))
by = collections.defaultdict(lambda: [0, 0]); fails = []
for rid in ORDER:
    r = rep[rid]; tr = {"route": {"reasonCodes": r["codes"]}, "answer": {"text": r["text"]}}
    ok, why = route_hit(rid, tr)
    c = EXP[rid]["category"]; by[c][0] += 1; by[c][1] += ok
    if not ok: fails.append((rid, why, [x for x in r["codes"] if x.startswith(("answer:", "detector:fire", "healthgate", "grounding:health", "grounding:fa-card"))][:4]))
tot = [sum(b[i] for b in by.values()) for i in (0, 1)]
print("route", tot[1], "/", tot[0]); print({k: f"{v[1]}/{v[0]}" for k, v in by.items()})
for f in fails: print(" miss", *f)
pt = ["sd-03", "sd-04", "co-07", "co-08", "co-14", "co-15"]
print("mnf", sum(1 for i in MNF if i not in [f[0] for f in fails]), "/5", "ptes", sum(1 for i in pt if i not in [f[0] for f in fails]), "/6")
