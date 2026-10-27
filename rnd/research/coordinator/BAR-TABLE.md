# BAR-TABLE: where every measured configuration stands against the bar (frozen definition; 0 judge calls)

Written 2026-10-10 by a coordinator subagent from existing aggregates only (HANDOFF-2026-10-11 §4 step 1). Nothing under `blind/` or `rnd/veil/` was opened, listed or grepped. All numbers are development data. The coordinator hashes this file; §2 and later bar updates go in dated addenda or a new version.

## 0. Target

"Primary research target = V-para floor-adjusted ratio, two seeds (42, 43), Opus judge.v1 both orders, item-bootstrap 95 % CI low ≥ 0.50. Formal rule (analysis-plan §3, r4to 2026-10-02) = raw ratio CI low > 0.50 on V-para and on v0.2. Secondary = floor-adjusted ≥ Haiku 5.5 no-web anchor (0.48 on V-para). Pairwise win-rate is reported, never gated. All current numbers are development data (v0.2 burnt; V-para dev-style after 2026-10-06)."

### Definitions used in this table (from the code, not from prose)
| Column | Definition | Code / JSON key |
|---|---|---|
| raw | Σ mean-rubric(BOAR) / Σ mean-rubric(ref); mean-rubric = mean(correctness, completeness, usefulness), both orders averaged | `floor_metrics.py` → `raw` (paired.mjs → `ratio`) |
| **floor-adj** | **Σ(S − 1) / Σ(R − 1)** (rubric minimum removed). This is the number every report calls "floor-adjusted" (H 0.436, K 0.261). It does **not** use D | `floor_metrics.py` → `above_min`; paired.mjs → `floorAdj` |
| above-decline | (raw − D) / (1 − D), D fixed at 0.306 (analysis-plan §4.2) | `floor_metrics.py` → `above_decl` |
| useful ≥ 3/5 | share of items whose (order-averaged) usefulness ≥ 3. Not computed by any script; only two values exist in prose (K rows, labelled "items ≥ 3/5", PIPELINE-AUDIT l.13–14) | none (0-call computable from `<run>.judgments.jsonl`, `mapped.boar.usefulness`) |
| W/T/L | combined winner vs the reference per item (order disagreement = tie), per seed | paired.mjs → `winsVsRef` / `tiesVsRef` / `lossesVsRef` |
| CI | floor_metrics.py: stratified (by category) two-level bootstrap, 2,000 resamples, seed 11 (plan §3 method). Rows marked "plain" are paired.mjs item bootstrap | — |

Notes: `addendum-05*` does not exist in `boar-eval/bench/v0.2/plan/` (BENCH-V03-SPEC l.75 plans it for v0.3). "Floor-adjusted" and "D = 0.306" belong to two different scales; the target in §0 refers to `above_min`.

### Reading codes
- **MET**: CI low clears the threshold (raw: > 0.50; floor-adj: ≥ 0.50; Haiku parity: ≥ 0.48).
- **STRADDLES**: the CI contains the threshold.
- **SHORT by x**: CI high below the threshold; x = threshold − point estimate.
- Primary (floor-adj) needs 2 seeds on V-para; a 1-seed row gets its reading in brackets (not eligible). Haiku parity exists only on V-para (no Haiku no-web anchor on v0.2).

## 1. Table

Configurations: **K** = 4B claim build (cut 7 = cut 6 on these sets: FACTS fires 0/110 and 0/58); **D** = deep Qwen3.6-35B-A3B, no thinking (DEEPVPARA); **T / TV** = deep + thinking 1024 (DEEPTHINK V-para / DEEPTHINK-V02 v0.2); **H** = deep + thinking 512, the recommended configuration (DT512 / DT512-V02 / SEEDVAR); **Q** = deep + thinking 256 (DT256); **G** = Gemma 4 26B-A4B + thinking 1024 (GEMMATHINK); **Z / ZV** = thinking 4B @ 512 (THINK4B / THINK4B-V02); **Haiku** = Haiku 5.5 no-web anchor; **R2→H, R8→H, R2→TV, R2→D** = hybrid routing simulations (DEEPROUTE-VPARA, descriptive, recombined existing rows).

### 1a. V-para (51 judged ids)

