# SHIP15B-PACKS criterion (frozen 2026-10-21 before any generation or judge call of this arm)

## Question
Does the K1 pack kit help the shipped RC1 model (Qwen2.5-1.5B-Instruct Q4_K_M) under our engine, vs the same model closed-book? Feeds NOTE-5 and claim variant S01.

## Arms (same host: Mac mini M4, tree <runner>/kiln/be-0cfd4a77-cut7-litepacks, llama-server b11010 CPU -t 4, seed 42, Succinct persona, maxTokens 512, LITEDECLINE_OFF=5, --reasoning off)
- P (packs): arms/lp-screens/tools/run_arm.sh ship15b-packs K1 main patches/ship15b-packs.patch with IDS_OVERRIDE = arms/litepacks/data/v01-57.ids.
  Patch = FLOOR's model swap (the qwen3-1.7b-q4km id loads Qwen2.5-1.5B-Instruct-Q4_K_M.gguf, sha 1adf0b11...) + FACTS tables off; retrieval ON with the K1 kit.
- C (closed-book control): the existing FLOOR-ANCHORS 1.5B traces arms/floor-anchors/traces/floor-anchors-K0-main-sub3e6183-s42.traces.jsonl,
  generated 2026-10-21 on the mini with the same tree, binary, threads, seed, persona and model swap; differences: retrieval returns [] (closed-book hunk) and
  the request kit field lists K0 (inert when retrieval returns []). Same-host comparable by MINI-BASELINE rule 1 (same tree/binary/concurrency class); stated as a limit.
- Context row (no rule): 1.7B K1 mini control arms/lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl (FACTS on), Haiku rows existing; Opus rows only where the
  identical (id, text) already has Opus judge.v1 rows in the pool (cv5_opus_pool.py); no new Opus calls for it.

## Items
The CV5 51 v0.1 dev ids = ruler/cv5-ladder/in/set.json "ids". No blind/, rnd/veil, bench/v0.4.

## Judge
- Primary: Opus judge.v1 (judge.mjs --judge-model opus via arms/deepthink/tools/shard_judge.sh model opus), both orders, seed 7, N 4 shards, + DECLINE2STAGE
  (ruler/tools/decline2stage_stage1.mjs, Haiku 5.5-low, one call per (id, text), rep 1) on P and C texts.
- C Opus rows: ruler/cv5-ladder/out/L0_15B_closedbook.judgments.jsonl + pool reuse (as cv5_ladder.py). P: units whose identical (id, text) already has an Opus pool row reuse it.
- Secondary: Haiku 5.5-low judge.v1 both orders (P via run_arm.sh; C = FLOOR judgments + lpctl-K0 rows for identical texts, as cv5_ladder.py).
- Caps: Opus 120 (planned <= 102), Haiku (task-wide incl. STYLE15B and stage 1) 500. 0 paid, 0 phone.

## Metrics (tools/ship15b_analyze.py)
Per item: s, r = mean of the 3 dimensions, averaged over both orders; corr = mean correctness. D2S: stage-1 "no" -> s := 1 (s-1 = 0).
U raw = sum(s)/sum(r); U floor-adj = sum(s-1)/sum(r-1) (primary); U_net = (U-0.058)/0.942. Win-rate = share of items with s > r.
Per 100 (of 51): correct-shown = not declined (answer.declined false and D2S attempted) with corr >= 4; CE-shown = not declined with corr <= 1.5.
Bootstrap: item clusters, B 2000, numpy default_rng(11), 2.5/97.5 pct, pairs on the same draws.

## Decision (Opus + D2S)
- PASS iff dU(P - C) floor-adj >= +0.03 AND CI low > 0 AND CE-shown(P) - CE-shown(C) < 3 per 100.
- FAIL-HARM iff CE-shown up by >= 3 per 100 (whatever dU). Otherwise NO-GAIN (dU < 0.03 or CI low <= 0).
- Report beside it: Haiku same frame, retrieval facts (kept sources per item), tokens and wall per arm.

## Limits (stated before)
One seed; n 51 dev; the control was generated hours earlier (not interleaved); FACTS off in both 1.5B arms (the 1.7B context row has FACTS on); bench engine (TS), not the native RC1 app.

## Budget
calls_cap: Haiku 500 / Opus 120
