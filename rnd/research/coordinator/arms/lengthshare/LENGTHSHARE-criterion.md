# LENGTHSHARE: how much of the recommended deep configuration's V-para floor-adjusted gap is reference length rather than substance (frozen 2026-10-10 22:3x, coordinator)

## Tags
Tags: none

## Question
Measurement, not a lever. Part 1 (0 calls, done: BAR-TABLE §2) showed H (deep + thinking 512) at correctness-only floor-adj 0.660 on V-para but completeness 0.301 / usefulness 0.341 against ≈ 280-word frontier+web references. Part 2 asks: if the same H answers are judged against the same references condensed to ≤ 80 words (key facts kept, nothing added), how much does the 3-dim floor-adj ratio move? That movement = the share of the remaining gap the judge attributes to reference length/detail; the rest is substance (missing key points per the item rubric).

## Fixed inputs
- Answers: H s42 traces, unchanged (`blind/V-para/runs-dt512/dh-H-vpara-s42.traces.jsonl`, the DT512 frozen run). No generation.
- Original judgments (control): `dh-H-vpara-s42.judgments.jsonl` (Opus judge.v1, both orders, 51 ids = runs-cut6/judged.ids).
- Capped references: `blind/V-para/refs-80w/refs.jsonl` = each ok reference row of `refs/refs.jsonl` with `answer` rewritten by Opus (`claude -p`, no tools, system prompt `tools/cap80.system.md`, temperature default) to ≤ 80 words keeping every fact, number, name and caveat that answers the question; rows keep id/question/ok; MANIFEST.json records jsonl_sha256 and the source refs sha. Any row > 95 words after one retry is re-capped by truncation at the last sentence boundary ≤ 80 words and flagged `truncated:true`. Script: `tools/cap_refs.mjs`.
- Judge: `shard_judge.sh` N = 4, opus (judge.v1), bench `bench-shim-80w` (same items.jsonl, refs-80w), system `lengthshare-H80`, output `runs-dt512/dh-H-vpara-s42.judgments.len80.jsonl`. 102 Opus judge calls + 51 Opus capping calls.
- Script-only scoped exception: the coordinator runs the scripts; no researcher agent touches blind/.

## Power
expected_delta: +0.05…+0.15 floor-adj on the 3-dim mean (source: 27/57 "correct but thin" bucket, BOAR ≈ 51 words vs ref ≈ 250, PIPELINE-AUDIT-2026-10-06 / HANDOFF-10-11 §1; if the judge follows its own "do not reward length" rule the shift is ≈ 0)
n: 51 (V-para judged ids), same traces both arms
seeds: 1 (s42; re-judge only, generation unchanged; judge noise only — Opus test-retest σ never measured, CI from the paired item bootstrap)
mde: ≈ 0.04 floor-adj paired (same items, same answers; judge-noise-only comparison)
slice: none (re-judge of existing traces; no generation, no L1 stage)
l1_futility: n/a (Opus directly; measurement)
reopen: n/a (new measurement, no closed family)

## Stages and rules
1. Cap refs (51 Opus calls); verify every row ≤ 80 words (or flagged truncated), ids = 51, sha into MANIFEST.
2. Judge H s42 vs refs-80w (102 Opus). Fail-closed: shard_judge rc 0 and check_judgments pass before any number.
3. Compute with `tools/dimshare.mjs` (per-dim ratios) and `deepvpara/tools/paired.mjs` (paired Δ, H80 vs H, same ids): Δ floor-adj (3-dim), Δ per dimension, W/T/L.
4. Reading (descriptive, no LEVER/NO verdict): length_share = Δ floor-adj / (1 − floorAdj_H) (gap to the reference) and Δ floor-adj / (0.50 − floorAdj_H) (gap to the bar, 0.064). If H80 floor-adj CI low ≥ 0.50 the sentence in BAR-TABLE reads "H clears the primary target only against 80-word references", never "bar met".
5. K s42 re-judge (102 more Opus) only if Δ ≥ 0.05 (to show the ranking K < H holds against short refs); otherwise skipped. One post-hoc split at most (by category), labelled hypothesis.

## Stop rules and budget
≤ 153 Opus calls (+102 conditional). Rate limit → stop (exit 3), resume; never skip a shard. No edits to the original refs or judgments.

## Outputs and exposure
`arms/lengthshare/LENGTHSHARE.md`, `aggregates/`, BAR-TABLE §2 addendum; refs-80w + judgments under blind/V-para/. EXPOSURES.md row: V-para, 0 new generations, 102 Opus judge calls on existing H s42 traces, 51 reference rewrites (reference text + question sent to Opus, no BOAR answers).
