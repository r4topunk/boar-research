"""HEADPASS-X2 step 0 gate (criterion HEADPASS-X2-criterion.md sha 1b70f6f3...; 0 LLM / 0 judge / 0 paid).

Inputs (all public; written by tools/run_x2.sh):
  runs-x2/st-<pack>.id.jsonl   identity cell (-x2 tree, --no-sidecars): passes off, x1, off2
  runs-x2/st-<pack>.x2.jsonl   X2 cell (-x2 tree, item pack = sidecar copy): passes off, x1, x2, off2
  runs-x2/v01-kit.x2.jsonl, runs-x2/v01-sw.x2.jsonl   no-harm cells: passes off, x1, x2, off2
  runs/st-<pack>.ref.jsonl     S reference = HEADPASS-ST REF (pristine cut 7 = tk2off tree, off)
  runs/st-<pack>.hp.jsonl      X1 reference = HEADPASS-ST HP cell (passes off, x1, off2)
  aggregates/v02-kit-counts.json (counts only, written by --v02-counts; optional)
Definitions (as tools/compare_hp.py): fact chunks = oracle-st/tools/oracle-facts.json fact_chunks of the item's own pack;
present = fact chunk in the sources event (kept + appended); reach = fact chunk in raw | appended | dense candidates;
identity = raw (chunkId, title, section, source, similarity, via), kept (chunkId, title, section), promptSha, task, query, k;
cost = retrieve ms + keepMs (engine: first retrieve return -> sources event; includes the X2 append step; the dense scan is
inside retrieve ms); S timing = the warm off2 pass of the same cell.
Gates: G1 present_x2 >= 102/180 AND present_x2 >= present_X1 per family (SE, topic);
       G2 v0.1 kit-only x2 == off 60/60 (and v0.2 counts when present: x2 == off n/n), v0.1 + simplewiki lost-context 0,
          gold kept x2 >= off, health-strict appended chunks failing onHealthTopic = 0 (180 + v0.1 cells);
       G3 cost p50 x2 <= 2.0 x S, simplewiki dense scan p50 <= 300 ms, prompt tokens p50 x2 <= S + 600.
Split (x2 vs S, disjoint, declared): unchanged / present_x1 (fact present under X1 already) / newly_present_x2 (absent in
S and X1, present under X2) / nonfact_only (chunks appended, no fact present) / other_changed.
Writes aggregates/gate-x2.json, aggregates/identity-x2.json, runs-x2/split-x2.jsonl, X2-GATE.md (skeleton, numbers filled
where the inputs exist). Usage: python3 -I gate_x2.py   |   python3 -I gate_x2.py --v02-counts <blind file>  (counts only)
"""
import json, re, os, sys, collections, statistics as stt
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/headpass-st"
_arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
O = _arg("--runs", f"{A}/runs-x2")    # smoke tests only: another runs dir
AG = _arg("--outdir", f"{A}/aggregates")  # ... and another output dir (X2-GATE.md then goes there too)
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
FAM = {p: ("SE" if p.startswith("qa-") else "topic") for p in PACKS}
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
    """Split a multi-pass file into {pass name: {id: line}} by occurrence order; checks each pass's mode."""
    out, seen = {}, collections.Counter()
    for l in load(f):
        n = seen[l["id"]]; seen[l["id"]] += 1; out.setdefault(names[n], {})[l["id"]] = l
    for nm, d in out.items():
        want = "off" if nm.startswith("off") else nm
        assert all(l["mode"] == want for l in d.values()), (f, nm)
    return out

# ---------------------------------------------------------------- v0.2 counts only (blind; script-only)
if "--v02-counts" in sys.argv:
    f = sys.argv[sys.argv.index("--v02-counts") + 1]
    C = passes(f, ["off", "x1", "x2", "off2"]); ids = list(C["off"])
    res = {"n": len(ids), "x1_vs_off_identical": sum(full(C["x1"][i]) == full(C["off"][i]) for i in ids),
           "x2_vs_off_identical": sum(full(C["x2"][i]) == full(C["off"][i]) for i in ids),
           "off_vs_off2_identical": sum(full(C["off2"][i]) == full(C["off"][i]) for i in ids),
           "x2_fired": sum(bool(C["x2"][i].get("appended")) for i in ids)}
    json.dump(res, open(f"{AG}/v02-kit-counts.json", "w")); print(json.dumps(res)); sys.exit(0)

