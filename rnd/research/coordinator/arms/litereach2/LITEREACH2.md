# LITEREACH2: wider X2b append budget on the lite 1.7B: step 0 PASS (×2 budget + ×2 dense slots: fact in context 97 → 119/180, +458 prompt tokens p50); random20 Haiku Δ +0.032 (−0.006…+0.070) vs X2b = DIRECTION-POSITIVE (2026-10-16 10:3x; Haiku 40, Opus 0, 0 paid)

Criterion LITEREACH2-criterion.md v2 sha 2f65ddd0… (Ruleset 30). v1 (b418afd6…, kept as .v1.md) failed identity I3 at 175/180 only on the engine device-date line (Wednesday 14 vs Friday 16 October, 5 date-bearing prompts; raw/kept/appended 180/180), as LITEREADERS v1; v2 normalises that line in I3 only, re-frozen before any generation or judge call. The cell numbers below were computed before v2 and are unchanged by it. Smoke (3 items, b20) PASS for v2: 7.8 s/unit, mean prompt 1426.5 ≤ 1647.67.

## Setup
- Tree kiln-local/be-0cfd4a77-cut7-litereach2 = APFS clone of cut7-headpass-x2 (0fba26b8…) + litereach2-env.patch (e4c65b55…): HEADPASS_BUDGET_TOKENS / DENSE_D / MAX_APPEND read from BOAR_LR2_* (unset = 600/2/4). ARM file kept cut7-headpass-x2 so requests = LITE5-180 ON rows with only runId changed (one file per pack: the kit differs per pack).
- Step 0 = headpass-st replay-x2.ts, mode x2b, --tasks-from the LITE5-180 ON traces (1.7B gate decisions + mmbert detector scores), sidecars v3proto. 0 LLM, 7 cells × 9 packs, 6 min.
- Identity: I1 env-unset = env 600/2/4 180/180; I2 c1 appended ids = LITE5-180 ON traces 180/180, fact in context 97 = 97 (per-item 180/180: the replay/trace 97 vs 102 gap of HEADPASS-X2b is gone with --tasks-from); I3 clone vs headpass-st x2b 180/180 (date-normalised; 175 raw).

## Step 0 (180, replay approxTokens; Δprompt paired vs c1)
| cell (budget/D/cap) | fact in ctx | ΔF | articles kept (mean) | kept chunks | appended | budget-drop items | prompt p50 / max | Δprompt p50 / max | changed vs c1 | pass |
|---|---|---|---|---|---|---|---|---|---|---|
| c1 600/2/4 (= X2b) | 97 | — | 2.12 | 3.68 | 390 | 74 | 973.5 / 1319 | 0 / 0 | — | base |
| b15 900/3/6 | 109 | +12 | 2.76 | 4.79 | 590 | 47 | 1215 / 1650 | +237.5 / +539 | 155 | no |
| **b20 1200/4/8** | **119** | **+22** | 3.32 | 5.81 | 772 | 24 | 1444.5 / 1901 | **+458** / +810 | 155 | **yes** |
| t15 900/2/4 (budget only) | 105 | +8 | 2.43 | 4.20 | 483 | 10 | 1088 / 1650 | 0 / +520 | 74 | no |
| t20 1200/2/4 (budget only) | 106 | +9 | 2.46 | 4.26 | 493 | 0 | 1112.5 / 1650 | 0 / +561 | 74 | no |
Health-strict appended failing onHealthTopic 0 in every cell; lost-vs-c1 0 in every cell. b20 gains: SE 16, topic 6. Budget alone saturates at +9 (the D = 2 slot cap binds); the reach is in the extra dense slots.

## Random20 (seed 888; b20, seed 42, --reasoning off; Haiku 5.5-low N=4 both orders, 40 calls; l2_agg.py, B 2000)
Run gate PASS: 20/20 rows, 0 errors/empty/reasoning/<think>, kept + appended = step-0 b20 replay 20/20.
| cell | n | b20 − X2b (ref, LITE5-180 ON rows) | b20 − 1.7B OFF | b20 − 4B plain | b20 − 4B X2b |
|---|---|---|---|---|---|
| pooled | 20 | **+0.032 (−0.006…+0.070)**, b/w 9/7 | +0.087 (+0.018…+0.172) | +0.009 (−0.069…+0.094) | −0.080 (−0.134…−0.021) |
| split: newly gain the fact | 4 | +0.089 (−0.008…+0.201), b/w 3/1 | +0.033 | −0.071 | −0.138 |
| split: rest | 16 | +0.018 (−0.021…+0.060), b/w 6/6 | +0.100 | +0.027 | −0.068 |
Ratios: b20 0.518, X2b 0.486, OFF 0.431, 4B plain 0.509, 4B X2b 0.598. Prompt changed vs c1 on 19/20 (+0.035).
Cost (MacBook, trace medians on the 20): prompt tokens 913 → 1372 (+459), ttft 6.5 → 9.6 s, total 7.7 → 11.1 s, words 36 → 36.5.

## Verdict (frozen rule)
**Step 0 PASS** (b20 +22 ≥ +15, Δprompt p50 +458 ≤ +900, health 0). **Slice: DIRECTION-POSITIVE (Haiku, dev, n 20)**: Δ +0.032 ≥ +0.03 but CI low −0.006 ≤ 0, so not LEVER-shaped. As the Power block says, n 20 cannot decide a pooled effect of this size (ceiling ≈ +0.026 on the 180). The gain sits where expected (newly gained the fact +0.089, n 4). The rest is +0.018. b20 puts the 1.7B at the 4B plain level on this slice (+0.009) and still −0.080 under the 4B X2b.
Caveats: dev self-tests with agent-written gold; Haiku only; one seed; the ref rows were generated earlier on the same host (LITE5-180 saw 2/20 answers re-sample with the same inputs); prompt +459 tokens ≈ +3.1 s ttft on the desktop, phone not measured (LITE6's estimate is ≤ +5.8 s per +400 tokens on the 1.7B).
Next (coordinator): either a 180 run of b20 on the 1.7B (180 generations + 360 Haiku; ref = the LITE5-180 ON rows) to read the pooled Δ at MDE ≈ 0.03, or keep X2b's 600/2/4 until a phone prefill number prices +460 tokens.

## Files
LITEREACH2-criterion{,.v1}.md + .sha256, smoke.verdict.json, arm.conf, litereach2-env.patch, random20-st180-s888.ids (7b884d76…); tools/{run_step0.sh, step0.py, mkreq.py, run_gen.sh, gen_chain.sh, gate_r20.py, judge_r20.sh, agg_r20.py}; aggregates/{step0.json, gate-r20.json, r20.json}; runs/{step0/, smoke/, r20/} (12 MB). No blind/ read; rnd/veil/ not read. No servers left running (the :8094 detector untouched). MacBook free 5 GiB at the end (floor 5); the clone tree costs ≈ 0 (APFS).
