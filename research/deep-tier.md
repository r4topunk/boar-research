# 6 · The deep tier

> Closed record · research record 1.1.2 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/deep-tier/ · Markdown twin: https://r4topunk.github.io/boar-research/research/deep-tier.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-10-02, 10-06 → 10-10; dropped from delivery 10-21

**In one sentence.** The one lever that beat noise was a much bigger model, a 35B mixture-of-experts with only about 3B active per token, and letting it think for 512 tokens before answering; it climbs the ladder from 0.26 to 0.44 floor-adjusted on the bounty-style set (desktop only, dev-style data), and still wins no head-to-head. It never ran on a phone: on 2026-10-21 the author decided that no 35B deep mode is delivered for the bounty; the deep tier stays in the record as a roadmap with its desktop numbers ([D-147] / [F-1532];; open fronts OF-1 and OF-2 dropped, `data/status.json`).

## For curious readers {#curious}

#### A much bigger brain that mostly sleeps

The one idea that clearly beat the noise was a much bigger model: 35 billion parameters, built as a "mixture of experts". Think of a hospital with many specialists where each patient only sees a few. Only about 3 billion parameters work on each word, so it can run on strong hardware without needing all of its weights at once.

#### Scratch paper with a page limit

Then we let it think before answering: it writes hidden notes, up to a budget, and only then the answer. Thinking was the biggest single step we measured. And the budget had a sweet spot: 512 tokens of notes (a token is roughly a word piece) were as good as 1,024, in about half the time.

#### Climbing the ladder

On the bounty-style questions, the honest score climbs: 0.261 for the phone's small model, 0.329 for the big model, 0.436 for the big model with thinking. The line is 0.50.

*Badge:* V-para · practice-style for the big model (used for decisions after 6 Oct) · Claude Opus · 51 questions · 2 runs.

#### Still zero wins

Even at its best, the big model did not beat the frontier answer on a single one of the 51 questions. It would also need a phone with 12 GB of memory and, by our estimate, two to three minutes per answer. It only ever ran on a desktop: on 21 October the author decided not to ship it, and it stays in this record as a possible future, with its desktop numbers.

#### What's still missing

When we looked at where its remaining points were lost, most of it was knowledge the phone does not hold and the model does not know, and the rest was confident wrong facts.

**In one sentence card:** "A bigger model that thinks first got closest, 0.436, on a desktop, with no wins, and it was never shipped." Badge as in 6.3.

*Facts: [F-650] [F-033] [F-008] [F-010] [F-593] [F-009] [F-766] [F-1532] [F-1184]*

## For tech people {#tech}

### 35B mixture-of-experts + 512 tokens of thinking: 0.261 → 0.436 floor-adjusted, 79 s per answer on desktop; never delivered

The only lever that beat noise on bounty-style questions was a larger model, and it stayed on the desktop: on 2026-10-21 the author decided that no 35B deep mode is delivered [D-147]. Qwen3.6-35B-A3B activates about 3B parameters per token, so it fits a desktop CPU at 2-bit (UD-Q2_K_XL). On V-para (Opus, two seeds; dev-style data, desktop only) the ladder is: 4B claim build floor-adjusted 0.261 → deep tier 0.329 → deep + thinking 1024 0.422 → deep + thinking 512 0.436, all 0 wins of 51. Thinking is the biggest step (+0.093 floor-adjusted, CI +0.050…+0.137), and the budget has a knee: 512 tokens matches 1024 (+0.014 floor-adjusted, CI −0.012…+0.039) at 0.55× the time. Desktop p50 per answer: 4B ≈ 6–10 s, deep ≈ 31–33 s, deep + 512 ≈ 79 s, deep + 1024 ≈ 143–146 s.

**Table: the ladder** (judge.v1 ratio; V-para, Opus, 2 seeds unless noted; no phone rows: the deep tier was never run on a phone)

