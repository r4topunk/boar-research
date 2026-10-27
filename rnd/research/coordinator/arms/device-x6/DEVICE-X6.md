# DEVICE-X6 — cut 7 on a 12 GB-class phone: device = desktop (measurement, 2026-10-14)

Criterion: DEVICE-X6-criterion.md sha256 ed1d7dc1af6c8de5… (written before any judge call). Estimator: tools/agg_device.py (copy of the frozen l2_agg.py estimator), output aggregates: aggregate.json. Judge: Haiku 5.5-low, judge.v1, N = 4, both orders, 57 non-venue v0.1 public ids, refs bd235bb9…; 228 calls (phone 114 + native 114), desktop rows reused (arms/stack/runs/v01-cut7-stack-off-s42.judgments.jsonl, tracesSha e1d01295…). 0 paid API. No blind exposure (v0.1 public only).

## Device and runs
- Phone: Xiaomi 2311DRK48G (POCO X6 Pro), MT6897 (4 × 2.2 + 3 × 3.2 + 1 × 3.35 GHz), 11,202,880 kB RAM (10.7 GiB), Android 16, 252 GB free, airplane mode, Wi-Fi/BT off, BOAR Bench 0.2.0 with no INTERNET permission.
- A = BOAR Bench `final-cut7-v01`: engine 0cfd4a77 arm cut7, patch 0fba26b8… (= the frozen claim build), kit boar-crypto + boar-wikivoyage-en (claim kit), 4B Q4_K_M, n_ctx 4096, 4 threads. Sanity `final-a-cut7` 9/9 before it. Raw files: boar-eval/runs/device-poco-x6pro/final-cut7-v01/ (rows, telemetry, meminfo, device/bench/status/wall, kit listing; logcat kept out of git).
- B = native app team.sopa.aoair 2.0.0-dev (branch labs/engines b075adca + a 38-file uncommitted diff, sha a55f94b5…), same 73 questions byte-identical (questions sha 1b916fa2…), same 4B GGUF (3605803b…), preset "Boar's Path" (4 threads, F16 KV, thinking off), succinct, maxTokens 512, corpus = the app's own KB + wiki-vital5 (NOT the claim kit), Deep Research and adaptive routing off. Raw: boar-eval/runs/device-poco-x6pro/native-x6-v01/.
- D = desktop reference: arms/stack/runs/v01-cut7-stack-off-s42 (cut 7, same 2-pack kit, MacBook M1 Pro llama-server, seed 42).

## A — cut 7 on the phone (72 items + warmup)
| metric | value |
|---|---|
| outcome | 72/72 success, 0 declined, 0 timed out; logcat 0 lmkd / ANR / crash lines |
| tiers | fast 51 (4B 42, grounding-guard 9), instant 21 (guard 12, extractive 4, places 3, calculator 2) |
| fast tier total | p50 30.7 s, p90 48.4 s, max 53.0 s; TTFT p50 18.5 s; decode p50 5.5 tok/s (4.6–7.4); output p50 64 tokens |
| instant tier total | p50 0.1 s, p90 11.2 s (guard items that still prefill) |
| all 72 total | p50 24.7 s, p90 41.4 s; run wall 29 min 14 s |
| memory (app PSS) | peak 5.88 GB during model load, then p50 3.64 / p90 3.80 / max 4.23 GB; meminfo end 3.60 GB PSS, 2.88 GB RSS |
| thermal | battery 34.5 → 41.7 °C max (39.8 end), thermal_status 0 throughout; battery 73 → 74 % (charging) |

## Parity A vs D on the 60 public ids (0 calls)
tier 60/60 identical; instant-tier answers 16/16 byte-identical; kept titles 59/60 (dng-002: on-device detector p 0.431 vs 0.374 keeps one extra Wikivoyage source); reasonCodes differ only by the phone's `route-gate:*` codes (not emitted by the desktop adapter); 4B answers byte-identical 3/44 (llama.rn vs llama-server sampling, as DEEPPAR found for bmoe). Desktop total p50 7.5 s vs phone 28.3 s (×3.4); decode 22.6 vs 5.6 tok/s.

## Judged (57 ids, Haiku L1)
| set | raw (CI95) | above_min (CI95) | win/tie/loss vs ref |
|---|---|---|---|
| phone cut 7 (A) | **0.529 (0.481–0.575)** | 0.403 (0.343–0.461) | 2/1/54 |
| desktop cut 7 (D) | 0.529 (0.484–0.575) | 0.402 (0.346–0.458) | 1/2/54 |
| native app (B) | 0.440 (0.396–0.487) | 0.291 (0.236–0.349) | 0/1/56 |

Paired: phone − desktop raw **−0.000 (−0.026…+0.028)**, above_min +0.000 (−0.031…+0.033), items better/worse 22/17 → **device = desktop within noise** (the declared reading: |Δ| ≤ 0.03, CI inside ±0.05). Same conclusion as the cut-6 A15 run (0.561 vs 0.558/0.560 on the same 57, 10-06).
Native − phone raw **−0.089 (−0.145…−0.032)**, above_min −0.111 (−0.182…−0.040), better/worse 15/33; native − desktop −0.089 (−0.141…−0.036). Product comparison only: same device and 4B, different corpus (own KB + wiki-vital5) and pipeline; retrieval used 37/72 in both, overlapping on 19 items.

## B — native app speed (72 items)
total p50 18.9 s / p90 37.8 s (×0.77 of A's p50: shorter prompts, 143-token prompt sample; TTFT p50 7.0 s), decode p50 6.1 tok/s, output p50 78 tokens, peak RSS 5.14 GB, battery 33.5 → 43.3 °C, thermal 0.

## What this changes
1. First on-device run of the frozen claim build (cut 7): quality = desktop; the desktop numbers (v0.1/v0.2/V-para) transfer to this device class with the sampling caveat.
2. A 12 GB-class phone now exists in the team (10.7 GiB usable RAM): the deep tier's device steps (deep/RESUME.md D2/D3/D5: bmoe + Qwen3.6-35B UD-Q2_K_XL 7.9 GB, thinking 512 app-side cap) are no longer blocked on hardware. Risk: RAM headroom (7.9 GB model + KV on 10.7 GiB; the 4B peaked at 5.88 GB PSS at load).
3. The native app loses 0.09 raw vs the bench engine on the same phone and model: corpus/pipeline parity is the native line's first item (Forge), not an engine problem.
