"""LITEREACH2 stage 3-4 aggregation (0 LLM). Estimator = packs-l2/tools/l2_agg.py (load/setstats/paired: per-item bootstrap of the ratio-of-sums
difference, B 2000, seed 11, paired on queryId). Arm = 1.7B X2b at b20 (1200/4/8), ref = LITE5-180 ON (1.7B X2b c1) Haiku rows, same 20 ids.
Descriptive: vs LITE5-180 OFF (1.7B plain), 4B plain, 4B X2b. Split (declared): ids gaining the fact at b20 vs c1 (step0.json) vs rest."""
import json, glob
A = "<workspace>/rnd/research/coordinator/arms"; L = f"{A}/litereach2"
src = open(f"{A}/packs-l2/tools/l2_agg.py").read().split("cell = sys.argv[1]")[0]; ns = {"__file__": f"{A}/packs-l2/tools/l2_agg.py"}; exec(src, ns)
load, setstats, paired, SE, TOPIC = ns["load"], ns["setstats"], ns["paired"], ns["SE"], ns["TOPIC"]
ids = [l.strip() for l in open(f"{L}/random20-st180-s888.ids") if l.strip()]
J = {k: {} for k in ("B20", "ON", "OFF", "C4B", "X4B")}
for f in glob.glob(f"{L}/runs/r20/*.judgments.haiku55-low.jsonl"): J["B20"].update(load(f))
for p in SE + TOPIC:
    J["ON"].update(load(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.judgments.haiku55-low.jsonl")); J["OFF"].update(load(f"{A}/lite5/runs/180/lite5-180-off-{p}-s42.judgments.haiku55-low.jsonl"))
    J["C4B"].update(load(f"{A}/packs/selftest-runs/st-{p}-cut7-s42.judgments.jsonl")); J["X4B"].update(load(f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.judgments.jsonl"))
assert all(i in J[k] for k in J for i in ids), {k: sum(i in J[k] for i in ids) for k in J}
S0 = json.load(open(f"{L}/aggregates/step0.json")); g = set(S0["cells"]["b20"]["gained_vs_c1"])
groups = {"pooled": ids, "split:gained": [i for i in ids if i in g], "split:rest": [i for i in ids if i not in g],
          "changed_vs_c1": None}
# items whose prompt changed vs c1 in the step-0 replay
P = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
R = {c: {(l := json.loads(x))["id"]: l for p in P for x in open(f"{L}/runs/step0/{c}.{p}.jsonl") if x.strip()} for c in ("c1", "b20")}
groups["changed_vs_c1"] = [i for i in ids if R["b20"][i]["promptSha"] != R["c1"][i]["promptSha"]]
CMP = {"B20-ON": ("B20", "ON"), "B20-OFF": ("B20", "OFF"), "B20-C4B": ("B20", "C4B"), "B20-X4B": ("B20", "X4B"), "ON-OFF": ("ON", "OFF")}
out = {"criterion_sha256": open(f"{L}/LITEREACH2-criterion.sha256").read().split()[0], "estimator": "l2_agg.py per-item bootstrap ratio-of-sums diff, B 2000, seed 11",
       "judge": "claude-haiku-5-5 effort low, N=4 shards, both orders", "groups": {}}
for k, v in groups.items():
    if not v: continue
    out["groups"][k] = {"n": len(v), "ids": v if len(v) <= 6 else None, "stats": {a: setstats(J[a], v) for a in J}, "paired": {c: paired(J[a], J[b], v) for c, (a, b) in CMP.items()}}
po = out["groups"]["pooled"]["paired"]["B20-ON"]; d, lo = po["d_raw"], po["d_raw_ci"][0]
out["verdict"] = "LEVER-shaped (Haiku, dev, n 20)" if d >= 0.03 and lo > 0 else "DIRECTION-POSITIVE (Haiku, dev, n 20)" if d > 0 else "DIRECTION-NEGATIVE (Haiku, dev, n 20)"
# cost from traces
T = [json.loads(l) for l in open(f"{L}/runs/r20.all.traces.jsonl")]; T0 = {}
for f in glob.glob(f"{A}/lite5/runs/180/lite5-180-on-*-s42.traces.jsonl"):
    for l in open(f): t = json.loads(l); T0[t["itemId"]] = t
import statistics as st
def med(xs): xs = [x for x in xs if x is not None]; return round(st.median(xs), 1) if xs else None
out["cost"] = {k: {"B20": med([t["timing"].get(k) for t in T]), "ON": med([T0[i]["timing"].get(k) for i in ids])} for k in ("promptTokens", "totalMs", "ttftMs")}
out["cost"]["words"] = {"B20": med([len(t["answer"]["text"].split()) for t in T]), "ON": med([len(T0[i]["answer"]["text"].split()) for i in ids])}
json.dump(out, open(f"{L}/aggregates/r20.json", "w"), indent=1)
f = lambda pr: f"{pr['d_raw']:+.3f} ({pr['d_raw_ci'][0]:+.3f}..{pr['d_raw_ci'][1]:+.3f}) b/w {pr['items_better_worse'][0]}/{pr['items_better_worse'][1]}"
for k, r in out["groups"].items():
    s = r["stats"]; print(f"{k:16s} n={r['n']:2d} " + " ".join(f"{a} {s[a]['raw']:.3f}" for a in s) + " | " + " | ".join(f"{c} {f(pr)}" for c, pr in r["paired"].items()))
print("cost", json.dumps(out["cost"])); print("VERDICT", out["verdict"])
