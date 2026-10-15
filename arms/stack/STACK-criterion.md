# STACK: the pack stack that survived step 0 — keep rule X3 + per-pack quota under "all packs installed" — does it move quality versus today's peers engine? (frozen 2026-10-13 16:0x, coordinator)

## Tags
Tags: none

## Question
HANDOFF-2026-10-13 §4.4 planned router + dense extra + keep rule. What survived: dense extra NO (R46); top-1 routing closed (R48); crowding cost measured small (CROWDQ: P − S −0.016 (−0.033…−0.001) pooled; SE −0.033 (−0.055…−0.011), topic +0.004); keep rule X3 recovers reach at 0 harm (GROUND-ST: fact chunk kept 43 → 54, article 68 → 95 single-pack; FAIL by one item on the chunk bar, R47); quota 2/6 recovers 5 of the 22 crowded article-kept items (PACKROUTE Q). Arm **X = STACK-lite = packGround "perpack" + packRoute "quota"** (both 0-LLM, engine-side), all 9 packs + kit installed. Control **P = CROWDQ's peers run** (cut 7, all 9 installed; traces + Haiku rows arms/crowdq/runs/st-<pack>-cut7-all9-s42.*). Reference **S** = single pack (SELFTEST-SCORES). Use: the product recommendation for the "many packs installed" setup and the closing number of the pack stack.

## Fixed inputs
- Items: the 180 public self-test items; no-harm: v0.1 public 60 (quality run, see stage 1b) and the kit replays (v0.1 60, v0.2 110 script-only).
- Tree for generation: runner-local/be-0cfd4a77-cut7-stack = cut 7 (runner-local/be-0cfd4a77-cut7) + the packGround patch (arms/groundst/packground2.vs-dt512.patch, perpack mode) + the quota part of the packRoute patch (arms/packroute2/packroute2.vs-dt512.patch, mode "quota" only), rebased onto cut 7; default settings byte-identical to cut 7 (vitest/tsc; OFF replay identical to P's retrieval on 180/180). Requests = CROWDQ's all-9 requests with config.settings += {packGround: "perpack", packRoute: "quota"}; runId st-<pack>-cut7-stack-s42.
- Replay tree for step 0: wt/groundst + the quota hunks (or wt/packs + perpack hunks) — whichever is smaller; OFF identical to PACKROUTE's peers replay 180/180.
- Judge: Haiku 5.5-low N=4 both orders (360 on the 180; 240 on v0.1 OFF/ON); Opus N=4 on a near-miss (360 + P's 360).

## Power
expected_delta: +0.03 raw X − P on the 180 (source: CROWDQ crowding cost −0.016 of which the quota recovers ≈ 1/4 by reach; GROUND-ST keep rule +11 chunks / +27 articles kept single-pack ≈ ST2's +18 chunks → +0.017 at the same conversion; SE family expected +0.03…+0.05, topic ≈ 0)
n: 180
seeds: 1 (deterministic)
mde: ≈ 0.03 raw paired at n 180 (Haiku; Opus on a near-miss)
slice: n/a
l1_futility: n/a
reopen: n/a (new combined configuration; components cite R46/R47/R48)
split: paired Δ by pack family (SE vs topic), declared; expected gain in SE
NOTE: expected_delta ≈ mde: the arm can return "not decided"; that outcome closes the pack stack with the component numbers as the product note (no further stack arms on the 180).

## Stages and rules
0. Step 0 (0 calls): replays on the 180 (all 9 + kit) P vs X: **G1** fact article kept ≥ 56 (P 46; S 68) and fact chunk kept ≥ P + 8; **G2** kit no-harm (RULE 26): lost-context 0 on v0.1/v0.2 vs kit-only (P has 1 + 3: X must not add any; the ids under P are allowed to persist only if the same source is lost for the same reason — report), empty-kept over OFF-retrieving not up, v0.1 gold kept ≥ 12, v0.2 resolvable gold kept ≥ 3 (P has 3), tokens ≤ cap; **G3** p50 ≤ 1.3 × P. FAIL → FAIL at step 0.
1a. Generation X on the 180 (MacBook, nohup, resumable); precheck ≥ 20 % changed prompts vs P; Haiku N=4 both orders; paired Δ X − P pooled and by family; X − S; same_answer field.
1b. Quality no-harm on v0.1 public 60: OFF (cut 7, kit only, settings absent) and ON (stack settings, kit only) generations on the stack tree, Haiku N=4 both orders (240), paired Δ; rule: CI high of (ON − OFF) ≥ −0.03 → no harm; else X is not recommended as a default regardless of 1a.
2. Verdict: **LEVER** (CI low > 0 and Δ ≥ +0.03) → recommended default for the many-packs setup + re-score the 9 packs' cards with/without under X; **SMALL** (CI low > 0, Δ < 0.03) → optional setting, product note; **NO** / "not decided at MDE 0.03" → pack stack closed with the component numbers; near-miss (Haiku Δ > 0 with CI through 0 and Δ ≥ 0.015) → Opus N=4 on X and P (720).

## Stop rules and budget
0 paid API. MacBook only. Never two 4B generation jobs at once. Disk ≥ 8 GiB (tree copy ≈ 220 MB; traces ≈ 20 MB). Haiku 600 (+ 720 Opus on a near-miss).

## Outputs and exposure
arms/stack/{GATE.md, STACK.md, tools/, aggregates/, runs/, stack.vs-cut7.patch + .sha256}; v0.2 replay under $HELDOUT_DIR/bench-v02/runs-packs/stack-v02-kit.jsonl (script-only; EXPOSURES row). QUEUE rows per stage.
