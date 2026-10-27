# Review: README-claim.md, DEMO-SCRIPT.md, DEMO-POST-DRAFT.md (Refresh + whole) — independent Opus reviewer, 2026-10-11

Sources: CLAIM-DRAFT v3.8 (§1, §4, §5), repro/demo-answers/ANSWERS.md + cut7-demo-s42.traces.jsonl, HANDOFF-2026-10-11 §5, CLAIM-READINESS-2026-10-10, repro/BOM.md, repro/REPRODUCE.md, EXPOSURES.md TL;DR, arms/facts/FACTS.md, handoff/DEMO-QUERIES.md, BOUNTY_31.md, bench-app/src/runner.ts + bench-app/reports/cut7-nonet/SUMMARY.md. No blind/ or rnd/veil/ read, no boar-eval history, no LLM/judge calls, no commits.

**Verdict: ACCEPT WITH EDITS** (3 blockers, 7 major, 9 minor, 3 nits; all edits applied except m9 and the nits, see reasons). The 3 blockers were all in DEMO-SCRIPT and are fixed.

Checks passed: every number matches CLAIM-DRAFT §1: V-para 0.413 (0.384–0.445) / 0.261 (0.224–0.299) / 0 of 51; v0.2 two-seed 0.513 (0.479–0.550) / 0.389 (0.347–0.435) / 0/0/110 (s42); D = 0.306; Haiku 0.588 (0.48); A15 73/73, p50 49 s, p90 77 s, instant 8.5 s, PSS 4.41 GiB, 0.561 vs 0.558/0.560. No file uses the single-seed 0.397 or HANDOFF §1's 0.40/0.519. Set status, "no unexposed English set", same-family closed judge, win-rate 0, deep tier excluded, venue wording, and speed "cut 6, 8 GB A15" were all present in the README. BOM consistency holds: APK sha256 6eb8cb45… (row 14), tree 7c96e59e…, patch 0fba26b8… (row 11 = ANSWERS l.3), 3.03 / 2.50 / 0.39 GB, tile 0.2–1.1 MB, t-N52E013 in rows 16-24.

