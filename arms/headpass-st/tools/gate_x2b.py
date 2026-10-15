"""HEADPASS-X2b step 0 gate (HEADPASS-X2-criterion-addendum-1.md sha a66a3b79...; base criterion 1b70f6f3...; 0 LLM / 0 judge / 0 paid).

gate_x2.py extended to the x2b cells (tools/run_x2.sh phases x2b, v01b, v02b; modes off,x1,x2,x2b,off2 in the x2b tree):
  runs-x2/st-<pack>.x2b.jsonl, runs-x2/v01-kit.x2b.jsonl, runs-x2/v01-sw.x2b.jsonl; references as gate_x2.py
  (runs/st-<pack>.ref.jsonl = S, runs/st-<pack>.hp.jsonl = X1) plus runs-x2/st-<pack>.x2.jsonl (X2 as gated, R73).
Identity: off == S, x1 == X1, x2 (re-run in the x2b tree) == X2, off == off2, all on the full line key of gate_x2.py.
Gates (unchanged bars): G1 present_x2b >= 102/180 AND >= X1 per family; G2 kit v0.1/v0.2 x2b == off, v0.1 + simplewiki
lost-context 0 and gold kept x2b >= off, health-strict appended failing onHealthTopic 0; G3 cost p50 x2b <= 2 x S, simplewiki
dense scan p50 <= 300 ms, prompt tokens p50 x2b <= S + 600 (also per item: max x2b - S reported; must be <= 600 by construction).
Budget drops: chunk ids in headpass:budget:dropped:*; fact = an oracle fact chunk of the item's own pack.
Splits: vs S (as gate_x2.py) and vs X2 (identical prompt / both present / fact lost vs X2 / fact gained vs X2 / other changed).
Writes aggregates/gate-x2b.json, runs-x2/split-x2b.jsonl, aggregates/x2b-section.md (appended to X2-GATE.md by hand).
Usage: python3 -I gate_x2b.py   |   python3 -I gate_x2b.py --v02-counts <blind file>  (counts only; script-only)
"""
import json, re, os, sys, collections, statistics as stt
ROOT = "$BOAR_WS"; A = f"{ROOT}/rnd/research/coordinator/arms/headpass-st"; O = f"{A}/runs-x2"; AG = f"{A}/aggregates"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
FAM = {p: ("SE" if p.startswith("qa-") else "topic") for p in PACKS}
NAMES = ["off", "x1", "x2", "x2b", "off2"]
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
num = lambda c: int(c.rsplit(":", 1)[1])
def own(ids, p): return {int(m.group(2)) for x in ids for m in [CID.match(x or "")] if m and m.group(1) == p}
full = lambda l: json.dumps([[[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]],
                             [[x.get("chunkId"), x.get("title"), x.get("section")] for x in l["kept"]], l.get("promptSha"), l["task"], l["query"], l["k"]])
def p50(xs):
    xs = [x for x in xs if x is not None]
    return round(stt.median(xs), 1) if xs else None
cost = lambda l: None if l["ms"] is None and l["keepMs"] is None else (l["ms"] or 0) + (l["keepMs"] or 0)
def passes(f, names):
    out, seen = {}, collections.Counter()
    for l in load(f):
        n = seen[l["id"]]; seen[l["id"]] += 1; out.setdefault(names[n], {})[l["id"]] = l
    for nm, d in out.items():
        want = "off" if nm.startswith("off") else nm
        assert all(l["mode"] == want for l in d.values()), (f, nm)
    return out

if "--v02-counts" in sys.argv:  # blind: counts only, nothing printed but the counts
    f = sys.argv[sys.argv.index("--v02-counts") + 1]
    C = passes(f, NAMES); ids = list(C["off"])
    res = {"n": len(ids), **{f"{m}_vs_off_identical": sum(full(C[m][i]) == full(C["off"][i]) for i in ids) for m in ("x1", "x2", "x2b", "off2")},
           "x2b_fired": sum(bool(C["x2b"][i].get("appended")) for i in ids), "x2b_budget_dropped": sum(len(C["x2b"][i].get("budgetDropped") or []) for i in ids)}
    json.dump(res, open(f"{AG}/v02-kit-counts.x2b.json", "w")); print(json.dumps(res)); sys.exit(0)

