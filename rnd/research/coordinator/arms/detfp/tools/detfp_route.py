"""DETFP M4 (0 LLM): layer per item in the claim traces (cut6-v02-s42) and the replay cells c7 / pr / prng. Codes and ids only.
Usage: python3 -I detfp_route.py <scratch dir> <out.json>"""
import json, sys, re
SP, OUT = sys.argv[1:3]
IDS = "v02-reasoning-A02 v02-reasoning-A03 v02-reasoning-A06 v02-reasoning-A07 v02-reasoning-B01 v02-reasoning-B09 v02-crypto-B03".split()
Q = {json.loads(l)["id"]: json.loads(l) for l in open("<private held-out dir>") if l.strip()}
H18 = {i for i, q in Q.items() if q["category"] == "health" or q.get("danger") in (True, "True")}
KEEP = re.compile(r"^(detector:fire|grounding:health-|healthgap:|numguard:|answer:|instant:final|detector:numeric-guard)")
def load(p):
    R = {}
    for l in open(p):
        t = json.loads(l); d = [e for e in t["events"] if e.get("type") == "done"]; rc = (d[-1].get("receipt") or {}) if d else {}
        codes = rc.get("reasonCodes") or t["route"].get("reasonCodes") or []
        pc = next((c for c in codes if c.startswith("detector:p=")), None)
        R[t["itemId"]] = {"modelId": rc.get("modelId"), "outcome": t["route"].get("outcome"), "p": float(pc[11:]) if pc else None,
                          "fire": "detector:fire" in codes, "sig": sorted(c for c in codes if KEEP.match(c) and "off-topic-dropped" not in c)}
    return R
cells = {"claim_s42": load("<private held-out dir>"), **{c: load(f"{SP}/{c}.traces.jsonl") for c in ("c7", "pr", "prng")}}
key = lambda r: (r["modelId"], tuple(r["sig"]))
out = {"seven": {i: {c: cells[c][i] for c in cells} for i in IDS}, "cells": {}}
for c in cells:
    R = cells[c]; diff = [i for i in R if key(R[i]) != key(cells["c7"][i])]
    out["cells"][c] = {"n": len(R), "fire_all": sum(r["fire"] for r in R.values()), "fire_nonhealth92": sum(R[i]["fire"] for i in R if i not in H18),
        "seven_fire": sum(R[i]["fire"] for i in IDS), "seven_health_no_source": sum("grounding:health-no-source" in R[i]["sig"] for i in IDS),
        "diff_vs_c7": len(diff), "diff_ids": diff, "diff_in_health18": sorted(set(diff) & H18), "diff_in_seven": sorted(set(diff) & set(IDS)),
        "p_mismatch_vs_c7": [i for i in R if R[i]["p"] != cells["c7"][i]["p"]]}
json.dump(out, open(OUT, "w"), indent=1); print(json.dumps(out["cells"], indent=1))
for i in IDS: print(i, {c: (cells[c][i]["modelId"], cells[c][i]["fire"], [s for s in cells[c][i]["sig"] if not s.startswith("detector:fire")]) for c in cells})
