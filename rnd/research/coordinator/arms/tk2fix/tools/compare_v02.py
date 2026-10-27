"""TK2-FIX v0.2 kit no-harm scorer (criterion TK2FIX-V02-criterion.md; 0 LLM). SCRIPT-ONLY on blind: prints counts/ids only.
Writes aggregates/tk2fix-v02.json."""
import json, re, sys
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/tk2fix"; O = f"{ROOT}/blind/bench-v02/runs-packs"
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).lower(); bare = lambda t: _LIB.sub("", str(t or ""))
def gmatch(gold, ref):  # = compare_fix.py / scorers/retrieval.py rule
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
def passes(lines):
    out, seen = {}, {}
    for l in lines:
        n = seen.get(l["id"], 0); seen[l["id"]] = n + 1; out.setdefault(n, {})[l["id"]] = l
    return out
ids = lambda l, f="kept": [x.get("chunkId") for x in l[f]]
sig = lambda l: json.dumps([ids(l), ids(l, "raw"), l.get("promptSha")])
G = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json")).items() if isinstance(v, list) and v}
CELLS = ["cut7", "tk2fix"]; P = {c: passes(load(f"{O}/tk2fix-v02-kit.{c}.jsonl")) for c in CELLS}
res = {"criterion_sha256": open(f"{A}/TK2FIX-V02-criterion.md.sha256").read().split()[0], "set": "bench-v02 (110, kit, script-only)", "cells": {}}
errs = {c: sum(1 for p in P[c].values() for l in p.values() if l.get("error")) for c in CELLS}
gm = lambda i, l: {g for g in G.get(i, []) for x in l["kept"] if gmatch(g, x)}
for c in CELLS:
    L = P[c][0]
    res["cells"][c] = {"rows_pass1": len(L), "rows_pass2": len(P[c].get(1, {})), "repeat_identical": sum(sig(L[i]) == sig(P[c][1][i]) for i in L if i in P[c].get(1, {})),
        "errors": errs[c], "gold_kept_items": sum(1 for i in L if gm(i, L[i])), "gold_entries_kept": sum(len(gm(i, L[i])) for i in L),
        "gold_raw6_items": sum(1 for i in L if any(gmatch(g, x) for g in G.get(i, []) for x in L[i]["raw"][:6])),
        "kept_slots": sum(len(L[i]["kept"]) for i in L), "articles_kept": sum(len({x.get("title") for x in L[i]["kept"]}) for i in L),
        "empty_kept_retrieving": sum(1 for l in L.values() if l["raw"] and not l["kept"])}
a, b = P["cut7"][0], P["tk2fix"][0]; common = sorted(set(a) & set(b))
kset = [i for i in common if set(ids(a[i])) != set(ids(b[i]))]
kord = [i for i in common if ids(a[i]) != ids(b[i]) and i not in kset]
raw = [i for i in common if ids(a[i], "raw") != ids(b[i], "raw")]
route = [i for i in common if [a[i].get(k) for k in ("task", "query", "k")] != [b[i].get(k) for k in ("task", "query", "k")]]
codes = [i for i in common if a[i].get("codes") != b[i].get("codes")]
prompt = [i for i in common if a[i].get("promptSha") != b[i].get("promptSha")]
titles = [i for i in common if [x.get("title") for x in a[i]["kept"]] != [x.get("title") for x in b[i]["kept"]]]
harm = [i for i in common if gm(i, a[i]) - gm(i, b[i])]; gain = [i for i in common if gm(i, b[i]) - gm(i, a[i])]
res["diff"] = {"n_common": len(common), "kept_set_changed": kset, "kept_order_only": kord, "raw_changed": raw, "route_changed": route,
               "codes_changed": codes, "prompt_changed": prompt, "kept_titles_changed": titles, "harm_ids": harm, "gold_gain_ids": gain}
C7, TF = res["cells"]["cut7"], res["cells"]["tk2fix"]
g0 = all(res["cells"][c]["rows_pass1"] == 110 and res["cells"][c]["rows_pass2"] == 110 and res["cells"][c]["repeat_identical"] == 110 and errs[c] == 0 for c in CELLS)
res["gate"] = {"G0_infra": g0, "G1_kept_changes_le_10": len(kset) <= 10, "G2_gold_kept_ge_cut7": TF["gold_kept_items"] >= C7["gold_kept_items"], "G3_no_harm": not harm}
res["verdict"] = "VOID" if not g0 else ("PASS" if all(res["gate"].values()) else "FAIL")
json.dump(res, open(f"{A}/aggregates/tk2fix-v02.json", "w"), indent=1)
print(json.dumps(res["cells"])); print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in res["diff"].items()})); print(json.dumps(res["gate"]), res["verdict"])
