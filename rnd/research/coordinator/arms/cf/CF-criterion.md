# CF (country-facts lookup pack, Wikidata CC0) on cut 3 — frozen 2026-10-04 by the coordinator, before any CF code or data exists

Base: cut 3 (arms/cut3-final-candidate.vs-0cfd4a77.patch a67c70db…). Design: KNOWLEDGE-PACK-SIZING.md §4 (facts block first, one fact per line with units + "Wikidata, <date>"; computed verdict line for two-country numeric comparisons; 4B writes ≤ 2 sentences constrained to the facts; never on health/danger/card/calculator/venue paths; EN only).

## L0 (deterministic, dev only, no judge)
1. Data: ≥ 190 sovereign states. A reviewer subagent checks 30 random rows × 5 fields against live Wikipedia infoboxes: ≥ 98% agreement, 0 errors on capital, currency, plug type.
2. Trigger, on the blind set arms/cf/trigger-set/items.jsonl (written by a blind writer; the builder never opens it; scored once by the coordinator): recall ≥ 90% on positives, false fires ≤ 2/100 on lookalikes. Plus 0 fires on Sonar's 1,328 EN dev messages except true country-slot messages, which the reviewer labels correct.
3. v0.1 + V-exact replay with cut 3 requests: CF fires on ≥ 6 of the 9 target items named in KNOWLEDGE-PACK-SIZING.md and on vx-001; ≤ 3 other v0.1 items change; 0 changes on health, danger, card, calculator or venue items; venues 6/6, GPS city 3/3.
4. ≥ 20 unit tests pass (density ratio, population difference, area rank).
5. Lookup p50 ≤ 5 ms; retrieval p50 ≤ 1.5× cut 3 on the replay.
Stop rule: one revision allowed after a trigger FAIL (new blind set needed); a second FAIL kills CF.

## L1 (v0.1 EN s44 + s45, Android 12 GB 4B profile; control = cut 3 traces + verdicts)
- Byte identity first; judge only changed items with judge.v1-med; reuse control verdicts (cut3-confirm precedent).
- V-exact vx-001 s42 + s43, judge.v1: reported, expectation ≥ +0.10, not a gate.
- ADOPT iff: targeted changed items' mean rubric up ≥ +0.5 on average; no changed item down ≥ 1.0; confident-wrong not up; unsafe 0 (safety v0.9.1); paired 57-item Δ ≥ 0 (CI reported); retrieval p50 ≤ 1.5× cut 3.
- Deviation from the sizing draft, declared before any run: the Δ ≥ +0.02 bar is replaced by per-component gates, following the precedent for deterministic, item-scoped modules (travel-calc, CO card, VG, AR). Forecast Δ +0.005 to +0.012.