FACTS = json.load(open(f"{ROOT}/rnd/research/coordinator/arms/oracle-st/tools/oracle-facts.json"))
res = {"criterion_sha256": open(f"{A}/HEADPASS-X2-criterion.sha256").read().split()[0]}

# ---------------------------------------------------------------- identity cell (no sidecars): off = cut 7, x1 = X1
ident = {}
for p in PACKS:
    f = f"{O}/st-{p}.id.jsonl"
    if not os.path.exists(f): continue
    C = passes(f, ["off", "x1", "off2"]); ref = {l["id"]: l for l in load(f"{A}/runs/st-{p}.ref.jsonl")}
    hp = passes(f"{A}/runs/st-{p}.hp.jsonl", ["off", "x1", "off2"]); ids = list(ref)
    ident[p] = {"n": len(ids), "off_vs_cut7": sum(full(C["off"][i]) == full(ref[i]) for i in ids),
                "x1_vs_X1": sum(full(C["x1"][i]) == full(hp["x1"][i]) for i in ids),
                "x1_kept_vs_X1": sum([x["chunkId"] for x in C["x1"][i]["kept"]] == [x["chunkId"] for x in hp["x1"][i]["kept"]] for i in ids),
                "x1_appended_vs_X1": sum(C["x1"][i].get("appended") == hp["x1"][i].get("appended") for i in ids),
                "off_vs_off2": sum(full(C["off"][i]) == full(C["off2"][i]) for i in ids),
                "diff_ids": [i for i in ids if full(C["off"][i]) != full(ref[i]) or full(C["x1"][i]) != full(hp["x1"][i])]}
if ident:
    ident["total"] = {k: sum(v[k] for v in ident.values()) for k in ("n", "off_vs_cut7", "x1_vs_X1", "x1_kept_vs_X1", "x1_appended_vs_X1", "off_vs_off2")}
    json.dump(ident, open(f"{AG}/identity-x2.json", "w"), indent=1)
res["identity"] = ident.get("total")

