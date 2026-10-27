# LITETHINK: does thinking ON (budget 256 / 512) help the lite 1.7B + HEADPASS-X2b on selftest20? (frozen 2026-10-16 15:0x, Haiku, dev)

Frozen before any judged LITETHINK run. Mechanism = LITE5-180 ON exactly (1.7B + X2b; LITE5-180-criterion.md, tree kiln-local/be-0cfd4a77-cut7-headpass-x2 PATCH_SHA256 0fba26b8…, adapter be/adapter-lite5.ts 5785ffc48240f839…, model shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf, b11010 llama-server -t 4, seed 42, MacBook M1 Pro, mmbert detector :8094) with ONE change: thinking ON. Server: BOAR_SERVER_EXTRA_ARGS="--reasoning-budget B" (no "--reasoning off"); engine fast path sends thinking_budget_tokens = FAST_THINKING_BUDGET. B = 256: the X2b tree as is (stock FAST_THINKING_BUDGET 256). B = 512: tree ...-x2-t512 = APFS clone + litethink512-on-x2.patch (sha in litethink512-on-x2.patch.sha256; answer.ts FAST_THINKING_BUDGET 256 -> 512, max_tokens +256). Runner tools/run_lt_gen.sh (asserts tree/adapter/patch shas and the budget constant).

## Tags
Tags: none
Ruleset: 30

## Question
The lite tier runs the 1.7B with thinking OFF. LITE6: the residual loss vs the 4B is mostly "thin" (53 %) and "not_read" (22 %), invented 17 %. Does a short think pass before the answer (budget 256 or 512) raise the 1.7B + X2b's judged quality on selftest20, at an acceptable time cost? Use: lite-tier default for FAST_THINKING_BUDGET on the 1.7B (product-only).

## Fixed inputs
- Requests: runs/litethink-t<B>-st20-<pack>-s42.requests.jsonl (tools/mkreq.py): the LITE5-180 ON rows on the 20 lite2/selftest20.ids with only runId changed (asserted).
- No-think arm (not regenerated, not re-judged): LITE5-180 ON traces + Haiku 5.5-low judgments on the same 20 ids (lite5/runs/180/lite5-180-on-<pack>-s42.*). Same bench (boar-eval/bench/selftest/<pack>), same judge model/effort, same reference answers.
- Host load differs from the LITE5-180 run (MacBook load ≈ 16-19 now): the time clause compares against the LITE5-180 ON p50 on the 20 ids (6.54 s total) and is reported with this caveat.

## Power
expected_delta: 0…+0.04 raw (source: THINK4B +0.026 (−0.013…+0.068) on the 4B V-para, THINK4B-V02 +0.009; DEEPTHINK +0.093 on the 35B; the 1.7B's thin bucket may not move with thinking)
n: 20 (selftest20)
seeds: 1
mde: ≈ 0.04-0.05 raw at n = 20, Haiku (LITE5 CI half-width ±0.05)
slice: selftest20 (lite2/selftest20.ids)
l1_futility: n/a (Haiku is the deciding judge here; Opus 0)
reopen: n/a

## Ceiling (RULE 29; 0 calls)
ceiling: LITE6 gap 1.7B X2b vs 4B X2b = −0.065 mean; thinking can at most close part of not_read + invented (39 % of the loss) and some thin -> ≤ +0.04 plausible
bar_ceiling: n/a (pack self-tests, lite tier)
launch: coordinator brief 2026-10-16 (LITE-THINK; MacBook generation lane)
transfer: product-only (lite tier)

## Budget (RULE 29)
wall_cap: 1.5 h (40 generations ≈ 10-15 s + 18 server loads; judge ≈ 15 min)
calls_cap: Haiku 80 / Opus 0
smoke: runs/smoke/litethink-t{256,512}-smoke-<pack>-s42 (re-run 14:53-14:55 as one file per pack; the 13:06 smoke failed on mixed runId/config in one file): 3/3 per budget, 0 errors, 0 empty/cut, reasoning 89/128/163 tokens (≤ B), gate.py PASS, total p50 9.0 s (512) / 9.2 s (256)
kill_if: > 1 empty/cut answer OR reasoning 0 on ≥ 3 LLM items, per budget (gate.py KILL=1) -> KILL that budget, 0 Haiku for it
checkpoint: n/a
subset_step0: n/a

## Precheck (0 calls)
token_projection: 1037 (smoke mean promptTokens, both budgets) / token_budget: 1415 (LITE5-180 ON p50 815 on the 20 + 600)
disk_peak_gib: 0.05 (traces + logs; MacBook free 6.2 GiB, floor 5)
off_baseline: lite5-180-on-*-s42 (LITE5-180, MacBook, Haiku rows)
call_pattern: Haiku 5.5-low N=4 shards, both orders, think arm vs gold, per pack (deepthink/tools/shard_judge.sh, PREFLIGHT_PROBE_IDS=0), 2 × 20 = 40 per budget, 80 total; 0 Opus; 0 paid
lane: mac-gen
opus_clause: none
wall_cap_h: 1.5
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. Generate on the MacBook, one llama-server at a time (busy.sh), B = 512 first then 256, per pack. Per budget: tools/gate.py B (per item: 0 errors, non-empty, no `<think>` in answer, LLM items 0 < reasoning ≤ B + 10, no length cut) and KILL=1 gate.py (kill_if). Per-item gate fails other than kill_if are reported, not rerun.
2. Judge each surviving budget: Haiku 5.5-low N=4 both orders vs gold, fail-closed check_judgments.py.
3. Estimator = packs-l2/tools/l2_agg.py (per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId), as lite5/tools/agg_180.py. Paired Δ(think − no-think) raw with CI per budget, plus 512 − 256.
4. Split (declared): LITE6 bucket of the item (lite6/aggregates/lite6.json `items[].bucket`): thin vs invented vs rest. Descriptive: reasoning tokens (p50/p90/max), budget-hit share (reasoning ≥ B − 8), total/ttft p50, answer words p50, think vs no-think.
5. **Verdict per budget (frozen; Haiku, dev, n = 20):** **LEVER-shaped (Haiku, dev)** if Δ ≥ +0.03 AND CI low > 0 AND p50 total ≤ 2 × the no-think p50 (≤ 13.08 s); **DIRECTION** if Δ ≥ +0.03 but CI low ≤ 0 or the time clause fails; **FLAT** if −0.03 < Δ < +0.03; **NEGATIVE** if Δ ≤ −0.03. No adoption from this arm (a LEVER-shaped result needs the 180 before any default change).
- One generation per budget and pack; rerun only after an infrastructure error before the first token.

## Stop rules and outputs
MacBook disk ≥ 5 GiB, one llama-server at a time, :8094 untouched, no server left running. Haiku ≤ 80, Opus 0, 0 paid. No git push; commit the arm files in rnd. Outputs: LITETHINK.md (≤ 50 lines, cites this sha), aggregates/litethink.json, gate outputs, traces + judgments under runs/. Self-tests are public; blind/ and rnd/veil/ not read (no EXPOSURES row). QUEUE row (tools/qrow.sh, tag main), BACKLOG LITE-TIER row.
