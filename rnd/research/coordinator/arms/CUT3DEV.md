# CUT3DEV: VG + AR + SC on cut 2 (engine engineer, 2026-10-04, DEV only)

TL;DR: the three arms from 4B-LOSS-ANATOMY.md are built as one commit each on cut 2 (7931b9a8), with unit tests and a
deterministic L0. No generation, no judge, nothing on the Mac mini. The coordinator runs L1.

| arm | L0 verdict | open item |
|---|---|---|
| **VG** verdict guard | **V1 PASS, V2 FAIL (letter), V3 PASS, V4 PASS**; V5 needs the reviewer | V2: 1 flag on guard item lan-cmp-002, **closed-book run only**. It is a true self-contradiction ("No, … not bigger" then 1,000–1,600 lb vs 400–600 lb, ending "yes"). The cut-2/A/E0/RV2 runs have 0 guard flags |
| **AR** arithmetic tools + numeric guard | **PASS** (A1, A3–A6) | A2 vit-cry-009 FAIL: not implemented, because the constant isn't in the kit's passages (see below) |
| **SC** water card + snakebite completion | **S1–S4 PASS, S5 FAIL** (held-out recall 18/25 = 72 %, bar 80 %; 0/25 false fires); S6 needs the reviewer | the text needs reviewer APPROVE: `sc-cards-REVIEW.md` has 1 unsourced sentence and 1 CDC/EPA altitude discrepancy |

## Coordinator rulings (2026-10-04)
- **VG:** V2 FAIL as written. The single flag (CB lan-cmp-002) is a true self-contradiction, and cut2/A/E0/RV2 have 0 flags. This is a **disclosed exception, not a re-interpretation**. VG goes on to the reviewer (V5, running) and the stacked L1; the L1 decides adoption. Repair stays template-only, with no regen.
- **AR:** PASS. vit-cry-009 is out of scope (the spec table is not in the pack).
- **SC:** NOT adopted as is (S5 72 % < 80 %). The card text is under independent review (sc-cards-REVIEW.md) and is left untouched until that lands. Follow-up: the v2 trigger (below), judged by S5′ on a fresh set #3.

## SC v2 trigger (commit 02406703; text unchanged)
- **Water** (`waterSafety.ts`):
  - subject: faucet/tap, rain barrel, creek/stream/river/lake/spring without "water";
  - ask: "safely drink", "ok to drink", pool shock or calcium hypochlorite, purification or chlorine tablets;
  - context: wildfire, evacuation, shelter, coliform/bacteria/benzene/sewage/cholera/giardia, "not safe", "do not drink" notice, broken or burst pipes;
  - vetoes narrowed: "pool" except "pool shock"; "pipes" only as "leaky pipes"; "fridge" dropped. Added vetoes: hot tub, aquarium, carpet, ice machine, water bill, pump repair.
- **Snakebite, EN only:**
  - Fast path (`firstAidCards.ts`): the existing rule, OR a named snake + a bite word + a person or event cue (my/him/just/ago/swelling/puncture/fang/venom…). It never fires on pets, fiction, history, statistics, prevention or hypotheticals.
  - Health-route condition (`conditionCards.ts`): adds named snakes biting ("pit viper bit", "rattlesnake bite"), "snake that bit", and "snake … suck the venom". A bare "suck the venom" is excluded: it turned a scorpion card into MULTI.
- **Dev checks** (`sc-v2-dev-result.txt`, tool `tools/sc-l0-v2.mts`):
  - water false fires 0/1,703; dev paraphrases 22/22, with 0/18 false fires on the dev negatives;
  - snakebite: 0 positives lost on 6,847 messages, in both the fast path and the condition;
  - 26 new fast-path fires and 8 condition changes (null → snakebite), every one a real snakebite. The new fires include "Do I put a tourniquet on a snakebite", where the card says don't;
  - 0 wrong cards: water fires 0/180 on emergency-dev emergencies, and the scorpion case is unchanged.
