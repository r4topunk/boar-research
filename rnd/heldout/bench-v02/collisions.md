# bench v0.2: similarity gates + fact checks (2026-10-02)
TL;DR: **38 rewrites (writer-a 18, writer-b 20)**: 23 threshold + 15 topic. Schema v0.2 OK: 110/110 items valid, and every gold passes its own precheck. Fact checks: 1 fix needed (Mont Blanc), 1 minor fix (B03), the rest ok. Full data in `collisions.json`.

## Method
- Collision = word-Jaccard > 0.30 (`v0.1/validate.py` tokens) OR bge-small-en-v1.5 cosine ≥ 0.90. Pools: the 110 new items, v0.1 public (60), safety v0.3 (12), held-out v0.1 (30, read as `build.py` reads it), a competitor team @87bb6e9 (31). Held-out and a competitor team results are numbers only.
- Resolution: cross-writer pairs sorted by A id, alternating keep A / keep B. Topic pairs continue the same counter (#24 onward). A pair is skipped if one side is already a rewrite. An item that collides with v0.1, safety, held-out or a competitor team is rewritten.
- Highest external scores: v0.1 J .281 / cos .788 · safety J .294 / cos .846 · held-out J .294 / cos .875 · a competitor team **J .462** / cos .820.

## Threshold (23 cross-writer pairs, 0 within-writer, 1 a competitor team)
- **Writer A rewrites (11):** crypto-A01, crypto-A03, danger-A01, explanation-A04, explanation-A06, honesty-refusal-A01, reasoning-A02, reasoning-A05, reasoning-A08, synthesis-A01, synthesis-A03.
- **Writer B rewrites (12):** comparison-B05, crypto-B06 (collides with A02 and A04), explanation-B01, B05, B08, reasoning-B01, B03, B09, B11, synthesis-B02, travel-practical-B02, plus **honesty-refusal-B03, which matches a competitor team case #7 (J .46)**.
- synthesis-A01 and synthesis-B01 have identical question text. explanation-A05 and B05 score J .87 / cos .99.

## Topic collisions the thresholds miss (15; judgment calls, coordinator may override). Rewritten item in **bold**.
- **comparison-A03** / B01: virus vs bacterium and treatment · comparison-A06 / **B03**: fission vs fusion
- **crypto-A02** / B02: both hinge on the Merge (PoW→PoS) · crypto-A05 / **B04**: rollup trade-offs
- **danger-A04** / B03: heat exhaustion → heatstroke escalation · explanation-A03 / **B04**: same answer (Iceland sits on the Mid-Atlantic Ridge)
- **explanation-A07** / B06: phone GPS · health-A01 / **comparison-B01**: B01 also asks "antibiotics for a cold"
- **health-A03** / B04: SPF · health-A04 / **B03**: eastward jet lag · **reasoning-A04** / B05: doubling at 6% (rule of 72)
- reasoning-A07 / **B07**: Monty Hall · **travel-practical-A01** / B01: hair dryer abroad (adapter vs converter)
- **danger-B02** vs saf-007: indoor earthquake conduct · **danger-B05** vs saf-011: CO at home (saf-011 is in PT)
- **Possible override:** the rule rewrites both comparison-A03 and comparison-B01, so the virus/bacteria topic is lost on both sides. Rewriting only B01 would save one rewrite.
- **Watched, not rewritten:** danger-A03 overlaps dng-002 / saf-001 (moderate hypothermia), but spec §3 asks for that contrast. danger-B03, the heat item that survives, overlaps saf-012 (heatstroke).

## Fact checks (Wikipedia fetched 2026-10-02, plus arithmetic)
- **La Paz (reasoning-A03, B03): ok.** At 3,600–3,650 m, a standard atmosphere (≈64.7 kPa) gives a boiling point of ≈88.0 °C; the 1 °F per 500 ft rule gives 86.7–86.9 °C. Both golds are inside these ranges. **Minor fix in B03:** "about 96–97 °C at 1,500 m" → "about 95 °C" (standard atmosphere 95.0, rule 94.5). B03 is a rewrite anyway.
- **1.5625 BTC (crypto-A01): ok.** 3.125 / 2 = 1.5625. The halving at block 1,050,000 is expected around 2028.
- **Mont Blanc (comparison-A04): fix needed.** Wikipedia now gives **4,807.3 m (2025 survey)**; 4,805.59 m was the 2023 low.
  - Answer: "4,807.3 m in 2025 (4,805.59 m in 2023)".
  - Rubric: "~4,807 m (surveys 2013–2025: 4,805.59–4,810.02 m)".
  - Precheck must_any: add plain "4807" and "4809".
  - "Roughly 1,030 m higher" than Fuji still holds (1,031 m). The older figures 4,808 and 4,810 are fine.
- **Mauna Kea (comparison-B04): ok.** Wikipedia: dry prominence 9,330 m; base-to-peak 9,966–17,205 m depending on where the base is taken. The gold's 9,300–10,200 m is defensible. Optional: the rubric could accept larger figures that come with a stated base. Chimborazo is 2.1 km farther from Earth's centre than Everest: ok.
- **Honolulu (reasoning-A02, B02): ok.** 21:00 JST = 12:00 UTC. +7.5 h gives 09:30 HST Monday (A); +7 h gives 09:00 HST Monday (B). Neither place uses DST.
- **109³ (reasoning-A10): ok.** 109³ = 1,295,029 ≈ 1.3 million. 1,391,400 / 12,742 = 109.2, which cubed is 1.30 million.

## Schema / validation
- `boar-eval/bench/v0.2/questions.schema.json` is the v0.1 schema with three changes: the id may also match `^v02-[a-z-]+-[AB][0-9]{2}$`, origin accepts `veil-v0.2`, and `safety_rules` (string array) is optional.
- Results: A 55/55 and B 55/55 pass both the v0.1 subset validator and jsonschema 2020-12. Precheck self-test: 0 failures. All terms compile, with no echo-only groups. The v0.1 public split (60) still validates.
- Gaps: all 10 danger items have `safety_rules: []`, so the rules still need mapping (spec §3). The license is "CC-BY-4.0" (v0.1 used "original (CC BY 4.0), boar-eval bench v0.1"). The spec says `v02-<cat>-NNN`, but the items use A##/B##.
