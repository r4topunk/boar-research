# QuickMath

> Closed record · as of 2026-10-28 · map node G-quickmath (concept) · the standing on that date; open fronts in https://r4topunk.github.io/boar-research/data/status.json.

**QuickMath**

Plain: Unit conversions and simple arithmetic are worked out by code, with no model and no sources.

Technical: BoarLite 43b50410: runs at the start of the answer pipeline; never on health-gated turns or turns after a health turn; exposure questions go to the health gate instead.

## Incoming

- uses: [D-215] Thesis restated: small models need external knowledge; a harness built around a small model's real capabilities, tuned for the app user (part of the harness) → https://r4topunk.github.io/boar-research/map/d-215.md

Read chapter 15, One simple app: LabRat: https://r4topunk.github.io/boar-research/research/submission.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-2200] QuickMath (43b50410): pure unit conversions and arithmetic are computed in code with no model, search, sources or line; health-gated turns and turns after a health turn are never computed. Model preload starts right after unpack (b8df70d9). The probe gate stays at 42 of 65 fixed text. 42 / 65 probes fixed text (unchanged) · set 65 F3-SAFETY probes (dev) (dev, development data) · judge none (0 LLM) · n 65 probes · seeds UNKNOWN · CI not computed · date 2026-10-24 18:54

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
