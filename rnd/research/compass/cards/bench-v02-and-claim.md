# Bench v0.2 design and the claim framing (Summit front F3)
TL;DR: to reach a CI half-width ≤ 0.035 the ratio needs ~120 judged items. 110 new blind items alone give ±0.037; v0.1 + 110 new (~167 judged) gives ±0.030. Seeds don't help: a 3rd run changes the half-width by < 0.001. The floor is higher than assumed: a declined answer scores 1.50/5, so an **always-decline system already scores 0.31** on the raw ratio. Today's 4B at 0.512 is 0.39 above the rubric minimum and 0.30 above always-decline. A draft pre-registered analysis plan is ready for freezing.
Lane: Compass · Status: **plan FROZEN** (boar-eval 799f1c9, `bench/v0.2/plan/`: analysis-plan.md 697b4327…, item-spec e1c0943c…, floor_metrics.py fe7c70b7…, paired_gap.py 85310635…, strata.py 1d5324ff…, judge.v1 judge-core; combined sha256 fe100e91…855e). Items being written blind (2 writers); Compass never reads them · Priority: A
Axes moved: stability (the CI the claim rests on) and the honesty of the headline. No product change.
Fits BOAR? Eval-side. Judge cost ≈ 110 items × 2 orders × 2–3 seeds ≈ 440–660 calls per system ([usage detail removed]).
Evidence:
- **Power (Compass, `exp/bench-v02/power.py`):** two-level bootstrap on Android Qwen3-4B `and-qwen` s42/s43 (57 judged items, ratio 0.512, ref mean 4.90). Half-width by number of judged items:

  | judged items | 2 runs | 3 runs |
  |---|---|---|
  | 57 | 0.052 | 0.052 |
  | 100 | 0.039 | 0.039 |
  | 120 | **0.035** | 0.035 |
  | 150 | 0.032 | 0.032 |
  | 200 | 0.029 | 0.028 |

  This reproduces Summit's scaling (±0.051 at 57). The projection assumes new items behave like v0.1's; if v0.2's items are more heterogeneous, the half-width is wider.
- **Floor (Compass, `exp/bench-v02/floor.py`):** 79 judged *declined* answers across 7 night runs (iPhone 1.5B, Android Qwen3-4B, Gemma E4B):
  - mean rubric **1.50/5**: correctness **2.40** (a decline asserts nothing false), completeness 1.05, usefulness 1.04;
  - answered: 2.39; reference: 4.90;
  - **always-decline system ratio ≈ 0.306**.
  - Summit's "blank ≈ 0.20" is the rubric minimum (1/4.9). Declines score above it because of correctness.

  | System | raw ratio | floor = rubric min (Σ(S−1)/Σ(R−1)) | gain over always-decline ((r − 0.306)/(1 − 0.306)) |
  |---|---|---|---|
  | Android Qwen3-4B | 0.512 | 0.387 | 0.297 |
  | Android Gemma E4B | 0.496 | 0.367 | 0.274 |
  | iPhone Qwen2.5-1.5B | 0.379 | 0.219 | 0.104 |

- Judge facts already measured (cards [judge-reliability-run-budget](judge-reliability-run-budget.md), [gate-new-cw-jev](gate-new-cw-jev.md)):
  - position bias cancels with both orders;
  - judge-only noise is 2–9 % of run variance;
  - the judge doesn't reward padding (persona arm);
  - cw/fail is its weakest boundary.
