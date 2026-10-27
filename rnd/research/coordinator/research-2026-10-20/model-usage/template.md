# Model-usage audit: chat templates and thinking mode (2026-10-20 20:51)

TL;DR: the prompt today's 1.7B arms sent is byte-identical to the Hugging Face reference render (Qwen/Qwen3-1.7B tokenizer_config, enable_thinking=false). It has no BOS, ends in the empty `<think>\n\n</think>\n\n` block, and nothing leaked: 0/1,269 answers with think or ChatML tags and 0 reasoning tokens across 1,966 trace rows. Desktop llama-server and phone llama.rn both run llama.cpp b11010 `4bc272f` and render through the same GGUF jinja template. Template misuse does not explain any of today's NOs. Three smaller findings follow, none of them high.

Scope: Qwen3-1.7B (unsloth Q4_K_M, sha b139949c), Qwen3-4B-Instruct-2507 (unsloth Q4_K_M), Qwen2.5-1.5B-Instruct (Q4_K_M), OCC-RAG-1.7B (Q4_K_M, sha 5ff807a9, mini only).
Cost: 0 judge calls, 0 paid. 1 local generation (MacBook, llama-server b11010, -c 4096, killed afterwards). Mini: read-only GGUF header parse (no slot lock needed, no model load).

## Method
1. The embedded `tokenizer.chat_template` and tokenizer keys were extracted from each GGUF: python `gguf` for the local files, a stdlib header parser (`template-evidence/ggufkv.py`) on the mini for OCC.
2. tokenizer_config.json, chat_template.jinja and generation_config.json were downloaded from HF for Qwen/Qwen3-1.7B, Qwen/Qwen3-4B-Instruct-2507, Qwen/Qwen2.5-1.5B-Instruct and occ-ai/OCC-RAG-1.7B.
3. One public dev question was rendered: st-qa-travel-se, messages taken from oracle-st/runs/st-qa-travel-se-cut7-oracleadd-s42.prompts.jsonl, i.e. assembleChatMessages output (system = persona + source rules + grounding + 3 sources; user = question + "(Response style: ...)"). Each model was rendered with its GGUF template and with the HF template (jinja2 sandbox, `template-evidence/render.py`), plus a 4-message multi-turn variant.
4. The real server path was checked: llama-server b11010 started with the arms' exact flags (`--jinja --reasoning-format deepseek --reasoning off`), then `/apply-template` (with and without the kwarg), `/tokenize` (add_special on and off), and one `/v1/chat/completions` call.
5. Statistics were computed over today's traces (litepacks, lp-screens control, b-honest, shortctx, quotefirst, greedy, logprob, occrag, vendorsamp): leaks, empty answers, reasoning tokens, prompt and output token distributions, server flags, and the server-log truncation flag.
6. Code read: src/rag/pure.ts (assembleChatMessages/assemblePrompt), src/inference/LlamaEngine.ts, src/routing/answer.ts, src/routing/depth.ts, src/routing/routeGate.ts, be/server.ts, be/adapter-litedecline.ts, be/gate.ts, occrag.patch, logprob.patch, bench-app/src/benchModels.ts and llamaRnShim.ts, and llama.rn 0.13.0-rc.4 (src/index.ts, cpp/rn-llama.cpp, vendor/VERSIONS).

