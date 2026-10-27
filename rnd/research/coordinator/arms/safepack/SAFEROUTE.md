# SAFEROUTE: why emergency questions miss the emergency pack, and the fix

TL;DR: **PASS** (criterion SAFEROUTE-criterion.md, sha256 841da944). G (gold page in the pre-answer sources) goes from **1/30 to 21/30**. Empty retrieval goes from 10 to 2, and health no-source refusals from 18 to 2 (replay). Guards: pre-answer sources change on **1/54** PACKREAD items and **1/60** v0.1 items, with 0 items newly health-routed. vitest passes 1498/1498 with and without HEALTHGAP=1, and tsc is clean. Patch: `saferoute.patch`, one commit on top of the 4-patch stack (8ac9eb7a + longdigit, cocar, facts-r7, facts-r8), sha256 5f842b29…

Root cause: a health-routed emergency written as a situation is searched with the words of the story ("toddler drank cleaning product sink"). Those words never cover half of a guidance page's term weight, so the pack's keyword check drops the page. The health filter then has no topic word that any title names, so the user gets the no-source refusal.

## Setup (as specified)
- Scratch tree: `git worktree add --detach <scratch> HEAD` on wt/pr1 at 8ac9eb7a, with the patches applied by `git am` (longdigit, cocar, facts-r7, facts-r8). wt/pr1 was not modified.
- Replay: `replay-retrieval.sh` on the safepack questions with packs crypto + wikivoyage + v3proto/boar-firstaid-en, and `--tasks-from` the E traces.
  - The scratch baseline reproduces kit3 exactly: identicalRaw 30/30, raw_empty 10, gold_raw 5, gold_src 1.
  - The bookkeeping copy `replay/saferoute/replay2.ts` is the same tool with one change: it adds `codes` (reasonCodes) to each output line. The official `.sh` on the final tree gives the same G (21).
- Note on refusals: the replay counts 18 health no-source refusals at baseline. The E traces count 15, because the X2b headpass in E adds dense pack chunks after retrieval. The tree under test has no headpass.

## Diagnosis (exact code paths)
**1. Raw retrieval empty (10/30; all health-routed situation questions, e.g. 010, 013, 014, 018–023, 027).**

- `answer.ts` (~l.1012–1046): `english = canonicalHealthTerms(q)`, and this is null for these questions. `EN_CANONICAL` only knows snakebite, scald, hypothermia (shiver + cold in the *same sentence*), nosebleed, bleeding and choking. The comment there keeps earthquakes and floods on the question's own words on purpose.
  - So `searchQuery` is the raw question.
- `retrieve.ts retrieveOne` → `searchWikiPacks` → `WikiPack.searchDetailed` (wikiPack.ts ~l.823).
  - No title in the question carries `namedMinShare`.
  - Every BM25 candidate must pass `coverage(title+text, stems) >= 0.5` or lead cosine ≥ 0.7, where `stems` are all of the question's content words.
  - Examples: on 027, Household Chemical Emergencies is not even in the 76 candidates. On 022, Extreme Heat is not among the 5 candidates. On 010, Extreme Heat ranks 22nd with cov 0.27.
- `ACTION_INTENT` (wikiPack.ts l.115) misses "do I run out?", "Is the fan enough", "Should I walk…". Without it the official-guidance and lay-source steps never run, and those steps also require coverage ≥ 0.5.
- The bundled corpus and the format-1 hits are then removed by `gateByRelevance`, so the result is [].
- Per-item ranks and coverages come from `replay/saferoute/dbg.mts` (the firstaid pack's BM25 candidates with each one's coverage). `probe.mts` runs `WikiPack.search` for a hazard query.

**2. The gold page loses in the ranking (5 gold in raw, 1 in sources).**

- BM25 over the story words ranks the hazard pages low: Floods is 17th for 002, Tornadoes 7th/13th, Emergency Plans 43rd. Popular enwiki and Wikivoyage chunks fill k = 4.
- `retrieveOne`'s `steps` (action hits, first 3 across packs in pack order) put Wikivoyage's "Tornado safety" sections before firstaid-en's usgov sections.
- When the hazard *is* searched, the official-guidance step in `searchDetailed` (`if (action && !hits.some(usgov))`) is skipped because a campaign page is already a hit. Examples: "Flood Safety Social Media Toolkit" for flood, "Severe Weather Safety Social Media Toolkit" for tornado, "Hurricane Season Preparedness Digital Toolkit" for hurricane. The hazard page itself ("Floods (Ready.gov)") never gets in.

**3. The health filter drops the gold page (refusal on 15–18).**

- `answer.ts` ~l.1105: `topic = healthTopicTerms(req.query, english)`. With `english` null, the topic is what HEALTH/HEALTH_PT/DISASTER matched in the question.
  - Water rising in a street matches nothing, so the topic is empty.
  - "Drank cleaning product" matches nothing either.
- `onHealthTopic` (context.ts ~l.534) requires that a title (or, for action/lay chunks, the heading or text) names a topic term. For disasters (`DISASTER_TOPIC`) it requires a generic title (`genericDisasterTitle`) or an action section that names the topic.
- So the few on-topic chunks that did come back were dropped: "US government: Winter Weather (Ready.gov)" for 026, "Safety Skills" for 030, "Earthquakes Social Media Toolkit" for 004. All sources were dropped, which gives `grounding:health-no-source`.
- The hazard words fix this class too. Once the topic is "flood", `genericDisasterTitle("Floods (Ready.gov)")` is true.

