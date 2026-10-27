# DEEPITER: planner-driven second retrieval pass on the deep thinking tier — NO at the slice (criterion DEEPITER-criterion.md sha 432fddf9…, arm I; 2026-10-10)

TL;DR: on the recommended deep configuration (dt512: Qwen3.6-35B + thinking 512) a no-thinking planner call named ≤ 2 follow-up searches, their on-topic passages joined the sources (budget 800) before the unchanged thinking answer. On the random20-v02 slice (s42) the planner fired on 12/20 items (+3 sources median, 41 in total) and the answers did not improve: Haiku paired Δ **+0.006 (−0.041…+0.048)**, h2h 11/2/7 → near-miss rule → Opus N = 4 on the same 20 ids: **−0.019 (−0.046…+0.008)**, floor-adj −0.023, h2h 4/9/7, wins 0/0 → **NO** (the LEVER threshold +0.03 is outside the Opus CI). Cost: p50 107 s vs 81 s (+32 %), prompt 587 vs 342 tokens. Same pattern as DEEPWIKI (−0.034, pack crowds the slots) and DEEPRERANK step 0 (+2 gold items of 39): more or re-ordered sources do not move the 35B reader; the coverage limit is what the kit contains, not how much of it reaches the prompt.

| slice 20 (random20-v02, s42) | I (DEEPITER) | H (dt512) | paired I − H |
|---|---|---|---|
| Haiku 5.5-low ratio | 0.577 (0.496–0.655) | 0.571 (0.488–0.642) | +0.006 (−0.041…+0.048); floor-adj +0.006; h2h 11/2/7; ties vs ref 2 vs 0 |
| Opus judge.v1 ratio | 0.631 (0.540–0.711) | 0.649 (0.557–0.729) | **−0.019 (−0.046…+0.008)**; floor-adj −0.023 (−0.056…+0.011); h2h 4/9/7 |
| p50 total (mini) | 107.2 s | 81.2 s | +26 s (planner call + 800-token context) |
| prompt tokens (median) | 587 | 342 | |
| follow-ups | 2 on 9 items, 1 on 3, NONE on 3, no deep path on 5 | — | sources added: 41 (median 3 on the 12 items); retrievalMs2 median 0.48 s |

Post-hoc split (one, hypothesis only; aggregates/posthoc-followups-split.opus.json): items where follow-ups added sources (12) mean rubric Δ −0.07 (3 ↑ / 4 = / 5 ↓); planner NONE (3) −0.28 (the planner call alone, i.e. the 800 budget / early load, on 3 items: 0/1/2); no deep path (5) +0.03. Hypothesis: the extra passages displace or dilute the first-pass ones under compression; nothing suggests a routed variant.

Method: mini tree `be-0cfd4a77-deepiter` = rsync of -dt512 + `deepiter.vs-dt512.patch` (a83bead8…; cumulative ad86e920…; content hash 040be888…) + adapter boar-eval 4a22a4e (6298e5d3…); runner `deepiter-remote-run.sh` (cb60971a…); requests = H's v0.2 s42 with `deepIterFollowups: 2` (slice sha d2b1a146…); smoke 3/3 PASS (`boar-eval/runs/kiln/deepiter/`); `arm.sh chain` → L1 Haiku vs H's slice rows (judged for this arm, 40 Haiku) → Opus vs H's Opus rows (dhv-H-v02-s42). Aggregates: `aggregates/L1-IvsH-slice.haiku55-low.json`, `L2-IvsH-slice.opus.json`, `followups-I-slice.json`, `think-I-slice.json`. Engine/adapter: `README.md`; `deepIterFollowups: 0` reproduces dt512 byte-identically (6/6 differential scenarios).

Not run: full 110, V-para. Verdict strength: slice only (n = 20, Opus CI −0.046…+0.008): "no gain detected; a gain ≥ +0.03 raw is excluded at the slice". Exposure: v0.2 1 smoke (3) + 1 slice generation; Haiku 20 ids (40) + H control 20 ids (40); Opus 20 ids (40).