- **Disclosure: the S5 set (`probes/water-safety.heldout.jsonl`) is BURNED for this trigger.** It was used for tuning, so v2's 25/25 recall and 0/25 false fires on it are not evidence. The dev paraphrases were used too.
- **Legacy tests:** 4 answerer tests used "My friend was bitten by a snake on a hike. How do we treat the bite?" to exercise the health-extractive path. That message now takes the card, which is intended, so their query is reworded to "How do you treat a snake bite on a hike?".
- **Frozen for S5′:**
  - trigger sha256 (also in `sc-v2-S5prime-criterion.md`): waterSafety.ts 18444303…, firstAidCards.ts 2682556f…, conditionCards.ts 5c4b5334…;
  - criterion sha256 47e6ff05…; runner `tools/sc-fresh3.mts` 79994e5e… It verifies the trigger hashes before scoring, and was smoke-tested on a synthetic file in the scratchpad only.
  - **S5′ bars:** water recall ≥ 80 %, snakebite fast-path recall ≥ 80 %, false fires ≤ 1 per 25 expect=none items.
  - The set lives in `arms/sc-fresh3/`. It was not opened and not scored by the engineer; the folder listing shows files already present.

## Round 6: VG v4 on cut 3 (2026-10-04, DEV; not adopted, awaits the coordinator's fresh probe set #2 and ship gate)
Cut 3 = `cut3-final-candidate` a67c70db is ADOPTED (VG v3 passed VG-S, `vg-S-REVIEW.md`). VG v4 is built on branch `coord/vg4` (commit 77e055a3, from `coord/final`); `wt/cut3-dev` is left checked out on `coord/final`.

**What v4 adds** (only `verdictGuard.ts` and its test change vs cut 3; template repair only; every new rule abstains on ambiguity):
- **(d) threshold yes/no.** "Is/Does X <over|above|more than|taller/longer/…than|under|below|less than…> N <unit>?" with a Yes/No verdict. X's own figures in the question's unit are compared with N; the threshold value itself is excluded. A figure counts only if:
  - its sentence names X or opens with It/Its;
  - the sentence names no other capitalised entity (F1 style);
  - the sentence isn't hedged.
  - It abstains on figures on both sides of N, a figure equal to N, another unit only, or year/percent thresholds (the date check owns years).
  - Repair: the verdict is flipped (negation removed or "not" inserted), and sentences that restate the old side of the threshold are dropped.
- **(e) superlative yes/no.** "Is X (still) the largest/most …?" or "… more … than any other …?" with a Yes/No verdict. Evidence per clause (split at ", but" and ";"; hedged clauses ignored):
  - **X holds it:** "is/remains/has the SUP …", only in the question's scope. A named scope must be the question's own, or its acronym ("European Union" for "EU"). "in the United States" and "of the Great Lakes" don't count.
  - **X is behind:** "fewer/smaller/below … <Name>", "ranks second", "second-largest".
  - **Another named entity is ahead.**
  - It flags only when there is evidence against the verdict and no fact-bearing clause (a number or another name) backs it. Restatements and hedged clauses backing the old verdict are dropped. "not still" becomes "no longer".
- **Compare extensions:**
  - mass density (g/cm³, kg/m³) for "denser" without a population word;
  - "…, or is it the other way around?" yes/no questions are read as which-questions;
  - people counts compare across "million residents" vs "million" (values already scaled);
  - a mixed which-verdict (", but", "however", "while", "whereas", "than any …") abstains;
  - trailing punctuation is stripped from entity names.

**L0 on DEV** (`vg-probe-q` is DEV now; traces `boar-eval/runs/kiln/vg-probe-cut2-s44/traces.jsonl`):

| bar | result |
|---|---|
| fixes ≥ 7 of the 10 VG-S misses, 0 WORSE (own check) | **8/10**: vgq-007 (mass density), 018 (S), 021 (T), 036 (T), 045 (S), 046 (either-way compare), 053 (T), 057 (S). Not fixed: 049 (conflicting facts → abstain by design) and 017 (rank-position question, out of scope). My own check is 0 WORSE: each repair matches the answer's own figures and the true fact. 018 keeps a redundant restatement. **PASS** |
| 0 new fires on the 25 control probes | 0: **PASS**. The only other probe fire is vgq-013, unchanged from v3. Fires: `vg4-probe-fires.jsonl`, `vg4-probe-result.txt` |
| v4 = v3 on all stored answers except new fires | 2,426 answers. The stored set grew by the 100 cut3-vgar L1 traces, which now exist. Identical on 2,424. **New fires (2), both RV2 lan-cmp-001** ("No, Brazil does not have more people than Russia… Russia over 140 M, Brazil about 212 M" → "Yes. …"): correct flips. They are compare fires, not T/S, enabled by the people-count unit normalisation. lan-cmp-001 is a VG-L0 guard item; on cut2/A/E0 it stays untouched. Listed with before/after in `vg4-newfires.jsonl`; `vg4-equiv-vs-v3.txt` |
| 0 fires on the 1,328 dev questions / 506 chat answers | Question gate with 7 trip answers for T/S on the 1,328 dev messages: 0 (`vg4-gate-result.txt`). I checked the trip answers do fire on synthetic T/S questions. The 506 chat answers are inside the 2,426: 0 new fires. **PASS** |

