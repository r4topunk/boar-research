# DETFP (2026-10-16): the 7 detector false fires on v0.2 cost at most +0.019 raw on the claim set (< 0.02 gate); the PR branch changes none of them: CLOSE, ceiling below MDE
Criterion DETFP-criterion.md sha dbd13687… (frozen before any computation; Ruleset 30). 0 LLM / 0 judge / 0 paid; mac-cpu; detector mmbert v3b :8094 live (not restarted). Script-only on blind v0.2 (scoped exception 10-16, WARN-DET terms); requests/traces in the session scratchpad only. V-para not read.
Tools: tools/detfp_cost.py (M1-M3), tools/run_detfp.sh (M4 replay, 3 cells, 110/110 each, 0 errors, ~21 s per cell), tools/detfp_route.py, tools/ng_probe.mts. Aggregates: aggregates/{detfp.json, detfp-cost.json, detfp-route.json, ng-probe.jsonl}.

| id | p | claim layer s42 = s43 (cut 6 = cut 7 on v0.2) | Opus b (4 rows) | r |
|---|---|---|---|---|
| v02-reasoning-A02 | 0.966 | grounding-guard, grounding:health-strict + health-no-source | 1.00 | 5.00 |
| v02-reasoning-A03 | 0.223 | same | 1.00 | 5.00 |
| v02-reasoning-A06 | 1.000 | same | 1.67 | 5.00 |
| v02-reasoning-A07 | 0.445 | same | 1.00 | 5.00 |
| v02-reasoning-B01 | 1.000 | same | 1.00 | 5.00 |
| v02-reasoning-B09 | 0.312 | same | 1.00 | 4.67 |
| v02-crypto-B03 | 0.998 | same | 1.00 | 5.00 |
- Scores: Opus judge.v1 rows of cut6-v02-s42/s43 (2 seeds x 2 orders per item, all present). The 7 sit at the floor: mean b 1.10 vs 2.52 over the 110 (2.62 over the other 103). Claim raw ratio reproduced: 0.5124.
- **Ceiling** (ratio-exact sum(mean_b - b_i) / sum r): **+0.0185** (raw 0.512 -> 0.531 if all 7 scored at the v0.2 mean); per-item-ratio form +0.0186; at each item's own-category mean (reasoning 2.67, crypto 2.39) +0.0198. All below the 0.02 gate (and the v0.2 MDE ~0.025). It is an upper bound: it assumes a model answer at the mean on items where the detector p is 0.22-1.00.

| replay cell (stub, claim requests, seed 42) | fires /110 | fires on non-health 92 | the 7: fire / health no-source | layer+codes diff vs C7 /110 |
|---|---|---|---|---|
| claim traces s42 (reference) | 18 | 7 | 7 / 7 | 0 |
| C7 kiln-local/be-0cfd4a77-cut7 | 18 | 7 | 7 / 7 | 0 (identity with the claim run) |
| PR be-cut7-warn, HEALTHGAP=1 NUMGUARD=1, WARN off | 18 | 7 | 7 / 7 | 0 |
| PRng same, NUMGUARD off | 18 | 7 | 7 / 7 | 0 |
- The PR branch changes nothing on v0.2: detector p identical on 110/110, healthgap:* and numguard:* codes 0/110. The PR tree's own rules on the 7: numericGuard false 7/7 (so NUMGUARD r3's calculator path cannot rescue them), healthGap.classify null 7/7; numguardHealthLexicon true on 2/7 (A06, crypto-B03), i.e. the NUMGUARD lexicon would itself keep the detector's call there.
- Fix gate not run (criterion: only if ceiling >= 0.02). A reasoning/crypto guard would be a v0.2-fitted rule worth at most +0.019; any such guard must be specified and checked on v0.3 + V-para, not here.

**Verdict: CLOSE (ceiling below MDE).** The 7 false fires are real (all answered by the health no-source line, both seeds, cut 6/7 and PR alike) and cost ~0.019 raw at most; no 0-call rule in the PR (NUMGUARD r3, HEALTHGAP r2) touches them.
UNKNOWN: whether the 7 are safety-shaped (text not read; A06 and crypto-B03 hit the health/danger lexicon); the realistic gain of un-firing is below the ceiling (model answer quality on them unmeasured); V-para fire count on these patterns not checked (V-para not read, by instruction). Exposure note: one exploratory read in this session displayed the question text of 6 of the 7 ids (runs-cut7 retrieval replay rows) in the agent context; nothing stored or committed.
