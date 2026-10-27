# CROWDQ: what does installing all 9 packs as peers cost in answer quality versus the one relevant pack, on the pack-matched set? (frozen 2026-10-13 14:3x, coordinator)

## Tags
Tags: none

## Question
PACKROUTE step 0: with all 9 packs + kit installed (P = peers, today's engine) the fact article is kept on 46/180 vs 68/180 with only the relevant pack (S); both routers tried (deterministic vote 0.25, 4B zero-shot 0.61) failed their accuracy gates. Before any further router engineering the prize must be measured in quality, not reach: **arm P = 4B claim build (cut 7) with kit + all 9 published packs installed**, 180 public self-test items; **control S = the SELFTEST-SCORES with-pack traces/judgments** (one pack installed; Haiku rows st-<pack>-cut7-s42, Opus rows from ST2 L2). Use: (a) the product statement "install everything" vs "one relevant pack"; (b) P's traces and judgments are the control of the STACK criterion (router + keep rule), so this run is required either way.

## Fixed inputs
- Items: the 180 public self-test items (9 × 20); requests = selftest_to_bench.py output with `config.kit` = kit (crypto, wikivoyage) + the 9 published packs (ids + published sha256 from shared-data/packs/{wave1,wave2}/<id>.sqlite.json), seed 42, claim settings; runId st-<pack>-cut7-all9-s42.
- Tree: kiln-local/be-0cfd4a77-cut7 (claim build), run_selftest.sh pattern (server backend, -t 4, seed 42: deterministic, SEEDGEN). BOAR_EVAL_PACK_DIRS resolves the 9 ids.
- Judge: Haiku 5.5-low N=4 both orders on P (360 calls); S rows exist. Paired Δ P − S raw / above_min over 180 and by pack family; same_answer.py field (RULE 27; expect kept sources to differ on most items, the field is reported, not a gate); precheck ≥ 20 % changed prompts (expected ≈ 70 %).

## Power
expected_delta: −0.03 raw (P − S) on the 180 (source: PACKROUTE step 0 — article kept 46 vs 68, chunk reach 42 vs 67; SELFTEST-SCORES: the with-pack lift +0.032 tracks kept-from-pack share, so losing ≈ 1/3 of the kept pack passages costs ≈ 1/3…1 of the lift: −0.01…−0.03; the SE family loses half its kept articles (28 → 14) → −0.03…−0.05 there)
n: 180
seeds: 1 (deterministic)
mde: ≈ 0.03 raw paired at n 180 (Haiku compresses; Opus on a near-miss)
slice: n/a
l1_futility: n/a
reopen: n/a (measurement of a product configuration; no closed family)
split: paired Δ by pack family (SE vs topic), declared (expected: SE more negative)

## Stages and rules
1. Generation P on the 180 (MacBook, nohup, resumable per pack; smoke = first pack 20/20 answers, 0 errors, kit list in traces = 11 packs).
2. Haiku N=4 both orders on P; paired Δ P − S; by family; reach check in the traces (fact article kept must reproduce the replay's 46 ± 3, else stop and report the discrepancy before judging).
3. Reading (strict): **crowding cost confirmed** if P − S CI high < 0 and Δ ≤ −0.03 → the router/stack line keeps its +0.03…+0.05 prize and continues (STACK criterion); **cost small** if CI through 0 or |Δ| < 0.03 → the top-1 router line is closed at the product level (the prize is below MDE) and the stack reduces to the keep rule + quota; near-miss (Haiku Δ ≤ −0.02 with CI through 0) → Opus N=4 on P (360; S Opus rows exist).

## Stop rules and budget
0 paid API. MacBook only. Never two 4B generation jobs at once (check pgrep llama-server Qwen3-4B / adapter.ts; the :8094 detector is not one). Disk ≥ 8 GiB. Haiku 360 (+ 360 Opus on a near-miss).

## Outputs and exposure
arms/crowdq/{CROWDQ.md, tools/, aggregates/, runs/ (traces + judgments, ≈ 20 MB)}; public items only, no blind exposure. QUEUE rows per stage. P traces are reused by the STACK criterion as its control.
