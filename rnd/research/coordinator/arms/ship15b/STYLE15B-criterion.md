# STYLE15B criterion (frozen 2026-10-21 before any generation or judge call of this arm)

## Question
Is the engine's Succinct persona not worse than its Detailed persona (the native RC1 default) on the 1.5B and the 1.7B, with K1 packs? Feeds NOTE-1's Succinct ask.

## Arms (all on the Mac mini, tree be-0cfd4a77-cut7-litepacks, b11010 CPU -t 4, seed 42, K1 kit, LITEDECLINE_OFF=5, --reasoning off, ids arms/litepacks/data/v01-57.ids)
- 1.5B-S: = SHIP15B-PACKS arm P (patch ship15b-packs.patch: 1.5B swap, FACTS off, Succinct, maxTokens 512).
- 1.5B-D: patch style15b-detailed.patch = ship15b-packs.patch + the tree's own "detailed" personality (src/constants/personalities.ts) + maxTokens 1024
  (native Detailed cap, AppSettings Auto 512 Succinct / 1024 Detailed).
- 1.7B-S: the existing mini K1 control lpctl-K1-main-s42 (Succinct, maxTokens 512, FACTS on) and its Haiku rows.
- 1.7B-D: patch style17-detailed.patch = "detailed" personality + maxTokens 1024 (FACTS on), run_arm.sh style17-detailed K1 main.

## Judge
Haiku 5.5-low judge.v1, both orders, N 4 shards (run_arm.sh; identical (id, text) to the K1 control reuse its rows). Planned <= 3 x 114 new calls; task-wide Haiku cap 500
(incl. 102 DECLINE2STAGE stage-1 calls of SHIP15B). If the cap would be exceeded, the 1.7B pair is judged on the divergent half only (stated). Opus: none (task cap spent on SHIP15B);
the 1.7B Opus length slope (+0.31 s per doubling, LENGTH-SLOPE) is quoted next to the 1.7B result as a caveat, not applied.

## Metrics (tools/ship15b_analyze.py)
Items: the CV5 51 ids. U floor-adj = sum(s-1)/sum(r-1) (primary), raw, win-rate, per-100 correct-shown and CE-shown (not declined), item-cluster bootstrap B 2000 default_rng(11).
Cost: output tokens (timing.outputTokens) p50/mean, wall (timing.totalMs) p50/sum, share of rows at the token cap, per arm.

## Decision, per model (dU = U(S) - U(D), Haiku)
- NONINFERIOR iff CI low of dU >= -0.02. NOT-WORSE (point) iff dU >= -0.02 but CI low < -0.02. WORSE iff dU < -0.02.
- Report CE-shown difference beside it. Known Haiku bias: under-calls long warned answers (Haiku-only CE excess, CV5-PER100); stated, not corrected.

## Limits
One seed; n 51 dev; Haiku only; desktop mini decode speed, not the phone; bench engine, not the native app.

## Budget
calls_cap: Haiku 500 / Opus 120