| Row | raw (95 % CI) | floor-adj (CI) | above-decline (CI) | useful ≥ 3/5 | W/T/L vs ref (per seed) | seeds | p50 desktop | judge · source |
|---|---|---|---|---|---|---|---|---|
| **K two-seed** | 0.413 (0.384–0.445) | 0.261 (0.224–0.300) | 0.155 (0.112–0.200) | 2 % ("items ≥ 3/5", PIPELINE-AUDIT l.14) | 0/0/51 · 0/0/51 | 2 (42, 43) | 10.1 s claim run (CLAIM-RESULTS-cut6 "full answer p50"); 6.3 s same-backend C (DEEPVPARA.md l.17) | Opus · arms/deepvpara/aggregates/dv-vpara-2seed.L2.json `floorK` |
| K s42 only | 0.413 (0.381–0.446) | 0.261 (0.222–0.302) | 0.155 (0.109–0.201) | UNKNOWN | 0/0/51 | 1 | as above | Opus · dv-vpara-s42.L2.json `floorK` (point = two-seed; s42 and s43 both 0.413, QUEUE l.872) |
| D | 0.467 (0.439–0.494) | 0.329 (0.294–0.362) | 0.232 (0.192–0.271) | UNKNOWN | 0/0/51 · 0/0/51 | 2 | 33.3 / 30.9 s | Opus · deepvpara/aggregates/dv-vpara-2seed.L2.json `floorD` |
| T (1024) | 0.542 (0.513–0.571) | 0.422 (0.385–0.459) | 0.340 (0.298–0.382) | UNKNOWN | 0/0/51 · 0/0/51 | 2 | 142.9 / 146.0 s | Opus · deepthink/aggregates/L2-TvsD-2seed.opus.json `floorD` (= T); p50 think-T-s42/s43.json |
| **H (512) two-seed** | **0.553 (0.524–0.581)** | **0.436 (0.401–0.472)** | 0.355 (0.315–0.396) | UNKNOWN | 0/0/51 · 0/0/51 | 2 | 78.9 / 79.4 s | Opus · dt512/aggregates/L2-H-2seed.opus.json `H`; p50 think-H-full-s42/s43.json |
| H three-seed | mean 0.550, SD 0.020 (0.533 / 0.572 / 0.544) | mean 0.432, SD 0.025 (0.412 / 0.460 / 0.425) | UNKNOWN | UNKNOWN | 0 wins each seed | 3 (42–44) | s44 80.4 s | Opus · seedvar/aggregates/seedvar-H-3seed.opus.json `acrossSeeds` (plain per-seed CIs only). Pooled 3-seed CI UNKNOWN: dt512/aggregates/L2-H-3seed.opus.json is 0 bytes, paired_gap-Hvs{D,T}-3seed.json 1 byte |
| Q (256) | 0.514 (0.483–0.544) | 0.387 (0.349–0.426) | 0.300 (0.256–0.343) | UNKNOWN | 0/0/51 · 0/0/51 | 2 | 57.5 / 53.2 s | Opus · dt256/aggregates/L2-Q-2seed.opus.json `Q`; think-Q-full-s42/s43.json |
| G (Gemma + 1024) | 0.514 (0.487–0.540) | 0.388 (0.354–0.421) | 0.299 (0.261–0.337) | UNKNOWN | 0/0/51 · 0/0/51 | 2 | 106.2 / 108.5 s | Opus · gemmathink/aggregates/L2-G-2seed.opus.json `G`; think-G-full-s42/s43.json |
| Z (4B think 512) | 0.439 (0.401–0.476) | 0.293 (0.244–0.340) | 0.192 (0.137–0.245) | UNKNOWN | 0/0/51 | 1 (42) | 23.6 s | Opus · think4b/aggregates/L2-Z-1seed.opus.json `Z`; think-Z-full-s42.json |
| **Haiku no-web** | **0.588 (0.559–0.615)** | **0.48** (CI UNKNOWN) | 0.406 (0.365–0.445), derived = (raw − 0.306)/0.694 | UNKNOWN | UNKNOWN | 1 | — | Opus · raw: CLAIM-RESULTS-cut6.md l.83 (= cut3 l.65); floor-adj: BOUNTY-BOARD.md l.16, CLAIM-DRAFT l.11. Underlying rows are in `runs-cut3/anchors` under blind/ (not opened); a floor_metrics run there would give the CI |
| R2→H hybrid | 0.465 / 0.467 (plain; vs K +0.052 / +0.054) | ≈ 0.33 (prose estimate, no CI) | — | — | — | 2 (per seed) | 13.2 / 13.4 s | Opus rows recombined · deeproute/DEEPROUTE-VPARA.md table rows 1–2 (19/51 routed) |
| R8→H hybrid | 0.486 / 0.499 (plain) | UNKNOWN | — | — | — | 2 | 72.0 / 71.6 s | deeproute/DEEPROUTE-VPARA.md rows 3–4 (29/51 routed) |
| R2→D hybrid | 0.440 / 0.429 (plain) | UNKNOWN | — | — | — | 2 | 13.2 / 13.4 s | deeproute/DEEPROUTE-VPARA.md rows 5–6 |

