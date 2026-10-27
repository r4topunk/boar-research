# C — Places/GPS path audit: "vegan restaurants near me" on GrapheneOS, offline

Sonar exp-31 (C). 2026-10-03. Read-only audit; no repo or engine tree modified.

**Code basis.** App = `UPSTREAM_REPO/boar-app` **upstream/main 38f996d1** (2026-10-03, "main is Android only"). For every file cited below, the local checkout (`docs/privacy-ios-location` @ 5ad9dcf7) is byte-identical to 38f996d1, except `src/routing/answer.ts`, which differs only after line 649. Engine = health13 checkout `be-0cfd4a77-health13` (0cfd4a77 + health patches). `geo.ts` there is identical to the app's.
**Runs.** `C-runs/` next to this file: `requests.jsonl` (18 places questions), `traces.jsonl`, `summary.txt` (desktop runner on the health13 engine with gazetteer 215ce466 and tiles Berlin, Lisbon, São Paulo, Rome). `coverage.py`/`coverage.json` hold the per-city vegan counts. `intent.ts`/`intent.out.txt` hold 24 intent probes.

---

## 1. TL;DR

- **No. On the Android app that ships (main 38f996d1), "vegan restaurants near me" never reaches the places engine.** The Android chat (`src/ui-android/ChatScreen.tsx:625-649`) sends every question to `classifyTask → retrieve → LLM`. Nothing on Android calls `detectGeoIntent`, `registerGeoProviders` or the location module. The README says so too: places are "in the iPhone app on `ios_android` for now" (`README.md:89`). What the question gets instead is a generic retrieval answer from Wikivoyage/Wikipedia with no position, which risks invented venue names. That path was not run on a device (UNKNOWN U1).
- **Location permission is missing from the APK.** `app.json` has no Android location permission. `plugins/withBuildVariant.js`, which adds FINE/COARSE (`:42-46`, `:59-63`), is "called from app.config.js", and `app.config.js` was deleted in revert aec9a0b7 and never restored. `aapt2 dump permissions boar-0cfd4a77-forge-release-arm64.apk` lists no `ACCESS_*_LOCATION`. The older new-UI build (4f170bb9-offline) did list them. Without the permission, the GPS module cannot get a fix on any phone.
- **The building blocks are GrapheneOS-safe and work.** The location module is a custom Expo module on plain `LocationManager.GPS_PROVIDER` plus the passive provider's last fix. It uses no FusedLocationProviderClient, no NETWORK_PROVIDER and no Play Services (`OfflineLocationModule.kt:21-28`). `expo-location` is banned by test (`src/config/networkAudit.test.ts:33-35`). The engine path works on desktop with a GPS point injected: Berlin, Lisbon and São Paulo (PT) "near me" each list 10 real OSM vegan venues with distance, address, hours and `[n]` OSM links in 12-130 ms (`C-runs/summary.txt` pl-01/02/09). The Sextant gate passes places-001..007 at 20/20 rows (`handoff/Sextant.md:45-54,81`).
- **The data is ready and small.** World coverage is 8,374 one-degree tiles, 980 MB in total, holding 3.49 M food POIs and 51,840 vegan-tagged ones, all hosted on HF. A diet-only global pack (vegan or vegetarian, 115,055 POIs) would be about 32 MB. Vegan venues within 10 km: Berlin 1,696, London 1,116, NYC 576, Tokyo 149, São Paulo 112, Lisbon 108, Rome 100, Bangkok 77, Mexico City 57. None of it is installable from the Android UI, because `CORPUS_CATALOG` has no POI entries (`src/models/manifest.ts:275`).
- **Shortest path to a working the post author demo: about 5 small changes, all already written on the `ios_android` branch.** (1) Register geo providers in the Android `App.tsx`. (2) Send places intents from ChatScreen through `answer()`. (3) Declare FINE/COARSE location. (4) Add a "Use my location / type the city" affordance. (5) Ship the gazetteer plus tiles (whole world ≈ 1 GB). Next priorities: a GPS wait longer than 10 s for offline cold starts (no A-GPS on GrapheneOS when offline), and restaurant-only filtering. Today 2-4 of every 10 listed "restaurants" are ice-cream shops, cafés or bakeries.

---

## 2. The path, step by step

Statuses: **works**, **broken**, **missing**, **untested**. "Engine" means it was verified through the desktop runner. "Android" means the shipped Android app.

