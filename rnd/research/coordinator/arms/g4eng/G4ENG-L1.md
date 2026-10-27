# G4ENG L1: Gemma 4 E4B as the reader inside cut 3 (run 2026-10-05; criterion sha256 5aecdd03d1adc3b42dd89220f35601acc07bcfdf7f4760ddfc9648405f903eaa)

TL;DR: **FAIL, not adopted. Paired Δ −0.0385 (CI90 −0.0725…−0.0058), time p50 1.49×, 1 channel-token leak, VG verdict-guard codes missing on 3 items. Unsafe 0 and cw not up are the only passes besides empties.** G4ENG ends here (stop rule).

## Setup
- Arm: tree `<runner>/kiln/be-0cfd4a77-g4eng` = byte copy of `be-0cfd4a77-cut3` (patch a67c70dbd194da82…, runner be-ship 949eee03…, src diff identical), `ARM=g4eng`. Only change: requests `config.modelId = gemma-4-e4b-it-q4_0` (the QUEUE #2 config-only path; GGUF sha 676c3507… = adapter MODELS, verified after re-download). Same engine Gemma template path as Oct-1.
- Control: cut 3 re-run in the same session (tree `be-0cfd4a77-cut3`, Qwen3-4B), interleaved ctl s44, G4ENG s44, ctl s45, G4ENG s45. v0.1 EN requests = cut3-confirm's, 60 items (57 judged, venue-list items are scored by OSM), Android 12 GB, kit A, detector v3b on, heavy lock via run.sh. 0 run errors both arms.
- Judge: `judge.mjs --bench bench/v0.1 --effort medium` (judge.v1-med), ALL 57 items, both orders, both arms, both seeds (456 calls). Read-out `rnd/kiln/l1/g4eng-l1-analyze.py` (paired ratio, two-level bootstrap 2000, seed 11; safety v0.9.1).
- Gen script `rnd/kiln/l1/g4eng-l1.sh`, judge script `g4eng-l1-judge.sh`. Traces/judgments in `runs/`.

## Gates
| gate | result | verdict |
|---|---|---|
| paired Δ ≥ +0.02, CI90 low > 0 | ratio cut 3 **0.5600** (s44 0.558, s45 0.562) vs G4ENG **0.5216** (0.531, 0.513): **Δ −0.0385, CI90 [−0.0725, −0.0058]** (significantly worse) | **FAIL** |
| unsafe 0 (safety v0.9.1) | 0 / 0 on both seeds, both arms | PASS |
| confident-wrong not up (mean correctness ≤ 1.0) | cut 3 5 / 5 vs G4ENG 5 / 7 (s44 / s45); labels cw(≤2) 13 / 12 vs 13 / 13; pass(≥4) 28 / 28 vs 32 / 30 | **FAIL** (up by 2 at s45; flat at s44) |
| total time p50 ≤ 1.25× cut 3 | 11.59 s vs 17.24 s = **1.49×** (fast tier only 1.49×); median decode 24.2 vs 4.0 tok/s | **FAIL** |
| 0 empty answers | 0 / 120 | PASS |
| 0 template/channel leaks | **1**: s44 `lan-exp-007` contains `…requirement and answers the prompt.)<channel\|>Greenland is…` (thought text before a stray close-channel token) | **FAIL** |
| card/calculator/VG/AR paths unchanged (route codes identical) | card/calculator/places/diet items (dng-001, food-001/002/006, vit-sci-003, vit-trv-004): identical text and codes on both seeds. But **`verdict-guard:compare|date|rank` fire in cut 3 and not in G4ENG** on vit-sci-002, lan-ref-003, lan-cmp-003 (both seeds), and **no `route-gate:*` code is emitted at all for G4ENG** (54/54 fast-tier items in cut 3 carry `route-gate:search`). Full route-code identity 12/120 | **FAIL** (VG verdict-guard path changed) |

## Reading
- Answers changed on 100/120 items; Gemma passes more items (pass 32/30 vs 28/28) but the rubric ratio is lower, i.e. completeness/usefulness lose more than correctness gains, consistent with the Oct-1 RAG notes (Gemma sticks to sources, Qwen answers more completely).
- Time: effective decode 4.0 tok/s vs the 22-24 tok/s of the closed-book screen. The shared engine's fast tier generates with `thinking = true` and a 256-token thinking budget (`depth.ts`, `answer.ts:1127`; Anvil's cycle-10 correction in `anvil/cards/gemma4-e4b-reader-android.md`), so G4ENG ran Gemma with hidden thinking, which also explains the one leaked `<channel|>`. The criterion froze "the engine's existing Gemma template path", so this is the arm as specified; a non-thinking Gemma (engine change) would be a different arm and was not run.
- The missing `route-gate`/`verdict-guard` codes for Gemma are unexplained here (UNKNOWN: probably a capability/model-id gate in the engine; not investigated, engine untouched).

## Verdict
**FAIL on 5 gates (Δ, cw, time, leaks, route identity). Not adopted; G4ENG ended.** GGUF deleted from the mini; tree `be-0cfd4a77-g4eng` (~40 MB) kept, see DISK-LOG.md.
