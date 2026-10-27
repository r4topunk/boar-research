# LITEREACH2-180: does the wider X2b append budget (b20 = 1200/4/8) beat X2b's 600/2/4 on the lite 1.7B over all 180 public self-tests? (frozen 2026-10-16 by the LITEREACH2-180 agent; Haiku, dev 180)

Frozen before any LITEREACH2-180 run. Follow-up of LITEREACH2 (criterion v2 2f65ddd09d27a92ca931af37799860e3088084102434d5d3ff05cecec4e455f4; step 0 PASS: fact in context 97 -> 119/180, +458 prompt tokens p50; random20 Haiku +0.032 (-0.006...+0.070) DIRECTION-POSITIVE). Mechanism = HEADPASS-X2b (settings packHeadPass "a2" + packDense2 "append-budget") with its three constants set by env (litereach2-env.patch, e4c65b55...).

## Tags
Tags: none
Ruleset: 30

## Question
On all 180 self-tests, does b20 (HEADPASS_BUDGET_TOKENS 1200, DENSE_D 4, MAX_APPEND 8) raise the 1.7B's judged score over X2b's 600/2/4 (the LITE5-180 ON rows), at MDE about 0.03? Use: the lite tier's X2b budget setting (keep 600/2/4 or widen).

## Fixed inputs
- Arm B20: requests litereach2-b20-180-<pack>-s42 (9 files x 20) = the LITE5-180 ON request rows (lite5/runs/180/lite5-180-on-<pack>-s42.requests.jsonl) with only runId changed (tools/mkreq.py asserts it), env BOAR_LR2_BUDGET_TOKENS=1200 BOAR_LR2_DENSE_D=4 BOAR_LR2_MAX_APPEND=8.
- Same tree, adapter, model, runner and env as LITEREACH2 r20: kiln-local/be-0cfd4a77-cut7-litereach2 (PATCH_SHA256 0fba26b8..., LITEREACH2_PATCH_SHA256 = sha of litereach2-env.patch), be/adapter-lite5.ts 5785ffc4..., Qwen3-1.7B Q4_K_M b139949c..., b11010 llama-server --reasoning off, seed 42, -t 4, mmbert detector :8094, tools/run_gen.sh 1200 4 8.
- Host: MacBook (M1 Pro), the host of the control rows. The mini's X2b tree copy (<runner>/kiln/be-0cfd4a77-cut7-headpass-x2, QUANTLITE) has the v3proto sidecars but lacks the env patch, and a cross-host run adds an answer re-sample (LITE5 hostid: answer text 5/20 cross-host vs 18/20 same-host), so the MacBook lane is used (one server, busy.sh, disk floor 5 GiB).
- Control (not regenerated, not re-judged): LITE5-180 ON (= 600/2/4) Haiku 5.5-low rows lite5/runs/180/lite5-180-on-<pack>-s42.judgments.haiku55-low.jsonl and their traces. Descriptive references: LITE5-180 OFF (1.7B plain), 4B plain (packs/selftest-runs/st-<pack>-cut7-s42.judgments.jsonl), 4B X2b (headpass-st/gen-x2b/st-<pack>-cut7-headpassx2b-s42.judgments.jsonl).
- Fact in context (trace rule = LITE5 fic rule): split-x2b S_present OR an oracle fact chunk (oracle-st/tools/oracle-facts.json) of the item's pack among the trace's appended ids (headpass:add / headpass:dense:add codes). Step-0 b20 replay = runs/step0/b20.<pack>.jsonl (F 119, fic 119).

## Power
expected_delta: +0.010...+0.025 raw pooled (source: 22 items newly gaining the fact x +0.089 (LITEREACH2 r20 split, n 4) ... +0.173 (LITE5-180 newly-present cell) / 180 = +0.011...+0.021; LITEREACH2 Power ceiling +0.026; random20 +0.032 includes rest +0.018 that should be about 0)
n: 180 (all public self-tests, 9 packs x 20)
seeds: 1
mde: about 0.03 raw at n 180 one seed Haiku (LITE5-180 ON-OFF CI half-width +-0.023)
slice: n/a (full 180)
l1_futility: expected_delta is below the LEVER bar (+0.03): the likely positive outcome is SMALL; declared, run anyway per the coordinator brief (Haiku is the deciding judge on this dev set; no Opus)
split: (declared) (a) items newly gaining the fact at b20 vs c1 in step 0 (gained_vs_c1, 22) vs the rest (158); (b) per pack (9); (c) SE (100) / topic (80). Descriptive: B20 - OFF, B20 - 4B plain, B20 - 4B X2b
reopen: n/a (LITEREACH2 follow-up, LITEREACH2.md Next)

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: +0.026 pooled (LITEREACH2 Power: 22-27 newly gained items x +0.173 / 180); realistic +0.011...+0.021
bar_ceiling: n/a (pack self-tests, lite tier; not a bounty-bar lever)
launch: coordinator brief 2026-10-16 (LITE-REACH2-180)
transfer: product-only (lite tier pack line)

