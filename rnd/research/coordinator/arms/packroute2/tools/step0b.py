"""PACKROUTE-2 step 0b aggregation (criterion sha d67fd81c…; 0 LLM / 0 judge). Run: python3 -I step0b.py [--wording v2]
(after run_step0b.sh). Adapted from arms/packroute/tools/step0.py.
Arms on the 180: S = densechunk-st runs/st-<pack>.jsonl OFF (one pack installed), P = all9 off (first pass, this tree),
R4 = llm, R4Q = llmq, P2 = off second pass (warm; the cost reference). G2 reach, G3 kit no-harm (RULE 26) + cost.
Identity: this tree's default-off replays vs PACKROUTE's diff-*.jsonl and all9 off pass. v0.2 lines are read script-only:
only counts and item ids leave this script. Writes aggregates/step0b[.v2].json."""
import json, math, os, re, sqlite3, statistics as stt, sys
from collections import Counter
ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/packroute2"
PR = f"{ROOT}/rnd/research/coordinator/arms/packroute"; DC = f"{ROOT}/rnd/research/coordinator/arms/densechunk-st"
ST = f"{ROOT}/rnd/research/packs/selftest"; B2 = f"{ROOT}/blind/bench-v02/runs-packs"
W = sys.argv[sys.argv.index("--wording") + 1] if "--wording" in sys.argv else "v1"; SUF = "" if W == "v1" else f".{W}"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SE = {p for p in PACKS if p.startswith("qa-")}; K = 6
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
def cid(ref, pack):
    m = CID.match(ref.get("chunkId") or ""); return int(m.group(2)) if m and m.group(1) == pack else None
def pk(ref):
    m = CID.match(ref.get("chunkId") or ""); return m.group(1) if m else "seed"
def passes(lines):
    out, seen = {}, {}
    for l in lines:
        n = seen.get((l["mode"], l["id"]), 0); seen[(l["mode"], l["id"])] = n + 1
        out.setdefault(l["mode"] + ("2" if n else ""), {})[l["id"]] = l
    return out
def p50(xs):
    xs = [x for x in xs if x is not None]; return round(stt.median(xs), 1) if xs else None
def key(l):  # densechunk-st gate_st.py identity key
    return json.dumps([[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]] + [[x.get("chunkId"), x.get("title")] for x in l["kept"]])
_LIB = re.compile(r"^[^:]{2,40}:\s+")
norm = lambda s: " ".join(str(s or "").split()).lower()
bare = lambda t: _LIB.sub("", str(t or ""))
def gmatch(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
def ident(a, b):
    return f"{sum(key(a[i]) == key(b[i]) for i in b if i in a)}/{len(b)}"

# ------------------------------------------------------------------ identity (default off byte-identical)
identity = {}
D = passes(load(f"{ARM}/runs/diff-v01-kit.jsonl")); Dref = passes(load(f"{PR}/runs/diff-v01-kit.jsonl"))
identity["v01_kit_vs_packroute"] = {m: ident(D[m], Dref[m]) for m in ("off", "router", "quota")}
identity["st_single_pack_off_vs_packroute"] = {p: ident(passes(load(f"{ARM}/runs/diff-st-{p}.jsonl"))["off"], passes(load(f"{PR}/runs/diff-st-{p}.jsonl"))["off"]) for p in PACKS}

# ------------------------------------------------------------------ self-test items: facts
items, facts = [], {}
dbs = {p: sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True) for p in PACKS}
for p in PACKS:
    db = dbs[p]; ch_art = dict(db.execute("SELECT id, article_id FROM chunks").fetchall())
    for it in load(f"{ST}/{p}.jsonl"):
        fa = it["source"]["article_id"]; fcs = set()
        for f in it["in_pack_facts"]:
            if f.get("chunk_index") is None: continue
            cs = [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (f.get("article", fa),))]
            if f["chunk_index"] < len(cs): fcs.add(cs[f["chunk_index"]])
        items.append(it["id"]); facts[it["id"]] = (p, fa, fcs, ch_art)
def reach(l, iid):
    p, fa, fcs, ch_art = facts[iid]
    if not l: return {"chunk_raw6": False, "art_kept": False, "art_raw6": False, "chunk_kept": False, "kept_n": 0}
    raw = [cid(x, p) for x in l["raw"][:K]]; kept = [cid(x, p) for x in l["kept"]]
    return {"chunk_raw6": any(c in fcs for c in raw if c), "art_raw6": any(ch_art.get(c) == fa for c in raw if c),
            "chunk_kept": any(c in fcs for c in kept if c), "art_kept": any(ch_art.get(c) == fa for c in kept if c), "kept_n": len(l["kept"])}

