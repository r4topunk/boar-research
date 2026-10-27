# judge.v2 independent review (2026-10-20)

Scope: `boar-eval/harness/judge-v2.mjs` (EXTRACT_SYSTEM, JUDGE_SYSTEM_V2, judgeSchema, scoreRepeat/aggregate), contrast `judge-core.mjs` (v1), RULER-SPEC-v1 §3.1/§3.6/§6/§4, smoke `runs/smoke/{kp,j1}.jsonl` + the 2 source dev items. No LLM calls made; blind/, veil/, v0.4 items not opened.

## TL;DR
- The judge is properly pointwise and reference-blind; the main risks are in the CE rule and in point construction, not in leaks to the judge.
- CE as coded (`contradicted OR false_facts`, gated on judge class != decline) is not the CE frozen in RULER-SPEC §3.1/§3.6 (`x = any contradicted`, z from trace only), and the smoke already shows a false_facts false positive turning an answer into a CE.
- Compound / example-list points + "Every part of the point must be there" reward longer answers and are the likely main source of flips; the dev extractor also imports reference-only and own-knowledge facts.

## Findings

**F1 (blocker): CE rule differs from the frozen spec, and false_facts adds noise to it.**
Spec §3.1: "Contradiction x_g(a,i) = 1 if any k has v_g = contradicted"; §3.6 CE uses only z=0 and x=1. Code: `ce: cls !== "decline" && (contradicted > 0 || falseFact)` and in aggregate `ce: !declineMaj && (verdicts.includes("CONTRADICTED") || ffMaj)`. Evidence: smoke `vit-hum-001` gets `ce=true` with 0 contradicted points, solely from the false fact "Later Confucian ideals placed more emphasis on hierarchical relationships" (`why`: Confucius predates Mozi). That claim is defensible (Mencius and Xunzi are later than Mozi) and it overlaps checklist P4 (Confucian contrast), which the prompt says false_facts must not cover. false_facts also scale with answer length (F4), and ffMaj only asks "some false fact in > R/2 repeats", not the same claim.
Edit (code): `scoreRepeat` → `ce: contradicted > 0`; `aggregate` → `ce: verdicts.includes("CONTRADICTED")`. Keep `false_facts` as a separately published, labelled diagnostic ("uncovered false-claim rate", per-claim majority, see F4), never inside CE, unless an erratum to §3.6 is frozen first. Keep `declineMaj` only as a logged diagnostic (F7).

