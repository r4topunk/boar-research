# QWEN35-2B onboarding (2026-10-20, before any judged screen)

TL;DR: Qwen/Qwen3.5-2B (post-trained hybrid, Apache-2.0) as unsloth Q4_K_M loads in llama.cpp b11010 on the mini. The GGUF-embedded template renders the LITEPACKS prompt byte-identically to the Hugging Face chat_template. Thinking is off, and 0 reasoning tokens were produced. Prompts fit -c 4096 (max 1133 + 768 tokens). The 5-item smoke has 0 failures and 0 think leaks. **The answers are longer than the 1.7B's, though:** vendor sampling gives a median of 97 output tokens vs 41 (one 293-token runaway), and engine sampling gives a median of 63. Smoke wall time is 1.38x the 1.7B with vendor sampling and 1.33x with engine sampling, measured under different mini load. Addresses MC-1 (research-2026-10-20/model-usage/model_choice.md, refute-2.md).

## Checkpoint
| Item | Value |
|---|---|
| Model | `Qwen/Qwen3.5-2B` @ `15852e8c16360a2fea060d615a32b45270f8a8fc` (created 2026-02-28). The "post-trained model" is hybrid: one checkpoint with thinking and non-thinking modes, and the card says "Qwen3.5-2B operates in non-thinking mode by default". Base = Qwen/Qwen3.5-2B-Base. HF pipeline tag image-text-to-text (VLM weights; we use text only). 24 layers in a 3:1 linear-attention (Gated DeltaNet) / full-attention pattern. |
| Licence | Apache-2.0 (card front matter + LICENSE file) |
| GGUF | No official Qwen GGUF repo exists (Qwen/Qwen3.5-2B-GGUF returns 404). Using `unsloth/Qwen3.5-2B-GGUF` @ `f6d5376be1edb4d416d56da11e5397a961aca8ae`, `Qwen3.5-2B-Q4_K_M.gguf`, 1,280,835,840 B, sha256 **`aaf42c8b7c3cab2bf3d69c355048d4a0ee9973d48f16c731c0520ee914699223`** (= HF LFS oid; checked after download). Stored at mini `<runner>/shared-models/lite/` (sha appended to its SHA256SUMS). Free disk after download: 36 GiB. |
| Load | llama-server b11010 (4bc272f) build-cpu on the mini: `model loaded` in 1.1 s, n_ctx_slot 4096 (onboarding/srvA.log). The `qwen35` arch is supported. |

