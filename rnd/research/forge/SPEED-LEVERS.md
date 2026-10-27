# Quality-neutral speed levers for the 12 GB tier (spec; they become BOAR Bench flags)

TL;DR
- **Threads (`nThreads: "big"`):** llama.rn on Android **already pins** its threads to the fastest cores. `set_best_cores` sorts by `cpuinfo_max_freq` and sets a strict mask. The only lever left is the **count**, hard-coded to 4.
  - It pays only on SoCs with > 4 big cores: Pixel 10 / G5 has 6, Snapdragon 8 Gen 2/3 has 5–6, 8 Elite has 8. Prefill could gain up to ~1.3–1.5×; decode is ~0 (memory-bound).
  - Zero gain on the D8300, G4 and g75: their 4 big cores are already the ones used.
  - **Output-neutral:** greedy output is byte-identical at 2/4/6/8 threads (desktop, Qwen3-4B Q4_K_M, 2 prompts × 48 tokens).
- **Q4_0 instead of Q4_K_M:** **demoted.**
  - In llama.rn rc.4, Q4_K *and* Q6_K are repacked on ARM: i8mm 8×8, dotprod 8×4 (`ggml-cpu/repack.cpp`). The "Q4_0 has the best repack kernels" premise is outdated.
  - Expected gain is small: file 2.37 vs 2.50 GB → decode ≤ +5%; prefill ± ~10%, UNKNOWN.
  - It is **not** output-neutral (different weights).
  - Gate: device A/B in BOAR Bench first. Only if it shows ≥ +15%, run a quality parity check: KLD vs Q4_K_M on the 24-item EN slice prompts, then Kiln's judged L1.
- **Stream answer text, show sources/instant preview first:** the engine already emits `sources` → `instant` → `token` → `done` (`routing/events.ts`). The gap is the Android UI, which runs a legacy path (`UI-WIRING-NOTES.md`, PR phase).
  - For measurement: BOAR Bench records **time to sources, time to instant preview, time to first token, total** per item. That gives the perceived latency next to the raw one.

Lane: Forge · front #4 on BOUNTY-BOARD · Status: spec + desktop checks; device numbers come from BOAR Bench on the demo phone

## 1. Thread count

- **Evidence:**
  - `node_modules/llama.rn/cpp/jsi/JSIParams.cpp:34-60, 318, 616` (`#if __ANDROID__`): `target = min(n_threads, hw)`; cores sorted by max freq; `cpumask` = the top `target` cores; `strict_cpu = true`. With `n_threads` 4: D8300 → 4× A715, G4 → X4 + 3× A720, SD 6 Gen 3 → 4× A78. That is already all their big cores.
  - The engine sets `n_threads: opts?.nThreads ?? 4` (`src/inference/LlamaEngine.ts:227`).
- **Policy (pure function, unit-testable):**
  - Read every core's `cpuinfo_max_freq` and cluster the distinct values.
  - Drop the lowest cluster if there are ≥ 2 clusters **and** its freq < 0.8 × max.
  - `n_threads` = the remaining count, clamped to [2, 8].
  - Checks:

    | SoC | Clusters (GHz) | n_threads |
    |---|---|---|
    | g75 | 2.4×4 / 1.8×4 | 4 |
    | D8300 | 3.35/3.2×3 / 2.2×4 | 4 |
    | G4 | 3.1/2.6×3 / 1.92×4 | 4 |
    | G5 | 3.78/3.05×5 / 2.25×2 | 6 |
    | SD8G3 | 3.3/3.15×3/2.96×2 / 2.27×2 | 6 |
    | 8 Elite | 4.32×2 / 3.53×6 | 8 (0.82 > 0.8, nothing dropped) |

- **Open question:** on 8-big-core SoCs, does `n_threads = 8` starve the UI/JS thread? BOAR Bench measures `{4, big, big − 1}`.
- **Bench flag:** `nThreads: 4 | "big" | number`. The app reads `/sys/devices/system/cpu/cpu*/cpufreq/cpuinfo_max_freq` (its own Kotlin helper) and writes the core table into `device.json`.
- **Desktop parity (done):** `llama-completion --temp 0 -n 48 -t {2,4,6,8}` on 2 prompts → identical output hashes (`9b790731…` / `0f0fee7b…` for all 4 counts). Row-split matmuls give each output to one thread, so results don't depend on the count. UNKNOWN on the phone's i8mm kernels (same design; BOAR Bench verifies with a 2-item hash check per thread count).

## 2. Q4_0 vs Q4_K_M

- **Evidence:** `ggml_repack_get_optimal_repack_type` (`repack.cpp:4528+`):

  | Type | ARM repack (i8mm / dotprod) |
  |---|---|
  | Q4_0 | 4×8 / 4×4 |
  | **Q4_K** | **8×8 / 8×4** |
  | **Q6_K** | **8×8 / 8×4** |
  | IQ4_NL | 8×8 / 4×4 |

- **Prediction:** speed Δ within ±10% on prefill, ≤ +5% on decode; quality Δ < 0, size unknown.
- **No desktop run:** the M1 has no i8mm, so it would test a different kernel; and the MacBook disk is 99% full.
- **Bench flag:** `model: <file>` (already a request field).
- **Device A/B:** `bench()` pp512/tg64 × 3 + 10 answers each, ABAB.
- **Kill rule:** < +15% on (first-text p50, total p50) → stop.

## 3. Perceived latency (streaming, sources first)

- **Engine:** emits `sources` (after retrieval), `instant` (extractive preview), `token`, `done` (`routing/events.ts`).
  - iOS renders them as they arrive.
  - The Android legacy UI renders sources only at the end and re-renders the list on every token.
- **Bench fields per item:** `tSourcesMs`, `tInstantMs`, `tFirstTokenMs`, `totalMs`, plus the stage timers (`retrievalStages`).
- **Product decision for the PR phase:** "time to first visible text" = the instant preview when there is one. Anvil's §3 action 5; recorded here, decided by r4to.

## 4. Not here (quality-affecting, owned by Anvil's L1s)
- context k = 3, shorter answers, model choice.
