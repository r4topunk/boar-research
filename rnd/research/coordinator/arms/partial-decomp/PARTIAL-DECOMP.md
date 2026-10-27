# PARTIAL-DECOMP: stop decompressing a pack block at the needed offset (0 LLM, MacBook, 2026-10-21; web log 23.3b)

TL;DR: **with fzstd streaming the saving is ~0 (0.06-0.35 % of decoded bytes)**, because 95.6 % of pack blocks are ONE zstd block (fzstd streams per zstd block, <= 128 KB) so there is nothing to stop at. A decoder that could stop mid-block would save 20-32 %, and **repacking the pack into 16 KB blocks saves 70-75 % of decoded bytes (+6.5 % pack size)** with no decoder change. Class: pack-build change (new pack version), not an engine flag.

## Layout (wikiPack.ts, packs.sqlite format 2)
- Unit stored in a block is the ARTICLE, not the chunk: `articles(block_id, off, len)`; `article()` decompresses the block, slices [off, off+len) and decodes the whole article (chunks are offsets inside that text; they are read after, from the article LRU). Block cache = per-pack FIFO map (Map.get does not refresh), 16 slots.
- Builder params: blockKb 64 (closes a block once >= 64 KB), zlevel 12, no dictionary. Across the 6 A-union packs: 4 363 blocks, 40 649 articles = **9.3 articles and 149 chunks per block** (wikivoyage 9.6 / 155; crypto 7.7 / 135; factbook 2.6 / 103; medlineplus 29 / 87). Decompressed block mean 81.5 KB (p10 66, p90 105 KB).
- Needed article inside its block: **end offset / block length: p10 0.18, p25 0.37, p50 0.62, mean 0.63** over 16 529 article reads (aunion73-a, 73 questions, 59 pack searches, replay on the instrumented be-pd tree: misses 13 549 at 16 slots, 6 862 at 64 = BLOCKCACHE.md exactly). Per decompression, counting every later hit of the cached block (max end over the residency): p50 0.70 (16 slots) / 0.81 (64 slots), mean 0.67 / 0.72.

## Why fzstd streaming does not help
- Zstd blocks inside a frame are <= 128 KB decompressed; fzstd `Decompress.ondata` fires once per zstd block. Our 2 235 touched blocks: 1 zstd block 2 137 (95.6 %), 2 blocks 96, 3-7 blocks 2. Stopping at the zstd block that covers the needed end moves the stop fraction to 1.0 for 99.1 % of decompressions.
- Bench (bench.mjs, Node 25.9, fzstd 0.1.1, 200 real blocks x 3 seeded articles = 600 pairs, median of 7 reps): full `decompress` 0.363 ms, streaming-all 0.371 ms, streaming-stop 0.372 ms (stop = 1.02x full on 591 single-block pairs: pure overhead). Only the 9 pairs on multi-block frames gain: 0.754 -> 0.707 ms (stop = 0.88x total).
- Cache semantics: replayed with a prefix-cache (hit needing a later zstd block = re-decode from the start, or resume from the kept Decompress state): 15 upgrades in 16 529 reads. With a hypothetical mid-block stopper the upgrades are 1 130 (7 %), still small; resume (keep decoder state + compressed bytes) beats restart (-31.7 % vs -28.7 % at 16 slots; -26.9 % vs -20.0 % at 64).

## Decoded bytes over the 73-question session (MB; saved vs full-block decode)
| variant | 16 slots | 64 slots (BLOCKCACHE 64) |
|---|---|---|
| full block (today) | 1 091 | 565 |
| fzstd stream-stop, resume / restart | 1 089 / 1 090 (-0.24 / -0.06 %) | 563 / 565 (-0.35 / -0.00 %) |
| hypothetical byte-exact stop, resume / restart (native libzstd streaming, not fzstd) | 745 / 778 (-31.7 / -28.7 %) | 413 / 452 (-26.9 / -20.0 %) |
| repack 16 KB blocks, same cached bytes (256 slots/pack at "64") | 322 (-70.5 %) | 143 (-74.6 %) |
| repack 32 KB blocks | 484 (-55.7 %) | 259 (-54.1 %) |
- Repack sim: articles never split, greedy <= N KB (article larger than N = its own block), slots scaled by 64/N so cached bytes are equal (conservative: shipped blocks average 81 KB, my 64 KB control 14 % smaller), whole-block decode per miss. Pack size (node zstd level 12, 6 packs): 16 KB +6.5 % (+8.5 MB of 131), 32 KB +3.9 %, 4 363 -> 19 511 blocks (16 KB). Wikivoyage is the whole size (111 of 131 MB).
- Time: desktop fzstd 4.79 ms per decoded MB (0.36 ms per 76 KB). Phone scale (BLOCKCACHE.md: 12.5 ms per decompression of 80.5 KB = 155 ms/MB at f=1, 93 at f=0.6): per pack search saved on top of BLOCKCACHE 64 (baseline decode 1.49 s/search at f=1): fzstd stream-stop 3-5 ms (nothing); mid-block stop 0.24-0.40 s; **repack 16 KB 0.67-1.11 s, repack 32 KB 0.48-0.80 s**. Session means, upper bounds: the real phone cost of a hit/miss, SQL rows (4.5x more rows at 16 KB) and the BLOCK_WINDOW prefetch are not modelled.

## Verdict
- fzstd streaming stop: CLOSED, no gain (flag or engine change not worth it; zstd frame structure is the cause).
- Real lever = **pack-build change** (blockKb 64 -> 16-32, new pack version + re-publish; engine unchanged because article() already reads [off, off+len)) and it stacks with BLOCKCACHE 64 only partly (fewer, smaller cache entries; the 64-slot cache of 16 KB blocks holds 1/4 of the bytes unless slots are raised: memory-neutral at 256 slots). Needs a device A/B (1 rebuilt pack, e.g. firstaid, + the e1par order) before adopting; sizes +4-6 %. A mid-block-stop decoder (zstd-jni/native libzstd `ZSTD_decompressStream`) on the Kotlin app would give 20-32 % without a rebuild.
- UNKNOWN: phone share of decompression in the 12.5 ms; chunk-level reads (engine still materialises whole articles; byte offsets of chunks are UTF-16 offsets, not stored as bytes); retrieval-quality neutrality of smaller blocks (should be nil: only storage changes).
Files: partial.mjs (layout + cache sim), bench.mjs, repack.mjs, project.mjs, article-log.patch (be-bc + one "art" log line), aggregates/{replay-sim,bench-stop,repack-sim,projection}.json, S-16.article-reads.jsonl.gz (gunzip into a file for partial.mjs/repack.mjs).
