METHODS — frozen from CLAIM-DRAFT v3.8 on 2026-10-10; weekly batch edits only; reviewed (CLAIM-REVIEW-v3.8.md)
Scrubbed copy for the public repo: handles, upstream maintainer name, absolute paths, device-tester names and withheld-set paths removed; no number changed.
> **Public-release path map (v1.1.2).** This file was written for the first single-package release. Read `boar-eval/...` as `boar-bench/...` (sibling repository) and `engine/...` and `tools/...` as this folder (`rnd/research/coordinator/repro/`); other workspace-relative paths resolve in `boar-research` or `boar-bench` unless `docs/EXCLUDED.md` lists them as withheld. Full table: [REPRODUCE.md](REPRODUCE.md), section "v1.1 layout".
Source: rnd/research/coordinator/CLAIM-DRAFT.md (v3.8). Paths below are relative to the private workspace root unless they are public URLs.

Draft v3.8 (2026-10-10 midday; v3.7 + one levers row: thinking 4B on the fast path, not adopted; S42; §6 deep-tier row: best-of-2 and V-para routing sentences, S43, S44; independent review 2026-10-10 ACCEPT WITH EDITS, applied) — Draft v3.7 (2026-10-09 night; v3.6 + thinking-budget curve closed (256 loses), 512 measured on v0.2; independent review 2026-10-09 night ACCEPT WITH EDITS, 1 major + 6 minor + 1 nit applied) — Draft v3.6 (2026-10-09 evening; v3.5.1 + v0.2 two-seed thinking number, thinking budget 512, phone-speed estimate from a public competitor measurement, long-answer persona negative; independent review 2026-10-09 ACCEPT WITH EDITS, 3 major + 7 minor applied) — Draft v3.5.1 (2026-10-09; v3.5 + v0.2 thinking sentence S35 + Gemma 4 deep-model sentence S36, unreviewed) — Draft v3.5 (2026-10-09; v3.4 + deep tier with thinking (DEEPTHINK, S33; DEEPTHINK-2 negative); independent review 2026-10-09 ACCEPT WITH EDITS, 3 major + 7 minor applied) — Draft v3.4 (2026-10-08; v3.3 + the deep-tier held-out-style results (DEEPVPARA, S31; DEEPROUTE-OOS, S32); independent review 2026-10-08 ACCEPT WITH EDITS, 4 edits applied) — v3.3 (v3.2 reviewed; v3.3 adds only the deep-tier engine-parity sentence and S30, reviewed 2026-10-07 ACCEPT WITH EDITS, edits applied) — v2 reviewed (CLAIM-REVIEW.md), updated with evidence from 2026-10-05/06; v3.1 (2026-10-07) reordered the headline to floor-removed + win rate (PIPELINE-AUDIT-2026-10-06 D1); v3.2 (2026-10-07) adds the 10-07 results (cut 7 claim build, venues with location + area tile, local-judge bias, deep-tier routing, v0.3 plan). Not published; pending independent review.

# BOAR claim draft for poidh bounty #31 (DRAFT; independently reviewed through v3.8, see the changelogs; not published)

Status: draft. Nothing here has been posted, pushed or uploaded. Every number carries a source tag in square brackets. The tags are listed in "Sources" at the end. Paths are relative to the workspace root.

## 1. TL;DR