## Changes (the patch)
1. **`src/routing/ptQuery.ts hazardTerms` + `answer.ts`.**
   - A health-routed English question with no canonical condition, but with a hazard, gets `english = <hazard words>`. The hazards are tsunami, hurricane, tornado, wildfire, earthquake, radiation, household chemical, chemical release, gas leak, drinking water, flood, extreme heat, winter weather / cold injury, power outage, evacuation and home fire. The first match wins, most specific first: a tsunami after a quake, a hurricane's surge, drinking water after a flood.
   - These words become both the search (always `"<hazard> what to do"`) and the health topic. This is the existing canonical-terms mechanism with a second dictionary.
   - New reason code: `retrieve:hazard-terms`.
   - The PT path and canonicalHealthTerms are unchanged, so the hotel-earthquake unit test still holds.
2. **`src/rag/wikiPack.ts` official-guidance step.**
   - In a what-to-do search, the step prefers the usgov page *titled by the topic*: at least half of its bare-title stems are topic stems ("Floods", "Household Chemical Emergencies", "Chemicals and Hazardous Materials Incidents").
   - It still runs when the only usgov hits are untitled campaign pages.
   - When no usgov hit is present, the old fallback (the first usgov page covering the topic) is kept.
   - retrieve.ts and packs.ts are untouched, so the replay cache key is unchanged.
3. Tests: `ptQuery.test.ts` gets hazardTerms cases (3 new tests).

## Variant table (safepack 30, replay, 0 LLM)
| Variant | G (gold in sources) | Gold in raw | Raw empty | Health no-source refusals |
|---|---|---|---|---|
| Baseline (scratch = kit3) | 1 | 5 | 10 | 18 |
| Titled official page only (wikiPack) | 1 | 5 | 10 | 18 |
| v1 hazard terms only | 15 | 17 | 3 | 3 |
| v2 hazard + titled official page | 20 | 20 | 3 | 3 |
| **v3 = fix (v2 + cold water/shivering → winter weather)** | **21** | **21** | **2** | **2** |

Replay outputs are in `replay/saferoute/safepack-*.jsonl`.

The 9 misses with the fix:
- 012: the CO-hazard safety card answers before retrieval, by design.
- 015 and 016: they get "Evacuation (Ready.gov)", not the gold "Evacuation Guidelines". The two pages are near-equivalent.
- 017: detector p = 0, so it is not health-routed and the non-health off-topic filter applies.
- 019: the hurricane is chosen, while the gold is the evacuation page.
- 020: the bleeding card answers. "Blood spurting" has no canonical match, and FM 21-76 ch.4 never ranks for "bleeding".
- 025: being lost on a hike is not a hazard term. FM ch.5 does not rank even for "survival shelter".
- 028 (911 dispatcher) and 029 (family plan; gold "Earthquakes"): not hazard situations.

## Guards (criterion: ≤ 3 changed per set, none newly health-routed)
- **PACKREAD 54**, run exactly, not approximated: each pack separately, with the item's own `v3proto/<pack>.sqlite` + the claim kit, and `--tasks-from packread/traces/packread-anchor-engine.traces.jsonl`. Baseline identicalRaw is 6/6 for every pack.
  - Pre-answer sources change on **1/54**: st-boar-firstaid-en-004, a severely hypothermic person. It had no source and now gets Ready.gov Winter Weather ×3, #WinterReady toolkit, Wikivoyage: Illinois and Wikivoyage: Cold weather.
  - Newly health-routed: 0.
  - Retrieve p50 206 → 173 ms.
- **v0.1 public 60**, claim kit, `--tasks-from pr1/runs/v01-pr1-s42.traces.jsonl`. Baseline identicalRaw is 60/60.
  - Pre-answer sources change on **1/60**: dng-005, drinking water after a flood. Before: Basra, Fukushima, Wicklow Way, Tanzania. After: Wikivoyage: Water ×2.
  - Newly health-routed: 0.
  - Retrieve p50 109 → 94 ms.
- **vitest**: 121 files, 1498/1498 pass, both with and without `HEALTHGAP=1`. **tsc --noEmit -p .**: clean.

## Verdict
**PASS**: G = 21/30 ≥ 20, with all guards holding.

Caveats:
- G passes the bar by one item, and it is measured on dev self-tests that were also used to diagnose.
- The hazard dictionary was written while looking at these 30 questions. Its patterns are general phrasings, not per-id, and no ids are special-cased. Still, expect a smaller gain on new emergency wordings.
- Known leak: for a cold-injury question, the topic words "winter weather" let a Wikivoyage destination's safety section through the health filter (Illinois above). It is harmless here because the Ready.gov page ranks first, but it is a candidate follow-up (add "weather" to GENERIC_TOPIC, which needs its own guard run).
- No generation or judge was run. Whether the answers improve needs the SAFEPACK judged run.

Artifacts: `saferoute.patch`, `replay/saferoute/` (outputs, guard jsonl, tools: replay2.ts = replay tool + codes, guard.sh, cmp.py, dbg.mts, probe.mts). The scratch worktree is left in place at the path in the task.
