"""Build items/qform.jsonl (432), items/qform.questions.jsonl, items/facts.json from tools/forms_src.py.
Gold is resolved against the source pack (self-test or authored quote) and the merged A-union file (chunk id the replay returns).
python3 -I tools/build_items.py"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from pack_reader import Pack, SOURCES
import forms_src

B = "<workspace>/"
PATHS = {"boar-crypto": B + "shared-data/crypto/boar-crypto.sqlite",
         "boar-wikivoyage-en": B + "shared-data/packs/boar-wikivoyage-en.sqlite",
         "boar-visa-en": B + "shared-data/packs/wave4/boar-visa-en.sqlite"}
MERGED = Pack(B + "shared-data/packs/persona-a-union-merged/boar-aunion-merged.sqlite")
ST = {}
for p in ["boar-factbook", "boar-firstaid-en", "boar-medlineplus-en"]:
    for l in open(B + f"rnd/research/packs/selftest/{p}.jsonl"):
        r = json.loads(l); ST[r["id"]] = r
byk = {}
for aid, src, title, *_ in MERGED.articles():
    byk.setdefault((src, title), []).append(aid)
srcpacks = {k: Pack(v) for k, v in PATHS.items()}

def merged_gold(src_code, title, ci, quote):
    for aid in byk.get((src_code, title), []):
        ch = MERGED.chunks(aid)
        if ci < len(ch):
            cid, tx = MERGED.chunk_text(aid, ci)
            if quote in tx:
                return aid, cid
    raise SystemExit(f"merged gold not found: {title} {ci} {quote[:50]}")

def find_chunk(pack, aid, quote):
    for i in range(len(pack.chunks(aid))):
        if quote in pack.chunk_text(aid, i)[1]:
            return i
    raise SystemExit(f"quote not in article {aid}: {quote[:60]}")

counters = {}
facts_out, items = [], []
for f in forms_src.FACTS:
    pack = f["pack"]
    nn = counters[pack] = counters.get(pack, 0) + 1
    fid = f"qf-{pack}-{nn:02d}"
    if "st" in f:
        r = ST[f["st"]]; fa = r["in_pack_facts"][f["prim"]]
        quote, ci, src_aid, title = fa["quote"], fa["chunk_index"], fa.get("article", r["source"]["article_id"]), r["source"]["title"]
        src_code = SOURCES.index(r["source"]["pack_source"]) if r["source"]["pack_source"] in SOURCES else None
        # self-test pack_source is 'factbook'/'medlineplus'/'enwiki'... map to merged source code by trying all codes
        cands = [c for c in range(len(SOURCES)) if (c, title) in byk]
        mg = None
        for c in cands:
            try:
                mg = merged_gold(c, title, ci, quote); src_code = c; break
            except SystemExit:
                pass
        if mg is None: raise SystemExit("no merged gold for " + f["st"])
        q0 = r["question"]; st_ans, st_rub = r["answer"], r["rubric"]
        alt = [x["quote"] for i, x in enumerate(r["in_pack_facts"]) if i != f["prim"]]
        alt_gold = []
        for i, x in enumerate(r["in_pack_facts"]):
            if i == f["prim"]: continue
            alt_gold.append({"quote": x["quote"], "chunk_index": x["chunk_index"],
                             "merged_chunk_id": merged_gold(src_code, title, x["chunk_index"], x["quote"])[1]})
    else:
        p = srcpacks[pack]; aid = f["art"]
        title = p.title(aid)
        src_code = p.db.execute("select source from articles where id=?", (aid,)).fetchone()[0]
        quote = f["quote"]; assert len(quote) <= 200, (fid, len(quote))
        ci = find_chunk(p, aid, quote); src_aid = aid
        mg = merged_gold(src_code, title, ci, quote)
        q0 = f["q0"]; st_ans = st_rub = None; alt_gold = []
    avoid = sorted({t for t in f.get("avoid", [])})
    fact = {"fact_id": fid, "pack": pack, "selftest_id": f.get("st"), "title": title, "source_code": src_code,
            "gold": {"article_id": src_aid, "chunk_index": ci, "quote": quote, "title": title,
                     "merged_article_id": mg[0], "merged_chunk_id": mg[1], "alt": alt_gold},
            "avoid": avoid, "answer": f["ans"], "rubric": f["rubric"]}
    facts_out.append(fact)
    forms = {0: q0}
    for k in range(1, 9): forms[k] = f[f"F{k}"]
    for k in range(9):
        ans = f["ans"]
        if k == 5: ans = "Yes. " + ans
        if k == 6: ans = "No, that premise is wrong. " + ans
        it = {"id": f"{fid.replace('qf-', 'qf-', 1)}-F{k}", "pack": pack, "fact_id": fid, "form": k, "question": forms[k], "lang": "en",
              "gold": {"article_id": src_aid, "chunk_index": ci, "quote": quote, "title": title},
              "answer": ans, "rubric": f["rubric"]}
        if k == 0 and st_ans: it["selftest"] = {"id": f["st"], "answer": st_ans, "rubric": st_rub}
        items.append(it)

with open(os.path.join(ROOT, "items/qform.jsonl"), "w") as o:
    for it in items: o.write(json.dumps(it, ensure_ascii=False) + "\n")
with open(os.path.join(ROOT, "items/qform.questions.jsonl"), "w") as o:
    for it in items:
        o.write(json.dumps({"id": it["id"], "question": it["question"], "lang": "en", "pack": it["pack"],
                            "fact_id": it["fact_id"], "form": f"F{it['form']}"}, ensure_ascii=False) + "\n")
json.dump(facts_out, open(os.path.join(ROOT, "items/facts.json"), "w"), indent=1, ensure_ascii=False)
print(len(items), "items,", len(facts_out), "facts")
