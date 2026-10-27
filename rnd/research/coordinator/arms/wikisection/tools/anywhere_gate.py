#!/usr/bin/env python3
"""H5b ANYWHERE 0-call gate (jev only). Are the deep tier's missing facts ANYWHERE in the enwiki top-100k pack?
Same items/rationales/ask() as section_gate.py. Query = top content terms of the two Opus rationales (+ a second
query: kept title + top 6 terms), FTS5 BM25 over the pack (weights 2,1,1 as the engine), top 20 chunks per query,
dedupe, cap 40 per item, jev boolean has_fact per chunk. Writes ONLY ids/titles/probabilities/counts (no rationale text).

usage: anywhere_gate.py --set vpara|v02 [--dry-run] [--limit-items N] [--workers 8] [--smoke]
"""
import sys, os, re, json, argparse, collections, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import section_gate as sg
from concurrent.futures import ThreadPoolExecutor

TOPK = 20; CAPC = 40; TH = sg.TH; NTERMS = 12
STOP = set("""a an the and or but if then of to in on at by for with from as is are was were be been being it its this that these those
which who whom whose what when where why how not no nor so than too very can could should would may might must will shall do does did done
has have had having he she they them their his her we our you your i me my also both each any all some such other more most less least only own same
into onto over under between about above below up down out off again further once here there while because until against during before after
however although though yet still just even much many few several one two three four five six seven eight nine ten
answer answers reference response responses system a b mentions mention mentioned includes include included omits omit omitted lacks lack lacked
missing misses miss states state stated provides provide provided gives give given does doesnt doesn t s say says said
judge criterion criteria rubric correct incorrect correctness completeness complete specific specifics details detail general generic
version output outputs question text item key points point covers cover covered fails fail failed fact facts information""".split())
TOK = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-\.]*[A-Za-z0-9]|[A-Za-z0-9]")

def terms(rats, n):
    cnt = collections.Counter(); first = {}
    for ri, r in enumerate(rats):
        for pos, m in enumerate(TOK.finditer(r)):
            w = m.group(0).strip(".'-")
            if not w or w.lower() in STOP: continue
            cap = w[0].isupper() and pos > 0 and not r[:m.start()].rstrip().endswith((".", ":", "?", "!"))
            num = any(ch.isdigit() for ch in w)
            if len(w) < 3 and not num: continue
            k = w.lower(); cnt[k] += 1 + (1 if cap or num else 0) + (0.5 if len(w) > 7 else 0); first.setdefault(k, (ri, pos))
    return [w for w, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], first[kv[0]]))[:n]]

