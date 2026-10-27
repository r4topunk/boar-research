# VG verdict guard: independent review of repairs (criterion V5)
Reviewer: Opus 5.5 (independent; did not write VG; did not open `blind/` or `rnd/veil/`), 2026-10-04.
Inputs: `arms/vg-repairs.jsonl` (32 pairs, 12 runs), `arms/CUT3DEV.md` (VG section), `arms/vg-L0-criterion.md` (sha256 3efcb2c5… verified), engine source `wt/cut3-dev/src/routing/verdictGuard.ts` (read to explain patterns; not modified).

## Verdict: **FAIL** (frozen bar: 0 repaired answers WORSE or WRONG)
- Counts: **BETTER 31 · SAME 0 · WORSE 0 · WRONG 1** (#32, CB lan-cmp-003).
- All 29 pairs from the cut-2, A, E0 and RV2 runs are BETTER. The single failure is in the closed-book (CB) run, which is not the ship stack, but the bar is per repaired answer and is not scoped.
- The failure is a narrow, fixable rank-repair bug (R1 below). After that fix, re-run L0 and re-review only the CB pairs; the other 29 need no re-review if their output stays byte-identical.

## How labels were applied
- **BETTER**: the repaired verdict is correct and consistent with the answer's own facts, and the answer is easier to use than before.
- **WRONG**: the repaired answer, as the user reads it, gives a false answer to the question asked, or the new verdict conflicts with facts the answer states. False content the model wrote that is off the question (e.g. a tangential figure) is flagged as "inherited" but does not by itself make a pair WRONG, because VG neither wrote nor could fix it.

## Fact checks (my own knowledge)
| fact | check | confidence |
|---|---|---|
| Japan ≈ 330–340 people/km², Germany ≈ 230–240/km² | correct to "about"; 339/230 = 1.47, so "about 1.5 times" is correct; differences 108/109 are the right arithmetic | high (exact figure depends on land vs total area and year) |
| First Moon walk 20 July 1969 (Apollo 11); Apollo 12 also in Nov 1969 | correct, so "Yes, before 1970" is correct | high |
| India is 7th by area; the six larger are Russia, Canada, China, US, Brazil, Australia (US/China order depends on how area is measured) | correct | high |
| Kazakhstan ≈ 2.72 M km² < India ≈ 3.29 M km² | Kazakhstan is **smaller** than India | high |
| Polar bear larger than grizzly on average (adult males ~350–700 kg vs ~180–360 kg) | verdict "Yes" correct. The answer's own "average 1,000–1,600 lb" overstates (that is roughly the upper male range) | high on the verdict; inherited figure imprecise |
| Apollo 8 (Dec 1968) and Apollo 10 crews travelled to and orbited the Moon | so "Before that, no humans had ever traveled to the Moon" (#31) is wrong if "that" means Apollo 11; it is inherited and off the question (walking) | high |

## All 32 pairs
| # | run | item | kind | label | reason |
|---|---|---|---|---|---|
| 1 | cut2-s44 | vit-sci-002 | compare | BETTER | Wrong "Germany" verdict + note + "Corrected:" block → one clean correct verdict with 109/km², 1.5×. |
| 2 | cut2-s44 | lan-ref-003 | date | BETTER | "No" → "Yes, astronauts did walk…"; the kept "no walks before that date" (July 1969) stays consistent. |
| 3 | cut2-s44 | lan-cmp-003 | rank | BETTER | "No country" → "Six countries are bigger" (correct). Partial: the question asks "which" and no names are given (no list in the source answer). |
| 4 | cut2-s45 | vit-sci-002 | compare | BETTER | Self-contradiction + "[Note]" → correct verdict, 108/km². |
| 5 | cut2-s45 | lan-ref-003 | date | BETTER | Verdict flipped to correct Yes; rest consistent. |
| 6 | cut2-s45 | lan-cmp-003 | rank | BETTER | As #3 (correct count, no names). Citation marker "[2]" dropped from the verdict sentence. |
| 7 | cut2-s46 | vit-sci-002 | compare | BETTER | Contradiction removed; correct verdict and difference. |
| 8 | cut2-s46 | lan-ref-003 | date | BETTER | Correct Yes; rest consistent. |
| 9 | cut2-s46 | lan-cmp-003 | rank | BETTER | Correct count and the six names taken from the answer's own "after …" list. |
| 10 | cut2-s47 | vit-sci-002 | compare | BETTER | Contradiction and caveat note removed; correct verdict. |
| 11 | cut2-s47 | lan-ref-003 | date | BETTER | Correct Yes. |
| 12 | cut2-s47 | lan-cmp-003 | rank | BETTER | As #3. |
| 13 | A-s42 | vit-sci-002 | compare | BETTER | Also fixes the model's arithmetic ("about 100" → 108 from its own 338 vs 230). |
| 14 | A-s42 | lan-ref-003 | date | BETTER | Correct Yes ("in 1969"). |
| 15 | A-s42 | lan-cmp-003 | rank | BETTER | Correct count + names (Russia, Canada, USA, China, Brazil, Australia). |
| 16 | A-s43 | vit-sci-002 | compare | BETTER | Contradiction removed; correct. |
| 17 | A-s43 | lan-ref-003 | date | BETTER | Correct Yes; "No other moonwalks occurred before that date" remains true. |
| 18 | A-s43 | lan-cmp-003 | rank | BETTER | Correct count + names. |
| 19 | E0-s42 | vit-sci-002 | compare | BETTER | Same as #13. |
| 20 | E0-s42 | lan-ref-003 | date | BETTER | Same as #14. |
| 21 | E0-s42 | lan-cmp-003 | rank | BETTER | Same as #15. |
| 22 | E0-s43 | vit-sci-002 | compare | BETTER | Same as #16. |
| 23 | E0-s43 | lan-ref-003 | date | BETTER | Same as #17. |
| 24 | E0-s43 | lan-cmp-003 | rank | BETTER | Same as #18. |
| 25 | E0-s44 | vit-sci-002 | compare | BETTER | Same as #1. |
| 26 | E0-s44 | lan-ref-003 | date | BETTER | Same as #2. |
| 27 | E0-s44 | lan-cmp-003 | rank | BETTER | Same as #3. |
| 28 | RV2-s42 | vit-sci-002 | compare | BETTER | Wrong lead verdict → correct; figures kept. |
| 29 | RV2-s43 | vit-sci-002 | compare | BETTER | Same. |
| 30 | CB | lan-cmp-002 | compare | BETTER | Self-contradicting "No … not bigger" → "Yes." with the figures; the contradicting "grizzlies are typically heavier" sentence goes. Residue: a dangling "However," and the inherited overstated "average 1,000–1,600 lb". |
| 31 | CB | lan-ref-003 | date | BETTER | Correct "Yes"; the two pre-1970 denials are dropped. Residue: "The idea that astronauts walked on the Moon earlier is false" (true, meaning before Apollo 11, but it reads as a contradiction right after "Yes"), and the inherited "Before that, no humans had ever traveled to the Moon" (wrong for Apollo 8/10 orbits; off the question). |
| 32 | CB | lan-cmp-003 | rank | **WRONG** | New lead "Six countries are bigger than India" sits on top of the model's **seven**-item "Countries larger than India include" list, which includes **Kazakhstan (smaller than India)**, and "smaller than all of the above" is kept. The user's answer to "which countries" now names a false country, and the new count contradicts the answer's own list. The dangling "The statement is false —" is also left. VG read the rank and ignored the bulleted list. |

## Pattern-level risks (from the pairs and the code)
| id | risk | evidence | severity | fix |
|---|---|---|---|---|
| R1 | **Rank repair ignores the answer's own enumerated list.** `checkRank` reads the list only from "after/following/behind X, Y, Z"; a bulleted list is never compared with n − 1. | #32 | **blocks V5** | Abstain (return null) when the answer has a bullet or numbered list under a "larger/bigger than" lead whose item count ≠ n − 1. When it equals n − 1, name those items as now. |
| R2 | **Wrong metric, same unit.** `quantities` takes the first number after each entity mention and checks only that the unit strings match, not that the metric matches the question. "Which is more densely populated, the Netherlands or Brazil?" answered with populations ("18 million people" vs "216 million people") would flip a **correct** verdict to Brazil. | code (`quantities`, `unitSig`); not in the 32 | high in real traffic | Require a unit that fits the comparative (density → "per km²/mi²"; heavier → mass; taller/longer → length), or require both numbers in one sentence with parallel structure. |
| R3 | **"older/younger" with dates.** Polarity "max" assumes bigger number wins; with founding/birth years the bigger year is younger. Years 1500–2100 without a unit are skipped, but years outside that range (e.g. 1096) are parsed. | code (`MORE_WORDS` has "older") | medium | Drop older/younger from the compare check unless the unit is "years old"/an age. |
| R4 | **Ratio on interval scales.** "about N times as much" is printed for any unit; for °C/°F, elevations below sea level or negative values it is meaningless or wrong. The difference uses range low ends only. | code (`BY_HOW_MUCH` branch) | medium | Print the ratio only for ratio-scale units (counts, mass, length, area, density); never for temperature or values ≤ 0. For ranges, omit the difference. |
| R5 | **VG trusts the stated facts.** If the model states a wrong number but the right verdict, VG confidently flips it to the wrong verdict. No case among the 32 (all stated facts were right), but V1 was tuned on these traces and the 30 probe questions have no answers. | CUT3DEV disclosure | medium–high, unmeasured | Before ship, generate answers for `probes/vg-questions.probes.jsonl` (and a few wrong-figure lookalikes) and count false fires. |
| R6 | **Residual old-verdict sentences** after partial deletion: "The idea … is false", "The statement is false —", dangling "However,". | #30, #31, #32 | low (confusing, not false in #30/#31) | Also drop sentences that only assert falsity of an unnamed "statement/idea/claim" when the verdict flips; strip a leading "However," from the first kept sentence. |
| R7 | **Date check takes the first year in the first "first …" sentence.** A sentence like "first proposed in 1890 but not built until 1925" or a "first" about a different event decides the verdict. | code (`checkDate`) | low–medium | Abstain when the fact sentence has more than one year. |
| R8 | **Citation markers dropped** from the rewritten verdict sentence ("[1]", "[2]"). | #3, #6, #9, … | low (provenance) | Carry the verdict sentence's citation markers into the template. |
| R9 | Rank count can come from any "Nth-largest" sentence, even one about another entity or another metric. | code (`rankSeg = segs.find`) | low | Require the rank sentence to mention X. |

No unit mismatch was found among the 32: lb vs lb (bears) and people/km² vs people/km² (density); kg values in parentheses were correctly ignored by `unitSig`.

## What would turn this into PASS
1. Fix R1 (abstain on list-count mismatch). #32 then stays unflagged (its original wrong answer is unchanged, so VG is neutral on it).
2. Re-run `tools/vg-l0.mts` and confirm the other 31 repairs are byte-identical; re-review only changed pairs.
3. R2 and R5 are not V5 blockers on this set, but they are the main real-traffic risks; measure R5 before shipping VG.

AI-reviewed, not clinically reviewed (no clinical content here; factual checks are from model knowledge, flagged above where imprecise).
