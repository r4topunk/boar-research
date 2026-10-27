"""HEADPASS-X3 step 0 gate (criterion HEADPASS-X3-criterion.md sha 275fe748...; 0 LLM / 0 judge / 0 paid).

Inputs (tools/run_x3.sh): runs-x3/st-<pack>.x3.jsonl (modes off,x1,x2b,x3a,x3b,off2; scores looked up), runs-x3/score-*.jsonl
(live reranker passes: rr ms/pairs per item), runs-x3/v01-{kit,sw}.x3.jsonl (off,x3a,x3b,m2,off2), runs-x3/m2-all9-
{st180,v01}.jsonl (off,m2,off2; all 9 packs + kit). References: runs/st-<pack>.ref.jsonl = S, runs/st-<pack>.hp.jsonl = X1,
runs-x2/st-<pack>.x2b.jsonl = X2b (its x2b pass), aggregates/gate-x2b.json (X2b present per family).
Identity (full line key of gate_x2.py): off == S, x1 == X1, x2b == X2b (+ appended), off == off2.
Fact chunk present = an oracle fact chunk (oracle-st/tools/oracle-facts.json) of the item's own pack in the final context
(kept = the sources event, appended chunks included). Fact article kept (M2) = packroute step0.py's art_kept (the item's
source.article_id among the kept chunks of its pack).
Gates per variant v in {x3a, x3b}: G1 present_v >= X2b present + 15 (117) AND >= X2b per family (power line: + 25 = 127);
G2 kit-only v0.1 / v0.2 v == off, v0.1 + simplewiki lost-context 0 and gold kept v >= off, health-strict appended failing
onHealthTopic 0; G3 prompt tokens p50 <= S + 600 (per item max delta vs off reported); reranker ms per item reported (LEVER
default only if p50 <= 1,000 ms, else optional). M2: fact article kept with all 9 >= 57; lost kit contexts 0 (v0.1 public
with all 9 + kit: an item with kept sources under off and none under m2; also reported: kit chunks dropped, gold kept);
kit-only v0.1 / v0.2 m2 == off. Verdict: the passing variant with the highest present enters stage 1; none -> FAIL at step 0.
Writes aggregates/gate-x3.json, runs-x3/split-x3.jsonl.
Usage: python3 -I gate_x3.py   |   python3 -I gate_x3.py --v02-counts <blind file>  (counts only; script-only)
"""
import json, re, os, sys, sqlite3, collections, statistics as stt
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/headpass-st"; O = f"{A}/runs-x3"; O2 = f"{A}/runs-x2"; AG = f"{A}/aggregates"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
FAM = {p: ("SE" if p.startswith("qa-") else "topic") for p in PACKS}
VARS = ["x3a", "x3b"]
NAMES = ["off", "x1", "x2b", "x3a", "x3b", "off2"]
KITN = ["off", "x3a", "x3b", "m2", "off2"]
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
num = lambda c: int(c.rsplit(":", 1)[1])
def own(ids, p): return {int(m.group(2)) for x in ids for m in [CID.match(x or "")] if m and m.group(1) == p}
full = lambda l: json.dumps([[[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]],
                             [[x.get("chunkId"), x.get("title"), x.get("section")] for x in l["kept"]], l.get("promptSha"), l["task"], l["query"], l["k"]])
def pq(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return None
    i = (len(xs) - 1) * q; lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (i - lo), 1)
p50 = lambda xs: pq(xs, 0.5)
cost = lambda l: None if l["ms"] is None and l["keepMs"] is None else (l["ms"] or 0) + (l["keepMs"] or 0)
def passes(f, names):
    out, seen = {}, collections.Counter()
    for l in load(f):
        n = seen[l["id"]]; seen[l["id"]] += 1; out.setdefault(names[n], {})[l["id"]] = l
    for nm, d in out.items():
        want = "off" if nm.startswith("off") else nm
        assert all(l["mode"] == want for l in d.values()), (f, nm)
    return out
keptset = lambda l: {x["chunkId"] for x in l["kept"]}

