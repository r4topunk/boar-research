# LOSSMAP: where does the recommended configuration lose against the reference? (frozen 2026-10-11 12:2x, loop coordinator)

## Tags
Tags: blocker
<!-- measurement arm: no generation, no Claude judge calls; it re-ranks BACKLOG B2–B7. `blocker` waives the Power check (nothing is decided by a threshold here). -->

## Question
For the recommended deep configuration H (cut 6 + Qwen3.6-35B-A3B + thinking 512, dt512 trees) and the 4B claim control K (cut 6 rows), classify the Opus judge.v1 rationales (both orders, seed 42) of every judged item on v0.2 (110) and V-para (51) into loss buckets, weight each bucket by the item's rubric loss (reference points − BOAR points over the three dimensions, averaged over the two orders), and split by category and route task. Output: the share of H's total loss per bucket, per category and per task; the same for K; the H–K difference tells which buckets the deep tier already drained.

## Fixed inputs
- H: `blind/V-para/runs-dt512/dh-H-vpara-s42.judgments.jsonl` (102 rows) + its traces (sha-matched); `blind/bench-v02/runs-dt512v02/dhv-H-v02-s42.judgments.jsonl` (220 rows) + traces.
- K: `blind/V-para/runs-cut6/cut6-vpara-s42.judgments.jsonl`, `blind/bench-v02/runs-cut6/cut6-v02-s42.judgments.jsonl` + the sha-matched traces (cut 3 traces reused by cut 6: FACTS fired 0 on these sets).
- Classifier: `typesafe-ai/jev` via the Vercel AI Gateway (`tools/lossmap.py`, question texts frozen with this file): seven boolean axes (missing_facts, wrong_fact, reasoning_error, hedged, thin, off_question, source_on_topic) at threshold 0.6, plus one `choice` primary bucket (absent_knowledge | thin | wrong | hedged | off_question | fine | other). State per item = the two rationales + the answer text (≤ 2,500 chars) + kept-source titles + the declined flag; question text is never read or sent.
- Script-only scoped exception on blind: the script reads rationales/answers; the cache of raw gateway responses stays under `blind/<set>/runs-<arm>/lossmap-cache/`; rnd receives ids, labels, probabilities and aggregates only.

## Power
expected_delta: n/a (measurement)
n: 51 + 110 items per arm, two arms
seeds: 1 (s42; SEEDVAR: v0.2 seed-stable r 0.90, V-para r 0.5–0.7 → bucket shares on V-para carry ≈ ±0.05)
mde: n/a
slice: none
l1_futility: n/a
reopen: n/a (never done at the configuration level; the 10-06 buckets were the 4B on v0.1)

## Stages and rules
1. Dry run (schema, trace match by sha) → 2. classify H and K on both sets (≈ 322 gateway requests, [usage detail removed]) → 3. aggregates + `LOSSMAP.md` → 4. re-rank BACKLOG: a lever's prior is scaled by the loss share of the bucket it attacks (B2 DEEPCOVER ← missing_facts ∧ thin; B3/B6 kit content ← absent_knowledge ∧ ¬source_on_topic; B4/B5 model ceiling ← absent_knowledge ∧ source_on_topic plus wrong; B7 ← off_question/reasoning on comparison).
Reading rules: a bucket with loss share < 10 % on H is not a lever target; `source_on_topic` is title-level only (a follow-up may look the missing fact up in the pack text); a `primary` with confidence < 0.6 is reported as "undecided" and excluded from the primary table but kept in the axes.
No Claude judge calls. No generation. No mini.

## Outputs and exposure
`arms/lossmap/LOSSMAP.md`, `aggregates/lossmap-{H,K}-{vpara,v02}-s42.json` (ids + labels + aggregates). One EXPOSURES row (script-only read of 4 judgment files + 4 trace files; 0 judge calls; external classifier = Vercel gateway, rationales + answers sent, no question text).
