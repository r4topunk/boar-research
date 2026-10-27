"""MICROD2Q default-off identity: d2q tree passes vs the tk2off reference (h8st/runs/<set>.ref.jsonl), with compare_h8.py's
`full` signature (raw chunkId/title/section/source/similarity/via, kept chunkId/title/section, promptSha, task, query, k).
Smoke: medlineplus copy passes off/x1/x2/off2. Writes aggregates/identity.json."""
import json, os
A = "<workspace>/rnd/research/coordinator/arms"; M = f"{A}/microd2q"
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
full = lambda l: json.dumps([[[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]],
                             [[x.get("chunkId"), x.get("title"), x.get("section")] for x in l["kept"]], l.get("promptSha"), l["task"], l["query"], l["k"]])
def passes(f, names):
    out, seen = {}, {}
    for l in load(f):
        n = seen.get(l["id"], 0); seen[l["id"]] = n + 1; out.setdefault(names[n], {})[l["id"]] = l
    return out
res = {}
sets = ["v01-kit"] + [f"st-{p}" for p in ("qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en")]
for s in sets:
    ref = {l["id"]: l for l in load(f"{A}/h8st/runs/{s}.ref.jsonl")}; P = passes(f"{M}/runs/id-{s}.jsonl", ["off", "x2"])
    res[s] = {"n": len(ref), "off_eq_ref": sum(full(ref[i]) == full(P["off"][i]) for i in ref), "x2_eq_ref": sum(full(ref[i]) == full(P["x2"][i]) for i in ref)}
ref = {l["id"]: l for l in load(f"{A}/h8st/runs/st-boar-medlineplus-en.ref.jsonl")}
P = passes(f"{M}/runs/smoke-medlineplus.d2q.jsonl", ["off", "x1", "x2", "off2"])
res["smoke-medlineplus"] = {c: sum(full(ref[i]) == full(P[c][i]) for i in ref) for c in P}
res["smoke-medlineplus"]["changed"] = {c: [i for i in ref if full(ref[i]) != full(P[c][i])] for c in P}
res["smoke-medlineplus"]["013"] = {c: {"raw": [x["chunkId"] for x in P[c]["st-boar-medlineplus-en-013"]["raw"]], "kept": [x["chunkId"] for x in P[c]["st-boar-medlineplus-en-013"]["kept"]]} for c in P}
json.dump(res, open(f"{M}/aggregates/identity.json", "w"), indent=1); print(json.dumps(res, indent=1))
