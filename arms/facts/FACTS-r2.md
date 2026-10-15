# FACTS r2: DATA-REVIEW §4 gates applied, checks re-run

TL;DR: all four §4 gates are in (data at build time, trigger rule in facts.ts). **The 13 review probes: 13 wrong under r1, 0 fires under r2.** The 8 targets and the 2 chat fires return byte-identical answers. G1–G5 all pass with the same numbers as r1. **The 8-item judge is now safe to run** (caveats at the end). Deterministic only: no network, no LLM, no judge. Criterion `FACTS-criterion.md` sha256 `4328960e…77d63b5`, unchanged. Raw cache `data/raw/` unchanged: the aggregate sha `6b3e7487…` is the same before and after, and the r1 builder still rebuilds r1's `036b0b0b…` byte-for-byte.

- Commit: wt/facts `24cd66ef` (branch coord/facts, on r1 `1bc4ad1f`, on cut 6 `5e5567ca`).
- Patch: `facts-r2.vs-cut6.patch`, sha256 `d8f8142df66ee965d169123dd090addda1426955dc159d052c3ffc529c2572a7` (5 files, +450).
- Asset: `src/rag/facts.v1.json` (same import path), r2 build, 1,036 entities, 248,093 bytes, sha256 `f4d3ab2ef38a44890ef9c73f14c5fb4c92ffa54ad6dcd1094f144d6dc4db4a50`.

## What changed

**Data** (`tools/build_asset.py`, now r2; r1 kept as `tools/build_asset.r1.py`; gate log in `build-r2.gates.log`):

| § 4 gate | rule as built | effect |
|---|---|---|
| 1 dates | `inc`/`end` only for buildings, events, "other" (Berlin Wall). This follows §4's letter ("print inc only for buildings/events"), so cities lose it too, not only countries. Years < 1000 print without a leading zero (facts.ts `date()`). | inc 475 → 62 (countries 197 → 0, cities 214 → 0) |
| 2 population | Rows that are undated, zero, or dated before year 1000 are dropped. The latest remaining row must be dated ≥ 2020; otherwise the entity has no population. | pop 659 → 546 (113 removed: 109 dated < 2020, 4 with no valid dated row). Rows dated < 2020 left: 0 |
| 3 non-existent | A lake, building, river or mountain whose description matches `former\|paleo\|prehistoric\|proposed\|planned\|envisioned\|unbuilt\|under construction` is dropped. Cities are exempt, because "former capital" would drop Saint Petersburg, Lagos, Nanjing and others. | 16 dropped: 8 buildings (X-Seed 4000, Akhmat, Burj Azizi, Bein Arim, Dubai One, Six Senses, Diamond Tower, 80 South St) and 8 lakes (Ptolemy, Mega-Chad, Bonneville, Missoula, South Aral, Tauca, Aral Sea, Tengger) |
| 3 ranges | A value outside the §2 range table is dropped (the entity stays): area ≤ 0 or > 20,000,000 km²; lake area > 400,000; building height > 900 m; elevation > 9,000 m; river length > 7,000 km; Bian River length by hand (§2 "manual"). | 5 values dropped: Taxtakörpü area, Lake Agassiz area, 85 Broad St height, Dubai City Tower height, Bian River length |
| 4 aliases | Lake aliases Michigan, Superior and Huron and the Cape Town alias Cape are removed. A **nickname** is a multi-word alias that does not contain the label and is not contained in it, is not a spelling variant of the label (edit distance ≤ 2), and whose non-stopword tokens are all lowercase dictionary words (`/usr/share/dict/web2`, sha `be41ad97…`). Nicknames are removed. | aliases 3,259 → 3,056 (4 explicit + 186 nicknames + aliases of dropped entities) |

**Trigger** (`src/rag/facts.ts`, +30 lines):
- Every non-stopword of a matched label or alias must be typed capitalised (or start with a digit). Before, only lone words had this check. Now "white house" and "lake baikal" do not resolve.
- If one name maps to ≥ 2 entities after the exact-label rule, the whole question gets no answer. Before, the most populous entity won. In the r2 table this hits 9 same-label pairs: Bandung, Tokyo, Suzhou, Fuzhou, Yulin, Taizhou, and the city-states Luxembourg, San Marino and Djibouti.
- **Beyond §4's letter:** a one-entry `HOMONYMS` set (`georgia`) is also treated as ambiguous, because the US state is not in the table. This applies the spirit of gate 3. Without it, "What is the capital of Georgia?" → Tbilisi would remain the only probe that fires.

**Tests:** `facts.test.ts` gains a 4-test r2 block (one per gate).

## Gates (same scripts as r1)