### 1b. v0.2 (110 ids; ex-held-out, burnt → dev)

| Row | raw (95 % CI) | floor-adj (CI) | above-decline (CI) | useful ≥ 3/5 | W/T/L vs ref (per seed) | seeds | p50 desktop | judge · source |
|---|---|---|---|---|---|---|---|---|
| **K two-seed** | 0.512 (0.478–0.549) | 0.388 (0.346–0.434) | 0.297 (0.248–0.350) | UNKNOWN | 0/0/110 · 0/1/109 | 2 | 6.3 / 6.1 s (same-backend C, DEEPVPARA.md l.19); claim-run p50 UNKNOWN (CLAIM-RESULTS-cut6 gives none for v0.2) | Opus · deepvpara/aggregates/dv-v02-2seed.floorK.json; W/T/L deepthinkv02/aggregates/L2-TV-2seed.opus.json `paired` vs K |
| K s42 only | 0.519 (0.483–0.555) | 0.397 (0.351–0.442) | 0.307 (0.254–0.359) | 41 % ("items ≥ 3/5", PIPELINE-AUDIT l.13) | 0/0/110 | 1 | as above | Opus · deepthinkv02/aggregates/L2-TV-1seed.opus.json `K`. The handoff's "0.519 / 0.40" is this s42 row |
| D | 0.568 (0.536–0.602) | 0.457 (0.417–0.500) | 0.377 (0.331–0.426) | UNKNOWN | 0/0/110 · 0/0/110 | 2 | 34.4 / 33.6 s | Opus · deepvpara/aggregates/dv-v02-2seed.floorD.json; p50 DEEPVPARA.md l.18 |
| TV (1024) | 0.612 (0.581–0.644) | 0.514 (0.475–0.554) | 0.442 (0.397–0.487) | UNKNOWN | 0/1/109 · 0/2/108 | 2 | 132.6 / 136.8 s | Opus · deepthinkv02/aggregates/L2-TV-2seed.opus.json `TV`; think-TV-s42/s43.json |
| **H (512)** | **0.608 (0.575–0.641)** | **0.508 (0.467–0.550)** | 0.435 (0.388–0.483) | UNKNOWN | 0/1/109 | 1 (42) | 82.4 s | Opus · dt512v02/aggregates/L2-H-1seed.opus.json `H`; think-H-full-s42.json |
| Q, G, Z | — | — | — | — | — | — | — | never measured on v0.2 |
| ZV (4B think 512) | 0.485 (0.453–0.517) plain | 0.350 (0.310–0.387) plain | UNKNOWN | UNKNOWN | 0/1/109 | 1 | 17.6 s | **Haiku 5.5-low** (not comparable to Opus rows; Opus never run) · think4b/aggregates/L1-ZVvsC-ZV-full-s42.haiku55-low.json `ZV`; think-ZV-ZV-full-s42.json |
| Haiku no-web | — | — | — | — | — | — | — | no v0.2 anchor (v0.1 only: 0.653 raw, QUEUE l.265) |
| R2→H hybrid | 0.561 (plain; vs K +0.042) | ≈ 0.45 (prose estimate) | — | — | — | 1 | 11.7 s | deeproute/DEEPROUTE-VPARA.md Addendum row 1 (33/110 routed) |
| R2→TV hybrid | 0.568 (plain) | UNKNOWN | — | — | — | 1 | 11.7 s | idem row 2 |
| R2→D hybrid | 0.550 (plain) | UNKNOWN | — | — | — | 1 | 11.7 s | idem row 3 |
| R8→H hybrid | 0.571 (plain) | UNKNOWN | — | — | — | 1 | 73.3 s | idem row 4 |

