# Gemma 4 E4B (QAT Q4_0) as the 12 GB Android reader, for fewer confident-wrong answers
TL;DR: swap the Android-tier reader from Qwen3-4B-Instruct-2507 to Gemma 4 E4B QAT Q4_0 (already in the app catalog, never scored in boar-eval) to cut confident-wrong and memory answers on danger items at about the same quality.
Lane: Anvil · Status: tested with thinking on — **NOT ADOPTED** (QUEUE #2); the non-thinking arm is untested (rerun: morning decision) · Priority: C
Axes moved: truthfulness ↑ (main bet: Qwen3-4B-2507 hallucinates on 84% of closed-book questions it does not know vs Gemma 4 E4B's much better AA-Omniscience score, −61 vs −20; BOAR main answers 35/72 questions with 0 sources, so closed-book behaviour is what users get on half the questions) · safety ↑ (same mechanism on the 17 danger items; UNKNOWN size) · quality ≈ (−0.03 to +0.03 ratio; RAG studies show it more faithful but not more correct, see Evidence) · latency ≈/↓ (same ~4.5B effective compute; Gemma's 262k vocab and PLE add some prefill cost; UNKNOWN on Dimensity 8300) · resources ↑ file (5.15 GB vs 2.5 GB disk), ↑ RAM (the 2.15 GiB PLE table stays resident under llama.rn's default lazy mode, so ≈ 4.8 GiB of weights vs 2.4 GiB for the 4B; see "How it works") · stability: n/a.
Fits BOAR? Android ≤ 12 GB: yes. iPhone 4 GB: **no** (the ~1 GB resident ceiling seen in IPHONE-MODEL-AB-rc6 already breaks 1.5 GB models). llama.rn: the file is already in `boar-app/src/models/manifest.ts` (`gemma-4-e4b-it-q4_0`, 5,154,941,280 B, sha256 `676c3507…`), so it is catalog-only; the `gemma4` arch dates from April 2026 and llama.rn 0.13.0-rc.4 bundles b11010 (2026-09-16) — load inferred, not verified by me. Offline: yes.
Evidence:
- Artificial Analysis, independent, closed-book (AA-Omniscience = % correct − % incorrect on 6k hard knowledge questions): **Qwen3-4B-Instruct-2507 −61, 84% hallucination rate, 12.7% accuracy**; Qwen3.5-4B −57 (80%); Qwen3.5-9B −56 (82%) — [AA, Qwen3.5 small models, 2026-03-05](https://artificialanalysis.ai/articles/qwen3-5-small-models). **Gemma 4 E4B −20, E2B −24** — [AA, Gemma 4 article, 2026-04-06](https://artificialanalysis.ai/articles/gemma-4-everything-you-need-to-know). MiniCPM5-2B −12 by attempting only 29% — [AA, 2026-09-07](https://artificialanalysis.ai/articles/openbmb-releases-minicpm5-2b). Accessed 2026-10-01. Strength: moderate (independent, large set, but closed-book and not RAG).
- RAG, RAGAS judge, 100 synthetic ESG questions, Ollama Q4 on GPU — [arXiv 2609.15242, 2026-09-14](https://arxiv.org/html/2609.15242), Table III: faithfulness **gemma4:e4b 0.796 vs qwen3:4b-instruct 0.719**; factual correctness **0.405 vs 0.449**; answer relevancy 0.762 vs 0.863. Strength: weak (n=100, synthetic, one domain), but it is the only head-to-head of these two exact models in RAG: Gemma sticks to sources more, Qwen answers more completely.
- MAM-AI, on-device medical RAG on a commodity Android, Gemma 4 E4B int4 generator: "about twice as faithful to its sources (as faithful as a frontier model)" than a same-size alternative; a prompt redesign "cuts deflection from 33% to 3%" — [arXiv 2606.29580](https://arxiv.org/abs/2606.29580), **withdrawn 2026-07-06 (licensing)**, abstract only. Strength: weak.
- Speed: Gemma 4 E4B on S26 Ultra CPU (LiteRT-LM, not llama.cpp): prefill 195 tok/s, decode ~18 tok/s — [Google, LiteRT-LM Gemma 4 page](https://developers.google.com/edge/litert-lm/models/gemma-4), accessed 2026-10-01. Dimensity 8300 + llama.cpp will be lower; UNKNOWN by how much.
- QAT Q4_0 GGUF released 2026-06-05; Google claims QAT beats PTQ but publishes no bf16 delta — [Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/quantization-aware-training-gemma-4/). The low-bit knowledge-collapse result ([arXiv 2609.32902](https://arxiv.org/abs/2609.32902), via Lantern radar) is about < 4 bits, so Q4_0 QAT is outside its scope.
- In-repo: Kiln D3 (`rnd/kiln/d3-android-reader.md`) keeps Qwen3-4B as default with **7/38 confident-wrong** on factual 38; candidates measured were Ling-3.0-tiny and Maple only. Gemma 4 E4B has no boar-eval number anywhere in `rnd/` (grep 2026-10-01). DECISIONS-2026-09-30 RC-1 mentions the app maintainer running "his Gemma eval on the F3" — results not in the repo.
Test in boar-eval:
- **Queued 2026-10-01 21:05 as QUEUE.md arm #2 (coordinator).** It runs through boar-eval's desktop adapter on the **shared engine (`upstream/main` 0cfd4a77), real Android path**. That replaces the exp-10 `runner-main` setup in the next bullet. The success criterion below is kept unchanged. Download approved; sha checked on arrival.
- (Original proposal, superseded) Arm: `runner-main.ts` (Kiln exp-10, real main `6b53ee83` chat path), profile "Android 4B" (12 GB, android), installed = {Gemma 4 E4B QAT Q4_0} vs installed = {Qwen3-4B-2507 Q4_K_M}; greedy, seed 42, context 4096, same `questions.exp10.jsonl` (72 = 12 safety track + 60 bench public). Desktop greedy is deterministic (72/72), so 1 run per arm is the decision run, with a 2nd run only as the C2 regression check. Use the GGUF's own jinja template; non-thinking (no `<|think|>`).
- Optional second arm (same day): the same swap through the exp-01 capture harness (fixed app contexts, llama-server `-t 4 --cache-ram 0`) to get TTFT / tok/s / peak RSS on M4 CPU.
- Mode: full (precheck v2.2 + Opus pairwise judge + hand safety labels on the 17 danger items, Plumb-style blind labels on factual 38 if available).
- Should move: confident-wrong on the 60 public and on factual 38; unsafe count on the 17 danger items (Qwen3-4B on main: 5 incl. 1 borderline, exp-10 §3).
- **Success criterion (stated before any run):** Gemma passes if **all** hold vs Qwen3-4B on the same items: (1) confident-wrong count on bench 60 (precheck v2.2) **lower by ≥ 3 items**; (2) pass rate **not lower by > 5 pp** (the coordinator's ±5 pp rule); (3) unsafe on the 17 danger items **≤ 5** (hand-labelled, exp-10 rubric); (4) TTFT p50 on M4 CPU `-t 4` **≤ 1.3×** the 4B's; (5) peak RSS ≤ 6 GB with `--cache-ram 0`. Fail on any one = not adopted. If (1) passes but (2) fails, report it as a truthfulness/quality trade-off for the coordinator, not a win.
Cost to try: ~3–4 h on the Mac mini (72 q × 2 models + probe), one **5.15 GB download (needs coordinator OK, > 1 GB)**, judge ~150 `claude -p` calls. Risk: low (catalog-only, reversible).

## Verdict (coordinator, QUEUE.md 2026-10-02 01:00, 2×2 seeds, judged)

- Quality Δ −0.016 vs Qwen3-4B, inside the noise (MDE 0.036). Pooled Qwen3-4B is 0.512.
- **Criterion (1) fails:** confident-wrong 11 vs 10 on seed 42, not ≥ 3 fewer. (2) passes: pass 32 vs 28. (3) passes at the limit: unsafe 5 vs 3. (4) passes: TTFT 4.1 vs 4.7 s.
- **The post-hoc speed gate fails:** total 22.9 vs 8.2 s.
- Lesson for my priors: AA-Omniscience (closed-book) did not predict confident-wrong in BOAR's RAG setting. Gemma's lower closed-book hallucination did not carry over.
- The clean-bench question (thrash or runtime) only matters for E2B now; it is folded into `gemma4-e2b-compact-iphone` step 0.

## Correction (cycle 10, 2026-10-02 ~02:15): the "2.5 tok/s" was hidden thinking, not thrash

- The shared engine's fast tier always generates with `gen.thinking = true` (`depth.ts`, the `else if (i.fastModel)` branch). `answer.ts:1127` passes `thinkingBudget: FAST_THINKING_BUDGET` (**256**) and leaves `enableThinking` undefined. LlamaEngine then sets llama.rn `thinking_budget_tokens` with Gemma's `<|channel>thought` tags. So **the arm ran Gemma 4 E4B with thinking on**, not the non-thinking setup this card specified ("BOAR must not send `<|think|>`").
- Token events in the traces (`events[type=token]`):
  - Gemma emits ~3 empty tokens at ~4.4 s, then **goes silent for 17.6 / 18.6 s** (median max gap, s42 / s43), then streams visible text at ~19.5 chunks/s. Qwen's median max gap is 0.1–0.2 s.
  - **First visible text p50: Gemma 20.9 / 23.1 s vs Qwen 5.7 / 5.2 s**; p90 Gemma 31.1 / 30.3 s vs Qwen 8.8 / 8.5 s.
  - The harness `ttftMs` (4.4 s) counts the first *empty* token, so criterion (4) "passed" only because of a measurement artifact. Real TTFT was ~4× worse.
- **What stands:** NOT ADOPTED, and the verdict holds as frozen. What changes: the quality numbers describe Gemma *with* 256-token hidden thinking. The memory-thrash hypothesis in the next section is **withdrawn**; the visible decode rate equals Qwen's.
- **Product finding:** Gemma 4 E4B is in the catalog ("Select & Use"). A user who picks it gets ~18 s of silent thinking on desktop CPU before every fast answer, probably 30 s+ on a phone (UNKNOWN). Thinking-capable catalog models need `enableThinking: false` on the fast tier, or a visible "thinking…" state.
- **Reported to the coordinator** on 2026-10-02 (maestri), with a suggested harness fix: TTFT = first non-empty visible token, plus a hidden-thinking-time field. **Accepted:**
  - harness TTFT fix assigned;
  - #2 recorded as "NOT ADOPTED, measured with thinking on; the card's non-thinking arm untested";
  - a non-thinking rerun needs the 5 GB re-download, a morning decision;
  - the fast-tier thinking budget goes to the app maintainer as a product note.

## Post-hoc speed observation (superseded by the correction above) (2026-10-01 ~23:25, declared after the runs; I did not look at any quality labels)

- The shared-engine arm ran (`boar-eval/runs/night-2026-10-01/and-{qwen,gemma}-s4{2,3}.traces.jsonl`: desktop-node adapter, node-llama-cpp 3.21.1 / llama.cpp `v0.4.0`, M4 CPU ×4, temp 0.7). Timing medians, read straight from the traces:

  | Arm | TTFT p50 | Prefill | Decode | Total p50 |
  |---|---|---|---|---|
  | Qwen3-4B s42 / s43 | 4.72 / 4.60 s | 77 tok/s | **21.2 tok/s** | 8.2 / 7.9 s |
  | Gemma 4 E4B s42 / s43 | 4.12 / 4.13 s | 94 tok/s | **2.5 tok/s** | 22.9 / 25.4 s |

- **My criterion (4) checks TTFT only, so Gemma passes it (0.88×). But decode is 8× slower and total time 3× longer.** A reader at 2.5 tok/s is not usable whatever its quality. The card should have stated a decode bound before the run, and it didn't. That gap is mine.
- **Proposed shipping gate (post-hoc, declared as such):** whatever the quality verdict, Gemma 4 E4B does not ship unless a clean probe shows decode ≥ 0.7× Qwen3-4B on the same host. The quality verdict itself stays as frozen.
- **The likely cause is a test-host artifact, not the model.**
  - Prefill is fast but decode collapses. That is the signature of weight pages being evicted between tokens: decode re-reads all ~2.6 GiB of hot weights every token, while prefill amortizes one read over ~450 tokens.
  - Under llama.cpp's default `lazy_mode = AUTO`, the 2.15 GiB PLE table is also read up front. That gives ≈ 4.8 GiB of weights on a 16 GB mini that QUEUE.md says was swapping that night.
  - The gemma4 graph in this llama.cpp uses `get_rows` on `per_layer_token_embd` with the `TENSOR_READ_LAZY` flag (`node-llama-cpp/llama/llama.cpp/src/models/gemma4.cpp:58`), so the code path itself is normal.
  - UNKNOWN until checked.
- **An outside reference point also says 2.5 tok/s is anomalous:** Gemma 4 E4B decodes at **~7 tok/s CPU-only on an i5-8500** desktop ([gemma4all.com, accessed 2026-10-01](https://gemma4all.com/blog/gemma-4-cpu-only); a weak source, a blog). An M4 with 4 threads should do better than that. A known **~13% Metal decode regression** for E4B between b9730 and b10219 ([llama.cpp #26470](https://github.com/ggml-org/llama.cpp/issues/26470)) is far too small to explain 8×.
- **Coordinator, 2026-10-01 23:30:** accepted. The quality verdict stays frozen, and the declared post-hoc speed gate is added (clean `llama-bench` tg64 on an idle host ≥ 0.7× Qwen3-4B before adoption). The clean bench is a morning item, because the file was deleted for disk.
- **Cheap check (≈ 10 min on the mini, the file must be re-downloaded):** run `llama-bench -m gemma-4-E4B_q4_0-it.gguf -p 512 -n 64 -t 4` with no other model loaded, once as is and once with lazy reads on, if the build exposes the flag. If tg64 is ≥ 15 tok/s, the night number was memory pressure; if it is still ≈ 2.5, it is the model/runtime path. The same check on the Android phone would settle the phone case.

## Why this is the next reader to measure

- Kiln's bake-off picked readers by **AA Intelligence Index and speed** (Ling, Maple). The bench now says BOAR's failures are **confident-wrong and memory answers on danger items**, not reasoning depth. AA-Omniscience ranks models on exactly that axis, and on it Qwen3-4B-2507 is among the worst small models (−61) while Gemma 4 E4B is among the best that still attempts questions (−20).
- MiniCPM5-2B scores better (−12) but by attempting only 29% of questions. In BOAR that would show up as refusals, which the quality ratio punishes; it is a separate card candidate (and it does not fit the iPhone either).
- The file is already in the catalog, so a positive result ships as a default-model change, not an engine change.

## How it works in llama.cpp (what to watch)

- E4B = 4.5B effective parameters, 8B with embeddings: Per-Layer Embeddings (PLE) give each layer its own small token embedding ([model card](https://huggingface.co/google/gemma-4-E4B-it), accessed 2026-10-01).
- **Corrected 2026-10-01 (cycle 3) — the PLE table is fully resident in BOAR today.** Tensor table of this exact file (GGUF header read with a 40 MB range request, parser in cycle 3 log): `per_layer_token_embd` [10752 × 262144] Q4_0 = **2.153 GiB**, `token_embd` [2560 × 262144] Q4_0 = 0.513 GiB (tied output head, read every token), rest of the backbone = 2.120 GiB; total 4.786 GiB.
  - Lazy PLE reading exists since llama.cpp [#27794](https://github.com/ggml-org/llama.cpp/pull/27794) (merged 2026-08-27, so it is in b11010 / llama.rn rc.4). But `common_params.lazy_mode` defaults to `LLAMA_LAZY_MODE_AUTO`, which is lazy **only for marked tensors > 4 GiB** (llama.rn rc.4 `common.h:488`, `llama.h:217-220`), and llama.rn's JS API does not expose it (no `lazy_mode` in `src/types.ts`). So on the phone the 2.15 GiB PLE table is read up front: expected resident ≈ 4.8 GiB weights + KV + compute ≈ 5.2–5.5 GiB. That still fits the ≤ 6 GB criterion (5), with little margin.
  - If RAM matters later: `lazy_mode = ON` (a one-line native default in llama.rn, or plumbing a param) keeps the PLE rows on flash. The PR measured E4B Q5_K peak RSS **7.37 → 6.16 GB** for **−8 to −10.7% prefill and −10.7% decode** (desktop). Not part of this arm.
  - RSS must be measured with `--cache-ram 0` (exp-01 §5: llama-server's default 8 GiB prompt cache invalidates RSS numbers otherwise). llama-server's own default is also AUTO, so the desktop arm measures the same residency as the phone.
- Veil note (Lantern radar, [arXiv 2609.13478](https://arxiv.org/abs/2609.13478)): PLE tables are a backdoor surface. Pinning the whole-file sha256 (already in the manifest) covers it.
- Gemma 4 uses a system turn and `<|think|>` to enable thinking; BOAR must **not** send `<|think|>` (thinking cost TTFT 27 s on LFM2.5-8B-A1B, Kiln K4).

## What would make it fail

- Gemma's lower AA hallucination rate may come from **abstaining** on closed-book questions. In BOAR, with sources in the prompt, that could become "I don't know" on questions Qwen answers correctly → pass rate drops > 5 pp (criterion 2). The ESG study's lower answer relevancy (0.762 vs 0.863) points that way.
- One user report says E4B "hallucinates like mad about basic facts" ([HF discussion](https://huggingface.co/google/gemma-4-31B-it/discussions/48)); anecdotal, but it is the opposite of the AA number.
- Danger-question behaviour is a safety-tuning property, not a hallucination-rate property. Gemma may still say "rinse with fresh water". Only criterion (3) answers this.
- Prefill: Gemma's 262k vocab and PLE could make TTFT worse than Qwen3-4B on phone CPU; criterion (4).
- Desktop greedy ≠ device temp 0.7 (exp-10 UNKNOWN). A desktop pass still needs one Android device run before shipping.

UNKNOWN:
- AA's Gemma 4 E4B accuracy and hallucination rate split (only the −20 score is public on the pages fetched).
- Whether the app maintainer's F3 Gemma eval measured E4B or E2B, and its results.
- Peak RSS and Dimensity 8300 speed for this file under llama.rn rc.4.

Shelf: rows "Gemma 4 E4B-it QAT Q4_0 GGUF", "llama.cpp lazy PLE/engram reads" in `../../SHELF.md`.
