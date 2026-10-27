# Overture "vegan/vegetarian restaurant" places as a supplement to OSM diet tags in the places tiles
TL;DR: BOAR's answer to "best vegan restaurants in [city I'm in]" depends on OSM `diet:*` tags, which are sparse outside a few cities. Overture's places theme labels venues `vegan_restaurant` / `vegetarian_restaurant` from Meta, Foursquare and Microsoft data under permissive licenses. Within BOAR's own tile boxes it adds 10 (Edmonton), 189 (Bien Hoa) and 220 (Queens) dedicated veg venues that the OSM tile doesn't have. Precision varies, so the existing diet-plausibility check must apply.
Lane: Sonar · Status: evidence · Priority: B
Axes moved:
- quality/retrieval on the post author's own stated query, in cities where OSM diet tagging is thin: more and real vegan/vegetarian venues near the user;
- truthfulness ± (category errors: a bar labeled vegetarian; mitigated by the existing `dietCheck` / "verify" flag);
- resources: + a few MB per tile;
- not measurable by the current bench: its 3 vegan items are graded against OSM gold, so Overture-only venues would score as unverified.

Fits BOAR? Yes, entirely at pack-build time (desktop DuckDB over Overture's public GeoParquet, bbox reads of a few MB to tens of MB). Records go into the existing `pois` schema:
- `source.kind` gains "overture";
- `diet.vegan`/`diet.vegetarian` = "only" for a restaurant whose primary category is dedicated, like OSM `cuisine=vegan` today.

The app side is unchanged: same tiles, same ranking, same "according to …" label with a new source name. Offline.

Evidence (own, 2026-10-02, `sonar/exp/12-overture-diet/`). Overture release 2026-09-23.1, `taxonomy.primary` (the `categories` field was replaced in Sept 2026). Boxes = the bbox of BOAR's own built tiles `shared-data/poi/drawn/{city}.sqlite`. Confidence ≥ 0.7.

| City tile | OSM POIs in tile | OSM vegan-tagged / vegetarian-tagged | Overture vegan_restaurant / vegetarian_restaurant | Overture venues not matched in the OSM tile (name ±150 m) | Matched, but OSM has no diet tag |
|---|---|---|---|---|---|
| Edmonton | 2,409 | 12 / 17 | 7 / 13 | **10 / 18** | 6 |
| Bien Hoa (VN) | 3,206 | 273 / — | 6 / 491 (253 at ≥ 0.7 conf.) | **189 / 259** | 4 |
| Queens (NYC) | 19,963 | 703 / 855 | 201 / 145 | **220 / 313** | 19 |

- Name matching is crude (normalized substring + 150 m), so "not in OSM" is an upper bound.
- **Spot check (first 14 rows, `ov3.py` listing):**
  - Bien Hoa: all names carry "chay" (Vietnamese for vegetarian): plausible 14/14.
  - Edmonton: plausible: Noorish Conscious Eatery, Padmanadi, Seitan's, Copper Branch, Die Pie, Veg Delight, VISH. Doubtful: Freshii (salad chain), The Buckingham (bar), Doppio Zero (pizza), Remedy Cafe (options, not veg-only). So ~60% precision.
  - Sources: Meta, Foursquare, Microsoft.
- Licenses (Overture's attribution page, accessed 2026-10-02; SHELF row): places sources are CDLA-Permissive-2.0, Apache-2.0 (Foursquare) and CC0 (AllThePlaces). Attribution is required, with no share-alike. **Mixing with ODbL OSM records in one SQLite pack: Veil should confirm** whether it is a collective database (separate records, separate attribution) or a derivative of OSM. UNKNOWN.
- the bounty post's test is a city he happens to be in. The bench's 3 named-city items (Berlin, Lisbon, Tokyo) are OSM-rich and pass today. The risk is the unknown city, and thin-OSM regions (SE Asia, parts of North America) are exactly where Overture adds most.

Test (not boar-eval's judge; the bench's venue gold is OSM-only):
- Build Overture-supplemented versions of 5 existing tiles: Edmonton, Bien Hoa, Queens, and 2 more thin-OSM cities picked by lowest vegan/POI ratio in `shared-data/poi/drawn/`. Run the existing `scripts/audit-poi-diet.mjs` plausibility check on the added records.
- Success criterion (frozen now):
  - (a) within 3 km of each tile's centre, places labeled vegan or vegetarian rise from < 5 to ≥ 5 in at least 3 of the 5 cities;
  - (b) on a blind 30-venue sample of *added* records (pooled across cities, shuffled, labelled by a separate Opus rater with web access as plant-based / has options / not), ≥ 80% plant-based or vegetarian-dedicated after the `dietCheck` filter;
  - (c) every added record has a source URL or record id and the attribution line;
  - (d) Veil OKs the license mix before anything ships.
- Optional bench extension (Lantern/Veil): 3 "vegan in [thin-OSM city]" items graded against OSM ∪ Overture gold.

Cost to try: ~4–6 h (DuckDB extract per tile + pois writer adapter + audit + 30-label check). Download: bbox reads only (tens of MB). Risk: low for the app (data only); medium for licensing (needs Veil).

## Details

Why this and not more OSM: BOAR's OSM pipeline already reads `diet:vegan`, `diet:vegetarian` and `cuisine=vegan` (`scripts/lib/poi-pack-lib.mjs`). The gap is missing tags in OSM itself, not missing parsing.

Ranking "best": neither source has ratings. Overture's `confidence` measures the place's existence, not its quality. Dedicated places ("only") should rank above "has options" as today. Overture adds dedicated places, not reviews. UNKNOWN whether any open, licensable rating source exists (not found yet).

What would make it fail:
- Category precision in Western cities (~60% in the Edmonton sample) is below the bar after `dietCheck`. Then use Overture only to *confirm* OSM venues (the "in OSM, no diet tag" column: 6 / 4 / 19) and in regions where names carry the diet word ("chay", "vegan", "vegetarian", "素").
- Stale places (Overture has `operating_status`; all 0 closed in these samples). UNKNOWN freshness.
- Licensing mix rejected by Veil, so a separate Overture tile with separate attribution would be needed.
