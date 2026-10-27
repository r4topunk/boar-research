#!/usr/bin/env python3
"""COMBINED judge plan (0 LLM). python3 -I plan.py -> judge/plan.json, judge/S<seed>/{C,F}.ids
C side: items whose answer text differs from SEFIX-ALL of the same seed and (id, text) has no known judged row (cache = K3 control, ARM-G, SEFIX-ALL rows of both seeds); F side (seed 43 only, own fill): SEFIX-ALL s43 rows that are proxies on those items.
Priority: RD1 fired (readseq code) first, then v0.1 / cooking / money by id order. Cap 200 total."""
import json, os
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; SF = CM + "/sefix"; CB = CM + "/combined"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ld = lambda p: {t["itemId"]: t for t in rd(p)}
ids = open(A + "/lp-screens/main-97.ids").read().split()
r42 = json.load(open(SF + "/answers-sefixall.json")); r43 = json.load(open(SF + "/answers-sefixall-s43.json")); pool = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
TG = ld(CM + "/compose/screen/traces/cmp-G-K10-main-s42.traces.jsonl")
TF = {s: ld(SF + f"/ans-traces/sefixall-main-s{s}.traces.jsonl") for s in (42, 43)}; TK43 = ld(SF + "/ans-traces/ctlk1-main-s43.traces.jsonl"); TC = {s: ld(CB + f"/traces/combined-main-s{s}.traces.jsonl") for s in (42, 43)}
cache = set()
for i in ids:
    cache.add((i, pool[i]["text"])); cache.add((i, TG[i]["answer"]["text"])); cache.add((i, TF[42][i]["answer"]["text"]))
    if r43["items"][i]["ALL"]["judgment"] != "proxy": cache.add((i, TF[43][i]["answer"]["text"]))
    if r43["items"][i]["ctl"]["judgment"] != "proxy": cache.add((i, TK43[i]["answer"]["text"]))
fired = {s: {i for i in ids if any(r.startswith("readseq") for r in TC[s][i]["route"]["reasonCodes"])} for s in (42, 43)}
plan = {}; tot = 0
for s in (42, 43):
    chg = [i for i in ids if TC[s][i]["answer"]["text"] != TF[s][i]["answer"]["text"]]
    c = [i for i in chg if (i, TC[s][i]["answer"]["text"]) not in cache]
    f = [i for i in chg if s == 43 and r43["items"][i]["ALL"]["judgment"] == "proxy"]
    key = lambda i: (0 if i in fired[s] else 1, ids.index(i))
    plan[s] = dict(changed=len(chg), C=sorted(c, key=key), F=sorted(f, key=key), calls=2 * (len(c) + len(f)))
    tot += plan[s]["calls"]
    os.makedirs(f"{CB}/judge/S{s}", exist_ok=True)
    open(f"{CB}/judge/S{s}/C.ids", "w").write("\n".join(plan[s]["C"]) + "\n"); open(f"{CB}/judge/S{s}/F.ids", "w").write("\n".join(plan[s]["F"]) + ("\n" if plan[s]["F"] else ""))
plan["total_calls"] = tot
json.dump(plan, open(CB + "/judge/plan.json", "w"), indent=1); print({s: (v["changed"], len(v["C"]), len(v["F"]), v["calls"]) for s, v in plan.items() if s != "total_calls"}, tot)
