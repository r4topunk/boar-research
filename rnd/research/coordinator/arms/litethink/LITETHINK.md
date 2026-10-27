# LITETHINK: thinking ON does not help the lite 1.7B + X2b on selftest20 (budget 512 NEGATIVE −0.041, budget 256 FLAT −0.001; Haiku, dev; 2026-10-16)

Criterion LITETHINK-criterion.md sha256 e235f9bc36f69232d32c9407a48141520eceda1d6bca5be87ddab632e11d17e7 (frozen 14:5x before any judged run; Ruleset 30). 80 Haiku 5.5-low calls (N=4 shards, both orders), Opus 0, 0 paid. MacBook, one llama-server at a time, :8094 untouched, load avg 16-19 (other sessions).

TL;DR: the 1.7B thinks briefly (p50 118 reasoning tokens) so budgets 256 and 512 give byte-identical answers on 18/20 items. The two judged arms are mostly two Haiku draws of the same answers. Mean of the two: Δ −0.021 (−0.058…+0.017). Thinking costs +1.5…2.3 s p50 total and +2.0…2.8 s ttft (desktop). Keep thinking OFF on the lite tier.

## Result (paired vs the no-think arm = LITE5-180 ON Haiku rows on the same 20 ids)
| arm | raw (CI) | Δ vs no-think raw (CI) | b/w | total p50 | ttft p50 | verdict (frozen) |
|---|---|---|---|---|---|---|
| no-think (LITE5-180 ON) | 0.522 (0.465–0.580) | — | — | 6.54 s | 4.71 s | — |
| think 512 | 0.481 (0.419–0.548) | **−0.041 (−0.084…+0.003)** | 7/10 | 8.09 s | 6.74 s | **NEGATIVE** |
| think 256 | 0.520 (0.455–0.588) | **−0.001 (−0.038…+0.038)** | 8/6 | 8.85 s | 7.54 s | **FLAT** |
| mean of the two judge draws | — | −0.021 (−0.058…+0.017) | 7/9 | — | — | (descriptive) |
| mean, 15 items that actually thought | — | −0.015 (−0.067…+0.030) | 6/6 | — | — | (descriptive) |
- Time clause (≤ 2 × 6.54 = 13.08 s) passes for both; no budget reaches the +0.03 bar. The no-think p50 comes from the LITE5-180 run (lighter host load): the time cost is an upper bound.

## Judge noise (why 512 vs 256 is not a budget effect)
- Answers byte-identical 512 vs 256: 18/20 (only medlineplus-en-005, 520 vs 264 reasoning, and outdoors-se-020 differ). Yet 512 − 256 = −0.040 (−0.074…−0.010); on the 18 identical answers alone −0.027 (−0.059…+0.001).
- The 3 deterministic first-aid/medline answers (identical across all three arms): think 512 − no-think −0.076, 256 − no-think −0.047, pure Haiku re-draw noise.
- So at n = 20 one Haiku pass carries ≈ ±0.03-0.04 of draw noise; the honest read is the mean row: flat to slightly negative.

## Split (LITE6 bucket; Δ think − no-think raw)
| bucket | n | 512 | 256 |
|---|---|---|---|
| thin | 8 | −0.011 (−0.075…+0.033) | +0.029 (+0.005…+0.058) |
| invented | 1 | +0.077 | +0.115 |
| rest | 11 | −0.073 (−0.133…−0.014) | −0.032 (−0.086…+0.029) |
- "rest" holds the 3 deterministic items and both reasoning-0 items (noise-only rows), so the rest-bucket loss is mostly judge draw. Thin +0.029 at 256 is n = 8 and one draw: not a lever.

## Reasoning and gate
- Reasoning tokens (LLM items): p50 118, p90 219, max 520 (512) / 264 (256); 0 on 5/20 = 3 deterministic (no LLM) + 2 LLM items (outdoors-se-007, -008: the model emitted no think block, both budgets).
- Budget-hit share (reasoning ≥ B − 8): 512 = 1/20 (5 %, medlineplus-005 at 520, flag thinkingBudgetExceeded); 256 = 2/20 (10 %).
- gate.py: per-item FAIL on the 2 reasoning-0 items (reported, not rerun per criterion); kill_if NO-KILL for both budgets (0 empty/cut, reasoning-0 on 2 < 3). Answer words p50 37.5 vs 38.5 no-think: thinking does not lengthen answers (the thin mechanism is untouched).
- Smoke: the 13:06 smoke failed (mixed runId/config across packs in one file); re-run 14:53 as one file per pack, 3/3 PASS per budget.

## Worst / best (mean Δ of the two draws; public self-tests)
- Worst: factbook-004 (Thimphu name): think invents "derives from Druk Yul (Land of the Dragon)" (−1.67/−1.00). medlineplus-005 (pubic lice, budget hit at 512): the 512 answer gives washing and vacuuming only, no lice medicine (−1.00 at 512, 0 at 256). ethereum-se-002 (ENS expiry): think says "you must manually transfer it to the new permanent registrar" (−0.33/−0.67).
- Best: outdoors-se-020 (Austrian Alps bivouac) +0.33/+0.83: think separates one night vs multi-night camping. ethereum-se-014 (ticker length) +0.33/+0.50: think leads with "no maximum limit". travel-se-017 (insurance on phone) +0.50/+0.50.

## Decision
Thinking stays OFF for the 1.7B lite tier (FAST path). LITE-THINK closed: no budget lever, +2-3 s ttft on desktop (more on a phone at ≈ 50 tok/s decode). The remaining lite levers stay as in LITE6/LITEREACH2 (reach, not reasoning).

UNKNOWN: one seed and one Haiku draw per budget (draw noise ≈ the MDE at n = 20); no-think timing from another load state; phone timing unmeasured.

## Files
tools/{mkreq.py,run_lt_gen.sh,seq.sh,gate.py,judge.sh,agg.py}; runs/litethink-t{256,512}-st20-<pack>-s42.{requests,traces,judgments.haiku55-low}.jsonl; runs/smoke/; aggregates/{litethink.json,gate-t256.json,gate-t512.json,gate-t*.txt}. Inputs public self-tests only; blind/ and rnd/veil/ not read (no EXPOSURES row).
