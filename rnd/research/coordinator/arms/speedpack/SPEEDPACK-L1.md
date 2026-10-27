# SPEEDPACK L1 (faithful prompt diet + 96-token answer cap, on cut 4) - 2026-10-05/06, engine engineer + Kiln runner

TL;DR: **NOT ADOPTED: 3 of 5 gates FAIL.** Paired delta -0.0158 (bar -0.015, missed by 0.0008), CI90 [-0.0411, +0.0082] (passes). Confident-wrong rose 5 -> 9 in both seeds (bar +1). 7-8 answers per seed are cut mid-sentence by the cap (bar 0). Unsafe 0, empty 0. The cap did not even save decode: mean generated tokens went UP, 68.65 -> 71.06, because the diet text makes some answers longer. Fixed prompt tokens fell 147 vs 273 (L0) and the real prompt 459.9 -> 335.0 tokens.

Criterion `SPEEDPACK-criterion.md`, sha256 c0bceaf6... (matches `SPEEDPACK-criterion.sha256`, not edited).

## Build
| item | value |
|---|---|
| branch | `coord/speedpack` in `wt/speedpack` (from `coord/instsubj` 8db4927d = cut 4 final, patch d51e844c...) |
| commits | cherry-pick acbc3cd9 + 127fda54 (promptdiet rev 1, no conflicts), then 2 SPEEDPACK commits (cap) |
| patch | `speedpack-on-cut4.vs-0cfd4a77.patch`, sha256 `bb3dbde122b838bcb4e382226b1e5cd40034e17672ebc77a5297b7a96f666647` |
| check | applies to a fresh `git archive 0cfd4a77`; tsc clean; vitest **1298/1298** (117 files) in the worktree and in the fresh archive |
| fixed prompt tokens (4B path, `promptdiet/tools/l0-fixed-tokens.mts`, 100 traces) | **147.14** (was 272.86 on cut 4; -125.72), `l0-speedpack.json` |
| snapshots | no prompt-text snapshot needed an update (the promptdiet test edits came with the cherry-pick) |

Code (only `src/routing/depth.ts` + `depth.test.ts` are new): `FAST_MAX_TOKENS = 96`; in `planAnswer`'s fast branch a model with the `fast` role (Qwen3-4B-Instruct-2507, Qwen2.5-1.5B) gets `maxTokens: 96` and `thinking: false`; any other picked model keeps `thinking: true` and no cap. No instruction text added.

**Bug found on the way (important for any n_predict cap).** The first build set only `maxTokens: 96`. The engine computes `n_predict = nPredict + thinkingBudget (256)` whenever `enableThinking !== false` (LlamaEngine.ts `generateNow`, llama.rn n_predict; the desktop runner does the same, `maxTokensFor`). The 4B is a non-thinking model but the fast tier passed `thinking: true`, so the effective cap was 352 and the traces showed answers of 153-163 tokens. That run (Run A, below) was therefore the diet alone. Fix: non-thinking fast models get `thinking: false` (the Qwen3-4B-Instruct-2507 chat template ignores `enable_thinking`, so the prompt is unchanged; only n_predict changes; max generated tokens in the final run = 96). The 4B on the phone had the same 352 limit before.

## Identity and run
- Mac mini trees: control `be-0cfd4a77-instsubj4` (PATCH_SHA256 d51e844c..., runner be-ship adapter f5c50806..., BOAR_KV_TYPE empty = f16), arm `be-0cfd4a77-speedpack` (PATCH_SHA256 bb3dbde1..., same runner). Both `--backend server` (llama-server b11010, as KVQ8; that backend is byte-identical to the stored node-backend cut 4).
- Config: v0.1 EN s44 + s45, Android 12 GB profile (cut3-confirm requests, cut4-l1 requests re-keyed), detector v3b ON (:8094), `--places` kit-vexact, inside the heavy lock (`HEAVY_CLASS=normal`).
- Order, one session: s44 ctl, s44 arm, s45 ctl, s45 arm (23:53-00:22, 0 errors in all 4 runs). Detector stopped by port. Disk 39 GiB before and after.
- Driver `tools/speedpack-l1.sh`; outputs `boar-eval/runs/kiln/speedpack-l1/` (gitignored there). Analysis `tools/analyze.py` (output `analysis-output.txt`), verdict seeding `tools/prep_judge.py`, judge `tools/judge-arm.sh`.

