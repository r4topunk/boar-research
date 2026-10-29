# floor-adjusted ratio

> Closed record · as of 2026-10-28 · map node G-floor-adjusted (concept) · the standing on that date; open fronts in https://r4topunk.github.io/boar-research/data/status.json.

**floor-adjusted ratio**

Plain: The same ratio after removing the free point from both sides: how much of the reference's value above "nothing" BOAR delivers. This is the headline number.

Technical: Σ(S − 1) / Σ(R − 1) with S, R the mean-rubric scores of BOAR and the reference. Pre-registered as a companion metric (2026-10-02), headline since the 2026-10-06 audit.

## Incoming

- uses: [D-036] Headline = floor-adjusted ratio + win/tie/loss (+ share of items ≥ 3/5), raw second; own bar = floor-adj ≥ 0.50 on V-para (floor-adjusted + win-rate lead) → https://r4topunk.github.io/boar-research/map/d-036.md

Read chapter 3, The floor trap: https://r4topunk.github.io/boar-research/research/floor-trap.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-001] The frozen 4B claim build on the bounty-style set (V-para) delivers about a quarter of the frontier reference's value above "nothing", and loses every head-to-head. raw 0.413 (0.384–0.445); floor-adjusted 0.261 (0.224–0.300); win/tie/loss 0/0/51 in both seeds (judge.v1 ratio) · set V-para (held-out for this run (cut 3 on 2026-10-05, cut 6 on 2026-10-06); dev-style for everything measured after 2026-10-06) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 (42, 43) · CI 95 % item bootstrap · date 2026-10-06 · caveat: Cut 7 = cut 6 on this set (the FACTS table fires 0 times on it). Public BAR-TABLE prints CI high 0.300; one claim draft prints 0.299 (rounding).
- [F-044] The floor-adjusted scale was pre-registered as a companion metric before any held-out result; it was promoted to headline after the audit. 2026-10-02: plan lists floor-adjusted as companion (plan sha 375ff004…); 2026-10-06: audit decision D1 makes it the headline with win/tie/loss; 2026-10-07: applied in claim draft v3.1 (judge.v1 ratio) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-06 · caveat: The headline promotion came after the first held-out results; all three scales are always printed.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
