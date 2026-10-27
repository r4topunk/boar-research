# TK2-FIX step 0: does the sources patch v2 (bare title for the T-K2 sources + the title-lookup rule for codes 10-12) keep the reach gain without the own-pack drops? (frozen 2026-10-16 before any replay of the v2 tree; 0 LLM / 0 judge / 0 paid; public items only)

## Tags
Tags: probe
Ruleset: 30

## Question
TK2-REPLAY (arms/packs/tk2-replay, 10-13): the T-K2 sources patch changes kept lists on 52/180 self-tests via (1) the "Stack Exchange: " / "Simple English Wikipedia: " ... title prefixes feeding onTopic / termCoverage / the keep step (own-pack drops on 17 items) and (2) codes 10-12 (medlineplus, factbook, simplewiki) entering topicSources (title lookup), net fact chunk kept 35 -> 42. v2 removes (1) only: packHitToChunk keeps the bare title for the four T-K2 sources (cut 7 mapped their codes to enwiki, i.e. bare title); the label stays in `source` (citation); (2) is kept as is. Use: a PASS sends BACKLOG row 4 to a smoke + Haiku L1 re-score of the 180 at the next META; a FAIL closes the row.

## Fixed inputs
- cut 7 = kiln-local/be-0cfd4a77-cut7-tk2off (byte clone of cut 7 src, COMMIT 0cfd4a77, PATCH_SHA256 0fba26b8...).
- tk2 (reference) = kiln-local/be-0cfd4a77-cut7-tk2 = cut 7 + tools/tk2.patch (recovered by diffing the two trees' src; hunks identical to arms/packs/tk2-replay/tk2.vs-cut7.patch d2d09813...); sha in tools/tk2.patch.sha256.
- tk2fix (arm) = kiln-local/be-0cfd4a77-cut7-tk2fix = tk2 + tools/tk2fix.vs-tk2.patch (src/rag/packs.ts only: BARE_TITLE_SOURCES); full patch vs cut 7 tools/tk2fix.vs-cut7.patch; shas in tools/tk2fix.patches.sha256.
- Replay: arms/packs/tk2-replay/tools/replay-tk2.sh (engine retrieval + keep step + grounding, no LLM), --gate search --k 6 --modes off,off (two passes, repeat identity), detector not used. Sets: 9 x 20 self-tests (rnd/research/packs/selftest/<pack>.jsonl; kit + the item's pack) and v0.1 public 60 (kit only; gold boar-eval/bench/v0.1/gold/sources.json). Same KIT and pack paths as tk2-replay/tools/run_tk2.sh.
- Scorer: tools/compare_fix.py = tk2-replay/tools/compare_tk2.py definitions (fact chunk / fact article = packroute step0.py, item's own pack only via chunkId prefix; empty-kept = raw non-empty, kept empty) over three cells.
- v0.2 kit no-harm: SKIPPED (its plaintext lives under blind/, off-limits to this runner).

## Power
expected_delta: reach only (fact chunk kept +5...+8 on the 180; TK2-REPLAY mechanism 2 = +7)
n: 180 + 60
seeds: 1 (deterministic replay; repeat identity checked)
mde: n/a (0-call gate, counts)
slice: all
l1_futility: n/a
reopen: n/a
split (declared): per pack; descriptive

## Ceiling (RULE 29; 0 calls)
ceiling: ORACLE-ST +0.095 on the 180 (fact in context); TK2 mechanism 2 = +7 fact chunks
bar_ceiling: n/a (pack self-tests; product correctness of citations)
launch: BACKLOG row 4 (coordinator, 2026-10-16)
transfer: product-only (engine sources patch for PR 1 / pack cards)

## Budget (RULE 29)
wall_cap: 0.5 h
calls_cap: Haiku 0 / Opus 0
smoke: n/a (0-call replay)
kill_if: replay errors or repeat identity < 180/180, 60/60 in any cell
checkpoint: n/a
subset_step0: n/a

## Precheck (0 calls)
token_projection: n/a
token_budget: n/a
disk_peak_gib: 0.1 (one tree copy 17 MB + <= 2 replay cache keys ~25 MB each; MacBook free 6.6 GiB)
off_baseline: cut 7 cell rerun in this arm (kiln-local/be-0cfd4a77-cut7-tk2off)
call_pattern: none (0 LLM, 0 judge, 0 paid)
lane: mac-cpu
opus_clause: none
wall_cap_h: 0.5
parallelism: 1
run_type: replay

## Gate (all of G0-G3; PASS -> smoke + Haiku L1 of the 180 at the next META; FAIL -> close)
- G0 infra: every cell 180/180 and 60/60 rows, repeat identity 180/180 and 60/60, 0 replay errors.
- G1 reach: on the 180, items with the fact chunk in kept (tk2fix) >= cut 7's count + 5.
- G2 own-pack drops: items where tk2fix drops >= 1 own-pack chunk that cut 7 kept AND the drop is not a title-lookup replacement (i.e. tk2fix's raw list for the item equals cut 7's raw list) <= 5 (TK2-REPLAY: 17 drop items under tk2). Also reported: all items with any own-pack chunk dropped vs cut 7 (descriptive).
- G3 v0.1 no-harm (RULE 26): kept lists identical to cut 7 on every v0.1 item whose route is not affected (affected = task / query / k / reason codes differ between cells; the affected ids are listed); harm = any v0.1 item where cut 7 keeps a gold-bearing source (gold refs match) and tk2fix does not. Gate: 0 unaffected-item kept diffs AND 0 harm items.
