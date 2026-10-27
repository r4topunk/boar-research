# GEMMA-PACKS criterion (N3; frozen 2026-10-21 before any generation; MEASUREMENT, no pass/fail clause)

TL;DR: does Gemma 4 E2B read packs better than Qwen3-1.7B? On the 80 candidate-pack self-tests (pack-matched under K3), compare Gemma's U gain from K0 -> K3 with the 1.7B's (difference-in-differences). The 1.7B side is reused from LITEPACKS (not regenerated). Changes no verdict or product decision.

## Set
packs/cand80.ids (sha256 3e9f9beb10c5d801e73e7618d118e0d92b09d976cca83a85ea46f1ced91a1376) = the 80 st-boar-{simplewiki-en,factbook,medlineplus-en,firstaid-en} ids of null-cal/pool/st180.ids (20 each). Dev (selftest-180). Requests = the LITEPACKS lp-K0-st / lp-K3-st requests (null-cal/tools/mkreq_pool.py, byte-identical except runId and config.arm). K0 = claim kit (crypto + wikivoyage); K3 = K0 + simplewiki v3proto, factbook, medlineplus, firstaid (sha-pinned in the requests).

## Rows
- Q0 / Q3 (1.7B): LITEPACKS traces litepacks/traces/lp-K{0,3}-st-s42.traces.jsonl + their existing Haiku judgments, aggregated with lp-screens/tools/agg_run.py (0 LLM) into packs/aggregates/q17-lp-K0-cand80.json (sha256 1653971b455461e931c730825675f6fecaf1a81992affaa1b9ac9d2f867857ac) and q17-lp-K3-cand80.json (sha256 2000fcc7c2257876865c83aa9b9837a603549be477f7040e5b5a8117fce13513); they reproduce LITEPACKS (U 0.393 / 0.462, dU +0.069). Host MacBook M1 Pro.
- G0 / G3 (Gemma, new): Gemma 4 E2B-it Q4_K_M (740185b2...), engine sampler patch gemma4-e2b-engsamp.patch (sha256 095ca9d71b6f8814bf8e77e796531936cfe9f8f85559bdde5d8ba26b4fc2b248), seed 42, --reasoning off, LITEPACKS mini tree, host mini M4. Arm name gemma4-e2b-eng (same config.arm as the screens), output root packs/ (OUT_BASE).
  - G0: `OUT_BASE=arms/gemma4-e2b/packs CRITERION=arms/gemma4-e2b/PACKS-criterion.md CTLAGG_OVERRIDE=arms/gemma4-e2b/packs/aggregates/cache-K0-cand80.json bash gemma4-e2b/tools/run_pool_k.sh gemma4-e2b-eng K0 gemma4-e2b/packs/cand80.ids gemma4-e2b/gemma4-e2b-engsamp.patch`
  - G3: the same with K3 and CTLAGG_OVERRIDE=arms/gemma4-e2b/packs/aggregates/gemma4-e2b-eng-K0-cand80-s42.json (runs after G0 is aggregated).
  - tools/run_pool_k.sh (sha256 9d5e73efcbbc1efeb406d64d139c7ad2e2a4071ac312ba0a857df3ada314b641) = null-cal/tools/run_pool.sh (sha256 e277d8c722e00c704ebcddeb0bbc376c30ade7c65d599e48ac1e1e5a73517ea5) with 2 changed lines: K3 accepted; CTLAGG_OVERRIDE sets the judgment-reuse aggregate. Judge path unchanged (shard_judge.sh, Haiku 5.5-low, judge.v1-low, both orders, N = 4).
  - Judgment reuse (harness rule: byte-identical answer text reuses a judgment, never re-judged): G0 reuses packs/aggregates/cache-K0-cand80.json (sha256 891fa19c3312a43c2e8a8da0a2dd7528774bd0ad917388c7d867268e15f95522) = null-cal/control/pool-K0.json rows (1.7B mini) with the 12 overlapping ids taken from the Gemma-eng K0 screen2 aggregate (same requests, patch, seed, host); G3 reuses G0's rows (as LITEPACKS K3 reused K0). agg_run's vs_control block of G0 is therefore not a measurement and is not reported.

## Sanity (run void and repeated once if violated)
80/80 traces per run, 0 error rows, 0 generation_failed, model.sha256 740185b2... on 80/80, 0 reasoning tokens / thought markers; G3 traces carry the 6-pack kit.

## Reported (tools/packs_report.py, sha256 71bd50d5caa60fc68acd58a8264abcdfdbfeed2581c45b5f88cec894399f3e1a; B 2000, seed 11; the 4 rows of a resampled item move together)
All 80 and per pack (20, indicative): U of Q0 Q3 G0 G3; dU_G = U(G3) - U(G0) and dU_Q with CIs; **DiD = dU_G - dU_Q with CI**; level gaps G - Q at K0 and at K3; default-mode U (R := 0) and its DiD; CE-unwarned counts and the DiD of the CEu rate; CE, declines, warned, refused R counts; prompt tokens (mean, p50, live items), output tokens, totalMs per row; changed answers G3 vs G0 and Q3 vs Q0.

## Reading rule (pre-registered)
1. DiD CI low > 0 -> "Gemma gains more from the K3 packs than the 1.7B (reads packs better)"; CI high < 0 -> "Gemma gains less"; else "no measurable difference in pack gain".
2. dU_G CI low > 0 -> "the packs help Gemma on their own topics"; else "no measurable pack gain for Gemma".
3. Per-pack slices are indicative only (n 20); no claim rests on them.
4. Caveats stated beside the number: one seed; self-tests are pack-written (an on-topic ceiling, not casual traffic); host differs between the models (1.7B MacBook, Gemma mini), which cancels inside each model's K3 - K0 difference but not in the level gaps.

## Budget
calls_cap: Haiku 250 / Opus 0
(G0 <= 2 x 80 minus reused, G3 <= 2 x 80 minus reused; combined with GEMMA-VS-4B <= 450 Haiku calls in total. If G3's changed set would push the combined total over 450, G3 is not judged and the report says pending; no subsetting. 0 paid API.)
