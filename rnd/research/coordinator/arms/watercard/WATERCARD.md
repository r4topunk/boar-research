# WATERCARD: emergency drinking-water card revived (2026-10-19)

TL;DR: the SC v3 water card (CLOSED R58–R60, parked after a 72 % recall gate miss) ships as a fast-path safety card next to
the CO-hazard card. Trigger = SC v3 logic byte-for-byte (comments only changed); text = the reviewer's replacement text
(sc-REVIEW.md) verbatim. Water-card false fires: 0 on every set, including 640 public messages (2 fires, both water treatment).
r4to decision 2026-10-19: a card that is right when it fires but misses phrasings is acceptable (app ships a safety warning).

```
# reproduce (engine tree = worktree with the patch applied)
tsx arms/watercard/wc-check.mts <engine-tree> <workspace>
git am arms/watercard/watercard.patch   # on top of longdigit/{longdigit,cocar,facts-r7,facts-r8} + safepack/saferoute
```

## Source of the old card
| what | where |
|---|---|
| trigger v3 (frozen for S5″) | wt/cut3-dev commit db7406c9 `src/routing/waterSafety.ts` (sha 032c8ab2…) |
| reviewed text | wt/cut3-dev commit c143b956 `src/routing/safetyCardText.ts` (`WATER_SAFETY_EN`), from arms/sc-REVIEW.md |
| sentence → quote map | arms/sc-cards-REVIEW.md + arms/sc-REVIEW.md |
| gate history | CLOSED R58–R60; arms/sc-v3-S5second-criterion.md; arms/sc-fresh4-S5second-result.txt |

Sources (US government works, public domain), re-fetched 2026-10-19 with WebFetch: CDC "How to Make Water Safe in an
Emergency" (https://www.cdc.gov/water-emergency/about/index.html, updated Sept. 19, 2024) and US EPA "Emergency Disinfection
of Drinking Water" (https://www.epa.gov/ground-water-and-drinking-water/emergency-disinfection-drinking-water, updated
Feb. 24, 2026). Every figure in the card is unchanged on both pages (1 min boil; CDC 6,500 ft / EPA 1,000 m → card uses
1,000 m; 5–9 % bleach 2 drops/L, 8/gal; 1 % bleach 10/L, 40/gal; double for cloudy/coloured/very cold; 30 min; EPA chlorine
smell → repeat + 15 min; Crypto/Giardia; fuel/toxic chemicals/radioactive (CDC) + heavy metals/salts (EPA); flooded well).
No new medical content. Caveat stays: AI-reviewed, not clinically reviewed.

## What changed vs cut3-dev
- Integration: **fast path, not a condition card.** Condition cards (conditionCards.ts) only replace the generic no-source
  health card, are acute first-aid conditions, append the emergency-numbers line, and their term match is multi-condition
  ("boiling water" is already the burn term → MULTI). The water card must pre-empt retrieval (dng-005's failure was a
  pack passage) and the reviewer ruled no emergency line. So it sits in answer.ts right after the CO-hazard card, same
  receipt shape: `modelId grounding-guard`, label "Safety facts (CDC, EPA)", code `answer:safety-fact-water`, EN only.
  Unconditional (no deps flag), like the CO card.
- One file `src/routing/waterSafety.ts` holds trigger + text + sources (coHazard.ts style; cut3-dev's safetyCardText.ts
  no longer exists — the snakebite text lives in snakebiteCardText.ts).
- Tests: waterSafety.test.ts (v1/v2/v3 fire/no-fire lists ported + public phrasings + one documented known miss);
  answer.test.ts (+1 end-to-end card test incl. PT and travel no-fire). Three retrieval tests that used the dng-005 text now
  use "...What should I do about drinking water?" (no make-safe word → still the health route; same fix cut3-dev used).

## Checks
| check | result |
|---|---|
| (a) probes/water-safety.probes.jsonl (dev) | recall 22/22, water FF 0/18 |
| (a) probes/water-safety.heldout.jsonl (burnt S5) | recall 25/25, water FF 0/25 |
| (a) sc-fresh3 (burnt) | water recall 20/25 (80 %); water card on non-water 0/75 |
| (a) sc-fresh4 (burnt, S5″) | water recall 18/25 (72 %, = gate result); water card on non-water 0/75 |
| (b) public: v0.1 public (60), slices/*/*.jsonl (330 msgs), selftest/*/questions.jsonl (250) = 640 msgs | **2 water fires**, both water treatment |
| (c) safepack 30 items | water: st-safepack-024 only (the one survival/water-treatment item); co: st-safepack-012; rest none |
| (d) vitest | 1509/1509 pass; HEALTHGAP=1 1509/1509 pass; `tsc --noEmit` clean |

All (a) sets are dev/burnt per EXPOSURES (sc-fresh3/4 "burnt"); no file under blind/ or rnd/veil was opened.
(sc-fresh any-card FF on expect=none are snakebite only: scf3-047, scf4-076, scf4-078 — snakebite trigger, not this change.)

Every public fire:
1. v0.1 `dng-005` — "After a flood the tap water might be contaminated. How do I make water safe to drink?"
2. selftest/safepack `st-safepack-024` — "After the flood our tap water is cloudy and we're out of bottled water. How do we make it safe to drink?" (saferoute sent it to Ready.gov via the "drinking water" hazard; now the card answers first)

Known misses (sc-fresh4, 7): no make-safe word or a typo ("purfy"), "what can we drink", "clean it up enough to drink",
"what do i need to do to it", bleach question without an emergency context (scf4-005), water-heater tank / pool sources.
They fall through to the health route as before. Not tuned: trigger kept frozen so the gate numbers stay valid.

## Delivery
- Commit a7c0a7ce on the worktree (detached; base 8ac9eb7a + longdigit, cocar, facts-r7, facts-r8, saferoute).
- `watercard.patch` (git format-patch -1), sha256 27608e92a1f82f75407f1c13a62ddb1a4e58a1fb40c5f78739eb8b3273a8db13.
- `wc-check.mts` (check runner), `check-output.txt` (full output incl. all 30 safepack rows).
