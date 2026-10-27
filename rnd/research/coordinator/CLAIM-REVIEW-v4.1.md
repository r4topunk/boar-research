# CLAIM-REVIEW v4.1 — independent Opus reviewer (2026-10-15; read-only; 0 judge calls, 0 paid API; blind/ and rnd/veil/ not opened)

Reviewed: rnd c5ef7dfd (v4.0.1 → v4.1 diff), CLAIM-DRAFT.md §0, Appendix A, §1, §4, §6, §7, UNKNOWN; CLAIM-REVIEW-v4.0.md; sources S55/S56 (QUEUE.md rows 10:07, 10:10, 10:17, 10:49, 11:00; handoff/REPLY-MAINTAINER-ALIGNMENT-2026-10-15.md, REPLY-MAINTAINER-UPDATE-2026-10-15.md); arms/longsession/LONGSESSION.md (app window); arms/facts/FACTS-r6-SET4.md; research page artifacts/boar-research-share-2026-10-15/index.html l.143–146, 234, 459–461; `gh pr checks 85` and `gh repo view` (read-only).

**Verdict: ACCEPT WITH EDITS — 1 must-fix, 8 should-fix, 3 nits; 20 mechanical edits (E1–E17, E19–E21; no E18).** Every OLD string below matches CLAIM-DRAFT.md v4.1 exactly once; forward and reverse application give the same file (script on a scratch copy). After all edits: §0 = **898 words** (`**BOAR: …` to the end of "Limits", whitespace split; v4.1 as written = 898), "AI-reviewed, not clinically reviewed" 10 occurrences (unchanged). E14–E17, E19 and E21 are meaning-neutral trims that pay for E1 and E3; apply them together.

**Headline.** The new fact is handled honestly. Every §0 number is attributed to the TypeScript engine, the phone run is attributed to the measurement app, the submitted native app gets no quality statement either way, and §0 matches the research page's scope note. Two problems remain. First, the cuts made to stay under 900 words undid part of a v4.0 must-fix. Second, "the app" in the long-session sentence now points readers to the wrong app. Several body rows went stale on the day: public repos, PR #85, and CI that runs no Android build.

