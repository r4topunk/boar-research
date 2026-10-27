# CV (computed verdict) on cut 3 — frozen 2026-10-04 by the coordinator, before any CV code, gold key or answer exists

Mechanism: for EN questions whose verdict is computable from numbers (two-entity numeric comparison, numeric/date threshold yes/no, superlative yes/no), the 4B is asked for the facts only in a constrained format (grammar/JSON: entity, quantity, value, unit, year), the engine computes the verdict deterministically and renders "verdict + facts" plus at most 2 model sentences constrained to them (travel-calc pattern). Never on health/danger/card/calculator/venue/CF paths. Abstain (normal path) when parsing fails or units can't be reconciled.

## Dev set and key
- DEV questions: arms/vg-probe-q (compare2 25, threshold 20, rank 20) + arms/vg-probe-q2 (threshold 30, superlative 30, compare2 30) = 155 verdict items; controls (55) for false fires.
- Gold key: a separate labeler writes the correct verdict for each verdict item (checked against Wikipedia), frozen with sha256 BEFORE any CV answer exists. The builder never opens the key.

## L0 (deterministic routing + Mac mini generation; no judge)
- Routing: CV fires on ≥ 80% of the 155 verdict items; 0 fires on the 55 controls; 0 fires on Sonar's 1,328 EN dev messages except true verdict questions (listed).
- Accuracy (scored by the coordinator against the key, verdict only): verdict accuracy of cut 3 + CV ≥ cut 3 + 10 percentage points on the 155 items (cut 3 answers generated once, same seed/config), AND CV produces ≤ 2 verdicts that are wrong where cut 3's were right. Unparseable/abstained items count as cut 3's answer.
- Latency: median added time on the 4B path ≤ +2 s desktop proxy.
## Ship gate (after L0 pass)
- Fresh blind verdict set (≥ 90 items + 30 controls), new gold key, same bars.
- v0.1 EN L1, changed items only (judge.v1-med): no changed item down ≥ 1.0; unsafe 0; confident-wrong not up; paired Δ ≥ 0.
Stop rule: one revision after an L0 FAIL; a second FAIL kills CV.
