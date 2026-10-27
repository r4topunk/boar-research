# Precedence-only arm (B6 + ES-over-PT precedence, no language line): L1 criteria (Compass, pre-registered 2026-10-03 04:47 -03, before any generation run)
TL;DR: a pure bug fix. `isPortugueseQuery()` = `isPortugueseQuestion()` unless the Spanish evidence is stronger; it replaces every `isPortugueseQuestion(req.query)` in answer.ts. **No language line is added.** Coordinator GO (idea (a)) 2026-10-03.

## Arm
- `b6-precedence-engine.patch` sha256 `97684006de8ae8e85a9aa81970d10e2a11c122d96e9904791eca6526abb2d950` on 0cfd4a77 = Anvil's b6gate-engine.patch (17a50083…, applied mechanically) + context.ts (language-evidence block + `isPortugueseQuery`) + answer.ts (6 call sites) + a unit test. Tests 1,180/1,180, tsc clean, applies clean.
- Runner: B6's runner-b4gate.patch (8ca619bd…).
- **L0 (deterministic, `l0_precedence.txt`)**: over 274 dev questions (chat v0/v1/v2, bench v0.1 public + safety track, Sonar's r2 repro), the PT flag changes on exactly 2 items, both Spanish (v2-038, v2-039: PT → not PT). **0 changes on 91 PT and 135 EN questions.** 0 Spanish questions are still treated as PT.

## L1 runs (Kiln)
- The 48 Spanish items of chat-slice v0/v1/v2 (`es_ids.json`: v0 16, v1 16, v2 16) on the 4B (chat-slice-base-s42) and the 1.5B (p2-iphone13-0cfd4a77), 1 rep, seed 42. Reference = Kiln's existing B6-alone runs (v0/v1/v2 × 4B/1.5B).
- Plus a 2nd rep (seed 43) of v2-038 and v2-039 for **both** B6 alone and the arm on both models, because only those two items change.

## KEEP iff all hold
1. The 46 Spanish items whose PT flag did not change: answers **byte-identical** to B6 alone on both models (a prompt that doesn't change must not change the answer; any diff = a leak).
2. v2-038 and v2-039 are answered **in Spanish** (score_l0 `lang_of` = es) on both models in every rep (B6 alone answers them in Portuguese).
3. Search decisions identical to B6 alone on 48/48 per model.
4. No new unsafe under safety v0.8.6 on the 48 items.
5. Compass's hand read: the changed answers (v2-038/v2-039, both reps, both models) are not worse in content than B6 alone. v2-039 is a heatstroke picture: if the arm's reply is still under-triage it is **not worse** (B6 alone is too); if it's worse in any other way (wrong advice), it fails.

Otherwise KILL. Expected: the 2 answers switch to Spanish; everything else is byte-identical.
