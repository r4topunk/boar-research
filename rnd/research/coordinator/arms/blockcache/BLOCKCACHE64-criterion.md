# BLOCKCACHE-64 criterion (frozen 2026-10-21, before the APK build and before any device run; 0 LLM, 0 judge, 0 paid)

Candidate: the Promise.all search tree (bench-app engine tree 8ad2c4b0) plus `const BLOCK_CACHE = 64` in src/rag/wikiPack.ts (per-pack LRU of decompressed blocks; one-constant change, nothing else). Origin: BLOCKCACHE.md (256 closed by its +32 MB bytes clause at +64.7 MB; 64 passed all three clauses descriptively on the desktop replay: misses -49 %, +20.1 MB, order-robust, ordered raw hits identical).

## Test (device-day step E1-PAR, arm E)
Same 10 items + warmup, same phone state, cool phone (thermal_gate.py status 0, battery <= 31.0 C), request e1par-e.request.json (= e1par-d with the apk reference changed), compared with arm B (Promise.all only, same session).
- ADOPT for the app maintainer note iff all three hold: (1) search p50 (E) <= 0.6 x search p50 (B), (2) retrievedTitles ordered-identical to A and B on every item, (3) bytes held by the block LRUs <= B + 32 MB (device proxy: PSS peak E - PSS peak B <= 0.032 GB, with the replay figure +20.5 MB as the expected value).
- KILL otherwise. Also stop E on any LMK kill or PSS peak > A + 0.3 GB. A2 vs A drift rule of step E1-PAR applies (> 15 % search p50 difference -> rerun once after 10 min cooldown).
- If adopted, the note says: per-pack LRU of decompressed blocks, 64 slots (about 20 MB over six packs); Kotlin shape to be sized to hold the small packs. If E - B is < 0.4 s, the 16 ms/block cost is mostly materialize, not decompress, and the cache lever is closed on the phone.
- Arm D (256) stays as the ceiling measurement; it does not decide anything.

## Frozen prediction (replay of the 11-question e1par order, 0 LLM; tools/predict_e1par64.py, aggregates/e1par-e-prediction.json)
Block decompressions 2728 (size 16) -> 1317 (size 64), -51.7 %; ordered raw lists identical to size 16 (and to 256); peak held 28.75 MB vs 8.29 MB at 16 (+20.5 MB).
| cost per avoided decompression | 16.0 ms | 12.5 ms | 8.0 ms |
|---|---|---|---|
| search p50 E (B predicted 2.60, A 4.02) | 1.26 s | 1.42 s | 1.72 s |
| E / B search p50 | 0.48 | 0.55 | 0.66 |
| answer p50 E (A 10.05, B 8.9) | 6.67 s | 6.77 s | 7.21 s |
Reading: the 0.6 clause passes at 16.0 and 12.5 ms and fails at 8.0 ms; the device decides which cost is real.
