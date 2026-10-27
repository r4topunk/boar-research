# DEEPCOVER — key-point enumeration in the reasoning + 120–200-word answer (cap 300) on the deep thinking tier (2026-10-12; criterion `DEEPCOVER-criterion.md` sha e325ab46…)

**Verdict: NO at the slice.** On the random20-v02 slice (s42), Haiku 5.5-low N=4 paired vs H: C 0.575 vs H 0.571, Δ +0.005 (−0.040…+0.046), h2h 10/1/9 → not a promotion; Δ > 0 → Opus N=4 on the same 20 ids: **C 0.623 (0.537–0.702) vs H 0.649, Δ −0.027 (−0.077…+0.019)**, floor-adj −0.033 (−0.100…+0.024), h2h 7/5/8, wins 0/0. A gain ≥ +0.03 raw is excluded at the slice; no full-set judging, no V-para judging. Per dimension (Opus, slice): correctness **0.707 vs 0.818 (−0.11)**, completeness 0.605 vs 0.572 (+0.03), usefulness 0.556 vs 0.556. The instruction buys a little completeness and pays for it in correctness: the model asserts facts it does not hold (the COMPLETE failure mode of the 4B, milder on the 35B). Answers 168 words p50 vs 60 (full v0.2), 32/90 at the 300-cap edge; +12 % total time.

| stage | n | judge | C | H | Δ (CI) | h2h | cost |
|---|---|---|---|---|---|---|---|
| smoke (3 v0.1) | 3 | — | PASS (infra) | | | | mini 6 min |
| slice random20-v02 s42 | 20 | Haiku N=4 | 0.575 | 0.571 | +0.005 (−0.040…+0.046) | 10/1/9 | 40 Haiku (+ H rows reused) |
| same 20 ids | 20 | Opus N=4 | 0.623 | 0.649 | **−0.027 (−0.077…+0.019)** | 7/5/8 | 40 Opus |

Method: mini tree `be-0cfd4a77-deepcover` = dt512 + `deepcover.vs-dt512.patch` (180adac4…, default-off differential 6/6 byte-identical vs dt512, tests 3); `settings.deepCover: true`; requests = H's (kit, seed 42). Control H = dt512 rows (Haiku slice rows, Opus L2-H-1seed). Pre-generated and left unjudged: full v0.2 (`dc-C-v02-s42`, 110, 0 errors) and V-para s42 (`dc-C-vpara-s42`, 58); they stay on disk for a later labelled measurement if a META tick finds budget idle.
Reading for the backlog: prompt-side coverage on the deep tier is closed (DEEPFULL persona, DEEPCOVER enumeration): the model does not hold the missing facts (LOSSMAP absent-knowledge 55–59 %), so asking for them produces wrong ones. Levers left: kit content and model knowledge.
Exposure: v0.2 smoke 3 + slice 20 + full 110 generations, V-para 58 generation; Haiku 40 (C) ; Opus 40 (C). Verdict strength: slice only (n = 20).
