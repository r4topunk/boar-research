"""KIT-X2b 0-call gate (META 2026-10-16). SCRIPT-ONLY on blind (scoped exception 10-16 13:xx): prints counts only.
Projects gold-in-kept on v0.2 110 (claim kit, cut 7 replay traces from TK2FIX-V02) if the X1 neighbour append
(packHeadPass a2: chunks 1-2 of the first raw pack passage's article) also ran on the kit packs.
Gold is article-level (0/129 entries carry #section), so a neighbour of an already-kept article adds 0 gold by construction."""
import json, re, sqlite3, sys
ROOT = "<workspace>"
T = f"{ROOT}/blind/bench-v02/runs-packs/tk2fix-v02-kit.cut7.jsonl"
G = {k: v for k, v in json.load(open(f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json")).items() if isinstance(v, list) and v}
DB = {"local-boar-crypto": f"{ROOT}/shared-data/crypto/boar-crypto.sqlite", "local-boar-wikivoyage-en": f"{ROOT}/shared-data/packs/boar-wikivoyage-en.sqlite"}
_LIB = re.compile(r"^[^:]{2,40}:\s+"); norm = lambda s: " ".join(str(s or "").split()).lower(); bare = lambda t: _LIB.sub("", str(t or ""))
def tmatch(g, title):
    g = g.partition("#")[0]
    return norm(g) == norm(title) or (not _LIB.match(g) and norm(g) == norm(bare(title)))
L = {}
for l in open(T):
    o = json.loads(l); L.setdefault(o["id"], o)  # pass 1
con = {k: sqlite3.connect(f"file:{v}?mode=ro", uri=True) for k, v in DB.items()}
def art_title(pack, cid):
    r = con[pack].execute("SELECT a.title FROM chunks c JOIN articles a ON a.id=c.article_id WHERE c.id=?", (cid,)).fetchone()
    return r[0] if r else None
def in_store(g):
    t = g.partition("#")[0]
    for p, c in con.items():
        if c.execute("SELECT 1 FROM articles WHERE title = ? COLLATE NOCASE", (bare(t),)).fetchone() or c.execute("SELECT 1 FROM articles WHERE title = ? COLLATE NOCASE", (t,)).fetchone(): return True
        try:
            if c.execute("SELECT 1 FROM redirects WHERE title = ? COLLATE NOCASE", (bare(t),)).fetchone(): return True
        except sqlite3.Error: pass
    return False
gk = lambda i, xs: any(tmatch(g, x.get("title")) for g in G.get(i, []) for x in xs)
res = {"n": len(L), "gold_items": sum(1 for i in L if i in G)}
res["gold_kept_items"] = sum(1 for i in L if gk(i, L[i]["kept"]))
res["gold_raw6_items"] = sum(1 for i in L if gk(i, L[i]["raw"][:6]))
fired = gain = anchor_in_kept_article = 0
for i, o in L.items():
    a = next((x for x in o["raw"] if re.match(r"^pack:([^:]+):(\d+)$", x["chunkId"])), None)
    if not a: continue
    fired += 1
    pack, cid = re.match(r"^pack:([^:]+):(\d+)$", a["chunkId"]).groups()
    t = art_title(pack, int(cid)) if pack in con else a.get("title")
    if any(norm(bare(x.get("title"))) == norm(bare(t)) for x in o["kept"]): anchor_in_kept_article += 1
    if i in G and not gk(i, o["kept"]) and any(tmatch(g, t) for g in G[i]): gain += 1
res.update({"x1_kit_fires": fired, "x1_anchor_article_already_kept": anchor_in_kept_article, "x1_kit_gold_gain_items": gain,
            "upper_any_raw6_not_kept": res["gold_raw6_items"] - res["gold_kept_items"]})
res["gold_items_title_in_kit_store"] = sum(1 for i in L if i in G and any(in_store(g) for g in G[i]))
res["gold_items_in_store_not_raw6"] = sum(1 for i in L if i in G and not gk(i, L[i]["raw"][:6]) and any(in_store(g) for g in G[i]))
conv, mde = 0.18, 0.025
for k in ("x1_kit_gold_gain_items", "upper_any_raw6_not_kept", "gold_items_in_store_not_raw6"):
    res["ceiling_" + k] = round(res[k] * conv / res["n"], 4)
res["items_needed_for_mde"] = round(mde * res["n"] / conv, 1)
res["verdict"] = "PASS" if res["ceiling_x1_kit_gold_gain_items"] >= mde else "FAIL"
json.dump(res, open(sys.argv[1], "w"), indent=1); print(json.dumps(res))
