# GEMMA4-E2B onboarding (2026-10-20, before any judged screen)

TL;DR: google/gemma-4-E2B-it (Apache-2.0) as unsloth Q4_K_M loads and generates in llama.cpp b11010 on the mini (arch `gemma4`). The embedded template renders the LITEPACKS prompt byte-identically to the HF chat_template. Thinking is off (no `<|think|>`, 0 reasoning tokens, no thought markers). Prompts fit -c 4096 (max 1129 + 512). Stage 0: mini tg128 is **0.62x** the 1.7B (same threads, interleaved), so the projected Pixel 8a decode is **8.6 tok/s (7.4-9.9)**: above the 6 tok/s drop line and the 8 tok/s stage-2 line at the midpoint, below 8 at the low end. Smoke: 0 failures, 0 leaks, answer length similar to the 1.7B (median 36-39 vs 41 tokens), wall 1.41-1.43x the 1.7B. Shortlist rank 1 (research-2026-10-20/pixel8-models/SHORTLIST.md).

## Checkpoint
| Item | Value |
|---|---|
| Model | `google/gemma-4-E2B-it` @ `3e22461f65e89153144f8adb70e3b8c2cc9845a7` (created 2026-03-02), not gated; text use only (pipeline tag any-to-any, no mmproj loaded). |
| Licence | Apache-2.0 (card front matter `license: apache-2.0`, link ai.google.dev/gemma/docs/gemma_4_license; card header "License: Apache 2.0"). The unsloth GGUF repo also says apache-2.0. |
| GGUF | `unsloth/gemma-4-E2B-it-GGUF` @ `0314792d7f1f7e229411f620751375812bb9faf2`, `gemma-4-E2B-it-Q4_K_M.gguf`, 3,106,738,272 B, sha256 **`740185b21d22ceb83a11c3aa62ad5842ef32c70f6096d756bbee85a1e4ec34b8`** (= HF LFS oid; checked after download). Mini `<runner>/shared-models/lite/` (appended to SHA256SUMS). llama-bench reports 2.88 GiB, 4.65 B params (PLE tables included). |
| Load + 1 generation | llama-server b11010 (4bc272f) build-cpu on the mini: `model loaded`, n_ctx_slot 4096 (onboarding/srvA.log). Greedy 64-token generation on the first LITEPACKS prompt: finish `stop`, 60 tokens, reasoning_content empty, coherent English (onboarding/gen1.json). Prefill 56 tok/s, decode 19.9 tok/s at -t 2 under load. **Supported.** |
| Disk | Free before 28.8 GiB; a concurrent Ministral download made "after >= 25 GiB" uncertain, so the download was paused at 0.99 GB and resumed by tools/dl_poll.sh once no other download ran and the projection held (22:22, after 29.0 GiB). Free after: 27.0 GiB. Only Q4_K_M downloaded; Q3_K_M not needed (no RSS stage here). |

## (1) Template and thinking-off
- tools/template_check.sh (mini): two llama-servers `--jinja --reasoning off`, A = embedded template, B = `--chat-template-file` with the HF `chat_template.jinja` (google @ 3e22461f, "Canonical Chat Template, Published 2026-07-09"). Renders the first LITEPACKS prompt (vit-hum-001) through `/apply-template`.
- A vs B: **byte-identical** for kwargs absent, `enable_thinking:false` and `enable_thinking:true` (onboarding/renders.json). The template texts differ only by the HF header comment and unsloth's pre-serialized tool-arguments branch (tool calls, never reached).
- Thinking: the template opens the system turn with `<|think|>\n` only when `enable_thinking` is true (HF template l.186-195). The engine sends no enable_thinking kwarg on this path (budget 256 with BOAR_THINK_KWARG unset), so the render is `<|turn>system\nYou are Boar...<turn|>\n<|turn>model\n` with **no `<|think|>`**. Card: on E2B/E4B thinking off emits no empty thought block. Checked: reasoningTokens 0 on 11/11 Gemma generations (gen1 + 2 x 5 smoke), no `<|channel>` / `<channel|>` / `<|think|>` in any answer.
- Previous thoughts: the template's strip_thinking macro removes `<|channel>...<channel|>` from history; BOAR's single-turn requests carry no history anyway.

