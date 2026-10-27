"""TK2-FIX step 0 scorer (0 LLM): cells cut7 / tk2 / tk2fix; definitions = tk2-replay/tools/compare_tk2.py (fact chunk /
fact article = packroute step0.py, item's own pack via chunkId prefix). Gate per TK2FIX-step0-criterion.md. Public sets only."""
import json, re, sqlite3, os, sys
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/tk2fix"; ST = f"{ROOT}/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
CELLS = ["cut7", "tk2", "tk2fix"]; K = 6; load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
def cid(ref, pack):
    m = CID.match(ref.get("chunkId") or ""); return int(m.group(2)) if m and m.group(1) == pack else None
def passes(lines):
    out, seen = {}, {}
    for l in lines:
        n = seen.get(l["id"], 0); seen[l["id"]] = n + 1; out.setdefault(n, {})[l["id"]] = l
    return out
ids = lambda l, f="kept": [x.get("chunkId") for x in l[f]]
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).lower(); bare = lambda t: _LIB.sub("", str(t or ""))
def gmatch(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
def rep(P): return sum(json.dumps([ids(P[0][i]), ids(P[0][i], "raw"), P[0][i].get("promptSha")]) == json.dumps([ids(P[1][i]), ids(P[1][i], "raw"), P[1][i].get("promptSha")]) for i in P[0])
route = lambda l: [l["task"], l["query"], l["k"], l.get("codes")]
res = {"criterion_sha256": open(f"{A}/TK2FIX-step0-criterion.md.sha256").read().split()[0], "sets": {}}; diffs = []
# ---- 180
per = {}; drops = {c: [] for c in ("tk2", "tk2fix")}
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True); ch_art = dict(db.execute("SELECT id, article_id FROM chunks").fetchall())
    facts = {}
    for it in load(f"{ST}/{p}.jsonl"):
        fa = it["source"]["article_id"]; fcs = set()
        for f in it["in_pack_facts"]:
            if f.get("chunk_index") is None: continue
            cs = [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (f.get("article", fa),))]
            if f["chunk_index"] < len(cs): fcs.add(cs[f["chunk_index"]])
        facts[it["id"]] = (fa, fcs)
    P = {c: passes(load(f"{A}/runs/st-{p}.{c}.jsonl")) for c in CELLS}
    o = {"n": {c: len(P[c][0]) for c in CELLS}, "repeat_identical": {c: rep(P[c]) for c in CELLS}}
    for c in CELLS:
        L = P[c][0]; s = {"chunk_raw6": 0, "chunk_kept": 0, "art_raw6": 0, "art_kept": 0, "empty_kept": 0, "kept_slots": 0, "own_kept_slots": 0, "articles_kept": 0}
        for i, (fa, fcs) in facts.items():
            l = L[i]; raw = [cid(x, p) for x in l["raw"][:K]]; kept = [cid(x, p) for x in l["kept"]]
            s["chunk_raw6"] += any(x in fcs for x in raw if x); s["art_raw6"] += any(ch_art.get(x) == fa for x in raw if x)
            s["chunk_kept"] += any(x in fcs for x in kept if x); s["art_kept"] += any(ch_art.get(x) == fa for x in kept if x)
            s["empty_kept"] += (l["raw"] != [] and not l["kept"]); s["kept_slots"] += len(l["kept"])
            s["own_kept_slots"] += sum(1 for x in kept if x); s["articles_kept"] += len({x.get("title") for x in l["kept"]})
        o[c] = s
    for c in ("tk2", "tk2fix"):
        same = 0
        for i in facts:
            a, b = P["cut7"][0][i], P[c][0][i]; same += ids(a) == ids(b)
            ka, kb = [x for x in ids(a) if cid({"chunkId": x}, p)], set(ids(b))
            lost = [x for x in ka if x not in kb]
            if lost:
                d = {"pack": p, "id": i, "lost_own": len(lost), "raw_same": ids(a, "raw") == ids(b, "raw"),
                     "route_same": route(a)[:3] == route(b)[:3], "kept_cut7": len(ids(a)), f"kept_{c}": len(ids(b)),
                     "fact_chunk_lost": any(cid({"chunkId": x}, p) in facts[i][1] for x in lost) and not any(cid({"chunkId": x}, p) in facts[i][1] for x in kb if cid({"chunkId": x}, p))}
                drops[c].append(d)
            if ids(a) != ids(b) or ids(a, "raw") != ids(b, "raw"):
                diffs.append({"set": "st", "cell": c, "pack": p, "id": i, "kept_same": ids(a) == ids(b), "raw_same": ids(a, "raw") == ids(b, "raw"),
                              "dropped": [[x["chunkId"], x["title"]] for x in a["kept"] if x["chunkId"] not in kb],
                              "added": [[x["chunkId"], x["title"]] for x in b["kept"] if x["chunkId"] not in set(ids(a))]})
        o[f"kept_same_{c}"] = same
        o[f"raw_same_{c}"] = sum(ids(P["cut7"][0][i], "raw") == ids(P[c][0][i], "raw") for i in facts)
        o[f"prompt_same_{c}"] = sum(P["cut7"][0][i].get("promptSha") == P[c][0][i].get("promptSha") for i in facts)
    per[p] = o
