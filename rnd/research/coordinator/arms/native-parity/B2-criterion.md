# B2-HARNESS-17S criterion (frozen 2026-10-21 before any generation or judge call of this arm)

## Question
In the app maintainer's exact native pipeline (JVM harness tools/harness on snapshot 5f8cc8f4: KB-only Standard KB, 0.7 gate, his small-model
prompts, Succinct), what does Qwen3-1.7B score vs his Qwen2.5-1.5B Succinct arm N-S on the 51 CV5 v0.1 dev ids (cv5-51.ids)?
Measures NOTE-1's two asks together (1.7B entry + Succinct default) inside his pipeline.

## Arm
- N-17S: harness label kb, cutoff 0.7, persona succinct, small-model texts (file 1,107,409,472 B < SMALL_MODEL_BYTES 2e9, as N-S), maxTokens 512
  (AppSettings Auto), prompt = the 1.7B's own chat template via llama-server b11010 /apply-template with chat_template_kwargs
  enable_thinking false (as boar_jni.cpp:263, thinking off by default). Model Qwen3-1.7B Q4_K_M sha b139949c5bd7...
- Generation: Mac mini, llama-server b11010 CPU -t 2 -c 4096, POST /completion (tools/s3_gen.py unchanged): temperature 0.7, top_k 40,
  top_p 0.95, min_p 0.05, repeat_penalty 1.0, seed 42, stop <|im_end|>, n_predict 512.
- Prompt-identity check (before generation): the N-17S prompt bytes equal the N-S prompt bytes except the chat-template difference
  (expected: only the empty think block "<think>\n\n</think>\n\n" after "<|im_start|>assistant\n"); any other diff = stop and report.
- Control N-S: existing S3 traces and Haiku rows (judgments/native-N-S-v01-s42.judgments.jsonl, same judge config); existing C2 Opus rows.

## Judge
Haiku 5.5-low judge.v1-low, both orders, N 4 shards (deepthink/tools/shard_judge.sh, preflight), bench boar-eval/bench/v0.1: 102 new calls.
Opus judge.v1 (tools/c2_judge.sh config) on N-17S only, 102 calls, ONLY if the Haiku d (N-17S - N-S, floor-adj) lies in [+0.02, +0.08]
(within +-0.03 of the +0.05 line); then the Opus result decides, paired vs the C2 N-S Opus rows.

## Metric (estimator arms/device-x6/tools/agg_device.py: per-item s, r over both orders, ratio of sums, paired item bootstrap B 2000 seed 11)
U floor-adj = sum(s-1)/sum(r-1); raw = sum(s)/sum(r). Also correct / CE per 100 where the labels exist, output tokens p50.

## Rules
- Validity: >= 49/51 non-empty texts, 0 texts containing "<think>", every id judged in both orders; else INVALID (quote nothing).
- PASS: d U floor-adj (N-17S - N-S) >= +0.05 AND CI low > 0 (Haiku; Opus if triggered as above).
- FAIL otherwise; reported as "the 1.7B adds no separable gain over the 1.5B inside his Succinct pipeline".
- Prediction (from our engine's 1.7B - 1.5B gap): Opus CB17 closed-book 0.337 vs 1.5B closed-book 0.261 = +0.076, K0 - N-S +0.087;
  Haiku compresses it: our engine 1.7B-S 0.263 vs 1.5B-S 0.220 = +0.043 (STYLE15B). Predicted Haiku d = +0.04 (0.00...+0.08),
  i.e. near the line; P(PASS) about 0.4.
- One seed, dev ids, one run: stated next to every number.

## Budget
calls_cap: Haiku 102 / Opus 102 (Opus only by the trigger above); 0 paid; no blind/, rnd/veil, bench/v0.4.
