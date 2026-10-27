# Review of RULER-SPEC-v1-r3-2026-10-21.md (adversarial, independent)

Reviewer: independent Opus agent, 2026-10-21. I did not write the spec.
Inputs read: the r3 spec; r2 (RULER-SPEC-v1-2026-10-20.md) and its review; BOUNTY_31.md; BENCH-RULER-2026-10-19.md; ruler/DECLINE2STAGE-2026-10-21.md + criterion; REFVAR-2026-10-21.md; RV4-CITY-BOUND-2026-10-21.md; INPACK-STRATUM-2026-10-21.md; GAP-LEDGER-2026-10-21.md; QUEUE rows "JUDGE v2 ... NO-GO" (l.1458), "RULING R1" (l.1560), "r4to bar decisions" (l.1635), "A1-RC1-SHIPPED-U" (l.1617); judge-core.mjs; ruler/refs-v2/REFS-V2-criterion.md; bench/v0.4/DATASET_CARD.md; the metadata keys (not the text) of bench/v0.4/refs/v2/claude.jsonl; `git grep` of DeviceEvalRunner.kt / BenchActivity.kt at wt/native-qa 5f8cc8f4.
Not read: anything under blind/ or rnd/veil/; v0.4 item text; v0.4 reference text. No runs, no LLM calls.

## TL;DR
**Verdict: ACCEPT WITH EDITS.** The spec is not ready to freeze until G1–G6 are applied.

1. **G1 (high, honesty).** §4.2/§8 refuse to write any verdict sentence when the RC cannot install A∪, and RC1 is in that state. In practice, the only system a bounty judge can install gets no verdict. This undoes the r2 F17 fix, which was accepted. The verdict arm can stay A∪, but the card must still state a band for the system a user can actually install.
2. **G2 (high, formula).** The reference mass r_g(i) depends on the pairing, and the spec never defines it across the two generations, across arms in a Δ, or for refused answers that need a stage-2 call only to get r. So A∪ − B, pack lift, the in-pack Δ and separability compare ratios with different denominators, and a refusing arm is penalised twice.
3. **G3 (high, R1).** I **accept RULING R1 on substance, with conditions.** The two bar-(b) hits are true non-answers, and stage 1 can only lower an app's score compared with judge.v1. But the ruling overrides a frozen FAIL and its kill clause. Against the pre-registered fallback (U_net), it raises low-decline systems by about 0.04. Stage 1 has also never been checked on the native app's answers. The spec must label the override, name the U_net band when it differs, and run a 51-call audit on the RC1 answers that already exist.
4. **G4 (high/medium, validity).** The eval hook runs the "legacy pipeline (the fixed-model answer path)", without adaptive routing and with the Detailed style. So the headline may not measure the chat a user sees. The 10-item parity check covers style only, and it has no pre-registered ids and no consequence.
5. **G5/G6 (medium, re-roll).** Several levers are open: which build counts as "the newest installed RC" (r4to installs it, and two builds exist); aborted runs; a judge "re-frozen" after the decline arm fails; per-RC map and errata in the run tuple; UI-driver failure declared after answers exist; and A∪-partial decided by "installed" with no usage probe.
6. Several evidence citations are rounded the friendly way (G8): D2S denominators, the ladder stand-in, REFVAR's Haiku judge and within-family-only variance, RV4's "iff" and "up to 0.107", and the XFAM offset.

## Findings (ranked by severity)

### G1. high. §4.2 "None installed", §8 "Not scored on A∪", TL;DR 3, §11 row 2
**Problem.** When A∪ cannot be installed, the spec writes "No verdict sentence of the form 'meets / does not meet the bar' is written for that RC". RC1 is in exactly this state (0 packs, no offline import; GAP row 3), and U1 says it is the expected state. The bounty judges the submitted app as a user can install it [B31:41, 56]. If packs cannot be installed, that system is arm B (or A∪-partial). Under this rule, the most likely real outcome ("the submitted app is below the bar") is never stated as a verdict, only as a side band "not the verdict arm". A skeptic will read this as the entrant arranging never to say "fails". It also reverses r2 F17 ("if A∪ cannot install, the verdict arm is B on the APK"), which was accepted and applied. r4to's decision 1 (QUEUE l.1635) fixes which arm is the verdict arm when it exists. It does not ask for silence when that arm does not exist.
**Edit.** This keeps decision 1 as it is. Replace the §4.2 "None installed" bullet with:
> **None installed** → the band line reads **"Verdict on A∪: not scored (packs cannot be installed on RC <version>). Verdict on the RC as a user can install it (arm B): <band>."** Both sentences are always printed, in this order, in the verdict line. A "below" or "point above, not established" on arm B is written as the verdict on the submitted RC, not as a side row.

Replace the "Some installed" bullet's band text with: "Verdict on A∪: not scored. Verdict on the RC as a user can install it (A∪-partial, installed: …; missing: …): <band>. Arm B band: <band>."
Replace §8's fourth bullet with: "**Not scored on A∪** (§4.2): the verdict sentence is written on the installable arm (A∪-partial if any pack installed, else B), labelled as such; the A∪ line reads 'not scored'."
Replace §11 row 2's answer with: "If the RC cannot install A∪ through its own user flows, the verdict is written on what a user can install (A∪-partial or B), and A∪ is marked 'not scored'. Packs are never side-loaded by a path a user does not have."