FACTS = json.load(open(f"{ROOT}/rnd/research/coordinator/arms/oracle-st/tools/oracle-facts.json"))
res = {"criterion_sha256": open(f"{A}/HEADPASS-X2-criterion.sha256").read().split()[0],
       "addendum1_sha256": open(f"{A}/HEADPASS-X2-criterion-addendum-1.sha256").read().split()[0]}
st, rows, unreached, ident = {}, [], collections.Counter(), collections.Counter()
costs = {"S": [], "x2": [], "x2b": []}; ptok = {"S": [], "x2": [], "x2b": []}; dtok = []; sw_scan = []
health_fail = health_checked = 0
for p in PACKS:
    f = f"{O}/st-{p}.x2b.jsonl"
    if not os.path.exists(f): continue
    C = passes(f, NAMES); ref = {l["id"]: l for l in load(f"{A}/runs/st-{p}.ref.jsonl")}
    hp = passes(f"{A}/runs/st-{p}.hp.jsonl", ["off", "x1", "off2"]); old = passes(f"{O}/st-{p}.x2.jsonl", ["off", "x1", "x2", "off2"]); ids = list(ref)
    s = collections.Counter(n=len(ids))
    for i in ids:
        ident["n"] += 1; ident["off_vs_S"] += full(C["off"][i]) == full(ref[i]); ident["x1_vs_X1"] += full(C["x1"][i]) == full(hp["x1"][i])
        ident["x2_vs_X2"] += full(C["x2"][i]) == full(old["x2"][i]) and C["x2"][i].get("appended") == old["x2"][i].get("appended")
        ident["off_vs_off2"] += full(C["off"][i]) == full(C["off2"][i])
        fcs = {num(x) for x in FACTS[i]["fact_chunks"]}; S, X1, X2, B = ref[i], hp["x1"][i], old["x2"][i], C["x2b"][i]
        pres = lambda l: bool(fcs & own([x["chunkId"] for x in l["kept"]], p))
        pS, pX1, pX2, pB = pres(S), pres(X1), pres(X2), pres(B)
        cands = own([x["chunkId"] for x in B.get("denseCands") or []], p); raw = own([x["chunkId"] for x in B["raw"]], p)
        appX1 = own(B.get("appendedX1") or [], p); appD = own(B.get("appendedDense") or [], p); drop = B.get("budgetDropped") or []
        s["present_S"] += pS; s["present_X1"] += pX1; s["present_X2"] += pX2; s["present_x2b"] += pB
        s["reach_x2b"] += bool(fcs & (raw | appX1 | appD | cands)); s["dense_fact_cand"] += bool(fcs & cands)
        s["fire_x2b"] += bool(B.get("appended")); s["fire_dense"] += bool(appD); s["appended_x2b"] += len(B.get("appended") or [])
        s["appended_dense"] += len(appD); s["appended_x1"] += len(appX1); s["nosidecar"] += "headpass:dense:nosidecar" in (B.get("denseCodes") or [])
        s["budget_items"] += bool(drop); s["budget_dropped"] += len(drop)
        dfact = fcs & own(drop, p); s["budget_dropped_fact_chunks"] += len(dfact); s["budget_dropped_fact_items"] += bool(dfact)
        s["budget_dropped_fact_items_absent"] += bool(dfact) and not pB
        s["lost_kept_vs_S"] += bool({x["chunkId"] for x in S["kept"]} - {x["chunkId"] for x in B["kept"]})
        for h in B.get("hpHealth") or []: health_checked += 1; health_fail += not h["ok"]
        if B["promptSha"] == S["promptSha"] and [x["chunkId"] for x in B["kept"]] == [x["chunkId"] for x in S["kept"]]: k = "unchanged"
        elif pB and pX1: k = "present_x1"
        elif pB and not pS: k = "newly_present_x2b"
        elif B.get("appended") and not pB: k = "nonfact_only"
        else: k = "other_changed"
        s[f"split_{k}"] += 1
        if B["promptSha"] == X2["promptSha"] and [x["chunkId"] for x in B["kept"]] == [x["chunkId"] for x in X2["kept"]]: k2 = "identical_to_x2"
        elif pB and pX2: k2 = "both_present"
        elif pX2 and not pB: k2 = "fact_lost_vs_x2"
        elif pB and not pX2: k2 = "fact_gained_vs_x2"
        else: k2 = "other_changed"
        s[f"vsx2_{k2}"] += 1
        if not pB:
            have = {x["chunkId"] for x in B["kept"]} | set(B.get("appendedX1") or []) | set(drop)
            if not B["raw"]: c = "no_retrieval"
            elif dfact: c = "fact_budget_dropped"
            elif "headpass:dense:nosidecar" in (B.get("denseCodes") or []): c = "nosidecar"
            elif fcs & cands:
                picks = own([x["chunkId"] for x in B["denseCands"] if x["chunkId"] not in have][:2], p)
                c = "fact_dense_health_dropped" if fcs & picks else "fact_in_cands_beyond_D"
            elif fcs & raw: c = "fact_in_raw_dropped_by_keep"
            elif B.get("denseCands"): c = "cands_without_fact"
            else: c = "no_dense_cands"
            unreached[c] += 1; unreached[f"{FAM[p]}:{c}"] += 1
        costs["S"].append(cost(C["off2"][i])); costs["x2"].append(cost(C["x2"][i])); costs["x2b"].append(cost(B))
        ptok["S"].append(C["off2"][i].get("promptTokens")); ptok["x2"].append(C["x2"][i].get("promptTokens")); ptok["x2b"].append(B.get("promptTokens"))
        if B.get("promptTokens") is not None and C["off"][i].get("promptTokens") is not None: dtok.append(B["promptTokens"] - C["off"][i]["promptTokens"])
        if p == "boar-simplewiki-en" and B.get("denseMs") is not None: sw_scan.append(B["denseMs"])
        rows.append({"pack": p, "family": FAM[p], "id": i, "split_vs_S": k, "split_vs_x2": k2, "S_present": pS, "X1_present": pX1, "x2_present": pX2,
                     "x2b_present": pB, "appendedX1": B.get("appendedX1") or [], "appendedDense": B.get("appendedDense") or [], "budgetDropped": drop,
                     "budget_dropped_fact": bool(dfact), "dtok": dtok[-1] if dtok else None})
    st[p] = dict(s)
