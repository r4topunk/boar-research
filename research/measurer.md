# 10 · Measuring the measurer

> Closed record · research record 1.1.2 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/measurer/ · Markdown twin: https://r4topunk.github.io/boar-research/research/measurer.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-10-02 → 10-21

**In one sentence.** Claude wrote the questions, wrote the references and judged them, so the project measured its own instrument: judge noise is tiny, seed noise is not, and a judge from another company scores everything about 0.10 higher while keeping the same ranking and a near-zero win-rate.

## For curious readers {#curious}

#### Claude graded Claude

One AI family wrote the test questions, wrote the reference answers and did the grading. That is a known risk: a judge may prefer answers that sound like itself.

#### A judge from another company

So we re-graded the same answers with a judge from another AI company, using the same rules. It scored everything about 0.10 higher. It kept the same order of who is better. And it still almost never preferred our answer over the frontier one.

*Badge:* V-para and v0.2 · cross-family judge (an OpenAI model) · graded after the fact, not planned in advance.

#### We keep the stricter one

Under the other judge, the big model with thinking crosses 0.50 on the honest scale. We do not headline that. Our rule, written before we had the number, says that when two judges disagree, the lower one is the headline.

#### Luck of the draw

Re-grading identical answers barely changes anything. Re-generating answers with a different random seed changes the score by about 0.02, sometimes 0.04. That is why important numbers use two runs.

**In one sentence card:** "A different judge changes the level, not the ranking, and not the wins."

*Facts: [F-017] [F-018] [F-490] [F-1208] [F-232] [D-122] [F-019] [F-020]*

## For AI professionals {#ai}

### The record for this chapter

**Key facts:**
- Second Claude judge (Fable 5.1): same winner 453/456 [F-1142].
- Haiku 5.5-low vs Opus on v0.1: r 0.922, κ 0.651, ratio −0.069 (lead with these; "same winner 54/57" is near-uninformative because the reference wins ≈ 100 % of items) ([F-996] OVERCLAIM note).
- Local open-weights judge (Gemma 4 26B): +0.11 lenient, κ 0.32/0.55, same ranking ([F-164], -47).
- Opus test-retest: σ ≈ 0.003 raw; per-item r 0.96; winner 51/51 [F-019].
- Seed noise: SD 0.020 raw / 0.025 floor on the deep tier; two seeds differ −0.039 (−0.072…−0.011) ([F-012], -34).
- Reference length: shortening references to ≤ 80 words moves H floor-adj 0.412 → 0.514 (s42); ≈ 17 % of the gap is length, ≈ 83 % substance [F-467].
- Correctness alone: H floor-adj 0.660 (0.608–0.712) on V-para; completeness 0.301, usefulness 0.341 [F-284].
- Cross-family judge (post-hoc, 408 + 660 calls, same rubric, orders and blinding): V-para 4B raw 0.497 / floor 0.361; H raw 0.667 / floor 0.577 (0.519–0.632); win-rate 0.00–0.01. v0.2: 4B 0.617 / 0.517 (2 seeds); H 0.714 / 0.639 (1 seed); deep − 4B gap +0.097 vs Claude +0.096; win-rate 2.7 % / 6.4 % vs 0 % [F-017] [F-017] [F-017] [F-018] [F-018] [F-490] [F-1208] [F-232].
- Outside critique: numbers real (15/17 re-derive), internal summaries overstated; 7 re-wordings applied [F-227] [D-113].
- Later calibration (10-20/21, dev): Haiku and Opus agree on confident errors (κ 0.75) far better than on "correct" (κ 0.49; 0.22 on warned answers); Opus finds 98 correct answers Haiku misses vs 10 the other way, so Haiku-only correctness rates are low-biased [F-2083] [F-1432]. judge.v1 gives a bare refusal U 0.058 (0.037–0.081), not zero [F-2081]: the reason the second ruler adds a stage-1 zero (chapter 12).

