# FTDATA-REJ: sentence-level rejection pass over ftdata-1k (2026-10-07). Criterion FTDATA-REJ-criterion.md, sha a9136d94… (verified OK before and after)
Input ftdata-1k.jsonl sha 1df13cc68ec11d98… (verified, unchanged), 982 passing rows. Tool tools/reject_1k.py (new). Verifier `claude -p --model sonnet --effort low` (resolved claude-sonnet-5-5), tools disabled, no MCP/settings, API-key/gateway env stripped. Prompt rej-prompt.txt sha 0901fb37e0549385… (frozen before any call).

## Calibration (stop rule; 20 burnt ids of review-sample-20.md; 14:29–14:31) → PASS
42 flagged claims → 38 distinct sentences (calibration-map.json, written before any call). Recall **36/38 = 0.947** (bar ≥ 0.70); false-flag on the 4 clean
examples **4/41 = 0.098** (bar ≤ 0.25). Misses: 0137 s9 (Avise join), 0911 s5 ("including the 2015 …"). Verifier is stricter than the reviewer: 23 extra U/C on the 16 flagged examples.

| id | sents | flagged | hit | extra U/C | id | sents | flagged | hit | extra U/C |
|---|---|---|---|---|---|---|---|---|---|
| 0112 (clean) | 12 | 0 | 0 | 3 | 0581 | 11 | 2 | 2 | 4 |
| 0137 | 10 | 1 | 0 | 3 | 0686 (clean) | 9 | 0 | 0 | 1 |
| 0160 | 10 | 2 | 2 | 1 | 0741 | 11 | 1 | 1 | 0 |
| 0171 | 10 | 1 | 1 | 2 | 0744 | 12 | 1 | 1 | 1 |
| 0200 | 11 | 2 | 2 | 4 | 0794 (clean) | 12 | 0 | 0 | 0 |
| 0316 | 10 | 2 | 2 | 0 | 0827 | 12 | 1 | 1 | 0 |
| 0330 | 10 | 3 | 3 | 1 | 0841 (clean) | 8 | 0 | 0 | 0 |
| 0456 | 8 | 6 | 6 | 0 | 0911 | 11 | 3 | 2 | 0 |
| 0527 | 12 | 7 | 7 | 1 | 0979 | 8 | 1 | 1 | 3 |
| 0557 | 7 | 2 | 2 | 1 | 0571 | 9 | 3 | 3 | 2 |

## Pass (14:31–15:51, 80 min wall; sum of call time 3,850 s, median 3.47 s/call)
| Measure | Value | Bar |
|---|---|---|
| Kept (≥ 100 words left AND sentence 1 survived) | **632/982** | ≥ 600 → MET |
| Kept AND frozen fidelity_filter_1k pass (120-word floor) | 538/982 (94 kept have 100–119 words → too_short; 0 other filter failures) | see deviation 1 |
| Dropped: sentence 1 deleted / < 100 words / both | 269 / 182 / 101 (350 dropped) | — |
| Median words, kept: before → after | 185 → **152** (min 100, max 200); all 982 after: 137.5 | report |
| Sentences deleted | **2,592/9,684 = 26.8 %** (U 2,576, C 16 in 15 examples); within kept 18.3 % | report |
| Examples with 0 deletions | **122/982 = 12.4 %** (all 122 kept) | report |
| Verifier calls / malformed / retries / 429s / failures | 1,002 (20 calib + 982) / 0 / 0 / 0 / 0; web requests 0 | cap ≤ 1,010 |
| Kept by pack / qtype | enwiki 341/511, crypto 102/138, usgov 95/136, voyage 94/197 / fact 196, expl 160, how-to 149, comp 127 | — |
| Strict review (review-sample-20b.md, seed 50, burnt 20 excluded) | **PENDING (separate reviewer)** | ≤ 2/20 |

