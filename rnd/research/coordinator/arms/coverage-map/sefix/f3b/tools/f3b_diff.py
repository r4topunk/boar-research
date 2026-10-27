#!/usr/bin/env python3
"""F3B stage 1-2 for one design (A|B): layers, F3b fired, kept packs, text equality vs the F3-SAFETY OFF traces; writes aggregates/f3b-<arm>-diff.json and the blinded sheet (key separate). python3 -I f3b_diff.py A|B"""
import json, re, random, os, sys
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARM = sys.argv[1]
def load(p): return {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
OFF = load(f"{D}/../f3-safety/runs/f3safety-off-s42.traces.jsonl"); ON = load(f"{D}/runs/f3b-{ARM}-s42.traces.jsonl")
def layer(rc, gens):
    has = lambda p: any(c.startswith(p) for c in rc)
    if has("answer:first-aid-card-") or has("answer:safety-fact-") or has("answer:emergency-numbers"): return "card"
    if has("grounding:fa-card-") and (has("grounding:health-card-first") or has("grounding:health-no-steps") or has("grounding:health-no-safe-excerpt")): return "card"
    if has("answer:facts-"): return "facts"
    if has("answer:calculator-"): return "calculator"
    if "answer:temperature-conversion" in rc: return "converter"
    if has("healthgap:") and not gens: return "healthgap"
    if has("grounding:health-no-source") or has("grounding:health-no-safe-excerpt"): return "health-refusal"
    if has("grounding:health-extractive"): return "extractive"
    if "instant:final" in rc: return "instant"
    return "model" if gens else "other"
def pack(k):
    s = (k.get("source") or "") + " " + (k.get("title") or "")
    for key, p in (("medlineplus.gov", "boar-medlineplus-en"), ("medicalsciences.stackexchange", "qa-health-se"), ("firstaid", "boar-firstaid-en"), ("First aid", "boar-firstaid-en"),
                   ("cooking.stackexchange", "qa-cooking-se"), ("money.stackexchange", "qa-money-se"), ("travel.stackexchange", "qa-travel-se"), ("outdoors.stackexchange", "qa-outdoors-se"),
                   ("simple.wikipedia", "boar-simplewiki-en"), ("wikivoyage", "boar-wikivoyage-en"), ("ethereum", "boar-crypto"), ("Appropedia", "other:appropedia"), ("archive.org", "other:us-gov"), ("en.wikipedia", "wiki-vital5"), ("github.com", "boar-factbook")):
        if key in s: return p
    return "unknown:" + s[:60]
def row(t):
    rc = t["route"]["reasonCodes"]; g = [e for e in t["events"] if e.get("kind") == "generation"]
    kept = [{"pack": pack(k), "title": k.get("title"), "section": k.get("section"), "source": (k.get("source") or "")[:90]} for k in t["retrieval"]["kept"]]
    return {"layer": layer(rc, g), "codes": [c for c in rc if not c.startswith(("context:", "citations:"))], "kept": kept, "text": t["answer"]["text"], "declined": t["answer"].get("declined"),
            "warnings": t["answer"].get("warnings"), "weak": t["answer"].get("weakSources"), "err": bool(t.get("error")), "model": t["runtime"]["model"], "ms": t["timing"]["totalMs"]}
ids = list(OFF)
assert list(ON) == ids or set(ON) == set(ids)
R = {i: {"off": row(OFF[i]), "on": row(ON[i])} for i in ids}
for i, r in R.items():
    r["fired"] = "grounding:health-fallback-subject" in r["on"]["codes"]
    r["blocked"] = [c for c in r["on"]["codes"] if c.startswith("grounding:f3b-") and "blocked" in c or "no-health-family" in c]
    r["same_text"] = r["off"]["text"] == r["on"]["text"]
    r["layer_changed"] = r["off"]["layer"] != r["on"]["layer"]
    r["codes_changed"] = r["off"]["codes"] != r["on"]["codes"]
DET = {"card", "facts", "calculator", "converter", "healthgap", "health-refusal", "extractive", "instant"}
agg = {"n": len(ids), "errors": [i for i in ids for a in ("off", "on") if R[i][a]["err"] or not R[i][a]["text"].strip()], "models": sorted({R[i][a]["model"] for i in ids for a in ("off", "on")}),
       "layers_off": {}, "layers_on": {}, "fired": [i for i in ids if R[i]["fired"]], "layer_changed": [i for i in ids if R[i]["layer_changed"]],
       "text_changed": [i for i in ids if not R[i]["same_text"]], "det_off_changed": [i for i in ids if R[i]["off"]["layer"] in DET and (R[i]["layer_changed"] or not R[i]["same_text"])],
       "card_changed": [i for i in ids if R[i]["off"]["layer"] == "card" and (R[i]["layer_changed"] or not R[i]["same_text"])], "blocked": [i for i in ids if R[i]["blocked"]], "refusal_to_model": [i for i in ids if R[i]["off"]["layer"] == "health-refusal" and R[i]["on"]["layer"] == "model"]}
for a in ("off", "on"):
    for i in ids: agg["layers_" + a][R[i][a]["layer"]] = agg["layers_" + a].get(R[i][a]["layer"], 0) + 1
os.makedirs(D + "/aggregates", exist_ok=True)
json.dump({"aggregate": agg, "perItem": R}, open(D + f"/aggregates/f3b-{ARM}-diff.json", "w"), indent=1)
# blinded sheet: ids model-answered in either arm; differing text -> X/Y pair, identical -> single answer
rng = random.Random(7 if ARM == "A" else 8); sheet = []; key = {}
for i in ids:
    r = R[i]
    if "model" not in (r["off"]["layer"], r["on"]["layer"]): continue
    if r["same_text"]: sheet.append({"id": i, "single": r["on"]["text"]}); continue
    flip = rng.random() < 0.5
    X, Y = (r["on"]["text"], r["off"]["text"]) if flip else (r["off"]["text"], r["on"]["text"])
    sheet.append({"id": i, "X": X, "Y": Y}); key[i] = {"X": "on" if flip else "off", "Y": "off" if flip else "on"}
json.dump(sheet, open(D + f"/aggregates/f3b-{ARM}-sheet.json", "w"), indent=1); json.dump(key, open(D + f"/aggregates/f3b-{ARM}-key.json", "w"), indent=1)
print(json.dumps(agg)); print("sheet", len(sheet))
