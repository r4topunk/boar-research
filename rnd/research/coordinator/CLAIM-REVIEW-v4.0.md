# CLAIM-REVIEW v4.0 — independent Opus reviewer (2026-10-15, closing sprint; read-only; 0 judge calls, 0 paid API; blind/ and rnd/veil/ not opened)

**Verdict: ACCEPT WITH EDITS — 2 must-fix, 9 should-fix, 5 nits; 26 mechanical edits (E1–E26).** Every OLD string below matches CLAIM-DRAFT.md v4.0 exactly once, the edits do not overlap, and applying them in forward or reverse order gives the same file (checked by script on a scratch copy). After all edits: §0 = 898 words (`**BOAR: …` to the end of "Limits", whitespace split; v4.0 as written = 876), "AI-reviewed, not clinically reviewed" 10 occurrences (unchanged), BENCH_REPO_LINK / RESEARCH_REPO_LINK placeholders 4 / 4 (unchanged). Several should-fix edits add words; E5, E6, E12, E16, E17, E19, E20 and E21 are meaning-neutral trims that keep §0 under 900. Apply them together.

**Headline: the text is honest and nearly ready.** It never says the bar is met or that BOAR wins. Floor-adjusted numbers lead on every quality set, the deep tier is fenced off, and PR-1's untested wiring is stated. The two must-fixes are both §0 omissions on exactly the points this review was asked to check: (1) the POCO 0.529 (Haiku) sits next to the A15 0.561 (Opus) with no warning that the levels are not comparable, and both are raw-only scores above 0.50; (2) the long-session result was measured with full history on the desktop, but §0 does not say that the app drops the oldest turns at turns 5–7 before any summary exists. That gap bears directly on the judges' top criterion (consistent quality over longer sessions).

