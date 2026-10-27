# Speed for the bounty: Forge arms in the ship candidate, end-to-end latency (12 GB tier: 4B and deep35), demo device

TL;DR
- **Ready to land:** `arms/ship/forge-ship.patch` (sha256 `cbca8efc…`) on the ship candidate (0cfd4a77 + `b6-on-health12final` 68f9868d).
  - It carries native zstd + the vector cache + P-8 sqlBatch + stage timers, **on by default**.
  - `EXPO_PUBLIC_BOAR_PERF=none` is a build-time kill switch.
  - Tree `wt/forge-ship` @ `ccc7688b`, local only.
  - vitest **1199/1199** in all 3 states (flags on, `=none`, arms-only); tsc clean.
  - **Not landed until 3 checks pass:** Kiln desktop identity on this tree, an Android build, and a ≥ 10-item device smoke. Native zstd has never executed on a phone: the g75 session never ran.
- **What the arms buy:** retrieval ≈ 1.2–1.8 s → ≈ 0.35–0.6 s on a Dimensity-8300/Tensor-class phone. That is **≈ −1 s per answer, ~4–5% of a 4B answer.**
  - Necessary, but not what decides "usable speed".
  - The 4B's prefill (~225 new tokens) and decode (~66 tokens) are ≈ 90% of the time.
- **4B fast tier, 12 GB phone, estimated** (p50, model loaded):
  - **first model text ≈ 8.5–12 s**, total ≈ **20–27 s**. Sources/instant preview show at ≈ 1–1.5 s.
  - Pixel 10 (G5): ≈ 7–10 s first text, total ≈ 18–24 s, if the threads land on its big cores.
- **Deep35 tier** (Qwen3.6-35B-A3B streamed, on demand): **first text ≈ 15–25 s, total ≈ 55–80 s** including a model swap. Usable only as an explicit "go deeper", never as the default.
- **Demo device: a 12 GB Pixel on GrapheneOS.**
  - **Pixel 10 (Tensor G5)** first choice; **Pixel 9 (G4)** second.
  - Verify the exact RAM before buying: the 16 GB Pro models exceed the bounty's 12 GB environment.
  - The bounty names GrapheneOS hardware, and the competing claim (a competitor team) demoed on a 12 GB Pixel 8 Pro.
  - Until we have one, the app maintainer's Dimensity 8300 12 GB phone (Xiaomi 2311DRK48G, already measured on 2026-09-24) is the measurement stand-in.

Lane: Forge · Status: patch ready, unverified on any device · 2026-10-03

## 1. What lands, and how