<!-- src: CLAIM-RESULTS-cut3.md (raw, floor removed, CIs); PIPELINE-AUDIT-2026-10-06 §1 (win/tie/loss, anchors floor-adj); CLAIM-RESULTS-cut6.md (s42 105/110 identical) -->
- **Headline metric (changed in v3.1):** floor-removed ratio plus pairwise win rate, raw ratio second. The judge gives a blank or wrong answer 1/5 on each axis, so a system that declines every question gets a raw ratio of about 0.31 (D = 0.306) for free; raw 0.50 is therefore not "half as good". [S1] [S2]
- **Held-out set in the style of the bounty's example questions (V-para, written by our team, 51 judged questions plus 7 venue questions; blind to the engine builders when these claim runs were made, spent since by deep-tier and venue arms, see section 5):** floor removed **0.261 (0.224–0.299)**; pairwise wins **0 of 51**; raw 0.413 (0.384–0.445). The bar is not met on this set. A no-web Haiku scores raw 0.588 (floor removed 0.48) on the same items. [S1] The 7 venue questions scored 0 of 7 in the claim run, which passed no device location; **with device location and the user's area tile** (5 tiles, +3.65 MB) the places path returned ≥ 3 OSM-gold venues on 7 of 7 (10 per item), both seeds (measured 2026-10-07, development-style per section 5); engine venues and gold both come from OSM diet tags. That is a plumbing check, not a quality score (section 5). [S1] [S20]
- **Held-out result (bench v0.2, 110 new questions, written blind):** floor removed **0.389 (0.347–0.435)** (cut 6 s42 alone: 0.397 [S27]); raw 0.513 (95% CI 0.479–0.550), an interval that contains 0.50. On the cut 6 re-run (seed 42; 105 of 110 answers byte-identical to cut 3) win/tie/loss is **0/0/110**. The honest reading is "below half once the floor is removed; not shown to be above half even on the raw scale". The v0.2 set has since been exposed (plaintext in a private repository's history, 4 runs) and is treated as development data; a final number needs a new set (bench v0.3, written outside the Claude family; claim run planned by 10-24, section 7). [S1] [S25]
- **Three scales, always shown together:**

| Set | Raw | Floor removed | Above always-decline |
|---|---|---|---|
| v0.2, formerly held-out (exposed) (110) | 0.513 (0.479–0.550) | 0.389 (0.347–0.435) | 0.299 (0.250–0.351) |
| V-para (51 judged) | 0.413 (0.384–0.445) | 0.261 (0.224–0.299) | 0.154 (0.112–0.200) |

  [S1] "Floor removed" subtracts the judge's minimum score from both sides. "Above always-decline" measures the gain over a system that declines every question (fixed at D = 0.306). [S2]
- **Device status (8 GB phone only; no 12 GB phone run):** cut 6 (the claim build minus the facts tier) ran the 73 v0.1 questions on an 8 GB Galaxy A15 with airplane mode on and the network permission absent: 73/73 completed; model answers p50 49 s, p90 77 s, max 111 s; instant answers p50 8.5 s; app memory (PSS) max 4.41 GiB; thermal status 0. On the 57 judged items the phone scored 0.561 (0.507–0.617) against 0.558 and 0.560 on the desktop: device quality equals desktop within noise. These are development items the engine was tuned on, so this is not evidence for the bar. A cut 5 rate sweep on the same phone measured decode at 2.0–2.7 tokens/s. The earlier 9-question cut 3 smoke test (model answers 100–147 s) predates the KV-cache fix. Cut 7's facts tier has not run on a phone. [S28] <!-- src: QUEUE.md l.695, l.711 -->
- **Engine lineage (updated in v3.2):** the claim build is **cut 7** (commit 6d0b93b1, tree 7c96e59e…) = cut 6 + an instant facts tier (FACTS r6). The headline numbers were measured on **cut 3** and re-run on **cut 6** (held-out raw 0.512 vs 0.513, Δ −0.001, CI −0.010…+0.008; 210 of 220 held-out item-seed answers byte-identical). The facts tier fires on 0 of 110 held-out and 0 of 58 V-para questions, so cut 7's answers on those sets equal cut 6's (engine replay 110/110 and 58/58 identical); cut 7 was adopted on gates, with 0 judge calls. Its only measured effect is a projected +0.027 on the v0.1 development set (8 fires). See section 3. [S18] [S19]
- **Fidelity and reproducibility (new in v3):** the claim runs used the runner with the route gate and emergency detector on; the gate does not change v0.1 answers. The runner is now committed behind flags. See section 2. [S14] [S15] **Offline (new in v3):** no-network APKs (no INTERNET permission, by construction) of cut 4 and cut 5 exist. No phone run in airplane mode has happened yet. See rows 4 and 5. [S16]
- **Not yet done:** public repo, Android UI integration (PR phase), device speed numbers on a 12 GB phone, public demo post. See section 4.
- **Scope of this claim:** all claim numbers are desktop-proxy results of cut 3 (re-run on cut 6; cut 7 identical on these sets by replay). They are not device results. [S1] [S18] [S19]

## 2. What was measured and how

### Judge and reference
- Each BOAR answer is compared pairwise with a reference answer written by a frontier model (Claude Opus 5.5) with web search (`reference.v1`, generated once and frozen). The judge is the same model family. [S2]
- The judge is an Opus model (`judge.v1`). Every pair is judged in both A/B orders and the scores are averaged. Disagreement between orders counts as a tie. [S2]
- Score per answer = mean of correctness, completeness and usefulness. Ratio = sum of BOAR scores / sum of reference scores. [S2]
- Confidence intervals: stratified two-level bootstrap (resample items within category, then runs within item), 2,000 resamples, 95% percentile. Two runs per arm (seeds 42 and 43). [S1] [S2]
- Always-decline reference point D = 0.306, measured on 79 declined answers across 7 earlier runs. [S2]
- **Triage judges (new in v3.2; method only, not claim numbers).** Development screens are now triaged with Haiku 5.5 (effort low): same winner as Opus on 54 of 57 v0.1 items, about 14× cheaper than Sonnet-low, run 8 in parallel (same winner 55/57 vs sequential). It compresses paired gaps (deep35 − 4B +0.007 vs Opus +0.029), so it ranks but does not size effects. Every claim number in this draft is Opus `judge.v1`. [S22]

### Frozen before running
- The bench, references, judge prompt, analysis plan and scoring scripts were hashed (per-file sha256 plus one combined hash) before any BOAR run on the held-out set. [S2] [S1]
- The claim runs had a written authorisation file with its own hash, verified unchanged. No code, config or criterion changed between the authorisation and the runs. No re-runs. [S1]
- Dev and held-out are separate. Bench v0.1 (60 items, the planned public split) is the development set; engine changes were tuned on it. The 110 v0.2 questions are held-out: no engine change was tuned on their scores, with one disclosed exception (below). [S2]
- The V-para set was written separately and kept blind through the claim runs (cut 3 on 2026-10-05, cut 6 on 2026-10-06). Researchers did not read it; only aggregate scripts touched it. It has been spent since (section 5). [S1]
- Caveat on the held-out rule: one held-out item (a generator-indoors safety question) was known before the safety fix. It is excluded from any claim of improvement. [S3]

### Runner fidelity and reproducibility (new in v3)
- **Which runner made the claim numbers.** The cut 3 claim runs (held-out v0.2 and V-para) used the "be-ship" desktop runner: node backend, **route gate on**, learned emergency detector on. An earlier internal note that desktop runs had no gate was true only for the older committed runner. [S14]
- **The gate does not change v0.1 answers.** On v0.1 EN (seed 44, 60 items), a same-tree run with the gate off was compared with the gate on. Cut 4 with gate: 54 gate calls, all "search"; cut 5 with gate: 22 calls (32 skipped by rule), all "search". 0 of 60 answers changed text, 0 route or tier changes. Nothing needed judging. Limits: one seed; v0.1 has no small-talk items, so the gate's answer-directly path is not exercised; this shows the gate is harmless on questions, not that its other path is right. [S15]
- **Reproducibility.** The runner variant that made the claim numbers lived only on the experiment machine. It is now committed behind flags (`BOAR_RUNNER_PROFILE=ship`, `BOAR_ROUTE_GATE`, `BOAR_DETECTOR*`, `BOAR_KV_TYPE`), with defaults of older committed runs unchanged, and a table maps each run to its runner. The commit is local; the repository is private and unpublished. Server-backend runs (some development experiments, not the claim runs) have no gate. [S14]

### Ladders
**Model-size ladder, 1.5B to 4B (development set, bench v0.1, earlier engine):**

| Config | Raw | Floor removed | Above always-decline |
|---|---|---|---|
| 1.5B (iPhone config) | 0.381 (0.350–0.414) | 0.222 (0.183–0.263) | 0.108 (0.063–0.156) |
| 4B (Android config) | 0.512 (0.466–0.558) | 0.387 (0.330–0.444) | 0.297 (0.231–0.363) |
| Paired gap 4B minus 1.5B | +0.131 (+0.095…+0.171) | +0.165 (+0.120…+0.215) | +0.189 (+0.137…+0.246) |

[S2, section 10] These were computed before the later engine changes. They show the size effect only.

**Frontier ladder on V-para, no web access, same judge (context, not a bar):**

| System | Raw ratio |
|---|---|
| BOAR cut 3 (4B) | 0.413 (0.384–0.445) |
| Haiku | 0.588 (0.559–0.615) |
| Sonnet | 0.961 |
| Opus | 1.044 |
| Fable | 1.037 |

The ladder models ran once each on the 51 items; BOAR's figure pools two runs. BOAR is below a small hosted model (Haiku) without web. This is the gap to close. [S1]

The deep tier (35B-class model, desktop proxy) is not on this ladder; its V-para rungs (floor removed: 4B 0.26 (held-out claim run) → deep 0.33 → deep + thinking 0.42 (0.44 at a 512-work budget) (the deep rungs are development-style, measured after 2026-10-06, section 5); win rate 0 of 51 at every rung; bar 0.50) and its v0.2 rungs (development data; floor removed: 4B 0.39 → deep 0.46 → deep + thinking 0.51 (0.475–0.554, CI straddles 0.50, bar reading not met) (0.51 at 512, 0.467–0.550, one seed); win rate 0 of 110 at every rung) are in section 6. [S31] [S33] [S35] [S37] [S41]

### Other results on the development set (not claim evidence)
- v0.1 EN, cut 3, seeds 44 and 45, 57 judged items: 0.566, versus 0.534 for cut 2 (+0.032, 90% CI +0.010…+0.062). These items are the ones the cut 3 levers were built on. [S4]
- The full 167-item view (0.533, CI 0.502–0.564) contains 57 development items, so it is not used as the claim. [S1]

### Departures from the pre-registered plan
- **Headline source.** The plan says device numbers lead. No 12 GB device run exists yet, so this draft leads with desktop-proxy numbers, labelled as such.
- **1B-class gap on the held-out set: not run.** The plan requires it with a paired CI. The only size ladder shown is from the development set on an earlier engine.
- **Seeds.** The plan planned three runs (seeds 42, 43, 44). Two were run (42, 43), which is the plan's stated minimum.
- **Not yet reported:** the always-decline level measured on the claim run's own declines; per-writer held-out results; the cross-family judge; the 40-pair human label check.
- **Pre-registration timing.** Hashes were committed to a private repository before the held-out runs. They have not been published, so an outside reader cannot yet verify the timing. The plan said to publish the combined hash before the first run.

## 3. The engine

### Default model and knowledge kit
- **Reader model:** Qwen3-4B-Instruct-2507, Q4_K_M quantisation, 2.50 GB. [S8] [S11]
- **Everything pushed to the phone (3.03 GB in total, model included):** reader model 2.50 GB, embedding model 37 MB, emergency detector 108 MB, English Wikivoyage pack 351 MB, crypto pack 36 MB. The knowledge packs themselves are therefore about 0.39 GB. The V-para run (desktop) also loaded a places kit (world places and three city tiles); its size is not in the sources reviewed. [S1] [S11] **Cut 7 additions (new in v3.2):** a facts table asset of 761 KB (4,233 entities); for venue questions, one area tile per user location (0.2–1.1 MB each; the 5 V-para tiles total +3.65 MB). [S18] [S20]
- Retrieval picks passages from the kit, then the 4B answers with citations. Questions about emergencies go to a separate safety path first. [S5]

### Deterministic modules (code answers instead of the model)
Each module acts only when its trigger fires. Otherwise the normal path runs.

| Module | What it does | Evidence |
|---|---|---|
| Travel calculator | Distance between two named places (great-circle times a route factor), round trip, travel time at a stated pace. Always labelled "an estimate, not a mapped route". Uses a 6,000-city table (GeoNames, CC BY 4.0, 272 KB). English only. Never fires on emergencies. | Paris–Rome item: 0.29 before, 0.89–0.94 after. 0 false fires on 1,034 dev messages. [S3] |
| Arithmetic tools | Computes simple rates and times from the numbers in the question, plus a guard against the health detector firing on a math question. | 1 dev item moved +3.33; 0 fires on 1,467 dev messages; on a separate held-out probe set (not bench v0.2), 28/32 right, 0 wrong numbers. [S3] [S4] |
| Verdict guard (v3) | Checks a yes/no or compare answer against the model's own stated facts. If the verdict contradicts them, it repairs the verdict. It abstains when facts are ambiguous. | 3 dev items improved (+1.0 to +2.7 each); 0 worse. On 90 fresh probes it fired once, correctly. It catches only a small part of such errors (1 of 17 on a later probe set). [S3] [S4] |
| Safety cards | Fixed text from official sources for snakebite and other emergencies, shown before the model. The snakebite text was revised after an independent review. | Snakebite item +0.92 on the confirmation run. 0 unsafe-rule hits on the 10 held-out danger questions, both seeds. One of the 10 (generator indoors) had failed in an earlier run and motivated the CO card, so it is not independent evidence. Card texts are AI-reviewed, not clinically reviewed. [S1] [S4] |
| Facts instant tier (cut 7, new in v3.2) | Answers single-fact questions (capital, currency, height and similar) from a fixed table, before the model. Does not fire on health, emergency or Portuguese or Spanish questions. | Blind recall set 4: recall 28/40 (70 %, below its 75 % partial bar (pass 85 %), so the recall line was closed), precision 28/29, 0/20 false fires on near-misses. v0.1: 8 fires, projected +0.027. 0 fires on held-out v0.2 and V-para. Warm lookup p95 0.090 ms; desktop cold load 111–129 ms; phone cold load unmeasured. [S18] |
| Places with device location (new in v3.2) | Lists venues near the user's location from the area tile (OpenStreetMap tags), with no model call. Needs a location fix and the tile for that area. | V-para venues 7/7 both seeds with location + tile (0/7 with no location, both seeds; 0/7 with location but no tile, seed 42 only); 5–192 ms per item, desktop; 5 non-venue controls unchanged. [S20] |
| CO hazard card | Fixed carbon-monoxide safety answer when a fuel-burning device and an enclosed space appear together, plus a symptom card. Reviewed by an independent model reviewer, sources checked. | On a separate blind lookalike set (not bench v0.2): recall 23/26, 1 false fire in 38. The earlier engine gave an unsafe answer on the held-out generator-indoors item. Cut 3 did not, but the card was built after that failure was seen, so this item is excluded from any improvement claim. Card texts are AI-reviewed, not clinically reviewed. [S3] [S1] |

### Levers that failed
Many ideas were tested against frozen criteria and dropped. The full record is in `rnd/research/QUEUE.md` [S3]. One line each, for the 4B reader:

| Lever | What happened |
|---|---|
| Larger Wikipedia packs (top-100k) | Retrieval 3.3× slower, no gain on knowledge items, v0.1 −0.005 to −0.016. Killed. |
| Retrieval v2 (right sentence reached the model 7 → 18 of 56 dev items) | Judged score did not rise (−0.021, 90% CI −0.054…+0.009). Killed. |
| Query expansion, passage reranker | Expansion: no key passage reached the context after gating. Reranker: dropped 0 key passages, 1 worse item. Killed at the first gate. |
| Answer-style prompts (answer first, check then conclude) | −0.031 and −0.006; more confident-wrong answers. Closed. |
| Self-check by the 4B, separate passage checker | The 4B flagged 8 of 20 correct answers (bar 2); the NLI checker caught 0 of 7 (wrong claims came from memory, not from a contradicted passage). Closed. |
| Computed-verdict arms (four variants) | Verdict accuracy rose on fresh verdict sets, but the judged score fell or new wrong answers appeared. Closed. |
| Other 4B-class readers (Qwen3.5-4B, Gemma 4 E4B, Ministral; Qwen3.5-9B) | None beat the current one in screens; Gemma in the engine was −0.0385 and 1.49× slower. Closed. |
| Country-facts pack, water-safety card, crypto and travel passage selection | Each failed its own frozen gate. |
| Prompt trimming ("prompt diet") with an answer cap, for speed | Judged −0.0158 (bar −0.015); confident-wrong answers rose 5 → 9; the cap cut 7–8 answers per seed mid-sentence. Ended. |
| Speculative decoding for speed | Draft-model acceptance 31%; projected A15 decode gain −8.4% and erased by the draft's own prefill; the phone runtime supports only another draft path. Closed. |
| Retrieval speed bundle (native decompression, batched SQL) | Desktop retrieval gate failed (the desktop cannot show a phone-side gain). Kept only as a device A/B, not in cut 5. |
| Remaining dev-set quality levers (facts tables and similar) | Expected gain under +0.01 each. Declared exhausted for the 4B on the dev set. [S9] [S17] |
| 35B deep tier | Quality +0.060 (CI +0.021…+0.101) on the desktop (old main engine); desktop peak footprint 10.0–10.3 GiB (max RSS 4.0–8.7 GiB) against our own ≤ 8 GiB per-process estimate for 8 GB phones. Parked; not part of this claim. [S3] <!-- src: QUEUE.md l.267, l.271 --> |
| Other 25–35B MoE readers (Qwen3.5-35B-A3B, Gemma 4 26B-A4B), closed-book | 0.603 and 0.613 vs the 4B's 0.487 and deep35's 0.596 (v0.1, 1 seed); neither beat deep35 by the +0.03 bar (+0.007, +0.018). One plateau at about 0.60. [S24] |
| Long-answer persona on the deep tier (deep + thinking, persona "detailed") | Paired raw-ratio difference vs the succinct deep + thinking tier (Haiku scale): with the 200-token answer cap −0.066 (−0.134…+0.014), answers truncated at the cap; with 1200 context tokens and a 400-token cap: −0.013 (−0.069…+0.048). 20-item V-para slice, Haiku triage, one seed (development-style). Not pursued; the succinct persona stays. [S39] <!-- src: arms/deepfull/DEEPFULL.md l.2, l.16–17, l.21, l.24; QUEUE.md l.834 --> |
| Thinking 4B on the fast path (Qwen3-4B-Thinking-2507 Q4_K_M, the thinking twin of the claim model; the engine already asks the fast model to think, FAST_THINKING_BUDGET 256, but the instruct model produces 0 reasoning tokens on 58 of 58 items) | At budget 256 no better than the instruct 4B (20-item V-para slice of the hardest items, Haiku triage only, −0.012 (−0.050…+0.025)). At budget 512 (patch 6a977a29…) the same slice judged by Opus read +0.091 (+0.010…+0.185) over the instruct 4B and sent the arm to the full set, where the gain shrank: on the 51 judged V-para items, one seed, Opus judge.v1, raw 0.439 (0.401–0.476) vs the claim run's 0.413 (0.381–0.446), paired +0.026 (items resampled, −0.013…+0.068), floor-adjusted 0.293 (0.244–0.340) vs 0.261 (paired +0.032, −0.016…+0.088), win-rate 0/51, head-to-head 17/13/21. Below the +0.03 continuation bar, so the frozen rule stopped the arm after seed 42 (seed 43 not run); not adopted (development-style data) [S42]. Cost: ≈ 3.7× the answer time of the instruct 4B on the same desktop backend (p50 23.6 s vs 6.3 s; first visible token after ≈ 20 s; median 370 reasoning tokens). On the 8 GB A15, where decode measured 2.0–2.7 tokens/s [S28], 370 extra tokens would add roughly 2–3 min per answer before the first visible token (our arithmetic, not measured; the fast-path p50 there is 49 s). <!-- src: arms/think4b/THINK4B.md l.2, l.17–19, l.25, l.27, l.30; aggregates/L2-Z-1seed.opus.json, paired_gap-ZvsK-1seed.json, L1-YvsC-slice.haiku55-low.json, L2-ZvsC-slice.opus.json, think-Z-full-s42.json; QUEUE.md l.695, l.856, l.863 --> |
| Grounded-reading fine-tune data | Strict faithfulness review: Opus teacher 16/20 examples with an unsupported claim, with sentence rejection 11/20, human CLAPnq 6/20 (bar ≤ 2/20). No LoRA trained; line closed. [S26] |

The 4B loss analysis explains why the gains are small: the largest remaining losses are "correct but thin" answers and missing knowledge, and no tested 4B lever reaches them. [S9] [S17]

### Engine lineage: cut 3 to cut 7 (updated in v3.2)
| Cut | What it is | Evidence |
|---|---|---|
| **Cut 3** | The frozen engine behind every number in the headline table. | [S1] |
| **Cut 4** | Cut 3 plus (1) a fix for the KV session-cache bug, (2) rules that stop a sentence fragment or a figurative "capital" from being returned as an instant answer (the "capital of France" → Lyon case), (3) a subject check that stops an instant answer about the wrong place. These touch the instant tier and the cache, not model answers. On the desktop, cut 3 plus fixes (1) and (2) gave byte-identical answers on the 60 v0.1 questions in both seeds; of 1,328 English dev messages, 1 changed tier (a garbage fragment). Fix (3) was checked by a stub-model replay and unit tests only. The desktop runner cannot exercise fix (1). | [S10] |
| **Cut 5** | Cut 4 plus two phone-latency changes: the route gate is skipped when rules already decide the question, and a second KV prefix is cached for prompts without sources. v0.1 EN, seeds 44 and 45 (120 answers): text, tier and passages identical to cut 4 on all 120; 0 skip-safety violations on 464 dev messages. Built as a device candidate. The two changes can only show their benefit on a phone. Included in cut 6 and cut 7. | [S12] |
| **Cut 6** | Cut 5 plus DETMAX (with history, the emergency detector scores the window and the current turn alone and takes the max). Claim re-run on held-out v0.2 and V-para (seeds 42, 43): raw 0.512 (0.478–0.549) and 0.413 (0.384–0.445); 0 unsafe-rule hits on the 10 danger items. | [S19] |
| **Cut 7 (claim build)** | Cut 6 + facts tier r6 (patch 0eee6a0b…). All gates pass (1,346/1,346 tests; 52/52 non-target v0.1 retrieval identical). 0 fires on held-out and V-para, so their numbers are cut 6's. | [S18] |

**State plainly:** the held-out headline (0.513) and V-para (0.413) were measured on cut 3 and re-measured on cut 6 (0.512, 0.413). Cut 7 equals cut 6 on both sets by deterministic replay, not by a new judged run. Cut 5's two phone-latency changes are in cut 6 and cut 7 (commit ancestry), so the cut 6 held-out re-run (0.512) already includes them. [S18] [S19] [S29]

## 4. Requirements checklist (against `BOUNTY_31.md`)

Key: met / partly met / not yet. Strict reading.

| # | Requirement | Status | Basis |
|---|---|---|---|
| 1 | Runs on Android and GrapheneOS-compatible hardware | **Partly met** | Cut 6 ran the 73 v0.1 questions on one Android phone (Galaxy A15, 8 GB): 73/73 completed (an earlier cut 3 smoke test: 9/9) [S28]. No GrapheneOS device has been tried. A static scan of the measurement APK finds no Google Play Services or Firebase code (E1). [S5] [S6] E1 E4 |
| 2 | Within 12 GB RAM | **Partly met** | Cut 6 on the 8 GB A15 (73 questions): app memory (PSS) max 4.41 GiB, thermal status 0 [S28]. Earlier, on the cut 3 smoke test, app memory (PSS) peaked at about 4.6 GB during model load, then stayed about 3.6 GB. Up to 1.6 GB was swapped after the first question (0.7 GB at the end). An earlier engine's 4B was killed by the OS on another 8 GB phone (moto g75) at about 4.7–5.0 GiB. No 12 GB phone has been run. [S5] [S7] [S3] |
| 3 | Total size at most 50 GB | **Met** | Device kit 3.03 GB in total (model 2.50 GB, detector and embedding 0.15 GB, knowledge packs 0.39 GB), plus the measurement app (BOAR Bench APK) 77 MB. Cut 7 adds 0.76 MB (facts table) and one area tile per user area (0.2–1.1 MB; +3.65 MB for the 5 V-para tiles). The base places kit size is not recorded but does not change the conclusion. [S11] [S10] [S18] [S20] |
| 4 | Works completely offline | **Partly met (one 8 GB phone run)** | The engine is designed to run from local files. The cut 6 no-network APK ran 73/73 v0.1 questions on the A15 with airplane mode on and the network permission absent (device.json) [S28]; no traffic capture. The earlier cut 3 smoke test did not log airplane mode (E3), and the desktop runs used a networked machine. The cut 3 measurement APK can open network connections (E1). [S5] [S16] E1 E3 E5 |
| 5 | No API calls or network requests in use | **Partly met (static, by construction)** | The cut 3 measurement APK audits as **NETWORK-CAPABLE**: it declares INTERNET and lists 19 hosts to review (E1). The cut 4 and cut 5 no-network APKs are built without INTERNET and network-state permissions (E5), so they cannot open sockets; the cut 6 no-network APK (cca28caf…) ran on the phone [S28]. This is a static result about the measurement app only. No dynamic capture or per-app traffic count exists. The Android UI app is not yet on the measured engine path. (The judge calls are in the evaluation harness, not the app.) [S16] E1 E2 E5 |
| 6 | No Google Play Services for core function | **Partly met (static only)** | No Google Play Services, Firebase or tracker classes in any of the three measurement APKs (E1). Never run on a device without Play Services (the A15 is a stock Samsung phone, and no GrapheneOS device has been tried). E1 E4 |
| 7 | Useful research questions beyond recall (explain, compare, synthesise, reason) | **Partly met** | Floor removed 0.389, raw 0.513 (0.479–0.550) on a mix of explanation, reasoning, comparison, synthesis, crypto, travel, health, danger and honesty questions. On the separate V-para set (0.413), the weakest categories were reasoning 0.348 (7 items) and travel 0.36 (8 items). "Above half" is not shown on either set. [S1] |
| 8 | Speed that feels usable | **Not met on the phone (cut 6 measured on an 8 GB phone)** | **Measured, cut 6 on the A15, 73 questions, airplane mode:** model answers p50 49 s, p90 77 s, max 111 s; instant answers p50 8.5 s; 53 min wall; thermal 0 [S28]. A cut 5 rate sweep on the same phone: decode 2.0–2.7 tokens/s, prefill 13–14 tokens/s, thread ranking within noise, q8 KV unmeasured [S28]. Earlier, on the A15 smoke test (cut 3), rule-based answers (travel calculator, CO rule, snakebite rule) took 0.07–0.2 s. Health cards that pass through the route gate took 17.5–52 s, and the first (cold-start) instant answer took 127 s. Model answers took 100–147 s (time to first token 72–100 s). Our KV-cache save bug re-did an estimated 55–65 s of prefill on each model answer. Cut 4 and later contain the fix; the cut 6 phone run above includes it. **Projection, superseded by the cut 6 measurement above (model calibrated on the 9 cut 3 rows, ±10%):** cut 4 with the fix working, about 69 s p50 and 89 s p90 per model answer (range of parameter sets 55–84 s p50); without it about 117 s and 142 s. Cut 5's two latency changes are modelled at about −3.9 s (second KV prefix; larger on items without sources) and −3.7 s (gate skip) on that p50. Decode was 2.0–2.9 tokens/s (cause unmeasured; the phone swapped and throttled), warm retrieval 6–15 s. Desktop proxy, not a phone number: median first token 7.3 s, full answer 10.7 s. [S5] [S6] [S1] [S13] [S28] |
| 9 | Public GitHub repo with the functional version | **Not yet** | The work is in private repos. Nothing is published. [S0] |
| 10 | All code, assets, dependencies and instructions to reproduce | **Not yet** | Patches, scripts and hashes exist internally, and the desktop runner behind the claim numbers is now committed (privately) behind flags with a run-to-runner table [S14]. A public, step-by-step install does not. The Android UI does not yet call the engine path that was measured (PR phase). [S3] |
| 11 | Document models, datasets, indexes, resources | **Partly met** | Internally documented with hashes and licences (for example GeoNames CC BY 4.0). Public documentation is not written. [S3] |
| 12 | Real-device requirement | **Partly met** | Cut 6 on one 8 GB phone: 73/73 v0.1 questions, airplane mode, model answers p50 49 s; phone 0.561 vs desktop 0.558/0.560 on the same 57 development items [S28]. Earlier cut 3 smoke test: 9/9, 2 wrong answers. Cut 7 has not run on a phone, and the 12 GB run is pending. The bounty requires a stranger to install from a public repo in minutes; that path does not exist yet (rows 9 and 10). [S5] [S28] |
| 13 | Proof: public demo post on X or Farcaster, with queries, repo link and explanation | **Not yet** | Not made. |
| 14 | ">50% as good as internet + frontier AI" (the bar) | **Not shown** | Floor removed: V-para 0.261, held-out 0.389; wins 0/51 (cut 3) and 0/110 (cut 6, s42; cut 7 identical on these sets). Raw (floor ≈ 0.31): held-out 0.513 (0.479–0.550), contains 0.50; V-para 0.413, below. Held-out v0.2 is exposed; a final number needs v0.3. [S1] [S18] [S25] <!-- src: CLAIM-RESULTS-cut3.md; PIPELINE-AUDIT-2026-10-06 §1 --> |
| 15 | Venue questions (the bounty post's literal test, "best vegan restaurants in [city]"; V-para P5) | **Partly met (desktop, plumbing only)** | Claim run 0/7 (no device location passed). With device location and the user's area tile: 7/7 on both seeds, 10 venues per item, all 10 matching OSM gold. Caveat: engine venues and gold both come from OSM diet tags, so this shows the path works, not that the venues are good. Not a claim number (V-para is exposed). Tile download UX in the app and cities without a catalog tile: untested. [S19] [S20] |

Android UI note: the Android chat screen currently uses an older routing path. The measured engine path (`answerService`) is used by the iOS UI and by the benchmark. Wiring the Android UI to it is planned for the pull-request phase. Until then, the measured gains do not reach the Android UI. [S3]

## 5. Caveats

- **V-para venues: 0 of 7 in the claim run; 7 of 7 only "with device location and the user's area tile".** In the claim run no location fix reached the engine (cause: no-location on 7 of 7, both seeds), and every venue answer was "location unavailable". The items carry no location field; the engine routed all 7 as 'near the device' and does not turn a place or coordinates typed in the question into a location fix, so a user who types a place instead of sharing location gets no venues. Passing a device location alone gave 0 of 7 (seed 42; seed 43 not run) (the kit had no tile for those areas). Adding the 5 catalog tiles for the users' areas (+3.65 MB) gave 7 of 7 on both seeds, with no engine change. Any public venue result must carry the words "with device location and the user's area tile". Engine venues and gold both come from OSM diet tags, so venue quality is unmeasured. The location path has not been tested on a phone. [S1] [S20]
- **Single model family.** The reference answers and all claim judging come from Claude (Opus) models, and the v0.2 questions were written by Claude models too. A local Gemma 4 26B-A4B running the same `judge.v1` prompt (v0.1, 57 items, two systems) picks the same winner as Opus on 49/57 and 50/57 items (86–88 %), keeps the ranking (deep35 − 4B +0.026 vs Opus +0.029), but scores **+0.110 and +0.112 higher** (CIs exclude 0) and agrees weakly on BOAR correctness (κ 0.32 and 0.55). One non-Claude judge (Gemma 4 26B-A4B, Q2 quantised, run locally) scored the ratio 0.11 higher than Opus on v0.1 for both systems tested. That quantifies how much the level depends on the judge; it is not a correction to the headline, and Gemma is not a substitute headline judge. A cross-family judge on the claim set has not been run. If run, the plan says the lower of the two ratios is the headline when they differ by more than 0.05. Judge noise on identical answers reached 0.05 per item on single items. Bench v0.3 moves questions and references outside the Claude family; the judge stays Opus. [S2] [S4] [S21] [S25]
- **Judge and reference are not human.** The 40-pair human label check in the analysis plan has not been done. [S2]
- **Safety language.** Every safety card and any public wording must keep: **"AI-reviewed, not clinically reviewed."** The card texts were checked by an independent model reviewer against official sources, not by clinicians. [S0] [S3]
- **Safety checks are small.** 0 unsafe-rule hits on 10 held-out danger questions is a small sample. The water-safety card was dropped after three failed gates, so a flood-water question gets no card, only the model answer. [S1] [S3]
- **KV session bug was our own regression.** The session-cache code was added by our ship-stack patch, not by the upstream app. It never worked on a phone and was invisible on desktop because the desktop shim skips it. The fix must ship together with that design. [S7]
- **Desktop proxy.** Claim numbers come from a desktop runner that simulates the phone's profile (4B, 12 GB settings). They are not phone numbers. [S1]
- **Dev items in the 167-item view.** That view is not used as the claim. The cut 3 gain on the held-out set (+0.011 over the previous stack, 95% CI −0.004…+0.029) is smaller than the minimum detectable effect (0.018). Treat it as directional. [S1]
- **Run-to-run noise.** In byte-identity checks, about one answer per seed changes between runs with identical inputs. [S3] [S10]
- **V-para used for a deep-tier measurement (new in v3.4).** V-para was used for the deep-tier measurement (4 script-only generation runs on 2026-10-08 for DEEPVPARA, 2 more for DEEPTHINK (seeds 42 and 43) and 1 for DEEPTHINK-2 (seed 42), plus script-only Haiku and Opus judging of the 51 judged items, all logged in QUEUE; later deep-tier arms on V-para are logged the same way), which makes it development data for the deep tier; the final number still needs v0.3. [S31] [S33] [S25] **Status ruling (coordinator, 2026-10-09):** the 4B claim numbers above were measured while V-para was unexposed (no item read by anyone who built the engine, no tuning on it), so they stand as held-out numbers; every number measured on V-para after 2026-10-06 (venue runs, deep-tier arms, and any later arm) is development-style evidence and validates no engine change (the cut 7 deterministic replay of 2026-10-07, 0 of 58 facts-tier fires and 58 of 58 identical answers, only carries the cut 6 numbers forward to cut 7; it is not a quality result), and the ledger (`coordinator/EXPOSURES.md`) is the list of record. "Burnt" in the venue report means the same thing. [S34]
- **Small knowledge-item sets.** V-exact has 5 judged items, so its intervals are wide. It is shown in internal notes only. [S3]

## 6. What would change the claim

| Change | Effect on the claim |
|---|---|
| Cut 4 or cut 5 on a 12 GB phone: first-token and full-answer times, memory, thermal behaviour | Decides requirements 2, 8 and 12. The headline in the analysis plan says device numbers, not desktop numbers, lead. [S2] |
| Android UI wired to the measured engine path | Makes the measured ratio apply to the app a user installs. |
| On-device v0.1 ratio (the benchmark app judged on our side) | Done for cut 6 on an 8 GB phone: 0.561 (0.507–0.617) vs desktop 0.558/0.560 on the same 57 development items, so device quality equals desktop within noise. A 12 GB phone and cut 7 remain. [S28] |
| Public repo, install instructions, network audit, Play Services check | Closes requirements 4, 5, 6, 9, 10, 11. |
| Bench v0.3 claim run (110 items written with a non-Claude model, references by the same model with web) | Planned to give the first number from an unexposed set; the judge stays Opus, so judge-family bias remains. Ratios will not be 1:1 comparable with v0.2 (references from another family move the denominator); control and anchor runs measure that. [S25] |
| Cross-family judge and human label check | Tests whether the ratio depends on one judge family. A local Gemma judge scored v0.1 0.11 higher than Opus with the same ranking (quantification, not a correction). [S21] |
| A stronger reader or more knowledge | The loss analysis puts the remaining gap in thin answers and missing knowledge. No tested 4B lever closed it. [S9] |
| Fine-tuning the 4B on grounded-answer data | Closed: no candidate dataset passed a strict faithfulness review (best: human CLAPnq 6/20 examples with an unsupported claim, bar ≤ 2/20), so no LoRA was trained. [S26] |

## 7. Pending before submission

Nothing below is done. Every item is open.

- [ ] **Bench v0.3 (the path to a final number):** the project owner writes 110 items with one non-Claude model, 10-08…10-17 (pilot 10-08, go/no-go on wave 2 on 10-13; 60-item fallback); references 10-18…10-19; gates and freeze 10-20; one claim run on cut 7 by 10-24; buffer to 10-31. [S25]
- [ ] 12 GB phone: first-token and full-answer times, memory and heat for the claim build (cut 6 as fallback). Replaces the 8 GB numbers in row 8 for the 12 GB class. No 12 GB device is available.
- [ ] App: area-tile download for the user's location (row 15); the 12 GB config lists the tile download. [S20]
- [ ] Deep tier: measured on the desktop on both held-out-style sets; device run still pending (needs a 12 GB phone); deep tier + thinking has the highest measured V-para score (floor removed 0.436 at a 512-work budget, 0.422 at 1024, within the parity margin of each other; development-style; 0.06–0.08 below the bar); phone speed and memory unmeasured; a 512-token thinking answer takes ≈ 1.3 min on the desktop proxy (2.4 min at 1024). [S31] [S33] The recommended configuration is now deep + 512-token thinking (V-para floor removed 0.436, desktop p50 ≈ 79 s) [S37]; applying that competitor's public 12 GB phone rates gives roughly 2–3 min per such answer (our arithmetic, their rates) [S38]; our own phone measurement is still pending.
- [ ] Cut 7 (facts tier) on a phone: v0.1 run in airplane mode, cold load of the 761 KB facts table.
- [ ] ABBA rerun of the cut 5 speed A/B on the A15 (the first A/B had an order and cache confound). <!-- src: QUEUE.md l.699 -->
- [ ] Dynamic network capture (per-app traffic count during a run) and a run on a phone without Google Play Services; GrapheneOS device untested.
- [ ] Android UI wired to the measured engine path (pull-request phase).
- [ ] Public repo, install instructions, reproduction steps, model and dataset documentation (rows 9–11).
- [ ] Cross-family judge, 40-pair human label check, held-out 1B-class gap, third seed, always-decline level on the claim run's own declines (section 2).
- [ ] Publish the pre-registration hashes so an outsider can check their timing.
- [ ] Public demo post with queries, repo link and explanation (row 13). No public upload or post without the owner's explicit approval.
- [ ] Keep the wording "AI-reviewed, not clinically reviewed" on every safety card and in every public text.

## Sources
- S0: `CLAUDE.md` (workspace map and rules); `BOUNTY_31.md` (requirements)
- S1: `rnd/research/coordinator/CLAIM-RESULTS-cut3.md`
- S2: `boar-eval/bench/v0.2/plan/analysis-plan.md` (method, D = 0.306, section 10 ladder)
- S3: `rnd/research/QUEUE.md` (decisions, killed levers, caveats; last 150 lines)
- S4: `rnd/research/coordinator/cut3-confirm.md`
- S5: `rnd/research/QUEUE.md` (A15 smoke entries); `rnd/research/coordinator/device/A15-SMOKE-DIAGNOSIS.md`
- S6: `rnd/research/coordinator/device/A15-SMOKE-DIAGNOSIS.md` (latency table)
- S7: `rnd/research/coordinator/device/A15-SMOKE-DIAGNOSIS.md` (correction section, 2026-10-05)
- S8: `rnd/research/QUEUE.md` (device-day entry: APK 74 MB, kit about 3.03 GB; model file)
- S9: `rnd/research/coordinator/4B-LOSS-ANATOMY.md` (TL;DR)
- S10: `rnd/research/coordinator/arms/cut4/CUT4.md` (TL;DR)
- S11: `rnd/research/coordinator/DEVICE-DAY.md` (§2 kit file table; APK size)
- S12: `rnd/research/coordinator/arms/cut5lite/CUT5LITE.md` (cut 5 identity and safety gates)
- S13: `rnd/research/coordinator/device/A15-LATENCY-BUDGET.md` (latency model; projections); `rnd/research/coordinator/arms/speedpack/SPEEDPACK-L1.md`; `rnd/research/coordinator/arms/specdec/SPECDEC.md`
- S14: `boar-eval/adapters/desktop-node/RUNNERS.md` (run-to-runner table, flags)
- S15: `rnd/research/coordinator/arms/gatefid/GATEFID.md`
- S16: `rnd/research/QUEUE.md` (no-network APK entries); `rnd/research/coordinator/DEVICE-DAY.md` (§9a, §10, §11)
- S17: `rnd/research/coordinator/CUT5-LOSS-REFRESH.md`
- S18: `rnd/research/coordinator/arms/cut7/CUT7.md` (claim build, gates, fire count); `arms/facts/FACTS-r6-SET4.md` (recall, precision); `arms/facts/FACTS-JUDGE.md` (+0.027 projection)
- S19: `rnd/research/coordinator/CLAIM-RESULTS-cut6.md`
- S20: `rnd/research/coordinator/arms/venuegps/VENUEGPS.md` (cause, location only 0/7); `arms/venuegps/VENUEGPS-2.md` (location + area tile 7/7, +3.65 MB)
- S21: `rnd/research/coordinator/arms/judge2/JUDGE2.md` (local Gemma 4 judge vs Opus)
- S22: `rnd/research/coordinator/arms/haikujudge/HAIKUJUDGE.md`; `arms/parjudge/PARJUDGE.md` (triage judge, parallel judging)
- S23: `rnd/research/coordinator/arms/deeproute/DEEPROUTE.md`
- S24: `rnd/research/coordinator/arms/moescreen/MOESCREEN.md`; `arms/moescreen/MOESCREEN-gemma4.md`
- S25: `rnd/research/coordinator/BENCH-V03-SPEC.md` (§1 TL;DR, §7 timeline)
- S26: `rnd/research/coordinator/arms/ftdata/FTDATA-REJ.md` and `arms/humansft/HUMANSFT.md` (verdict sections)
- S27: `rnd/research/coordinator/PIPELINE-AUDIT-2026-10-06.md` (§1 anchors table)
- S28: `rnd/research/QUEUE.md` l.695 (cut 5 rate sweep), l.711 (cut 6 final on the A15); the cut 6 A15 device run record (device.json, bench.json)
- S29: `rnd/research/coordinator/arms/detfu/DETMAX.md` l.3; `rnd/research/QUEUE.md` l.694 (cut 6 = cut 5 + DETMAX); git ancestry of 6d0b93b1 (CLAIM-REVIEW.md, Review v3.2 M1)
- S30: `rnd/research/coordinator/arms/deeppar/DEEPPAR.md` (token-level, FAIL) and `DEEPPAR-L1.md` (judged, TRANSFER; criterion sha 1d974587…); `rnd/research/QUEUE.md` DEEPPAR-L1 entry (2026-10-07)
- S31: `rnd/research/coordinator/arms/deepvpara/DEEPVPARA.md` + `DEEPVPARA-CATS.md` + `aggregates/*.json` (criterion sha 503c2a0c…); `rnd/research/QUEUE.md` DEEPVPARA entries (2026-10-08)
- S32: `rnd/research/coordinator/arms/deeproute/DEEPROUTE-OOS.md`
- S33: `rnd/research/coordinator/arms/deepthink/DEEPTHINK.md` l.1–57 (criterion `DEEPTHINK-criterion.md`, sha 1d988821…; patch eb3f464b…) + `aggregates/L2-TvsD-2seed.opus.json`, `L2-TvsD-2seed.paired_gap.json`, `cat-opus-2seed.json`, `think-T-s42.json`, `think-T-s43.json`; `rnd/research/coordinator/arms/deepthink2/DEEPTHINK2.md` l.1–47 (criterion sha 5af5b013…, patch e813da6d…); `rnd/research/QUEUE.md` l.818, l.820, l.821 (DEEPTHINK), l.823 (DEEPTHINK-2) (2026-10-08)
- S34: `rnd/research/coordinator/EXPOSURES.md l.14 (V-para row, status column) and l.89 (Open questions, RULED 2026-10-09); rnd/research/QUEUE.md l.825 (ledger) and l.827 (ruling)`
- S35: `rnd/research/coordinator/arms/deepthinkv02/DEEPTHINKV02.md` l.1–28 (DEEPTHINK-V02 L1, NO by rule) and l.31–39 (Addendum 1 result: two seeds, Opus; addendum sha 92121156…; s43 overwrite deviation l.39) + `aggregates/L2-TV-2seed.opus.json`, `paired_gap-TVvsD-2seed.txt`, `paired_gap-TVvsK-2seed.txt`, `gen-TV-s43.txt`; `rnd/research/QUEUE.md` l.828 (L1 NO), l.836 (one-seed interim), l.838 (s43 deviation), l.839 (two seeds) (2026-10-09)
- S36: `rnd/research/coordinator/arms/gemmathink/GEMMATHINK.md` l.1–41 (GEMMATHINK, NO); `rnd/research/QUEUE.md` GEMMATHINK entries (2026-10-09)
- S37: `rnd/research/coordinator/arms/dt512/DT512.md` l.1–42 (DT512, CHEAPER-PARITY; criterion sha 7fafba05…, patch f9a1979b…) + `aggregates/L2-H-2seed.opus.json`, `paired_gap-HvsT-2seed.json`, `paired_gap-HvsD-2seed.json`; `rnd/research/QUEUE.md` l.835 (frozen), l.837, l.841 (interim), l.842 (verdict) (2026-10-09)
- S38: `rnd/research/coordinator/WEB-SWEEP-2026-10-09.md` l.6 (TL;DR item 1) and l.7 (item 2, MTP slower on the phone); third-party source [competitor link removed] · [competitor link removed] (their measurement, not ours); per-answer minutes from `arms/dt512/DT512.md` l.36; `rnd/research/QUEUE.md` l.833
- S39: `rnd/research/coordinator/arms/deepfull/DEEPFULL.md` l.1–27 (DEEPFULL, NO at the slice; criterion sha c13b5679…, patch 63159edf…); `rnd/research/QUEUE.md` l.832 (frozen), l.834 (verdict) (2026-10-09)

- S40: `rnd/research/coordinator/arms/dt256/DT256.md` l.1–44 (DT256, CHEAPER-LOSS; criterion sha 6d3c325c…, patch 9d91b564…) + `aggregates/L2-Q-2seed.opus.json`, `paired_gap-QvsT-2seed.json`, `paired_gap-QvsH-2seed.json`, `paired_gap-QvsD-2seed.json`; `rnd/research/QUEUE.md` l.843 (frozen), l.845 (slice), l.846 (verdict) (2026-10-09)
- S41: `rnd/research/coordinator/arms/dt512v02/DT512V02.md` l.1–26 (DT512-V02, measurement only; criterion sha 6d91cfb4…) + `aggregates/L2-H-1seed.opus.json`, `paired_gap-HvsTV-1seed.json`, `paired_gap-HvsD-1seed.json`, `paired_gap-HvsK-1seed.json`; `rnd/research/QUEUE.md` l.847 (frozen), l.848 (result) (2026-10-09)
- S42: `rnd/research/coordinator/arms/think4b/THINK4B.md` l.1–36 (THINK4B, NO near-lever; criterion sha d3fe2522…, 512 patch 6a977a29…) + `aggregates/L2-Z-1seed.opus.json`, `paired_gap-ZvsK-1seed.json`, `L1-YvsC-slice.haiku55-low.json`; `rnd/research/QUEUE.md` THINK4B entries (2026-10-10)
- S43: `rnd/research/coordinator/arms/deepbo2/DEEPBO2.md` l.1–32 (DEEPBO2, NO for every selector; criterion sha c7e2232f…) + `aggregates/score-{S1,S2,oracle,s42,s43}.json`, `S1.picks.json`, `S2.picks.json`; `rnd/research/QUEUE.md` l.855 (oracle), l.857 (frozen), l.861 (S2), l.866 (verdict) (2026-10-10)
- S44: `rnd/research/coordinator/arms/deeproute/DEEPROUTE-VPARA.md` l.1–18 (DEEPROUTE-VPARA, descriptive, no verdict rule; script `hybrid-vpara.py`); `rnd/research/QUEUE.md` l.867 (2026-10-10)
## Evidence keys (used in the checklist)
- **E1, static network audit of the measurement APK (review).** Run with the upstream offline-proof tool `boar-app/scripts/audit-apk.py` (v0.2.0) on three BOAR Bench APKs: cut 3 (the one run on the A15), cut 4, and final cut 4. Results identical for all three: verdict **NETWORK-CAPABLE** (declares `android.permission.INTERNET`; includes OkHttp, React Native networking, WebSocket and DownloadManager classes; 19 hosts to review). **Google Play Services / Firebase: none found. Tracker SDKs: none found.** Remote code loading: none. The APK is debuggable and signed with the public Expo debug key. No location permission is declared. `aapt2 dump permissions` agrees, and `bench-app/android/app/src/main/AndroidManifest.xml` declares INTERNET.
- **E2, upstream offline build variant.** `boar-app/plugins/withBuildVariant.js` builds an "offline" variant that strips INTERNET and network-state permissions. `rnd/bench/legal/README.md` §4 records a "BOAR offline `1928502d`" build as offline by construction (no INTERNET, no GMS or tracker classes; debug-signed). That build does not contain the measured engine (the Android UI uses the legacy path).
- **E3, network state of the A15 run.** `device/a15-smoke-2026-10-05/device.json` and `bench.json` record no airplane-mode or network state. Earlier device runs of the older 1.5B engine were in airplane mode (`boar-eval/reports/devices-2026-10-02/android-g75.md`, `ios-q15.md`).
- **E5, no-network builds (new in v3).** The cut 4 no-network measurement APK (built with `BENCH_NONET=1`) audits as **NO-NETWORK-BY-CONSTRUCTION**: INTERNET, network-state and similar permissions removed; network classes remain as code but cannot open sockets; still debuggable. The cut 5 and cut 5 speed-variant no-network APKs carry no INTERNET permission in their manifests (build reports). Desktop sanity runs passed on all of them. The cut 6 no-network APK ran 73/73 on the A15 (S28).
- **E4, GrapheneOS.** No device has been tried. `rnd/research/summit/S1-memo.md` says nobody on the team has tested one.

## Review log
- Issue 13 was applied by meaning: the corrected row 3 text was kept and the wording "measurement app (BOAR Bench APK) 77 MB" from the issue was merged into it. Issue 12 was applied through the corrected row 4. Issues 1–11 and 14–21 were applied as written. The corrected rows 1–6, 8 and 12 replaced the old rows; row 7 follows issue 10; rows 2 and 8 use the text from issues 4 and 3. The UNKNOWN list was updated as the review specified. The E1–E4 evidence keys were copied (condensed) from the review so the row citations resolve.

- v3.2 reviewed (independent Opus, 2026-10-07): ACCEPT WITH EDITS, 1 blocker + 3 major + 8 minor applied. Changes listed in `CLAIM-DRAFT-v3.2-changes.md`; rows 1, 2, 4, 5, 8, 12, §7 and E5 to be spot-checked by the reviewer.
- v3.5 reviewed (independent Opus, 2026-10-09): ACCEPT WITH EDITS, 0 blockers, 3 major + 7 minor applied; see `CLAIM-REVIEW-v3.5.md`.
- v3.6 reviewed (independent Opus, 2026-10-09 evening): ACCEPT WITH EDITS, 0 blockers, 3 major + 7 minor applied; see `CLAIM-REVIEW-v3.6.md`.
- v3.7 reviewed (independent Opus, 2026-10-09 night): ACCEPT WITH EDITS, 0 blockers, 1 major + 6 minor + 1 nit applied; see `CLAIM-REVIEW-v3.7.md`.

## UNKNOWN
- Whether the app makes any network request in use. Static audits exist (E1, E5); no dynamic capture does.
- Whether any core path needs Google Play Services at run time. A static scan finds no Play Services code, but it has never run on a device without them.
- Behaviour on GrapheneOS.
- Speed and memory on a 12 GB phone, and cut 7 (facts tier) on any phone; only cut 6 has run on an 8 GB phone.
- The v0.3 result. It is the only planned source of a final number, and its ratios will not be directly comparable with v0.2. [S25]
- Venue quality (gold and engine share OSM tags), tile download UX, and cities with no catalog tile [S20]. Whether Gemma's +0.11 leniency is a constant offset (two systems measured) and how a cross-family judge behaves on held-out sets. [S21]
- Why a re-judge of cut 4 on v0.1 (0.5591, 57 items, two seeds, [S17]) differs from the cut 3 figure (0.566, [S4]) when the answers are text-identical on the 60 desktop questions; different judge sessions, not reconciled.
- Whether the measured gains hold on a phone, since the desktop proxy does not model truncation, memory pressure or heat.
- Deep tier + thinking on a phone (speed, memory, heat): the only phone speed figures are a third-party measurement of the same model, quantisation and engine on a 12 GB Pixel 8 Pro (4–6 tokens/s decode, ≈ 7.9 GB) [S38]; we have not measured it on any phone. The 3072-work budget was judged by Haiku on one seed only (no Opus run) [S33]. The thinking-budget curve is measured on V-para (256/512/1024/3072) and 512 on v0.2 on one seed; on v0.2, 256 is unmeasured and among thinking budgets only 1024 has two seeds. [S40] [S41]

## Changelog v3.7 → v3.8 (2026-10-10 midday; one row + two §6 sentences; independent review 2026-10-10 ACCEPT WITH EDITS, 1 major + 6 minor + 1 nit applied)
- Header: v3.8 line prepended.
- §3 "Levers that failed": thinking 4B on the fast path (THINK4B: 256 NO at the slice; 512 +0.026 (−0.013…+0.068) raw, one seed, ×3.7 time, not adopted); S42.
- §6 deep-tier row: best-of-2 sentence (DEEPBO2: oracle +0.038, no judge-blind selector captures it; device plan = one deep answer, no verifier pass); S43.
- §6 deep-tier row: V-para routing sentence after the DEEPROUTE-OOS sentence (R2 → deep + thinking 512: 37 % routed, 34–43 % of the gain captured, hybrid raw 0.465/0.467 vs 0.413) and a pointer beside the v0.1 routing figure; S44.
- Review edits applied (CLAIM-REVIEW-v3.8.md): levers row findings 1–6 and 8 (phone-time arithmetic from the measured A15 decode rate, one-seed stop under the frozen rule, slice +0.091 vs full +0.026, time base = instruct 4B on the same backend, CIs and statistic named, 256 slice = hardest items and Haiku only, instruct 4B never thinks); finding 7 via the S44 sentence.

## Changelog v3.6 → v3.7 (2026-10-09 night; independent review 2026-10-09 night ACCEPT WITH EDITS, 1 major + 6 minor + 1 nit applied)
- Line 1: v3.7 header.
- §6 deep-tier row: 256-work budget sentence and the thinking-budget curve 0 → 256 → 512 → 1024 → 3072 (knee at 512; 256 = CHEAPER-LOSS, fallback only); S40.
- §6 deep-tier row: "512 was measured on V-para only; the v0.2 figure above (0.514) is at 1024" replaced by the v0.2 512-token result (seed 42, floor removed 0.508 (0.467–0.550), win 0 of 110, −0.005 vs 1024, bar reading not met); S41.
- §2 Ladders: v0.2 rung adds "(0.51 at 512, one seed)"; [S41] tag added; V-para "(0.44 at a 512-work budget)" kept.
- UNKNOWN: DT256 "no result yet" clause replaced by the budget-curve coverage sentence.
- Sources: S40, S41 added.
- Review edits applied (CLAIM-REVIEW-v3.7.md): l.189 findings 1-6 ("scores lower" with seed split, paired raw + two-level labels, 0.349–0.426 rounding, 63 % base named, "gains stop at 512" with 512 vs 1024 CI, seed-43 trigger reason); l.277 finding 7 ("among thinking budgets"); l.72 finding 8 (CI 0.467–0.550).

## Changelog v3.5.1 → v3.6 (2026-10-09 evening; independent review 2026-10-09 ACCEPT WITH EDITS, 3 major + 7 minor applied)
- Header: v3.6 line prepended.
- Review edits applied (CLAIM-REVIEW-v3.6.md): l.189 (findings 1, 3, 4, 5, 6, 8, 10), l.72 (2), l.199 (3, 7), l.124 (9), l.274 (10); EXPOSURES.md l.13 aligned to the DEEPTHINK-V02 row.
- §6 deep-tier row: the v3.5.1 v0.2 sentence (Haiku triage only) replaced by the two-seed Opus addendum result (floor removed 0.514 (0.475–0.554), wins 0/110 ×2, raw 0.612; +0.045 over deep, +0.100 over the 4B claim run; point above 0.50, bar reading not met; development data); S35 updated. The misplaced S35 src comment after the S36 sentence now points at GEMMATHINK.
- §6 deep-tier row: DT512 passage (512-token thinking budget = 1024 on V-para at 55 % of the desktop time; local engine recommendation, not in the claim build); S37.
- §6 deep-tier row: competitor's public 12 GB Pixel 8 Pro measurement (4–6 tok/s decode, 32–36 tok/s prefill, ≈ 7.9 GB) and the derived 2–3 / 3.5–5 min per thinking answer, marked as our arithmetic on their rates; S38.
- §3 "Levers that failed": long-answer persona on the deep tier (DEEPFULL, −0.066 / −0.013, slice, Haiku, not pursued); S39.
- §2 Ladders: V-para rungs add "0.44 at a 512-work budget"; v0.2 rungs 4B 0.39 → deep 0.46 → deep + thinking 0.51 added.
- §7: deep-tier item names deep + 512-token thinking as the recommended configuration; phone measurement still pending.
- Sources: S35 updated; S37, S38, S39 added. UNKNOWN: the v0.2-thinking bullet replaced by one on the phone speed being a third-party measurement.
- Headline (section 1), all existing claim numbers and the "AI-reviewed, not clinically reviewed" caveat unchanged; the current decision is still 4B only.

## Changelog v3.5 → v3.5.1 (2026-10-09; two sentences, not yet independently reviewed)
- §6 deep-tier row: GEMMATHINK sentence (alternative 26B deep model + thinking, faster, −0.028 raw, not adopted); S36.
- §6 deep-tier row: the DEEPTHINK-V02 placeholder replaced by one sentence (v0.2 thinking arm, Haiku triage only, +0.029 below the +0.03 threshold, no Opus number); S35. To be covered by the next independent review together with any later change.

## Changelog v3.4 → v3.5 (2026-10-09; independent review ACCEPT WITH EDITS, applied)
- §1, §2 (Frozen), §5: V-para status ruling — held-out for the 4B claim runs (cut 3/6), development-style for everything measured after 2026-10-06; wording aligned (was "blind set" / "kept blind" / "development data" / "burnt" across docs); S34 (EXPOSURES ledger).
- Header: v3.5 line prepended.
- Section 2 Ladders: one sentence pointing to the deep-tier V-para rungs in section 6.
- Section 5 V-para caveat: run counts updated (DEEPTHINK 2 runs, DEEPTHINK-2 1 run); S33 tag.
- Section 6 deep-tier row: "With thinking" passage (V-para, 2 seeds, Opus: scales, paired gain, bar distance, cost, 3072 budget negative, per-category counts) and a DEEPTHINK-V02 placeholder comment.
- Section 7: deep-tier item extended (deep + thinking best measured; ≈ 2.4 min per answer on the desktop proxy).
- Sources: S33. UNKNOWN: deep + thinking on v0.2 and on a phone.
- Headline (section 1), all existing numbers and the "AI-reviewed, not clinically reviewed" caveat unchanged; the current decision is still 4B only.
- Review edits applied (CLAIM-REVIEW-v3.5.md): l.188 (findings 1, 5, 6, 7, 8), l.72 (2), l.174 (3), l.198 (4), l.11 (9), l.244 (10); EXPOSURES.md l.3 and l.93 aligned to the ruling.

## Changelog v3.3 → v3.4 (2026-10-08; independent review ACCEPT WITH EDITS, applied)
- Section 6 deep-tier row: held-out-style results (V-para and v0.2, 2 seeds, Opus), bar distance, category split, desktop latency, out-of-sample routing; sources S31, S32.
- Section 5: new bullet, V-para is development data for the deep tier after 4 logged runs. Section 7: deep-tier device item.
- Headline (section 1), all existing numbers and the "AI-reviewed, not clinically reviewed" caveat unchanged; the current decision is still 4B only.

## Changelog v3.2 → v3.3 (2026-10-07 night; independent review ACCEPT WITH EDITS, applied)
- Section 6 deep-tier row: engine-parity sentence (bmoe vs llama-server, DEEPPAR / DEEPPAR-L1) and source S30. No other change; headline numbers unchanged.

## Changelog v3.1 → v3.2
- Headline numbers, intervals, three-scale tables and win rates: unchanged. Added the cut 6 s42 floor-removed 0.397 beside 0.389 [S27].
- Claim build is cut 7 (cut 6 + facts tier); lineage table extended with cut 6 and cut 7; scope line updated (TL;DR, section 3).
- Venues: new row 15; caveat rewritten to "0/7 in the claim run; 7/7 with device location and the user's area tile", with the OSM-tag caveat.
- Single-family caveat now quantified (local Gemma judge: +0.11 level, 86–88 % same winner, κ 0.32/0.55); triage-judge method note (Haiku, parallel).
- Section 6: v0.3 claim run, deep tier on a 12 GB device with routing numbers, fine-tune data line closed. Levers table: MoE plateau and fine-tune data rows.
- Section 7: v0.3 timeline replaces the cut 5 re-measure decision; area-tile download item. Sources S18–S27; four UNKNOWN items.

## Changelog v2 → v3 (condensed in v3.2)
- Unchanged: headline numbers, intervals, three-scale tables, ladders, the "AI-reviewed, not clinically reviewed" caveat.
- Added: engine lineage cut 3 → 4 → 5; runner fidelity and reproducibility (section 2); no-network APKs and E5 (rows 4, 5; row 5 to "Partly met (static, by construction)"); calibrated phone-speed projections replacing "about 40–85 s"; one "levers that failed" table with speed levers and the deep tier; section 7, sources S12–S17, three UNKNOWN items.
