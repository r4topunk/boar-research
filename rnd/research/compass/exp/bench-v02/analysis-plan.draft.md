# Bench v0.2 analysis plan (DRAFT by Compass, to be frozen by the coordinator with the items + references + judge prompt under one sha256)

## Sets
- **v0.2-new:** 110 new public items written blind by Veil (category mix below, declared before writing). All judgeable by the pairwise judge; no venue-list items.
- **v0.2 = v0.1 public (60) + v0.2-new (110).** The ratio uses judged items only (v0.1 venue items are scored by OSM, not the judge).
- **Held-out subset = v0.2-new.** No arm decision is ever taken on it (Summit rule). v0.1 stays the development set.

## Category mix of v0.2-new (declared before writing; mirrors v0.1's judged mix ×1.93 so E3 compares like with like)
explanation 21 · reasoning 21 · comparison 13 · crypto 13 · honesty-refusal 12 · health (non-danger) 8 · danger + danger-situation 10 · synthesis 6 · travel-practical 4 · travel-local 2 = **110**.
- English only, like v0.1's public split (PT is parked).
- No question whose answer can change before 2026-10-31. If a question is time-sensitive, it pins "as of 2026-09".

## References and judge (unchanged recipe)
- References: `reference.v1` recipe (Opus 5.5 + web, prompt sha `d5144343…`), generated once, frozen. Missing references are regenerated before the freeze, never after.
- Judge: `judge.v1` (claude-opus-5-5, pairwise vs the reference, both A/B orders, scores averaged, disagreement = tie).

## Primary metric (pre-registered)
- **Quality ratio on all v0.2 judged items** = Σ mean-rubric(BOAR) / Σ mean-rubric(ref), with a **two-level bootstrap** (items, then runs within item; 2,000 resamples; seed 11). Seeds 42/43/44 for the claim run.
- **CI method: stratified two-level bootstrap.** Resample items *within each declared category* (the quotas are fixed by design), then runs within item. The plain two-level bootstrap is reported beside it. Justification: with category quotas fixed before writing, between-category sampling variance isn't part of the design. On v0.1 (Android 4B, 2 runs) stratifying narrows the half-width from 0.052 to **0.045** (`exp/bench-v02/strata.py`). The choice is declared here, before any v0.2 data.
- Expected half-width at ~167 judged items: **≈ 0.030 plain, ≈ 0.026 stratified** (Compass projection from `and-qwen` s42/s43; `exp/bench-v02/power.py`, `strata.py`).
- Category labels for v0.1 items (for stratification of the combined set): as in `questions.public.jsonl`, with danger-situation → danger and travel-local/travel-practical → travel.

## Decided framing (r4to, 2026-10-02)
The bar (> 0.50) is judged on the **raw** ratio. Every publication shows, side by side: raw, rubric-minimum-removed, and above-always-decline (D = 0.306), each with its CI.

## Secondary metrics (reported next to the primary, never instead of it)
1. **Held-out ratio (v0.2-new only)**, same method. Expected half-width ≈ 0.037 at ~110 items.
2. **Floor-aware readings of the same judgments:**
   - (a) ratio with the rubric minimum removed: Σ(S − 1)/Σ(R − 1);
   - (b) gain over an always-decline system: (ratio − D)/(1 − D), with **D fixed now at 0.306** (mean judge rubric of 79 declined answers across 7 night-2026-10-01 runs ÷ mean reference rubric; `exp/bench-v02/floor.py`). The D measured on the claim run is reported beside it. Robustness: per-category D ranges 0.25 (reasoning) to 0.44 (honesty-refusal, where declining is often correct), and weighted by the declared v0.2-new mix it is 0.307 (`decline_by_cat.py`), so the fixed 0.306 doesn't depend on the mix.
   - Reference implementation: `exp/bench-v02/floor_metrics.py` (two-level bootstrap, seed 11, 2,000 resamples) to be frozen with this plan.
3. Win / tie / loss vs the reference; share of items judged correct (correctness ≥ 4).
4. Truthfulness, safety and the other axes as in boar-eval's 7-axis report (never averaged).
5. **Cross-family judge:** the final device run re-scored once by a judge from another model family, with the same `judge.v1` system prompt, schema, pairs and both orders. If its ratio differs by > 0.05, headline the lower one.
   - Judge: `openai/gpt-5.5` via the Vercel AI Gateway (already used for Jev), temperature 0, JSON schema = judge-core's VERDICT_SCHEMA. Name it in the frozen plan; no swapping after seeing scores.
   - **Pilot now on the development set, not on v0.2:** re-judge `and-qwen-s42` (57 items × 2 orders = 114 calls, [usage detail removed] at list price). If Δratio > 0.05 vs judge.v1, the claim framing changes before any v0.2 run.
   - Report Cohen's κ on pass/not-pass labels between the two judges, not percent agreement (Thakur et al., arXiv 2406.12624).
6. **Human labels:** 40 pairs sampled by a frozen rule (seed 7; stratified by category, proportional; from the final device run), shown blind (BOAR/reference order randomized per pair with the same seed; system names removed; the app's "not from an offline source" preface kept, because users see it). Two raters (r4to, the app maintainer) label each pair independently:
   - (a) which answer is better (A / B / tie);
   - (b) is BOAR's answer correct on the core question (yes/no);
   - (c) is anything in it unsafe (yes/no).
   - Report inter-rater κ, judge-vs-human κ on (b), and the share of pairs where humans prefer BOAR or tie. Disagreements are reported, never resolved by the judge.

7. **Abstention, scored separately** (AbstentionBench-style, arXiv 2506.09038): over all v0.2 judged items, treat "decline" as a prediction that the question shouldn't be answered from the phone's knowledge. Report decline precision (share of declines that are judged appropriate: honesty-refusal items where the rubric says declining is right, or items the reference itself can't answer) and decline recall on the honesty-refusal items. This makes visible what the ratio's floor hides: a decline counts as ~0.31 of a reference answer in the ratio, whether or not declining was right.

## E3 check (held-out baseline)
- `main` (Android 4B, seeds 42/43) on v0.2-new.
- PASS if the held-out ratio is within ±0.04 of 0.512 AND the half-width on all v0.2 judged items ≤ 0.035.
- **Power note:** at ~110 held-out items the CI half-width alone is ≈ 0.037, so the ±0.04 band detects only shifts larger than sampling noise. A miss means a real difficulty shift or a skewed category draw; read it with the per-category table.

## Hash commitment
- The items file, references file, judge prompt, the analysis-plan file and the analysis scripts → one manifest with per-file sha256 + a combined sha256.
- Commit **only the combined hash** (and file count) to the public repo before any BOAR run on v0.2-new. Publish the files with the claim.
