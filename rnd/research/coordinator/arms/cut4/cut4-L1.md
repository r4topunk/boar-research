# Cut 4 desktop gate (L1) - 2026-10-05, Kiln runner

TL;DR: cut 4 is byte-identical to a same-day cut 3 control on v0.1 EN s44 and s45 (60/60 each). Zero changed items, so the judge was skipped.

## Setup
- Tree `<runner>/kiln/be-0cfd4a77-cut4` built from `cut4-stack.vs-0cfd4a77.patch` (sha256 1fd5d9a5..., verified); be-ship adapter sha 949eee03... (same as cut 3 tree).
- Config: Android 12 GB profile, cut3-confirm config (detector v3b on :8094, `--places`, be-ship), inside the heavy lock (`HEAVY_CLASS=normal`). Control = `be-0cfd4a77-cut3` (PATCH_SHA256 a67c70db...) run in the same session with the same requests. Detector stopped by port afterwards; disk 41 -> 40 GiB free.
- Outputs: `boar-eval/runs/kiln/cut4-l1/`, `boar-eval/runs/kiln/cut3-sameday/`.

## Comparison (cmp.py: text, tier, reason codes)
| pair | s44 | s45 |
|---|---|---|
| cut 4 vs same-day cut 3 | 60 identical, 0 diffs | 60 identical, 0 diffs |
| same-day cut 3 vs stored cut3-confirm | 59 identical, 1 diff (lan-exp-007) | 59 identical, 1 diff (lan-exp-007) |
| cut 4 vs stored cut3-confirm | 59 identical, 1 diff (lan-exp-007) | 59 identical, 1 diff (lan-exp-007) |

Changed items cut 4 vs control: none. lan-exp-007 differs from the stored run in the control too, so it is run-to-run noise (known precedent); cut 4 reproduces the control exactly. Tier changes 0, instant lost/gained 0.

## Judge
Skipped: no answer changed vs the same-day control, so judge.v1-med has nothing to score.

## Verdicts
- KVFIX gate 2 (desktop replay, <= 1 item/seed noise): PASS (0 items differ from same-day control).
- INSTANT-FRAG L1 (changed items only, no item down >= 1.0, unsafe 0, cw not up, delta >= 0): PASS vacuously, changed set empty (matches the L0 prediction).
- KVFIX gate 1 (unit tests, 1293/1293): per CUT4.md, not re-run here.
- KVFIX gate 3 (the real gate): device-only. The desktop adapter uses makeServerEngine, not LlamaEngine.ts, and its shim no-ops saveSession, so this replay cannot exercise KVFIX. It only shows the stack changes nothing else. Still open: "[gate] session save failed" absent, no gate/answer prefix re-prefill from question 2, TTFT p50 down vs the A15 smoke.
