"""QMERGE step 0 compare (0 LLM; criterion QMERGE-criterion.md 78dfbd59...). Reach definitions = qwrite/tools/compare_qw.py.
Cells per file: off (pass 1), qm (pass 2), off2 (pass 3). Writes aggregates/compare.json + runs/changed.jsonl."""
import json, re, sqlite3, statistics as stt
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/qmerge"; ST = f"{ROOT}/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SE = [p for p in PACKS if p.startswith("qa-")]; TOPIC = [p for p in PACKS if p not in SE]
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
def cid(ref, pack):
    m = CID.match(ref.get("chunkId") or ""); return int(m.group(2)) if m and m.group(1) == pack else None
full = lambda l: json.dumps([[[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]],
                             [[x.get("chunkId"), x.get("title"), x.get("section")] for x in l["kept"]], l.get("promptSha"), l["task"], l["query"], l["k"],
                             [x.get("chunkId") for x in l.get("pool") or []], l.get("codes")])
ids = lambda l, f="kept": [x.get("chunkId") for x in l.get(f) or []]
merged = lambda l: any(c.startswith("qmerge:candidates:") for c in l.get("qmCodes") or [])
codeval = lambda l, pre: next((int(c.split(":")[-1]) for c in l.get("qmCodes") or [] if c.startswith(pre)), None)
def cells(path):
    C = {}; seen = {}
    for l in load(path):
        n = seen.get(l["id"], 0); seen[l["id"]] = n + 1; C.setdefault(("off", "qm", "off2")[n], {})[l["id"]] = l
    return C
CN = ("off", "qm", "off2"); KEYS = ("chunk_raw6", "chunk_top8", "chunk_kept", "art_raw6", "art_kept", "empty_kept", "health_strict")
res = {"per_pack": {}}; changed = []; L = {k: [] for k in ("displaced", "gained_kept", "lost_art", "gained_art", "skip_not_identical")}
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True); ch_art = dict(db.execute("SELECT id, article_id FROM chunks").fetchall())
    titles = dict(db.execute("SELECT id, title FROM articles").fetchall()); facts = {}
    for it in load(f"{ST}/{p}.jsonl"):
        fa = it["source"]["article_id"]; fcs = set()
        for f in it["in_pack_facts"]:
            if f.get("chunk_index") is None: continue
            cs = [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (f.get("article", fa),))]
            if f["chunk_index"] < len(cs): fcs.add(cs[f["chunk_index"]])
        facts[it["id"]] = (fa, fcs)
    C = cells(f"{A}/runs/st-{p}.qm.jsonl")
    def m(l, fa, fcs):
        raw = [cid(x, p) for x in l["raw"][:6]]; pool = [cid(x, p) for x in (l.get("pool") or [])[:8]]; kept = [cid(x, p) for x in l["kept"]]
        return {"chunk_raw6": any(x in fcs for x in raw if x), "chunk_top8": any(x in fcs for x in raw + pool if x),
                "chunk_kept": any(x in fcs for x in kept if x), "art_raw6": any(ch_art.get(x) == fa for x in raw if x),
                "art_kept": any(ch_art.get(x) == fa for x in kept if x), "empty_kept": bool(l["raw"]) and not l["kept"],
                "health_strict": "grounding:health-strict" in (l.get("codes") or [])}
    o = {"n": len(facts)}
    for c in CN:
        o[c] = {k: sum(int(m(C[c][i], *facts[i])[k]) for i in facts) for k in KEYS}
        o[c]["kept_slots"] = sum(len(C[c][i]["kept"]) for i in facts); o[c]["kept_tokens"] = sum(C[c][i].get("keptTokens") or 0 for i in facts)
    o["off_vs_off2_identical"] = sum(full(C["off"][i]) == full(C["off2"][i]) for i in facts)
    o["merged_items"] = sum(merged(C["qm"][i]) for i in facts)
    o["skipped_identical"] = sum(full(C["off"][i]) == full(C["qm"][i]) for i in facts if not merged(C["qm"][i]))
    o["skipped"] = len(facts) - o["merged_items"]
    o["kept_same"] = sum(ids(C["off"][i]) == ids(C["qm"][i]) for i in facts)
    o["kept_from_rewrite_items"] = sum((codeval(C["qm"][i], "qmerge:kept-from-rewrite:") or 0) > 0 for i in facts)
    o["kept_from_rewrite_slots"] = sum(codeval(C["qm"][i], "qmerge:kept-from-rewrite:") or 0 for i in facts)
    o["candidates"] = [codeval(C["qm"][i], "qmerge:candidates:") for i in facts if merged(C["qm"][i])]
    o["raw_off"] = [len(C["off"][i]["raw"]) for i in facts if merged(C["qm"][i])]
    o["ret_ms_off"] = [C["off"][i]["ms"] for i in facts if C["off"][i]["ms"] is not None]
    for i, (fa, fcs) in facts.items():
        a, b = m(C["off"][i], fa, fcs), m(C["qm"][i], fa, fcs)
        if not merged(C["qm"][i]) and full(C["off"][i]) != full(C["qm"][i]): L["skip_not_identical"].append(i)
        if a["chunk_kept"] and not b["chunk_kept"]: L["displaced"].append(i)
        if b["chunk_kept"] and not a["chunk_kept"]: L["gained_kept"].append(i)
        if a["art_kept"] and not b["art_kept"]: L["lost_art"].append(i)
        if b["art_kept"] and not a["art_kept"]: L["gained_art"].append(i)
        ch = {k: [a[k], b[k]] for k in a if a[k] != b[k]}
        if ch or ids(C["off"][i]) != ids(C["qm"][i]):
            changed.append({"pack": p, "id": i, "fact_article": titles.get(fa), "changes": ch, "query": C["off"][i]["query"], "qmCodes": C["qm"][i].get("qmCodes"),
                            "off_kept": [x["title"] for x in C["off"][i]["kept"]], "qm_kept": [x["title"] for x in C["qm"][i]["kept"]],
                            "raw2": [x["title"] for x in C["qm"][i].get("raw2") or []]})
    res["per_pack"][p] = o