## Findings
| # | Sev | Location | Quote (≤ 15 words) | Problem (evidence) | Edit |
|---|---|---|---|---|---|
| F1 | **must-fix** | §0 "Longer sessions", last sentence | "The app's own window (last 6 messages, plus a summary from turn 8)" | (a) Regression of v4.0 must-fix F2 (E4). The trim removed "so turns 5–7 lose the oldest turns": the bold "no drop to turn 15" holds for full history only, and at turns 5–7 the app drops the oldest turns with no summary in their place (LONGSESSION.md l.104–108). (b) New in v4.1: the window described is the React Native ChatScreen's (cut 7 tree, LONGSESSION.md l.103), but §0 now says the submission is the native app. "The app" therefore points the judges, whose top criterion is longer sessions, to an app whose window nobody has measured | E1 |
| F2 | should-fix | §0 "How we measured", Sets; Appendix A1 | "51 judged bounty-style questions written by a Claude Opus agent, held out" | Regression of v4.0 F4 (E8). The venue clause "(plus 7 venue questions, 0/7 in the claim run)" was cut. The 0/7 is now in §1, §4 row 15 and §5 only, and not in Appendix A, which contradicts the v4.1 changelog ("numbers unchanged and in Appendix A"). The bounty's literal example is a venue question | E3, E5 |
| F3 | should-fix | §0 "What is submitted" | "(FACTS citation check, emergency routing, grounding and health)" | In the measured engine and in the public research repo, FACTS is the 4,233-entity fact table (§3 facts row; FACTS-r6-SET4.md), not a citation check. Pairing it with the port invites a reader to attach FACTS precision (90–97 %) to the native citation check, and our own reply note (point 1) asks the app maintainer not to do that. "FACTS" is also undefined in §0 | E4 |
| F4 | should-fix | §1 "Scope of this claim" | "They are not device results." | The v4.1 changelog says the TypeScript-engine attribution is "said in … §1". It is not: §1 has no TypeScript or native-app wording | E7 |
| F5 | should-fix | §6 row "Android UI wired…" | "Makes the measured ratio apply to the app a user installs." | Check (1): the judges will install the native app. Wiring the React Native chat does not reach it (S55; QUEUE 10:17 "PR-1 … does not reach the native app"). The row also still says "PR-1 carries the wiring commit" | E10 |
| F6 | should-fix | Android UI note "Update v4.0"; §7 PR line; §1 "Not yet done" | "but no device run of that commit yet" | v4.1 removed "no Android build" in two places and added "CI green". PR #85's checks are CodeQL ×2, CodeRabbit and typecheck-and-test (`gh pr checks 85`; ci.yml runs `npm run typecheck` and `npm test`). No Android build ran, so "CI green" without that clause suggests one did. Row 12 still says "not yet built", which is correct | E8, E11, E12 |
| F7 | should-fix | §4 row 9; §1 "Not yet done"; §7 repo line | "The code is in private repos; no public code repository exists." | Stale and contradicted by §0's own links: boar-bench and boar-research are PUBLIC (QUEUE 10:07; `gh repo view`), PR #85 is public, and UPSTREAM_REPO/boar-app is public with branch `fullnative-dev` (`gh`). §7 still says "being prepared … needs the owner's explicit approval" | E8, E9, E13 |
| F8 | should-fix | Appendix A2, A15 row | "raw 0.561 (0.507–0.617) vs 0.558 and 0.560" | Partial regression of v4.0 F1/E2. §0 dropped "(floor-adjusted not computed)" and A2 never carried it, so the only A15 score in the post is a raw score above 0.50 with no floor-adjusted figure beside it. §0 explains raw 0.50 early, so the fix is in A2 only and costs no §0 words | E6 |
| F9 | should-fix | §0 "Longer sessions", first sentence | "Ten 5-turn sessions (three to 15 turns)" | The trim changed the meaning: it now reads as sessions of 3 to 15 turns. In fact all are 5 turns and three are extended to 15 (A3) | E2 |
| F10 | nit | §0 several | "thermal status 0 over the 29-minute run" etc. | Word budget for E1/E3. Meaning-neutral trims: the 29-min wall stays in A2; "pending" stays in the bold "What is submitted" sentence | E14–E17, E19, E21 |
| F11 | nit | title line 3 | "v4.1 awaiting review" | Update after applying | E20 |
| F12 | nit (research page, outside this file) | index.html l.146 glance tile | "The app's 4B build: 0.261." | Sits right under the Scope note and reads as the submitted app scoring 0.261. Replace with "The engine's 4B build: 0.261." on the next page republish | — (page) |

