# FOLLOWQ-G - cut 5 + Q1 query for rule-flagged follow-ups only (2026-10-06)

TL;DR: **NOT ADOPTED. G3 FAIL (arm wins 9 of 20 non-tie decisions = 45%, bar >= 60%); G1, G2, G4 pass.** G3 safety clause fine (0 unsafe arm replies; 1 unsafe control reply). The gate is clean (0 retrieval diffs on 171 non-flagged messages, 60/60 v0.1 identical, retrieval 0.91x control), but the extra sources it finds for follow-ups do not make answers better: of 13 changed answers the judge prefers control or ties as often as the arm. Criterion `FOLLOWQG-criterion.md` sha256 ade5c84e... verified, not edited. Dev only (chat slices v0-v2, v0.1 EN); no chat-v3, blind/, rnd/veil/.

| gate | result | bar |
|---|---|---|
| G1 build | patch applies to a fresh `git archive 0cfd4a77`, tsc clean, 118 files / 1313 tests pass (1312 before + 1 new answer test; 4 new unit tests for the rule/query in followUpQuery.test.ts) | pass |
| G2 identity | v0.1 EN s44: text + tier + passages identical **60/60** vs same-day cut 5, rule fired 0 times, 0 errors. 192 chat: **21 flagged** (same 21 as FOLLOWQ), retrieval (raw + kept) differs on **0/171** non-flagged; non-flagged answer text also identical 171/171 | 60/60, 0 diffs: PASS |
| G3 quality | 13 flagged answers changed (of 21; 13 had different kept passages). A/B Opus, both orders: see below. arm 9 / ctl 11 / ties 6 of 26 decisions -> **45%** of non-tie; unsafe: arm 0, ctl 1 | >= 60% and no new unsafe: **FAIL** |
| G4 latency | retrievalMs on the 21 flagged: ctl mean 174.8 / median 142.2 ms, arm mean 159.5 / median 130.1 ms: **0.91x** (0.92x by medians); retrieve-event time 0.91x | <= 1.3x: PASS |

## G3 A/B (judge: `claude -p` Opus, no tools, JSON verdict; prompt per the criterion plus a per-reply unsafe flag; only the 13 changed follow-up answers; `tools/ab_judge.mjs`, rows `followqg-ab.jsonl`)
| order | arm wins | control wins | ties |
|---|---|---|---|
| control = A, arm = B | 5 (cs-030, cs-032, cs-035, v1-035, v2-029) | 6 (cs-029, cs-034, cs-039, v1-033, v2-032, v2-035) | 2 (cs-036, cs-038) |
| arm = A, control = B | 4 (cs-029, cs-030, cs-035, v1-035) | 5 (cs-034, cs-038, cs-039, v1-033, v2-035) | 4 (cs-032, cs-036, v2-029, v2-032) |
| sum | **9** | **11** | 6 |

Consistent in both orders: arm better on cs-030 (dengue prevention), cs-035 (Australia population), v1-035 (Night Watch); control better on cs-034, cs-039, v1-033, v2-035 (the arm's new passages were off-topic or led to a wrong name, e.g. John Pierce for the telephone); order-dependent: cs-029, cs-032, cs-038, v2-029, v2-032; tie both: cs-036. Position bias is visible (control wins 6/5, arm 5/4 by position; 2 vs 4 ties), so the 45% carries an uncertainty of a few decisions; with 20 non-tie decisions it cannot reach 60% without 3 more arm wins.

## What was built (worktree `<workspace>/wt/followqg`, branch `coord/followqg` from `coord/cut5lite` 7173c9af, commit b8e7785e, never pushed)
- `src/routing/followUpQuery.ts`: the FOLLOWQ rule ported verbatim from `tools/mkreq.py` (same stoplist, entity rule, pronoun/opener lists); `tools/equiv.mts` checks it against the python rule on all 192 messages: 21 flagged, 0 mismatches in flag or Q1 string.
- `answer.ts`: in the "1. Sources" block only, `sq = followUpQuery(req.query, ctx.history.turns)` replaces `req.query` for the search query, PT/EN term translation, lexicon names, identifiers/acronyms, matchQuery and the on-subject filter (`ptS` = language of sq, the downstream `pt` is unchanged). Reason code `retrieve:followup-query` marks a fired item. Deviation from the FOLLOWQ diagnostic: there Q1 replaced the query for the whole pipeline (health, gate, instant); here the gate, health/safety detection, small-talk and the prompt keep the user's own message, which is the safer reading. A flagged follow-up with a changed query has no instant snippet (matchQuery differs from the message).
- Patch: `followqg-on-cut4.vs-0cfd4a77.patch` (git diff 0cfd4a77..HEAD, includes cut 5 lite + speed), **sha256 544b1b8f7b77009cf69166163e7bc3d4d5da912bbe9e24b27647454658294687**. Increment over cut 5: 4 files, +124/-12.

## Run
Mac mini, trees `be-0cfd4a77-cut5lite` (control, patch 3b7a0dfa...) and `be-0cfd4a77-followqg` (arm), same committed adapter `be-repo` (sha 7a0282ae...), `BOAR_RUNNER_PROFILE=ship`, detector v3b on :8094 (started and stopped by the run, port verified down), node backend, seed 44, heavy lock, same day, order ctl v0.1, arm v0.1, ctl chat, arm chat; kit boar-crypto + boar-wikivoyage-en; 0 errors in all four runs; disk 37 -> 36 GiB. Chat requests = CHATGATE's (192, history via item.history). No Docker touched.
Files: `tools/followqg-run.sh`, `tools/analyze_g.py` (output `followqg-analysis.txt`), `tools/ab_judge.mjs`, `tools/equiv.mts`, `followqg-ab.jsonl`. Traces: `boar-eval/runs/kiln/followqg/` (not committed).

## Notes
- The criterion's adopt rule is applied as written (sum over both orders of non-tie decisions). The 13 are a small sample; nothing here argues for retuning the rule post hoc.
- Side effect to know: Q1 sometimes removes off-topic Q0 passages (cs-038, v1-033, v1-035) which is neutral to good; the failures are where the previous turn pulls in a different off-topic article.