S = {}
for p in PACKS: S.update(passes(load(f"{DC}/runs/st-{p}.jsonl"))["off"])
A = passes(load(f"{ARM}/runs/all9-st180{SUF}.jsonl"))
identity["st180_P_vs_packroute_P"] = ident(A["off"], passes(load(f"{PR}/runs/all9-st180.jsonl"))["off"])
arms = {"S": S, "P": A["off"], "R4": A["llm"], "R4Q": A["llmq"]}
routes = {x["id"]: x["choice"] for x in load(f"{ARM}/runs/routes-st180{SUF}.jsonl")}
rows = []
for i in items:
    p = facts[i][0]; row = {"id": i, "pack": p, "family": "SE" if p in SE else "topic", "route": routes.get(i)}
    for a, L in arms.items(): row[a] = reach(L.get(i), i)
    rows.append(row)
def summ(rs):
    o = {"n": len(rs)}
    for a in arms: o[a] = {k: sum(r[a][k] for r in rs) for k in ("chunk_raw6", "art_raw6", "chunk_kept", "art_kept")} | {"empty_kept": sum(r[a]["kept_n"] == 0 for r in rs)}
    o["route_own"] = sum(r["route"] == r["pack"] for r in rs); o["route_none"] = sum(r["route"] == "none" for r in rs)
    return o
allx = summ(rows)
fam = {f: summ([r for r in rows if r["family"] == f]) for f in ("SE", "topic")}
per_pack = {p: summ([r for r in rows if r["pack"] == p]) for p in PACKS}
# reach split by route correctness (R4)
def outcome(r): return "own" if r["route"] == r["pack"] else "none" if r["route"] == "none" else "invalid" if r["route"] in (None, "invalid") else "elsewhere"
by_route = {k: summ([r for r in rows if outcome(r) == k]) for k in ("own", "elsewhere", "none", "invalid")}
lost180 = {a: sorted(r["id"] for r in rows if r["S"]["kept_n"] and not r[a]["kept_n"]) for a in ("P", "R4", "R4Q")}
ms180 = {a: p50([l["ms"] for l in A[m].values()]) for a, m in (("P", "off"), ("R4", "llm"), ("R4Q", "llmq"), ("P2", "off2"))}

# ------------------------------------------------------------------ kit sets (v0.1 public, v0.2 script-only)
def kit(runf, reff, goldf, prref, res_ids=None):
    Pm = passes(load(runf)); ref = passes(load(reff))["off"]
    G = {k: v for k, v in json.load(open(goldf)).items() if isinstance(v, list) and v}
    o = {"n": len(Pm["off"]), "P_identity_vs_packroute": ident(Pm["off"], passes(load(prref))["off"])}
    sets = {"kit": ref, "P": Pm["off"], "R4": Pm["llm"], "R4Q": Pm["llmq"]}
    ids_all = sorted(G); ids_res = res_ids if res_ids is not None else ids_all
    for a, L in sets.items():
        o[a] = {"gold_raw6": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["raw"][:6]) for i in ids_res if i in L),
                "gold_kept": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["kept"]) for i in ids_res if i in L),
                "gold_kept_all_gold_items": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["kept"]) for i in ids_all if i in L),
                "empty_kept_retrieving": sum(1 for l in L.values() if l["raw"] and not l["kept"]),
                "ms_p50": p50([l["ms"] for l in L.values()])}
        if a != "kit":
            o[a]["lost_context"] = sorted(i for i in ref if ref[i]["kept"] and not L.get(i, {}).get("kept"))
            o[a]["wave_slots_kept"] = sum(pk(x) in PACKS for l in L.values() for x in l["kept"])
            o[a]["kept_slots"] = sum(len(l["kept"]) for l in L.values())
    o["P2_ms_p50"] = p50([l["ms"] for l in Pm["off2"].values()])
    o["gold_set"] = "resolvable (p4b-diag)" if res_ids is not None else "all gold items"
    return o
