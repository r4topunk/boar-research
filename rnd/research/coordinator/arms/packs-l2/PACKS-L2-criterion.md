# PACKS-L2: do the pack line's Haiku L1 headline numbers hold under Opus judge.v1 (L2)? (frozen 2026-10-13 20:4x, coordinator; a parallel session)

## Tags
Tags: none

## Question
The technical report (REPORT-PACKS-2026-10-13.md) rests on Haiku 5.5-low L1 rows for three paired cells on the 180 public self-test items (9 packs × 20, seed 42, generation deterministic — RULE 27): S − OFF (one pack vs claim kit only) +0.032 (+0.016…+0.050); P − S (all 9 packs as peers vs one pack) −0.016 (−0.033…−0.001); X − P (STACK-2 keep rule + quota 2/6 under all 9 vs peers) +0.005 (−0.009…+0.021). Haiku compresses paired gaps vs Opus (L1-PROTOCOL addenda 10-07/10-10). This arm re-judges the same traces with Opus judge.v1 (L2) so the report carries L2 numbers, and so the SE-only stack decision (R49: Haiku CI low −0.000 on SE) is decided at L2. Also the wave-3 packs' S − OFF (qa-cooking-se, qa-money-se; 40 items) at L2, reported separately (never pooled into the 180 headline).

## Fixed inputs
- Traces (all existing, nothing generated): S = `arms/packs/selftest-runs/st-<pack>-cut7-s42.traces.jsonl` (Opus rows already exist: `.judgments.opus.jsonl`, 40 rows each, from DENSECHUNK-ST2's control — REUSED, not re-judged); OFF = `st-<pack>-cut7-nopack-s42.traces.jsonl` (wave 3: `-nopack-s42` / `.fix003` as SELFTEST-SCORES' addendum names it); P = `arms/crowdq/runs/st-<pack>-cut7-all9-s42.traces.jsonl`; X = `arms/stack/runs/st-<pack>-cut7-stack-s42.traces.jsonl`.
- Judge: `arms/deepthink/tools/shard_judge.sh <traces> <R>.judgments.opus.jsonl boar-eval/bench/selftest/<pack> <R>.ids selftest-<pack>-cut7-<cell>-opus 4 opus` (judge.v1, `--judge-model opus`, no --effort, seed 7, both orders). Output next to the Haiku file as `<R>.judgments.opus.jsonl`. Record 429 / exit-3 counts per set (OPUSSHARD caveat: the first claim-size sharded Opus pass must log them).
- Aggregation: `arms/packs/tools/localjudge_agg.py` pattern (per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId) with the Opus rows; one JSON per cell under `arms/packs-l2/aggregates/`.
- Public items only (bench/selftest/*); no blind set touched.

## Power
expected_delta: +0.032 (S − OFF, Haiku pooled 180; Opus expected equal or larger, HAIKU-OPUS calibration 10-10: sign 5/5, size ±0.02); −0.016 (P − S); +0.005 (X − P)
n: 180 (9 packs × 20); wave 3 n 40 separate
seeds: 1 (generation byte-deterministic on the MacBook CPU path — SEEDGEN, RULE 27; judge seed 7)
mde: ≈ 0.02 raw at n 180, one seed, Opus (v0.2 one seed ≈ 0.025 at 110)
slice: none — L2 pass over existing full-set traces; L1 is complete (SELFTEST-SCORES, CROWDQ, STACK-2)
l1_futility: n/a (L1 done; S − OFF Haiku CI low > 0)
reopen: R49 (STACK-2 "not decided at MDE 0.03 → optional setting") is re-decided at L2 on the same traces, as its row foresaw ("SE-only product decision possible, CI low −0.000"); nothing else reopened
split: pre-declared: SE packs (travel, ethereum, bitcoin, health, outdoors) vs topic packs (firstaid, medlineplus, factbook, simplewiki), as in the report

## Stages and rules
1. Smoke: one set (qa-travel-se OFF, 40 calls) → rows 40, 0 failures, 429 count logged. FAIL-INFRA stops.
2. OFF ×9 → S − OFF at L2 (pooled + per pack + split). Then P ×9 → P − S. Then X ×9 → X − P. Then wave 3 S + OFF (4 sets). One chain of N = 4 shards at a time; a second chain in parallel only after the first three sets show 0 429s.
3. Verdicts (strict, Opus rows only; never pooled with Haiku rows):
   - S − OFF: **CONFIRMED** if CI low > 0 and Δ ≥ +0.02; **SMALL** if CI low > 0 and Δ < +0.02; **NOT CONFIRMED** otherwise. Report per-pack Δ and the split.
   - P − S: **COST CONFIRMED** if CI high < 0; otherwise **NOT DETECTED**.
   - X − P: **SETTING-ELIGIBLE** (recommend the keep rule + quota as a default-eligible setting for SE packs) if the SE split Δ has CI low > 0 and the topic split Δ CI high ≥ −0.03 and v0.1 no-harm from STACK-2 stands; **OPTIONAL** (R49 unchanged) otherwise.
- No generation. One judge pass per set; a shard resumed on exit 3/4 counts as the same pass.

## Stop rules and budget
≤ 1,300 Opus calls total (0 paid API, 0 Haiku). No llama-server needed. STOP file semantics of shard_judge.sh respected; never delete another run's lock. Must finish before the 2026-10-14 01:00 BRT weekly reset or stop cleanly at a set boundary (partial results reported as partial).

## Outputs and exposure
`arms/packs-l2/PACKS-L2.md` (coordinator writes from the runner's text), `aggregates/*.json`, judgments next to the traces. Public items only → no EXPOSURES row; one QUEUE row per verdict stage.
