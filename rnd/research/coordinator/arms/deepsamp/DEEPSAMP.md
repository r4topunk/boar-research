# DEEPSAMP result (coordinator-run, 2026-10-10 13:43–14:4x). Criterion DEEPSAMP-criterion.md sha256 f4a5a4aa2d82cac0d0bb3184363fb06e7eeaafc3012e0886f88a55a940f1b1a1 (not edited); adapter boar-eval 6914ec8 (adapter.ts d8dcc88f…, server.ts 4c347f03…: `BOAR_SAMPLER_JSON`)
**Verdict: NO at the slice for both vendor settings.** On the 20-item V-para slice (Haiku 5.5-low N = 4, paired vs H = the recommended deep configuration at the engine's sampling 0.7 / top_k 40 / top_p 0.95 / min_p 0.05): **Q** (Qwen's "thinking, general": temp 1.0, top_k 20, top_p 0.95, min_p 0, presence_penalty 1.5) Δ **−0.029 (−0.073…+0.010)**, h2h 6/4/10; **P** (Qwen's "thinking, precise": temp 0.6, top_k 20, top_p 0.95, min_p 0) Δ **−0.017 (−0.056…+0.029)**, h2h 4/5/11; wins 0/0 everywhere. Neither reaches the promotion rule nor a near-miss; no full set, no Opus. The engine's default sampling stays for the deep thinking tier.

## Identity
| item | value |
|---|---|
| tree | mini `be-0cfd4a77-deepsamp` = rsync of `-dt512` (cut 6 824e0b35… + deepthink eb3f464b… + dt512 f9a1979b…; thinking 512, succinct, ctx 400) + be-repo adapter/server from boar-eval 6914ec8 (sampler override on the server backend, recorded in `versions["sampler.override"]`); `diff -rq` vs dt512: ARM, adapter.ts, server.ts |
| runner | `tools/remote-run.sh` (dt512's + tree/adapter/server/ARM checks; env by arm), llama-server b11010 CPU, `--deep-model`, `--places` kit-vexact, detector up throughout, `--timeout-ms 600000`, seed 42 |
| smokes | Q and P 2/2 deep-thinking, reasoning 522, 0 errors, override string present in both traces → PASS |
| requests | smoke cf7339ae… / 459e56e6…; slice 1ecc1f91… / e76cd37e… (= H's slice requests, signal20-vpara 6e707734…, runId/arm rewritten) |

## Slice 20 (seed 42; Haiku 5.5-low N = 4 vs H's slice rows)
| arm | sampler | ratio (CI) | floor-adj | Δ vs H (CI) | h2h >/=/< | reasoning p50 (cap hits /20) | answer tok p50 | total p50 (p90) | rule |
|---|---|---|---|---|---|---|---|---|---|
| H | 0.7 / 40 / 0.95 / 0.05 (engine) | 0.519 (0.466–0.567) | 0.384 | — | — | 522 (17) | 94 | 77.6 s (97.6) | control |
| Q | 1.0 / 20 / 0.95 / 0 + presence 1.5 | 0.490 (0.436–0.538) | 0.347 | **−0.029 (−0.073…+0.010)** | 6 / 4 / 10 | 522 (19) | 91 | 73.3 s (86.4) | NO |
| P | 0.6 / 20 / 0.95 / 0 | 0.502 (0.451–0.551) | 0.363 | **−0.017 (−0.056…+0.029)** | 4 / 5 / 11 | 522 (17) | 96 | 69.1 s (83.4) | NO |
20/20 generated per arm, 0 errors; mini ≈ 30 min per arm; Haiku 80 calls, Opus 0.

## Reading
- Neither the hotter vendor setting (with its presence penalty, meant for long agentic sessions) nor the colder "precise" one beats the engine's default on this slice; both sit slightly below it, with CIs that include 0 and head-to-head counts against them. Under SEEDVAR's noise (one-seed SD ≈ 0.02 on V-para; a 20-item slice is noisier still), a true effect of either sign up to ≈ 0.03 cannot be excluded, but nothing here motivates a full set.
- Sampling is not a lever for the deep thinking tier on the desktop; the device plan keeps temperature 0.7 (the app's default) with thinking 512.
- Tooling kept: `BOAR_SAMPLER_JSON` on the server backend (frozen arms never set it; request bodies unchanged when unset, unit-tested).

## Exposures (script-only; no blind content in any context)
V-para: 2 slice generations (Q, P; 20 ids, seed 42) + Haiku 20 ids × 2 (80 calls); H slice rows re-read. Smokes on v0.1 (dev). Outputs: `blind/V-para/runs-deepsamp/`, smoke in `boar-eval/runs/kiln/deepsamp/`, aggregates here. Cost: Haiku 80, Opus 0, mini ≈ 1.1 h.
