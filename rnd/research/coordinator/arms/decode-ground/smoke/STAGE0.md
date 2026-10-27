# DECODE-GROUND stage 0: llama-server b11010 capability check (2026-10-21 20:5x, Mac mini)

Server: `<runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m <runner>/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf -t 4 -tb 4 -c 8192 -ngl 0 -np 2 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek --reasoning off --port 8096` (default repack). Probe: `tools/stage0_probe.py` (raw output `smoke/stage0-probe.json`), 2,424-token chat prompt. Server stopped after the probe (port 8096 free); :8094 untouched.

| # | check | result |
|---|---|---|
| 0 | `/apply-template` (+ `chat_template_kwargs.enable_thinking:false`) → `/tokenize` (`parse_special`) → `/detokenize` round trip | PASS: string identical; prompt ends `<|im_start|>assistant\n<think>\n\n</think>\n\n`; 2,424 ids = `/v1/chat/completions` usage.prompt_tokens 2,424; greedy 12 tokens via ids = chat endpoint text (byte-equal) |
| 1 | `/completion` with `prompt` = token-id array, `n_probs: 40` | PASS. Field is **`completion_probabilities[0].top_logprobs[]`** (not `top_probs`) with `id`, `token`, `bytes`, `logprob`; 40 entries. Default = **pre-sampling** (raw softmax): identical top-5 logprobs at T 0 / top_k 1 and at T 0.7/40/0.95/0.05. `post_sampling_probs: true` switches to `top_probs[]` with `prob` after the sampler chain (top_k 1 → 1 entry, p 1.0). The DG driver uses pre-sampling logprobs. |
| 2 | `cache_prompt: true` token-by-token | PASS: every 1-token call after the first has `prompt_n` 1, `tokens_cached` = prompt+i; **27.2 ms/call** (single slot); token-by-token greedy = one-shot greedy (byte-equal) |
| 3 | GBNF `grammar`, 29 literal sentences (UTF-8 `—`, `ï`, `é`, `№`, escaped `"`) + `"NO_EVIDENCE"` | PASS: output = exactly one alternative (`River 12 flows "north" into lake 84 — naïve café №12.`), off-topic question → `NO_EVIDENCE`; 3.4 s incl. ~1k-token prefill |
| 4 | `logit_bias` `[[id, bias]]` per request | PASS: +30 on the 2nd-ranked id forces it; `[[id, false]]` bans the top id |
| 5 | `id_slot` pinning (two prompts alternated on slots 0/1) | PASS: both keep their cache (`prompt_n` 1 on each slot every call; 27 ms / 17 ms) |

No failures, no workaround needed. Caveat found in stage 1 (not a server failure): a token that is in one side's top-40 and absent from the other's gets the imputed logprob; with the spec's −30 the ctx-only tail tokens (true logprob −12…−16) win the CAD score (see SMOKE.md), so an adaptive plausibility cut (`DG_PLAUS`) is implemented as an option.
