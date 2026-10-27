# LLM-as-a-judge reliability and noise reduction: research notes

Date: 2026-10-20. Angle: judge test-retest consistency, repeated sampling, rubric granularity, pairwise vs absolute, position bias, power and sample size under noisy judges, checklist evaluation.
Context: BOAR (offline Android RAG assistant, Qwen3-1.7B main model). Walls measured 2026-10-20 with a Haiku judge: 1-5 correctness re-judged on identical text changed the score on 13 of 37 items.

## Searches run

WebSearch, mode standard, 9 queries:
1. LLM-as-a-judge test-retest reliability, repeated sampling noise
2. LLM judge checklist binary vs Likert rubric granularity agreement
3. pairwise vs pointwise position bias mitigation swap
4. statistical power sample size noisy LLM judge MDE
5. CheckEval checklist binary sub-questions
6. prediction-powered inference LLM judge bias correction
7. LLM judge temperature 0 nondeterminism
(plus a few follow-ups)

WebFetch on primary arXiv abstract pages (each opened): 2606.13685, 2511.21140, 2601.05420, 2406.12319, 2606.26185, 2403.18771, 2602.02219, 2606.00093, 2306.05685, 2412.12509.

Not fetched: full PDFs. Most numbers below come from abstracts or the fetched abstract pages, so they are not verified against full-paper tables. Licences are as shown on each arXiv page.

## Findings

### F1. Single-run judge verdicts flip under identical reruns (load-bearing)
- Source: https://arxiv.org/abs/2606.13685 ("The Coin Flip Judge? Reliability and Bias in LLM-as-a-Judge Evaluation", Abel Yagubyan, submitted 2026-04-23). Licence: arXiv non-exclusive 1.0.
- Models: GPT-4o-mini and GPT-4.1-mini (both OpenAI, single provider). 29 tasks, 10 categories. 50 pairwise and 50 pointwise trials per question.
- Numbers: pairwise preferences "flip on average 13.6% of the time"; 28% of questions exceed a 20% flip rate; one question reaches 56%. Pointwise mean score gaps 0.19 to 0.36 on a 10-point scale, not significant in aggregate. Cross-judge agreement 76% (kappa 0.51). Semantically equivalent prompt templates change majority outcomes in 25% of cases. Deterministic decoding "reduces but does not eliminate" inconsistency.
- Averaging: 11 repeated trials are needed for a majority vote to recover the 50-trial reference verdict with 95% probability on average; 15 for high-variance questions.
- Recommendations from the paper: treat single-trial judging as too noisy for high-stakes evaluation, use multi-trial aggregation, randomize answer position, report uncertainty.
- Limitation stated by the author: both judges from one provider; cross-provider replication is the next step.

### F2. Temperature 0 is not reproducibility (load-bearing for the judge setup)
- Source: https://arxiv.org/abs/2606.26185 ("Necessary but Not Sufficient: Temperature Control and Reproducibility in LLM-as-Judge Safety Evaluations", Hiroki Tamba, single author). Licence: CC BY-NC-ND 4.0 (NC: do not reuse content in BOAR publications without checking; cite only).
- Setup: an open-source safety-evaluation harness that never set temperature or seed, so the provider default of 1.0 applied. Per-item disagreement reached up to about 50% over 20 runs (at default temperature).
- Under forced greedy decoding (top_k=1), 1 to 2 of 7 borderline items stayed non-reproducible.
- The abstract says a Claude model (Opus 4.7/4.8) has deprecated the temperature parameter, which removes this mitigation for newer Claude models. Relevant to any Claude Haiku/Opus judge BOAR uses: pin the judge's sampling settings where the API allows it, and expect residual flips anyway. (Model names are as stated in the abstract; not independently checked.)

### F3. Infrastructure-level nondeterminism at t=0 (supporting F2)
- Source: same arXiv 2606.13685 (F1). The authors attribute residual t=0 flips (GPT-4.1-mini non-zero flips on 7 of 29 questions, one at 50%) to API-level floating-point and batching effects rather than sampling.
- Secondary: https://arxiv.org/abs/2603.04417 ("Same Input, Different Scores") reports cross-model variability at t=0, with lower temperature helping some models (GPT-4o, Gemini) but having limited or inconsistent effects for Anthropic models. Not opened in full; abstract-level from search only.

