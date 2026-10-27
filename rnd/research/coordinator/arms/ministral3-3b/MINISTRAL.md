# MINISTRAL3-3B (2026-10-20): GATE v2 screens NO-GO on K0 and K1, both samplers; stage 2 not run

TL;DR: swapping Qwen3-1.7B for Ministral-3-3B-Instruct-2512 (official Q4_K_M) cuts default-mode confident errors a lot: net +11 to +17 against bars of 10 and 9. But it fails GATE v2 on **false refusals** in all 4 runs (K0 3-4 of 20, max 2; K1 7-9 of 20, max 4), and on K1 also on U over covered items (-0.12 / -0.16, min -0.071). The mechanism is citation non-compliance, not knowledge. Ministral drops the `[n]` citations on about 60 % of the items the 1.7B cited, so the engine releases those answers behind the warning line, which the default product refuses. About half of the "fixes" are also refusals produced the same way (by refusal 6-8 of 13-18). Answers are 2.0-2.4x longer, and screen wall time is 2.4-3.5x the 1.7B's on the mini. Frozen rule: NO-GO, so the arm ends.

| Item | Value |
|---|---|
| Criterion | MINISTRAL-criterion.md sha256 80add993..., committed with patches + tools as fa1c4a9b before screen generation; GATE v2 = null-cal/GATE-V2.md @ 8c175580 |
| Candidates | V = ministral3-3b.patch (T 0.1 vendor, other samplers neutral), E = ministral3-3b-engsamp.patch (engine 0.7/40/0.95/0.05); both model swap only otherwise |
| Sanity | 4/4 runs: traces n/n, 0 error rows, model.sha256 9ed150d4 on every row, temperatures 0.1 (V) / 0.7 (E) as specified, dead changed 0 |
| Haiku calls | screens 364 (100 + 100 + 82 + 82) + onboarding smokes 20 = **384**; 0 Opus, 0 paid |

## Gate lines (verbatim, screen_gate_v2.py)
```
min3v K0: problems 30 | fixed_u 18 (by refusal 8) | new CEu 1 | net 17 (bar 10) | false refusals 3/20 (max 2) | sentinels worse 10 (report only) | U_cov -0.0320 [-0.0957, 0.0244] (min -0.059) | changed 50 | dead changed 0 -> NO-GO
min3e K0: problems 30 | fixed_u 14 (by refusal 6) | new CEu 3 | net 11 (bar 10) | false refusals 4/20 (max 2) | sentinels worse 9 (report only) | U_cov -0.0415 [-0.1043, 0.0188] (min -0.059) | changed 50 | dead changed 0 -> NO-GO
min3v K1: problems 21 | fixed_u 13 (by refusal 8) | new CEu 0 | net 13 (bar 9) | false refusals 7/20 (max 4) | sentinels worse 6 (report only) | U_cov -0.1231 [-0.2076, -0.0425] (min -0.071) | changed 41 | dead changed 0 -> NO-GO
min3e K1: problems 21 | fixed_u 13 (by refusal 8) | new CEu 1 | net 12 (bar 9) | false refusals 9/20 (max 4) | sentinels worse 8 (report only) | U_cov -0.1642 [-0.255, -0.076] (min -0.071) | changed 41 | dead changed 0 -> NO-GO
```

## Per-run extras (tools/screen_extras.py; control = mini pool control traces on the same items)
| run | CE-unwarned ctl -> cand | warned ctl -> cand | U_cov ctl -> cand | answer tokens median (ctl) | mean ratio | wall ratio (mean totalMs) | decode median (ctl 57) |
|---|---|---|---|---|---|---|---|
| V K0 | 30 -> 13 | 0 -> 11 | 0.386 -> 0.354 | 83.5 (41.5) | 2.11 | 3.46 | 27.6 |
| E K0 | 30 -> 19 | 0 -> 10 | 0.386 -> 0.345 | 91.5 (41.5) | 2.38 | 2.79 | 30.3 |
| V K1 | 21 -> 8 | 0 -> 15 | 0.431 -> 0.307 | 88 (44) | 2.00 | 3.31 | 23.1 |
| E K1 | 21 -> 9 | 0 -> 17 | 0.431 -> 0.266 | 93 (44) | 2.27 | 2.44 | 28.2 |
Wall ratios mix model cost with mini load (the controls ran under different load). Prefill medians were 1.9-2.8 s against 0.93 s for the control. Decode is about 0.5x the control's, as in stage 0.

## Why (citations)
| run | control answers with citations | of those, candidate uncited | candidate answers with citations |
|---|---|---|---|
| V K0 | 17/50 | 11 | 6 |
| E K0 | 17/50 | 10 | 7 |
| V K1 | 28/41 | 15 | 13 |
| E K1 | 28/41 | 17 | 11 |
Every false-refusal example checked (V K0 3/3, E K1 5/9) is a plausible answer released as `weak_sources` behind "Not found in this phone's offline library. From the model's memory, may be wrong:" with `cited: []`. Examples: Podgorica/euro, fetal alcohol spectrum disorder, ASIC miner, the Union won the Civil War, the origin of "Google". The model knows the answer and ignores the `[n]` citation instruction, and the compact-model rules (uncited-with-sources / all-citations-removed) then warn. On K1, which leans on retrieved packs (28/41 control answers cited), the effect is larger.

## Reading
- This is a NO under the frozen gate. The gate cannot tell "better knowledge" from "refuses more". About half of the CE-unwarned fixes are new warnings (by refusal 6-8), while the non-refusal fixes are 6-10 on K0 and 5 on K1, about at the null's level (6-10 fixes).
- The lever, if anyone wants one, is citation compliance, not the model's knowledge. A prompt or format adaptation (Mistral-style citation instruction, or few-shot `[1]`) would be a new arm on the same swap. It also needs a second look at the speed and length cost (2x tokens at about 0.5x decode), so per-answer time on the phone would be about 4x the 1.7B's unless length is controlled.
- Stage 2 (MAIN n 97) was not run: the criterion requires GO on K0.

## Files
screen/min3v, screen/min3e (runs, traces, judgments, aggregates incl. .gate2.txt/.json), screen/min3*-screens.log; ONBOARDING.md (step 1); tools/screen_extras.py, tools/stage2_verdict.py (unused).
