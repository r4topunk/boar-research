# Draft reply to the app maintainer's PR #85 questions (for r4to to post as himself; English)

## Public comment (no absolute native-app scores; the full breakdown is in the private handoff)

Thanks. On the two questions:

**1. What made the most difference.** On the X6, both builds answered the same 60 public v0.1 questions; the judge scored 57 of them (the three venue questions are excluded by the protocol). Grouping the paired per-item scores by the cut 7 mechanism that handled each question:

| Mechanism in cut 7 | questions | share of the gap between the two builds | per-question lift |
|---|---|---|---|
| Emergency / health path (detector → first-aid card or strict safe excerpt) | 12 | ≈ 56 % | large (cut 7 ahead on 9 of 12) |
| 4B answers with the grounding rules (on-topic keep, no-source handling, FACTS cards where they fire) | 42 | ≈ 30 % | small but consistent (ahead on 22, behind on 12) |
| Calculator / unit-conversion path | 2 | ≈ 22 % | very large (ahead on both; the model path invented context) |
| Extractive instant path | 1 | negative | the one case where the native answer was better |

So the porting order the data supports: (a) the emergency/health path first (detector + cards + strict grounding), (b) the calculator path, which is tiny to port and removes the invented-context failure you saw with 30 °C, (c) the grounding rules on the 4B path. Caveat: 57 dev questions, one run per build, Haiku judge; the native build was the Oct 14 dev build, not the release. Send the release build's traces (v0.1 60 + longsession-v1 80) and we re-run the same comparison.

**2. Wiring commits.** They are independent of the engine (they touch only `src/ui-android/**` and `src/models/settings.ts`; the engine dirs are byte-identical before and after them). `main` can take the engine first: say the word and we split the branch into PR-1a (engine, the first 14 commits) and PR-1b (chat wiring) with no other change.

CodeRabbit's five findings are being fixed on the branch now (detector re-init on failed load, the Portuguese/Spanish word list, the cold-load warnings, the frozen-prompt test, and the KV session race); the identity check against the measured run will be re-run after the fix commit.

## Private breakdown (handoff, not for the PR): paired on 57 ids, Haiku L1
ALL: cut 7 0.529 vs native (10-14 dev build) 0.440, Δ +0.089. Health/grounding guard (12): 0.688 vs 0.463 (+0.225, 9/2). 4B plain (42): 0.474 vs 0.436 (+0.038, 22/12). Calculator (2): 0.922 vs 0.315 (+0.607, 2/0). Extractive (1): 0.267 vs 0.600 (−0.333). Health-related items (8): 0.578 vs 0.475.

## Correction (posted on the PR, 10-15): the 12 guard items = 4 first-aid cards (first-aid cards: n=4 0.711 vs 0.373 Δ+0.338 share 27% ahead 4/4) + 8 FACTS cards (FACTS cards: n=8 0.677 vs 0.511 Δ+0.166 share 29% ahead 5/8).
