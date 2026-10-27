# CEOPUS criterion (frozen before any call), 2026-10-20

Purpose: validate the Haiku 5.5-low CE label (model-usage audit M5) against Opus at the 1.7B's CE rate. Measurement only; nothing here changes a verdict.

## Set (0 calls to build: tools/prep.py)
- Answers judged by Opus: (a) the 23 K0 screen-control answers (arms/lp-screens/control, lpctl-K0-screen-s42) that are CE under Haiku; (b) the 24 GREEDY K0 screen answers (arms/greedy, greedy-K0-screen-s42) whose text differs from the control's. n = 47 answers.
- Cap 100 Opus calls: 47 answers x 2 orders = 94 calls (6 spare for retries). The full set (37 control + 24 changed = 61 answers = 122 calls) exceeds the cap, so the 14 non-CE control answers (10 sentinels + 4 non-CE problems) are dropped. Consequence: no "sentinel worse" check under Opus, and the control side is selected on the Haiku CE label (agreement on (a) is conditioned on Haiku CE; (b) is unselected).
- GREEDY answers byte-identical to the control reuse the control's Opus label.

## Judge
judge.v1 bytes: `node harness/judge.mjs --judge-model opus` (no --effort, as in past Opus claim runs), both orders, seed 7, --gap-ms 0, N = 4 shards via arms/deepthink/tools/shard_judge.sh (model opus), one pass per (source, unit): source in {ctl, greedy}, unit in {v01, qa-cooking-se, qa-money-se}, bench dirs as run_arm.sh. No preflight probe beyond the script's own checks. A shard that stops is resumed, never skipped.

## Definitions (same as lp-screens/tools/agg_run.py)
corr = correctness of the answer averaged over both orders; declined = trace answer.declined; CE = not declined and corr <= 1.5; warned = text starts with "Not found in this phone's offline library. From the model's memory, may be wrong:"; CE-unwarned = CE and not warned (reread-2026-10-20 definition). Haiku values = judgments already in the aggregates.

## Reported (tools/analyze.py)
1. CE agreement Haiku vs Opus over the 47 answers, plus Cohen kappa; same for CE-unwarned (label = CE and not warned); also split by source (ctl 23, greedy 24).
2. Correctness MAE = mean |corr_Haiku - corr_Opus| over the 47, and mean signed (Opus - Haiku).
3. GREEDY fixed count, frozen-gate definition (control CE -> greedy not CE), over the 27 screen problems: Haiku = 4 as frozen. Opus primary = problems whose Opus control label is CE and whose Opus greedy label (own judgment if changed, else control label) is not CE. Secondary = Haiku-CE control items whose Opus greedy label is non-CE. Limited to items with an Opus control judgment (the 23 Haiku-CE control items; the 4 non-CE control problems cannot be judged CE here and are counted as not-CE).

## Rule (measurement only, recorded)
If Opus-vs-Haiku CE agreement < 0.80 (over the 47 answers), flag every screen verdict of 2026-10-20 as judge-sensitive. Otherwise no flag.
