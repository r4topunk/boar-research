# NUMCHECK (B6) 0-call gate — 2026-10-12: **FAIL** (coverage 0/16 V-para, 0/17 v0.2; 1 false rewrite on 20 correct V-para answers)
Tool `tools/numcheck_gate.py` (jev typesafe-ai/jev, 0 Claude; threshold 0.6). Arm H s42 (dt512 + think), wrong-primary ids from `arms/lossmap/aggregates/lossmap-H-{set}-s42.json`. Script-only on blind; caches under `blind/<set>/runs-dt512*/numcheck-cache/`. Outputs `aggregates/numcheck-gate-{vpara,v02}.json` (ids, labels, probs, row keys). jev cost [usage detail removed] total (incl. one superseded run), 0 failures.

## Table (FACTS r6, `wt/cut7/src/rag/facts.v1.json`, sha 92d64c02…, snapshot 2026-10-06, CC0)
- 4,233 entities: city 1,833, mountain 1,183, building/tower 452, river 286, country 197, lake 185, dam 94, + 3 singletons (Nobel Literature, Rio 2016, Berlin Wall).
- Schema per entity (label, aliases, kind, description) + properties: pop [value, year] (1,406), area km² (2,039), elev (2,779), height (544), len (286), depth (124), inc/end dates (434/3), country-only cap/cur/lang/cont/bord/plug/volt (≈ 195), ctry (3,981). Only `pop` carries an "as of" year; everything else is "as of snapshot".
- Domain = static geography + structures. No economy, crypto, health, price, science or event-date properties. Question-side matcher (facts.ts): label/alias n-gram + one FACT_LEXICON property template + VETO list.

## Part 1 — coverage (state = 2 Opus rationales + answer + ≤ 20 candidate rows whose entity label/alias ≥ 4 chars appears in answer or rationales)
| set | wrong items | items with any candidate row | wrong_is_numeric_or_date ≥ 0.6 | table_covers ≥ 0.6 | max p(table_covers) |
|---|---|---|---|---|---|
| V-para | 16 | 5 | 6 | **0** | 0.18 |
| v0.2 | 17 | 10 | 7 | **0** | 0.26 |
`which_row` = "none" on all 33. Gate needs ≥ 4/16: structurally impossible already (11/16 V-para items name no table entity at all).

## Part 2 — answer-side matcher (no gateway): entity label/alias in sentence + numeric-property keyword + a number in that sentence none of which is within 10 % of the table value (metric or imperial; years ±1)
- V-para top-20 non-wrong by ratio (min ratio 0.571): **1 rewrite** (1 item, keys Q1490:pop + Q7473516:pop, two Tokyo entities; likely city-vs-metro scope, answer text not read). Gate needs 0 → FAIL on this clause too.
- v0.2 top-20 (min ratio 0.767): 3 rewrites (Q1867:elev + Q83101:height = Taipei / Taipei 101; Q145:area + Q408:area = UK / Australia; Q131230:elev + Q14081:elev = Mauna Kea / Chimborazo; all on absent_knowledge-primary items, likely scope/definition mismatches such as base-to-peak or distance-from-centre framings, answer text not read).
- Reach: the matcher fires on 0/16 V-para and 0/17 v0.2 wrong items. Hits 0, false rewrites 4 across 40 correct answers.

## What table would be needed (faulted_kind over the numeric-wrong items, jev choice; categories only)
- V-para (6): national statistic 2, computed result 2, crypto protocol parameter 1, health dose/threshold 1. Item categories: explanation 3, crypto 1, reasoning 1, travel-practical 1.
- v0.2 (7): historical/release date 3, science constant 2, computed result 2. Categories: reasoning 4, explanation 2, honesty-refusal 1.
- None of the 13 is a geo attribute (the only thing the table holds). ≈ 4/13 are arithmetic the answer performed (a lookup table cannot fix those; a calculator/recheck path could). The rest would need: a dated country-statistics table (GDP/inflation/rates, World Bank/IMF-style, with "as of" years), an Ethereum/crypto protocol-parameter + upgrade-date table, a dosing/threshold table (health, high risk), a historical event/release-date table and a physical-constants table — five new tables for ≤ 2 items each, on a set where the gate bar is 4.
- Reading: the answer-side FACTS line is closed with the current table (0 coverage, nonzero false rewrites). The numeric share of the wrong bucket is real (6/16 V-para by this stricter "wrong, not missing" wording vs T1's 9/16 numeric-or-date incl. missing), but it is spread over domains the Wikidata geo table does not hold.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file; the gate is stated only with the result (no pre-registration).
