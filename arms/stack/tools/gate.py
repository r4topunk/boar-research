"""STACK step 0 gates (criterion STACK-criterion.md, sha 56ed7ccf…; 0 LLM / 0 judge). Run: python3 -I gate.py (after run_step0.sh).
Inputs: runs/st180-all9.jsonl (kit + all 9; passes off=P, stack=X, off2, stack2, quota, perpack), runs/v01-{kit,all9}.jsonl and
$HELDOUT_DIR/bench-v02/runs-packs/stack-v02-{kit,all9}.jsonl (passes off, stack, off2). Reach as arms/packroute/tools/step0.py (fact chunk =
in_pack_facts chunk_index over the article's chunks by start; fact article = source.article_id; chunkId match on the item's pack).
G1: X fact article kept >= 56 and X fact chunk kept >= P + 8. G2 (RULE 26) vs kit-only OFF: lost context (kit-OFF kept non-empty ->
arm kept empty) under X adds no id to P's (P's ids may persist only when X loses the same source the same way: reported); empty kept
over kit-OFF-retrieving items not above P (all 9) / kit OFF (kit only); v0.1 gold kept >= 12; v0.2 resolvable gold kept >= 3;
tokens never above the cap (keptTokens <= max(budget, OFF keptTokens)). G3: retrieval + keep p50 on the 180, X <= 1.3 x P
(warm passes stack2 vs off2; first passes reported). Identity: P = PACKROUTE's all-9 OFF (raw + kept) 180/180.
v0.2 lines are read script-only: counts and item ids only. Writes aggregates/gate.json; prints a summary."""
import json, re, sqlite3, statistics as stt
from collections import Counter
ROOT = "$BOAR_WS"; A = f"{ROOT}/rnd/research/coordinator/arms"; ARM = f"{A}/stack"; B2 = f"$HELDOUT_DIR/bench-v02/runs-packs"
ST = f"{ROOT}/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SE = {p for p in PACKS if p.startswith("qa-")}
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
def key(l):
    return json.dumps([[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]] + [[x.get("chunkId"), x.get("title")] for x in l["kept"]])
ids = lambda xs: [x.get("chunkId") for x in xs]
def p50(xs):
    xs = [x for x in xs if x is not None]; return round(stt.median(xs), 1) if xs else None
tot = lambda l: (l["ms"] + (l.get("keepMs") or 0)) if l.get("ms") is not None else None
_LIB = re.compile(r"^[^:]{2,40}:\s+")
norm = lambda s: " ".join(str(s or "").split()).lower()
bare = lambda t: _LIB.sub("", str(t or ""))
def gmatch(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))

# ---------------------------------------------------------------- 180
facts, items = {}, []
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True); ch_art = dict(db.execute("SELECT id, article_id FROM chunks").fetchall())
    for it in load(f"{ST}/{p}.jsonl"):
        fa = it["source"]["article_id"]; fcs = set()
        for f in it["in_pack_facts"]:
            if f.get("chunk_index") is None: continue
            cs = [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (f.get("article", fa),))]
            if f["chunk_index"] < len(cs): fcs.add(cs[f["chunk_index"]])
        items.append(it["id"]); facts[it["id"]] = (p, fa, fcs, ch_art)
def reach(l, i):
    p, fa, fcs, ch_art = facts[i]
    raw = [cid(x, p) for x in l["raw"][:6]]; kept = [cid(x, p) for x in l["kept"]]
    return {"chunk_raw6": any(c in fcs for c in raw if c), "art_raw6": any(ch_art.get(c) == fa for c in raw if c),
            "chunk_kept": any(c in fcs for c in kept if c), "art_kept": any(ch_art.get(c) == fa for c in kept if c),
            "empty_kept": not l["kept"], "own_slots": sum(pk(x) == p for x in l["kept"]), "kept_slots": len(l["kept"])}
