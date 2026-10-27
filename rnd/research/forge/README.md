# Forge: native performance for BOAR's retrieval path (L0, 2026-10-02)

TL;DR
- **Question:** would native code (Rust or other) make answers faster on the moto g75?
- **Answer:** yes, in one place: **zstd decompression**.
  - Under Hermes V1 (no JIT) it is **~76% of retrieval's JS work** (p50 499 ms per question on an M1 Pro).
  - libzstd does the same blocks in **6.7 ms (~75× less)**.
  - Expected saving on the g75: **≈ 1.2 s p50 / ≈ 2.6 s p90 of TTFT** in release JS, more in dev JS.
- **Second lever, pure JS:** the main-corpus semantic scan.
  - Every question pulls all **5,300 chunks (≈ 10.6 MB of bodies and float32 vectors)** across the bridge and cosines them in JS: ≈ 100 ms on the M1, ≈ 0.23 s on the g75.
  - Caching the vectors once in JS cuts the JS part 3× and removes the 10.6 MB transfer per question. The transfer's cost on the phone is UNKNOWN.
- **Not worth porting:** BM25, tokenize and scoring (≈ 0.12 s on the g75 for a ~1,000-line rewrite), compressContext (< 1 ms), and decode (already llama.cpp C++).
- **Rust:** no speed advantage over C here. The `zstd` crate is libzstd; pure-Rust `ruzstd` is 4× slower. It adds a heavy toolchain for a stranger's build, and uniffi-bindgen-react-native is still pre-release. **Route = vendored C decoder behind a JSI/Expo module.**

Lane: Forge (native performance; F2 latency) · Status: L0 done; the phone breakdown is the next step · Time box: ~2 h used

## 1. L0: retrieval stages under Hermes V1 (MacBook M1 Pro)

**Method** (`exp/l0-hermes/`):
1. **Record** (`record.mts`, Node):
   - Runs BOAR's real `retrieve()` at engine **0cfd4a77**, the g75 build, through the boar-eval desktop-node shims.
   - Kit: corpus-standard + corpus-full, plus boar-crypto `ae9fbd2c…` and boar-wikivoyage-en `ff8595e3…` (sha-checked = the device kit).
   - Workload: the **68 exact (query, k) retrieve calls** of the g75-matched desktop run (`boar-eval/runs/g75desk/g75desk-s42`), in device order, after one warm-up ask. Pack LRU caches carry over between questions, as in the app.
   - Logs every expo-sqlite call and its result, plus every query embedding (bge-small).
2. **Replay** (`replay/`, `build.sh`):
   - esbuild bundles the app's `retrieve.ts` and `compress.ts`, unchanged.
   - SQLite and the embedder are replaced by the recorded results.
   - fzstd 0.1.1 is real.
   - **TextDecoder is Expo's JS polyfill** (`expo/src/winter/TextDecoder.ts`): Hermes V1 has no TextDecoder (checked in the CLI and in the Hermes source), so the app uses Expo's polyfill on the phone.
   - Stage timers sit around each stage. `compressContext(query, raw, {tokenBudget: 320})` runs after retrieve.