complete = len(st) == len(PACKS)
tot = collections.Counter()
for p in st: tot.update(st[p])
fam = {F: {k: sum(st[p].get(k, 0) for p in st if FAM[p] == F) for k in ("n", "present_S", "present_X1", "present_X2", "present_x2b", "reach_x2b", "budget_dropped", "budget_dropped_fact_items")} for F in ("SE", "topic")}
res.update(per_pack=st, st180=dict(tot), family=fam, identity=dict(ident), unreached_D0=dict(unreached), health={"checked_180": health_checked})
res["timing"] = {"cost_p50": {k: p50(v) for k, v in costs.items()}, "ptok_p50": {k: p50(v) for k, v in ptok.items()},
                 "ptok_delta_max": max(dtok) if dtok else None, "ptok_delta_p50": p50(dtok), "ptok_delta_over_600": sum(d > 600 for d in dtok),
                 "simplewiki_dense_scan_p50_ms": p50(sw_scan), "simplewiki_dense_scan_max_ms": max(sw_scan) if sw_scan else None}
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).lower(); bare = lambda t: _LIB.sub("", str(t or ""))
def gmatch(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
G = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list) and v}
for cellname in ("v01-kit", "v01-sw"):
    f = f"{O}/{cellname}.x2b.jsonl"
    if not os.path.exists(f): continue
    C = passes(f, NAMES); ids = list(C["off"]); o = {"n": len(ids)}
    for c in ("off", "x2", "x2b"):
        L = C[c]
        o[c] = {"gold_kept": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["kept"]) for i in G if i in L),
                "fire": sum(bool(l.get("appended")) for l in L.values()), "appended": sum(len(l.get("appended") or []) for l in L.values()),
                "budget_dropped": sum(len(l.get("budgetDropped") or []) for l in L.values()),
                "health_fail": sum(1 for l in L.values() for x in l.get("hpHealth") or [] if not x["ok"]),
                "cost_p50": p50([cost(l) for l in L.values()]), "ptok_p50": p50([l.get("promptTokens") for l in L.values()]),
                "dense_scan_p50_ms": p50([l.get("denseMs") for l in L.values()])}
    health_fail += o["x2b"]["health_fail"]
    o["x2b_vs_off_identical"] = sum(full(C["x2b"][i]) == full(C["off"][i]) for i in ids)
    o["off_vs_off2_identical"] = sum(full(C["off2"][i]) == full(C["off"][i]) for i in ids)
    o["lost_context_x2b"] = [i for i in ids if {x["chunkId"] for x in C["off"][i]["kept"]} - {x["chunkId"] for x in C["x2b"][i]["kept"]}]
    fired = [i for i in ids if C["x2b"][i].get("appended")]
    o["added_ptok_fired_p50"] = p50([C["x2b"][i]["promptTokens"] - C["off"][i]["promptTokens"] for i in fired if C["x2b"][i]["promptTokens"] and C["off"][i]["promptTokens"]])
    o["added_ptok_max"] = max([C["x2b"][i]["promptTokens"] - C["off"][i]["promptTokens"] for i in ids if C["x2b"][i]["promptTokens"] and C["off"][i]["promptTokens"]] or [0])
    res[cellname] = o
