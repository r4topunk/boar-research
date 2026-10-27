# WIKIFULL stage B — DONE 2026-10-13 01:55 (criterion WIKIFULL-REOPEN ee81ad30…, stage B)
TL;DR: English Wikipedia pages outside FineWiki Aug-2025 (enwiki **20261001** dump) add **2** V-para items → pooled A+B = **9/34 verified → MARGINAL** (bands REOPEN ≥ 14 / MARGINAL 7–13 / CLOSE ≤ 6; 15/15 shards + B present). No WIKI-ALL arm. Lower bound: the old-id part of the delta was sampled at 28 % (see Caveats).

## Delta (tools/stageB/delta.py; aggregates/stageB-delta-counts.json)
- FineWiki side: page_id + title columns only of the 15 HuggingFaceFW/finewiki enwiki parquet shards @ 8bd13e72 (hyparquet HTTP range reads, ≈ 12 MB/shard, 6,498,759 page_ids).
- Dump side: enwiki-20261001 multistream index (25.9 M rows) − non-ns0 prefixes − redirects (20261001 redirect.sql.gz) = 7,249,154 ns0 pages; − same page_id in FineWiki (6.35 M same title + 95,834 renamed: content covered) − new page_id with a FineWiki title (5,223) − disambiguation pages (page_props, 376,106) = **delta 418,962 pages**: 226,058 with page_id > FineWiki max (80,803,173 = created after the snapshot) + 192,904 older ids that FineWiki lacks.
- Bytes: full delta = 122,046 bz2 streams, 13.25 GB > 6 GB cap → stratified (better than uniform for the "new pages" question): **all** new-id pages (12,060 streams, 1.03 GB) + seed-11 uniform **28 %** of the old-id pages. Fetched **5.85 GB** (32,841 range requests, 2 connections, no gap fill), 280,071 pages wanted, 280,035 kept (36 #REDIRECT).

## Pack (boar-wiki-en-B.sqlite, sha256 09c43792…a1e9e2, 834 MB; kept on the mini under <runner>/kiln/wikifull-b/work/)
- tools/stageB/wikifullb_convert.mjs: body = builder's own `cleanWikivoyage` (wikitext → text); `{{Infobox …}}` params flattened to FineWiki's infobox shape (builder's `infoboxText` "Key facts" line); dropped 10,595 template-disambiguation + 14,128 bodies < 200 chars. Then `build-wiki-pack.mjs --shards <3 JSONL parts> --no-embed` (no pageviews → every page kept in full).
- Counts: **255,304 articles** (209,496 new-id, 45,808 old-id sample), 1,494,823 chunks, 1,436,713 indexed, 755 MB text.

## Gate (tools/wikifull_gate.py --shard <pack> --tag B, A0 logic unchanged; aggregates/stageA-<set>-B.json)
| set | group | n | B verified | B ≥0.7 | B ≥0.6 | B-only verified (new vs A) | pooled A (15) | pooled A+B |
|---|---|---|---|---|---|---|---|---|
| V-para | on_topic | 13 | 2 | 2 | 2 | 1 | 3 | 4 |
| V-para | off_topic_kept | 1 | 0 | 0 | 0 | 0 | 1 | 1 |
| V-para | no_kept | 20 | 1 | 1 | 1 | 1 | 3 | 4 |
| **V-para** | **ALL** | 34 | 3 | 3 | 3 | **2** | **7** | **9** |
| v0.2 (dev) | ALL | 78 | 2 | 4 | 8 | 1 | 37 | 38 |
- V-para B hits: 2 items on one post-snapshot page (page_id > 80.8 M; one item was already verified on shard 12), 1 item on an old-id page FineWiki lacks (page_id 62.4 M; from the 28 % sample). Pooled ≥0.7 unverified 12/34, ≥0.6 17/34; verified outside top-100k 8/34.
- `python3 -I tools/stageA_pool.py --with-b` (extended: pools stageA-<set>-B.json; bands only with 15 shards + B) → aggregates/stageAB-pooled.json. Its v0.2 band label ("REOPEN 38/78") is the script applying V-para bands to dev context; not a decision.

## Verdict (frozen rule): **MARGINAL — 9/34 verified (A 7 + B 2)**. B does not lift the pooled count to ≥ 14 → no WIKI-ALL arm; Wikipedia is not reopened as kit content for V-para, and not closed either (> 6).

## Spend and disk
- jev: V-para [usage detail removed] (927 calls) + v0.2 [usage detail removed] (2,254 calls; allowed: V-para ≤ [usage detail removed] and balance stays ≥ [usage detail removed]) = **[usage detail removed]** (cap [usage detail removed]). Gateway balance 0.684 → **0.591**. No judge calls, no llama-server, no Docker.
- Mini: <runner>/shared-data/dumps/20261001/ 930 MB (index, redirect.sql.gz, page_props.sql.gz); <runner>/kiln/wikifull-b/ 3.9 GB (pack 834 MB + raw.jsonl 3.1 GB + id lists); free 31 GiB. MacBook: pack deleted after the gate.

## Caveats
- Lower bound on B: old-id delta sampled at 28 %; its sample gave 1 B-only item, so the 72 % not fetched could add ≈ 0–3 more (naive scaling), still < 14. Fetching it is ≈ 7.4 GB more (`fetch.py --old-frac 1.0`, resumable; same raw.jsonl).
- Text path differs from FineWiki (rendered HTML): `cleanWikivoyage` drops non-listing templates (e.g. {{convert}}, date templates) and all tables, so numbers inside templates/tables are lost in B (infobox values kept). Biases B down.
- B's pack is small (255 k articles), so its FTS idf differs from a 400 k-article shard; same gate code, 40-chunk cap per item.
- FineWiki membership is by page_id; the stage-A packs hold 6.12 M of FineWiki's 6.50 M ids (builder drops chunkless pages); those ≈ 0.4 M are in neither A nor B (tiny pages).
- quote_supports is a jev boolean proxy (as in A). Blind read script-only; only ids/titles/probabilities/counts printed.
- Resume/rebuild: tools/stageB/ (fw_ids → delta.py → fetch.py → after_fetch.sh), logs on the mini under <runner>/kiln/wikifull-b/logs/. EXPOSURES row + QUEUE entry: coordinator.
