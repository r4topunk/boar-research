"""SECTIONHIT summary: counts per P1 bucket from aggregates/sectionhit.json (ids, ranks, booleans only; no text).
Usage: python3 -I tools/sectionhit_agg.py [aggregates/sectionhit.json]  -> prints tables; writes `summary` into the json."""
import json, sys, os
A = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "../aggregates/sectionhit.json")
d = json.load(open(A)); items = d["items"]
B = ["retrieved-not-used", "used-wrong", "used-right", "dropped-by-grounding", "not-retrieved"]
def rb(r):  # rank bucket
    return "null" if r is None else "1" if r <= 1 else "2" if r == 2 else "3" if r == 3 else "4" if r == 4 else ">4"
def row(xs):
    b = [x["best"] for x in xs]
    c = lambda f: sum(1 for h in b if h and f(h))
    out = {"n": len(xs), "article_raw": c(lambda h: h["article_in_raw"]), "article_kept": c(lambda h: h["article_in_kept"]),
           "sec_raw": c(lambda h: h["fact_section_in_raw"]), "sec_kept": c(lambda h: h["fact_section_in_kept"]),
           "chunk_kept": c(lambda h: h["fact_chunk_in_kept"]), "lead": c(lambda h: h["is_lead"]),
           "art_kept_sec_not": c(lambda h: h["article_in_kept"] and not h["fact_section_in_kept"]),
           "sec_kept_cut": c(lambda h: h["fact_section_in_kept"] and any(r is not None and r < 0.98 for r in h["kept_ratio"])),
           "health": sum(1 for x in xs if x["health_strict"])}
    for k in ("fact_section_rank", "rank_unfiltered", "alt_rank"):
        dist = {}
        for h in b:
            if h: dist[rb(h[k])] = dist.get(rb(h[k]), 0) + 1
        out[k] = dict(sorted(dist.items()))
    return out
S = {bk: row([x for x in items if x["bucket"] == bk]) for bk in B}
S["all"] = row(items)
# Headroom: article kept, fact section not kept (best hit; and min rank over F0 hits of kept articles).
H = [x for x in items if x["best"] and x["best"]["article_in_kept"] and not x["best"]["fact_section_in_kept"]]
def minr(x, k):
    rs = [h[k] for h in x["hits"] if h["article_in_kept"] and h[k] is not None]
    return min(rs) if rs else None
head = {"n": len(H), "ids": [x["id"] for x in H], "buckets": [x["bucket"] for x in H]}
for k in ("fact_section_rank", "rank_unfiltered", "alt_rank"):
    head[k] = [x["best"][k] for x in H]; head[k + "_min_over_hits"] = [minr(x, k) for x in H]
head["recover_keep3_engine"] = sum(1 for r in head["fact_section_rank_min_over_hits"] if r is not None and r <= 4)
head["recover_keep3_unfiltered"] = sum(1 for r in head["rank_unfiltered_min_over_hits"] if r is not None and r <= 4)
head["recover_alt_top2"] = sum(1 for r in head["alt_rank_min_over_hits"] if r is not None and r <= 3)
head["recover_alt_top3"] = sum(1 for r in head["alt_rank_min_over_hits"] if r is not None and r <= 4)
head["already_rank_le3"] = sum(1 for r in head["fact_section_rank_min_over_hits"] if r is not None and r <= 3)
S["headroom"] = head
d["summary"] = S
json.dump(d, open(A, "w"), indent=1)
for k, v in S.items(): print(k, json.dumps(v))
