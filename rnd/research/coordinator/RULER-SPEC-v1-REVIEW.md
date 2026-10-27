# Review of RULER-SPEC-v1-2026-10-20.md (adversarial, independent)

Reviewer inputs: RULER-SPEC-v1-2026-10-20.md, BOUNTY_31.md, BENCH-RULER-2026-10-19.md only. No item text, no blind/ or veil reads, no runs.

## TL;DR
1. The verdict arm (A, "persona") installs packs chosen per item from the item's own `family` label. That gives the app oracle routing by question type, which no real user has, and it is the most attackable rule in the spec. Make arm B (or a single fixed union of persona packs) the verdict arm.
2. The decline arm cannot fail. §3.1 forces s := 0 for the fixed refusal string before the judge runs, so "U ≤ 0.05" is true by construction and says nothing about the judge.
3. The health 0.5 weight and the persona map were decided or approved by r4to after the item set was frozen (16:42 freeze, 20:24 decisions), and r4to co-wrote the items. "Decided before any system answered" holds, but "blind to item content" does not.
4. Rebuilding the APK or editing the map resets "the first complete run", so the run ledger can be gamed. Both judge families also wrote the items, which contradicts R-D3.
5. Several formulas have undefined cases: empty or zero-denominator subsets, ties on even R, multi-turn refusals, how two references combine for TS and W/T/L, and arm C, which is assumed always to refuse. Several free parameters (R, radius, the safety criteria, gold re-check errata) are fixed after v0.4 exposure or not frozen at all.

## Findings (ranked by severity)

### F1. high. A, D. §4 arm A, §5, §8
**Problem:** Arm A gives each item the packs mapped to that item's `family` tag. The tag is an item label written by the item authors. In effect the app gets perfect per-question pack routing, which a real user cannot have, because a user does not know a question's "family" before asking it. This contradicts the spirit of §3.3 ("No item label … enters coverage"), since a label decides what can be kept. A skeptic would say: "your headline is the app plus an oracle that knows the topic of each question, using packs built by your team." R-D8 (entrant-agnostic) is also strained, because rivals have no persona map.
**Edit:** Make the verdict arm the system as a user installs it: either arm B, or **A' = one fixed install of the union of all persona packs plus the general layer, the same for every item** (it fits the 50 GB gate). Keep the per-family arm A as a labelled sensitivity row ("oracle topic routing"). Change §8 and TL;DR item 5 to match.

### F2. high. B. §3.1 refusal rule, §4 decline arm, §10.9
**Problem:** The decline arm emits "the fixed refusal string for every item". §3.1 sets s := 0 and t := 0 whenever the text equals that string, "regardless of the judge". So decline U = 0 by construction, and the validity check "U ≤ 0.05 under both families" can never fail. It does not test whether the judge gives a true zero to non-answers.
**Edit:** The decline arm bypasses the z override and goes through the judge. Use at least three pre-registered variants: (a) the bare refusal string; (b) a generic hedged non-answer ("It depends; consult local sources…"); (c) a fluent on-topic answer with no content, matched in length to the reference. Validity requires judge U ≤ 0.05 on each variant, under each family.

### F3. high. A, C. §2 weights, §5.1 step 2, §11 row 4, §10 order
**Problem:** The item set was frozen at 16:42, and the r4to decisions (health 0.5, arms, persona) were recorded at 20:24 on the same day. r4to co-wrote the items with a non-Claude model and also approves the persona map (§5.1). The §11 defence ("decided before any system answered") is true but beside the point. The decisions were made by someone who knows the item content and BOAR's known weak areas, after the items existed. The §5.1 rule "never item text" applies to the drafter but not to the approver.
**Edit:**
- Make the headline weight 1 for all items, and move health 0.5 to a labelled sensitivity row. Alternatively, require that the verdict hold under both weightings.
- Remove the item author from persona-map approval. Use an independent reviewer and r4to only for a veto with a logged reason.
- Add a sentence to §11 that states the timeline honestly.

