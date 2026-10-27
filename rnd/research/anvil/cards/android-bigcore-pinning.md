# Pin llama.rn's threads to the big cores on Android (`cpu_mask` + `cpu_strict`)
TL;DR: BOAR runs 4 unpinned threads on Android, so the scheduler can put some of them on the slow Cortex-A510 cores, and every ggml barrier then waits for the slowest thread. Setting llama.rn's existing `cpu_mask` to the four A715 cores (with `cpu_strict`) should raise prefill and decode on the 12 GB tier. The gain size is UNKNOWN until a device bench.
Lane: Anvil · Status: evidence · Priority: B
Axes moved:
- **latency ↓**: TTFT and total time. Expected 0–25% on prefill/decode, from the paper below; no Dimensity number exists.
- **resources ≈**: same RAM. Thermal may be slightly higher, because the work stays on the hot cluster; the bench must record it.
- **stability ↑**: less run-to-run variance from thread migration (UNKNOWN).
- **quality / truthfulness / safety**: none. The output is the same at the same seed; only the speed changes.
Fits BOAR?
- Android only: iOS does not allow thread affinity.
- llama.rn rc.4 already exposes the knobs: `cpu_mask?: string` ("0-3" style) and `cpu_strict?: boolean` in `ContextParams` (`node_modules/llama.rn/src/types.ts:75-88`). They feed ggml threadpool params (`cpp/rn-llama.cpp` ~480-515).
- BOAR sets neither: `n_threads: 4` only, `LlamaEngine.ts` (0cfd4a77) lines 216 and 275.
- The big-core indices must be read on the device from `/sys/devices/system/cpu/cpu*/cpufreq/cpuinfo_max_freq`, not hard-coded. UNKNOWN whether the RN sandbox can read them; a native module or llama.rn's own device info may be needed.
- Offline: yes.
Evidence:
- **Phone study, many SoCs:** "In most cases, setting the number of threads equal to the number of big cores (prime and performance cores) can achieve the optimal performance." For decode, "adding more little cores typically leads to a decline in performance"; Kirin 9000E and Snapdragon 8+ Gen 1 peak with "four active big cores". On Snapdragon 8 Gen 3, all 8 cores were slower than the 6 big ones for prefill. Source: [Li et al., arXiv 2410.03613](https://arxiv.org/html/2410.03613v3), accessed 2026-10-01. Strength: moderate. It is a careful multi-device study with llama.cpp, but it varies thread **count**, not affinity, and none of its devices is a Dimensity 8300.
- **Topology of BOAR's Android test phone** (Xiaomi 2311DRK48G, Dimensity 8300): 1× Cortex-A715 @ 3.35 GHz + 3× A715 @ 3.2 GHz + **4× Cortex-A510 @ 2.2 GHz** ([MediaTek press release](https://www.prnewswire.com/news-releases/mediateks-new-dimensity-8300-chipset-redefines-premium-experiences-in-5g-smartphones-301992592.html), accessed 2026-10-01). So `n_threads: 4` already matches the big-core count. What it lacks is the guarantee that the 4 threads land on those cores.
- **llama.cpp's threadpool** carries `cpumask`, `strict_cpu`, `prio` and `poll` per pool. It was designed by Qualcomm engineers for exactly this case, with Snapdragon 8 Gen 3 / X-Elite reports ([PR #8672](https://github.com/ggml-org/llama.cpp/pull/8672), via search summary; numbers not re-read, UNKNOWN).
- **In-repo:**
  - `review/boar.md` #7 lists "detect big cores" as untested.
  - `review/research-pipeline/02-medicoes-existentes.md` §73 says "Still `n_threads: 4`".
  - Plumb's new iPhone grid (`wt/plumb-bench-uiios/scripts/bench-iphone.mjs`, commit 00747371, 2026-10-01) sweeps threads 2–6, ubatch, flash attention, KV type and Metal on **iOS only**. There is no Android grid and no `cpu_mask`.
Test in boar-eval:
- Device bench, not quality. Port Plumb's grid idea to Android: llama.rn `context.bench(pp=512, tg=64, pl=1, nr=3)`, model Qwen3-4B-2507 Q4_K_M (12 GB tier), thermal-gated, configs rotated per rep, ≥ 3 reps. Configs:
  - `base`: `n_threads: 4`, no mask;
  - `big4`: `n_threads: 4, cpu_mask: "<the 4 A715 ids>", cpu_strict: true`;
  - `big4-nostrict`: the same with `cpu_strict: false`;
  - `t3big`: the 3 non-prime A715 + prime;
  - `t6` and `t8`: no mask (to see whether the A510s help prefill on this SoC, as on Kirin).
- Then one boar-eval gate run (bench public 60, greedy) with the winning config, to confirm byte-identical answers and a TTFT drop end to end.
- **Success criterion (stated before any run):**
  - median pp512 **or** tg64 of `big4` ≥ **1.10×** `base`, with the other metric not below 0.97×;
  - thermal state no worse than `base` at the end of the rep;
  - end-to-end TTFT p50 on the gate run ≥ 10% lower with identical greedy answers.
  - Any config with ≥ 1.10× on both metrics wins outright.
Cost to try: ~2 h. A small Android bench harness (Plumb's iOS script is the template), 1 h of device time on the Dimensity 8300 phone (the app maintainer's; not in the lab, so the coordinator schedules it), no download. Risk: low and fully reversible (two init params).

## Thread count per SoC (cycle 18): pin to the big cores and use all of them

- BOAR hard-codes `n_threads: 4`.
  - Dimensity 8300: 4 big cores (fine).
  - Tensor G4: 1× X4 + 3× A720 = 4 (fine).
  - **Tensor G5 (Pixel 10): 1× X4 + 5× A725 = 6 big cores.** 4 threads leave a third of the compute unused for prefill.
  - Tensor G6: 1 + 6 C1 cores.
- So the arm should test **"n_threads = number of big cores, pinned"**, not just pinning at 4. Read the cores from `/sys/devices/system/cpu/cpu*/cpufreq/cpuinfo_max_freq`: the cluster(s) above the lowest frequency.
- See `android-4b-latency-budget` §3b for the SoC table and sources.

## What would make it fail

- The Android EAS scheduler may already keep 4 busy, high-utilization threads on the big cluster. Then `big4` ≈ `base`, and the card dies cheaply. That is a fine outcome.
- `cpu_strict` + `poll` spinning can heat the big cluster faster. A 10% gain that turns into throttling after 20 answers is a loss, so the bench must include a sustained run (Lantern's Q3-style 150-question thermal pass) before shipping.
- The likely judge phone is UNKNOWN (Pixel = Tensor with 1+4+4 or similar). Masks must be computed per device from cpufreq, never hard-coded.

## Considered and dropped this cycle

- **Quant format as a prefill lever on Android:** llama.rn rc.4's prebuilt `librnllama_v8_2_dotprod_i8mm.so` already contains ggml's ARM repack GEMMs for q4_0, q4_K, q5_K, q6_K and q8_0 (8×8 / 4×8 i8mm). It has no KleidiAI. Q4_K_M is already on the fast path.
- **GPU prefill + CPU decode on iOS (Metal op-offload):** llama.rn rc.4 keeps llama.cpp's `op_offload` on (`common.h:583`, `GGML_OP_OFFLOAD_MIN_BATCH` present). So with Metal allowed and `n_gpu_layers: 0`, prefill batches go to the GPU. The only iPhone 13 measurement of that setup (`review/IPHONE-TEST.md`, "Metal on for the embedder" arm, 707ac6d) was **worse on both**: TTFT 5.3 vs 4.0 s, decode 14.2 vs 22.7 tok/s. The full-GPU arm cut TTFT to 2.95 s but halved decode (12.3) and raised a critical memory warning. Plumb's `--metal` grid will re-measure it with the increased-memory-limit entitlement, which the 707ac6d build lacked. No card from me unless that grid shows pp512 ≥ 1.5× with tg ≥ 0.9×.

UNKNOWN:
- The CPU numbering on the Dimensity 8300 (usually 0–3 = A510, 4–7 = A715, but read it from sysfs).
- Whether the RN JS layer can read sysfs.
- PR #8672's exact numbers.

Shelf: row "llama-bench (llama.cpp) with -C/--cpu-mask" in `../../SHELF.md` (sweep affinity over adb before touching the app).
