# FOLLOWUP: follow-up query expansion — STOPPED at the 0-call reach gate (2026-10-16 10:3x; 0 generation, 0 judge, 0 paid; public sets; MacBook replay)

TL;DR: **G3 FAIL. The gold chunk is in kept context on 1/20 turn-2s with OFF and 3/20 with ON (needs ≥ OFF + 6 = 7).** No pair loses its gold chunk, and identity holds everywhere else (OFF = wt/pr1 80/80; turn-1 + v0.1 ON = OFF 80/80, 0 fires). The expansion does find the **article**: 2/20 → 10/20 kept. But it then keeps the chunk turn 1 was about (t1 fact chunk kept 0 → 4), not the neighbour that answers the follow-up. Under the frozen rule the arm stops here: no generation and no Haiku, so the judged stage was never run.

Criterion `FOLLOWUP-criterion.md` sha256 a97b22d30af7e39d252ce852e9b63120de01b6aeb815d72f3be1271e814dd89b (Ruleset 30, frozen 10:1x before any run; hash = file through `<!-- END FROZEN -->`).
Patch `tools/followup.patch` ad3a59b9… (vs wt/pr1 8ac9eb7a src: rag/pure.ts optional `ConversationTurn.sources`, routing/answer.ts, new routing/followup.ts + followup.test.ts; deps.followupContext, codes followup:expanded / followup:title-boost-N). tsc clean; src/routing vitest 709/709 + followup 4/4 on a scratch copy of wt/pr1. Eval switch `tools/followup-adapter.eval.patch` 71b6b933… (FOLLOWUP=1; trace.ts passes the assistant `sources`). Shas are in `tools/followup.patch.sha256`. Tree kiln-local/be-cut7-followup (ARM pr1+followup, 18 MB).
Pairs `pairs.jsonl` 5f687e26… / `gold.json` e81d771e…: 20 pairs from the 180 self-tests (seed 999 draw, 2 per pack plus 1 extra each for factbook and ethereum; 1 skip logged). Turn 2 is an agent-written follow-up of ≤ 8 words whose answer sits in a neighbour (non-fact) chunk of turn 1's article. Pairs and gold were written before any retrieval ran.

## Step 0 (tools/replay-fu.sh, --gate search, k 6, lexical detector; kit = claim kit + own pack; history = [t1 question, placeholder + t1 OFF kept titles])
| cell (20 turn-2s) | gold chunk kept | gold chunk raw top-6 | gold article kept | t1 fact chunk kept | empty kept | fired |
|---|---|---|---|---|---|---|
| OFF (bare follow-up) | 1 | 1 | 2 | 0 | 5 | 0 |
| ON (follow-up + t1 terms) | **3** (+2: fu-08, fu-15; lost 0) | 4 | **10** | 4 | 4 | 20 |
- G0 infra PASS: 0 missing; repeat identity on every cell. G1 OFF = wt/pr1: 80/80 (raw ids, kept ids, promptSha). G2: turn-1 + v0.1 ON = OFF on 80/80 (raw, kept, promptSha, codes), followup:expanded fires on 0/80. **G3 FAIL: 3 < 1 + 6.**
- Kept flips: 4 pairs go from kept to empty (fu-11 camp, fu-13 evacuation, fu-16 Austria river, fu-17 Paraguay debt) and 5 go from empty to kept (fu-10, -12, -14, -15, -18). fu-16 is the only article loss: "longest river in Austria" plus "Ireland … landscapes height" pulls the Ireland side.
- The title boost fired on 2/20 pairs. The previous answer's kept titles are rarely in the turn-2 raw list, and when they are, they are already first.
- Why the reach does not follow: the expanded query (≤ 12 t1 terms added to a 4–8-word turn) is dominated by turn 1's words. Search (lexical coverage needs a majority of ≤ 12 terms; semantic search uses the merged text) and compressContext's sentence scoring (the same expanded matchQuery) both favour turn 1's lead or fact chunks over the neighbour that answers turn 2. Of the 7 pairs where ON keeps the article without the gold chunk, 4 keep turn 1's fact chunk.

## Reading
- PHONEFAIL's symptom is confirmed as a reach gap. The bare follow-up keeps the gold chunk on 1/20 and the gold article on 2/20 (5/20 kept nothing at all). History-aware retrieval is the right target, and query expansion is not the right mechanism: it fixes the article, not the chunk.
- Post-10-20 candidate, FOLLOWUP r2 (BACKLOG row 17): article-scoped neighbour fetch. When the previous answer's kept article is known (via the history turn's `sources`, which this patch already carries), fetch that article's chunks and score them against the **bare** follow-up (X2b-style neighbour append, LEVER +0.066 on the 180), with no t1 terms in compressContext. Run it on the same 20 pairs under a new freeze. The ceiling is visible now: ON already reaches the article on 10/20.
- Wiring note: the app's ConversationTurn has no sources today. Any title-based variant needs the chat to pass the shown source titles in the history turns.

UNKNOWN: whether the real route gate, which sees the history, sends every turn-2 to search (the replay forces search). The learned detector is not used in the replay (lexical only), so health turn-2s may route differently on the device.

## Files
`tools/` draw.py, show_nb.py (authoring aid), fu_draft.tsv, fu_rubric.tsv, mkpairs.py, mkq.py, replay-fu.ts/.sh, run_step0.sh, gate0.py, followup.patch (+ .sha256), followup-adapter.eval.patch; `runs/draw.json`, `runs/q/` (replay inputs), `runs/replay/` (t1/t2 per pack, fu + pr1 cells, v0.1; 1.7 MB); `aggregates/gate0.json` (per-pair table), `aggregates/followup.json`. Replay cache: 9 new appdir keys (≈ 0.2 GiB) were deleted after the run; MacBook free 6.2 GiB. No server was started; the 1.7B llama-server seen by busy.sh belongs to another lane and was left alone. Exposure: public self-tests + v0.1 public only (no EXPOSURES row).
