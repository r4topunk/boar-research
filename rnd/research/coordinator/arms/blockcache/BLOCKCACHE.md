# BLOCKCACHE (H-A3): decompressed-block LRU 16 -> 64 / 256 / unbounded, desktop replay (2026-10-21)

TL;DR: raising BLOCK_CACHE cuts fzstd block decompressions by 78 % at 256 (49 % at 64), the same in every question order (shuffles 78 %, MAIN 97 76 %), with ordered raw hits identical in all 22 runs. But the cache is per pack, so 256 holds +65 MB of decompressed blocks (not +16 MB): **H-A3 as frozen is CLOSED by its bytes clause (> 32 MB)**. The phone projection is large anyway (T_8GB p50 7.57 -> 3.3-4.4 s serial, 2.4-2.8 s with Promise.all), so the device A/B (arm D, APK built) decides whether 65 MB on a 4.2 GB PSS matters. Size 64 passes all three clauses descriptively (+20 MB, 49 %, order-robust; p50 4.0-5.0 s serial) but was not the frozen size.

Criterion: BLOCKCACHE-criterion.md (sha in BLOCKCACHE-criterion.sha256, commit 4dab635a, before any run). 0 LLM, 0 judge, 0 paid; boar-app/ untouched; no llama.cpp/llama.rn change.

## Setup
- Tree: scratch copy of bench-app/engine (parsearch tree 8ad2c4b0) + tools/blockcache-instrument.patch (BLOCK_CACHE from env, 0 = unbounded; per-miss log with pack, block id, bytes held over all packs; a marker per searchWikiPacks call). Driver tools/run_replay.sh (boar-eval replay-retrieval.sh, --gate rules, MacBook), one process per (order, size) so LRU state carries across questions like a phone session.
- Packs: the 6 A-union files (shared-data/packs/persona-a-union), phone kit order. Orders: S = aunion73-a (73 incl. warmup, 59 pack searches), R1-R3 = 72 shuffled (seeds 1-3, warmup first), M = MAIN 97 (86 searches).
- Parity: ordered raw lists identical across all sizes in every order (22/22 runs, aggregates/raw-parity.json); instrumented S-16 = unpatched engine 73/73.
- Validation vs the phone: replay misses at 16 = 13 549 vs 10 583 compressed blocks fetched on the Pixel (ratio 1.28; p50 per search 232 vs 194). The extra 28 % are blocks evicted from the 16-slot LRU and decompressed again from the per-search compressed prefetch (no SQL fetch, so PARTIME did not count them). Hence 16.0 ms per fetched block = 12.5 ms per decompression.

## Misses (whole session, cold start included) and decompressed bytes held
| order | 16 | 64 | 256 | unbounded |
|---|---|---|---|---|
| S (aunion73-a) | 13 549 | 6 862 (-49.4 %) | 2 953 (-78.2 %) | 2 235 (-83.5 %) |
| R1 | 13 555 | 6 916 (-49.0 %) | 3 032 (-77.6 %) | 2 235 (-83.5 %) |
| R2 | 13 594 | 6 918 (-49.1 %) | 3 039 (-77.6 %) | 2 235 (-83.6 %) |
| R3 | 13 604 | 6 902 (-49.3 %) | 2 988 (-78.0 %) | 2 235 (-83.6 %) |
| M (MAIN 97) | 21 302 | 11 702 (-45.1 %) | 5 104 (-76.0 %) | 3 047 (-85.7 %) |
| peak held MB, S (extra vs 16) | 8.2 | 28.3 (+20.1) | 72.9 (+64.7) | 173.8 (+165.5) |
| peak held MB, M | 8.3 | 28.9 | 75.1 | 235.5 |
- Per pack at 256 (S): medlineplus 35, visa 95, factbook 102, firstaid 193 = every block of those packs exactly once (all fit); crypto 642 (379 distinct), wikivoyage 1 886 (1 431 distinct). At 16, medlineplus alone is decompressed 1 717 times (49 x its 35 blocks).
- Decompressed blocks are 66-86 KB, not 64 KB, so 256 slots per pack can hold about 16-21 MB per pack, and the small packs fill completely.

## Projected T_8GB on the Pixel (aunion73-a, 73 rows; saved = avoided decompressions x cost, clamped to each pack's JS time, applied to the PARTIME per-pack windows)
| size | cost/miss | p50 serial | p50 Promise.all (JS LB) | p90 serial | saved per search p50 |
|---|---|---|---|---|---|
| 16 (measured) | - | 7.57 | 5.53 | 15.05 | 0 |
| 64 | 16.0 / 12.5 / 8.0 ms | 4.01 / 4.31 / 4.98 | 2.46 / 2.73 / 3.16 | 13.50 / 13.81 / 14.23 | 1.47 / 1.23 / 0.80 s |
| 256 | 16.0 / 12.5 / 8.0 ms | 3.29 / 3.66 / 4.37 | 2.43 / 2.44 / 2.79 | 12.78 / 12.97 / 13.58 | 1.98 / 1.92 / 1.37 s |
| unbounded | 16.0 / 12.5 / 8.0 ms | 3.29 / 3.52 / 4.37 | 1.99 / 2.11 / 2.79 | 12.62 / 12.84 / 13.49 | 2.06 / 1.97 / 1.40 s |
- 16.0 ms = the frozen PARTIME rate (block phase per fetched block, includes materialize); 12.5 ms = the same per decompression (validation ratio); 8.0 ms = half, for the case where a hit still pays most of the materialize. Even 8.0 ms reaches the <= 5.0 s target at 64 or 256 serial.

