"""LITEREACH2 step-0 gate (criterion LITEREACH2-criterion.md sha b418afd6...; 0 LLM). Reads runs/step0/<cell>.<pack>.jsonl; writes aggregates/step0.json; prints the table.
Fact in context = an oracle fact chunk of the item's own pack in the kept list (gate_x2b.py rule); fic = LITE5 fic.py rule (split-x2b S_present OR appended fact)."""
import json, re, statistics as st, collections, hashlib
A = "<workspace>/rnd/research/coordinator/arms"; L = f"{A}/litereach2"; O = f"{L}/runs/step0"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
CELLS = ["c1", "b15", "b20", "t15", "t20"]; ENV = {"c1": "600/2/4", "b15": "900/3/6", "b20": "1200/4/8", "t15": "900/2/4", "t20": "1200/2/4"}
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$"); load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
own = lambda ids, p: {int(m.group(2)) for x in ids for m in [CID.match(x or "")] if m and m.group(1) == p}
full = lambda l: json.dumps([[[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]],
                             [[x.get("chunkId"), x.get("title"), x.get("section")] for x in l["kept"]], l.get("promptSha"), l["task"], l["query"], l["k"]])
FACTS = json.load(open(f"{A}/oracle-st/tools/oracle-facts.json"))
SPLIT = {d["id"]: d for d in map(json.loads, open(f"{A}/headpass-st/runs-x2/split-x2b.jsonl"))}
FIC = json.load(open(f"{A}/lite5/aggregates/fic-180.json"))
def cell(c): return {l["id"]: (p, l) for p in PACKS for l in load(f"{O}/{c}.{p}.jsonl")}
D = {c: cell(c) for c in ["i3", "u1"] + CELLS}; ids = sorted(D["c1"]); assert len(ids) == 180
res = {"criterion_sha256": open(f"{L}/LITEREACH2-criterion.sha256").read().split()[0], "patch_sha256": open("<workspace>/kiln-local/be-0cfd4a77-cut7-litereach2/LITEREACH2_PATCH_SHA256").read().strip()}
# identities
ref_x2b = {}
for p in PACKS:
    seen = collections.Counter()
    for l in load(f"{A}/headpass-st/runs-x2/st-{p}.x2b.jsonl"):
        n = seen[l["id"]]; seen[l["id"]] += 1
        if n == 3: ref_x2b[l["id"]] = l
i1 = sum(full(D["u1"][i][1]) == full(D["c1"][i][1]) and D["u1"][i][1]["appended"] == D["c1"][i][1]["appended"] for i in ids)
DATE = re.compile(r"Today is [A-Za-z]+, \d{1,2} [A-Za-z]+ \d{4} \(this device's date\)")
def dnorm(l):  # v2: I3 with the engine's device-date line normalised (prompt re-hashed)
    l = dict(l); l["promptSha"] = None if l.get("prompt") is None else hashlib.sha256(DATE.sub("Today is <DATE> (this device's date)", l["prompt"]).encode()).hexdigest(); return l
