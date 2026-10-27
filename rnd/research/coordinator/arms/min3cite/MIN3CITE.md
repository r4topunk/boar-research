# MIN3CITE: Ministral-3-3B + citation-compliant 2-4 sentence prompt (2026-10-21)

TL;DR: **stage 1 GO on both GATE v2 screens** (K0 net 13 / bar 10, FR 0/20, U_cov +0.056; K1 net 11 / bar 9, FR 1/20, U_cov +0.018). The prompt fixed the
failure of MINISTRAL3-3B (dropped/stripped [n] -> warned -> false refusals 3-9/20): citation compliance on source-present answers 0.35 -> 0.94 (K0) and
0.46 -> 0.89 (K1). Cost: answers ~2.2-2.4x the 1.7B's, projected Pixel 8a p50 17.5-21.3 s (K0) / 30.0-33.6 s (K1) vs 5.7-6.6 / 11.4-12.6 s for the 1.7B.
**Stage 2 (MAIN 97, K0) PASS**: U +0.062 [+0.037, +0.089], CE-unwarned rate -0.010; cost ~3x projected phone answer time.

## Setup
- Criterion MIN3CITE-criterion.md sha256 3b17dbfd... (frozen before any judged screen, 0 judge calls before freeze). Patch min3cite.patch = patches/min3cite-v2.patch
  (sha 26f4200a...) = ministral3-3b.patch (Ministral-3-3B-Instruct-2512 Q4_K_M sha 9ed150d4, vendor sampler T 0.1) + prompt.min3cite v2 (2-4 sentences,
  cite each sourced sentence "[n]", one number per bracket, reuse source wording, no source list). No retrieval/routing/decline/citation-check change.
- Screens null-cal/pool/screen2-K0.ids (50: 30 problems + 20 sentinels) and screen2-K1.ids (41: 21 + 20); controls null-cal/control/pool-K{0,1}.json;
  gate tools/screen_gate_v2.py (GATE-V2.md 34ada53f). Generation on the mini, seed 42; Haiku 5.5-low judge.v1-low, N = 4, both orders.

## Smoke (generation only, 10 items: smoke/smoke-K0.ids + smoke-K1.ids; tools/smoke_gen.sh; tools/citecomp.py)
| version | logs | compliant /10 | warned /10 | tokens median |
|---|---|---|---|---|
| min3v base | ministral3-3b/screen/min3v | 2 | 8 | 102 |
| v1 (format + negative examples) | smoke/min3c1-K{0,1}.log, smoke/min3c1/ | 6 | 4 | 84.5 |
| **v2 (frozen)** | smoke/min3c2-K{0,1}.log, smoke/min3c2/ | **10** | **0** | 100 |
| v3 (v2 + under 70 words) | smoke/min3c3-K{0,1}.log, smoke/min3c3/ | 6 | 4 | 77.5 |

## Stage 1 results (aggregates in screen/min3cite/aggregates/*.gate2.{json,txt})
| screen | CE-unwarned ctl -> cand | fixed (by refusal) | new CEu | **net** (bar) | false refusals (max) | U_cov delta [CI] (min) | sentinels worse (report) | verdict |
|---|---|---|---|---|---|---|---|---|
| K0 | 30 -> 17 | 14 (1) | 1 | **13** (10) | 0/20 (2) | +0.056 [+0.012, +0.100] (-0.059) | 10 | **GO** |
| K1 | 21 -> 10 | 12 (2) | 1 | **11** (9) | 1/20 (4) | +0.018 [-0.045, +0.077] (-0.071) | 11 | **GO** |
Pooled vs control: K0 U +0.072 [+0.030, +0.115], CE 17 vs 30; K1 U +0.053 [+0.002, +0.102], CE 11 vs 21. Warned answers 1 (K0) / 3 (K1), control 0.
Compared with min3v (same model, no prompt change): net 17 / 13 but FR 3 / 7 and U_cov -0.032 / -0.123; MIN3CITE trades refusal-driven fixes for real ones.

## Extras (0 LLM)
| | K0 | K1 |
|---|---|---|
| sanity | n 50/50, 0 errors, sha 9ed150d4 all, T 0.1 all, prompt.min3cite v2 all, 0 dead changed | n 41/41, same |
| compliance (source-present): ctl / min3v / cand | 17/17 / 6/17 / **16/17** | 28/28 / 13/28 / **25/28** |
| model-own [n] kept (cand) | 10 | 23 |
| answer tokens median/mean: cand vs ctl | 91 / 97 vs 41.5 / 41 (x2.35) | 91 / 95 vs 44 / 44 (x2.15) |
| sentences median | 4 (ctl 2) | 4 (ctl 2) |
| wall mean totalMs (mini) | 8.2 s vs 2.1 s (x3.86) | 12.2 s vs 3.6 s (x3.37) |
| projected Pixel 8a p50 / p90 (tools/pixel_proj.py) | 17.5-21.3 / 28.4-34.1 s (1.7B 5.7-6.6 / 9.1-10.4) | 30.0-33.6 / 37.9-41.8 s (1.7B 11.4-12.6 / 14.8-15.7) |

## Haiku calls
Screens: K0 100, K1 82 (runs/logs/*.calls; the first attempts at 01:22/01:29 died on the previous account's session limit with 0 judgments written,
STOP files removed, resumed 01:31). Stage 2: 150. Total 332 of cap 450. 0 Opus, 0 paid.

## Stage 2 (MAIN 97, K0) - per criterion
Command: CRITERION=MIN3CITE-criterion.md bash lp-screens/tools/run_arm.sh min3cite K0 main min3cite.patch (log min3cite/stage2-K0-main.log, launched 01:35).
PASS iff U delta >= +0.03 with paired bootstrap CI low > 0 AND CE-unwarned rate change <= +0.02 (ministral3-3b/tools/stage2_verdict.py).
**PASS (02:10, stage2_verdict.py sha e60e7371, unchanged):** U +0.0623 [+0.0366, +0.0891] (need >= +0.03, CI low > 0); CE-unwarned rate 0.072 -> 0.062
(-0.010 [-0.072, +0.052], need <= +0.02); default-mode U 0.257 -> 0.313 (+0.056 [+0.031, +0.083], report only). 75/97 answers changed (22 dead items).
| MAIN 97 | control (1.7B) | MIN3CITE |
|---|---|---|
| CE (all) | 27 | 22 |
| warned (refused in default mode) | 39 | 33 |
| citation compliance, source-present | 18/34 | 24/34 |
| answer tokens median / mean (live 75) | 47 / 46 | 106 / 106 (x2.32) |
| mini wall mean | 1.9 s | 5.4 s (x2.88) |
| projected Pixel 8a p50 / p90 | 6.8-7.9 / 10.3-11.2 s | 21.6-25.6 / 30.6-35.7 s |
Sanity: n 97, 0 errors, sha 9ed150d4, T 0.1 on the 75 generated, prompt v2 all. 150 Haiku (aggregates/min3cite-K0-main-s42.json).
A PASS is a screening result: phone speed and PSS unmeasured; one seed, one pack set (K0).

## Reading
- The MINISTRAL failure was a citation-format problem, and a prompt-only fix removes it: false refusals drop to the null band and U on covered items turns positive.
- A GO is a screening result. Phone cost is the open price: ~3x the 1.7B's answer time projected (decode 6.5-8.7 tok/s, 2x longer answers); PSS unmeasured.
- Ministral GGUF stays on the mini (line still open).
