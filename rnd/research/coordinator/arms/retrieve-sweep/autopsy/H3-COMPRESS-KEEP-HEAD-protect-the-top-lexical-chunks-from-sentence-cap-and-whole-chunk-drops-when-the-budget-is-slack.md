# H3 COMPRESS-KEEP-HEAD (RETRIEVE-SWEEP stage 2, 2026-10-22, MacBook, 0 LLM / 0 judge / 0 Opus / 0 paid / 0 phone)

TL;DR: **verdict NO** (frozen rule, RETRIEVE-SWEEP-criterion sha 94ddb631). MAIN recovery **0/25**, losses **0/22**, QFORM hit@kept **41.4 % -> 41.4 %** (delta +0.0, CI [0, 0], 0 gained / 0 lost), junk-kept 1.08x, context tokens +18 % (QFORM) / +16 % (MAIN). Not a single gold chunk or fact moved. Cause: the keep step does not lose these facts in `compressContext`: of the 25 QFORM golds that are retrieved and then dropped, 22 die in the grounding filters after compression (`onSubject` / health-strict), and of the 25 MAIN S2/S3 ids the fact is in the retrieved list for only 4, three of which the fix cannot reach (see the table).

## What the patch does
Patch: `patches/H3-COMPRESS-KEEP-HEAD-protect-the-top-lexical-chunks-from-sentence-cap-and-whole-chunk-drops-when-the-budget-is-slack.patch`, sha256 `8f521ec75b2080429cae3d92b7e9def141e7b374c74a1c68cc6c65fcfc821909` (diff -ruN of `src/` against the base tree `kiln-local/be-0cfd4a77-cut7-litepacks`, applies with `patch -p0`). Tree: `kiln-local/rs-H3` (APFS clone; base not touched). Patched files in the clone (sha256 prefix): `src/rag/compress.ts` f1dba94748c1, `src/routing/context.ts` 9ecd24b30135, `src/routing/answer.ts` cf6cf0c8d0d9, tests `src/rag/compress.test.ts`, `src/routing/context.test.ts`.

Deviation from the spec (closest faithful version): the spec names `src/rag/compress.ts`, but **`answer.ts` imports `compressContext` from `./context` (`src/routing/context.ts`), a second copy of the function** (it also adds the `relevance` field); `rag/compress.ts` is only used by `executor.ts`/`compressForAnswer`. A patch to `rag/compress.ts` alone would have been inert in the replay, so the same change is applied to both copies (same logic, same switch).