## Findings
| # | Sev | Location | Quote (≤ 15 words) | Problem (evidence) | Edit |
|---|---|---|---|---|---|
| F1 | **must-fix** | §0 "On a phone" | "raw 0.529 vs 0.529 … (one run, Haiku judge)" | (3) The text never says the POCO level is not comparable with Opus numbers, so a reader compares 0.529 (cut 7) with the A15's 0.561 (cut 6, Opus) and reads it as a regression. A2 and §1 carry the caveat, but §0 is the post (DEVICE-X6.md:3, :28–29; QUEUE.md:711). (2) Both phone scores are raw-only and above 0.50; the POCO floor-adjusted 0.403 vs 0.402 exists (DEVICE-X6.md:28–29), and the A15 has none (an earlier README review used "floor-adjusted not computed"). Also missing: the runs were in the measurement app with the same engine code, not the user app (DEVICE-X6.md:6; PR-DESCRIPTION.md:67) | E1, E2 |
| F2 | **must-fix** | §0 "Longer sessions" | "The app keeps the last 6 messages plus a summary, which bounds the prompt" | (4) The bold "no drop to turn 15" holds only for full history on the desktop (LONGSESSION.md:7, :100). The app drops the oldest turns at turns 5–7 with no summary in their place (LONGSESSION.md:102–106), and §0 hides this; the draft's own UNKNOWN lists it. Also: "11 s at turn 1" conflicts with A3's turn-1 median of 9.1 s (LONGSESSION.md:14 vs :66). "On self-contained questions 1.017" applies only to turns 6–15, 17 items (:81); turns 2–5 give 1.205 (:22). A ratio above 1 needs a one-clause reason. The required items (dev data, agent-written, one seed, Haiku judge, latency cost) are present | E3, E4 |
| F3 | should-fix | §0 claim build | "Measured on cut 3 and repeated on cut 6" | Cut 6 copied the verdicts of byte-identical answers and judged only 10 item-seeds fresh (CLAIM-RESULTS-cut6.md l.20–29). This is v3.9 objection §2.4, fixed in §1 but not carried into §0 | E7 |
| F4 | should-fix | §0 Sets | "v0.2 … held out at the time, since exposed" | The v0.2 plaintext was in a private repository's history from 2026-10-02, before the claim runs (§1 l.82 [S47]; v3.9 §2.1); a rival reading the research repo will find it. The text also drops V-para's 7 venue questions silently: they scored 0/7 in the claim run (CLAIM-RESULTS-cut3.md:63), and the bounty's literal example is a venue question. The new wording states only the claim-run 0/7, so the "with device location and the user's area tile" rule is not triggered | E8 |
| F5 | should-fix | §0 deep tier | "measured on desktop only; needs a 12 GB phone" | The previous paragraph shows a 12 GB-class phone in hand, so "needs a 12 GB phone" invites "why not run it?" (DEVICE-X6.md:40; relapse of v3.9 R1). Also missing: the selection caveat (best of many deep variants on exposed sets; v3.9 §2.6, §6 l.82 "selection inflates it"). The v0.2 interval is seed-noise but not labelled as such (BAR-TABLE.md:128) | E9, E10 |
| F6 | should-fix | §0 bar | "The pre-registered rule is a raw-ratio 95% CI above 0.50" | The judges score with the bounty's shared rubric, so "the pre-registered rule" reads as the bounty's. It is our analysis plan's rule (BAR-TABLE.md:7). "Meets it" also needs "not shipped" next to it so a skim cannot attach it to BOAR | E11 |
| F7 | should-fix | §0 bar | "The win rate is 0 everywhere." | A2 shows POCO W/T/L 2/1/54 (DEVICE-X6.md:28): 2 wins on v0.1 dev. The 0 holds on V-para and v0.2 (BAR-TABLE.md:80) | E13 |
| F8 | should-fix | §0 bar | "answers are often right but thin" | True for the deep tier (BAR-TABLE.md:95). For the 4B claim build on V-para, correctness is ≤ 2 on 49 % of items and ≥ 4 on 27.5 % (§4 row 7; BAR-TABLE.md:93). A rival can quote the overstatement | E14 |
| F9 | should-fix | §0 Limits | "0 unsafe-rule hits on 10 danger questions" | One of the 10 (generator indoors) motivated the CO card and is "not independent evidence" (§3 safety-cards row; CLAIM-RESULTS-cut3.md:47–50). The caveat is in the body only | E15 |
| F10 | should-fix | A3 note | "0 in turns 6–15" | It counts only the card and detector defects. In turns 6–15 there is a history-caused wrong referent (ls02-t11, LONGSESSION.md:114) and a context-primed invented penalty (ls02-t14, :118) | E23 |
| F11 | should-fix | §7 deep line | "device run still pending (needs a 12 GB phone)" | Stale: the POCO exists; it has run only the 4B build (§6 row 1, UNKNOWN) | E24 |
| F12 | nit | §0 What ships | "1,378/1,378 tests" | The count includes the wiring commit; the engine-only branch is 1,360/1,360 (PR-DESCRIPTION.md:57, :132). Moved off the "byte-identical" clause | E18 |
| F13 | nit | §0 Open | "so every team gets an unexposed set" | A promise the repo cannot keep alone. The writer-family rule also excludes the contributor's own app family (release-staging/bench/CONTRIBUTING.md rule 2): point to CONTRIBUTING | E22 |
| F14 | nit | §4 row 6 | "in any of the three measurement APKs (E1)" | §0's "no Google Play Services code" rests on the cut 7 no-network APK audit (0 GMS, QUEUE.md:897), which is not cited | E26 |
| F15 | nit | title line 3 | "v4.0 pending review" | Update after applying | E25 |
| F16 | nit | §0 throughout | "p50", "PSS", long parentheticals | Jargon and word budget: "median" replaces p50 where touched; meaning-neutral trims keep §0 ≤ 900 after F1–F9 | E5, E6, E12, E16, E17, E19, E20, E21 |

## Self-refutation (findings tested and withdrawn or downgraded)
- **F2 as must-fix?** Counter: §0 already says "that policy itself was not run here." Kept: the sentence does not say that the policy *drops* turns 1–2 at turns 5–7, and a judge testing longer sessions in the app will hit exactly that. Cost: +12 words.
- **F7 is conservative (it understates)?** Kept as should-fix, because "everywhere" is false against the document's own A2.
- **Withdrawn:** moving "Where we stand" earlier (the bold lead-ins already allow a 5-minute scan, and the numbers → bar order is logical). The body's competitor phone-speed estimate (§6/§7) is a cited measurement, not a quality comparison, reviewed v3.6–v3.9, and absent from §0. The 4B V-para CI 0.299 vs BAR-TABLE 0.300 is the cut 3 figure (notes l.9; §0 says cut 3). "72/72" vs "73/73" is 72 items plus a warm-up (DEVICE-X6.md:11). The V-para grading-field print stays in §1 only: no questions or answers were printed, and the word budget is tight. "Desktop median 79 s" vs v0.2's 82.4 s: the v0.2 figure is in A1. The POCO is called "12 GB class" with 10.7 GiB stated.
- **Not a text defect (coordinator):** CLOSING-SPRINT Q8 says "numbers only after the shared rubric exists" for the bounty chat. §0 is full of numbers, so confirm that §0 goes out as the submission post, not as a chat message, before the rubric.

