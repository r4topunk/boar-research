# Methods survey: a fair "X% as good as web + frontier AI" benchmark for an offline assistant

## 0. Anchor: what the bounty text actually fixes (and what it leaves open)

From `<workspace>/BOUNTY_31.md` (mirror of the poidh page; OG post https://x.com/VitalikButerin/status/2100695863026954698):

- Bar: "Submissions are judged against the requirements above and the bar described in the post author's post: a useful, fully offline research tool that's >50% as good as internet + frontier models."
- Task scope: "a casual info lookup and research tool" that must "handle useful research questions beyond simple factual recall, including explanation, comparison, synthesis, and reasoning" and "respond at speeds that feel usable for real lookups on a phone".
- Proof: "several example queries and responses (include ones a 1B model would fail on)".
- Decider: "If the post author publicly confirms that a submitted build meets that bar, that submission wins"; otherwise contributors "select a winner they believe best satisfies the requirements and spirit".

What the text does **not** fix: the baseline system, the question distribution, the scoring unit, or what "50% as good" means numerically. Those are the choices the ruler must make explicitly and defend.

UNKNOWN: I could not read the OG X post itself (x.com returned HTTP 402 to the fetcher), so every quote above is from the bounty file, not the tweet. A second public lead exists: PANews (https://panews.io/articles/01a0dcec-f582-7131-b756-7f6039640b50, dated September 26) says the post author posted about testing offline mobile apps (https://x.com/VitalikButerin/status/2103762130554204651). Its only quoted text is his example query "the best vegetarian restaurants in my city". The article paraphrases him and gives no verbatim quotes. Someone should read that post directly before treating it as evidence of which query types he values, such as local or venue queries.

### Critical interpretation trap: "50% as good" is not "wins 50% of the time"
- A pairwise **win-rate of 50%** against the reference means **parity** (equally good), not half as good. If a pairwise preference is the headline, the bar is set far above what the post author asked for.
- In reference-relative scores like DeepResearch Bench RACE, s_t/(s_t+s_r) ([arXiv 2506.11763](https://arxiv.org/abs/2506.11763)), 0.5 also means parity. "s_t = 0.5·s_r" corresponds to a relative score of **0.333**.
- A **ratio of mean absolute scores** (offline mean / baseline mean) reads most literally as "X% as good". It is inflated by any rubric floor, though, because a nonsense answer still earns the minimum points. The fix is to subtract the floor, as BOAR's "floor-adjusted" ratio already does. The cleanest form anchors 0 = "useless / no answer" and 1 = "the baseline's answer".
- A user-centric alternative is the **ratio of task-success rates**: the share of queries where the answer is good enough to act on, offline over baseline. It maps to "casual info lookup" and is easy for a non-specialist judge to understand.
- Recommendation: pre-register one primary operationalisation and report the others as sensitivity analyses. Win-rate should be a secondary "how often it is at least as good" number, not the bar.

## 1. LLM-as-judge: absolute vs pairwise scoring

- **MT-Bench / Chatbot Arena** (Zheng et al. 2023, [arXiv 2306.05685](https://arxiv.org/abs/2306.05685)) introduced single-answer grading, pairwise comparison, and reference-guided grading. A strong judge reached ">80% agreement" with humans, about the human-human level. The paper also documented position, verbosity, and self-enhancement bias, and showed that judges fail on math/reasoning unless given a reference answer.
- **Pairwise** comparisons are more sensitive to small quality differences and are more stable against scale drift. They are more exposed to position and length bias, and they produce preferences, not magnitudes. **Absolute rubric scores** give magnitudes, which a ratio needs, but they drift with the judge and compress gaps.
- **G-Eval** (Liu et al. 2023, [arXiv 2303.16634](https://arxiv.org/abs/2303.16634)) uses chain-of-thought plus probability-weighted scores. **Prometheus** (Kim et al. 2023, [arXiv 2310.08491](https://arxiv.org/abs/2310.08491)) adds per-item rubrics plus a reference answer, and the reference raises agreement.
- **WildBench** (Lin et al. 2024, [arXiv 2406.04770](https://arxiv.org/abs/2406.04770)) pairs a checklist-guided absolute score (WB-Score) with pairwise WB-Reward against several baselines, and adds a length penalty. That is a useful template for running both scoring modes.
- Implication: use **absolute, reference-anchored scores for the ratio**, and keep **pairwise vs the baseline** as a secondary check that should rank systems the same way.

## 2. Judge biases and mitigations

| Bias | Evidence | Mitigation |
|---|---|---|
| Position | Wang et al. 2023 [arXiv 2305.17926](https://arxiv.org/abs/2305.17926) (swapping order flips verdicts); Shi et al. 2024 [arXiv 2406.07791](https://arxiv.org/abs/2406.07791) (position bias varies by judge/task, worse when quality gap is small) | Score both orders and count disagreements as a tie; randomise order; report the consistency rate |
| Verbosity / style | Saito et al. 2023 [arXiv 2310.10076](https://arxiv.org/abs/2310.10076); length-controlled AlpacaEval (Dubois et al. 2024, [arXiv 2404.04475](https://arxiv.org/abs/2404.04475)); LMSYS style control ([lmsys.org/blog/2024-08-28-style-control](https://lmsys.org/blog/2024-08-28-style-control/)) | Cap answer length or regress out length/markdown; rubric criteria for correctness that ignore form |
| Self-preference / family | Panickssery et al. 2024 [arXiv 2404.13076](https://arxiv.org/abs/2404.13076) (self-recognition correlates with self-preference); Wataoka et al. 2024 [arXiv 2410.21819](https://arxiv.org/abs/2410.21819) (bias toward low-perplexity, familiar text) | Judge from a family different from both the baseline and the system under test; or a **jury** of judges from several families (PoLL, Verga et al. 2024, [arXiv 2404.18796](https://arxiv.org/abs/2404.18796): a panel of smaller, diverse models beat a single large judge and showed less intra-model bias) |
| Judge can't answer the item | Krumdick et al. 2025 "No Free Labels" [arXiv 2503.05061](https://arxiv.org/abs/2503.05061): judges grade poorly on questions they can't answer themselves; a weaker judge with **human-quality references** beat a stronger one with synthetic references | Verified reference answers or key facts per item |
| Agreement looks high but scores are off | Thakur et al. 2024 [arXiv 2406.12624](https://arxiv.org/abs/2406.12624): high percent agreement can hide large score deviations; use Cohen's κ, not raw agreement. JUDGE-BENCH (Bavaresco et al. 2024, [arXiv 2406.18403](https://arxiv.org/abs/2406.18403)): agreement varies widely by task | Report κ/Spearman against humans on a spot-check subset, broken down by item type |

BOAR's own XFAM result shows exactly this family effect: a Claude judge vs a non-Claude judge gives a stable offset of about +0.10 with the ranking unchanged. A public ruler should therefore **report the ratio under at least two judge families** (or a jury) and state that the bar is met only if it holds under the stricter judge, or under the jury mean, pre-registered.

## 3. Arena-style win-rates

- **Chatbot Arena** (Chiang et al. 2024, [arXiv 2403.04132](https://arxiv.org/abs/2403.04132)) fits Bradley-Terry strengths from crowd pairwise votes and reports CIs. It needs thousands of votes, which is not feasible for us. The useful pieces are BT/Elo for more than two systems and ties counted as 0.5.
- **Arena-Hard-Auto / BenchBuilder** (Li et al. 2024, [arXiv 2406.11939](https://arxiv.org/abs/2406.11939)) uses an LLM judge pairwise against a fixed baseline on 500 curated prompts. It measures *separability* (how often CIs between models don't overlap) and agreement with the human Arena ranking. Adopt the separability idea: show that the benchmark separates a 1B model, our 4B model, and the frontier baseline, with non-overlapping CIs.
- Caveat for the bar: the win-rate against a frontier+web reference will sit near 0 for any offline system, which BOAR already observes. That is evidence the win-rate is the wrong primary metric for a "50% as good" bar. It is still worth reporting honestly.

## 4. Reference-answer and baseline design

- The baseline must be the literal "internet search + frontier AI models": a frontier model with web search, run at a fixed date with archived outputs and cited URLs. Freeze the baseline answers and publish them, so the bar does not move as the web changes.
- **Reference answers** serve as grading aids, not as the comparison target. Keep (a) the baseline's answer, which is the "100%" anchor, separate from (b) a verified key-facts list per item, which is what correctness is checked against. Krumdick et al. show (b) is what keeps judges honest.
- **DeepResearch Bench** RACE ([arXiv 2506.11763](https://arxiv.org/abs/2506.11763)) generates task-specific weighted criteria (comprehensiveness, depth, instruction-following, readability) and scores the target *relative to a reference report*. Its FACT component checks citation support. It is the closest published analogue to "X% as good as a reference research answer"; mind the 0.5 = parity convention.
- Items where the baseline itself is wrong must be flagged and either excluded or scored against the key facts. Otherwise the offline system is penalised for disagreeing with a wrong reference.

## 5. Task-success rubrics

- **HealthBench** (Arora et al. 2025, [arXiv 2505.08775](https://arxiv.org/abs/2505.08775)): physician-written, **per-item rubric criteria with positive and negative point values**, graded by a model judge and validated against physician grading. This fits the bounty's mixed "explanation, comparison, synthesis, reasoning" items well: each item lists the 3–7 things a useful answer must contain, the things it must not do (dangerous or false claims), and weights.
- Add an item-level binary "**would a casual user be able to act on this?**" label. This gives the task-success ratio from §0 and is the easiest number to explain to the post author.
- Rubric points should come from humans, or from a model outside the judge's family that is then checked by humans. A judge grading against its own rubric compounds self-preference.

## 6. Factuality sets as design patterns

- **SimpleQA** (Wei et al. 2024, [arXiv 2411.04368](https://arxiv.org/abs/2411.04368)): short fact questions with one indisputable answer, graded correct / incorrect / **not attempted**, adversarially collected against GPT-4. That collection method biases the set against the model it was filtered on. Good for the "lookup" slice and for abstention.
- **FRAMES** (Krishna et al. 2024, [arXiv 2409.12941](https://arxiv.org/abs/2409.12941)): multi-hop questions needing 2–15 Wikipedia articles, testing retrieval plus reasoning. Close to the "synthesis/comparison" requirement and natural for a Wikipedia-backed offline system.
- **HotpotQA** (Yang et al. 2018, [arXiv 1809.09600](https://arxiv.org/abs/1809.09600)): bridge and comparison multi-hop questions with supporting facts. Useful item templates, but heavily contaminated.
- **BrowseComp** (Wei et al. 2025, [arXiv 2504.12516](https://arxiv.org/abs/2504.12516)): hard-to-find, easy-to-verify facts that need persistent browsing. It is the wrong distribution for "casual lookup": nearly every offline system scores near 0 and it rewards agentic web search. At most a small "ceiling" slice.
- Lesson: the **item mix decides the outcome**. The mix must be justified from the bounty text ("casual info lookup and research", "beyond simple factual recall"), published as strata, and reported per stratum, so judges can re-weight it themselves.

## 7. Long-form factuality

- **FActScore** (Min et al. 2023, [arXiv 2305.14251](https://arxiv.org/abs/2305.14251)): split a long answer into atomic facts and compute the share supported by a knowledge source. Precision only; it does not reward coverage.
- **SAFE / LongFact** (Wei et al. 2024, [arXiv 2403.18802](https://arxiv.org/abs/2403.18802)): atomic facts checked with search; **F1@K** combines precision with recall against a target number of facts K, so a short, safe answer does not win by default.
- Applicability: run an atomic-fact precision check on long answers as a **guardrail metric** (an offline system must not reach "50%" by being verbose and wrong). Use the per-item rubric (§5) for coverage. The verification source must be the frozen key facts or archived pages, not live search, for reproducibility.

## 8. Calibration and abstention: penalise confident errors

- Kalai et al. 2025, "Why Language Models Hallucinate" ([arXiv 2509.04664](https://arxiv.org/abs/2509.04664)): binary grading rewards guessing. Their proposal is **explicit confidence targets**: correct = 1, "I don't know" = 0, wrong = −t/(1−t). For t = 0.5 that is −1; for t = 0.75, −2.
- SimpleQA's not-attempted category and **AbstentionBench** (Kirichenko et al. 2025, [arXiv 2506.09038](https://arxiv.org/abs/2506.09038)) show abstention as its own axis. A survey of abstention is Wen et al. 2024 ([arXiv 2407.18418](https://arxiv.org/abs/2407.18418)).
- Applicability: for a travel or offline tool, a confident wrong answer (wrong dosage, a closed venue, a wrong border rule) is worse than "I don't know offline". Score each answer as correct / partial / abstain / **confidently wrong**, with a pre-registered negative weight for the last, and apply the same scoring to the baseline. Otherwise the ratio rewards the side that guesses more.

## 9. Latency- and cost-aware utility

- **HELM** (Liang et al. 2022, [arXiv 2211.09110](https://arxiv.org/abs/2211.09110)) reports efficiency next to accuracy. **AI Agents That Matter** (Kapoor et al. 2024, [arXiv 2407.01502](https://arxiv.org/abs/2407.01502)) argues for **Pareto frontiers (accuracy vs cost/time)** instead of accuracy alone.
- The bounty makes speed a requirement ("respond at speeds that feel usable for real lookups on a phone"), not part of the 50% ratio. Recommendation: (a) keep the quality ratio latency-free; (b) report on-device p50/p90 time-to-first-token and time-to-complete-answer per tier on a named phone; (c) optionally show quality vs latency as a Pareto plot, e.g. fast tier vs deep tier with thinking. Do not fold latency into one composite score with an arbitrary discount, since a judge can't audit the discount.

## 10. Human vs LLM agreement and the human spot check

- MT-Bench ([arXiv 2306.05685](https://arxiv.org/abs/2306.05685)) found judge-human agreement about equal to human-human on chat preferences. Thakur et al. ([arXiv 2406.12624](https://arxiv.org/abs/2406.12624)) and JUDGE-BENCH ([arXiv 2406.18403](https://arxiv.org/abs/2406.18403)) show this does not transfer automatically to correctness or to new tasks.
- **Prediction-powered inference** (Angelopoulos et al. 2023, [arXiv 2301.09633](https://arxiv.org/abs/2301.09633)) and **AutoEval done right** (Boyeau et al. 2024, [arXiv 2403.07008](https://arxiv.org/abs/2403.07008)): combine many LLM-judge labels with a small random human-labelled subset to get a **bias-corrected estimate with valid CIs**. This is the principled way to use a human spot check: pick the items at random (stratified), not hand-picked, and the human labels then *correct* the LLM number instead of just anecdotally confirming it.
- Report κ/Spearman between humans and each judge family, per stratum, on that subset.

## 11. Sample size and CIs for 50–150 items

- Miller 2024, "Adding Error Bars to Evals" ([arXiv 2411.00640](https://arxiv.org/abs/2411.00640)): report SEs; use **paired** differences when both systems answer the same items; use **clustered SEs** when items share a source or topic; resample answers to measure within-item variance.
- Madaan et al. 2024 ([arXiv 2406.10229](https://arxiv.org/abs/2406.10229)): seed variance alone can move scores by amounts that look like real gains. Card et al. 2020 ([arXiv 2010.06595](https://arxiv.org/abs/2010.06595)): small NLP test sets are often underpowered.
- Rough size: with n = 100 and per-item score SD about 0.3, the SE of a mean is about 0.03. A ratio near 0.5 then has a 95% CI of roughly ±0.06–0.08 once baseline variance is included. That is enough to call "clearly above / clearly below 0.5", not to resolve ±0.03. Use paired bootstrap over items, with judge and generation seeds nested, for the ratio CI. Pre-register that the bar is met only if the **lower CI bound** is above 0.50, or state plainly that the claim is a point estimate. BOAR's own SEEDVAR result (about ±0.02 per-seed SD) says to use at least 2 generation seeds.

## 12. Contamination and who writes the items

- Contamination: Sainz et al. 2023 ([arXiv 2310.18018](https://arxiv.org/abs/2310.18018)); Golchin & Surdeanu 2023 ([arXiv 2308.08493](https://arxiv.org/abs/2308.08493)). **LiveBench** (White et al. 2024, [arXiv 2406.19314](https://arxiv.org/abs/2406.19314)) handles it with fresh, dated items and objective answers.
- Model-written evals (Perez et al. 2022, [arXiv 2212.09251](https://arxiv.org/abs/2212.09251)) carry the writer's distribution. Adversarial filtering against specific models (SimpleQA vs GPT-4; **Humanity's Last Exam**, [arXiv 2501.14249](https://arxiv.org/abs/2501.14249), filtered on frontier failures) biases a set *against* the filter model. Items a model family writes tend to be easy for that family's style of answer and judging.
- For our ruler: the baseline is a frontier model, the judge may be a frontier model, and items may be model-assisted. Every link where the same family appears twice is a bias path. Items should be written by humans, or by a non-Claude, non-baseline family with human editing. They should be dated after the offline models' training cutoff where possible, and **not filtered on either system's failures**, since that tilts the ratio. Publish a hash of the item set before running and the plaintext after. Keep a private held-out split for the final number and publish a dev split for reproduction.

## 13. Ten practices for a 50–150 item public benchmark (LLM-judged, human spot check)

1. **Define "X% as good" in one pre-registered formula**: floor-adjusted ratio of reference-anchored absolute scores (0 = useless, 1 = baseline answer). Report pairwise win-rate and task-success ratio as secondary numbers, and never present a 50% win-rate as the bar.
2. **Freeze and publish the baseline**: a named frontier model with web search, a fixed date, archived answers and URLs. Re-grade the baseline with the same rubric.
3. **Per-item human-written rubrics with negative points** (HealthBench-style) plus a **verified key-facts reference**, so the judge grades correctness rather than style or its own knowledge.
4. **A stratified item mix taken from the bounty's own words**: lookup, explanation, comparison, synthesis, reasoning, plus a small "would a 1B model fail" slice. Report per stratum so judges can re-weight.
5. **Penalise confident errors and credit honest abstention** (Kalai-style confidence target), applied identically to both systems.
6. **Judge-family control**: a judge from a family that neither wrote the items nor is the baseline, or a cross-family jury. Report the ratio under at least two families; the claim must hold under the pre-registered stricter rule.
7. **Bias hygiene**: both orders for any pairwise call, length cap or style control, blinding of system identity, and a published judge prompt and rubric (with hashes).
8. **Random, stratified human spot check (30–50 items) used statistically** (PPI / AutoEval) to bias-correct the LLM estimate and report κ. Hand-picked spot checks are anecdote, not calibration.
9. **Paired bootstrap CIs with at least 2 generation seeds**: state whether the lower bound clears 0.50, and pre-register pass/fail before the run.
10. **Contamination and authorship controls**: human or non-judge-family item writing, no adversarial filtering against either system, a dated, hashed held-out split for the headline number, and a public dev split plus harness for reproduction. Report on-device latency next to the ratio, not merged into it.

## UNKNOWN
- The exact wording of the post author's OG post and of the later post about offline mobile apps (status 2103762130554204651) is unverified here (X blocked the fetch). Read them before fixing the item mix, especially whether local or venue queries are central.
- Which judge family the post author or the contributors would trust is not stated publicly. Hence the recommendation to report multiple families.
- The baseline ("internet + frontier models") is unspecified as to which model, which search tool, and whether multi-turn is allowed. The ruler must name its choice and justify it as a conservative, strong baseline.
