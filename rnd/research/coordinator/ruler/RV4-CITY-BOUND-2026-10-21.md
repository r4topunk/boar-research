# RV4-CITY-BOUND: the 7 current-city items CAN move the verdict band; pre-register them as a separate stratum, scored as given (2026-10-21)

TL;DR (0 LLM, 0 judge; v0.4 read only through INPACK-STRATUM tags: ids, has_location, health_safety, anchor_vexact; criterion RV24-criterion.md sha 53f75edc…, committed 69430af4 before computing):
- The 7 location items (cw-027/028/029, cx-027/028/029/038; all travel, weight 1, all in H) hold **7/65.5 = 10.7 %** of the headline weight. The dev reference-mass proxy gives 9.8 % (8.9–10.6 %).
- **Max swing (all 0 vs all 1) ≥ 0.107 U-total**, whatever the reference scores. Refusal → reference-level (tile ceiling): **0.098 (0.089–0.106)**. Even refusal → memory-answer level: **0.041–0.054** (4B: 0.050, CI 0.033–0.076).
- **Kill branch: CI high 0.107 > 0.03.** The hypothesis ("≤ 0.03, cannot change the verdict") is FALSE.
- Band flips: scoring the 7 as 0 vs excluding them flips the 0.50 band iff U-total without them is in **0.50–0.56**. Refusal vs tile ceiling flips it iff U-total without them is in **0.44–0.56**.

## 1. Bound
| quantity | nominal (equal ref mass) | dev proxy (CI) |
|---|---|---|
| share φ of the 7 items in Σ w s_ref | 0.107 | 0.098 (0.089–0.106) |
| swing all 0 → all 1 | ≥ 0.107 (7/D, D ≤ 65.5) | — |
| refusal (0) → app = reference (tile ceiling) | 0.107 | 0.098 (0.089–0.106) |
| refusal → 4B memory-answer level (dev travel U 0.51) | 0.054 | 0.050 (0.033–0.076) |
| refusal → 1.7B memory-answer level (dev travel U 0.42) | 0.045 | 0.041 |
| excluded vs scored 0 = φ × U_excl | 0.053 at U_excl 0.50 | 0.049 |
Proxy inputs: the v0.1 travel ids with judge.v1 rows (vit-trv-003/004, trv-002/004; n 4, so this is wide). ρ = reference mass on travel / overall = 0.91 (0.81–0.99).

## 2. Deviations (criterion method vs what exists)
- The method named food-001/002/006 and vx-003/4/5 as proxies. The food items have **no judge.v1 rows**: judge.mjs skips venue-list items, so the 57 exclude them. vx-* are blind. Neither was read. VENUEGPS-2 measured plumbing (P5 7/7, OSM gold), not U. So the tile path is modelled as a ceiling (app = reference), not measured.
- The bound does not depend on the proxy. The 7/65.5 floor on the max swing holds for any reference scores, and so does the conclusion.
- Tags cannot show which of the 7 are food/drink-intent. Only food/drink questions reach the tile path; no route passes the device location to the model otherwise (TILE-PATH §2). So even the desktop runner with tiles may lift only some of the 7.

## 3. How to report the current-city stratum (recommendation for the R2 spec sha, 10-23; no change to the frozen set)
1. **Headline U-total = all 71 scored as given** (spec §1.2/§3.3: U-total is never dropped; a refusal is a true 0; a memory answer is scored as given). Exclusion with the weight redistributed is **not** the spec's rule, and choosing it after R4 would be post-hoc stratum surgery.
2. Pre-register "current-city (device location), n 7" as its **own stratum row**. Print **U-total with and without the 7** next to each other. The verdict uses "with".
3. The headline row states: "the submitted APK has no location or places path; it cannot answer current-city questions (7 of 71 items, 10.7 % of headline weight)".
4. One labelled sensitivity row: "with device location + area tile (desktop runner, not the submitted APK)". It is never the headline.
5. Flag on the card: if the "with" vs "without" U-totals fall on different sides of 0.50 (that happens iff U-without is in 0.50–0.56), the verdict sentence names both.

## Files
- RV4-CITY-BOUND-2026-10-21.json, tools/rv4_city_bound.py (`python3 -I tools/rv4_city_bound.py RV4-CITY-BOUND-2026-10-21.json`), RV24-criterion.md + .sha256.
- Exposure: no new v0.4 field or file opened (INPACK-STRATUM json tags only, already logged), no blind/, no rnd/veil.
