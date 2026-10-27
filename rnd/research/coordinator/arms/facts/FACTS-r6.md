# FACTS r6 (2026-10-06): asset coverage expansion + 5 trigger fixes. All gates green; nearmiss-lc2 FP 0/40. Set 4 not run (coordinator).
- Commit: wt/facts `98db9827` (branch coord/facts, on r5 `802c28bb`). 3 files (facts.ts, facts.test.ts, facts.v1.json).
- Patch `facts-r6.vs-cut6.patch` (base `5e5567ca` = cut 6, same as r3/r5), 819,676 bytes (asset inside, one line),
  sha256 `0eee6a0bf1f73e9ca939c915e06c26c2d5c8804b2462bee36a67b551cd3ae995`.
- Asset `src/rag/facts.v1.json` (same import path), build "r6": **4,233 entities, 760,970 bytes** (≤ 1.5 MB),
  sha256 `92d64c02f7cdf2dc5c61b9d73377d0aec45a8187defa3d911d50d39b79d61598`; r5 was 1,036 / 248,093 / f4d3ab2e….
- Criterion FACTS-r6-criterion.md sha `60027d01…` (verified). Network: query.wikidata.org only, via fetch_wikidata.q() (generic UA, 1 req/min):
  8 selections + 30 property queries (`*_r6*` in data/raw) + 5 homonym queries. No LLM, no judge.

| class | r5 | r6 | selection (build takes top N whose selection value passes the r2 range table; r2 selection kept) |
|---|---|---|---|
| city | 463 | 1,833 | all with population ≥ 300k (r1 class list) + capitals |
| mountain | 100 | 1,183 | 500 highest by elevation + all prominence ≥ 1,500 m (P31/P279? mountain) |
| building (incl. towers) | 82 | 452 | 300 tallest skyscrapers + 300 tallest towers (only 235 towers > 150 m) |
| river / lake | 100 / 91 | 286 / 185 | 300 longest / 200 largest |
| dam (new kind) | 0 | 94 | 100 highest dams (P31/P279* Q12323) |
| country / award / event / other | 197 / 1 / 1 / 1 | same | unchanged |
r2 gates unchanged (pop dated ≥ 2020, no country/city dates, former/unbuilt dropped incl. dams, ranges + dam ≤ 350 m, nickname aliases, no hand aliases).
r5 entities: none dropped; values identical except `ctry` (gate a) on 35. Cold load: JSON 5 ms + module 19 ms + first call 88 ms = 107 ms (r5 98 ms) ≤ 250.

## Data review (DATA-REVIEW-r6.md)
Seed 46 (first candidate): 4/60 flags (Gwangju, Toyota, The One = label of a more prominent item; Dykh-Tau = dissolved states in ctry) → gates:
(a) ctry keeps current table countries; (b) new entity dropped if another Wikidata item with the same English label has more sitelinks (150 dropped);
rebuild. Seed 47 (rebuilt): **1/60** (Migdal Haemek water tower 297 m) → gate (c) water-tower height > 200 m dropped (1 value). Bar ≤ 2: PASS.

## Trigger fixes as implemented (src/rag/facts.ts; r5 guard rules untouched)
1. Opening word whta/waht/wat → what, hwo → how, whats' → whats (replaced before every check).
2. `^(official languages?|continent) of` is a question without "?".
3. "what/which continent is X in/on" with X a place: its P17 countries that are table countries must be exactly one, on exactly one continent
   → "Nairobi is in Kenya, which is in Africa." (Paris/Cairo: no answer, France/Egypt span continents).
4. `^(what|which) (country|countries) surround(s)` is read as "… border" (then the normal borders path).
5. "which/what (one) is taller/higher, X or Y" and "is X taller/higher than Y": each side (optional "the") must be, case-folded, the label/alias of
   exactly one entity, both mountains or both building/dam → compare heights (lowercase one-word mountains work only inside this frame).
Tests: r6 block of 5 `it`s, 23 assertions (incl. set-3 misses rephrased); r3 "Lake Chad" assertion now expects the lake (Q125309), not null.

## Gates
| gate | r5 | r6 |
|---|---|---|
| G1 tsc + full vitest | 0; 1341/1341 | **0; 1346/1346** (118 files) `g1-r6.out.txt` |
| 13 DATA-REVIEW probes | 0 fires | **0 fires, P13 block identical to r3**; wider list: Red River no longer fires (2 Red Rivers → ambiguous) `probes-r6.out.txt` |
| r4 fresh probes (22) | 1/22 | **1/22** (kuala lumpur tower only) `probes-r6-fresh.txt` |
| nearmiss-lc (dev, 40) | FP 0/40 | **FP 0/40** `nearmiss-lc-r6.out.txt` |
| G2 precheck | 7/8 | **7/8, output identical to r5** `g2-precheck-r6.out.txt` |
| G3 other v0.1 / safety / V-exact / dev chat | 0/52, 0/12, 0/11, 2/192 | **0/52, 0/12, 0/11, 2/192 same items; facts-check-r6.jsonl identical to r5 275/275**; no new TRUE-slot fires |
| G4 replay non-target vs cut 6 | 52/52 | **52/52**; r6 vs r5 60/60; median ms 118/122/112 `g4-compare-r6.txt` |
| G5 warm (5,500 calls) | p95 0.085 ms | **p50 0.052 / p95 0.082 / p99 0.135 / max 0.331 ms**; cold 107 ms `g5-cold-r6.txt` |

## Dev sets (scorer v2)
| set | r5 recall / prec / FP | r6 recall / prec / FP | changed items |
|---|---|---|---|
| set 1 | 33/40 = 82.5 % / 89.2 % / 0/20 | **34/40 = 85.0 % / 89.5 % / 0/20** | +f18 Eiffel Tower |
| set 2 | 31/40 = 77.5 % / 93.9 % / 0/20 | **32/40 = 80.0 % / 94.1 % / 0/20** | +r2-f20 Rhine |
| set 3 | 24/40 = 60.0 % / 88.9 % / 0/20 | **29/40 = 72.5 % / 90.6 % / 0/20** | +f14 Denver, f27 official language, f30 nairobi, f32 surrounds, f39 empire/chrysler |
No item lost. Set-3 misses left (11): data value 3 (Berlin, Seoul, Mekong); not in the asset 4 (Matterhorn: prominence 1,042 m and < top-500
elevation; Hoover Dam not in the dam selection; Thames, Seine below the top-300 river cut of 900 km); lowercase one-word non-capital 2 (istanbul, rhine); 2 entities without
a comparison (Shard + London); "Everest" is not a Wikidata alias of Mount Everest (K2/Everest). Denali has no English label in the r1 cache (skipped).

## nearmiss-lc2 (run once, after commit 98db9827; `shasum -c nearmiss-lc2.sha256` OK, a4428c78…)
**FP 0/40** (`nearmiss-lc2-r6.jsonl`, `.out.txt`). No code change after the run.

UNKNOWN: recall on set 4 (blind; coordinator). Data review is one reviewer's memory on 120 rows of 3,197 new; obscure peaks and 2020 city
estimates (Sirajganj, Junagadh) unverified. Gate (b) uses sitelinks as "prominence" and matches labels case-sensitively (it misses
lowercase senses). The criterion's "500 highest" yields mostly 6,600–8,800 m Himalayan sub-peaks; mid-height famous peaks enter only via prominence.