| # | Step | Code (file:line) | Status | Evidence |
|---|------|------------------|--------|----------|
| 0 | **Chat entry on Android** | `src/ui-android/ChatScreen.tsx:625-649` (`classifyTask` → `retrieve` → `llamaEngine.generate` / `runAdaptiveChat`). `src/services/adaptiveChat.ts:17-31` imports no geo code. | **broken (missing route)** | `git grep detectGeoIntent 38f996d1 -- src` matches only `answer.ts:80,621,624` and `geo.ts:163`. Android UI files never import `answerService` (only `src/eval/answerEval.ts:13` does). README: `README.md:89`. |
| 0b | **Provider registration** | `src/routing/answerService.ts:30-41` (`registerGeoProviders`). `:96` `getGeoProviders: () => geoProviders` | **missing on Android** | No caller in 38f996d1. The only caller was `src/ui-ios/App.tsx:25-35` (a6633f8d, now on `ios_android`). On-device Android eval (moto g75, 2026-10-02) through `answer()`: "Tell me the best vegan restaurants in Berlin / Lisbon / Tokyo" all gave "The offline places pack is not installed…" with `places:no-pack` (`boar-eval/runs/devices/2026-10-02/android/be-and-q15-quick-r1/rows.jsonl`, food-001/002/006). The same happened in all 804 `task:places` rows across `boar-eval/runs` (kiln, night, p*). |
| 1 | **Intent detection** | `src/routing/geo.ts:163-194` (diet `:99-105`, FOOD_PLACE `:109`, NEAR_DEVICE `:123-124`, IN_PLACE `:127-128`, placeCandidates `:134-153`) | **works (engine)**, with gaps (§4) | pl-01..18 routed as expected, except the cases in §4. Probes in `C-runs/intent.out.txt`. |
| 1b | **Health pre-emption** | engine `answer.ts:671-673` (health13: `healthNow` / `isCardEmergency` → `places:skipped-health`). App main: `answer.ts:619-625` has no guard. | **works (engine health13)**. **Broken on main**: a health message with a food or place word goes to places. | pl-15 "choking at a vegan restaurant near me" → choking card plus `places:skipped-health` (traces). On main, eval rows show PT diarrhoea in Manaus → `task:places places:no-pack` (12 rows, kiln health5/b5gate). |
| 2 | **Location acquisition: API** | `modules/offline-location/android/.../OfflineLocationModule.kt:78-102` (`getCurrentPosition`), `:106-148` (`freshGpsFix`: `getCurrentLocation(GPS_PROVIDER)` on API 30+, else `requestSingleUpdate`), `:151-157` (lastKnown: GPS + PASSIVE) | **works in code, untested on device** | No Play Services: `strings classes*.dex` in the 0cfd4a77 APK finds `offlinelocation` (classes10.dex) and no `gms/location` / FusedLocation. The module has no gradle dependency beyond the Expo module plugin (`modules/offline-location/android/build.gradle`). |
| 2b | **Permission** | Declared in `plugins/withBuildVariant.js:42-46,59-63`, but that plugin is not loaded: `app.json:43-62` lists plugins without it, and there is no `app.config.js` in 38f996d1. Request: `OfflineLocationModule.kt:58-68`. Policy: `src/location/locationPolicy.ts`, `src/services/location.ts:87-93` (`locateForUser`). | **broken (not declared)**. **Missing on Android**: nothing calls `locateForUser`. | `aapt2 dump permissions` on `<volume>/boar/android/apk/boar-0cfd4a77-forge-release-arm64.apk` shows INTERNET, RECORD_AUDIO, … and no location permission. The 4f170bb9-offline APK (Sep 30) shows ACCESS_FINE_LOCATION and ACCESS_COARSE_LOCATION. v1.0.0 APK: none. |
| 2c | **No prompt in the answer path** | `src/services/location.pure.ts:52-55` (`permissionBlock` → `prompt`). `answer.ts:479-482` maps prompt, denied and timeout to `needsPlaceAnswer` | **works (by design)**. Needs a UI button that is missing on Android. | pl-03 (no fix): "I couldn't get your location (permission denied or GPS unavailable). Which city are you in?" with `location:unavailable`. |
| 2d | **Timeout and stale fix** | `answer.ts:204-213` (`LOCATION_WAIT_MS` = 10 s, `LOCATING_SIGNAL_MS` = 150 ms, `DEVICE_INSIDE_TIMEOUT_MS` = 150 ms). `location.ts:60-75` (last fix ≤ 5 min → used, else a new fix within `timeoutMs`). `location.pure.ts:6,70-79` (older than 5 min → `stale`). `answer.ts:472-478` (stale → "The last one was in X, N min ago…") | **works (logic, unit-tested)**. **Risky on a device**: 10 s is short for an offline cold GNSS start. | Offline GrapheneOS has no SUPL/A-GPS, so a cold time-to-first-fix is typically tens of seconds and longer indoors (U3). `nearestCity` uses only the 10 sample regions' cities (`geoWiring.ts:31-39` plus the iOS wiring's `POI_REGIONS.flatMap`), so with tiles the stale message usually names no city. |
| 2e | **Coarse-only grant** | `OfflineLocationModule.kt:96-99` (without FINE: cached passive fix, else `E_UNAVAILABLE`) | **degrades silently** | On Android 12+ a user who picks "Approximate" gets no fresh fix offline, because no network provider is used. The answer then says "permission denied or GPS unavailable" and does not explain that precise location is needed. |
| 3 | **Place resolution (gazetteer)** | `src/rag/pois.ts:144-171` (opens `poi/world-places.sqlite`). `src/rag/poiPack.ts:274-300` (`cleanPlaceName`, `resolvePlaceIn`: exact name or alternate name, NOCASE, most populous). Fallback `src/routing/geoWiring.ts:43-48` (pack cities plus the PT lexicon). Lower-case candidates `answer.ts:411-424` | **works (engine)** | 34,149 places with population ≥ 15k and 366,144 names (`shared-data/poi/world-places-tiles.sqlite.json`). Resolves NYC, New York, CDMX, Ciudad de México, Roma, Tóquio, Berlim, Lisboa, Kreuzberg and Shibuya; Alexanderplatz does not resolve. pl-08 "rome" (lower case) → `places:gazetteer-name`. pl-16 "Kreuzberg" lists 10 venues. |
| 4 | **POI tile lookup** | `pois.ts:92-111` (`installedPoiAreas`: tile bbox from the file name, opened lazily). `poiPack.ts:209-214` (coverage), `:224-246` (radii 3 → 10 → 25 km until ≥ 3 exact matches, every overlapping area). `poiPack.ts:142-157` (cell-range SQL plus FTS for the cuisine text) | **works (engine)** | pl-01 region `t-N52E013`, coverage `full`, retrieval 62 ms. pl-04 and pl-07 (Tokyo, no tile installed) give an honest `coverage-none` with no list. |
| 5 | **Diet filter** | `poiPack.ts:163-167`: OSM `diet:<d>` not equal to `no`, or a Wikivoyage listing that mentions the diet. Doubtful tags `:249-253` (`diet_check` < 0.35 → listed last as "to verify") | **works**, with gaps | Only the vegan tag is plausibility-checked. Tile meta shows `dietChecked` 2,117 ≈ vegan 2,113 for Berlin, so vegetarian tags are not checked: pl-18 lists "Poke House — vegetarian: only" (a fast_food poke shop). "plant-based" and "veggie" get no diet filter at all (§4). |
| 6 | **Ranking** | `poiPack.ts:254-260` (diet strength only > yes > limited, then distance; approximate places, then doubtful ones). City mode `answer.ts:518-530` (with address first). No category filter: `FOOD_CATEGORIES` `poiPack.ts:22-25` includes bar, pub, ice_cream, bakery, deli, … | **works as specified**. Weak for "restaurants" | Non-restaurant venues in the top 10 (tile lookup by OSM ref): Berlin 3-4/10 (Brammibal's Donuts, Zerö Kebab, The Sanctuary bakery, Die vegane Fleischerei deli), Rome 4/10 (2 gelaterias at #1 and #5), São Paulo 4/10, Lisbon 2/10. "Best" in a city means "diet:vegan=only nearest the city centroid". The answer states this criterion (`geo.ts:358-365`). |
| 7 | **Answer text and UI** | `geo.ts:311-375` (`formatPlacesAnswer`: name, distance, address, diet level, hours, `[n]`). `answer.ts:533-565` emits `sources` and `places` events and returns the text (no `token` event) | **works (engine text)**. **Missing on Android** (no places card, no "locating…" state, no "type the city" fallback) | The full text is in `C-runs/summary.txt`. The iOS UI had a `PlacesCard` (`ios_android` branch). |
| 8 | **Attribution** | `geo.ts:263-284` (each POI is a source chunk with its OSM URL and extract date). `geo.ts:367-373` (ODbL / volunteers line). `answer.ts:533-536` (attribution: osm/ODbL, wikivoyage/CC BY-SA). License strings `poiRegions.ts:37` | **works (engine)** | Each list row carries `[n]` → `https://www.openstreetmap.org/node/…` (traces `retrieval.kept`). |
| 9 | **Pack install** | Catalog: `poiRegions.ts:48-55` (gazetteer 22.96 MB, HF commit 0d75f30), `:828-864` (regions plus `registerAssetProvider("poi")`). Tiles: `pois.ts:186-212` (`loadTileCatalog`: tile index inside the gazetteer, 8,374 URLs), `:233-239` (`tilesFor`). City tiles `poiRegions.ts:897-` | **works in engine/eval** (`src/eval/answerEval.ts:79-96` installs a city's tiles). **Missing in the Android UI**: setup and Knowledge Base read `CORPUS_CATALOG` (`manifest.ts:275`), which has no POI entries, and nothing calls `loadTileCatalog` | The Android Knowledge Base therefore cannot install places, so the engine's own message "Install it from Knowledge Base" (`geo.ts:438-442`) points nowhere on Android. |

---

## 3. Data coverage

**What exists** (all local under `<workspace>/shared-data/poi/`):

| Asset | Size | Content | Hosted |
|---|---|---|---|
| Gazetteer `world-places.sqlite` (sha 215ce466; = `hf-stage-gaz/places/world-places.sqlite`) | 22.96 MB | 34,149 places (GeoNames ≥ 15k), 366,144 names, tile index (8,374 rows) | HF `r4topunk/boar-packs` @0d75f30 |
| World tiles `geofabrik/work/tiles/t-*.sqlite` | **980.3 MB total**, 8,374 files; median 36 KB, p90 0.22 MB, max 9.9 MB (Tokyo) | 3,384,898 OSM + 105,758 Wikivoyage food/drink POIs; **51,840 vegan-tagged**, 103,575 vegetarian-tagged (vegan or vegetarian: 115,055); OSM 2026-09-25/27 | HF @44c3375 (all 8,374 have a `url`) |
| Sample city packs `POI_REGIONS` (`poiRegions.ts:58-`) | 0.04-4.3 MB each | 10 regions (Berlin 3.3 MB / 1,979 vegan; Queens 665; Taipei 156; São Paulo 126; Singapore 97; Buenos Aires 78; Bien Hoa 266; Neza 60; Edmonton 12; Qujing 0) | HF @2b5b193 |

Cost per POI as measured: about 281 B, including the cell index and FTS5.

**Vegan-tagged POIs by city** (`C-runs/coverage.py`). The centre is the gazetteer point, the categories are `FOOD_CATEGORIES`, and "vegan" means `diet:vegan` ∈ {only, yes, limited}. Tiles are those within 15 km of the centre.

| City | Tiles (MB) | ≤3 km vegan (only) | ≤10 km vegan (only) | ≤10 km vegan *restaurants* | ≤10 km vegetarian | ≤25 km vegan |
|---|---|---|---|---|---|---|
| Berlin | 1 (3.7) | 521 (35) | 1,696 (103) | 801 | 2,909 | 1,902 |
| London | 2 (9.3) | 388 (19) | 1,116 (80) | 454 | 1,614 | 1,386 |
| New York City | 2 (7.2) | 152 (23) | 576 (63) | 269 | 717 | 656 |
| Tokyo | 1 (9.9) | 18 (9) | 149 (45) | 89 | 134 | 167 |
| São Paulo | 1 (1.7) | 38 (13) | 112 (32) | 68 | 84 | 121 |
| Lisbon | 2 (2.1) | 90 (13) | 108 (13) | 82 | 185 | 140 |
| Rome | 2 (2.3) | 38 (4) | 100 (13) | 59 | 148 | 120 |
| Bangkok | 1 (1.7) | 27 (2) | 77 (12) | 65 | 115 | 86 |
| Chiang Mai | 2 (0.8) | 50 (7) | 58 (7) | 52 | 93 | 61 |
| Mexico City | 2 (2.1) | 8 (2) | 57 (13) | 40 | 48 | 59 |
| Kathmandu | 1 (0.9) | 9 (1) | 17 (1) | 15 | 51 | 17 |
| Nairobi | 1 (0.4) | 3 (1) | 9 (1) | 8 | 19 | 9 |
| Qujing | 1 (0.04) | 0 | 0 | 0 | 0 | 0 |

Takeaway: every big travel city has ≥ 50 tagged vegan venues within 10 km. The Global South and smaller cities thin out fast (Nairobi 9, Qujing 0). There, the honest "no place tagged vegan within 25 km" answer (`geo.ts:389-417`) is the correct output.

**What a GLOBAL pack costs:**

| Option | Size | Notes |
|---|---|---|
| All OSM food/drink POIs, world (already built) | **0.98 GB** (+ 23 MB gazetteer) | 2% of the 50 GB budget. This is the recommended default for the demo kit. |
| Vegan + vegetarian only, world (OSM) | **≈ 32 MB** (115,055 × 281 B) | It cannot answer "restaurants near me" without a diet, nor give honest no_match answers about other diets. Fits in the APK. |
| OSM raw tag counts (taginfo, 2026-10-03) | — | `diet:vegan` 67,658 objects; `diet:vegetarian` 117,846. This includes `=no` and non-food objects. [taginfo diet:vegan](https://taginfo.openstreetmap.org/keys/diet:vegan), [API](https://taginfo.openstreetmap.org/api/4/key/stats?key=diet:vegan) |
| Overture Places (all categories) | ≈ 20 GB at 281 B/POI (estimate) | 72 M POIs as of Jan 2026 ([marksblogg](https://tech.marksblogg.com/overture-places-pois.html); [Overture places guide](https://docs.overturemaps.org/guides/places/)). The food share and diet categories are not verified (U6). If the food share is about 20%, a food-only pack would be about 4 GB. Overture adds coverage where OSM is thin, but it has no `diet:*` tags, and its rows need dedup against OSM. |

---

## 4. Failure modes with repro questions

| # | Failure | Repro (where) | Cause (file:line) | Severity for the demo |
|---|---|---|---|---|
| F1 | **Android chat never does places.** It answers from the LLM plus Wikipedia/Wikivoyage, without a position. | Any of: "vegan restaurants near me", "best vegan restaurants in Berlin" in the Android app | `ChatScreen.tsx:625-649`; no `registerGeoProviders` caller | **Blocker** |
| F2 | **No location permission in the APK**, so even a wired path gets `denied` or "unavailable" | `aapt2 dump permissions <0cfd4a77 apk>` | `app.config.js` missing; `withBuildVariant.js` unused | **Blocker** |
| F3 | **No way to install places on Android.** The engine message "Install it from Knowledge Base" is a dead end. | Engine `answer()` on Android: moto g75 rows food-001/002/006 → `places:no-pack` | `manifest.ts:275`, Android Knowledge UI; `loadTileCatalog` never called | **Blocker** |
| F4 | **Offline cold GPS exceeds the 10 s wait**, which leads to "Which city are you in?" or the stale prompt | Phone offline for hours (or after a reboot), indoors: "vegan restaurants near me" | `answer.ts:206` (`LOCATION_WAIT_MS` = 10 s) | High (first-run demo) |
| F5 | **"Approximate" grant yields no fix offline**, and the message blames "denied or GPS unavailable" | Android 12+: choose "Approximate" in the dialog, then ask "vegan near me" | `OfflineLocationModule.kt:96-99`; `geo.ts:419-423` | Medium |
| F6 | **"Restaurants" lists ice cream, donuts, delis and bars** | pl-08 "best vegan restaurants in rome" → #1 Gelateria Olive Dolci, #5 Gelateria Fassi; pl-05 Berlin → #1 Brammibal's Donuts | No category filter for "restaurants" (`geo.ts:184-193` never sets categories; `poiPack.ts:147`) | Medium (looks sloppy) |
| F7 | **"near <landmark/neighbourhood>" is ignored**: it falls back to device GPS, or with no fix asks for the city | pl-11 "vegan restaurants near Alexanderplatz" → `location:unavailable`. Probe: "…close to the Colosseum" → device | `IN_PLACE` has no "near" (`geo.ts:127-128`); the gazetteer has no landmarks | Medium |
| F8 | **Diet synonyms are lost**: the list comes back with no diet filter and nothing says the diet was dropped | Probes: "plant-based restaurants near me", "veggie food near me" → `diet=-` | `DIET_PATTERNS` `geo.ts:99-105` | Medium |
| F9 | **Explanation question answered with a list** | Probe: "Why are there so many vegan restaurants in Berlin?" → places:Berlin | `geo.ts:172-173` (an EXPLANATORY question is excluded only when it names no place) | Low-medium |
| F10 | **"Open now" ignored**: hours are shown but not checked against the current time, and the answer does not say so | pl-13 "Is any vegan restaurant near me open right now?" → plain list | No opening-hours evaluator (none in `src/`) | Low-medium |
| F11 | **Out-of-scope venue type answered as restaurants** | pl-17 "Where can I find vegan groceries near me?" → restaurant list | Packs hold food/drink only (`FOOD_CATEGORIES`); intent fires on diet + "near me" (`geo.ts:176`) | Low-medium |
| F12 | **Unchecked vegetarian tags** | pl-18 Lisbon → "Poke House — vegetarian: only" | `diet_check` vegan-only (tile meta `dietChecked` ≈ `vegan`) | Low |
| F13 | **Health pre-emption absent on main**: a health message with a place or food word gets the places path | Kiln rows: "Minha filha … diarreia … aqui em Manaus … sem comida" → `task:places places:no-pack` | `answer.ts:619-625` (main) vs engine health13 `answer.ts:671-673` | High for safety; fixed in health13, not yet on main |
| F14 | **Stale fix rarely names a city** | A last fix older than 5 min in any non-sample city | `nearestCity` uses `POI_REGIONS` cities only (iOS wiring / `geoWiring.ts:31-39`) | Low |
| F15 | **No tile, no hint**: "no offline place data near you" without an offer to download that area | pl-04 (Tokyo GPS, tile not installed) | `geo.ts:378-383`; the Android UI lacks the `tilesFor` offer | Low if the world pack ships |

The following work correctly in the engine and are worth keeping: Tokyo with no tile gives an honest "no data" (pl-07). PT/BR "restaurantes veganos perto de mim" gives a PT answer (pl-09). Cuisine text works ("vegan ramen" → 6 ramen places, pl-12). Lower-case city names resolve (pl-08), and so do neighbourhoods (pl-16 Kreuzberg). A choking emergency at a restaurant gets the first-aid card (pl-15, health13).

---

## 5. Minimal fixes for an end-to-end the post author demo (impact/effort order)

**Decisions** (direction):
- D1. Ship the whole-world places pack (0.98 GB of tiles plus the 23 MB gazetteer) in the default offline kit, with no per-city picking. It costs 2% of the budget and makes "near me" work wherever the judge is.
- D2. Places answers stay deterministic with no model, as built: names come only from OSM records.

**Tasks** (each has a definition of done):

| # | Fix | Effort | Done when |
|---|---|---|---|
| T1 | Restore the location permissions: re-add `app.config.js` calling `applyVariant` from `plugins/withBuildVariant.js` (it also restores the offline variant's network-permission stripping), or add `android.permissions: [ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION]` to `app.json` | XS | `aapt2 dump permissions <new apk>` lists both; no INTERNET in the offline variant |
| T2 | In `src/ui-android/App.tsx`, call `registerGeoProviders(geoProvidersFrom({installedPoiPacks, getCurrentPoint, getLocationFix, resolvePlace, searchPois, cities}))`. These 10 lines exist at `ios_android:src/ui-ios/App.tsx:25-35`. Also call `loadTileCatalog()` at boot. | XS | The device eval request (`answerEval`) with tiles installed returns `places:10` for food-001 instead of `places:no-pack` |
| T3 | In `ChatScreen.tsx`, before `runFixedModelChat`/`runAdaptiveChat` (≈ `:620`): if `detectGeoIntent(query)` matches (and, after the health13 merge, the message is not health), call `answer({query})` from `answerService`, render `result.text` (markdown list with `[n]`) and `sources` | S | On the phone, "vegan restaurants near me" (permission granted, GPS fix) shows ≥ 3 OSM vegan venues with distances within 1 s of the fix. pl-01..18 answers match the desktop runner |
| T4 | Location UX on Android: on the `location` events `prompt` / `denied` / `unavailable` / `stale`, show inline buttons "Use my location" (→ `locateForUser`, `location.ts:87-93`, then re-ask) and "Type a city" (→ `answer({query, place})`, `answer.ts:620-622`). Show "Locating…" on `locating` with Stop | S | On a fresh install: first "near me" → explanation, system dialog, list. Deny → "type a city" works. No dialog is ever shown again after a "no" |
| T5 | Install places on Android: a Knowledge Base row "Places — whole world (1.0 GB)" (gazetteer + 8,374 tiles via the asset registry), plus file import for the offline build (`services/importBatch.ts` already knows `WORLD_PLACES`) | M | After a fresh setup the phone has `poi/world-places.sqlite` plus the tiles; `hasPlaces` is true; pl-07 Tokyo lists venues |
| T6 | Raise `LOCATION_WAIT_MS` 10 s → 30 s for the device path, keeping the "Type a city" escape visible while locating (check AOSP's `getCurrentLocation` cap, U4) | XS | On a phone offline ≥ 4 h, indoors near a window, "near me" resolves or offers the city prompt, never a silent hang |
| T7 | Restaurant filter: when FOOD_PLACE matched "restaurant(s)/restaurante(s)", pass `categories: ["restaurant","fast_food","food_court"]`, falling back to all food categories if fewer than 3 results | XS | pl-05/08: 0 ice-cream/bakery/deli entries in the top 10; Rome #1 is a restaurant |
| T8 | Intent fixes: (a) "near/close to/perto de X" → place candidate through the gazetteer, and if unresolved, ask "Which city?" instead of falling back to the device; (b) diet synonyms plant-based/veggie/vegetariano/vegano/vegana/sin carne; (c) explanatory "why/how" + place → not places; (d) "groceries/supermarket/mercado" → say places cover food and drink venues only | S | The probes in `C-runs/intent.out.txt` route as stated; unit tests in `geo.test.ts` |
| T9 | Merge the health13 `places:skipped-health` guard to main | XS (already written) | F13 repro is not `task:places` |
| T10 | "Open now": evaluate OSM `opening_hours` for the simple forms (Mo-Su hh:mm-hh:mm; off; PH ignored) against device time, and mark rows "open now" / "closed now". Otherwise, append "hours not checked against the current time" | S-M | pl-13 lists only the venues open at the test time, or says it could not check |
| T11 | (polish) Run the `diet_check` plausibility audit for vegetarian too; make `nearestCity` use the gazetteer (closest place ≥ 15k) | S | pl-18 Poke House is flagged "to verify"; the stale message names a city for any tile |

**Metric to close the loop:** one on-device run (Pixel/GrapheneOS, airplane mode) of `C-runs/requests.jsonl` through the Android chat. Pass when ≥ 15/18 answers match the desktop traces and "near me" works on a cold start, with time-to-list ≤ 30 s including the GPS wait.

**Options** (exploration, not decided):
- O1. A 32 MB diet-only global pack bundled inside the APK as an always-on fallback, with the 1 GB full pack optional.
- O2. Overture Places as a second source where OSM is thin. Needs dedup and has no diet tags.
- O3. Show Wikivoyage "Eat" listings next to the OSM list as a curated "guide picks" signal for "best".

### UNKNOWN
- **U1**: What the Android chat answers today for "vegan restaurants near me" (LLM over Wikivoyage, no position). It was not run on a device, and the desktop runner exercises `answer()`, not ChatScreen. The risk of invented venue names is unmeasured.
- **U2**: Whether Expo's `askForPermissions` resolves "denied" without a dialog when the permission is undeclared. AOSP behaviour suggests yes; not verified on a device.
- **U3**: Real offline cold time-to-first-fix on a Pixel running GrapheneOS: SUPL is unavailable offline, and the PSDS/XTRA cache may help if the phone was online recently. Needs a measurement.
- **U4**: Whether AOSP `LocationManager.getCurrentLocation` caps the request at about 30 s internally. That affects whether T6 needs `requestLocationUpdates` instead.
- **U5**: Battery and UX cost of 8,374 tile files on Android: directory listing time in `installedPoiAreas` (`pois.ts:92-111`) per question. Not measured; a merged per-continent file may be needed.
- **U6**: Overture's food-and-drink share and whether its taxonomy has vegan/vegetarian restaurant categories. Not verified.
- **U7**: The `ios_android` branch was not audited for Android-side wiring beyond confirming that `registerGeoProviders` is called only from `src/ui-ios/App.tsx`.

Competitors (noted, not copied): no device-location code was found in the local `competitors/competitor-app` or `a competitor team` trees (grep for LocationManager/FusedLocation: no hits). a competitor team (#132, "OSM") is not available locally.