def tot(ps):
    t = {c: {k: sum(res["per_pack"][p][c][k] for p in ps) for k in KEYS + ("kept_slots", "kept_tokens")} for c in CN}
    for k in ("n", "off_vs_off2_identical", "merged_items", "skipped", "skipped_identical", "kept_same", "kept_from_rewrite_items", "kept_from_rewrite_slots"):
        t[k] = sum(res["per_pack"][p][k] for p in ps)
    cand = sum((res["per_pack"][p]["candidates"] for p in ps), []); ro = sum((res["per_pack"][p]["raw_off"] for p in ps), [])
    t["candidates_p50"] = stt.median(cand) if cand else None; t["raw_off_p50_on_merged"] = stt.median(ro) if ro else None
    return t
res["total"] = tot(PACKS); res["SE"] = tot(SE); res["topic"] = tot(TOPIC)
for p in PACKS:
    for k in ("candidates", "raw_off", "ret_ms_off"): res["per_pack"][p].pop(k)
# ---- v0.1 (gold/sources.json rule of scorers/retrieval.py: title (+ section) match, library prefix stripped)
gold = json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")); gold.pop("_about", None)
norm = lambda s: " ".join(str(s or "").split()).lower(); LIB = re.compile(r"^[^:]{2,40}:\s+")
def gm(g, r):
    t, _, sec = g.partition("#")
    if norm(t) != norm(r["title"]) and (LIB.match(t) or norm(t) != norm(LIB.sub("", r["title"]))): return False
    return not sec or norm(sec) == norm(r.get("section"))
V = cells(f"{A}/runs/v01.qm.jsonl"); vid = list(V["off"])
gk = lambda l, i: any(gm(g, r) for g in gold.get(i, []) for r in l["kept"])
v = {"n": len(vid), "off_vs_off2_identical": sum(full(V["off"][i]) == full(V["off2"][i]) for i in vid),
     "merged_items": sum(merged(V["qm"][i]) for i in vid),
     "skipped_identical": sum(full(V["off"][i]) == full(V["qm"][i]) for i in vid if not merged(V["qm"][i])),
     "skipped": sum(not merged(V["qm"][i]) for i in vid), "gold_items": sum(i in gold for i in vid),
     "kept_diff": sum(ids(V["off"][i]) != ids(V["qm"][i]) for i in vid),
     "gold_kept_off": sum(gk(V["off"][i], i) for i in vid), "gold_kept_qm": sum(gk(V["qm"][i], i) for i in vid),
     "gold_kept_lost": [i for i in vid if gk(V["off"][i], i) and not gk(V["qm"][i], i)],
     "gold_kept_gained": [i for i in vid if gk(V["qm"][i], i) and not gk(V["off"][i], i)],
     "kept_slots_off": sum(len(V["off"][i]["kept"]) for i in vid), "kept_slots_qm": sum(len(V["qm"][i]["kept"]) for i in vid),
     "kept_from_rewrite_items": sum((codeval(V["qm"][i], "qmerge:kept-from-rewrite:") or 0) > 0 for i in vid),
     "prompt_changed": sum(V["off"][i].get("promptSha") != V["qm"][i].get("promptSha") for i in vid),
     "skip_not_identical": [i for i in vid if not merged(V["qm"][i]) and full(V["off"][i]) != full(V["qm"][i])]}
res["v01"] = v
T = res["total"]; d = T["qm"]["chunk_kept"] - T["off"]["chunk_kept"]
g = {"G0_off_identical": T["off_vs_off2_identical"], "G0_v01_identical": v["off_vs_off2_identical"],
     "G0_skip_identity": [T["skipped_identical"], T["skipped"], v["skipped_identical"], v["skipped"]],
     "G0_pass": T["off_vs_off2_identical"] == 180 and v["off_vs_off2_identical"] == 60 and not L["skip_not_identical"] and not v["skip_not_identical"],
     "off_kept_vs_tk2off_ref_35": T["off"]["chunk_kept"],
     "G1_kept_gain": d, "G1_pass": d >= 10,
     "G2_art_kept": [T["off"]["art_kept"], T["qm"]["art_kept"]], "G2_pass": T["qm"]["art_kept"] >= T["off"]["art_kept"],
     "G3_displaced": L["displaced"], "G3_pass": len(L["displaced"]) <= 3,
     "G4_gold_kept": [v["gold_kept_off"], v["gold_kept_qm"]], "G4_lost": v["gold_kept_lost"],
     "G4_pass": v["gold_kept_qm"] >= v["gold_kept_off"] and len(v["gold_kept_lost"]) <= 1, **{k: L[k] for k in ("gained_kept", "lost_art", "gained_art")}}
g["PASS"] = all(g[k] for k in ("G0_pass", "G1_pass", "G2_pass", "G3_pass", "G4_pass")); res["gate"] = g
json.dump(res, open(f"{A}/aggregates/compare.json", "w"), indent=1)
with open(f"{A}/runs/changed.jsonl", "w") as f:
    for x in changed: f.write(json.dumps(x) + "\n")
for k in ("total", "SE", "topic"): print(k, json.dumps(res[k]))
for p in PACKS: print(p, {c: {k: res["per_pack"][p][c][k] for k in ("chunk_top8", "chunk_kept", "art_kept", "empty_kept")} for c in ("off", "qm")}, "merged", res["per_pack"][p]["merged_items"])
print("v01", json.dumps(v)); print("gate", json.dumps(g))
