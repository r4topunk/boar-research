# OCC-RAG released artifacts (angle: artifacts, cards, licences, configs, GGUF)

Date of research: 2026-10-20. Scope: released artifacts only. No model weights were downloaded
(GGUF sizes come from the HF tree API metadata). Raw small files were fetched to /tmp (config,
generation_config, tokenizer_config, chat_template.jinja, README) for reading.

## 0. Identity

- Paper: "OCC-RAG: Optimal Cognitive Core for Faithful Question Answering", arXiv 2606.00683, cs.CL,
  submitted 30 May 2026, licence CC BY 4.0 (arxiv.org/abs/2606.00683).
- Authors (10): Maksim Savkin, Mikhail Goncharov, Alexander Gambashidze, Alla Chepurova,
  Dmitrii Tarasov, Nikita Andriianov, Daria Pugacheva, Vasily Konovalov, Andrey Galichin,
  Ivan Oseledets. Affiliations not listed on the abstract page.
- Abstract (verbatim fragments): "we present OCC-RAG, optimized for faithful question answering
  (QA) grounded in the provided context." and "We release OCC-RAG-0.6B and OCC-RAG-1.7B, both
  mid-trained on this corpus." and "The models produce structured reasoning traces with source
  citations grounded in literal quotes from the context."
- Abstract claim: "match or exceed general-purpose models 2 -- 6x their size across multi-hop
  reasoning (HotpotQA, MuSiQue, TAT-QA), faithfulness (ConFiQA), and refusal (MuSiQue-Un)
  benchmarks." Authors' claim, not independently verified.

## 1. Repositories found

| Artifact | Ref | Facts from HF API / page |
|---|---|---|
| Model 1.7B | huggingface.co/occ-ai/OCC-RAG-1.7B | licence mit; created 2026-05-29; last modified 2026-06-28; downloads 1496; likes 16; sha 733cc24406179feedbd4bf54b4723c8d414bbc94; safetensors; HF lists 2B params in BF16 |
| Model 0.6B | huggingface.co/occ-ai/OCC-RAG-0.6B | licence mit; created 2026-05-29; downloads 379; likes 2 |
| GGUF 1.7B | huggingface.co/occ-ai/OCC-RAG-1.7B-GGUF | official; created 2026-06-09; downloads 556; tags gguf, llama.cpp, quantized; base_model occ-ai/OCC-RAG-1.7B; gguf metadata: total 1,720,574,976 params, architecture qwen3, context_length 32768 |
| GGUF 0.6B | occ-ai/OCC-RAG-0.6B-GGUF | official; created 2026-06-09; downloads 111 |
| ONNX 1.7B | occ-ai/OCC-RAG-1.7B-ONNX | official; created 2026-06-05; tags transformers.js, onnx, webgpu; downloads 11 |
| ONNX 0.6B | occ-ai/OCC-RAG-0.6B-ONNX | official; created 2026-06-05; downloads 11 |
| Collection | huggingface.co/collections/occ-ai/occ-rag-6a1985edcff89db09aef719c | 6 items per the card |
| Code | github.com/optimal-cognitive-core/OCC-RAG | licence MIT (GitHub API spdx MIT); pushed 2026-06-28; 48 stars; files: README, LICENSE, requirements.txt, examples/quickstart_transformers.py, examples/quickstart_vllm.py, assets/ |
| Cloud | cloud.ru/products/evolution-ml-inference | hosted endpoint linked from the card (paid/hosted, not usable offline; not investigated further) |

Third-party repackagings (not official, not verified for fidelity):
- mradermacher/OCC-RAG-1.7B-GGUF (created 2026-06-03, downloads 175, gguf, MIT)
- mradermacher/OCC-RAG-0.6B-GGUF (created 2026-06-03)
- useitone/OCC-RAG-0.6B (created 2026-06-03, 14 downloads)
- mrsndmn/OCC-RAG-0.6B-ONNX (created 2026-06-04, 2 downloads)

No dataset repo was found in the occ-ai listing returned by the API search (the search was for
models only). The training corpus (~3.25M QA) is described but no public dataset link was found.
Not verified exhaustively: the occ-ai/OCC-RAG collection may list more items.

## 2. Licence

- HF model card YAML: `license: mit` (both sizes; GGUF and ONNX repos too).
- Model card body and GGUF card: "Released under the [MIT License](...), inherited from the base
  model." (The phrase "inherited from the base model" is the card's own wording. The base
  Qwen3-1.7B-Base licence was NOT checked in this pass.)
- LICENSE file in the GitHub repo: "MIT License / Copyright (c) 2026 optimal cognitive core".
- The HF repo tree has no LICENSE file (LICENSE returned 404 on the HF model repo); the licence is
  declared in the YAML header only.
