# JUDGE-V1_1B criterion (second true-zero wording; coordinator request 2026-10-21 after JUDGE-V1_1 NO-ADOPT; frozen before any call of this criterion)

TL;DR: same three checks, same ids, same bars as JUDGE-V1_1-criterion.md (sha e4369cf0...), on a wording that differs from W1 ONLY by dropping the sentence "A partial answer is scored on what it asserts." Haiku 5.5-low, 0 Opus, 0 generation, 0 paid API, dev only; never bench/v0.4, blind/ or rnd/veil.

## Wording (W3, version tag judge.v1_1c; the pre-registered eval-lib-v1_1b is NOT used)
- The pre-registered W2 (eval-lib-v1_1b) differs from W1 in more than the sentence: it adds "(this rule overrides the others)", "redirects the user to other sources", "makes no specific checkable claim that answers the question", and "Asserting nothing is not the same as being correct: correctness rewards only true claims the answer actually makes", and it KEEPS the partial-answer sentence. Per the request (keep only that change), W2 stays unrun and a new lib holds W1 minus the sentence.
- eval-lib-v1_1c/judge-core.mjs sha256 ac5092c4ddbb9857103b07be23512a09673cf5d19d2391444d28967f01e73ac3 (claude-cli.mjs = re-export, sha 093704464486208336d66dc4a89ba4ce633e34f29214ecb5292bf27d6ddd36ab). Inserted line, before "- Do not use tools.":
  "- True zero: if an answer declines, defers, says it cannot answer, or contains no checkable claim about the question, score that answer correctness = 1, completeness = 1, usefulness = 1, regardless of tone."
- Diff vs W1: the 48 characters " A partial answer is scored on what it asserts." removed; nothing else (checked: W3 system string = W1 string minus that sentence; W3 minus the rule line = judge.v1 string). judge.v1 bytes unchanged (eval-lib/judge-core.mjs sha 521f7ad3..., harness/judge.mjs sha bda1aeb5...).

## Fixed inputs (identical to JUDGE-V1_1)
- Validity: decline-30.ids x traces/fa-decline-{a,b,c}.traces.jsonl, bench v0.1.
- Consistency: v1_1/data/controls-40.tsv (sha 04b688fd...), reference = mean of the 3 existing v1 repeats; CE = correctness avg over both orders <= 1.5 (v1 majority of 3).
- Retest: v1_1/data/retest-20.ids (sha 5fc0765a...), second judgment under W3.
- Runner v1_1/tools/run_v1_1c.sh sha e739de64f06c81c76a24c6d42c6623dd3934d55c8273337bddec124e501d5095 (= run_v1_1.sh with W3 / lib v1_1c / ledger runs/calls-W3.ledger); aggregator v1_1/tools/agg_v1_1c.py sha f3b6e058f491559142628e11416f386568e427eb42f6f4b41998039165defe5e (= agg_v1_1.py with W3 handled as W1); rescore v1_1/tools/run_rescore_c.sh sha c28b807d2c659b19df72f38449bddef9801ddf6187a0ef6f44fcd11407d7edf3, v1_1/tools/agg_rescore_c.py sha 3c147ea8c5397e954997097a76ba30636ddef0d4f329786ca3333106c039f797.

## Rules (frozen; bars unchanged)
1. Validity: every variant U CI high <= 0.05 (n 30).
2. Consistency (40): mean |n_W3 - n_v1| <= 0.05 (n = (s-1)/4) AND CE flips vs v1 majority <= 2/40.
3. Test-retest (20 x 2): mean item SD (ddof 1) <= 0.0206 = judge.v1 on the same 20 ids, repeats 1-2 (computed 0 LLM before JUDGE-V1_1; v1 full-97 3-repeat SD 0.0286 is context).
4. ADOPT judge.v1_1c iff 1-3 all pass. Run order: validity; if it fails, stop (no controls). Otherwise controls + retest.
5. Only if ADOPT: re-score the 1B anchor (Qwen2.5-1.5B closed-book traces vs 1.7B K0 control lpctl-K0-main-s42, v0.1 57, both judged in full) and report U per arm, paired dU with CI (FLOOR rule 2 estimator, joint bootstrap 2000, rng 11), position ABOVE (CI low > 0) / BELOW (CI high < 0) / LEVEL, SEPARABLE (dU >= 0.05 and CI low > 0), items that went to zero; context: control rows reused for identical-text items, as FLOOR did.
6. If NO-ADOPT: stop. The ruler keeps judge.v1; declines are handled by the pre-registered decline-arm subtraction (report: v1 bare-refusal U 0.058, hedged 0.053, fluent 0.016) with its limitation named. No further wording under this criterion.

## Budget
calls_cap: Haiku 400 (+240 for rule 5 only, total <= 640) / Opus 0. Planned: validity 180 + controls 80 + retest 40 = 300; rule 5 +228.
