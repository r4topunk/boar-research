"""PACKROUTE step 0 aggregation (criterion sha 801e9ac9…; 0 LLM / 0 judge). Run: python3 -I step0.py  (after run_step0.sh).
Per self-test item (180): fact chunks = in_pack_facts (chunk_index over the article's chunks by start; densechunk-st d0_st.py),
fact article = source.article_id; measures per arm: fact chunk in raw[:6], fact article in kept (the item pack's chunks only).
Arms: S = densechunk-st runs/st-<pack>.jsonl OFF (one pack installed), P = all9 off (first pass), R = router, Q = quota, P2 = off
(second pass, warm, for cost). G1 routing accuracy, G2 reach, G3 kit no-harm + cost, as in the criterion. v0.2 lines are read
script-only: only counts and item ids leave this script. Writes aggregates/step0.json."""
import json, math, os, re, sqlite3, statistics as stt
from collections import Counter
ROOT = "<workspace>"; ARM = f"{ROOT}/rnd/research/coordinator/arms/packroute"; DC = f"{ROOT}/rnd/research/coordinator/arms/densechunk-st"
ST = f"{ROOT}/rnd/research/packs/selftest"; B2 = f"{ROOT}/blind/bench-v02/runs-packs"
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
base = lambda s: (s or "").replace("local-", "")
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

S = {}; diff_st = {}
for p in PACKS:
    ref = passes(load(f"{DC}/runs/st-{p}.jsonl"))["off"]; S.update(ref)
    f = f"{ARM}/runs/diff-st-{p}.jsonl"
    if os.path.exists(f):
        d = passes(load(f))["off"]; diff_st[p] = f"{sum(key(d[i]) == key(ref[i]) for i in ref if i in d)}/{len(ref)}"
A = passes(load(f"{ARM}/runs/all9-st180.jsonl"))
arms = {"S": S, "P": A["off"], "R": A["router"], "Q": A["quota"]}

def sel(l):
    r = (l or {}).get("route") or []
    return base(r[0]["selected"]) if r and r[0].get("selected") else ("none" if r else "no-route")

rows = []
for i in items:
    p = facts[i][0]; row = {"id": i, "pack": p, "family": "SE" if p in SE else "topic", "route": sel(arms["R"].get(i))}
    for a, L in arms.items(): row[a] = reach(L.get(i), i)
    rows.append(row)

def summ(rs):
    o = {"n": len(rs)}
    for a in arms: o[a] = {k: sum(r[a][k] for r in rs) for k in ("chunk_raw6", "art_raw6", "chunk_kept", "art_kept")} | {"empty_kept": sum(r[a]["kept_n"] == 0 for r in rs)}
    o["route_own"] = sum(r["route"] == r["pack"] for r in rs); o["route_none"] = sum(r["route"] == "none" for r in rs)
    o["route_acc"] = round(o["route_own"] / len(rs), 3) if rs else None
    return o
fam = {f: summ([r for r in rows if r["family"] == f]) for f in ("SE", "topic")}
per_pack = {p: summ([r for r in rows if r["pack"] == p]) for p in PACKS}
allx = summ(rows)
confusion = Counter(f"{r['pack']}->{r['route']}" for r in rows if r["route"] != r["pack"])
# lost context on the 180 vs S (kept under S, empty under the arm)
lost180 = {a: sorted(r["id"] for r in rows if r["S"]["kept_n"] and not r[a]["kept_n"]) for a in ("P", "R", "Q")}
ms180 = {a: p50([l["ms"] for l in A[m].values()]) for a, m in (("P", "off"), ("R", "router"), ("Q", "quota"), ("P2", "off2"))}
votes_hist = Counter(max((x["route"][0]["votes"].values()), default=0) for x in A["router"].values() if x.get("route"))

# ------------------------------------------------------------------ kit sets (v0.1 public, v0.2 script-only)
def gold_in_wave(g):
    t = bare(g.partition("#")[0])
    for p, db in dbs.items():
        if db.execute("SELECT 1 FROM articles WHERE title = ? COLLATE NOCASE LIMIT 1", (t,)).fetchone(): return True
        try:
            if db.execute("SELECT 1 FROM redirects WHERE title = ? COLLATE NOCASE LIMIT 1", (t,)).fetchone(): return True
        except sqlite3.Error: pass
    return False

def kit(name, runf, reff, goldf, res_ids=None, kitdiff=None):
    Pm = passes(load(runf)); ref = passes(load(reff))["off"]
    G = {k: v for k, v in json.load(open(goldf)).items() if isinstance(v, list) and v}
    o = {"n": len(Pm["off"])}
    retr = [i for i, l in Pm["router"].items() if l["raw"] or l.get("route")]
    nowave = [i for i in sorted(G) if i in Pm["router"] and Pm["router"][i].get("route") and not any(gold_in_wave(g) for g in G[i])]
    o["G1_none"] = {"gold_items_routed_no_wave_gold": len(nowave), "none": sum(sel(Pm["router"][i]) == "none" for i in nowave),
                    "picked": dict(Counter(sel(Pm["router"][i]) for i in nowave if sel(Pm["router"][i]) != "none"))}
    o["G1_none"]["share"] = round(o["G1_none"]["none"] / len(nowave), 3) if nowave else None
    allr = [i for i in Pm["router"] if Pm["router"][i].get("route")]
    o["route_all_retrieving"] = {"n": len(allr), "none": sum(sel(Pm["router"][i]) == "none" for i in allr)}
    sets = {"kit": ref, "P": Pm["off"], "R": Pm["router"], "Q": Pm["quota"]}
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
    if res_ids is not None: o["resolvable_ids"] = res_ids
    if kitdiff: o["kit_ref_identity"] = kitdiff
    return o

