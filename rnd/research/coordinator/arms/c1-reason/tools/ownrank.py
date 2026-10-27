#!/usr/bin/env python3
"""Own-pack lexical rank of the fact article (0 LLM): FTS5 bm25 over OR(question content tokens), read-only.
usage: ownrank.py <questions.jsonl> <vitalik pack path> -> stdout JSON {id: {pack, rank_of_fact_article, top3_titles}}"""
import json, sqlite3, sys, re
B = "<workspace>"
Q = {json.loads(l)["id"]: json.loads(l)["question"] for l in open(sys.argv[1])}
VIT = sys.argv[2]
STOP = set("a an the of to in on for and or is are was were be been what why how when which who whom does do did can could would should will i my me you your it its this that these those with without from at by as into than then so if not no any all some more most less very just about there their they them we our us he she his her".split())
def toks(q): return [t for t in re.findall(r"[a-z0-9]+", q.lower()) if t not in STOP and len(t) > 1]
F = {}
for p in ["qa-cooking-se", "qa-money-se"]:
    for l in open(f"{B}/boar-eval/bench/selftest/{p}/questions.jsonl"):
        d = json.loads(l); F[d["id"]] = (f"{B}/shared-data/packs/wave3/{p}.sqlite", [d["selftest"]["source"]["title"]])
F["vit-cry-005"] = (VIT, ["Why I support privacy"]); F["vit-cry-007"] = (VIT, ["d/acc: one year later", "My techno-optimism"])
F["vit-cry-005/crypto"] = (f"{B}/shared-data/packs/persona-a-union/boar-crypto.sqlite", ["ERC-8262: Zero-Knowledge Compliance Oracle"])
out = {}
for i, (pf, ts) in F.items():
    qid = i.split("/")[0]
    if qid not in Q: continue
    db = sqlite3.connect(f"file:{pf}?mode=ro", uri=True)
    q = " OR ".join('"%s"' % t for t in toks(Q[qid]))
    seen, rank, top = [], None, []
    for (rid,) in db.execute("select rowid from fts where fts match ? order by rank limit 400", (q,)):
        aid = db.execute("select article_id from chunks where id=?", (rid,)).fetchone()[0]
        if aid in seen: continue
        seen.append(aid); t = db.execute("select title from articles where id=?", (aid,)).fetchone()[0]
        if len(top) < 3: top.append(t)
        if rank is None and t in ts: rank = len(seen) - 1
    out[i] = {"pack": pf.rsplit("/", 1)[1], "article_rank": rank, "articles_scanned": len(seen), "top3": top}
print(json.dumps(out, indent=1))