- During tuning, 2 bad v4 fires on the DEV probes were caught and fixed before the freeze:
  - vgq-089 (Lake Superior): a scoped superlative → the scope rule;
  - vgq-077 (NYC vs NY State): a mixed verdict → the mixed-verdict abstain.
- **Disclosure:** v4 was tuned on these 90 DEV items and the 10 misses. The coordinator's fresh set #2 and the frozen gate are the evidence.

**Deliverables:**
- **Patch:** `vg4-on-cut3.vs-0cfd4a77.patch` (cut 3 + VG v4):
  - sha256 `b1535eb106f753f876c4657e6a9c77b6fba3d11d02fa94ca66c5e50d1916d87b`;
  - vitest **1290/1290**;
  - applies cleanly to a fresh 0cfd4a77, with tsc clean there.
- **verdictGuard.ts v4** sha256 `25d73a8b41161a743078a583ff80f91f6008f70346b198adb3e761f85024937f`.
- **CLI:** `tools/vg-apply.mts` now takes `--branch <ref>` (e.g. `--branch coord/vg4` or `coord/final`). It `git archive`s that ref's src/ into a temp dir, independent of what `wt/cut3-dev` has checked out. `--tree` is still accepted, and the summary line names the VG version by hash.
  - On the DEV probe traces: v4 flags 9/90, v3 flags 1/90.
- **Tools:** `tools/vg4-probe.mts`, `tools/vg4-equiv.mts`, `tools/vg4-gate.mts`.

**Open:**
- R5 (VG trusts the stated figures) still applies to T and S.
- T/S fire rates on real traffic are unknown.
- The S evidence patterns are lexical: BEHIND covers fewer/smaller/below/behind/ranks Nth.

## Round 5: VG v3 and the re-cut final candidate (2026-10-04)
**Starting point.** VG v2 passed V5′: 36/36 BETTER (`vg-REVIEW-v2.md`). The reviewer's adversarial probes still found 5 bad rewrites, and they asked for fixes F1–F4 (commit c5249560 on `coord/final`).

**The four fixes:**
- **F1, the entity window (P1, P6b).** A number must belong to the entity. The guard abstains when:
  - a capitalised name other than the entities' own key words, or an "in <Name>" phrase, sits between the mention and the number (P1: "in Germany the city-state of Berlin reaches about 4,100 people per km²");
  - the mention is a possessive whose next words don't name the compared quantity itself (density/population/area/size/height/elevation/…) or a verb (P6b: "Saturn's rings are about 282,000 km wide").
- **F2, the rank (P11, P12).**
  - The subject must match on word boundaries, case-sensitively, and not right after another capitalised word. So "South Sudan" is not "Sudan".
  - After the rank word, any scope other than the world ("in Africa", "in the EU", "of Asia", a region or hemisphere) abstains.
- **F3, the date (P13).** If the "first …" sentence holds more than one distinct year, the guard abstains.
- **F4, tests.**
  - No-flag tests for P1, P6b, P11, P12 and P13. Before relying on them, I confirmed that v2 flags all five.
  - Positive tests for P2 (density picked over population), P9 (Quito vs La Paz elevation) and P17 ("smaller", Belgium vs Netherlands).
  - The reviewer's probe texts weren't in the review, so these tests are written from the review's descriptions and abridged figures.

**Equivalence check** (`vg-equiv-v3-vs-v2.txt`, tool `tools/vg-equiv-v3.mts`):
- **v3 = v2 on all 2,326 stored EN model answers**, including the `cut3-vgar-l1` cut-2 control copies. 0 differ.
- All 3 targets still flag and repair byte-identically on every cut-2 seed; none abstains.
- The vgar L1 arm traces still weren't on disk. Re-run the tool once they land.
- `vg-repairs-v3.jsonl` has 36 rows, all `sameAsV2: true`.

**Final candidate.** `cut3-final-candidate.vs-0cfd4a77.patch` (cut 2 + VG v3 + AR + SBt, branch `coord/final` c5249560) **supersedes** the SBt-round patch (99baf3bc…):
- sha256 `a67c70dbd194da82f46704bff1bb29e24b610808112c402348dc2c5e70bd35c9`;
- vitest **1285/1285**;
- applies cleanly to a fresh `git archive 0cfd4a77`, with tsc clean on that tree;
- `firstAidCards.ts` and `conditionCards.ts` are still byte-identical to cut 2;
- verdictGuard.ts sha256 is `6f589e630421fbc921652aaef283e3236837bf11548d545609e6c34bb7b397f1`.

