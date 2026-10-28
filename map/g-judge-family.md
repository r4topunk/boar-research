# judge family / self-preference

> Closed record · as of 2026-10-28 · map node G-judge-family (concept) · the standing on that date; open fronts in https://r4topunk.github.io/boar-research/data/status.json.

**judge family / self-preference**

Plain: The questions, the reference answers and the judge all came from the same AI company, which may bias the scores.

Technical: Claude wrote v0.2 and V-para items and the references, and judged. Self-preference direction is measured only by one post-hoc cross-family re-judge. v0.3 is to be written outside the Claude family.

## Incoming

- uses: [X-175] XFAM: XFAM: cross-family re-judge of the existing V-para traces (the other family scores ≈ 0.10 higher, same ranking) → https://r4topunk.github.io/boar-research/map/x-175.md

Read chapter 10, Measuring the measurer: https://r4topunk.github.io/boar-research/research/measurer.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-017] A judge from a different model family scores everything higher on V-para, but keeps the ranking and the near-zero win-rate. 4B: raw 0.497 (0.449–0.547), floor-adjusted 0.361; deep + think 512: raw 0.667 (0.621–0.711), floor-adjusted 0.577 (0.519–0.632); deep − 4B +0.171 (+0.123…+0.219) vs +0.139 under Claude; per-item Spearman 0.88–0.92; win-rate 0.00–0.01 (judge.v1 ratio) · set V-para (dev-style, development data) · judge cross-family: OpenAI gpt-5.6-sol (via the Codex CLI) (post-hoc, not pre-registered) · n 51 (408 judge calls) · seeds 2 · CI 95 % item bootstrap (4B floor-adjusted CI not in the sources read) · date 2026-10-16 · caveat: Post-hoc and not pre-registered; it is the only point above 0.50 floor-adjusted on V-para and exists only under the cross-family judge; the lower-judge rule keeps the Claude number as headline.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
