# Bounty board: poidh #31 (the post author, >50% of internet + frontier AI)

TL;DR: one goal, English only, one scoreboard. Each front has one owner, one metric and one next step. An idea that doesn't move a row below is parked.

## Scoreboard (EN, Android 12 GB tier)

Headline = floor-adjusted ratio + pairwise win/tie/loss; raw ratio second. Bar is not met: floor-adjusted 0.40 on v0.2, 0.26 on V-para, 0 wins on either.

**How to read the ratio.** A blank or wrong answer still scores 1/5 on each axis, so an always-decline system gets raw ≈ 0.31 (D = 0.306) for free. Floor-adjusted = Σ(S − 1) / Σ(R − 1) (rubric minimum removed from BOAR and reference); a second view, above-decline = (raw − D) / (1 − D), is lower still.
<!-- src: PIPELINE-AUDIT-2026-10-06 §1; formula verified in boar-eval/bench/v0.2/plan/floor_metrics.py L7-8 (above_min, above_decl) -->

<!-- src: PIPELINE-AUDIT-2026-10-06 §1 (rows 3-5); CLAIM-RESULTS-cut6.md (2-seed, device row from QUEUE.md A15 FINAL) -->
| Metric | Now | Target | Source |
|---|---|---|---|
| **V-para (the post author-style, n=51, blind), 4B** | **floor-adjusted 0.26** · win 0/51 · raw 0.413 · items ≥ 3/5: 2% · correctness ≤ 2 on 49%; venue items 0/7 | floor-adjusted ≥ 0.50 (audit D1) | blind/V-para/runs-cut3 (= cut 6, CLAIM-RESULTS-cut6) |
| V-para anchors, no web (same judge) | Haiku 0.588 (floor-adj 0.48) · Sonnet 0.961 · Opus 1.044 | ≥ Haiku-no-web: not met | runs-cut3/anchors |
| **v0.2 held-out (now dev: burnt), cut 6, 4B** | **floor-adjusted 0.40 (0.397)** · win/tie/loss **0/0/110** · raw 0.519 (s42) · items ≥ 3/5: 41%; 2-seed raw 0.512 (0.478–0.549), floor-removed 0.388 | final number needs v0.3 (non-Claude writer) | blind/bench-v02/runs-cut6 |
| Device vs desktop (v0.1 EN 57, cut 6, A15 8 GB) | phone 0.561 (CI 0.507–0.617) vs desktop 0.558 / 0.560 → device = desktop on quality; fast p50 49 s / p90 77 s | n/a | QUEUE.md "A15 FINAL device result" |
| v0.1 dev ratio, 4B | 0.51–0.53 (raw) | ↑ | Kiln L2s |
| Retrieval ceiling (v0.1 EN 57, oracle) | engine 0.507 · Q450 0.567 · R450 0.606 · Haiku 0.653; model sweep closed (9B = 4B); big packs KILL; rv2 KILL (−0.021 despite gold-in-context 7 → 18); answer style KILL (S2 −0.031, S3 −0.006) | engine → ≥ 0.55 | Sonar + Anvil diagnosis |
| the post author V-exact (11) | **cut 2: judge items 0.510 (plain CI 0.303–0.739, n=5)** (was 0.390); ≥ Haiku on 2/5 (Paris–Rome 0.94, PQ signatures 0.53); Mozi 0.56, Japan 0.36, Gríma 0.20 (false correction); venues 6/6, GPS city 3/3 | ≥ Haiku-no-web per item | bench-vslice/VSLICE-REPORT.cut2.md |
| Deep tier (35B) ratio, reported separately | ≈ 0.57 (v0.1, desktop) | device-confirmed | Forge DEEP-TIER-PLAN |
| Time to first text, 12 GB phone, 4B | est. 8.5–12 s; total 20–27 s | total ≤ 15 s | Forge speed levers + bench app |

### Levers measured 2026-10-06 (walls + the one above-noise lever)
<!-- src: PIPELINE-AUDIT-2026-10-06 §6; FACTS projection from arms/facts/FACTS-JUDGE.md -->
| Lever | Result | Status |
|---|---|---|
| Model size (DEEPREAD, 35B + gold passages) | +0.06 is knowledge only; reading +0.03 (0.634 vs 4B 0.606, floor-adj 0.541) | wall |
| Retrieval (scorecard, NAMEDSLOT) | captures +0.02 of the +0.10 oracle gap; recall@5 0.333 | wall; NAMEDSLOT NOT ADOPTED |
| Completeness prompt (COMPLETE) | correctness 3.89 → 3.10 (−0.80), confident-wrong 7 → 15 | NO |
| **FACTS** (structured facts, no model) | projected v0.1 Δ ≈ +0.027; blind 0/20 false positives, recall 67% | ADOPT (research-only); r4 pending |

## Fronts

| # | Front | Owner | Metric it moves | Next step |
|---|---|---|---|---|
| 1 | Default model for the 12 GB tier (dense 7–9B, newer 4B-class) | Anvil | ratio | closed-book screen → top 1–2 through the full engine (L1 → L2) |
| 2 | the bounty post's questions: pack coverage ≤ 50 GB, places/GPS, Gríma, Paris–Rome | Sonar | V-exact, V-para | coverage table + pack additions |
| 3 | Bounty eval + claim report (EN primary) | Compass | trust in the number | V-exact run, V-para, claim_report |
| 4 | BOAR Bench device app + speed levers + deep-tier plan | Forge | speed, device numbers | BENCH-APP.md → MVP |
| 5 | Runs: v0.2 L3 → V-exact → model screens → hf3 | Kiln | all | queue in this order |

## Rules for faster iteration

- **English only.** PT/ES work is parked, and existing PT/ES code is left untuned.
- **Funnel:**
  - L0 is seconds.
  - L1 is the EN slice with 24 items: closed-book for models, full engine for technique.
  - L2 is v0.1 EN, with a frozen criterion.
  - L3 is v0.2 or V-para, run only for the ship candidate.
- **Time box:** 2 h per idea, or it is killed.
- **No human sign-offs.** An Opus reviewer agent decides content questions.
- **Safety:** only fixes for issues a demo would expose in English.
- **the app maintainer's app:** no work inside it. Measure through boar-eval plus BOAR Bench, and open the PR to the app maintainer at the end.