tot = {}
for k, v in per[PACKS[0]].items():
    if isinstance(v, dict): tot[k] = {kk: sum(per[p][k][kk] for p in PACKS) for kk in v}
    else: tot[k] = sum(per[p][k] for p in PACKS)
res["sets"]["st180"] = {"per_pack": per, "total": tot,
    "own_drop_items": {c: len(drops[c]) for c in drops}, "own_drop_items_same_raw": {c: sum(d["raw_same"] for d in drops[c]) for c in drops},
    "own_drop_detail": drops}
# ---- v0.1
G = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list) and v}
P = {c: passes(load(f"{A}/runs/v01-kit.{c}.jsonl")) for c in CELLS}
o = {"n": {c: len(P[c][0]) for c in CELLS}, "repeat_identical": {c: rep(P[c]) for c in CELLS}}
for c in CELLS:
    L = P[c][0]
    o[c] = {"gold_raw6": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["raw"][:6]) for i in G if i in L),
            "gold_kept": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["kept"]) for i in G if i in L),
            "empty_kept_retrieving": sum(1 for l in L.values() if l["raw"] and not l["kept"]), "kept_slots": sum(len(l["kept"]) for l in L.values())}
for c in ("tk2", "tk2fix"):
    aff = [i for i in P["cut7"][0] if route(P["cut7"][0][i]) != route(P[c][0][i])]
    unaff_diff = [i for i in P["cut7"][0] if i not in aff and ids(P["cut7"][0][i]) != ids(P[c][0][i])]
    harm = [i for i in G if i in P["cut7"][0] and any(gmatch(g, x) for g in G[i] for x in P["cut7"][0][i]["kept"]) and not any(gmatch(g, x) for g in G[i] for x in P[c][0][i]["kept"])]
    o[f"affected_{c}"] = aff; o[f"unaffected_kept_diff_{c}"] = unaff_diff; o[f"harm_{c}"] = harm
    o[f"kept_same_{c}"] = sum(ids(P["cut7"][0][i]) == ids(P[c][0][i]) for i in P["cut7"][0])
    o[f"prompt_same_{c}"] = sum(P["cut7"][0][i].get("promptSha") == P[c][0][i].get("promptSha") for i in P["cut7"][0])
res["sets"]["v01"] = o
# ---- gate (tk2fix)
t = res["sets"]["st180"]["total"]; v = res["sets"]["v01"]
g = {"G0": all(t["n"][c] == 180 and t["repeat_identical"][c] == 180 and v["n"][c] == 60 and v["repeat_identical"][c] == 60 for c in CELLS),
     "G1": t["tk2fix"]["chunk_kept"] >= t["cut7"]["chunk_kept"] + 5,
     "G2": sum(d["raw_same"] for d in drops["tk2fix"]) <= 5,
     "G3": not v["unaffected_kept_diff_tk2fix"] and not v["harm_tk2fix"]}
res["gate"] = {**g, "verdict": "PASS" if all(g.values()) else "FAIL",
               "G1_values": [t["cut7"]["chunk_kept"], t["tk2fix"]["chunk_kept"]], "G2_value": sum(d["raw_same"] for d in drops["tk2fix"])}
json.dump(res, open(f"{A}/aggregates/tk2fix-step0.json", "w"), indent=1)
with open(f"{A}/runs/diff-items.jsonl", "w") as f:
    for d in diffs: f.write(json.dumps(d) + "\n")
print(json.dumps(res["gate"])); print("total", json.dumps({c: t[c] for c in CELLS}))
print({k: t[k] for k in t if k.startswith(("kept_same", "raw_same", "prompt_same"))})
print("drops", res["sets"]["st180"]["own_drop_items"], res["sets"]["st180"]["own_drop_items_same_raw"])
print("v01", json.dumps({k: v[k] for k in v}))
for p in PACKS: print(p, {c: (per[p][c]["chunk_kept"], per[p][c]["art_kept"], per[p][c]["empty_kept"], per[p][c]["kept_slots"]) for c in CELLS}, per[p]["kept_same_tk2fix"])
