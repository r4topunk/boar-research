# HAIKUJUDGE result (2026-10-07 17:58, runner; criterion HAIKUJUDGE-criterion.md sha256 58e9c084…, verified OK before the first call)
**Verdict: ADOPT Haiku 5.5-low as L1 judge** (all 4 bars pass, rule read once). Caveat below: it compresses paired gaps (deep35 − 4B Δ +0.007 vs Opus +0.029).

## Inputs (sha256 first 12, inputs.sha256; all equal to the JUDGE2 record)
| file | sha |
|---|---|
| arms/deepread/deep35-R450.traces.jsonl / .judgments.jsonl (Opus judge.v1) | 05710eee2f92 / b40265bf921b |
| arms/deepread/deep35-R450.judgments.sonnet-low.jsonl / .sonnet-med.jsonl | c4d5400d6054 / fa40dcd451ea |
| anvil/exp/oracle/runs/qwen3-4b-R450.traces.jsonl / .judgments.jsonl (Opus judge.v1) | 21a761a3ca1a / d51e87775b38 |
| bench/v0.1 refs / questions | bd235bb9811f / 568b3ececd8a |
| harness/judge.mjs / eval-lib judge-core.mjs / claude-cli.mjs (unchanged; boar-eval HEAD 0ccab93) | b3c3cd160dab / 521f7ad33a13 / cdbdcb584f63 |
| analysis: arms/judge2/judge2-analysis.mjs (reused as is) | 0ac055aa17fb |

## Smoke
`claude -p --model claude-haiku-5-5 --effort low --output-format json` accepted (CLI 2.1.293); modelUsage key `claude-haiku-5-5` (canonicalModel claude-haiku-5-5, firstParty). All 228 judged rows carry judgeModel claude-haiku-5-5, judgeVersion judge.v1-low (same tag as Sonnet-low: kept apart by file and system name; never pooled).

## Legs (commands per criterion, from boar-eval/; runner wrapper run-leg.sh = rerun on exit 4, stop at > 2 failures)
| leg | outputs (boar-eval/runs/kiln/haikujudge/) | calls | failures / reruns | median s/call | wall | [usage detail removed] USD |
|---|---|---|---|---|---|---|
| A1 deep35-R450, low | deep35-R450.judgments.haiku55-low.jsonl | 114 | 0 / 0 | 3.52 | 11.5 min | 0.073 |
| A2 medium | not run (A1 passed the agreement bar; condition not met) | 0 | — | — | — | — |
| B qwen3-4b-R450, low | qwen3-4b-R450.judgments.haiku55-low.jsonl | 114 | 0 / 0 | 3.65 | 11.7 min | 0.074 |
Total: 228 Haiku calls + 1 smoke, 0 Opus, 0 mini (cap 342). Opus judge.v1 on the same 114 calls = [usage detail removed] [usage detail removed], Sonnet-low [usage detail removed]; Haiku ≈ 0.07 (≈ 14× cheaper than Sonnet-low).

## 3-judge table, deep35-R450 v0.1 EN 57 (orders combined per item, disagreement = tie; analysis.json)
| judge | same winner vs Opus | vs Sonnet-low | r BOAR mean vs Opus | κ corr ≥ 4 vs Opus | ratio (Δ vs Opus, 95 % CI, 2000 boots seed 5) | pos. consistency | median s/call |
|---|---|---|---|---|---|---|---|
| Opus 5.5 judge.v1 | — | — | — | — | 0.634 | 96.5 % | 5.08 |
| Sonnet 5.5-low (judge.v1-low) | 54/57 | — | 0.930 | 0.682 | 0.597 (−0.037 [−0.057, −0.019]) | 98.2 % | 3.14 |
| Haiku 5.5-low (judge.v1-low) | **54/57** | 53/57 | 0.922 | 0.651 | 0.566 (**−0.069** [−0.090, −0.049]) | 96.5 % | **3.52** |
Haiku vs Sonnet-low: r 0.920, κ 0.755, Δ −0.032 [−0.053, −0.011].
Leg B (4B-R450): Haiku vs Opus same winner 56/57, r 0.889, κ 0.690, ratio 0.559 vs 0.606 (Δ −0.047 [−0.073, −0.022]), pos. cons. 98.2 %.
Ranking (deep35 − 4B paired Δratio, 57 items): Opus +0.029 [−0.004, +0.063] (26 better / 18 worse); Haiku **+0.007** [−0.018, +0.032] (25 / 20) → sign preserved.

## Rule (criterion, read once)
same winner ≥ 54/57: 54 PASS · median s/call ≤ 4.7: 3.52 PASS · failures ≤ 2/114: 0 PASS · ranking Δ > 0: +0.007 PASS → **ADOPT**.

## Deviations
- Leg runs wrapped in run-leg.sh (same judge.mjs command; only adds the resume-on-exit-4 loop and logs). No reruns were needed.
- s/call = median of row durationMs (claude CLI duration_ms), the same measure that gives Sonnet-low 3.14 / Opus 5.08 on the frozen files.
- Sonnet-low has no 4B-R450 judgments, so leg B has no Sonnet column.

## UNKNOWN
- Gap compression: Haiku's offset vs Opus differs by arm (−0.069 deep35, −0.047 4B), so the paired Δ shrinks from +0.029 to +0.007 (×0.25). The L1 promotion bar (Δ ≥ +0.03 under Sonnet-low) is likely too strict under Haiku; a re-anchored bar is not measured here (n = 1 arm pair).
- Haiku 5.5-low agreement on signal20 specifically (the L1 slice) is untested; this calibration is on the full 57.
- Concurrency / rate limits under parallel judging: PARJUDGE (frozen) tests it next.

## Draft addendum for L1-PROTOCOL.md (NOT applied; coordinator decides)
- **Addendum 2026-10-07 (HAIKUJUDGE, criterion 58e9c084…):** Haiku 5.5 effort low replaces Sonnet-low as the L1 judge: same command with `--judge-model claude-haiku-5-5 --effort low --system <arm>-haiku55-low`, outputs `<arm>.judgments.haiku55-low.jsonl` (rows still tag `judgeVersion: judge.v1-low`, so judge identity is the `judgeModel` field + file/system name; never pool Haiku and Sonnet rows). Calibration: same winner 54/57 vs Opus (= Sonnet-low), r 0.92, κ 0.65, 3.5 s/call, 0 failures/228, ≈ 14× cheaper. Haiku runs ≈ −0.05…−0.07 vs Opus and compresses paired gaps (deep35 − 4B +0.007 vs Opus +0.029), so the Δ ≥ +0.03 promotion bar is conservative under Haiku; the "wins ≥ control + 3" arm of the rule is unchanged. Any control judged with Sonnet-low must be re-judged with Haiku 5.5-low (`--system <ctl>-haiku55-low`) before it is reused as a paired L1 control.