v01diff = None
if os.path.exists(f"{ARM}/runs/diff-v01-kit.jsonl"):
    D = passes(load(f"{ARM}/runs/diff-v01-kit.jsonl")); ref = passes(load(f"{DC}/runs/v01-kit.jsonl"))["off"]
    v01diff = {m: f"{sum(key(D[m][i]) == key(ref[i]) for i in ref if i in D[m])}/{len(ref)}" for m in ("off", "router", "quota")}
v01 = kit("v01", f"{ARM}/runs/all9-v01.jsonl", f"{DC}/runs/v01-kit.jsonl", f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json", kitdiff=v01diff)
p4b = json.load(open(f"{ROOT}/rnd/research/coordinator/arms/packcond/aggregates/p4b-diag.json"))["items"]
res = sorted(x["id"] for x in p4b if x["set"] == "v02" and any(t["kind"] == "gold" and t["resolved"] for t in x["targets"]))
v02f = f"{B2}/packroute-all9-v02.jsonl"
v02 = kit("v02", v02f, f"{B2}/densechunk-st-v02-kit.jsonl", f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json", res_ids=res) if os.path.exists(v02f) else None

# ------------------------------------------------------------------ gates
g1_items = allx["route_own"] >= math.ceil(0.85 * 180 - 1e-9)
nw = [x["G1_none"] for x in (v01, v02) if x]
none_n = sum(x["none"] for x in nw); none_d = sum(x["gold_items_routed_no_wave_gold"] for x in nw)
g1_none = none_d > 0 and none_n >= math.ceil(0.85 * none_d - 1e-9)
R, Pq, Sq = allx["R"], allx["P"], allx["S"]
g2 = R["chunk_raw6"] >= 60 and R["art_kept"] >= 61 and R["chunk_raw6"] >= Pq["chunk_raw6"] and R["art_kept"] >= Pq["art_kept"]
q2 = allx["Q"]["chunk_raw6"] >= 60 and allx["Q"]["art_kept"] >= 61 and allx["Q"]["chunk_raw6"] >= Pq["chunk_raw6"] and allx["Q"]["art_kept"] >= Pq["art_kept"]
def nh(arm):
    ok = True
    for x in (v01, v02):
        if not x: ok = False; continue
        ok &= not x[arm]["lost_context"] and x[arm]["gold_kept"] >= x["kit"]["gold_kept"] and x[arm]["gold_raw6"] >= x["kit"]["gold_raw6"]
    return bool(ok)
cost_ratio = round(ms180["R"] / ms180["P2"], 2) if ms180["P2"] else None
cost_ratio_q = round(ms180["Q"] / ms180["P2"], 2) if ms180["P2"] else None
g3 = nh("R") and cost_ratio is not None and cost_ratio <= 1.5
gates = {"G1": {"route_own_180": allx["route_own"], "need": math.ceil(0.85 * 180 - 1e-9), "items_pass": g1_items,
                "none_kit": f"{none_n}/{none_d}", "none_need": math.ceil(0.85 * none_d - 1e-9) if none_d else None, "none_pass": g1_none, "pass": g1_items and g1_none},
         "G2": {"S": {k: Sq[k] for k in ("chunk_raw6", "art_kept")}, "P": {k: Pq[k] for k in ("chunk_raw6", "art_kept")},
                "R": {k: R[k] for k in ("chunk_raw6", "art_kept")}, "Q": {k: allx["Q"][k] for k in ("chunk_raw6", "art_kept")},
                "need": {"chunk_raw6": 60, "art_kept": 61}, "pass": g2, "Q_would_pass": q2},
         "G3": {"R_no_harm": nh("R"), "Q_no_harm": nh("Q"), "P_no_harm": nh("P"), "ms_p50_180": ms180, "ratio_R_P2": cost_ratio, "ratio_Q_P2": cost_ratio_q, "pass": g3}}
verdict = "PASS -> stage 1 (R vs P)" if all(gates[g]["pass"] for g in ("G1", "G2", "G3")) else "FAIL at step 0"
out = {"criterion_sha256": "801e9ac9fd1853c3c990ecd60e9c8e696b4a036bddf61a92b310ace6cfae70b6",
       "differential": {"st_single_pack_off_vs_S": diff_st, "v01_kit_modes_vs_kit_ref": v01diff},
       "selftest180": {"all": allx, "family": fam, "per_pack": per_pack, "confusion": dict(confusion.most_common()),
                       "lost_context_vs_S": lost180, "ms_p50": ms180, "max_votes_hist": dict(sorted(votes_hist.items()))},
       "v01": v01, "v02": v02, "gates": gates, "verdict_step0": verdict,
       "items": [{"id": r["id"], "pack": r["pack"], "route": r["route"], **{a: {k: r[a][k] for k in ("chunk_raw6", "art_kept")} for a in arms}} for r in rows]}
json.dump(out, open(f"{ARM}/aggregates/step0.json", "w"), indent=1)
print(json.dumps({"diff": out["differential"], "all": {a: allx[a] for a in arms}, "route_acc": allx["route_acc"],
                  "family_acc": {f: fam[f]["route_acc"] for f in fam}, "gates": gates, "verdict": verdict}, indent=0))
