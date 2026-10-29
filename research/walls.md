# 5 · The walls

> Closed record · research record 1.1.2 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/walls/ · Markdown twin: https://r4topunk.github.io/boar-research/research/walls.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-10-03 → 10-06

**In one sentence.** Oracle tests showed where the small model's ceiling was: handing it the perfect passage helps, but getting that passage, and knowing what isn't in the kit, was the wall; bigger dense models, better prompts and better retrieval variants all failed.

## For curious readers {#curious}

#### Hand it the right page

We tried cheating on purpose: give the small model the exact passage that holds the answer. Its score rose from 0.507 to 0.606 on the practice set. So the reader can read. The question is whether the right page ever reaches it.

*Badge:* v0.1 practice · Claude Opus · 57 questions · 1 run.

#### The library doesn't have the book

Often it doesn't, because the downloaded libraries simply don't contain the fact. A smarter search that pulled the right sentence into the prompt more than twice as often still did not raise the score.

#### Bigger small models, longer answers: no

Swapping in other models of similar size did not help. Asking for longer answers made the model invent more.

#### An audit, and a burnt exam

On 6 October an internal audit said the process was rigorous but going in circles. The same day we found that one sealed exam's questions had sat in a private code history the builders could have seen. We declared it burnt: from then on it counts as practice.

**In one sentence card:** "The small model reads well enough; what it lacks is knowledge the phone doesn't hold."

*Facts: [F-314] [F-443] [F-992] [F-450] [F-433]*

## For tech people {#tech}

### Retrieval, prompts and bigger small models: the walls

Oracle runs set the ceiling. On v0.1 (dev, Opus, 1 seed, n 57): closed-book 0.487, engine 0.507, question-chosen passages 0.567, gold passages 0.606, Claude Haiku with no web 0.653. A retrieval rewrite put the gold sentence in context 7 → 18 times out of 56 and still lost 0.021. A Wikipedia top-100k pack bought nothing for the 4B and made retrieval 3.3× slower. Recall@5 was 0.333 and coverage was the largest failure bucket (49 %). Other 4–9B models were no better closed-book (Qwen3.5-9B 0.488 vs Qwen3-4B 0.487). Prompts that asked for longer or more complete answers raised confident-wrong answers. The lesson for builders: on this hardware the small model's reading is not the bottleneck; knowledge the kit does not hold is.

**Decision table:** lever → measured effect → status (from the public registry; e.g. R3 named-slot ranking, R5 enwiki top-100k for the 4B, R7 shorter prompt, R8 "answer completely", R13 multi-pass).

*Facts: [F-314] [F-443] [F-993] [F-453] [F-450] [F-433]*

## For AI professionals {#ai}

### The record for this chapter

**Key facts (v0.1 dev, Opus unless noted):**
- Oracle ladder: closed-book 0.487 · engine 0.507 · question-chosen passages 0.567 · gold passages 0.606 · Haiku no-web 0.653 (raw, 1 seed, n 57) [F-314].
- Retrieval v2 put the gold sentence in context 7 → 18/56 times yet lowered quality −0.021 [F-443].
- Perfect Wikipedia retrieval buys at most ≈ +0.005–0.017; most of the oracle gain came from web-only facts [F-992].
- Retrieval scorecard: recall@5 0.333; coverage is the largest failure bucket (49 %) [F-453].
- Model line closed for the 4B tier: Qwen3.5-4B 0.437, Gemma 4 E4B 0.495, Qwen3.5-9B 0.488, Ministral 8B 0.457 vs 0.487 [F-450].
- Longer-answer persona: Δ −0.044, confident-wrong 10 → 20 [E-027] [F-433]. A completeness instruction made the 35B longer but less correct (correctness 3.89 → 3.10) [F-579].
- 4B loss anatomy: gap to Haiku +0.121 net; biggest buckets have no live lever [F-317].
- DEEPREAD: the 35B reads gold passages about like the 4B (0.634 vs 0.606, +0.029, CI −0.004…+0.063): its advantage is knowledge [F-455] [F-578].

**Key decisions:** [D-010] (strategy memo: Android-only, three fronts, stop list), [D-012] (close the big-pack front, kill rule K1), [D-029] (park retrieval after rv2), [D-039] (stop answer-identical 4B arms; reopen the deep tier), [D-037] / [D-037] (v0.2 burnt → dev).

