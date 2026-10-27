# Verify: eval_judge (adversarial pass, 2026-10-12)

Scope: the 4 claim groups given to the verifier for `notes/eval_judge.md`. Method: full HTML text of each arXiv paper fetched with curl and grepped locally (no fetch summaries); competitor repos read through raw.githubusercontent.com and the GitHub REST API; our own aggregates read from `rnd/research/coordinator/arms/{seedvar,dt512}` and `boar-eval/scorers/vendor/eval-lib/judge-core.mjs`. Nothing under `blind/` or `rnd/veil/` was opened. No competitor question text was copied. 0 judge calls.

---

## Claim 1: GDPval (arXiv 2510.04374v1)

**Claim (notes):** "Headline metric = wins + ties vs human experts; best model 47.6 %; human–human agreement 71 %; automated grader agreement 66 %"; ties = 0.5; GPT-5 grader agrees less on OpenAI outputs.

**Evidence (https://arxiv.org/html/2510.04374v1):**
- §3.1: "47.6% of deliverables by Claude Opus 4.1 were graded as better than (wins) or as good as (ties)". The headline wins+ties figure is real. The model is Claude Opus 4.1, on the 220-task gold subset.
- §1, advantages list: "our primary metric is win rate". §A.2.1 defines the model win rate w as "rated better than the human deliverable". Wins+ties is the Figure 5 framing, while the cost model and the stated primary metric use wins only.
- §2.5: ties come from **human expert graders**. In blinded pairwise comparisons, experts "rank two or more unlabeled work deliverables". The automated grader does not decide them. §3.1: 3 samples × 3 human graders = 9 comparisons per prompt per model.
- §A.6.1: scores take values in {0, 0.5, 1} with "0.5 indicates a tie", and agreement = E[1 − |H − A|]. A tie against a win therefore counts as 0.5 agreement. This is not κ, and the paper says κ/α "are less directly applicable".
- §A.6.2: "average human-automated grader agreement was 65.7% and human inter-rater agreement was 70.8%". These are averages over 3 automated-grader sweeps, and 12 of the 220 tasks were excluded as ungradable (needs internet, non-Python code, fonts, audio).
- §A.6.2: the automated grader is "based on GPT-5-high" and agrees less on capable OpenAI outputs, which the authors tie to self-preference (Panickssery 2024).

**Verdict: corrected** (the numbers are confirmed; the description of the metric and who adjudicates ties needed fixing).

**Corrected claim:** On the 220-task gold subset, blinded **human expert** graders rated 47.6 % of Claude Opus 4.1 deliverables better than or as good as the expert deliverable. The paper's stated primary metric is win rate (wins only), and wins+ties is how Figure 5 is framed. Experts adjudicate ties. A separate GPT-5-high-based automated grader agrees with experts 65.7 % of the time (human–human 70.8 %), measured as mean 1 − |H − A| on {0, 0.5, 1} over 208 tasks. That grader's agreement drops on OpenAI outputs.

**Implication for BOAR:** judge.v1 pairwise already has a tie option ("Declare 'tie' when the answers are of practically equal quality", `bench/v0.2/plan/judge-core.judge.v1.mjs` l.72). A wins+ties rate can therefore be rescored at 0 calls from existing rows. One caveat: `combineOrders` turns AB/BA disagreement into a tie (l.93–95). That inflates ties compared with GDPval, where a grader actually judged "as good as". Report the two separately: ties where both orders said tie (GDPval-like), and ties from order disagreement. The GDPval agreement figures do not transfer to an LLM judge of our answers.

---

## Claim 2: same-family judge inflation (2502.01534, 2604.06996, 2609.17857)

### 2a. Preference Leakage (https://arxiv.org/html/2502.01534; arXiv API: v3 updated 2026-03-04, comment "Accepted by ICLR 2026")
- §4.1: generator/judge LLMs are **GPT-4o-2024-11-20, Gemini-1.5-flash and LLaMA-3.3-70B**. The students are Mistral-7B and Qwen-2.5-14B, fine-tuned (SFT) on 30k UltraFeedback prompts answered by each generator.
- §4.1: "two representative pairwise evaluation datasets, Arena-Hard … and AlpacaEval 2.0". The effect is measured **only pairwise**.
- Table 1: the metric is PLS, a **relative** win-rate inflation. Average PLS is 23.6 % / 27.9 % for the GPT-4o & Gemini pair, 16.4 % / 21.9 % for LLaMA & Gemini, and about 0 (−0.1 % / 1.7 %) for GPT-4o & LLaMA. It is not in rubric points.
- §5.2: "In the same series setting, the average preference leakage score is 8.9%", against 2.8 % for different series. By learning method (§5.3): SFT 23.6 %, DPO 5.2 %.
- The mechanism is a judge favouring a student **trained on its own synthetic data**. That is not the same as a judge scoring its own family's answers, which is classic self-preference.

### 2b. Self-Preference Bias in Rubric-Based Evaluation (https://arxiv.org/html/2604.06996; v3 2026-08-03)
- Abstract: on IFEval/LiveCodeBench, "judges can be more than 50% more likely to incorrectly mark them as satisfied". On HealthBench, "SPB skews model scores by up to 10 points".
- Judges: Gemma 3 (4B/12B/27B), Llama 4 Scout/Maverick, Qwen 3 (4B/30B/235B), GPT-oss-120B, GPT-5, **Claude 4.5 Sonnet and Haiku** (§3 setup).
- Table 1, rubric-level HSPP ratio (self), IFEval / LCB / HealthBench: **Claude-Sonnet 0.98 [0.64, 1.32] / 1.78 [1.58, 1.99] / 0.93 [0.86, 1.01]**; Claude-Haiku 1.15 / 1.71 / 0.90. The ">50 %" headline is driven by GPT-5 (LCB 20.15), GPT-oss-120B (5.97) and Qwen-4B (2.21). For Claude it holds on LiveCodeBench only.
- §4, Fig. 5: the "up to 10 points" is **Gemma-4B judging itself (10.90 on a ×100 scale)**. GPT-5 gives itself about 4 points. From the Fig. 5 matrix row, Claude-Sonnet self is **+1.52** and Claude-Haiku self **+0.96**. I did not check the per-cell CIs in Table 28.
- §3 heading: "Rubric-based evaluation is more robust than pairwise comparison, but not necessarily direct assessment". SPB "is significantly more severe in PWC than in RB and DA". **Claude was not run in DA or PWC** ("for cost purposes").

### 2c. Who Judges Matters (https://arxiv.org/html/2609.17857; v1 2026-09-15)
- Abstract: "four open-weight families (Llama 3.1, Qwen 2.5, Gemma 2, and Yi 1.5) in a fully crossed pairwise design with 9,312 judgments". No Claude or GPT. The models are GGUF Q4_K_M via llama-cpp-python.
- §2 (related work): "our judges never score their own outputs, so the relevant overlap is family-level".
- Table 1: global FPS 0.067 [0.053, 0.084], with corrected per-family values 0.034–0.084. The unit is **share of pairwise support** (≈ 6.7 pp), not rubric points. The naive row-wise statistic tracks Bradley–Terry ability at r = 0.95.
- §5: one judge sharing a family with one candidate "changes 18.5% of pairwise outcomes (Wilson 95% CI [16.4, 20.8])", measured against a family-balanced 4-judge panel.
- Sensitivity: across 72 specifications, FPS ranges 0.039–0.231. The AB/BA reversal rate is 55.4 % (Gemma 78.8 %).

**Verdict: corrected.**

**Corrected claim:** Preference leakage (ICLR 2026) is a pairwise-only effect: judges (GPT-4o, Gemini-1.5, LLaMA-3.3) favour students fine-tuned on their own outputs. PLS runs up to 28 % relative win-rate inflation, 8.9 % within the same series against 2.8 % across series. The rubric-SPB paper shows self-preference in binary-rubric grading, which is weaker than in pairwise and similar to direct assessment. Its headline magnitudes (> 1.5× false-pass, up to 10 HealthBench points) come from GPT-5, GPT-oss and Gemma-4B. **Claude 4.5 judges show 1.7–1.8× on LiveCodeBench, no significant inflation on IFEval/HealthBench rubrics, and about +1–1.5 HealthBench points.** The 0.067 family lift and the 18.5 % flip rate are pairwise results on four open families with no Claude.

**Implication for BOAR:** none of the three measures Opus as a 1–5 direct-assessment judge, so a published "Opus inflates the Opus reference by X" number does not exist. The best estimate for Claude-as-rubric-judge is small (≈ 1–2 points/100). The bias acts on our pairwise win-rate more than on the floor-adjusted ratio. Keep the caveat in the claim and spend a cross-family judge check on the pairwise/win-rate headline. Do not assume a large ratio correction.

---

## Claim 3: small-sample statistics (2609.35815 evalstats; 2411.00640 Miller) and n for Δ = 0.03

### Evidence
- **evalstats** (https://arxiv.org/html/2609.35815; v1 2026-09-20; package MIT per the repo LICENSE, while the `website/` folder is CC BY-NC-ND 4.0 and the GitHub API reports NOASSERTION):
  - §5: "bootstrap CI methods were overconfident nearly everywhere". On paired binary data, none reached nominal coverage even at N = 100. "We strongly advise against bootstrap CIs at N<100". The smooth bootstrap is the only variant that holds nominal coverage, but it grows conservative.
  - §A.2.2, pairwise single-run recommendations: **binary → Bonett-Price**; **continuous [0, 1] → logit-t**; **Likert → Bayesian NIG** (logit-t on the PPI path). For paired p-values, Wilcoxon and paired t keep good control (Table 6).
  - §3: a hard floor of N = 15, which also applies to the human labels under PPI. §6.1: `compare()` needs **≥ 50 judge-scored items** for PPI. **Human-label size: "25" is only the worked example** (BiGGen Bench, N = 80 per model, N_lab = 25; Fig. 1 caption). It is not a recommendation.
  - §6.3: gains begin at ρ² ≥ 0.4, where the judge is worth about 1.5× the human labels. Below about 0.2 the judge gives no usable gain. In Landis–Koch terms, aim for κ ≥ 0.61 between judge and human.
  - §6.2: κ = 0.81 "still gave an ≈37% false-positive rate" uncorrected.
  - Limitations: multi-run CI methods "not reported in this paper". PPI "cannot be combined with multi-run data".
- **Miller** (https://arxiv.org/html/2411.00640; v1 2024-11-01): CLT standard errors; bootstrap is treated as unnecessary when n is large (§2.1). Clustered SEs (§2.2). Resampling K answers per question (§3.1). Paired differences recommended (§4.2). Power, eq. 9: n = (z_{α/2} + z_β)²(ω² + σ²_A/K_A + σ²_B/K_B)/δ². Worked example: δ = 0.03, ω² = 1/9 gives n ≈ 969. Miller gives no small-n rule.
- **Our harness:** `judge-core.mjs` l.111–121 is a **percentile bootstrap** (2,000 resamples) used at n = 51 (V-para) and n = 110. SEEDVAR/DT512 CIs come from it, which is exactly the regime evalstats flags.

### Per-item SDs back-solved from our own V-para CIs (n = 51, Opus, raw ratio scale; bootstrap SE = half-width/1.96, SD = SE·√51)
| source | CI | implied per-item SD |
|---|---|---|
| deep+think 512 vs deep no-think, s42 (DT512.md l.31) | +0.027…+0.119 | **0.168** |
| same, s43 | +0.060…+0.143 | 0.151 |
| seed vs seed, same config (SEEDVAR, 3 pairs) | hw 0.027–0.036 | 0.100–0.131 (seed noise alone) |
| 512 vs 1024 (shares first 512 thinking tokens), s42 | −0.003…+0.033 | 0.066 (correlated arms) |
| single-run floor-adj level, s42 | 0.375–0.450 | 0.137 |
| run-level seed SD 0.020 raw / 0.025 floor (SEEDVAR) ×√51 | — | 0.14 / 0.18 if the seed noise were item-independent |

Because evalstats finds bootstrap intervals overconfident at n < 100, these SDs are lower bounds.

### n to detect Δ = 0.03 (paired, 80 % power, α = 0.05); n = k·s_d²/δ², k = 7.849 two-sided / 6.183 one-sided
| assumed per-item paired SD s_d | two-sided n | one-sided n |
|---|---|---|
| 0.094 (notes; back-solved from v0.2 MDE) | 78 | 61 |
| 0.12 (seed-noise scale) | 126 | 99 |
| 0.136 (deep arm change, **2 seeds per arm**) | 162 | 128 |
| 0.15 | 197 | 155 |
| 0.168 (deep arm change, 1 seed) | 247 | 194 |
| **0.20 (task default σ_item)** | **349** | **275** |

The two-seed row models s_d² = ω² + 2σ²_seed/K, with ω² ≈ 0.0112 (between-arm item variance) and σ²_seed ≈ 0.0072 per arm (from the seed-vs-seed SD 0.12). With K = 3 seeds, s_d is about 0.126, so n ≈ 140 two-sided / 110 one-sided.

**Absolute claim (mean > 0.50):** with σ = 0.18, true value 0.53 and 80 % power one-sided, n ≈ 223 (σ = 0.20 → 275). At n = 110 the one-sided 95 % margin is ±0.028 (σ 0.18) to ±0.031 (σ 0.20). The point estimate must therefore be ≥ about 0.53 just to reach significance, and that holds only at a 50 % chance if the truth is 0.53.

**Verdict: corrected.** The CI guidance is confirmed. "PPI with about 25 human labels" is an example, not a rule; the floor is 15 labels plus ≥ 50 judge items. The notes' n ≈ 77 for Δ 0.03 assumes s_d 0.094, the v0.2 4B scale. Deep-tier arms on V-para imply s_d 0.15–0.17, which means n ≈ 200–250 two-sided per seed.

**Implication for BOAR:** v0.3 at n ≈ 110 can resolve Δ = 0.03 arm decisions only for low-variance (4B-like) arms. Deep/thinking arms need about 2–3 seeds plus one-sided frozen criteria, or n ≈ 160–250. For the >0.50 headline, n = 110 gives a coin flip at a true 0.53. Swap the percentile bootstrap for logit-t (continuous per-item scores) and Bonett-Price (win/tie binaries) as a 0-call sensitivity check. If a human spot-check is ever added, ≥ 15 labels (25 is the published example) with ρ² ≥ 0.4 is the bar for PPI. Note that evalstats PPI does not support our multi-seed design.

---

## Claim 4: competitors' [competitor score removed] / [competitor score removed] protocols

**Evidence:**
- a competitor team `docs/BENCHMARK.md` ([competitor link removed]; commit 0c29266f, 2026-10-07; repo MIT per the GitHub API):
  - Summary table: 0.8.4, Qwen3.6-35B-A3B 2-bit, **54 %**; 0.7.2 45 %; 0.7.0 4B 34 %; the first run (0.6.0, 4B) 26 %.
  - Grading: "blind pairs in random order, three graders (restaurants, crypto, the rest), each a separate Claude instance … used web search to check facts". Scores 0–10. The share is the app's total divided by the reference's total, i.e. a ratio of sums, which equals the ratio of means at fixed n = 61. **The Claude model version of the graders is not stated.**
  - 0.8.4 run: "three fresh grader instances given word for word the instructions". "The graders were language-model instances that checked a sample of facts on the web". Reference preferred 0/61/0. The answers came from an 8 GB Redmi, not a 12 GB phone.
  - Own caveat: "graders can differ by ten". The questions were used to fix faults. `heldout40` has not been run.
  - `bench/README.md`: the reference is "Claude Opus 5.5 answering with web search", taken from a competitor team `eval/answers_web_vitalik.jsonl` at 0edb11f (Apache-2.0). The questions are boar-app eval set v2 (MIT): 20 restaurants, 20 crypto, 10 travel facts, 5 emergencies, 6 arithmetic.
- a competitor team (repo licence **Apache-2.0** per the GitHub API, not MIT as the notes say):
  - `notes/2026-09-28-vitalik-bar.md`: reference "Claude (Opus 5.5) with web search", citing 3.5 pages on average. Three graders, "each a separate Claude instance", using web search, 0–10 scores, share = app total / reference total. Result **64 %**, reference preferred 61/61. The note itself says graders and reference "are the same model family". **Grader model version not stated.**
  - `notes/2026-10-01-vitalik-bar-121.md` (commit 99413f9b, 2026-10-02): a 3-way same-sitting grading scored **65 %** (9/28 build 53 %). In that sitting "the web search quota had run out for all three graders", so they fetched pages directly. Pairs against the reference gave **62 %**, with the restaurant grader having web search for "part of its checks". The 44 closed places / 86 errors figure is confirmed. "Two graders gave the same 9/28 restaurant answers 68% and 46%", a 10–20 pt spread between graders, measured on the restaurant group only.

**Verdict: corrected.**

**Corrected claim:** Both report a share = app total / reference total of 0–10 scores (= ratio of means, n = 61, no floor adjustment). The scores come from three blind pairwise Claude grader instances, one per group (20/20/21 items). The grader model version is unstated in both, and the reference is Claude Opus 5.5 + web. Web checking was not uniform. a competitor team 1.2.1's same-sitting graders had **no web search** (quota exhausted; they fetched pages directly), and its pair grader had it only partly. a competitor team 0.8.4's graders checked "a sample of facts" on the web. Figures: a competitor team [competitor score removed] (35B 2-bit on an 8 GB phone); a competitor team [competitor score removed] (9/28), [competitor score removed] pairs / [competitor score removed] 3-way same-sitting (1.2.1). a competitor team's licence is Apache-2.0, not MIT. The questions themselves are MIT, from boar-app v2.

**Implication for BOAR:** the competitors' numbers are ratio-of-sums on a 0–10 single score, without a floor and with Claude graders of unknown version whose web use varied. They are not comparable to our floor-adjusted 1–5×3 judge.v1. The only meaningful cross-app number would be a single-sitting regrade of all three apps' published answers by one grader configuration. Its 10–20 pt grader spread is larger than the headline gaps between the apps. Eval-side use of their published answers remains subject to coordinator sign-off. Apache-2.0 on a competitor team's reference file requires attribution if it is redistributed.

---

## Reconciliations
1. **"judge.v1 pairwise has no tie-by-adequacy option" (notes Q1 action) vs the notes' UNKNOWN list.** Settled: judge.v1 **does** allow ties (`judge-core.judge.v1.mjs` l.57 enum A/B/tie; l.72 "Declare 'tie' when … practically equal quality"). A wins+ties rescore is 0 calls. Order-disagreement ties (l.93–95) must be reported separately to match GDPval's semantics.
2. **"GDPval headline = wins+ties" vs "primary metric is win rate".** Both phrasings are in the paper. The wins+ties 47.6 % is the Figure 5 / §3.1 framing, while §1 and §A.2.1 call win rate (wins only) primary. Ties come from human experts, not the automated grader.
3. **"HealthBench skew up to 10 points" applied to our Opus judge.** That maximum is Gemma-4B self-grading. Claude 4.5 Sonnet is about +1.5 points and Haiku about +1.0, and Claude's IFEval/HealthBench HSPP is not significant. The bias for a Claude rubric judge is small. Claude was never tested as a direct-assessment judge, which is judge.v1's mode.
4. **"One same-family judge flips 18.5 % of outcomes".** This is a pairwise result for a 4-judge open-family panel against a family-balanced reference, and it does not transfer to a single-judge 1–5 rubric.
5. **n for Δ 0.03.** The notes' n ≈ 77 holds for s_d 0.094 (v0.2/4B). Deep-tier V-para arms back-solve to s_d 0.15–0.17 per seed, even from bootstrap CIs that evalstats says are overconfident at n < 100. The planning number is n ≈ 160 two-sided with 2 seeds, and about 350 under the σ_item = 0.2 default.
6. **"evalstats recommends about 25 human labels".** 25 is the worked example. The rule is a floor of 15 labels, ≥ 50 judge-scored items for PPI and ρ² ≥ 0.4.
7. **a competitor team licence.** The notes say MIT; the GitHub API and a competitor team's attribution both say Apache-2.0. MIT applies to a competitor team's repo and to the boar-app v2 question set.
