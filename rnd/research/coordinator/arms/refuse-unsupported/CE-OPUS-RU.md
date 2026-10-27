# CE-OPUS-RU (HON-3): RU's gate headline re-judged by Opus (2026-10-21)

TL;DR: **PASS by the frozen rule** (criterion sha256 `e1d6f03b...`, committed 4dd4bd08 before any call). The Opus judge (judge.v1,
claude-opus-5-5, both orders, N = 4 shards) re-judged the 38 deciding K3 answers: 76 calls, 76 ok, 0 reruns, 0 STOP files, about 3 min wall.
The headline changes from **10 -> 4** to **7 -> 3** of 177. Claim v5 should quote the Opus numbers.

| (pooled 177, t = 0.919) | Haiku 5.5-low (RU) | Opus judge.v1 |
|---|---|---|
| CE-unwarned, control C | 10/177 (exact CI 2.7-10.1 %) | **7/177 (1.6-8.0 %)** |
| CE-unwarned, gated R | 4/177 (0.6-5.7 %) | **3/177 (0.35-4.9 %)** |
| CEs removed by the gate | 6 (one-sided sign test p 0.016) | 4 (p 0.063) |
| relative drop | 60 % | 57 % |
| rate diff, RU bootstrap CI | -0.062...-0.011 | -0.051...-0.006 |
| false refusals | 0/15 (exact CI 0-21.8 %) | **0/14 (0-23.2 %)** |
| refused answers that are correct (corr >= 4) | 5 of 19 | 6 of 19 |
| U on answered C -> R | 0.526 -> 0.556 | 0.543 -> 0.575 |
| coverage C -> R | 0.435 -> 0.328 | unchanged |
| RU's own rule (secondary) | PASS | PASS |
| t = 0.5 row | 10 -> 3, FR 0/15 | 7 -> 2, FR 0/14 |

- **Clause (a):** PASS. Control is 7 (>= 6) and R is 3 (<= 3.5).
- **Clause (b):** PASS. 0 of 14. This was near-structural, as the criterion said before the run: no refused answer carries a SUPPORTED label.
- **HON-3 wording variants:** control >= 7 holds (exactly 7), and the >= 40 % drop holds.
- **By set:** MAIN goes 5 -> 2 (Haiku 5 -> 2); CAND goes 2 -> 1 (Haiku 5 -> 2). The CAND pack-written self-tests carried most of the Haiku over-calls.

## Haiku vs Opus CE agreement (38 answers)
- They agree on 35/38 (exact CI 0.79-0.98), kappa 0.78. Haiku labels 10 CE and Opus 7.
- Haiku-only CEs: st-boar-factbook-004 and -009 (both gate-refused; Opus scores them 2.0), and st-boar-factbook-018 (the Wikidata facts table, Opus 3.5).
- Opus-only CEs: 0. The direction is the same as CE-OPUS: Haiku over-calls CE.
- Correctness MAE 0.49. Opus is more lenient on average (+0.22).
- Other movements:
  - lan-exp-003 is supported-correct under Haiku (4.5) but Opus scores it 2.0. It leaves the FR denominator, so 15 becomes 14. It is shown in both arms and is not a CE.
  - lan-cmp-005 is gate-refused. Opus scores it 4.0 (Haiku 3.0), so the count of correct answers the gate refuses goes from 5 to 6.

## Reading
- The gate effect survives Opus with smaller counts. The Opus-labelled reduction rests on 4 removed CEs; the sign test p is 0.063, and the RU bootstrap CI still excludes 0.
- Claim text: "7 to 3 of 177 confident errors shown (Opus judge), at the cost of 6 correct but unsupported answers refused and coverage 0.44 -> 0.33".

## Limits
- One seed. The answers are MacBook texts.
- The 139 items outside the set keep their Haiku correctness. An Opus-only CE elsewhere is not counted; CE-OPUS saw 0/47 such cases.
- Support labels are Haiku-only and were not re-judged.

## Budget
76 Opus calls (cap 200). Haiku 0, paid 0, generation 0, phone 0. Dev sets only.

## Files
- `CE-OPUS-RU-criterion.md` (+ `.sha256`)
- `ce-opus-ru/tools/{prep.py, run.sh, analyze.py}` (analyze.py imports the frozen RU tools/analyze.py unchanged)
- `ce-opus-ru/in/` (set + ids)
- `ce-opus-ru/out/` (Opus judgments and logs)
- `ce-opus-ru/ceopusru-{opus,haiku}.json` and `analysis-{opus,haiku}.json`