**Turning point:** 2026-10-06 14:06, the pipeline audit; same day v0.2 declared burnt because its plaintext sat in a private repo's git history.

### The small model's walls (v0.1 dev)

Oracle runs on v0.1 (n = 57, 1 seed, Opus, raw) bracket the 4B: closed-book 0.487, engine 0.507, question-chosen passages 0.567, gold passages 0.606, Claude Haiku without web 0.653. The 35B reads the same gold passages only slightly better (0.634, +0.029, −0.004…+0.063), so its advantage is stored knowledge. A retrieval rewrite increased gold-sentence presence 7 → 18 of 56 yet lowered quality (−0.021); 25–35B MoEs form a closed-book plateau at ≈ 0.60 (0.596–0.613); 4–9B alternatives do not beat Qwen3-4B (0.437–0.495 vs 0.487).

*Facts: [F-314] [F-443] [F-034] [F-455] [F-450]*

### 8 A registry of what did not work

We keep a public registry of 76 lever families (61 closed, 13 not detected, 2 measurements; a private registry continues to 98 rows) with, for each: what was tried, set and judge, effect with CI, minimum detectable effect where the test had one, and the condition that would reopen it. Families include larger closed-book models, prompt and persona changes, sampling presets, best-of-2 and self-verification, routing between tiers, re-ranking, query rewriting, corpus size, Wikipedia variants, computed verdicts, fine-tuning data, speculative decoding and quantization. Five closures based on n ≈ 20 slices with CI upper bounds ≥ +0.03 are relabelled here as "not detected at MDE 0.08" (R31, R83, R84, R85, R97), following an outside critique.

