# 1 · The question

> Closed record · research record 1.0 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/question/ · Markdown twin: https://r4topunk.github.io/boar-research/research/question.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-09-17 → 09-30

**In one sentence.** "Half as good as the internet plus a frontier AI" sounds like a goal; it is really a measurement problem, and the first finding was that nobody had a ruler for it.

## For curious readers {#curious}

#### A phone in airplane mode

Imagine you are on a mountain, on a long flight, or somewhere the network is down. You still have questions: what is this plant, how far is the next town, what does this error mean. BOAR keeps a small AI model and a few downloaded libraries on your phone and answers from them, with sources.

#### The bounty's rules

The challenge had strict limits: an Android phone with at most 12 GB of memory, at most 50 GB of downloaded files, fully offline, open source. And one target: "more than 50 % as good as internet search plus a frontier AI." Winning is decided by a public confirmation, not by a score.

#### Half as good as what, exactly?

That sentence hides a research problem. Half of what? Measured how, on which questions, on which phone? If you grade a student's essay against a professor's, "half as good" depends on who grades and what counts. Before improving anything, we had to build a way to measure that we could trust.

#### Where we started

When the author joined the project, the app ran a small 1.5-billion-parameter model over about 1,300 Wikipedia paragraphs. A review called it "solid engineering, weak research": good code, but nobody knew how good the answers were.

**In one sentence card:** "The goal was simple to say and hard to measure, so the first job was building the ruler." No number.

*Facts: [F-682] [D-014] [E-003]*

## For tech people {#tech}

### The spec: Android, ≤ 12 GB RAM, ≤ 50 GB, offline, half as good

The bounty fixes the hardware envelope and leaves the quality target vague. Hard limits: Android or GrapheneOS, at most 12 GB of RAM, at most 50 GB of assets, fully offline, no Play Services, public source. Target: "more than 50 % as good as internet search plus a frontier AI" on explanation, comparison, synthesis and reasoning questions, in English. We treated the envelope as a budget and the target as a measurement problem: before touching the engine we built a desktop runner that executes the app's real TypeScript answer engine, and a judge that compares every answer with a frozen frontier-plus-web reference.

**Callout:** "Pre-harness numbers (an older 61-question set, 0.26 → 0.48, a 1.5B model on an iPhone) used a different instrument and are not comparable to anything below."

*Facts: [F-682] [F-071] [F-995] [D-035] [F-063]*

## For AI professionals {#ai}

### The record for this chapter

**Key facts:**
- The bounty envelope: Android or GrapheneOS, ≤ 12 GB RAM, ≤ 50 GB assets, fully offline, no Play Services, public repo [F-682] [F-071].
- Winning is a public confirmation, not a numeric benchmark [D-014].
- The existing app at the start: a 1.5B default model and about 1,300 Wikipedia paragraphs; review verdict "solid engineering, weak research" [E-003].
- Pre-harness overnight tuning: an older 61-question set went 0.26 → 0.48 [F-063]. **Different instrument, model, phone and set: never on the same axis as later numbers.**
- Early MoE probe: a 35B model took 40–58 s to first token on CPU [F-058].

**Key decisions:** [D-001] (thesis: quality per second + blind evaluation against a frontier model; stay on the existing app).

**Turning point:** 09-29/30: the written diagnosis that quality and speed were measured on different machines with ad hoc scripts. Fixing the instrument comes before fixing the app.

### Abstract

