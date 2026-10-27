# Model-usage audit: quantization and runtime flags (2026-10-20)

TL;DR: no runtime/quant misuse found that could explain today's 7 NOs on Qwen3-1.7B. Desktop and phone run the same llama.cpp
(b11010 4bc272f), the same GGUF (unsloth Q4_K_M with an imatrix), the same n_ctx (4096), the default f16 KV, flash-attn auto, and no rope
override. Prompts peak at 1,702 tokens against 4,096 (truncated = 0 everywhere). Thinking is off byte-correctly (empty `<think>\n\n</think>\n\n`),
0 of 1,758 answers leak tags or reasoning, and no answer reaches the 512-token cap (max 80). Three residual items are listed below (none high).
Scope: read-only plus 3 non-generating llama-server calls (/apply-template, /props, /tokenize) on a server another agent already had running on
the MacBook (:18731), plus GGUF header parses. 0 generations, 0 judge calls, 0 paid. No blind, veil or v0.4 content was read.

## Evidence

### Models (GGUF headers, parsed with b11010 gguf-py / a header-only parser)
| file | producer | ftype | imatrix | tensors | notes |
|---|---|---|---|---|---|
| lite/Qwen3-1.7B-Q4_K_M.gguf (sha b139949c, = HF LFS oid, unsloth @ d7f544ee) | Unsloth | 15 (Q4_K_M) | yes: imatrix_unsloth.dat, 685 chunks, 196 entries | Q4_K 168, Q6_K 29 (attn_v, ffn_down, token_embd), F32 113 | tied embeddings (no output.weight; Q6_K token_embd serves as the head); ctx_train 40960; rope base 1e6, no scaling keys; template has enable_thinking |
| Qwen3-4B-Instruct-2507-Q4_K_M.gguf (sha 3605803b) | Unsloth | 15 | yes (79 chunks) | Q4_K 216, Q6_K 37 | ctx_train 262144, no yarn needed at 4096; instruct-only template (no enable_thinking), correct for 2507 |
| Qwen2.5-1.5B-Instruct-Q4_K_M.gguf (sha 1adf0b11) | bartowski-style (calibration_datav3) | 15 | yes | Q4_K 168, Q6_K 29 | fine |
| OCC-RAG-1.7B-Q4_K_M.gguf (mini, sha 5ff807a9) | occ-ai | 15 | **no imatrix keys** | same layout | general.sampling.temp = 0.0 (the OCC arm used greedy, which matches); eos 151643, eot 151645, eom 151683 (all EOG in llama.cpp); the vendor repo also ships Q5_K_M/Q6_K/Q8_0/BF16 |
| bge-small-en-v1.5-q8_0.gguf (sha ec38e8da) | — | 7 (Q8_0) | — | — | bert.pooling_type = 2 (CLS) = the model's intended pooling; the app's embed.ts passes no pooling_type, so the GGUF's CLS is used on the phone and on the desktop (node-llama-cpp, llama.cpp v0.4.0) |

### Desktop runtime (be/adapter-litedecline.ts:430-434; arms/lp-screens/tools/mini_gen.sh; arms/litepacks/tools/run_lp.sh)
`llama-server -m … -t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek --reasoning off`, b11010 (4bc272f) CPU.
- KV: no --cache-type, so f16 (BOAR_KV_TYPE unset). FA: default auto. batch/ubatch: defaults (2048/512), which affect speed only.
- `--reasoning off` (common/arg.cpp:3677-3685) sets default_template_kwargs enable_thinking=false, and every request also sends chat_template_kwargs {enable_thinking:false} (be/server.ts:61).
  /apply-template on the running b11010 server with a real LITE17 system prompt renders `…<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n` both with and without the kwarg.
  This is Qwen's documented non-thinking format. `</think>` tokenizes as the single special id 151668.
- Context: the LITEPACKS server logs show `n_ctx_slot = 4096` and `truncated = 0` on every slot release, with max n_tokens 1,702 (MacBook K1 runs).
  Over the traces from today's arms (lp-screens control K0/K1, litepacks K0-K4, greedy, occrag, vendorsamp, b-honest, shortctx, quotefirst):
  promptTokens max 1,388 (the K1 st set) and outputTokens max 80 (1.7B), so the 512 nPredict cap is never reached. Output ends with "." in 1,685/1,758 and with "]" in 69/1,758.
- Sampling: T 0.7 / top_k 40 / top_p 0.95 / min_p 0.05 / seed 42 (server.ts:26). Server defaults: repeat_penalty 1.0, presence 0, dry 0 (/props). Sampling is another dimension, but no flag overrides it silently.
- Load warning `control-looking token: 128247 '</s>' was not control-type` is the standard Qwen-vocab override and harmless.
- The engine's context budget (answer.ts:1041-1064) uses ctxSize 4096 minus 512 minus overhead. The trimming that "context:452->320" reports comes from compressContext relevance, not from the runtime window (context-policy dimension).