### F4. Test-retest is necessary, not sufficient; reproducible judges can still be biased
- Source: https://arxiv.org/pdf/2606.19544 ("Reliability without Validity: A Systematic, Large-Scale Evaluation of LLM-as-a-Judge Models Across Agreement, Consistency, and Bias"). Found in search; not opened in full. Secondary report via https://kili-technology.com/blog/data-story-who-judges-the-judge-llm-as-a-judge (blog, not primary): two production judges scored at least 0.95 test-retest while showing strong position bias.
- Use: check reproducibility AND position/validity separately. A stable judge is not thereby a correct one.

### F5. Pairwise judging amplifies verbosity and authority bias; pointwise is less affected
- Source: https://arxiv.org/abs/2406.12319 ("The Comparative Trap: Pairwise Comparisons Amplifies Biased Preferences of LLM Evaluators", Jeong, Park, Hong, Lee, Choo; v4 April 2025). Licence: CC BY-SA 4.0.
- Claim: verbosity and authoritative tone are "exacerbated in pairwise evaluation"; pointwise is "less susceptible to such bias because each output is judged in isolation." Proposes PRePair (pointwise reasoning inside a pairwise frame), reported to improve on LLMBar. The page gives no numbers and names no models; the full paper is needed for those.
- Implication for BOAR: a pairwise "answer A vs answer B" judge will reward longer answers. BOAR answers are short and cited, so verbosity bias is less of a risk, but an authoritative-tone bias could favour confident wrong answers (28% of BOAR answers are confident errors).

### F6. Position bias in rubric-based judging: permutation averaging fixes most of it cheaply
- Source: https://arxiv.org/abs/2602.02219 ("Am I More Pointwise or Pairwise? Revealing Position Bias in Rubric-Based LLM-as-a-Judge", Xu, Hirasawa, Kozuno, Ushiku; Feb 2026). Licence: CC BY 4.0.
- Claim: bias is consistent across models and datasets, with model-specific direction ("some judges favor the first option, while others favor the last"). Bias can be attenuated by permuting rubric option order; "only a small number of random order permutations are sufficient to reduce the error" for most models; correlation with human annotations improved mainly for models with strong bias.
- The page gives no exact numbers and does not name the models. Full paper needed.
- Also related: the Zheng et al. MT-Bench paper (F9) and the "Comparative Trap" paper (F5) both report position effects, but no numbers were on the fetched pages.

### F7. Binary/checklist decomposition improves consistency across evaluators (CheckEval)
- Source: https://arxiv.org/abs/2403.18771 ("CheckEval: A reliable LLM-as-a-Judge framework for evaluating text generation using checklists", Yukyung Lee, Joonghoon Kim, Jaehee Kim, Hyowon Cho, Jaewook Kang, Pilsung Kang, Najoung Kim; v1 March 2024, EMNLP 2025 per the ACL Anthology entry). Licence: CC BY-NC-ND 4.0 (NC; cite only).
- Method: each criterion is split into sub-aspects, each turned into a yes/no question; the judge answers the Boolean checklist instead of giving a Likert score. The stated cause of inconsistency is subjective criteria combined with Likert scoring.
- Numbers from the abstract: average agreement across 12 evaluator models improves by 0.45; average correlation with human judgments improves by 0.10 (per search summary, verify in full). Variance reduction is stated without a number.
- Caveat: the checklist is built per task and its gain is measured by the authors' own setup, not on a 1.7B model.
- Implication for BOAR: this is the checklist-based evaluation the brief asks about. It maps directly to a per-key-point "does the answer contain fact X, and is it supported by the cited source" test, which gives binary, auditable items. Not yet measured against a small-model reader.

