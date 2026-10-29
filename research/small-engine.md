# 11 · A smaller engine for 8 GB phones

> Closed record · research record 1.1.2 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/small-engine/ · Markdown twin: https://r4topunk.github.io/boar-research/research/small-engine.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-10-18 → 10-21

**In one sentence.** On a real 8 GB phone the 4B was too slow and once killed by the operating system, so on 2026-10-20 the author made Qwen3-1.7B the main 8 GB engine, for latency and memory and explicitly not for quality. Two days of screens found no small model, prompt, decoder or gate that closes the 1.7B's reading gap at the same phone time, and the product rule became "refuse by default when no source is kept, with a warning line on what is shown".

## For curious readers {#curious}

#### The ordinary phone said no

On a common 8 GB phone the model we had used all along needed half a minute or more per answer, and once the phone simply shut it down for lack of memory. A smaller model, with 1.7 billion parameters, answered in a quarter of a minute or less.

*Badge:* Pixel 8a · our measurement app (not the submitted app) · 9 public practice questions · timing only.

#### Faster, and it reads worse

On 20 October the author made the small model the main engine for 8 GB phones. Not because it is better: on 51 practice questions the bigger model stays clearly ahead. Because a phone that answers in seconds, without crashing, is a phone people can use.

*Badge:* v0.1 practice · Claude Opus judge · 51 questions · 1 run per model · 4B ahead by 0.109 (old scale).

#### Nothing closed the gap

Over two days dozens of tricks were tried on the small model: other small models, new prompts, different ways of picking words, confidence checks. None made it read as well as the bigger one at the same speed on the phone.

#### No source, no answer (by default)

The product rule changed too: when the phone's libraries hold nothing on the question, the app says so instead of guessing, and a button shows the model's unsourced guess under a warning. We counted what that button reveals: more wrong answers than right ones, so it sits behind a second tap and never appears for health questions.

*AI-reviewed, not clinically reviewed. Nothing here is medical advice.*

**In one sentence card:** "For an 8 GB phone, speed and memory picked the small model; it reads worse, and we say so."

*Facts: [F-1418] [F-1386] [F-2077] [F-2072] [F-2076] [F-1933] [D-187] [D-149] [F-2084] [F-1633]*

## For tech people {#tech}

### Qwen3-1.7B on 8 GB: chosen for latency and memory, not quality

On a Pixel 8a (8 GB) running our measurement app, the 4B decoded at 3.6–6 tok/s, answered in 29–46 s and was killed once by the low-memory killer at 4.4 GB RSS; Qwen3-1.7B decoded at 13–16 tok/s and answered in 13–16 s (9 public dev questions, before batched lookups). On 2026-10-20 the author made the 1.7B the main 8 GB engine and the 4B an optional tier. Batching the pack lookups (937 → 48 SQL calls per retrieval, byte-identical retrieval on 390/390) cut the 1.7B's time to first token on the phone from 9.12 to 5.55 s. On the 73-question phone run the 1.7B's p50 is 4.2 s with PSS 3.39 GB, but that p50 covers deterministic answers and declines (35 % of v0.1); its model-path p50 is about 12 s. The cost is reading: under Opus on v0.1 51 dev the 4B leads by +0.109 (+0.063…+0.160) on the judge.v1 floor-adjusted ratio, and at identical pack contexts it reads 0.650 vs 0.529 (Haiku raw).

**Gotcha box: "citation-dropping models get refused by your own engine."** Ministral, Qwen3.5-2B, SmolLM3, granite and a public RAG LoRA dropped `[n]` markers, so the engine's 50 % key-word support check stripped their answers and false refusals rose to 9/20 [F-2117] [F-1931].

**Gotcha box: "set the screen bar from a null arm."** A whitespace-only patch or a new seed already "fixes" 23–31 % of problem items; GATE v2 sets the bar at the largest measured null net + 2 [F-2073] [D-141].

**Product rule box:** no source kept → decline by default; "show anyway" behind a second confirmation, never on health; shown answers carry the warning line (precision 0.39–0.40, recall 0.65–0.67 on the 1.7B) [D-149] [F-2085] [F-1633]. AI-reviewed, not clinically reviewed.

*Facts: [D-134] [D-187]*

## For AI professionals {#ai}

### The record for this chapter

