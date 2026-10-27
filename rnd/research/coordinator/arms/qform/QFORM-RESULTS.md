# QFORM results (2026-10-21, 0 LLM: replay only; dev, agent-written items)

**TL;DR.** On the A-union (merged file), K1 tree, phone retrieval config, the form of the question moves "gold chunk kept" far more than the pack does: F5 (statement with the answer term in it) 83 %, F2 keywords 62 %, F0 base 50 %, F6 50 %, F4 typos 42 %, F7 42 %, F3 situational 25 %, F1 entity-free 10 %, F8 bare follow-up 8 %. Named holes: **F1, F3, F8**. The engine does not rewrite the query (search query = the user text on 431/432), and the grounding step, not the k cut, is where the right chunk is lost after retrieval.

## Matrix (hit@kept %, n 48 per form; per pack n 8; full tables in aggregates/matrix.md)
| form | hit@raw | hit@wide12 | hit@kept [Wilson 95]| article@kept | drop F0-Fi, kept [CI] |
|---|---|---|---|---|---|
| F0 base | 54 | 60 | 50 [36-64] | 65 | - |
| F1 entity-free | 27 | 33 | 10 [5-22] | 15 | +40 [+23,+54] HOLE |
| F2 keywords | 65 | 69 | 62 [48-75] | 73 | -12 [-27,0] |
| F3 situational | 31 | 33 | 25 [15-39] | 44 | +25 [+8,+42] HOLE |
| F4 typos | 44 | 46 | 42 [29-56] | 52 | +8 [-6,+23] |
| F5 yes/no true | 83 | 85 | 83 [70-91] | 92 | -33 [-48,-19] |
| F6 false premise | 65 | 71 | 50 [36-64] | 62 | 0 [-15,+15] |
| F7 comparison | 44 | 54 | 42 [29-56] | 52 | +8 [-6,+23] |
| F8 follow-up | 12 | 19 | 8 [3-20] | 8 | +42 [+27,+56] HOLE |

By pack, F0 hit@kept: wikivoyage 100, crypto 75, medlineplus 50, visa 50, factbook 12, firstaid 12 (self-test packs 25 % pooled vs authored 75 %). F1 is 0-12 % in every pack. F8 is 0-25 % in every pack. Per-pack CIs (n 8) are wide; per-pack "holes" in aggregates/matrix.md are indicative only.

## Reads
- **Holes (frozen rule: drop >= 20 points, CI excludes 0):** F1 (-40), F3 (-25), F8 (-42) pooled. F4 is not a hole pooled (-8, CI -6..+23; wikivoyage alone -50). F1 = dense/lexical limit, goes to the pack card: without the entity name the right article is in raw for 38 % and kept for 15 %. F8: the engine gets the bare fragment as the query (no history in this design), so it is by construction an underspecified-query read, an engine note for history-aware rewriting. F3 (long first-person) is addressable by a rewrite: 9 of 48 return an empty retrieval and 19 an empty kept list.
- **No rewrite:** the engine's search query equals the user question on 431/432 items (one compare item became "bleeding"). The PT->EN/canonical-term rewrite never fires for English; typos, keywords and long queries reach FTS and the embedder unchanged.
- **Keep step vs raw:** cut-by-k is small (gold in wide12 but not in raw: 1-5 of 48 per form). The loss is after retrieval: 25 items have the gold in raw and not in kept (F1 8, F6 7, F3 3, F0 2, F8 2); codes `grounding:off-topic-dropped` 22, `grounding:no-good-source` 13, health-strict/off-health 4 (aggregates/keep_loss.json). Kept lists are empty for 23/48 F1 and 19/48 F3 items.
- **Right article, wrong chunk:** article@raw exceeds hit@raw by 13 points at F0 (67 vs 54) and 21 at F3 (52 vs 31): the retrieved article is often right but the chunk holding the fact is not the one returned (e.g. Chacahua F4 kept three chunks of the right page, none with the rainy season).
- **K1 settings (head pass a2 + dense append, secondary run):** F1 10 -> 21, F6 50 -> 60, F0 50 -> 54, F3 25 -> 27, F8 unchanged 8. The head pass helps entity-free and false-premise forms, not follow-ups. Holes unchanged (F1, F3, F8).

## Prediction (QFORM.md) vs what happened
| predicted | observed |
|---|---|
| F0 70-85 % | **50 %** (wrong; self-test packs factbook/firstaid 12 %: the multi-part self-test questions retrieve the article's lead chunk or another pack's page, not the deep chunk of the primary fact; authored packs 75 %) |
| F2, F4 lose 15-30 | F2 **gains** 12 (keywords match the lead/title chunk); F4 loses 8 (not significant) |
| F1 loses 25-40 | -40, top of the range; confirmed |
| F8 worst, < 0.4 | 8 %, confirmed (worst) |
| F5/F6 ~ F0 | F6 = F0 (0); F5 **+33** above F0 (the answer terms are in the query) |
| F7 -10 | -8, not significant |

