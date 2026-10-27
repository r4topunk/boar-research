# JAN-V1-EDGE onboarding (2026-10-21, before any judged screen)

TL;DR: janhq/Jan-v1-edge (Apache-2.0, Qwen3-1.7B base, SFT from Jan-v1-4B + RLVR for agentic search) as the official Q4_K_M GGUF loads and generates in llama.cpp b11010 on the mini (same arch and file size as the 1.7B). The embedded template is byte-identical to the HF chat_template and renders the LITEPACKS prompt identically with and without the GGUF; it is the stock Qwen3 template plus training-only `{% generation %}` markers, `enable_thinking` switch kept. **Thinking cannot be turned off cleanly:** the template's empty `<think>\n\n</think>\n\n` prefill is applied (`--reasoning off`) and 0 reasoning tokens are parsed, but on 3/5 smoke items per sampler the model keeps reasoning in the visible answer ("Okay, so the user is asking...", "Let me think...") and emits `</think>`, with runaways to the 768-token cap. Smoke median answer 133-233 tokens vs 41 for the 1.7B; wall 1.74-2.05x. Shortlist rank 3 (research-2026-10-20/hf-finetunes/SHORTLIST.md).

## Checkpoint
| Item | Value |
|---|---|
| Model | `janhq/Jan-v1-edge` @ `f4ed4d61df6fa0bb4724101b4ae1ab81dd3aa299` (2025-08-27), base `Qwen/Qwen3-1.7B`, English. Card: SFT distillation from Jan-v1-4B, then RLVR (as Jan-v1/Lucy) for "reasoning efficiency, tool use, and correctness"; SimpleQA 83 % with search tools (own harness). |
| Licence | Apache-2.0 (card front matter `license: apache-2.0`; GGUF repo the same). |
| GGUF | `janhq/Jan-v1-edge-gguf` @ `e2c9bc87988c8d08b03301255faa58c5ddb8ee64`, `Jan-v1-edge-Q4_K_M.gguf`, 1,107,409,440 B, sha256 **`bdde4346e5e0ecc8b679dd6ca43d4e66d85c50227cda5287428d65489fad0c59`** (= HF LFS oid; checked after download). Mini `<runner>/shared-models/lite/` (appended to SHA256SUMS). |
| Load + 1 generation | llama-server b11010 build-cpu on the mini: `model loaded`, n_ctx_slot 4096 (onboarding/srvA.log). Greedy 64 tokens on the first LITEPACKS prompt: coherent English, reasoning_content empty, no think markers (gen1.json). **Supported.** |
| Disk | Free before 27.3 GiB (29.33e9 B); after-download projection 26.3 GiB >= 25, no other download in flight -> downloaded at once. Free after: 26 GiB. |

## (1) Template and thinking-off
- tools/template_check.sh (mini): llama-servers `--jinja --reasoning off`, A = embedded template, B = `--chat-template-file` with the HF chat_template.jinja (@ f4ed4d61). Renders through `/apply-template` (onboarding/renders.json).
- A vs B: **byte-identical** renders for kwargs absent, `enable_thinking:false` and `true`; embedded template file == HF file.
- Diff vs the Qwen/Qwen3-1.7B HF template (onboarding/qwen3-1.7b-hf_chat_template.jinja): only `{% generation %}...{% endgeneration %}` wrappers around assistant content (a transformers training mask; no effect on the rendered prompt). The generation prompt and the `enable_thinking is false -> '<think>\n\n</think>\n\n'` branch are the stock Qwen3 ones.
- Under `--reasoning off` the absent-kwargs render already ends with the empty think block (the server sets enable_thinking false), as for the 1.7B. Greedy 200-token probes with the engine's request shape (thinking_budget_tokens 256, no kwarg; gen2) and with `enable_thinking:false` (gen3): identical output, 76 tokens, finish stop, 0 reasoning, no markers.
- **But in the harness smoke (sampled, 5 items) the prefill does not hold.** reasoningTokens 0 on 10/10, yet 3/5 answers per sampler contain `</think>` (1-5 times) with chain-of-thought before and/or after it, e.g. vit-hum-004 V: answer, `</think>`, then "Okay, so the user is asking ... Let me check the context" until the 768-token cap. The model was distilled and RL-trained thinking-on (card compares with "Qwen 3 1.7B Thinking"); the non-thinking path is out of its training distribution. No clean switch exists (the template has none beyond the prefill; llama.cpp cannot strip reasoning that comes after an already-closed think block).
- Thinking-on size probe (jan-v1-edge-think256.patch: `--reasoning on`, engine fast-tier budget 256, engine sampler; smoke only): reasoning 93-264 tokens (3/5 at the budget), visible answer 61-145 tokens (median 65), total out median 328 vs 41, wall **2.21x** the 1.7B; still 2/5 answers with a stray `</think>` after the budget message. Thinking-on is not a fast-path option.

