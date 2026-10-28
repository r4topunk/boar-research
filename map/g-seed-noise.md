# seed and seed noise

> Closed record · as of 2026-10-28 · map node G-seed-noise (concept) · the standing on that date; open fronts in https://r4topunk.github.io/boar-research/data/status.json.

**seed and seed noise**

Plain: Running the same setup again with a different random seed gives different answers and a different score; that variation is seed noise.

Technical: Seed = sampling seed of answer generation. Same deep configuration, s42 vs s43: Δ −0.039 (−0.072…−0.011) raw on V-para. Rule since 2026-10-16: a one-seed deep-tier Δ < 0.05 on V-para is noise (was 0.03).

## Incoming

- uses: [X-110] SEEDVAR: SEEDVAR (seed noise sets the reading rule) → https://r4topunk.github.io/boar-research/map/x-110.md

Read chapter 10, Measuring the measurer: https://r4topunk.github.io/boar-research/research/measurer.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-012] Three seeds of the recommended deep configuration show how much one run can move. raw mean 0.550, SD 0.020 (0.533 / 0.572 / 0.544); floor-adjusted mean 0.432, SD 0.025 (0.412 / 0.460 / 0.425); 0 wins each seed (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 3 (42–44) · CI pooled CI UNKNOWN (aggregate file empty) · date 2026-10-10
- [F-020] Seed noise: the same deep configuration run with two random seeds differs by more than many tested "levers". s42 vs s43, same configuration: Δ −0.039 (−0.072…−0.011) raw; house rule since 2026-10-16: a one-seed deep-tier Δ below 0.05 on V-para is seed noise (raised from 0.03) (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 · CI paired 95 % bootstrap · date 2026-10-16 · caveat: The public boar-research README.md:77 still says 0.03.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
