# LCRELAX probe (2026-10-08 00:13): relaxing "lowercase one-word names = countries/capitals only", per entity kind. Dev only, burnt sets, no LLM.
Code wt/facts branch `probe/lcrelax` 58adf998 (on r6 98db9827; coord/facts untouched). `FACTS_LCRELAX=0..3` selects the variant; risk list,
r5 two-sided neighbour guard and all other r6 rules unchanged. Names = one-word label **plus one-word English aliases** of the relaxed entities
(`FACTS_LCALIAS=1`; needed because Bangalore, Kangchenjunga, Yangtze are aliases, labels Bengaluru/Kanchenjunga/Yangtze River). Scorer v2 unchanged; 6 set sha256 OK.
V1 = + mountain/river/lake/dam · V2 = V1 + city pop ≥ 1 M · V3 = V2 + every kind (all cities, buildings, award/event/other).
| variant | recall s1 | s2 | s3 | s4 | FP s1/s2/s3/s4 near-miss | FP nearmiss-lc | FP nearmiss-lc2 | probes: 13 P13 / 22 r4-fresh |
|---|---|---|---|---|---|---|---|---|
| V0 (r6) | 34/40 | 32/40 | 29/40 | 28/40 | 0/20 0/20 0/20 0/20 | 0/40 | 0/40 | 0 / 1 |
| V1 | 35/40 | 32/40 | 29/40 | 31/40 | 0/20 0/20 0/20 0/20 | 0/40 | 0/40 | 0 / 1 |
| V2 | 35/40 | 32/40 | 30/40 | 32/40 | 0/20 0/20 0/20 0/20 | 0/40 | 0/40 | 0 / 1 |
| V3 | 35/40 | 32/40 | 30/40 | 32/40 | 0/20 0/20 0/20 0/20 | 0/40 | 0/40 | 0 / 1 |
| V1 labels only | 34 | 32 | 29 | 30 | all 0 | 0/40 | 0/40 | 0 / 1 |
| V2/V3 labels only | 34 | 32 | 30 | 30 | all 0 | 0/40 | 0/40 | 0 / 1 |
Precision moves with recall (s4 96.6 → 97.0 %). The 39 wider r2 probes: 12 fires in every variant, output byte-identical to V0. The single
fresh fire is the known r5 one (kuala lumpur tower). Gains: V1 f29 kilimanjaro, r4-f20 aconcagua, r4-f22 kangchenjunga (alias), r4-f28 ganges;
V2 adds r3-f03 istanbul, r4-f14 bangalore (alias). Still missed in V3: houston ("texas" neighbour, rule A), osaka ("teh population of …" frame does not fire),
yangtze ("roughly" opener), zambezi (not in the table at all: the r6-SET4 "all 8 in the table" holds for 7), turkey (risk list).
## New false positives (the cost)
None. 0 new fires on any FP item in any variant. Exposure check: near-miss/probe items (160 near-misses + 22 fresh probes) that contain a
lowercase-typed word newly allowed by the variant: V1 12, V2 26, V3 35 of 182 (labels only: 6 / 15 / 23), e.g. "nile perch", "nile rodgers",
"blue danube waltz", "volga car", "sydney sweeney", "toronto raptors", "boston butt", "denver omelet", "florence pugh", "seville orange".
All 35 are blocked by the r5 neighbour guard, the opener rule or the property/question frame; none reaches an answer.
## Homonym exposure per kind (one-word label = lowercase exact entry in /usr/share/dict/words; risk-list words and r3-allowed entities excluded)
| kind (variant that adds it) | entities with one-word label | label is a dict word | + via a one-word alias | examples |
|---|---|---|---|---|
| mountain (V1) | 279 | 2 | 4 | trisul, tronador |
| river (V1) | 71 | 6 | 15 | don, ket, oka, om, prut, rhine |
| lake (V1) | 15 | 0 | 1 | — |
| dam (V1) | 0 | 0 | 0 | (no one-word labels) |
| city ≥ 1 M (V2) | 412 | 10 | 22 | aba, barcelona, fez, perm, phoenix, rosario, samara, shanghai, siping, van |
| city < 1 M (V3) | 913 | 33 | 61 | ambon, aurora, bari, boston, bursa, florence, fresno, ganja, … |
| building (V3) | 18 | 0 | 0 | — |
| award/event/other (V3) | 0 | 0 | 0 | — |
## UNKNOWN
- FP sets are Claude-written and built against the r3 rule: only 12–35 of 182 items even exercise the new words, so "0 new FP" bounds
  the cost loosely (0/35 ⇒ 95 % upper bound ≈ 8.6 % on exposed items, V3). No fresh blind set for natural-feature or city homonyms exists.
- Dict-word list is a narrow homonym proxy (misses first names/brands: "sydney", "aurora" brand, "jordan"-like cases); real-traffic rate unmeasured.
- Recall sets are burnt dev sets (set 4 seen in r6 analysis); gains are upper bounds on unseen phrasing. tsc/vitest not run on the probe branch
  (default `LC_RELAX=0` is the r6 code path).

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.