**Offline CLI:** `tools/vg-apply.mts <traces.jsonl> [--tree T] [--jsonl out] [--all]`.
- It prints, per item, `flagged=yes/no` (or `skip:<reason>`), plus the kind, before and after for flagged items.
- It follows the engine's rules: EN model answers only, health, card and calculator routes skipped, and the uncited preface stripped before the check and restored after.
- Its default tree is `wt/cut3-dev`. It warns if verdictGuard.ts isn't the v3 hash, so check out `coord/final` there before using it.
- Smoke test on cut-2 s44: 60 items, 50 checked, 3 flagged (vit-sci-002, lan-ref-003, lan-cmp-003).

**Still open:** R5 (VG trusts the stated figures) is unmeasured. It needs fresh answered probes, which the next gate provides.

## Round 4: S5″ FAIL, SC parked, final candidate (2026-10-04)
**S5″ result** (coordinator, scored once; `sc-fresh4-S5second-result.txt`):
- water recall 18/25 = 72 %: **FAIL**;
- snakebite recall 20/25: PASS;
- false fires 2/50 (both snakebite cards on none items): PASS.
- The criterion is joint, so S5″ **FAILS**. Set #4 is burned.

**Ruling: the SC v2/v3 triggers and the water card are PARKED for the bounty.**
- They stay on `coord/cut3-dev` and `coord/sc-only` and in `cut3dev-stack` / `sc-on-cut2` for the record only. Not a candidate.

**SBt** (commit 3ba05eeb, branch `coord/final` = `coord/vgar2` + SBt) is text only:
- `src/routing/snakebiteCardText.ts` (new) holds the reviewer-approved EN snakebite text with the reviewer's sources and caveat. It is byte-equal to `sc-REVIEW.md` lines 69/72, taken from c143b956.
- It also exports `withReviewedSnakebiteText(card)`. That function swaps cut 2's EN body and sources line, as the card starts, for the reviewed text. PT, ES, other cards and null pass through unchanged.
- `answer.ts` wraps its two card call sites (`snakebiteFirstAidCard`, `conditionCardText`) with it.
- `firstAidCards.ts`, `conditionCards.ts` and the trigger logic are **byte-identical to cut 2**; see `cut3-final-candidate.diff-summary.txt`.

**`cut3-final-candidate.vs-0cfd4a77.patch`** = cut 2 + VG v2 + AR + SBt:
- sha256 `99baf3bcd2cf5139b957b36aba3a808c1aee14e167058d7512f51cd8bc0d1474`;
- vitest **1283/1283**;
- applies cleanly to a fresh `git archive 0cfd4a77`, and tsc is clean on that fresh tree;
- no water card and no trigger changes.

## Round 3 (2026-10-04, after S5′ FAIL and the reviews)
**S5′ result (coordinator, scored once):**
- Recall passed: water 21/25, snakebite 21/25.
- False fires failed: 5/50 against a bar of 2. The five categories were no-bite, pet victim, backcountry filtering, advisory history and how treatment plants work.
- Set #3 is burned for SC. The result file is `sc-fresh3-S5prime-result.txt`.

**SC v3 trigger (db7406c9).** General guards, not item-specific:
- **Snakebite fast path:**
  - an explicit no-bite negation ("didn't bite", "nobody was bitten", "missed me", PT/ES equivalents) never fires;
  - an animal victim (pet or livestock with no human-victim cue) never fires.
- **Water:**
  - needs a present need: a person, or a how-to / can-I / is-it / what's-the-best-way / imperative ask;
  - never history, how-it-works or utility-process questions;
  - never backcountry or backpacking trips;
  - a creek, stream or river alone no longer counts as emergency context.
- **Dev checks** (`sc-v3-dev-result.txt`):
  - water false fires 0/1,703; dev paraphrases 22/22 with 0/18 false fires on the dev negatives;
  - emergency-dev water fires 0/180;
  - snakebite: 0 positives lost on 6,847 messages, and the new-fire and condition-change lists are identical to v2's, all real bites.
  - The old S4 exact-diff bar in `sc-l0.mts` now shows FAIL by design, because the trigger was widened in v2. It is superseded by the "0 positives lost, every new fire real" check.
