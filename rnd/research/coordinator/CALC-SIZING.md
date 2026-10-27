# CALC-SIZING: is a units / time-zone / date / percent calculator worth building next?

Analyst pass, 2026-10-05. Read-only: regex scans, my own arithmetic, stored cut 3 traces. No runs, no judge, no LLM calls. Never opened: blind/, rnd/veil/, bench v0.2, V-para, the `*-blind` chat-slice dirs.

## TL;DR
- **Recommendation: SKIP as a bounty lever.** The Δ ceiling on bench v0.1 EN is **+0.000**: 0 of 57 judged items are a new calculator target. The three calculator-shaped items (vit-trv-004, vit-sci-003, vit-sci-002) are already fixed or correct on cut 3.
- **Dev traffic share is about 0.2 %**: 3 of 1,470 EN dev questions (the Sonar 1,328 + chat dev 66 + bench 60 + V-slice 16). The Sonar pool is detector-negative text built for routing tests, not real traffic, so the real rate is UNKNOWN.
- **Part of the idea already exists.** `src/routing/calculators.ts` has C/F temperature, fuel economy, Naismith, currency with a user-given rate plus tip, battery Wh and trip water. `smallTalk.ts` answers "what time/date is it". Still missing: other unit conversions, percent-of, date arithmetic, time-zone difference.
- **No evidence the 4B botches conversions it states.** Across all cut 3 v0.1 + V-slice traces, 12 "X km (Y miles)"-style pairs, 0 off by more than 3 %. The only unit-related value is VG threshold questions in another unit (about 7 of 240 VG probes).
- **If you want it anyway, build an MVP (about 1 agent-day) for product polish, not for the ratio.** Order: percent + units, date arithmetic, time zone via `Intl`. Criterion drafted below, but L1 is vacuous on v0.1.

## Method and pools (EN only)
| Pool | n | Notes |
|---|---|---|
| bench v0.1 EN | 60 (57 judged) | `boar-eval/bench/v0.1/questions.public.jsonl` |
| V-exact / V-slice | 11 + 5 | `rnd/research/compass/exp/bounty-eval/` (vit-trv-004 + venue/overview items) |
| Sonar EN dev | 1,328 | = aligned-en 1,010 + terse-live EN 213 + emergency-dev EN 105 (the files `tools/vg4-gate.mts` reads) |
| Chat dev (VG L0 slices) | 66 | chat-slice v0, v1-fresh, v2-fresh (22 EN each) |
| Probe sets, questions only | 475 | arithmetic 95, water 90, VG probes 30 + 90 + 120 (`arms/probes`, `vg-probe-q`, `vg-probe-q2`) |

I ran regexes for unit, tz, date, percent and cooking cues, then read every hit by hand.

## Counts per sub-type (deterministically answerable from the question alone)
| Sub-type | bench v0.1 | V-exact | Sonar 1,328 | chat dev 66 | probes (questions) | Examples |
|---|---|---|---|---|---|---|
| Unit conversion, with the number in the question | 0 | 0 | 0 | 0 | 2 arithmetic (arh-050 oz in 2 lb, arh-042 cups in 500 g: ingredient-dependent) | arh-050 |
| Unit conversion inside a VG threshold or compare | 0 | 0 | 0 | 0 | about 7 of 240 VG probes need another unit (vq-013, vgq-053, vgq2-066, -090, -091, -109; vgq-068 "in miles"); 4 are pure unit comparisons (vq-021, vgq2-056, -114, -003) | vq-021, vgq2-114 |
| Time-zone difference or "time in X" | 0 | 0 | 1 (en-0720 "what time is it in Sydney now"; needs the phone clock) | 0 | 0 (vq-020 is a fact) | en-0720 |
| Date arithmetic (days between, weekday, age) | 0 strict; lan-rsn-006 and lan-rsn-007 are derived from recalled facts | 0 | 0 | 0 | 1 (arh-048 Roman Empire span, fact-dependent) | none |
| Percent / tip | 0 | 0 | 1 (en-0709 "what's 15 percent of 84"); en-0690 "how much should I tip in the US" is a customs fact, not a calculation | 0 | 0 | en-0709 |
| Cooking units | 0 | 0 | 0 | 0 | 1 (arh-042, shared with row 1) | none |
| Currency (excluded: rates go stale) | 0 | 0 | 1 (en-0692) | 0 | 0 | en-0692 |
| Already covered by an existing calculator | 3: vit-trv-004 (travel), vit-sci-003 (AR rate-time), vit-cry-009 (AR ceil-div, not fired on cut 3) | 1 (vit-trv-004) | 2 (en-0507, en-0571: distance between two places) | 0 | 95 arithmetic, 0 new | n/a |