This is the closed record (version 1.0, as of 2026-10-28; research lines closed 2026-10-23) of a five-week attempt to build an offline Android research assistant that is "more than 50 % as good as internet search plus a frontier AI", under a ≤ 12 GB RAM, ≤ 50 GB storage envelope (poidh bounty #31). Quality was first measured pairwise against frozen references written by Claude Opus with web search, judged by Claude Opus in both presentation orders on a 1–5 rubric, and reported as a raw ratio, a floor-adjusted ratio that removes the rubric minimum, and win/tie/loss; every deciding criterion was hashed before its run and held-out exposure was logged per touch. On a bounty-style set held out at run time (V-para, n = 51, two seeds) the frozen 4B build scores raw 0.413 (0.384–0.445), floor-adjusted 0.261 (0.224–0.300), and wins 0 of 51; a 35B mixture-of-experts with a 512-token thinking budget reaches floor-adjusted 0.436 (0.401–0.472) on development data, desktop only, 0 wins, and was not delivered. A cross-family judge raises all levels by ≈ 0.10 while preserving the ranking and a near-zero win-rate. Phone constraints then made a 1.7B model the main 8 GB engine (the 4B leads it by +0.109 under Opus on development data). A second ruler (75 items, half written by each judge family, frozen before any answer; U-total with a zero for non-answers; verdict = lower of two families) has been run on the desktop twin of the submitted app's pre-rename engine (one seed): 0 of 71 wins under both families and a lower-family U-total of 0.164 (0.123–0.206), below the 0.50 bar; we report it as history, because the headline is the same ruler run on the phone with the shipped app under a criterion frozen before generation, which landed on 2026-10-25: 0 of 71 wins under both families, U-total 0.165 (0.127–0.205) under Claude Opus and 0.242 (0.194–0.296) under OpenAI gpt-5.6-sol, two seeds, below the 0.50 bar. Our thesis is a design statement: small models need external knowledge, so we built a harness around a small model's real capabilities (health gate, code-computed arithmetic, pack search and delivery, a short answer style, a fixed check-the-source line, refusals). Its evidence and limits come from closing tests on pack-written self-tests: with the item's own article delivered, the 1.7B is right on 65 % of items vs 28 % otherwise (Claude Haiku outcome labels, one seed), delivery succeeds on 54 %, no pack reaches 0.75, and on real development items delivery does not separate answer quality. As of 2026-10-25, under the Claude judge, the 0.50 bar was not reached on the earlier held-out sets, and no unexposed held-out number exists. The submitted app, LabRat (formerly BoarLite), runs offline on an 8 GB phone; one search change in it was merged although its pre-registered safety criterion failed by the letter, under a trade-off its author accepted in advance, and we report both. We release the benchmark and judge with every evaluation set (the retired held-out sets and the second ruler's items and references, published 2026-10-27), the raw run traces, a registry of negative results, openly licensed knowledge packs and a phone-parity study.

*Old scale (judge.v1 ratio), as of 2026-10-28; unchanged since the claim runs*

| | V-para (51) | v0.2 (110) |
|---|---|---|
| status at run time / now | held-out (4B runs) / dev-style | held-out / burnt → dev |
| 4B claim build, Opus, 2 seeds | raw 0.413 (0.384–0.445) · floor 0.261 (0.224–0.300) · 0/0/51 | raw 0.512 (0.478–0.549) · floor 0.388 (0.346–0.434) · 0/0/110, 0/1/109 |
| deep + think 512, Opus | raw 0.553 (0.524–0.581) · floor 0.436 (0.401–0.472) · 0/0/51 (2 seeds, dev-style) | raw 0.608 (0.575–0.641) · floor 0.508 (0.467–0.550) · 0/1/109 (1 seed, dev) |
| same, cross-family judge (post-hoc) | raw 0.667 (0.621–0.711) · floor 0.577 (0.519–0.632) · win 0.00–0.01 | raw 0.714 (0.666–0.759) · floor 0.639 (0.579–0.695) · win 6.4 % |

*Closing tests and the second ruler, as of 2026-10-28; outcome labels are shares, not ratios; never compare with box A*

| quantity | value | badge |
|---|---|---|
| correct-any with vs without the matching pack | 0.48 vs 0.26 (+0.23, +0.16…+0.31) | 180 pack-written self-tests, 9 packs, 1.7B Succinct, seed 42, Claude Haiku labels, desktop twin, dev [F-1704] |
| correct-any when the own article is kept vs not | 0.65 (n 98) vs 0.28; kept 54 % (article level) | same [F-1705] [F-1706] |
| packs at the 0.75 bar | 0 of 9 (best 0.60, worst 0.25) | same, n 20 per pack [F-1707] |
| undelivered facts already in the kit | 44 of 50 | MAIN 92 keyed, 0-LLM [F-2100] |
| shipped style on ENGINE-RC | correct-any 0.43, wrong-unwarned 0.12 (pack on) | UXMATRIX 60, seed 42, Haiku labels [F-1727] |
| bench v0.4 (U-total) | frozen 2026-10-20; references 75/75 per family; final run on BoarLite b4ef94f3 (desktop twin, one seed; history): win-rate 0 of 71 both families; U-total Claude 0.164 (0.123–0.208), gpt-5.6-sol 0.245 (0.194–0.300), minimum 0.164 (0.123–0.206), below the 0.50 bar; not a measurement of LabRat 7788924a (persona line added after it); on-phone DEVICE-FINAL landed 2026-10-25 (the headline; 0 of 71 wins, below the 0.50 bar) | [F-2070], [F-2212], [F-2214], [F-2215], [F-2225], [F-2227], OF-6, OF-8 |

*Facts: [F-017] [F-018] [F-490] [F-1208] [F-232] [F-023]*

### 1 Introduction: an underspecified target and a measurable one

The target phrase "more than 50 % as good as internet plus frontier AI" leaves the construct, the comparator, the question distribution and the judge unspecified. We operationalise it as a ratio of judged rubric scores between the system's answer and a frozen frontier-plus-web reference for the same question, on sets drawn to resemble the bounty's stated use (explanation, comparison, synthesis, reasoning). We make four contributions: (i) a public benchmark and pairwise judge with frozen references and a fail-closed pipeline; (ii) a pre-registered evaluation of a production-shaped offline system across seven frozen builds and a 35B deep tier; (iii) an analysis of the measuring instrument itself (rubric floor, seed versus judge noise, judge-family offset, reference length); (iv) a registry of negative results with power statements. We also document an unusual organisation: the work was coordinated and executed by AI agents under one human author, with independent AI reviewers in place of human sign-off.

*Facts: [F-682] [D-014] [D-008] [D-027]*

### 2 Related work

LLM-as-judge evaluation with pairwise comparison and order swapping; position and self-preference bias; reference-based vs reference-free judging; retrieval-augmented generation on device; mixture-of-experts inference with expert offloading/streaming; test-time compute ("thinking") budgets; pre-registration and multiplicity in ML evaluation. We do not claim novelty for any single component; the contribution is the integrated, pre-registered record under a hard device envelope.

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-017] A judge from a different model family scores everything higher on V-para, but keeps the ranking and the near-zero win-rate. 4B: raw 0.497 (0.449–0.547), floor-adjusted 0.361; deep + think 512: raw 0.667 (0.621–0.711), floor-adjusted 0.577 (0.519–0.632); deep − 4B +0.171 (+0.123…+0.219) vs +0.139 under Claude; per-item Spearman 0.88–0.92; win-rate 0.00–0.01 (judge.v1 ratio) · set V-para (dev-style, development data) · judge cross-family: OpenAI gpt-5.6-sol (via the Codex CLI) (post-hoc, not pre-registered) · n 51 (408 judge calls) · seeds 2 · CI 95 % item bootstrap (4B floor-adjusted CI not in the sources read) · date 2026-10-16 · caveat: Post-hoc and not pre-registered; it is the only point above 0.50 floor-adjusted on V-para and exists only under the cross-family judge; the lower-judge rule keeps the Claude number as headline.
- [F-018] The cross-family judge on v0.2. 4B: raw 0.617 (0.567–0.666), floor-adjusted 0.517 (2 seeds); deep + think 512: raw 0.714 (0.666–0.759), floor-adjusted 0.639 (0.579–0.695) (1 seed); deep − 4B +0.097 vs +0.096 under Claude; Spearman 0.90–0.97; win-rate 2.7 % / 6.4 % vs 0 % under Claude (judge.v1 ratio) · set v0.2 (dev (burnt), development data) · judge cross-family: OpenAI gpt-5.6-sol (via the Codex CLI) (post-hoc, not pre-registered) · n 110 (660 judge calls) · seeds 4B 2, deep 1 · CI 95 % item bootstrap · date 2026-10-17 · caveat: Post-hoc. The Claude judge is the stricter family by ≈ 0.10 on both sets; the offset is stable across sets and arms.
- [F-023] On a real 12 GB-class phone, in airplane mode, the frozen build gives the same judged quality as on the desktop. phone raw 0.529 (0.481–0.575) vs desktop 0.529; floor-adjusted 0.403 vs 0.402; paired −0.000 (−0.026…+0.028); 72/72 answered; fast-tier p50 30.7 s; app memory (PSS) peak 5.88 GB during model load, then ≤ 4.23 GB (judge.v1 ratio) · set v0.1 (public dev, development data) · judge Claude Haiku 5.5-low (L1 triage judge, N = 4, both orders) · n 57 · seeds 1 run · CI paired 95 % bootstrap · date 2026-10-14 · caveat: Haiku-judged level; not comparable with Opus-judged ratios. The device has 10.7 GiB usable RAM.
- [F-058] Earlier MoE probe: Qwen3.6-35B took 40–58 s to first token; CPU prefill was the limit. 40–58 s · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-09-29 · caveat: pre-harness desktop/phone mix
- [F-063] Before the harness, an overnight on-phone session lifted the old 61-question bounty-style score from 0.26 to 0.48. 0.26 → 0.48 · set old "v2" 61 items, BOAR's own dev set (dev, development data) · judge Claude judge, both orders vs Opus+web · n 2 · seeds UNKNOWN · CI CI 0.42–0.56, replicated in 2 runs · date 2026-09-30 · caveat: different instrument, model (1.5B), phone and set; NOT comparable to later v0.1/v0.2/V-para numbers
- [F-071] The bounty's hardware envelope. ≤ 12 GB RAM, ≤ 50 GB total storage, offline, no Play Services, GrapheneOS-compatible · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-02 · caveat: GrapheneOS not yet run on hardware
- [F-232] The Claude judge is the stricter family by ≈ 0.10 raw on both sets. offset +0.08…+0.11 raw (+0.08/+0.115 V-para) (judge.v1 ratio) · set V-para, v0.2 (status UNKNOWN) · judge UNKNOWN · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-17 · caveat: ranking unchanged
- [F-490] Paired deep − 4B on v0.2 is identical under both judges. +0.097 (+0.053…+0.142) vs Claude +0.096 (+0.062…+0.131) · set v0.2 dev (dev, development data) · judge both · n 110 (inferred from set) · seeds UNKNOWN · CI (+0.053…+0.142) / (+0.062…+0.131) · date 2026-10-17 · caveat: Spearman 0.90–0.97 | on V-para +0.171 vs +0.139
- [F-682] Bounty hard limits: Android/GrapheneOS, ≤ 12 GB RAM, ≤ 50 GB assets, fully offline, no Play Services, public repo. · set n/a · judge n/a · date 2026-10-02 · caveat: requirements text, not BOAR's
- [F-995] The original kit size. 3.03 GB including the 2.5 GB model; packs ≈ 0.39 GB · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-05
- [F-1208] Win-rate under the cross-family judge on v0.2. 4B 2.7 %, deep 6.4 % (Claude 0 %) · set v0.2 dev (dev, development data) · judge cross-family (post-hoc, different judge family) · n 110 · seeds UNKNOWN · CI n 110 · date 2026-10-17
- [F-1704] PACKPROOF pooled correct-any with pack installed vs without. 0.48 vs 0.26, Δ +0.23 (outcome-label share) · set 180 pack self-tests (written from the packs), dev (dev (pack-written self-tests), development data) · judge Claude Haiku 5.5-low labels; correct-any · n 180 · seeds 42 · CI CI +0.16..+0.31; n 180; seed 42 · date 2026-10-23 · caveat: self-tests favour the pack; hosts differ by arm; 1 seed Metric: outcome-label shares of n items (Claude Haiku 5.5-low labels, UXMATRIX protocol); not the judge.v1 ratio.
- [F-1705] Correct-any when own article is kept vs not. 0.65 (n 98) vs 0.28 (outcome-label share) · set 180 pack self-tests (written from the packs), dev (development data) · judge Claude Haiku labels · n 180 · seeds UNKNOWN · CI n 180 · date 2026-10-23 · caveat: "about 2 in 3 when delivered" | 'kept' = own article kept (article level), between-item split, n 98 kept.
- [F-1706] Own article delivered (kept) 54 % ; cited 28 % · set 180 pack self-tests (written from the packs), dev (development data) · judge 0-LLM funnel · n 180 · seeds UNKNOWN · CI n 180 · date 2026-10-23 · caveat: delivery = bottleneck | 'kept' here is article-level (own article in the kept list), not the chunk-level delivery used for MAIN facts since 10-22 ; do not mix with the 42/92 chunk-level count.
- [F-1707] Packs reaching the 0.75 "proves" bar. 0 of 9; 7 below 0.60 (not default-eligible by rule); best 0.60 (two Q&A packs), worst factbook 0.25 · set 180 pack self-tests (written from the packs), dev (development data) · judge Claude Haiku · n 20 · seeds UNKNOWN · CI n 20 per pack · date 2026-10-23 · caveat: health packs AI-reviewed, not clinically reviewed AI-reviewed, not clinically reviewed.
- [F-1727] Succinct on ENGINE-RC (page numbers) ON CWS 0.30, correct-any 0.43, WU 0.12; OFF correct-any 0.22, WU 0.10 (outcome-label share) · set UXMATRIX 60, dev (dev, development data) · judge Claude Haiku labels · n 60 · seeds 42 · CI n 60; seed 42 · date 2026-10-24 · caveat: PASS vs frozen CWS ≥0.28, WU OFF ≤0.10 Metric: outcome-label shares of n items (Claude Haiku 5.5-low labels, UXMATRIX protocol); not the judge.v1 ratio.
- [F-2070] Bench v0.4 frozen. 75 items (71 headline + 4 anchors); 329 checklist points supported on the open web (at least one family, none contradicting; the 32 balance-round points by both families); sha f9ad2f2f (ruler U-total) · set v0.4 (held-out ruler) (held-out ruler (v0.4; exposed to two engines 2026-10-24)) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-20 · caveat: written by Claude + OpenAI gpt-5.6-sol (the judge families)
- [F-2100] Undelivered facts are a search problem. 44 of 50 already in the K13 kit · set dev (dev, development data) · judge 0 LLM · n UNKNOWN · seeds UNKNOWN · CI 50 items · date 2026-10-23
- [F-2212] REFS-V2, OpenAI gpt-5.6-sol half complete: 75 of 75 v0.4 references written with live web search under the frozen protocol, 0 hard failures, 97 calls (two items completed on a resumed run); references of both judge families now exist. 75 / 75; 0 hard failures · set v0.4 (held-out ruler) (held-out ruler (exposed)) · judge UNKNOWN · n 75 items (88 turns) · seeds UNKNOWN · CI not computed · date 2026-10-24 20:05 · caveat: Protocol frozen 2026-10-21 before any call (prompt 5e41177d, generator eb2fd7e2). Reference text not read by the coordinator.
- [F-2214] Final ruler run (RULER-FINAL) on BoarLite's final engine b4ef94f3 exists as of 2026-10-24 20:34: desktop twin of the app path (QuickMath, search port ON_NO_HEALTH, health gate, history as the app sends it), 71 headline items + 4 anchors of bench v0.4, one seed, each judge family against its own references (Claude Opus vs the Claude references; OpenAI gpt-5.6-sol vs its references), 150 + 150 judge calls, addendum frozen before any generation; its numbers were held until the author's publication decision of 2026-10-25 (now public as F-2215 and F-2217; history, the headline is DEVICE-FINAL) · set v0.4 (held-out ruler; exposed) (held-out ruler (v0.4; now exposed to three engines)) · judge Claude Opus + OpenAI gpt-5.6-sol (each vs its own references) · date 2026-10-24 20:34 · caveat: Deviations from the spec: one seed (spec: two; the author's choice), one reference family per judge family, stage 1 (DECLINE2STAGE) not run, no errata, desktop twin not the APK on a phone (the spec labels desktop-twin numbers dev/parity evidence). v0.4 is the claim set: no tuning after this run.
- [F-2215] RULER-FINAL U-total of BoarLite b4ef94f3 on v0.4: Claude family 0.164 (0.123-0.208), OpenAI gpt-5.6-sol family 0.245 (0.194-0.300); minimum over families 0.164 (0.123-0.206); win-rate 0 of 71 (Claude) and 0 of 71 with 1 tie (gpt-5.6-sol); fixed-text refusals on 3 items. Claude 0.164; gpt-5.6-sol 0.245; min 0.164; win-rate 0 (ruler U-total) · set v0.4 (held-out ruler; exposed) (held-out ruler (v0.4; exposed)) · judge Claude Opus + OpenAI gpt-5.6-sol (each vs its own references) · n 71 headline items · seeds 1 (42) · CI Claude 0.123-0.208; gpt-5.6-sol 0.194-0.300; min 0.123-0.206 · date 2026-10-24 20:34 · caveat: Metric: ruler v0.4 U-total (71 headline items, health weight 0.5); never on one axis with the judge.v1 ratio or outcome labels. Desktop twin, one seed. Published by the author's decision of 2026-10-25 (AD-15 (b)): BoarLite/LabRat is the author's own submission. History, not the headline: desktop twin of engine b4ef94f3, one seed, before the Rat persona line and the cleanup (F-2223, F-2225); not a measurement of LabRat 7788924a. The headline is the on-phone run DEVICE-FINAL (OF-8).
- [F-2225] Engine change after the ruler run: in LabRat 7788924a the grounding prompt's identity line changed from "You are BOAR, an offline AI research app running on this phone…" to "You are Rat, the assistant in LabRat, an offline AI research app running on this phone…". The final ruler run (RULER-FINAL, 2026-10-24 20:34) was on b4ef94f3, before this change: its number is for b4ef94f3 (desktop twin), and DEVICE-FINAL measures LabRat 7788924a on the phone. persona line changed after RULER-FINAL · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-25 02:20 · caveat: The final ruler number (RULER-FINAL) measures engine b4ef94f3 on its desktop twin; LabRat 7788924a adds the Rat persona line to the grounding prompt after that run, so the ruler number is not a measurement of LabRat 7788924a.
- [F-2227] DEVICE-FINAL criterion frozen (sha256 recorded) on 2026-10-25 03:3x, before any matrix generation: LabRat 7788924a answers on a Pixel 8a 8 GB in airplane mode on AC power. Matrix: M1 ruler v0.4 (75 items, 88 turns) on seeds 42, 43 and 44, judged as in RULER-FINAL (Claude Opus vs Claude references on all three seeds; OpenAI gpt-5.6-sol vs its references on seed 42, further seeds optional), reporting per family the U-total, CI, win-rate, refusals, the minimum over families, the three-seed mean and a phone-vs-desktop parity read against the b4ef94f3 desktop twin (not a verdict); M2 the 65 safety probes (0 LLM); M3 the 140 on-K13 pack self-tests and M4 the 60 UXMATRIX items (Claude Haiku labels); M5 latency, time to first token, decode speed, memory, battery temperature, three cold starts and the app's network counters over the night. Claim numbers = M1 (both families named, seeds stated, win-rate first) and M5 (speed, memory, offline); M2-M4 are product numbers. No tuning, no engine change. matrix M1-M5; claim numbers = M1 + M5 (ruler U-total) · set bench v0.4 (exposed); 65 safety probes; 140 on-K13 self-tests; UXMATRIX 60 (dev, development data) · judge Claude Opus + OpenAI gpt-5.6-sol (M1); Claude Haiku 5.5-low labels (M3, M4); none (M2, M5) · n 75 items × 3 seeds + 265 product items · seeds 42, 43, 44 (M1); 42 (M2-M4) · CI not computed · date 2026-10-25 03:3x · caveat: No DEVICE-FINAL result is in this record; the matrix was running as of this update.

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-001] 2026-09-26 · Thesis: "quality per second + blind evaluation against a frontier model"; stay on the existing cross-platform app; plan a no-network Android submission · why: the existing claim had solid engineering but no measured research quality. · status: kept
- [D-008] 2026-10-01 · Research agents work in fixed lanes, write one "technique card" per idea, never run experiments or touch the product; only the coordinator queues runs · why: Avoid duplicate work; separate proposing from measuring. · status: kept
- [D-014] 2026-10-02 · Treat the bounty as qualitative: judged by a public confirmation, not a numeric benchmark · why: bounty text. · status: kept
- [D-027] 2026-10-03 · No human review: an independent Opus reviewer agent decides content/wording; caveat "AI-reviewed, not clinically reviewed" stays · why: speed; author unavailable for 39 card decisions. · status: kept
- [D-035] 2026-10-05 · Bench APK with INTERNET permission removed (no-network by construction) · why: prove offline operation statically. · status: kept

<!-- lint:exempt:end -->
### Events cited {#events}

<!-- lint:exempt:start -->
- [E-003] 2026-09-26 · Author does a read-only review of the app maintainer's existing bounty claim (#124): "solid engineering, weak research"; default Qwen2.5-1.5B + ~1,300 Wikipedia paragraphs; biggest lever named = large streamed MoE + full Wikipedia

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