## Findings (line numbers = pre-edit files)
| # | Sev | File:line | Problem | Fix (applied) |
|---|---|---|---|---|
| B1 | blocker | DEMO-SCRIPT:18-26 | lan-rsn-007 was described as a retrieval/Wikivoyage model answer. In the cut 7 capture it is a facts-tier answer (Wikidata, 0 sources, 0.1 s) | Item 2 is now lan-rsn-006 (4B answer, 2 Wikivoyage sources, cites [2], 8.0 s). lan-rsn-007 is now a backup that can only swap for item 3 |
| B2 | blocker | DEMO-SCRIPT:41 | vit-sci-003 was described as an "arithmetic tool route" with a 49 s model-answer reference. The capture is instant "Calculator": the detector fired (p 0.29) and the numeric guard kept it off the safety path | Route corrected and a phone check added |
| B3 | blocker | DEMO-SCRIPT:54-59 | The venue path cannot be filmed with BOAR Bench cut 7: runner.ts hard-wires the location fix to "unavailable", and the APK has no location permission (SUMMARY.md) | Item 6 is now conditional: a real location fix plus the tile, or disclose a simulated location; otherwise drop it and use backup vit-trv-004 |
| M1 | major | DEMO-SCRIPT:8 | "Card before the model" was wrong: the trace shows a 5.4 s route-gate model call, then the card with 0 generated tokens. The card text has no caveat. The timing reference used the model-answer p50 | Corrected. Caveat added as an on-screen caption. Phone reference changed to "cards behind the gate 17.5–52 s (cut 3 A15 smoke)" (CLAIM-DRAFT §4 row 8) |
| M2 | major | DEMO-SCRIPT selection | 5 of 6 answers came without the 4B, including two near-identical facts items | Final 6: vit-hlt-001 card, lan-rsn-006 4B + citation, lan-cmp-001 facts, vit-sci-003 calculator, vit-cry-004 4B + 4 crypto sources, venue (conditional). All items except the venue are 1.5B-fail rows |
| M3 | major | DEMO-SCRIPT:63-70 | The checklist did not say the answers are desktop or that the phone run can differ. It omitted that BOAR Bench has no chat UI and is driven by adb, and it named only 2 items for rerun | All three added. All 6 items are rerun twice (detector items first), and any item that differs from the script is dropped |
| M4 | major | POST:12, :19 | Floor-adjusted only, plus "Bar not met". This contradicts CLAIM-DRAFT §4 row 14 "Not shown" (the v0.2 raw CI contains 0.50) and the HANDOFF §5 default | Post 3 and the cast now give raw / floor-adjusted / wins and say "Bar not shown above" (Post 3 278 chars; cast 939 bare) |
| M5 | major | POST:19 | The cast said "the 4B's answers", but in ANSWERS.md the card and the facts table answer two of the filmed items | Changed to "cut 7's answers". The query list was dropped to stay within 1,024 characters |
| M6 | major | README:40, :55 | Linked EXPOSURES.md, which is not in the package and is private (REPRODUCE §6) | Now "team-internal ledger, not in this package; per-set status in REPRODUCE.md §6" |
| M7 | major | README Limits | Missing: the Android chat UI is not on the measured path, and there is no public repo or install steps (CLAIM-DRAFT §4 rows 9-10, UI note) | Limit bullet added |
| m1 | minor | README:23 | "(v0.2 raw 0.512 vs 0.513)" had an unclear order | "0.513 on cut 3, 0.512 on cut 6; V-para 0.413 on both" |
| m2 | minor | README:33 | The phone's 0.561 had no named scale and no CI | Now "raw ratio 0.561 (0.507–0.617)", with "floor-adjusted and win-rate not computed for this comparison" |
| m3 | minor | README:21 | The bar text was not stated, and the Haiku floor-adjusted 0.48 was missing | Both added |
| m4 | minor | README:30-31 | "p50" was not labelled; the APK's signing and hosting were not stated | Now "model answers p50…, no network permission"; "debug-signed, not hosted" |
| m5 | minor | README:39 | "Measurement APKs (cut 4 to cut 7)" | Now "no-network builds of the measurement app"; the cut 3 bench APK was network-capable (E1) |
| m6 | minor | POST:32 | Refresh listed only 0(a), (b), (d) as open | All five are open. Added the BOAR Bench limits and "DEMO-SCRIPT supersedes checklist items 2 and 6" |
| m7 | minor | POST:22 | "(none built yet)" was stale, and the owner's handle appeared twice (leak grep) | 0(a) updated; the handle is replaced by "the owner" |
| m8 | minor | DEMO-SCRIPT | 70 lines, over the 60-line limit | Now 51 lines |
| m9 | minor | POST:6 | Post 1 mentions first-aid cards without the caveat | **Not applied:** this is pre-existing text and the caveat does not fit in 280 characters (284+). Post 4 of the same thread and the video caption carry it |
| n1 | nit | README:38 | "Shown before the model": in the jellyfish trace, the route-gate call comes first (no answer tokens) | Kept, because it is CLAIM-DRAFT §3 wording |
| n2 | nit | README:19, :45 | "v0.2 written by Claude-family writers" conflicts with EXPOSURES (writer model UNKNOWN) | Kept: CLAIM-DRAFT §5 wins. The coordinator should reconcile the ledger |
| n3 | nit | DEMO-SCRIPT 3 | Brazil 214.2 M is labelled "(2026)" | Verbatim engine output, kept |

## Edits to DEMO-POST-DRAFT text above "Refresh"
Every edit fixes a factual contradiction: Post 2 l.9 (Berlin Wall replaced by the Hundred Years' War, since it is no longer in the script); Post 3 l.12 and the cast l.19 (scales and bar wording, "cut 7's answers"); precondition l.22 (APK state and owner handle). All are listed in the file's Refresh section.

## Caveat grep (`grep -n 'AI-reviewed, not clinically reviewed'`)
README-claim.md:8, :38, :50 · DEMO-SCRIPT.md:9, :50 · DEMO-POST-DRAFT.md:15, :19, :26, :34. Every card mention is covered except POST:6 (m9).

## Leak grep (`grep -n -i -E 'r4to|the app maintainer|<maintainer-name>|<users-dir>/|tester|blind/|veil/|@'` on the three files)
0 hits (rc = 1). The pre-edit hit was POST:22 ("r4to" twice), now removed.

Residuals (not text): all of POST precondition 0 is open (product APK, public repo, phone, owner OK). Item 6 can only be filmed with a location-capable build.
