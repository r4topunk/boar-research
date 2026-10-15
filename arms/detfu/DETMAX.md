# DETMAX build and scoring

> Health and first-aid content here is AI-reviewed, not clinically reviewed; nothing in this file is medical advice.

Criterion `DETMAX-criterion.md` sha256 `a7c784af...2328` (verified, unedited). Arm = cut 5 + one rule. Worktree `$BOAR_WS/wt/detmax`, branch `coord/detmax` from `coord/cut5lite`, commit 5e5567ca, never pushed.
**Patch** `detmax-on-cut4.vs-0cfd4a77.patch` sha256 `3f355999fca1e1127772698109b41894134eccbc5c4a6127a563f936d70730d8` (4 files vs cut 5: answer.ts +8, answer.test.ts +4 tests).

## TL;DR: ADOPT. All five gates pass.
| gate | result | verdict |
|---|---|---|
| G1 build | applies to a fresh `git archive 0cfd4a77`; `tsc --noEmit` clean; vitest 117 files, 1312/1312 passed (4 new tests) | pass |
| G2 v0.1 EN s44 (Mac mini, same day, vs cut 5) | text 60/60, tier 60/60, passages 60/60, reason codes (excl route-gate) 60/60; 0 errors | pass |
| G3 S3 + held-out prefixes (60 probes each, 240 forms) | arm mismatches 0/60 on each of the 4 prefixes; control (cut 5) had 1 / 3 / 0 / 3 (7 total) | pass |
| G4 false fire, 192 dev chat messages | routes added by the arm: **1** (<= 2), fires standalone: yes | pass |
| G5 cost | extra detector calls only on turns with history: 39 of 231 user turns (1 extra call each); desktop detector 52.8 ms mean per call | reported |

## The rule
answer.ts, where `deps.emergencyScore(query, userTurns)` is called: if that returned a score and the conversation has earlier user turns, also call `emergencyScore(query, [])` (the current turn alone), and use `p = max(p_window, p_alone)`, `fire = fire_window || fire_alone`; a failing second call keeps the window's verdict. Same threshold (0.2), same model, no lexical-list change; no history means no extra call (single-turn behaviour unchanged). Tests: two calls with history and fire from the turn alone, one call without history, max / either-fire / failing second call, nothing added when neither fires.

## G3 detail
Baseline = the 60 DETFU EN probes whose standalone form routes emergency/danger with the real detector (same set and route definition as DETFU; `ed-en-073` excluded). Turn 1 = prefix, turn 2 = probe; mismatch = route class differs from the standalone form.
| prefix | control mismatches | arm mismatches |
|---|---|---|
| "Hi, quick question." (DETFU S3) | 1 (ed-en-049) | 0 |
| "Thanks for the help earlier." | 3 | 0 |
| "Different topic now." | 0 | 0 |
| "Ok so I have another question." | 3 | 0 |
Real detector: mmbert-small v3b on the Mac mini :8094 through an ssh tunnel (calls as in the adapter's `emergencyScore`), stopped by port and verified down on both hosts.

## G4 detail (192 dev chat messages: all 231 user turns of the 192 conversations scored with their history, real detector; and the real arm-vs-control run on the mini)
Reason-code changes: 5 messages (cs-032, cs-039: detector p 0.000 -> 0.008/0.001, no route change; cs-040, v1-031: p 0.93 -> 1.00, already fired). **Added emergency/health route: 1.**
| id | turn | change | standalone |
|---|---|---|---|
| v2-031 | "andei na água da enchente ontem, o que eu faço?" after "o que é leptospirose?" | window p 0.006 -> 0.552: adds `detector:fire`, `health:detector-fire`, `grounding:health-strict`, `grounding:health-extractive`; tier fast -> instant (answer text changes from an off-topic flood excerpt with uncited warning to the health-extractive path) | alone: fires (p 0.552), routes health (verified) |
Everything else on the mini run: 0 tier changes, 0 text changes besides v2-031.

## G5
Chat: control 231 detector calls, arm 270 (+39 = turns with history). Mean desktop (llama-server, CPU, tunnel included) 52.8 ms per call over all calls; the extra call is the current turn alone (shorter text than the window). No device timing.

## Notes
Dev only. The one added route is a real emergency-style turn that the diluted window missed. Raw: `out/detmax-result.json`, `out/detmax-run-compare.txt`; tools: `tools/detmax.mts`, `tools/detmax-run.sh`.
