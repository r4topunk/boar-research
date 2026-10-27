"""BONSAI2-2B Q2: which layer answered each trace (from route.reasonCodes + generation events only). Prints JSON per item + aggregate.
Usage: python3 -I layers.py <traces.jsonl> [out.json]
Layer precedence (first match wins):
  card        answer:first-aid-card-* | answer:safety-fact-* | answer:emergency-numbers | grounding:fa-card-* with grounding:health-card-first|health-no-steps|health-no-safe-excerpt
  facts       answer:facts-*
  calculator  answer:calculator-*
  health-refusal  grounding:health-no-source (no-source health card) | grounding:health-no-safe-excerpt without a card (fixed line)
  extractive  grounding:health-extractive (the answer is the source excerpt, no model)
  instant     instant:final (source sentence, no model)
  model       a generation event exists and none of the above (the model's text is the answer)
  other       none of the above (no generation)"""
import json, sys, collections, statistics as st
def layer(rc, gens):
    has = lambda p: any(c.startswith(p) for c in rc)
    if has("answer:first-aid-card-") or has("answer:safety-fact-") or has("answer:emergency-numbers"): return "card"
    if has("grounding:fa-card-") and (has("grounding:health-card-first") or has("grounding:health-no-steps") or has("grounding:health-no-safe-excerpt")): return "card"
    if has("answer:facts-"): return "facts"
    if has("answer:calculator-"): return "calculator"
    if has("grounding:health-no-source") or has("grounding:health-no-safe-excerpt"): return "health-refusal"
    if has("grounding:health-extractive"): return "extractive"
    if "instant:final" in rc: return "instant"
    return "model" if gens else "other"
T = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]; rows = []
for t in T:
    rc = t["route"]["reasonCodes"]; g = [e for e in t.get("events", []) if e.get("kind") == "generation"]
    rows.append({"id": t["itemId"], "layer": layer(rc, g), "detectorFire": "detector:fire" in rc,
                 "detectorConsulted": any(c.startswith("detector:p") for c in rc), "healthStrict": "grounding:health-strict" in rc,
                 "faCardGrounding": [c for c in rc if c.startswith("grounding:fa-card-")], "gens": len(g),
                 "noSourceBanner": any(c in rc for c in ("grounding:no-source-memory", "grounding:uncited-warning", "grounding:uncited-preface")),
                 "tier": t["route"].get("tier"), "task": t["route"].get("task"), "totalMs": t["timing"].get("totalMs"),
                 "error": bool(t.get("error")), "words": len(((t.get("answer") or {}).get("text") or "").split()),
                 "reasoning": sum(e.get("reasoningTokens") or 0 for e in g), "codes": [c for c in rc if not c.startswith(("context:", "citations:"))]})
agg = {"n": len(rows), "errors": sum(r["error"] for r in rows), "detectorFire": sum(r["detectorFire"] for r in rows),
       "layer": dict(collections.Counter(r["layer"] for r in rows)),
       "layerWhenFired": dict(collections.Counter(r["layer"] for r in rows if r["detectorFire"])),
       "modelAnswered": [r["id"] for r in rows if r["layer"] == "model"],
       "modelAnsweredFired": [r["id"] for r in rows if r["layer"] == "model" and r["detectorFire"]],
       "modelAnsweredHealthStrict": [r["id"] for r in rows if r["layer"] == "model" and r["healthStrict"]],
       "p50TotalS": round(st.median([r["totalMs"] for r in rows]) / 1000, 2),
       "p50ModelAnsweredS": round(st.median([r["totalMs"] for r in rows if r["layer"] == "model"] or [0]) / 1000, 2),
       "maxReasoning": max(r["reasoning"] for r in rows), "emptyAnswers": sum(r["words"] == 0 for r in rows)}
print(json.dumps(agg))
if len(sys.argv) > 2: json.dump({"aggregate": agg, "perItem": rows}, open(sys.argv[2], "w"), indent=1)
