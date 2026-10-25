# DECLINE2STAGE

> Living preprint · as of 2026-10-25 · map node G-decline2stage (concept) · interim record, not a final result.

**DECLINE2STAGE**

Plain: A first check that gives zero to answers that do not try to answer, before the usual judge scores the rest.

Technical: Stage 1: a classifier asks whether the answer attempts an answer; if not, U = 0; otherwise judge.v1 scores it unchanged. Adopted as RULING R1 (2026-10-21) after the decline arm was invalid under judge.v1 (a bare refusal scored U 0.016-0.058); a coordinator override of a frozen FAIL, accepted with conditions by the spec reviewer. The decline offset D 0.058 is kept as a sensitivity row (U_net).

## Incoming

- uses: [D-144] RULING R1: judge = judge.v1 unchanged + DECLINE2STAGE zero per detected non-answer; D 0.058 kept as sensitivity row → https://r4topunk.github.io/boar-research/map/d-144.md

Read chapter 12, A second ruler (bench v0.4): https://r4topunk.github.io/boar-research/research/new-ruler.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-1529] RULING R1: judge = judge.v1 unchanged + DECLINE2STAGE zero per detected non-answer; D 0.058 kept as sensitivity row. adopted into ruler r3/r4 (judge.v1 ratio) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-21 · caveat: who decided: delegated coordinator (override of a frozen FAIL, accepted with conditions by reviewer); why: judge v1.1/v1.1b changed CE verdicts (5-7/40 flips); DECLINE2STAGE's 2 bar-(b) hits were engine refusal strings; alternatives: judge v1.1; decline subtraction only; reversible: yes (pre-exposure)
- [F-1637] Ruler floor anchors on judge.v1: the decline arm is INVALID (non-answers score U 0.016-0.058) and the closed-book 1.5B is not separable from the 1.7B under Haiku. decline U 0.058 / 0.053 / 0.016; 1.5B CB 0.259 vs 1.7B K0 0.294, +0.035 (-0.019..+0.089) (judge.v1 ratio) · set v0.1 public dev (dev, development data) · judge Claude Haiku 5.5-low judge.v1 · n 57 · seeds 1 · CI see value · date 2026-10-21 04:01-04:08 · caveat: Motivated DECLINE2STAGE and RULING R1 ; under Opus the 1.7B-1.5B gap becomes separable (+0.090)

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-25. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
