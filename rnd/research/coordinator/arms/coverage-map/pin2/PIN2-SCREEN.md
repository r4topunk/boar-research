# PIN2-SCREEN: context re-gate + Haiku answer screen on the 7 PIN2 changed items (2026-10-23)
Criterion ../PIN2-SCREEN-criterion.md sha256 `175076c03903517a46524f96cebbbcca4e07350f11b70ae67c150234e29b98dc` (frozen before any generation or judge call, not edited). Haiku 5.5-low 24 calls of 60, Opus 0, paid 0, phone 0. Generation: 1.7B Q4_K_M on the mini, seed 42.

**TL;DR. LEVER-CANDIDATE by the frozen rule, but thin.** Context re-gate PASS (total kept tokens MAIN +0.9 %, 27 topics +3.3 %; compressor tokensAfter over its own budget 0/86 and 0/26). Answer screen on 7 items: better 3 / worse 1 / tie 3 (rule better >= worse + 2: 3 >= 3), paired raw U on the 5 MAIN items 0.464 -> 0.482 (dU +0.018, CI -0.034...+0.068), 0 health items among the 7, 0 new confident errors. Two of the three "better" items are minimal-edit answers sitting exactly on the +1/3 threshold (trv-004 differs only in a citation index, [5] -> [7]; vit-hum-002 in one phrase): with those read as ties the count is 1 / 1 / 5 and the rule would say NO. The one substantive win is b15 (Kyoto chunk kept: "seat of the imperial court until 1869", H2H tie + PIN2 win); the substantive loss is b18 (second Cheetah chunk, the answer drops "20-30 seconds", H2H base wins both orders, -0.83).

## Context clause (section 1, 0 LLM, existing PIN2 replays)
| set | total kept tokens base | PIN2 | ratio | gate <= 1.10 | compressor tokensAfter > own budget | items without a compressor call |
|---|---|---|---|---|---|---|
| MAIN 97 | 56,812 | 57,333 | 1.009 | PASS | 0 of 86 | 11 |
| 27 topics | 8,701 | 8,987 | 1.033 | PASS | 0 of 26 | 1 |
Source: screen_ctx.json (tools/screen_ctx.py on replays/main.{off,PIN2}.jsonl, t27.{off,PIN2}.jsonl; budget = context:pin2-budget-N, count = context:A->B).

## Answer screen (section 2)
| item | set | judged as | base s | PIN2 s | delta | corr base -> PIN2 | warned base / PIN2 | verdict |
|---|---|---|---|---|---|---|---|---|
| vit-hum-002 | v0.1 | vs ref | 1.00 | 1.33 | +0.33 | 1.0 -> 2.0 | yes / yes | better (minimal edit) |
| vit-cry-008 | v0.1 | vs ref | 2.50 | 2.33 | -0.17 | 3.5 -> 3.0 | yes / **no** (now grounded, cites the rescued chunk) | tie |
| lan-exp-005 | v0.1 | vs ref | 2.00 | 1.83 | -0.17 | 2.0 -> 3.0 | no / no | tie |
| trv-004 | v0.1 | vs ref | 2.00 | 2.33 | +0.33 | 2.0 -> 2.5 | no / no | better (text identical except [5] -> [7]) |
| st-qa-cooking-se-004 | cooking | vs ref | 3.17 | 3.17 | 0.00 | 4.0 -> 4.0 | no / no | tie |
| b15 | 27 | H2H (PIN2 vs base) | 3.00 | 3.50 | +0.50 | 4.0 -> 4.5 | no / no | **better** (winners tie, PIN2) |
| b18 | 27 | H2H (PIN2 vs base) | 3.33 | 2.50 | -0.83 | 4.0 -> 3.5 | yes / yes | **worse** (winners base, base) |
s = mean over 2 orders of the mean of the 3 judge.v1 dims (1-5); better/worse at |delta| >= 1/3. Paired raw U (MAIN 5, ratio of sums vs the reference): base 0.4638, PIN2 0.4818, dU +0.018 (bootstrap -0.034...+0.068). Divergent pairs 7/7 (no byte-identical pair, so 0 free ties). Health items among the 7: none (MAIN base codes have no grounding:health-strict on these 5; b15 b18 not in the 27-topic health list). New CE: 0 (vit-hum-002 was CE in base, corr 1.0, and is not in PIN2, corr 2.0).
**Rule: context PASS, better 3 >= worse 1 + 2, 0 health losses, 0 new CE -> LEVER-CANDIDATE.**

## Validity
- Base regeneration = SEFIX-124 s42: 5/5 MAIN answer texts and kept titles byte-identical to sefix/ans-traces/sefix124-main-s42.traces.jsonl.
- Live kept titles = replay keptFull titles on 7/7 items in both arms; 0 errors, 0 empty.
- Deviation from the criterion text: "one job per arm" became two jobs per arm (MAIN and 27 topics), because the adapter refuses mixed runId/config in one requests file; same tree, env and kit per arm.

## Commands
```
cd <workspace>/rnd/research/coordinator/arms/coverage-map/pin2
python3 -I tools/screen_ctx.py                       # section 1
python3 -I tools/screen_req.py                        # req/screen-{base,pin2}-{main,t27}-s42.requests.jsonl
bash tools/screen_gen.sh base main; bash tools/screen_gen.sh base t27; bash tools/screen_gen.sh pin2 main; bash tools/screen_gen.sh pin2 t27
bash tools/screen_judge.sh                           # tools/screen_plan.py + shard_judge.sh ... 4 haiku; ledger judge/calls.log
python3 -I tools/screen_agg.py                       # -> screen.json
```
Tree on the mini = be-0cfd4a77-cut7-litepacks + H4-MERGE (4cd94755) + SEFIX-ALL (e3d6c3db) [+ PIN2.patch d6c0533c, RS_PIN2=1], env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1, BOAR_EVAL_PACK_DIRS=compose/packs-k13 (MAIN: the 13-pack kit pinned in the SEFIX-124 requests, i.e. the SEFIX screen recipe; b15/b18: kit wiki-vital5 only, Succinct). Traces (gitignored): traces/pin2screen-{base,pin2}-{main,t27}-s42.traces.jsonl (1eac79fe, 585259f7, 78395571, eb472258).
Judge rows: judge/{base,pin2}-{v01,cooking}.judgments.jsonl, judge/h2h.judgments.jsonl, h2h bench judge/h2h-bench/ (refs = the base t27 answers), plan.json, calls.log (24 calls: 8 + 2 + 8 + 2 + 4).

## Caveats
7 items, one seed (42), Haiku 5.5-low L1 judge (compresses gaps, threshold-level noise on near-identical texts is visible here: trv-004), b15/b18 judged head-to-head with no reference, dev items, bench engine (not the native Kotlin app). The context re-gate was written after the PIN2 replay numbers were known (coordinator-directed), so section 1 confirms known numbers. The verdict rests on items at exactly the +1/3 threshold; a post hoc reading with minimal-edit items as ties gives 1 / 1 / 5 (NO). Before any adoption: a second seed (s43) on the same 7 items and an Opus read of b15/b18/vit-cry-008 would separate the Kyoto gain and the Cheetah loss from judge noise.