### Phone (bench-app)
- llama.rn 0.13.0-rc.4 (package.json:23) vendors llama.cpp `LLAMA_BUILD_NUMBER = 11010`, `LLAMA_COMMIT = "4bc272f"` (node_modules/llama.rn/vendor/llama.cpp/common/build-info.cpp:6-7), the same build as the desktop.
- initLlama (engine/src/inference/LlamaEngine.ts:288-296) passes n_ctx = contextSizeForRam (4096 for > 6.5 GB, memoryFit.ts:280-285), n_threads 4, n_gpu_layers 0,
  and no cache_type (so f16) and no flash_attn (so auto; forced off only on iOS/the CPU fallback). This matches the desktop.
- Completion (LlamaEngine.ts:538-558): messages + jinja, enable_thinking:false, temperature, n_probs 0, stop []; top_k/top_p/min_p fall back to
  the context's common defaults (40/0.95/0.05; JSIParams.cpp:447-449), the same values the desktop sends. Seed -1 (random) on the phone vs 42 on the desktop, as intended.
- Route gate (temperature 1, persisted per rc.4) runs only for the 4B (answer.ts:790 "4B only"), and the next answer call resets temperature and n_probs.

### Prior measurements that already cover parts of this dimension
- QUANTLITE (arms/quantlite/QUANTLITE.md, 10-16): Q8_0 vs Q4_K_M on the 1.7B, same unsloth revision: Δ −0.003 (−0.025…+0.019), n 20, Haiku.
- KVQ8 (arms/kvq8/KVQ8-L1.md, 10-05): q8_0 KV on the 4B is non-inferior (−0.008). This is not relevant today because f16 is used.

## Findings (none high)
1. **M: today's quant evidence is thin for today's metric.** QUANTLITE is n 20, one seed, cross-host (the Q4 anchor was identical to the MacBook Q4 on only 6/20),
   measured on the ratio with X2b, not on confident errors on K0/K1. Qwen3 is reported to be more quant-sensitive than earlier families at 4 bit (arXiv 2505.02214),
   and the 1.7B is the smallest model in play. The data are thin rather than a demonstrated error.
   Cheapest test: re-download unsloth Q8_0 (1.83 GB, sha 0becaa82) to the mini and run `run_arm.sh q8screen K0 screen` with the model swapped (37 gens, 74 Haiku calls).
   Fixed ≥ 6 → the NOs are partly quant-bound. Or, zero-judge: llama-perplexity --kl-divergence Q4 vs BF16 on 30 dumped K0 prompts (top-1 agreement).
2. **L-M: the OCC-RAG file has no imatrix and broke the format on 8/40 calls.** The vendor repo ships Q5_K_M/Q6_K/Q8_0; OCCRAG.md:67 left "Q8 better?" UNKNOWN.
   A strict section/status format on a 1.7B fine-tune is the case where non-imatrix Q4_K_M hurts most. Cheapest test: 5 greedy OCC calls on the
   malformed items with OCC Q8_0 on the mini (0 judge); if ≥ 4/5 come out well formed, re-screen.
3. **L: the screen gate has no sampling-resample null.** SCREENS.md:58-60 estimates judge noise (~5 %/CE item) but not the re-sampling a prompt change causes at T 0.7
   (the problem items were selected as CE in one sample, so they regress to the mean). This inflates "fixed" for every arm. It cannot manufacture a NO, so it does not explain today's
   NOs, but 4/23 fixed (four arms) may be at the null. Cheapest test: control with seed 43 on K0 screen (37 gens, ≈ 74 Haiku calls) → null "fixed" count.
4. **L (untested option, not a misuse):** unsloth recommends its UD-Q4_K_XL (1,132,952,128 B, +25 MB) over plain Q4_K_M. It is untested here and unlikely to matter given finding 1's direction.

## Checked OK
GGUF provenance + sha for 1.7B/4B/1.5B/bge/OCC; imatrix present on the 1.7B/4B/1.5B; tied embedding Q6_K; no rope/yarn override needed (ctx 4096 ≪ train 40960);
n_ctx 4096 desktop = phone (≥ 6.5 GB), 0 truncations, max prompt 1,702; output never capped; KV f16 both; FA auto both; same llama.cpp build on desktop and
phone (b11010 4bc272f), node-llama-cpp embeddings on llama.cpp v0.4.0; thinking off renders the vendor's empty think block, 0 tag leaks, 0 reasoning tokens in 1,758 rows;
`--reasoning off` + kwarg consistent; EOG/stop handling (chat path uses template EOG, no string stops); bge CLS pooling from the GGUF; detector mean pooling matches its head;
threads/batch affect speed only; seed/determinism (mini 37/37 repeatable per SCREENS.md).

Sources: https://huggingface.co/unsloth/Qwen3-1.7B-GGUF (file list via HF API), https://huggingface.co/occ-ai/OCC-RAG-1.7B-GGUF (file list),
https://docs.unsloth.ai/basics/qwen3-how-to-run-and-fine-tune, https://localbench.substack.com/p/gguf-benchmark-methodology, arXiv 2505.02214.