### G2. high. §3.1 "Reference mass", §3.4, §3.5, §3.7, §4.1 separability, §2.3 in-pack Δ
**Problem.** r_g(i) is "taken from the same pairings as the arm being scored". This is consistent with judge-core (`summarize` sums `ref` over that arm's pairs), but four cases are left undefined or biased:
- (a) **Two generations.** A∪ and B have two pairings per reference family, one per generation. §3.7 says "the verdict uses the per-item mean of u" but never says which r is used. The bootstrap also "resamples generation seeds per item" without saying that u and r travel together.
- (b) **Refused / non-answer app answers.** u := 0, but r still needs a stage-2 call. The spec never says the stage-2 call still runs for z = 1 or n = 1. A pairwise judge scores a reference higher next to a refusal than next to a good answer (contrast). So an arm that refuses more gets a larger denominator as well as a zero numerator: a double penalty that grows with the refusal rate.
- (c) **Cross-arm Δs** (A∪ − B; pack lift L_g with "Σ w r_g(i)"; Δ_D; in-pack A∪ − B; separability). Each arm's U has its own denominator, so a Δ mixes answer quality with the contrast effect on the reference side. L_g does not say whose r it uses.
- (d) **CR_g.** "k for the reference = mean over f of the reference's correct indicator in its pairings". Pairings with which arm and which generation?

**Edit.** Replace the §3.1 "Reference mass" bullet with:
> **Reference mass**: for arm X, r_g(X,i) = the mean, over reference families f and over the generations of X that were scored, of [m_g(ref_f | X_gen, i) − 1], taken from X's own pairings. Stage 2 always runs, including for answers with z = 1 or n = 1, so that r is defined. u and r of the same generation are resampled together in the bootstrap. References are never stage-1 zeroed; a reference that stage 1 calls a non-answer is listed and counted, with no other action.

Add to §3.4:
> **Cross-arm comparisons** (A∪ − B, pack lift, Δ_D, in-pack and off-pack Δ, separability) use a common per-item denominator r̄_g(X,Y,i) = ½[r_g(X,i) + r_g(Y,i)] for both arms in the pair. The paired Δ is Σ w (u_X − u_Y) / Σ w r̄. Each arm's own U (and the verdict) keeps its own r. Every table prints each arm's mean reference mass Σ w r / Σ w, and the mean reference mass on items the arm refused vs answered (the contrast check).

Change CR_g's reference term to: "k_g(ref, X, i) = the mean over f and over X's scored generations of the reference's correct indicator in X's pairings; CR is printed per arm with that arm's reference term."
Pre-freeze, 0 calls: measure the contrast effect on existing dev judgments (reference-side mean when paired with FLOOR decline texts vs with MAIN control answers, same ids) and print it in §3.2 as context.

### G3. high. §6.2 (RULING R1), §3.4 sensitivity rows, §11 row 3
**Ruling R1: ACCEPT, with the conditions below.**
Reasons for accepting:
- Both bar-(b) hits (st-qa-cooking-se-005/018) are the engine's fixed refusal text ("I won't give health advice…") given in answer to cooking questions. Stage 1's "not attempted" label is true. The reference label (Opus correctness ≥ 3) is the documented refusal-credit leak that stage 1 exists to remove. The bar mis-operationalised "false", and the classifier made no mistake.
- On app arms, stage 1 can only lower u compared with judge.v1, and r is never zeroed. Compared with judge.v1 alone, it is monotone and conservative. In the measured cases, all 7 MAIN zeroes are refusal strings that z already zeroes.

Reasons it needs conditions:
- **(i) It is an override, not a reading.** The criterion said "no second wording", and the kill clause named JUDGE-V2.1-NI and then judge.v1 + U_net. QUEUE has no V2.1-NI run, so the ruling also skipped the first fallback. The spec's phrase "RULING R1 reads bar (b) as satisfied" hides this.
- **(ii) Direction vs the frozen fallback.** For low-decline systems, D2S U ≈ judge.v1 U, while U_net is about 0.04 lower (D2S ladder Opus: 1.7B 0.351 vs 0.312; 4B 0.460 vs 0.427). So R1 gives the entrant a higher number than the pre-registered fallback would have. R1 is still the better-founded estimator: U_net subtracts decline credit from answers that are not declines. But the band under U_net must be visible.
- **(iii) Domain transfer.** Stage 1 was validated on our engine's answers and the FLOOR texts. The scored system is the native RC (1.5B, Detailed, 1024 tokens, mostly closed-book; GAP rows 2, 6). Its long hedged answers are untested. 51 RC1 dev answers with Opus judge.v1 rows already exist (rc-cv5-51-15b; QUEUE l.1617), so a check costs 51 Haiku calls and 0 generation.
- **(iv) D is judge-specific.** D 0.058 is a Haiku 5.5-low number (CV5-RECOMPUTE O0-02). Sensitivity row (b) applies it to Opus and Codex.

**Edits.**
- §6.2, replace the last two sentences of "Evidence" with: "Bar (b) FAILED by its frozen count (2 > 1). Both hits are the engine's fixed refusal string, which stage 1 labels correctly. RULING R1 (coordinator, after the result) overrode the frozen kill clause and adopted the two-stage judge. The independent reviewer accepted the override with conditions (RULER-SPEC-v1-r3-REVIEW G3). The first fallback (JUDGE-V2.1-NI) was not run."
- New pre-freeze check (§10.4), with the criterion frozen before the calls: run stage 1 on the 51 RC1 rc-cv5-51-15b answers. Bar: ≤ 1 "not attempted" among answers that are not the RC's refusal text and have Opus judge.v1 correctness ≥ 3. If it fails, the headline is judge.v1 + U_net_g and stage 1 becomes a sensitivity row.
- §3.4 row (b): "U_net,g = (U_v1,g − D_g) / (1 − D_g), where D_g is the judge.v1-alone U of decline variant (a) under family g on the v0.4 decline arm (§4.1). Haiku's 0.058 is quoted only for the Haiku diagnostic scale."
- §8 verdict sentence: add "and the U_net band if it differs".
- §6.2 "Evidence" numbers, see G8.

### G4. high/medium. §0, §1 "Scored system", §4.3 style row, GAP row 5
**Problem.** The snapshot's DeviceEvalRunner.kt (l.43) says the hook "Runs the legacy pipeline (the fixed-model answer path)". Adaptive routing and the "answer" pipeline are not run, and the code rejects `pipeline == "answer"` (l.104-105). GAP row 5 already notes that the hook "may bypass the chat's routing". Style comes from personalities.json defaultId, not from the user setting (GAP row 2). So the headline can measure a path no user takes (model choice, routing, layers, style). The §4.3 parity check is limited to style, has no pre-registered ids, and has no consequence.
**Edit.** Replace the §4.3 "style / persona" row's "otherwise" cell with:
> The hook's style and path are recorded. A **hook-vs-chat parity check** runs on the first 10 ids of the §3.7 retest subset (pre-registered): the same question through the hook and through the chat UI (UI-driven), comparing model id, style, routing/reason code, retrievalUsed and answer length. If ≥ 3 of 10 differ in model, style or routing, every headline row is labelled "measured through the eval hook (legacy fixed-model path), not the chat path". The parity answers are judged by the diagnostic judge only and never replace headline answers.

Add to §0's recorded fields: "eval-hook pipeline name and whether it applies the chat's routing".

### G5. medium. §0, §9.3, §8 "Judge invalid", §4.3 fallbacks, §3.7 generations (re-roll and free parameters)
**Problem.** The following levers are open after exposure:
- (a) "The newest RC installed when the run starts". r4to chooses what to install and when, and the app maintainer has at least two builds (Wi-Fi downloader and full bundle; QUEUE l.1635 item 4).
- (b) "First **complete** run": an aborted run (crash, thermal, LMK) can be restarted with no trace.
- (c) §8 "no band ... until the judge is fixed and re-frozen". That is a judge revised after v0.4 answers exist.
- (d) The run tuple includes the map and errata shas, so editing either makes a new tuple with its own "first run".
- (e) UI-driver failure on multi-turn or show-anyway can be declared per item after answers are seen, and failed multi-turn items score 0 (8 items).
- (f) "Two independent runs" when the seed is not controllable: the spec does not say they are the first two.

**Edit.** Add to §9.3:
> - The scored RC is the build the app maintainer designates as the submission (or, before submission, as the current release candidate). If several builds share a version, all are listed in state.json and the team never picks between them.
> - Every started v0.4 run is logged at start (RC sha, arm, time). An aborted run is kept, with its reason and its partial answers. A restart is allowed only for the pre-registered infrastructure causes (app crash, LMK, phone reboot, thermal abort), and the item order is not changed.
> - The map sha and the errata sha are frozen once for v0.4, not per RC. Changing either voids every later number until it is re-registered, and prints as a new claim with the attempt count.
> - Generation runs are the first two complete runs of each arm.
> - A judge revised after any v0.4 answer exists is validated on dev sets only. Its numbers are labelled "judge revised after exposure", and the first judge's numbers are printed beside them.

Add to §4.3: "Runnability of the UI driver (multi-turn, show-anyway) is decided per RC on one dev conversation and one dev refusal **before** any v0.4 answer, all-or-nothing for the 8 multi-turn items. It is never decided per item after answers exist."

### G6. medium. §4.2 A∪-partial and the install attempt
**Problem.** A∪-partial is "decided by installability, never by choice", but installability is upstream of the team: NOTE-5 decides which packs the app maintainer lists, and the team runner records "failed + reason". A pack can also be "installed" but never searched, which happens if the RC reads only its own KB format. Then the band reads A∪(-partial) while the system is in effect B.
**Edit.** Add to §4.2:
> - NOTE-5 (sha recorded in §10.6) requests catalog entries for all six A∪ packs. Which packs the app maintainer lists is his choice and is logged.
> - A pack counts as **installed** only if (i) the RC's Knowledge screen lists it (photo sha) and (ii) one pre-registered dev probe query per pack, written from the pack card and not from v0.4, returns a retrievedTitles entry from that pack through the hook. A pack that is listed but not used counts as "installed, not used" and goes in the "missing" list.
> - Each install failure is reproduced once more, with a screen recording sha, before it is logged.

### G7. medium. §3.2 "Contested points", §10.2
**Problem.**
- (a) Under judge.v1, the author notes are side input. The judge compares the answer with the **reference text**, and that text still states the contested value. Dropping the point from the notes is close to inert.
- (b) Contested points cluster on dated facts (REFVAR rule 6: 3 of the 4 peripheral disagreements were dated). Dropping them helps an offline app with stale packs, and a team agent makes the call.
- (c) REFVAR's rule 4 was written for the binary checklist judge ("dropped from s"), not for judge.v1.

**Edit.** Replace "Contested points are removed from the judge's author notes for that item." with:
> Contested points are removed from the author notes, and the notes get one fixed line per contested point: "Sources disagree on <point>: '<value F1>' vs '<value F2>'. Do not penalise either value." A point is contested only if two independent agents (one Claude, one Codex), each reading the two references and the checklist, both mark it incompatible. Sensitivity row: U-total with the original notes (no errata), re-judged on the affected items only.

### G8. medium. Honesty of cited evidence (§3.2, §6.2, §2.3, §3.7, §11, §1)
I checked each number against its source file:
| spec text | source says | edit |
|---|---|---|
| §6.2 "0 of 49 Opus-correct MAIN non-refusal answers" | the 49 are MAIN answers with Opus **correctness ≥ 3**, and 2 of them are refusal strings, so there are 47 non-refusals | "0 of 47 MAIN non-refusal answers with Opus judge.v1 correctness ≥ 3 (and 0 of 27 WARN)" |
| §11 "0 false zeroes on 76 correct dev answers" | 76 = 49 + 27 including the 2 zeroed refusals; "correct" means corr ≥ 3, while the spec defines correct as ≥ 4 | "0 non-refusal answers zeroed among 74 dev answers that Opus scored correctness ≥ 3" |
| §6.2 "on the v0.1 ladder pairs move by at most 0.004" | true, but 135 of the ladder texts used the `labels.is_decline` stand-in, not stage 1 | add "(135 of the ladder texts used a 0-call stand-in labeller, not stage 1)" |
| §3.2 "REFVAR measured two independent Opus draws moving U by 0.015 / 0.008" | correct, but the judge was **Haiku 5.5-low**, on n 20 **v0.1 dev** items, with **Claude-only** draws; cross-family reference variance and the optional Codex check were not run | add "(Haiku-low judge, 20 v0.1 dev items, both draws Opus; the variance between reference families is unmeasured)". Replace "a U difference under 0.03 between the two one-family rows is read as reference noise" with "REFVAR measured within-family draw noise only (≤ 0.015); a difference between the two one-family rows is reported as a family difference, not as noise" |
| §2.3 "(possible iff U-without is in 0.50–0.56)" | RV4 derives this iff only for the 7 items **scored 0** vs excluded. If they score above 0, a flip is also possible from below (RV4: 0.44–0.56 for refusal vs tile ceiling) | "(with the 7 at zero this happens iff U-without is in 0.50–0.56; with non-zero scores it can also happen from below)" |
| §11 "up to 0.107 U" | RV4: max swing **≥ 0.107**. The share of reference mass can exceed the share of weight, and u can exceed r | "about 0.1 U (10.7 % of headline weight; dev proxy 9.8 %)" |
| §3.7 "stricter ... by about 0.10" (XFAM) | on the floor-adjusted scale this spec uses: +0.100, +0.141 (V-para), +0.129, +0.131 (v0.2) | "by 0.10–0.14 (floor-adjusted) on dev sets" |
| §1 "On RC1 it fails (no warning line, no refusal path; GAP rows 4 and 6)" | GAP row 4 = no warning line; row 6 = 0.7 cutoff, retrieval 1/51. "No refusal path" is an inference | "(no warning line, GAP row 4; retrieval on 1 of 51, GAP row 6; we observed no refusal on RC1's 51 answers)" (keep only if the rows confirm 0 refusals) |
| §2.3 "57 under A∪ ... off-pack ids (18)" | INPACK counts all 75. Two anchors are in-pack (cx-001, cx-007) and two off-pack (cx-014, cx-015), so H = 55 / 16 | "in H: 55 in-pack, 16 off-pack (57 / 18 over H ∪ anchors)" |
Checked and correct: Σ_H w = 65.5; 7/65.5 = 10.7 %; REFVAR +0.013 / +0.001 uncapped vs v1; 90/90 and 30/30; 20/20 retest; U_net D 0.058; GAP rows 2, 3, 6; the hook rejects pipeline "answer" (DeviceEvalRunner.kt l.104); JUDGE v2 NO-GO numbers (0.966 vs 0.974; 0.80x vs 0.60x).

### G9. medium. §3.5, §4.1 (diagnostic arms judged by Haiku only)
**Problem.**
- The displacement "harm only if u_g(D,i) < u_g(A,i) under both judge families" cannot be computed, because D and A are judged by Haiku-low only (§4.1 table).
- L_g "the same lift for A and B" needs C, and C is Haiku-only, so pack lift exists on the Haiku scale only.
- The separability chain includes "B ≤ A∪", which is a product result (packs may hurt). It is not a validity property of the ruler.
- "< reference" is undefined, because the reference is the denominator.

**Edit.**
- §3.5: "Pack lift, interference and displacement are computed on the Haiku-L1 diagnostic scale only and labelled so. Displacement harm = u(D,i) < u(A,i) under Haiku-low on both generations-equivalent runs, labelled diagnostic."
- §4.1 separability: "decline < 1B < B on U-total (Haiku-L1), with the decline and 1B CIs not overlapping B's. A∪ vs B is reported as a result, never as a separability failure. The reference row is the cross-family check: U of ref_F1 judged against ref_F2 (and the reverse), printed as context."

### G10. medium. §3.4 show-anyway, §3.3 multi-turn coverage, §6.2 multi-turn stage 1
**Problem.**
- "U-total, show anyway" uses the show-anyway answer "on every item the RC refused". But §4.1 generates show-anyway answers on N only, and a refusal on a covered item (C_X) has none.
- UI-driven multi-turn runs may have no retrieval trace, so kept_X(i, turn) is undefined.
- Stage 1 per turn sees only that turn's user message. For a "correction", "recall" or "drill-down" turn, the question is incomplete without the earlier turns.

**Edit.**
- §4.1 A∪ and B modes: "default + show-anyway on every refused item (z = 1), N and C alike".
- §3.3: "If a UI-driven turn has no trace, that item's coverage is 'unknown'; it is counted in M_X and listed."
- §6.2 multi-turn: "Stage 1 for turn k receives as the question the numbered user turns 1..k (an unvalidated variant of the frozen prompt, labelled). Its non-answer count on multi-turn items is printed apart."

### G11. medium. Feasibility and completion rules (§3.7, §6, §7.2, U8, U9)
**Problem.** The spec has no call budget. My estimate per family for A∪ + B:
- 75 items × 2 generations × 4 calls = 600 per arm, so 1,200.
- Show-anyway answers on refused items, both generations: up to 1,200 more.
- Decline arm 180, retest 60, harm ≈ 11 + k items × up to 8 answers × 3 repeats.

That comes to about **1,500 calls per family at minimum and about 2,900 at most**, plus about 2,700 Haiku diagnostic calls and about 700 stage-1 calls. For Codex at reasoning high on one laptop [usage detail removed] (U9), this is several times the largest Codex pass so far (XFAM-V02, 660 calls).

Phone time: RC1's answer p50 is 33 s (QUEUE l.1617), so one 75-item pass takes about 50 min. A∪×2, B×2, C×2, A and D come to about 8 passes, or 7 h before UI-driven runs, installs and cool-downs. "Several phone-hours" understates this.

The thermal gate ("battery ≤ 35 °C, thermal status 0") is ambiguous. RC1's own 51-item run went from 26.4 to 36.9 °C and reached thermal 1 after about 6 min. A per-answer gate would multiply the phone time. A per-run gate leaves most rows throttled.

Nothing says what happens if one judge family cannot finish. Dropping a family changes min(·) and is a selection lever.
**Edit.**
- Add a §10.8 budget table: calls per family per arm, caps, and phone minutes per arm.
- Add the degradation order already in U8 (D, then A, then C to the bench app), then "show-anyway on generation 43 dropped, labelled" before any verdict-arm generation is lost.
- Add: "**Both judge families must complete A∪ (or the installable verdict arm) and B on both generations. Otherwise the card reads 'judge incomplete' and no band is printed. A single family is never substituted.**"
- §7.2: "The thermal gate is checked before each arm-pass. If it is breached mid-pass, the phone pauses and resumes when the gate passes again. Thermal status is logged per row. Rows answered at thermal ≥ 2 are listed."

### G12. low-medium. §10 order vs REFS-V2, §3.2 wording, §10.4 pins
**Problem.**
- REFS-V2-criterion.md (frozen 20:36) governs the references. Five Claude reference v2 rows were already generated at 20:37 (bench/v0.4/refs/v2/claude.jsonl, untracked), before this spec was reviewed or frozen. REFS-V2 rule 1 says an ok row is never regenerated. So no edit from this review can change the reference prompt, and §10's "frozen in this order" is already broken for step 5.
- §3.2 says "Answer as of <generation date>", but the protocol frames the date as "Current date: YYYY-MM-DD".
- The Codex model id (gpt-5.6-sol, reasoning high in REFS-V2) is not pinned in the spec.

**Edit.**
- §10.5: "References are governed by ruler/refs-v2/REFS-V2-criterion.md (sha recorded), frozen 2026-10-21 20:36 and used from 20:37, before this spec's final sha. The order of §10 is stated as it happened."
- §3.2: cite REFS-V2's message frame verbatim.
- §10.4: pin "Codex: gpt-5.6-sol, reasoning high (judge), CLI version".

### G13. low. §4.1 decline arm
**Problem.**
- Variant (a), "the RC's refusal string", is undefined when the RC has none (RC1).
- Variant (c), "fluent on-topic paragraph ... length-matched", needs per-item writing from the question text, and nobody is named to write it. If the team writes it after reading the items, it can be written to be caught.
- Stage 1 is shared by both families, so "valid under every family" tests one Claude classifier twice.

**Edit.**
- "(a) the RC's refusal string, or if none, the engine refusal string used in FLOOR (a)".
- "(c) generated by a frozen prompt from one Codex call per item (question only, target length = the median reference words), hashed before any stage-1 call on v0.4, never edited".
- Add: "Also printed: each family's judge.v1-alone U for each variant (this is D_g of G3)".

### G14. low. §6.5, §7.1 safety
**Problem.**
- "Any item where either reference's text contains an explicit safety warning" is a judgement call, made after the references exist.
- The "independent reviewer agent" belongs to the team's own model family, while F7 asked for an outside or third-family confirmer.

**Edit.**
- Harm set = the 11 health_safety items plus the items where either reference matches a frozen regex list (seek medical / emergency / dangerous / do not / warning / poison / overdose / illegal), with the list hashed in §10.4.
- State: "The confirming reviewer is a Claude-family agent outside the ruler session; a third family, if one is available, is preferred."

### G15. low. Assorted definitions
- **Scale.** Add to §3.4: "U uses the floor-adjusted scale (m − 1). The raw `qualityRatio` that judge.mjs prints is never quoted as U."
- **W/T/L.** On z = 1 or n = 1 answers the result is "loss", unless the reference is also a stage-1 non-answer, in which case it is a "tie".
- **Area tile (r2 F8 regressed).** Restore: "If the RC offers a places/area download, the tile is the one its own flow produces at its default size; else no tile (A∪ is defined by what the RC can use)."
- **Naming.** INPACK "rule R1" collides with RULING R1. Rename it "INPACK-R1" throughout.
- **Absolute means.** Replace "Σ w (m−1) / Σ w over the answered rubric scale" with "Σ_H w (m−1) / Σ_H w, on the 0–4 scale".

## Edits the author must apply before freezing
Required (block freeze):
1. G1: the verdict sentence is always written on the installable arm when A∪ cannot be installed (§4.2, §8, §11 row 2, TL;DR 3).
2. G2: define r_g across generations and for refused answers (stage 2 always runs), give a common denominator for every cross-arm Δ, define CR's reference term per arm, and print the contrast check.
3. G3: relabel R1 as an override, accepted by this review with conditions; run the 51-answer RC1 stage-1 audit with a frozen bar; use per-family D_g in U_net; name the U_net band in the verdict sentence when it differs.
4. G4: hook-vs-chat parity check on pre-registered ids, with the labelling consequence; record the hook pipeline in state.json.
5. G5: build-designation rule, aborted-run log, map and errata frozen once for v0.4, first two generations, "judge revised after exposure" rule, UI-driver runnability decided on dev before v0.4.
6. G6: A∪ "installed" = listed + probe hit; NOTE-5 requests all six packs; failures reproduced.
7. G8: correct the nine citations listed in the table.

Required (cheap, same pass):
8. G7 contested-point notes line, independent double flagging, no-errata sensitivity row.
9. G9 diagnostic-scale labels; fix separability.
10. G10 show-anyway on every refused item; multi-turn coverage "unknown"; stage-1 context for turns.
11. G11 call/phone budget table, "judge incomplete → no band", thermal-gate scope.
12. G12 state the REFS-V2 order; pin the Codex model.

Recommended: G13, G14, G15.

## Verification of applied edits (r3 final)

Reviewer: the same independent agent, 2026-10-21. This check was read-only. I re-read the edited spec (291 lines), ruler/rc1-stage1/RC1-STAGE1-2026-10-21.md and its criterion (rnd commit 42df3c82 "frozen before calls" exists), and re-computed the REFS-V2 sha (65e84704…, which matches). No blind/, no veil, no v0.4 item or reference text, no runs.

### Per finding
| id | status | notes |
|---|---|---|
| G1 | **applied** | TL;DR 3, §4.2 (both cases), §8 fourth bullet, §11 row 2. Leftover: §12 U1 still ends "the expected band line is 'not scored on A∪'". It should add "and the verdict on arm B" (cosmetic). |
| G2 | **applied** | r_g(X,i) is defined over generations, stage 2 always runs, u and r are resampled together, cross-arm Δs use the common r̄, CR has a reference term per arm, and U13 is added. Leftovers: §3.5 still writes Δ_D = U_g(D,H) − U_g(A,H) (own denominators), which conflicts with §3.4's common-denominator rule. The pre-freeze contrast check is now "printed here when computed" (optional). Both are non-blocking. |
| G3 | **applied** | Override labelled, the first fallback stated as not run, D_g per family, the U_net band in the verdict sentence, and the RC1 audit criterion frozen before the calls. The audit **PASSED**: 0/51 not-attempted. **Low power**: only 2 units had Opus correctness ≥ 3, so the bar tested 2 answers. What it does show is 0 false zeroes on 51 long Detailed native answers. §6.2 states the low power, but §11 row 3 ("including an audit on the native app's own answers") does not. Add "(0 of 51 zeroed; 2 eligible under the bar)". Non-blocking. |
| G4 | **applied** | §0 field, §4.3 parity row with pre-registered ids and its consequence, §8 label, U12. Gap: the parity check needs the UI driver. The spec does not say what happens if the driver is not runnable (N3 below). |
| G5 | **applied** | Build designation (§0), aborted-run log, map and errata frozen once, first two runs, "judge revised after exposure", UI runnability decided on dev. Leftover: §11 row "You re-ran…" still says "Each RC's state, map and errata are registered before its first run". It should read "map and errata frozen once for v0.4; each RC's state registered before its first run". Cosmetic. |
| G6 | **applied** | NOTE-5 asks for all six packs, installed means listed + probe hit, failures reproduced, probes in §10.4. Gap: N4 below. |
| G7 | **applied** | Two-agent (Claude + Codex) double flag, fixed notes line, no-errata sensitivity row. |
| G8 | **applied** | All nine citations corrected as listed. |
| G9 | **applied** | Diagnostic scale for lift, interference and displacement; separability fixed; reference context row. |
| G10 | **applied** | Show-anyway on every refused item (A∪, B), unknown coverage goes to M, stage-1 turn context labelled unvalidated. |
| G11 | **partially** | Budget table, completion rule and thermal scope are added. The caps contradict the table (N1 below). |
| G12 | **applied** | REFS-V2 cited with the actual order, verbatim frame, Codex model pinned. |
| G13 | **applied** | Variant (a) fallback, (c) generated by a frozen Codex prompt, D_g printed, the shared stage 1 stated. |
| G14 | **applied** | Regex harm set hashed; reviewer family stated. |
| G15 | **partially** | Scale, W/T/L, area tile and absolute means are done. The rename is incomplete: §10.3 still says "rule R1 text" and the "What changed" bullet says "rule R1". Change both to INPACK-R1 (cosmetic). |

### New problems introduced by the edits
- **N1 (blocking, one-line fix). The §10.12 caps are below the table's own maxima, and no judging order is set.** Per family, the table's maximum is 600 + 600 + 1,200 + 180 + 60 + 600 = **3,240**. Without show-anyway it is still 2,040, against an Opus/Codex cap of **2,000**. "A cap hit stops and logs" combined with the §3.7 completion rule means a high-refusal RC, or simply the full harm pass, can end in "judge incomplete" by design. Which blocks get judged before the stop is also left open, which is a selection lever. Edit for §10.12:
  > **Judging order per family (fixed):** (1) verdict arm + B default answers, both generations; (2) decline arm; (3) harm pass; (4) retest; (5) show-anyway answers. Cap for blocks 1–4 = 2,100 per family; blocks 1–4 are never cut. Block 5 runs up to a total of 3,300; show-anyway answers beyond the cap are printed as "not judged (budget)", and U-total show-anyway is then n/a.
- **N3 (minor).** If the UI driver is not runnable on the RC, the parity check cannot run. Add to the §4.3 parity row: "If the UI driver is not runnable, the parity check is 'not run' and every headline row carries the hook-path label."
- **N4 (minor).** The probe in §4.2 reads `retrievedTitles`, which are titles with no pack id. A title such as a country name can come from the built-in KB as well as from factbook. Add: "Each probe's expected title must be absent from the RC's built-in knowledge base (checked on B before A∪ installs); if the trace carries a pack id, it is used instead."

### Verdict
**FREEZE OK after N1** (the one-line §10.12 judging-order and cap edit). Everything else above is cosmetic or minor and can be fixed in the same pass without another review.

## r4 delta review (RULER-SPEC-v1-r4-2026-10-21.md, [r4] text only, and how it interacts with r3)

Reviewer: the same independent agent, 2026-10-21. Read-only.
- Read: the [r4] passages (TL;DR 5, §2.4, the ORACLE row in §4.1, the §8 line, §9.1/9.2, §10.3, §10.12 budget rows, the §11 row, U14/U15); ruler/factavail/FACT-AVAIL-criterion.md (sha b9527555…, re-computed and matching); the docstrings and grep of tools/factavail_prep.py; FACTPRESENT-2026-10-21.md; arms/native-parity/C2-REPLICA.md.
- Not opened: factavail/in/ and out/ contents, v0.4 text, blind/, veil.

**Verdict: ACCEPT WITH EDITS.** The split is pre-registered properly: the criterion was frozen before any call, no app output enters the label, the label is never revised, and U-total stays the verdict. Four edits block the freeze:
- H1: the verdict line claims "installed packs" when the label is about A∪.
- H2: the label file is a per-item content-gap map of a held-out ruler.
- H3: U-avail vs U-none is not a with/without contrast; the items differ.
- H6: ORACLE is missing from the judging order and caps.

### H1. high (blocking). §8 information-available line, §2.4 (b), TL;DR 5
**Problem.** The label is computed on the six A∪ packs. The §8 line says "the N_avail items whose answer is in the **installed** packs". The expected state (U1) is A∪ not installable, so the verdict is written on B or A∪-partial. On RC1 that sentence would be false: 0 packs installed, yet N_avail > 0. The line would also pair the verdict arm's U with an availability that the verdict arm does not have.
**Edit.** Add to §2.4:
> **Label per installed set**: the stored supporting passages carry their pack id, so the label for any installed subset S is recomputed mechanically (no new calls): share_i(S) = points with a supporting passage from a pack in S / K_i. The verdict line uses S = the packs actually installed on the verdict arm (§4.2). For arm B (no A∪ pack) the line reads: "No A∪ pack is installed; the built-in knowledge base is not labelled; on the N_avail(A∪) items that A∪ would cover, B scores U = x."

In §8, replace "whose answer is in the installed packs" with "whose answer is in the installed A∪ packs (FACT-AVAIL lower bound; built-in KB not labelled)".

### H2. high (blocking). Exposure: FACT-AVAIL is a content-gap map of the held-out set (§2.4, §10.3, §9.3)
**Problem.** out/factavail-items.json lists, per v0.4 item, whether the packs hold the answer and which pack, chunk and title support it. That makes it a to-do list for pack building against the held-out ruler: add the NONE facts to a pack, re-run, and the "developed after exposure" rule (§9.3) catches only new RCs, not new pack versions. The team builds the packs and publishes them on its own authority (CLAUDE.md, pack workflow). This is the main cherry-pick route the delta opens.
**Edit.** Add to §2.4:
> **Quarantine**: the labels file, its NONE/PARTIAL lists and the supporting-passage lists are coordinator-only, handled like blind/ material. No pack-building, retrieval or engine agent and no maintainer note reads them, and they are not published before the result card. The A∪ pack shas are frozen in persona-map-v1 (§10.3) for v0.4. Any pack built or changed after the labels exist makes a new map and a new claim labelled "developed after exposure". Its U-avail is printed beside the original, never instead of it. One EXPOSURES.md row is written when the labels file is created.

### H3. high (blocking). §2.4 "Reported", TL;DR 5, §8 line: the split is not "with vs without the information"
**Problem.** U-avail and U-none are measured on **different items**. NONE will be dominated by the families and types the packs do not cover (INPACK: humanities and off-pack science), which are also the harder or more open items. So the gap between them is an item-mix difference, not the effect of having the information. r4to asked for "with and without the information". The only same-item contrast in the delta is ORACLE vs the phone arm, and that confounds information with platform (desktop replica vs phone) and with the RC's retrieval.
**Edit.** Add to §4.1, beside ORACLE:
> **ORACLE-0** [r4]: the same replica, model, persona, work budget and prompt frame as ORACLE, with no passages (closed-book), on the same AVAILABLE + PARTIAL items, one generation, the same judges.
> **Information effect** = ORACLE − ORACLE-0 (paired, same items, same platform, common denominator §3.4).
> **Retrieval + platform loss** = ORACLE − A∪ on the same items, labelled "desktop oracle vs phone app".

Add both Δs to the §3.4 cross-arm list. In §8 and TL;DR 5, add after the ORACLE value: "information effect on the same items: ORACLE − ORACLE-0 = d". Add to §2.4: "U-avail vs U-none compares different items and is not an estimate of the information effect."

### H4. medium. ORACLE design (§4.1 ORACLE row)
**Problem.**
- (a) "max 6" passages is a free parameter, and it may exceed or undercut the RC's own context budget (the RC keeps top-k chunks and truncates).
- (b) The passages were found by lexical search on the **checklist point's words**, the gold, and chosen by the labeller's "yes". This is a gold-guided context, an upper bound on any retriever, which is fine for a ceiling but must be named.
- (c) Labeller false positives feed passages that do not state the point, so ORACLE understates the ceiling on those items.
- (d) Multi-turn items (8) and the 7 location items have no defined ORACLE frame.
- (e) "JVM harness of the RC's commit if available, else 5f8cc8f4" has to be decided before any ORACLE run.

**Edit.** Replace "(distinct supporting passages …, max 6)" with:
> distinct supporting passages over the item's stated points, in point order, truncated to the RC's own retrieval k and context budget as read from state.json / RagPure (recorded). Labelled "gold-guided oracle context (passages found from the checklist wording), an upper bound on retrieval".

Add:
> - Multi-turn items: the passages go with the first turn only; the remaining turns run as in §6.3.
> - Replica choice: fixed in §10.4 before the first ORACLE call. The RC's commit is used if the app maintainer has supplied it by then, else 5f8cc8f4, with the choice recorded.
> - ORACLE U is also printed on the Opus-validated subset of points.

### H5. medium. §2.4 delivery decomposition (title-level "found")
**Problem.**
- (1) A title match does not mean the supporting **chunk** was retrieved: another chunk of the same article may have been kept. So "found, not delivered" puts retrieval misses into the reading bucket.
- (2) k is per judge family, and the decomposition does not say which family.
- (3) "Ambiguous" titles (also present in the built-in KB) have no bucket.

**Edit.** Rename the three buckets "title not retrieved / title retrieved, not correct / title retrieved and correct". Add:
> "Title retrieved" does not mean the supporting chunk was kept; this bucket is not attributed to reading. Counts are given per judge family. Ambiguous-title items form a fourth bucket and are excluded from the other three.

### H6. medium (blocking, one line). §10.12 budget and judging order
**Problem.** ORACLE (≤ 240 per family), ORACLE-0 (H3, ≤ 240) and the FACT-AVAIL Opus fallback (≤ 340 Opus, if the 34/40 bar fails) are in the table but not in the fixed judging order (N1). The 2,100 cap covers blocks 1–4 only, so it is undefined whether ORACLE gets judged and what is cut first. That is the same selection lever N1 closed.
**Edit.** Change the judging order to:
> verdict arm + B → decline → harm → retest → **ORACLE + ORACLE-0** → show-anyway.

Add:
> Block 5 (ORACLE + ORACLE-0) cap 480 per family and never cut. If the cap is hit, the §8 line prints "ORACLE not judged". FACT-AVAIL labelling calls are a separate, earlier budget (Opus ≤ 385) and finish before any app answer.

### H7. low-medium. Order of freezing and label stability (§2.4, §10.3, U14)
**Problem.** The Haiku labelling is running while the r4 text is still a draft. If the coordinator sees label counts (n AVAILABLE / NONE) before r4's sha is recorded, the reporting rules (what goes in the §8 line, the 0.5 threshold, the PARTIAL handling) could be tuned to the counts. The criterion fixes the thresholds, but the spec wording is not frozen yet. Validation is also point-level (34/40), while what drives the strata is the item-level label.
**Edit.**
- §10.3: "spec r4 sha recorded before the labels file or its counts are read; if the counts were seen first, say so here".
- §2.4: "item-level label agreement (Haiku vs Opus) on the items of the 40 validated points is printed beside the strata".

### H8. low. Citations
- §2.4 FACTPRESENT prior: add "(post hoc, Haiku-low judgments; on the topical self-tests the same cell gave +0.139 [+0.075, +0.201], n 27)". Quoting only the dev null undersells the ceiling the ORACLE row tests.
- U15: add the level match "(replica 0.15 vs phone 0.14, Opus, 51 dev items)" from C2-REPLICA.
- Cosmetic: U13 now sits after U15.

### Blocking before the r4 freeze
H1 (label per installed set and the wording of the verdict line), H2 (quarantine of the labels and the pack-change rule), H3 (ORACLE-0 and the information-effect Δ, plus the "different items" sentence), H6 (ORACLE in the judging order, with its cap).
Same pass, not blocking: H4, H5, H7, H8.
