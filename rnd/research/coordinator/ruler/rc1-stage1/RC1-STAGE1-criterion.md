# RC1-STAGE1 audit criterion (frozen 2026-10-21 before any call; condition of RULER-SPEC-v1-r3-REVIEW G3)

- Units: the 51 scored answers of RC1 (team.sopa.aoair 2.0.0-rc1, apk 2ef43258…) in handoff/pixel8-2026-10-20/bench/results/rc-cv5-51-15b/rows.jsonl (sha df26ed79…), warm-up row excluded; question = the row's query, text = the row's answer, unchanged. Dev set v0.1; no v0.4.
- Reference correctness: Opus judge.v1 correctness of the RC1 answer, mean of both orders, from arms/rc1-pixel/a1/judgments/rc1-shipped.opus.judgments.jsonl (A1).
- Stage 1: ruler/tools/decline2stage_stage1.mjs unchanged (sha 9599c1ba…), claude-haiku-5-5 low, one call per unit, rep 1, cap 55 (51 + retries).
- RC refusal text: RC1 has no fixed refusal string observed (A1: decline 0 per 100), so every unit counts as "not the RC's refusal text".
- **Bar (PASS):** ≤ 1 unit labelled "not attempted" among units with Opus correctness ≥ 3. Reported, no bar: total "not attempted" count, and their Opus correctness.
- PASS → R1 stands as the headline judge (spec §6.2). FAIL → headline = judge.v1 + U_net,g; stage 1 becomes a sensitivity row (spec §3.4). No second wording.
