#!/usr/bin/env python3
"""C1-REASON desktop install replay reader (0 LLM): LITEPACKS K3 + {qa-cooking-se, qa-money-se, boar-vitalik-blog-en} (K3X) on the RAG-FUNNEL
tree, vs the RAG-FUNNEL K3 traces. Fact chunk = chunk of the source article holding the self-test quote (vitalik: the named phrase).
usage: c1_desktop.py <K3X out dir> <RAG-FUNNEL out dir> <vitalik pack> <out json>"""
import json, os, sys, sqlite3, re
from compression import zstd
X, F, VIT, OUT = sys.argv[1:5]
B = "<workspace>"
PF = {"qa-cooking-se": f"{B}/shared-data/packs/wave3/qa-cooking-se.sqlite", "qa-money-se": f"{B}/shared-data/packs/wave3/qa-money-se.sqlite",
      "boar-vitalik-blog-en": VIT, "boar-crypto": f"{B}/shared-data/crypto/../packs/persona-a-union/boar-crypto.sqlite"}
nrm = lambda s: re.sub(r"\s+", " ", s.lower()).strip()
def chunks_with(pack, title=None, aid=None, needles=()):
    db = sqlite3.connect(f"file:{PF[pack]}?mode=ro", uri=True)
    if aid is None: aid = db.execute("select id from articles where title=?", (title,)).fetchone()[0]
    b, off, ln = db.execute("select block_id, off, len from articles where id=?", (aid,)).fetchone()
    txt = zstd.decompress(db.execute("select zdata from blocks where id=?", (b,)).fetchone()[0])[off:off + ln].decode("utf-8", "replace")
    out = []
    for cid, s, e in db.execute("select id, start, end from chunks where article_id=? order by start", (aid,)):
        c = nrm(txt[s:e])
        if any(nrm(n)[:60] in c for n in needles): out.append(f"{pack}:{cid}")
    return out
FC = {}
for p in ["qa-cooking-se", "qa-money-se"]:
    for l in open(f"{B}/boar-eval/bench/selftest/{p}/questions.jsonl"):
        d = json.loads(l); st = d["selftest"]
        FC[d["id"]] = chunks_with(p, aid=st["source"]["article_id"], needles=[f["quote"] for f in st["in_pack_facts"]])
FC["vit-cry-005"] = chunks_with("boar-vitalik-blog-en", "Why I support privacy", needles=["privacy pools"]) + ["boar-crypto:27321"]
FC["vit-cry-007"] = chunks_with("boar-vitalik-blog-en", "d/acc: one year later", needles=["d/acc"]) + chunks_with("boar-vitalik-blog-en", "My techno-optimism", needles=["d/acc"])
IDS = ["st-qa-cooking-se-002", "st-qa-cooking-se-003", "st-qa-cooking-se-008", "st-qa-cooking-se-012", "st-qa-cooking-se-013",
       "st-qa-cooking-se-015", "st-qa-money-se-004", "st-qa-money-se-007", "st-qa-money-se-009", "st-qa-money-se-010",
       "st-qa-money-se-011", "st-qa-money-se-020", "vit-cry-005", "vit-cry-007"]
def load(d, names):
    r = {}
    for n in names:
        for l in open(os.path.join(d, n + ".traces.jsonl")):
            t = json.loads(l); codes = (t.get("route") or {}).get("reasonCodes", [])
            g = lambda pre: next((c[len(pre):].split(",") for c in codes if c.startswith(pre)), [])
            kept = next((c.split(":", 3)[3].split(",") for c in codes if c.startswith("retfloor:kept:")), [])
            norm = lambda L: [re.sub(r"^pack:(local-)?", "", x) for x in L if x]
            r[t["itemId"]] = {"raw": norm(g("fun:raw:")), "dense": norm(g("fun:dense:")), "kept": norm(kept),
                              "retrieve": any(c == "retrieve:yes" for c in codes),
                              "route": [c for c in codes if c.startswith(("task:", "answer:", "grounding:health", "places:", "near:"))][:4]}
    return r
K3X = load(X, ["K3X-V01", "K3X-CM"]); K3 = load(F, ["K3-V01", "K3-CM"])
res = {"fact_chunks": FC, "items": {}}
for i in IDS:
    t = K3X[i]; fc = set(FC[i])
    pos = lambda L: next((k for k, x in enumerate(L) if x in fc), None)
    res["items"][i] = {"retrieve": t["retrieve"], "route": t["route"], "raw_pos": pos(t["raw"]), "dense_rank": pos(t["dense"]),
                       "kept": bool(fc & set(t["kept"])), "n_kept": len(t["kept"]), "n_fact_chunks": len(fc)}
others = [i for i in K3 if i not in IDS]
res["crowding_changed_other"] = [i for i in others if K3X[i]["kept"] != K3[i]["kept"]]
json.dump(res, open(OUT, "w"), indent=1)
for i, v in res["items"].items(): print(i, v)
print("other items kept changed", len(res["crowding_changed_other"]), "of", len(others), [i for i in res["crowding_changed_other"] if not i.startswith("st-")])