- Paper: CC BY 4.0 (arXiv).
- Implication: the declared licence allows redistribution in an app, subject to keeping the MIT
  notice. The base-model licence still needs one check (Qwen3 base licence, not done here).

## 3. config.json (1.7B, verbatim key values)

- architectures: ["Qwen3ForCausalLM"]; model_type: qwen3
- hidden_size 2048; intermediate_size 6144; num_hidden_layers 28; num_attention_heads 16;
  num_key_value_heads 8; head_dim 128; hidden_act silu
- vocab_size 151936; tie_word_embeddings true
- max_position_embeddings 32768; rope_theta 1000000 (rope_parameters block); sliding_window null
- eos_token_id 151643; pad_token_id 151643; bos_token_id null
- dtype bfloat16; transformers_version 5.5.4
- 0.6B differs only in hidden_size 1024 and intermediate_size 3072 (diff against 1.7B).

## 4. generation_config.json (1.7B, verbatim)

```
do_sample: false
temperature: 0.0
eos_token_id: [151643, 151645, 151683]
max_new_tokens: 2048
pad_token_id: 151643
```

Note: max_new_tokens 2048 is a default that matters for a long reasoning trace on a phone. The
card says greedy is the training/eval default and is "baked into generation_config.json".

## 5. tokenizer_config.json (1.7B)

- tokenizer_class Qwen2Tokenizer; eos_token "<|endoftext|>"; pad_token "<|endoftext|>";
  bos_token null; model_max_length 131072 (tokenizer value; config says 32768).
- additional_special_tokens (added on top of the Qwen3 set), 28 OCC tokens in this list:
  `<|query_start|>`, `<|query_end|>`, `<|source_start|>`, `<|source_end|>`, `<|source_id|>`,
  `<|query_analysis_start|>`, `<|query_analysis_end|>`, `<|source_analysis_start|>`,
  `<|source_analysis_end|>`, `<|reasoning_start|>`, `<|reasoning_end|>`, `<|status_start|>`,
  `<|status_end|>`, `<|answer_start|>`, `<|answer_end|>`. The list also keeps the Qwen vision
  tokens (object_ref, box, quad, vision, image_pad, video_pad) and `<|im_start|>`/`<|im_end|>`.
- special_tokens_map.json: not present (404). LICENSE on HF: 404.

## 6. Chat template (chat_template.jinja, 1.7B; IDENTICAL to 0.6B, diff empty)

Verbatim:

```
{%- for message in messages -%}
    {%- if message['role'] == 'system' -%}
        {{ '<|im_start|>system\n' + message['content'] + '<|im_end|>\n' }}
    {%- elif message['role'] == 'user' -%}
        {%- if documents and loop.last -%}
            {{ '<|im_start|>user\n<|query_start|>' + message['content'] + '<|query_end|>\n' }}
            {%- for doc in documents -%}
                {{ '<|source_start|><|source_id|>' + (loop.index | string) + ' ' + doc['text'] + '<|source_end|>\n' }}
            {%- endfor -%}
            {{ '<|im_end|>\n' }}
        {%- else -%}
            {{ '<|im_start|>user\n' + message['content'] + '<|im_end|>\n' }}
        {%- endif -%}
    {%- elif message['role'] == 'assistant' -%}
        {{ '<|im_start|>assistant\n<think>\n\n</think>\n\n' + message['content'] + '<|im_end|>\n' }}
    {%- endif -%}
{%- endfor -%}
{%- if add_generation_prompt -%}
    {{ '<|im_start|>assistant\n<think>\n\n</think>\n\n<|query_analysis_start|>\n' }}
{%- endif -%}
```

Behaviour that follows from it:
- Sources are passed only through the `documents=` kwarg, and only on the LAST user turn.
  Each doc is `{"text": ...}`; the index is 1-based and written as the `<|source_id|>` number.
- The generation prompt pre-fills an empty think block and the first token
  `<|query_analysis_start|>`, so thinking mode is off and the model is forced to start in
  the query-analysis section. The `enable_thinking=False` flag in the examples is not needed for
  this template to produce the empty think block (it is baked in).
- A system message is supported, but it is rendered as a plain system turn with no OCC tags.
- Multi-turn history: assistant turns are rendered with the empty think block and raw content.
  The template does not add the tags to earlier assistant turns.
- There is no BOAR-style "warning line" logic in the template. Abstention is a model output
  (status UNANSWERABLE, then the refusal phrase).

Alternative (card): build the content by hand as
`<|query_start|>{question}<|query_end|>\n<|source_start|><|source_id|>{i} {text}<|source_end|>\n`
inside a user turn, then use the same template with the documents argument omitted.

## 7. Output schema (verbatim from card, sections and tokens)

Five sections, each delimited by special tokens:

