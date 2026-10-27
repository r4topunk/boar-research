# GEMMA-OPUS-MAIN (2026-10-21): GO by 0.001. Under Opus, Gemma 4 E2B is +0.031 U over the 1.7B on MAIN 97 (CI +0.005...+0.058), seed 42; seed 43 +0.041, pooled +0.036

Criterion GEMMA-OPUS-MAIN-criterion.md (sha 8bf4a4ae..., rnd b0ad9295), frozen with the unit set before any call. Cost: **362 new Opus judge.v1 calls** (cap 400; all claude-opus-5-5, every shard rc 0, no STOP file) plus 134 reused units (CV5-LADDER-OPUS, CV5-PER100-OPUS, CE-OPUS-CHECK, WARN-OPUS, packs self-tests, kiln runs). 0 generation, 0 Haiku, 0 paid.
Output: GEMMA-OPUS-MAIN-2026-10-21.json (sha 717ed35ee036...), tools/gemma_opus_{prep,run,analyze}.py/sh. Metric definitions are confirm_report.py's, applied to Opus labels.

## TL;DR
- **Verdict: GO** (frozen rule: dU >= +0.03 and CI low > 0). The margin is thin: dU **+0.0311** against the +0.03 bar. One more item going the other way would flip it.
- The Haiku stage-2 verdict (FAIL, +0.028) is not reopened. It stays FAIL under Haiku. The two judges differ by +0.003 on this pair.
- The seed-43 pair agrees and is larger: **+0.041 (+0.013...+0.069)**. Pooled over both seeds: **+0.036 (+0.011...+0.062)**. Both are report-only.
- **Phone trade:** on the Pixel 8a, 73 questions, answer p50 is 4.2 s for the 1.7B and 11.8 s for Gemma (2.8x). PSS is 3.39 GB vs 4.52 GB.

## Primary pair, seed 42 (Opus judge.v1, MAIN 97 K0, item bootstrap B 2000 seed 11)
| measure | 1.7B | Gemma E2B | Gemma - 1.7B [95 % CI] | Haiku, same pair |
|---|---|---|---|---|
| **U** | 0.435 | 0.466 | **+0.031 [+0.005, +0.058]** | +0.028 [+0.006, +0.052] |
| CE-unwarned (count) | 6 | 3 | rate -0.031 [-0.083, +0.010] | 7 -> 2 |
| CE any | 18 | 10 | | |
| declined / warned / refused R | 7 / 39 / 46 | 9 / 33 / 41 | | 46 -> 41 |
| default-mode U (refusals = 0) | 0.271 | 0.310 | +0.039 [+0.005, +0.074] | +0.034 |
| U on items both answer (n 47) | 0.534 | 0.564 | +0.031 [-0.009, +0.074] | +0.023 |
| U on control-covered (n 51) | | | +0.003 [-0.042, +0.048] | |
| items better / worse | | | 39 / 21 (75 texts changed) | |

## Seed 43 and pooled (report only)
| pair | dU [CI] | CE-unwarned | refused R | default-mode dU | both-shown dU (n) |
|---|---|---|---|---|---|
| seed 43 | +0.041 [+0.013, +0.069] (Haiku +0.030) | 4 -> 1 | 46 -> 40 | +0.048 [+0.016, +0.083] | +0.048 [+0.007, +0.088] (48) |
| pooled 2 x 97 | +0.036 [+0.011, +0.062] (Haiku +0.029) | 10 -> 4, rate -0.031 [-0.062, 0.000] | 92 -> 81 | | |

## Opus vs Haiku, per arm
| arm | U Opus | U Haiku | offset [CI] | Spearman s | CE agree / correct agree (of 97) | CEu Haiku-only / Opus-only |
|---|---|---|---|---|---|---|
| 1.7B s42 | 0.435 | 0.406 | +0.029 [+0.007, +0.050] | 0.88 | 88 / 83 | 2 / 1 |
| Gemma s42 | 0.466 | 0.434 | +0.032 [+0.010, +0.053] | 0.89 | 88 / 77 | 2 / 3 |
| 1.7B s43 | 0.436 | 0.402 | +0.033 [+0.013, +0.053] | 0.87 | 88 / 87 | 4 / 1 |
| Gemma s43 | 0.476 | 0.432 | +0.044 [+0.026, +0.062] | 0.93 | 88 / 79 | 5 / 0 |
Reading:
- Item rankings agree across judges (Spearman 0.87-0.93).
- Opus scores every arm higher, by +0.03 to +0.04 U. That offset is smaller than the +0.08 to +0.10 seen on the ladder frame.
- On seed 42 the Opus offset is nearly equal for both arms, so dU hardly moves (+0.028 -> +0.031). On seed 43 Opus lifts Gemma more.

## Sentences the morning report may use (each names the judge, the seed count and "dev")
- "Under Opus, Gemma 4 E2B is +0.031 U over the 1.7B on MAIN 97 (CI +0.005...+0.058), 1 seed, dev questions. This passes the pre-registered +0.03 rule by 0.001. Under Haiku the same pair is +0.028 and fails it."
- "A second seed agrees under Opus (+0.041, CI +0.013...+0.069); pooled over two seeds +0.036 (+0.011...+0.062) (report only)."
- "Gemma shows fewer confident errors without a warning: 3 vs 6 per 97 under Opus (seed 42; pooled 4 vs 10 of 194, CI includes 0)."
- "The gain comes mostly from answering more, not answering better: refusals drop 46 -> 41. On items both models answer, the gain is +0.031 with a CI that includes 0 (seed 42)."
- "The cost is speed: on a Pixel 8a, answer p50 is 4.2 s for the 1.7B vs 11.8 s for Gemma, and PSS is 3.4 vs 4.5 GB."

## Sentences that may NOT be used
- "Gemma clears the bar" or "Gemma passes" without "under Opus" and "1 seed": under Haiku the same traces fail.
- "Gemma is clearly / robustly better": the margin over the bar is 0.001, and the CI low is +0.005.
- "Gemma gives better answers": on both-shown and covered items the seed-42 CI includes 0.
- Any U without its judge family.

## Limits and deviations
- One seed decides. n 97 dev (v0.1 57 + cooking 20 + money 20). Earlier Opus passes had already exposed many of these units.
- Run order deviation: tools/gemma_opus_run.sh listed its files through one sorted ls, so the ctl43 files ran before gem42 instead of "seed 42 first". No effect on the result: the full list fitted the cap (362 <= 400), and every file finished.
- The judge sees the warning line in warned texts. Reused rows come from earlier passes on the identical (item, text, refs/questions frame).

## Files
- ruler/gemma-opus-main/in/set.json, gemma-opus-main/out/*.judgments.jsonl
- tools/gemma_opus_prep.py, gemma_opus_run.sh, gemma_opus_analyze.py
