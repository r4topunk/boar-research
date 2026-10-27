# MINISTRAL3-3B onboarding (2026-10-20, before any judged screen)

TL;DR: mistralai/Ministral-3-3B-Instruct-2512 (Apache-2.0) has an **official** mistralai Q4_K_M GGUF, and it loads in llama.cpp b11010 on the mini (text model only, no mmproj). The GGUF-embedded template renders the LITEPACKS prompt byte-identically to the HF chat_template, with exactly one BOS. Prompts fit -c 4096 (max 1130 + 512 tokens). The 5-item smoke has 0 failures and 0 template-token leaks. **Speed:** desktop tg is 0.541x the 1.7B in the clean bench round, which projects to **6.5-8.7 tok/s on the Pixel 8a** by the shortlist rule (12-16 x ratio), so the model passes the >= 6 gate. The projection from the measured 4B (3.6-6 x 1.16 = 4.2-7.0 tok/s) is borderline. **Answers are about 2.4x longer than the 1.7B's** (median 100 vs 41 tokens), and smoke wall time is 1.9-2.0x the 1.7B.

## Checkpoint
| Item | Value |
|---|---|
| Model | `mistralai/Ministral-3-3B-Instruct-2512` @ `b35d4dfe56c142746f54dbd64f579faab2744308` (created 2025-10-31). 3.4B LM + 0.4B vision encoder (`Mistral3ForConditionalGeneration`). Text config: 26 layers, hidden 3072, 32 heads / 8 KV heads x 128, vocab 131072, tied embeddings, YaRN rope (factor 16 over 16384), 256k context. The Instruct variant has no thinking mode. |
| Licence | Apache-2.0 (card front matter of the base and GGUF repos, plus the card's "Apache 2.0 License" section; neither repo is gated). The card adds the line "You must not use this model in a manner that infringes ... any third party's rights", which places no extra restriction. Neither repo ships a LICENSE file (the card links apache.org). |
| GGUF | **Official** `mistralai/Ministral-3-3B-Instruct-2512-GGUF` @ `eb599d408350ea2bb60452cb86be7c7b2fc28227`, `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf`, 2,147,023,008 B, sha256 **`9ed150d4367e68df0ac8e1540f6ddc65b42d0ee26378329d1ecbca60f93fc5f8`** (= HF LFS oid; checked after download). The unsloth (fd46fc37..., 2,146,497,824 B) and bartowski repos were not used. Stored at mini `<runner>/shared-models/lite/` (sha appended to SHA256SUMS). The mmproj (`...-BF16-mmproj.gguf`) was not downloaded or loaded. |
| Disk | Free before: 28.76 GiB. Download 2.0 GiB. Free after: 29 GiB by `df -g` (other jobs had freed space). Only the Q4_K_M was downloaded, so nothing needs deleting. |
| Load | llama-server b11010 (4bc272f) build-cpu: `model loaded` in 1.4 s, n_ctx_slot 4096 (onboarding/srvA.log). One greedy generation on vit-hum-001 gave 113 tokens, finish `stop`, coherent English (onboarding/gen1.json). The `mistral3` arch is supported. |

## (1) Template, system prompt, BOS
- tools/template_check.sh (mini, 0 generation) starts two llama-servers with the adapter's flags (`--jinja --reasoning off --reasoning-format deepseek -c 4096`). A uses the embedded template. B uses `--chat-template-file` with the HF `chat_template.jinja` (onboarding/hf-chat_template.jinja, @ b35d4dfe). Both render the first LITEPACKS prompt (vit-hum-001; real engine system + user messages from the gate17 dumps) through `/apply-template`.
- Rendered prompts A vs B are **byte-identical**, both with kwargs absent and with the engine's `enable_thinking:false`. The template ignores that kwarg (onboarding/renders.json). Format: `[SYSTEM_PROMPT]<engine system>[/SYSTEM_PROMPT][INST]<user>[/INST]`.
- System prompt: the engine always sends a system message. The template then puts it in `[SYSTEM_PROMPT]` and **does not inject** Mistral's default "Le Chat" system prompt (hf-SYSTEM_PROMPT.txt), which it adds only when messages[0] is not a system message. Checked: the system text sits inside the `[SYSTEM_PROMPT]` block.
- BOS: the template emits `bos_token`. llama-server blanks it in the rendered text and adds BOS at tokenization, and `/tokenize` with add_special=true gives `<s>`(1), `[SYSTEM_PROMPT]`(17), ... **One BOS, no double BOS.** The HF render begins `<s>[SYSTEM_PROMPT]`, so the two are token-equivalent.
- Engine kwargs that do not apply: the engine sends `thinking_budget_tokens 256` and `enable_thinking:false`, as it does for the 1.7B. With `--reasoning off`, smoke reasoningTokens were 0 on 10/10, and no `[INST]`, `[/INST]`, `[SYSTEM_PROMPT]` or `</s>` appears in any answer text.

## (2) Sampling (vendor card "Recommended Settings", fetched 2026-10-20)
- "Use a **temperature below 0.1** for daily-driver and production environments". No top_k, top_p, min_p or penalty is named, and generation_config.json has none either.
- V (`ministral3-3b.patch`): the samplerFor default temperature changes from 0.7 to **0.1** (be/server.ts), with `BOAR_SAMPLER_JSON ??= {"top_k":0,"top_p":1,"min_p":0}` in the adapter, which neutralises the samplers the card does not name (vLLM defaults). Health items keep the engine's T 0. The trace records `runtime.sampler.temperature 0.1` and `sampler.override` (checked in the smoke).
- E (`ministral3-3b-engsamp.patch`): model swap only, with the engine sampler 0.7/40/0.95/0.05.
- Greedy was not run as a separate arm. T 0.1 with neutral top_k is near-greedy, and GREEDY on the 1.7B was a NO-GO.

## (3) Quant
- The official repo offers Q4_K_M, Q5_K_M (2.47 GB), Q8_0 (3.65 GB) and BF16. Q4_K_M is the shortlist's size and the only one under the RSS budget. Q4 vs Q8 at 3B is not tested here (UNKNOWN). QUANTLITE found Q8_0 = Q4_K_M on the 1.7B.
- RSS (desktop, adapter peakRssMb including node and the embedder): 4.63 GB vs 2.65 GB for the 1.7B, so +2.0 GB. The shortlist's phone estimate is 3.7 GB (3.5 with a q8_0 KV cache). Phone PSS is unmeasured (stage 3).
- **Catalog size held at the 1.7B value:** the real file is 2.147e9 B, which is above `LOW_RAM_MAX_MODEL_BYTES` 1.6e9. If the real size were used, `isCompactModel` would turn false and change declines and routing. Both patches keep `sizeBytes 1107409472` so that only the weights differ. A product adoption would have to set `answerTier: "compact"` (or move the threshold) explicitly.

## (4) Context fit
- `/tokenize` over all 103 LITEPACKS prompts (gate17 dumps: K0 MAIN 75 + K1 screen 28): min 235, median 432, max **1130** (vit-hum-004). With max nPredict 512 the worst case is 1642 vs `-c 4096`. Token counts are within about 1 % of the Qwen tokenizer's (1133 max).
- KV f16 at 4k = 0.44 GB (26 L x 8 KV x 128), against 0.11 GB for the 1.7B at the same context.

## (5) Stage 0 speed (mini, llama-bench b11010, -t 4 -p 512 -n 128 -r 3, interleaved, two rounds; the other gen slot was busy throughout)
| round (load 1 min) | Qwen3-1.7B tg / pp | Ministral-3-3B tg / pp | Qwen3-4B-2507 tg / pp | tg Min / 1.7B | tg 4B / 1.7B |
|---|---|---|---|---|---|
| r1 (13.7-18.8) | 27.1 / 121 | 17.0 (sd 4.8) / 61 | 28.1 / 69 | 0.63 | 1.04 (invalid: the 1.7B ran at 4B speed) |
| **r2 (10.8-15.1)** | 59.8 / 178 | **32.4** / 86 | 27.9 / 71 | **0.541** | 0.466 |
- Round 1 is load-contaminated (the 1.7B ran at half speed and Ministral's sd was 28 %). Round 2 matches the bandwidth prediction (1.107 / 2.147 GB = 0.516) and the 4B's (2.50 / 2.147 -> Ministral / 4B 1.16 measured, 1.16 predicted).
- In-situ decode in the smoke (adapter, concurrent jobs): 29.6-30.5 tok/s vs 47-53 for the 1.7B control, a ratio of about 0.61.
- **Projected Pixel 8a decode** (shortlist rule: 12-16 tok/s x tg ratio 0.541) = **6.5-8.7 tok/s, >= 6, the gate passes**. Cross-check from the measured 4B (3.6-6 tok/s x 1.16) = 4.2-7.0 tok/s, which straddles 6. The two anchors disagree because the 4B ran slower on the phone than its bandwidth predicts (desktop 4B / 1.7B = 0.47 gives 5.6-7.5, against the measured 3.6-6). Ministral's file size sits between the two anchors, so the truth is probably near 6-7 tok/s. Prefill is 0.49x the 1.7B (pp512), about the same as the 4B.

## (6) Smoke (5 K0 items: lan-cmp-004, vit-hum-004, st-qa-money-se-007, lan-exp-003, vit-sci-002; run_arm.sh IDS_OVERRIDE, mini, seed 42; reference = the mini control trace lpctl-K0-screen-s42)
| Run | generation_failed / errors | template leak | output tokens per item | median | sum totalMs | ratio vs 1.7B | decode tok/s |
|---|---|---|---|---|---|---|---|
| 1.7B mini control | 0 | 0 | 55 53 41 35 41 | 41 | 15.7 s | 1.00 | 47-53 |
| Ministral V (T 0.1) | 0 | 0 | 81 122 108 54 100 | 100 | 29.7 s | **1.89** | 29.6-30.3 |
| Ministral E (engine) | 0 | 0 | 99 122 98 66 113 | 99 | 30.7 s | **1.96** | 29.7-30.5 |
- The answers are longer and use markdown bold. The persona asks for 2-3 short sentences, and Ministral writes 3-4. They keep the warning prefix on memory answers, as the 1.7B does.
- Judge (5 items, informational only): control corr 1.0/1.0/1.5/4.5/1.0 (CE 4/5). V 3.0/1.0/2.5/4.0/1.0 (CE 2/5). E 3.0/1.0/2.5/3.5/1.0 (CE 2/5). lan-cmp-004 flips from a confident wrong "moose heavier" to "bison heavier" (warned). Both variants still give confident wrong facts (Gríma "kills Saruman for power"; Japan density 570/km², or 126/km² in E). Not a decision.
- Haiku calls: 10 (V) + 10 (E) = 20. Outputs are in onboarding/smoke-vendor, onboarding/smoke-engsamp (run as arms `ministral3-3b` / `min3engsamp`, then moved here).

## (7) Wall time vs Qwen3-1.7B
On the 5 items, 1.9-2.0x (sum of totalMs). The cause is about 0.6x decode speed times about 2.4x answer length, partly offset by retrieval and the shared prefill share. On the phone at 6.5-8.7 tok/s, a 100-token answer costs 11-15 s of decode plus a prefill at about half the 1.7B's speed. The screens report the per-run mean totalMs ratio on the same items.

## Decisions for the screen
- Both V (vendor T 0.1, primary) and E (model only) are screened under GATE v2 on K0 and K1 and frozen in MINISTRAL-criterion.md before generation, so that a NO on V cannot be blamed on the sampler alone.
- Swap mechanism (same as QWEN35-2B): the patches repoint the adapter's `qwen3-1.7b-q4km` MODELS entry at the Ministral GGUF and keep the catalog entry's size, so requests, routing, prompts, declines and the compact tier stay byte-identical. Traces still say `model: qwen3-1.7b-q4km`, and `versions["model.sha256"] = 9ed150d4...` identifies the weights.

## Deviations
- The bench shared the mini with null-cal and gate17 jobs (both gen slots busy for 11 min before the bench got gen2). Round 1 is reported but not used.
- llama-server at the adapter's verbosity does not print arch/BOS metadata. BOS was checked through `/tokenize` instead.

UNKNOWN: Pixel 8a decode/PSS (the two anchors give 4.2-8.7 tok/s); Q4_K_M vs Q8_0 at 3B; whether the persona's length instruction can bring the answers back to 1.7B length without loss.
