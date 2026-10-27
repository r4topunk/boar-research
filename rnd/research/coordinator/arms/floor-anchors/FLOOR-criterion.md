# FLOOR-ANCHORS criterion (RJ2-FLOORANCHORS; frozen 2026-10-21 before any generation or judge call; ruler baseline, NOT a model screen)

TL;DR: (1) do the three pre-registered decline variants score U <= 0.05 under the R4 judge (Haiku 5.5-low, judge.v1, z override off)? (2) is a ~1B closed-book arm at least 0.05 U below the 1.7B K0 control on the v0.1 57? Dev data only (v0.1); never bench/v0.4, never blind/ or rnd/veil. Sources: RULER-SPEC-v1-2026-10-20 §4/§8 (decline validity = verdict precondition), BENCH-RULER-2026-10-19 R-D7, ruler/hypotheses-2026-10-21.json RJ2-FLOORANCHORS.

## Sets
- Bench: boar-eval/bench/v0.1 (questions.public.jsonl, refs/refs.jsonl = frozen Opus+web references). Dev.
- 57 ids: arms/litepacks/data/v01-57.ids, sha256 3e6183f6518263fcb2691050d3d9dca33ee08d2fcb95d78f9240da2a2d579531 (= gemma4-e2b/phone/JUDGE-criterion.md list).
- 30 decline ids: decline-30.ids, sha256 2894af5213205fb36c0b337a34a1eb310533d819acd716a960154dcde78a6e94. Stratified by id group (prefix before the last dash; 12 groups), largest-remainder allocation of 30 over 57, random.Random(11).sample within each sorted group: vit-hum 3, lan-exp 4, lan-rsn 4, lan-cmp 3, lan-ref 3, lan-hlt 1, vit-trv 1, vit-cry 6, vit-sci 1, vit-hlt 1, trv 1, dng 2.

## Decline variants (exact texts; written once, never edited after scoring)
- (a) bare refusal, texts/a-bare-refusal.txt (sha256 148442de301c15928d84fbe472a104e2013fc48c623a0738acf23321c048a820): "I couldn't find this in the offline library, so I can't answer it." (a proxy for the APK's refusal string, which is pinned only with the v0.4 APK).
- (b) hedged non-answer, texts/b-hedged.txt (sha256 c2447cd523ca72ed00165475b3848722e9b494da7504c63d44684b76d537b92b): "It depends on your situation and on details I don't have. I'd suggest checking local sources or asking someone who knows the area well."
- (c) fluent length-matched no-content answer, texts/c-fluent-template.txt (sha256 c8ed54f1952bc53cb38c798c9f15e1f321ec3ba8c8b326ea94d61349321f7d51): a fixed ~250-word generic answer; the only per-item change is {question} -> the item's question text. Length target = v0.1 reference median over the 57 = 262 words (1,592 chars); realised on the 30: median 265 words (253-272).
- Traces: tools/mk_decline_traces.py -> traces/fa-decline-{a,b,c}.traces.jsonl (sha256 a 15d087575f182dad..., b 6f45705fff541f65..., c 4a7e7ce72b33d8bb...); answer.declined = false; no generation.

## 1B arm (closed-book)
- Model: Qwen2.5-1.5B-Instruct Q4_K_M (app catalog, iOS default; MODELS.md; already on the mini, no download), file shared-models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf, sha256 1adf0b11065d8ad2e8123ea110d1ec956dab4ab038eab665614adba04b6c3370 (verified on the mini 2026-10-21). Label: "~1B class (1.5B)"; the smallest instruct GGUF already present (Gemma-3-1B was deleted 10-16; prompt rule: prefer a present file).
- Frame: identical to the 1.7B K0 control (LP-SCREENS runner arms/lp-screens/tools/run_arm.sh, arm floor-anchors, K0, main, IDS_OVERRIDE = the 57; LITEPACKS requests seed 42, Succinct persona, cut7-headpass-x2+litepacks tree be-0cfd4a77-cut7-litepacks, LITEDECLINE_OFF=5, --reasoning off, llama-server b11010 CPU -t 4, one mini slot).
- Patch fa-1b-closedbook.patch (sha256 2f0f9085cf33611331aa98c43243619140b73111e042a86828c57c0cba8fc0d2), adapter only: (1) the qwen3-1.7b-q4km id loads the 1.5B file (sizeBytes, tier, prompts unchanged, as gemma4-e2b/vs4b-engsamp.patch); (2) closed-book: the engine's only retrieval dependency (deps.retrieve) returns [] (logged as a retrieve event n 0, closedBook true); (3) deps.facts = false (FACTS tables off). The engine's deterministic safety/emergency layers (not retrieval) stay as in the control; items answered by a non-model path (receipt modelId grounding-guard etc.) are counted and a sensitivity without them is printed (not a rule).
- Control: arms/lp-screens/control lpctl-K0-main-s42 (1.7B, K0 kit, with retrieval), v01 judgments (114 rows, Haiku 5.5-low). Two-seed sensitivity (not a rule): per-item mean with gemma4-e2b-confirm-c43 (unjudged ids reuse s42 rows, as run_arm.sh does).

## Judge
- judge.v1-low = boar-eval harness/judge.mjs, Haiku 5.5-low (claude-haiku-5-5 --effort low), pairwise vs the v0.1 reference, both orders, seed 7, N = 4 shards via arms/deepthink/tools/shard_judge.sh; z override OFF (no --floor-errored, no refusal zeroing: every answer, including the decline texts, is judged). MacBook.

## Budget
calls_cap: Haiku 320 / Opus 0
- planned: 1B 57 x 2 = 114; decline 3 x 30 x 2 = 180; total 294. 0 paid API. opus_clause: none.

## Estimator
- Per item and arm: s = mean over the two orders of mean(correctness, completeness, usefulness) of the answer; r = same for the reference (1-5 rubric). Items judged in one order only are dropped and named.
- **U** = floor-adjusted ratio of sums sum(s-1)/sum(r-1) (the spec's true-zero scale: a 1/1/1 answer contributes 0; the raw ratio sum s/sum r has a rubric floor near 0.2 and is printed beside it, never used for a rule).
- CI = 2.5/97.5 percentiles of 2000 item-bootstrap resamples, numpy default_rng(11); paired differences resample items jointly.

## Rules (frozen)
1. **Decline validity**: VALID iff for each variant (a), (b), (c) the U upper CI <= 0.05 (n 30). Any variant above -> INVALID: the judge's zero is not a true zero; T2 must change before 10-24 (candidates: checklist-only scoring of generic answers, or an explicit true-zero rule); texts are not tuned after scores.
2. **Separability**: SEPARABLE iff U(1.7B K0 s42) - U(1B) >= 0.05 AND its paired CI low > 0 (n 57). Else "not separable on dev" and the research page withdraws the separability claim for the 1B anchor.
3. Context printed, no rule: raw ratios, win/tie/loss, per-variant mean dims, the 1B-fail-like count (items with 1B s <= 2 and control s >= 4), two-seed control sensitivity, non-model-path sensitivity.
4. Haiku is one judge family (Claude); the spec's validity needs every family: a Codex pass on variant (c) is optional (r4to) and does not change these rules.
