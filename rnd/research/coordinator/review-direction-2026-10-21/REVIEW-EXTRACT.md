# STAND
- TARGET: DIRECTION-2026-10-21.md:6 "Gemma 4 E2B: +0.03 desktop (fewer refusals), = 1.7B on the phone (57 ids), -0.083 vs the 4B"
  REASON: Partly refuted. The numbers are not wrong. The report's own title says phone Gemma is at the '1.7B level', and device parity is shown for both Gemma (+0.001) and the 4B (+0.006), so comparing phone Gemma with the desktop 1.7B is defensible. The real defect is smaller: the sentence mixes U on MAIN 97 with the raw ratio on v0.1 57 and does not label them. The memo also leaves out that the 4B and Gem
  WORDING: Gemma 4 E2B: +0.029 U on MAIN 97 (desktop, 2 seeds), mostly from fewer refusals. On the Pixel 8a (raw ratio, v0.1 57) it matches desktop Gemma and is not distinguishable from the desktop 1.7B (+0.008, CI -0.020..+0.039; no 57-id phone 1.7B run). It is 0.083 below the phone 4B. On MAIN the 4B leads it by +0.048 U overall but is level in default mode (-0.005).
- TARGET: DIRECTION-2026-10-21.md:41 "Model screens below 4B: 9 arms, 0 adopted" (GATE v2 as stop basis)
  REASON: GATE v2's own author says to recalibrate before using the gate for a decision that matters, and no third null exists. A NO at stage 1 means 'below +4..+6 net', not 'no effect'. One mitigation applies: Gemma, Ministral and granite reached stage 2 on MAIN 97, so the verdicts on those three do not rest on the screen alone. Granite's K0 GO followed by a flat stage 2 is consistent with a false GO.
  WORDING: Model screens below 4B are parked as a priority call. Stage-1 NOs mean 'below +4..+6 net fixes', on a screen with about 15 % false GO that was never recalibrated with a third null. Gemma, Ministral and granite were measured at stage 2.
- TARGET: DIRECTION-2026-10-21.md:3, :6, :41 (all model verdicts Haiku-only)
  REASON: Confirmed. Every model delta comes from Haiku 5.5-low, which the project documents as compressing gaps. CE-OPUS validated only the CE labels (CE-unwarned is judge-robust), not the U deltas.
  WORDING: All model deltas are Haiku-only. Haiku compresses gaps, so parity readings lean toward the null. CE-unwarned is the judge-robust error metric (Opus agreement 45/47).
- TARGET: DIRECTION-2026-10-21.md:8 "CE-unwarned 10 -> 4 of 177, 0/15 false refusals, U on shown answers +0.030"
  REASON: Confirmed. The memo leaves out the costs and caveats that the report itself states: per-set CIs touch 0, coverage falls 0.435 to 0.328, correct answers shown fall 37 to 32, and the result is one seed with Haiku labels.
  WORDING: Gate: visible confident errors 10 to 4 of 177 (pooled; per-set CIs touch 0), at the cost of 5 correct memory answers (37 to 32 correct shown) and coverage 0.44 to 0.33. One seed, Haiku labels, +9 s projected on the Pixel.
- TARGET: DIRECTION-2026-10-21.md:21 A1 done-when "AUC >= 0.90 at <= 3 s projected Pixel"
  REASON: Confirmed. With 37 positives and 87 negatives, the Hanley-McNeil SE of an AUC near 0.90 is about 0.035; GATELAT's V0 CI was 0.883-0.974. The 124 labels have already been used to compare V0 to V3h. A retrained adapter needs a new threshold, and the memo gives no rule for choosing it.
  WORDING: A1 done when, on held-out labelled answers: AUC with a lower CI >= 0.85, a threshold fixed by a pre-frozen rule on a separate split, and the RU rule passing at that threshold (CE-unwarned drop with CI high < 0, false refusals <= 15 %, correct-shown loss reported), at <= 3 s projected.
- TARGET: DIRECTION-2026-10-21.md:22 A2 "20-item check ... same CE-unwarned drop on his traces"
  REASON: Confirmed. At a 5.6 % base rate, 20 items hold about one CE-unwarned answer, so 'the same drop' cannot be observed.
  WORDING: A2 = port parity: on the same 20 contexts, his build's gate P(FAIL) and decisions match ours (>= 19/20 identical decisions). The effect claim stays with the desktop 177.
- TARGET: DIRECTION-2026-10-21.md:28-29 B1/B2 done-when
  REASON: Confirmed. Neither task names an MDE or a GO bar. B2 measures on pack-written self-tests, which the RU criterion calls an upper bound. One mitigation: the A-union packs differ from the LITEPACKS K packs (no simplewiki), so B2 is not a pure re-measurement.
  WORDING: Freeze before B2: MDE about 0.03 (one seed, n 80); GO = dU >= +0.03 with CI low > 0 and no MAIN 97 drop worse than -0.02. Label the 80 pack-written results as an upper bound.
- TARGET: DIRECTION-2026-10-21.md:9 "Knowledge coverage is the ceiling"
  REASON: Confirmed, and the memo is also inaccurate on one count. It says '10/20 have the fact in no pack', but the report says the fact is in neither of the new packs (simplewiki, top-100k). Two of those 10 (cry-005, trv-003) have it in K0's own packs, unretrieved. Presence was checked only at article level.
  WORDING: Among 20 no-source confident errors, the largest single cause is a fact missing from the new packs (10/20, CI about 30-70 %; 2 of those are in K0 packs but never retrieved), ahead of pre-retrieval routing (4/20).