### F4. high. A, C. §9.3 run ledger, §5.1 step 3
**Problem:** The headline is "the first complete pre-registered run per (APK sha, map sha)". Any rebuild, even a trivial one, or any map edit creates a new key with its own "first run". This is a re-roll loophole, and §11's answer to "you re-ran until it looked good" does not survive it. §5.1 also does not say which run is the headline after a map change.
**Edit:**
- Register the APK sha and the map sha in §10 before the first run.
- The headline is the first complete run of the registered pair.
- Any later pair is a new, separately labelled claim that must print every earlier pair's result beside it, plus a count of attempts.
- An APK built after the first v0.4 run is labelled "developed after exposure" by rule, not by intent.

### F5. high. D. §6, §3.7, §11 row 6 (R-D3, R-D1)
**Problem:** R-D3 requires items "written outside the judge/reference family". In v0.4 the items were written by Claude and Codex, and Claude and a non-Claude family (Codex, per U6) are the two judge families and probably the two reference families. The per-writer breakdown shows the bias but is not the separation R-D3 requires. The spec does not mark this as a deviation.
**Edit:** Add an explicit "Deviation from R-D3" line in §1 or §12. If any third family is available, make it a judge, or at least the confirming judge. Otherwise report a family-by-writer cross table: judge G times writer, U for app and reference.
- R-D3's other two requirements are also missing from the spec: "not filtered on any system's failures" and "drafted and rejected items published". Add both to §10.

### F6. medium. A, B. §7.2 speed verdict
**Problem:** TFUC and completion p50/p90 are taken over all of H in arm A's default mode, and that includes near-instant refusals. A higher refusal rate therefore improves the speed verdict. The thresholds (30/60/60 s) are "our choice" and were chosen by a team that knows its own latency. "TFUC = first 30 tokens" measures time to 30 tokens, not useful content.
**Edit:**
- Compute the speed verdict over answered items only (z = 0) and report refusal latency separately, as the spec already does.
- Publish the full latency CDF.
- Anchor the thresholds to something outside the team: the reference arm's measured end-to-end time (web search plus frontier model) on the same items, or the post author's quotes converted to answer time at the median answer length.
- Rename TFUC "time to 30 tokens".

### F7. medium. A, C. §7.1 safety gate
**Problem:** "Confirmed dangerous" is decided by r4to, an entrant, and the confirmation criteria are not pre-registered. A skeptic would say the team reviews its own app's dangerous answers.
**Edit:**
- Pre-register a written harm rubric in §10.9.
- The confirmer is someone outside the team, or an independent agent from a third family, with r4to's view logged but not deciding.
- Publish every flagged answer with its text and the decision.
- A flag from both families counts as confirmed unless the outside reviewer overturns it in writing.

### F8. medium. A. §5.2 area tile, §10.3
**Problem:** For the 7 location items, the area tile is built "for a fixed radius around the item's `context` lat/lon". That uses item data to build the system configuration, and the radius is a free parameter set by the team. This conflicts with the claim at the top of the spec that nothing is derived from item content.
**Edit:**
- The tile is whatever the APK's own user flow produces for that city (city-name selection or a GPS download), at the APK's default radius, built before the item set is opened.
- Otherwise, the radius is fixed in the spec now, with a reason that does not depend on the items.
- State whether arm B gets the tile. Today it is ambiguous.

### F9. medium. B. §3.4, §3.5, §3.6
**Problem:** Several cases are undefined:
- (a) U_g(X,m,S) when Σ_S w·s_ref = 0. N_X or M_X can be empty or have zero reference mass, which affects U-noref, the ρ terms, and some bootstrap draws.
- (b) Items where the reference scores 0 give the app free numerator mass, so U can exceed 1, and the ratio of sums lets items the reference fails on weigh little.
- (c) CE when no answers have z = 0, which is the case for the decline arm and for arm C's default mode.

**Edit:**
- If the denominator is 0, the term is "n/a" and ρ_S·U_S is replaced by its numerator form Σ_S w·s_X / Σ_H w·s_ref (still exact).
- Bootstrap draws with a zero denominator are redrawn, and the number of redraws is reported.
- Report the count of items with s_ref = 0 and the app's share of numerator mass from those items.
- CE is "n/a" when the answered count is 0.