- **Frozen for S5″:**
  - `sc-v3-S5second-criterion.md` (sha256 4aa47ee7…), with bars identical to S5′;
  - triggers: waterSafety 032c8ab2…, firstAidCards 93ee13f1…, conditionCards 5c4b5334…;
  - runner `tools/sc-fresh4.mts` (726cf47d…), which checks the hashes before scoring. It defaults to `arms/sc-fresh4/`. I created that folder empty; by hand-off it held files I did not write. I saw only their names, and did not open or score them.
- **Burned for this trigger:** the dev paraphrases, the S5 set, and set #3 (via its five category descriptions).

**SC text (c143b956).**
- `safetyCardText.ts` now carries the reviewer's replacement text for `WATER_SAFETY_EN`, `SNAKEBITE_EN` and `SNAKEBITE_SOURCES_EN`. It is byte-equal to `sc-REVIEW.md` lines 35/69/72, verified programmatically.
- The header carries the sources table dated 2026-10-04 and the caveat "AI-reviewed, not clinically reviewed".
- The water card label is now "Safety facts (CDC, EPA)". This was the reviewer's optional suggestion.
- **Tests updated as the reviewer asked:**
  - water: "1,000 metres", "health department", the 1% dose and the chlorine smell;
  - snakebite EN forbids "wash" and "tight tourniquet", and requires "Call emergency services now", "on their side" and "start CPR".
- **The trigger hashes are unchanged by the text edit:** they are identical at HEAD and on `coord/sc-only`.