## Verdict vs the frozen kill (only 256 decides)
| clause | value at 256 | rule | result |
|---|---|---|---|
| misses fall | -78.2 % (S) | < 30 % kills | pass |
| extra decompressed bytes | +64.7 MB | > 32 MB kills | **FAIL** |
| shuffled vs session gain | 77.8 % vs 78.2 % | < half kills | pass |
-> **CLOSED as stated** (the hypothesis assumed a global 16 MB cache; the LRU is per pack). Descriptive: 64 passes all three (+20.1 MB, -49 %, shuffles -49 %), projected p50 4.0-5.0 s serial / 2.5-3.2 s Promise.all. A 64-slot or a byte-budgeted cache (e.g. 32 MB over all packs) is a new hypothesis that needs its own criterion; it is not adopted from this table.

## APK (built because the 256 projection saves >= 1 s; criterion APK rule)
- bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-blockcache256-nonet-3bf53253e984.apk, sha256 74dbb664bae8eb5ba8669e0b99811a301c77827f8a76004141ba65316bb1299e (89.7 MB, no INTERNET).
- Engine = parsearch patch + BLOCK_CACHE 256 (tools/cut7-cmp30off-batchret-parsearch-blockcache256.vs-0cfd4a77.patch sha c1563afe..., delta tools/blockcache256.delta.patch); scripts/engine.sh --arm cut7-cmp30off-batchret-parsearch-blockcache256, tree 3bf53253; incremental gradle :app:assembleRelease (JDK17 Homebrew, BENCH_NONET=1) as PARSEARCH-APK.md; the release sourcemap shows BLOCK_CACHE = 256 and the Promise.all search. bench-app/engine restored to the parsearch tree afterwards; engine.lock.json unchanged.
- DEVICE-DAY-2026-10-22 step E1-PAR: arm D appended with a frozen prediction from the replay of the 11-question e1par order (decompressions 2728 -> 941, -65.5 %): search p50 1.0-1.5 s vs B 2.6, answer p50 6.6-7.0 s vs A 10.05 / B 8.9, about +57 MB of blocks held vs B. Request e1par-d.request.json.

## Caveats / UNKNOWN
- Hit cost: a cache hit still runs utf8 + passage materialize unless the article LRU (16) also hits; the phone A/B is the only real cost measure.
- The phone session starts cold after each APK install; the 73-row projection assumes one long session (cold misses included).
- Memory: +65 MB is measured JS-heap payload (Uint8Array bytes), not PSS; Hermes overhead and GC behaviour are unmeasured.
- Native Kotlin app: its own block cache shape is unknown; the app maintainer note should state "per-pack LRU of decompressed blocks sized to hold the small packs".
- Prior art for the app maintainer note (web log T23.3): libzim (Kiwix) caches decompressed clusters and moved to lazy streaming decompression (Streamreader, PR #421); the 2020 partial-decompression PR cut a kiwix-serve crawl 59 s -> 37 s on a 563 MB Wikipedia ZIM (https://github.com/openzim/libzim/pull/411 ; https://github.com/openzim/libzim/issues/84 ; https://web.dev/case-studies/kiwix). Server workload, no Android numbers.

Files: aggregates/blockcache-summary.json (all runs, per pack, projection, kill), perq-projection-256.json, raw-parity.json, e1par-d-prediction.json; tools/ (instrument patch, run_replay.sh, analyze.py, predict_e1par.py, APK patches).

## 64-slot candidate (BLOCKCACHE-64, 2026-10-21)
- Criterion BLOCKCACHE64-criterion.md (sha in BLOCKCACHE64-criterion.sha256, commit 2cf58d2b, before the build and any device run). Adopt iff device search p50 <= 0.6 x the Promise.all-only arm B, ordered titles identical, PSS E - B <= 0.032 GB; kill otherwise.
- Prediction (replay of the 11-question e1par order, tools/predict_e1par64.py): decompressions 2728 -> 1317 (-51.7 %), +20.5 MB held; search p50 1.26 / 1.42 / 1.72 s at 16.0 / 12.5 / 8.0 ms per avoided decompression (B 2.6), E/B 0.48 / 0.55 / 0.66; answer p50 6.67 / 6.77 / 7.21 s.
- APK: bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-batchret-parsearch-blockcache64-nonet-31ba12c473d1.apk, sha256 0a4e370effc1a3706566cbb4764d9c0a488f847ef10e665d2d6b0966dceaeb45 (+ .sha256 file); release sourcemap shows BLOCK_CACHE = 64 and Promise.all in packs.ts; patch tools/cut7-cmp30off-batchret-parsearch-blockcache64.vs-0cfd4a77.patch (sha 2d6c5ccb...), delta tools/blockcache64.delta.patch. bench-app/engine restored to the parsearch tree 8ad2c4b0.
- Device: DEVICE-DAY-2026-10-22 step E1-PAR arm E (request e1par-e.request.json); arm D (256) remains the ceiling measurement.
