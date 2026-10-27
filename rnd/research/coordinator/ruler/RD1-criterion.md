# RD-1 CONVERSION-MAP criterion (frozen 2026-10-21 before computing; coordinator subagent; 0 LLM, 0 generation, 0 judge calls)

Hypothesis (ruler/hypotheses-round3-2026-10-21.json, RD-1): when the fact chunk is already in the reader's context, whether the answer uses
the fact depends on chunk features pack building controls (residue, length, fact offset, slot, number of kept chunks); they matter less for the 4B.

## Rows (item x reader x arm; fact chunk present in the generation prompt; existing Haiku 5.5-low judge.v1-low judgments only)
- R-A 1.7B LITEPACKS K3, self-tests 180: oracle fact chunk id (arms/oracle-st/tools/oracle-facts.json) in the replay's retfloor:kept ids
  (FACTPRESENT replay, kept-title parity 280/280) and the fact block found in a dumped generation prompt.
- R-B 1.7B LITEPACKS K1, self-tests 180: same rule.
- R-C 1.7B LITEPACKS K3, v0.1: the ORACLE-REAL gold chunk (arms/oracle-real/gold-labels.tsv, 30 items, Y/P) in the K3 kept ids, block in prompt.
- R-D 1.7B ORACLE-REAL arm (30 items, gold forced to slot [1]); context = the trace's kept list; fact block text = gold-chunks.json.
- R-E Gemma E2B K3 cand80 and R-F 4B K3 cand80 (coverage-matrix q4b): rows whose trace kept titles equal the 1.7B K3 replay's (then the
  1.7B replay context stands in) and whose oracle chunk is kept; corr from the arm aggregates.
- R-G 4B cut 7 ORACLE-ST ADD (180 self-tests, prompts dumped): fact block found in the prompt.
Rows with no LLM generation (extractive / instant answers: outputTokens 0 or no dumped prompt with the block) are excluded.

## Outcome
conversion = judge correctness (boar side) both-order mean >= 4 (ties: 4.0 counts).

## Features (deterministic, on the fact block as it appears in the context)
tokens = ceil(chars / 4) of the block body (the engine's estimator); slot = 1-based block index in the first generation prompt holding it;
n_kept = number of blocks in that prompt; residue = share of the block's characters on residue lines (>= 2 pipes, list/heading markers
-,*,•,#,> or '**' at line start, coordinate / Category: / File: strings, or a line < 40 chars without terminal punctuation) plus the PACK-HOLES
strong-pattern flag (arms/pack-holes/holes.py STRONG patterns) as a separate binary; fact_offset = characters from the body start to the start of
the sentence holding the fact (self-tests: the oracle in_pack_fact quote, exact normalised match else best >= 0.6 content-token overlap sentence;
v0.1: the first CHUNKCLEAN extraction span); fact_first2 = fact sentence is sentence 1 or 2 of the body; siblings = other blocks with the same title;
pack = the chunk's pack; qtype = self-test category / v0.1 category; family = SE / topic / v0.1.

## Analysis
Per reader (primary 1.7B = R-A..R-D pooled; Gemma = R-E; 4B = R-F + R-G): tercile conversion rates per continuous feature (terciles on the
reader's rows), top-vs-bottom difference with item-cluster bootstrap (B 2000, seed 11, 2.5/97.5 pct); binary features: rate(1) - rate(0) with the
same bootstrap; logistic regression of conversion on the standardized continuous features + binaries (ridge 1.0, numpy IRLS), coefficient CIs by
the same cluster bootstrap; 1.7B vs 4B slope difference per feature (bootstrap of the coefficient difference on the union, item clusters).
Ceiling per feature (1.7B): (rate_best_tercile - rate_worst_tercile) x n_worst-tercile rows of R-A x (mean U converted - mean U unconverted
item rows of R-A) / 180.

## Verdict (from the hypothesis, unchanged)
KILL if no feature has a 1.7B top-vs-bottom tercile (or binary) conversion difference >= 10 pp with a CI excluding 0, or if the best feature's
projected ceiling is < 0.03 U on the 180. Separately: if the 1.7B and 4B slopes are equal (difference CI covers 0) for the best feature,
report 'reading capacity, not chunk form'. Otherwise PASS (chunk form lever) with the top 3 features by |tercile difference|.
Dev sets only (self-tests, bench v0.1 public ids); no blind/, no rnd/veil, no bench/v0.4.
