"""H8-ST step 0 compare (0 LLM; criterion sha 3765405d...). Cells: REF = tk2off tree + published packs (off); H8 tree + h8proto
copies: off (pass 1), lead (pass 2, BOAR_H8_INDEX=lead), off2 (pass 3, repeat identity). Reach definitions = tk2-replay
compare_tk2.py / packroute step0.py: fact chunks = in_pack_facts chunk_index over the article's chunks by start; fact
article = source.article_id; item pack's chunks only (chunkId prefix). raw6 = raw[:6] (raw has k <= 6 chunks, so = whole raw);
top8 = fact chunk in raw[:6] OR in pool[:8] (the replay's --pool 8: an extra retrieve(query, 8) not returned to the engine).
Writes aggregates/compare.json + runs/newly.jsonl. Public sets only."""
import json, re, sqlite3, statistics as stt, os, sys
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/h8st"; ST = f"{ROOT}/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SE = [p for p in PACKS if p.startswith("qa-")]; TOPIC = [p for p in PACKS if p not in SE]
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
def cid(ref, pack):
    m = CID.match(ref.get("chunkId") or ""); return int(m.group(2)) if m and m.group(1) == pack else None
def cells(ref_f, h8_f):
    out = {"ref": {l["id"]: l for l in load(ref_f)}}; seen = {}
    for l in load(h8_f):
        n = seen.get(l["id"], 0); seen[l["id"]] = n + 1; out.setdefault(["off", "lead", "off2"][n], {})[l["id"]] = l
    return out
ids = lambda l, f="kept": [x.get("chunkId") for x in l.get(f) or []]
full = lambda l: json.dumps([[[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]],
                             [[x.get("chunkId"), x.get("title"), x.get("section")] for x in l["kept"]], l.get("promptSha"), l["task"], l["query"], l["k"]])
p50 = lambda xs: round(stt.median([x for x in xs if x is not None]), 1) if any(x is not None for x in xs) else None
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).lower(); bare = lambda t: _LIB.sub("", str(t or ""))
def gmatch(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
res = {"st180": {"per_pack": {}}, "v01": {}}; newly = []
CN = ("ref", "off", "lead", "off2")
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True); ch_art = dict(db.execute("SELECT id, article_id FROM chunks").fetchall())
    titles = dict(db.execute("SELECT id, title FROM articles").fetchall())
    facts = {}
    for it in load(f"{ST}/{p}.jsonl"):
        fa = it["source"]["article_id"]; fcs = set()
        for f in it["in_pack_facts"]:
            if f.get("chunk_index") is None: continue
            cs = [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (f.get("article", fa),))]
            if f["chunk_index"] < len(cs): fcs.add(cs[f["chunk_index"]])
        facts[it["id"]] = (fa, fcs)
    C = cells(f"{A}/runs/st-{p}.ref.jsonl", f"{A}/runs/st-{p}.h8.jsonl")
    o = {"n": len(facts)}
    def m(l, fa, fcs):
        raw = [cid(x, p) for x in l["raw"][:6]]; pool = [cid(x, p) for x in (l.get("pool") or [])[:8]]; kept = [cid(x, p) for x in l["kept"]]
        return {"chunk_raw6": any(x in fcs for x in raw if x), "chunk_top8": any(x in fcs for x in raw + pool if x),
                "chunk_kept": any(x in fcs for x in kept if x), "art_kept": any(ch_art.get(x) == fa for x in kept if x),
                "art_raw6": any(ch_art.get(x) == fa for x in raw if x), "empty_kept": bool(l["raw"]) and not l["kept"]}
    for c in CN:
        s = {}; ms = []
        for i, (fa, fcs) in facts.items():
            for k, v in m(C[c][i], fa, fcs).items(): s[k] = s.get(k, 0) + int(v)
            ms.append(C[c][i]["ms"])
        s["kept_slots"] = sum(len(C[c][i]["kept"]) for i in facts); s["ms_p50"] = p50(ms); s["ms_list"] = ms; o[c] = s
    o["ref_vs_off_identical"] = sum(full(C["ref"][i]) == full(C["off"][i]) for i in facts)
    o["off_vs_off2_identical"] = sum(full(C["off"][i]) == full(C["off2"][i]) for i in facts)
    o["lead_kept_same"] = sum(ids(C["off"][i]) == ids(C["lead"][i]) for i in facts)
    o["lead_raw_same"] = sum(ids(C["off"][i], "raw") == ids(C["lead"][i], "raw") for i in facts)
    for i, (fa, fcs) in facts.items():
        a, b = m(C["off"][i], fa, fcs), m(C["lead"][i], fa, fcs)
        ch = {k: [a[k], b[k]] for k in a if a[k] != b[k]}
        if ch: newly.append({"pack": p, "id": i, "fact_article": titles.get(fa), "changes": ch,
                             "off_raw": [x["title"] for x in C["off"][i]["raw"]], "lead_raw": [x["title"] for x in C["lead"][i]["raw"]],
                             "off_kept": [x["title"] for x in C["off"][i]["kept"]], "lead_kept": [x["title"] for x in C["lead"][i]["kept"]], "query": C["off"][i]["query"]})
    res["st180"]["per_pack"][p] = o