i3_raw = sum(full(D["i3"][i][1]) == full(ref_x2b[i]) for i in ids)
i3 = sum(full(dnorm(D["i3"][i][1])) == full(dnorm(ref_x2b[i])) and D["i3"][i][1]["appended"] == ref_x2b[i]["appended"] for i in ids)
tr = {}
for p in PACKS:
    for l in load(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.traces.jsonl"): tr[l["itemId"]] = [x.split(":add:")[1] for x in l["route"]["reasonCodes"] if x.startswith(("headpass:add:", "headpass:dense:add:"))]
i2 = sum(D["c1"][i][1]["appended"] == tr[i] for i in ids)
def pres(i, l): p = D["c1"][i][0]; return bool({int(x.rsplit(":", 1)[1]) for x in FACTS[i]["fact_chunks"]} & own([x["chunkId"] for x in l["kept"]], p))
def fic(i, l): p = D["c1"][i][0]; return SPLIT[i]["S_present"] or bool({int(x.rsplit(":", 1)[1]) for x in FACTS[i]["fact_chunks"]} & own(l.get("appended") or [], p))
F1 = {i: pres(i, D["c1"][i][1]) for i in ids}
res["identity"] = {"I1_u1_vs_c1": i1, "I2_c1_appended_vs_lite5_on_traces": i2, "I3_i3_vs_headpass_x2b": i3, "I3_unnormalised_v1": i3_raw,
                   "F_c1": sum(F1.values()), "fic_c1": sum(fic(i, D["c1"][i][1]) for i in ids), "fic_lite5_traces": sum(FIC[i]["on"] for i in ids),
                   "c1_vs_lite5_fic_agree": sum(fic(i, D["c1"][i][1]) == FIC[i]["on"] for i in ids)}
p50 = lambda xs: round(st.median(xs), 1)
cells = {}
for c in CELLS:
    rows = [D[c][i][1] for i in ids]; F = {i: pres(i, D[c][i][1]) for i in ids}
    dt = [D[c][i][1]["promptTokens"] - D["c1"][i][1]["promptTokens"] for i in ids if D[c][i][1]["promptTokens"] is not None and D["c1"][i][1]["promptTokens"] is not None]
    pt = [l["promptTokens"] for l in rows if l["promptTokens"] is not None]
    hf = sum(not h["ok"] for l in rows for h in (l.get("hpHealth") or []))
    fam = collections.Counter(("SE" if D[c][i][0].startswith("qa-") else "topic") for i in ids if F[i] and not F1[i])
    cells[c] = {"env_budget/D/cap": ENV[c], "F": sum(F.values()), "dF_vs_c1": sum(F.values()) - sum(F1.values()), "fic": sum(fic(i, D[c][i][1]) for i in ids),
                "gained_vs_c1": sorted(i for i in ids if F[i] and not F1[i]), "lost_vs_c1": sorted(i for i in ids if F1[i] and not F[i]), "gained_family": dict(fam),
                "articles_kept_mean": round(st.mean(len({x["title"] for x in l["kept"]}) for l in rows), 2), "kept_chunks_mean": round(st.mean(len(l["kept"]) for l in rows), 2),
                "appended_chunks": sum(len(l.get("appended") or []) for l in rows), "fired": sum(bool(l.get("appended")) for l in rows),
                "budget_dropped_items": sum(bool(l.get("budgetDropped")) for l in rows),
                "prompt_p50": p50(pt), "prompt_max": max(pt), "dprompt_vs_c1_p50": p50(dt), "dprompt_vs_c1_max": max(dt),
                "changed_vs_c1": sum([x["chunkId"] for x in D[c][i][1]["kept"]] != [x["chunkId"] for x in D["c1"][i][1]["kept"]] or D[c][i][1]["promptSha"] != D["c1"][i][1]["promptSha"] for i in ids),
                "health_fail": hf}
    x = cells[c]; x["pass"] = x["dF_vs_c1"] >= 15 and x["dprompt_vs_c1_p50"] <= 900 and hf == 0
res["cells"] = cells
idok = i1 == 180 and i2 >= 170 and i3 >= 178
P = [c for c in CELLS if cells[c]["pass"]]
best = sorted(P, key=lambda c: (-cells[c]["F"], cells[c]["prompt_p50"]))[0] if P and idok else None
res["identity_ok"] = idok; res["best"] = best; res["verdict"] = "PASS" if best else "FAIL"
json.dump(res, open(f"{L}/aggregates/step0.json", "w"), indent=1)
print(json.dumps(res["identity"]))
print("cell  env        F  dF  fic  art  kept  app  fired  bdrop  p50   max   dp50  dmax  chg  hf  pass")
for c in CELLS:
    x = cells[c]; print(f"{c:5s} {x['env_budget/D/cap']:9s} {x['F']:3d} {x['dF_vs_c1']:+3d} {x['fic']:4d} {x['articles_kept_mean']:4.2f} {x['kept_chunks_mean']:5.2f} {x['appended_chunks']:4d} {x['fired']:5d} {x['budget_dropped_items']:5d} {x['prompt_p50']:6.1f} {x['prompt_max']:5d} {x['dprompt_vs_c1_p50']:+6.1f} {x['dprompt_vs_c1_max']:+5d} {x['changed_vs_c1']:4d} {x['health_fail']:3d} {x['pass']}  lost={len(x['lost_vs_c1'])} fam={x['gained_family']}")
print("VERDICT", res["verdict"], "best", best)