v02 = json.load(open(f"{AG}/v02-kit-counts.x2b.json")) if os.path.exists(f"{AG}/v02-kit-counts.x2b.json") else None
res["v02-kit"] = v02; res["health"]["fail_all"] = health_fail
g = {}; t = res["timing"]
if complete:
    g["G1_present"] = tot["present_x2b"] >= 102 and all(fam[F]["present_x2b"] >= fam[F]["present_X1"] for F in fam)
    g["G3_cost"] = t["cost_p50"]["x2b"] <= 2.0 * t["cost_p50"]["S"]
    g["G3_ptok"] = t["ptok_p50"]["x2b"] <= t["ptok_p50"]["S"] + 600
    g["G3_sw_scan"] = t["simplewiki_dense_scan_p50_ms"] is not None and t["simplewiki_dense_scan_p50_ms"] <= 300
if "v01-kit" in res: g["G2_kit_v01"] = res["v01-kit"]["x2b_vs_off_identical"] == res["v01-kit"]["n"]
if v02: g["G2_kit_v02"] = v02["x2b_vs_off_identical"] == v02["n"]
if "v01-sw" in res:
    g["G2_sw_lost_context"] = not res["v01-sw"]["lost_context_x2b"]
    g["G2_sw_gold_kept"] = res["v01-sw"]["x2b"]["gold_kept"] >= res["v01-sw"]["off"]["gold_kept"]
if complete and "v01-sw" in res: g["G2_health"] = health_fail == 0
needed = ["G1_present", "G2_kit_v01", "G2_kit_v02", "G2_sw_lost_context", "G2_sw_gold_kept", "G2_health", "G3_cost", "G3_ptok", "G3_sw_scan"]
res["gates"] = g; res["missing_inputs"] = [k for k in needed if k not in g]
res["verdict"] = "FAIL" if any(v is False for v in g.values()) else "PASS" if not res["missing_inputs"] else "INCOMPLETE"
json.dump(res, open(f"{AG}/gate-x2b.json", "w"), indent=1)
with open(f"{O}/split-x2b.jsonl", "w") as fh:
    for r in rows: fh.write(json.dumps(r) + "\n")
print(json.dumps({k: res[k] for k in ("verdict", "gates", "missing_inputs", "identity")}))
