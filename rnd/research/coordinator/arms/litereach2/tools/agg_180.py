"""LITEREACH2-180 stage 4-5 aggregation (0 LLM; criterion LITEREACH2-180-criterion.md sha 0f515606...). Estimator = packs-l2/tools/l2_agg.py
(per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId). Arm B20 = 1.7B X2b at 1200/4/8 (runs/180);
ref ON = LITE5-180 ON (600/2/4) Haiku rows; descriptive OFF, C4B (4B plain), X4B (4B X2b). Writes aggregates/lr2-180.json."""
import json, glob, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"; L = f"{A}/litereach2"; R = f"{L}/runs/180"
src = open(f"{A}/packs-l2/tools/l2_agg.py").read().split("cell = sys.argv[1]")[0]; ns = {"__file__": f"{A}/packs-l2/tools/l2_agg.py"}; exec(src, ns)
load, setstats, paired, SE, TOPIC = ns["load"], ns["setstats"], ns["paired"], ns["SE"], ns["TOPIC"]
PATH = {"B20": lambda p: f"{R}/litereach2-b20-180-{p}-s42.judgments.haiku55-low.jsonl", "ON": lambda p: f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.judgments.haiku55-low.jsonl",
        "OFF": lambda p: f"{A}/lite5/runs/180/lite5-180-off-{p}-s42.judgments.haiku55-low.jsonl", "C4B": lambda p: f"{A}/packs/selftest-runs/st-{p}-cut7-s42.judgments.jsonl",
        "X4B": lambda p: f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.judgments.jsonl"}
J = {k: {} for k in PATH}; pk = {}
for p in SE + TOPIC:
    d = {k: load(f(p)) for k, f in PATH.items()}; ids = set.intersection(*(set(v) for v in d.values())); assert len(ids) == 20, (p, {k: len(v) for k, v in d.items()})
    for k in d: J[k].update({q: d[k][q] for q in ids})
    for q in ids: pk[q] = p
ALL = sorted(J["B20"]); assert len(ALL) == 180
g = set(json.load(open(f"{L}/aggregates/step0.json"))["cells"]["b20"]["gained_vs_c1"])
groups = {"pooled": ALL, "SE": [q for q in ALL if pk[q] in SE], "topic": [q for q in ALL if pk[q] in TOPIC],
          "split:gained": [q for q in ALL if q in g], "split:rest": [q for q in ALL if q not in g]}
for p in SE + TOPIC: groups[f"pack:{p}"] = [q for q in ALL if pk[q] == p]
CMP = {"B20-ON": ("B20", "ON"), "B20-OFF": ("B20", "OFF"), "B20-C4B": ("B20", "C4B"), "B20-X4B": ("B20", "X4B"), "ON-OFF": ("ON", "OFF")}
out = {"criterion_sha256": open(f"{L}/LITEREACH2-180-criterion.sha256").read().split()[0], "estimator": "l2_agg.py per-item bootstrap ratio-of-sums diff, B 2000, seed 11, paired on queryId",
       "judge": "claude-haiku-5-5 effort low, N=4 shards, both orders", "groups": {}}
for k, v in groups.items():
    cm = CMP if not k.startswith("pack:") else {"B20-ON": CMP["B20-ON"], "ON-OFF": CMP["ON-OFF"]}
    out["groups"][k] = {"n": len(v), "stats": {a: setstats(J[a], v) for a in J}, "paired": {c: paired(J[a], J[b], v) for c, (a, b) in cm.items()}}
po = out["groups"]["pooled"]["paired"]["B20-ON"]; d, lo = po["d_raw"], po["d_raw_ci"][0]
out["verdict"] = "LEVER (Haiku, dev 180)" if d >= 0.03 and lo > 0 else "SMALL (Haiku, dev 180)" if lo > 0 else "NO (Haiku, dev 180)"
T = {(t := json.loads(l))["itemId"]: t for l in open(f"{R}/b20-180.all.traces.jsonl") if l.strip()}; T0 = {}
for f in glob.glob(f"{A}/lite5/runs/180/lite5-180-on-*-s42.traces.jsonl"):
    for l in open(f): t = json.loads(l); T0[t["itemId"]] = t
def med(xs): xs = [x for x in xs if x is not None]; return round(st.median(xs), 1) if xs else None
llm = [i for i in ALL if T[i]["timing"].get("promptTokens") is not None and T0[i]["timing"].get("promptTokens") is not None]
out["cost"] = {"n_llm_pairs": len(llm)}
for k in ("promptTokens", "ttftMs", "totalMs", "decodeTokPerSec", "outputTokens"):
    out["cost"][k] = {"B20": med([T[i]["timing"].get(k) for i in llm]), "ON": med([T0[i]["timing"].get(k) for i in llm]),
                      "paired_p50": med([T[i]["timing"][k] - T0[i]["timing"][k] for i in llm if T[i]["timing"].get(k) is not None and T0[i]["timing"].get(k) is not None])}
out["cost"]["words"] = {"B20": med([len(T[i]["answer"]["text"].split()) for i in ALL]), "ON": med([len(T0[i]["answer"]["text"].split()) for i in ALL])}
r20 = {(t := json.loads(l))["itemId"]: t for l in open(f"{L}/runs/r20.all.traces.jsonl") if l.strip()}
out["same_host_anchor_r20"] = {"n": len(r20), "answer_identical": sum(T[i]["answer"]["text"] == r20[i]["answer"]["text"] for i in r20),
                               "promptTokens_identical": sum(T[i]["timing"].get("promptTokens") == r20[i]["timing"].get("promptTokens") for i in r20)}
json.dump(out, open(f"{L}/aggregates/lr2-180.json", "w"), indent=1)
f = lambda pr: f"{pr['d_raw']:+.3f} ({pr['d_raw_ci'][0]:+.3f}..{pr['d_raw_ci'][1]:+.3f}) b/w {pr['items_better_worse'][0]}/{pr['items_better_worse'][1]}"
for k, r in out["groups"].items():
    s = r["stats"]; print(f"{k:26s} n={r['n']:3d} " + " ".join(f"{a} {s[a]['raw']:.3f}" for a in s) + " | " + " | ".join(f"{c} {f(pr)}" for c, pr in r["paired"].items()))
print("aboveMin B20-ON", json.dumps({k: po[k] for k in po if "min" in k}))
print("cost", json.dumps(out["cost"])); print("anchor", json.dumps(out["same_host_anchor_r20"])); print("VERDICT", out["verdict"])