### F10. medium. B, C. §3.1 majority, §6 R rule
**Problem:**
- "Majority over r (ties → not met)" over three categories is ambiguous. With met / not met / contradicted it is unclear whether this means a plurality or a strict >R/2 majority. The rule is also undefined for t and d when R is even.
- §6 lets T2 raise R "if the measured point flip rate on the first pass exceeds 10 %". If that first pass is on v0.4, R is set after v0.4 judgments have been seen, which breaks the §10.4 rule that the judge is frozen before any v0.4 judgment.

**Edit:**
- State a strict majority (> R/2), with anything else counting as not met, and the same rule for t and d (no majority means 0).
- Require R to be odd.
- Measure the flip rate and fix R on a dev set before freezing step 4. No change to R after v0.4 judging starts.

### F11. medium. B. §2 unit, §3.1, §3.3, §7.2 (multi-turn)
**Problem:**
- For multi-turn items (8 of them), refusal z is defined per answer, but s is scored once per transcript. It is undefined what happens when one turn refuses.
- Show-anyway is never defined for mixed items.
- Coverage c_X leaves the mixed set M_X out of both C and N, so c is not 1 − share(N). The prose "coverage = share of items where retrieval kept a source" is wrong for mixed items.
- Latency per turn versus per item is unspecified.

**Edit:**
- A multi-turn item with any refused turn is scored on the transcript as given, with refused turns contributing nothing, and the judge is told so.
- Publish |M_X| beside c.
- Speed is measured per turn, and the 8 items' turns are pooled.
- Close U8 in the spec rather than leaving it to T2.

### F12. medium. B, C. §3.7, §4 (one seed)
**Problem:** The CI resamples items and judge repeats, but not app generation noise (one phone run, seed 42) or reference generation noise (one archived answer per family). For a sampled model, the per-item seed correlation can be well below 1, so a CI low just above 0.50 can be a lucky seed.
**Edit:** Do one of the following: run the phone at greedy or deterministic decoding, or run at least 2 phone seeds with the verdict on their mean and seed variance added. Report reference re-generation variance on a subset. Pre-register whichever you choose.

### F13. medium. B. §3.4 TS, §3.5 displacement, §3.6 W/T/L and CE
**Problem:**
- TS_g uses t_g(ref,i), but there are two references and no aggregation rule. §3.2 defines only the mean of s.
- The displacement case uses s_g without saying which g.
- W/T/L and CE are unweighted while the headline is weighted, and the weight-1 versus 0.5 variants are not specified for them.

**Edit:**
- Define t_g(ref,i) as the mean over f, so TS reference values lie in [0, 1].
- Count a displacement as harm only when s_g(D) < s_g(A) under both families.
- State that W/T/L and CE are unweighted on purpose, or give w and w1 forms.

### F14. medium. B. §3.5, §4 arm C
**Problem:** "Arm C has no packs, so every C answer is a refusal in default mode." This is false if the APK keeps deterministic fact-table rows or built-in places records. §3.3 counts those as kept sources. In that case C_show(i) does not exist on items C covers, and the lift formula is undefined.
**Edit:** Define C_ans(i) = C's show-anyway answer if C refused, else C's default answer. Use C_ans in L_g, and report c_C.

### F15. medium. A. §2 headline set
**Problem:** Excluding the 4 V-exact anchors leaves the post author's own stated eval out of the verdict. A skeptic can read this either way: hiding a weak spot, or hiding a spot that was overfit. BENCH-RULER §1 puts the current-city stratum "inside the headline".
**Edit:** Publish a co-row H ∪ anchors next to the headline. Under §9.2, the headline may not be shown without it. Confirm that the 7 location items in H cover the V2 eval shape.

### F16. medium. C. §3.2, §10.5 (reference)
**Problem:** The reference prompt v2 is written by an entrant. The references only have to be archived "before any app answer is judged", so they could be generated, or the prompt revised, after app answers exist.
**Edit:**
- Archive the references before any app arm generates answers on v0.4.
- Prefer the frontier products' stock web-search mode with the question as the prompt, and no system-prompt shaping, or publish the exact prompt with a reason for each instruction.

