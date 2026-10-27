"""EVALFIX part 1: wins / ties / order-disagreement ties / losses vs the reference, from existing judgment rows.
python3 -I winsties.py  -> aggregates/winsties.json (numbers only; no item text read or printed).
Encoding (judge-core.mjs mapVerdict/combineOrders): mapped.winner in {boar, ref, tie}; per item the two orders (boarA, boarB)
are combined: equal -> that verdict; different -> 'tie' (order-disagreement tie). Same-order tie = both orders say tie."""
import json, math, os
B = "<private held-out dir>"
VP, V2 = B + "V-para/", B + "bench-v02/"
IDS = {"vpara": VP + "runs-cut6/judged.ids", "v02": V2 + "runs-deepvpara/judged.ids"}
RUNS = {
 "H-vpara-s42": ("vpara", VP + "runs-dt512/dh-H-vpara-s42.judgments.jsonl"),
 "H-vpara-s43": ("vpara", VP + "runs-dt512/dh-H-vpara-s43.judgments.jsonl"),
 "K-vpara-s42": ("vpara", VP + "runs-cut6/cut6-vpara-s42.judgments.jsonl"),
 "K-vpara-s43": ("vpara", VP + "runs-cut6/cut6-vpara-s43.judgments.jsonl"),
 "Q-vpara-s42": ("vpara", VP + "runs-quantceil/qc-Q-vpara-s42.judgments.jsonl"),
 "Q-vpara-s43": ("vpara", VP + "runs-quantceil/qc-Q-vpara-s43.judgments.jsonl"),
 "H-v02-s42": ("v02", V2 + "runs-dt512v02/dhv-H-v02-s42.judgments.jsonl"),
 "K-v02-s42": ("v02", V2 + "runs-cut6/cut6-v02-s42.judgments.jsonl"),
}
def load(path, want):
    by = {}
    for l in open(path):
        if not l.strip(): continue
        r = json.loads(l)
        if r.get("ok") and r["queryId"] in want: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]["winner"]
    return {i: o for i, o in by.items() if "boarA" in o and "boarB" in o}
def wilson(k, n, z=1.96):
    if n == 0: return [None, None]
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n); h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return [round((c-h)/d, 4), round((c+h)/d, 4)]
def tally(P):
    n = len(P); w = t_same = t_dis = l = 0; raw = {"AB_BA_agree": 0}
    for o in P.values():
        a, b = o["boarA"], o["boarB"]
        if a == b:
            raw["AB_BA_agree"] += 1
            if a == "boar": w += 1
            elif a == "tie": t_same += 1
            else: l += 1
        else: t_dis += 1
    t = t_same + t_dis
    return {"n": n, "wins": w, "ties_same_order": t_same, "ties_order_disagree": t_dis, "losses": l,
            "win_rate": round(w/n, 4), "win_rate_ci": wilson(w, n),
            "wins_plus_ties_rate": round((w+t)/n, 4), "wins_plus_ties_ci": wilson(w+t, n),
            "wins_plus_same_order_ties_rate": round((w+t_same)/n, 4), "order_agreement": round(raw["AB_BA_agree"]/n, 4)}
out = {"encoding": "mapped.winner in {boar,ref,tie}; combineOrders: disagreement -> tie", "runs": {}}
vals = {}
for name, (s, p) in RUNS.items():
    want = set(x for x in open(IDS[s]).read().split("\n") if x)
    P = load(p, want); out["runs"][name] = tally(P); vals[name] = P
# pooled per arm over seeds on V-para (item x seed units, not independent: CI is indicative)
for arm in "HKQ":
    P = {}
    for s in ("s42", "s43"):
        for i, o in vals[f"{arm}-vpara-{s}"].items(): P[f"{i}|{s}"] = o
    out["runs"][f"{arm}-vpara-2seed-pooled"] = tally(P)
# distinct raw values check (counts per order)
import collections
c = collections.Counter()
for P in vals.values():
    for o in P.values(): c.update(o.values())
out["distinct_mapped_winner_values"] = dict(c)

# score-parity check: items where the order-summed rubric mean of boar >= ref (a tie-by-score proxy, independent of the winner field)
K = ("correctness", "completeness", "usefulness")
for name, (s_, p) in RUNS.items():
    want = set(x for x in open(IDS[s_]).read().split("\n") if x); by = {}
    for l in open(p):
        if not l.strip(): continue
        r = json.loads(l)
        if r.get("ok") and r["queryId"] in want:
            m = r["mapped"]; by.setdefault(r["queryId"], {})[r["order"]] = (sum(m["boar"][k] for k in K)/3, sum(m["ref"][k] for k in K)/3)
    full = [o for o in by.values() if len(o) == 2]
    out["runs"][name]["score_ge_ref"] = sum(1 for o in full if o["boarA"][0]+o["boarB"][0] >= o["boarA"][1]+o["boarB"][1])
    out["runs"][name]["score_gt_ref"] = sum(1 for o in full if o["boarA"][0]+o["boarB"][0] > o["boarA"][1]+o["boarB"][1])
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "aggregates", "winsties.json"), "w"), indent=1)
for k, v in out["runs"].items(): print(k, {x: v[x] for x in ("n","wins","ties_same_order","ties_order_disagree","losses","win_rate","wins_plus_ties_rate","wins_plus_ties_ci")})
print(out["distinct_mapped_winner_values"])