**Key facts (dev data throughout; bench app or desktop research engine, never the submitted app):**
- Why no 8 GB lever could move the bounty-style number: on V-para the 4B's gap of 0.586 ratio points splits into wrong-from-memory 0.309 (23 items), absent knowledge 0.239 (24), thin 0.038 (4), refusals 0 (Opus judge.v1, seed 42, single-seed labels ± 0.05; [F-1406]). The fact is in the installed kit for 6 of 51 items and in any pack on disk for 10 of 51 [F-1407]. Estimated ceiling of all 8 GB levers on V-para: about +0.01–0.02 raw [F-1411].
- Honest prompt for the app's longer style: honesty clauses cut the audited wrong-claim rate 0.231 → 0.062 (paired −0.169, CI −0.281…−0.073; Claude Opus sentence audit, 15 agent-written chat turns per arm, 407 claims, dev) at no judged-ratio cost [F-1394] [F-1397].
- The pivot: on a Pixel 8a (8 GB) the 4B decoded 3.6–6 tok/s, answered in 29–46 s and was killed once at 4.4 GB RSS; the 1.7B decoded 13–16 tok/s and answered in 13–16 s (9 public dev questions, before batched lookups; [F-1418]). The author made the 1.7B the main 8 GB engine and the 4B an optional "more complete" tier ([D-134] / [F-1386]).
- Batched pack lookups (937 → 48 SQL calls per retrieval, retrieval byte-identical 390/390) cut the 1.7B's time to first token on the phone from 9.12 to 5.55 s (n 9; [F-1422], [F-1423]).
- 73-question phone runs (bench app, Pixel 8a, v0.1 dev, one run each): 1.7B p50 4.2 s over all items, PSS 3.39 GB; Gemma 4 E2B 11.8 s, PSS 4.52 GB; 4B 26.0 s complete (older engine), PSS peak 4.76–4.92 GB [F-1565] [F-2078]. **Caveat that travels with the 4.2 s:** it covers deterministic answers and declines (the 1.7B declined 35 % of v0.1); its model-path p50 is about 12 s; never set it beside the 13–16 s of the 9-question runs.
- The cost is reading. Under Opus (judge.v1 floor-adjusted ratio "U", v0.1 51 dev, one seed per rung): 4B − 1.7B +0.109 (+0.063…+0.160); 4B − Gemma E2B +0.098 (+0.054…+0.146); 1.7B − closed-book 1.5B +0.090 (+0.009…+0.170), which under Haiku is +0.038 (−0.023…+0.098), so that last step is judge-dependent [F-2077]. At identical pack contexts (54 pack self-tests, Haiku raw): 4B 0.650, LFM2.5-8B-A1B 0.554, 1.7B 0.529 [F-1401].
- Screens that did not close it (GATE v2, two-stage; [F-2072], [F-2117]): six prompt, decoding and confidence levers (fixes 1–4 of 21–23 confident errors, bar 6; token-probability AUC 0.530); decoder-level grounding [D-159]; Ministral-3-3B with a citation prompt passed stage 2 (Opus +0.047) but at about 3× phone time and below the 4B (−0.037 Opus), closed as dominated [D-189] [F-1933]. Gemma 4 E2B: Haiku +0.028, a FAIL by 0.002; Opus +0.031 (+0.005…+0.058), a GO by 0.001 [F-2076]; on the phone 11.8 s vs 4.2 s and +1.1 GB; kept as an opt-in proposal only [D-143].
- Honesty surface: the author set "no source → refuse by default, with a 'show anyway' control" [D-138] [D-149]. A groundedness gate cut visible confident errors 7 → 3 of 177 under an Opus re-judge (Haiku 10 → 4), false refusals 0 of 14, at about +9.3 s per answer projected for the Pixel 8a (5.1 s measured on a desktop); it is not in any app [F-1430] [F-2074]. Revealed answers behind "show anyway" were 11 correct to 16 confident errors in an Opus census [F-2084], so the button is a liability: it sits behind a second confirmation and never on health [F-1633]. The warning line's precision is 0.39–0.40 and recall 0.65–0.67 on the 1.7B (Haiku / Opus; [F-2085]). No drift detected over five turns [F-1957]. AI-reviewed, not clinically reviewed.