**F2 (major): compound points + "Every part of the point must be there" = over-strict, flip-prone and length-favouring.**
Smoke points: "botulism, caused by Clostridium botulinum bacteria" (species not required by the note "Names botulism"); "toxin has no taste or smell, so eating or smelling..." (smell imported from a Penalize note); "such as opposition to offensive war, frugality, and following Heaven's will" (a note's example list becomes a 3-part conjunction). A terse correct answer ("Botulism; you can't taste it") misses P1 and P3; a long answer that enumerates more sub-parts gets them. Boundary cases ("partly stated" vs "more specific") are exactly where R repeats disagree.
Edit (EXTRACT_SYSTEM, replace the "Each point is ONE checkable claim..." bullet):
`- Each point is ONE checkable claim, written as a plain factual statement ("<neutral example, see F6>"), not as an instruction. Put only what the note requires in the point: no added names, species, numbers, qualifiers or reasons the note does not ask for. If a note gives examples ("such as", "e.g.", a list in parentheses), write the point as "<general claim>, for example A, B or C" and never as "A, B and C".`
Edit (JUDGE_SYSTEM_V2, replace "Every part of the point must be there."):
`Every required part of the point must be there; for a point that lists examples ("for example A, B or C") the general claim plus one listed example is enough.`
Same rule goes into the v0.4 checklist-writing guide for authors.

**F3 (major): shotgun / hedged-alternative answers can earn PRESENT.**
"A point stated with a hedge ('probably', 'I think') still counts as stated" plus "in any wording" lets "It could be salmonella, listeria or botulism" score P1, and long lists of candidates hit more points by chance. v1 had "Penalize factual errors heavily"; v2 has no rule for alternatives.
Edit (JUDGE_SYSTEM_V2, replace the hedge bullet):
`- A point stated with a hedge ("probably", "I think") still counts as stated. But if the answer offers several incompatible options for the same thing (several causes, numbers, places) without committing to one, a point is PRESENT only if the answer clearly favours the point's option; otherwise ABSENT. Listing many candidates earns nothing by itself.`

**F4 (major): false_facts is length-biased and biases CE comparisons toward the app.**
"specific factual claims ... NOT covered by any checklist point" grows with claim count: the reference (long, sourced) exposes more claims than the 4B/1.7B app, so ref CE inflates relative to app CE (app-favouring on the CE row); Haiku-low judging truth "by well-established knowledge" is the least reliable part of the call (F1 evidence).
Edit if false_facts is kept as a diagnostic: schema item `{quote, why}` with `quote` = verbatim span ≤ 25 words, reject rows whose quote is not found (reuse the `quoteFound` normaliser), count a false fact only if the same quote (normalised overlap ≥ 0.5) is flagged by a strict majority of repeats, and publish it per 1,000 answer characters beside the raw rate. Prompt line to add: `Only claims about the question's main subject that a user would rely on; if the claim could be true under a reasonable reading (e.g. "later" relative to a different figure), do not list it.`

**F5 (major): the decline-arm variant (c) and (b) can hit generic-advice points.**
Dev notes such as "Suggests a doctor or dietitian for long-term use" (lan-hlt-001) and "seek care" points become checklist points; a fluent content-free answer ("results vary; if symptoms persist, talk to a professional") would be PRESENT under "any wording". Summed over 75 items, ~15 such 1/K hits can push U past 0.05. (a) and (b) otherwise land at s=0 and class decline (smoke `st-qa-cooking-se-002`: wrong-pack message → decline, s=0, ce=false), and with F1 applied no variant can be CE unless a point is CONTRADICTED.
Edit (JUDGE_SYSTEM_V2, append to PRESENT): `Generic advice that fits any question of this kind ("it depends", "check local sources", "see a professional") is PRESENT only if the point names that same specific action, person or threshold and the answer states it at that level of specificity.` Plus a pre-freeze dev check: run variants (b)/(c) on the 97 dev items with `--no-override` and list every PRESENT (must be ≤ 0.05 U before freeze; any hit becomes a checklist-guide rule).

**F6 (minor): extraction imports facts and copies reference phrasing; example text is item-adjacent.**
Rule "Do not add facts from your own knowledge" is broken in smoke: "paralysis" and "Clostridium botulinum" appear in neither notes nor reference of st-qa-cooking-se-002. "When the notes miss something central" let reference-only points in (Mozi P3 "promotes the benefit of the world and removes its harm" is a near-verbatim reference quote; P6 sage-kings is reference-only), so K goes 4 → 6 and the reference is graded on a checklist shaped by its own content (inflates s(ref), deflates dev U). The extraction example ("Water boils at a lower temperature at high altitude...") sits next to a dev item on boiling water at altitude. Does not affect v0.4 (author checklists), but does affect the dev R-selection and decline checks.
Edits: (a) replace the notes/reference bullet with `Take every point from the author notes, one point per positive note. Use the reference only to make a note concrete (the actual name, number or mechanism the note refers to). Never add a point that no note asks for.`; (b) replace the example with `("Copper conducts electricity better than iron")`; (c) code post-check after extraction: flag any capitalised term or number in a point that is absent from notes + reference (case-insensitive), and re-extract or hand-fix flagged points before the flip-rate pass.

**F7 (minor): judge answer_class is half-used and can disagree with the trace.**
`hedged` is never used in score or CE (wasted output, more variance). Spec §3.1: "Refusal is decided by the trace, never by the judge"; the code gates CE on `cls !== "decline"`, so an answer the trace calls answered but the judge calls decline silently drops out of CE errors while staying in the CE denominator. Also z only reads `declined`; spec also matches "the text equals the app's fixed refusal string".
Edits: drop the class gate from CE (F1); log `classMismatch` = trace answered && declineMaj, and treat rows with class decline but any PRESENT/CONTRADICTED as invalid (retry once). Override: `if ((ans.declined || prepped.text.trim() === REFUSAL_STRING) && !has("--no-override"))` with REFUSAL_STRING pre-registered. Either use `hedged` (publish CE split answer/hedged) or remove it from the enum.

**F8 (minor): CONTRADICTED boundary is underspecified (number/rounding, compatible extra detail).**
"a different number, name, date, place or mechanism" will flag "about 2 drops per litre" vs "2 drops", or "boil 1-3 minutes" vs "1 minute", inconsistently across repeats.
Edit (replace the CONTRADICTED line): `- CONTRADICTED: the answer states something that cannot be true at the same time as the point (a different number outside any range or rounding the point allows, a different name, date or place, a different mechanism, or the opposite claim). An extra, compatible detail is not a contradiction; a missing part is ABSENT, not CONTRADICTED.`

**F9 (minor): evidence is computed but not enforced.**
`quoteFound` is logged and unused, so a PRESENT with a paraphrased or invented "verbatim span" still scores.
Edit (code, in judge after mapping): `if (verdicts[k] !== "ABSENT" && quoteFound[k] === false) { verdicts[k] = "ABSENT"; row.quoteDowngrade = (row.quoteDowngrade ?? 0) + 1; }` and publish the downgrade rate; if it exceeds ~5 % on dev, loosen the normaliser rather than the rule.

**F10 (minor): multi-turn scope is ambiguous.**
"the checklist applies to the whole conversation" vs "copy ... the shortest verbatim span of the answer" (quoteFound checks the last answer only): a point met in turn 1 may be PRESENT in one repeat and ABSENT in the next.
Edit: `A point stated in any assistant turn not marked [REFUSED] counts; quote it from that turn and prefix the evidence with the turn label (e.g. "A1: ...").` and make quoteFound search all non-refused turns.

**F11 (minor): task_success has no length guard.**
"a casual user could act on or be satisfied by this answer" can drift toward rewarding thorough-looking answers.
Edit (append): `Extra length, detail or caveats beyond what was asked do not make an answer successful; a short answer that settles the question is successful.`

## Validation to add before freeze (no prompt change)
- Padding probe on ~20 dev answers: append a length-matched block of correct, off-checklist text; Δs must be ~0 and false-fact/CE rate must not rise.
- Report Spearman(s, log answerChars) within item across arms on dev; flip rate per point, split by compound vs single-claim points (tests F2).

Top objection (ranked): 1) F1 CE ≠ frozen spec + noisy false_facts already producing a false CE; 2) F2 compound points with "every part" (verbosity + flips); 3) F5 generic-advice points threatening the decline-arm U ≤ 0.05; 4) F3 shotgun answers.

