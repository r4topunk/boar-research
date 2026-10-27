# gap_judge_panel: non-Claude judge panel + human-origin query seeds for held-out v0.3

State as of 2026-10-12. Extends `notes/eval_judge.md` (preference leakage, family lift, evalstats, open-judge overview) and `BENCH-V03-SPEC.md` (writer = Gemini web UI, O3 cross-family judge proposed as `openai/gpt-5.5`). Not repeated here except where new numbers were found. Nothing under blind/ or rnd/veil/ was opened. 0 judge calls, 0 downloads. Dataset licences were read from the HF Hub API (`cardData.license`) on 2026-10-12. "fetch-summary" means a small model summarised the page, so spot-check those numbers before quoting them in the claim. Cost arithmetic is mine and labelled.

## TL;DR

- **A two-vendor non-Claude panel costs tens of dollars, not hundreds.** At about 4k input and 400 output tokens per call:
  - gpt-5.5 [usage detail removed] per call ([usage detail removed] Batch/Flex).
  - gpt-5.6-terra [usage detail removed].
  - Gemini 3.1 Pro Preview [usage detail removed] ([usage detail removed] Batch).
  - Our Opus judge is [usage detail removed].
  - A 440-call claim run on gpt-5.5 plus Gemini 3.1 Pro [usage detail removed] before reasoning tokens, and [usage detail removed] or less with ≈ 1k reasoning tokens per call (my arithmetic).
  - Both APIs are available in Brazil.
  - Sources: https://developers.openai.com/api/docs/pricing · https://ai.google.dev/gemini-api/docs/pricing (page dated 2026-10-09)
- **Held-out exposure rule: paid tier only.** The Gemini API's unpaid tier may use prompts and responses to improve products, and human reviewers may read them. The paid tier does not train on them and keeps logs only "for a limited period". OpenAI API data is not used for training by default and is retained for up to 30 days. Each v0.3 judge call is therefore an EXPOSURES row: vendor, tier, retention. https://ai.google.dev/gemini-api/terms · https://developers.openai.com/api/docs/guides/your-data
- **Family choice is asymmetric.** v0.3 references are written by Gemini (spec D1).
  - A Gemini judge then shares a family with the reference. It will tend to prefer the reference, which pushes BOAR's ratio *down*: biased against us, so conservative.
  - An OpenAI judge is neutral to both sides.
  - Use OpenAI as the primary cross-family judge, Gemini as the conservative bound and Opus as continuity. Report all three. Never average them into one number.
  - Basis: family lift +0.067 (2609.17857, in eval_judge.md).
- **A bigger panel adds little information; its value is bias balance.** Nine frontier judges from seven families gave "about 2 independent votes' worth of information". The best single judge matched or beat the full panel. https://arxiv.org/abs/2605.29800 PoLL (three families) still beats one large judge on intra-model bias at about 1/7 the cost. https://arxiv.org/abs/2404.18796
- **No open judge that fits a 16 GB M4 is validated for our task.** On FLASK, Prometheus 2 reaches Pearson 0.545 (7B) / 0.555 (8x7B) vs humans and 0.617 / 0.659 vs GPT-4. It accepts a reference plus a 1–5 rubric natively. The 8x7B does not fit in 16 GB. Selene-1-Mini 8B has no human long-form-QA number. JudgeLM sits on a LLaMA-1 licence. Skywork-Critic is pairwise only. Our JUDGE2 (Gemma 4 26B, κ 0.32/0.55) remains the best local option. https://arxiv.org/html/2405.01535
- **PPI human spot-check: about 25 labels corrects the bias but not the CI width.** evalstats sets the floor at N ≥ 50 judged items and ≥ 15 human labels, and its worked example uses N = 80 with 25 labels. Efficiency is 1/(1 − ρ²(1 − n/N)), about 1.4× at ρ² = 0.4. My calculation at N = 110, σ ≈ 0.18: 25 labels → CI ±0.059; 50 → ±0.044; all 110 → ±0.034. The theoretical cap is less than 2× label savings when the judge is no more accurate than the evaluated system. https://arxiv.org/html/2609.35815 · https://arxiv.org/abs/2410.13341
- **The best human-origin seed pool for "internet + frontier AI" questions is Search Arena 24k.**
  - 24,069 conversations with search-augmented LLMs (2025-03-18…05-08).
  - User prompts are CC BY 4.0, redacted with Google DLP, about 56–58 % English.
  - Each prompt carries an intent label: Factual Lookup is 19.3 %; most of the rest is synthesis, guidance or analysis.
  - Arena-140k (CC BY 4.0, 2025) and WildChat (ODC-BY, 1.04M conversations, 53 % English turns, factual 6.3 % of English first turns) come second.
  - https://huggingface.co/datasets/lmarena-ai/search-arena-24k · https://arxiv.org/html/2506.05334 · https://arxiv.org/html/2405.01470v1
