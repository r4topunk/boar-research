#!/usr/bin/env python3
"""LITE5 declared splits (0 LLM): per item ratio = Σboar / Σref over 3 dims and both orders (LITE3 estimator) for ON (L5), OFF (LITE2 L), 4B plain (C4B), 4B X2b;
cells: LITE3 L bucket (health-safety separate) and reach (newly present / present under OFF / absent in both; fic.json). Writes aggregates/split5.json."""
import json, collections
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/lite5"
ids = [l.strip() for l in open(f"{A}/lite2/selftest20.ids") if l.strip()]
def ratios(f):
    s = collections.defaultdict(lambda: [0, 0])
    for l in open(f):
        r = json.loads(l)
        if not r.get("ok") or r["queryId"] not in ids: continue
        v = r["verdict"]; b, g = (v["scores_A"], v["scores_B"]) if r["order"] == "boarA" else (v["scores_B"], v["scores_A"])
        s[r["queryId"]][0] += sum(b.values()); s[r["queryId"]][1] += sum(g.values())
    return {i: s[i][0] / s[i][1] for i in ids}
R = {"ON": ratios(f"{H}/runs/lite5-on-st20-s42.judgments.haiku55-low.jsonl"), "OFF": ratios(f"{A}/lite2/runs/l-st20-s42.judgments.haiku55-low.jsonl"),
     "C4B": ratios(f"{A}/lite2/runs/c4b-st20-s42.judgments.haiku55-low.jsonl"), "X2b4B": ratios(f"{H}/runs/x2b4b-st20.judgments.haiku55-low.jsonl")}
L3 = {r["id"]: ("health_safety" if r["health_safety"] else r["L"]["bucket"]) for r in json.load(open(f"{A}/lite3/aggregates/lite3.json"))["slices"]["st20"]["items"]}
F = json.load(open(f"{H}/aggregates/fic.json"))["items"]
reach = {i: ("newly_present" if F[i]["on"] and not F[i]["off"] else "present_off" if F[i]["off"] else "absent") for i in ids}
def cells(key):
    out = {}
    for c in sorted(set(key.values())):
        m = [i for i in ids if key[i] == c]; mean = lambda k: round(sum(R[k][i] for i in m) / len(m), 3)
        d = [R["ON"][i] - R["OFF"][i] for i in m]
        out[c] = {"n": len(m), **{k: mean(k) for k in R}, "d_on_off": round(sum(d) / len(m), 3), "up_same_down": [sum(x > 1e-9 for x in d), sum(abs(x) <= 1e-9 for x in d), sum(x < -1e-9 for x in d)], "ids": m}
    return out
res = {"estimator": "sum boar / sum ref per item, 3 dims x both orders (LITE3)", "means": {k: round(sum(v.values()) / 20, 4) for k, v in R.items()},
       "by_lite3_bucket": cells(L3), "by_reach": cells(reach), "per_item": {i: {k: round(R[k][i], 3) for k in R} | {"bucket": L3[i], "reach": reach[i]} for i in ids}}
json.dump(res, open(f"{H}/aggregates/split5.json", "w"), indent=1)
print(json.dumps(res["means"]))
for k in ("by_lite3_bucket", "by_reach"):
    for c, v in res[k].items(): print(k, c, {x: v[x] for x in ("n", "OFF", "ON", "C4B", "X2b4B", "d_on_off", "up_same_down")})
