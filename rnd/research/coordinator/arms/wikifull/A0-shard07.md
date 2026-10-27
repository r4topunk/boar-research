# T2 stage A0: WIKIFULL anywhere-gate on shard 07 (2026-10-12)
TL;DR: one local shard of 15, 0 Claude calls, [usage detail removed] jev. NOT a verdict against WIKIFULL-REOPEN (14/34): A0 covers 1 of 15 shards.
- Shard: `shared-data/gate-ref/boar-wiki-en-07.sqlite`, formatVersion 2, "English Wikipedia (part 07 of 15)", 403,973 articles, 1,913,583 chunks, 1,581,704 indexed (17.3 % table/unindexed), built 2026-09-26, FineWiki Aug-2025, fullTop 1M / leadChars 2500, 1.21 GB.
- Tool: `tools/wikifull_gate.py` (imports section_gate/anywhere_gate; q1 12-term OR, q2 title+6 terms or top-4 AND, + table chunks of top-5 hit articles, Σ-idf rescore from shard fts5vocab, top 40, jev has_fact, then jev quote_supports on p >= 0.7). Cache: blind/<set>/runs-dt512{,v02}/wikifull-cache (also reads the H5b cache). Aggregates: `aggregates/A0-shard07-{vpara,v02}.json`.
- quote_supports is a jev boolean proxy (not a verbatim quote check), so "verified" is weaker than the design's local-judge quote.

| set (absent items) | n | split on/off/no-kept | items with a hit p>=0.6 / 0.7 / 0.8 | verified @0.7 | hit in table chunk @0.7 | hit in article outside top-100k @0.7 (verified) |
|---|---|---|---|---|---|---|
| V-para | 34 | 13 / 1 / 20 | 3 / 1 / 1 | 0 | 0 | 0 (0) |
| v0.2 (dev) | 78 | 30 / 14 / 34 | 19 / 11 / 6 | 9 | 0 | 5 (4) |

- V-para by group at p>=0.7: on-topic 1/13 (Quantum computing, p 0.80, a top-100k article, not verified), off-kept 0/1, no-kept 0/20 (one at 0.6). So the 20 no-kept items add nothing on this shard.
- v0.2 by group at p>=0.7: on-topic 7/30, off-kept 2/14, no-kept 2/34 (Leap year, Nikon D200; both verified). Verified hits: Inflation targeting, Season, GPS, Emperor Meiji, Astana, Leap year, Roman Empire history, Cottonopolis/Liverpool/Salford cluster, Nikon D200.
- Table chunks: 1,141 (V-para) and 1,978 (v0.2) table candidates entered the pool; only 1 chunk reached p >= 0.6 (v0.2), none at 0.7. Numeric facts in tables are not where the hits are, at least on this shard.
- Cost and time: V-para 1,124 uncached requests, [usage detail removed], 74 s; v0.2 2,778 requests, [usage detail removed], 164 s ([usage detail removed]).
- What A0 validates: tooling end to end (Σ-idf query, no-kept items, table-chunk coverage, quote proxy), the cost/time model (about [usage detail removed] per 34 items per shard), and that the rank-100k..1M body tier of one shard adds no V-para hits (0 outside-top-100k hits). What only stages A/B answer: the other 14 shards (the pooled 15-shard count and the 14/34 bar), post-Aug-2025 freshness (stage B), and a local-judge verbatim-quote verification.
- UNKNOWN: threshold sensitivity; V-para ge06 3/34 vs ge07 1/34 mirrors H5b's 4/13 vs 1/13 pattern; hits sit near the cut.