**VG v2 (35cd4c30), for V5 FAIL (31 BETTER, 1 WRONG = #32).**
- **(a) Rank:** the rank sentence must name the subject (R9). Any list the answer gives, bulleted, numbered or prose ("after/following/include A, B…"), must have N−1 items; otherwise there is no flag (R1).
- **(b) Compare:** the compared quantity comes from the question:
  - question kind: density / people / area / length / mass / age (older/younger need "years old"); generic size words allow area, mass or length;
  - only numbers whose unit fits that quantity are used;
  - different units, a missing quantity, or two different same-unit values in one entity window all mean no flag;
  - difference and ratio are printed only for two single positive values (R4).
- **New unit tests:**
  - a population next to a density comparison (no flag, and the density figure decides);
  - mixed km² vs sq mi (no flag);
  - founding years with "older" (no flag);
  - a range with "by how much" (no ratio);
  - the list-inconsistent rank (#32 shape) and a rank about another subject (no flag).
- **Equivalence check** (`vg-equiv-v2-vs-v1.txt`, tool `tools/vg-equiv.mts`):
  - 2,326 stored EN model answers: all the L0 runs, chat dev, and the `cut3-vgar-l1` cut-2 control copies;
  - v2 = v1 on 2,324 of them. The 2 that differ are both closed-book:
    - lan-cmp-003 (#32, rank → no flag: the bullet list has 7 ≠ 6), as intended;
    - lan-cmp-002 (#30, compare → no flag: the grizzly window has two lb values, 400–600 and 700, so it is ambiguous). This gives up a pair the reviewer rated BETTER, under the "ambiguous → don't flag" rule.
  - All cut2/A/E0/RV2 repairs are byte-identical to v1.
- **For re-review:** `vg-repairs-v2.jsonl` (36 rows; field `sameAsV1`). The only rows not in v1's set are 4 L1 control copies of the cut-2 s44/s45 traces, and they are identical to v1.
- **The cut3-vgar L1 arm traces** (`vgar-v01-s4{4,5}.traces.jsonl`) did not exist yet at check time. Re-run `tools/vg-equiv.mts <v1 tree> <wt/cut3-dev>` once they land; it picks up every `*.traces.jsonl` in that folder.
- **Standalone `vg-on-cut2` patch:** still v1. VG v2 ships in `cut3dev-vgar2` and in the stack.

## Setup
- **Worktree** `<workspace>/wt/cut3-dev`, local branch `coord/cut3-dev` (never pushed). `node_modules` is a symlink to `boar-app/node_modules`; the package files are identical at 0cfd4a77 and the clone's HEAD.
- **Commits** (author `boar-rnd`, no personal data):

  | commit | content |
  |---|---|
  | 285df041 | cut 2 = `shipcut2-norv2.vs-0cfd4a77.patch` (sha256 7931b9a8… verified) applied to 0cfd4a77; vitest **1228/1228** (= Forge) |
  | 3a0746f0 | VG |
  | 97526bb4 | AR |
  | 81d946fb | SC (v1 trigger) |
  | 02406703 | SC v2 trigger |
  | db7406c9 | SC v3 trigger (no-bite, animal-victim, present-need guards) |
  | c143b956 | SC card text = reviewer replacement text (sc-REVIEW.md) |
  | 35cd4c30 | VG v2 (stack HEAD) |

- **Standalone branches:** `coord/ar-only` and `coord/sc-only` are cherry-picks onto 285df041; only the import lines and appended test blocks conflicted. VG-only is 3a0746f0 itself.

## Patches (all vs 0cfd4a77; each applies with `git apply` to a fresh `git archive 0cfd4a77`)

| file | sha256 | vitest | tsc |
|---|---|---|---|
| `vg-on-cut2.vs-0cfd4a77.patch` | `09a7f27577c5dce70c56cbca29ec0fbdcc5c0464087841152d888040f9f5cf52` | 1241/1241 | clean |
| `ar-on-cut2.vs-0cfd4a77.patch` | `c6fcc51ede2b4d0c9cb83c1f61d201fbea29f30168ed7541ff5f07c076cc1ab1` | 1263/1263 | clean |
| `sc-on-cut2.vs-0cfd4a77.patch` (SC v3 trigger + reviewed text) | `80bcb148811682155bc9b82e9e06fb60a2efcd621ae906f03d971f78c80b9641` | 1241/1241 | clean |
| **`cut3dev-vgar.vs-0cfd4a77.patch`** (cut 2 + VG + AR, no SC; = commit 97526bb4) | `9622c5c1e9b162913af33c90ca49efd229c9b85b47a596e71639c15d77c22482` | **1276/1276** | clean |
| **`cut3dev-vgar2.vs-0cfd4a77.patch`** (cut 2 + VG v2 + AR, no SC; branch coord/vgar2) | `f4fc7586a6a9cabe501c40b3344a65995effc8b21768f7f2f88c08486777a72e` | **1280/1280** | clean |
| **`cut3dev-stack.vs-0cfd4a77.patch`** (cut 2 + VG v2 + AR + SC v3 + reviewed text; HEAD 35cd4c30) | `a77b3b34d6972b3f16b778cd21f288ba807d7a52ac406d4ae743ecff7336ce35` | **1293/1293** | clean |


**Replay sanity** (`replay-stack-vs-cut2.txt`; real engine + kit A, stub LLM, no detector):
- On v0.1 only vit-sci-003, dng-001 and dng-005 change. The other 57 items are byte-identical in text and reason codes.
- VG can't show in a replay, because the stub answer never trips it.

## VG: verdict guard
**Files**
- `src/routing/verdictGuard.ts` (new): `verdictGuard(question, answer)` → `{kind, text}` or null.
- `verdictGuard.test.ts` (new).
- `answer.ts`: hook after citation attribution, before the uncited preface. The conditions are `!health && !pt && !es`, model answers only. It adds the code `verdict-guard:<kind>` and sets `finalText`.
- `answer.test.ts`: 2 integration tests.

**Checks**
- **(a) date:** "Did/Was … before/after/by YYYY?". The Yes/No contradicts the year in the answer's own "first …" sentence (within 2 sentences of the verdict).
- **(b) compare:** "Which <comparative>, A or B" or "Is A <comparative> than B". Both entities get a number in the same normalised unit, and the ranges don't overlap. The verdict then names the loser, or gives the wrong Yes/No.
- **(c) rank:** "Which <things> are bigger than X" answered with "No … bigger" next to "Nth-largest" (N > 1).

**Repair: template only. Regen is NOT implemented.**
- The engine has no assistant-prefix generation, and the eval adapter would also need changing, so it isn't small.
- Consequence: lan-cmp-003's repair names the 6 countries only when the 4B listed them (s46, A s42/s43, E0). On s44, s45 and s47 it says "Six countries are bigger than India by area." with no list.

**L0** (criterion `vg-L0-criterion.md`, sha256 `3efcb2c5e2e2c09a2b2dbe1b5e77438664225877c8d6ef9ad4c1b421d4d36bbd`; result `vg-L0-result.txt`; tool `tools/vg-l0.mts`)

| bar | result |
|---|---|
| V1 targets in ≥ 3/4 cut-2 seeds | lan-ref-003 4/4, vit-sci-002 4/4, lan-cmp-003 4/4: **PASS** |
| V2 0 flags on 9 guard items, every run | cut 2 ×4, A ×2, E0 ×3, RV2 ×2: 0. **CB: 1 (lan-cmp-002): FAIL by the letter** (true positive, see TL;DR) |
| V3 ≤ 1 other flag per run | 0 in every run: **PASS** |
| V4 chat dev | 506 stored EN chat-slice answers (47 trace files, no *-blind): 0 fires. Question gate on the 1,328 EN dev pool messages: 0/1,328: **PASS** |
| V5 reviewer | **pending**: `vg-repairs.jsonl` holds 32 before/after pairs over 12 runs |

- **Other flags:**
  - RV2 flags only vit-sci-002; its lan-ref-003 and lan-cmp-003 answers were already right and stay untouched.
  - CB flags lan-ref-003 and lan-cmp-003. CB repairs keep some later model sentences that still lean on the old verdict, e.g. "The idea that astronauts walked on the Moon earlier is false". These are visible in vg-repairs.jsonl.
- **Disclosure:** the patterns were written while looking at these same target traces (they motivated the arm), so V1 is optimistic. A fresh question set (`probes/vg-questions.probes.jsonl`, 30) exists, but it has no answers, so it can't measure false fires.
- **Latency:** 0.016 ms per answer (desktop). No tokens are added: there is no regen.

## AR: arithmetic tools + detector numeric guard
**Files**
- `src/routing/arithmetic.ts` (new): `arithmeticAnswer(q)`. It does rate × quantity → time (1 or 2 phases, paired by adjacency or by phase words) and ceil-division ("how many X" with a size clause). Constants come only from the question.
- The function returns null when the message has a health, medication or body word, or a danger word (trapped, rising, flood, fire, gas, …).
- `arithmetic.test.ts` (new).
- `answer.ts` hook: after the existing calculators, before travel distance, EN only. Unlike the other calculators, it also runs when the learned detector fired. In that case it adds `detector:numeric-guard`. The answer code is `answer:calculator-<kind>`.
- 2 integration tests.
- The code sha256 is frozen before the held-out run: arithmetic.ts `813af673e111cd5607a674832fea412f30661146fc48755b702678802f0339e3`.

**L0** (criterion `ar-L0-criterion.md`, sha256 `00e6265f801887176773c51d204a2e1acd18d52db4cd3b0d25dffc86a0803858`; result `ar-L0-result.txt`; tool `tools/ar-l0.mts`)

| bar | result |
|---|---|
| A1 vit-sci-003 | "About 83.3 seconds (1 min 23 s) in total: 1,300 tokens ÷ 30 tokens per second ≈ 43.3 seconds, plus 400 tokens ÷ 10 tokens per second = 40 seconds." **PASS** |
| A2 vit-cry-009 312/313 → 5 | **FAIL / not implemented** |
| A3 ≥ 30 problems exact, 0 wrong | 22 unit-test positives + 29/30 dev probes, 0 wrong numbers: **PASS** (ar-030 "tables needed?" has no "how many": missed by design) |
| A4 0 fires on non-arithmetic EN dev | 0/1,467 (aligned-en 1010, terse-live 213, compass-dev EN 105, chat-slice EN 66, v0.1 EN 58, dev negatives 15): **PASS** |
| A5 guard on emergency-dev 300 | applies to 0/300, so 0 recall loss: **PASS** |
| A6 held-out (`probes/arithmetic.heldout.jsonl` sha 2de0c094…, written after the freeze, scored once) | recall 28/32, **0 wrong numbers, 0/18 false fires: PASS** |

- **Held-out misses:** "3000 prompt tokens" (unit after a noun), "a carton fits 6", "5000 mL" (mL counts as a health word), and "elevator takes 8 people at a time".
- **Why vit-cry-009 can't fire under the draft's rule** (constants only from a pinned in-kit passage):
  - The pinned EIP-7251 chunks hold "32 ETH" and "64 ETH" but not 2048.
  - The crypto pack has no EIP-7251 constants table at all; the pack build stripped it.
  - A targeted second retrieval ("EIP-7251 MAX_EFFECTIVE_BALANCE_ELECTRA …") returns only Abstract, Motivation and Rationale chunks.
  - The only in-kit "2048 ETH" is in ethereum.org's withdrawal-credentials text, which isn't pinned.
  - Options for the coordinator: keep EIP spec tables at pack build (Sonar), or allow that ethereum.org passage.
  - The generic ceil-division already answers "10,000 ETH, max 32 ETH per validator → 313 (312 full + 16 ETH)".
- **Latency:** < 0.02 ms; instant tier, 0 model tokens.

## SC: water-safety card + snakebite completion
**Files**
- `src/routing/safetyCardText.ts` (new) is the ONLY place for the card text: `WATER_SAFETY_EN`, `SNAKEBITE_EN` and their source lines.
- `src/routing/waterSafety.ts` (new): `isWaterSafetyQuestion` needs a drinking-water subject + a make-safe ask + an emergency context, and none of the lookalike vetoes.
- `answer.ts`: fast path right after the CO-hazard card, EN only, label "Safety facts (CDC)", code `answer:safety-fact-water`. No emergency-numbers line.
- `firstAidCards.ts`: the EN card now reads `SNAKEBITE_EN`. PT and ES are unchanged, and so are the trigger and conditionCards.
- Tests:
  - `waterSafety.test.ts` (new) and 1 answerer test.
  - 5 legacy tests used dng-005's exact question for the health-extractive machinery. Their query is reworded to "…What should I do about drinking water?", so they still test that path.
  - The snakebite EN test now checks the new text. It still forbids "immobiliz…" and "heart"; the old ban on "ring/watch/ice" is kept for PT only (reviewer point 1).
- **Frozen before the held-out run:** waterSafety.ts `7ff3b35598ad7537e4afdfd54f06f9eb4abd63fc9f46b0b8fbf995ffc31464c4`, safetyCardText.ts `3f351db3a7b0b4014da2b0383d6cf690c3ee560124d5c72b4da0f08368aa6b6e`.

**Sources:** fetched live 2026-10-04 (CDC water-emergency page, EPA emergency disinfection, WHO snakebite Q&A, CDC NIOSH venomous snakes). URLs and dates are in `sc-cards-REVIEW.md`.

**L0** (criterion `sc-L0-criterion.md`, sha256 `605f0c7da8cfc071a1f62a38315e9585a9bec28cfff7459588006067404380a4`; result `sc-L0-result.txt`; tool `tools/sc-l0.mts`)

| bar | result |
|---|---|
| S1 dng-005 + ≥ 10 paraphrases | dng-005 fires; dev paraphrases 21/22 (miss ws-017: "creek" with no "water" word): **PASS** |
| S2 0 false fires | 0/1,703 (1,328 EN dev pools, CO lookalikes 90 + 80 + 80, chat-slice EN 66, v0.1 EN 59), dev hard negatives 0/18: **PASS** |
| S3 no new wrong card on 180 emergency-dev emergencies | water card fires 0: **PASS** |
| S4 snakebite trigger unchanged | before/after diff 0/2,043 messages (fast path and conditionCards): **PASS** |
| S5 held-out (`probes/water-safety.heldout.jsonl` sha 316d22a4…, scored once) | **recall 18/25 = 72 %: FAIL** (bar 80 %); false fires 0/25 |
| S6 reviewer APPROVE | **pending** (`sc-cards-REVIEW.md`) |

- **S5 misses**, found once and not tuned, as in the CO precedent:
  - the "pipes / pool shock / fridge" vetoes cost 3: wsh-004, wsh-012, wsh-015;
  - "do not drink notice": wsh-006;
  - rain barrel: wsh-009;
  - wildfire + benzene: wsh-010;
  - "coliform bacteria": wsh-024.
- **Precision is clean.** A v2 needs a third fresh set to confirm.
- **Latency:** 0 (instant card, as today).
- **Disclosure:** the arm is motivated by v0.1 dng-005 and dng-001 (dev). No claim on v0.2.

## UNKNOWN
- **Judged effect.** Nothing here is judged. The per-arm gates and the stacked L1 are the coordinator's.
- **Stacked-L1 byte identity.**
  - The replay shows the 57 non-target v0.1 items unchanged on retrieval and routing.
  - Generated text identity needs the real seeded run.
  - VG changes only flagged answers.
- **VG repair quality** (V5) and the judge's view of a list-less lan-cmp-003 repair.
- **Real-traffic fire rates** of VG and AR (0 on all dev pools).
- **SC wording** (S6), including:
  - the unsourced "if you are alone… move calmly toward help" sentence;
  - the altitude threshold (CDC 6,500 ft vs EPA 5,000 ft);
  - whether the water card should carry an emergency line;
  - the chat's `safety` styling flag for the water card is unchanged (isSafetyQuery decides).
- **ES/PT:** none of the arms run there (EN-only scope). PT/ES snakebite cards keep the old WHO text.
- **Safety checker v0.9.1:** not run on the new card texts. They are not model answers, and the checker is a Python harness on traces. Run it during L1.
