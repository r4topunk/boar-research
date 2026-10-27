# WIKIFULL/WIKIFRESH anywhere-gate: design only (not run), 2026-10-12

## TL;DR
- **Question it settles.** Are the deep tier's missing facts on V-para's absent-knowledge items anywhere in (a) all 15 Aug-2025 enwiki shards or (b) a fresh enwiki dump? The gate covers **all 34** absent items, including the 20 with no kept source.
- **What it costs.** 0 Claude calls. ≈ 4.5k jev requests per stage, [usage detail removed] each. Peak disk ≤ 3 GB. Wall ≈ 1–1.5 h (A) and 1.5–3 h (B) on the mini.
- **What it reuses.** `anywhere_gate.py`'s `terms()`/`mq()`/`ask()`, the jev cache and the item selection minus the `n_kept > 0` filter.
- **Pass bar `WIKIFULL-REOPEN`.** At least 14/34 V-para absent items must be *verified* present in A ∪ B. If ≥ 7/34 are found only in B, the next arm is a fresh-dump rebuild. At ≤ 6/34, Wikipedia is closed at every scope.
- **Preconditions owned by r4to.** Two downloads above the 100 MB rule: 14 shards ≈ 16.9 GB from his own HF dataset, and the dump at 25.8 GB, streamed. Free disk must be ≥ 28 GiB first: both machines sit at 25–26 GiB today.

## Why a new gate (verify/wikisection_scope.md)
H5b looked in a narrow place: the top-100k pack only, the FineWiki August 2025 snapshot, and FTS without tables (19.5 % of chunks are tables and are not indexed). It also gated only the 14/34 V-para absent items that kept a source. Those items hold 0.254 of arm H's V-para loss. The 20 items it skipped hold 0.333.

The 15 shards add full bodies for pageview ranks ≈ 100k–1M plus leads for ≈ 5.1 M more articles. No local corpus holds anything newer than August 2025.

## Inputs
| input | source | note |
|---|---|---|
| items | `arms/lossmap/aggregates/lossmap-H-{vpara,v02}-s42.json`: `primary == absent_knowledge` (V-para 34 = 13 on-topic + 1 off-kept + 20 no-kept; v0.2 78) | drop H5b's `n_kept > 0` filter; tag each item's group |
| query text | both Opus judge.v1 rationales (s42), script-only from the blind runs dirs, as `section_gate.py` does | `terms(r, 12)` unchanged, so results are comparable with H5b |
| second query | kept title + top 6 terms (as H5b). For no-kept items: top 4 terms as an implicit FTS5 AND | the AND query restores precision when there is no title anchor |
| term weights | document frequency from shard 07 (local `shared-data/gate-ref/boar-wiki-en-07.sqlite`, a random FineWiki shard) via `CREATE VIRTUAL TABLE temp.v USING fts5vocab(main,'fts','row')` on a read-only connection | one df table for both stages, so pooled scores are comparable across shards and the dump |
| judge | jev `has_fact`, exactly H5b's `Q` and request body, so identical chunk text hits the existing cache for free | threshold 0.7, as H5/H5b |

## Stage A: the 15 Aug-2025 shards (settles (a))
- **Shards.** Rotate one at a time. Shard 07 is already local. Shards 00–06 and 08–14 come from `huggingface.co/datasets/r4topunk/boar-packs` at the pinned commit 6e9afe96 (URLs and sha256 in `boar-app/src/rag/wikiEnPacks.ts`). Check each sha256, query it, delete it, fetch the next one.
- **Per shard and item.**
  - Run q1 (12-term OR) and q2, `bm25(fts,2,1,1)`, top 20 each.
  - Add the **table chunks**: chunks of the pooled top-5 articles whose id is missing from `fts_docsize` and whose text contains any numeric or capitalised item term.
- **Pool across 15 shards** (≤ 600 per item). Rescore by Σ idf over the distinct item terms in each chunk, then keep the **top 40 unseen** for jev. Chunks already judged in H5b are served from the cache at no cost and still count.
- **Requests.** 112 items × ≤ 40 = ≤ 4,480; ≈ 3.5–4.5k after cache, [usage detail removed]–0.13 at H5b's [usage detail removed] per 1k. Run V-para first (34 × 40 = 1,360). v0.2 is dev and secondary.
- **Wall time on the mini (M4 16 GB).**
  - Downloads: 14 × 1–3 min.
  - FTS: 3,360 queries × 0.2–1 s.
  - jev: 4.5k × 0.3 s / 8 workers ≈ 3 min.
  - Total ≈ 1–1.5 h, with the download of shard n+1 overlapping the queries on shard n.
- **Disk.** Peak 2.4 GB (current shard plus the prefetched one).

## Stage B: the 2026-10-01 enwiki XML dump (settles (b))
**Why this source.**
- No public 2026-09/10 Enterprise HTML exists: the mirror stopped 2025-03-24, and fresh HTML needs an account.
- No refreshed FineWiki exists.
- No 2026-09/10 Kiwix "all" nopic exists: the newest is 2026-06 at 52.7 GB, and maxi 2026-08 is 127 GB.
- The 20261001 `pages-articles-multistream{1..71}` parts total ≈ 27.2 GB bz2, completed 2026-10-08.

