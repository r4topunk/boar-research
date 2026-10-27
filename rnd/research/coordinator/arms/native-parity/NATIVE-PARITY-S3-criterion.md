# NATIVE-PARITY step 3 criterion (frozen 2026-10-21 before any generation or judge call of this step)

## Question
At fixed model (Qwen2.5-1.5B-Instruct Q4_K_M, the RC1 model, sha 1adf0b11...), how much of the native pipeline's loss vs our engine is the
native prompt/pipeline at its default (Detailed persona, KB-only Standard KB, 0.7 gate), and how much of that is the persona alone?

## Arms (51 CV5 v0.1 dev ids = ruler/cv5-ladder/in/set.json "ids", copied to cv5-51.ids)
- N-D (native exact, RC1 default): the harness prompt string (tools/harness, snapshot 5f8cc8f4, label kb, cutoff 0.7, persona detailed:
  small-model texts, ShortAnswer fallback to Succinct for health/seed/small talk, maxTokens = AppSettings Auto 1024, 512 for small talk),
  i.e. the model's own chat template applied to RagPure.assembleChatMessages(kept context). Generated on the Mac mini with llama-server
  b11010 CPU (-t 2, -c 4096), POST /completion with that prompt, sampling = native Sampling defaults (temperature 0.7, top_k 40, top_p 0.95,
  min_p 0.05, repeat_penalty 1.0), seed 42, n_predict = maxTokens. Answer = generated text, trimmed (the eval row stores the raw text).
- N-S (native, Succinct): same, persona succinct, maxTokens 512.
- O (ours, existing): arms/ship15b-packs traces ship15b-packs-K1-main-sub3e6183-s42 (our engine cut7 + litepacks tree, 1.5B swap, Succinct,
  maxTokens 512, K1 kit, mini) and its existing Haiku judge.v1-low rows; dng-005 (text identical to the K1 control) takes the control's rows.
- Context only (no rule): STYLE15B 1.5B-D (our engine, Detailed) if its Haiku rows exist at analysis time.

## Judge
Haiku 5.5-low judge.v1-low, both orders, N 4 shards (deepthink/tools/shard_judge.sh, preflight), bench boar-eval/bench/v0.1.
Calls: 2 arms x 51 ids x 2 orders = 204 (cap 300). No Opus, 0 paid, no blind/, rnd/veil, bench/v0.4.

## Metrics (tools/s3_agg.py; estimator = arms/device-x6/tools/agg_device.py: per-item s, r = mean of 3 dims over both orders,
## ratio of sums, paired item bootstrap B 2000 seed 11)
raw = sum(s)/sum(r); above_min (floor-adj) = sum(s-1)/sum(r-1). Paired deltas: O - N-D (total, model fixed), O - N-S (pipeline + packs at
the same persona), N-S - N-D (persona inside the native pipeline). Also output tokens (llama-server tokens_predicted) p50 per native arm.

## Reading rules (descriptive attribution; nothing is adopted)
- Validity: >= 49/51 non-empty generations per native arm and every id judged in both orders, else the step is reported INVALID.
- Persona share = (N-S - N-D) / (O - N-D) on raw, reported only when O - N-D CI excludes 0.
- "persona-dominant" if |N-S - N-D| >= 2 x |O - N-S|; "pipeline-dominant" if |O - N-S| >= 2 x |N-S - N-D|; else "mixed".
- One seed, Haiku (compresses gaps), dev ids: stated next to every number.

## Budget
calls_cap: Haiku 300 / Opus 0
(Addendum 2026-10-21, after generation, before any judge call: the judge preflight needs this machine-readable line; the cap is the one already stated above. Nothing else changed; original sha 4d1d4042.)
