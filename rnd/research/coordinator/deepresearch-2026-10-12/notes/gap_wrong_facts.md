# gap_wrong_facts: wrong and stale parametric facts in a 2-bit 35B MoE (detection, offline verification, staleness)

State as of 2026-10-12. Gap angle opened by `_critique.md` §1 row "Wrong facts". It builds on `generation_quality.md`, which already covers decoding (DoLa/CAD/CoCoA/ID/ThinkMerge), SEP probes, CCP, LUQ, conformal factuality and TruthRL. Those are not repeated here. The angle has four parts: per-claim verification against the local kit, staleness, error-type taxonomies, and numeric errors.

Local facts checked for this note (0 Claude calls):
- **llama.rn 0.13 already has the encoder-decoder (T5) path.** `cpp/rn-completion.cpp` l.437 calls `llama_model_has_encoder`, l.636 calls `llama_encode`, and l.652 handles the decoder-start token. A MiniCheck-Flan-T5 GGUF should therefore load in the app. This closes the SHELF row 27 UNKNOWN. One caveat: QUEUE l.347 says rc.4 `n_probs` are post-sampling, so the Yes/No probability needs a non-greedy or raw-logit read.
- **The engine adds the device date only to "now" questions.** It calls `todayLine()` only when `mentionsNow()` fires (wt/cut7 `src/routing/context.ts` l.840–857). Nothing in the prompt tells the model how old its knowledge is.
- **BOAR has already measured two verifier lines on the 4B.** QUEUE l.283: the 4B self-check (P3-0) flagged 4/7 wrong sentences but also 8/20 correct ones. QUEUE l.285: the NLI passage checker (mDeBERTa) caught 0/7. Its ceiling read was that none of the 7 wrong sentences is contradicted by a prompt passage, because they are MEMORY claims written next to off-topic passages.
- **LOSSMAP numbers for the wrong bucket.** Wrong-primary is 16 items = 0.40 of loss on V-para and 17 items = 0.21 on v0.2. Comparison items are wrong on 4/7 and crypto on 3/5. LOSSMAP already ran jev over the two Opus rationales per item on seven axes (`arms/lossmap/LOSSMAP.md` l.10–16, 35).