## Checked and OK
| Check | Evidence |
|---|---|
| Qwen3-1.7B GGUF template vs HF | The source differs: unsloth rewrote `messages[::-1]` and `startswith` into jinja-compatible forms. Renders are byte-identical: single-turn thinking off sha 0cf43a5f, thinking default sha e3d02cd0, multi-turn identical. |
| Qwen3-4B-Instruct-2507 GGUF vs HF | The source differs: unsloth added reasoning_content and `</think>` handling for assistant turns after the last user turn. Renders are identical for single-turn and multi-turn (the branch only fires for an assistant message after the last user message, which the engine never sends). |
| Qwen2.5-1.5B GGUF vs HF | The template source is identical (sha cd8e9439). |
| OCC-RAG GGUF vs HF chat_template.jinja | Byte-identical (sha 6bc65ed5, 985 chars). |
| llama-server render, 1.7B | `/apply-template` with `enable_thinking:false` gives the HF render byte-for-byte (3,050 chars). With **no** kwarg, `--reasoning off` alone gives the same bytes, so the server-wide flag is what turns thinking off (see F1). |
| BOS | `add_bos_token=false` in all four GGUFs; `/tokenize` gives 680 tokens with add_special on and off; the first token is 151644 `<|im_start|>`. `/props` reports `bos_token ','` because the unsloth Qwen3 GGUFs have no bos id (llama.cpp falls back to id 11), but it is never inserted and no Qwen template references bos_token. |
| Stop / EOG | eos `<|im_end|>` (151645) in the Qwen GGUFs. The test generation ended with finish_reason `stop` after 52 tokens. Server logs: 1,137/1,137 slots `truncated = 0`. On the chat path the engine adds no string stops (LlamaEngine.ts:545 `stop ?? []`; server.ts:57). |
| Think leakage | 0/1,269 answer texts (and 0 in the 1,966 rows across all of today's runs) contain `<think>`, `</think>`, `<|im_*` or `<|endoftext`. reasoningTokens 0 everywhere. |
| Server config parity | All 1,966 trace rows of today's arms: backend llama-server, b11010 `4bc272f`, `server.extra_args --reasoning off`, model sha b139949c. The greedy and vendorsamp overrides are recorded as intended. |
| Context truncation | Prompt tokens p50 687, p90 1,034, max 1,662 against ctx 4,096. Output tokens p50 45, p99 76, max 105, so the 512 cap is never reached. |
| Desktop vs phone template engine | llama.rn 0.13.0-rc.4 vendors llama.cpp `LLAMA_CPP_REF=b11010`, commit 4bc272fd (vendor/VERSIONS), the same build as the desktop server. `enable_thinking` and `chat_template_kwargs` are forwarded into `common_chat_templates_inputs` (rn-llama.cpp:691,707). The bench-app engine files LlamaEngine.ts, pure.ts and format.ts are byte-identical to the desktop tree. |
| Phone thinking off for the 1.7B | bench-app/src/llamaRnShim.ts:28-33 applies `withThinkingOff` (enable_thinking false, budget params dropped, n_predict without the budget) to every completion while the 1.7B is loaded, so it matches the desktop `--reasoning off` render. |
| Prefix-warm render (phone) | warmNow renders `[system, user ""]` without the kwarg. The shared prefix runs through the system turn's `<|im_end|>`, which is identical in both renders. |
| Route gate | Runs only on the 4B (ROUTE_GATE_MODEL_IDS, routeGate.ts:13). The server engine has no nextTokenProbs, so no `route-gate` events appear in today's traces (0). The desktop `renderChatML` (be/gate.ts) matches the 4B-Instruct/Qwen2.5 render; for the hybrid 1.7B it would miss the empty think block, but it is never used there. |
| OCC-RAG input format | Matches the card: question as the only user turn, sources via `chat_template_kwargs.documents`, no system prompt, greedy (`general.sampling.temp 0.0` in the GGUF), `--special` so the section tokens come through. Section tokens 151669–151683 are CONTROL type. A raw output ends exactly at `<|answer_end|>` (0/56 with trailing text). `<|reasoning_start|>` appears in 49/56 raws, so the server's chat parser does not strip section tokens. |
| LOGPROB capture | `logprobs:true, top_logprobs:20` without `post_sampling_probs`, which returns pre-sampling probabilities (logprob.patch:60). The AUC is not distorted by top-k/min-p truncation. |

## Findings

### F1 (medium): the engine plans thinking ON for the 1.7B; only the harness turns it off
- depth.ts:259 gives the fast tier `thinking: true` for any model, so answer.ts:1457-1458 sends `thinkingBudget: 256` and **does not** send `enableThinking:false`. server.ts:48-64 therefore sends `thinking_budget_tokens 256` and no `chat_template_kwargs`.
- Thinking is off in today's arms only because of the server-wide `--reasoning off` (run_lp.sh, BOAR_SERVER_EXTRA_ARGS). On the phone it is off only because of the bench-app shim (benchModels.ts `withThinkingOff`).
- The adapter comment "thinking OFF (`--reasoning off` + enable_thinking:false)" (adapter-litedecline.ts:165) is wrong for the answer call.
- Without these harness switches, the TS engine as written runs the 1.7B with a 256-token think block. That is LITE17 arm T: −0.002, ×1.9 tokens.
- Not an artefact for today's NOs: the measured config is consistent across desktop, mini and bench. It is a product-parity risk: the shipping app or a Kotlin port that copies the request shape would not run what was measured.
- Cheapest test: in the shipping app, log the rendered prompt tail of one 1.7B answer and check that it ends with `<think>\n\n</think>\n\n`. In the engine, either set `thinking:false` for non-reasoning-role models or tag the 1.7B.

### F2 (low): budgets still reserve the 256 thinking tokens when thinking is off
- answer.ts:1050 subtracts FAST_THINKING_BUDGET from the source budget unless `gen.thinking === false`.
- server.ts:22 and LlamaEngine.ts:539 add 256 to n_predict / max_tokens.
- With ctx 4,096 and the quick budgets of 450/700 tokens this never binds: measured prompt max 1,662 and output max 105. It could bind on a 2,048-ctx device.
- Cheapest test: compute the `budget` value for ctx 2,048 in a unit test.

### F3 (low): OCC-RAG ran at Q4_K_M, which the vendor card says to avoid when accuracy matters; the format breaks the adapter saw are model-side
- The GGUF card says: "Lower-bit quants (Q4) trade some quality for size; prefer Q6_K/Q8_0 when accuracy matters most". Q5_K_M, Q6_K and Q8_0 are published, Q8_0 at 1.83 GB.
- 8 of the 40 OCC-eligible generations were malformed or looped:
  - bare `_start` text where `<|reasoning_start|>` belongs (4/56 raws);
  - a status of `ANSWER_SOURCE ... HAS_ANSWER` (lan-ref-002 K0);
  - a lowercase `unanswerable` status, counted as malformed (vit-hum-005 K0);
  - a 1,352-token status loop (lan-rsn-003 K0).
- The trace cap was 512 trace + 512 answer tokens against the card's `max_new_tokens=2048`. There were 2 forced closes.
- The OCC server also received `--reasoning off` and `thinking_budget_tokens 256`. Both are inert here: the template does not depend on enable_thinking, and no reasoning tokens appeared.
- Effect on OCCRAG: small. The malformed K0 items were mostly heading to abstain (lan-rsn-001, vit-trv-003 "Not enough information"), or were sentinels already at 5.0 (lan-ref-002). The NO-GO stands. The verdict is dominated by the screen design that erased its faithful refusals, which was found earlier today.
- Cheapest test: Q8_0 on the 8 malformed items on the mini (one gen slot, about 8 × 10 s), counting valid status sections.

## Not checked / UNKNOWN
- The node-llama-cpp backend (be/adapter.ts makeEngine) builds the prompt through `resolveChatWrapper` / LlamaChatSession, not the GGUF jinja template. None of today's arms used it (all llama-server). Older 4B runs on that backend were not re-rendered here.
- The production Android app (the app maintainer's Kotlin app) builds its own requests. Whether it sends enable_thinking=false for the 1.7B is unknown (see F1).
- Prompt content is outside this dimension, but worth noting for the honesty line: CONTEXT_INSTRUCTION (pure.ts) tells the model "If the context doesn't cover the question, say so and answer from general knowledge". That is an explicit invitation to parametric answers on a 1.7B. B-HONEST tested modified clauses; today's ruler decision is refuse-by-default.
- Qwen2.5-1.5B runs with the engine sampler (0.7/40/0.95/0.05, no repetition penalty) where its generation_config has top_p 0.8, top_k 20 and repetition_penalty 1.1. This is a sampling dimension, recorded only.

## Evidence files
- `template-evidence/qwen3-1.7b.rendered.st-qa-travel.txt`: the exact prompt (HF = GGUF = llama-server), sha 0cf43a5f.
- `template-evidence/render.py`: jinja2 render. `template-evidence/ggufkv.py`: stdlib GGUF metadata reader.
