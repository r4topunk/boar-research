# TK2FIX-L1: sources patch v2 on the 4B, 180 self-tests: NO (Haiku, dev 180), Δ +0.010 (−0.003…+0.024); the 9 fact-gained items +0.190 (+0.059…+0.368), no harm (2026-10-16 03:4x; Haiku 360, Opus 0, 0 paid)

## Frozen inputs
- Criterion `TK2FIX-L1-criterion.md` sha `49beb0c5…e47d` (Ruleset 30), frozen before any run (header says "03:1x": typo, file written 02:5x, before the smoke). Smoke 5 factbook items: PASS (smoke.verdict.json, projected 0.51 h, 10.2 s/unit, mean prompt 612.6 ≤ 789; identity PASS). Kept lists = step-0 replay v2 on 5/5.
- ON: tree kiln-local/be-0cfd4a77-cut7-tk2fix (src = cut 7 src + tk2fix.vs-cut7.patch 6cd09ca6…, checked; be/ = cut 7's runner, adapter 6298e5d3), the reference requests with only runId/arm changed (l1/tools/mkreq.py asserts it). 4B, seed 42, claim settings, MacBook, same env as the reference.
- OFF: SELFTEST-SCORES with-pack traces + Haiku rows (packs/selftest-runs/st-<pack>-cut7-s42), MacBook, same tree minus the patch. Reused, not re-judged.

## Step 1: code checks (scratch copy of wt/pr1 8ac9eb7a + the v2 patch)
- `git apply --check` on wt/pr1: OK. `tsc --noEmit`: 0 errors.
- `vitest run src/rag src/routing`: 61/62 files pass. The failing file is the patch's own new `wikiPack.attribution.test.ts`. It fails because wt/pr1's `scripts/build-wiki-pack.mjs` does not know source codes 9–12. With the T-K2 builder hunk added (wt/packs builder, saved as tools/tk2-builder.vs-pr1.patch, 34 lines, applies on wt/pr1): **62/62 files, 955/955 tests**. **The PR must carry both patches.**

## Gates (0 calls)
- Per-run 9/9 PASS (0 errors, 0 empty, 0 reasoning tokens). Checkpoint (medlineplus, factbook, simplewiki first): kept-diff 34/60 = 0.567 ≥ 0.15, CONTINUE.
- Gate 180 PASS (l1/gate.json): kept-diff vs OFF 34, all in the 3 changed packs, the same 34 ids as step 0 (34/34). Kept identical on 146/146 kept-same ids. Route/tier diffs 0.
- **144/180 answers are byte-identical to OFF**, even though the prompt date differs (10-12/13 vs 10-16).

## Δ (Haiku 5.5-low N=4, both orders; l2_agg.py per-item bootstrap, B 2000, seed 11)
| group | n | ON / OFF raw | Δ raw (CI) | Δ above-min (CI) | h2h >/=/< |
|---|---|---|---|---|---|
| **pooled** | 180 | 0.502 / 0.493 | **+0.010 (−0.003…+0.024)** | +0.012 (−0.004…+0.029) | 58/65/57 |
| SE | 100 | 0.494 / 0.490 | +0.004 (−0.006…+0.014) | +0.004 | 28/44/28 |
| topic | 80 | 0.512 / 0.496 | +0.016 (−0.009…+0.046) | +0.020 | 30/21/29 |
| **fact-kept-gained (9)** | 9 | 0.573 / 0.382 | **+0.190 (+0.059…+0.368)** | +0.238 | 7/1/1 |
| rest | 171 | 0.498 / 0.499 | −0.000 (−0.010…+0.009) | −0.001 | 51/64/56 |
| kept-diff (34) | 34 | 0.562 / 0.515 | +0.047 (−0.005…+0.110) | +0.058 | 17/8/9 |
| kept-same (null control) | 146 | 0.488 / 0.487 | +0.001 (−0.008…+0.010) | +0.001 | 41/57/48 |

- Per pack Δ raw: factbook **+0.058 (+0.014…+0.105)**, travel +0.016, simplewiki +0.013 (−0.057…+0.122), bitcoin +0.009, outdoors +0.002, ethereum +0.001, medlineplus −0.001, firstaid −0.006, health-se −0.009. All CIs except factbook straddle 0.
- On the six packs whose retrieval is unchanged, the Δ is judge noise around 0. The kept-same null is +0.001.
- W/T/L vs gold: ON 1/0/179, OFF 0/0/180.

**Reading.** The mechanism works where the patch acts: the 9 items that gain the fact chunk gain +0.19 (7 better, 1 worse). On the other 25 kept-diff items the effect is about 0 (−0.007, −0.046…+0.029, b/w 10/8). The pooled gain is close to the step-0 projection (+0.005…+0.008, ceiling +0.009) and below the MDE: 9/180 items cannot move the 180 mean by 0.03. There is no harm signal: pooled CI high +0.024 > 0, kept-diff CI high +0.110 > 0, and medlineplus (the only pack where v2 replaced own-pack candidates) is −0.001.

## Cost (p50, ON vs OFF)
- 180 items: prompt tokens 471.5 vs 453.5; total 8.06 vs 8.30 s; ttft 5.56 vs 5.69 s; answer words 50 = 50.
- 34 kept-diff items: +86 prompt tokens paired; total 10.2 vs 11.9 s.
- Wall: smoke 2 min, generation 30 min (9 runs), judge 8 min (360 calls, 0 failures).

## Verdict
**NO (Haiku, dev 180)** by the frozen rule. Pooled Δ +0.010, CI low −0.003 ≤ 0.
- Expected and pre-declared: expected_delta < MDE, launched as the step-0 follow-up.
- Not a harm: harm_flag false. The declared mechanism split is positive (+0.190 on the 9 fact-gained items; factbook +0.058 with CI > 0).
- Ship call (coordinator): v2 is a retrieval correctness fix with no measured cost. On the self-tests it is score-neutral pooled and helps where it acts.
- If it ships: wt/pr1 needs tk2fix.vs-cut7.patch + tk2-builder.vs-pr1.patch. The v0.2 kit no-harm is still unrun (blind/, needs a coordinator-scoped exception).

## Files
`TK2FIX-L1-criterion.md` + `.sha256`, `smoke.verdict.json`, `aggregates/tk2fix-l1.json`, `tools/tk2-builder.vs-pr1.patch`. `l1/`: arm-tk2fix-l1.conf, splits.json (e28e4704…), checkpoint.json, gate.json, tools/{splits.py, mkreq.py, run_gen.sh, gen.sh, gate.py, judge.sh, agg.py}, runs/ (requests, traces, Haiku judgments, logs).
- Public self-tests only: no blind/ or rnd/veil/ read, no EXPOSURES row.
- MacBook free 6.5 → 5.5 GiB: this arm used ≈ 0.1 GiB (traces + 9 × 20 MB app dirs); the rest is another process.
- No servers left running; the :8094 detector was untouched.
