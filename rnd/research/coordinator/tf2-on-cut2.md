# tf2-on-cut2: verdict NO-GO (tf2 stays out of the next ship cut)

- Criterion: `rnd/research/coordinator/tf2-criterion.md` sha256 **2e0dec75f56ab36f039c606ba78969c0dda2806131a8fe93dc51d1ecddc09bac** (frozen before any run).
- Candidate patch (flattened, vs 0cfd4a77): `rnd/research/coordinator/tf2-on-cut2.vs-0cfd4a77.patch` sha256 **bd39546d3e1f8a2b112f38851ac5b390b0cbd213e08fbf0e967742dd0b62fd83**.
  - = cut 2 (7931b9a8…) + `sonar/exp/39-travel-food-probes/tf1-on-cut2-citefix.patch` (61eb9ede…) + `sonar/exp/40-grima/cryptogate-on-tf1.patch` (40df6227…).
  - Sonar's `tf2-on-cut2.patch` (1f7be5d9…) is a delta from cut 2 *before* citefix, so it does not apply on final cut 2. Applied on cut 1c it gives a tree identical file-for-file to the flattened one.
  - Delta vs cut 2: `src/routing/answer.ts`, `geo.ts`, `travelDistance.ts`, + `travelFood.exp39.test.ts`.
- Tree: mini `<runner>/kiln/be-0cfd4a77-tf2` (ARM tf2, PATCH_SHA256 bd39546d…), runner `be-ship/adapter.ts` 949eee03 (copied from the cut 2 tree). Cut 2 tree `be-0cfd4a77-cut2` untouched.
- Run setup: detector v3b ON (THR unset), `--places` kit-vexact, Android 12 GB 4B config, kit A. Generation ran inside `<runner>/bin/run-heavy` through run.sh.
- Free disk on the mini: 30 GiB before the runs, 29 GiB after.

## Gates

| gate | result | detail |
|---|---|---|
| G1 units | **PASS** | `npx vitest run` (0cfd4a77 archive + patch, boar-app node_modules, MacBook): tf2 **1236/1236** tests, 115/115 files. Cut 2 on the same machine: 1228/1228, 114 files. The 8 new tests are exp-39's. |
| G2 v0.1 EN s44 | **PASS** | 60/60 items, 0 errors. Route changes: 0. Context changes: 1, **vit-cry-006** (allowed), which loses kept "ethereum.org: Decentralized finance (DeFi)" and "ethereum.org: What are zero-knowledge proofs?". Answer changes on items with unchanged route and context: **0**, so the sampler is deterministic at the same seed. Safety v0.9.1 unsafe: cut 2 0, tf2 0. |
| G3 V-exact and4b s42+s43 | **FAIL** | Japan 0.338 < 0.356 (bar). Details below. |

### G3: per-item means (judge.v1, claude-opus-5-5, 20/20 judgments ok)

| item | cut 2 (s42, s43) | tf2 (s42, s43) | Δ mean | bar |
|---|---|---|---|---|
| vx-001 Japan | 0.356 (0.345, 0.367) | **0.338** (0.276, 0.400) | −0.018 | ≥ 0.356 → **FAIL** |
| vx-002 PQ signatures | 0.533 (0.533, 0.533) | 0.500 (0.533, 0.467) | −0.033 | drop < 0.15 → pass |
| vit-hum-001 Mozi | 0.562 (0.552, 0.571) | 0.552 (0.552, 0.552) | −0.010 | pass |
| vit-hum-004 Gríma | 0.200 | 0.200 | 0 | pass |
| vit-trv-004 Paris–Rome | 0.944 | 0.944 | 0 | pass |
| venues (vexact-venues.mjs) | 6/6 + 6/6, GPS city 3/3 | **6/6 + 6/6, GPS city 3/3** | — | pass |

Determinism on V-exact:
- Only vx-001 (kept "Stablecoin" dropped) and vx-002 (kept "NSA cryptography" dropped) change context, as Sonar predicted.
- The other 9 items, in both seeds, have byte-identical routes, contexts and answers to cut 2.

## Reading (not part of the verdict)
- **The gate did its job for Japan.**
  - The crypto aside is gone in both seeds. Cut 2 said "regulatory frameworks for stablecoins" in both.
  - Without it, s42 drifted to two obscure travel-memoir books, which the judge scored correctness 2, so s42 fell to 0.276. s43 rose to 0.400.
  - The judged Japan answer is still a 2-sentence culture blurb. The real gap is completeness 1/5, and removing the noise passage does not fix that.
- **Judge noise is about ±0.02 on these items.**
  - Mozi's answers are byte-identical between arms, but the s43 score moved 0.571 → 0.552.
  - Japan's −0.018 is inside that noise, so tf2 is about neutral on V-exact, not worse.
  - The frozen bar (≥ 0.356) still fails. Per the criterion, NO-GO.
- **The exp-39 travel/food fixes are behaviour-neutral on every judged item**, with 0 changes on v0.1 and V-exact routes. They could ship alone as a separate, deterministic-only cut (tf1 without the crypto gate) if the coordinator wants the probe fixes (47/47). That would need its own frozen criterion; it was not tested here.

## Paths
- Runs/traces/judgments: `boar-eval/runs/kiln/tf2-on-cut2/`
  - `tf2-vslice-and4b-s4{2,3}.{requests,traces,judgments}.jsonl`
  - `tf2-v01-s44.*`, `cut2-v01-s44.*` (baseline copied from the mini overnight dir)
  - `venues.json`, `safety-summary.md`, `vitest-{t2,c2}.log`, `gen.log`
- Trace sha256 (prefix): tf2-v01-s44 ab90df98, tf2-vslice-and4b-s42 094ff329, s43 09ed36e4; baseline cut2-v01-s44 70434d59.
- Cut 2 V-exact baseline: `boar-eval/runs/kiln/vexact-cut2/vslice-and4b-s4{2,3}.*`
- Scripts:
  - `rnd/kiln/l1/tf2-on-cut2.sh` (generation)
  - `rnd/kiln/l1/tf2-g2-diff.py` (G2 diff)
  - `rnd/kiln/l1/tf2-g3-items.py` (per-item means; reproduces the cut 2 report's 0.36/0.53/0.56/0.20/0.94)
  - `rnd/kiln/l1/vexact-venues.mjs` (venues)
  - the overnight `score.py` (safety v0.9.1)
- Mini tree `be-0cfd4a77-tf2` (21 MB) kept for now; it can be deleted.
