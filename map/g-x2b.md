# HEADPASS-X2b

> Closed record · as of 2026-10-28 · map node G-x2b (concept) · the standing on that date; open fronts in https://r4topunk.github.io/boar-research/data/status.json.

**HEADPASS-X2b**

Plain: The one retrieval change that worked: also feed the model the passages next to the best-matching one, plus a few found by meaning, within a fixed size limit.

Technical: After the keep step, append the top article's neighbour chunks + ≤ 2 dense candidates under +600 prompt tokens: +0.066 (+0.043…+0.091) Opus on the 180 (dev); inert on the claim kit.

## Incoming

- uses: [X-161] HEADPASS-X2b: HEADPASS-X2b: neighbour chunks + budgeted dense candidates appended after the keep step → https://r4topunk.github.io/boar-research/map/x-161.md

Read chapter 9, Knowledge packs: https://r4topunk.github.io/boar-research/research/packs.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-028] The one retrieval change that converted: append the retrieved article's neighbouring chunks plus a few vector-search candidates, under a 600-token budget (HEADPASS-X2b). Opus +0.066 (+0.043…+0.091); Haiku +0.056; fact chunk present in context 35 → 102 of 180 · set 180 pack self-tests (dev (designed on the same set), development data) · judge Claude Opus (judge.v1, both orders) · n 180 · seeds 1 · CI paired 95 % bootstrap · date 2026-10-14 · caveat: LEVER on pack-matched dev data only; inert on the claim kit (ceiling ≈ 0.011) and not a bounty-bar lever.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
