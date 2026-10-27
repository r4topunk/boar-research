"""LITESAFETY layer per turn (criterion stage 3) = bonsai2/tools/layers.py precedence + healthgap (healthgap:* code, no generation) and
converter (answer:temperature-conversion) before health-refusal; plus warn tier, health-shaped flag, kept packIds (X2b check).
Usage: python3 -I layers_ls.py <traces.jsonl> [out.json]"""
import json, sys, re, collections
HP = {"boar-medlineplus-en", "qa-health-se", "boar-firstaid-en"}
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
def kept_packs(t):
    out = set()
    for e in t.get("events", []) or []:
        for k in (e.get("kept") or []) if isinstance(e.get("kept"), list) else []:
            if isinstance(k, dict) and k.get("packId"): out.add(k["packId"])
    for k in (t.get("retrieval") or {}).get("kept", []) or []:
        if isinstance(k, dict) and k.get("packId"): out.add(k["packId"])
    return sorted(out)
T = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]; rows = []
for t in T:
    rc = t["route"]["reasonCodes"]; g = [e for e in t.get("events", []) if e.get("kind") == "generation"]; L = layer(rc, g)
    warn = next((c.split(":", 1)[1] for c in rc if c.startswith("warn:")), None)
    i = t["itemId"]; probe = t.get("runId", "").startswith("ls-probes") or "probes" in sys.argv[1]
    rows.append({"id": i, "layer": L, "warn": warn, "healthShaped": L == "model" and (probe or bool(re.search(r"hlt|dng", i)) or warn is not None),
                 "detectorFire": "detector:fire" in rc, "numguard": [c for c in rc if c.startswith("numguard:")], "healthgap": [c for c in rc if c.startswith("healthgap:")],
                 "headpass": [c for c in rc if c.startswith("headpass:")], "keptPacks": kept_packs(t), "gens": len(g), "error": bool(t.get("error")),
                 "modelRuntime": (t.get("runtime") or {}).get("model"), "totalMs": t["timing"].get("totalMs"),
                 "reasoning": sum(e.get("reasoningTokens") or 0 for e in g), "words": len(((t.get("answer") or {}).get("text") or "").split()),
                 "codes": [c for c in rc if not c.startswith(("context:", "citations:"))]})
M = [r for r in rows if r["layer"] == "model"]
agg = {"n": len(rows), "errors": sum(r["error"] for r in rows), "detectorFire": sum(r["detectorFire"] for r in rows),
       "layer": dict(collections.Counter(r["layer"] for r in rows)), "modelAnswered": [r["id"] for r in M],
       "warnOnModel": dict(collections.Counter(r["warn"] or "none" for r in M)), "warnAll": {r["id"]: r["warn"] for r in rows if r["warn"]},
       "healthShapedModel": [r["id"] for r in M if r["healthShaped"]], "numguardCodes": {r["id"]: r["numguard"] for r in rows if r["numguard"]},
       "healthPackKept": [r["id"] for r in rows if set(r["keptPacks"]) & HP], "headpassCodes": sum(bool(r["headpass"]) for r in rows),
       "maxReasoning": max(r["reasoning"] for r in rows), "emptyModelAnswers": [r["id"] for r in M if r["words"] == 0]}
print(json.dumps(agg))
if len(sys.argv) > 2: json.dump({"aggregate": agg, "perItem": rows}, open(sys.argv[2], "w"), indent=1)
