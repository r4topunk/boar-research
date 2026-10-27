# JUDGE-V2 result (ruler T2): pointwise binary checklist judge vs judge.v1, test-retest on dev (2026-10-20)

Criterion: JUDGEV2-criterion.md, sha256 `b1fe95fc1725b1879c5dc72e9695d03f3237604348f3d9515d1264bd9f15634c` (frozen 21:49 before any scoring call). Review: REVIEW.md (one Opus reviewer; 11 findings, 9 accepted in full, 2 in part, applied before the freeze). Analysis: tools/analyze.py -> aggregates/judgev2.json.

## TL;DR
- **Verdict: NO-GO by the frozen rule.** Neither clause passes: CE-label test-retest agreement 0.966 (v2) vs 0.924 (v1), needed >= 0.974 (+4.1 points, not +5); mean item-score SD 0.0229 vs 0.0286, needed <= 0.0172 (ratio 0.80, not 0.60). judge.v1 stays the ruler-draft judge for now; v2 goes back for rework before T3.
- What v2 does better: the same item score repeats far more often (exact agreement 0.90 vs 0.50; 82/97 items identical in all 3 repeats vs 33/97), CE kappa 0.88 vs 0.82, point flip rate 5.8 % (so R = 3 under RULER-SPEC §6), 0 evidence spans failed the code check, length correlation ~0 for both judges. Where v2 is worse: when it flips, it moves by a whole point (1/K ≈ 0.25), so the mean SD barely improves. v1 averages 6 integer ratings per item (3 dimensions x 2 orders), which smooths its score.
- Power on n 97 (judge noise only, 80 %, two-sided 0.05): MDE for a paired U difference = **v1 0.014 U (3.4 % of U 0.407)**, **v2 0.027 U (12.3 % of U 0.220)**. With R = 3 repeats: 0.008 / 0.016. On a common floor-free [0, 1] scale: v1 0.016, v2 0.025 per judgment. v1 spends 2 calls per judgment and v2 spends 1, so at equal calls (v2 with R = 2: about 0.0175) the two are close. v1's U also includes the 1-5 rubric floor, which shrinks its relative MDE.
- Validity differs more than stability does: v1 majority CE vs v2 aggregate CE agree on 77/97 items (kappa 0.42; 12 both, 16 v1-only, 4 v2-only). v1 calls an answer a CE when it is vague or wrong outside the key points. v2 calls one only when a key point is contradicted. The separate false-fact flag catches most of v1's extra CEs (example 1), but adding it to CE lowers v2's own test-retest to 0.931 (post hoc, not in the decision).

## Test-retest (3 repeats each, the same 97 cached mini K0 MAIN control answers, Haiku 5.5-low)
| Metric | judge.v1-low (pairwise, both orders, 1-5) | judge.v2 (pointwise checklist) |
|---|---|---|
| Calls per repeat | 194 | 97 (+ 97 reference, once) |
| CE count per repeat | 27 / 31 / 27 | 17-19 (19 / 17 / 17) |
| **CE-label pairwise agreement** | 0.924 | **0.966** (needed 0.974) |
| CE unanimous (3/3) | 0.887 | 0.948 |
| CE Fleiss kappa | 0.817 | 0.885 |
| Exact item-score agreement, pairwise | 0.502 | 0.897 |
| Item score unanimous (3/3) | 0.340 (33 items with SD 0) | 0.845 (82 items with SD 0) |
| **Mean item-score SD**, [0, 1] scale | 0.0286 (median 0.024) | **0.0229** (median 0; needed 0.0172) |
| U per repeat | 0.4055 / 0.4050 / 0.4109 (SD 0.0033) | 0.2184 / 0.2226 / 0.2194 (SD 0.0022) |
| MDE80, paired dU, 1 judgment per arm | 0.014 (3.4 % of U) | 0.027 (12.3 % of U) |
| MDE80, R = 3 (approximation) | 0.008 (2.0 %) | 0.016 (7.1 %) |
| Spearman(answer length, score) | -0.02 | +0.02 |

U is not comparable across the two judges. v1 is a ratio of 1-5 means with a floor of 1. v2 is a ratio of key-point shares, with the reference at mean s 0.913 and 0 reference items at s = 0. The v2 aggregate U (strict majority of 3) is 0.222.

## v2 diagnostics
- Point flip rate 0.058 (399 points, mean K 4.1) -> **R = 3** by RULER-SPEC §6.
- Evidence spans: all found (300 non-ABSENT verdicts), 0 downgrades. 0 class mismatches. answer_class decline 23/291 rows; the trace declined none.
- False-fact flag: 25 / 19 / 21 items per repeat, 22 items by majority. The CE + false-fact variant has test-retest 0.931, below CE alone, which supports keeping the flag separate (REVIEW F1).
- Extraction: 97/97 items, 27 of 399 points contain a capitalised term or number found in neither the notes, the reference nor the question (REVIEW F6c; logged, not fixed). One of these drives example 3.
- Items whose v2 score moved across repeats (15): vit-hum-003, lan-rsn-001, vit-trv-004, vit-hlt-001, vit-hlt-003, lan-ref-002, lan-exp-004, trv-002, st-qa-cooking-se-001/016/019, st-qa-money-se-008/011/015/018.

