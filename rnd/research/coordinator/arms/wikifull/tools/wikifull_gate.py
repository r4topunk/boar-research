#!/usr/bin/env python3
"""T2 stage A0 WIKIFULL gate on ONE shard (shard 07). Extends anywhere_gate.py / section_gate.py (imports them).
All absent_knowledge-primary items of arm H (kept or not). Queries: q1 = 12-term OR; q2 = kept title + top 6 terms, or
top 4 terms as implicit AND when no kept title. + table chunks (not in FTS) of the top-5 hit articles. Pool, rescore by
sum idf (shard df via fts5vocab) over distinct item terms in chunk, keep top 40, jev has_fact; hits p>=0.7 get a second
jev boolean quote_supports. Writes ONLY ids/titles/probabilities/counts (never rationale/answer text).

usage: wikifull_gate.py --set vpara|v02 [--shard PATH --tag XX] [--dry-run] [--limit-items N] [--workers 8]
Stage A: --shard/--tag (default = A0 shard 07, tag 07, A0 outputs/cache unchanged). Other tags write
aggregates/stageA-<set>-<XX>.json and cache under wikifull-cache/s<XX>/ (shard-keyed, no cross-shard reuse).
"""
import sys, os, re, json, argparse, collections, sqlite3, math, time, threading
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/wikisection/tools")
import section_gate as sg, anywhere_gate as ag
from compression import zstd
from concurrent.futures import ThreadPoolExecutor

SHARD = f"{sg.ROOT}/shared-data/gate-ref/boar-wiki-en-07.sqlite"
TOP100K = sg.PACK
OUT = f"{sg.ROOT}/rnd/research/coordinator/arms/wikifull/aggregates"
TOPK = 20; CAPC = 40; NT = 12; TH = 0.7
QV = {"quote_supports": {"type": "boolean",
  "instructions": "Does `text` contain, in its own words, the specific value, name, date or step that `rationale_1` or `rationale_2` say is missing or wrong in the system answer, not merely the topic?",
  "criteria": {"true": "`text` states the concrete value, name, date or step itself",
               "false": "`text` only discusses the topic, or lacks the specific value, name, date or step"}}}

