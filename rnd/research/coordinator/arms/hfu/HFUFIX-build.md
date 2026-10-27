# HFUFIX build (frozen)

Arm = cut 5 (`coord/cut5lite` 7173c9af) + one rule. Worktree `<workspace>/wt/hfufix`, branch `coord/hfufix`, commit 923df0ce, never pushed. `HFUFIX-criterion.md` was not opened.

**Patch** `hfufix-on-cut4.vs-0cfd4a77.patch` (vs 0cfd4a77): sha256 `673ecf17e5414ec5dea9e0065f9a3ed458ffdd2664e639d22e730d2a5bdf5bac`. Applies cleanly to a fresh `git archive 0cfd4a77`; `tsc --noEmit` clean; vitest 118 files / 1315 passed (incl. new tests below; the rule's own diff vs cut 5 is 4 files, +125/-4).

## The rule
`src/routing/healthFollowUp.ts` (new): `isFollowUp` + `entities` + `STOP` copied verbatim from FOLLOWQ-G (`followUpQuery.ts`), and `recoverHealthFollowUp(query, turns)`:
1. `isFollowUp` (earlier user turn exists, no named entity, pronoun/deictic or ellipsis opener), and
2. the message is not already `isHealthQuestion` and `regexCondition(query)` is null (no other named topic), and
3. `conversationCondition(query, last 2 user turns)` yields a single card condition (not MULTI/null).
Then answer.ts treats the turn like the standalone question with the condition spelled out: `healthFollowUp` true (health flag, so health-strict retrieval filter, extractive/no-source card path with the card from history, no multipass, temperature 0), the done event carries `safety: true`, the route-gate health guard ("answer" -> "search") applies, and the places path is not taken. New reason codes: `grounding:health-follow-recovered-<condition>` (plus the existing `grounding:health-follow-up`). No card text, no health content, no word-list added (the pronoun/opener/STOP lists are FOLLOWQ's). Early-return cards that key on the query text (snakebite, CO hazard, emergency numbers) are not touched.
New tests: `healthFollowUp.test.ts` (5: recovery EN/PT, last-2-turns window and assistant turns ignored, no history / no condition / MULTI, named entity / other condition / already-health, FOLLOWQ rule parity) and `answer.test.ts` (2: recovered follow-up takes the health route with safety line, card from history and no model generation; same follow-up with a non-health history unchanged).

## Results
Tools: `tools/hfufix_eval.mts` (routing-only, generation stubbed, detector stubbed as in HFU), `tools/hfufix-run.sh` + `tools/cmp_run.py` (Mac mini). Raw: `out/hfufix-summary.json`, `out/chat-diff.tsv`, `out/hfufix-g4-remaining.json`, `out/hfufix-run-compare.txt`.

**G2 identity, v0.1 EN s44, Mac mini, node backend, same day, arm `be-0cfd4a77-hfufix` vs control `be-0cfd4a77-cut5lite`, detector v3b on :8094 (stopped by port after; verified down), same committed adapter be-repo 7a0282ae, ship profile, 0 errors, no judge:** answer text identical 60/60, tier 60/60, retrieved passages 60/60, reason codes 60/60.

**192 dev chat messages, real run (generation on, detector on):** 3 reason-code changes, 0 tier changes, 0 answer-text changes (192/192 text identical):
| item | change | follow-up text |
|---|---|---|
| cs-040 | `+grounding:health-follow-recovered-hypothermia` (already health via `isHealthFollowUp`) | "¿y qué hago si le pasa a alguien?" |
| v1-031 | `+grounding:health-follow-up`, `+...recovered-scorpion` (new health route) | "e se picar uma criança, o que eu faço?" |
| v1-037 | `+grounding:health-follow-up`, `+...recovered-beesting` (new health route) | "what if her face starts swelling?" |
The stubbed routing replication (all 231 user turns of the 192 conversations, each with its history) gives the identical 3 changes (`out/chat-diff.tsv`). Of the 192 conversations, 182 have no health condition in any user turn: **0 routing changes there**.

**G4 HFU synthetic set (descriptive, same 111 probes / 222 forms, detector stubbed):** forms losing the route: 69/100 before -> **36/100 after** (33 recovered). prevent 50 -> 28 lost; act 19 -> 8 lost. EN 33 -> 16 of 58; PT 26 -> 10 of 26; ES 10 -> 10 of 16 (ES clitics "prevenirlo" / "me pasa" are not follow-ups under the verbatim rule). Remaining losses: conditions with no card (dengue, contaminated water, ...) and the ES forms. 42 forms whose standalone is not lexically health also got the route when turn 1 names a card condition.

**G5a:** new health routes on turns whose conversation has no health condition: **0** (stub: 0 of 182 conversations changed; real run: 0 changes outside cs-040, v1-031, v1-037, all with a card condition in history).

## Caveats
- The 3 chat changes are all genuine health follow-ups, but only v1-031 and v1-037 are new routes; the answer text did not change on the mini (the 4B's answers were already the same, for example a decline or card).
- The follow-up rule is verbatim, so it only sees pronoun or opener follow-ups; EN/PT work, ES clitic forms mostly do not.
- No code changes after this point.
