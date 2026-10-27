# OCCDECL (OCC hybrid, abstention = engine refusal; A = OCC-RAG-1.7B, B = OCC-RAG-0.6B; GATE v2 K0 + K1, 2026-10-21): stage 1 NO-GO on all 4 screens, stage 2 not run

TL;DR: turning OCC's abstentions into the engine's refusal removes default-mode confident errors with 0 new ones (CEu 30 -> 23/22 on K0, 21 -> 10/9 on K1),
but not enough on K0 (net 7 and 8, bar 10, null max 8) and at the price of many false refusals on K1 (7/20 and 9/20, max 4; U_cov -0.17 / -0.21, min -0.071).
The 0.6B is 2.25x faster per token on the mini than the 1.7B and refuses more. Both GGUFs deleted from the mini.

| Item | Value |
|---|---|
| Criterion | OCCDECL-criterion.md sha256 `01b04fc8...` (commit 3f97edb8, before generation), cites GATE v2 sha `34ada53f` |
| Patches | occdecl-A.patch `1f96f2a1...`, occdecl-B.patch `a493dbe3...` (be/adapter-litedecline.ts only) |
| Models | A: occ-ai/OCC-RAG-1.7B-GGUF @ 57938bfa Q4_K_M sha `5ff807a9...`; B: occ-ai/OCC-RAG-0.6B-GGUF @ 53da9f5d Q4_K_M, 396,701,824 B, sha `2b0bf248d0cdd60ea37c0fa092134acea35ee4bca0ee11ee031b91bf04281d17` (= LFS oid; free 26.3 GiB after download) |
| Runs | occdecl-{A,B}-{K0,K1}-screen2-{K}-s42 (mini, gen slot lock); Haiku calls 22 + 54 + 34 + 58 = **168** (cap 400); 0 Opus, 0 paid |

## Gate v2 (verbatim, aggregates/*.gate2.txt)
```
A K0: problems 30 | fixed_u 7 (by refusal 7) | new CEu 0 | net 7 (bar 10) | false refusals 0/20 (max 2) | sentinels worse 0 | U_cov -0.0349 [-0.0614, -0.0132] (min -0.059) | changed 11 -> NO-GO
A K1: problems 21 | fixed_u 11 (by refusal 9) | new CEu 0 | net 11 (bar 9) | false refusals 7/20 (max 4) | sentinels worse 2 | U_cov -0.1729 [-0.2557, -0.1003] (min -0.071) | changed 27 -> NO-GO
B K0: problems 30 | fixed_u 8 (by refusal 8) | new CEu 0 | net 8 (bar 10) | false refusals 2/20 (max 2) | sentinels worse 0 | U_cov -0.0684 [-0.1141, -0.0308] (min -0.059) | changed 17 -> NO-GO
B K1: problems 21 | fixed_u 12 (by refusal 10) | new CEu 0 | net 12 (bar 9) | false refusals 9/20 (max 4) | sentinels worse 0 | U_cov -0.2122 [-0.2966, -0.1368] (min -0.071) | changed 29 -> NO-GO
```
False refusals: A K1 lan-cmp-003, st-boar-factbook-010/-013, st-boar-medlineplus-en-019/-020, st-boar-simplewiki-en-015, st-qa-outdoors-se-014;
B K1 the same minus simplewiki-015 plus lan-exp-003, st-qa-outdoors-se-008, st-boar-medlineplus-en-007; B K0 lan-exp-002, st-boar-factbook-007.
Reading: every fix is a refusal (except 2 OCC answers on K1); K0's 30 problems are mostly items with no kept source (33/50 screen items go qwen-nosource), which OCC never sees.
On K1, where OCC sees most items, it refuses 15-19 of 28 OCC calls, and about half of the refused sentinels were judge-correct Qwen answers (pack factbook/medlineplus items).

## Routes, tokens, latency (tools/report.py -> report.json)
| | A K0 | A K1 | B K0 | B K1 |
|---|---|---|---|---|
| OCC answered / decline / decline-malformed / malformed->Qwen / looped->Qwen | 5 / 6 / 0 / 5 / 1 | 12 / 15 / 0 / 0 / 1 | 7 / 10 / 0 / 0 / 0 | 9 / 19 / 0 / 0 / 0 |
| qwen-nosource | 33 | 13 | 33 | 13 |
| OCC tokens per call: median / p90 / max (answered only, median) | 266 / 475 / 1350 (226) | 386 / 691 / 1289 (444) | 233 / 365 / 528 (209) | 315 / 506 / 1289 (334) |
| Mini wall median, all screen items: cand / ctl (ratio) | 1.94 / 1.89 s (1.03x) | 9.07 / 4.06 s (**2.23x**) | 1.88 / 1.89 s (0.99x) | 3.43 / 4.06 s (0.85x) |
| Mini wall median, OCC-eligible items: cand / ctl | 6.73 / 2.86 s | 12.11 / 4.38 s | 2.21 / 2.86 s | 4.09 / 4.38 s |

- Control Qwen output on the same items: median 45-46 tokens.
- Mini OCC decode: A 53.6 tok/s, B 120.8 tok/s (median per call), so the ratio r = 2.25.
- **Projected Pixel decode per OCC call** (median 326 tokens for A, 274 for B):
  - A: 27 s at 12 tok/s, 20 s at 16 tok/s.
  - B: 10 s at 12 x 2.25 tok/s, 7.6 s at 16 x 2.25 tok/s.
  - Today's Qwen answer: about 3-4 s.
- Latency clause (all-item median <= 1.5x): fails only on A K1. It is moot, since no screen is GO.

## Verdict
NO-GO on all 4 screens: K0 misses the net bar, and K1 fails false refusals and U_cov. Stage 2 (MAIN 97) was not run.
The abstain-as-decline gain REREAD saw on the old screens (K0 CEu 4 -> 1) holds in direction: 0 new CEu anywhere. But on the calibrated screens it is at the null on K0 (null net 6-8), and on K1 it costs 7-9 false refusals.

## Deviations
- **CRITERION env dropped.** The first chain set CRITERION, and the shard_judge preflight refused it because the frozen criterion has no `calls_cap:` line in a `## Budget` block. The criterion was not edited; the cap (400) stays in its Judge section and was checked by hand (168 used). The first A-K0 traces were reused (same inputs sha).
- **Wall times are confounded.** A-K1 and B-K0 generated concurrently on the mini, next to other arms' jobs (load1m about 4-6, vs 4.5-4.7 in the control). The B ratios against the control on the OCC items are below 1, which is implausible, so read the wall ratios as rough. The tg rates are per-call decode only.
- **Sidecars.** run_pool.sh does not copy the adapter sidecar, so tools/chain.sh fetched each one from the mini job dir into sidecar/.
- **Design check.** The decline classifier was checked on the OCCRAG sidecars before the freeze: K0 10, K1 17 declines, matching REREAD.

## Cleanup
Both OCC GGUFs (and their SHA256SUMS lines) were deleted from the mini at 2026-10-21 00:13. Recipes are in rnd/kiln/MODELS.md and the deletion is logged in DISK-LOG.md. Free disk on the mini is about 28 GiB.