| config | raw (CI) | floor-adj (CI) | W/T/L | desktop p50 | status |
|---|---|---|---|---|---|
| 4B claim build (cut 6 = cut 7) | 0.413 (0.384–0.445) | 0.261 (0.224–0.300) | 0/0/51 | 6.3–10.1 s | held-out at run time |
| deep, no thinking | 0.467 (0.439–0.494) | 0.329 (0.294–0.362) | 0/0/51 | 30.9–33.3 s | dev-style |
| deep + thinking 256 | 0.514 (0.483–0.544) | 0.387 (0.349–0.426) | 0/0/51 | 53.2–57.5 s | dev-style |
| deep + thinking 1024 | 0.542 (0.513–0.571) | 0.422 (0.385–0.459) | 0/0/51 | 142.9–146.0 s | dev-style |
| deep + thinking 512 (recommended) | 0.553 (0.524–0.581) | 0.436 (0.401–0.472) | 0/0/51 | 78.9–79.4 s | dev-style; best of ≥ 8 configs |
W/T/L is per seed and identical for both seeds on every row.

**Gotcha boxes:**
- The on-device MoE engine (bmoe v0.28.0) has no thinking-budget flag; a phone build needs an app-side cap [F-751].
- The deep tier still needs retrieval: removing packs costs −0.045 (−0.083…−0.011) (slice of 20, 1 seed, Haiku) [F-1000].
- Bigger thinking budgets do nothing: the model stops by itself around 1.3k tokens [F-363].

*Facts: [F-005]*

## For AI professionals {#ai}

### The record for this chapter