if "--v02-counts" in sys.argv:  # blind: counts only, nothing printed but the counts
    f = sys.argv[sys.argv.index("--v02-counts") + 1]
    C = passes(f, KITN); ids = list(C["off"])
    res = {"n": len(ids), **{f"{m}_vs_off_identical": sum(full(C[m][i]) == full(C["off"][i]) for i in ids) for m in ("x3a", "x3b", "m2", "off2")},
           **{f"{m}_fired": sum(bool(C[m][i].get("appended")) or "headpass:rerank:m2:fired" in (C[m][i].get("codes") or []) for i in ids) for m in ("x3a", "x3b", "m2")},
           "scorer_calls": sum(C[m][i]["rr"]["calls"] for m in ("x3a", "x3b", "m2") for i in ids)}
    json.dump(res, open(f"{AG}/v02-kit-counts.x3.json", "w")); print(json.dumps(res)); sys.exit(0)

FACTS = json.load(open(f"{ROOT}/rnd/research/coordinator/arms/oracle-st/tools/oracle-facts.json"))
X2B = json.load(open(f"{AG}/gate-x2b.json"))
X2B_PRESENT = X2B["st180"]["present_x2b"]; X2B_FAM = {F: X2B["family"][F]["present_x2b"] for F in ("SE", "topic")}
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
DB = {p: sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True) for p in PACKS}
ART = {p: dict(DB[p].execute("SELECT id, article_id FROM chunks").fetchall()) for p in PACKS}
res = {"criterion_sha256": open(f"{A}/HEADPASS-X3-criterion.sha256").read().split()[0],
       "patch_sha256": open(f"{A}/headpass-x3.vs-cut7.patch.sha256").read().split()[0],
       "x2b_reference": {"present": X2B_PRESENT, "family": X2B_FAM}}

# ------------------------------------------------------------------ live reranker timing (score-* passes)
rrs = {"x3_180": [], "m2_180": [], "x3_v01sw": [], "m2_v01sw": [], "m2_v01all9": []}
for p in PACKS:
    f = f"{O}/score-st-{p}.jsonl"
    if os.path.exists(f): rrs["x3_180"] += [(l["id"], l["rr"]) for l in load(f) if l["rr"]["calls"]]
for f, k in ((f"{O}/score-all9-st180.jsonl", "m2_180"), (f"{O}/score-all9-v01.jsonl", "m2_v01all9")):
    if os.path.exists(f): rrs[k] += [(l["id"], l["rr"]) for l in load(f) if l["rr"]["calls"]]
if os.path.exists(f"{O}/score-v01-sw.jsonl"):
    for l in load(f"{O}/score-v01-sw.jsonl"):
        if l["rr"]["calls"]: rrs["x3_v01sw" if l["mode"] == "x3a" else "m2_v01sw"].append((l["id"], l["rr"]))
rr_live = {i: r for i, r in rrs["x3_180"]}
# clean timing pass (tools/run_x3_timing.sh: 36-item subset, MacBook idle) -> the G3 number when present
clean = {"x3a": [], "m2": []}
for p in PACKS:
    f = f"{O}/timing-x3a-{p}.jsonl"
    if os.path.exists(f): clean["x3a"] += [(l["id"], l["rr"]) for l in load(f) if l["rr"]["calls"]]
if os.path.exists(f"{O}/timing-m2-all9.jsonl"): clean["m2"] += [(l["id"], l["rr"]) for l in load(f"{O}/timing-m2-all9.jsonl") if l["rr"]["calls"]]
rrs.update({f"clean_{k}": v for k, v in clean.items()})
res["rerank_latency"] = {k: {"items": len(v), "pairs_p50": p50([r["pairs"] for _, r in v]), "pairs_max": max([r["pairs"] for _, r in v] or [0]),
                             "ms_p50": p50([r["ms"] for _, r in v]), "ms_p90": pq([r["ms"] for _, r in v], 0.9),
                             "ms_per_pair_p50": p50([r["ms"] / r["pairs"] for _, r in v if r["pairs"]]), "miss": sum(r["miss"] for _, r in v)} for k, v in rrs.items()}