### 1c. One-line readings (formal raw · primary floor-adj · secondary Haiku parity ≥ 0.48)

| Row | V-para | v0.2 | Formal rule (both sets) |
|---|---|---|---|
| K | raw SHORT by 0.087 · floor-adj SHORT by 0.239 · parity SHORT by 0.219 | raw STRADDLES · floor-adj SHORT by 0.112 | not met |
| D | raw SHORT by 0.033 · floor-adj SHORT by 0.171 · parity SHORT by 0.151 | raw MET (0.536) · floor-adj STRADDLES (CI high 0.500) | not met (V-para) |
| T / TV | raw MET (0.513) · floor-adj SHORT by 0.078 · parity SHORT by 0.058 | raw MET (0.581) · floor-adj STRADDLES | **met, 2 seeds on both sets** |
| **H** | raw MET (0.524) · floor-adj SHORT by 0.064 · parity SHORT by 0.044 | raw MET (0.575, 1 seed) · floor-adj STRADDLES (1 seed) | **met** (v0.2 leg on 1 seed) |
| Q | raw STRADDLES · floor-adj SHORT by 0.113 · parity SHORT by 0.093 | — | not met |
| G | raw STRADDLES · floor-adj SHORT by 0.112 · parity SHORT by 0.092 | — | not met |
| Z / ZV | raw SHORT by 0.061 · [floor-adj SHORT by 0.207, 1 seed] · parity SHORT by 0.187 | Haiku judge only: n/a | not met |
| Haiku no-web | raw MET (0.559) · floor-adj SHORT by 0.020 at the point (CI UNKNOWN → MET/STRADDLES undecidable) · parity = itself | — | n/a (no v0.2 run) |
| Hybrids | descriptive: raw points 0.43–0.50, no stratified CI | raw points 0.55–0.57 | n/a |

Bottom line: the formal raw rule is already met by T and H; on the primary reading nothing reaches 0.50 on V-para (best H 0.436, CI high 0.472, short by 0.064); on the secondary reading nothing reaches Haiku no-web (H CI high 0.472 < 0.48). Win-rate is 0 for every row on every seed.

## 2. LENGTHSHARE part 1 — which rubric dimension carries the gap (0 calls; arms/lengthshare/tools/dimshare.mjs, aggregates/dimshare-*.opus.json; Opus judge.v1 rows, pooled over the seeds listed in §1)

Per-dimension ratios (raw = Σboar/Σref on that dimension; floor-adj = Σ(boar−1)/Σ(ref−1); CI = item bootstrap 2,000, plain). "all" reproduces §1 (K V-para 0.413 / 0.261, H 0.552 / 0.436, H v0.2 0.608 / 0.508).

| Row | all raw / floor-adj | correctness raw / floor-adj (CI) | completeness raw / floor-adj | usefulness raw / floor-adj | mean boar / ref per dim (corr · comp · usef) |
|---|---|---|---|---|---|
| K V-para (2 seeds) | 0.413 / 0.261 | 0.544 / **0.427** (0.371–0.482) | 0.349 / 0.172 | 0.346 / 0.183 | 2.66/4.88 · 1.63/4.68 · 1.73/5.00 |
| H V-para (2 seeds) | 0.552 / 0.436 | 0.730 / **0.660** (0.608–0.712) | 0.452 / 0.301 | 0.472 / 0.341 | 3.56/4.88 · 2.09/4.63 · 2.36/5.00 |
| K v0.2 (2 seeds) | 0.512 / 0.388 | 0.678 / **0.595** (0.544–0.646) | 0.423 / 0.274 | 0.437 / 0.296 | 3.33/4.91 · 2.06/4.88 · 2.18/4.99 |
| H v0.2 (s42) | 0.608 / 0.508 | 0.795 / **0.743** (0.681–0.805) | 0.503 / 0.375 | 0.527 / 0.408 | 3.89/4.89 · 2.45/4.88 · 2.63/4.99 |

Shares of items (order-averaged scores; tools/useful3.mjs, aggregates/useful3.opus.jsonl): usefulness ≥ 3 — K V-para 2.9 %, D 10.8 %, H 33.3 %; K v0.2 34.5 %, H 58.2 %, TV 56.4 %. Correctness ≥ 4 — K V-para 27.5 %, H 56.9 %; K v0.2 54.5 %, H 72.7 %. (Fills the "useful ≥ 3/5" column of §1 for K, D, H, TV.)

