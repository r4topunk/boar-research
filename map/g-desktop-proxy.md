# desktop proxy and device parity

> Living preprint · as of 2026-10-25 · map node G-desktop-proxy (concept) · interim record, not a final result.

**desktop proxy and device parity**

Plain: The exact phone engine also runs on a Mac for fast testing; real phones confirmed that the Mac gives the same judged quality.

Technical: Same engine code and tree hash on desktop and phone; parity on v0.1: 12 GB-class phone 0.529 = desktop 0.529 (Haiku); 8 GB phone 0.561 vs 0.558/0.560 (Opus).

## Incoming

- uses: [X-165] DEVICE-X6: Cut 7 on a 12 GB-class phone (phone = desktop on v0.1 dev) → https://r4topunk.github.io/boar-research/map/x-165.md

Read chapter 7, A phone on a desk, and in a hand: https://r4topunk.github.io/boar-research/research/phone.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-023] On a real 12 GB-class phone, in airplane mode, the frozen build gives the same judged quality as on the desktop. phone raw 0.529 (0.481–0.575) vs desktop 0.529; floor-adjusted 0.403 vs 0.402; paired −0.000 (−0.026…+0.028); 72/72 answered; fast-tier p50 30.7 s; app memory (PSS) peak 5.88 GB during model load, then ≤ 4.23 GB (judge.v1 ratio) · set v0.1 (public dev, development data) · judge Claude Haiku 5.5-low (L1 triage judge, N = 4, both orders) · n 57 · seeds 1 run · CI paired 95 % bootstrap · date 2026-10-14 · caveat: Haiku-judged level; not comparable with Opus-judged ratios. The device has 10.7 GiB usable RAM.
- [F-024] Earlier, on an 8 GB phone, cut 6 also matched the desktop. phone 0.561 (0.507–0.617) vs desktop 0.558 / 0.560; 73/73 answered; PSS max 4.41 GiB · set v0.1 (public dev, development data) · judge Claude Opus (judge.v1-med) · n 57 · seeds 1 run · CI 95 % item bootstrap · date 2026-10-06 · caveat: Opus-judged; not comparable in level with the Haiku-judged 12 GB-class run.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-25. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
