# JUDGE-V1_1 criterion (ruler T2 fix for FLOOR-ANCHORS decline INVALID; frozen 2026-10-21 before any judge.v1_1 call; measurement arm, not a model screen)

TL;DR: judge.v1_1 = judge.v1 + ONE added rule line (explicit true zero). Does it make the three pre-registered decline variants score U <= 0.05 (validity) without moving ordinary answers (consistency, test-retest)? Haiku 5.5-low only, 0 Opus, 0 generation, 0 paid API, dev only (bench v0.1 + selftest qa-cooking-se / qa-money-se). Never bench/v0.4, blind/ or rnd/veil. Sources: FLOOR.md §1 (decline INVALID: correctness scores a refusal 2-3 as "not wrong"), RULER-SPEC-v1-2026-10-20 §4/§8, judge-v2/JUDGEV2.md (v1 test-retest).

## Judge versions (judge.v1 bytes untouched)
- judge.v1 = boar-eval/scorers/vendor/eval-lib/judge-core.mjs sha256 521f7ad33a130e1a4b5906b9578fc78d84749fc1ad3d9e89c64600a83ac57080 (unchanged) + harness/judge.mjs sha256 bda1aeb5fe196b72d82c7699115e6ef13b7c516063a7198e38c00e488700fddf (unchanged).
- judge.v1_1 (W1) = eval-lib-v1_1/judge-core.mjs sha256 0ac269680c8f5cb1ec57272a7d8a85dc60f7d8da48aadd72c531de039dcc7c85: re-exports judge.v1 and replaces JUDGE_SYSTEM with judge.v1's string plus this line inserted before "- Do not use tools.":
  "- True zero: if an answer declines, defers, says it cannot answer, or contains no checkable claim about the question, score that answer correctness = 1, completeness = 1, usefulness = 1, regardless of tone. A partial answer is scored on what it asserts."
- judge.v1_1b (W2, the ONE allowed second wording, pre-registered now, run only if W1 fails validity) = eval-lib-v1_1b/judge-core.mjs sha256 ea0828e1c69e14267041c8f60ae4d397dbd23d7049ef1bbe2575da41bcddf7db, same insertion point:
  "- True zero (this rule overrides the others): an answer that declines, defers, redirects the user to other sources, says it cannot answer, or makes no specific checkable claim that answers the question scores exactly 1 on correctness, 1 on completeness and 1 on usefulness. Asserting nothing is not the same as being correct: correctness rewards only true claims the answer actually makes. A partial answer is scored on what it asserts."
- claude-cli.mjs in both dirs = re-export of eval-lib/claude-cli.mjs. Rubric, schema, user prompt, blinding, order seed 7, mapping: identical. Wiring: BOAR_EVAL_LIB=<dir> node harness/judge.mjs (rows keep judgeVersion "judge.v1-low"; the true version is in each output's .version sidecar).
- Command path: v1_1/tools/run_v1_1.sh sha256 a28457f7a273d206de562f63391aa7292357bc8bb288c6de7f747ccfd7cfbe33 -> arms/deepthink/tools/shard_judge.sh, Haiku (claude-haiku-5-5 --effort low), both orders, N = 4. MacBook.

## Sets (0 LLM, fixed before any call)
- Validity: decline-30.ids (sha256 2894af52...) x traces/fa-decline-{a,b,c}.traces.jsonl (the FLOOR texts, unchanged), bench v0.1.
- Controls: 40 cached 1.7B K0 MAIN control answers (lp-screens/control lpctl-K0-main-s42, mini, dev 97), chosen by v1_1/tools/select_controls.py sha256 afa01f17998e78e8bb014291d158a79e596f0c59af6506d3caf181c87770641f from the three existing judge.v1-low judgments (repeat 1 = lp-screens/control/judgments, 2-3 = judge-v2/v1): WRONG = v1 CE (correctness avg over both orders <= 1.5) in >= 2 of 3 repeats (pool 28); CORRECT = not WRONG and mean correctness >= 3.5 (pool 26); first 20 of each by sha256(id). v1_1/data/controls-40.tsv sha256 04b688fda8d6a3c2028278a0b2a1e00bbc681cad4b09154dc9cf7761e6217d4f (29 v01, 6 qa-cooking-se, 5 qa-money-se).
- Retest: first 10 of each group -> v1_1/data/retest-20.ids sha256 5fc0765ab7c4a4989903c67882bcbc22257409ac477cf974a1ad2a25f95bd956.
- Note: the brief quoted "v1's 0.023" as the SD bar; 0.0229 is judge.v2's full-97 SD and v1's is 0.0286 (JUDGEV2.md). The bar below is v1 on the same 20 ids with the same repeat count (2), computed before any call: **0.0206** (repeats 1-3: 0.0212).

## Estimators (v1_1/tools/agg_v1_1.py sha256 5d3e7a89f26551dbe124ff5b9c731df3f96e050c5ddd7804c1d70c2d2dae2933)
- s = mean over both orders of mean(correctness, completeness, usefulness); n = (s - 1)/4; U = sum(s-1)/sum(r-1) (FLOOR estimator), CI 2000 item bootstraps, default_rng(11).
- v1 per-item reference = mean n over the 3 existing v1 repeats; v1 CE = majority of 3; v1.1 CE = correctness avg <= 1.5 in its one judgment ("CE-unwarned": 0 of these traces carry the warning line / declined flag, K0 main).

## Rules (frozen)
1. **Validity** (W1): VALID iff for each of (a), (b), (c) on the 30 ids, U CI high <= 0.05.
2. **Consistency** (W1, 40 controls): PASS iff mean |n_v1.1 - n_v1| <= 0.05 AND CE label flips (v1 majority vs v1.1) <= 2/40. Context only: each v1 single repeat vs the v1 majority/mean on the same 40.
3. **Test-retest** (W1, 20 retest ids judged a second time): PASS iff mean item SD (ddof 1, n over the 2 v1.1 judgments) <= 0.0206.
4. **ADOPT judge.v1_1 for the ruler** iff 1, 2 and 3 all pass. Validity fail -> W1 consistency/retest NOT run; W2 runs: validity on the same 90 (180 calls) + consistency on the 20 retest ids only (40 calls; MAD <= 0.05 and flips <= 1/20); no retest (cap). ADOPT judge.v1_1b iff both pass. Then STOP: no third wording, no tuning on ordinary answers, texts never edited.
5. Consistency/retest fail with validity pass -> NO-ADOPT (the rule moves ordinary answers); report and stop.
6. One judge family (Claude/Haiku). The spec's validity needs every family; a Codex pass is out of scope here and does not change these rules.

## Budget
calls_cap: Haiku 400 / Opus 0 (v1_1/runs/calls.ledger; run_v1_1.sh refuses past 400)
planned: W1 validity 180 + controls 80 + retest 40 = 300; if W1 fails validity: 180 + W2 180 + 40 = 400. 0 paid API, no generation, no phone, no mini.
