# C2-REPLICA-FIDELITY (2026-10-21): PASS. The desktop replica of RC1's default pipeline reproduces the phone's 0.14 under Opus; Succinct lifts it by +0.115

Criterion C2-criterion.md (sha ef72a1ef..., rnd f6f0377b), frozen before any Opus call. Tools: tools/c2_judge.sh, tools/c2_analyze.py (estimator copied from a1_analyze.py).
Output: aggregates/C2-REPLICA.json (sha af2eeefe...); judgments/native-N-D-v01-s42.opus.judgments.jsonl (4b6fadec...), native-N-S-v01-s42.opus.judgments.jsonl (096af182...).
Cost: 204 Opus judge.v1 calls (N-D 102, N-S 102; cap 210; 0 retries, 0 floor-scored), 0 Haiku, 0 paid, 0 generation (S3 traces reused).

## Rows (Opus judge.v1, both orders, v0.1 dev 51 CV5 ids, one run each; item-cluster bootstrap B 2000 seed 11)
| row | host | U floor-adj (CI) | raw | win/tie/loss | correct / CE / decline per 100 | tokens p50 |
|---|---|---|---|---|---|---|
| RC1 shipped 1.5B, Detailed, KB-only (A1) | Pixel 8a | 0.143 (0.103-0.188) | 0.316 | 0/0/51 | 2.0 / 68.6 / 0 | 384 |
| **N-D replica: his pipeline, Detailed, KB-only** | mini (JVM harness + b11010) | **0.150 (0.112-0.192)** | 0.321 | 0/0/51 | 2.0 / 60.8 / 0 | 392 |
| **N-S: his pipeline, Succinct, KB-only** | mini | **0.265 (0.189-0.347)** | 0.415 | 1/1/49 | 27.5 / 39.2 / 0 | 44 |
| 1.5B closed-book, our engine (L0) | desktop | 0.261 (0.189-0.342) | 0.412 | 1/0/50 | 27.5 / 31.4 / 2.0 | - |
| our 1.7B K0 bench (L1) | desktop | 0.351 (0.279-0.437) | 0.483 | 1/3/47 | 35.3 / 15.7 / 0 | - |
| our 4B cut 7 bench (L3) | Pixel 8a | 0.460 (0.387-0.537) | 0.570 | 1/3/47 | 49.0 / 9.8 / 0 | - |
U_D2S equals U for N-D, N-S and RC1 (no decline detected). Validity: 51/51 non-empty texts per arm, every id judged in both orders.

## Fidelity (frozen rule: |dU| <= 0.05 AND Spearman >= 0.6 AND paired CI includes 0)
- N-D - RC1 = **+0.007 (-0.025...+0.039)**, raw +0.005 (-0.021...+0.031); better/worse 13/13. |dU| 0.007 <= 0.05: yes. CI includes 0: yes.
- Per-item Spearman of s (N-D vs RC1) = **0.81** >= 0.6: yes. -> **FIDELITY PASS**.
- Secondary: EQUIVALENT yes (paired CI inside +-0.05). CE-REPRODUCED yes (N-D 60.8 per 100 >= 55; RC1 68.6, d -7.6 (-19.6...+3.9)).
- Reading: the 0.14 is a property of the shipped configuration (model + Detailed + KB-only), not of the Pixel, its thermals or one bad run.

## Attribution (persona, his pipeline, Opus)
- N-S - N-D = **+0.115 (+0.051...+0.181)** floor-adj; raw **+0.093 (+0.042...+0.145)**; better/worse 26/11. PERSONA-CONFIRMED (CI low > 0).
  Haiku S3 had raw +0.077 (+0.038...+0.120): the Opus raw CI contains it -> consistent; Opus spreads it a little, as predicted.
- Per 100: correct +25.5 (+13.7...+39.2), CE -21.9 (-37.3...-7.8).
- N-S - RC1 (Succinct stand-in vs the phone) = +0.122 (+0.063...+0.187); CE per 100 -29.4 (-41.2...-17.6), correct +25.5.
- N-S - 1.5B closed-book = +0.004 (-0.045...+0.055): with KB-only retrieval (1/51 fires), the Succinct pipeline scores as the model closed-book.
- Remaining gap to our engine: 1.7B K0 - N-S +0.087 (+0.008...+0.167), i.e. model + packs + layers, not persona.
- Prediction check: U(N-D) 0.15 in the predicted 0.13-0.15 band; Spearman beat the predicted 0.4-0.7; N-S - N-D +0.115 vs predicted ~+0.10.

## Sentences (each names judge, set, n, one run)
- NOTE-1 (Succinct): "On the same model and your own pipeline, switching the default persona from Detailed to Succinct raises the score from 0.15 to 0.26 U (Opus, 51 dev questions, one run each; +0.115, CI +0.05...+0.18) and cuts confident errors from 61 to 39 per 100; a desktop replica of your default reproduces the phone's 0.14."
- Page: "A desktop replica of the app's default pipeline reproduces the phone's 0.14 (0.15; Opus, 51 dev questions, one run each, per-item rank correlation 0.81), so the gap to our engine comes from configuration, not the device; the Detailed persona alone accounts for about 0.12 of it."
- Label: 'replica' (cross-host: Pixel app vs mini JVM harness), never 'same-host'. N-S may stand in for 'RC1 with Succinct' with this label.

## Deviations and limits
- None from the criterion. One run per arm, one seed (mini s42; phone app default), n 51 dev; desktop embeddings via llama-server b11010 CPU, not his JNI build.
- On the phone the app routed dng-005 to Succinct (55 tokens); in the harness all 51 N-D rows ran the Detailed persona path. Runsheet row 0b (installed RC1 catalog vs snapshot 5f8cc8f4) not checked here: the replica sentence is scoped to RC1.
- DECLINE2STAGE stage 1 by the labels.is_decline stand-in (0 Haiku). Comparison rungs are other frames/hosts (desktop K0, Pixel cut 7).
