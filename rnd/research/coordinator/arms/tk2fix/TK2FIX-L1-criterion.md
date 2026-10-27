# TK2FIX-L1: does the sources patch v2 (fact chunk kept 35 -> 44 on the 180 self-tests, 0 own-pack drops) move the judged score of the 4B claim build on the 180? (frozen 2026-10-16 03:1x, TK2FIX-L1 agent; Haiku, dev)

Frozen before any TK2FIX-L1 generation or judge call. Arm = TK2-FIX v2 exactly as step 0 replayed it (TK2FIX-step0-criterion.md f7193cc4…; TK2FIX-STEP0.md PASS): tree kiln-local/be-0cfd4a77-cut7-tk2fix = cut 7 (0cfd4a77 + PATCH_SHA256 0fba26b8…) + tools/tk2fix.vs-cut7.patch 6cd09ca64067bd82bd2ddb51fa6bbb3be53ae7f99670e476fe73e7aedf4925ea (src identical to cut7 src + this patch, checked 03:0x; assets/modules identical); runner dir be/ added = cut 7's be/ (adapter.ts 6298e5d3…, same app-shims, node_modules symlinked to cut 7's), marker file TK2FIX_PATCH_SHA256.

## Tags
Tags: none
Ruleset: 30

## Question
Step 0 (0 calls) showed v2 adds the fact chunk to the kept context on 9 items (+9/−0) and changes kept lists on 34 items (factbook 13, simplewiki 17, medlineplus 4), with the five SE packs and firstaid identical to cut 7. Does that reach gain show up in the Haiku-judged score of the 4B with its pack (vs the SELFTEST-SCORES with-pack rows = cut 7)? Use: whether the engine PR ships v2 (cards' lines only if it does).

## Fixed inputs
- ON: requests tk2fix-l1-<pack>-s42 (9 × 20) = packs/selftest-runs/st-<pack>-cut7-s42.requests.jsonl with only runId and config.arm ("tk2fix-cut7") changed (l1/tools/mkreq.py asserts it): 4B qwen3-4b-instruct-2507-q4km, seed 42, claim settings quickFirst true / alwaysComplete false, kit = boar-crypto + boar-wikivoyage-en + the item's pack (same sha256 pins). Runner l1/tools/run_gen.sh = packs/tools/run_selftest.sh with the tree, adapter pin and ARM changed (same env: wave3:wave2:wave1 pack dirs, ship profile, mmbert detector :8094 v3b head, b11010 llama-server CPU -t 4, MacBook M1 Pro = the reference host).
- OFF (not regenerated, not re-judged): the 4B with-pack traces + Haiku 5.5-low rows packs/selftest-runs/st-<pack>-cut7-s42.{traces,judgments}.jsonl (SELFTEST-SCORES; MacBook, same tree minus the patch, 10-12/13). Same bench boar-eval/bench/selftest/<pack>, judge model/effort, both orders, same 180 ids.
- Known nuisance: the prompt carries the device date ("Today is …"), 10-12/13 in OFF vs 10-16 in ON, on all 180 items; on the 146 kept-identical items ON − OFF therefore measures date + re-sampling noise (declared null control below).

## Power
expected_delta: +0.005…+0.02 raw ratio pooled (source: TK2FIX-STEP0.md "HEADPASS conversion 0.11–0.17 per newly present chunk projects ≈ +0.005…+0.008"; BACKLOG row 4 expected +0.00…+0.02; per gained item ≈ +0.135 (4B X2b newly-present cell, LITE5-180))
n: 180 (9 packs × 20, public self-tests)
seeds: 1
mde: ≈ 0.03 raw at n = 180, one seed, Haiku (4B X2b − S CI half-width ±0.020 at n = 180)
slice: n/a (full 180; the arm changes 34 items only, a random20 slice would hold ≈ 4)
l1_futility: n/a (Haiku is the deciding judge on this dev set; Opus 0)
reopen: n/a (follow-up of TK2FIX step 0, BACKLOG row 4)
split (declared): (a) per pack (9) ON − OFF; (b) fact-kept-gained (the 9 ids of l1/splits.json e28e4704…: medlineplus-007, factbook-001/002/004/009/017/019, simplewiki-016/020) vs rest (171); (c) descriptive: kept-diff (34) vs kept-same (146, the date/re-sample null control).
Note: expected_delta < mde: the arm can only show LEVER if the gain is far above the reach projection; SMALL/NO is the expected reading, and the 9-id split is the mechanism check.

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: 9 newly kept fact chunks / 180 × 0.18 = +0.009 pooled (expected 9 / 180 × 0.11 = +0.0055); plus any effect of the 25 other kept-diff items (unsigned)
bar_ceiling: n/a (v0.1 60/60 identical and v0.2 kit not replayable here; product/engine-PR arm, not a bounty-bar lever)
launch: ceiling < mde, launched anyway as the step-0 follow-up the coordinator briefed (BACKLOG row 4, "smoke + Haiku L1 re-score of the 180"); the decision it feeds is ship/no-ship of a retrieval fix, and a harm check (Δ < 0, CI high < 0) is the main read
transfer: product-only (pack line; engine PR)

## Budget (RULE 29)
wall_cap: 1.5 h (180 generations ≈ 15 s + 9 server loads ≈ 50 min; judge ≈ 10 min)
calls_cap: Haiku 720 / Opus 0
smoke: 5 factbook items (001, 002, 004, 009 kept-diff; 003 kept-same = identity anchor vs the reference answer), run id tk2fix-l1-smoke-s42, scored with `arm.sh l1/arm-tk2fix-l1.conf smoke <traces> --n-full 180` (no marker: the patch has no reason code)
kill_if: any error/empty answer, reasoning tokens > 0, projected wall > 2.25 h; checkpoint below
checkpoint: after the first 3 packs in the generation order (boar-medlineplus-en, boar-factbook, boar-simplewiki-en = the 3 packs step 0 changed, 60 items): KILL (0 Haiku, stop) if kept-diff share (ON kept (title, section) list ≠ OFF trace kept list) < 15 % (step 0 expects 34/60 = 57 %)
subset_step0: n/a

## Precheck (S2 of the smoke ladder; 0 calls)
token_projection: 389 (OFF mean timing.promptTokens on the 5 smoke ids) / token_budget: 789 (projection + 400; keep budget 700 caps the context)
disk_peak_gib: 0.3 (traces + logs + 9 new 20 MB app dirs; MacBook free 6.5 GiB, floor 5)
off_baseline: packs/selftest-runs/st-<pack>-cut7-s42 (reference traces; identity: kept identical on the 146 kept-same ids expected ≥ 140)
call_pattern: Haiku 5.5-low N=4 shards, both orders, ON vs gold on the 180 (360 calls; preflight probe disabled, PREFLIGHT_PROBE_IDS=0); OFF rows reused; 0 Opus; 0 paid
lane: mac-gen
opus_clause: none
wall_cap_h: 1.5
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. Smoke (5 items) -> smoke.verdict.json PASS for this sha, else stop.
2. Generate on the MacBook, one llama-server at a time (headpass-st/tools/busy.sh), per pack in the order medlineplus, factbook, simplewiki, travel, ethereum, bitcoin, health-se, outdoors, firstaid. Per-run gate (l1/tools/gate.py run): 20 rows, ids = OFF ids, 0 errors, 0 empty answers, 0 reasoning tokens. FAIL -> stop.
3. Checkpoint after pack 3 (0 calls): rule in Budget.
4. 0-call gate + precheck on the 180 (l1/tools/gate.py all): G0 as stage 2 on all 180; G1 (precheck) kept-diff vs OFF traces ≥ 25 and ≥ 90 % of them inside the 3 changed packs (step 0: 34, all in those packs; fewer = the generation path does not run the patch -> stop, 0 Haiku); G2 kept identical to OFF on ≥ 140 of the 146 kept-same ids (descriptive beyond that: route/tier/health-path differences reported). FAIL -> stop.
5. Haiku 5.5-low N=4 both orders, ON vs gold per pack (bench boar-eval/bench/selftest/<pack>, deepthink/tools/shard_judge.sh, fail-closed check_judgments.py; 360 calls). Estimator = packs-l2/tools/l2_agg.py (load/setstats/paired unchanged: per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId). Report: paired Δ(ON − OFF) raw + above-min with CI, W/T/L vs gold, head-to-head (items ON score >/=/< OFF score), per pack, the 9-id split vs rest, kept-diff vs kept-same; p50 total ms, ttft, prompt tokens, answer words ON vs OFF.
6. **Verdict (frozen; Haiku, dev 180):** **LEVER (Haiku, dev 180)** if paired Δ(ON − OFF) raw ≥ +0.03 AND CI low > 0; **SMALL (Haiku, dev 180)** if CI low > 0 but Δ < +0.03; **NO (Haiku, dev 180)** otherwise. Descriptive harm flag: CI high < 0 (pooled, or the 34 kept-diff items) = "HARM" note on the PR decision. No adoption from this arm; the ship call is the coordinator's.
- One generation per pack. No rerun, except after an infrastructure error before the first token.

## Stop rules and budget
MacBook disk ≥ 5 GiB (runner floor), one llama-server at a time, never stop the :8094 detector or anything else; none left running at the end. Haiku ≤ 720, Opus 0, 0 paid. No git push; `git -C rnd commit` of the arm files allowed. Never read blind/ or rnd/veil/ (v0.2 no-harm stays skipped).

## Outputs and exposure
`arms/tk2fix/TK2FIX-L1.md` (≤ 50 lines, cites this sha), `aggregates/tk2fix-l1.json`, `l1/` (tools, conf, splits, runs: requests + traces + judgments). Self-tests are public (bench/selftest): no EXPOSURES row. QUEUE row (tools/qrow.sh, tag main), BACKLOG row 4 updated, CLOSED.md row only if NO.
