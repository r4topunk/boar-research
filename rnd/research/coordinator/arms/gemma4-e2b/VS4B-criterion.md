# GEMMA-VS-4B criterion (frozen 2026-10-21 before any generation; MEASUREMENT, no pass/fail clause)

TL;DR: how much of the Qwen3-4B's gain over Qwen3-1.7B does Gemma 4 E2B capture on MAIN 97 K0? One new run: Qwen3-4B-Instruct-2507 Q4_K_M as a weight-only swap on the LITEPACKS mini tree, seed 42, same requests as the Gemma stage-2 / confirm runs. Nothing here changes the GEMMA4-E2B stage-2 verdict (FAIL, stage2/verdict.json) or any product decision; numbers are reported as measured with the reading rule below.

## System under test
- 4B = Qwen3-4B-Instruct-2507 Q4_K_M (shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf, sha256 3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597 = the adapter's own "qwen3-4b-instruct-2507-q4km" entry, the engine's default model). Selection = the same mechanism as the Gemma arm: patch vs4b-engsamp.patch (sha256 485feceaec4b37d2aa21d64129c1e92716a4e479c97f4f82e235e954213c1c7b) points the 1.7B id's MODELS entry at the 4B file and keeps the catalog sizeBytes at the 1.7B value, so the compact tier, prompts, declines, retrieval and the warning line are byte-identical to the 1.7B / Gemma path and only the weights differ. Engine sampler unchanged (0.7/40/0.95/0.05, health 0), seed 42, --reasoning off (the instruct 2507 model has no thinking mode). No sampler is invented.
- Not measured: the 4B on its own product tier (answerTier default, non-compact prompts/declines); this is a model-only comparison at the lite tier.
- Run: `CRITERION=arms/gemma4-e2b/VS4B-criterion.md bash lp-screens/tools/run_arm.sh gemma4-e2b-vs4b K0 main arms/gemma4-e2b/vs4b-engsamp.patch` (arms/gemma4-e2b-vs4b is a symlink to gemma4-e2b/vs4b), control lpctl-K0-main-s42 (judgment reuse for byte-identical answers only). run_arm.sh sha256 3285c0236f3040bfb749717312ced1be8baa6e7c69a27776b1f89dfd3ce535b0, agg_run.py sha256 7fc23c004008d3973a97192c255df020b578a7d98326a260ba5aa616701b22d2. Generation on the mini through the gen1/gen2 slot lock.
- Judge: Haiku 5.5-low, judge.v1-low, both orders, N = 4 shards (run_arm.sh unchanged). Dev set MAIN 97 (lp-screens/main-97.ids sha256 9664d81fdf182603617d31d75b34eaa8fcb1eeb5f0fa87e68352e1fe09d2a462).

## Comparison rows (existing, not regenerated)
1.7B s42 lp-screens/control/aggregates/lpctl-K0-main-s42.json; 1.7B s43 gemma4-e2b-confirm/runs/c43; Gemma s42 stage2/aggregates/gemma4-e2b-eng-K0-main-s42.json; Gemma s43 gemma4-e2b-confirm/runs/g43.

## Sanity (run void and repeated once if violated)
97/97 traces, 0 error rows, 0 generation_failed, runtime.versions["model.sha256"] = 3605803b... on 97/97, 0 reasoning tokens, >= 10 answers differ from lpctl-K0-main-s42.

## Reported (tools/vs4b_report.py, sha256 b557ccb868de02372f23c323a71d75a8a9cbb07ba99a096e6419523fd534d8c1; B 2000, seed 11, items resampled)
dU with paired CI for 4B - 1.7B (s42), 4B - Gemma s42, 4B - Gemma s43 (cross seed, item-paired); CE-unwarned counts and dCEu (CI); declines, warned, refused R; default-mode U delta; U on items both sides show (neither refused in default mode); changed answers; answer/prompt tokens (live items) and mini wall per item (mean, p50; includes slot contention); F42 = dU(Gemma - 1.7B) / dU(4B - 1.7B) at seed 42 and Fpool (Gemma and 1.7B pooled over seeds 42 + 43, 4B seed 42), ratio CI over item resamples with the share of resamples whose denominator <= 0.

## Reading rule (pre-registered)
1. 4B vs 1.7B: CI low > 0 -> "the 4B is measurably better than the 1.7B on MAIN K0 (Haiku)"; CI includes 0 -> "no measurable 4B gain on this set", and F is then reported but NOT interpreted.
2. 4B vs Gemma (s42 and s43 rows): CI low > 0 -> "4B better than Gemma"; CI high < 0 -> "Gemma better than 4B"; else "not distinguishable on this set".
3. F (only when rule 1 reads "measurably better"): point >= 0.5 with CI low >= 0.5 -> "Gemma captures most of the 4B gain"; point >= 0.5 with CI low < 0.5 -> "Gemma captures about half or more, CI wide"; point < 0.5 -> "Gemma captures less than half". Fpool is the headline when both seeds exist.
4. One 4B seed: per the seed-noise rule, a one-seed delta < 0.05 is not a robust ordering; the report says so beside every one-seed 4B number.

## Budget
calls_cap: Haiku 200 / Opus 0
(97 items x 2 orders = 194 upper bound; byte-identical answers reuse control rows. Combined with GEMMA-PACKS (PACKS-criterion.md) the two tasks spend <= 450 Haiku calls. 0 paid API.)
