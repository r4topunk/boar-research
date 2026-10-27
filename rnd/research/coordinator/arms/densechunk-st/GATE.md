# DENSECHUNK-ST step 0 gate — **FAIL at step 0 on G2** (G1 and G3 PASS) (2026-10-13 11:1x; criterion sha 24793013…; 0 judge calls, 0 paid)

| gate | rule | OFF → ON | verdict |
|---|---|---|---|
| G1 reach (180 self-test items) | fact chunk in raw top-6 ≥ +25 % relative (≥ 84) AND fact article in kept not lower | chunk 67 → **95** (+42 %); article kept 68 → **95**; article in raw6 107 → 149; chunk kept 43 → 58 | **PASS** |
| G2 no-harm, v0.1 public (60; 39 gold) | gold-in-kept not lower; empty-kept not up | gold raw6 13 → 17, gold kept 12 → 15; **empty-kept 11 → 13**; churn raw 42 / kept 27 | FAIL (empty-kept +2) |
| G2 no-harm, v0.2 resolvable gold (9 items of 110) | gold raw6/kept not lower; empty-kept not up | gold raw6 **6 → 5**, gold kept 4 → 5; **empty-kept 28 → 30**; churn raw 100 / kept 50 (all 86 gold, descriptive: raw6 18 → 23, kept 15 → 21) | FAIL (raw6 −1; empty-kept +2) |
| G3 cost | retrieval p50 ≤ 2 × OFF; scan ≤ 300 ms on simplewiki | p50 ON 308 ms vs OFF 192–242 ms (×1.61); simplewiki two-stage scan p50 103 ms, p95 162 ms (first load 462 ms); SE packs 24–27 ms | **PASS** |

Identity checks: OFF vs the T-K2 tree on the published files identical 60/60 and 110/110; OFF vs OFF2 (second pass) identical.
Per pack (fact chunk in raw6 OFF → ON; fact article kept OFF → ON): travel 8 → 10 / 6 → 11; ethereum 3 → 5 / 5 → 9; bitcoin 1 → 5 / 2 → 8; health 4 → 8 / 5 → 9; outdoors 8 → 9 / 10 → 13; firstaid 1 → 8 / 3 → 5; medlineplus 14 → 18 / 11 → 11; factbook 13 → 16 / 13 → 15; simplewiki 15 → 16 / 13 → 14. Self-test empty-kept 48 → 44.

Reading: the two-stage chunk path reaches the fact passage far more often (the largest retrieval effect measured on this line) and improves every gold measure except one resolvable v0.2 item, but it raises empty-kept by 2 per set: dense candidates that fail the grounding rules (onTopic needs a title term or coverage ≥ 0.75) can displace a lexical hit that would have survived, leaving the context empty. Under the frozen rule this is FAIL at step 0. The mechanism is specific and fixable by construction (never displace the OFF list: add dense hits as extra slots) → DENSECHUNK-ST2 criterion.