### F17. medium. D, C. §4 last bullet, U3 (R-D5)
**Problem:** The fallback covers only arms C and D. If the APK cannot switch pack sets per item family, arm A, the verdict arm, cannot run on the APK at all, and the spec does not say what the headline becomes.
**Edit:** State the rule. If A cannot run on the APK, the verdict arm is B on the APK, or A' (F1) installed once. A is never run on the bench app as a headline.

### F18. medium. D. §7.3, §8 (B31:41)
**Problem:** "Running within a few minutes without substantial debugging" is a bounty requirement, but install time is only reported. It is not a gate and does not enter the verdict. The verdict arm's extra persona install is not timed against any limit.
**Edit:** Add an install gate with a pre-registered threshold for setup without the download, and a requirement of zero debugging steps. Apply it to the verdict arm's install path.

### F19. low-medium. C. U10, §10.2 (time-sensitive gold)
**Problem:** Re-checking the gold of the 19 time-sensitive items "before any answer is judged" changes checklists after the item-set sha is frozen. The re-check is also done by the two judge families.
**Edit:** Any re-check produces an errata file, frozen and hashed in §10 before judging. The headline uses the original sha plus the errata sha, and the number of changed points is published.

### F20. low. B. §3.7, §8 (min over families)
**Problem:** "Min over g of the CI low" is not the CI of min(U_G1, U_G2), and it is not stated whether the band rule "point > 0.50" uses the min point.
**Edit:** Compute min(U_G1, U_G2) inside each joint bootstrap draw, using the same item resample for both families. The verdict uses that statistic's point and 2.5 percentile.

### F21. low. B, D. §7.1 storage gate
**Problem:** The gate applies to "arm A's and arm D's largest install". D is a diagnostic arm, not the submission, and A's per-family installs understate what a user who installs every persona pack would hold.
**Edit:** Apply the gate to the APK plus the union of all packs the README offers. Report D's bytes as information only.

### F22. low. D. §2, §8 (R-D4, R-D9, B31:27)
**Problem:**
- R-D4 says "weights stated" for the strata, and the spec gives no stratum weights, so the effective weights come from item counts.
- R-D9 requires English scope labelled "our choice", and the spec does not mention language.
- B31:27 "beyond simple factual recall" has no verdict consequence: a pass could come from lookup items alone.

**Edit:**
- State the effective type and family mass shares.
- Add the R-D9 line.
- Add a verdict condition or flag: U-total on non-lookup types reported, and flagged if its CI low is ≤ 0.50.

### F23. low. A. §3.6 CE
**Problem:** CE's denominator excludes refusals, so refusing more often lowers CE and makes the app look careful.
**Edit:** Print the answered count beside CE, and also report CE over H, where a refusal counts as a non-error.

### F24. low. B. §3.3 kept_X
**Problem:** The text says both "received at least one kept source record" and "the app cites". A source can be received without being cited.
**Edit:** Choose one: received by the answer step, or cited in the output. The pinned trace field must match it.

### F25. low. D. §8, §7.1 (B31:21)
**Problem:** "Meets the bar" can be issued with the GrapheneOS requirement UNVERIFIED, even though the issuer called GrapheneOS compatibility required.
**Edit:** When GrapheneOS is UNVERIFIED, the band reads "Meets the bar (this ruler), GrapheneOS unverified" in the band name itself, not in a side note.

## Coordinator disposition

Author: coordinator agent (spec author), 2026-10-20. Edits applied in RULER-SPEC-v1-2026-10-20.md revision r1, cited inline as [Fn].

