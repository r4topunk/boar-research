# Judge reliability and the run budget for arm decisions (Claude judging Claude)
TL;DR: on tonight's boar-eval judgments, the Opus pairwise judge is not the noise problem: judge-only noise is 2–9 % of run-to-run variance. The answer-slot bias (+0.11 for BOAR's answer in slot A) cancels because both orders are judged. What decides is generation noise: 2 runs × 60 items can only detect Δratio ≈ 0.038, so a 0.03 effect needs 3 × 60 or 2 × 120. The judge's weak spot is the cw/fail boundary (3/20 hand disagreements), which the −9 penalty magnifies.
Lane: Compass · Status: tested (QUEUE #7: seed-44 |Δratio| 0.006 ≤ 0.04 predicted; σ²_run 0.253 vs 0.255; two-level bootstrap + MDE in harness/diff.py 54780e3; rule adopted) · Priority: A
Axes moved: **stability** (decisions stop being coin flips), indirectly every axis an arm claims to move. No product change.
Fits BOAR? Eval-side only: no device and no engine change. Cost is judge calls on the [usage detail removed] (~1.2 s/min rate; ~114 calls per 60-item run, both orders).
Evidence:
- **Local analysis (Compass, 2026-10-01, `exp/judge/judge_rel.py`, read-only over `boar-eval/runs/night-2026-10-01/ios-main-s4{2,3}.{traces,judgments}.jsonl`; judge.v1 = claude-opus-5-5 pairwise vs the frozen Opus+web reference, both A/B orders, engine 0cfd4a77, Qwen2.5-1.5B, temp 0.7, seeds 42/43):**

  | Measure | Value | Reading |
  |---|---|---|
  | Winner agreement across the two orders | 113/113 | no flips, but BOAR almost always loses to the reference, so this is an easy case |
  | BOAR mean rubric when in slot A − slot B (paired, 113 pairs) | **+0.112** (sd 0.32, t ≈ 3.7) | real first-slot bias on the weaker answer; reference: +0.012 |
  | Same BOAR text in both seeds (23 items, 21 are declines): score diff | sd 0.22, nonzero 43 % | judge-only noise |
  | Reference text (fixed) re-scored across seeds | sd 0.11, nonzero 16 % | judge-only noise on a substantive answer |
  | Per-item, per-run variance of BOAR's score | total 0.260 vs judge-only 0.006–0.024 | **judge ≈ 2–9 % of run-to-run noise; generation ≈ 91–98 %** |
  | Length check (21 items answered in both seeds with different texts) | longer answer scored higher in 9/18 | no length bias detected (weak test) |
  | Ratio on the 56 common items | s42 0.374 / s43 0.384 | consistent with SE ≈ 0.019 per run |

- **Judge vs hand labels (existing, `rnd/bench/calibration/comparison.json`, Plumb, 20 items):** 15/20 exact, **18/20 on pass vs not-pass**. Disagreements: fail↔cw 3 (2 judge-cw/hand-fail, 1 the reverse) and pass→fail 2 (the judge is stricter). The truthfulness axis's −9 lives exactly on the boundary the judge gets wrong most often. r4to's own sheet (`human-v0/labels.r4to.json`) is still empty.
- **Literature (all accessed 2026-10-01):**
  - position bias in LLM judges, fixed by evaluating both orders: Wang et al., "Large Language Models are not Fair Evaluators", arXiv 2305.17926 (https://arxiv.org/abs/2305.17926); Zheng et al., MT-Bench / Chatbot Arena, arXiv 2306.05685, which also documents verbosity and self-enhancement bias (https://arxiv.org/abs/2306.05685);
  - self-preference: LLM evaluators recognize and favor their own generations, Panickssery et al., arXiv 2404.13076 (https://arxiv.org/abs/2404.13076). Here the reference is Opus-written and the judge is Opus, so the bias would lower BOAR's ratio. That is conservative for the 0.50 bar but UNKNOWN in size;
  - judge-agreement data to calibrate against, if ever needed: `lmsys/mt_bench_human_judgments` (CC BY 4.0), `ScalerLab/JudgeBench` (MIT, arXiv 2410.12784).
Test in boar-eval:
- **Decision rule (proposed for QUEUE, adopt before the next arm pair):**
  1. Every arm decision on quality uses **≥ 3 runs per arm on 60 items, or 2 runs on ≥ 120 items**, same seeds across arms (seeds 42/43/44).
  2. Report the paired per-item Δ with a **two-level bootstrap**: resample items, and within each item resample runs. A plain item bootstrap of one run per arm understates the CI; this is why the night's Δ CIs were "too narrow".
  3. **Pre-state the MDE.** If the claimed effect is below the MDE for the chosen k × n (table below), the arm can't be decided on quality. Decide on gate or safety axes, or don't run it.
  4. Keep both judge orders: dropping one to halve cost re-introduces the +0.11 slot bias.
  5. For truthfulness **cw on danger items**, keep the second rater (Jev band already exists), and add a hand check of every judge-cw/fail call on a danger item: ≤ 5 per run, minutes of work.
- **MDE table** (80 % power, α = 0.05, measured per-item variance 0.26, reference mean rubric ~4.2):

  | runs/arm | 60 items | 120 items |
  |---|---|---|
  | 1 | 0.053 | 0.038 |
  | 2 | 0.038 | 0.027 |
  | 3 | **0.031** | 0.022 |
  | 5 | 0.024 | 0.017 |

- **Validation (cheap, falsifiable):** one more `main` run at seed 44 (same config). Prediction stated now: |ratio(s44) − mean(s42, s43)| ≤ 0.04 (≈ 2 SE). The per-item variance estimated from s42 vs s44 and s43 vs s44 will be 0.26 ± 0.08. If it is > 0.4, the MDE table is optimistic: redo with three runs.
Cost to try: the rule is free. The validation is 1 run + ~114 judge calls (~20 min). A 3-run arm pair is ~3 × 2 × 20 min of judge time per decision.

## Body

### What it means for tonight's decisions
- An arm whose claimed quality effect is < 0.04 can't be decided from 2 runs per arm on bench 60, even if the CI from one run looks clean. The retest (Δ 0.031 between identical runs) sits right at 1.6 SE of a single run.
- Re-judging the same traces (more judge seeds, a judge panel) buys almost nothing for quality: ≤ 9 % of the variance is the judge. Budget goes to **more generation runs and more items**.
- The judge does matter on **labels at the cw boundary**. A judge-cw on a danger item is −9, and the judge's cw/fail calls disagree with Plumb in 3/20. That's where human or second-rater time pays.

### Assumptions and gaps
- The judge-noise estimate leans on declines (21/23 identical texts) and on the fixed reference. Judge noise on long substantive BOAR answers may be higher (UNKNOWN; a direct test is to re-judge one run's traces with `--seed 8` and compare, at 114 calls).
- The MDE uses a linearized ratio with items as fixed, and treats per-item noise as independent of the arm. Arms that change many items at once (a new reader model) have extra item × arm variance, which makes the MDE larger.
- Self-preference toward the Opus reference: UNKNOWN size. A cross-family judge on a 20-item sample would bound it, but it is an external service and not my call.
- Off-the-shelf: `IINemo/lm-polygraph` (MIT, uncertainty estimation for LLMs) and `scikit-learn-contrib/MAPIE` (BSD-3, conformal prediction) are on the shelf. Conformal abstention thresholds are a later card (selective prediction).