*Facts: [F-487] [F-932] [D-073]*

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-034] Mixture-of-experts models in the 25–35B class form one closed-book plateau, well above the 4B. closed-book raw: Gemma 4 26B-A4B 0.613; Qwen3.5-35B-A3B 0.603; Qwen3.6-35B-A3B 0.596; vs 4B 0.487 (judge.v1 ratio) · set v0.1 (public dev, development data) · judge Claude Opus (judge.v1, both orders) · n 57 · seeds 1 · CI 1 seed; n 57 · date 2026-10-07 · caveat: Screen differences between the MoE models are not detected at MDE 0.055.
- [F-314] Oracle ladder: closed-book 0.487 · engine 0.507 · question-chosen passages 0.567 · gold passages 0.606 · 1500-token gold 0.626 · Haiku no-web 0.653. see value · set v0.1 EN dev (dev, development data) · judge Opus · n UNKNOWN · seeds UNKNOWN · CI 57 items · date 2026-10-03 · caveat: gold passages chosen with knowledge of the reference → upper bound
- [F-317] 4B loss anatomy: gap to Haiku +0.121 net; cut 2's gain over old main (+0.026) came entirely from non-model paths. +0.121 · set v0.1 EN dev (dev, development data) · judge existing verdicts · n UNKNOWN · seeds UNKNOWN · CI 57 items · date 2026-10-04 · caveat: biggest buckets "thin but correct" and "knowledge" had no lever
- [F-433] Asking the 4B for longer answers (persona P2) lowered quality: correct items 39 % → 14 %, confident-wrong 10 → 20. Δ −0.044 · set v0.1 dev (dev, development data) · judge Opus · n UNKNOWN · seeds UNKNOWN · CI (−0.076…−0.014), MDE 0.029 · date 2026-10-02 · caveat: judge length slope negative (−0.34 per log-word)
- [F-443] Retrieval v2 put the gold sentence in context 7 → 18/56 times but lowered quality. Δ −0.021 · set v0.1 EN dev (dev, development data) · judge Opus · n UNKNOWN · seeds 2 · CI CI90 −0.054…+0.009, 2 seeds · date 2026-10-03 · caveat: retrieval 3.6× slower; 3 items carry the loss
- [F-450] Bigger closed-book models do not help the 4B tier. Qwen3.5-4B 0.437, Gemma E4B 0.495, Qwen3.5-9B 0.488, Ministral 8B 0.457 vs 0.487 · set v0.1 dev (dev, development data) · judge Opus · n 57 · seeds 1 · CI n 57; 1 seed · date 2026-10-05/06 · caveat: not detected at MDE 0.055
- [F-453] Retrieval failure scorecard on v0.1 gold items. coverage bucket 49 %; recall@5 0.333; gold in prompt 24/78 item-runs · set v0.1 dev (dev, development data) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI 39 gold items × 2 runs · date 2026-10-06
- [F-455] Deep model reads gold passages like the 4B. R450 0.634; paired vs 4B +0.029 (−0.004…+0.063) · set v0.1 dev (dev, development data) · judge Opus · n 57 · seeds 1 · CI 1 seed; n 57 · date 2026-10-06 · caveat: deep gain = knowledge, not reading
- [F-487] Registry size. 98 rows private (R1–R98); 76 rows public · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-16 · caveat: public lags R77–R98
- [F-578] Deep 35B reading the same gold passages as the 4B scored only slightly higher: the reader converts like the 4B; engine-level +0.06 is knowledge. 0.634 vs 0.606; Δ +0.029 · set v0.1 EN dev (dev, development data) · judge Opus · n UNKNOWN · seeds 1 · CI (−0.004…+0.063), 57 items, 1 seed · date 2026-10-06 · caveat: "not detected at MDE 0.055"
- [F-579] A completeness instruction made the 35B longer but less correct. correctness 3.89 → 3.10; CW 7 → 15; ratio Δ −0.014 (judge.v1 ratio) · set v0.1 EN dev (dev, development data) · judge Opus · n UNKNOWN · seeds 1 · CI (−0.055…+0.024), 1 seed · date 2026-10-06
- [F-932] Closed-family registry size. public 76 rows (61 closed, 13 not detected, 2 measurement); private 98 rows by 10-16 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-15/16 · caveat: public snapshot frozen 10-15 | Verification note: 76 = 61 + 13 + 2 is at REVIEW-RESEARCH-PAGE:5, not :33.
- [F-992] Perfect Wikipedia retrieval buys at most ~+0.005–0.017; most oracle gain came from web-only facts. web-only +0.027, wiki-only +0.005 · set v0.1 EN dev (dev, development data) · judge Opus · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-03
- [F-993] Big pack (top-100k Wikipedia) on the 4B: no gain, retrieval 3.3× slower. Δ −0.005 / −0.016 · set v0.1 EN dev (dev, development data) · judge Opus-med · n UNKNOWN · seeds 1 · CI 1 seed · date 2026-10-03 · caveat: one seed: under-powered (audit) | Verification note: Public CLOSED.md:20 (R5) is the 10-01 #6 v1 gate, not exp-33 (10-03). No dedicated public row for exp-33. One seed, under-powered.

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-010] 2026-10-02 · Strategy memo: Android-only, three fronts (knowledge into the 4B's context; device truth + reader; held-out bench + claim); stop iPhone/1.5B quality work, perso · why: measured gap; only the 4B near the bar. · status: kept
- [D-012] 2026-10-02 · Close the knowledge-pack front for the bounty after the big-pack gate failed replay ("no fourth pack iteration") · why: kill rule K1 pre-registered in the strategy memo. · status: superseded (packs reopened later only for the deep tier and as products)
- [D-029] 2026-10-03 · Park the retrieval line after rv2 failed despite more gold in context · why: gold-sentence-in-context did not translate into judged quality. · status: superseded (retrieval reopened later only for the deep tier)
- [D-037] 2026-10-06 · Treat v0.2 as burnt (dev); a final number needs v0.3 written outside the Claude family · why: plaintext in private git history + 4 runs + a targeted fix. · status: kept
- [D-039] 2026-10-06 · Stop answer-identical 4B arms; reopen the deep tier as the primary quality lever · why: 15 arms, 0 ratio movement. · status: kept
- [D-073] 2026-10-11 · Negative results relabelled "not detected at MDE x (n, seeds)" when under-powered · why: "closed" overstated weak negatives. · status: kept

<!-- lint:exempt:end -->
### Events cited {#events}

<!-- lint:exempt:start -->
- [E-027] 2026-10-02 04:30 · Longer-answer persona makes the 4B hallucinate (Δ −0.044, confident-wrong 10 → 20)

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
