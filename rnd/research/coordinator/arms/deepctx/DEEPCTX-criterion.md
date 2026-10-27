# DEEPCTX: does the deep tier gain from reading 1200 context tokens instead of 400? (frozen 2026-10-10 10:4x, coordinator; r4to's standing instruction 2026-10-08: run autonomously)

Question: the recommended deep configuration (cut 6 + Qwen3.6-35B-A3B + thinking 512, arm H of DT512) reads DEEP_CONTEXT_TOKENS = 400 of retrieved context (the fast tier reads 1200). DEEPNORAG showed the packs still add ≈ +0.045 to the deep tier; DEEPFULL changed context to 1200 only bundled with the "detailed" persona and cap 400 (−0.013, confounded). Isolate the context lever: 1200 tokens, succinct persona, cap 200, thinking 512, everything else as H.

## Fixed inputs
- Arm **X**: mini tree `be-0cfd4a77-deepctx` = rsync of `-dt512` (cut 6 824e0b35… + deepthink eb3f464b… + dt512 f9a1979b…) + `deepctx-on-dt512.patch` (sha 1335c2c7…: depth.ts DEEP_CONTEXT_TOKENS 400 → 1200; DEEP_MAX_TOKENS 200 unchanged); `diff -rq` vs dt512: ARM, DEEPCTX_PATCH_SHA256, depth.ts only. Context budget: 4096 − 200 − 512 − overhead ≥ 1200 (answer.ts budget clamp), ctx stays 4096. Runner `tools/remote-run.sh` (= dt512's + patch/constant/ARM checks), adapter 7a0282ae…, llama-server b11010, `--deep-model`, `--places` kit-vexact, detector v3b, `--timeout-ms 600000`. Requests = H's with runId/arm rewritten: smoke 36de9ad0…, slice 781d0a47….
- Controls: **H** (DT512; Haiku rows s42 for L1, Opus s42/s43 for L2), **D** (no thinking) and **K** (claim) for the ladder.
- Script-only scoped exception as DT512; exposures logged.
## Stages and rules (strict; SLICE20; near-miss rule)
1. Smoke (2 v0.1 items, dx-smoke-X): 2/2 `generate:deep-thinking`, 1 ≤ reasoning ≤ 522, 0 errors, non-empty answers; also record the context tokens actually used per item from the trace (expected > 400 on at least one). Else FAIL-INFRA, stop.
2. Slice 20 (signal20-vpara, seed 42), Haiku 5.5-low N = 4, paired vs H's Haiku rows on the same ids: **continue** if wins ≥ H + 3 OR Δ ≥ +0.03; near-miss (Δ within 0.01 of +0.03) → Opus N = 4 on the 20 ids for X and H. Else **NO** (log; context lever closed for the deep tier).
3. Full 51 ids seed 42, Haiku vs H: same rule → Opus N = 4 on s42, seed 43 (generation + Opus), two-seed scales beside H, D, K. Verdict: **BETTER** (two-seed Δ vs H CI low > 0), else **NO** (report the point and CI; a non-negative point with a longer prefill is not adopted). Report time p50 (prefill grows with context) and reasoning stats.
- One generation per seed and stage; no rerun except an infrastructure error before the first token.
## Stop rules and budget
Disk ≥ 25 GiB (30 GiB now), swap ≤ 8 GB, heavy lock, one MoE server, never restart Docker or stop the detector; never run while another heavy job is on the mini. Mini: smoke ≤ 10 min, slice ≤ 1 h, full ≤ 2.5 h per seed. Haiku ≤ 40 + 102 (+ 40 near-miss); Opus ≤ 204 only after stage 3 continuation (+ ≤ 80 near-miss).
## Outputs
`arms/deepctx/DEEPCTX.md` (≤ 60 lines; cites this sha and the patch sha), `aggregates/`, `tools/`, `arm.conf`; traces/judgments in `blind/V-para/runs-deepctx/`; smoke in `boar-eval/runs/kiln/deepctx/`. QUEUE entry and EXPOSURES row by the coordinator.