### Accepted (applied)
| id | What changed in the spec |
|---|---|
| F1 | New verdict arm **A∪** = B's kit + union of all persona packs, installed once, same for every item (no per-question routing). Per-family arm A kept as r4to's persona row, labelled "topic known in advance". §4, §5.2, §8, §11. r4to can revert this before the spec is frozen; it changes the verdict arm, not his arm set. |
| F2 | Decline arm is judged without the z override; three pre-registered variants (bare refusal, hedged non-answer, length-matched fluent no-content); valid only if U ≤ 0.05 for each variant under each family. §3.1, §4. |
| F3 (partial) | Honest timeline sentence (§1, §11). Persona map now approved by an independent reviewer; r4to has a veto that must be logged in writing (§5.1). Verdict sentence states the weight-1 band whenever it differs (§8). Rejected part: see below. |
| F4 | APK sha and map sha registered before the first run; later pairs print all earlier results and the attempt count; post-exposure label by rule. §9.3, §10. |
| F5 | Stated deviation from R-D3; judge family × writer family table; third family as confirming judge if available; "not filtered on failures" and "drafts/rejected published" added to §10. |
| F6 | Speed over answered items only; T30 renamed; full CDF; reference end-to-end time printed as context. Thresholds kept (our choice, labelled). |
| F7 | Harm rubric written and pre-registered; both-family flag = confirmed unless an outside reviewer or a third-family agent overturns it in writing; r4to does not decide; all flagged answers published. |
| F8 | Area tile = the APK's own flow at default size; else 25 km radius fixed in the spec; B gets the tile only if the README says so. |
| F9 | n/a for zero denominators; decomposition in numerator form; bootstrap redraws counted; items with s_ref = 0 and their numerator share published; CE n/a when nothing answered. |
| F10 | Strict majority (> R/2), R odd; same rule for t and d; R fixed from a dev test-retest pass before the judge freeze, never changed after. |
| F11 | Multi-turn refused turns defined; show-anyway for mixed items defined; |M| and |N| printed beside c; per-turn speed pooled. U8 closed in the spec. |
| F12 | Two phone seeds for A∪ and B, verdict on the per-item seed mean, seed level in the bootstrap; reference regeneration on a 15-item subset. |
| F13 | t_ref = mean over reference families; displacement harm requires both judge families; W/T/L per reference family; weighted forms given. |
| F14 | C_ans defined (show-anyway if refused, else default); c_C reported. |
| F15 | H ∪ anchors co-row is mandatory beside the headline. |
| F16 | References archived before any app arm generates; prompt published with reasons; stock web mode preferred. |
| F17 | Fallback rule: A∪ and B always on the APK; if A∪ cannot install, the verdict arm is B on the APK; never a bench-app headline. |
| F18 | Install gate: ≤ 15 min without download and 0 debugging steps on A∪'s path (threshold labelled our choice). |
| F19 | Errata file for time-sensitive re-checks, hashed before judging; changed points counted. |
| F20 | Verdict statistic = min(U_G1, U_G2) inside each joint bootstrap draw. |
| F21 | Storage gate on APK + union of every pack the README offers; D bytes information only. |
| F22 | Effective stratum mass shares printed; English-only R-D9 line; non-lookup pooled row flagged if its CI low ≤ 0.50. Kept as a flag, not a verdict condition (the bounty names no per-type bar). |
| F23 | CE over H and the answered count printed beside CE. |
| F24 | kept = received by the answer step; the trace field must mean that. |
| F25 | Band name carries "GrapheneOS unverified" when it is. |

### Rejected (with reasons)
| id | Rejected part | Reason |
|---|---|---|
| F3 | Making weight 1 the headline and moving health 0.5 to a sensitivity row | The 0.5 headline weight is a named r4to decision (GRILL Q8-Q9, QUEUE 20:24) with a textual basis (B31:7 "casual info lookup and research", health never named), recorded before any system answered. The spec cannot override it. Mitigations kept: weight-1 U always beside it, the verdict sentence names the weight-1 band when it differs, and the safety gate is stricter for health. Flagged to r4to as the most attackable remaining rule. |
| F3 | "r4to co-wrote the items" | Factually, the items were written by Claude and Codex agents; r4to resolved 3 disputed points and approved the balance round. The timeline sentence states his exposure precisely. |
| F12 | Greedy decoding on the phone | It would score a configuration the product does not ship; two seeds were chosen instead. |

### Post-review addition (r2)
Coordinator input 2026-10-20 (OCCRAG sidecar): two coverage levels added to §3.3/§3.4/§3.6/§9.1/§10.6/§12. Retrieval coverage routes items into U-ref vs U-noref; support coverage (checklist judge on the kept chunks) is reported beside it and never routes or selects items; faithful refusals on kept-but-unsupporting items score 0 in U, are not confident errors, and count as correct behaviour; their show-anyway answers count in the show-anyway mode. Not re-reviewed.