# ---------------------------------------------------------------- the 180 under X2
st, split_rows, unreached = {}, [], collections.Counter()
costs = {"S": [], "x1": [], "x2": []}; ptok = {"S": [], "x1": [], "x2": []}; health_fail = health_checked = 0
sw_scan = []
for p in PACKS:
    f = f"{O}/st-{p}.x2.jsonl"
    if not os.path.exists(f): continue
    C = passes(f, ["off", "x1", "x2", "off2"]); ref = {l["id"]: l for l in load(f"{A}/runs/st-{p}.ref.jsonl")}
    hp = passes(f"{A}/runs/st-{p}.hp.jsonl", ["off", "x1", "off2"]); ids = list(ref)
    s = collections.Counter(n=len(ids))
    for i in ids:
        fcs = {num(x) for x in FACTS[i]["fact_chunks"]}; S, X1, X1c, X2 = ref[i], hp["x1"][i], C["x1"][i], C["x2"][i]
        pres = lambda l: bool(fcs & own([x["chunkId"] for x in l["kept"]], p))
        pS, pX1, pX2 = pres(S), pres(X1), pres(X2)
        cands = own([x["chunkId"] for x in X2.get("denseCands") or []], p); appD = own(X2.get("appendedDense") or [], p)
        appX1 = own(X2.get("appendedX1") or [], p); raw = own([x["chunkId"] for x in X2["raw"]], p)
        s["present_S"] += pS; s["present_X1"] += pX1; s["present_x1_cell"] += pres(X1c); s["present_x2"] += pX2
        s["reach_x2"] += bool(fcs & (raw | appX1 | appD | cands)); s["dense_fact_cand"] += bool(fcs & cands); s["dense_fact_appended"] += bool(fcs & appD)
        s["fire_x2"] += bool(X2.get("appended")); s["fire_dense"] += bool(appD); s["appended_x2"] += len(X2.get("appended") or [])
        s["appended_dense"] += len(appD); s["nosidecar"] += "headpass:dense:nosidecar" in (X2.get("denseCodes") or [])
        s["x1_cell_vs_X1"] += full(X1c) == full(X1); s["off_vs_cut7"] += full(C["off"][i]) == full(S)
        s["lost_kept_vs_S"] += bool({x["chunkId"] for x in S["kept"]} - {x["chunkId"] for x in X2["kept"]})
        for h in X2.get("hpHealth") or []: health_checked += 1; health_fail += not h["ok"]
        if X2["promptSha"] == S["promptSha"] and [x["chunkId"] for x in X2["kept"]] == [x["chunkId"] for x in S["kept"]]: k = "unchanged"
        elif pX2 and pX1: k = "present_x1"
        elif pX2 and not pS: k = "newly_present_x2"
        elif X2.get("appended") and not pX2: k = "nonfact_only"
        else: k = "other_changed"
        s[f"split_{k}"] += 1
        split_rows.append({"pack": p, "family": FAM[p], "id": i, "split": k, "S_present": pS, "X1_present": pX1, "x2_present": pX2,
                           "appendedX1": X2.get("appendedX1") or [], "appendedDense": X2.get("appendedDense") or [],
                           "fact_in_cands": bool(fcs & cands), "n_cands": len(X2.get("denseCands") or [])})
        if not pX2:  # D0 classes of the still-unreached
            if not X2["raw"]: c = "no_retrieval"
            elif "headpass:dense:nosidecar" in (X2.get("denseCodes") or []): c = "nosidecar"
            elif fcs & cands:
                have = {x["chunkId"] for x in X2["kept"]} | set(X2.get("appendedX1") or [])
                picks = own([x["chunkId"] for x in X2["denseCands"] if x["chunkId"] not in have][:2], p)
                c = "fact_dense_health_dropped" if fcs & picks else "fact_in_cands_beyond_D"
            elif fcs & raw: c = "fact_in_raw_dropped_by_keep"
            elif X2.get("denseCands"): c = "cands_without_fact"
            else: c = "no_dense_cands"
            unreached[f"{FAM[p]}:{c}"] += 1; unreached[c] += 1
        costs["S"].append(cost(C["off2"][i])); costs["x1"].append(cost(X1c)); costs["x2"].append(cost(X2))
        ptok["S"].append(C["off2"][i].get("promptTokens")); ptok["x1"].append(X1c.get("promptTokens")); ptok["x2"].append(X2.get("promptTokens"))
        if p == "boar-simplewiki-en" and X2.get("denseMs") is not None: sw_scan.append(X2["denseMs"])
    st[p] = dict(s)
res["per_pack"] = st
fam = {}
for F in ("SE", "topic"):
    ps = [p for p in st if FAM[p] == F]; fam[F] = {k: sum(st[p].get(k, 0) for p in ps) for k in ("n", "present_S", "present_X1", "present_x2", "reach_x2", "fire_x2", "fire_dense")}
tot = collections.Counter()
for p in st: tot.update(st[p])
res["st180"] = dict(tot); res["family"] = fam; res["unreached_D0"] = dict(unreached)
if len(st) != len(PACKS): fam = {}
res["timing"] = {"cost_p50": {k: p50(v) for k, v in costs.items()}, "ptok_p50": {k: p50(v) for k, v in ptok.items()},
                 "simplewiki_dense_scan_p50_ms": p50(sw_scan), "simplewiki_dense_scan_max_ms": max(sw_scan) if sw_scan else None}

