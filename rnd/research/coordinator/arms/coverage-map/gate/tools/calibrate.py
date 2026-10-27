#!/usr/bin/env python3
"""PRECISION-GATE step 0 (0 LLM): calibrate tau on compose/replays/main.N10.gidf.jsonl. python3 -I tools/calibrate.py -> calibration.json
S_i = max fused score over the base kept chunks of item i = keptFull minus the chunks the head pass appended (reasonCodes headpass:add:<id> / headpass:dense:add:<id>);
the appended chunks are outside the keep step (neighbours carry score 0, dense candidates carry a cosine, not a fused score). No base kept chunk -> S = None (gate closes).
FACTPRESENT = compose.json labels[N10.gidf].kept_list (lexical FACTPRESENT OR cm oracle, the compose/kfull-funnel stage K); fact-absent = keyed MAIN items (kfull.json) not in it; unkeyed = the 5 other MAIN-97 ids.
tau = largest value with <= 10 % of the fact-present items strictly below it (None counts as below), truncated to 4 dp (live scores are unrounded)."""
import json, re, math, collections
A = "<workspace>/rnd/research/coordinator/arms"; C = A + "/coverage-map/compose"
R = {json.loads(l)["id"]: json.loads(l) for l in open(C + "/replays/main.N10.gidf.jsonl")}
K = set(json.load(open(C + "/compose.json"))["labels"]["N10.gidf"]["kept_list"]); KEYED = json.load(open(C + "/kfull.json"))["items"]
ids = open(A + "/lp-screens/main-97.ids").read().split()
def base_kept(r):
    app = set()
    for rc in r["reasonCodes"]:
        m = re.match(r"headpass:(?:dense:)?add:(.*)", rc)
        if m: app.add(m.group(1))
    return [k for k in r["keptFull"] if k["chunkId"] not in app]
S = {}; flag = {}; base_closed = {}
for i in ids:
    b = base_kept(R[i]); S[i] = max((k["score"] for k in b), default=None)
    flag[i] = "P" if i in K else ("A" if i in KEYED else "U"); base_closed[i] = not R[i]["keptFull"]
P = [i for i in ids if flag[i] == "P"]; Aa = [i for i in ids if flag[i] == "A"]; U = [i for i in ids if flag[i] == "U"]
key = lambda i: -1.0 if S[i] is None else S[i]
sv = sorted(key(i) for i in P); budget = math.floor(0.10 * len(P) + 1e-9)
t_exact = sv[budget]                       # (budget+1)-th smallest: S < t_exact holds for exactly `budget` items when no tie
tau = math.floor(t_exact * 1e4) / 1e4
below = lambda i, t: S[i] is None or S[i] < t
res = dict(n=len(ids), fact_present=len(P), fact_absent=len(Aa), unkeyed=len(U), budget_items=budget, tau_exact=t_exact, tau=tau)
for nm, g in (("P", P), ("A", Aa), ("U", U)):
    res[f"closed_at_tau_{nm}"] = sum(below(i, tau) for i in g); res[f"base_closed_{nm}"] = sum(base_closed[i] for i in g)
    res[f"newly_closed_{nm}"] = [i for i in g if below(i, tau) and not base_closed[i]]
    res[f"S_{nm}"] = sorted(key(i) for i in g)
res["fp_closed"] = [i for i in P if below(i, tau)]
res["newly_closed_all"] = [i for i in ids if below(i, tau) and not base_closed[i]]
# sensitivity: curve of tau
res["curve"] = []
for t in sorted({key(i) for i in ids if key(i) <= 0.6} | {0.5001}):
    tt = t + 1e-4 if t >= 0 else 1e-4
    res["curve"].append(dict(tau=round(tt, 4), fact_present_closed=sum(below(i, tt) for i in P), fact_absent_closed=sum(below(i, tt) for i in Aa), unkeyed_closed=sum(below(i, tt) for i in U)))
# alternative definition (all kept incl. appended) for the record
Sall = {i: max((k["score"] for k in R[i]["keptFull"]), default=None) for i in ids}
res["alt_all_kept_P"] = sorted(-1 if Sall[i] is None else Sall[i] for i in P); res["alt_all_kept_A"] = sorted(-1 if Sall[i] is None else Sall[i] for i in Aa)
res["S"] = {i: S[i] for i in ids}; res["flag"] = flag; res["base_closed"] = base_closed
json.dump(res, open(A + "/coverage-map/gate/calibration.json", "w"), indent=1)
print({k: v for k, v in res.items() if k not in ("S", "flag", "base_closed", "curve", "alt_all_kept_P", "alt_all_kept_A")})
for c in res["curve"]: print(c)
