# VITAL-ONOFF-DEV criterion (frozen 2026-10-23 before any generation or judge call of this arm; never edited afterwards)

## Question
Does the app maintainer's wiki-vital5 pack (his "Encyclopedia" tier) raise the judged quality of HIS native pipeline on our dev set,
at fixed model and persona (pack on vs off)? Context: Vital keyword hits bypass his 0.70 gate and outrank personal files (PR #86).
The word "gain" may be used toward the app maintainer only on a GAIN verdict below.

## Arms (51 CV5 v0.1 dev ids = cv5-51.ids; same harness, snapshot 5f8cc8f4)
- N-D (existing, step 3 of NATIVE-PARITY): label kb (Standard KB only), cutoff 0.7, persona detailed (small-model texts, ShortAnswer
  fallback to Succinct for health/seed/small talk, maxTokens AppSettings Auto), Qwen2.5-1.5B-Instruct Q4_K_M (sha 1adf0b11...).
  Generations runs/s3-gen.jsonl (arm N-D), Haiku rows judgments/native-N-D-v01-s42.judgments.jsonl. Not regenerated.
- N-DV (new): identical except corpus = kb + wiki-vital5 (catalog sha d3b87d56, work/dl/wiki-vital5.sqlite, opened as DeviceEvalRunner
  opens packs), label kbvital5, cutoff 0.7 (his default), persona detailed, default --model-bytes (986048768, the 1.5B = small).
  Prompt string = harness output. Generation exactly as step 3: Mac mini, llama-server b11010 CPU (-t 2, -c 4096, -np 1), tools/s3_gen.py
  (POST /completion, temperature 0.7, top_k 40, top_p 0.95, min_p 0.05, repeat_penalty 1.0, seed 42, n_predict = maxTokens, stop <|im_end|>).
  Kept titles per item recorded in the prompts file.

## Divergence-first judging
An item is divergent iff its N-DV answer text != its N-D answer text (exact string compare after trim). Only divergent items are judged:
Haiku 5.5-low judge.v1-low, N 4 shards, both orders (deepthink/tools/shard_judge.sh), bench boar-eval/bench/v0.1, system
native-parity-N-DV-v01-haiku55-low. Non-divergent items inherit the N-D rows (same text => same score by construction).

## Metrics (estimator = arms/device-x6/tools/agg_device.py, as tools/s3_agg.py: per-item s = mean of 3 dims over both orders,
## raw = sum(s)/sum(r), floor-adj = sum(s-1)/sum(r-1), paired item bootstrap B 2000 seed 11, over all 51 ids)
- PRIMARY: paired raw delta N-DV - N-D (judge.v1, Haiku) with 95 % CI.
- Secondary (descriptive): floor-adj delta, win/tie/loss vs reference per arm, better/worse/equal per item (|ds| > 0 counts),
  kept-on count (>= 1 kept source), divergent count, output tokens p50 (tokens_predicted), at-cap count.
- Confident error (CE): step 3 defined none, so the LITEPACKS rule is adopted here: non-declined answer with judge correctness
  (mean of the two orders) <= 1.5; decline = empty, or body < 300 chars matching the LITEPACKS MODEL_DECLINE regex (native has no
  warning line, so every non-declined answer counts). Reported per 100 items per arm. Health items = ids with prefix lan-hlt or vit-hlt (4 ids).

## Pre-registered predictions (from the existing 0-LLM stage data)
- Kept-on: N-DV keeps >= 1 source on 32/51 (existing kbvital5 retrieval at 0.7 on these ids); N-D keeps on 1/51.
- Divergent items: 32 +- 3 (prompts differ only where retrieval keeps a source).
- Sign of the primary delta: positive but small (+0.00..+0.04), CI straddling 0 => NEUTRAL is the expected verdict.

## Decision rule
- GAIN: CI low > 0 AND no new confident error on a health item (no health id that is non-CE in N-D and CE in N-DV).
- HARM: CI high < 0.
- else NEUTRAL (including CI low > 0 with a new health CE).
- Validity: >= 49/51 non-empty N-DV generations and every divergent id judged in both orders, else INVALID.
- One seed, Haiku (compresses gaps), dev ids, 1.5B (not the 1.7B), desktop harness + mini generation: stated next to every number.

## Budget
No Opus, no paid API, no llama.cpp changes, no blind/, rnd/veil, bench/v0.4.
calls_cap: Haiku 110 / Opus 0