Net new calculator-answerable questions in the real-ish pools: **3 of 1,470 (0.2 %)**: percent 1, time-now 1, a currency item that is out of scope. The synthetic "aligned" set was written as detector negatives (diverse non-emergency chat), so a 0.2 % hit rate there suggests low demand, but it is not a measurement of live traffic.

## How cut 3 answers the bench items today (stored traces cut3-confirm s44/s45; my own arithmetic)
| Item | Cut 3 answer | Verdict |
|---|---|---|
| vit-trv-004 (V-exact too) | `answer:calculator-travel-distance`. 1,107 km = 687 mi (checked); x1.3 = 1,439 km; x2 = 2,880 ~ 2,900; 57.6 d ~ 58 d at 25 km/d; 288 h at 5 km/h. Byte-identical in both seeds and in V-exact. | **correct** |
| vit-sci-003 | `answer:calculator-rate-time`: 43.3 + 40 = 83.3 s. | **correct** (+3.33 rubric already banked) |
| vit-sci-002 | VG compare: Japan 339 vs Germany 230 per km2. 339 - 230 = 109 (s45: 338 - 230 = 108), 339/230 = 1.47 ~ 1.5. | **correct** (+1.08 already banked) |
| lan-rsn-006 | "1337 to 1453, spanning 116 years". 1453 - 1337 = 116. | **correct**; the model did the subtraction right |
| lan-rsn-007 | "built in 1961 and came down in 1989" (28 years is not stated). | **vague**; no calculator gap, the question asks for the two years |
| lan-rsn-002 | 828 m vs 1,642 m; s45 says "below the water surface by roughly 814 meters" (1,642 - 828 = 814, correct); s44 gives no number. | **correct arithmetic**; the fact "1,642 m below sea level" is wrong (it is depth), which a calculator cannot fix |
| vit-cry-009 | "156 validators ... same after EIP-7251" (10,000/64 = 156.25, so 157 is needed; 10,000/2,048 gives 5). | **wrong**; it needs the constant from the pack (AR scoped out), not a units/date calculator |

So the arithmetic-shaped losses on v0.1 are exhausted: AR, VG and the travel calculator already took them. This is selection: those tools were built after those items were found.

Side check on stated conversions: 12 parenthetical pairs (km to mi, m to ft, kg to lb, C to F) across cut 3 v0.1 s44/s45 + V-slice s42/s43. Largest error under 3 % (rounding), e.g. lan-exp-006 5,895 m = 19,340 ft (true 19,341), lan-cmp-005 "5 to 6 m (16 to 20 ft)". A post-hoc unit-pair guard would have fired 0 times.

## Δ ceiling and coverage
| Quantity | Value | Basis |
|---|---|---|
| Δ ceiling on v0.1 EN | **+0.000** | Σ w·max(0, target - cut3) over new targets = 0 items; the three calculator-shaped items are at or above the Haiku target |
| Δ ceiling if the 4B botched lan-rsn-007 (28 years) | at most +0.001 | one more derived sentence; it is not a calculator route |
| Dev traffic covered | about 0.2 % (3/1,470) | real rate UNKNOWN; the Sonar pool is synthetic |
| v0.2 / bounty mix | UNKNOWN | held out, hashes only; I did not open it. v0.1 was written as knowledge, explanation, comparison and danger items, so calculator content on v0.2 is probably similarly rare |

## Offline feasibility per sub-type
| Sub-type | Offline? | Size / data | Router risk | Verdict |
|---|---|---|---|---|
| Length, mass, volume, speed, area, temperature (C/F exists) | Yes, exact constants | under 2 KB of code | Low with "N unit to unit" or "N unit in unit". Must not fire when the question has no number ("how tall is Everest in feet" is a lookup) | easy |
| Cooking units | Volume to volume (cup, tbsp, tsp, ml, oz) exact; cup to gram needs an ingredient table (about 15 entries) and is ambiguous | about 1 KB | Medium: "500 g flour in cups" depends on flour type | volume only; grams optional |
| Percent, tip, discount, split | Yes | trivial | "15%" appears in health and finance text; needs "of", "tip on", "off" frames and no health or crypto context | easy |
| Date arithmetic (days between, weekday, age, +N days) | Yes, pure code; "today" from the phone clock (`deps.today`, already used by `todayLine`) | under 2 KB | Low with explicit dates; "how old is X" needs a lookup, so only when the birth date is in the question | easy |
| Time zone ("9 am in Y is what in X") | Yes through `Intl.DateTimeFormat({timeZone})` (ICU on Android; Hermes Intl needs checking on the target RN version) plus a city to IANA alias table of about 300 entries (about 10 KB). No bundled DST rules needed. Fallback: a table of about 60 zones with the US / EU / AU / NZ DST rules | about 10 KB | Medium: the home zone comes from the phone; "now" depends on a correct clock; DST changes after the build are rare | feasible; check Intl on device (UNKNOWN) |
| Currency | No (rates go stale). Keep the existing given-rate form | n/a | n/a | exclude |

