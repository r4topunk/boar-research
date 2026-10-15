# T-K4a — CROWDING probe, 7 wave-1 packs (2026-10-12; 0 LLM, 0 judge, MacBook)
TL;DR: no single pack crowds (share 0.03–0.32 ≤ 0.40), but travel/ethereum/bitcoin SE displace kit gold → **default-eligible: qa-health-se, qa-outdoors-se, boar-firstaid-en, boar-medlineplus-en; user-selected only: qa-travel-se, qa-ethereum-se, qa-bitcoin-se, and the 5 SE together** (share 0.48 on v0.2). Rerun: `arms/packs/tools/crowding.sh` (≈ 12 min).
## Method
- Replay `tools/replay-crowd.ts` = packcond `replay-pg.ts` + per-slot `pack` (chunkId prefix). `--deep --gate rules --k 6 --pool 20 --tree wt/packs`, `BOAR_REPLAY_CACHE=arms/deepcovfb/cache`; v0.2 110 items `--tasks-from` dt512 s42 traces (outputs in $HELDOUT_DIR/bench-v02/runs-packs/), v0.1 public 60 (arms/packs/replay/). Kit = boar-crypto + boar-wikivoyage-en; each run = kit + 1 pack as peer, plus kit + 5 SE packs (se5).
- Baseline check: wt/packs vs wt/packcond raw and kept identical 60/60 (v0.1) and 110/110 (v0.2); v0.2 raw = dt512 traces 110/110.
- Share = pack kept slots / all kept slots (all items). Gold = replay-pg goldMatch (p4_diag normalisation), restricted to gold whose article resolves in the kit packs (v0.2: 35 strings, v0.1: 22); counts = gold strings hit, summed. "Gold not lower" = raw6 and kept counts ≥ baseline. Verdict needs both sets. Aggregation `tools/crowding_agg.py` → `aggregates/crowding.json` (counts/ids only).

## v0.2 (110; 107 retrieve) — base: kept 136, gold raw6/kept 18/15, empty 50, p50 169 ms
| pack | share kept | items ≥1 | gold raw6/kept | items gold↓ | empty | changed | p50 ms |
|---|---|---|---|---|---|---|---|
| qa-travel-se | 0.316 (48/152) | 20 | 13/11 | 4 | 48 | 26 | 206 |
| qa-ethereum-se | 0.110 (15/136) | 8 | 14/12 | 4 | 50 | 9 | 200 |
| qa-bitcoin-se | 0.146 (21/144) | 9 | 14/12 | 4 | 48 | 14 | 200 |
| qa-health-se | 0.108 (16/148) | 7 | 18/15 | 0 | 45 | 11 | 187 |
| qa-outdoors-se | 0.116 (17/146) | 11 | 18/15 | 0 | 48 | 12 | 172 |
| boar-firstaid-en | 0.101 (15/148) | 7 | 18/15 | 0 | 45 | 9 | 302 |
| boar-medlineplus-en | 0.043 (6/138) | 4 | 18/15 | 0 | 48 | 6 | 178 |
| 5 SE together | 0.479 (78/163) | 32 | 9/8 | 8 | 46 | 40 | 314 |

## v0.1 public (60; 54 retrieve) — base: kept 111, gold raw6/kept 16/14, empty 15, p50 140 ms
| pack | share kept | items ≥1 | gold raw6/kept | items gold↓ | empty | changed | p50 ms |
|---|---|---|---|---|---|---|---|
| qa-travel-se | 0.196 (20/102) | 11 | 11/9 | 4 | 15 | 15 | 165 |
| qa-ethereum-se | 0.088 (10/114) | 4 | 16/15 | 0 | 15 | 8 | 158 |
| qa-bitcoin-se | 0.079 (8/101) | 4 | 15/13 | 1 | 15 | 9 | 160 |
| qa-health-se | 0.061 (7/115) | 6 | 16/14 | 0 | 13 | 6 | 160 |
| qa-outdoors-se | 0.046 (5/109) | 5 | 16/14 | 0 | 15 | 8 | 134 |
| boar-firstaid-en | 0.060 (7/116) | 5 | 16/14 | 0 | 14 | 5 | 217 |
| boar-medlineplus-en | 0.026 (3/114) | 2 | 16/14 | 0 | 15 | 2 | 129 |
| 5 SE together | 0.340 (34/100) | 16 | 11/9 | 4 | 15 | 24 | 291 |

## Where the slots go (pack slots / kept slots; in = matching category, out = the rest)
| pack (matching) | v0.2 in | v0.2 out | v0.1 in | v0.1 out |
|---|---|---|---|---|
| qa-travel-se (travel-*, local-food) | 9/13 | **39/139** (17 items) | 1/8 | **19/94** (10 items) |
| qa-ethereum-se (crypto) | 13/19 | 2/117 | 5/30 | 5/84 |
| qa-bitcoin-se (crypto) | 18/30 | 3/114 | 3/25 | 5/76 |
| qa-health-se (health, danger*) | 14/20 | 2/128 | 5/13 | 2/102 |
| qa-outdoors-se (danger*, travel-practical) | 0/6 | 17/140 | 1/12 | 4/97 |
| 5 SE together | 39/53 | 39/110 | 14/44 | 20/56 |

## Reading
- Travel SE crowds where it does not belong: 81 % of its v0.2 slots sit on non-travel items, and it takes kit gold on 4+4 items. Ethereum/bitcoin SE stay on crypto items but displace the kit's gold there (the same 4 v0.2 crypto items for both; bitcoin also 1 v0.1 item): in-topic, so the loss is in the target category itself.
- Outdoors SE takes 0 slots on its matching v0.2 items and 17 elsewhere; it passes the rule but brings no in-topic content on these sets.
- Health SE, first aid, MedlinePlus: in-topic, small share, 0 gold lost. First aid costs +130/+77 ms p50 (v0.2/v0.1).
- Multi-pack (D4): the 5 SE packs together exceed 0.40 on v0.2 and lose gold on 8 items → SE packs are not to be enabled as a bundle by default.

## Caveats
- Retrieval only: a displaced gold slot is not a measured answer loss, and a pack slot may hold the fact (no F0 here; coverage = T-K4 jev probe). Gold sets are Wikipedia/Wikivoyage-titled, so the "not lower" test is one-sided against non-Wikipedia packs. v0.2 is dev (burnt); small counts (35/22 resolvable gold strings). Only the first retrieve call per item.
- Blind hygiene: two stderr lines of the v0.2 bitcoin/se5 runs (ref mismatch log, in the scratchpad log only) showed retrieved Stack Exchange post titles (pack titles, not item text); nothing from them was written here.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.
