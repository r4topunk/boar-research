#!/usr/bin/env python3
"""COVERAGE-MAP pool search (2026-10-22; 0 LLM, 0 judge, 0 paid). For every MAIN 97 keyed item (92), which pack file on disk holds the key fact?
Rule = RAG-FUNNEL's pack-presence rule, unchanged (fact rule + pool search + idf anchor exec'd from ruler/tools/ragfunnel.py): per pack, FTS5 bm25
top 200 for OR(question tokens) and top 200 for OR(question tokens + grading terms); a chunk holds the fact when the fact rule on that chunk alone
gives share >= 0.5 and its idf topic anchor >= 0.5. Generalised only to more pack files (format-1 wiki-vital5: chunks_fts(title, body)).
Usage: python3 -I coverage_pool.py <out json> [shard nshards]"""
import json, sys, re, glob, sqlite3, functools, importlib.util, hashlib, math, unicodedata
from compression import zstd
OUT = sys.argv[1]; SH, NSH = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
CO = "<workspace>/rnd/research/coordinator/"; A = CO + "arms/"; BE = "<workspace>/boar-eval/bench/"; SD = "<workspace>/shared-data/"
SP = "<scratch>"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
spec = importlib.util.spec_from_file_location("pc", "<workspace>/boar-eval/scorers/vendor/lantern/precheck.py")
pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
FP = json.load(open(CO + "ruler/FACTPRESENT-2026-10-21.json"))["items"]
FUN = json.load(open(CO + "ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
MAIN = [l.strip() for l in open(A + "lp-screens/main-97.ids") if l.strip()]
V01 = set(l.strip() for l in open(A + "litepacks/data/v01-57.ids") if l.strip())
Q = {q["id"]: q for q in rd(BE + "v0.1/questions.public.jsonl")}
for f in glob.glob(BE + "selftest/*/questions.jsonl"):
    for q in rd(f): Q[q["id"]] = q
PF = {  # K3 kit files (= RAG-FUNNEL PF)
    "boar-crypto": SD + "crypto/boar-crypto.sqlite", "boar-wikivoyage-en": SD + "packs/boar-wikivoyage-en.sqlite",
    "boar-simplewiki-en": SD + "packs/v3proto/boar-simplewiki-en.sqlite", "boar-factbook": SD + "packs/v3proto/boar-factbook.sqlite",
    "boar-medlineplus-en": SD + "packs/v3proto/boar-medlineplus-en.sqlite", "boar-firstaid-en": SD + "packs/v3proto/boar-firstaid-en.sqlite",
    # on disk, not in K3
    "boar-visa-en": SD + "packs/wave4/boar-visa-en.sqlite", "boar-nist-crypto": SD + "packs/wave4/boar-nist-crypto.sqlite",
    "qa-bitcoin-se": SD + "packs/v3proto/qa-bitcoin-se.sqlite", "qa-ethereum-se": SD + "packs/v3proto/qa-ethereum-se.sqlite",
    "qa-health-se": SD + "packs/v3proto/qa-health-se.sqlite", "qa-outdoors-se": SD + "packs/v3proto/qa-outdoors-se.sqlite",
    "qa-travel-se": SD + "packs/v3proto/qa-travel-se.sqlite", "qa-cooking-se": SD + "packs/wave3/qa-cooking-se.sqlite",
    "qa-money-se": SD + "packs/wave3/qa-money-se.sqlite", "boar-preparedness-en": SD + "preparedness-v3/boar-preparedness-en.sqlite",
    "boar-vitalik-blog-en": SP + "boar-vitalik-blog-en.sqlite", "boar-wiki-en-top100k": SD + "packs/boar-wiki-en-top100k.sqlite",
    "wiki-vital5": SD + "packs/wiki-vital5.sqlite", "boar-wiki-sample": SD + "packs/boar-wiki-sample.sqlite"}
K3 = ["boar-crypto", "boar-wikivoyage-en", "boar-simplewiki-en", "boar-factbook", "boar-medlineplus-en", "boar-firstaid-en"]
DB = {k: sqlite3.connect(f"file:{v}?mode=ro", uri=True) for k, v in PF.items()}
FMT1 = {"wiki-vital5"}
@functools.lru_cache(maxsize=4096)
def block(pk, bid): return zstd.decompress(DB[pk].execute("select zdata from blocks where id=?", (bid,)).fetchone()[0])
@functools.lru_cache(maxsize=300000)
def chunk(pk, cid):
    if pk in FMT1:
        r = DB[pk].execute("select title, body from chunks where id=?", (cid,)).fetchone(); return (r[0], r[1]) if r else None
    r = DB[pk].execute("select article_id, start, end from chunks where id=?", (cid,)).fetchone()
    if not r: return None
    b, off, ln, t = DB[pk].execute("select block_id, off, len, title from articles where id=?", (r[0],)).fetchone()
    txt = block(pk, b)[off:off + ln].decode("utf-8", "replace")
    return t, txt[r[1]:r[2]].strip()
# fact rule + helpers, verbatim from ragfunnel.py (STOP .. anchor)
src = open(CO + "ruler/tools/ragfunnel.py").read().split("\n")
a = next(i for i, l in enumerate(src) if l.startswith("STOP = set("))
b = next(i for i, l in enumerate(src) if l.startswith("def pool_hits"))
exec("\n".join(src[a:b]))
def pool_hits(i, pk):  # = ragfunnel.pool_hits, returns every qualifying chunk (best first) + fts table name per format
    q = Q[i]; qt = list(dict.fromkeys(toks(q["question"]))); out = {}; tbl = "chunks_fts" if pk in FMT1 else "fts"
    for qq in (fts_or(qt), fts_or(qt + grading_words(q))):
        if not qq: continue
        try:
            for r, (rid,) in enumerate(DB[pk].execute(f"select rowid from {tbl} where {tbl} match ? order by rank limit 200", (qq,))):
                out.setdefault(rid, r)
        except sqlite3.OperationalError as e: print("fts err", i, pk, e, file=sys.stderr)
    hits = []
    for rid, rank in out.items():
        c = chunk(pk, rid)
        if not c: continue
        txt = c[0] + "\n" + c[1]; sh = share(q, [txt])
        if sh is None or sh < 0.5: continue
        anc = anchor(qt, txt)
        if anc < 0.5: continue
        th = int(bool({stem(w) for w in qt if idf(w) >= 2.0} & {stem(w) for w in toks(c[0])}))
        hits.append(((sh, th, anc, -rank), f"pack:{pk}:{rid}", c[0], round(sh, 3), anc, rank, c[1][:400]))
    hits.sort(key=lambda h: h[0], reverse=True)
    return [dict(chunk=h[1], title=h[2], share=h[3], anchor=h[4], bm25_rank=h[5], text=h[6]) for h in hits[:3]], len(hits)
KEYED = [i for i in MAIN if FP[i]["K0"]["share"] is not None][SH::NSH]
res = {}
for n, i in enumerate(KEYED):
    e = dict(set="v0.1" if i in V01 else "cm", tag=FUN[i]["tag"], question=Q[i]["question"], K1=FUN[i]["K1"]["vstage"], K3=FUN[i]["K3"]["vstage"], packs={})
    for pk in PF:
        hits, nq = pool_hits(i, pk)
        if hits: e["packs"][pk] = dict(n_qualifying=nq, top=hits)
    res[i] = e
    print(n, i, e["K1"], sorted(e["packs"]), file=sys.stderr, flush=True)
sha = {k: hashlib.sha256(open(__file__, "rb").read()).hexdigest() for k in ["script"]}
json.dump(dict(method=__doc__, packs=PF, script_sha256=sha["script"], items=res), open(OUT, "w"), indent=1)