# ------------------------------------------------------------------ the 180, one pack installed
st = {v: {} for v in VARS}; rows = []; unreached = {v: collections.Counter() for v in VARS}; ident = collections.Counter()
costs = {"S": [], **{v: [] for v in VARS}}; costs_rr = {v: [] for v in VARS}; ptok = {"S": [], **{v: [] for v in VARS}}; dtok = {v: [] for v in VARS}
health_fail = collections.Counter(); health_checked = collections.Counter(); misses = collections.Counter(); fact_rank = {v: [] for v in VARS}
complete = all(os.path.exists(f"{O}/st-{p}.x3.jsonl") for p in PACKS)
for p in PACKS:
    f = f"{O}/st-{p}.x3.jsonl"
    if not os.path.exists(f): continue
    C = passes(f, NAMES); ref = {l["id"]: l for l in load(f"{A}/runs/st-{p}.ref.jsonl")}
    hp = passes(f"{A}/runs/st-{p}.hp.jsonl", ["off", "x1", "off2"]); xb = passes(f"{O2}/st-{p}.x2b.jsonl", ["off", "x1", "x2", "x2b", "off2"]); ids = list(ref)
    for i in ids:
        ident["n"] += 1; ident["off_vs_S"] += full(C["off"][i]) == full(ref[i]); ident["x1_vs_X1"] += full(C["x1"][i]) == full(hp["x1"][i])
        ident["x2b_vs_X2b"] += full(C["x2b"][i]) == full(xb["x2b"][i]) and C["x2b"][i].get("appended") == xb["x2b"][i].get("appended")
        ident["off_vs_off2"] += full(C["off"][i]) == full(C["off2"][i])
        fcs = {num(x) for x in FACTS[i]["fact_chunks"]}; S, X1, XB = ref[i], hp["x1"][i], xb["x2b"][i]
        pres = lambda l: bool(fcs & own([x["chunkId"] for x in l["kept"]], p))
        pS, pX1, pXB = pres(S), pres(X1), pres(XB)
        row = {"pack": p, "family": FAM[p], "id": i, "S_present": pS, "X1_present": pX1, "x2b_present": pXB}
        for v in VARS:
            L = C[v][i]; pv = pres(L); s = st[v].setdefault(p, collections.Counter(n=0)); s["n"] += 1
            cands = [c for c, _ in L.get("rrCands") or []]; candset = own(cands, p); raw = own([x["chunkId"] for x in L["raw"]], p)
            appX1 = own(L.get("appendedX1") or [], p); appR = own(L.get("appendedRerank") or [], p); drop = L.get("rerankDropped") or []
            dense = own([x["chunkId"] for x in L.get("denseCands") or []], p)
            top = next((x["chunkId"] for x in L["raw"] if CID.match(x["chunkId"]) and CID.match(x["chunkId"]).group(1) == p), None)
            topart = ART[p].get(num(top)) if top else None
            s["present_S"] += pS; s["present_X1"] += pX1; s["present_x2b"] += pXB; s["present"] += pv
            s["reach"] += bool(fcs & (raw | appX1 | appR | candset)); s["fact_in_cands"] += bool(fcs & candset)
            s["fire"] += bool(L.get("appended")); s["fire_rerank"] += bool(appR); s["appended"] += len(L.get("appended") or [])
            s["appended_x1"] += len(appX1); s["appended_rerank"] += len(appR)
            s["appended_rerank_in_dense"] += len(appR & dense); s["appended_rerank_in_top_article"] += sum(ART[p].get(c) == topart for c in appR - dense)
            s["appended_rerank_bm25_only"] += sum(ART[p].get(c) != topart for c in appR - dense)
            s["appended_rerank_fact"] += len(appR & fcs)
            s["nocand"] += "headpass:rerank:nocand" in (L.get("rerankCodes") or [])
            s["health_dropped"] += sum(int(c.rsplit("-", 1)[1]) for c in L.get("rerankCodes") or [] if c.startswith("headpass:rerank:health-dropped-"))
            s["budget_items"] += bool(drop); s["budget_dropped"] += len(drop)
            dfact = fcs & own(drop, p); s["budget_dropped_fact_chunks"] += len(dfact); s["budget_dropped_fact_items"] += bool(dfact)
            s["budget_dropped_fact_items_absent"] += bool(dfact) and not pv; s["budget_dropped_nonfact"] += len(drop) - len(dfact)
            s["lost_kept_vs_S"] += bool(keptset(S) - keptset(L))
            misses[v] += L["rr"]["miss"]
            for h in L.get("hpHealth") or []: health_checked[v] += 1; health_fail[v] += not h["ok"]
            # reranker order of the candidates (score desc, ties in candidate order) -> rank of the best fact chunk
            order = [c for _, c in sorted(((-(sc if sc is not None else -1e9), k), c) for k, (c, sc) in enumerate(L.get("rrCands") or []))]
            fr = next((k for k, c in enumerate(order) if CID.match(c) and CID.match(c).group(1) == p and num(c) in fcs), None)
            if fr is not None: fact_rank[v].append(fr + 1)
            # split vs S (as X2b) and the declared split vs X2b
            unchanged = L["promptSha"] == S["promptSha"] and [x["chunkId"] for x in L["kept"]] == [x["chunkId"] for x in S["kept"]]
            k = "unchanged" if unchanged else "present_x1" if pv and pX1 else "newly_present" if pv and not pS else "nonfact_only" if L.get("appended") and not pv else "other_changed"
            s[f"splitS_{k}"] += 1
            k2 = ("unchanged" if unchanged else "newly_present_x3" if pv and not pXB else "present_x2b" if pv and pXB
                  else "nonfact_only" if L.get("appended") else "other_changed")
            s[f"split_{k2}"] += 1; s["fact_lost_vs_x2b"] += pXB and not pv; s["fact_gained_vs_x2b"] += pv and not pXB
            if not pv:
                have = keptset(L) | set(L.get("appendedX1") or [])
                if not L["raw"]: c = "no_retrieval"
                elif "headpass:rerank:nocand" in (L.get("rerankCodes") or []): c = "nocand"
                elif dfact: c = "fact_budget_dropped"
                elif fcs & candset:
                    picks = own([c for c in order if c not in have][:2], p)
                    c = "fact_rerank_health_dropped" if fcs & picks else "fact_in_cands_beyond_D"
                elif fcs & raw: c = "fact_in_raw_dropped_by_keep"
                else: c = "cands_without_fact"
                unreached[v][c] += 1; unreached[v][f"{FAM[p]}:{c}"] += 1
            if v == "x3a": costs["S"].append(cost(C["off2"][i])); ptok["S"].append(C["off2"][i].get("promptTokens"))
            costs[v].append(cost(L)); costs_rr[v].append((cost(L) or 0) + (rr_live[i]["ms"] if i in rr_live else 0)); ptok[v].append(L.get("promptTokens"))
            if L.get("promptTokens") is not None and C["off"][i].get("promptTokens") is not None: dtok[v].append(L["promptTokens"] - C["off"][i]["promptTokens"])
            row.update({f"{v}_present": pv, f"{v}_split_vs_S": k, f"{v}_split": k2, f"{v}_appended": L.get("appended") or [], f"{v}_dropped": drop,
                        f"{v}_fact_rank": fr + 1 if fr is not None else None, f"{v}_dtok": dtok[v][-1] if dtok[v] else None})
        rows.append(row)
