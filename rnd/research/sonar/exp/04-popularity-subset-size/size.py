"""Sonar exp-04: size of a popularity-ordered English Wikipedia subset (top-N articles in full), estimated from
(1) pageviews-en-20250815.tsv (page_id -> views, the builder's own popularity input), (2) boar-wiki-sample.sqlite =
the format-2 build of ONE FineWiki shard (000_00007) with fullTop 1,000,000 (so articles ranked <= 1M are stored in full),
(3) the 15 shard manifests (pack bytes vs text bytes). Shards are a random split of articles, so the sample shard's
top-N articles are ~an unbiased 1/15 sample of the global top-N. Read-only."""
import json, glob, sqlite3, bisect
views = sorted((int(l.split("\t")[1]) for l in open("<workspace>/shared-data/dumps/pageviews-en-20250815.tsv")), reverse=True)
db = sqlite3.connect("file:<workspace>/shared-data/packs/boar-wiki-sample.sqlite?mode=ro", uri=True)
arts = db.execute("SELECT views, len FROM articles WHERE source = 0").fetchall()  # enwiki only
man = [json.load(open(f)) for f in sorted(glob.glob("<workspace>/shared-data/packs/boar-wiki-en-*.sqlite.json"))]
pack_per_text = sum(m["sizeBytes"] for m in man) / sum(m["textBytes"] for m in man)
fts_share = sum(m["tables"]["fts_data"] for m in man) / sum(m["sizeBytes"] for m in man)
print(f"15 shards: {sum(m['sizeBytes'] for m in man)/1e9:.2f} GB pack, {sum(m['textBytes'] for m in man)/1e9:.2f} GB text, {sum(m['articles'] for m in man):,} articles; pack/text = {pack_per_text:.3f}; fts_data share {fts_share:.2f}")
print(f"pageview pages {len(views):,}; sample shard enwiki articles {len(arts):,}")
rows = []
for N in (50_000, 100_000, 200_000, 300_000, 500_000, 1_000_000):
    thr = views[N - 1]
    sel = [ln for v, ln in arts if v >= thr]
    scale = N / max(len(sel), 1)
    text = sum(sel) * scale
    rows.append((N, thr, len(sel), text / 1e9, text * pack_per_text / 1e9, sum(sel) / len(sel)))
    print(f"top {N:>9,}: views>={thr:>6}  in sample {len(sel):>6,} (x{scale:.1f})  full text ~{text/1e9:5.2f} GB  -> pack ~{text*pack_per_text/1e9:5.2f} GB  (mean article {sum(sel)/len(sel)/1e3:.1f} kB)")
json.dump(rows, open("size.json", "w"))
