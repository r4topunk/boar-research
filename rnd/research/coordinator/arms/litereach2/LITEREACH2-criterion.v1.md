# LITEREACH2: does a wider X2b append budget (x1.5, x2) put the fact into the lite 1.7B's context on enough more of the 180 self-tests to be worth a judged slice? (frozen 2026-10-16, LITEREACH2 agent; 0-LLM gate, then Haiku random20, dev)

Frozen before any LITEREACH2 run (replay or generation). Mechanism = HEADPASS-X2b (HEADPASS-X2-criterion.md 1b70f6f3… + addendum 1 4b3578e7…; settings packHeadPass "a2" + packDense2 "append-budget") with its three constants made env-overridable; everything else as LITE5-180 (criterion 8fafa952…0481).

## Tags
Tags: none
Ruleset: 30

## Question
LITEREADERS: with the fact chunk in context the 1.7B is −0.032 behind the 4B, without it −0.088; LITE5-180: X2b puts the fact in the 1.7B's context on 97/180 (traces). The 1.7B decodes ≈ 2.5× faster than the 4B, so it can afford more prompt. Does a wider append budget raise fact-in-context on the 180 by ≥ 15 items within +900 prompt tokens p50 over X2b, and if so, does the 1.7B convert it (random20 Haiku)? Use: the lite tier's X2b budget setting.

## Fixed inputs
- Tree kiln-local/be-0cfd4a77-cut7-litereach2 = APFS clone of kiln-local/be-0cfd4a77-cut7-headpass-x2 (PATCH_SHA256 0fba26b8…) + litereach2-env.patch: src/rag/denseCandidates.ts reads HEADPASS_DENSE_D, HEADPASS_MAX_APPEND, HEADPASS_BUDGET_TOKENS from env BOAR_LR2_DENSE_D / BOAR_LR2_MAX_APPEND / BOAR_LR2_BUDGET_TOKENS (positive integers; unset = 2 / 4 / 600 = X2b). Patch sha recorded in the tree (LITEREACH2_PATCH_SHA256) and in the report.
- Cells (env): c1 = 600/2/4 (= X2b, baseline); b15 = 900/3/6 and b20 = 1200/4/8 (budget and dense slots scaled together: the X2b gate's D0 shows 16 fact chunks beyond D = 2 and 11 budget-dropped); t15 = 900/2/4 and t20 = 1200/2/4 (budget only). All five cells are gate-eligible.
- Replay = headpass-st/tools/replay-x2.ts (engine answer() with generation stubbed; 0 LLM) in the litereach2 tree, mode x2b, --sidecars shared-data/packs/v3proto, --gate search --k 6, kit + the item's pack as run_x2.sh, **--tasks-from the LITE5-180 ON traces** (route-gate decision and mmbert detector score of the 1.7B generation, so the health-strict class is the generation's, not the lexical one: removes the 97 vs 102 replay/trace gap of HEADPASS-X2b).
- Fact in context (per item) = an oracle fact chunk (oracle-st/tools/oracle-facts.json) of the item's own pack among the replay's kept list (sources event, appended chunks included) = gate_x2b.py's rule; LITE5's fic.py rule (S_present OR appended fact) reported beside it.
- Prompt tokens = the replay's promptTokens (engine approxTokens of the first generate prompt; the same count the budget uses).
- Identity checks (0 LLM): I1 c1 with env unset vs c1 with env set to 600/2/4: byte-identical lines (full key of gate_x2b.py + appended); I2 c1 vs the LITE5-180 ON traces: appended chunk ids (headpass:add / headpass:dense:add codes) identical on ≥ 170/180 and fact-in-context c1 reported vs 97 (fic-180.json); I3 the env-unset litereach2 tree without --tasks-from reproduces headpass-st/runs-x2/st-<pack>.x2b.jsonl x2b lines on the full key (sanity of the clone, ≥ 178/180).

## Power
expected_delta: +0.01…+0.02 raw pooled on random20 (source: LITE5-180 newly-present cell +0.173 on the 1.7B; ≈ +15…+25 newly present items on 180 → ≈ 1.7…2.8 items per random20 → +0.015…+0.024; the rest is generation noise ≈ 0)
n: 20 (random20 of the 180, seed 888)
seeds: 1
mde: ≈ 0.05 raw at n 20 one seed Haiku (LITE4/LITE7 random20 CI half-widths ±0.05…0.06)
slice: random20-st180-s888 = sorted(random.Random(888).sample(sorted(180 self-test ids), 20)); written to litereach2/random20-st180-s888.ids before generation (no signal20)
l1_futility: expected_delta < mde: the random20 cannot decide a pooled effect; it reads DIRECTION only (frozen labels below); the newly-gained split is the informative cell; no Opus; a 180 run is a coordinator call after this arm
split: (declared) random20 items whose fact-in-context is gained at the best cell vs c1 (newly gain the fact) vs the rest
reopen: n/a (LITE5-180 / LITEREADERS follow-up)

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: replay reach bound under lexical health (X2-GATE.md): X2b 102, X2 unbudgeted (D 2) 113, + fact beyond D 16 → ≤ 129/180 (≤ +27 items); × +0.173 / 180 → ≤ +0.026 pooled on the 180
bar_ceiling: n/a (pack self-tests, lite tier; not a bounty-bar lever)
launch: ceiling below the random20 MDE: run as declared by the coordinator brief (the step-0 gate is the deciding stage; the slice is DIRECTION only)
transfer: product-only (lite tier pack line)

