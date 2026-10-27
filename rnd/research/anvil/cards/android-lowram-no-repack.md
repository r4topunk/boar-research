# Stop the 4B's LMK kill on 8 GB Android: count repacked weights as anonymous memory, and load without repack on low-RAM phones
TL;DR: on r4to's moto g75 (8 GB, MemTotal 7.2 GiB, ~3.4 GB available before launch), BOAR + Qwen3-4B is **LMK-killed while loading** (RSS 5.03 / 4.74 GiB, reproduced 2×). The engine's fit rule called it a fit because `memoryFit.ts` counts only KV + compute as anonymous memory. llama.cpp's ARM **weight repack** copies the whole Q4_K model (~2.3 GiB) into anonymous memory on top of the mmap'd file. Two fixes, both config-level: (1) count repacked weights in the fit estimate, so the app never auto-picks a model that will be killed; (2) on low-RAM phones, load with llama.rn's existing **`no_extra_bufts: true`**, which keeps the weights file-backed and reclaimable. Anonymous memory goes from ~3.0 to ~0.8 GiB, at a speed cost to be measured.
Lane: Anvil · Status: ready-to-test (**Probe A done: root cause confirmed**, anon 3.25 → 0.88–0.91 GB, RSS 5.1–5.4 → 3.41 GB, decode unchanged; **Probe B run sheet** `../specs/probe-b-no-repack-g75.md`; Fix 1 = card `fit-estimate-repack`) · Priority: A
Axes moved:
- **stability ↑↑:** a crash on load becomes an answer.
- **resources ↓:** anonymous memory ≈ 3.0 → ≈ 0.8 GiB for the 4B.
- **latency ↓ (cost):** without repack, ARM uses the generic Q4_K kernels. Prefill is likely slower by roughly 1.5–2.5× and decode by less, since decode is memory-bound. UNKNOWN; measured by the probe below.
- quality ≈ (same weights; float accumulation order may differ slightly).
- safety: none.
Fits BOAR? Android only; the iPhone 13 already runs the 1.5B. llama.rn rc.4 already has the switch (`no_extra_bufts?: boolean`, "Disable extra buffer types for weight repacking", `node_modules/llama.rn/src/types.ts` ~132–136). No new model. Offline.

## Evidence

- **Device** (QUEUE.md 19:31; `boar-eval/runs/devices/2026-10-02/android/lmk-4b.log`):
  - moto g75 5G, SM6475, MemTotal 7,553,584 kB;
  - BOAR killed by lmkd as the **foreground** app while loading the 4B, twice (RSS 5.03 / 4.74 GiB; MemAvailable before launch 3.38 GB);
  - the engine used nCtx 4096 (`contextSizeForRam` > 6.5 GB) and labelled the 4B as fitting.
  - The 1.5B on the same phone: 72/72, no kill, RSS 2.6 GB.
- **What the fit rule assumes** (`src/inference/memoryFit.ts` @ upstream/main 0cfd4a77, header comment):
  - "Anonymous memory (KV cache, compute/scratch buffers, logits): must be resident … File-backed weights (the mmap'd tensors): clean page cache. The kernel can drop and re-read these pages";
  - `anonBytes` = KV + compute.
  - **That is false whenever llama.cpp repacks.** Repacked tensors are copied into a CPU_REPACK buffer, which is anonymous memory.
- **Measured repack residency** (Kiln exp-01 §5, clean probe `--cache-ram 0`, llama.cpp with repack on "the default, same as llama.rn"):
  - Qwen3-4B anonymous footprint **3.03 GiB ≈ 2.33 GiB weights + 0.56 GiB KV + ~0.15 GiB compute**;
  - peak RSS 4.60 GiB (anonymous plus the file pages read during repack).
  - This matches the g75 kill (RSS 4.7–5.0 GiB against ~3.4 GB available).
- **The kernels exist in the shipped library:** llama.rn rc.4's `librnllama_v8_2_dotprod_i8mm.so` contains repack GEMMs for q4_K / q6_K / q4_0 / q8_0 (cycle 3). So on any i8mm/dotprod phone (Snapdragon 6 Gen 3 = A78, dotprod), the Q4_K_M 4B is repacked.

## Fix 1: count repack in the fit estimate (engine, small)