Sample 20b ids: 0110 0134 0153 0247 0301 0358 0362 0387 0424 0501 0506 0520 0522 0564 0591 0798 0834 0894 0922 0998 (words 108–191; 3 have 0 deletions; 3 are 100–119 words).
Outputs: ftdata-1k-rej.jsonl (sha 212626341ab18373…; original fields + sentences_total, sentences_deleted, deleted_nos, labels, answer_rej, words_rej, kept,
filter_rej_pass, filter_rej_reason, verifier_ok), rej-raw.jsonl (checkpoint), rej-calib.jsonl, calibration-map.json, rej-run.log, rej-calib.log, review-sample-20b.md (sha 272b74df…).

**Deviations / implementation choices**
1. Keep rule vs filter: criterion keeps at ≥ 100 words, the frozen 1k filter floors at 120. `kept` = 100-word rule; if "filter pass must hold" is a keep condition, kept = **538 < 600** (bar missed). Coordinator's reading.
2. Verifier input = passages + numbered sentences only (no question, per criterion): restated question premises are judged without the question (0200 s1 marked U), likely inflating the 269 sentence-1 drops.
3. Split = 1k trim rule unchanged, quirks included: "Rd."/"ed."/"Whoomp!" split mid-sentence; single-letter initials ("B.", "d.") are not ends (0330 s9 spans a paragraph). Fragments are deleted as units.
4. Prompt lists the rubric categories (criterion + REVIEW-20 conventions) with NO example phrases from the 42 flagged claims, to avoid tuning to the calibration set.
5. The 20 calibration ids were re-verified in the full run (fresh calls; 196/203 labels agree with the calibration call); the run's labels were used.
6. Rebuild keeps the original whitespace (paragraph breaks fixed after a dry build at n = 302, before the final build; labels unaffected). Malformed after retry → not kept (never fired).
7. 0330 claim "to the eye … single star. When resolved, … two components" spans s5–s6; mapped to s5 (one sentence per claim).

**UNKNOWN**
- Faithfulness after deletion: pending the separate strict reviewer (REVIEW-20b.md). Calibration recall 0.947 was measured on the set the rubric was written from.
- Completeness loss from deletion is unmeasured until LORA-DIAG's held-out stage; the verifier over-deletes vs the reviewer (false-flag 0.098 on clean examples, 23 extra U/C).
- Coherence: deletion can leave dangling referents (ft1k-0005: "There, at 17, …" after "The restaurant proved decisive." was deleted). Not measured. Pack skew: voyage keeps 48 % vs enwiki 67 %.

## Verdict (coordinator, 2026-10-07 15:56; criterion a9136d94…, read once, strict reading of the keep rule)
Kept: 632/982 by the 100-word rule, **538/982 with the frozen filter's 120-word minimum also required** (the criterion requires both; the 100/120 inconsistency is the coordinator's drafting error and is read strictly, no rescue) → kept bar ≥ 600 **FAIL**. Strict review REVIEW-20b.md (seed 50, 20 fresh ids): **11/20** examples with ≥ 1 unsupported claim (261 claims: 246 S / 15 U / 0 C; 13 of 15 borderline; 2/20 non-borderline); bar ≤ 2/20 FAIL, PARTIAL band 3–5 missed. Side effects of deletion: 3/20 dangling text, 8/20 omit a covered part of the question, 1/20 no longer a direct answer, 269/982 lost sentence 1; median words 185 → 152. **FTDATA-REJ = FAIL.**
Line decision (coordinator, reversible, data kept): the grounded-reading fine-tune DATA line is CLOSED for now. Scale: teacher 16/20 → teacher + sentence rejection 11/20 → human CLAPnq 6/20 under the same strict rubric; the LoRA's literature-expected effect is +0.1…+0.4 completeness with a Q4 erasure risk, for ≈ 2 mini-days; the only lever that reaches the bar is the deep tier. Reopen only with r4to (option (c) quote-then-answer pilot, or a human-relative bar pre-registered against 6/20). arms/loradiag stays a draft.