## Budget (RULE 29)
wall_cap: 1.5 h (replay 5 cells × 180 ≈ 15 min; smoke 3 + random20 generation ≈ 5 min; judge ≈ 5 min)
calls_cap: Haiku 40 / Opus 0 / paid 0
smoke: 3 random20 items (the first 3 sorted ids) at the best cell, same runner as the slice; arm.sh smoke --n-full 20 --marker headpass:
kill_if: any error/empty answer, reasoning tokens > 0 or <think>, smoke FAIL, an identity check (I1, I2 ≥ 170, I3 ≥ 178) failing
checkpoint: step 0 gate (below) before any generation
subset_step0: n/a (step 0 is 0-LLM on all 180)

## Precheck (S2 of the smoke ladder; 0 calls)
token_projection: 1000 (LITE5 smoke mean 738 + ≤ 300 extra appended at x2)
token_budget: 1647.67 (LITE5 OFF smoke mean 447.67 + 1200 = the widest cell's budget)
disk_peak_gib: 0.1 (APFS clone ≈ 0 + replay lines ≈ 30 MB + traces; MacBook floor 5 GiB)
off_baseline: lite5-180-on-<pack>-s42 (LITE5-180 ON traces = the X2b reference rows, MacBook)
call_pattern: Haiku 5.5-low N=4 shards both orders on random20, arm vs gold (40 calls); reference = LITE5-180 ON Haiku rows (not re-judged)
lane: mac-gen
opus_clause: none
wall_cap_h: 1.5
parallelism: 1
run_type: 4b-patch

## Stages and rules
0. Step-0 gate (0 LLM, all 180, MacBook): I1–I3 hold, then per cell: fact-in-context F (gate_x2b rule), articles kept (distinct titles in kept), prompt tokens p50 / max, items whose kept list or prompt changed vs c1, health-strict appended failing onHealthTopic. **PASS** if some cell has F ≥ F(c1) + 15 AND paired p50 of (cell promptTokens − c1 promptTokens) ≤ +900 AND 0 health-strict failures (F(c1) is the same-instrument baseline; if I2 gives F(c1) = 97 this is the brief's 97 + 15 = 112). Best cell = the highest F among passing cells; ties → lower prompt p50. FAIL → stop, 0 generation, 0 Haiku.
1. Smoke (only on PASS): 3 items at the best cell (requests = LITE5-180 ON rows, runId litereach2-smoke-s42, env of the best cell), smoke.verdict.json PASS for this sha.
2. Generate random20 at the best cell: requests = the LITE5-180 ON request rows of the 20 ids, only runId changed (litereach2-<cell>-r20-s42); same model (Qwen3-1.7B Q4_K_M b139949c…), adapter be/adapter-lite5.ts 5785ffc4…, b11010 --reasoning off, seed 42, -t 4, mmbert :8094, MacBook, one server (busy.sh). Run gate: 20 rows, 0 errors, 0 empty, 0 reasoning tokens, no <think>; kept list per item = the step-0 replay's best-cell kept list on ≥ 18/20.
3. Haiku 5.5-low N=4 both orders, arm vs gold (bench boar-eval/bench/selftest/<pack>, fail-closed check_judgments.py; 40 calls). Paired vs the LITE5-180 ON Haiku rows of the same 20 ids; estimator = packs-l2/tools/l2_agg.py (per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11).
4. **Verdict (frozen; Haiku, dev, n 20):** **LEVER-shaped** if Δ ≥ +0.03 AND CI low > 0; **DIRECTION-POSITIVE** if Δ > 0 otherwise; **DIRECTION-NEGATIVE** if Δ ≤ 0. Split (declared) reported with n. No adoption from this arm.
- One generation; no rerun except an infrastructure error before the first token.

## Stop rules and budget
MacBook disk ≥ 5 GiB, one llama-server at a time (busy.sh), never stop the :8094 detector; none left running. Haiku ≤ 40, Opus 0, 0 paid. No git push; git -C rnd commit of the arm files allowed.

## Outputs and exposure
arms/litereach2/LITEREACH2.md (≤ 50 lines, cites this sha), aggregates/{step0.json, r20.json}, tools/, runs/. Self-tests are public (bench/selftest); no blind/ read; rnd/veil/ never read. QUEUE row (tools/qrow.sh, tag main), BACKLOG LITE-TIER row.