tot = {v: collections.Counter() for v in VARS}
for v in VARS:
    for p in st[v]: tot[v].update(st[v][p])
fam = {v: {F: {k: sum(st[v][p].get(k, 0) for p in st[v] if FAM[p] == F) for k in ("n", "present_S", "present_X1", "present_x2b", "present", "reach", "budget_dropped_fact_items")} for F in ("SE", "topic")} for v in VARS}
res.update(per_pack={v: {p: dict(st[v][p]) for p in st[v]} for v in VARS}, st180={v: dict(tot[v]) for v in VARS}, family=fam, identity=dict(ident),
           unreached_D0={v: dict(unreached[v]) for v in VARS}, health={"checked_180": dict(health_checked), "fail_180": dict(health_fail)}, score_misses_180=dict(misses),
           fact_rank={v: {"items": len(fact_rank[v]), "rank1": sum(r == 1 for r in fact_rank[v]), "rank_le2": sum(r <= 2 for r in fact_rank[v]),
                          "rank_le4": sum(r <= 4 for r in fact_rank[v]), "p50": p50(fact_rank[v])} for v in VARS})
res["timing"] = {"cost_p50_engine": {k: p50(v) for k, v in costs.items()}, "cost_p50_with_rerank": {v: p50(costs_rr[v]) for v in VARS},
                 "ptok_p50": {k: p50(v) for k, v in ptok.items()},
                 "ptok_delta": {v: {"p50": p50(dtok[v]), "max": max(dtok[v]) if dtok[v] else None, "over_600": sum(d > 600 for d in dtok[v])} for v in VARS}}