| gate | r1 | r2 |
|---|---|---|
| G1 tsc + vitest (full suite) | 0 errors; 1326/1326 | **0 errors; 1330/1330** (118 files; +4 r2 tests) |
| G2 precheck, 8 targets | 7/8 | **7/8 = 87.5%** (bar 75%). trv-002 fires but is judge-only. All 8 answers are byte-identical to r1 (`g2-precheck-r2.out.txt`) |
| G3 false fires: other v0.1 | 0/52 | **0/52** |
| G3: safety track | 0/12 | **0/12** (9 EN + 3 PT) |
| G3: V-exact | 0/11 | **0/11** |
| G3: dev chat v0–v2 | 2/192 (true-slot) | **2/192**, the same two true-slot fires with identical text: v2-045 Iceland population 376,248 (2022); v2-054 Andorra → Catalan |
| G4 replay, non-target raw retrieval vs cut 6 | 52/52 | **52/52** identical (raw titles + sections + source, query, k, tier, task, pre-answer sources). r2 vs r1 identical 60/60. The 8 targets go fast → instant. Median retrieve ms on non-targets: 118 → 137 (noise: retrieval code is untouched, and r1 vs r2 traces are identical) |
| G5 latency (warm, 5,500 calls) | p50 0.047 / p95 0.063 / p99 0.104 / max 0.74 ms | **p50 0.045 / p95 0.066 / p99 0.113 / max 0.242 ms**; cold first call 84 ms, module load 168 ms |

Outputs: `facts-check-r2.jsonl` / `.out.txt`, `g2-precheck-r2.out.txt`, `replay-facts-r2.jsonl` / `.summary.txt`, `g4-compare-r2.txt`, `probes-r2.out.txt` (and `probes-r1.out.txt` for contrast), `tools/probe_r2.mts`.

## The 13 probe questions (DATA-REVIEW §2)

| # | question | r1 output (wrong) | r2 output |
|---|---|---|---|
| 1 | How tall is the White House? | Casablanca elevation 115 m | no fire (normal path) |
| 2 | How big is Michigan? | Lake Michigan 57,750 km² | no fire |
| 3 | What's the area of the West Side? | Cape Town 2,455 km² | no fire |
| 4 | How high is the Cape? | Cape Town elevation 5 m | no fire |
| 5 | How long is the Green River? | Colorado River 2,334 km | no fire |
| 6 | How many people live in Garden City? | Singapore 5.9 million | no fire |
| 7 | How high is Snow Peak? | Piton des Neiges 3,070 m | no fire |
| 8 | How tall is Trump Tower? | Chicago tower 423 m | no fire |
| 9 | What is the capital of Georgia? | Tbilisi (ambiguous) | no fire (HOMONYMS) |
| 10 | When was Italy founded? | "built/founded 0476" | no fire |
| 11 | When was the United States founded? | "12 May 1784" | no fire |
| 12 | How long is the Bian River? | 5,806 km | no fire |
| 13 | What is the population of the Netherlands? | 17.1 million (2013) | no fire |

**Wrong answers: 13 → 0.** Wider probe list (39 more, `probes-r2.out.txt`), r2 behaviour:
- Correct fires are kept: Lake Michigan, Lake Superior, Colorado River, Madrid, Rio de Janeiro, Kenya, and Chad vs Jordan by area.
- Ambiguous names now fall through: Bandung, Tokyo, Suzhou, Fuzhou, New York.
- Residual issues outside §4 still fire: "What is the capital of South Africa?" → "Cape Town, Pretoria and Bloemfontein" (grammar); Russia's 36 "official languages"; "Which countries border Iceland?" → Faroe Islands, Greenland, Svalbard (maritime neighbours, not borders). Pakistan's capital list (with Rawalpindi) was not probed.
- "Which language is spoken in Swiss schools?" fires on the alias Swiss and gives Switzerland's four official languages (acceptable).

## Recall cost (trade-off, not measured on a trigger set)

- Same-label pairs no longer answer, for example "population of Tokyo", "of Luxembourg" or "of San Marino".
- Legitimate multi-word aliases that look like plain English are gone: East Timor, Swiss Confederation, Argentine Republic, Rio 2016, Khalifa Tower, 1 World Trade Center.
- Questions typed in lowercase no longer resolve multi-word names.
- Cities have no founding dates.

None of this touches the 8 targets or the 2 chat fires.

## Is the 8-item judge safe to run?

**Yes, as far as these checks can tell.**
- The judge would see exactly r1's 8 answers: byte-identical, and all 8 values were correct in DATA-REVIEW §1.
- The gates remove every probed wrong-answer path.
- G3 still shows no false fires.

Caveats carried over:
- trv-002 still lacks 60 Hz (`hz` is empty table-wide).
- lan-exp-006 answers "is it a volcano?" only through `type: dormant volcano`.
- lan-cmp-001 uses Brazil 214.2 M (2026), about 5% above the gold census figure.
- Multi-capital and border/language list quality is unreviewed.
- There is still no blind trigger set, so recall on fresh phrasings is unknown.

UNKNOWN: whether the dictionary-based nickname rule over-prunes real names in other regions (not measured); whether the coordinator wants cities' founding dates back (§4's letter dropped them; the caller's summary named only countries).
