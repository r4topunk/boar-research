# A1-RC1-SHIPPED-U (2026-10-21): KILLED. The shipped RC1 scores U 0.143 under Opus, 0.12 BELOW the closed-book 1.5B proxy, with 69 confident errors per 100

Criterion A1-criterion.md (sha 0475ac51..., rnd dcdec468), frozen before the phone run and before any judge call. Tools: tools/a1_traces.py, a1_judge.sh, a1_analyze.py.
Output: a1/aggregates/A1-RC1-SHIPPED-U.json (sha 3116407c0f29aca0...), judgments a1/judgments/rc1-shipped.opus.judgments.jsonl (sha bf6bab00c7222872...).
Cost: 102 Opus judge.v1 calls (cap 120; 0 retries, 0 floor-scored), 0 Haiku, 0 paid, 0 desktop generation. About 28 phone minutes.

## System (default install, not 'only model')
- team.sopa.aoair 2.0.0-rc1 (apk 2ef43258...) on the Pixel 8a, as installed: Qwen2.5-1.5B Q4_K_M, eval-hook style Detailed/1024, Standard KB, 0 packs. Nothing installed or changed.
- Request rc-cv5-51-15b (warm-up + 51 v0.1 dev ids, CV5 frame), one run. Raw: handoff/pixel8-2026-10-20/bench/results/rc-cv5-51-15b/ (rows.jsonl sha df26ed79...).

## Run readout (rc_eval)
- 52/52 success (51 scored), 0 empty, 0 LMK, 0 app deaths. Retrieval used on 1/51 (lan-exp-005, title Sahara): effectively closed-book.
- The app routed dng-005 to personality succinct by itself (55 tokens); the other 50 ran Detailed. Tokens p50 384, max 696, 0 hit 1024.
- Answer p50 33.0 s (p90 47.5), TTFT p50 1.8 s, decode p50 12.3 tok/s (first 10 rows 17.8, last 10 12.1). PSS peak 2.34 GB, RSS 2.58 GB.
- Battery 26.4 C before, 36.9 C after (max 36.9); thermal status 0 before, 1 from about 6.4 min to the end. No thermal gate (not a speed run): speed numbers here are thermally degraded and not for the page.

## Levels (Opus judge.v1, both orders, v0.1 dev 51, one run; item-cluster bootstrap B 2000 seed 11)
| row | U floor-adj (CI) | raw ratio | U_D2S | win/tie/loss vs ref | correct / CE / decline per 100 |
|---|---|---|---|---|---|
| **RC1 1.5B shipped (Pixel, Detailed)** | **0.143 (0.103-0.188)** | 0.316 | 0.143 | 0/0/51 | **2.0 / 68.6 / 0** |
| 1.5B closed-book (desktop, K0 frame) | 0.261 (0.189-0.342) | 0.412 | 0.258 | 1/0/50 | 27.5 / 31.4 / 2.0 |
| 1.7B K0 bench (desktop) | 0.351 (0.279-0.437) | 0.483 | 0.351 | 1/3/47 | 35.3 / 15.7 / 0 |
| Gemma E2B bench (desktop) | 0.362 (0.290-0.444) | 0.492 | 0.359 | 1/3/47 | 43.1 / 7.8 / 2.0 |
| 4B cut 7 bench (Pixel) | 0.460 (0.387-0.537) | 0.570 | 0.460 | 1/3/47 | 49.0 / 9.8 / 0 |
U_net (D 0.058) for RC1 = 0.090. Win-rate RC1 0/51 (CI 0-0). RC1 CE per 100 CI 54.9-80.4; correct 0-5.9.

## Paired (same 51 ids, same draws)
| pair | dU (CI) | better/worse items | d CE per 100 (CI) | d correct per 100 (CI) |
|---|---|---|---|---|
| 1.7B bench - RC1 | +0.209 (+0.134...+0.288) | 37/8 | -52.8 (-66.7...-39.2) | +33.3 (+19.6...+47.1) |
| RC1 - 1.5B closed-book | -0.119 (-0.182...-0.065) | 11/26 | +37.1 (+23.5...+51.0) | -25.6 (-39.2...-13.7) |
| Gemma bench - RC1 | +0.219 (+0.147...+0.296) | 42/5 | -60.5 | +40.8 |
| 4B bench - RC1 | +0.318 (+0.249...+0.388) | 43/3 | -58.6 | +46.9 |
U_D2S pairs move by at most 0.004 (no decline detected in RC1 texts).

## Verdict vs the frozen rule
- PARTIAL: no (51/51 answered, 0 LMK). PROXY-HOLDS: **no** (|0.143 - 0.261| = 0.118 > 0.05) -> **KILLED**.
- BELOW-ENGINE: yes (1.7B - RC1 +0.209, CI low +0.134 > 0). Retrieval <= 5/51: yes (1/51). Same flags under U_D2S.
- The prior failed: the closed-book 1.5B rung does NOT stand in for the app. With the same model, the app's Detailed answers lose 0.12 U and add 37 confident errors per 100 against the closed-book rung. Untested reading: the long Detailed answers pile up wrong specifics that Opus scores corr 1 (CE 35/51 rows).
- Spot check: 51/51 row questions byte-equal the v0.1 text; rationales name concrete factual errors (e.g. vit-hum-005, lan-rsn-001).

## Sentences (each names judge, set, n, one run)
- Claim v5 section 0: "The submitted app as shipped (RC1 default install: Qwen2.5-1.5B, Detailed, built-in knowledge base, no packs) scores U 0.14 (CI 0.10-0.19) on 51 v0.1 dev questions under an Opus judge, one run, with 69 confident errors and 2 correct answers per 100 and 0 wins against the reference; the bench engine's 1.7B scores 0.35 and its 4B 0.46 on the same questions."
- Page: "Measured on the phone as shipped, the submitted app's default 1.5B answers score 0.14 U (Opus, 51 dev questions, one run), below even the same model answering closed-book in our engine (0.26): the shipped configuration, not the model, costs about 0.12 U and adds about 37 confident errors per 100."
- Do NOT use the closed-book 1.5B rung (0.261) as a proxy for the app, or "effectively the 1.5B rung", anywhere.

## Deviations and limits
- Wi-Fi radio was connected under airplane mode (airplane on, Wi-Fi override), as in rc-speed9-15b; settings not touched. Retrieval titles show only Standard KB content.
- No thermal gate (task rule; the hypothesis had 31.0 C). Request id rc-cv5-51-15b and criterion file A1-criterion.md (the hypothesis named rc-v01-51-15b and RC1-SHIPPED-criterion.md).
- DECLINE2STAGE stage 1 by the labels.is_decline stand-in (0 Haiku). One run, one seed, n 51 dev; comparison rungs are other styles/frames (desktop K0, Pixel cut 7).