def tot(ps):
    t = {}
    for c in CN:
        t[c] = {k: sum(res["st180"]["per_pack"][p][c][k] for p in ps) for k in res["st180"]["per_pack"][ps[0]][c] if k not in ("ms_p50", "ms_list")}
        t[c]["ms_p50"] = p50(sum((res["st180"]["per_pack"][p][c]["ms_list"] for p in ps), []))
    for k in ("ref_vs_off_identical", "off_vs_off2_identical", "lead_kept_same", "lead_raw_same", "n"): t[k] = sum(res["st180"]["per_pack"][p][k] for p in ps)
    return t
res["st180"]["total"] = tot(PACKS); res["st180"]["SE"] = tot(SE); res["st180"]["topic"] = tot(TOPIC)
for p in PACKS:
    for c in CN: res["st180"]["per_pack"][p][c].pop("ms_list")
# v0.1 kit only
G = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list) and v}
C = cells(f"{A}/runs/v01-kit.ref.jsonl", f"{A}/runs/v01-kit.h8.jsonl"); o = {"n": len(C["ref"])}
KIT = ("boar-crypto", "boar-wikivoyage-en")
for c in CN:
    L = C[c]
    o[c] = {"gold_raw6": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["raw"][:6]) for i in G if i in L),
            "gold_kept": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["kept"]) for i in G if i in L),
            "empty_kept_retrieving": sum(1 for l in L.values() if l["raw"] and not l["kept"]),
            "kit_kept_slots": sum(1 for l in L.values() for x in l["kept"] if any(f"pack:{k}:" in (x.get("chunkId") or "") or f"pack:local-{k}:" in (x.get("chunkId") or "") for k in KIT)),
            "kept_slots": sum(len(l["kept"]) for l in L.values()), "ms_p50": p50([l["ms"] for l in L.values()])}
# kit lost-context: items whose OFF kept a kit chunk and LEAD kept none
o["kit_lost_context"] = [i for i in C["off"] if any("pack:" in (x.get("chunkId") or "") for x in C["off"][i]["kept"]) and not any("pack:" in (x.get("chunkId") or "") for x in C["lead"][i]["kept"])]
o["ref_vs_off_identical"] = sum(full(C["ref"][i]) == full(C["off"][i]) for i in C["ref"])
o["off_vs_off2_identical"] = sum(full(C["off"][i]) == full(C["off2"][i]) for i in C["ref"])
o["lead_kept_same"] = sum(ids(C["off"][i]) == ids(C["lead"][i]) for i in C["ref"])
o["lead_raw_same"] = sum(ids(C["off"][i], "raw") == ids(C["lead"][i], "raw") for i in C["ref"])
o["gold_changed_ids"] = [i for i in G if i in C["off"] and (any(gmatch(g, x) for g in G[i] for x in C["off"][i]["kept"]) != any(gmatch(g, x) for g in G[i] for x in C["lead"][i]["kept"]) or any(gmatch(g, x) for g in G[i] for x in C["off"][i]["raw"][:6]) != any(gmatch(g, x) for g in G[i] for x in C["lead"][i]["raw"][:6]))]
res["v01"] = o
os.makedirs(f"{A}/aggregates", exist_ok=True); json.dump(res, open(f"{A}/aggregates/compare.json", "w"), indent=1)
with open(f"{A}/runs/newly.jsonl", "w") as f:
    for d in newly: f.write(json.dumps(d) + "\n")
for k in ("total", "SE", "topic"): print(k, json.dumps(res["st180"][k]))
for p in PACKS:
    r = res["st180"]["per_pack"][p]; print(p, {c: {k: r[c][k] for k in ("chunk_raw6", "chunk_top8", "chunk_kept", "art_kept", "empty_kept", "ms_p50")} for c in ("ref", "off", "lead")},
                                       "ref=off", r["ref_vs_off_identical"], "off=off2", r["off_vs_off2_identical"], "keptSame", r["lead_kept_same"], "rawSame", r["lead_raw_same"])
print("v01", json.dumps(o)); print("changed items", len(newly))