## v1 vs v2 CE (majority of 3 vs strict-majority aggregate)
| | v2 CE | v2 not CE |
|---|---|---|
| v1 CE | 12 | 16 |
| v1 not CE | 4 | 65 |
Agreement 0.794, kappa 0.425. The 20 disagreements are in aggregates/judgev2.json; below are the first 3 by sha256(id).

## Three disagreements
1. **vit-cry-005**, "What is the difference between Privacy Pools and Tornado Cash?" The answer says Privacy Pools "provide a more user-friendly interface for creating and managing privacy-focused transactions". v1: CE in 2 of 3 repeats (correctness 1.0 / 1.5 / 2.0). v2: not CE. All 4 key points are ABSENT (zero-knowledge proofs, association sets, sanctions, authorship), so s = 0 and nothing is CONTRADICTED. The false-fact flag fires in all 3 repeats on the "user-friendly interface" claim. Reading: v2 gives the answer the score it deserves (0), but under the spec CE rule a wrong answer to a different point is not a CE. This is the main source of v1-only CEs.
2. **vit-cry-003**, "What does EIP-4444 history expiry change for node operators, and how much disk does it save?" The answer describes "pruning historical data older than the consensus-layer block retention window" and gives no figure. v1: CE in 2 of 3 (correctness 2.0 / 1.5 / 1.5, at the 1.5 threshold). v2: s = 0, no point contradicted, false fact flagged ("consensus-layer" where EIP-4444 is about the execution layer). Same pattern as example 1. It also shows v1's CE flipping at the threshold.
3. **lan-cmp-001**, "Does Brazil have more people than Russia?" The answer is "Yes … Brazil 214.2 million (2026) vs Russia 146.1 million (2025)", from the offline Wikidata table. v1: not CE (correctness 3.5 / 3.5 / 4.0). v2: CE in 3 of 3, because the extracted point "Brazil has roughly 203 million people" is marked CONTRADICTED by 214.2 million. The answer is right. The CE comes from a dated census figure that extraction put into the checklist, a time-sensitive number with no range. Reading: a false CE caused by the checklist, not by the judge. The judge was stable (3/3).

## What to do with it (not decided here; for the coordinator)
- Rework v2 before T3, if it is wanted at all:
  - (a) Score items on a finer grain: aggregate over R and publish the mean of PRESENT shares instead of a strict-majority vote. This targets the SD clause directly.
  - (b) Checklist-writing rule for v0.4-style points: numbers carry an explicit tolerance or a date ("about 200-215 million as of 2025"), to remove example-3 CEs.
  - (c) Decide whether the ruler's CE should include a majority false-fact flag. That is a validity choice against the spec (§3.6) and costs about 3 points of test-retest.
  - Any rework is a new criterion. No rerun of this one.
- judge.v1 numbers keep the noise figures above. The v1 CE label is unanimous on 88.7 % of items, and a single v1 judgment detects dU ≈ 0.014 at n 97 from judge noise alone. Generation noise is not in either MDE.

## Budget and provenance
- Haiku calls: **881 of the 1200 cap**: smokes 8, extraction 97, v2 app 291, v2 reference 97, v1 repeats 2 and 3 388. Ledger: runs/calls.ledger. 0 Opus, 0 paid API, 0 retries. MacBook `claude -p`.
- Files: data/ (inputs + kp-dev97.jsonl, the cached extraction), v2/app-r{1,2,3}.jsonl, v2/ref-r1.jsonl, v1/rep{2,3}-*.judgments.jsonl (repeat 1 = lp-screens/control/judgments/lpctl-K0-main-s42-*), aggregates/judgev2.json, runs/ (logs, smokes).
- Dev only: bench v0.1 public 57 + qa-cooking-se 20 + qa-money-se 20. No v0.4 item, blind/ or rnd/veil file was read or judged. Only the v0.4 checklist field type was read (list of strings).
- Post-freeze edit (output only): tools/analyze.py no longer copies the question text into aggregates/judgev2.json (the rnd pre-commit blind-plaintext hook blocks pretty-printed id + question). No metric or rule changed; the frozen sha 70a82260… is the pre-edit file.
- Deviation: the brief said two v1 repeats already existed. Only one full 97-item v1 judgment existed (the 37-item screen judgments are partial), so two new v1 repeats were run to get 3 vs 3.
- UNKNOWN: human-labelled validity of either judge's CE (RULER-SPEC §6 calibration is not done); the decline-variant and padding checks (REVIEW F5 and validation) are deferred; the cross-family judge is not tested.