## Self-refutation (findings tested; withdrawn or downgraded)
- **F1 as must-fix?** Counter: the parenthetical gives the window and says it was not run, so a careful reader can infer the gap, and A3's note states it. Kept as must-fix for two reasons. v4.0 made this exact clause a must-fix and v4.1 removed it. And after v4.1, "the app" names the wrong app on the judges' top criterion. Cost: +10 words, paid by the F10 trims.
- **Withdrawn: verdict reuse (v4.0 E7) missing from §0.** §0 no longer says "re-run on cut 6", so it no longer suggests an independent confirmation. The reuse is stated in the Appendix A header ("judge verdicts copied for byte-identical answers") and in §1's lineage bullet, and "cut 7 identical by replay" matches §0's "claim build (cut 7…)". No contradiction.
- **Withdrawn: the dropped "(above 1: …)" clause and "in turns 6–15" scope (v4.0 E3).** The remaining 1.136 has CI 0.993–1.320, which includes 1, so no reason clause is needed. The self-contained clause follows "on turns 6–15" after a semicolon, and A3 scopes it.
- **Withdrawn: the "(rules in CONTRIBUTING)" pointer (v4.0 E22 nit).** §7 names CONTRIBUTING, and the word budget is tight.
- **Withdrawn: "not been measured on the release build" hides the 2026-10-14 dev-build comparison.** The sentence is literally true and says nothing about quality either way. The decision to keep that comparison internal is logged (QUEUE 11:00), and the public research repo carries redaction notes only (release-staging/REVIEW.md l.20).
- **Withdrawn: the "the app maintainer" handle in the PR #85 URL (check 5).** It is a functional link to the public repository the submission lives in, and the research page footer uses the same link. The v4.0 hygiene precedent concerned a competitor's handle in a source line. No personal names appear in §0 or Appendix A.
- **Withdrawn: "for air-gapped testing on GrapheneOS" vs Limits "No GrapheneOS device".** The first states a purpose, not a run. §4 row 1 says "tried by us".
- **Withdrawn: the native bundle's knowledge packs differ from the measured kit (Vital Articles vs Wikivoyage + crypto).** §0 lists the bundle's contents, and the bold "not measured" sentence blocks any transfer of numbers. Adding a sentence would cost words for no gain in honesty.
- **Not a defect: four URLs in §0, not three.** Bench, research and research notes are the three "open" links. PR #85 is the reference-implementation link.

## Checks (1)–(6)
| Check | Result |
|---|---|
| (1) numbers attributed to the TS engine; device run to the measurement app | §0: paragraph 1 "In the measured engine (TypeScript, cut 7)", "On a phone … measurement app with the TypeScript engine (not the submitted native app)", bar paragraph "These are the TypeScript engine's numbers", deep tier "Not in any submitted build". Appendix A header, §4 rows 1, 12, 14 ✓. Gaps: §1 (F4), §6 Android UI row (F5), and "the app's window" (F1) |
| (2) "What is submitted" factual, no quality claim | Two APKs ✓, port of the rules ✓ (FACTS mislabel F3), math through the model / no calculator ✓ (S55 A3), score not measured ✓ (bold), traces requested ✓ (v0.1 60 + longsession-v1 80, matches the reply note point 3). No quality statement either way ✓ |
| (3) caveats after the cuts | **A15 numbers:** §0 (shortened), A2, §1 device bullet, §4 rows 2/8/12, §6; "floor-adjusted not computed" lost → F8. **Venue 0/7:** §1, §4 row 15, §5; lost from §0 and absent from App. A → F2. **Verdict reuse:** App. A header + §1 lineage; no §0 contradiction (withdrawn). **v0.2 plaintext:** §0 Sets ✓, §1 ✓. **Long-session app window:** regressed → F1 |
| (4) §0 ≤ 900, health caveat, three scales, links | 898 words as written and after edits ✓; health caveat in paragraph 1 and Limits ✓ (10 file-wide); three scales defined and ordered ✓; bench, research and notes links plus PR #85 ✓ |
| (5) no names/handles; no competitor or native-app comparison | No personal names, e-mails or paths in §0/App. A. Repo-owner path in the PR URL kept (withdrawn above). No competitor or native-app comparison in §0. The body's competitor phone-speed estimate (§6/§7) predates v4.1 and was reviewed in v3.6–v4.0 |
| (6) consistency with the research page scope note | Page l.144 / l.460: "numbers = TypeScript engine; submitted = native port; its score pending (reported when traces arrive); PR #85 = reference implementation". §0 says the same ✓. Page l.146 glance tile "The app's 4B build" contradicts its own scope note → F12 (page) |

## v4.0 edits: sample of 6 checked against v4.1
| v4.0 edit | Status in v4.1 |
|---|---|
| E9 deep heading "measured on desktop only, never on a phone" + "best of many deep variants" + "Intervals include seed noise" | survived ✓ |
| E11 "Our own pre-registered rule, not the bounty's … desktop only, not shipped" | survived, "not shipped" → "not submitted" ✓ |
| E13 "The win rate is 0 on both sets." | survived ✓ |
| E14 "answers are often thin or partly wrong" | survived ✓ |
| E15 "one of which prompted a fix" | survived ✓ |
| E23 A3 note on turns 6–15 (wrong coin, invented penalty) | survived ✓ |