v01 = kit(f"{ARM}/runs/all9-v01{SUF}.jsonl", f"{DC}/runs/v01-kit.jsonl", f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json", f"{PR}/runs/all9-v01.jsonl")
p4b = json.load(open(f"{ROOT}/rnd/research/coordinator/arms/packcond/aggregates/p4b-diag.json"))["items"]
res = sorted(x["id"] for x in p4b if x["set"] == "v02" and any(t["kind"] == "gold" and t["resolved"] for t in x["targets"]))
v02 = kit(f"{B2}/packroute2-all9-v02{SUF}.jsonl", f"{B2}/densechunk-st-v02-kit.jsonl", f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json",
          f"{B2}/packroute-all9-v02.jsonl", res_ids=res)

# ------------------------------------------------------------------ gates
Pq = allx["P"]
def g2(a):
    x = allx[a]; return bool(x["chunk_raw6"] >= 60 and x["art_kept"] >= 61 and x["chunk_raw6"] >= Pq["chunk_raw6"] and x["art_kept"] >= Pq["art_kept"])
def g3(a):
    parts = {}
    for name, x in (("v01", v01), ("v02", v02)):
        parts[f"{name}_lost_context_0"] = not x[a]["lost_context"]
        parts[f"{name}_empty_kept_not_up"] = x[a]["empty_kept_retrieving"] <= x["kit"]["empty_kept_retrieving"]
    parts["v01_gold_kept_ge_12"] = v01[a]["gold_kept"] >= 12
    parts["v02_res_gold_kept_ge_4"] = v02[a]["gold_kept"] >= 4
    ratio = round(ms180[a] / ms180["P2"], 2) if ms180["P2"] else None
    parts["p50_le_1.5xP"] = ratio is not None and ratio <= 1.5
    return {"parts": parts, "p50_ratio_vs_P2": ratio, "pass": all(parts.values())}
gates = {"G2": {a: {"chunk_raw6": allx[a]["chunk_raw6"], "art_kept": allx[a]["art_kept"], "pass": g2(a)} for a in ("R4", "R4Q")}
         | {"S": {k: allx["S"][k] for k in ("chunk_raw6", "art_kept")}, "P": {k: Pq[k] for k in ("chunk_raw6", "art_kept")}, "need": {"chunk_raw6": 60, "art_kept": 61}},
         "G3": {a: g3(a) for a in ("R4", "R4Q", "P")}}
ok = {a: gates["G2"][a]["pass"] and gates["G3"][a]["pass"] for a in ("R4", "R4Q")}
variant = "R4" if ok["R4"] else "R4Q" if ok["R4Q"] else None
acc = json.load(open(f"{ARM}/aggregates/accuracy{SUF}.json"))
verdict = (f"PASS -> stage 1 with {variant}" if acc["G1"]["pass"] and variant else
           "FAIL at step 0a (G1)" if not acc["G1"]["pass"] else "FAIL at step 0 (G2/G3: neither R4 nor R4Q)")
out = {"criterion_sha256": "d67fd81c4b58ff150fd8f893d53bf90d3e7e030ebd3a513e9f6e8cb2a00c9d05", "wording": W, "identity": identity,
       "router_ms_cold_p50": acc["ms"]["cold_all"]["p50"], "router_ms_cached_p50": acc["ms"]["cached20"]["p50"],
       "selftest180": {"all": allx, "family": fam, "per_pack": per_pack, "by_route_correctness": by_route,
                       "lost_context_vs_S": lost180, "ms_p50": ms180},
       "v01": v01, "v02": v02, "gates": gates, "G1": acc["G1"], "variant_stage1": variant, "verdict_step0": verdict,
       "items": [{"id": r["id"], "pack": r["pack"], "route": r["route"], **{a: {k: r[a][k] for k in ("chunk_raw6", "art_kept")} for a in arms}} for r in rows]}
json.dump(out, open(f"{ARM}/aggregates/step0b.json", "w"), indent=1)  # wording recorded in out["wording"]
print(json.dumps({"identity": identity, "all": {a: allx[a] for a in arms}, "family": {f: {a: fam[f][a] for a in arms} for f in fam},
                  "buckets": {k: {"n": v["n"], **{a: v[a]["art_kept"] for a in ("S", "P", "R4", "R4Q")}} for k, v in by_route.items()}, "gates": gates, "v01_lost": {a: v01[a]["lost_context"] for a in ("P", "R4", "R4Q")},
                  "v02_lost": {a: v02[a]["lost_context"] for a in ("P", "R4", "R4Q")}, "variant": variant, "verdict": verdict}, indent=0))
