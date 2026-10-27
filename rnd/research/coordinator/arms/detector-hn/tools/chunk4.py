#!/usr/bin/env python3
"""Read 4 (0 LLM): chunk-level delivery of the v3c replay vs SEFIX-124 (sefix/replays/main.F1F2F4.jsonl), reusing
coverage-map/tools/chunklevel.py's own score()/summ() (its source is exec'd up to the ARMS table, unchanged). usage: chunk4.py <out.json> label=path ..."""
import json, sys
CL = "<workspace>/rnd/research/coordinator/arms/coverage-map/tools/chunklevel.py"
src = open(CL).read(); pre = src.split("\nARMS = {")[0]; summ_src = "def summ(s):" + src.split("def summ(s):")[1].split("\nSUM = ")[0]
g = {"__name__": "chunk4"}; exec(pre, g); exec(summ_src, g)
res = {}; per = {}
for a in sys.argv[2:]:
    lab, p = a.split("=", 1); s = g["score"](p); per[lab] = s; res[lab] = g["summ"](s)
labs = list(per); base = labs[0]
for lab in labs[1:]:
    res[lab]["gained_vs_" + base] = [i for i in g["ids92"] if per[lab][i] and per[lab][i]["chunk"] and not (per[base][i] and per[base][i]["chunk"])]
    res[lab]["lost_vs_" + base] = [i for i in g["ids92"] if per[base][i] and per[base][i]["chunk"] and not (per[lab][i] and per[lab][i]["chunk"])]
json.dump(res, open(sys.argv[1], "w"), indent=1)
for k, v in res.items(): print(k, {x: v[x] for x in v if not x.startswith("flip")})
