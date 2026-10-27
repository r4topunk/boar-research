# REPACK16: repack pack zstd blocks 64 KB -> 16 / 32 KB, desktop replay (0 LLM, MacBook, 2026-10-21)

TL;DR: **KILL by the frozen criterion** (REPACK16-criterion.md, sha daedb7dd, commit 38c5a047). Repacking only Wikivoyage (the device kit A) cuts decoded bytes per search by **18 %** at 64 slots (ratio 0.819 S / 0.821 M; rule <= 0.50), with retrieval **identical 26/26 runs** and size **+4.6 %**. The PARTIAL-DECOMP figure (-70 to -75 %) holds only when all 6 packs are repacked AND slots are raised to keep cached bytes equal: descriptive all-6 replay at 256 slots = **-70.5 % (S) / -69.7 % (M)** vs today's 64 KB at 64 slots. Scope note: the lever is **bench-only**; on the native Kotlin app retrieval is 0.6-1.6 % of an answer (arms/native-partime/NATIVE-PARTIME.md), so a repack saves at most ~0.06 s there. No device arm, no APK, no publish.

## Builder and repack
- Builder (mini, kiln/packs/builder-cf/scripts/build-wiki-pack.mjs) already has `--block-kb N` (default 64; l.74/112/151): articles appended in id order, block closed once blockLen >= N KB (l.233-237), zstd level 12. **No builder change needed.**
- A rebuild from the dump would also change article text (convert-fix lib) and embeddings, so the packs were repacked from the existing files instead: tools/repack.mjs rewrites only `blocks` and `articles(block_id, off, len)` with the builder's exact rule, other tables untouched, VACUUM INTO. Tool check: repack at 64 KB reproduces the original layout for 34 002 / 34 002 (wikivoyage) and 208 711 / 208 711 (simplewiki) articles, zdata byte-identical (block 7 compared); article text identical 100 % at 16 / 32 / 64 for all 7 packs (aggregates/check-*.json*).
- Ran on the MacBook, not the mini: mini had 26 GiB free (floor 25) and 4 extra files need ~1.8 GB. MacBook scratch only; originals and device-day kit dirs untouched.

| pack | KB | blocks | zdata MB | file bytes (vs original) | sha256 | wall |
|---|---|---|---|---|---|---|
| wikivoyage ff8595e3 | 64 | 3 531 | 108.8 | 351 092 736 | ff8595e3 | - |
| | 32 | 6 137 | 112.1 (+3.0 %) | 359 874 560 (+2.5 %) | 98765f6c | 20 s |
| | 16 | 9 981 | 115.0 (+5.8 %) | 367 206 400 (**+4.6 %**) | 6f004263 | 22 s |
| simplewiki r2 e14bdff1 | 64 | 4 844 | 121.2 | 481 017 856 | e14bdff1 | - |
| | 32 | 9 167 | 125.9 (+3.9 %) | 501 833 728 (+4.3 %) | fe9926eb | 39 s |
| | 16 | 17 012 | 130.8 (+7.9 %) | 508 698 624 (**+5.8 %**) | 20f21826 | 28 s |
- File growth > zdata growth: each blob loses about half an 8 KB page to overflow slack. The other 5 A-union packs at 16 KB (descriptive): 2 319 blocks vs 832, zdata 21.5 MB; their files shrink 4-32 % only because the originals were not vacuumed (aggregates/repack-other5-16.jsonl).

## Replay (boar-eval replay-retrieval.sh, --gate rules; scratch engine = bench-app/engine parsearch 8ad2c4b0 + blockcache-instrument.patch)
Validation: A-S-64 at 16 slots = 13 549 misses and at 64 = 6 862, M = 21 302 / 11 702 (= BLOCKCACHE.md exactly).
Decoded KB per search (whole session; S = aunion73-a 59 searches, M = MAIN 97 86 searches):