## Budget (RULE 29)
wall_cap: 1.5 h (180 generations about 11 s + 9 server loads about 35 min; judge 360 calls about 10 min)
calls_cap: Haiku 720 (360 expected: 180 items x 2 orders) / Opus 0 / paid 0
smoke: LITEREACH2's 3-item b20 smoke (runs/smoke, same tree/adapter/model/env: 0 errors, 0 empty, 0 reasoning tokens, mean prompt 1426.5 vs budget 1647.67, 7.8 s/unit) re-scored for this sha with arm.sh smoke --n-full 180 --marker headpass: (LITEREACH2's own verdict kept as smoke.verdict.litereach2-v2.json)
kill_if: any error/empty answer, reasoning tokens > 0 or <think>, projected wall > 2.25 h, per-pack run gate FAIL, checkpoint KILL
checkpoint: after the first 3 packs (qa-travel-se, qa-ethereum-se, qa-bitcoin-se = 60 items): KILL (stop generation, 0 Haiku) unless fact-in-context(B20 traces) - fact-in-context(LITE5-180 ON traces) >= +4 on those 60 AND the paired p50 of (B20 - ON) trace promptTokens on those 60 is <= +600
subset_step0: n/a

## Precheck (S2 of the smoke ladder; 0 calls)
token_projection: 1426.5 (LITEREACH2 smoke mean timing.promptTokens at b20)
token_budget: 1647.67 (LITEREACH2: LITE5 OFF smoke mean 447.67 + 1200)
disk_peak_gib: 0.1 (traces + logs + judgments; no new model; MacBook floor 5 GiB)
off_baseline: lite5-180-on-<pack>-s42 (LITE5-180 ON traces and Haiku rows = X2b 600/2/4, MacBook)
call_pattern: Haiku 5.5-low N=4 shards, both orders, B20 vs gold on the 180 (360 calls); preflight live probe disabled (PREFLIGHT_PROBE_IDS=0); 0 Opus; 0 paid
lane: mac-gen
opus_clause: none
wall_cap_h: 1.5
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. Generate on the MacBook, one llama-server at a time (busy.sh), per pack in the order travel, ethereum, bitcoin, health-se, outdoors, firstaid, medlineplus, factbook, simplewiki (tools/gen_chain.sh 180). Per-pack run gate (tools/gate_180.py run <pack>): 20 rows, 0 errors, 0 empty, 0 reasoning tokens, no <think>; kept (title, section) list and appended ids = the step-0 b20 replay on >= 18/20. FAIL -> stop.
2. Checkpoint after pack 3 (tools/gate_180.py checkpoint; 0 calls): rule frozen in Budget.
3. 0-call gate on the 180 (tools/gate_180.py all): G0 as stage 1 on all 180; G1 kept + appended = step-0 b20 replay on >= 170/180; G2 fact in context (trace rule) B20 > ON, reported against the step-0 count (expected 119); G3 paired p50 Delta promptTokens (B20 - ON) <= +600. FAIL -> stop, 0 Haiku.
4. Haiku 5.5-low N=4 both orders, B20 vs gold, per pack (bench boar-eval/bench/selftest/<pack>, fail-closed check_judgments.py; 360 calls). Estimator = packs-l2/tools/l2_agg.py (per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId). Report: paired Delta(B20 - ON) with CI (raw, above-min), splits, b/w; descriptive B20 - OFF, - 4B plain, - 4B X2b; p50 promptTokens, ttftMs, totalMs, decode tok/s, answer words B20 vs ON (same host). Same-host anchor (0 calls): answer text of the 20 LITEREACH2 r20 ids vs the r20 traces (reported, rule unchanged).
5. **Verdict (frozen; Haiku, dev 180):** **LEVER (Haiku, dev 180)** if paired Delta(B20 - ON) raw >= +0.03 AND CI low > 0; **SMALL (Haiku, dev 180)** if CI low > 0 but Delta < +0.03; **NO (Haiku, dev 180)** otherwise. No adoption from this arm (product-only; phone prefill for about +460 tokens not measured).
- One generation per pack. No rerun, except after an infrastructure error before the first token.

## Stop rules and budget
MacBook disk >= 5 GiB, one llama-server at a time (busy.sh), never stop the :8094 detector or anything else; none left running at the end. Haiku <= 720, Opus 0, 0 paid. No git push; git -C rnd commit of the arm files allowed.

## Outputs and exposure
arms/litereach2/LITEREACH2-180.md (<= 50 lines, cites this sha), aggregates/{gate-180.json, checkpoint-180.json, lr2-180.json}, tools/*180*, runs/180/. Self-tests are public (bench/selftest); no blind/ read; rnd/veil/ never read. QUEUE row (tools/qrow.sh, tag main), BACKLOG LITE-TIER row, CLOSED.md row if NO.