class Shard:
    def __init__(s, path=SHARD):
        s.db = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False); s.lk = threading.Lock(); s.blk = {}
        s.db.execute("create virtual table temp.v using fts5vocab(main,'fts','row')")
        s.N = s.db.execute("select count(*) from fts_docsize").fetchone()[0]
        s.titles = {}
        for i, t in s.db.execute("select id,title from articles"): s.titles.setdefault(t.lower(), i)
        s.idfc = {}
    def idf(s, w):
        if w in s.idfc: return s.idfc[w]
        cands = [w] + [w[:-len(x)] for x in ("ing", "ed", "es", "s", "ly", "al") if w.endswith(x) and len(w) - len(x) >= 3]
        d = None
        with s.lk:
            for c in cands:
                r = s.db.execute("select doc from v where term=?", (c,)).fetchone()
                if r: d = r[0]; break
        v = math.log((s.N + 1) / ((d or 0) + 0.5)); s.idfc[w] = v; return v
    def resolve(s, t):
        i = s.titles.get(t.lower())
        if i: return i
        with s.lk:
            r = s.db.execute("select article_id from redirects where title=? collate nocase", (t,)).fetchone()
        return r[0] if r else None
    def text(s, aid):
        with s.lk:
            t, b, off, ln = s.db.execute("select title,block_id,off,len from articles where id=?", (aid,)).fetchone()
            if b not in s.blk:
                if len(s.blk) > 8: s.blk.clear()
                s.blk[b] = zstd.decompress(s.db.execute("select zdata from blocks where id=?", (b,)).fetchone()[0])
            return t, s.blk[b][off:off+ln].decode("utf-8")
    def chunk(s, cid):
        with s.lk: aid, st, en = s.db.execute("select article_id,start,end from chunks where id=?", (cid,)).fetchone()
        t, text = s.text(aid); return aid, t, sg.u16(text, st, en).strip()
    def is_table(s, cid):
        with s.lk: return s.db.execute("select 1 from fts_docsize where id=?", (cid,)).fetchone() is None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--set", required=True); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit-items", type=int); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--shard", default=SHARD); ap.add_argument("--tag", default="07"); a = ap.parse_args()
    A0 = (a.tag == "07" and os.path.abspath(a.shard) == SHARD)
    if not os.path.exists(a.shard): sys.exit("missing shard " + a.shard)
    S = sg.SETS[a.set]; key = os.environ.get("VERCEL_AI_GATEWAY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not key and not a.dry_run: sys.exit("no gateway key")
    t0 = time.time()
    agg = json.load(open(f"{sg.ROOT}/rnd/research/coordinator/arms/lossmap/aggregates/{S['agg']}"))["items"]
    groups = {}
    for i in agg:
        if i["primary"] != "absent_knowledge": continue
        groups[i["id"]] = "on_topic" if i["labels"]["source_on_topic"] else ("off_topic_kept" if i["n_kept"] > 0 else "no_kept")
    rat = collections.defaultdict(list)
    for r in sg.read_jsonl(f"{S['dir']}/{S['j']}"):
        if r.get("ok") and r["queryId"] in groups: rat[r["queryId"]].append(r)
    tr = {t["itemId"]: t for t in sg.read_jsonl(f"{S['dir']}/{S['t']}")}
    cd = f"{S['dir']}/wikifull-cache"; oldcd = f"{S['dir']}/wikisection-cache"
    if not A0: cd = f"{cd}/s{a.tag}"; oldcd = cd
    os.makedirs(cd, exist_ok=True)
    sh = Shard(a.shard)
    t100 = sqlite3.connect(f"file:{TOP100K}?mode=ro", uri=True); top_titles = {t.lower() for (t,) in t100.execute("select title from articles")}; t100.close()
    ids = sorted(groups)[: a.limit_items] if a.limit_items else sorted(groups)
    plan = []
    for qid in ids:
        rows = sorted(rat[qid], key=lambda r: r["order"])
        r1 = rows[0]["verdict"]["rationale"][:2500]; r2 = rows[-1]["verdict"]["rationale"][:2500] if len(rows) > 1 else ""
        kt = []
        for k in (tr[qid].get("retrieval") or {}).get("kept") or []:
            t = k.get("title") or ""
            if t.startswith(("Wikivoyage: ", "Wikibooks: ", "Appropedia: ")): t = t.split(": ", 1)[1]
            if t not in kt: kt.append(t)
        plan.append((qid, groups[qid], r1, r2, kt))
    fl = sh.lk
    def fts(q):
        with fl:
            try: return [r[0] for r in sh.db.execute("select rowid from fts where fts match ? order by bm25(fts,2.0,1.0,1.0) limit ?", (q, TOPK))]
            except sqlite3.OperationalError: return []
    def build(p):
        qid, g, r1, r2, kt = p; ts = ag.terms([r1, r2], NT)
        ts_idf = sorted(ts, key=lambda w: -sh.idf(w))
        q1 = ag.mq(ts)
        q2 = ag.mq(re.findall(r"[A-Za-z0-9]+", kt[0].lower()) + ts[:6]) if kt else " ".join('"%s"' % w.replace('"', "") for w in ts_idf[:4])
        pool = []
        for q in (q1, q2):
            for c in fts(q):
                if c not in pool: pool.append(c)
        # table chunks of top-5 hit articles (by first appearance)
        arts = []
        with fl:
            for c in pool:
                aid = sh.db.execute("select article_id from chunks where id=?", (c,)).fetchone()[0]
                if aid not in arts: arts.append(aid)
                if len(arts) >= 5: break
        tabs = []
        for aid in arts:
            with fl: cs = [r[0] for r in sh.db.execute("select id from chunks where article_id=?", (aid,))]
            tabs += [c for c in cs if sh.is_table(c)]
        pool += [c for c in tabs if c not in pool]
        tl = [w.lower() for w in ts]; 
        def score(c):
            _, _, txt = sh.chunk(c); low = txt.lower()
            return sum(sh.idf(w) for w in set(tl) if w in low)
        sc = sorted(((score(c), c) for c in pool), reverse=True)[:CAPC]
        return [c for _, c in sc], len(tabs)
    if a.dry_run:
        n = nt = 0
        for p in plan: cs, tn = build(p); n += len(cs); nt += tn
        print(f"{a.set}: items={len(plan)} approx_requests={n} table_candidates={nt} t={time.time()-t0:.0f}s"); return
    def call(body, cdir):
        raw = json.dumps(body, sort_keys=True, ensure_ascii=False)
        import hashlib
        h = hashlib.sha256(raw.encode()).hexdigest() + ".json"
        for d in (cdir, oldcd):
            pth = os.path.join(d, h)
            if os.path.exists(pth): return json.load(open(pth)), True
        return sg.call(body, key, cdir)
    def ask(q, r1, r2, text, name):
        res, hit = call({"model": sg.MODEL, "state": {"rationale_1": r1, "rationale_2": r2, "text": text}, "questions": q}, cd)
        c = 0.0 if hit else float(((res.get("providerMetadata") or {}).get("gateway") or {}).get("marketCost") or 0)
        return res["answers"][name]["probability"], c
    def work(p):
        qid, g, r1, r2, kt = p; cost = 0.0; reqs = 0; recs = []
        cs, ntab = build(p)
        for cid in cs:
            aid, t, txt = sh.chunk(cid)
            if not txt: continue
            pp, c = ask(sg.Q, r1, r2, txt, "has_fact"); cost += c; reqs += 1
            rec = dict(chunk=cid, article=aid, title=t, p=round(pp, 3), table=sh.is_table(cid), outside_top100k=t.lower() not in top_titles)
            if pp >= TH:
                qp, c = ask(QV, r1, r2, txt, "quote_supports"); cost += c; reqs += 1; rec["quote_p"] = round(qp, 3); rec["verified"] = qp >= TH
            recs.append(rec)
        best = max(recs, key=lambda r: r["p"], default=None)
        it = dict(id=qid, group=g, kept_titles=kt, n_chunks=len(recs), n_table_candidates=ntab, max_p=best["p"] if best else None, best_title=best["title"] if best else None,
                  hits=[r for r in recs if r["p"] >= 0.6])
        return it, cost, reqs
    items = []; tc = 0.0; tq = 0
    with ThreadPoolExecutor(a.workers) as ex:
        for it, c, r in ex.map(work, plan): items.append(it); tc += c; tq += r
    def cnt(L, th): return sum(1 for i in L if i["max_p"] is not None and i["max_p"] >= th)
    summ = {}
    for g in ("ALL", "on_topic", "off_topic_kept", "no_kept"):
        L = [i for i in items if g == "ALL" or i["group"] == g]
        summ[g] = dict(n=len(L), ge06=cnt(L, .6), ge07=cnt(L, .7), ge08=cnt(L, .8),
            verified_ge07=sum(1 for i in L if any(h.get("verified") for h in i["hits"] if h["p"] >= TH)),
            table_hit_ge07=sum(1 for i in L if any(h["table"] for h in i["hits"] if h["p"] >= TH)),
            outside_top100k_ge07=sum(1 for i in L if any(h["outside_top100k"] for h in i["hits"] if h["p"] >= TH)),
            verified_outside_top100k=sum(1 for i in L if any(h.get("verified") and h["outside_top100k"] for h in i["hits"] if h["p"] >= TH)),
            verified_table=sum(1 for i in L if any(h.get("verified") and h["table"] for h in i["hits"] if h["p"] >= TH)))
    stage = "A0 shard07 (one of 15; NOT a REOPEN verdict)" if A0 else f"A shard{a.tag} (one of 15; pooled by stageA_pool.py)"
    out = dict(set=a.set, stage=stage, threshold=TH, topk_per_query=TOPK, cap_chunks=CAPC, model=sg.MODEL,
               requests_uncached=tq, gateway_cost_usd=round(tc, 5), runtime_s=round(time.time()-t0), summary=summ, items=items)
    if not A0: out["shard"] = a.tag; out["shard_file"] = os.path.basename(a.shard)
    dst = f"{OUT}/A0-shard07-{a.set}.json" if A0 else f"{OUT}/stageA-{a.set}-{a.tag}.json"
    json.dump(out, open(dst + ".tmp", "w"), indent=1); os.replace(dst + ".tmp", dst)
    print(a.set, json.dumps(summ), f"requests(uncached)={tq} cost=${tc:.5f} t={time.time()-t0:.0f}s")

if __name__ == "__main__": main()
