"""HEALTHGAP ON vs OFF trace comparison (0 LLM). Per item: the answering layer before/after, and whether text, reason codes,
kept sources and the generation flag are identical. Items the v1.1 scan fires on may change; any other change is a FAIL.
Usage: python3 -I compare_hg.py <scan-v11.json> <out.json> <name>=<off.traces.jsonl>,<on.traces.jsonl> ...
"""
import json, sys
scan = json.load(open(sys.argv[1])); out = sys.argv[2]
fires = {r["id"] for r in scan["q2"] if r["cls"]} | {h["id"] for h in scan["public_hits"]}
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
def gen(t): return any(e.get("type") == "other" and e.get("kind") == "generation" for e in t["events"])
def layer(t):
    c = t["route"]["reasonCodes"]; has = lambda p: next((x for x in c if x.startswith(p)), None)
    if gen(t): return "model"
    for p, name in [("answer:first-aid-card", "snakebite-card"), ("answer:safety-fact", "co-hazard"), ("answer:emergency-numbers", "emergency-numbers"),
                    ("answer:small-talk", "small-talk"), ("answer:calculator", "calculator"), ("answer:temperature", "calculator"), ("answer:facts", "facts"),
                    ("grounding:health-no-dose", "dose-line"), ("grounding:health-card-first", None), ("grounding:fa-card-", None),
                    ("grounding:health-no-safe-excerpt", "no-safe-steps"), ("grounding:health-no-source", "no-source-line"),
                    ("grounding:health-extractive", "excerpt"), ("instant:final", "excerpt"), ("grounding:current-event", "current-event"), ("places:", "places")]:
        x = has(p)
        if x: return name or ("card:" + (has("grounding:fa-card-") or "?").split("grounding:fa-card-")[1] + ("(first)" if has("grounding:health-card-first") else ""))
    return "other:" + (t["route"]["tier"] or "?")
res = {"sets": {}, "items": []}
bad = []
for spec in sys.argv[3:]:
    name, paths = spec.split("="); off_p, on_p = paths.split(",")
    off = {t["itemId"]: t for t in jl(off_p)}; on = {t["itemId"]: t for t in jl(on_p)}
    assert off.keys() == on.keys(), name
    n = changed = 0; cf = []
    for i in off:
        a, b = off[i], on[i]; n += 1
        same = {"text": a["answer"]["text"] == b["answer"]["text"], "codes": a["route"]["reasonCodes"] == b["route"]["reasonCodes"],
                "kept": [k.get("title") for k in a["retrieval"]["kept"]] == [k.get("title") for k in b["retrieval"]["kept"]], "gen": gen(a) == gen(b)}
        ident = all(same.values())
        if not ident:
            changed += 1; cf.append(i)
            if i not in fires: bad.append(f"{name}:{i}")
        if i in fires or not ident:
            res["items"].append({"set": name, "id": i, "fires": i in fires, "identical": ident, "same": same, "before": layer(a), "after": layer(b),
                                 "gen_before": gen(a), "gen_after": gen(b), "codes_after": [c for c in b["route"]["reasonCodes"] if c.startswith(("healthgap:", "grounding:", "detector:"))],
                                 "text_after": b["answer"]["text"][:150], "q": a["question"][:100]})
    res["sets"][name] = {"n": n, "changed": changed, "changed_ids": cf, "fires_in_set": sorted(fires & off.keys()), "changed_outside_fires": [x for x in cf if x not in fires]}
res["unexpected_changes"] = bad
res["verdict_c"] = "PASS" if not bad and all(not it["gen_after"] for it in res["items"] if it["fires"] and it["id"] not in ("n12", "vit-hlt-003")) else "FAIL"
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
for k, v in res["sets"].items(): print(k, {x: v[x] for x in ("n", "changed", "changed_outside_fires")}, "changed:", " ".join(v["changed_ids"]))
for it in res["items"]: print(f'{it["set"]:7} {it["id"]:28} fires={int(it["fires"])} ident={int(it["identical"])} {it["before"]:>18} -> {it["after"]:<22} {" ".join(c for c in it["codes_after"] if not c.startswith("detector"))[:110]}')
print("unexpected:", bad, "verdict (c):", res["verdict_c"])