Also seen beyond the sample: E1 (adapted), E24, E26 survived. E8's v0.2 plaintext half survived. **Partly reverted by the v4.1 trims:** E2 ("floor-adjusted not computed", CI) → F8; E3 ("three extended to 15") → F9; E4 (turns 5–7 drop) → F1; E7 (verdict reuse in §0) → withdrawn; E8 (venue clause) → F2; E22 (CONTRIBUTING) → withdrawn. E18–E21 were superseded by the "What is submitted" / "Reference implementation" rewrite.

## Edits (exact OLD → NEW; each OLD occurs once in v4.1; order-independent)
**E1**

OLD:
```
The app's own window (last 6 messages, plus a summary from turn 8) was not run.
```
NEW:
```
Neither the React Native app's window (6 messages, summary from turn 8; turns 5–7 drop the oldest) nor the submitted app's was run.
```

**E2**

OLD:
```
Ten 5-turn sessions (three to 15 turns) on desktop
```
NEW:
```
Ten 5-turn sessions (three extended to 15) on desktop
```

**E3**

OLD:
```
written by a Claude Opus agent, held out for the 4B claim runs
```
NEW:
```
written by a Claude Opus agent (plus 7 venue questions, 0/7), held out for the 4B claim runs
```

**E4**

OLD:
```
(FACTS citation check, emergency routing, grounding and health)
```
NEW:
```
(emergency routing, grounding and health, citation support)
```

**E5**

OLD:
```
Win rate: 0 on every row and seed. Deep-tier rows:
```
NEW:
```
Win rate: 0 on every row and seed. V-para's 7 venue questions (outside the 51): 0/7 in the claim run (no device location passed); 7/7 only with device location and the user's area tile (§4 row 15; plumbing check, not a quality score). Deep-tier rows:
```

**E6**

OLD:
```
raw 0.561 (0.507–0.617) vs 0.558 and 0.560 |
```
NEW:
```
raw 0.561 (0.507–0.617) vs 0.558 and 0.560 (floor-adjusted not computed) |
```

**E7**

OLD:
```
They are not device results. [S1] [S18] [S19]
```
NEW:
```
They are not device results, and they are the TypeScript engine's numbers, not the submitted native app's (its score is pending [S55]). [S1] [S18] [S19]
```

**E8**

OLD:
```
- **Not yet done:** public repos (snapshots being prepared: https://github.com/r4topunk/boar-bench, https://github.com/r4topunk/boar-research), Android UI integration (PR-1 prepared with a wiring commit not yet built or run on a device [S53]), the deep tier on any phone, public demo post.
```
NEW:
```
- **Not yet done:** the submitted native app's score on our benchmark (traces requested [S55]), Android UI integration (PR #85 open, CI green on typecheck and tests; its wiring not yet built for Android or run on a device [S53] [S56]), the deep tier on any phone, public demo post. Done 2026-10-15: public benchmark and research repos (https://github.com/r4topunk/boar-bench, https://github.com/r4topunk/boar-research; QUEUE.md row "PUBLIC REPOS LIVE (10:07)").
```

**E9**

OLD:
```
| 9 | Public GitHub repo with the functional version | **Not yet** | The code is in private repos; no public code repository exists.
```
NEW:
```
| 9 | Public GitHub repo with the functional version | **Partly met (code public; release not checked by us)** | The submitted native app's code is on a public branch (`fullnative-dev`) of the BOAR app repository, not checked by us [S55]; the measured engine is public as PR #85 [S56]; the benchmark and research record are public (https://github.com/r4topunk/boar-bench, https://github.com/r4topunk/boar-research; QUEUE.md row "PUBLIC REPOS LIVE (10:07)"). A public release of the submitted APKs is the app maintainer's step, not checked by us.
```