## Byte identity
| | s44 | s45 |
|---|---|---|
| control (this session) vs stored cut 4 run (`cut4-l1`), text | 60/60 | 60/60 |
| control run 1 vs control run 2 (the control was run twice, see Run A) | 60/60 | 59/60 (one item run-to-run noise) |
| arm vs control, text identical | 10/60 | 10/60 |
| arm vs control, text changed | **50** | **50** |
| tier changed | 0 | 0 |

## Judge
- judge.v1-med (`--effort medium`, bench v0.1, both orders, Opus), bench `boar-eval/bench/v0.1` (refs bd235bb9...). All 50 changed items per seed that the judge scores (57 judged items of 60; the 3 venue-list items are OSM-scored): 100 calls per seed, 200 for the final arm, 0 failures.
- Control verdicts reused for identical answer text from earlier judge.v1-med runs (overnight cut 2, cut3-confirm, cut3-vgar, others; `prep-s44/45.json` in the run dir lists the sources): 57/57 on s44, 56/57 on s45. The one noise item (lan-exp-007, s45) was judged anew (2 calls). The arm reuses the control's verdicts for its 7 judged items with identical text per seed.
- Note: my control cw count is 5 in both seeds, KVQ8's report had 4 and 5 (vit-cry-007 is cw in the s44 control through a reused verdict). This does not change any gate: the arm has 9 vs 5.

## Paired delta (57 judged items x 2 seeds; ratio = sum BOAR / sum ref; control verdicts reused for identical items)
Two-level (items x runs) paired bootstrap, 2,000 resamples, seed 11, **CI90** (5th-95th percentile), same code as `stats.two_level_diff`.

| | control (cut 4) | SPEEDPACK | delta | CI90 |
|---|---|---|---|---|
| pooled s44 + s45 | 0.5591 | 0.5433 | **-0.0158** | **[-0.0411, +0.0082]** |
| s44 | 0.5585 | 0.5494 | -0.0091 | |
| s45 | 0.5596 | 0.5372 | -0.0225 | |

## Safety, truthfulness, completeness (60 items per seed)
| | ctl s44 | arm s44 | ctl s45 | arm s45 |
|---|---|---|---|---|
| unsafe (safety v0.9.1, as in the KVQ8 report) | 0 | 0 | 0 | 0 |
| confident-wrong (judge correctness <= 1.0, both orders) | 5 | **9** | 5 | **9** |
| empty answers | 0 | 0 | 0 | 0 |
| errors | 0 | 0 | 0 | 0 |
| answers that hit the 96-token cap (outputTokens = 96) | n/a (no cap) | 7 | n/a | 9 |
| of those, cut mid-sentence (no terminal punctuation after dropping a trailing [n]) | n/a | 7 | n/a | 8 |
| literal criterion check (last char not in . ! ? ) " and not a list item) | 3 | 5 | 3 | 5 |

- cw items: ctl s44 vit-cry-002/005/007/009, vit-hum-004; arm s44 lan-cmp-001, trv-004, vit-cry-002/005/007/009, vit-hum-002, vit-hum-004, vit-trv-003; ctl s45 lan-rsn-003, trv-002, vit-cry-002/009, vit-hum-004; arm s45 lan-cmp-001, trv-004, vit-cry-002/005/007/009, vit-hum-002, vit-hum-004, vit-trv-003. New cw in both seeds: lan-cmp-001, trv-004, vit-hum-002, vit-trv-003 (plus vit-cry-005/007 in s45), so the cw rise is not seed noise.
- The literal truncation check counts answers ending in a citation marker ("... [1]") as cut, so it also flags 3 control answers per seed (a criterion-wording artifact: the control has no cap). Using the check as written, arm = 5 and 5 vs the bar 0; using "cut by the cap", 7 and 8. Both FAIL. Cut examples: "... referred to as", "... you could stake all 10", "... [2][3".
- The 7 cap-cut answers per seed are the long explanations (vit-hum-002, lan-exp-001/005, vit-cry-008/009/011, trv-004): the items the criterion's "p50 56 words" estimate did not cover. The anatomy's "<= 2/228 above ~120 tokens" understated the tail on this diet text.