**Index choice: none.** A temporary FTS5 over the full dump would take about 22 GB of text plus about 11 GB of index, which breaks the disk floor. The plan instead:
1. **Stream each part with no file on disk.** Pipe the download through `lbzip2 -dc` into `python3 -I scan.py`, 2 parts in flight.
2. **Prefilter.** Run one compiled alternation over all items' terms against the raw wikitext. An article goes on only if it holds ≥ 3 distinct terms of one item.
3. **Strip markup** with `mwparserfromhell` (MIT) on the articles that pass. Infobox template parameters are kept as `key: value` lines, because numbers live there.
4. **Chunk** at 1,000 chars, matching the builder.
5. **Score** each chunk by the Σ-idf scorer above. Keep a top-60 heap per item, plus every chunk of the articles whose title matches a kept title or a Stage-A hit title (the fresh version of the same article).
6. **Judge.** Send the top 40 per item to jev.

**Attribution.** For each B hit, record the article's dump `<timestamp>`. Also record whether the same article in Stage A (Aug text) had p ≥ 0.7. "Fresh-only" means a B hit with no A hit on that item.

**Cost and time.**
- Requests ≈ 4.5k, [usage detail removed].
- Wall ≈ 1.5–3 h: the download at 5–20 MB/s bounds it, and the Python prefilter at ≈ 100 GB of XML across 2–4 processes adds to it.
- Disk < 1 GB: the heaps, plus a cache of judged chunk text under `blind/<set>/runs-dt512*/wikifull-cache/`, as H5b.
- **Optional B0, a 30-min probe.** Kiwix `wikipedia_en_top_nopic_2026-09` (2.75 GB, best 50k, 2026-09-14) with python-libzim's built-in Xapian `Searcher`. It gives only a same-tier freshness signal and does not settle (b) for the long tail.

**Rejected.**
- The live Wikipedia search API is cheapest, but it sends bench-derived terms to a third party and is not a fixed snapshot.
- CirrusSearch dumps are deprecated (last run 2025-12-29, 43 GB).

## Verification of hits (0 Claude calls)
H5b's v0.2 hits included tangential articles. For each item whose max p ≥ 0.7:
1. Ask the local judge (the JUDGE2 llama-server setup on the mini) to quote the sentence that states the missing fact, or to answer NONE.
2. **Verified** means a non-NONE quote that is found verbatim (whitespace-normalised) in the chunk, **and** jev p ≥ 0.7.

This is about 1–3 local calls per hit item, so ≤ 100 calls in all.

## Pass bar: `WIKIFULL-REOPEN` (freeze it with sha256 before any run; scope V-para, n = 34)
| outcome | rule | action |
|---|---|---|
| **REOPEN** | verified present in A ∪ B on **≥ 14/34** (≥ 40 %, the H5/H5b bar applied to the whole absent bucket) | Wikipedia stays a source. Arithmetic: 0.467 loss × 0.59 absent share × 0.40 × 0.3 retrieval+reading capture ≈ **+0.033**, about the V-para MDE 0.03. Below 40 %, no arm can be detected. |
| ↳ fresh route | of those, **≥ 7/34 fresh-only** (B hit, no A hit) | next arm: rebuild the shards from the 2026-10-01 dump (WIKIFRESH) |
| ↳ coverage route | fewer than 7 fresh-only, hits mostly in rank-100k–1M bodies or leads | next arm needs a **named new retrieval mechanism**. DEEPWIKI (peer pack, crowding) and DEEPCOV-FB (fallback) are closed for the top-100k, and the same mechanism over a bigger corpus is closed-family. |
| MARGINAL | 7–13/34 | report it. Use v0.2 (dev) for direction only. No arm. |
| **CLOSE** | **≤ 6/34** | Wikipedia is closed at every scope (Aug-2025 top-1M bodies + 5.1 M leads + Oct-2026 dump). Non-Wikipedia corpora (datastores Q-actions) are next. |

Also report:
- the split by group (on-topic / off-kept / no-kept);
- the counts at p ≥ 0.6 and 0.8, because H5b's 1/13 at 0.7 becomes 4/13 at 0.6;
- the hits that sit in table chunks.

## Exposure and rules
- Script-only on blind data. Only ids, titles, probabilities and counts go to rnd.
- jev receives the rationales plus public Wikipedia text, as in H5b.
- One row in `coordinator/EXPOSURES.md` plus a QUEUE entry.
- Downloads carry no item data. Both are above 100 MB, so they need r4to's OK: the shards are from his own HF dataset, the dump from Wikimedia.
- Disk: run the Kiln `disk-gc.sh --dry-run` first. Do not start below 28 GiB free.

## UNKNOWN
- The dumps.wikimedia.org per-IP concurrency limit and sustained speed from the mini. The wall time assumes 5–20 MB/s and 2 streams.
- `mwparserfromhell` throughput on the prefiltered subset. It is bounded by the prefilter pass rate, which is unmeasured.
- Whether the JUDGE2 local judge fits in RAM next to the scan on the 16 GB mini. If it does not, run verification after the scan.
