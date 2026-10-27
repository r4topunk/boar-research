# CE-OPUS-RU criterion (frozen 2026-10-21 before any Opus call), hypothesis HON-3 (ruler/hypotheses-2026-10-21.json)

## Question
Does RU's headline ("the groundedness gate cuts confident errors a user sees in default mode from 10 to 4 of 177, with 0 of 15 supported-correct
answers refused") survive when the deciding answers are re-judged by Opus judge.v1 instead of Haiku 5.5-low? CE-OPUS (2026-10-20) found Haiku
over-calls CE (Haiku-only CE 8/47, Opus-only 0/47), so the control count of 10 may shrink.

## Set (0 calls; ce-opus-ru/tools/prep.py on the frozen RU analysis.json, t = 0.919)
The decisive RU K3 answers only: 10 control CE-unwarned + 19 gate-refused + 15 supported-correct + the 4 CE-unwarned R still shows
(subset of the 10); overlaps (6 CEs are among the 19 refused) give **38 unique answers** (v01 12, boar-factbook 10, boar-medlineplus-en 6,
boar-simplewiki-en 7, qa-money-se 3). Answer texts = the existing MacBook LITEPACKS K3 traces (arms/litepacks/traces/lp-K3-{v01,cm,st}-s42),
no generation. Dev sets only (v0.1 57 + self-tests); no blind/, rnd/veil, bench/v0.4.

## Judge
judge.v1 bytes, Opus: arms/deepthink/tools/shard_judge.sh model opus (= node harness/judge.mjs --judge-model opus, no --effort), both orders,
seed 7, --gap-ms 0, N = 4 shards, one pass per unit (ce-opus-ru/tools/run.sh; bench dirs as litepacks/tools/judge.sh).
**calls_cap: Opus 200** (planned 76 = 38 x 2; spare for shard reruns). Haiku 0, paid API 0, generation 0, phone 0.
A shard that stops (STOP file) is fixed and rerun, never skipped; every id needs both orders before analysis.

## Analysis (ce-opus-ru/tools/analyze.py, committed with this file)
The frozen RU code (tools/analyze.py, unchanged, imported) with one substitution: for the 38 set answers, (s, sref, corr) come from the Opus
judgments; the other 139 items keep their Haiku values; gate scores (P_FAIL) and Haiku support labels are unchanged. `--haiku-only` reproduces
RU (10 -> 4, 0/15) as the sanity check (done before freezing: reproduces). Definitions as RU: CE-unwarned = shown in default mode AND corr <= 1.5;
false refusal = shown by C, gated, SUPPORTED, corr >= 4, refused by R (P_FAIL >= 0.919).

## Decision (pooled 177, t = 0.919, Opus labels)
- **(a)** Opus control CE-unwarned count >= 6 AND gated-arm (R) count <= half of the control count.
- **(b)** 0 false refusals under Opus labels (k = 0 of the supported answers with Opus corr >= 4; denominator reported; the brief's "0 of the 15").
- **PASS iff (a) and (b).** Kill rule: if (a) or (b) fails, claim v5 drops the "10 to 4" headline and the gate goes to post-bounty research
  ("Haiku-only signal"); the honesty section leads with HON-1/HON-2 numbers instead.

Reported, not deciding: exact Clopper-Pearson 95 % CIs on every count (/177 and the FR denominator), one-sided sign test on the gate-removed CEs,
RU's bootstrap CI of the rate difference, the RU rule verdict under Opus, the t = 0.5 row, MAIN/CAND split, HON-3's own wording variants
(control >= 7; relative drop >= 40 %), Haiku-Opus CE agreement on the 38 (count, exact CI, kappa, Haiku-only / Opus-only lists, corr MAE and
signed mean), and the number of refused answers that are Opus-correct (corr >= 4; RU's "memory-correct answers lost", 5 under Haiku).

## Known limits (stated before the run)
- (b) is near-structural: none of the 19 gate-refused answers carries a Haiku SUPPORTED label (support labels are not re-judged), so a false
  refusal under Opus correctness cannot appear; only its denominator can move. The informative cost number is the refused Opus-correct count.
- Items outside the 38 keep Haiku correctness: a shown answer Haiku scored > 1.5 that Opus would score <= 1.5 is not counted. CE-OPUS saw
  0/47 Opus-only CEs, so this is assumed small, not measured.
- One seed, MacBook texts, one Opus judge pass (two orders), single-family support labeller.
