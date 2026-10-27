# Vendor prompting and sampling guidance: Qwen3-4B-Instruct-2507, Qwen3-1.7B, LFM2.5-8B-A1B

Status: LEADS, not conclusions. Sweep date 2026-10-19. Tags: [F] = page fetched with WebFetch (the tool returns a summary of the page, not the raw source; quotes are as the tool returned them, verify before a decision rests on one). [S] = search snippet only. Nothing here was run on our llama-server b11010 setup.

## 1. Qwen3-4B-Instruct-2507

Sampling
- [F] https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507: "We suggest using `Temperature=0.7`, `TopP=0.8`, `TopK=20`, and `MinP=0`." (the card lists these as its recommended settings).
- [F] same URL: "For supported frameworks, you can adjust the `presence_penalty` parameter between 0 and 2 to reduce endless repetitions."
- [S] https://featherless.ai/models/Qwen/Qwen3-4B-Instruct-2507/readme (mirror, same values): higher presence_penalty "may occasionally cause language mixing and a slight drop in performance."

Thinking control
- [F] same card: "This model supports only non-thinking mode and does not generate `<think></think>` blocks in its output." and "specifying `enable_thinking=False` is no longer required." No /think or /no_think switch mentioned. This is a separate model from the Qwen3-4B hybrid (which is different).

Output length and context
- [F] same card: "We recommend using an output length of 16,384 tokens for most queries." Context: "262,144 natively"; for OOM "reducing the context length to a shorter value, such as `32,768`."

System prompt
- [F] no system-prompt guidance found on the card.