- In `memoryFit.ts`: when the platform repacks (Android arm64 with dotprod/i8mm, `use_mmap: true`, `no_extra_bufts` not set), add the bytes of repackable tensor types to `anonBytes`. For a dense Q4_K_M model that is ≈ the file size minus the embeddings (Q4_K/Q6_K/Q4_0/Q8_0 are all repackable).
- Effect: on the g75 (≈ 3.4 GB available), the 4B's anonymous bytes are ≈ 3.0 GiB plus the app, so the verdict becomes `insufficient` / not auto-picked. The app falls back to the 1.5B, or to Fix 2, instead of crashing.
- The same correction applies to the iOS 8 GB routing note in QUEUE.md ("the same engine fit rule said the 4B fits").

## Fix 2: load without repack on low-RAM phones (config)

- `initLlama({ …, use_mmap: true, no_extra_bufts: true })` when total RAM ≤ ~8 GB, or when Fix 1's repack-inclusive estimate exceeds ~60% of available memory.
- The weights stay mmap'd (reclaimable). Anonymous memory ≈ KV 0.56 GiB at nCtx 4096 + compute ~0.15 + logits ≈ **0.8 GiB**.
- **Optional extra:** nCtx 4096 → 2048 on 8 GB phones. BOAR's answer prompts are ≤ ~700 tokens plus ≤ 512 answer tokens, so 2048 is enough, and it saves ~0.28 GiB of KV.
- **Cost:** the repacked i8mm GEMMs are what make ARM prefill fast. Without them, prefill falls back to the generic Q4_K dot products. The g75 4B is already predicted at 33–45 s total (`android-4b-latency-budget` §2b), so a slower prefill pushes it further.
  - Fix 2 makes the 4B **run** on 8 GB phones; it doesn't make it **fast**.
  - Whether the 4B or the 1.5B is the right default on 8 GB is then a quality-vs-latency call, with both numbers in hand.

## Test (cheap first)

- **Probe A (desktop, ~5 min, Mac mini b11010 build, no download):**
  - `llama-bench -m Qwen3-4B-Instruct-2507-Q4_K_M.gguf -p 512 -n 64 -t 4`, with and without the no-repack option. `--no-repack` is in recent llama-bench builds; confirm the exact flag with `--help` on b11010.
  - Record pp512 / tg64 and `/usr/bin/time -l` max RSS and footprint for both.
  - This gives the CPU speed ratio (an upper bound for the phone) and confirms the anonymous-memory drop.
- **Probe B (device, the g75, ~15 min):** the same dev client with `no_extra_bufts: true` for the 4B; P3a-style speed rows (unplugged, airplane), 10 answers.
- **Frozen criterion (stated before any run):**
  1. **0 LMK kills** over 2 cold launches plus 10 answers on the g75;
  2. peak RSS of the BOAR process ≤ 3.5 GiB during load;
  3. answers are produced, with route and sources 10/10 identical to the repack-on desktop trace for the same items;
  4. speed is **reported, not gated** (prefill and decode tok/s, first visible, total), next to the frozen g75 prediction. The device-default decision (4B vs 1.5B on 8 GB) is r4to's, made with these numbers.
  - Fix 1 has its own unit-test criterion: the fit verdict for (4B Q4_K_M, 7.2 GiB total, 3.4 GB available, repack on) is not `resident`.
- **Cost:** Probe A ~5 min; Probe B ~15 min of device time; Fix 1 ~1 h of engine work plus tests.

## What would make it fail

- lmkd also counts the file pages the process touches heavily (RSS includes them), and under pressure Android may still kill the foreground app. Then Fix 2 needs the smaller nCtx, or the 1.5B is the 8 GB default.
- The no-repack prefill is so slow on the A78 that the 4B is unusable (> 60 s total). Then the honest default for 8 GB is the 1.5B (12 tok/s, total p50 9.6 s on the g75, measured) and the 4B is opt-in.

UNKNOWN:
- the exact no-repack speed ratio on ARM phones;
- lmkd's accounting of file-backed RSS for a foreground app on Android 16;
- ~~whether llama.rn honours `no_extra_bufts`~~ **resolved:** `cpp/jsi/JSIParams.cpp:356` reads it into `cparams.no_extra_bufts`.