**Key decisions:** / (hold the cross-family pilot; done later with OpenAI gpt-5.6-sol via the Codex CLI), [D-049] (Haiku as L1), [D-050] (open judge for ranking only), [D-057] (near-miss rule), [D-072] (common-mode CI), [D-122] / [D-115] (lower judge is the headline; family named next to every ratio).

**Turning point:** 2026-10-16 19:01, the cross-family judge: the deep tier crosses 0.50 floor-adjusted only under the other family, and the win-rate does not move.

### 7.1 One family wrote, referenced and judged: what changes under another

Items (v0.2, V-para), references and the judge all come from the Claude family. We ran four checks. A second Claude judge (Fable 5.1) agrees with Opus on 453/456 verdicts. Haiku 5.5-low tracks Opus on v0.1 with r = 0.922, κ = 0.651 and a −0.069 level offset (agreement on the winner, 54/57, is near-uninformative because the reference wins almost every item) and compresses paired gaps to 0.70–0.95× of Opus's on pack arms and as low as 0.25× on one 4B-vs-deep pair. A local Gemma 4 26B judge is +0.11 lenient (κ 0.32/0.55) but preserves the deep − 4B ranking (+0.026 vs +0.029). Post hoc, the author re-judged existing traces with an OpenAI model using the same rubric, orders and blinding (408 calls on V-para, 660 on v0.2). It scores every configuration higher: on V-para the 4B rises from 0.413 / 0.261 to 0.497 / 0.361 and the 512 configuration from 0.553 / 0.436 to 0.667 / 0.577 (0.519–0.632); on v0.2 the 4B rises to 0.617 / 0.517 (two seeds) and the deep configuration to 0.714 / 0.639 (0.579–0.695) (one seed). The deep − 4B gap is preserved (V-para +0.171 vs +0.139; v0.2 +0.097 vs +0.096), per-item Spearman is 0.88–0.97, and win-rate stays near zero (V-para 0.00–0.01; v0.2 2.7 % and 6.4 % vs 0 %). Per the analysis plan, when two families differ by more than 0.05 raw the lower is the headline; we report the Claude numbers as headline and the cross-family numbers beside them.

**Caveat line under the figure:** "Cross-family runs were not pre-registered; their reports live with the held-out data and were not opened by the authors of this page; CIs for the 4B floor-adjusted cells were not available."

*Facts: [F-1142] [F-996] [F-1153] [F-1187] [F-164] [F-583] [F-017] [F-018] [F-490] [F-1208] [F-232]*

### Noise budget

Re-judging unchanged answers with Opus gives σ_judge ≈ 0.003 raw (per-item r = 0.96; winner 51/51). Re-generating answers is the dominant noise: on the deep tier, seeds 42/43/44 give raw 0.533 / 0.572 / 0.544 (SD 0.020; floor-adjusted SD 0.025), and two seeds of the same configuration differ by −0.039 (−0.072…−0.011), a CI excluding zero. The 4B on V-para is seed-stable (identical ratios across seeds; per-item r = 0.81), and the desktop 4B path is byte-deterministic on a fixed host (20/20). A single 20-item Haiku pass carries ±0.03–0.04 of judge noise, about the size of the decision threshold, so slices screen for futility only; "hardest-20" slices inflated deltas 3–10× and were retired. The house reading rule is that a one-seed deep-tier Δ on V-para below 0.05 is seed noise (raised from 0.03 on 2026-10-16).

*Facts: [F-019] [F-012] [F-020] [F-618] [F-463] [F-476] [F-1166] [F-184] [F-199] [F-1195] [D-058]*

### Multiplicity and selection