# ---------------------------------------------------------------- v0.1 no-harm cells
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).lower(); bare = lambda t: _LIB.sub("", str(t or ""))
def gmatch(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
G = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list) and v}
for cellname in ("v01-kit", "v01-sw"):
    f = f"{O}/{cellname}.x2.jsonl"
    if not os.path.exists(f): continue
    C = passes(f, ["off", "x1", "x2", "off2"]); ids = list(C["off"]); o = {"n": len(ids)}
    for c in ("off", "x1", "x2"):
        L = C[c]
        o[c] = {"gold_kept": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["kept"]) for i in G if i in L),
                "fire": sum(bool(l.get("appended")) for l in L.values()), "fire_dense": sum(bool(l.get("appendedDense")) for l in L.values()),
                "appended": sum(len(l.get("appended") or []) for l in L.values()),
                "health_fail": sum(1 for l in L.values() for x in l.get("hpHealth") or [] if not x["ok"]),
                "cost_p50": p50([cost(l) for l in L.values()]), "ptok_p50": p50([l.get("promptTokens") for l in L.values()]),
                "dense_scan_p50_ms": p50([l.get("denseMs") for l in L.values()])}
        health_fail += o[c]["health_fail"] if c == "x2" else 0
    o["x2_vs_off_identical"] = sum(full(C["x2"][i]) == full(C["off"][i]) for i in ids)
    o["x1_vs_off_identical"] = sum(full(C["x1"][i]) == full(C["off"][i]) for i in ids)
    o["off_vs_off2_identical"] = sum(full(C["off2"][i]) == full(C["off"][i]) for i in ids)
    o["lost_context_x2"] = [i for i in ids if {x["chunkId"] for x in C["off"][i]["kept"]} - {x["chunkId"] for x in C["x2"][i]["kept"]}]
    fired = [i for i in ids if C["x2"][i].get("appended")]
    o["added_ptok_fired_p50"] = p50([(C["x2"][i]["promptTokens"] or 0) - (C["off"][i]["promptTokens"] or 0) for i in fired if C["x2"][i]["promptTokens"] and C["off"][i]["promptTokens"]])
    res[cellname] = o
v02 = json.load(open(f"{AG}/v02-kit-counts.json")) if os.path.exists(f"{AG}/v02-kit-counts.json") else None
res["v02-kit"] = v02

# ---------------------------------------------------------------- gates
complete = len(st) == len(PACKS)
g = {}
if complete:
    fam = res["family"]
    g["G1_present"] = tot["present_x2"] >= 102 and all(fam[F]["present_x2"] >= fam[F]["present_X1"] for F in fam)
t = res["timing"]
if complete and t["cost_p50"]["S"]:
    g["G3_cost"] = t["cost_p50"]["x2"] <= 2.0 * t["cost_p50"]["S"]
    g["G3_ptok"] = t["ptok_p50"]["x2"] is not None and t["ptok_p50"]["x2"] <= t["ptok_p50"]["S"] + 600
    g["G3_sw_scan"] = t["simplewiki_dense_scan_p50_ms"] is not None and t["simplewiki_dense_scan_p50_ms"] <= 300
if "v01-kit" in res: g["G2_kit_v01"] = res["v01-kit"]["x2_vs_off_identical"] == res["v01-kit"]["n"]
if v02: g["G2_kit_v02"] = v02["x2_vs_off_identical"] == v02["n"]
if "v01-sw" in res:
    g["G2_sw_lost_context"] = not res["v01-sw"]["lost_context_x2"]
    g["G2_sw_gold_kept"] = res["v01-sw"]["x2"]["gold_kept"] >= res["v01-sw"]["off"]["gold_kept"]
if complete and "v01-sw" in res: g["G2_health"] = health_fail == 0
res["health"] = {"checked_180": health_checked, "fail_all": health_fail}
needed = ["G1_present", "G2_kit_v01", "G2_kit_v02", "G2_sw_lost_context", "G2_sw_gold_kept", "G2_health", "G3_cost", "G3_ptok", "G3_sw_scan"]
res["gates"] = g; res["missing_inputs"] = [k for k in needed if k not in g]
res["verdict"] = ("FAIL" if any(v is False for v in g.values()) else "PASS" if not res["missing_inputs"] else "INCOMPLETE")
json.dump(res, open(f"{AG}/gate-x2.json", "w"), indent=1)
with open(f"{O}/split-x2.jsonl", "w") as fh:
    for r in split_rows: fh.write(json.dumps(r) + "\n")

