# 3 · The floor trap

> Closed record · research record 1.1.2 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/floor-trap/ · Markdown twin: https://r4topunk.github.io/boar-research/research/floor-trap.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-10-02 → 10-07

**In one sentence.** The obvious score, "our answer's points divided by the reference's", gives a system that refuses every question about 0.31 for free, so the project moved its headline to a floor-adjusted ratio and win-rate, and kept printing all three.

## For curious readers {#curious}

#### A blank answer still gets points

The judge's scale runs from 1 to 5, not 0 to 5. So even an answer that says nothing earns a 1. If you divide BOAR's points by the reference's points, a version of BOAR that politely declines every single question already scores about 0.31.

#### So 0.50 was 61 % free

That means the bounty's 0.50 line was more than halfway reached by doing nothing. A number that rewards silence is not a fair ruler.

#### Subtract the free point

The fix: subtract the free point from both sides before dividing. On this "floor-adjusted" scale, silence scores 0 and matching the reference scores 1. A floor-adjusted 0.50 means "half of the frontier answer's value above nothing". It is a stricter scale, and we made it our headline. We still print the flattering one next to it, so you can see both.

#### And we count wins

A third, plainer number: on how many questions did the judge prefer BOAR's answer over the frontier answer, in both orders? We report it everywhere. You will see a lot of zeros.

#### Our real starting point

Here is the small model the phone runs, on the bounty-style questions it had never seen: 0.413 on the flattering scale, 0.261 on the honest one, and 0 wins out of 51.

*Badge:* V-para (bounty-style, sealed at the time) · Claude Opus judge · 51 questions · 2 runs.

**In one sentence card:** "We grade on the scale where a blank answer scores zero, and still show the flattering scale beside it." Number: 0.261 floor-adjusted / 0.413 raw, 0 of 51 wins (badge as above).

*Facts: [F-263] [F-341] [D-036]*

## For tech people {#tech}

### Raw, floor-adjusted, win/tie/loss: read the last two first

With S and R the mean rubric (mean of three axes, both orders averaged) of the app and of the reference: raw = ΣS / ΣR; floor-adjusted = Σ(S − 1) / Σ(R − 1); above-decline = (raw − D) / (1 − D) with D = 0.306, the measured raw score of a system that declines everything. Because the rubric's minimum is 1, raw 0.50 is about 61 % free. References score about 4.9/5, so the ratio behaves like an absolute rubric mean. Example on the 4B (v0.1, dev): raw 0.512 = floor-adjusted 0.387 = above-decline 0.297. We report all three, lead with floor-adjusted and win/tie/loss.

*Facts: [F-236] [F-237] [F-126] [F-263] [F-341] [F-268]*

## For AI professionals {#ai}

### The record for this chapter

**Key facts:**
- Always-decline floor D = 0.306 raw (79 judged declines, 7 runs) [F-263].
- An always-decline app gets ≈ 61 % of the 0.50 bar for free [F-341].
- References average ≈ 4.9/5, so the ratio behaves like an absolute rubric mean [F-182].
- Worked example on the 4B: raw 0.512 = 0.387 floor-removed = 0.297 above always-decline [F-268].
- The floor-adjusted scale was already a **pre-registered companion metric** in the plan frozen on 10-02; only its promotion to headline came after results (group-A §2 item 6).

**Key decisions:** [D-011] (10-02: bar on the raw ratio, but always print raw + floor-removed side by side), [D-036] / [D-036] / [D-036] (10-06: headline = floor-adjusted + win/tie/loss), [D-065] (win-rate reported, never gated; history: the 10-08/09 arm reports did read the bar with a win-rate conjunct; "never gated" fixed in BAR-TABLE on 10-10).

**Turning point:** the 10-06 pipeline audit: "rigorous process, looping direction" (E-process timeline). The switch went toward the stricter scale; an outside critic later called it post-hoc but "not self-serving" [D-036].

### Metrics

Let S_i and R_i be the order-averaged mean rubric of system and reference on item i. Raw = Σ S_i / Σ R_i. Floor-adjusted = Σ (S_i − 1) / Σ (R_i − 1). Above-decline = (raw − D)/(1 − D) with D = 0.306, the mean judged rubric of 79 declined answers over 7 runs divided by the mean reference rubric. Win/tie/loss is the order-combined winner per item. CIs: stratified (category) two-level bootstrap, items within stratum then runs within item, 2,000 resamples, seed 11, percentile; paired differences use the same procedure. For deep-tier rows we also report a common-mode CI that adds run-level seed variance: point ± 1.96·sqrt(SE_item² + (σ_run/√seeds)²).

*Facts: [F-236] [F-237] [F-126] [F-263] [F-127] [F-239] [D-072]*

### The bar and its history

