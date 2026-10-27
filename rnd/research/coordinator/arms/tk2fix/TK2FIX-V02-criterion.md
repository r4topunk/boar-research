# TK2-FIX v0.2 kit no-harm: does the sources patch v2 change retrieval on the v0.2 110 with the claim kit, and does any item lose a gold-bearing source? (frozen 2026-10-16 before any v0.2 replay of either tree; 0 LLM / 0 judge / 0 paid; script-only on blind)

## Tags
Tags: probe
Ruleset: 30

## Question
TK2FIX-STEP0 skipped its v0.2 kit no-harm line (plaintext under blind/). The coordinator's scoped script-only exception (10-16 04:0x, same terms as LITE2/LITE3/LITE4) lets the scripts of this step read blind/bench-v02/ (questions + v0.2 gold sources); nothing but counts, ids, hashes and title-id diffs reaches the context. The claim kit has no pack with source codes 9-12 (crypto + wikivoyage only), so the expected result is no change. Use: PASS = the v0.2 no-harm line of RULE 26 for the v2 patch is closed (PR may carry it); FAIL = the change and the harm ids go to the coordinator before any PR.

## Fixed inputs
- cut 7 = kiln-local/be-0cfd4a77-cut7 (src byte-identical to -cut7-tk2off, diff -rq src empty).
- tk2fix (arm) = kiln-local/be-0cfd4a77-cut7-tk2fix (cut 7 + tools/tk2fix.vs-cut7.patch 6cd09ca6...).
- Replay: arms/packs/tk2-replay/tools/replay-tk2.sh (engine retrieval + keep step + grounding; LLM stubbed; no geo providers = the claim runs' noplaces), --gate search --k 6 --modes off,off (two passes, repeat identity), kit = shared-data/crypto/boar-crypto.sqlite + shared-data/packs/boar-wikivoyage-en.sqlite (same KIT as run_fix.sh), questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl (110), gold boar-eval/bench/v0.2/gold/sources.json. Outputs under blind/bench-v02/runs-packs/tk2fix-v02-kit.{cut7,tk2fix}.jsonl.
- Scorer: tools/compare_v02.py; gold match = compare_fix.py gmatch (scorers/retrieval.py rule). Counts/ids only.

## Power
expected_delta: none (no code 9-12 pack in the kit)
n: 110
seeds: 1 (deterministic replay; repeat identity checked)
mde: n/a (0-call gate, counts)
slice: all
l1_futility: n/a
reopen: n/a
split (declared): none

## Ceiling (RULE 29; 0 calls)
ceiling: n/a (no-harm line)
bar_ceiling: n/a
launch: coordinator 10-16 04:0x (TK2FIX v0.2 no-harm)
transfer: product-only (engine sources patch for PR 1)

## Budget (RULE 29)
wall_cap: 0.5 h
calls_cap: Haiku 0 / Opus 0
smoke: n/a
kill_if: replay errors or repeat identity < 110/110 in either cell
checkpoint: n/a
subset_step0: n/a

## Precheck (0 calls)
token_projection: n/a
token_budget: n/a
disk_peak_gib: 0.1 (<= 2 replay cache keys ~25 MB each; MacBook free 5.5 GiB)
off_baseline: cut 7 cell run in this arm
call_pattern: none (0 LLM, 0 judge, 0 paid)
lane: mac-cpu
opus_clause: none
wall_cap_h: 0.5
parallelism: 1
run_type: replay

## Definitions
- kept-list change: the set of kept chunkIds (order-insensitive) differs between cells for the item; ordered-only differences and reasonCode differences are reported separately.
- gold-bearing source kept (item level): >= 1 kept ref matches >= 1 of the item's v0.2 gold entries; count over the 110 (items without gold count 0).
- item loses a gold-bearing source: some gold entry matched by a cut 7 kept ref is matched by no tk2fix kept ref.
- articles kept: distinct kept titles per item, summed (descriptive).

## Gate (all; PASS -> v0.2 no-harm closed for the v2 patch; FAIL -> coordinator)
- G0 infra: both cells 110/110 rows per pass, repeat identity 110/110, 0 replay errors (else void, not FAIL).
- G1: kept-list changes <= 10 items.
- G2: gold-bearing source kept (tk2fix) >= cut 7's count.
- G3: 0 items lose a gold-bearing source.