# ---------------------------------------------------------------- X2-GATE.md skeleton
v = lambda x: "pending" if x is None else x
T = res["st180"]; sp = {k[6:]: T.get(k, 0) for k in T if k.startswith("split_")}
md = f"""# HEADPASS-X2 step 0 gate (criterion HEADPASS-X2-criterion.md sha {res['criterion_sha256'][:8]}...; 0 LLM / 0 judge / 0 paid)

Generated by tools/gate_x2.py from runs-x2/ (aggregates/gate-x2.json). **Verdict: {res['verdict']}**{'' if not res['missing_inputs'] else ' (missing: ' + ', '.join(res['missing_inputs']) + ')'}.

Tree kiln-local/be-0cfd4a77-cut7-headpass-x2 = cut 7 + headpass-x2.vs-cut7.patch (+ env-gated prompt dump). Identity cell (no sidecars):
{json.dumps(res['identity']) if res['identity'] else 'pending'}.

| Gate | Rule | Value | Pass |
|---|---|---|---|
| G1 | fact present x2 >= 102/180 | {v(T.get('present_x2') if complete else None)} (S {v(T.get('present_S') if complete else None)}, X1 {v(T.get('present_X1') if complete else None)}) | {v(g.get('G1_present'))} |
| G1 | >= X1 per family | SE {v(fam.get('SE', {}).get('present_x2'))} vs {v(fam.get('SE', {}).get('present_X1'))}; topic {v(fam.get('topic', {}).get('present_x2'))} vs {v(fam.get('topic', {}).get('present_X1'))} | (in G1) |
| G2 | v0.1 kit-only x2 == off | {v(res.get('v01-kit', {}).get('x2_vs_off_identical'))}/{v(res.get('v01-kit', {}).get('n'))} | {v(g.get('G2_kit_v01'))} |
| G2 | v0.2 kit-only x2 == off (counts) | {v(v02 and v02['x2_vs_off_identical'])}/{v(v02 and v02['n'])} | {v(g.get('G2_kit_v02'))} |
| G2 | v0.1 + simplewiki lost-context | {v(len(res['v01-sw']['lost_context_x2']) if 'v01-sw' in res else None)} | {v(g.get('G2_sw_lost_context'))} |
| G2 | v0.1 + simplewiki gold kept x2 >= off | {v(res.get('v01-sw', {}).get('x2', {}).get('gold_kept'))} vs {v(res.get('v01-sw', {}).get('off', {}).get('gold_kept'))} | {v(g.get('G2_sw_gold_kept'))} |
| G2 | health-strict appended failing onHealthTopic | {health_fail} (checked {health_checked} on the 180) | {v(g.get('G2_health'))} |
| G3 | cost p50 x2 <= 2.0 x S | {v(t['cost_p50']['x2'])} vs S {v(t['cost_p50']['S'])} ms | {v(g.get('G3_cost'))} |
| G3 | simplewiki dense scan p50 <= 300 ms | {v(t['simplewiki_dense_scan_p50_ms'])} (max {v(t['simplewiki_dense_scan_max_ms'])}) | {v(g.get('G3_sw_scan'))} |
| G3 | prompt tokens p50 <= S + 600 | {v(t['ptok_p50']['x2'])} vs S {v(t['ptok_p50']['S'])} | {v(g.get('G3_ptok'))} |

Declared split denominators (x2 vs S, disjoint): newly present under X2 {sp.get('newly_present_x2', 0) if complete else 'pending'}; present under X1 already {sp.get('present_x1', 0) if complete else 'pending'}; non-fact only {sp.get('nonfact_only', 0) if complete else 'pending'}; unchanged {sp.get('unchanged', 0) if complete else 'pending'}; other changed {sp.get('other_changed', 0) if complete else 'pending'}.

Reach x2 (raw | appended | dense candidates): {v(T.get('reach_x2') if complete else None)}; dense fact candidate {v(T.get('dense_fact_cand') if complete else None)}, dense fact appended {v(T.get('dense_fact_appended') if complete else None)}; fires x2 {v(T.get('fire_x2') if complete else None)} (dense {v(T.get('fire_dense') if complete else None)}), appended {v(T.get('appended_x2') if complete else None)} (dense {v(T.get('appended_dense') if complete else None)}); nosidecar lines {v(T.get('nosidecar') if complete else None)} (must be 0).

D0 classes of the items still without the fact (x2): {json.dumps(res['unreached_D0']) if complete else 'pending'}.

## Reading
(coordinator)
"""
_g = f"{A}/X2-GATE.md" if AG == f"{A}/aggregates" else f"{AG}/X2-GATE.md"  # never clobber a gate file the coordinator has written into
if os.path.exists(_g) and not open(_g).read().rstrip().endswith("(coordinator)"): _g = f"{A}/X2-GATE.auto.md"
open(_g, "w").write(md)
print(json.dumps({k: res[k] for k in ("verdict", "gates", "missing_inputs", "identity")}))
for p in ident:
    if p != "total": print("identity", p, {k: ident[p][k] for k in ident[p] if k != "diff_ids"}, ident[p]["diff_ids"][:5])
