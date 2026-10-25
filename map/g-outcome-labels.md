# outcome labels (CWS, correct-any, WU, WW, HU)

> Living preprint · as of 2026-10-25 · map node G-outcome-labels (concept) · interim record, not a final result.

**outcome labels (CWS, correct-any, WU, WW, HU)**

Plain: Each answer is put into one class: right with the right source shown, right from memory, wrong with no warning, wrong with a warning, or an honest "unknown".

Technical: Shares of n items labelled by Claude Haiku 5.5-low under the UXMATRIX protocol: CWS = correct with the right source shown; CFM = correct from memory; correct-any = CWS + CFM; WC/WU = wrong with no warning; WW = wrong with the warning line; HU = honest unknown; RW = refused wrongly. Not a ratio to a reference: never compare with the judge.v1 ratio or with U-total.

## Incoming

- uses: [X-382] PACKPROOF: PACKPROOF → https://r4topunk.github.io/boar-research/map/x-382.md

Read chapter 14, Closing the research: what a small model needs: https://r4topunk.github.io/boar-research/research/closure.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-1704] PACKPROOF pooled correct-any with pack installed vs without. 0.48 vs 0.26, Δ +0.23 (outcome-label share) · set 180 pack self-tests (written from the packs), dev (dev (pack-written self-tests), development data) · judge Claude Haiku 5.5-low labels; correct-any · n 180 · seeds 42 · CI CI +0.16..+0.31; n 180; seed 42 · date 2026-10-23 · caveat: self-tests favour the pack; hosts differ by arm; 1 seed Metric: outcome-label shares of n items (Claude Haiku 5.5-low labels, UXMATRIX protocol); not the judge.v1 ratio.
- [F-1709] UXMATRIX Succinct: correct-any ON / OFF. 0.35 / 0.28 (CWS 0.28 / 0.03; WC 0.22 / 0.07) (outcome-label share) · set 60 dev items (40 cooking/money, 15 delivered general, 5 no-pack) (dev, development data) · judge Claude Haiku; outcome shares · n 60 · seeds 42 · CI n 60; seed 42 · date 2026-10-23 · caveat: Succinct and Detailed on different hosts Metric: outcome-label shares of n items (Claude Haiku 5.5-low labels, UXMATRIX protocol); not the judge.v1 ratio.
- [F-1727] Succinct on ENGINE-RC (page numbers) ON CWS 0.30, correct-any 0.43, WU 0.12; OFF correct-any 0.22, WU 0.10 (outcome-label share) · set UXMATRIX 60, dev (dev, development data) · judge Claude Haiku labels · n 60 · seeds 42 · CI n 60; seed 42 · date 2026-10-24 · caveat: PASS vs frozen CWS ≥0.28, WU OFF ≤0.10 Metric: outcome-label shares of n items (Claude Haiku 5.5-low labels, UXMATRIX protocol); not the judge.v1 ratio.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-25. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
