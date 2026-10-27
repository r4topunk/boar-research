"""QWRITE step 0 compare (0 LLM; criterion 80695f6a...). Reach definitions = h8st/tools/compare_h8.py (fact chunks = in_pack_facts
chunk_index over the article's chunks by start, item pack only; raw6 = raw[:6]; top8 = raw[:6] or pool[:8]). Cells from one file
per pack: off (pass 1), qw (pass 2), off2 (pass 3). Writes aggregates/compare.json + runs/changed.jsonl."""
import json, re, sqlite3, statistics as stt
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/qwrite"; ST = f"{ROOT}/rnd/research/packs/selftest"
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
                             [x.get("chunkId") for x in l.get("pool") or []]])
ids = lambda l, f="kept": [x.get("chunkId") for x in l.get(f) or []]
qmap = json.load(open(f"{A}/runs/qmap.json")); CN = ("off", "qw", "off2"); KEYS = ("chunk_raw6", "chunk_top8", "chunk_kept", "art_raw6", "art_kept", "empty_kept")
res = {"per_pack": {}}; changed = []; lost_top8 = []; gained_top8 = []; lost_kept = []; gained_kept = []; qcheck = 0
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
    C = {}; seen = {}
    for l in load(f"{A}/runs/st-{p}.qw.jsonl"):
        n = seen.get(l["id"], 0); seen[l["id"]] = n + 1; C.setdefault(CN[n], {})[l["id"]] = l
    def m(l, fa, fcs):
        raw = [cid(x, p) for x in l["raw"][:6]]; pool = [cid(x, p) for x in (l.get("pool") or [])[:8]]; kept = [cid(x, p) for x in l["kept"]]
        return {"chunk_raw6": any(x in fcs for x in raw if x), "chunk_top8": any(x in fcs for x in raw + pool if x),
                "chunk_kept": any(x in fcs for x in kept if x), "art_raw6": any(ch_art.get(x) == fa for x in raw if x),
                "art_kept": any(ch_art.get(x) == fa for x in kept if x), "empty_kept": bool(l["raw"]) and not l["kept"]}
    o = {"n": len(facts)}
    for c in CN:
        o[c] = {k: sum(int(m(C[c][i], *facts[i])[k]) for i in facts) for k in KEYS}
        o[c]["kept_slots"] = sum(len(C[c][i]["kept"]) for i in facts); o[c]["arts_kept"] = sum(len({x.get("title") for x in C[c][i]["kept"]}) for i in facts)
        o[c]["ms_p50"] = round(stt.median([C[c][i]["ms"] for i in facts if C[c][i]["ms"] is not None] or [0]), 1)
    o["off_vs_off2_identical"] = sum(full(C["off"][i]) == full(C["off2"][i]) for i in facts)
    o["qw_raw_same"] = sum(ids(C["off"][i], "raw") == ids(C["qw"][i], "raw") for i in facts)
    o["qw_kept_same"] = sum(ids(C["off"][i]) == ids(C["qw"][i]) for i in facts)
    for i, (fa, fcs) in facts.items():
        if i in qmap and C["qw"][i]["query"] == qmap[i]: qcheck += 1
        a, b = m(C["off"][i], fa, fcs), m(C["qw"][i], fa, fcs)
        if a["chunk_top8"] and not b["chunk_top8"]: lost_top8.append(i)
        if b["chunk_top8"] and not a["chunk_top8"]: gained_top8.append(i)
        if a["chunk_kept"] and not b["chunk_kept"]: lost_kept.append(i)
        if b["chunk_kept"] and not a["chunk_kept"]: gained_kept.append(i)
        ch = {k: [a[k], b[k]] for k in a if a[k] != b[k]}
        if ch: changed.append({"pack": p, "id": i, "fact_article": titles.get(fa), "changes": ch, "off_query": C["off"][i]["query"], "qw_query": C["qw"][i]["query"],
                               "off_raw": [x["title"] for x in C["off"][i]["raw"]], "qw_raw": [x["title"] for x in C["qw"][i]["raw"]]})
    res["per_pack"][p] = o
def tot(ps):
    t = {c: {k: sum(res["per_pack"][p][c][k] for p in ps) for k in KEYS + ("kept_slots", "arts_kept")} for c in CN}
    for k in ("n", "off_vs_off2_identical", "qw_raw_same", "qw_kept_same"): t[k] = sum(res["per_pack"][p][k] for p in ps)
    return t
res["total"] = tot(PACKS); res["SE"] = tot(SE); res["topic"] = tot(TOPIC)
T = res["total"]; d8 = T["qw"]["chunk_top8"] - T["off"]["chunk_top8"]
res["gate"] = {"qmap_items": len(qmap), "qw_lines_using_qmap": qcheck, "G0_identity": T["off_vs_off2_identical"], "G0_off_top8": T["off"]["chunk_top8"],
               "G0_pass": T["off_vs_off2_identical"] == 180 and abs(T["off"]["chunk_top8"] - 69) <= 3,
               "top8_gain": d8, "lost_top8": lost_top8, "gained_top8": gained_top8, "lost_kept": lost_kept, "gained_kept": gained_kept,
               "G1_pass": d8 >= 15 and len(lost_top8) <= 5}
json.dump(res, open(f"{A}/aggregates/compare.json", "w"), indent=1)
with open(f"{A}/runs/changed.jsonl", "w") as f:
    for d in changed: f.write(json.dumps(d) + "\n")
for k in ("total", "SE", "topic"): print(k, json.dumps(res[k]))
for p in PACKS: print(p, {c: {k: res["per_pack"][p][c][k] for k in ("chunk_raw6", "chunk_top8", "chunk_kept", "art_kept", "empty_kept")} for c in ("off", "qw")})
print("gate", json.dumps(res["gate"]))