Test in boar-eval: E3 as in the Summit memo, with the plan in `exp/bench-v02/analysis-plan.draft.md`:
- **v0.2-new** = 110 items, mix declared before writing (mirrors v0.1's judged mix: explanation 21, reasoning 21, comparison 13, crypto 13, honesty-refusal 12, health 8, danger 10, synthesis 6, travel-practical 4, travel-local 2), English, no venue lists, no answers that can change before Oct 31;
- **v0.2** = v0.1 public + v0.2-new;
- items + references + judge prompt + analysis plan + scripts under one combined sha256, committed publicly before any run.
- **E3 expectation (stated now):**
  - all-v0.2 half-width ≈ 0.030 (passes ≤ 0.035);
  - held-out ratio: the band ±0.04 is about one held-out CI half-width (0.037), so the check can only flag shifts beyond sampling noise.
  - My prior is that Veil's fresh items are somewhat harder than v0.1 for BOAR, because v0.1's items have been studied for weeks (arms tuned on them). Expect the held-out ratio a little under 0.512 (0.47–0.51). K5 (< 0.48) is a real possibility, not a tail.
Cost to try: Veil 1–2 days for 110 items; references ~110 Opus+web calls; E3 run 2 seeds × 110 × 2 orders ≈ 440 judge calls.

## Body

### K1 fired (#17 G1+ failed its replay; coordinator, 2026-10-02): the claim goes to Summit's FALLBACK framing
- With the knowledge front closed, no measured lever moves the Android ratio meaningfully before Oct 31. Expect the claim's point estimate near today's 0.51 (or the held-out level, if K5 bites).
- **Expected v0.2 interval:** ±0.026 (stratified) to ±0.030 (plain) around ~0.51 → roughly **0.48–0.54, which contains 0.50**. That is Summit's fallback sentence: "point estimate X, 95 % CI a–b, which includes 0.50; a 1.5B model on the same bench scores 0.38 with a disjoint interval".
- **What v0.2 still buys under the fallback:**
  - (a) a credible held-out number instead of a number on a set tuned for weeks;
  - (b) a tight enough CI that the "disjoint from the 1.5B" statement holds on all three scales;
  - (c) a public hash commitment.
  - On v0.1 today (stratified), raw 4B 0.466–0.558 vs 1.5B ~0.35–0.41: disjoint on raw. Also check above_min and above_decl once both runs exist on v0.2.
- **Measured now on v0.1 (stratified two-level bootstrap; `exp/bench-v02/paired_gap.py`, `floor_metrics.py`):** Android Qwen3-4B vs iPhone 1.5B, same 57 items:

  | scale | 4B | 1.5B | **paired gap 4B − 1.5B (95 % CI)** |
  |---|---|---|---|
  | raw | 0.512 (0.466–0.558) | 0.381 (0.350–0.414) | **+0.131 (+0.095 … +0.171)** |
  | rubric min removed | 0.387 (0.330–0.444) | 0.222 (0.183–0.263) | **+0.165 (+0.120 … +0.215)** |
  | above always-decline | 0.297 (0.231–0.363) | 0.108 (0.063–0.156) | **+0.189 (+0.137 … +0.246)** |

  Gemma E4B: 0.496 / 0.367 / 0.274. The "a 1B-class model fails" half of the fallback sentence already holds on all three scales, and the paired gap is the stronger way to say it. The gap *grows* on the floor-aware scales, because much of the 1.5B's raw score is the decline floor. Recompute on v0.2 for the claim.
- **Honesty point for the write-up:** with a CI that contains 0.50, the claim is "consistent with the bar, not shown above it". Say so in the first paragraph, not in a footnote.

### Claim framing: DECIDED by r4to (2026-10-02 morning)
- **The bar is on the RAW ratio.** Every publication shows raw + floor-removed (rubric minimum) + above-always-decline **side by side**.
- The analysis plan's secondary metric 2 (a, b) therefore becomes a mandatory companion in every published table, not optional.

### Claim framing (recommendation, kept for the record)
- **Headline the pre-registered raw ratio** (changing the primary after seeing data is worse than its flaw). Put the floor-aware readings in the **same table, same size**, with one-line definitions:
  - "Raw ratio (pre-registered): 0.51 (95 % CI a–b)."
  - "With the rubric's minimum score removed: 0.39."
  - "Above a system that declines every question (which scores 0.31): 0.30."
- **Say it in words:** "The judge gives a polite 'I don't know' 31 % of the reference's score, so 50 % on this scale means BOAR's answers carry roughly 30–40 % of the reference's added value." That's the honest reading of ">50 % as good". r4to should decide before the claim whether the bounty's "50 %" is read on the raw scale (Summit's open question). No measured lever moves the floor-aware numbers to 0.5 in 29 days.
- **Always report alongside:**
  - win/tie/loss (today 2/2/96 %), share judged correct (39 %);
  - the 1.5B baseline on the same items (raw 0.38; floor-aware 0.22 / 0.10). This is the "a 1B model fails" evidence the bounty asks for, and the gap is larger on the floor-aware scales.
- **Claude judging Claude:** the cross-family re-score and the 40 human labels (plan items 5–6) are what make the number trustworthy to outsiders. Pre-register the "headline the lower one if they differ by > 0.05" rule now, as Summit proposes.

### Stratified CI and the category mix (`exp/bench-v02/strata.py`)
- Android 4B per-category ratio on v0.1 (2 runs): comparison 0.591, honesty-refusal 0.639, health 0.550, explanation 0.539, reasoning 0.538, synthesis 0.457, danger 0.423, travel 0.408, **crypto 0.356**. The mix moves the headline by a few points: an explanation/comparison/synthesis/reasoning-only mix (the bounty's four types) would read ~0.54.
- Since v0.2 fixes per-category quotas, a **stratified** bootstrap is the design-consistent CI. On v0.1 it gives 0.045 vs 0.052 plain, **−13 % width for free**. At ~167 items that's ≈ 0.026. Declared in the plan draft before any v0.2 data, so it isn't a post-hoc choice.

- **D is robust to the mix** (`decline_by_cat.py`): the always-decline floor per category is reasoning 0.25, explanation 0.28, synthesis 0.30, travel 0.30, comparison 0.31, crypto 0.32, health 0.32, honesty-refusal **0.44** (a decline is often the right answer there). Weighted by v0.2-new's declared mix it's 0.307 ≈ 0.306.

### Item-writing spec (`exp/bench-v02/item-spec.draft.md`, for Veil after approval)
- Reuses v0.1's method. Additions:
  - rubric bullets that name specific wrong answers (the judge uses them);
  - explicit decline rules on honesty-refusal items (the floor is highest there);
  - context-dependent danger items (earthquake on a coast vs indoors);
  - a phrasing mix (first-person / direct / imperative);
  - optionally two blind writers to expose writer-style bias;
  - Jaccard ≤ 0.30 + bge cosine < 0.90 similarity gates;
  - no post-freeze drops except factual errors in the gold answer.

### Cross-family judge and human labels (protocol in the plan, items 5–6)
- **Why not more Claude raters:** correlated judges add few effective votes ("Nine Judges, Two Effective Votes", arXiv 2605.29800, 2026). Veil's 3-Opus panel (Fleiss κ 0.92) is closer to one vote than three. Self-preference in LLM judges is tied to low-perplexity text (Wataoka et al., arXiv 2410.21819). With an Opus-written reference and an Opus judge, any self-preference favors the reference, i.e. works against BOAR. One judge from another family plus a small human set is the cheapest real check.
- **Available now:** the Vercel AI Gateway (already used for Jev) lists 406 models, including `openai/gpt-5.5` ([usage detail removed] / 30 per M tokens) and Google Gemini models (public `/v1/models` listing, 2026-10-02). A judge call (~3k in, ~300 out) costs [usage detail removed]–0.03: [usage detail removed] for a pilot on v0.1's `and-qwen-s42`, [usage detail removed] for the v0.2 claim run (≈ 170 items × 2 orders × 3 seeds). Spend is the coordinator's/r4to's call.
- **HELD for r4to (coordinator, 2026-10-02):** a gateway judge is a paid external call, and the private Opus reference text would leave the machine (Veil's legal note). I missed the second point when proposing it. **Option that keeps references local:** an open-weights judge from another family run on the MacBook (e.g. a Gemma-4-31B or Qwen3-32B-class GGUF, ~20 GB, so a download above the 1 GB limit that needs approval). It's slower and weaker than a frontier judge, but no text leaves the machine. Its agreement with judge.v1 must be measured before it counts. UNKNOWN whether a 30B-class judge is good enough; Thakur et al. found mid-size judges far less aligned than the best ones.
- **Pilot first, on the development set:** if the other family's ratio differs by > 0.05 from judge.v1 on v0.1, the claim's framing needs that before v0.2 is spent.
- **Floor metrics script:** `exp/bench-v02/floor_metrics.py` reproduces the report: raw 0.512 (0.458–0.561); rubric-min-removed 0.387 (0.319–0.448); above always-decline 0.297 (0.218–0.367) on `and-qwen` s42/s43. Freeze it with the plan.

### What would make it fail
- Category mix drift: if Veil's items skew to synthesis or comparison (BOAR's weakest), the held-out ratio drops for reasons unrelated to generalization. The declared mix prevents that; report the per-category table.
- Leakage: anyone who sees v0.2-new items or per-item outputs before the claim run can tune toward them, Compass included. Only aggregates may leave the coordinator, as with crisis1.
- Reference drift: a web-dependent reference generated on a different day for the new items vs v0.1. Pin the recipe and generation window; time-sensitive facts pinned "as of 2026-09".

### Not in scope
Detector work (stopped per Summit); PT items (parked); venue-list items (scored by OSM, outside the ratio).