Reading: on correctness alone the recommended deep configuration is **above the bar on both sets** (V-para floor-adj 0.660, v0.2 0.743) and the 4B is not (0.427 / 0.595). The whole shortfall sits in completeness (H V-para 0.30) and usefulness (0.34): the judge scores BOAR's answers as right but thin against ≈ 280-word references (p10/p50/p90 = 251/280/318 words). Gap bookkeeping on V-para for H: floor-adj gap to the reference 1 − 0.436 = 0.564 on the 3-dim mean vs 1 − 0.660 = 0.340 on correctness only → the difference (0.22) is ≥ 0.05, so HANDOFF-10-11 §4 step 2's second part (80-word-capped references, re-judge) runs; its result goes in a dated addendum below. Caveat: "correct but thin" is also what an always-decline system looks like on completeness/usefulness, so correctness-only is not a bar reading; it locates the gap, it does not close it.

### Addendum 2026-10-10 (LENGTHSHARE part 2, 255 Opus; arms/lengthshare/LENGTHSHARE.md)
Same answers, references condensed to ≤ 80 words (V-para, s42, 51 ids): H floor-adj 0.412 → **0.514 (0.456–0.578)**, paired +0.102 (+0.068…+0.144); K 0.261 → 0.322 (+0.060); H80 − K80 +0.192. Correctness unchanged; the shift is completeness/usefulness, half of it the capped references scoring lower themselves. Length share of H's gap to the reference ≈ 17 %; ≈ 83 % is substance. Not a bar reading (dev, 1 seed, CI straddles, references altered); the §0 target is unchanged and still unmet.

## 3. Pipeline metric: V-para floor-adj points (2 seeds) per 1,000 judge calls

