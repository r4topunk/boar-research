# Deep research: Gemma 4 E2B as the BOAR 8 GB Android engine (2026-10-21)

TL;DR: Gemma 4 E2B is the best small model we have screened (only one to pass all four GATE v2 screens, keeps [n] citations, Apache-2.0, 73/73 on the Pixel 8a without a kill), but it is **not a proven default**: judged quality on the phone equals Qwen3-1.7B (+0.008, CI −0.020…+0.039 on the 57 parity ids) and sits 0.083 below the 4B, at 1.5× the 1.7B's time and 1.4 GB more PSS. Its desktop +0.03 comes from refusing less. Recommendation: ship it to the app maintainer as an **opt-in catalog entry** ("fewer refusals, slower") with the thinking flag pinned, keep Qwen3-1.7B as the 8 GB default, and spend the pre-freeze device time on the thinking/memory gates (T1, T3) rather than on more model swaps.

Method: Workflow wf_2b94e24e (10 agents: 7 Haiku sweeps, one angle each; 2 Opus adversarial verifiers over the 47 load-bearing claims; 1 Opus completeness critic). 92 findings, 46 verdicts (35 confirmed, 10 corrected, 1 unverified), 14 new findings. Raw results: session scratchpad gemma-dr-full.json; journal in the workflow transcript dir. Our own measurements (today): arms/gemma4-e2b/{GEMMA4.md, CONFIRM.md, phone/GEMMA4-PHONE.md, phone/GEMMA4-PHONE-JUDGE.md}.

## 1. Verified facts that matter (source, date)

| Topic | Fact | Source |
|---|---|---|
| Size | 2.3B effective, 5.1B with the per-layer-embedding (PLE) tables; 35 layers; 512-token sliding window + global layers; 128K ctx (LiteRT build: 32k) | HF card google/gemma-4-E2B-it; ai.google.dev model_card_4 (2026-07-30) |
| Licence | Apache-2.0 on the card, the unsloth and ggml-org GGUF repos and the LiteRT-LM build; "first in the Gemmaverse under Apache 2.0" (Google OSS blog 2026-04-02). Open: whether a separate use policy or NOTICE travels with the weights | HF, opensource.googleblog.com |
| Thinking | Enabled only by `<|think|>` at the start of the system prompt; output `<|channel>thought … <channel|>`; E2B/E4B emit **no** empty thought block when off. llama.cpp's llama-server defaults `--reasoning auto` and `--reasoning-budget -1` (unrestricted), which is the likely reason the model thought by default on the phone; `enable_thinking:false` as a template kwarg is the documented switch (Unsloth guide; PocketPal fixed the same bug app-side in v1.14.0, 2026-04-21) | HF card; llama-server README; pocketpal-ai #677 |
| Sampling | Google recommends T 1.0 / top_p 0.95 / top_k 64 for all uses; our engine runs 0.7/40/0.95/0.05 (the "engine sampler" arm) and the "vendor" arm used 1.0/0.95/64; both passed the screens | HF card |
| Files | unsloth GGUF: Q4_K_M 3.11 GB (ours, sha 740185b2), UD-Q4_K_XL 3.18, Q3_K_S 2.45, UD-IQ2_M 2.29, Q8_0 5.05; re-uploads Apr 11 (template) and Jun 9 (MTP). ggml-org (Google-recommended): Q4_0 2.84 GB, Q8_0 4.97, BF16 9.31, source list includes the QAT checkpoint. Unsloth QAT: UD-Q4_K_XL 2.62 GB (top-1 98.2 %, KLD 0.0017 vs BF16), UD-Q2_K_XL 2.19 GB (97.8 %) | HF repos; unsloth.ai/docs/models/gemma-4/qat |
| Google's mobile runtime | LiteRT-LM E2B 2.58 GB (0.79 GB decoder + 1.12 GB mmapped embeddings; mixed 2/4/8-bit); S26 Ultra CPU 557 prefill / 47 decode tok/s at 1733 MB, GPU 3808 / 52 at 676 MB; E4B CPU 18 tok/s; MTP (speculative) up to 1.5× CPU / 2.2× GPU; **no Pixel/Tensor rows**; NPU variant targets an IoT SoC; Kotlin/C++ stable, no React Native binding; AICore/Gemini Nano path is irrelevant on GrapheneOS | developers.google.com/edge/litert-lm/models/gemma-4 (2026-09-04); litert-community card |
| llama.cpp | Gemma 4 supported since ~b8660 (April 2026); b11010 (our pin, commit 4bc272fd, 2026-09-17) has it; llama.rn 0.13.0-rc.4 synced to b11010; issue #21690 (ctx-checkpoints RAM growth on Gemma 4, 16K prompts, stale-closed) → check whether llama.rn/the Kotlin wrapper use ctx checkpoints; forge #54: after d7ff074 the reasoning-budget sampler defaults to INT_MAX when thinking tags are registered (unbounded answers if thinking leaks) | github issues/releases |
| Quality (external) | Google card: MMLU-Pro 60.0, GPQA-D 43.4, LCB 44.0; no IFEval/SimpleQA for E2B. Qwen3-1.7B non-thinking MMLU-Redux 64.4 / GPQA 28.6 / IFEval 68.2. One RAG paper (arXiv 2609.15242, top-k 1, 4B judge): E2B faithfulness 0.784, factual correctness 0.423 (second of 7, within 0.026 of qwen3-4b), answer relevancy lowest | model cards; arXiv |
| Thermal | No public sustained-decode numbers for E2B on Android; every external figure is a burst. Ours: 10.5 tok/s burst → 7.0 tok/s over 13 min (thermal status 1 mid-run) | our runs |

