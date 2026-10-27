#!/usr/bin/env python3
"""ADDENDUM-4 jobs 19, 20, 21, 24 (coordinator, 0 LLM): same derive() as mk_jobs_ext.py, appended to jobs-ext.json's order (done jobs are skipped
by mini_queue.sh run-ext). Jobs 22 (carry with S+) and 23 (LONGSESSION conversations) are not built here: they need carry-dump paths and a multi-turn
builder that only the prep agent's tooling has. usage: python3 -I mk_jobs_ext2.py"""
import json, os, sys
N = "<workspace>/rnd/research/coordinator/arms/validation-1024/night"
src = open(N + "/tools/mk_jobs_ext.py").read().split("J = [derive(")[0]   # imports, personas, derive() only
G = {"__name__": "ext2"}; exec(compile(src, "mk_jobs_ext.py", "exec"), G); derive = G["derive"]; FE = G["FE"]
E = json.load(open(N + "/jobs-ext.json"))
J = [derive("v2-s", "v2-p2-s43", seed=43, persona="P2", suite="V2-p2-s43", reference=FE + "/v2-p2"),
     derive("v2-s", "v2-p2-s44", seed=44, persona="P2", groups="on", suite="V2-p2-s44", reference=FE + "/v2-p2"),
     derive("s5-packproof", "s5-packproof-p2", persona="P2", groups="on", suite="S5-p2", reference=FE + "/s5-packproof"),
     derive("s4-main-s42", "s4-main-p2-s42", persona="P2", suite="S4-p2", reference=FE + "/s4-main-s42/out/00-main/traces.jsonl"),
     derive("s5-packproof", "s5-packproof-s43", seed=43, suite="S5-s43", reference=FE + "/s5-packproof")]
for j in J:
    if j["name"] not in E["order"]: E["order"].append(j["name"]); E["jobs"].append(j)
json.dump(E, open(N + "/jobs-ext.json", "w"), indent=1)
for j in J: print(f"{j['name']:20s} {j['suite']:10s} groups {len(j['groups']):2d} requests {j['n_requests']}")
