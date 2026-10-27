"""TK2-REPLAY compare (0 LLM): OFF (cut 7) vs ON (cut 7 + tk2.vs-cut7.patch) per item. Fact chunk / fact article as
arms/packroute/tools/step0.py (in_pack_facts chunk_index over the article's chunks by start; source.article_id; item pack's
chunks only, via the chunkId prefix). Writes aggregates/compare.json + runs/diff-items.jsonl. Public sets only."""
import json, re, sqlite3, os
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms/packs/tk2-replay"; ST = f"{ROOT}/rnd/research/packs/selftest"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
K = 6; load = lambda f: [json.loads(l) for l in open(f) if l.strip()]
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
def cmp(off, on):
    d = {"kept_same": ids(off) == ids(on), "raw_same": ids(off, "raw") == ids(on, "raw"),
         "raw6_same": ids(off, "raw")[:K] == ids(on, "raw")[:K], "prompt_same": off.get("promptSha") == on.get("promptSha"),
         "task_same": off["task"] == on["task"] and off["query"] == on["query"] and off["k"] == on["k"]}
    if not d["kept_same"]:
        a, b = ids(off), ids(on); t = {x["chunkId"]: x["title"] for x in off["kept"] + on["kept"]}
        d["dropped"] = [[c, t[c]] for c in a if c not in b]; d["added"] = [[c, t[c]] for c in b if c not in a]
        d["reordered"] = not d["dropped"] and not d["added"]
    return d
res = {"sets": {}}; diffs = []
def repeat_ok(P): return sum(json.dumps([ids(P[0][i]), ids(P[0][i], "raw"), P[0][i].get("promptSha")]) == json.dumps([ids(P[1][i]), ids(P[1][i], "raw"), P[1][i].get("promptSha")]) for i in P[0])
# ---- 180 self-tests
tot = None; per = {}
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
    P = {c: passes(load(f"{A}/runs/st-{p}.{c}.jsonl")) for c in ("off", "on")}
    o = {"n": len(facts), "repeat_identical": {c: repeat_ok(P[c]) for c in P}}
    for c in ("off", "on"):
        L = P[c][0]; s = {"chunk_raw6": 0, "chunk_kept": 0, "art_raw6": 0, "art_kept": 0, "empty_kept": 0, "kept_slots": 0}
        for i, (fa, fcs) in facts.items():
            l = L[i]; raw = [cid(x, p) for x in l["raw"][:K]]; kept = [cid(x, p) for x in l["kept"]]
            s["chunk_raw6"] += any(x in fcs for x in raw if x); s["art_raw6"] += any(ch_art.get(x) == fa for x in raw if x)
            s["chunk_kept"] += any(x in fcs for x in kept if x); s["art_kept"] += any(ch_art.get(x) == fa for x in kept if x)
            s["empty_kept"] += (l["raw"] != [] and not l["kept"]); s["kept_slots"] += len(l["kept"])
        o[c] = s
    cs = {i: cmp(P["off"][0][i], P["on"][0][i]) for i in facts}
    for k in ("kept_same", "raw_same", "raw6_same", "prompt_same", "task_same"): o[k] = sum(v[k] for v in cs.values())
    for i, v in cs.items():
        if not v["kept_same"] or not v["raw_same"]: diffs.append({"set": "st", "pack": p, "id": i, **v})
    per[p] = o
res["sets"]["st180"] = {"per_pack": per, "total": {k: (sum(per[p][k] for p in PACKS) if not isinstance(per[PACKS[0]][k], dict) else
    {kk: sum(per[p][k][kk] for p in PACKS) for kk in per[PACKS[0]][k]}) for k in per[PACKS[0]]}}
# ---- v0.1 kit only
G = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")).items() if isinstance(v, list) and v}
P = {c: passes(load(f"{A}/runs/v01-kit.{c}.jsonl")) for c in ("off", "on")}
o = {"n": len(P["off"][0]), "repeat_identical": {c: repeat_ok(P[c]) for c in P}}
for c in ("off", "on"):
    L = P[c][0]
    o[c] = {"gold_raw6": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["raw"][:6]) for i in G if i in L),
            "gold_kept": sum(any(gmatch(g, x) for g in G[i] for x in L[i]["kept"]) for i in G if i in L),
            "empty_kept_retrieving": sum(1 for l in L.values() if l["raw"] and not l["kept"]), "kept_slots": sum(len(l["kept"]) for l in L.values())}
cs = {i: cmp(P["off"][0][i], P["on"][0][i]) for i in P["off"][0]}
for k in ("kept_same", "raw_same", "raw6_same", "prompt_same", "task_same"): o[k] = sum(v[k] for v in cs.values())
for i, v in cs.items():
    if not v["kept_same"] or not v["raw_same"] or not v["prompt_same"]: diffs.append({"set": "v01", "id": i, **v})
res["sets"]["v01"] = o
os.makedirs(f"{A}/aggregates", exist_ok=True)
json.dump(res, open(f"{A}/aggregates/compare.json", "w"), indent=1)
with open(f"{A}/runs/diff-items.jsonl", "w") as f:
    for d in diffs: f.write(json.dumps(d) + "\n")
print(json.dumps(res["sets"]["st180"]["total"])); print(json.dumps(res["sets"]["v01"]))
for p in PACKS: print(p, {k: per[p][k] for k in ("kept_same", "raw_same", "prompt_same")}, per[p]["off"], per[p]["on"])
print("diff items", len(diffs))