3. **Fidelity:**
   - Under every engine, all 69 replays return the recorded raw and compressed chunk ids exactly.
   - 0 SQL calls go unrecorded.
   - ~479 SQL calls per question (P-8's ~476 baseline).
4. **Engines:**
   - **Hermes V1 CLI built from tag `hermes-v250829098.0.17`**: the exact Hermes the app's RN 0.86.3 ships (`HERMES_V1_VERSION_NAME`; V1 is the RN default). JIT off by default. No prebuilt V1 VM exists.
   - Two Hermes modes: `hermesc -O` bytecode (as a release APK ships), and `-lazy` from source (closest to dev/Metro).
   - Node 25 / V8, with and without JIT.
5. **Runs:** 3 interleaved reps of each config. Per question, each stage's **min** over reps. The MacBook was shared (load avg 9–46), and single runs varied ±40%.

**Stage table** (ms per retrieval, p50 / p90 / share of summed JS work; `exp/l0-hermes/out/table.txt`):

| Stage | Hermes V1 `-O` bytecode (release-like) | Hermes V1 lazy source (dev-like) | Node JIT, Expo TextDecoder | Node JIT, native TextDecoder | Node `--jitless` |
|---|---|---|---|---|---|
| zstd (fzstd) | **499 / 1084 / 76.3%** | 727 / 1485 / 74.3% | 37 / 73 / 61.4% | 36 / 79 / 74.1% | 756 / 1555 / 78.7% |
| utf8 (TextDecoder) | 32 / 93 / 5.1% | 59 / 132 / 5.9% | 9 / 26 / 16.1% | 1 / 3 / 2.0% | 2 / 4 / 0.2% |
| other JS in retrieve (tokenize, BM25 helpers, scoring, **corpus cosine scan**, fusion) | 146 / 178 / 18.5% | 216 / 266 / 19.7% | 13 / 22 / 22.2% | 11 / 16 / 23.6% | 222 / 246 / 21.1% |
| compressContext | ≤ 1 / 1 / 0.0% | ≤ 1 / 1 / 0.0% | 0.2 / 0.2 | 0.2 / 0.3 | 0.3 / 0.5 |
| **JS total** | **677 / 1333** | 999 / 1851 | 58 / 119 | 50 / 97 | 980 / 1789 |

- **Ratios:**
  - Hermes `-O` vs V8 JIT: **13.6×** on the total (zstd 14×, other JS 10.7×).
  - Dev-like lazy source vs `-O` bytecode: **1.4×**. This is a *lower bound* on dev-mode inflation: Metro dev bundles add `__DEV__` paths, the inspector and LogBox.
- **Inside "other JS"** (Hermes sampling profile, `out/prof.cpuprofile`): the main-corpus brute-force scan (`semanticSearch`'s `rows.map(cosineSimilarity)`) is **~60% of the bucket**, about 11% of all samples. That's ≈ 97 ms on the M1 in the isolated bench (`exp/cosine-bench/`). The pack-search logic is the remaining ≈ 50 ms.
- **Per question** (p50):
  - 68 zstd blocks decompressed: 5.7 MB out, of which only **1.6 MB** is article text actually decoded. That's 3.5× decompression waste, P-7b's target.
  - 479 SQL calls.
  - One `getAllAsync` returning **5,300 corpus rows**: bodies average 470 chars, plus a 1,536-byte float32 vector each, ≈ 10.6 MB.

**Scaled to the g75:**
- **Single-core ratio:** M1 Pro ≈ 2,400 vs Snapdragon 6 Gen 3 ≈ 1,015 (Geekbench 6) → **×2.4**, with a range of ×2.0–3.0. Interpreters are memory- and branch-bound, so the true ratio may be worse. The loaded Mac pushes the other way.
- **Release-mode JS estimate:** **≈ 1.6 s p50** (1.35–2.0 s), of which zstd ≈ 1.2 s.
- **Dev mode:** ≥ ×1.4 → **≥ 2.3 s**.
- **Against the device measurement:** the g75 measured 3.2–3.4 s in dev JS, so JS plausibly explains **~70–85%** of it. The remaining ~0.5–1 s would be native SQL plus bridge (479 async calls + the 10.6 MB scan) plus the bge-small embedding. That split is UNKNOWN until the phone measures it (§4).

## 2. Native ceiling (zstd, same blocks)

**Setup** (`exp/zstd-bench/results.txt`):
- The exact 5,565 decompressions the app did over the 68 questions: 1,878 unique 64 KB-class blocks, 57 MB compressed.
- Per question, best of 5. M1 Pro.

| Decoder | p50 / p90 ms per question | vs libzstd |
|---|---|---|
| C libzstd 1.5.7 (`ZSTD_decompressDCtx`) | **6.7 / 15.3** | 1× |
| Rust `zstd` 0.13 crate (libzstd bindings) | 5.3 / 11.1 | ≈ 1× (same C code) |
| Rust `ruzstd` 0.8 (pure Rust) | 21.7 / 44.7 | ~4× slower |
| fzstd, V8 JIT | 39 / 83 | 5.7× |
| **fzstd, Hermes V1 `-O`** (what the phone runs) | **554 / 1189** | **~80×** |
| fzstd, V8 `--jitless` | 816 / 1753 | 118× |

- **Ceiling:** native zstd turns ~0.5 s (M1) / **~1.2 s (g75)** per question into **~7 ms / ~16 ms**. Decompression drops out of the latency budget.
- **The other stages:**
  - Corpus cosine scan, cached in JS (Float32Array matrix + precomputed norms): 97 → 33 ms under Hermes. Native NEON would be < 1 ms.
  - utf8 (32 ms) is the last native-able piece.

## 3. Ranked "port X" candidates (g75, release JS, ×2.4 scaling)

| # | Change | What it is | Expected saving on the g75 (p50 / p90) | Integration cost | Build burden for a stranger | Verdict |
|---|---|---|---|---|---|---|
| 1 | **zstd → native** | Vendored zstd **decoder-only** C source (upstream single-file `zstddeclib.c`) behind a sync JSI function: `decompress(ArrayBuffer) → ArrayBuffer`. Built as a local Expo module (C++ via JSI) or a pure-C++ Turbo Module; Nitro is an alternative. Replaces `fzstd` in `packs.ts` (one import). | **≈ −1.2 s / −2.6 s**; TTFT 6.5 → ~5.3 s. With P-7b packs already shipped: ≈ −0.6 s more, and P-7b's +18 MB becomes optional. | 1–2 days, plus device tests on Android and iOS | **Low:** NDK + CMake + Xcode are already required by RN New Arch. No cargo or extra SDK. +O(100–300 KB)/ABI (UNKNOWN exact) | **GO** (biggest lever) |
| 2 | **Corpus semantic scan: cache vectors in JS** (not native) | Load `chunk_embeddings` once into one Float32Array (or int8) matrix with norms; invalidate on corpus or collection change. Score per question, then fetch bodies only for the top-k ids. | ≈ −0.15 s JS, **plus the 10.6 MB/question row materialization in expo-sqlite (UNKNOWN; plausibly ≥ 0.1–0.5 s)** | ½ day, `retrieve.ts` only; RAM +8 MB (f32) / +2 MB (int8) | None | **GO** (cheap, no native) |
| 3 | **SQL bridge calls** | P-8 (batching, queued: 476 → 190 calls), then the remaining pack-search calls on expo-sqlite's **`*Sync`** APIs (`getFirstSync`/`getAllSync`/`prepareSync`, already in expo-sqlite 57). op-sqlite only if Sync is still slow. | 286 fewer calls × per-call cost (UNKNOWN; the P-8 phone pair measures it). At 1–3 ms/call: −0.3 to −0.85 s | P-8 is ready; Sync is ~½ day | None (op-sqlite would add a 115 MB npm tarball) | GO via P-8 first; Sync after the P-8 number |
| 4 | utf8 decode in native | The same module as #1: `decompressSlices(zdata, [[off, len]…]) → string[]`, so Expo's JS TextDecoder is skipped | ≈ −0.08 s / −0.2 s | +½ day on top of #1 | Same as #1 | Add-on to #1 only |
| 5 | Native dot product for the corpus scan | The same module: `topK(matrix, query, k)` | ≈ −0.08 s after #2 | +½ day on top of #1 + #2 | Same as #1 | Optional |
| ✗ | Port tokenize / BM25 helpers / scoring (`wikiPack.ts`, `pure.ts`) | Rust/C++ rewrite of ~1,400 lines | ≈ −0.12 s | Weeks; logic would be duplicated and the eval parity lost | — | **KILL** |
| ✗ | compressContext | — | < 1 ms | — | — | **KILL** |
| ✗ | Rust route (uniffi-bindgen-react-native) | Rust → Turbo Module/JSI | No gain over C for zstd: the `zstd` crate *is* libzstd, and `ruzstd` is 4× slower | Pre-release 0.31.0-x ("not yet for production") | rustup with 7 targets + cargo-ndk + NDK + Xcode, or committed prebuilt binaries (a reproducibility smell) | **KILL** for this bounty |
| ✗ | Decode / prefill | Already llama.cpp C++ | 0 | — | — | n/a |

- **Cumulative, if #1–#3 land:** retrieval JS ≈ 1.6 s → **≈ 0.25–0.35 s** on the g75 in release (pack logic ≈ 0.12 s + scan ≈ 0.08 s + utf8 ≈ 0.08 s), plus whatever native SQL and embedding remain.
- **Integration routes:** from the web survey, sources in §6.
  - **Hand-written C++ JSI / pure-C++ Turbo Module** shipped as a local autolinked library. create-react-native-library has a C++ template. Sync by default, no new toolchain.
  - **Expo Modules (Kotlin/Swift):** native-owned ArrayBuffer in SDK 57. JNI to C is fine on Android, while iOS would need a C bridge in Swift. Sync `Function` ≈ 0.5 µs/call on iOS (Expo's benchmark).
  - **Nitro Modules:** zero-copy ArrayBuffer and the fastest calls, but adds react-native-nitro-modules (NDK ≥ 27, Xcode ≥ 16.4).
  - **react-native-zstd (Nitro):** exists, but `decompress` returns a **UTF-8 string of the whole block**. BOAR slices blocks by **byte** offsets, so it can't be used as-is.
  - **sqlite-zstd (Rust SQLite extension):** has no Android or iOS builds. KILL.

## 4. What the next phone session must measure (g75, same packs, 1.5B, airplane, 2 reps)

1. **Release-mode JS** (needs main's ui-android to poll with `DEVICE_EVAL_ON`, a one-line change that is the app maintainer's call).
   - If release isn't possible, run dev and release builds back to back on 10 items to get the **real dev/release ratio** (L0 lower bound: 1.4×).
2. **Stage timers inside `retrieve`**, logged per item (a small instrumentation patch, ready to write on request):
   - `zstd` ms and blocks;
   - `utf8` ms;
   - the corpus `getAllAsync` wall ms (5,300 rows) and its cosine ms;
   - the summed wall ms of the other SQL awaits and their call count;
   - `embed` ms;
   - the rest of the JS.
   - This gives the real native SQL/bridge share (UNKNOWN here) and the true M1→g75 Hermes ratio.
3. **In-app fzstd microbench:** the same 60 blocks (`sonar/exp/23` zbench set), MB/s on the g75. One number that calibrates the ×2.4 scaling.
4. **The P-7b and P-8 arms as already ordered:** base → P-7b → P-7b+P-8. P-8's Δ ÷ 286 calls gives the per-call async cost, which decides candidate #3 (Sync APIs).
5. **Kill rule for #1:**
   - Stop if the measured g75 zstd stage (release, P-7b packs) is **< 300 ms p50**: native would then save < 0.3 s.
   - Otherwise build the native module as an arm: criterion retrieval p50 ≤ 0.6× base, with byte-identical sources (the same pre-check as P-7b).

## 5. Caveats and UNKNOWN

- UNKNOWN: the native SQL/bridge cost on the g75: the async per-call cost, and the cost of materializing 5,300 rows (10.6 MB) per question. Excluded from the replay by design.
- UNKNOWN: the M1 Pro → g75 Hermes ratio. ×2.4 comes from Geekbench single-core; the interpreter ratio may differ, which is why item 3 of §4 calibrates it.
- UNKNOWN: the dev-mode overhead beyond the compile mode (1.4× is a floor).
- The replay bundle is built with esbuild (target es2020); Metro's Babel transforms differ slightly. The effect on interpreter speed is expected to be small, not measured.
- Recording used `Platform.OS = "node"` (the adapter default). Retrieval has no platform branch on this path, but this was not proven.
- compressContext used budget 320 (`context:452->320` on the device), not each item's exact budget. It's < 1 ms either way.
- Hermes CLI timing is `Date.now()` (ms ticks): fine for stage sums, coarse for sub-ms stages.

## 6. Arms built for the phone session (2026-10-02 night; run sheet: `PHONE-SESSION.md`)

- **`arms/forge-arms.patch`** (vs 0cfd4a77, sha256 `914086dcfdedb1ef…a107f`; Kiln builds D and R from it):
  - **`modules/boar-zstd`:** local Expo module, vendored **libzstd 1.5.7 decoder** (upstream single-file amalgamation, BSD; `cpp/vendor/README.md`).
    - Kotlin → JNI and Swift → C, sync `decompress(Uint8Array) → ArrayBuffer`, zero-copy in and out.
    - Throws `E_ZSTD` on anything that isn't one frame with a recorded size; JS then uses fzstd.
    - 104 KB arm64 `.so`, exports only the JNI and `boar_zstd_*` symbols.
    - No package.json or lockfile change: autolinking scans `./modules`.
  - **`src/rag/perfFlags.ts`:** `nativeZstd`, `vectorCache`, `sqlBatch`, **all off by default**. Set at build time with `EXPO_PUBLIC_BOAR_PERF` (also read under Node), or per device eval request (`"perf": {…}`, restored after the run).
  - **`sqlBatch`** = Sonar's P-8 patch (75751ea5), applied verbatim, then gated at its 2 prefetch call sites.
  - **`vectorCache`:**
    - corpus rows and squared norms are kept in JS, keyed by a one-query signature (count + rowid sums over the same join and filter);
    - scores are the same doubles as `cosineSimilarity`;
    - on the cached path, only rows ≥ 0.55 are sorted (stable), so the order is identical.
  - **`receipt.retrievalStages`:** zstd/utf8/SQL/corpus/embed/branch timings plus the flags in effect, in every device row.
  - **Device eval polls on `DEVICE_EVAL_ON`**, not only `__DEV__`, so a release-JS build made with `EXPO_PUBLIC_DEVICE_EVAL=1` answers requests.
- **`arms/forge-eval-history.patch`** (v2, JS only, sha `d12c5779…`): device eval questions may carry `history`, needed by the gate probe's multi-turn items. It runs on D through Metro; no rebuild.
- **Local checks** (MacBook):
  - tsc clean; vitest **1172/1172** (1164 base + 8 new);
  - **native decoder vs fzstd byte-identical on every block** of the g75 kit and the P-7b 16 KB packs: 15,070 blocks, 0 refused (`arms/identity/identity.txt`), plus 9/9 fallback cases.
- **Arm tree replayed under Hermes V1** (`exp/l0-hermes/build-arm.sh`, `out/table-arm.txt`, 3 reps):
  - flags off and `vectorCache` both return the recorded raw and compressed sources **69/69**;
  - `vectorCache` saves **30 ms/question** of Hermes JS on the M1 (≈ 70 ms on the g75), plus the bridge transfer the phone measures.
  - Less than the isolated bench's 66 ms: the in-app scan was cheaper than its profile share suggested.
- **Native zstd under Hermes:** not replayable in the CLI. The ceiling is the §2 microbench.
- **Desktop step 0 and the APKs:** Kiln (identity 72/72 flags off and on, with SQL call counts proving the flags arrived).

## 7. Files and reproduce

```fish
cd rnd/research/forge/exp/l0-hermes
mkdir -p app; git -C ../../../../../boar-app archive 0cfd4a77 src assets modules package.json tsconfig.json | tar -x -C app
ln -s (realpath ../../../../../boar-app/node_modules) app/node_modules
../../../../../boar-eval/adapters/desktop-node/node_modules/.bin/tsx record.mts   # ~3.5 min, writes rec/rec.json (108 MB, gitignored)
./build.sh && ./reps.sh && python3 table.py                                       # Hermes: build ~/src/hermes-v1 from tag hermes-v250829098.0.17 (cmake -G Ninja, ninja hermes hermesc, ~10 min)
```

- `exp/l0-hermes/`: recorder, replay shims, `out/` (per-rep JSON, `table.txt`, Hermes `prof.cpuprofile`).
- `exp/zstd-bench/`: `dump_blobs.py`, `bench_c.c`, `rs/` (Rust), `bench_js_body.js`, `results.txt`.
- `exp/cosine-bench/`: `bench.js`, `results.txt`.
- Survey sources:
  - uniffi-bindgen-react-native [docs](https://jhugman.github.io/uniffi-bindgen-react-native/), [pre-install](https://github.com/jhugman/uniffi-bindgen-react-native/blob/main/docs/src/guides/rn/pre-installation.md)
  - [RN pure C++ modules](https://reactnative.dev/docs/the-new-architecture/pure-cxx-modules)
  - [Expo Modules 2.0 benchmark](https://expo.dev/blog/an-early-look-at-expo-modules-2-0)
  - [NitroBenchmarks](https://github.com/mrousavy/NitroBenchmarks), [Nitro array buffers](https://github.com/mrousavy/nitro/blob/main/docs/docs/types/array-buffers.md)
  - [op-sqlite API](https://github.com/OP-Engineering/op-sqlite/blob/main/docs/docs/api.md)
  - [expo-sqlite v57](https://docs.expo.dev/versions/v57.0.0/sdk/sqlite.md)
  - [react-native-zstd](https://www.npmjs.com/package/react-native-zstd)
  - [sqlite-zstd releases](https://github.com/phiresky/sqlite-zstd/releases)
  - [RN 0.82 / Hermes V1](https://reactnative.dev/blog/2025/10/08/react-native-0.82)
  - Geekbench 6: [Snapdragon 6 Gen 3 (nanoreview, moto g75)](https://nanoreview.net/en/benchmark-ranking/motorola-moto-g75), [M1 Pro (browser.geekbench.com)](https://browser.geekbench.com/v6/cpu/507119)
