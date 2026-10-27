# X2B-OFF-MAIN criterion (frozen 2026-10-21, before any generation)

Source: X2B-RETEST.md UNKNOWN ("OFF on MAIN live 77 = the revisit entry's set") and its engine-note candidate (X2b OFF on kit-only installs halves the prompt).
Question: does the engine lose anything on real (non-pack-written-for-the-installed-pack) items when the X2b neighbour-chunk append is off?

## Set
main-live77.ids (77 ids, sha256 89d4501cc2ea3759af672d207fba366bab7af973a22236fb1478aca5329a84b7) = MAIN 97 (v0.1 57 + cooking-se 20 + money-se 20)
minus the 20 ids with reaches_model = false in ruler/divergence-map.json (deterministic layers; divergence-map.json sha256 512a866e...).
Split: 44 v0.1 + 33 qa-cooking-se/qa-money-se ids (MAIN's casual off-pack questions; K1 kit installed, not their own pack). Dev set only.

## System and arms
System = LITEPACKS 1.7B (cut7-headpass-x2+litepacks tree, Qwen3-1.7B Q4_K_M, LITEDECLINE_OFF=5, --reasoning off, seed 42, adapter be/adapter-litedecline.ts), mini, gen slot lock (mini_gen.sh), K1 pack set.
| arm | what | input |
|---|---|---|
| ON (control) | X2b on, the existing mini K1 control | null-cal/control/pool-K1.json (traces lp-screens/control/traces/lpctl-K1-main-s42) |
| OFF | adapter deletes packHeadPass and packDense2 from the answer settings | x2b-off.patch, sha256 a6018c67fa5f10c1a9ddde53ac013ae66b58a8dc54c7b5932647e5bbd3cfe1a7 (same patch as X2B-RETEST) |
Run (cwd arms): `OUT_BASE=$PWD/x2b-retest/main GEN_ONLY=1 bash x2b-retest/tools/run_pool_x2b.sh x2boffmain K1 x2b-retest/main-live77.ids x2b-retest/x2b-off.patch`, then the same without GEN_ONLY and with CRITERION=<this file> to judge.
Fresh generation of all 77 (the 37 MAIN-pool OFF traces of X2B-RETEST are not reused; they are reported only as a nondeterminism check).

## Judge
Haiku 5.5-low, judge.v1-low, N = 4 shards, both orders (deepthink/tools/shard_judge.sh via the runner). Only answers whose text differs from the ON control are judged; byte-identical answers reuse the control judgment.
Cap: 160 Haiku calls (77 x 2 = 154 max, so the cap cannot bind). 0 Opus, 0 paid, 0 phone.

## Metrics (default-mode product, null-cal/tools/labels.py; same as X2B-RETEST)
Per item: R = decline or warned; s_d = 0 if R else s; CEu = CE and not warned.
- U_d(set) = sum s_d / sum sref; paired dU = OFF - ON, item bootstrap B 2000 seed 11, 95 % percentile CI.
- CE-unwarned count (CEu), refusal count (R), changed answers, changed contexts.
- Prompt tokens: mean timing.promptTokens over items with promptTokens > 0 in both arms. Retrieval wall: mean and p50 timing.retrievalMs.
- Reported on MAIN77 (decides), and v0.1-44 / cm-33 (reported only).

## Decision (frozen; read on MAIN77)
1. **"OFF is better"** iff dU > 0 with CI low > 0 (and the safe clause below holds).
2. **"OFF is safe for kit-only installs"** iff dU >= -0.02 AND CI low >= -0.05 AND CEu(OFF) - CEu(ON) <= 2.
3. Otherwise **X2b stays on**.
Rule 1 implies rule 2's clauses must also hold; if rule 1's CI clause holds but CEu rises by > 2, the verdict is rule 3.
Power note: n 77 single seed; the 1.7B s42 vs s43 per-item r is 0.66 on these items (DIVERGENCE-MAP), so a Haiku dU within 0.01 of a bar is reported as borderline, not re-run.

## Sanity (invalidate, not a verdict)
77/77 trace rows, 0 error rows; OFF: 0 "headpass:add" reason codes; items with 0 prompt tokens in ON stay 0 in OFF (deterministic path unchanged).

## Budget
calls_cap: Haiku 160 / Opus 0
opus_clause: none