| Piece | In the patch | Default | Fallback / risk |
|---|---|---|---|
| Native zstd (`modules/boar-zstd`, vendored libzstd 1.5.7 decoder, 104 KB arm64 `.so`) | yes | on | **Android only** (`expo-module.config.json` platforms `["android"]`). The Swift side was never compiled. iOS keeps fzstd. Any refused block goes to fzstd. Byte-identical to fzstd on 15,070 blocks (desktop) |
| Vector cache (corpus vectors kept in JS) | yes | on | **New in the ship delta:** any error in the signature query falls back to the uncached scan. That also kept 9 unit tests with legacy DB mocks green. +~8 MB JS heap (f32) |
| P-8 sqlBatch (Sonar's prefetch) | yes | on | Same results on desktop (Kiln step 0: pack SQL calls 455.5 → 183 per question) |
| Stage timers (`receipt.retrievalStages`) | yes | always | A clock read per stage. Gives per-stage numbers from the first real device run |
| `DEVICE_EVAL_ON` polling in ui-android | yes | — | Release builds answer eval requests only with `EXPO_PUBLIC_DEVICE_EVAL=1` |
| **P-7b 16 KB packs** | **no** | — | It needs re-built pack files (an asset change, +18 MB). With native zstd, decompression waste costs ~ms, so P-7b is **dropped unless** the device shows `zstdMs` p50 > 300 ms with native zstd on (the PHONE-SESSION kill rule) |

- **Patches** (`arms/ship/`, SHA256SUMS):
  - `forge-ship.patch` = arms + ship defaults vs the ship candidate (27 files);
  - `forge-ship-defaults.delta.patch` = the 4-file delta on top of `forge-arms.patch`: defaults on, kill switch, signature fallback, Android-only module.
- **Merge note:** `forge-arms.patch` conflicts with the ship base only in `answer.ts` imports. Both blocks are kept.
- **Kill switch:** build with `EXPO_PUBLIC_BOAR_PERF=none` to get 0cfd4a77's retrieval code exactly. A list such as `nativeZstd,sqlBatch` enables exactly those. Device eval requests can still override per run (`"perf": {…}`).
- **Env read:** now `process.env.EXPO_PUBLIC_BOAR_PERF`, plain, like `deviceEvalGate.ts`. The old `typeof process` guard is gone; Expo's inline plugin handles both forms, checked in `babel-preset-expo/build/plugins/inline-env-vars.js`.

**Landing checklist** (owner → done when):
1. **Kiln, desktop identity** on `ccc7688b`, flags default vs `EXPO_PUBLIC_BOAR_PERF=none`, v0.1 72 items: sources incl. passage text, route and answer text **72/72 identical**, 0 errors, pack SQL calls ≈ 455 → 183. Same protocol as step 0 on 0cfd4a77.
2. **Kiln, Android release APK** of `ccc7688b` (recipe `rnd/kiln/recipes/forge-build.sh`): `libboarzstd.so` present in arm64-v8a, exporting only JNI + `boar_zstd_*`.
3. **Device smoke, any Android** (g75, the app maintainer's D8300 or the demo Pixel): 10 v0.1 items × 2 builds (default vs `=none`).
   - rows show `zstdModule: true` and perf all true;
   - `retrievedTitles` identical 10/10;
   - `zstdFallbacks` 0;
   - 0 crashes.
   - The `retrievalStages` give the first real per-stage numbers (replaces the estimates in §2).
   - ~15 min of device time.
4. Then it lands in the ship candidate. If step 3 can't happen before the freeze, ship with `EXPO_PUBLIC_BOAR_PERF=none` (today's code). **Never ship native code unrun on a phone.**

## 2. End-to-end latency, 12 GB Android tier (estimates, p50, model loaded)

Inputs:
- 4B rates = Anvil's frozen device model (`anvil/cards/android-4b-latency-budget.md` §2, Dimensity 8300, Qwen3-4B Q4_K_M): prefill **20–30 tok/s**, decode **4.4–6 tok/s**.
- Prompts: ~225 new tokens after the cached ~225-token prefix (p90 405); answers ~66 tokens.
- Retrieval: L0 Hermes replay (`README.md` §1: 677 ms JS on the M1 Pro), scaled ×1.5–2.1 to a D8300 (single-core JS), plus native SQL/bridge (UNKNOWN, ~0.1–0.4 s).
- **No 4B number exists from any phone with today's engine.**

| Stage | 4B, base | 4B, + Forge arms | How |
|---|---|---|---|
| route gate B6 (cached prefix, session swap) | 0.5–0.8 s | same | 13 new tokens at 20–30 tok/s + 2 `loadSession` (36 + 32 MiB). Anvil spec §3 (g75 0.8–1.4 s; D8300 faster) |
| emergency detector (mmBERT v3b, all tiers) | 0.01–0.03 s | same | `classifier-runtime.md` (g75 16–35 ms; D8300 ≈ 0.6×) |
| retrieval | **1.2–1.8 s** | **0.35–0.6 s** | zstd ≈ 0.85 s → ≈ 15 ms; vector cache −~50 ms + the 10.6 MB row transfer; P-8 −272 SQL calls |
| prefill of new tokens | 7.5–11 s (p90 13.5–20 s) | same | 225 / 20–30 |
| **first model text** | **9.5–13.5 s** | **8.5–12 s** | sources and instant preview at ≈ 1–1.5 s (`firstSourcesMs`) |
| decode, 66 tokens | 11–15 s | same | 66 / 4.4–6 |
| **total** | **21–28 s** | **20–27 s** | |

- **Pixel 9 (G4):** ≈ the D8300 (Geekbench multi ≈ 0.97×; LPDDR5X). Its X4 core is faster single-thread, so JS retrieval may be a bit quicker.
- **Pixel 10 (G5):** prefill up to ×1.3, **only if BOAR runs on its 6 big cores**. `n_threads: 4` is hard-coded, so ≈ ×1.1 today. Decode is ≈ the same (memory-bound). → first text ≈ 7–10 s, total ≈ 18–24 s.
- A secondary aggregator (promptquorum) claims 12–15 tok/s decode for a 3.8B on G5. That conflicts with our measured 4.0 tok/s for Phi-3.5 3.8B on the D8300 (older engine). Not used; UNKNOWN until measured.
- **Bigger levers than Forge's** (Anvil's ladder §3; all unmeasured on device):

  | Lever | Expected effect | Cost |
  |---|---|---|
  | context k = 4 → 3 | −5–7 s first text | −0.006 ratio |
  | threads = big cores | +0–25%; more on G5 | — |
  | Q4_0 repack | prefill +10–30% | — |
  | stream answer text as it decodes | perceived wait ≈ first text, not total | product |
  | shorter answers | — | quality trade |

  Stacked (Anvil): total ≈ −35–45% → ≈ 13–17 s.

