# T-K4c — pack self-tests scorable by the standard pipeline; qa-travel-se scored (2026-10-12)

TL;DR: qa-travel-se self-test with the shipped 4B (cut 7, claim kit + the pack), Haiku 5.5-low L1: **raw 0.423 (0.360–0.484), above_min 0.262 (0.182–0.341), win/tie/loss 0/0/20** (40/40 ref wins). Pack retrieval fires (15/28 kept passages from the pack, 9/20 items) but the fact's article is kept on only 6/20 and the ratio is flat whether it is kept or not (0.431 vs 0.419). Dev number, agent-written items.

## Pipeline (tools/)
- `selftest_to_bench.py <pack> [--seed 42] [--no-pack]` (python3 -I): selftest jsonl → `boar-eval/bench/selftest/<pack>/` (bench.json, questions.jsonl, refs/refs.jsonl, refs/MANIFEST.json with shas) + `selftest-runs/st-<pack>-cut7-s<seed>.requests.jsonl` (claim config `repro/claim-config-cut7.json` + kit entry {id, sha256 from wave1/<pack>.sqlite.json}; item {id, question, lang}). Mapping: id/question/category kept; rubric list → question.rubric (judge joins it as notes, Penalize bullet included); gold `answer` → refs.answer (ok=true); style/in_pack_facts/source → question.selftest (not read by the judge).
- `run_selftest.sh` = mp4b `local-run.sh` + `shared-data/packs/wave1` first in BOAR_EVAL_PACK_DIRS (install = adapter resolves kit id → `<id>.sqlite`, sha-checks, symlinks into the app dir `corpus/`). Tree kiln-local/be-0cfd4a77-cut7 (patch 0fba26b8, adapter 6298e5d3), server backend, 4 threads, ship profile, mmbert :8094, noplaces.
- `selftest_agg.py <pack> <traces>`: 0-LLM checks (non-empty, retrieval fired, kept-from-pack by pack title / stackexchange url, fact article in raw/kept/shown, p50).
- Judge: `deepthink/tools/shard_judge.sh … haiku` (N = 4, both orders); `bench/v0.2/plan/floor_metrics.py --runs R --dir selftest-runs --ids R.ids --strict`.
- One command per pack: `tools/score_selftest.sh <pack> [seed] [--no-pack]`.

## Run st-qa-travel-se-cut7-s42 (MacBook M1 Pro, 23:43–23:49)
| metric | value |
|---|---|
| answers non-empty / errors / declined | 20/20 / 0 / 0 (all tier fast) |
| retrieval fired (raw > 0) | 20/20 |
| kept passages from the pack | 15/28 (items with ≥ 1: 9/20; 6 items kept 0) |
| fact article in raw / kept / shown | 13/20 / **6/20** / 6/20 |
| Haiku ratio raw (CI) | **0.423 (0.360–0.484)** |
| above_min (CI) | **0.262 (0.182–0.341)** |
| wins / ties / losses vs gold | 0 / 0 / 20 |
| ratio, fact article kept vs not | 0.431 (n 6) vs 0.419 (n 14) — descriptive |
| p50 / p90 total | 11.7 s / 16.3 s; answers median ≈ 50 words |
Judge calls: 40 (Haiku 5.5-low, 54 s wall). Files: selftest-runs/R.{requests,traces,judgments}.jsonl, aggregates/R.{gen.json,floor_metrics.txt,strata.txt}.

## Findings / caveats
- Bottleneck is the keep step, not BM25: the fact article is in raw on 13/20 but kept on 6/20 (6 items kept nothing at all → closed-book answers). Even when kept, the 4B's ≈ 50-word answer misses the rubric facts (item 001: kept a neighbouring Thai-visa thread and answered "may be denied entry").
- Cut 7 predates T-K2 source codes: SE rows fall back to source "enwiki", so the citation reads "Wikipedia — https://travel.stackexchange.com/…" (wrong label, correct URL). Pack membership was counted by title, not label. A cut with T-K2 would also exclude SE from topicSources.
- Haiku L1 compresses gaps; gold answers are short agent-written (Claude family) texts written from the very article; ratios not comparable with v0.1/v0.2/V-para or Opus numbers. Dev number, never a claim row.
- No no-pack control run (budget); the pack's lift needs `score_selftest.sh qa-travel-se 42 --no-pack` (+40 calls).

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.
