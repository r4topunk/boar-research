# H1 HP-SLATE (stage 1b, 0 LLM / 0 judge / 0 Opus / 0 paid / 0 phone, MacBook) - verdict: NO

TL;DR: implemented as specified. Switch-off is byte-identical (kept lists 97/97 and 432/432 vs B1/B0.main; 20/20 vs B0). With RS_HP_SLATE=1: MAIN recovery 5/25 and losses 1/22 pass the numbers, but QFORM is **+2.3 pts (CI +0.9..+3.7), below B1's +3.9** (the X1 gate removes 7 of B1's 17 gains), and junk-kept is **1.49x B0 (limit 1.25x)**. The 5/25 recovery is a FACTPRESENT-rule count: by content only lan-rsn-005 is a partial recovery (Nile longest, Amazon second, no "why disputed"); the other four are lexical false positives. Frozen rule (RETRIEVE-SWEEP-criterion sha 94ddb631): not a CANDIDATE.

## Patch
- Clone: kiln-local/rs-H1 (cp -c -R of be-0cfd4a77-cut7-litepacks; base untouched). Patch: patches/H1-HP-SLATE-dense-first-on-subject-gated-article-deduped-head-pass-append.patch, sha256 c3a43d90226f3c3536e8a5760c4762c73edc82c52ecb1f981b2aa64c09bbc41c (files in the clone: answer.ts 1e46816c2af0, denseCandidates.ts 15aab60593a3, denseCandidates.test.ts 735562559057). Only those three files change; retrieve.ts did not need a carrier (retrieve() already attaches the dense candidates to the empty array it returns).
- Switch: `RS_HP_SLATE` (Number > 0; unset or '' = off), `RS_HP_SLATE_D` (default 3, still capped by HEADPASS_MAX_APPEND = 4), read as `(globalThis as any).process?.env`.
- answer.ts HEADPASS block, when on:
  1. X1 gate: the head article = raw (substantive) chunks with the same docId as `head.first`; if grounding ran with onSubject (guarded, not health) and every one of them fails `onSubject`, all X1 neighbours are dropped; also any X1 chunk with score 0 that shares no `tokenizeTerms` token (question or search query) with title+body. Reason `rs:hp:x1-offsubject-skip:<chunkId>`. Implementation choice: onSubject is pure, so the article's rejection is re-evaluated on all its raw chunks (including ones compression never passed to grounding). Health keeps its own filter (the onSubject test is not applied there).
  2. Order: `applyAppendBudget([...pendDense, ...pendX1], chars, 4*600, skipOver=true)`; `rs:hp:dense-first:<chunkId>` for each pending dense pick.
  3. `pickDenseAppend(..., d = RS_HP_SLATE_D, cap, maxPerArticle = 1)`: cosine order, skips a candidate whose article (docId) is already in present (kept + X1) or in the picks.
  4. Raw-empty gate: the block also runs when retrievedRaw is empty but `denseCandidatesOf(retrievedRaw)` has candidates (`rs:hp:rawempty-dense`); the head-pass (X1) part is skipped in that case.
