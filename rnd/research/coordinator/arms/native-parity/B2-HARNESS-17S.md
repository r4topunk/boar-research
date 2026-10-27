# B2-HARNESS-17S (2026-10-21): FAIL. Inside his Succinct pipeline, the Qwen3-1.7B scores the same as his 1.5B (+0.010, Haiku)

Criterion B2-criterion.md (sha 0de88243..., rnd d299d4eb), frozen before generation. Tool tools/b2_agg.py -> aggregates/B2-HARNESS-17S.json (7db45411...).
Calls: 102 Haiku judge.v1-low (cap 102), 0 Opus (trigger not met), 0 paid. Generation: 51 on the Mac mini (b11010 CPU -t 2, port 8197, about 2 min).

## Setup
- N-17S = the app maintainer's pipeline exactly as N-S (JVM harness, snapshot 5f8cc8f4, KB-only Standard KB, 0.7 gate, small-model Succinct texts,
  maxTokens 512), model swapped to Qwen3-1.7B Q4_K_M (sha b139949c), chat template via /apply-template with enable_thinking false.
  Prompts built on the MacBook (harness + 1.7B tokenizer server); generation on the mini with tools/s3_gen.py unchanged (native Sampling defaults, seed 42).
- Prompt identity: 51/51 N-17S prompts equal the N-S prompts byte for byte except the empty Qwen3 think block after "<|im_start|>assistant\n"
  (aggregates/B2-prompt-identity.json). Same kept context (1/51 items keep a KB source in both).
- Validity: 51/51 non-empty, 0 "<think>", 0 at the 512 cap, every id judged in both orders: VALID.
- N-S side: the existing S3 Haiku rows (same judge config, shard_judge.sh judge.v1-low N 4). No re-judging.

## Rows (CV5 51 v0.1 dev ids, one run each, seed 42; item bootstrap B 2000 seed 11)
| row | host | judge | U floor-adj (CI) | raw | correct / CE per 100 | out tokens p50 |
|---|---|---|---|---|---|---|
| N-D his RC1 default, 1.5B Detailed | mini (harness) | Haiku | 0.129 (0.098-0.163) | 0.312 | 0.0 / 66.7 | 392 |
| N-S his pipeline, 1.5B Succinct | mini (harness) | Haiku | 0.226 (0.167-0.293) | 0.389 | 25.5 / 41.2 | 44 |
| **N-17S his pipeline, 1.7B Succinct** | mini (harness) | Haiku | **0.236 (0.177-0.300)** | 0.398 | 25.5 / 37.3 | 37 |
| our 1.7B K0 (claim kit, layers) | mini | Haiku | 0.248 (0.194-0.309) | 0.406 | 29.4 / 25.5 | - |
| our 1.7B K1 Succinct (STYLE15B 1.7B-S) | mini | Haiku | 0.263 (0.201-0.333) | 0.419 | 27.5 / 27.5 | 46 |
| our 1.7B closed-book (CB17) | mini | Haiku | 0.250 (0.190-0.317) | 0.407 | 33.3 / 35.3 | - |
| N-S (C2) / our K0 / CB17 | as above | Opus | 0.265 / 0.351 / 0.337 | 0.415 / 0.483 / - | 27.5 / 39.2 (N-S) | - |
Per 100: correct = mean correctness over both orders >= 4, CE = <= 1.5 (ship15b thresholds; native arms never decline).

## Paired (Haiku, n 51)
| pair | dU floor-adj (CI) | d raw (CI) | better / worse |
|---|---|---|---|
| **N-17S - N-S (model, his pipeline)** | **+0.010 (-0.043...+0.062)** | +0.009 (-0.034...+0.051) | 21 / 18 |
| N-17S - N-D (model + Succinct = NOTE-1 both asks) | +0.107 (+0.061...+0.158) | +0.086 (+0.049...+0.126) | 30 / 11 |
| N-S - N-D (Succinct alone, S3) | +0.097 (+0.048...+0.151) | +0.077 (+0.038...+0.120) | 27 / 12 |
| our 1.7B K0 - N-17S (our pipeline vs his, same model) | +0.011 (-0.050...+0.073) | +0.008 | 21 / 19 |
| CB17 - N-17S | +0.014 (-0.033...+0.070) | +0.009 | 16 / 23 |
CE per 100 N-17S - N-S: -3.9.

## Verdict (frozen rules)
- PASS needs N-17S - N-S >= +0.05 with CI low > 0 (Haiku). Observed +0.010, CI low -0.043: **FAIL**.
- Opus trigger ([+0.02, +0.08]) not met (+0.010), so 0 Opus calls; the verdict is Haiku's.
- Prediction (+0.04, 0.00...+0.08): inside the band, low end. Haiku compresses model gaps (STYLE15B 1.7B-S - 1.5B-S +0.043 Haiku vs Opus CB17 - 1.5B closed-book +0.076),
  so an Opus re-judge could show a larger gap; under the frozen rule that was not run.
- Decomposition of NOTE-1's combined +0.107 (Haiku): Succinct +0.097 (91 %), model +0.010 (9 %). Style share >= 2/3: NOTE-1 leads with the Succinct ask.
- His pipeline with the 1.7B is level with ours on the same model (+0.011, CI straddles 0): with KB-only retrieval (1/51 fires), both behave like the model closed-book.

## Sentence for NOTE-1
"In your pipeline, the 1.7B with Succinct scores 0.236 vs 0.226 for the 1.5B with Succinct and 0.129 for your current default
(1.5B Detailed) (Claude Haiku judge, 51 dev questions, one run each); almost all of the gain is the Succinct persona, the model adds
+0.01 (CI -0.04...+0.06) under this judge." The 1.7B case then rests on speed/RAM and on the Opus-judged bench gap, not on this run.

## Files
traces/native-N-17S-v01-s42.traces.jsonl (7498dca1...), judgments/native-N-17S-v01-s42.judgments.jsonl (3c5bc0c4...), runs/b2-gen.jsonl (83b7471c...),
runs/b2-prompts.jsonl, runs/judge-N-17S.log, aggregates/B2-HARNESS-17S.json, aggregates/B2-prompt-identity.json, tools/b2_agg.py.

## Limits
One seed, one run, Haiku only (compresses gaps), n 51 dev ids. Embeddings via llama-server b11010 CPU, not his JNI build (C2 bounds this).
The 1.7B is not in his catalog: small-model texts chosen by file size (1.11 GB < 2 GB), as his DeviceEvalRunner would. Stage B (device) not run.
