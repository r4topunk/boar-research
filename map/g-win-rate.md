# win / tie / loss and win-rate

> Closed record · as of 2026-10-28 · map node G-win-rate (concept) · the standing on that date; open fronts in https://r4topunk.github.io/boar-research/data/status.json.

**win / tie / loss and win-rate**

Plain: For each question: did the judge prefer BOAR's answer, the reference, or neither? BOAR won 0 of 51 bounty-style questions.

Technical: Per-item combined winner over both orders (disagreement = tie). Reported, never gated (since 2026-10-10). 0 wins on every Claude-judged row of V-para and v0.2; isolated wins on v0.1 dev only.

Read chapter 3, The floor trap: https://r4topunk.github.io/boar-research/research/floor-trap.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-016] Win-rate against the frontier reference: zero on both bounty-relevant sets under the Claude judge; a few isolated wins exist only on the public dev set. 0 wins on every row and seed of V-para and v0.2 (Opus); v0.1 dev: 1/57 under Opus for the deep R450, LES and 4B rows; 2/57 under Haiku on the 12 GB-class phone run · set V-para; v0.2; v0.1 (dev-style / dev / public dev, development data) · judge Claude Opus; Claude Haiku L1 (phone run) · n 51 / 110 / 57 · seeds all · CI not computed · date 2026-10-14 · caveat: Public text that says "0 everywhere" (boar-research README.md:42, boar-bench TRACE-FORMAT.md:70) overstates the scope.
- [F-045] How the win-rate condition changed: secondary metric in the plan, briefly part of the bar in arm reports, then "reported, never gated". 2026-10-02 plan: W/T/L secondary; 2026-10-08/09 arm reports read the bar as "floor-adjusted CI low > 0.50 AND win-rate > 0"; 2026-10-10 BAR-TABLE: win-rate reported, never gated (judge.v1 ratio) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-10

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