## Recommendation
**Skip building it now.** Reasons (the profile's own antipatterns apply: scope explosion, tool before demand):
1. v0.1 can't show a gain: no new target items, so Δ ceiling = +0.000 and the L1 gate "targets up" can't be satisfied or tested.
2. Dev share about 0.2 %, on a synthetic pool. No traffic evidence of demand.
3. The compact model's stated conversions are fine (12/12), so there is no confident-wrong to remove (cw is already 4 to 5 per seed).
4. The remaining v0.1 headroom is knowledge (M5) and thin answers (M6), which a calculator cannot touch.

**Reopen if** (a) the coordinator gets a real or bounty-style question sample (not written by us) with at least 1 % calculator-shaped questions, or (b) the product side wants a demo-polish feature. Then build the MVP in this order (about 1 agent-day, one commit each):
1. Percent + units (length, mass, volume, speed, area) with the exact constants, reusing `parseNumber` and the `calculate()` registry. Cooking volume-to-volume only.
2. Date arithmetic (days between, weekday of a date, age from a birth date in the question, +/- N days).
3. Time-zone difference through `Intl`, only for cities in a bundled alias table.

Cheaper spin-off worth its own tiny item: **VG unit normalisation** (v4 abstains when the threshold unit differs from the answer's unit). About 7 of 240 probe items (3 %) would be checked, but the VG fire rate on real traffic is unknown, so treat it as an optional VG v5 add-on.

## Draft criterion (to freeze with sha256 before any run; applies only if the MVP is built)
**Arm CALC-MVP** (sub-types in the build order above; EN only; never on health, danger, card or PT/ES paths; never fires without a number or date in the question; no currency).

**L0 (deterministic, minutes, no generation):**
- C0. Exactness tests: at least 60 unit tests (at least 40 conversions incl. rounding, edge and negative values; at least 10 date cases incl. leap years and month ends; at least 10 percent cases) with exact expected strings or values; tz: at least 20 cases across DST boundaries (US, EU, AU), compared with Node `Intl` (desktop) and a fixed clock.
- C1. Router precision/recall on a **fresh blind set** written by an independent subagent that has not seen the regexes: 25 positives per sub-type (at least 100 total, with paraphrases, word numbers, "how many X in Y") and at least 150 negatives (lookups with no number, health dose questions, "15%" in finance or health text, history years, travel distance, crypto). Bars: recall at least 80 % per sub-type, **false fires at most 1 of 150**. Set kept outside `boar/rnd` readers until scoring; burned for tuning after the first run.
- C2. 0 fires on the 1,328 EN Sonar dev messages and the 66 chat dev, except messages a reviewer labels true positives (expected: en-0709, en-0720); 0 fires on the 95 arithmetic and 90 water probes beyond what AR/SC already handle; 0 changes on the stored cut 3 v0.1 + V-slice answers (the engine must be byte-identical on all 57 items; every other calculator keeps its route).
- C3. Reviewer (fresh Opus): reads every L0 positive answer and all fires on C2; pass = 0 wrong, 0 misleading.

**L1 (v0.1 changed items only, judge.v1-med, s44 + s45):** the expected changed set is **empty**, so L1 degenerates to the identity check "0 changed items, byte-identical to cut 3". Gates, if any item does change: targets up (mean rubric Δ at least +1.0), no changed item down by 1.0 or more, unsafe 0 (safety v0.9.1), cw not up, whole-bench Δ at least 0. **No ratio claim**; report as polish with "no v0.1 target; v0.2 untouched".

**Latency:** under 5 ms regex; 0 tokens on a fire (as the travel calculator).

**Disclosure:** the motivating hits (en-0709, en-0720, VG unit probes) are DEV; no claim on v0.2.

## UNKNOWN
- Real-traffic share of calculator questions; the bounty judge's mix and v0.2 content (not opened).
- Hermes `Intl` time-zone support on the shipping Android RN version.
- Whether the 4B's own stated unit conversions stay accurate at the long tail (only 12 pairs were seen).