Switch `RS_COMPRESS_HEAD=1` (optional `RS_COMPRESS_HEAD_TOK`, default 160). Unset = byte-identical (the exported function calls the unchanged body as `compressBase` and returns it; no flag is set).
1. Slack: `tokensBefore <= tokenBudget` (the function's own budget) -> every input chunk with `approxTokens(title\nbody) <= RS_COMPRESS_HEAD_TOK` comes back whole (verbatim body, no sentence cap), added to the normal picks; chunks above the cap go through the normal selection.
2. Always: input positions 0 and 1 (the top-2 chunks as passed by `answer.ts`) are never dropped wholesale. If the base pass drops one, the pass is re-run with that chunk protected: relevance floor bypassed, its opening sentence first, then its query-scoring sentences up to `perChunk`, ahead of the other chunks (the pinned-chunk mechanism, without the `pinned` ordering priority). A protected chunk can displace later chunks under a binding budget (accepted by the spec; checked by the losses count).
3. Sentence scoring untouched. `compressContext` returns `headProtected: true` only when the output differs from the base output; `answer.ts` turns it into reason code `rs:compress-head` (pushed right after `context:a->b`).

## Checks
- Unit tests (vitest 5.0.3, run from a scratch copy of the patched `src/` against boar-app's node_modules because the tree has no test runner): 17/17 in `compress.test.ts` (3 new: slack 6-sentence ~120-token chunk comes back whole, off = unchanged and `TOK=40` is not whole; binding budget keeps positions 0 and 1 where the base drops them; 20 fixture calls with the switch unset / `=0` deep-equal to each other and unflagged ON results deep-equal to the base) and 103/103 in `compress.test.ts` + `context.test.ts` (2 new on the live copy).
- `tsc --noEmit`: the same 4 pre-existing errors as the base tree (missing `app.json` / `assets/corpus/corpus.json` in the scratch dir); no new error.
- Full suite in the scratch dir: base 17 files / 5 tests failing, patched identical failing set (missing assets in the scratch dir, not related) and +5 passing tests.
- **Switch-off identity** (tools/proofdiff.py; raw / wide / kept chunk ids and reason codes): 20 items (replay/proof20) vs the QFORM B0 replay **20/20 on all four**; full QFORM 432 switch-off run vs B0 **432/432 on all four** (replay/H3off.qform.jsonl); MAIN 97 switch-off vs B0.main **97/97 on all four** (replay/H3off.main.jsonl).

## Commands
```
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep
tools/run_h3.sh            # off20 + proofdiff, QFORM ON, (MAIN hit "database is locked": other workers shared the replay app dir), QFORM off 432
tools/run_h3_main.sh       # MAIN ON/OFF with retry (K1 kit, K1 settings, as replay/RUN.md) + proofdiff vs B0.main
tools/run_h3_sens.sh       # sensitivity: RS_COMPRESS_HEAD_TOK=256 and 1000 on MAIN + QFORM
tools/run_h3_wall.sh       # adjacent OFF/ON/OFF/ON QFORM runs for wall
python3 -I tools/sweep_h3.py ; python3 -I tools/sweep_h3_sens.py          # -> aggregates/sweep-h3{,-sens}.{json,md}
tsx tools/h3-stage.mts <replay.jsonl> task > ...; python3 -I tools/h3_stage_report.py ...; python3 -I tools/h3_main_autopsy.py ...   # stage attribution
tsx tools/h3-bench.mts ../qform/replay/qform.replay.jsonl 700             # in-process compress timing
```
Replays are `tools/replay.sh` (replay-sweep.ts sha da1978bf2075c255) with `env RS_COMPRESS_HEAD=1`; sets as in replay/RUN.md (QFORM 432, merged A-union pack, stock settings; MAIN 97, K1 kit and K1 settings).

## Numbers (paired vs B0; CI = item bootstrap B 2000 seed 11)
| | B0 | H3 (TOK 160, the verdict arm) | H3 TOK 256 | H3 TOK 1000 (ceiling) |
|---|---|---|---|---|
| QFORM hit@kept (432) | 41.4 % (179) | 41.4 % (179) | 41.4 % (179) | 41.4 % (179) |
| delta vs B0, CI | | +0.0 pts [0.0, 0.0]; fact-cluster [0.0, 0.0]; gained/lost 0/0 | same | same |
| QFORM dropped-25 kept | 0/25 | 0/25 | 0/25 | 0/25 |
| MAIN recovery on the 25 S2/S3 ids | 0 | **0/25** | 0/25 | 0/25 |
| MAIN losses on the 22 S4/S5 ids | 0 | **0/22** | 0/22 | 0/22 |
| MAIN kept lists changed (ids) | | 5/97 (bodies/context changed in 21) | 5 | 5 |
| junk-kept (206 items, gold not in wide-12) | 1.53 | 1.66 (**1.08x**) | 1.67 (1.09x) | 1.66 (1.08x) |
| mean kept chunks QFORM / MAIN | 1.83 / 2.77 | 2.02 / 2.84 | 2.05 | 2.05 |
| ctx tok after compression QFORM (mean) | 276 | **327 (+18.5 %)** | 390 (+41 %) | 399 (+44 %) |
| ctx tok after compression MAIN (mean, n 86) | 230 | **266 (+16 %)** | | |
| kept tok QFORM / MAIN | 191 / 374 | 212 (+11 %) / 386 (+3 %) | 248 | 251 |
| `rs:compress-head` fired QFORM / MAIN | | 230/432 / 35/97 | | |
Per-form hit@kept identical to B0 on all nine forms. Wall: the first full runs overlapped with other workers (load average 130-150, wall means 315 / 1390 ms, unusable). Clean adjacent QFORM pairs at load ~20: **OFF 75.0 / 76.2 ms, ON 73.9 / 76.0 ms per query (parity)**; the compress call itself in-process (interleaved): 0.63 ms off vs 1.14 ms on per call (the extra base pass), negligible against the 75 ms replay and the LLM prefill.
Rule: hit +8 pts with CI low > 0 **fails** (0.0); recovery >= 5/25 **fails** (0); losses <= 2/22 passes (0); junk <= 1.25x passes (1.08x). **NO.** The ctx-token cost (+16 to +18 %, about +36 to +51 tokens per item, up to +426 on a single item) buys nothing here.

## Where the gold is lost (why a compression fix cannot move it)
Stage attribution by re-running the live `compressContext` on every replay row's retrieved list with the per-task budget (lookup 450, others 700; reproduces the replay's `context:a->b` on 429/430 QFORM and 85/86 MAIN rows, and the 230/230 flags), `aggregates/h3-qform-stage.txt`:
- QFORM: gold quote/chunk in the retrieved list 204/432; kept by B0 179; **dropped 25 = 22 in the grounding filters after compression (gold survives `compressContext`, then `onSubject` or the health topic filter removes it), 3 in compression**. The switch rescues the gold at the compress stage in 1 of those 3 (`qf-boar-visa-en-07-F1`), and grounding drops it afterwards; the other 2 (`factbook-08-F0`, `medlineplus-en-03-F0`) are not rescued (not checked further why). Compress-stage gold: 200 -> 201 of 204.
- MAIN (`aggregates/h3-main-autopsy.txt`, `.json`): the fact is in the retrieved list for only **4/25** S2/S3 ids; for the other 21 it is a retrieval miss, so no compression change can recover them.

| S2/S3 id with the fact retrieved | what happens | why H3 does nothing |
|---|---|---|
| vit-cry-010 (DAO hack lessons) | fact chunk `crypto:40957` (192 tok, raw position 2) is kept as a chunk but its fact sentence is cut; task = lookup, budget 450 < 496 tokens retrieved | **budget is binding, so no slack-whole**; position 2 is outside the protected head; with TOK 1000 still nothing (still binding). The task note's guess that this item is the one recoverable was wrong |
| vit-cry-001 (ECDSA broken) | fact sentences in chunks at positions 1 and 2 are cut by the 4-sentence cap / budget | 769 > 700 so not slack; positions 0 and 1 are kept anyway (clause 2 inert); the chunks are above 160 tok |
| vit-hlt-001 (jellyfish) | fact survives compression (4 Wikivoyage pages), then removed by `grounding:health-strict` / off-topic filter | lost after compression |
| vit-hlt-002 (altitude, the HIV case) | raw order is Glioblastoma (0), HIV (1), then the three Wikivoyage "Altitude sickness" chunks (2, 4) and North Sikkim; the relevance floor drops the altitude chunks because HIV's "headache, nausea, dizziness" sentence out-scores them | **the protection hits the wrong chunks**: clause 2 re-adds Glioblastoma (position 0), context 66 -> 149 tokens, still no altitude chunk; the gold sits at positions 2-4, outside the head. Health-strict then drops everything anyway (`health-no-source` -> altitude first-aid card, as in B0) |

S4/S5 must-not-lose: 22/22 present in both, 0 losses; the ON compress output contains the fact in two more cases (`lan-exp-005`, `lan-hlt-003`, already present in kept via other chunks), so the fix is harmless for recall and only costs tokens.

## Assessment
- The hypothesis "the head chunks lose their fact sentence or get displaced wholesale in compression" is true only for a handful of items and, for the ids that matter, the gold is not a head chunk (positions 2-4) or the loss is downstream. In the HIV-vs-Altitude case the displaced chunk IS the gold, at raw position 2+, so a rule that protects positions 0-1 protects the distractors.
- If compression is to be touched again, the evidence points elsewhere: protect by relevance to the article the question names (not by raw position), or fix the grounding filters (`onSubject`, health-strict), which hold 22/25 of QFORM's drops and the S3-grounding ids of MAIN (A GROUND-DENSE targets this). Whole-chunk-under-slack alone is a pure token cost (+16 to +18 % context; G stage 2 found about +73 prompt tokens cost U on yes/yes items for the 1.7B).
- No answer-stage screen is warranted (not a CANDIDATE; Haiku/Opus untouched).

## Files
patch + sha above; `tools/run_h3*.sh`, `tools/sweep_h3.py`, `tools/sweep_h3_sens.py`, `tools/h3-stage.mts`, `tools/h3-bench.mts`, `tools/h3_stage_report.py`, `tools/h3_main_autopsy.py`; replays `replay/H3*.jsonl` (H3.qform, H3.main, H3off.*, H3t256.*, H3t1000.*, H3wall.*, H3.off20, H3.stage.*); `aggregates/sweep-h3*.{json,md}`, `aggregates/h3-main-autopsy.{json,txt}`, `aggregates/h3-qform-stage.txt`.
