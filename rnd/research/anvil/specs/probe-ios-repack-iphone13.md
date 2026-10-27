# iPhone 13 probe: does the 1.5B repack on iOS, and what does no-repack cost? (run-ready, frozen 2026-10-02)

Why: Kiln's Fix 1 patch (`boar-eval/arms/fit-repack.patch`, from card `fit-estimate-repack`) would flip the shipped iPhone 13 + Qwen2.5-1.5B to `no_extra_bufts: true`. The estimate's iOS budget is ~1.5–2.0 GiB, and the 1.5B's repack load peak is ≈ file 0.92 GiB + copy 0.9 + KV/compute ≈ 2.0 GiB. Yet the iPhone has **no kills today**. The coordinator scoped Fix 1 to Android until this probe. Two questions:
- **(Q1)** Does llama.rn's iOS build actually repack the 1.5B on the A15? If not, Fix 1's repack term is wrong for iOS.
- **(Q2)** If it does, what does no-repack cost or gain?
  - On macOS, Probe A found prefill *faster* without repack (Accelerate). iOS also links Accelerate, so it may do the same.
  - The earlier "1 GB thrash ceiling" (`review/IPHONE-MODEL-AB-rc6.md`) may interact with where the weights live.

## Setup (iPhone 13, 4 GB, Metal off as shipped; unplugged, airplane, thermal "nominal" before each run)

**Part 1: bench (no answer pipeline).** Plumb's `scripts/bench-iphone.mjs` grid (`wt/plumb-bench-uiios`, commit 00747371) already sends llama.rn init params into the app and runs `bench()` with thermal gating. Add one config:

```js
{ ...BASE, id: "norepack", no_extra_bufts: true },   // BASE = { n_ctx: 2048, n_threads: 4, n_gpu_layers: 0 }
```

- Run `--only base,norepack --reps 3 --pp 512 --tg 64` on the 1.5B.
- Record pp512 and tg64 tok/s, plus the app's memory telemetry around each run:
  - `[BOAR mem] footprint_mb` (ram-monitor), which iOS jetsam counts;
  - peak during load if it is logged.

**Part 2: 10 real answers.** The same one-line JS change as Android Probe B (`specs/probe-b-no-repack-g75.md` §1), with the platform condition set to `"ios"`.
- Run the P3a speed items through `scripts/eval-iphone.mjs`: 10 answers with repack (stock) and 10 without (patched), in ABBA order, cool-down between blocks.
- Verify the `[engine] PROBE-B no_extra_bufts=true` log line before the patched block.
- Then revert the tree.

## Frozen reading (stated before any run)

**Q1, does iOS repack?** Compare the footprint after load, base vs norepack.
- **Repack is active** if the base footprint is ≥ 0.5 GiB higher (the 1.5B's weights ≈ 0.9 GiB). Fix 1's repack term then holds on iOS.
- If the difference is **< 0.2 GiB**, iOS does not repack this model. Fix 1 must set `repack: false` on iOS, and stays scoped as the coordinator did.

**Q2, which default for the iPhone 13** (only if Q1 says repack is active)? Adopt no-repack on iOS (let Fix 1 flip it) only if all hold:
1. **0 jetsam kills** across both blocks (load markers / CR-2, no unexpected restarts);
2. pp512 no-repack ≥ **0.9×** base, and tg64 ≥ **0.9×** base (bench, median of 3);
3. answers: first visible text p50 and total p50 no worse than **1.1×** base, and route/sources 10/10 identical to the stock block.

- If 2 or 3 fails while repack is active, keep the 1.5B on repack. Fix 1 then needs an iOS exception sized from the measured footprint, not from the estimate's 1.5–2.0 GiB budget.
- **Reported, not gated:** whether no-repack changes behaviour near the old ~1.2 GB "thrash ceiling". A note for the stopped iPhone-tier work, in case it reopens.

**Cost:** ~20 min bench plus ~25 min answers on the device. No download (the 1.5B is installed). No native rebuild: `no_extra_bufts` is read by llama.rn's JSI layer (`cpp/jsi/JSIParams.cpp:356`), and the bench app passes init params through.

UNKNOWN:
- whether llama.rn's iOS framework picks the i8mm/dotprod repack path on the A15 (Q1 answers it);
- whether the bench app forwards arbitrary init keys (check `src/bench/modelBench.ts` passes `no_extra_bufts` through before the session; if not, Part 1 needs a one-line change there, and Part 2 still works).
