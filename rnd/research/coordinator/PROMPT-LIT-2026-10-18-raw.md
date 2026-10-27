# Prompting small instruct models: fabrication vs over-refusal (raw collection, 2026-10-18)

Scope: literature and vendor docs on prompt wording for 1–8B instruct models. Collection only, no conclusions.
Status key: **[F]** = fetched and checked on the page; **[S]** = seen in search snippet only (not opened); **unverified** = could not confirm the claim or the model sizes.
Relevance = to BOAR (Qwen3-4B-Instruct-2507 Q4_K_M + 1.7B lite, retrieval over local chunks, offline).

---

## Angle 1: Abstention / "say I don't know" prompting

| Source | What was measured | Model sizes | Finding (one line) | Relevance |
|---|---|---|---|---|
| R-Tuning, Zhang, Diao et al., NAACL 2024, https://arxiv.org/abs/2311.09677 (code: https://github.com/shizhediao/R-Tuning) [S] | Fine-tuning with refusal-aware data built by probing which questions are beyond parametric knowledge | unverified (LLaMA-family; sizes not checked) | Trains abstention; claims better calibration than uncertainty-based testing. Training, not prompting. | med |
| Rewarding Intellectual Humility, arXiv 2601.20126 (27 Jan 2026) https://arxiv.org/abs/2601.20126 [S] | RLVR with ternary reward (correct +1, wrong −1, abstain r_abs); MedMCQA and MATH | Granite-3.3-2B-Instruct, Qwen3-4B-Instruct | Moderate abstention reward cuts wrong answers without severe accuracy loss on MCQ; open-ended exploration still weak. Closest small-model evidence, but training-time. | high (same size class) |
| AbstentionBench, arXiv 2506.09038 (2025) https://arxiv.org/pdf/2506.09038 [S] | Abstention benchmark across LLMs; reasoning models fail to abstain on unanswerable questions | unverified | Abstention is under-measured; reasoning models abstain poorly. | med |
| Temporal QA abstention, ICLR 2026, arXiv 2602.04755 https://arxiv.org/pdf/2602.04755v2 [S] | Accuracy vs abstention trade-off when training for abstention | unverified | Reports a trade-off between accuracy and abstention; reward/data ratio hard to tune. | med |
| Conformal abstention, arXiv 2405.01563 (2024) https://arxiv.org/abs/2405.01563 [S] | Sample-and-agree check with conformal threshold for abstention | general LLMs, sizes unverified | Gives a hallucination-rate guarantee via abstention threshold; not a prompt wording. | low |
| Anthropic "Reduce hallucinations" docs https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations [F] | Vendor guidance, no measurement reported | Claude (sizes n/a) | "Explicitly give Claude permission to admit uncertainty. This simple technique can drastically reduce false information." Says techniques "don't eliminate them entirely." | high (wording), low (evidence) |
| Penn State ICDS review on abstention, https://www.icds.psu.edu/?p=44935 [S] | Narrative review | n/a | Forcing abstention can cause over-refusal of valid questions; models lack epistemic awareness. Opinion-level. | low |

Count: 7 sources (2 with small-model sizes).

---

## Angle 2: Over-refusal / capability refusals from system prompts

