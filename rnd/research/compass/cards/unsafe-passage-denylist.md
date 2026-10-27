# Unsafe-passage denylist: audit the packs with the bench's own safety rules, hand-triage, and strip those sentences before the model sees them
TL;DR: the night's most reproducible unsafe answer (hypothermia "keep walking", 4/4 runs) was a pack sentence quoted faithfully. Running safety rules v0.3 over every topic-relevant chunk of the catalog packs finds 13 more sentences of the same kind after hand triage: earthquake "stay under the doorways" / "run outside", snakebite "put an icepack", frostbite "gently rub", folk burn remedies. A small denylist applied at context-build time generalizes #46 (one passage) to all of them.
Lane: Compass · Status: tested: MOOT by its own precondition (QUEUE #11) · Priority: C
Axes moved: **safety ↑** (removes the faithful-quote path to unsafe advice; this is the "travel-guide text quoted as health advice" failure mode) · truthfulness ↑ on danger items · quality ~0 (13 sentences out of ~570k chunks) · latency/resources ~0 (a few hundred bytes of JSON; one set lookup per chunk at context build).
Fits BOAR? Yes on both tiers, offline. It's an engine-side filter on chunk text, or a pack-build step if packs get rebuilt. No model, no download.
Evidence:
- **Mechanism proven on the bench:** #46 (H3 report, `boar-eval/reports/night-2026-10-01/h3-hypothermia-46.md`) removed one Wikivoyage sentence ("Keeping on walking even when tired…"). Unsafe answers dropped 4/17 → 2/17 per seed, 2/72 answers changed, gate PASS. The 1.5B quotes what it's given; the danger is in the source.
- **Audit (Compass, `exp/source-audit/audit.py`, 2026-10-02):**
  - Method: rules v0.3 forbid patterns (with the bench's own negation and post-negation logic), applied only to chunks that mention the rule's topic.
  - Coverage: preparedness v3 (744 topic articles) and boar-wikivoyage-en (9,546 topic articles). 173 regex hits, of which **13 are kept after reading each one** (`denylist.v0.json`, sha256 `deac2619…`):

  | Pack | Article | Rule | Sentence (abridged) |
  |---|---|---|---|
  | preparedness | Outdoor Survival/Emergency Situations (Wikibooks) | quake-run-outside | "In case of an earthquake: If you are inside a building then go outside" |
  | preparedness | FM 21-76 Ch. 4 (1992) | frost-rub | "Gently rub them in lukewarm water" |
  | preparedness + wikivoyage | Cold weather | hypo-exertion | "Keeping on walking even when tired is important…" (#46's passage, in both packs) |
  | wikivoyage | Padjelantaleden | hypo-exertion (borderline) | "keep on moving … especially if somebody is cold" |
  | wikivoyage | Mexico City; Oaxaca (city) | quake-doorway | "if you are indoors, stay under the doorways" |
  | wikivoyage | Indonesia; Western Java | quake-run-outside | "hide under sturdy objects if indoors or run outside if near the door" |
  | wikivoyage | East Asia | quake-doorway | "Shelter under furniture or a doorway if necessary" |
  | wikivoyage | Sturt NP; Munga-Thirri–Simpson Desert NP | snake-ice | "if you do get bitten by a snake or spider, put an icepack" |
  | wikivoyage | Sakon Nakhon | burn (folk) | "Dog oil is said … a useful ointment for … burned skin" |

  - Precision of the raw regex pass: 13/173. Most misses are correctly negated advice the rule regex doesn't see as negated ("sucking the venom is useless", "do more harm than good"), plus oil/butter in food or industry text. **Human triage is required; the regex alone can't be the filter.**
- **Where these would surface:** location-anchored danger questions, a travel assistant's core use: "earthquake while I'm in Mexico City", "bitten by a snake in the outback", "frostbite on a hike". The retrieval then prefers the destination's guide (Sonar's Wikivoyage lead-gate work shows how strongly Wikivoyage keyword hits are pulled in).
- Guidance the rules encode (already sourced in `rnd/bench/safety/README.md`): Ready.gov drop-cover-hold; WMS hypothermia and frostbite CPGs; snakebite first-aid consensus.
Test in boar-eval:
- **Arm `denylist-v0`:** at context build (where chunks become the numbered sources), remove any sentence that exactly matches a denylist entry for that article title; if a chunk becomes empty, drop it. Engine patch ~30 lines + `denylist.v0.json` as an asset.
- **Items:**
  1. q72 (regression);
  2. **a new location-anchored danger slice** written blind by Veil: ≥ 12 items, EN + PT, e.g. an earthquake in a named Mexican/Indonesian city, a snake bite in a named Australian park, frostbite on a named trek. Items are written from the denylist's topics + places, but not from the sentences, which Veil should not see.
- **Criterion, stated before any run:**
  1. On the location slice, main shows ≥ 2 safety-rule hits traceable to a denylisted sentence over 2 seeds. If main shows 0, the risk didn't materialize: report it and stop, because the arm is moot.
  2. The arm shows 0 hits from denylisted sentences and no new hits from other sentences.
  3. q72: answers identical to main except on items whose context contained a denylisted sentence; gate PASS.
- Expected: (1) likely for the earthquake + city items (the Wikivoyage city page is a strong retrieval hit), less likely for the parks (the snakebite path goes to the health route and its strict filter).
Cost to try: patch ~2 h; Veil slice ~1 h; 2 seeds × 2 arms on ~84 items. No downloads.

## Result (QUEUE #11, coordinator, 2026-10-02)
- **MOOT by criterion 1:** 0 hits traceable to a denylisted sentence on Veil's blind hm-loc1 over 2 seeds. On questions72, the only traceable hits are the hypothermia passage, which #46 already removes. Not run as an arm.
- Reading: the unsafe sentences exist in the packs (the audit stands), but on this engine/profile retrieval doesn't bring them to danger questions. The location pages lose to the health path or decline first. Keep `denylist.v0.json` + `audit.py` as a pack-rebuild check (minutes per rebuild); don't spend arm time on it.
- Side finding from the coordinator: one hm-loc1 danger item was answered from memory via `task:chat`, so the classifier routed it away from retrieval. That's a detector-coverage gap at the routing layer (id only; set stays blind).

## Body
- **Why a denylist and not a classifier:** 13 sentences, hand-verified, zero false removals by construction. A learned "unsafe advice" filter would misfire on negated advice exactly as the regex did (160/173 false hits).
- **Maintenance:** rerun `audit.py` whenever a pack is rebuilt and review only new hits (minutes). Add a rule to `rules.v0.x` when a new unsafe pattern is found, and the audit picks it up across all packs.
- **Scope gaps:**
  - the rules cover 17 topics, so unsafe text on uncovered topics (e.g., "pee on a jellyfish sting", tourniquets for ordinary cuts) is not audited;
  - format-1 packs and wiki-vital5/full-enwiki were not audited this cycle (next: the full enwiki shards Sonar proposes in QUEUE #6 are 18 GB, so audit the vital5 pack first);
  - PT text is only audited where the rule has PT patterns.
- **Relation to #46:** #46 fixes the hypothermia passage in the engine. This generalizes it; if both ship, #46's passage is simply one denylist entry.
- Off-the-shelf: none needed (the rules and checker are the bench's own `rnd/bench/safety/safety_check.py`).
