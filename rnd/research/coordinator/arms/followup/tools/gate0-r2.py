"""FOLLOWUP r2 step-0 gate (copy of gate0.py; modes off/anc, runs/replay-r2, G4 no-loss/no-displacement) -- was: FOLLOWUP step-0 gate (0 LLM) per FOLLOWUP-criterion.md: G0 infra/repeat, G1 OFF = wt/pr1, G2 turn-1 + v0.1 identity, G3 reach (gold chunk kept).
Usage: python3 -I gate0.py  -> aggregates/gate0.json + a short stdout summary."""
import json, re, sqlite3
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/followup"; O = f"{A}/runs/replay-r2"
P = [json.loads(l) for l in open(f"{A}/pairs.jsonl")]; PACKS = list(dict.fromkeys(p["pack"] for p in P))
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def passes(f):
    out = {}; seen = {}
    for l in load(f):
        k = (l["mode"], l["id"]); n = seen.get(k, 0); seen[k] = n + 1; out[(l["mode"], n, l["id"])] = l
    return out
ids = lambda l, f="kept": [x.get("chunkId") for x in l[f]]
sig = lambda l: json.dumps([ids(l), ids(l, "raw"), l.get("promptSha")])
sigc = lambda l: json.dumps([ids(l), ids(l, "raw"), l.get("promptSha"), l.get("codes")])
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
def cid(x, pack):
    m = CID.match(x or ""); return int(m.group(2)) if m and m.group(1) == pack else None
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
res = {"criterion_sha256": open(f"{A}/FOLLOWUP-R2-criterion.sha256").read().split()[0]}
g0 = {"missing": [], "repeat_diff": []}; g1 = {"diff": [], "n": 0}; g2 = {"diff": [], "n": 0, "fired": []}
items = []
def chk_repeat(D, iid, tag):
    for m in ("off", "anc"):
        a, b = D.get((m, 0, iid)), D.get((m, 1, iid))
        if a is None or b is None: g0["missing"].append(f"{tag}:{m}:{iid}"); continue
        if sig(a) != sig(b): g0["repeat_diff"].append(f"{tag}:{m}:{iid}")
for pk in PACKS:
    db = sqlite3.connect(f"file:{pub(pk)}?mode=ro", uri=True); art = dict(db.execute("SELECT id, article_id FROM chunks").fetchall())
    T1 = passes(f"{O}/t1-{pk}.anc.jsonl"); T2 = passes(f"{O}/t2-{pk}.anc.jsonl"); T2p = passes(f"{O}/t2-{pk}.pr1.jsonl")
    for p in P:
        if p["pack"] != pk: continue
        i1, i2 = f"{p['id']}-t1", f"{p['id']}-t2"
        chk_repeat(T1, i1, "t1"); chk_repeat(T2, i2, "t2")
        a, b = T1.get(("off", 0, i1)), T1.get(("anc", 0, i1)); g2["n"] += 1
        if a and b and sigc(a) != sigc(b): g2["diff"].append(i1)
        if b and any(c.startswith("followup:anchor") for c in b["codes"]): g2["fired"].append(i1)
        o, q = T2.get(("off", 0, i2)), T2p.get(("off", 0, i2)); g1["n"] += 1
        if o is None or q is None or sig(o) != sig(q): g1["diff"].append(i2)
        on = T2.get(("anc", 0, i2)); g = p["gold_chunk"]; ga = p["article_id"]
        row = {"id": p["id"], "pack": pk, "t2": p["t2"]}
        for tag, l in (("off", o), ("on", on)):
            kept = [cid(x, pk) for x in ids(l)]; raw = [cid(x, pk) for x in ids(l, "raw")[:6]]
            row[tag] = {"gold_kept": g in kept, "gold_raw6": g in raw, "art_kept": any(art.get(x) == ga for x in kept if x),
                        "t1fact_kept": any(x in p["t1_fact_chunks"] for x in kept if x), "n_kept": len(kept), "empty": not kept,
                        "fired": any(c.startswith("followup:anchor:") for c in l["codes"]), "fetched": next((int(c.split(":")[2]) for c in l["codes"] if c.startswith("followup:anchor:")), None),
                        "anchor_kept": "followup:anchor-kept" in l["codes"], "kept_ids": [cid(x, pk) if cid(x, pk) is not None else x for x in ids(l)],
                        "query": l.get("query"), "kept_titles": list(dict.fromkeys(x["title"] for x in l["kept"])), "task": l.get("task"),
                        "health": "grounding:health-strict" in l["codes"]}
        items.append(row)
V = passes(f"{O}/v01-kit.anc.jsonl"); Vp = passes(f"{O}/v01-kit.pr1.jsonl")
vids = sorted({k[2] for k in V})
for i in vids:
    chk_repeat(V, i, "v01"); g2["n"] += 1; g1["n"] += 1
    a, b = V.get(("off", 0, i)), V.get(("anc", 0, i))
    if a is None or b is None or sigc(a) != sigc(b): g2["diff"].append(i)
    if b and any(c.startswith("followup:anchor") for c in b["codes"]): g2["fired"].append(i)
    q = Vp.get(("off", 0, i))
    if a is None or q is None or sig(a) != sig(q): g1["diff"].append(i)
cnt = lambda arm, k: sum(r[arm][k] for r in items)
G3 = {k: {"off": cnt("off", k), "on": cnt("on", k)} for k in ("gold_kept", "gold_raw6", "art_kept", "t1fact_kept", "empty", "fired", "anchor_kept")}
G3["gained"] = [r["id"] for r in items if r["on"]["gold_kept"] and not r["off"]["gold_kept"]]
G3["lost"] = [r["id"] for r in items if r["off"]["gold_kept"] and not r["on"]["gold_kept"]]
G3["displaced"] = [r["id"] for r in items if not set(map(str, r["off"]["kept_ids"])) <= set(map(str, r["on"]["kept_ids"]))]
for r in items: r["anchor_added"] = [x for x in r["on"]["kept_ids"] if x not in r["off"]["kept_ids"]]
gates = {"G0": not g0["missing"] and not g0["repeat_diff"], "G1": not g1["diff"], "G2": not g2["diff"] and not g2["fired"],
         "G3": G3["gold_kept"]["on"] >= 7, "G4": not G3["lost"] and not G3["displaced"]}
res.update({"n_pairs": len(items), "n_v01": len(vids), "G0": g0, "G1": g1, "G2": g2, "G3": G3, "gates": gates, "PASS": all(gates.values()), "items": items})
json.dump(res, open(f"{A}/aggregates/gate0-r2.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({"gates": gates, "PASS": res["PASS"], "G3": {k: v for k, v in G3.items()}, "G1diff": g1["diff"][:10], "G2diff": g2["diff"][:10], "G2fired": g2["fired"], "G0": {k: v[:10] for k, v in g0.items()}}, indent=0))
