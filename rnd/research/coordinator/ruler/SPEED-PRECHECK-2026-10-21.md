# SPEED-PRECHECK (RJ5 step 1, 2026-10-21): the ruler's speed row, projected from existing Pixel 8a traces

Criterion frozen before computing: SPEED-PRECHECK-criterion.md (sha 4bd52b3d…, rnd commit db89827f). Script tools/speed_precheck.py (sha 26c87a9c7248…), output SPEED-PRECHECK-2026-10-21.json (sha ad0b4ea47369…; every run's rows.jsonl sha inside). 0 LLM, 0 judge, 0 generation, 0 paid, phone untouched. **Status: PROJECTED from BOAR Bench (bench-app) traces, not the verdict run** (that is the RC APK, RJ5 step 2 / PLAN 0.2).

## TL;DR
- **All four tiers pass USABLE on the traces** (p50 T30 ≤ 30 s, p90 T30 ≤ 60 s, p50 complete ≤ 60 s, answered items).
- The 1.7B + A-union headline config clears with a wide margin: p50 T30 4.4 s, p90 11.7 s, p50 complete 4.4 s (model-path answers only: 11.2 / 13.0 / 12.1 s).
- **The 4B also passes**: p50 T30 20.2 s, p90 39.2 s, p50 complete 26.0 s (model-path only: 28.4 / 39.9 / 37.1 s; 95 % complete ≤ 60 s). This holds on a pre-BATCHRET engine, which is about 3.5 s slower.
- **The RJ5 step-1 prediction is FALSE.** The trace projection does not support a "latency constraint" rationale for the 1.7B default as a gate failure. What separates the tiers is margin and decode rate: 4B 4.2 tok/s vs 1.7B 11-12 tok/s. It is not the USABLE line. The final call stays with the RC run, per the RJ5 kill criterion.
- T30 is derived for every model row (no per-token timestamps in the traces): firstTokenMs + 29 / row decode rate. The check residual (first token + (n-1)/rate vs the logged total) has a median of 40-100 ms on the 1.7B / Gemma runs and 230 ms on the 4B.

## Verdict table (primary runs, Pixel 8a 8 GB, set S1 = answered, warm-up dropped)
| tier | run (engine tree) | n answered / declined | TTFT p50 / p90 | **T30 p50 / p90** | **complete p50 / p90** | ≤ 60 s | decode / prefill tok/s | thermal start → max | PSS peak | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.7B + A-union (headline config) | aunion73-a (0ca54d87) | 46 / 26 | 4.3 / 9.7 | **4.4 / 11.7** | **4.4 / 13.7** | 100 % | 11.3 / 69.5 | 0 (30.1 C) → 0 | 3.41 GB | USABLE |
| 1.7B claim kit | q17b73-a (0ca54d87) | 47 / 25 | 2.7 / 7.1 | **2.9 / 9.9** | **2.9 / 11.7** | 100 % | 12.4 / 80.2 | 0 (26.2 C) → 0 | 3.39 GB | USABLE |
| Gemma 4 E2B | gemma73-a (0ca54d87) | 72 / 0 | 5.8 / 13.8 | **9.4 / 18.1** | **11.8 / 23.9** | 100 % | 7.0 / 34.1 | 0 (33.0 C) → 1 | 4.52 GB | USABLE |
| 4B (Qwen3-4B-2507) | final-cut7-v01 (7c96e59e, cut 7, pre-BATCHRET) | 72 / 0 | 15.9 / 31.1 | **20.2 / 39.2** | **26.0 / 52.0** | 97 % | 4.2 / 18.0 | 0 (33.5 C) → 1 | 4.92 GB | USABLE |

## Without deterministic items (S2 = answered, ids not in deterministic-v01.ids; model-path questions)
| tier | n | TTFT p50 / p90 | T30 p50 / p90 | complete p50 / p90 | ≤ 60 s | passes |
|---|---|---|---|---|---|---|
| 1.7B + A-union | 16 | 8.2 / 10.5 | 11.2 / 13.0 | 12.1 / 15.1 | 100 % | yes |
| 1.7B claim kit | 17 | 6.4 / 7.5 | 9.0 / 10.7 | 10.8 / 13.3 | 100 % | yes |
| Gemma 4 E2B | 42 | 9.8 / 15.7 | 13.9 / 19.9 | 16.7 / 25.0 | 100 % | yes |
| 4B | 42 | 21.3 / 32.6 | 28.4 / 39.9 | 37.1 / 56.5 | 95 % | yes (p50 T30 1.6 s under the line) |
| 4B, BATCHRET-adjusted (−3.494 s on model rows; sensitivity) | 72 S1 | 13.3 / 28.1 | 18.2 / 35.7 | 22.5 / 48.5 | 97 % | yes |

All rows incl. declines (S3), p50 T30 / complete: A-union 6.9 / 7.6 s, claim kit 4.2 / 4.2 s, Gemma 9.4 / 11.8 s, 4B 20.2 / 26.0 s. Refusal latency (S4, the decline message shown), p50 complete: A-union 11.1 s (n 26), claim kit 8.2 s (n 25). The 1.7B declines 35 % of v0.1 here, while Gemma and the 4B decline 0 %. So the 1.7B's answered set is easier and faster, and its speed row is not like-for-like with the other tiers on the same items.

## Secondary runs (S1 T30 p50 / p90, complete p50; small n, reported only)
| tier | run (tree) | n | T30 | complete p50 | decode | PSS |
|---|---|---|---|---|---|---|
| 1.7B + A-union | aunion10-a (0ca54d87) | 7 | 8.0 / 10.2 | 8.9 | 16.1 | 3.32 |
| 1.7B claim kit | q17b10-a (0ca54d87) | 6 | 5.2 / 9.1 | 6.0 | 13.9 | 3.25 |
| 1.7B claim kit | batchret-2b / 4b (0ca54d87, litelat-9) | 5 / 5 | 6.9 / 7.2; 7.7 / 9.2 | 7.6; 8.8 | 14.7; 12.2 | 3.22 |
| 1.7B claim kit | batchret-1a / 3a (c407db32, pre-BATCHRET) | 5 / 6 | 11.2 / 12.0; 10.7 / 14.2 | 12.2; 11.6 | 15.6; 14.9 | 3.22-3.23 |
| 1.7B claim kit | cmp30-q17 (7c96e59e) / cmp30off-q17 (c407db32), 30 ids | 13 / 30 | 11.8 / 15.4; 11.2 / 15.2 | 12.7; 13.3 | 12.9; 11.7 | 3.12-3.30 |
| Gemma 4 E2B | gemma10-b (0ca54d87) | 10 | 10.0 / 14.4 | 12.6 | 10.5 | 4.63 |
| 4B | final-a-cut7 / live-4b-final2 (7c96e59e), 9 q | 8 / 8 | 14.9 / 44.2; 13.2 / 28.5 | 18.8; 13.2 | 6.2; 4.6 | 4.23-4.24 |
Every secondary run is USABLE on S1. One exception is the 4B's final-a-cut7 model rows alone (n 3): T30 p50 33.9 s and p90 61.3 s. That is the only cell with a threshold breach, and it rests on 3 items.

## Sentences the ruler can print (projected; replace with the RC run when it exists)
- "Speed (Pixel 8a, 8 GB, airplane mode, default tier Qwen3-1.7B with the A-union packs; bench app, not the release APK): first 30 words of an answer in 4.4 s median and 11.7 s at p90, complete answer in 4.4 s median (12.1 s when the model writes it). Decode is 11.3 tokens/s. Verdict: USABLE by our pre-set thresholds (30 / 60 / 60 s, our choice; the bounty gives no number)."
- "The optional 4B tier is slower but still inside the same thresholds on this phone: 20 s median to the first 30 tokens, 26 s median to a complete answer, and 3 % of answers over 60 s. Its decode rate is 4.2 tokens/s, below the ~10 tokens/s that the post author's failed 1B attempt reached on a laptop."
- "Speed is measured on answered items only. The 1.7B declines 35 % of these questions; a decline takes 11 s median."

## Missing rows (named, not estimated)
- 1B no-RAG baseline arm (B31:9 anchor; the context row): not run on the phone.
- Native APK (maintainer RC) rows: none. Every number above is the BOAR Bench app. The native app on the POCO measured −0.089 in quality earlier, and its speed is unknown.
- Reference arm end-to-end time (web search + frontier model) on the same items: not measured.
- Per-token timestamps: absent. T30 is derived, so the RC run should log the 30th-token time directly.
- gemmaa73-a (Gemma + A-union) is running now and excluded. The 4B has no A-union run, so the 4B row uses the claim kit (A-union adds about +2.4 s of retrieval per researched answer, AUNION-PIXEL).

## Caveats
- Single phone, single seed per run. Thermal status was 0 at every start; the max during the Gemma and 4B 73-runs was 1, on AC power.
- The 4B primary is cut 7 (7c96e59e), not the 0ca54d87 engine of the other primaries. The adjusted row shows the direction: faster still.
- The 1.7B rows decline items after generating, so S1 excludes them. Show-anyway latency from the tap is about 0 when tokens exist; it is not measured here.