| # | Section | Tokens |
|---|---|---|
| 1 | Query analysis | `<\|query_analysis_start\|> ... <\|query_analysis_end\|>` (start tag is injected by the template; the model emits only the end tag) |
| 2 | Source analysis | `<\|source_analysis_start\|> ... <\|source_analysis_end\|>`, cites sources as `<\|source_id\|>N` |
| 3 | Reasoning | `<\|reasoning_start\|> ... <\|reasoning_end\|>` |
| 4 | Status | `<\|status_start\|> ... <\|status_end\|>`, value ANSWERABLE or UNANSWERABLE |
| 5 | Answer | `<\|answer_start\|> ... <\|answer_end\|>`; final answer span or the refusal phrase |

Card calls the refusal output `Not enough information` when the context does not support an
answer. Citations are by `<|source_id|>N` inside the analysis (literal quote form per the abstract).
Parsing: the vLLM quickstart (examples/quickstart_vllm.py) parses each section with a regex, takes
the last matching span, and tolerates a missing end tag. It requires `skip_special_tokens=False`.
`<|im_end|>` and `<|answer_end|>` are in generation_config eos per the vLLM quickstart comment
(the eos list in generation_config has 151645 = `<|im_end|>` and 151683 = likely `<|answer_end|>`;
the id-to-token mapping was not checked against tokenizer.json).

Output length is not measured in the card. The output is a multi-section trace, so the
generated token count per answer is much larger than a 2-5 sentence answer. The sum of five
sections is a structural cost for an on-device run; this has not been measured.

## 8. Quickstart snippets and runtimes

- Transformers quickstart (card): `apply_chat_template(..., documents=documents, enable_thinking=False)`,
  `generate(max_new_tokens=2048)`, regex `<\|answer_start\|>(.*)` to extract the answer.
  Example answer: Canada.
- vLLM quickstart (examples/quickstart_vllm.py): batched, `LLM(model, dtype="bfloat16")`,
  `SamplingParams(temperature=0.0, max_tokens=2048, skip_special_tokens=False)`.
- OpenAI-compatible servers: documents go through `extra_body={"chat_template_kwargs": {"documents": documents}}`.
- Compatible runtimes (card): transformers>=5.5.1, vllm>=0.19.1, sglang>=0.5.11. requirements.txt
  (GitHub): torch>=2.10, transformers>=5.5.1, accelerate>=1.1, vllm>=0.19.1.
- llama.cpp (GGUF card): `llama-cli -hf occ-ai/OCC-RAG-1.7B-GGUF:Q4_K_M -p "Hello" -no-cnv`;
  the card notes "newer llama.cpp: use llama-completion". The chat template is embedded in the
  GGUF; the card says apply with `--jinja`. No llama.cpp build version is pinned.
- Ollama (GGUF card): `ollama run hf.co/occ-ai/OCC-RAG-1.7B-GGUF:Q4_K_M`.
- Card note: "With only 1.7B parameters, it can be readily deployed in constrained infrastructure,
  including desktop systems running on CPU RAM." No mobile or Android statement, no latency numbers.

## 9. GGUF variants (tree API metadata; sizes in bytes, not downloaded)

| File | Bytes | GB (approx) | Card note |
|---|---|---|---|
| OCC-RAG-1.7B-Q4_0.gguf | 1,054,420,096 | 1.05 | legacy, smallest |
| OCC-RAG-1.7B-Q4_K_M.gguf | 1,107,405,952 | 1.11 | "recommended balance" |
| OCC-RAG-1.7B-Q5_K_M.gguf | 1,257,876,608 | 1.26 | |
| OCC-RAG-1.7B-Q6_K.gguf | 1,417,751,680 | 1.42 | |
| OCC-RAG-1.7B-Q8_0.gguf | 1,834,423,424 | 1.83 | "near-lossless" |
| OCC-RAG-1.7B-F16.gguf | 3,447,346,304 | 3.45 | full precision |
| OCC-RAG-1.7B-BF16.gguf | 3,447,346,304 | 3.45 | "lossless base" |

All quants are derived from BF16 (card). Card limitations line: "Lower-bit quants (Q4) trade some quality
for size; prefer Q6_K/Q8_0 when accuracy matters most." These are size/quality notes from the card,
not measured here. Note the GGUF tree lists every file above 100 MB, which is the constraint
on weights for this research pass; nothing was downloaded.

## 10. Benchmark table (card and paper, copied exactly)

Card table (card's own columns: HotpotQA In-Acc, MuSiQue In-Acc, TAT-QA F1, ConFiQA In-Acc,
ConFiQA M_R (lower = better), MuSiQue-Un R-Acc). Card baseline for Qwen3-1.7B is the THINK row.

