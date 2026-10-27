#!/usr/bin/env python3
"""TK2FIX-L1 declared splits from the step-0 replay (0 LLM): fact-chunk-kept gained (cut7 no -> tk2fix yes), kept-diff, prompt-diff ids.
Definitions = tk2fix/tools/compare_fix.py (fact chunk = in_pack_facts chunk_index of the item's own pack; first replay pass). Writes l1/splits.json."""
import json, re, sqlite3
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/tk2fix"; ST = f"{ROOT}/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]; CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
pub = lambda p: f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
def cid(x, p):
    m = CID.match(x.get("chunkId") or ""); return int(m.group(2)) if m and m.group(1) == p else None
def first(f):
    o = {}
    for l in load(f): o.setdefault(l["id"], l)
    return o
out = {"fact_gained": [], "fact_lost": [], "kept_diff": [], "prompt_diff": [], "fact_kept_cut7": 0, "fact_kept_tk2fix": 0, "per_pack_kept_diff": {}}
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True); facts = {}
    for it in load(f"{ST}/{p}.jsonl"):
        fa = it["source"]["article_id"]; fcs = set()
        for f in it["in_pack_facts"]:
            if f.get("chunk_index") is None: continue
            cs = [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (f.get("article", fa),))]
            if f["chunk_index"] < len(cs): fcs.add(cs[f["chunk_index"]])
        facts[it["id"]] = fcs
    C, X = first(f"{A}/runs/st-{p}.cut7.jsonl"), first(f"{A}/runs/st-{p}.tk2fix.jsonl"); k = 0
    for i, fcs in facts.items():
        a = any(cid(x, p) in fcs for x in C[i]["kept"] if cid(x, p)); b = any(cid(x, p) in fcs for x in X[i]["kept"] if cid(x, p))
        out["fact_kept_cut7"] += a; out["fact_kept_tk2fix"] += b
        if b and not a: out["fact_gained"].append(i)
        if a and not b: out["fact_lost"].append(i)
        if [x["chunkId"] for x in C[i]["kept"]] != [x["chunkId"] for x in X[i]["kept"]]: out["kept_diff"].append(i); k += 1
        if C[i].get("promptSha") != X[i].get("promptSha"): out["prompt_diff"].append(i)
    out["per_pack_kept_diff"][p] = k
for k in ("fact_gained", "fact_lost", "kept_diff", "prompt_diff"): out[f"n_{k}"] = len(out[k])
json.dump(out, open(f"{A}/l1/splits.json", "w"), indent=1)
print({k: v for k, v in out.items() if not isinstance(v, list)}); print("fact_gained", out["fact_gained"])