## Applied (coordinator, 2026-10-20, before the criterion freeze; judge-v2.mjs prompt sha 3595d696…, extraction prompt sha 2f36ce39…)
| Finding | Decision | What changed |
|---|---|---|
| F1 | accepted | CE = trace not declined AND >= 1 CONTRADICTED point (spec §3.1/§3.6); false facts kept as a separate flag `ff` (task requirement), never in CE; judge class no longer gates CE |
| F2 | accepted | extraction: no added qualifiers, example lists as "for example A, B or C"; judge: "every required part", general claim + one example suffices |
| F3 | accepted | shotgun / incompatible-options rule added verbatim |
| F4 | accepted in part | false_facts items are {quote, why}; a false fact counts only if its quote is found in the answer; main-subject and reasonable-reading lines added. Not done: per-claim overlap matching across repeats and the per-1,000-characters rate (ff is a diagnostic flag only; majority = >= 1 found false fact in > R/2 repeats) |
| F5 | accepted in part | generic-advice line added to PRESENT. Deferred: the decline-variant dev check (b)/(c) (spec §4 decline arm; needs pre-registered variant texts; T2 follow-up, not in this criterion) |
| F6 | accepted | (a) points from notes only, one per positive note; (b) neutral example ("Copper conducts electricity better than iron"); (c) post-check logged as `imported` terms per point (diagnostic; no hand fix, no re-extraction) |
| F7 | accepted | answer_class = answer / decline (hedged removed); `classMismatch` logged; `--refusal-string` override option (text equal to the APK's refusal string = trace decline) |
| F8 | accepted | CONTRADICTED boundary text replaced verbatim |
| F9 | accepted (normaliser loosened up front) | PRESENT / CONTRADICTED whose evidence span is not found -> ABSENT; match = normalised substring or >= 80 % of the span's words (>= 3 letters) in the answer; downgrade count published |
| F10 | accepted | multi-turn: any non-refused assistant turn counts; evidence searched in all non-refused turns |
| F11 | accepted | task_success length guard added verbatim |
| Validation (padding probe, within-item length correlation) | deferred | Spearman(answer length, score) per judge is reported as a diagnostic; the padding probe is a T2 follow-up |
Re-smoke after the edits: runs/smoke2/ (2 items, 4 calls; parse ok, 0 false CE on vit-hum-001).
