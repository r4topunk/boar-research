# VG v2: independent re-review (criterion V5′)
**Verdict: PASS on the frozen bar.** Of 36 repaired pairs, 36 are BETTER, 0 SAME, 0 WORSE and 0 WRONG. **Not a ship clearance:** adversarial probes still turn 2 correct comparison verdicts wrong (P1, P6b), plus 3 wrong fires in the rank and date checks (P11–P13).

Reviewer: Opus 5.5 (independent; did not write VG; did not open `blind/` or `rnd/veil/`), 2026-10-04.
Inputs:
- `arms/vg-repairs-v2.jsonl` (36 rows);
- `CUT3DEV.md`, VG v2 section;
- `wt/cut3-dev` at 35cd4c30: `src/routing/verdictGuard.ts` (sha256 ca7366c1…) and `verdictGuard.test.ts`.

The engine code was not modified. The probes ran the pure function from a copy in the scratchpad, using `node --experimental-strip-types` (Node 25.9).

## 1. Labels (36 pairs)
I diffed every v2 row against v1 by run and item. All 36 `before` and `after` texts are **byte-identical** to the v1 rows I labelled BETTER in `vg-REVIEW.md`. The `L1:cut2-v01-s44/s45` rows are byte-identical to the v1 `cut2-s44/s45` rows. The two v1 rows missing from v2 are the ones v2 now leaves unflagged:
- CB lan-cmp-003 (#32, v1 WRONG);
- CB lan-cmp-002 (#30, v1 BETTER; now ambiguous because the grizzly window holds two lb values).

| rows | run(s) | item | label | reason (same as v1) |
|---|---|---|---|---|
| 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 29, 31, 34 | cut2 s44–47, A s42/43, E0 s42–44, RV2 s42/43, L1 s44/45 | vit-sci-002 | BETTER | Wrong "Germany" verdict or self-correction → "Japan … by about 108/109 per km² (≈1.5×)", from the answer's own figures; arithmetic fixed where the model said "about 100". |
| 2, 5, 8, 11, 14, 17, 20, 23, 26, 32, 35 | same cut2/A/E0 runs + L1 | lan-ref-003 | BETTER | "No" → "Yes, astronauts did walk on the Moon before 1970" (Apollo 11, July 1969); the kept "none before that date" stays consistent. |
| 30 | CB | lan-ref-003 | BETTER | Correct "Yes". Residue as in v1: "The idea … earlier is false" (true, but reads oddly) and the inherited Apollo 8 imprecision. |
| 3, 6, 12, 27, 33, 36 | cut2 s44/45/47, E0 s44, L1 s44/45 | lan-cmp-003 | BETTER | "No country" → "Six countries are bigger than India by area" (correct); no names, because the source answer listed none. |
| 9, 15, 18, 21, 24 | cut2 s46, A s42/43, E0 s42/43 | lan-cmp-003 | BETTER | Correct count + the six names from the answer's own "after/following" list. |

The v1 failure (#32) is resolved, because v2 abstains when the bullet list has 7 items and the count is 6. I re-checked it in the unit test and in the equivalence note.

## 2. Probes: population vs density, mixed units, and others
Scripts and output are in the scratchpad (`…/scratchpad/vg2/adv.ts`, `adv2.ts`, `adv.out.txt`). "Safe" means no flag, or a flip to the verdict the facts support.

| # | shape | question → answer (abridged) | VG v2 | result |
|---|---|---|---|---|
| P2 | population **and** density, wrong verdict | NL vs Brazil; "NL 18 million people and 520 people per km², Brazil 216 million people and 25 people per km²", verdict Brazil | flips to NL | ✅ density figure chosen, population ignored |
| P3 | population only, "more populated" | NL vs Brazil, people counts only | null | ✅ ("populated" isn't a density cue; no flag) |
| unit test | population only, density question | NL vs Brazil, people counts only | null | ✅ (v1 flipped this correct verdict) |
| P4 | density format mix | "233 people/km²" vs "339 people per km²" | null | ✅ unit strings differ |
| P5 | scale mix (area) | Alaska "1.72 million km²" vs Texas "696,000 km²" | null | ✅ (a missed flip, but safe) |
| P7 | mass mix | "700 kg" vs "800 lb" | null | ✅ |
| unit test | km² vs sq mi | — | null | ✅ |
| P8 | two values for one entity | Empire State "381 m to its roof and 443 m with its antenna" | null | ✅ ambiguous → abstain |
| P9 | elevation, wrong verdict | Quito vs La Paz, 2,850 m vs 3,640 m | flips to La Paz | ✅ correct |
| P10 | age with "years old" | Stonehenge 5,000 vs Great Pyramid 4,500 years old, verdict Stonehenge | null | ✅ |
| P14 | different metric, different unit | Canada "9.98 million km²" vs US "12,000 miles of coastline" | null | ✅ |
| P15 | common word in an entity key ("new" for New York) | "new suburbs add 9.9 million people…" | null | ✅ (this phrasing) |
| P16 | "less dense" polarity | Canada 4 vs Australia 3.5 per km², verdict Australia | null | ✅ |
| P17 | "smaller" polarity, wrong verdict | Belgium 30,689 vs NL 41,850 km², verdict NL | flips to Belgium | ✅ correct |
| **P1** | **sub-region figure attributed to the country**, correct verdict | "Japan is more densely populated than Germany. Japan has about 339 people per km², while in Germany the city-state of Berlin reaches about 4,100 people per km²." | **"Germany is more densely populated than Japan."** | ❌ **correct verdict turned WRONG** |
| **P6b** | **another attribute of the same entity**, correct verdict | "Jupiter is bigger than Saturn. Jupiter is about 139,820 km wide, while Saturn's rings are about 282,000 km wide." | **"Saturn is bigger than Jupiter."** | ❌ **correct verdict turned WRONG** (with "km across" vs "km wide" it abstains only because the unit strings differ) |
| **P11** | rank with a regional scope | "No country is bigger than Sudan. Sudan is the third-largest country in Africa." | "Two countries are bigger than Sudan." | ❌ false (about 15 countries are larger; the original was also false) |
| **P12** | rank subject is a substring | "No country is bigger than Sudan by area. South Sudan is the 42nd-largest country." | "41 countries are bigger than Sudan by area." | ❌ reads another country's rank |
| **P13** | date: first year belongs to another event (v1 R7, unchanged) | "Was the Channel Tunnel opened before 1990?" → "No, it was not. The first plans … date from 1802, but it opened in 1994." | "Yes, it was. …" | ❌ correct verdict turned WRONG |

**On the risk I raised (population vs density, R2):** fixed as specified. Only numbers whose unit matches the question's quantity are used. Mixed units, mixed scales and mixed formats all abstain, and two different same-unit values in one entity window abstain.

**What remains is attribution, not units.** The entity window still runs from the entity's mention to the other entity's next mention. So any same-unit number in that span is credited to the entity, even when it belongs to:
- a part of the entity (Berlin in P1);
- another attribute of it (Saturn's rings in P6b).

## 3. Recommendations (not blocking V5′; I'd fix them before ship, because each flips a correct answer)
| id | fix | covers |
|---|---|---|
| F1 | Credit a number to an entity only when no capitalised name, possessive noun ("Saturn's rings") or "in <Name>" phrase sits between the mention and the number. Otherwise abstain. | P1, P6b |
| F2 | Rank: match the subject on word boundaries and not right after another capitalised word ("South Sudan"). Abstain if the rank sentence has a scope other than "in the world" ("in Africa", "in Asia", "in Europe", "in the EU"). | P11, P12 |
| F3 | Date: abstain when the "first …" sentence has more than one year (v1 R7). | P13 |
| F4 | Add P1, P6b and P11–P13 as no-flag unit tests, and P2, P9 and P17 as positive tests. | regression |

Unchanged from v1 and still unmeasured: **R5**. VG trusts the stated facts, so a wrong figure with a right verdict gets flipped. Real-traffic exposure looks low: there were 0 fires outside the 3 targets on 2,326 stored EN answers. But each wrong fire is a confident error, so measure it on a fresh answered probe set before ship.

AI-reviewed, not clinically reviewed.