The analysis plan, frozen and hashed on 2026-10-02 before any v0.2 item existed, set the primary metric to the raw ratio with a bar "CI low > 0.50" on both held-out sets and listed the floor-adjusted and above-decline ratios as pre-registered companion metrics, with win/tie/loss as a secondary. On 2026-10-02 the rubric floor was quantified (an always-decline system scores raw ≈ 0.31, ≈ 61 % of the bar). On 2026-10-06 an internal audit promoted the floor-adjusted ratio and win/tie/loss to the headline; the claim text adopted it on 2026-10-07. The primary research target since then is V-para floor-adjusted CI low ≥ 0.50 with two seeds; the formal raw rule is still printed. Some arm reports of 2026-10-08/09 read the bar with an additional "win-rate > 0" conjunct; from 2026-10-10 win-rate is "reported, never gated". We list this trail because the change of headline came after results; it went toward the stricter scale and all scales are printed for every row.

*Facts: [D-020] [D-021] [D-036] [D-065]*

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-126] Above-decline ratio = (raw − D) / (1 − D) with D fixed at 0.306. formula (judge.v1 ratio) · set all (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-02 · caveat: different scale from floor-adjusted; does not use the floor
- [F-127] CIs are a stratified (by category) two-level bootstrap: resample items within stratum, then runs within item; 2,000 resamples; seed 11; percentile 95 %. B 2000, seed 11 · set all (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-02 · caveat: does not include run-level noise beyond the runs available (see F-method-41)
- [F-182] The reference answers score ≈ 4.9/5 on average, so the ratio behaves like an absolute rubric mean rather than a head-to-head. ≈ 4.9 (judge.v1 ratio) · set v0.2, V-para (status UNKNOWN) · judge Opus · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-10 · caveat: public citation fix: per-dimension reference means (4.63-5.00) are at l.88-91, not l.66-69
- [F-236] Raw ratio = Σ S / Σ R, where S and R are the app's and reference's mean rubric (mean of 3 axes, both orders averaged). formula (judge.v1 ratio) · set all (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed
- [F-237] Floor-adjusted ratio = Σ (S − 1) / Σ (R − 1): quality above the rubric minimum of 1; 0.50 here means "half as good as the reference". formula (judge.v1 ratio) · set all (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed
- [F-239] Paired differences between two systems use the same stratified two-level bootstrap on the three scales. B 2000, seed 11 · set all (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed
- [F-263] D = 0.306 = mean judge rubric of 79 declined answers across 7 runs (≈ 1.50/5) divided by the mean reference rubric; v0.2-weighted 0.307. 0.306 · set v0.1 night runs, dev (dev, development data) · judge Opus · n 79 · seeds UNKNOWN · CI n 79 declines, 7 runs · date 2026-10-01
- [F-268] On the 4B, raw 0.512 = 0.387 floor-removed = 0.297 above always-decline. 0.512 / 0.387 / 0.297 (judge.v1 ratio) · set v0.1 dev (dev, development data) · judge Opus · n UNKNOWN · seeds 2 · CI 2 seeds; floor-removed CI 0.319–0.448 · date 2026-10-02 · caveat: three scales for one run; v0.1 dev, 2026-10-02; the near-identical 0.512 on v0.2 (F-002) is a different set.
- [F-341] An app that declines every question scores raw ≈ 0.31, i.e. ≈ 61 % of the 0.50 bar for free. 0.306 / 61 % (judge.v1 ratio) · set v0.1 (status UNKNOWN) · judge Opus · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-06 · caveat: citation fix: l.13 is the cut 6 v0.2 row

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-011] 2026-10-02 · Bar on the RAW ratio; every publication shows raw + floor-removed + above-always-decline side by side · why: rubric floor gives a blank system ~0.20–0.31. · status: superseded by D-036 (Floor-adjusted ratio + win/tie/loss became the headline on 2026-10-06 (applied 2026-10-07); the raw rule is still printed as the formal rule.)
- [D-020] 2026-10-02 · Freeze the analysis plan (metrics, CI method, seeds, wording rules) before items existed · why: prevents tuning metric to results. · status: kept
- [D-021] 2026-10-02 · Primary metric = raw ratio, bar > 0.50 (the author's decision on 2026-10-02, not the app maintainer's) · status: superseded by D-036 (Floor-adjusted ratio + win/tie/loss became the headline on 2026-10-06 (applied 2026-10-07); the raw rule is still printed as the formal rule.)
- [D-036] 2026-10-06 · Headline = floor-adjusted ratio + win/tie/loss (+ share of items ≥ 3/5), raw second; own bar = floor-adj ≥ 0.50 on V-para · why: raw 0.50 is ~61 % free because of the rubric floor. · status: kept
- [D-065] 2026-10-10 · Win-rate reported, never gated (later: proposal to drop the win-rate conjunct because it is saturated at 0) · why: every phone system scores 0 wins vs a 4.9/5 reference. · status: kept
- [D-072] 2026-10-11 · Common-mode CIs for deep-tier rows: CI = Δ ± 1.96·sqrt(SE_item² + 2σ_run²) · why: item bootstrap ignores run-level seed noise. · status: kept

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
