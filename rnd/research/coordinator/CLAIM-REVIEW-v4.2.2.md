# CLAIM-REVIEW v4.2.2 — independent Opus reviewer (2026-10-17; read-only; 0 judge/LLM/API calls; blind/ and rnd/veil/ not opened)

[private correspondence with the app maintainer, or a result of a run on his device, removed]

**Verdict: ACCEPT WITH EDITS — 1 must-fix (R1), 3 should-fix (R2–R4), 1 nit (R5), 4 meaning-neutral trims (T1–T4), 5 version-line edits (V1–V5); no decision pending.** `CLAIM-REVIEW-v4.2.2-edits.py` (no flags) applies them. Every OLD matches v4.2.2 exactly once (tested to a scratch copy; the draft was not touched and CLAIM-DRAFT-v4.2.3.md was not written). After the edits: §0 = **1,093 words** (same method as the change list; v4.2.2 = 1,100 reproduced); "AI-reviewed, not clinically reviewed" 10×, sentences byte-identical to v4.2.1 (§0 intro l.37 and Limits l.59 included); "would clear" 0; "does not depend on the judge" 0.

**Headline.** Every new number traces to its row; nothing internal about the native app leaked. The one real problem is the §0 Judge-family paragraph. It regressed against v4.2 E1: wins moved from second to fifth place, behind four ratios above 0.50. "Not shown" lost "BOAR half as good". The editor's least-sure sentence says the higher judge "would clear our pre-registered rule". It cannot, because that rule's own lower-judge clause excludes the higher judge. The sentence also says the deep tier "would clear our floor-adjusted target", but that target is read on seed-noise intervals, and the OpenAI intervals' seed-noise treatment is unknown. The fact itself must stay (readers can find it in A1, and hiding it would be spin by omission). R1 rewords it to what the intervals are and puts it last, after the rule.