### F8. Coarse scales may correlate better with humans; binary alignment is strong (mixed evidence)
- Source for granularity effect: https://arxiv.org/abs/2601.08843 (Deng et al., Dec 2025). Found in search. Reported: Qwen 2.5-72B on SciEntsBank; alignment strong for binary tasks, degrading with rubric granularity. One model, one dataset. Not opened in full.
- Source for coarse scales: https://arxiv.org/pdf/2502.08489 (Salamandra technical report). It cites prior work suggesting coarse rubrics correlate with humans at least as well as per-level-described rubrics. The authors kept descriptors anyway for interpretability.
- Non-academic: MLflow article and tianpan.co blog both argue for binary pass/fail. Opinion-level; not used as evidence.
- Net: binary or 3-level judgments look at least as reliable as 1-5 for human agreement, but the direct controlled comparison was not found. Measure it on BOAR's own data (see recipe).

### F9. Strong judges reach human-level agreement, with position bias as a known limitation
- Source: https://arxiv.org/abs/2306.05685 (Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", v4). Licence: arXiv non-exclusive 1.0.
- Claim (abstract): GPT-4 achieves over 80% agreement with humans, "the same level of agreement between humans." Position bias is named as a limitation; the fetched page gave no swap-consistency number.
- Use: a baseline for what a judge can reach. It was measured on GPT-4 with pairwise comparisons, not on a 1-5 absolute score of a small model.

### F10. Judge error correction with human calibration labels: PPI and measurement-error estimators (load-bearing)
- Sources:
  - https://arxiv.org/abs/2511.21140 ("How to Correctly Report LLM-as-a-Judge Evaluations", Chungpa Lee, Thomas Zeng, Jongwon Jeong, Jy-yong Sohn, Kangwook Lee; submitted 2025-11-26, v4 2026-05-31, listed for ICML 2026). Licence: CC BY-SA 4.0. Proposes a plug-in correction for judge sensitivity and specificity, with confidence intervals that include uncertainty from both the test set and a human-labelled calibration set, plus an adaptive allocation of calibration samples. The page does not name the Rogan-Gladen estimator or give calibration sizes or CI numbers. v3 note (from search summary): existing PPI-style methods can be biased when test and calibration distributions differ.
  - https://arxiv.org/abs/2601.05420 ("Efficient Inference for Noisy LLM-as-a-Judge Evaluation", Yiqun T Chen, Sizhu Lu, Sijia Li, Moran Guo, Shengyi Li; Jan 2026). Licence: CC BY 4.0. Derives efficient-influence-function estimators that unify measurement-error correction (Rogan-Gladen style) with PPI. Claims PPI-style estimators have strictly smaller asymptotic variance under stated conditions. No numbers on the fetched page.
  - https://arxiv.org/pdf/2505.21972 ("LLMs Judging LLMs: A Simplex Perspective"; from search): PPI gave reliable intervals with good coverage with small labelled sets (5 to 10%), per the search summary; not opened.
  - Original PPI: Angelopoulos et al. 2023 (cited by the above; not opened).
- Implication: BOAR can estimate true correctness rates with CIs by hand-labelling a small calibration subset (for example 50 to 100 items, labelled by the human, not by Claude), then correcting the judge's sensitivity and specificity. Calibration size and the CI numbers still need to be taken from the full papers before we commit.

### F11. Power and sample size: paired designs and clustering change the answer (load-bearing)
- Sources:
  - https://tianpan.co/blog/2026/04/15/statistical-power-llm-evals (practitioner blog, not primary). Claim: resolving 82% vs 85% needs about 2,400 examples per variant at 80% power (two-proportion z-test, alpha 0.05); a 100-item suite has a minimum detectable effect of about 10 to 12 points. The formula ignores judge error.
  - https://icml.cc/virtual/2026/80066 ("Resolution Diagnostics for Paired LLM Evaluation", ICML 2026). From search summary only: shared-prompt comparisons should be treated as paired; the unpaired shortcut underestimates the required sample size by about 2x in close comparisons; many leaderboard pairwise rankings are unresolved at standard settings. Not opened; verify before quoting.
  - Clustering: one LLM-judgment paper (search summary, not opened) uses a design effect 1 + (m-1) ICC and gets an effective n of about 870 from 8,387 observations. Repeated judgments of the same item are not independent.