## (2) Sampling (card "Recommended Inference Parameters" + generation_config.json, fetched 2026-10-21)
- Vendor: temperature 0.6, top_p 0.95, top_k 20, min_p 0.0, max_tokens 2048 (generation_config: 0.6 / 0.95 / 20). These are Qwen3's thinking-mode defaults.
- V = jan-v1-edge.patch: adapter `BOAR_SAMPLER_JSON ??= {"top_k":20,"top_p":0.95,"min_p":0}` + samplerFor default temperature 0.7 -> 0.6 in be/server.ts (per-item health T 0 kept). max_tokens 2048 not adopted (engine budgets kept).
- E = jan-v1-edge-engsamp.patch: model swap only, engine 0.7/40/0.95/0.05.
- Both patches repoint the `qwen3-1.7b-q4km` MODELS entry (file + sha) and the catalog label; catalog `sizeBytes` stays 1107409472 (the real file is 1107409440 B, compact either way).

## (3) Quant
Q4_K_M only (QUANTLITE: Q8_0 = Q4_K_M on the base Qwen3-1.7B, -0.003). Q5/Q6/Q8 exist in the GGUF repo; not tested (UNKNOWN for this fine-tune).

## (4) Context fit
`/tokenize` over the 103 LITEPACKS prompts: min 243, median 436, max **1133** (vit-hum-004); + max nPredict 512 = 1645 vs -c 4096; harness worst case 1133 + 768 = 1901, fits.

## (5) Embeddings
Unchanged (bge-small-en-v1.5 q8_0): retrieval does not depend on the generator.

## Speed
Same Qwen3-1.7B architecture and quant, file size within 32 B of the 1.7B: per-token decode and prefill equal the 1.7B; no stage-0 bench. All wall differences come from answer length.

## Smoke (5 K0 items: lan-cmp-004, vit-hum-004, st-qa-money-se-007, lan-exp-003, vit-sci-002; run_arm.sh IDS_OVERRIDE, mini, seed 42)
| Run | errors / gen failed | reasoning tok | answers with `</think>` | output tokens | median | `[n]` cites (items) | mean totalMs | ratio vs 1.7B |
|---|---|---|---|---|---|---|---|---|
| 1.7B ref (qwen35-2b/onboarding/smoke-ref17) | 0 / 0 | 0 | 0 | 55 53 41 35 41 | 41 | 1 (lan-cmp-004) | 3209 | 1.00 |
| Jan V (card 0.6/0.95/20/0) | 0 / 0 | 0 | **3** | 62 768 233 54 267 | 233 | 2 (lan-cmp-004, vit-hum-004 inside the CoT) | 6567 | **2.05** |
| Jan E (engine) | 0 / 0 | 0 | **3** | 133 64 385 54 496 | 133 | 1 (lan-cmp-004) | 5597 | **1.74** |
| Jan think-on 256 (engine sampler, size only) | 0 / 0 | 93-264 | 2 | 397 409 328 154 263 | 328 (visible ~65) | 1 (lan-cmp-004) | 7089 | 2.21 |
- `[n]` citation compliance: the only smoke item where the 1.7B cites (lan-cmp-004) is cited by every Jan run, but Jan puts the marker first (`[1] The adult male moose...`).
- Judge on 5 items (information only, Haiku): CE 4/5 in all three runs, as the 1.7B; dU vs control V -0.050, E -0.057, think -0.003. Haiku calls 10 + 10 + 10 = 30.
- Outputs: onboarding/smoke-vendor, smoke-engsamp, smoke-think256 (ran as arms janedgev / janedgee / janedget, moved).

## Decision
Proceed to the GATE v2 screen with both thinking-off samplers (the deployable path; the brief asks for the screen; the smoke does not separate the samplers). The `</think>` leak is reported per run, not a void condition. Criterion: JAN-criterion.md (frozen, commit 40803f4a).

UNKNOWN: whether a stop sequence on `</think>` (cut the answer at the first `</think>`) or a different prompt shape (sources as tool results, the card's trained format) would keep the model's reading gains without the CoT leak; Q4 vs Q8 for this fine-tune; HF tree of Jan-v1-edge (Lucy is the alt per the shortlist).
