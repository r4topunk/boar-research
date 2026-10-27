# VENUEGPS — V-para P5 cause + runner-only device location (2026-10-07, criterion 378f11ec…, 0 judge calls)
TL;DR: cause on cut 6 = **no-location 7/7** (both seeds). With the injected device fix the engine gets a GPS point on 7/7 but
returns **0 venues on 7/7 (places:coverage-none)**: kit-vexact has only Berlin/Lisbon/Tokyo tiles, the V-para venue points
fall in 5 other 1° tiles. **P5 with location 0/7 (s42)**, s43 not run (no pass). Verdict branch 0/7, see below.
## 1. Cause (tools/cause.mjs, cause.md)
| class | cut 6 s42 | cut 6 s43 | cut 7 + location s42 |
|---|---|---|---|
| no-location | 7 | 7 | 0 |
| no-places-hit | 0 | 0 | **7** (places:coverage-none) |
| places-hit-but-answer-ignores / other | 0 / 0 | 0 / 0 | 0 / 0 |
Ids: vpara-016, 017, 018, 019, 020, 049, 050. All route task:places + near:device (the questions read as "near me").
## 2. Schema
items.jsonl keys: id, category, question, answer, lang, danger, rubric, grading{type, must_any, forbid, refuse_ok, city, diet,
minRealVenues, matchAgainst, gold_file, gold_snapshot, scorer}, grading_version, reference_sources, origin, provenance, license.
**No location field.** Gold files carry `user_location{lat, lon}` → tools/venue_locations.py → blind/V-para/venue-locations.json
(sha 376a4e9a…): 016 (50.0617, 19.9373), 017 (50.0513, 19.9445), 018 (41.6934, 44.8014), 019 (41.7092, 44.7994),
020 (46.0514, 14.5061), 049 (39.4699, −0.3763), 050 (−13.5167, −71.9787).
## 3. Runner option (runner-location.patch, sha 1d10fc58…; boar-eval uncommitted, adapter.ts only, +17/−1)
`BOAR_ITEM_LOCATIONS=<json [{id,lat,lon}]>`: for an item with no context lat/lon, the adapter sets the point that its
geoProvidersFrom getCurrentPoint/getLocationFix already return (the app's GPS slot), in the app's Point shape
(src/services/location.pure.ts: lat, lon, accuracyM 20, ageS 0 = fresh fix); records an `other/item-location` event and
versions["item.locations.sha256"]. Unset → no code path changes. tsc 0 errors, vitest 35/35. Engine untouched.
## Gate (option OFF, cut 7 = wt/cut7 6d0b93b1 via git-archive copy, config (b) s42, MacBook M1 Pro cpu x4, no detector)
| set | answer text identical | route identical (excl. detector codes) |
|---|---|---|
| 7 venue items vs cut 6 s42 traces (mini M4) | **7/7** | 7/7 |
| 5 non-venue (vpara-001…005) vs cut 6 s42 traces | **2/5** | 5/5 (retrieval raw+kept 5/5, prompt tokens 5/5) |
| same 5, patched-OFF vs committed runner (adapter 7a0282ae) on the MacBook | **5/5** | 5/5 |
The 3 non-venue diffs are generation only (same prompt, M1 vs M4 CPU kernels); the patch is byte-neutral when off.
## 4. P5 with location (cut 7, config (b) kit-vexact, s42; scorer rnd/kiln/l1/cut6-claim-b-venues.mjs unchanged)
| id | location event | POIs returned | venues returned | OSM gold matches | pass (≥ 3) |
|---|---|---|---|---|---|
| 016, 017, 018, 019, 020, 049, 050 | granted (7/7) | 0 (coverage none) | 0 | 0 | no |
**P5 0/7** (OFF 0/7). Engine-returned venue names: none. Runtime: places path median 10 ms/item, max 177 ms; setup ≈ 50 s.
Coverage check (no blind data): the 5 covering tiles t-N50E019, t-N41E044, t-N46E014, t-N39W001, t-S14W072 ARE in the shipping
world-places tile catalog (8,374 tiles; 0.2–1.1 MB each, 36–139 vegan POIs) but not on the MacBook and not in kit-vexact.
## Verdict (criterion rule, read once)
0/7 → "the cause is not location". Precise reading: location is the first blocker (7/7 → 0/7 no-location) but not
sufficient; the next blocker is places-kit coverage (7/7 coverage-none). Runner fix NOT adopted by the rule (needs ≥ 5/7).
Next step (not run, needs a new criterion): config (b) + the 5 catalog tiles + location; tiles must be fetched first.
## Deviations
1. MacBook-local tree (git archive of wt/cut7 into the session scratchpad, tools/build-tree.sh) instead of run.sh on the mini.
2. No learned detector (no llama-server on the MacBook): lexical predicate; venue traces never consult it; non-venue p was 0.000.
3. Extra same-machine gate (committed vs patched runner) because cross-machine generation is not byte-stable.
## Exposure log
Scripts read: blind/V-para/items.jsonl, gold files (venue_locations.py, venue scorer), runs-cut6 s42/s43 traces,
requests, config. Written in blind/: venue-locations.json, runs-venuegps/ (vg-{off,offnv,orig,on}-s42 requests/traces/logs,
venues-vg-s42.json). Left blind/: ids, the 7 coordinate pairs, route codes, counts, booleans, timings. No question, gold or
reference text read; field names seen: trace keys incl. "question" (name only), gold keys incl. user_location. wt/cut7 status clean.
UNKNOWN: P5 with tiles installed; s43 (not triggered); whether the app auto-installs the covering tile for a fresh fix.