Across ≈ 60 judged comparisons, ≈ 1.5 false "CI low > 0" results are expected at α = 0.05; the large levers survive a Bonferroni-style correction (X2b z ≈ 5.5, LITE5 z ≈ 6, thinking z ≈ 4.2). The larger risk is selection on the same development sets (winner's curse on the deep configuration; levers designed on the 180 self-tests), which is why development and held-out readings are separated throughout.

*Facts: [F-1079] [F-1078]*

### Two judges on labels, refusals and correctness (2026-10-20/21)

On double-labelled development units Haiku and Opus agree on confident errors (κ 0.75) far better than on "correct" (κ 0.49; 0.22 on warned answers); Opus finds 98 correct answers that Haiku misses vs 10 the other way, a +0.02 U shift [F-2083]. A Haiku confident-error count moves by about ± 1.3 per 100 on retest of identical answers. judge.v1 gives non-answers a positive score (bare refusal 0.058, hedge 0.053, fluent no-content 0.016; [F-2081]), and attempts to fix this inside the rubric flipped 5–7 of 40 confident-error verdicts [F-1955], hence the stage-1 zero of §3.6. Reference draws matter little: two uncapped Opus draws move U by ≤ 0.015 [F-2114]. Same-family judge lift in the literature is 3.4–8.4 points for open-model families and untested for Claude and GPT [F-2115].

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-012] Three seeds of the recommended deep configuration show how much one run can move. raw mean 0.550, SD 0.020 (0.533 / 0.572 / 0.544); floor-adjusted mean 0.432, SD 0.025 (0.412 / 0.460 / 0.425); 0 wins each seed (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 3 (42–44) · CI pooled CI UNKNOWN (aggregate file empty) · date 2026-10-10
- [F-017] A judge from a different model family scores everything higher on V-para, but keeps the ranking and the near-zero win-rate. 4B: raw 0.497 (0.449–0.547), floor-adjusted 0.361; deep + think 512: raw 0.667 (0.621–0.711), floor-adjusted 0.577 (0.519–0.632); deep − 4B +0.171 (+0.123…+0.219) vs +0.139 under Claude; per-item Spearman 0.88–0.92; win-rate 0.00–0.01 (judge.v1 ratio) · set V-para (dev-style, development data) · judge cross-family: OpenAI gpt-5.6-sol (via the Codex CLI) (post-hoc, not pre-registered) · n 51 (408 judge calls) · seeds 2 · CI 95 % item bootstrap (4B floor-adjusted CI not in the sources read) · date 2026-10-16 · caveat: Post-hoc and not pre-registered; it is the only point above 0.50 floor-adjusted on V-para and exists only under the cross-family judge; the lower-judge rule keeps the Claude number as headline.
- [F-018] The cross-family judge on v0.2. 4B: raw 0.617 (0.567–0.666), floor-adjusted 0.517 (2 seeds); deep + think 512: raw 0.714 (0.666–0.759), floor-adjusted 0.639 (0.579–0.695) (1 seed); deep − 4B +0.097 vs +0.096 under Claude; Spearman 0.90–0.97; win-rate 2.7 % / 6.4 % vs 0 % under Claude (judge.v1 ratio) · set v0.2 (dev (burnt), development data) · judge cross-family: OpenAI gpt-5.6-sol (via the Codex CLI) (post-hoc, not pre-registered) · n 110 (660 judge calls) · seeds 4B 2, deep 1 · CI 95 % item bootstrap · date 2026-10-17 · caveat: Post-hoc. The Claude judge is the stricter family by ≈ 0.10 on both sets; the offset is stable across sets and arms.
- [F-019] Re-judging the exact same answers barely moves the score: judge noise is negligible next to seed noise. σ_judge ≈ 0.003 raw / 0.004 floor-adjusted; per-item r 0.96; same winner 51/51 (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 (102 Opus calls) · seeds 1 (re-judge of s42) · CI n 51; 102 calls · date 2026-10-11
- [F-020] Seed noise: the same deep configuration run with two random seeds differs by more than many tested "levers". s42 vs s43, same configuration: Δ −0.039 (−0.072…−0.011) raw; house rule since 2026-10-16: a one-seed deep-tier Δ below 0.05 on V-para is seed noise (raised from 0.03) (judge.v1 ratio) · set V-para (dev-style, development data) · judge Claude Opus (judge.v1, both orders) · n 51 · seeds 2 · CI paired 95 % bootstrap · date 2026-10-16 · caveat: The public boar-research README.md:77 still says 0.03.
- [F-164] Local Gemma 4 26B judge: same winner as Opus 49/57 and 50/57, κ 0.32 / 0.55, ratio +0.110 / +0.112 above Opus, 41-43 s/call. +0.11 (judge.v1 ratio) · set v0.1 dev (dev, development data) · judge Gemma vs Opus · n UNKNOWN · seeds UNKNOWN · CI 228 calls, 2 legs · date 2026-10-07
- [F-184] "20 hardest" slices inflated deltas: +0.091 slice vs +0.026 full (THINK4B); +0.089 vs +0.009 (THINK4B-V02). inflation ×3-10 · set dev (dev, development data) · judge Opus/Haiku · n 20 · seeds UNKNOWN · CI n 20 vs 51/110 · date 2026-10-10
- [F-199] A 20-item random slice has SE ≈ 0.04-0.05: it only screens for futility. SE 0.04-0.05 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n 20 · seeds UNKNOWN · CI n 20 · date 2026-10-11
- [F-227] Critique: most traced numbers re-derive. 15/17 numbers, 16/17 criterion hashes match · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-16
- [F-232] The Claude judge is the stricter family by ≈ 0.10 raw on both sets. offset +0.08…+0.11 raw (+0.08/+0.115 V-para) (judge.v1 ratio) · set V-para, v0.2 (status UNKNOWN) · judge UNKNOWN · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-17 · caveat: ranking unchanged
- [F-284] On correctness alone H is above 0.50 floor-adj; the gap is in completeness and usefulness. V-para correctness floor-adj 0.660 (0.608–0.712) vs completeness 0.301 / usefulness 0.341 · set V-para dev (dev, development data) · judge Opus · n 51 (inferred from set) · seeds 2 · CI 2 seeds · date 2026-10-10 · caveat: "correct but thin" also describes an always-decline system on those dims; not a bar reading
- [F-463] The 4B's two seeds on V-para give identical ratios (Δ 0.000, −0.023…+0.023). 0.000 · set V-para (status UNKNOWN) · judge Opus · n 51 · seeds UNKNOWN · CI n 51 · date 2026-10-10
- [F-467] Shortening references to ≤ 80 words lifts H floor-adj 0.412 → 0.514 and K 0.261 → 0.322. +0.102 (+0.068…+0.144) H; +0.060 K · set V-para dev, references altered (dev, development data) · judge Opus · n 51 (inferred from set) · seeds 1 · CI 1 seed (s42) · date 2026-10-10 · caveat: ≈ 17 % of H's gap is reference length, ≈ 83 % substance; not a bar reading
- [F-476] 4B generation on desktop CPU is byte-deterministic. 20/20 identical across 5 pairings · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-13 · caveat: citation fix (l.16 is the stack bullet)
- [F-490] Paired deep − 4B on v0.2 is identical under both judges. +0.097 (+0.053…+0.142) vs Claude +0.096 (+0.062…+0.131) · set v0.2 dev (dev, development data) · judge both · n 110 (inferred from set) · seeds UNKNOWN · CI (+0.053…+0.142) / (+0.062…+0.131) · date 2026-10-17 · caveat: Spearman 0.90–0.97 | on V-para +0.171 vs +0.139
- [F-583] The Gemma judge preserved the ranking: deep35 − 4B +0.026 vs Opus +0.029. +0.026 vs +0.029 · set v0.1 dev (dev, development data) · judge both · n 57 · seeds UNKNOWN · CI n 57 · date 2026-10-07 · caveat: neither CI excludes 0
- [F-618] Per-item seed agreement: deep thinking tier r 0.5-0.7 on V-para vs 0.81 for the 4B; on v0.2 the deep tier r 0.90. r · set V-para / v0.2 dev (dev, development data) · judge Opus · n 51 · seeds UNKNOWN · CI n 51 / 110 · date 2026-10-10
- [F-996] Haiku 5.5-low vs Opus on 57 v0.1 items: same winner 54/57, r 0.922, κ 0.651, ratio −0.069 lower, 3.52 s/call, 0 failures. 54/57 (judge.v1 ratio) · set v0.1 dev (dev, development data) · judge Haiku vs Opus · n 57, · seeds UNKNOWN · CI n 57, 228 calls · date 2026-10-07 · caveat: 'same winner 54/57' carries almost no information because the reference wins ≈ 100 % of items (CRITIQUE-2026-10-16.md:32); quote the informative statistics instead: r 0.922, κ 0.651, level −0.069, Haiku Δ ≈ 0.70-0.85× the Opus Δ on pack arms
- [F-1078] Multiplicity check. ≈ 60 judged comparisons → ≈ 1.5 false "CI low > 0" expected; X2b z ≈ 5.5 survives Bonferroni over 100 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-16 · caveat: main risk is selection on dev sets, not multiplicity
- [F-1079] Large levers survive multiplicity correction. X2b z ≈ 5.5, LITE5-180 z ≈ 6, DEEPTHINK z ≈ 4.2 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI ≈ 60 judged comparisons · date 2026-10-16 · caveat: citation fix; ≈ 60 judged comparisons, Bonferroni over 100; the bigger risk is selection on the same dev sets
- [F-1142] Second Claude judge (Fable 5.1) vs Opus: same winner 453/456 verdicts, Pearson r 0.939, κ (correctness ≥ 4) 0.894, ratio +0.004…+0.010. 453/456 (judge.v1 ratio) · set v0.1 dev (dev, development data) · judge Opus vs Fable · n UNKNOWN · seeds UNKNOWN · CI 456 verdicts · date 2026-10-02 · caveat: both judges are Claude: tests noise, not self-preference
- [F-1153] Haiku compresses paired gaps: deep35 − 4B was +0.007 under Haiku vs +0.029 under Opus (×0.25). +0.007 vs +0.029 · set v0.1 dev (dev, development data) · judge both · n 57 · seeds UNKNOWN · CI n 57 · date 2026-10-07 · caveat: review later measured ×0.6-1.0 on full deep sets, ×3-4 on hard slices
- [F-1166] On the 20 hardest items Haiku showed +0.029 where Opus gave +0.091; on the full set they agreed within 0.005 (+0.022 vs +0.026). ×3 compression on slice · set V-para dev (dev, development data) · judge both · n 20 · seeds UNKNOWN · CI n 20 / 51 · date 2026-10-10
- [F-1187] Haiku L1 compresses paired gaps vs Opus. Haiku Δ ≈ 0.70-0.95× the Opus Δ across six pack/retrieval arms (X1 0.70, pack 0.76, ONLY 0.83, X2b 0.85, ST2 0.88, ADD 0.95); per-item Δ r 0.75-0.84 · set 180 self-tests (status UNKNOWN) · judge Haiku vs Opus · n 180 (inferred from set) · seeds UNKNOWN · CI several arms · date 2026-10-14/16 · caveat: citation fix (critique row is l.32); '0.70-0.85' are the two quoted examples; on deep/4B slices compression ranged ×0.25 to a sign flip
- [F-1195] A single n=20 Haiku pass carries ±0.03–0.04 noise. per-item retest SD 0.22–0.28 rubric points · set dev (dev, development data) · judge Haiku · n 18 · seeds UNKNOWN · CI n 18–30 · date 2026-10-16 · caveat: citation fix (l.34 is the self-preference row) | at the MDE: n=20 labels are noise-level
- [F-1208] Win-rate under the cross-family judge on v0.2. 4B 2.7 %, deep 6.4 % (Claude 0 %) · set v0.2 dev (dev, development data) · judge cross-family (post-hoc, different judge family) · n 110 · seeds UNKNOWN · CI n 110 · date 2026-10-17
- [F-1432] Haiku vs Opus on confident-error labels. agree 39/47 (kappa 0.63); Haiku over-calls; Opus +0.106 more lenient on correctness · set dev (dev, development data) · judge UNKNOWN · n 47 · seeds UNKNOWN · CI n 47 · date 10-20
- [F-1955] JUDGE-V1_1 / V1_1B: Can one rule line make judge.v1 give declines a true zero? declines U 0.000, but CE flips 7/40 and 5/40; retest SD 0.0265/0.0295 vs 0.0206 (judge.v1 ratio) · set decline variants; 40 controls (status UNKNOWN) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-21 · caveat: criterion frozen: yes (bf560ea9; 6edbacf6); arm verdict: NO-ADOPT both
- [F-2081] judge.v1 does not give declines a true zero. bare refusal U 0.058 (0.037-0.081); hedge 0.053; fluent no-content 0.016 (judge.v1 ratio) · set dev (dev, development data) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI 30 v0.1 ids · date 2026-10-21 · caveat: leak in correctness dimension
- [F-2083] Haiku vs Opus calibration. κ CE 0.75, κ correct 0.49 (warned 0.22); Opus finds 98 correct Haiku misses vs 10 the other way; U shift +0.022 · set dev (dev, development data) · judge both · n UNKNOWN · seeds UNKNOWN · CI 1,911 units · date 2026-10-21
- [F-2114] Reference draw noise. two uncapped Opus draws move U ≤ 0.015 · set dev (dev, development data) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI 20 v0.1 · date 2026-10-21 · caveat: between-family variance unmeasured
- [F-2115] Same-family judge lift in the literature. 3.4-8.4 pp (open-model families; Claude/GPT not tested) · set external (external) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-21 · caveat: external paper, abstract only

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-049] 2026-10-07 · Haiku 5.5-low replaces Sonnet-low as L1 judge · why: same winner 54/57, 3.5 s/call, ~14× cheaper. · status: kept
- [D-050] 2026-10-07 · Local open-weights judge (Gemma 4 26B) allowed for triage/ranking only, never for the number · why: keeps ranking, +0.11 lenient, κ 0.32-0.55. · status: kept
- [D-057] 2026-10-10 · Near-miss rule: a Haiku Δ within 0.01 of a threshold triggers Opus on the same ids · why: Haiku compressed a +0.048 Opus gap to +0.027. · status: kept
- [D-058] 2026-10-10 · Seed-noise reading rule (V-para one-seed deep Δ < ~0.03 is noise; later raised to 0.05) · why: SEEDVAR three-seed spread. · status: superseded by D-113 (Threshold raised from 0.03 to 0.05 on 2026-10-16 after the outside critique (SEEDVAR showed a −0.039 gap between seeds).)
- [D-072] 2026-10-11 · Common-mode CIs for deep-tier rows: CI = Δ ± 1.96·sqrt(SE_item² + 2σ_run²) · why: item bootstrap ignores run-level seed noise. · status: kept
- [D-113] 2026-10-16 · Apply the adversarial critique: lite "= 4B" only on pack-matched dev; one-seed V-para noise rule 0.03 → 0.05; n≈20 closures relabelled "not detected at MDE 0.08 · why: over-stated internal summaries. · status: kept
- [D-115] 2026-10-16 · Claude judge stays the headline (lower of two judges); judge family named next to every ratio; win/tie/loss leads · why: analysis-plan rule: when judges differ by > 0.05, the lower is the headline. · status: kept
- [D-122] 2026-10-17 · When judges from two families disagree, the lower number is the headline; judge family named next to every ratio · why: XFAM offset ≈ +0.10. · status: kept

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
