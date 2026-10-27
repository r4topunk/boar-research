#!/usr/bin/env python3
"""ROUTING-R1 inventory (0 LLM). For every MAIN 97 item (v0.1 57 + cooking/money 40) on the LITEPACKS K0/K1/K3 runs, list the
items that never reach retrieval or the model (no retrieve:yes: facts table / calculator / places / first-aid card) or whose sources are
all dropped by the health gate (grounding:health-strict -> health-no-source / health-extractive). Judgments = existing LITEPACKS Haiku 5.5-low
rows (K1/K3 reuse K0 rows for byte-identical answers). Usage: python3 -I inventory.py [arm ...] -> ../aggregates/inventory.json + stdout."""
import json, glob, os, re, sys
H = "<workspace>/rnd/research/coordinator/arms/litepacks"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "aggregates")
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def traces(arm):
    out = {}
    for f in sorted(glob.glob(f"{H}/traces/lp-{arm}-*-s42.traces.jsonl")):
        if "smoke" in f or "-st-" in f: continue
        for t in rd(f): out[t["itemId"]] = t
    return out
def judg(arm):
    by = {}
    for f in sorted(glob.glob(f"{H}/judgments/lp-{arm}-*.judgments.jsonl")):
        if "-st-" in f: continue
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    out = {}
    for q, v in by.items():
        if len(v) != 2: continue
        ms = list(v.values()); m3 = lambda d: sum(d.values()) / 3
        out[q] = dict(s=sum(m3(m["boar"]) for m in ms) / 2, sref=sum(m3(m["ref"]) for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
    return out
TR = {a: traces(a) for a in ["K0", "K1", "K3"]}
J0 = {a: judg(a) for a in TR}
def J(a, i):
    if a == "K0" or TR[a][i]["answer"]["text"] == TR["K0"][i]["answer"]["text"]: return J0["K0"].get(i)
    return J0[a].get(i)
def rule(rc):
    r = [x for x in rc if x.startswith(("answer:", "task:places", "near:", "places:", "grounding:health", "grounding:fa-card", "headpass:health", "headpass:dense:health", "instant:off-health"))]
    return r
def klass(rc):
    if "retrieve:yes" not in rc:
        if any(x.startswith("answer:facts-") for x in rc): return "facts-table"
        if any(x.startswith("answer:calculator-") for x in rc): return "calculator"
        if "task:places" in rc: return "places"
        if any(x.startswith("answer:first-aid-card") for x in rc): return "fa-card-direct"
        return "other-no-retrieval"
    if "grounding:health-strict" in rc:
        if "grounding:health-no-source" in rc: return "health-gate:no-source"
        return "health-gate:extractive"
    return None
arms = sys.argv[1:] or ["K1", "K3", "K0"]
res = {}
for a in arms:
    rows = []
    for i, t in TR[a].items():
        rc = t["route"]["reasonCodes"]; k = klass(rc)
        if not k: continue
        txt = t["answer"]["text"]; j = J(a, i)
        rows.append(dict(id=i, cls=k, task=t["route"].get("task"), rule=rule(rc), kept=len((t.get("retrieval") or {}).get("kept") or []),
                         declined=bool(t["answer"].get("declined")), warned=txt.startswith(W), corr=j and j["corr"], s=j and round(j["s"], 3),
                         sref=j and round(j["sref"], 3), answer=txt[:260]))
    rows.sort(key=lambda r: (r["cls"], r["id"])); res[a] = rows
    print(f"== {a}: {len(rows)} routed items")
    for r in rows: print(f"  {r['id']:24} {r['cls']:22} corr={r['corr']} s={r['s']}/{r['sref']} w={int(r['warned'])} d={int(r['declined'])} {r['rule'][:4]} | {r['answer'][:110]!r}")
os.makedirs(OUT, exist_ok=True); json.dump(res, open(f"{OUT}/inventory.json", "w"), indent=1)
