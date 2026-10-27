#!/usr/bin/env python3
"""X2B-OFF-MAIN addendum 1 step 2: JUDGE_ALLOW lists for x2bon43 / x2boff43 under the reuse + cap-160 rule (0 LLM).
Reuse = byte-identical (itemId, text) from ON s42 control, OFF s42, null-s43 K1 aggregates; ON43/OFF43 identical text judged once (in ON43).
Over the cap: items in main-live77.ids order, both arms of an item together. Writes main/judge43/{on43,off43}.allow and plan.json."""
import json, os
A = "<workspace>/rnd/research/coordinator/arms"; X = A + "/x2b-retest"; CAP = 160
ids = open(X + "/main-live77.ids").read().split()
rd = lambda f: {json.loads(l)["itemId"]: json.loads(l) for l in open(f) if l.strip()}
pool = set()
for f in (A + "/null-cal/control/pool-K1.json", X + "/main/x2boffmain/aggregates/x2boffmain-K1-main-live77-s42.json", A + "/null-cal/arms/null-s43/aggregates/null-s43-K1-screen2-K1-s42.json"):
    for i, x in json.load(open(f))["items"].items(): pool.add((i, x["text"]))
ON = rd(f"{X}/main/x2bon43/traces/x2bon43-K1-main-live77-s42.traces.jsonl"); OFF = rd(f"{X}/main/x2boff43/traces/x2boff43-K1-main-live77-s42.traces.jsonl")
on_need, off_need, calls, dropped = [], [], 0, []
for i in ids:
    a = (i, ON[i]["answer"]["text"]) not in pool
    b = (i, OFF[i]["answer"]["text"]) not in pool and OFF[i]["answer"]["text"] != ON[i]["answer"]["text"]
    c = 2 * (a + b)
    if calls + c > CAP: dropped.append(i); continue
    calls += c; on_need += [i] * a; off_need += [i] * b
os.makedirs(X + "/main/judge43", exist_ok=True)
open(X + "/main/judge43/on43.allow", "w").write("".join(i + "\n" for i in on_need))
open(X + "/main/judge43/off43.allow", "w").write("".join(i + "\n" for i in off_need))
p = dict(on43_judge=len(on_need), off43_judge=len(off_need), calls=calls, cap=CAP, dropped=dropped,
         on43_reused=sum((i, ON[i]["answer"]["text"]) in pool for i in ids), off43_reused=sum((i, OFF[i]["answer"]["text"]) in pool for i in ids),
         on43_eq_off43=sum(ON[i]["answer"]["text"] == OFF[i]["answer"]["text"] for i in ids))
json.dump(p, open(X + "/main/judge43/plan.json", "w"), indent=1); print(p)
