# DT256: a quarter of the deep thinking budget (256) — where does the thinking gain start to fall? (frozen 2026-10-09 18:4x, coordinator)

Question: DT512 showed 512 ≡ 1024 (V-para paired +0.011, −0.010…+0.031) at ×0.55 time. Is 256 still at parity (≈ ×0.35 time; ≈ 1–1.3 min on a 12 GB phone by the competitor's numbers), or is this where the gain drops? FAST_THINKING_BUDGET is already 256 for the fast tier.

## Fixed inputs
- Arm **Q**: tree `be-0cfd4a77-dt256` = rsync of `be-0cfd4a77-deepthink` + `arms/dt256/dt256-on-deepthink.patch` (sha 9d91b564…; answer.ts DEEP_THINKING_BUDGET 1024 → 256; tsc rc 0 on a MacBook copy). Everything else as DT512/T (persona succinct, `--deep-model qwen3.6-35b-a3b-ud-q2kxl`, places kit-vexact, detector v3b, `--timeout-ms 600000`, ctx 4096). Model sha 96b9c0af…, llama-server b11010.
- Controls: **T** = DEEPTHINK dt-T-vpara-s42/s43 (L1 control, Haiku rows s42; Opus rows), **H** = DT512 dh-H-vpara-s42/s43 (Opus), **D** = DEEPVPARA (Opus).
- Driver: `arms/_lib/arm.sh arms/dt256/arm.conf` (first arm on the consolidated driver; launch guards on). Script-only scoped exception as DEEPTHINK; exposures logged.
## Stages and rules (strict; SLICE20)
1. Smoke (2 v0.1 items): 2/2 deep-thinking, 0 < reasoning ≤ 266, 0 errors, non-empty answers. Else FAIL-INFRA.
2. Slice 20 (signal20-vpara, seed 42), Haiku vs T: **continue** on (a) wins ≥ T + 3 or Δ ≥ +0.03, or (b) Δ ≥ −0.03 and p50 ≤ 0.5 × T's p50 [cheaper]. Else **NO** (256 loses measurable quality; 512 stays the recommendation).
3. Full 51 ids s42, Haiku vs T: same → Opus s42, seed 43 + Opus, two-seed scales beside T, H, D. Verdict: **CHEAPER-PARITY** if the two-seed Δ vs T CI includes 0 with CI low ≥ −0.03 and p50 ≤ 0.5 × T; **CHEAPER-LOSS** if Δ vs T CI low < −0.03 but Δ vs D CI low > 0 (report the fraction of the thinking gain kept); else **NO**. Report the ladder entry either way.
- One generation per seed and stage; no rerun except an infrastructure error before the first token.
## Stop rules and budget
Disk ≥ 25 GiB (33), swap ≤ 8 GB, heavy lock, one MoE server, never restart Docker or stop the detector. Mini: smoke ≤ 10 min, slice ≤ 45 min, full ≤ 1.5 h per seed. Haiku ≤ 40 + 120; Opus ≤ 204 only after stage 3 continuation.
## Outputs
`arms/dt256/DT256.md` (≤ 60 lines), `aggregates/`, `arm.conf`; traces/judgments in `blind/V-para/runs-dt256/`; smoke in `boar-eval/runs/kiln/dt256/`. QUEUE entry by the coordinator.
