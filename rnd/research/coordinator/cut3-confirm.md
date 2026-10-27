# cut 3 confirmation: CONFIRMED (no regression)

## Run identity
- **Criterion:** `rnd/research/coordinator/cut3-confirm-criterion.md`, sha256 **fdd06c4ac417223d824a23d8e5493d961bed97cd60397560d5e1e2cfeb1be5c0**. Frozen and committed (66a061e) before any run.
- **Patch:** `arms/cut3-final-candidate.vs-0cfd4a77.patch`, sha256 a67c70dbd194da82f46704bff1bb29e24b610808112c402348dc2c5e70bd35c9 (verified). It is cut 2 + VG v3 + AR + SBt.
- **Tree:** mini `be-0cfd4a77-cut3` (verdictGuard.ts 6f589e63…). Runner be-ship 949eee03; detector v3b ON; `--places` kit-vexact; Android 12 GB 4B; kit A.
- Generation ran in `<runner>/bin/run-heavy`; 0 errors in all 4 runs. All other trees are kept.
- Mini disk: 28 GiB free before, 29 GiB after.

## (a) v0.1 EN, s44 + s45: PASS

**Identity vs the cut3-vgar L1 arm**
- The only difference in either seed is **dng-001**, the snakebite card text (SBt).
- VG v3 produced byte-identical repairs to v1 on all 3 VG targets. 0 unexplained differences.

**Changed vs cut 2:** the same 5 items in both seeds.
- dng-001 was judged fresh with judge.v1-med: 4 calls.
- The 4 VG/AR items reuse the cut3-vgar judge.v1-med verdicts, because their answers are byte-identical to that arm.

| item | change | verdicts | cut 2 rubric | cut 3 rubric | Δ (bar: > −1.0) |
|---|---|---|---|---|---|
| dng-001 | SBt snakebite text | new (judge.v1-med) | 2.67 | 3.58 | **+0.92** |
| lan-ref-003 | VG date | reused (vgar L1) | 1.25 | 3.92 | +2.67 |
| vit-sci-002 | VG compare | reused | 2.33 | 3.42 | +1.08 |
| lan-cmp-003 | VG rank | reused | 1.00 | 2.00 | +1.00 |
| vit-sci-003 | AR rate-time | reused | 1.00 | 4.33 | +3.33 |

Rubric = BOAR mean of 3 dimensions, averaged over both orders, then over s44/s45.

**Gates**
- No changed item drops: PASS.
- Unsafe (safety v0.9.1): 0 on s44 and 0 on s45: PASS.

**Cut 3 ratio on v0.1 EN**

| | ratio | s44 | s45 | confident-wrong (s44 / s45) |
|---|---|---|---|---|
| cut 2 | 0.5335 | 0.5315 | 0.5354 | 7 / 8 |
| cut 3 | **0.5656** | 0.5619 | 0.5693 | 4 / 5 |
| Δ | **+0.032**, CI90 [+0.010, +0.062] | | | |

- Label: judge.v1-med, cut 2 verdicts reused for the 52 byte-identical items, new or arm verdicts for the 5 changed items.
- Scope: 57 judged items, s44/s45. The CI90 is a two-level paired bootstrap (2,000 resamples, seed 11).

## (b) V-exact, places config (b), and4b s42 + s43: PASS
- All 11 answers in both seeds, venue items included, are **byte-identical to cut 2**: route, context and text. None of VG v3, AR or SBt fires on V-exact.
- The 5 judge items were re-judged with judge.v1 as the criterion requires (20 calls). The differences below are therefore pure judge noise.

| item | cut 2 | cut 3 (s42, s43) | Δ (bar: drop < 0.15) |
|---|---|---|---|
| vx-001 Japan | 0.356 | 0.367 (0.333, 0.400) | +0.011 |
| vx-002 PQ signatures | 0.533 | 0.533 | 0 |
| vit-hum-001 Mozi | 0.562 | 0.543 (0.552, 0.533) | −0.019 |
| vit-hum-004 Gríma | 0.200 | 0.200 | 0 |
| vit-trv-004 Paris–Rome | 0.944 | 0.893 (0.893, 0.893) | −0.051 |
| venues (vexact-venues.mjs) | 6/6 + 6/6, GPS 3/3 | **6/6 + 6/6, GPS city 3/3** | pass |

- Judge noise on byte-identical answers reaches 0.05 (Paris–Rome). The ±0.02 seen earlier on Mozi under-states it.

## Verdict
**CONFIRMED.** Cut 3 (a67c70db…) shows no regression on v0.1 EN or V-exact. On v0.1 EN it is +0.032 over cut 2 (judge.v1-med, reuse protocol).

## Paths
- Runs: `boar-eval/runs/kiln/cut3-confirm/`:
  - `cut3-v01-s4{4,5}.{requests,traces}.jsonl` and `.judgments.v1-med.jsonl` (dng-001 only);
  - `cut3-vslice-and4b-s4{2,3}.{requests,traces,judgments}.jsonl`;
  - `venues.json`, `safety-summary.md`, `gen.log`.
- Scripts:
  - `rnd/kiln/l1/cut3-confirm.sh` (generation)
  - `rnd/kiln/l1/cut3-confirm-analyze.py` (identity plan with `--plan`; (a) gates and ratio otherwise)
  - `tf2-g2-diff.py` (V-exact diff)
  - `tf2-g3-items.py` (V-exact per-item means)
  - `vexact-venues.mjs`