S = passes(load(f"{ARM}/runs/st180-all9.jsonl"))
MODES = [m for m in ("off", "stack", "quota", "perpack") if m in S]
rows = [{"id": i, "pack": facts[i][0], "family": "SE" if facts[i][0] in SE else "topic", **{m: reach(S[m][i], i) for m in MODES}} for i in items]
def summ(rs): return {"n": len(rs), **{m: {k: sum(r[m][k] for r in rs) for k in rs[0][m]} for m in MODES}} if rs else {}
allx = summ(rows); fam = {f: summ([r for r in rows if r["family"] == f]) for f in ("SE", "topic")}
per_pack = {p: summ([r for r in rows if r["pack"] == p]) for p in PACKS}
PR = passes(load(f"{A}/packroute/runs/all9-st180.jsonl"))["off"]
ident = {"P_vs_packroute_off": f"{sum(key(S['off'][i]) == key(PR[i]) for i in items)}/180",
         "P_vs_off2": f"{sum(key(S['off'][i]) == key(S['off2'][i]) for i in items)}/180",
         "X_vs_stack2": f"{sum(key(S['stack'][i]) == key(S['stack2'][i]) for i in items)}/180" if "stack2" in S else None}
enter_leave = {m: {k: [sum(r[m][k] and not r["off"][k] for r in rows), sum(r["off"][k] and not r[m][k] for r in rows)] for k in ("chunk_kept", "art_kept")} for m in MODES if m != "off"}
changed = {m: sum(ids(S[m][i]["kept"]) != ids(S["off"][i]["kept"]) or S[m][i].get("keptTokens") != S["off"][i].get("keptTokens") for i in items) for m in MODES if m != "off"}
def attribution(m):
    c = Counter(); own = Counter(); foreign = Counter()
    for i in items:
        p = facts[i][0]
        for x in S[m][i]["kept"]:
            c[pk(x)] += 1
            (own if pk(x) == p else foreign)[pk(x)] += 1
    n = sum(c.values())
    return {"kept_slots": n, "own_pack_slots": sum(own.values()), "foreign_slots": sum(foreign.values()),
            "share": {k: round(v / n, 3) for k, v in c.most_common(6)}, "foreign_top": dict(foreign.most_common(6)),
            "simplewiki_share": round(c["boar-simplewiki-en"] / n, 3) if n else None}
attrib = {m: attribution(m) for m in MODES}
codes = {m: dict(Counter(c for i in items for c in S[m][i].get("keepCodes", [])).most_common()) for m in MODES if m != "off"}
tok180 = {m: sum(1 for i in items if S[m][i].get("budget") is not None and S[m][i]["keptTokens"] > max(S[m][i]["budget"], S["off"][i]["keptTokens"])) for m in MODES if m != "off"}
ms = {m: p50([tot(l) for l in S[m].values()]) for m in S}
ret_ms = {m: p50([l["ms"] for l in S[m].values()]) for m in S}

# ---------------------------------------------------------------- kit sets
def lost_reason(kref, L):
    """Why an arm lost the kit-OFF kept sources: 'not-in-raw' (all crowded out of the raw list) or 'dropped-in-keep'."""
    kk = set(ids(kref["kept"])); raw = set(ids(L["raw"]))
    return "not-in-raw" if not (kk & raw) else "dropped-in-keep"
