# DEEPTHINK-V02 Addendum 1 (frozen 2026-10-09 08:2x, coordinator): claim-scale measurement of the v0.2 thinking arm

Why: the L1 rule stopped the arm at Haiku Δ +0.027 vs the +0.03 clause (NO stands; this addendum does not reopen the promotion). The claim draft needs the v0.2 (development data) number for deep + thinking on the Opus scale, because the ladder's second set is otherwise unsized (CLAIM-DRAFT S35 says "no Opus number"). This is a measurement, not a decision: no engine change follows from it.

## Fixed inputs
- Traces: existing `blind/bench-v02/runs-deepthinkv02/dtv-TV-v02-s42.traces.jsonl` (sha b69323e0a5f3; no new generation). Judge: Opus judge.v1 sharded N = 4, both orders, 110 ids (`runs-deepvpara/judged.ids`), `--system deepthinkv02-TV-opus`, v0.2 refs 1e2668c488a1 / questions c883053b0595.
- Controls: D = `runs-deepvpara/dv-D-v02-s42.judgments.jsonl` (Opus), K = `runs-cut6/cut6-v02-s42.judgments.jsonl` (Opus). Scales as DEEPVPARA Stage 2 (floor_metrics with questions.v02-new strata, D_decl 0.306; paired.mjs TV vs D and TV vs K; per-category Δ), via tools/l2.sh.
## Rules
- Report: TV raw / floor-adjusted / above-decline with CIs, win-rate, paired Δ vs D and vs K with CIs, the bar reading ("floor-adjusted CI low > 0.50 and win-rate > 0" or "below by X"), per-category counts. One seed.
- Seed 43 (generation 3.3 h + 220 Opus) only if the one-seed paired Δ TV − D CI low > 0 (then the two-seed scales as planned in the main criterion); otherwise the one-seed number is reported as such.
- Opus ≤ 220 (+ 220 on seed 43). No Haiku. No rescue of the L1 verdict.
