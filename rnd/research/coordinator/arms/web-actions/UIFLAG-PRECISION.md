# UIFLAG-PRECISION (2026-10-21): a UI-only flag ("no kept source OR no [n] in the answer") is a weaker error signal than our five-rule line on every tier

0 LLM, 0 judge calls, 0 generation, 0 paid, 0 phone. Script tools/uiflag.py (python3 -I) -> aggregates/uiflag.json (sha256 c16036a9...). Descriptive re-cut, no frozen criterion, no decision.
Rows and labels reused unchanged: HON-7 frame (MAIN 97 dev, desktop K0 s42, one run; hon67.py rows via cv5_per100.py's loader), LITEPACKS 1.7B K0/K1 (MacBook, MAIN + ST-SE + ST-cand; warncal_showanyway.py rows).
UI flag = model-generated answer (outputTokens > 0) AND (retrieval.kept = 0 OR no `[n]` in the raw token stream, i.e. before our citation-support check strips citations). Our line = answer starts with the warning text (five rules, switch on).
CE = correctness <= 1.5, correct >= 4; declines excluded (same population as HON-7). Wilson 95 % CIs.

## Main table: Haiku 5.5-low judge.v1 (census), MAIN 97 dev, desktop, one run
| tier | signal | flagged / n (coverage) | P(correct \| flagged) | P(CE \| flagged) | recall of CEs |
|---|---|---|---|---|---|
| Qwen3-1.7B | UI flag | 59 / 90 (0.66) | 0.15 (0.08-0.27) | **0.29** (0.19-0.41) | 0.74 |
| Qwen3-1.7B | our line | 39 / 90 (0.43) | 0.08 (0.03-0.20) | 0.41 (0.27-0.57) | 0.70 |
| Gemma 4 E2B | UI flag | 52 / 88 (0.59) | 0.13 (0.07-0.25) | **0.21** (0.12-0.34) | 0.85 |
| Gemma 4 E2B | our line | 32 / 88 (0.36) | 0.03 (0.01-0.16) | 0.34 (0.20-0.52) | 0.85 |
| Qwen3-4B (compact tier) | UI flag | 46 / 90 (0.51) | 0.20 (0.11-0.33) | **0.20** (0.11-0.33) | 0.56 |
| Qwen3-4B (compact tier) | our line | 40 / 90 (0.44) | 0.10 (0.04-0.23) | 0.28 (0.16-0.43) | 0.69 |
Our-line rows reproduce HON-7 exactly (precision 0.41 / 0.34 / 0.275, recall 0.70 / 0.85 / 0.69).

## Where the difference comes from (Haiku)
- Rows the UI flag adds over the line (UI and not line): 1.7B 27 (P(CE) 0.22, P(correct) 0.22), Gemma 22 (P(CE) 0.00, CI 0-0.15; P(correct) 0.27), 4B 20 (0.15 / 0.30). These are mostly answers the model wrote without citing, and they err at about the unwarned rate (MAIN unwarned LLM answers 0.17, WEB-ACTIONS-B), so they add coverage, not error information.
- Rows the line has and the UI flag misses: 1.7B 7 (false-claim and all-citations-removed cases: the raw stream still carries `[n]`).
- Non-health only: UI-flag P(CE) 1.7B 0.31, Gemma 0.22, 4B 0.21 (same picture).
- A naive flag that does not check "model-generated" would also mark 14 of 97 deterministic answers per tier (no `[n]` in calculator / card / facts answers). His UI must skip deterministic-layer answers.

## LITEPACKS 1.7B replication (Haiku, MacBook, one run)
| arm | UI flag: coverage, P(CE \| flag) (CI), P(correct \| flag) | our line: coverage, P(CE \| line), P(correct \| line) |
|---|---|---|
| K0 (247 answers) | 0.66, 0.28 (0.22-0.35), 0.13 | 0.50, 0.41 (0.33-0.50), 0.07 |
| K1 (249 answers) | 0.46, 0.33 (0.25-0.42), 0.10 | 0.53, 0.36 (0.29-0.45), 0.03 |

## Opus judge.v1 (CV5-PER100-OPUS units on the same MAIN rows; shown-answer census + 20-row hidden sample per tier, unweighted, direction only)
- Flagged rows with Opus labels, correct / CE: 1.7B UI 24 rows 7 / 3 vs line 14 rows 4 / 3; Gemma UI 23 rows 6 / 3 vs line 13 rows 3 / 3; 4B UI 15 rows 5 / 0 vs line 14 rows 5 / 1. Same direction: the UI flag adds correct answers, not errors. Too few CEs for a rate.

## Reading
- One line: on MAIN 97 (Haiku, desktop, one run) the UI-only flag marks 51-66 % of model answers and about 1 in 5 (4B, Gemma) to 1 in 3.5 (1.7B) of them are confidently wrong, against 1 in 3.6 to 1 in 2.4 under our five-rule line; it keeps most of the recall (0.56-0.85).
- As a warning-line source for step 1 it is usable (status copy, no hiding). As the trigger for step 2's refuse-by-default it is not: on the 1.7B its precision 0.29 sits under HON-7's 0.30 bar, and it would hide about 2 in 3 of the 1.7B's answers.
- Caveats: our kept set (retrieval.kept, after our off-topic drop) stands in for his Done.sources, which may differ (not checked); the text is our engine's model text, not his. Dev sets, one seed, Haiku over-calls CE vs Opus (HAIKU-CAL).
