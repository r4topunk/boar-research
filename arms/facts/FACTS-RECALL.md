# FACTS r2: trigger recall and precision on a blind fresh-phrasing set (L0)

TL;DR: on 40 fresh fact questions, **recall is 22/40 = 55%**, and **precision is 22/27 = 81%** over all fires. **False positives: 2/20 near-misses**, and both print a wrong fact. The biggest single miss cause is the r2 capitalisation rule: **0/10 lowercase questions fire**, including one-word country names. Capitalised questions alone score 22/30 = 73% recall. Of the 27 fires, 5 are wrong: 3 stale populations and 2 false positives.

- Set: `recall-set.jsonl` (60 items: 40 fact, 20 near-miss). Written blind, before any FACTS code or data was opened. sha256 `414e4de21895b3366f3013986916d7f67af3c54907b2322b6d10002d29451297` (`recall-set.sha256`), frozen before Part 2.
- Engine: wt/facts `24cd66ef`, asset `facts.v1.json` r2 (`f4d3ab2e…`). `factsAnswer()` was called through the desktop-node adapter's tsx, the same way `tools/probe_r2.mts` calls it. Deterministic: no network, no LLM, no judge. wt/facts was not modified.
- Scoring (frozen in the task): a fact question counts as correct only if it fires and the answer contains `expect` (a number within 3% or a matching name). A near-miss that fires counts as a false positive.

## Numbers

| metric | value |
|---|---|
| fact questions fired | 25/40 |
| correct fires (recall) | **22/40 = 55.0%** |
| precision (correct / all 27 fires) | **22/27 = 81.5%** |
| false positives (near-misses) | **2/20 = 10%** |
| lowercase questions fired | 0/10 |
| capitalised questions: recall | 22/30 = 73% |
| comparison questions ("which is bigger/longer/more") correct | 0/3 |

## Misses (18)

| id | question | output | cause |
|---|---|---|---|
| f05 | what's the size of brazil | no fire | lowercase, and "size" is not an area cue (the capitalised form also gives no fire) |
| f11 | how high is mont blanc | no fire | lowercase rule (the capitalised form fires 4,806 m) |
| f16 | how long is the amazon river | no fire | lowercase rule (the capitalised form fires 6,400 km) |
| f21 | what is the official language of egypt | no fire | lowercase rule (the capitalised form fires Arabic) |
| f25 | what continent is peru on | no fire | lowercase rule (the capitalised form fires South America) |
| f29 | how tall is kilimanjaro | no fire | lowercase rule (the capitalised form fires 5,895 m) |
| f33 | what currency does the uk use | no fire | lowercase, and alias not matched: "UK" is no alias, and "the UK" is unreachable because n-grams drop "the" |
| f34 | how long is the danube river | no fire | lowercase rule (the capitalised form fires 2,850 km) |
| f36 | what language do they speak in argentina | no fire | lowercase rule (the capitalised form fires Spanish) |
| f38 | what is the population of canada | no fire | lowercase rule (the capitalised form fires 40 M (2023), within 3%) |
| f14 | Which is bigger, Canada or the United States? | no fire | template not matched: "bigger" is in COMPARE but in no lexicon. "Which is bigger by area, …" fires correctly |
| f26 | Which is longer, the Nile or the Amazon? | no fire | alias not matched: "Amazon" alone is not indexed, and "the Amazon" is unreachable. "…or the Amazon River?" fires correctly |
| f37 | Which country has more people, China or India? | no fire | alias not matched: Q148 is labelled "People's Republic of China" and has no "China" alias, so only India resolves and the comparison falls through |
| f18 | How tall is the Eiffel Tower? | no fire | entity not in table |
| f39 | How high is Mount Fuji? | no fire | entity not in table (neither "Fuji" nor "Mount Fuji") |
| f15 | What is the population of India approximately? | "population 1.33 billion (2020)" | wrong value: stale. 1.43 B expected (−7%) |
| f22 | How many people live in Nigeria? | "population 211.4 million (2021)" | wrong value: stale. 223 M expected (−5%) |
| f31 | Approximately what is the population of Mexico? | "population 132.3 million (2024)" | wrong by the frozen rule (+3.4% vs 128 M). Borderline: my `expect` is the weak side here (UN 2024 ≈ 131 M) |

## False positives (2/20)

| id | question | output |
|---|---|---|
| n07 | How tall is Paris Hilton? | "Paris (capital and most populous city in France): elevation 48 m" (person named like a place; "Paris Hilton" is not in the index, so "Paris" resolves) |
| n12 | What is the area code for London? | "London (…): area 1,572 km²" ("area" cue matches inside "area code") |

The other 18 near-misses did not fire: why/history/food/safety/visa/weather/currency-exchange questions, "How many people live in Michigan?", "What is the population of Georgia, the US state?" (HOMONYMS works), "What is Jordan Peterson's height?" and "How tall is Georgia May Jagger?".

## Reading: dominant miss causes

1. **Lowercase rule: 10/18 misses, the largest cause.** r2 made multi-word names require capitals. Lone words already needed a capital, so even "egypt" and "canada" fail. Casual phone typing loses the whole tier.
2. **Alias not matched: 3** (UK, Amazon, China). `titleCandidates` drops "the", so the "the X" aliases are dead. China is missing as a short name altogether, a high-traffic gap.
3. **Wrong value: 3 fires.** The ≥ 2020 population gate still lets 2020/2021 figures through, which are 5–7% stale for India and Nigeria. Mexico is borderline.
4. **Template not matched: 2** ("bigger" alone, "size"). Comparisons fire only with an explicit property cue, so 0/3 comparisons scored.
5. **Entity not in table: 2** (Eiffel Tower, Mount Fuji). Coverage of famous landmarks is thin. False positives come from person-name prefixes (Paris Hilton) and compound nouns (area code). Both print confident wrong facts.

UNKNOWN: the set is 60 items written by one author (Opus), so the CI is wide (55% ± ~15 pp). Real user casing on the phone is not measured: phone keyboards auto-capitalise the first word only, so the lowercase share could be higher or lower than 10/40. My `expect` values come from memory, and f31 is the one I would not defend at 3%.
