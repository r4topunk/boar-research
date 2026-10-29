# thinking budget

> Closed record · as of 2026-10-28 · map node G-thinking-budget (concept) · the standing on that date; open fronts in https://r4topunk.github.io/boar-research/data/status.json.

**thinking budget**

Plain: How many hidden "reasoning" words the model may write before answering. 512 was as good as 1024 at about half the time.

Technical: Cap on reasoning tokens; budget curve on V-para floor-adjusted: 0 → 0.33, 256 → 0.39, 512 → 0.44, 1024 → 0.42; 3072 no gain (model stops ≈ 1.3k tokens).

Read chapter 6, The deep tier: https://r4topunk.github.io/boar-research/research/deep-tier.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-008] Thinking is the largest single measured gain on the bounty-style set. thinking (1024) vs no thinking: raw +0.075 (+0.040…+0.110); floor-adjusted +0.093 (+0.050…+0.137) (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 · CI paired 95 % bootstrap · date 2026-10-08
- [F-010] A 512-token thinking budget matches 1024 in quality at about half the time. 512 vs 1024 on V-para: raw +0.011 (−0.010…+0.031), floor-adjusted +0.014 (−0.012…+0.039), ×0.55 time; on v0.2 −0.005 (−0.020…+0.009), ×0.62 time (judge.v1 ratio) · set V-para; v0.2 (dev-style / dev, development data) · judge Claude Opus (judge.v1, both orders) · n 51 / 110 · seeds 2 (V-para) / 1 (v0.2) · CI paired 95 % bootstrap · date 2026-10-09 · caveat: Verdict label: CHEAPER-PARITY (an equivalence, not a gain).
- [F-011] A 256-token budget is cheaper but measurably worse. raw 0.514 (0.483–0.544); floor-adjusted 0.387 (0.349–0.426); vs 1024 raw −0.028 (−0.056…−0.003); p50 ≈ 55 s (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 · CI paired 95 % bootstrap · date 2026-10-09 · caveat: Keeps ≈ 63 % of the thinking gain at 40 % of the time.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