| kit | block KB | slots | S KB/search | M KB/search | vs 64 KB same slots | peak held MB (S) |
|---|---|---|---|---|---|---|
| A (6 packs) | 64 | 16 | 18 494 | 20 150 | - | 8.2 |
| A | 64 | 64 | 9 572 | 11 280 | - | 28.3 |
| A, wikivoyage 32 | 32 | 64 | 8 386 | 9 899 | 0.876 / 0.878 | 26.8 |
| **A, wikivoyage 16 (criterion)** | 16 | 64 | 7 841 | 9 263 | **0.819 / 0.821** | 25.8 |
| A, wikivoyage 16 | 16 | 256 | 2 788 | 3 225 | 0.151 / 0.160 vs 64 KB@16 | 62.5 |
| A6 all 6 at 16 (descriptive) | 16 | 16 | 8 862 | 9 950 | 0.479 / 0.494 | 4.0 |
| A6 all 6 at 16 | 16 | 64 | 6 363 | 7 552 | 0.665 / 0.670 | 13.7 |
| A6 all 6 at 16 | 16 | 256 | 2 824 | 3 422 | **0.295 / 0.303 vs 64 KB@64** | 43.0 |
| A+SW (7 packs) 64 | 64 | 64 | 12 129 | 14 125 | - | 32.6 |
| A+SW, wv + sw at 16 | 16 | 64 | 8 612 | 10 106 | 0.710 / 0.716 | 27.0 |
- Why only -18 %: per pack, wikivoyage bytes fall 201.8 -> 99.7 MB (-51 %) and simplewiki 150.9 -> 45.5 MB (-70 %) at 64 slots, but wikivoyage is 36 % of kit A's decoded bytes; the other 5 packs stay at 64 KB. Misses barely move (6 862 -> 6 902): almost every miss is a block holding one needed article, so smaller blocks cut bytes per miss, not misses.
- Why all-6 at 64 slots gains only 33 %: at 16 KB the small packs stop fitting in 64 slots (firstaid 193 -> 561 blocks, factbook 102 -> 231), so misses rise +59 %. Raising slots to 256 (cached bytes about the same as 64 KB x 64) gives the -70 % at +15 MB held vs 64 KB@64.
- Parity: ordered raw (title, section, source) and kept `sources` identical to the 64 KB run in **26/26** comparisons (kits A, A+SW, A6; S 73 and M 97 items; 39 items with kept sources each; aggregates/repack16-summary.json).

## MacBook decode time (fzstd 0.1.1, logged miss sequences, median of 5; aggregates/decode-bench.jsonl)
| config | S ms/search | M ms/search | ms per miss |
|---|---|---|---|
| A 64 KB, 16 slots (today) | 99.4 | 102.2 | 0.43 |
| A 64 KB, 64 slots (arm E) | 51.4 | 60.1 | 0.44 |
| A wikivoyage 16, 64 slots | 40.9 (-20 %) | 48.7 (-19 %) | 0.35 |
| A6 16 KB, 64 slots | 38.2 (-26 %) | 44.9 (-25 %) | 0.21 |
| A6 16 KB, 256 slots | 18.2 (-65 %) | 22.0 (-63 %) | 0.22 |
- A 16 KB decode costs 0.21 ms vs 0.43 ms for 64 KB: half, not a quarter (per-call overhead), so time falls less than bytes. Phone scale (BLOCKCACHE: 12.5 ms per 80.5 KB decompression, ~28x the desktop) would put kit A at -0.3 s per search; on the native app this is inside a 0.3-0.5 s retrieval.

## Verdict
| clause | value | rule | result |
|---|---|---|---|
| 1 decoded bytes, kit A, 64 slots | 0.819 (S) / 0.821 (M) | <= 0.50 both | **FAIL** |
| 2 parity raw + kept | 26/26 identical | 100 % | pass |
| 3 size, 16 KB file vs original | wikivoyage +4.6 %, simplewiki +5.8 % | <= 8 % | pass |
-> **KILL.** Not adopted for a device A/B; device-day arm F not added (scope change: bench-only lever); no APK built, so no BENCH_WASM log line (void anyway: the submission is the native app). No 6-pack rebuild estimate (out of scope).
- The finding is still useful for the research page: smaller blocks are retrieval-neutral (26/26) and cost +4.6-5.8 % size; the byte saving needs all packs repacked and a slot count scaled to block size (all-6 at 256 slots: -70 % bytes, -64 % desktop decode time vs 64 KB at 64 slots).
- Transfers to the native app mechanically: its WikiPack.kt reads blocks the same way (lru 16 per pack l.309, `zstd.decompress` l.341, `String(block(a.blockId), a.off, a.len)` l.349; wt/native-qa/android-native/engine/src/main/java/team/sopa/boar/engine/rag/WikiPack.kt), so a repacked file needs no engine change there either; with JNI libzstd per-call overhead and the share of retrieval differ.

## UNKNOWN
- Phone cost of more, smaller SQL blob reads (BLOCK_WINDOW prefetch of 8 covers 1/4 of the bytes); not replayable on the desktop.
- Byte-budgeted cache (slots x block size constant) was not frozen; the 256-slot rows are descriptive.

Files: tools/{repack.mjs, check.mjs, run_replay.sh, analyze.py, decode_bench.mjs, run_decode.sh}; aggregates/{repack-wikivoyage.jsonl, repack-simplewiki.jsonl, repack-other5-16.jsonl, check-*.json*, repack16-summary.json, decode-bench.jsonl}. Repacked files in the session scratchpad only (rebuildable from tools/repack.mjs + the input shas; deterministic).
