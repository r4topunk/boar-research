# TRAVELSEL on cut 3 (retrieval engineer, 2026-10-05, DEV; L0 only, no judge, nothing pushed)

TL;DR: **L0 FAIL after the one allowed revision** (round 1: 0/3 gain; round 2: 1/3 gain, bar is >= 2). Everything else passes (0 lost, only travel-routed contexts changed, venues 6/6 and GPS identical, p50 0.98x). The gate fails on structure, not on tuning: with the frozen gold facts the bar is reachable by at most 1 of the 3 targets (see "Why it fails"). The coordinator decides whether to go to L1 anyway or to change the arm.

- **Patch:** `travelsel-on-cut3.vs-0cfd4a77.patch` (cut 3 + TRAVELSEL round 2), sha256 `fb2fdd1d067a378a78824372e3557e568f1a1fab741592819cbf641e5d7ab6af`. Applies cleanly to a fresh `git archive 0cfd4a77`; tsc clean there; vitest **1307/1307** (cut 3 is 1285, **+22 units**).
- Branch `coord/travelsel` (worktree `wt/travelsel`, from `coord/final` = cut 3 c5249560), 2 local commits (84c6a273 round 1, then round 2), never pushed.
- Criterion `TRAVELSEL-criterion.md` untouched (sha256 e4ffcb5c..., matches `TRAVELSEL-criterion.sha256`).

## Pre-registration
- `gold-facts.json` sha256 `75aaaac1f471827cc6d85cdfdd308daebaac8f41647ff7b960bce2646835a7ed` (`gold-facts.sha256`), written 12:51 -03, before any replay of this arm; never edited. Targets: trv-004 (Lisbon airport), vit-trv-003 (Chiang Mai -> Pai), trv-002 (Brazil voltage/plugs). Hit rule as cryptosel: any alternative, sentence >= 60% of its word 4-grams (regex for none here) in the placed context.
- Process: the cut 3 base replay ran (12:55) before the arm existed, then I read the base contexts of the 3 targets. That showed two flaws in my own gold file, below. I did not edit it. `gold-facts-supplement.json` is a **post-hoc, non-gating** file written after round 2 to show what the frozen one cannot.

