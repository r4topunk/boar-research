"""HEALTHGAP-r2 generation comparison (rule v1.2 §5d, 0 judge calls): OFF vs ON traces (seed 42, 4B, claim kit; genmlp with
+ boar-medlineplus-en). Per item: layer before -> after, generation count, kept titles, identical text, first 150 chars of ON.
Checks: the 10 controls, n12, vit-hlt-003 byte-identical; h21 ON = one generation with "Wikivoyage: Cold weather" kept and
grounding:health-survival-sourced; every other fired item leaves the model; vitamin D -> grounding:health-dose-excerpt.
Usage: python3 -I compare_gen_hg2.py <out.json>"""
import json, sys
H = "<workspace>/rnd/research/coordinator/arms/healthgap"; R = f"{H}/runs/r2"
sys.argv, out_p = sys.argv[:1], sys.argv[1]
# jl / gen / key / layer: copied verbatim from tools/compare_hg2.py
def jl(p): return {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
def gen(t): return any(e.get("type") == "other" and e.get("kind") == "generation" for e in t["events"])
def key(t): return (t["answer"]["text"], t["route"]["reasonCodes"], [k.get("title") for k in t["retrieval"]["kept"]], gen(t))
def layer(t):
    c = t["route"]["reasonCodes"]; has = lambda p: next((x for x in c if x.startswith(p)), None)
    if gen(t): return "model+sourced" if has("grounding:health-survival-sourced") else "model"
    for p, name in [("answer:first-aid-card", "snakebite-card"), ("answer:safety-fact", "co-hazard"), ("answer:emergency-numbers", "emergency-numbers"),
                    ("answer:small-talk", "small-talk"), ("answer:calculator", "calculator"), ("answer:temperature", "calculator"), ("answer:facts", "facts"),
                    ("grounding:health-dose-excerpt", "dose-excerpt"), ("grounding:health-no-dose", "dose-line"), ("grounding:health-card-first", None), ("grounding:fa-card-", None),
                    ("grounding:health-no-safe-excerpt", "no-safe-steps"), ("grounding:health-no-source", "no-source-line"),
                    ("grounding:health-extractive", "excerpt"), ("instant:final", "excerpt"), ("grounding:current-event", "current-event"), ("places:", "places")]:
        x = has(p)
        if x: return name or ("card:" + (has("grounding:fa-card-") or "?").split("grounding:fa-card-")[1] + ("(first)" if has("grounding:health-card-first") else ""))
    return "other:" + (t["route"]["tier"] or "?")
CONTROLS = "food-002 lan-cmp-004 lan-cmp-005 lan-exp-001 lan-exp-007 lan-ref-001 lan-ref-003 vit-cry-006 vit-hum-001 vit-sci-002".split()
def ngen(t): return sum(1 for e in t["events"] if e.get("type") == "other" and e.get("kind") == "generation")
res = {"items": [], "fail": []}
for s in ["gen", "genmlp"]:
    off, on = jl(f"{R}/hg2-{s}-off-s42.traces.jsonl"), jl(f"{R}/hg2-{s}-on-s42.traces.jsonl")
    assert off.keys() == on.keys()
    for i in off:
        a, b = off[i], on[i]; same = a["answer"]["text"] == b["answer"]["text"]
        res["items"].append({"set": s, "id": i, "control": i in CONTROLS, "identical": same, "before": layer(a), "after": layer(b), "gen_before": ngen(a), "gen_after": ngen(b),
                             "kept_after": [k.get("title") for k in b["retrieval"]["kept"]][:3], "codes_after": [c for c in b["route"]["reasonCodes"] if c.startswith(("healthgap:", "grounding:health-dose", "grounding:health-survival", "grounding:fa-card", "grounding:health-no"))],
                             "q": b["question"][:90], "off150": a["answer"]["text"][:150], "on150": b["answer"]["text"][:150], "error": b.get("error") or a.get("error")})
it = {x["id"]: x for x in res["items"]}
for i in CONTROLS + ["n12", "vit-hlt-003"]:
    if not it[i]["identical"]: res["fail"].append(f"not identical: {i}")
h = it["h21"]
if not (h["gen_after"] == 1 and "Wikivoyage: Cold weather" in h["kept_after"] and "grounding:health-survival-sourced" in h["codes_after"]): res["fail"].append("h21 not sourced")
if "grounding:health-dose-excerpt" not in it["st-boar-medlineplus-en-003"]["codes_after"]: res["fail"].append("vitamin D not dose-excerpt")
for x in res["items"]:
    if x["error"]: res["fail"].append(f"error {x['id']}")
    if not x["control"] and x["id"] not in ("n12", "vit-hlt-003", "h21") and x["gen_after"] != 0: res["fail"].append(f"model after: {x['id']}")
res["counts"] = {"n": len(res["items"]), "changed": sum(not x["identical"] for x in res["items"]), "left_model": sum(x["gen_before"] > 0 and x["gen_after"] == 0 for x in res["items"]),
                 "controls_identical": sum(it[i]["identical"] for i in CONTROLS)}
res["verdict_d"] = "PASS" if not res["fail"] else "FAIL"
json.dump(res, open(out_p, "w"), indent=1, ensure_ascii=False)
print(res["counts"])
for x in res["items"]: print(f'{x["id"]:28} ident={int(x["identical"])} {x["before"]:>14}({x["gen_before"]}) -> {x["after"]:<16}({x["gen_after"]}) {x["kept_after"][:1]} | {"" if x["identical"] else x["on150"]!r}')
print("fail:", res["fail"], "verdict (d):", res["verdict_d"])