**Key facts (V-para unless noted; Opus; 2 seeds unless noted; deep-tier V-para numbers are dev-style):**
- First deep test on v0.1: +0.060 (+0.021…+0.101), 0.565 vs 0.505, n 57, 2 seeds, dev [F-033].
- Closed-book plateau of 25–35B MoEs ≈ 0.60 vs 4B 0.487 (v0.1, 1 seed) [F-034].
- Deep, no thinking: raw 0.467 (0.439–0.494), floor-adj 0.329 (0.294–0.362), 0/51 [F-005].
- Thinking 1024: floor-adj 0.422 (0.385–0.459); gain +0.093 (+0.050…+0.137) floor-adj, the largest single gain [F-007] [F-008].
- Budget curve (floor-adj): 0 → 0.329, 256 → 0.387, 512 → 0.436, 1024 → 0.422, 3072 no further gain (3072: 1 seed, Haiku) [F-593].
- 512 vs 1024: raw +0.011 (−0.010…+0.031), floor +0.014 (−0.012…+0.039) at 0.55× the time (p50 79 s vs 143 s, desktop) [F-010] [F-010].
- Recommended config H: raw 0.553 (0.524–0.581), floor-adj **0.436** (0.401–0.472), common-mode floor CI 0.387–0.486, 0/51; selected as best of ≥ 8 deep configs (winner's curse ≈ 0.01–0.02) [F-009] [F-009].
- Three seeds: raw mean 0.550 (SD 0.020); floor-adj mean 0.432 (SD 0.025) [F-012].
- On v0.2 (dev, 1 seed): raw 0.608 (0.575–0.641), floor-adj 0.508 (0.467–0.550), 0/1/109: CI straddles 0.50 [F-013].
- Remaining loss on V-para: 59 % absent knowledge, 40 % wrong facts [F-1184] [F-630].
- Closed with numbers: Gemma 26B + thinking (−0.028 raw, 27 % faster), thinking 4B (+0.026, CI crosses 0), best-of-2 selectors (chance), sampling presets, context 1200, top-100k Wikipedia pack on the deep tier (−0.034, crowding), 3-bit quant (+0.004, not detected) ([F-608], -34, -60, -59; [F-999]).
- Retrieval still matters for the deep tier: no-pack −0.045 (−0.083…−0.011) [F-1000].

**Key decisions:** [D-013] (run the deep tier, report it separately with its latency), [D-031] (park it, 10-04), [D-039] (reopen it, 10-06), [D-056] / [D-056] (thinking budget 512), [D-068] (keep retrieval on the deep path), [D-067] (deep line closed on desktop, 10-10), [D-058] (seed-noise rule; raised from 0.03 to 0.05 on 10-16), [D-147] (author, 2026-10-21: no 35B deep mode delivered; roadmap only, with desktop numbers).

**Turning point:** 2026-10-08 20:20, DEEPTHINK: thinking adds +0.093 floor-adjusted, the biggest step on the ladder.

### 6.2 Model scale and test-time compute

All deep-tier rows were measured on V-para after it became development-style and on v0.2 after it was burnt; they are development evidence, desktop only. On V-para (Opus, two seeds): deep without thinking raw 0.467 (0.439–0.494), floor-adjusted 0.329 (0.294–0.362); with a 1024-token thinking budget 0.542 / 0.422 (0.385–0.459); with 512 tokens 0.553 (0.524–0.581) / 0.436 (0.401–0.472), common-mode floor-adjusted CI 0.387–0.486; with 256 tokens 0.514 / 0.387 (0.349–0.426). Every row wins 0 of 51 in each seed. Thinking (1024 vs none) adds +0.093 (+0.050…+0.137) floor-adjusted, the largest single effect we measured; 512 vs 1024 is parity (+0.014, −0.012…+0.039) at 0.55× the wall time; 256 vs 1024 loses −0.028 raw (−0.056…−0.003); a 3072 budget adds nothing (the model stops near 1.3k tokens; 1 seed, Haiku). The 512 configuration was selected as the best of at least eight deep configurations on V-para, so a winner's-curse discount of ≈ 0.01–0.02 applies; over three seeds its floor-adjusted mean is 0.432 (SD 0.025). On v0.2 the 512 configuration scores raw 0.608 (0.575–0.641), floor-adjusted 0.508 (0.467–0.550), W/T/L 0/1/109 with one seed; the 1024 configuration with two seeds scores 0.612 (0.581–0.644) / 0.514 (0.475–0.554).

*Facts: [F-005] [F-459] [F-006] [F-007] [F-008] [F-014] [F-605] [F-009] [F-012] [F-020] [F-464] [F-013] [F-460] [F-010] [F-011] [F-606] [F-593] [F-1231] [F-607] [F-750] [F-608] [F-465] [F-1170] [F-188] [F-004] [F-363]*

### 6.3 Right but thin: dimension shares, reference length and the loss map

Decomposed by rubric dimension, the 512 configuration on V-para is above 0.50 floor-adjusted on correctness alone (0.660, 0.608–0.712) and well below it on completeness (0.301) and usefulness (0.341); the 4B is 0.427 on correctness. Re-judging the same answers against references condensed to ≤ 80 words moves the 512 configuration from 0.412 to 0.514 (0.456–0.578) floor-adjusted (seed 42, Opus), a paired +0.102 (+0.068…+0.144); half of that shift comes from the shortened references scoring lower themselves, and we attribute ≈ 17 % of the gap to reference length and ≈ 83 % to substance. This is not a bar reading: references were altered and n is one seed. A loss map attributes 59 % of the remaining V-para loss to knowledge absent from both the kit and the model and 40 % to wrong facts; numbers and dates dominate wrong-fact loss. All of English Wikipedia (Aug-2025 + a 2026-10-01 delta) verifiably holds the missing fact for 9 of 34 absent bounty-style items, a lower bound.

*Facts: [F-284] [F-466] [F-190] [F-467] [F-468] [F-1184] [F-630] [F-470] [F-1008]*

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-004] Bar status: no configuration reaches 0.50 on the primary (floor-adjusted) reading; the formal raw rule is met only on development data by the deep tier with thinking. best floor-adjusted on V-para = 0.436 (CI high 0.472), short by 0.064; formal raw rule (CI low > 0.50) met by deep + thinking on dev data only (desktop; the v0.2 leg of the 512 budget is 1 seed); 0 wins on every Claude-judged row of V-para and v0.2 (judge.v1 ratio) · set V-para; v0.2 (dev / dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 / 110 · seeds see rows · CI see F-28 · date 2026-10-10 · caveat: Never present as "bar reached". Under the Claude judge on held-out data the bar was not reached.
- [F-005] Swapping in the 35B mixture-of-experts deep tier (no thinking) raises the bounty-style score. raw 0.467 (0.439–0.494); floor-adjusted 0.329 (0.294–0.362); win 0/51; desktop p50 ≈ 33 s (judge.v1 ratio) · set V-para (dev-style (measured after 2026-10-06), development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 · CI 95 % item bootstrap · date 2026-10-08 · caveat: Desktop only; the deep tier has never run on a phone.
- [F-006] Deep tier (no thinking) on v0.2. raw 0.568 (0.536–0.602); floor-adjusted 0.457 (0.417–0.500); win 0/110 (judge.v1 ratio) · set v0.2 (dev (burnt), development data) · judge Claude Opus (judge.v1, both orders) · n 110 · seeds 2 · CI 95 % item bootstrap · date 2026-10-08
- [F-007] Letting the deep tier think for up to 1024 tokens before answering. raw 0.542 (0.513–0.571); floor-adjusted 0.422 (0.385–0.459); win 0/51; desktop p50 ≈ 143 s (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 · CI 95 % item bootstrap · date 2026-10-08
- [F-008] Thinking is the largest single measured gain on the bounty-style set. thinking (1024) vs no thinking: raw +0.075 (+0.040…+0.110); floor-adjusted +0.093 (+0.050…+0.137) (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 · CI paired 95 % bootstrap · date 2026-10-08
- [F-009] Recommended deep configuration (35B mixture-of-experts + 512-token thinking budget) on the bounty-style set. raw 0.553 (0.524–0.581; with seed noise 0.513–0.592); floor-adjusted 0.436 (0.401–0.472; with seed noise 0.387–0.486); win 0/51; desktop p50 ≈ 79 s (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 · CI 95 % item bootstrap; common-mode CI adds seed noise · date 2026-10-09 · caveat: Chosen as the best of ≥ 8 deep configurations on this same set: expect a winner's-curse discount of about 0.01–0.02. QUEUE prints raw 0.552; the two-seed aggregate is 0.553. Desktop only.
- [F-010] A 512-token thinking budget matches 1024 in quality at about half the time. 512 vs 1024 on V-para: raw +0.011 (−0.010…+0.031), floor-adjusted +0.014 (−0.012…+0.039), ×0.55 time; on v0.2 −0.005 (−0.020…+0.009), ×0.62 time (judge.v1 ratio) · set V-para; v0.2 (dev-style / dev, development data) · judge Claude Opus (judge.v1, both orders) · n 51 / 110 · seeds 2 (V-para) / 1 (v0.2) · CI paired 95 % bootstrap · date 2026-10-09 · caveat: Verdict label: CHEAPER-PARITY (an equivalence, not a gain).
- [F-011] A 256-token budget is cheaper but measurably worse. raw 0.514 (0.483–0.544); floor-adjusted 0.387 (0.349–0.426); vs 1024 raw −0.028 (−0.056…−0.003); p50 ≈ 55 s (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 · CI paired 95 % bootstrap · date 2026-10-09 · caveat: Keeps ≈ 63 % of the thinking gain at 40 % of the time.
- [F-012] Three seeds of the recommended deep configuration show how much one run can move. raw mean 0.550, SD 0.020 (0.533 / 0.572 / 0.544); floor-adjusted mean 0.432, SD 0.025 (0.412 / 0.460 / 0.425); 0 wins each seed (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 3 (42–44) · CI pooled CI UNKNOWN (aggregate file empty) · date 2026-10-10
- [F-013] Recommended deep configuration on v0.2: the first point above 0.50 floor-adjusted on any set, with a CI that straddles 0.50. raw 0.608 (0.575–0.641); floor-adjusted 0.508 (0.467–0.550); win/tie/loss 0/1/109; desktop p50 ≈ 82 s (judge.v1 ratio) · set v0.2 (dev (burnt), development data) · judge Claude Opus (judge.v1, both orders) · n 110 · seeds 1 (42) · CI 95 % item bootstrap · date 2026-10-09 · caveat: One seed, development data, desktop only.
- [F-014] Deep tier with 1024-token thinking on v0.2. raw 0.612 (0.581–0.644); floor-adjusted 0.514 (0.475–0.554); 0 wins (judge.v1 ratio) · set v0.2 (dev (burnt), development data) · judge Claude Opus (judge.v1, both orders) · n 110 · seeds 2 · CI 95 % item bootstrap · date 2026-10-09
- [F-020] Seed noise: the same deep configuration run with two random seeds differs by more than many tested "levers". s42 vs s43, same configuration: Δ −0.039 (−0.072…−0.011) raw; house rule since 2026-10-16: a one-seed deep-tier Δ below 0.05 on V-para is seed noise (raised from 0.03) (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 · CI paired 95 % bootstrap · date 2026-10-16 · caveat: The public boar-research README.md:77 still says 0.03.
- [F-033] The first deep-tier test was the first lever to beat noise. deep35 vs 4B: 0.565 vs 0.505, Δ +0.060 (+0.021…+0.101) raw (judge.v1 ratio) · set v0.1 (public dev, development data) · judge Claude Opus (judge.v1, both orders) · n 57 · seeds 2 · CI paired 95 % bootstrap · date 2026-10-02 · caveat: Raw ratio on the public dev set.
- [F-034] Mixture-of-experts models in the 25–35B class form one closed-book plateau, well above the 4B. closed-book raw: Gemma 4 26B-A4B 0.613; Qwen3.5-35B-A3B 0.603; Qwen3.6-35B-A3B 0.596; vs 4B 0.487 (judge.v1 ratio) · set v0.1 (public dev, development data) · judge Claude Opus (judge.v1, both orders) · n 57 · seeds 1 · CI 1 seed; n 57 · date 2026-10-07 · caveat: Screen differences between the MoE models are not detected at MDE 0.055.
- [F-188] Formal raw rule (CI low > 0.50 on both sets) reading. met by T and H on dev data only (judge.v1 ratio) · set V-para + v0.2 dev (dev, development data) · judge Opus · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-10 · caveat: H's v0.2 leg is 1 seed; desktop only
- [F-190] Share of items with usefulness ≥ 3/5. K V-para 2.9 %, D 10.8 %, H 33.3 %; K v0.2 34.5 %, H 58.2 % · set V-para / v0.2 (status UNKNOWN) · judge Opus · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-10
- [F-284] On correctness alone H is above 0.50 floor-adj; the gap is in completeness and usefulness. V-para correctness floor-adj 0.660 (0.608–0.712) vs completeness 0.301 / usefulness 0.341 · set V-para dev (dev, development data) · judge Opus · n 51 (inferred from set) · seeds 2 · CI 2 seeds · date 2026-10-10 · caveat: "correct but thin" also describes an always-decline system on those dims; not a bar reading
- [F-363] Thinking budget 3072 added nothing: the model stops by itself at ~1.3k tokens. Δ +0.010 (−0.014…+0.041) · set V-para dev-style (dev-style, development data) · judge Haiku L1 · n UNKNOWN · seeds 1 · CI 1 seed · date 2026-10-08
- [F-459] Deep tier vs 4B paired gain on V-para. +0.068 floor-adj · set V-para dev (dev, development data) · judge Opus · n 51 (inferred from set) · seeds UNKNOWN · CI (two-level paired gap file) · date 2026-10-08
- [F-460] H vs the 4B on v0.2. +0.089 raw; +0.111 floor-adj (judge.v1 ratio) · set v0.2 dev (dev, development data) · judge Opus · n 110 (inferred from set) · seeds 1 · CI raw +0.054…+0.126; floor +0.066…+0.159; 1 seed · date 2026-10-09
- [F-464] The 4B is seed-stable on V-para (identical seeds) per-item r 0.81; Δ 0.000 · set V-para (status UNKNOWN) · judge Opus · n 51 (inferred from set) · seeds 2 · CI 2 seeds · date 2026-10-10
- [F-465] Thinking twin of the claim 4B (Qwen3-4B-Thinking-2507 @512) on V-para. raw 0.439; floor-adj 0.293; Δ +0.026 vs K (judge.v1 ratio) · set V-para dev (dev, development data) · judge Opus · n 51 (inferred from set) · seeds 1 · CI Δ CI −0.013…+0.068; 1 seed · date 2026-10-10 · caveat: ×3.7 time (23.6 s); not detected at MDE 0.06
- [F-466] 4B correctness-only floor-adj on V-para / v0.2. 0.427 (0.371–0.482) / 0.595 (0.544–0.646) · set V-para / v0.2 dev (dev, development data) · judge Opus · n 51 (inferred from set) · seeds 2 · CI 2 seeds · date 2026-10-10
- [F-467] Shortening references to ≤ 80 words lifts H floor-adj 0.412 → 0.514 and K 0.261 → 0.322. +0.102 (+0.068…+0.144) H; +0.060 K · set V-para dev, references altered (dev, development data) · judge Opus · n 51 (inferred from set) · seeds 1 · CI 1 seed (s42) · date 2026-10-10 · caveat: ≈ 17 % of H's gap is reference length, ≈ 83 % substance; not a bar reading
- [F-468] Reference answers are long. p10/p50/p90 = 251/280/318 words · set V-para (status UNKNOWN) · judge UNKNOWN · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-10
- [F-470] Numbers and dates dominate the wrong-fact loss; declining instead of a wrong answer would lower the score (RATIONALEPASS) numeric + date 0.51 (V-para) / 0.70 (v0.2) of wrong loss; decline oracle −0.064 / −0.040 · set V-para / v0.2 (status UNKNOWN) · judge jev over Opus rationales · n UNKNOWN · seeds UNKNOWN · CI 0/16, 0/17 items better · date 2026-10-12 14:17
- [F-593] Budget curve (V-para floor-adj): 0 → 256 → 512 → 1024 → 3072. 0.329 → 0.387 → 0.436 → 0.422 → no further gain · set V-para dev (dev, development data) · judge Opus (3072 Haiku) · n 51 (inferred from set) · seeds 2 · CI 2 seeds each (3072: 1 seed Haiku, +0.010) · date 2026-10-08/09 · caveat: knee at 512; Qwen stops thinking ≈ 1.3k tokens
- [F-605] Haiku L1 stopped the v0.2 thinking arm at +0.027 (vs +0.03 clause); Opus later measured +0.045 (+0.022…+0.070) +0.027 Haiku / +0.045 Opus · set v0.2 dev (dev, development data) · judge Haiku L1 / Opus · n 110 · seeds Haiku 1; Opus 2 · CI Haiku s42: +0.027 (+0.002…+0.054), n 110; Opus two seeds two-level: +0.045 (+0.022…+0.070); Opus same-seed s42 comparison: +0.048 · date 2026-10-09 · caveat: +0.045 is the two-seed figure (not '1 seed'); the near-miss rule text quotes the same-seed +0.048. Both are correct in context
- [F-606] Budget 256 vs 1024 / vs 512. −0.028 / −0.039 raw (judge.v1 ratio) · set V-para dev (dev, development data) · judge Opus · n 51 (inferred from set) · seeds 2 · CI −0.056…−0.003 / −0.066…−0.015; 2 seeds · date 2026-10-09 · caveat: keeps ≈ 63 % of the thinking gain at 40 % of the time
- [F-607] Thinking budget hits: at 1024, 58/91 generating v0.2 items and 36/51 V-para; at 512, 83/110 v0.2 and 46/51 V-para. 1024: 58/91 generating v0.2 items (s42) and 36/51 V-para (s42); 512: 83/110 v0.2 (s42) and 46/51 (s42) / 42/51 (s43) V-para · set v0.2 / V-para dev (dev, development data) · judge UNKNOWN · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-09 · caveat: the 36/51 figure was uncited (it is DEEPTHINK.md l.16); counts are per seed
- [F-608] Gemma + thinking vs Qwen + thinking. −0.028 raw (judge.v1 ratio) · set V-para dev (dev, development data) · judge Opus · n 51 (inferred from set) · seeds 2 · CI −0.057…+0.003; 2 seeds · date 2026-10-09 · caveat: parity-faster clause failed
- [F-630] Where the deep tier loses points (LOSSMAP) absent knowledge 0.59 (V-para) / 0.55 (v0.2) of loss; wrong fact 0.40 / 0.21 · set V-para dev-style + v0.2 dev (dev-style, development data) · judge Opus rationales classified by jev (a calibrated classifier) · n UNKNOWN · seeds 1 · CI 51 / 110 items; 1 seed · date 2026-10-11 12:10 · caveat: label model unvalidated against humans (CRITIQUE C3)
- [F-650] The deep-tier model is Qwen3.6-35B-A3B UD-Q2_K_XL. 12,290,628,576 B, Apache-2.0 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10 · caveat: desktop only so far
- [F-750] Gemma 4 26B-A4B + thinking (G) on V-para. raw 0.514; floor-adj 0.388 (judge.v1 ratio) · set V-para dev (dev, development data) · judge Opus · n 51 (inferred from set) · seeds 2 · CI raw 0.487–0.540; floor 0.354–0.421; 2 seeds · date 2026-10-09 · caveat: 27 % faster than T, RSS ≈ 7.7 GB
- [F-751] bmoe v0.28.0 has no thinking-budget flag; a device needs an app-side cap. · date 2026-10-09 · caveat: unbounded thinking ≈ 1.3k tokens, ≈ 2× time
- [F-766] Deep + think 512 on a Pixel 8 Pro CPU is projected at 1.9–2.8 min per answer. 1.9–2.8 min · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI from published third-party rates · date 2026-10-12 · caveat: not our measurement; deep tier never ran on a phone
- [F-999] Adding the top-100k Wikipedia pack to the deep tier crowded out curated chunks. Δ −0.034 (−0.082…+0.003); 26/28 slots taken · set V-para dev-style (dev-style, development data) · judge Haiku L1 · n UNKNOWN · seeds UNKNOWN · CI slice 20 · date 2026-10-10 · caveat: corpus size closed for deep tier too
- [F-1000] Retrieval still matters for the deep tier (removing packs hurts) −0.045 (−0.083…−0.011) · set V-para slice dev (dev, development data) · judge Haiku N=4 · n 20 (slice) · seeds 1 · CI slice 20; 1 seed · date 2026-10-10 · caveat: slice power low
- [F-1008] Wikipedia-anywhere gate for V-para absent-knowledge items. 9/34 verified (MARGINAL band 7–13) · set V-para dev (dev, development data) · judge jev + quote check · n 51 (inferred from set) · seeds UNKNOWN · CI 34 items · date 2026-10-12/13 · caveat: 25/34 unverified, not shown absent
- [F-1170] Thinking 4B on v0.2. Δ +0.009 · set v0.2 dev (dev, development data) · judge Haiku L1 · n 110 (inferred from set) · seeds 1 · CI −0.015…+0.035; 1 seed · date 2026-10-10 · caveat: Haiku compresses; Opus never run
- [F-1184] V-para remaining loss composition (deep tier) 59 % absent knowledge + 40 % wrong facts · set V-para dev (dev, development data) · judge jev labels (LOSSMAP) · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-12 · caveat: label model unvalidated (critique C3)
- [F-1231] Desktop latency per answer (p50) along the ladder on V-para. 4B 6.3 s (same backend) / 10.1 s (claim run); D 33.3/30.9 s; Q 57.5/53.2 s; H 78.9/79.4 s; G 106–109 s; T 142.9/146.0 s; Z 23.6 s · set V-para (status UNKNOWN) · judge UNKNOWN · n 51 (inferred from set) · seeds UNKNOWN · CI per seed · date 2026-10-08/10 · caveat: Mac mini M4 CPU desktop proxy, not a phone
- [F-1532] 35B deep mode not delivered; deep tier appears only as roadmap with desktop numbers. stood · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-21 · caveat: who decided: author (GRILL); why: focus on 8 GB UX; no Android expert-streaming build; alternatives: 12 GB deep tier; reversible: yes

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-013] 2026-10-02 · Run the deep tier (35B MoE); its ratio counts only reported separately from the default, with its latency · why: first candidate lever with a prior above noise; bounty hint about large MoE. · status: kept
- [D-031] 2026-10-04 · Focus on the 4B default tier; deep tier parked at D1; coordinator runs work with subagents instead of a standing chat team · why: work budget; no 12 GB phone. · status: superseded (4B levers exhausted by 10-05; deep tier reopened 10-06)
- [D-039] 2026-10-06 · Stop answer-identical 4B arms; reopen the deep tier as the primary quality lever · why: 15 arms, 0 ratio movement. · status: kept
- [D-056] 2026-10-09 · Recommend thinking budget 512 for the deep tier · why: CHEAPER-PARITY with 1024 at 0.55× time. · status: kept
- [D-058] 2026-10-10 · Seed-noise reading rule (V-para one-seed deep Δ < ~0.03 is noise; later raised to 0.05) · why: SEEDVAR three-seed spread. · status: superseded by D-113 (Threshold raised from 0.03 to 0.05 on 2026-10-16 after the outside critique (SEEDVAR showed a −0.039 gap between seeds).)
- [D-067] 2026-10-10 · Declare the deep-tier line closed on desktop and the 4B side closed · why: model, parity, thinking, budget, persona/context, routing all measured. · status: kept
- [D-068] 2026-10-10 · Keep retrieval on the deep path · why: no-pack −0.045 (−0.083…−0.011) · status: kept
- [D-147] 2026-10-21 · 35B deep mode not delivered; deep tier appears only as roadmap with desktop numbers · why: focus on 8 GB UX; no Android expert-streaming build. · status: kept

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