| Source | What was measured | Model sizes | Finding (one line) | Relevance |
|---|---|---|---|---|
| SkillShield, arXiv 2608.25817 https://arxiv.org/pdf/2608.25817 [S] | False refusals on 731 benign software-engineering tasks under different safety-rule bundles | includes Qwen3 (size unverified) | Most configs under ~0.7 % false refusal; a reactive, failure-derived rule set reached 16.3 % on one Qwen3 bundle vs 0.27 % for proactive rules. Benign code tasks share surface signals with harmful ones. | high (direct match: code refusal from safety rules) |
| MS-XSB, "Beyond Over-Refusal", arXiv 2510.08158 https://arxiv.org/pdf/2510.08158 [S] | Multi-turn exaggerated refusals in context-rich dialogue; up to 4 prior responses fed back | Llama family (sizes unverified) | Over-refusals persist across recent LLMs and worsen in multi-turn. Post-hoc mitigation is model-agnostic. | high (multi-turn) |
| XSTest-based studies, e.g. arXiv 2607.24392 "When LLM Defenses Backfire" https://arxiv.org/pdf/2607.24392 [S] | Over-refusal on XSTest vs OpenAssistant under defense prompts/methods | unverified | Over-refusal consistently worse on XSTest; some conservative defenses raise refusal on safe prompts. | med |
| arXiv 2606.09697 PsychoSafe https://arxiv.org/pdf/2606.09697 [S] | Safety-tuned system prompt vs base on XSTest-style benign prompts | one model, size unverified | Reported over-refusal on benign prompts 3.6 % with the safety prompt vs 13.2 % base (single study; direction is opposite to the usual claim). | med (contradicts the simple story) |
| XSCode / CyberSecEval false-refusal sets, PurpCode arXiv 2507.19060 https://arxiv.org/pdf/2507.19060 [S] | Benchmark construction: 589 benign code prompts (XSCode), 750 false-refusal prompts | n/a | Ready-made test sets for coding refusals. | high (as test set) |
| FalseReject (Amazon), summarised secondhand | 16,000 benign-but-sensitive prompts, 29 LLMs | 29 models, sizes unverified | Reported that every model over-refuses; not verified at source. | low |
| Latitude blog, https://latitude.so/blog/how-to-detect-when-your-ai-agent-refuses-or-over-refuses [S] | Practitioner opinion | n/a | Over-refusal "tends to spike" when a system prompt is tightened. No measurement. | low |

Gap: no controlled study found that varies honesty/system-prompt wording and reports refusal rate per wording on 1–8B models. Would need our own XSTest-style run.

Count: 6 sources (2 with direct code/multi-turn relevance).

---

## Angle 3: RAG grounding instructions ("answer only from context" vs "context first")

| Source | What was measured | Model sizes | Finding (one line) | Relevance |
|---|---|---|---|---|
| FaithEval, ICLR 2025, arXiv 2410.03727 https://arxiv.org/abs/2410.03727 [S] | 4.9K problems: unanswerable, inconsistent, counterfactual contexts | 18 proprietary + open models (small-model numbers not checked) | Even SOTA models often fail to stay faithful to context; larger does not reliably mean more faithful. Check tables for <8B rows. | high (unanswerable = our "not in context" failure mode) |
| FaithfulRAG, ACL 2025 (long), arXiv 2506.08938 https://arxiv.org/abs/2506.08938 [S] | Fact-level conflict modelling; critiques strict-adherence prompts | unverified | Argues strict "stick to context" prompts suppress parametric knowledge and can distort reading. Counter-evidence to "answer only from context". | high (direct trade-off) |
| RAGTruth, ACL 2024 https://aclanthology.org/2024.acl-long.585 [S] | ~18k RAG responses annotated for word-level hallucination; detector + fine-tune | several models; small fine-tuned detector | Shows a small fine-tuned detector competitive with GPT-4 prompting; does **not** test grounding-instruction wording. | low (for prompts) |
| Anthropic docs, "Direct quotes" and "External knowledge restriction" https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations [F] | Vendor guidance, no measurement | Claude (sizes n/a) | Extract word-for-word quotes first (recommended for >20k-token docs); "Only base your analysis on the extracted quotes"; say "No relevant quotes found." when none. | high (wording), low (evidence) |
| ALCE / citation-prompting, Gao et al. 2023, arXiv 2305.14627 https://arxiv.org/pdf/2305.14627 [S] | Prompted citation generation, automatic citation recall/precision | several incl. smaller open models (sizes unverified) | Prompting-only citation quality substantial room to improve. | med |
| Huang et al., ACL 2024, arXiv 2402.04315 https://arxiv.org/pdf/2402.04315 [S] | Prompting alone vs fine-grained reward training for citations | LLaMA-2-7B and others | Prompting gave unsatisfactory citation quality, especially for smaller models; trained version beat GPT-3.5-turbo on LLaMA-2-7B. | high (negative evidence for prompt-only at 7B) |

Count: 6 sources. No source found that directly compares "answer only from context" vs "context first, then general knowledge" wording on 1–4B models.

---

## Angle 4: Length / style control and factuality