## (2) Sampling (card "Best Practices" + generation_config.json, fetched 2026-10-20)
- Vendor: "temperature=1.0, top_p=0.95, top_k=64" for all use cases; generation_config.json the same. No min_p (set 0).
- V = gemma4-e2b.patch: adapter `BOAR_SAMPLER_JSON ??= {"top_k":64,"top_p":0.95,"min_p":0}` + samplerFor default temperature 0.7 -> 1.0 in be/server.ts (per-item health T 0 kept). Trace shows sampler temperature 1 and the override.
- E = gemma4-e2b-engsamp.patch: model swap only, engine 0.7/40/0.95/0.05.
- Both patches repoint the `qwen3-1.7b-q4km` MODELS entry (file + sha) and the catalog label. **Deviation from the Qwen3.5-2B patches:** the catalog `sizeBytes` stays at the 1.7B's 1107409472, because the real 3.1 GB file is above the compact cap (isCompactModel <= LOW_RAM_MAX_MODEL_BYTES) and would move the model off the compact tier (other prompts/declines). Only the weights differ.

## (3) Quant
Q4_K_M only (the shortlist's RSS fallback Q3_K_M matters on the phone, stage 3, not here). Q4 vs Q6/Q8 at this size not tested (UNKNOWN). Note: a large share of the 4.65 B params are PLE embedding tables, which are cheap per token; quant error there is less likely to matter than in the 2.3 B effective body.

## (4) Context fit
`/tokenize` over the 103 LITEPACKS prompts (gate17 dumps): min 242, median 440, max **1129** (vit-hum-004); + max nPredict 512 = 1641 vs -c 4096 (SWA 512 window on most layers, handled by llama.cpp). The harness max_tokens is 512 + 256 = 768: worst case 1897, fits.

## (5) Embeddings
Unchanged (bge-small-en-v1.5 q8_0, ec38e8da): retrieval does not depend on the generator. The HF fine-tune scan (memory rule item 6) was not done here (UNKNOWN).

## Stage 0: speed (mini, llama-bench b11010 CPU, -t 4 -p 512 -n 128 -r 3, interleaved 1.7B / Gemma x 2; onboarding/bench/)
| Rep | 1.7B pp512 | Gemma pp512 | 1.7B tg128 | Gemma tg128 | tg ratio | loadavg 1m |
|---|---|---|---|---|---|---|
| 1 | 120.9 | 116.0 | 30.29 | 18.93 | 0.625 | 9.5 / 13.4 |
| 2 | 117.1 | 83.5 | 28.27 | 17.18 | 0.608 | 13.8 / 16.0 |
Mean tg ratio **0.616**. Projected Pixel 8a decode = 12-16 tok/s (measured 1.7B) x 0.616 = **7.4-9.9 tok/s, midpoint 8.6**. Above the 6 tok/s drop line; the shortlist estimate was 7.5-11. The mini was loaded (other lab jobs held both gen slots), which is why interleaving was used; the absolute numbers are depressed, the ratio is the usable figure. Caveat: the M4 has far more memory bandwidth than the Tensor G3, and the PLE lookup cost and paging on Android are unmeasured (shortlist UNKNOWN).

## Smoke (5 K0 items: lan-cmp-004, vit-hum-004, st-qa-money-se-007, lan-exp-003, vit-sci-002; run_arm.sh IDS_OVERRIDE, mini, seed 42)
| Run | errors / gen failed | reasoning tok / leak | output tokens | median | sum totalMs | ratio vs 1.7B | harness decode tok/s |
|---|---|---|---|---|---|---|---|
| 1.7B ref (qwen35-2b/onboarding/smoke-ref17, same tree + ids) | 0 / 0 | 0 / 0 | 55 53 41 35 41 | 41 | 16.0 s | 1.00 | 43-51 |
| Gemma V (vendor) | 0 / 0 | 0 / 0 | 56 36 41 33 32 | 36 | 22.8 s | **1.43** | 32-37 |
| Gemma E (engine) | 0 / 0 | 0 / 0 | 54 39 33 33 50 | 39 | 22.6 s | **1.41** | 34-37 |
- Answer length is similar to the 1.7B (no runaway, unlike Qwen3.5-2B V). Wall ratio comes from per-token speed (and possibly a different mini load than the ref run).
- Behaviour: Gemma says "The context provided does not contain..." on items without a source, also behind the memory-warning prefix (vit-hum-004, vit-sci-002 under V): it abstains where the 1.7B confabulated. Under GATE v2 labels such answers are declines/refusals, so the screen's false-refusal clause matters for this model.
- Judge on 5 items (information only): V CE 2/5, E CE 3/5, 1.7B control CE 4/5. Haiku calls 10 + 10 = 20. Outputs: onboarding/smoke-vendor, onboarding/smoke-engsamp (E ran as arm `g4e2bengsamp`, moved).

## Decision
Proceed to the GATE v2 screen with both samplers (cheap; the smoke does not separate them). Criterion: GEMMA4-criterion.md.

UNKNOWN: Pixel 8a decode and PSS (PLE paging); Q4 vs Q8 quality; HF fine-tunes of gemma-4-E2B-it; whether the app maintainer's native llama.cpp build has the `gemma4` arch.