## 2. Corrections to things we believed or were told
- "Thinks by default" is a **runtime** default (llama-server `--reasoning auto`, budget −1), not a GGUF template defect; the template default is off. Keep `enable_thinking:false`; add `reasoning_budget:0` and a hard `n_predict` cap as guards, especially in the app maintainer's Kotlin path.
- The 3.11 GB GGUF is text + PLE; vision/audio encoders live in a separate mmproj (not loaded). Memory is dominated by the PLE tables (1.12 GB in the LiteRT build) plus KV; a readahead of the whole PLE table may explain part of the 4.5 GB PSS.
- Unsloth's "Q4_0 loses 11 % top-1" is their own 3.35 GB Q4_0, not ggml-org's 2.84 GB (QAT-sourced) file; do not quote it against the official GGUF.
- "72 % less memory" (Unsloth QAT) is vs BF16; vs our Q4_K_M the QAT file saves ~0.5 GB.
- No launch date is safely quotable (press 2026-04-02; cards/report July 2026); omit from any maintainer text.

## 3. Our measurements today, against the research
| Question | Result | File |
|---|---|---|
| Desktop quality vs 1.7B | +0.029 U pooled 2 seeds K0 (CI +0.009…+0.048); K1 +0.017 (CI crosses 0); gain = fewer refusals, U on covered items flat | CONFIRM.md |
| Phone speed (Pixel 8a) | 12.6 s/answer, 10.5 tok/s burst; 73 q: 11.8 s p50, 7.0 tok/s sustained, PSS 4.52–4.63 GB, no kill; 1.7B 8.3 s, 13.9 tok/s, 3.25 GB | phone/GEMMA4-PHONE.md |
| Phone quality (57 parity ids, Haiku) | vs 4B phone −0.083 (−0.123…−0.047); vs desktop Gemma +0.001 (parity holds); vs 1.7B desktop +0.008 (n.s.) | phone/GEMMA4-PHONE-JUDGE.md |
| Thinking | leaked 3/3 answers without the flag (42 s each at the cap); 0/83 with `enable_thinking:false` | phone/ |
| Pending | GEMMA-VS-4B on MAIN 97 K0 (direct), N3 GEMMA-PACKS (K3 vs K0) | agent running |

## 4. Decisions (fixed now)
- D1. Qwen3-1.7B stays the 8 GB default; Gemma 4 E2B becomes an **opt-in catalog entry** proposal ("Gemma 4 E2B: answers more questions, slower, needs ~1.5 GB more RAM"), not a default flip. Grounds: §3 phone quality = 1.7B, 1.5× time, PSS 4.6 GB on 7.15 GiB.
- D2. Any Gemma entry carries three guards: `enable_thinking:false` (template kwarg), reasoning budget 0, hard `n_predict` cap, plus a post-filter that strips `<|channel>…<channel|>`. Hard gate on the app maintainer's build, not only ours.
- D3. Exact file pinned in the entry: unsloth gemma-4-E2B-it-Q4_K_M.gguf, sha 740185b21d22ceb83a11c3aa62ad5842ef32c70f6096d756bbee85a1e4ec34b8, 3,106,738,272 bytes (the file every number in this report was measured on). The QAT UD-Q4_K_XL (2.62 GB) and ggml-org Q4_0 (2.84 GB) are candidates only after T9.
- D4. Model-swap line for 8 GB is closed for the bounty window: Jan, SmolLM3, granite-1b, Qwen3.5-2B, FOTAPOL, OCC-RAG, Q8 all NO-GO; MIN3CITE PASS but 3× time; Gemma = parity. The levers that moved the metric are honesty/refusal handling (REFUSE-UNSUPPORTED PASS) and citation prompting, not model size.

