# CV5-RECOMPUTE (2026-10-21): 263 of 270 checkable page numbers re-derive from their sources; 7 mismatch (2.6 %), 25 of 295 have no machine-readable source (8.5 %)

TL;DR (0 LLM, 0 judge, 0 paid; criterion ruler/CV5-criterion.md sha 78f43da6, frozen before the final runs; script tools/recompute_page_numbers.py sha c778a6cbeef5; output CV5-NUMBERS-2026-10-21.json sha 9f407d94fea3):
- Scope: every measured number quoted in RESEARCH-PAGE-OUTLINE-2026-10-21 §0-§2 (incl. the 05:xx update blocks) and PLAN-2026-10-21-TO-25 §1 (table + 05:xx update): **295 numbers** (CIs and ranges counted per bound; duplicates counted per occurrence). Excluded: bounty constants, dates, shas, QUEUE line numbers, rule thresholds.
- **Verdict under the frozen rule: PASS on the rate (2.6 % < 5 % mismatch; 8.5 % < 10 % unsourced), KILL for one headline sentence**: the outline §2 row "4B single pack vs claim kit ... above_min +0.042 (+0.024…+0.062) Opus L2" quotes the **Opus raw** delta under an above_min label. Opus above_min is **+0.053 (+0.030…+0.078)** (arms/packs-l2/aggregates/s_off.json; CI bound off by 0.016 > 0.01). Fix: write "raw +0.042 (+0.024…+0.062), above_min +0.053 (+0.030…+0.078), Opus, 180 self-tests, 1 seed". Haiku above_min happens to be +0.042 (+0.021…+0.065), which is probably how the label slipped.
- Other mismatches (not headline): X6 "72/72" (the boar-eval copy of final-cut7-v01 has 73 rows, 73 success; CLAUDE.md says 72/73) and X6 "p90 48.4 s" (fast-tier rows give p50 30.7 exactly but nearest-rank p90 42.6 s; DEVICE-X6.md's p90 definition is not recoverable); MATRIX "652 Haiku calls" vs 646 rows in the judgments files (MATRIX.md l.43 itemises 652; 6 rows not on disk); A-union retrieval "3.9–4.0 s" holds for the 1.7B runs only (3.90 / 3.99 s); the Gemma and 4B A-union runs are 4.41 / 4.25 s, so "3.9–4.0 s on all three tiers" would be wrong.
- Definition notes (MATCH, but the writer must keep the definition): 4B Pixel "answer p50 25.5 s" is the median of **wallMs** (totalLatencyMs gives 25.4 s); Gemma p90 24.3 s is **nearest-rank**; REFVAR "0.015" is |−0.0154| (draw A − B is negative); ORACLE "= 10 % of the self-test gain" is 0.015 / 0.139 = 0.108 (say "about a tenth"; against the LITEPACKS +0.069 it would be 22 %); the decline floor 0.206 recomputes as 3·51/744 from the LOSSMAP K items.
- PLAN §1 gap table recomputes exactly from arms/lossmap/aggregates/lossmap-K-vpara-s42.json (gap 0.586 = 1 − mean ratio; shares = gap × loss-point share; wrong split by the jev source_on_topic label 12/11; no kept source 29/51 carrying 58 %); ladder 0.261 / 0.329 / 0.436 from deepvpara and dt512 Opus aggregates.
- Recompute depth: aggregate JSON values are read as stored (no re-bootstrap); phone timings, call counts, the gap decomposition and the floor are recomputed from raw rows. Re-running the bootstraps from raw judgment rows (the hypothesis' full method) is not done here.

## Numbers with no machine-readable source (re-derive or drop before publication)
Headline ones first: **A-union "+2.4 s retrieval"** (the 1.5–1.6 s baseline side has no JSON field; bench rows carry firstSourcesMs, a different stamp, p50 1.70 s) and **"deep + think Codex 0.577" / "Codex +0.10 on each rung"** (XFAM sources live under blind/, not opened here; the coordinator must re-derive them with the numbers-only report script).

| id | number | doc value | cited source | note |
|---|---|---|---|---|
| O0-15 | same-family judge lift 3.4-8.4 pp | 3.4 | arXiv 2609.17857 (web/WEB-LOG-2026-10-21.md) | external paper |
| O1-05 | TTFT 9.1 s before BATCHRET (litelat-9) | 9.1 | QUEUE l.1428 (litelat-9 not in arms/litelat/compare.json) | compare.json holds litelat-00..07 only (base ttft 9.18 s) |
| O1-06 | TTFT 5.5 s after BATCHRET | 5.5 | QUEUE l.1428 |  |
| O1-14 | 4B low-memory kill at 4.4 GB RSS | 4.4 | QUEUE l.1415 / GEMMA4-PHONE.md (logcat) | prose only |
| O1-18 | X6 PSS <= 4.23 GB after load | 4.23 | arms/device-x6/DEVICE-X6.md (meminfo prose) | no JSON field |
| O1-28 | 8,374 world tiles hosted | 8374 | ruler/TILE-PATH-2026-10-21.md | prose only (tilepath.py writes no JSON) |
| O2-35 | PACKREAD 4B D4 0.650 | 0.65 | QUEUE l.1387-1390 (arms/packread has judgments, no aggregate) | judgment rows exist; definition of the scale not in a JSON |
| O2-36 | PACKREAD 1.7B D4 0.529 | 0.529 | QUEUE l.1387-1390 |  |
| O2-37 | PACKREAD LFM2.5 0.554 | 0.554 | QUEUE l.1387-1390 |  |
| O2-51 | venues P5 0/7 -> 7/7 | 7 | arms/venuegps/VENUEGPS-2.md (blind-side venue scorer output) | prose only; scorer outputs under blind/ |
| O2-52 | area tile +3.65 MB | 3.65 | arms/venuegps/VENUEGPS-2.md | tiles.json has fetch metadata, not the kit delta |
| O2-68 | A-union +2.4 s retrieval p50 (1.7B) | 2.4 | arms/aunion-pixel (A-union side only) | A-union side 3.99 s in aunion-summary.json; the 1.5-1.6 s baseline has no JSON field (rows firstSourcesMs p50 = 1.70 s, a different stamp) |
| O2-70 | V-para kit holds the fact 6/51 | 6 | VPARA-DIAGNOSIS §1 / PACKCOND-P1 (no count field in packcond-K-vpara.json) |  |
| O2-71 | V-para all packs 10/51 | 10 | VPARA-DIAGNOSIS §1 / PACKCOND-P2 |  |
| O2u-51 | A-union retrieval +2.4 s p50 (dup of O2-68) | 2.4 | arms/aunion-pixel | baseline side has no JSON field |
| O2u-52 | baseline retrieval p50 1.5-1.6 s | 1.5 | arms/aunion-pixel/AUNION-PIXEL.md | prose only |
| O2u-64 | ~0.15 s per small pack | 0.15 | arms/aunion-pixel/AUNION-PIXEL.md | prose only (sql_ms_by_db is a sum, not per query) |
| O2u-65 | PK-5 kept-source identity 81/97 | 81 | arms/aunion-pixel/AUNION-PIXEL.md (replay) | no JSON field |
| P1-11 | kit 6/51 (dup O2-70) | 6 | VPARA-DIAGNOSIS / PACKCOND-P1 |  |
| P1-12 | all packs 10/51 (dup O2-71) | 10 | VPARA-DIAGNOSIS / PACKCOND-P2 |  |
| P1-20 | 1.7B = 4B - 0.07..0.11 | 0.07 | CRITIQUE-2026-10-16 (md) | prose only |
| P1-21 | Codex +0.10 on each rung | 0.1 | blind/V-para/runs-xfam (XFAM-REPORT.md; off-limits here) | blind-only source: coordinator must re-derive |
| P1-22 | deep + think Codex 0.577 | 0.577 | blind/V-para/runs-xfam | blind-only source |
| P1-23 | win-rate ~0 everywhere | 0 | CLAIM-RESULTS-cut6 / XFAM (md, blind) | prose only |
| P1-24 | +0.03 reading (DEEPREAD) | 0.03 | arms/deepread (md) | prose only |

Fixes in one line each: litelat-9 TTFT 9.1 → 5.5 s (add the litelat-9 run to arms/litelat/compare.json or quote compare.json's base 9.2 s); PACKREAD 0.650 / 0.529 / 0.554 (write an aggregate from arms/packread/judgments); 6/51 and 10/51 (add counts to packcond-K/p2-vpara.json); VENUEGPS 0/7 → 7/7 and +3.65 MB, 8,374 tiles, 81/97 PK-5 identity, 0.15 s per pack, X6 PSS 4.23 GB, LMK at 4.4 GB (prose only: cite the md or add a JSON field); 3.4–8.4 pp is an external paper (keep as a citation, not a measurement).

## Full table (295 rows; H = headline tag used for the kill rule)
| id | doc | sec | H | number | doc | recomputed | status | judge | n | seeds | source | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O0-01 | OUTLINE | §0 |  | V-para 1/1/1 floor = 0.206 raw | 0.206 | 0.2056 | MATCH | Opus (judge.v1 rows) | 51 | s42 | arms/lossmap/aggregates/lossmap-K-vpara-s42.json (items ref scores) | recomputed 3*51/sum(ref) |
| O0-02 | OUTLINE | §0u | H | decline floor D | 0.058 | 0.058 | MATCH | Haiku 5.5-low | 30 | 1 | arms/floor-anchors/aggregates/floor-decline.json |  |
| O0-03 | OUTLINE | §0u | H | D CI low | 0.037 | 0.037 | MATCH | Haiku 5.5-low | 30 | 1 | arms/floor-anchors/aggregates/floor-decline.json |  |
| O0-04 | OUTLINE | §0u | H | D CI high | 0.081 | 0.081 | MATCH | Haiku 5.5-low | 30 | 1 | arms/floor-anchors/aggregates/floor-decline.json |  |
| O0-05 | OUTLINE | §0u |  | D calls (180 Haiku) | 180 | 180 | MATCH | Haiku 5.5-low | 30 | 1 | arms/floor-anchors/judgments/fa-decline-*.judgments.jsonl | row count |
| O0-06 | OUTLINE | §0u |  | v1.1 decline U 0.000 | 0 | 0 | MATCH | Haiku 5.5-low | 30 | 1 | arms/floor-anchors/v1_1/aggregates/W1.json |  |
| O0-07 | OUTLINE | §0u |  | v1.1 CE flips 7/40 | 7 | 7 | MATCH | Haiku 5.5-low | 40 | 1 | arms/floor-anchors/v1_1/aggregates/W1.json |  |
| O0-08 | OUTLINE | §0u |  | v1.1 CE flips denominator 40 | 40 | 40 | MATCH | Haiku 5.5-low | 40 | 1 | arms/floor-anchors/v1_1/aggregates/W1.json |  |
| O0-09 | OUTLINE | §0u |  | v1.1 retest SD 0.0265 | 0.0265 | 0.0265 | MATCH | Haiku 5.5-low | 20 | 2 repeats | arms/floor-anchors/v1_1/aggregates/W1.json |  |
| O0-10 | OUTLINE | §0u |  | v1 retest SD 0.0206 | 0.0206 | 0.0206 | MATCH | Haiku 5.5-low | 20 | 2 repeats | arms/floor-anchors/v1_1/aggregates/W1.json | stored as the bar "need" |
| O0-11 | OUTLINE | §0u |  | v1.1 calls 528 Haiku | 528 | 528 | MATCH | Haiku 5.5-low | - | - | arms/floor-anchors/v1_1/judgments/W1-*.judgments.jsonl | row count |
| O0-12 | OUTLINE | §0u |  | v1.1b CE flips 5/40 | 5 | 5 | MATCH | Haiku 5.5-low | 40 | 1 | arms/floor-anchors/v1_1/aggregates/W3.json |  |
| O0-13 | OUTLINE | §0u |  | v1.1b retest SD 0.0295 | 0.0295 | 0.0295 | MATCH | Haiku 5.5-low | 20 | 2 repeats | arms/floor-anchors/v1_1/aggregates/W3.json |  |
| O0-14 | OUTLINE | §0u |  | v1.1b calls 300 Haiku | 300 | 300 | MATCH | Haiku 5.5-low | - | - | arms/floor-anchors/v1_1/judgments/W3-*.judgments.jsonl | row count |
| O0-15 | OUTLINE | §0u |  | same-family judge lift 3.4-8.4 pp | 3.4 |  | UNSOURCED | - | - | - | arXiv 2609.17857 (web/WEB-LOG-2026-10-21.md) | external paper |
| O0-16 | OUTLINE | §0u |  | WARN-OPUS CE kappa 0.81 | 0.81 | 0.805 | MATCH | Opus vs Haiku | 111 | 1 | ruler/warn-opus/warn-opus-opus.json |  |
| O0-17 | OUTLINE | §0u |  | WARN-OPUS correct kappa 0.29 | 0.29 | 0.294 | MATCH | Opus vs Haiku | 111 | 1 | ruler/warn-opus/warn-opus-opus.json |  |
| O0-18 | OUTLINE | §0u |  | WARN-OPUS n 111 | 111 | 111 | MATCH | Opus vs Haiku | 111 | 1 | ruler/warn-opus/warn-opus-opus.json |  |
| O1-01 | OUTLINE | §1 |  | 1.7B TTFT p50 4.9 s (10 q) | 4.9 | 4.905 | MATCH | - | 10 | 1 | arms/gemma4-e2b/phone/q17b10-a/rows.jsonl | rows.jsonl median ttftMs |
| O1-02 | OUTLINE | §1 |  | 1.7B answer p50 8.3 s | 8.3 | 8.3181 | MATCH | - | 10 | 1 | arms/gemma4-e2b/phone/q17b10-a/rows.jsonl |  |
| O1-03 | OUTLINE | §1 |  | 1.7B 13.9 tok/s | 13.9 | 13.9206 | MATCH | - | 10 | 1 | arms/gemma4-e2b/phone/q17b10-a/rows.jsonl | median tokPerSec |
| O1-04 | OUTLINE | §1 |  | 1.7B PSS 3.25 GB | 3.25 | 3.25 | MATCH | - | 10 | 1 | ruler/SPEED-PRECHECK-2026-10-21.json |  |
| O1-05 | OUTLINE | §1 |  | TTFT 9.1 s before BATCHRET (litelat-9) | 9.1 |  | UNSOURCED | - | - | - | QUEUE l.1428 (litelat-9 not in arms/litelat/compare.json) | compare.json holds litelat-00..07 only (base ttft 9.18 s) |
| O1-06 | OUTLINE | §1 |  | TTFT 5.5 s after BATCHRET | 5.5 |  | UNSOURCED | - | - | - | QUEUE l.1428 |  |
| O1-07 | OUTLINE | §1 |  | Gemma answer p50 11.8 s | 11.8 | 11.7806 | MATCH | - | 73 | 1 | arms/gemma4-e2b/phone/gemma73-a/rows.jsonl |  |
| O1-08 | OUTLINE | §1 |  | Gemma answer p90 24.3 s | 24.3 | 24.2642 | MATCH | - | 73 | 1 | arms/gemma4-e2b/phone/gemma73-a/rows.jsonl | nearest-rank p90 |
| O1-09 | OUTLINE | §1 |  | Gemma 7.0 tok/s | 7 | 7.0133 | MATCH | - | 73 | 1 | arms/gemma4-e2b/phone/gemma73-a/rows.jsonl |  |
| O1-10 | OUTLINE | §1 |  | Gemma PSS peak 4.52 GB | 4.52 | 4.52 | MATCH | - | 73 | 1 | ruler/SPEED-PRECHECK-2026-10-21.json |  |
| O1-11 | OUTLINE | §1 |  | Gemma 73/73 | 73 | 73 | MATCH | - | 73 | 1 | arms/gemma4-e2b/phone/gemma73-a/rows.jsonl | success rows |
| O1-12 | OUTLINE | §1 |  | 4B 4.2 tok/s (Pixel, cut 7) | 4.2 | 4.1765 | MATCH | - | 73 | 1 | handoff/pixel8-2026-10-20/bench/results/final-cut7-v01/rows.jsonl |  |
| O1-13 | OUTLINE | §1 |  | 4B answer p50 25.5 s (Pixel) | 25.5 | 25.453 | MATCH | - | 73 | 1 | handoff/pixel8-2026-10-20/bench/results/final-cut7-v01/rows.jsonl | median wallMs over 73 rows (GEMMA4-PHONE definition); totalLatencyMs median = 25.42 -> 25.4 |
| O1-14 | OUTLINE | §1 |  | 4B low-memory kill at 4.4 GB RSS | 4.4 |  | UNSOURCED | - | - | - | QUEUE l.1415 / GEMMA4-PHONE.md (logcat) | prose only |
| O1-15 | OUTLINE | §1 |  | X6 4B 72/72 | 72 | 73 | MISMATCH | - | 73 | 1 | boar-eval/runs/device-poco-x6pro/final-cut7-v01/rows.jsonl | boar-eval copy has 73 rows, 73 success; DEVICE-X6.md says 72/72 (CLAUDE.md says 72/73): denominator unresolved |
| O1-16 | OUTLINE | §1 |  | X6 fast p50 30.7 s | 30.7 | 30.661 | MATCH | - | 51 | 1 | boar-eval/runs/device-poco-x6pro/final-cut7-v01/rows.jsonl | fast tier rows only (DEVICE-X6 definition) |
| O1-17 | OUTLINE | §1 |  | X6 fast p90 48.4 s | 48.4 | 42.5501 | MISMATCH | - | 51 | 1 | boar-eval/runs/device-poco-x6pro/final-cut7-v01/rows.jsonl | nearest-rank; DEVICE-X6.md definition unresolved |
| O1-18 | OUTLINE | §1 |  | X6 PSS <= 4.23 GB after load | 4.23 |  | UNSOURCED | - | - | - | arms/device-x6/DEVICE-X6.md (meminfo prose) | no JSON field |
| O1-Sa0 | OUTLINE | §1u |  | SPEED-PRECHECK aunion73-a T30 p50 | 4.4 | 4.4 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sa1 | OUTLINE | §1u |  | SPEED-PRECHECK aunion73-a T30 p90 | 11.7 | 11.7 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sa2 | OUTLINE | §1u |  | SPEED-PRECHECK aunion73-a complete p50 | 4.4 | 4.4 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sa3 | OUTLINE | §1u |  | SPEED-PRECHECK aunion73-a complete p90 | 13.7 | 13.7 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sa4 | OUTLINE | §1u |  | SPEED-PRECHECK aunion73-a decode tok/s | 11.3 | 11.3 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sa5 | OUTLINE | §1u |  | SPEED-PRECHECK aunion73-a PSS peak GB | 3.41 | 3.41 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sb0 | OUTLINE | §1u |  | SPEED-PRECHECK q17b73-a T30 p50 | 2.9 | 2.9 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sb1 | OUTLINE | §1u |  | SPEED-PRECHECK q17b73-a T30 p90 | 9.9 | 9.9 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sb2 | OUTLINE | §1u |  | SPEED-PRECHECK q17b73-a complete p50 | 2.9 | 2.9 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sb3 | OUTLINE | §1u |  | SPEED-PRECHECK q17b73-a complete p90 | 11.7 | 11.7 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sb4 | OUTLINE | §1u |  | SPEED-PRECHECK q17b73-a decode tok/s | 12.4 | 12.4 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sb5 | OUTLINE | §1u |  | SPEED-PRECHECK q17b73-a PSS peak GB | 3.39 | 3.39 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sc0 | OUTLINE | §1u |  | SPEED-PRECHECK gemma73-a T30 p50 | 9.4 | 9.4 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sc1 | OUTLINE | §1u |  | SPEED-PRECHECK gemma73-a T30 p90 | 18.1 | 18.1 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sc2 | OUTLINE | §1u |  | SPEED-PRECHECK gemma73-a complete p50 | 11.8 | 11.8 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sc3 | OUTLINE | §1u |  | SPEED-PRECHECK gemma73-a complete p90 | 23.9 | 23.9 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sc4 | OUTLINE | §1u |  | SPEED-PRECHECK gemma73-a decode tok/s | 7 | 7 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sc5 | OUTLINE | §1u |  | SPEED-PRECHECK gemma73-a PSS peak GB | 4.52 | 4.52 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sd0 | OUTLINE | §1u |  | SPEED-PRECHECK final-cut7-v01 T30 p50 | 20.2 | 20.2 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sd1 | OUTLINE | §1u |  | SPEED-PRECHECK final-cut7-v01 T30 p90 | 39.2 | 39.2 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sd2 | OUTLINE | §1u |  | SPEED-PRECHECK final-cut7-v01 complete p50 | 26 | 26 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sd3 | OUTLINE | §1u |  | SPEED-PRECHECK final-cut7-v01 complete p90 | 52 | 52 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sd4 | OUTLINE | §1u |  | SPEED-PRECHECK final-cut7-v01 decode tok/s | 4.2 | 4.2 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-Sd5 | OUTLINE | §1u |  | SPEED-PRECHECK final-cut7-v01 PSS peak GB | 4.92 | 4.92 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | answered set S1 |
| O1-19 | OUTLINE | §1u |  | 1.7B declines 35 % of v0.1 | 0.35 | 0.3472 | MATCH | - | 72 | 1 | ruler/SPEED-PRECHECK-2026-10-21.json | 25/72 claim kit; A-union run 26/72 |
| O1-20 | OUTLINE | §1u |  | Gemma declines 0 % | 0 | 0 | MATCH | - | 72 | 1 | ruler/SPEED-PRECHECK-2026-10-21.json |  |
| O1-21 | OUTLINE | §1u |  | 4B declines 0 % | 0 | 0 | MATCH | - | 72 | 1 | ruler/SPEED-PRECHECK-2026-10-21.json |  |
| O1-22 | OUTLINE | §1u |  | model-path-only 1.7B+A-union T30 p50 11.2 | 11.2 | 11.2 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json |  |
| O1-23 | OUTLINE | §1u |  | model-path-only T30 p90 13.0 | 13 | 13 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json |  |
| O1-24 | OUTLINE | §1u |  | model-path-only complete p50 12.1 | 12.1 | 12.1 | MATCH | - | - | 1 | ruler/SPEED-PRECHECK-2026-10-21.json |  |
| O1-25 | OUTLINE | §1u |  | 4B + A-union answer p50 19.4 s | 19.4 | 19.4329 | MATCH | - | 73 | 1 | arms/aunion-pixel/q4ba73-a/aunion-summary.json |  |
| O1-26 | OUTLINE | §1u |  | 4B + A-union PSS peak 4.76 GB | 4.76 | 4.7643 | MATCH | - | 73 | 1 | arms/aunion-pixel/q4ba73-a/aunion-summary.json |  |
| O1-27 | OUTLINE | §1u |  | 4B + A-union 0 LMK | 0 | 0 | MATCH | - | 73 | 1 | arms/aunion-pixel/q4ba73-a/aunion-summary.json |  |
| O1-28 | OUTLINE | §1u |  | 8,374 world tiles hosted | 8374 |  | UNSOURCED | - | - | - | ruler/TILE-PATH-2026-10-21.md | prose only (tilepath.py writes no JSON) |
| O1-29 | OUTLINE | §1u |  | RV4 7 has_location items | 7 | 7 | MATCH | - | 7 | - | ruler/RV4-CITY-BOUND-2026-10-21.json | ids only (v0.4 metadata) |
| O1-30 | OUTLINE | §1u |  | RV4 headline weight 65.5 | 65.5 | 65.5 | MATCH | - | 71 | - | ruler/RV4-CITY-BOUND-2026-10-21.json |  |
| O1-31 | OUTLINE | §1u | H | RV4 share 10.7 % | 0.107 | 0.1069 | MATCH | - | 71 | - | ruler/RV4-CITY-BOUND-2026-10-21.json |  |
| O1-32 | OUTLINE | §1u |  | RV4 swing >= 0.107 | 0.107 | 0.1069 | MATCH | - | 71 | - | ruler/RV4-CITY-BOUND-2026-10-21.json |  |
| O1-33 | OUTLINE | §1u |  | RV4 tile ceiling 0.098 | 0.098 | 0.0982 | MATCH | Haiku 5.5-low | - | - | ruler/RV4-CITY-BOUND-2026-10-21.json | dev proxy |
| O1-34 | OUTLINE | §1u |  | RV4 tile ceiling CI low 0.089 | 0.089 | 0.0886 | MATCH | Haiku 5.5-low | - | - | ruler/RV4-CITY-BOUND-2026-10-21.json |  |
| O1-35 | OUTLINE | §1u |  | RV4 tile ceiling CI high 0.106 | 0.106 | 0.1062 | MATCH | Haiku 5.5-low | - | - | ruler/RV4-CITY-BOUND-2026-10-21.json |  |
| O1-36 | OUTLINE | §1u |  | decline bare 0.058 | 0.058 | 0.058 | MATCH | Haiku 5.5-low | 30 | 1 | arms/floor-anchors/aggregates/floor-decline.json |  |
| O1-37 | OUTLINE | §1u |  | decline hedged 0.053 | 0.053 | 0.0531 | MATCH | Haiku 5.5-low | 30 | 1 | arms/floor-anchors/aggregates/floor-decline.json |  |
| O1-38 | OUTLINE | §1u |  | decline fluent no-content 0.016 | 0.016 | 0.0163 | MATCH | Haiku 5.5-low | 30 | 1 | arms/floor-anchors/aggregates/floor-decline.json |  |
| O1-39 | OUTLINE | §1u |  | 1.5B anchor judge.v1 +0.035 | 0.035 | 0.0347 | MATCH | Haiku 5.5-low | 57 | 1 | arms/floor-anchors/aggregates/floor.json |  |
| O1-40 | OUTLINE | §1u |  | 1.5B anchor judge.v1 CI low | -0.019 | -0.019 | MATCH | Haiku 5.5-low | 57 | 1 | arms/floor-anchors/aggregates/floor.json |  |
| O1-41 | OUTLINE | §1u |  | 1.5B anchor judge.v1 CI high | 0.089 | 0.089 | MATCH | Haiku 5.5-low | 57 | 1 | arms/floor-anchors/aggregates/floor.json |  |
| O1-42 | OUTLINE | §1u |  | 1.5B anchor v1.1 +0.047 | 0.047 | 0.0469 | MATCH | Haiku 5.5-low | 57 | 1 | arms/floor-anchors/v1_1/aggregates/W1-sep.json |  |
| O1-43 | OUTLINE | §1u |  | 1.5B anchor v1.1 CI low | -0.0005 | -0.0005 | MATCH | Haiku 5.5-low | 57 | 1 | arms/floor-anchors/v1_1/aggregates/W1-sep.json |  |
| O1-44 | OUTLINE | §1u |  | 1.5B anchor v1.1 CI high | 0.097 | 0.0972 | MATCH | Haiku 5.5-low | 57 | 1 | arms/floor-anchors/v1_1/aggregates/W1-sep.json |  |
| O1-45 | OUTLINE | §1u | H | RV2 1.7B-1.5B +0.040 | 0.04 | 0.0401 | MATCH | Haiku 5.5-low | 51 | 2 (1.7B) | ruler/RV2-SEP-LADDER-2026-10-21.json |  |
| O1-46 | OUTLINE | §1u | H | RV2 1.7B-1.5B CI low | -0.019 | -0.019 | MATCH | Haiku 5.5-low | 51 | 2 | ruler/RV2-SEP-LADDER-2026-10-21.json |  |
| O1-47 | OUTLINE | §1u | H | RV2 1.7B-1.5B CI high | 0.096 | 0.0961 | MATCH | Haiku 5.5-low | 51 | 2 | ruler/RV2-SEP-LADDER-2026-10-21.json |  |
| O1-48 | OUTLINE | §1u |  | REFVAR draw A-B 1.7B /dU/ 0.015 | 0.015 | 0.0154 | MATCH | Haiku 5.5-low | 20 | 1 | ruler/refvar/refvar-results.json | sign: A-B = -0.015 |
| O1-49 | OUTLINE | §1u |  | REFVAR draw A-B 4B 0.008 | 0.008 | 0.0079 | MATCH | Haiku 5.5-low | 20 | 1 | ruler/refvar/refvar-results.json |  |
| O1-50 | OUTLINE | §1u |  | REFVAR uncapped - v1 1.7B +0.013 | 0.013 | 0.0129 | MATCH | Haiku 5.5-low | 20 | 1 | ruler/refvar/refvar-results.json |  |
| O1-51 | OUTLINE | §1u |  | REFVAR uncapped - v1 4B +0.001 | 0.001 | 0.0012 | MATCH | Haiku 5.5-low | 20 | 1 | ruler/refvar/refvar-results.json |  |
| O1-52 | OUTLINE | §1u |  | REFVAR 4B-1.7B gap v1 0.084 | 0.084 | 0.0836 | MATCH | Haiku 5.5-low | 20 | 1 | ruler/refvar/refvar-results.json |  |
| O1-53 | OUTLINE | §1u |  | REFVAR 4B-1.7B gap draws 0.072 | 0.072 | 0.0719 | MATCH | Haiku 5.5-low | 20 | 1 | ruler/refvar/refvar-results.json |  |
| O1-54 | OUTLINE | §1u |  | REFVAR Opus+web reference draws 40 | 40 | 40 | MATCH | Opus | 20 | - | ruler/refvar/refs | rows in drawA + drawB |
| O2-01 | OUTLINE | §2 |  | 1.7B K0 U on 80 self-tests 0.393 | 0.393 | 0.3934 | MATCH | Haiku 5.5-low | 80 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-02 | OUTLINE | §2 |  | 1.7B K3 U 0.462 | 0.462 | 0.462 | MATCH | Haiku 5.5-low | 80 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-03 | OUTLINE | §2 |  | 1.7B K3-K0 +0.069 | 0.069 | 0.0686 | MATCH | Haiku 5.5-low | 80 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-04 | OUTLINE | §2 |  | CI low +0.038 | 0.038 | 0.0381 | MATCH | Haiku 5.5-low | 80 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-05 | OUTLINE | §2 |  | CI high +0.099 | 0.099 | 0.0993 | MATCH | Haiku 5.5-low | 80 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-06 | OUTLINE | §2 |  | simplewiki +0.104 (low end K1-K3) | 0.104 | 0.1035 | MATCH | Haiku 5.5-low | 20 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-07 | OUTLINE | §2 |  | simplewiki +0.106 (high end) | 0.106 | 0.1057 | MATCH | Haiku 5.5-low | 20 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-08 | OUTLINE | §2 |  | factbook +0.104 (K3) | 0.104 | 0.1036 | MATCH | Haiku 5.5-low | 20 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-09 | OUTLINE | §2 |  | medlineplus +0.057 (K3) | 0.057 | 0.0568 | MATCH | Haiku 5.5-low | 20 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-10 | OUTLINE | §2 |  | firstaid +0.007 (K3) | 0.007 | 0.0066 | MATCH | Haiku 5.5-low | 20 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-11 | OUTLINE | §2 |  | MAIN off-pack dU high end -0.004 (K1-K4) | -0.004 | -0.0039 | MATCH | Haiku 5.5-low | 97 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-12 | OUTLINE | §2 |  | MAIN off-pack dU low end -0.012 | -0.012 | -0.0118 | MATCH | Haiku 5.5-low | 97 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-13 | OUTLINE | §2 |  | MAIN all CIs straddle 0 (1 = yes) | 1 | 1 | MATCH | Haiku 5.5-low | 97 | 1 | arms/litepacks/aggregates/litepacks.json | boolean |
| O2-14 | OUTLINE | §2 |  | SE off-pack dU high end -0.003 | -0.003 | -0.0033 | MATCH | Haiku 5.5-low | 100 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-15 | OUTLINE | §2 |  | SE off-pack dU low end -0.011 | -0.011 | -0.0108 | MATCH | Haiku 5.5-low | 100 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-16 | OUTLINE | §2 |  | Gemma K0 U 0.395 | 0.395 | 0.3947 | MATCH | Haiku 5.5-low | 80 | 1 | arms/gemma4-e2b/packs/packs-report.json |  |
| O2-17 | OUTLINE | §2 |  | Gemma K3 U 0.497 | 0.497 | 0.4971 | MATCH | Haiku 5.5-low | 80 | 1 | arms/gemma4-e2b/packs/packs-report.json |  |
| O2-18 | OUTLINE | §2 |  | Gemma dU +0.102 | 0.102 | 0.1024 | MATCH | Haiku 5.5-low | 80 | 1 | arms/gemma4-e2b/packs/packs-report.json |  |
| O2-19 | OUTLINE | §2 |  | Gemma dU CI low 0.061 | 0.061 | 0.0608 | MATCH | Haiku 5.5-low | 80 | 1 | arms/gemma4-e2b/packs/packs-report.json |  |
| O2-20 | OUTLINE | §2 |  | Gemma dU CI high 0.144 | 0.144 | 0.144 | MATCH | Haiku 5.5-low | 80 | 1 | arms/gemma4-e2b/packs/packs-report.json |  |
| O2-21 | OUTLINE | §2 |  | DiD vs 1.7B +0.034 | 0.034 | 0.0338 | MATCH | Haiku 5.5-low | 80 | 1 | arms/gemma4-e2b/packs/packs-report.json |  |
| O2-22 | OUTLINE | §2 |  | DiD CI low +0.001 | 0.001 | 0.0006 | MATCH | Haiku 5.5-low | 80 | 1 | arms/gemma4-e2b/packs/packs-report.json |  |
| O2-23 | OUTLINE | §2 |  | DiD CI high +0.066 | 0.066 | 0.0663 | MATCH | Haiku 5.5-low | 80 | 1 | arms/gemma4-e2b/packs/packs-report.json |  |
| O2-24 | OUTLINE | §2 |  | Gemma MAIN K0 U 0.434 | 0.434 | 0.4336 | MATCH | Haiku 5.5-low | 97 | 1 | arms/gemma4-e2b/vs4b/vs4b-report.json |  |
| O2-25 | OUTLINE | §2 |  | 1.7B MAIN K0 U 0.406 | 0.406 | 0.4055 | MATCH | Haiku 5.5-low | 97 | 1 | arms/gemma4-e2b/vs4b/vs4b-report.json |  |
| O2-26 | OUTLINE | §2 |  | Gemma-1.7B MAIN +0.028 | 0.028 | 0.0281 | MATCH | Haiku 5.5-low | 97 | 1 | arms/gemma4-e2b/vs4b/vs4b-report.json |  |
| O2-27 | OUTLINE | §2 |  | Gemma K1 MAIN dU +0.017 | 0.017 | 0.0173 | MATCH | Haiku 5.5-low | 97 | 1 | arms/gemma4-e2b-confirm-gk1/aggregates/gemma4-e2b-confirm-gk1-K1-main-s42.json |  |
| O2-28 | OUTLINE | §2 |  | Gemma K1 MAIN CI low -0.008 | -0.008 | -0.0066 | MATCH | Haiku 5.5-low | 97 | 1 | arms/gemma4-e2b-confirm-gk1/aggregates/gemma4-e2b-confirm-gk1-K1-main-s42.json |  |
| O2-29 | OUTLINE | §2 |  | Gemma K1 MAIN CI high +0.040 | 0.04 | 0.0408 | MATCH | Haiku 5.5-low | 97 | 1 | arms/gemma4-e2b-confirm-gk1/aggregates/gemma4-e2b-confirm-gk1-K1-main-s42.json |  |
| O2-30 | OUTLINE | §2 |  | MATRIX 1.7B KA MAIN dU -0.007 | -0.007 | -0.0072 | MATCH | Haiku 5.5-low | 97 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2-31 | OUTLINE | §2 |  | MATRIX KA MAIN CI low -0.026 | -0.026 | -0.0258 | MATCH | Haiku 5.5-low | 97 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2-32 | OUTLINE | §2 |  | MATRIX KA MAIN CI high +0.012 | 0.012 | 0.0124 | MATCH | Haiku 5.5-low | 97 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2-33 | OUTLINE | §2 |  | CE-unwarned K0 7 | 7 | 7 | MATCH | Haiku 5.5-low | 97 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2-34 | OUTLINE | §2 |  | CE-unwarned KA 12 | 12 | 12 | MATCH | Haiku 5.5-low | 97 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2-35 | OUTLINE | §2 |  | PACKREAD 4B D4 0.650 | 0.65 |  | UNSOURCED | Haiku 5.5-low | 54 | 1 | QUEUE l.1387-1390 (arms/packread has judgments, no aggregate) | judgment rows exist; definition of the scale not in a JSON |
| O2-36 | OUTLINE | §2 |  | PACKREAD 1.7B D4 0.529 | 0.529 |  | UNSOURCED | Haiku 5.5-low | 54 | 1 | QUEUE l.1387-1390 |  |
| O2-37 | OUTLINE | §2 |  | PACKREAD LFM2.5 0.554 | 0.554 |  | UNSOURCED | Haiku 5.5-low | 54 | 1 | QUEUE l.1387-1390 |  |
| O2-38 | OUTLINE | §2 |  | 4B single pack raw +0.032 (Haiku) | 0.032 | 0.032 | MATCH | Haiku 5.5-low | 180 | 1 | arms/packs/aggregates/selftest-scores.json |  |
| O2-39 | OUTLINE | §2 |  | raw CI low +0.016 | 0.016 | 0.016 | MATCH | Haiku 5.5-low | 180 | 1 | arms/packs/aggregates/selftest-scores.json |  |
| O2-40 | OUTLINE | §2 |  | raw CI high +0.050 | 0.05 | 0.05 | MATCH | Haiku 5.5-low | 180 | 1 | arms/packs/aggregates/selftest-scores.json |  |
| O2-41 | OUTLINE | §2 | H | "above_min +0.042 Opus L2" | 0.042 | 0.053 | MISMATCH | Opus | 180 | 1 | arms/packs-l2/aggregates/s_off.json | LABEL: 0.042 (0.024-0.062) is the Opus RAW delta; Opus above_min = 0.053 |
| O2-42 | OUTLINE | §2 | H | "above_min" CI low 0.024 | 0.024 | 0.03 | MISMATCH | Opus | 180 | 1 | arms/packs-l2/aggregates/s_off.json | raw CI low = 0.024 |
| O2-43 | OUTLINE | §2 | H | "above_min" CI high 0.062 | 0.062 | 0.078 | MISMATCH | Opus | 180 | 1 | arms/packs-l2/aggregates/s_off.json | raw CI high = 0.062 |
| O2-44 | OUTLINE | §2 |  | wave 3 +0.045 Opus | 0.045 | 0.045 | MATCH | Opus | 40 | 1 | arms/packs-l2/aggregates/wave3_s_off.json | raw scale |
| O2-45 | OUTLINE | §2 |  | wave 3 CI low +0.007 | 0.007 | 0.007 | MATCH | Opus | 40 | 1 | arms/packs-l2/aggregates/wave3_s_off.json |  |
| O2-46 | OUTLINE | §2 |  | wave 3 CI high +0.087 | 0.087 | 0.087 | MATCH | Opus | 40 | 1 | arms/packs-l2/aggregates/wave3_s_off.json |  |
| O2-47 | OUTLINE | §2 |  | deep + think: packs add -0.002 | -0.002 | -0.002 | MATCH | Haiku 5.5-low | 180 | 1 | arms/packs/aggregates/selftest-deep.json |  |
| O2-48 | OUTLINE | §2 |  | deep packs CI low -0.020 | -0.02 | -0.02 | MATCH | Haiku 5.5-low | 180 | 1 | arms/packs/aggregates/selftest-deep.json |  |
| O2-49 | OUTLINE | §2 |  | deep packs CI high +0.016 | 0.016 | 0.016 | MATCH | Haiku 5.5-low | 180 | 1 | arms/packs/aggregates/selftest-deep.json |  |
| O2-50 | OUTLINE | §2 |  | deep reads +0.054 over 4B | 0.054 | 0.054 | MATCH | Haiku 5.5-low | 180 | 1 | arms/packs/aggregates/selftest-deep.json |  |
| O2-51 | OUTLINE | §2 |  | venues P5 0/7 -> 7/7 | 7 |  | UNSOURCED | 0 judge | 7 | 2 | arms/venuegps/VENUEGPS-2.md (blind-side venue scorer output) | prose only; scorer outputs under blind/ |
| O2-52 | OUTLINE | §2 |  | area tile +3.65 MB | 3.65 |  | UNSOURCED | - | - | - | arms/venuegps/VENUEGPS-2.md | tiles.json has fetch metadata, not the kit delta |
| O2-53 | OUTLINE | §2 |  | warned share SE +0.12 (low end K1-K4) | 0.12 | 0.12 | MATCH | Haiku 5.5-low | 100 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-54 | OUTLINE | §2 |  | warned share SE +0.19 (high end) | 0.19 | 0.19 | MATCH | Haiku 5.5-low | 100 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-55 | OUTLINE | §2 |  | 4B fact article kept 68/180 (one pack) | 68 | 68 | MATCH | 0 judge | 180 | - | arms/packroute/aggregates/step0.json |  |
| O2-56 | OUTLINE | §2 |  | 4B fact article kept 46/180 (9 peers) | 46 | 46 | MATCH | 0 judge | 180 | - | arms/packroute/aggregates/step0.json |  |
| O2-57 | OUTLINE | §2 |  | 4B crowding -0.019 Opus L2 | -0.019 | -0.019 | MATCH | Opus | 180 | 1 | arms/packs-l2/aggregates/p_s.json |  |
| O2-58 | OUTLINE | §2 |  | crowding CI low -0.035 | -0.035 | -0.035 | MATCH | Opus | 180 | 1 | arms/packs-l2/aggregates/p_s.json |  |
| O2-59 | OUTLINE | §2 |  | crowding CI high -0.003 | -0.003 | -0.003 | MATCH | Opus | 180 | 1 | arms/packs-l2/aggregates/p_s.json |  |
| O2-60 | OUTLINE | §2 |  | prompt tokens K0 384 | 384 | 383.7 | MATCH | - | 97 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-61 | OUTLINE | §2 |  | prompt tokens K1-K4 low 729 | 729 | 729 | MATCH | - | 97 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-62 | OUTLINE | §2 |  | prompt tokens K1-K4 high 792 | 792 | 792 | MATCH | - | 97 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-63 | OUTLINE | §2 |  | desktop TTFT K0 1.6 s | 1.6 | 1.5621 | MATCH | - | 97 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-64 | OUTLINE | §2 |  | desktop TTFT K1-K4 low 3.9 s | 3.9 | 3.8516 | MATCH | - | 97 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-65 | OUTLINE | §2 |  | desktop TTFT K1-K4 high 4.4 s | 4.4 | 4.4379 | MATCH | - | 97 | 1 | arms/litepacks/aggregates/litepacks.json |  |
| O2-66 | OUTLINE | §2 |  | disk +0.74 GB (K1) | 0.74 | 0.7355 | MATCH | - | - | - | arms/litepacks/aggregates/litepacks.json | decimal GB |
| O2-67 | OUTLINE | §2 |  | disk +2.5 GB (K4) | 2.5 | 2.5422 | MATCH | - | - | - | arms/litepacks/aggregates/litepacks.json | decimal GB |
| O2-68 | OUTLINE | §2 | H | A-union +2.4 s retrieval p50 (1.7B) | 2.4 |  | UNSOURCED | - | 73 | 1 | arms/aunion-pixel (A-union side only) | A-union side 3.99 s in aunion-summary.json; the 1.5-1.6 s baseline has no JSON field (rows firstSourcesMs p50 = 1.70 s, a different stamp) |
| O2-69 | OUTLINE | §2 |  | A-union answer p50 +3.4 s (1.7B) | 3.4 | 3.4082 | MATCH | - | 73 | 1 | arms/aunion-pixel/aunion73-a/rows.jsonl | rows medians 7.57 - 4.16 |
| O2-70 | OUTLINE | §2 |  | V-para kit holds the fact 6/51 | 6 |  | UNSOURCED | jev | 51 | - | VPARA-DIAGNOSIS §1 / PACKCOND-P1 (no count field in packcond-K-vpara.json) |  |
| O2-71 | OUTLINE | §2 |  | V-para all packs 10/51 | 10 |  | UNSOURCED | jev | 51 | - | VPARA-DIAGNOSIS §1 / PACKCOND-P2 |  |
| O2u-01 | OUTLINE | §2u | H | FACTPRESENT self-test cell a +0.139 | 0.139 | 0.139 | MATCH | Haiku 5.5-low | 27 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-02 | OUTLINE | §2u | H | cell a CI low +0.075 | 0.075 | 0.075 | MATCH | Haiku 5.5-low | 27 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-03 | OUTLINE | §2u | H | cell a CI high +0.201 | 0.201 | 0.201 | MATCH | Haiku 5.5-low | 27 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-04 | OUTLINE | §2u |  | cell a n 27 | 27 | 27 | MATCH | Haiku 5.5-low | 27 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-05 | OUTLINE | §2u |  | Gemma cell a +0.168 | 0.168 | 0.168 | MATCH | Haiku 5.5-low | 27 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-06 | OUTLINE | §2u | H | real MAIN cell a K3-K0 -0.010 | -0.01 | -0.01 | MATCH | Haiku 5.5-low | 10 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-07 | OUTLINE | §2u | H | real cell a CI low -0.077 | -0.077 | -0.077 | MATCH | Haiku 5.5-low | 10 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-08 | OUTLINE | §2u | H | real cell a CI high +0.050 | 0.05 | 0.05 | MATCH | Haiku 5.5-low | 10 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-09 | OUTLINE | §2u |  | real cell a n 10 | 10 | 10 | MATCH | Haiku 5.5-low | 10 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-10 | OUTLINE | §2u |  | strict +0.005 | 0.005 | 0.005 | MATCH | Haiku 5.5-low | 7 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-11 | OUTLINE | §2u |  | strict n 7 | 7 | 7 | MATCH | Haiku 5.5-low | 7 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-12 | OUTLINE | §2u |  | K1-K0 -0.015 | -0.015 | -0.015 | MATCH | Haiku 5.5-low | - | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-13 | OUTLINE | §2u |  | cell b +0.059 | 0.059 | 0.059 | MATCH | Haiku 5.5-low | 13 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-14 | OUTLINE | §2u |  | cell b CI low +0.022 | 0.022 | 0.022 | MATCH | Haiku 5.5-low | 13 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-15 | OUTLINE | §2u |  | cell b CI high +0.093 | 0.093 | 0.093 | MATCH | Haiku 5.5-low | 13 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-16 | OUTLINE | §2u |  | cell b n 13 | 13 | 13 | MATCH | Haiku 5.5-low | 13 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-17 | OUTLINE | §2u |  | MAIN 92 keyed | 92 | 92 | MATCH | - | 92 | - | ruler/FACTPRESENT-2026-10-21.json |  |
| O2u-18 | OUTLINE | §2u | H | INPACK K3-K0 -0.023 | -0.023 | -0.023 | MATCH | Haiku 5.5-low | 17 | 1 | ruler/inpack-split.json |  |
| O2u-19 | OUTLINE | §2u | H | INPACK CI low -0.081 | -0.081 | -0.081 | MATCH | Haiku 5.5-low | 17 | 1 | ruler/inpack-split.json |  |
| O2u-20 | OUTLINE | §2u | H | INPACK CI high +0.027 | 0.027 | 0.027 | MATCH | Haiku 5.5-low | 17 | 1 | ruler/inpack-split.json |  |
| O2u-21 | OUTLINE | §2u |  | INPACK n 17 | 17 | 17 | MATCH | Haiku 5.5-low | 17 | 1 | ruler/inpack-split.json |  |
| O2u-22 | OUTLINE | §2u |  | 4B in-pack minus off-pack -0.081 | -0.081 | -0.081 | MATCH | Haiku 5.5-low | 97 | 1 | ruler/inpack-split.json |  |
| O2u-23 | OUTLINE | §2u |  | ORACLE U 0.427 | 0.427 | 0.427 | MATCH | Haiku 5.5-low | 30 | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| O2u-24 | OUTLINE | §2u |  | ORACLE control U 0.412 | 0.412 | 0.412 | MATCH | Haiku 5.5-low | 30 | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| O2u-25 | OUTLINE | §2u | H | ORACLE +0.015 | 0.015 | 0.015 | MATCH | Haiku 5.5-low | 30 | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| O2u-26 | OUTLINE | §2u | H | ORACLE CI low -0.029 | -0.029 | -0.029 | MATCH | Haiku 5.5-low | 30 | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| O2u-27 | OUTLINE | §2u | H | ORACLE CI high +0.059 | 0.059 | 0.059 | MATCH | Haiku 5.5-low | 30 | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| O2u-28 | OUTLINE | §2u |  | = 10 % of the self-test gain | 0.1 | 0.1079 | MATCH | Haiku 5.5-low | - | - | arms/oracle-real/aggregates/oracle-real.json / ruler/FACTPRESENT-2026-10-21.json | derived 0.015/0.139 = 0.108 (11 %); vs LITEPACKS +0.069 it is 22 % |
| O2u-29 | OUTLINE | §2u |  | ORACLE n 30 | 30 | 30 | MATCH | Haiku 5.5-low | 30 | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| O2u-30 | OUTLINE | §2u |  | ORACLE 98 Haiku calls | 98 | 98 | MATCH | Haiku 5.5-low | - | - | arms/oracle-real/judgments | row count |
| O2u-31 | OUTLINE | §2u |  | clean key-fact chunks +0.106 | 0.106 | 0.106 | MATCH | Haiku 5.5-low | 6 | 1 | arms/oracle-real/aggregates/oracle-real.json | post-hoc |
| O2u-32 | OUTLINE | §2u |  | clean chunks CI low +0.054 | 0.054 | 0.054 | MATCH | Haiku 5.5-low | 6 | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| O2u-33 | OUTLINE | §2u |  | clean chunks CI high +0.159 | 0.159 | 0.159 | MATCH | Haiku 5.5-low | 6 | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| O2u-34 | OUTLINE | §2u |  | lexical golds -0.009 | -0.009 | -0.009 | MATCH | Haiku 5.5-low | - | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| O2u-35 | OUTLINE | §2u |  | Jaccard median real 0.053 | 0.053 | 0.0532 | MATCH | - | 37 | - | ruler/PK3-OVERLAP-2026-10-21.json |  |
| O2u-36 | OUTLINE | §2u |  | Jaccard median self-tests 0.045 | 0.045 | 0.0445 | MATCH | - | 80 | - | ruler/PK3-OVERLAP-2026-10-21.json |  |
| O2u-37 | OUTLINE | §2u |  | reweighted 1.7B gain +0.064 | 0.064 | 0.064 | MATCH | Haiku 5.5-low | 80 | 1 | ruler/PK3-OVERLAP-2026-10-21.json |  |
| O2u-38 | OUTLINE | §2u |  | reweighted CI low +0.035 | 0.035 | 0.035 | MATCH | Haiku 5.5-low | 80 | 1 | ruler/PK3-OVERLAP-2026-10-21.json |  |
| O2u-39 | OUTLINE | §2u |  | reweighted CI high +0.095 | 0.095 | 0.095 | MATCH | Haiku 5.5-low | 80 | 1 | ruler/PK3-OVERLAP-2026-10-21.json |  |
| O2u-40 | OUTLINE | §2u |  | Gemma reweighted +0.101 | 0.101 | 0.101 | MATCH | Haiku 5.5-low | 80 | 1 | ruler/PK3-OVERLAP-2026-10-21.json |  |
| O2u-41 | OUTLINE | §2u |  | 37 real golds | 37 | 37 | MATCH | - | 37 | - | ruler/PK3-OVERLAP-2026-10-21.json |  |
| O2u-RFS1 | OUTLINE | §2u |  | RAG-FUNNEL K3 MAIN keyed 92 S1 | 45 | 45 | MATCH | Haiku 5.5-low labels | 92 | 1 | ruler/RAG-FUNNEL-2026-10-21.json |  |
| O2u-RFS2 | OUTLINE | §2u |  | RAG-FUNNEL K3 MAIN keyed 92 S2 | 7 | 7 | MATCH | Haiku 5.5-low labels | 92 | 1 | ruler/RAG-FUNNEL-2026-10-21.json |  |
| O2u-RFS3 | OUTLINE | §2u |  | RAG-FUNNEL K3 MAIN keyed 92 S3 | 17 | 17 | MATCH | Haiku 5.5-low labels | 92 | 1 | ruler/RAG-FUNNEL-2026-10-21.json |  |
| O2u-RFS4 | OUTLINE | §2u |  | RAG-FUNNEL K3 MAIN keyed 92 S4 | 15 | 15 | MATCH | Haiku 5.5-low labels | 92 | 1 | ruler/RAG-FUNNEL-2026-10-21.json |  |
| O2u-RFS5 | OUTLINE | §2u |  | RAG-FUNNEL K3 MAIN keyed 92 S5 | 8 | 8 | MATCH | Haiku 5.5-low labels | 92 | 1 | ruler/RAG-FUNNEL-2026-10-21.json |  |
| O2u-42 | OUTLINE | §2u |  | S1 of which cooking/money 39 | 39 | 39 | MATCH | Haiku 5.5-low | 40 | 1 | ruler/RAG-FUNNEL-2026-10-21.json |  |
| O2u-MX-q17-K0 | OUTLINE | §2u |  | MATRIX U q17-K0 on 80 | 0.381 | 0.3808 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-MX-q17-K3mb | OUTLINE | §2u |  | MATRIX U q17-K3mb on 80 | 0.462 | 0.462 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-MX-q17-KA | OUTLINE | §2u |  | MATRIX U q17-KA on 80 | 0.435 | 0.435 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-MX-gem-K0 | OUTLINE | §2u |  | MATRIX U gem-K0 on 80 | 0.395 | 0.3947 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-MX-gem-K3 | OUTLINE | §2u |  | MATRIX U gem-K3 on 80 | 0.497 | 0.4971 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-MX-gem-KA | OUTLINE | §2u |  | MATRIX U gem-KA on 80 | 0.45 | 0.4497 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-MX-q4b-K0 | OUTLINE | §2u |  | MATRIX U q4b-K0 on 80 | 0.461 | 0.4606 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-MX-q4b-K3 | OUTLINE | §2u |  | MATRIX U q4b-K3 on 80 | 0.545 | 0.5446 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-MX-q4b-KA | OUTLINE | §2u |  | MATRIX U q4b-KA on 80 | 0.513 | 0.5128 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-43 | OUTLINE | §2u |  | KA-K0 low end +0.052 | 0.052 | 0.0521 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-44 | OUTLINE | §2u |  | KA-K0 high end +0.055 | 0.055 | 0.055 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-45 | OUTLINE | §2u |  | KA-K0 all CI low > 0 (1 = yes) | 1 | 1 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json | boolean |
| O2u-46 | OUTLINE | §2u |  | 4B-1.7B ~ +0.08 at every pack set (mean of K0/K3/KA) | 0.08 | 0.0801 | MATCH | Haiku 5.5-low | 80 | 1 | arms/coverage-matrix/matrix-report.json | cells: +0.080 / +0.083 / +0.078 |
| O2u-47 | OUTLINE | §2u |  | MATRIX 652 Haiku calls | 652 | 646 | MISMATCH | Haiku 5.5-low | - | - | arms/coverage-matrix/*/judgments | row count of judgments.jsonl files (MATRIX.md l.43 itemises 652) |
| O2u-48 | OUTLINE | §2u |  | A-union MAIN CE-unwarned rate diff +0.052 | 0.052 | 0.0515 | MATCH | Haiku 5.5-low | 97 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-49 | OUTLINE | §2u |  | CE rate diff CI low -0.010 | -0.01 | -0.0103 | MATCH | Haiku 5.5-low | 97 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-50 | OUTLINE | §2u |  | CE rate diff CI high +0.113 | 0.113 | 0.1134 | MATCH | Haiku 5.5-low | 97 | 1 | arms/coverage-matrix/matrix-report.json |  |
| O2u-51 | OUTLINE | §2u | H | A-union retrieval +2.4 s p50 (dup of O2-68) | 2.4 |  | UNSOURCED | - | 73 | 1 | arms/aunion-pixel | baseline side has no JSON field |
| O2u-52 | OUTLINE | §2u |  | baseline retrieval p50 1.5-1.6 s | 1.5 |  | UNSOURCED | - | 73 | 1 | arms/aunion-pixel/AUNION-PIXEL.md | prose only |
| O2u-53 | OUTLINE | §2u |  | A-union retrieval p50 low end 3.9 s | 3.9 | 3.902 | MATCH | - | 73 | 1 | arms/aunion-pixel/%s/aunion-summary.json | 1.7B runs (aunion10-a 3.90, aunion73-a 3.99); Gemma and 4B A-union runs are 4.2-4.3 s, outside the quoted range |
| O2u-54 | OUTLINE | §2u |  | A-union retrieval p50 high end 4.0 s | 4 | 3.9915 | MATCH | - | 73 | 1 | arms/aunion-pixel/%s/aunion-summary.json | 1.7B runs |
| O2u-54b | OUTLINE | §2u |  | A-union retrieval p50 on the other tiers (implied 3.9-4.0) | 4 | 4.408 | MISMATCH | - | 73 | 1 | arms/aunion-pixel/%s/aunion-summary.json | Gemma 4.41 s / 4B 4.25 s A-union runs; the outline range 3.9-4.0 is 1.7B-only |
| O2u-55 | OUTLINE | §2u |  | A-union retrieval max 10.7 s | 10.7 | 10.71 | MATCH | - | 73 | 1 | arms/aunion-pixel/aunion73-a/aunion-summary.json | 1.7B run; 4B run max 11.1 s |
| O2u-56 | OUTLINE | §2u |  | A-union answer p50 +3.4 s (dup) | 3.4 | 3.4082 | MATCH | - | 73 | 1 | arms/aunion-pixel/aunion73-a/rows.jsonl |  |
| O2u-57 | OUTLINE | §2u |  | 1.7B PSS A-union 3.41 | 3.41 | 3.413 | MATCH | - | 73 | 1 | arms/aunion-pixel/aunion73-a/aunion-summary.json |  |
| O2u-58 | OUTLINE | §2u |  | 1.7B PSS base 3.39 | 3.39 | 3.39 | MATCH | - | 73 | 1 | ruler/SPEED-PRECHECK-2026-10-21.json |  |
| O2u-59 | OUTLINE | §2u |  | Gemma PSS A-union 4.38 | 4.38 | 4.3813 | MATCH | - | 73 | 1 | arms/aunion-pixel/gemmaa73-a/aunion-summary.json |  |
| O2u-60 | OUTLINE | §2u |  | Gemma PSS base 4.52 | 4.52 | 4.52 | MATCH | - | 73 | 1 | ruler/SPEED-PRECHECK-2026-10-21.json |  |
| O2u-61 | OUTLINE | §2u |  | 4B PSS A-union 4.76 | 4.76 | 4.7643 | MATCH | - | 73 | 1 | arms/aunion-pixel/q4ba73-a/aunion-summary.json |  |
| O2u-62 | OUTLINE | §2u |  | 4B PSS base 4.92 | 4.92 | 4.92 | MATCH | - | 72 | 1 | ruler/SPEED-PRECHECK-2026-10-21.json |  |
| O2u-63 | OUTLINE | §2u |  | 0 LMK on all three tiers | 0 | 0 | MATCH | - | 73 | 1 | arms/aunion-pixel/%s/aunion-summary.json |  |
| O2u-64 | OUTLINE | §2u |  | ~0.15 s per small pack | 0.15 |  | UNSOURCED | - | - | - | arms/aunion-pixel/AUNION-PIXEL.md | prose only (sql_ms_by_db is a sum, not per query) |
| O2u-65 | OUTLINE | §2u |  | PK-5 kept-source identity 81/97 | 81 |  | UNSOURCED | - | 97 | - | arms/aunion-pixel/AUNION-PIXEL.md (replay) | no JSON field |
| O2u-66 | OUTLINE | §2u |  | PK-5 identity 83.5 % | 0.835 | 0.8351 | MATCH | - | 97 | - | derived 81/97 | arithmetic only |
| O2u-67 | OUTLINE | §2u |  | PK-5 merged U 0.365 | 0.365 | 0.3648 | MATCH | Haiku 5.5-low | 16 | 1 | arms/aunion-pixel/pk5/aggregates/pk5-M-diff16-s42.json |  |
| O2u-68 | OUTLINE | §2u |  | PK-5 control U 0.399 | 0.399 | 0.3991 | MATCH | Haiku 5.5-low | 16 | 1 | arms/aunion-pixel/pk5/aggregates/pk5-M-diff16-s42.json | derived merged - delta |
| O2u-69 | OUTLINE | §2u |  | PK-5 -0.034 | -0.034 | -0.0343 | MATCH | Haiku 5.5-low | 16 | 1 | arms/aunion-pixel/pk5/aggregates/pk5-M-diff16-s42.json |  |
| O2u-70 | OUTLINE | §2u |  | PK-5 16 items | 16 | 16 | MATCH | Haiku 5.5-low | 16 | 1 | arms/aunion-pixel/pk5/aggregates/pk5-M-diff16-s42.json |  |
| O2u-71 | OUTLINE | §2u |  | PK-5 38 Haiku | 38 | 38 | MATCH | Haiku 5.5-low | - | - | arms/aunion-pixel/pk5/judgments | row count |
| P1-01 | PLAN | §1 | H | gap 0.586 | 0.586 | 0.5857 | MATCH | Opus rows + jev labels | 51 | s42 | arms/lossmap/aggregates/lossmap-K-vpara-s42.json | 1 - mean item ratio |
| P1-02 | PLAN | §1 | H | wrong from memory share 0.167 | 0.167 | 0.1671 | MATCH | Opus + jev | 51 | s42 | lossmap-K-vpara-s42.json | wrong & labels.source_on_topic false |
| P1-03 | PLAN | §1 |  | wrong from memory items 12 | 12 | 12 | MATCH | Opus + jev | 51 | s42 | lossmap-K-vpara-s42.json |  |
| P1-04 | PLAN | §1 | H | absent knowledge share 0.239 | 0.239 | 0.2389 | MATCH | Opus + jev | 51 | s42 | lossmap-K-vpara-s42.json |  |
| P1-05 | PLAN | §1 |  | absent knowledge items 24 | 24 | 24 | MATCH | Opus + jev | 51 | s42 | lossmap-K-vpara-s42.json |  |
| P1-06 | PLAN | §1 | H | misread (on-topic source) share 0.142 | 0.142 | 0.1422 | MATCH | Opus + jev | 51 | s42 | lossmap-K-vpara-s42.json |  |
| P1-07 | PLAN | §1 |  | misread items 11 | 11 | 11 | MATCH | Opus + jev | 51 | s42 | lossmap-K-vpara-s42.json |  |
| P1-08 | PLAN | §1 |  | thin share 0.038 | 0.038 | 0.0376 | MATCH | Opus + jev | 51 | s42 | lossmap-K-vpara-s42.json |  |
| P1-09 | PLAN | §1 |  | thin items 4 | 4 | 4 | MATCH | Opus + jev | 51 | s42 | lossmap-K-vpara-s42.json |  |
| P1-10 | PLAN | §1 |  | refusals/truncation 0 | 0 | 0 | MATCH | Opus + jev | 51 | s42 | lossmap-K-vpara-s42.json | declined items |
| P1-11 | PLAN | §1 |  | kit 6/51 (dup O2-70) | 6 |  | UNSOURCED | jev | 51 | - | VPARA-DIAGNOSIS / PACKCOND-P1 |  |
| P1-12 | PLAN | §1 |  | all packs 10/51 (dup O2-71) | 10 |  | UNSOURCED | jev | 51 | - | VPARA-DIAGNOSIS / PACKCOND-P2 |  |
| P1-13 | PLAN | §1 |  | full Wikipedia 9/34 | 9 | 9 | MATCH | jev | 34 | - | arms/wikifull/aggregates/stageAB-pooled.json |  |
| P1-14 | PLAN | §1 |  | absent items 34 | 34 | 34 | MATCH | jev | 34 | - | arms/wikifull/aggregates/stageAB-pooled.json |  |
| P1-15 | PLAN | §1 |  | no kept source 29/51 | 29 | 29 | MATCH | Opus + jev | 51 | s42 | lossmap-K-vpara-s42.json | n_kept == 0 |
| P1-16 | PLAN | §1 |  | those carry 58 % of the loss | 0.58 | 0.5796 | MATCH | Opus + jev | 51 | s42 | lossmap-K-vpara-s42.json |  |
| P1-17 | PLAN | §1 | H | ladder 4B 0.26 floor-adj | 0.26 | 0.2611 | MATCH | Opus | 51 | 2 | arms/deepvpara/aggregates/dv-vpara-2seed.L2.json |  |
| P1-18 | PLAN | §1 | H | ladder deep 0.33 | 0.33 | 0.3288 | MATCH | Opus | 51 | 2 | arms/deepvpara/aggregates/dv-vpara-2seed.L2.json |  |
| P1-19 | PLAN | §1 | H | ladder deep + think 512 0.44 | 0.44 | 0.4359 | MATCH | Opus | 51 | 2 | arms/dt512/aggregates/L2-H-2seed.opus.json |  |
| P1-20 | PLAN | §1 |  | 1.7B = 4B - 0.07..0.11 | 0.07 |  | UNSOURCED | Haiku 5.5-low | - | - | CRITIQUE-2026-10-16 (md) | prose only |
| P1-21 | PLAN | §1 |  | Codex +0.10 on each rung | 0.1 |  | UNSOURCED | Codex gpt-5.6-sol | 51 | 2 | blind/V-para/runs-xfam (XFAM-REPORT.md; off-limits here) | blind-only source: coordinator must re-derive |
| P1-22 | PLAN | §1 | H | deep + think Codex 0.577 | 0.577 |  | UNSOURCED | Codex gpt-5.6-sol | 51 | 2 | blind/V-para/runs-xfam | blind-only source |
| P1-23 | PLAN | §1 |  | win-rate ~0 everywhere | 0 |  | UNSOURCED | both | - | - | CLAIM-RESULTS-cut6 / XFAM (md, blind) | prose only |
| P1-24 | PLAN | §1 |  | +0.03 reading (DEEPREAD) | 0.03 |  | UNSOURCED | Opus | - | - | arms/deepread (md) | prose only |
| P1u-01 | PLAN | §1u | H | gate visible CE 7 (Opus) | 7 | 7 | MATCH | Opus | 177 | 1 | arms/refuse-unsupported/ce-opus-ru/ceopusru-opus.json |  |
| P1u-02 | PLAN | §1u | H | gate visible CE 3 (Opus) | 3 | 3 | MATCH | Opus | 177 | 1 | arms/refuse-unsupported/ce-opus-ru/ceopusru-opus.json |  |
| P1u-03 | PLAN | §1u |  | of 177 | 177 | 177 | MATCH | Opus | 177 | 1 | arms/refuse-unsupported/ce-opus-ru/ceopusru-opus.json |  |
| P1u-04 | PLAN | §1u |  | Haiku was 10 -> 4 | 10 | 10 | MATCH | Haiku 5.5-low | 177 | 1 | arms/refuse-unsupported/ce-opus-ru/ceopusru-haiku.json |  |
| P1u-05 | PLAN | §1u |  | Haiku 4 | 4 | 4 | MATCH | Haiku 5.5-low | 177 | 1 | arms/refuse-unsupported/ce-opus-ru/ceopusru-haiku.json |  |
| P1u-06 | PLAN | §1u |  | FR 0/14 | 0 | 0 | MATCH | Opus | 14 | 1 | arms/refuse-unsupported/ce-opus-ru/ceopusru-opus.json |  |
| P1u-07 | PLAN | §1u |  | FR denominator 14 | 14 | 14 | MATCH | Opus | 14 | 1 | arms/refuse-unsupported/ce-opus-ru/ceopusru-opus.json |  |
| P1u-08 | PLAN | §1u |  | 6 Opus-correct answers refused | 6 | 6 | MATCH | Opus | 177 | 1 | arms/refuse-unsupported/ce-opus-ru/ceopusru-opus.json |  |
| P1u-09 | PLAN | §1u |  | fact-added real -0.010 (dup) | -0.01 | -0.01 | MATCH | Haiku 5.5-low | 10 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| P1u-10 | PLAN | §1u |  | self-tests +0.139 (dup) | 0.139 | 0.139 | MATCH | Haiku 5.5-low | 27 | 1 | ruler/FACTPRESENT-2026-10-21.json |  |
| P1u-11 | PLAN | §1u |  | matching pack -0.023 (dup) | -0.023 | -0.023 | MATCH | Haiku 5.5-low | 17 | 1 | ruler/inpack-split.json |  |
| P1u-12 | PLAN | §1u |  | oracle +0.015 (dup) | 0.015 | 0.015 | MATCH | Haiku 5.5-low | 30 | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| P1u-13 | PLAN | §1u |  | oracle CI low -0.029 (dup) | -0.029 | -0.029 | MATCH | Haiku 5.5-low | 30 | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| P1u-14 | PLAN | §1u |  | oracle CI high +0.059 (dup) | 0.059 | 0.059 | MATCH | Haiku 5.5-low | 30 | 1 | arms/oracle-real/aggregates/oracle-real.json |  |
| P1u-15 | PLAN | §1u |  | 1.7B-1.5B +0.040 (dup) | 0.04 | 0.0401 | MATCH | Haiku 5.5-low | 51 | 2 | ruler/RV2-SEP-LADDER-2026-10-21.json |  |
| P1u-16 | PLAN | §1u |  | CI low -0.019 (dup) | -0.019 | -0.019 | MATCH | Haiku 5.5-low | 51 | 2 | ruler/RV2-SEP-LADDER-2026-10-21.json |  |
| P1u-17 | PLAN | §1u |  | CI high +0.096 (dup) | 0.096 | 0.0961 | MATCH | Haiku 5.5-low | 51 | 2 | ruler/RV2-SEP-LADDER-2026-10-21.json |  |
| P1u-18 | PLAN | §1u | H | 4B over Gemma +0.117 | 0.117 | 0.1167 | MATCH | Haiku 5.5-low | 51 | 2 | ruler/RV2-SEP-LADDER-2026-10-21.json |  |

## Reproduce
`python3 rnd/research/coordinator/ruler/tools/recompute_page_numbers.py --json CV5-NUMBERS-2026-10-21.json --table /tmp/t.md` (reads only rnd/, boar-eval/runs and handoff/ files; never blind/, rnd/veil or bench/v0.4).