- denseCandidates.ts: optional `maxPerArticle` on pickDenseAppend, optional `skipOver` on applyAppendBudget (defaults = old behaviour).
- Tests (denseCandidates.test.ts, 3 new): dedup (two same-article candidates -> one + next article, present article, cap), skipOver, default-arg identity. `vitest run`: 11 failed files / 2 failed tests / 1217 passed, identical failing set to a clone of the base tree (1214 passed there; the failures are the stripped tree: scripts/*.mjs and plugins/*.js missing, networkAudit); `tsc --noEmit`: 697 errors, identical to the base clone modulo line numbers (no @types/node, react-native, ...). The tree has no node_modules/.bin, so the runs used boar-app's vitest/tsc with symlinks in rs-H1/node_modules (not part of the patch).

## Commands
```
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep
tools/replay.sh $K/rs-H1 replay/proof20.questions.jsonl replay/H1.off20.jsonl qform ; python3 -I tools/proofdiff.py ../qform/replay/qform.replay.jsonl replay/H1.off20.jsonl
tools/run_h1.sh      # H1.off.qform (K1 settings), H1.off.main, H1.qform (RS_HP_SLATE=1, K1 settings), H1.main (RS_HP_SLATE=1)
python3 -I tools/sweep_h1.py   # = sweep.py restricted to B0/B1/H1 -> aggregates/sweep-H1.{json,md}
```
K1 settings on QFORM: `--forward-opts --settings-json {"packHeadPass":"a2","packDense2":"append-budget"}`; MAIN as RUN.md (K1 kit, the same settings). Two MAIN runs hit `database is locked` inside run_h1.sh (the replay-cache app dir d010726f is shared with other agents' replays); both were rerun by hand with the same command.

## Switch-off identity
H1.off20 vs B0: raw/wide/kept/codes 20/20 each. H1.off.qform vs B1w.qform (and vs the QFORM K1 replay): 432/432 raw, wide, kept, codes. H1.off.main vs B0.main: 97/97.

## Result row (aggregates/sweep-H1.md)
| arm | hit@kept | delta vs B0 pts [CI item] | gained/lost | QFORM dropped-25 kept | recovery /25 | losses /22 | junk-kept (B0 x) | mean kept | kept tok | wall ms/q |
|---|---|---|---|---|---|---|---|---|---|---|
| B1 K1 settings | 45.4 (196) | +3.9 [+2.1, +5.8] | 17/0 | 7/25 | - | - | 3.02 (1.97) | 3.25 | 438 | 92 |
| **H1 HP-SLATE** | 43.8 (189) | **+2.3 [+0.9, +3.7]** (fact-cluster [+0.9, +3.9]) | 10/0 | 0/25 | **5** | **1** | **2.29 (1.49)** | 2.76 | 358 | 622 (see caveat) |

Per form (H1 / B1 / B0): F0 54/54/50, F1 12/21/10, F2 62/62/62, F3 27/27/25, F4 46/46/42, F5 83/83/83, F6 54/60/50, F7 46/46/42, F8 8/8/8. Rule clauses: QFORM delta >= +8 FAIL; recovery >= 5 pass (5, lexical); losses <= 2 pass (1); junk <= 1.25x FAIL (1.49x). MAIN mean kept 2.77 -> 3.44; ctx tokens after compression unchanged (276); kept tokens 358 (B1 438: fewer X1 neighbours).
Wall caveat: machine load average was 100-155 from other agents' replays during the runs; H1 622 ms/q vs H1.off 870 ms/q in a different window is not a comparison. The extra work is a few string operations on the already-fetched lists plus one extra onSubject pass over the head article; no embedding call was added (B1 clean-machine wall: 92 ms/q).

## What it did on QFORM (432)
- The merged A-union pack has no chunk_vecs: dense append and raw-empty paths never run (`headpass:dense:nosidecar` 408/430), so on QFORM H1 = B1 + the X1 gate alone. The gate fired 217 times on 122 items and removed 7 of B1's 17 golds, all through rule 1 (article all off-subject; each has `grounding:no-good-source` or off-topic-dropped, and the gold sits in the neighbour chunk): factbook-05-F1 (Mauritius), medlineplus-07-F1 (VLDL), crypto-01-F6 (Pass), wikivoyage-02-F6 (Ogliastra), wikivoyage-04-F1 and -F6 (Gouda), visa-07-F1 (Palestine). The second rule (no question token) explained none of them. So the predicted risk materialised: the on-subject test is wrong exactly on the paraphrased forms (F1, F6) where the right article is named by none of the question words.
- Junk-kept fell from 1.97x to 1.49x, still over the bar.

## What it did on MAIN 97 (K1 kit; simplewiki has a sidecar, so dense runs)
The gate fired 39 times, dense-first 216, `rawempty-dense` on 18 items.
Recovered by the FACTPRESENT rule (5): lan-rsn-005, lan-cmp-004, vit-hum-003, vit-sci-001, st-qa-money-se-012. Lost (1): lan-rsn-004.
- lan-rsn-005 (longest rivers): X1 neighbours of Gilgit-Baltistan dropped; dense picks Amazon River + River; River states Nile longest, Amazon second. Only a partial content recovery (nothing on why the ranking is disputed; the third rubric group is absent, 2/3 groups passes the rule).
- lan-cmp-004 (moose vs bison): Siberian tiger X1 dropped, dense picks Moose, American bison, Bison. Counted present because the rubric regex matches "bison"; no weight figure in any kept chunk (kg/pound/weigh absent), so not recovered by content.
- vit-hum-003 (Mozi), vit-sci-001 (far-UVC), st-qa-money-se-012 (UK tax threshold): all three are raw-empty items. The dense list gave off-topic picks (Altruism / Self-censorship / Social rejection; Ultraviolet / Ozone depletion / Photosensitivity; Child benefits / PIP / Tax rate). The rule counted them on generic terms ("benefit", "skin"); no Mozi, 222 nm or marginal-rate text is present. These are false positives, as st-qa-money-se-012 was expected to be; the other two are the same kind. Content-verified recovery is therefore about 0-1 of 25.
- lan-cmp-002 (Kodiak): picks Polar bear, Grizzly bear, Bear; Kodiak not picked, still absent. lan-cmp-005 (crocodiles): dense picks Crocodile, Morelet's crocodile, Freshwater crocodile; fact still absent (nothing recovered; the head-pass neighbour came back through the budget).
- lan-rsn-004 (lost): the head article Human overpopulation failed onSubject, so its X1 neighbours (which held the fact in B1) were dropped, and the dense picks were 20th century / 20th century BC / 1900s.

## Reading
1. Rule 1 (on-subject gate on X1) trades real gold for junk: -7 QFORM golds and -1 MAIN loss for a drop of 0.5x in junk. The gate needs a better article-relevance signal than onSubject (e.g. dense similarity of the head chunk).
2. Dense-first with D = 3 and dedup is what moves MAIN recovery by the lexical rule, but the picks added where raw is empty are off-topic by construction (raw empty means nothing matched the words; the dense list then returns the nearest cosine-0.7 articles). The raw-empty path should not be shipped without a topical gate; it is where all three false recoveries came from.
3. Nothing in H1 reaches the bar, and nothing here changes the answer-screen status: no Haiku screen is warranted (not a CANDIDATE).
Files: replay/H1.{off20,off.qform,off.main,qform,main}.jsonl, replay/run_h1.log, tools/run_h1.sh (e458cfdc), tools/sweep_h1.py (6c96ff20), aggregates/sweep-H1.{json,md}.