def kitset(name, kitf, allf, goldf, res_ids=None):
    K = passes(load(kitf)); Al = passes(load(allf)); ref = K["off"]
    G = {k: v for k, v in json.load(open(goldf)).items() if isinstance(v, list) and v}
    sel = res_ids if res_ids is not None else sorted(G)
    arms = {"kitX": K["stack"], "P": Al["off"], "X": Al["stack"]}
    o = {"n": len(ref), "identity_kit_off_vs_off2": f"{sum(key(ref[i]) == key(K['off2'][i]) for i in ref)}/{len(ref)}",
         "kit_off": {"gold_kept": sum(any(gmatch(g, x) for g in G.get(i, []) for x in ref[i]["kept"]) for i in sel if i in ref),
                     "empty_kept_retrieving": sum(1 for l in ref.values() if l["raw"] and not l["kept"])}}
    for a, L in arms.items():
        lost = sorted(i for i in ref if ref[i]["kept"] and not L[i]["kept"])
        o[a] = {"gold_kept": sum(any(gmatch(g, x) for g in G.get(i, []) for x in L[i]["kept"]) for i in sel if i in L),
                "empty_kept_over_off_retrieving": sum(1 for i in ref if ref[i]["raw"] and not L[i]["kept"]),
                "lost_context": lost, "lost_reason": {i: lost_reason(ref[i], L[i]) for i in lost},
                "tokens_over_cap": sum(1 for i in ref if L[i].get("budget") is not None and L[i]["keptTokens"] > max(L[i]["budget"], ref[i]["keptTokens"])),
                "kept_changed_vs_kit_off": sum(ids(L[i]["kept"]) != ids(ref[i]["kept"]) for i in ref),
                "wave_slots_kept": sum(pk(x) in PACKS for l in L.values() for x in l["kept"]), "kept_slots": sum(len(l["kept"]) for l in L.values()),
                "total_ms_p50": p50([tot(l) for l in L.values()])}
    # kit-only OFF on the stack replay tree = the kit reference for stage 1b (OFF generations must keep these lists)
    o["P_identity_vs_packroute"] = None
    return o