- TARGET: DIRECTION-2026-10-21.md:42 "RETV1ORC, VENDORSAMP, SHORTCTX2, LITE17 all null-band"
  REASON: Confirmed. The four results are of different kinds. SHORTCTX2 was harmful, and VENDORSAMP ran on the old under-powered screen.
  WORDING: LITE17: no effect beyond +-0.02. RETV1ORC: below the null. SHORTCTX2: harmful (U_cov -0.13, 6/20 false refusals). VENDORSAMP: near no-op, measured on the old screen. All parked.
- TARGET: DIRECTION-2026-10-21.md:36 C2 "key-point extraction once + majority of 3"
  REASON: Confirmed. Judge v2 already extracted key points once and already scored a majority over 3. The report's rework options are different, and the memo drops the SD clause.
  WORDING: C2: v2.1 = JUDGEV2 option (a), mean of PRESENT shares over R = 3, plus option (b), numeric points with a tolerance or date. New frozen criterion with both clauses (CE test-retest >= 0.974 AND item SD <= 0.60x v1) plus a v1/v2 validity check, tested on answers other than the 97 already used.
- TARGET: DIRECTION-2026-10-21.md:6 (Gemma as best sub-4B swap, selection)
  REASON: It stands only as a minor omission. The fresh-seed replication (+0.030) and granite's flat stage 2 on the same control show the selection bias is small.
  WORDING: Gemma is the best of about 9 candidates. A fresh-seed confirm replicates (+0.030), so the selection discount looks small (about 0.01).
- TARGET: DIRECTION-2026-10-21.md:3, :32 "The deliverable the judges see on 10-31 is the ruler, not a model"
  REASON: Mostly confirmed. BENCH-RULER calls the ruler 'part of the submission's value', so the memo is not without basis. But the same document and the spec both say the ruler only predicts the holistic judgement and cannot replace it, and that whether judges will read it is UNKNOWN. Round 2 is the post author testing the app in person.
  WORDING: What the judges see is the app maintainer's app on an 8 GB Pixel-class phone. The ruler is supporting evidence that makes our claim checkable.
- TARGET: DIRECTION-2026-10-21.md:3, :14 planning horizon to 10-31
  REASON: Confirmed. The memo does partly account for the 10-23 window: D3 limits maintainer sends to before 10-23. But its fronts are planned to 10-31, and nothing marks which tasks can reach the judged build.
  WORDING: Split tasks into pre-freeze (by 10-22, must reach his APK) and post-freeze (claim, ruler, research page). Add a 'reaches the judged build? yes/no' column, and give pre-freeze compute only to the 'yes' rows.
- TARGET: DIRECTION-2026-10-21.md:13 D1 "8 GB default stays Qwen3-1.7B"
  REASON: Confirmed. 'Stays' is wrong for the product. The native app ships the 4B with a 1.5B fallback, and the 1.7B is not in its catalog. The 1.7B default is r4to's recommendation (GRILL Q2), not the shipped state.
  WORDING: Our recommended 8 GB default is Qwen3-1.7B. His app ships the 4B today and has no 1.7B entry, so getting it into his catalog before 10-23 is task #1.
- TARGET: Missing: native-app gap vs our engine
[private correspondence with the app maintainer, or a result of a run on his device, removed]
  WORDING: Add front 0, native parity (pre-freeze): check which deterministic layers his build carries, send one port list, and re-judge his release build on the 57 parity ids. Done when the native - cut 7 gap on no-retrieval items is within noise.
- TARGET: DIRECTION-2026-10-21.md:15, :21-23 Front A as pre-freeze lever
  REASON: Confirmed. The gate is a 1.7B-only LoRA, the shipped default is the 4B, A1 is a day of uncertain retraining, and the memo omits the coverage cost.
  WORDING: Front A is post-freeze research. Before the freeze, send only the warning line and, if it can be done as UI only, show-anyway. Always report the gate as 'confident errors 10 to 4 of 177 at coverage 0.435 to 0.328'.