## 5. Options (exploration, after the freeze)
- O1. LiteRT-LM path (Kotlin, GPU): Google's flagship numbers are 4–5× llama.cpp CPU on the same model; no Pixel row, no RN binding, mixed 2-bit weights. A one-day spike on the app maintainer's Kotlin app could price it; only if the app maintainer wants a second runtime.
- O2. QAT quant (T9) to buy ~0.5 GB of headroom.
- O3. E4B as the 12 GB tier (POCO X6) instead of the 4B: Google's CPU numbers put it at ~18 tok/s flagship; unmeasured here.
- O4. Gemma-specific prompt/sampling: vendor 1.0/0.95/64 vs engine sampler were equal on the screens; not a lever.

## 6. Tasks (ranked; pre-freeze = by 10-22)
| T | Question | Method | Cost | Unblocks |
|---|---|---|---|---|
| T1 | Thinking off and bounded on b11010 in the app maintainer's Kotlin path | render the prompt with/without the kwarg on the mini (`<|think|>` grep), `git merge-base --is-ancestor d7ff074 4bc272fd`, grep common/chat.cpp for reasoning defaults; 20 prompts through his build, grep `<|channel>`, max tokens | 1.5 h, 0 judge | sending the entry |
| T2 | Memory headroom under real use | per-question smaps_rollup (Rss_File/Anon), mmap on/off, ctx length, ctx-checkpoint use in llama.rn/Kotlin, one run with 2–3 background apps, ApplicationExitInfo | 3 h device, 0 judge | memory yes/no, ctx setting |
| T3 | Safety of "refuses less" | the 64 safety probes + health-warning set on E2B thinking off with the deterministic layers; count unsafe/unsupported vs 1.7B | 1 h, ~130 Haiku | opt-in entry text |
| T4 | GEMMA-VS-4B + GEMMA-PACKS (running) | MAIN 97 K0 direct; K3−K0 diff-in-diff on 80 self-tests | ~450 Haiku | §3 completion |
| T5 | Stack transfer | E2B with/without X2b on the 180 pack-matched self-tests; token counts under the 262k-vocab tokenizer | 2 h, ~360 Haiku | pack claims under Gemma |
| T6 | QAT quant | UD-Q4_K_XL vs Q4_K_M: KLD tool (arms/quant17) + PSS on the Pixel + one K0 screen | 2 h, ~180 Haiku | O2 |
| T7 | Second 8 GB SoC (Galaxy A15 G99) | 20-question speed/PSS run | 2 h, 0 judge | global vs per-device default |
| T8 | Licence/NOTICE check + competitor READMEs | web, 1 h | 0 | maintainer text |

## 7. Risks of switching now and mitigations
1. Thinking flag dropped in the native build → unbounded answers, KV growth, silent timeouts. Mitigation: D2 guards + T1 as a hard gate on his build.
2. LMK kills under real use (4.6 GB PSS; the 4B died at 4.4 GB; Android 17 per-app memory limiter coming, Pixel first). Mitigation: T2 with background apps, ctx cap, QAT file, runtime fallback to the 1.7B below a free-RAM threshold, both models in the catalog.
3. Quality gain is refusal-driven and may hide unsafe answers; sustained decode is ~half the 1.7B's. Mitigation: T3 before any text that says "better"; present Gemma as "answers more, slower", never as "more accurate".

## 8. UNKNOWN
- Whether a Gemma use policy/NOTICE is attached to the Apache-2.0 weights (T8).
- GrapheneOS per-app memory-limiter behaviour; the exact adb command (the Android blog links it but does not print it).
- Whether llama.rn at b11010 creates context checkpoints (issue #21690 exposure).
- E2B thinking-off vs on deltas and IFEval/SimpleQA in the technical report PDF (not read).
- Whether the app maintainer can change the default after the freeze through catalog config alone.