| Source | What was measured | Model sizes | Finding (one line) | Relevance |
|---|---|---|---|---|
| FActScore, EMNLP 2023, arXiv 2305.14251 https://arxiv.org/abs/2305.14251 [S] | Atomic-fact precision for long-form bios | ChatGPT, GPT-4, Vicuna, Alpaca and others | ChatGPT ~58 % on bios in original human eval; metric is per atomic fact. Base for length studies. | high (metric) |
| Zhao et al., ACL 2025 Findings, "How Does Response Length Affect Long-Form Factuality" (URL not confirmed; found via themoonlight.io review https://www.themoonlight.io/review/how-does-response-length-affect-long-form-factuality) | Factual precision vs response length | unverified | Longer responses show lower factual precision (length bias), attributed to "facts exhaustion" (reliable facts run out first). | high (mechanism matches "Detailed" style) |
| BAFE follow-up (cited in same review) | Length bias with broader coverage than single-Wikipedia FActScore | unverified | FActScore's single-Wikipedia reference gives false negatives; length comparisons can be confounded by coverage. | med (measurement caution) |
| Multilingual hallucination study, arXiv 2502.12769 https://arxiv.org/pdf/2502.12769 [S] | Hallucination across 30 languages | includes smaller models | Overall length-hallucination correlation not uniform; smaller models suffer more when generating long answers across languages. | med |
| Giskard/Phare brevity benchmark (vendor report; reported via the-decoder / Yahoo coverage) [S] | Accuracy when user asks for brevity | GPT-4o mini, Qwen 2.5 Max, Gemma 3 27B | Asking for concise answers can reduce accuracy; vendor-run, not peer-reviewed. | med (cuts both ways: brevity pressure can hurt) |
| "Illusion of Progress" arXiv 2508.08285 https://arxiv.org/pdf/2508.08285 [S] | Hallucination detection re-evaluation | unverified | Hallucinated responses tend to be longer with more length variance; correlation only. | low |

Count: 6 sources. Direct measurement of "Detailed (3–5 paragraphs)" vs short style on 4B models: none found.

---

## Angle 5: Vendor guidance (Qwen3 2507, llama.cpp / chat template)

| Source | What was measured / stated | Model sizes | Finding (one line) | Relevance |
|---|---|---|---|---|
| Qwen3-4B-Instruct-2507 model card https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 [F] | Recommended sampling; output length; mode | 4B | "We suggest using Temperature=0.7, TopP=0.8, TopK=20, and MinP=0." "We recommend using an output length of 16,384 tokens for most queries." "This model supports only non-thinking mode and does not generate `<think></think>` blocks." Says nothing on system prompts or hallucination. | high |
| Qwen official hallucination / system-prompt guidance | Searched; nothing found | n/a | No Qwen-published hallucination prompting guidance located. | — (gap) |
| llama.cpp / chat-template notes | Not searched in depth | n/a | unverified; check llama.cpp server docs for the Qwen3 template handling of system role | — (gap) |
| Anthropic "Reduce hallucinations" (cross-listed from Angle 1) [F] | see above | Claude | see above | high (only vendor doc with explicit wording found) |

Count: 2 usable vendor sources (Qwen card, Anthropic docs) plus 2 gaps.

---

## Angle 6: Practical prompt patterns (self-verification, uncertainty sections, confidence, citations, few-shot)

| Source | What was measured | Model sizes | Finding (one line) | Relevance |
|---|---|---|---|---|
| Chain-of-Verification, arXiv 2309.11495 https://arxiv.org/pdf/2309.11495 [S] | Draft → plan verification questions → answer them independently → revise | Llama 65B (reported) | Large gains on list and long-form factual accuracy; factored (non-attending) variant reduces copied hallucinations. No small-model numbers. | med (method, not size-matched) |
| Multi-stage self-verification, arXiv 2509.05741 https://arxiv.org/pdf/2509.05741 [S] | Self-verification for factual accuracy and citations | unverified | Reports gains; sizes not confirmed. | low (unverified) |
| Verbal uncertainty as linear feature, arXiv 2503.14477 (Apr 2025) https://arxiv.org/pdf/2503.14477 [S] | Mismatch between semantic and verbal uncertainty; inference-time intervention | unverified | Intervention reduced confident hallucinations on short-form answers ~30 % on average. Intervention is activation-level, not prompt text. | med |
| Cacioli, "Distilling Self-Consistency into Verbal Confidence", arXiv 2604.24070 (Apr 2026) https://www.alphaxiv.org/abs/2604.24070 [S] | Verbal confidence on Gemma 3 4B-it; pre-registered fine-tune | Gemma 3 4B-it | Verbal confidence channel classified invalid; negative result; linear probes beat verbal channel. Single-author preprint. | high (4B, verbal tags) |
| "Wired for Overconfidence", arXiv 2604.01457 https://www.alphaxiv.org/abs/2604.01457 [S] | Mechanistic study of inflated verbalized confidence, 2 models, 3 QA sets | unverified | Inflated verbal confidence localised to a few layers. | low |
| ALCE citation prompting (see Angle 3) | — | — | Prompt-only citation weak for smaller models (Huang et al. ACL 2024). | high |
| Anthropic docs, "Verify with citations" and "quote then answer" [F] | Vendor patterns | Claude | Require a supporting quote per claim; remove claims with no quote. | high (wording), low (evidence) |

Count: 7 sources. Measured for ≤8B: verbal-confidence negative (4B, Cacioli), prompt-only citations weak (7B, Huang). Only the verbal-uncertainty paper reports a positive effect, and it is not a prompt.

---

## Angle 7: Multi-turn follow-ups and capability requests

| Source | What was measured | Model sizes | Finding (one line) | Relevance |
|---|---|---|---|---|
| "LLMs Get Lost In Multi-Turn Conversation", Laban et al., ICLR 2026 oral, arXiv 2505.06120 https://arxiv.org/abs/2505.06120 [F] | Single-turn instructions sharded across turns; 200k+ simulated conversations, six generation tasks | Stated range "Llama 3.1 8B to Gemini 2.5 Pro"; per-model sizes not extracted | Average drop of 39 % across six tasks; unreliability rises more than aptitude loss; models make early assumptions and do not recover. Prompt-level fixes such as temperature or recap reportedly insufficient (from secondary summary, not checked in paper). | high |
| MS-XSB (see Angle 2) | multi-turn over-refusal | Llama | over-refusal worsens in multi-turn | high |
| "Over-Searching in Search-Augmented LLMs", arXiv 2601.05503 https://arxiv.org/pdf/2601.05503 [S] | Abstention across 1–9 turns, GPT-4o-mini | GPT-4o-mini (≈ not small open) | Abstention holds or improves when earlier turns are unanswerable; weakens when earlier turns are answerable, so the model leans to answering. Direct history effect on abstention. | high (history effect), med (model class) |
| "Intent Mismatch Causes LLMs to Get Lost", arXiv 2602.07338 https://arxiv.org/html/2602.07338v1 [S] | Counter-explanation to Laban | unverified | Argues intent mismatch, not early assumptions, drives the loss. Not checked. | med |

Count: 4 sources. No benchmark specifically on refusal snowball in small (1–4B) assistants found.

---

## Totals

| Angle | Sources found | Small-model (≤8B) evidence |
|---|---|---|
| 1 Abstention | 7 | 1 (2601.20126, 2B/4B, training) |
| 2 Over-refusal | 6 | weak (Qwen3 in SkillShield; sizes unverified) |
| 3 RAG grounding | 6 | 1 negative (Huang, 7B citations) |
| 4 Length | 6 | 2 (multilingual small models; Zhao, sizes unverified) |
| 5 Vendor | 2 + 2 gaps | Qwen card only (no hallucination text) |
| 6 Patterns | 7 | 1 (Cacioli, Gemma 3 4B, negative) |
| 7 Multi-turn | 4 | none at ≤4B |

---

## Concrete wordings / patterns the sources support (≤ 10)

Support level is stated honestly. "Vendor" = wording from Anthropic docs, not measured on small models.

1. Permission to abstain (Anthropic, vendor): "Explicitly give Claude permission to admit uncertainty." Example wording: *"If you're unsure about any aspect or if the report lacks necessary information, say \"I don't have enough information to confidently assess this.\""* — support: vendor only, no small-model measurement.
2. Fixed null phrase for missing quotes (Anthropic, vendor): *"If you can't find relevant quotes, state \"No relevant quotes found.\""* — support: vendor; pattern for grounding, untested at 4B.
3. Quote-then-answer for longer contexts (Anthropic, vendor): *"Extract exact quotes from the policy that are most relevant ... Only base your analysis on the extracted quotes."* — support: vendor; docs threshold is >20k tokens, so may not apply to short retrieved chunks.
4. Per-claim quote check with removal (Anthropic, vendor): *"For each claim, find a direct quote ... If you can't find a supporting quote for a claim, remove that claim ... and mark where it was removed with empty [] brackets."* — support: vendor; mechanism matches FActScore-style precision, not measured on 4B.
5. Restrict to provided material (Anthropic, vendor): *"Only use information from provided documents and not general knowledge."* — support: vendor; FaithfulRAG (ACL 2025) argues strict adherence suppresses parametric knowledge, so this is a trade-off, not a free win.
6. Shorter answer scope (length evidence): cap answer length and enumerate atomic claims rather than 3–5 paragraphs — support: Zhao (ACL Findings, facts-exhaustion mechanism) and multilingual small-model result, sizes unverified. Our inference, not a tested wording. Note the Giskard brevity result: brevity pressure can also hurt accuracy.
7. Abstention as a reward, not a sentence (2601.20126): moderate abstention value r_abs ≈ −0.25 to 0.3 — support: measured on Qwen3-4B-Instruct and Granite-3.3-2B, but **training-time**, not prompting. Listed for completeness; not usable as a prompt.
8. Chain-of-Verification loop: draft → verification questions → answer each question without seeing the draft → revise — support: measured on Llama 65B; small-model unverified.
9. Verbal confidence tag (negative evidence): "Rate your confidence 0–100" — support: Cacioli (Gemma 3 4B-it) found verbal channel invalid; do **not** rely on it without a calibration check.
10. Prompt-only citation per sentence (negative evidence): support: Huang et al. (ACL 2024) found prompting-only citations unsatisfactory at small scale; fine-tuning with fine-grained reward was needed.

---

## Five strongest sources to verify first

1. **Laban et al., "LLMs Get Lost In Multi-Turn Conversation", ICLR 2026, arXiv 2505.06120** https://arxiv.org/abs/2505.06120 — multi-turn degradation with the strongest design; need per-model sizes and whether prompt-level fixes were tested. (Fetched: 39 % average drop; the search snippet gave 90 %→65 % for one setting, reconcile.)
2. **Rewarding Intellectual Humility, arXiv 2601.20126** https://arxiv.org/abs/2601.20126 — only small-model (2B/4B) abstention evidence; training-time, so verify the accuracy cost numbers.
3. **FaithfulRAG, ACL 2025, arXiv 2506.08938** https://arxiv.org/abs/2506.08938 — direct counter-evidence to "answer only from context"; check its baselines for small models.
4. **SkillShield, arXiv 2608.25817** https://arxiv.org/pdf/2608.25817 — measured false-refusal on benign code tasks under safety-rule bundles including Qwen3; confirm model size and the 16.3 % figure.
5. **Huang et al., ACL 2024 (citation rewards), arXiv 2402.04315** https://arxiv.org/pdf/2402.04315 — prompt-only citation weakness at 7B; confirm the table values.

Also to check (not in the top 5): Zhao et al. ACL Findings 2025 on length and facts-exhaustion (URL not yet located; start from themoonlight.io review), FaithEval small-model rows (arXiv 2410.03727), and the Qwen3-4B-Instruct-2507 card for any system-prompt guidance (none found on the page).

---

## Gaps (explicit)

- No study found that compares "I don't know" system-prompt wording with a 1–8B model and reports answer rate **and** fabrication rate together.
- No study found that varies honesty-instruction wording and reports XSTest-style refusal per wording.
- No controlled "Detailed vs short" measurement on 4B models.
- No small-model multi-turn refusal snowball benchmark found.
- No Qwen-published hallucination or system-prompt guidance found.
