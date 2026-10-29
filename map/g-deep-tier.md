# deep tier

> Closed record · as of 2026-10-28 · map node G-deep-tier (concept) · the standing on that date; open fronts in https://r4topunk.github.io/boar-research/data/status.json.

**deep tier**

Plain: An optional slower mode that uses a much bigger model which "thinks" before answering; the largest quality gain measured so far, but as of 2026-10-18 it has not run on a phone (a pending run).

Technical: Cut 6 + Qwen3.6-35B-A3B UD-Q2_K_XL (≈ 3B active per token) + thinking budget 512: V-para floor-adjusted 0.436 (2 seeds, dev-style, Opus), desktop p50 ≈ 79 s; projected ≈ 1.9–2.8 min on a 12 GB phone.

## Incoming

- ruled out: [X-103] DEEPNORAG: DEEPNORAG (the deep tier without retrieval was worse (retrieval stays)) → https://r4topunk.github.io/boar-research/map/x-103.md

Read chapter 6, The deep tier: https://r4topunk.github.io/boar-research/research/deep-tier.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-009] Recommended deep configuration (35B mixture-of-experts + 512-token thinking budget) on the bounty-style set. raw 0.553 (0.524–0.581; with seed noise 0.513–0.592); floor-adjusted 0.436 (0.401–0.472; with seed noise 0.387–0.486); win 0/51; desktop p50 ≈ 79 s (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 · CI 95 % item bootstrap; common-mode CI adds seed noise · date 2026-10-09 · caveat: Chosen as the best of ≥ 8 deep configurations on this same set: expect a winner's-curse discount of about 0.01–0.02. QUEUE prints raw 0.552; the two-seed aggregate is 0.553. Desktop only.
- [F-035] Projected phone time for the recommended deep configuration (never measured on a phone). ≈ 1.9–2.8 min per answer at thinking budget 512 on a 12 GB phone CPU (third-party public decode rates of 4–6 tok/s + BOAR arithmetic); the 2026-10-09 estimate of 3.5–5 min was for budget 1024 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI projection · date 2026-10-12 · caveat: Third-party rates, not a BOAR measurement.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