# ------------------------------------------------------------------ v0.1 kit-only / + simplewiki
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).lower(); bare = lambda t: _LIB.sub("", str(t or ""))
def gmatch(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
G = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list) and v}
gold_kept = lambda L: sum(any(gmatch(g, x) for g in G[i] for x in L[i]["kept"]) for i in G if i in L)
hf_kit = 0
for cellname in ("v01-kit", "v01-sw"):
    f = f"{O}/{cellname}.x3.jsonl"
    if not os.path.exists(f): continue
    C = passes(f, KITN); ids = list(C["off"]); o = {"n": len(ids)}
    for c in ("off", "x3a", "x3b", "m2"):
        L = C[c]
        o[c] = {"gold_kept": gold_kept(L), "fire": sum(bool(l.get("appended")) for l in L.values()), "appended": sum(len(l.get("appended") or []) for l in L.values()),
                "m2_fired": sum("headpass:rerank:m2:fired" in (l.get("codes") or []) for l in L.values()),
                "rerank_dropped": sum(len(l.get("rerankDropped") or []) for l in L.values()), "scorer_misses": sum(l["rr"]["miss"] for l in L.values()),
                "health_fail": sum(1 for l in L.values() for x in l.get("hpHealth") or [] if not x["ok"]),
                "cost_p50": p50([cost(l) for l in L.values()]), "ptok_p50": p50([l.get("promptTokens") for l in L.values()])}
        if c != "off":
            hf_kit += o[c]["health_fail"]
            o[c]["vs_off_identical"] = sum(full(L[i]) == full(C["off"][i]) for i in ids)
            o[c]["lost_context"] = [i for i in ids if C["off"][i]["kept"] and not L[i]["kept"]]
            o[c]["lost_kept_chunk_items"] = sum(bool(keptset(C["off"][i]) - keptset(L[i])) for i in ids)
            o[c]["added_ptok_max"] = max([L[i]["promptTokens"] - C["off"][i]["promptTokens"] for i in ids if L[i]["promptTokens"] and C["off"][i]["promptTokens"]] or [0])
    o["off_vs_off2_identical"] = sum(full(C["off2"][i]) == full(C["off"][i]) for i in ids)
    res[cellname] = o
v02 = json.load(open(f"{AG}/v02-kit-counts.x3.json")) if os.path.exists(f"{AG}/v02-kit-counts.x3.json") else None
res["v02-kit"] = v02

# ------------------------------------------------------------------ M2: all 9 packs + kit
SRC = {}
for p in PACKS:
    for it in load(f"{ROOT}/rnd/research/packs/selftest/{p}.jsonl"): SRC[it["id"]] = (p, it["source"]["article_id"])
def art_kept(l, i):
    p, fa = SRC[i]; return any(ART[p].get(c) == fa for c in own([x["chunkId"] for x in l["kept"]], p))
def chunk_kept(l, i):
    p = SRC[i][0]; return bool({num(x) for x in FACTS[i]["fact_chunks"]} & own([x["chunkId"] for x in l["kept"]], p))
