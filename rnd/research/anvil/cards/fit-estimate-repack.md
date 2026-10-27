# Fit estimate counts repacked weights and the load-time peak (memoryFit.ts patch)
TL;DR: `estimateMemoryFit` treats every weight as reclaimable mmap page cache, so it called Qwen3-4B "resident" on the 7.2 GiB moto g75, where lmkd killed it while loading. On CPU backends llama.cpp **repacks** Q4_K/Q4_0/Q6_K/Q8_0 weights into anonymous memory, and **during load** the file pages and the repacked copy are both resident. The patch adds both to the estimate and, when the repack peak doesn't fit but the no-repack estimate does, tells the engine to load with `no_extra_bufts: true` instead of crashing or refusing.
Lane: Anvil · Status: ready-to-test (engine patch + unit tests specified) · Priority: A
Axes moved:
- **stability ↑↑:** no load-time LMK kill from a wrong "fits".
- resources: honest auto-pick on 6–8 GB phones.
- latency: none, except on phones that switch to no-repack (see `android-lowram-no-repack`).
Fits BOAR? Pure TS in `src/inference/memoryFit.ts` (already a pure, unit-tested module: `memoryFit.test.ts`) plus ~6 lines in `LlamaEngine.load()`. Every platform with a CPU backend: Android, and iOS, where BOAR runs CPU-only.

## Evidence

- **g75 kill:**
  - RSS 4.74 / 5.03 GiB while loading the 4B; MemTotal 7.2 GiB; MemAvailable 3.38 GB before launch;
  - `lmk-4b.log`, QUEUE.md 19:31.
- **Probe A** (Kiln, mini, 2026-10-02): with repack, anonymous memory **3.25 GB** and RSS **5.1–5.4 GB**; without repack, **0.88–0.91 GB** and **3.41 GB**; decode unchanged.
- **exp-01 §5:** the 4B's anonymous footprint is 3.03 GiB ≈ 2.33 GiB weights + 0.56 KV + 0.15 compute.
- **What the module says today:** the `memoryFit.ts` header assumes "File-backed weights (the mmap'd tensors): clean page cache"; `anon = kv + compute` (`estimateMemoryFit`, ~line 200).
- **The budget** comes from `availableRamFrom`: max(total − max(25%, 2.5 GB), availMem). That is ≈ **4.7 GiB** on the g75.
  - The old estimate: anon 0.9 + file 2.33 ≤ 4.7 → `resident`.
  - Real load peak ≈ file pages 2.33 + repacked copy 2.33 + KV 0.56 + compute ≈ **5.4 GiB**.
- **Which types repack:** llama.rn rc.4's `librnllama_v8_2_dotprod_i8mm.so` exports repack GEMMs for `q4_0`, `q4_K`, `q5_K`, `q6_K`, `q8_0`, `mxfp4`, `iq4_nl` (cycle 3 `strings` dump). Ternary `tq*` and IQ2/IQ3 are not repacked (Maple's anonymous footprint was 0.50 GiB, exp-02).

## The patch (spec)

**`memoryFit.ts`:**

```ts
export interface FitInputs {
  …
  /** CPU backend repacks weights into anonymous buffers (llama.cpp CPU_REPACK): true unless loaded with no_extra_bufts. */
  repack?: boolean;
  /** general.file_type from the GGUF header (llama_ftype), to tell whether the weights are a repackable type. */
  fileType?: number;
}
export interface MemoryFit {
  …
  /** Bytes copied into anonymous repack buffers (0 without repack). */
  repackBytes: number;
  /** Load-time peak: file pages read while repacking + repacked copy + KV + compute. Equals anonBytes when repackBytes is 0. */
  loadPeakBytes: number;
}

/** llama_ftype values whose weights llama.cpp's CPU backend repacks on ARM (Q4_0, Q8_0, Q4_K_S/M, Q5_K_S/M, Q6_K, IQ4_NL). */
const REPACKABLE_FTYPES = new Set([2, 7, 14, 15, 16, 17, 18, 25]);   // verify against llama.h llama_ftype in rc.4

// in estimateMemoryFit:
const repackBytes = i.repack && i.fileType !== undefined && REPACKABLE_FTYPES.has(i.fileType)
  ? i.fileBytes * REPACK_FRACTION   // ≈ 0.97: everything but the input embedding lookup (get_rows) is repacked
  : 0;
const anon = kv + compute + repackBytes;
const loadPeak = repackBytes > 0 ? anon + i.fileBytes : anon;   // file pages are read in full while repacking
// verdict: a repacked model is resident in its anonymous copy, so its hot set is not the file:
if (loadPeak > avail) verdict = anon - repackBytes + /* no-repack */ 0 <= avail ? "repack-peak" : "insufficient";
else verdict = "resident";            // (non-repacked paths keep today's resident/streaming/thrashing logic)
```

