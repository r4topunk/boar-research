# exp-37: symptomatic CO card (Forge's sanity find): verification kit (Sonar, 2026-10-03 night)

TL;DR:
- **Gap:** "Since we started the generator in the garage my head hurts and I feel dizzy and sick. What should I do?" → detector p = 1.0 → health route → **no CO card** → generic no-source line. The CO trigger needs the words "carbon monoxide", "gas heater/leak" or "generator inside/indoors".
- **Owner split:** Compass writes the delta on shipcut1, reusing `coHazard.ts`. Sonar verifies with this kit before it goes to Forge (ship cut 1).
- **Baseline (health13)** (`cokit.mts`, A = B = health13):
  - CO probes: 0/8 positives get the CO card; 6/6 negatives correct.
  - Labelled `cards-en`: CO recall **4/19**, wrong CO cards 0.
- **The delta's bars** (EN, L0):
  - Forge's sentence + the 7 positive probes get `co`, and the 6 negative probes don't;
  - `cards-en` CO recall rises, with 0 wrong CO cards on non-CO items;
  - every NEW CO card on the EN dev pools (aligned-en 1010, terse-live EN 213, Compass emergency-dev EN 105) is hand-checked and justified (a real CO exposure).
- **Usage:** `tsx cokit.mts <health13 tree> <delta tree>`.

## Result: Compass's delta PASSES (2026-10-03 night)
- **Delta:** compass/exp/co-hazard/co-exposure-delta-vs-shipcut1.patch, sha256 **ff2be8f04f8a9b5c6c6793c119e0268ecca8213ee1cf66ab9dc8f83941752b62**.
  - Full patch vs 0cfd4a77: shipcut1-co-exposure.vs-0cfd4a77.patch 8b10cdf3…. Both hashes verified.
  - A = shipcut1 (the full patch with the delta reversed); B = with the delta.

| Check | shipcut1 | + delta |
|---|---|---|
| probes (8 positive + 6 negative) | 6/14 (0/8 positives) | **13/14** (p-multi missed: symptoms in a later turn, by design) |
| cards-en CO recall (19 labelled) | 4/19 | **13/19** |
| wrong CO card on non-CO cards-en items | 0 | **0** |
| NEW CO cards, EN dev pools (aligned-en 1010, terse-live EN 213, Compass emergency-dev EN 105) | — | **3, all real CO exposures** (generator in garage + confused dad; whole family headaches since the heater went on; alarm next to the cabin heater + 3 with headaches + vomiting) |
| Compass emergency-dev positives (cardpick.mts) | right 28 / wrong 11 / generic 141 | right 29 / wrong 11 / generic 140: no new wrong card (the 11 are the known mapping cases) |

- **Remaining CO misses** (6/19; follow-ups for Compass, not blockers):
  - device in an earlier turn, symptoms now (3);
  - "engine running" / "engine exhaust" as the device, and "barely waking up" / "slurring" as symptoms (2);
  - CO alarm/detector + symptoms with no device named (1). Arguably the clearest CO case of all.

## exposure2 check (2026-10-03 night): PASS except one new cross-turn false fire → fix requested before Forge
- **Patches:** cumulative delta on shipcut1 f103f80d…; full 7873ba7c…; incremental 99b55b7d….
  - The cumulative delta applied to shipcut1 equals the full patch (verified).
- **Kit** (A = exposure1, B = exposure2), with 7 adversarial probes added (`probes2.jsonl`):
  - CO recall 13 → **18/19**, wrong CO 0;
  - EN dev pools: 1 new CO card (tl-en-0040 "co alarm going off and I have a headache", real);
  - real multi-turn cases now caught (p-multi, x-prev-real, x-car-cold).
- **New false fire:** `x-prev-size`. "what size generator do I need for my garage workshop?" → "unrelated, but I have a headache from stress, what can I take?" gets **co**.
  - Cause: `isCoExposureAcrossTurns` accepts `hazardContext(previousTurn)`, the PLANNING trigger, so a device+space mention with nothing running counts as an exposure.
  - **Requested fix:** in the cross-turn path, the previous turn must say the device is IN USE (running, on, started, left on, been using, burning, lit…) or be a CO alarm going off. A shopping/sizing/how-to question doesn't count.
- **Pre-existing in shipcut1, not exposure2** (noted for Compass, not blockers):
  - "how do I test my carbon monoxide alarm?" → co (the literal words); a card only shows on the health route.
  - Shopping for a gas heater → "dizzy all week, probably the flu" → co (the newest single-turn condition fallback).

## exposure2.1 (2026-10-03 night): PASS → forwarded to Forge (replaces exposure1)
- **Patches:** cumulative on shipcut1 **d66cadac0121e92adda83b59b6b05daced12b1343d5cd54c45a3fe4e4ca01274**; full 261ab0fa…; incremental 904d8002….
  - Shas verified; cumulative applied to shipcut1 == full.
- **Kit:** A = shipcut1, B = exposure2.1; 25 probes, incl. 4 more lookalikes for the in-use rule.

| Check | shipcut1 | exposure2.1 |
|---|---|---|
| probes | 13/25 | **23/25** (misses = the 2 pre-existing shipcut1 cases) |
| cards-en CO recall | 4/19 | **18/19** (miss: ce-0014, alarm two turns back) |
| wrong CO cards | 0 | 0 |
| NEW CO cards, EN dev pools (1,328) | — | 4, all real exposures (en-0245, tl-en-0040, tl-en-0173, ed-en-091) |
| cardpick, Compass 180 positives | 28 right / 11 wrong | 29 / 11 (no new wrong) |
| cardpick probes | 26/27 | 27/27 |

- The cross-turn false fire is fixed: x-prev-size and x-onoff → generic; x-lit-candle (fireplace outside) → generic.
- Real cross-turn cases → co: x-prev-real, x-car-cold, x-heater-now, x-alarm-prev.

## Re-check on Forge's SHIP CUT 1b itself (shipcut1b.vs-0cfd4a77.patch 6f5936d7…; components incl. co-exposure ff2be8f0)
- **shipcut1 → 1b (as built):**
  - Forge's sentence → co;
  - probes 20/25 (all 8 single-turn positives; misses = 2 pre-existing shipcut1 + 3 cross-turn cases exposure1 doesn't cover);
  - CO recall 4 → 13/19, wrong CO 0;
  - EN dev pools: 3 new CO cards, all real;
  - cardpick: no new wrong card (11 → 11), right 28 → 29.
  - **PASS: nothing comes out of the cut.**
- **Optional upgrade:** `co-exposure2.1-delta-vs-exposure1.patch` 904d8002… applies cleanly on 1b (no fuzz/offset). coHazard.ts and conditionCards.ts then equal the verified exposure2.1 tree.
  - 1b → 1b + 2.1: probes 20 → 23/25, CO recall 13 → 18/19, 0 wrong, 1 new CO card (real: "co alarm going off and I have a headache").
