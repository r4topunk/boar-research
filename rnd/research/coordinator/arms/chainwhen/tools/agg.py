#!/usr/bin/env python3
"""CHAINWHEN aggregation (0 LLM; criterion adba95cb). Score = PACKREAD agg: per-item score = mean of the 3 dims averaged over both judge orders,
Q = sum s / sum s_ref, item bootstrap B 2000 (single-run CI seed 11, paired CI seed 1, percentile 2.5/97.5 as PACKREAD agg.py).
ON for untriggered items = OFF (same answer and judgment, by construction). Writes ../aggregates/chainwhen.json and prints a summary.
Usage: python3 -I agg.py"""
import json, os, random, collections
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p):
    by = {}
    for l in open(p):
        r = json.loads(l)
        if str(r.get("ok")) != "True": continue
        m = r["mapped"] if isinstance(r["mapped"], dict) else json.loads(r["mapped"].replace("'", '"'))
        mr = lambda d: sum(d.values()) / len(d)
        by.setdefault(r["queryId"], []).append((mr(m["boar"]), mr(m["ref"]), m["boar"]["correctness"], m["winner"]))
    return {q: dict(s=sum(x[0] for x in v) / 2, r=sum(x[1] for x in v) / 2, corr=sum(x[2] for x in v) / 2, win=sum(x[3] == "boar" for x in v) / 2)
            for q, v in by.items() if len(v) == 2}
def ratio(d, ids): return sum(d[i]["s"] for i in ids) / sum(d[i]["r"] for i in ids)
def boot(fn, ids, seed, B=2000):
    if not ids: return None
    rnd = random.Random(seed); xs = sorted(fn([rnd.choice(ids) for _ in ids]) for _ in range(B)); return [round(xs[50], 3), round(xs[1949], 3)]
plan = json.load(open(f"{H}/data/plan.json")); P = {p["id"]: p for p in plan}
OFF = load(f"{H}/judgments/chainwhen-OFF.judgments.jsonl"); ONj = load(f"{H}/judgments/chainwhen-ON.judgments.jsonl")
TRIG = {"pick>1", "pick0"}
ON = {i: (ONj[i] if P[i]["branch"] in TRIG else OFF[i]) for i in OFF if P[i]["branch"] not in TRIG or i in ONj}
def contrast(ids):
    ids = sorted(i for i in ids if i in OFF and i in ON)
    if not ids: return dict(n=0)
    return dict(n=len(ids), Q_off=round(ratio(OFF, ids), 3), Q_on=round(ratio(ON, ids), 3), delta=round(ratio(ON, ids) - ratio(OFF, ids), 3),
                ci=boot(lambda s: ratio(ON, s) - ratio(OFF, s), ids, 1), ci_off=boot(lambda s: ratio(OFF, s), ids, 11), ci_on=boot(lambda s: ratio(ON, s), ids, 11),
                corr_off=round(sum(OFF[i]["corr"] for i in ids) / len(ids), 3), corr_on=round(sum(ON[i]["corr"] for i in ids) / len(ids), 3),
                win_off=round(sum(OFF[i]["win"] for i in ids) / len(ids), 3), win_on=round(sum(ON[i]["win"] for i in ids) / len(ids), 3))
by = lambda f: [p["id"] for p in plan if f(p)]
trig = by(lambda p: p["branch"] in TRIG)
M = dict(criterion="adba95cb", judged_off=len(OFF), judged_on_triggered=len(ONj),
         branches=dict(collections.Counter(p["branch"] for p in plan)), trigger_rate=round(len(trig) / len(plan), 3),
         triggered=contrast(trig), pick_gt1=contrast(by(lambda p: p["branch"] == "pick>1")), pick0=contrast(by(lambda p: p["branch"] == "pick0")),
         pick_gt1_fact1=contrast(by(lambda p: p["branch"] == "pick>1" and p["state"] == "fact@1")),
         pick_gt1_factelse=contrast(by(lambda p: p["branch"] == "pick>1" and p["state"] == "fact-elsewhere")),
         pick_gt1_nofact=contrast(by(lambda p: p["branch"] == "pick>1" and p["state"] == "no-fact")),
         pick_gt1_pick_is_fact=contrast(by(lambda p: p["branch"] == "pick>1" and p["pick_is_fact"])),
         pick0_nofact=contrast(by(lambda p: p["branch"] == "pick0" and p["state"] == "no-fact")),
         overall=contrast([p["id"] for p in plan]),
         untriggered_off_Q=round(ratio(OFF, [i for i in by(lambda p: p["branch"] not in TRIG) if i in OFF]), 3),
         by_pack={pk: contrast(by(lambda p, pk=pk: p["pack"] == pk and p["branch"] in TRIG)) for pk in sorted({p["pack"] for p in plan})})
T = M["triggered"]; F1 = M["pick_gt1_fact1"]
rule = {"delta>=+0.02": T.get("delta", -9) >= 0.02, "ci_low>0": bool(T.get("ci")) and T["ci"][0] > 0,
        "untriggered_identical": True, "pick>1&fact@1 delta>=-0.05": F1.get("n", 0) == 0 or F1["delta"] >= -0.05}
M["rule"] = rule; M["verdict"] = "ADOPT-CANDIDATE" if all(rule.values()) else "NO"
n_trig = len(trig); M["phone_cost"] = dict(per_triggered_s_kv=0.57, per_triggered_s_nokv=18, mean_per_question_s_kv=round(0.57 * n_trig / len(plan), 2),
                                           mean_per_question_s_nokv=round(18 * n_trig / len(plan), 1),
                                           note="G3 runs on every non-skipped item (pick=1 included), so the G3 prefill cost applies to all eligible items")
elig = len(by(lambda p: p["branch"] in ("pick>1", "pick0", "pick1"))); M["phone_cost"]["eligible_items"] = elig
M["phone_cost"]["mean_per_question_s_kv_all_eligible"] = round(0.57 * elig / len(plan), 2); M["phone_cost"]["mean_per_question_s_nokv_all_eligible"] = round(18 * elig / len(plan), 1)
json.dump(M, open(f"{H}/aggregates/chainwhen.json", "w"), indent=1)
for k in ("triggered", "pick_gt1", "pick0", "pick_gt1_fact1", "pick_gt1_factelse", "pick_gt1_nofact", "pick_gt1_pick_is_fact", "pick0_nofact", "overall"):
    print(f"{k:24}", M[k])
print("rule", rule, "->", M["verdict"])
