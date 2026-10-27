# DT512: half the deep thinking budget (512) — same quality at ×0.6 time? (frozen 2026-10-09 08:3x, coordinator)

Question: the deep tier + 1024-token thinking (T) is the best measured configuration (V-para floor-adj [competitor score removed]) at p50 143–146 s on the desktop proxy and ≈ 3.5–5 min per answer on a 12 GB phone by a competitor's public measurement (WEB-SWEEP 10-09). DEEPTHINK-2 found no gain at 3072. Does a 512-work budget keep the gain (T − D = +0.075 raw) while cutting the thinking time roughly in half? p10 of T's reasoning was 497–644 tokens and 61–71 % of items hit 1024, so a 512 budget cuts most items short: the question is how much quality that costs.

## Fixed inputs
- Arm **H**: tree `be-0cfd4a77-dt512` = rsync of `be-0cfd4a77-deepthink` (cut 6 + deepthink patch eb3f464b…) + `arms/dt512/dt512-on-deepthink.patch` (sha f9a1979b…; one constant in answer.ts: DEEP_THINKING_BUDGET 1024 → 512; tsc rc 0 on a MacBook copy). Everything else as T: persona succinct, `--backend server --deep-model qwen3.6-35b-a3b-ud-q2kxl`, {quickFirst, alwaysComplete, deepModelId}, detector v3b, ship profile, `--places` kit-vexact, `--timeout-ms 600000`, ctx 4096 (context budget grows by 512: 4096 − 200 − 512 − 512 = 2872 ≥ 400, unchanged cap 400). Model sha 96b9c0af…, llama-server b11010.
- Control **T** = DEEPTHINK dt-T-vpara-s42 (Haiku rows for L1; Opus rows s42/s43 for L2); **D** = DEEPVPARA dv-D-vpara-s42/s43 (Opus) for the ladder.
- Script-only scoped exception as DEEPTHINK; exposures logged.
## Stages and rules (strict; SLICE20)
1. Smoke (2 v0.1 items, dt-smoke-T requests): 2/2 `generate:deep-thinking`, reasoning tokens ≤ 522 on both (budget enforced at 512 + message) and > 0, 0 errors, non-empty answers. Else FAIL-INFRA, stop.
2. Slice 20 (signal20-vpara, seed 42), Haiku 5.5-low N = 4 both orders, paired vs T's Haiku rows: **continue** if (a) wins ≥ T wins + 3 OR Δ ≥ +0.03 [promotion], OR (b) Δ ≥ −0.03 AND total-ms p50 ≤ 0.7 × T's p50 on the same ids [cheaper]. Else **NO**.
3. Full 51 ids seed 42, Haiku vs T: same clauses → Opus judge.v1 N = 4 on s42, seed 43 (generation + Opus), two-seed scales beside T and D. Verdict: **BETTER** (two-seed Δ vs T CI low > 0), **CHEAPER-PARITY** (CI includes 0, CI low ≥ −0.03, p50 ≤ 0.7 × T), **CHEAPER-LOSS** (Δ vs T CI low < −0.03 but Δ vs D CI low > 0: keeps part of the thinking gain at lower time; report the fraction kept = (H − D)/(T − D) on raw), else **NO**. Report the ladder entry either way.
- One generation per seed and stage; no rerun except an infrastructure error before the first token.
## Stop rules and budget
Disk ≥ 25 GiB (33 GiB now), swap ≤ 8 GB, heavy lock, one MoE server, never restart Docker or stop the detector. Mini: smoke ≤ 10 min, slice ≤ 1 h, full ≤ 2 h per seed. Haiku ≤ 40 + 120; Opus ≤ 204 only after stage 3 continuation.
## Outputs
`arms/dt512/DT512.md` (≤ 60 lines; cites this sha and the patch sha), `aggregates/`, `tools/`; traces/judgments in `blind/V-para/runs-dt512/`; smoke in `boar-eval/runs/kiln/dt512/`. QUEUE entry by the coordinator.