## TL;DR
- **Neither Qwen model has an official training cutoff.** The Qwen3.6-35B-A3B card says nothing about one; the HF repo was created 2026-04-15 ([card](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)). Qwen3-4B-Instruct-2507's repo was created 2025-08-05 ([card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)). The Qwen team's only on-record comment, for Qwen2, says self-reported cutoffs are unreliable and the data reaches "as late as the end of 2023" ([issue #525](https://github.com/QwenLM/Qwen3/issues/525)). Third-party trackers give low-confidence estimates: Qwen3 2025-01, Qwen3.6-27B 2025-10 ([knowledge-cutoff.date](https://www.knowledge-cutoff.date/providers/qwen.html)). **Effective cutoffs often differ from reported ones** ([Dated Data, COLM 2024](https://arxiv.org/abs/2403.12958)). We should measure ours (EFFCUT below, 0 Claude calls).
- **The largest open lever here is a measurement, not a method.** The wrong bucket has never been split into stale, numeric, date, entity-swap and over-generalisation. Published long-form error distributions are dominated by entity errors: 42.7 % (ChatGPT), 48.6 % (Llama2-7B) and 55.7 % (Llama2-70B) of detected errors, against 2.8–4.7 % relation errors ([FAVA, COLM 2024](https://arxiv.org/html/2401.06855v4)). A jev pass over the existing LOSSMAP rationales (STALESPLIT) costs about [usage detail removed] and decides which of the levers below is worth anything.
- **Per-sentence support checkers are cheap and fit on the device. The policy is the problem.** Options:
  - MiniCheck-FT5: 770M, BAcc 74.7 vs GPT-4 75.3 ([MiniCheck](https://arxiv.org/html/2404.10774)), MIT, GGUF on SHELF, loadable in llama.rn.
  - FactCG-DeBERTa-L: 0.4B, MIT, best BAcc of any model under 1B ([repo](https://github.com/derenlei/FactCG)).
  - TinyLettuce: 17–68M, RAGTruth F1 68.5–75.0, MIT ([HF blog](https://huggingface.co/blog/adaamko/tinylettuce)).

  All of them answer "is this sentence supported by this text", and BOAR's wrong claims sit where the kit has no text. A drop-if-unsupported rule would delete the deep tier's correct memory claims, which is where its whole gain came from (LOSSMAP).
- **Against a retrieval corpus, "contradicted" is rare and "no evidence" is common.** On medical claims, Refuted is 4.6–7.1 % against Not-Enough-Evidence 8–26 %. The best verifier (GPT-5.4) reaches recall 25.6 for refuted claims, and a larger corpus did not help ([2609.30467](https://arxiv.org/html/2609.30467), 2026-09). Only a contradiction-only policy can act safely, and its reach is bounded by kit coverage (WIKISECTION 1/13 on V-para).
- **Staleness is real and large for time-sensitive facts:**
  - 24–64 % of time-sensitive items in five QA benchmarks had outdated gold by 2025-07 ([When Benchmarks Age](https://arxiv.org/html/2510.07238)).
  - 48 % of SituatedQA answers changed between 2018 and 2021 ([Zhang & Choi, EMNLP 2023](https://arxiv.org/abs/2305.14824)).
  - GPT-4 without search stays at or below 15 % on fast-changing FreshQA questions, with "flat scaling curves" ([FreshLLMs](https://arxiv.org/html/2310.03214v1)).

  The model cannot know post-cutoff values, so the only levers are fresh data (datastores' WIKIFRESH) or honest "as of" framing.
- **Stale-fact detection is feasible but coarse.**
  - Fact-duration prediction places 65 % of time-dependent facts within 3 years (baseline 11 %) and cuts QA calibration error by 50–60 % ([Zhang & Choi](https://arxiv.org/abs/2305.14824)).
  - LLMs classify how often a question's answer changes at only 24–52 % strict accuracy, 81 % within ±1 class (Qwen2.5-72B) ([RecencyQA](https://arxiv.org/html/2603.16544), MIT).
  - Date prefixes recover the newer fact in 61–81 % of conflict cases on base models ([PTC 2606.20959](https://arxiv.org/abs/2606.20959)). But a generic date injection is noise (±2–6 pp, no consistent sign) on MCQ, Qwen3-4B included ([2609.36931](https://arxiv.org/html/2609.36931v1)).
- **No published inference-time number fix works at ≤ 35B without training.**
  - Benford's Curse neuron pruning has no numbers ([2506.01734](https://arxiv.org/abs/2506.01734)).
  - FLARE-style low-probability retrieval triggers *hurt* Llama2 (HotpotQA EM 0.223 → 0.180). DRAGIN gains +0.05–0.09 EM, but only on short multi-hop QA and at 2.5–4.8 retrievals per question ([DRAGIN](https://arxiv.org/html/2403.10081v3)).
  - Entity-token probes reach AUC 0.85–0.90 on LongFact against 0.71–0.76 for entropy and perplexity, Qwen2.5-7B included. They need about 2k labelled samples, and abstaining on them costs about 50 % of correct answers ([2509.03531](https://arxiv.org/html/2509.03531v2), Apache-2.0 code).
  - The one BOAR-native numeric path is extending the FACTS Wikidata table from "answer" to "check" (NUMCHECK, VeriFin-style contradiction on (entity, property, value, date)).

## Q1. Offline claim verification against the local kit (no web)

Takeaway: the checker models exist, are small, open, and (for MiniCheck) already runnable in llama.rn. The binding constraint is evidence: BOAR's wrong claims are memory claims next to off-topic passages (P3-NLI ceiling 2/7), and the kit lacks the fact on most absent items. A per-claim retrieval step plus a **contradiction-only** policy is the only safe shape. Drop vs hedge has no long-form evidence. Short-QA user evidence says removing or vaguing doubtful content keeps perceived quality.

| item | date | URL | what it is | key numbers | licence | fit to our constraints | BOAR bucket | novelty | proposed action + 0-call gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| MiniCheck-FT5 (EMNLP 2024) | 2024-04 | https://arxiv.org/html/2404.10774 ; https://github.com/Liyan06/MiniCheck | sentence-level doc→claim support checker; one encoder pass + 1 decoder step | LLM-AggreFact BAcc 74.7 (GPT-4 75.3; RoBERTa/DeBERTa variants 72.7/72.6); 13K checks cost [usage detail removed] vs GPT-4 [usage detail removed]; decomposition "not necessary"; > 500 docs/min on an A6000 (card) | MIT (model), Apache-2.0 (repo) | GGUF 487 MB Q4_K_M on SHELF; **llama.rn 0.13 has the T5 encode path (verified locally)**; CPU latency per sentence UNKNOWN (no published CPU number) | wrong (only where the kit holds the fact) | known (SHELF row 27); the llama.rn T5 path is new | part of CONTRA (below); desktop latency probe is free (llama.cpp CLI, no calls) |
| FactCG-DeBERTa-v3-Large (NAACL 2025) | 2025-01 | https://github.com/derenlei/FactCG | 0.4B checker trained on graph-based multi-hop synthetic data | "best BAcc among < 1B" on LLM-AggreFact (README; numbers only in figures); third-party mirror lists avg 75.6 (unverified) | MIT | encoder-only, ONNX-able (≈ 0.4B ≈ 450 MB int8); needs onnxruntime-react-native or a GGUF port (DeBERTa not in llama.cpp) | wrong | new | alternative to MiniCheck if ONNX is already shipped; otherwise MiniCheck wins on runtime fit |
| LettuceDetect large / base + TinyLettuce 17/32/68M | 2025-02 / 2025-2026 | https://arxiv.org/abs/2502.17125 ; https://huggingface.co/blog/adaamko/tinylettuce | token-level unsupported-span tagger for RAG (ModernBERT / Ettin encoders, 8k ctx) | RAGTruth example-F1: large 79.22, base 76.07, Tiny-68M 74.97, 32M 72.15, 17M 68.52; 30–60 ex/s on 1 A100; no CPU ms published | MIT (repo, models) | 17–68M is phone-trivial; ONNX runtime needed; trained for answer-vs-context, i.e. it flags *ungrounded* spans, which on BOAR are mostly correct memory claims | wrong (contextual only) | known (SHELF row 29); TinyLettuce sizes new | relevance 1: same policy problem as MiniCheck; useful only as a span highlighter in the UI |
| HHEM-2.1-Open | 2024-08 | https://huggingface.co/vectara/hallucination_evaluation_model ; https://www.vectara.com/blog/hhem-2-1-a-better-hallucination-detection-model/ | 110M flan-t5-base consistency classifier | AggreFact-SOTA BAcc 76.55, RAGTruth-QA 74.28 (card mirror); < 600 MB RAM, ≈ 1.5 s per 2k-token input on CPU (card text); trained partly on RAGTruth (inflates RAGTruth) | Apache-2.0 | no GGUF (custom head); English | wrong | known (SHELF row 28) | none beyond MiniCheck |
| Bespoke-MiniCheck-7B | 2024-08 | https://huggingface.co/bespokelabs/Bespoke-MiniCheck-7B | 7B checker, LLM-AggreFact rank 1 | avg 77.4 (leaderboard mirror 2026-05) | no licence field | 15.5 GB; judge-side only | — | known (SHELF row 30) | none |
| Paladin-mini | 2025-06 | https://arxiv.org/html/2506.20384v1 | 3.8B grounding model | avg BAcc 79.31 at 70 ms (own benchmark + AggreFact mix; not leaderboard-comparable) | not checked | second 3.8B model in RAM next to the 35B: no | wrong | new | relevance 0 |
| VeriScore (EMNLP Findings 2024) | 2024-06 | https://arxiv.org/abs/2406.19276 ; https://github.com/Yixiao-Song/VeriScore | extract only *verifiable* claims → search per claim → supported / contradicted / inconclusive | (pipeline paper; Google-Search evidence; own analysis: retrieval of evidence for complex claims fails) | Apache-2.0 | evidence step is web; the extraction prompt is reusable offline with a local retriever | wrong (eval-side) | known as an eval metric (eval-methodology 10-06); as an *offline on-device* pipeline new | use its "verifiable-claim" extraction idea inside CONTRA (claims about prices/opinions are skipped) |
| VeriFastScore (EMNLP Findings 2025) | 2025-05 | https://arxiv.org/html/2505.16973v3 ; https://github.com/RishanthRajendhran/VeriFastScore | one fine-tuned Llama-3.1-8B does extraction + verification in one pass over ≈ 4k tokens of evidence | r = 0.80 example-level / 0.94 system-level vs VeriScore; 6.6× faster (9.9× excluding retrieval) | repo: no licence | 8B second model on device: no; desktop eval tool: yes | — | new | relevance 1 (eval-side, licence missing) |
| OpenFActScore | 2025-07 | https://arxiv.org/html/2507.05965v1 ; https://github.com/lflage/OpenFActScore | FActScore with any HF model; GTR retriever, topic + fact query, top-5 Wikipedia passages, "True or False?" | cumulative FActScore error vs human: Gemma 12.2, Llama-3.1 13.4, **Qwen 27.8**, OLMo 55.6; Pearson > 0.99 with original FActScore | MIT | the closest published offline-Wikipedia claim-verifier recipe; Qwen is the worst open verifier tested | wrong (eval / gate) | new | relevance 1: a 0-Claude-call desktop gate tool (Gemma verifier) for CONTRA's hit/false-flag counts |
| HalluLens LongWiki (ACL 2025) | 2025-04 | https://arxiv.org/html/2504.17550v1 ; https://github.com/facebookresearch/HalluLens | long-form factuality vs Wikipedia page retrieval (title match, 256-token passages, top 5), Llama-405B verifier | precision of supported claims: Qwen2.5-7B 44.53, Qwen2.5-14B 52.84, Llama-3.1-8B 45.36, 70B 53.74; recall@32 70.9 / 74.1 / 64.0 / 66.3; false refusal Qwen 0.53 % (LongWiki) | code NOASSERTION | context only | wrong | new | relevance 1: Qwen-family open models produce ≈ 45–53 % Wikipedia-supported claims even on Wikipedia topics, so "unsupported" ≠ "wrong" at scale |
| FAVA (COLM 2024) | 2024-01 | https://arxiv.org/html/2401.06855v4 | 6-type hallucination taxonomy + 7B retrieval-augmented detector/editor | Llama2-Chat-7B gens: FAVA binary F1 79.9 vs Rt+ChatGPT 70.4, GPT-4 72.1; fine-grained F1 39.6 (see Q3 for the distribution) | repo: no licence | 7B editor: no | wrong | new | relevance 1 (taxonomy reused in STALESPLIT) |
| Medical retrieval-verifier failure taxonomy | 2026-09 | https://arxiv.org/html/2609.30467 | retrieval-stage (entity/scope/polarity/chunking) and verifier-stage failure codes | claim labels per retriever: Supported 65.0–78.3 %, **Refuted 4.6–7.1 %**, NE 8.0–26.0 %; high-quality passages only 2–14.5 %; verifier recall 25.6 (GPT-5.4) vs 8.1 (Gemma 3 27B); larger corpus (Google) did not raise recall | arXiv | warns that small verifiers (Gemma 3 27B) miss most refutations | wrong | new | supports contradiction-only policy and low expectations |
| BOAR P3-0 / P3-NLI (internal) | 2026-10-02 | QUEUE.md l.283–285 | 4B self-check; mDeBERTa NLI passage checker | 4B: 4/7 hits, **8/20 false flags**; NLI: 0/7, 0/20; ceiling 2/7 for any passage checker | — | — | wrong | known | the reason CONTRA must retrieve per claim and act only on contradictions |
| Hide or Highlight (AIES 2025) | 2025-08 | https://arxiv.org/abs/2508.07095 | user study, N = 148, QA: highlight doubtful / highlight factual / remove doubtful / make doubtful vague | "opaque" (remove) and "ambiguity" (vague) gave the highest trust **and kept perceived answer quality** (abstract; effect sizes not on the page) | arXiv | evidence about humans, not about an Opus judge | wrong → drop/vague | new | relevance 1: if CONTRA fires, prefer drop or "vague the number" over a visible flag |
| Conformal factuality / specificity back-off | 2024-02 / 2025-02 | https://arxiv.org/abs/2402.10978 ; https://arxiv.org/abs/2502.19110 | drop or de-specify least-certain claims until a calibrated threshold | see generation_quality Q3 | — | — | wrong | known (generation_quality) | none |

## Q2. Temporal staleness: cutoffs, measurements, detection

Takeaway: there is no official cutoff for Qwen3.6-35B-A3B or Qwen3-4B-2507. The literature agrees that 25–65 % of time-sensitive facts drift within a few years, and that scale does not fix fast-changing knowledge. Detecting likely-stale *questions* is coarse but cheap (fact duration, recency class). Detecting stale *claims* inside an answer has no off-the-shelf tool. For BOAR the staleness question is first a measurement: how much of the 0.40 V-para wrong loss is stale (STALESPLIT), and how old the deep model's knowledge effectively is (EFFCUT).

| item | date | URL | what it is | key numbers | licence | fit | bucket | novelty | proposed action + 0-call gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3.6-35B-A3B model card | 2026-04-15 (repo created; modified 04-24) | https://huggingface.co/Qwen/Qwen3.6-35B-A3B | official card | **no cutoff statement** (README grepped for cutoff/knowledge/date: none) | Apache-2.0 | — | stale | new (no BOAR doc states a cutoff; models_moe UNKNOWN row) | treat the cutoff as unknown; measure with EFFCUT |
| Qwen3-4B-Instruct-2507 card | 2025-08-05 (repo created) | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 | official card | no cutoff; "substantial gains in long-tail knowledge coverage" | Apache-2.0 | — | stale | new | as above |
| Qwen team statement (Qwen2 era) | 2024-06-11 | https://github.com/QwenLM/Qwen3/issues/525 | maintainer comment | self-reported cutoffs unreliable ("date is injected in post-training"); data "as late as the end of 2023" (Qwen2) | — | — | stale | new | do not ask the model its cutoff |
| Third-party cutoff trackers | 2026 | https://www.knowledge-cutoff.date/providers/qwen.html | community estimates | Qwen3-235B: 2025-01 (low confidence); Qwen3.6-27B: 2025-10 (low) | — | weak evidence | stale | new | context only |
| Dated Data (COLM 2024) | 2024-03 | https://arxiv.org/abs/2403.12958 ; https://github.com/nexync/dated_data | effective per-resource cutoff via perplexity over dated versions of the same document | effective cutoffs "often drastically differ" from reported ones, because CommonCrawl dumps carry old text and deduplication fails (abstract) | repo: no licence | method needs only log-likelihoods: runs on llama.cpp `llama-perplexity` | stale | new | **EFFCUT** (below) |
| FreshQA / FreshLLMs | 2023-10; repo updated 2026-05 | https://arxiv.org/html/2310.03214v1 ; https://github.com/freshllms/freshqa | 600 Qs: never / slow / fast-changing / false-premise | no-search GPT-4 28.6 strict / 46.4 relaxed overall; **≤ 15 % on fast-changing**; flat scaling on fast-changing | Apache-2.0 | offline: fast-changing part is unanswerable by design | stale | known (eval_judge 10-12 row) | none; cite as the ceiling for parametric fast-changing facts |
| When Benchmarks Age | 2025-10 (v2 2026-01) | https://arxiv.org/html/2510.07238 | re-checks gold of time-sensitive items against 2025-07 web | drift of time-sensitive items: TriviaQA 37.05 %, BoolQ 63.78 %, NQ 24.19 %, TruthfulQA 36.88 %, SelfAware 28.26 %; Qwen2.5-14B matches *current* facts more than stale gold (NQ 24.19 vs 17.92) | arXiv | — | stale | new | context: the reference (frontier + web, 2026-10) will disagree with a 2025-cutoff model on roughly a quarter to two-thirds of time-sensitive facts |
| Fact duration prediction (Zhang & Choi, EMNLP 2023) | 2023-05 | https://arxiv.org/abs/2305.14824 ; https://github.com/mikejqzhang/mitigating_misalignment | classifier predicts how long a fact stays true; discard volatile answers | 65 % of time-dependent NQ facts predicted within 3 years (baseline 11 %); ECE −50–60 % on two QA systems; SituatedQA: 48 % of answers changed 2018 → 2021 (verified PDF) | repo: no licence | BERT/T5-sized classifier, phone-trivial; or a jev rubric on desktop | stale | new | relevance 1–2: only useful after STALESPLIT shows stale is large; then a question-side "volatile" tag can route to "as of" framing |
| RecencyQA | 2026-03 | https://arxiv.org/html/2603.16544 ; https://github.com/DataScienceUIBK/RecencyQA | 4,031 Qs labelled with 12 recency classes (hour … never) + stationarity | LLM recency-class accuracy strict 24–52 % (best Gemma 3 27B few-shot 52.05), ±1 class best 81.05 % (Qwen2.5-72B CoT); models evaluated incl. Qwen2.5-7B | MIT (repo) | training data for a small volatility classifier | stale | new | data source if a volatility tag is ever built |
| Parametric Temporal Conflict (PTC) | 2026-06 (v3 08-05) | https://arxiv.org/abs/2606.20959 | 8,746 Wikidata position-holder transitions; models hold the new fact but answer the old | date prefix recovers the newer fact in **61–81 %** of PTC cases; patching flips 72–85 %; automatic detection "remains unreliable"; base (non-instruct) models only | arXiv | recipe (Wikidata SPARQL transitions) is reusable for EFFCUT; the deep tier is an instruct model, so transfer is untested | stale | new | use the transition set idea in EFFCUT; also test "date always on" only on transition-type questions |
| Hidden dates in system prompts | 2026-09-29 | https://arxiv.org/html/2609.36931v1 | 9 open models incl. Qwen3-4B and Qwen3-Next-80B; vary the injected date | MMLU avg swing 2.30 pp (max 3.51), GPQA 3.80 (max 6.06), ARC 1.46; **no consistent direction**; recommends removing or fixing the date | arXiv | — | stale | new | relevance 0 as a lever: a generic always-on date line is noise; keep BOAR's `mentionsNow` gating |
| BOAR engine date line (internal) | 2026-10 | wt/cut7 `src/routing/context.ts` l.840–857 | date injected only when the question says "today/now/latest…" | — | — | — | stale | known (engine) | none |
| a competitor team fresh-Wikipedia snapshot | 2026-09 | [competitor link removed] | competitor's 2023 → 2026-09 Wikipedia refresh | 0.464 → 0.508 judged, inside own ±0.05 noise | — | — | stale (corpus side) | known (datastores, critique §2) | none here; corpus freshness belongs to WIKIFRESH |

## Q3. Wrong-claim taxonomies and splitting *wrong* into stale vs false at 0 Claude calls

Takeaway: published long-form distributions put **entity errors first (43–56 % of errors)**. After that come whole-sentence contradictions (16–20 %) and invented entities (9.5–17 %). Relation errors are rare (3–5 %). None of the published taxonomies separates "stale" from "false", and none is for 2025–26 Qwen models. BOAR already has the input for its own split: two Opus rationales per item, jev-classified on seven axes in LOSSMAP. Adding axes is a 0-Claude-call, [usage detail removed] job.

| item | date | URL | what it is | key numbers | licence | fit | bucket | novelty | proposed action + 0-call gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| FAVA error distribution | 2024-01 | https://arxiv.org/html/2401.06855v4 | human-annotated types in info-seeking long-form answers | ChatGPT / Llama2-7B / Llama2-70B: entity 42.7 / 48.6 / 55.7 %; relation 4.7 / 3.4 / 2.8; sentence 18.9 / 15.7 / 19.9; invented 14.2 / 17.4 / 9.5; subjective 9.9 / 8.6 / 5.8; unverifiable 9.6 / 6.3 / 6.3; responses with ≥ 1 hallucination 59.8 / 70.2 / 64.9 % | no repo licence | prior for STALESPLIT | wrong | new | use as the prior distribution (entity-heavy) |
| Hallucinated-entity probes | 2025-08 (v2 2026-02) | https://arxiv.org/html/2509.03531v2 ; https://github.com/obalcells/hallucination_probes | linear / LoRA probe at layer ⌊0.95·L⌋ tags fabricated entity tokens (names, dates, numbers) while streaming | LongFact AUC: Llama-3.1-8B linear 0.854 / LoRA 0.894 vs perplexity 0.760, entropy 0.742, semantic entropy 0.719; Llama-3.3-70B LoRA 0.905; Qwen2.5-7B / Gemma-2-9B / Mistral-24B LoRA 0.87–0.90 with 2k samples; selective answering: cutting hallucinations costs ≈ 50 % of correct answers (SimpleQA, 70B) | Apache-2.0 (repo) | needs residual-stream read in llama.cpp (eval callback; not in llama.rn/bmoe JS) + ≈ 2k web-labelled training samples for Qwen3.6 (a Claude/web labelling job) | wrong (entity/number/date) | new (generation_quality has SEP, not entity probes) | relevance 2: the strongest *detector* found, but the action after detection (drop/abstain) is unproven on judged quality; park unless STALESPLIT shows entity/number errors ≥ 50 % of wrong loss |
| Medical verifier taxonomy | 2026-09 | https://arxiv.org/html/2609.30467 | see Q1 | — | — | — | — | new | taxonomy headers reusable for the rationale axes (entity mismatch, scope over-generalisation) |
| ErrorAtlas | 2026-01 | https://arxiv.org/html/2601.15812v1 | induced failure taxonomy over 83 models / 35 datasets | "incorrect identification" is a top category (abstract level) | arXiv | — | — | new | relevance 0 |
| LOSSMAP jev axes (internal) | 2026-10-12 | arms/lossmap/LOSSMAP.md | jev over 2 Opus rationales + answer + kept titles, 7 boolean axes at p ≥ 0.6 | wrong-primary V-para 16 items = 0.40 of loss; v0.2 17 = 0.21; comparison 4/7 wrong, crypto 3/5 wrong | — | input exists; coordinator-side read (researchers never see item text) | wrong | known | **STALESPLIT** (below) |

## Q4. Reducing wrong numeric/date claims at inference without prompts (≤ 35B)

Takeaway: nothing in the literature reaches long-form judged quality at ≤ 35B with a no-training, no-prompt numeric fix:
- Digit-bias pruning has no numbers.
- Token-probability triggers either hurt (FLARE) or help only short multi-hop QA at several extra retrievals (DRAGIN).
- Probability-based abstention on numerals is weak at this scale (generation_quality: CCP AUROC ≈ 0.65; sub-3B entropy ≈ 0).
- Probes work, but they need training labels and a hidden-state hook.

BOAR's own FACTS tier (Wikidata table, CC0, precision 90–97 %) is already a working "retrieve-then-copy for numbers" on the question side. The untried mechanism is running it on the **answer** side as a contradiction check.

| item | date | URL | what it is | key numbers | licence | fit | bucket | novelty | proposed action + 0-call gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| FLARE vs DRAGIN (ACL 2024) | 2023-05 / 2024-03 | https://arxiv.org/abs/2305.06983 ; https://arxiv.org/html/2403.10081v3 ; https://github.com/oneal2000/DRAGIN | retrieve mid-generation when token confidence drops (FLARE) or by entropy × attention × semantics (DRAGIN) | Llama2-13B HotpotQA EM: no-RAG 0.223, single RAG 0.263, **FLARE 0.180**, DRAGIN 0.314; Vicuna-13B HotpotQA FLARE 0.092 vs no-RAG 0.228; DRAGIN 2.5–4.8 retrievals/question; no wall-clock | DRAGIN Apache-2.0 | multi-pass retrieval during decoding; ×2–5 prefill on a 35B at 32 tok/s prefill on phone | wrong + absent | closed_family_new_mechanism (DEEPITER closed planner-driven second retrieval; confidence-triggered mid-sentence retrieval was never tested) | relevance 1: bounded by kit coverage (WIKISECTION 1/13) and by DEEPITER's −0.019; do not test unless the WIKIFRESH anywhere-gate shows the facts are in a pack |
| Benford's Curse (NeurIPS 2025) | 2025-06 | https://arxiv.org/abs/2506.01734 | digit-selective FFN neurons in deep layers cause a skewed digit distribution; pruning them | qualitative only ("partially corrects") | arXiv | needs per-neuron surgery on a 2-bit MoE | wrong (numeric) | new | relevance 0 |
| VeriFin (neurosymbolic numeric verification) | 2026-08 | https://arxiv.org/pdf/2608.10213 | ground each LLM figure in structured facts (XBRL), check with Z3, repair from the unsat core | finance only (numbers not read) | arXiv | the *pattern* maps onto FACTS: (entity, property, value, unit, date qualifier) | wrong (numeric/date) | new | idea source for NUMCHECK |
| CheckThat! 2025 numerical claims | 2025-09 | https://arxiv.org/pdf/2509.11492 | prompted vs fine-tuned verification of numeric claims | topic match ≠ quantity/date/scope match (main failure) | arXiv | — | wrong | new | relevance 0–1: argues NUMCHECK must match the date qualifier, not just the entity |
| Quantization and factual recall | 2025-05 / 2026-04 | https://arxiv.org/abs/2505.13963 ; https://www.alphaxiv.org/abs/2604.19884 | 4/8-bit effect on factual knowledge recall; 2-bit "performance cliff" on precise facts (GPTQ) | 4/8-bit: lower bits not always worse; 2-bit numbers not read | arXiv | BOAR's QUANTCEIL measured 2 → 3-bit +0.004 (not detected) | wrong | closed_family_same_mechanism (QUANTCEIL) | do not re-test |
| ClaimCheck | 2025-09 | https://arxiv.org/abs/2510.01226 | Qwen3-4B fact-checking pipeline with live web | AVeriTeC 76.4 % (vs Llama-3.1-70B, GPT-4o pipelines) | no code licence | web-only | — | new | relevance 0 (shows a 4B can verify with good evidence; evidence is BOAR's gap) |
| FACTS tier (internal) | 2026-10-07 | QUEUE l.718–735; CLAIM build cut 7 | Wikidata fact table (1,052 entities, 263 KB, CC0) that answers numeric questions | precision 90–97 %, FP 0/100 blind, recall 60–70 %; 3 of 10 misses are stale populations (India 2020, Nigeria 2021) | CC0 | already on device | wrong (numeric) | known | base of NUMCHECK |

## Proposed actions (ordered, each with a 0-Claude-call gate)

1. **STALESPLIT (measurement, about [usage detail removed] of jev, coordinator-only read).**
   - **Input.** LOSSMAP's existing per-item rationales on H (dt512), V-para 51 and v0.2 110.
   - **Axes.** Add jev boolean axes over the two Opus rationales plus the answer. Each axis needs p ≥ 0.6. The axes are:
     - `stale`: the rationale says the claim was true earlier, or names a newer value, version, rule, price or office-holder.
     - `numeric_wrong`: a number differs.
     - `date_wrong`
     - `entity_swap`
     - `overgeneralised`: true in part, scoped wrongly.
     - `fabricated`
   - **Labels.** Report counts on wrong-primary items, weighted by loss share.
   - **Decision.**
     - stale ≥ 40 % of the wrong loss: the lever is freshness. That means WIKIFRESH or fresh packs plus "as of" framing, not a verifier.
     - numeric + date ≥ 40 %: run NUMCHECK.
     - entity_swap + fabricated ≥ 50 %: the entity-probe line is the only detector with evidence, and it is training-gated.
   - **Caveats.** The judge rationale may not name the correct value. Report the share of wrong items where the rationale gives any correction (`rationale_names_correction`), and treat stale as a lower bound.
   - **Cost.** About 1 h coordinator time.

2. **EFFCUT (0 Claude calls, desktop llama.cpp, about 1–2 h).** Estimate the effective knowledge cutoff of Qwen3.6-35B-A3B UD-Q2_K_XL and Qwen3-4B-2507.
   - **Probe set.** Build it from Wikidata SPARQL position-holder transitions dated 2024-01 … 2026-06, as in the PTC recipe ([2606.20959](https://arxiv.org/abs/2606.20959)). Use about 30 transitions per quarter and closed-book prompts. A string match against the new holder needs no judge.
   - **Optional second signal.** Run Dated-Data perplexity over monthly revisions of a few fast-changing Wikipedia pages.
   - **Output.** The quarter where the new-holder rate falls to chance. Compare it with the pack snapshot (FineWiki Aug-2025) and the reference date (2026-10).
   - **Decision.** If the effective cutoff is earlier than the Aug-2025 pack, the packs are fresher than the model. Wrong claims on items with a kept on-topic source are then a reading problem, not staleness.
   - **Cost.** One SPARQL query, about 500 local generations, 0 Claude.

3. **NUMCHECK (only if STALESPLIT gives numeric + date ≥ 40 %).** Run the FACTS table on the answer side.
   - **Extraction.** Regex/NER pulls (entity, number, unit, year) spans from the generated answer.
   - **Lookup.** Exact-alias entities go into the existing FACTS lookup, with the same risk-list rules as `src/rag/facts.ts`.
   - **Action.** A mismatch beyond tolerance, with a compatible date qualifier, replaces the number with the table value plus "(Wikidata, as of …)". Otherwise leave the answer untouched.
   - **Gate (0 Claude calls).** On H's existing answers, count wrong-primary items whose wrong span is a FACTS-covered (entity, property). Pass ≥ 4/16 V-para wrong items, and 0 rewrites on the 20 random-slice correct answers.
   - **Prior.** Low. FACTS covers 1,052 entities, and FACTS fires 0/58 on V-para (CLAUDE.md state).

4. **CONTRA (only if NUMCHECK fails and STALESPLIT shows contradicted-by-kit errors).** Per sentence of the deep answer:
   - **Verifiable-claim filter.** Apply a VeriScore-style filter: skip opinions, advice and hedges.
   - **Claim-level retrieval.** Run BM25 over all packs, the full enwiki shards included. Keep evidence only if its title matches an entity named in the sentence.
   - **Check.** MiniCheck-FT5 GGUF in llama.rn.
   - **Action.** Only if the checker says unsupported **and** the evidence contains a conflicting number, date or entity for the same slot, drop or vague the sentence. Use Hide-or-Highlight's "opaque/ambiguity" variants and never show a visible flag.
   - **Gate (0 Claude calls).** Reuse P3-0's frozen 7 + 20 shape on H's traces: ≥ 4/16 wrong items hit, ≤ 2/20 false flags, OpenFActScore-Gemma as the offline adjudicator.
   - **Prior.** Low. P3-NLI's ceiling is 2/7, WIKISECTION found 1/13, and Refuted is 5–7 % even with a good retriever ([2609.30467](https://arxiv.org/html/2609.30467)).
   - **Cost if it passes.** About 1 day of engine work plus desktop latency, with about 5–8 sentences per answer × (BM25 + 1 T5 pass).

5. **Do not do:**
   - Generic always-on date injection (noise, [2609.36931](https://arxiv.org/html/2609.36931v1)).
   - Drop-if-unsupported with any checker (it deletes correct memory claims; HalluLens shows only 45–53 % of Qwen claims are Wikipedia-supported even on Wikipedia topics).
   - FLARE-style probability triggers (they hurt at 7–13B).
   - Digit-neuron pruning.
   - Re-testing 3-bit (QUANTCEIL).

## Searched, found nothing
- An official training-data cutoff for Qwen3.6-35B-A3B, Qwen3.5 or Qwen3-4B-2507: not in the HF cards (grepped), the Qwen3 technical report (2505.09388, pdftotext grep: no "cutoff"), or the qwen.ai blog (JS page, empty on fetch).
- FreshQA, or any freshness benchmark, run on Qwen3 / 3.5 / 3.6 instruct models. Only Qwen2.5 appears (When Benchmarks Age) and Qwen3-4B on MCQ date-injection.
- A published per-type distribution of long-form errors (numeric / date / entity / stale) for any 2025–26 open model; only FAVA (2024, ChatGPT/Llama2) has numbers.
- A taxonomy that separates "stale" from "false" in judged long-form answers.
- A measured CPU latency per sentence for MiniCheck-FT5, HHEM-2.1 (only the vendor's "≈ 1.5 s / 2k tokens" text) or TinyLettuce (only "real-time on CPU").
- A head-to-head of drop vs hedge vs rewrite for flagged sentences, evaluated by an LLM judge on long-form answers. The only evidence is the short-QA user study (Hide or Highlight) and the conformal back-off papers (automatic metrics).
- Number-aware decoding or "copy numbers from retrieved context" constrained decoding with a long-form factuality result at ≤ 35B.
- Token-probability abstention on numerals specifically, evaluated on long-form factuality.
- An on-device (Android / llama.cpp) implementation of any claim-verification pipeline.

## UNKNOWN
- How judge.v1 scores a stale-but-labelled answer ("as of 2025, X") against a stale bare claim against a decline. This decides whether "as of" framing can move the number at all; generation_quality has the same UNKNOWN for declines.
- Whether the Opus rationales name the correct value often enough for STALESPLIT to tell stale from false (`rationale_names_correction` rate).
- MiniCheck-FT5 GGUF numerical parity with the PyTorch model under llama.cpp's T5 path. The Yes/No probability read in llama.rn may need raw logits, because `n_probs` is post-sampling (QUEUE l.347).
- Whether the hallucinated-entity probe transfers to a 2-bit MoE, and whether bmoe exposes the layer-0.95 residual.
- The effective cutoff of the deep model, and so whether its stale claims predate or postdate the Aug-2025 pack snapshot (EFFCUT).
