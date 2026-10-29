# expert streaming (bmoe, LES)

> Closed record · as of 2026-10-28 · map node G-expert-streaming (concept) · the standing on that date; open fronts in https://r4topunk.github.io/boar-research/data/status.json.

**expert streaming (bmoe, LES)**

Plain: Loading only the expert blocks a word needs from storage, instead of keeping the whole big model in memory.

Technical: bmoe v0.28.0 (the on-device engine) is judged-equivalent to llama-server on identical contexts. An OpenBMB llama.cpp fork (LES) runs the 35B in ≈ 2.8 GiB RSS on a desktop CPU at 14–17 tok/s, judged-equivalent; phone flash speed unmeasured.

Read chapter 7, A phone on a desk, and in a hand: https://r4topunk.github.io/boar-research/research/phone.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-036] An expert-streaming engine runs the 35B model in under 3 GiB of RAM on a desktop CPU with judged-equivalent answers. judged 0.625 vs llama-server 0.634, paired −0.010 (−0.042…+0.018); RSS 2.75–2.81 GiB; 14–17 tok/s on the Mac mini CPU; 10/10 greedy-identical vs the fork base · set v0.1 (public dev, development data) · judge Claude Opus (judge.v1, both orders) · n 57 (R450 contexts) · seeds 1 · CI paired 95 % bootstrap · date 2026-10-16 · caveat: Desktop only, experts read from a fast SSD and page cache; phone flash speed is unmeasured (analytic bound ≈ 4–6 tok/s with compute).
- [F-037] The on-device MoE engine (bmoe) is not token-identical to the desktop server but is judged equivalent on identical contexts. 0.623 vs 0.634, Δ −0.012 (−0.045…+0.020); greedy token-identical 0/10 · set v0.1 (public dev, development data) · judge Claude Opus (judge.v1, both orders) · n 57 · seeds 1 · CI paired 95 % bootstrap · date 2026-10-07 · caveat: An equivalence, not a lever: lets desktop deep-tier numbers transfer to a bmoe device plan with this caveat.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