- Implication: BOAR's 37-item judge check is far too small to resolve a 0.05 gain on 1-5 scores. Use paired per-item differences (same questions for both arms), report the per-item SD of the difference, and size n from that. Judge flip noise adds to the variance and must be included.

### F12. Judge-noise-aware evaluation, concrete recipe (synthesis of F1, F10, F11)
- No single paper found that gives a full recipe for a small-model RAG benchmark with a noisy judge. The recipe below is assembled from the above and must be checked against the full papers.
  1. Test-retest first: re-judge a fixed set of N items (N about 40 to 100) K = 3 to 5 times with the same judge and settings, and record the flip rate per item. This is the number that decides how many judge repeats are needed.
  2. Use repeated judgments with majority or mean aggregation. F1 gives an empirical target: about 11 trials for pairwise verdicts; the number for absolute scores is not known and needs to be measured with step 1.
  3. Randomize or permute the order of compared answers and rubric options (F6). Check position bias by running both orders.
  4. Prefer binary or 3-level per-key-point checks (F7, F8) over a free 1-5 score, if the per-check agreement with a human labeller is at least as good (measure it).
  5. Calibrate with a human-labelled subset and correct sensitivity and specificity (F10) before quoting a headline number.
  6. Compare systems on the same items (paired), and size the set from the per-item SD of the difference (F11).
  7. Report judge family, settings and flip rate next to every number. Cross-family judge checks are needed (F1 limitation; F4).

## What this means for BOAR

- The 13-of-37 Haiku re-judge flip rate is in the same range as F1 (13.6% pairwise flip rate, 28% of questions above 20%). A single Haiku pass is not a measurement. Before any new arm is compared, run step 1 of F12 and log the flip rate in the QUEUE.
- Under this noise, the 1.7B vs 4B gap (-0.070, CI -0.094 to -0.044 at n 97, from the 10-16 notes) is a measured number only if the judge repeats and the calibration are in place. Treat the earlier small deltas (for example the 0.003 to 0.012 pack-add deltas) as below the noise floor until re-judged.
- The most useful new levers are (a) repeated judging with aggregation, (b) a small human-labelled calibration set with a sensitivity/specificity correction (F10), and (c) per-key-point binary checks (F7). None of these changes the model or the retrieval stack, so they do not reopen the closed prompt or packs lines.
- Watch out: several of these papers test OpenAI models only (F1, F2). The Claude judge family has not been tested in this literature. The XFAM result (non-Claude judge scoring higher by about 0.10) is consistent with judge-family offset, which means cross-family judge checks are required.
- Licence check: CheckEval and the temperature paper are CC BY-NC-ND. Cite them, do not copy text or figures into anything public.

## Searched, did not find or did not fully verify

- Direct controlled comparison of 1-5 Likert vs binary judge agreement with humans on the same items (found only indirect evidence: F7, F8).
- A 2025 (not 2026) paper on judge test-retest or repeated sampling; the search returned 2026 work for these topics.
- Exact calibration-set sizes and CI widths for the PPI / Rogan-Gladen estimators (F10 abstracts have none).
- Numeric position-bias swap-consistency for GPT-4 in MT-Bench (F9; the fetched abstract has none).
- Judge reliability studies for Claude or Haiku-family judges specifically.
- Judge-noise-aware power formulas (search summary of F11 says none explicitly model judge error).
- The full text of 2601.08843, 2502.08489, 2606.19544, 2505.21972, 2601.05420 (abstract-level only).

## Open items for a follow-up (not done)

- Open the full PDFs of 2606.13685 (tables for flip rates and vote counts), 2511.21140 (calibration sizes), 2406.12319 (PRePair numbers), 2602.02219 (permutation numbers) and the ICML 2026 paired resolution paper.
- A targeted search for "Claude judge test-retest" and "Haiku judge agreement" in 2026.
