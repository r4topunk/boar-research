# FACTS r3: the FACTS-RECALL fixes, gates re-run

TL;DR: the five fixes named in FACTS-RECALL.md are in, and nothing else. **Recall on the recall set goes 22/40 = 55% → 30/40 = 75%**, below the expected ≥ 80%. **False positives go 2/20 → 0/20**, and precision goes 81.5% → 88.2% (30/34). The 13 probes give 0 fires, and the wider probe list prints exactly what r2 printed. The 8 targets are byte-identical to r2. G3 is unchanged (0/52, 0/12, 0/11, 2/192). G4 is 52/52 and G5 p95 is 0.077 ms. Deterministic only: no network, no LLM, no judge. The asset is unchanged (`f4d3ab2e…`). All r3 work is code in `facts.ts`.

- Commit: wt/facts `45d5d058` (branch coord/facts, on r2 `24cd66ef`). Patch `facts-r3.vs-cut6.patch` sha256 `37e65204260b4c91b000982a019d820aab202b284e913edffdd85f994c0eef7d` (5 files, +596 vs cut 6; r3 alone: 2 files, +162 −16).
- The recall set is no longer blind. It drove these fix categories, and this run scores it after the fixes (sha `414e4de2…`, unchanged). Treat 75% as a dev number.

## Changes (src/rag/facts.ts; the asset is untouched)

| fix | rule as built |
|---|---|
| 1 lowercase | A one-word **label** of a country, or of a city that is some country's capital, resolves when typed lowercase. The opening-word rule stays. Risk list (lowercase never resolves): georgia, turkey, chad, jordan, guinea, chile, china, america, us, wellington, victoria, sofia, israel, santiago, kingston, nice, reading, male, malé. Multi-word names keep the r2 capitalisation rule. A lowercase multi-word table name that contains such a word ("south sudan", "mexico city") makes the question unanswerable, so its inner word cannot answer for it. A lowercase name after north/south/new/latin/… ("new mexico") does not resolve. |
| 2 aliases | Aliases added in code: China → Q148; UK, U.K., the UK, Britain → Q145; US, U.S., USA, the USA, America → Q30; the Amazon → Q3783 (already in the data). A "the X" alias matches when the question types "the" right before X. "Amazon" alone (the company) does not resolve. "US" is a titleCandidates stopword, so the exact upper-case token is added as a candidate. Lowercase is allowed for uk, u.k, britain, usa and u.s, but never for us, america or china. |
| 3 templates | "size of" is an area cue. "bigger/larger/smaller than" and "which is bigger/larger" ask for **area only when no other property is named**: "Is Brazil's population larger than Russia's?" stays a population question. A comparison prints the verdict and both areas. |
| 4 precision | A name glued (whitespace only) to a capitalised word that is not in the table, not a function or question word, and not the opening word, makes the question unanswerable: Paris Hilton, Paris Agreement, London Eye, Michael Jordan, South America, Lake Chad. Exception: Mount/Mt/River/Lake next to an entity of that kind ("Danube River"). Title case ("What Is The Population Of France?") still fires. A stop-phrase list is removed before template matching: area code(s), area of expertise/study/interest/focus/research, capital letter(s)/gains/punishment. |
| 5 population | The ≥ 2020 gate is kept. A figure dated before 2023 now prints "(dated 2021)" instead of "(2021)". The year was already printed, and the source line already said "figure dated YEAR". |

Tests: one r3 block of 5 tests (one per fix). Two r2 assertions updated: the lowercase example is now "turkey" (risk list), and "Is Iceland bigger than Brazil?" now answers with area.

## Gates

| gate | r2 | r3 |
|---|---|---|
| G1 tsc + vitest (full) | 0 errors; 1330/1330 | **0 errors; 1335/1335** (118 files) |
| 13 probes (DATA-REVIEW §2) | 0 fires | **0 fires**. The whole probes output (13 + 39) is identical to r2's (`probes-r3.out.txt`) |
| G2 precheck, 8 targets | 7/8 | **7/8 = 87.5%**. All 8 answers byte-identical to r2: no target prints a population dated before 2023 (`g2-precheck-r3.out.txt`) |
| G3 other v0.1 / safety / V-exact | 0/52, 0/12, 0/11 | **0/52, 0/12, 0/11** |
| G3 dev chat v0–v2 | 2/192 (true-slot) | **2/192**, the same two items. 274/275 answers are byte-identical to r2. The one changed answer is v2-045 Iceland "376,248 (2022)" → "376,248 (dated 2022)" |
| G4 replay, non-target raw vs cut 6 | 52/52 | **52/52**. r3 vs r2 is 60/60 identical, and the 8 targets go fast → instant. Median retrieve ms on non-targets: 118 / 137 / 127 (base / r2 / r3; noise) |
| G5 latency (warm, 5,500 calls) | p50 0.045 / p95 0.066 / p99 0.113 ms | **p50 0.051 / p95 0.077 / p99 0.120 / max 0.697 ms**. Cold first call 82 ms, module load 82 ms |

## Recall set (`tools/recall_score.mts`, frozen FACTS-RECALL rule)

The scorer reproduces r2's numbers exactly on a snapshot of `24cd66ef`: 22/40, 22/27, FP 2/20. Comparison items count as correct only if the verdict names `expect`.

| metric | r2 | r3 |
|---|---|---|
| recall (correct / 40 fact) | 22/40 = 55.0% | **30/40 = 75.0%** |
| fact items fired | 25/40 | 34/40 |
| precision (correct / all fires) | 22/27 = 81.5% | **30/34 = 88.2%** |
| false positives (near-misses) | 2/20 | **0/20** (Paris Hilton and area code fixed) |
| lowercase-typed items correct | 0/10 | 6/10 |

Gains (+8): f05 size of brazil, f14 Canada vs United States (bigger), f21 egypt, f25 peru, f26 Nile vs the Amazon, f33 the uk, f36 argentina, f38 canada.

## Remaining misses (10)

| cause | items |
|---|---|
| lowercase multi-word name, or a lowercase non-country/capital (by the rule) | f11 mont blanc, f16 amazon river, f29 kilimanjaro, f34 danube river |
| stale population (data, not trigger; now printed "(dated YEAR)") | f15 India 1.33 B (dated 2020), f22 Nigeria 211.4 M (dated 2021), f31 Mexico 132.3 M (2024; +3.4%, borderline expect) |
| wrong verdict from stale data | f37 "China or India": the alias now resolves, but India's 2020 figure makes China the winner |
| entity not in table | f18 Eiffel Tower, f39 Mount Fuji |

The 80% bar would need one of these: lowercase acceptance for one-word mountain/river names (Kilimanjaro, Danube), or fresher India and Nigeria populations, which also fixes f37. Both fall outside the five fixes, so neither was done.

UNKNOWN: lowercase person-name homographs of an accepted name still fire, because the glue guard needs capitals. Verified: "how tall is paris hilton" → Paris elevation 48 m. Not measured on a fresh set. The risk list is hand-made, not dictionary-derived (web2 marks brazil, canada and russia as common words, so it is unusable). The precision guard can drop real questions whose name is glued to an unknown capitalised word. Its recall cost on a fresh set is unmeasured. "Paris France" gives no fire: two entities and no comparison.
