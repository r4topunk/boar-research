# QMERGE step 0: merging the engine query's and the 4B rewrite's retrieval before the keep step keeps the fact chunk on 42/180 vs 36 (+6, gate +10): FAIL, the QWRITE reopen closes (2026-10-16 14:3x; 0 judge, 0 paid)

**Verdict: step 0 FAIL on G1 only.** G0 identity, G2 (article kept 59 -> 67), G3 (0 displaced) and G4 (v0.1 gold-kept 8 -> 9) pass. The merge adds the fact chunk to the candidate list on 11 items and the keep step admits 6 of them. Nothing is lost, but +6 is short of +10. The judged stage (random20, Haiku 40) does not run.

## Frozen inputs
- Criterion QMERGE-criterion.md sha 78dfbd59... (Ruleset 30), frozen 14:18 before any patch run, generation or replay.
- Tree kiln-local/be-cut7-qmerge = wt/pr1 8ac9eb7a (git archive) + tools/qmerge.patch sha e38cabc1... (answer.ts only, +38 lines; applies cleanly to wt/pr1, which stays untouched). ARM pr1+qmerge. tsc: 0 errors in the patched files (the only 3 errors are the archive's missing app.json). vitest src/routing/answer.test.ts 173/173.
- deps.queryMerge = { rewrite(question) }. With a rewrite that differs from searchQuery, the engine runs retrieve(rw, same k), appends the new chunk ids after its own list, then applies dedupeArticleCopies. The keep step is unchanged: compressContext against the engine's matchQuery, same budget, then grounding / health-strict. Codes qmerge:candidates:<n> and qmerge:kept-from-rewrite:<m>. With the dep absent the code path is untouched.
- Rewrites: the 180 come from qwrite/runs/qmap.json (177; 3 fallbacks skip the merge). v0.1 has 60 new ones from the same writer (tools/gen_v01.py, run_gen_v01.sh; 36 s wall, p50 0.59 s, 6 words). 1 failed the gate (vit-sci-003, over 12 words); the kill line was 6.
- Replay tools/replay-qm.ts = replay-qw.ts + deps.queryMerge in mode qm + the adapter's mmbert detector client on :8094 (untouched, 720 calls) + healthgap true. Modes off,qm,off, --gate search --k 6 --pool 8. Wall 2 min 36 s.

## Gate (aggregates/compare.json)
| gate | OFF | QM | rule | result |
|---|---|---|---|---|
| G0 off = off2 (180 / v0.1 60); skipped items = OFF | 180/180, 60/60 | 4/4, 14/14 | all identical | PASS |
| G1 fact chunk kept | 36 (tk2off ref 35) | **42** | >= 46 | **FAIL** |
| G2 fact article kept | 59 | 67 | >= 59 | PASS |
| G3 displaced fact chunks | - | 0 | <= 3 | PASS |
| G4 v0.1 gold-kept items | 8 | 9 | >= 8, lost <= 1 | PASS (lost lan-exp-004; gained vit-trv-003, lan-exp-003) |

- Gained kept (6): bitcoin-019, health-se-015, medlineplus-012, factbook-010, simplewiki-002, simplewiki-016. Article gained (8), lost 0.
- Per pack kept OFF -> QM: travel 1->1, ethereum 2->2, bitcoin 1->2, health-se 1->2, outdoors 6->6, firstaid 1->1, medlineplus 10->11, factbook 3->4, simplewiki 11->13. SE 11 -> 13, topic 25 -> 29.
- Cost of the merge: it ran on 176/180 items. Candidates went from p50 4 to 6. Kept slots rose 272 -> 379 (+39 %) and kept tokens 30.0k -> 40.3k (+34 %). Empty kept fell 47 -> 39. Rewrite-only chunks were kept on 71 items (110 slots), mostly non-fact.
- v0.1 (claim kit): merged on 46/60. Kept list changed on 15/60 and the prompt on 18/60. Kept slots 78 -> 93.

## Reading
- Reach is capped by k, not by the keep step. The engine retrieves k = 4 on 161/180 items (3 on 18). So the rewrite's list is 4 chunks, not the raw6 + pool8 behind the QWRITE union bound of 87. In the merged candidates the fact appears on 66 items vs 55 in raw (+11). The keep step admits 6 of those 11 and displaces none.
- Most of what the merge adds is distractor text (+34 % kept tokens for +6 fact items). On the HEADPASS conversion (about +0.12 per newly-present item, Opus) that projects to roughly +0.004 pooled. That is below anything a judge pass can resolve.
- Reopen (per criterion): a different merge rule, e.g. a larger k for the rewrite list or RRF interleave, only with a new criterion. Low prior given +11 at k = 4. HEADPASS X2b already puts the fact chunk in 102/180 contexts by the append path.

## Files
QMERGE-criterion.md + .sha256; tools/{qmerge.patch + .sha256, replay-qm.ts, replay-qm.sh, run_replay.sh, compare_qm.py, gen_v01.py, run_gen_v01.sh}; runs/{st-*.qm.jsonl, v01.qm.jsonl, v01-qw-raw.jsonl, v01-qmap.json, v01-server.log, changed.jsonl}; aggregates/compare.json.
Cost: 0 judge, 0 paid, about 4 min of compute. The writer server was stopped and :8094 was never restarted. Nothing was read from blind/ or rnd/veil/.