## Mechanism (`src/rag/travelSelect.ts`, pure; hooks in `wikiPack.ts`)
1. A question that asks a practical slot (specific phrases: get from/to/there, get around, safe/scams, plug/voltage, currency/ATM/tipping, visa, tap water/vaccination) and is not a health question (`isHealthQuestion`) and not an ACTION_INTENT question gets a slot. Anything else gets null and nothing changes.
2. In a Wikivoyage **destination** article (has a `## Get in` section; topic and airport guides don't) that the question reaches **by name** (title route, `articlePassages`), passages of the matching section sort first: Get in / Get around / Stay safe / Stay healthy / Electricity (parent Cope) / Money (parent Buy). Visa -> Get in. Preferred passages are exempt from the 0.15 score floor.
3. Same budget: still lead + 2 passages per named article, same compressor, same fusion.
- **Round 2 (the one revision; one rule beyond the criterion's text):** a "how do I get from A to B" question counts as a travel question in `titlesInQuestion`, so B (after "to") is its destination and goes first. Without it Pai is never retrieved for vit-trv-003 (the question is not a travel question for `isTravelQuestion`; Pai's share of the question is < 0.5, so only Chiang Mai, the origin, was).

## L0 (stub-LLM replay, real engine, kit A + V-exact places kit (`shared-data/poi/kit-vexact`), no detector; v0.1 EN 60 + V-exact 11 = 71 items; `tools/`)
| bar | round 1 | round 2 (final) |
|---|---|---|
| gold fact in context on the 3 targets, >= 2 gain, 0 lose | trv-004 no, vit-trv-003 no, trv-002 already in base: **0 gain, 0 lost, FAIL** | **vit-trv-003 gains** (Pai Get in > By bus: minivans 150 baht hourly from Chiang Mai), trv-004 no, trv-002 already in base (not a gain): **1 gain, 0 lost, FAIL** |
| other contexts byte-identical except travel-routed items | 2 changed (vit-trv-003, trv-002), both travel-routed; other 69 identical. PASS | same 2 changed; other 69 identical (29 travel-routed items in base, 27 untouched). PASS |
| travel-routed item loses its gold sentence | none (goldhit-sent 1 -> 1). PASS | none (1 -> 1). PASS |
| venues 6/6, GPS city 3/3 unchanged | all 6 venue items (food-001/002/006, vx-003/4/5) identical context + route. PASS | same. PASS |
| retrieval p50 <= 1.2x | one-shot 1.012 | **0.979x** (p50 of per-item min over 3 interleaved runs: 91.9 -> 90.0 ms; per-run ratios 0.947/0.972/1.009). PASS |
Venue 6/6 and GPS 3/3 are text-scored on real answers; under the stub, "unchanged" means the placed context and route reason codes are byte-identical, which implies the same answer inputs.

## Why it fails (frozen gold, structural)
- **trv-004:** cut 3 retrieves the **"Lisbon Airport"** guide (the question names "Lisbon airport"; "Lisbon" is inside the longer title), not "Lisbon". My frozen gold sentences are in the **Lisbon** article (Get in > By plane), which this question never reaches, so no selection rule on the named article can put them in. The airport guide has the fact too (`Ground transportation > By train`: Red Line terminates at the airport, ~20 min) but has no "Get in" section, and "Ground transportation" is not in the criterion's heading list, so the literal mechanism leaves it untouched.
- **trv-002:** my second alternative (the plug sentence) is already in cut 3's context, so it can never "gain"; the needed voltage sentence ("uses both 110 and 220 volts") sits in the other chunk of the same `Cope > Electricity` section, dropped by the one-passage-per-section rule. Round 2 context: only the Electricity plug chunk survives; it **loses** the Buy > Shopping chunk ("dual voltage... voltage varies by state"), 235 -> 115 tokens. Net on the fact: not gained, a voltage mention lost. L1's "no changed item down >= 1.0" would test this.
- **vit-trv-003:** the accident warning (Pai, Get in > By road) is not in the context: the By bus chunk outscores By road; a Chiang Mai "Get in > By train" chunk also rides along (low value).

## Post-hoc, non-gating (`gold-facts-supplement.json`; round 2 as in the patch)
Round 2 as shipped: trv-004 0, vit-trv-003 0 (accident/winding road not placed), trv-002 0 (voltage sentence not placed).
**Exploratory variant, not in the patch** (a throwaway tree, 3 more lines): treat "Ground transportation" as a Get in section and a guide with it as a destination. Result: **trv-004 gains the Red Line metro fact** (supplement), 3 contexts change (trv-004, vit-trv-003, trv-002), all travel-routed, venues identical, p50 0.82x one-shot. It still scores 1/3 on the frozen gold (no frozen fact lives in "Lisbon Airport"). It is one more rule than the criterion names, so I did not put it in the patch.

## UNKNOWN / for the coordinator
- Whether to run L1 on the round 2 patch anyway (L0 bar failed; the criterion stop rule says one revision, none after L1). The only measurable gain is vit-trv-003's minivan fact; the stub can't say whether the 4B uses it.
- Options I did not take (each is a rule the criterion doesn't name): (a) "Ground transportation" as a get-in heading (above); (b) allow two chunks of the preferred section (would put the 110/220 sentence in for trv-002); (c) for an airport guide, also read the city guide's Get in.
- Held-out V-para travel items (8) not looked at; the rule fires on any destination-named get-in/safety/plug/money/visa question, so its V-para exposure is unknown.
- Size: no new model call; one extra regex pass per named Wikivoyage article, and `isHealthQuestion` called per titleHits article.

## Files
`tools/` (`mktree.sh`, `replay.sh`, `l0.py`, `cmp.py`, `lat.sh`, `latp.py`, `stub-server.mjs`, `dumpart.mts`, `dumpsec.mts`, `headings.mts`, `items71.jsonl`); `L0-round1.txt`, `L0-round2.txt` (both with the post-hoc supplement block); `traces-cut3.jsonl`, `traces-cut3+travelsel-r1.jsonl`, `traces-cut3+travelsel-r2.jsonl`. Replay needs the stub server: `node tools/stub-server.mjs 18510 <workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf`; requests file = cryptosel's 71 requests with runId `ts` and the GPS fixes of vx-003/4/5 (Berlin, Lisbon, Tokyo) added from bench-vslice.
