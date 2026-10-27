# JUDGE-V2: does a pointwise binary key-point checklist judge (judge.v2) measure more stably than judge.v1? (frozen 2026-10-20, coordinator / ruler T2)

## Tags
Tags: blocker
Ruleset: 30
<!-- blocker = measurement / infrastructure arm for the ruler (RULER-SPEC-v1 §6, T2): no engine change, no generation, judge calls only. -->

## Question
The ruler (RULER-SPEC-v1-2026-10-20 §3.1, §6) needs a judge whose verdicts repeat. judge.v1 (pairwise vs the reference, both orders, 1-5 scales) re-judged on identical text changed correctness on 13/37 items (SCREENS.md). Is judge.v2 (one answer per call, per key point PRESENT / ABSENT / CONTRADICTED with a code-checked evidence span, answer class answer / decline, a separate false-fact flag, score derived from the checklist) stable enough to replace it in the ruler draft? Measurement only, dev data only; nothing here touches bench v0.4 items (only its `checklist` field format was read: list of 3-6 strings).

## Fixed inputs
- Answers: the cached mini K0 MAIN control (arms/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl, 97 rows, 0 declined, 0 errored), ids arms/lp-screens/main-97.ids (sha256 9664d81f…2a462): v0.1 public 57 + qa-cooking-se 20 + qa-money-se 20. Built by tools/build_inputs.py into data/ (items-dev97.jsonl sha256 1eb14e34…4f6f4a5650, answers-K0main.jsonl 694b1ef8…29b2f5c, answers-ref.jsonl 06c0fbe2…26a3e18c). No new generation.
- judge.v1: judge.v1-low = harness/judge.mjs unchanged, Haiku 5.5 (claude-haiku-5-5) --effort low, both orders, N = 4 shards (deepthink/tools/shard_judge.sh), exactly as lp-screens run_arm.sh step 4. Repeat 1 = the existing control judgments (lp-screens/control/judgments/lpctl-K0-main-s42-*.judgments.jsonl); repeats 2 and 3 = tools/run_v1.sh 2|3 (new). The 37-item screen judgments are not used (partial).
- judge.v2: boar-eval/harness/judge-v2.mjs (sha256 and prompt shas in the freeze block below; prompts as revised after REVIEW.md), Haiku 5.5 --effort low, one call per (item, repeat), checklist order permuted per (id, repeat), app warning line stripped and blind() applied. Repeats 1-3 on the app answers (v2/app-r{1,2,3}.jsonl); reference answers judged once (v2/ref-r1.jsonl) for the U denominator.
- Key points: all 97 dev items lack a `checklist`; key points come from ONE frozen extraction prompt (EXTRACT_SYSTEM in judge-v2.mjs; Haiku 5.5 --effort medium; input = question + the item's `rubric` author notes + the frozen reference answer), run once, cached in data/kp-dev97.jsonl (sha recorded in JUDGEV2.md after extraction; never re-extracted).

## Formulas (judge.v2; implemented in judge-v2.mjs scoreRepeat / aggregate)
- Evidence check (code, F9): a PRESENT or CONTRADICTED verdict whose evidence span is not found in the answer (normalised substring, or >= 80 % of the span's words of >= 3 letters) becomes ABSENT.
- Per repeat: s = #PRESENT / K (CONTRADICTED and ABSENT count 0); if the app trace declined, s = 0, CE = false, no call (true zero; not triggered here: 0 declined).
- Confident error per repeat: CE = trace not declined AND >= 1 point CONTRADICTED (RULER-SPEC §3.1 x, §3.6; the judge's answer_class does not gate it).
- False-fact flag (separate, never in CE or s): ff = >= 1 false_facts entry whose quote is found in the answer.
- Over R repeats (ruler use, reported here for R = 3): per point the category of a strict majority, else ABSENT; s = #majority-PRESENT / K; CE = some point majority-CONTRADICTED; ff = flagged in a strict majority of repeats.
- U (either judge) = Σ s_app / Σ s_ref over the 97 items (v1: 1-5 means of both orders, pairwise reference scores; v2: reference judged by v2, repeat 1).

## Metrics (tools/analyze.py, 0 LLM)
For each judge over its 3 single-repeat judgments of the same 97 answers:
1. Exact score agreement: mean over the 3 repeat pairs of the share of items with identical item score (v1 item score = mean of the 3 dims over both orders; v2 = s); also unanimity (all 3 equal).
2. CE-label agreement (**primary**): mean over the 3 repeat pairs of the share of items with the same CE label; also unanimity and Fleiss' kappa.
3. Item-score SD (**primary**): mean over items of the sample SD (ddof 1) over the 3 repeats of the score normalised to [0, 1] (v1: (s - 1) / 4; v2: s).
4. U per repeat and its SD; MDE (80 % power, two-sided 0.05) for a paired U difference on n 97 from judge noise alone: SE = sqrt(Σ_i 2 σ_i²) / D (σ_i² = variance over repeats of the item's raw score, D = mean U denominator), MDE = 2.80 SE, absolute and relative to U; also the R = 3 version (SE / sqrt 3, approximation). Generation noise is not included (same for both judges).
5. v1 vs v2 CE: v1 majority CE (>= 2 of 3) vs v2 aggregate CE; 2x2 table, agreement, Cohen's kappa; 3 disagreement examples (first 3 by sha256(id)) quoted in JUDGEV2.md.
6. Diagnostics (no decision): v2 false-fact flag counts, evidence downgrades, class mismatches, extraction points with imported terms; v2 point flip rate (share of (item, point) pairs not unanimous over 3 repeats; sets R for the ruler: R = 3 if <= 10 %, else 5), evidence-quote found rate, answer-class counts, false-fact and contradicted item counts per repeat, Spearman(answer length, score) per judge (verbosity check), reference mean s and items with s_ref = 0.

## Decision rule (stated before any scoring call)
GO (adopt judge.v2 for the ruler draft) iff
- (a) v2 CE-label pairwise agreement >= v1 CE-label pairwise agreement + 0.05, AND
- (b) v2 mean item-score SD <= 0.6 x v1 mean item-score SD,
- sanity (else VOID, not NO-GO): v2 CE prevalence (mean CE count per repeat / 97) >= 0.05 (a judge that never says CE agrees with itself trivially), 97/97 ok rows in every repeat, 97/97 key-point rows.
Otherwise NO-GO: judge.v1 stays and v2 is reworked before T3. No rerun to rescue a NO-GO; a prompt change after this freeze is a new criterion.

## Power
expected_delta: n/a (measurement arm; the decision is on agreement and SD ratios, not on a U delta)
n: 97 items x 3 repeats per judge
seeds: 1 (answers fixed; judge repeats are the replication)
mde: computed by this arm (metric 4)
slice: none (full MAIN 97)
l1_futility: n/a
split: by set (v01 / self-tests) reported, no decision

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: n/a (measurement arm)
bar_ceiling: n/a
launch: blocker tag
transfer: n/a; the v0.4 ruler runs use the items' own checklists, so the extraction step is dev-only

## Budget (RULE 29)
wall_cap: 2 h (MacBook)
calls_cap: Haiku 1200 / Opus 0
planned: smokes 8 (runs/smoke, runs/smoke2; before the freeze, not used) + extraction 97 + v2 app 3 x 97 = 291 + v2 ref 97 + v1 repeats 2 x 194 = 388 -> 881 (ledger runs/calls.ledger; judge-v2.mjs and run_v1.sh refuse once the ledger reaches 1200)
smoke: 2 dev items, extraction + 1 judge call each (runs/smoke/, done 2026-10-20 before the review)
kill_if: any rate limit twice in a row (stop, resume later), or ok rows < 97 after one resume
checkpoint: after v2 repeat 1 (parse rate)

## Precheck
token_projection: n/a / token_budget: n/a
disk_peak_gib: n/a
off_baseline: n/a
call_pattern: Haiku extraction 97, then judge.v2 3 x 97 + 97 ref (concurrency 4), then judge.v1 2 x 194 (N = 4 shards)
lane: judge
opus_clause: none
wall_cap_h: 2
parallelism: 4
run_type: judge

## Review
One independent Opus reviewer (REVIEW.md) checked the prompts for leaks, verbosity bias and refusal handling before this freeze; accepted edits are in the frozen judge-v2.mjs (see REVIEW.md "Applied").

## Freeze block
Frozen 2026-10-20 21:49 -0300 before any scoring call (8 smoke calls spent, not used).
```
judge-v2.mjs prompt/version: {"judgeVersion":"judge.v2","judgePromptSha":"3595d696549c9e397b04239fbc52c6d03d6b3979e9a612b6d4231e67a74b6e36","kpVersion":"kp.v1","extractPromptSha":"2f36ce39c1fe803dee1df7857078e9e6bc97451c57ca3b0aa35d765f20037e8b"}
c283a1bc869d49ed56bab0bf342bb76506062ed23ed1dc9a385c3eb172f17134  boar-eval/harness/judge-v2.mjs
bda1aeb5fe196b72d82c7699115e6ef13b7c516063a7198e38c00e488700fddf  boar-eval/harness/judge.mjs
521f7ad33a130e1a4b5906b9578fc78d84749fc1ad3d9e89c64600a83ac57080  boar-eval/scorers/vendor/eval-lib/judge-core.mjs
cdbdcb584f63b95384cd113956da8d482c4ea30dc5100ed02f9befa57db20694  boar-eval/scorers/vendor/eval-lib/claude-cli.mjs
70a82260429cd78570429ae6faf342253802ea034c836be83a8804b1e112aeab  rnd/research/coordinator/arms/judge-v2/tools/analyze.py
fa1f271faa90f958d4696376f70e870ee9bdef971fdf0cdbd4b721445f340208  rnd/research/coordinator/arms/judge-v2/tools/build_inputs.py
418c588f9a6ff2db049768e2a990e24d236dab04c94053d74d5872a7950b6a5c  rnd/research/coordinator/arms/judge-v2/tools/run_v1.sh
55ea168db0a22514c3802e3acce473472ddada7301ef333fe02a8261a7e82bbb  rnd/research/coordinator/arms/judge-v2/tools/run_v2.sh
1eb14e34a5231e73a105a8da83bf044d1ee7a4894e7e10423c70574f6f4a5650  rnd/research/coordinator/arms/judge-v2/data/items-dev97.jsonl
694b1ef8d79abb78caa177d66997c531ff8e7a53d60cd8b97149c345829b2f5c  rnd/research/coordinator/arms/judge-v2/data/answers-K0main.jsonl
06c0fbe29759e04871f465c8b3eda37f9ed78a541a79c8e25585342426a3e18c  rnd/research/coordinator/arms/judge-v2/data/answers-ref.jsonl
d3ccbbb061c27e75448ba0434afd10864ce0daaf46a2dc6fdb09be1a6c72914a  rnd/research/coordinator/arms/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl
db58729752e603210cd610cccfb7f2bacfc7213e8dd43fb96683df9860b17b24  rnd/research/coordinator/arms/lp-screens/control/judgments/lpctl-K0-main-s42-qa-cooking-se.judgments.jsonl
0c910b23707f2fea5cdacd8373b7bb4b8459dd30a06f43acd187a562664548f2  rnd/research/coordinator/arms/lp-screens/control/judgments/lpctl-K0-main-s42-qa-money-se.judgments.jsonl
f2d0d707592aed7d9a40a662f19729bfa0905344f25653d1ca0bbfe5dfec57a8  rnd/research/coordinator/arms/lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl
```
