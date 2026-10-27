"""HEALTHGAP-r2 replay comparison (rule v1.2 §5c, 0 LLM). Per set: (1) hg2 OFF vs plain cut 7 (must be identical on every item);
(2) hg2 ON vs hg2 OFF (changes only on predicate fires, from aggregates/healthgap-scan-r2.json); (3) hg2 ON vs the v1.1 ON traces
(runs/hg-replay-<set>-on.traces.jsonl, patch 8be8c9d1…) where they exist. Identity key = answer text + reason codes + kept titles
+ generation flag. Usage: python3 -I compare_hg2.py <out.json>"""
import json, sys
H = "<workspace>/rnd/research/coordinator/arms/healthgap"; R = f"{H}/runs/r2"
scan = json.load(open(f"{H}/aggregates/healthgap-scan-r2.json"))
fires = {h["id"] for h in scan["public_hits"]} | {r["id"] for r in scan["q2"] if r["cls"]} | {p["id"] for p in scan["r2_probes"] if p["got"]} | {p["id"] for p in scan["s4_multiturn"] if p["got"] and p["id"] == "mt-es-para"}
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
res = {"sets": {}, "items": [], "fail": []}
for s in ["probes", "v01", "st", "mlp", "r2"]:
    c7, off, on = jl(f"{R}/c7-replay-{s}.traces.jsonl"), jl(f"{R}/hg2-replay-{s}-off.traces.jsonl"), jl(f"{R}/hg2-replay-{s}-on.traces.jsonl")
    assert c7.keys() == off.keys() == on.keys(), s
    v11p = f"{H}/runs/hg-replay-{s}-on.traces.jsonl"
    try: v11 = jl(v11p)
    except FileNotFoundError: v11 = {}
    off_ne_c7 = [i for i in off if key(off[i]) != key(c7[i])]
    chg = [i for i in on if key(on[i]) != key(off[i])]
    out_fire = [i for i in chg if i not in fires]
    vs11 = [i for i in on if i in v11 and key(on[i]) != key(v11[i])]
    res["sets"][s] = {"n": len(on), "off_eq_c7": len(on) - len(off_ne_c7), "off_ne_c7": off_ne_c7, "fires": sorted(fires & on.keys()), "on_changed": chg,
                      "changed_outside_fires": out_fire, "fires_unchanged": sorted((fires & on.keys()) - set(chg)), "v11_n": len(v11.keys() & on.keys()), "vs_v11_changed": vs11}
    res["fail"] += [f"{s}:off!=c7:{i}" for i in off_ne_c7] + [f"{s}:change-outside-fire:{i}" for i in out_fire]
    for i in on:
        if i in fires or i in chg or i in vs11:
            b, a = off[i], on[i]
            res["items"].append({"set": s, "id": i, "fires": i in fires, "changed": i in chg, "before": layer(b), "after": layer(a), "v11_after": layer(v11[i]) if i in v11 else None,
                                 "vs_v11_changed": i in vs11, "kept_after": [k.get("title") for k in a["retrieval"]["kept"]][:3],
                                 "codes_after": [c for c in a["route"]["reasonCodes"] if c.startswith(("healthgap:", "grounding:", "numguard:"))], "text_after": a["answer"]["text"][:150], "q": a["question"][:90]})
exp_v11 = {"probes": ["h21", "h23", "h24", "m01", "m02", "nm02"], "v01": [], "st": [], "mlp": ["st-boar-medlineplus-en-003"]}
for s, e in exp_v11.items():
    if sorted(res["sets"][s]["vs_v11_changed"]) != sorted(e): res["fail"].append(f"{s}:vs-v11 {res['sets'][s]['vs_v11_changed']} != {e}")
res["verdict_c"] = "PASS" if not res["fail"] else "FAIL"
json.dump(res, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
for k, v in res["sets"].items(): print(k, {x: (len(v[x]) if isinstance(v[x], list) and x in ("fires",) else v[x]) for x in ("n", "off_eq_c7", "fires", "on_changed", "changed_outside_fires", "fires_unchanged", "v11_n", "vs_v11_changed")})
for it in res["items"]: print(f'{it["set"]:6} {it["id"]:28} f={int(it["fires"])} c={int(it["changed"])} {it["before"]:>16} -> {it["after"]:<18} v11={it["v11_after"]} {" ".join(c for c in it["codes_after"])[:90]} | {it["kept_after"][:1]}')
print("fail:", res["fail"], "verdict (c):", res["verdict_c"])
