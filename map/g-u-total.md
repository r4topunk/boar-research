# U-total

> Closed record · as of 2026-10-28 · map node G-u-total (concept) · the standing on that date; open fronts in https://r4topunk.github.io/boar-research/data/status.json.

**U-total**

Plain: The ruler's headline number: how much of a reference answer's useful content the app delivers, over all 71 headline questions.

Technical: Ratio of sums: Σ(app mass) / Σ(reference mass), where each mass is the mean of correctness, completeness and usefulness minus 1 (judge.v1, 1-5 scale), so the rubric floor maps to 0; detected non-answers are set to 0 by DECLINE2STAGE; health items weigh 0.5 (weight-1 printed beside). Verdict statistic = the lower of the two judge families per bootstrap draw; "meets the bar" needs CI low > 0.50. A different metric from the judge.v1 V-para / v0.2 ratios: never compare across.

## Incoming

- uses: [X-405] RULER-FINAL: Ruler v0.4 on BoarLite's final engine (desktop twin) → https://r4topunk.github.io/boar-research/map/x-405.md

Read chapter 12, A second ruler (bench v0.4): https://r4topunk.github.io/boar-research/research/new-ruler.md

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-1529] RULING R1: judge = judge.v1 unchanged + DECLINE2STAGE zero per detected non-answer; D 0.058 kept as sensitivity row. adopted into ruler r3/r4 (judge.v1 ratio) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-21 · caveat: who decided: delegated coordinator (override of a frozen FAIL, accepted with conditions by reviewer); why: judge v1.1/v1.1b changed CE verdicts (5-7/40 flips); DECLINE2STAGE's 2 bar-(b) hits were engine refusal strings; alternatives: judge v1.1; decline subtraction only; reversible: yes (pre-exposure)
- [F-1543] Freeze r4: add information-available split (FACT-AVAIL) + ORACLE/ORACLE-0 rows; U-total stays verdict. frozen sha 82772e33; labels quarantined (ruler U-total) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-21 · caveat: who decided: author asked; coordinator + reviewer (H1-H8); why: separate "packs lack it" from "app fails to deliver it"; alternatives: no split; reversible: no (frozen) Metric: ruler v0.4 U-total (ratio of sums against the reference mass, 71 headline items, health weight 0.5); never compare with the judge.v1 ratio.

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