**E10**

OLD:
```
| Android UI wired to the measured engine path | Makes the measured ratio apply to the app a user installs. PR-1 carries the wiring commit (tests only; no Android build or device run yet) [S53]. |
```
NEW:
```
| Android UI wired to the measured engine path | Makes the measured ratio apply to the React Native app's chat; it does not reach the submitted native app, a separate port whose score is pending [S55]. PR #85 carries the wiring (CI green on typecheck and tests; no Android build or device run yet) [S53] [S56]. |
```

**E11**

OLD:
```
but no device run of that commit yet, and no UI for
```
NEW:
```
but no Android build or device run of that commit yet (the PR's CI runs typecheck, tests and CodeQL), and no UI for
```

**E12**

OLD:
```
PR #85 open, CI green (reference implementation; no device run of the wiring yet) [S53] [S56].
```
NEW:
```
PR #85 open, CI green on typecheck and tests (reference implementation; no Android build or device run of the wiring yet) [S53] [S56].
```

**E13**

OLD:
```
- [ ] Public repo, install instructions, reproduction steps, model and dataset documentation (rows 9–11). Two curated public repos are being prepared (benchmark: https://github.com/r4topunk/boar-bench; research record: https://github.com/r4topunk/boar-research); publishing needs the owner's explicit approval.
```
NEW:
```
- [ ] Install instructions, reproduction steps, model and dataset documentation (rows 9–11). Done 2026-10-15: two curated public repos (benchmark: https://github.com/r4topunk/boar-bench; research record: https://github.com/r4topunk/boar-research).
```

**E14**

OLD:
```
and will publish the result as "the submitted app".
```
NEW:
```
and will publish the result.
```

**E15**

OLD:
```
The official submission is the app maintainer's
```
NEW:
```
The submission is the app maintainer's
```

**E16**

OLD:
```
These are the TypeScript engine's numbers; the submitted app's score is pending.
```
NEW:
```
These are the TypeScript engine's numbers; the submitted app is unscored.
```

**E17**

OLD:
```
(12 GB class: 10.7 GiB usable RAM, Android 16)
```
NEW:
```
(12 GB class, 10.7 GiB usable, Android 16)
```

**E19**

OLD:
```
thermal status 0 over the 29-minute run.
```
NEW:
```
thermal status 0 throughout.
```

**E20**

OLD:
```
(DRAFT v4.1; independently reviewed through v4.0.1, see CLAIM-REVIEW-v4.0.md and the changelogs; v4.1 awaiting review; not published)
```
NEW:
```
(DRAFT v4.1; independently reviewed through v4.1, see CLAIM-REVIEW-v4.1.md and the changelogs; not published)
```

**E21**

OLD:
```
Desktop median rose to about 22 s at turns 14–15
```
NEW:
```
Desktop median rose to 22 s at turns 14–15
```

## UNKNOWN
- **Research notes link.** [private page] was published PRIVATE (QUEUE 10:48: r4to sets sharing to "anyone with the link"). If it is not shared before posting, §0 carries a dead link.
- **What the Kotlin port contains.** S55 (QUEUE 11:00) does not list the ported rules. §0's list comes from our own spec (REPLY-MAINTAINER-UPDATE l.7) minus the calculator, plus the app maintainer's A13 quote_supports. If the app maintainer cannot confirm emergency routing and grounding/health, shorten it to "It ports rules from the measured engine to Kotlin".
- **Row 9 status.** E9 moves it from "Not yet" to "Partly met (code public; release not checked by us)". That is a content call. A stricter alternative keeps "Not yet" and uses E9's basis text.
- **The branch path** (`android-native/`, `fullnative-dev`) has no repository link in §0. A reader finds it through the PR #85 repository. Adding the link would cost words.