**Key decisions:** [D-123] / [D-124] (delegated decisions D1–D7: no v0.3, site only as v1.0 at closure), [D-129] (direction review: consolidate), [D-134] (1.7B main engine), [D-141] (GATE v2), [D-149] (refuse by default), [D-159] (decoder grounding closed), [D-186] (keep Q4_K_M), [D-187] (1.7B on latency and memory, not quality; model screens parked), [D-189] (Ministral closed). **Reversals to show:** the 10-20 morning proposal "answer under a warning line" was replaced the same evening by refuse-by-default ([D-135] → [D-149]); the 10-19 release of a safety-failing patch was reversed the same day [D-128].

**Turning point:** 2026-10-20 ~11:50, the author: "Qwen3-1.7B becomes the main engine".

### 6.8 Latency and memory over quality: the 1.7B as main engine

A V-para diagnosis decomposed the 4B's 0.586 ratio-point gap into wrong-from-memory 0.309 (23 items), absent knowledge 0.239 (24), thin 0.038 (4) and refusals 0 (Opus, seed 42, labels ± 0.05), with the fact present in the installed kit for 6 of 51 items; the estimated ceiling of all 8 GB levers on V-para was ≈ +0.01–0.02 raw [F-1406] [F-1407] [F-1411]. On a Pixel 8a the 4B answered in 29–46 s and was killed once at 4.4 GB RSS, the 1.7B in 13–16 s (9 public dev questions; [F-1418]); the author made the 1.7B the main 8 GB engine on 2026-10-20 [D-134]. Under Opus on CV5 51 (judge.v1 floor-adjusted ratio of sums, one seed per rung) the 4B leads the 1.7B by +0.109 (+0.063…+0.160) and Gemma 4 E2B by +0.098 (+0.054…+0.146); the 1.7B's lead over a closed-book 1.5B is +0.090 (+0.009…+0.170) under Opus and +0.038 (−0.023…+0.098) under Haiku, i.e. judge-dependent [F-2077]. Two-stage screens (GATE v2; the bar = the largest measured null-arm net + 2, after null arms "fixed" 23–31 % of problem items; [F-2073]) closed prompts, decoding, token-confidence gates (AUC 0.530), decoder grounding, fine-tuned readers and small-model swaps; Gemma 4 E2B's stage-2 verdict flips with the judge (Haiku −0.002 below the bar, Opus +0.001 above; [F-2076]) at 2.8× phone time. A groundedness gate cut visible confident errors 7 → 3 of 177 under an Opus re-judge (Haiku 10 → 4), false refusals 0/14, at ≈ +9.3 s per answer projected on the phone [F-1430]. The reveal-anyway control returned 11 correct to 16 confident errors in an Opus census [F-2084]. No drift was detected over five turns [F-1957].

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-1386] Qwen3-1.7B = main 8 GB engine; 4B = optional "more complete" tier. adopted; confirmed at 19:07 grill · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-20 ~11:50 · caveat: who decided: author; why: Pixel 8a: 1.7B 13-16 tok/s, answers 13-16 s; 4B 3.6-6 tok/s, 29-46 s, one LMK kill; alternatives: keep 4B default; Qwen2.5-1.5B (faster but weaker); reversible: yes
- [F-1394] Honest Detailed prompt (D1) cuts wrong-claim rate on the app's chat-template path. 0.231 -> 0.062 (paired -0.169) · set set A (agent-written chat turns), dev (dev, development data) · judge Claude Opus sentence audit; wrong claims / claims · n 15 · seeds UNKNOWN · CI CI -0.281..-0.073; n 15 answers/arm, 407 claims · date 10-18 · caveat: answers 42 % shorter; vaguer on 2/15
- [F-1397] D4 costs no judged ratio on v0.1. D4 0.427 vs D1 0.425 (+0.003); D0 0.452 (judge.v1 ratio) · set v0.1 public dev (dev, development data) · judge Claude Haiku 5.5-low, raw ratio · n 57 · seeds 1 · CI CI -0.024..+0.028; 57 ids, 1 seed · date 10-18 · caveat: win 0/57 for both. Proxy contexts (not the app retrieval), one seed, Claude Haiku judge; raw ratio only (the source has no floor-adjusted value).
- [F-1401] PACKREAD: reading with packs, D4 prompt. 4B 0.650, LFM2.5 0.554, 1.7B 0.529; engine Succinct anchor 0.610 · set pack self-tests, dev (dev, development data) · judge Claude Haiku, raw ratio · n UNKNOWN · seeds UNKNOWN · CI 54 pack self-test items; LF-D4 vs M4-D4 -0.096 (-0.145..-0.052) · date 10-19 · caveat: identical contexts: 1.7B gap is reading
- [F-1406] V-para 4B gap decomposition. gap 0.586 ratio points: wrong 0.309 (23 items), absent 0.239 (24), thin 0.038 (4), refusals 0 (judge.v1 ratio) · set V-para (dev-style since 10-09) (dev-style since 2026-10-09, development data) · judge Claude Opus judge.v1; LOSSMAP labels · n 51 · seeds UNKNOWN · CI n 51, s42 · date 10-19 · caveat: single-seed labels, shares ±0.05
- [F-1407] Facts for V-para are mostly nowhere. in installed kit 6/51; all packs on disk 10/51; full English Wikipedia 9/34 absent items · set V-para (dev-style since 2026-10-09, development data) · judge coverage counts · n 51 · seeds UNKNOWN · CI n 51 / 34 · date 10-19 · caveat: The 34 are the deep tier's absent items; the 4B's absent set is 24, of which 17 are shared.
- [F-1411] Estimated ceiling of all 8 GB levers on V-para. about +0.01-0.02 raw (judge.v1 ratio) · set V-para (dev-style since 2026-10-09, development data) · judge estimate · n UNKNOWN · seeds UNKNOWN · CI estimate, untested · date 10-19 · caveat: estimate only
- [F-1418] Pixel 8a speed, 1.7B vs 4B. 1.7B 13-16 tok/s, answers 13-16 s; 4B 3.6-6 tok/s, 29-46 s; 4B LMK kill at 4.4 GB RSS · set public dev questions (dev, development data) · judge timing · n UNKNOWN · seeds UNKNOWN · CI 9-question runs · date 10-20 · caveat: 4B 73/73 only after a reboot | VERIFIER NOTE: Pre-BATCHRET, 9 public dev questions; not comparable with the 73-question p50 of 10-21.
- [F-1422] BATCHRET. SQL calls per retrieve 937 -> 48; retrieval byte-identical 390/390 · set public dev (dev, development data) · judge parity · n 390 · seeds UNKNOWN · CI 390 items · date 10-20
- [F-1423] BATCHRET on the Pixel 8a, 1.7B. TTFT 9.12 -> 5.55 s (-39 %); retrieval 5.04 -> 1.45 s; total 12.39 -> 9.40 s; safety card 8.27 -> 3.10 s · set litelat-9 (unspecified) · judge timing · n 9 · seeds UNKNOWN · CI 9 items, A B A B, thermal 0 · date 10-20
- [F-1430] REFUSE-UNSUPPORTED. visible confident errors 7 -> 3 of 177 under Claude Opus (re-judge of the 38 deciding answers; Claude Haiku 10 -> 4); false refusals 0/15; U on answered +0.030 (+0.005..+0.057, Haiku); coverage 0.435 -> 0.328; +9.3 s p50 projected on the Pixel 8a · set MAIN 97 + 80 self-tests, dev (dev, development data) · judge Claude Haiku 5.5-low; Claude Opus re-judge for the confident-error count · n 177 · seeds UNKNOWN · CI n 177 · date 10-20 · caveat: GATELAT: no cheaper variant keeps AUC | Verification note: Judge-dependence: Haiku 10 -> 4 of 177; Opus re-judge of the 38 deciding answers 7 -> 3 of 177 ; the claim text should quote 7 -> 3 with Opus named. +9.3 s is projected.
- [F-1565] Phone, Pixel 8a, 73 questions, bench app. 1.7B p50 4.2 s, p90 12.2, 12.4 tok/s, PSS 3.39 GB; Gemma E2B p50 11.8 s, 7.0 tok/s, PSS 4.52 GB · set v0.1 (dev) (dev, development data) · judge speed · n 73 · seeds 1 · CI n 73, 1 run each · date 10-21 03:31 · caveat: p50 is over all 73 items including deterministic-layer and declined items: the 1.7B made 38 LLM calls vs Gemma 55 and declines 35 % of v0.1; model-path answer p50 is about 12 s. Not like-for-like with the 9-question 13-16 s runs of 2026-10-20.
- [F-1633] Earlier: Product behaviour "refuse + show anyway" (GRILL D4). Changed to: Show-anyway only behind second confirmation, never on health; RC1 has no warning line at all.
- [F-1931] CITEFIX: Is the citation-drop failure a format issue? engine's 50 % key-word support check strips 161 paraphrased citations; format fix flips no gate · set 910 candidate answers (status UNKNOWN) · judge 0 Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-21 · caveat: criterion frozen: yes (93c85722); arm verdict: open lever: paraphrase-tolerant check
- [F-1933] MIN3CITE: Ministral-3-3B + citation prompt v2. stage 2 Haiku +0.062 (+0.037..+0.089); Opus +0.047 (+0.021..+0.075); ~3x phone time; −0.037 vs 4B (Opus, 61) · set screens; MAIN 97 K0 (dev, development data) · judge Claude Haiku; Claude Opus revisit · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-21 · caveat: criterion frozen: yes (a4d2d9a3; revisit e9813e2c); arm verdict: Haiku PASS; closed as dominated
- [F-1957] DRIFT17: Does the 1.7B degrade over a session? CE-unwarned t1 0/10 vs t4-5 3/20, CI covers 0; one unsafe health error in both arms · set longsession-v1 80 (dev) (dev, development data) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI rise CI 0.00..0.30 · date 2026-10-21 · caveat: criterion frozen: yes (5ea4b345); arm verdict: KILLED (no drift detected) AI-reviewed, not clinically reviewed.
- [F-2072] Six prompt/decoding/confidence levers for the 1.7B were null. fixes 1-4 of 21-23 CEs (need 6); logprob AUC 0.530; first-token AUC 0.488 · set dev (dev, development data) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI screens of 37 · date 2026-10-20 · caveat: old CE metric; REREAD re-counted
- [F-2073] Null arms already "fix" a quarter of screen problems. 23-31 %; bar = max null net + 2 · set dev (dev, development data) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI 2 nulls per set · date 2026-10-20 · caveat: calibration rests on 2 nulls
- [F-2074] Groundedness gate refusing unsupported 1.7B answers. visible CEs 10→4 of 177 (Opus 7→3); false refusals 0/15; +9.3 s projected per answer · set MAIN 97 + 80 self-tests (dev) (dev (pack-written self-tests), development data) · judge Claude Haiku; Claude Opus · n 177 · seeds UNKNOWN · CI n 177, 1 seed · date 2026-10-20/21 · caveat: latency blocks shipping; aLoRA unverified
- [F-2076] Gemma 4 E2B vs Qwen3-1.7B on MAIN 97. Haiku +0.028 (+0.006..+0.052) FAIL by 0.002; Opus +0.031 (+0.005..+0.058) GO by 0.001; pooled Opus +0.036 (+0.011..+0.062) · set MAIN 97 (dev) (dev, development data) · judge Claude Haiku; Claude Opus · n UNKNOWN · seeds UNKNOWN · CI 2 seeds · date 2026-10-21 · caveat: gain mostly fewer refusals; 2.8x phone time
- [F-2077] Tier ladder under Opus. 4B−1.7B +0.109 (+0.063..+0.160); 4B−Gemma +0.098 (+0.054..+0.146); 1.7B−closed-book 1.5B +0.090 (+0.009..+0.170) · set v0.1 (dev) (dev, development data) · judge Claude Opus judge.v1 · n UNKNOWN · seeds UNKNOWN · CI v0.1 51, 1 seed per rung · date 2026-10-21 · caveat: Haiku: 1.7B−1.5B +0.038 (−0.023..+0.098), so judge-dependent
- [F-2078] Pixel 8a 73-question runs. 1.7B p50 4.2 s, PSS 3.39 GB; Gemma 11.8 s, 4.52 GB; 4B 26.0 s complete, PSS peak 4.76-4.92 GB · set public dev (dev, development data) · judge timing · n UNKNOWN · seeds UNKNOWN · CI 73 items · date 2026-10-21 · caveat: 1.7B declines 35 % of v0.1 (not like-for-like) | Runs differ: 4B 26.0 s complete is final-cut7-v01 (pre-BATCHRET engine); the 4B LMK kill is the 10-20 first attempt . 1.7B declines 35 % of v0.1, so speeds are not like-for-like .
- [F-2084] Show-anyway reveals under Opus. MAIN census 11 correct : 16 CE (0.69; non-health 0.56, CI 0.22-1.35) · set MAIN 97 (dev) (dev, development data) · judge Claude Opus · n UNKNOWN · seeds UNKNOWN · CI 58 hidden answers · date 2026-10-21 · caveat: Haiku 7:19 on same rows AI-reviewed, not clinically reviewed.
- [F-2085] Warning line precision/recall (1.7B) precision 0.39 (0.32-0.46), recall 0.67 (0.59-0.75); Opus 0.40 / 0.65 · set dev (dev, development data) · judge Claude Haiku; Claude Opus · n UNKNOWN · seeds UNKNOWN · CI 746 answers · date 2026-10-21 · caveat: mostly a support signal (77 % of warned rows had a source)
- [F-2117] Model-onboarding pattern: citation-dropping models get penalised by the engine. Ministral, Qwen3.5-2B, SmolLM3, granite, FOTAPOL all drop [n]; false refusals up to 9/20 · set dev (dev, development data) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI screens · date 2026-10-20/21 · caveat: engine-specific confound (lexical support check)

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-123] 2026-10-18 · D1: no LFM2.5 desktop replay · why: audit already 7/58 vs 3/73 wrong; product already chose Qwen. · status: kept
- [D-124] 2026-10-18 · D7: upload the research site only as v1.0 at closure; v0.x are internal build states · why: one publication, no intermediate states. · status: kept
- [D-128] 2026-10-19 · Release saferoute patch despite SAFEPACK frozen-rule FAIL (app ships with a warning); FAIL kept on record · why: rule judged too strict for stage. · status: reversed (Reversed the same day: the saferoute patch was held out of the pushed stack after the independent direction review.)
- [D-129] 2026-10-19 · Stop opening new arms; consolidate; hold saferoute; correct over-reads (SMALLCLS, SAFEPACK) · why: scope drift two days before closure; small-n in-sample results drove release calls. · status: kept
- [D-134] 2026-10-20 · Qwen3-1.7B = main 8 GB engine; 4B = optional "more complete" tier · why: Pixel 8a: 1.7B 13-16 tok/s, answers 13-16 s; 4B 3.6-6 tok/s, 29-46 s, one LMK kill. · status: kept
- [D-135] 2026-10-20 · Propose to maintainer: 8 GB = Qwen3-1.7B + fixed warning line instead of compact declines · why: CMP30OFF: 1.7B with declines released leads 1.5B. · status: superseded by D-149 (superseded at 20:24 by refuse-by-default)
- [D-138] 2026-10-20 · Ruler headline = coverage x U decomposition + U-total; product refuses by default when no source is kept, with a "show anyway" control · why: separate what packs answer from memory answers. · status: kept
- [D-141] 2026-10-20 · GATE v2: screen bar = max measured null net + 2 · why: null runs fixed 23-31 % of problems; old 6-fix bar sat at the null. · status: kept
- [D-143] 2026-10-21 · Gemma 4 E2B only as opt-in catalog entry with thinking guards (thinking off, budget 0, n_predict cap, post-filter); exact file pinned · why: phone quality = 1.7B, 1.5-2.8× time, +1.1-1.4 GB; runtime risks (thinking default on, KV growth) · status: kept
- [D-149] 2026-10-21 · No source found → refuse by default + "show anyway", shown answers carry a warning line · why: honesty on 8 GB. · status: kept
- [D-159] 2026-10-21 · Close decoder-level grounding axis on the 1.7B · why: all arms net 4-6 vs bar 9. · status: kept
- [D-186] 2026-10-20 · Keep Q4_K_M quantisation for the 1.7B · why: Q8_0 inside null band, decode x0.66, +0.7 GB. · status: kept
- [D-187] 2026-10-21 · 1.7B stays the 8 GB recommendation on latency and memory, not quality; model screens parked · why: MIN3CITE/Gemma gains cost 2.8-3x phone time. · status: kept
- [D-189] 2026-10-21 · Close MIN3CITE (Ministral + citation prompt) as dominated by the 4B; do not send · why: Opus +0.047 but −0.037 vs 4B, ~3x time. · status: kept

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.1.2, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.