### Deep35 tier (Qwen3.6-35B-A3B UD-Q2_K_XL streamed by BigMoeOnEdge; on demand)
- **Inputs:** a competitor team on a Pixel 8 Pro, same file (`deep-tier-streamed-moe.md` §3): prefill 24–30 tok/s, decode 4–6 (3.7–4.5 warm). Deep contract: 400 context / 200 answer tokens.
- **Memory forces a model swap:** the 4B (~3 GiB anonymous with repack) and bmoe (Linux peak 6.59 GiB, P0) do not both fit next to Android on a 12 GB phone.
  - Unload the 4B → start bmoe (dense 1.63 GiB + expert cache warm-up): **≈ 3–10 s, UNKNOWN**.
  - Reload the 4B lazily after.

| Stage | Time |
|---|---|
| swap to deep | 3–10 s (UNKNOWN) |
| retrieval (with arms) | 0.35–0.6 s |
| prefill 400 tokens | 13–17 s |
| **first deep text** | **≈ 17–27 s** |
| decode 200 tokens at 3.7–6 tok/s | 33–54 s |
| **total** | **≈ 55–80 s** (ADR projection 50 s without the swap) |

- **Reading:**
  - ~4–5× faster than the ~5 min the post author reported for a competitor team (Lantern `vitalik-thesis.md`);
  - still a "go deeper" button with a progress line, never the default path;
  - the D6 auto-pick floor (5 tok/s) will rarely admit it, so it needs an explicit user choice.
  - Thermal: 50 s of sustained decode throttles (3.7–4.5 warm).

## 3. Demo device

| Option | RAM | GrapheneOS | Expected 4B speed vs D8300 | Verdict |
|---|---|---|---|---|
| **Pixel 10 (Tensor G5)** | 12 GB (verify per model; **Pro = 16 GB, over the cap**) | yes (Pixel 6 → 10a supported, Sept 2026) | prefill ≤ 1.3× with big-core threads; decode ≈ | **first choice** |
| Pixel 9 (Tensor G4) | 12 GB (Pro 16 GB) | yes | ≈ 1.0× | second choice |
| Pixel 8 Pro (G3) | 12 GB | yes | slower (UNKNOWN); a competitor team's demo phone | same phone as the competitor's demo; fine for deep35 parity, weaker for the 4B |
| the app maintainer's Xiaomi 2311DRK48G (Dimensity 8300) | 12 GB (11.6 visible) | no | 1.0 (our reference) | **measurement stand-in now**, not the demo |
| moto g75 (8 GB) | 8 GB | no | ~0.6 | not a 12 GB tier device; deep35 won't fit |
| iPhone 13 | 4 GB | n/a | — | outside the Android bounty |

- **Why a Pixel:**
  - the requirement reads "Android and compatible GrapheneOS hardware";
  - a GrapheneOS demo with no Google Play Services proves two requirements in one video;
  - the competitor already demoed on a 12 GB Pixel.
- **Before the demo, on that phone** (one session, ~1 h):
  1. the device smoke of §1 (step 3);
  2. Anvil's E2-style latency run (P3a, 4B, streaming);
  3. the deep35 device criteria (ADR §7: TTFT ≤ 15 s, total ≤ 60 s, ≥ 4 tok/s sustained, 0 LMK in 10 answers);
  4. thermal log.

UNKNOWN:
- every phone number above (no 4B or deep35 run on a 12 GB phone with today's engine);
- the native SQL/bridge cost on Android (the phone session never ran);
- Tensor G4/G5 llama.cpp rates (no public primary source found, 2026-10-03);
- the deep swap time;
- Pixel 10 sustained thermals.

Sources (accessed 2026-10-03; secondary, not used for numbers):
- [promptquorum: Android local LLM apps 2026](https://www.promptquorum.com/power-local-llm/best-local-llm-apps-android-2026)
- [Notebookcheck: Tensor G5 CPU benchmarks](https://www.notebookcheck.net/Tensor-G5-Disappointing-CPU-performance-and-atrocious-GPU-numbers-in-Google-Pixel-10-Pro-XL-hands-on-benchmarks.1097374.0.html)
- [Geekbench: Pixel 10](https://browser.geekbench.com/android_devices/google-pixel-10)
