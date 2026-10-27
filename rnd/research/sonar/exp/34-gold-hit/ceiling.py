"""L0 coverage ceiling (Sonar exp-34): for each v0.1 EN item, the pageview rank of its gold Wikipedia articles
(Anvil oracle articles.jsonl), offline: titles -> page ids from the local enwiki multistream index, ranks from
pageviews-en-20250815.tsv (the ranking the top-N packs were cut by). No network."""
import json, bz2, bisect, collections
D = "<workspace>/shared-data/dumps/"
O = "<workspace>/rnd/research/anvil/exp/oracle/"
ids = open("<workspace>/rnd/research/anvil/exp/outofkit/v01-en-ids.txt").read().strip().split(",")
gold = collections.defaultdict(list)
for l in open(O + "articles.jsonl"):
    a = json.loads(l)
    if a["kind"] == "wiki": gold[a["id"]].append(a["title"])
top = {}
for l in open(O + "ctx-R450.jsonl"):
    r = json.loads(l)
    w = [p["title"] for p in r["passages"] if p["kind"] == "wiki"]
    if w: top[r["id"]] = collections.Counter(w).most_common(1)[0][0]
want = {t for v in gold.values() for t in v}
pid = {}
with bz2.open(D + "enwiki-latest-pages-articles-multistream-index.txt.bz2", "rt") as f:
    for l in f:
        _, p, t = l.rstrip("\n").split(":", 2)
        if t in want: pid[t] = int(p)
pv = {}
for l in open(D + "pageviews-en-20250815.tsv"):
    a, b = l.split("\t"); pv[int(a)] = int(b)
neg = sorted(-v for v in pv.values())
rank = lambda t: (bisect.bisect_left(neg, -pv[pid[t]]) + 1) if t in pid and pv.get(pid[t]) else None
rows = []
for i in ids:
    rs = [(rank(t), t) for t in gold.get(i, [])]
    best = min((r for r, _ in rs if r), default=None)
    tr = rank(top[i]) if i in top else None
    rows.append({"id": i, "gold": [[t, r] for r, t in rs], "best": best, "top_passage_article": top.get(i), "top_rank": tr})
json.dump(rows, open("ceiling.json", "w"), indent=0)
withg = [r for r in rows if r["gold"]]
print(f"items {len(ids)}; with a gold wiki article {len(withg)}; titles resolved {len(pid)}/{len(want)}")
for N in (10_000, 50_000, 100_000, 300_000, 1_000_000, 10**9):
    a = sum(1 for r in withg if r["best"] and r["best"] <= N)
    b = sum(1 for r in withg if r["top_rank"] and r["top_rank"] <= N)
    print(f"top{N if N < 10**9 else 'ALL'}: any gold article {a}/{len(withg)}; top-passage article {b}/{len(withg)}")
print("unresolved:", sorted(want - set(pid))[:20])