Formula: points = 100 × two-level paired Δ floor-adj (`paired_gap.py` `above_min.gap_a_minus_b`, V-para, 2 seeds, vs the arm's control); calls = all judge calls the arm logged in QUEUE (Haiku + Opus); metric = points / calls × 1,000.

| Arm (adopted) | Δ floor-adj (CI), source | Calls (QUEUE) | pts / 1k calls (all) | pts / 1k Opus |
|---|---|---|---|---|
| DEEPTHINK (T vs D) | +0.093 (+0.050…+0.137), deepthink/aggregates/L2-TvsD-2seed.paired_gap.json | 102 Haiku + 204 Opus = 306 (QUEUE l.821) | 30.5 | 45.7 |
| DT512 (H vs T) | +0.014 (−0.012…+0.039), dt512/aggregates/paired_gap-HvsT-2seed.json | 142 Haiku + 204 Opus = 346 (QUEUE l.842) | 4.0 | 6.8 |
| **Adopted arms together** (H vs D) | +0.107 (+0.064…+0.152), dt512/aggregates/paired_gap-HvsD-2seed.json | 652 (244 Haiku + 408 Opus) | **16.4** | 26.2 |
| Beside: K → H chain incl. DEEPVPARA (D vs K +0.068, dv-vpara-2seed.paired_gap.json; 1,390 Haiku + 644 Opus, QUEUE l.816) | +0.175 (0.4359 − 0.2611) | 2,686 (1,052 Opus) | 6.5 | 16.6 |

| Pack line, cycle 10-12 20:4x → 10-13 14:0x (ST2 L2, SELFTEST-SCORES, PACKROUTE, GROUND-ST, SEEDGEN) | 0 V-para points (product line: pack-matched Δ +0.032 packs measured; ST2 +0.017 not adopted) | 1,840 (720 Opus + ≈ 1,120 Haiku); 4 step-0 closures at 0 calls | 0 | 0 |

UNKNOWN: the pipeline-wide rate (all arms, adopted or not, since the claim build): needs the call counts of every arm since 10-06 summed from QUEUE (non-adopted deep arms alone: GEMMATHINK 142 H + 204 O l.831, DT256 142 H + 204 O l.846, THINK4B 182 H + 182 O l.863, THINK4B-V02 300 H l.880–881, DEEPTHINK-V02 266 H + 440 O l.828/839, DT512-V02 220 O l.848, SEEDVAR 102 O l.876, plus DEEPTHINK-2, DEEPFULL, DEEPNORAG, DEEPSAMP, DEEPCTX, DEEPWIKI rows not tallied here).

## 4. Sources

- Plan and code: boar-eval/bench/v0.2/plan/analysis-plan.md §3–§4 (raw = primary; above_min, above_decl with D = 0.306); boar-eval/bench/v0.2/plan/floor_metrics.py (keys `raw`, `above_min`, `above_decl`; stratified two-level bootstrap); rnd/research/coordinator/arms/deepvpara/tools/paired.mjs (keys `ratio`, `floorAdj` = Σ(S−1)/Σ(R−1), `winsVsRef`/`tiesVsRef`/`lossesVsRef`, `headToHead`); no addendum-05 in that directory.
- Aggregates (all under rnd/research/coordinator/arms/): deepvpara/aggregates/{dv-vpara-2seed.L2.json, dv-vpara-s42.L2.json, dv-vpara-2seed.paired_gap.json, dv-v02-2seed.floorK.json, dv-v02-2seed.floorD.json}; deepthink/aggregates/{L2-TvsD-2seed.opus.json, L2-TvsD-2seed.paired_gap.json, think-T-s42.json, think-T-s43.json, think-D-s42.json}; deepthinkv02/aggregates/{L2-TV-1seed.opus.json, L2-TV-2seed.opus.json, think-TV-s42.json, think-TV-s43.json}; dt512/aggregates/{L2-H-2seed.opus.json, paired_gap-HvsT-2seed.json, paired_gap-HvsD-2seed.json, think-H-full-s42.json, think-H-full-s43.json}; dt512v02/aggregates/{L2-H-1seed.opus.json, think-H-full-s42.json}; seedvar/aggregates/{seedvar-H-3seed.opus.json, think-H-s44.json}; dt256/aggregates/{L2-Q-2seed.opus.json, think-Q-full-s42.json, think-Q-full-s43.json}; gemmathink/aggregates/{L2-G-2seed.opus.json, think-G-full-s42.json, think-G-full-s43.json}; think4b/aggregates/{L2-Z-1seed.opus.json, think-Z-full-s42.json, L1-ZVvsC-ZV-full-s42.haiku55-low.json, think-ZV-ZV-full-s42.json}.
- Result docs: arms/deepvpara/DEEPVPARA.md l.15–19 (p50 table); arms/dt512/DT512.md l.2; arms/deeproute/DEEPROUTE-VPARA.md (both tables); coordinator/CLAIM-RESULTS-cut6.md (P1/P3/P6 table, Haiku 0.588 (0.559–0.615), K timing 10.1 s); coordinator/CLAIM-DRAFT.md §1 l.11; rnd/research/BOUNTY-BOARD.md l.15–16 (Haiku floor-adj 0.48; K "items ≥ 3/5"); coordinator/PIPELINE-AUDIT-2026-10-06.md l.13–14, l.53 (D1); coordinator/HANDOFF-2026-10-11.md §1, §4; rnd/research/QUEUE.md l.265, 642, 816, 821, 828, 831, 839, 842, 846, 848, 863, 872–873, 876, 880–881.
- Anomalies seen while compiling (not fixed): dt512/aggregates/L2-H-3seed.opus.json is empty and paired_gap-Hvs{D,T}-3seed.json are 1 byte; in dt256/aggregates/L2-Q-2seed.opus.json the seed-43 head-to-head of Q vs T and Q vs H is identical (10/15/26) although H s43 ≠ T s43 (H vs T s43 h2h 15/26/10 in dt512/aggregates/L2-H-2seed.opus.json): possible control mix-up in that file's s43 pairing (two-level paired_gap files are separate and unaffected).

### Addendum 2026-10-11 (JUDGEVAR + common-mode CIs; arms/judgevar/, aggregates/bar-cm.json)
Opus test-retest on unchanged traces: Δ +0.004 raw, per-item r 0.96 → σ_judge ≈ 0.003, negligible. Run-level seed noise (SEEDVAR σ_run) is the missing term; CI_cm = point ± 1.96·sqrt(SE_item² + (σ_run/√seeds)²), σ_run raw 0.020 / floor-adj 0.025 on V-para, ≈ 0.010 on v0.2, 0 for the 4B (seeds identical):
| Row | raw CI → CI_cm | floor-adj CI → CI_cm | reading change |
|---|---|---|---|
| H V-para 2 seeds | 0.524–0.581 → **0.513–0.592** | 0.401–0.472 → **0.387–0.486** | formal raw rule still MET (low 0.513); primary still SHORT |
| T V-para 2 seeds | 0.513–0.571 → 0.502–0.582 | 0.385–0.459 → 0.371–0.473 | formal rule MET by 0.002 |
| H v0.2 1 seed | 0.575–0.641 → 0.569–0.647 | 0.467–0.550 → 0.463–0.553 | unchanged |
| TV v0.2 2 seeds | 0.581–0.644 → 0.578–0.647 | 0.475–0.554 → 0.472–0.556 | unchanged |
| H s42 only (1 seed) | 0.500–0.563 → 0.483–0.583 | 0.375–0.450 → 0.350–0.474 | a one-seed V-para deep row no longer clears the raw rule: use two seeds |
Claim wording should cite the CI_cm columns for deep-tier rows (weekly batch, independent reviewer).

### Addendum 2026-10-12 (loop cycle 10-11 → 10-12: arms, ladder, pipeline metric, direction check)
Arms with frozen criteria this cycle: VITALPACK-DEEP (FAIL step 0), VITALADD (NO slice; full 110 not detected at 0.025), DEEPCOVER (NO slice, correctness −0.11), QUANTCEIL (NO: V-para 2 seeds +0.004, −0.024…+0.033; v0.2 +0.008; mechanism confirmed on the *wrong* bucket of v0.2, +0.087), SYNTHDEEP (FAIL step 0), DEEPHEDGE (closed step 0: health-strict fallback), WIKISECTION H5/H5b (FAIL: the facts are not in Wikipedia). Measurements: LOSSMAP (+ per-path), V02GOLD, LIT-QUANTCEIL.
| Row (V-para, 2 seeds, Opus) | raw (CI) | floor-adj (CI) | win |
|---|---|---|---|
| K cut 6 | 0.413 (0.384–0.445) | 0.261 (0.224–0.300) | 0 |
| H deep + thinking 512 | 0.553 (0.524–0.581) | 0.436 (0.401–0.472) | 0 |
| Q = H with UD-IQ3_XXS | 0.557 (0.526–0.585) | 0.441 (0.403–0.477) | 0 |
| bar | 0.50 | 0.50 | — |
Pipeline metric (§3): **0 V-para floor-adj points adopted per 1,804 judge calls** this cycle (Opus 544 + Haiku 340 in week 10-12; 0 + 0 in the 10-11 part); cumulative since 10-06 unchanged in adopted points. Cost of the cycle's knowledge: [usage detail removed] of jev gateway, ≈ 18 h mini.
Direction check (LOOP-PROGRAM §5.6), evidenced at the fact level: for the deep tier's absent-knowledge items the rubric's missing facts are in neither the kept article (2/13, 4/30), nor anywhere in the enwiki top-100k pack on V-para (1/13), nor in the model (thinking did not emit them); the deep tier's and the 3-bit quant's gains both sit in the *wrong* bucket; V-para's remaining loss is 59 % absent knowledge + 40 % wrong facts. **Honest state: formal raw rule met by H (CI_cm low 0.513); floor-adjusted V-para target 0.50 not reachable with any lever measurable on ≤ 12 GB (model, quant, thinking, prompt, retrieval, packs, notes, sections).** Remaining inputs are external: v0.3 items (unexposed number), a non-Wikipedia offline corpus that holds question-shaped facts, a 12 GB device for the deep-tier plan.

### Correction 2026-10-12 (after DEEP-RESEARCH-2026-10-12 §1, premises 1–3)
The addendum above overstates WIKISECTION: H5/H5b opened only `boar-wiki-en-top100k.sqlite` (98,389 articles, FineWiki Aug-2025; 19.5 % of its chunks — tables — are not in FTS) and gated only the absent-knowledge items that had a kept source (14 of 34 on V-para, 44 of 78 on v0.2). The 20 V-para no-kept absent items (0.333 of H's loss) were never tested, nor the 15 full shards (6.1 M articles) or a fresh snapshot; the 1/13 figure is threshold-sensitive (p ≥ 0.6 → 4/13). Withdrawn: "the facts are not in Wikipedia". Standing: "not in the top-100k pack's indexed text for the gated subset". Decision D-1 (peer research): no non-Wikipedia corpus build and no such claim until the WIKIFULL gate runs over all 34 V-para absent items (T2). The honest state sentence stands with that scope.
