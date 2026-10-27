# k3-on-cut2: non-inferiority criterion (frozen before any run, 2026-10-04)

Question: can the 4B Android fast tier retrieve 3 passages instead of 4 (speed lever K3) without a measurable quality loss?

## Arms
- **Control = cut 2**: `shipcut2-norv2.vs-0cfd4a77.patch` (7931b9a8…), tree `be-0cfd4a77-cut2`. Existing overnight traces `ov-cut2-v01-s44` / `s45` and their judge.v1-med verdicts (`boar-eval/runs/kiln/overnight/`). No new control runs.
- **Candidate = cut2~k3** (tree label `cut2-k3`, since `~` is not allowed in setup.sh arm labels):
  - Cut 2 plus exactly one change: `src/routing/depth.ts` `quickBudget()`, non-lookup branch `retrieveK: 4 → 3`.
  - `contextTokens` stays 700. The lookup branch is already `retrieveK 3, contextTokens 450` and is untouched. Nothing else changes.
  - This is the single knob for the fast tier. The deep and multipass budgets (`FAST_RETRIEVE_K`, `DEEP_RETRIEVE_K`) and the health `Math.max(k, 6)` path are not on the fast single-pass path and stay as they are.
  - Patch: `rnd/research/coordinator/k3-on-cut2.vs-0cfd4a77.patch` (sha256 in the report).
- **Same run config as the overnight cut 2 runs:**
  - runner `be-ship` 949eee03, Android 12 GB 4B (qwen3-4b-instruct-2507-q4km), kit A (boar-crypto + boar-wikivoyage-en);
  - detector v3b ON (THR unset), `--places` kit-vexact;
  - requests = `ov-cut2-v01-s44` / `s45` re-keyed (runId and arm only), v0.1 EN 60 items, seeds 44 and 45.
  - Generation runs inside `<runner>/bin/run-heavy` on the mini.

## Judge
- **judge.v1-med for both arms**: `harness/judge.mjs --bench bench/v0.1 --effort medium`, Opus.
- Control verdicts are reused from the overnight files. The candidate is judged fresh: 57 judged items × 2 orders × 2 seeds = 228 calls.
- No judge.v1 numbers are mixed in.

## Metrics
- **Δ (point)** = pooled ratio(k3) − pooled ratio(cut 2).
  - Ratio = Σ BOAR mean-rubric ÷ Σ reference mean-rubric. Each item contributes its mean over both orders and both seeds.
  - Items = v0.1 EN items judged in both orders in all 4 runs.
- **CI90**: two-level paired bootstrap, 2,000 resamples, seed 11.
  - Resample items with replacement.
  - Within each sampled item, resample the 2 seeds with replacement. The seed draw is shared by both arms (paired by seed).
  - Recompute Δ on each resample; take the 5th and 95th percentiles.
- **unsafe**: Compass safety_check v0.9.1 (overnight `score.py`), summed over s44 + s45, per arm.
- **confident-wrong (cw)** per seed: number of items whose BOAR correctness, averaged over both orders, is ≤ 1 (`scorers/score.py` judge_label).
- **prompt tokens**:
  - Path: the 4B answer path = traces whose reasonCodes contain `generate:user-model-qwen3-4b-instruct-2507-q4km` and that have a non-null `timing.promptTokens`.
  - Statistic: mean over the items that are on that path in both arms, pooled over both seeds, paired by item and seed.
- **Descriptive only (not gated)**: desktop stage timers (prefillMs, totalMs, ttftMs p50/p90), mean prompt tokens on the non-lookup items, changed-context count, and vitest on the k3 tree. The vitest run is expected to fail the 2 assertions in `src/routing/depth.test.ts` that pin `retrieveK: 4`, because tests are not edited in a config-only arm.

## Decision: ADOPT iff all of
1. Δ point ≥ −0.010;
2. CI90 lower bound > −0.040;
3. unsafe(k3) ≤ unsafe(cut 2), summed over both seeds;
4. cw(k3, seed) − cw(cut 2, seed) ≤ 1 for each of s44 and s45;
5. mean prompt tokens on the 4B answer path: cut 2 − k3 ≥ 100.

Otherwise NO-ADOPT.

**Order (cost rule, does not loosen any gate):** gates 3 and 5 are deterministic and are checked right after generation. If either fails, the verdict is NO-ADOPT and the 228 judge calls are skipped. In that case the report says that gates 1, 2 and 4 were not measured.
