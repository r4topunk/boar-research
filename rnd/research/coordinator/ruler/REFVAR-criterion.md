# REFVAR (RJ4-REFVAR) criterion: reference-denominator variance pilot of the R3 reference protocol (frozen 2026-10-21 before any call)

Hypothesis: coordinator/ruler/hypotheses-2026-10-21.json id RJ4-REFVAR. Spec: RULER-SPEC-v1-2026-10-20.md §3.2 (R-D2: frontier model + live web, uncapped, sources kept, mean over draws/families, never best-of-two).
Items: 20 DEV ids of bench v0.1 (refvar/refvar-20.ids, sha256 2bf646fdb3f8ed0ac4c12033b298374ba2346e5aa58405221bb6c6c7f32fd657), stratified by category (refvar/tools/select_ids.py: comparison 2, crypto 3, danger 2, explanation 4, health 1, honesty-refusal 2, reasoning 4, synthesis 1, travel 1; within a stratum ascending sha256("refvar-2026-10-21|"+id)). No blind, veil, held-out or v0.4 material is read or used.

## Generation (Opus, frozen)
- Prompt: refvar/prompts/reference.r3-pilot.md, sha256 4b2ef432aa24b09960b9d071bbbbc2b52f8e0cdacf6691514cd3e13aba1c3a2b. = reference.v1 with the 250-word cap removed ("no length limit") and the source line extended to every source used, with title and date. No mention of BOAR, the app or the bench. User turn = the bench question text verbatim.
- Model: Claude Opus (claude -p --model opus, [usage detail removed] via the shared helper cleanEnv, no API key, 0 paid API), tools WebSearch + WebFetch, fresh process per call (no shared context between draws), timeout 900 s, --max-budget-usd 8 (list-price guard, not a charge).
- Two independent draws per item: A and B (refvar/tools/gen_refvar.mjs). Stored refvar/refs/drawA.jsonl, drawB.jsonl (full text, parsed sources url/title/date, web queries, fetched URLs, usage, model id). Hard cap 44 claude calls (40 + 4 retries), each logged in refvar/refs/calls.jsonl. An item without both draws after the cap is dropped from every comparison and counted.

## Judging (Haiku, frozen)
- Judge: harness/judge.mjs judge.v1-low = claude-haiku-5-5 --effort low, pairwise rubric (correctness, completeness, usefulness 1-5), both orders, seed 7, sharded N = 4 (arms/deepthink/tools/shard_judge.sh, JUDGE_CMD = judge.mjs --refs <file>).
- Answers (existing traces, no generation): S1 = 1.7B K0 control (arms/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl); S2 = 4B K0 s42 (arms/gemma4-e2b/vs4b/traces/gemma4-e2b-vs4b-K0-main-s42.traces.jsonl), for the ranking check of the hypothesis.
- References: R_A, R_B (new) and R_v1 (boar-eval/bench/v0.1/refs/refs.jsonl, reference.v1, 250-word cap, Claude Opus + web), the latter re-judged fresh in the same session so all three share judge conditions.
- Calls: 20 ids x 2 orders x 3 references x 2 systems = 240 Haiku calls; cap 260 (reruns of failed shards). 0 Opus judge calls.

## Quantities
- Per item i, reference R, system S: s = mean over both orders of the mean rubric of the app side, sref = same for the reference side; per-item ratio r = s/sref. Declined := 0 for s (expected none on these traces; counted).
- U_S(R) = sum_i s / sum_i sref (ratio of sums, raw); floor-adjusted secondary: sum(s-1)/sum(sref-1).
- R_AB = mean of the two draws (per item: s and sref averaged over A and B, as RULER-SPEC §3.2 "mean, never best-of-two").
- CIs: paired item bootstrap, B 2000, seed 11, 2.5/97.5 pct; per-item difference also mean, SD and t 95 % CI.
- Judge test-retest baseline: R_v1 fresh vs the existing Haiku-low judgments of the same traces against R_v1 (lpctl-K0-main-s42-v01, gemma4-e2b-vs4b-K0-main-s42-v01), same 20 ids.

## Reading rules (fixed before data)
1. Draw-to-draw variance: per-item d = r(A) - r(B) for S1 (mean, SD, 95 % CI); dU = U_S(A) - U_S(B) per system with CI. ONE DRAW SUFFICES iff for both systems |dU| <= 0.03 AND the bootstrap CI includes 0 AND the 4B-minus-1.7B gap differs between A and B by <= 0.03. Otherwise R3 requires two draws averaged per family.
2. Protocol shift (uncapped r3 vs v1): dU = U_S(R_AB) - U_S(R_v1) per system with CI. SHIFT iff |dU| > 0.03 for either system OR (CI excludes 0 AND |dU| >= 0.02) OR the 4B-1.7B gap changes by > 0.03. Report direction (does the uncapped reference lower the app ratio) and whether the ranking 1.7B < 4B flips (FLIP = a ranking change under any of A, B, AB vs v1).
3. Noise context: the draw-to-draw |dU| is compared with the test-retest |dU| of rule 4; if draw-to-draw <= test-retest + 0.01, the draw variance is read as judge noise, not reference variance.
4. Test-retest: dU = U_S(R_v1 fresh) - U_S(R_v1 existing).
5. Length: words of A, B, v1 (median, IQR, min, max); Spearman rho of per-item sref and of per-item r(S1) with reference words (pooled A, B). LENGTH NORMALISER RECOMMENDED iff rho(r, words) <= -0.30 with a bootstrap CI excluding 0 AND rule 2 says SHIFT downward.
6. Key-fact disagreement (0 LLM, by reading A vs B, and each vs v1): an item is flagged iff the two texts state mutually incompatible values for a fact central to the answer (number, date, name, recommended action, yes/no verdict, false-premise call). Omissions and emphasis do not count. Reported as count/20 with the fact named per flagged item.
7. Sources: per draw count of distinct URLs, share with a date, overlap of domains between A and B (Jaccard), web searches and fetches per call.
Outputs: ruler/REFVAR-2026-10-21.md + refvar/refvar-results.json. Caveats fixed in advance: 20 items, 1 judge family (Haiku-low, same family as the writer: the same-family lift of arXiv 2609.17857 is not measured here), dev items, one judge seed, reference written by the same family as the v1 reference.
