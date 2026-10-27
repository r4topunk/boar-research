#!/usr/bin/env python3
"""LITE7 stage 4-5 (0 LLM). Estimator = packs-l2/tools/l2_agg.py load/setstats/paired (ratio-of-sums, per-item bootstrap B 2000, seed 11, paired on queryId).
ON = lite7 random20 Haiku rows; OFF = LITE5-180 ON rows (1.7B + X2b) on the same ids; X4B = 4B + X2b rows (descriptive). Per bucket (LITE6): mean per-item ratio s/r.
Writes aggregates/lite7-v2.json; prints numbers + the frozen verdict."""
import json, re, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/lite7"
src = open(f"{A}/packs-l2/tools/l2_agg.py").read().split("cell = sys.argv[1]")[0]; ns = {"__file__": f"{A}/packs-l2/tools/l2_agg.py"}; exec(src, ns)
load, setstats, paired, SE, TOPIC = ns["load"], ns["setstats"], ns["paired"], ns["SE"], ns["TOPIC"]
L6 = json.load(open(f"{A}/lite6/aggregates/lite6.json")); IDS = L6["random20_seed616"]; B6 = {x["id"]: x["bucket"] for x in L6["items"]}
G7 = json.load(open(f"{H}/aggregates/gate7-v2.json")); assert G7["verdict"] == "PASS"
pk = lambda q: next(p for p in SE + TOPIC if q.startswith(f"st-{p}-"))
J = {"ON": {}, "OFF": {}, "X4B": {}}; T = {"ON": {}, "OFF": {}}
for p in sorted({pk(q) for q in IDS}):
    J["ON"].update(load(f"{H}/runs/180/lite7-r20-on-{p}-s42.judgments.haiku55-low.jsonl"))
    J["OFF"].update(load(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.judgments.haiku55-low.jsonl"))
    J["X4B"].update(load(f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.judgments.jsonl"))
    for m, f in (("ON", f"{H}/runs/180/lite7-180-on-{p}-s42.traces.jsonl"), ("OFF", f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.traces.jsonl")):
        T[m].update({(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()})
for k in J: assert all(q in J[k] for q in IDS), (k, [q for q in IDS if q not in J[k]])
txt = lambda t: (t.get("answer") or {}).get("text") or ""
thin = [q for q in IDS if B6[q] == "thin"]; rest = [q for q in IDS if q not in thin]; changed = [q for q in IDS if txt(T["ON"][q]) != txt(T["OFF"][q])]
ir = lambda m, q: J[m][q]["s"] / J[m][q]["r"]
bucket = lambda ids: {"n": len(ids), "on": round(st.mean(ir("ON", q) for q in ids), 3), "off": round(st.mean(ir("OFF", q) for q in ids), 3),
                      "d": round(st.mean(ir("ON", q) - ir("OFF", q) for q in ids), 3), "up_same_down": [sum(ir("ON", q) > ir("OFF", q) + 1e-9 for q in ids), sum(abs(ir("ON", q) - ir("OFF", q)) <= 1e-9 for q in ids), sum(ir("ON", q) < ir("OFF", q) - 1e-9 for q in ids)]}
SENT = re.compile(r"(?<=[.!?])\s+"); nsent = lambda s: len([x for x in SENT.split((s or "").strip()) if len(x.strip()) > 1])
NOTICE = "This answer is not from an offline source on this phone; check it before relying on it."
HEDGE = re.compile(open(f"{H}/tools/gate7.py").read().split('HEDGE = re.compile(r"')[1].split('", re.I)')[0].replace('"\n                   r"', ""), re.I)
prof = lambda m, ids: {"words_p50": st.median(len(txt(T[m][q]).split()) for q in ids), "gt2": sum(nsent(txt(T[m][q])) > 2 for q in ids),
                       "hedged": sum(bool(HEDGE.search(txt(T[m][q]).replace(NOTICE, " "))) for q in ids),
                       "total_p50_s": round(st.median(T[m][q]["timing"]["totalMs"] / 1000 for q in ids if (T[m][q]["timing"].get("outputTokens") or 0) > 0), 2),
                       "ttft_p50_s": round(st.median(T[m][q]["timing"]["ttftMs"] / 1000 for q in ids if (T[m][q]["timing"].get("outputTokens") or 0) > 0), 2)}
out = {"criterion_sha256": open(f"{H}/LITE7-criterion-v2.sha256").read().split()[0], "judge": "claude-haiku-5-5 effort low, N=4, both orders", "ids": IDS,
       "stats": {k: setstats(J[k], IDS) for k in J}, "paired": {"ON-OFF": paired(J["ON"], J["OFF"], IDS), "ON-X4B": paired(J["ON"], J["X4B"], IDS), "OFF-X4B": paired(J["OFF"], J["X4B"], IDS)},
       "paired_changed": paired(J["ON"], J["OFF"], changed), "buckets": {"thin": bucket(thin), "rest": bucket(rest), "changed": bucket(changed)},
       "per_item": {q: {"bucket": B6[q], "on": round(ir("ON", q), 3), "off": round(ir("OFF", q), 3), "changed": q in changed} for q in IDS},
       "profile_r20": {"on": prof("ON", IDS), "off": prof("OFF", IDS)}, "gate7": {"pass": G7["pass"], "profile_180": G7["profile_180"], "latency_llm_p50_s": G7["latency_llm_p50_s"]}}
d = out["paired"]["ON-OFF"]["d_raw"]; tu = out["buckets"]["thin"]["on"] > out["buckets"]["thin"]["off"]
out["verdict"] = "DIRECTION-POSITIVE" if d > 0 and tu else "DIRECTION-NEGATIVE" if d < 0 else "FLAT"
out["licenses_180"] = bool(out["verdict"] == "DIRECTION-POSITIVE" and d >= 0.03 and out["paired"]["ON-OFF"]["d_raw_ci"][0] > 0)
json.dump(out, default=float, fp=open(f"{H}/aggregates/lite7-v2.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("stats", "paired", "paired_changed", "buckets", "profile_r20", "verdict", "licenses_180")}, indent=1))
for q, v in out["per_item"].items(): print(q, v)
