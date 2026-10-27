# BLOCKCACHE criterion (frozen 2026-10-21, before the replay; 0 LLM, 0 judge, 0 paid)

Hypothesis: ruler/hypotheses-round4-2026-10-21.json id "H-A3 BLOCKCACHE" (line E1 engine time, GOAL-2026-10-21.md).

## Facts read from the code before freezing (bench-app/engine, wikiPack.ts, parsearch tree 8ad2c4b0)
- BLOCK_CACHE = 16 is the size of a per-pack LRU (one Lru per WikiPack instance), not a global one: large packs cannot evict small ones, but the memory bound is per pack (256 x 64 KB = 16 MB per pack, up to 6 x 16 MB with six packs). The hypothesis's "at most +16 MB" is therefore not a given; it is measured here.
- A miss = a block() call that does not find the block in that pack's LRU and runs fzstd decompress (the compressed-block prefetch window BLOCK_WINDOW and the ARTICLE_CACHE are unchanged).

## Method
- Desktop node replay (boar-eval replay-retrieval.sh, --gate rules, engine k, MacBook) on a scratch copy of bench-app/engine with an instrumentation patch (tools/blockcache-instrument.patch): BLOCK_CACHE read from an env var (0 = unbounded); every miss logged with pack id and block id; held decompressed bytes (sum over all packs' LRUs) logged after each miss; a marker per searchWikiPacks call. Packs = the 6 A-union files (shared-data/packs/persona-a-union, SHA256SUMS). One node process per (order, cache size): the LRU state carries across questions as in a phone session.
- Orders: S = aunion73-a request order (73 incl. warmup); R1-R3 = the 72 non-warmup questions shuffled with python random.Random(seed).shuffle, seed 1/2/3, warmup first; M = MAIN 97 in the order of gemma4-e2b/vs4b K0 main requests (ids = lp-screens/main-97.ids).
- Cache sizes: 16 (control), 64, 256, unbounded.
- Recorded per run: misses per pack and per search, peak held decompressed bytes, ordered raw hit list per item.
- Parity (precondition): ordered raw lists identical across cache sizes within each order; any diff -> result void.
- Gain(order, size) = 1 - misses(size) / misses(16), whole session including the cold first questions.
- Extra bytes(size) = peak held bytes(size) - peak held bytes(16), all packs summed, on S.

## Kill (frozen, from the hypothesis)
At size 256: Gain(S) < 30 % OR extra bytes > 32 MB OR mean Gain(R1..R3) < 0.5 x Gain(S) -> CLOSED (the gain depends on question order or does not exist). Otherwise GO for the device A/B. M is reported, not gating.
The same three tests are reported for 64 and unbounded (descriptive; only 256 decides).

## Projection (phone, no new phone data)
- Validation first: replay misses at 16 per search vs the phone's compressed blocks fetched per search (PARTIME FROM-blocks rows) on aunion73-a; reported as a ratio.
- Per question q and pack p on S: saved_ms = (misses16 - missesX) x 16.0 ms (PARTIME ms_per_block). Serial: new search = sum over packs of (window - saved). Promise.all (JS-bound LB, PARTIME): max(sum over packs of (js - saved), max over packs of (window - saved)). T_q = total - (serial search - new search); T_8GB p50 over the 73 rows (perq-aunion73-a.json).
- Caveat stated with the number: 16.0 ms/block is the whole block phase per block (fetch + decompress + materialize), so cache hits that still materialize remove less; the projection is an upper bound on saving.
- APK rule: projected serial p50 saving at 256 >= 1.0 s -> build the bench APK on top of the parsearch patch (const BLOCK_CACHE = 256 only), tag -blockcache256-, and append a frozen-prediction run to DEVICE-DAY-2026-10-22 step E1-PAR.
