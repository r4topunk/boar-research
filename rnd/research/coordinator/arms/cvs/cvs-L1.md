# CVS v0.1 EN L1 (changed items only, judge.v1-med): FAIL

TL;DR: CVS (patch 7bb693c8…) changes 4 of the 60 v0.1 EN answers (the same 4 in s44 and s45, all `lan-cmp-*`); 2 of the 4 go down, one by 1.08, so the "no changed item down ≥ 1.0" gate and the Δ ≥ 0 gate FAIL.

## Run
- Tree `be-0cfd4a77-cvs` (patch sha256 7bb693c83e7166fa…), runner be-ship 949eee03, detector v3b on, `--places` kit-vexact, Android 12 GB 4B, kit A, same requests as cut3-confirm re-keyed (arm cvs), seeds 44 and 45, heavy lock, 60/60 valid, 0 errors. Script `rnd/kiln/l1/cvs-l1.sh`; traces `boar-eval/runs/kiln/cvs-l1/cvs-v01-s4{4,5}.traces.jsonl`.
- **Byte identity vs cut 3** (`cut3-confirm` traces): 56/60 identical in each seed. Changed (answer text differs): `lan-cmp-001` (Brazil vs Russia people), `lan-cmp-002` (polar vs grizzly bear), `lan-cmp-004` (moose vs bison weight), `lan-cmp-005` (saltwater vs Nile crocodile). All four are CVS answers (`answer:computed-verdict`), both seeds.
- Judge: `judge.mjs --effort medium`, both orders, 16 calls (4 items x 2 seeds x 2 orders); cut 3's verdicts reused for the 56 identical items (rebuilt as in cut3-confirm; cut 3 ratio reproduces 0.5656). Script `rnd/kiln/l1/cvs-l1-analyze.py`, output `boar-eval/runs/kiln/cvs-l1/analysis.txt`.

## Changed items (BOAR rubric, mean of 3 dims, both orders, mean over seeds)
| item | cut 3 | CVS | Δ | s44 (cut3 → CVS) | s45 |
|---|---|---|---|---|---|
| lan-cmp-001 | 3.667 | 4.333 | +0.667 | 3.67 → 4.33 | 3.67 → 4.33 |
| lan-cmp-002 | 3.083 | 2.333 | -0.750 | 3.00 → 2.33 | 3.17 → 2.33 |
| lan-cmp-004 | 3.083 | 2.000 | **-1.083** | 3.00 → 2.00 | 3.17 → 2.00 |
| lan-cmp-005 | 2.750 | 2.417 | -0.333 | 3.00 → 2.50 | 2.50 → 2.33 |

What changed in the text: CVS answers are the short verdict + Facts block (+ model sentences) instead of cut 3's cited prose; on the animal items the 4B's facts are mass in kg for "bigger"/"grows bigger"/"weighs more" (crocodile "bigger" read as mass 1,500 vs 1,000 kg), which the judge scores below cut 3's fuller explanations (cut 3 also answered those three with the right winner).

## Gates
| gate | result |
|---|---|
| no changed item down ≥ 1.0 | **FAIL**: lan-cmp-004 -1.083 |
| unsafe (safety v0.9.1) | PASS: 0 in s44, 0 in s45 (cut 3: 0, 0) |
| confident-wrong not up | PASS: 4/5 (s44/s45), identical sets to cut 3 (4/5) |
| paired Δ ≥ 0 (57 items, s44+s45, two-level bootstrap seed 11, 2,000) | **FAIL**: cut 3 0.5656 → CVS 0.5606, Δ -0.0050, CI90 [-0.0150, +0.0031] |

Verdict: **FAIL** (two gates). Per the frozen stop rule (no revision) this ends CVS.

## Notes
- The 4 changed items are all v0.1 comparison questions the router fires on (Brazil/Russia, bear, moose/bison, crocodile); no other v0.1 item routes. `lan-cmp-003` (rank) is not routed since rev1.
- UNKNOWN: whether a different render (e.g. keeping cut 3's prose and only fixing the verdict) would score higher; not tested (no revision allowed).
