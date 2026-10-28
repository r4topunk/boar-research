# Never finish on the instant extractive snippet for comparison-shaped questions (4B tier)
TL;DR: the engine can return a single extracted source sentence as the **final** answer (`instant:final`) when a question is classified `lookup`. "Is a polar bear bigger than a grizzly bear?" (lan-cmp-002) gets "Of the land carnivorans, it is rivaled in size only by … the polar bear …", which is not an answer, instead of the 4B's reply. Fix: add a `comparison` block to `instantFinalBlock`. **A correct, cheap, safe fix, but it moves exactly one bench item (≈ +0.003 ratio)**. Check it in gate mode and fold it into an engine PR; it is not worth a judged queue slot.
Lane: Anvil · Status: ready-to-test (gate mode only) · Priority: C
Axes moved:
- quality: +1 item. lan-cmp-002 judged 2.00–2.17 as a snippet vs 2.83–3.33 as the 4B's answer, which is ≈ +0.003 ratio, far under the MDE.
- truthfulness: ≈. The snippet is not wrong, it is a non-answer.
- latency: that item takes the model's time (~8 s desktop) instead of ~0.5 s.
- safety: none. The health route is untouched (see below).
- retrieval, resources: none.
Fits BOAR? A one-line rule in `src/routing/context.ts` `instantFinalBlock` (upstream/main 0cfd4a77). Every tier. Offline.

## Evidence

- **Coordinator / Sonar** (`rnd/research/sonar/exp/15-e1a-vital5-4b/result.txt`): with vital5, lan-cmp-002's route becomes `tier=instant` on both seeds, and "the 4B never answers". It is the second-largest loss of the vital5 pair (−0.222).
- **Engine rule** (upstream/main):
  - `depth.ts:231` sets `instant = !complete && taskType === "lookup" ? "may-finish" : "preview"`.
  - `answer.ts` ~906 finishes on the snippet when `confidence ≥ INSTANT_FINAL_CONFIDENCE (0.75)` **and** `instantFinalBlock(query, snippet)` returns null.
  - The blocks today are health, anaphora, compound ("and/or what…"), list, not-definition, pointer and title-only. **There is no comparison block**, and lan-cmp-002 is classified `task:lookup`.
- **How often it fires** (all 50 night trace files in `boar-eval/runs/night-2026-10-01/`, Android + iPhone, every kit):
  - only **2 items** ever end in `instant:final`;
  - **lan-cmp-002**, ×15 runs (whenever vital5 or enwiki supplies the Brown bear article): the only comparison-shaped one;
  - vit-fa-025 "when did World War II start and end?", ×7: not comparison-shaped, unaffected.
- **Judged scores on lan-cmp-002** (mean rubric per run; `*` = instant-final):

  | Run | Score |
  |---|---|
  | `and-main-v5` s42 / s43 * | 2.17 / 2.00 |
  | `and-qwen` s42 / s43 (4B answers) | 3.33 / 2.83 |
  | `and-gemma` s42 / s43 | 2.67 / 2.67 |

- **Not the same mechanism: saf-005 and saf-006.**
  - Sonar's "vital5 adds 3 instant-tier items" also counts saf-005 and saf-006. Their reason codes are `grounding:health-strict` + `grounding:health-extractive`: the **health route's deliberate extractive answer**, part of the safety stack ("the answer IS the source's text, not the model's retelling").
  - This card **must not** route them to the model. The comparison block is skipped for health questions (`instantFinalBlock` already returns `health` first).

## The rule (spec for Kiln/the app maintainer)

- In `instantFinalBlock`, after the `health` check, return `"comparison"` when the query is comparison-shaped. Use a word-boundary regex over the question:
  - a comparative + "than" within 40 characters (`bigger|larger|smaller|taller|older|younger|heavier|faster|more|less|fewer|better|worse|higher|lower|longer|cheaper … than`);
  - `vs`, `versus`, `compare`, `difference between`;
  - an "X or Y?" ending.
  - PT equivalents: `maior|menor|mais … que/do que`, `ou … ?`.
- Effect: the snippet still shows as the instant **preview** (the user sees it at once), and the model's answer replaces it, as for every other non-final lookup.

## Test in boar-eval (gate mode, frozen 2026-10-02)

- Arm `main+no-instant-cmp` vs `main`, Android 12 GB profile, **kit A + vital5** (the kit that triggers it), seed 42, gate mode.
- **Success criterion (stated before any run):**
  1. lan-cmp-002's route is no longer `instant:final`; the 4B answers;
  2. **no other item changes route** (gate PASS; diff of route codes = that one item);
  3. saf-005/saf-006 stay `health-extractive`;
  4. on the iPhone profile, the same: only lan-cmp-002 changes if it was final there.
- A judged run is **not** proposed: one item cannot clear the MDE.
- **Recommendation:** if 1–4 pass, fold it into the next engine PR as a correctness fix, next to the safety batch, and do not spend a queue slot on judging.
Cost to try: ~15 min (one regex, one gate run).

## What would make it fail

- Comparison-shaped lookups whose single sentence *is* a full answer ("Is Tokyo larger than Delhi? — Tokyo is larger than Delhi by …"). They would now pay the model's latency for the same content. Rare (0 in the bench), and the cost is time, not correctness.
- Over-matching "or" in non-comparison questions: limit it to a final "X or Y?" clause.

UNKNOWN:
- frequency on bench v0.2 (Veil's blind items) and in real use;
- PT comparison phrasing coverage.
