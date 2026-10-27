"""MICROD2Q compare (0 LLM; criterion sha 5988da96...). Reach definitions = h8st compare_h8.py (fact chunks = selftest in_pack_facts
chunk_index over the article's chunks by start; item pack's chunks only; raw6 = raw[:6]; top8 = raw[:6] OR pool[:8]).
Cells: ref = runs/id-<set>.jsonl pass 1 (published packs), off/x1/x2/off2 = runs/<set>.full.jsonl, dx1/dx2 = runs/<set>.deinfl.jsonl.
Split over the 137 (diag137.json best.cls): lexical 27, gate 21, article 56, other 33; kept43 = the 43 ORACLE-kept items.
G1/G2/G3 per the criterion. Writes aggregates/compare.json + runs/changed.jsonl."""
import json, re, sqlite3, statistics as stt, os
ROOT = "<workspace>"; ARMS = f"{ROOT}/rnd/research/coordinator/arms"; A = f"{ARMS}/microd2q"; ST = f"{ROOT}/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
load = lambda f: [json.loads(l) for l in open(f) if l.strip()] if os.path.exists(f) else []
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
CID = re.compile(r"^pack:(?:local-)?([^:]+):(\d+)$")
def cid(ref, pack):
    m = CID.match(ref.get("chunkId") or ""); return int(m.group(2)) if m and m.group(1) == pack else None
DATE = re.compile(r"Today is \w+, \d+ \w+ \d{4}")
sig = lambda l: json.dumps([[[x.get(k) for k in ("chunkId", "title", "section", "source", "similarity", "via")] for x in l["raw"]],
                            [[x.get("chunkId"), x.get("title"), x.get("section")] for x in l["kept"]], DATE.sub("D", l.get("prompt") or ""), l["task"], l["query"], l["k"]])
def passes(f, names):
    out, seen = {}, {}
    for l in load(f):
        n = seen.get(l["id"], 0); seen[l["id"]] = n + 1; out.setdefault(names[n], {})[l["id"]] = l
    return out
D = {x["id"]: x for x in json.load(open(f"{ARMS}/h8st/tools/diag/diag137.json"))}
def split(i):
    x = D[i]
    if x["S_kept_ST2"]: return "kept43"
    c = x["best"]["cls"]
    return "lexical" if c.startswith("lexical") else "gate" if c == "relevance_gate" else "article" if c in ("article_cap", "article_found_other_chunk") else "other"
CELLS = ["ref", "off", "x1", "x2", "off2", "dx1", "dx2"]; KEYS = ["chunk_raw6", "chunk_top8", "chunk_kept", "art_kept", "empty_kept"]
per_item = {}; ms = {c: [] for c in CELLS}; ident = {"ref_off": 0, "off_off2": 0, "n": 0}; changed = []
for p in PACKS:
    db = sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True); ch_art = dict(db.execute("SELECT id, article_id FROM chunks").fetchall())
    C = {"ref": passes(f"{A}/runs/id-st-{p}.jsonl", ["ref", "_"]).get("ref", {})}
    C.update(passes(f"{A}/runs/st-{p}.full.jsonl", ["off", "x1", "x2", "off2"])); C.update(passes(f"{A}/runs/st-{p}.deinfl.jsonl", ["dx1", "dx2"]))
    for it in load(f"{ST}/{p}.jsonl"):
        i = it["id"]; fa = it["source"]["article_id"]; fcs = set()
        for f in it["in_pack_facts"]:
            if f.get("chunk_index") is None: continue
            cs = [r[0] for r in db.execute("SELECT id FROM chunks WHERE article_id=? ORDER BY start", (f.get("article", fa),))]
            if f["chunk_index"] < len(cs): fcs.add(cs[f["chunk_index"]])
        row = {"pack": p, "split": split(i), "family": "SE" if p.startswith("qa-") else "topic"}
        for c in CELLS:
            if i not in C.get(c, {}): continue
            l = C[c][i]; raw = [cid(x, p) for x in l["raw"][:6]]; pool = [cid(x, p) for x in (l.get("pool") or [])[:8]]; kept = [cid(x, p) for x in l["kept"]]
            row[c] = {"chunk_raw6": any(x in fcs for x in raw if x), "chunk_top8": any(x in fcs for x in raw + pool if x), "chunk_kept": any(x in fcs for x in kept if x),
                      "art_kept": any(ch_art.get(x) == fa for x in kept if x), "empty_kept": bool(l["raw"]) and not l["kept"]}
            ms[c].append(l["ms"])
        if "off" in C and i in C["off"]:
            ident["n"] += 1; ident["ref_off"] += sig(C["ref"][i]) == sig(C["off"][i]); ident["off_off2"] += sig(C["off"][i]) == sig(C["off2"][i])
            for c in ("x1", "x2"):
                d = {k: [row["off"][k], row[c][k]] for k in KEYS if row["off"][k] != row[c][k]}
                if d: changed.append({"id": i, "cell": c, "split": row["split"], "changes": d, "off_kept": [x["title"] for x in C["off"][i]["kept"]], c + "_kept": [x["title"] for x in C[c][i]["kept"]]})
        per_item[i] = row