## (1) Template and thinking-off
- tools/template_check.sh (mini, 0 generation) starts two llama-servers on the GGUF with `--jinja --reasoning off`: A uses the embedded template, B uses `--chat-template-file` with the HF `chat_template.jinja` (onboarding/hf-chat_template.jinja). It renders the first LITEPACKS prompt (vit-hum-001, real engine messages from arms/gate17 prompt dumps) through `/apply-template`.
- Rendered prompts A vs B: **byte-identical** with kwargs absent, `enable_thinking:false` and `enable_thinking:true` (onboarding/renders.json). The two template texts differ only in the tool-call argument loop (unsloth's `is mapping` fix, template lines 119-121), which our prompts never reach (no tools).
- Thinking off follows the vendor's documented method: non-thinking is the template default, and the template emits an empty `<think>\n\n</think>\n\n` unless `enable_thinking` is true (HF template l.149-152). The rendered prompt ends `<|im_start|>assistant\n<think>\n\n</think>\n\n` in both the absent and false cases. The harness also passes `--reasoning off` (BOAR_SERVER_EXTRA_ARGS, unchanged). The engine sends `thinking_budget_tokens 256` with no enable_thinking kwarg (audit M1), as it does for the 1.7B, so max_tokens = 512 + 256 for both models. Smoke result: reasoningTokens 0 on 15/15 2B generations, and no `<think>` or `</think>` in any answer text.

## (2) Sampling (vendor card, Best Practices, fetched 2026-10-20)
- "Non-thinking mode for text tasks: `temperature=1.0, top_p=1.00, top_k=20, min_p=0.0, presence_penalty=2.0, repetition_penalty=1.0`". The VL-task line is T 0.7 / top_p 0.8 / presence 1.5. The card's own non-thinking benchmark settings were T 0.7 / top_p 0.8 / top_k 20 / presence 1.5. The card also warns that higher presence_penalty "may occasionally result in language mixing and a slight decrease in model performance".
- Candidate V sampling (qwen35-2b.patch): `BOAR_SAMPLER_JSON ??= {"top_k":20,"top_p":1,"min_p":0,"presence_penalty":2}` set in the adapter, plus the samplerFor default temperature 0.7 -> 1.0 in be/server.ts. The engine's per-item health temperature 0 is kept on purpose (it is a safety design, not a sampler preference). repetition_penalty is not sent because llama-server's default is already 1.0. One difference from vLLM: llama.cpp applies presence_penalty over the last 64 tokens (penalty_last_n default), not over the whole output.
- Model-only variant E (qwen35-2b-engsamp.patch): the same model swap with engine sampling 0.7/40/0.95/0.05 unchanged. Added after the smoke to separate the model from the sampler (see (5)).

## (3) Quant at 2B
- Q4_K_M is a 4.8 bpw average. A 2B model has less redundancy than a 4B, and the DeltaNet linear-attention state/gate tensors are newer to llama.cpp quant recipes. unsloth's dynamic quant lists Q4_K_M, UD-Q4_K_XL (1.34 GB), Q6_K (1.57 GB) and Q8_0 (2.01 GB). QUANTLITE found Q8_0 = Q4_K_M (-0.003) on Qwen3-1.7B, but that result does not transfer automatically to a hybrid DeltaNet 2B. The smoke shows wrong facts ("Japan has approximately 1 trillion people", "Germany ~477/km2 vs Japan 35") with both samplers, so a quant contribution cannot be excluded. Not tested here (UNKNOWN). The cheap follow-up is a Q8_0 smoke if the screen is close to the bar.
- Hot-set / RAM: 1.28 GB file vs the 1.7B's 1.11 GB. Both are compact by size (<= 1.6e9 B, isCompactModel), so engine routing, declines and prompts are the same.

## (4) Context fit
- `/tokenize` on the 2B over all 103 LITEPACKS prompts in the gate17 dumps (K0 MAIN 75 + K1 screen 28): prompt tokens min 244, median 440, max **1133** (vit-hum-004). Plus max_tokens 768, the worst case is 1901 vs `-c 4096` (BOAR_SERVER_CTX unset). It fits with about 2x headroom. The 2B and the 1.7B tokenize the smoke prompts within +1 to +3 tokens of each other (same Qwen vocab family; the 2B vocab is 248k).

## (5) Smoke (5 K0 screen items: lan-cmp-004, vit-hum-004, st-qa-money-se-007, lan-exp-003, vit-sci-002; run_arm.sh IDS_OVERRIDE, mini, seed 42)
| Run | generation_failed / errors | reasoning tokens / think leak | output tokens per item | median | sum totalMs | ratio vs 1.7B | mini loadAvg1m |
|---|---|---|---|---|---|---|---|
| 1.7B ref (unchanged, `none`) | 0 | 0 / 0 | 55 53 41 35 41 | 41 | 16.0 s | 1.00 | 5.1-5.5 |
| 2B V (vendor sampling) | 0 | 0 / 0 | 67 97 82 133 293 | 97 | 22.1 s | **1.38** | 3.1-3.4 |
| 2B E (engine sampling) | 0 | 0 / 0 | 106 78 63 56 52 | 63 | 21.4 s | **1.33** | 2.9-4.1 |
- The 1.7B ref reproduced the mini control byte-for-byte on 5/5 items (0 changed answers, 0 judge calls), so the harness is intact.
- Decode speed is equal (2B 39-49 tok/s vs 1.7B 43-51). The extra wall time comes from answer length. Prefill is noisy across runs because the load differed (other lab jobs held both slots). The 1.15x hot-set ratio predicts about 1.15x per token, which these numbers cannot resolve.
- **Answer length is not similar.** V is 2.4x the median with one runaway (vit-sci-002: 293 tokens, a long hedged paragraph after a wrong number). E is 1.5x. The 2B also tends to keep the "Not found... may be wrong" warning prefix with longer memory answers. Both samplers produce confident wrong facts on these 5 items (judge on 5 items, informational only: V CE 5/5, E CE 3/5, 1.7B CE 4/5). Not a decision.
- Haiku calls: 10 (V) + 10 (E) + 0 (ref) = 20.

## (6) Wall time vs Qwen3-1.7B
1.33-1.38x on the 5 items (sum of totalMs), <= 1.5x, but the margin is thin. The 2B runs had lower machine load than the reference, so the true ratio is probably somewhat higher. The screen's per-arm wall ratio (mean totalMs over the same items vs the control trace) is the number used for the stage-2 condition.

## Decisions for the screen
- Primary candidate = V (vendor sampling), as the coordinator specified. Secondary = E (model swap only, "everything else identical"), screened under the same gate so that a NO on V cannot be blamed on the sampler alone. Both are frozen in QWEN35-criterion.md before generation.
- Model swap mechanism: the patches repoint the adapter's `qwen3-1.7b-q4km` MODELS entry (file + sha) and its catalog label/size at the 2B GGUF, so requests, routing, prompts, declines and the compact tier stay byte-identical. Traces still say `model: qwen3-1.7b-q4km`; `versions["model.sha256"] = aaf42c8b...` identifies the weights.

## Deviations
- Harness quirk (not changed): mini_gen.sh's "<= 2 llama-servers" guard counts any process whose command line contains `llama-server`, including other jobs' node adapters (`--server-bin .../llama-server`). One running job therefore blocks a second one even when it holds a free slot, and the smoke waited about 18 min behind poolctl-K0-st180.
- Diagnostic dirs: the 1.7B ref and E smoke ran as arms `q35ref17` / `q35engsamp` (run_arm.sh forbids `/` in names) and were moved to onboarding/smoke-ref17, onboarding/smoke-engsamp. The V smoke is in onboarding/smoke-vendor.

UNKNOWN: Q4_K_M vs Q8_0 quality at 2B for this hybrid; phone (ARM) prefill for DeltaNet layers; whether presence_penalty over 64 tokens (llama.cpp) behaves like the vendor's vLLM setting.
