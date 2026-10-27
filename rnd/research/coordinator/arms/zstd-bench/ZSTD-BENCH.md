# ZSTD-BENCH: fzstd vs WASM vs native zstd on real pack blocks (MacBook, 0 LLM, 2026-10-21)

TL;DR: on 200 real A-union blocks the WASM decoders are 3-4x faster than fzstd (0.10-0.14 vs 0.41 ms/block incl. UTF-8 decode) and Node native zstd is 3.7x, but none of the WASM options runs on Hermes (no WebAssembly), so for the RN bench app the only JS-thread-free path is a JSI/Nitro native module (react-native-zstd, not benchmarked here). The pure-JS asm.js build is slower than fzstd. Projected Pixel search p50 3.95 s -> 1.4-2.8 s serial, 1.1-1.7 s with Promise.all + BLOCKCACHE 64, only if a faster decoder can actually be loaded on the phone (unproven).

## Method
- Blocks: 200 zdata blobs sampled (seeded LCG 42, ~33 per pack) from the 6 A-union packs in shared-data/packs/persona-a-union (crypto, factbook, firstaid, medlineplus, visa, wikivoyage). Format (wikiPack.ts): table blocks(id, zdata), one whole-frame zstd per block, level 12, blockKb 64, no dictionary; articles slice [off, off+len) after decompress + UTF-8 decode. Sample: 4.79 MB compressed (mean 24.0 KB), mean 78.4 KB decompressed (max 189 KB).
- Script bench.mjs (one library per process, Node v25.9.0, MacBook M1 Pro): 1 warm call, then 5 repetitions over the 200 blocks; median/p90 pooled over 1000 samples per mode. "decompress" = decoder only; "+utf8" = plus TextDecoder.decode. Identity = sha256 of every output vs fzstd 0.1.1 (the version pinned in bench-app/package.json). extract.mjs builds the sample (blocks/ is gitignored).

## Results (ms/block, pooled median / p90)
| library (exact version) | decompress | decompress + utf8 | vs fzstd | identical to fzstd | size shipped | runs on Hermes (RN) without a native module |
|---|---|---|---|---|---|---|
| fzstd 0.1.1 (pure JS) | 0.386 / 0.505 | 0.410 / 0.571 | 1.0x | reference | 24 KB (esm) | yes (today) |
| @bokuweb/zstd-wasm 0.0.27 | 0.106 / 0.148 | 0.133 / 0.201 | 3.1x | 200/200 | 252 KB .wasm + 12 KB glue | no: needs WebAssembly |
| zstddec 0.2.0 (wasm, base64 in JS) | 0.090 / 0.113 | 0.098 / 0.136 | 4.2x | 200/200 only when given the exact output size (API needs it; pack format does not store it, the zstd frame header does) | 76 KB esm | no: needs WebAssembly |
| @oneidentity/zstd-js 1.0.3 wasm | 0.108 / 0.148 | 0.139 / 0.215 | 2.9x | 0/200: output truncated by 18 trailing bytes (prefix-equal 200/200), unusable | 261 KB cjs | no |
| @oneidentity/zstd-js 1.0.3 asm.js | 0.671 / 0.917 | 0.680 / 0.977 | 0.6x (slower) | 0/200 (same truncation) | 387 KB cjs | runs as plain JS, but slower than fzstd and wrong |
| node:zlib zstdDecompressSync (libzstd native, upper bound) | 0.090 / 0.122 | 0.110 / 0.161 | 3.7x | 200/200 | built in | n/a: stands for a native module |
- Raw: aggregates/bench-*.json (per-repetition medians included), ref-hashes.json, ref-lens.json.
- Hermes: WebAssembly is not available in Hermes (my knowledge, UNVERIFIED on the pinned RN version; check typeof WebAssembly on the Pixel build). So every WASM row is a desktop/browser/Node number only. On RN the realistic faster path is a JSI/Nitro native binding (web notes tick 20: react-native-zstd) which would also take the work off the JS thread when called async; on the app maintainer Kotlin app, zstd-jni on Dispatchers.IO.
- Desktop-vs-phone: phone 16.0 ms/block (PARTIME; includes SQL blob fetch + materialize) over MacBook fzstd 0.41 = 39x. The WASM/native ratio on an ARM phone core (Pixel 8a, Tensor G3) was not measured; ARM libzstd uses NEON-less scalar paths in WASM, so the 3-4x may shrink. Treat it as an upper bound.

## Projection: Pixel pack-search p50 (aunion73-a, PARTIME serial 3947 ms; 194 blocks/search; block phase 73.2 % = 2889 ms; Promise.all JS-bound bounds 2534-2892 ms, full-parallel floor 1063 ms)
Model: block phase scales by 1 - f(1 - lib/fzstd) where f = share of the 16 ms block that is decompress (unknown; f=1 optimistic, f=0.6 conservative; the rest is fetch/materialize); BLOCKCACHE 64 multiplies block count by 0.506. Promise.all = PARTIME bound minus the saved ms, floored at 1063. Aggregates: projection.json.
| decoder | f | serial | serial + BC64 | Promise.all | Promise.all + BC64 |
|---|---|---|---|---|---|
| fzstd (today) | - | 3947 | 2520 | 2534-2892 | 1107-1465 |
| @bokuweb wasm (3.1x) | 1.0 / 0.6 | 1994 / 2775 | 1532 / 1927 | 1063 / 1362-1720 | 1063 / 1063 |
| zstddec wasm (4.2x) | 1.0 / 0.6 | 1749 / 2628 | 1408 / 1853 | 1063 / 1215-1573 | 1063 / 1063 |
| native zstd bound (3.7x) | 1.0 / 0.6 | 1833 / 2679 | 1450 / 1878 | 1063 / 1266-1624 | 1063 / 1063 |
- Reading: BLOCKCACHE 64 + Promise.all already reaches 1.1-1.5 s with the fzstd we have; a faster decoder adds only ~0.0-0.4 s on top there. The decoder swap matters most for the serial path (3.95 -> 1.4-2.8 s) and for cache-cold first questions. Simple T_8GB p50 scaling (7.57 s minus saved search time) gives 4.7-5.1 s for Promise.all + BC64 +/- decoder; PARTIME per-row accounting is more careful (5.5-6.0 s for Promise.all alone), so use search p50 as the claim, not these totals.
- Next (device, 0 LLM): (1) on the Pixel, print typeof WebAssembly in the bench build; (2) micro-bench 194 blocks with fzstd vs a JSI native zstd to replace the 39x assumption; both are DEVICE-DAY items, nothing was run on the phone here.

UNKNOWN: Hermes WebAssembly status on the pinned RN; phone-side ratio for any decoder; f (decompress share of the 16 ms); react-native-zstd not installed or benchmarked (needs native build, out of scope).