def mq(ws): return " OR ".join('"' + w.replace('"', "") + '"' for w in ws if w)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--set", required=True); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit-items", type=int); ap.add_argument("--workers", type=int, default=8); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    S = sg.SETS[a.set]; key = os.environ.get("VERCEL_AI_GATEWAY") or os.environ.get("AI_GATEWAY_API_KEY")
    if not key and not a.dry_run: sys.exit("no gateway key")
    agg = json.load(open(f"{sg.ROOT}/rnd/research/coordinator/arms/lossmap/aggregates/{S['agg']}"))["items"]
    groups = {}
    for i in agg:
        if i["primary"] != "absent_knowledge": continue
        if i["labels"]["source_on_topic"]: groups[i["id"]] = "on_topic"
        elif i["n_kept"] > 0: groups[i["id"]] = "off_topic_kept"
    rat = collections.defaultdict(list)
    for r in sg.read_jsonl(f"{S['dir']}/{S['j']}"):
        if r.get("ok") and r["queryId"] in groups: rat[r["queryId"]].append(r)
    tr = {t["itemId"]: t for t in sg.read_jsonl(f"{S['dir']}/{S['t']}")}
    cd = f"{S['dir']}/wikisection-cache"; os.makedirs(cd, exist_ok=True)
    pack = sg.Pack(); fdb = sqlite3.connect(f"file:{sg.PACK}?mode=ro", uri=True, check_same_thread=False); fl = pack.lk
    ids = sorted(groups)[: a.limit_items] if a.limit_items else sorted(groups)
    plan = []
    for qid in ids:
        rows = sorted(rat[qid], key=lambda r: r["order"])
        r1 = rows[0]["verdict"]["rationale"][:2500]; r2 = rows[-1]["verdict"]["rationale"][:2500] if len(rows) > 1 else ""
        kt = []; kaid = set()
        for k in (tr[qid].get("retrieval") or {}).get("kept") or []:
            t = k.get("title") or ""
            if t.startswith(("Wikivoyage: ", "Wikibooks: ", "Appropedia: ")): t = t.split(": ", 1)[1]
            if t not in kt:
                kt.append(t); aid, _ = pack.resolve(t)
                if aid: kaid.add(aid)
        plan.append((qid, groups[qid], r1, r2, kt, kaid))
    def cand(q):
        with fl: return [r[0] for r in fdb.execute("select rowid from fts where fts match ? order by bm25(fts,2.0,1.0,1.0) limit ?", (q, TOPK))]
    def chunk(cid):
        with fl:
            aid, s, e = fdb.execute("select article_id,start,end from chunks where id=?", (cid,)).fetchone()
            t, text, _ = pack._article(aid)
        return aid, t, sg.u16(text, s, e).strip()
    def build(p):
        qid, g, r1, r2, kt, kaid = p; ts = terms([r1, r2], NTERMS)
        qs = [mq(ts)]
        if kt: qs.append(mq(re.findall(r"[A-Za-z0-9]+", kt[0].lower()) + ts[:6]))
        seen = []; 
        for q in qs:
            for c in cand(q):
                if c not in seen: seen.append(c)
        return seen[:CAPC]
    if a.dry_run:
        n = 0
        for p in plan: n += len(build(p))
        print(f"{a.set}: items={len(plan)} approx_requests={n}"); return
    def ask(r1, r2, text):
        res, hit = sg.call({"model": sg.MODEL, "state": {"rationale_1": r1, "rationale_2": r2, "text": text}, "questions": sg.Q}, key, cd)
        c = 0.0 if hit else float(((res.get("providerMetadata") or {}).get("gateway") or {}).get("marketCost") or 0)
        return res["answers"]["has_fact"]["probability"], c
    def work(p):
        qid, g, r1, r2, kt, kaid = p; cost = 0.0; reqs = 0; recs = []
        for cid in build(p):
            aid, t, txt = chunk(cid)
            if not txt: continue
            pp, c = ask(r1, r2, txt); cost += c; reqs += 1
            recs.append((cid, aid, t, round(pp, 3), aid in kaid))
        best = max(recs, key=lambda r: r[3]) if recs else None
        bk = max((r for r in recs if r[4]), key=lambda r: r[3], default=None); bo = max((r for r in recs if not r[4]), key=lambda r: r[3], default=None)
        it = dict(id=qid, group=g, kept_titles=kt, n_chunks=len(recs), n_kept_article_chunks=sum(r[4] for r in recs),
                  max_p=best[3] if best else None, best_title=best[2] if best else None, best_in_kept=best[4] if best else None, best_chunk_id=best[0] if best else None,
                  max_p_kept=bk[3] if bk else None, max_p_other=bo[3] if bo else None, best_other_title=bo[2] if bo else None,
                  hits_ge_th=[dict(chunk=r[0], title=r[2], p=r[3], kept=r[4]) for r in recs if r[3] >= TH])
        return it, cost, reqs
    items = []; tc = 0.0; tq = 0
    with ThreadPoolExecutor(a.workers) as ex:
        for it, c, r in ex.map(work, plan): items.append(it); tc += c; tq += r
    ok = lambda v: v is not None and v >= TH
    summ = {}
    for g in ("on_topic", "off_topic_kept"):
        L = [i for i in items if i["group"] == g]; n = len(L)
        s = dict(n_items=n, anywhere_ge_th=sum(ok(i["max_p"]) for i in L), in_other_article=sum(ok(i["max_p_other"]) for i in L),
                 in_kept_article=sum(ok(i["max_p_kept"]) for i in L), other_only=sum(ok(i["max_p_other"]) and not ok(i["max_p_kept"]) for i in L),
                 no_chunks=sum(1 for i in L if not i["n_chunks"]))
        s["anywhere_share"] = round(s["anywhere_ge_th"] / n, 3) if n else None; s["pass_40pct"] = bool(n and s["anywhere_share"] >= 0.40); summ[g] = s
    out = dict(set=a.set, hypothesis="H5b ANYWHERE", threshold=TH, topk_per_query=TOPK, cap_chunks=CAPC, model=sg.MODEL, requests=tq, gateway_cost_usd=round(tc, 5), summary=summ, items=items)
    op = f"{sg.ROOT}/rnd/research/coordinator/arms/wikisection/aggregates/anywhere-gate-{a.set}.json"; json.dump(out, open(op, "w"), indent=1)
    for g, s in summ.items():
        print(f"{a.set} {g}: n={s['n_items']} anywhere>={TH}: {s['anywhere_ge_th']} ({s['anywhere_share']}) | other article: {s['in_other_article']} (other-only {s['other_only']}) | kept article: {s['in_kept_article']} | PASS40={s['pass_40pct']}")
    print(f"{a.set} requests(uncached)={tq} cost=${tc:.5f}")

if __name__ == "__main__": main()