- New `FitVerdict` member: **`"repack-peak"`**, meaning "loads only without repack".
- `describeFit` gets one line for it. The note should not tell the user to free RAM, because the engine handles it.
- `REPACKABLE_FTYPES` values must be checked against `llama.h` in rc.4. The numbers above are from memory of `llama_ftype` (2 Q4_0, 7 Q8_0, 14 Q4_K_S, 15 Q4_K_M, 16 Q5_K_S, 17 Q5_K_M, 18 Q6_K, 25 IQ4_NL). **UNKNOWN until checked.**

**`LlamaEngine.ts`:**

- `estimateFitAt` passes `repack: true` (the default load) and `fileType: Number(meta["general.file_type"])`.
- In `load()`:

  ```ts
  const noRepack = fit?.verdict === "repack-peak";
  if (noRepack) console.warn(`[engine] ${modelFilename}: repack peak ${toGb(fit.loadPeakBytes)}GB > budget; loading without repack`);
  … initWithCpuFallback(initLlama, { …, ...(noRepack ? { no_extra_bufts: true } : {}) }, …)
  ```

- `contextSizeForRam` is unchanged here. nCtx 2048 on ≤ 8 GB is a separate decision.

## Tests (`memoryFit.test.ts`, frozen expectations)

Shapes from the real headers: Qwen3-4B (36 layers, nEmbd 2560, 32 heads, 8 KV heads, head dim 128, vocab 151,936) and Qwen2.5-1.5B (28, 1536, 12, 2, 128). Q4_K_M = file_type 15.

| Case | Inputs | Expected |
|---|---|---|
| T1 | 4B Q4_K_M, file 2.50e9, nCtx 4096, total 7.2 GiB, available → budget 4.7 GiB (`availableRamFrom`), repack true | `verdict === "repack-peak"`; `loadPeakBytes > 4.7 GiB`; `repackBytes ≈ 0.97 × file` |
| T2 | same, repack false | `verdict === "resident"`; `anonBytes < 1.2 GiB` (Probe A: 0.88–0.91 GB) |
| T3 | 4B Q4_K_M on a 12 GB phone (total 11.6 GiB → budget 8.7 GiB), repack true | `"resident"` (loadPeak ≈ 5.4 GiB fits) |
| T4 | 1.5B Q4_K_M (file 0.99e9) on the g75, repack true | `"resident"` (loadPeak ≈ 2.4 GiB; the g75 measured RSS 2.6 GB, no kill) |
| T5 | ternary file_type (Maple-like) or an unknown file_type, repack true | `repackBytes === 0`; verdicts as today (no regression) |
| T6 | 4B on the iPhone 13 (4 GB, budget = availMem) | not `"resident"` (unchanged behaviour: too big) |

- Plus `LlamaEngine.test.ts`: when `estimateFitAt` returns `repack-peak`, the params passed to `initLlama` include `no_extra_bufts: true`. Mock `initLlama` and assert on its first argument.

## Test in the real world

- Probe B on the g75 (`specs/probe-b-no-repack-g75.md`) validates the no-repack load.
- This patch only decides **when** to use it. Its device check is the same as Probe B's criterion, run with the patch instead of the hard-coded flag: 0 LMK kills on the g75 4B, plus `[engine] … loading without repack` in the log.

## Status (2026-10-02 evening)

- **Implemented by Kiln:** `boar-eval/arms/fit-repack.patch`.
- **Scoped Android-only by the coordinator.** On iOS the estimate (budget 1.5–2.0 GiB) would flip the shipped iPhone 13 1.5B to no-repack, while there are no kills there today.
- **iOS evidence first:** `../specs/probe-ios-repack-iphone13.md`. Does iOS repack at all, and what does no-repack cost on the A15? Frozen reading inside.

## Cost and risk

- Cost: ~1–2 h for the patch and tests (Kiln/the app maintainer).
- Risk: low. It only changes behaviour where the estimate says the repack peak doesn't fit.
- Risk: `REPACK_FRACTION` and `REPACKABLE_FTYPES` are approximations. They are conservative: over-estimating anonymous memory means falling back to no-repack, which is slower but alive.

UNKNOWN:
- the exact `llama_ftype` numbers in rc.4 (to verify);
- whether the input embedding is repacked when it is tied to the output (Qwen3-4B ties). A fraction of 0.97 vs 1.0 changes nothing in the verdicts above.
