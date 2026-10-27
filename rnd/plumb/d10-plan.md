# D10 device session: plan (Plumb)

TL;DR: one session on `team.sopa.aoair` with `o2eval-aoair-611a4b9` (main fd24992 + O2 behind a flag). Every step is a separate call of `rnd/plumb/run-d10.sh <stage>`. Any error means stop and report, with no retries.

| # | Stage | Who / condition | Est. |
|---|---|---|---|
| 0 | take the lock (`.tools/appium/.iphone-lock`), `status` | Plumb, after r4to's GO | 1 min |
| 1 | `install` | Plumb | 1 min |
| 2 | `neutralize` + `launch-once` | **r4to: mobile data on** during the single launch. If it fails: stop and report the exact error | 1 min |
| 3 | airplane mode on | **r4to** | – |
| 4 | `kit-a`: copy wiki-vital5 (sha d3b87d56…) | Plumb | 1 min |
| 5 | `bench60 kitA`: 60 public items (split sha dc859ebd…), `--o2 off` | Plumb | ~10 min |
| 6 | `o2ab`: 82 items (Veil 30 + device 52, sha 351c5273…), ABBA | Plumb | ~30 min |
| 7 | `safety rnd/bench/safety/track.v0.1.jsonl` (sha 7560f6fd…), `--o2 off` | Plumb | ~2 min |
| 8 | *only if the window allows:* `kit-b` → `bench60 kitB` → `kit-restore` (check sha ae9fbd2c… / ff8595e3…) | Plumb | ~13 min |
| 9 | `vital5-off`, `status`, delete the lock, update note rows #7/#8/D10 | Plumb | 1 min |

Fixed settings: `--models qwen2.5-1.5b --quick-first on --always-complete off`, no answer-anyway, `GGML_METAL_DEVICES=0` (in eval-iphone), airplane mode on for every eval block.

Outputs:
- `rnd/plumb/data/qwen2.5-1.5b-instruct-q4km__iphone-611a4b9-o2off-bench-v0.{jsonl,report.md,request.json}`
- `…o2-ab` runs in the worktree, then `make_blind.py`
- `…611a4b9-o2off-safety.jsonl`

What the report records:
- CFBundleShortVersionString/CFBundleVersion and the main.jsbundle sha256 (from `install`)
- packs and sizes (from `status`/`files`)
- the O2 flag seen in the request and in `answerSettings.o2Compact`

Labels: P3 = rc6eval 14de107 (eval branch, rc.6); BOAR main = 611a4b9 (main + O2, rc.6). Compare quality only within a build, or declare the engine as the only variable when comparing P3 with BOAR main on kit A.