p4b = json.load(open(f"{A}/packcond/aggregates/p4b-diag.json"))["items"]
res = sorted(x["id"] for x in p4b if x["set"] == "v02" and any(t["kind"] == "gold" and t["resolved"] for t in x["targets"]))
v01 = kitset("v01", f"{ARM}/runs/v01-kit.jsonl", f"{ARM}/runs/v01-all9.jsonl", f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")
v02 = kitset("v02", f"{B2}/stack-v02-kit.jsonl", f"{B2}/stack-v02-all9.jsonl", f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json", res_ids=res)
PR1 = passes(load(f"{A}/packroute/runs/all9-v01.jsonl"))["off"]; Al1 = passes(load(f"{ARM}/runs/v01-all9.jsonl"))["off"]
v01["P_identity_vs_packroute"] = f"{sum(key(Al1[i]) == key(PR1[i]) for i in PR1)}/{len(PR1)}"
PR2 = passes(load(f"{B2}/packroute-all9-v02.jsonl"))["off"]; Al2 = passes(load(f"{B2}/stack-v02-all9.jsonl"))["off"]
v02["P_identity_vs_packroute"] = f"{sum(key(Al2[i]) == key(PR2[i]) for i in PR2)}/{len(PR2)}"
DC1 = passes(load(f"{A}/densechunk-st/runs/v01-kit.jsonl"))["off"]; K1 = passes(load(f"{ARM}/runs/v01-kit.jsonl"))["off"]
v01["kit_off_identity_vs_densechunk_st"] = f"{sum(key(K1[i]) == key(DC1[i]) for i in DC1)}/{len(DC1)}"

# ---------------------------------------------------------------- gates
P, X = allx["off"], allx["stack"]
g1 = {"P": {k: P[k] for k in ("art_kept", "chunk_kept", "art_raw6", "chunk_raw6", "empty_kept")}, "X": {k: X[k] for k in ("art_kept", "chunk_kept", "art_raw6", "chunk_raw6", "empty_kept")},
      "need_art_kept": 56, "need_chunk_kept": P["chunk_kept"] + 8,
      "family": {f: {"P": [fam[f]["off"]["chunk_kept"], fam[f]["off"]["art_kept"]], "X": [fam[f]["stack"]["chunk_kept"], fam[f]["stack"]["art_kept"]]} for f in fam}}
g1["pass"] = X["art_kept"] >= 56 and X["chunk_kept"] >= P["chunk_kept"] + 8
def g2set(o, gold_need):
    newX = [i for i in o["X"]["lost_context"] if i not in o["P"]["lost_context"]]
    newK = o["kitX"]["lost_context"]
    persist = {i: {"P": o["P"]["lost_reason"][i], "X": o["X"]["lost_reason"][i]} for i in o["X"]["lost_context"] if i in o["P"]["lost_context"]}
    ok = (not newX and not newK and all(v["P"] == v["X"] for v in persist.values())
          and o["X"]["empty_kept_over_off_retrieving"] <= o["P"]["empty_kept_over_off_retrieving"]
          and o["kitX"]["empty_kept_over_off_retrieving"] <= o["kit_off"]["empty_kept_retrieving"]
          and o["X"]["gold_kept"] >= gold_need and o["kitX"]["gold_kept"] >= gold_need
          and o["X"]["tokens_over_cap"] == 0 and o["kitX"]["tokens_over_cap"] == 0)
    return {"lost_P": len(o["P"]["lost_context"]), "lost_X": len(o["X"]["lost_context"]), "lost_kitX": len(newK), "new_under_X": newX,
            "persisting_same_reason": persist, "empty_kept_P_X_kitoff_kitX": [o["P"]["empty_kept_over_off_retrieving"], o["X"]["empty_kept_over_off_retrieving"],
            o["kit_off"]["empty_kept_retrieving"], o["kitX"]["empty_kept_over_off_retrieving"]],
            "gold_kept_kitoff_P_X_kitX": [o["kit_off"]["gold_kept"], o["P"]["gold_kept"], o["X"]["gold_kept"], o["kitX"]["gold_kept"]], "gold_need": gold_need,
            "tokens_over_cap_X_kitX": [o["X"]["tokens_over_cap"], o["kitX"]["tokens_over_cap"]], "pass": ok}
g2 = {"v01": g2set(v01, 12), "v02": g2set(v02, 3), "tokens_over_cap_180_X": tok180.get("stack")}
g2["pass"] = g2["v01"]["pass"] and g2["v02"]["pass"] and g2["tokens_over_cap_180_X"] == 0
r_warm = round(ms["stack2"] / ms["off2"], 2) if "stack2" in ms else None
g3 = {"total_ms_p50": ms, "retrieve_ms_p50": ret_ms, "ratio_warm_stack2_off2": r_warm, "ratio_first_stack_off": round(ms["stack"] / ms["off"], 2), "need": 1.3}
g3["pass"] = r_warm is not None and r_warm <= 1.3
verdict = "PASS -> stage 1" if g1["pass"] and g2["pass"] and g3["pass"] else "FAIL at step 0"
out = {"criterion_sha256": open(f"{ARM}/STACK-criterion.sha256").read().split()[0], "identity_180": ident, "selftest180": {"all": allx, "family": fam, "per_pack": per_pack},
       "enter_leave_vs_P": enter_leave, "changed_vs_P": changed, "attribution": attrib, "keep_codes": codes, "tokens_over_cap_180": tok180,
       "v01": v01, "v02": v02, "gates": {"G1": g1, "G2": g2, "G3": g3}, "verdict_step0": verdict,
       "items": [{"id": r["id"], "pack": r["pack"], **{m: {k: r[m][k] for k in ("chunk_kept", "art_kept", "own_slots")} for m in MODES}} for r in rows]}
json.dump(out, open(f"{ARM}/aggregates/gate.json", "w"), indent=1)
print(json.dumps({"identity": ident, "v01_P_ident": v01["P_identity_vs_packroute"], "v02_P_ident": v02["P_identity_vs_packroute"], "v01_kitoff_ident": v01["kit_off_identity_vs_densechunk_st"],
                  "all": {m: allx[m] for m in MODES}, "G1": g1, "G2": g2, "G3": {k: v for k, v in g3.items()}, "changed": changed,
                  "attrib": attrib, "codes": codes, "verdict": verdict}, indent=None))
