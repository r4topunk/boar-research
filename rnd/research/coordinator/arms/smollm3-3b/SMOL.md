# SMOLLM3-3B: NO-GO on all 4 GATE v2 screens (2026-10-21)

TL;DR: SmolLM3-3B (Q4_K_M, thinking off) as a drop-in for Qwen3-1.7B fixes enough problems on K0 (net 16 vendor / 13 engine, bar 10) but fails the false-refusal and U_cov clauses on every screen. Every false refusal is a dropped/stripped [n] citation that the engine pushes behind the warning line: the same failure as MINISTRAL, QWEN35-2B, FOTAPOL, JAN. No stage 2. GGUF deleted from the mini (class A).

Criterion: SMOL-criterion.md, sha256 a9f5143d... (matches SMOL-criterion.sha256). Gate: GATE v2 (arms/null-cal/GATE-V2.md 34ada53f, screen_gate_v2.py fa726fc0). Judge: Haiku 5.5-low, judge.v1-low, N 4, both orders. Dev sets only (MAIN 97 + 180 self-tests pool screens).

## 1. Onboarding (stage 0)
| check | result |
|---|---|
| model | HuggingFaceTB/SmolLM3-3B @ a07cc9a0 (Apache-2.0) via bartowski GGUF @ 86b3536e, Q4_K_M 1,915,305,792 B, sha 51973255 |
| template | GGUF-embedded = HF chat_template.jinja (cmp identical); with --reasoning off renders "Reasoning Mode: /no_think" + empty think block (onboarding/renders.json). Without the flag (C_gguf_noflag_none) the empty think block is absent: a native app must pass enable_thinking false explicitly |
| speed (mini llama-bench tg128) | 32.88 / 32.47 vs 1.7B 56.35 / 53.68 tok/s, ratio 0.594 (0.583, 0.605) -> projected Pixel 8a 8.3 tok/s (7.1-9.5); criterion 3(b) holds |
| smoke 5 (vendor) | 5/5, U 0.462, warned 2, 10 Haiku calls; engine-sampler smoke generated 5/5 but its judge failed in 4 s (0 judgments recorded) |

## 2. Screens (gate lines verbatim from aggregates/*.gate2.txt)
| run | net (bar) | fixed_u (by refusal) | new CEu | false refusals (max) | U_cov delta (min) | verdict |
|---|---|---|---|---|---|---|
| V K0 (smollm3-3b, T 0.6) | **16** (10) | 17 (7) | 1 | **4/20** (2) | **-0.068** [-0.131, -0.006] (-0.059) | NO-GO |
| V K1 | 10 (9) | 10 (5) | 0 | **7/20** (4) | **-0.129** [-0.207, -0.060] (-0.071) | NO-GO |
| E K0 (smollm3-3b-eng, 0.7/40/0.95/0.05) | **13** (10) | 14 (8) | 1 | **3/20** (2) | **-0.072** [-0.128, -0.022] (-0.059) | NO-GO |
| E K1 | 12 (9) | 12 (7) | 0 | **6/20** (4) | **-0.128** [-0.208, -0.055] (-0.071) | NO-GO |
Stage-2 entry (criterion 3) needs GO on K0: neither variant -> stage 2 not run. Sanity (criterion 2) clean on all 4: traces 50/50 and 41/41, 0 error rows, 0 generation_failed, model.sha256 = 51973255 on every trace, 0 reasoning-token rows, 0 think-tag leaks, temperature 0.6 (V) / 0.7 (E) on every row (no health-routed generation in these screens, so the health T 0 clause is vacuous).

## 3. Diagnostics (tools/extras.py, 0 LLM; aggregates/*.extras.json)
| run | [n] kept on control-cited items | cand cited / all | warned (warning line) ctl -> cand | uncited-release rows | FR that are citation drops | refusal-fixes that are citation drops | non-refusal fixes - new CEu | out tokens median ctl -> cand | mini wall ratio |
|---|---|---|---|---|---|---|---|---|---|
| V K0 | 6/17 (35 %) | 6/50 | 0 -> 11 | 11 | 4/4 | 7/7 | 10 - 1 = 9 | 41.5 -> 39.5 | 1.88x |
| V K1 | 16/28 (57 %) | 16/41 | 0 -> 12 | 12 | 7/7 | 5/5 | 5 - 0 = 5 | 44 -> 41 | 1.81x |
| E K0 | 6/17 (35 %) | 6/50 | 0 -> 11 | 11 | 3/3 | 8/8 | 6 - 1 = 5 | 41.5 -> 34.5 | 1.85x |
| E K1 | 15/28 (54 %) | 15/41 | 0 -> 13 | 13 | 6/6 | 7/7 | 5 - 0 = 5 | 44 -> 43 | 1.84x |
- Mechanism: every warned candidate row carries grounding:compact-decline-released-uncited-with-sources (some also -all-citations-removed); the 1.7B control has 0 such rows. All 20 false refusals across the 4 runs were cited by the control and uncited by SmolLM3. The same mechanism produces 27 of the 53 "fixes" (refusals of problems), so the net is inflated by refusal.
- Without refusal fixes the lever is at the null: answer-quality fixes net 5-9 per screen vs null raw fixes 6-10 (GATE-V2 3, of which 1-3 by refusal). Only V K0 (9) is marginally above the null non-refusal level (4-8).
- Length is not the issue (answers as short as the 1.7B, unlike Ministral/Qwen3.5-2B 2x); latency 1.8-1.9x the 1.7B on the mini (decode median 32-34 tok/s), consistent with the 0.59 tg128 ratio.
- Sentinels worse (report only): V K0 9, V K1 3, E K0 8, E K1 5; one new CEu (st-qa-money-se-008, corr 4.0 -> 1.0) in both K0 runs.

## 4. Reading and next
- Verdict: **NO-GO** (all 4); stage 2 not run; SmolLM3 drop-in closed.
- Follow-up candidate (not run, not in this criterion): a SMOLCITE arm on the MIN3CITE pattern (citation-compliant prompt v2 passed stage 2 for Ministral, +0.062). SmolLM3 is the better fit for that than Ministral on cost (answers ~40 tokens, wall 1.85x vs 2.9x) and its K0 fixes without refusal (9) are the highest of the citation-dropping models. CITEFIX's open lever (a paraphrase-tolerant support check) would also apply. Needs a re-download (MODELS.md row).

## 5. Spend
Haiku: screens 364 (V K0 100, V K1 82, E K0 100, E K1 82; ALLDONE lines in screens/logs/*.log) + onboarding smoke 10 (vendor) + 0 recorded (engine smoke, judge failed) = **374 of the 700 cap**. 0 Opus, 0 paid. This report: 0 calls.

## 6. Paths
- Criterion/patches: SMOL-criterion.md (+ .sha256), smollm3-3b.patch (c623338f), smollm3-3b-engsamp.patch (0fae1ba0)
- Screens: screens/{smollm3-3b,smollm3-3b-eng}/{traces,judgments,aggregates}/ (gate2.txt/json, extras.json), screens/logs/
- Onboarding: onboarding/ (bench/, renders.json, templates, smoke-vendor/); engine smoke under arms/smol3e/
- Disk: GGUF deleted from the mini 2026-10-21 02:22 (rnd/kiln/MODELS.md row, rnd/kiln/DISK-LOG.md line, free 26.9 -> 28.6 GiB)