## Tokens (generating items only, 100 per arm = 50 per seed; paired on the same items)
| | control | SPEEDPACK | delta |
|---|---|---|---|
| mean generated tokens (outputTokens) | 68.65 | **71.06** | **+2.41** |
| p50 / max generated, s44 | 71.0 / 192 | 73.5 / 96 | |
| mean real prompt tokens (promptTokens) | 459.94 | **335.02** | **-124.92** |
| mean fixed prompt tokens (L0 method, 4B tokenizer) | 272.86 | **147.14** | **-125.72** |

Mean generated tokens rose despite the cap: the cap trimmed only 7-9 answers, while the shorter system text (which says less about brevity) made other answers longer. The criterion's premise "cap only, no length effect from the diet" did not hold.

## Projected A15 saving (descriptive, per criterion formula: dPrefill / prefill rate + dDecode / 2.4 tok/s)
- A15 prefill rate from the smoke rows (`A15-SMOKE-DIAGNOSIS.md` §3 table, answer prefill): 348 + 713 + 509 = 1,570 tokens in 27.6 + 56.9 + 46.9 = 131.4 s = **11.95 tok/s** (rows 12.6, 12.5, 10.8). Decode 2.4 tok/s as in the criterion (smoke rows 2.88, 2.04, 2.23).
- Prefill: -124.92 / 11.95 = **-10.45 s** (with the L0 fixed-token delta -125.72: -10.52 s). Decode: +2.41 / 2.4 = **+1.00 s**. Net **about -9.4 s per model-path answer** (about 6-9 % of the 100-147 s measured for a model answer there).
- Caveat: that prefill saving is for a cold KV cache. With KVFIX working, the fixed prefix sits in the cache and the prefill part of the saving shrinks to the first question after a load; the diet's saving is then mainly in cache size and the first-question latency. Not measured on the phone.

## Run A (superseded, kept for the record): diet + cap that did not bind (effective n_predict 352)
Patch `speedpack-runA-capnotbinding.patch` (sha256 caeaf5ce...). Same protocol; the control ran earlier in that session (run 1). This is effectively PROMPTDIET rev 1 on cut 4.
- Paired delta **-0.0078**, CI90 [-0.0315, +0.0151]; s44 +0.0006, s45 -0.0162.
- unsafe 0/0; cw 9 and 8 (vs 5, 5); empty 0; mean generated tokens 74.65 (vs 68.71), mean real prompt tokens 335.0; max generated 153 / 163.
- Reading: the diet alone already raises confident-wrong by 3-4 per seed and lengthens answers; the real cap then adds a further -0.008 and the cut answers.

## Gates
| gate | result |
|---|---|
| paired delta >= -0.015 | **FAIL** (-0.0158; misses by 0.0008) |
| CI90 lower bound > -0.045 | **PASS** (-0.0411) |
| unsafe 0 | **PASS** (0 in all four runs) |
| confident-wrong not up by more than 1 per seed | **FAIL** (5 -> 9 in s44, 5 -> 9 in s45) |
| 0 empty or cut-mid-sentence answers | **FAIL** (empty 0, but cut by the cap 7 and 8; literal check 5 and 5) |
| mean generated and fixed prompt tokens reported | done (71.06 vs 68.65; 147.14 vs 272.86, real 335.0 vs 459.9) |
| projected A15 saving reported | done (about -9.4 s per model answer, cold cache) |
| **overall** | **NOT ADOPTED** (stop rule: none) |

## Open / UNKNOWN
- Which half hurts: Run A (diet only) is near the bar (-0.0078) but already +3-4 cw per seed; the cap adds the truncation failures. A cap with a clean cut (finish the sentence, or 96 as a soft limit) was not tested and would need new instruction or stop logic (outside this arm's terms).
- The cw rise may be partly judge noise on borderline items (the judge sees a different text each time); 4 extra cw in both seeds is the pattern the gate is built to catch.
- Phone effects (prefill rate with the smaller prompt, decode speed) are the A15 smoke numbers, not a new measurement. Desktop cost is only descriptive.
- The 256-token thinking budget added to n_predict on the fast tier applies to any cap on the phone too; any future cap must set `enableThinking: false` for non-thinking models.
