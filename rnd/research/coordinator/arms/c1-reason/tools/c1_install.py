#!/usr/bin/env python3
"""C1-REASON install replay reader, 0 LLM. usage: c1_install.py <dir with O1.jsonl, I1.jsonl, sets.json> <out json>
I1 = phone engine (bench-app/engine 0ca54d87) with the 6 A-union packs + qa-cooking-se + qa-money-se + boar-vitalik-blog-en.
Fact reached = the fact's source article title is in the engine's kept sources (article level; SE threads are short)."""
import json, os, sys
D, OUT = sys.argv[1], sys.argv[2]
B = "<workspace>"
L = lambda o: {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(D, o + ".jsonl"))}
O1, I1 = L("O1"), L("I1")
sets = json.load(open(os.path.join(D, "sets.json"))); main = sets["main"]
fact = {}
for p in ["qa-cooking-se", "qa-money-se"]:
    for l in open(f"{B}/boar-eval/bench/selftest/{p}/questions.jsonl"):
        d = json.loads(l); fact[d["id"]] = [d["selftest"]["source"]["title"]]
fact["vit-cry-005"] = ["Why I support privacy", "ERC-8262: Zero-Knowledge Compliance Oracle"]
fact["vit-cry-007"] = ["d/acc: one year later", "My techno-optimism"]
IDS = ["st-qa-cooking-se-002", "st-qa-cooking-se-003", "st-qa-cooking-se-008", "st-qa-cooking-se-012", "st-qa-cooking-se-013",
       "st-qa-cooking-se-015", "st-qa-money-se-004", "st-qa-money-se-007", "st-qa-money-se-009", "st-qa-money-se-010",
       "st-qa-money-se-011", "st-qa-money-se-020", "vit-cry-005", "vit-cry-007"]
def hit(lst, ts):
    lst = [x.lower() for x in lst]
    return any(t.lower() == x or x.endswith(": " + t.lower()) for t in ts for x in lst)
res = {"items": {}}
for i in IDS:
    r = I1[i]; raw = [x["title"] for x in r["raw"]]
    res["items"][i] = {"task": r.get("task"), "retrieved": bool(raw), "raw_hit": hit(raw, fact[i]),
                       "raw_rank": next((k for k, x in enumerate(raw) if hit([x], fact[i])), None),
                       "kept_hit": hit(r["sources"], fact[i]), "n_kept": len(r["sources"])}
others = [i for i in main if i not in IDS]
ch = [i for i in others if I1[i]["sources"] != O1[i]["sources"]]
probes = [i for i in O1 if i.startswith("probe:") or i.startswith("saf-")]
res["crowding_other_MAIN_changed"] = ch
res["crowding_v01_changed"] = [i for i in ch if not i.startswith("st-")]
res["safety_changed"] = [i for i in probes if I1[i]["sources"] != O1[i]["sources"]]
json.dump(res, open(OUT, "w"), indent=1)
for i, v in res["items"].items(): print(i, v)
print("other MAIN kept changed", len(ch), "of", len(others), "v0.1", len(res["crowding_v01_changed"]), "safety", len(res["safety_changed"]))
