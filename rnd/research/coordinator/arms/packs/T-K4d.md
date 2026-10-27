# T-K4d: COVERAGE probe of the 7 wave-1 packs on V-para (2026-10-12; jev [usage detail removed], 0 Claude)
TL;DR: the wave-1 packs cover **1/34** V-para absent-knowledge items (verified; qa-travel-se, travel-practical, on-topic group); 2/34 at p >= 0.7. With the installed kit (P1 F0): **5/34** (kit alone 4/34). Six of seven packs cover 0 items. Packs do not move the V-para conditional subset; consistent with P1/P2 (6/51 kit, 10/51 every pack then on disk) and WIKIFULL.

Method: tools/coverage_vpara.py = wrapper around arms/wikifull/tools/wikifull_gate.py (unchanged logic: q1 12-term OR + q2 kept-title/4-term AND, idf rescoring, jev has_fact, quote_supports on p >= 0.7), pack passed as the gate "shard", TOPK 20, **CAPC 20**. Items = the 34 absent_knowledge-primary items of arm H s42 (LOSSMAP groups 13 on-topic kept / 1 off-topic kept / 20 no kept). Cache blind/V-para/runs-dt512/packs-cache/<pack>/. Runner tools/run_coverage_vpara.sh (spend/balance guards), log tools/coverage_vpara.log. Outputs aggregates/coverage-vpara-<pack>.json + coverage-vpara-union.json (ids/titles/probabilities/counts only).

| pack | >= 0.6 | >= 0.7 | verified @0.7 | on / off / no-kept (verified) | jev $ | s |
|---|---|---|---|---|---|---|
| qa-travel-se | 3 | 1 | 1 | 1 / 0 / 0 | 0.021 | 42 |
| qa-ethereum-se | 0 | 0 | 0 | 0 / 0 / 0 | 0.022 | 40 |
| qa-bitcoin-se | 1 | 1 | 0 (quote 0.61) | 0 / 0 / 0 | 0.021 | 43 |
| qa-health-se | 0 | 0 | 0 | 0 / 0 / 0 | 0.021 | 43 |
| qa-outdoors-se | 0 | 0 | 0 | 0 / 0 / 0 | 0.021 | 42 |
| boar-firstaid-en | 0 | 0 | 0 | 0 / 0 / 0 | 0.021 | 39 |
| boar-medlineplus-en | 0 | 0 | 0 | 0 / 0 / 0 | 0.022 | 40 |
| **union 7 packs** | 4 | 2 | **1** | 1 / 0 / 0 | 0.149 | 289 |
| **union 7 + kit (P1 F0)** | - | - | **5** | 4 / 0 / 1 | - | - |

All >= 0.6 hits sit in the on-topic-kept group (vpara-045 bitcoin 0.70 unverified; vpara-051/054/055 travel, 054 verified across 8 voltage/adapter threads). The 20 no-kept items (where the loss is largest) get 0 hits from any pack.

Per category (n of the 34; 7-pack verified / >= 0.7 / kit / 7 + kit):
| category | n | 7 packs verified | >= 0.7 | kit | 7 + kit |
|---|---|---|---|---|---|
| comparison | 3 | 0 | 0 | 0 | 0 |
| crypto | 2 | 0 | 0 | 2 | 2 |
| explanation | 12 | 0 | 0 | 0 | 0 |
| reasoning | 5 | 0 | 1 (bitcoin) | 1 | 1 |
| synthesis | 5 | 0 | 0 | 0 | 0 |
| travel-local | 3 | 0 | 0 (travel 0.60) | 0 | 0 |
| travel-practical | 4 | 1 (travel) | 1 | 1 | 2 |
Pack -> category: qa-travel-se = travel-practical (1 verified) + travel-local (0.60 lead); qa-bitcoin-se = one reasoning lead; ethereum/health/outdoors/firstaid/medlineplus = none (V-para has no health/outdoors category; crypto items are already covered by the kit).

Spend: jev [usage detail removed] (4,769 uncached requests incl. verify; 0 cached), wall ≈ 5 min. Gateway balance 0.954 -> 0.684 over the window (includes WIKIFULL stage A shard 14 running concurrently, [usage detail removed]); >= [usage detail removed] held.
Caveats: recall-limited by a 20-chunk pool per pack (CAPC 20 vs 40 in P2/WIKIFULL); quote_supports is a jev proxy, not a verbatim check; kit column is P1 F0 (answer-support mode on ratio >= 0.75 items), not the same probe; 1 seed, arm H s42; V-para is dev-style after 10-06 (EXPOSURES ruling). Blind files read script-only; only ids/titles/probabilities/counts printed.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.