## Traceability ([v4.2.2] numbers → primary source)
| # | Sentence (where) | Source | Status |
|---|---|---|---|
| 1 | 4B v0.2 OpenAI raw 0.617 (0.567–0.666), floor-adj 0.517 (§0, §1, §4 r14, §5, A1) | QUEUE l.1280; CLAUDE.md l.29 | CONFIRMED |
| 2 | Deep v0.2 OpenAI raw 0.714 (0.666–0.759), floor-adj 0.639 (0.579–0.695) (§4 r14, §5, A1) | QUEUE l.1280 | CONFIRMED |
| 3 | Claude baselines on the same traces 0.512 / 0.388 (4B cut 6), 0.608 / 0.508 (deep) (§0, §5, A1) | QUEUE l.1280; CLAIM-RESULTS-cut6 l.38; A1 row 77 | CONFIRMED (headline 0.389 = cut 3; Δ −0.001, QUEUE l.707) |
| 4 | Paired deep − 4B +0.097 (+0.053…+0.142) vs +0.096 (+0.062…+0.131) (§0, §5, A1, Changes) | QUEUE l.1280 | CONFIRMED |
| 5 | Spearman 0.90–0.97 (v0.2); 0.88–0.97 merged (§0, §6) | QUEUE l.1280 + l.1270 (0.88–0.92) | CONFIRMED |
| 6 | Wins 2.7 % (4B) / 6.4 % (deep), Claude 0; "at most 6.4 %", "2.7–6.4 %" (§0, §1, §4, §5, §6, A1) | QUEUE l.1280; CLAUDE.md l.29 | CONFIRMED (seed pooling not in row; UNKNOWN says so) |
| 7 | 660 calls, 110 dev ids, 4B s42/s43, deep s42, no generation (§1, §2, §5, A1, S61) | QUEUE l.1280; EXPOSURES l.182; (2+1)×110×2 = 660 | CONFIRMED |
| 8 | Model "gpt-5.6-sol (Codex CLI)" (§0, §2, §5, A1, S61) | QUEUE l.1278 ("XFAM judge named gpt-5.6-sol"), l.1280 | CONFIRMED (closes v4.2 D2) |
| 9 | Dates: V-para 2026-10-16, v0.2 2026-10-17, both after the claim results (§0, §2, A1) | CLAUDE.md l.29 (10-16 19:01); QUEUE l.1280 (01:09) | CONFIRMED |
| 10 | Raw offsets v0.2 +0.105 / +0.106 (A1, §5) | 0.617 − 0.512; 0.714 − 0.608 | CONFIRMED |
| 11 | Raw offsets V-para +0.084 / +0.114 (A1, §5) | 0.497 − 0.413; 0.667 − 0.553 (QUEUE l.1280 writes +0.115, unrounded) | CONFIRMED (rounding) |
| 12 | Floor-adj offsets "+0.10 to +0.14" (§5) | 0.100 / 0.141 / 0.129 / 0.131 | CONFIRMED |
| 13 | "≈ 0.10 raw higher on both sets and arms" (§0, A1, Changes) | range 0.084–0.114 | **DIFFERENT** (fair as "about"; §0 shows no breakdown) → R1, R3, R5 |
| 14 | "The ranking does not depend on the judge" (§0, Changes); "ranking of configurations is the same" (A1) | 2 arms per set, one paired contrast each; V-para +0.171 vs +0.139 | **DIFFERENT** (generalises from 2 arms) → R1, R3, R5 |
| 15 | "Under OpenAI alone the 4B's v0.2 raw CI would clear our pre-registered rule and the deep tier our floor-adjusted target" (§0) | plan l.17–19 (final run, stratified two-level CI), l.43 (lower-judge clause); A1 l.65 / BAR-TABLE (seed-noise CIs for the deep target); UNKNOWN (OpenAI CI method not stated) | **DIFFERENT** (the rule cannot be cleared by the higher judge; the deep target's CI basis is unknown for OpenAI; "target" is V-para, sentence reads as v0.2) → R1 |
| 16 | "addenda 01–04, none on the judge" (§2) | plan/ listing | CONFIRMED |
| [private correspondence with the app maintainer, or a result of a run on his device, removed] |
| 18 | §0 = 1,100 words | reproduced with the change list's method | CONFIRMED |
**Counts: 15 CONFIRMED · 3 DIFFERENT (scope/wording, no wrong number) · 0 NOT FOUND.**

## Packet Q1–Q11 and checks 1–6
- **Q1 / check 1:** yes, all v0.2 numbers match QUEUE l.1280 and EXPOSURES l.182 in every section (rows 1–9).
- **Q2:** the derived offsets are right (rows 10–12). "≈ +0.10" is fair as "about" but it rounds a 0.08–0.11 range. The range costs no words, so R1, R3 and R5 use it. §1, §5 and §6 already say "about 0.10" next to the breakdown (OK).
- **Q3 / check 3: accept A1's explanation, no §0 parenthetical.** The Δ is 0.001 and below the printed precision. The §0 sentence already says "re-scored the existing … answers", which implies the same traces. A1 reconciles 0.388 vs 0.389 explicitly with [S18]. A §0 parenthetical would cost words for no change in meaning.
- **Q4 / check 2 (spin): not as drafted.** "Post-hoc, not pre-registered, both after the claim results" survives (§0, §2, A1). But the order regressed from v4.2 E1: method, offset, four ratios (0.517, 0.577 and 0.639 are above 0.50), ranking, wins, rule. R1 restores method → wins → lower-judge rule → ratios → OpenAI-only intervals → not shown. The new win-rate clause "the bar is not met by win rate" reads as if the bar were a win-rate rule, so R1 drops it.
- **Q5 / check 2 (least-sure sentence): reword; it stays, placed last.** It is needed for honesty, because the 4B is the claim build, v0.2 is the plan's set, and §1, §4 r14 and A1 state the interval. It must not say "would clear our rule". The plan's rule (l.17–19, l.43) is a final-run, stratified two-level-CI reading in which the lower of two judges is the headline, so the higher judge cannot clear it by construction. The deep tier's floor-adjusted target is a V-para reading on seed-noise intervals (A1 l.65), and neither OpenAI interval is known to include seed noise. R1 states only what the intervals are, then the exclusion and the seed-noise caveat. **Not in "Where we stand":** that paragraph is the lower-judge headline; it already points down ("at most 6.4 % under the second judge below").
- **Q6:** the evidence is thin for "does not depend": two arms per set, one paired contrast each, and V-para margins of +0.171 vs +0.139. It supports "both judges put the deep tier above the 4B" (R1, R3, R5); §5 "order … configurations alike" and §6 "keeps the ranking" are OK.
- **Q7 / check 4:** no leak. Grep of the internal figures (0.459, −0.070, 0.315, 1.288, 1.228, 1.316, 18.1 s, 5.53 GB, 2.0.0-dev, 18/31, 1/0/56, Oct-14's 0.440 / −0.089) gives 0 native hits. The matches are unrelated: 0.459, 0.070 and 0.089 sit in deep-tier CIs and the DT512-V02 delta. S62 names files but quotes no number or direction. Not evasive, but the §0 sentence only implies why the number is withheld. R2 says it plainly, in fewer words: "We scored intermediate builds … internally and publish only the final build's number, when it ships." The plural is correct, since both the Oct-14 and the Oct-17 builds were scored.
- **Q8:** yes. "Intermediate" fits appVersion 2.0.0-dev (pre-release; the app maintainer is still changing the tiers for 10-20, QUEUE l.1287). "Scored internally only (below)" is consistent with "What is submitted".
- **Q9 / check 5: the 1,100-word count is accepted, but it leaves no margin, and R1 adds words.** T1–T4 are meaning-neutral cuts: T4 removes "Not in any submitted build", which "Where we stand" already states. The result is 1,093.
- **Q10 / check 6:** present 10×, unchanged; §0 intro (l.37) and Limits (l.59) confirmed.
- **Q11:** keep "CI not in the source row" (it matches the V-para 4B row's "not in the sources read"), so the check is not blocked. Optional, if the coordinator wants it later: copy the 4B v0.2 floor-adjusted CI, the ties and the seed pooling from the numbers-only XFAM-V02 report (scoped exception, as in EXPOSURES l.182).
- *Coordinator note (no edit):* CLAIM-DRAFT-v4.2.2-changes.md ("Internal, not in the text") holds every native-app number, so it must stay out of any public research-repo snapshot.
- *Out of scope (pre-existing, no edit):* the deep tier's v0.2 reading is one seed against the plan's ≥ 2 (l.19). It is labelled "one seed" everywhere.

## Edits (exact; `ID :: OLD ⇒ NEW`; ⏎ = newline; byte-exact strings in CLAIM-REVIEW-v4.2.2-edits.py)
```text
R1 :: [§0 Judge family, from "Two post-hoc re-judges" to "a repeat pass."] … It scores ≈ 0.10 raw higher on both sets and arms. Floor-adjusted, OpenAI vs Claude: … The ranking does not depend on the judge (deep − 4B on v0.2: +0.097 vs +0.096 raw; Spearman 0.88–0.97). Wins: 0–1 % on V-para, 2.7 % (4B) and 6.4 % (deep) on v0.2, 0 under Claude; the bar is not met by win rate under either judge. The plan's headline is the lower judge: Claude. Under OpenAI alone the 4B's v0.2 raw CI (0.567–0.666) would clear our pre-registered rule and the deep tier our floor-adjusted target. Not shown: an unexposed set, human labels, a repeat pass. ⇒ Two post-hoc re-judges, not pre-registered, both after the claim results: OpenAI's gpt-5.6-sol (Codex CLI) re-scored the existing 4B and deep-tier answers on V-para and on v0.2, the set our plan names (same rubric, orders, blinding). Wins stay low: 0–1 % on V-para, 2.7 % (4B) and 6.4 % (deep) on v0.2, 0 under Claude. The plan's headline is the lower judge: Claude. Ratios rise 0.08–0.11 raw on both sets and arms; floor-adjusted, OpenAI vs Claude: V-para 0.361 vs 0.261 (4B), 0.577 vs 0.436 (deep); v0.2 0.517 vs 0.388, 0.639 vs 0.508. Both judges put the deep tier above the 4B (v0.2: +0.097 vs +0.096 raw) and rank items similarly (Spearman 0.88–0.97). Read alone, OpenAI's intervals for the 4B's v0.2 raw ratio (0.567–0.666) and the deep tier's V-para floor-adjusted ratio (0.519–0.632) lie above 0.50; the rule excludes that reading, and neither is known to include seed noise. Not shown: BOAR half as good, an unexposed set, human labels, a repeat pass.
R2 :: **It has been scored on our benchmark internally, on an intermediate build; the final build's number is published when it ships.** ⇒ **We scored intermediate builds on our benchmark internally and publish only the final build's number, when it ships.**
R3 :: The offset is ≈ +0.10 raw on both sets and both arms, the ranking of configurations is the same under both judges, and ⇒ The raw offset is +0.08 to +0.11 on both sets and both arms, both judges put the deep tier above the 4B, and
R4 :: On v0.2, the plan's own set, the OpenAI re-judge puts ⇒ On v0.2, the set the plan names (now development data), the post-hoc OpenAI re-judge puts
R5 :: The offset is ≈ +0.10 raw on both sets and both arms; the ranking of configurations does not depend on the judge ⇒ The raw offset is +0.08 to +0.11 on both sets and both arms; both judges put the deep tier above the 4B
T1 :: Ten 5-turn sessions (three extended to 15) on desktop with full history; ⇒ Ten 5-turn sessions (three extended to 15), desktop, full history;
T2 :: Desktop median rose to 22 s at turns 14–15 (8 s standalone). ⇒ Desktop median: 22 s at turns 14–15, 8 s standalone.
T3 :: the submitted app is scored only internally so far (below). ⇒ the submitted app is scored internally only (below).
T4 :: Desktop median 79 s. Not in any submitted build. An expert ⇒ Desktop median 79 s. An expert
V1 :: Draft v4.2.2 (2026-10-17) — v4.2.1 + two folds ⇒ Draft v4.2.3 (2026-10-17) — v4.2.2 with the edits of CLAIM-REVIEW-v4.2.2 applied (reviewer verdict ACCEPT WITH EDITS) — Draft v4.2.2 (2026-10-17) — v4.2.1 + two folds
V2 :: (DRAFT v4.2.2; independently reviewed through v4.2, see CLAIM-REVIEW-v4.2.md and the changelogs; the v4.2.2 folds await review, see CLAIM-REVIEW-v4.2.2-packet.md; not published) [v4.2.2] ⇒ (DRAFT v4.2.3; independently reviewed through v4.2.2, see CLAIM-REVIEW-v4.2.2.md and the changelogs; not published)
V3 :: ## 0. Post text (v4.2.2, post-facing; ⇒ ## 0. Post text (v4.2.3, post-facing;
V4 :: ## Changelog v4.2.1 → v4.2.2 [v4.2.2] ⇒ ## Changelog v4.2.2 → v4.2.3⏎- v4.2.3 (2026-10-17): edits of CLAIM-REVIEW-v4.2.2.md applied by CLAIM-REVIEW-v4.2.2-edits.py.⏎⏎## Changelog v4.2.1 → v4.2.2 [v4.2.2]
V5 :: awaiting independent review (`CLAIM-REVIEW-v4.2.2-packet.md`). [v4.2.2] ⇒ (same)⏎- v4.2.2 reviewed 2026-10-17 (independent Opus reviewer): ACCEPT WITH EDITS, see `CLAIM-REVIEW-v4.2.2.md`; applied as v4.2.3.
```

## Summary
1. ACCEPT WITH EDITS. 15 of 18 traced items are confirmed and the other 3 are scope or wording problems, with no wrong number. The model ID gpt-5.6-sol is now sourced (QUEUE l.1278/l.1280). No native-app number or direction is in the draft.
2. Must-fix R1: the §0 Judge-family paragraph goes back to the v4.2 E1 order (wins, then the lower-judge rule, then ratios). "Would clear our pre-registered rule" becomes a plain statement of the intervals, followed by the exclusion and the seed-noise caveat. "BOAR half as good" returns to Not shown.
3. Should-fix: R2 says plainly that intermediate builds were scored and why their number is withheld. R3 and R5 scope "ranking" to two arms and give the offset as a range. R4 labels v0.2 as development data in §1.
4. With T1–T4, §0 drops to 1,093 words (cap 1,100). The caveat appears 10× and is unchanged. The 0.388 vs 0.389 difference is accepted on A1's explanation.
5. No decision for r4to. Run `python3 CLAIM-REVIEW-v4.2.2-edits.py` to write CLAIM-DRAFT-v4.2.3.md, and keep CLAIM-DRAFT-v4.2.2-changes.md out of any public snapshot.
