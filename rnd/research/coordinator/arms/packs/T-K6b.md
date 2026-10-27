# T-K6b — CROWDING + V-para COVERAGE, 2 wave-2 packs (2026-10-13; 0 Claude, jev [usage detail removed], MacBook)
TL;DR: **boar-simplewiki-en = user-selected only** (share 0.83/0.71, kit gold displaced on 9/13 items: the DEEPWIKI failure mode). **boar-factbook = passes the frozen rule as implemented** (share 0.11/0.20, gold counts up) **but loses kit-slot gold on 1+3 items** → recommend user-selected only until a quality check. Coverage: factbook 1/34 verified (vpara-002, "Japan"), simplewiki 0/34 (one 0.74 lead); 9-pack union 2/34 verified, + kit 6/34 (was 5).
Method: wave-1 tooling unchanged except `crowding.sh --wave2` / `crowding_agg.py --wave2` (pack list + MATCH rows; T-K4a baselines reused, same tree wt/packs, which has source codes 11/12) and the coverage runner called per pack (CAPC 20, TOPK 20).
## Crowding (deep, k 6, pool 20, gate rules; kit + pack as peer)
| set | pack | share kept | items ≥1 | gold raw6/kept (all slots) | kit-slot gold raw6/kept | items gold↓ (kit-slot) | empty | changed | p50 ms |
|---|---|---|---|---|---|---|---|---|---|
| v0.2 base | — | — | — | 18/15 | 18/15 | — | 50 | — | 169 |
| v0.2 | factbook | 0.107 (15/140) | 11 | 20/17 | 17/14 | 0 (1) | 48 | 12 | 201 |
| v0.2 | simplewiki | **0.829** (218/263) | 75 | 29/25 | **10/8** | 4 (9) | 24 | 80 | 175 |
| v0.1 base | — | — | — | 16/14 | 16/14 | — | 15 | — | 140 |
| v0.1 | factbook | 0.200 (24/120) | 10 | 18/16 | **12/10** | 1 (3) | 14 | 10 | 134 |
| v0.1 | simplewiki | **0.714** (95/133) | 38 | 20/16 | **5/3** | 3 (13) | 8 | 39 | 147 |
- "All slots" = the T-K4a aggregator: a pack slot counts as gold when its bare title equals the gold title. Factbook country pages and Simple Wikipedia articles share titles with the kit's Wikivoyage/Wikipedia gold, so that column is inflated for these two packs (it was not for wave-1, whose titles never collide). The kit-slot column counts kit (crypto/wikivoyage) slots only.
- Simplewiki slots by category, pack/kept (items ≥1 / n), v0.2: explanation 55/67 (20/21), comparison 38/44 (12/13), reasoning 39/39 (11/21), honesty-refusal 30/32 (10/12), crypto 15/26 (6/13), health 15/18, synthesis 15/19, travel-local 6/8, danger 3/5, travel-practical 2/5. v0.1: explanation 29/30, comparison 21/24, reasoning 15/20, honesty-refusal 7/9, health 6/7, crypto 4/20, travel-practical 5/7. Slots everywhere, including crypto and refusal items; it also empties fewer kept lists (50→24, 15→8), i.e. it fills gaps where the kit had nothing on-topic.
- Factbook on comparison/reasoning: v0.2 comparison 2/25 (2 items), reasoning 5/9 (2); v0.1 comparison 9/17 (3), reasoning 1/12 (1). Rest: explanation 5/46 + 11/26, travel-practical 2/3 + 1/7, health 1/6, honesty-refusal 0 + 2/12, crypto 0. In-category (comparison/reasoning/travel) 9/44 v0.2, 11/40 v0.1.
- Verdict (frozen rule: share ≤ 0.40 and kit gold not lower, both sets): simplewiki fails on share alone. Factbook passes as implemented (aggregate `verdict`), fails on the literal "kit's gold" reading (v0.1 −4/−4). Coordinator call; default suggestion: user-selected only.
## Coverage (V-para 34 absent items, jev fact-in-text, 20 candidate chunks/item, arm H s42)
| pack | ≥0.6 | ≥0.7 | verified | on / off / no-kept (verified) | jev $ |
|---|---|---|---|---|---|
| boar-factbook | 3 (vpara-001 0.65, 002 0.91, 035 0.60) | 1 | 1 (vpara-002, explanation, "Japan") | 1 / 0 / 0 | 0.0223 |
| boar-simplewiki-en | 2 (vpara-001 0.60, 002 0.74) | 1 | 0 | 0 / 0 / 0 | 0.0204 |
| union 9 packs | — | 3 | **2** (travel-practical 1, explanation 1) | 2 / 0 / 0 | 0.191 |
| union 9 + kit (P1 F0) | — | — | **6** | 5 / 0 / 1 | — |
By category, wave-2: explanation 1 verified (factbook); comparison/crypto/reasoning/synthesis/travel 0. The 20 no-kept items: 0 hits ≥ 0.7 from any pack. Simplewiki's only lead is the item factbook verifies.
Spend: jev [usage detail removed] (factbook 0.0223, simplewiki 0.0204); balance 0.591 → 0.569 → 0.549 (≥ 0.50 held). Crowding 0 LLM, ≈ 9 min.
Outputs: aggregates/crowding-wave2.json (+ `kit_slot_gold`), coverage-vpara-boar-factbook.json, coverage-vpara-boar-simplewiki-en.json, coverage-vpara-union.json (now 9 packs). Replays: replay/v01-boar-*.jsonl, blind/bench-v02/runs-packs/v02-boar-*.jsonl.
Caveats: retrieval only (no answers judged); gold is Wikipedia/Wikivoyage-titled and title collisions make the all-slots gold test meaningless for these two packs; small counts (35/22 resolvable gold strings); v0.2 dev (burnt), V-para dev-style; coverage recall-limited to 20 chunks per pack and quote_supports is a jev proxy. Blind files read script-only; only ids/titles/probabilities/counts seen.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.