m2 = {}
f = f"{O}/m2-all9-st180.jsonl"
if os.path.exists(f):
    C = passes(f, ["off", "m2", "off2"]); ids = list(C["off"])
    m2["st180"] = {"n": len(ids), **{a: {"art_kept": sum(art_kept(C[a][i], i) for i in ids), "chunk_kept": sum(chunk_kept(C[a][i], i) for i in ids),
                                         "empty_kept": sum(not C[a][i]["kept"] for i in ids), "fired": sum("headpass:rerank:m2:fired" in (C[a][i].get("codes") or []) for i in ids),
                                         "cost_p50": p50([cost(C[a][i]) for i in ids])} for a in ("off", "m2")},
                   "art_kept_family": {F: {a: sum(art_kept(C[a][i], i) for i in ids if FAM[SRC[i][0]] == F) for a in ("off", "m2")} for F in ("SE", "topic")},
                   "lost_context": sorted(i for i in ids if C["off"][i]["kept"] and not C["m2"][i]["kept"]),
                   "art_lost": sum(art_kept(C["off"][i], i) and not art_kept(C["m2"][i], i) for i in ids), "art_gained": sum(art_kept(C["m2"][i], i) and not art_kept(C["off"][i], i) for i in ids),
                   "off_vs_off2_identical": sum(full(C["off"][i]) == full(C["off2"][i]) for i in ids), "scorer_misses": sum(C["m2"][i]["rr"]["miss"] for i in ids),
                   "packroute_P_art_kept": 46}
f = f"{O}/m2-all9-v01.jsonl"
if os.path.exists(f):
    C = passes(f, ["off", "m2", "off2"]); ids = list(C["off"])
    iskit = lambda c: bool(re.match(r"^pack:(?:local-)?(boar-crypto|boar-wikivoyage-en):", c)) or not c.startswith("pack:")
    m2["v01_all9"] = {"n": len(ids), "gold_kept": {a: gold_kept(C[a]) for a in ("off", "m2")},
                      "fired": sum("headpass:rerank:m2:fired" in (C["m2"][i].get("codes") or []) for i in ids),
                      "lost_context": sorted(i for i in ids if C["off"][i]["kept"] and not C["m2"][i]["kept"]),
                      "kit_chunks_lost_items": sorted(i for i in ids if {c for c in keptset(C["off"][i]) if iskit(c)} - keptset(C["m2"][i])),
                      "kit_context_lost_items": sorted(i for i in ids if any(iskit(c) for c in keptset(C["off"][i])) and not any(iskit(c) for c in keptset(C["m2"][i]))),
                      "scorer_misses": sum(C["m2"][i]["rr"]["miss"] for i in ids), "cost_p50": {a: p50([cost(C[a][i]) for i in ids]) for a in ("off", "m2")}}
    kf = f"{O}/v01-kit.x3.jsonl" if os.path.exists(f"{O}/v01-kit.x3.jsonl") else f"{O}/pass1/v01-kit.x3.jsonl"
    if os.path.exists(kf):  # packroute step0.py's lost_context: kept under the kit-only reference, empty with all 9 installed
        K = passes(kf, KITN)["off"]
        m2["v01_all9"].update({"kit_only_gold_kept": gold_kept(K),
                               "lost_context_vs_kit_only": {a: sorted(i for i in ids if K[i]["kept"] and not C[a][i]["kept"]) for a in ("off", "m2")}})
res["m2"] = m2