Factuality / hallucination
- [F] no SimpleQA, TruthfulQA, FActScore, LongFact or HalluLens row on the card. Knowledge rows only: MMLU-Pro 69.6, MMLU-Redux 84.2, GPQA 62.0, SuperGPQA 42.8 (from search snippet [S] of the card).
- [S] search found no independent SimpleQA number for this exact model. A 2026 arXiv paper (https://arxiv.org/pdf/2607.05861) evaluates Qwen3-4B and 8B (the hybrid, not necessarily 2507) on SimpleQA and five other factuality benchmarks; numbers not in the snippet. [F] not read.

Instruction following
- [F] IFEval 83.4 for Qwen3-4B-Instruct-2507 (vs 81.2 Qwen3-4B Non-Thinking, 83.7 Qwen3-30B-A3B Non-Thinking, 74.5 GPT-4.1-nano), same card table.

Known failure modes
- [F] repetition (the card's presence_penalty advice above). Language mixing if presence_penalty is raised.

## 2. Qwen3-1.7B (hybrid thinking)

Sampling
- [F] https://huggingface.co/Qwen/Qwen3-1.7B, thinking mode: "For thinking mode, use `Temperature=0.6`, `TopP=0.95`, `TopK=20`, and `MinP=0`." Also: "DO NOT use greedy decoding, as it can lead to performance degradation and endless repetitions."
- [F] same card, non-thinking mode: "For non-thinking mode, we suggest using `Temperature=0.7`, `TopP=0.8`, `TopK=20`, and `MinP=0`." (This matches our enable_thinking=false path.)
- [F] presence_penalty "between 0 and 2 to reduce endless repetitions"; higher "may occasionally result in language mixing." Earlier note in the card: set presence_penalty to 1.5 if repetition is significant.

Thinking control
- [F] "We provide a hard switch to strictly disable the model's thinking behavior." Under enable_thinking=False "the model will not generate any think content and will not include a `<think>...</think>` block."
- [F] "`/think` and `/no_think` soft switches ... apply only when `enable_thinking=True`." Also: "When `enable_thinking=False`, the soft switches are not valid." So our enable_thinking=false setup does not need /no_think, and adding it is inert.
- [S] a dev.co page says /no_think or enable_thinking=False is needed. This conflicts with the card; go with the card.

Output length and context
- [F] "We recommend using an output length of 32,768 tokens for most queries." Context length: 32,768 tokens. Very hard math or code: max output 38,912 tokens.

System prompt
- [F] none beyond the soft switches, which the card describes as user-prompt or system-prompt suffixes only in thinking mode.

Factuality / hallucination
- [F] card has no IFEval or factuality numbers; points to the blog, GitHub, and docs for benchmarks.
- [S] search found no published SimpleQA, TruthfulQA or hallucination score for Qwen3-1.7B. OpenHalDet (https://arxiv.org/pdf/2606.06959) reports Qwen3 at 8B and 14B only (detection work, not factuality).

Known failure modes
- [F] greedy decoding gives "endless repetitions"; higher presence_penalty gives language mixing.

## 3. LFM2.5-8B-A1B (MoE, about 1.5B active by the card, 8.3B total)

Sampling
- [F] https://huggingface.co/LiquidAI/LFM2.5-8B-A1B: "temperature 0.2, top_k 80, repetition_penalty 1.05". top_p and min_p are not given. Same values on the vLLM recipe [F] https://docs.vllm.ai/projects/recipes/en/latest/LiquidAI/LFM2.5.html ("Sampling defaults (8B-A1B): temperature 0.2, top_k 80, no min_p, repetition_penalty 1.05"; "per-request client defaults, not server flags").
- [F] https://docs.liquid.ai/lfm/models/lfm25-8b-a1b.md: llama.cpp quick start "--temp 0.2 --top-k 80 --repeat-penalty 1.05". Note: the Liquid docs page does not quote a top_p, so do not set one from another checkpoint's values (the 1.2B-Thinking card uses top_p 0.1, which is a different model).
- [F] llama.cpp chat doc https://docs.liquid.ai/deployment/on-device/llama-cpp/chat.md lists per-checkpoint values: 1.2B-Instruct temp 0.1 top_k 50 repeat 1.05; 1.2B-Thinking temp 0.1 top_k 50 top_p 0.1 repeat 1.05; "Other LFM2.5 variants have different values ... The exact values for any checkpoint are on its Hugging Face model card."

Thinking and reasoning
- [F] HF card: "Because LFM2.5-8B-A1B is a reasoning model, assistant turns contain an explicit chain of thought before the final answer." Card also: "LFM2.5-8B-A1B is Liquid AI's Mixture-of-Experts reasoning model."
- [F] vLLM recipe: "`LFM2.5-8B-A1B` and `LFM2.5-1.2B-Thinking` emit an explicit `<think>…</think>` chain-of-thought." Launch with "`--reasoning-parser qwen3`" to split reasoning into reasoning_content. "A trivial prompt may be answered directly, in which case `reasoning_content` is empty."
- [F] vLLM recipe: "Leave `max_tokens` unset — capping it truncates the reasoning models' chain-of-thought." Our 900-token answer cap could be cutting the answer, not the reasoning; check which budget bites.
- [F] No official way to disable or shorten reasoning found on the HF card, the Liquid model page, the Liquid llama.cpp chat doc, or the vLLM recipe. The HF card says nothing about think tags; the vLLM recipe is the only source naming <think>.
- [S] https://docs.liquid.ai/lfm/models/lfm25-8b-a1b.md (search snippet) earlier: "reasoning-only model." Not verified on the page itself beyond the [F] text above.
- [S] Liquid announcement coverage (secondary, not the official post): reasoning is "always" written before the answer. Official blog not found in search.

Tool calls and template
- [F] https://docs.liquid.ai/deployment/on-device/llama-cpp/function-calling.md: "LFM2 and LFM2.5 emit tool calls between `<|tool_call_start|>` and `<|tool_call_end|>` control tokens." LFM2.5 writes Pythonic calls (e.g. `get_weather(city="Paris")`); LFM2 wraps tool definitions in `<|tool_list_start|>` / `<|tool_list_end|>`. Same token pair on the HF card [F] (Pythonic list between the tokens).
- [F] llama.cpp: "`--jinja` is required" for tool-call parsing; "Use a recent llama.cpp release"; "LFM2/LFM2.5 template detection lives in `common/chat.cpp`"; older builds fall back to a generic parser. With `parse_tool_calls: false`, raw tool tokens come back in `content`.
- [F] the think tokens themselves (what the chat template injects for thinking) are not on any page read. vLLM says `<think>`; HF card says nothing. Check the GGUF's embedded template (`llama-server --jinja`, template dump) rather than trust either page.

Context and factuality
- [F] Context: 128K tokens (HF card and Liquid specs table).
- [F] HF card benchmarks: IFEval 91.84; IFBench 56.47; Multi-IF 79.93.
- [F] HF card factuality: AA-Omniscience Index -24.70; Accuracy 8.67; Non-hallucination rate 63.47 (the card describes the index as rewarding correct answers and penalising hallucination). This is the closest published hallucination number for this model; it is the vendor's, and the AA-Omniscience harness is not SimpleQA.
- [S] AIME25 42.53, MATH500 88.76 (Liquid announcement, secondary coverage).

Known llama.cpp issues
- [S] HF card: the tokenizer was updated "to fix tool-calling issues in llama.cpp"; users who downloaded before commit feb5e04 should re-download the tokenizer files, and GGUFs were re-converted. Verify our GGUF's date against this.
- [S] one GGUF repo: always pass `--jinja`, otherwise the model "can produce malformed turns." Not verified.
- No llama.cpp GitHub issue specific to LFM2.5 thinking or think tags was found. Issue #19647 (https://github.com/ggml-org/llama.cpp/issues/19647) is about Devstral 2 thinking tags ([THINK] vs <think>), closed as not planned 2026-04-03; it does not mention LFM2 (read [F]). It is the closest thinking-tag template issue found, and it shows that the `<think>` tag is not guaranteed by a family's tokenizer alone.

## 4. Known llama.cpp issues that apply to thinking control on any of these (not LFM2-specific)

- [F] https://github.com/ggml-org/llama.cpp/issues/25067 (opened 2026-06-26, closed not planned 2026-09-12, stale bot): the log warns "Setting 'enable_thinking' via --chat-template-kwargs is deprecated. Use --reasoning on / --reasoning off instead." Our b11010 is older than this issue, so check whether b11010 has the same warning.
- [F] https://github.com/ggml-org/llama.cpp/issues/20182 (opened 2026-03-07, closed not planned 2026-08-12): llama-cli with `--chat-template-kwargs '{"enable_thinking": false}'` on Qwen3.5-9B still thinks. Not our model; it shows the kwarg path has failed before.
- [S] PR #13771 ("--reasoning-budget 0 to disable thinking, incl. qwen3 w/ enable_thinking:false"): the flag exists upstream; reports say `--reasoning-budget` stopped working in a Windows build (issue #22717, unread). Open PR #20329 "cli: fix --reasoning-budget and --chat-template-kwargs being ignored" (unread; merge state unknown).
- [S] Cherry Studio issue #14981: a UI "Reasoning Effort" setting cannot turn thinking back on once the kwarg disabled it.

## Gaps

- No published SimpleQA, TruthfulQA, FActScore, LongFact or HalluLens score found for Qwen3-4B-Instruct-2507 or Qwen3-1.7B. Next: the Qwen3 technical report (arXiv) and the paper https://arxiv.org/pdf/2607.05861 (Qwen3-4B SimpleQA; not read).
- LFM2.5-8B-A1B: the official Liquid blog post was not found; the HF card and docs say nothing about how to disable or shorten reasoning, and the think tokens are not shown on any page read. Next: GGUF chat template dump (`llama-server --jinja` or the template in the GGUF metadata) and the official blog.
- LFM2.5-8B-A1B: no published factuality number on SimpleQA/TruthfulQA; only AA-Omniscience (vendor run).
- llama.cpp b11010 specifics: the reasoning-budget and chat-template-kwargs status at that build not checked; issues above are from later builds.
- The phone-app observation (about 160 words of reasoning vs about 1100 tokens in our tests) was not researched; no vendor statement on the reasoning-token vs visible-word gap was found.
- Unverified claim from the search snippet: the card's sampling for 8B-A1B may be surfaced through a vLLM recipe rather than the card; the HF card fetch confirmed the same values, so this is closed for sampling only.
- No llama.cpp issue about the LFM2.5 tokenizer re-download was read; commit feb5e04 is only from a search snippet.
- Search returned secondhand parameter counts that disagree (8.3B vs 8.5B total; 1.5B vs 1B active). Use the HF card.
- WebSearch mode was standard throughout; extended search was not run (the coverage of LFM2.5 official blog and llama.cpp threads looked thin enough to warrant it, but the output is leads only).
