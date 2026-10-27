# CMP30OFF: Qwen2.5-1.5B vs Qwen3-1.7B on the Pixel 8a under "answer with a warning instead of declining"

r4to decided on 2026-10-20 that the app should answer, with an explicit warning, when the small model cannot ground its answer in the offline library. It should no longer decline. This arm repeats CMP30 under that policy.

- Setup: same phone (Pixel 8a, GrapheneOS, Android 17, 8 GB), same 31-row requests (warm-up + 30 public v0.1 dev items), same models, same judge.
- The one change is `engineOverrides.compactDeclinesOff: true`. It turns off the five compact-only declines (LITEDECLINE OFF5).
- Measurement only, no frozen rule. **n = 26 judged items, one phone run per model.**
- Phone sampling is unseeded, so the override − product deltas include run-to-run sampling noise.

## TL;DR

| Arm (Pixel 8a, n 26) | Q | U0 | Declines | Confident errors (corr ≤ 1.5) | Mean corr. of answered | Warned answers / their mean corr. | TTFT p50 | Decode tok/s p50 |
|---|---|---|---|---|---|---|---|---|
| 1.5B product rules (cmp30-q15) | 0.301 | 0.190 | 13 | 4 / 13 | 2.23 | – | 8.2 s | 18.6 |
| 1.7B product rules (cmp30-q17) | 0.334 | 0.179 | 17 | 1 / 9 | 3.50 | – | 9.5 s | 12.9 |
| **1.5B override (cmp30off-q15)** | 0.349 | 0.349 | 0 | 10 / 26 | 2.15 | 14 / 1.71 | 8.9 s | 17.6 |
| **1.7B override (cmp30off-q17)** | **0.394** | **0.394** | 0 | 8 / 26 | **2.62** | 14 / 2.00 | 9.2 s | 11.7 |

**Paired 1.7B − 1.5B under the override** (item bootstrap, B 2000, seed 11):
- Q = U0: +0.045 (−0.009…+0.100).
- Confident-error rate: −0.077 (−0.269…+0.154), that is 8 vs 10.
- Correctness: +0.46 (+0.02…+0.90). Both models answer all 26 items here.

**Which model wins under the override: Qwen3-1.7B.**
- It leads on every quality measure: Q/U0, mean correctness, and fewer confident errors.
- Only the correctness gap has a CI that excludes 0. The Q gap CI touches 0, so this is a lean, not a proven gap, at n 26.
- The 1.5B is still faster: decode 17.6 vs 11.7 tok/s, TTFT p50 8.9 vs 9.2 s (TTFT is about the same).

## What the override does

- **Per model:** U0 rises by +0.160 (+0.091…+0.226) for the 1.5B and by +0.215 (+0.146…+0.288) for the 1.7B. Q also rises (+0.049 / +0.060, CIs above 0).
  - Q rises because the judge scores a decline text lower than a partly right answer.
- **Confident errors:** the 1.5B goes from 4 to 10 and the 1.7B from 1 to 8.
  - The CE-rate delta is +0.08 (−0.13…+0.29) for the 1.5B and +0.20 (−0.02…+0.42) for the 1.7B.
  - This is the same trade LITEDECLINE measured on the desktop: OFF5 doubled the confident errors.
- **Warning line:** 14 of 26 answers carry it, for each model.
  - Mean correctness of warned answers: 1.71 (1.5B) and 2.00 (1.7B). Of these, 7 / 14 are confident errors for each model.
  - Unwarned (grounded) answers score 2.67 (1.5B, 3 CE in 12) and 3.33 (1.7B, 1 CE in 12).
  - So the warning lands where the errors are: 7 of the 1.5B's 10 confident errors and 7 of the 1.7B's 8 sit behind it.
- **Released rules** (reason codes, items can carry two):

| Released rule | 1.5B | 1.7B |
|---|---|---|
| uncited-with-sources | 9 | 9 |
| no-source (`declined-compact`) | 5 | 5 |
| all-citations-removed (always together with uncited-with-sources) | 2 | 6 |
| false-claim, uncited | 0 | 0 |

- **Under the product rules (CMP30, same table):** the 1.7B's better reading was hidden by its extra declines (U0 −0.010). The override removes the declines, and the reading gap shows up in U0.

## Build

- **bench-app** (branch live-view):
  - New request field `engineOverrides.compactDeclinesOff` (boolean, default absent). `src/engineOverrides.ts` parses it. It is excluded from the init-config key, so it never forces a model reload.
  - `src/runner.ts` calls the engine's `setBenchCompactDeclinesOff()` before each request.