| Model | HotpotQA | MuSiQue | TAT-QA F1 | ConFiQA In-Acc | ConFiQA M_R | MuSiQue-Un R-Acc |
|---|---|---|---|---|---|---|
| gemma-3-4b-it | 55.8 | 30.1 | 65.3 | 69.8 | 8.9 | 55.8 |
| Qwen3-1.7B (think) | 60.9 | 30.7 | 74.8 | 70.4 | 8.3 | 82.8 |
| Qwen3-4B (think) | 67.1 | 41.5 | 79.1 | 74.1 | 7.5 | 84.0 |
| Pleias-RAG-1.2B | 48.5 | 15.0 | 8.4 | 37.3 | 25.3 | 21.9 |
| OCC-RAG-0.6B | 57.6 | 36.6 | 75.0 | 79.9 | 5.2 | 86.9 |
| OCC-RAG-1.7B | 60.9 | 38.2 | 81.0 | 81.4 | 5.0 | 87.2 |

Paper Table 2 adds the no-think Qwen3-1.7B row (fetched from arxiv.org/html/2606.00683v1):

| Model | HotpotQA | MuSiQue | TAT-QA F1 | ConFiQA In-Acc | ConFiQA MR | MuSiQue-Un R-Acc |
|---|---|---|---|---|---|---|
| Qwen3-1.7B (no-think) | 47.7 | 20.1 | 74.4 | 64.8 | 12.7 | 54.7 |
| Qwen3-1.7B (think) | 60.9 | 30.7 | 74.8 | 70.4 | 8.3 | 82.8 |
| OCC-RAG-1.7B | 60.9 | 38.2 | 81.0 | 81.4 | 5.0 | 87.2 |

Reading:
- The no-think baseline is the one that matches BOAR's mode (no thinking, 1.7B). Its gaps are large
  (HotpotQA +13.2, MuSiQue +18.1, TAT-QA F1 +6.6, ConFiQA +16.6, MuSiQue-Un refusal +32.5).
- Against the think baseline the HotpotQA score is equal (60.9 vs 60.9), as the task text said.
- The task text's no-think figures (47.7, 20.1, 74.4, 64.8, 12.7, 54.7) are confirmed by the paper table.
- Evaluation setup per the paper: 10 sources per question for HotpotQA, MuSiQue and MuSiQue-Un;
  1 source for TAT-QA and ConFiQA. Decoding for OCC-RAG is not specified in the paper.
  Comparison models use "sampling parameters as recommended in the corresponding technical reports".
- In-Acc = substring match for HotpotQA and MuSiQue. For ConFiQA the match rule is not defined.
- The reasoning traces were generated by Qwen3.5-27B (the paper's trace generator). The card calls
  it "distilled from a larger teacher model".
- Not verified here: no independent re-run; the In-Acc substring metric is generous (the task
  text noted this too). The card's "best faithfulness across all evaluated scales (up to 32B)"
  claim is the authors' claim.

## 11. Limitations (card, verbatim)

- "Context-grounded only. The model is trained to answer from the supplied sources and to ignore
  parametric knowledge. It is not a general-purpose chat or knowledge model."
- "Reasoning depth. Training and evaluation are capped at three-hop reasoning; longer chains are
  out of distribution."

## 12. Fit notes against BOAR (for the coordinator; not a recommendation)

- BOAR's fallback (answer from memory under a warning line when no source is found) is the exact
  behaviour OCC-RAG is trained to refuse. If OCC-RAG is used, the no-source path stays with the main model
  or a separate route; OCC-RAG only handles the has-source path. This is a design decision, not
  a model defect.
- Output is a five-section trace. BOAR's UI wants 2-5 sentences with [n] citations. The answer
  section is parseable, but the trace tokens are generated on the phone. Token cost and latency are
  unmeasured.
- Quant options are small enough (Q4_K_M 1.11 GB) for the 8 GB Pixel 8a memory budget on paper.
  The GGUF was not run.
- Sources per question in the eval (10 for multi-hop) are above BOAR's typical chunk count; the
  effect of BOAR's retrieval shape (chunk size, count, citation id scheme) on OCC is unknown.
- Russian is listed as a second language in the tags; English is the only concern for BOAR.

## 13. Unknowns / not checked

- Base model licence (Qwen3-1.7B-Base) not fetched in this pass.
- Dataset/corpus licence: no public corpus link found; the 3.25M QA corpus is not confirmed as released.
- Whether the GGUF was produced by occ-ai (official GGUF repo exists; the GGUF README is written by
  occ-ai, and the 0.6B GGUF repo is also official). Tensor-level checksums were not compared to
  the safetensors weights.
- llama.cpp version compatibility of the embedded template (`--jinja`): not tested.
- Whether llama.cpp treats the 28 OCC special tokens as control tokens (affects skip-special parsing).
- Exact token id mapping for generation_config eos ids 151645 and 151683.
- Whether the mradermacher GGUF files match the official ones (third-party; not compared).
- The 0.6B numbers were read from the card table only; the 0.6B no-think row was not in the paper fetch.