## Checks (1)–(10)
| Check | Result |
|---|---|
| (1) numbers vs sources | All §0/Appendix figures trace: 0.261 (0.224–0.299) / 0.413 CLAIM-RESULTS-cut3.md:57, :61; 0/0/51 BAR-TABLE.md:35; 0.389 / 0.513 cut3.md:24; 0/0/110 · 0/1/109 BAR-TABLE.md:53; D 0.306 :14; deep D/T/H/TV rows :37–39, :55–57; seed-noise CIs :126–129; bar readings :70–73, :80; correctness 0.427 / 0.660 :88–89; POCO DEVICE-X6.md:6, :14–20, :28–32; A15 QUEUE.md:711, κ :543; LONGSESSION.md:14–22, :66, :76–81, :104–108; PR-1 PR-DESCRIPTION.md:57–59, :107–108, :122, :132; safety cut3.md:42–50; 4,233 PR-DESCRIPTION.md:15. Mismatches: 11 s vs 9.1 s, 1.017 scope (F2); "win rate 0 everywhere" vs A2 (F7); A3 "0 in turns 6–15" (F10). Unsourced: none |
| (2) honesty / raw 0.50 | No "bar met / wins / beats". Bar statement matches BAR-TABLE §1c and the bottom line. Raw-only above 0.50: the phone scores (F1). Whose rule: F6 |
| (3) POCO label, A15 cut 6 | A15 correctly cut 6; POCO label missing in §0 (F1) |
| (4) long sessions | dev, agent-written, one seed, Haiku and latency all present; full history and the app gap missing (F2) |
| (5) deep tier desktop-only | Fenced, but heading and §7 stale (F5, F11); selection caveat (F5) |
| (6) PR scope, open source | Accurate (PR-DESCRIPTION.md:94–132); placeholders remain; F12, F13 nits |
| (7) readability | 10 bold-led paragraphs, ≤ 900 words, scales defined before use; jargon trims F16 |
| (8) attack surface | F3, F4, F8, F9 (hidden caveats), F5 (phone in hand) |
| (9) personal data / internal | grep for names, handles, e-mail, <users-dir>/, team and agent names: none in the post or appendix (one internal folder name in the path of evidence key "E4, GrapheneOS", body only). No native-app comparison, no competitor quality comparison |
| (10) health caveat | §0 paragraph 1 and Limits; 10 occurrences file-wide |

## v3.9 standing objections
§2.1 v0.2 wording: regressed in §0 → F4. §2.4 verdict reuse: regressed in §0 → F3. §2.5 judge.v1-med: held (A2). §2.6 selection: missing in §0 → F5. §2.7 seed-noise CIs: held. §4.4 win rate reported, not gated: held. R1 "no 12 GB device": relapsed in the §0 heading and §7 → F5, F11. RIVALSET: nothing added (held).

## Edits (exact OLD → NEW; each OLD occurs once in v4.0; order-independent)

**E1**

OLD:
```
Cut 7 ran on a POCO X6 Pro (12 GB class: 10.7 GiB usable RAM, Android 16) in airplane mode, without the INTERNET permission: **72/72** answered, 0 crashes. Fast-tier answers (the 4B path) p50 30.7 s, p90 48.4 s.
```
NEW:
```
Cut 7 ran in our measurement app (same engine code) on a POCO X6 Pro (12 GB class: 10.7 GiB usable RAM, Android 16) in airplane mode: **72/72** answered, 0 crashes. Fast-tier answers median 30.7 s, p90 48.4 s.
```

**E2**