- **Engine copy:** arm `cut7-cmp30off`, tree `c407db3224e2…`.
  - The LITEDECLINE patch is ported to `src/routing/answer.ts`: `AnswerDeps.compactDeclinesOff?: "three" | "all"` plus a module-level bench switch (true = "all").
  - Each released rule pushes `grounding:compact-decline-released-<rule>`. `<rule>` is one of `no-source` (was `declined-compact`), `false-claim`, `all-citations-removed`, `uncited-with-sources` or `uncited`.
  - Released rules emit one non-declining `weak_sources` warning event. The final text becomes `Not found in this phone's offline library. From the model's memory, may be wrong:` + newline + the answer.
  - The 4B-style uncited preface is skipped when the warning line is used, so there is one notice, never two. The `grounding:uncited-preface` code can still appear in that case, but its text is not added.
  - Grounded answers are untouched.
  - Patches: `tools/cut7-cmp30off.vs-0cfd4a77.patch` (sha256 `53f19f9d68a85125…`; it reproduces tree c407db32 from boar-app 0cfd4a77 with `scripts/engine.sh`, checked) and `tools/cmp30off.vs-cut7.answer.diff` (the readable delta).
- **APK:** `bench-app/build/boar-bench-0cfd4a77-cut7-cmp30off-nonet-c407db3224e2.apk`, sha256 `c1864d32872f09395b9cbac51505eac516d333d55c99536792123feecd901ef4`.
  - Built on the MacBook with an incremental gradle assembleRelease (Homebrew openjdk@17; no npm ci, no prebuild; existing nonet android/), signed with the same debug key.
  - Installed with `adb install -r`, so files/ was kept. `boar_bench.py check` reports networkPermissionAbsent true.
  - Both runs' bench.json carry tree c407db32 and `{"compactDeclinesOff": true}`. The script's "tree hash not found" warning only means it does not know the new tree.
  - Disk stayed at 5–6 GB free.

## Identity proof (override off)

1. **Engine test suite:** a copy of the cut 7 tree with node_modules from wt/cut7 passes 1346/1346 tests before the change. After the change it passes 1350/1350: the 1346 existing tests plus 4 new CMP30OFF tests in answer.test.ts (rules 1–4 released with the warning, a grounded answer unchanged, switch off = decline). `tsc --noEmit` is clean for both the engine and bench-app.
2. **3-item replay (plus warm-up)** on the desktop, using the bench runner's dry run: llama-server b11010 CPU, `--seed 42`, Qwen2.5-1.5B, items lan-cmp-003 / lan-hlt-002 / vit-cry-002.
   - With the override absent, answer text, reason codes and retrieved titles are identical, 4/4, between bench HEAD 7cdced8 with the cut 7 engine and the new build.
   - With the override on, the two declines (no-source, all-citations-removed) are released with the warning, and the grounded answer is unchanged.
   - Files are in `proof/`.
   - The phone is not seeded (LITELAT saw decline flips between repeats), so this proof was done on the desktop.

## Run

- **cmp30off-q15:** 31/31 rows, 6.6 min.
- **Cool-down:** about 4 min until thermal status had been 0 on 3 checks in a row, battery 33.6 °C.
- **cmp30off-q17:** 31/31 rows, 7.7 min.
- **Phone settings:** airplane mode on, Wi-Fi and Bluetooth off, app in front.
- **Conversion:** convert_device.py (commit 0cfd4a77, android, "Pixel 8a GrapheneOS Android 17", 8 GB, arm cut7) into `boar-eval/runs/device-pixel8a/cmp30off-q1{5,7}/`.
- **Judge:** Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, 52 + 52 calls, 0 failures.
  - The 4 saf-* items are first-aid cards with no public reference. They are reported missing, as in CMP30, so shard_judge exits with rc 1 by design.

## Caveats

- n = 26, one seed per arm, unseeded phone sampling.
- The product-rule rows are CMP30's runs, not same-session repeats.
- Haiku is the L1 triage judge, not Opus.
- These are v0.1 public dev items.
- The warned answers' correctness is low for both models: about half are confident errors. The warning is doing real work, and the policy trades declines for visible-but-wrong answers.

## Files

- `aggregates/cmp30off.json`: all metrics, the deltas, and the per-item warned list.
- `tools/agg.py`: the aggregation, 0 LLM calls.
- `tools/*.patch` / `*.diff`.
- `requests/`.
- `proof/`: desktop replay requests and answers, and the seeded llama-server wrapper.
- Phone results: `handoff/pixel8-2026-10-20/bench/results/cmp30off-q1{5,7}`.