- TARGET: DIRECTION-2026-10-21.md:13, :15 D3 Gemma opt-in send
  REASON: Mostly confirmed. The source makes T1 a hard gate and requires T3 before any entry text, and the memo schedules neither. One correction to the finding: the native app already renders thinking OFF by default (the 3/3 leak was in bench-app/llama.rn), so T1's risk is lower, though still unverified for Gemma's template. PSS 4.5-4.6 GB is above the 4.4 GB kill point, although the 4B also survived at a 
  WORDING: The Gemma opt-in entry is sent only after T1 (20 prompts through his build: 0 thinking markers, bounded tokens) and T3 (64 safety probes: unsafe count <= the 1.7B's), with entry text 'answers more questions, slower, needs ~1.5 GB more RAM'.
- TARGET: DIRECTION-2026-10-21.md:3, :7, :13, :41 "stop buying models / engine not model decides"
  REASON: Partly refuted. The memo already qualifies the claim as 'judged quality per second' and states Ministral's +0.06 at 3x time. But 'the engine, not the model, decides' overstates the case given the 4B's +0.076, and E4B (already in the app's catalog) is unmeasured. Downgrade to low-medium.
  WORDING: Stop screening sub-4B swaps for the 8 GB default: at the phone's speed budget nothing beats the 1.7B on quality per second. Larger models do read better (4B +0.076) at 2-3x the time. E4B as the 12 GB tier is unmeasured.
- TARGET: DIRECTION-2026-10-21.md:27-30 Front B scope
  REASON: Confirmed in substance. Competitors ship tens of GB of packs, the bounty allows 50 GB, and B3 (0 LLM, decisive) is ordered last. Comparing against a competitor team's 12 GB 35B setup is only partly relevant at 8 GB, but the coverage gap is the measured loss.
  WORDING: Run B3 first and widen it: fact reach for the 20 no-source errors under top-100k, full enwiki and the app maintainer's optional packs. Pre-freeze, ship only optional downloads that go through his pack mechanism.
- TARGET: DIRECTION-2026-10-21.md:44 "Deep tier on 8 GB: needs a 12 GB phone"
  REASON: Low severity. Parking the deep tier on 8 GB is correct, but 'needs a 12 GB phone' reads as if we had none. We have the POCO X6 (10.7 GiB), and the app maintainer's 35B scores at cut 7 level on it, +0.08 over his native 4B, at 6x the time.
  WORDING: Deep tier: parked on 8 GB. On the POCO X6 (12 GB class) the app maintainer's 35B matches cut 7 (+0.08 over his 4B, about 6x time). Present it as the >= 12 GB tier with its measured cost, and check its answer-time cap once if he ships it.
- TARGET: Missing: speed UX
  REASON: Confirmed omission. Speed is a must-have in the bounty, and the memo has no speed check on the shipped build. One correction: the 29-46 s figure is the 4B in the bench app, not his native build (native X6 p50 18.1 s; Pixel native unmeasured).
  WORDING: Front 0 adds one 9-question timed run of his release-candidate APK on the Pixel 8a (TTFT, p50/p90, PSS, LMK) before 10-23.
- TARGET: Missing: health and safety in the shipped build
  REASON: Confirmed omission. Detailed-style errors include safety errors, saferoute shipped with 3 unsafe extracts, and the app maintainer's side argued for a Detailed default.
  WORDING: Pre-freeze, check the shipped defaults (Succinct style, health warning on, first-aid/CO/water cards present). Run the 64 safety probes once if feasible, and record the result in the claim's safety caveat.
- TARGET: Missing: multi-turn / long session
  REASON: Confirmed, with low-medium severity. The late-turn loss rests on 3 sessions, and overall native = engine on longsession, but it matches the post author's top criterion, and the fix is a config-level ask.
  WORDING: Add a one-line maintainer ask with the numbers: widen the chat window or port the follow-up anchor.
- TARGET: DIRECTION-2026-10-21.md:36-38 C scope (C2 before C4)
  REASON: Confirmed, low. v1 is the working judge, v2 failed, and C4 depends on the submitted APK.
  WORDING: C2 optional this window: keep judge v1 with the family named. Pre-register that C4 scores whatever APK sha is submitted.
- TARGET: DIRECTION-2026-10-21.md:21 A1 context-first retrain gives 1.8 s
  REASON: Confirmed. The 1.8 s comes only from aLoRA mode. A full LoRA in the context-first layout is V1f (12.7 s). Training would have to mask the adapter by token span, and the repo's MLX path has never done that.
  WORDING: A1: train an activated LoRA (adapter on from the gate-turn invocation tokens). Stage 0 (half a day, 0 judge calls): confirm invocation-span masking in the training stack, run a 50-step smoke, and export a GGUF aLoRA that b11010 loads. Train fully only if all pass.
- TARGET: DIRECTION-2026-10-21.md:21 'MIT groundedness data', '1 day mini'
  REASON: Confirmed. The dataset's licence was never recorded; GATE17 records only the adapter's Apache-2.0 and the dataset's name. The BF16 base and the mlx-lm venv have both been deleted.
  WORDING: Use aaryand/context-adherence-guardrail-10k (licence to be read from its card before download). Cost: stage 0 (download, licence, re-wrap, export smoke, about 0.5 day), plus training wall time to be measured, plus 0-judge eval.
- TARGET: DIRECTION-2026-10-21.md:47 resource view (mini double-booking, disk)
  REASON: Confirmed. The mini has two generation slots, about 27-30 GiB free against a 25 GiB floor, and training alongside generation has never been measured. B1 is listed as 30 min in its row and 1 h in the resource view.
  WORDING: A1 training runs only while the generation slots are idle, after freeing at least 8 GiB of class-A files, adapter only, no merge. B1 = 30 min build plus its K1 regeneration.
- TARGET: A1 alternative 'or train a 0.6B head'
  REASON: Confirmed, low. A separate model cannot reuse the KV and must prefill about 790 tokens itself.
  WORDING: 0.6B head: projected 3-5 s on the Pixel 8a with no KV reuse and a second resident model. Eligible only if the A1 aLoRA fails stage 0.
- TARGET: A1 Done-when and '~150 Haiku'
  REASON: Confirmed. GATELAT's frozen rule also had a decision-agreement clause. A new threshold is needed. The labels exist, so the 150 calls are unexplained. B1 would change the eval contexts.
  WORDING: Done-when: AUC >= 0.90 on the 124 frozen RU contexts (pre-B1), false refusals <= 1/37 at a threshold set by a pre-frozen split rule, and <= 3 s projected. Cost: 0 Haiku (labels reused).
- TARGET: DIRECTION-2026-10-21.md:15, :22 strict mode before 10-23 and A2 2 h
  REASON: Confirmed. The gate needs the 1.7B in his catalog or a second resident model. On-device aLoRA/KV support is unverified, and A1's earliest result is around 10-23.
  WORDING: Drop strict mode from the pre-10-23 sends. A2 is conditional on the 1.7B catalog entry being accepted; otherwise it is post-10-31 work.
- TARGET: DIRECTION-2026-10-21.md:28 B1 re-baseline
  REASON: Confirmed. The rebuild changes every K1 control, its benefit is unmeasured (3.2 % of K1 v0.1 kept chunks), and pack shas must be frozen in spec §10 item 3.
  WORDING: Run B1 as a paired arm with a frozen criterion (K1 MAIN 97 + 80 self-tests), adopt only on no harm, and pin in-flight comparisons to the old shas. Do it (wikivoyage first) before the persona-map freeze.
- TARGET: DIRECTION-2026-10-21.md:36 C2 (feasibility lens)
  REASON: Same as the C2 statistics finding: v2 already used extraction once and a majority of 3, and the SD clause is missing.
  WORDING: C2 = JUDGEV2 options (a) + (b) under a new criterion with both clauses (CE test-retest >= 0.974 AND item SD <= 0.60x v1). Otherwise keep v1.
- TARGET: DIRECTION-2026-10-21.md:35 C1 signed before C2/C3/B2
  REASON: Partly refuted. Spec §10 puts the spec first in its freeze order and the persona map, judge and references later, so signing C1 first follows the spec's own order. What holds: the spec hard-codes a binary checklist judge, so a 'v1 kept' outcome of C2 would contradict a signed spec.
  WORDING: C1: sign the spec only after C2's verdict, with §6 naming v2.1 or v1 (fallback paragraph pre-written). The persona map and pack shas are frozen later as §10 item 3.
- TARGET: DIRECTION-2026-10-21.md:38, :47 C4 '9-question runs'
  REASON: Confirmed. The spec runs every arm on 75 items with two seeds for A∪ and B, which is several phone-hours (spec U8). The 9-question rule would need an explicit exception.
  WORDING: C4 needs a batch path on the submitted APK and an r4to exception to the 9-question rule: about 5-6 phone-hours. Otherwise A/C/D move to the bench app (labelled).
- TARGET: DIRECTION-2026-10-21.md:47 'Judge: ~1.6k Haiku'
  REASON: Confirmed. The figure leaves out the ruler's own scoring (two families x R = 3 x many arms) and the Codex steps that run through r4to.
  WORDING: Judge: about 1.6k Haiku for A/B/C2, plus about 3k Claude-family and about 3k Codex calls for C4, plus Opus references. The Codex steps need r4to.
- TARGET: DIRECTION-2026-10-21.md:37 C3 placement
  REASON: Confirmed. References must be archived before any app arm generates a v0.4 answer.
  WORDING: C3 done when 75/75 refs x 2 families plus the 15-item regeneration subset are archived and sha'd before C4's first run (target 10-24). Cost includes r4to (Codex).
- TARGET: Fronts overall: no dates
  REASON: Confirmed. The memo has no dates and does not mark A/B work after 10-23 as post-submission.
  WORDING: Add a dated sequence (10-21 to 10-31) with C on the critical path, the APK sha registered at submission, and A/B results after 10-23 labelled post-submission.
- TARGET: "granite-1b ... : NO-GO" (line 6)
  REASON: Partly holds, low severity. 'NO-GO' fits the K1 screens and the arm is closed. But the decisive stage-2 result is a tie with the 1.7B, not a worse model, and the memo's own TL;DR calls the pattern 'parity'. The finding is a precision fix, not a factual error.
  WORDING: granite-4.0-1b: stage-2 FAIL at parity (dU +0.000, CI -0.019..+0.020, wall 0.97x; Haiku, 1 seed); K1 screens NO-GO on citation drops.
- TARGET: "Gemma 4 E2B: +0.03 desktop (fewer refusals)" (line 6)
  REASON: The number itself is fair: the pooled +0.029 rounds to +0.03, and the refusal mechanism is supported. The memo is still incomplete: it leaves out that Gemma FAILED the frozen stage 2 by 0.002 and that K1 MAIN is null. That matters because D3 calls Gemma a 'measured' send. Medium severity is too high; low-medium fits.
  WORDING: Gemma 4 E2B: +0.029 U pooled on K0 (2 seeds, Haiku 5.5-low, dev MAIN 97), which misses the frozen +0.03 stage-2 rule by 0.002; +0.017 (CI crosses 0) on K1. The gain comes from fewer refusals; covered-item U does not move.
- TARGET: "= 1.7B on the phone (57 ids)" (line 6)
  REASON: Holds. No 57-id phone 1.7B run exists. The 'parity' comparison is phone Gemma vs the DESKTOP 1.7B. On the raw ratio, desktop Gemma also equals the desktop 1.7B (+0.007). So '+0.03 desktop vs = on phone' compares two metrics and two sets, not desktop vs phone.
  WORDING: On the raw ratio over 57 v0.1 ids, phone Gemma cannot be told apart from the desktop 1.7B (+0.008, CI -0.020..+0.039). Desktop Gemma vs desktop 1.7B is also level on that metric (+0.007). The +0.03 is U on MAIN 97, a different metric and set. Against the phone 1.7B only a 26-id subset exists (+0.055, CI -0.005..+0.117).
- TARGET: "Ministral + citation prompt: +0.06 but 3x time" (line 6)
  REASON: Holds. The +0.06 is right, but the memo leaves out that it is the only frozen stage-2 PASS of the night. '3x' is a projected phone time (mini measured 2.88x), and phone speed and PSS were never measured.
  WORDING: Ministral-3-3B + citation prompt v2 PASSES stage 2 (+0.062, CI +0.037..+0.089; 1 seed, K0, Haiku): the only frozen PASS of the night. Projected phone time is about 3x (mini measured 2.9x); phone speed and PSS are unmeasured.
- TARGET: "Model line at 8 GB is exhausted" (line 6 heading) and D1 "No more model screens below 4B until 10-31"
  REASON: Holds. A frozen PASS exists (MIN3CITE), shortlisted granite-4.0-micro was never screened, and most NO-GOs come from how the engine handles citations. Stopping screens can be a sound budget call, but 'exhausted' is not established. The memo's source report (DEEP-RESEARCH-GEMMA4 D4, l.41) itself says 'MIN3CITE PASS but 3x time'.
  WORDING: Drop-in model swaps screened under the current citation-release rules come out at parity or fail on citation drops. One prompt-adapted swap (MIN3CITE) passed at about 3x projected time. granite-4.0-micro and LFM2-2.6B are unscreened. Stopping model screens until 10-31 is a budget decision, not proof the line is exhausted.
- TARGET: "The 1.7B is the right default for 8 GB" / D1
  REASON: Holds. The decision is sound, but it rests on latency and RAM (r4to's ruling), not on quality. Three candidates beat the 1.7B on desktop U with CIs that exclude 0.
  WORDING: The 1.7B stays the 8 GB default for speed and memory. The alternatives that score higher (Gemma +0.03, mostly fewer refusals; Ministral+cite +0.06; 4B +0.08) cost 1.5-3x time and/or more RAM on the 8 GB Pixel 8a.
- TARGET: "the lexical citation check strips paraphrased [n] and turns correct answers into refusals" (l.7)
  REASON: Holds, medium. CITEFIX shows CT-1 removing in-range [n] below the 0.5 key-word bar, but no one tested whether the stripped sentences are paraphrases or truly unsupported. One cause in five is 'no reference at all'. The memo copies 'paraphrased' from the QUEUE row, so the wording comes from the log, not from new error.
  WORDING: The engine's 0.5 key-word support check (CT-1) strips in-range [n] in 74 of 105 warned answers of the failed models (CITEFIX); 21 of 105 had no reference at all. In default mode these answers become refusals (up to 7-9/20 false refusals on K1 sentinels). Whether the stripped sentences are faithful paraphrases is untested.
- TARGET: "cost +9 s on the Pixel" (l.8) / "1.8 s instead of 9 s" (l.21)
  REASON: Holds. Both numbers are projections from the mini; the gate never ran on a phone, and the 1.8 s also assumes llama.rn aLoRA/KV support that nobody has verified.
  WORDING: Projected +9.3 s p50 (12.2 s p90) on a Pixel 8a, measured 5.1 s on the mini. The context-first 1.8 s is a projection that depends on llama.rn aLoRA and KV-reuse support, which is unverified.
- TARGET: A1 premise (l.21) + UNKNOWN on MLX training fitting 16 GB (l.49)
  REASON: Holds. The dataset's MIT licence comes only from a model-card sweep. SFT4B STAGE1 already answers most of the memory UNKNOWN (4B 8-bit peaked at 10.63 GB, about 4 h per 600 it), but with 24k-char contexts runs will take longer. The phone runtime support that the ≤3 s target depends on is unverified. The AUC ≥ 0.90 bar sits below V0's 0.934 on labels that were already used.
  WORDING: A1 is plausible but unproven. Step 0: confirm the dataset licence on the HF card, and check that llama.rn supports aLoRA invocation and keeps the answer KV; without that the ≤3 s target cannot be reached on the phone. Size the run from SFT4B STAGE1 (4B 8-bit: 10.6 GB peak, about 4 h per 600 it) and plan for longer contexts. Freeze a held-out split of the 124 labels. Bar: AUC within 0.03 of V0's 0.934 with ≥95 % decision agreement.
- TARGET: D3: groundedness gate as opt-in strict mode only if A1 lands under ~3 s (l.15)
  REASON: Holds. A1's done-when is a projected latency plus an AUC proxy. D3 does not require a measured phone latency or the A2 transfer check, even though the only passing gate (RU) is desktop-only.
  WORDING: Strict mode is sent only if A1 passes, a phone run measures latency at ≤ ~3 s, and A2 shows the same CE-unwarned drop on the native path.
- TARGET: Memo l.9: "K1-COVERAGE: 10/20 confident errors have the fact in no pack"
  REASON: Holds. The 10/20 is absent only from simplewiki and top-100k. 2 of those 10 sit in K0 packs (never retrieved), and the cooking/money facts sit in the qa SE packs.
  WORDING: 10/20 no-source K0 confident errors (old CE definition, Haiku, 1 seed, article-level match) have the key fact in neither simplewiki nor top-100k. 2 of those are in K0 packs but were never retrieved, and most of the cooking/money facts are in the matching SE packs.
- TARGET: Memo l.9: "packs give +0.04...+0.07 when the question is in their domain and nothing otherwise"
  REASON: Holds, low severity. The numbers match LITEPACKS' own wording, but the memo drops the report's caveat that the self-tests are pack-written, so these are upper bounds. It also leaves out the context and latency cost.
  WORDING: +0.036 to +0.069 U on pack-written self-tests (an upper bound for on-topic use; 1 seed, Haiku-low), no change on MAIN (frozen NO CHANGE), at about 2x context tokens and desktop ttft 1.6 -> 3.9-4.4 s.
- TARGET: Memo l.9: "1.3 % of pack chunks have template holes"
  REASON: Holds, low. The 1.3 % figure is fact-bearing holes in simplewiki and wikivoyage only. Other packs differ (top100k ~0.3 %, factbook 0.06 %), and the share counting cosmetic holes is higher.
  WORDING: Fact-bearing template holes in 1.3-1.4 % of simplewiki and wikivoyage chunks (1.1-3.2 % of K1 kept chunks); effect on judged answers unmeasured.
- TARGET: Memo l.9: "8 pts of 'coverage' were padding"
  REASON: Holds, low. The number is right, but the scope is missing: K1 MAIN retrieval coverage only, by a mechanical label. Removing the padding gave no quality gain.
  WORDING: 8.2 pts of K1 MAIN retrieval coverage (8/97) came only from off-topic appends (mechanical label). That matters for the ruler's coverage definition, not as a quality lever.
- TARGET: Memo l.9 heading: "Knowledge coverage is the ceiling"
  REASON: Holds. The source report ranks content as the largest bucket and explicitly calls reading 'the ceiling once the source is there'.
  WORDING: Content is the largest single bucket of no-source errors (10/20). Routing (4) and reading (2+2, plus the crypto reading failures) remain.
- TARGET: Memo B1 l.28: holes <= 0.2 %, 30 min + ~400 Haiku
  REASON: Holds. The PACK-HOLES plan gates at ≤0.5 % (simplewiki) and ≤0.8 % (wikivoyage); the wikivoyage prototype only reached 1.50 %. The plan sends Haiku triage on the hole items first, so '~400 Haiku' has no source. The memo's resource view says 'B1 (1 h)', against 30 min in the table.
  WORDING: Gate: fact holes ≤ 0.5 % simplewiki and ≤ 0.8 % wikivoyage (frozen before the build). Cost: about 30 min build plus whitelist code and tests plus retrieval replay, then a Haiku triage of the 25 hole items (about 50 calls) before any full K1 re-baseline.
- TARGET: Memo B2 l.29: A-union on the 80 pack-matched self-tests
  REASON: Holds. The 80 self-tests include 20 simplewiki items, and A-union has no simplewiki pack, so only 60 match. LITEPACKS recommends user-selected packs, not default ones, because MAIN shows no gain. B2 has no frozen pass threshold.
  WORDING: Measure A-union on the 60 self-tests that match its packs (an on-topic upper bound) plus a MAIN 97 no-harm check, under a frozen criterion. Fix the pack shas first (persona Q3). Default-eligibility needs MAIN not to drop.
- TARGET: Memo B3 l.30
  REASON: Holds, low. K1-COVERAGE already checked top-100k and concluded that topic-matched SE packs hold the cooking/money facts. Adding those packs would make MAIN pack-matched, so it would no longer serve as the off-pack control.
  WORDING: Narrow B3 to the remaining unknowns: crypto (d/acc, Privacy Pools), the HSA/I-bond rules and the Thai route. Note that adding the qa-cooking/qa-money packs would stop MAIN from being an off-pack control.
- TARGET: Memo C1 l.35
  REASON: Holds. The review edits and the health weight 0.5 + safety gate are already in spec r1/r2. 'Grounded-only coverage' is a new change (from RETFLOOR/RETV1ORC), not a review item; the spec currently routes on retrieval coverage.
  WORDING: C1: specify grounded-only retrieval coverage as an r3 change, have the r2/r3 edits independently re-reviewed, close or explicitly defer the open U-items, then record the sha.
- TARGET: Memo C2 l.36
  REASON: Holds. v2 already used extraction once and a majority of 3. The report's proposed fixes are different (mean PRESENT share, number/date tolerance, a decision on the false-fact flag). The memo also drops the SD clause and over-counts calls.
  WORDING: Judge v2.1: aggregate the mean PRESENT share over R, give checklist numbers a tolerance or date, and decide on the false-fact flag, under a new frozen criterion. Done when CE agreement ≥ 0.974 AND mean SD ≤ 0.0172. About 400 Haiku, reusing the extraction and the v1 repeats.
- TARGET: Memo C3 l.37
  REASON: Holds, low. No source gives '1 day', and the Codex runs depend on r4to. The spec requires a 15-item regeneration subset and archiving before any app arm answers, and it states the R-D3 deviation.
  WORDING: References v2 on v0.4: Claude + Codex (Codex run by r4to), web, uncapped, frozen. Cost estimated, depends on r4to. Done when 75/75 refs exist in two families, the 15-item regeneration subset is run, and the references are archived before C4. Restate the R-D3 caveat.
- TARGET: Memo l.47: "Judge: ~1.6k Haiku over the week"
  REASON: Holds, low. 1.6k is the sum of A1 150 + B1 400 + B2 160 + C2 900. B1's 400 has no source, and C2's 900 re-counts the v1 repeats.
  WORDING: Judge: about 750-1,000 Haiku over the week, plus a full K1 re-baseline only if the B1 triage moves.
- TARGET: "Model screens below 4B: 9 arms, 0 adopted; parity is the pattern." (memo l.41)
  REASON: Holds. Two candidates beat the 1.7B with CIs above 0 (MIN3CITE PASS, Gemma +0.029). Only granite is a true parity result. D1 in the same memo proposes Gemma as an opt-in entry, which blurs '0 adopted'.
  WORDING: 9 model arms screened (Haiku 5.5-low); none replaces the 1.7B default. MIN3CITE (+0.062, stage-2 PASS, about 3x time) and Gemma (+0.029, misses +0.03 by 0.002, 1.5x time, +1.4 GB) beat it on desktop U. The rest are NO-GO, mostly on dropped [n] citations. The pattern is speed and format cost, not parity.
- TARGET: "SHORTCTX2 ... null-band" (l.42)
  REASON: Partly holds. In project usage 'null band' means below the bar (QUEUE l.1469 calls net 9 vs bar 10 'null band'), so the label alone is not wrong. But SHORTCTX2 did measurable harm (U_cov CI excludes 0, FR 6/20 over the limit), which 'null' hides.
  WORDING: SHORTCTX2: NO-GO by harm. Net 8 vs bar 9, false refusals 6/20, U_cov -0.132 (CI -0.222..-0.053).
- TARGET: "Engine fixes for paraphrasing models (CITESUP): a third of the loss, no gate flips." (l.43)
  REASON: Holds, low. The stop is defensible, but CITESUP tested only one tau, picked to keep the 1.7B identical. K1 missed by 1 false refusal and 0.002 U_cov, and the report says a lower tau needs its own criterion. So this is a parked near-miss, not a closed line.
  WORDING: CITESUP: parked. One tau tested (0.701, 1.7B-safe); K1 missed by 1 false refusal and 0.002 U_cov; K0 false refusals do not come from CT-1.
- TARGET: "Deep tier on 8 GB: needs a 12 GB phone; keep documented as the optional tier." (l.44)
  REASON: Holds. An 8 GB LES build was sent to the app maintainer for his F3, and those results are still pending (no later QUEUE row). The app maintainer already ran the 35B on the X6. GRILL Q2 assigns 'optional tier' to the 4B; deep is a third tier.
  WORDING: Deep tier: parked for 10-31. The desktop line is closed. The app maintainer ran it on the X6 (0.536 = cut 7, 6x time). The 8 GB LES build is with the app maintainer and F3 results are pending. The 4B is the optional 10-12 GB tier (GRILL Q2); deep is the third tier.
- TARGET: D3: Gemma opt-in entry as a pre-10-23 send (l.15)
  REASON: Holds. GRILL Q10 allows sends only for a stage-2 PASS, and Gemma failed stage 2. The memo builds in r4to's per-message OK (l.47), but it should name the exception and explain why the actual PASS (MIN3CITE) is not sent. Severity is somewhat lower than 'high' because r4to approves each message anyway.
  WORDING: Gemma opt-in entry: an explicit exception to GRILL Q10, for r4to to approve (stage-2 FAIL by 0.002; phone parity; 73/73, no LMK kill; PSS 4.5-4.6 GB). MIN3CITE (stage-2 PASS) is not sent: about 3x projected time, PSS unmeasured.
- TARGET: D3/Resource view: "the fixed warning line" as a pre-10-23 send (l.15, l.47)
  REASON: Holds. The warning-line proposal was already sent on 10-20. r4to's 20:24 ruling replaced it with refuse-by-default + show-anyway, and that note is drafted as OVERNIGHT Q16 (WAIT).
  WORDING: Refuse-by-default + show-anyway note (the warning line reused as the show-anyway label), drafted as OVERNIGHT Q16, pending r4to's OK. The warning line itself was already sent on 10-20.
- TARGET: D3: groundedness gate send before 10-23 conditional on A1 (l.15, l.21)
  REASON: Holds. A1 yields a new adapter, which under GRILL Q10 needs a judged stage-2 PASS. With A1 at 1 day and A2 after it, 10-23 is tight. The resource view budgets only two notes.
  WORDING: A gate send needs A1 plus a judged stage-2 rerun of REFUSE-UNSUPPORTED with the new adapter (GRILL Q10). It will likely miss 10-23; the resource view should say so.
- TARGET: Resource view: "Device: A2/A3/C4 need r4to at the phone (9-question runs)." (l.47)
  REASON: Holds, low-medium. A2 (20 items) and C4 (75-item ruler) do not fit the standing ≤9-question rule; only A3 does. Larger runs have happened (GEMMA4-PHONE 73), but r4to has to set the size.
  WORDING: A3 is a 9-question run. A2 (20 items) and C4 (75-item ruler run) need r4to to set the run size.
- TARGET: D2 / three fronts vs GRILL standing rulings
  REASON: Holds, low. GRILL's Q1/Q3 fronts all closed NO-GO, and the memo replaces them without saying so. The memo also drops GRILL task 6 (4B tier note) without listing it as parked, and reuses the letter 'C', which GRILL used for the archived safety-card front. B2 has no frozen threshold, which GRILL Q6 requires.
  WORDING: Add: 'supersedes GRILL Q1/Q3 fronts (B-HONEST, SHORTCTX, QUOTEFIRST closed NO-GO); 4B tier note (GRILL task 6) parked'. Rename front C to R (ruler). Give B2 a frozen criterion.
- TARGET: DIRECTION-2026-10-21.md:3/:6/:41 parity claims (critique)
  REASON: Holds. The CIs exclude 0 for Gemma, MIN3CITE and the 4B. Keeping the 1.7B is a latency choice by r4to, not a measured tie.
  WORDING: Below 4B, no swap gives a gain worth its cost on the 8 GB Pixel. Gemma 4 E2B: +0.03 U (CI excludes 0, two seeds, mostly fewer refusals) at 1.5x time and +1.4 GB. Ministral-3B + citation prompt: +0.06 at about 3x projected time. Granite: equal to the 1.7B. The 4B: +0.08 at about 2.7x time. Keeping the 1.7B is a latency decision (r4to), not a measured tie.
- TARGET: DIRECTION-2026-10-21.md:3 "at parity ... on judged quality per second" (critique)
  REASON: Holds. 'Quality per second' appears in no arm, criterion or QUEUE row, only in the memo. It is a post-hoc composite.
  WORDING: Drop 'per second' and report dU (with CI) next to p50 phone time. Say the 1.7B wins on a latency constraint, not on quality.
- TARGET: DIRECTION-2026-10-21.md:6 NO-GO list vs :7 (engine confound critique)
  REASON: Holds. Most NO-GOs come from false refusals caused by dropped or stripped [n], which point 2 of the memo itself names. MIN3CITE shows a prompt fix turns one of them into a PASS. So point 1's 'exhausted' holds only under the current engine.
  WORDING: Under the current lexical citation check, models that do not keep engine-readable [n] fail on false refusals. Model quality was not separated from this engine effect (one prompt fix, MIN3CITE, passed stage 2). Add this as an UNKNOWN, or make the stop read 'no more drop-in model screens until the citation check changes'.

# FALL (memo was right)
- DIRECTION-2026-10-21.md:6 "(fewer refusals)" / "not better answers" :: The memo says only '(fewer refusals)', and the confirm report supports that directly. The phrase 'not better answers' comes from the arm reports, not from the memo. The CI caveat is a fair note for the arm reports, but the memo's own wording is suppo
- "(MINISTRAL, SmolLM3, Qwen3.5-2B all failed on this ...)" (l.7) :: Refuted as a correction. The memo's claim is substantially right: all three NO-GOs were driven by dropped or stripped [n] that the engine shows behind the warning line. For Qwen3.5-2B, CITEFIX shows CT-1 removal dominates in 3 of 4 runs. The list was
- "CITESUP could only rescue a third" (l.7) and "a third of the loss, no gate flips" (l.43) :: Refuted. 'A third' is CITESUP's own reading (3 of 10 pending citations per screen), and K1 false refusals 7->5 recover 2 of 7, which is also about a third. 'No gate flips' is correct. The single-tau point is real but is covered more precisely by the 
- Memo l.10: "persona map drafted" :: Refuted as an error. The map is a draft, not frozen, and waiting for r4to's veto, so 'drafted' is accurate. The independent approval is extra detail worth adding, but the memo does not misstate anything; its UNKNOWN line already names r4to's veto.
- "LITE17 ... null-band" and filed under retrieval hygiene / sampling / prompt phrasing (l.42) :: Refuted as a material error. LITE17's three arms are true nulls (all paired CIs straddle 0), so 'null' is right. Q is prompt phrasing and S is chunk filtering, so the grouping mostly fits. Calling T (thinking) a 'reading lever' is a labelling nicety 

# RIGHT
- (Bounty #31 and the p) Closing the sub-4B model line for the 8 GB default fits the evidence. On the Pixel 8a, Gemma 4 E2B judges level with Qwen3-1.7B (+0.008, n.s.) and 0.083 below the 4B, at 1.5x the 1.7B's time and +1.4 
- (Bounty #31 and the p) Calling coverage the ceiling matches four independent sources: K1-COVERAGE (QUEUE.md:1455), CE-TAXONOMY (20 of 27 errors had no relevant source, QUEUE.md:1437), RIVALSET (the loss is in obscure subjec
- (Bounty #31 and the p) The diagnosis that the engine's lexical citation-support check turns paraphrased correct answers into refusals is real and well sourced (CITEFIX, QUEUE.md:1475; CITESUP, QUEUE.md:1485). It explains wh
- (Bounty #31 and the p) Parking retrieval hygiene, sampling and prompt phrasing is justified by repeated null results under frozen gates (QUEUE.md:1438, 1442, 1453, 1464, 1467).
- (Bounty #31 and the p) Limiting pre-freeze maintainer sends to measured, reversible items follows GRILL-2026-10-20.md:18 (Q10) and the per-message OK rule (HANDOFF-2026-10-20.md:9).
- (Bounty #31 and the p) Gemma 4 E2B as opt-in rather than default, described as answering more questions while slower, is the right product framing (DEEP-RESEARCH-GEMMA4-MOBILE:38, :64).
- (Bounty #31 and the p) The UNKNOWN line names the decisive risk: whether the app maintainer's build can still take changes after 10-23.
- (Statistics and infer) The headline error metric is CE-unwarned, which is the judge-robust one: Haiku and Opus agree on it 45/47 (kappa 0.87, QUEUE 2026-10-20 22:06), while raw CE agrees only 0.83.
- (Statistics and infer) The individual numbers are transcribed correctly: the gate's 10 -> 4 of 177 and 0/15 (RU.md:5-6), GATELAT's 1.8 s / AUC 0.66 vs 9.3 s / 0.934 (QUEUE 23:21), Ministral +0.06 at about 3x time (QUEUE 02:
- (Statistics and infer) Point 7 correctly names the engine's lexical citation check as what turns paraphrased correct answers into refusals (CITEFIX, QUEUE 01:15). That is the right causal lead, even though point 1 then does
- (Statistics and infer) D1 sends Gemma as an opt-in entry only and keeps the default unchanged. That is a reversible, proportionate response to a +0.03 gain at 1.5x time, and it follows the frozen stage-2 FAIL rather than ov
- (Statistics and infer) D3 limits maintainer sends to measured, reversible items, and makes the strict mode depend on the latency result, which matches the measured +9 s cost.
- (Statistics and infer) Parking the deep tier on 8 GB is consistent with the record: it needs a 12 GB phone (CLAUDE.md, DEEPROUTE/DEEPVPARA).
- (Statistics and infer) The UNKNOWN list states real gaps (MLX memory fit on the mini, the app maintainer build's capacity, the persona-map veto), and the C1/C2 'sha committed' / 'rule met or v1 kept' clauses keep the frozen-cri
- (Feasibility, cost an) The night's numbers it cites match the QUEUE: REFUSE-UNSUPPORTED cut confident errors 10 to 4 of 177, with 0/15 false refusals, +0.030 U on shown answers and +9 s on the Pixel (QUEUE l.1461). GATELAT 
- (Feasibility, cost an) The 'model line exhausted' summary matches the screens. Granite stage 2 gave dU +0.0003 (l.1487). Q8_0 landed in the null band (l.1469). Gemma 4 E2B on the phone matched the 1.7B and sat 0.083 below t
- (Feasibility, cost an) C2's cost of about 900 Haiku matches the measured judge-v2 pass, which used 881 calls (JUDGEV2.md:57). Judge v2 is correctly reported as NO-GO by its frozen rule (l.1458).
- (Feasibility, cost an) Parking the deep tier on 8 GB and further sub-4B model screens fits the evidence and GRILL Q2. Limiting maintainer sends to measured, reversible items fits GRILL Q10.
- (Feasibility, cost an) The memo correctly treats the ruler as the 10-31 deliverable, and it lists two real unknowns: MLX memory fit on the mini, and the app maintainer's build window after 10-23.
- (Feasibility, cost an) B2's cost (2 h, about 160 Haiku on the 80 pack-matched self-tests) is consistent with judge.v1 at 2 calls per answer (JUDGEV2.md:14).
