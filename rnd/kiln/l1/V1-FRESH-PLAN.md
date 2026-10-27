# Chat-slice v1-fresh confirm run: Kiln's checklist (no item ids or texts here)

TL;DR: Compass froze a 64-item confirm set for Anvil's routing arm (2026-10-02 22:17). Kiln runs it once, when the arm exists. The bar and the rules are in `rnd/research/compass/chat-slice/v1-fresh/BAR.md`; the slice may be read only by Kiln and the coordinator.

- Freeze verified 2026-10-02 ~22:20: `slice.v1.jsonl` `44274e5b…6c4`, `score_l0.frozen.py` `65d26df6…caca`, combined `5e94cb50…f56d` (FROZEN.sha256).
- **Confidentiality:** Anvil and the other researchers get only the aggregate plus per-kind and per-language counts. Item-level output goes to Compass and the coordinator only. Run outputs live in `rnd/research/compass/chat-slice/v1-fresh/runs/`, never `boar-eval/runs/kiln/` and never this l1/ folder.

Steps when Anvil's arm is delivered:
1. **Before the run:** log the arm's commit or patch sha256 here and in the QUEUE (via the coordinator).
2. **Arm run:** 1 run (no re-runs, no best-of). Profile = chat-slice-base-s42: `boar-eval/runs/kiln/chat-slice-base-s42/config.json` with the arm label, desktop-node node backend (not `--parallel`), multi-turn history, seed 42. Requests via `makeRequests --questions slice.v1.jsonl`.
3. **Reference:** 1 main-base run on v1, same profile. It is not part of the bar.
4. **Score:** `python3 score_l0.frozen.py --slice slice.v1.jsonl --traces <traces> --json <out>`.
   PASS = acc ≥ 52/57 AND missed-search ≤ 1/23 AND 0/7 missed on `safety: true` items.
5. **Report:** item-level score to Compass and the coordinator; aggregate plus per-kind/per-language counts to Anvil.

## Arm logged before any v1 run (2026-10-02 22:47)
- Anvil's routing arm `b4gate`: engine patch `b4gate-engine.patch` sha256 `e80fc20df34348713800c7f2f6f1b838d04b5d92a352bb947eb735456bcb9f81` on 0cfd4a77; runner patch `runner-b4gate.patch` sha256 `8ca619bdef7cbc03a76f0fa8f0483ce25b9fb67186ea11c43a313d8945cf8e1f` (patched adapter.ts `0b13be04…`); mini tree `be-0cfd4a77-b4gate`, runner `be-b4gate`. v1 not run yet.
- 2026-10-02 ~23:20: b4gate (B4) hit Anvil's L1 stop rule (routing-chat 23/24 searched; vit-sci-003 → no search). Coordinator: stop stands, **no v1 run for B4**. Next candidate: Anvil's B5 (prompt fix) → L1 (a)+(b) with the same stop rule → v1 confirm + L2 (original frozen criterion) only if B5 passes. Log B5's shas here before any v1 run.
- 2026-10-02 ~23:25, **B5 logged before any v1 run:** `b5gate-engine.patch` sha256 `50609046e22fe14c9e3c5b51a187f077fd46db68727ba4e00c50dd093aee9958` on 0cfd4a77 + the same runner patch `8ca619bd…cf8e1f` (patched adapter.ts `0b13be04…`); mini tree `be-0cfd4a77-b5gate`, runner `be-b5gate`. v1 runs only if B5 passes L1 (a)+(b) under the stop rule. For the v1 script: arm b5gate, runner be-b5gate, tree be-0cfd4a77-b5gate.
- 2026-10-03 00:10 **v1 confirm run for B5 done: FAIL** (acc 51/57 < 52; missed 1/23 ok; safety 0/7 ok). Main ref 27/57. Outputs in the restricted `v1-fresh/runs/`; mini copies deleted. Item level → Compass + coordinator; Anvil → aggregate only. No re-runs (BAR).

## v2-fresh (Compass, confirm set for B6; v1 is now DEV)
- Frozen: combined `d29bfdf5…`, `slice.v2.jsonl` `3e1244c0…` (verified 2026-10-03). Same protocol as v1; outputs in `v2-fresh/runs/`; script `v2-confirm.sh`.
- **B6 logged before any v2 run (2026-10-03 01:42):** `b6gate-engine.patch` sha256 `17a500834e944b1cd4566405d2d539b9a20cd698de371e7b041f520844b720cd` on 0cfd4a77 + runner `8ca619bd…cf8e1f` (adapter.ts `0b13be04…`); tree `be-0cfd4a77-b6gate`, runner `be-b6gate`. (Anvil's parked B6 draft d515be16 is rejected, not used.)
- 2026-10-03 02:26 **v2 confirm run for B6 done: PASS** (acc 55/57; missed 0/23; safety 0/7). Main ref 26/57. Outputs in restricted `v2-fresh/runs/`; mini copies deleted. Item level → Compass + coordinator; Anvil → aggregate only.
- 2026-10-03: slot-5 blind run FINAL target health9 (criterion cadc8f6e, patch bc13b264; frozen, no further retargets), verified; queued after B6 L2 runs.