## Caveats
Agent-written questions and gold (24 from the agent-written self-tests, 24 authored from pack text), dev only, never claim items. One fact per article, one primary chunk per fact as gold (other chunks of the same article may also answer; see article@kept). F0 for self-tests is the multi-part self-test question while Fi target one fact, so the F0 baseline is a lower bound for self-test packs (hit@kept on any of the self-test's facts: 56 % vs 50 %). Per-pack n 8. One deterministic replay; stock settings are the phone's config, lexical emergency detector instead of mmBERT (health grounding may differ), gate stubbed to SEARCH. Only the first retrieve call per item is reported. Quote matching also credits duplicate copies of the text in other documents.

Files: items/{qform.jsonl,qform.questions.jsonl,facts.json,draw.json}, replay/{RUN.md,qform.replay.jsonl,qform.replay.k1settings.jsonl}, aggregates/{matrix.json,matrix.md,matrix.k1settings.*,keep_loss.json}, tools/.

## W74 (web tick 39): the follow-up hole closes when the search query carries the previous turn (0 LLM, coordinator, 22:5x)
TREC CAsT practice: build the search query from the conversation history, not the fragment alone. Replay of the 48 F8 fragments with (a) the previous turn (= the fact's F0 question) prepended, (b) the F0 run's kept titles prepended; same tree, merged A-union pack, gate search; files replay/w74/. Scorer = the coordinator's quote-in-kept check (counts differ by 1–3 from matrix.py's, same direction).
| query | gold in raw | in wide-12 | in kept | kept where F0 was kept |
|---|---|---|---|---|
| F8 fragment alone | 6/48 | 9/48 | 4/48 | — |
| F0 base (reference) | 26/48 | 29/48 | 21/48 | 21/21 |
| **prev turn + F8** | **27/48** | **29/48** | **24/48** | **21/21** |
| F0 kept titles + F8 | 24/48 | 25/48 | 20/48 | 16/21 |
Reading: concatenating the previous user turn restores the follow-up to the base level (every item the base found is found again) with no model call; titles alone recover most of it. Engine note (our engine and the app maintainer's Retriever.kt): for a short second turn, search with previous turn + current text. The hole was the query, not the packs.

## Secondary: answers with the reference (2026-10-21 23:0x; Qwen3-1.7B, K1 tree, A-union merged kit, dev, agent-written items)
**TL;DR.** When the gold chunk is kept the 1.7B answers at reference level (U 0.88, corr 4.09, n 43); when it is not, U 0.19 (corr 1.94, n 147). The form moves the answer almost only through whether the gold is kept: where the gold is missing in both forms F1 and F3 answer as well as F0 (dU +0.07 and -0.03, CIs span 0); F8 is worse even then (dU +0.28, the fragment gives the model nothing to recall).
Setup: 192 items (F0/F1/F3/F8 x 48), tools gen/tools/{mkreq_qform.py,run_qform_gen.sh,sanity_qform.py}, 2 mini jobs, seed 42, stock retrieval settings (quickFirst only, as the primary replay; kit = merged file as one entry, sha 7e86674b). Judge: judge.mjs judge.v1, Haiku 5.5-low, N 4 shards, both orders, reference = item `answer`, rubric = item `rubric` (judge/bench/qform192). 384 Haiku calls (ledger gen/CALLS.md), 0 retries, Opus 0, paid 0, phone 0. Tables: aggregates/answers.md; CIs = item bootstrap B 2000 seed 11.
Sanity: 192/192 rows, 0 empty, 0 errors, 0 loops. **Kept-list identity vs the replay: 180/192 = 93.8 % (below the 95 % bar); raw lists 188/192, task 191/192.** Cause of the 12 (gen/sanity.json): the real engine differs from the replay in three ways, not in retrieval: (1) the mmBERT emergency detector fires on 7 first-aid items the lexical detector let through and `grounding:health-strict` drops every off-health source (kept = empty), plus firstaid-04-F0 (hypothermia card answer, no sources shown); (2) the 1.7B context budget/grounding keeps fewer chunks (medlineplus-04-F1, -07-F0: same titles, shorter list; visa-02-F1: empty), (3) the real gate routed wikivoyage-06-F1 to translate where the replay forced SEARCH. Gold-kept for the splits = the replay flag where the lists match, No where the run's kept list is empty (10 items), and the 2 unknown items are left out of the splits.
| form | corr | use | U [CI] | gold kept | confident err (corr<=1.5) | warned | declined | out tok | total ms |
|---|---|---|---|---|---|---|---|---|---|
| F0 base | 3.23 | 2.55 | 0.622 [0.51,0.74] | 22 | 10 | 11 | 0 | 33 | 3219 |
| F1 entity-free | 2.14 | 1.59 | 0.230 [0.14,0.33] | 5 | 25 | 20 | 0 | 29 | 2639 |
| F3 situational | 2.66 | 2.05 | 0.401 [0.30,0.52] | 12 | 14 | 12 | 0 | 31 | 2951 |
| F8 follow-up | 1.73 | 1.33 | 0.133 [0.07,0.20] | 4 | 28 | 10 | 0 | 34 | 3104 |
Gold kept x form (U; n): F0 yes 0.904 (22) / no 0.352 (25); F1 yes 1.065 (5) / no 0.133 (42); F3 yes 0.783 (12) / no 0.284 (36); F8 yes 0.753 (4) / no 0.079 (44); all forms yes 0.876 (43) / no 0.185 (147). Confident errors with the gold kept: 2 of 43; without: 75 of 147. 9 F0, 6 F1, 13 F3, 4 F8 answers are instant extractive (0 tokens).
Paired F0 - Fi on the same fact (dU [CI]): gold kept in BOTH: F1 -0.163 (n 2), F3 +0.000 [-0.26,+0.28] (n 7), F8 +0.023 [-0.01,+0.09] (n 3). Kept in NEITHER (the memory question): F1 +0.074 [-0.05,+0.20] (n 22), F3 -0.026 [-0.22,+0.16] (n 20), F8 +0.283 [+0.16,+0.43] (n 24). F0 kept but Fi not: F1 +0.873 (n 19), F3 +0.737 (n 15), F8 +0.835 (n 19), i.e. the whole form effect (all pairs: F1 +0.392, F3 +0.221, F8 +0.489) is the retrieval hole.
Per pack (all forms, U / corr, n 32, indicative): factbook 0.32/2.14, firstaid 0.35/2.84, medlineplus 0.33/2.56, crypto 0.35/2.47, wikivoyage 0.39/2.50, visa 0.27/2.11. The authored packs fall hardest from F0 to F1 (crypto 0.75 -> 0.13, wikivoyage 0.97 -> 0.16, visa 0.59 -> 0.03); the self-test packs start low at F0 (the multi-part self-test question vs a single-fact gold) and move less.
Frozen prediction (gold kept, F0 vs F1 within +-0.05): **not testable as stated**: only 5 F1 items keep the gold (U 1.065 vs F0 0.904 on its 22 kept; paired n 2); the direction is "no loss", the size is unmeasured. The reading gap on kept gold is small (U 0.88 overall); F3 with gold kept (0.78) sits below F0 (0.90) at n 12, within noise.
Reads: (a) when the reference is in hand the form hardly changes the answer, so the lever for F1/F3/F8 is retrieval (a rewrite or history for F8, entity recovery for F1), not the reader; (b) without the gold, F1 and F3 are as bad as the base question (the 1.7B has no memory of these facts, 25/42 F1 confident errors), F8 is worse; (c) the weak-sources warning fires on 53 of 192 answers (20 of 48 F1), so the user is told in most failing cases, but 75 gold-less answers are still confidently wrong (corr <= 1.5).
Caveats: judge Haiku 5.5-low (Claude family, compresses gaps); gold-kept uses the primary replay flag (title+body quote match, only the primary chunk), so an answer can be right with the gold chunk "not kept" if another chunk carries the fact; 12 items had a different kept list than the replay; n 43 vs 147 and 2 to 24 per pair; one seed.
Files: gen/{req,traces,logs,CALLS.md,sanity.json,tools/}, judge/{bench/qform192,qform-F{01,3,8}.judgments.jsonl,agg_answers.py}, aggregates/answers.{json,md}.

### W74 correction (23:0x): the app maintainer's app already carries the previous question; our bench tree does not
`wt/native-qa/android-native/.../answer/FollowUp.kt` (port of upstream `src/routing/followUp.ts`, absent from our cut7 bench tree and from our boar-app clone): a question that points back (he/it/its/those/there…) is searched together with the previous question (then the previous alone if that finds nothing); a short question (≤ 3 content words, no name of its own) is searched as written and borrows the previous question only when it finds nothing. Simulation of that plan on the 48 F8 fragments with the existing replays (0 LLM): 39 point back → combined query, 20 gold-in-kept; 1 short → fallback, 0; 8 neither (≥ 4 content words, no pronoun, e.g. "and how many breaths do I give?") → searched alone, 0. **Total 20/48** vs 24/48 for the unconditional "previous + fragment" and 21/48 for the base question. Reading: the F8 hole of the matrix is a bench-engine artefact (no follow-up rule in cut7) and overstates the app's; in the app the residual is the 8/48 fragments with no pronoun and ≥ 4 content words, worth at most +4/48 by always combining when the fragment opens with "and"/"then" or by raising SHORT_FOLLOW_UP_TERMS. Not a note to send on its own.