OLD:
```
On 57 v0.1 development items it matched the desktop: raw 0.529 vs 0.529, paired −0.000 (−0.026…+0.028) (one run, Haiku judge). Earlier, cut 6 on an 8 GB Galaxy A15, same conditions: 73/73 answered, model answers p50 49 s, PSS max 4.41 GiB; phone 0.561 (0.507–0.617) vs desktop 0.558 and 0.560 on the same 57 items (Opus judge).
```
NEW:
```
On 57 v0.1 development items it matched the desktop: floor-adjusted 0.403 vs 0.402, raw 0.529 vs 0.529 (one run; Haiku triage judge, level not comparable with Opus). Earlier, cut 6 on an 8 GB Galaxy A15, same conditions: 73/73, model answers median 49 s; raw 0.561 (0.507–0.617) vs desktop 0.558 and 0.560 on the same 57 items (Opus judge; floor-adjusted not computed).
```

**E3**

OLD:
```
three extended to 15 turns; each in-session answer paired with the same question asked standalone. **No quality drop was detected out to turn 15**: in-session/standalone ratio 1.397 (1.187–1.673) on turns 2–5, 1.136 (0.993–1.320) on turns 6–15; on self-contained questions 1.017 (0.950–1.095), parity.
```
NEW:
```
three extended to 15 turns, on desktop with full history; each in-session answer paired with the same question asked standalone. **No quality drop was detected out to turn 15**: in-session/standalone ratio 1.397 (1.187–1.673) on turns 2–5, 1.136 (0.993–1.320) on turns 6–15 (above 1: asked alone, a follow-up lacks context); on self-contained questions in turns 6–15, 1.017 (0.950–1.095), parity.
```

**E4**

OLD:
```
The cost is speed: with full history, desktop p50 rose from 11 s at turn 1 to 22 s at turns 14–15 (about 8 s standalone). The app keeps the last 6 messages plus a summary, which bounds the prompt; that policy itself was not run here.
```
NEW:
```
The cost is speed: desktop median rose to about 22 s at turns 14–15 (about 8 s standalone). The app sends only the last 6 messages, plus a summary from turn 8, so turns 5–7 lose the oldest turns; that app policy was not run.
```

**E5**

OLD:
```
Ten five-turn sessions (follow-ups that point back, topic switches, deepening),
```
NEW:
```
Ten five-turn sessions (follow-ups, topic switches, deepening),
```

**E6**

OLD:
```
Limits: 80 development questions written by a Claude agent, one seed, Haiku judge, and the reference is
```
NEW:
```
Limits: 80 agent-written development questions, one seed, Haiku judge; the reference is
```

**E7**

OLD:
```
Measured on cut 3 and repeated on cut 6; cut 7's answers on both sets are identical.
```
NEW:
```
Measured on cut 3, re-run on cut 6 (verdicts reused for unchanged answers); cut 7's answers equal cut 6's.
```

**E8**

OLD:
```
**V-para**, 51 judged bounty-style questions written by a Claude Opus agent, held out for the 4B claim runs (2026-10-05/06), development-style since; **v0.2**, 110 questions by Claude-family agents, held out at the time, since exposed (now development data);
```
NEW:
```
**V-para**, 51 judged bounty-style questions written by a Claude Opus agent (plus 7 venue questions, 0/7 in the claim run), held out for the 4B claim runs (2026-10-05/06), development-style since; **v0.2**, 110 questions by Claude-family agents, held out at the time but stored in plaintext in a private repository before the claim runs; now development data;
```

**E9**

OLD:
```
**Deep tier: measured on desktop only; needs a 12 GB phone.** Qwen3.6-35B-A3B with a 512-token thinking budget, development data. V-para (two seeds): floor-adjusted **0.436** (0.387–0.486 with seed noise) vs 0.261 for the 4B,
```
NEW:
```
**Deep tier: measured on desktop only, never on a phone.** Qwen3.6-35B-A3B with a 512-token thinking budget, development data, best of many deep variants tried on these sets. Intervals include seed noise. V-para (two seeds): floor-adjusted **0.436** (0.387–0.486) vs 0.261 for the 4B,
```

**E10**

OLD:
```
Desktop p50 about 79 s. Never run on any phone; not in the shipped build.
```
NEW:
```
Desktop median 79 s. Not in the shipped build.
```

**E11**

OLD:
```
The pre-registered rule is a raw-ratio 95% CI above 0.50 on v0.2; we also apply it to V-para. On both sets only the deep tier with thinking meets it, on development data, on the desktop.
```
NEW:
```
Our own pre-registered rule, not the bounty's, is a raw-ratio 95% CI above 0.50 on v0.2; we also apply it to V-para. On both sets only the deep tier with thinking meets it: development data, desktop only, not shipped.
```

