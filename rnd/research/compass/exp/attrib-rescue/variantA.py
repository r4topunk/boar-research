# Offline estimate of variant A (compact model: decline unless EVERY >=4-word sentence carries [n] after attribution).
# A changed answer's judged rubric is replaced by D x its reference rubric (D = 0.306, frozen bench floor). Judged runs only.
import json, collections, os
R = "<workspace>/boar-eval/runs/"
P = {"ios-main-s42": "night-2026-10-01/ios-main-s42", "ios-main-s43": "night-2026-10-01/ios-main-s43", "ios-main-s44": "night-2026-10-01/ios-main-s44",
     "g75desk-s42": "g75desk/g75desk-s42", "and-q15-r1": "devices/2026-10-02/and-q15-r1", "and-q15-r2": "devices/2026-10-02/and-q15-r2",
     "ios-q15-r1": "devices/2026-10-02/ios-q15-r1", "ios-q15-r2": "devices/2026-10-02/ios-q15-r2"}
D = 0.306
rows = json.load(open("rescued.json"))
aff = collections.defaultdict(set)
for r in rows:
    if r["nUncited"] > 0: aff[r["run"]].add(r["id"])
m = lambda s: (s["correctness"] + s["completeness"] + s["usefulness"]) / 3
for run, p in P.items():
    by = collections.defaultdict(list)
    for l in open(R + p + ".judgments.jsonl"):
        j = json.loads(l)
        if not j.get("ok"): continue
        v = j["verdict"]; b, ref = (v["scores_A"], v["scores_B"]) if j["order"] == "boarA" else (v["scores_B"], v["scores_A"])
        by[j["queryId"]].append((m(b), m(ref), b["correctness"]))
    J = {k: v for k, v in by.items() if len(v) == 2}
    sb = sum(sum(x[0] for x in v) / 2 for v in J.values()); sr = sum(sum(x[1] for x in v) / 2 for v in J.values())
    sbA = sb + sum(D * sum(x[1] for x in J[i]) / 2 - sum(x[0] for x in J[i]) / 2 for i in aff[run] if i in J)
    cw0 = sum(1 for v in J.values() if sum(x[2] for x in v) / 2 <= 1); cwA = cw0 - sum(1 for i in aff[run] if i in J and sum(x[2] for x in J[i]) / 2 <= 1)
    print(f"{run:13s} judged {len(J):2d} affected {len([i for i in aff[run] if i in J]):2d}  ratio {sb/sr:.3f} -> {sbA/sr:.3f} (Δ {sbA/sr-sb/sr:+.3f})  cw {cw0} -> {cwA}")
