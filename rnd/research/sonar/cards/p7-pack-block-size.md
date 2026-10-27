# P-7: rebuild the format-2 packs with 8 KB zstd blocks, so retrieval stops spending ~1.5 s in pure-JS decompression on Android
TL;DR: On r4to's moto g75 (Android 16, 8 GB), retrieval alone takes **3.1–3.3 s p50**, which is 42–45% of the 1.5B's 7.0–7.5 s time-to-first-token (TTFT); the iPhone takes 1.3 s and desktop 0.2 s. The pack search checks BM25 candidates for relevance by fully decompressing each candidate's 64 KB zstd block, ≈ 60 blocks / 4.8 MB per question, with **`fzstd` (pure JS)**. With the JIT off (a proxy for Hermes, which has none), that alone costs **≈ 0.6 s on an M1**, so several times more on the phone's slower cores. Rebuilding the packs with **8 KB blocks** cuts the JS decompression **4.3×** for **+2% pack size** and **byte-identical** retrieval results. No engine code change.
Lane: Sonar (retrieval latency; F2 latency front) · Status: **STOPPED: pre-check 0 PASS (72/72 byte-identical), criterion 3 FAIL** (+9.83% / +9.49% vs ≤ +5%; Kiln, `boar-eval/adapters/desktop-node/arms/p7-blk8.README.md`). Superseded by `p7b-pack-block-16k`. Also: my 4.3× estimate assumed 8 KB *raw* blocks; the builder flushes after the article that crosses the bar, so its "8 KB" blocks average ~19 KB raw (real-read reduction −62%, not −77%) · Priority: A
Axes moved:
- latency ↓ on both phones: retrieval −1 to −2 s on the moto (estimate; UNKNOWN factor M1-jitless → Snapdragon 6 Gen 3 Hermes, measured by the run itself), less on the iPhone;
- quality and safety unchanged by construction (same article text, same offsets after rebuild, same ranking code);
- storage +~2% (+~8 MB on the 351 MB Wikivoyage pack).
Fits BOAR? `scripts/build-wiki-pack.mjs` already takes `blockKb` (pack meta `params`: `"blockKb":64,"zlevel":12`). Rebuild `boar-wikivoyage-en` and `boar-crypto` with `blockKb: 8`. The reader (`WikiPack.article`: block → `off`/`len` slice) is unchanged. Pack sha changes → kit/manifest update.

Evidence (`exp/23-device-retrieval-profile/`):
- **Device timings** (Plumb's moto g75 P1, `boar-eval/runs/devices/2026-10-02/and-q15-r{1,2}.traces.jsonl`, 1.5B, airplane mode, 72 items × 2):

  | | moto r1 | moto r2 | iPhone r1 |
  |---|---|---|---|
  | retrieval p50 (answered items) | 3265 ms | 3088 ms | 1289 ms |
  | TTFT p50 | 7451 ms | 7048 ms | 4735 ms |
  | retrieval share of TTFT | 0.45 | 0.42 | 0.28 |
  | prefill | 310 tok @ 63 tok/s | 310 @ 65 | 311 @ 72 |

  - Desktop (`and-qwen-s44`): retrieval p50 203 ms. The moto is ~16× slower.
- **Where pack search spends its work** (`prof.txt`, `prof2.txt`, `p7.txt`; engine @0cfd4a77 copy, 60 public questions, cold caches, `fzstd`, V8 with JIT):
  - per question: ~445 SQL calls and **~61 block decompressions = 4.9 MB p50** (11.4 MB p90);
  - decompression is 42% of pack-search time even with the JIT on;
  - the reads come from `searchDetailed` → `materialize` (11,374 of 11,414 cold `article()` reads), the BM25 relevance loop.
- **Interpreter cost** (`zbench.mjs`): 60 real blocks (4.8 MB) take `fzstd` 40 ms with the JIT, **609 ms without** (`node --jitless`, 7.9 MB/s), and native zstd 8–10 ms.
- **Block-size trade-off** (`blocksize.mjs`; 120 real blocks of article text re-packed at zstd level 12, 60 article reads):

  | blockKb | compressed / raw text | bytes decompressed | fzstd, JIT | fzstd, JIT off |
  |---|---|---|---|---|
  | 64 (now) | 0.398 | 3.36 MB | 38 ms | 442 ms |
  | 32 | 0.413 | 1.71 MB | 13 ms | 251 ms |
  | 16 | 0.422 | 0.97 MB | 11 ms | 138 ms |
  | **8** | **0.428** | **0.73 MB** | 7 ms | **104 ms** |

  - Text blocks are 109 MB of the 351 MB file (3531 × 30.8 KB), so +7.5% on text is ≈ +2.3% on the file.
- **Alternatives considered:**
  - native zstd: `react-native-zstd` (MIT, Nitro/JSI) returns a **string**, not bytes, and `WikiPack` slices by byte offset, so it isn't drop-in. It also adds a native dependency. Kept as plan B.
  - skipping title lookups for sources a pack has no articles from: identical results on 178/178 lists, but only −10% SQL calls. Small; noted for Kiln.

Frozen criterion (arm `p7-blk8` = packs rebuilt with `blockKb: 8`, same sources and dump, vs the current packs; engine 0cfd4a77; moto g75, 1.5B, airplane mode, same protocol as Plumb's P1):
0. Desktop pre-check (no device): for all 72 v0.1 items, the `-kic` traces' pre-answer sources (titles, sections and passage text) are **byte-identical** to base. Any difference → stop: the rebuild isn't equivalent.
1. **Moto retrieval p50 ≤ 0.6× base** (base = P1 r1/r2: 3.1–3.3 s), on answered items, 2 reps.
2. TTFT p50 reported (expected −1 to −2 s); 0 BOAR kills; 0 errors.
3. Pack file size ≤ +5% per pack.
- Fail 1 with 0 passing → plan B (a native byte-returning zstd), and the measured residual tells how much retrieval time is SQL bridge calls instead.

Cost to try: pack rebuild on the mini (Wikivoyage ~35k articles + crypto; no new download) + desktop pre-check + one 2-rep device run (~30 min). Risk: none to quality by construction (pre-check 0 enforces it).