**E12**

OLD:
```
Our stricter target, a floor-adjusted CI low end at or above 0.50 on V-para, is met by no configuration (best 0.436).
```
NEW:
```
Our stricter target (floor-adjusted CI low end ≥ 0.50 on V-para) is met by no configuration (best 0.436).
```

**E13**

OLD:
```
The win rate is 0 everywhere. BOAR is not shown
```
NEW:
```
The win rate is 0 on both sets. BOAR is not shown
```

**E14**

OLD:
```
answers are often right but thin, or miss knowledge the packs do not hold.
```
NEW:
```
answers are often thin or partly wrong, or miss knowledge the packs do not hold.
```

**E15**

OLD:
```
Safety evidence is small (0 unsafe-rule hits on 10 danger questions).
```
NEW:
```
Safety evidence is small (0 unsafe-rule hits on 10 danger questions, one of which prompted a fix).
```

**E16**

OLD:
```
We report three scales, in this order:
```
NEW:
```
Three scales, in this order:
```

**E17**

OLD:
```
App memory (PSS) peaked at 5.88 GB during model load, then stayed at or below 4.23 GB;
```
NEW:
```
App memory peaked at 5.88 GB at model load, then stayed ≤ 4.23 GB;
```

**E18**

OLD:
```
(retrieval 60/60 identical to the measured build, desktop answers 59/60 byte-identical, 1,378/1,378 tests)
```
NEW:
```
(retrieval 60/60 and desktop answers 59/60 identical to the measured build; 1,378/1,378 tests)
```

**E19**

OLD:
```
Not in PR-1: the deep tier; the knowledge-pack retrieval improvements and pack catalogue (a second PR after 2026-10-20); "answer anyway" and "deeper answer" buttons.
```
NEW:
```
Not in PR-1: the deep tier, the knowledge-pack improvements (a second PR after 2026-10-20), and "answer anyway" / "deeper answer" buttons.
```

**E20**

OLD:
```
(v0.1 questions with reference answers, judge harness, a trace format any app can emit, scorers)
```
NEW:
```
(v0.1 questions and references, judge harness, trace format, scorers)
```

**E21**

OLD:
```
(reports, frozen criteria, closed experiments, device runs)
```
NEW:
```
(reports, frozen criteria, closed experiments)
```

**E22**

OLD:
```
Other teams are welcome to run the judge on their own traces and to contribute held-out questions written outside the Claude family, so every team gets an unexposed set.
```
NEW:
```
Other teams can run the judge on their own traces and contribute held-out questions written outside the Claude family (rules in CONTRIBUTING).
```

**E23**

OLD:
```
history pushing a comparison onto the health extractive path, 1); 0 in turns 6–15.
```
NEW:
```
history pushing a comparison onto the health extractive path, 1); none of these two kinds in turns 6–15, where one follow-up resolved "it" to the wrong coin and one answer invented a penalty figure primed by earlier turns.
```

**E24**

OLD:
```
device run still pending (needs a 12 GB phone);
```
NEW:
```
device run still pending (the 12 GB-class POCO X6 Pro has run only the 4B build);
```

**E25**

OLD:
```
(DRAFT v4.0; independently reviewed through v3.9, v4.0 pending review; see the changelogs; not published)
```
NEW:
```
(DRAFT v4.0; independently reviewed through v4.0, see CLAIM-REVIEW-v4.0.md and the changelogs; not published)
```

**E26**

OLD:
```
No Google Play Services, Firebase or tracker classes in any of the three measurement APKs (E1).
```
NEW:
```
No Google Play Services, Firebase or tracker classes in any of the three measurement APKs (E1), nor in the cut 7 no-network APK (audit 2026-10-10, QUEUE.md l.897).
```

## UNKNOWN
- Whether §0 is posted before the bounty's shared rubric exists (CLOSING-SPRINT Q8 limits numbers in the chat). If the rubric orders the scales differently, re-check the "Three scales, in this order" sentence.
- The A15 floor-adjusted ratio was never computed. It could be computed from the A15 judgments with 0 calls; E2 says "not computed".
- The PR-1 tip may move before submission (numbers cite 8b117738).
