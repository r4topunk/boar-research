#!/usr/bin/env python3
"""Step-3 aggregation (0 LLM). Estimator = arms/device-x6/tools/agg_device.py (load/setstats/paired, B 2000 seed 11), on the 51 CV5 ids.
O = ship15b-packs P Haiku rows; an id P did not re-judge (text identical to the K1 control) takes the control's rows for that id."""
import json, statistics, collections
A = "<workspace>/rnd/research/coordinator/arms/"; ARM = A + "native-parity/"
src = open(A + "device-x6/tools/agg_device.py").read().split("P, D, N = sys.argv")[0]; ad = {}; exec(src, ad)
ids = open(ARM + "cv5-51.ids").read().split()
ND = ad["load"](ARM + "judgments/native-N-D-v01-s42.judgments.jsonl"); NS = ad["load"](ARM + "judgments/native-N-S-v01-s42.judgments.jsonl")
O = ad["load"](A + "ship15b-packs/judgments/ship15b-packs-K1-main-sub3e6183-s42-v01.judgments.jsonl")
CTL = ad["load"](A + "lp-screens/control/judgments/lpctl-K1-main-s42-v01.judgments.jsonl")
OT = {json.loads(l)["itemId"]: json.loads(l)["answer"]["text"] for l in open(A + "ship15b-packs/traces/ship15b-packs-K1-main-sub3e6183-s42.traces.jsonl")}
CT = {json.loads(l)["itemId"]: json.loads(l)["answer"]["text"] for l in open(A + "lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl")}
filled = []
for i in ids:
    if i not in O and i in CTL and OT.get(i) == CT.get(i): O[i] = CTL[i]; filled.append(i)
out = {"n_ids": len(ids), "O_filled_from_control": filled}
# context: STYLE15B 1.5B-D (our engine, Detailed), if judged
import glob
sd = glob.glob(A + "ship15b-packs/judgments/style15b-detailed*-v01.judgments.jsonl") + glob.glob(A + "style15b-detailed/judgments/*-v01.judgments.jsonl")
OD = ad["load"](sd[0]) if sd else {}
common = [i for i in ids if i in ND and i in NS and i in O]
out["n_paired"] = len(common)
out["sets"] = {"O_ours_succinct_K1": ad["setstats"](O, common), "N-S_native_succinct_KB": ad["setstats"](NS, common), "N-D_native_detailed_KB": ad["setstats"](ND, common)}
out["paired"] = {"O_minus_ND": ad["paired"](O, ND, common), "O_minus_NS": ad["paired"](O, NS, common), "NS_minus_ND": ad["paired"](NS, ND, common)}
c2 = [i for i in common if i in OD]
if len(c2) >= 45:
    out["context_OD"] = {"n": len(c2), "file": sd[0], "OD_ours_detailed_K1": ad["setstats"](OD, c2), "OD_minus_ND": ad["paired"](OD, ND, c2), "O_minus_OD": ad["paired"](O, OD, c2)}
gen = [json.loads(l) for l in open(ARM + "runs/s3-gen.jsonl")]
for arm in ["N-D", "N-S"]:
    g = [r for r in gen if r["arm"] == arm and r["id"] in ids]
    out.setdefault("gen", {})[arm] = {"n": len(g), "nonempty": sum(bool(r["text"]) for r in g), "tokens_p50": statistics.median(r["tokens_predicted"] for r in g),
                                      "at_cap": sum(bool(r["stopped_limit"]) for r in g), "chars_p50": statistics.median(len(r["text"]) for r in g)}
tot = out["paired"]["O_minus_ND"]["d_raw"]; per = out["paired"]["NS_minus_ND"]["d_raw"]; pipe = out["paired"]["O_minus_NS"]["d_raw"]
ci = out["paired"]["O_minus_ND"]["d_raw_ci"]
out["persona_share_raw"] = round(per / tot, 3) if (ci[0] > 0 or ci[1] < 0) and tot else None
out["reading"] = "persona-dominant" if abs(per) >= 2 * abs(pipe) else ("pipeline-dominant" if abs(pipe) >= 2 * abs(per) else "mixed")
out["valid"] = all(v["nonempty"] >= 49 for v in out["gen"].values()) and len(common) == len(ids)
json.dump(out, open(ARM + "aggregates/s3-attribution.json", "w"), indent=1)
print(json.dumps(out, indent=1))
