# GREEDY (K0, Qwen3-1.7B, 2026-10-20): stage 1 NO-GO, stage 2 not run

TL;DR: greedy decoding (temperature 0, top_k 1) instead of temperature 0.7 / top_k 40 fixes 4 of 23 control CEs on the screen (need 6), with 1 sentinel worse (max 1). Screen CE count 19 vs 23 (-0.108, CI -0.216...-0.027) but the gate is the frozen rule: NO-GO, arm ends.

| Item | Value |
|---|---|
| Sampling before -> after | T 0.7, top_k 40, top_p 0.95, min_p 0.05 (health items T 0) -> T 0, top_k 1 (top_p/min_p inert), seed 42; env BOAR_SAMPLER_JSON (be/server.ts samplerOverride), no source change |
| Candidate | greedy.env sha256 bdda451e... |
| Criterion | GREEDY-criterion.md sha256 7e17dd98..., committed with env + tools/verdict.py as 3a1849c9 before generation |
| Screen run | greedy-K0-screen-s42, mini, 37 items, 24 changed answers, 48 Haiku calls, 0 Opus, 0 paid |
| Screen deltas vs control | U +0.004 (-0.015...+0.026), CE -0.108 (-0.216...-0.027), decline 0, refusal_like 0, warned 17 |
| Stage 2 | not run: NO-GO |

## Gate (verbatim)
```
screen K0: problems 27 (CE in mini control 23) | fixed 4 (need >= 6) | still CE 19 | sentinels worse 1/10 (max 1) | changed answers 24/37 -> NO-GO
  fixed vit-cry-003 1.5 -> 2.0
  fixed vit-cry-005 1.0 -> 2.0
  fixed vit-sci-002 1.0 -> 3.0
  fixed vit-trv-003 1.0 -> 2.0
  sentinel worse st-qa-money-se-002 corr 3.5->2.5
```
Note: the CE count drops 4 but 15+ items stay CE; greedy changes which wrong answer is produced, not whether the model answers confidently. Three of four "fixes" only reach 2.0.

## Examples (control -> greedy)
1. vit-sci-002 (1.0 -> 3.0): control gives wrong densities (355 vs 103 per km2); greedy swaps to populations (124M vs 83M), correct.
2. vit-trv-003 (1.0 -> 2.0): Chiang Mai to Pai "about 50 km east" -> "about 150 km north"; closer, still wrong.
3. st-qa-money-se-002 sentinel (3.5 -> 2.5): control answers the statement question; greedy rewrites it as "payment due date" (drifts off the question).

## Deviation
First attempt (unquoted JSON in greedy.env, shell stripped the quotes) produced 29/37 generation_failed rows and no usable output; env quoted, same override value, re-run. Failed artifacts kept in failed-quoting-attempt/. The criterion text was unchanged (it specifies the override value). Haiku calls total: 48 (the failed attempt judged 0).