- **Do not use these licences:**
  - LMSYS-Chat-1M forbids redistribution.
  - MS MARCO is "non-commercial research purposes only".
  - QQP falls under Quora's ToS (non-commercial, secondary source).
  - Pushshift is limited to Reddit moderators.
  - ShareGPT has no consent licence (the HF re-upload's "apache-2.0" tag was set by the uploader).
  - NQ (CC BY-SA 3.0), GooAQ (Apache-2.0) and Researchy Questions (CDLA-Permissive-2.0) are usable.
  - https://huggingface.co/datasets/lmsys/lmsys-chat-1m · https://microsoft.github.io/msmarco/

## Q1. Judge options outside the Claude family

Per-call cost = 4,000 × input price + 400 × output price, before reasoning tokens. Reasoning or thinking tokens are billed as output on both vendors. The pricing pages fetched do not state this, so treat it as UNKNOWN-confirm. Every +1k reasoning tokens adds [usage detail removed] on gpt-5.5, [usage detail removed] on gpt-5.6-terra and [usage detail removed] on Gemini 3.1 Pro.

| item | date | URL | what it is | key numbers | licence / terms | fit | bucket | novelty | proposed action + 0-call gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| gpt-5.5 (OpenAI API) | pricing page fetched 2026-10-12 | https://developers.openai.com/api/docs/pricing | frontier OpenAI model | [usage detail removed] in / [usage detail removed] cached / [usage detail removed] out per 1M; Batch and Flex [usage detail removed] / [usage detail removed] → **[usage detail removed]/call** ([usage detail removed] Batch) | API data not trained on by default; retained ≤ 30 days (https://developers.openai.com/api/docs/guides/your-data) | eval-side; Brazil supported (https://developers.openai.com/api/docs/supported-countries) | measurement | known (spec O3 names it); prices new | **Primary O3 judge.** judge.v1 bytes unchanged, both orders. Gate: 57-pair JUDGE2 agreement set vs Opus (≥ 49/57 same winner, κ reported). Cost ≈ 57 × 2 × [usage detail removed] [usage detail removed] to validate; claim run 440 × [usage detail removed] [usage detail removed] ([usage detail removed] with 1k reasoning). Needs r4to's paid-API OK + key. |
| gpt-5.6-sol / terra / luna | same | same | newer OpenAI tiers | sol $4/[usage detail removed] → [usage detail removed]; terra $2/[usage detail removed] → [usage detail removed]; luna [usage detail removed]/[usage detail removed] → [usage detail removed] | same | Build tier (≥ $5 credits): 5,000 RPM, 1M TPM (Sol/Terra) (https://developers.openai.com/api/docs/guides/rate-limits) | measurement | new | terra as a cheaper O3 if it passes the same gate; luna for L1-triage only |
| gpt-5.4 / 5.4-mini | same | same | previous gen | 5.4 [usage detail removed]/[usage detail removed] → [usage detail removed]; mini [usage detail removed]/[usage detail removed] → [usage detail removed] | same | — | — | new | fallback only |
| Gemini 3.1 Pro Preview | pricing page dated 2026-10-09 | https://ai.google.dev/gemini-api/docs/pricing | Google's Pro tier (no newer Pro listed) | [usage detail removed] / [usage detail removed] (≤ 200k ctx) → **[usage detail removed]/call**; Batch [usage detail removed] / [usage detail removed] → [usage detail removed]; **no free tier** | paid: "Google doesn't use your prompts… to improve our products"; logs kept a limited period (days unstated) (https://ai.google.dev/gemini-api/terms) | Brazil listed (https://ai.google.dev/gemini-api/docs/available-regions); Tier 1 = linked billing, [usage detail removed] cap, [usage detail removed] per 10-min spend limit; RPM visible only in AI Studio | measurement | new | **Conservative-bound judge.** It shares a family with the v0.3 references (spec D1), so it should under-rate BOAR vs the reference. Report it beside the others; never as the headline. Cost 440 × [usage detail removed] [usage detail removed]. "Preview" means the model id may change mid-claim: pin and record the id. |
| Gemini 3.6 / 3.8 Flash | same | same | Flash tier | [usage detail removed] / [usage detail removed] → [usage detail removed] (doubles to [usage detail removed] / [usage detail removed] in 2027); free tier exists | **unpaid tier trains on and human-reviews prompts**: never send v0.3 items to it | — | — | new | L1 triage alternative to Haiku; paid tier only for held-out |
| Gemini 2.5 Pro | same | same | older Pro | [usage detail removed] / [usage detail removed] → [usage detail removed] | same | — | — | new | none |
| Jev (typesafe-ai/jev, Vercel AI Gateway) | skill local; paper 2609.26550 v5 2026-10-09 | https://arxiv.org/abs/2609.26550 | decision-only evaluator with rubric "score" mode | [usage detail removed] per 1M input, output free → [usage detail removed]/call (local skill doc); family and weights UNKNOWN | gateway terms; weights not public | eval-side | measurement | known (eval_judge Q3) | cheap fourth voice for disagreement flags only; weak on reference-free prose |
| Panel theory: "Nine Judges, Two Effective Votes" | 2026-05-28 | https://arxiv.org/abs/2605.29800 | 9 frontier judges from 7 families on 3 NLI sets (100 human labels per item) | n_eff ≈ 2 of 9; panel accuracy 8–22 pp below independent voting; the best single judge ≥ the panel; smarter aggregation closes ≤ 11 % of the gap | paper | eval-side | measurement | new | Do not build a 5+ judge panel. Use 2–3 families for bias balance, report per-judge numbers and inter-judge error correlation. 0 calls. |
| PoLL (panel of diverse small judges) | 2024-04 | https://arxiv.org/abs/2404.18796 | 3-family panel vs one GPT-4 judge | beats single large judge across 6 datasets; less intra-model bias; > 7× cheaper | paper | — | measurement | known (eval-methodology.md, 10-06) | cite only |
| Prometheus 2 7B / 8x7B | 2024-05 | https://arxiv.org/html/2405.01535 · https://huggingface.co/prometheus-eval/prometheus-7b-v2.0 | open judge; input = instruction + response + **reference answer** + 1–5 rubric with level descriptions; outputs feedback + `[RESULT] n` | Pearson vs GPT-4 / vs Claude-3-Opus: Vicuna 0.666/0.654 (7B), 0.685/0.635 (8x7B); FLASK 0.617/0.561, 0.659/0.626; **FLASK vs humans 0.545 / 0.555**; MT-Bench human pairwise with ties 50.45 / 55.07 % | Apache-2.0 (HF API) | 7B Q4 ≈ 4–5 GB fits M4 16 GB; 8x7B Q4 ≈ 26 GB **does not fit** | measurement | known by name (eval_judge); numbers new | relevance 1. Our 1–5×3 rubric maps directly. Only worth a 57-pair JUDGE2-style check if a third, non-API family is required. |
| Selene-1-Mini 8B | 2025-01 | https://arxiv.org/html/2501.17195v1 | Llama-3.1-8B judge; optional reference field; 1–5 rubric | absolute-scoring avg 0.648 (vs GPT-4o-mini 0.640); expert-label accuracy: medical 0.717, FinanceBench 0.74; no long-form-QA vs human number (per-column table garbled in the fetch) | Apache-2.0 (card) + Llama 3.1 base terms | fits M4 | measurement | known (eval_judge) | relevance 1 |
| JudgeLM 7B/13B/33B | 2023-10 | https://github.com/baaivision/JudgeLM | pairwise/single judge, optional reference | agreement with its GPT-4 teacher 81.1 → 84.1 % (7B, ±ref), 89.0 → 89.3 % (33B); no human number in the table | code Apache-2.0; **models "under LLaMA's model license"** (LLaMA-1, non-commercial) | 7B/13B fit | — | known | relevance 0 (licence + age) |
| Skywork-Critic-Llama-3.1 8B/70B | 2024-09 | https://huggingface.co/Skywork/Skywork-Critic-Llama-3.1-8B | pairwise preference judge | RewardBench 89.0 (8B) / 93.3 (70B); pointwise "might not be particularly strong"; no reference or rubric mode | Skywork Community License (commercial allowed with conditions) | 8B fits | — | known | relevance 0: no 1–5 rubric + reference mode |
| CompassJudger-2 7B / 32B, Flow-Judge 3.8B, M-Prometheus 14B | 2024-09…2025-07 | HF API: opencompass/CompassJudger-2-7B-Instruct (Apache-2.0), flowaicom/Flow-Judge-v0.1 (Apache-2.0), Unbabel/M-Prometheus-14B (other) | open judges | no long-form-QA human agreement found; 32B Q4 ≈ 19 GB does not fit 16 GB | as listed | 7B/3.8B/14B fit | — | partly known | relevance 0–1 |
| "JEV-35B" | — | — | — | no model of that name on HF; the typesafe-ai/jev repo is private or absent (HF API 401) | — | — | — | — | closes the question |

**How each handles a 1–5 rubric with a reference.**
- **API frontier models (GPT, Gemini):** take judge.v1 verbatim. Pin the model id and the temperature/reasoning settings; record seed/fingerprint where exposed.
- **Prometheus 2:** native format (rubric with five level descriptions + reference). judge.v1 would need re-templating into its format, which is a new prompt and a new sha.
- **Selene:** reference optional, 1–5 native.
- **JudgeLM:** pairwise 1–10.
- **Skywork-Critic:** pairwise A/B only.

## Q2. Human-origin query sources for v0.3 seeds

Seed protocol (proposal):
1. A script filters candidates, using jev classification where possible.
2. r4to picks seeds. The **question text stays the human's** (light edits by r4to only: typos, de-dating).
3. The non-Claude model writes only gold, rubric and sources.
4. Add a `seed_source` field (dataset, row id) to the schema for attribution; ODC-BY and CC BY need attribution.

| item | date | URL | what it is | key numbers | licence | fit | bucket | novelty | proposed action + 0-call gate + cost |
|---|---|---|---|---|---|---|---|---|---|
| **Search Arena 24k** | 2025-03-18…05-08 (card updated 2026-03) | https://huggingface.co/datasets/lmarena-ai/search-arena-24k · https://arxiv.org/html/2506.05334 | real prompts sent to search-augmented LLMs (i.e. the bounty's "internet + frontier AI" use case) | 24,069 conversations, ≈ 11k users, 136 countries; English 56.4–58.3 % (paper inconsistent); intent labels by GPT-4.1 (κ 0.812 vs humans on top-2); Factual Lookup 19.3 %; topics: tech comparisons 22 %, market analysis 12.3 % (health/shopping present, travel not named) | **prompts CC BY 4.0**; outputs under provider terms; DLP-redacted | eval-side seeds; many prompts are time-sensitive (unfair offline) → filter | measurement (honest number); comparison cell | new | **Top seed pool.** Filter: English, first turn, intent ∈ {Factual Lookup, Info Synthesis, Explanation, Recommendation, Guidance}, then jev "answerable without post-2025 info" and "fits stratum X". Gate: count per stratum ≥ 3 × n needed. Cost [usage detail removed] of jev; parquet size UNKNOWN (check < 100 MB before any download, else r4to OK). |
| Arena human-preference 140k | 2025-04-17…07-24 | https://huggingface.co/datasets/lmarena-ai/arena-human-preference-140k | general Chatbot Arena prompts with category tags (math, creative, hard prompts, IF, criteria incl. domain knowledge) | 135,634 battles; 126 languages | **prompts CC BY 4.0**; no PII statement on card | seeds for explanation/reasoning strata | measurement | new | second pool; filter `is_code = false`, `creative_writing = false`, `domain_knowledge = true` |
| WildChat-1M / 4.8M | 2023-04-09…2024-05-01 (4.8M to 2024-05-02) | https://huggingface.co/datasets/allenai/WildChat-1M · https://arxiv.org/html/2405.01470v1 | ChatGPT conversations from consenting users (free GPT-3.5/4 proxy) | 1,039,785 convs, ≈ 204,736 users (IP estimate); English 52.94 % of turns; English first-turn mix: creative writing 61.9 %, analysis 13.6 %, factual info 6.3 %; country field (205 values), Presidio PII redaction | **ODC-BY** (HF API; paper still says AI2 ImpACT, superseded) | seeds; heavy creative/roleplay share → low yield | measurement | known by name (critique); numbers new | third pool. Estimated yield (inference): ≈ 0.5M English first turns × 6.3 % factual ≈ 30k factual prompts; travel/health/crypto share UNKNOWN. Gate: jev stratum classifier on a 5k sample. |
| Researchy Questions | 2024-02 | https://huggingface.co/datasets/corbyrosset/researchy_questions | ≈ 96k real Bing queries (90k train / 6.45k test), non-factoid, decomposable | filters: decompositional ≥ 0.6, non-factoid ≥ 0.75; ClueWeb22 click docs | **CDLA-Permissive-2.0** | synthesis/comparison/explanation seeds; queries are short and keyword-ish | synthesis, comparison | known (eval_judge Q2, as corpus) | Seeds for synthesis + comparison (the weakest cells). **Conflict:** eval_judge proposes it as a notes corpus (B6 QNOTES); if used for seeds, exclude seed ids from any pack build, or v0.3 leaks into the build. |
| Natural Questions | 2019 | https://huggingface.co/datasets/google-research-datasets/natural_questions | aggregated real Google queries with Wikipedia answers | ≈ 307k train / 7.8k dev (from the TACL paper, not re-fetched) | **CC BY-SA 3.0** (share-alike on derived items) | factoid, Wikipedia-answerable; skews to entertainment trivia | wrong fact | new to v0.3 | low priority; v0.3 needs practical questions, NQ gives trivia |
| GooAQ | 2021 | https://huggingface.co/datasets/allenai/gooaq | ≈ 3M+ questions from Google autocomplete (count from paper, not re-fetched) | — | **Apache-2.0** (HF API) | practical "how/what/can I" phrasing, incl. health/travel; answers are Google snippets (do not use) | travel-practical, health | new | cheap keyword pool for travel-practical/health seeds |
| MS MARCO | 2016+ | https://microsoft.github.io/msmarco/ | real Bing queries | 100k (QnA v1) → > 1M queries | "**non-commercial research purposes only**", no licence granted | public repo + bounty = grey | — | new | relevance 0: do not use |
| LMSYS-Chat-1M | 2023-04…08 | https://huggingface.co/datasets/lmsys/lmsys-chat-1m | 1M convs, 25 models, 154 languages | — | custom agreement: "should not distribute, copy… host"; commercial use allowed; gated | seeds would be derived redistribution → grey | — | new | relevance 0 (use Arena-140k / Search Arena instead) |
| ShareGPT (Vicuna re-upload) | 2023-04 | https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered | scraped user-shared ChatGPT logs | — | HF tag "apache-2.0" set by an anonymous uploader; no user consent licence; source site gone | — | — | new | relevance 0 |
| Quora Question Pairs | 2017 | https://arxiv.org/pdf/2505.24147 (secondary licence audit) | 400k question pairs | — | Quora ToS, non-commercial (secondary source; primary page not found) | — | — | new | relevance 0 |
| Reddit (Pushshift) | 2023 → | https://reddit.birdcat.cafe/r/Pushshift (mirror of r/pushshift announcements) | — | access restricted to approved moderators, moderation use only; community torrents (Arctic Shift, Academic Torrents) of unclear ToS status | Reddit terms | — | — | new | relevance 0: no clean licence path |
| Stack Exchange travel / expatriates / bitcoin / ethereum titles | dump 2026-06-30 | https://archive.org/details/stackexchange_20260630 | human-written question titles | per-site counts in notes/datastores.md | CC BY-SA (per post) | strong practical/crypto seeds | travel, crypto | known (datastores, as a corpus) | Same **leakage conflict** as Researchy: if datastores ships an SE pack, SE-seeded v0.3 items have their answer in the pack verbatim. Pick one role, or hold seed posts out of the pack by id. |

## Q3. PPI / human spot-check protocol

| item | date | URL | key numbers | licence | novelty | action |
|---|---|---|---|---|---|---|
| evalstats PPI | 2026-09-20 | https://arxiv.org/html/2609.35815 · https://github.com/ianarawjo/evalstats | `compare()` with `alignment=` needs ≥ 50 judged items; human labels ≥ 15 (hard cutoff); worked example N = 80, n_lab = 25 (BiGGen); label efficiency 1/(1 − ρ²(1 − n/N)); worth ≈ 1.5× the labels at ρ² = 0.4; ρ² < 0.2 = useless judge; CLI `evalstats label` samples items to label; one factor only, no multi-run data | MIT (README) | known (eval_judge), API details new | Tooling choice. The no-multi-run limit means one seed per PPI analysis: run it per seed, or average seeds per item first. |
| Limits to scalable evaluation ("won't beat twice the data") | 2024-10 (v4) | https://arxiv.org/abs/2410.13341 | when the judge is no more accurate than the evaluated model, debiasing cannot cut ground-truth labels by more than ½; in practice savings are smaller | paper | known (10-06 "Limits paper") | Expectation setting: PPI will not turn 25 labels into a ±0.03 claim. |
| AutoEval done right | 2024-03 | https://arxiv.org/abs/2403.07008 | effective human sample +50 % with GPT-4 labels | paper | known (10-06 #32) | — |
| Confidence-driven inference | 2024-08 | https://arxiv.org/abs/2408.15204 | uses LLM confidence to choose which items humans label; valid CIs, never worse than human-only | paper | new | Choose human labels where the 3 judges disagree most, not uniformly (needs the method's weighting to stay valid). |
| Lee et al. Rogan-Gladen correction | ICML 2026 | https://github.com/UW-Madison-Lee-Lab/LLM-judge-reporting | adaptive label allocation | no licence | known | for the binary win/tie metric |

**Sizing (my calculation, σ_item ≈ 0.18 floor-adjusted from V-para, N = 110, ρ² = 0.4):** SE ≈ √(0.6σ²/n_lab + 0.4σ²/N).
- n_lab = 25 → ±0.059 (95 %).
- n_lab = 40 → ±0.049.
- n_lab = 50 → ±0.044.
- n_lab = 110 → ±0.034 (≈ the human-only CI).

**Protocol proposal.**
1. r4to labels the 25 items the three judges disagree on most, plus 15 random items (40 labels, ≈ 3 min each, ≈ 2 h).
2. He sees question + reference + BOAR answer, with system identity hidden, and gives a binary "as good as the reference for the user's purpose?" plus the 1–5 usefulness score.
3. Run PPI via evalstats per judge.
4. Report the PPI-corrected mean beside the raw judge means.
5. Use it as a **bias check** (does the judge–human gap CI exclude 0?), not to tighten the claim CI.

## Q4. Third-party blind comparison of several offline apps

| item | date | URL | what | key numbers | licence | novelty | action |
|---|---|---|---|---|---|---|---|
| Chatbot / Search Arena protocol | 2024–26 | https://arxiv.org/html/2506.05334 | anonymous side-by-side, randomized order, identities hidden, user votes | Search Arena 12,652 votes over 24k convs | prompts CC BY 4.0 | known (Arena) | template for a same-sitting regrade |
| Competitor regrade (eval_judge Q5) | 2026-10 | [competitor link removed] | public answers on BOAR-v2's 61 questions (MIT) | grader spread 10–20 pts | MIT | known | — |
| **New option: run competitors' public builds on our v0.3** | — | (their repos, MIT) | competitors' apps answer *our* held-out items; one panel grades all apps blind in one sitting | none published | MIT apps | new | Avoids copying their test sets entirely: the items are ours, and their APK only produces answers. Needs a device per app and stays eval-side (no code in our build). It is also an exposure: v0.3 items are typed into third-party apps that are offline and local, so it is acceptable, but log it. Cost: ≈ 110 × (apps) × panel calls; device-blocked until a phone is in hand. |

## Searched, found nothing

- A published protocol specific to comparing **offline** assistants blind across vendors: none. The Arena/PoLL general patterns are the closest.
- An English share or travel/health/crypto counts for WildChat or Search Arena: not published. The HF datasets-server search API timed out (> 120 s), so the keyword counts were not obtained.
- An open judge with published agreement vs humans on ≈ 250-word research answers: none, beyond Prometheus 2's FLASK 0.55.
- RPM numbers for Gemini 3.1 Pro paid Tier 1: not on the public page (AI Studio only).
- OpenAI's mapping of gpt-5.5 to a rate-limit family (Astra/Sol/Terra/Luna): not stated on the rate-limit page.
- The primary Quora licence page for QQP: not found.

## UNKNOWN

- Whether reasoning/thinking tokens are billed as output on gpt-5.5 and Gemini 3.1 Pro. Assumed yes; the pricing pages fetched do not say. The actual reasoning length under judge.v1 is unknown until a 5-call probe.
- Gemini paid-tier log retention in days (the terms say only "limited period"; Search grounding: 30 days). Never enable grounding for the judge.
- Parquet sizes of Search Arena 24k and Arena-140k (the 100 MB download rule).
- Whether r4to's account can open paid API billing in Brazil (an account action; r4to only).
- Whether gpt-5.5 as judge shows self-preference toward Gemini-written references. It is not same-family, so no lift is expected; unmeasured.
- Whether human-origin seeds change v0.3 difficulty relative to the Gemini-proposed topics in the spec. "What has been lost with synthetic evaluation" (in eval_judge) says human items are harder.
