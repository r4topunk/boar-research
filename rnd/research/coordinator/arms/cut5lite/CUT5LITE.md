# CUT5-LITE (cut 4 + KV `.nosrc` prefix + route-gate skip) - 2026-10-06

TL;DR: **ADOPT as cut 5 (device-day candidate): G1, G2, G4, G5 all PASS.** Criterion `CUT5LITE-criterion.md` sha256 e8be61a9... verified, not edited. Perf arms are not in this arm (device-only A/B).

Patch `cut5lite-on-cut4.vs-0cfd4a77.patch` sha256 `3b7a0dfa42bddee21c349a55f3d7ea3a5a1b98b58355c78b2768de75108d3e53`. Worktree `wt/cut5lite`, branch `coord/cut5lite` = coord/instsubj (8db4927d) + cherry-picks of c66fb4f5 -> 07f65d69 and 3658379f -> 7173c9af (no conflicts, nothing else). Never pushed.

| Gate | Result | Bar |
|---|---|---|
| G1 build | fresh `git archive 0cfd4a77` + patch applies; tsc clean; vitest 1308/1308 (117 files), worktree and archive | all pass |
| G2 identity (v0.1 EN s44+s45, node backend, same-day cut 4 control `be-0cfd4a77-instsubj4`, arm tree `be-0cfd4a77-cut5lite`) | text 120/120, tier 120/120, passages 120/120, reason codes (excl. route-gate:*) 120/120; no reruns needed; 0 errors | 120/120 |
| G4 skip safety (same 464 dev messages) | 0 violations; 116 skipped; skip list identical to CUT5-SPEED's (`diff` empty) | 0 |
| G5 retrieval wall arm/control | s44 7198 -> 7120 ms (0.989); s45 7402 -> 6911 (0.934); pooled 14600 -> 14031 = **0.961** | <= 1.03 |

Gate calls on desktop: control 54 per seed, arm 22 (32 of 54 skipped, 59%). Run 02:09-02:43, heavy lock, detector :8094 stopped by port, disk 39 GiB before/after, no judge, no blind/veil. Passage identity = (title, section, source) in order (traces carry no chunk id). KV changes (.nosrc) are covered by unit tests only; the desktop adapter does not use LlamaEngine.ts. G5 differences are within the ~5% control run-to-run noise seen in CUT5-SPEED.

Files: patch, `cmp5-output.txt`, `g4-output.txt`, `tools/cut5lite-l1.sh`, `tools/cmp5.py`, `tools/g4_skip.mts`. Run outputs: `boar-eval/runs/kiln/cut5lite-l1/`.
