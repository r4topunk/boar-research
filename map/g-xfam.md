# cross-family judge (XFAM)

> Closed record · as of 2026-10-28 · map node G-xfam (concept) · the standing on that date; open fronts in https://r4topunk.github.io/boar-research/data/status.json.

**cross-family judge (XFAM)**

Plain: The same answers were re-scored by an AI judge from a different company, to see whether a Claude judge treats Claude-written references kindly or harshly.

Technical: Post-hoc re-judge of existing traces with OpenAI gpt-5.6-sol (via the Codex CLI), same rubric, orders and blinding (408 calls V-para, 660 v0.2). Scores ≈ +0.10 higher on both sets, ranking unchanged (Spearman 0.88–0.97), win-rate 0.00–0.06. Not pre-registered.

Read chapter 10, Measuring the measurer: https://r4topunk.github.io/boar-research/research/measurer.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-017] A judge from a different model family scores everything higher on V-para, but keeps the ranking and the near-zero win-rate. 4B: raw 0.497 (0.449–0.547), floor-adjusted 0.361; deep + think 512: raw 0.667 (0.621–0.711), floor-adjusted 0.577 (0.519–0.632); deep − 4B +0.171 (+0.123…+0.219) vs +0.139 under Claude; per-item Spearman 0.88–0.92; win-rate 0.00–0.01 (judge.v1 ratio) · set V-para (dev-style, development data) · judge cross-family: OpenAI gpt-5.6-sol (via the Codex CLI) (post-hoc, not pre-registered) · n 51 (408 judge calls) · seeds 2 · CI 95 % item bootstrap (4B floor-adjusted CI not in the sources read) · date 2026-10-16 · caveat: Post-hoc and not pre-registered; it is the only point above 0.50 floor-adjusted on V-para and exists only under the cross-family judge; the lower-judge rule keeps the Claude number as headline.
- [F-018] The cross-family judge on v0.2. 4B: raw 0.617 (0.567–0.666), floor-adjusted 0.517 (2 seeds); deep + think 512: raw 0.714 (0.666–0.759), floor-adjusted 0.639 (0.579–0.695) (1 seed); deep − 4B +0.097 vs +0.096 under Claude; Spearman 0.90–0.97; win-rate 2.7 % / 6.4 % vs 0 % under Claude (judge.v1 ratio) · set v0.2 (dev (burnt), development data) · judge cross-family: OpenAI gpt-5.6-sol (via the Codex CLI) (post-hoc, not pre-registered) · n 110 (660 judge calls) · seeds 4B 2, deep 1 · CI 95 % item bootstrap · date 2026-10-17 · caveat: Post-hoc. The Claude judge is the stricter family by ≈ 0.10 on both sets; the offset is stable across sets and arms.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