def tot(f):
    return {c: {k: sum(int(r[c][k]) for i, r in per_item.items() if f(i, r) and c in r) for k in KEYS} for c in CELLS}
res = {"identity": ident, "total": tot(lambda i, r: True), "SE": tot(lambda i, r: r["family"] == "SE"), "topic": tot(lambda i, r: r["family"] == "topic"),
       "split": {s: dict(n=sum(1 for r in per_item.values() if r["split"] == s), **tot(lambda i, r, s=s: r["split"] == s)) for s in ("lexical", "gate", "article", "other", "kept43")},
       "ms_p50": {c: round(stt.median([x for x in v if x is not None]), 1) for c, v in ms.items() if any(x is not None for x in v)}}
infl = json.load(open(f"{A}/aggregates/deinfl-items.json")) if os.path.exists(f"{A}/aggregates/deinfl-items.json") else []
if infl:
    res["deinfl_removed_items"] = len(infl)
    res["reach_without_removed_items"] = tot(lambda i, r: i not in infl)
# v0.1
G = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list) and v}
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).lower(); bare = lambda t: _LIB.sub("", str(t or ""))
def gm(gold, ref):
    title, _, section = gold.partition("#")
    if norm(title) != norm(ref.get("title")) and (_LIB.match(title) or norm(title) != norm(bare(ref.get("title")))): return False
    return not section or norm(section) == norm(ref.get("section"))
V = {"ref": passes(f"{A}/runs/id-v01-kit.jsonl", ["ref", "_"]).get("ref", {})}; V.update(passes(f"{A}/runs/v01-kit.full.jsonl", ["off", "x1", "x2", "off2"]))
res["v01"] = {c: {"gold_raw6": sum(any(gm(g, x) for g in G[i] for x in L[i]["raw"][:6]) for i in G if i in L),
                  "gold_kept": sum(any(gm(g, x) for g in G[i] for x in L[i]["kept"]) for i in G if i in L),
                  "empty_kept": sum(1 for l in L.values() if l["raw"] and not l["kept"]), "ms_p50": round(stt.median([l["ms"] for l in L.values() if l["ms"] is not None]), 1),
                  "same_as_off": sum(sig(L[i]) == sig(V["off"][i]) for i in L) if "off" in V else None} for c, L in V.items() if L}
# gates
t = res["total"]; v = res["v01"]
res["G1"] = {c: {"top8": t[c]["chunk_top8"], "kept": t[c]["chunk_kept"], "kept_off": t["off"]["chunk_kept"], "pass": t[c]["chunk_top8"] >= 90 and t[c]["chunk_kept"] >= t["off"]["chunk_kept"] + 15} for c in ("x1", "x2")}
res["G2"] = {c: {"pass": v[c]["gold_kept"] >= v["off"]["gold_kept"] and v[c]["gold_raw6"] >= v["off"]["gold_raw6"] and v[c]["empty_kept"] <= v["off"]["empty_kept"] + 2} for c in ("x1", "x2") if c in v}
# G3: projected index growth per pack = mean questions-column tokens per expanded chunk / mean indexed tokens per chunk (3 original columns)
def varints(b):
    out, i = [], 0
    while i < len(b):
        x = 0
        while True:  # SQLite varint: big-endian 7-bit groups
            y = b[i]; i += 1; x = (x << 7) | (y & 0x7F)
            if y < 0x80: break
        out.append(x)
    return out
g3 = {}
for p in PACKS + ["boar-crypto", "boar-wikivoyage-en"]:
    f = f"{ROOT}/shared-data/packs/d2qproto/full/{p}.sqlite"
    if not os.path.exists(f): continue
    db = sqlite3.connect(f"file:{f}?mode=ro", uri=True); tot3 = n = qt = qn = 0
    for (sz,) in db.execute("SELECT sz FROM fts_d2q_docsize"):
        c = varints(bytes(sz)); tot3 += sum(c[:3]); n += 1
        if len(c) > 3 and c[3]: qt += c[3]; qn += 1
    g3[p] = {"chunks": n, "expanded": qn, "mean_tokens_chunk": round(tot3 / n, 1), "mean_tokens_questions": round(qt / max(qn, 1), 1), "projected_growth": round((qt / max(qn, 1)) / (tot3 / n), 3)}
res["G3"] = {"index": g3, "p50_ratio": {c: round(res["ms_p50"][c] / res["ms_p50"]["off"], 2) for c in ("x1", "x2") if c in res["ms_p50"]},
             "pass_index": all(x["projected_growth"] <= 0.25 for x in g3.values()) if g3 else None}
os.makedirs(f"{A}/aggregates", exist_ok=True); json.dump(res, open(f"{A}/aggregates/compare.json", "w"), indent=1)
with open(f"{A}/runs/changed.jsonl", "w") as fh:
    for d in changed: fh.write(json.dumps(d) + "\n")
print(json.dumps({k: res[k] for k in res if k != "G3"}, indent=None)); print(json.dumps(res["G3"]))