# ------------------------------------------------------------------ gates
g = {v: {} for v in VARS}; g["m2"] = {}
t = res["timing"]
for v in VARS:
    if complete:
        g[v]["G1_present"] = tot[v]["present"] >= X2B_PRESENT + 15 and all(fam[v][F]["present"] >= X2B_FAM[F] for F in X2B_FAM)
        g[v]["G1_power_line"] = tot[v]["present"] >= X2B_PRESENT + 25
        g[v]["G3_ptok"] = t["ptok_p50"][v] <= t["ptok_p50"]["S"] + 600 and t["ptok_delta"][v]["over_600"] == 0
        g[v]["G2_health"] = health_fail[v] == 0
        g[v]["identity_180"] = ident["off_vs_S"] == ident["x1_vs_X1"] == ident["x2b_vs_X2b"] == ident["off_vs_off2"] == ident["n"] == 180
    if "v01-kit" in res: g[v]["G2_kit_v01"] = res["v01-kit"][v]["vs_off_identical"] == res["v01-kit"]["n"]
    if v02: g[v]["G2_kit_v02"] = v02[f"{v}_vs_off_identical"] == v02["n"]
    if "v01-sw" in res:
        g[v]["G2_sw_lost_context"] = not res["v01-sw"][v]["lost_context"]
        g[v]["G2_sw_gold_kept"] = res["v01-sw"][v]["gold_kept"] >= res["v01-sw"]["off"]["gold_kept"]
        g[v]["G2_sw_health"] = res["v01-sw"][v]["health_fail"] == 0
if "st180" in m2: g["m2"]["M2_art_kept"] = m2["st180"]["m2"]["art_kept"] >= 57
if "v01_all9" in m2 and "lost_context_vs_kit_only" in m2["v01_all9"]:
    g["m2"]["M2_lost_kit_contexts"] = not m2["v01_all9"]["lost_context"] and not m2["v01_all9"]["lost_context_vs_kit_only"]["m2"]
    g["m2"]["M2_v01_gold_kept"] = m2["v01_all9"]["gold_kept"]["m2"] >= m2["v01_all9"]["gold_kept"]["off"]
if "v01-kit" in res: g["m2"]["G2_kit_v01"] = res["v01-kit"]["m2"]["vs_off_identical"] == res["v01-kit"]["n"]
if v02: g["m2"]["G2_kit_v02"] = v02["m2_vs_off_identical"] == v02["n"]
if "v01-sw" in res: g["m2"]["G2_sw_lost_context"] = not res["v01-sw"]["m2"]["lost_context"]
need = {v: ["G1_present", "G3_ptok", "G2_health", "identity_180", "G2_kit_v01", "G2_kit_v02", "G2_sw_lost_context", "G2_sw_gold_kept", "G2_sw_health"] for v in VARS}
need["m2"] = ["M2_art_kept", "M2_lost_kit_contexts", "M2_v01_gold_kept", "G2_kit_v01", "G2_kit_v02", "G2_sw_lost_context"]
verd = {}
for v, nd in need.items():
    gg = {k: x for k, x in g[v].items() if k != "G1_power_line"}
    miss = [k for k in nd if k not in gg]
    verd[v] = "FAIL" if any(x is False for x in gg.values()) else "PASS" if not miss else "INCOMPLETE"
res["gates"] = g; res["verdict_per_variant"] = verd
lat = res["rerank_latency"]["clean_x3a"]["ms_p50"] if res["rerank_latency"]["clean_x3a"]["items"] else res["rerank_latency"]["x3_180"]["ms_p50"]
res["G3_rerank_default_eligible"] = lat is not None and lat <= 1000
passing = [v for v in VARS if verd[v] == "PASS"]
res["stage1_variant"] = max(passing, key=lambda v: tot[v]["present"]) if passing else None
res["verdict"] = ("PASS -> stage 1 with " + res["stage1_variant"]) if passing else ("INCOMPLETE" if any(verd[v] == "INCOMPLETE" for v in VARS) else "FAIL at step 0")
res["verdict"] = f"x3 append: {res['verdict']}; M2 (crowding): {verd['m2']}" + (" -> M2 generation eligible (stage 1 rule: only if M2 passes)" if verd["m2"] == "PASS" else "")
json.dump(res, open(f"{AG}/gate-x3.json", "w"), indent=1)
with open(f"{O}/split-x3.jsonl", "w") as fh:
    for r in rows: fh.write(json.dumps(r) + "\n")
print(json.dumps({k: res[k] for k in ("verdict", "verdict_per_variant", "gates", "identity")}))
